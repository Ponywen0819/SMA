import time
import logging
from datetime import datetime
from youtube_crawler import YouTubeCrawler
from relationship_analyzer import RelationshipAnalyzer
from database import init_db

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)

def setup_database():
    """初始化資料庫"""
    try:
        init_db()
        logging.info("資料庫初始化成功")
    except Exception as e:
        logging.error(f"資料庫初始化失敗: {e}")
        raise

def search_and_save_creators(crawler, keywords=None, max_results=20):
    """搜尋並保存創作者資訊"""
    if keywords is None:
        keywords = [
            "Minecraft creator",
            "Minecraft YouTuber",
            "Minecraft content creator",
            "Minecraft streamer"
        ]
    
    all_creators = []
    for keyword in keywords:
        try:
            logging.info(f"開始搜尋關鍵字: {keyword}")
            creators = crawler.search_creators(query=keyword, max_results=max_results)
            logging.info(f"找到 {len(creators)} 個創作者")
            
            for creator in creators:
                person_id = crawler.save_creator(creator)
                if person_id:
                    logging.info(f"已保存創作者: {creator['title']}")
                    all_creators.append(creator)
                else:
                    logging.warning(f"保存創作者失敗: {creator['title']}")
            
            # 避免觸發 API 限制
            time.sleep(1)
        except Exception as e:
            logging.error(f"搜尋關鍵字 {keyword} 時發生錯誤: {e}")
    
    return all_creators

def crawl_creator_contents(crawler, creators):
    """爬取創作者的內容"""
    for i, creator in enumerate(creators, 1):
        try:
            logging.info(f"正在爬取第 {i}/{len(creators)} 個創作者: {creator['title']}")
            success = crawler.crawl_creator_content(creator['channel_id'])
            if success:
                logging.info(f"完成爬取 {creator['title']} 的內容")
            else:
                logging.warning(f"爬取 {creator['title']} 的內容失敗")
            
            # 避免觸發 API 限制
            time.sleep(2)
        except Exception as e:
            logging.error(f"爬取 {creator['title']} 的內容時發生錯誤: {e}")

def analyze_relationships(analyzer):
    """分析創作者關係"""
    try:
        logging.info("開始分析創作者關係...")
        analyzer.analyze_all_relationships()
        
        # 獲取關係統計信息
        stats = analyzer.get_relationship_stats()
        logging.info(f"總關係數: {stats['total_relationships']}")
        
        logging.info("關係類型統計:")
        for rel_type, count in stats['relationship_types'].items():
            logging.info(f"{rel_type}: {count}")
        
        logging.info("\n連接最多的創作者:")
        for creator in stats['most_connected_creators']:
            logging.info(f"{creator['name']}: {creator['connection_count']} 個連接")
            
    except Exception as e:
        logging.error(f"分析關係時發生錯誤: {e}")

def main():
    start_time = datetime.now()
    logging.info("開始執行爬蟲程序")
    
    try:
        # 初始化資料庫
        setup_database()
        
        # 創建爬蟲實例
        crawler = YouTubeCrawler()
        analyzer = RelationshipAnalyzer()
        
        # 第一步：搜尋並保存創作者資訊
        creators = search_and_save_creators(crawler)
        
        # 第二步：爬取創作者內容
        if creators:
            crawl_creator_contents(crawler, creators)
            
            # 第三步：分析創作者關係
            analyze_relationships(analyzer)
        else:
            logging.warning("沒有找到任何創作者，跳過內容爬取和關係分析")
        
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"爬蟲程序執行完成，總耗時: {duration}")
        
    except Exception as e:
        logging.error(f"程序執行失敗: {e}")
        raise

if __name__ == "__main__":
    main() 