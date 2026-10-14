from __future__ import annotations

import os
import json
import time
import hashlib
import threading
import glob as globmod
from functools import lru_cache

import numpy as np
from openai import OpenAI

import config

# Shared, read-only index of the built-in knowledge base. Loaded once per
# server process (not once per visitor) from the pre-built files in kb_index/,
# so a cold start makes zero OpenAI calls. Uploaded docs live in each
# visitor's session and are passed to retrieve() via extra_docs.
_index: dict | None = None  # {texts, sources, matrix (L2-normalized), fingerprint}
_index_lock = threading.Lock()
_client: OpenAI | None = None

INDEX_META_PATH = os.path.join(config.KB_INDEX_DIR, "chunks.json")
INDEX_EMB_PATH = os.path.join(config.KB_INDEX_DIR, "embeddings.npy")


def _get_openai_client():
    # One client per process keeps the HTTPS connection pool warm between requests
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.OPENAI_API_KEY, timeout=30, max_retries=2)
    return _client


def _embed(texts: list[str], client=None) -> np.ndarray:
    client = client or _get_openai_client()
    response = client.embeddings.create(input=texts, model=config.EMBEDDING_MODEL)
    return np.array([d.embedding for d in response.data], dtype=np.float32)


def _normalize(matrix: np.ndarray) -> np.ndarray:
    return matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)


@lru_cache(maxsize=512)
def _embed_query(query: str) -> np.ndarray:
    # Repeat questions (e.g. the suggestion buttons) skip the embedding call entirely
    vec = _embed([query])[0]
    return vec / (np.linalg.norm(vec) + 1e-10)


def _chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(para) > chunk_size:
                words = para.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= chunk_size:
                        current_chunk = current_chunk + " " + word if current_chunk else word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = word
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _read_knowledge_base() -> tuple[list[str], list[str], str]:
    """Chunk every KB file. Returns (texts, sources, fingerprint of the KB + settings)."""
    texts, sources = [], []
    digest = hashlib.sha256(
        f"{config.EMBEDDING_MODEL}|{config.CHUNK_SIZE}|{config.CHUNK_OVERLAP}".encode()
    )
    for filepath in sorted(globmod.glob(os.path.join(config.KNOWLEDGE_BASE_DIR, "*.md"))):
        filename = os.path.basename(filepath)
        with open(filepath, "r") as f:
            content = f.read()
        digest.update(filename.encode())
        digest.update(content.encode())
        for chunk in _chunk_text(content):
            texts.append(chunk)
            sources.append(filename)
    return texts, sources, digest.hexdigest()


def build_index() -> int:
    """Embed the knowledge base and write kb_index/. Run after editing any KB doc:
    python3 -c "import rag_engine; print(rag_engine.build_index())"
    """
    texts, sources, fingerprint = _read_knowledge_base()
    client = _get_openai_client()
    batch_size = 100
    embeddings = np.vstack([
        _embed(texts[start:start + batch_size], client)
        for start in range(0, len(texts), batch_size)
    ])
    os.makedirs(config.KB_INDEX_DIR, exist_ok=True)
    np.save(INDEX_EMB_PATH, embeddings)
    with open(INDEX_META_PATH, "w") as f:
        json.dump({
            "fingerprint": fingerprint,
            "embedding_model": config.EMBEDDING_MODEL,
            "chunks": [{"text": t, "source": s} for t, s in zip(texts, sources)],
        }, f, indent=1)
    return len(texts)


def _load_index() -> dict:
    texts, sources, fingerprint = _read_knowledge_base()
    try:
        with open(INDEX_META_PATH) as f:
            meta = json.load(f)
        stale = meta["fingerprint"] != fingerprint
    except (OSError, ValueError, KeyError):
        stale = True
    if stale:
        # KB docs changed since the index was built — rebuild it (one-time cost)
        build_index()
    matrix = np.load(INDEX_EMB_PATH)
    return {
        "texts": texts,
        "sources": sources,
        "matrix": _normalize(matrix),
        "fingerprint": fingerprint,
    }


def ingest_knowledge_base() -> int:
    """Load the shared index (once per process). Returns the number of chunks."""
    global _index
    if _index is None:
        with _index_lock:
            if _index is None:
                _index = _load_index()
    return len(_index["texts"])


def ingest_text(text: str, source_name: str) -> list[dict]:
    """Chunk and embed an uploaded doc. Returns the chunks for the caller to keep
    in session state — uploads are private to the visitor who added them."""
    chunks = _chunk_text(text)
    if not chunks:
        return []
    embeddings = _normalize(_embed(chunks))
    return [
        {"text": chunk, "source": source_name, "chunk_index": i, "embedding": emb}
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]


def retrieve(query: str, top_k: int = None, extra_docs: list[dict] = None) -> list[dict]:
    top_k = top_k or config.TOP_K_RESULTS
    ingest_knowledge_base()
    extra_docs = extra_docs or []

    texts = _index["texts"] + [d["text"] for d in extra_docs]
    sources = _index["sources"] + [d["source"] for d in extra_docs]
    if not texts:
        return []

    matrix = _index["matrix"]
    if extra_docs:
        matrix = np.vstack([matrix, np.array([d["embedding"] for d in extra_docs])])

    scores = matrix @ _embed_query(query)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": texts[idx],
            "source": sources[idx],
            "distance": float(1 - scores[idx]),
        }
        for idx in top_indices
    ]


def _build_messages(query: str, context_docs: list[dict], system_prompt: str = None) -> list[dict]:
    context_text = "\n\n---\n\n".join(
        f"[Source: {doc['source']}]\n{doc['text']}" for doc in context_docs
    )
    return [
        {"role": "system", "content": system_prompt or config.SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\n---\n\nQuestion: {query}",
        },
    ]


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    model_pricing = config.MODELS.get(model, config.MODELS[config.DEFAULT_MODEL])
    return (
        (input_tokens / 1000) * model_pricing["input_cost_per_1k"]
        + (output_tokens / 1000) * model_pricing["output_cost_per_1k"]
    )


def generate(
    query: str,
    context_docs: list[dict],
    model: str = None,
    temperature: float = None,
    openai_client=None,
) -> dict:
    model = model or config.DEFAULT_MODEL
    temperature = temperature if temperature is not None else config.DEFAULT_TEMPERATURE
    client = openai_client or _get_openai_client()

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=_build_messages(query, context_docs),
        temperature=temperature,
        max_tokens=1024,
    )
    generation_ms = int((time.time() - start) * 1000)

    usage = response.usage
    return {
        "answer": response.choices[0].message.content,
        "model": model,
        "temperature": temperature,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "generation_ms": generation_ms,
        "estimated_cost": _estimate_cost(model, usage.prompt_tokens, usage.completion_tokens),
    }


def generate_stream(
    query: str,
    context_docs: list[dict],
    model: str = None,
    temperature: float = None,
    max_tokens: int = 1024,
    system_prompt: str = None,
    openai_client=None,
):
    """Streaming version of generate(). Returns (token_iterator, result).
    Pass the iterator to st.write_stream; `result` gets the same fields as
    generate() (plus first_token_ms) once the iterator is exhausted."""
    model = model or config.DEFAULT_MODEL
    temperature = temperature if temperature is not None else config.DEFAULT_TEMPERATURE
    client = openai_client or _get_openai_client()
    result = {"model": model, "temperature": temperature}

    def tokens():
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=_build_messages(query, context_docs, system_prompt),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            stream_options={"include_usage": True},
        )
        parts, usage, finish_reason = [], None, None
        for chunk in response:
            if chunk.usage:
                usage = chunk.usage
            if chunk.choices and chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason
            if chunk.choices and chunk.choices[0].delta.content:
                if "first_token_ms" not in result:
                    result["first_token_ms"] = int((time.time() - start) * 1000)
                parts.append(chunk.choices[0].delta.content)
                yield parts[-1]

        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        result.update({
            "answer": "".join(parts),
            "finish_reason": finish_reason,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "generation_ms": int((time.time() - start) * 1000),
            "estimated_cost": _estimate_cost(model, input_tokens, output_tokens),
        })

    return tokens(), result


GROUNDEDNESS_PROMPT = """You are a strict fact-checker for a RAG system.
Break the ANSWER into its atomic factual claims (at most 8; skip greetings and filler).
For each claim, decide using ONLY the CONTEXT:
- "supported": the context states it
- "unsupported": the context doesn't mention it (invented or outside knowledge)
- "contradicted": the context says something different
Return JSON: {"claims": [{"claim": "...", "verdict": "supported|unsupported|contradicted", "evidence": "short quote from the context, or empty"}]}
Statements about the context itself ("the context doesn't say", "I don't have that information") are NOT claims.
If the answer makes no factual claims (e.g. it says it doesn't know), return {"claims": []}."""


def check_groundedness(answer: str, context_docs: list[dict], openai_client=None) -> dict:
    """LLM-as-judge hallucination check: what share of the answer's claims
    are backed by the context that was actually sent to the model?"""
    client = openai_client or _get_openai_client()
    context_text = "\n\n---\n\n".join(
        f"[Source: {doc['source']}]\n{doc['text']}" for doc in context_docs
    ) or "(no context)"

    start = time.time()
    response = client.chat.completions.create(
        model=config.DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": GROUNDEDNESS_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context_text}\n\nANSWER:\n{answer}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=800,
    )
    check_ms = int((time.time() - start) * 1000)

    try:
        claims = json.loads(response.choices[0].message.content).get("claims", [])
    except (ValueError, AttributeError):
        claims = []
    supported = sum(1 for c in claims if c.get("verdict") == "supported")
    usage = response.usage
    return {
        "claims": claims,
        "supported": supported,
        "total": len(claims),
        "score": supported / len(claims) if claims else None,
        "check_ms": check_ms,
        "estimated_cost": _estimate_cost(config.DEFAULT_MODEL, usage.prompt_tokens, usage.completion_tokens),
    }
