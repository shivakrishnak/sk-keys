---
layout: default
title: "OAuth2"
parent: "HTTP & APIs"
nav_order: 235
permalink: /http-apis/oauth2/
number: "0235"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, HTTPS, API Authentication, JWT
used_by: Third-party Integrations, Social Login, Enterprise SSO, Mobile Apps
related: OIDC, JWT, API Authentication, API Keys, PKCE
tags:
  - api
  - oauth2
  - authentication
  - authorization
  - security
  - intermediate
---

# 235 — OAuth 2.0

⚡ TL;DR — OAuth 2.0 is an authorization framework that allows a user to grant a third-party application limited access to their resources at another service without sharing their password; the app receives a short-lived access token by directing the user through a consent flow — "Login with Google" and Stripe's API delegation are both OAuth 2.0.

| #235 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, HTTPS, API Authentication, JWT | |
| **Used by:** | Third-party Integrations, Social Login, Enterprise SSO, Mobile Apps | |
| **Related:** | OIDC, JWT, API Authentication, API Keys, PKCE | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user wants to give a third-party app (say, a calendar sync service) access to their
Google Calendar. Before OAuth: the only option was to give the third-party service
your Google username and password. They stored it, used it to log in as you, and had
full access to your entire Google account — forever, unless you changed your password.
This was called the "password anti-pattern." Security disaster: if the sync service
was breached, your Google credentials were compromised. No way to revoke just that
service's access. No visibility into what it accessed.

**THE INVENTION MOMENT:**
OAuth was designed specifically to solve the password anti-pattern. The key insight:
instead of giving a third party your credentials (full access), you give them a
"voucher" (access token) that:

1. Was issued by YOU via a consent flow ("Do you authorize CalSync to READ your calendar?")
2. Is scoped (read-only, not write or email access)
3. Expires (valid for 1 hour, not forever)
4. Can be revoked (revoke just CalSync's access, not your whole account)
   OAuth 2.0 (RFC 6749, 2012) became the industry standard. OIDC built on top of it
   to standardize user authentication.

---

### 📘 Textbook Definition

**OAuth 2.0** (OAuth2) is an authorization framework (RFC 6749) that defines protocols
for a resource owner (user) to grant a third-party client application limited, scoped,
and time-bounded access to resources at a resource server, mediated by an authorization
server issuing access tokens — without the client application ever seeing the user's
credentials. OAuth2 defines four **grant types** (flows): Authorization Code (interactive
web/mobile), Implicit (deprecated), Client Credentials (machine-to-machine), and
Resource Owner Password Credentials (deprecated for third-party, allowed for first-party).
The current best-practice extension for public clients (SPAs, mobile) is
**Authorization Code + PKCE** (RFC 7636), which prevents authorization code interception
attacks. OAuth2 itself is an authorization framework, not an authentication protocol —
**OIDC (OpenID Connect)** is the authentication layer built on top.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OAuth2 lets users grant third-party apps limited access to their data at another
service, through a consent flow, without sharing their password.

**One analogy:**

> OAuth2 is like a valet key. Your main car key opens everything — trunk, all doors,
> glove box. A valet key only starts the car and unlocks the driver door — limited
> access, designed to be handed to someone you don't fully trust.
>
> The user is the car owner. The third-party app is the valet. OAuth2 lets you
> generate and hand over a valet key (access token with limited scope) rather than
> your master key (password). You can take the valet key back (revoke the token)
> without changing your master key.

**One insight:**
OAuth2's core insight is separating authorization from authentication: "what are
you permitted to do" (OAuth2) from "who are you" (OIDC). This separation allowed
OAuth2 to become the universal standard for third-party access, while OIDC standardized
how identity claims travel alongside that authorization.

---

### 🔩 First Principles Explanation

**THE FOUR ROLES:**

```
RESOURCE OWNER — the user
  Owns the resource (Google Calendar, GitHub repos)
  Grants or denies consent to third-party apps

RESOURCE SERVER — the API holding the resource
  (Google Calendar API, GitHub API)
  Accepts and validates access tokens
  Returns protected data if token has correct scope

AUTHORIZATION SERVER — issues tokens after consent
  (Google Identity Platform, Auth0, Keycloak, Okta)
  Authenticates the user
  Presents consent screen (scopes)
  Issues access_token + refresh_token

CLIENT — the third-party app (CalSync, your app)
  Wants access to the user's resource
  Initiates the OAuth flow
  Exchanges code for token
  Calls Resource Server with access_token
```

**THE FOUR GRANT TYPES:**

```
1. AUTHORIZATION CODE (with PKCE) — current best practice for interactive apps

   Use for: web apps, SPAs, mobile apps where a user is present
   Flow:
   a. Client redirects user to auth server /authorize:
      ?response_type=code
      &client_id=app123
      &redirect_uri=https://app.example.com/callback
      &scope=calendar:read
      &state=random-csrf-token
      &code_challenge=PKCE_challenge  (PKCE extension)
   b. Auth server: authenticate user → show consent screen
   c. User consents → auth server redirects to redirect_uri with:
      ?code=AUTH_CODE&state=random-csrf-token
   d. Client: verify state → POST /token:
      code=AUTH_CODE, client_id, redirect_uri, code_verifier (PKCE)
   e. Auth server: verify code + PKCE → issue:
      { access_token, refresh_token, expires_in, scope }
   f. Client calls Resource Server with Bearer access_token

2. CLIENT CREDENTIALS — machine-to-machine (no user)

   Use for: service A calling service B, cron jobs, backend integrations
   Flow:
   a. Client: POST /token
      grant_type=client_credentials
      client_id=svc_A, client_secret=secret_A
      scope=orders:read
   b. Auth server: validate credentials → issue access_token (no refresh)
   c. Client calls Resource Server

3. REFRESH TOKEN — extend sessions without re-login

   Use for: renewing expired access tokens silently
   Flow:
   a. access_token expires (401 from Resource Server)
   b. Client: POST /token grant_type=refresh_token, refresh_token=<token>
   c. Auth server: validate refresh token → issue new access_token
      (optionally: new refresh_token via token rotation)

4. IMPLICIT (deprecated) — don't use
   ROPC (deprecated) — avoid for third-party use
```

---

### 🧪 Thought Experiment

**SCENARIO:** "Login with GitHub" for a developer tools app.

```
Your app (DevTools.io) wants to:
- Identify who the GitHub user is (name, email)
- Read their public repos list

FLOW:

1. User clicks "Login with GitHub" on DevTools.io
2. DevTools.io redirects to:
   https://github.com/login/oauth/authorize
   ?client_id=Ov23li...
   &redirect_uri=https://devtools.io/callback
   &scope=user:email,public_repo
   &state=abc123
   &code_challenge=xyz...  (PKCE)

3. User: logs into GitHub (if not) → sees:
   "DevTools.io wants to:
    ✓ Read your email address
    ✓ Read your public repositories
    [Authorize DevTools.io]"

4. User clicks Authorize → GitHub redirects to:
   https://devtools.io/callback?code=AUTH_CODE&state=abc123

5. DevTools.io backend:
   verify state=abc123 → POST to GitHub:
   https://github.com/login/oauth/access_token
   { code: AUTH_CODE, client_id: ..., client_secret: ..., code_verifier: ... }

6. GitHub returns: { access_token: "gho_...", scope: "user:email,public_repo" }

7. DevTools.io calls GitHub API:
   GET https://api.github.com/user
   Authorization: Bearer gho_...
   → { login: "alice", email: "alice@example.com", ... }

8. DevTools.io: find or create user by GitHub ID,
   issue your own session token to the user

NOTE: access_token is GitHub's, not yours. You use it to get user info.
Then you issue YOUR OWN JWT to the user for subsequent requests.
```

---

### 🧠 Mental Model / Analogy

> OAuth2 is the "front desk authorization" model:
>
> You (user) arrive at a hotel (authorization server).
> A courier from FedEx (third-party app) needs access to your room (resource) to
> deliver a package. FedEx can't have your room key (password).
>
> OAuth2 process:
>
> - FedEx asks the front desk (authorization server): "May I access Alice's room?"
> - Front desk calls you: "FedEx wants to enter your room for 30 minutes to drop
>   a package. Do you consent?"
> - You say yes.
> - Front desk gives FedEx a temporary keycard (access token): room 412, door only,
>   valid 30 minutes, one entry.
> - FedEx enters room 412, drops package, leaves. Keycard expires.
> - FedEx never knew your master key. You can revoke the keycard at reception.
>   You keep your master key.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OAuth2 is the "Login with Google/GitHub/Facebook" system. It lets apps get permission
to access bits of your data at another service, with your consent, without you giving
them your password. The access is limited and can be revoked.

**Level 2 — How to use it (junior developer):**
Don't build OAuth2 yourself — use a library (Spring Security OAuth2 Client, Auth0 SDK,
Keycloak). For "Login with Google": register your app at Google Cloud Console, get
client_id + client_secret, configure redirect URIs. Configure Spring Security:
`spring.security.oauth2.client.*`. For machine-to-machine: use Client Credentials grant.

**Level 3 — How it works (mid-level engineer):**
Authorization Code + PKCE: Client generates a `code_verifier` (random 32+ bytes),
`code_challenge = SHA256(code_verifier)`. Redirect to `/authorize` with
`code_challenge`. Auth server stores it. When client exchanges code for token at
`/token`, send `code_verifier`. Auth server: SHA256(code_verifier) == stored
code_challenge? → prevents authorization code theft (e.g., by a malicious app
intercepting the redirect on mobile). Token rotation: each `refresh_token` use
issues a new `refresh_token`; old one is invalidated — detect if the old one is
replayed (token reuse attack: invalidate the entire grant).

**Level 4 — Why it was designed this way (senior/staff):**
OAuth2 deliberately left several design decisions open (RFC 6749 is intentionally
flexible), which led to fragmented implementations and security issues — the JWT
profile for access tokens (RFC 9068) and PKCE (RFC 7636) were later additions
to close gaps. The Implicit flow was deprecated (RFC 9700) because access tokens
delivered in URL fragments were vulnerable to history/log leakage. The OAuth 2.1
draft consolidates best practices: Authorization Code + PKCE as the only interactive
flow, Client Credentials for M2M, and eliminates the vulnerable flows. OIDC layered
on top of OAuth2 adds the missing authentication contract: standardized `id_token`
(JWT with user claims), `userinfo` endpoint, discovery document
(`/.well-known/openid-configuration`). This separation allows OAuth2 to be used
for authorization without OIDC, while OIDC always includes OAuth2.

---

### ⚙️ How It Works (Mechanism)

```
AUTHORIZATION CODE + PKCE FLOW DIAGRAM:

User        Client (App)       Auth Server         Resource Server
                               (Google/Keycloak)   (Google Calendar API)

  [Click "Login with Google"]
               ↓
               Generate: code_verifier (random 32B)
               code_challenge = BASE64URL(SHA256(code_verifier))
               ↓
               Redirect to GET /authorize
               ?response_type=code
               &client_id=app123
               &scope=calendar.read
               &redirect_uri=https://app/callback
               &state=randomcsrf
               &code_challenge=XXXX
               &code_challenge_method=S256
                                   ↓
                                   Authenticate user
                                   Show consent screen
                                   User clicks "Allow"
                                   ↓
               ← Redirect https://app/callback
                 ?code=AUTH_CODE&state=randomcsrf
               ↓
               Verify state matches
               POST /token
               { code: AUTH_CODE,
                 redirect_uri: ...,
                 client_id: app123,
                 client_secret: secret,  ← server-side apps only
                 code_verifier: YYYY }   ← PKCE verification
                                   ↓
                                   SHA256(YYYY) == XXXX? ✓
                                   Issue tokens
               ← { access_token: "ey...",
                   refresh_token: "...",
                   expires_in: 3600,
                   scope: "calendar.read" }
               ↓
               GET /calendars
               Authorization: Bearer ey...
                                              ↓
                                              Validate token
                                              Check scope: calendar.read
                                              ← 200 { calendars: [...] }
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Spring Security + Google OAuth2 Login:

1. User hits /dashboard (protected) → Spring redirects to:
   https://accounts.google.com/o/oauth2/auth?... (auto-generated by Spring)

2. Google: authenticate user → consent screen
   → redirect to /login/oauth2/code/google?code=xxx&state=yyy

3. Spring Security OAuth2 Client:
   - Verify state (CSRF protection)
   - Exchange code for tokens (POST to Google /token)
   - Call Google /userinfo → { sub, email, name }
   - Create/lookup local user record
   - Create local session (SecurityContext)
   - Redirect to original /dashboard

4. Subsequent requests use local session cookie (Spring Session)
   NOT the Google access_token (that was ephemeral for identity lookup)
```

---

### 💻 Code Example

```java
// Spring Boot — OAuth2 Login (Social Login with GitHub)
// build.gradle: implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login").permitAll()
                .anyRequest().authenticated())
            .oauth2Login(oauth2 -> oauth2
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard"));
        return http.build();
    }
}

// application.yml
// spring:
//   security:
//     oauth2:
//       client:
//         registration:
//           github:
//             client-id: ${GITHUB_CLIENT_ID}
//             client-secret: ${GITHUB_CLIENT_SECRET}
//             scope: user:email,read:user

// Custom success handler that saves or creates the user
@Component
public class OAuthLoginSuccessHandler implements AuthenticationSuccessHandler {

    @Override
    public void onAuthenticationSuccess(HttpServletRequest req,
                                        HttpServletResponse res,
                                        Authentication auth) throws IOException {
        OAuth2AuthenticationToken token = (OAuth2AuthenticationToken) auth;
        OAuth2User principal = token.getPrincipal();

        String email = principal.getAttribute("email");
        String githubId = principal.getAttribute("id").toString();

        // Find or create user in local DB
        User user = userRepository.findByGithubId(githubId)
            .orElseGet(() -> userRepository.save(
                new User(githubId, email, principal.getAttribute("name"))));

        // Issue our own JWT for subsequent API calls
        String jwt = jwtService.generateToken(user);
        res.addCookie(createSecureCookie("session", jwt));
        res.sendRedirect("/dashboard");
    }
}
```

```java
// Spring Boot — Client Credentials (machine-to-machine)
@Configuration
public class ServiceClientConfig {

    @Bean
    public WebClient inventoryServiceClient(OAuth2AuthorizedClientManager manager) {
        // Automatically fetches + refreshes Client Credentials tokens
        ServletOAuth2AuthorizedClientExchangeFilterFunction oauth2 =
            new ServletOAuth2AuthorizedClientExchangeFilterFunction(manager);
        oauth2.setDefaultClientRegistrationId("inventory-service");

        return WebClient.builder()
            .baseUrl("https://inventory.internal")
            .apply(oauth2.oauth2Configuration())
            .build();
    }
}
// application.yml:
// spring.security.oauth2.client.registration.inventory-service:
//   authorization-grant-type: client_credentials
//   client-id: ${SVC_CLIENT_ID}
//   client-secret: ${SVC_CLIENT_SECRET}
//   scope: inventory:read,inventory:write
```

---

### ⚖️ Comparison Table

| Grant Type             | User Present | Use Case                 | PKCE     | Tokens Issued    |
| ---------------------- | ------------ | ------------------------ | -------- | ---------------- |
| **Auth Code + PKCE**   | Yes          | Web/Mobile apps          | Required | access + refresh |
| **Client Credentials** | No           | M2M, services            | No       | access only      |
| **Implicit**           | Yes          | (deprecated — don't use) | N/A      | access only      |
| **ROPC**               | Yes          | (avoid for 3rd party)    | No       | access + refresh |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| OAuth2 is an authentication protocol        | OAuth2 is an authorization protocol — it does NOT authenticate users by itself. OIDC adds authentication (id_token, userinfo endpoint) |
| The access_token IS the user session        | The access_token grants access to a third-party resource. After validating GitHub identity, issue YOUR OWN session token               |
| Client Credentials needs PKCE               | PKCE is for flows with a redirect (interactive). Client Credentials is a direct server-to-server POST — no redirect, no PKCE needed    |
| refresh_token can be stored in localStorage | Refresh tokens are long-lived and must be stored securely: HttpOnly cookie or secure device keychain — never localStorage (XSS risk)   |

---

### 🚨 Failure Modes & Diagnosis

**Authorization Code Injection / CSRF on Callback**

Symptom:
Security test shows that an attacker can insert their own `code` into the redirect
callback URL, causing your app to exchange a code that was authorized by the attacker's
account — logging YOU in as the ATTACKER.

Root Cause:
State parameter missing or not validated. PKCE not implemented.

Diagnostic:

```
# Verify state parameter round-trip:
1. Generate state = random 32-byte hex → store in session
2. Include state in /authorize redirect
3. On callback: assert request.state == session.state
4. If mismatch → abort → return 400

# PKCE prevents code interception on mobile (no client_secret):
# Without PKCE: attacker intercepts auth code from redirect URI
# → exchanges it at /token → gets tokens for your user
# With PKCE: attacker doesn't have code_verifier → token exchange fails

# Spring Security: PKCE enabled by default for public clients
# Keycloak: require PKCE on client configuration
```

---

### 🔗 Related Keywords

- `OIDC` — the authentication layer built on top of OAuth2 (adds id_token and userinfo)
- `JWT` — the token format commonly used for OAuth2 access tokens
- `PKCE` — the security extension required for public clients (mobile/SPA)
- `API Authentication` — the broader category that OAuth2 is one solution within

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Authorization framework for delegated    │
│              │ third-party access via consent flow       │
├──────────────┼───────────────────────────────────────────┤
│ CORE INSIGHT │ Issue scoped, expiring tokens instead of │
│              │ sharing passwords ("password anti-pattern")│
├──────────────┼───────────────────────────────────────────┤
│ FOUR ROLES   │ Owner → AuthServer → Client → ResServer  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHICH    │ Web/Mobile: Auth Code + PKCE              │
│ GRANT?       │ M2M: Client Credentials                  │
│              │ Extending session: Refresh Token          │
├──────────────┼───────────────────────────────────────────┤
│ OAUTH2 ≠     │ OAuth2 = authorization (what can you do) │
│ AUTHN        │ OIDC = authentication (who are you)      │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS:      │ Validate state; use PKCE; short-lived    │
│              │ access tokens; rotate refresh tokens     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consent-based delegated access"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OIDC → JWT → PKCE → Token Rotation       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A mobile app uses Authorization Code + PKCE with Google. The app stores the refresh_token in Android Keystore. The user's device is stolen and the thief factory-resets the phone. The Google refresh token was also backed up to Google Drive (standard behavior). An attacker restores the backup on a new device. Design a comprehensive token security model that: prevents use of stolen refresh tokens, limits blast radius of a compromised token, and supports instant user-initiated "sign out everywhere" — without requiring all requests to be stateful.
