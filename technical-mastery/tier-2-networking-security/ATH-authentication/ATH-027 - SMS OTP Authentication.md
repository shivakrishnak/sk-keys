---
id: ATH-027
title: "SMS OTP Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-012, ATH-013
used_by: ATH-036, ATH-044, ATH-050
related: ATH-013, ATH-026, ATH-028
tags:
  - security
  - authentication
  - sms
  - otp
  - mfa
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/authentication/sms-otp-authentication/
---

⚡ **TL;DR** - SMS OTP (one-time password via text message) is the
most common second factor for consumer applications. But SMS is the
weakest MFA channel: SIM swap attacks (convincing the carrier to
transfer your number) give attackers your OTPs. NIST SP 800-63B
(2017) deprecated SMS OTP as an authentication channel. Use it
only when better options (TOTP app, hardware key) are not viable,
and document the risk tradeoff explicitly.

---

### 📊 Entry Metadata

| #027 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-012 MFA, ATH-013 TOTP | |
| **Used by:** | ATH-036, ATH-044, ATH-050 | |
| **Related:** | ATH-013 TOTP, ATH-026 Magic Link, ATH-028 Hardware Keys | |

---

### 📘 Textbook Definition

SMS OTP authentication delivers a short-lived (typically 6-digit,
5-10 minute) numeric code to the user's registered phone number
as a second authentication factor. The user proves physical
possession of the registered phone by entering the code. The
weakness is that the phone number is not a cryptographic identity:
phone number ownership can be transferred (SIM swap, SS7 attack)
without the user's knowledge, allowing an attacker to intercept
future OTPs and bypass SMS-based MFA.

---

### ⚙️ How It Works (Mechanism)

**SIM swap attack path:**

```
┌────────────────────────────────────────────────────────┐
│         SMS OTP: Attack Vectors                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SIM Swap (most common):                               │
│  Attacker calls carrier with social engineering        │
│  → carrier transfers victim's number to attacker SIM   │
│  → attacker receives all SMS including OTPs            │
│  Real incidents: Twitter CEO Jack Dorsey (2019),       │
│  multiple crypto exchange hacks                        │
│                                                        │
│  SS7 Protocol Vulnerability:                           │
│  SS7 (Signaling System 7) is the telecom routing       │
│  protocol. Nation-state actors can intercept SMS at    │
│  the network level. Demonstrated publicly at CCC 2014. │
│                                                        │
│  OTP Phishing:                                         │
│  Attacker creates fake bank login page                 │
│  → victim enters OTP on fake page                     │
│  → attacker relays to real bank in real time           │
│  Mitigated by: FIDO2 (cryptographically bound to       │
│  the legitimate origin)                                │
│                                                        │
│  WHEN TO USE SMS OTP:                                  │
│  - Consumer apps where TOTP is too complex for users   │
│  - Phone number already required for account recovery  │
│  - NOT for high-value targets (banking, crypto)        │
│  - NOT when SIM swap risk is elevated for target users │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - SMS OTP flow with Twilio**

```java
@Service
public class SmsOtpService {

    @Transactional
    public void sendOtp(String userId, String phoneNumber) {
        // Generate 6-digit OTP
        String otp = String.format("%06d",
            new SecureRandom().nextInt(1_000_000));
        String otpHash = sha256Hex(otp);

        // Rate limit: max 3 OTP requests per 10 min
        enforceRateLimit(userId);

        // Store hashed OTP, expire in 5 minutes
        otpRepo.save(new SmsOtp(userId, otpHash,
            Instant.now().plus(5, ChronoUnit.MINUTES)));

        // Send via Twilio Verify API (preferred over raw SMS)
        // Twilio Verify handles carrier rate limiting and
        // SIM swap detection signals
        twilioVerify.verifications()
            .create(phoneNumber, "sms");
    }

    @Transactional
    public boolean verifyOtp(String userId, String otp) {
        SmsOtp stored = otpRepo
            .findByUserIdAndUsedFalse(userId)
            .orElse(null);
        if (stored == null || stored.isExpired()) return false;
        if (!stored.getOtpHash().equals(sha256Hex(otp)))
            return false;
        stored.setUsed(true);
        otpRepo.save(stored);
        return true;
    }
}
```

**Example - BAD: predictable OTP**

```java
// BAD: math.random is not cryptographically secure
// and produces predictable sequences
String otp = String.valueOf(
    (int)(Math.random() * 1_000_000));

// BAD: 4-digit OTP (10,000 possibilities - bruteforceable)
String otp = String.format("%04d",
    new SecureRandom().nextInt(10_000));
// Without rate limiting: 10,000 tries on average to crack

// GOOD: 6-digit, cryptographically random, rate limited
String otp = String.format("%06d",
    new SecureRandom().nextInt(1_000_000));
// + max 3 wrong guesses before invalidation
// + 5 minute expiry
```

---

*Authentication category: ATH | Entry: ATH-027 | v5.0*