import json
import os
from jsonschema import ValidationError, validate

# Resolve paths dynamically to target clean_schema.json in this folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "clean_schema.json")

# Load blueprint definition
with open(SCHEMA_PATH, "r") as file:
    schema = json.load(file)

# Hand-written clean record matching your schema rules
sample_clean_asteroid = {
    "id": "2000433",
    "name": "433 Eros (1898 DQ)",
    "is_potentially_hazardous": False,
    "estimated_diameter_meters": 16840.0,
    "velocity_km_per_sec": 24.35,
    "orbiting_body": "Earth",
}

try:
    validate(instance=sample_clean_asteroid, schema=schema)
    print("✅ SUCCESS: Sample record passed JSON Schema validation!")
except ValidationError as error:
    print(f"❌ VALIDATION ERROR: {error.message}")