---
id: ATZ-056
title: "Formal RBAC Theory (Sandhu 1996)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-006, ATZ-013, ATZ-014
used_by: ATZ-057, ATZ-060
related: ATZ-006, ATZ-014, ATZ-057
tags:
  - security
  - authorization
  - rbac
  - formal-model
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/authorization/formal-rbac-theory-sandhu-1996/
---

⚡ **TL;DR** - Ravi Sandhu's 1996 RBAC96 paper formalized
Role-Based Access Control as a family of four models (RBAC0
through RBAC3). RBAC0: basic roles, users, permissions. RBAC1:
adds role hierarchies (senior roles inherit junior permissions).
RBAC2: adds constraints (separation of duty - can't hold two
conflicting roles). RBAC3: combines hierarchies and constraints.
This formal foundation explains why flat RBAC is insufficient
for enterprise (need hierarchies and SoD), and is the theoretical
basis for NIST RBAC standards and implementations like Keycloak.

---

### 📊 Entry Metadata

| #056 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-006 RBAC, ATZ-013 RBAC Patterns, ATZ-014 Hierarchical RBAC | |
| **Used by:** | ATZ-057, ATZ-060 | |
| **Related:** | ATZ-006 RBAC, ATZ-014 Hierarchical RBAC, ATZ-057 Bell-LaPadula | |

---

### 📘 Textbook Definition

The RBAC96 model family (Sandhu, Coyne, Youman, Ferraiolo,
1996, IEEE Computer) provides a formal framework for RBAC
with four progressive models. RBAC0 (core): Users (U), Roles
(R), Permissions (P). UA: U x R (user-role assignment). PA:
P x R (permission-role assignment). Sessions: a user activates
a subset of roles. RBAC1 (hierarchical): adds role hierarchy
RH (partial order on R). Senior roles implicitly hold
permissions of junior roles. RBAC2 (constrained): adds
constraints, notably Separation of Duty (SoD). Static SoD:
user cannot be assigned to two mutually exclusive roles. Dynamic
SoD: user cannot activate two conflicting roles simultaneously.
RBAC3 (combined): RBAC1 + RBAC2. The NIST RBAC standard
(2004) is largely based on RBAC96.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         RBAC96 Model Family                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  RBAC0 (Core - minimum viable RBAC):                   │
│  Users -> Roles -> Permissions                         │
│  Sessions: user activates subset of assigned roles     │
│  Permission review = check PA table                    │
│                                                        │
│  RBAC1 (+ Hierarchy):                                  │
│  Role hierarchy RH: senior >= junior (partial order)   │
│  Example: Director >= Manager >= Employee              │
│  Director inherits all Manager and Employee perms      │
│  Benefits: reduces role explosion                      │
│  Danger: deep hierarchies hide permission scope        │
│                                                        │
│  RBAC2 (+ Constraints):                                │
│  Static SoD: user cannot hold Cashier AND Approver     │
│  Dynamic SoD: cannot activate both in same session     │
│  Mutual exclusion enforced at assignment OR activation  │
│  Use case: financial controls, fraud prevention        │
│                                                        │
│  RBAC3 (Full: RBAC1 + RBAC2):                          │
│  Senior roles do NOT inherit mutually exclusive roles  │
│  Complex SoD with inheritance is enterprise RBAC       │
│  Implemented by: Keycloak, LDAP, enterprise IAM        │
│                                                        │
│  PRACTICAL IMPLICATION:                                │
│  "Our RBAC doesn't support SoD" = using only RBAC0     │
│  For finance/compliance: need RBAC2 or RBAC3           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Static Separation of Duty enforcement**

```java
// Static SoD: user cannot be assigned to mutually
// exclusive roles simultaneously
@Service
public class RoleAssignmentService {

    // Mutually exclusive role pairs (SoD constraints)
    private static final Map<String, String> MUTEX_ROLES =
        Map.of(
            "PAYMENT_REQUESTER", "PAYMENT_APPROVER",
            "ACCOUNT_CREATOR", "ACCOUNT_AUDITOR",
            "TRADER", "RISK_MANAGER"
        );

    @Transactional
    public void assignRole(String userId, String role) {
        Set<String> currentRoles =
            userRoleRepo.findRolesForUser(userId);

        // SoD check: does assigning this role conflict?
        String conflictingRole = MUTEX_ROLES.get(role);
        if (conflictingRole != null
                && currentRoles.contains(conflictingRole)) {
            throw new SeparationOfDutyViolationException(
                "Cannot assign role " + role +
                " to user " + userId +
                ": conflicts with existing role " +
                conflictingRole +
                " (static SoD constraint)");
        }
        // Also check reverse direction
        MUTEX_ROLES.forEach((r1, r2) -> {
            if (r2.equals(role)
                    && currentRoles.contains(r1)) {
                throw new SeparationOfDutyViolationException(
                    "SoD conflict: " + r1 + " vs " + role);
            }
        });

        userRoleRepo.assignRole(userId, role);
        auditLog.record("ROLE_ASSIGNED", userId, role);
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-056 | v5.0*