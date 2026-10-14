# API Reference Guide

## Basics

### What is the base URL for the Stratify Labs API?
All API requests go to:

`https://api.stratifylabs.io/v1/{org}/`

Replace `{org}` with your organization's slug, which you chose during signup. You can find it at **Settings > Organization**. EU-West customers use `https://eu.api.stratifylabs.io/v1/{org}/` instead — sending EU data to the US endpoint returns a **421 Misdirected Request** error.

### How do I authenticate API requests?
Pass your API key in the `Authorization` header as a Bearer token:

```
Authorization: Bearer ak_live_yourkey
```

Never send the key as a query parameter — keys in URLs end up in proxy and server logs. Requests without a valid key return **401 Unauthorized**.

### Which API version should I use?
The current version is **v1**. We never make breaking changes inside a version. New optional fields and endpoints can be added at any time, so make sure your client ignores fields it doesn't recognize. When v2 ships, v1 will be supported for at least **12 months** after the v2 release date.

---

## Core Endpoints

### What are the main endpoints?

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/query` | Ask a question and get an AI answer with sources |
| POST | `/search` | Return matching chunks only — no AI-generated answer |
| POST | `/collections/{name}/documents` | Upload or update a document |
| GET | `/collections/{name}/documents/{id}` | Get a document and its ingestion status |
| DELETE | `/collections/{name}/documents/{id}` | Delete a document and its embeddings |
| GET | `/collections` | List collections |
| GET | `/usage` | Current usage against your plan limits |

### How do I send a query?
Send a POST to `/query` with a JSON body:

```json
{
  "collection": "support-articles",
  "question": "How do I reset my password?",
  "top_k": 5,
  "stream": false
}
```

The response includes the `answer`, a `sources` list (document ID, title, and relevance score for each chunk used), `usage` (tokens consumed), and a `request_id`.

### What's the difference between /query and /search?
- **/query** retrieves the most relevant chunks and then generates a natural-language answer from them. It counts as 1 API request plus generation tokens.
- **/search** only returns the matching chunks and their scores. It is faster (typically under 300ms) and cheaper, and is the right choice if you want to build your own answer UI or run your own LLM.

### Can I stream answers?
Yes. Set `"stream": true` in your `/query` request. The API returns Server-Sent Events (SSE): one `token` event per piece of text, then a final `done` event containing sources and usage. Streaming doesn't make the full answer finish sooner, but users see the first words in under a second, which makes the experience feel much faster.

---

## Pagination, Request IDs and Idempotency

### How does pagination work?
List endpoints return up to 50 items by default (maximum 200, set with `limit`). If more results exist, the response includes a `next_cursor` value. Pass it as `cursor` on your next request. Cursors expire after 24 hours.

### What is a request ID and why does support ask for it?
Every response includes an `X-Request-Id` header (for example, `req_8f2a1c9e`). It uniquely identifies that request in our logs. When you contact support about a failed or slow request, include the request ID and timestamp — it lets us find the exact request in seconds instead of searching by time window.

### How do I avoid creating duplicate documents when I retry?
Send an `Idempotency-Key` header (any unique string, such as a UUID) with POST requests. If you retry with the same key within 24 hours, we return the original response instead of processing the request again. This is especially important for document uploads in retry loops.

---

## Errors

### What does an error response look like?
All errors use the same JSON format:

```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded",
    "message": "Rate limit of 60 requests/minute exceeded. Retry after 12 seconds.",
    "request_id": "req_8f2a1c9e"
  }
}
```

### Which errors should my code retry?

| Status | Retry? | Notes |
|--------|--------|-------|
| 400 Bad Request | No | Fix the request body first |
| 401 / 403 | No | Key or permission problem |
| 404 Not Found | No | Check the collection name and document ID |
| 409 Conflict | No | Document is still processing; wait, then send the update |
| 413 Payload Too Large | No | File exceeds your plan's size limit |
| 429 Too Many Requests | Yes | Wait for the `Retry-After` seconds |
| 500 / 502 / 503 / 504 | Yes | Use exponential backoff with jitter |

For retryable errors, wait 1s, 2s, 4s, 8s (plus a random 0–1s of jitter) and stop after 5 attempts. Retrying immediately in a tight loop makes rate limiting worse and can extend an outage for everyone on your account.

---

## SDKs and Timeouts

### Are there official SDKs?
Yes:
- **Python**: `pip install stratifylabs`
- **Node.js / TypeScript**: `npm install @stratifylabs/sdk`

Both SDKs handle authentication, retries with backoff, pagination, and streaming for you. Community libraries exist for Go and Ruby but are not officially supported.

### What timeout should I set on my client?
We recommend:
- **/search**: 10 seconds
- **/query** (non-streaming): 30 seconds
- **/query** (streaming): 30 seconds to the first token, then no overall limit
- **Document uploads**: 60 seconds

The server-side limit for a single request is 60 seconds. Requests that run longer are cancelled and return **504 Gateway Timeout**.
