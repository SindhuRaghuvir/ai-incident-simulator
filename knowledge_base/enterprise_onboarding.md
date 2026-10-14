# Enterprise Onboarding and Go-Live

## Onboarding Overview

### What does Enterprise onboarding look like?
Enterprise onboarding typically takes **4–6 weeks** and is led by your Technical Account Manager (TAM) together with a solutions engineer.

| Phase | Weeks | What happens |
|-------|-------|--------------|
| **Kickoff** | 1 | Confirm goals, success metrics, stakeholders, and timeline |
| **Setup** | 1–2 | SSO, roles, data region, integrations, first collections |
| **Content and tuning** | 2–4 | Ingest content, build an evaluation set, tune retrieval settings |
| **Pilot** | 4–5 | Limited rollout to a pilot group, feedback, fixes |
| **Go-live** | 5–6 | Production launch, monitoring, hypercare |

### Who should attend the kickoff call?
- An **executive sponsor** who owns the business goal
- A **technical owner** who will manage the integration and API keys
- A **content owner** responsible for the knowledge base itself
- A **security or IT contact** for SSO, IP allowlisting, and compliance review

Projects that are missing a content owner are the most likely to stall, because answer quality depends on content more than on configuration.

### How do we define success?
In the kickoff we agree on 2–3 measurable success metrics, written into a shared **success plan**. Common examples:
- **Ticket deflection**: 25% of incoming support questions answered without an agent
- **Answer accuracy**: 85% or higher on your evaluation set
- **Agent efficiency**: 20% reduction in average handle time with Zendesk Agent Assist
- **Adoption**: 60% of the pilot group using the assistant weekly

---

## Setup Checklist

### What do we need to have ready before setup?
1. **SSO details** — your identity provider metadata URL (Okta, Azure AD, Google Workspace, and others are supported)
2. **Data region decision** — US-East or EU-West. This cannot be changed later without a migration.
3. **Content inventory** — where your knowledge lives (Zendesk, Confluence, file shares) and roughly how many documents
4. **Access model** — which teams should see which content; this decides your collection and role structure
5. **Security review documents** — request our SOC 2 Type II report from security@stratifylabs.io (NDA required). HIPAA customers also need a signed BAA.

### How should we structure our collections?
Group content by **who searches it**, not by where it came from. For example:
- `customer-help` — public help articles for your customer-facing chatbot
- `agent-internal` — internal macros and resolved tickets for support agents
- `engineering-runbooks` — restricted to on-call engineers

Mixing internal and customer-facing content in one collection is the most common onboarding mistake. It risks internal notes appearing in customer answers.

---

## Pilot and Go-Live

### How do we run a good pilot?
- Choose a pilot group of **20–50 real users** who ask real questions daily
- Run for at least **2 weeks** so you see a realistic range of questions
- Review **Analytics > Unanswered Questions** and thumbs-down feedback twice a week with your TAM
- Fix content gaps first, then tune settings

### What is the go-live readiness checklist?
- Evaluation set accuracy meets the target in the success plan
- Fallback message reviewed and approved (and it routes users to a human)
- Production keys (`ak_live_`) created and stored in a secrets manager, test keys removed from production code
- Retry logic with exponential backoff and client timeouts in place
- Monitoring and alerting set up on error rate and p95 latency
- Status page subscription set up for your on-call team
- Support escalation path shared with your team (see Support Policy)
- TAM notified of launch date and expected traffic at least 5 business days ahead

### What is hypercare?
For the first **2 weeks after go-live**, your account is in hypercare: your TAM and support engineer monitor your error rates, latency, and unanswered-question trends daily and reach out proactively if anything looks off. Hypercare ends with a go-live retrospective.

---

## Ongoing Relationship

### What happens in a Quarterly Business Review (QBR)?
Each quarter your TAM walks through:
- Progress against the success plan metrics
- Usage trends and cost forecast against your contract
- Incidents and support tickets from the quarter, with any RCAs
- Upcoming product changes and model deprecations that affect you
- Recommendations — new use cases, content gaps, or settings changes

QBRs are the right place to raise roadmap requests and renewal planning.

### What is an account health check?
Twice a year (or on request) your TAM runs a configuration review covering key hygiene (old or unused keys), role assignments, integration sync health, retrieval settings, and content freshness. You get a short report with prioritized recommendations.

### Who do I contact for what after onboarding?

| Need | Contact |
|------|---------|
| Production issue or error | Dedicated support engineer / support@stratifylabs.io |
| Sev 1 outage | 24/7 Enterprise phone line |
| Architecture or best-practice advice | Your TAM |
| Contract, billing, or seat changes | Your account executive / billing@stratifylabs.io |
| Security questionnaire or SOC 2 report | security@stratifylabs.io |
