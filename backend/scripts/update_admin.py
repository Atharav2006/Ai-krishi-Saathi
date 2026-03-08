from app.db.session import SessionLocal
from app.models.user import User, Role
from sqlalchemy import text

def update_admin():
    db = SessionLocal()
    try:
        # Update phone_number to email format for the input validation to pass on frontend
        user = db.query(User).filter(User.phone_number == 'admin').first()
        if user:
            user.phone_number = 'admin@krishi.com'
            db.commit()
            print("Successfully updated admin to admin@krishi.com")
        else:
            # Check if it's already updated or if we need to create it
            user_exists = db.query(User).filter(User.phone_number == 'admin@krishi.com').first()
            if not user_exists:
                # If neither 'admin' nor 'admin@krishi.com' exists, it means previous injection failed or something.
                # Let's just ensure an admin exists.
                from app.core.security import get_password_hash
                admin_role = db.query(Role).filter(Role.name == 'Admin').first()
                if not admin_role:
                    admin_role = Role(name='Admin', description='Admin')
                    db.add(admin_role)
                    db.commit()
                    db.refresh(admin_role)
                
                new_admin = User(
                    phone_number='admin@krishi.com',
                    full_name='Admin User',
                    hashed_password=get_password_hash('admin123'),
                    role_id=admin_role.id
                )
                db.add(new_admin)
                db.commit()
                print("Created new admin: admin@krishi.com")
            else:
                print("Admin admin@krishi.com already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    update_admin()
