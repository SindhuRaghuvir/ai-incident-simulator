# Support Policy, Severity Levels and Escalation

## How Support Works

### How do I open a support ticket?
- **Email**: support@stratifylabs.io (creates a ticket automatically)
- **Dashboard**: click **Help > New Ticket** (Professional and Enterprise also have live chat)
- **Phone**: Enterprise customers have a 24/7 phone line for Severity 1 issues, listed in your order form

Opening a ticket from the dashboard is fastest because it attaches your organization ID and recent error logs automatically.

### What information should I include in a ticket?
The fastest tickets to resolve include:
1. **What you expected vs. what happened** — one or two sentences each
2. **Request IDs** from the `X-Request-Id` header of failing requests
3. **Timestamps** with time zone (UTC preferred)
4. **Error codes and full error messages**
5. **Scope** — one user or everyone? One collection or all? Since when?
6. **What changed** — recent deploys, key rotations, integration changes, or new documents

Never include a full API key. The first 10 characters (the prefix) are enough for us to identify it.

---

## Severity Levels

### How is the severity of my ticket decided?
You set the initial severity when you open the ticket. Our support engineers may adjust it based on impact, and will tell you if they do.

| Severity | Definition | Example |
|----------|------------|---------|
| **Sev 1 — Critical** | Production is down or unusable for all users, no workaround | All API requests return 503 |
| **Sev 2 — High** | Major feature broken or badly degraded, workaround is painful | Zendesk sync stopped; answers 10x slower than normal |
| **Sev 3 — Medium** | Partial or minor impact, a reasonable workaround exists | One document fails to ingest |
| **Sev 4 — Low** | Questions, how-to requests, feature requests | "How do I set up SSO?" |

### What are the response times for each severity?
First-response targets by plan:

| Severity | Starter | Professional | Enterprise |
|----------|---------|-------------|------------|
| Sev 1 | 24 hours | 2 hours | 1 hour, 24/7 |
| Sev 2 | 48 hours | 4 hours | 2 hours, 24/7 |
| Sev 3 | 48 hours | 1 business day | 4 business hours |
| Sev 4 | 3 business days | 2 business days | 1 business day |

Free Trial accounts are supported through the community forums on a best-effort basis. Business hours are Monday–Friday, 6 AM – 6 PM Pacific, excluding US holidays. Sev 1 and Sev 2 for Enterprise are handled around the clock.

### What counts as "first response"?
A first response is a reply from a human support engineer who has reviewed your ticket — not an automated acknowledgment. Resolution time depends on the issue, but for Sev 1 and Sev 2 we provide updates at least every 2 hours until it is resolved or downgraded.

---

## Escalation

### My ticket isn't moving — how do I escalate?
1. **Reply on the ticket** with "Please escalate" and the business impact (for example, "500 customers can't get answers in our help widget"). This alerts the support team lead.
2. **Professional**: if there's no update within the response target, email escalations@stratifylabs.io with the ticket number.
3. **Enterprise**: contact your dedicated support engineer or Technical Account Manager (TAM) directly. For Sev 1, call the 24/7 phone line.

Escalation brings in senior engineers and management visibility. It does not change the technical facts of the issue, so a clear description of impact is the most useful thing you can add.

### When should I raise a ticket to Sev 1?
Raise to Sev 1 when production is unusable for your users and there is no workaround — for example, every query is failing or returning errors. Partial slowness, a single failing integration, or an issue in a test environment is Sev 2 or lower. Accurate severity helps us get the right engineers on the right problems fastest.

---

## Incidents and Communication

### How will I know if there's a platform-wide incident?
Check **status.stratifylabs.io**, which shows real-time health for the API, dashboard, ingestion pipeline, and each integration. You can subscribe to updates by email, SMS, Slack, or RSS. During an incident we post an update at least every 2 hours.

If you open a ticket about an issue that is already a known incident, your ticket will be linked to it and you'll be notified when it's resolved — you don't need to keep checking.

### Will I get a root cause analysis (RCA) after an incident?
Yes. For any Sev 1 platform incident we publish a post-incident report within **5 business days**. It covers the timeline, customer impact, root cause, how it was resolved, and the specific changes we're making to prevent it from happening again. Enterprise customers can request a private RCA review call with their TAM.

### Do SLA breaches earn service credits?
Yes, for paid plans. If monthly uptime falls below your plan's SLA (Starter 99.5%, Professional 99.9%, Enterprise 99.99%), you can request a credit within 30 days of the end of the affected month:

| Monthly uptime below SLA by | Credit |
|-----------------------------|--------|
| Up to 0.5% | 10% of monthly fee |
| 0.5% – 1.0% | 25% of monthly fee |
| More than 1.0% | 50% of monthly fee |

Email billing@stratifylabs.io with the incident dates. Scheduled maintenance announced at least 72 hours in advance does not count against uptime.

---

## Enterprise Support

### What does the Enterprise support package include?
- A **dedicated support engineer** who knows your configuration
- A named **Technical Account Manager (TAM)** for onboarding, architecture reviews, and quarterly business reviews
- 24/7 coverage for Sev 1 and Sev 2
- A shared Slack channel with our support team
- Proactive alerts when your usage, error rates, or latency look abnormal
- Advance notice of maintenance and model changes
