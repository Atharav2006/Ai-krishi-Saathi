from app.core.config import settings
from sqlalchemy import create_engine, text

def check():
    print(f"URL: {settings.DATABASE_URL}")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_user, current_database()")).fetchone()
            print(f"Connected as: {result}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
