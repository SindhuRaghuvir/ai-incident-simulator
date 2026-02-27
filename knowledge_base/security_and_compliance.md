# Security and Compliance

## Data Security

### Is my data encrypted?
Yes. All data is encrypted both in transit and at rest:

- **In transit**: All communication uses TLS 1.3. We do not support TLS 1.1 or earlier.
- **At rest**: Documents and embeddings are encrypted with AES-256-GCM. Encryption keys are managed through AWS Key Management Service (KMS) and rotated automatically every 90 days.

Your search queries are also encrypted in transit and are **not** logged by default. If you want query logging for analytics purposes, you can enable it explicitly at **Settings > Security > Query Logging**.

### Where is my data stored?
By default, data is stored in US-East AWS data centers.

- **Professional and Enterprise plans** can choose EU-West (Ireland) as their primary data region. If you select EU-West, your data never leaves that region.
- **Enterprise plans** have access to global deployment options and custom data residency configurations.

All infrastructure runs in SOC 2 certified AWS data centers.

### Who can access my data?
Only authorized members of your organization can access your data through the platform. Stratify Labs staff do not access customer data except when required to provide support (and only with your permission). Access is logged in the audit trail.

---

## Authentication and Access Control

### How do I enable Multi-Factor Authentication (MFA)?
To enable MFA for your own account:
1. Go to **Settings > Security > Authentication**
2. Click "Enable MFA"
3. Choose your method: authenticator app (Google Authenticator, Authy), SMS, or hardware key (YubiKey, FIDO2)
4. Scan the QR code or follow the setup instructions
5. Enter the verification code to confirm setup

To require MFA for everyone in your organization, go to **Settings > Security > Authentication > Require MFA**. Once enforced, members must set up MFA before they can log in again.

Note: SMS is supported but not recommended for high-security environments. Authenticator apps and hardware keys are more secure.

### Does Stratify Labs support Single Sign-On (SSO)?
Yes, SSO is available on **Professional and Enterprise plans**. We support:
- SAML 2.0
- OIDC (OpenID Connect)

Compatible identity providers include Okta, Azure AD, Google Workspace, OneLogin, and PingFederate.

To configure SSO:
1. Go to **Settings > Security > SSO**
2. Enter your Identity Provider metadata URL
3. Map your IdP attributes to Stratify Labs roles
4. Optionally enforce SSO (this disables password-based login for your org)

### Can I restrict which IP addresses can access the API?
Yes — IP allowlisting is available on **Professional and Enterprise plans**. Go to **Settings > Security > IP Allowlist** to add approved IP ranges. Requests from unlisted IPs will be rejected.

### What roles and permissions are available?
All plans include three built-in roles:
- **Owner** — Full access including billing and member management
- **Admin** — Manages API keys, integrations, and analytics. No billing access.
- **Member** — Uses the platform and generates personal API keys

**Enterprise plans** support custom roles with granular permission controls, including specific access to collections, analytics, billing, integrations, and more. Custom roles are created at **Settings > Security > Roles**.

---

## Compliance

### Is Stratify Labs SOC 2 certified?
Yes. Stratify Labs maintains **SOC 2 Type II** certification, audited annually by an independent firm. The audit covers Security, Availability, Confidentiality, and Processing Integrity.

To request our latest SOC 2 report, email security@stratifylabs.io. An NDA is required.

### Is Stratify Labs GDPR compliant?
Yes. For EU customers:

- **Data Processing Agreement (DPA)**: All Professional and Enterprise customers are automatically covered. You can find the DPA at stratifylabs.io/legal/dpa.
- **Data residency**: EU customers on Professional and Enterprise plans can select EU-West (Ireland) as their data region. Data never leaves that region.
- **Right to erasure**: We can delete all data associated with a specific end user within 72 hours upon request.
- **Data portability**: Export all your organization's data in JSON format from **Settings > Security > Data Export**.
- **Sub-processors**: Our sub-processor list is published at stratifylabs.io/legal/sub-processors. We notify customers 30 days before adding new sub-processors.

### Does Stratify Labs support HIPAA compliance?
HIPAA-compliant configurations are available for **Enterprise customers** with a signed Business Associate Agreement (BAA). This includes dedicated infrastructure, enhanced audit logging, automatic PHI detection and redaction, and 7-year audit log retention.

Contact support@stratifylabs.io to discuss HIPAA-compliant deployment options.

### What happens to my data if I cancel my account?
After cancellation, your data is retained for **30 days**. During this window, you can export everything from **Settings > Security > Data Export**. After 30 days, all data — documents, embeddings, query logs, and audit logs — is permanently deleted.

If you reactivate within the 30-day window, your data is fully restored.

---

## Audit Logging

### Does Stratify Labs keep an audit log of account activity?
Yes. All API actions are logged with:
- Timestamp (UTC)
- Who performed the action (user ID or API key prefix)
- What action was taken
- Which resource was affected
- Source IP address

You can view audit logs at **Settings > Security > Audit Log**. Enterprise plans can stream audit logs to external SIEM systems (Splunk, Datadog, Sumo Logic).

### How long are audit logs retained?
- Standard: 2 years
- HIPAA-compliant configurations: 7 years

---

## Reporting Security Issues

### How do I report a security vulnerability?
We take security reports seriously and will respond promptly. Here's how to reach us:

1. **Email**: Send details to security@stratifylabs.io
2. **What to include**: Description of the vulnerability, steps to reproduce, potential impact, and any relevant screenshots or logs
3. **Response timeline**:
   - Acknowledgment within **24 hours**
   - Assessment and severity rating within **72 hours**
   - Fix timeline communicated within **1 week**

We follow responsible disclosure practices and do not pursue legal action against good-faith security researchers.

### Is there a bug bounty program?
Yes. We run a private bug bounty program through HackerOne. Bounties range from $100 to $10,000 depending on severity. Email security@stratifylabs.io to request an invitation.

### How will I be notified during a security incident?
If a security incident affects your account, we will:
1. Send an email and post to our status page (status.stratifylabs.io) within **1 hour** of detection
2. Provide updates every 2 hours until the issue is resolved
3. Publish a post-incident report within **5 business days**, including root cause and preventive measures

---

## Data Retention Reference

| Data Type | Default Retention |
|-----------|------------------|
| Documents | Until deleted by user |
| Embeddings | Until source document is deleted |
| Query logs | 90 days (configurable) |
| Analytics | 1 year |
| Audit logs | 2 years (7 years for HIPAA) |
| Backups | 30 days |

Enterprise customers can configure custom retention policies per collection.
