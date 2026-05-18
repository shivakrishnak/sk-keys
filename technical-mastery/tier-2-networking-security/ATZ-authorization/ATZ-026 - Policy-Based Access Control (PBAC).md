---
id: ATZ-026
title: "Policy-Based Access Control (PBAC)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-015
used_by: ATZ-027, ATZ-028, ATZ-029, ATZ-030
related: ATZ-015, ATZ-027, ATZ-030
tags:
  - security
  - authorization
  - pbac
  - policy
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/authorization/policy-based-access-control-pbac/
---

⚡ **TL;DR** - Policy-Based Access Control (PBAC) generalizes RBAC
and ABAC: access decisions are made by evaluating declarative
policies rather than hardcoded logic. A policy is a set of rules
("if user.department == 'Finance' AND resource.sensitivity < 3
THEN allow:read"). The key benefit is externalization: policies
live outside application code and can be updated without
redeployment. The key challenge: policy complexity compounds -
policies interact, conflict, and their combined effect is hard
to reason about at scale.

---

### 📊 Entry Metadata

| #026 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-015 ABAC | |
| **Used by:** | ATZ-027 OPA, ATZ-028 Cedar, ATZ-029 Rego, ATZ-030 Externalized | |
| **Related:** | ATZ-015 ABAC, ATZ-027 OPA, ATZ-030 Externalized Auth | |

---

### 📘 Textbook Definition

Policy-Based Access Control (PBAC) is an access control paradigm
in which authorization decisions are governed by explicit,
declarative policies rather than by role assignments or hardcoded
rules. A policy engine evaluates policies (sets of rules) against
a request context (subject attributes, resource attributes, action,
environment) and returns a decision (allow/deny). PBAC subsumes
RBAC (a role is a policy) and ABAC (attributes form policy
conditions). Examples: AWS IAM policies, OPA/Rego policies,
Cedar policies, XACML, Spring Security method security.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            PBAC Request Evaluation Flow                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Authorization Request:                                │
│  {                                                     │
│    subject: {user_id: "alice",                         │
│               department: "Finance",                   │
│               clearance: 2},                           │
│    resource: {id: "report-2024-q4",                    │
│                type: "report",                         │
│                sensitivity: 1,                         │
│                owner: "finance-team"},                 │
│    action:   "read",                                   │
│    context:  {time: "09:30 UTC",                       │
│                ip: "10.0.0.1"}                         │
│  }                                                     │
│                                                        │
│  Policy Engine Evaluation:                             │
│  1. Load applicable policies for (user, resource, action)
│  2. Evaluate conditions for each policy                │
│  3. Combine decisions per combination algorithm:       │
│     - deny-overrides: any DENY -> DENY                 │
│     - permit-overrides: any ALLOW -> ALLOW             │
│     - first-applicable: stop at first matching rule    │
│  4. Return: ALLOW, DENY, or INDETERMINATE              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security method-level PBAC**

```java
@Service
public class ReportService {

    // Policy expressed declaratively via SpEL expression
    // Access allowed only if:
    // - user has VIEWER role AND is in Finance dept
    //   OR user has ADMIN role
    @PreAuthorize(
        "(hasRole('VIEWER') and "
        + "@deptService.isInDepartment("
        + "authentication.name, 'Finance')) "
        + "or hasRole('ADMIN')"
    )
    public Report getFinancialReport(String reportId) {
        return reportRepo.findById(reportId)
            .orElseThrow(NotFoundException::new);
    }

    // Object-level policy: user can only edit own reports
    @PreAuthorize(
        "hasRole('EDITOR') and "
        + "#report.ownerId == authentication.name"
    )
    public Report updateReport(Report report) {
        return reportRepo.save(report);
    }

    // Post-filter: filter result set by ownership
    @PostFilter(
        "filterObject.ownerId == authentication.name "
        + "or hasRole('ADMIN')"
    )
    public List<Report> getAllReports() {
        return reportRepo.findAll();
    }
}
```

**Example - PBAC conflict: policy order matters**

```java
// POLICY 1: Finance team can read all Finance reports
// POLICY 2: Reports marked CONFIDENTIAL require MANAGER role

// Evaluation for alice (Finance, not Manager) on
// a CONFIDENTIAL Finance report:
// P1: ALLOW (alice is Finance)
// P2: DENY  (alice is not Manager)
// Combined result depends on combination algorithm:
//   deny-overrides: DENY (safer, more restrictive)
//   permit-overrides: ALLOW (less safe)

// Most authorization systems default to deny-overrides
// because it is more secure (explicit allow required)
```

---

*Authorization category: ATZ | Entry: ATZ-026 | v5.0*