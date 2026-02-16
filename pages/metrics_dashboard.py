import streamlit as st
import plotly.express as px

import metrics_store

st.title("Metrics Dashboard")

df = metrics_store.get_metrics()

if df.empty:
    st.info("No requests yet. Ask some questions in the Chat tab first.")
    st.stop()

# -- Summary row --
summary = metrics_store.get_summary()
cols = st.columns(5)
cols[0].metric("Total Requests", summary["total_requests"])
cols[1].metric("Success Rate", f"{summary['success_rate']:.0f}%")
cols[2].metric("Avg Latency", f"{summary['avg_latency_ms']}ms")
cols[3].metric("Total Tokens", f"{summary['total_tokens']:,}")
cols[4].metric("Total Cost", f"${summary['total_cost']:.4f}")

st.divider()

# -- Latency over time --
col1, col2 = st.columns(2)

with col1:
    st.subheader("Latency Breakdown")
    latency_df = df[["timestamp", "retrieval_ms", "generation_ms"]].copy()
    latency_df = latency_df.melt(
        id_vars="timestamp",
        value_vars=["retrieval_ms", "generation_ms"],
        var_name="Phase",
        value_name="Latency (ms)",
    )
    latency_df["Phase"] = latency_df["Phase"].map({
        "retrieval_ms": "Retrieval",
        "generation_ms": "Generation",
    })
    fig = px.bar(
        latency_df,
        x="timestamp",
        y="Latency (ms)",
        color="Phase",
        barmode="stack",
        title="Latency per Request",
    )
    fig.update_layout(xaxis_title="", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Token Usage")
    token_df = df[["timestamp", "input_tokens", "output_tokens"]].copy()
    token_df = token_df.melt(
        id_vars="timestamp",
        value_vars=["input_tokens", "output_tokens"],
        var_name="Type",
        value_name="Tokens",
    )
    token_df["Type"] = token_df["Type"].map({
        "input_tokens": "Input",
        "output_tokens": "Output",
    })
    fig = px.bar(
        token_df,
        x="timestamp",
        y="Tokens",
        color="Type",
        barmode="stack",
        title="Tokens per Request",
    )
    fig.update_layout(xaxis_title="", height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -- Success vs failure --
col3, col4 = st.columns(2)

with col3:
    st.subheader("Success vs Failure")
    status_counts = df["success"].value_counts().reset_index()
    status_counts.columns = ["success", "count"]
    status_counts["status"] = status_counts["success"].map({True: "Success", False: "Failed"})
    fig = px.pie(status_counts, values="count", names="status", color="status",
                 color_discrete_map={"Success": "#2ecc71", "Failed": "#e74c3c"})
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Failure Modes")
    failed = df[df["failure_mode"] != ""]
    if failed.empty:
        st.info("No failures recorded yet.")
    else:
        mode_counts = failed["failure_mode"].value_counts().reset_index()
        mode_counts.columns = ["mode", "count"]
        fig = px.bar(mode_counts, x="mode", y="count", title="Failures by Mode")
        fig.update_layout(height=300, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# -- Request log --
st.subheader("Request Log")
display_cols = ["timestamp", "query", "model", "total_ms", "input_tokens", "output_tokens",
                "success", "failure_mode", "estimated_cost"]
st.dataframe(
    df[display_cols].head(50),
    use_container_width=True,
    hide_index=True,
    column_config={
        "estimated_cost": st.column_config.NumberColumn(format="$%.4f"),
        "timestamp": st.column_config.DatetimeColumn(format="HH:mm:ss"),
    },
)
