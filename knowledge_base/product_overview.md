# Product Overview and Core Concepts

## What Stratify Labs Does

### What can I use Stratify Labs for?
Stratify Labs answers questions from your own content. The three most common uses:

- **Customer-facing chatbot or help widget** — answers customers from your public help articles, around the clock.
- **Internal knowledge assistant** — answers employees from wikis, runbooks, HR policies, and engineering specs, in Slack or your own tools.
- **Agent Assist in Zendesk** — shows support agents the top 3 relevant answers in the ticket sidebar, ready to insert into a reply.

### How does Stratify Labs work?
1. **You add documents to a collection**: upload files, send them through the API, or sync them from Zendesk or Confluence.
2. **Each document is split into chunks**, and each chunk is turned into an embedding (a vector that captures its meaning).
3. **Someone asks a question.** Retrieval compares the question with every chunk in the collection and picks the `top_k` most relevant ones (semantic search, or hybrid search on Professional and Enterprise).
4. **The answer model writes the answer only from those chunks** and returns it with its sources. You can choose the Fast model (default) or the Advanced model.
5. **If no chunk passes the confidence threshold**, the user gets your fallback message instead of a guess.

---

## Core Concepts

### What is a collection?
A collection is a named group of documents that is searched together, such as `customer-help`, `agent-internal`, or `engineering-runbooks`. You name the collection in each query; querying one specific collection is faster than searching across all of them.

- **Group collections by who searches them**, not by where the content came from. Mixing internal and customer-facing content in one collection risks internal notes appearing in customer answers.
- **Each collection has its own settings**: answer model, confidence threshold, search mode, chunk size, Answer Cache, and Custom Instructions, all under **Collections > Settings**.
- **Each collection is tied to one embedding model.** Switching models means re-indexing the whole collection.
- **Collection names are case-sensitive** in the API. A wrong case returns 404.
- **Limits by plan**: Free Trial 1 collection, Starter 5, Professional and Enterprise unlimited.

### What is a document?
A document is one item in a collection: a .txt, .md, .pdf (text-based), or .html file, one row of a CSV file, or a synced Zendesk article, ticket, or macro, or Confluence page. Every document has an ID. To update a document, upload the new version with the same ID; a new ID creates a duplicate. You can attach up to 20 metadata fields per document and filter searches by them.

A document moves through **Queued → Processing → Indexed**. It is searchable once it reaches Indexed, usually within 1–2 minutes.

### What are chunks, embeddings, and sources?
- **Chunk**: a searchable piece of a document. Chunk size is set per collection (300–500 characters suits FAQs; 800–1,200 suits how-to guides).
- **Embedding**: a list of numbers that represents a chunk's meaning, created by the collection's embedding model. Questions are embedded the same way, and the closest chunks are retrieved.
- **Sources**: the chunks used to write an answer, returned in the `sources` list with each document's ID, title, and relevance score. When an answer looks wrong, check the sources first.

### What are top_k and the confidence threshold?
- **top_k** is how many chunks are sent to the answer model. 3 to 5 is usually enough; more adds latency and cost.
- **Confidence threshold** is the minimum relevance score (0 to 1) a chunk needs to be used. Start at **0.70** and tune it in the Retrieval Debugger at **Collections > Debug**.

---

## Quickstart

### How do I make my first API query?
1. **Sign up** at dashboard.stratifylabs.io (Start Free Trial: 14 days, no credit card) and create your organization. Its slug becomes part of your API URL.
2. **Create a collection and add documents**: in **Collections**, open or create a collection and click "Upload Documents". Wait until the documents show **Indexed**.
3. **Create an API key** at **Settings > API Keys**. Store it in an environment variable or secrets manager, never in code.
4. **Send a query** to `POST https://api.stratifylabs.io/v1/{org}/query` (EU-West: `https://eu.api.stratifylabs.io/v1/{org}/query`):

```
curl https://api.stratifylabs.io/v1/{org}/query \
  -H "Authorization: Bearer ak_live_yourkey" \
  -H "Content-Type: application/json" \
  -d '{"collection": "support-articles", "question": "How do I reset my password?", "top_k": 5}'
```

5. **Read the response**: `answer`, `sources`, `usage`, and `request_id`. Keep the `X-Request-Id` header of any request you need help with.

The official SDKs (`pip install stratifylabs`, `npm install @stratifylabs/sdk`) handle authentication, retries, pagination, and streaming for you.

### Where do I go after my first query?
- **Rate limits and key types**: Getting Started
- **Errors, retries, streaming, and pagination**: API Reference
- **Improving wrong or made-up answers**: Answer Quality and Tuning
- **Slack, Zendesk, and Confluence**: Integrations
- **Latency targets and timeouts**: Performance and Latency
