import streamlit as st

st.set_page_config(
    page_title="Stratify Labs Knowledge Assistant",
    page_icon="🔍",
    layout="wide",
)

# -- Initialize shared state --

if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb_ingested" not in st.session_state:
    st.session_state.kb_ingested = False

# Auto-ingest knowledge base on first run
if not st.session_state.kb_ingested:
    import rag_engine
    with st.spinner("Indexing knowledge base..."):
        count = rag_engine.ingest_knowledge_base()
    st.session_state.kb_ingested = True
    st.session_state.kb_chunk_count = count

# -- Navigation --

chat_page = st.Page("pages/chat.py", title="Chat", icon="💬")
failure_page = st.Page("pages/failure_lab.py", title="Failure Lab", icon="⚠️")
queue_page = st.Page("pages/ticket_queue.py", title="Ticket Queue", icon="🎫")
resolved_page = st.Page("pages/resolved_tickets.py", title="Resolved Tickets", icon="✅")
runbook_page = st.Page("pages/incident_runbook.py", title="Incident Runbook", icon="📖")
logs_page = st.Page("pages/logs_viewer.py", title="Logs", icon="📜")
metrics_page = st.Page("pages/metrics_dashboard.py", title="Metrics", icon="📊")
cost_page = st.Page("pages/cost_dashboard.py", title="Cost", icon="💰")
sla_page = st.Page("pages/sla_dashboard.py", title="SLA", icon="🛡️")
rca_page = st.Page("pages/rca_templates.py", title="RCA", icon="📋")

pg = st.navigation([chat_page, failure_page, queue_page, resolved_page, runbook_page, logs_page, metrics_page, cost_page, sla_page, rca_page])
pg.run()
