---
id: ATH-045
title: "JWT Signature Algorithm Security (RS256 vs HS256)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-023, ATH-031
used_by: ATH-046, ATH-047, ATH-053
related: ATH-023, ATH-046, ATH-061
tags:
  - security
  - authentication
  - jwt
  - algorithm
  - cryptography
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/authentication/jwt-signature-algorithm-security-rs256-vs-hs256/
---

⚡ **TL;DR** - JWT signature algorithm choice determines the trust
model. HS256 (HMAC-SHA256) uses a symmetric shared secret - both
the issuer and every verifier must know the same secret. RS256/PS256
(RSA) and ES256 (ECDSA) use asymmetric keys: the issuer signs with
a private key, verifiers use a public key - no secret sharing. The
critical vulnerability: algorithm confusion attacks. An attacker
can change the header to `alg:none` (no signature) or to HS256 when
the server expects RS256 (using the public key as the HMAC secret).
Always pin the expected algorithm server-side.

---

### 📊 Entry Metadata

| #045 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-023 JWT Validation, ATH-031 Bearer Tokens | |
| **Used by:** | ATH-046, ATH-047, ATH-053 | |
| **Related:** | ATH-023 JWT Validation, ATH-046 Token Theft, ATH-061 WebAuthn Internals | |

---

### 📘 Textbook Definition

JWT signature algorithms fall into two categories: symmetric
(HMAC: HS256, HS384, HS512) and asymmetric (RSA: RS256, RS384,
RS512, PS256; ECDSA: ES256, ES384, ES512). HS256 uses the same
secret for signing and verification; RS256 uses a private key
for signing and a public key for verification. The algorithm
confusion vulnerability (CVE-2015-9235 and similar) exploits
libraries that accept any algorithm from the JWT header instead
of verifying a pre-configured expected algorithm. This allows
an attacker to craft tokens signed with `alg:none` (no
signature) or to forge HS256 tokens using a known RS256 public
key as the HMAC secret.

---

### ⚙️ How It Works (Mechanism)

**Algorithm confusion attack vector:**

```
┌────────────────────────────────────────────────────────┐
│         Algorithm Confusion Attack                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SETUP: Server expects RS256                           │
│  Server has RSA public key (publicly known)            │
│                                                        │
│  ATTACK: "alg:none" bypass                             │
│  1. Attacker: change header to {"alg":"none"}          │
│  2. Craft payload: {"sub":"admin","roles":["admin"]}   │
│  3. Token: base64(header).base64(payload). (no sig)   │
│  4. Vulnerable server accepts: "no signature = valid"  │
│                                                        │
│  ATTACK: RS256->HS256 confusion                        │
│  1. Attacker knows server's RSA public key             │
│     (from JWKS endpoint - public information)          │
│  2. Change header: {"alg":"HS256"}                     │
│  3. Sign with: HMAC-SHA256(payload, RSA_PUBLIC_KEY)    │
│     (treating the public key bytes as HMAC secret)     │
│  4. Vulnerable server (accepts alg from header):       │
│     Switches to HS256 mode                             │
│     Verifies HMAC with... the RSA public key           │
│     Which the attacker also used to sign               │
│  5. Signature matches. Token "valid". Attacker is admin│
│                                                        │
│  FIX: pin algorithm server-side                        │
│  NEVER accept algorithm from JWT header                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Algorithm pinning in Spring Security**

```java
@Bean
public JwtDecoder jwtDecoder() {
    // Load public key for RS256 verification
    RSAPublicKey publicKey = loadPublicKey();

    NimbusJwtDecoder decoder = NimbusJwtDecoder
        // Explicitly specify algorithm - ignore header alg
        .withPublicKey(publicKey)
        .signatureAlgorithm(SignatureAlgorithm.RS256)
        .build();
    // If token has alg=none or alg=HS256: decoding FAILS
    // Algorithm is pinned to RS256 - header is IGNORED
    return decoder;
}

// Or with JWKS endpoint (supports key rotation):
@Bean
public JwtDecoder jwtDecoderJwks() {
    NimbusJwtDecoder decoder = NimbusJwtDecoder
        .withJwkSetUri("https://auth/.well-known/jwks.json")
        // Only accept RS256 or ES256 - never HS256 or none
        .jwsAlgorithms(algorithms -> {
            algorithms.add(SignatureAlgorithm.RS256);
            algorithms.add(SignatureAlgorithm.ES256);
        })
        .build();
    return decoder;
}
```

**Example - When to choose HS256 vs RS256**

```
HS256 - symmetric HMAC:
  Use when: single server issues AND verifies tokens
  (no token sharing between services)
  Never use when: multiple services verify tokens
  (each verifier needs the secret = secret sprawl)
  Secret management: store in secret manager,
  rotate periodically, all services must be updated

RS256 - asymmetric RSA:
  Use when: multiple services verify tokens
  Issuer keeps private key, verifiers use public key
  Public key: shareable via JWKS endpoint
  Key rotation: publish new public key to JWKS,
  old tokens still valid until expiry (no secret update)

ES256 - asymmetric ECDSA:
  Same as RS256 but shorter keys (faster verification)
  Preferred for high-throughput APIs
  Smaller JWT: P-256 key = 64-byte signature vs RSA 256 bytes

NEVER USE:
  alg=none: unsigned - no integrity protection
  RS1 (SHA-1): deprecated
  HS256 for multi-service: secret sprawl risk
```

---

*Authentication category: ATH | Entry: ATH-045 | v5.0*