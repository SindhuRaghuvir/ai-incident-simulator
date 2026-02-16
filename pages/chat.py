import time
import streamlit as st

import config
import rag_engine
import metrics_store
import failure_simulator
import logger

# -- API Key input --

api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=config.OPENAI_API_KEY, help="Get one at platform.openai.com/api-keys")
if api_key:
    config.OPENAI_API_KEY = api_key

# -- Sidebar controls --

st.sidebar.header("Settings")

model = st.sidebar.selectbox("Model", list(config.MODELS.keys()), index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, config.DEFAULT_TEMPERATURE, 0.1)
top_k = st.sidebar.slider("Retrieved chunks (top-k)", 1, 10, config.TOP_K_RESULTS)

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
            chunk_count = rag_engine.ingest_text(content, uf.name)
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

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.caption(f"{src['source']} (distance: {src['distance']:.3f})")
                    st.text(src["text"][:200] + "...")

# Chat input
if prompt := st.chat_input("Ask about Stratify Labs..."):
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
            context_docs = rag_engine.retrieve(retrieval_query, top_k=top_k)
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
            gen_params = {"model": model, "temperature": temperature}
            context_docs, gen_params = failure_simulator.pre_generation(
                context_docs, gen_params, st.session_state
            )

            logger.info(
                f"Sending to OpenAI {gen_params['model']} (temperature={gen_params['temperature']})",
                request_id=req_id, component="generation",
            )

            result = rag_engine.generate(
                query=prompt,
                context_docs=context_docs,
                model=gen_params["model"],
                temperature=gen_params["temperature"],
            )

            total_ms = int((time.time() - total_start) * 1000)

            logger.info(
                f"Response received — {result['output_tokens']} tokens in {result['generation_ms']}ms",
                request_id=req_id, component="generation",
            )
            logger.info(
                f"Request complete — total: {total_ms}ms, tokens: {result['input_tokens']}+{result['output_tokens']}, cost: ${result['estimated_cost']:.4f}",
                request_id=req_id, component="chat",
            )

            # Display answer
            st.markdown(result["answer"])

            # Show sources
            with st.expander("Sources & Metrics"):
                for doc in context_docs:
                    st.caption(f"{doc['source']} (distance: {doc['distance']:.3f})")
                cols = st.columns(4)
                cols[0].metric("Retrieval", f"{retrieval_ms}ms")
                cols[1].metric("Generation", f"{result['generation_ms']}ms")
                cols[2].metric("Tokens", f"{result['input_tokens']}+{result['output_tokens']}")
                cols[3].metric("Cost", f"${result['estimated_cost']:.4f}")

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": context_docs,
            })

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
                estimated_cost=result["estimated_cost"],
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
