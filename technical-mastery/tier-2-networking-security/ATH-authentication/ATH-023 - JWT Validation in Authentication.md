---
id: ATH-023
title: "JWT Validation in Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-010, ATH-022
used_by: ATH-031, ATH-032, ATH-045, ATH-047
related: ATH-010, ATH-022, ATH-045
tags:
  - security
  - authentication
  - jwt
  - validation
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/authentication/jwt-validation-in-authentication/
---

⚡ **TL;DR** - JWT validation has eight mandatory checks. Miss any one
and authentication can be bypassed. The most critical: verify the
signature, reject `alg:none`, validate `aud` (prevents tokens meant
for service A being used at service B), validate `exp` (prevents
use of old tokens), and validate `iss` (prevents accepting tokens
from untrusted issuers). Each skipped check is an exploited
vulnerability in production.

---

### 📊 Entry Metadata

| #023 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-010, ATH-022 | |
| **Used by:** | ATH-031, ATH-032, ATH-045, ATH-047 | |
| **Related:** | ATH-010 Token Auth, ATH-022 OIDC, ATH-045 JWT Algorithm Security | |

---

### 📘 Textbook Definition

JWT validation is the process of verifying that a received
JWT is authentic, unexpired, intended for this service, and
issued by a trusted party. The validation steps are defined
in RFC 7519 and OIDC Core 1.0. Proper validation includes:
(1) decode and parse header/payload, (2) verify the algorithm
is acceptable (reject `none`), (3) verify signature using
the correct key, (4) verify `exp` (expiry), (5) verify `nbf`
(not-before, if present), (6) verify `iss` (issuer against
whitelist), (7) verify `aud` (audience matches this service),
and (8) verify `nonce` (in OIDC flows).

---

### ⚙️ How It Works (Mechanism)

**The eight validation steps:**

```
┌────────────────────────────────────────────────────────┐
│             JWT Validation Checklist                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Parse structure (header.payload.signature)         │
│     Reject: malformed JSON, invalid base64url          │
│                                                        │
│  2. Algorithm check                                    │
│     Reject: alg=none (unsigned token accepted as valid)│
│     Accept: RS256, ES256 (asymmetric preferred)        │
│     Warn:   HS256 (symmetric - secret must be shared)  │
│                                                        │
│  3. Signature verification                             │
│     RS256: verify with issuer's RSA public key         │
│     Reject: tampered payload (any claim modification)  │
│                                                        │
│  4. Expiry (exp)                                       │
│     Reject: exp <= now (token expired)                 │
│     Allow: small clock skew tolerance (30-60s)         │
│                                                        │
│  5. Not-before (nbf) if present                        │
│     Reject: nbf > now (token not yet valid)            │
│                                                        │
│  6. Issuer (iss)                                       │
│     Reject: iss not in trusted issuer whitelist        │
│     Accept: "https://auth.example.com" only            │
│                                                        │
│  7. Audience (aud)                                     │
│     Reject: this service's URL not in aud list         │
│     Prevents: token issued for service A used at B     │
│                                                        │
│  8. Nonce (OIDC only)                                  │
│     Verify: nonce matches the per-request value stored │
│     in session before redirecting to IdP               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Complete JWT validation (Spring Security)**

```java
@Bean
public JwtDecoder jwtDecoder() {
    // Build decoder with JWKS key rotation support
    NimbusJwtDecoder decoder = NimbusJwtDecoder
        .withJwkSetUri(
            "https://auth.example.com/.well-known/jwks.json")
        .jwsAlgorithm(SignatureAlgorithm.RS256) // HS256 rejected
        .build();

    // Add custom validators
    OAuth2TokenValidator<Jwt> audienceValidator =
        new JwtClaimValidator<List<String>>("aud",
            aud -> aud.contains("https://api.example.com"));

    OAuth2TokenValidator<Jwt> issuerValidator =
        JwtValidators.createDefaultWithIssuer(
            "https://auth.example.com");

    OAuth2TokenValidator<Jwt> combined =
        new DelegatingOAuth2TokenValidator<>(
            issuerValidator,    // validates iss + exp
            audienceValidator   // validates aud
        );

    decoder.setJwtValidator(combined);
    return decoder;
    // Spring auto-validates: alg, signature, exp, iss, aud
}
```

**Example - BAD: algorithm confusion attack**

```java
// BAD: accepting all algorithms including "none"
// This is the classic JWT algorithm confusion vulnerability
public Claims parseToken(String token) {
    // Don't specify algorithm - use whatever is in header
    return Jwts.parser()
        .setSigningKey(secretKey)
        .parseClaimsJws(token) // VULNERABLE
        .getBody();
}

// Attack:
// Attacker creates header: {"alg":"none","typ":"JWT"}
// Creates payload: {"sub":"admin","roles":["admin"]}
// Creates token: base64(header).base64(payload). (empty sig)
// If server accepts alg=none: this token is "valid"

// GOOD: pin algorithm explicitly
public Claims parseToken(String token) {
    return Jwts.parser()
        .verifyWith(publicKey)          // RS256 public key
        .requireIssuedAt(new Date())    // fail if no iat
        .requireAudience("https://api.example.com")
        .build()
        .parseSignedClaims(token)       // rejects alg=none
        .getPayload();
}
```

---

*Authentication category: ATH | Entry: ATH-023 | v5.0*