---
id: IAM-007
title: "Identity Lifecycle Management"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-002, IAM-006
used_by: IAM-011, IAM-019, IAM-020
related: IAM-006, IAM-011, IAM-019
tags:
  - iam
  - security
  - identity
  - foundational
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/iam/identity-lifecycle-management/
---

⚡ TL;DR - Identity lifecycle management governs how
identities are created (joiners), modified (movers), and
removed (leavers) - the JML process. Failure to automate
deprovisioning creates orphaned accounts: former employees
who retain access months after leaving. The solution is
integrating HR systems with IdP via SCIM for automated
provisioning and deprovisioning triggered by HR events.

---

### 🔥 The Problem This Solves

A SOC 2 auditor asks: "Show me all access that was
removed within 24 hours of employee termination." The
answer at a company with manual IT provisioning:
silence. Termination requests go to IT helpdesk via
email; helpdesk manually deactivates accounts across
twelve different systems over the course of days. Some
apps are forgotten. The contractor who left three months
ago still has Salesforce access because nobody knew
they had it.

This is the joiner-mover-leaver problem: identity
lifecycle events in HR (hire, promotion, departure) do
not automatically propagate to IT systems. The gap
creates orphaned accounts, over-privileged accounts,
and compliance violations.

---

### 📘 Textbook Definition

Identity lifecycle management is the set of processes
and systems that govern the complete lifecycle of an
IAM principal from creation to deletion:

**Joiners (Provisioning):** When a new employee or
contractor is hired, creating their identity and granting
baseline access. Triggered by HR onboarding event.
Automated via SCIM: IdP creates accounts in all
provisioned SaaS apps automatically on day one.

**Movers (Modification):** When an employee changes
role, department, or location, updating their access
permissions accordingly. Old role access is removed;
new role access is granted. Triggered by HR role-change
event.

**Leavers (Deprovisioning):** When an employee or
contractor leaves, revoking all access immediately.
Triggered by HR offboarding event. Automated via SCIM:
IdP deactivates accounts across all connected apps
simultaneously.

**Access Certification (Recertification):** Periodic
review of all access grants to confirm they are still
appropriate. Typically quarterly. Managers certify that
their team members still need the access assigned. Any
access not certified is automatically revoked.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Identities must be created when people join, updated
when they change roles, and removed when they leave.
Without automation, the "removed" step is consistently
forgotten and creates security liability.

**One analogy:**
> Hotel key card lifecycle: a new guest checks in and
> gets a card programmed for their room and floor
> (joiner). They upgrade to a suite: old card updated
> or replaced (mover). They check out: card is
> deactivated at checkout, not when they physically
> return it (leaver). The hotel does not rely on guests
> to return cards - it deactivates them automatically.
>
> IAM lifecycle management is the checkout system -
> not the guest's good faith.

**One insight:**
The "leaver" step is the most security-critical and
the most commonly failed. Humans reliably remember to
create accounts; they systematically forget to delete
them. Automation is the only reliable solution.

---

### 🔩 First Principles Explanation

**Why automation is required:**

Access provisioning has three steps:
1. Detect the identity lifecycle event (hire, leave)
2. Determine what access should change
3. Execute the change across all relevant systems

Manual execution requires: IT staff knowing about the
event, knowing all systems the user has access to,
having admin access to all those systems, and executing
the change before any access is misused. This fails at
scale and under time pressure.

Automated execution via SCIM requires: HR system fires
an event, IdP receives the event, IdP pushes SCIM
provisioning/deprovisioning to all connected apps.
Time to execute: seconds. No human in the critical path.

**The access creep problem:**

Without a mover process, every job change adds new
access without removing old access. A developer promoted
to lead still has all their individual developer
permissions plus the new lead permissions. After three
role changes, they have accumulated access from all
three previous roles - violating least privilege.

---

### 🧪 Thought Experiment

**Scenario:** Alice leaves the company on Friday at 5pm.

**Without lifecycle automation:**
- HR tells IT via email at 5pm Friday
- IT receives email Monday morning
- IT deactivates account in Okta (Monday, 10am)
- Okta propagates to Microsoft 365, Slack (Monday, 10am)
- Salesforce: IT forgot about it (still active for weeks)
- GitHub: separate manual process, done Tuesday
- AWS: forgotten (access persists for months)
- Gap window: 64 hours in primary systems, months in others

**With lifecycle automation:**
- HR triggers termination event in HRIS at 5pm Friday
- HRIS sends SCIM DELETE to Okta at 5:00:03pm
- Okta deactivates user in Okta at 5:00:05pm
- Okta SCIM pushes deprovisioning to all 40 connected
  apps within 5:00:05pm - 5:00:30pm
- AWS access via SAML federation: denied immediately
  (active sessions expire within 1 hour max)
- Gap window: under 30 seconds for all connected apps

**The insight:** Automation does not just make lifecycle
management faster - it makes it complete. Manual processes
are inherently partial.

---

### 🧠 Mental Model / Analogy

> Identity lifecycle is a continuous conveyor belt:
>
> **Joiners lane:** new employees flow in, identities
> are stamped and provisioned before they arrive at
> their first desk.
>
> **Movers lane:** employees changing roles have their
> identity updated while still moving - no disruption,
> old access removed, new access added.
>
> **Leavers lane:** departing employees flow out;
> identities are removed before they reach the exit.
> They do not carry access out the door.
>
> **Certification lane:** every identity on the belt
> passes a checkpoint quarterly. Those that are stale
> or wrong are removed before they cause problems.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
When you join a company, IT sets up your accounts.
When you move teams, your permissions change. When you
leave, all your access is removed. The problem is that
"removed" step is almost never automated and often
missed.

**Level 2 (junior developer):**
Lifecycle management connects the HR system (source of
truth for employment status) to the IdP (source of
truth for digital identity) via SCIM. When HR says
"Alice is terminated," SCIM tells Okta, which tells
all connected apps. No manual steps.

**Level 3 (mid engineer):**
SCIM provisioning is bidirectional: IdP pushes user
creates/updates/deletes to SaaS apps (outbound). SaaS
apps can also push user imports back to IdP (inbound).
Error handling matters: if SCIM deprovisioning fails
for one app, a retry mechanism must ensure eventual
deprovisioning. SCIM failures must alert, not silently
fail.

**Level 4 (senior/staff):**
Enterprise lifecycle management requires orchestration
beyond simple SCIM. Role-based provisioning: when a
user's department in HR changes, the IdP must calculate
the delta (remove old department apps, add new
department apps) without disrupting neutral access.
Access request workflows: non-automatic provisioning
for sensitive systems requires manager approval before
access is granted, with full audit trail.

**Level 5 (distinguished):**
At scale, the identity lifecycle interacts with
governance: every provisioning event produces an audit
record for SOC 2 compliance. Access certification
requires evidence that every access grant was reviewed
and approved within the last 90 days. IGA platforms
(SailPoint, Saviynt) orchestrate this: automated
provisioning/deprovisioning + workflow-gated exceptions
+ certification campaigns + audit reporting. The
technical challenge is reconciliation: IGA must
periodically scan all systems to detect out-of-band
access grants (direct DB grants, manual script-created
accounts) and bring them under governance.

---

### ⚙️ How It Works (Mechanism)

```
Automated Identity Lifecycle (JML):

JOINER (Day 1 provisioning):
HR Event: NewHire {name, dept, title, start_date}
  -> HRIS webhook -> IdP (Okta/Entra)
  -> IdP creates user {email, profile attributes}
  -> IdP evaluates provisioning rules:
       dept=Engineering -> provision GitHub, Jira, AWS
       dept=Finance -> provision Netsuite, Salesforce
  -> SCIM POST /Users to each app
  -> User arrives day 1: all access ready

MOVER (Role change):
HR Event: RoleChange {userId, oldDept=Eng, newDept=Finance}
  -> IdP updates user attributes
  -> IdP evaluates delta provisioning:
       Remove: GitHub, Jira, AWS (Eng apps)
       Add: Netsuite, Salesforce (Finance apps)
       Keep: Okta, Slack, Office 365 (neutral apps)
  -> SCIM PATCH or DELETE/POST per app

LEAVER (Offboarding):
HR Event: Termination {userId, date=today}
  -> IdP receives SCIM DELETE or status=inactive
  -> IdP disables user account (immediate)
  -> IdP sends SCIM DELETE to all 40+ connected apps
  -> Active SSO sessions: expire per token TTL (max 1h)
  -> Break-glass: if any app misses SCIM, IGA scan
       detects orphan within 24 hours

ACCESS CERTIFICATION (quarterly):
  IGA sends: "Certify access for your direct reports"
  Manager reviews: still needed? (YES/NO per permission)
  Uncertified access: auto-revoked after deadline
  Audit record: {certifier, date, decision} per grant
```

---

### ⚖️ Comparison Table

| Approach | Leaver Revocation Time | Coverage | Compliance Evidence |
|:---|:---|:---|:---|
| Manual IT helpdesk | Hours to days (business hours) | Incomplete (apps forgotten) | None |
| SCIM automated | Seconds | All connected apps | Audit trail per event |
| SCIM + IGA with certification | Seconds + quarterly review | Complete + drift detected | Full SOC 2 evidence |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Deactivating the Okta account removes all access" | Only for apps using SSO via Okta. Apps with local authentication, API keys, or manual provisioning still have active access. Okta deactivation is necessary but not sufficient. |
| "SCIM handles everything automatically" | SCIM handles provisioning for connected apps. Apps not connected to SCIM require manual deprovisioning or out-of-band detection via IGA reconciliation. |
| "We do offboarding checklists so we are covered" | Checklists have ~70% completion rates in practice. Automated SCIM has >99% completion. For SOC 2, automated evidence beats human attestation. |
| "Access certification is just for compliance theatre" | Certification catches access creep that automation misses: permissions granted manually by admins, test accounts promoted to prod, access retained after a role change. |

---

### 🚨 Failure Modes & Diagnosis

**Orphaned accounts after SCIM failure**

**Symptom:** SCIM deprovisioning event sent successfully
from IdP, but user still has access in the target SaaS
app. SCIM call failed silently.

**Diagnosis:**
```bash
# Check SCIM provisioning logs in Okta
# Okta Admin Console: Reports -> System Log
# Filter: eventType = "application.provision.user.deactivate"
# Look for error codes in the event details

# For any critical SaaS app: run weekly reconciliation
# Compare IdP active users vs SaaS app active users
# Any user in SaaS but not in IdP = orphaned account

# Okta API: list provisioning errors
curl -H "Authorization: SSWS $OKTA_API_TOKEN" \
  "https://$OKTA_DOMAIN/api/v1/logs?filter=\
   outcome.result+eq+\"FAILURE\"\
   &eventType+eq+\"application.provision.user.deactivate\""
```

**Fix:** Alert on SCIM provisioning failures immediately.
Implement an IGA reconciliation scan that runs daily
to detect orphaned accounts across all apps. Never rely
on SCIM success alone without confirmation.

---

**Access creep from mover process failures**

**Symptom:** User in role 4 (after three promotions)
has 4x the intended permissions because old role access
was never removed during role changes.

**Diagnosis:**
```bash
# AWS IAM: check all policies attached to a user
aws iam list-attached-user-policies --user-name alice
aws iam list-groups-for-user --user-name alice

# Cross-reference with current HR role
# If user is in Finance but still in "Engineering" IAM group:
# access creep from a missed mover event
```

**Fix:** Implement role-based provisioning with delta
calculation: calculate exact access delta on every
HR role change event rather than only adding new access.
Run quarterly access certifications to catch any
missed deltas.

---

### 🔗 Related Keywords

**Prerequisites:**

- `IAM-002` - What IAM Actually Manages: the identity and session objects
- `IAM-006` - IAM Principals: what gets provisioned

**Builds On This:**

- `IAM-011` - SCIM: the protocol for automated provisioning
- `IAM-019` - Identity Governance and Administration (IGA)
- `IAM-020` - Just-in-Time Access Provisioning

**Related:**

- `IAM-029` - IAM Compliance: SOC 2, GDPR audit requirements
- `IAM-030` - IAM Observability: lifecycle event monitoring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IDENTITY LIFECYCLE: JML                              │
├──────────────┬───────────────────────────────────────┤
│ JOINER       │ Trigger: HR new hire event            │
│              │ Action: provision all role-based apps │
│              │ Protocol: SCIM POST /Users            │
│              │ SLA: access ready before day 1        │
├──────────────┼───────────────────────────────────────┤
│ MOVER        │ Trigger: HR role/department change    │
│              │ Action: add new role apps, remove old │
│              │ Protocol: SCIM PATCH + delta calc     │
│              │ Risk: access creep without delta calc │
├──────────────┼───────────────────────────────────────┤
│ LEAVER       │ Trigger: HR termination event         │
│              │ Action: disable all access in seconds │
│              │ Protocol: SCIM DELETE / deactivate    │
│              │ Risk: orphaned accounts = security gap│
├──────────────┼───────────────────────────────────────┤
│ CERTIFICATION│ Trigger: quarterly schedule           │
│              │ Action: manager reviews all access    │
│              │ Uncertified: auto-revoked             │
│              │ Output: SOC 2 audit evidence          │
└──────────────┴──────────────────────────────────────┘
```

**If you remember 3 things:**

1. JML: Joiners, Movers, Leavers. The leaver step is
   the most critical and most commonly missed.

2. Automate deprovisioning via SCIM. Manual checklists
   are 70% reliable. Automation is > 99%.

3. Access creep = accumulated permissions from multiple
   role changes never cleaned up. Certification detects
   and removes it quarterly.

**Interview one-liner:**
"Identity lifecycle management automates the JML process:
provision access on join, update on role change, revoke
immediately on departure - triggered by HR events,
delivered via SCIM, validated quarterly by access
certifications."

---

### 💎 Transferable Wisdom

**Reusable Principle:**
Any system where objects (users, resources, permissions)
have lifecycle events must handle all three lifecycle
phases: creation, modification, and deletion. The
deletion phase is universally the most error-prone
because it is invisible - nothing breaks immediately
when it is skipped. The engineering response is always
the same: automate deletion triggers, add reconciliation
scans to detect what automation missed, and generate
audit evidence for compliance.

**Where else this appears:**

- Database connection pools: connections created (join),
  reused (move), destroyed (leave). Connection leak =
  "leaver" lifecycle not triggered on exception paths.

- Kubernetes pod lifecycle: created (join), updated
  (move via rolling deploy), terminated (leave).
  Finalizers ensure cleanup on termination - same
  pattern as SCIM deprovisioning.

---

### 💡 The Surprising Truth

Studies of SOC 2 Type II audit findings consistently
show that "terminated users with active access" is one
of the top three findings across organizations of all
sizes. A 2023 Okta workforce report found that the
average time-to-deprovision for a terminated employee
in companies without automated lifecycle management
is 5.2 days. During those 5.2 days, a disgruntled
employee has ample opportunity to exfiltrate data.
The technical solution (SCIM + HR integration) typically
costs less than the legal and investigation costs of
a single insider threat incident.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**

1. **EXPLAIN** Why SCIM deprovisioning from the IdP
   is necessary but not sufficient for complete
   access revocation, and what must supplement it.

2. **DESIGN** An automated offboarding flow for a
   company with Workday (HRIS), Okta (IdP), and
   30 SaaS applications connected via SCIM. Describe
   the trigger, the execution path, and the
   failure-recovery mechanism.

3. **AUDIT** Given a list of active accounts in
   Salesforce and a list of active employees in
   Workday, describe how to identify orphaned accounts
   and which ownership team is responsible for each.

---

*Identity & Access Management | IAM-007 | v5.0*