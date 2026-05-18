---
id: API-022
title: "Authentication Schemes (Bearer Token, Basic Auth)"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★★☆
depends_on: API-007, API-008, API-010
used_by: API-023, API-024, API-057, API-058
related: API-016, API-066, API-021
tags:
  - authentication
  - bearer-token
  - basic-auth
  - http
  - security
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/api/authentication-schemes-bearer-token-basic-auth/
---

⚡ TL;DR - HTTP authentication schemes define how clients
prove identity in the `Authorization` header; Basic Auth
sends base64-encoded credentials on every request (requires
TLS), Bearer Token sends an opaque or JWT token that the
server validates, and Digest Auth is an obsolete challenge-
response scheme that is never used in modern APIs.

---

| #022 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Request Headers, HTTP Status Codes, Request/Response | |
| **Used by:** | JWT, OAuth 2.0 Flows, OWASP API Top 10, JWT Security | |
| **Related:** | API Key Auth, TLS in APIs, CORS | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
HTTP is stateless. Every request stands alone. Without
a standard authentication mechanism, APIs invent their
own credential-passing conventions: custom headers,
query string tokens, session cookies with incompatible
naming, proprietary schemes. No interoperability, no
shared security knowledge, repeated vulnerabilities.

**THE BREAKING POINT:**
The web needed a standard. RFC 7617 (Basic Auth),
RFC 6750 (Bearer Token), RFC 7616 (Digest Auth) define
the HTTP `Authorization` header format:
`Authorization: <scheme> <credentials>`.
Standardizing the header means proxies, CDNs, API
gateways, and security scanners all understand where
credentials live. Middleware can strip, inject, or
validate credentials without knowing application details.

**THE CONSEQUENCE:**
Today, virtually every API uses one of: Basic Auth
(internal services, simple scripts), Bearer Token
(external APIs with OAuth), API Key (developer APIs).
`Authorization: Bearer <token>` is the de facto standard
for modern REST APIs.

---

### 📘 Textbook Definition

HTTP authentication schemes are standardized mechanisms
for transmitting credentials in the `Authorization`
request header. The format is `<scheme> <credentials>`.
**Basic Auth** (RFC 7617): credentials are
`base64(username:password)`. It is reversible encoding
(not encryption) so it requires TLS. **Bearer Token**
(RFC 6750): a short-lived token (opaque or JWT) issued
by an authorization server. The server validates the
token on each request. **Digest Auth** (RFC 7616):
challenge-response with MD5 (deprecated; avoid). The
`WWW-Authenticate` response header (on 401) tells the
client which scheme the server expects. The
`Authorization` request header carries the actual
credentials.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every API request proves identity via `Authorization:
<scheme> <credentials>` - Basic Auth is a base64-encoded
password, Bearer Token is a short-lived token, API Key
is a static shared secret.

**One analogy:**
> Showing ID at different security checkpoints.
> Basic Auth = showing your actual passport (permanent
> credential) at every checkpoint - risky if the
> checkpoint is compromised.
> Bearer Token = showing a visitor badge issued by the
> security desk (expires in 1 hour; if stolen, it goes
> stale). The badge was issued after the passport was
> verified once (OAuth flow).

**One insight:**
Base64 is encoding, not encryption. `Authorization:
Basic dXNlcjpwYXNzd29yZA==` decoded is `user:password`.
Any man-in-the-middle who sees this header has your
credentials. Basic Auth is only safe over TLS (HTTPS).
Over HTTP, it is plaintext password exposure.

---

### 🔩 First Principles Explanation

**BASIC AUTH:**
```
Client sends:
  Authorization: Basic dXNlcjpwYXNzd29yZA==

Decoded (base64):
  user:password

Server must:
1. Decode base64
2. Split on first ':'
3. Validate username + password against credential store
4. Return 401 + WWW-Authenticate: Basic realm="..."
   on failure

Security requirements:
- HTTPS mandatory (base64 is trivially reversible)
- No token expiry; credentials valid until changed
- Cannot revoke without changing the password
```

**BEARER TOKEN:**
```
Client sends:
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

Server options:
A. Opaque token: look up token in database/Redis
   → find associated user, scopes, expiry
B. JWT: validate signature, check expiry (exp claim)
   → no database lookup needed (stateless)

Security properties:
- Token is short-lived (typically 15min - 1 hour)
- Stolen token expires; minimal damage window
- Revocation: opaque tokens → delete from DB;
  JWT → revocation list (expensive) or just let expire
- 401 Unauthorized if token missing/invalid
- 403 Forbidden if token valid but insufficient scope
```

**HEADER FORMAT:**
```
Authorization: <scheme> <credentials>

Schemes:
  Basic  <base64(user:password)>
  Bearer <token>
  Digest <complex challenge-response params>
  ApiKey <key>  ← non-standard but common

Server response on missing/invalid auth:
  401 Unauthorized
  WWW-Authenticate: Bearer realm="api.example.com"
```

**WHEN TO USE WHICH:**

| Scheme | Use Case | Risk |
|:---|:---|:---|
| Basic Auth | Internal services, scripts, CLI tools | Credentials on every request; requires TLS |
| Bearer Token | User-facing APIs, OAuth, mobile apps | Token expiry mitigates stolen-token risk |
| API Key | Developer APIs, B2B integrations | Long-lived; rotate regularly |
| Digest Auth | Avoid | MD5-based; has known weaknesses; avoid |

---

### 🧪 Thought Experiment

**SCENARIO: GitHub API authentication**

GitHub supports three authentication schemes:
1. Basic Auth: `curl -u username:password` (deprecated)
2. Personal Access Token as Bearer:
   `curl -H "Authorization: Bearer ghp_abc123"`
3. OAuth App Bearer: short-lived tokens from OAuth flow

**WHY GITHUB DEPRECATED BASIC AUTH:**
- Password breaches expose all GitHub repos
- No granularity: password gives full account access
- No expiry: leaked credential valid forever

**WHY BEARER TOKEN IS BETTER:**
- Fine-grained scopes: `repo:read` only
- Expiry: token invalid after 8 hours or on revocation
- Different token per device/app - revoke one without
  affecting others
- Audit log: which token made which API call

---

### 🧠 Mental Model / Analogy

> Basic Auth is like giving a hotel your house key when
> you check in - on every visit to the room service desk,
> you hand over your actual house key. If anyone copies
> it, they can enter your home forever.
>
> Bearer Token is like getting a hotel keycard at check-in.
> The keycard represents your identity for this stay only.
> It expires at checkout. If you lose it, the hotel
> deactivates it. Your actual house key was only shown
> once to get the keycard issued.

Mapping:
- "Hotel check-in with passport" → OAuth login (one-time
  credential exchange)
- "Hotel keycard" → Bearer token
- "Keycard expires at checkout" → token expiry
- "Deactivate lost keycard" → token revocation
- "Giving house key on every visit" → Basic Auth risk

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Every API request needs to prove who is asking. The
`Authorization` header carries the proof. Basic Auth
sends your username and password (encoded but readable).
Bearer Token sends a temporary pass (like a visitor
badge) that was issued after you logged in once. When
the pass expires, you get a new one.

**Level 2 - How to use it (junior developer):**
For most modern REST APIs: use `Authorization: Bearer
<token>`. Get the token from a login endpoint or OAuth
flow. Send it on every API request. Handle 401 (token
invalid/expired) by refreshing the token. Never use
Basic Auth over HTTP; always use HTTPS.

**Level 3 - How it works (mid-level engineer):**
Bearer token validation: server receives the `Authorization`
header, extracts the token after "Bearer ", validates
it (either DB lookup for opaque tokens, or JWT signature
verification + expiry check). Returns 401 if token
invalid/missing; 403 if valid but insufficient scope.
Basic Auth validation: base64-decode, split on ':', hash
the password and compare to stored hash (bcrypt/Argon2).
Never store or compare plaintext passwords.

**Level 4 - Why it was designed this way (senior/staff):**
Bearer token design reflects stateless authentication:
the token is a self-contained credential that can be
validated without server state (for JWT). This enables
horizontal scaling: any server in a pool can validate
the same token without session affinity. The trade-off:
JWT revocation requires either a short expiry (accept
up-to-expiry window of unauthorized access) or a
revocation list (adds stateful lookup, defeating the
benefit). High-security APIs use opaque tokens with DB
validation; latency-sensitive APIs use JWT with short
expiry.

**Level 5 - Mastery (distinguished engineer):**
The Bearer scheme name is "bearer" because "whoever
bears this token is authenticated" - no identity binding.
Stolen Bearer token = immediate impersonation. Mitigations:
short expiry, token binding (RFC 8471, bind token to TLS
channel), DPoP (RFC 9449, proof-of-possession for OAuth).
For high-value APIs: consider mTLS (mutual TLS) where
the client certificate cryptographically proves identity
at the transport layer - no token can be stolen (the
private key never leaves the client). The combination
of mTLS + Bearer at the API layer provides defense in
depth.

---

### ⚙️ How It Works (Mechanism)

**Basic Auth flow:**

```
Client:
  GET /api/data HTTP/1.1
  Authorization: Basic dXNlcjpwYXNzd29yZA==

Decode: base64("user:password") = "user:password"

Server:
  1. Extract credentials
  2. Hash password: bcrypt("password", stored_salt)
  3. Compare to stored hash
  4. Success → 200 OK with data
  5. Fail → 401 Unauthorized
     WWW-Authenticate: Basic realm="API"
```

**Bearer Token flow:**

```
Step 1: Get token (OAuth/Login)
  POST /auth/token
  {"username":"user","password":"pass"}
  ← {"access_token":"eyJ...", "expires_in": 3600}

Step 2: Use token
  GET /api/data HTTP/1.1
  Authorization: Bearer eyJ...

Step 3: Server validates
  a. Extract token from "Bearer " prefix
  b. For JWT: verify signature + check exp claim
  c. For opaque: Redis/DB lookup → find user + scopes
  d. Check required scope for this endpoint
  e. 200 OK on success / 401 on invalid / 403 on scope
```

```mermaid
sequenceDiagram
    participant C as Client
    participant AS as Auth Server
    participant API
    C->>AS: POST /auth/token (credentials)
    AS-->>C: access_token (expires_in: 3600)
    C->>API: GET /data (Authorization: Bearer token)
    API->>API: Validate token (JWT sig or DB lookup)
    API-->>C: 200 OK with data
    Note over C,API: After expiry
    C->>API: GET /data (Authorization: Bearer token)
    API-->>C: 401 Unauthorized
    C->>AS: POST /auth/refresh (refresh_token)
    AS-->>C: new access_token
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Production Bearer token validation middleware:**

```python
import jwt
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET = "your-256-bit-secret"  # from env var
JWT_ALGORITHM = "HS256"

def require_auth(required_scope=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return jsonify(
                    {"error": "missing_token"}
                ), 401

            token = auth[7:]  # strip "Bearer "
            try:
                payload = jwt.decode(
                    token,
                    JWT_SECRET,
                    algorithms=[JWT_ALGORITHM]
                )
            except jwt.ExpiredSignatureError:
                return jsonify(
                    {"error": "token_expired"}
                ), 401
            except jwt.InvalidTokenError:
                return jsonify(
                    {"error": "invalid_token"}
                ), 401

            if required_scope:
                scopes = payload.get("scope", "").split()
                if required_scope not in scopes:
                    return jsonify(
                        {"error": "insufficient_scope"}
                    ), 403

            g.user_id = payload["sub"]
            g.scopes = payload.get("scope", "")
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route("/api/orders")
@require_auth(required_scope="orders:read")
def get_orders():
    return jsonify(
        db.orders.for_user(g.user_id)
    )
```

---

### 💻 Code Example

**Example 1 - BAD: Basic Auth over HTTP (plaintext)**

```python
# BAD: Basic Auth without TLS = credentials in plaintext
import requests

# Anyone sniffing network traffic sees:
# Authorization: Basic dXNlcjpwYXNzd29yZA==
# Decoded: user:password
response = requests.get(
    "http://api.example.com/data",  # HTTP, not HTTPS!
    auth=("user", "password")
)

# GOOD: Always use HTTPS with Basic Auth
response = requests.get(
    "https://api.example.com/data",  # HTTPS required
    auth=("user", "password")
)

# BETTER: Use Bearer token instead of Basic Auth
token = get_bearer_token()
response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {token}"}
)
```

---

**Example 2 - BAD: Token in URL query string**

```python
# BAD: token in URL (logged in server logs, CDN, browser
#      history; cached by CDN; visible in Referer header)
response = requests.get(
    "https://api.example.com/data?token=eyJ..."
)

# GOOD: token always in Authorization header
response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer eyJ..."}
)
```

---

**Example 3 - Diagnostic: decode a token**

```bash
# Inspect a JWT Bearer token without secret
token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSJ9.xxx"

# Decode header.payload (never sends secret anywhere)
echo $token | cut -d'.' -f1 | \
  base64 -d 2>/dev/null | python3 -m json.tool
# {"alg":"HS256","typ":"JWT"}

echo $token | cut -d'.' -f2 | \
  base64 -d 2>/dev/null | python3 -m json.tool
# {"sub":"user1","exp":1706000000,"scope":"read"}

# Check expiry
date -d @1706000000
# Tue Jan 23 04:53:20 UTC 2024
```

---

### ⚖️ Comparison Table

| Scheme | Encoding | Expiry | Revocable | Use Case |
|:---|:---|:---|:---|:---|
| Basic Auth | base64 | No | No | Internal/scripts; requires TLS |
| Bearer (opaque) | Opaque | Yes | Yes (DB delete) | User sessions, high security |
| Bearer (JWT) | Signed JSON | Yes | Limited (list) | Microservices, stateless scale |
| API Key | Custom | Rarely | Yes (delete key) | B2B/developer APIs |
| mTLS | Certificate | Certificate TTL | Yes (revoke cert) | High-security service mesh |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Base64 is encryption | Base64 is reversible encoding - trivially decoded without any key. Basic Auth credentials are plaintext over non-TLS connections. |
| Bearer tokens are safe forever | Bearer tokens are opaque credentials: "whoever bears this token is authenticated." A stolen token = immediate impersonation until expiry. Short expiry (15-60 min) limits the damage window. |
| 401 and 403 are interchangeable | 401 = authentication failure (who are you?). 403 = authorization failure (I know who you are, but you do not have permission). Mixing these breaks OAuth clients that depend on 401 to trigger token refresh. |
| JWT are always better than opaque tokens | JWT cannot be revoked before expiry without a revocation list (defeating the stateless benefit). For logout or account compromise scenarios, opaque tokens with DB lookup are easier to revoke instantly. |

---

### 🚨 Failure Modes & Diagnosis

**Token sent in URL query string - exposed in logs**

**Symptom:** Tokens appearing in web server access logs,
CDN request logs, and browser history. Tokens in
`Referer` headers sent to third-party analytics.

**Root Cause:** Developer used `?access_token=...` for
convenience. Query strings are logged everywhere.

**Diagnostic:**
```bash
# Check if tokens appear in logs
grep "access_token=" /var/log/nginx/access.log | head -5
# If results appear: tokens are in plaintext in logs
```

**Fix:** Always use `Authorization: Bearer <token>`.
Remove query string token support. Rotate all exposed tokens.

---

**401 vs 403 confusion breaking OAuth clients**

**Symptom:** After token expiry, mobile client loops
instead of refreshing. OAuth framework does not retry.

**Root Cause:** Server returns 403 (not 401) for expired
tokens. OAuth clients watch for 401 to trigger refresh.
403 is interpreted as "permanently unauthorized."

**Fix:** Return 401 with `WWW-Authenticate: Bearer
error="invalid_token"` for expired/invalid tokens.
Return 403 only for valid tokens with insufficient scope.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Request Headers` - `Authorization` header is the
  delivery mechanism
- `HTTP Status Codes` - 401 vs 403 distinction
  is critical for auth flows

**Builds On This (learn these next):**
- `JWT (JSON Web Token)` - most common Bearer token format
- `OAuth 2.0 Flows` - standard flow for issuing Bearer tokens
- `JWT Security` - algorithm confusion, weak secrets

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Standardized HTTP credential format in    │
│              │ Authorization header                      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without standards, every API invents its  │
│ SOLVES       │ own credential mechanism                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ base64 is NOT encryption. Basic Auth      │
│              │ credentials are readable by anyone who    │
│              │ can see the request. TLS is mandatory.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any HTTP API needing authentication       │
│              │ Bearer for user APIs; Basic for internals │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Tokens in URL query strings (logged)      │
│ PATTERNS     │ Basic Auth over HTTP (plaintext creds)    │
│              │ 403 for expired tokens (breaks OAuth)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Bearer token expiry (more auth round-     │
│              │ trips) vs long-lived (revocation risk)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bearer token = visitor badge (expires).  │
│              │ Basic Auth = house key (permanent risk)." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JWT → OAuth 2.0 Flows → JWT Security      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. base64 is encoding, not encryption. Basic Auth requires
   TLS; without it, credentials are plaintext.
2. Return 401 for invalid/expired tokens, 403 for
   insufficient scope. Mixing them breaks OAuth clients.
3. Never put tokens in URL query strings - they get
   logged in servers, CDNs, browser history, and Referer
   headers.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Authentication is a trade-off between security (short-lived
credentials, revocable) and latency (longer-lived, no
DB lookup per request). JWT Bearer tokens optimize for
latency (no DB lookup) at the cost of revocability.
Opaque tokens optimize for revocability at the cost of
a DB lookup on every request. The right choice depends
on security requirements: financial/health APIs → opaque
with instant revocation; public read APIs → JWT with
short expiry.

**Where else this pattern applies:**
- SSH key authentication: private key signs a challenge
  (similar to mTLS concept)
- AWS IAM: temporary STS credentials (Bearer token
  analog, expire in 1-12 hours)
- Kubernetes Service Accounts: pod tokens are JWT Bearer
  tokens validated by the API server

---

### 💡 The Surprising Truth

The HTTP `Authorization` header name is misleading. Despite
the name, the header is used for **authentication** (proving
identity), not **authorization** (proving permission).
The RFC authors acknowledged this was a naming error but
did not change it for backward compatibility. In OAuth 2.0,
this creates genuine confusion: the OAuth spec calls it
"authorization" throughout, but what flows through the
`Authorization` header is the authentication token.
The correct terms: authentication = who are you;
authorization = what are you allowed to do.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe why base64 encoding of credentials
   in Basic Auth is not encryption, and what this requires.
2. **DISTINGUISH** Explain when to return 401 vs 403 and
   why mixing them breaks OAuth clients.
3. **BUILD** Implement a Bearer token validation middleware
   that correctly handles: missing token (401), expired
   token (401), invalid signature (401), insufficient
   scope (403).
4. **DIAGNOSE** Given a token, decode its header and
   payload without a library, identify the algorithm
   and expiry claim.
5. **COMPARE** Explain the trade-off between JWT (stateless)
   and opaque tokens (revocable) for high-security APIs.

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Basic Auth and
Bearer Token authentication?**

*Why they ask:* Fundamental API security knowledge.
Tests understanding of credential lifecycle.

*Strong answer includes:*
- Basic Auth: base64(username:password) on every request.
  Long-lived credential. Requires TLS. No expiry, hard
  to revoke without password change.
- Bearer Token: short-lived token (opaque or JWT) issued
  by auth server. Validated on each request. Expires.
  Can be revoked. Scoped to specific permissions.
- When to use each: Basic Auth for internal services,
  scripts, CLI. Bearer for user-facing APIs, mobile
  apps, OAuth flows.
- Critical: base64 is NOT encryption. Basic Auth is
  plaintext without TLS.

**Q2: When should you return 401 vs 403 in an API?**

*Why they ask:* Tests precise HTTP knowledge and awareness
of how OAuth clients behave.

*Strong answer includes:*
- 401 Unauthorized (misleadingly named): authentication
  problem. Token missing, expired, or invalid signature.
  Should include `WWW-Authenticate` header. OAuth clients
  use 401 as the signal to attempt token refresh.
- 403 Forbidden: authentication succeeded (token is
  valid) but the identity lacks permission for this
  resource or action. Do not trigger token refresh.
- Mixing 401/403: if server returns 403 for expired
  tokens, OAuth clients do not refresh → user stuck in
  an "infinite logout" state. Production bug.
- Rule: 401 = "prove yourself," 403 = "I know who you
  are, but no."

**Q3: Why is putting access tokens in URL query strings
a security problem?**

*Why they ask:* Tests practical security awareness.

*Strong answer includes:*
- URLs are logged in: web server access logs, CDN logs,
  browser history, server-side analytics.
- URLs appear in `Referer` headers sent to third-party
  scripts (ads, analytics) when the user navigates away.
- URLs can be bookmarked, shared, cached by proxies.
- Mitigation: always use `Authorization: Bearer` header.
  Headers are not logged by default. They are not included
  in `Referer`.
- RFC 6750 explicitly states tokens MUST NOT be passed
  in URLs except when HTTP headers are not available.
