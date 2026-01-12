from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, DateTime, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class StudyPlan(Base):
    __tablename__ = 'study_plans'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.now().date, unique=True) # 每天一个计划
    content = Column(JSON) # 存储任务列表 [{"topic":.., "status":..}]
    encouragement = Column(String)
    status = Column(String, default="in_progress") # in_progress, completed
    reflection = Column(Text, nullable=True)

class InterviewSession(Base):
    __tablename__ = 'interview_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    topic = Column(String)
    # 存储问答对 [{"role": "assistant", "content": "Q1..."}, {"role": "user", "content": "..."}]
    messages = Column(JSON, default=list) 
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

# 确保 data 目录存在
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'interview.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
