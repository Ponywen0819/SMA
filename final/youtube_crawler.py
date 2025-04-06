import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from database import get_db
from models import Person, Account, Channel, Content, Relationship
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging

load_dotenv()

class YouTubeCrawler:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.db = next(get_db())

    def search_creators(self, query: str, max_results: int = 50) -> List[Dict]:
        """搜索台灣地區的創作者並按訂閱數排序"""
        try:
            # 構建搜索請求，添加地區限制
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results,
                regionCode="TW",  # 限制為台灣地區
                fields="items(id(channelId),snippet(title,description,channelId))"
            )
            
            # 執行搜索
            response = request.execute()
            
            # 獲取所有頻道ID
            channel_ids = [item['id']['channelId'] for item in response.get('items', [])]
            
            # 批量獲取頻道統計數據
            request = self.youtube.channels().list(
                part="statistics,snippet,brandingSettings",
                id=','.join(channel_ids)
            )
            channel_response = request.execute()
            
            # 過濾和排序結果
            creators = []
            for item in channel_response.get('items', []):
                channel_id = item['id']
                snippet = item['snippet']
                stats = item['statistics']
                branding = item.get('brandingSettings', {})
                
                # 排除 "minecraft creator" 頻道
                if "minecraft creator" in snippet['title'].lower():
                    continue
                
                # 獲取地區和語言信息
                country = branding.get('channel', {}).get('country', '')
                language = snippet.get('defaultLanguage', '')
                
                # 只保留台灣地區的頻道
                if country != 'TW':
                    continue
                
                creators.append({
                    'channel_id': channel_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'subscriber_count': int(stats.get('subscriberCount', 0)),
                    'country': country,
                    'language': language
                })
            
            # 按訂閱數降序排序
            creators.sort(key=lambda x: x['subscriber_count'], reverse=True)
            
            return creators
            
        except Exception as e:
            logging.error(f"搜索創作者時出錯: {str(e)}")
            return []

    def get_channel_info(self, channel_id):
        """獲取頻道詳細資訊"""
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return None
                
            channel = response['items'][0]
            return {
                'channel_id': channel_id,
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'created_at': channel['snippet']['publishedAt'],
                'subscriber_count': channel['statistics']['subscriberCount']
            }
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def save_creator(self, creator_info: Dict) -> Optional[int]:
        """保存創作者信息到數據庫"""
        try:
            # 檢查是否已存在
            existing_person = self.db.query(Person).join(Account).filter(
                Account.account_handle == creator_info['channel_id']
            ).first()
            
            if existing_person:
                return existing_person.person_id
            
            # 創建新創作者
            person = Person(
                name=creator_info['title'],
                description=creator_info['description']
            )
            self.db.add(person)
            self.db.flush()  # 獲取 person_id
            
            # 創建帳號
            account = Account(
                person_id=person.person_id,
                account_handle=creator_info['channel_id'],
                platform="youtube",
                url=f"https://www.youtube.com/channel/{creator_info['channel_id']}"
            )
            self.db.add(account)
            self.db.flush()  # 獲取 account_id
            
            # 創建頻道
            channel = Channel(
                channel_id=creator_info['channel_id'],
                account_id=account.account_id,
                title=creator_info['title'],
                description=creator_info['description'],
                created_at=datetime.now(),
                subscriber_count=creator_info['subscriber_count'],
                country=creator_info['country'],
                language=creator_info['language']
            )
            self.db.add(channel)
            
            self.db.commit()
            return person.person_id
            
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error saving creator: {str(e)}")
            return None

    def get_channel_videos(self, channel_id, max_results=50):
        """獲取頻道的影片列表"""
        try:
            # 首先獲取頻道的上傳播放列表 ID
            request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return []
                
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # 獲取播放列表中的影片
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            # 獲取所有影片ID
            video_ids = [item['snippet']['resourceId']['videoId'] for item in response['items']]
            
            # 批量獲取影片統計數據
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=','.join(video_ids)
            )
            video_response = request.execute()
            
            videos = []
            for item in video_response['items']:
                stats = item['statistics']
                video = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0))
                }
                videos.append(video)
            
            return videos
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []

    def save_video(self, account_id, video_info):
        """將影片資訊保存到資料庫"""
        try:
            # 計算互動率
            view_count = video_info.get('view_count', 0)
            like_count = video_info.get('like_count', 0)
            comment_count = video_info.get('comment_count', 0)
            
            engagement_rate = 0.0
            if view_count > 0:
                engagement_rate = (like_count + comment_count) / view_count
            
            content = Content(
                account_id=account_id,
                platform_content_id=video_info['video_id'],
                title=video_info['title'],
                description=video_info['description'],
                published_at=datetime.fromisoformat(video_info['published_at'].replace('Z', '+00:00')),
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                engagement_rate=engagement_rate
            )
            self.db.add(content)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error saving video: {e}")
            return False

    def crawl_creator_content(self, channel_id):
        """爬取創作者的所有內容"""
        account = self.db.query(Account).join(Channel).filter(Channel.channel_id == channel_id).first()
        if not account:
            return False
            
        videos = self.get_channel_videos(channel_id)
        for video in videos:
            self.save_video(account.account_id, video)
        return True 