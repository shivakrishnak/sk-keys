---
id: ATH-020
title: "Secure Password Reset Flow"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-006, ATH-007, ATH-016, ATH-019
used_by: ATH-021, ATH-035, ATH-044
related: ATH-016, ATH-019, ATH-021
tags:
  - security
  - authentication
  - password-reset
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/authentication/secure-password-reset-flow/
---

⚡ **TL;DR** - Password reset is an authentication bypass: it proves
identity without the current password, so it must be as secure as
the credential it replaces. The secure pattern: generate a
cryptographically random one-time token, send only via email (out-of-band),
expire in 15-60 minutes, invalidate on first use, invalidate all
existing sessions on password change. Security questions are not acceptable
second factors - they are guessable from public information.

---

### 📊 Entry Metadata

| #020 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-006, ATH-007, ATH-016, ATH-019 | |
| **Used by:** | ATH-021, ATH-035, ATH-044 | |
| **Related:** | ATH-016 Error Messages, ATH-019 Password Policy, ATH-021 Enumeration | |

---

### 🔥 The Problem This Solves

**PASSWORD RESET IS AN AUTH BYPASS:**

A password reset proves "this person has access to the
registered email" - which is a weaker proof of identity
than "this person knows the account password." If the
reset flow is insecure, an attacker who can access the
email account (from a separate breach, phishing, or SIM swap)
can reset the password and take over the primary account.

Security anti-patterns in password reset:
- Reset tokens that do not expire
- Reset tokens that are reusable
- Reset tokens that are guessable (sequential, timestamp-based)
- Tokens sent in URLs (logged in server logs, referrer headers)
- Reactivating old sessions after password change

---

### 📘 Textbook Definition

A secure password reset flow authenticates the reset request
via out-of-band channel (email), provides a cryptographically
random single-use token with short expiry, validates the token
at the reset step, enforces the new password against the current
policy, invalidates the token on use, and invalidates all
existing sessions for the user after a successful password change.
The flow must also prevent account enumeration (same response
whether the email exists or not) and resist timing attacks.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            Secure Password Reset Flow                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STEP 1: User requests reset                           │
│  POST /reset-password {"email": "alice@co.com"}        │
│  Server:                                               │
│    - Look up email (but do not reveal if found)        │
│    - If found: generate token (SecureRandom 256 bits)  │
│    - Hash token (SHA-256); store hash + user_id        │
│    - Set expiry: NOW + 30 minutes                      │
│    - Send email with: /reset?token=<raw_token>         │
│  Response: ALWAYS "Check your email" (no 404)          │
│                                                        │
│  STEP 2: User clicks email link                        │
│  GET /reset?token=abc123...                            │
│  Server:                                               │
│    - Hash presented token → compare to stored hash     │
│    - Check expiry: not expired?                        │
│    - Check used: not already used?                     │
│    - If valid: show password reset form                │
│                                                        │
│  STEP 3: User submits new password                     │
│  POST /reset {"token": "...", "new_password": "..."}   │
│  Server:                                               │
│    - Re-validate token (same checks as step 2)         │
│    - Validate new password (policy check)              │
│    - Hash new password (bcrypt/Argon2)                 │
│    - Update password hash in database                  │
│    - Mark token as USED (or delete it)                 │
│    - Invalidate ALL existing sessions for this user    │
│    - (Optional: send "password changed" alert email)   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Secure reset token generation and storage**

```java
@Service
public class PasswordResetService {

    @Transactional
    public void initiateReset(String email) {
        // Always respond the same - no account enumeration
        User user = userRepo.findByEmail(email).orElse(null);
        if (user == null) {
            return; // silently exit; same response to caller
        }

        // Invalidate any existing reset tokens for this user
        resetTokenRepo.deleteByUserId(user.getId());

        // Generate cryptographically random token (256-bit)
        byte[] tokenBytes = new byte[32];
        new SecureRandom().nextBytes(tokenBytes);
        String rawToken = Base64.getUrlEncoder()
            .withoutPadding()
            .encodeToString(tokenBytes);

        // Store HASH of token (never the raw token)
        String tokenHash = sha256Hex(rawToken);
        PasswordResetToken token = new PasswordResetToken(
            user.getId(),
            tokenHash,
            Instant.now().plus(30, ChronoUnit.MINUTES) // 30m
        );
        resetTokenRepo.save(token);

        // Email contains the RAW token (user needs it)
        emailService.sendPasswordReset(
            email, rawToken);
    }

    @Transactional
    public boolean completeReset(
            String rawToken, String newPassword) {
        String tokenHash = sha256Hex(rawToken);
        PasswordResetToken token = resetTokenRepo
            .findByTokenHash(tokenHash).orElse(null);

        if (token == null
                || token.isExpired()
                || token.isUsed()) {
            return false; // invalid/expired/used
        }

        // Validate new password against policy
        passwordPolicy.validate(newPassword);

        // Update password
        User user = userRepo.findById(token.getUserId())
            .orElseThrow();
        user.setPasswordHash(
            passwordEncoder.encode(newPassword));
        userRepo.save(user);

        // Invalidate token (mark used)
        token.setUsed(true);
        resetTokenRepo.save(token);

        // Invalidate ALL active sessions for this user
        sessionStore.invalidateAllSessions(user.getId());

        return true;
    }
}
```

**Example - BAD: reset token in URL logged by servers**

```
Vulnerability:
  Token sent in URL: /reset?token=abc123
  
  This URL appears in:
  - Server access logs: "GET /reset?token=abc123"
  - Browser history
  - Referrer header (if user clicks a link from the reset page)
  - Email client's URL prefetch (some clients load links)

Fix: Use POST forms for token submission, or use
  fragment identifiers (# part is not sent to server).
  Better: POST /reset with token in request body (not URL).
  Email link GET /reset?token=... is acceptable only if:
    1. Short expiry (15-30 min)
    2. Single use (invalidate after first visit)
    3. Server logs are secured and do not retain token URLs
    4. HTTPS (TLS prevents network interception)
```

---

*Authentication category: ATH | Entry: ATH-020 | v5.0*