---
layout: default
title: "API Authentication"
parent: "HTTP & APIs"
nav_order: 234
permalink: /http-apis/api-authentication/
number: "0234"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, HTTPS, Cryptography Basics
used_by: All APIs, API Gateways, Microservices, SaaS Platforms
related: OAuth2, JWT, API Keys, HMAC, OIDC, mTLS
tags:
  - api
  - authentication
  - security
  - jwt
  - oauth2
  - intermediate
---

# 234 — API Authentication

⚡ TL;DR — API authentication verifies the identity of a client making an API request; the main mechanisms are API Keys (simple shared secrets), Bearer Tokens / JWT (stateless signed tokens), OAuth 2.0 (delegated authorization), Basic Auth (username/password in header), and mTLS (mutual TLS certificate exchange) — each appropriate for different trust and use-case contexts.

| #234 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, HTTPS, Cryptography Basics | |
| **Used by:** | All APIs, API Gateways, Microservices, SaaS Platforms | |
| **Related:** | OAuth2, JWT, API Keys, HMAC, OIDC, mTLS | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your API is publicly reachable at api.company.com. Any HTTP client anywhere in
the world can call it. Without authentication: competitor bots scrape all your
data, users can access other users' private data (no identity = no access control),
you have no audit trail, and you can't enforce per-client rate limits or quotas
because you don't know who "the client" is. Authentication is the foundation
on which authorization, rate limiting, billing, and auditing all depend.

**THE INVENTION MOMENT:**
HTTP Basic Auth was RFC 2617 (1999) — username:password encoded in the header.
API Keys emerged from the developer API economy (~2005–2010) — random tokens
assigned to developers to identify and control their integrations. OAuth 1.0/2.0
solved the delegation problem: how can a user authorize a third-party app to
access their data without giving the third party their password? JWT solved the
session scalability problem: stateless tokens the server can verify without
a database lookup. Each mechanism emerged to solve a specific limitation of
its predecessor.

---

### 📘 Textbook Definition

**API Authentication** is the process of verifying the identity of a client making
an API request. It establishes "who is making this request?" — which enables
subsequent authorization ("are they allowed to?"). Common API authentication
mechanisms: **API Keys** (opaque secret strings sent in a header or query param,
validated against a database); **HTTP Basic Auth** (username:password Base64-encoded
in the Authorization header — for system accounts, never for production APIs serving
end users); **Bearer Tokens / JWT** (signed tokens the server validates cryptographically
without database lookup); **OAuth 2.0** (delegation protocol allowing third-party
access with user consent, producing Bearer tokens); **mTLS** (client presents
a certificate that the server validates — common in service-to-service APIs).
Distinct from **Authorization**: Authentication proves identity, Authorization
decides what that identity is allowed to do.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API authentication is proving to an API server "I am who I claim to be" before
it will process your request — via a secret, a signed token, or a certificate.

**One analogy:**

> Authentication is the bouncer checking your ID. Authorization is the staff
> deciding what you're allowed to do once inside. You need the ID check first.
> Different IDs work in different contexts: passport (mTLS), club membership
> card (API key), temporary wristband (JWT), or a voucher from the event organizer
> (OAuth token delegated by the user).

**One insight:**
Authentication mechanisms differ primarily on: who holds the secret (client vs
shared), whether verification requires a DB lookup (API key) or is stateless
(JWT), whether the identity is a human user or a service account, and whether
delegation is needed (OAuth: user authorizes a third-party to act on their behalf).

---

### 🔩 First Principles Explanation

**AUTHENTICATION MECHANISM DECISION TREE:**

```
Q1: Is the client a machine-to-machine integration (no human user)?
  → YES: Use API Key or mTLS or Client Credentials (OAuth2 flow)
  → NO (human user): Continue to Q2

Q2: Does the client need to act on behalf of a user at a DIFFERENT OAuth provider?
  → YES (Google, GitHub, enterprise SSO): Use OAuth 2.0 Authorization Code flow
  → NO (you control both client and auth): Continue to Q3

Q3: Is the user authenticating directly with your service?
  → YES: Issue your own JWT after login (local auth) + check on each request
  → Hybrid: OAuth2 + OIDC (user authenticates with your identity provider, get JWT)
```

**MECHANISM BREAKDOWN:**

```
1. API KEY
   Client sends: GET /resource
                 X-API-Key: sk_live_abc123def456ghi789

   Server receives key → look up in database → find associated account → grant/deny

   Characteristics:
   + Simple to implement and use
   + Works for any HTTP client
   - Requires DB lookup on every request (unless cached)
   - No expiry unless explicitly rotated
   - Long-lived keys are security risk (no refresh)

   Use when: developer integrations, server-to-server, webhooks

2. HTTP BASIC AUTH
   Client sends: Authorization: Basic dXNlcjpwYXNzd29yZA==
                 (base64 of "user:password")

   Server: decode, look up user+hash in DB

   + Very simple
   - Credentials on every request (even to proxies)
   - Not token-based: can't revoke without password change
   - MUST use HTTPS (trivially decoded in transit)
   - Never appropriate for end-user auth in modern APIs

   Use when: internal admin endpoints, simple machine-to-machine with network controls

3. BEARER TOKEN / JWT
   Client sends: Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...

   Server: verify JWT signature (RSA/ECDSA/HMAC) → read claims → no DB needed

   + Stateless verification (no DB hit)
   + Short-lived (exp claim) — limits damage from theft
   + Carries identity claims (userId, roles, scope)
   - Revocation is hard (token valid until expiry)
   - Payload is Base64-encoded, NOT encrypted (don't put secrets in it)

   Use when: user authentication, API-to-API where issuer controls tokens

4. OAUTH 2.0 BEARER TOKEN
   Same as JWT Bearer but token acquired via OAuth2 authorization flow
   Client first exchanges credentials for access_token via /oauth/token
   Then uses access_token as Bearer in API requests

   + Delegated authorization (user consents, third party accesses)
   + Refresh tokens for long-lived access without re-login
   + Scoped (token works for specific resources only)
   - More complex flow to implement

   Use when: third-party apps accessing user data, enterprise SSO

5. mTLS (MUTUAL TLS)
   Both server AND client present TLS certificates
   Server verifies client cert against trusted CA

   + Cryptographically strong; no shared secrets
   + Certificate rotation possible without downtime
   + Works at TLS layer — transparent to application
   - Certificate provisioning complexity (requires PKI)
   - Common in zero-trust architectures and service meshes

   Use when: service-to-service in zero-trust, high-security APIs (banking)
```

---

### 🧪 Thought Experiment

**SCENARIO:** You're building a platform with three client types:

```
Client Type A: Your own mobile app (iOS/Android)
  → Users log into YOUR service
  → Need: user authentication, short-lived sessions
  → Solution: OAuth2 Authorization Code + PKCE → JWT access token (1hr) + refresh token (30 days)

Client Type B: Third-party developers building integrations
  → Developers register at your portal, build scripts that run 24/7
  → Need: server-to-server, no user interaction
  → Solution: API Key (long-lived) OR OAuth2 Client Credentials flow → access token

Client Type C: Internal microservices calling each other
  → service-catalog calls service-inventory
  → Need: service identity, mutual authentication
  → Solution: mTLS (service mesh, each service has a cert) OR OAuth2 Client Credentials
             with per-service client_id/client_secret

Wrong choices:
  Client A with API Keys → developer's key is shared across all users (no per-user identity)
  Client B with password login → no human to type password at 3am in the cron job
  Client C with user JWTs → tokens expire; no mechanism to refresh without user session
```

---

### 🧠 Mental Model / Analogy

> API authentication is like different lock-and-key systems in an office building:
>
> API Key = unique ID badge — anyone with this badge can enter. If lost, issue
> a new one and revoke the old. Identifies the holder (the company/developer),
> not the individual human.
>
> JWT = visitor pass with printed claims ("John from ACME, access floors 2-4,
> valid until 5pm"). Security scans the pass, checks the security manager's
> signature on it (JWKS), and knows the claim is legit without calling the
> security desk. Pass expires automatically.
>
> OAuth2 = signed permission slip from the building owner: "I, Alice, permit
> Bob to access my office (floor 7) during my absence." Bob shows the permission
> slip; security grants him access to floor 7, but not Alice's personal files.
>
> mTLS = both parties swipe their certificate smartcards into a two-way reader.
> Neither can proceed without the other confirming identity.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
API authentication means proving to the server "I'm allowed to be here" before it
responds. You prove this with a secret (API key), a short-lived pass (JWT), or a
login flow (OAuth2). Without it, anyone can call the API.

**Level 2 — How to use it (junior developer):**
For user authentication: issue JWTs after login (POST /auth/login → {access_token, refresh_token}).
Client sends `Authorization: Bearer <token>` on every request. Server validates signature.
For developer integrations: issue API keys from an admin portal. Client sends `X-API-Key: <key>`.
Server looks up key in DB (cached in Redis).

**Level 3 — How it works (mid-level engineer):**
JWT validation: split token into header.payload.signature (Base64). Fetch JWKS from
`/.well-known/jwks.json` (cache 5min). Verify: signature (RSA-256, keyId from header),
expiry (`exp` claim), audience (`aud` claim), issuer (`iss` claim). Extract claims:
userId, roles, scope. Spring Security: configure `JwtDecoder` bean with JWKS URI.
API Gateway: `jwt` plugin validates all tokens before requests reach services.

**Level 4 — Why it was designed this way (senior/staff):**
The evolution from API Keys to JWT to OAuth2 reflects the shift from "who is this
client" to "what is this client allowed to do AND who gave them permission." JWT's
statelessness trades revocation capability for scalability — a 5-minute access token
expiry limits the window of misuse without centralized revocation. OAuth2 solves the
"delegation consent" problem that API Keys can't: with an API key, Alice must give
her key to Bob to act on her behalf; with OAuth2, Alice grants permission scoped
specifically to what Bob needs, revocable at any time. Modern identity (OIDC on top
of OAuth2) adds standardized user profile claims and resolves the "authentication vs
authorization" conflation in vanilla OAuth2, which was an authorization protocol
being widely misused for authentication.

---

### ⚙️ How It Works (Mechanism)

```
JWT VALIDATION MECHANISM:

Token: eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleS0xIn0.
       eyJzdWIiOiJ1c2VyLTQyIiwiZXhwIjoxNjMwMDAwMDYwLCJhdWQiOiJhcGkuY29tcGFueSJ9.
       <signature>

Step 1: Split by "." → header, payload, signature
Step 2: Decode header: { "alg": "RS256", "kid": "key-1" }
Step 3: Fetch JWKS from cache: GET /.well-known/jwks.json → find key with kid="key-1"
Step 4: Verify signature: RS256_verify(header + "." + payload, publicKey, signature)
Step 5: Decode payload: { "sub": "user-42", "exp": 1630000060, "aud": "api.company" }
Step 6: Check claims:
  - exp > now → not expired
  - aud matches our API → intended for us
  - iss = "https://auth.company.com" → from trusted issuer
Step 7: Extract sub="user-42" → set in security context
Step 8: Authorization layer: can user-42 access GET /users/42?
         userSecurity.isOwner(42, "user-42") → yes → allow
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
User login flow (issues JWT):
  POST /auth/login { email, password }
  → verify credentials → generate JWT (5min) + refresh token (30 days)
  → return { access_token, refresh_token }

API call flow (validates JWT):
  GET /api/users/me
  Authorization: Bearer <access_token>
  → API Gateway: validate JWT (JWKS cache)
  → extract sub=user-42, scope=read
  → route to user-service
  → user-service: get user 42 → 200 { id:42, name:"Alice" }

Token refresh flow:
  POST /auth/refresh { refresh_token }
  → validate refresh token (DB lookup — stateful)
  → issue new access_token (5min)
  → return { access_token }
```

---

### 💻 Code Example

```java
// Spring Security — JWT authentication configuration
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // REST API — no CSRF needed (stateless)
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/**").permitAll()       // public auth endpoints
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().authenticated())                  // everything else: require JWT
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.decoder(jwtDecoder())));        // validate JWT on each request
        return http.build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        // Validate JWTs signed by the JWKS from auth server
        return NimbusJwtDecoder.withJwkSetUri("https://auth.company.com/.well-known/jwks.json")
            .build();
    }
}

// API Key authentication filter (for developer integrations)
@Component
public class ApiKeyAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws IOException, ServletException {
        String apiKey = request.getHeader("X-API-Key");
        if (apiKey != null) {
            // Validate API key (uses Redis cache to avoid DB hit per request)
            ApiKeyPrincipal principal = apiKeyService.validate(apiKey);
            if (principal != null) {
                UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        filterChain.doFilter(request, response);
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism      | Stateless  | Expiry                | Delegation | Complexity | Best For                                |
| -------------- | ---------- | --------------------- | ---------- | ---------- | --------------------------------------- |
| **API Key**    | No (DB)    | Manual rotation       | No         | Low        | Server-to-server, developer integration |
| **Basic Auth** | No (DB)    | None                  | No         | Lowest     | Internal/admin only                     |
| **JWT Bearer** | Yes        | Short-lived (exp)     | No         | Medium     | User APIs, microservices                |
| **OAuth2**     | Token yes  | Short-lived + refresh | ✅         | High       | Third-party delegation, SSO             |
| **mTLS**       | Yes (cert) | Certificate expiry    | No         | High       | Zero-trust, service mesh                |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                  |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Authentication = Authorization       | Authentication = who you are; Authorization = what you're allowed to do. Separate concerns               |
| JWT is encrypted                     | JWT is Base64-encoded (not encrypted by default — use JWE for encryption); anyone can decode the payload |
| API Keys are secure long-term        | API Keys don't expire; rotate regularly (90 days). Use short-lived JWTs for user sessions                |
| OAuth2 is an authentication protocol | OAuth2 is an authorization protocol. OIDC (OpenID Connect) is the authentication layer on top of OAuth2  |

---

### 🚨 Failure Modes & Diagnosis

**Token Claims Not Verified — Broken Auth**

Symptom:
Security audit finds that any valid JWT (not expired) from any issuer is accepted.
User from a test environment can access production APIs.

Root Cause:
JWT decoder configured with `jwsAlgorithm` only, not checking `iss` (issuer) or
`aud` (audience) claims. Any RS256-signed JWT is accepted.

Diagnostic / Fix:

```java
// WRONG — only checks signature algorithm:
NimbusJwtDecoder.withJwkSetUri(jwksUri).build();

// CORRECT — also validates issuer and audience claims:
JwtDecoder decoder = NimbusJwtDecoder.withJwkSetUri(jwksUri).build();
OAuth2TokenValidator<Jwt> issuerValidator =
    JwtValidators.createDefaultWithIssuer("https://auth.company.com");
OAuth2TokenValidator<Jwt> audienceValidator =
    token -> token.getAudience().contains("api.company.com")
             ? OAuth2TokenValidatorResult.success()
             : OAuth2TokenValidatorResult.failure(
                 new OAuth2Error("invalid_token", "Wrong audience", null));
((NimbusJwtDecoder) decoder).setJwtValidator(
    new DelegatingOAuth2TokenValidator<>(issuerValidator, audienceValidator));
```

---

### 🔗 Related Keywords

- `JWT` — the token format used for stateless API authentication
- `OAuth2` — the authorization framework enabling delegated API access
- `OIDC` — the authentication layer built on top of OAuth2
- `API Keys` — the simplest API authentication mechanism for developer integrations
- `HMAC` — the signing algorithm used in API key signature verification

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Proving identity to an API: keys,         │
│              │ JWT, OAuth2, mTLS                         │
├──────────────┼───────────────────────────────────────────┤
│ USE CASE MAP │ User login: JWT Bearer                    │
│              │ Third-party delegation: OAuth2            │
│              │ Dev integration: API Key                  │
│              │ Service-to-service: mTLS / Client Creds  │
├──────────────┼───────────────────────────────────────────┤
│ JWT MUST DO  │ Verify sig + exp + iss + aud claims       │
├──────────────┼───────────────────────────────────────────┤
│ API KEY MUST │ Hash stored (not raw), Redis cached,      │
│              │ rotate every 90 days                      │
├──────────────┼───────────────────────────────────────────┤
│ NEVER DO     │ JWT in URL params; API key in git; mTLS   │
│              │ without cert rotation plan                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Who are you?" — proven via secret/cert  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OAuth2 → JWT → OIDC → mTLS               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A JWT has `exp` set to 5 minutes after issuance. A user's account is suspended (banned). The JWT they hold is still valid for up to 4 minutes 59 seconds. How do you revoke a JWT immediately when the token is stateless by design? Design a solution that keeps most JWT validation stateless (no DB hit) while enabling near-instant revocation for the banned-user case, and quantify the tradeoff in infrastructure overhead.
