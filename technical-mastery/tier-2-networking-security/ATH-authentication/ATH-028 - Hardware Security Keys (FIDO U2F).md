---
id: ATH-028
title: "Hardware Security Keys (FIDO U2F)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-012, ATH-037
used_by: ATH-036, ATH-037, ATH-038
related: ATH-036, ATH-037, ATH-038
tags:
  - security
  - authentication
  - hardware-key
  - fido
  - u2f
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/authentication/hardware-security-keys-fido-u2f/
---

⚡ **TL;DR** - FIDO U2F (Universal 2nd Factor) hardware security keys
(YubiKey, Google Titan) are phishing-proof MFA. Unlike TOTP or SMS,
the key cryptographically binds its response to the origin URL -
a key registered at `bank.com` will not respond to `fake-bank.com`.
Even if an attacker tricks you into entering credentials on a fake
site, the U2F response is invalid at the real site. This origin
binding is what makes hardware keys the gold standard for high-risk
accounts.

---

### 📊 Entry Metadata

| #028 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-012 MFA, ATH-037 FIDO2 | |
| **Used by:** | ATH-036, ATH-037, ATH-038 | |
| **Related:** | ATH-036 Phishing-Resistant MFA, ATH-037 FIDO2/WebAuthn, ATH-038 Passkeys | |

---

### 📘 Textbook Definition

FIDO U2F (FIDO Alliance, 2014) is a second-factor authentication
standard using hardware security keys that perform public-key
cryptography. The key generates a key pair per relying party
(origin URL), stores the private key in tamper-resistant hardware,
and signs a server-provided challenge. The signature is valid only
for the registered origin - the key refuses to respond for any
other origin. This makes U2F phishing-proof: even if a user
navigates to a fraudulent site, the key's response cannot be used
at the legitimate site. FIDO U2F is superseded by FIDO2/WebAuthn
(ATH-037) but the core security model is identical.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            FIDO U2F Authentication Flow                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  REGISTRATION:                                         │
│  1. User plugs in YubiKey                              │
│  2. Server: send challenge + appId (origin)            │
│  3. Key: generate key pair for this origin             │
│     - Private key: stored on key, never exported       │
│     - Public key: sent to server for storage           │
│     - key_handle: opaque reference to the key pair     │
│  4. Server: store {user_id, public_key, key_handle}    │
│                                                        │
│  AUTHENTICATION:                                       │
│  1. User plugs in key (or taps NFC/Lightning key)      │
│  2. Server: send challenge + key_handle                │
│  3. Browser: check origin = registered origin          │
│     If origin mismatch: STOP (phishing protection)    │
│  4. Key: sign {challenge + origin + counter}           │
│     with private key, increment counter                │
│  5. Server verifies:                                   │
│     - Signature valid (public key)                     │
│     - Origin matches registered origin                 │
│     - Counter > last seen counter (replay protection)  │
│  6. If all pass: authenticated                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Why U2F blocks phishing**

```
Scenario: TOTP vs U2F against a phishing attack

TOTP (vulnerable):
  1. Attacker: fake-bank.com (looks identical)
  2. Victim: enters password + 6-digit TOTP code
  3. Attacker: relays credentials to real bank.com
     in real time
  4. Result: attacker authenticated. TOTP stolen.

U2F (phishing-proof):
  1. Attacker: fake-bank.com
  2. Victim: enters password, taps YubiKey
  3. Browser sends challenge to key with
     origin = "fake-bank.com"
  4. Key signs for "fake-bank.com" key pair
     (key has NO pair for fake-bank.com - registered
      only for real bank.com)
  5. Attacker relays this response to bank.com
  6. bank.com: origin mismatch - fake-bank.com ≠ bank.com
     Response INVALID. Authentication REJECTED.
  7. Attacker cannot authenticate.
```

**Example - WebAuthn assertion (modern U2F equivalent)**

```java
@RestController
public class AuthController {

    @PostMapping("/auth/webauthn/challenge")
    public AssertionRequestWrapper challenge(
            HttpSession session) {
        AssertionRequest request = relyingParty
            .startAssertion(StartAssertionOptions.builder()
                .username(Optional.empty()) // allow any user
                .build());
        session.setAttribute("webauthn-challenge", request);
        return new AssertionRequestWrapper(request);
    }

    @PostMapping("/auth/webauthn/verify")
    public AuthResponse verify(
            @RequestBody AuthenticationResponse response,
            HttpSession session) throws Exception {
        AssertionRequest savedRequest = (AssertionRequest)
            session.getAttribute("webauthn-challenge");

        AssertionResult result = relyingParty
            .finishAssertion(FinishAssertionOptions.builder()
                .request(savedRequest)
                .response(response)
                .build());
        // result.isSuccess(): signature valid, origin matches,
        // counter incremented, user handle matches
        if (!result.isSuccess()) {
            throw new AuthenticationException(
                "WebAuthn assertion failed");
        }
        return buildSession(result.getUserHandle());
    }
}
```

---

*Authentication category: ATH | Entry: ATH-028 | v5.0*