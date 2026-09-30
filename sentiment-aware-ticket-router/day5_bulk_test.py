import time
import requests

API_URL = "http://127.0.0.1:8000/tickets"

# Sample test complaints ranging from positive/neutral to severe complaints
TEST_TICKETS = [
    {
        "product": "Credit card",
        "issue": "Unauthorized charges",
        "narrative": "I am absolutely furious! An unauthorized charge of $3,500 appeared on my card and customer support hung up on me!",
        "company": "Chase",
        "state": "NY"
    },
    {
        "product": "Checking account",
        "issue": "General inquiry",
        "narrative": "Hi, I just wanted to ask what the daily ATM withdrawal limit is for my checking account. Thanks!",
        "company": "Wells Fargo",
        "state": "CA"
    },
    {
        "product": "Mortgage",
        "issue": "Foreclosure risk",
        "narrative": "Your system wrongly reported me as delinquent! My house is going into foreclosure because of your glitch! Fix this NOW or I am suing!",
        "company": "Bank of America",
        "state": "FL"
    },
    {
        "product": "Savings account",
        "issue": "Interest rates",
        "narrative": "I noticed the interest rate dropped slightly this month. Where can I find the updated rates schedule?",
        "company": "Capital One",
        "state": "TX"
    },
    {
        "product": "Student loan",
        "issue": "Payment process",
        "narrative": "I paid off my loan balance last week. How long does it take for the account status to update to zero?",
        "company": "Navient",
        "state": "IL"
    },
    {
        "product": "Credit card",
        "issue": "Identity theft",
        "narrative": "WARNING: Someone opened a card in my name without permission! My credit score was destroyed! This is illegal negligence!",
        "company": "Citibank",
        "state": "GA"
    },
    {
        "product": "Auto loan",
        "issue": "Late fees",
        "narrative": "I was charged a $25 late fee even though I paid on the 1st. Can you please refund it?",
        "company": "Ally Financial",
        "state": "OH"
    },
    {
        "product": "Credit card",
        "issue": "Card replacement",
        "narrative": "My card expired yesterday. Could you please send me a replacement card as soon as possible?",
        "company": "Discover",
        "state": "PA"
    },
    {
        "product": "Personal loan",
        "issue": "Predatory fees",
        "narrative": "You stole my money! Hidden fees added over $1,000 to my principal balance without my knowledge! I demand an immediate audit!",
        "company": "SoFi",
        "state": "NC"
    },
    {
        "product": "Checking account",
        "issue": "Mobile deposit",
        "narrative": "The mobile app deposit feature is working great, just checking on when the funds clear.",
        "company": "US Bank",
        "state": "MI"
    },
    {
        "product": "Credit card",
        "issue": "Account lockout",
        "narrative": "Locked out of my account while traveling abroad with NO access to funds! Terrible customer service refused to verify my identity!",
        "company": "American Express",
        "state": "WA"
    },
    {
        "product": "Mortgage",
        "issue": "Escrow analysis",
        "narrative": "Received my annual escrow statement today. Everything looks clear, thank you.",
        "company": "Rocket Mortgage",
        "state": "MI"
    }
]


def run_bulk_simulation():
    print("🚀 Starting Day 5 Real-Time Routing Simulation...\n")
    urgent_count = 0

    for idx, ticket in enumerate(TEST_TICKETS, 1):
        try:
            response = requests.post(API_URL, json=ticket)
            data = response.json()

            priority = data.get("routing_priority")
            queue = data.get("target_queue")
            score = data.get("sentiment_score")

            if priority == "URGENT_ESCALATION":
                status_icon = "🚨 [DISCORD ALERT TRIGGERED]"
                urgent_count += 1
            elif priority == "HIGH":
                status_icon = "⚠️  [TIER 2 ESCALATION]"
            else:
                status_icon = "✅ [GENERAL ROUTING]"

            print(
                f"Ticket #{idx:02d} | Score: {score:.4f} | Priority: {priority:<17} | Queue: {queue:<26} | {status_icon}"
            )

        except Exception as e:
            print(f"Failed to submit ticket #{idx}: {e}")

        # Brief delay to space out incoming requests
        time.sleep(1)

    print(
        f"\n🎉 Simulation Complete! Processed {len(TEST_TICKETS)} tickets. {urgent_count} urgent alerts were routed to Discord."
    )


if __name__ == "__main__":
    run_bulk_simulation()