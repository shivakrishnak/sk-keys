---
id: ATZ-016
title: "Claims-Based Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-007, ATZ-015
used_by: ATZ-017, ATZ-018, ATZ-026, ATZ-030
related: ATZ-015, ATZ-017, ATZ-018
tags:
  - security
  - authorization
  - claims
  - jwt
  - oidc
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/authorization/claims-based-authorization/
---

⚡ **TL;DR** - Claims-based authorization makes access decisions based
on claims embedded in a token (JWT, SAML assertion). A claim is a
key-value statement about the subject: `"department": "finance"`,
`"clearance": "SECRET"`, `"subscription_tier": "premium"`. The key
advantage: the authorization decision can happen without a database
lookup - all needed context is in the token. The risk: stale claims
(the token says finance, but the user moved to engineering last week).

---

### 📊 Entry Metadata

| #016 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-007, ATZ-015 | |
| **Used by:** | ATZ-017, ATZ-018, ATZ-026, ATZ-030 | |
| **Related:** | ATZ-015 ABAC, ATZ-017 OAuth Scopes, ATZ-018 JWT Claims | |

---

### 📘 Textbook Definition

Claims-based authorization (popularized by Microsoft's WIF in
2010, now standard via OAuth 2.0/OIDC and SAML) makes authorization
decisions based on verified assertions (claims) embedded in a
security token. A claim is a name-value pair that the token issuer
(identity provider) asserts about the subject, such as role, group
membership, department, or custom attributes. Resource servers
evaluate claims to determine whether an action is permitted without
querying a separate authorization store. Claims-based authorization
is a form of attribute-based access control where subject attributes
are pre-fetched into the token rather than retrieved per-request.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The token carries "facts about you"; the server makes
authorization decisions from those facts without asking
anyone else.

**JWT claims example:**

```json
{
  "sub": "alice@company.com",
  "roles": ["editor", "reporter"],
  "department": "editorial",
  "clearance": 2,
  "subscription": "premium",
  "tenant_id": "acme-corp"
}
```

The API server reads these claims and decides:
- "EDITOR role" → can write articles
- "clearance: 2" → can access CONFIDENTIAL content
- "subscription: premium" → can access premium features
No additional database calls needed.

---

### 💻 Code Examples

**Example - Spring Security claims-based authorization**

```java
// Extract claims from JWT and make authorization decisions
@GetMapping("/reports/confidential")
@PreAuthorize(
    "#jwt.getClaim('clearance') >= 2 " +
    "&& #jwt.getClaim('department') == 'editorial'")
public List<Report> getConfidentialReports(
        @AuthenticationPrincipal Jwt jwt) {
    // clearance and department are claims in the JWT
    return reportRepo.findByClassification("CONFIDENTIAL");
}

// Custom SpEL expression using claims
@GetMapping("/api/premium-feature")
public ResponseEntity<?> premiumFeature(
        @AuthenticationPrincipal Jwt jwt) {
    String subscription = jwt.getClaimAsString("subscription");
    if (!"premium".equals(subscription)
            && !"enterprise".equals(subscription)) {
        return ResponseEntity.status(403)
            .body("Premium subscription required");
    }
    return ResponseEntity.ok(generatePremiumContent());
}
```

**Example - BAD vs GOOD: overly broad claims**

```json
// BAD: embed all permissions in the JWT
{
  "permissions": [
    "orders:read", "orders:write", "orders:delete",
    "reports:read", "reports:write", "reports:export",
    "users:read", "users:write", "users:delete",
    "settings:read", "settings:write"
  ]
}
// Token becomes large (adds to every request payload)
// Changing permissions requires re-issuing tokens for all users
// Cannot revoke individual permissions without token rotation

// GOOD: embed roles/attributes, derive permissions on evaluation
{
  "roles": ["EDITOR"],
  "department": "sales",
  "region": "EMEA"
}
// Server-side policy maps EDITOR → {reports:read, reports:write}
// Policy changes deploy without touching tokens
// Token stays small
```

**Example - FAILURE: stale claims cause authorization errors**

```
Scenario:
  Alice has JWT with "department": "finance"
  Alice is moved to "engineering" by HR
  Alice's new HR record: department = engineering
  
  24-hour token validity: Alice's JWT still says "finance"
  for up to 24 hours after the move.
  
  Result: Alice can still access finance reports
  (stale claims grant unwanted access) AND cannot access
  engineering tools (correct claims not in token yet).

Fix options:
  1. Short-lived access tokens (15 min): stale window is small
  2. Token introspection endpoint: validate token live at
     resource server (defeats stateless advantage)
  3. Claim refresh: re-issue tokens on profile change
     (event-driven: HR system → IdP token invalidation)
  4. Hybrid: core identity claims (sub) in token; sensitive
     attributes (department, clearance) looked up per-request
```

---

*Authorization category: ATZ | Entry: ATZ-016 | v5.0*