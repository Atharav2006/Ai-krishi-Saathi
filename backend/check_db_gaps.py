
import json
import os
from sqlalchemy.orm import Session
import sqlite3
from datetime import date

# Mock the parts of app needed to run this script standalone or use existing db
DB_PATH = "c:/Users/ATHARAV/Documents/Hackathon/Elite hack 1.0/ai_krishi_saathi/backend/krishi_saathi.db"

DEMO_DISTRICTS = [
    "Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda",
    "Agra", "Lucknow", "Kanpur", "Varanasi", "Meerut",
    "Pune", "Nashik", "Nagpur", "Kolhapur", "Ahmednagar",
    "Ahmedabad", "Rajkot", "Surat", "Vadodara", "Bhavnagar",
    "Indore", "Ujjain", "Bhopal", "Gwalior", "Jabalpur",
    "Coimbatore", "Madurai", "Chennai", "Salem", "Tiruchirappalli",
    "Bengaluru", "Mysuru", "Hubballi", "Belagavi", "Mangaluru",
    "Burdwan", "Hooghly", "Howrah", "Darjeeling", "Nadia",
    "Cuttack", "Khordha", "Ganjam", "Puri", "Balasore",
    "Raipur", "Bilaspur", "Durg", "Bastar", "Rajnandgaon",
]

DEMO_CROPS = ["onion", "tomato", "wheat", "soybean", "cotton", "rice", "apple"]

def check_gaps():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    print(f"Checking data for {today}")
    
    missing = []
    for district in DEMO_DISTRICTS:
        for crop in DEMO_CROPS:
            cursor.execute(
                "SELECT COUNT(*) FROM crop_price_forecasts WHERE district=? AND crop=? AND forecast_date>=?",
                (district, crop, today)
            )
            count = cursor.fetchone()[0]
            if count == 0:
                missing.append((district, crop))
    
    conn.close()
    return missing

if __name__ == "__main__":
    gaps = check_gaps()
    if not gaps:
        print("No gaps found. All combinations have data.")
    else:
        print(f"Found {len(gaps)} missing combinations.")
        for d, c in gaps[:10]:
            print(f"Missing: {d} - {c}")
        if len(gaps) > 10:
            print("...")
