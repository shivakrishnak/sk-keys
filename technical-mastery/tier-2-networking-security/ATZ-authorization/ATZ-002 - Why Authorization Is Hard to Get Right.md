---
id: ATZ-002
title: "Why Authorization Is Hard to Get Right"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-001
used_by: ATZ-013, ATZ-026, ATZ-040, ATZ-050
related: ATZ-001, ATZ-003, ATZ-004
tags:
  - security
  - authorization
  - foundational
  - mental-model
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 2
permalink: /technical-mastery/authorization/why-authorization-is-hard-to-get-right/
---

⚡ **TL;DR** - Authorization is conceptually simple but operationally
hard: the gap between business intent ("Alice should see her department's
data") and correct enforcement ("SELECT WHERE org_id=? AND user_id=?") is
where breaches live. The problem compounds at scale: permissions drift,
roles multiply, and the authorization model that worked at 10 users
becomes unmaintainable at 10,000.

---

### 📊 Entry Metadata

| #002 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-001 The Authorization Problem | |
| **Used by:** | ATZ-013, ATZ-026, ATZ-040, ATZ-050 | |
| **Related:** | ATZ-001, ATZ-003, ATZ-004 | |

---

### 🔥 The Problem This Solves

**FIVE REASONS AUTHORIZATION FAILS:**

**1. Permission creep:** Over time, users accumulate permissions
they no longer need. A developer who briefly needed production
database access for an incident still has it 6 months later.
Nobody revokes permissions proactively. Every added permission
is permanent by default.

**2. Role explosion:** A system starts with 3 roles (admin,
manager, user). Over 2 years it has 47 roles, many overlapping,
several redundant. Nobody knows what "supervisor_plus" and
"team_lead_extended" differ in. Role assignments are copied
from similar users rather than defined from policy.

**3. Policy/code drift:** Business rules change faster than code.
"The compliance team must review all reports over $10,000" is
a business policy. If the threshold changes to $5,000, who
updates the authorization code? It may not happen for months.

**4. IDOR blindness:** Developers check "is the user authenticated?"
but not "does this user own this record?" This is invisible in
code review - the check looks correct. Only authorization-specific
testing reveals it.

**5. Context-blindness:** "Alice can access the report" does not
account for "but not from home, not after business hours, and not
on an unmanaged device." Context-dependent authorization requires
richer policy infrastructure than simple role checks.

---

### 📘 Textbook Definition

Authorization hardness refers to the gap between policy intent
and correct enforcement, and the systemic tendency for permissions
to accumulate, drift, and diverge from organizational intent.
The causes are structural: permissions are easy to grant and
costly to audit, policy expression in code is error-prone, and
access patterns change faster than security reviews occur.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Permissions are easy to grant, nearly impossible to revoke
correctly, and drift away from intent over time.

**One analogy:**
> Office key access. It is easy to hand someone a key. It is
> hard to get it back when they leave. It is nearly impossible
> to know, six months later, exactly who has access to which
> rooms, why, and whether they still need it. The same
> dynamic plays out in digital permission systems - just
> faster and at larger scale.

**One insight:**
The hardest part of authorization is not the initial design
but the ongoing maintenance. A correctly designed permission
system at launch will drift into an incorrectly enforced
system within a year without active curation. Authorization
requires operational discipline, not just initial architecture.

---

### 🔩 First Principles Explanation

**THE FIVE HARDNESS DRIVERS:**

```
┌─────────────────────────────────────────────────────┐
│       Why Authorization Drifts Over Time            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GRANT IS EASY                                      │
│  "Give Alice access to X" = one command             │
│                                                     │
│  REVOKE IS HARD                                     │
│  Who knows what Alice should still have?            │
│  Who reviews it? When?                              │
│                                                     │
│  POLICY CHANGES FASTER THAN CODE                    │
│  Business: "New compliance rule effective today"    │
│  Engineering: "That's a deployment, needs a sprint" │
│                                                     │
│  TESTING IS EXPLICIT, NOT INCIDENTAL               │
│  IDOR doesn't throw exceptions - it silently works  │
│  Auth failures require specific test cases          │
│                                                     │
│  CONTEXT IS INVISIBLE TO SIMPLE ROLE CHECKS         │
│  "Can Alice access reports?" is not one question -  │
│  it is 50 context-dependent sub-questions           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**The asymmetry of permission management:**

Adding a permission: instant, low friction, usually done by
an engineer or ops person in under a minute.

Removing a permission: requires knowing who has it (audit),
why they were granted it (history), whether they still need
it (business validation), who to ask (ownership unclear),
and what breaks if it is removed (dependency analysis). This
takes days to do correctly - and is usually deferred forever.

---

### 💻 Code Examples

**Example - Permission creep in practice**

```sql
-- Six months of production permission grants
-- (common in organizations without access review)
SELECT u.email, r.name as role, g.granted_at
FROM user_roles ur
JOIN users u ON u.id = ur.user_id
JOIN roles r ON r.id = ur.role_id
JOIN grant_history g ON g.role_id = r.id
WHERE g.granted_at < NOW() - INTERVAL '90 days'
  AND u.status = 'ACTIVE'
ORDER BY g.granted_at;

-- Typical finding: 40% of active users have roles
-- they haven't used in 90+ days.
-- These are attack surface - compromised accounts
-- with stale high permissions = maximum blast radius.
```

**Example - Authorization test coverage (what teams miss)**

```java
// Most teams test the happy path:
@Test
void aliceCanReadOwnInvoice() {
    mockMvc.perform(get("/invoices/1001")
        .with(user("alice")))
        .andExpect(status().isOk());
}

// Few teams test the authorization boundary (what prevents IDOR):
@Test
void aliceCannotReadBobsInvoice() {
    // Alice requests Bob's invoice ID
    mockMvc.perform(get("/invoices/2002")
        .with(user("alice")))
        .andExpect(status().isForbidden());
}

@Test
void unauthenticatedCannotReadAnyInvoice() {
    mockMvc.perform(get("/invoices/1001"))
        .andExpect(status().isUnauthorized());
}
// The second and third tests are the authorization tests.
// Most code reviews never check if they exist.
```

---

### ⚠️ Common Failure Modes

**Role explosion (symptoms and fix):**

```
Symptom:
  - 100+ roles in the role table
  - Many roles have nearly identical permissions
  - No documentation on what "editor_plus" vs "editor"
    means or who decided the distinction
  - Access requests result in copying another user's roles

Root cause:
  Roles created ad-hoc for each access request instead of
  designed from a role matrix.

Fix:
  1. Conduct role rationalization: group by job function
  2. Define canonical roles (3-7 is ideal; <20 is manageable)
  3. Migrate users to canonical roles
  4. Automate new-user provisioning from job title → roles
  5. Make role creation require approval; roles are expensive
```

**No access review process:**

```
Symptom:
  Security audit reveals employees who left 6 months ago
  still have active access. Current employees have roles
  from previous positions they no longer hold.

Fix:
  Quarterly access review: report all (user, role, last_used)
  tuples. Manager certifies or revokes each. Access not
  certified in 30 days is automatically revoked.
  Tooling: AWS IAM Access Analyzer, Okta Access Certifications,
  or custom query + email workflow.
```

---

### 🔭 At Scale

The authorization hardness problem scales super-linearly.
At 100 users with 10 resources: 1,000 potential permission
combinations - manually auditable. At 10,000 users with 500
resources: 5 million combinations - requires automated tooling.
At 1M users: no human review is possible; authorization must
be model-driven (RBAC/ABAC/ReBAC with automated provisioning
from HR systems) and continuously audited via anomaly detection.

---

*Authorization category: ATZ | Entry: ATZ-002 | v5.0*