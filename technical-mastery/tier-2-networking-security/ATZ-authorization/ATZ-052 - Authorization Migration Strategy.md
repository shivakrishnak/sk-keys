---
id: ATZ-052
title: "Authorization Migration Strategy"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-013, ATZ-027, ATZ-030, ATZ-050, ATZ-051
used_by: ATZ-053, ATZ-062
related: ATZ-049, ATZ-051, ATZ-053
tags:
  - security
  - authorization
  - migration
  - strategy
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/authorization/authorization-migration-strategy/
---

⚡ **TL;DR** - Migrating authorization - from hardcoded role checks
scattered across services to a centralized OPA policy engine, or
from a custom RBAC table to a standards-based system - is high-risk
because a mistake either over-denies (service outage) or under-
denies (security hole). The safe pattern: run old and new
authorization systems in parallel (shadow mode), compare decisions,
fix discrepancies, then gradually shift traffic. Never cut over
all enforcement at once.

---

### 📊 Entry Metadata

| #052 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC Patterns, ATZ-027 OPA, ATZ-030 Externalized Authz, ATZ-050 Enterprise Arch, ATZ-051 Central vs Dist | |
| **Used by:** | ATZ-053, ATZ-062 | |
| **Related:** | ATZ-049 Microservices Fleet, ATZ-051 Central vs Distributed, ATZ-053 Policy-as-Code | |

---

### 📘 Textbook Definition

Authorization migration is the process of transitioning an
existing access control system from one model, technology, or
architecture to another. Common scenarios: (1) hardcoded
if-else role checks to a policy engine (OPA), (2) application-
level RBAC to externalized authorization, (3) RBAC to ABAC or
ReBAC, (4) monolith auth to microservices distributed auth,
(5) custom permission tables to a standards-based system.
Migration risks: over-denial (legitimate users blocked, service
disruption), under-denial (security holes introduced during
transition), and policy drift (old and new systems disagree,
leading to inconsistent decisions). Shadow mode (run both systems,
log differences, don't enforce the new one yet) is the safe migration pattern.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authorization Migration Phases                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PHASE 1: Shadow Mode (weeks 1-4)                      │
│  - Old auth: enforcing                                 │
│  - New auth (OPA): running, logging, NOT enforcing     │
│  - Compare: log every case where old != new            │
│  - Fix: update OPA policies to match intended behavior │
│  Success: 0 discrepancies for 1 week                   │
│                                                        │
│  PHASE 2: Canary Enforcement (weeks 5-6)               │
│  - 10% of requests: enforce OPA, disable old check     │
│  - 90%: still use old auth                             │
│  - Monitor: error rates, access denied metrics         │
│  - Fix any issues found                                │
│  Success: no increase in 403/unauthorized errors       │
│                                                        │
│  PHASE 3: Progressive Rollout (weeks 7-10)             │
│  - 10% -> 25% -> 50% -> 100% on new auth              │
│  - Each stage: monitor for 48 hours                    │
│  - Rollback trigger: >0.1% increase in 403 rate        │
│                                                        │
│  PHASE 4: Cleanup (weeks 11-12)                        │
│  - Remove old authorization code                       │
│  - Remove old permission tables (after audit)          │
│  - Documentation + runbook update                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Shadow mode authorization comparison**

```java
@Component
public class ShadowAuthzService {

    public boolean isAllowed(String userId,
                              String resource,
                              String action) {
        // OLD: existing RBAC check
        boolean oldDecision =
            legacyRbacService.hasPermission(
                userId, resource, action);

        // NEW: OPA (not enforcing yet)
        boolean newDecision = opaClient.isAllowed(
            userId, resource, action);

        if (oldDecision != newDecision) {
            // Log discrepancy for investigation
            // Never log sensitive data or user content
            log.warn("Auth decision mismatch: " +
                "user={}, resource={}, action={}, " +
                "old={}, new={}",
                userId, resource, action,
                oldDecision, newDecision);
            metrics.increment("authz.shadow.mismatch",
                Tags.of("resource", resource,
                         "action", action));
        }

        // Shadow mode: enforce OLD decision
        // When mismatch rate = 0 for 1 week:
        // switch to enforcing NEW decision
        return oldDecision;
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-052 | v5.0*