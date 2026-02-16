import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
import metrics_store

st.title("Cost Dashboard")

df = metrics_store.get_metrics()

if df.empty:
    st.info("No requests yet. Ask some questions in the Chat tab first.")
    st.stop()

# -- Summary --
total_cost = df["estimated_cost"].sum()
successful = df[df["success"]]
avg_cost = successful["estimated_cost"].mean() if not successful.empty else 0

cols = st.columns(4)
cols[0].metric("Total Spend", f"${total_cost:.4f}")
cols[1].metric("Avg Cost / Request", f"${avg_cost:.4f}")
cols[2].metric("Total Input Tokens", f"{int(df['input_tokens'].sum()):,}")
cols[3].metric("Total Output Tokens", f"{int(df['output_tokens'].sum()):,}")

st.divider()

# -- Cumulative cost --
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cumulative Cost")
    cost_over_time = df.sort_values("timestamp").copy()
    cost_over_time["cumulative_cost"] = cost_over_time["estimated_cost"].cumsum()
    fig = px.area(
        cost_over_time,
        x="timestamp",
        y="cumulative_cost",
        title="Cumulative Cost Over Time",
        labels={"cumulative_cost": "Cost ($)", "timestamp": ""},
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Cost per Request")
    fig = px.bar(
        df.sort_values("timestamp"),
        x="timestamp",
        y="estimated_cost",
        color="model",
        title="Cost per Request",
        labels={"estimated_cost": "Cost ($)", "timestamp": ""},
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -- Model cost comparison --
st.subheader("Model Pricing Comparison")
st.caption("How much would your queries cost on different models?")

if not successful.empty:
    comparison = []
    for model_name, pricing in config.MODELS.items():
        projected_cost = (
            (successful["input_tokens"].sum() / 1000) * pricing["input_cost_per_1k"]
            + (successful["output_tokens"].sum() / 1000) * pricing["output_cost_per_1k"]
        )
        comparison.append({
            "Model": model_name,
            "Projected Cost": projected_cost,
            "Input $/1K tokens": pricing["input_cost_per_1k"],
            "Output $/1K tokens": pricing["output_cost_per_1k"],
        })

    comp_df = pd.DataFrame(comparison)
    fig = px.bar(
        comp_df,
        x="Model",
        y="Projected Cost",
        title="Projected Cost by Model (Same Token Usage)",
        text_auto="$.4f",
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(comp_df, use_container_width=True, hide_index=True,
                 column_config={"Projected Cost": st.column_config.NumberColumn(format="$%.4f")})

st.divider()

# -- Cost impact of parameters --
st.subheader("Parameter Impact on Cost")

col3, col4 = st.columns(2)
with col3:
    if len(successful["top_k"].unique()) > 1:
        fig = px.scatter(
            successful, x="top_k", y="estimated_cost",
            title="Top-K vs Cost", trendline="ols",
            labels={"top_k": "Top-K Chunks", "estimated_cost": "Cost ($)"},
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Vary the top-k setting in Chat to see its impact on cost.")

with col4:
    if len(successful["temperature"].unique()) > 1:
        fig = px.scatter(
            successful, x="temperature", y="output_tokens",
            title="Temperature vs Output Length", trendline="ols",
            labels={"temperature": "Temperature", "output_tokens": "Output Tokens"},
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Vary the temperature in Chat to see its impact on output length.")
