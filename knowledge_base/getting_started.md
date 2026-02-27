# Getting Started with Stratify Labs

## Account Setup

### How do I create a Stratify Labs account?
Visit dashboard.stratifylabs.io and click "Start Free Trial." You'll need a valid business email address. Personal email domains (gmail.com, yahoo.com, etc.) are not accepted for enterprise accounts. After submitting, you'll receive a verification email within 5 minutes.

### I didn't receive my verification email — what do I do?
First, check your spam or junk folder. If it's not there, wait a few minutes and try again. Still nothing? Contact us at support@stratifylabs.io and we'll resend it or verify your account manually.

### How do I set up my organization?
After verifying your email, you'll be prompted to create your organization. Choose your organization name carefully — it becomes part of your API endpoint and cannot be changed later without contacting support. If you need to rename your org, reach out to support@stratifylabs.io.

### How do I invite my team?
Go to **Settings > Team** and enter their email addresses. Team members receive an invitation email with a link to join. There are three roles:

- **Owner** — Full access including billing, API key management, and member management. Only one owner per organization.
- **Admin** — Can manage API keys, configure integrations, and view all analytics. Cannot modify billing or transfer ownership.
- **Member** — Can use the platform and generate personal API keys. Cannot access organization-wide settings.

---

## API Keys

### What are the different API key types?
Every API key has a prefix that tells you what it's for:

- `ak_live_` — Production keys. These count toward your usage limits.
- `ak_test_` — Sandbox keys for development and testing. They do **not** count toward your usage limits.
- `ak_readonly_` — Read-only keys for analytics and monitoring dashboards.

Use test keys when building and testing so you don't burn through your plan's limits.

### How do I create or rotate an API key?
Go to **Settings > API Keys** and click "Create New Key." To rotate an existing key, click the key and select "Rotate." The old key stays valid for 24 hours so you have time to update your integrations. If you think a key was compromised, you can expire it immediately.

### My API key isn't working — what should I check?
A few common reasons an API key stops working:

1. **Wrong key type** — Test keys (`ak_test_`) only work in the sandbox environment. Make sure you're using a live key (`ak_live_`) for production requests.
2. **Key was rotated or revoked** — Check Settings > API Keys to see if the key is still active.
3. **Key was detected in a public repo** — If we detect your key in a public GitHub repository, we automatically revoke it and notify the account owner. Check your email for a notification.
4. **Permissions** — If you're using a read-only key (`ak_readonly_`), it can't make write requests.

If none of those apply, contact support@stratifylabs.io with the key prefix (not the full key) and we'll investigate.

### How do I keep my API key secure?
Never paste your API key directly into code or commit it to version control. Store it as an environment variable or use a secrets manager. We automatically revoke keys found in public GitHub repositories.

---

## Rate Limits

### What are my rate limits?
Your rate limits depend on your plan:

| Plan | Requests/minute | Requests/day | Concurrent connections |
|------|-----------------|--------------|----------------------|
| Free Trial | 10 | 1,000 | 2 |
| Starter | 60 | 50,000 | 10 |
| Professional | 300 | 500,000 | 50 |
| Enterprise | Custom | Custom | Custom |

### I'm hitting rate limits — what should I do?
When you hit a rate limit, you'll get an HTTP **429 Too Many Requests** error. Here's what to do:

1. **Wait before retrying** — The response includes a `Retry-After` header telling you how many seconds to wait.
2. **Check your usage** — Go to Settings > Billing > Usage to see how close you are to your daily limit.
3. **Use test keys for development** — Test API keys don't count toward your limits.
4. **Consider upgrading** — If you're regularly hitting limits, it may be time to move to a higher plan. You can upgrade anytime from Settings > Billing.

If you're on Enterprise and hitting custom limits, contact your dedicated support engineer.

---

## Uploading and Ingesting Documents

### What file types can I upload?
Stratify Labs supports these file formats:
- Plain text (.txt)
- Markdown (.md)
- PDF (.pdf) — text is extracted; scanned/image-only PDFs are not supported
- HTML (.html) — HTML tags are automatically stripped
- CSV (.csv) — each row is treated as a separate document

### How do I upload documents to the platform?
You can upload documents directly from the **Collections** section of your dashboard:
1. Go to your dashboard at dashboard.stratifylabs.io
2. Open or create a Collection
3. Click "Upload Documents" and select your files
4. Wait for processing — you'll see a confirmation once documents are indexed

### How long does it take for uploaded documents to be searchable?
Most documents are indexed within 1–2 minutes. The first query after a new upload may take a few extra seconds while embeddings are being generated. After that, responses should come back in under 500ms.

### Why is my first query slow after uploading?
This is normal. The first query after ingesting new documents may take 2–5 seconds while embeddings are being generated in the background. Subsequent queries will be fast.

---

## Still Need Help?

If you've gone through these steps and are still stuck, we're happy to help. Reach out at **support@stratifylabs.io** and include:
- Your organization name
- The API key prefix (first 10 characters only — never the full key)
- The exact error message you're seeing
- What you were trying to do when the error occurred
