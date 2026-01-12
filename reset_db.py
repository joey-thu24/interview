import sys
import os
from sqlalchemy import text

# Init path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import engine, Base

def reset_database():
    print("⚠️  WARNING: This will DROP ALL DATA in your TiDB Database!")
    
    # Auto-confirm for convenience since user asked "You do it"
    print("Automatically confirming reset...")

    print("Dropping all tables...")
    try:
        # Disable foreign key checks to allow dropping tables in any order
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.commit()
            
        Base.metadata.drop_all(bind=engine)
        
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
            
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema reset successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    reset_database()
