---
id: SEC-057
title: "OAuth 2.0 Deep Dive"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-010, SEC-016, SEC-028, SEC-045, SEC-056
used_by: SEC-058, SEC-071, SEC-078, SEC-087, SEC-088
related: SEC-010, SEC-016, SEC-028, SEC-045, SEC-056, SEC-058, SEC-071
tags:
  - security
  - oauth
  - oauth2
  - pkce
  - authorization-code
  - access-token
  - refresh-token
  - openid-connect
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/sec/oauth-2-deep-dive/
---

⚡ TL;DR - OAuth 2.0 delegates authorization (not authentication)
to a trusted authorization server. The authorization code + PKCE
flow is the current standard for both web and mobile apps.
The state parameter prevents CSRF. The `redirect_uri` must
be exact-matched. Implicit flow is deprecated (RFC 9700).

**OAuth 2.0 in one diagram:**
```
User → [Client App] → Auth Server → "Allow access?" → User
                                         ↓ yes
                    code → Client App → token endpoint → access_token
                                         ↓
                           Client calls API with Bearer token
```

---

| #057 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Fundamentals, Input Validation, JWT, Authentication Decision Tree, JWT Anti-Patterns | |
| **Used by:** | OpenID Connect (OIDC), OAuth Implicit Flow Deprecation, Advanced JWT Attacks, OAuth vs SAML Decision | |
| **Related:** | OIDC, JWT, Session Management, API Security | |

---

### 🔥 The Problem This Solves

**WHY OAUTH EXISTS:**

```
BEFORE OAUTH (delegated credential sharing):

  You use a third-party app (App B) that needs to read your
  emails from Gmail.
  
  Old approach:
    App B: "Give me your Gmail username and password."
    You: (type Gmail credentials into App B)
    App B: logs in as you, reads your emails.
  
  PROBLEMS:
    1. App B has your full Gmail credentials.
    2. App B can do ANYTHING in your Gmail account (delete, send as you).
    3. App B could be compromised → your Gmail password is stolen.
    4. To revoke App B's access: change your Gmail password.
       (Also revokes every other app that knows your password.)
    5. Google can't tell if you're logging in or App B is.

AFTER OAUTH:

  You use App B, it needs to read your emails.
  
  OAuth approach:
    App B: "I need read access to your emails. Redirecting to Google."
    Google: "App B wants to read your emails. Allow?" [Yes] [No]
    You: [Yes]
    Google: Gives App B an access_token with scope=gmail.readonly
    App B: Calls Gmail API with access_token.
  
  BENEFITS:
    1. App B NEVER gets your Gmail password.
    2. App B can only READ emails (not delete, not send).
    3. Revoke App B: Google revokes access_token.
       Your password unchanged. Other apps unaffected.
    4. Google can see which apps you've authorized.
    5. Access_token expires (15 minutes). Refresh requires consent.

OAUTH 2.0 ROLES:
  Resource Owner: The user who owns the data.
  Client: The app that wants access (App B).
  Authorization Server: The auth provider (Google, GitHub).
  Resource Server: The API that holds the data (Gmail API).
```

---

### 📘 Textbook Definition

**OAuth 2.0:** An authorization framework (RFC 6749) that enables
limited access to user accounts on an HTTP service. Key distinction:
OAuth 2.0 is for AUTHORIZATION (access delegation), not
AUTHENTICATION (identity verification). OpenID Connect (OIDC)
adds authentication on top of OAuth 2.0.

**Grant Types (flows):**
- **Authorization Code + PKCE:** For web apps and mobile apps.
  Current recommended flow.
- **Client Credentials:** For service-to-service (no user involved).
- **Device Authorization:** For devices with limited input (smart TVs).
- **Implicit Flow:** DEPRECATED (RFC 9700, 2023).
- **Resource Owner Password Credentials (ROPC):** Deprecated for most uses.

**Key components:**
- **Access Token:** Short-lived credential to call the API.
  Format: opaque (random string) or JWT.
- **Refresh Token:** Long-lived credential to get new access tokens.
  Store in HttpOnly cookie or secure storage.
- **Scope:** What the access token permits (`email`, `gmail.readonly`).
- **State:** Random nonce for CSRF protection.
- **Code Verifier / Code Challenge (PKCE):** Proof Key for Code Exchange.
  Prevents authorization code interception.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OAuth 2.0 = your app asks a trusted service (Google, GitHub)
"please let this app access this specific data on my behalf."
The user approves on the trusted service's site. Your app
gets a time-limited token to make API calls. Your app
never sees the user's password.

**One analogy:**
> OAuth is like a valet parking service.
> 
> Old approach (credential sharing): "Here are my car keys.
> You can drive it anywhere." The valet has full access.
> 
> OAuth approach: "Here is a valet key." A valet key only
> unlocks the ignition and driver door. It doesn't open
> the glove box or trunk. It might expire after 4 hours.
> The car manufacturer limits what the valet can do.
> 
> You didn't give the valet your master key.
> The valet can only perform the specific actions you authorized.
> The car manufacturer (authorization server) issued the
> valet key and controls its permissions.

---

### 🔩 First Principles Explanation

**Authorization Code + PKCE flow - step by step:**

```
AUTHORIZATION CODE + PKCE (current standard):

STEP 0: Client generates PKCE values
  code_verifier = random_string(32 bytes, URL-safe)
  code_challenge = BASE64URL(SHA256(code_verifier))
  code_challenge_method = "S256"
  
  State (CSRF protection):
  state = random_string(16 bytes)
  Store code_verifier and state in session (server-side or encrypted cookie)

STEP 1: Authorization Request (Client → Browser → Auth Server)

  GET https://auth.example.com/authorize?
    response_type=code
    &client_id=my_client_id
    &redirect_uri=https://myapp.com/callback         ← EXACT MATCH required
    &scope=openid%20email%20profile
    &state=<random_state>                            ← CSRF protection
    &code_challenge=<sha256_of_verifier>             ← PKCE
    &code_challenge_method=S256
  
  Auth server shows login page and consent screen.
  User authenticates and approves.

STEP 2: Authorization Response (Auth Server → Browser → Client)

  GET https://myapp.com/callback?
    code=<authorization_code>                        ← One-time, short-lived
    &state=<same_state>
  
  CLIENT VALIDATION:
    1. Verify state matches what was stored in step 0.
       (If not: CSRF attack → reject)
    2. Code is a one-time-use, short-lived (10 min) authorization code.
       It's NOT an access token.

STEP 3: Token Exchange (Client → Auth Server, server-to-server)

  POST https://auth.example.com/token
  Content-Type: application/x-www-form-urlencoded
  
  grant_type=authorization_code
  &code=<authorization_code>
  &redirect_uri=https://myapp.com/callback           ← Must match step 1
  &client_id=my_client_id
  &client_secret=my_client_secret                    ← Server-side only!
  &code_verifier=<original_verifier>                 ← PKCE verification
  
  Auth server:
    1. Verify code is valid and not expired.
    2. Verify code_verifier: SHA256(code_verifier) == code_challenge (from step 1)
    3. Verify redirect_uri matches exactly.
    4. Verify client_id and client_secret.
    5. Issue access_token (short-lived) and refresh_token (long-lived).

STEP 4: Access Token Response

  {
    "access_token": "eyJhbGc...",    # JWT or opaque
    "token_type": "Bearer",
    "expires_in": 900,               # 15 minutes
    "refresh_token": "7fd...",       # Long-lived, store securely
    "scope": "openid email profile"
  }

STEP 5: API Call

  GET https://api.example.com/userinfo
  Authorization: Bearer <access_token>
  
  API verifies access_token signature (if JWT) or calls introspection endpoint.
  Returns data matching the granted scope.

STEP 6: Token Refresh (when access_token expires)

  POST https://auth.example.com/token
  grant_type=refresh_token
  &refresh_token=<refresh_token>
  &client_id=my_client_id
  &client_secret=my_client_secret
  
  Returns new access_token (and optionally new refresh_token).
  Refresh token rotation: issue new refresh_token and invalidate old one.

WHY PKCE:
  Without PKCE: if an attacker intercepts the authorization code
  (via malicious app registered with the same redirect_uri on mobile,
  or via browser history), they can exchange it for an access_token.
  
  With PKCE: the code exchange requires code_verifier.
  The attacker has the code but not the code_verifier (it was only
  in the client's memory during the flow). Exchange fails.
  
  PKCE was originally for mobile apps (no client_secret possible).
  Now recommended for ALL apps (including web apps with client_secret).
  Provides defense-in-depth: even if client_secret is compromised,
  code interception still requires code_verifier.
```

---

### 🧪 Thought Experiment

**SCENARIO: redirect_uri validation vulnerability**

```
AUTHORIZATION SERVER: Allows redirect_uri if it's a prefix of registered URI.

  Registered: https://client.example.com/oauth/callback
  
  Attack:
    Attacker registers: https://attacker.com/steal
    Builds link: 
      https://auth.example.com/authorize?
        client_id=legitimate_client
        &redirect_uri=https://client.example.com/oauth/callback/../../../openredirect?next=https://attacker.com/steal
        &response_type=code
    
    Auth server: 
      Does redirect_uri start with https://client.example.com/oauth/callback? 
      YES (it starts with the registered URI prefix).
    
    After user consents:
      Authorization code sent to: https://client.example.com/oauth/callback/../../../openredirect?next=https://attacker.com/steal
    
    Client app has an open redirect at /openredirect.
    Redirects user (and the code!) to https://attacker.com/steal?code=<auth_code>
    
    Attacker exchanges code for access_token.
    Account takeover.

CORRECT VALIDATION:
  redirect_uri must be EXACT MATCH (not prefix, not regex, not substring).
  
  Registered: https://client.example.com/oauth/callback
  Submitted: anything different → REJECT (400 Bad Request).
  
  Also: redirect_uri must be HTTPS (except localhost for development).
  Localhost exception: allow http://127.0.0.1:PORT for local dev only.
  
  RFC 6749 Section 10.6: "The authorization server MUST require
  the use of TLS when sending responses to the redirection endpoint
  in cases where the requested response data is sensitive."

ALSO: CLIENT CREDENTIALS (no user involved):

  For service-to-service API calls:
    POST /token
    grant_type=client_credentials
    &client_id=service_a_id
    &client_secret=service_a_secret
    &scope=api.read
  
  No user consent. No redirect_uri. Client authenticates with
  its own credentials (not on behalf of a user).
  Access token has no sub claim (or sub = client_id).
  
  Use case: microservice A calls microservice B (no user context).
  Background job calling an API.
```

---

### 🧠 Mental Model / Analogy

> OAuth 2.0 is like a hotel key card system.
>
> Old approach (master key sharing): hotel gives you the master key.
> You give the master key to room service, housekeeping, and bellhop.
> Anyone with the master key can access any room at any time.
>
> OAuth approach:
> Authorization server = hotel front desk
> Access token = room key card (only opens room 324, expires in 24h)
> Scope = permissions on the key (room 324 only, no minibar)
> Client = the person/service holding the key card
>
> You (Resource Owner) asked the front desk (Auth Server)
> to create a limited key card (access token with scope)
> for the bellhop (Client).
> You never gave the bellhop your master key or room combination.
> The key expires. The front desk can deactivate it.
> The bellhop can only do what the key permits.
>
> PKCE = the key card also has a PIN (code_verifier).
> Even if someone steals the key card (authorization code),
> they can't use it without the PIN.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
OAuth 2.0 lets you give an app limited access to your account on another service (like GitHub) without giving it your password. You see GitHub's "Allow access?" screen. If you say yes, the app gets a temporary token to do only what you approved. You can revoke it from GitHub settings without changing your password.

**Level 2 - How to use it (junior developer):**
Use an OAuth library (authlib, passport.js) - don't build the flow manually. Generate state before redirecting to auth server. Verify state matches on callback (CSRF check). Exchange code for tokens at the token endpoint (server-side - never in the browser). Use PKCE always (authorization code + PKCE). Store refresh token in HttpOnly cookie. Access token in memory (not localStorage). Refresh when expired.

**Level 3 - How it works (mid-level engineer):**
The authorization code flow separates concerns: (1) user-facing consent (via browser redirect, public channel), (2) token exchange (server-to-server, private channel with client_secret). The code is short-lived (10 min) and single-use; even if intercepted in the browser redirect, it's useless without client_secret + code_verifier. PKCE adds a second layer: even if client_secret is compromised, code interception still fails without the code_verifier. The state parameter serves the same role as a CSRF token: verifies the callback is a response to a request the client initiated (not a CSRF-injected callback).

**Level 4 - Why it was designed this way (senior/staff):**
OAuth 2.0 (RFC 6749) deliberately separated the authorization endpoint (user-facing) from the token endpoint (server-to-server). This separation is why the implicit flow (skipping the server-side exchange) is insecure: tokens returned in URL fragments are visible to the browser, JavaScript, browser extensions, and any scripts loaded on the redirect page. RFC 9700 (2023) formally deprecates implicit flow. PKCE (RFC 7636) was originally designed for mobile apps that cannot have client_secret (a secret embedded in an app binary is not a secret). But the same code interception risk exists on any platform, so PKCE was extended to web apps in RFC 9700. Client credentials flow has no user involvement, so redirect_uri is not applicable.

**Level 5 - Mastery (distinguished engineer):**
Advanced OAuth security considerations: token introspection (RFC 7662) vs JWT verification - introspection calls the auth server to validate an opaque token (always fresh but adds latency); JWT verification is local but the token is only as fresh as its expiry. At scale: JWKS endpoint caching with rotation (the auth server publishes public keys; clients cache them with TTL; key rotation requires cache invalidation - use `kid` to identify which key to use). OAuth security model assumes the authorization server is trusted - if the auth server is compromised, all clients are compromised. RFC 9700 ("OAuth 2.0 Security Best Current Practice") is the comprehensive modern guide, superseding RFC 6749's security section.

---

### ⚙️ How It Works (Mechanism)

**Token endpoint authentication methods:**

```
CLIENT AUTHENTICATION METHODS (at token endpoint):

1. client_secret_post (simplest, less secure):
   POST /token
   grant_type=authorization_code
   &client_id=my_client
   &client_secret=my_secret       ← In request body
   &code=...

2. client_secret_basic (HTTP Basic Auth):
   POST /token
   Authorization: Basic base64(client_id:client_secret)
   
   grant_type=authorization_code&code=...

3. client_secret_jwt (signed JWT - more secure):
   POST /token
   grant_type=authorization_code
   &client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
   &client_assertion=<JWT signed with client secret>
   
   JWT contains: iss=client_id, sub=client_id, aud=token_endpoint, exp, jti
   One-time use JWT prevents replay attacks.

4. private_key_jwt (most secure, mutual TLS alternative):
   Client has RSA private key. Public key registered with auth server.
   Signs JWT with private key.
   Proof of possession: private key never leaves the client.

5. PKCE (for public clients - mobile, SPAs):
   No client_secret (can't be kept secret in mobile app or browser).
   PKCE provides code exchange security without a client_secret.

FLOW SELECTION GUIDE:
  Browser SPA:
    Authorization Code + PKCE
    No client_secret (it would be in browser JS - not secret)
    Access token in memory (not localStorage)
    Refresh token in HttpOnly cookie
  
  Server-side web app:
    Authorization Code + PKCE + client_secret
    Both PKCE and client_secret (defense in depth)
    Tokens stored server-side, session cookie to browser
  
  Mobile app:
    Authorization Code + PKCE
    No client_secret (can be extracted from APK)
    Use iOS Keychain / Android Keystore for refresh token
  
  Service-to-service (no user):
    Client Credentials
    client_id + client_secret OR private_key_jwt
    No user consent, no redirect_uri
  
  Smart TV / limited input device:
    Device Authorization Grant (RFC 8628)
    Device shows a short code, user enters on phone/computer
    Device polls token endpoint until user authorizes
```

---

### 💻 Code Example

**Python: authorization code + PKCE flow (server-side):**

```python
# OAuth 2.0 Authorization Code + PKCE - Flask implementation

import secrets, hashlib, base64
from flask import Flask, redirect, request, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
oauth = OAuth(app)

oauth.register(
    name='github',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

def generate_pkce_pair():
    """Generate code_verifier and code_challenge for PKCE."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

@app.route('/login')
def login():
    # Generate CSRF state
    state = secrets.token_urlsafe(16)
    
    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Store in server-side session (never in URL)
    session['oauth_state'] = state
    session['code_verifier'] = code_verifier
    
    # Build authorization URL
    return oauth.github.authorize_redirect(
        redirect_uri='https://myapp.com/auth/callback',
        state=state,
        code_challenge=code_challenge,
        code_challenge_method='S256',
    )

@app.route('/auth/callback')
def auth_callback():
    # Step 1: Verify state (CSRF check)
    returned_state = request.args.get('state')
    expected_state = session.pop('oauth_state', None)
    
    if not returned_state or returned_state != expected_state:
        return "CSRF token mismatch", 400  # Possible CSRF attack
    
    # Step 2: Get code_verifier from session
    code_verifier = session.pop('code_verifier', None)
    
    # Step 3: Exchange code for token (server-to-server)
    code = request.args.get('code')
    if not code:
        return "Missing authorization code", 400
    
    # Authlib handles the token exchange with PKCE
    token = oauth.github.fetch_access_token(
        redirect_uri='https://myapp.com/auth/callback',
        code=code,
        code_verifier=code_verifier,
    )
    
    # Step 4: Use access token to get user info
    resp = oauth.github.get('user')
    user_info = resp.json()
    
    # Store user session (not the token itself in the cookie)
    # Create server-side session record
    session['user_id'] = user_info['id']
    session['username'] = user_info['login']
    
    return redirect('/dashboard')
```

---

### ⚖️ Comparison Table

| Flow | User Involved | client_secret | Where Token Appears | Status |
|:---|:---|:---|:---|:---|
| **Auth Code + PKCE** | Yes | Optional (web) / No (mobile) | Server-side | Current standard |
| **Client Credentials** | No | Yes | Server-side | Current standard |
| **Device Authorization** | Yes (on separate device) | Optional | Server-side | Current |
| **Implicit** | Yes | No | URL fragment (browser) | DEPRECATED (RFC 9700) |
| **ROPC (password)** | Yes (gives password to client) | Optional | Server-side | Deprecated for most uses |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| OAuth 2.0 is an authentication protocol. | OAuth 2.0 is an authorization framework. It answers "can this app access this resource?" not "who is this user?" An access token proves the user authorized the client to access specific scopes - it does not directly identify the user. OpenID Connect (OIDC) is the authentication layer built on top of OAuth 2.0, adding an ID token that contains user identity claims (`sub`, `email`, `name`). If you're implementing "login with Google," you're using OIDC (not pure OAuth 2.0). Many developers conflate OAuth and OIDC because they're used together, but they solve different problems. |
| The access token can be stored in localStorage for convenience since it expires in 15 minutes. | Short expiry reduces risk but doesn't eliminate XSS token theft. An XSS payload can immediately exfiltrate the current access token and refresh token. If the access token is in localStorage and an attacker has XSS, they steal it within milliseconds of it being stored. 15-minute expiry helps only if: (a) the XSS doesn't run immediately or (b) you detect and fix the XSS within 15 minutes. Neither is reliable. Store access tokens in HttpOnly cookies (for SSR/BFF pattern) or in memory (JavaScript variables, not localStorage) for SPAs. In-memory tokens are lost on page refresh - use the refresh token pattern with HttpOnly cookie to restore them. |

---

### 🚨 Failure Modes & Diagnosis

**Common OAuth implementation errors:**

```
DIAGNOSIS CHECKLIST FOR OAUTH IMPLEMENTATIONS:

1. State parameter
   Test: Remove state from authorization request. What happens?
   Safe: Auth server rejects the request OR client rejects
         the callback with no state.
   Vulnerable: OAuth flow completes without state validation.
   Risk: CSRF against OAuth → attacker's account linked to victim.

2. redirect_uri validation
   Test: Add extra path to registered redirect_uri:
     registered: https://app.com/callback
     submitted:  https://app.com/callback/../../evil
   Safe: Auth server rejects (must be exact match).
   Vulnerable: Auth server accepts and sends code to malicious URL.

3. Authorization code single-use
   Test: Capture authorization code. Use it to get a token.
         Then submit the SAME code again.
   Safe: Token endpoint returns error (invalid_grant).
   Vulnerable: Second exchange succeeds → code replay attack.

4. Token endpoint: client auth
   Test: Submit request without client_secret.
   Safe: Token endpoint returns 401.
   Vulnerable: Tokens issued without client authentication.

5. Scope validation
   Test: Request scope higher than registered.
     Client registered with scope=email
     Request with scope=admin
   Safe: Auth server issues token with scope=email only.
   Vulnerable: Token with scope=admin issued → privilege escalation.

6. Access token validation (at resource server)
   Test: Forge a token (change sub, change roles) - modify JWT payload.
   Safe: Signature verification fails.
   Vulnerable: Resource server doesn't verify signature.
   
   Also test: submit expired token.
   Safe: 401 Unauthorized.
   Vulnerable: Request succeeds.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Fundamentals` - authentication and authorization
- `JSON Web Tokens (JWT)` - JWT format for access tokens
- `JWT Security Anti-Patterns` - JWT verification pitfalls
- `Authentication Method Decision Tree` - when to use OAuth

**Builds on this:**
- `OpenID Connect (OIDC)` - identity layer on OAuth 2.0
- `OAuth Implicit Flow Deprecation` - RFC 9700 rationale
- `OAuth vs SAML Decision` - when to choose each

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WEB/MOBILE   │ Authorization Code + PKCE                 │
│ SERVICE-SVC  │ Client Credentials                        │
│ TV/DEVICE    │ Device Authorization Grant                │
├──────────────┼───────────────────────────────────────────┤
│ STATE        │ Random nonce, verify on callback (CSRF)   │
│ redirect_uri │ Exact match only (no prefix/wildcard)     │
│ PKCE         │ code_verifier + SHA256 challenge          │
├──────────────┼───────────────────────────────────────────┤
│ DEPRECATED   │ Implicit flow (RFC 9700)                  │
│              │ ROPC (for third-party apps)               │
├──────────────┼───────────────────────────────────────────┤
│ ACCESS TOKEN │ 15 min expiry; HttpOnly cookie or memory  │
│ REFRESH      │ 7 days; HttpOnly Secure SameSite cookie   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Delegate security responsibilities to a dedicated service
rather than implementing them everywhere."
OAuth 2.0's authorization server centralizes: user authentication,
consent management, token issuance, key management, audit logging,
rate limiting, and access revocation. Without OAuth: every service
implements its own credential handling (inevitable inconsistency).
With OAuth: one trusted authority for all authorization decisions.
This principle generalizes to other security domains:
certificate management (Let's Encrypt, AWS ACM): centralized
instead of per-service self-signed certs;
secrets management (Vault, AWS Secrets Manager): centralized
instead of per-app secrets files;
identity management (LDAP, Okta): centralized instead of
per-app user databases.
Centralize security-sensitive components. Delegate to experts.
The auth server handles all the hard security problems so
your service only needs to validate tokens.

---

### 💡 The Surprising Truth

OAuth 2.0 was designed with a deliberate trade-off: RFC 6749
(2012) was intentionally vague and flexible to allow adoption
across different deployment scenarios. This flexibility led to
insecure implementations: developers filled in the gaps with
unsafe defaults (implicit flow for SPAs, skipping state
parameter, prefix matching for redirect_uri).
Eleven years later, RFC 9700 (2023) essentially reversed many
of these flexibilities:
- Implicit flow: deprecated
- ROPC: deprecated for third-party clients
- redirect_uri: must be exact match
- PKCE: recommended for all OAuth clients
The story of OAuth is a case study in standards design:
maximum flexibility at publication → maximum implementation
diversity → maximum vulnerabilities → specification amendments
to prohibit dangerous options. The "right" design was not
available at the start because real-world deployment scenarios
weren't fully known. Security standards need to be updated as
threat intelligence accumulates. The flexibility that enabled
adoption also enabled vulnerabilities.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **TRACE** the authorization code + PKCE flow step by step:
   generate code_verifier, compute challenge, build authorize URL,
   validate state on callback, exchange code at token endpoint.
2. **EXPLAIN** why redirect_uri must be exact match and what
   happens if prefix matching is used (auth code interception via open redirect).
3. **CHOOSE** the right grant type: auth code+PKCE for web/mobile,
   client credentials for service-to-service.
4. **IMPLEMENT** OAuth client in Python/Node with state, PKCE, and
   proper token storage (HttpOnly cookie, not localStorage).

---

### 🎯 Interview Deep-Dive

**Q: Explain the OAuth 2.0 authorization code + PKCE flow.
Why was PKCE added?**

*Why they ask:* OAuth is the de facto standard for API authorization.
Understanding PKCE separates those who know OAuth from those who use it.

*Strong answer covers:*
- Full flow: client generates state + PKCE pair → redirects to auth server →
  user consents → auth server redirects with code → client verifies state
  (CSRF check) → client POSTs code + code_verifier to token endpoint →
  auth server verifies code_challenge matches SHA256(code_verifier) →
  issues access_token + refresh_token.
- PKCE rationale: authorization code can be intercepted (malicious app with
  same redirect_uri on mobile; browser history; referer header). Without PKCE:
  stolen code → stolen token. With PKCE: stolen code is useless without
  code_verifier (only in client memory). PKCE was originally for mobile apps
  (no client_secret possible); now recommended for all.
- State: CSRF protection. Without state: attacker can CSRF the callback URL
  and link victim's account to attacker's OAuth account.
- redirect_uri exact match: prefix matching can be abused with open redirect
  chains to redirect authorization codes to attacker-controlled URLs.
- Implicit flow deprecated (RFC 9700): tokens in URL fragments visible
  to browser, scripts, referrer headers. Auth code flow sends tokens only
  in server-to-server request, never in browser-visible URL.