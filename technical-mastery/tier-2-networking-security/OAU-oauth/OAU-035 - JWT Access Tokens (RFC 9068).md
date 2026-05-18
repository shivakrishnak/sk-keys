---
id: OAU-035
title: "JWT Access Tokens (RFC 9068)"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★★☆
depends_on: OAU-008, OAU-015, OAU-023, OAU-028
used_by: OAU-028, OAU-036, OAU-041, OAU-045, OAU-050
related: OAU-008, OAU-023, OAU-028, OAU-041, OAU-045
tags:
  - security
  - oauth
  - jwt
  - access-tokens
  - rfc-9068
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/oauth/jwt-access-tokens-rfc-9068/
---

⚡ TL;DR - RFC 9068 standardizes the structure of JWT-based
OAuth 2.0 access tokens. Key requirements: `iss` (issuer),
`exp` (expiry), `aud` (audience - the RS identifier, NOT the
client_id), `sub` (subject - user or client), `client_id`
(the OAuth client), `iat` (issued-at), `jti` (unique ID for
replay prevention), and `scope` (granted permissions). The
critical difference from ID tokens: `aud` must be the Resource
Server identifier, not the client. Validating `aud` at the RS
is non-negotiable - it prevents tokens issued for one service
from being used against another (confused deputy attack).

---

### 🔥 The Problem This Solves

**THE TOKEN FORMAT STANDARDIZATION PROBLEM:**

Before RFC 9068 (2021), every OAuth provider invented their
own JWT access token structure. Auth0, Keycloak, AWS Cognito,
Azure AD all used different claim names, different `aud`
semantics, and different scope formats. Resource Servers had
to be configured per-AS. RFC 9068 defines the standard claim
set so any RFC-compliant access token can be validated by any
RFC-compliant RS without provider-specific logic.

---

### 📘 Textbook Definition

RFC 9068 (JSON Web Token Profile for OAuth 2.0 Access Tokens)
defines the standard structure for JWT access tokens in OAuth
2.0. It specifies required and optional claims and their
semantics, extending RFC 7519 (JWT) and the OpenID Connect
Core claim definitions.

**Required claims:**

**`iss` (Issuer):** AS identifier URL. RS must verify this
matches the expected AS.

**`exp` (Expiration):** Unix timestamp. RS rejects expired
tokens.

**`aud` (Audience):** The RS identifier (a URI or logical
identifier like `api.example.com`). NOT the client_id. RS
must verify the token is intended for it specifically.

**`sub` (Subject):** User identifier (for user-delegated
tokens) or client_id (for client credentials tokens).

**`iat` (Issued At):** Unix timestamp of issuance.

**`jti` (JWT ID):** Unique identifier for this token.
Enables replay detection when combined with a seen-token
store (optional but recommended for refresh tokens,
high-security contexts).

**`client_id`:** The OAuth client that was issued this
token (different from `sub` when acting on behalf of user).

**`scope`:** Space-separated list of granted scopes. RS uses
this for per-endpoint authorization.

---

### ⏱️ Understand It in 30 Seconds

**A complete RFC 9068 access token payload:**

```json
{
  "iss": "https://as.example.com",
  "exp": 1883000400,
  "aud": "https://api.example.com",
  "sub": "user-123",
  "client_id": "contacts-spa",
  "iat": 1882996800,
  "jti": "dbe39bf3-a3eb-4734-b4e2-cd5d496879bb",
  "scope": "read:contacts write:contacts",
  "auth_time": 1882996000
}
```

**The `aud` vs `client_id` distinction:**
`aud` = WHO the token is FOR (the Resource Server)
`client_id` = WHO obtained the token (the OAuth client)

Token says: "The contacts-spa (client_id) obtained permission
on behalf of user-123 (sub) to call api.example.com (aud)
with scopes read:contacts write:contacts."

---

### ⚙️ How It Works (Mechanism)

**JWT access token validation chain at the Resource Server:**

```
┌──────────────────────────────────────────────────────────┐
│  RFC 9068 JWT ACCESS TOKEN VALIDATION                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Incoming: Authorization: Bearer eyJhbGciOiJSUzI1NiJ9... │
│                                                           │
│  STEP 1: Structural parse                                  │
│    Split by '.': header.payload.signature                 │
│    header: { "alg": "RS256", "kid": "key-2024-01" }       │
│    Decode payload (base64url) → claims                    │
│                                                           │
│  STEP 2: Signature verification                           │
│    Fetch JWKS from AS (cached):                           │
│      GET https://as.example.com/.well-known/jwks.json     │
│    Find key matching kid="key-2024-01" in JWKS            │
│    Verify RS256 signature using public key                │
│    FAIL → 401 (tampered token)                            │
│                                                           │
│  STEP 3: iss validation                                   │
│    JWT.iss == configured AS issuer URL?                   │
│    FAIL → 401 (wrong issuer / multi-tenant violation)     │
│                                                           │
│  STEP 4: aud validation ← CRITICAL                        │
│    JWT.aud contains this RS's identifier?                 │
│    aud may be a string or array of strings                │
│    FAIL → 401 (token intended for different service)      │
│    SKIP → confused deputy vulnerability                   │
│                                                           │
│  STEP 5: exp validation                                   │
│    JWT.exp > current_time?                                │
│    FAIL → 401 (expired token, client should refresh)      │
│                                                           │
│  STEP 6: scope validation (per endpoint)                  │
│    JWT.scope contains required scope for this endpoint?   │
│    FAIL → 403 insufficient_scope                          │
│                                                           │
│  STEP 7: Business authorization (optional)                │
│    JWT.sub → look up user permissions in DB?              │
│    Check if user owns the requested resource?             │
│                                                           │
│  SUCCESS → Allow request, set SecurityContext             │
└──────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
  TOKEN[JWT Access Token\nfrom Authorization Header] --> SIG{Step 1-2:\nSignature valid?}
  SIG -->|No| R401A[401 invalid_token]
  SIG -->|Yes| ISS{Step 3:\niss == expected issuer?}
  ISS -->|No| R401B[401 invalid_token\ntenant/issuer mismatch]
  ISS -->|Yes| AUD{Step 4:\naud contains this RS?}
  AUD -->|No| R401C[401 invalid_token\nwrong audience]
  AUD -->|Yes| EXP{Step 5:\nexp > now?}
  EXP -->|No| R401D[401 invalid_token\ntoken expired]
  EXP -->|Yes| SCOPE{Step 6:\nscope contains required?}
  SCOPE -->|No| R403[403 insufficient_scope]
  SCOPE -->|Yes| ALLOW[200 - Allow request]
```

---

### 💻 Code Example

**Example 1 - BAD then GOOD: aud claim validation:**

```python
# BAD: Validates signature and expiry but NOT aud claim
# Any token from this AS can be used against this RS,
# even if it was issued for a completely different service.

def validate_token_bad(token: str) -> dict:
    jwks_client = PyJWKClient(JWKS_URI)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # WRONG: audience=False skips aud validation
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=EXPECTED_ISSUER,
        options={"verify_aud": False},  # DANGEROUS
    )
    # A token issued for payments-api.example.com can now
    # be used against contacts-api.example.com
    # → CONFUSED DEPUTY ATTACK
    return claims
```

```python
# GOOD: Full RFC 9068 validation including aud
# WHY: aud validation is the defense against confused deputy.
#   Token for Service A MUST NOT be accepted by Service B.

from jwt import PyJWKClient, decode as jwt_decode
from datetime import datetime, timezone

EXPECTED_ISSUER = "https://as.example.com"
THIS_RS_AUDIENCE = "https://contacts-api.example.com"
JWKS_URI = "https://as.example.com/.well-known/jwks.json"

# Singleton: JWKS client caches keys automatically
_jwks_client = PyJWKClient(JWKS_URI, cache_keys=True)

def validate_access_token(token: str) -> dict:
    """
    RFC 9068 compliant JWT access token validation.
    Validates: signature, iss, aud, exp.
    Raises: jwt.exceptions.* on failure.
    """
    # Step 1+2: Get signing key (uses JWKS cache)
    try:
        signing_key = (
            _jwks_client.get_signing_key_from_jwt(token)
        )
    except Exception as e:
        raise TokenValidationError(
            f"Cannot find signing key: {e}"
        )

    # Steps 3-5: Validate iss, aud, exp in one decode call
    claims = jwt_decode(
        token,
        signing_key.key,
        algorithms=["RS256"],   # Only accept RS256
        issuer=EXPECTED_ISSUER,
        audience=THIS_RS_AUDIENCE,  # CRITICAL: aud check
        options={
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": True,   # Never set to False
            "require": ["exp", "iss", "aud", "sub", "jti"],
        },
    )

    # Step 6: Validate required RFC 9068 claims present
    required_claims = {"iss", "exp", "aud", "sub", "jti"}
    missing = required_claims - set(claims.keys())
    if missing:
        raise TokenValidationError(
            f"Missing required claims: {missing}"
        )

    return claims

def validate_scope(
    claims: dict,
    required_scope: str,
) -> None:
    """Validate token has required scope for this endpoint."""
    granted_scopes = set(
        claims.get("scope", "").split()
    )
    if required_scope not in granted_scopes:
        raise InsufficientScopeError(
            f"Token lacks required scope: {required_scope}. "
            f"Granted: {granted_scopes}"
        )
```

**Example 2 - JWT access token structure for different grant types:**

```python
# For reference: claim differences by grant type

# CLIENT CREDENTIALS GRANT (machine-to-machine):
# sub = client_id (NO user identity)
{
  "iss": "https://as.example.com",
  "sub": "batch-processor-service",   # client_id as sub
  "aud": "https://data-api.example.com",
  "client_id": "batch-processor-service",
  "exp": 1883000400,
  "iat": 1882996800,
  "jti": "abc-123",
  "scope": "read:orders write:reports",
  # NO: email, name, auth_time (no user)
}

# AUTHORIZATION CODE GRANT (user-delegated):
# sub = user identifier, client_id = the app
{
  "iss": "https://as.example.com",
  "sub": "user-alice-789",            # user identifier
  "aud": "https://contacts-api.example.com",
  "client_id": "contacts-spa",        # different from sub
  "exp": 1883000400,
  "iat": 1882996800,
  "jti": "def-456",
  "scope": "read:contacts",
  "auth_time": 1882996000,  # when user last authenticated
  "acr": "urn:mace:incommon:iap:silver",  # auth strength
}

# VALIDATION RULE: check sub to determine delegation type
# sub == client_id: machine token (client credentials)
# sub != client_id: user-delegated token (auth code flow)
```

---

### ⚖️ Comparison Table

| Claim | Required | Who Validates | Security Purpose |
|---|---|---|---|
| `iss` | Yes | RS | Issuer integrity (multi-tenant isolation) |
| `aud` | Yes | RS | Audience check (confused deputy prevention) |
| `exp` | Yes | RS | Token expiry enforcement |
| `sub` | Yes | App layer | User/client identity |
| `jti` | Recommended | RS (for revocation lists) | Replay prevention |
| `scope` | Yes (practical) | RS per endpoint | Permission enforcement |
| `client_id` | Yes | App layer | Which app obtained this token |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The `aud` claim should contain the client_id | `aud` is the AUDIENCE (the Resource Server, the service the token is intended for), not the requesting client. The OAuth client is identified by `client_id`. An access token issued for `payments-api.example.com` has `aud: "payments-api.example.com"`, and `client_id: "checkout-app"`. If `aud` is the client_id, the confused deputy defense is broken. |
| JWT access tokens are an OpenID Connect concept | JWT access tokens for OAuth 2.0 are standardized in RFC 9068 (2021), which is an OAuth specification, not OIDC. ID tokens (the OIDC concept) use a similar JWT structure but with different required claims and different `aud` semantics (ID token `aud` = client_id; access token `aud` = RS). These are distinct token types with different purposes. |
| `jti` is just optional noise; nobody implements replay detection | `jti` is optional per RFC, but its practical importance scales with token sensitivity. For short-lived access tokens (5-15 minutes), replay windows are narrow and a revocation list isn't worth the overhead. For refresh tokens or high-value operations (fund transfers, one-time-use codes), a `jti`-based seen-token store prevents replay attacks. Many financial APIs (PSD2 Open Banking) require `jti` replay detection. |
| The `sub` claim is always the user's ID | In client credentials flow, `sub` is the `client_id` (there is no user). In authorization code flow, `sub` is the user's identifier. The same claim has two different semantics depending on the grant type. To distinguish: if `sub == client_id`, it's a machine token; if `sub != client_id`, it's a user-delegated token. |

---

### 🚨 Failure Modes & Diagnosis

**Confused Deputy Attack via Missing `aud` Validation**

**Symptom:**
Penetration test finds that an access token issued for
`payments-api.example.com` can be used to call
`contacts-api.example.com` successfully. Both services share
the same AS, same JWKS endpoint, and the contacts service
does not validate `aud`.

**Root Cause:**
RS configured with `options={"verify_aud": False}` or
no `audience` parameter in JWT decode call.

**Diagnostic:**

```python
# Check if aud validation is active:
import jwt
token_payload = jwt.decode(
    token,
    options={"verify_signature": False},  # decode only
)
print(f"Token aud: {token_payload.get('aud')}")
print(f"This RS expected aud: {THIS_RS_AUDIENCE}")
# If different: the check would catch confused deputy
# If aud validation is disabled: it won't
```

**Fix:**
Always pass `audience=THIS_RS_AUDIENCE` to JWT decode.
Never set `verify_aud=False`. In Spring Security:
configure `spring.security.oauth2.resourceserver.jwt.audiences`
with the RS's own audience identifier. Test that tokens for
other services are rejected with 401.

---

**JWT Access Token Too Large for HTTP Headers**

**Symptom:**
After adding more custom claims to access tokens, some HTTP
clients (NGINX, Apache, certain load balancers) start returning
400 Bad Request for requests with Bearer tokens. Error message:
"request header too large" or "Header too large".

**Root Cause:**
JWT access tokens grow linearly with claims. A token with
20+ claims (user profile, roles, org info, permissions) can
exceed 4-8KB. HTTP headers have limits: NGINX default 8KB
per header, some AWS ALB configurations 10KB. Base64-encoded
JWTs are ~33% larger than the JSON payload.

**Fix:**
Keep JWT access tokens small. Store only authentication/
authorization claims in the token (iss, sub, aud, exp, scope,
client_id, jti). For larger user data, use token introspection
(call AS per request) or include a `sub` claim and look up
profile in a shared cache (Redis) keyed by sub. Alternatively,
increase NGINX `large_client_header_buffers` and ALB limits.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Access Token` - the general concept
- `Token Validation` - the validation chain

**Builds On:**
- `DPoP (RFC 9449)` - proof-of-possession extension to JWT AT
- `OAuth 2.0 with Spring Security` - the RS that validates these

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REQUIRED     │ iss, exp, aud, sub, iat, jti, client_id   │
│ CLAIMS       │ scope (practical requirement)             │
├──────────────┼───────────────────────────────────────────┤
│ AUD vs       │ aud = Resource Server identifier          │
│ CLIENT_ID    │ client_id = OAuth client (the app)        │
│              │ NEVER aud = client_id in access tokens    │
├──────────────┼───────────────────────────────────────────┤
│ SUB MEANING  │ User token: sub = user ID                 │
│              │ Machine token: sub = client_id            │
├──────────────┼───────────────────────────────────────────┤
│ VALIDATION   │ sig → iss → aud → exp → scope (in order)  │
│ ORDER        │ Never skip aud! Confused deputy risk.     │
├──────────────┼───────────────────────────────────────────┤
│ TOKEN SIZE   │ Keep <2KB (fit in HTTP headers safely)    │
│              │ Don't embed large user profiles in AT     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "aud = RS, not client. Validate all 5:    │
│              │  sig, iss, aud, exp, scope. Never skip."  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `aud` must be the Resource Server's identifier, NOT the
   `client_id`. The RS must validate it explicitly. Skipping
   `aud` validation enables confused deputy attacks where any
   valid token from the AS can be used against any service.

2. Validation order is non-negotiable: signature → iss → aud →
   exp → scope. All five steps at every request. Short-circuit
   any one step and the RS has a security vulnerability.

3. JWT access tokens should be small: iss, sub, aud, exp, jti,
   client_id, scope. Don't embed user profiles. Large tokens
   exceed HTTP header limits and create privacy/caching issues.
