---
id: ATH-033
title: "PKCE for Mobile and SPA Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-022, ATH-032
used_by: ATH-047, ATH-048, ATH-053
related: ATH-022, ATH-032, ATH-046
tags:
  - security
  - authentication
  - pkce
  - oauth
  - spa
  - mobile
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/authentication/pkce-for-mobile-and-spa-authentication/
---

⚡ **TL;DR** - PKCE (Proof Key for Code Exchange, RFC 7636) prevents
authorization code interception attacks in public clients (mobile
apps, SPAs) that cannot store a client secret safely. Without PKCE,
a malicious app on the same device can intercept the authorization
code redirect and exchange it for tokens. PKCE adds a one-time
cryptographic challenge: only the client that started the flow can
complete it. PKCE is now required for all OAuth 2.0 clients
(RFC 9700, 2025), including server-side clients.

---

### 📊 Entry Metadata

| #033 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-022 OIDC, ATH-032 Refresh Tokens | |
| **Used by:** | ATH-047, ATH-048, ATH-053 | |
| **Related:** | ATH-022 OIDC, ATH-032 Refresh, ATH-046 Token Theft | |

---

### 📘 Textbook Definition

PKCE (Proof Key for Code Exchange, RFC 7636) is an extension to
OAuth 2.0 Authorization Code flow that protects against
authorization code interception attacks. PKCE requires the
client to generate a cryptographically random `code_verifier`
before starting the flow, derive a `code_challenge` from it
(SHA-256), and include the challenge in the authorization
request. The server stores the challenge. When the client
exchanges the authorization code for tokens, it presents the
original `code_verifier`; the server verifies that
SHA-256(verifier) == stored challenge. Only the client that
started the flow knows the verifier.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            PKCE Flow                                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Client generates:                                  │
│     code_verifier = 32 random bytes (base64url)        │
│     code_challenge = base64url(SHA-256(code_verifier)) │
│     code_challenge_method = "S256"                     │
│                                                        │
│  2. Authorization request:                             │
│     GET /authorize?                                    │
│       ...&code_challenge=ABC123                        │
│          &code_challenge_method=S256                   │
│  3. Server: store code_challenge with auth code        │
│                                                        │
│  4. Auth code issued: GET /callback?code=XYZCODE       │
│                                                        │
│  Without PKCE:                                         │
│  Malicious app intercepts XYZCODE redirect             │
│  POST /token {code: XYZCODE, client_id: malicious}     │
│  Server: issues tokens to attacker                     │
│                                                        │
│  With PKCE:                                            │
│  Malicious app intercepts XYZCODE redirect             │
│  POST /token {code: XYZCODE, code_verifier: ???}       │
│  Attacker does not know code_verifier: REJECTED        │
│  Only the original client knows verifier               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - PKCE generation (Java)**

```java
public class PkceGenerator {

    public static PkceChallenge generate() throws Exception {
        // Generate 32-byte random verifier (43-128 chars base64)
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        String codeVerifier = Base64.getUrlEncoder()
            .withoutPadding().encodeToString(bytes);

        // Derive challenge: BASE64URL(SHA256(verifier))
        byte[] digest = MessageDigest.getInstance("SHA-256")
            .digest(codeVerifier.getBytes(
                StandardCharsets.US_ASCII));
        String codeChallenge = Base64.getUrlEncoder()
            .withoutPadding().encodeToString(digest);

        return new PkceChallenge(codeVerifier, codeChallenge);
    }
}

// Usage:
PkceChallenge pkce = PkceGenerator.generate();
// Store pkce.codeVerifier() in session (not accessible to other apps)
// Include pkce.codeChallenge() in authorization URL
// On callback: include pkce.codeVerifier() in token exchange
```

**Example - BAD: using plain (no hash) challenge method**

```java
// BAD: code_challenge_method=plain
// challenge = verifier (no hashing)
// Attacker intercepts the authorization request URL
// -> extracts code_challenge
// -> code_challenge == code_verifier (plain mode)
// -> can exchange the code themselves

// Authorization URL contains:
// &code_challenge=the_verifier_itself
// &code_challenge_method=plain
// Attacker reads the URL -> has the verifier

// GOOD: always use S256 method
// &code_challenge=BASE64URL(SHA256(verifier))
// &code_challenge_method=S256
// Attacker reads URL -> has the challenge (hash)
// Cannot reverse SHA-256 to get the verifier
```

---

*Authentication category: ATH | Entry: ATH-033 | v5.0*