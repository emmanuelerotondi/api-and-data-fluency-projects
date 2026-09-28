import json
import os
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Sentiment-Aware Ticket Router",
    description="Automated routing API for financial consumer complaints based on sentiment scoring.",
    version="1.0.0"
)

DATA_FILE = "scored_complaints.json"

def load_scored_data():
    """Helper function to load scored dataset."""
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail=f"Data file '{DATA_FILE}' not found. Run Day 2 first.")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_routing_rules(tickets):
    """Applies priority routing tags based on sentiment score thresholds."""
    routed_tickets = []
    for ticket in tickets:
        item = ticket.copy()
        label = item.get("sentiment_label", "UNKNOWN")
        score = item.get("sentiment_score", 0.0)

        # Priority Routing Logic
        if label == "NEGATIVE" and score >= 0.90:
            item["routing_priority"] = "URGENT_ESCALATION"
            item["target_queue"] = "Tier 3 Specialist Support"
        elif label == "NEGATIVE" and score >= 0.70:
            item["routing_priority"] = "HIGH_PRIORITY"
            item["target_queue"] = "Tier 2 Escalations"
        elif label == "POSITIVE":
            item["routing_priority"] = "LOW_PRIORITY"
            item["target_queue"] = "Customer Feedback & Retention"
        else:
            item["routing_priority"] = "STANDARD_QUEUE"
            item["target_queue"] = "Tier 1 Support"

        routed_tickets.append(item)
    return routed_tickets

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Sentiment-Aware Ticket Router API",
        "docs_url": "http://127.0.0.1:8000/docs"
    }

@app.get("/tickets")
def get_all_tickets(limit: int = Query(default=50, ge=1, le=200)):
    """Retrieve all tickets with routing rules applied."""
    tickets = load_scored_data()
    routed = apply_routing_rules(tickets)
    return {
        "total_available": len(routed),
        "returned_count": len(routed[:limit]),
        "tickets": routed[:limit]
    }

@app.get("/tickets/urgent")
def get_urgent_tickets():
    """Filter tickets requiring immediate Tier 3 intervention."""
    tickets = load_scored_data()
    routed = apply_routing_rules(tickets)
    urgent = [t for t in routed if t["routing_priority"] == "URGENT_ESCALATION"]
    return {
        "urgent_count": len(urgent),
        "tickets": urgent
    }

@app.get("/tickets/stats")
def get_routing_stats():
    """Summary statistics across all ticket routing queues."""
    tickets = load_scored_data()
    routed = apply_routing_rules(tickets)

    priority_counts = {}
    queue_counts = {}

    for t in routed:
        p = t["routing_priority"]
        q = t["target_queue"]
        priority_counts[p] = priority_counts.get(p, 0) + 1
        queue_counts[q] = queue_counts.get(q, 0) + 1

    return {
        "total_tickets_processed": len(routed),
        "priority_distribution": priority_counts,
        "queue_distribution": queue_counts
    }