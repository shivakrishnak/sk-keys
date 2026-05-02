---
layout: default
title: "OIDC"
parent: "HTTP & APIs"
nav_order: 237
permalink: /http-apis/oidc/
number: "0237"
category: HTTP & APIs
difficulty: ★★★
depends_on: OAuth2, JWT, HTTP
used_by: Enterprise SSO, Social Login, Identity Federation, Mobile Apps
related: OAuth2, JWT, API Authentication, SAML, Federation
tags:
  - api
  - oidc
  - authentication
  - identity
  - sso
  - advanced
---

# 237 — OIDC (OpenID Connect)

⚡ TL;DR — OpenID Connect (OIDC) is an authentication layer built on top of OAuth 2.0 that adds a standardized `id_token` (a JWT containing verified user identity claims), a `/userinfo` endpoint, and a discovery document — turning OAuth2 from a pure authorization protocol into a complete identity and authentication protocol used by "Login with Google/Microsoft/Apple."

┌──────────────────────────────────────────────────────────────────────────┐
│ #237 │ Category: HTTP & APIs │ Difficulty: ★★★ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ OAuth2, JWT, HTTP │ │
│ Used by: │ Enterprise SSO, Social Login, │ │
│ │ Identity Federation, Mobile │ │
│ Related: │ OAuth2, JWT, API Auth, SAML, Fed │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
OAuth2 tells you that a user authorized your app to access their Google account.
But it doesn't tell you WHO that user is. OAuth2 says "you have permission to read
the calendar" — it doesn't say "this token belongs to alice@example.com, born 1985,
account ID xyz." Companies working around this started using OAuth2 for authentication
improperly: calling `/userinfo` in non-standard ways, using the access token as an
identity signal (wrong — it's an authorization artifact). Every identity provider
(Google, Facebook, GitHub) implemented a different OAuth2-based login flow with
incompatible user profile endpoints and different claim names for the same concept
("email" vs "mail" vs "primary_email").

**THE INVENTION MOMENT:**
OpenID Connect (2014, finalized by OpenID Foundation) was created to standardize
identity on top of OAuth2. The insight: add one more token to the OAuth2 response
— the `id_token` — a JWT specifically for authentication that carries standardized
identity claims (sub, email, name, picture) signed by the identity provider.
This one addition transforms OAuth2 into a full authentication protocol. OIDC also
standardizes discovery (`.well-known/openid-configuration`) so any client can
automatically discover the authentication endpoints and capabilities of any
OIDC-compliant provider.

---

### 📘 Textbook Definition

**OpenID Connect (OIDC)** is a standard authentication protocol (OpenID Connect Core 1.0, 2014) built as a thin identity layer on top of OAuth 2.0. OIDC extends the OAuth2
Authorization Code flow by returning an `id_token` alongside (or instead of) an
`access_token`. The `id_token` is a JWT signed by the identity provider containing
standardized claims: `sub` (stable, unique user identifier), `iss` (issuer),
`aud` (intended recipient client), `exp`, `iat`, and optionally `email`, `name`,
`picture`, and other profile claims. OIDC also defines: a `/userinfo` endpoint for
additional claims, a discovery document at `/.well-known/openid-configuration` (OIDC
Discovery), and nonce-based replay protection for the `id_token`. OIDC separates
identity (who is this user?) from authorization (what can they do?): the `id_token`
answers identity; the `access_token` answers authorization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OIDC is "OAuth2 + a standardized identity token" — it adds the `id_token` (a JWT with
who-you-are claims) to OAuth2's access token, turning authorization into authentication too.

**One analogy:**

> OAuth2 is a building access card: it lets you in and specifies what floors you
> can access. OIDC adds a name badge to that access card: it says "John Smith,
> Engineering". The access system (OAuth2) handles entry permissions; the name
> badge (id_token) establishes identity.
>
> Before OIDC, everyone improvised their own name badge format. After OIDC,
> all name badges follow the same standard — any organization can read any badge.

**One insight:**
The key design insight of OIDC: the `id_token` is for the CLIENT to verify
user identity. The `access_token` is for the CLIENT to call the RESOURCE SERVER.
They serve different audiences. Never use the `access_token` to determine who the user
is — it's an opaque authorization credential for the resource server.

---

### 🔩 First Principles Explanation

**OIDC vs OAUTH2 (what OIDC adds):**

```
OAUTH2 Response:
{
  "access_token": "ya29.opaque_token...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read:calendar"
}

OIDC Response (adds id_token):
{
  "access_token": "ya29.opaque_token...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "openid profile email",  ← openid scope triggers OIDC
  "id_token": "eyJhbGciOiJSUzI1NiJ9..."  ← THIS is the new OIDC addition
}
```

**ID_TOKEN STRUCTURE:**

```
DECODED id_token PAYLOAD:
{
  "iss": "https://accounts.google.com",     ← who issued this
  "sub": "10769150350006150715113082367",   ← stable, unique user ID
  "aud": "your-client-id.apps.googleusercontent.com", ← must match your client_id
  "exp": 1630003600,                        ← expiry
  "iat": 1630000000,                        ← issued at
  "nonce": "abc123xyz",                     ← replay protection
  "email": "alice@example.com",             ← from profile scope
  "email_verified": true,
  "name": "Alice Smith",
  "picture": "https://lh3.googleusercontent.com/...",
  "given_name": "Alice",
  "family_name": "Smith",
  "locale": "en"
}
```

**OIDC DISCOVERY (OpenID Provider Metadata):**

```
GET https://accounts.google.com/.well-known/openid-configuration

{
  "issuer": "https://accounts.google.com",
  "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
  "token_endpoint": "https://oauth2.googleapis.com/token",
  "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
  "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",  ← key for id_token validation
  "scopes_supported": ["openid", "email", "profile", ...],
  "claims_supported": ["sub", "email", "email_verified", "name", ...]
}

This standard endpoint lets ANY OIDC client:
- Auto-discover all endpoints (no hardcoding)
- Auto-fetch JWKS for token validation
- Understand supported features
→ One config URL → fully configured OIDC client
```

**NONCE — REPLAY PROTECTION:**

```
1. Client generates random nonce="abc123xyz" → stores in session
2. Client includes nonce in /authorize request
3. Provider includes nonce in id_token payload
4. Client verifies: id_token.nonce == stored nonce
→ Prevents: attacker replaying a captured id_token from a previous login
  (old nonce won't match current session's nonce)
```

---

### 🧪 Thought Experiment

**SCENARIO:** "Login with Microsoft" for an enterprise SaaS.

```
Your app: ProjectMgr SaaS
Identity Provider: Microsoft Azure AD (Entra ID)
Goal: enterprise customers use their Microsoft identity to log in

FLOW:

1. Discovery:
   GET https://login.microsoftonline.com/common/.well-known/openid-configuration
   → discover: authorization_endpoint, token_endpoint, jwks_uri

2. User: clicks "Sign in with Microsoft" on ProjectMgr
3. Redirect to Microsoft /authorize with scope: "openid profile email"

4. Microsoft: authenticate user (password/MFA) → consent screen
   → type: enterprise SSO → no consent needed if admin pre-authorized

5. Redirect back with code → ProjectMgr exchanges for tokens:
   { access_token, id_token, refresh_token }

6. ProjectMgr: verify id_token:
   - Signature: JWKS from jwks_uri in discovery doc
   - iss: "https://login.microsoftonline.com/tenant-id/v2.0"
   - aud: "ProjectMgr client_id"
   - nonce: matches stored nonce
   - exp: not expired

7. Extract from id_token:
   sub = "90839df0-abc-123"  ← stable MS user ID (never changes)
   email = "alice@acmecorp.com"
   name = "Alice Johnson"

8. ProjectMgr: find user by MS sub (not email — email can change)
   Create if new → local session → redirect to dashboard

CRITICAL: store users by id_token.sub, NOT email
  Email can change; sub is permanent and unique per provider
```

---

### 🧠 Mental Model / Analogy

> OIDC is the passport + access badge system at an international conference:
>
> OAuth2 is the access badge: it says which sessions you can attend (authorization).
> OIDC adds the passport: it establishes who you are internationally (authentication).
>
> The passport (id_token) is issued by your country (identity provider — Google, MS).
> It's signed by the country (cryptographic signature — JWKS).
> Any conference organizer (OIDC client) worldwide can verify the signature
> and trust the identity claims in the passport.
> The discovery document is the list of embassies (where to verify each country's passports).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OIDC is what powers "Login with Google/Apple/Microsoft." It adds a standard identity
token (id_token) to OAuth2's permission token (access_token), so your app knows not
just that the user authorized you, but WHO they are.

**Level 2 — How to use it (junior developer):**
Add `openid` to OAuth2 scopes. Extract `id_token` from token response. Validate it
(signature + iss + aud + exp + nonce). Extract `sub` for stable user identity, `email`
for display. Use a library (Spring Security, Auth0 SDK) — don't parse id_tokens manually.
Store users by `sub`, not by email.

**Level 3 — How it works (mid-level engineer):**
OIDC Discovery: fetch `/.well-known/openid-configuration` → cache the JSON. Extract
`jwks_uri`, `authorization_endpoint`, `token_endpoint`. Spring Security OAuth2 Client
does this automatically via `issuer-uri`. `id_token` validation: same as JWT — JWKS
signature + iss + aud + exp + nonce. `userinfo` endpoint: call with access_token to
get additional claims not in id_token (useful for large payloads or dynamic profile info).
Back-channel logout (optional spec): provider POSTs a logout token to your registered
`backchannel_logout_uri` when user signs out from provider.

**Level 4 — Why it was designed this way (senior/staff):**
OIDC's key design decision — using OAuth2 as the foundation rather than a new protocol —
was pragmatic: OAuth2 infrastructure (authorization servers, client libraries, browser
redirect flows) already existed. OIDC adds a ~10% specification on top to fix the
authentication gap. The `sub` claim being a stable opaque identifier (not email) is
critical: email addresses change, email providers change, but `sub` (scoped to issuer)
uniquely identifies the user forever for that issuer. The separation of `id_token`
(for client authentication) from `access_token` (for API authorization) is often
misunderstood: sending the `id_token` to your API as authentication is wrong —
the `id_token.aud` is your client_id, not your API. Your API should receive an
`access_token` (with your API in the `aud`). This separation enabled federated identity:
log in with any OIDC provider, your app creates a local account linked to the provider's sub.

---

### ⚙️ How It Works (Mechanism)

```
OIDC AUTHORIZATION CODE FLOW:

Client App                    Auth Server (OIDC Provider)
    │                                │
    ├─ GET /authorize ───────────────►│
    │  scope: openid profile email   │
    │  response_type: code            │
    │  nonce: abc123 (random)         │
    │  state: csrf456 (random)        │
    │                                │
    │◄── redirect /callback?code=X ──┤ (after user auth + consent)
    │    state: csrf456              │
    │                                │
    ├─ POST /token ──────────────────►│
    │  code: X                       │
    │  client_secret: ***            │
    │                                │
    │◄── { access_token,             │
    │      id_token: JWT,            │
    │      refresh_token } ──────────┤
    │                                │
    Validate id_token:               │
    • verify signature (JWKS)        │
    • iss, aud, exp, nonce           │
    Extract: sub, email, name        │
    Find/create user by sub          │
    Issue local session              │

    [Optional: GET /userinfo ────────►]
    [  Authorization: Bearer access_token]
    [◄── { sub, email, name, picture } ]
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Spring Boot + Google OIDC ("Login with Google"):

application.yml:
  spring:
    security:
      oauth2:
        client:
          registration:
            google:
              client-id: ${GOOGLE_CLIENT_ID}
              client-secret: ${GOOGLE_CLIENT_SECRET}
              scope: openid,profile,email
          provider:
            google:
              issuer-uri: https://accounts.google.com  ← auto-discovers all endpoints

Spring Security auto:
  1. Redirects unauthenticated requests to Google /authorize
  2. Handles /login/oauth2/code/google callback
  3. Exchanges code for tokens at Google /token
  4. Validates id_token (JWKS from discovery + claims)
  5. Calls /userinfo (if configured)
  6. Creates OidcUser principal with all claims
  7. Creates local SecurityContext/session

Your code: @AuthenticationPrincipal OidcUser user
   → user.getSubject() // stable id
   → user.getEmail()
   → user.getFullName()
```

---

### 💻 Code Example

```java
// Spring Security OIDC — custom user loading from id_token
@Service
public class CustomOidcUserService extends OidcUserService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public OidcUser loadUser(OidcUserRequest userRequest) throws OAuth2AuthenticationException {
        OidcUser oidcUser = super.loadUser(userRequest); // validates id_token internally

        // Extract stable identifier: sub (never use email as primary key)
        String providerId = oidcUser.getSubject();  // e.g. "10769150350006..."
        String provider = userRequest.getClientRegistration().getRegistrationId(); // "google"

        // Find or create local user
        User localUser = userRepository.findByProviderAndProviderId(provider, providerId)
            .orElseGet(() -> {
                User newUser = new User();
                newUser.setProvider(provider);
                newUser.setProviderId(providerId);
                newUser.setEmail(oidcUser.getEmail());
                newUser.setName(oidcUser.getFullName());
                return userRepository.save(newUser);
            });

        // Sync mutable fields (email/name can change)
        localUser.setEmail(oidcUser.getEmail());
        localUser.setName(oidcUser.getFullName());
        userRepository.save(localUser);

        // Return OidcUser enriched with local user data (for your app's authorization)
        return new CustomOidcUser(oidcUser, localUser);
    }
}

// Access in controller
@GetMapping("/dashboard")
public String dashboard(@AuthenticationPrincipal OidcUser oidcUser, Model model) {
    model.addAttribute("user", oidcUser.getFullName());
    model.addAttribute("email", oidcUser.getEmail());
    // id_token claims
    String subject = oidcUser.getSubject();  // stable across sessions
    return "dashboard";
}
```

---

### ⚖️ Comparison Table

| Protocol            | Purpose                 | Token Type                    | Standardized Claims    | Discovery    |
| ------------------- | ----------------------- | ----------------------------- | ---------------------- | ------------ |
| **OAuth2**          | Authorization           | access_token (opaque)         | None                   | No           |
| **OIDC**            | Authentication + AuthZ  | id_token (JWT) + access_token | sub, email, name, etc. | ✅           |
| **SAML 2.0**        | Authentication (legacy) | XML assertions                | Varies                 | XML metadata |
| **Custom JWT auth** | Authentication          | JWT (custom)                  | Non-standard           | No           |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OIDC and OAuth2 are independent protocols  | OIDC is a thin layer ON TOP of OAuth2 — it requires an OAuth2 authorization server as its foundation                                                          |
| The access_token can verify user identity  | access_token is for authorizing API calls, not identifying users. id_token is for identity. Never forward access_token as "proof of identity" to your backend |
| Same sub claim works across OIDC providers | Sub is scoped to the issuer — Google sub ≠ Microsoft sub for the same user. Store (provider + sub) as composite identity key                                  |
| OIDC handles authorization too             | OIDC handles authentication (identity). Combine with authorization (roles, permissions) in your own system or use OAuth2 scopes for coarse-grained access     |

---

### 🚨 Failure Modes & Diagnosis

**User Records Duplicated After Email Change**

Symptom:
User changes their Google email. On next login: a new account is created for them.
Their old account (with all data) is orphaned. User contacts support "I lost all my data."

Root Cause:
Users stored by email (`WHERE email = ?`) instead of by sub (`WHERE sub = ?`).
Google's sub is permanent; email changes when user renames their Google account.

Diagnostic:

```sql
-- Find users registered multiple times (different emails, same provider)
SELECT sub, COUNT(*) as logins
FROM user_oauth_identities
WHERE provider = 'google'
GROUP BY sub HAVING COUNT(*) > 1;
-- These are duplicate accounts for the same Google sub
-- Fix: merge accounts, use (provider, sub) as unique identifier

-- Prevention: add unique constraint on (provider, provider_id):
ALTER TABLE user_oauth_identities
  ADD CONSTRAINT uq_provider_sub UNIQUE (provider, provider_id);
```

---

### 🔗 Related Keywords

- `OAuth2` — the authorization protocol that OIDC builds upon
- `JWT` — the token format of the OIDC `id_token`
- `SAML` — the older enterprise SSO protocol that OIDC is often replacing
- `Federation` — the broader concept of trusting external identity providers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Authentication layer on OAuth2; adds     │
│              │ id_token (JWT) + discovery endpoint      │
├──────────────┼───────────────────────────────────────────┤
│ KEY ADDITION │ id_token: JWT with sub, email, name,     │
│              │ signed by IdP, for CLIENT to verify      │
├──────────────┼───────────────────────────────────────────┤
│ DISCOVERY    │ /.well-known/openid-configuration →      │
│              │ auto-discover all endpoints + JWKS       │
├──────────────┼───────────────────────────────────────────┤
│ USER KEY     │ Store by (provider + sub) — never email  │
├──────────────┼───────────────────────────────────────────┤
│ id_token vs  │ id_token → client identity verification │
│ access_token │ access_token → API authorization         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "OAuth2 + WHO YOU ARE in a standard JWT"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JWT → OAuth2 → SAML → Federation         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your SaaS supports both OIDC SSO (enterprise customers using Google/Microsoft) and local email/password accounts. A user has a local account (email: alice@company.com). Their company later configures Google SSO. The user logs in via Google for the first time — Google's id_token contains email "alice@company.com". Should you link their Google identity to the existing local account? What are the security implications? Design the account-linking policy that prevents account takeover while enabling a smooth SSO transition for legitimate users.
