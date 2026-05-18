---
id: IAM-012
title: "Principle of Least Privilege - IAM Perspective"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-002, IAM-006
used_by: IAM-013, IAM-015, IAM-016
related: IAM-013, ATZ-005, SEC-012
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
nav_order: 12
permalink: /technical-mastery/iam/principle-of-least-privilege-iam-perspective/
---

⚡ TL;DR - The Principle of Least Privilege (PoLP) states
that every principal should have only the minimum permissions
needed to perform their current function - nothing more.
In IAM terms: no standing admin access, no wildcard
permissions, no inherited over-privilege. Its application
in IAM is the hardest part: not technically enforcing it
(that is trivial), but continuously maintaining it as
roles and permissions drift over time.

---

### 🔥 The Problem This Solves

The easiest way to onboard a new engineer is to give them
the "admin" role. They can do everything, no support tickets
needed. The problem accumulates silently:

- 50 engineers, all with admin access
- One compromised account = attacker has admin access
- One misconfigured script run by an admin = production
  data deleted
- SOC 2 auditor asks: "why does the mobile frontend
  developer have prod database admin access?"

Least privilege is not about security theatre - it is
about blast radius minimization. Compromised accounts
can only do what they were permitted to do. Mistakes
are bounded. Malicious insiders face meaningful friction.
The gap between "your credentials are stolen" and
"everything is compromised" is determined by how well
you applied least privilege.

---

### 📘 Textbook Definition

The Principle of Least Privilege (PoLP), defined in the
1974 Saltzer and Schroeder foundational paper on protection
in computer systems, states: "Every program and every
privileged user of the system should operate using the
least amount of privilege necessary to complete the job."

In IAM practice, this means:

**Minimal permissions:** grant only the specific actions
on specific resources required for the specific job
function. Not "S3 full access" - "s3:GetObject on
arn:aws:s3:::reports-bucket/*".

**No standing access:** privileged permissions should not
be permanently assigned. Request them when needed; they
expire automatically. (Just-in-Time access).

**Role minimality:** roles should be scoped to job
functions, not organizational hierarchy. A team lead
does not need admin access because of their seniority.

**Service account minimality:** automation accounts
need only the permissions for their specific task,
not the permissions of the humans who created them.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Grant the minimum permissions needed to do the job,
and no more. Every extra permission is a risk that
exists for no benefit.

**One analogy:**
> A hotel housekeeper has a master key that opens all
> guest rooms - but only on the floor they are assigned
> to, and only during their shift. They do not have the
> master key that opens the manager's office and the
> safe. They do not have 24/7 access. Each permission
> is scoped to exactly what is needed for the job.

**One insight:**
Least privilege is not a one-time configuration. Roles
evolve, people change jobs, services gain new features.
Without active maintenance, permissions only ever grow.
Access creep is the default direction in any IAM system.

---

### 🔩 First Principles Explanation

**The blast radius equation:**

Blast radius of a compromised identity =
  sum of all permissions granted to that identity

If an identity has admin access to everything: blast
radius = everything. If it has read access to one
bucket: blast radius = that one bucket.

Least privilege minimizes the blast radius of every
identity in the system. This does not prevent breaches;
it contains them.

**The compliance dimension:**

SOC 2 Trust Service Criteria 1.6 requires that access
to production systems is granted on a need-to-know basis
and reviewed periodically. PCI-DSS Requirement 7.1
requires restricting access to system components to
only individuals whose job requires it. Least privilege
is not optional for compliance.

**Why enforcement is hard:**

Granting permissions is fast (one AWS policy attachment).
Removing unnecessary permissions requires knowing which
ones are unnecessary - which requires access usage data,
role analysis, and organizational knowledge. IAM systems
make granting easy and make revocation hard. This
asymmetry is the root cause of access creep.

---

### 🧪 Thought Experiment

**Deploy a Lambda function that reads from DynamoDB:**

**Over-privileged (common mistake):**
```json
{
  "Effect": "Allow",
  "Action": "dynamodb:*",
  "Resource": "*"
}
```
Lambda can read, write, delete any DynamoDB table in
the account. If a bug causes unintended writes: data
corruption. If account is compromised: entire DynamoDB
accessible.

**Least privilege (correct):**
```json
{
  "Effect": "Allow",
  "Action": "dynamodb:GetItem",
  "Resource": "arn:aws:dynamodb:us-east-1:123:table/orders"
}
```
Lambda can only read from the orders table. A bug
cannot write or delete. Compromise of this function's
credentials only exposes the orders table reads.

**The blast radius difference:**
- Over-privileged: entire DynamoDB service at risk
- Least privilege: one table, one action

---

### 🧠 Mental Model / Analogy

> Least privilege is like a gas pipe with a pressure
> regulator and shutoff valves:
>
> - **Full admin:** the main gas pipe is always fully
>   open to all appliances. One fault = gas leak throughout
>   the building.
>
> - **Least privilege:** each appliance has its own
>   shutoff valve, sized to its actual gas requirement.
>   The stove gets cooking amounts. The water heater
>   gets heating amounts. A fault in the stove circuit
>   affects only the stove.
>
> Access permissions are like gas pressure. Every
> identity has its own valve. The valve is sized
> to exactly what is needed.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Only give people access to what they actually need to
do their job. An accountant does not need access to the
engineering codebase.

**Level 2 (junior developer):**
When writing IAM policies, specify exact actions and
exact resource ARNs. Avoid wildcards (`*`) in both.
Use the AWS IAM Policy Simulator or GCP IAM recommender
to identify what permissions your code actually uses.
Grant those; remove the rest.

**Level 3 (mid engineer):**
AWS IAM Access Analyzer + Access Advisor identify unused
permissions (permissions granted but never invoked in
the last 90 days). This is the practical tool for
implementing least privilege at scale. Schedule monthly
reviews: check Access Advisor output, propose permission
reductions, get sign-off, remove.

**Level 4 (senior/staff):**
Permission boundaries (AWS) are a guardrail mechanism:
they define the maximum permissions an IAM identity can
ever have, regardless of what policies are attached.
This prevents permission escalation attacks where a
developer creates a new IAM role with admin permissions
for themselves. The boundary says: "this account's
users can never exceed these permissions, regardless
of what policies they attach."

**Level 5 (distinguished):**
Zero standing privilege (ZSP): in highly secure
environments, no human has any standing permissions
in production. All access requires explicit Just-in-
Time (JIT) approval via a PAM tool (CyberArk, AWS
IAM Identity Center with approval workflow). Permissions
are issued for the specific task duration (typically
1-4 hours) and automatically revoked. This eliminates
the entire category of "compromised standing privileged
account" - there are no standing privileged accounts
to compromise. The operational cost (JIT request per
task) is the accepted trade-off.

---

### ⚙️ How It Works (Mechanism)

```
AWS Least Privilege Pattern:

BAD (wildcard permissions):
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

GOOD (least privilege):
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::my-data-bucket",
    "arn:aws:s3:::my-data-bucket/*"
  ]
}

IDENTIFY WHAT'S ACTUALLY NEEDED:
aws iam get-service-last-accessed-details \
  --arn arn:aws:iam::ACCOUNT:role/MyRole
# Shows: last time each service was accessed
# Services not used in 90 days -> candidate for removal

AWS IAM Access Analyzer:
aws accessanalyzer list-findings \
  --analyzer-arn arn:aws:accessanalyzer:...:analyzer/NAME
# Finds: policies that grant access beyond what is used
# Action: reduce policy to match actual usage
```

---

### ⚖️ Comparison Table

| Approach | Blast Radius | Operational Cost | Compliance |
|:---|:---|:---|:---|
| Full admin for everyone | Maximum | Low (no management) | Non-compliant |
| Role-based broad roles | High | Low-medium | Partial |
| Least-privilege per service | Minimal | Medium (initial setup) | Compliant |
| Zero standing privilege (JIT) | Zero for standing access | High (JIT per task) | Strictest compliant |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Least privilege means no admin accounts exist" | It means no standing admin access. Admins can exist and get temporary elevated access via JIT when legitimately needed. |
| "It is set up once and maintained automatically" | Permissions only grow without active review. Least privilege requires quarterly access certifications and AWS Access Advisor reviews. |
| "Least privilege slows down development" | Poorly scoped temporary admin access given lazily for "development convenience" is a security incident waiting to happen. DevOps environments can use sandbox accounts with broader permissions; production must have PoLP. |
| "Service accounts need fewer restrictions than user accounts" | Service accounts often have broader access (they call APIs 24/7, not just during business hours) and therefore need least privilege applied more strictly, not less. |

---

### 🚨 Failure Modes & Diagnosis

**Permission creep: excessive accumulated permissions**

```bash
# AWS: find unused permissions across all roles
aws iam generate-service-last-accessed-details \
  --arn arn:aws:iam::ACCOUNT:role/my-service-role

# Wait for report completion
aws iam get-service-last-accessed-details \
  --job-id <job-id>

# Services with LastAuthenticated > 90 days ago
# = permissions that have not been used and can be removed

# AWS IAM Access Analyzer: comprehensive unused findings
aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-002` - What IAM Actually Manages
- `IAM-006` - IAM Principals

**Builds On This:**
- `IAM-013` - Permissions and Policies: implementing PoLP in policies
- `IAM-015` - Cloud IAM: PoLP in AWS/GCP/Azure
- `IAM-016` - Privileged Access Management: PoLP for admin accounts

**Related:**
- `ATZ-005` - Principle of Least Privilege (Authorization category)
- `IAM-020` - Just-in-Time Access: the zero standing privilege model

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ LEAST PRIVILEGE IN IAM                              │
├──────────────────────┬──────────────────────────────┤
│ Rule 1               │ Specify exact actions        │
│                      │ Never: dynamodb:*            │
│                      │ Always: dynamodb:GetItem     │
├──────────────────────┼──────────────────────────────┤
│ Rule 2               │ Specify exact resources      │
│                      │ Never: Resource: "*"         │
│                      │ Always: specific ARN         │
├──────────────────────┼──────────────────────────────┤
│ Rule 3               │ No standing admin access     │
│                      │ JIT for elevated permissions │
├──────────────────────┼──────────────────────────────┤
│ Rule 4               │ Review quarterly             │
│                      │ Remove unused permissions    │
│                      │ Use Access Advisor (AWS)     │
├──────────────────────┼──────────────────────────────┤
│ Blast radius limit   │ Permissions define the max   │
│                      │ damage a breach can cause    │
└──────────────────────┴──────────────────────────────┘
```

**If you remember 3 things:**

1. Blast radius of a breach = permissions granted to
   the compromised identity. PoLP minimizes blast radius.

2. Permissions creep. They do not shrink automatically.
   Active review cycles are required.

3. Access Advisor (AWS) shows unused permissions.
   Use it monthly. Remove what is not used.

**Interview one-liner:**
"Least privilege: grant only the minimum permissions
needed for the specific function. In cloud IAM: specific
actions, specific resource ARNs, no wildcards, no
standing admin. Use AWS Access Advisor to identify and
remove unused permissions quarterly."

---

### 💎 Transferable Wisdom

The blast-radius minimization pattern appears throughout
secure system design. Unix process isolation: processes
run as the least-privileged UID that can perform their
function. Browser tab isolation: each tab runs in a
sandboxed process with least-privilege system access.
Microservice authorization: each service has only the
permissions it needs for its specific function, not
the permissions of the whole application. The pattern
is: decompose permissions to match the decomposition
of responsibility.

---

### 💡 The Surprising Truth

AWS's own internal analysis (documented in their security
best practices) found that the average AWS IAM policy
grants 5-10x more permissions than the workload actually
uses. The IAM Access Analyzer Unused Access analyzer,
launched in 2023, scans all IAM roles and reports on
permissions not used in the last 90 days. In most
customer accounts it activates against, it immediately
flags 40-60% of existing permissions as candidates for
removal. Least privilege is universally agreed to be
important; it is almost universally not practiced.

---

### ✅ Mastery Checklist

1. **WRITE** An AWS IAM policy for a Lambda that reads
   from one specific DynamoDB table. Specify exact
   actions and exact resource ARN. Identify what a
   wildcard policy would additionally grant.

2. **AUDIT** Given an IAM role's Access Advisor report
   showing 20 services, 12 of which have not been
   accessed in 180 days, describe the process for
   safely removing those 12 services from the policy.

3. **DESIGN** A zero-standing-privilege model for
   production database access: who can request access,
   what approvals are required, how long is it valid,
   and how is it automatically revoked.

---

*Identity & Access Management | IAM-012 | v5.0*