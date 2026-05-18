---
id: ATZ-003
title: "Authorization vs Access Control - Terminology"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-001
used_by: ATZ-006, ATZ-013, ATZ-040
related: ATZ-001, ATZ-002, ATH-004
tags:
  - security
  - authorization
  - access-control
  - foundational
  - mental-model
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 3
permalink: /technical-mastery/authorization/authorization-vs-access-control-terminology/
---

⚡ **TL;DR** - "Authorization" and "access control" are often used
interchangeably but are technically distinct: authorization is the
decision (may this subject perform this action?), access control is
the enforcement (blocking or allowing the request based on that
decision). Authentication, authorization, and access control form
a sequential chain - each feeds the next.

---

### 📊 Entry Metadata

| #003 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-001 The Authorization Problem | |
| **Used by:** | ATZ-006, ATZ-013, ATZ-040 | |
| **Related:** | ATZ-001, ATZ-002, ATH-004 | |

---

### 📘 Textbook Definition

Authorization is the process of evaluating whether an
authenticated subject is permitted to perform an action
on a resource - producing an allow/deny decision.
Access control is the broader mechanism that enforces
authorization decisions: the gates, middleware, and
policy enforcement points that prevent unauthorized
operations from completing. Access control = authorization
(decision) + enforcement (mechanism). Authentication,
authorization, and access control are sequential layers:
authentication establishes identity, authorization evaluates
permission, access control enforces the outcome.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Authorization is the decision; access control is the
enforcement of that decision.

**One analogy:**
> A bouncer at a club has a guest list (the policy).
> Authorization is the bouncer consulting the list and
> deciding "yes" or "no." Access control is the physical
> act of letting someone through the rope or turning them
> away. The decision and the enforcement are conceptually
> separate even if done by the same person.

**One insight:**
In software systems, the place where the decision is made
(policy decision point / PDP) and the place where it is
enforced (policy enforcement point / PEP) are often in
different parts of the code or on different servers entirely.
Understanding this split is essential for designing systems
where authorization decisions are consistent and auditable.

---

### 🔩 First Principles Explanation

**THE SECURITY MODEL LAYERS:**

```
┌─────────────────────────────────────────────────────┐
│        Authentication → Authorization → Access Control│
├─────────────────────────────────────────────────────┤
│                                                     │
│  LAYER 1: AUTHENTICATION                            │
│  Question: Who is this?                             │
│  Input: credential (password, token, cert)          │
│  Output: verified identity principal                │
│  Failure: 401 Unauthorized                          │
│                                                     │
│  LAYER 2: AUTHORIZATION                             │
│  Question: May this identity do this?               │
│  Input: identity + action + resource                │
│  Output: allow / deny decision                      │
│  Failure: 403 Forbidden                             │
│                                                     │
│  LAYER 3: ACCESS CONTROL                            │
│  Question: Is the authorization decision enforced?  │
│  Input: the allow/deny decision                     │
│  Output: request proceeds or is blocked             │
│  Failure: 403 Forbidden (same as authz failure)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Key terminology:**

| Term | Precise meaning |
|---|---|
| **Authorization** | The decision: may subject S perform action A on resource R? |
| **Access control** | The enforcement mechanism for authorization decisions |
| **Policy** | The rules that define authorization decisions |
| **Permission** | A specific (action, resource) pair that is allowed |
| **Privilege** | Elevated permission set (admin, root, superuser) |
| **PDP** (Policy Decision Point) | Where authorization decisions are evaluated |
| **PEP** (Policy Enforcement Point) | Where decisions are enforced in the request flow |
| **PIP** (Policy Information Point) | Where context data is fetched for evaluation |

**PDP/PEP separation - why it matters:**

If PDP and PEP are the same code in every service, every
authorization change requires deploying every service. If
PDP is a centralized service and PEP is lightweight middleware,
policy changes happen in one place and propagate immediately.

```
Monolith (PDP == PEP, inline):
  service A has its own auth check code
  service B has its own auth check code
  service C has its own auth check code
  → policy change = 3 deployments, risk of inconsistency

Centralized PDP + distributed PEP:
  OPA sidecar on each service (PEP)
  Central OPA policy server (PDP) with policy files
  → policy change = update one policy file, propagates to all
```

---

### 💻 Code Examples

**Example - Inline PDP+PEP (simple, common in monoliths)**

```java
// Both decision and enforcement happen here
@GetMapping("/reports/{id}")
public Report getReport(@PathVariable Long id,
                        @AuthUser User user) {
    Report report = reportRepo.findById(id)
        .orElseThrow(NotFoundException::new);
    // Decision: may user read this report?
    if (!report.getOrgId().equals(user.getOrgId())) {
        // Enforcement: block the request
        throw new ForbiddenException();
    }
    return report; // access granted
}
```

**Example - Separated PDP (centralized) + PEP (middleware)**

```java
// PEP: Spring Security method-level enforcement
@GetMapping("/reports/{id}")
@PreAuthorize("@authzService.canRead(#user, #id)")
public Report getReport(@PathVariable Long id,
                        @AuthUser User user) {
    return reportRepo.findById(id).orElseThrow();
}

// PDP: centralized decision logic
@Service
public class AuthzService {
    public boolean canRead(User user, Long reportId) {
        // Could call OPA, check DB, evaluate policy
        Report report = reportRepo.findById(reportId)
            .orElse(null);
        if (report == null) return false;
        return report.getOrgId().equals(user.getOrgId());
    }
}
// Changing "who can read reports" = change AuthzService only
// Not every endpoint handler
```

---

### 🔭 At Scale

At microservices scale (50+ services), maintaining consistent
authorization across services requires the PDP/PEP separation.
Each service runs a lightweight PEP (OPA sidecar, middleware,
annotation). The PDP is a central policy engine with versioned
policies. A compliance-driven policy change (e.g., "all
financial data access requires MFA re-verification in last
10 minutes") is a policy file change, not 50 service deployments.

---

*Authorization category: ATZ | Entry: ATZ-003 | v5.0*