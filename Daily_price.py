import requests
import csv
import time

API_KEY = "579b464db66ec23bdd0000017bdd73636b67464466d153f476561be5"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

limit = 1000   # records per request (safe value)
offset = 0
all_records = []

print("Starting download...")

while True:
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    records = data.get("records", [])

    if not records:
        break

    all_records.extend(records)
    print(f"Downloaded {len(all_records)} records...")

    offset += limit
    time.sleep(0.5)  # avoid hitting rate limits

print("Download complete.")
print(f"Total records: {len(all_records)}")

# Save to CSV
if all_records:
    keys = all_records[0].keys()

    with open("mandi_prices.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_records)

    print("Saved as mandi_prices.csv successfully ✅")
else:
    print("No records found.")