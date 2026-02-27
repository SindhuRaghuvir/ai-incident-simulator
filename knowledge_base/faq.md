# Frequently Asked Questions

## About Stratify Labs

### 1. What is Stratify Labs?
Stratify Labs is an AI-powered knowledge base platform. You upload your documents — support articles, internal wikis, product guides, resolved tickets — and Stratify Labs makes that content searchable using AI. Instead of keyword matching, it understands the meaning of questions and returns the most relevant answers from your content.

Teams use it to power customer-facing chatbots, internal knowledge assistants, and support agent tools.

### 2. How is Stratify Labs different from a regular search engine?
Traditional search engines match keywords. If you search for "can't log in" and your article says "account access issues," keyword search might miss it.

Stratify Labs uses semantic search — it understands that "can't log in" and "account access issues" are related concepts and returns the right content either way. It's also designed to pull the specific, relevant chunk of a document rather than returning the whole page.

### 3. Do you store my documents permanently?
Your documents are stored as long as your account is active. You can delete individual documents or entire collections at any time.

If you cancel your account, your data is retained for 30 days so you have time to export it. After 30 days, everything is permanently deleted.

---

## Features and Capabilities

### 4. What file types are supported?
Stratify Labs supports:
- Plain text (.txt)
- Markdown (.md)
- PDF (.pdf) — text-based PDFs only; scanned/image PDFs are not supported
- HTML (.html)
- CSV (.csv) — each row is indexed as a separate document

If you have documents in a format not listed here, contact support@stratifylabs.io and we'll let you know if we can support it.

### 5. Can I use Stratify Labs for internal company knowledge?
Absolutely — this is one of the most common use cases. Teams use it to index internal wikis, runbooks, HR policies, product documentation, and engineering specs. You can connect it directly to Confluence, or upload documents manually.

Permissions can be scoped so different teams only see content relevant to them.

### 6. How accurate are the answers?
Accuracy depends on the quality and coverage of your knowledge base. If your documents contain clear, well-written answers, Stratify Labs will return them accurately. If your KB has gaps, the system will tell the user it doesn't know rather than guessing.

You can improve accuracy by:
- Adding more relevant documents
- Writing content clearly and directly
- Using Q&A format in source documents when possible

### 7. What happens if the AI doesn't know the answer?
If no content in your knowledge base meets the confidence threshold for a query, the system returns a "I don't have enough information to answer that" response rather than making something up.

You can configure a custom fallback message that directs users to human support or other resources.

---

## Pricing and Trial

### 8. Is there a free trial?
Yes — the free trial is 14 days with no credit card required. You get:
- 1,000 API requests per day
- 1 collection (up to 10,000 documents)
- Community support

After the trial ends, you can upgrade to a paid plan or your data will be kept for 30 days before being deleted.

### 9. What plans are available?
- **Free Trial** — 14 days, no credit card
- **Starter** — $49/month
- **Professional** — $199/month
- **Enterprise** — Custom pricing

See the full plan comparison and feature details in the Billing and Plans section, or visit dashboard.stratifylabs.io.

---

## Data and Privacy

### 10. Where is my data stored?
By default, data is stored in US-East AWS data centers. Professional and Enterprise customers can choose EU-West (Ireland) as their data region. Enterprise customers have additional options for global deployment and custom data residency.

All data is encrypted at rest (AES-256-GCM) and in transit (TLS 1.3).

### 11. Can I use my own embedding model or OpenAI API key?
Enterprise plans support bring-your-own-model (BYOM) configurations, including using your own OpenAI API key or a self-hosted embedding model. Contact support@stratifylabs.io to discuss setup for your use case.

### 12. How do I export my data?
Go to **Settings > Security > Data Export** to download all your organization's data in JSON format. This includes your documents, collection metadata, and settings.

We recommend exporting before canceling your account since data is permanently deleted 30 days after cancellation.

---

## Technical and Integration

### 13. What languages are supported?
Stratify Labs supports multilingual search — you can index and query documents in most major languages including English, Spanish, French, German, Portuguese, Japanese, Chinese (simplified and traditional), and more.

For best results, keep query language consistent with document language (e.g., search in Spanish if your documents are in Spanish).

### 14. What is your uptime SLA?
Uptime commitments by plan:
- **Starter**: 99.5% uptime
- **Professional**: 99.9% uptime
- **Enterprise**: 99.99% uptime

Check current platform status at status.stratifylabs.io. During incidents, we post updates every 2 hours and publish a post-incident report within 5 business days.

---

## Getting Support

### 15. How do I talk to a human support agent?
You can reach us at:

- **Email**: support@stratifylabs.io (response times vary by plan — see below)
- **Live chat**: Available in your dashboard for Professional and Enterprise customers

Response time by plan:
- **Free Trial / Community**: Community forums, best effort
- **Starter**: Email support, 48-hour response time
- **Professional**: Priority email and chat, 4-hour response time
- **Enterprise**: Dedicated support engineer, 1-hour response time

When contacting support, please include your organization name, a description of the issue, and any relevant error messages or screenshots. The more detail you provide, the faster we can help.
