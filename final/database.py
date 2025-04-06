from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 資料庫連接設定
DATABASE_URL = "sqlite:///social_network.db"

# 創建資料庫引擎
engine = create_engine(DATABASE_URL)

# 創建 Session 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化資料庫，創建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 