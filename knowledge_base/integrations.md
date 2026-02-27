# Integrations

## Overview

Stratify Labs connects with the tools your team already uses — Slack, Zendesk, and Confluence — to automatically sync knowledge and deliver answers where work happens. All integrations are configured from **Settings > Integrations** in your dashboard at dashboard.stratifylabs.io.

---

## Slack Integration

### How do I connect Stratify Labs to Slack?
1. Go to **Settings > Integrations > Slack**
2. Click "Add to Slack" and authorize Stratify Labs in your workspace
3. Choose which channels the bot is allowed to respond in
4. Select which collections it should search when answering questions

Once connected, you can mention `@Stratify Labs` in any authorized channel to ask a question.

### My Slack bot isn't responding — what should I check?
A few common reasons the bot goes quiet:

1. **Channel not in the allowlist** — The bot only responds in channels you've explicitly enabled. Go to Settings > Integrations > Slack and check the channel list.
2. **API key was rotated** — If you recently rotated your API key, the Slack integration needs to be re-authorized. Go to Settings > Integrations > Slack and click "Reconnect."
3. **Confidence threshold too high** — If the bot can't find an answer above your confidence threshold, it stays silent. Lower the threshold or check that your knowledge base has relevant content.
4. **Bot was removed from the channel** — Re-invite the bot with `/invite @Stratify Labs`.

If the bot is still not responding after checking these, contact support@stratifylabs.io.

### The Slack bot is responding twice to the same message
This usually happens when the bot is installed in multiple Slack workspaces that both point to the same Stratify Labs organization. Go to Settings > Integrations > Slack and remove any duplicate workspace connections.

### Why does the Slack bot say "thinking..." before answering?
Slack requires an initial acknowledgment within 3 seconds. If your knowledge base is large, the search takes longer, so the bot sends a "thinking…" message first and then updates it with the actual answer. This is normal behavior.

### Can the bot answer automatically without being mentioned?
Yes — enable "Auto-respond" in **Settings > Integrations > Slack > Configuration**. When on, the bot uses AI to detect questions in designated channels and responds without being mentioned. You can set a confidence threshold so it only responds when it's reasonably confident in the answer.

---

## Zendesk Integration

### How do I connect Zendesk?
1. Go to **Settings > Integrations > Zendesk**
2. Enter your Zendesk subdomain (e.g., yourcompany.zendesk.com)
3. Authenticate with a Zendesk admin account
4. Choose your sync direction: one-way (Zendesk → Stratify Labs) or two-way

### My Help Center articles aren't syncing from Zendesk — what's wrong?
The most common causes:

1. **Article is still in draft** — Only published articles are synced. Publish the article in Zendesk and it will sync within 15 minutes.
2. **API token expired** — Zendesk API tokens can expire. Go to Settings > Integrations > Zendesk and reconnect with a fresh token.
3. **Sync is behind** — The default sync runs every 15 minutes. If you just published an article, wait a few minutes and check again.

If articles are still missing after 30 minutes, contact support@stratifylabs.io with the article URL.

### I see customer PII in synced Zendesk tickets — how do I fix this?
By default, the PII redaction engine removes emails, phone numbers, and names from synced tickets. If you're seeing other types of sensitive data (like account numbers or custom identifiers), you can add custom redaction rules at **Settings > Integrations > Zendesk > PII Rules** using regex patterns.

### How does the Zendesk Agent Assist feature work?
When two-way sync is enabled, Stratify Labs adds a sidebar to the Zendesk agent interface:
1. An agent opens a ticket
2. The Stratify Labs sidebar shows the top 3 relevant answers from your knowledge base
3. The agent can insert a suggestion directly into their reply with one click

Usage analytics track which suggestions are used vs. ignored to help you improve your KB over time.

### What sync options are available for Zendesk?
- **Articles** — Syncs Help Center articles to a collection (every 15 minutes by default)
- **Tickets** — Syncs resolved tickets with PII redacted. Only tickets tagged "knowledge-base" are included.
- **Macros** — Syncs agent macros as knowledge snippets

Enterprise plans support real-time sync via webhooks instead of the 15-minute polling interval.

---

## Confluence Integration

### How do I connect Confluence?
1. Go to **Settings > Integrations > Confluence**
2. Select "Confluence Cloud" or "Confluence Server/Data Center"
3. For Cloud: click "Authorize with OAuth"
4. For Server: enter your Confluence base URL and a personal access token
5. Select which spaces you want to sync

### My Confluence pages aren't showing up in search results — what should I check?
1. **Space not selected** — Only spaces you explicitly selected during setup are synced. Go to Settings > Integrations > Confluence and verify your space list.
2. **Page was just created or edited** — Sync runs every 30 minutes by default. Wait up to 30 minutes after a page is saved.
3. **Page is restricted** — If a page has view restrictions in Confluence, it will only appear in Stratify Labs search results for users who also have access in Confluence (requires "Permission Sync" to be enabled — available on Professional and Enterprise plans).
4. **Attachment-only pages** — Pages without body text may not index well. Make sure the page has visible text content.

### Does Stratify Labs respect Confluence permissions?
Yes, on Professional and Enterprise plans with "Permission Sync" enabled. If a user doesn't have access to a Confluence space, results from that space are filtered out of their search results. This requires the Confluence integration to have permission-aware access.

### How often do Confluence pages sync?
- **Starter**: every 30 minutes
- **Professional**: every 15 minutes
- **Enterprise**: every 5 minutes or real-time (configurable)

Deleted pages are removed from Stratify Labs within 1 hour of deletion in Confluence.

---

## Webhooks and Custom Integrations

### Can I connect Stratify Labs to a custom tool?
Yes. You can use inbound webhooks to push documents from any system into Stratify Labs. Go to **Settings > Integrations > Webhooks > Add Endpoint** and follow the setup instructions.

You can also configure outbound webhooks to get notified when events happen in Stratify Labs — for example, when a query completes, a document is ingested, or a usage alert fires.

### How do I verify webhook deliveries are genuine?
Every webhook request includes an HMAC-SHA256 signature in the `X-Stratify-Signature` header. Verify this against your webhook secret to confirm the request came from Stratify Labs. Details are in the developer documentation.

---

## Integration Limits by Plan

| Integration | Starter | Professional | Enterprise |
|------------|---------|-------------|------------|
| Slack workspaces | 1 | 3 | Unlimited |
| Zendesk instances | 1 | 2 | Unlimited |
| Confluence spaces | 5 | 25 | Unlimited |
| Webhook endpoints | 3 | 10 | Unlimited |
| Sync frequency | 30 min | 15 min | 5 min / real-time |

Need a limit increased? Contact support@stratifylabs.io.
