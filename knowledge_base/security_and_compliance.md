# Stratify Labs Platform - Security and Compliance

## Security Architecture

### Data Encryption

All data is encrypted at rest and in transit:

- **In transit**: TLS 1.3 for all API communications. We do not support TLS 1.1 or earlier. Certificate pinning is available for mobile SDK integrations.
- **At rest**: AES-256-GCM encryption for all stored documents and embeddings. Encryption keys are managed through AWS KMS with automatic rotation every 90 days.
- **Search queries**: Queries are encrypted in transit and are not logged by default. Enable query logging explicitly if needed for analytics (Settings > Security > Query Logging).

### Network Security

- All API endpoints are served from behind AWS CloudFront with DDoS protection
- IP allowlisting is available on Professional and Enterprise plans (Settings > Security > IP Allowlist)
- VPC peering is available for Enterprise customers to keep traffic within AWS private networks
- All infrastructure runs in SOC 2 certified AWS data centers

### Authentication

Stratify Labs supports multiple authentication methods:

**API Key Authentication** (all plans):
Pass your API key in the Authorization header:
```
Authorization: Bearer ak_live_your_key_here
```

**OAuth 2.0** (Professional and Enterprise):
For user-facing applications, use OAuth 2.0 authorization code flow:
1. Register your application at Settings > Security > OAuth Apps
2. Redirect users to `https://auth.acmesaas.com/authorize`
3. Exchange the authorization code for an access token
4. Access tokens expire after 1 hour; use refresh tokens for long-lived sessions

**SAML 2.0 SSO** (Professional and Enterprise):
Configure SSO for your organization:
1. Go to Settings > Security > SSO
2. Enter your Identity Provider metadata URL
3. Map IdP attributes to Stratify Labs roles
4. Optionally enforce SSO (disable password login)

Supported Identity Providers: Okta, Azure AD, Google Workspace, OneLogin, PingFederate.

**Multi-Factor Authentication** (all plans):
MFA can be enabled per user or enforced organization-wide:
- TOTP (Google Authenticator, Authy)
- SMS (not recommended for high-security environments)
- Hardware keys (YubiKey, FIDO2)

To enforce MFA for all members: Settings > Security > Authentication > Require MFA.

### Access Control

Role-based access control (RBAC) is available on all plans with three built-in roles (Owner, Admin, Member). Enterprise plans support custom roles with granular permissions:

- `collections:read` — View collection contents
- `collections:write` — Add/modify/delete documents
- `collections:admin` — Manage collection settings
- `analytics:read` — View usage analytics
- `analytics:export` — Export analytics data
- `billing:manage` — View and modify billing settings
- `members:manage` — Invite/remove team members
- `apikeys:manage` — Create/rotate/delete API keys
- `integrations:manage` — Configure third-party integrations

Custom roles are created at Settings > Security > Roles.

## Compliance

### SOC 2 Type II

Stratify Labs maintains SOC 2 Type II certification, audited annually by an independent firm. Our SOC 2 report covers:
- Security
- Availability
- Confidentiality
- Processing Integrity

Request our latest SOC 2 report at security@acmesaas.com (NDA required).

### GDPR

Stratify Labs is GDPR compliant for EU customers:

- **Data Processing Agreement (DPA)**: Available at acmesaas.com/legal/dpa. All Professional and Enterprise customers are automatically covered.
- **Data residency**: EU customers on Professional and Enterprise plans can choose EU-West (Ireland) as their primary data region. Data never leaves the selected region.
- **Right to erasure**: Delete all data associated with an end user via the API:
  ```
  DELETE /v2/data-subjects/{identifier}
  ```
  This removes all documents, queries, and analytics associated with the identifier within 72 hours.
- **Data portability**: Export all organization data in JSON format from Settings > Security > Data Export.
- **Sub-processors**: Our current sub-processor list is published at acmesaas.com/legal/sub-processors. We notify customers 30 days before adding new sub-processors.

### HIPAA

HIPAA compliance is available for Enterprise customers with a signed Business Associate Agreement (BAA). HIPAA-compliant configurations include:
- Dedicated infrastructure
- Enhanced audit logging
- Automatic PHI detection and redaction
- 7-year audit log retention
- No data sharing with sub-processors without BAA chain

Contact sales@acmesaas.com for HIPAA-compliant deployment.

### Data Retention

Default retention policies:
| Data Type | Retention Period |
|-----------|-----------------|
| Documents | Until deleted by user |
| Embeddings | Until source document is deleted |
| Query logs | 90 days (configurable) |
| Analytics | 1 year |
| Audit logs | 2 years (7 years for HIPAA) |
| Backups | 30 days |

Enterprise customers can configure custom retention policies per collection.

## Incident Response

### Reporting Vulnerabilities

Report security vulnerabilities to security@acmesaas.com. We follow responsible disclosure:
- Acknowledgment within 24 hours
- Assessment within 72 hours
- Fix timeline communicated within 1 week
- We do not pursue legal action against good-faith security researchers

### Bug Bounty Program

We operate a private bug bounty program through HackerOne. Bounties range from $100 to $10,000 depending on severity. Contact security@acmesaas.com for an invitation.

### Incident Communication

During security incidents:
1. Initial notification via email and status page (status.acmesaas.com) within 1 hour of detection
2. Updates every 2 hours until resolved
3. Post-incident report within 5 business days
4. Root cause analysis and preventive measures shared with affected customers

### Audit Logging

All API actions are logged with:
- Timestamp (UTC)
- Actor (user ID, API key prefix)
- Action performed
- Resource affected
- Source IP address
- User agent

Access audit logs at Settings > Security > Audit Log or via the API:
```
GET /v2/audit-log?start=2024-01-01&end=2024-01-31
```

Audit logs can be streamed to external SIEM systems (Splunk, Datadog, Sumo Logic) on Enterprise plans.

## Security Best Practices

1. **Rotate API keys regularly**: We recommend rotation every 90 days. Use the 24-hour grace period to update all consumers.
2. **Use least-privilege access**: Create separate API keys for different services, each with only the permissions needed.
3. **Enable MFA**: Enforce MFA for all organization members, especially Owners and Admins.
4. **Monitor audit logs**: Set up alerts for unusual activity (bulk deletions, new API key creation, role changes).
5. **Use IP allowlisting**: Restrict API access to known IP ranges if your infrastructure has static IPs.
6. **Keep SDKs updated**: We patch security issues in SDK releases. Enable Dependabot or similar tools for automatic update PRs.
7. **Separate environments**: Use different organizations or API keys for development, staging, and production. Never use production data in development.
