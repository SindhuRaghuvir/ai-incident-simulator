# Performance, Latency and Reliability

## What Normal Looks Like

### How fast should Stratify Labs respond?
Typical latency for a collection under 100,000 documents, measured inside the same region:

| Endpoint | p50 (median) | p95 |
|----------|--------------|-----|
| `/search` | 150 ms | 400 ms |
| `/query` (first token, streaming) | 600 ms | 1.2 s |
| `/query` (full answer, non-streaming) | 2.0 s | 4.5 s |
| Document upload accepted | 200 ms | 500 ms |

Most of a `/query` request's time is spent generating the answer, not searching. That's why streaming makes the biggest difference to how fast your app feels.

### What do p50 and p95 mean?
- **p50 (median)**: half of requests are faster than this.
- **p95**: 95% of requests are faster than this; 1 in 20 is slower.

Averages hide slow outliers, so we report percentiles. If your p95 is much higher than the numbers above, some of your users are having a slow experience even if the average looks fine.

### How can I see where the time is going?
Every `/query` response includes timing headers:
- `X-Stratify-Retrieval-Ms` — time spent embedding the query and searching
- `X-Stratify-Generation-Ms` — time spent generating the answer
- `X-Stratify-Queue-Ms` — time the request waited because you were at your concurrency limit

If `Queue-Ms` is high, you're hitting your concurrent connection limit. If `Retrieval-Ms` is high, look at collection size and `top_k`. If `Generation-Ms` is high, look at answer length and model choice.

---

## Making It Faster

### What are the quickest ways to reduce latency?
1. **Stream answers** (`"stream": true`) so users see text in under a second.
2. **Use /search instead of /query** when you don't need an AI-written answer.
3. **Query a specific collection** rather than searching across all of them.
4. **Keep top_k small** — 3 to 5 chunks is usually enough. Each extra chunk adds input tokens and generation time.
5. **Use the Fast answer model** unless you need Advanced reasoning.
6. **Reuse HTTP connections** — create one API client and reuse it. Opening a new TLS connection for every request adds 100–300 ms.
7. **Deploy close to your data region** — calling US-East from Asia adds 150–250 ms per round trip.

### Should I cache answers?
For high-traffic, repeated questions (like "How do I reset my password?"), yes. Cache responses for a short window (5–60 minutes) keyed on the normalized question and collection. Clear the cache when you update the underlying documents, or you'll serve stale answers. Professional and Enterprise plans can enable **Answer Cache** at **Collections > Settings > Performance**, which does this automatically and invalidates on document updates.

### Why is the first request after a quiet period slower?
Collections that haven't been queried for over 24 hours are moved to warm storage. The first query after that may take 1–3 extra seconds while the index is loaded into memory. Enterprise customers can enable **Always Warm** to keep indexes in memory permanently.

---

## Timeouts and Retries

### My requests are timing out — what should I check?
1. **Your client timeout** — make sure it's at least 30 seconds for non-streaming `/query`. A 5-second timeout will cut off normal long answers.
2. **Very large prompts** — a high `top_k` combined with large chunks can push requests near the model's context limit, which slows generation sharply.
3. **status.stratifylabs.io** — check for an active incident.
4. **Your network** — corporate proxies sometimes buffer or terminate streaming responses. Test from outside the proxy.

If timeouts continue, send the request IDs to support@stratifylabs.io.

### How should I retry failed requests?
Use **exponential backoff with jitter**: wait 1s, then 2s, 4s, 8s, adding a random 0–1 second each time, and give up after 5 attempts. Only retry 429 and 5xx errors. Always honor the `Retry-After` header on 429 responses.

Avoid retrying without delays — when many clients retry at the same moment, they create a "thundering herd" that can turn a brief blip into a longer outage.

### What is a circuit breaker and do I need one?
A circuit breaker stops sending requests to a service after repeated failures (for example, 5 failures in 30 seconds), returns a fallback immediately, and then tests again after a cool-down period. It protects your app from hanging on a struggling dependency. For customer-facing chat, a good fallback is a friendly "Search is temporarily unavailable — here's how to contact support" message.

---

## Concurrency and Load

### What happens if I go over my concurrent connection limit?
Requests over the limit are queued for up to 10 seconds (shown in `X-Stratify-Queue-Ms`). If a slot doesn't open in that time, the request fails with **429 Too Many Requests** and code `concurrency_limit_exceeded`. Concurrent connection limits are 2 (Free Trial), 10 (Starter), 50 (Professional), and custom for Enterprise.

### We're planning a launch — how do we prepare for a traffic spike?
1. Load-test against a **test key** (`ak_test_`) in the sandbox first — test traffic doesn't count toward your limits.
2. Estimate your peak requests per minute and confirm it's within your plan's limit with headroom.
3. Enable answer caching for your most common questions.
4. Enterprise customers: tell your TAM at least **5 business days** before the launch so we can pre-scale capacity and keep an engineer on standby.
