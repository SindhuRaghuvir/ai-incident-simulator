import streamlit as st
from datetime import datetime

import metrics_store
import failure_simulator

st.title("RCA Templates")
st.caption("Root Cause Analysis documents — what TAMs write after every major incident. Practice generating them from real failure data.")

st.divider()


# Per-mode RCA wording: impact, failing layer, technical detail, 3 action items, what to improve, process gap
RCA_DETAILS = {
    "rate_limit": ("intermittent request failures", "API gateway layer",
        "Requests exceeded the configured rate limit threshold, causing the API to return HTTP 429 responses.",
        ["Implement exponential backoff with jitter", "Add request queuing to smooth traffic spikes", "Set up usage alerts at 75% and 90% of rate limits"],
        "Detection was reactive — need proactive alerting before limits are hit",
        "Need a capacity planning review as part of customer onboarding"),
    "timeout": ("complete service outage", "upstream LLM provider",
        "The upstream LLM service experienced degraded performance, causing requests to exceed the configured timeout threshold.",
        ["Add circuit breaker pattern", "Configure fallback responses for degraded mode", "Add health check monitoring with PagerDuty"],
        "No fallback mechanism — service was fully unavailable during the outage",
        "Need a documented degraded-mode playbook"),
    "bad_context": ("degraded service quality", "retrieval/embedding pipeline",
        "The retrieval pipeline returned low-relevance results due to stale embeddings or corrupted query processing, causing the LLM to generate answers from irrelevant context.",
        ["Set up automated re-indexing pipeline", "Add relevance threshold monitoring", "Create golden test set for retrieval quality"],
        "No automated quality monitoring — degradation was noticed by users, not by our systems",
        "Need retrieval quality as a tracked SLA metric"),
    "high_temperature": ("inconsistent response quality", "configuration management layer",
        "The temperature parameter was set outside the validated range, causing non-deterministic and incoherent LLM outputs.",
        ["Add server-side parameter validation", "Lock production config behind change management", "Set up config change alerts"],
        "Configuration changes were not validated — need automated guardrails",
        "Need config change review process for production"),
    "context_window": ("requests rejected for large inputs", "prompt assembly layer",
        "Prompt plus retrieved context exceeded the model's maximum context length, so the API rejected requests with HTTP 400.",
        ["Count tokens before every API call", "Truncate or summarize context to a token budget", "Cap top-k and chunk size in config"],
        "No pre-flight token check — failures surfaced only as API errors",
        "Need input size limits documented and enforced at upload"),
    "hallucination": ("confident but fabricated answers", "generation layer (prompt and grounding)",
        "Retrieval missed the key chunk and the system prompt required a confident answer with no 'I don't know' path, so the model invented specifics. Groundedness checks showed most claims unsupported by the retrieved context.",
        ["Restore the grounding instruction and an explicit 'I don't know' fallback", "Alert when groundedness drops below 80%", "Run an evaluation set before any prompt change ships"],
        "Answers returned 200 OK — no error-based alert could catch this; it was found by a customer",
        "Need prompt changes to go through review and evaluation like code"),
    "prompt_injection": ("unsafe instructions delivered to end users", "ingestion and retrieval pipeline",
        "An imported community post containing hidden instructions was retrieved and the model followed it, telling users to email their API key to an external address. Groundedness checks passed because the answer was 'supported' by the poisoned source.",
        ["Remove the poisoned document and audit similar imported content", "Wrap retrieved text as data and instruct the model to ignore instructions inside it", "Scan content for injection patterns at ingest; block credential requests in outputs"],
        "Untrusted sources were ingested with the same trust as official docs",
        "Need a source allowlist and security review for new content connectors"),
    "empty_retrieval": ("no answers for any question", "index loading / ingestion",
        "Retrieval returned zero chunks for every query — the index was empty or failed to load after deployment.",
        ["Health-check index size at startup and fail the deploy on zero", "Alert on zero-result retrieval rate", "Verify ingestion status in the deploy checklist"],
        "The service looked healthy while the index was empty",
        "Need index validation as a deploy gate"),
    "truncated_output": ("answers cut off mid-sentence", "generation configuration",
        "max_tokens was set far below normal answer length, so responses stopped early with finish_reason='length' while still returning 200 OK.",
        ["Alert on finish_reason='length' rate", "Size max_tokens to the answer format; control length via the prompt", "Add config change review for generation parameters"],
        "Truncation never raised an error, so monitoring didn't see it",
        "Need generation parameters under change management"),
    "slow_latency": ("slow responses, SLA latency breach", "request queueing between retrieval and generation",
        "Requests waited several seconds before generation. Retrieval and generation timings were normal; the time was lost in queueing.",
        ["Break latency into retrieval / queue / generation stages on dashboards", "Alert on P95 latency, not the average", "Add capacity or limit concurrency; stream responses"],
        "Average latency looked acceptable while P95 breached the SLO",
        "Need stage-level latency as a tracked SLA metric"),
    "auth_error": ("complete service outage", "credentials / secrets management",
        "The LLM provider rejected the API key with HTTP 401 after it was rotated or revoked, and the new key never reached the production secret store.",
        ["Rotate the key and update the secret store", "Alert on any 401 immediately (never retry)", "Add key rotation to a runbook with a verification step"],
        "Retries hid the problem for minutes — 401s should page immediately",
        "Need a documented key rotation procedure with per-environment keys"),
    "model_deprecated": ("complete service outage", "model configuration",
        "Requests named a model version the provider had retired, returning HTTP 404 model_not_found.",
        ["Move the model name to config and switch to the supported replacement", "Track provider deprecation notices with owners and dates", "Run the eval set against the replacement model before switching"],
        "The deprecation notice was received months earlier but had no owner",
        "Need a model lifecycle review in every QBR / quarterly planning"),
}

# -- RCA Generator --
st.subheader("Generate RCA from Recent Incidents")

df = metrics_store.get_metrics()
# Errors plus silent failures (request succeeded while a failure mode was active)
failed = df[(~df["success"]) | (df["failure_mode"].fillna("") != "")] if not df.empty else df

if failed.empty:
    st.info("No failures recorded yet. Toggle a failure in Failure Lab, trigger it in Chat, then come back here to generate an RCA.")
else:
    # Group failures by mode
    failure_groups = failed.groupby("failure_mode").agg(
        count=("id", "count"),
        first_seen=("timestamp", "min"),
        last_seen=("timestamp", "max"),
        avg_latency=("total_ms", "mean"),
    ).reset_index()

    st.markdown("**Recent failure incidents:**")
    for _, row in failure_groups.iterrows():
        mode = row["failure_mode"] if row["failure_mode"] else "unknown"
        st.markdown(f"- **{mode}**: {row['count']} occurrence(s), first seen {row['first_seen']}")

    selected_mode = st.selectbox(
        "Generate RCA for",
        failure_groups["failure_mode"].tolist(),
    )

    if st.button("Generate RCA Document"):
        mode_data = failed[failed["failure_mode"] == selected_mode]
        incident_count = len(mode_data)
        first_seen = mode_data["timestamp"].min()
        last_seen = mode_data["timestamp"].max()
        avg_latency = int(mode_data["total_ms"].mean())
        total_requests = len(df)
        impact_pct = (incident_count / total_requests * 100) if total_requests > 0 else 0

        # Get failure mode details
        mode_keys = [k for k in failure_simulator.FAILURE_MODES if k in selected_mode]
        mode_info = failure_simulator.FAILURE_MODES.get(mode_keys[0] if mode_keys else "", {})
        root_cause = mode_info.get("cause", "Under investigation")
        fix = mode_info.get("fix", "See incident runbook")
        impact_txt, layer, technical, actions, improve, gap = RCA_DETAILS.get(
            mode_keys[0] if mode_keys else "",
            ("degraded service", "application layer", root_cause,
             [fix, "Add monitoring for this failure signal", "Add this scenario to the incident runbook"],
             "Detection relied on customer reports", "Need a runbook for this failure type"),
        )

        rca_doc = f"""# Root Cause Analysis (RCA)

## Incident Summary

| Field | Value |
|-------|-------|
| **Incident ID** | INC-{datetime.now().strftime('%Y%m%d')}-{selected_mode.upper().replace(', ', '-')[:20]} |
| **Date** | {datetime.now().strftime('%Y-%m-%d')} |
| **Severity** | {'P1 - Critical' if incident_count > 5 else 'P2 - High' if incident_count > 2 else 'P3 - Medium'} |
| **Status** | Resolved |
| **Author** | [Your Name], Technical Account Manager |
| **Reviewed By** | [Engineering Lead] |

## Timeline

| Time (UTC) | Event |
|-----------|-------|
| {first_seen} | First failure detected |
| {first_seen} | Automated alert triggered (Metrics Dashboard) |
| {first_seen} | Investigation started — checked Logs Viewer |
| {last_seen} | Root cause identified |
| {last_seen} | Fix applied |
| {last_seen} | Service restored, monitoring for recurrence |

## Impact

- **Duration**: {first_seen} to {last_seen}
- **Affected requests**: {incident_count} out of {total_requests} total ({impact_pct:.1f}%)
- **Average response time during incident**: {avg_latency}ms
- **Customer impact**: Users experienced {impact_txt}
- **SLA impact**: {'SLA breach — error budget consumed' if impact_pct > 1 else 'Within SLA — error budget partially consumed'}

## Root Cause

**Category**: {selected_mode}

**Description**: {root_cause}

**Technical details**:
The failure originated in the {layer}.
{technical}

## Resolution

{fix}

## Action Items

| # | Action | Owner | Priority | Due Date |
|---|--------|-------|----------|----------|
| 1 | {actions[0]} | Engineering | High | {(datetime.now()).strftime('%Y-%m-%d')} |
| 2 | {actions[1]} | Engineering | Medium | {(datetime.now()).strftime('%Y-%m-%d')} |
| 3 | {actions[2]} | TAM / Ops | Medium | {(datetime.now()).strftime('%Y-%m-%d')} |
| 4 | Update incident runbook with lessons learned | TAM | Low | {(datetime.now()).strftime('%Y-%m-%d')} |
| 5 | Schedule post-incident review with customer | TAM | High | {(datetime.now()).strftime('%Y-%m-%d')} |

## Lessons Learned

1. **What went well**: Incident was detected {'quickly via automated metrics' if incident_count <= 3 else 'through customer report'}. Investigation followed the incident runbook.
2. **What could improve**: {improve}
3. **Process gap**: {gap}

## Customer Communication

Post-incident summary was sent to affected customers. See Incident Runbook for the communication template used.

---
*Generated by Stratify Labs Incident Management System*
*Template version 1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*
"""

        st.markdown(rca_doc)

        # Download button
        st.download_button(
            label="Download RCA as Markdown",
            data=rca_doc,
            file_name=f"RCA_{selected_mode}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
        )

st.divider()

# -- Blank RCA Template --
st.subheader("Blank RCA Template")
st.markdown("Use this template to write your own RCA from scratch — practice for interviews.")

with st.expander("View Blank Template"):
    blank_template = """# Root Cause Analysis (RCA)

## Incident Summary

| Field | Value |
|-------|-------|
| **Incident ID** | INC-YYYY-MMDD-### |
| **Date** | YYYY-MM-DD |
| **Severity** | P1/P2/P3 |
| **Status** | Investigating / Resolved |
| **Author** | [Your Name] |

## Timeline

| Time (UTC) | Event |
|-----------|-------|
| HH:MM | First alert / customer report |
| HH:MM | Investigation started |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Service restored |
| HH:MM | Monitoring confirmed stable |

## Impact

- **Duration**: X hours Y minutes
- **Affected users/requests**: N
- **Customer impact**: [Describe what users experienced]
- **SLA impact**: [Within SLA / SLA breached by X%]
- **Revenue impact**: [If applicable]

## Root Cause

[Clear, non-blaming description of what went wrong and why]

## Resolution

[What was done to fix it]

## Action Items

| # | Action | Owner | Priority | Due Date |
|---|--------|-------|----------|----------|
| 1 | [Immediate fix] | | High | |
| 2 | [Preventive measure] | | Medium | |
| 3 | [Monitoring improvement] | | Medium | |

## Lessons Learned

1. **What went well**:
2. **What could improve**:
3. **Process gap**:

## Customer Communication

[Summary of what was communicated to customers and when]
"""
    st.code(blank_template, language="markdown")
    st.download_button(
        label="Download Blank Template",
        data=blank_template,
        file_name="RCA_template_blank.md",
        mime="text/markdown",
    )

st.divider()

# -- RCA Writing Guide --
st.subheader("How to Write a Good RCA")
st.markdown("""
**The 5 rules of effective RCAs:**

### 1. Be Blameless
Bad: *"The developer pushed broken code to production."*
Good: *"A configuration change was deployed without automated validation, allowing an out-of-range parameter."*

### 2. Focus on Systems, Not People
Ask "why did the system allow this?" not "who did this?" Every RCA action item should improve a system or process.

### 3. Be Specific with Timelines
Vague: *"The issue started in the afternoon."*
Specific: *"First error detected at 14:23 UTC. Alert fired at 14:25. Engineer engaged at 14:31."*

### 4. Action Items Must Be Actionable
Bad: *"Be more careful with deployments."*
Good: *"Add automated parameter validation that rejects temperature values > 1.0 before API call. Owner: Backend team. Due: 2026-02-28."*

### 5. Include the Customer Angle
TAMs own the customer relationship. Your RCA should always cover:
- What did the customer experience?
- When and how were they notified?
- What follow-up is planned?

---
""")
