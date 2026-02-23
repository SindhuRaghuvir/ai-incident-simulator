# AI Incident Simulator — RAG Troubleshooting Lab

A production-style RAG (Retrieval-Augmented Generation) system with intentional failure injection, built to demonstrate AI incident response, observability, and troubleshooting workflows.

Built as both a **learning tool** and **portfolio piece** for Technical Account Manager (TAM) and AI Support Engineering roles.

## Live Demo

**https://sindhu-ai-incident-simulator.streamlit.app**
Password: `stratify2026`

## What It Does

- **RAG Pipeline** — Ingests enterprise docs, retrieves relevant chunks via vector search, generates answers with OpenAI
- **5 Failure Modes** — Rate limit (429), timeout (503), bad retrieval context, high temperature, context window exceeded (400) — toggled on/off in real time
- **Structured Logging** — Request tracing with INFO/WARN/ERROR levels, component tags, and request IDs
- **SLA Monitoring** — Uptime %, P95 latency, error budget gauge with configurable SLA targets
- **Incident Runbooks** — Step-by-step diagnosis, resolution, and customer communication templates
- **Live Ticket Queue** — auto-generates tickets from failure events, mirrors a real support inbox
- **Resolved Ticket History** — closed tickets with full investigation reports, timeline, root cause, and customer response
- **RCA Generator** — Auto-generates Root Cause Analysis documents from actual failure data
- **Cost Tracking** — Per-request cost, cumulative spend, model pricing comparison

## Architecture

```
User Question
     ↓
 Streamlit UI (9 pages)
     ↓
 Failure Simulator ← toggles from Failure Lab
     ↓
 ChromaDB Retrieval (vector search over knowledge base)
     ↓
 Failure Simulator (2nd check)
     ↓
 OpenAI API (gpt-4o-mini)
     ↓
 SQLite (metrics + structured logs)
     ↓
 Answer displayed + dashboards update
```

## Pages

| Page | What It Does |
|------|-------------|
| **Chat** | Ask questions, get AI answers with source attribution and per-request metrics |
| **Failure Lab** | Toggle 5 failure modes + educational content on causes and fixes |
| **Ticket Queue** | Live ticket queue auto-generated from failure events |
| **Resolved Tickets** | Closed tickets with full investigation reports and customer responses |
| **Incident Runbook** | Diagnostic steps, resolution guides, customer email templates |
| **Logs** | Structured log stream with filtering by level, component, and keyword |
| **Metrics** | Latency breakdown, token usage, success/failure rates |
| **Cost** | Cumulative spend, per-request cost, model pricing comparison |
| **SLA** | Uptime %, P95 latency, error budget gauge, breach tracking |
| **RCA** | Auto-generate Root Cause Analysis documents, download as markdown |

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI API (gpt-4o-mini)
- **Vector DB**: ChromaDB (with built-in sentence-transformer embeddings)
- **Metrics/Logs**: SQLite + Pandas
- **Charts**: Plotly
- **Language**: Python

## Setup

```bash
# Clone
git clone https://github.com/SindhuRaghuvir/ai-incident-simulator.git
cd ai-incident-simulator

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-your-key-here"' > .streamlit/secrets.toml

# Run
python3 -m streamlit run app.py
```

Then open http://localhost:8501

## Demo Flow (for interviews)

1. **Failure Lab** → Toggle "Stale / Bad Context"
2. **Chat** → Ask "How do I reset my API key?" → Get a confidently wrong answer
3. **Logs** → Filter to WARN/ERROR → Trace the corrupted query and high distance score
4. **SLA** → Show uptime drop and error budget burn
5. **Incident Runbook** → Walk through diagnostic and resolution steps
6. **Ticket Simulator** → Draft a customer response
7. **RCA** → Generate a post-incident report
8. **Failure Lab** → Toggle off → System recovers

Full incident lifecycle in under 5 minutes.

## Project Structure

```
├── app.py                      # Entrypoint + password gate + navigation
├── config.py                   # All settings: models, pricing, prompts
├── rag_engine.py               # Ingest, retrieve, generate (RAG pipeline)
├── metrics_store.py            # SQLite metrics persistence
├── failure_simulator.py        # 4 failure modes with pre/post hooks
├── logger.py                   # Structured logging to SQLite
├── requirements.txt
├── pages/
│   ├── chat.py                 # Chat UI + file upload + logging
│   ├── metrics_dashboard.py    # Latency, tokens, success/failure charts
│   ├── failure_lab.py          # Failure toggles + educational content
│   ├── cost_dashboard.py       # Cost tracking + model comparison
│   ├── incident_runbook.py     # Diagnosis + resolution + comms templates
│   ├── logs_viewer.py          # Structured log stream with filters
│   ├── ticket_simulator.py     # Customer ticket practice scenarios
│   ├── sla_dashboard.py        # Uptime, latency SLAs, error budgets
│   └── rca_templates.py        # RCA generator + blank templates
└── knowledge_base/
    ├── getting_started.md
    ├── billing_and_plans.md
    ├── integrations.md
    └── security_and_compliance.md
```

## License

MIT
