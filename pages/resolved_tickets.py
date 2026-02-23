import streamlit as st
import metrics_store
import failure_simulator

# -- Shared persona map --

TICKET_PERSONAS = {
    "rate_limit": {
        "customer": "Sarah Chen, Engineering Lead at Finova",
        "priority": "P2 - High",
        "subject": "API calls failing intermittently — 429 errors",
    },
    "timeout": {
        "customer": "Alex Kim, DevOps Engineer at RetailStack",
        "priority": "P1 - Critical",
        "subject": "Knowledge search completely unresponsive",
    },
    "bad_context": {
        "customer": "Priya Sharma, Product Manager at EduTech",
        "priority": "P2 - High",
        "subject": "Search quality degraded after knowledge base update",
    },
    "high_temperature": {
        "customer": "Dana Foster, QA Lead at LegalAI",
        "priority": "P3 - Medium",
        "subject": "Inconsistent responses for the same question",
    },
    "context_window": {
        "customer": "Raj Patel, Lead Engineer at DocuFlow",
        "priority": "P2 - High",
        "subject": "Assistant crashing on large document uploads",
    },
}

PRIORITY_COLOR = {
    "P1 - Critical": "🔴",
    "P2 - High": "🟠",
    "P3 - Medium": "🟡",
}

# -- Hardcoded investigation reports --

INVESTIGATIONS = {
    "context_window": {
        "resolved_by": "Support Engineering",
        "resolved_at": "2026-02-23 21:30 UTC",
        "timeline": """
| Timestamp (UTC) | Query | Result | Latency |
|---|---|---|---|
| 2026-02-23 20:58:24 | "Summarize our entire compliance policy library" | ❌ 400 | 120ms |

**Key observations:**
- Single event, but the query tells the whole story — "entire compliance policy library" means the user asked for everything at once.
- `top_k = 10` — the system retrieved **10 chunks** of context before calling the model. For large policy documents, 10 chunks can easily be thousands of tokens each.
- Failed in 120ms — rejected immediately before any generation started. The model never read a single word.
- The error message is precise: **132,456 tokens sent, 128,000 allowed.** They are 4,456 tokens over — about 3,300 words too many.
""",
        "error_summary": """
```
HTTP 400 — invalid_request_error
code: context_length_exceeded

"This model's maximum context length is 128000 tokens.
 Your request has 132,456 tokens."
```

**What this means:** Unlike a 429 (rate limit), this is not a quota issue. It's a hard structural error — the request itself is too large to process. No amount of retrying will fix it. The request needs to be smaller.

**128,000 tokens** is gpt-4o-mini's context window — the model's working memory. Everything it needs to read (system prompt, retrieved chunks, user question) must fit inside that window at once. DocuFlow sent 132,456 — 3.5% over the limit. A targeted fix is enough; no full architecture change needed.
""",
        "root_cause": """
One setting caused this: **`top_k = 10`**

1. User asks: *"Summarize our entire compliance policy library"* — a broad, document-heavy query.
2. The retrieval system fetches the top 10 most relevant chunks (`top_k = 10`).
3. Compliance documents are dense — each chunk is likely 500–1,000 tokens. 10 chunks = up to 10,000 tokens of context before the prompt is even added.
4. All of it gets packaged into one API call — totalling 132,456 tokens.
5. The API refuses. Request fails.

Most RAG applications use `top_k = 3` to `top_k = 5`. DocuFlow set it to 10 — probably assuming more context means better answers. That's true up to the context limit. Beyond it, the entire request fails. There was also no token counting before the API call — nothing to catch the overflow before it was sent.
""",
        "resolution": """
1. **Reduce top_k to 3 (immediate fix)** — drops retrieved context from ~10,000 tokens to ~3,000, well within limits. For most queries, the top 3 chunks are the most relevant anyway.

2. **Add token counting before API calls** — use `tiktoken` to count tokens before sending. If over a safe threshold (e.g. 100k tokens), trim context or return a user-friendly message instead of crashing.

3. **Re-chunk large documents** — re-index with a smaller chunk size (300–400 tokens vs 800–1,000). Smaller chunks give more precision at any top_k setting.

4. **Catch the error gracefully** — when `context_length_exceeded` is returned, surface a helpful message: *"This document is too large to summarize in one pass. Try asking about a specific section."*
""",
        "customer_response": """Hi Raj,

I've identified the cause. Your assistant is retrieving 10 context chunks per query (top_k = 10), and for large compliance documents, that pushes the total request over gpt-4o-mini's 128k token limit by about 4,500 tokens.

Immediate fix: reduce top_k to 3 in your configuration — this alone should stop the crashes. Longer term, I'd recommend adding token counting before each API call so the system catches overflow before it errors.

Happy to walk you through both changes if helpful.

— Support Engineering""",
    },
    "timeout": {
        "resolved_by": "Support Engineering",
        "resolved_at": "2026-02-16 20:15 UTC",
        "timeline": """
| Timestamp (UTC) | Query | Result | Latency |
|---|---|---|---|
| 2026-02-16 19:42:35 | "hello" | ❌ 503 | 3,109ms |

**Key observations:**
- Single event. The query was trivial — "hello" — which rules out prompt complexity as a cause.
- `total_ms = 3,109ms` — the request hung for over 3 seconds before failing. This is a server-side delay, not an instant rejection. Something was slow upstream.
- `input_tokens = 0` — no tokens were ever counted, confirming the request never reached the model. It timed out at the network or API layer.
- `top_k = 3`, `temperature = 0.3` — both normal. Configuration was not the cause.
- Alex reported 45 minutes of unresponsiveness starting 2:15 PM EST. The log event aligns with that window.
""",
        "error_summary": """
```
HTTP 503 — server_error
code: service_unavailable

"Service temporarily unavailable (simulated timeout)"
```

**What this means:** A 503 means the server received the request but couldn't handle it — either because it was overloaded, a downstream dependency failed, or the service was temporarily degraded. Unlike a 400 (bad request) or 429 (rate limit), this is entirely on the infrastructure side. The client did nothing wrong.

**3,109ms to fail** — the client waited 3+ seconds before getting a response. For a search feature, this reads as a complete hang to the end user. Alex's team has a 99.9% uptime SLA — 45 minutes of downtime is significant budget burn (~31% of monthly error budget consumed in a single incident).
""",
        "root_cause": """
The 503 points to a **transient API-side outage or severe degradation** on OpenAI's infrastructure during this window.

What likely happened:
- OpenAI's API servers were overloaded or a backend service (routing, inference cluster) experienced a partial failure.
- Requests queued, then timed out server-side before a response could be generated.
- The client had no circuit breaker — it kept waiting the full timeout duration (3s+) on every request rather than failing fast and switching to a fallback.

**Why a simple "hello" query was affected:** Timeouts during infrastructure incidents are not query-dependent. Even the lightest request gets stuck in the same queue. This confirms it was not a code or configuration issue on RetailStack's side.

**What made it worse:** No fallback response and no circuit breaker. Every user who searched during the 45-minute window got a hang or an error, rather than a graceful degraded experience.
""",
        "resolution": """
1. **Check the status page first** — status.openai.com. For any timeout incident, this is step one. If there's a known outage, the response to the customer changes entirely: acknowledge the platform issue, share the status link, and commit to updates.

2. **Implement a circuit breaker** — after 2–3 consecutive timeouts, stop sending requests to the API for a cooldown period (e.g. 30 seconds). Return a cached or static fallback response instead. Users get a degraded but functional experience rather than a hang.

3. **Set explicit client-side timeouts** — don't let requests hang indefinitely. A 10-second timeout with a friendly error is better than a 45-second hang. Fail fast.

4. **Commit to SLA communication** — during an outage, proactively update the customer every 30 minutes. Don't wait for them to follow up. After resolution, send a post-incident summary with timeline and steps taken.

5. **Review SLA credit entitlement** — 45 minutes of downtime on a 99.9% uptime SLA likely triggers a credit. Proactively acknowledge this rather than waiting for the customer to claim it.
""",
        "customer_response": """Hi Alex,

I can confirm this was caused by a period of API-side degradation during that window — your infrastructure was healthy. The 503 errors indicate the upstream service was temporarily unable to handle requests.

The incident lasted approximately 45 minutes. Given your 99.9% SLA, I'm initiating a review for a service credit for the affected period — you don't need to file a separate claim.

Going forward, I'd recommend implementing a circuit breaker on your client so that during future degradation events, your app returns a graceful fallback rather than hanging. I can share a reference implementation.

A post-incident report will follow within 24 hours.

— Support Engineering""",
    },
    "rate_limit": {
        "resolved_by": "Support Engineering",
        "resolved_at": "2026-02-23 21:15 UTC",
        "timeline": """
| Timestamp (UTC) | Query | Result | Latency |
|---|---|---|---|
| 2026-02-16 19:40:01 | "How do I reset my API key?" | ❌ 429 | 117ms |
| 2026-02-23 19:57:34 | "h" | ❌ 429 | 113ms |
| 2026-02-23 19:57:34 | "h'h" | ❌ 429 | 86ms |
| 2026-02-23 19:57:35 | "h" | ❌ 429 | 84ms |
| 2026-02-23 20:58:24 | "What is our refund policy?" | ❌ 429 | 80ms |

**Key observations:**
- First incident was isolated — Feb 16, single failure on a well-formed query.
- Second cluster — three failures fired within **1.4 seconds** on Feb 23. The malformed queries (`"h"`, `"h'h"`) indicate keystrokes being sent directly to the API without debouncing.
- Final event — an hour later, a normal query also failed. Quota had not recovered.
- **Total: 5 failures, 0 successful generations.** Every request was rejected before reaching the model.
""",
        "error_summary": """
```
HTTP 429 — Rate limit reached for gpt-4o-mini. Limit: 3 RPM.
Please try again in 20s.
```

**What this means:** The API is not broken — it's saying "too many requests, slow down." The account allows only **3 calls per minute**. Once that's hit, every request after it is rejected instantly — before the model even sees the question. Failures at 80–117ms confirm this: the server didn't attempt to answer, the rate limiter blocked it upstream.
""",
        "root_cause": """
Three things went wrong at the same time:

- **Rate limit tier is too low.** 3 RPM is a free/starter cap. A production feature with multiple users will exceed it the moment two people search at the same time.
- **No retry logic.** When the first 429 hit, the app kept firing more requests instead of waiting. A proper client would have read the `retry-after: 20s` header, paused, and retried — quietly, without the user noticing.
- **Keystrokes sent as API calls.** Queries like `"h"` are partial inputs, not real questions. The app was calling the API on every keystroke instead of waiting for the user to finish typing — burning through quota instantly.
""",
        "resolution": """
1. **Upgrade the plan** — move off the 3 RPM limit. For production, the minimum is Tier 2 (5,000 RPM). This is the only fix for the root cause.

2. **Add retry logic** — when a 429 hits, wait before retrying. Simple rule: wait 20 seconds on first failure, double it each time, max 3 retries. Then surface a friendly error to the user if still failing.

3. **Debounce user input** — wait until the user stops typing for 500ms before calling the API. Standard practice for any search-as-you-type feature. Would have prevented 3 of the 5 failures in this log.
""",
        "customer_response": """Hi Sarah,

I've reviewed the logs and found the cause. Your integration is hitting a **3 RPM rate limit** on `gpt-4o-mini` — a plan-level cap that production traffic will regularly exceed.

Two immediate steps:
1. I'm initiating a rate limit increase on your account — you should see it within 24 hours.
2. In the meantime, please add exponential backoff to your API client so 429s are retried gracefully rather than surfaced as errors to users. I'll send a code snippet separately.

Let me know if you'd like to jump on a call.

— Support Engineering""",
    }
}

# -- Session state init --

if "ticket_statuses" not in st.session_state:
    st.session_state.ticket_statuses = {}

# Pre-seed investigated tickets as Resolved so they appear on first load
for _mode in ["rate_limit", "context_window", "timeout"]:
    if _mode not in st.session_state.ticket_statuses:
        st.session_state.ticket_statuses[_mode] = "Resolved"

# -- Get resolved tickets --

resolved_modes = [
    mode for mode, status in st.session_state.ticket_statuses.items()
    if status == "Resolved" and mode in TICKET_PERSONAS
]

# -- Page layout --

st.title("Resolved Tickets")
st.caption("Closed tickets with full investigation history. Use these as a reference for recurring issues.")

st.divider()

if not resolved_modes:
    st.info("No resolved tickets yet. Investigate and close a ticket in **Ticket Queue** to see it here.")
    st.stop()

# -- Two-column layout: ticket list on left, detail on right --

col_list, col_detail = st.columns([1, 3])

with col_list:
    st.markdown("**Closed Tickets**")
    st.markdown("---")

    if "selected_resolved" not in st.session_state:
        st.session_state.selected_resolved = resolved_modes[0]

    for mode in resolved_modes:
        persona = TICKET_PERSONAS[mode]
        icon = PRIORITY_COLOR.get(persona["priority"], "⚪")
        is_selected = st.session_state.selected_resolved == mode
        label = f"{'→ ' if is_selected else ''}{icon} {persona['subject']}"
        if st.button(label, key=f"resolved_select_{mode}", use_container_width=True):
            st.session_state.selected_resolved = mode
            st.rerun()

with col_detail:
    mode = st.session_state.selected_resolved
    persona = TICKET_PERSONAS[mode]
    failure_info = failure_simulator.FAILURE_MODES.get(mode, {})
    investigation = INVESTIGATIONS.get(mode)

    # -- Ticket header --
    icon = PRIORITY_COLOR.get(persona["priority"], "⚪")
    st.subheader(f"{icon} {persona['subject']}")

    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.markdown(f"**Customer**  \n{persona['customer']}")
    with meta_col2:
        st.markdown(f"**Priority**  \n{persona['priority']}")
    with meta_col3:
        if investigation:
            st.markdown(f"**Resolved**  \n{investigation['resolved_at']}")
        st.markdown("**Status**  \n✅ Resolved")

    st.divider()

    if investigation:

        # -- Timeline --
        with st.expander("1. Timeline of Events", expanded=True):
            st.markdown(investigation["timeline"])

        # -- Error messages --
        with st.expander("2. Error Messages and What They Mean", expanded=True):
            st.markdown(investigation["error_summary"])

        # -- Root cause --
        with st.expander("3. Why It Happened", expanded=True):
            st.markdown(investigation["root_cause"])

        # -- Resolution --
        with st.expander("4. How to Avoid It in the Future", expanded=True):
            st.markdown(investigation["resolution"])

        # -- Customer response --
        with st.expander("5. Response Sent to Customer", expanded=False):
            st.code(investigation["customer_response"], language=None)

        st.divider()

        # -- Related logs from metrics --
        df = metrics_store.get_metrics()
        if not df.empty:
            mode_logs = df[(~df["success"]) & (df["failure_mode"] == mode)].sort_values("timestamp", ascending=False)
            if not mode_logs.empty:
                st.subheader("Log Entries at Time of Incident")
                st.dataframe(
                    mode_logs.head(5)[["timestamp", "query", "error_message", "total_ms"]],
                    use_container_width=True,
                    hide_index=True,
                )

    else:
        # Generic view for resolved tickets without a written investigation
        st.info("No detailed investigation report for this ticket.")
        st.markdown(f"**Failure type:** {failure_info.get('label', mode)}")
        st.markdown(f"**Description:** {failure_info.get('description', '—')}")
        st.markdown(f"**Root cause:** {failure_info.get('cause', '—')}")
        st.markdown(f"**Fix applied:** {failure_info.get('fix', '—')}")

        df = metrics_store.get_metrics()
        if not df.empty:
            mode_logs = df[(~df["success"]) & (df["failure_mode"] == mode)].sort_values("timestamp", ascending=False)
            if not mode_logs.empty:
                st.subheader("Log Entries at Time of Incident")
                st.dataframe(
                    mode_logs.head(5)[["timestamp", "query", "error_message", "total_ms"]],
                    use_container_width=True,
                    hide_index=True,
                )
