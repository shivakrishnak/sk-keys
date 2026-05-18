---
id: ATH-036
title: "Phishing-Resistant MFA"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-012, ATH-027, ATH-028, ATH-029
used_by: ATH-037, ATH-038, ATH-044, ATH-050
related: ATH-027, ATH-028, ATH-037
tags:
  - security
  - authentication
  - mfa
  - phishing-resistant
  - fido
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/authentication/phishing-resistant-mfa/
---

⚡ **TL;DR** - Most MFA (SMS OTP, TOTP, push notifications) is
phishable: a real-time relay attack captures your OTP and uses it
before it expires. Phishing-resistant MFA is cryptographically
bound to the origin URL - the key or credential will not respond
to any site other than the exact registered URL. FIDO2/WebAuthn
hardware keys and passkeys are the only NIST-approved
phishing-resistant methods. CISA mandates phishing-resistant MFA
for federal agencies (2022 directive).

---

### 📊 Entry Metadata

| #036 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-012 MFA, ATH-027 SMS OTP, ATH-028 Hardware Keys, ATH-029 TOTP | |
| **Used by:** | ATH-037, ATH-038, ATH-044, ATH-050 | |
| **Related:** | ATH-027 SMS OTP, ATH-028 Hardware Keys, ATH-037 FIDO2/WebAuthn | |

---

### 📘 Textbook Definition

Phishing-resistant MFA refers to authentication methods where
the second factor response is cryptographically bound to the
legitimate origin (registered URL), making it impossible for
an attacker to relay the response to the real site even if they
successfully phish the user. NIST SP 800-63B defines two
phishing-resistant authenticator categories: (1) hardware
cryptographic authenticators (FIDO2 security keys) and (2)
verifier impersonation-resistant authenticators (WebAuthn
platform authenticators, passkeys). Non-phishing-resistant
methods (SMS OTP, TOTP, push without number matching) are
vulnerable to real-time relay attacks and adversary-in-the-middle
(AiTM) proxy attacks.

---

### ⚙️ How It Works (Mechanism)

**Why origin binding prevents phishing:**

```
┌────────────────────────────────────────────────────────┐
│     Phishable vs Phishing-Resistant MFA                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PHISHABLE (SMS OTP, TOTP):                            │
│  1. User visits fake-bank.com (looks real)             │
│  2. Enters password + 6-digit OTP                      │
│  3. Attacker relays BOTH to real bank.com in <30s      │
│  4. bank.com validates OTP (time-window still open)    │
│  5. Attacker authenticated. Attack succeeds.           │
│                                                        │
│  PHISHING-RESISTANT (FIDO2/WebAuthn):                  │
│  1. User visits fake-bank.com                          │
│  2. Browser requests WebAuthn assertion                │
│     rpId = "fake-bank.com" (from the URL)              │
│  3. Authenticator signs for rpId=fake-bank.com         │
│     (has NO registered credential for fake-bank.com)  │
│  4. Attacker relays this to real bank.com:             │
│     rpId in assertion = "fake-bank.com"                │
│     bank.com's registered rpId = "bank.com"            │
│  5. MISMATCH: assertion rejected by bank.com           │
│  6. Attack fails. Origin binding protected the user.   │
│                                                        │
│  REQUIREMENT: phishing-resistant MFA for               │
│  - Financial services, healthcare, government          │
│  - Any service targeted by nation-state actors         │
│  - High-value accounts (crypto, exec accounts)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Enforcing phishing-resistant MFA in Okta**

```yaml
# Okta Authentication Policy: require hardware key
# (Okta FastPass or FIDO2 security key)
# Administrative UI or Okta API:

{
  "name": "High Value Access Policy",
  "conditions": {
    "app": {
      "include": ["financial-app", "admin-portal"]
    }
  },
  "rules": [{
    "name": "Require Hardware Authenticator",
    "conditions": {
      "network": {"connection": "ANYWHERE"}
    },
    "actions": {
      "appSignOn": {
        "access": "ALLOW",
        "verificationMethod": {
          "factorMode": "2FA",
          "constraints": [{
            "possession": {
              "hardwareProtection": "REQUIRED",
              "phishingResistant": "REQUIRED"
            }
          }]
        }
      }
    }
  }]
}
```

**Example - Detecting AiTM attack via token binding signals**

```java
// AiTM (Adversary in the Middle) proxy attack:
// Even with session cookie stolen after WebAuthn login,
// detect session anomalies:

@Component
public class SessionAnomalyDetector {

    @EventListener
    public void onRequest(RequestEvent event) {
        Session session = event.getSession();
        String currentIp = event.getIpAddress();
        String registeredIp = session.getInitialIpAddress();
        String currentUA = event.getUserAgent();
        String registeredUA = session.getInitialUserAgent();

        // Sudden IP change + UA change in same session
        // can indicate session cookie theft after auth
        if (!currentIp.equals(registeredIp)
                && !currentUA.equals(registeredUA)) {
            sessionService.forceReauth(session.getId());
            alertService.sendAlert("Session anomaly - "
                + "possible cookie theft: " + session.getId());
        }
    }
}
```

---

*Authentication category: ATH | Entry: ATH-036 | v5.0*