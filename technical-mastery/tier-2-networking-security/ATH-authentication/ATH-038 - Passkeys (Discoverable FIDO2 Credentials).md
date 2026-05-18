---
id: ATH-038
title: "Passkeys (Discoverable FIDO2 Credentials)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-037
used_by: ATH-056, ATH-060, ATH-062, ATH-065
related: ATH-037, ATH-036, ATH-061
tags:
  - security
  - authentication
  - passkeys
  - fido2
  - passwordless
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/authentication/passkeys-discoverable-fido2-credentials/
---

⚡ **TL;DR** - Passkeys are FIDO2 credentials stored in the device's
secure enclave and synchronized via the platform's cloud (iCloud
Keychain, Google Password Manager, Windows Hello cloud). Unlike
hardware security keys (tied to one physical device), passkeys roam
across your devices. From a user perspective: no password, tap Face
ID or fingerprint, done. Phishing-proof because credentials are
origin-bound. The industry is converging on passkeys as the
password replacement.

---

### 📊 Entry Metadata

| #038 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-037 FIDO2/WebAuthn | |
| **Used by:** | ATH-056, ATH-060, ATH-062, ATH-065 | |
| **Related:** | ATH-037 FIDO2, ATH-036 Phishing-Resistant MFA, ATH-061 WebAuthn Internals | |

---

### 📘 Textbook Definition

Passkeys are a FIDO2 implementation using discoverable credentials
(resident keys) that are synchronized across devices via platform
cloud services. A passkey is a private key stored in the device's
secure hardware enclave and backed up (encrypted) to the user's
cloud account (Apple iCloud Keychain, Google Password Manager,
Microsoft account). Passkeys enable sign-in without a password:
the user verifies identity via biometrics or device PIN, the
authenticator signs the server's challenge, and authentication
completes. Passkeys are phishing-resistant (origin-bound),
multi-device (synced), and resistant to server-side breaches
(server stores only public keys).

---

### ⚙️ How It Works (Mechanism)

**Passkey vs hardware key vs password:**

```
┌────────────────────────────────────────────────────────┐
│         Passkey Comparison                             │
├──────────────────┬────────────────┬────────────────────┤
│  Property        │ Password       │ Passkey            │
├──────────────────┼────────────────┼────────────────────┤
│  Phishing-proof  │ No             │ Yes (origin-bound) │
│  Multi-device    │ Yes (shared)   │ Yes (synced key)   │
│  Server breach   │ Hashes stolen  │ Public key only    │
│  Lost device     │ N/A            │ Restore from cloud │
│  User experience │ Type password  │ Touch biometric    │
│  UX friction     │ Medium         │ Very low           │
│  Org control     │ Policy-managed │ Sync depends on OS │
├──────────────────┼────────────────┼────────────────────┤
│  Hardware Key    │ N/A            │ Hardware-only      │
│  + Passkey       │                │ No sync, 1 device  │
│  Sync            │ N/A            │ Never synced       │
│  Highest sec     │ N/A            │ Yes (for admin)    │
└──────────────────┴────────────────┴────────────────────┘

SYNC SECURITY NOTE:
Passkeys in iCloud Keychain are encrypted with the user's
iCloud account password + device passcode. Apple cannot
decrypt them (client-side encryption). Same for Google and
Microsoft. Enterprise concern: employee personal account sync
may not meet org security requirements -> use enterprise
passkeys (YubiKey Enterprise, device-bound only policies).
```

---

### 💻 Code Examples

**Example - Enabling passkey creation in WebAuthn**

```java
// The key difference between hardware key and passkey:
// residentKey = REQUIRED (discoverable credential)
// Hardware key: residentKey = DISCOURAGED (device-bound)
// Passkey: residentKey = REQUIRED (synced across devices)

PublicKeyCredentialCreationOptions passkeyOptions =
    relyingParty.startRegistration(
        StartRegistrationOptions.builder()
            .user(UserIdentity.builder()
                .name(username)
                .displayName(displayName)
                .id(userHandle)
                .build())
            .authenticatorSelection(
                AuthenticatorSelectionCriteria.builder()
                    // REQUIRED = passkey (discoverable)
                    .residentKey(
                        ResidentKeyRequirement.REQUIRED)
                    // Prefer platform (built-in) authenticator
                    .authenticatorAttachment(
                        AuthenticatorAttachment.PLATFORM)
                    .userVerification(
                        UserVerificationRequirement.REQUIRED)
                    .build())
            .build());
```

**Example - Conditional UI for passkey autofill**

```javascript
// Modern passkey UX: conditional mediation
// Shows saved passkey in browser's autofill dropdown
// (like saved passwords but phishing-proof)
if (PublicKeyCredential
        .isConditionalMediationAvailable
        && await PublicKeyCredential
            .isConditionalMediationAvailable()) {
    const credential = await navigator.credentials.get({
        mediation: "conditional", // autofill trigger
        publicKey: {
            challenge: serverChallenge,
            rpId: "app.example.com",
            userVerification: "preferred"
        }
    });
    // User sees their passkey in the username field dropdown
    // No explicit "use passkey" button needed
    await submitCredential(credential);
}
```

---

*Authentication category: ATH | Entry: ATH-038 | v5.0*