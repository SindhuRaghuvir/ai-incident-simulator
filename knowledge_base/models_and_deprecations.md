# AI Models, Upgrades and Deprecations

## Models We Use

### Which AI models power Stratify Labs?
Stratify Labs uses two kinds of models:

- **Answer models** generate the natural-language answer from your retrieved content. You can choose between **Fast** (lowest latency and cost, the default) and **Advanced** (better reasoning on complex, multi-step questions, roughly 3x the generation cost).
- **Embedding models** turn your documents and queries into vectors for semantic search. Every collection is tied to one embedding model version, shown at **Collections > (your collection) > Settings > Embedding Model**.

Enterprise customers can bring their own model (BYOM) — see the FAQ for details.

### How do I change the answer model?
Set it per collection at **Collections > Settings > Answer Model**, or per request by passing `"model": "advanced"` in the `/query` body. A per-request setting overrides the collection default. Changing the answer model does not require re-indexing.

---

## Deprecation Policy

### How much notice do you give before retiring a model?
- **Answer models**: at least **90 days** notice before retirement.
- **Embedding models**: at least **6 months** notice, because switching requires re-indexing your content.

Notices go to the account Owner and all Admins by email, appear as a banner in the dashboard, and are listed at status.stratifylabs.io/deprecations. Enterprise customers are also contacted directly by their dedicated support engineer.

### What happens on the retirement date if I haven't migrated?
For answer models, requests that name the retired model are automatically routed to its listed replacement, and the response includes a `X-Stratify-Model-Redirect` header so you can detect it. You will not get errors, but answers may read differently.

For embedding models, collections that haven't been re-indexed by the retirement date are switched to **read-only**: search keeps working on existing content, but new uploads fail with a **409 Conflict** error until you re-index.

### What is model pinning?
Pinning locks a collection to a specific model version (for example, `fast-2026-03`) instead of the moving alias (`fast`). The alias is upgraded automatically when we release improvements; a pinned version is not. Pin a version if you have automated tests or compliance review that depend on consistent wording. Pinned versions are still subject to the deprecation policy above.

---

## Migrating

### How do I re-index a collection onto a new embedding model?
1. Go to **Collections > (your collection) > Settings > Embedding Model**
2. Select the new model and click **Start Re-index**
3. A shadow copy of the index is built in the background. Search keeps using the old index until the new one is complete, so there is no downtime.
4. When it finishes, compare results in the **Preview** tab, then click **Promote**.

Re-indexing time depends on collection size — roughly 10 minutes per 10,000 documents. Embedding generation for re-indexing is billed at the normal per-document rate, except during the final 30 days before a forced retirement, when it is free.

### Can I roll back after promoting a new embedding model?
Yes, for **7 days**. The previous index is kept and can be restored from **Collections > Settings > Index History**. After 7 days it is deleted.

### Why can't I mix embedding models in one collection?
Vectors from different embedding models live in different mathematical spaces, so comparing them gives meaningless similarity scores. If a query is embedded with one model and documents with another, search returns confidently wrong results. This is why the whole collection must be re-indexed together.

---

## Troubleshooting After a Model Change

### Answers changed after a model upgrade — is this a bug?
Usually not. New answer models can phrase things differently, give longer or shorter answers, or cite different chunks even with the same content. To check:

1. Look at the `model` field in the API response to confirm which version answered.
2. Compare the `sources` list from before and after. If the sources are the same and only the wording changed, it's the new model's style.
3. If you need the old behavior, pin the previous version while you adjust your prompts or tests.

If the sources themselves changed after an **embedding** migration, or answer quality dropped noticeably, contact support@stratifylabs.io with example queries and the before/after request IDs.

### Search quality dropped right after re-indexing — what should I check?
1. **Confidence threshold** — new embedding models often produce scores on a different scale. A threshold tuned for the old model (for example, 0.80) may now filter out good results. Re-tune it using the Preview tab.
2. **Partial re-index** — check that the re-index status is "Complete" and the document count matches the old index.
3. **Custom integrations caching vectors** — if your own system stores query embeddings, it must switch to the new model at the same time.

### How do I test a new model before it becomes the default?
Every new model is available as a **preview** for at least 30 days before we move the default alias. Pass `"model": "fast-preview"` on individual requests, or create a test collection pinned to the preview version and run your evaluation set against it.
