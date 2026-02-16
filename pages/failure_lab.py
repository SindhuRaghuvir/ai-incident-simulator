import streamlit as st

import failure_simulator

st.title("Failure Lab")
st.caption("Toggle failure modes to simulate production issues. Active failures affect the Chat tab in real time.")

st.divider()

for key, mode in failure_simulator.FAILURE_MODES.items():
    col1, col2 = st.columns([1, 3])

    with col1:
        state_key = f"failure_{key}"
        current = st.session_state.get(state_key, False)
        toggled = st.toggle(mode["label"], value=current, key=f"toggle_{key}")
        st.session_state[state_key] = toggled

    with col2:
        status = "ACTIVE" if toggled else "Inactive"
        color = "red" if toggled else "green"
        st.markdown(f"**Status:** :{color}[{status}]")
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
