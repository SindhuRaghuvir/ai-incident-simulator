import streamlit as st

import failure_simulator

st.title("Failure Lab")
st.caption("Toggle failure modes to simulate production issues. Active failures affect the Chat tab in real time.")
st.markdown(
    "🔊 **Loud** failures return an error code, so dashboards catch them. "
    "🔇 **Silent** failures return 200 OK with a bad answer, and only quality checks catch them."
)

st.divider()

for key, mode in failure_simulator.FAILURE_MODES.items():
    col1, col2 = st.columns([1.5, 3])

    with col1:
        state_key = f"failure_{key}"
        current = st.session_state.get(state_key, False)
        toggled = st.toggle(mode["label"], value=current, key=f"toggle_{key}")
        st.session_state[state_key] = toggled

    with col2:
        status = "ACTIVE" if toggled else "Inactive"
        color = "red" if toggled else "green"
        kind = "🔇 Silent (200 OK)" if mode.get("kind") == "silent" else "🔊 Loud (error code)"
        st.markdown(f"**Status:** :{color}[{status}] · {kind}")
        st.markdown(f"**What it does:** {mode['description']}")

        with st.expander("Root Cause & Fix"):
            st.markdown(f"**Cause:** {mode['cause']}")
            st.markdown(f"**Fix:** {mode['fix']}")

    st.divider()

# -- Summary --
active = failure_simulator.get_active_failures(st.session_state)
if active:
    st.warning(f"**{len(active)} failure mode(s) active.** Go to Chat to see their effect.")
else:
    st.success("All systems nominal. Toggle a failure mode above to simulate issues.")

# -- Hallucination analysis walkthrough --
st.subheader("🔎 Hallucination Analysis")
st.markdown("""
Every answer in **Chat** is checked by a second model (an LLM judge at temperature 0). It breaks the answer
into individual claims and checks each one against the chunks that were actually sent to the model:
✅ **supported**, ⚠️ **unsupported** (invented), or ❌ **contradicted**. The **groundedness score** is the
share of supported claims. Anything under 80% is logged as a WARN on the `eval` component and flagged on the ticket.

**Run the analysis:**

1. Make sure **Hallucination check** is on in the Chat sidebar (it is by default).
2. **Baseline**: with every failure off, ask *"How long do refunds take to process?"* The KB doesn't say, so the
   correct answer is "the documentation doesn't specify", which scores as *no factual claims*.
3. Toggle **Hallucination** above and ask the same question. Expect an invented, confident answer
   (e.g. *"5–7 business days"*) and a groundedness score well under 80%.
4. Open **Hallucination analysis** under the answer. Count the ⚠️ and ❌ claims, and look for exact numbers or dates the docs never mention.
5. In **Logs**, filter to `retrieval`, `generation` and `eval`:
   - `retrieval`: did the right source come back? (In this mode, the best chunk is deliberately dropped.)
   - `generation`: *"Non-default system prompt in use"* and a raised temperature point to the root cause.
   - `eval`: the groundedness WARN line, with its request ID, is your evidence for the ticket.
6. Decide which half failed: **retrieval** (the right chunk never arrived) or **generation** (it arrived and was ignored).
7. Toggle it off, re-ask, and confirm the score recovers. Then check **Ticket Queue** for the new P1 and write the **RCA**.

**What groundedness can't catch** (try these too):

| Mode | Why the score misleads |
|------|------------------------|
| Prompt Injection | Claims *are* supported, but by the poisoned source. Check **which** sources were used, not just whether claims match them. |
| Stale / Bad Context | The model usually says it doesn't know, so there are no claims to score. The signal is the high retrieval distance. |
| Questions outside the KB | A correct "I don't have that information" scores as *no claims*. That's the right behaviour, not a failure. |

Groundedness measures **faithfulness to the sources**, not **truth**. If the docs themselves are wrong, the
answer can be 100% grounded and still wrong. That's why teams also keep a golden evaluation set of questions with known answers.
""")

st.divider()

# -- Educational section --
st.subheader("Why Failure Simulation Matters")
st.markdown("""
In production AI systems, failures are inevitable. Understanding how your system behaves under
different failure conditions is critical for building resilient applications.

**Key patterns for production AI:**

| Pattern | Purpose |
|---------|---------|
| **Exponential Backoff** | Handle rate limits without overwhelming the API |
| **Circuit Breaker** | Stop sending requests to a failing service |
| **Fallback Responses** | Provide degraded but functional responses during outages |
| **Relevance Thresholds** | Detect when retrieval quality drops below acceptable levels |
| **Parameter Validation** | Prevent misconfigured API calls from reaching production |
| **Groundedness Checks** | Catch hallucinations that return 200 OK |
| **Treat Retrieved Text as Data** | Stop instructions hidden in documents from hijacking the model |
| **Request Queuing** | Smooth out traffic spikes to stay within rate limits |

---

**Further Reading — RAG Failure Troubleshooting:**

- [Seven RAG Pitfalls and How to Solve Them](https://labelstud.io/blog/seven-ways-your-rag-system-could-be-failing-and-how-to-fix-them/) — 7 specific failure points with fixes
- [RAG in Production: What Actually Breaks](https://alwyns2508.medium.com/retrieval-augmented-generation-rag-in-production-what-actually-breaks-and-how-to-fix-it-5f76c94c0591) — production-focused debugging
- [Debugging RAG Pipelines](https://www.getmaxim.ai/articles/rag-debugging-identifying-issues-in-retrieval-augmented-generation/) — step-by-step debugging guide
- [10 RAG Failure Modes at Scale](https://medium.com/@bhagyarana80/10-rag-failure-modes-at-scale-and-how-to-fix-them-158240ce3a05) — drift, stale indexes, chunking bugs
- [Enterprise RAG Failures: 5-Part Framework](https://www.analyticsvidhya.com/blog/2025/07/silent-killers-of-production-rag/) — why 80% of enterprise RAG projects fail
- [Fixing RAG in 2026](https://medium.com/@gokulpalanisamy/fixing-rag-in-2026-why-your-enterprise-search-underperforms-and-what-actually-works-93480190fdd0) — hybrid search vs dense-only retrieval
- [Seven Failure Points in RAG Systems (Paper)](https://arxiv.org/abs/2401.05856) — the original research taxonomy
- [RAG Failure Modes (Snorkel AI)](https://snorkel.ai/blog/retrieval-augmented-generation-rag-failure-modes-and-how-to-fix-them/) — data-centric approach to fixes
""")
