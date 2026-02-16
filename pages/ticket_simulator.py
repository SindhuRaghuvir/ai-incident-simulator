import random
import streamlit as st

import metrics_store
import failure_simulator

st.title("Customer Ticket Simulator")
st.caption("Practice handling real support tickets. Read the customer's message, investigate, and write your response — just like a TAM interview.")

st.divider()

# -- Ticket templates --

TICKETS = {
    "rate_limit": [
        {
            "customer": "Sarah Chen, Engineering Lead at Finova",
            "priority": "P2 - High",
            "subject": "API calls failing intermittently since this morning",
            "message": """Hi Support,

Since about 9am today, our integration has been returning errors intermittently. Roughly 30% of our API calls are failing with some kind of 429 error. This is impacting our customer-facing search feature.

We haven't changed anything on our end. Can you look into this urgently?

Thanks,
Sarah""",
            "hints": [
                "Check their plan's rate limits vs current usage",
                "Look at Metrics Dashboard for the spike in failures",
                "Check if they recently deployed a new feature that increased API calls",
                "Look at the timestamps — are failures clustered or spread out?",
            ],
            "good_response_points": [
                "Acknowledge the impact on their customer-facing feature",
                "Explain what a 429 error means (rate limit exceeded)",
                "Ask about recent changes (new integration, traffic increase)",
                "Suggest immediate mitigation (exponential backoff)",
                "Offer to review their plan limits vs usage",
            ],
        },
        {
            "customer": "Mike Rodriguez, CTO at HealthBridge",
            "priority": "P1 - Critical",
            "subject": "URGENT: All API requests blocked, production down",
            "message": """We're getting rate limited on EVERY request. Our entire production search is down.

We just launched a new feature that our sales team demoed to a big client. This is extremely time-sensitive.

Error: "Rate limit reached for gpt-4o-mini. Limit: 60 RPM."

We need this fixed NOW.

Mike""",
            "hints": [
                "This is an urgent customer — acknowledge the severity immediately",
                "They launched a new feature without load testing",
                "60 RPM suggests they're on the Starter plan",
                "Immediate action: help them implement backoff, discuss plan upgrade",
            ],
            "good_response_points": [
                "Respond with urgency — 'I understand this is blocking your production'",
                "Don't blame them for the launch without testing",
                "Explain the 60 RPM limit on their current plan",
                "Offer immediate help: implement backoff + request queuing",
                "Suggest upgrading to Professional (300 RPM) for their use case",
                "Offer a temporary rate limit increase while they evaluate",
            ],
        },
    ],
    "timeout": [
        {
            "customer": "Alex Kim, DevOps Engineer at RetailStack",
            "priority": "P1 - Critical",
            "subject": "Knowledge search completely unresponsive",
            "message": """Hi team,

Our knowledge search has been completely unresponsive for the last 45 minutes. All requests are timing out after 30 seconds. This started at approximately 2:15 PM EST.

We've checked our infrastructure and everything on our end looks healthy. Is there an ongoing outage?

Our SLA requires 99.9% uptime and we're burning through our error budget fast.

Regards,
Alex""",
            "hints": [
                "Check the status page first — is there a known outage?",
                "They mentioned SLA — this needs careful handling",
                "They've already ruled out their own infrastructure",
                "45 minutes of downtime on 99.9% SLA = significant budget burn",
            ],
            "good_response_points": [
                "Confirm whether there's a known outage (check status page)",
                "Acknowledge the SLA concern explicitly",
                "Provide specific timeline: when it started, when you expect resolution",
                "Commit to regular updates (every 30 minutes)",
                "Mention SLA credit if the outage exceeds their SLA terms",
                "After resolution: share post-incident report",
            ],
        },
    ],
    "bad_context": [
        {
            "customer": "Priya Sharma, Product Manager at EduTech Global",
            "priority": "P2 - High",
            "subject": "Search quality has degraded significantly",
            "message": """Hi,

Over the past week, we've noticed that our knowledge assistant is returning increasingly irrelevant answers. Questions that used to get perfect responses are now pulling in completely wrong information.

For example, when a user asks "How do I reset my password?", the assistant talks about billing plans instead.

We updated our knowledge base articles last Wednesday. Could that be related?

Best,
Priya""",
            "hints": [
                "They updated their knowledge base last Wednesday — that's likely the trigger",
                "Were the docs updated but not re-indexed?",
                "Check if chunking split the password reset info away from its context",
                "Look at retrieval distance scores in the logs",
            ],
            "good_response_points": [
                "Connect the timing: degradation started after their Wednesday update",
                "Explain the relationship between doc updates and embeddings/re-indexing",
                "Offer to re-index their knowledge base",
                "Suggest monitoring retrieval quality scores going forward",
                "Recommend a test suite of known question-answer pairs",
            ],
        },
        {
            "customer": "James Liu, Support Director at CloudNine",
            "priority": "P3 - Medium",
            "subject": "Assistant giving confidently wrong answers",
            "message": """Hey,

We've been getting complaints from our support agents that the AI assistant is confidently giving wrong answers. It doesn't say "I don't know" — it just makes stuff up that sounds plausible but isn't in our docs.

This is worse than no answer at all because agents are trusting it and sending wrong info to customers.

Can we add some kind of confidence check?

James""",
            "hints": [
                "This is a hallucination / low-relevance retrieval issue",
                "The ask is for a relevance threshold — if confidence is low, say 'I don't know'",
                "Check distance scores — high distance = low relevance",
                "This might also be a temperature issue if responses are too creative",
            ],
            "good_response_points": [
                "Acknowledge the severity — wrong answers erode agent trust",
                "Explain the concept of relevance thresholds",
                "Recommend setting a distance threshold (e.g., > 1.5 = 'I don't have enough info')",
                "Suggest reviewing the temperature setting (lower = more factual)",
                "Offer to help set up quality monitoring",
            ],
        },
    ],
    "high_temperature": [
        {
            "customer": "Dana Foster, QA Lead at LegalAI",
            "priority": "P3 - Medium",
            "subject": "Inconsistent responses for the same question",
            "message": """Hi Support,

We're running compliance testing on the knowledge assistant, and we're seeing a problem: the same question gives wildly different answers each time we ask it.

For legal use cases, we need deterministic, consistent responses. Is there a way to make the output more predictable?

Example:
- Ask 1: "What is our data retention policy?" → Correct, professional answer
- Ask 2: Same question → Rambling, informal, includes irrelevant details
- Ask 3: Same question → Partially correct but contradicts Ask 1

Dana""",
            "hints": [
                "This is almost certainly a temperature issue",
                "Legal/compliance use case demands temperature close to 0",
                "Check if someone changed the config or if user controls are unrestricted",
                "They need deterministic output — recommend temperature 0.0-0.1",
            ],
            "good_response_points": [
                "Explain what temperature does in simple terms",
                "Recommend temperature 0.0-0.1 for compliance/legal use cases",
                "Offer to lock the temperature setting for their account",
                "Suggest they also use a fixed model version for consistency",
                "Mention that even at temperature 0, minor variation is possible",
            ],
        },
    ],
}

# -- Ticket selection --

st.subheader("Select a Scenario")

# Build flat list of all tickets with labels
all_tickets = []
for failure_key, tickets in TICKETS.items():
    for i, ticket in enumerate(tickets):
        label = f"{failure_simulator.FAILURE_MODES[failure_key]['label']} — {ticket['subject']}"
        all_tickets.append((label, failure_key, ticket))

# Random ticket button
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Random Ticket"):
        st.session_state.selected_ticket_idx = random.randint(0, len(all_tickets) - 1)

selected_idx = st.session_state.get("selected_ticket_idx", 0)

with col2:
    ticket_labels = [t[0] for t in all_tickets]
    selected_idx = st.selectbox(
        "Or choose a specific ticket",
        range(len(ticket_labels)),
        format_func=lambda i: ticket_labels[i],
        index=selected_idx,
        label_visibility="collapsed",
    )

st.session_state.selected_ticket_idx = selected_idx
label, failure_key, ticket = all_tickets[selected_idx]

st.divider()

# -- Display ticket --

st.subheader("Incoming Ticket")

st.markdown(f"**From:** {ticket['customer']}")
st.markdown(f"**Priority:** {ticket['priority']}")
st.markdown(f"**Subject:** {ticket['subject']}")
st.markdown("---")
st.markdown(ticket["message"])

st.divider()

# -- Investigation section --

st.subheader("Your Investigation")
st.markdown("Before responding, investigate the issue. What would you check?")

with st.expander("Investigation Hints (click after you've thought about it)"):
    for i, hint in enumerate(ticket["hints"], 1):
        st.markdown(f"{i}. {hint}")

    st.markdown("---")
    st.markdown(f"**Related failure mode:** Go to **Failure Lab** and toggle **{failure_simulator.FAILURE_MODES[failure_key]['label']}**, then ask a question in **Chat** to see this failure in action. Check **Logs** to trace what happened.")

# -- Check recent metrics for context --
df = metrics_store.get_metrics()
if not df.empty:
    failed = df[~df["success"]]
    if not failed.empty:
        with st.expander("Recent System Data (from your Metrics)"):
            recent = failed.head(5)
            st.dataframe(
                recent[["timestamp", "query", "failure_mode", "error_message", "total_ms"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption("Use this data to inform your investigation — a real TAM would pull this from Datadog/Splunk.")

st.divider()

# -- Response section --

st.subheader("Write Your Response")
st.markdown("Draft your reply to the customer. Think about: empathy, clarity, next steps.")

response = st.text_area(
    "Your response to the customer",
    height=250,
    placeholder="Hi [Customer],\n\nThank you for reaching out. I understand this is impacting...\n\n",
    key=f"response_{selected_idx}",
)

if response:
    st.divider()
    st.subheader("Response Review")
    st.markdown("Check your response against these points:")

    for point in ticket["good_response_points"]:
        st.checkbox(point, key=f"check_{selected_idx}_{point[:20]}")

    st.markdown("---")
    st.markdown("""
    **TAM Response Formula:**
    1. **Empathy** — Show you understand the impact
    2. **Status** — What do you know right now?
    3. **Action** — What are you doing about it?
    4. **Timeline** — When will they hear back?
    5. **Prevention** — How do you stop it happening again?
    """)

st.divider()

# -- Interview context --
st.subheader("Interview Context")
st.markdown(f"""
**This ticket simulates a `{failure_simulator.FAILURE_MODES[failure_key]['label']}` scenario.**

In a TAM interview, you might be asked:

> *"Walk me through how you would handle this support ticket."*

Your answer should cover:
1. **Triage** — Assess priority and impact
2. **Investigate** — What data do you look at? (Logs, metrics, status page)
3. **Communicate** — What do you tell the customer right now?
4. **Resolve** — Technical steps to fix it
5. **Follow up** — RCA, prevention, relationship management

**Pro tip:** Use this app as a live demo. Toggle the failure in Failure Lab, reproduce the issue in Chat, show the logs in Logs Viewer, and reference the Incident Runbook. That tells the interviewer you can *do* the job, not just talk about it.
""")
