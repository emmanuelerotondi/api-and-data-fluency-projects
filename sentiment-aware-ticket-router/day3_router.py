import json
import os
import time
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
from day2_sentiment import query_sentiment

app = FastAPI(
    title="Sentiment-Aware Ticket Router",
    description="Automated routing API for financial consumer complaints based on sentiment scoring.",
    version="1.0.0"
)

DATA_FILE = "scored_complaints.json"

class TicketCreate(BaseModel):
    product: str = "Credit card or other prepaid card"
    issue: str = "Billing dispute / Unauthorized charges"
    narrative: str
    company: str = "Global Financial Bank"
    state: str = "NY"

def load_scored_data():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail=f"Data file '{DATA_FILE}' not found.")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_scored_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def assign_routing(item):
    label = item.get("sentiment_label", "UNKNOWN")
    score = item.get("sentiment_score", 0.0)

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
    return item

@app.get("/")
def root():
    return {"status": "online", "docs_url": "http://127.0.0.1:8000/docs"}

@app.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate):
    """Creates a new ticket, scores narrative sentiment on the fly, and routes it."""
    label, score = query_sentiment(payload.narrative)
    
    tickets = load_scored_data()
    new_id = str(int(time.time()))
    
    new_ticket = {
        "complaint_id": new_id,
        "date_received": time.strftime("%Y-%m-%d"),
        "product": payload.product,
        "issue": payload.issue,
        "company": payload.company,
        "state": payload.state,
        "narrative": payload.narrative,
        "sentiment_label": label,
        "sentiment_score": score
    }
    
    routed_ticket = assign_routing(new_ticket)
    tickets.insert(0, routed_ticket)
    save_scored_data(tickets)
    
    return routed_ticket

@app.get("/tickets")
def get_all_tickets(limit: int = Query(default=50, ge=1, le=200)):
    tickets = load_scored_data()
    routed = [assign_routing(t) for t in tickets]
    return {
        "total_available": len(routed),
        "returned_count": len(routed[:limit]),
        "tickets": routed[:limit]
    }

@app.get("/tickets/urgent")
def get_urgent_tickets():
    tickets = load_scored_data()
    routed = [assign_routing(t) for t in tickets]
    urgent = [t for t in routed if t["routing_priority"] == "URGENT_ESCALATION"]
    return {"urgent_count": len(urgent), "tickets": urgent}

@app.get("/tickets/stats")
def get_routing_stats():
    tickets = load_scored_data()
    routed = [assign_routing(t) for t in tickets]

    priority_counts, queue_counts = {}, {}
    for t in routed:
        p, q = t["routing_priority"], t["target_queue"]
        priority_counts[p] = priority_counts.get(p, 0) + 1
        queue_counts[q] = queue_counts.get(q, 0) + 1

    return {
        "total_tickets_processed": len(routed),
        "priority_distribution": priority_counts,
        "queue_distribution": queue_counts
    }

@app.get("/tickets/{ticket_id}")
def get_ticket_by_id(ticket_id: str):
    """Lookup a single ticket by ID."""
    tickets = load_scored_data()
    for t in tickets:
        if str(t["complaint_id"]) == str(ticket_id):
            return assign_routing(t)
    raise HTTPException(status_code=404, detail="Ticket not found")