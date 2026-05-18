---
id: IAM-029
title: "IAM Compliance (SOC 2, GDPR, ISO 27001)"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★★
depends_on: IAM-019, IAM-026, IAM-030
used_by: []
related: IAM-019, IAM-030, SEC-015
tags:
  - iam
  - security
  - compliance
  - advanced
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/iam/iam-compliance-soc2-gdpr-iso-27001/
---

⚡ TL;DR - IAM controls are the most audited area in
security compliance: SOC 2 Logical Access Controls,
ISO 27001 Annex A.9, and PCI DSS Requirement 7/8 all
mandate who has access to what systems and how that
access is governed. IAM compliance requires: access
reviews (quarterly for privileged, annual for standard),
MFA for all privileged and remote access, offboarding
within 24 hours of termination, access provisioning
with approval workflows, Segregation of Duties,
and audit logs retained for 12+ months. Evidence
collection should be automated: IGA reports, IAM
audit logs, and access certification completion rates.

---

### 🔥 The Problem This Solves

Security auditors (SOC 2, PCI, ISO 27001) spend 40-60%
of their time on IAM controls. The questions are
predictable: "Show me who had access to the cardholder
data environment in Q3"; "Show me that Alice's access
was revoked within 24 hours of her termination";
"Show me evidence that all privileged access accounts
have MFA enabled"; "Show me the access review from
last quarter for production systems."

Organizations without mature IAM governance answer
these questions with manual, error-prone processes:
spreadsheets, email chains, manual access inventories.
The answers are late, incomplete, and often inconsistent.
Mature IAM governance automates evidence collection:
IGA certification reports, IAM audit log exports, and
provisioning workflow logs provide audit-ready answers
in minutes.

---

### 📘 Textbook Definition

IAM compliance is the set of controls, processes, and
evidence required to satisfy the identity and access
management requirements of security frameworks and
regulations.

**SOC 2 - Logical Access Controls (CC6 Trust Service Criteria):**

- CC6.1: Logical access security to protect against
  unauthorized access. MFA required. Access reviews.
- CC6.2: Prior to issuing credentials, entity registers
  and authorizes new internal and external users.
  (Formal provisioning process with approval)
- CC6.3: Role-based access. Removal of access when
  employment ends. Access reviews.
- CC6.6: Logical access to information assets from
  outside the entity's infrastructure.
  (MFA for remote/external access)
- CC6.7: Changes to access rights and related changes
  to logical access security. (Change management for access)
- CC6.8: Entity implements controls to prevent or
  detect and act upon the introduction of unauthorized
  or malicious software. (Related: privileged access controls)

**ISO 27001 Annex A.9 - Access Control:**

- A.9.1: Business requirements of access control
  (access control policy)
- A.9.2: User access management (provisioning,
  deprovisioning, review, privileged access)
- A.9.3: User responsibilities (password management,
  clean desk, no shared credentials)
- A.9.4: System and application access control
  (MFA, secure logon, session timeout)

**GDPR - Article 5/32 (IAM relevant):**

- Data access limited to authorized personnel only
- Audit logs of personal data access
- Rights management: right to access, erasure, portability
- Data breach notification: know who had access when

**PCI DSS Requirements 7 and 8:**

- 7.1: Limit access to system components and cardholder data
  to only those individuals whose job requires such access
- 7.2: Role-based access control
- 8.1: Define and manage all user IDs
- 8.2: MFA for all access to CDE (Cardholder Data Environment)
- 8.3: No shared accounts in CDE
- 8.6: Service accounts managed and monitored
- 8.8: Policies on user IDs and authentication

---

### ⏱️ Understand It in 30 Seconds

**One line:**
IAM compliance is the evidence that your identity
controls work: who has access to what, how access
is granted and revoked, MFA is enforced, and privileged
accounts are governed - all documented and auditable.

**One analogy:**
> IAM compliance is like a food safety inspection:
>
> - Inspectors do not trust self-reporting
> - They check: records, receipts, logs, processes
> - "Show me the access log for the production database"
>   = "Show me the temperature log for the cold storage"
> - Evidence must be: objective, complete, verifiable
> - Past paper records -> now automated system exports
>
> The goal: make audit evidence automatic, not a fire drill.

**One insight:**
The biggest compliance risk is not missing a control -
it is missing the evidence that the control exists and
works. An access review that happened but was not
documented provides zero audit value. All IAM governance
processes must generate artifacts (reports, tickets,
log exports) automatically.

---

### 🔩 First Principles Explanation

**The three audit questions:**

Every IAM compliance audit reduces to three questions:

1. **"Who had access at time T?"**
   Answered by: IGA point-in-time access snapshot,
   IAM platform user-role report, application SCIM
   provisioning history.

2. **"Was that access appropriate?"**
   Answered by: IGA access certification records
   (manager certified this access on date X), access
   request workflow records (approved by Y for reason Z).

3. **"Was access removed when it should have been?"**
   Answered by: IAM termination workflow records
   (terminated on date A, access removed by date B),
   SCIM deprovisioning event log.

If your IAM system cannot answer all three questions
for any principal and any point in time going back
12 months, you have a compliance gap.

**Privileged access is highest scrutiny:**

Auditors focus on privileged access because the
blast radius of privilege misuse is greatest. For all
privileged accounts:
- MFA is mandatory (not optional)
- JIT access is preferred over standing privilege
- All sessions must be recorded (PAM session recording)
- Access reviews more frequent: quarterly for privileged
  vs. annual for standard

PCI DSS is explicit: MFA is required for ALL access
to the CDE. SOC 2 CC6.1 requires MFA as a logical
access control. These are audit findings if not met.

---

### 🧪 Thought Experiment

**Preparing for a SOC 2 Type II audit (identity section):**

```
Auditor requests (typical IAM evidence package):

1. Access control policy document
   -> Artifact: IAM policy (version-controlled in Confluence)
   -> Who, what, when, approval history

2. User access reviews (last 12 months)
   -> Artifact: IGA (SailPoint) campaign reports
   -> Campaign dates, scope, completion %, revocations
   -> Automated: SailPoint exports PDF report per campaign

3. Privileged access list and MFA evidence
   -> Artifact: Okta admin user report
   -> All users with admin role: MFA enrolled? Last MFA use?
   -> Automated: Okta report export API

4. Termination workflow (offboarding < 24h)
   -> Artifact: last 50 offboarding events from HRIS/Okta
   -> HRIS termination date vs. Okta deactivation timestamp
   -> Automated: Okta system log export

5. Access request/approval audit trail
   -> Artifact: IGA access request workflow records
   -> Request, approver, approval date, access granted
   -> Automated: IGA audit export

6. SOD policy and violation tracking
   -> Artifact: IGA SOD policy rules + violation log
   -> What combinations are prohibited, last scan results
   -> Automated: IGA SOD report

Total evidence preparation with mature IAM: 2 hours
Without mature IAM: 2 weeks of manual data gathering
```

---

### 🧠 Mental Model / Analogy

> IAM compliance is like car maintenance records:
>
> - Insurance claim: "Was the car maintained?"
> - Without records: "I think so, we serviced it..."
> - With service book: date, mileage, what was done,
>   who did it, warranty stamp
>
> IAM compliance = the service book for your access controls:
> - Access review certification = scheduled service
> - Offboarding workflow = annual MOT (mandatory test)
> - MFA evidence = safety equipment check
> - PAM session recording = dashcam footage
>
> The auditor is the insurance adjuster:
> they need records, not assurances.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
IAM compliance means having documented evidence that
the right people have access to the right systems,
access is reviewed regularly, and departed employees
have their access removed promptly.

**Level 2 (junior developer):**
Developers are part of IAM compliance: every access
request should go through an approval workflow (not
Slack DMs). Access to production systems should have
a documented business justification. This creates the
audit trail that compliance requires.

**Level 3 (mid engineer):**
Automating SOC 2 evidence for the access review
requirement: configure SailPoint (or Okta access reviews)
to run quarterly access certification campaigns. The
IGA platform generates a campaign report that includes:
scope, reviewer, certification decisions, revocations,
and completion percentage. Export this as PDF/Excel
and store in the compliance evidence repository.
Evidence generation: 1 hour per quarter.

**Level 4 (senior/staff):**
GDPR data access governance in IAM: map every personal
data store (customer database, analytics warehouse,
support ticket system) to the IAM roles that have
access. For right-to-erasure requests: the data map
tells you which systems to query for deletion.
For breach notification: the access log tells you
who had access to the affected data in the 90 days
before discovery. This requires: IAM-to-data-store
access mapping documentation, audit log retention
for 90+ days, and a documented right-to-erasure
execution runbook.

**Level 5 (distinguished):**
Continuous compliance monitoring (Compliance-as-Code):
rather than point-in-time audit preparation, implement
continuous control monitoring. Automated checks run
daily: "Are any users missing MFA?", "Are there any
offboarding tickets older than 24 hours?", "Are there
any privileged users without a recent access review?"
Failures generate tickets automatically. Compliance
dashboard shows real-time control health. At the SOC 2
audit: provide the continuous monitoring reports as
evidence that controls operate continuously (not just
at audit time). This is the difference between Type I
(controls exist at a point in time) and Type II
(controls operate effectively over a period) evidence.

---

### ⚙️ How It Works (Mechanism)

```
Automated Evidence Collection Pipeline:

SOC 2 Logical Access Controls - Weekly Check:

1. MFA coverage check:
   Okta Report API:
   GET /api/v1/users?filter=status eq "ACTIVE"
   For each user: GET /api/v1/users/{id}/factors
   Alert if any active user has 0 enrolled MFA factors
   
   Okta automated report:
   Admin Console -> Reports -> User Enrollment
   Export: weekly CSV of all users + MFA status
   Store in: s3://compliance-evidence/soc2/mfa/YYYY-MM-DD.csv

2. Offboarding SLA check (< 24h):
   Query HRIS API: terminations in last 30 days
   Query Okta API: user status + deactivation date
   For each terminated user:
     sla_met = (okta_deactivation - hris_termination) < 24h
   Alert if any termination > 24h Okta deactivation lag
   
   Export: monthly offboarding SLA report
   Store: s3://compliance-evidence/soc2/offboarding/

3. Access review evidence (quarterly):
   SailPoint API:
   GET /cc/api/campaign?status=COMPLETED
   Filter: last 90 days
   Export per campaign:
   {
     name: "Q3 Production Access Review",
     startDate: "2024-07-01",
     endDate: "2024-07-14",
     completionRate: 97%,
     totalItems: 2450,
     revokedItems: 127,
     reviewerReport: [...per-manager summary...]
   }
   
   PDF export stored in compliance evidence vault

4. SOD violation report (quarterly):
   SailPoint API:
   GET /cc/api/policyViolation?status=OPEN
   Export: open violations + remediation status
   For each violation:
     {rule, user, detected, remediated_or_accepted, reason}

PCI DSS CDE Access Evidence:
  Tag all CDE applications in IAM platform
  Weekly: export all users with CDE app access
  Verify: all have MFA enrolled (mandatory for PCI 8.2)
  Export: stored per PCI audit cycle
```

---

### ⚖️ Comparison Table

| Framework | Key IAM Requirements | Evidence Required | Frequency |
|:---|:---|:---|:---|
| SOC 2 | MFA, access reviews, provisioning/deprovisioning workflows | Campaign reports, offboarding logs, MFA enrollment | Annual (Type I) or 6-12 months (Type II) |
| PCI DSS | MFA for CDE, no shared accounts, quarterly user reviews | CDE access list, MFA evidence, quarterly review certs | Quarterly reviews; annual audit |
| ISO 27001 | Access control policy, formal provisioning, reviews | Policy doc, provisioning workflow records, review evidence | Annual surveillance + triennial recertification |
| GDPR | Access limitation, audit logs, deletion rights | Access logs, DPA records, erasure workflow logs | Ongoing |
| HIPAA | Minimum necessary access, access monitoring, audit logs | PHI access reports, activity logs, BAA records | Annual risk assessment |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Completing access reviews satisfies SOC 2" | SOC 2 requires evidence that access reviews were completed correctly (not just attempted). Completion rate, revocation decisions, and manager sign-off are all examined. A 60% completion rate is a finding. |
| "GDPR is only about data, not identity" | GDPR Article 32 requires appropriate technical controls for data security, including access controls. Who can access personal data is directly in scope. GDPR data breaches require knowing who had access. |
| "ISO 27001 certification means you are secure" | ISO 27001 certifies that you have an Information Security Management System (ISMS) and specific controls. It does not certify that you have no vulnerabilities. Controls must be effective, not just documented. |
| "Privileged access reviews can be annual" | PCI DSS requires quarterly user access reviews for CDE access. SOC 2 auditors treat privileged access as higher-risk and expect more frequent reviews. Annual privileged access reviews are typically a finding. |

---

### 🚨 Failure Modes & Diagnosis

**SOC 2 audit finding: terminated user access not revoked**

```bash
# Auditor: Alice was terminated 2024-09-15.
# Her Okta account was deactivated 2024-09-22 (7 days late)
# This is a CC6.3 finding.

# Root cause analysis:
# 1. Check HRIS termination event:
#    Workday: when was Alice's employment end recorded?
#    Workday: when did the Workday->Okta sync run?

# 2. Check Okta import log:
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?
   filter=actor.displayName eq \"Workday\"
   AND target.alternateId eq \"alice@company.com\"
   &since=2024-09-14T00:00:00Z" | \
  jq '.[] | {time: .published, outcome}'

# 3. Check Okta deactivation event:
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?
   filter=eventType eq \"user.lifecycle.deactivate\"
   AND target.alternateId eq \"alice@company.com\""

# Root cause typically: HRIS sync delay OR
# HR did not mark termination same day (recorded 2024-09-22)

# Fix: configure real-time HRIS webhook (not daily batch)
# Remediation for audit: document that SLA breach was
# due to HRIS data entry delay; now fixed with real-time sync
```

**MFA audit finding: privileged users without MFA**

```bash
# Auditor: list of admin users who have not enrolled MFA
# This is an SOC 2 CC6.1 finding

# Immediate action: enforce MFA on next login
curl -X POST -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/policies/mfa/rules" \
  -d '{
    "name": "Force-Admin-MFA",
    "conditions": {
      "people": {"groups": {"include": ["admin-group-id"]}}
    },
    "actions": {
      "signon": {
        "requireFactor": true,
        "factorPromptMode": "ALWAYS"
      }
    }
  }'

# For audit response:
# 1. Explain: MFA policy was in place but not enforced for
#    service accounts that had admin group membership
# 2. Remediation: removed service accounts from admin group;
#    enforced MFA policy; weekly MFA enrollment audit report
# 3. Evidence: new weekly automated report (going forward)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-019` - IGA: access certification as SOC 2 evidence
- `IAM-026` - Enterprise IAM Architecture: the governed stack
- `IAM-030` - IAM Observability: audit logs as compliance evidence

**Related:**
- `SEC-015` - Security Compliance Frameworks
- `IAM-016` - PAM: privileged access controls for PCI/SOC 2

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IAM COMPLIANCE EVIDENCE CHECKLIST                    │
├────────────────────────────────────────────────────── ┤
│ SOC 2 / ISO 27001:                                   │
│  MFA enrollment report (all users)                   │
│  Access review campaign reports (quarterly/annual)   │
│  Offboarding SLA log (termination -> deactivation)   │
│  Provisioning approval workflow records              │
│  SOD violation and remediation log                   │
│  Privileged account list + JIT session log           │
├────────────────────────────────────────────────────── ┤
│ PCI DSS (additional):                                │
│  CDE access list with MFA verification               │
│  Quarterly user access review for CDE                │
│  No shared accounts evidence (unique user IDs)       │
├────────────────────────────────────────────────────── ┤
│ GDPR (additional):                                   │
│  Personal data access log (who accessed what when)   │
│  Right-to-erasure execution records                  │
└────────────────────────────────────────────────────── ┘
```

**Interview one-liner:**
"IAM compliance (SOC 2, ISO 27001, PCI DSS) requires:
MFA for all privileged/remote access, quarterly access
reviews with certification records, offboarding within
24 hours with evidence, SOD enforcement, and 12+ months
of audit log retention. Evidence should be automated
via IGA campaign reports, IAM log exports, and continuous
compliance monitoring - not manual spreadsheets."

---

### 💎 Transferable Wisdom

IAM compliance automation reveals a broader principle:
the best evidence is a living record, not a retrospective
reconstruction. Continuous control monitoring (daily
MFA check, real-time offboarding SLA check) creates
Type II SOC 2 evidence: the controls operate continuously.
Retrospective manual collection (gather evidence when
auditor arrives) creates Type I evidence at best,
and frequently fails to satisfy Type II requirements.
This principle extends to: infrastructure compliance
(continuous CloudTrail analysis vs. point-in-time
config snapshots), code quality (continuous test/lint
CI vs. manual code review before release), and data
quality (streaming validation vs. periodic audit).
Build the audit evidence into the operational process,
not as a separate audit preparation activity.

---

### ✅ Mastery Checklist

1. **MAP** Identify the five most common SOC 2 IAM
   audit findings and describe the specific evidence
   artifact, the IAM control, and the automated
   evidence generation process for each.

2. **AUTOMATE** Design an automated compliance monitoring
   pipeline that runs daily checks for: MFA coverage,
   offboarding SLA, quarterly access review completion,
   and privileged account inventory. Include the alert
   routing and evidence storage strategy.

3. **RESPOND** An auditor requests: "Show me all access
   to the production payments database in Q3, who
   approved each grant, and evidence that any terminated
   employees had their access removed within 24 hours."
   Describe the specific queries, reports, and artifacts
   you would provide, and which IAM systems they come from.

---

*Identity & Access Management | IAM-029 | v5.0*