# Stratify Labs — App Explainer & Interview Reference

---

## What Is the App?

**Stratify Labs Knowledge Assistant** is a production-style AI support tool I built from scratch.

At its core it's a **RAG system** — Retrieval-Augmented Generation. That means:
1. You ask a question
2. The app searches a knowledge base of documents to find relevant content
3. It sends that content + your question to OpenAI's API
4. You get an answer grounded in the actual documents

But the interesting part isn't the chat — it's everything built *around* it. The app simulates the kinds of failures that real AI systems encounter in production, and gives you the full support engineering workflow to investigate and resolve them: live metrics, structured logs, ticket queue, incident runbooks, RCA generator, SLA tracking, and resolved ticket history with full investigation reports.

---

## Why I Built It

I wanted to demonstrate that I understand not just how AI systems work, but **how they break** — and what a support engineer or TAM does when they do.

Most people applying for AI support roles can talk about LLMs in theory. I wanted to show:
- I can build a working RAG pipeline
- I understand the failure modes customers actually call about (rate limits, timeouts, context overflows, bad retrieval)
- I know how to investigate incidents using logs and metrics
- I can write RCAs, customer communications, and runbooks — not just describe them

The app is a simulator of the day-to-day work of an AI support engineer.

---

## What the Code Contains

### Core Files (root level)

| File | What it does |
|---|---|
| `app.py` | Entry point. Sets up password gate, initializes the knowledge base, defines all navigation pages |
| `rag_engine.py` | The RAG pipeline — ingests documents into ChromaDB, retrieves relevant chunks via vector search, calls OpenAI to generate answers |
| `failure_simulator.py` | Failure injection engine. Sits between the UI and the RAG engine. Checks which failures are toggled on, then raises exceptions or corrupts data accordingly |
| `metrics_store.py` | Persists every request to SQLite — model, latency, tokens, success/failure, failure mode, error message, cost |
| `logger.py` | Structured logging to SQLite — INFO/WARN/ERROR levels with component tags and request IDs |
| `config.py` | All settings in one place — model names, pricing, prompts, SLA targets, DB paths |

### Pages (what you see in the app)

| Page | What it does |
|---|---|
| **Chat** | Ask questions, get AI answers with source attribution and per-request cost/latency |
| **Failure Lab** | Toggle 5 failure modes on/off in real time. Each has an explanation of cause and fix |
| **Ticket Queue** | Live ticket queue auto-generated from failures logged in metrics. Mirrors a real support inbox |
| **Resolved Tickets** | Closed tickets with full investigation reports — timeline, error breakdown, root cause, fix, customer response |
| **Incident Runbook** | Step-by-step diagnostic and resolution guides for each failure type, with customer email templates |
| **Logs** | Structured log stream with filtering by level, component, and keyword |
| **Metrics** | Latency breakdown, token usage, success/failure rates over time |
| **Cost** | Per-request cost, cumulative spend, model pricing comparison |
| **SLA** | Uptime %, P95 latency, error budget gauge, breach detection |
| **RCA** | Auto-generates Root Cause Analysis documents from actual failure data. Downloadable as markdown |

### Failure Modes

| Mode | HTTP Code | What it simulates |
|---|---|---|
| Rate Limit | 429 | Too many requests — quota exceeded |
| Timeout | 503 | API unresponsive — service degraded |
| Bad Context | — | Corrupted retrieval — wrong docs returned |
| High Temperature | — | temperature=2.0 — incoherent output |
| Context Window | 400 | Prompt too long — 132k tokens sent, 128k limit |

### Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **LLM:** OpenAI API (gpt-4o-mini)
- **Vector DB:** ChromaDB (sentence-transformer embeddings)
- **Storage:** SQLite (metrics + logs)
- **Charts:** Plotly
- **Deployment:** Streamlit Community Cloud

---

## What Someone Sees on GitHub

**Link:** github.com/SindhuRaghuvir/ai-incident-simulator

When an interviewer opens the repo they see:

1. **README.md** — overview, architecture diagram, tech stack, setup instructions, demo flow
2. **File structure** — clean separation of concerns: core engine files at root, UI pages in `/pages/`, knowledge base docs in `/knowledge_base/`
3. **No secrets** — `.streamlit/secrets.toml` is in `.gitignore`. API keys never committed
4. **requirements.txt** — clean dependency list (streamlit, openai, chromadb, pandas, plotly)
5. **Commit history** — shows iterative development: initial build → README → feature additions → UI cleanup

---

## How to Demo It (5-Minute Walkthrough)

1. **Failure Lab** → toggle on "Rate Limit (429)"
2. **Chat** → ask any question → show the error
3. **Ticket Queue** → show the ticket that auto-generated from the failure
4. **Resolved Tickets** → open the rate_limit investigation — walk through the timeline, root cause, and customer response
5. **Logs** → show the structured log entry for the failure
6. **Metrics** → show the success rate drop
7. **Incident Runbook** → walk through the diagnostic steps
8. **RCA** → generate the post-incident document
9. **Failure Lab** → toggle off → system recovers

Full incident lifecycle — detection → investigation → resolution → documentation — in under 5 minutes.

---

## Interview Q&A

**"What is this app?"**
> A production-style RAG system with failure injection and the full support engineering workflow around it — ticket queue, incident runbooks, SLA tracking, RCA generation. It simulates the actual day-to-day of an AI support engineer.

**"Why did you build it?"**
> I wanted to demonstrate practical knowledge of how AI systems fail in production and how support engineers handle those failures. It was also a way to learn by building — I understand RAG, vector search, and the OpenAI API much better from having wired them together myself.

**"Walk me through the architecture."**
> A user question goes through the Failure Simulator first, which checks if any failures are active. If not, it hits the RAG engine — ChromaDB retrieves the top matching document chunks, those get passed to OpenAI with the question, and the answer comes back. Every request is logged to SQLite with latency, tokens, cost, and whether it succeeded. All the dashboards read from that same SQLite store.

**"How does the failure injection work?"**
> There's a `failure_simulator.py` that acts as middleware between the UI and the RAG engine. It has two hooks — `pre_retrieval()` and `pre_generation()`. Depending on which failure is toggled on in session state, it either corrupts the query, raises a real OpenAI exception (RateLimitError, APIStatusError), modifies the API parameters, or replaces the retrieved context with garbage. The RAG engine itself stays clean.

**"What failure modes does it support?"**
> Five: rate limit (429), timeout (503), bad retrieval context, high temperature, and context window exceeded (400). Each one maps to a real class of support ticket I've seen documented across OpenAI, Anthropic, and Google support forums.

**"How is data stored?"**
> Two SQLite databases — one for metrics (every request's latency, tokens, cost, success/failure) and one for structured logs (INFO/WARN/ERROR with component tags). Pandas reads from them for the dashboards. No external database needed — it all runs locally or on Streamlit Cloud.

**"What would you add next?"**
> A few things: authentication per user so multiple people can have separate sessions, a webhook that triggers alerts when failure rates spike (like PagerDuty), and a replay feature so you can re-run a failed request after toggling the failure off to confirm it resolves.

**"What was the hardest part to build?"**
> The failure simulator. Getting it to raise real OpenAI SDK exceptions (not fake ones) required constructing mock `httpx.Response` objects with the exact structure the SDK expects. If the exception type is wrong, the error handling in the chat UI doesn't catch it correctly and the wrong message shows.

**"What does a TAM actually do with something like this?"**
> Use it to onboard — understand the failure modes before a customer calls about them. Use the runbooks as a reference during an active incident. Use the RCA generator as a starting point after an incident. And use the ticket queue flow to practice the full investigation → customer communication cycle.

---

## Key Numbers to Know

| Metric | Value |
|---|---|
| gpt-4o-mini input cost | $0.150 per 1M tokens |
| gpt-4o-mini output cost | $0.600 per 1M tokens |
| gpt-4o-mini context window | 128,000 tokens |
| Default temperature used | 0.3 |
| Default top_k (chunks retrieved) | 3 |
| SLA target (default) | 99.9% uptime, <2s P95 latency |
| Monthly error budget at 99.9% | ~43 minutes of downtime |
