import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import metrics_store

st.title("SLA Dashboard")
st.caption("Monitor uptime, latency SLAs, and error budgets — the metrics TAMs live in daily.")

df = metrics_store.get_metrics()

if df.empty:
    st.info("No requests yet. Ask questions in Chat to generate SLA data.")
    st.stop()

# -- SLA Targets (configurable) --
st.sidebar.header("SLA Targets")
uptime_sla = st.sidebar.selectbox("Uptime SLA", ["99.0%", "99.5%", "99.9%", "99.99%"], index=2)
latency_sla_ms = st.sidebar.number_input("P95 Latency SLA (ms)", value=5000, step=500)
error_rate_sla = st.sidebar.number_input("Max Error Rate (%)", value=1.0, step=0.5)

uptime_target = float(uptime_sla.replace("%", "")) / 100

# -- Calculate SLA metrics --
total_requests = len(df)
successful_requests = df["success"].sum()
failed_requests = total_requests - successful_requests

# Uptime (based on success rate as proxy)
current_uptime = successful_requests / total_requests if total_requests > 0 else 1.0
uptime_pct = current_uptime * 100

# Error rate
error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0

# Error budget
# SLA allows (1 - target) failure rate. Error budget = how much of that allowance is left.
allowed_failure_rate = (1 - uptime_target)
actual_failure_rate = failed_requests / total_requests if total_requests > 0 else 0
error_budget_remaining = max(0, (allowed_failure_rate - actual_failure_rate) / allowed_failure_rate * 100) if allowed_failure_rate > 0 else 100

# Latency P50, P95, P99
p50 = int(df["total_ms"].quantile(0.5))
p95 = int(df["total_ms"].quantile(0.95))
p99 = int(df["total_ms"].quantile(0.99))
latency_sla_met = p95 <= latency_sla_ms

# -- SLA Status Header --
sla_violations = []
if uptime_pct < float(uptime_sla.replace("%", "")):
    sla_violations.append("Uptime")
if not latency_sla_met:
    sla_violations.append("Latency")
if error_rate > error_rate_sla:
    sla_violations.append("Error Rate")

if sla_violations:
    st.error(f"SLA VIOLATION: {', '.join(sla_violations)} targets breached")
else:
    st.success("All SLA targets met")

st.divider()

# -- Top-level metrics --
cols = st.columns(5)

# Uptime
uptime_delta = uptime_pct - float(uptime_sla.replace("%", ""))
cols[0].metric(
    "Uptime",
    f"{uptime_pct:.2f}%",
    delta=f"{uptime_delta:+.2f}% vs SLA",
    delta_color="normal" if uptime_delta >= 0 else "inverse",
)

# Error Budget
budget_color = "normal" if error_budget_remaining > 20 else "inverse"
cols[1].metric(
    "Error Budget Remaining",
    f"{error_budget_remaining:.0f}%",
    delta="Healthy" if error_budget_remaining > 20 else "Burning fast",
    delta_color=budget_color,
)

# P95 Latency
latency_delta = latency_sla_ms - p95
cols[2].metric(
    "P95 Latency",
    f"{p95}ms",
    delta=f"{latency_delta:+d}ms vs SLA",
    delta_color="normal" if latency_delta >= 0 else "inverse",
)

# Error Rate
error_delta = error_rate_sla - error_rate
cols[3].metric(
    "Error Rate",
    f"{error_rate:.1f}%",
    delta=f"{error_delta:+.1f}% vs SLA",
    delta_color="normal" if error_delta >= 0 else "inverse",
)

# Total Requests
cols[4].metric("Total Requests", total_requests)

st.divider()

# -- Error Budget Gauge --
col1, col2 = st.columns(2)

with col1:
    st.subheader("Error Budget")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=error_budget_remaining,
        title={"text": "Budget Remaining (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2ecc71" if error_budget_remaining > 50 else "#f39c12" if error_budget_remaining > 20 else "#e74c3c"},
            "steps": [
                {"range": [0, 20], "color": "#fadbd8"},
                {"range": [20, 50], "color": "#fdebd0"},
                {"range": [50, 100], "color": "#d5f5e3"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 20,
            },
        },
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    **How to read this:**
    - Your SLA target is **{uptime_sla}** uptime
    - That allows **{(1-uptime_target)*100:.2f}%** failure rate
    - You've used **{100-error_budget_remaining:.0f}%** of that budget
    - When it hits 0%, you've breached your SLA
    """)

with col2:
    st.subheader("Latency Distribution")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["total_ms"], nbinsx=20, name="Requests"))
    fig.add_vline(x=latency_sla_ms, line_dash="dash", line_color="red",
                  annotation_text=f"SLA: {latency_sla_ms}ms")
    fig.add_vline(x=p95, line_dash="dash", line_color="orange",
                  annotation_text=f"P95: {p95}ms")
    fig.update_layout(
        xaxis_title="Latency (ms)",
        yaxis_title="Count",
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    | Percentile | Latency |
    |-----------|---------|
    | P50 | {p50}ms |
    | P95 | {p95}ms |
    | P99 | {p99}ms |
    | SLA Target | {latency_sla_ms}ms |
    """)

st.divider()

# -- Uptime over time (rolling window) --
st.subheader("Uptime Trend")

if len(df) >= 5:
    rolling_df = df.sort_values("timestamp").copy()
    rolling_df["request_num"] = range(1, len(rolling_df) + 1)
    window = min(10, len(rolling_df))
    rolling_df["rolling_success"] = rolling_df["success"].rolling(window=window, min_periods=1).mean() * 100

    fig = px.line(
        rolling_df, x="request_num", y="rolling_success",
        title=f"Rolling Uptime ({window}-request window)",
        labels={"rolling_success": "Uptime %", "request_num": "Request #"},
    )
    fig.add_hline(
        y=float(uptime_sla.replace("%", "")),
        line_dash="dash", line_color="red",
        annotation_text=f"SLA: {uptime_sla}",
    )
    fig.update_layout(height=300, yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Need at least 5 requests to show uptime trend.")

st.divider()

# -- SLA breach incidents --
st.subheader("SLA Breach Incidents")

breaches = df[~df["success"]].copy()
if breaches.empty:
    st.success("No SLA breaches recorded.")
else:
    st.dataframe(
        breaches[["timestamp", "query", "failure_mode", "error_message", "total_ms"]].head(20),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f"**{len(breaches)} failed request(s)** out of {total_requests} total ({error_rate:.1f}% error rate)")

st.divider()

# -- SLA explainer --
st.subheader("Understanding SLAs")
st.markdown("""
**What TAMs need to know about SLAs:**

| SLA Target | Allowed Downtime/Month | Allowed Downtime/Year |
|-----------|----------------------|---------------------|
| 99.0% | 7.3 hours | 3.65 days |
| 99.5% | 3.65 hours | 1.83 days |
| 99.9% | 43.8 minutes | 8.77 hours |
| 99.99% | 4.38 minutes | 52.6 minutes |

**Error Budget** is the difference between 100% and your SLA target. It's how much failure you're "allowed" before breaching the SLA.

**In a TAM conversation:**
- *"We're at 99.7% uptime this month against a 99.9% SLA — we've consumed 130% of our error budget. Here's what's burning it..."*
- *"Our P95 latency is 3200ms against a 5000ms SLA — healthy, but trending upward. We should investigate before it becomes a problem."*

**Key insight:** SLAs aren't about being perfect. They're about setting expectations, measuring against them, and having a plan when you miss.
""")
