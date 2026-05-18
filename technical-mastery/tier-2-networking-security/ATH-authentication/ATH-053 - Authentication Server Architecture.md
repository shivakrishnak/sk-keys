---
id: ATH-053
title: "Authentication Server Architecture"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-022, ATH-047, ATH-048, ATH-050, ATH-052
used_by: ATH-054, ATH-056, ATH-057
related: ATH-054, ATH-056, ATH-057
tags:
  - security
  - authentication
  - architecture
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/authentication/authentication-server-architecture/
---

⚡ **TL;DR** - An authentication server (auth server, identity
provider, or authorization server in OAuth terminology) is the
centralized service responsible for verifying credentials,
issuing tokens, managing sessions, and federating with external
identity providers. Architecturally, it is the highest-value
target in the entire system - a compromise means every user
account is compromised. Design requirements: high availability
(99.99% or better), horizontal scalability, stateless token
issuance (JWT), encrypted and audited credential storage, and
a zero-trust deployment (hardened, isolated, minimal attack surface).

---

### 📊 Entry Metadata

| #053 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC, ATH-047 Distributed Auth, ATH-048 Service Identity, ATH-050 Risk-Based, ATH-052 Observability | |
| **Used by:** | ATH-054, ATH-056, ATH-057 | |
| **Related:** | ATH-054 Distributed Sessions, ATH-056 Enterprise Arch, ATH-057 IdP Design | |

---

### 📘 Textbook Definition

An authentication server implements the OAuth 2.0 Authorization
Server spec (RFC 6749), OIDC Provider spec, and optionally
SAML 2.0 IdP. Core responsibilities: authenticate user
credentials, federate with upstream IdPs (LDAP, SAML, social),
issue access tokens and ID tokens (JWT, RS256/ES256),
manage refresh tokens (stored, rotatable, revocable),
serve JWKS endpoint for token verification, manage user
sessions (with revocation capability), enforce MFA flows,
and emit security audit events. Production auth servers are
highly available, geo-distributed (to meet authentication SLAs
globally), and isolated from application services (separate
network segment, own database, own certificate chain).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authentication Server Architecture             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  COMPONENTS:                                           │
│  Login service: credential verification UI + API       │
│  Token service: JWT issuance, RS256/ES256 signing       │
│  Session store: Redis cluster (distributed)            │
│  JWKS endpoint: public key for token verification      │
│  User store: Postgres (bcrypt/Argon2 hashed passwords) │
│  MFA service: TOTP, push, WebAuthn                     │
│  Federation: SAML/OIDC upstream IdP connectors         │
│  Audit log: all auth events to append-only store       │
│                                                        │
│  TOKEN ISSUANCE (stateless):                           │
│  1. Verify credentials (user + MFA)                    │
│  2. Build JWT claims (sub, iss, aud, exp, roles)       │
│  3. Sign with private key (RSA or ECDSA)               │
│  4. Return access token (15 min TTL)                   │
│     + refresh token (30 day TTL, stored in DB)         │
│  5. Services verify: GET /oauth/jwks (public key)      │
│     Validate sig locally (no round-trip to auth server)│
│                                                        │
│  HIGH AVAILABILITY:                                    │
│  Stateless token issuance: any instance handles it     │
│  Session store: Redis cluster with replication         │
│  Database: primary + read replicas + failover          │
│  Global: active-active in 3+ regions                   │
│  SLA target: 99.99% (52 min downtime/year)             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - JWKS endpoint for token verification**

```java
// Auth server: expose JWKS so services can verify JWTs locally
// Services NEVER need to call auth server per-request
@RestController
@RequestMapping("/oauth")
public class JwksController {

    private final RSAPublicKey publicKey;

    @GetMapping("/.well-known/jwks.json")
    public Map<String, Object> jwks() {
        // Return public key in JWK format
        // Services cache this and verify tokens locally
        // Key rotation: add new key, keep old for overlap
        return Map.of("keys", List.of(
            Map.of(
                "kty", "RSA",
                "use", "sig",
                "kid", "key-2024-01",  // Key ID for rotation
                "alg", "RS256",
                "n", base64Url(publicKey.getModulus()),
                "e", base64Url(publicKey.getPublicExponent())
            )
        ));
    }
}

// Downstream service: verify JWT without calling auth server
@Bean
public JwtDecoder jwtDecoder() {
    return NimbusJwtDecoder
        // Cache JWKS for 5 minutes (reduces latency)
        // Refetch on "unknown kid" header (key rotation)
        .withJwkSetUri(
            "https://auth.company.com/oauth/.well-known/jwks.json")
        .jwsAlgorithms(algs -> {
            algs.add(SignatureAlgorithm.RS256);
            algs.add(SignatureAlgorithm.ES256);
        })
        .build();
}
```

---

*Authentication category: ATH | Entry: ATH-053 | v5.0*