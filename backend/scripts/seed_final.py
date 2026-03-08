from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

def seed():
    db = SessionLocal()
    try:
        # 1. Ensure Role exists
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created Admin role")
        
        # 2. Ensure User exists
        admin_user = db.query(User).filter(User.phone_number == "admin@krishi.com").first()
        if not admin_user:
            admin_user = User(
                phone_number="admin@krishi.com",
                full_name="System Admin",
                hashed_password=get_password_hash("admin123"),
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin_user)
            print("Created Admin user")
        else:
            admin_user.role_id = admin_role.id
            admin_user.is_active = True
            print("Updated Admin user")
        
        db.commit()
        print("SEEDING_COMPLETE")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
