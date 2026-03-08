import os
import sys

# Ensure the app module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        # Check if admin role exists, if not create it
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator role")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created 'admin' role.")
        
        # Check if admin user exists, if not create it
        # We will use "admin@krishi.com" as the username (phone_number field is used for login)
        # The schema allows str(20) for phone_number, so we will use a valid string length.
        admin_email = "admin@krishi.com"
        admin_pass = "admin123"
        
        admin_user = db.query(User).filter(User.phone_number == admin_email).first()
        if not admin_user:
            admin_user = User(
                phone_number=admin_email,
                full_name="System Administrator",
                hashed_password=get_password_hash(admin_pass),
                is_active=True,
                role_id=admin_role.id
            )
            db.add(admin_user)
            db.commit()
            print(f"Created admin user. Login: {admin_email} | Password: {admin_pass}")
        else:
            # Ensure it has admin role
            admin_user.role_id = admin_role.id
            db.commit()
            print(f"Admin user already exists. Login: {admin_email} | Password: {admin_pass}")
            
    except Exception as e:
        print(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
