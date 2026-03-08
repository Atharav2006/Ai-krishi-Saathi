import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup path
import sys
sys.path.append(os.getcwd())

# 2. Import everything from models __init__
from app.db.base_class import Base
from app.models import (
    User, Role, State, District, Crop, Market, MandiPrice, PricePrediction,
    DiseaseReport, Advisory, RainfallData, SoilMoistureData,
    PredictionLog, GroundTruthLog, ModelMetric, ModelDegradationLog,
    ModelRegistry, ModelRetrainingJob
)
from app.core.security import get_password_hash

# 3. SQLite setup
DB_URL = "sqlite:///./krishi_saathi.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def force_init():
    print(f"Initializing SQLite DB with Comprehensive Demo Data: {DB_URL}")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # --- 1. Roles ---
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(id=uuid.uuid4(), name="Admin", description="Administrator")
            db.add(admin_role)
            db.commit(); db.refresh(admin_role)
            print("Created 'Admin' role.")
        
        farmer_role = db.query(Role).filter(Role.name == "Farmer").first()
        if not farmer_role:
            farmer_role = Role(id=uuid.uuid4(), name="Farmer", description="Farmer User")
            db.add(farmer_role)
            db.commit(); db.refresh(farmer_role)
            print("Created 'Farmer' role.")

        # --- 2. Admin User ---
        admin_email = "admin@krishi.com"
        admin_user = db.query(User).filter(User.phone_number == admin_email).first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                phone_number=admin_email,
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                role_id=admin_role.id
            )
            db.add(admin_user)
            db.commit()
            print(f"Created Admin User: {admin_email} / admin123")
        else:
            admin_user.role_id = admin_role.id
            admin_user.is_active = True
            db.commit()
            print(f"Updated existing Admin User: {admin_email}")

        # --- 3. Farmer User ---
        farmer_phone = "9999999999"
        farmer_user = db.query(User).filter(User.phone_number == farmer_phone).first()
        if not farmer_user:
            farmer_user = User(
                id=uuid.uuid4(),
                phone_number=farmer_phone,
                full_name="Demo Farmer",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                role_id=farmer_role.id
            )
            db.add(farmer_user)
            db.commit()
            print(f"Created Farmer User: {farmer_phone} / password123")
        else:
            farmer_user.role_id = farmer_role.id
            farmer_user.is_active = True
            db.commit()
            print(f"Updated existing Farmer User: {farmer_phone}")

        # --- 3. Geography & Crops ---
        maharashtra = db.query(State).filter(State.name == "Maharashtra").first()
        if not maharashtra:
            maharashtra = State(id=uuid.uuid4(), name="Maharashtra")
            db.add(maharashtra); db.commit(); db.refresh(maharashtra)
        
        pune = db.query(District).filter(District.name == "Pune").first()
        if not pune:
            pune = District(id=uuid.uuid4(), name="Pune", state_id=maharashtra.id)
            db.add(pune); db.commit(); db.refresh(pune)

        tomato = db.query(Crop).filter(Crop.name == "Tomato").first()
        if not tomato:
            tomato = Crop(id=uuid.uuid4(), name="Tomato", scientific_name="Solanum lycopersicum")
            db.add(tomato); db.commit(); db.refresh(tomato)

        # --- 4. Models ---
        for m_type in ["price_forecast", "disease_detection"]:
            active_model = db.query(ModelRegistry).filter(
                ModelRegistry.model_type == m_type, 
                ModelRegistry.status == "active"
            ).first()
            if not active_model:
                active_model = ModelRegistry(
                    id=uuid.uuid4(),
                    model_type=m_type,
                    model_version="v1.0.0",
                    status="active",
                    trained_at=datetime.now(timezone.utc) - timedelta(days=7),
                    metrics_snapshot={"accuracy": 0.92, "f1": 0.89} if m_type == "disease_detection" else {"mae": 15.5, "rmse": 22.1}
                )
                db.add(active_model)
                print(f"Seeded active model for {m_type}")
        db.commit()

        # --- 5. Logs & Metrics ---
        # Last 24 hours logs
        now = datetime.now(timezone.utc)
        if db.query(PredictionLog).count() < 10:
            for i in range(24):
                ts = now - timedelta(hours=i)
                log = PredictionLog(
                    id=uuid.uuid4(),
                    user_id=admin_user.id,
                    model_type="price_forecast",
                    model_version="v1.0.0",
                    input_hash=str(uuid.uuid4())[:8],
                    predicted_value=str(2500 + random.randint(-100, 100)),
                    confidence_score=0.85 + (random.random() * 0.1),
                    latency_ms=45.2,
                    created_at=ts
                )
                db.add(log)
            print("Seeded 24h prediction logs.")

        # Last 30 days metrics
        if db.query(ModelMetric).count() < 10:
            for i in range(30):
                day = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                metric = ModelMetric(
                    id=uuid.uuid4(),
                    model_type="price_forecast",
                    model_version="v1.0.0",
                    metric_name="MAE",
                    metric_value=12.0 + (random.random() * 5.0),
                    window_start=day,
                    window_end=day + timedelta(days=1),
                    created_at=day + timedelta(hours=23)
                )
                db.add(metric)
            print("Seeded 30d metrics.")

        db.commit()
        print("SQLITE_READY")
            
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_init()
