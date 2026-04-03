import os
import time
import glob as globmod

import numpy as np
from openai import OpenAI

import config

# In-memory vector store — re-populated on each Streamlit startup
_store: list[dict] = []  # [{text, source, chunk_index, embedding}]


def _get_openai_client():
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _embed(texts: list[str], client=None) -> np.ndarray:
    client = client or _get_openai_client()
    response = client.embeddings.create(input=texts, model="text-embedding-3-small")
    return np.array([d.embedding for d in response.data], dtype=np.float32)


def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return m @ q


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


def ingest_knowledge_base() -> int:
    global _store
    _store = []
    client = _get_openai_client()

    md_files = globmod.glob(os.path.join(config.KNOWLEDGE_BASE_DIR, "*.md"))
    all_chunks = []
    all_meta = []

    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r") as f:
            content = f.read()
        chunks = _chunk_text(content)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_meta.append({"source": filename, "chunk_index": i})

    if not all_chunks:
        return 0

    batch_size = 100
    embeddings = []
    for start in range(0, len(all_chunks), batch_size):
        embs = _embed(all_chunks[start:start + batch_size], client)
        embeddings.append(embs)

    all_embeddings = np.vstack(embeddings)

    for i, (chunk, meta) in enumerate(zip(all_chunks, all_meta)):
        _store.append({
            "text": chunk,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "embedding": all_embeddings[i],
        })

    return len(_store)


def ingest_text(text: str, source_name: str) -> int:
    global _store
    client = _get_openai_client()
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    embeddings = _embed(chunks, client)
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        _store.append({
            "text": chunk,
            "source": source_name,
            "chunk_index": i,
            "embedding": emb,
        })
    return len(chunks)


def retrieve(query: str, top_k: int = None) -> list[dict]:
    top_k = top_k or config.TOP_K_RESULTS
    if not _store:
        return []

    client = _get_openai_client()
    query_emb = _embed([query], client)[0]

    matrix = np.array([item["embedding"] for item in _store])
    scores = _cosine_similarity(query_emb, matrix)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": _store[idx]["text"],
            "source": _store[idx]["source"],
            "distance": float(1 - scores[idx]),
        }
        for idx in top_indices
    ]


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

    context_text = "\n\n---\n\n".join(
        f"[Source: {doc['source']}]\n{doc['text']}" for doc in context_docs
    )

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\n---\n\nQuestion: {query}",
        },
    ]

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1024,
    )
    generation_ms = int((time.time() - start) * 1000)

    usage = response.usage
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens

    model_pricing = config.MODELS.get(model, config.MODELS[config.DEFAULT_MODEL])
    cost = (
        (input_tokens / 1000) * model_pricing["input_cost_per_1k"]
        + (output_tokens / 1000) * model_pricing["output_cost_per_1k"]
    )

    return {
        "answer": response.choices[0].message.content,
        "model": model,
        "temperature": temperature,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "generation_ms": generation_ms,
        "estimated_cost": cost,
    }
