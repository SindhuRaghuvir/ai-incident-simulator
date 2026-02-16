import streamlit as st

import logger

st.title("Logs Viewer")
st.caption("Structured log stream — trace requests from query to response, investigate failures like you would in Datadog or Splunk.")

# -- Controls --
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    level_filter = st.multiselect(
        "Log Level",
        ["INFO", "WARN", "ERROR"],
        default=["INFO", "WARN", "ERROR"],
    )

with col2:
    component_filter = st.multiselect(
        "Component",
        ["chat", "retrieval", "generation", "failure_sim", "ingest"],
        default=["chat", "retrieval", "generation", "failure_sim", "ingest"],
    )

with col3:
    search_term = st.text_input("Search logs", placeholder="e.g. rate_limit, timeout...")

with col4:
    max_logs = st.selectbox("Show last", [50, 100, 200, 500], index=1)

if st.button("Clear All Logs"):
    logger.clear_logs()
    st.success("Logs cleared.")
    st.rerun()

st.divider()

# -- Fetch and filter logs --
df = logger.get_logs(limit=max_logs)

if df.empty:
    st.info("No logs yet. Ask questions in the Chat tab to generate log entries.")
    st.stop()

# Apply filters
if level_filter:
    df = df[df["level"].isin(level_filter)]

if component_filter:
    df = df[df["component"].isin(component_filter)]

if search_term:
    df = df[df["message"].str.contains(search_term, case=False, na=False)]

if df.empty:
    st.warning("No logs match your filters.")
    st.stop()

# -- Stats --
total = len(df)
errors = len(df[df["level"] == "ERROR"])
warnings = len(df[df["level"] == "WARN"])

cols = st.columns(3)
cols[0].metric("Visible Entries", total)
cols[1].metric("Errors", errors)
cols[2].metric("Warnings", warnings)

st.divider()

# -- Render log stream --
LEVEL_COLORS = {
    "INFO": "#2ecc71",
    "WARN": "#f39c12",
    "ERROR": "#e74c3c",
}

# Group by request_id for visual separation
prev_request_id = None

for _, row in df.iterrows():
    level = row["level"]
    color = LEVEL_COLORS.get(level, "#95a5a6")
    timestamp = row["timestamp"]
    component = row["component"]
    message = row["message"]
    request_id = row["request_id"]

    # Add separator between different requests
    if request_id and prev_request_id and request_id != prev_request_id:
        st.markdown("---")
    prev_request_id = request_id

    # Format: timestamp [LEVEL] [component] message
    req_tag = f"`{request_id}`" if request_id else ""
    comp_tag = f"**[{component}]**" if component else ""

    st.markdown(
        f"`{timestamp}` :{color}[**[{level}]**] {comp_tag} {message} {req_tag}",
        unsafe_allow_html=False,
    )

st.divider()

# -- Investigation guide --
st.subheader("How to Investigate")
st.markdown("""
**Tracing a request:**
1. Find the query you want to investigate — look for `Query received:` entries
2. Note the **request ID** (the short code at the end of each line)
3. Filter by that request ID to see every step: retrieval → generation → response
4. Look for WARN and ERROR entries — they tell you where things went wrong

**Common patterns to look for:**

| Log Pattern | What It Means |
|-------------|--------------|
| `WARN` Failure mode active | A simulated failure is about to fire |
| `WARN` Query modified by failure simulator | The search query was corrupted (bad context mode) |
| `WARN` Low relevance: distance > 1.5 | Retrieved docs don't match the query well |
| `ERROR` RateLimitError | API rejected the request (429) |
| `ERROR` APIStatusError | API is down or timed out (503) |
| `INFO` Suggested action: see Incident Runbook | Points you to the right runbook after a failure |

**Pro tip:** Toggle a failure in Failure Lab, ask a question in Chat, then come here and trace exactly what happened.
""")
