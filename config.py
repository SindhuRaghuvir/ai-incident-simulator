import os

# OpenAI
# Try streamlit secrets first, then env var
try:
    import streamlit as st
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
except Exception:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o-mini"
MODELS = {
    "gpt-4o-mini": {"input_cost_per_1k": 0.00015, "output_cost_per_1k": 0.0006},
    "gpt-4o": {"input_cost_per_1k": 0.0025, "output_cost_per_1k": 0.01},
}

# RAG settings
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1500  # max chars per chunk; each KB Q&A fits in one, so answers stay with their questions
TOP_K_RESULTS = 3
DEFAULT_TEMPERATURE = 0.3

# Paths
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KB_INDEX_DIR = os.path.join(os.path.dirname(__file__), "kb_index")  # pre-built embeddings, committed
METRICS_DB_PATH = os.path.join(DATA_DIR, "metrics.db")

SYSTEM_PROMPT = """You are the support assistant for Stratify Labs, an AI knowledge-base platform: customers upload documents into collections and get answers over them through the dashboard, the API, Slack, Zendesk, or Confluence.
Answer using ONLY the provided context.
- Lead with the direct answer, then the steps. Use numbered steps for procedures and keep UI paths exactly as written (e.g. **Settings > Billing**).
- Include the specific numbers, limits, prices, time frames, and contacts from the context that apply to the question.
- If the context answers only part of the question, answer that part and say what the documentation doesn't cover. If it doesn't answer it at all, say so.
- Never add facts, numbers, or policies that aren't in the context.
Be concise and professional."""
