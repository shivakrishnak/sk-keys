---
id: SEC-029
title: "OAuth 2.0 Basics"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-008, SEC-015, SEC-016, SEC-028
used_by: SEC-058, SEC-059, SEC-079, SEC-087, SEC-126
related: SEC-008, SEC-016, SEC-028, SEC-058, SEC-059, SEC-079, SEC-087, SEC-126
tags:
  - security
  - oauth
  - oauth2
  - authorization
  - authentication
  - oidc
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/sec/oauth-2-0-basics/
---

⚡ TL;DR - OAuth 2.0 is an AUTHORIZATION framework (RFC 6749)
- not authentication. It allows a user to grant a third-party
application access to their resources WITHOUT sharing their
credentials.

Think: "Login with Google" on a third-party app. You grant
the app access to your Google profile. You never give your
Google password to the third-party app. Google issues an
access token. The app uses that token to access ONLY
what you authorized.

**Critical distinction:** OAuth 2.0 = authorization (what
can you access). OpenID Connect (OIDC) = authentication
(who are you). OIDC is built on top of OAuth 2.0.

**Grant types:** Authorization Code + PKCE (use this for
everything), Client Credentials (machine-to-machine),
Device Flow (TV/CLI), Implicit (deprecated, vulnerable).

**Common misconfigurations:** wildcard redirect_uri,
token leakage via Referer header, state parameter bypass
(CSRF), open redirect.

---

| #029 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Auth vs AuthZ vs Auditing, TLS, Sessions, JWT | |
| **Used by:** | OAuth 2.0 Deep Dive, OIDC, OAuth RFC 9700, OAuth vs SAML | |
| **Related:** | JWT, OIDC, SAML, Auth Mechanism Migration, Advanced OAuth Attacks | |

---

### 🔥 The Problem This Solves

**THE CREDENTIAL SHARING ANTI-PATTERN:**
Before OAuth: if you wanted a third-party app (e.g., a
calendar client) to access your email to send meeting
invites, you gave it your email password. Problems:
- The app has full account access (not just calendar permission)
- If the app is breached: your password is stolen
- To revoke: you must change your password (affects all apps)
- No audit trail of what the app actually accessed

**WHAT OAUTH 2.0 SOLVES:**
OAuth 2.0 introduces a delegation protocol. The user grants
an app specific permissions (scopes) without sharing credentials.
The app receives an access token that represents those
specific permissions. If the token is compromised: only
those specific permissions are affected, and the token
can be revoked without changing the password. This is
"delegated authorization" - you authorize an app to act
on your behalf, with limited scope, without your credentials.

---

### 📘 Textbook Definition

**OAuth 2.0:** An authorization framework (RFC 6749, 2012)
that enables a third-party application to obtain limited
access to a user's account on an HTTP service, either on
behalf of a user or on the user's own behalf.

**Roles in OAuth 2.0:**

**Resource Owner:** The user who owns the data and can grant
access to it.

**Client:** The third-party application requesting access
to the user's resources.

**Authorization Server:** The server that authenticates
the user and issues access tokens (e.g., Google's OAuth
authorization server at accounts.google.com).

**Resource Server:** The API server holding the user's
data (e.g., Google's Gmail API). Often the same organization
as the authorization server.

**Key Artifacts:**

**Authorization Code:** A short-lived, single-use code
issued by the authorization server after user consent.
The client exchanges it for access tokens. Never exposed
to the browser after the authorization code flow.

**Access Token:** A credential (usually JWT) representing
the authorization. Sent to resource server with each API
call. Short-lived (typically 15 min to 1 hour).

**Refresh Token:** A long-lived credential used to obtain
new access tokens without user interaction. Stored securely
server-side. Rotating refresh tokens (each use invalidates
old token) are security best practice.

**Scope:** Defines the specific permissions requested.
Examples: `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`.
User sees and approves the requested scopes during authorization.

**PKCE (Proof Key for Code Exchange):** An extension
(RFC 7636) that prevents authorization code interception
attacks in public clients (single-page apps, mobile apps)
by binding the authorization request to the token request
using a cryptographic challenge.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OAuth 2.0 = "I authorize this app to do X on my behalf"
without giving the app my password. Authorization server
issues access tokens representing specific permissions.
App uses token to call API.

**One analogy:**
> OAuth is like a hotel key card. You (resource owner)
> check in and tell the front desk (authorization server)
> "issue a key card for room 205 only." The maintenance
> worker (client app) gets a key card (access token) that
> opens room 205 (the specific scope you authorized).
> The maintenance worker never gets your master key
> (password). The hotel can deactivate the key card (revoke
> token) at any time without you needing to change your
> room. The key card expires after a set time. The
> maintenance worker can renew the key card at the desk
> (refresh token flow) without you having to be present.

---

### 🔩 First Principles Explanation

**Authorization Code + PKCE flow (the recommended flow):**

```
AUTHORIZATION CODE + PKCE FLOW:
(Recommended for all clients, especially public clients)

CLIENT SETUP:
  - Client registered with Authorization Server:
    client_id, redirect_uri, allowed scopes
  - Public client (SPA/mobile): no client_secret
    (can't be kept secret in browser/device)

STEP 1: User initiates login
  Client generates:
    code_verifier = random 32-byte string (URL-safe base64)
    code_challenge = BASE64URL(SHA256(code_verifier))
    state = random nonce (CSRF protection)
  
  Client redirects user to authorization endpoint:
  
  GET https://auth.example.com/authorize?
    response_type=code
    &client_id=my-spa
    &redirect_uri=https://myapp.com/callback
    &scope=openid profile email
    &state=abc123xyz          ← CSRF protection
    &code_challenge=SjT5...   ← PKCE challenge
    &code_challenge_method=S256

STEP 2: Authorization Server
  1. Authenticates the user (login form)
  2. Shows consent screen (requested scopes)
  3. User approves → server issues authorization code
  
  Redirects to:
  https://myapp.com/callback?code=AUTH_CODE_HERE&state=abc123xyz

STEP 3: Client validates state
  state from redirect MUST match state sent in step 1.
  If mismatch: CSRF attack. Reject. Do not proceed.

STEP 4: Client exchanges code for tokens
  POST https://auth.example.com/token
  Content-Type: application/x-www-form-urlencoded
  
  grant_type=authorization_code
  &code=AUTH_CODE_HERE
  &redirect_uri=https://myapp.com/callback
  &client_id=my-spa
  &code_verifier=ORIGINAL_VERIFIER    ← PKCE verification
  
  Server verifies: SHA256(code_verifier) == code_challenge
  If match: issues tokens.

STEP 5: Tokens received
  {
    "access_token": "eyJ...",     ← Use for API calls (short-lived)
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "dGhpcyBp...", ← Renew access token
    "id_token": "eyJ..."           ← OIDC: who the user is
  }

STEP 6: API calls
  GET https://api.example.com/profile
  Authorization: Bearer <access_token>

WHY PKCE PROTECTS AGAINST CODE INTERCEPTION:
  Without PKCE: if the authorization code is intercepted
    (URL exposed in browser history, Referer header, malicious
    redirect): attacker calls /token with the code.
  
  With PKCE: attacker has the code but NOT the code_verifier
    (never sent in URL, only sent in POST /token).
    Server verifies SHA256(code_verifier) == code_challenge
    sent in step 1. Attacker can't compute code_verifier
    from the challenge (SHA256 is one-way).
    Code is useless without code_verifier.
```

---

### 🧪 Thought Experiment

**SCENARIO: Evaluating OAuth 2.0 grant type selection**

```
CONTEXT: Building a system with three clients.

CLIENT A: Single-page application (browser)
  - Cannot store secrets (browser code is public)
  - User is present for login
  
  CORRECT: Authorization Code + PKCE
    No client_secret. PKCE prevents code interception.
  
  WRONG: Implicit flow (deprecated, RFC 9700 obsoleted it)
    Returns access token directly in URL fragment.
    Vulnerability: URL fragment in browser history,
    Referer header exposure, malicious script access.
    PKCE solves the same problem without token-in-URL.

CLIENT B: Native mobile app
  - Same as SPA: can't store secrets securely
  - User is present for login
  
  CORRECT: Authorization Code + PKCE
    Uses custom URL scheme or claimed HTTPS for redirect
    (e.g., myapp://callback). PKCE is critical here
    because custom schemes can be registered by malicious apps.

CLIENT C: Backend service calling another backend API
  - No user involved (machine-to-machine)
  - Can store client_secret securely (server-side)
  
  CORRECT: Client Credentials flow
    POST /token {grant_type=client_credentials,
                 client_id=svc-a, client_secret=...}
    Returns access token. No user consent step.
    The client_secret IS the authentication.
    Must be protected like a password.
    Rotate regularly. Use secrets manager, not config files.

CLIENT D: CLI tool or Smart TV
  - User can't easily type in a browser URL
  - Limited input capability
  
  CORRECT: Device Authorization Grant (RFC 8628)
    CLI gets: user_code=ABCD-EFGH, verification_uri=device.example.com
    User types code on phone/computer.
    CLI polls /token until user completes authorization.

WRONG FOR ALL: Storing tokens in localStorage
  XSS can read localStorage. Access tokens there = token theft.
  Memory (for access tokens) + HttpOnly cookie (for refresh)
  is the correct storage pattern.
```

---

### 🧠 Mental Model / Analogy

> OAuth 2.0 is the power of attorney model applied to APIs.
> When you grant someone power of attorney, you don't give
> them your identity (they're still them). You grant them
> authority to act on your behalf in specific, defined ways
> (scopes). The authorization server (notary/registry) validates
> the grant. The attorney (client app) presents the grant
> document (access token) when acting on your behalf.
> The agent (resource server) accepts the document if it's
> valid. You can revoke the grant at any time. The attorney
> can't grant the same authority to someone else (token
> binding). This is delegation without identity transfer
> - the security property OAuth 2.0 was specifically designed
> to provide.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OAuth 2.0 is the protocol behind "Login with Google" on
third-party websites. Instead of giving the website your
Google password, Google confirms your identity and issues
a temporary permission card. The website uses this card
to access specific parts of your Google account (like
your email address for account creation). If you later
change your Google password: the card is unchanged. If
you revoke the website's access in Google settings: the
card stops working.

**Level 2 - How to use it (junior developer):**
Most apps use Authorization Code + PKCE. Step 1: redirect
to authorization server. Step 2: user logs in and approves
scopes. Step 3: authorization code arrives at your redirect_uri.
Step 4: POST to /token endpoint, exchange code for access
token (+ refresh token). Step 5: use access token in
Authorization header. When access token expires: use refresh
token to get a new one. Use a library: most frameworks
have OAuth 2.0 clients. Don't implement the protocol manually.

**Level 3 - How it works (mid-level engineer):**
Security controls required around Authorization Code + PKCE:
(1) state parameter: random nonce, verified on callback,
prevents CSRF. (2) PKCE: code_verifier generated client-side,
code_challenge sent in authorization request, code_verifier
sent in token request - server verifies SHA256 match.
(3) Exact redirect_uri matching: authorization server must
validate redirect_uri exactly against registered URIs.
Wildcard or partial matching enables open redirect attacks.
(4) Short-lived authorization codes: 10-minute max.
Single-use (exchange once, then invalidated).

**Level 4 - Why it was designed this way (senior/staff):**
OAuth 2.0 (RFC 6749, 2012) deliberately chose to be an
authorization FRAMEWORK rather than a protocol. This
flexibility enabled adoption across diverse use cases
(mobile, web, server, device, IoT) but created the "OAuth
proliferation" problem: many interoperable but incompatible
implementations. OAuth 2.1 (currently in draft) consolidates
the security improvements: requires PKCE for all flows,
deprecates implicit flow, requires refresh token rotation.
OIDC (OpenID Connect) addresses the authentication layer
that OAuth 2.0 deliberately omitted - it defines the
id_token (JWT containing user identity claims), the userinfo
endpoint, and the discovery document (/.well-known/openid-configuration).

**Level 5 - Mastery (distinguished engineer):**
Advanced OAuth deployments use DPoP (Demonstrating Proof
of Possession, RFC 9449) to bind tokens to the client's
key pair. A DPoP-bound access token can only be used by
the client that holds the corresponding private key.
Even if the token is stolen from an HTTPS proxy or log,
the attacker cannot use it without the private key. This
addresses the fundamental weakness of bearer tokens (whoever
holds the token can use it). OAuth 2.0 Rich Authorization
Requests (RAR, RFC 9396) allow fine-grained authorization
details beyond simple scopes: "authorize read access to
files in folder /documents only." Pushed Authorization
Requests (PAR, RFC 9126) move the authorization request
parameters from URL to a POST request to the auth server,
preventing parameter tampering via URL manipulation.

---

### ⚙️ How It Works (Mechanism)

**Authorization server token issuance and validation:**

```
AUTHORIZATION SERVER CORE COMPONENTS:

  Authorization Endpoint (/authorize):
    - Authenticates user (login)
    - Shows consent screen
    - Issues authorization code
    - Validates: client_id, redirect_uri, scope, state

  Token Endpoint (/token):
    - Validates: authorization code, PKCE code_verifier
    - Validates: client authentication (for confidential clients)
    - Issues: access_token, refresh_token, id_token (OIDC)
    - Returns: JSON response with tokens

  JWKS Endpoint (/.well-known/jwks.json):
    - Public keys for verifying JWTs
    - Resource servers fetch these to validate access tokens

  Introspection Endpoint (/introspect):
    - Resource server can ask: is this token active?
    - Server returns: active, scope, sub, exp, etc.
    - Alternative to local JWT validation

  Revocation Endpoint (/revoke):
    - Client revokes access or refresh token (RFC 7009)
    - Use on logout: revoke refresh token

DISCOVERY DOCUMENT (/.well-known/openid-configuration):
  JSON document listing all endpoints and capabilities.
  Libraries auto-configure from this URL.
  {
    "issuer": "https://auth.example.com",
    "authorization_endpoint": "https://auth.example.com/authorize",
    "token_endpoint": "https://auth.example.com/token",
    "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
    "scopes_supported": ["openid", "profile", "email"],
    ...
  }
```

---

### 💻 Code Example

**Authorization Code + PKCE implementation (Python FastAPI):**

```python
# OAuth 2.0 Authorization Code + PKCE - Server-side
# Client implementation for SPA or native app integration

import secrets
import hashlib
import base64
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()

# OAuth configuration - loaded from environment
AUTH_SERVER = "https://auth.example.com"
CLIENT_ID = "my-app"
CLIENT_SECRET = "secret"  # Only for confidential clients
REDIRECT_URI = "https://myapp.example.com/callback"
SCOPES = "openid profile email"

# State and PKCE storage (use Redis/session in production)
_pending_flows: dict = {}

@app.get("/login")
async def login():
    """Initiate Authorization Code + PKCE flow."""
    # Generate PKCE code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).rstrip(b"=").decode()
    
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store for callback verification
    # In production: store in server-side session (Redis)
    _pending_flows[state] = {
        "code_verifier": code_verifier
    }
    
    # Build authorization URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    auth_url = f"{AUTH_SERVER}/authorize?{query_string}"
    
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(code: str, state: str, error: str = None):
    """Handle authorization server callback."""
    if error:
        raise HTTPException(400, f"Auth server error: {error}")
    
    # CRITICAL: Verify state parameter (CSRF protection)
    if state not in _pending_flows:
        raise HTTPException(400, "Invalid state: CSRF detected")
    
    flow = _pending_flows.pop(state)  # Single use
    code_verifier = flow["code_verifier"]
    
    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVER}/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                # For confidential clients:
                "client_secret": CLIENT_SECRET,
                # PKCE verification:
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code != 200:
            raise HTTPException(400, "Token exchange failed")
        
        tokens = response.json()
    
    # tokens["access_token"]: use for API calls
    # tokens["refresh_token"]: store in HttpOnly cookie
    # tokens["id_token"]: decode for user identity (OIDC)
    
    # Set refresh token in HttpOnly cookie
    resp = RedirectResponse(url="/dashboard")
    resp.set_cookie(
        "refresh_token",
        tokens.get("refresh_token", ""),
        httponly=True,   # No JavaScript access
        secure=True,     # HTTPS only
        samesite="lax",  # CSRF protection
        max_age=7 * 24 * 3600  # 7 days
    )
    return resp

# BAD: Implicit flow (deprecated)
# Returns access_token directly in URL fragment:
# redirect_uri=#access_token=... (visible in browser history)
# Never implement this for new systems.
```

---

### ⚖️ Comparison Table

| Flow | Use Case | Client Type | State of Practice |
|:---|:---|:---|:---|
| **Auth Code + PKCE** | Web apps, SPA, mobile, CLI | Public and confidential | Recommended for all |
| **Client Credentials** | Machine-to-machine | Confidential only | Recommended for M2M |
| **Device Authorization** | TV, CLI, limited input | Public | Recommended for device |
| **Implicit** | SPA (historical) | Public | DEPRECATED. Don't use. |
| **Password Grant** | Legacy migration only | Confidential | DEPRECATED. Don't use. |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| OAuth 2.0 is an authentication protocol | OAuth 2.0 is purely an authorization framework. It answers "can this app access this resource?" not "who is this user?" The id_token and user identity in "Login with Google" flows come from OpenID Connect (OIDC), which is built on top of OAuth 2.0. Using an OAuth 2.0 access token as proof of identity (without OIDC) is incorrect and can be exploited. Apps receiving an access token should use the /userinfo endpoint (OIDC) or validate the id_token to establish user identity. |
| "Login with Google" is OAuth 2.0 | "Login with Google" is OpenID Connect (OIDC), which uses OAuth 2.0 as its authorization layer. OIDC adds the id_token (JWT containing user identity: sub, email, name), the /userinfo endpoint (fetch user claims with access token), and the discovery document (/.well-known/openid-configuration). OAuth 2.0 alone cannot tell you who the user is. OIDC adds the identity layer that makes it suitable for authentication. |

---

### 🚨 Failure Modes & Diagnosis

**OAuth 2.0 misconfigurations that lead to security incidents:**

```
MISCONFIGURATION 1: Wildcard or partial redirect_uri matching
  Registration: https://myapp.com/*
  Attack: attacker registers https://myapp.com.evil.com
    or sends redirect_uri=https://myapp.com.evil.com
  If server does prefix matching: authorization code
    delivered to attacker's domain.
  
  Fix: exact matching only. register the EXACT URIs.
    No wildcards in production redirect URIs.

MISCONFIGURATION 2: Missing state parameter
  Without state: attacker can forge a callback:
    GET /callback?code=LEGIT_CODE&state=
    If state not validated: attacker's code accepted.
  This is a CSRF on the OAuth callback.
  
  Fix: always generate and verify state.
    State must match between authorization request
    and callback. Reject if missing or mismatched.

MISCONFIGURATION 3: Authorization code reuse
  OAuth spec: authorization codes must be single-use.
  If the same code can be used twice: code replay attack.
  
  Diagnosis: POST /token with same code twice.
    Second call should return error (invalid_grant).
    If second call succeeds: code reuse vulnerability.

MISCONFIGURATION 4: Tokens in URLs
  Access token in URL query string:
    https://app.com/dashboard?access_token=...
  Vulnerability: URL in browser history, server logs,
    Referer header sent to other servers.
  
  Fix: access tokens ONLY in Authorization header.
    Never in URLs. Return from /token endpoint only.

MISCONFIGURATION 5: Long-lived access tokens, no refresh
  Access tokens valid for 24 hours: if stolen, 24-hour
  window for attacker. No refresh token means user must
  re-login every hour (poor UX with short tokens).
  
  Fix: short access tokens (15 min) + refresh tokens.
    Refresh tokens: long-lived, server-side revocable,
    stored in HttpOnly cookie.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication vs Authorization vs Auditing`
- `JWT (JSON Web Tokens)`
- `TLS, HTTPS`

**Builds on this:**
- `OAuth 2.0 Deep Dive` - all grant types, security details
- `OpenID Connect (OIDC)` - identity layer on OAuth 2.0
- `OAuth RFC 9700` - latest security best practices
- `OAuth vs SAML Decision` - when to choose each

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OAUTH 2.0    │ Authorization framework (NOT authn)       │
│              │ Grants limited access without credentials │
├──────────────┼───────────────────────────────────────────┤
│ BEST FLOW    │ Authorization Code + PKCE for all apps    │
│              │ Client Credentials for M2M                │
├──────────────┼───────────────────────────────────────────┤
│ ROLES        │ Resource Owner (user)                     │
│              │ Client (3rd party app)                    │
│              │ Auth Server (Google, Okta, Auth0)         │
│              │ Resource Server (API)                     │
├──────────────┼───────────────────────────────────────────┤
│ TOKENS       │ Access token: short-lived, for API calls  │
│              │ Refresh token: long-lived, revocable      │
│              │ Auth code: single-use, 10 min max         │
├──────────────┼───────────────────────────────────────────┤
│ SECURITY     │ Exact redirect_uri match (no wildcards)   │
│              │ State parameter (CSRF protection)         │
│              │ PKCE (code interception protection)       │
├──────────────┼───────────────────────────────────────────┤
│ DEPRECATED   │ Implicit flow (don't use)                 │
│              │ Password Grant (don't use)                │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Least privilege in delegation: grant only the minimum
scope, for the minimum time, to the specific resource."
OAuth 2.0's scope mechanism is least privilege applied
to API authorization. The principle generalizes: whenever
you delegate access (service accounts, IAM roles, API
keys, OAuth tokens), scope to exactly what's needed for
exactly what duration. Over-scoped tokens are the primary
reason token compromise has high blast radius. Under-scoped
tokens: even a compromised token cannot access more than
it was authorized for. Design authorization grants to
be as narrow as the use case requires, not as broad as
the system allows.

---

### 💡 The Surprising Truth

OAuth 2.0 was designed by committee and the result shows
it. The "authorization framework" label hides significant
fragmentation: the grant types are not interchangeable,
the security properties vary dramatically by flow, and
the spec deliberately omitted authentication (needing OIDC
as a separate spec). The implicit flow (now deprecated)
was considered "reasonable" in 2012 for browser apps
and is now known to be fundamentally flawed. Every major
version of OAuth has required security best current practice
(BCP) updates to paper over the gaps: RFC 6819 (OAuth
threat model, 2013), RFC 8252 (native apps, 2017), RFC
8628 (device flow, 2019), RFC 9700 (current OAuth 2.0
BCP, 2024). The lesson: security protocols age poorly,
and the original spec is rarely sufficient. Always implement
current security best practices, not just the base RFC.
RFC 9700 is the current authoritative reference for
OAuth 2.0 security practices.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the Authorization Code + PKCE flow step by
   step, including what state and code_verifier protect against.
2. **CHOOSE** the correct grant type for a given scenario:
   SPA, mobile app, server-to-server, CLI, TV.
3. **IDENTIFY** common OAuth misconfigurations: wildcard
   redirect_uri, missing state, tokens in URLs.
4. **DISTINGUISH** OAuth 2.0 (authorization) from OIDC
   (adds identity/authentication on top of OAuth 2.0).

---

### 🎯 Interview Deep-Dive

**Q: Explain how OAuth 2.0 Authorization Code flow works
and what security issues you need to address.**

*Why they ask:* OAuth is ubiquitous. Misimplementing it
leads to authorization bypasses and token theft.

*Strong answer includes:*
- Complete flow: redirect to /authorize → user authenticates →
  consent → authorization code in redirect → exchange code
  for token at /token → use access token for API calls.
- PKCE is required: code_verifier/code_challenge pair prevents
  interception of the authorization code. Without PKCE: code
  in URL could be stolen and exchanged for tokens by attacker.
  PKCE means the code is useless without the code_verifier
  that was never sent in a URL.
- State parameter: random nonce. Verified on callback. Prevents
  CSRF where attacker forces user to complete an auth flow
  they didn't initiate.
- Redirect URI: must be registered exactly. No wildcards.
  Mismatched URI = auth code delivered to attacker.
- Token storage: access token in memory (short-lived, ~15 min).
  Refresh token in HttpOnly Secure cookie.
  Never localStorage for access tokens (XSS readable).
- Distinguish from OIDC: OAuth is authorization only.
  For user identity: must use OIDC id_token or /userinfo.
  Using access token as identity proof is incorrect.
- Implicit flow: deprecated for good reason. Don't use.
  PKCE solves the same browser-client problem without returning
  tokens in URL fragments.