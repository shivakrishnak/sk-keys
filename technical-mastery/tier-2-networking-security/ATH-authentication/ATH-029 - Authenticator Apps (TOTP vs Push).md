---
id: ATH-029
title: "Authenticator Apps (TOTP vs Push)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-013, ATH-027
used_by: ATH-036, ATH-044
related: ATH-013, ATH-027, ATH-028
tags:
  - security
  - authentication
  - totp
  - push-mfa
  - authenticator
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/authentication/authenticator-apps-totp-vs-push/
---

⚡ **TL;DR** - Authenticator apps come in two models: TOTP (Time-based
OTP - the 6-digit rotating code from Google Authenticator) and push
notifications (Duo, Okta Verify - "Tap to approve"). TOTP works
offline and is phishing-susceptible. Push is online-only but can be
bypassed by MFA fatigue attacks (bombarding with approve requests
until the user clicks by mistake). Pick based on threat model,
and implement MFA fatigue protection for push: number matching
or location context.

---

### 📊 Entry Metadata

| #029 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-013 TOTP, ATH-027 SMS OTP | |
| **Used by:** | ATH-036, ATH-044 | |
| **Related:** | ATH-013 TOTP, ATH-027 SMS OTP, ATH-028 Hardware Keys | |

---

### 📘 Textbook Definition

Authenticator apps implement two distinct MFA mechanisms. TOTP
(RFC 6238) generates time-synchronized one-time passwords using
a shared secret and the current time; it works offline and
requires the user to type the 6-digit code. Push MFA (Duo, Okta
Verify, Microsoft Authenticator) delivers a push notification to
the user's phone requiring an explicit approval tap; it requires
internet connectivity and an active registration. Both are stronger
than SMS OTP. Push is more user-friendly but vulnerable to MFA
fatigue attacks; TOTP is more resilient but also phishable via
real-time relay.

---

### ⚙️ How It Works (Mechanism)

**TOTP vs Push comparison:**

```
┌──────────────────────────────────────────────────────────────────┐
│               TOTP vs Push Authentication                        │
├────────────────────────┬─────────────────────────────────────────┤
│  TOTP (Google Auth)    │  Push (Duo, Okta Verify)                │
├────────────────────────┼─────────────────────────────────────────┤
│  Works offline         │  Requires internet + active push        │
│  Shared secret         │  Private key on device                  │
│  User types 6 digits   │  User taps Approve/Deny                 │
│  30-second window      │  Push expires (e.g., 30-120s)           │
│  Phishable (relay)     │  Phishable if no number matching        │
│  MFA fatigue: N/A      │  MFA fatigue: YES (must mitigate)       │
│  Backup: recovery codes│  Backup: TOTP + recovery codes          │
│  Open standard RFC6238 │  Vendor-specific (Duo, Okta)            │
└────────────────────────┴─────────────────────────────────────────┘

MFA Fatigue Attack (Push):
  Attacker has stolen username + password
  Attacker sends 50+ push notifications at 2AM
  Victim, half asleep: taps Approve to stop notifications
  Attacker: authenticated

Mitigations (use at least one):
  Number Matching: push shows "Enter code 47 from your app"
  → attacker cannot tell victim what code to enter
  Location/IP context: push shows "Login from Kyiv, Ukraine"
  → victim rejects unusual location
  Rate limiting: block after 3 denied pushes in 30 min
```

---

### 💻 Code Examples

**Example - Enabling number matching in Okta push**

```yaml
# Okta Admin API - require number matching on push
# (disables pure one-tap approval)
PUT /api/v1/authenticators/{authenticatorId}/policies
{
  "settings": {
    "userVerification": "REQUIRED",
    "compliance": {
      "fips": false
    }
  }
}
```

**Example - TOTP backup code handling**

```java
@Service
public class TotpService {

    public List<String> generateBackupCodes(String userId) {
        List<String> codes = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            byte[] bytes = new byte[5];
            new SecureRandom().nextBytes(bytes);
            // Format as XXXXX-XXXXX (10 hex chars)
            String code = String.format("%010X",
                new BigInteger(1, bytes));
            codes.add(
                code.substring(0, 5) + "-"
                + code.substring(5));
        }
        // Store HASHED backup codes
        List<String> hashed = codes.stream()
            .map(this::sha256Hex)
            .collect(Collectors.toList());
        backupCodeRepo.save(userId, hashed);
        // Return plain codes ONCE for user to store
        return codes;
    }

    public boolean redeemBackupCode(String userId,
                                     String inputCode) {
        String hash = sha256Hex(
            inputCode.replaceAll("-", ""));
        Optional<BackupCode> found = backupCodeRepo
            .findUnusedByUserAndHash(userId, hash);
        if (found.isPresent()) {
            found.get().setUsed(true);
            backupCodeRepo.save(found.get());
            return true;
        }
        return false;
    }
}
```

---

*Authentication category: ATH | Entry: ATH-029 | v5.0*