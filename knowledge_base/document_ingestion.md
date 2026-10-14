# Document Ingestion and Indexing

## Limits and Formats

### What are the file size and document limits?

| Limit | Free Trial | Starter | Professional | Enterprise |
|-------|-----------|---------|-------------|------------|
| Max file size | 10 MB | 25 MB | 100 MB | 500 MB |
| Documents per collection | 10,000 | 50,000 | 500,000 | Custom |
| Collections | 1 | 5 | Unlimited | Unlimited |
| Files per bulk upload | 50 | 200 | 1,000 | Custom |

Files over your plan's size limit are rejected with **413 Payload Too Large**. Split large documents (for example, by chapter) before uploading.

### Which file types are supported?
Text (.txt), Markdown (.md), PDF (.pdf, text-based only), HTML (.html), and CSV (.csv). Text must be UTF-8 encoded. For CSV files, each row is indexed as a separate document, and the first row must be a header row.

---

## Ingestion Status

### What do the document statuses mean?

| Status | Meaning |
|--------|---------|
| **Queued** | Upload received, waiting for a processing slot |
| **Processing** | Text is being extracted, chunked, and embedded |
| **Indexed** | Ready — the document is searchable |
| **Partially indexed** | Some pages or rows failed; the rest are searchable |
| **Failed** | Nothing was indexed; see the error message on the document |

You can check status in the dashboard or with `GET /collections/{name}/documents/{id}`. You can also subscribe to the `document.indexed` and `document.failed` webhook events instead of polling.

### My document has been stuck in "Queued" or "Processing" for a long time
Normal processing takes 1–2 minutes per document. Large bulk uploads are processed in order, so the last files in a batch of 1,000 can take 20–30 minutes.

1. Check **status.stratifylabs.io** for ingestion pipeline delays.
2. Check the collection's queue depth at **Collections > (your collection) > Activity**.
3. If a single document has been in **Processing** for more than 60 minutes while others finish, delete and re-upload it.

If it still doesn't complete, contact support@stratifylabs.io with the document ID.

---

## Common Ingestion Errors

### My PDF failed with "No extractable text"
The PDF is a scanned image or a photo of a document, so there's no text layer to read. Run it through OCR software (most PDF editors have a "Recognize Text" option), save it, and upload again. To check, open the PDF and try to select a sentence — if you can't highlight the text, it needs OCR.

### My PDF failed with "Document is encrypted"
Password-protected or permission-restricted PDFs can't be processed. Remove the password (File > Properties > Security in most PDF readers), save a new copy, and upload that.

### I'm getting "Invalid encoding" errors on text or CSV files
The file isn't UTF-8. This is common with CSVs exported from older versions of Excel. Re-save the file as **CSV UTF-8** (Excel: File > Save As > CSV UTF-8), or convert it with a text editor that lets you choose the encoding.

### My CSV was only partially indexed
Usually caused by rows with a different number of columns than the header — often from unescaped commas or line breaks inside a field. Wrap fields that contain commas or line breaks in double quotes. The document's error details list the first 20 failing row numbers.

### Tables in my PDF come out jumbled in answers
PDF text extraction reads left to right, which can scramble multi-column layouts and complex tables. For table-heavy content, export the table as CSV or Markdown and upload it separately so each row stays intact.

---

## Updating and Deleting

### How do I update a document that has changed?
Upload it again with the **same document ID** (`PUT /collections/{name}/documents/{id}`, or **Replace** in the dashboard). The old chunks and embeddings are removed and the new version is indexed. Uploading under a new ID creates a duplicate, and both versions will appear in search results.

### Why am I seeing old content in answers after I updated a document?
1. **It was uploaded as a new document** instead of replacing the old one — search the collection for the old title and delete the outdated copy.
2. **Re-indexing hasn't finished** — the old version stays searchable until the new one reaches **Indexed**.
3. **Answer Cache** — if enabled, cached answers expire within 60 minutes, or you can clear the cache at **Collections > Settings > Performance**.
4. **Synced source not updated** — for Zendesk or Confluence, the change appears after the next sync.

### When I delete a document, is it removed immediately?
The document stops appearing in search results within **1 minute**. Its stored file, chunks, and embeddings are permanently deleted within **24 hours**, and removed from backups within 30 days, in line with our retention policy.

### Does Stratify Labs detect duplicate documents?
Yes. Exact duplicates (identical content) in the same collection are skipped and the upload returns the existing document's ID. Near-duplicates (for example, the same article with a different footer) are flagged in **Collections > Content Health** so you can decide which version to keep.

---

## Metadata and Filtering

### Can I add tags or metadata to documents?
Yes. Attach up to 20 key-value metadata fields per document, such as `{"product": "billing", "audience": "admin", "language": "en"}`. You can then filter searches by metadata, for example to only search admin docs for admin users. Metadata filters are applied before similarity search, so they also make queries faster.
