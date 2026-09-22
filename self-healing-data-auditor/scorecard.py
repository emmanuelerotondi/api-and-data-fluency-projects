from collections import Counter
import json
import os

# Resolve paths dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, "raw_nasa_data.json")
CLEAN_PATH = os.path.join(BASE_DIR, "clean_asteroids.json")
QUARANTINE_PATH = os.path.join(BASE_DIR, "quarantine.json")


def load_json(filepath):
    if not os.path.exists(filepath):
        return [] if "json" in filepath else {}
    with open(filepath, "r") as f:
        return json.load(f)


def generate_scorecard():
    raw_data = load_json(RAW_PATH)
    clean_records = load_json(CLEAN_PATH)
    quarantine_records = load_json(QUARANTINE_PATH)

    # 1. Count total raw asteroids ingested across all dates
    total_raw = 0
    neo_days = (
        raw_data.get("near_earth_objects", {})
        if isinstance(raw_data, dict)
        else {}
    )
    for date_str, asteroid_list in neo_days.items():
        total_raw += len(asteroid_list)

    total_clean = len(clean_records)
    total_quarantined = len(quarantine_records)

    # Calculate percentages
    clean_pct = (total_clean / total_raw * 100) if total_raw > 0 else 0
    quarantine_pct = (
        (total_quarantined / total_raw * 100) if total_raw > 0 else 0
    )

    # 2. Identify the most common quarantine reason
    errors = [
        q.get("error_reason", "Unknown error") for q in quarantine_records
    ]
    most_common_error = Counter(errors).most_common(1)
    top_error_msg = (
        most_common_error[0][0]
        if most_common_error
        else "None (100% Pass Rate!)"
    )

    # Print executive summary scorecard
    print("\n" + "=" * 45)
    print("        📊 PIPELINE SCORECARD REPORT        ")
    print("=" * 45)
    print(f"Total Raw Records Ingested:  {total_raw}")
    print(f"✅ Clean & Auto-Repaired:    {total_clean} ({clean_pct:.1f}%)")
    print(
        f"⚠️ Quarantined for Review:   {total_quarantined} ({quarantine_pct:.1f}%)"
    )
    print("-" * 45)
    print(f"Top Quarantine Reason:\n  -> {top_error_msg}")
    print("=" * 45 + "\n")


if __name__ == "__main__":
    generate_scorecard()