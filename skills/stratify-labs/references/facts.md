# Stratify Labs Fact Sheet

Condensed from the 15 docs in `knowledge_base/`. The doc name in brackets is where the full detail lives.

## Contents
1. Plans and pricing
2. Limits
3. API
4. Keys, roles, auth
5. Support, severity, escalation
6. Incidents, SLA, credits
7. Models and deprecations
8. Performance
9. Answer quality
10. Ingestion
11. Integrations
12. Security and compliance
13. Enterprise onboarding (TAM)
14. Contacts and URLs
15. Simulator failure modes

---

## 1. Plans and pricing [billing_and_plans, faq]

| Plan | Price | Requests/min | Requests/day | Concurrent | Collections | Support |
|------|-------|--------------|--------------|-----------|-------------|---------|
| Free Trial | Free, 14 days, no card | 10 | 1,000 | 2 | 1 (≤10k docs) | Community forums |
| Starter | $49/mo ($470/yr) | 60 | 50,000 | 10 | 5 | Email (Sev 1: 24h) |
| Professional | $199/mo ($1,910/yr) | 300 | 500,000 | 50 | Unlimited | Priority email + chat (Sev 1: 2h) |
| Enterprise | Custom | Custom | Custom | Custom | Unlimited | Dedicated engineer + TAM (Sev 1: 1h, 24/7) |

- Annual billing = 20% off (Starter, Professional). Switch at **Settings > Billing**.
- Overage: extra requests $0.002 (Starter) / $0.001 (Pro); storage $0.10 / $0.05 per GB-month; embeddings $0.0001 / $0.00005 per doc; priority processing Pro $0.005/request, Enterprise included.
- Usage charges calculated daily, billed monthly. Invoices at **Settings > Billing > Invoice History**.
- Cancellation: data kept 30 days, then permanently deleted. Reactivating within 30 days restores everything.
- Professional adds SSO, IP allowlist, EU-West region, hybrid search, reranking, Answer Cache, Permission Sync. Full Starter vs. Professional table in billing_and_plans.
- Refunds: new customers get a full refund within 7 days of their first subscription; no refunds on consumed usage; Enterprise per contract; request via support@stratifylabs.io (reply within 1 business day). Outages earn service credits (section 6), not refunds.
- **Refund processing time is deliberately undefined.** "How long do refunds take to process?" is the Failure Lab's hallucination baseline question, so never add a figure for it to the KB.

## 2. Limits [document_ingestion, integrations]

| | Free Trial | Starter | Professional | Enterprise |
|--|-----------|---------|-------------|------------|
| Max file size | 10 MB | 25 MB | 100 MB | 500 MB |
| Docs per collection | 10,000 | 50,000 | 500,000 | Custom |
| Files per bulk upload | 50 | 200 | 1,000 | Custom |
| Slack workspaces | — | 1 | 3 | Unlimited |
| Zendesk instances | — | 1 | 2 | Unlimited |
| Confluence spaces | — | 5 | 25 | Unlimited |
| Webhook endpoints | — | 3 | 10 | Unlimited |
| Sync frequency | — | 30 min | 15 min | 5 min / real-time |

File types: .txt, .md, .pdf (text-based only, no scans), .html, .csv (one row = one doc, header row required). UTF-8 only.

## 3. API [api_reference]

- Base URL `https://api.stratifylabs.io/v1/{org}/`; EU: `https://eu.api.stratifylabs.io/v1/{org}/` (wrong region → 421).
- Auth: `Authorization: Bearer ak_live_...`. Never in a query string.
- Endpoints: `POST /query` (answer + sources), `POST /search` (chunks only, <300 ms), `POST|PUT|GET|DELETE /collections/{name}/documents/{id}`, `GET /collections`, `GET /usage`.
- Streaming: `"stream": true` → SSE `token` events then `done`.
- Pagination: `limit` (default 50, max 200), `next_cursor` → `cursor`, cursors expire in 24h.
- Every response has `X-Request-Id` (e.g. `req_8f2a1c9e`). Support always wants it.
- `Idempotency-Key` header on POST; replays within 24h return the original response.
- Retry: only 429 and 5xx. Backoff 1s, 2s, 4s, 8s + 0–1s jitter, max 5 tries, honor `Retry-After`. Don't retry 400/401/403/404/409/413.
- Recommended timeouts: /search 10s, /query 30s, uploads 60s. Server hard limit 60s → 504.
- SDKs: `pip install stratifylabs`, `npm install @stratifylabs/sdk`. v1 supported ≥12 months after v2.
- First-query walkthrough (sign up → collection → key → `POST /query`) and plain definitions of collection, document, chunk, embedding, sources, top_k: [product_overview].

## 4. Keys, roles, auth [getting_started, account_and_login, security_and_compliance]

- `ak_live_` production (counts toward limits), `ak_test_` sandbox (does not count), `ak_readonly_` read-only.
- Rotation: old key valid 24h. Keys found in public GitHub repos are auto-revoked and the owner is emailed.
- Roles: Owner (one per org, billing), Admin (keys, integrations, analytics, no billing), Member. Enterprise: custom roles.
- MFA: authenticator app, SMS (not recommended), hardware key. Org-wide enforcement available.
- SSO (SAML 2.0, OIDC; Okta, Azure AD, Google Workspace, OneLogin, PingFederate): Professional+.
- 401 = missing/invalid/revoked key; 403 = valid key, no permission (read-only key, role, IP allowlist); 404 = case-sensitive collection name, empty collection, typo.

## 5. Support, severity, escalation [support_and_escalation, faq]

| Severity | Meaning | Starter | Professional | Enterprise |
|----------|---------|---------|-------------|------------|
| Sev 1 Critical | Production down for all users, no workaround | 24h | 2h | 1h, 24/7 |
| Sev 2 High | Major feature broken or badly degraded | 48h | 4h | 2h, 24/7 |
| Sev 3 Medium | Partial impact, workaround exists | 48h | 1 business day | 4 business hours |
| Sev 4 Low | How-to, questions, feature requests | 3 business days | 2 business days | 1 business day |

- First response = a human engineer, not an auto-ack. Sev 1/2: updates at least every 2 hours.
- Business hours: Mon–Fri 6 AM–6 PM Pacific.
- Escalation: reply "Please escalate" + business impact → Professional: escalations@stratifylabs.io → Enterprise: dedicated engineer/TAM, Sev 1 = 24/7 phone line.
- A good ticket has: expected vs. actual, request IDs, UTC timestamps, full error text, scope (who/what/since when), what changed.
- The simulator's runbook page labels P1/P2; map P1 = Sev 1, P2 = Sev 2 in anything customer-facing.

## 6. Incidents, SLA, credits [support_and_escalation, faq, security_and_compliance]

- Uptime SLA: Starter 99.5%, Professional 99.9%, Enterprise 99.99%. Status: status.stratifylabs.io (email, SMS, Slack, RSS).
- Incident updates every 2 hours. Post-incident report (RCA) within 5 business days for Sev 1 platform incidents.
- Security incidents: notify within 1 hour of detection.
- Service credits (request within 30 days of the month's end, billing@stratifylabs.io): ≤0.5% below SLA → 10%; 0.5–1.0% → 25%; >1.0% → 50% of monthly fee. Maintenance announced ≥72h ahead doesn't count.

## 7. Models and deprecations [models_and_deprecations]

- Answer models: **Fast** (default) and **Advanced** (~3x generation cost). Set per collection or per request (`"model": "advanced"`).
- Each collection is tied to one embedding model; mixing models in a collection gives meaningless scores.
- Notice: answer models ≥90 days, embedding models ≥6 months. Listed at status.stratifylabs.io/deprecations.
- Retired answer model → auto-routed to replacement, header `X-Stratify-Model-Redirect`. Un-migrated embedding collections go read-only (uploads → 409).
- Pinning (e.g. `fast-2026-03`) vs. moving alias (`fast`). Previews (`fast-preview`) available ≥30 days before alias moves.
- Re-index: shadow index, no downtime, ~10 min per 10k docs, **Promote** when done, rollback within 7 days. Free in the final 30 days before forced retirement.

## 8. Performance [performance_and_latency]

| Endpoint | p50 | p95 |
|----------|-----|-----|
| /search | 150 ms | 400 ms |
| /query first token (streaming) | 600 ms | 1.2 s |
| /query full answer | 2.0 s | 4.5 s |

- Timing headers: `X-Stratify-Retrieval-Ms`, `X-Stratify-Generation-Ms`, `X-Stratify-Queue-Ms` (high = concurrency limit).
- Over concurrency limit: queued up to 10s, then 429 `concurrency_limit_exceeded`.
- Idle >24h collections go to warm storage: first query +1–3s. Enterprise "Always Warm".
- Answer Cache (Pro+) at **Collections > Settings > Performance**, expires within 60 min, invalidated on doc updates.
- Launch prep: Enterprise tells TAM ≥5 business days ahead.

## 9. Answer quality [answer_quality_and_tuning, troubleshooting]

- Diagnose retrieval first: right doc missing from `sources` = retrieval problem; right doc present but answer wrong = generation problem.
- Temperature 0.0–0.3 for support content. >0.7 increases hallucination.
- Confidence threshold: start 0.70; tune in **Collections > Debug** (Retrieval Debugger).
- Strict Grounding at **Collections > Settings > Answer Behavior**.
- Chunk size: FAQ 300–500 chars, how-tos 800–1,200, long policy 1,200–2,000. Changing it requires re-indexing.
- Hybrid search and reranking (+~150 ms, +10–20% accuracy): Professional+.
- Quality signals: thumbs feedback (**Analytics > Answer Feedback**), "I don't know" rate, evaluation set of 30–100 questions (**Collections > Evaluate**). Gaps: **Analytics > Unanswered Questions**.

## 10. Ingestion [document_ingestion, getting_started]

- Statuses: Queued → Processing → Indexed / Partially indexed / Failed. Webhooks `document.indexed`, `document.failed`.
- Normal: 1–2 min per doc; large batches 20–30 min. Stuck >60 min in Processing → delete and re-upload.
- Errors: "No extractable text" = scanned PDF → OCR. "Document is encrypted" → remove password. "Invalid encoding" → save as CSV UTF-8. Partial CSV = mismatched columns / unquoted commas.
- Update with the same document ID (PUT / **Replace**). A new ID creates a duplicate.
- Delete: gone from search in 1 min, storage 24h, backups 30 days. Up to 20 metadata fields per doc.

## 11. Integrations [integrations]

- Slack: mention `@Stratify Labs`; silent bot = channel not allowlisted, key rotated (Reconnect), threshold too high, bot removed. "thinking…" is normal (3s Slack ack).
- Zendesk: only published articles sync; tokens expire; tickets sync only if tagged "knowledge-base"; PII redaction + custom regex rules; Agent Assist sidebar shows top 3 answers.
- Confluence: only selected spaces; restricted pages need Permission Sync (Pro+); deleted pages removed within 1h.
- Webhooks: HMAC-SHA256 in `X-Stratify-Signature`.
- Zendesk and Confluence sync on the plan interval: Starter 30 min, Professional 15 min, Enterprise 5 min / real-time (webhooks).
- No native Microsoft Teams, Google Drive, Notion, or SharePoint integration: use inbound webhooks / `POST /collections/{name}/documents` plus `/query`. Requests for new integrations are Sev 4 tickets.

## 12. Security and compliance [security_and_compliance]

- TLS 1.3 in transit; AES-256-GCM at rest; AWS KMS keys rotated every 90 days. Queries not logged unless enabled.
- Regions: US-East default; EU-West (Ireland) Pro+; custom residency Enterprise.
- SOC 2 Type II (report via security@stratifylabs.io, NDA). GDPR DPA at stratifylabs.io/legal/dpa; erasure within 72h; 30 days notice of new sub-processors.
- HIPAA: Enterprise with signed BAA (PHI redaction, 7-year audit logs).
- Audit logs kept 2 years (7 for HIPAA); SIEM streaming (Splunk, Datadog, Sumo Logic) on Enterprise.
- Vulnerabilities: ack 24h, severity 72h, fix timeline 1 week. Private HackerOne bounty $100–$10,000.
- Retention: query logs 90 days, analytics 1 year, backups 30 days.

## 13. Enterprise onboarding (TAM) [enterprise_onboarding]

- 4–6 weeks: Kickoff (wk 1) → Setup (1–2) → Content & tuning (2–4) → Pilot (4–5) → Go-live (5–6) → 2 weeks hypercare.
- Kickoff roles: executive sponsor, technical owner, content owner, security/IT contact. A missing content owner is the top stall risk.
- Success plan: 2–3 measurable metrics, e.g. 25% ticket deflection, ≥85% eval accuracy, 20% lower handle time, 60% weekly adoption of the pilot group.
- Collections are grouped by who searches them (e.g. `customer-help`, `agent-internal`, `engineering-runbooks`). Mixing internal and public content is the #1 onboarding mistake.
- Pilot: 20–50 users, ≥2 weeks, review unanswered questions twice a week.
- QBR: success metrics, usage and cost forecast, incidents and RCAs, upcoming deprecations, recommendations, roadmap, renewal.
- Health check twice a year: key hygiene, roles, sync health, retrieval settings, content freshness.

## 14. Contacts and URLs

| Need | Where |
|------|-------|
| Support | support@stratifylabs.io |
| Escalations (Pro) | escalations@stratifylabs.io |
| Billing and credits | billing@stratifylabs.io |
| Security, SOC 2, vulns | security@stratifylabs.io |
| Dashboard | dashboard.stratifylabs.io |
| Status | status.stratifylabs.io |
| Deprecations | status.stratifylabs.io/deprecations |
| DPA / sub-processors | stratifylabs.io/legal/dpa, /legal/sub-processors |

## 15. Simulator failure modes [failure_simulator.py in the app]

The app's Failure Lab injects twelve failures between Stratify's app and its LLM provider (OpenAI, gpt-4o-mini):

| Mode | What the user sees | Real-world cause | Fix |
|------|-------------------|------------------|-----|
| `rate_limit` | HTTP 429 `rate_limit_exceeded` | RPM/TPM quota exceeded | Backoff + jitter, queue, plan check |
| `timeout` | HTTP 503 after ~3s | Provider outage, overload, huge prompts | Timeouts, circuit breaker, fallback |
| `bad_context` | Confident, irrelevant answer; high retrieval distance | Stale embeddings, bad chunking, model drift | Relevance thresholds, re-index |
| `high_temperature` | Incoherent output (temp forced to 2.0) | Unvalidated params | Clamp temperature server-side |
| `context_window` | HTTP 400 `context_length_exceeded` (128k) | Prompt + context too large | Token counting, truncate, lower top_k |
| `hallucination` | Confident invented specifics; groundedness <80% | Best chunk missing + prompt that forbids "I don't know" | Grounding instruction, fallback, groundedness alerts, eval set |
| `prompt_injection` | Bot tells users to email their API key; groundedness still 100% | Poisoned forum post ingested and obeyed | Treat retrieved text as data, source allowlist, output filter |
| `empty_retrieval` | "No relevant documents" for everything | Index empty / not loaded | Index-size deploy gate, zero-result alert |
| `truncated_output` | Answer stops mid-sentence, 200 OK, `finish_reason=length` | max_tokens 25 | Alert on truncation, size max_tokens |
| `slow_latency` | 4–7s extra "waiting" time, no errors | Queueing / capacity | Stage latency, P95 alerts, streaming |
| `auth_error` | HTTP 401 `invalid_api_key` | Rotated / revoked key | Rotate + update secret, page on 401 |
| `model_deprecated` | HTTP 404 `model_not_found` | Retired pinned model | Model in config, deprecation tracking |

Every Chat answer gets a **hallucination check** (LLM judge, groundedness = supported claims ÷ total). Silent failures still create tickets, with the observed signal (groundedness, truncation, latency) as the ticket's evidence.

Chat's "Try asking" buttons come from `suggestions.py` (questions per KB doc, with expected facts). `eval/run_kb_eval.py` checks every one for retrieval and answer correctness; run it after any KB edit. Questions the KB deliberately can't answer (`HALLUCINATION_BAIT`) only appear while the Hallucination failure is on.

App pages for evidence: Logs (request IDs, WARN/ERROR, components incl. `eval`), Metrics, SLA (uptime, P95, error budget), Cost, Ticket Queue, RCA generator.
