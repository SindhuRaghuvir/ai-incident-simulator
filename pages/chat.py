import time
import streamlit as st

import config
import rag_engine
import metrics_store
import failure_simulator
import logger

# -- Sidebar controls --

st.sidebar.header("Settings")

model = st.sidebar.selectbox("Model", list(config.MODELS.keys()), index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, config.DEFAULT_TEMPERATURE, 0.1)
top_k = st.sidebar.slider("Retrieved chunks (top-k)", 1, 10, config.TOP_K_RESULTS)
check_hallucinations = st.sidebar.toggle(
    "Hallucination check", value=True,
    help="After each answer, an LLM judge checks every claim against the retrieved chunks and reports a groundedness score.",
)

# -- File upload --
st.sidebar.divider()
st.sidebar.header("Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Add to knowledge base",
    type=["md", "txt"],
    accept_multiple_files=True,
    key="file_uploader",
)
if uploaded_files:
    for uf in uploaded_files:
        file_key = f"uploaded_{uf.name}_{uf.size}"
        if file_key not in st.session_state:
            content = uf.read().decode("utf-8")
            new_chunks = rag_engine.ingest_text(content, uf.name)
            st.session_state.setdefault("uploaded_chunks", []).extend(new_chunks)
            chunk_count = len(new_chunks)
            st.session_state[file_key] = chunk_count
            st.session_state.kb_chunk_count = st.session_state.get("kb_chunk_count", 0) + chunk_count
            st.sidebar.success(f"Added **{uf.name}** ({chunk_count} chunks)")
            logger.info(f"Uploaded file: {uf.name} — indexed {chunk_count} chunks", component="ingest")
        else:
            st.sidebar.info(f"{uf.name} already indexed ({st.session_state[file_key]} chunks)")

# Show active failures
active = failure_simulator.get_active_failures(st.session_state)
if active:
    st.sidebar.divider()
    st.sidebar.markdown("**Active Failures**")
    for key in active:
        label = failure_simulator.FAILURE_MODES[key]["label"]
        st.sidebar.warning(label)

# -- Main chat area --

st.title("Stratify Labs Knowledge Assistant")
st.caption(f"Indexed {st.session_state.get('kb_chunk_count', 0)} chunks from knowledge base")

VERDICT_ICON = {"supported": "✅", "unsupported": "⚠️", "contradicted": "❌"}


def render_groundedness(g: dict):
    """Show the hallucination check: score line + per-claim breakdown."""
    if g["score"] is None:
        st.caption("🔎 Hallucination check: no factual claims to verify (refusal or fallback answer)")
        return
    pct = int(round(g["score"] * 100))
    color = "green" if pct >= 80 else "orange" if pct >= 50 else "red"
    st.markdown(
        f"🔎 **Groundedness:** :{color}[{pct}%] · {g['supported']}/{g['total']} claims supported by sources"
    )
    with st.expander("Hallucination analysis"):
        for c in g["claims"]:
            icon = VERDICT_ICON.get(c.get("verdict"), "❔")
            st.markdown(f"{icon} **{c.get('verdict', '?')}** — {c.get('claim', '')}")
            if c.get("evidence"):
                st.caption(f"Source says: “{c['evidence']}”")
        st.caption(f"Judge: {config.DEFAULT_MODEL}, temperature 0 · {g['check_ms']}ms · ${g['estimated_cost']:.5f}")


# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("groundedness"):
            render_groundedness(msg["groundedness"])

# Suggested questions — always shown, refreshes after every answer
import random

from suggestions import SUGGESTIONS, HALLUCINATION_BAIT


def pick_suggestions(n: int = 6) -> list[str]:
    """One question from each of n different KB docs, so every refresh covers a
    spread of topics. While the Hallucination failure is on, half of them are
    questions the KB deliberately doesn't answer."""
    by_doc = {}
    for s in SUGGESTIONS:
        by_doc.setdefault(s["doc"], []).append(s["q"])
    picks = [random.choice(by_doc[doc]) for doc in random.sample(list(by_doc), n)]
    if "hallucination" in active:
        picks[: n // 2] = [b["q"] for b in random.sample(HALLUCINATION_BAIT, n // 2)]
    return picks


bait_mode = "hallucination" in active
if "current_suggestions" not in st.session_state or st.session_state.get("suggestions_bait_mode") != bait_mode:
    st.session_state.current_suggestions = pick_suggestions()
    st.session_state.suggestions_bait_mode = bait_mode

st.markdown("**Try asking:**")
if bait_mode:
    st.caption("Hallucination mode is on: questions marked ⚠️ aren't answered by the docs. Watch the groundedness score.")
bait_questions = {b["q"] for b in HALLUCINATION_BAIT}
cols = st.columns(2)
for i, suggestion in enumerate(st.session_state.current_suggestions):
    label = f"⚠️ {suggestion}" if suggestion in bait_questions else suggestion
    if cols[i % 2].button(label, use_container_width=True):
        st.session_state.pending_prompt = suggestion
        st.rerun()

# Pick up a suggestion click or typed input
# chat_input must always be rendered so it never disappears
typed = st.chat_input("Ask about Stratify Labs...")
prompt = st.session_state.pop("pending_prompt", None) or typed
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process
    with st.chat_message("assistant"):
        failure_mode = ", ".join(active) if active else ""
        total_start = time.time()
        req_id = logger.new_request_id()

        try:
            logger.info(f"Query received: \"{prompt}\"", request_id=req_id, component="chat")

            # Log active failures
            if active:
                for key in active:
                    logger.warn(
                        f"Failure mode active: {key}",
                        request_id=req_id, component="failure_sim",
                    )

            # 1. Retrieval (with failure hook)
            logger.info(
                f"Retrieval started — searching with top_k={top_k}",
                request_id=req_id, component="retrieval",
            )
            retrieval_query = failure_simulator.pre_retrieval(prompt, st.session_state)

            if retrieval_query != prompt:
                logger.warn(
                    f"Query modified by failure simulator: \"{retrieval_query}\"",
                    request_id=req_id, component="failure_sim",
                )

            retrieval_start = time.time()
            context_docs = rag_engine.retrieve(
                retrieval_query, top_k=top_k,
                extra_docs=st.session_state.get("uploaded_chunks"),
            )
            context_docs = failure_simulator.post_retrieval(context_docs, st.session_state)
            retrieval_ms = int((time.time() - retrieval_start) * 1000)

            if not context_docs:
                logger.warn(
                    "Retrieval returned 0 results",
                    request_id=req_id, component="retrieval",
                )
                st.warning("No relevant documents found.")
                answer = "I couldn't find any relevant information in the knowledge base."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                metrics_store.log_request(
                    query=prompt, model=model, temperature=temperature, top_k=top_k,
                    retrieval_ms=retrieval_ms, total_ms=int((time.time() - total_start) * 1000),
                    success=False, failure_mode=failure_mode,
                    error_message="Retrieval returned 0 results — index empty or not loaded",
                )
                st.stop()

            best_distance = min(doc["distance"] for doc in context_docs)
            sources = ", ".join(doc["source"] for doc in context_docs)
            logger.info(
                f"Retrieval complete — {len(context_docs)} chunks found (best distance: {best_distance:.3f}) from [{sources}]",
                request_id=req_id, component="retrieval",
            )

            if best_distance > 1.5:
                logger.warn(
                    f"Low relevance: best distance {best_distance:.3f} exceeds threshold 1.5",
                    request_id=req_id, component="retrieval",
                )

            # 2. Generation (with failure hook)
            gen_params = {"model": model, "temperature": temperature, "max_tokens": 1024}
            context_docs, gen_params = failure_simulator.pre_generation(
                context_docs, gen_params, st.session_state
            )

            logger.info(
                f"Sending to OpenAI {gen_params['model']} (temperature={gen_params['temperature']})",
                request_id=req_id, component="generation",
            )

            # Stream tokens to the screen as they arrive
            token_stream, result = rag_engine.generate_stream(
                query=prompt,
                context_docs=context_docs,
                model=gen_params["model"],
                temperature=gen_params["temperature"],
                max_tokens=gen_params["max_tokens"],
                system_prompt=gen_params.get("system_prompt"),
            )
            st.write_stream(token_stream)

            total_ms = int((time.time() - total_start) * 1000)

            logger.info(
                f"Response received — {result['output_tokens']} tokens in {result['generation_ms']}ms "
                f"(first token after {result.get('first_token_ms', result['generation_ms'])}ms)",
                request_id=req_id, component="generation",
            )
            # Silent-failure signals: the request "succeeded", but something is off
            observations = []
            if result.get("finish_reason") == "length":
                observations.append(f"Answer truncated (finish_reason=length, max_tokens={gen_params['max_tokens']})")
                logger.warn(observations[-1], request_id=req_id, component="generation")
            if gen_params.get("system_prompt"):
                logger.warn("Non-default system prompt in use", request_id=req_id, component="generation")
            other_ms = total_ms - retrieval_ms - result["generation_ms"]
            if total_ms > 5000:
                observations.append(
                    f"Slow response: {total_ms}ms total (retrieval {retrieval_ms}ms, generation {result['generation_ms']}ms, waiting {other_ms}ms)"
                )
                logger.warn(f"{observations[-1]} exceeds 5000ms latency SLO", request_id=req_id, component="chat")

            # Hallucination check (LLM-as-judge groundedness)
            groundedness = None
            if check_hallucinations and result["answer"].strip():
                with st.spinner("Checking answer against sources..."):
                    groundedness = rag_engine.check_groundedness(result["answer"], context_docs)
                render_groundedness(groundedness)
                if groundedness["score"] is not None:
                    pct = int(round(groundedness["score"] * 100))
                    unsupported = groundedness["total"] - groundedness["supported"]
                    msg = f"Groundedness {pct}% — {unsupported} of {groundedness['total']} claims not supported by retrieved context"
                    if pct < 80:
                        observations.append(f"Possible hallucination: {msg}")
                        logger.warn(msg, request_id=req_id, component="eval")
                    else:
                        logger.info(msg, request_id=req_id, component="eval")

            logger.info(
                f"Request complete — total: {total_ms}ms, tokens: {result['input_tokens']}+{result['output_tokens']}, cost: ${result['estimated_cost']:.4f}",
                request_id=req_id, component="chat",
            )

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": context_docs,
                "groundedness": groundedness,
            })

            # Refresh suggestions for next round
            st.session_state.current_suggestions = pick_suggestions()

            # Log metrics
            metrics_store.log_request(
                query=prompt,
                model=result["model"],
                temperature=result["temperature"],
                top_k=top_k,
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                retrieval_ms=retrieval_ms,
                generation_ms=result["generation_ms"],
                total_ms=total_ms,
                success=True,
                failure_mode=failure_mode,
                error_message="; ".join(observations),
                estimated_cost=result["estimated_cost"] + (groundedness["estimated_cost"] if groundedness else 0),
            )

        except Exception as e:
            total_ms = int((time.time() - total_start) * 1000)
            error_msg = str(e)

            logger.error(
                f"{type(e).__name__}: {error_msg}",
                request_id=req_id, component="generation",
            )
            if failure_mode:
                logger.info(
                    f"Suggested action: see Incident Runbook for '{failure_mode}' resolution steps",
                    request_id=req_id, component="failure_sim",
                )

            st.error(f"**Error**: {error_msg}")

            if failure_mode:
                st.info(f"Active failure mode(s): **{failure_mode}**. Disable in Failure Lab to resolve.")

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {error_msg}",
            })

            metrics_store.log_request(
                query=prompt,
                model=model,
                temperature=temperature,
                top_k=top_k,
                total_ms=total_ms,
                success=False,
                failure_mode=failure_mode,
                error_message=error_msg,
            )
