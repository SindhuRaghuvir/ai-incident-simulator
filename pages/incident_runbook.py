import streamlit as st

import metrics_store
import failure_simulator

st.title("Incident Runbook")
st.caption("Step-by-step guides for diagnosing and resolving AI system incidents — the same process used by TAMs and support engineers on-call.")

st.divider()

# -- Runbook definitions --

RUNBOOKS = {
    "rate_limit": {
        "title": "Rate Limit Exceeded (HTTP 429)",
        "severity": "P2 - High",
        "symptoms": [
            "Customer reports: 'API calls are failing intermittently'",
            "Error message contains 'Rate limit reached' or HTTP 429",
            "Failures spike during peak hours, work fine at low traffic",
        ],
        "diagnostic_steps": [
            "1. Check the **Metrics Dashboard** — look for a spike in failed requests",
            "2. Check error messages — look for `rate_limit_exceeded` in the logs",
            "3. Confirm the customer's current plan and rate limits (see Billing & Plans docs)",
            "4. Check if the customer recently increased traffic or deployed a new integration",
            "5. Look at request timestamps — are failures clustered or spread out?",
        ],
        "root_causes": [
            "Customer exceeded their plan's requests-per-minute (RPM) limit",
            "A new feature or bot is making rapid-fire API calls without backoff",
            "Multiple services sharing the same API key, combined usage exceeds limits",
            "Batch processing job running during peak hours instead of off-peak",
        ],
        "resolution": [
            "**Immediate**: Identify the source of excess requests and throttle it",
            "**Short-term**: Implement exponential backoff with jitter in client code",
            "**Long-term**: Add request queuing, upgrade plan if usage is legitimate, separate API keys per service",
        ],
        "customer_comms": """
**Subject: Resolution — API Rate Limit Errors**

Hi [Customer],

We've identified the cause of the intermittent API failures you reported. Your application was exceeding the rate limit of [X] requests/minute on your current [Plan] plan.

**What happened:** Between [time] and [time], your integration sent [N] requests/minute, exceeding the [limit] RPM limit. The API correctly returned HTTP 429 responses for excess requests.

**What we've done:**
- Identified the specific integration causing the spike
- Confirmed no data was lost — requests can be safely retried

**Recommended next steps:**
1. Implement exponential backoff in your API client (see our SDK docs)
2. Consider upgrading to [Higher Plan] for [higher limit] RPM
3. Stagger batch operations to avoid bursts

Let me know if you'd like help implementing any of these changes.

Best,
[Your Name]
""",
        "prevention": [
            "Set up usage alerts at 50%, 75%, 90% of rate limits",
            "Implement client-side rate limiting before hitting the API",
            "Use separate API keys per service to isolate usage",
            "Schedule batch jobs during off-peak hours",
        ],
    },
    "timeout": {
        "title": "Request Timeout / Service Unavailable (HTTP 503)",
        "severity": "P1 - Critical",
        "symptoms": [
            "Customer reports: 'The system is completely down' or 'Requests hang forever'",
            "HTTP 503 or timeout errors in logs",
            "Latency spikes to 30s+ before failing",
            "Affects all users, not just one customer",
        ],
        "diagnostic_steps": [
            "1. Check **status page** — is this a known outage with the LLM provider?",
            "2. Check the **Metrics Dashboard** — when did latency start spiking?",
            "3. Test with a simple query — is it all requests or only complex ones?",
            "4. Check upstream dependencies — is the vector database (ChromaDB) responsive?",
            "5. Check network — any DNS issues, firewall changes, or certificate expirations?",
            "6. Check resource usage — CPU, memory, disk on the application server",
        ],
        "root_causes": [
            "LLM provider (OpenAI) experiencing an outage or degraded performance",
            "Network issue between your infrastructure and the API endpoint",
            "Application server overloaded — too many concurrent requests",
            "Very large prompts causing slow processing (context window near limit)",
            "Database connection pool exhausted",
        ],
        "resolution": [
            "**Immediate**: Activate circuit breaker — stop sending requests to the failing service",
            "**Immediate**: Serve fallback responses: 'Our AI assistant is temporarily unavailable. Here are links to our documentation that may help.'",
            "**Short-term**: Implement request timeouts (30s max) so users aren't left hanging",
            "**Long-term**: Add health checks, auto-scaling, and a secondary LLM provider as failover",
        ],
        "customer_comms": """
**Subject: Incident Update — Service Degradation**

Hi [Customer],

We're aware of the service disruption affecting the Knowledge Assistant starting at [time].

**Current status:** Our AI processing service is experiencing elevated latency due to [upstream provider issues / infrastructure issue]. Our team is actively working on resolution.

**Impact:** Search queries may time out or return errors. Your data is safe — this is a processing issue, not a data issue.

**What we're doing:**
- Engaged with [provider] support for status updates
- Activated fallback responses to provide basic assistance
- Monitoring for recovery

**ETA:** We expect resolution within [X hours]. We'll update you every 30 minutes.

We apologize for the disruption.

Best,
[Your Name]
""",
        "prevention": [
            "Implement circuit breaker pattern with automatic fallback",
            "Set up uptime monitoring with PagerDuty/OpsGenie alerts",
            "Have a secondary LLM provider configured for failover",
            "Load test to know your system's breaking point",
        ],
    },
    "bad_context": {
        "title": "Retrieval Quality Degradation (Wrong Answers)",
        "severity": "P2 - High",
        "symptoms": [
            "Customer reports: 'The assistant is giving wrong or irrelevant answers'",
            "Answers don't match the source documents",
            "Confidence scores / relevance distances are unusually high (bad)",
            "Worked fine before but quality has degraded over time",
        ],
        "diagnostic_steps": [
            "1. Reproduce the issue — ask the same question and check retrieved chunks",
            "2. Expand **Sources & Metrics** in the Chat tab — are the right docs being retrieved?",
            "3. Check the **distance scores** — values above 1.5 indicate poor matches",
            "4. Verify the knowledge base — was it recently updated? Were docs deleted?",
            "5. Test with a known question that should match a specific doc",
            "6. Check if embeddings were regenerated recently (model change or re-indexing)",
        ],
        "root_causes": [
            "Knowledge base documents are outdated or were accidentally deleted",
            "Embeddings are stale — docs were updated but not re-indexed",
            "Poor chunking — relevant info is split across chunks and neither chunk has enough context",
            "Embedding model was changed or updated, old embeddings are incompatible",
            "Query is ambiguous and matches multiple topics poorly",
        ],
        "resolution": [
            "**Immediate**: Verify knowledge base contents — are all expected docs present?",
            "**Short-term**: Re-index the knowledge base to regenerate fresh embeddings",
            "**Short-term**: Add a relevance threshold — if distance > 1.5, say 'I don't have enough information' instead of giving a bad answer",
            "**Long-term**: Set up automated re-indexing on a schedule, monitor retrieval quality metrics",
        ],
        "customer_comms": """
**Subject: Resolution — Knowledge Search Accuracy Issue**

Hi [Customer],

Thank you for flagging the accuracy issues with search results. We've investigated and identified the cause.

**What happened:** [Recent knowledge base updates were not reflected in the search index / Chunking configuration caused relevant information to be split across segments, reducing match quality].

**What we've done:**
- Re-indexed the full knowledge base with updated embeddings
- Verified search accuracy across [N] test queries
- Added relevance thresholds to prevent low-confidence answers from being shown

**Result:** Search accuracy has been restored. Please test with the queries that were previously returning incorrect results.

Let us know if you notice any further issues.

Best,
[Your Name]
""",
        "prevention": [
            "Schedule automatic re-indexing after any knowledge base update",
            "Monitor average retrieval distance scores — alert if they drift upward",
            "Test retrieval quality with a golden set of question-answer pairs",
            "Use overlapping chunks so context isn't lost at boundaries",
        ],
    },
    "high_temperature": {
        "title": "Incoherent or Unpredictable LLM Output",
        "severity": "P3 - Medium",
        "symptoms": [
            "Customer reports: 'The assistant is giving random or nonsensical answers'",
            "Output tone and quality varies wildly between requests",
            "Answers are creative but factually wrong",
            "Same question gives very different answers each time",
        ],
        "diagnostic_steps": [
            "1. Check the **temperature setting** — is it higher than expected?",
            "2. Look at recent config changes — did anyone modify API parameters?",
            "3. Check if the parameter is being set by user input without validation",
            "4. Compare outputs at temperature 0.3 vs the current setting",
            "5. Check if other parameters (top_p, frequency_penalty) were also changed",
        ],
        "root_causes": [
            "Temperature accidentally set too high (>1.0) in configuration",
            "User-facing controls allow unrestricted parameter values",
            "Config file was modified without review (no config validation)",
            "A/B test or experiment left a non-default setting active",
        ],
        "resolution": [
            "**Immediate**: Reset temperature to the default (0.3 for factual Q&A)",
            "**Short-term**: Add server-side validation — clamp temperature between 0.0 and 1.0",
            "**Long-term**: Lock production parameters behind config management with change tracking",
        ],
        "customer_comms": """
**Subject: Resolution — Inconsistent Assistant Responses**

Hi [Customer],

We've resolved the issue causing inconsistent responses from the Knowledge Assistant.

**What happened:** A configuration parameter controlling response variability was set outside the normal range, causing the assistant to generate less predictable outputs.

**What we've done:**
- Restored the parameter to its validated default
- Added guardrails to prevent out-of-range configurations
- Verified response consistency across test queries

The assistant should now provide consistent, accurate responses. Please let us know if you see any further issues.

Best,
[Your Name]
""",
        "prevention": [
            "Validate all API parameters server-side before sending to the LLM",
            "Use infrastructure-as-code for config management with PR reviews",
            "Set up alerts for config changes in production",
            "Restrict who can modify production parameters (RBAC)",
        ],
    },
}

# -- Render runbooks --

# Check for recent incidents from metrics
df = metrics_store.get_metrics()
recent_failures = []
if not df.empty:
    failed = df[~df["success"]]
    if not failed.empty:
        recent_failures = failed["failure_mode"].unique().tolist()

if recent_failures:
    st.warning(f"Recent incidents detected: **{', '.join(recent_failures)}**. Relevant runbooks are highlighted below.")

for key, runbook in RUNBOOKS.items():
    # Highlight if this failure was recently triggered
    is_recent = any(key in f for f in recent_failures)
    header_prefix = "🔴 " if is_recent else ""

    with st.expander(f"{header_prefix}{runbook['title']} — {runbook['severity']}", expanded=is_recent):

        # Symptoms
        st.markdown("### What the Customer Reports")
        for symptom in runbook["symptoms"]:
            st.markdown(f"- {symptom}")

        st.markdown("---")

        # Diagnostic steps
        st.markdown("### Diagnostic Steps")
        for step in runbook["diagnostic_steps"]:
            st.markdown(step)

        st.markdown("---")

        # Root causes
        st.markdown("### Possible Root Causes")
        for cause in runbook["root_causes"]:
            st.markdown(f"- {cause}")

        st.markdown("---")

        # Resolution
        st.markdown("### Resolution")
        for step in runbook["resolution"]:
            st.markdown(f"- {step}")

        st.markdown("---")

        # Customer communication
        st.markdown("### Customer Communication Template")
        st.code(runbook["customer_comms"].strip(), language=None)

        st.markdown("---")

        # Prevention
        st.markdown("### Prevention (Stop It From Happening Again)")
        for item in runbook["prevention"]:
            st.markdown(f"- {item}")

st.divider()

# -- Common scenarios section --
st.subheader("Common TAM Scenario Questions")
st.markdown("""
**Other scenarios:**

1. **"A customer reports their AI assistant is returning wrong answers. Walk me through how you'd handle this."**
   → Use the *Retrieval Quality Degradation* runbook above.

2. **"Our API is returning 429 errors during peak hours. What do you tell the customer?"**
   → Use the *Rate Limit* runbook. Show empathy first, then explain the cause, then offer solutions.

3. **"How would you handle a situation where the service is completely down?"**
   → Use the *Timeout / 503* runbook. Emphasize: communicate early, communicate often, provide fallback.

4. **"A customer says the assistant's answers used to be good but now they're bad. What changed?"**
   → Use the *Retrieval Quality* runbook. Think: what changed? New docs? Re-indexing? Embedding model update?

**The TAM formula for any incident:**
1. **Acknowledge** — "I understand this is impacting your workflow"
2. **Investigate** — Walk through diagnostic steps out loud
3. **Communicate** — Set expectations on timeline
4. **Resolve** — Fix it
5. **Prevent** — Make sure it doesn't happen again (RCA + action items)
""")
