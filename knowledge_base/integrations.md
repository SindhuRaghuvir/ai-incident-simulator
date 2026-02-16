# Stratify Labs Platform - Integrations Guide

## Overview

Stratify Labs integrates with your existing tools to automatically sync knowledge and deliver answers where your team works. All integrations are configured from Settings > Integrations.

## Slack Integration

### Setup
1. Go to Settings > Integrations > Slack
2. Click "Add to Slack" and authorize Stratify Labs in your workspace
3. Choose which channels the bot can respond in
4. Select the collections to search when answering questions

### Usage
Once installed, mention @Stratify Labs in any authorized channel:

```
@Stratify Labs How do I configure SSO for my team?
```

The bot will search your knowledge base and respond in a thread. Responses include a confidence score and source attribution.

### Configuration Options
- **Auto-respond**: Automatically answer questions in designated channels without being mentioned (uses AI to detect questions vs. statements)
- **Confidence threshold**: Only respond when confidence exceeds this value (default: 0.7)
- **Response format**: Choose between "concise" (1-2 sentences) or "detailed" (full paragraph with sources)
- **Fallback message**: Custom message shown when no relevant answer is found
- **Channel allowlist**: Restrict which channels the bot operates in

### Troubleshooting Slack
- **Bot not responding**: Check that the channel is in the allowlist. Also verify the bot has been re-authorized if you recently rotated API keys.
- **Slow responses**: Slack has a 3-second timeout for initial acknowledgment. If your knowledge base is large, the bot sends a "thinking..." message first, then updates with the answer.
- **Duplicate responses**: This can happen if the bot is installed in multiple Slack workspaces pointing to the same Stratify Labs organization. Remove duplicate installations.

## Zendesk Integration

### Setup
1. Go to Settings > Integrations > Zendesk
2. Enter your Zendesk subdomain (e.g., yourcompany.zendesk.com)
3. Authenticate with an admin account
4. Choose sync direction: one-way (Zendesk → Stratify Labs) or two-way

### Sync Options
- **Articles**: Sync Help Center articles to a collection. Updates are synced every 15 minutes.
- **Tickets**: Sync resolved tickets (with PII redacted) to build a knowledge base from real customer interactions. Only tickets tagged with "knowledge-base" are synced.
- **Macros**: Sync agent macros as knowledge snippets.

### Agent Assist
When two-way sync is enabled, Stratify Labs can provide suggested answers directly in the Zendesk agent interface:

1. Agent opens a ticket
2. Stratify Labs sidebar shows top 3 relevant answers from your knowledge base
3. Agent can insert a suggestion directly into their reply with one click
4. Usage analytics track which suggestions agents use vs. ignore

### Troubleshooting Zendesk
- **Articles not syncing**: Ensure articles are published (draft articles are not synced). Check that the Zendesk API token hasn't expired.
- **PII in synced tickets**: The PII redaction engine removes emails, phone numbers, and names. For custom PII patterns (e.g., account numbers), configure regex patterns at Settings > Integrations > Zendesk > PII Rules.
- **Sync delays**: The default sync interval is 15 minutes. Enterprise plans can configure real-time sync via webhooks.

## Confluence Integration

### Setup
1. Go to Settings > Integrations > Confluence
2. Choose Confluence Cloud or Confluence Server/Data Center
3. For Cloud: OAuth 2.0 authentication
4. For Server: Provide base URL and personal access token
5. Select which spaces to sync

### Sync Behavior
- Pages are synced with their full content including tables and formatted text
- Attachments (PDF, Word) are extracted and indexed
- Page hierarchy is preserved in metadata (parent page, space, labels)
- Deleted pages are removed from Stratify Labs within 1 hour
- Sync frequency: every 30 minutes (configurable to 5 minutes on Enterprise plans)

### Permissions
Stratify Labs respects Confluence space permissions. If a user doesn't have access to a Confluence space, search results from that space are filtered out. This requires the "Permission Sync" option to be enabled (Professional and Enterprise plans only).

## Webhook Integration

For custom integrations, Stratify Labs supports inbound and outbound webhooks.

### Inbound Webhooks
Receive documents from any system:

```bash
curl -X POST https://api.acmesaas.com/v2/webhooks/ingest \
  -H "Authorization: Bearer ak_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "support-docs",
    "text": "Document content here",
    "metadata": {"source": "custom-app", "category": "faq"}
  }'
```

### Outbound Webhooks
Get notified when events occur in Stratify Labs:

Available events:
- `query.completed` — Triggered after every search query (includes query, results, latency)
- `document.ingested` — Triggered when new documents are added
- `collection.updated` — Triggered when collection settings change
- `alert.triggered` — Triggered when usage alerts fire

Configure at Settings > Integrations > Webhooks > Add Endpoint.

Each webhook delivery includes:
- HMAC-SHA256 signature in the `X-Stratify Labs-Signature` header for verification
- Event type in the `X-Stratify Labs-Event` header
- Delivery ID in the `X-Stratify Labs-Delivery` header
- Automatic retries (3 attempts with exponential backoff) on 5xx responses

## API Gateway Compatibility

Stratify Labs works behind any API gateway. Common setups:

### AWS API Gateway
- Use the REST API endpoint as the upstream
- Configure API key authentication as a custom authorizer
- Set timeout to at least 30 seconds

### Kong
- Add Stratify Labs as a service with the API endpoint
- Use the key-auth plugin and pass the API key in the `Authorization` header
- Enable the rate-limiting plugin to stay within your plan limits

### Nginx
```nginx
location /knowledge/ {
    proxy_pass https://api.acmesaas.com/v2/;
    proxy_set_header Authorization "Bearer $acme_api_key";
    proxy_read_timeout 30s;
}
```

## Integration Limits

| Integration | Starter | Professional | Enterprise |
|------------|---------|-------------|------------|
| Slack workspaces | 1 | 3 | Unlimited |
| Zendesk instances | 1 | 2 | Unlimited |
| Confluence spaces | 5 | 25 | Unlimited |
| Webhook endpoints | 3 | 10 | Unlimited |
| Sync frequency | 30 min | 15 min | 5 min / real-time |
