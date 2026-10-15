"""Suggested questions for the Chat page.

Each question names the KB doc that answers it ("doc", plus any other docs that
also cover it in "also") and the facts a correct answer must contain. The Chat
page only uses "q" and "doc"; eval/run_kb_eval.py uses the rest to check that
every suggestion retrieves the right doc and gets a correct answer. Re-run the
eval after editing this file or anything in knowledge_base/.
"""

SUGGESTIONS = [
    # -- account_and_login.md --
    {"q": "How do I reset my password?", "doc": "account_and_login.md",
     "facts": ["Click 'Forgot password?' on the dashboard sign-in page", "The reset link expires after 1 hour"]},
    {"q": "My account is locked", "doc": "account_and_login.md",
     "facts": ["The lockout lifts automatically after 15 minutes", "Resetting the password also unlocks the account"]},
    {"q": "I lost access to my MFA device", "doc": "account_and_login.md",
     "facts": ["Log in with a backup/recovery code", "Without backup codes, contact support@stratifylabs.io (can take up to 1 business day)"]},
    {"q": "My team invitation link doesn't work", "doc": "account_and_login.md",
     "facts": ["Invitation links expire after 7 days", "An Owner or Admin can resend it from Settings > Team"]},

    # -- getting_started.md --
    {"q": "How do I invite someone to my team?", "doc": "getting_started.md",
     "facts": ["Go to Settings > Team and enter their email", "Roles are Owner, Admin and Member"]},
    {"q": "My API key isn't working", "doc": "getting_started.md", "also": ["troubleshooting.md"],
     "facts": ["Test keys (ak_test_) only work in the sandbox; production needs ak_live_",
               "The key may have been rotated or revoked",
               "Keys found in public GitHub repos are revoked automatically"]},
    {"q": "What are the different API key types?", "doc": "getting_started.md",
     "facts": ["ak_live_ is production and counts toward limits", "ak_test_ is sandbox and does not count toward limits", "ak_readonly_ is read-only"]},
    {"q": "What are the rate limits on each plan?", "doc": "getting_started.md", "also": ["troubleshooting.md"],
     "facts": ["Free Trial: 10 requests/minute, 1,000/day", "Starter: 60 requests/minute, 50,000/day", "Professional: 300 requests/minute, 500,000/day"]},

    # -- billing_and_plans.md --
    {"q": "What's the difference between Starter and Professional?", "doc": "billing_and_plans.md",
     "facts": ["Starter is $49/month and Professional is $199/month",
               "Starter allows 50,000 requests/day; Professional 500,000",
               "Starter has 5 collections; Professional has unlimited",
               "Professional adds SSO"]},
    {"q": "I was charged unexpectedly — what happened?", "doc": "billing_and_plans.md",
     "facts": ["Usage overage", "Annual renewal charged upfront", "Prorated charge after a mid-cycle upgrade"]},
    {"q": "How do I cancel my subscription?", "doc": "billing_and_plans.md",
     "facts": ["Settings > Billing > Cancel Subscription", "Data is kept 30 days, then permanently deleted", "API keys are deactivated immediately"]},
    {"q": "Can I get a refund?", "doc": "billing_and_plans.md",
     "facts": ["New customers get a full refund within 7 days of their first subscription",
               "Usage charges already consumed are not refunded",
               "Email support@stratifylabs.io with the account name and invoice number"]},
    {"q": "Where can I find my invoice?", "doc": "billing_and_plans.md",
     "facts": ["Settings > Billing > Invoice History", "Invoices are also emailed on the billing date"]},
    {"q": "How do I upgrade my plan?", "doc": "billing_and_plans.md",
     "facts": ["Settings > Billing > Change Plan", "Upgrades take effect immediately", "You pay a prorated amount for the rest of the cycle"]},
    {"q": "Is there a discount for annual billing?", "doc": "billing_and_plans.md",
     "facts": ["20% off", "Starter $470/year", "Professional $1,910/year"]},

    # -- faq.md --
    {"q": "Is there a free trial?", "doc": "faq.md", "also": ["billing_and_plans.md"],
     "facts": ["14 days", "No credit card required", "1,000 API requests per day", "1 collection (up to 10,000 documents)"]},
    {"q": "What is your uptime SLA?", "doc": "faq.md", "also": ["support_and_escalation.md"],
     "facts": ["Starter 99.5%", "Professional 99.9%", "Enterprise 99.99%"]},
    {"q": "How do I talk to a human support agent?", "doc": "faq.md", "also": ["support_and_escalation.md"],
     "facts": ["Email support@stratifylabs.io", "Live chat is available on Professional and Enterprise"]},
    {"q": "What languages are supported?", "doc": "faq.md",
     "facts": ["Most major languages (e.g. English, Spanish, French, German, Japanese, Chinese)", "Keep the query language the same as the document language"]},
    {"q": "Where is my data stored?", "doc": "faq.md", "also": ["security_and_compliance.md"],
     "facts": ["US-East by default", "EU-West (Ireland) is available on Professional and Enterprise", "Enterprise can get custom data residency"]},

    # -- product_overview.md --
    {"q": "What is a collection?", "doc": "product_overview.md",
     "facts": ["A named group of documents that is searched together", "Group collections by who searches them", "Each collection is tied to one embedding model"]},
    {"q": "How do I make my first API query?", "doc": "product_overview.md", "also": ["api_reference.md"],
     "facts": ["Create a key at Settings > API Keys", "POST to /query with the key as a Bearer token", "Base URL https://api.stratifylabs.io/v1/{org}/"]},
    {"q": "How does Stratify Labs work?", "doc": "product_overview.md", "also": ["faq.md", "answer_quality_and_tuning.md"],
     "facts": ["Upload documents into collections", "Retrieval finds the most relevant chunks, then a model writes the answer from them", "Answers come with their sources"]},

    # -- security_and_compliance.md --
    {"q": "Is Stratify Labs HIPAA compliant?", "doc": "security_and_compliance.md",
     "facts": ["Enterprise only", "Requires a signed BAA", "7-year audit log retention"]},
    {"q": "How do I enable MFA?", "doc": "security_and_compliance.md", "also": ["account_and_login.md"],
     "facts": ["Settings > Security > Authentication, then Enable MFA", "Authenticator app, SMS, or hardware key"]},
    {"q": "How do I report a security issue?", "doc": "security_and_compliance.md",
     "facts": ["Email security@stratifylabs.io", "Acknowledged within 24 hours", "Severity assessed within 72 hours"]},
    {"q": "What happens to my data if I cancel?", "doc": "security_and_compliance.md", "also": ["billing_and_plans.md", "faq.md"],
     "facts": ["Data is kept for 30 days", "Export it at Settings > Security > Data Export", "After 30 days it is permanently deleted"]},
    {"q": "Is my data encrypted?", "doc": "security_and_compliance.md",
     "facts": ["TLS 1.3 in transit", "AES-256-GCM at rest", "Keys managed in AWS KMS and rotated every 90 days"]},
    {"q": "Do you support SSO?", "doc": "security_and_compliance.md",
     "facts": ["Professional and Enterprise plans", "SAML 2.0 and OIDC"]},

    # -- troubleshooting.md --
    {"q": "I got a 429 error — what do I do?", "doc": "troubleshooting.md", "also": ["getting_started.md"],
     "facts": ["You exceeded your plan's rate limit", "Wait for the Retry-After header", "Check usage at Settings > Billing > Usage"]},
    {"q": "The API is returning 500 errors", "doc": "troubleshooting.md",
     "facts": ["Check status.stratifylabs.io", "Retry after a few minutes", "If it persists, contact support with timestamps and request IDs"]},
    {"q": "I'm getting a 403 Forbidden error", "doc": "troubleshooting.md",
     "facts": ["A read-only key is making a write request", "Your role doesn't have access", "Your IP isn't on the IP allowlist"]},
    {"q": "My search results are irrelevant", "doc": "troubleshooting.md", "also": ["answer_quality_and_tuning.md"],
     "facts": ["The knowledge base may not contain the content", "Raise the confidence threshold", "Check you're querying the right collection"]},

    # -- integrations.md --
    {"q": "My Slack bot isn't responding", "doc": "integrations.md",
     "facts": ["The channel isn't in the allowlist", "The API key was rotated, so click Reconnect", "The confidence threshold is too high", "The bot was removed from the channel"]},
    {"q": "My Zendesk articles aren't syncing", "doc": "integrations.md",
     "facts": ["Only published articles sync, not drafts", "The Zendesk API token may have expired, so reconnect"]},
    {"q": "Do you integrate with Microsoft Teams or Google Drive?", "doc": "integrations.md",
     "facts": ["Native integrations are Slack, Zendesk and Confluence", "Other tools connect through inbound webhooks or the API"]},
    {"q": "How do I verify webhooks are really from Stratify?", "doc": "integrations.md",
     "facts": ["HMAC-SHA256 signature", "X-Stratify-Signature header"]},

    # -- api_reference.md --
    {"q": "Which API errors should my code retry?", "doc": "api_reference.md", "also": ["performance_and_latency.md"],
     "facts": ["Retry 429 and 5xx", "Don't retry 400, 401, 403, 404, 409 or 413",
               "Back off 1s, 2s, 4s, 8s with jitter, max 5 attempts"]},
    {"q": "How do I stream answers from the API?", "doc": "api_reference.md",
     "facts": ["Set \"stream\": true on /query", "Server-Sent Events: token events, then a done event with sources and usage"]},
    {"q": "What's the difference between /query and /search?", "doc": "api_reference.md",
     "facts": ["/query returns an AI answer with sources", "/search returns matching chunks only and is faster (under 300 ms)"]},
    {"q": "How do I avoid duplicate documents when I retry an upload?", "doc": "api_reference.md",
     "facts": ["Send an Idempotency-Key header", "Retries with the same key within 24 hours return the original response"]},

    # -- support_and_escalation.md --
    {"q": "What are the severity levels and response times?", "doc": "support_and_escalation.md",
     "facts": ["Sev 1 Critical to Sev 4 Low", "Sev 1 first response: Starter 24h, Professional 2h, Enterprise 1h (24/7)"]},
    {"q": "How do I escalate a ticket that isn't moving?", "doc": "support_and_escalation.md",
     "facts": ["Reply 'Please escalate' with the business impact", "Professional: email escalations@stratifylabs.io",
               "Enterprise: contact your dedicated engineer or TAM"]},
    {"q": "Do SLA breaches earn service credits?", "doc": "support_and_escalation.md",
     "facts": ["Credits of 10%, 25% or 50% of the monthly fee", "Request within 30 days via billing@stratifylabs.io"]},
    {"q": "What should I include in a support ticket?", "doc": "support_and_escalation.md",
     "facts": ["Expected vs. actual behaviour", "Request IDs", "Timestamps (UTC)", "Never the full API key"]},

    # -- performance_and_latency.md --
    {"q": "How fast should the API respond?", "doc": "performance_and_latency.md",
     "facts": ["/search p50 150 ms, p95 400 ms", "/query full answer p50 2.0 s, p95 4.5 s"]},
    {"q": "My requests are timing out", "doc": "performance_and_latency.md", "also": ["api_reference.md"],
     "facts": ["Set the client timeout to at least 30 seconds for /query", "Check status.stratifylabs.io"]},
    {"q": "What happens if I go over my concurrency limit?", "doc": "performance_and_latency.md",
     "facts": ["Requests queue for up to 10 seconds", "Then fail with 429 concurrency_limit_exceeded"]},
    {"q": "Why is the first request after a quiet period slow?", "doc": "performance_and_latency.md",
     "facts": ["Collections idle for over 24 hours move to warm storage", "The first query takes 1–3 extra seconds"]},

    # -- answer_quality_and_tuning.md --
    {"q": "The AI made up an answer — why?", "doc": "answer_quality_and_tuning.md",
     "facts": ["High temperature", "Low confidence threshold", "Custom instructions that encourage guessing"]},
    {"q": "What confidence threshold should I use?", "doc": "answer_quality_and_tuning.md",
     "facts": ["Start at 0.70", "Tune it in the Retrieval Debugger at Collections > Debug"]},
    {"q": "Is a bad answer a retrieval problem or a generation problem?", "doc": "answer_quality_and_tuning.md",
     "facts": ["Right doc missing from sources means retrieval", "Right doc in sources but answer wrong means generation"]},
    {"q": "What chunk size should I use?", "doc": "answer_quality_and_tuning.md",
     "facts": ["FAQs 300–500 characters", "How-to guides 800–1,200", "Long policy docs 1,200–2,000"]},

    # -- document_ingestion.md --
    {"q": "My PDF failed with 'No extractable text'", "doc": "document_ingestion.md",
     "facts": ["It's a scanned/image PDF with no text layer", "Run OCR and upload again"]},
    {"q": "Why am I seeing old content after updating a document?", "doc": "document_ingestion.md",
     "facts": ["It was uploaded as a new document instead of replacing the old one", "Re-indexing hasn't finished", "Answer Cache can serve it for up to 60 minutes"]},
    {"q": "What are the file size limits?", "doc": "document_ingestion.md",
     "facts": ["Free Trial 10 MB, Starter 25 MB, Professional 100 MB, Enterprise 500 MB", "Larger files get 413 Payload Too Large"]},
    {"q": "What file types can I upload?", "doc": "document_ingestion.md", "also": ["getting_started.md", "faq.md"],
     "facts": [".txt, .md, .pdf (text-based only), .html and .csv"]},
    {"q": "My document is stuck in Processing", "doc": "document_ingestion.md",
     "facts": ["Normal is 1–2 minutes per document", "Large batches can take 20–30 minutes", "Stuck over 60 minutes: delete and re-upload"]},

    # -- models_and_deprecations.md --
    {"q": "What happens when a model is deprecated?", "doc": "models_and_deprecations.md",
     "facts": ["At least 90 days notice for answer models, 6 months for embedding models",
               "Retired answer models are auto-routed to the replacement",
               "Un-migrated embedding collections become read-only"]},
    {"q": "Answers changed after a model upgrade — is this a bug?", "doc": "models_and_deprecations.md",
     "facts": ["Usually not; new models phrase things differently", "Compare the model field and the sources", "Pin the previous version if you need the old behaviour"]},
    {"q": "What is model pinning?", "doc": "models_and_deprecations.md",
     "facts": ["Locks a collection to a version such as fast-2026-03 instead of the moving alias", "Pinned versions are still subject to deprecation"]},

    # -- enterprise_onboarding.md --
    {"q": "What does Enterprise onboarding look like?", "doc": "enterprise_onboarding.md",
     "facts": ["4–6 weeks", "Kickoff, Setup, Content and tuning, Pilot, Go-live", "Led by the TAM"]},
    {"q": "What happens in a QBR?", "doc": "enterprise_onboarding.md",
     "facts": ["Progress against success plan metrics", "Usage and cost forecast", "Incidents and RCAs", "Upcoming deprecations"]},
    {"q": "Who should attend the onboarding kickoff?", "doc": "enterprise_onboarding.md",
     "facts": ["Executive sponsor", "Technical owner", "Content owner", "Security or IT contact"]},
    {"q": "What is hypercare?", "doc": "enterprise_onboarding.md",
     "facts": ["The first 2 weeks after go-live", "TAM and support engineer monitor daily"]},
]

# Questions the KB deliberately does NOT answer. With every failure off, the
# right answer is "the docs don't say" (or only the partial facts listed).
# Chat shows these only while the Hallucination failure is on, so the model's
# invented specifics are easy to spot. Failure Lab's walkthrough uses the first.
HALLUCINATION_BAIT = [
    {"q": "How long do refunds take to process?",
     "facts": ["Says the documentation doesn't give a refund processing time"]},
    {"q": "What's the exact price of the Enterprise plan?",
     "facts": ["Enterprise pricing is custom; no fixed price is published"]},
    {"q": "Which countries do you have data centers in?",
     "facts": ["US-East is the default region", "EU-West (Ireland) is the other named region"]},
    {"q": "What discount do nonprofits get?",
     "facts": ["Says the documentation doesn't mention a nonprofit discount"]},
    {"q": "What's the phone number for support?",
     "facts": ["No public phone number; Enterprise has a 24/7 Sev 1 line listed in the order form"]},
]
