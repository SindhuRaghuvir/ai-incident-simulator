# Stratify Labs Platform - Getting Started Guide

## Account Setup

To create your Stratify Labs account, visit dashboard.acmesaas.com and click "Start Free Trial." You'll need a valid business email address. Personal email domains (gmail.com, yahoo.com, etc.) are not accepted for enterprise accounts.

After registration, you'll receive a verification email within 5 minutes. If you don't receive it, check your spam folder or contact support@acmesaas.com.

### Organization Setup

Once verified, you'll be prompted to create your organization. Choose your organization name carefully — it becomes part of your API endpoint URL (e.g., api.acmesaas.com/v2/org/your-org-name/) and cannot be changed after creation without contacting support.

You can invite team members from the Settings > Team page. There are three roles:

- **Owner**: Full access including billing, API key management, and member management. Only one owner per organization.
- **Admin**: Can manage API keys, configure integrations, and view all analytics. Cannot modify billing or transfer ownership.
- **Member**: Can use the platform, view their own usage analytics, and generate personal API keys. Cannot access organization-wide settings.

## API Key Management

API keys are generated from Settings > API Keys. Each key has a prefix that indicates its type:

- `ak_live_` — Production keys with full access
- `ak_test_` — Sandbox keys that don't count toward usage limits
- `ak_readonly_` — Read-only keys for analytics and monitoring

To rotate an API key: go to Settings > API Keys, click the key you want to rotate, and select "Rotate." The old key remains valid for 24 hours to allow migration. You can also set it to expire immediately if you suspect a security breach.

**Important**: Never commit API keys to version control. Use environment variables or a secrets manager. If we detect a key in a public GitHub repository, we will automatically revoke it and notify the account owner.

### Rate Limits

Rate limits depend on your plan:

| Plan | Requests/minute | Requests/day | Concurrent connections |
|------|-----------------|--------------|----------------------|
| Free Trial | 10 | 1,000 | 2 |
| Starter | 60 | 50,000 | 10 |
| Professional | 300 | 500,000 | 50 |
| Enterprise | Custom | Custom | Custom |

When you hit a rate limit, the API returns HTTP 429 with a `Retry-After` header indicating how many seconds to wait. Implement exponential backoff in your client code.

## Quick Start: Your First API Call

Install the SDK:

```bash
pip install acmesaas-sdk
```

Make your first call:

```python
from acmesaas import AcmeClient

client = AcmeClient(api_key="ak_test_your_key_here")

# Search your knowledge base
results = client.search(
    query="How do I reset my password?",
    collection="support-docs",
    top_k=5
)

for result in results:
    print(f"Score: {result.score:.2f} - {result.text[:100]}")
```

## Data Ingestion

You can ingest documents through the API or the web dashboard.

### Supported Formats
- Plain text (.txt)
- Markdown (.md)
- PDF (.pdf) — text extraction only, no OCR
- HTML (.html) — tags are stripped automatically
- CSV (.csv) — each row becomes a separate document

### Ingestion via API

```python
# Single document
client.ingest(
    collection="support-docs",
    text="Your document content here",
    metadata={"source": "zendesk", "category": "billing"}
)

# Batch ingestion (up to 100 documents per request)
documents = [
    {"text": "Doc 1 content", "metadata": {"source": "wiki"}},
    {"text": "Doc 2 content", "metadata": {"source": "wiki"}},
]
client.ingest_batch(collection="support-docs", documents=documents)
```

### Chunking

Documents longer than 512 tokens are automatically chunked. The default chunking strategy is "paragraph" which splits on double newlines and tries to keep chunks between 200-500 tokens. You can configure this per collection:

```python
client.configure_collection(
    name="support-docs",
    chunking_strategy="sentence",  # or "paragraph", "fixed", "none"
    chunk_size=300,
    chunk_overlap=50
)
```

## Troubleshooting Common Setup Issues

**"Invalid API key" error**: Ensure you're using the correct key type. Test keys (ak_test_) only work against the sandbox environment (sandbox.api.acmesaas.com). Production keys (ak_live_) only work against the production API.

**"Organization not found" error**: Check that your API endpoint URL includes the correct organization name. The org name is case-sensitive.

**Slow initial queries**: The first query after ingesting new documents may be slow (2-5 seconds) as embeddings are being generated. Subsequent queries use cached embeddings and should respond in under 500ms.

**"Collection not found" error**: Collections are created automatically on first ingestion. If you're querying an empty collection, you'll get this error. Ingest at least one document first.

**Timeout errors**: The default timeout is 30 seconds. For large batch ingestions, increase the timeout in your client configuration: `client = AcmeClient(api_key="...", timeout=120)`
