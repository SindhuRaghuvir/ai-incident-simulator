# Stratify Labs Platform - Billing and Plans

## Plan Overview

Stratify Labs offers four tiers designed to scale with your business:

### Free Trial
- 14-day trial period, no credit card required
- 1,000 API requests per day
- 1 collection, up to 10,000 documents
- Community support only
- Data retained for 30 days after trial ends

### Starter ($49/month)
- 50,000 API requests per day
- 5 collections, up to 100,000 documents per collection
- Email support with 48-hour response time
- Basic analytics dashboard
- 99.5% uptime SLA
- Single region deployment (US-East)

### Professional ($199/month)
- 500,000 API requests per day
- Unlimited collections, up to 1,000,000 documents per collection
- Priority email and chat support with 4-hour response time
- Advanced analytics with custom reports
- 99.9% uptime SLA
- Multi-region deployment (US-East, US-West, EU-West)
- SSO integration (SAML 2.0, OIDC)
- Audit logging

### Enterprise (Custom pricing)
- Unlimited API requests (fair use policy applies)
- Unlimited collections and documents
- Dedicated support engineer with 1-hour response time
- Custom analytics and reporting
- 99.99% uptime SLA
- Global deployment with data residency options
- SOC 2 Type II compliance
- Custom data retention policies
- On-premises deployment option
- Dedicated infrastructure (no noisy neighbors)

## Billing Cycle

All plans are billed monthly. Annual billing is available for Starter and Professional plans with a 20% discount:
- Starter Annual: $470/year (saves $118)
- Professional Annual: $1,910/year (saves $478)

Billing occurs on the same day each month as your initial subscription. If you signed up on the 15th, you'll be billed on the 15th of each month.

## Usage-Based Charges

Beyond the included API requests, additional usage is charged as follows:

| Resource | Starter | Professional | Enterprise |
|----------|---------|-------------|------------|
| Additional API requests | $0.002/request | $0.001/request | Custom |
| Additional storage | $0.10/GB/month | $0.05/GB/month | Custom |
| Embedding generation | $0.0001/document | $0.00005/document | Custom |
| Priority processing | Not available | $0.005/request | Included |

Usage charges are calculated daily and added to your monthly invoice.

## Payment Methods

We accept:
- Credit cards (Visa, Mastercard, American Express)
- ACH bank transfers (US only, Professional and Enterprise plans)
- Wire transfers (Enterprise plans, minimum $1,000)
- Purchase orders (Enterprise plans only, NET 30 terms)

## Invoice and Receipts

Invoices are generated on your billing date and sent to the billing email address on file. You can also download invoices from Settings > Billing > Invoice History.

Each invoice includes:
- Base subscription cost
- Usage-based charges broken down by resource type
- Any applicable taxes
- Credits or adjustments

## Upgrading and Downgrading

### Upgrading
Upgrades take effect immediately. You'll be charged a prorated amount for the remainder of your current billing cycle. New rate limits and features are available instantly.

### Downgrading
Downgrades take effect at the start of your next billing cycle. You'll retain access to higher-tier features until then. Important: if your current usage exceeds the lower tier's limits (e.g., you have 8 collections but are downgrading to Starter which allows 5), you'll need to reduce your usage before the downgrade takes effect. Otherwise, the downgrade will be blocked.

### Cancellation
You can cancel at any time from Settings > Billing > Cancel Subscription. After cancellation:
- Your data is retained for 30 days
- You can export all data during this period
- API keys are deactivated immediately
- After 30 days, all data is permanently deleted

To reactivate within the 30-day window, contact support@acmesaas.com.

## Refund Policy

- Full refund within 7 days of initial subscription (first-time customers only)
- Pro-rated refunds for service outages exceeding SLA commitments
- No refunds for usage-based charges already consumed
- Enterprise customers: refer to your service agreement for refund terms

## Tax Information

Prices listed are exclusive of taxes. Applicable taxes (sales tax, VAT, GST) are added based on your billing address. To provide a tax exemption certificate, upload it at Settings > Billing > Tax Info.

For EU customers: VAT is charged based on your country of residence. Provide a valid VAT ID to apply reverse charge mechanism.

## Cost Optimization Tips

1. **Use test keys for development**: Test keys (ak_test_) don't count toward your usage limits.
2. **Cache frequent queries**: If the same queries are made repeatedly, implement client-side caching.
3. **Batch ingestion**: Batch API calls are more efficient than individual calls. Use ingest_batch() for bulk operations.
4. **Monitor usage**: Set up usage alerts at Settings > Billing > Alerts to get notified at 50%, 75%, and 90% of your included limits.
5. **Right-size collections**: Archive old or unused documents to reduce storage costs.
6. **Choose the right chunking**: Smaller chunks mean more embeddings to generate and store. Use larger chunks when precision isn't critical.
