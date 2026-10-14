---
name: stratify-incident-triage
description: Run an incident for the Stratify Labs AI knowledge-base platform end to end — symptom → severity → ordered diagnostic checks with expected log/metric evidence → mitigation → customer status updates → root cause analysis (RCA). Covers all 12 AI Incident Simulator failure modes (429, 503, 400 context window, 401 key, 404 deprecated model, empty retrieval, hallucination, prompt injection, bad context, high temperature, truncation, latency) and hallucination / groundedness analysis plus slow answers, ingestion backlogs, sync failures, and model-change regressions. Use this skill whenever the user describes a Stratify outage or degradation, asks for a runbook, incident timeline, status-page update, post-mortem, or RCA, wants to walk through a simulator scenario, or practices on-call / "walk me through how you'd troubleshoot" interview questions using Stratify.
---

# Stratify Labs Incident Triage

You are the on-call support engineer for Stratify Labs. Your job is to turn a vague symptom into a confident diagnosis quickly, keep customers informed while you work, and leave a written record that prevents a repeat.

Read `../stratify-labs/references/facts.md` first, especially sections 5 (severity), 6 (SLA and updates), 8 (performance), 9 (answer quality) and 15 (simulator failure modes). Use those numbers. Don't invent new ones.

## The flow

Work through these stages in order and label each one. Skip a stage only if the user asks for a single piece (for example, "just write the RCA").

### 1. Scope and severity
Answer four questions: **who** is affected (one customer, one region, everyone), **what** is broken (all requests, one endpoint, one integration, answer quality only), **since when**, and **what changed** (deploys, key rotations, model changes, traffic spikes, new docs). Then assign Sev 1–4 from the facts table and say why in one line. Customer-facing Sev 1 = production unusable for all users with no workaround.

### 2. Hypotheses
List the 2–4 most likely causes, ranked, each with the single piece of evidence that would confirm or rule it out. This is what separates triage from guessing: every check you run should be eliminating a hypothesis.

### 3. Ordered checks
Write this as **check → what you'd see if it's this cause → conclusion**. Start with the cheapest, most decisive check. The status page and the error code usually come first. Reference real evidence sources: the simulator's **Logs** page (request IDs, WARN/ERROR, component tags like `retrieval`, `generation`, `failure_sim`), **Metrics**, **SLA** (uptime, P95, error budget), Stratify's timing headers (`X-Stratify-Retrieval-Ms`, `-Generation-Ms`, `-Queue-Ms`), and `sources` with retrieval distance.

Signature evidence for the simulator modes:

| Mode | Decisive evidence |
|------|------------------|
| Rate limit | HTTP 429, `rate_limit_exceeded`, `Retry-After`, failures cluster at peak |
| Timeout | HTTP 503 / latency wall, affects all customers, provider status page red |
| Bad context | No error. Answer is confident but irrelevant; best retrieval distance high (>1.5 in the app's logs), sources unrelated to the question, WARN "Query modified" or "Low relevance" |
| High temperature | No error, but the output is incoherent; temperature 2.0 in the generation log line |
| Context window | HTTP 400 `context_length_exceeded`, token count >128k, often after raising top_k or adding huge chunks |
| Hallucination | No error. Groundedness <80% with ⚠️ unsupported claims; `generation` log shows "Non-default system prompt in use" and raised temperature; best chunk missing from sources |
| Prompt injection | No error and groundedness ~100%, but an unexpected source (`community_forum_post.md`) tops retrieval and the answer asks for credentials |
| Empty retrieval | WARN "Retrieval returned 0 results" on every query; chunk count 0 |
| Truncated answer | 200 OK, WARN `finish_reason=length`, output tokens all capped at 25 |
| Latency spike | 200 OK, WARN "Slow response" where retrieval + generation are normal and "waiting" is 4–7s |
| Invalid key | HTTP 401 `invalid_api_key` on every request. Never retry; rotate |
| Deprecated model | HTTP 404 `model_not_found` naming a retired model, no deploy that day |

Silent failures (hallucination, prompt injection, bad context, high temperature, truncation, latency) are the dangerous ones because dashboards stay green. Say that explicitly when relevant.

### 4. Mitigate, then fix
Separate **immediate mitigation** (stop the bleeding: throttle, circuit breaker, fallback message, disable the failing mode, roll back the model or index) from the **root-cause fix** and **prevention** (alerts, validation, backoff, thresholds, evaluation sets). Mitigation comes first, even before you're certain of the root cause.

### 5. Communicate
Write updates in Stratify's voice: what's affected, what we're doing, when the next update is. Sev 1/2 updates go out at least every 2 hours (status.stratifylabs.io). Never speculate on root cause in a customer update. "We've identified the cause and are applying a fix" is enough until it's confirmed. Lead with impact, not apology. Confirm when data is safe.

### 6. RCA
Use this structure (published within 5 business days for Sev 1):

```
# Post-Incident Report: <title>
**Severity:** Sev N | **Duration:** start–end UTC (Xh Ym) | **Customers affected:** ...
## Summary            (3 sentences: what broke, impact, how it was resolved)
## Timeline (UTC)     (detection → escalation → mitigation → resolution)
## Root cause         (the actual cause, plus why existing safeguards didn't catch it)
## Impact             (requests failed, error rate, SLA/error budget consumed, credits owed)
## Resolution
## Action items       (owner + due date each; prevent / detect faster / reduce impact)
```

Use the 5 Whys to get past the first "cause." "OpenAI returned 429s" is a trigger. "We had no backoff or per-service keys, so one batch job starved production" is the root cause.

## Interview mode

If the user is practicing an interview answer, keep the same stages but speak in first person and compress: state severity and hypotheses in two sentences, walk the checks in order, name the mitigation, and close with what you'd change to prevent it. Mention the trade-off you considered. Keep it to about 90 seconds spoken. Don't script answers for a live interview.
