---
id: ATH-046
title: "Token Theft and Session Hijacking"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-009, ATH-031, ATH-032, ATH-045
used_by: ATH-047, ATH-050, ATH-052
related: ATH-031, ATH-032, ATH-044
tags:
  - security
  - authentication
  - token-theft
  - session-hijacking
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/authentication/token-theft-and-session-hijacking/
---

⚡ **TL;DR** - Once an attacker has your session cookie or bearer
token, they are you - authentication is already complete. Token
theft vectors: XSS (JavaScript reads localStorage or cookie without
HttpOnly), network interception (HTTP, not HTTPS), server logs
(token in URL query param), or memory dumps. Defense: HttpOnly
cookies (XSS cannot read them), short token expiry, token binding
to device fingerprint, and continuous session monitoring
(unusual IP/UA = force re-auth).

---

### 📊 Entry Metadata

| #046 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-009 Cookie Mechanics, ATH-031 Bearer Tokens, ATH-032 Refresh Tokens, ATH-045 JWT Algorithm | |
| **Used by:** | ATH-047, ATH-050, ATH-052 | |
| **Related:** | ATH-031 Bearer, ATH-032 Refresh, ATH-044 ATO | |

---

### 📘 Textbook Definition

Token theft is the act of obtaining a valid authentication
token (session cookie, access token, refresh token) without
going through the authentication process. Session hijacking
uses a stolen token to impersonate the legitimate user.
Primary theft vectors: XSS (injected JavaScript exfiltrates
tokens from storage), network eavesdropping (HTTP responses
include tokens), exposed application logs (tokens in URLs
end up in access logs), CSRF (cross-site requests use
existing cookies), and physical access (tokens in browser
storage). Defense-in-depth: secure storage, short token
lifetime, device binding, and behavioral anomaly detection.

---

### ⚙️ How It Works (Mechanism)

**Token theft by storage location:**

```
┌────────────────────────────────────────────────────────┐
│         Token Storage vs Theft Risk                    │
├─────────────────────┬──────────────────────────────────┤
│  Storage Location   │ Theft Vector                     │
├─────────────────────┼──────────────────────────────────┤
│  localStorage       │ XSS (document.cookie inaccessible│
│                     │ but localStorage fully readable) │
│                     │ HIGH RISK for auth tokens        │
├─────────────────────┼──────────────────────────────────┤
│  sessionStorage     │ XSS (same as localStorage)       │
│                     │ Cleared on tab close             │
├─────────────────────┼──────────────────────────────────┤
│  Cookie (no flags)  │ XSS (document.cookie readable)   │
│                     │ Network (if not Secure)          │
├─────────────────────┼──────────────────────────────────┤
│  Cookie (HttpOnly)  │ Network if no Secure flag        │
│                     │ XSS CANNOT read (JS blocked)     │
├─────────────────────┼──────────────────────────────────┤
│  Cookie (HttpOnly   │ CSRF (mitigated by SameSite)     │
│  + Secure +         │ Best option for session tokens   │
│  SameSite=Strict)   │ Very low risk if CSP configured  │
├─────────────────────┼──────────────────────────────────┤
│  In-memory only     │ Cleared on page refresh          │
│  (JS variable)      │ Safe from XSS if no serialization│
│                     │ Poor UX (lost on navigation)     │
└─────────────────────┴──────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Secure cookie configuration for session token**

```java
@Bean
public CookieSerializer cookieSerializer() {
    DefaultCookieSerializer serializer =
        new DefaultCookieSerializer();
    serializer.setCookieName("SESSION");
    serializer.setHttpOnly(true);   // no JS access
    serializer.setUseSecureCookie(true); // HTTPS only
    // SameSite=Strict: cookie NOT sent on cross-site requests
    // (blocks CSRF completely for most scenarios)
    serializer.setSameSite("Strict");
    serializer.setCookiePath("/");
    // Set max age based on your session timeout
    // 0 = session cookie (cleared when browser closes)
    serializer.setCookieMaxAge(-1);
    return serializer;
}
```

**Example - DPoP (Demonstrating Proof of Possession)**

```java
// DPoP binds access tokens to a client-held keypair
// Even if access token is stolen: useless without the key
// RFC 9449 - modern alternative to bearer tokens

// Server-side DPoP validation
public void validateDpop(String accessToken,
                           String dpopProof,
                           String httpMethod,
                           String httpUri) {
    // Parse DPoP proof (a JWT)
    // Header: {"typ":"dpop+jwt","alg":"ES256","jwk":{...}}
    // Claims: {"jti":"unique-id","htm":"POST",
    //           "htu":"https://api.example.com/resource",
    //           "iat":1234567890,"ath":"access_token_hash"}

    // Validate:
    // 1. dpopProof.jwk = the public key presented
    // 2. htm = HTTP method of this request
    // 3. htu = URL of this request
    // 4. ath = SHA256(access_token) - binds to the token
    // 5. iat is recent (anti-replay)
    // 6. jti not seen before (anti-replay)
    // If access token stolen: attacker cannot produce
    // valid DPoP proof without the private key
}
```

---

*Authentication category: ATH | Entry: ATH-046 | v5.0*