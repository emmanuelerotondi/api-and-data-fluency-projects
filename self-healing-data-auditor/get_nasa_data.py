import json
import os
import ssl
import urllib.request

# 1. Fetch your NASA API Key stored in your terminal environment
api_key = os.environ.get("NASA_API_KEY")

# Fallback check if the key isn't detected
if not api_key:
    print(
        "⚠️ Could not find NASA_API_KEY in environment. Using DEMO_KEY instead."
    )
    api_key = "DEMO_KEY"
else:
    print("🔑 Loaded NASA_API_KEY successfully!")

# 2. Define the NASA API web address (requesting 7 days of asteroid data)
url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date=2026-09-01&end_date=2026-09-07&api_key={api_key}"

print("🛰️ Connecting to NASA servers...")

# Create SSL context to resolve Mac certificate check error
ssl_context = ssl._create_unverified_context()

# 3. Request the data from NASA and save it locally
try:
    with urllib.request.urlopen(url, context=ssl_context) as response:
        raw_data = response.read().decode("utf-8")
        json_data = json.loads(raw_data)

    # 4. Save the raw response into a JSON file in your folder
    with open("raw_nasa_data.json", "w") as file:
        json.dump(json_data, file, indent=4)

    total_asteroids = json_data.get("element_count", 0)
    print("✅ SUCCESS!")
    print(f"Downloaded data for {total_asteroids} asteroids.")
    print("File saved as 'raw_nasa_data.json' in your folder.")

except Exception as error:
    print(f"❌ Connection failed: {error}")