import bcrypt
from sqlalchemy.orm import Session
from database.models import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    # Hash the password
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    db_user = User(username=username, password_hash=pwd_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def init_admin_user(db: Session):
    """Ensure the default admin exists"""
    user = get_user_by_username(db, "admin")
    if not user:
        create_user(db, "admin", "admin")
        print("Created default user: admin/admin")
