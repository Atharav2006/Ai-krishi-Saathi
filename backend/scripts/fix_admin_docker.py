import sqlalchemy
from sqlalchemy import create_engine, text

def update_admin():
    # Use 127.0.0.1 to avoid potential 'localhost' resolution issues (IPv6 ::1 vs IPv4)
    db_url = "postgresql://user:password@127.0.0.1:5432/krishi_db"
    
    engine = create_engine(db_url)
    with engine.connect() as conn:
        try:
            # Update phone_number to email format
            conn.execute(text("UPDATE users SET phone_number = 'admin@krishi.com' WHERE phone_number = 'admin'"))
            # Ensure it works even if it was partially updated or created
            conn.execute(text("UPDATE users SET phone_number = 'admin@krishi.com' WHERE phone_number = 'admin@krishi.com'"))
            conn.commit()
            print("Successfully updated/confirmed admin@krishi.com")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_admin()
