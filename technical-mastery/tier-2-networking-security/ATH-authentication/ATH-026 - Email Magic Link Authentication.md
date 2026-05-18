---
id: ATH-026
title: "Email Magic Link Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-020
used_by: ATH-044, ATH-050
related: ATH-020, ATH-025, ATH-027
tags:
  - security
  - authentication
  - magic-link
  - passwordless
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/authentication/email-magic-link-authentication/
---

⚡ **TL;DR** - Email magic links are passwordless authentication:
the user enters their email, receives a one-click sign-in link,
and the link proves email ownership. Security requirements mirror
password reset: cryptographically random token, short expiry (15-30
minutes), single-use, HTTPS only. The vulnerability pattern is also
the same: if the email account is compromised, so is the application
account. Magic links are convenient but inherit the security of email.

---

### 📊 Entry Metadata

| #026 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-020 Secure Password Reset | |
| **Used by:** | ATH-044, ATH-050 | |
| **Related:** | ATH-020 Password Reset, ATH-025 Social Login, ATH-027 SMS OTP | |

---

### 📘 Textbook Definition

Email magic link authentication is a passwordless authentication
method where users verify their identity by clicking a unique,
time-limited link sent to their email address. The link contains
a cryptographically random token; clicking it proves control of
the email inbox. The security model is: trust in the email channel
as the second factor of identity. Implementation requirements:
random token generation (≥128 bits), short token validity (15-30
minutes), single-use enforcement, HTTPS-only links, and rate
limiting on link issuance.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            Magic Link Authentication Flow              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. User enters email: alice@example.com               │
│  2. Server: generate 32-byte SecureRandom token        │
│     Store: hash(token), user_id, expiry=now+15min      │
│  3. Email: https://app.com/auth?token=<raw_token>      │
│     Subject: "Your sign-in link (expires in 15 min)"   │
│  4. User clicks link                                   │
│  5. Server: hash(presented token) == stored hash?      │
│     AND current time < expiry?                         │
│     AND not already used?                              │
│  6. ALL YES: establish session, delete token           │
│     ANY NO: return 401 "Link invalid or expired"       │
│                                                        │
│  RATE LIMITING:                                        │
│  - Max 3 magic link requests per email per 15 minutes  │
│  - Prevents email flooding attacks (inbox spam)        │
│                                                        │
│  SECURITY BOUNDARY:                                    │
│  Magic link is as secure as the email account.         │
│  If email is compromised: app account is compromised.  │
│  For sensitive apps: pair with a second factor.        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Magic link generation and verification**

```java
@Service
public class MagicLinkService {

    @Transactional
    public void sendMagicLink(String email) {
        User user = userRepo.findByEmail(email).orElse(null);
        // Always respond "check email" even if user not found
        // (prevents account enumeration)
        if (user == null) return;

        // Rate limit: max 3 links per 15 minutes
        long recentLinks = magicLinkRepo
            .countByUserIdAndCreatedAtAfter(
                user.getId(),
                Instant.now().minus(15, ChronoUnit.MINUTES));
        if (recentLinks >= 3) {
            return; // silently rate-limit (no error reveal)
        }

        // Invalidate any existing unused links for this user
        magicLinkRepo.deleteByUserId(user.getId());

        // Generate token
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        String rawToken = Base64.getUrlEncoder()
            .withoutPadding().encodeToString(bytes);
        String tokenHash = sha256Hex(rawToken);

        magicLinkRepo.save(new MagicLinkToken(
            user.getId(), tokenHash,
            Instant.now().plus(15, ChronoUnit.MINUTES)));

        emailService.sendMagicLink(email, rawToken);
    }

    @Transactional
    public Optional<User> verifyMagicLink(String rawToken) {
        String tokenHash = sha256Hex(rawToken);
        MagicLinkToken link = magicLinkRepo
            .findByTokenHash(tokenHash)
            .orElse(null);

        if (link == null || link.isExpired()
                || link.isUsed()) {
            return Optional.empty();
        }

        link.setUsed(true);
        magicLinkRepo.save(link);
        return userRepo.findById(link.getUserId());
    }
}
```

**Example - BAD: predictable token**

```java
// BAD: timestamp-based token (predictable)
String token = String.valueOf(System.currentTimeMillis());
// An attacker who knows the approximate request time
// can brute-force the token in milliseconds

// BAD: user email as token
String token = Base64.encode(user.getEmail());
// Trivially guessable if you know the target email

// GOOD: cryptographically random, unpredictable
byte[] bytes = new byte[32]; // 256-bit entropy
new SecureRandom().nextBytes(bytes);
String token = Base64.getUrlEncoder()
    .withoutPadding().encodeToString(bytes);
// Brute force infeasible: 2^256 possible tokens
```

---

*Authentication category: ATH | Entry: ATH-026 | v5.0*