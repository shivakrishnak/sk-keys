---
id: ATH-013
title: "TOTP (Time-Based One-Time Password)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-012
used_by: ATH-029, ATH-036
related: ATH-012, ATH-027, ATH-029
tags:
  - security
  - authentication
  - totp
  - otp
  - mfa
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/authentication/totp-time-based-one-time-password/
---

⚡ **TL;DR** - TOTP (RFC 6238) generates a new 6-digit code every
30 seconds by computing HMAC-SHA1 of a shared secret and the current
Unix timestamp divided by 30. The user and server independently
compute the same value without network communication. TOTP codes are
ephemeral (30s lifetime) and single-use - even capturing the code
during transmission cannot be replayed after the window closes.

---

### 📊 Entry Metadata

| #013 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-012 MFA Basics | |
| **Used by:** | ATH-029, ATH-036 | |
| **Related:** | ATH-012 MFA, ATH-027 SMS OTP, ATH-029 Auth Apps | |

---

### 📘 Textbook Definition

TOTP (Time-Based One-Time Password, RFC 6238) is an MFA
mechanism where a shared secret is provisioned between the
authenticator app and the authentication server at enrollment.
At each 30-second interval, both independently compute:
`TOTP = HOTP(secret, floor(Unix_time / 30))`, where HOTP
is HMAC-based OTP (RFC 4226). The resulting 6-digit code
matches for that 30-second window and is discarded after use.
The algorithm requires no network communication during code
generation - only the shared secret and current time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Both your phone and the server independently compute the
same rotating code from a shared secret and the time.

**The algorithm (simplified):**

```
shared_secret = (set during QR code scan at enrollment)
time_step     = floor(unix_timestamp / 30)  // changes every 30s

code = HMAC-SHA1(shared_secret, time_step)
       → truncate to 6 digits

Your phone computes this.
The server computes this.
They match if: same secret + same time window.
No network call needed to generate the code.
```

**One analogy:**
> A combination lock where the combination changes every
> 30 seconds based on a synchronized clock. You and the
> bank both have the same locked-in algorithm. You compute
> the combination; the bank computes it; they match.
> No one needs to tell anyone the combination - it is
> derived from shared information.

---

### ⚙️ How It Works (Mechanism)

**Enrollment:**

```
┌────────────────────────────────────────────────────────┐
│                TOTP Lifecycle                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ENROLLMENT:                                           │
│  1. Server generates a random 160-bit secret           │
│  2. Server encodes as Base32, creates QR code:         │
│     otpauth://totp/Service:alice@co?                   │
│       secret=JBSWY3DPEHPK3PXP&issuer=Service          │
│  3. User scans QR code with Google Authenticator,      │
│     Microsoft Authenticator, Authy, etc.               │
│  4. Server stores secret (encrypted) for this user     │
│                                                        │
│  VERIFICATION (every login):                           │
│  1. User opens authenticator app                       │
│  2. App displays 6-digit code (computed from secret    │
│     + current time window)                             │
│  3. User enters code                                   │
│  4. Server computes same code (same secret + time)     │
│  5. Match? → second factor passes                      │
│                                                        │
│  WHY IT IS SECURE:                                     │
│  - Secret never transmitted after enrollment           │
│  - Code expires in ≤30 seconds (usually 60 with        │
│    ±1 window tolerance)                                │
│  - Code is single-use (server tracks used codes)       │
│  - Offline generation (no network = no interception)   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - TOTP verification with Google Authenticator library**

```java
import dev.samstevens.totp.code.*;
import dev.samstevens.totp.secret.DefaultSecretGenerator;
import dev.samstevens.totp.time.SystemTimeProvider;

@Service
public class TotpService {

    private final CodeVerifier verifier;
    private final DefaultSecretGenerator secretGenerator;

    public TotpService() {
        TimeProvider timeProvider = new SystemTimeProvider();
        CodeGenerator codeGenerator =
            new DefaultCodeGenerator(); // HMAC-SHA1, 6 digits
        // Allow ±1 time step for clock skew (30s tolerance)
        this.verifier = new DefaultCodeVerifier(
            codeGenerator, timeProvider);
        ((DefaultCodeVerifier) this.verifier)
            .setTimePeriod(30);     // 30-second windows
        ((DefaultCodeVerifier) this.verifier)
            .setAllowedTimePeriodDiscrepancy(1);
        this.secretGenerator = new DefaultSecretGenerator();
    }

    public String generateSecret() {
        return secretGenerator.generate(); // 320-bit secret
    }

    public boolean verify(String secret, String userCode) {
        return verifier.isValidCode(secret, userCode);
    }
}
```

**Example - BAD vs GOOD: not tracking used codes**

```java
// BAD: verify only signature, not whether code was used
public boolean verifyTotp(String secret, String code) {
    return totp.isValidCode(secret, code);
    // Problem: the same 6-digit code can be replayed
    // within the 30-second window by a MITM attacker
    // who captures it from an active phishing session
}

// GOOD: mark code as used; reject replays
public boolean verifyTotp(
        String userId, String secret, String code) {
    if (!totp.isValidCode(secret, code)) return false;

    // Prevent replay within the same time window
    String useKey = "totp_used:" + userId + ":" + code;
    // Redis SET with 60s TTL (covers both ±1 windows)
    Boolean isNew = redis.setIfAbsent(useKey, "1", 60,
        TimeUnit.SECONDS);
    return Boolean.TRUE.equals(isNew);
    // Returns false if this exact code was already used
}
```

**Example - FAILURE: TOTP secret stored in plaintext**

```
Finding in a security audit:
  totp_secrets table:
    user_id | secret               
    42      | JBSWY3DPEHPK3PXP     (Base32 plaintext)
    43      | MFRA4MBRGI4DS3TH     (Base32 plaintext)

  DB breach = all TOTP secrets compromised.
  Attacker can generate valid TOTP codes for any user
  indefinitely (secret does not expire).

Fix:
  Encrypt TOTP secrets at rest using a KMS-managed key.
  Store: AES-GCM encrypt(secret) using per-tenant key.
  Decrypt only at verification time in memory.
  Key rotation invalidates secrets even if DB is breached.
```

---

*Authentication category: ATH | Entry: ATH-013 | v5.0*