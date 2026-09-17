import json
import os

# Dynamic path resolution: targets 'raw_nasa_data.json' inside this script's folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "raw_nasa_data.json")

# 1. Load raw data using the resolved file path
with open(FILE_PATH, "r") as file:
    data = json.load(file)

near_earth_objects = data.get("near_earth_objects", {})

total_asteroids = 0
missing_orbiting_body = 0
string_velocities = 0

# 2. Loop through every date and inspect every asteroid
for date, asteroids in near_earth_objects.items():
    for asteroid in asteroids:
        total_asteroids += 1

        close_data = asteroid.get("close_approach_data", [])

        # Check for missing 'orbiting_body' field
        if (
            not close_data
            or "orbiting_body" not in close_data[0]
            or not close_data[0]["orbiting_body"]
        ):
            missing_orbiting_body += 1

        # Check if speed is stored as a text string instead of a number
        if close_data:
            vel = (
                close_data[0]
                .get("relative_velocity", {})
                .get("kilometers_per_hour")
            )
            if isinstance(vel, str):
                string_velocities += 1

# 3. Print the summary audit report
print("\n--- DAY 1 DATA AUDIT SUMMARY ---")
print(f"Total Asteroids Examined: {total_asteroids}")
print(f"Records missing 'orbiting_body': {missing_orbiting_body}")
print(f"Velocities stored as text strings instead of numbers: {string_velocities}")