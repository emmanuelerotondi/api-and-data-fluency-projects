# 🛠️ Self-Healing Data Auditor

An enterprise-grade, fault-tolerant Python data pipeline that ingests raw REST API feeds from NASA, enforces strict JSON Schema contracts, normalizes data types and units, and routes corrupted or orphaned records to a dead-letter quarantine queue.

## 📐 Architecture & Key Features

- **Data Contract Enforcement:** Prevents schema drift using `jsonschema` validation and strict structural boundaries (`additionalProperties: false`).
- **Self-Healing Engine:** Automatically standardizes unit systems (meters, km/s) and converts string-formatted numbers into floats.
- **Dead-Letter Queue (DLQ):** Isolates malformed or invalid records into a `quarantine.json` file with detailed diagnostic error messages without halting pipeline execution.
- **Relational Integrity Auditing:** Validates cross-record activity references in NASA DONKI space weather feeds to detect orphaned foreign keys.
- **Environment-Agnostic Paths:** Uses dynamic path resolution (`os.path.abspath`) for seamless execution across operating systems or CI/CD environments.

## 🚀 How to Run

```bash
# 1. Fetch raw asteroid data
python3 get_nasa_data.py

# 2. Run self-healing repair engine
python3 repair_data.py

# 3. Print pipeline scorecard
python3 scorecard.py

# 4. Audit space weather relational integrity
python3 get_donki_data.py
python3 repair_donki.py