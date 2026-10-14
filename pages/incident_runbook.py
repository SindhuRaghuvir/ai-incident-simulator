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
    "hallucination": {
        "title": "Hallucination — Confident, Fabricated Answers",
        "severity": "P1 - Critical",
        "symptoms": [
            "Customer reports: 'The bot told our user a refund policy we don't have'",
            "Answers contain specific numbers, prices, or dates that aren't in any doc",
            "No errors anywhere — every request returns 200 OK",
            "Groundedness score in Chat drops below 80%; Logs show WARN `eval` lines",
        ],
        "diagnostic_steps": [
            "1. Reproduce: ask the exact question from the ticket in **Chat** with the Hallucination check on",
            "2. Open **Hallucination analysis** under the answer — list every ⚠️ unsupported / ❌ contradicted claim",
            "3. In **Logs**, filter component `retrieval`: did the right source come back? Check the best distance",
            "4. Decide which half failed: right chunk missing → **retrieval problem**; right chunk present but answer wrong → **generation problem**",
            "5. In **Logs**, filter component `generation`: look for 'Non-default system prompt in use' and the temperature value",
            "6. Ask what changed: prompt edit, temperature change, docs deleted, re-index, model upgrade?",
            "7. Toggle the failure off and re-ask — confirm groundedness returns to 80%+",
        ],
        "root_causes": [
            "System prompt edited to 'always answer confidently' — removed the 'say you don't know' path",
            "Retrieval missed the chunk with the answer (deleted doc, bad chunking, low top-k)",
            "Temperature raised for 'more natural' answers",
            "Question is outside the knowledge base and nothing stops the model from answering anyway",
        ],
        "resolution": [
            "**Immediate**: Roll back the prompt / temperature change; enable strict grounding and the fallback message",
            "**Short-term**: Add the missing content, or raise the relevance threshold so weak matches trigger the fallback",
            "**Long-term**: Groundedness check on every answer with an alert below 80%; eval set run before any prompt or model change",
        ],
        "customer_comms": """
**Subject: Resolution — Incorrect Answers From Your Assistant**

Hi [Customer],

You were right: between [time] and [time], the assistant gave answers that weren't supported by your knowledge base, including [example claim].

**What happened:** A configuration change told the model to always give a specific answer, even when your documents didn't contain one. When the relevant article wasn't retrieved, it filled the gap with invented details.

**What we've done:**
- Rolled back the change and restored the "I don't have that information" fallback
- Re-ran the affected questions; every answer is now backed by your documents
- Turned on automatic groundedness checks that flag unsupported answers

**Recommended next steps:**
1. Review the [N] conversations from the affected window (list attached)
2. Correct anything sent to your customers using the accurate policy

I'm sorry for the confusion this caused your team. Happy to walk through the analysis on a call.

Best,
[Your Name]
""",
        "prevention": [
            "Groundedness score on every answer; alert when the daily average drops below 80%",
            "Treat prompt changes like code: review + eval set before release",
            "Keep the 'say you don't know' instruction and a fallback message in every prompt",
            "Track the 'I don't know' rate — a sudden drop can mean the model stopped admitting gaps",
        ],
    },
    "prompt_injection": {
        "title": "Prompt Injection via Poisoned Document",
        "severity": "P1 - Critical",
        "symptoms": [
            "Customer reports: 'The assistant told a user to email their API key somewhere'",
            "Answer contains instructions that appear in no official doc",
            "Groundedness looks fine — the claims ARE supported, by the poisoned source",
        ],
        "diagnostic_steps": [
            "1. In **Logs**, check the retrieval sources — look for an unexpected source (e.g. `community_forum_post.md`)",
            "2. Open that chunk: search for phrases like 'ignore previous instructions' or 'system note'",
            "3. Find how it got in: which connector, when, by whom",
            "4. Search the index for other content with the same pattern",
        ],
        "root_causes": [
            "Untrusted content (forum posts, synced tickets, scraped pages) ingested with no review",
            "Retrieved text placed in the prompt as if it were trusted instructions",
        ],
        "resolution": [
            "**Immediate**: Delete the poisoned document; warn affected users not to follow the instruction",
            "**Short-term**: Delimit retrieved text and instruct the model to ignore instructions inside it",
            "**Long-term**: Source allowlist, injection scanning at ingest, output filter for credential requests",
        ],
        "customer_comms": """
**Subject: Security Notice — Unsafe Instruction From Your Assistant**

Hi [Customer],

Between [time] and [time], your assistant showed some users an instruction to email their API key to an external address. This came from a malicious post imported into your knowledge base, not from Stratify Labs or your team.

**What we've done:** removed the post, blocked similar content, and added a filter that stops answers requesting credentials.

**Please:** ask any user who sent a key to rotate it immediately at Settings > API Keys. We can provide the list of affected conversations.

Best,
[Your Name]
""",
        "prevention": [
            "Allowlist trusted sources; review new connectors with security",
            "Scan content for injection patterns at ingest",
            "Block outputs that ask users for keys, passwords, or payment details",
        ],
    },
    "empty_retrieval": {
        "title": "Empty Retrieval — Index Empty or Not Loaded",
        "severity": "P2 - High",
        "symptoms": [
            "Every question returns 'I couldn't find any relevant information'",
            "Started right after a deploy or re-index",
            "Logs: WARN 'Retrieval returned 0 results'",
        ],
        "diagnostic_steps": [
            "1. Check the chunk count in the Chat caption — is it 0?",
            "2. In **Logs**, filter `retrieval` — are results 0 for every query, or only some?",
            "3. Check ingestion status and the index files after the last deploy",
            "4. Verify the collection name and any metadata filters",
        ],
        "root_causes": [
            "Index failed to load at startup", "Ingestion failed or was partial",
            "Wrong collection name or a filter that excludes everything",
        ],
        "resolution": [
            "**Immediate**: Reload / rebuild the index; roll back the deploy if needed",
            "**Long-term**: Fail the deploy when the index has 0 chunks; alert on zero-result rate",
        ],
        "customer_comms": """
**Subject: Resolved — Assistant Returning No Results**

Hi [Customer],

From [time] to [time], the assistant couldn't find content for any question because the search index didn't load after a deployment. No documents were lost. The index is restored and answers are back to normal. We've added a check that blocks deploys if the index is empty.

Best,
[Your Name]
""",
        "prevention": ["Index size check as a deploy gate", "Alert when zero-result rate > 5%"],
    },
    "truncated_output": {
        "title": "Truncated Answers (finish_reason = length)",
        "severity": "P3 - Medium",
        "symptoms": [
            "Answers stop mid-sentence", "Requests return 200 OK",
            "Logs: WARN 'Answer truncated (finish_reason=length …)'",
        ],
        "diagnostic_steps": [
            "1. In **Logs**, search `finish_reason` — how many answers were cut off?",
            "2. Check output tokens in **Metrics** — all capped at the same number?",
            "3. Check recent config changes to max_tokens",
        ],
        "root_causes": ["max_tokens lowered (often to cut cost)", "Answer format got longer (tables, steps) without raising the limit"],
        "resolution": [
            "**Immediate**: Restore max_tokens", "**Long-term**: Alert on finish_reason='length'; control length through the prompt",
        ],
        "customer_comms": """
**Subject: Resolved — Answers Cut Off Mid-Sentence**

Hi [Customer],

A configuration change limited answer length, so longer answers were cut off between [time] and [time]. We've restored the setting and added monitoring for truncated answers.

Best,
[Your Name]
""",
        "prevention": ["Alert on truncation rate", "Config review for generation parameters"],
    },
    "slow_latency": {
        "title": "Latency Spike — Slow but Successful",
        "severity": "P2 - High",
        "symptoms": [
            "Customer reports: 'Answers take 6+ seconds'", "No errors; success rate 100%",
            "SLA page: P95 latency breach", "Logs: WARN 'Slow response … waiting Xms'",
        ],
        "diagnostic_steps": [
            "1. **SLA** page — P95 vs. target; when did it start?",
            "2. **Logs** — compare retrieval, generation, and waiting time per request",
            "3. If retrieval and generation are normal, the time is queueing: check concurrency and capacity",
            "4. Check the provider status page for degraded performance",
        ],
        "root_causes": ["Concurrency limit reached — requests queue", "Cold index after idle period", "Provider degradation"],
        "resolution": [
            "**Immediate**: Add capacity / reduce concurrency; stream responses",
            "**Long-term**: Stage-level latency dashboards; alert on P95",
        ],
        "customer_comms": """
**Subject: Update — Slower Response Times**

Hi [Customer],

Between [time] and [time], answers took [X]s instead of the usual [Y]s. No requests failed. The delay came from requests queueing before processing. We've added capacity, and response times are back to normal. We now alert on 95th-percentile latency so we catch this before you do.

Best,
[Your Name]
""",
        "prevention": ["P95 alerting", "Capacity planning before customer launches"],
    },
    "auth_error": {
        "title": "Invalid API Key (HTTP 401)",
        "severity": "P1 - Critical",
        "symptoms": ["Every request fails with 401 invalid_api_key", "Started right after a key rotation or deploy"],
        "diagnostic_steps": [
            "1. **Logs** — confirm 401 on every request (not intermittent)",
            "2. Check the key prefix in use vs. the active key in the provider console",
            "3. Was the key auto-revoked (e.g. found in a public repo)? Check email",
            "4. Confirm the secret is set in this environment",
        ],
        "root_causes": ["Key rotated but secret not updated", "Key revoked after leak", "Wrong environment's key"],
        "resolution": [
            "**Immediate**: Issue a new key, update the secret store, redeploy",
            "**Long-term**: Page on any 401; never retry 401s; per-environment keys",
        ],
        "customer_comms": """
**Subject: Resolved — Service Outage (Authentication)**

Hi [Customer],

From [time] to [time], all requests failed because a rotated API credential wasn't updated in production. The credential is fixed and service is fully restored. No data was affected. We've added a verification step to our key rotation process.

Best,
[Your Name]
""",
        "prevention": ["Rotation runbook with a verify step", "Secret scanning in CI"],
    },
    "model_deprecated": {
        "title": "Model Deprecated (HTTP 404 model_not_found)",
        "severity": "P1 - Critical",
        "symptoms": ["Every request fails with 404 model_not_found", "Started on a specific date with no deploy"],
        "diagnostic_steps": [
            "1. **Logs** — read the model name in the error",
            "2. Check the provider's deprecation page for its retirement date",
            "3. Find where the model name is set (config vs. hard-coded)",
        ],
        "root_causes": ["Pinned model retired; deprecation notice had no owner"],
        "resolution": [
            "**Immediate**: Switch to the supported replacement model",
            "**Long-term**: Model name in config; track deprecations with owners; eval before switching",
        ],
        "customer_comms": """
**Subject: Resolved — Outage Due to Model Retirement**

Hi [Customer],

From [time] to [time], requests failed because the AI model we used was retired by its provider. We've moved to the supported replacement and verified answer quality against our test set. We're tightening how we track provider deprecations so this doesn't recur.

Best,
[Your Name]
""",
        "prevention": ["Deprecation calendar with owners", "Quarterly model lifecycle review"],
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
