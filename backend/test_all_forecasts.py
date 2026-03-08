
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/forecasts"

DISTRICTS = [
    "Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda",
    "Agra", "Lucknow", "Kanpur", "Varanasi", "Meerut",
    "Coimbatore", "Madurai", "Chennai", "Salem", "Tiruchirappalli",
    "Bengaluru", "Mysuru", "Hubballi", "Belagavi", "Mangaluru",
    "Burdwan", "Hooghly", "Howrah", "Darjeeling", "Nadia",
    "Cuttack", "Khordha", "Ganjam", "Puri", "Balasore",
    "Pune", "Nashik", "Nagpur", "Kolhapur", "Ahmednagar",
    "Ahmedabad", "Rajkot", "Surat", "Vadodara", "Bhavnagar",
    "Indore", "Ujjain", "Bhopal", "Gwalior", "Jabalpur",
    "Raipur", "Bilaspur", "Durg", "Bastar", "Rajnandgaon"
]

CROPS = [
    "rice", "wheat", "cotton", "sugarcane", "maize",
    "soybean", "potato", "onion", "tomato", "apple"
]

def test_all():
    failed = []
    print(f"Testing {len(DISTRICTS) * len(CROPS)} combinations...")
    for d in DISTRICTS:
        for c in CROPS:
            try:
                r = requests.get(BASE_URL, params={"district": d, "crops": c}, timeout=2)
                if r.status_code != 200:
                    failed.append((d, c, r.status_code))
                    print(f"FAILED: {d} - {c} ({r.status_code})")
            except Exception as e:
                failed.append((d, c, str(e)))
                print(f"ERROR: {d} - {c} ({e})")
    
    if not failed:
        print("All 500 combinations PASSED!")
    else:
        print(f"{len(failed)} combinations FAILED.")

if __name__ == "__main__":
    test_all()
