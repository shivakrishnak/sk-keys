---
id: SEC-058
title: "OpenID Connect (OIDC)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-010, SEC-016, SEC-028, SEC-045, SEC-056, SEC-057
used_by: SEC-071, SEC-078, SEC-087, SEC-088, SEC-112
related: SEC-010, SEC-016, SEC-028, SEC-045, SEC-057, SEC-071, SEC-088
tags:
  - security
  - oidc
  - openid-connect
  - authentication
  - identity
  - id-token
  - sso
  - federated-identity
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/sec/openid-connect-oidc/
---

⚡ TL;DR - OpenID Connect (OIDC) is an identity layer on top of
OAuth 2.0 that adds authentication. OAuth 2.0 says "access
granted." OIDC says "this is Alice, and she granted access."
The ID token is a signed JWT with user identity claims.
Always verify the nonce claim to prevent replay attacks.

**OIDC vs OAuth 2.0 in one comparison:**
```
OAuth 2.0 only:
  access_token → "this client can read emails"
  (Who is the user? Unknown from access_token alone)

OAuth 2.0 + OIDC:
  access_token → "this client can read emails"
  id_token     → "the user is alice@example.com (sub: usr_123)"
  userinfo endpoint → fetch full profile if needed
```

---

| #058 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Fundamentals, Input Validation, JWT, Authentication Decision Tree, JWT Anti-Patterns, OAuth 2.0 | |
| **Used by:** | OAuth Implicit Flow Deprecation, OAuth vs SAML Decision, DevSecOps Pipeline, Enterprise Security Architecture | |
| **Related:** | OAuth 2.0, JWT, SAML, SSO, Federated Identity | |

---

### 🔥 The Problem This Solves

**WHY OAUTH 2.0 IS NOT ENOUGH FOR "LOGIN WITH GOOGLE":**

```
PROBLEM WITH PURE OAUTH 2.0 FOR AUTHENTICATION:

OAuth 2.0 was designed for authorization (access delegation), not
authentication (identity verification). An access_token says:
"the user authorized this client to do X." It does NOT reliably say:
"here is who the user is."

WHAT WENT WRONG (before OIDC existed):

  Many developers used OAuth 2.0 access tokens as identity tokens.
  They called the userinfo API (e.g., GET /userinfo) and used the
  sub (user ID) from the response to identify the user.
  
  VULNERABILITY: The access_token is intended to call APIs, not to
  identify users. If an access_token from one Google API was accepted
  by another Google API: an attacker could take an access_token
  originally granted to App A (say, a game) and use it to "log in"
  to App B (a banking app). Both apps accept any Google access_token.
  
  This was an actual attack class called "access token injection":
    1. Attacker convinces victim to authorize their (attacker's) app.
    2. Attacker gets access_token for their app.
    3. Attacker submits this token to victim's bank as "login with Google."
    4. Bank calls userinfo API: returns attacker's own user ID.
    5. Bank creates session for attacker's Google account... 
       but attacker had crafted the flow to make it look like the victim's login.
  
  The attack was possible because access_tokens have no:
    - "intended audience" bound to the specific app
    - "this token was issued for THIS specific login session"
    - "was actually authenticated in THIS login flow"

WHAT OIDC ADDS:

  ID Token (a JWT) with:
    iss: issuer (e.g., https://accounts.google.com) - where the token came from
    sub: subject (user ID) - who the user is
    aud: audience - which client_id this token is for (your app ONLY)
    iat: issued at
    exp: expiry
    nonce: random value from the original auth request (replay prevention)
    email: user's email (if scope=email requested)
    name: display name (if scope=profile requested)
  
  PREVENTS ACCESS TOKEN INJECTION:
    Your app verifies: aud == your_client_id
    Token issued for App A has aud=app_a_client_id
    If submitted to App B: aud check fails → rejected
  
  PREVENTS REPLAY ATTACKS:
    nonce claim must match the nonce your app sent in the auth request
    An old token replayed to your app: nonce doesn't match → rejected
```

---

### 📘 Textbook Definition

**OpenID Connect (OIDC):** An identity layer built on top of
OAuth 2.0 (specification: openid.net/connect). OIDC adds:
(1) ID Token (JWT with user identity claims), (2) UserInfo
endpoint (REST API for additional user profile claims),
(3) Discovery document (`/.well-known/openid-configuration`),
(4) Standard scopes (`openid`, `email`, `profile`).

**ID Token:** A JWT issued by the identity provider (IdP) that
contains claims about the authentication event: who the user is
(`sub`), when they authenticated (`auth_time`), which app they
authenticated for (`aud`), and the nonce from the original request.
NOT an access token. Only used to establish identity.

**UserInfo Endpoint:** An OAuth 2.0 protected endpoint that
returns claims about the authenticated user. Called with the
access token. Returns additional profile data beyond what fits
in the ID token (which should be small).

**OIDC Flows:** OIDC uses OAuth 2.0 flows:
- Authorization Code Flow (server-side apps)
- Hybrid Flow (server + client split - rare)
- OIDC + PKCE for mobile/SPA

**Discovery Document:** `/.well-known/openid-configuration`
(e.g., `https://accounts.google.com/.well-known/openid-configuration`)
contains: authorization_endpoint, token_endpoint, userinfo_endpoint,
jwks_uri (public keys), supported scopes, supported response types.
Client libraries use this for auto-configuration.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OIDC = OAuth 2.0 + "here's who the user is." OAuth handles
access delegation. OIDC adds an ID token (JWT) proving the
user's identity and nonce to prevent replay attacks. Use OIDC
for "Login with Google/GitHub/Okta." Use pure OAuth for
"allow this app to access your data."

**One analogy:**
> OAuth 2.0 is like a building access card that opens specific
> doors (scopes). It proves "this card can open room 324."
> It doesn't say who carries it.
>
> OIDC adds a photo ID attached to the access card.
> Now you know: "Alice can open room 324."
>
> The ID token = the photo ID.
> The access token = the door-opening card.
> They serve different purposes.
>
> The nonce on the ID token is like a time-stamped receipt
> from the front desk: "Alice requested this card at 2:34pm."
> An old photo ID or replayed authentication can't match
> the receipt from this specific request.

---

### 🔩 First Principles Explanation

**OIDC flow with ID token:**

```
OIDC AUTHORIZATION CODE FLOW:

STEP 1: Authorization Request (with OIDC scopes)
  GET /authorize?
    response_type=code
    &client_id=my_client_id
    &redirect_uri=https://myapp.com/callback
    &scope=openid%20email%20profile     ← "openid" triggers OIDC
    &state=<random>
    &nonce=<random>                     ← OIDC-specific, stored in session
    &code_challenge=<sha256_verifier>
    &code_challenge_method=S256
  
  "openid" scope = OIDC trigger.
  Without "openid" scope: OAuth 2.0 only (no ID token).
  With "openid" scope: IdP returns ID token.
  nonce: random value stored in client session for replay prevention.

STEP 2: Token Exchange Response (includes ID token)

  {
    "access_token": "ya29.a0AfH6SM...",  # For API calls
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "1//0gBEj...",      # For refreshing
    "id_token": "eyJhbGciOiJSUzI1NiI..." # NEW: identity JWT
  }
  
  ID token decoded:
  {
    "iss": "https://accounts.google.com",
    "sub": "110169484474386459429",     # Stable user ID
    "aud": "my_client_id",             # Must match YOUR app
    "exp": 1714784400,
    "iat": 1714780800,
    "nonce": "abc123xyz",              # Must match what we sent
    "email": "alice@gmail.com",
    "email_verified": true,
    "name": "Alice Smith",
    "picture": "https://lh3.google..."
  }

STEP 3: ID Token Validation (MANDATORY - all checks required)

  def validate_id_token(id_token: str, nonce: str) -> dict:
      # 1. Fetch public keys from JWKS URI
      #    (cache these; refresh on kid cache miss)
      jwks = fetch_jwks("https://accounts.google.com/.well-known/openid-configuration")
      
      # 2. Verify signature (using public key matching kid header)
      payload = jwt.decode(
          id_token,
          key=jwks,                                # Public key set
          algorithms=["RS256"],                    # Fixed algorithm
          audience="my_client_id",                 # Must be your app
          issuer="https://accounts.google.com",    # Must be Google
          options={"require": ["exp","iss","aud","sub","nonce"]},
      )
      
      # 3. Verify nonce (replay attack prevention)
      if payload["nonce"] != nonce:
          raise AuthError("Invalid nonce - possible replay attack")
      
      # 4. Check token freshness (exp already checked above, but
      #    also check iat - reject tokens too old)
      if time.time() - payload["iat"] > 300:  # 5 min max
          raise AuthError("ID token too old")
      
      return payload

STEP 4: Establish User Session

  # sub is the stable, persistent user identifier
  user_id = payload["sub"]
  email = payload.get("email")
  
  # Upsert user in your database
  user = db.upsert_user(external_id=user_id, provider="google", email=email)
  
  # Create YOUR app's session (not tied to the ID token)
  session["user_id"] = user.id
  
  # The ID token is consumed here. Don't store it or use it again.
  # Your session is now the auth mechanism for subsequent requests.
```

---

### 🧪 Thought Experiment

**SCENARIO: Building SSO across microservices**

```
PROBLEM: Three microservices (API Gateway, Orders Service, Profile Service).
All need to authenticate users. How to share identity?

APPROACH 1: Each service validates ID token independently (WRONG for most cases)
  
  Every service fetches JWKS from IdP, verifies ID token.
  Problem: ID token has short expiry (1 hour).
  Lots of JWKS fetches. Each service needs IdP configuration.
  ID token wasn't designed for this (it's for one-time identity establishment).
  
APPROACH 2: API Gateway + opaque session tokens (common, correct)
  
  API Gateway (or BFF - Backend For Frontend):
    Validates ID token at login
    Creates server-side session (stores user_id, roles in session store)
    Returns session_id in HttpOnly cookie to browser
  
  Subsequent requests:
    Browser sends session_id cookie
    API Gateway looks up session_id in Redis
    Gets user_id and roles
    Forwards request to microservice with user context in headers:
      X-User-Id: usr_123
      X-User-Roles: admin, editor
    
    Internal microservices trust these headers (mTLS or internal network)
  
  The ID token is used once: to establish the session.
  It's not passed around between services.
  
APPROACH 3: Service mesh with JWT propagation (distributed, stateless)
  
  API Gateway:
    Validates ID token at login
    Issues an INTERNAL JWT (signed by your internal key)
    Short expiry: 15 minutes
    Microservices accept INTERNAL JWTs (different from ID tokens)
  
  The internal JWT is your service's own token format.
  Microservices verify it with your internal public key.
  
  Difference from passing ID token:
    Internal JWT: your control, your key, your claims
    ID token: Google's format, Google's key, Google's claims
  
APPROACH 4: UserInfo endpoint caching (when extra claims needed)
  
  Sometimes you need claims not in the JWT (address, phone).
  Call /userinfo with access_token:
    GET https://idp.example.com/userinfo
    Authorization: Bearer <access_token>
    → Returns full profile
  
  Cache this in your session (don't call on every request).
  Cache TTL: match access_token expiry.
  On access_token refresh: refresh cached userinfo.
```

---

### 🧠 Mental Model / Analogy

> OIDC vs OAuth is like the difference between a hotel key
> card system and a check-in process.
>
> OAuth 2.0 (key card only):
> "This card opens room 324 and the gym." (access delegation)
> Who's the guest? Unknown from the key card alone.
>
> OIDC (check-in + key card):
> Check-in (OIDC): "You are Alice Smith, passport verified.
> You're in room 324." (authentication - identity established)
> Key card (OAuth): "This card opens room 324 and the gym."
> (access delegation)
>
> The ID token = the check-in record (Alice's identity).
> The access token = the key card (access permissions).
>
> The hotel's check-in database (auth server/IdP) issues both.
> The key card proves access. The check-in record proves identity.
>
> The nonce on the check-in record = the specific reservation
> confirmation number. Even if someone had a photocopy of
> Alice's check-in record from last year, it has a different
> reservation number → rejected.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OIDC is what makes "Login with Google" work. After you log in with Google, your app gets an ID token (a kind of digital ID card from Google) that tells your app: "This is Alice, confirmed by Google." Without OIDC, OAuth 2.0 only provides access permission, not identity. OIDC adds who the user is.

**Level 2 - How to use it (junior developer):**
Use an OIDC library (python-social-auth, authlib, passport.js with openid-connect). The library handles the flow automatically if you give it: client_id, client_secret, issuer URL. The library fetches the discovery document automatically, validates the ID token, and returns the user's sub (stable user ID), email, and name. Store the sub in your database as the user's external identifier (it's permanent across logins). Create your own session after validating the ID token.

**Level 3 - How it works (mid-level engineer):**
ID token validation steps: (1) fetch JWKS from discovery document's jwks_uri, (2) select the key matching the `kid` (Key ID) in the JWT header, (3) verify RS256 signature, (4) check iss matches expected IdP, (5) check aud matches your client_id, (6) check exp is in the future, (7) check nonce matches what you sent. All 7 checks are mandatory - missing any one creates a specific attack vector. The nonce prevents replay: an old ID token (from a previous login session) cannot be replayed because the nonce stored in the current session won't match. The aud claim prevents cross-client token injection.

**Level 4 - Why it was designed this way (senior/staff):**
OIDC was standardized in 2014 after several years of ad-hoc OAuth-for-identity implementations that had security flaws. The key design decisions: (1) a separate token type (ID token, not access token) for identity to make the purpose explicit; (2) the nonce for replay prevention that doesn't require server-side state at the IdP; (3) the discovery document for auto-configuration to reduce misconfiguration risk; (4) the aud claim to prevent cross-client confusion. OIDC Core specification (openid.net/specs/openid-connect-core-1_0.html) is the foundation; extensions cover session management, back-channel logout, and more. Most enterprise IdPs (Okta, Azure AD, Auth0, Keycloak) support OIDC.

**Level 5 - Mastery (distinguished engineer):**
Advanced OIDC: at_hash and c_hash claims in the ID token are hashes of the access_token and authorization_code respectively, allowing cross-binding verification (prevent code substitution attacks in hybrid flows). Back-channel logout (RFC 9470): IdP sends a logout_token to the client's back-channel endpoint when the user logs out - enables single logout (SLO) across all clients. Session Management specification: iframe-based session checking for browser-side logout propagation (less commonly implemented). OIDC Dynamic Registration: clients can register programmatically with the IdP. Federation: OIDC federation specification (draft) enables trust chains between multiple IdPs for multi-tenant enterprise scenarios. The FAPI (Financial-grade API) profiles of OIDC add additional requirements (JARM, request objects with signed parameters) for high-security financial services.

---

### ⚙️ How It Works (Mechanism)

**OIDC discovery and dynamic configuration:**

```
DISCOVERY DOCUMENT (/.well-known/openid-configuration):

  GET https://accounts.google.com/.well-known/openid-configuration
  
  Response:
  {
    "issuer": "https://accounts.google.com",
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    "response_types_supported": ["code", "token", "id_token", "..."],
    "subject_types_supported": ["public"],
    "id_token_signing_alg_values_supported": ["RS256"],
    "scopes_supported": ["openid", "email", "profile"],
    "token_endpoint_auth_methods_supported": [
      "client_secret_post", "client_secret_basic"
    ],
    "claims_supported": ["sub", "iss", "aud", "exp", "iat", "email", "name", "..."]
  }
  
  CLIENT LIBRARY USAGE:
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        # ^ Library fetches this and auto-configures endpoints + keys
        client_id=...,
        client_secret=...,
        client_kwargs={'scope': 'openid email profile'},
    )

JWKS (JSON Web Key Set) - key rotation:

  GET https://www.googleapis.com/oauth2/v3/certs
  
  Response:
  {
    "keys": [
      {
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": "f0b6e0b65e0c4f4b9d3c...",  ← Key ID
        "n": "...",                          ← RSA modulus
        "e": "AQAB"                          ← RSA exponent
      },
      {
        "kid": "a3b4c5d6e7f8...",            ← Different key (rotation)
        ...
      }
    ]
  }
  
  When verifying ID token:
    1. Read kid from JWT header
    2. Find the matching key in JWKS by kid
    3. Verify signature with that specific key
    4. If kid not found in cached JWKS: refresh cache once
    5. If still not found: reject token
  
  Key rotation: IdP publishes new keys, removes old ones.
  Clients must handle this gracefully (cache miss → refresh JWKS).
  Clients should cache JWKS (e.g., 1 hour TTL) to avoid rate limits.
```

---

### 💻 Code Example

**FastAPI: OIDC login with Google:**

```python
# OIDC "Login with Google" - FastAPI + Authlib

import secrets
from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_bytes(32))

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url=(
        'https://accounts.google.com/.well-known/openid-configuration'
    ),  # Auto-discovers all endpoints + public keys
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile',  # "openid" = OIDC trigger
    },
)

@app.get('/auth/login')
async def login(request: Request, next: str = '/dashboard'):
    # Validate next before storing
    if not next.startswith('/') or next.startswith('//'):
        next = '/dashboard'
    
    # Store next and nonce in session
    nonce = secrets.token_urlsafe(16)
    request.session['nonce'] = nonce
    request.session['next'] = next
    
    redirect_uri = 'https://myapp.com/auth/callback'
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        nonce=nonce,  # OIDC nonce for replay prevention
    )

@app.get('/auth/callback')
async def auth_callback(request: Request):
    # Exchange code for tokens
    token = await oauth.google.authorize_access_token(request)
    
    # ID token is automatically validated by Authlib:
    #   - Signature verified (RS256 using Google JWKS)
    #   - iss verified (https://accounts.google.com)
    #   - aud verified (your client_id)
    #   - exp verified
    #   - nonce verified (from session)
    id_token_claims = token.get('userinfo')  # Parsed ID token
    
    if not id_token_claims:
        return RedirectResponse('/auth/login')
    
    # Extract stable user identifier
    google_sub = id_token_claims['sub']      # Stable, permanent
    email = id_token_claims.get('email')
    name = id_token_claims.get('name')
    
    # Find or create user in your database
    user = await db.upsert_user(
        provider='google',
        external_id=google_sub,
        email=email,
        display_name=name,
    )
    
    # Create YOUR app's session (not tied to Google's tokens)
    request.session.clear()               # Clear OAuth state
    request.session['user_id'] = user.id  # Your internal user ID
    
    # Redirect to original destination
    next_url = request.session.pop('next', '/dashboard')
    return RedirectResponse(next_url)

@app.get('/auth/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/')
```

---

### ⚖️ Comparison Table

| Feature | Pure OAuth 2.0 | OAuth 2.0 + OIDC | SAML 2.0 |
|:---|:---|:---|:---|
| **Purpose** | Authorization | Authentication + Authorization | Authentication + SSO |
| **Token format** | Opaque or JWT | ID token (JWT) + access token | XML assertion |
| **Identity claims** | None standard | sub, email, name, etc. | Attributes in assertion |
| **Discovery** | No standard | /.well-known/openid-configuration | metadata XML |
| **Nonce/replay prevention** | No standard | nonce claim | InResponseTo |
| **Mobile/SPA support** | Yes + PKCE | Yes + PKCE | Poor (XML heavy) |
| **Enterprise SSO** | Limited | Yes | Dominant legacy |
| **Typical use case** | API access delegation | Consumer/developer login | Enterprise B2B SSO |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| The access_token can be used to identify the user (same as using the ID token). | The access_token is opaque to the client - it's a credential for the resource server (API), not an identity token for the client app. Never use the access_token to identify the user on the client side. Correct: validate the ID token (contains aud=your_client_id, nonce, sub). Incorrect: call /userinfo with access_token and use the result as your identity signal without having first validated an ID token - this is vulnerable to access token injection across apps that share the same IdP. Always establish identity via the ID token validation; use access_token only for API calls. |
| sub (subject) is the user's email or username. | `sub` is an opaque, permanent user identifier assigned by the IdP. For Google, it's a long numeric string (e.g., "110169484474386459429"). It's NOT the email address. Email addresses can change; the sub is permanent. Store sub as your external user identifier in the database. If the user changes their Google email, their sub remains the same. If you store email as the identifier, you'll create duplicate accounts when emails change. Use sub for linking; email for display. |

---

### 🚨 Failure Modes & Diagnosis

**Testing OIDC implementation security:**

```
TESTING CHECKLIST:

1. Nonce validation
   Replay the same ID token twice (copy the id_token from a
   legitimate login, submit it again to the callback endpoint).
   Expected: second submission fails (nonce already used,
             or session no longer has the nonce).
   Vulnerable: second submission succeeds → replay attack.

2. Audience validation (aud check)
   Get an ID token from App B (another app using the same IdP).
   Submit it to App A's callback endpoint.
   Expected: auth error (aud=app_b_client_id doesn't match App A).
   Vulnerable: login succeeds → cross-app token confusion.

3. Issuer validation (iss check)
   Forge an ID token from a different issuer (self-signed key).
   Expected: auth error (iss doesn't match expected IdP).
   Vulnerable: login succeeds → attacker can forge identities.

4. State validation (CSRF)
   Load login URL. Don't click it. Instead:
   Load the callback URL directly with a valid-looking code and no state.
   Expected: auth error (state mismatch or missing).
   Vulnerable: callback processes any code without state → CSRF.

DEBUGGING OIDC ISSUES:

   "Invalid nonce": nonce in ID token doesn't match session.
   Common cause: session lost between authorize and callback
   (session storage failure, different server instance handled
   the callback vs the login request in a cluster).
   Fix: use centralized session storage (Redis), not in-memory.
   
   "Invalid audience": aud doesn't match client_id.
   Check: client_id in auth request matches what you configured
   in the OIDC library. Common mistake: wrong client_id in config.
   
   "Signature verification failed": JWKS cache stale after key rotation.
   Fix: on kid not found in cache, re-fetch JWKS from IdP once.
   
   "Token expired": exp check failed.
   Check: server clock synchronized (NTP). Time skew > 5 min
   causes false exp failures.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Fundamentals` - authentication vs authorization
- `JSON Web Tokens (JWT)` - ID token format
- `JWT Security Anti-Patterns` - ID token verification pitfalls
- `OAuth 2.0 Deep Dive` - OIDC is built on OAuth 2.0

**Builds on this:**
- `OAuth Implicit Flow Deprecation` - how OIDC handles SPA auth
- `OAuth vs SAML Decision` - enterprise identity choice
- `Enterprise Security Architecture` - SSO design patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TRIGGER OIDC │ scope=openid (required)                   │
│ GET IDENTITY │ Validate ID token (NOT access_token)      │
├──────────────┼───────────────────────────────────────────┤
│ VALIDATE     │ Signature (RS256 from JWKS)               │
│ ID TOKEN     │ iss, aud (must match your client_id)      │
│ CHECKS       │ exp, iat, nonce (anti-replay)             │
├──────────────┼───────────────────────────────────────────┤
│ USER ID      │ sub claim (stable, permanent, not email)  │
│ EXTRA DATA   │ /userinfo endpoint with access_token      │
├──────────────┼───────────────────────────────────────────┤
│ AUTO-CONFIG  │ /.well-known/openid-configuration (JWKS,  │
│              │ endpoints) - use OIDC library             │
│ SAML vs OIDC │ SAML: enterprise legacy B2B SSO          │
│              │ OIDC: modern, REST-native, mobile-ready   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Separate identity from authorization - they solve different
problems, even when they use the same infrastructure."
OIDC builds on OAuth 2.0's infrastructure (same authorization
endpoint, same token endpoint) but adds a fundamentally different
abstraction: identity. The ID token and the access token are
siblings, not synonyms. This separation allows identity and
authorization to evolve independently: you can use OIDC for
login but use a different system for fine-grained authorization
(ABAC, OPA, Casbin) without changing the identity layer.
The same principle: in microservices, separate the authentication
service (who is this user?) from the authorization service
(can this user do X?) from the user profile service (what is
this user's profile?). These often start in one service
(the auth server) but can be decomposed independently.
Mixing identity and authorization in one model creates
coupling: adding a permission changes the identity schema.
Separating them creates clean interfaces.

---

### 💡 The Surprising Truth

OIDC was finalized as a specification in February 2014 -
after years of OAuth-for-identity implementations with security
flaws. But the nonce mechanism (the main replay prevention in OIDC)
was actually inspired by the ID Assertion problem documented in
an academic paper by Facebook engineers in 2012, describing how
OAuth access tokens were being misused as identity assertions
across multiple websites. Multiple major companies (LinkedIn,
GitHub) had implemented "Login with X" using OAuth access tokens
in ways that were vulnerable to cross-site request forgery and
confused deputy attacks before OIDC standardized the correct approach.
The nonce, aud, and iss claims in the ID token directly address
the attack classes that were actively being exploited in production
systems at the time of OIDC's design. The specification was
written with known, real-world attacks in mind - not hypothetical ones.
This is why OIDC's validation requirements are not optional:
each required claim addresses a documented attack.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between OAuth 2.0 and OIDC:
   what the ID token adds (aud, nonce, sub) and why the access_token
   alone is insufficient for identity.
2. **IMPLEMENT** OIDC login with a standard library (authlib, passport.js),
   including nonce generation, state, and proper ID token validation.
3. **VALIDATE** ID token manually: verify iss, aud, exp, nonce, signature.
4. **DIAGNOSE** OIDC failures: nonce mismatch (session loss), aud mismatch
   (wrong client_id), JWKS stale (key rotation), clock skew (exp false positive).

---

### 🎯 Interview Deep-Dive

**Q: What is OpenID Connect? How does it differ from OAuth 2.0?**

*Why they ask:* "Login with Google" is OIDC. Many developers use it
without understanding the distinction from OAuth. Tests real understanding.

*Strong answer covers:*
- OAuth 2.0: authorization framework. "Can this app access this resource
  on behalf of a user?" Returns access_token. Does NOT directly identify
  the user (access_token is for the resource server, not the client).
- OIDC: adds authentication (identity) layer. Returns ID token (JWT)
  with user identity claims: sub, email, name, aud, iss, nonce.
  The ID token answers "who is this user?" specifically for your app.
- Key claims in ID token: aud (must match your client_id), nonce
  (prevents replay - must match what you sent in auth request),
  sub (stable user identifier, not email).
- access_token injection attack: without OIDC, access tokens from
  one app used to "log in" to another app → OIDC's aud check prevents this.
- OIDC vs SAML: both for SSO, but OIDC is REST-native JSON/JWT;
  SAML is XML-based, enterprise legacy. New integrations: OIDC.
  Enterprise B2B with legacy: SAML still common.
- Discovery document: /.well-known/openid-configuration auto-configures
  endpoints and keys. Use OIDC libraries that consume this.
- Validate ID token (not just call userinfo): signature, iss, aud, exp, nonce.
  Store sub as user's external ID (permanent, not email).