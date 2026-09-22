import json
import os
import ssl
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DONKI_DATA_PATH = os.path.join(BASE_DIR, "raw_donki_data.json")

# NASA DONKI CME (Coronal Mass Ejection) Endpoint
DONKI_URL = "https://api.nasa.gov/DONKI/CME?startDate=2024-01-01&endDate=2024-01-30&api_key=DEMO_KEY"


def fetch_donki_data():
    print("Connecting to NASA DONKI Space Weather servers...")
    try:
        # Create unverified SSL context for macOS compatibility
        ssl_context = ssl._create_unverified_context()

        req = urllib.request.Request(
            DONKI_URL, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ssl_context) as response:
            data = json.loads(response.read().decode("utf-8"))

        with open(DONKI_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)

        print(
            f"✅ Downloaded {len(data)} Space Weather records to 'raw_donki_data.json'"
        )
    except Exception as e:
        print(f"❌ Failed to fetch DONKI data: {e}")


if __name__ == "__main__":
    fetch_donki_data()