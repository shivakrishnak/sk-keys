---
id: ATZ-004
title: "The Principle of Least Privilege"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-001, ATZ-003
used_by: ATZ-013, ATZ-023, ATZ-041, ATZ-048, ATZ-050
related: ATZ-002, ATZ-005, ATZ-011
tags:
  - security
  - authorization
  - least-privilege
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/authorization/the-principle-of-least-privilege/
---

⚡ **TL;DR** - The Principle of Least Privilege (PoLP) states that every
subject (user, service, process) should have only the permissions
necessary to perform its current function - nothing more. It is not a
feature but a discipline: the default is zero access, and every
permission requires explicit justification. The principle limits blast
radius when credentials are compromised and is the foundational idea
behind every access control model.

---

### 📊 Entry Metadata

| #004 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-001, ATZ-003 | |
| **Used by:** | ATZ-013, ATZ-023, ATZ-041, ATZ-048, ATZ-050 | |
| **Related:** | ATZ-002 Authorization Hardness, ATZ-005 Break-Glass, ATZ-011 Superuser | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

If every service runs as root, every user is an admin, and
every API key has full account access - then one compromised
credential compromises everything. The blast radius of any
single failure is the entire system.

Least privilege limits blast radius: a compromised service
account that can only read S3 bucket A cannot read bucket B,
write to databases, or modify IAM policies. The breach is
real, but the damage is contained.

**BREAKING POINT:**

AWS S3 data breaches, 2019-present: the majority involve
an EC2 instance or Lambda function with an IAM role that has
`s3:GetObject` on `Resource: "*"` (all buckets). A compromise
of that one compute resource exposes every file in the account.
The correct scope: `s3:GetObject` on `Resource: arn:aws:s3:::
specific-bucket/*` only.

---

### 📘 Textbook Definition

The Principle of Least Privilege (PoLP), originally stated by
Jerome Saltzer and Michael Schroeder (1975), holds that every
subject in a system should operate using the minimal set of
privileges necessary to complete its authorized task. Access
should be granted for the minimum scope, minimum time, and
minimum resource set. The principle applies to all subjects:
human users, service accounts, processes, and automated agents.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Give every subject exactly enough access to do its job -
no more, and only for as long as needed.

**One analogy:**
> A hospital. A nurse has access to their patients' records,
> the medication room, and the ward where they work. They
> do not have access to the pharmacy dispensary, the surgery
> scheduling system, or the chief medical officer's email.
> Each role has exactly the access required for its function.
> This is not inconvenience - it is the design of a system
> where a compromised nurse badge has bounded impact.

**One insight:**
Least privilege is not about distrust of individuals; it is
about limiting the consequence of failure. Credentials get
compromised. Systems get breached. The question is: when that
happens, how much can an attacker do? Least privilege is the
answer to that question.

---

### 🔩 First Principles Explanation

**THREE DIMENSIONS OF LEAST PRIVILEGE:**

```
┌─────────────────────────────────────────────────────┐
│         The Three Dimensions of PoLP                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. SCOPE: Minimum resources                        │
│     ✓ Read this S3 bucket                           │
│     ✗ Read all S3 buckets                           │
│     ✓ Write to this table                           │
│     ✗ Write to any table in the database            │
│                                                     │
│  2. ACTIONS: Minimum operations                     │
│     ✓ SELECT on orders table                        │
│     ✗ SELECT, INSERT, UPDATE, DELETE, DROP          │
│     ✓ read:metrics scope in OAuth                   │
│     ✗ * scope (all operations)                      │
│                                                     │
│  3. TIME: Minimum duration                          │
│     ✓ Temporary credentials valid for 1 hour        │
│     ✗ Permanent credentials that never expire       │
│     ✓ Just-in-time access for a specific task       │
│     ✗ Standing admin access "just in case"          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**AWS IAM - least privilege in practice:**

The widest mistake is wildcard resources. The blast radius
of a compromised identity is bounded only by the resource
scope in its policy.

---

### 💻 Code Examples

**Example - BAD vs GOOD: AWS IAM policy scope**

```json
// BAD: wildcard resource - all S3 buckets
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "*"
}

// GOOD: specific bucket only
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": [
    "arn:aws:s3:::my-app-uploads/*",
    "arn:aws:s3:::my-app-uploads"
  ]
}
```

**Example - BAD vs GOOD: database service account**

```sql
-- BAD: application service account with superuser
GRANT ALL PRIVILEGES ON DATABASE production TO app_user;
-- Compromised app_user can: DROP tables, create users,
-- read any table, write any table, export any data

-- GOOD: minimum necessary permissions only
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT SELECT ON products TO app_user;
GRANT SELECT ON users TO app_user;
-- Compromised app_user cannot: DROP anything, CREATE,
-- access payment_methods table, access admin tables
```

**Example - FAILURE: wildcard permissions enable lateral movement**

```
Scenario:
  Microservice "order-processor" has IAM role with:
    - s3:* on Resource: *
    - dynamodb:* on Resource: *
    - sqs:* on Resource: *

  Attack:
    1. Attacker finds SSRF vulnerability in order-processor
    2. SSRF reads instance metadata endpoint
       → retrieves IAM role credentials
    3. Attacker uses credentials to:
       - Read all S3 buckets (customer PII, internal docs)
       - Read all DynamoDB tables (billing data, user data)
       - Send arbitrary SQS messages (queue poisoning)

  Correct scope (PoLP):
    - s3:GetObject on orders-bucket only
    - dynamodb:GetItem, PutItem on orders-table only
    - sqs:SendMessage on order-queue only

  With PoLP: SSRF is real, breach is scoped to one service's
  data. Without PoLP: SSRF = full account compromise.
```

---

### 🔭 At Scale

At large organizations (1000+ services), manually defining
least-privilege policies is impractical. The pattern:

1. **Policy generation from traffic analysis** - observe what
   IAM actions a service actually calls; generate a policy
   from that observed set (AWS IAM Access Analyzer does this)

2. **Permission boundaries** - set a maximum permission ceiling
   for entire service categories; no individual policy can
   exceed the boundary

3. **Just-in-time (JIT) access** - for sensitive operations,
   no standing access; request elevated permissions for a
   specific task, auto-expire in 1-8 hours

4. **Automated access review** - quarterly review of all
   permissions with last-used dates; auto-revoke if unused
   for 90 days

---

*Authorization category: ATZ | Entry: ATZ-004 | v5.0*