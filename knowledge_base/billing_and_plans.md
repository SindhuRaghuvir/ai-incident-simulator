# Billing and Plans

## Choosing the Right Plan

### Which plan is right for me?
Here's a quick breakdown to help you decide:

- **Free Trial** — Best if you're just exploring. 14 days, no credit card needed. Limited to 1,000 API requests/day and 1 collection.
- **Starter ($49/month)** — Good for small teams or early-stage products. 50,000 API requests/day, 5 collections, email support.
- **Professional ($199/month)** — For growing teams that need more scale, SSO, multi-region deployment, and faster support response. 500,000 API requests/day, unlimited collections.
- **Enterprise (custom pricing)** — For large organizations with compliance requirements, dedicated infrastructure, or high-volume needs. Includes SOC 2 Type II, HIPAA options, and a dedicated support engineer.

Not sure? Email us at support@stratifylabs.io and we'll help you pick the right fit.

### What's included in the Free Trial?
The free trial is 14 days with no credit card required. You get:
- 1,000 API requests/day
- 1 collection (up to 10,000 documents)
- Community support

Your data is retained for 30 days after the trial ends. After that, it's permanently deleted unless you've upgraded to a paid plan.

### Is there annual billing? Can I save money?
Yes. Annual billing is available for Starter and Professional plans at a 20% discount:
- **Starter Annual**: $470/year (saves $118 vs. monthly)
- **Professional Annual**: $1,910/year (saves $478 vs. monthly)

To switch to annual billing, go to **Settings > Billing** and select "Switch to Annual."

---

## Understanding Your Bill

### What does my monthly charge include?
Your invoice has two parts:

1. **Base subscription** — the flat monthly fee for your plan
2. **Usage-based charges** — anything you use beyond your plan's included limits

Usage charges by plan:

| Resource | Starter | Professional | Enterprise |
|----------|---------|-------------|------------|
| Extra API requests | $0.002/request | $0.001/request | Custom |
| Extra storage | $0.10/GB/month | $0.05/GB/month | Custom |
| Embedding generation | $0.0001/document | $0.00005/document | Custom |
| Priority processing | Not available | $0.005/request | Included |

Usage charges are calculated daily and added to your monthly invoice.

### Where can I find my invoice?
Go to **Settings > Billing > Invoice History**. Invoices are also emailed to the billing address on your account on your billing date each month.

Each invoice shows:
- Base subscription cost
- Usage-based charges by resource type
- Applicable taxes
- Any credits or adjustments

### How do I update my billing email or payment method?
Go to **Settings > Billing** to update your payment method or billing contact email. We accept:
- Credit cards (Visa, Mastercard, American Express)
- ACH bank transfers (US only — Starter and above)
- Wire transfers (Enterprise, minimum $1,000)
- Purchase orders (Enterprise only, NET 30 terms)

### I was charged unexpectedly — what happened?
Unexpected charges are usually caused by one of these:

1. **Usage overage** — You exceeded your plan's included API requests, storage, or document limit. Check **Settings > Billing > Usage** to see your usage breakdown.
2. **Annual renewal** — If you're on an annual plan, you were charged the full year upfront on your renewal date.
3. **Plan upgrade proration** — When you upgrade mid-cycle, you're charged a prorated amount for the remainder of the billing period.

If none of these explain the charge, contact support@stratifylabs.io with your invoice number and we'll look into it right away.

### How do I set up usage alerts to avoid surprise charges?
Go to **Settings > Billing > Alerts** and set thresholds at 50%, 75%, and 90% of your included limits. We'll email you when you approach those thresholds.

---

## Upgrading and Downgrading

### How do I upgrade my plan?
Go to **Settings > Billing > Change Plan** and select the plan you want. Upgrades take effect immediately — you'll have access to higher limits and features right away. You'll be charged a prorated amount for the remainder of your current billing cycle.

### How do I downgrade my plan?
Go to **Settings > Billing > Change Plan** and select the lower tier. Downgrades take effect at the start of your next billing cycle — you keep current features until then.

**Important:** If your usage exceeds the lower tier's limits (for example, you have 8 collections but the Starter plan allows 5), you'll need to reduce your usage before the downgrade kicks in. Otherwise the system will block the downgrade until you're within limits.

### What happens to my data if I downgrade?
Your data is safe. The downgrade only affects your limits going forward. You won't lose documents unless your collections or document count exceeds what the new plan allows — in that case, you'll be prompted to reduce usage before the change takes effect.

---

## Cancellation and Refunds

### How do I cancel my subscription?
You can cancel anytime at **Settings > Billing > Cancel Subscription**. There are no cancellation fees. After you cancel:

- Your data is retained for **30 days** — you can export everything during this window
- Your API keys are deactivated immediately
- After 30 days, all data is permanently and irreversibly deleted

If you change your mind within the 30-day window, contact support@stratifylabs.io and we can reactivate your account.

### Can I get a refund?
- **New customers**: Full refund within 7 days of your first subscription (one-time, for first-time customers only).
- **Service outages**: Pro-rated refunds for outages that exceed your plan's SLA commitments.
- **Usage charges**: No refunds for API requests, storage, or processing already consumed.
- **Enterprise customers**: Refund terms are defined in your service agreement.

To request a refund, email support@stratifylabs.io with your account name and invoice number. We'll get back to you within 1 business day.

### How do I export my data before canceling?
Go to **Settings > Security > Data Export** to download all your organization's data in JSON format. We recommend doing this before your account is fully cancelled — exported data includes your documents, collections, and metadata.

---

## Taxes

### Do prices include taxes?
No — listed prices are exclusive of taxes. Applicable taxes (sales tax, VAT, GST) are calculated based on your billing address and added to your invoice.

To apply a tax exemption, upload your certificate at **Settings > Billing > Tax Info**.

EU customers: VAT is applied based on your country of residence. If you have a valid VAT ID, add it to your billing settings to apply the reverse charge mechanism.
