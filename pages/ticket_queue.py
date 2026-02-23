import streamlit as st

import metrics_store
import failure_simulator

st.title("Ticket Queue")
st.caption("Live tickets generated from failure events. Investigate each ticket using logs and failure details.")

st.divider()

# -- Persona/subject mapping --

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

# -- Initialize ticket status tracking --

if "ticket_statuses" not in st.session_state:
    st.session_state.ticket_statuses = {}

if "open_ticket" not in st.session_state:
    st.session_state.open_ticket = None

# -- Load failures from metrics --

df = metrics_store.get_metrics()

if df.empty or df[~df["success"]].empty:
    st.info("No active tickets. Trigger a failure in **Failure Lab** to generate tickets.")
    st.stop()

failures = df[~df["success"]].copy()

# Group by failure_mode, keep most recent timestamp per mode
grouped = (
    failures.groupby("failure_mode")
    .agg(
        latest_timestamp=("timestamp", "max"),
        count=("failure_mode", "count"),
        latest_error=("error_message", "last"),
        latest_query=("query", "last"),
    )
    .reset_index()
    .sort_values("latest_timestamp", ascending=False)
)

# Filter to known failure modes only
grouped = grouped[grouped["failure_mode"].isin(TICKET_PERSONAS)]

if grouped.empty:
    st.info("No active tickets. Trigger a failure in **Failure Lab** to generate tickets.")
    st.stop()

# -- Ticket list --

if st.session_state.open_ticket is None:
    st.subheader(f"{len(grouped)} Active Ticket(s)")

    for _, row in grouped.iterrows():
        mode = row["failure_mode"]
        persona = TICKET_PERSONAS[mode]
        status = st.session_state.ticket_statuses.get(mode, "Open")
        priority_icon = PRIORITY_COLOR.get(persona["priority"], "⚪")
        count_label = f"{int(row['count'])} occurrence{'s' if row['count'] > 1 else ''}"
        ts = row["latest_timestamp"].strftime("%Y-%m-%d %H:%M UTC")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f"{priority_icon} **{persona['subject']}**  \n"
                f"*{persona['customer']}* · {persona['priority']} · {count_label} · Last seen: {ts}"
            )
        with col2:
            status_badge = {"Open": "🔓 Open", "Investigating": "🔍 Investigating", "Resolved": "✅ Resolved"}.get(status, status)
            st.markdown(f"**{status_badge}**")

        col_a, col_b, col_c = st.columns([2, 2, 4])
        with col_a:
            if st.button("Investigate", key=f"investigate_{mode}"):
                st.session_state.open_ticket = mode
                if status == "Open":
                    st.session_state.ticket_statuses[mode] = "Investigating"
                st.rerun()
        with col_b:
            if status != "Resolved":
                if st.button("Mark Resolved", key=f"resolve_{mode}"):
                    st.session_state.ticket_statuses[mode] = "Resolved"
                    st.rerun()

        st.divider()

# -- Investigation view --

else:
    mode = st.session_state.open_ticket
    persona = TICKET_PERSONAS.get(mode)
    failure_info = failure_simulator.FAILURE_MODES.get(mode)

    if st.button("← Back to Queue"):
        st.session_state.open_ticket = None
        st.rerun()

    st.divider()

    # Ticket header
    priority_icon = PRIORITY_COLOR.get(persona["priority"], "⚪")
    st.subheader(f"{priority_icon} {persona['subject']}")
    st.markdown(f"**From:** {persona['customer']}")
    st.markdown(f"**Priority:** {persona['priority']}")
    status = st.session_state.ticket_statuses.get(mode, "Open")
    st.markdown(f"**Status:** {status}")

    st.divider()

    # Customer error message from logs
    mode_logs = failures[failures["failure_mode"] == mode].sort_values("timestamp", ascending=False)
    latest = mode_logs.iloc[0]

    st.subheader("Customer Report")
    st.markdown(f"> **Error:** `{latest['error_message']}`")
    st.markdown(f"> **Query that triggered it:** *{latest['query']}*")

    st.divider()

    # Failure mode details
    if failure_info:
        st.subheader("Failure Mode Details")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**What it is:** {failure_info['description']}")
            st.markdown(f"**Root cause:** {failure_info['cause']}")
        with col2:
            st.markdown(f"**Recommended fix:** {failure_info['fix']}")

    st.divider()

    # Related log entries
    st.subheader("Related Log Entries (last 5)")
    recent_logs = mode_logs.head(5)[["timestamp", "query", "error_message", "total_ms"]]
    st.dataframe(recent_logs, use_container_width=True, hide_index=True)

    st.divider()

    # Resolution checklist
    st.subheader("Resolution Checklist")
    checklist_items = [
        "Reproduced the failure in Failure Lab",
        "Identified root cause from logs",
        "Drafted customer-facing response",
        "Applied or recommended fix",
        "Verified fix resolves the failure",
    ]
    for item in checklist_items:
        st.checkbox(item, key=f"checklist_{mode}_{item[:20]}")

    st.divider()

    # Response drafting
    st.subheader("Draft Customer Response")
    response = st.text_area(
        "Your response",
        height=220,
        placeholder="Hi [Customer],\n\nThank you for reaching out. I can see the issue...\n\n",
        key=f"queue_response_{mode}",
    )

    col_resolve, _ = st.columns([2, 6])
    with col_resolve:
        if st.button("Mark as Resolved", type="primary"):
            st.session_state.ticket_statuses[mode] = "Resolved"
            st.session_state.open_ticket = None
            st.success("Ticket resolved.")
            st.rerun()
