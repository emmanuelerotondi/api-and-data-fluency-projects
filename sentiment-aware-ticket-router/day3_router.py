import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
from transformers import pipeline

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

app = FastAPI(
    title="Sentiment-Aware Ticket Routing API",
    description="Classifies support tickets and routes urgent complaints to Discord in real-time.",
    version="1.0.0"
)

# Load sentiment analysis model
sentiment_task = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# In-memory ticket storage
tickets_db: List[Dict] = []


class TicketCreate(BaseModel):
    product: str
    issue: str
    narrative: str
    company: Optional[str] = "N/A"
    state: Optional[str] = "N/A"


def send_discord_alert(ticket: Dict):
    """Sends a formatted embed message to Discord for URGENT tickets."""
    if not DISCORD_WEBHOOK_URL:
        print("Warning: DISCORD_WEBHOOK_URL is not set.")
        return

    payload = {
        "content": "🚨 **URGENT TICKET ESCALATION DETECTED**",
        "embeds": [
            {
                "title": f"Complaint ID: {ticket['complaint_id']}",
                "color": 15158332,  # Red
                "fields": [
                    {"name": "Product", "value": ticket["product"], "inline": True},
                    {"name": "Company", "value": ticket["company"], "inline": True},
                    {"name": "Target Queue", "value": ticket["target_queue"], "inline": True},
                    {"name": "Issue", "value": ticket["issue"], "inline": False},
                    {"name": "Narrative", "value": ticket["narrative"][:300] + "...", "inline": False},
                    {"name": "Sentiment Score", "value": str(ticket["sentiment_score"]), "inline": True},
                ],
                "footer": {"text": "Sentiment Router Bot • Real-time Routing"}
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to post alert to Discord: {e}")


@app.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate):
    # Perform sentiment analysis
    result = sentiment_task(ticket.narrative[:512])[0]
    label = result['label']
    score = round(result['score'], 4)

    # Determine priority routing
    if label == "NEGATIVE" and score > 0.85:
        priority = "URGENT_ESCALATION"
        queue = "Tier 3 Specialist Support"
    elif label == "NEGATIVE":
        priority = "HIGH"
        queue = "Tier 2 Support"
    else:
        priority = "NORMAL"
        queue = "General Support"

    # Generate ticket ID
    import random
    complaint_id = str(random.randint(1000000000, 9999999999))

    new_ticket = {
        "complaint_id": complaint_id,
        "product": ticket.product,
        "issue": ticket.issue,
        "narrative": ticket.narrative,
        "company": ticket.company,
        "state": ticket.state,
        "sentiment_label": label,
        "sentiment_score": score,
        "routing_priority": priority,
        "target_queue": queue
    }

    tickets_db.append(new_ticket)

    # Trigger Discord webhook if urgent
    if priority == "URGENT_ESCALATION":
        send_discord_alert(new_ticket)

    return new_ticket


@app.get("/tickets/urgent")
def get_urgent_queue():
    urgent = [t for t in tickets_db if t["routing_priority"] == "URGENT_ESCALATION"]
    return {"urgent_count": len(urgent), "tickets": urgent}


@app.get("/tickets/stats")
def get_stats():
    total = len(tickets_db)
    if total == 0:
        return {"total_tickets_processed": 0, "priority_distribution": {}}

    df = pd.DataFrame(tickets_db)
    dist = df["routing_priority"].value_counts().to_dict()
    return {"total_tickets_processed": total, "priority_distribution": dist}


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    for t in tickets_db:
        if t["complaint_id"] == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket not found")