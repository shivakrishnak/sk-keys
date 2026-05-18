---
id: ATZ-018
title: "JWT Claims for Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-016, ATZ-017
used_by: ATZ-026, ATZ-030
related: ATZ-016, ATZ-017, ATZ-030
tags:
  - security
  - authorization
  - jwt
  - claims
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/authorization/jwt-claims-for-authorization/
---

⚡ **TL;DR** - JWT authorization claims embed authorization context
directly into the token: roles, permissions, scopes, tenant ID,
custom attributes. The API server reads these claims without any
database call. The design tension: include too few claims and every
request requires a database lookup; include too many and tokens become
bloated, hard to manage, and contain stale data. The right design:
stable identity facts in the token, dynamic or sensitive authorization
state fetched per-request.

---

### 📊 Entry Metadata

| #018 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-016, ATZ-017 | |
| **Used by:** | ATZ-026, ATZ-030 | |
| **Related:** | ATZ-016 Claims-Based, ATZ-017 OAuth Scopes, ATZ-030 Externalized Authorization | |

---

### 📘 Textbook Definition

JWT (JSON Web Token) authorization claims are name-value pairs
embedded in the token payload that carry authorization context.
Standard JWT claims (RFC 7519) include `sub` (subject), `iss`
(issuer), `aud` (audience), `exp` (expiry), and `iat` (issued-at).
Custom authorization claims extend these with application-specific
context: `roles`, `permissions`, `tenant_id`, `subscription`,
`clearance`. JWT claim design must balance completeness (enough
context for authorization decisions) against token size, staleness
risk, and privacy (minimal user data per GDPR recommendation).

---

### ⚙️ How It Works (Mechanism)

**JWT claim categories for authorization:**

```
┌────────────────────────────────────────────────────────┐
│           JWT Claim Design for Authorization           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STANDARD REGISTERED CLAIMS (always include):          │
│  sub: user ID or email (identity anchor)               │
│  iss: token issuer URL (validate token origin)         │
│  aud: intended audience (prevent cross-service use)    │
│  exp: expiration time (reject expired tokens)          │
│  iat: issued at (detect very new tokens in some cases) │
│  jti: unique token ID (for revocation/audit)           │
│                                                        │
│  AUTHORIZATION CLAIMS (application-specific):          │
│  roles:      ["EDITOR", "REPORTER"]  (RBAC)            │
│  scope:      "orders:read orders:write" (OAuth)        │
│  tenant_id:  "acme-corp" (multi-tenant routing)        │
│  org_id:     "42" (organization scoping)               │
│                                                        │
│  AVOID IN JWT (stale, sensitive, or too large):        │
│  email:      leaks PII in access logs                  │
│  all_permissions: large, changes often                 │
│  session_data: should be server-side                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - JWT with authorization claims (Spring)**

```java
// Issuing a JWT with authorization claims
public String issueToken(User user) {
    Instant now = Instant.now();
    return Jwts.builder()
        // Standard claims
        .subject(user.getId().toString())
        .issuer("https://auth.example.com")
        .audience().add("https://api.example.com").and()
        .issuedAt(Date.from(now))
        .expiration(Date.from(now.plusSeconds(900))) // 15 min
        .id(UUID.randomUUID().toString()) // jti
        // Authorization claims
        .claim("roles", user.getRoleNames())
        .claim("tenant_id", user.getTenantId())
        .claim("org_id", user.getOrganizationId())
        .claim("subscription", user.getSubscriptionTier())
        // Sign with private key (RS256)
        .signWith(privateKey, Jwts.SIG.RS256)
        .compact();
}

// Consuming claims in a resource server
@GetMapping("/reports")
public List<Report> listReports(
        @AuthenticationPrincipal Jwt jwt) {
    String tenantId = jwt.getClaimAsString("tenant_id");
    List<String> roles = jwt.getClaimAsStringList("roles");

    if (!roles.contains("REPORTER")
            && !roles.contains("EDITOR")) {
        throw new ForbiddenException();
    }
    // Tenant-scoped query: multi-tenant isolation
    return reportRepo.findByTenantId(tenantId);
}
```

**Example - BAD vs GOOD: audience validation**

```java
// BAD: no audience validation
// Order service accepts tokens intended for payment service
JwtDecoder decoder = NimbusJwtDecoder
    .withJwkSetUri(jwksUri)
    .build();
// Any valid token works on any service

// GOOD: validate audience restricts token to this service
JwtDecoder decoder = NimbusJwtDecoder
    .withJwkSetUri(jwksUri)
    .build();
// Spring Security additional validation:
http.oauth2ResourceServer(oauth2 -> oauth2
    .jwt(jwt -> jwt
        .decoder(decoder)
        .jwtAuthenticationConverter(converter -> {
            // Validate aud claim matches this service
            JwtClaimValidator<List<String>> audienceValidator =
                new JwtClaimValidator<>(
                    "aud",
                    aud -> aud.contains(
                        "https://order-service.example.com")
                );
        })
    )
);
// Token for payment-service cannot be replayed to order-service
```

**Example - FAILURE: sensitive PII in JWT visible in logs**

```
Problem:
  JWT payload includes: "email": "alice@corp.com"
  API gateway logs: Authorization: Bearer eyJ...(JWT)
  Base64 decode reveals email in plain text in log files.
  
  Even if JWT is signed, payload is not encrypted.
  Anyone who can read logs can read email addresses.
  GDPR/privacy violation if logs are shared.

Fix:
  Use sub (user ID) not email in JWT payload.
  If email is needed, fetch it from user service on demand.
  Never include:
    - Email addresses
    - Names
    - Phone numbers
    - Any PII that is not strictly necessary for auth
  JWT is not encrypted at rest - treat payload as visible.
  Use JWE (JSON Web Encryption) if confidentiality needed.
```

---

*Authorization category: ATZ | Entry: ATZ-018 | v5.0*