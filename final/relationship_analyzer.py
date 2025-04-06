import re
from typing import List, Dict
from database import get_db
from models import Person, Content, Relationship, Account
from youtube_crawler import YouTubeCrawler

class RelationshipAnalyzer:
    def __init__(self):
        self.db = next(get_db())
        self.youtube = YouTubeCrawler()
        
    def analyze_video_description(self, description: str) -> List[Dict]:
        """分析影片描述中的關係"""
        relationships = []
        
        # 常見的關係模式
        patterns = [
            r'collab with @(\w+)',  # 合作
            r'featuring @(\w+)',    # 特約
            r'with @(\w+)',         # 與某人一起
            r'guest: @(\w+)',       # 嘉賓
            r'@(\w+)',              # 提及
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, description.lower())
            for match in matches:
                mentioned_handle = match.group(1)
                relationships.append({
                    'handle': mentioned_handle,
                    'type': self._get_relation_type(pattern)
                })
        
        return relationships
    
    def _get_relation_type(self, pattern: str) -> str:
        """根據匹配模式返回關係類型"""
        if 'collab' in pattern:
            return 'collaboration'
        elif 'featuring' in pattern:
            return 'feature'
        elif 'guest' in pattern:
            return 'guest_appearance'
        else:
            return 'mention'
    
    def find_mentioned_creators(self, handle: str) -> List[Person]:
        """根據提及的帳號名稱查找創作者"""
        # 首先嘗試在帳號表中查找
        accounts = self.db.query(Person).join(Account).filter(
            Account.account_handle.ilike(f'%{handle}%')
        ).all()
        
        return accounts
    
    def analyze_creator_relationships(self, person_id: int):
        """分析特定創作者的關係"""
        # 獲取創作者的所有內容
        contents = self.db.query(Content).join(Account).filter(
            Account.person_id == person_id
        ).all()
        
        for content in contents:
            # 分析影片描述
            relationships = self.analyze_video_description(content.description)
            
            for rel in relationships:
                # 查找被提及的創作者
                mentioned_creators = self.find_mentioned_creators(rel['handle'])
                
                for target_person in mentioned_creators:
                    # 避免自引用
                    if target_person.person_id == person_id:
                        continue
                    
                    # 檢查關係是否已存在
                    existing = self.db.query(Relationship).filter(
                        Relationship.source_person_id == person_id,
                        Relationship.target_person_id == target_person.person_id,
                        Relationship.relation_type == rel['type']
                    ).first()
                    
                    if not existing:
                        # 創建新關係
                        relationship = Relationship(
                            source_person_id=person_id,
                            target_person_id=target_person.person_id,
                            relation_type=rel['type'],
                            evidence=f"Video: {content.platform_content_id}"
                        )
                        self.db.add(relationship)
        
        self.db.commit()
    
    def analyze_all_relationships(self):
        """分析所有創作者的關係"""
        persons = self.db.query(Person).all()
        for person in persons:
            self.analyze_creator_relationships(person.person_id)
    
    def get_relationship_stats(self) -> Dict:
        """獲取關係統計信息"""
        stats = {
            'total_relationships': self.db.query(Relationship).count(),
            'relationship_types': {},
            'most_connected_creators': []
        }
        
        # 統計關係類型
        relationships = self.db.query(Relationship).all()
        for rel in relationships:
            stats['relationship_types'][rel.relation_type] = \
                stats['relationship_types'].get(rel.relation_type, 0) + 1
        
        # 找出連接最多的創作者
        person_connections = {}
        for rel in relationships:
            person_connections[rel.source_person_id] = \
                person_connections.get(rel.source_person_id, 0) + 1
            person_connections[rel.target_person_id] = \
                person_connections.get(rel.target_person_id, 0) + 1
        
        sorted_creators = sorted(person_connections.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:5]
        
        for person_id, count in sorted_creators:
            person = self.db.query(Person).get(person_id)
            stats['most_connected_creators'].append({
                'name': person.name,
                'connection_count': count
            })
        
        return stats

if __name__ == "__main__":
    analyzer = RelationshipAnalyzer()
    analyzer.analyze_all_relationships()
    stats = analyzer.get_relationship_stats()
    print(stats)