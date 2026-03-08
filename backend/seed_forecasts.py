import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.services.forecasting.forecast_generator import generate_7_day_forecasts

def main():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        count = generate_7_day_forecasts(db)
        print(f"Successfully generated {count} forecasts!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
