import sqlalchemy
from sqlalchemy import create_engine, text

def test_connections():
    combos = [
        "postgresql://user:password@127.0.0.1:5432/krishi_db",
        "postgresql://postgres:password@127.0.0.1:5432/krishi_db",
        "postgresql://postgres:password@127.0.0.1:5432/postgres",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
        "postgresql://postgres@127.0.0.1:5432/postgres" # Trust?
    ]
    
    for url in combos:
        print(f"Testing {url}...")
        try:
            engine = create_engine(url, connect_args={'connect_timeout': 3})
            with engine.connect() as conn:
                res = conn.execute(text("SELECT current_user, current_database()")).fetchone()
                print(f"SUCCESS: {res}")
                return url
        except Exception as e:
            print(f"FAILED: {e}")
    return None

if __name__ == "__main__":
    test_connections()
