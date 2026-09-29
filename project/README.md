# ⚡ InfraPulse AI — Autonomous SRE Agent Powered by Hindsight Cloud

> **HackwithHyderabad 3.0** • Track: Enterprise AI & Agentic Memory  
> *Transforming dead postmortems and painful 3 AM outages into active, persistent institutional muscle memory.*

---

## 1. Project Overview
**InfraPulse AI** is an enterprise-grade Site Reliability Engineering (SRE) and IT Infrastructure Support agent that learns from historical incident logs, resolution outcomes, and failed remediation attempts. 

Unlike traditional LLM assistants that treat every incident as an isolated prompt, InfraPulse AI uses **Vectorize Hindsight Cloud** as its central memory layer. Every time an engineer or agent diagnoses a server failure, tests a remediation, or discovers a dangerous command, Hindsight commits that experience to a dedicated **Memory Bank**. When a new alert fires, the agent recalls past failures to actively halt destructive runbook commands and recommend verified safe remediations.

---

## 2. Real Business Problem
In cloud-native enterprises, production downtime costs between **$5,000 and $100,000+ per minute**. 

When a critical P1 alert triggers at 3 AM:
1. **On-Call Amnesia:** Junior or rotating on-call engineers repeat catastrophic mistakes that were documented 3 months ago in a buried postmortem wiki (e.g., executing a naive container restart that triggers a cascading database outage).
2. **Context Loss:** Different team leads enforce strict constraints (e.g., *“Never restart Redis between 09:00 - 15:00 IST without throttling payment workers first”*), but these rules exist only in human heads.
3. **Reactive Firefighting:** Engineering teams fix symptoms over and over rather than reflecting on systemic architectural vulnerabilities across incidents.

---

## 3. The Solution
InfraPulse AI provides a continuous learning loop for cloud reliability:
- **Halts Dangerous Commands:** Recalls past failed commands (`kubectl restart`, `purge_queue`, `ethtool reset`) and warns the engineer before catastrophic execution.
- **Enforces Lead SRE Policies:** Recalls team rules, maintenance windows, and customer-specific SLA constraints.
- **Continuous Improvement:** Evolves from a naive assistant (Interaction 1) into an autonomous, predictive SRE (Interaction 10).
- **Systemic Reflection:** Uses `reflect()` to synthesize patterns across multiple incidents, diagnosing root architectural flaws.

---

## 4. Why Hindsight is Central
Hindsight is not an optional feature or a simple chat log. It is the **brain and experience accumulator** of the agent:
- Without Hindsight, the agent gives textbook advice (`kubectl rollout restart pod`) that causes a 48-minute database blackout.
- With Hindsight, the agent recalls **Incident #INC-402**, halts the restart, cites Lead SRE Maya Krishnan's safe protocol, and executes a canary drain that saves $300,000+ in transaction losses.

---

## 5. Architecture
The system integrates an interactive frontend, high-throughput FastAPI backend, Groq LLM inference, Google Search Grounding for real-time CVEs/patches, and a dedicated Hindsight Cloud Memory Bank.

---

## 6. Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    User([SRE / On-Call Engineer]) -->|Interacts via UI| WebApp[Streamlit / React Ops Dashboard]
    WebApp -->|HTTP / REST| API[FastAPI Backend Engine]
    
    subgraph Agent Loop
        API --> SREAgent[InfraPulse SRE Agent]
        SREAgent -->|1. Ingest Alert Telemetry| Ctx[Live Incident & Server Context]
        SREAgent -->|2. recall()| MB[(Hindsight Memory Bank)]
        MB -->|Past Failures & Rules| SREAgent
        SREAgent -->|3. Grounding & CVEs| Search[Google Search Grounding]
        SREAgent -->|4. Reason over Experience| LLM[Groq Qwen-2.5 / Gemini 2.5]
        LLM -->|5. Verified Safe Runbook| SREAgent
        SREAgent -->|6. retain() New Lesson| MB
        SREAgent -->|7. reflect() Meta-Analysis| Reflection[Systemic Policy Synthesis]
        Reflection --> MB
    end

    SREAgent -->|Side-by-Side Diagnosis| WebApp
```

---

## 7. Technology Stack
- **Central Memory Layer:** Hindsight Cloud by Vectorize (`mb_infrapulse_sre_prod_01`)
- **LLM Reasoning Engine:** Groq API (`qwen/qwen3-32b` or `openai/gpt-oss-120b`) with Google Gemini 2.5/3.5 Flash fallback
- **Real-Time Web Grounding:** Google Search Grounding for upstream CVEs and kernel advisories
- **Backend Framework:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, HTTPX
- **Frontend Dashboard:** Streamlit & Modern React Dashboard
- **Testing:** Pytest test suite with mock & integration tests

---

## 8. Hindsight Setup & Dedicated Memory Bank
1. Sign up for [Vectorize Hindsight Cloud](https://vectorize.io).
2. Create a dedicated Memory Bank named:
   ```
   mb_infrapulse_sre_prod_01
   ```
3. Retrieve your `HINDSIGHT_API_KEY` and configure it in `.env`.
*(Note: InfraPulse AI includes an integrated local memory cache that seamlessly mirrors Hindsight Cloud for 100% offline reliability during live demo judging).*

---

## 9. Environment Variables (`.env.example`)
```env
# Vectorize Hindsight Cloud Configuration
HINDSIGHT_API_KEY="your-hindsight-cloud-api-key"
HINDSIGHT_API_URL="https://api.vectorize.io/v1/hindsight"
HINDSIGHT_MEMORY_BANK_ID="mb_infrapulse_sre_prod_01"

# LLM Providers
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="qwen/qwen3-32b"
GEMINI_API_KEY="your-gemini-api-key"

# Server Ports
BACKEND_HOST="0.0.0.0"
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

---

## 10. Installation
```bash
# Clone the repository
git clone https://github.com/hackwithhyderabad/infrapulse-ai.git
cd infrapulse-ai/project

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 11. Running Locally
```bash
# 1. Seed the Hindsight Memory Bank
python data/seed_data.py

# 2. Start the FastAPI Backend (Terminal 1)
python backend/main.py

# 3. Start the Streamlit Frontend (Terminal 2)
streamlit run frontend/app.py --server.port 8501
```

Open `http://localhost:8501` to access the Streamlit UI.

---

## 12. Seed Data
The dataset includes realistic enterprise context:
- **10 Enterprise Customers:** RazorPay, HealthGuard MedCloud, Nexus Logistics, FinEdge Trading, etc.
- **20+ Detailed Incident Memories:** Documenting historical P1/P2 outages across Redis, PostgreSQL, Envoy Ingress, RabbitMQ, Kafka, Ceph, and Slurm.
- **Catastrophic Outage Records:** Real failure commands (`rollout restart`, `purge_queue`, `ethtool reset`) and the exact damage they caused.

---

## 13. 60-Second Demo Walkthrough
1. **0–15s: The Naive Disaster**  
   Simulate a 3 AM P1 alert on `redis-orders-cache`. Click *"Without Memory"*. Generic AI recommends `kubectl rollout restart deployment`.
2. **15–30s: Hindsight Intervenes**  
   Click *"With Hindsight Memory"*. The agent immediately blocks the restart, citing **Incident #INC-402**, where that exact command crashed the database during morning traffic.
3. **30–45s: Verified Execution & `retain()`**  
   The agent prescribes Maya Krishnan's verified canary drain runbook. Click *"Retain Outcome"*, committing the updated latency metric to Hindsight.
4. **45–60s: Meta-Reflection with `reflect()`**  
   Trigger the Reflection Engine. Hindsight synthesizes across 4 incidents that connection pool crashes are caused by unbuffered worker ingress, outputting an autonomous mitigation policy.

---

## 14. Explanation of `retain()`
```python
record = hindsight_bank.retain(RetainPayload(
    customer_id="CUST-001",
    customer_name="RazorPay Financial Networks",
    incident_id="INC-402",
    service="redis-orders-cache",
    symptom="Connection pool timeout during peak checkout",
    naive_attempt="kubectl rollout restart deployment redis-orders-cache",
    outcome_of_naive_attempt="Dropped 48k transactions, crashed Aurora database",
    verified_remediation="Throttle payment workers to 20%, unlink stale keys, canary drain",
    rule_learned="Zero cold restarts between 09:00 - 15:00 IST without throttling workers"
))
```
*Stores specific negative commands, destructive outcomes, and verified fixes into long-term memory.*

---

## 15. Explanation of `recall()`
```python
memories = hindsight_bank.recall(RecallQuery(
    query="redis orders cache timeout razorpay",
    customer_id="CUST-001",
    service="redis-orders-cache",
    top_k=3
))
```
*Retrieves relevant historical incidents when a new alert occurs, matching by service topology, symptoms, and customer constraints.*

---

## 16. Explanation of `reflect()`
```python
reflection = hindsight_bank.reflect(
    topic="recurring connection pool failures",
    customer_id="CUST-001"
)
```
*Performs meta-analysis across all stored memories to identify underlying architectural flaws (e.g. unbuffered gRPC ingress) rather than isolated symptoms.*

---

## 17. How Persistent Memory Works
Hindsight memory persists across:
- **Multiple Conversations:** Different on-call shifts share the exact same organizational knowledge.
- **Multiple Sessions:** Server reboots and fresh agent containers retain full historical memory.
- **Different Days & Months:** Insights gained in June prevent repeat incidents in September.

---

## 18. Before vs. After Memory Comparison

| Dimension | WITHOUT HINDSIGHT MEMORY | WITH HINDSIGHT MEMORY |
| :--- | :--- | :--- |
| **Recommendation** | `kubectl rollout restart deployment` | 🛑 **BLOCKED:** Throttles workers, unlinks keys, executes canary drain |
| **Downstream Awareness** | Blind to Aurora DB connection limits | Aware of 3,000 connection ceiling and cascading failure risks |
| **Team Constraints** | Ignorant of lead engineer policies | Enforces Maya Krishnan's peak-hour embargo rule |
| **Outcome** | 48-minute database crash ($300k loss) | 100% uptime preserved; zero dropped transactions |

---

## 19. Deployment Instructions
To deploy the FastAPI backend and Streamlit frontend using Docker:
```bash
# Build & run with docker-compose
docker-compose up --build
```
Or deploy to Cloud Run / AWS ECS by setting `BACKEND_HOST=0.0.0.0` and mapping ports `8000` and `8501`.

---

## 20. Troubleshooting
- **Hindsight API Timeout:** The system automatically falls back to the embedded JSON Memory Bank store, ensuring 100% demo stability without breaking.
- **LLM Rate Limits:** If Groq key reaches rate limits, the agent smoothly transitions to Gemini 2.5 Flash or deterministic reasoning templates.

---

## 21. Future Improvements
- **Kubernetes Webhook Admission Controller:** Auto-intercept dangerous commands typed directly into `kubectl` by humans.
- **Bi-directional Slack/PagerDuty Bot:** Autonomous triage agent embedded in incident response channels.
- **Automated Chaos Engineering Verification:** Periodically re-validating retained postmortem fixes against staging environments.
