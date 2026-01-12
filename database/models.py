from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from core.config import DATABASE_URL

Base = declarative_base()

# --- User Model ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    # 存储加密后的哈希值，建议长度留够
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyPlan(Base):
    __tablename__ = 'study_plans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1) # 关联用户
    # 联合唯一索引: 同一个用户每天只能有一个计划
    date = Column(Date, default=lambda: date.today()) 
    
    content = Column(JSON) # 存储任务列表 [{"topic":.., "status":..}]
    encouragement = Column(String(500)) # MySQL String 需要长度，或者用 Text
    status = Column(String(50), default="in_progress") # in_progress, completed
    reflection = Column(Text, nullable=True)

class InterviewSession(Base):
    __tablename__ = 'interview_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1) # 关联用户
    
    topic = Column(String(100))
    messages = Column(JSON)
    feedback = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Engine Setup ---
connect_args = {}

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "mysql" in DATABASE_URL:
    # TiDB Cloud requires SSL. We force an SSL context.
    # We use a simple unverified context to ensure encryption is on without fighting CA paths.
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl": ssl_context}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True, # 自动心跳检查，防止云数据库断连
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
