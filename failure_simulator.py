"""
Failure injection engine.

Sits between the UI and RAG engine. Checks which failure modes are active
in session state, then modifies inputs or raises exceptions accordingly.
The RAG engine stays clean — all fault logic lives here.
"""

import time
import random
import httpx
from openai import RateLimitError, APIStatusError


# -- Failure mode definitions --

FAILURE_MODES = {
    "rate_limit": {
        "label": "Rate Limit (429)",
        "description": "Simulates hitting OpenAI's rate limit. The API returns HTTP 429.",
        "cause": "Too many requests in a short window, or token-per-minute quota exceeded.",
        "fix": "Implement exponential backoff with jitter. Use a request queue. Monitor usage against plan limits.",
    },
    "timeout": {
        "label": "Timeout",
        "description": "Simulates a slow API response that exceeds the client timeout.",
        "cause": "Network congestion, overloaded API servers, or extremely long prompts.",
        "fix": "Set reasonable timeouts. Use circuit breaker pattern. Provide fallback responses for degraded mode.",
    },
    "bad_context": {
        "label": "Stale / Bad Context",
        "description": "Corrupts the retrieved context so the LLM gets irrelevant information.",
        "cause": "Stale embeddings, poor chunking strategy, or embedding model drift after retraining.",
        "fix": "Monitor retrieval relevance scores. Set minimum similarity thresholds. Re-index periodically.",
    },
    "high_temperature": {
        "label": "High Temperature",
        "description": "Forces temperature to 2.0, making output random and incoherent.",
        "cause": "Misconfiguration, unvalidated user input passed to API parameters.",
        "fix": "Validate all API parameters server-side. Clamp temperature to acceptable range (0.0-1.0). Use config defaults.",
    },
    "context_window": {
        "label": "Context Window Exceeded",
        "description": "Simulates sending a prompt that exceeds the model's maximum context length.",
        "cause": "Prompt + retrieved context exceeds the model's token limit (e.g. 128k for gpt-4o-mini).",
        "fix": "Truncate context before sending. Reduce top-k. Implement token counting before API call.",
    },
}


def get_active_failures(session_state) -> list[str]:
    """Return list of currently active failure mode keys."""
    return [
        key for key in FAILURE_MODES
        if session_state.get(f"failure_{key}", False)
    ]


def pre_retrieval(query: str, session_state) -> str:
    """Hook called before retrieval. May modify the query."""
    active = get_active_failures(session_state)

    if "bad_context" in active:
        # Corrupt the query to get irrelevant results
        garbage_words = ["xylophone", "quantum", "banana", "frostbite", "parliament"]
        return " ".join(random.sample(garbage_words, 3))

    return query


def pre_generation(context_docs: list[dict], params: dict, session_state) -> tuple[list[dict], dict]:
    """
    Hook called before LLM generation.
    May modify context_docs and/or params (model, temperature).
    May raise exceptions to simulate API failures.
    """
    active = get_active_failures(session_state)

    if "rate_limit" in active:
        # Raise a real OpenAI RateLimitError
        mock_response = httpx.Response(
            status_code=429,
            headers={"retry-after": "30"},
            json={
                "error": {
                    "message": "Rate limit reached for gpt-4o-mini. Limit: 3 RPM. Please try again in 20s.",
                    "type": "tokens",
                    "code": "rate_limit_exceeded",
                }
            },
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
        )
        raise RateLimitError(
            message="Rate limit reached (simulated)",
            response=mock_response,
            body=mock_response.json(),
        )

    if "timeout" in active:
        # Simulate a slow response
        mock_response = httpx.Response(
            status_code=503,
            json={
                "error": {
                    "message": "Service temporarily unavailable (simulated timeout)",
                    "type": "server_error",
                    "code": "service_unavailable",
                }
            },
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
        )
        time.sleep(3)  # Brief delay to feel real without actually waiting forever
        raise APIStatusError(
            message="Request timed out (simulated)",
            response=mock_response,
            body=mock_response.json(),
        )

    if "bad_context" in active:
        # Replace context with nonsense
        context_docs = [
            {
                "text": "The annual migration of arctic terns covers roughly 44,000 miles. "
                        "Bananas are technically berries but strawberries are not. "
                        "The deepest point in the ocean is the Mariana Trench at 36,000 feet.",
                "source": "corrupted_data.md",
                "distance": 0.99,
            }
        ]

    if "high_temperature" in active:
        params["temperature"] = 2.0

    if "context_window" in active:
        mock_response = httpx.Response(
            status_code=400,
            json={
                "error": {
                    "message": "This model's maximum context length is 128000 tokens. Your request has 132456 tokens.",
                    "type": "invalid_request_error",
                    "code": "context_length_exceeded",
                }
            },
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
        )
        raise APIStatusError(
            message="Context length exceeded (simulated)",
            response=mock_response,
            body=mock_response.json(),
        )

    return context_docs, params
