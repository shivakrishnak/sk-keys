---
id: ATH-022
title: "OIDC Login Flow (Authentication via OAuth)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-010, ATH-011
used_by: ATH-025, ATH-033, ATH-059
related: ATH-010, ATH-023, ATH-033
tags:
  - security
  - authentication
  - oidc
  - oauth
  - sso
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/authentication/oidc-login-flow-authentication-via-oauth/
---

⚡ **TL;DR** - OpenID Connect (OIDC) is the authentication layer built
on top of OAuth 2.0. OAuth 2.0 handles authorization (delegating access
to resources); OIDC adds an ID Token (a signed JWT asserting the user's
identity) and a UserInfo endpoint. OIDC is how "Sign in with Google"
works: the user authenticates at Google, Google issues an ID Token
proving who the user is, your application trusts it without managing
credentials directly.

---

### 📊 Entry Metadata

| #022 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-010, ATH-011 | |
| **Used by:** | ATH-025, ATH-033, ATH-059 | |
| **Related:** | ATH-010 Tokens, ATH-023 JWT Validation, ATH-033 PKCE | |

---

### 📘 Textbook Definition

OpenID Connect 1.0 (OIDC) is an identity layer on top of
OAuth 2.0 that enables clients to verify the identity of end
users and obtain basic profile information. OIDC adds to
OAuth 2.0: an ID Token (a JWT containing identity claims such
as sub, email, name), a UserInfo endpoint for additional claims,
and a discovery document (`.well-known/openid-configuration`)
for metadata. The Authorization Code flow with PKCE is the
recommended OIDC flow for web applications, replacing all
password-based login for delegated identity scenarios.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           OIDC Authorization Code Flow                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. User clicks "Sign in with Google"                  │
│                                                        │
│  2. App redirects to IdP with:                         │
│     GET /authorize?                                    │
│       client_id=APP_ID                                 │
│       &response_type=code                              │
│       &scope=openid email profile                      │
│       &redirect_uri=https://app/callback               │
│       &state=RANDOM_STATE    ← CSRF protection        │
│       &nonce=RANDOM_NONCE    ← replay protection      │
│       &code_challenge=...     ← PKCE (ATH-033)        │
│                                                        │
│  3. User authenticates at IdP (Google, Okta, Auth0)    │
│  4. IdP redirects to callback:                         │
│     GET /callback?code=AUTH_CODE&state=RANDOM_STATE    │
│                                                        │
│  5. App verifies state == stored state (CSRF)          │
│  6. App exchanges code for tokens:                     │
│     POST /token {code, client_id, client_secret,       │
│                  code_verifier (PKCE)}                 │
│     Response: {access_token, id_token, refresh_token}  │
│                                                        │
│  7. App validates ID Token:                            │
│     - Verify signature (IdP's public key)             │
│     - Verify iss (issuer)                              │
│     - Verify aud (audience = client_id)               │
│     - Verify exp (not expired)                         │
│     - Verify nonce matches (replay attack prevention)  │
│  8. Extract sub (user identifier) - establish session  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security OIDC login**

```java
@Configuration
@EnableWebSecurity
public class OidcSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http)
            throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                // Spring auto-configures OIDC from
                // application.yml provider settings
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .failureUrl("/login?error")
                // Map OIDC claims to Spring Security authorities
                .userInfoEndpoint(info -> info
                    .oidcUserService(customOidcUserService())
                )
            );
        return http.build();
    }
}
```

**Example - BAD vs GOOD: missing nonce validation**

```java
// BAD: validating ID Token without nonce check
public OidcUser validateIdToken(String rawToken) {
    Jwt jwt = jwtDecoder.decode(rawToken);
    // Validates: signature, exp, iss, aud
    // MISSING: nonce validation
    return buildOidcUser(jwt);
}
// Risk: replay attack - attacker captures a victim's
// ID token from a previous session and replays it
// to log in as that victim

// GOOD: include nonce validation
public OidcUser validateIdToken(String rawToken,
                                String expectedNonce) {
    Jwt jwt = jwtDecoder.decode(rawToken);
    String tokenNonce = jwt.getClaimAsString("nonce");
    if (!expectedNonce.equals(tokenNonce)) {
        throw new InvalidNonceException("Nonce mismatch");
    }
    // Nonce was generated per-request and stored in session
    // If replay: token's nonce does not match fresh nonce
    return buildOidcUser(jwt);
}
```

---

*Authentication category: ATH | Entry: ATH-022 | v5.0*