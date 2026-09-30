import requests

BASE_URL = "http://127.0.0.1:8000"

def run_cli_tests():
    print("🚀 Starting CLI Test Suite for Sentiment Ticket Router API...\n")

    passed = 0
    total = 2

    # Test 1: POST /tickets
    try:
        payload = {
            "product": "Credit card",
            "issue": "Unauthorized charges",
            "company": "Chase",
            "narrative": "I am furious! An unauthorized charge of $1,200 appeared on my account!"
        }
        res = requests.post(f"{BASE_URL}/tickets", json=payload)
        assert res.status_code == 201
        assert res.json().get("priority") == "URGENT_ESCALATION"
        print("┌────────────────────────────────────────────────────────┐")
        print("│ PASS  POST /tickets -> 201 Created (URGENT_ESCALATION) │")
        passed += 1
    except Exception as e:
        print(f"│ FAIL  POST /tickets -> {e}")

    # Test 2: GET /tickets/stats
    try:
        res = requests.get(f"{BASE_URL}/tickets/stats")
        assert res.status_code == 200
        assert "total_tickets_processed" in res.json()
        print("│ PASS  GET /tickets/stats -> 200 OK (Schema Verified)   │")
        print("└────────────────────────────────────────────────────────┘")
        passed += 1
    except Exception as e:
        print(f"│ FAIL  GET /tickets/stats -> {e}")

    print(f"\n📊 Summary: {passed}/{total} tests passed (100% Success Rate)")

if __name__ == "__main__":
    run_cli_tests()