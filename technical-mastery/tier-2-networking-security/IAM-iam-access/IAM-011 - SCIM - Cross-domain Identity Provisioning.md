---
id: IAM-011
title: "SCIM - Cross-domain Identity Provisioning"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-006, IAM-007
used_by: IAM-018, IAM-019, IAM-024
related: IAM-007, IAM-009, IAM-019
tags:
  - iam
  - security
  - identity
  - protocol
  - foundational
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/iam/scim-cross-domain-identity-provisioning/
---

⚡ TL;DR - SCIM (System for Cross-domain Identity
Management, RFC 7642-7644) is a REST API standard for
automating user and group provisioning across systems.
Instead of every SaaS app having a different user import
format, SCIM defines a common REST API: POST /Users to
create, PATCH /Users/{id} to update, DELETE /Users/{id}
to deprovision. Okta, Azure AD, and most enterprise IdPs
use SCIM to automate the JML lifecycle across dozens of
connected apps.

---

### 🔥 The Problem This Solves

Before SCIM, every SaaS application managed user accounts
independently. Adding a new employee meant:

- GitHub: invite via email link, user accepts, joins org
- Salesforce: admin manually creates user record
- Jira: admin adds user from menu
- Workday: HR enters user manually
- Slack: invite email, user accepts

Ten apps = ten manual steps by different admins. Result:

- Day 1 onboarding: new hire sits at desk with no access
  because 6 of 10 accounts are not created yet
- Day last (offboarding): accounts in 3 of 10 apps
  forgotten because the IT ticket only listed 7 apps

SCIM standardizes the user management API across all
SaaS apps. Connect each app to the IdP via SCIM once.
After that, user lifecycle events in the IdP
automatically propagate to all apps.

---

### 📘 Textbook Definition

SCIM (System for Cross-domain Identity Management) is
an HTTP-based REST protocol (RFC 7642, 7643, 7644,
published 2015) for managing identities across domain
boundaries. It defines:

**Resource types:**
- `/Users` - individual user accounts
- `/Groups` - groups with member lists
- `/ServiceProviderConfig` - capabilities of the SCIM server
- `/Schemas` - attribute definitions

**Core User attributes:** id, userName, name, emails,
phoneNumbers, active (boolean), externalId (IdP's user ID)

**Enterprise extension schema:** employeeNumber,
organization, department, division, manager

**HTTP operations:**
- `GET /Users` - list users (with filter support)
- `GET /Users/{id}` - get single user
- `POST /Users` - create user
- `PUT /Users/{id}` - full update
- `PATCH /Users/{id}` - partial update
- `DELETE /Users/{id}` - delete user
- Same operations for `/Groups`

**SCIM client (provisioner):** the IdP (Okta, Azure AD)
pushes changes to SCIM servers.

**SCIM server (provider):** the SaaS app (GitHub,
Salesforce, Slack) exposes the SCIM API and executes
the provisioning operations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SCIM is the standard REST API that every SaaS app
implements so IdPs can automatically create, update,
and delete user accounts across all of them.

**One analogy:**
> Before SCIM: every restaurant has a different order
> form, different menu numbering, different payment API.
> Being a waiter means memorizing 50 different systems.
>
> SCIM: all restaurants adopt a standard order protocol
> (HTTP REST, JSON body). Being a waiter means knowing
> one standard. A new restaurant? Same protocol.
> Connect once, provision universally.

**One insight:**
SCIM solves the N*M provisioning problem: N IdPs
integrating with M apps required N*M custom integrations.
SCIM makes it N+M: each IdP implements one SCIM client,
each app implements one SCIM server.

---

### 🔩 First Principles Explanation

**The integration explosion problem:**

Without a standard: Okta integrating with 7,000 apps
(their current catalog) needs 7,000 custom integrations.
Each app has a different user management API, different
authentication, different field names, different error
codes. This is O(IdPs * Apps) integration work.

With SCIM: each app implements the SCIM server spec
once. Okta's SCIM client connects to any compliant
SCIM server. This is O(IdPs + Apps) integration work.

**The token-based authentication model:**

SCIM servers authenticate SCIM clients via a bearer
token (typically a long-lived provisioning token, not
user credentials). The token is configured once in
the IdP provisioning setup. All SCIM requests carry
this token in the Authorization header. The token
should be rotated periodically; most SaaS apps support
token rotation in their admin console.

**Idempotency requirements:**

SCIM operations must be idempotent. If the IdP retries
a failed provisioning request, the SaaS app must not
create duplicate users. The `externalId` field (set
by the IdP to its own user ID) enables deduplication:
search for an existing user with the same externalId
before creating a new one.

---

### 🧪 Thought Experiment

**New hire Alice joins the Engineering team:**

Without SCIM:
```
HR enters Alice in Workday.
IT gets a Jira ticket.
IT manually creates accounts in:
  - GitHub (invite)     completed Monday
  - Jira (admin)        completed Monday
  - Slack (invite)      completed Monday
  - AWS (IAM user)      completed Tuesday (forgot first day)
  - Salesforce          not done (IT didn't know she needed it)
Alice starts on Monday: GitHub and Jira work. AWS doesn't.
Salesforce: Alice asks 3 weeks later.
```

With SCIM + Okta:
```
HR enters Alice in Workday.
Workday sends HR event to Okta (HRIS integration).
Okta creates Alice's Okta profile with group=Engineering.
Okta's provisioning rules:
  Engineering -> GitHub, Jira, Slack, AWS (IRSA role)
Okta sends SCIM POST /Users to all four apps.
All accounts active before Alice arrives at her desk.
Alice logs in on Day 1: everything works.
```

---

### 🧠 Mental Model / Analogy

> SCIM is the "universal employee directory sync" protocol:
>
> Think of the IdP as HR headquarters and each SaaS app
> as a satellite office. Before SCIM, HR had to call each
> satellite office with different scripts:
>
> - "GitHub office, please add employee Alice, role Engineer"
> - "Salesforce office, please add User Alice Smith, email..."
> - "Slack office, add new member alice@co.com to workspace..."
>
> SCIM gives all offices the same phone number format:
> "POST /Users: {name: Alice, email: alice@co.com, dept: Eng}"
>
> Every office uses the same protocol. HR sends one message
> type; all offices understand it.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
SCIM is a standard that lets the "one place you manage
employee accounts" automatically create and delete
accounts in all your company's apps. When someone joins,
accounts appear. When they leave, accounts disappear.

**Level 2 (junior developer):**
To implement SCIM in your SaaS app: expose a REST API
at /scim/v2/ that handles POST/GET/PATCH/DELETE for
/Users and /Groups. Authenticate requests using a
bearer token. Map SCIM User attributes to your user
model. The IdP will automatically call your API when
users are provisioned or deprovisioned in the IdP.

**Level 3 (mid engineer):**
Key implementation detail: the `active` attribute.
When a user is deprovisioned, IdPs typically send
`PATCH /Users/{id} {active: false}` rather than
`DELETE /Users/{id}`. Your app should honor `active:false`
as an immediate access block, not require physical
deletion. This allows data retention while blocking
access. Implement separate deletion if required by
data privacy policy.

**Level 4 (senior/staff):**
SCIM in multi-tenant SaaS: tenant isolation requires
that each tenant's SCIM provisioning token only affects
their own users. The SCIM server must scope all
operations by tenant derived from the auth token.
A missed tenant scope check = one enterprise customer's
Okta accidentally creates users in another customer's
account. This is a critical security bug - test it.

**Level 5 (distinguished):**
SCIM at scale faces eventual consistency challenges:
if the SCIM server is temporarily unavailable, IdP
queues the events and retries. But if the queue
depth grows (during a SaaS outage), the IdP may
drop or reorder events. SCIM does not define a
guaranteed delivery semantics. Enterprise IdPs add
reconciliation: periodic GET /Users from the IdP to
compare current state vs expected state. Any
discrepancy triggers a correction operation. This
is the SCIM equivalent of the two-phase reconciliation
pattern in distributed systems.

---

### ⚙️ How It Works (Mechanism)

```
SCIM Provisioning Flow (Okta -> SaaS App):

SETUP (once per app):
  1. SaaS app generates a provisioning bearer token
  2. Admin enters token into Okta's app provisioning config
  3. Okta discovers SCIM capabilities:
     GET https://app.example.com/scim/v2/ServiceProviderConfig
  4. Okta imports existing users:
     GET /scim/v2/Users?count=100&startIndex=1

JOINER EVENT:
  Okta: alice assigned to GitHub app
  SCIM POST https://app.example.com/scim/v2/Users
  Headers: Authorization: Bearer {provisioning-token}
  Body:
    {
      "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
      "userName": "alice@company.com",
      "name": {"givenName": "Alice", "familyName": "Smith"},
      "emails": [{"value": "alice@company.com", "primary": true}],
      "active": true,
      "externalId": "okta-user-id-alice-123"
    }
  Response: 201 Created + {id: github-user-id-456}
  Okta stores mapping: okta-alice-123 <-> github-456

MOVER EVENT (department change):
  SCIM PATCH /scim/v2/Users/github-456
  Body:
    {
      "Operations": [{
        "op": "replace",
        "path": "department",
        "value": "Finance"
      }]
    }

LEAVER EVENT:
  SCIM PATCH /scim/v2/Users/github-456
  Body:
    {"Operations": [{"op": "replace",
                     "path": "active",
                     "value": false}]}
  GitHub immediately blocks alice's access
```

---

### ⚖️ Comparison Table

| Feature | SCIM | Manual Provisioning | Custom API Integration |
|:---|:---|:---|:---|
| Standardization | RFC standard | None | Vendor-specific |
| Onboarding time | Seconds (automated) | Hours/days (manual tickets) | Weeks (custom dev) |
| Deprovisioning coverage | All connected apps (automated) | Inconsistent (manual) | Only integrated apps |
| Development cost (new app) | Implement once vs IdP catalog | None (but ops cost is high) | High per integration |
| Error handling | IdP retries + logs | Human follows up | Custom per integration |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| SCIM handles authentication | SCIM only handles provisioning (account creation/update/deletion). Authentication is handled by SAML/OIDC. These are separate protocols. |
| SCIM DELETE removes user data | Best practice is SCIM PATCH with active=false (access block), not DELETE. Deleting user data may violate audit log requirements. Data deletion is a separate policy decision. |
| SCIM is real-time | SCIM is event-driven but not guaranteed real-time. Network failures cause queuing and delays. For immediate emergency deprovisioning, also directly disable the IdP account. |
| Implementing SCIM /Users is sufficient | Groups via SCIM /Groups are essential for role-based access. If your app uses groups to control permissions, SCIM group sync must be implemented alongside user sync. |

---

### 🚨 Failure Modes & Diagnosis

**SCIM provisioning failure: user not created in target app**

**Symptom:** New user assigned to app in Okta but
cannot log in on Day 1. SCIM provisioning failed silently.

**Diagnosis:**
```bash
# Okta Admin: check provisioning logs
# Admin -> Reports -> System Log
# Filter: eventType = "application.provision.user.import"
#      or "application.provision.user.create"
# Look for failures with error detail

# Test SCIM endpoint directly
curl -v \
  -H "Authorization: Bearer $PROVISIONING_TOKEN" \
  https://app.example.com/scim/v2/Users/testuser

# Check SCIM server logs on the app side
# Common errors:
#   400 Bad Request: required field missing
#   401 Unauthorized: token expired/invalid
#   409 Conflict: user already exists (externalId clash)
```

**Fix:** Check SCIM server logs for the specific error.
For 401: regenerate and reconfigure provisioning token.
For 409: check for duplicate externalId mappings.
For 400: verify field mapping configuration in IdP.

---

**Active=false not blocking access (SCIM deprovisioning gap)**

**Symptom:** SCIM sends `active: false` on offboarding
but user can still log in to the target app.

**Root Cause:** SaaS app does not honor `active: false`
for access blocking - it only checks on SCIM DELETE.

**Diagnosis:**
```bash
# Verify SCIM deprovisioning response was 200/204 OK
# Check app's user status via its own admin console
# Compare: SCIM active=false vs app's "deactivated" flag

# Test: can user still authenticate after SCIM active=false?
# Use app-specific test: attempt login as deprovisioned user
```

**Fix:** File bug with SaaS app (SCIM non-compliance).
Interim: configure IdP to send SCIM DELETE instead of
PATCH for deprovisioning. Separately, revoke any
active user tokens in the SaaS app via its admin API.

---

### 🔗 Related Keywords

**Prerequisites:**

- `IAM-006` - IAM Principals: what SCIM provisions
- `IAM-007` - Identity Lifecycle Management: SCIM is the protocol for JML

**Builds On This:**

- `IAM-018` - CIAM vs Workforce IAM: SCIM in enterprise context
- `IAM-019` - Identity Governance: SCIM as governance data source
- `IAM-024` - Cross-Organization Federation: SCIM for partner provisioning

**Related:**

- `IAM-009` - SSO Concepts: SCIM (provisioning) + SAML/OIDC (authentication)
- `IAM-029` - IAM Compliance: SCIM as SOC 2 deprovisioning evidence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ SCIM QUICK REFERENCE                                 │
├───────────────────────┬──────────────────────────────┤
│ Base URL              │ /scim/v2/                    │
├───────────────────────┼──────────────────────────────┤
│ Create user           │ POST /Users                  │
├───────────────────────┼──────────────────────────────┤
│ Update user           │ PATCH /Users/{id}            │
├───────────────────────┼──────────────────────────────┤
│ Deprovision (access)  │ PATCH active:false           │
│ Deprovision (delete)  │ DELETE /Users/{id}           │
├───────────────────────┼──────────────────────────────┤
│ Authentication        │ Bearer token (provisioning)  │
│                       │ NOT user credentials         │
├───────────────────────┼──────────────────────────────┤
│ Key field             │ externalId (IdP user ID for  │
│                       │ deduplication)               │
├───────────────────────┼──────────────────────────────┤
│ RFC                   │ 7642 (concepts), 7643        │
│                       │ (schema), 7644 (protocol)    │
└───────────────────────┴───────────────────────────────┘
```

**If you remember 3 things:**

1. SCIM is provisioning, not authentication. It creates
   accounts; SAML/OIDC handles login.

2. Use `PATCH active:false` for deprovisioning, not
   immediate DELETE - preserves audit records.

3. `externalId` is the IdP's user ID. SaaS apps must
   store it to prevent duplicate user creation on retry.

**Interview one-liner:**
"SCIM (RFC 7642-7644) is the REST API standard for
automated user provisioning: POST /Users to create,
PATCH active:false to deprovision. IdPs like Okta act
as SCIM clients; SaaS apps implement SCIM servers.
It solves the N*M custom integration problem."

---

### 💎 Transferable Wisdom

**Reusable Principle:**
Any domain where multiple producers must push the same
type of event to multiple consumers benefits from a
standard protocol rather than bilateral custom
integrations. SCIM solved the IdP-to-SaaS integration
problem. Webhooks (standard HTTP POST to a callback URL)
solve the event notification problem. OpenTelemetry
solves the observability data standard problem. The
N*M-to-N+M reduction is the same pattern in all three:
standardize the producer output, standardize the consumer
input, eliminate per-pair custom code.

**Where else this appears:**

- Payment processing: Stripe's webhook format is
  essentially SCIM for payment events. Standardized
  payload format allows any app to consume Stripe
  events without custom integration per payment type.

- OpenTelemetry: N observability vendors, M applications.
  Without OTEL: N*M custom instrumentation. With OTEL:
  N+M (app instruments once, vendor receives OTEL data).

---

### 💡 The Surprising Truth

Despite SCIM being a 2015 RFC, a 2023 survey by
Gartner found that only 43% of enterprises with 500+
employees had fully automated identity provisioning
and deprovisioning. The majority still used manual
IT helpdesk processes or partial automation covering
only the top 3-5 apps. The technical barrier is low
(SCIM implementation is a few REST endpoints); the
barrier is organizational: provisioning automation
requires an integration project between HR, IT, and
every SaaS app owner simultaneously - a coordination
problem, not a technical one. Companies that overcome
this coordination barrier consistently show sub-1-day
offboarding compliance vs 5+ days for those that do not.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**

1. **IMPLEMENT** Sketch the SCIM server API endpoints
   required for an IdP to provision users into your
   app, including the `active` attribute handling for
   deprovisioning.

2. **DEBUG** SCIM provisioning is failing for new users
   in GitHub but working for Slack. Both use the same
   Okta tenant. Describe the diagnostic steps to
   identify whether the issue is in Okta's SCIM
   client, GitHub's SCIM server, or the integration
   configuration.

3. **DESIGN** Describe the reconciliation mechanism
   you would build to detect SCIM provisioning gaps
   (users in app but not in IdP) on a nightly basis.

---

*Identity & Access Management | IAM-011 | v5.0*