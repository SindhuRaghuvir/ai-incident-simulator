import streamlit as st
from datetime import datetime

import metrics_store
import failure_simulator

st.title("RCA Templates")
st.caption("Root Cause Analysis documents — what TAMs write after every major incident. Practice generating them from real failure data.")

st.divider()

# -- RCA Generator --
st.subheader("Generate RCA from Recent Incidents")

df = metrics_store.get_metrics()
failed = df[~df["success"]] if not df.empty else df

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
- **Customer impact**: Users experienced {'complete service outage' if 'timeout' in selected_mode else 'degraded service quality' if 'bad_context' in selected_mode else 'intermittent request failures' if 'rate_limit' in selected_mode else 'inconsistent response quality'}
- **SLA impact**: {'SLA breach — error budget consumed' if impact_pct > 1 else 'Within SLA — error budget partially consumed'}

## Root Cause

**Category**: {selected_mode}

**Description**: {root_cause}

**Technical details**:
The failure originated in the {'API gateway layer' if 'rate_limit' in selected_mode else 'upstream LLM provider' if 'timeout' in selected_mode else 'retrieval/embedding pipeline' if 'bad_context' in selected_mode else 'configuration management layer'}.
{'Requests exceeded the configured rate limit threshold, causing the API to return HTTP 429 responses.' if 'rate_limit' in selected_mode else 'The upstream LLM service experienced degraded performance, causing requests to exceed the configured timeout threshold.' if 'timeout' in selected_mode else 'The retrieval pipeline returned low-relevance results due to stale embeddings or corrupted query processing, causing the LLM to generate answers from irrelevant context.' if 'bad_context' in selected_mode else 'The temperature parameter was set outside the validated range, causing non-deterministic and incoherent LLM outputs.'}

## Resolution

{fix}

## Action Items

| # | Action | Owner | Priority | Due Date |
|---|--------|-------|----------|----------|
| 1 | {'Implement exponential backoff with jitter' if 'rate_limit' in selected_mode else 'Add circuit breaker pattern' if 'timeout' in selected_mode else 'Set up automated re-indexing pipeline' if 'bad_context' in selected_mode else 'Add server-side parameter validation'} | Engineering | High | {(datetime.now()).strftime('%Y-%m-%d')} |
| 2 | {'Add request queuing to smooth traffic spikes' if 'rate_limit' in selected_mode else 'Configure fallback responses for degraded mode' if 'timeout' in selected_mode else 'Add relevance threshold monitoring' if 'bad_context' in selected_mode else 'Lock production config behind change management'} | Engineering | Medium | {(datetime.now()).strftime('%Y-%m-%d')} |
| 3 | {'Set up usage alerts at 75% and 90% of rate limits' if 'rate_limit' in selected_mode else 'Add health check monitoring with PagerDuty' if 'timeout' in selected_mode else 'Create golden test set for retrieval quality' if 'bad_context' in selected_mode else 'Set up config change alerts'} | TAM / Ops | Medium | {(datetime.now()).strftime('%Y-%m-%d')} |
| 4 | Update incident runbook with lessons learned | TAM | Low | {(datetime.now()).strftime('%Y-%m-%d')} |
| 5 | Schedule post-incident review with customer | TAM | High | {(datetime.now()).strftime('%Y-%m-%d')} |

## Lessons Learned

1. **What went well**: Incident was detected {'quickly via automated metrics' if incident_count <= 3 else 'through customer report'}. Investigation followed the incident runbook.
2. **What could improve**: {'Detection was reactive — need proactive alerting before limits are hit' if 'rate_limit' in selected_mode else 'No fallback mechanism — service was fully unavailable during the outage' if 'timeout' in selected_mode else 'No automated quality monitoring — degradation was noticed by users, not by our systems' if 'bad_context' in selected_mode else 'Configuration changes were not validated — need automated guardrails'}
3. **Process gap**: {'Need a capacity planning review as part of customer onboarding' if 'rate_limit' in selected_mode else 'Need a documented degraded-mode playbook' if 'timeout' in selected_mode else 'Need retrieval quality as a tracked SLA metric' if 'bad_context' in selected_mode else 'Need config change review process for production'}

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

**In interviews, you might hear:**

> *"Tell me about a time you conducted a root cause analysis."*

Use the structure above. Even if your example is from a different domain, the framework is the same: timeline → impact → root cause → action items → lessons learned.
""")
