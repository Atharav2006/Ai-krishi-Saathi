import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def update_admin():
    # Load .env manually
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL not found in environment.")
        return

    engine = create_engine(db_url)
    with engine.connect() as conn:
        try:
            # 1. Update existing admin if it has the simple 'admin' username
            conn.execute(text("UPDATE users SET phone_number = 'admin@krishi.com' WHERE phone_number = 'admin'"))
            
            # 2. Check if admin@krishi.com exists
            result = conn.execute(text("SELECT id FROM users WHERE phone_number = 'admin@krishi.com'")).fetchone()
            
            if not result:
                # Need to insert if it doesn't exist. 
                # We'll need a role ID for 'Admin'.
                role_result = conn.execute(text("SELECT id FROM roles WHERE name = 'Admin'")).fetchone()
                if not role_result:
                    # Create Admin role
                    import uuid
                    role_id = str(uuid.uuid4())
                    conn.execute(text("INSERT INTO roles (id, name, description, created_at, updated_at) VALUES (:id, 'Admin', 'Admin Role', now(), now())"), {"id": role_id})
                else:
                    role_id = role_result[0]
                
                # Insert admin user
                user_id = str(uuid.uuid4())
                # Hashed 'admin123'
                hashed_pass = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L65JGWyNyFZB5ge"
                conn.execute(text("INSERT INTO users (id, phone_number, full_name, hashed_password, is_active, role_id, created_at, updated_at, is_deleted) VALUES (:id, 'admin@krishi.com', 'Admin User', :hp, true, :rid, now(), now(), false)"), 
                             {"id": user_id, "hp": hashed_pass, "rid": role_id})
                print("Created admin@krishi.com")
            else:
                print("admin@krishi.com updated/exists successfully.")
            
            conn.commit()
            print("DONE")
        except Exception as e:
            print(f"SQL Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_admin()
