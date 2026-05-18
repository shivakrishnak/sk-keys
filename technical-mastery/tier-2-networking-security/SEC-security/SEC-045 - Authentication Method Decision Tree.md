---
id: SEC-045
title: "Authentication Method Decision Tree"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-014, SEC-016, SEC-018, SEC-034, SEC-039, SEC-040
used_by: SEC-056, SEC-057, SEC-058, SEC-071, SEC-078, SEC-113
related: SEC-014, SEC-016, SEC-018, SEC-034, SEC-039, SEC-040, SEC-056, SEC-057
tags:
  - security
  - authentication
  - jwt
  - sessions
  - oauth
  - api-keys
  - mtls
  - decision-tree
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/sec/authentication-method-decision-tree/
---

⚡ TL;DR - Authentication method selection determines your
security, scalability, and revocation capabilities. The wrong
choice creates hard-to-fix architectural debt. Use this
decision tree:

```
Is it a human-facing browser app?
  YES → Sessions (server-side) OR JWT in memory (not localStorage)
      → Need SSO/federated login? Add OAuth/OIDC on top
  
  NO - Is it machine-to-machine (service-to-service)?
      YES → Internal network: API keys OR mutual TLS (mTLS)
           → External partners: OAuth client_credentials flow
      
      NO - Is it a mobile app?
           YES → OAuth 2.0 + PKCE with refresh tokens
                → Store tokens in secure storage (Keychain/Keystore)
                → Never: localStorage in WebView

THEN: Add MFA for human auth where data is sensitive.
```

**The non-negotiable rule:** Every authentication method has
a revocation mechanism. Without one: compromised credentials
cannot be invalidated before expiry.

---

| #045 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Authentication, JWT, OAuth 2.0, CSRF Prevention, Session Security, API Security | |
| **Used by:** | JWT Anti-Patterns, OAuth 2.0 Deep Dive, OIDC, Auth Migration, OAuth vs SAML | |
| **Related:** | Session Management, JWT, OAuth 2.0, OIDC, mTLS, API Keys, MFA | |

---

### 🔥 The Problem This Solves

**WRONG AUTHENTICATION CHOICE = ARCHITECTURAL DEBT:**

```
CASE 1: Team chooses JWT for everything because "stateless is cool"
  
  Three months later:
  - Security incident: attacker got a JWT token
  - Security team: "Invalidate the compromised tokens"
  - Developer: "We can't. JWTs are stateless - we'd have to
    invalidate ALL tokens, logging out everyone, or rotate
    the signing secret (same effect)."
  - Security team: "What if we keep a token blacklist?"
  - Developer: "That requires a shared data store (Redis),
    which makes it stateful. We've rebuilt sessions with
    extra steps."
  
  Issue: JWT was chosen without thinking through revocation.
  Sessions (or JWT with refresh token + blacklist) would have
  been the right choice.

CASE 2: Team uses API keys for browser SPA
  
  The key must be embedded in JavaScript (client-side code):
  Any user can view it in browser DevTools → Network tab.
  It's not a secret at all.
  
  Issue: API keys are for server-to-server auth where the key
  can be stored securely server-side. Not for browser clients.

CASE 3: Team stores JWT in localStorage
  
  Any JavaScript running on the page can read localStorage.
  XSS vulnerability → `localStorage.getItem('jwt')` → steal token.
  JWT in localStorage + XSS = account takeover.
  
  Issue: localStorage has no XSS protection. HttpOnly cookies
  do. JWT in localStorage is never correct for security-sensitive apps.

CASE 4: Team uses OAuth for internal service-to-service auth
  
  OAuth is designed for delegated authorization
  (User A grants App B access to User A's data).
  For service-to-service: no user involved. OAuth is unnecessary
  complexity. API keys with key rotation or mTLS is simpler,
  more appropriate, and easier to reason about.
```

---

### 📘 Textbook Definition

**Authentication Methods:**

**Server-Side Sessions:** Server generates a session ID, stores
session data server-side (memory, Redis, database), sends session
ID to client as a cookie. Session cookie is opaque (just an ID).
Authorization check: look up session ID in store → get user data.
Revocation: delete session record. Requires server-side state.

**JWT (JSON Web Tokens):** Cryptographically signed token
containing user claims (user ID, roles, expiry). Client stores
token; server validates signature without database lookup.
Stateless: server doesn't store session data. Revocation:
difficult (requires blacklist or short expiry + refresh tokens).

**OAuth 2.0:** Framework for delegated authorization.
User grants third-party app access to their data. Access tokens
(short-lived), refresh tokens (long-lived). Flows: Authorization
Code + PKCE (browser/mobile), Client Credentials (server-to-server),
Device Flow (TV/CLI). OIDC adds identity layer on top of OAuth.

**API Keys:** Static shared secret. Server validates key on each
request. Simple key-value lookup. Used for server-to-server,
developer APIs, webhooks. Should be long (256-bit random),
rotatable, scoped (minimum privilege).

**Mutual TLS (mTLS):** Both client and server present X.509
certificates. Server verifies client certificate is signed by
a trusted CA. No shared secret to steal. Complex to set up
but strong for service meshes (Istio, Linkerd automate this).

**Passkeys (FIDO2/WebAuthn):** Platform-bound asymmetric
cryptography. Private key never leaves the device. Phishing-
resistant (bound to origin). Replacing passwords for consumer
apps. No server-side password storage needed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sessions are stateful (server stores data, cookie is just a key);
JWT is stateless (all data in the token); OAuth handles
"third party acts on behalf of user"; API keys handle
"server identifies itself to another server."

**One analogy:**
> Sessions = a coat check. You arrive, leave your coat
> (session data stored server-side), get a ticket (session ID cookie).
> To get your coat: present the ticket. If you lose the ticket:
> coat check can cancel ticket (revocation). If you misbehave:
> coat check can invalidate all your tickets immediately.
>
> JWT = a laminated ID card you printed yourself.
> Everything's on the card (name, photo, expiry). Businesses
> verify the card format and signature without calling anyone
> (no server state). But if you're banned: can't take the card away.
> Must wait for it to expire. Or build a blocklist (which is just
> a centralized coat check again).
>
> API key = a door access card for employees.
> Useful for recurring, automated access by known parties.
> Not for guests (users) who arrive unexpectedly.
>
> OAuth = a valet key.
> You give the valet a limited key (access token) that only
> opens the door and starts the car, not the glove compartment.
> You can take it back (revoke) when done.

---

### 🔩 First Principles Explanation

**Complete decision framework:**

```
AUTHENTICATION DECISION TREE:

STEP 1: WHO is being authenticated?

  A) Human User (has a browser or mobile device)
     → Go to Step 2A
  
  B) Machine / Service (no human involved)
     → Go to Step 2B

STEP 2A: HUMAN - What type of client?

  A1) Browser-based Web Application
       → PRIMARY: Server-side sessions
         WHY: HttpOnly cookie → XSS-resistant.
              Immediate revocation by deleting session record.
              Standard, well-understood, works everywhere.
         SECONDARY: JWT in memory (not localStorage, not cookie)
           WHY: Stateless reduces server load.
                BUT: Token lost on tab close (poor UX).
                     Cannot revoke individual tokens.
                ONLY IF: Short-lived token (15 minutes)
                         + refresh token pattern.
       → ADD: OAuth/OIDC if you need:
              Federated login (Google/GitHub/Azure AD)
              SSO across multiple applications
         NEVER: Store JWT in localStorage (XSS risk)
         NEVER: API key in browser (JavaScript-readable)

  A2) Mobile Application (iOS/Android)
       → PRIMARY: OAuth 2.0 + PKCE + refresh tokens
         WHY: Mobile apps are public clients (can't store secrets).
              PKCE prevents authorization code interception.
              Refresh tokens handle offline access.
              Store tokens in Keychain (iOS) / Keystore (Android).
         NEVER: Store tokens in AsyncStorage/SharedPreferences
                (easily readable without root on many devices).

  A3) CLI Tool / Desktop App
       → PRIMARY: OAuth 2.0 Device Authorization Grant
         WHY: User opens URL in browser, enters device code.
              App receives tokens without handling password.
         SECONDARY: OAuth 2.0 + PKCE (if browser available)

STEP 2B: MACHINE - What relationship?

  B1) Internal Service (same organization, same network/cluster)
       → PRIMARY: mTLS (mutual TLS)
         WHY: Certificate-based, no shared secret to leak.
              Service meshes (Istio, Linkerd) automate this.
              Identifies both parties cryptographically.
         SECONDARY: API keys (simpler to implement)
           REQUIREMENTS: Long (256-bit+), rotatable, scoped.
                         Stored in secrets manager (Vault, AWS SM).
                         Never hardcoded or in config files.

  B2) External Service / Partner / Third-Party API
       → PRIMARY: OAuth 2.0 Client Credentials Flow
         WHY: No user delegation. Client (your service)
              authenticates directly to authorization server.
              Access token is short-lived (revocable by expiry).
         SECONDARY: API keys (if OAuth is overkill)
           USE WHEN: Simple webhook signatures, basic API access.
           REQUIRES: Shared secret → rotate regularly.

  B3) Webhook Receiver (you receive events from external service)
       → HMAC signature verification
         WHY: External service signs payload with shared secret.
              You verify signature matches.
              Not authentication per se - message integrity.
         EXAMPLE: GitHub webhooks use X-Hub-Signature-256
                  Stripe uses Stripe-Signature header

STEP 3: REVOCATION - Can you revoke quickly?

  Sessions: Delete session record → immediate revocation
  JWT (stateless): Wait for expiry OR implement blacklist
    → If revocation is required: use short expiry (15min)
      + refresh token (stored server-side, revocable)
  OAuth tokens: Revoke via authorization server's revoke endpoint
  API keys: Delete key record → immediate revocation
  mTLS certs: CRL or OCSP (certificate revocation)
              OR: rotate certificates frequently (cert validity period)

STEP 4: MFA - Is the data sensitive enough to require MFA?
  Financial data, healthcare, PII, admin access → Yes, require MFA.
  TOTP (Google Authenticator) → implement, good baseline
  FIDO2/WebAuthn (hardware key or device biometric) → phishing-resistant
  SMS OTP → avoid (SIM swap attacks), but better than nothing
```

---

### 🧪 Thought Experiment

**SCENARIO: SaaS application architecture requiring multiple auth methods**

```
SYSTEM: Project management SaaS
  - Web application (human users in browsers)
  - Mobile apps (iOS and Android)
  - Public API (for customer integrations)
  - Internal microservices (inter-service communication)
  - Webhooks (events to customer systems)
  - GitHub Actions integration (CI/CD access to API)

AUTHENTICATION CHOICES:

1. WEB APP (human users in browsers):
   → Server-side sessions + HttpOnly cookies
   + OIDC federation (Google/Microsoft login)
   + TOTP MFA for sensitive operations
   
   Why sessions: immediate revocation when admin deactivates user.
   Why OIDC: users want single sign-on with corporate identity.
   
2. MOBILE APPS (iOS/Android):
   → OAuth 2.0 + PKCE (Authorization Code flow)
   → Access token: 15-minute expiry
   → Refresh token: 30-day expiry, stored in Keychain/Keystore
   → Refresh token rotation: each use → new refresh token issued
     (old one immediately invalid - detect replay attacks)
   
3. PUBLIC API (customer server integrations):
   → API keys for simple integrations
     (developer creates key in dashboard, stores in their secrets manager)
   → OAuth 2.0 Client Credentials for larger customers
     (proper client_id/client_secret flow with token rotation)
   
   Key management: keys are per-workspace, scopeable
   (read-only key vs read-write key vs admin key).

4. INTERNAL MICROSERVICES:
   → mTLS via Istio service mesh
     Each service gets a certificate; Istio automates rotation.
     No shared secrets to manage. Zero-trust within the cluster.

5. WEBHOOKS TO CUSTOMERS:
   → HMAC-SHA256 signatures (not authentication, integrity)
     Customer verifies signature to confirm event came from us.

6. GITHUB ACTIONS / CI/CD:
   → OIDC tokens (GitHub Actions native OIDC)
     GitHub Actions gets a short-lived JWT from GitHub's OIDC provider.
     Cloud providers (AWS, GCP, Azure) trust GitHub's OIDC.
     No long-lived secret stored in GitHub.
     This is the modern approach - no AWS_SECRET_ACCESS_KEY in secrets.

RESULT: Six different components → four authentication methods.
Not one method for everything. Right tool for each use case.
```

---

### 🧠 Mental Model / Analogy

> Authentication methods are like different types of employee
> access systems in a large building:
>
> **Sessions** = Receptionist-managed visitor badges.
> You sign in, receptionist keeps your info, gives you a badge
> (session ID). Badge alone means nothing - receptionist has
> your real info. Badge revoked: call receptionist, done.
>
> **JWT** = Self-contained laminated ID card.
> Card includes your name, photo, expiry. Guards verify the
> card itself without calling anyone. If you're fired: card
> still works until it expires. Security trade-off: convenience
> (no central lookup) vs revocation difficulty.
>
> **API Keys** = Employee keycards.
> Given to known people/systems. Magnetic stripe, no biometrics.
> Works 24/7 for the same person. Can be deactivated centrally.
> Not for guests (users who walk in from outside without prior registration).
>
> **OAuth** = Temporary contractor access.
> You're a visitor (user) who grants the contractor (third-party app)
> access to specific floors (resources) for a specific time.
> Contractor gets a temporary key (access token), not your master key.
> You can revoke the contractor's access at any time.
>
> **mTLS** = Security door that recognizes trusted organizations'
> ID cards. Your company's badge works because the door trusts
> your company's ID system. Partner company's badge also works
> because both organizations' ID systems are in the trusted list.
> Mutual recognition - both sides identify themselves.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Different ways applications verify who you are and what you're
allowed to do. Sessions: old-school, reliable (server remembers
you). JWT: modern, stateless (you carry a signed pass). OAuth:
"login with Google" style. API keys: for apps talking to other
apps. mTLS: secure automatic recognition for services.

**Level 2 - How to use it (junior developer):**
For your web app: use server-side sessions (Django, Flask, Spring Session). Cookie: `HttpOnly; Secure; SameSite=Lax`. For OAuth login (Google/GitHub): library handles flow (Authlib, Spring Security OAuth2). For your REST API called by other services: API keys stored in their secrets manager. For mobile: OAuth + PKCE, store tokens in Keychain. Never put JWT in localStorage.

**Level 3 - How it works (mid-level engineer):**
The stateful vs stateless distinction is the key trade-off. Sessions require distributed session store (Redis) for horizontal scaling. JWT eliminates this but loses revocation capability. Compromise: short-lived JWT (15min) + stateful refresh tokens (revocable, stored in DB). On logout: revoke refresh token. Short access token expiry limits blast radius of stolen access tokens. OAuth authorization code + PKCE: authorization code is single-use and short-lived (10s), code verifier prevents interception attacks. Client credentials: no user - service authenticates directly.

**Level 4 - Why it was designed this way (senior/staff):**
Each method was designed for a specific trust and deployment context. Sessions: designed for monolith web apps where the server holds all state. JWT: designed for distributed systems where services can validate tokens without calling home. OAuth: designed for the problem of "service A wants to access user's data in service B" without giving service A the user's password. API keys: designed for the B2B developer API context where the consumer is a known, registered entity. mTLS: designed for zero-trust network environments where even internal network traffic is not trusted. The wrong choice creates technical debt: using JWT where sessions fit causes revocation problems; using sessions where JWT fits causes session store scaling challenges.

**Level 5 - Mastery (distinguished engineer):**
Distributed systems introduce the "token exchange" problem:
service A validates user's JWT, then calls service B on behalf
of the user. Token forwarding (service A sends original JWT)
vs token exchange (OAuth 2.0 RFC 8693 Token Exchange: service
A gets a new token scoped for service B on behalf of user).
Token forwarding is simpler but gives service B full user access.
Token exchange enables least-privilege propagation. For complex
multi-service architectures: consider an authorization service
(Zanzibar model: SpiceDB, Permify) that handles "can user X
do action Y on resource Z" as a policy service, separate from
authentication. Authentication proves identity; authorization
determines permissions. These are separate concerns and separate
systems at scale.

---

### ⚙️ How It Works (Mechanism)

**Session vs JWT token lifecycle:**

```
SERVER-SIDE SESSION FLOW:

1. Login:
   Client → POST /login {username, password}
   Server validates credentials
   Server creates session: {user_id: 42, roles: ['user'], created_at: ...}
   Server stores session in Redis: KEY=session:abc123 VALUE=<json>
   Server sets cookie: Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax
   Client stores cookie automatically (browser)

2. Subsequent requests:
   Client → GET /api/profile (Cookie: session_id=abc123)
   Server reads session_id from cookie
   Server looks up Redis: GET session:abc123 → {user_id: 42, ...}
   Server processes request for user 42

3. Logout / Revocation:
   Client → POST /logout
   Server: DEL session:abc123 (delete from Redis)
   Server clears cookie
   Immediately effective: abc123 no longer valid.

JWT FLOW:

1. Login:
   Client → POST /login {username, password}
   Server validates credentials
   Server creates JWT:
     header: {alg: HS256, typ: JWT}
     payload: {sub: "42", roles: ["user"], exp: 1700000000, iat: 1699999000}
     signature: HMAC_SHA256(base64(header) + "." + base64(payload), SECRET_KEY)
   JWT = base64(header).base64(payload).signature
   Client receives JWT, stores it (memory or localStorage - see risk)

2. Subsequent requests:
   Client → GET /api/profile (Authorization: Bearer <JWT>)
   Server decodes JWT (base64)
   Server verifies signature (no DB call needed)
   Server checks exp (expiry) claim
   Server processes request for user in sub claim

3. "Revocation" (the problem):
   JWT is valid until exp.
   Server cannot invalidate individual JWTs without:
     a) Token blacklist (DB lookup - defeats stateless benefit) OR
     b) Rotating signing secret (invalidates ALL tokens - logs everyone out) OR
     c) Short expiry (15 minutes) + refresh token pattern

REFRESH TOKEN PATTERN (best of both worlds):
   Access token: JWT, 15-minute expiry (stateless, fast)
   Refresh token: opaque, 30-day expiry, stored in DB (revocable)
   
   Access token expires → client sends refresh token
   Server validates refresh token against DB → issues new access token
   Revocation: delete refresh token from DB → user must re-authenticate
   Refresh token rotation: each use issues new refresh token
     (old one invalidated → detect replay attacks)
```

---

### 💻 Code Example

**Session vs JWT implementation comparison:**

```python
# FastAPI: Sessions vs JWT - trade-offs in code

# === SERVER-SIDE SESSION (stateful, revocable) ===

import redis
import secrets
from fastapi import FastAPI, Cookie, HTTPException, Response

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/sessions/login")
async def session_login(credentials: LoginRequest, response: Response):
    user = verify_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Create session
    session_id = secrets.token_urlsafe(32)  # 256-bit random
    session_data = {"user_id": user.id, "roles": user.roles}
    
    # Store in Redis with TTL
    redis_client.setex(
        f"session:{session_id}",
        3600,  # 1 hour TTL
        json.dumps(session_data)
    )
    
    # Secure cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,   # XSS protection
        secure=True,     # HTTPS only
        samesite="lax",  # CSRF protection
        max_age=3600
    )
    return {"status": "logged in"}

@app.post("/sessions/logout")
async def session_logout(session_id: str = Cookie(None), response: Response):
    if session_id:
        redis_client.delete(f"session:{session_id}")  # Immediate revocation
    response.delete_cookie("session_id")
    return {"status": "logged out"}

# === JWT WITH REFRESH TOKEN (stateless access, revocable refresh) ===

import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRY = timedelta(days=30)

@app.post("/jwt/login")
async def jwt_login(credentials: LoginRequest):
    user = verify_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Short-lived access token (stateless)
    access_token = jwt.encode({
        "sub": str(user.id),
        "roles": user.roles,
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRY,
        "type": "access"
    }, SECRET_KEY, algorithm="HS256")
    
    # Long-lived refresh token (stored in DB for revocability)
    refresh_token = secrets.token_urlsafe(32)
    db.store_refresh_token(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + REFRESH_TOKEN_EXPIRY
    )
    
    # Refresh token in HttpOnly cookie (XSS protection)
    # Access token returned in body (stored in memory by client)
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 900  # 15 minutes in seconds
    }

@app.post("/jwt/refresh")
async def jwt_refresh(refresh_token: str = Cookie(None)):
    record = db.get_refresh_token(refresh_token)
    if not record or record.expires_at < datetime.utcnow():
        raise HTTPException(401, "Invalid or expired refresh token")
    
    # Refresh token rotation (invalidate old, issue new)
    db.invalidate_refresh_token(refresh_token)
    new_refresh_token = secrets.token_urlsafe(32)
    db.store_refresh_token(new_refresh_token, record.user_id, ...)
    
    # Issue new access token
    new_access_token = jwt.encode({
        "sub": str(record.user_id),
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRY,
    }, SECRET_KEY, algorithm="HS256")
    
    return {"access_token": new_access_token}

@app.post("/jwt/logout")
async def jwt_logout(refresh_token: str = Cookie(None)):
    if refresh_token:
        db.invalidate_refresh_token(refresh_token)
        # Access token expires naturally within 15 minutes
        # Can add to short-lived blacklist if needed
    return {"status": "logged out"}
```

---

### ⚖️ Comparison Table

| Method | Stateful | Revocation | Scalability | Complexity | Best For |
|:---|:---|:---|:---|:---|:---|
| **Server Sessions** | Yes | Immediate | Needs shared store | Low | Web apps, monoliths |
| **JWT (access only)** | No | On expiry only | Excellent | Medium | Short-lived API tokens |
| **JWT + refresh** | Partial | Refresh revocable | Good | Medium-High | Scalable web/mobile |
| **API Keys** | Yes | Immediate | Good | Low | Server-to-server B2B |
| **OAuth CC Flow** | Yes | Token expiry + revoke | Good | Medium | Service-to-service |
| **mTLS** | No (cert-based) | CRL/OCSP/rotation | Excellent | High | Service mesh, zero-trust |
| **Passkeys** | No (device-bound) | Device management | Excellent | Medium | Consumer phishing-resistant |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| JWT is more secure than sessions | JWT and sessions have different security profiles, not a clear hierarchy. Sessions: revocable immediately, stored server-side (not exposed to client). JWT: decoded on client (payload visible to anyone, even without secret key), difficult to revoke. "Stateless" is a scalability feature, not a security feature. For many applications, sessions are more secure than JWT because of immediate revocability and server-side storage. The choice depends on requirements: if revocation speed matters (financial, healthcare), sessions or short-JWT + stateful refresh are better. If horizontal scaling without shared state matters more: JWT addresses that. Neither is universally more secure. |
| API keys are only for developers, not production services | API keys are entirely appropriate for production service-to-service authentication. The key requirement: store them securely (secrets manager, not config files), rotate them regularly (quarterly or on compromise), scope them (minimum privilege), and audit usage. Many mature APIs (Stripe, Twilio, SendGrid, OpenAI) use API key auth for production integrations. The limitation is that API keys are symmetric secrets (both parties must know the secret), unlike mTLS which uses asymmetric cryptography. For high-security environments: mTLS is preferred. For most production B2B integrations: properly managed API keys are practical and appropriate. |

---

### 🚨 Failure Modes & Diagnosis

**Common authentication method misconfigurations:**

```
FAILURE: JWT stored in localStorage - XSS leads to session theft

  DETECT:
    Code review: localStorage.setItem('token', response.token)
    Browser console: localStorage.getItem('token')  → token visible!
  
  IMPACT: Any XSS vulnerability → immediate credential theft.
    XSS + localStorage = account takeover.
  
  FIX: Store JWT in memory (JavaScript variable, not persisted)
    OR store in HttpOnly cookie (JavaScript cannot read it)
    OR use server-side sessions (no client-side token storage)
  
  COMMON IN: "JWT tutorial" code that follows bad examples.

FAILURE: No refresh token expiry - "forever session"

  DETECT:
    Code review: refresh token has no expiry column in DB
    Test: create token, wait 90 days, still works → problem
  
  IMPACT: Stolen refresh token provides permanent access.
  
  FIX: Refresh tokens must have expiry (30-90 days typical).
    Idle timeout: if refresh token unused for 30 days → expire it.
    Absolute timeout: expire after 90 days regardless of use.

FAILURE: API key in browser JavaScript bundle

  DETECT:
    View source of the page / Chrome DevTools → Sources tab
    Search for "apiKey", "api_key", "Authorization"
    OR: curl https://example.com/static/app.js | grep -i "api_key"
  
  IMPACT: API key exposed to anyone who views source.
    Attacker uses key for: data exfiltration, rate limit abuse,
    billing abuse, accessing private data.
  
  FIX: Never embed API keys in client-side code.
    Use server-side proxy: browser → your server → third-party API.
    Your server holds the key securely.

FAILURE: JWT algorithm confusion (alg: none attack)

  DETECT:
    Test: send JWT with {"alg": "none"} and remove signature
    If server accepts it → algorithm confusion vulnerability.
  
  FIX: Use jwt library that requires explicit algorithm allowlist:
    jwt.decode(token, key, algorithms=["HS256"])  # Allowlist
    Never: jwt.decode(token, key)  # Uses algorithm from header
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication Fundamentals` - core concepts
- `JWT (JSON Web Tokens)` - JWT deep dive
- `OAuth 2.0 Overview` - OAuth flows
- `Session Security` - server-side session implementation

**Builds on this:**
- `JWT Anti-Patterns` - JWT misuse patterns
- `OAuth 2.0 Deep Dive` - authorization server implementation
- `OIDC` - identity layer on OAuth
- `Authentication Migration` - migrating between methods

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BROWSER APP  │ Server-side sessions (HttpOnly cookie)    │
│              │ + OIDC/OAuth for federated login          │
├──────────────┼───────────────────────────────────────────┤
│ MOBILE APP   │ OAuth 2.0 + PKCE + Refresh tokens        │
│              │ Store in Keychain (iOS) / Keystore (Android)│
├──────────────┼───────────────────────────────────────────┤
│ SERVER→SERVER│ mTLS (zero-trust) or API keys (managed)  │
│              │ OAuth client_credentials for external      │
├──────────────┼───────────────────────────────────────────┤
│ JWT RULE     │ Short-lived (15min) + stateful refresh    │
│              │ NEVER in localStorage                     │
├──────────────┼───────────────────────────────────────────┤
│ REVOCATION   │ Sessions: delete record (instant)         │
│              │ JWT: only on refresh token expiry/revoke  │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Match the authentication mechanism to the threat model."
The threat model determines which properties matter:
revocability (stolen credential must be invalidated quickly)
favors sessions and short-JWT + stateful refresh;
horizontal scalability without shared state favors stateless JWT;
phishing resistance favors FIDO2/WebAuthn;
no user involvement favors mTLS or API keys;
delegated authorization favors OAuth. Before choosing an
authentication method, document: who authenticates (human/machine),
how credentials are stored by the client (cookie/memory/file),
what happens when a credential is compromised (how fast can
you revoke?), and what scaling constraints exist. The answers
determine the correct method. Architectural decisions made
without this analysis create technical debt that is painful
to undo.

---

### 💡 The Surprising Truth

The OAuth 2.0 Implicit Flow - once widely recommended for
SPAs (Single Page Applications) - was deprecated in RFC 9700
(2023) because it has a fundamental security flaw: the access
token is returned in the URL fragment, which ends up in:
browser history, referrer headers to third-party resources,
server logs, and proxy logs. The access token - which is
effectively a credential - is visible in all these places.
Every OAuth tutorial and library that recommended "use Implicit
Flow for SPAs" was recommending a fundamentally flawed approach.
The replacement: Authorization Code + PKCE (Proof Key for Code
Exchange). PKCE was originally designed for mobile apps (which
also can't safely store a client secret), and it turns out the
same solution works for SPAs. The lesson: authentication
standards evolve as attacks against them are discovered and
refined. "This was the recommended approach in 2015" is not
sufficient justification for continuing to use it. Review
your authentication choices against current IETF and OWASP
recommendations periodically.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **SELECT** the correct authentication method for any given
   context: browser app, mobile app, server-to-server, and
   justify the choice in terms of revocability and threat model.
2. **EXPLAIN** why JWT stored in localStorage is a security
   anti-pattern and what the correct storage options are.
3. **IMPLEMENT** server-side sessions with proper cookie attributes
   (HttpOnly, Secure, SameSite) or JWT + refresh token pattern.
4. **COMPARE** stateless (JWT) vs stateful (sessions) and explain
   when each is appropriate.

---

### 🎯 Interview Deep-Dive

**Q: When should you use sessions vs JWT? What are the trade-offs
and when would you choose each?**

*Why they ask:* Architecture decision question. Tests whether
the candidate understands stateful vs stateless, revocability,
and can reason about trade-offs rather than following hype.

*Strong answer includes:*
- Core difference: sessions are stateful (server stores data,
  client has opaque ID); JWT is stateless (all data in the token,
  server validates signature without DB lookup).
- Session advantages: immediate revocation (delete record),
  server-side storage (not exposed to client), simple to implement.
  Disadvantages: requires shared session store for horizontal scaling (Redis).
- JWT advantages: stateless (no shared store needed), works
  across domains (Authorization header vs cookie), self-contained.
  Disadvantages: hard to revoke (must wait for expiry or maintain blacklist).
- Compromise: short-lived JWT (15min) + stateful refresh token.
  Access token stateless (fast), refresh token revocable (security).
  This is the industry standard for modern APIs.
- When to use sessions: web apps where revocation speed matters
  (financial, healthcare), monolith where scaling is not a concern.
- When to use JWT: distributed systems, microservices, mobile
  API backends where statelessness simplifies architecture.
- Never: JWT in localStorage (XSS risk). Use HttpOnly cookies
  or in-memory storage.