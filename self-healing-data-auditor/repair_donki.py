import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DONKI_DATA_PATH = os.path.join(BASE_DIR, "raw_donki_data.json")
CLEAN_DONKI_PATH = os.path.join(BASE_DIR, "clean_donki.json")
QUARANTINE_DONKI_PATH = os.path.join(BASE_DIR, "quarantine_donki.json")


def audit_donki_relationships():
    if not os.path.exists(DONKI_DATA_PATH):
        print("❌ 'raw_donki_data.json' not found. Run get_donki_data.py first.")
        return

    with open(DONKI_DATA_PATH, "r") as f:
        records = json.load(f)

    # 1. Index all primary IDs present in this dataset
    known_event_ids = {
        item.get("activityID") for item in records if item.get("activityID")
    }

    clean_events = []
    quarantined_events = []

    # 2. Inspect every record for missing foreign keys (orphaned references)
    for record in records:
        activity_id = record.get("activityID", "UNKNOWN")
        linked_events = record.get("linkedEvents") or []

        broken_references = []

        for ref in linked_events:
            ref_id = ref.get("activityID")
            # Check if referenced ID exists in our primary lookup table
            if ref_id and ref_id not in known_event_ids:
                broken_references.append(ref_id)

        # 3. Route clean vs. broken relationship records
        if broken_references:
            quarantined_events.append(
                {
                    "activityID": activity_id,
                    "error_type": "RELATIONAL_INTEGRITY_ERROR (Orphaned Reference)",
                    "missing_target_ids": broken_references,
                    "original_record": record,
                }
            )
        else:
            clean_events.append(
                {
                    "activityID": activity_id,
                    "catalog": record.get("catalog", "M2M_CATALOG"),
                    "startTime": record.get("startTime"),
                    "linked_event_count": len(linked_events),
                    "linkedEvents": linked_events,
                }
            )

    # Save outputs
    with open(CLEAN_DONKI_PATH, "w") as f:
        json.dump(clean_events, f, indent=4)

    with open(QUARANTINE_DONKI_PATH, "w") as f:
        json.dump(quarantined_events, f, indent=4)

    total = len(records)
    print("\n" + "=" * 50)
    print("   🌌 DONKI RELATIONAL INTEGRITY AUDIT COMPLETE   ")
    print("=" * 50)
    print(f"Total Space Weather Events Audited: {total}")
    print(
        f"✅ Verified & Clean Relationships:   {len(clean_events)} ({len(clean_events)/total*100:.1f}%)"
    )
    print(
        f"⚠️ Orphaned/Broken Foreign Keys:    {len(quarantined_events)} ({len(quarantined_events)/total*100:.1f}%)"
    )
    print("=" * 50 + "\n")


if __name__ == "__main__":
    audit_donki_relationships()