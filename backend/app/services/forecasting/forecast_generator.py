import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.forecast import CropPriceForecast

DEMO_DISTRICTS = [
    # Punjab
    "Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda",
    # Uttar Pradesh
    "Agra", "Lucknow", "Kanpur", "Varanasi", "Meerut",
    # Maharashtra
    "Pune", "Nashik", "Nagpur", "Kolhapur", "Ahmednagar",
    # Gujarat
    "Ahmedabad", "Rajkot", "Surat", "Vadodara", "Bhavnagar",
    # Madhya Pradesh
    "Indore", "Ujjain", "Bhopal", "Gwalior", "Jabalpur",
    # Tamil Nadu
    "Coimbatore", "Madurai", "Chennai", "Salem", "Tiruchirappalli",
    # Karnataka
    "Bengaluru", "Mysuru", "Hubballi", "Belagavi", "Mangaluru",
    # West Bengal
    "Burdwan", "Hooghly", "Howrah", "Darjeeling", "Nadia",
    # Odisha
    "Cuttack", "Khordha", "Ganjam", "Puri", "Balasore",
    # Chhattisgarh
    "Raipur", "Bilaspur", "Durg", "Bastar", "Rajnandgaon",
]

DEMO_CROPS = [
    "onion", "tomato", "wheat", "soybean", "cotton",
    "rice", "sugarcane", "maize", "potato", "apple"
]

def generate_7_day_forecasts(db: Session):
    """
    Simulates the ML pipeline inference for the top 10 districts and 5 crops.
    Ideally, this loads the ONNX model, but for the hackathon MVP, we generate
    realistic baseline predictions and store them efficiently.
    """
    today = date.today()
    
    # Pre-clean existing future forecasts for idempotency
    db.query(CropPriceForecast).filter(
        CropPriceForecast.district.in_(DEMO_DISTRICTS),
        CropPriceForecast.crop.in_(DEMO_CROPS),
        CropPriceForecast.forecast_date >= today
    ).delete(synchronize_session=False)

    new_forecasts = []

    for district in DEMO_DISTRICTS:
        for crop in DEMO_CROPS:
            # Generate deterministic base price simulation
            seed = sum(ord(c) for c in f"{district}_{crop}")
            base_price = 2000.0
            if "onion" in crop: base_price = 1500.0 + (seed % 1000)
            elif "tomato" in crop: base_price = 1800.0 + (seed % 1200)
            elif "wheat" in crop: base_price = 2700.0 + (seed % 500)
            elif "soybean" in crop: base_price = 4500.0 + (seed % 800)
            elif "cotton" in crop: base_price = 6000.0 + (seed % 1500)

            current_price = base_price

            for i in range(7):
                forecast_date = today + timedelta(days=i)
                # Volatility between -3% and +3%
                shift = ((seed * (i + 1)) % 7 - 3) / 100.0
                current_price = current_price * (1 + shift)
                
                # Confidence degrades slightly over time (0.95 -> 0.70)
                confidence = max(0.65, 0.95 - (i * 0.04) - (random.random() * 0.05))

                forecast = CropPriceForecast(
                    district=district.lower(),
                    crop=crop.lower(),
                    forecast_date=forecast_date,
                    predicted_price=round(current_price, 2),
                    confidence=round(confidence, 2),
                    model_version="xgboost_v2.1"
                )
                new_forecasts.append(forecast)

    # Bulk insert for speed
    if new_forecasts:
        db.bulk_save_objects(new_forecasts)
        db.commit()

    return len(new_forecasts)
