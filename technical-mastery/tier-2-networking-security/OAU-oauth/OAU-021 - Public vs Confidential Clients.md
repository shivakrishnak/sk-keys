---
id: OAU-021
title: "Public vs Confidential Clients"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★☆☆
depends_on: OAU-007, OAU-009, OAU-013, OAU-018
used_by: OAU-022, OAU-025, OAU-026, OAU-028
related: OAU-007, OAU-013, OAU-022, OAU-025
tags:
  - security
  - oauth
  - clients
  - architecture
  - foundational
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/oauth/public-vs-confidential-clients/
---

⚡ TL;DR - OAuth 2.0 clients are classified as confidential
(can keep a secret) or public (cannot keep a secret). Confidential
clients run on a server you control and can securely hold a
`client_secret`. Public clients - SPAs, mobile apps, desktop
apps - run on untrusted devices where any embedded secret can
be extracted by users or attackers, so they have NO client
secret. This distinction drives the security model: confidential
clients authenticate with their secret; public clients use PKCE
as a substitute. The classification determines which grant types
are available and what security controls are required.

---

### 🔥 The Problem This Solves

**THE CORE PROBLEM:**

The OAuth 2.0 specification requires client authentication at
the token endpoint for security: only the legitimate client
should be able to exchange an authorization code for tokens.
For server-side applications, this is straightforward: store
the `client_secret` on the server. But for a browser-based
SPA or a mobile app, any "secret" you embed in the code is
accessible to anyone who opens DevTools or decompiles the app.
A "secret" that everyone can see is not a secret. How do you
authenticate a client that has no ability to keep secrets?

**THE ANSWER:**

OAuth 2.0 formalizes this as a first-class distinction: some
clients are capable of maintaining confidentiality
(confidential clients); others are not (public clients). Public
clients use PKCE (Proof Key for Code Exchange) as a substitute
for client authentication - a per-authorization-request
challenge that cannot be pre-stolen because it is generated
fresh for each authorization request.

---

### 📘 Textbook Definition

RFC 6749 §2.1 classifies clients based on their ability to
maintain confidentiality of client credentials:

**Confidential clients:** Capable of maintaining the
confidentiality of their credentials. Examples: server-side
web applications, backend services, APIs. They authenticate to
the token endpoint using a `client_secret` (basic auth or
form parameter) or a client assertion (signed JWT, RFC 7523).

**Public clients:** Incapable of maintaining the
confidentiality of their credentials. Examples: native apps
(iOS, Android, desktop), single-page applications (SPAs),
command-line tools. They MUST use PKCE for the Authorization
Code flow. They cannot use Client Credentials flow (no way
to authenticate without a secret).

RFC 8252 (OAuth for Native Apps) and RFC 9207 (OAuth 2.1 draft)
further specify that native apps are always public clients
regardless of how the client_secret is delivered, because all
app distribution mechanisms expose embedded secrets.

---

### ⏱️ Understand It in 30 Seconds

**One question to classify any client:**

> "Can a user or attacker access the client's source code,
> configuration files, or memory at runtime?"

If YES → public client. If NO (code runs only on your server,
inaccessible to users) → confidential client.

**One table:**

```
CAN KEEP SECRET?  CLIENT TYPE     SECRET STRATEGY
Server-side app   Confidential    client_secret in env vars
Native mobile app Public          PKCE (no secret)
SPA (React/Vue)   Public          PKCE (no secret)
CLI tool          Public          PKCE (no secret)
Desktop app       Public          PKCE (no secret)
Backend service   Confidential    client_secret or JWT
```

**One insight:**
"Public" does not mean "insecure." Public clients with PKCE
are the correct, secure, modern pattern for browser-based and
native apps. "Public" means "cannot keep a secret" - not
"not protected." PKCE provides the client authentication
property without requiring a shared secret.

---

### ⚙️ How It Works (Mechanism)

**Token endpoint authentication - confidential vs public:**

```
CONFIDENTIAL CLIENT (has client_secret):

  POST /token
  Content-Type: application/x-www-form-urlencoded
  Authorization: Basic base64(client_id:client_secret)
                        ← OR in body:
  Body: grant_type=authorization_code
        &code=AUTH_CODE
        &client_id=CLIENT_ID
        &client_secret=CLIENT_SECRET  ← authenticates client
        &redirect_uri=REDIRECT_URI

  AS validates:
    1. client_id exists
    2. client_secret matches stored hash
    3. This client is authorized to use this grant type
    4. code is valid and bound to this client
    5. Issues tokens

PUBLIC CLIENT (no client_secret - uses PKCE instead):

  POST /token
  Content-Type: application/x-www-form-urlencoded
  Body: grant_type=authorization_code
        &code=AUTH_CODE
        &client_id=CLIENT_ID      ← identifies client
        &redirect_uri=REDIRECT_URI
        &code_verifier=CODE_VERIFIER  ← PKCE! no secret

  AS validates:
    1. client_id exists and is public client
    2. SHA256(code_verifier) == code_challenge in stored request
    3. Proves this is the same entity that started the flow
    4. Issues tokens (no client authentication - PKCE is the control)
```

**Why public clients cannot use Client Credentials:**

```
Client Credentials = M2M authentication

Authentication basis: client_id + client_secret
  → client_secret proves identity

Public client: no client_secret (anyone can read it)
  → client_id alone is NOT authentication (it's public)
  → There is no way to prove the client is legitimate
  → Client Credentials flow for public clients = no auth
  → ANY code with the client_id can get tokens
  → NEVER appropriate for public clients

Solution for M2M: use a backend server (confidential client)
as a proxy. The public client (SPA/mobile) calls your backend;
your backend calls the external API using Client Credentials.
```

---

### 💻 Code Example

**Example 1 - BAD then GOOD: Identifying and handling a public client:**

```javascript
// BAD: Embedding client_secret in a React SPA
// Anyone can view this in browser DevTools
// Anyone can view it in the minified bundle
// Any user can copy it from the network tab

const CLIENT_ID = 'my-client-id';
const CLIENT_SECRET = 'super-secret-value'; // WRONG!

async function exchangeCode(code) {
  const response = await fetch('/token', {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET, // EXPOSED IN BROWSER
    })
  });
  return response.json();
}
```

```javascript
// GOOD: SPA as public client - PKCE, no client_secret
// WHY: SPA cannot keep secrets. PKCE provides equivalent
//   authorization code binding without shared secret.
//   The server validates SHA256(verifier) == challenge.

import { randomBytes, createHash } from 'crypto';

function generatePKCE() {
  // Code verifier: 43-128 char random string
  const verifier = randomBytes(43)
    .toString('base64url')
    .slice(0, 64);
  // Code challenge: SHA256(verifier) base64url-encoded
  const challenge = createHash('sha256')
    .update(verifier)
    .digest('base64url');
  return { verifier, challenge };
}

function buildAuthorizationUrl(challenge) {
  const state = randomBytes(32).toString('base64url');
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: CLIENT_ID,  // Only client_id, no secret
    redirect_uri: REDIRECT_URI,
    scope: 'openid email',
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256',
  });
  // Store state + verifier in sessionStorage
  // (OK for state/verifier - they are single-use and
  //  not long-lived credentials)
  sessionStorage.setItem('oauth_state', state);
  sessionStorage.setItem('code_verifier', verifier);
  // Note: In production, prefer sessionStorage over
  // localStorage (cleared on tab close)
  return `${AUTH_ENDPOINT}?${params}`;
}

async function exchangeCode(code, verifier) {
  const response = await fetch(TOKEN_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      code_verifier: verifier,  // PKCE - no secret needed
    })
  });
  return response.json();
  // WHAT BREAKS: AS requires PKCE for public clients but
  //   code_challenge_method is set to 'plain' instead of 'S256'.
  //   Use S256 only (plain = no hash = insecure).
  // HOW TO TEST: Attempt exchange with wrong verifier →
  //   AS should return error=invalid_grant
}
```

**Example 2 - BAD then GOOD: Backend for Frontend (BFF) pattern:**

```python
# BAD: SPA calls external API directly with token
# Token visible to JavaScript → XSS risk
# SPA needs client_secret for some AS flows → can't

# GOOD: BFF pattern for public clients calling confidential APIs
# WHY: BFF is a server-side confidential client.
#   SPA calls only YOUR backend (same-origin or trusted).
#   YOUR backend calls external APIs as confidential client.
#   Tokens never go to browser JavaScript.

# In the SPA (public client):
# User triggers action → calls /api/contacts (your BFF)
# No access_token in the browser at all

# BFF server (Python Flask - confidential client):
from flask import Flask, request, g
from functools import wraps

app = Flask(__name__)

def require_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Session-based auth between SPA and BFF
        # (session cookie, httpOnly, not bearer token)
        if 'access_token' not in g.session:
            return {'error': 'not_logged_in'}, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/contacts')
@require_session
def get_contacts():
    # BFF holds the access token server-side
    # Client (SPA) never sees the access_token directly
    token = g.session['access_token']
    resp = requests.get(
        'https://external-api.example.com/contacts',
        headers={'Authorization': f'Bearer {token}'}
    )
    return resp.json()
    # WHAT BREAKS: Horizontal scaling of BFF requires shared
    #   session store (Redis). In-memory sessions break
    #   sticky-session-free deployments.
```

---

### ⚖️ Comparison Table

| Property | Confidential Client | Public Client |
|---|---|---|
| **Can keep secret** | Yes | No |
| **Authentication method** | client_secret or JWT | PKCE (no secret) |
| **Runs on** | Your server (inaccessible to users) | Browser, mobile device, desktop |
| **Client Credentials flow** | Yes | No (no client auth possible) |
| **Refresh tokens** | Yes | Yes (with AS config) |
| **PKCE required** | Optional (but recommended) | Mandatory |
| **Examples** | Spring Boot, Node.js backend, microservice | React SPA, iOS app, CLI tool |

---

### 🔁 Flow / Lifecycle

```
DESIGN TIME: Classify your client
  "Can the source code or running process be accessed
   by users or attackers?"
  → YES: public client
  → NO: confidential client

REGISTRATION TIME: Configure at AS
  Confidential: set client_secret, enable CC flow
  Public: mark as public, enable only Authorization Code flow
          (with required PKCE), no CC flow

RUNTIME:
  Confidential: include client_secret in token requests
  Public: generate PKCE per-request, include code_verifier
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Obfuscating the client_secret in a mobile app makes it confidential | RFC 8252 §8.4: "Secrets that are statically included as part of an app distributed to multiple users should not be treated as confidential." Reverse engineering, decompilation, and binary analysis trivially extract obfuscated secrets. A public client with an obfuscated secret is still a public client - the obfuscation provides no real protection. |
| Public clients are less secure than confidential clients | PKCE-protected public clients and confidential clients have comparable security for Authorization Code flow. The key difference is that confidential clients can use Client Credentials flow (M2M). Public clients are not "less secure" - they are appropriately secured without a shared secret. |
| A React app can be made confidential by using a proxy | Using a server-side proxy (BFF pattern) makes the PROXY a confidential client, not the React SPA. The SPA remains a public client; it just delegates the confidential operations to the BFF. This is the correct architecture. |
| Every OAuth client should request Client Credentials capability | Client Credentials is only for machine-to-machine flows with no user. Enabling Client Credentials on a client that is ever distributed to users is a security misconfiguration - any user with the client_id could potentially extract the secret and get M2M tokens. |

---

### 🚨 Failure Modes & Diagnosis

**client_secret Exposed in Mobile App Binary**

**Symptom:**
Security researcher or attacker extracts `client_secret` from
an iOS or Android app bundle. The secret is used to call the
token endpoint with `grant_type=client_credentials`, obtaining
access tokens without any user authorization.

**Root Cause:**
Mobile app was registered as a confidential client and the
`client_secret` was embedded in the app bundle, configuration
file, or hardcoded in source code.

**Diagnostic:**

```bash
# Check for secrets in Android APK:
apktool d com.example.app.apk -o decompiled/
grep -r "client_secret\|client-secret" decompiled/

# Check iOS IPA:
unzip -d extracted_ipa YourApp.ipa
strings extracted_ipa/Payload/YourApp.app/YourApp | \
  grep -i "secret\|password\|token"

# Check source code for embedded secrets:
grep -rn "client_secret" src/ --include="*.swift" \
  --include="*.kt" --include="*.java"
```

**Fix:**
Re-register the mobile app as a PUBLIC client (no
`client_secret`). Implement PKCE for Authorization Code flow.
Rotate the compromised `client_secret` immediately (if a
confidential client that runs server-side). For the mobile app:
remove the secret and use PKCE only.

---

### 🔗 Related Keywords

**Prerequisites:**
- `OAuth 2.0 Roles` - the client role in OAuth
- `Client ID and Client Secret` - the secret-keeping mechanism

**Builds On:**
- `PKCE` - the substitute for client authentication in public clients
- `Backend for Frontend (BFF)` - the architectural pattern for
  public clients that need confidential capabilities

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONFIDENTIAL │ Runs on server you control; has secret    │
│              │ that cannot be extracted by users         │
├──────────────┼───────────────────────────────────────────┤
│ PUBLIC       │ Runs on user's device (browser/mobile);   │
│              │ NO secret - use PKCE instead              │
├──────────────┼───────────────────────────────────────────┤
│ THE TEST     │ "Can a user view or extract the code/     │
│              │  config?" YES = public. NO = confidential │
├──────────────┼───────────────────────────────────────────┤
│ MOBILE APP   │ Always public (RFC 8252), even if secret  │
│              │ is embedded - binary is extractable       │
├──────────────┼───────────────────────────────────────────┤
│ PUBLIC AUTH  │ PKCE (code_challenge + code_verifier)     │
│ METHOD       │ - per-request, cannot be pre-stolen       │
├──────────────┼───────────────────────────────────────────┤
│ CC FLOW      │ Confidential clients only (needs auth).   │
│              │ Public clients: use BFF pattern           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Confidential = secret on server.         │
│              │  Public = PKCE instead of secret."        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Confidential = server-side, has client_secret.
   Public = browser/mobile, uses PKCE, has NO secret.
   Classification is determined by where code runs, not by how
   you configure the AS.

2. A `client_secret` embedded in a mobile app or SPA source is
   not a secret - anyone can extract it. Mobile apps are always
   public clients per RFC 8252.

3. Public clients use PKCE as a per-request substitute for
   client authentication. PKCE is not a weaker alternative
   to secrets - it provides equivalent security for the
   Authorization Code flow.

**Interview one-liner:**
"OAuth 2.0 clients are confidential (can keep a secret - server-
side) or public (cannot - SPA, mobile, CLI). Public clients use
PKCE instead of client_secret for Authorization Code flow;
they cannot use Client Credentials (no way to authenticate).
Mobile apps are always public per RFC 8252 even with obfuscated
secrets. Confidential clients authenticate at the token endpoint
with client_secret or a JWT assertion."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[CLASSIFY]** Given a system diagram showing 5 different
   OAuth clients (web app, mobile app, SPA, batch job, CLI),
   classify each as public or confidential, identify their
   authentication method, and state which grant types apply.

2. **[EXPLAIN]** A developer asks why their mobile app cannot
   use Client Credentials for API access. Explain the public
   client constraint and propose the BFF pattern as the
   architectural solution.

3. **[AUDIT]** Review a codebase for client_secret exposure:
   embedded in mobile app, hardcoded in SPA JavaScript, or
   present in a client-side configuration file. Identify each
   instance and describe the remediation steps including
   credential rotation.
