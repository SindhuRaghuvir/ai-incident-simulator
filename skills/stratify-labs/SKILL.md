---
name: stratify-labs
description: The source of truth for Stratify Labs, the AI knowledge-base SaaS company behind the AI Incident Simulator — its product, plans and prices, rate limits, API key types, SLAs, severity levels, support response times, contacts, compliance, integrations, and voice. Use this skill whenever you write, check, or answer anything about Stratify Labs (a customer reply, a doc, a runbook, an RCA, a QBR, test data, a new knowledge-base article, or a question like "what's the Pro rate limit?"), even if the user just says "Stratify" or "our product", so every number and policy stays consistent with the knowledge base.
---

# Stratify Labs — Company Reference

Stratify Labs is a fictional B2B SaaS company: an AI-powered knowledge-base platform. Customers upload documents (help articles, wikis, runbooks, resolved tickets) into **collections**, and Stratify answers questions over them with retrieval-augmented generation (RAG). It powers customer chatbots, internal assistants, and agent-assist in Zendesk.

It is the company in Sindhu's **AI Incident Simulator** portfolio app (`/Users/sindhu/claude`, live at ai-incident-simulator-ctnjdzv8zkkshgbnxwcykt.streamlit.app), which she uses to demonstrate TAM and AI Support Engineer skills.

## How to use this skill

1. Read `references/facts.md` before stating any Stratify number, limit, price, timeline, or policy. It condenses all 14 knowledge-base docs. Never invent a figure that isn't there: invented numbers that contradict the KB break the illusion of a real company, and the simulator's chatbot will contradict you.
2. If you need detail beyond the fact sheet, read the full KB doc. The docs live in `knowledge_base/` in the app repo (`/Users/sindhu/claude/knowledge_base/` on Sindhu's machine). `references/facts.md` lists which doc covers what.
3. If something genuinely isn't defined anywhere, say so and propose a value that fits the existing pattern (for example, Starter < Professional < Enterprise). Flag it as new so it can be added to the KB.

## Voice

Stratify writes like a calm, competent support engineer:
- Plain English, short sentences, numbered steps for anything procedural
- Lead with the answer, then the steps, then how to get more help
- Exact UI paths in bold: **Settings > API Keys**
- Confident, never apologetic filler. Acknowledge impact once, then focus on what happens next.
- Never ask for a full API key; ask for the prefix (first 10 characters)

## Adding to the knowledge base

New KB docs go in `knowledge_base/*.md` using the existing shape: `# Title`, `## Section`, `### Question as a customer would ask it?` followed by a direct answer. After adding or editing any doc, rebuild the search index so the app doesn't re-embed on startup:

```bash
cd /Users/sindhu/claude && python3 -c "import rag_engine; print(rag_engine.build_index())"
```

Then commit `knowledge_base/` and `kb_index/` together, and update `references/facts.md` if the new doc adds facts.
