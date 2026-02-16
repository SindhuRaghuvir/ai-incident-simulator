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
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3
DEFAULT_TEMPERATURE = 0.3

# Paths
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
METRICS_DB_PATH = os.path.join(DATA_DIR, "metrics.db")

SYSTEM_PROMPT = """You are a helpful enterprise support assistant for Stratify Labs, a cloud platform company.
Answer questions using ONLY the provided context. If the context doesn't contain enough information, say so.
Be concise and professional."""
