from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    
    person_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 關聯
    accounts = relationship("Account", back_populates="person")
    source_relationships = relationship("Relationship", 
                                      foreign_keys="[Relationship.source_person_id]",
                                      back_populates="source_person")
    target_relationships = relationship("Relationship",
                                      foreign_keys="[Relationship.target_person_id]",
                                      back_populates="target_person")

class Account(Base):
    __tablename__ = 'accounts'
    
    account_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.person_id'))
    platform = Column(String(50), nullable=False)
    account_handle = Column(String(255), nullable=False)
    url = Column(String(255))
    
    # 關聯
    person = relationship("Person", back_populates="accounts")
    channels = relationship("Channel", back_populates="account")
    contents = relationship("Content", back_populates="account")

class Channel(Base):
    __tablename__ = 'channels'
    
    channel_id = Column(String(255), primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime)
    subscriber_count = Column(Integer, default=0)
    country = Column(String(50))  # 國家/地區
    language = Column(String(50))  # 主要語言
    
    # 關聯
    account = relationship("Account", back_populates="channels")

class Content(Base):
    __tablename__ = 'contents'
    
    content_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id'))
    platform_content_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    
    # 聲量相關字段
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)  # 互動率 = (點讚數 + 評論數) / 觀看數
    
    # 關聯
    account = relationship("Account", back_populates="contents")

class Relationship(Base):
    __tablename__ = 'relationships'
    
    relationship_id = Column(Integer, primary_key=True)
    source_person_id = Column(Integer, ForeignKey('persons.person_id'))
    target_person_id = Column(Integer, ForeignKey('persons.person_id'))
    relation_type = Column(String(50), nullable=False)
    evidence = Column(Text)
    
    # 關聯
    source_person = relationship("Person", 
                               foreign_keys=[source_person_id],
                               back_populates="source_relationships")
    target_person = relationship("Person",
                               foreign_keys=[target_person_id],
                               back_populates="target_relationships") 