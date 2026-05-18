---
id: SEC-028
title: "JSON Web Tokens (JWT)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-008, SEC-014, SEC-015, SEC-016
used_by: SEC-029, SEC-056, SEC-058, SEC-069, SEC-087
related: SEC-008, SEC-016, SEC-029, SEC-056, SEC-058, SEC-069, SEC-087
tags:
  - security
  - jwt
  - authentication
  - authorization
  - tokens
  - stateless
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/sec/json-web-tokens-jwt/
---

⚡ TL;DR - A JWT (JSON Web Token) is a URL-safe, self-contained
token that encodes claims (user identity, roles, expiration)
and is cryptographically signed to prevent tampering.

Structure: `header.payload.signature` (three base64url
segments, dot-separated). The header declares the signing
algorithm. The payload contains claims (sub, exp, iss, iat, etc.).
The signature proves the payload wasn't tampered with since signing.

**Key security properties:**
- Stateless: server doesn't need to store sessions -
  the token carries its own validity proof.
- Tamper-evident: changing any claim invalidates the signature.
- NOT encrypted by default: payload is base64-decoded, not secret.
  Anyone with the JWT can read the claims. Use JWE for encryption.

**Critical attacks to know:**
- `alg:none` attack: accept unsigned tokens if algorithm not validated.
- Algorithm confusion: RS256 public key used as HS256 secret.
- Weak secret brute force: HS256 with guessable secret.

**When to use JWT:** Stateless API authentication, microservices
inter-service auth, short-lived access tokens. When NOT to use:
need to revoke tokens before expiry (sessions are better),
very long token lifetimes (sessions are better).

---

| #028 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Auth vs AuthZ vs Auditing, HTTPS, TLS, Session Management | |
| **Used by:** | OAuth 2.0, JWT Anti-Patterns, OIDC, Advanced JWT Attacks | |
| **Related:** | Sessions, OAuth 2.0, OIDC, Advanced JWT Attacks, Auth Mechanism Migration | |

---

### 🔥 The Problem This Solves

**THE STATEFUL SESSION PROBLEM:**
Traditional web sessions: browser sends session ID →
server looks up session in database/memory → retrieves
user data. This works perfectly but creates infrastructure
coupling: every server in a cluster must share the session
store, the session store becomes a critical dependency,
and scaling horizontally requires sticky sessions or
shared state management.

**WHAT JWT SOLVES:**
JWT moves the user's identity information from the server
(session store) INTO the token itself. The server verifies
the cryptographic signature (cheap computation) instead
of doing a database lookup. Any server can independently
validate any JWT without shared state. This enables:
- Stateless horizontal scaling
- Cross-domain / cross-service identity
- Mobile and SPA authentication without cookie complexity

**WHAT JWT DOESN'T SOLVE:**
JWT can't be revoked before expiry without external state.
If a user logs out or is compromised, the JWT is valid
until it expires. This is the fundamental tradeoff: stateless
efficiency vs instant revocation capability.

---

### 📘 Textbook Definition

**JWT (JSON Web Token):** An open standard (RFC 7519) that
defines a compact, URL-safe means of representing claims
between two parties. A JWT consists of three base64url-encoded
parts separated by dots: header, payload, and signature.

**Structure:**

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9  <- Header (base64url)
.
eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkFsaWNlIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMzYwMH0  <- Payload (base64url)
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  <- Signature
```

**Header (decoded):**
```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

**Payload (decoded):**
```json
{
  "sub": "user123",      // Subject: who the token is about
  "name": "Alice",       // Custom claim
  "role": "user",        // Custom claim
  "iat": 1700000000,     // Issued At (epoch timestamp)
  "exp": 1700003600,     // Expiration (epoch + 1 hour)
  "iss": "auth.example.com"  // Issuer
}
```

**Signing Algorithms:**

**HS256 (HMAC-SHA256):** Symmetric signing. Server signs and
verifies with the same secret key. Simple but: all parties
that need to VERIFY must have the secret, which means all
parties can also FORGE tokens. Use only when the signer
and verifier are the same service.

**RS256 (RSA-SHA256):** Asymmetric signing. Server signs
with private key. Any service can verify using the public
key. Public key can be distributed freely (no forgery risk
since private key is not shared). Use for multi-service
systems where multiple verifiers exist.

**ES256 (ECDSA-SHA256):** Asymmetric signing using Elliptic
Curve. Smaller keys, faster computation than RSA, same
security level. Preferred for modern systems.

**Standard Claims (IANA registered):**
- `iss`: Issuer
- `sub`: Subject (user identifier)
- `aud`: Audience (intended recipient)
- `exp`: Expiration Time
- `nbf`: Not Before
- `iat`: Issued At
- `jti`: JWT ID (unique identifier for this token)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JWT = signed JSON envelope. Server signs user claims at
login. Client stores the token. On every request: client
sends token, server verifies signature (no DB lookup),
reads claims. Tamper-proof but readable. Not encrypted.

**One analogy:**
> A JWT is like a government-issued passport. The passport
> (payload) contains identity information (name, nationality,
> expiry). The signature (stamps, holograms) proves authenticity
> without requiring the passport office to be called on
> every border crossing. The border guard (server) can
> verify the passport locally. Anyone can READ the passport
> information (it's printed in plaintext). But you cannot
> FORGE a valid passport (signature) without the private
> key the government used to issue it. Expiry is built in.
> But once issued: even a revoked passport may work at
> borders that don't check the revocation list.

---

### 🔩 First Principles Explanation

**Why asymmetric signing (RS256) is preferred for multi-service:**

```
SYMMETRIC (HS256) - Single secret for sign AND verify:

  Auth Service (signs) ←── same secret ──→ Service A (verifies)
                                      ──→ Service B (verifies)
                                      ──→ Service C (verifies)
  
  Problem: Service A, B, C all have the signing secret.
  If Service A is compromised: attacker can FORGE tokens.
  Because: HS256 verify key = HS256 sign key.
  Any party that can verify can also forge.

ASYMMETRIC (RS256) - Separate keys for sign and verify:

  Auth Service: holds PRIVATE KEY (never shared)
    → Signs tokens with private key
  
  Service A, B, C: hold PUBLIC KEY (safely distributed)
    → Verify tokens with public key
    → CANNOT forge tokens (private key is required for signing)
  
  Key distribution: JWKS (JSON Web Key Set) endpoint:
    GET https://auth.example.com/.well-known/jwks.json
    Returns public keys for all services to fetch and cache.
  
  Compromise of Service A: attacker gets public key only.
  Cannot forge tokens. Auth service private key is safe.
  
  RULE: Use RS256 or ES256 for multi-service architectures.
        Use HS256 ONLY when signer == verifier (single service).

JWT VALIDATION CHECKLIST (verify ALL, not just signature):
  1. Signature: cryptographically valid?
  2. Algorithm: matches expected alg (reject "none")?
  3. exp: not expired?
  4. nbf: not before current time?
  5. iss: from expected issuer?
  6. aud: intended for this service?
  Skipping ANY check = potential vulnerability.
```

---

### 🧪 Thought Experiment

**SCENARIO: Designing auth for a microservices system**

```
SYSTEM:
  API Gateway → Auth Service → User Service
                            → Order Service
                            → Payment Service

OPTION 1: Session-based auth
  Every service calls Auth Service to validate session ID.
  
  Request flow:
    Client → API Gateway → User Service
    User Service → Auth Service (validate session) → OK
    Auth Service → session DB → user data
    Response: ~150ms round-trip to auth on EVERY request
  
  Scaling problem: Auth Service is on every hot path.
    Auth Service failure = all services fail.
    Auth Service latency = added to every API call.
  
OPTION 2: JWT-based auth (RS256)
  Auth Service issues JWT at login. Includes user_id,
  roles, exp (1 hour). Signs with private key.
  Public key available via JWKS endpoint.
  
  Request flow:
    Client → API Gateway → User Service (with JWT in header)
    User Service: verify signature (local, < 1ms) → read claims
    No Auth Service call. No session DB.
    Response: ~5ms added for JWT verification.
  
  Scaling benefit:
    Auth Service not on every hot path.
    Any service validates any JWT independently.
    Auth Service can be temporarily unavailable (existing
    JWTs continue to work until expiry).
  
TRADEOFF: Token revocation
  Session: revoke immediately by deleting session DB record.
  JWT: cannot revoke before exp. If exp = 1 hour:
    compromised JWT is valid for up to 1 hour.
  
SOLUTION: Short-lived access token (15 min) + longer refresh token (7 days)
  Access token: JWT, short-lived, stateless validation
  Refresh token: opaque, stored in DB, can be revoked immediately
  When access token expires: use refresh token to get new access token
  Revoke refresh token: user must re-authenticate. 15-minute maximum
  exposure window for compromised access token.
```

---

### 🧠 Mental Model / Analogy

> JWT access tokens are like conference badges. On day 1:
> you show your ID at registration, they check you against
> the list, and issue a badge. For the rest of the day:
> every door just checks the badge - no more checking
> the master list. Efficient. But if someone steals your
> badge: they can use it until the conference ends.
> You can't "revoke" a conference badge without checking
> everyone at every door against a revoked-badge list
> (which defeats the efficiency point). Short expiry =
> short-lived badges that expire tonight. Refresh tokens
> = the master list: still exists, still revocable,
> but only consulted once when getting a new badge (access token).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A JWT is a digital membership card you can check without
calling the membership office. After logging in, the server
gives you a signed card (JWT) that says who you are. On
every request: you show the card. The server reads it and
trusts it without looking you up in a database. It's fast.
The downside: if someone steals your card, they can use
it until it expires. Keep expiry short (15-60 minutes).

**Level 2 - How to use it (junior developer):**
Typical implementation: POST /login returns access_token
(JWT, 15 min expiry) and refresh_token (opaque, 7 days).
Store access_token in memory (not localStorage). Store
refresh_token in HttpOnly cookie. Every API request:
`Authorization: Bearer <access_token>`. When access token
expires: POST /refresh with cookie → new access token.
Logout: call /logout (invalidates refresh token in DB),
clear tokens from memory/cookie.

**Level 3 - How it works (mid-level engineer):**
JWT signature validation for RS256: server fetches JWKS
(public keys) from auth service at startup (cached).
For each incoming JWT: decode header to get kid (key ID),
look up matching public key from JWKS cache, verify
RS256 signature over `header.payload`. If signature is
valid: decode payload (base64url), verify exp, iss, aud
claims. All must pass. Never skip the claim validations
- a valid signature with an expired token is still an
invalid token. Library choice: jose (Python/Node), java-jwt
(Java), ruby-jwt. Use well-tested libraries, not custom
JWT parsing.

**Level 4 - Why it was designed this way (senior/staff):**
RFC 7519 was designed as a general-purpose claims container,
not specifically for authentication. The original use cases
included cross-domain single sign-on and federated identity.
The "bearer token" model (whoever holds the token can use it)
simplifies verification but requires transport security
(HTTPS) and careful storage. The algorithm agility in the
header (declaring your own alg) was a later-recognized
design flaw that enabled the alg:none attack. Modern best
practice: server whitelists acceptable algorithms, ignores
client-declared alg entirely. RFC 7518 (JWA) and RFC 8725
(JWT Best Practices) updated the guidance significantly.

**Level 5 - Mastery (distinguished engineer):**
At scale: JWT management includes key rotation (RS256 keys
should rotate periodically). JWKS endpoint includes
multiple keys with different kid values. Clients should:
attempt verification with the declared kid key, if not
found: refresh JWKS cache once (key may have rotated),
retry. This handles rolling key rotation with no downtime.
Token binding (RFC 8471): cryptographically bind the JWT
to the TLS session, preventing token theft replay even
if the token is intercepted. Still not widely deployed
but addresses the "bearer token" theft risk. DPoP (Demonstrating
Proof-of-Possession, RFC 9449): sender-constrained tokens
where each request proves possession of a key pair, preventing
replay attacks. Used in OAuth 2.0 advanced deployments.

---

### ⚙️ How It Works (Mechanism)

**JWT signing and validation flow:**

```
JWT SIGNING (at login):

  1. User authenticates (username + password verified)
  
  2. Auth service creates payload:
       {sub: "user123", roles: ["user"], exp: now+3600}
  
  3. Auth service creates header:
       {alg: "RS256", typ: "JWT", kid: "key-2024-01"}
  
  4. Signs: base64url(header) + "." + base64url(payload)
     with RSA private key → signature bytes
  
  5. JWT = base64url(header) + "." + base64url(payload)
           + "." + base64url(signature)
  
  6. Returns JWT to client.

JWT VALIDATION (on every API request):

  Client sends: Authorization: Bearer <JWT>
  
  Service receives:
  1. Split on "." → [header_b64, payload_b64, signature_b64]
  2. Decode header: get {alg, kid}
  3. ALGORITHM WHITELIST: is alg in ["RS256", "ES256"]?
     If not → reject. Never trust client-declared alg.
  4. Fetch public key from JWKS by kid.
     (cached at startup, refresh if kid not found)
  5. Verify signature: RS256.verify(header_b64 + "." + payload_b64,
     signature, public_key) → boolean
  6. Decode payload.
  7. Verify exp: payload.exp > current_time?
  8. Verify iss: payload.iss == "auth.example.com"?
  9. Verify aud: payload.aud includes this service?
  10. If ALL checks pass: request is authenticated.
      Use payload.sub and payload.roles for authorization.
```

---

### 💻 Code Example

**JWT validation in Python (FastAPI) with all security checks:**

```python
# SECURE JWT VALIDATION
# Using python-jose library with RS256

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from fastapi import HTTPException, status
import httpx
import time

# ALGORITHM WHITELIST - never trust client-declared alg
ALLOWED_ALGORITHMS = ["RS256", "ES256"]
EXPECTED_ISSUER = "https://auth.example.com"
EXPECTED_AUDIENCE = "api.example.com"

# JWKS cache (fetched at startup, refreshed on unknown kid)
_jwks_cache = None
_jwks_cache_time = 0
JWKS_CACHE_TTL = 3600  # seconds

async def get_jwks():
    """Fetch and cache JWKS from auth server."""
    global _jwks_cache, _jwks_cache_time
    if _jwks_cache and (time.time() - _jwks_cache_time < JWKS_CACHE_TTL):
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://auth.example.com/.well-known/jwks.json",
            timeout=5.0
        )
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_time = time.time()
    return _jwks_cache

async def validate_jwt(token: str) -> dict:
    """
    Validate JWT with all required security checks.
    Returns decoded payload on success.
    Raises HTTPException on any failure.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode header WITHOUT verification to get kid
        # jose.get_unverified_header is safe: just parses base64
        unverified_header = jwt.get_unverified_header(token)
        
        # CRITICAL: Validate algorithm before anything else
        # Prevents alg:none attack and algorithm confusion
        alg = unverified_header.get("alg")
        if alg not in ALLOWED_ALGORITHMS:
            raise credentials_error
        
        # Get JWKS (cached)
        jwks = await get_jwks()
        
        # Decode and verify in one step with all checks
        payload = jwt.decode(
            token,
            jwks,                          # Public keys from JWKS
            algorithms=ALLOWED_ALGORITHMS, # Server whitelist, not client
            issuer=EXPECTED_ISSUER,        # Verify iss claim
            audience=EXPECTED_AUDIENCE,    # Verify aud claim
            options={
                "verify_exp": True,        # Verify expiration
                "verify_nbf": True,        # Verify not-before
                "verify_iat": True,        # Verify issued-at
                "require": ["exp", "iss", "sub", "aud"],  # Required claims
            }
        )
        
        return payload
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        # Any JWT error: don't reveal why (information disclosure)
        raise credentials_error

# BAD - common insecure patterns
def validate_jwt_bad(token: str) -> dict:
    # BAD 1: Trust client-declared algorithm
    # Enables alg:none attack
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "RS256")  # Don't use client-declared alg!
    
    # BAD 2: No iss/aud verification
    # BAD 3: verify=False allows any invalid token
    payload = jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=[alg],   # BAD: using attacker-controlled alg
        options={"verify_exp": False}  # BAD: no expiry check
    )
    return payload
```

---

### ⚖️ Comparison Table

| Feature | JWT (Stateless) | Session Cookie (Stateful) |
|:---|:---|:---|
| **Server storage** | None (stateless) | Session in DB/Redis |
| **Scalability** | Excellent (no shared state) | Requires shared session store |
| **Revocation** | Only at expiry (or blocklist) | Instant (delete session) |
| **Multi-service** | Yes (share public key) | Complex (single session store) |
| **Token size** | ~200-400 bytes (larger) | ~30-50 bytes session ID |
| **Sensitive data** | Not encrypted (avoid PII) | Data stays server-side |
| **Logout** | Refresh token revocation | Simple session deletion |
| **Best for** | API auth, microservices | Traditional web apps, SSO |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| JWT payload is encrypted so it's safe to store sensitive data | JWT payload is base64url-ENCODED, not encrypted. Anyone who has the token can decode the payload with base64url decoding - no key required. Never store passwords, SSNs, credit card numbers, or other sensitive PII in JWT claims. The signature provides integrity (tamper detection) not confidentiality. If you need encrypted tokens: use JWE (JSON Web Encryption, RFC 7516). |
| JWTs are more secure than sessions | JWT vs session is an architectural choice, not a security level difference. Both can be implemented securely or insecurely. Sessions with strong session IDs (128+ bits entropy), HttpOnly/Secure cookies, proper expiry, and server-side validation are as secure as properly-validated JWTs. The JWT algorithm confusion and alg:none attacks are JWT-specific vulnerabilities that have no session equivalent. Sessions' main weakness is revocation complexity at scale. |

---

### 🚨 Failure Modes & Diagnosis

**Critical JWT attacks and how to prevent them:**

```
ATTACK 1: alg:none bypass
  Attacker modifies header: {"alg":"none","typ":"JWT"}
  Modifies payload: {"sub":"user123","role":"admin"}
  Sets signature to empty: header.payload.
  (trailing dot, no signature)
  
  If server accepts alg:none: no signature check = token accepted.
  
  Root cause: server uses algorithm from token header.
  Fix: server ALWAYS uses its configured whitelist,
    NEVER the client-declared algorithm.
    jose library: pass algorithms= to jwt.decode(),
    never read alg from unverified_header.

ATTACK 2: RS256 → HS256 algorithm confusion
  Attack precondition:
    Service uses RS256. Public key is known (it's public).
  Attacker:
    Crafts token with alg:HS256 in header.
    Signs with HS256 using the SERVICE'S PUBLIC KEY as the HMAC secret.
  
  Vulnerable library behavior:
    Library reads alg:HS256 from token.
    Uses server's "key" to verify.
    If key = RS256 public key and library treats it as HMAC secret:
    Verification PASSES (attacker signed it with the same value).
  
  Fix: whitelist algorithms. If service expects RS256:
    reject any token with alg != RS256.
    Never allow HS256 and RS256 on same endpoint simultaneously.

ATTACK 3: Weak HS256 secret brute force
  If HS256 secret is short or guessable:
    Attacker captures a valid JWT.
    Runs hashcat/jwt-cracker against it.
    Finds secret.
    Can forge arbitrary tokens.
  
  Fix: HS256 secrets must be cryptographically random,
    minimum 256 bits (32 bytes). Use RS256 for new systems.
  
  Diagnosis:
    jwt-cracker <token> or hashcat -a 0 -m 16500 <token> wordlist.txt
    If it cracks: rotate secret immediately, move to RS256.

ATTACK 4: JWT stored in localStorage → XSS steals token
  If access token is in localStorage: any XSS can read it.
  document.cookie cannot be read by XSS if HttpOnly.
  localStorage has no HttpOnly equivalent.
  
  Fix: store access token in memory (JavaScript variable).
  Store refresh token in HttpOnly cookie.
  On page reload: use refresh token cookie to get new access token.
  Tradeoff: page reload requires a refresh token round-trip.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication vs Authorization vs Auditing`
- `HTTPS, TLS`
- `Cookie and Session Management`

**Builds on this:**
- `OAuth 2.0` - uses JWTs as access tokens
- `OIDC` - JWT-based identity layer on OAuth
- `JWT Anti-Patterns` - deep dive into JWT misuse patterns
- `Advanced JWT Attacks` - algorithm confusion, key confusion

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRUCTURE    │ header.payload.signature (base64url)      │
│ PAYLOAD      │ Readable by anyone. NOT encrypted.        │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHMS   │ RS256/ES256: asymmetric (multi-service)   │
│              │ HS256: symmetric (same svc signs+verifies)│
├──────────────┼───────────────────────────────────────────┤
│ VALIDATION   │ Sig + alg whitelist + exp + iss + aud     │
│              │ ALL required. Skip one = vulnerability.   │
├──────────────┼───────────────────────────────────────────┤
│ STORAGE      │ Access token: memory only                 │
│              │ Refresh token: HttpOnly cookie             │
│              │ Never: localStorage (XSS vulnerable)      │
├──────────────┼───────────────────────────────────────────┤
│ KEY ATTACKS  │ alg:none, algorithm confusion, weak secret│
│              │ Fix: server-side alg whitelist always     │
├──────────────┼───────────────────────────────────────────┤
│ REVOCATION   │ Use short expiry (15 min) + refresh token │
│              │ Revoke refresh token = max 15 min window  │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Algorithm agility is a double-edged sword." JWT's design
allows the client to declare its algorithm, enabling flexibility.
But this flexibility has been the source of multiple
critical vulnerabilities (alg:none, algorithm confusion).
The security lesson: when a security mechanism allows the
entity being authenticated to influence the authentication
mechanism itself, there's a potential for attack. The correct
pattern: the server decides and enforces the security
parameters; the client cannot influence them. Apply this
broadly: never let user-controlled input determine
which security control is applied. The server owns the
security model configuration.

---

### 💡 The Surprising Truth

The `alg:none` vulnerability (CVE-2015-9235) was so widespread
and so simple that it affected dozens of popular JWT libraries
in 2015. The attack was trivial: any attacker who understood
JWT structure could forge administrative tokens by setting
`"alg":"none"` and providing an empty signature. Libraries
were trusting the token's own declaration of how to verify
itself - a fundamental design flaw. Some libraries STILL
have this vulnerability in old versions. The lesson:
JWT validation is not "check signature." It's a multi-step
process: verify the algorithm is acceptable, THEN verify
the signature, THEN verify all claims. Every step must
be performed and every step can have a vulnerability.
This is why you should use well-maintained JWT libraries
and keep them updated - the JWT security bugs have been
found and fixed in good libraries, but only if you're
running a recent version.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DECODE** a JWT manually (base64url decode each part)
   and identify the header, payload claims, and signature.
2. **IMPLEMENT** RS256 JWT validation with algorithm whitelist,
   all claims verified (exp, iss, aud).
3. **EXPLAIN** the alg:none attack and why it works when
   the server trusts the client-declared algorithm.
4. **CHOOSE** between JWT and sessions for a given architecture,
   explaining the revocation tradeoff.

---

### 🎯 Interview Deep-Dive

**Q: What are the security risks with JWTs and how do you
mitigate them?**

*Why they ask:* JWT misuse is extremely common. Tests
whether the candidate knows JWT in production, not just
the theory.

*Strong answer includes:*
- Algorithm confusion attacks: if server uses RS256 but
  accepts alg:HS256, attacker uses RS256 public key as HMAC
  secret. Fix: server-side algorithm whitelist, never trust
  client-declared alg.
- alg:none: strip signature, claim no algorithm. Fix: same whitelist.
- Weak secret (HS256): brute-forceable HMAC keys. Fix:
  cryptographically random 256-bit secrets, or use RS256.
- No expiry verification: eternal tokens if exp not checked.
  Fix: always verify exp. Short expiry (15 min) for access tokens.
- No audience/issuer verification: token from one service
  accepted by another. Fix: verify iss and aud on every endpoint.
- Sensitive data in payload: payload is base64-decoded, not
  encrypted. Fix: no PII in JWT claims. Use JWE if needed.
- Storage: localStorage vulnerable to XSS theft. Fix: memory
  for access token, HttpOnly cookie for refresh token.
- Revocation: JWT can't be revoked before exp. Fix: short
  expiry (15 min) + refresh token pattern. Refresh token in
  DB can be revoked immediately. Maximum exposure: access
  token expiry window.