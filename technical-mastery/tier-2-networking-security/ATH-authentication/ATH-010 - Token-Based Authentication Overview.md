---
id: ATH-010
title: "Token-Based Authentication Overview"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-006, ATH-008
used_by: ATH-023, ATH-030, ATH-031, ATH-032
related: ATH-008, ATH-023, ATH-031
tags:
  - security
  - authentication
  - tokens
  - jwt
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/authentication/token-based-authentication-overview/
---

⚡ **TL;DR** - Token-based authentication replaces server-side
session state with a self-contained, signed token (typically JWT)
that the client stores and presents on each request. The server
verifies the signature without any storage lookup - enabling
stateless, horizontally scalable APIs. The trade-off: tokens
cannot be individually revoked before expiry without adding
server-side state (defeating the statelessness).

---

### 📊 Entry Metadata

| #010 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-006, ATH-008 | |
| **Used by:** | ATH-023, ATH-030, ATH-031, ATH-032 | |
| **Related:** | ATH-008 Sessions, ATH-023 JWT Validation, ATH-031 Bearer Tokens | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Server-side sessions require a shared session store (Redis)
accessible by every API server instance. Every request
requires a round-trip to the session store. In a microservices
architecture with 50 services, each service either needs access
to the central session store or cannot verify the user's identity.

Token-based auth eliminates the session store dependency: the
token itself contains the user's identity and is cryptographically
signed by the auth server. Any service that has the public key
can verify the token locally with zero network calls.

---

### 📘 Textbook Definition

Token-based authentication is a stateless mechanism where
the authentication server issues a cryptographically signed
token (typically a JWT) containing identity claims after
successful credential verification. The client stores the
token and presents it in the Authorization header of subsequent
requests. Resource servers verify the token's signature and
expiry locally without querying any central store, then extract
identity claims from the token payload. Token-based auth is the
dominant pattern for REST APIs, SPAs, and mobile applications.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log in once, receive a signed note that proves who you are;
show the note to each service, which verifies it without
calling anyone else.

**One analogy:**
> A concert wristband (instead of a ticket). The venue stamps
> your wrist at the entrance. Now you can move between the
> bar, the VIP area, and the stage without showing your
> ticket again - each area's staff can see and verify the
> wristband directly. No central check required.

**One insight:**
The JWT's value lies in being self-contained and verifiable
without a round-trip. But this creates the revocation problem:
if you want to kick someone out mid-concert, you cannot make
their wristband invisible. You either wait for it to expire,
or you add a revocation list (which reintroduces server state).

---

### ⚙️ How It Works (Mechanism)

**JWT structure:**

```
┌────────────────────────────────────────────────────────┐
│                  JWT Structure                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  A JWT is three Base64url-encoded sections             │
│  separated by dots:                                    │
│                                                        │
│  header.payload.signature                              │
│                                                        │
│  HEADER (algorithm + type):                            │
│  { "alg": "RS256", "typ": "JWT" }                     │
│                                                        │
│  PAYLOAD (claims):                                     │
│  {                                                     │
│    "sub": "alice@company.com",  // subject             │
│    "iat": 1716048000,           // issued at           │
│    "exp": 1716051600,           // expires (1hr)       │
│    "roles": ["user", "admin"],  // custom claim        │
│    "jti": "abc123"              // unique token ID     │
│  }                                                     │
│                                                        │
│  SIGNATURE:                                            │
│  RS256(base64(header) + "." + base64(payload),        │
│        private_key)                                    │
│                                                        │
│  ANY server with the public key can verify the         │
│  signature - no round-trip to auth server needed       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth Server
    participant S as API Service
    C->>A: POST /login (credentials)
    A->>A: Verify; sign JWT with private key
    A-->>C: JWT token
    C->>S: GET /api/data\nAuthorization: Bearer JWT
    S->>S: Verify JWT signature with public key
    S->>S: Check exp claim (not expired)
    S->>S: Extract sub, roles claims
    S-->>C: Response (no round-trip to auth server)
```

**Token storage options:**

| Location | XSS Safe | CSRF Safe | Notes |
|---|---|---|---|
| HttpOnly cookie | Yes | Needs SameSite | Best for web apps |
| Memory (JS var) | Yes | Yes | Lost on page refresh |
| localStorage | No | Yes | Vulnerable to XSS theft |
| sessionStorage | No | Yes | Vulnerable to XSS theft |

---

### 💻 Code Examples

**Example - Spring Security JWT validation**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http)
        throws Exception {
    http
        .sessionManagement(s -> s
            .sessionCreationPolicy(STATELESS)) // no server sessions
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(jwt -> jwt
                .decoder(jwtDecoder()) // validates sig + exp
            )
        );
    return http.build();
}

@Bean
public JwtDecoder jwtDecoder() {
    // Load public key from JWKS endpoint
    return NimbusJwtDecoder
        .withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
        .build();
}
```

**Example - BAD vs GOOD: token storage**

```javascript
// BAD: storing JWT in localStorage
// XSS attack can read and exfiltrate the token:
// malicious script: fetch(atob + localStorage.getItem('jwt'))
localStorage.setItem('jwt', token);

// GOOD: store in memory (lost on refresh, but XSS-safe)
// Combined with silent refresh using HttpOnly refresh cookie
let accessToken = token; // module-scoped variable

// BEST for web: HttpOnly cookie (server sets it)
// JS never sees the token at all
// Server: Set-Cookie: ACCESS_TOKEN=jwt; HttpOnly; Secure
```

**Example - FAILURE: algorithm confusion attack**

```
Vulnerability: accepting "alg": "none" in JWT header

Attack:
  Attacker creates a JWT with alg=none:
  header: {"alg":"none","typ":"JWT"}
  payload: {"sub":"admin","roles":["admin"]}
  signature: (empty)

  If server accepts alg=none, this unsigned token
  is treated as valid. Attacker grants themselves admin.

Fix: NEVER accept alg=none.
Configure the JWT library to only allow specific algorithms:
  jwtParser.setAllowedAlgorithms(Arrays.asList("RS256"));
  // or: NimbusJwtDecoder with explicit algorithm specification
```

---

### ⚠️ Common Failure Modes

**Long-lived tokens with no revocation:**

```
Symptom: user reports they changed password but old devices
still work for hours/days.

Root cause: JWT issued with 24h expiry; no revocation.
Changing password does not invalidate existing tokens.

Fix options:
  1. Short-lived access tokens (15 min) + refresh tokens
  2. Token revocation list in Redis (short-lived tokens
     only needing a small revocation cache)
  3. Include a credential version in the JWT (revoke by
     incrementing the user's credential version in the DB;
     tokens with old version = invalid)
```

---

### 📏 Decision Guide

| Use sessions when: | Use tokens when: |
|---|---|
| Web app with instant logout | API used by mobile/SPA/services |
| Single-domain, server-rendered | Multi-service / microservices |
| Need immediate revocation | Stateless scaling is critical |
| Simple CSRF protection needed | Cross-domain auth required |

---

*Authentication category: ATH | Entry: ATH-010 | v5.0*