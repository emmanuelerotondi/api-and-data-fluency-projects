# 🚀 Sentiment-Aware Ticket Router

An event-driven microservice built with **FastAPI** and **Hugging Face DistilBERT** that performs real-time NLP sentiment analysis on incoming customer support complaints, dynamically routes tickets across operational queues, and triggers instant Discord webhook alerts for urgent escalations.

---

## 🛠 System Architecture & Flow

┌──────────────────────────┐
│  Incoming Support Ticket │
└─────────────┬────────────┘
│
▼
┌──────────────────────────┐      ┌───────────────────────────────────┐
│     FastAPI Endpoint     ├────► │ Hugging Face DistilBERT Model     │
│       POST /tickets      │      │ (distilbert-base-uncased-SST-2)   │
└─────────────┬────────────┘      └─────────────────┬─────────────────┘
│                                     │
│◄────────────────────────────────────┘
▼
┌──────────────────────────┐
│   Dynamic Rules Engine   │
└──────┬───────────────────┬┘
│                   │
│ Score ≤ 0.85      │ Score > 0.85
▼                   ▼
┌───────────────┐   ┌─────────────────────────────────────────────────┐
│ General Queue │   │ Tier 3 Specialist Support + Discord Webhook 🚨   │
└───────────────┘   └─────────────────────────────────────────────────┘


---

## 💻 Tech Stack

* **API & Web Framework:** FastAPI, Uvicorn, Pydantic
* **Machine Learning / NLP:** Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`)
* **Alerting & Escalations:** Discord Webhooks (Structured JSON Embed Cards)
* **Testing & Quality Assurance:** Postman Collections, Python `requests` CLI Runner, Newman
* **Security & DevSecOps:** Credential isolation via `python-dotenv` & `.gitignore`
* **Dataset Ground Truth:** CFPB (Consumer Financial Protection Bureau) Complaint Database

---

## ✨ Key Features

1. **Real-Time Sentiment Classification:** Scores incoming ticket text on a normalized confidence scale ($0.0$ to $1.0$).
2. **Automated Incident Escalation:**
   * **Score $> 0.85$ (Urgent):** Pushes a rich, formatted alert card to Discord's `#angry-tickets` channel containing Complaint ID, Product, Company, Target Queue, and truncated Narrative snippet.
   * **Score $\le 0.85$ (Normal):** Silently routes tickets to standard operational queues.
3. **Live Operational Analytics:** `/tickets/stats` endpoint tracks live system state, total processed volumes, and queue distribution ratios.
4. **DevSecOps Security:** Sensitive API credentials and webhook tokens are managed via environment variables (`.env`) and explicitly ignored in version control.
5. **Automated CLI Test Suite:** Command-line runner (`day6_cli_runner.py`) validates HTTP status codes (`201`, `200`), payload structures, and dynamic endpoint state.

---

## 📊 Day 6 Reality Evaluation Matrix

To grade model performance against real ground truth, sentiment predictions were benchmarked against actual historical CFPB complaint outcomes (untimely responses, formal disputes, and monetary settlements):

| Metric | Output / Value |
| :--- | :--- |
| **Total Complaints Analyzed** | `204` |
| **Predicted Urgent (> 0.85)** | `204` |
| **Actual Critical Outcomes** | `4` |
| **Correctly Caught (True Positives)** | `4` |
| **Over-Escalated (False Positives)** | `200` |
| **Missed Escalations (False Negatives)** | `0` |
| **Recall (Catch Rate)** | **`100.0%`** |
| **Precision (Accuracy)** | **`2.0%`** |

### 💡 Strategic Engineering Takeaway
* **100% Recall Safety Net:** High negative sentiment serves as an effective zero-drop safety net, ensuring zero high-risk or disputed complaints bypass operational attention.
* **Production Recommendation:** Because consumer complaint datasets inherently skew negative, production routing should adopt a **hybrid rules engine**—combining sentiment scores ($> 0.85$) with operational metadata (such as monetary loss thresholds $> \$1,000$ or explicit legal terms) to eliminate false positives and prevent alert fatigue.

---

## 📂 Repository Structure

```text
sentiment-aware-ticket-router/
├── day3_router.py          # Core FastAPI server with DistilBERT & Discord Webhooks
├── day5_bulk_test.py        # Real-time traffic simulator for bulk complaints
├── day6_reality_check.py   # Ground-truth evaluation script against CFPB outcomes
├── day6_cli_runner.py      # Automated CLI testing script
├── collection.json         # API test suite specification
├── environment.json        # Test environment variables
├── complaints_subset.json  # Raw historical CFPB complaints
├── scored_complaints.json  # Pre-scored historical dataset
├── .env.example            # Environment template for credential configuration
├── .gitignore              # Ignored files (.env, venv/, caches)
└── README.md               # Project documentation