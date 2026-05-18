---
id: ATH-031
title: "Bearer Token Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-010, ATH-023, ATH-030
used_by: ATH-032, ATH-045, ATH-046, ATH-047
related: ATH-010, ATH-023, ATH-032
tags:
  - security
  - authentication
  - bearer-token
  - http
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/authentication/bearer-token-authentication/
---

⚡ **TL;DR** - Bearer token authentication means: "whoever bears
(presents) this token is authenticated." There is no cryptographic
binding between the token and the client - unlike a certificate or
hardware key, a stolen bearer token can be used by anyone. The
mitigation stack is: short expiry, HTTPS only (never transmit over
HTTP), token rotation, revocation capability, and sender-constrained
tokens (DPoP) for high-security scenarios. The `Authorization: Bearer`
header is the HTTP standard for token presentation.

---

### 📊 Entry Metadata

| #031 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-010 Tokens, ATH-023 JWT Validation, ATH-030 API Keys | |
| **Used by:** | ATH-032, ATH-045, ATH-046, ATH-047 | |
| **Related:** | ATH-010 Token Auth, ATH-023 JWT Validation, ATH-032 Refresh Tokens | |

---

### 📘 Textbook Definition

A bearer token (RFC 6750) is an opaque or structured security
token where possession of the token itself grants access - there
is no additional proof-of-possession required. The name comes
from "the bearer of this instrument" in financial instruments.
Bearer tokens are transmitted in the HTTP Authorization header
(`Authorization: Bearer <token>`), as a form parameter, or as
a query parameter (deprecated - gets logged). JWTs used as
access tokens are bearer tokens. The security implication:
bearer tokens must be treated as credentials - HTTPS is
mandatory, storage must be secure, and expiry must be short.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            Bearer Token Flow                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Client authenticates (password, OIDC, API key)     │
│  2. Server issues bearer token (JWT or opaque)         │
│  3. Client includes token in every subsequent request: │
│     GET /api/resource                                  │
│     Authorization: Bearer eyJhbGciOiJSUzI1...         │
│                                                        │
│  4. Server validates token:                            │
│     JWT: verify signature + claims (ATH-023)           │
│     Opaque: database lookup of token hash              │
│  5. If valid: process request                          │
│                                                        │
│  TOKEN THEFT SCENARIO:                                 │
│  Attacker intercepts token (XSS, log exposure,         │
│  insecure storage)                                     │
│  → uses token from different IP/device               │
│  → server cannot distinguish: it is a bearer token   │
│                                                        │
│  MITIGATIONS:                                          │
│  Short expiry (15min-1h for access tokens)             │
│  HTTPS everywhere (no token in HTTP)                   │
│  Secure storage (httpOnly cookie or secure storage)    │
│  DPoP binding (binds token to a keypair)               │
│  Token revocation (opaque tokens via DB lookup)        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Bearer token validation (Spring Security)**

```java
@Configuration
@EnableWebSecurity
public class BearerTokenSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http)
            throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            // Spring extracts "Authorization: Bearer <token>"
            // validates as JWT using configured JwtDecoder
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(Customizer.withDefaults())
                // Custom error response for invalid tokens
                .authenticationEntryPoint(
                    (req, res, ex) -> {
                        res.setStatus(401);
                        res.setHeader("WWW-Authenticate",
                            "Bearer realm=\"api\", "
                            + "error=\"invalid_token\"");
                    })
            );
        return http.build();
    }
}
```

**Example - BAD: token in URL query parameter**

```java
// BAD: token in query param
// GET /api/resource?access_token=eyJhbGci...
// This gets logged in:
//   - Web server access logs
//   - CDN/proxy logs
//   - Browser history
//   - Referrer header to linked external sites
// Attacker reads any of these logs -> steals all tokens

// GOOD: Always use Authorization header
// GET /api/resource
// Authorization: Bearer eyJhbGci...
// Headers are NOT typically logged by default
```

---

*Authentication category: ATH | Entry: ATH-031 | v5.0*