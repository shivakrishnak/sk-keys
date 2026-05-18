---
id: ATZ-061
title: "Authorization as Explicit Trust Assertion (Pattern Bridge)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-015, ATZ-027, ATZ-036, ATZ-050, ATZ-055
used_by: ATZ-062
related: ATZ-055, ATZ-062
tags:
  - security
  - authorization
  - pattern-bridge
  - trust
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/authorization/authorization-as-explicit-trust-assertion-pattern-bridge/
---

**TL;DR:** The unifying mental model across all authorization
mechanisms is "explicit trust assertion": every access decision
is an explicit claim that "subject S is permitted to perform
action A on resource R under conditions C." RBAC asserts: "Alice
is in role Admin, and Admins may delete users." ABAC asserts:
"Alice's department=Finance, and Finance members may read budget
reports on weekdays during business hours." ReBAC asserts:
"Alice owns document D, and owners may edit." Every authorization
system is just a different way of structuring and evaluating
these assertions.

---

### Textbook Definition

Authorization as explicit trust assertion is a unifying
conceptual model that views all access control decisions as
formalized trust statements: "I (the PDP) assert that principal
P is authorized to perform action A on resource R because
condition C holds." This model enables systematic design of
authorization systems by forcing explicit answers to: who is
the principal? what is the resource granularity? what actions
are controlled? what conditions govern access? and who audits
these assertions? The pattern bridge connects RBAC (role-based
conditions), ABAC (attribute-based conditions), ReBAC
(relationship-based conditions), and ZTA (risk-based conditions)
as special cases of the same general model.

---

### Pattern Bridge Analysis

```
ALL AUTHORIZATION MODELS = explicit trust assertions:

RBAC assertion:
  Subject: user with role=ADMIN
  Resource: /admin/users/*
  Action: DELETE
  Condition: user.roles contains 'ADMIN'
  Policy: "ADMIN role holders may DELETE admin users"

ABAC assertion:
  Subject: user with dept=Finance, clearance=3
  Resource: document with classification=internal
  Action: READ
  Condition: user.dept in resource.allowed_depts
             AND user.clearance >= resource.required_level
             AND env.time in business_hours
  Policy: "Finance members with clearance >= 3 may read
            internal docs during business hours"

ReBAC (Zanzibar) assertion:
  Subject: user:alice
  Resource: document:budget-2024
  Action: edit
  Condition: exists path in tuple graph:
             user:alice -> viewer/owner -> document:budget
  Policy: "Owners and editors of a doc may edit it"

ZTA assertion:
  Subject: user:alice (trust_score=85)
  Resource: payment-api/transfer
  Action: POST
  Condition: trust_score >= 80
             AND mfa_verified = true
             AND device.managed = true
             AND risk_score < 30
  Policy: "High-trust verified users on managed devices
            with low risk score may initiate transfers"

COMMON STRUCTURE (all models):
  GRANT(principal, action, resource) IF condition(context)
  Different models = different condition expressiveness
  RBAC: role membership (simplest)
  ABAC: arbitrary attribute expressions (most flexible)
  ReBAC: graph traversal (best for hierarchical resources)
  ZTA: ML-scored risk context (most dynamic)
```

---

### Code Examples

**Example - Unified authorization interface across models**

```java
// Unified authorization: same interface, different backends
// Enables mixing RBAC + ABAC + ReBAC in one system
public interface AuthorizationEngine {
    /**
     * Evaluate: is this principal allowed to perform
     * this action on this resource in this context?
     */
    AuthzDecision evaluate(AuthzRequest request);
}

// RBAC backend
public class RbacAuthorizationEngine
        implements AuthorizationEngine {
    public AuthzDecision evaluate(AuthzRequest req) {
        Set<String> roles = roleService.getRoles(
            req.getPrincipal().getId());
        boolean allowed = permissionService
            .hasPermission(roles, req.getAction(),
                req.getResource());
        return AuthzDecision.of(allowed,
            "RBAC: roles=" + roles);
    }
}

// OPA (ABAC/policy) backend
public class OpaAuthorizationEngine
        implements AuthorizationEngine {
    public AuthzDecision evaluate(AuthzRequest req) {
        Map<String, Object> input = buildOpaInput(req);
        boolean allowed =
            opaClient.evaluate("authz/allow", input);
        return AuthzDecision.of(allowed,
            "OPA: policy evaluation");
    }
}

// Composite: RBAC for coarse, OPA for fine-grained
public class CompositeAuthorizationEngine
        implements AuthorizationEngine {
    public AuthzDecision evaluate(AuthzRequest req) {
        // First: RBAC (fast, coarse-grained)
        AuthzDecision rbac = rbacEngine.evaluate(req);
        if (!rbac.isAllow()) {
            return rbac; // Denied at RBAC level
        }
        // Second: OPA (for fine-grained conditions)
        if (req.getResource().requiresFineGrained()) {
            return opaEngine.evaluate(req);
        }
        return rbac; // RBAC sufficient
    }
}
// Pattern bridge: ALL engines implement same interface
// Can compose, layer, or swap implementations freely
```

---

*Authorization category: ATZ | Entry: ATZ-061 | v5.0*