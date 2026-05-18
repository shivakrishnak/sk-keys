---
id: IAM-019
title: "Identity Governance and Administration (IGA)"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-006, IAM-007, IAM-013
used_by: IAM-026, IAM-029
related: IAM-007, IAM-020, IAM-025
tags:
  - iam
  - security
  - identity
  - governance
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/iam/identity-governance-and-administration-iga/
---

⚡ TL;DR - Identity Governance and Administration (IGA)
is the governance layer above IAM operations: it answers
"does this person STILL need this access?" on a periodic
basis, enforces Segregation of Duties (SoD - the same
person cannot initiate and approve a transaction), runs
role mining (discover role patterns from actual access
data), and provides compliance evidence for auditors.
SailPoint, Saviynt, and IBM Security Verify are the
leading IGA platforms. Without IGA, access creep makes
any IAM system an insider threat liability over time.

---

### 🔥 The Problem This Solves

IAM provisioning gives access. But access provisioning
without a recertification process means that over time:

- Engineers who moved to a different team still have
  access to the previous team's production systems
- Contractors who left 6 months ago still have active
  accounts (access creep via forgotten deprovisioning)
- An employee accumulates 5 years of "just in case"
  access grants from various projects
- The same person can submit purchase orders AND approve
  them (fraud risk - SoD violation)

For compliance frameworks (SOC 2, PCI DSS, ISO 27001),
the question from auditors is not just "who has access?"
but "how do you know that access is still appropriate?"
IGA provides the ongoing answer to that question.

---

### 📘 Textbook Definition

Identity Governance and Administration (IGA) encompasses
the policies, processes, and technologies for managing
the entitlement lifecycle and ensuring ongoing
appropriateness of access rights.

**Core IGA capabilities:**

**Access Certification (Recertification):** Periodic
review campaigns (quarterly, semi-annually, annually)
where managers review their team's access entitlements
and certify: "Yes, Alice still needs access to System X"
or revoke access. Automated enforcement: entries that
are not reviewed by deadline = auto-revoke.

**Segregation of Duties (SoD):** Policies that prevent
one person from having combinations of permissions that
would allow fraud or error without detection:
- Cannot submit AND approve purchase orders
- Cannot create AND authorize bank transfers
- Cannot modify AND deploy production code
  (four-eyes principle in some environments)

**Role Mining:** Analyze actual access data (who has
what in practice) to identify patterns and suggest
logical roles. Bottom-up role engineering: derive roles
from reality, not from theoretical job titles.

**Access Request Workflows:** Self-service portal for
requesting additional access. Approval workflows routed
to manager/resource owner. Access automatically granted
on approval. Audit trail of every request/approval.

**Provisioning and Deprovisioning Orchestration:**
IGA executes access changes in connected systems (AD,
Salesforce, Jira, GitHub) when role assignments change.
More comprehensive than SCIM provisioning: handles
fine-grained entitlements within systems, not just
account presence.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
IGA is the governance audit layer that asks "should
these people still have this access?" - quarterly,
systematically, with evidence for auditors.

**One analogy:**
> Annual employee badge renewal:
> - Every year, each employee's badge expires
> - Manager must certify: "Yes, Alice still needs
>   access to server room B and finance reports"
> - If manager does not respond in 2 weeks: access
>   is automatically revoked
> - Badge office keeps a ledger: who certified what,
>   when, and who let access lapse
> - Auditor arrives: "Show me who had access to
>   finance systems in Q3." Badge office has the log.

**One insight:**
IGA is distinct from IAM provisioning in the same way
that auditing is distinct from accounting. Provisioning
creates the access; IGA ensures the access remains
appropriate over time. Large organizations with thousands
of entitlements cannot manually review access - IGA
automates the review campaign and the enforcement.

---

### 🔩 First Principles Explanation

**Access creep - the entropy problem:**

Access is easy to grant and hard to remember to revoke.
Every project adds permissions; few projects clean them
up. After 3 years, an engineer may have:

- Access to 2 production systems from previous teams
- Admin access to a dev environment for a project that ended
- Read access to an HR system from a "temporary" request
- Write access to a shared S3 bucket for a one-time data migration

None of these are being actively abused. But each one
is a standing attack surface: if the engineer's account
is compromised, the attacker has all of these. IGA's
recertification campaigns force periodic cleanup of
stale entitlements before they accumulate into a
substantial excess privilege posture.

**The SoD challenge:**

SoD is the principle that sensitive processes require
at least two different people to complete. In financial
systems: one person can submit a payment, a different
person must approve it. IGA enforces this by maintaining
a SoD rule matrix (what role combinations are prohibited)
and checking every access grant or role assignment
against the matrix. Any proposed assignment that would
create a SoD violation is flagged for compensating
control review before being approved.

---

### 🧪 Thought Experiment

**Quarterly access certification campaign:**

```
SailPoint IdentityNow campaign structure:

Campaign scope: All production system access
              (all applications with production tag)
Reviewers: Direct manager of each account holder
Timeline: 14 days to complete
Remediation: Auto-revoke on non-response

Campaign launch (automated):
  For each principal in scope:
    1. Enumerate all entitlements from connected apps
       (via SCIM, LDAP, Salesforce API, GitHub API)
    2. Create certification item in IGA system
    3. Route to manager for review

Manager review interface:
  "Alice Smith has:
   - GitHub Org: payments-team, access since 2021-03-15
   - Salesforce: Sales Analytics, access since 2023-01-20
   - AWS Account 123: PowerUser, access since 2022-11-01"
  Manager clicks: [Certify] [Revoke] per item
  Or: [Certify All] (for managers who know their team)

Remediation on revoke:
  1. IGA creates SCIM PATCH to remove GitHub org membership
  2. IGA calls Salesforce API: revoke permission set
  3. IGA removes IAM Identity Center assignment for AWS

Audit artifact:
  Campaign report: 98% of entitlements reviewed,
  127 entitlements revoked, 23 were auto-revoked
  on non-response. Evidence exported to PDF for SOC 2 audit.
```

---

### 🧠 Mental Model / Analogy

> IGA is like library book renewal:
>
> - You checked out books (access grants) over time
> - Library sends renewal notice: "These books are
>   due. Do you still need them?"
> - You renew the ones you still use; return the rest
> - Books not renewed by due date are automatically
>   returned (auto-revoke on non-certification)
> - Library keeps a record of every checkout, renewal,
>   and return (audit trail)
> - Librarian can show any past snapshot:
>   "In March, Alice had checked out these 7 books"
>   (point-in-time access reporting for auditors)

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
IGA is the system that asks managers every quarter:
"Does your team still need all this access?" and
automatically removes access that managers do not
certify. It keeps the audit trail for compliance.

**Level 2 (junior developer):**
From an engineer's perspective: IGA means you get
a quarterly email from a tool like SailPoint asking
your manager to certify your access. If your manager
does not certify it, your access is automatically
removed. This is a feature, not a bug - it keeps
permissions clean and auditable.

**Level 3 (mid engineer):**
Access request workflow design: all access requests
go through IGA (not through Slack or email). Engineer
submits request in IGA portal, selects the role/resource.
IGA routes to the resource owner (not just manager).
Access is granted automatically on approval. The full
chain (request, approval, grant) is logged and searchable.
Audit query: "Who approved Alice's access to the payments
service?" returns the exact record.

**Level 4 (senior/staff):**
Role mining for RBAC simplification: starting from
scratch with 500 application entitlements across 2000
users is impossible to govern. IGA role mining analyzes
actual access data (a "who has what" snapshot) and
clusters similar access patterns into candidate roles.
Output: "These 87 users in the engineering org all
have access to Jira Projects A, B, C + GitHub org
eng + AWS dev account. Candidate role: Engineering
Standard." Converting 87 individual entitlement sets
into one role makes recertification 87x simpler:
certify the role, not each person.

**Level 5 (distinguished):**
IGA at enterprise scale (50,000+ employees, 500+
connected applications): The bottleneck is application
connectivity. IGA value is limited by the number of
systems whose entitlements it can read and write.
Connectors for common SaaS (Salesforce, Workday, GitHub,
AWS) are standard; custom app connectors require SCIM
or REST API development. The IGA program is only as
complete as its connector coverage. Mature IGA programs
track "connector coverage" as a security KPI and treat
ungoverned applications as a risk line item.

---

### ⚙️ How It Works (Mechanism)

```
IGA SoD Violation Detection:

SoD rule matrix (example, financial system):
  RULE-01: submit_payment AND approve_payment -> PROHIBITED
  RULE-02: create_vendor AND approve_vendor   -> PROHIBITED
  RULE-03: record_journal AND close_period    -> PROHIBITED

On access request: Bob (has approve_payment role)
                   requests submit_payment role

IGA evaluation:
  1. Check Bob's current roles: [approve_payment]
  2. Check requested roles: [submit_payment]
  3. Run SoD matrix check:
     submit_payment + approve_payment -> RULE-01 violation
  4. Flag violation: RULE-01 conflict detected
  5. Route to Risk Management for compensating control review
     (not automatic approval/rejection)

Compensating control: manager accepts risk with documented
justification (e.g., "Bob is the only person available;
will implement detective control: second reviewer for all
Bob's transactions").

IGA recertification (automated campaign):

SailPoint API:
  POST /cc/api/campaign/create
  {
    "name": "Q4 2024 Access Review",
    "type": "Manager",
    "deadline": "2024-12-31",
    "applications": ["*production*"]
  }

Certification decision:
  POST /cc/api/decision/certify
  {
    "certificationItemId": "12345",
    "decision": "REVOKED",
    "comments": "Engineer transferred teams"
  }
```

---

### ⚖️ Comparison Table

| Capability | IGA Platform | Basic SCIM Provisioning | Manual Process |
|:---|:---|:---|:---|
| Access certification | Automated campaigns | No | Spreadsheets |
| SoD enforcement | Policy engine | No | Manual check |
| Role mining | ML-based clustering | No | Consultant projects |
| Audit trail | Complete, searchable | Partial (event log) | Poor |
| Connector coverage | 200+ apps (SailPoint) | SCIM only | N/A |
| Compliance reporting | Out-of-box templates | No | Manual |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "IGA is just IAM with extra steps" | IGA adds the governance and compliance layer - recertification, SoD, audit reporting. IAM provisioning gives access; IGA governs that access over its lifecycle. |
| "SCIM provisioning replaces IGA" | SCIM handles account lifecycle (create/update/deactivate). IGA handles entitlement governance (recertification, SoD, role mining). They are complementary. |
| "IGA is only for compliance teams" | IGA reduces operational overhead: automated deprovisioning (instead of manual ticket-driven) and access request workflows reduce IT helpdesk load. |
| "SoD prevents all fraud" | SoD is a preventive control; it constrains fraud opportunities. Determined insiders with collusion can bypass SoD. Detective controls (audit logging, anomaly detection) are the complementary layer. |

---

### 🚨 Failure Modes & Diagnosis

**IGA certification campaign missed: access creep persists**

```bash
# Check campaign completion rate:
# SailPoint IdentityNow API:
curl -H "Authorization: Bearer $IGA_TOKEN" \
  "https://org.api.identitynow.com/v3/campaigns?
   status=IN_PROGRESS" | jq '.[] | {
     name: .name,
     completionPercentage: .completionPercentage,
     deadline: .deadline
   }'

# If completion % is low near deadline:
# 1. Send reminder emails to non-responding managers
# 2. Escalate to HR for managers 50% non-complete
# 3. On deadline: auto-revoke all uncertified items

# Prevention: weekly reminder automation
# Track: certification completion rate as security KPI
```

**SoD violation detected post-provisioning (missed at grant)**

```bash
# SailPoint: run SoD violation scan across all identities
POST /cc/api/policyViolation/search
{
  "query": {"status": "OPEN"},
  "includeRiskScore": true
}

# Prioritize by risk score (financial system SoD first)
# For each violation: notify manager + risk owner
# Remediation options:
# 1. Remove one of the conflicting entitlements
# 2. Accept risk with compensating control
# 3. Escalate to CISO for risk acceptance
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-006` - IAM Principals: roles and entitlements
- `IAM-007` - Identity Lifecycle Management
- `IAM-013` - Permissions and Policies

**Builds On This:**
- `IAM-026` - Enterprise IAM Architecture: IGA in the stack
- `IAM-029` - IAM Compliance: IGA evidence for SOC 2/ISO 27001

**Related:**
- `IAM-020` - Just-in-Time Access: alternative to standing access
- `IAM-025` - RBAC Overview: roles as IGA governance unit

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IGA CORE FUNCTIONS                                   │
├───────────────────────┬──────────────────────────────┤
│ Access Certification  │ Quarterly manager review     │
│                       │ Auto-revoke on non-response  │
├───────────────────────┼──────────────────────────────┤
│ SoD Enforcement       │ Policy matrix check on every │
│                       │ access grant                 │
├───────────────────────┼──────────────────────────────┤
│ Role Mining           │ Cluster actual access data   │
│                       │ -> derive logical roles      │
├───────────────────────┼──────────────────────────────┤
│ Access Request        │ Self-service + approval      │
│                       │ workflow -> audit trail      │
├───────────────────────┼──────────────────────────────┤
│ Compliance Reporting  │ Point-in-time access reports │
│                       │ SOC 2 / ISO 27001 evidence   │
└───────────────────────┴──────────────────────────────┘
Leading platforms: SailPoint, Saviynt, IBM ISVA
```

**Interview one-liner:**
"IGA governs access over its lifecycle: access
certification campaigns (quarterly manager review with
auto-revoke), SoD enforcement (no one person can both
submit and approve transactions), role mining (derive
roles from actual access patterns), and compliance
reporting for SOC 2/ISO 27001. SailPoint and Saviynt
are the leading IGA platforms."

---

### 💎 Transferable Wisdom

IGA's access certification process is the technical
embodiment of a fundamental security principle: trust
must be continuously re-earned, not established once
and held forever. The same principle applies to:
infrastructure (rotating credentials/keys even when not
compromised), database (periodic schema reviews to remove
unused tables/columns), code (removing dead code and
unused dependencies). "Default expire, explicit renewal"
is a safer posture than "default persist, explicit revoke"
for any resource with a security implication.

---

### ✅ Mastery Checklist

1. **DESIGN** A quarterly access certification campaign
   for 2,000 employees and 50 connected applications.
   Specify the scope, reviewer assignment logic, deadline
   enforcement rules, and what happens to uncertified
   entitlements.

2. **CONFIGURE** Define a SoD rule matrix for a financial
   application with these roles: submit_payment,
   approve_payment, create_vendor, approve_vendor,
   view_reports, admin. Identify which combinations
   are prohibited and why.

3. **JUSTIFY** A CISO asks why the company needs an IGA
   platform when it already has Okta for provisioning
   and CloudTrail for logging. Explain the specific
   compliance and risk gaps that IGA fills.

---

*Identity & Access Management | IAM-019 | v5.0*