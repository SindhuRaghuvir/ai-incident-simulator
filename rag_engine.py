import os
import time
import glob as globmod

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import chromadb
from openai import OpenAI

import config


def _get_openai_client():
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _get_chroma_client():
    os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=config.CHROMA_DB_DIR)


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
                # Split long paragraphs by sentence
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


def ingest_knowledge_base(chroma_client=None) -> int:
    """Load all markdown files from knowledge_base/ into ChromaDB. Returns doc count."""
    client = chroma_client or _get_chroma_client()

    # Delete and recreate to ensure fresh state
    try:
        client.delete_collection("knowledge_base")
    except Exception:
        pass
    collection = client.get_or_create_collection("knowledge_base")

    md_files = globmod.glob(os.path.join(config.KNOWLEDGE_BASE_DIR, "*.md"))
    all_chunks = []
    all_ids = []
    all_metadata = []

    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r") as f:
            content = f.read()
        chunks = _chunk_text(content)
        for i, chunk in enumerate(chunks):
            doc_id = f"{filename}_{i}"
            all_chunks.append(chunk)
            all_ids.append(doc_id)
            all_metadata.append({"source": filename, "chunk_index": i})

    if all_chunks:
        # ChromaDB has a batch limit, add in batches of 40
        batch_size = 40
        for start in range(0, len(all_chunks), batch_size):
            end = start + batch_size
            collection.add(
                documents=all_chunks[start:end],
                ids=all_ids[start:end],
                metadatas=all_metadata[start:end],
            )

    return len(all_chunks)


def ingest_text(text: str, source_name: str, chroma_client=None) -> int:
    """Add a single document to the existing knowledge base. Returns chunk count."""
    client = chroma_client or _get_chroma_client()
    collection = client.get_or_create_collection("knowledge_base")

    chunks = _chunk_text(text)
    if not chunks:
        return 0

    # Use source name + timestamp to avoid ID collisions
    import time as _t
    ts = int(_t.time())
    ids = [f"{source_name}_{ts}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source_name, "chunk_index": i} for i in range(len(chunks))]

    batch_size = 40
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.add(
            documents=chunks[start:end],
            ids=ids[start:end],
            metadatas=metadatas[start:end],
        )

    return len(chunks)


def retrieve(query: str, top_k: int = None, chroma_client=None) -> list[dict]:
    """Retrieve relevant chunks from ChromaDB."""
    top_k = top_k or config.TOP_K_RESULTS
    client = chroma_client or _get_chroma_client()

    try:
        collection = client.get_collection("knowledge_base")
    except Exception:
        return []

    results = collection.query(query_texts=[query], n_results=top_k)

    docs = []
    for i in range(len(results["documents"][0])):
        docs.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i] if results.get("distances") else 0,
        })
    return docs


def generate(
    query: str,
    context_docs: list[dict],
    model: str = None,
    temperature: float = None,
    openai_client=None,
) -> dict:
    """Call OpenAI with retrieved context. Returns response dict."""
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

    # Cost calculation
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
