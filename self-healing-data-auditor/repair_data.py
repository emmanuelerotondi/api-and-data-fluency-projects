import json
import os
from jsonschema import ValidationError, validate

# Resolve paths dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "raw_nasa_data.json")
SCHEMA_PATH = os.path.join(BASE_DIR, "clean_schema.json")
CLEAN_OUTPUT_PATH = os.path.join(BASE_DIR, "clean_asteroids.json")
QUARANTINE_OUTPUT_PATH = os.path.join(BASE_DIR, "quarantine.json")


def load_json(filepath):
    """Loads and parses a JSON file."""
    with open(filepath, "r") as file:
        return json.load(file)


def repair_record(raw_item):
    """Self-healing function: Standardizes unit systems and data types.

    - Converts velocity strings (e.g. "24.35") to float numbers.
    - Calculates average diameter in meters as a float.
    - Standardizes key names to match clean_schema.json.
    """
    # 1. Safely extract ID and Name as text strings
    asteroid_id = str(raw_item.get("id", ""))
    name = str(raw_item.get("name", ""))

    # 2. Extract hazardous flag as a boolean
    is_hazardous = bool(raw_item.get("is_potentially_hazardous_asteroid", False))

    # 3. Calculate average diameter in meters (float)
    diameter_info = raw_item.get("estimated_diameter", {}).get("meters", {})
    min_meters = float(diameter_info.get("estimated_diameter_min", 0.0))
    max_meters = float(diameter_info.get("estimated_diameter_max", 0.0))
    avg_diameter_meters = (min_meters + max_meters) / 2.0

    # 4. Convert velocity string (km/s) into a float
    close_approach = raw_item.get("close_approach_data", [])
    if close_approach:
        first_approach = close_approach[0]
        vel_str = (
            first_approach.get("relative_velocity", {})
            .get("kilometers_per_second", "0.0")
        )
        velocity_km_s = float(vel_str)
        orbiting_body = first_approach.get("orbiting_body", "Earth")
    else:
        velocity_km_s = 0.0
        orbiting_body = "Earth"

    # Construct standardized clean record dictionary
    return {
        "id": asteroid_id,
        "name": name,
        "is_potentially_hazardous": is_hazardous,
        "estimated_diameter_meters": round(avg_diameter_meters, 2),
        "velocity_km_per_sec": round(velocity_km_s, 2),
        "orbiting_body": orbiting_body if orbiting_body else "Earth",
    }


def main():
    raw_data = load_json(RAW_DATA_PATH)
    schema = load_json(SCHEMA_PATH)

    clean_records = []
    quarantined_records = []

    # Extract asteroid lists from raw NASA date structure
    neo_days = raw_data.get("near_earth_objects", {})

    for date_str, asteroid_list in neo_days.items():
        for item in asteroid_list:
            try:
                # 1 & 2. Apply self-healing transformation
                healed_record = repair_record(item)

                # 3. Validate healed record against schema rules
                validate(instance=healed_record, schema=schema)

                # If validation passes, add to clean list
                clean_records.append(healed_record)

            except Exception as error:
                # 4. If repair or validation fails, route to quarantine
                quarantined_records.append(
                    {
                        "raw_id": item.get("id"),
                        "error_reason": str(error),
                        "original_record": item,
                    }
                )

    # Save outputs to disk
    with open(CLEAN_OUTPUT_PATH, "w") as f:
        json.dump(clean_records, f, indent=4)

    with open(QUARANTINE_OUTPUT_PATH, "w") as f:
        json.dump(quarantined_records, f, indent=4)

    print("--- 🛠️ Self-Healing Pipeline Execution Complete ---")
    print(
        f"✅ Saved {len(clean_records)} clean records to 'clean_asteroids.json'"
    )
    print(
        f"⚠️ Saved {len(quarantined_records)} failing records to 'quarantine.json'"
    )


if __name__ == "__main__":
    main()