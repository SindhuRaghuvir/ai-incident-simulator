# Troubleshooting Common Errors

## HTTP Error Codes

### I'm getting a 429 error — what does it mean and what should I do?
A **429 Too Many Requests** error means you've exceeded your plan's rate limit — either the requests-per-minute or requests-per-day limit.

**What to do:**
1. **Check the `Retry-After` header** — the API response includes a number (in seconds) telling you how long to wait before retrying.
2. **Check your usage** — go to Settings > Billing > Usage to see how much of your daily limit you've used.
3. **Use test keys for development** — API calls made with test keys (`ak_test_`) don't count toward your limits.
4. **Spread out requests** — if you're making many calls in a short window, add small delays between them.
5. **Upgrade your plan** — if you're regularly hitting limits, you may need a higher tier. Go to Settings > Billing to compare plans.

Rate limits by plan:

| Plan | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Free Trial | 10 | 1,000 |
| Starter | 60 | 50,000 |
| Professional | 300 | 500,000 |
| Enterprise | Custom | Custom |

### I'm getting a 401 Unauthorized error
A **401** means your API key is missing, invalid, or has been revoked.

**What to check:**
1. **Is the key in the request?** Make sure you're passing the key in the `Authorization` header as `Bearer ak_live_yourkey`.
2. **Is the key still active?** Go to Settings > API Keys to check. The key may have been rotated or deleted.
3. **Was the key found in a public repo?** If we detect your key in a public GitHub repository, we automatically revoke it and send an email to the account owner. Check your inbox.
4. **Right key for the right environment?** Test keys (`ak_test_`) only work against the sandbox. Live keys (`ak_live_`) are required for production.

If you've verified all of the above and still get 401s, generate a new key from Settings > API Keys and test with that.

### I'm getting a 403 Forbidden error
A **403** means your API key is valid but doesn't have permission to perform the action you're trying to do.

**Common causes:**
- You're using a read-only key (`ak_readonly_`) to make a write request
- Your role doesn't have access to the collection or resource you're querying
- IP allowlisting is enabled and your IP isn't on the approved list (Settings > Security > IP Allowlist)

Check the key type and your account role. If you think your permissions are incorrect, ask your org's Owner or Admin to review your settings.

### I'm getting a 404 Not Found error
A **404** usually means the collection or resource you're looking for doesn't exist or can't be found.

**What to check:**
1. **Collection name** — collection names are case-sensitive. Make sure you're using the exact name as it appears in your dashboard.
2. **Organization name** — if your API endpoint includes your org name, verify it matches exactly.
3. **Empty collection** — if you created a collection but haven't ingested any documents yet, some queries will return a 404. Ingest at least one document first.
4. **Typo in the endpoint** — double-check the URL or collection name in your request.

### I'm getting 500 or 503 errors
A **500 Internal Server Error** or **503 Service Unavailable** means something went wrong on our end.

**What to do:**
1. **Check our status page** — visit status.stratifylabs.io to see if there's an active incident or scheduled maintenance.
2. **Try again in a few minutes** — transient errors often resolve quickly.
3. **If it persists** — contact support@stratifylabs.io with the timestamp of your requests and any request IDs from the error response. We'll investigate.

We aim to resolve incidents quickly and post updates on our status page every 2 hours during active incidents.

---

## Performance Issues

### My API responses are slow — what could be causing this?
Slow responses can have a few causes:

1. **Large knowledge base** — searching across many documents takes longer. Make sure you're querying a specific collection rather than searching everything.
2. **First query after ingestion** — the first query after adding new documents may take 2–5 seconds while embeddings are generated. This is normal; subsequent queries will be faster.
3. **High concurrency** — if you're approaching your concurrent connection limit, requests may queue. Check your plan's concurrent connection limit and consider upgrading if needed.
4. **Network latency** — if your application is in a different region from your Stratify Labs data region, there will be added latency. Enterprise plans support multi-region deployment.
5. **Large result sets** — requesting a high `top_k` value (many results per query) increases processing time. Start with 5 and increase only if needed.

If you're consistently seeing responses over 2 seconds and none of the above applies, contact support@stratifylabs.io with examples.

---

## Knowledge Base and Search Issues

### My embeddings aren't updating after I ingest new documents
After ingestion, embeddings are generated in the background. This usually takes 1–2 minutes for normal-sized documents. Large documents or large batches can take longer.

**What to check:**
1. **Wait a bit longer** — give it 5 minutes, then try your query again.
2. **Verify the document ingested** — check your collection in the dashboard to confirm the document appears. If it doesn't show up, the ingestion may have failed.
3. **Check for ingestion errors** — go to your collection and look for any error indicators on recently uploaded documents.

If a document shows as ingested but still isn't returning in search results after 10 minutes, contact support@stratifylabs.io.

### My query is returning wrong or irrelevant answers
If the answers you're getting back don't match what you asked, here are the most common reasons:

1. **Your knowledge base doesn't contain relevant content** — the system can only return what's in your documents. If the right answer isn't in your KB, it won't appear. Check whether the relevant content has been ingested.
2. **Query is too vague** — more specific queries return more relevant results. Try rephrasing your question to be more precise.
3. **Confidence threshold is too low** — if your app is set to return low-confidence results, you'll see less relevant content. Raise the confidence threshold in your collection settings.
4. **Chunk size mismatch** — if documents were chunked in a way that splits key context, results may seem incomplete. Check your collection's chunking settings.
5. **Wrong collection** — make sure you're querying the collection that contains the relevant documents.

If you've checked all of the above and are still seeing consistently poor results, contact support@stratifylabs.io with example queries and expected vs. actual answers. We can help tune the configuration.

### Why does the AI say "I don't know" or give no answer?
This means no content in your knowledge base met the confidence threshold for your query. It's actually the correct behavior — the system is designed not to make up answers.

To improve coverage:
- Add more relevant documents to your knowledge base
- Make sure documents are properly formatted and not truncated
- Try rewriting the query to match the language used in your documents

---

## Need More Help?

If an error isn't covered here, contact **support@stratifylabs.io** and include:
- The error code and full error message
- The timestamp(s) of the failing requests
- Your organization name and the collection you were querying
- What you were trying to do

The more detail you provide, the faster we can resolve it.
