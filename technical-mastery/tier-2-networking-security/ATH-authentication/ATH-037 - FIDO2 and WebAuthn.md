---
id: ATH-037
title: "FIDO2 and WebAuthn"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-028, ATH-036
used_by: ATH-038, ATH-053, ATH-056, ATH-061, ATH-062
related: ATH-028, ATH-036, ATH-038
tags:
  - security
  - authentication
  - fido2
  - webauthn
  - passkey
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/authentication/fido2-and-webauthn/
---

⚡ **TL;DR** - FIDO2 is the overarching standard; WebAuthn is the W3C
browser API. Together they enable passwordless, phishing-resistant
authentication using public-key cryptography - either on a hardware
key (roaming authenticator: YubiKey) or on-device (platform
authenticator: Touch ID, Windows Hello, becoming passkeys). The
browser/OS handles the cryptographic ceremony; your application
only receives a signed assertion. No shared secrets, no passwords
to breach.

---

### 📊 Entry Metadata

| #037 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-028 Hardware Keys, ATH-036 Phishing-Resistant MFA | |
| **Used by:** | ATH-038, ATH-053, ATH-056, ATH-061, ATH-062 | |
| **Related:** | ATH-028 U2F, ATH-036 Phishing-Resistant MFA, ATH-038 Passkeys | |

---

### 📘 Textbook Definition

FIDO2 (Fast IDentity Online 2) is a set of specifications
comprising WebAuthn (W3C Web Authentication API) and CTAP2
(Client to Authenticator Protocol). WebAuthn enables web
applications to use public-key cryptography for authentication.
During registration, the authenticator generates an asymmetric
key pair; the private key never leaves the authenticator. During
authentication, the server sends a challenge; the authenticator
signs it with the private key along with the rpId (origin hash).
The browser verifies the origin binding before invoking the
authenticator. The server verifies the signature using the
stored public key.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            WebAuthn Registration + Authentication      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  REGISTRATION:                                         │
│  1. Server: generate challenge, rpId=origin domain     │
│  2. Browser: calls navigator.credentials.create()     │
│  3. OS/hardware: prompts user (biometric, PIN, tap)    │
│  4. Authenticator: generates key pair PUB/PRIV         │
│     for (rpId + user handle)                           │
│     PRIV never leaves the authenticator               │
│  5. Returns: PUB, credentialId, attestation            │
│  6. Server: verify attestation, store PUB + credId     │
│                                                        │
│  AUTHENTICATION:                                       │
│  1. Server: generate new random challenge              │
│  2. Browser: calls navigator.credentials.get()         │
│  3. Authenticator: sign(challenge + rpId + counter)    │
│     using PRIV for this rpId                           │
│  4. Returns: assertion (signature + clientDataJSON)    │
│  5. Server: verify signature with stored PUB           │
│     verify rpId matches expected origin                │
│     verify counter > previous counter                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - WebAuthn registration with java-webauthn-server**

```java
@RestController
public class WebAuthnController {

    @Autowired RelyingParty relyingParty;
    @Autowired CredentialRepository credRepo;

    @PostMapping("/webauthn/register/start")
    public PublicKeyCredentialCreationOptions startRegistration(
            @RequestParam String username,
            HttpSession session) {
        PublicKeyCredentialCreationOptions options =
            relyingParty.startRegistration(
                StartRegistrationOptions.builder()
                    .user(UserIdentity.builder()
                        .name(username)
                        .displayName(username)
                        .id(new ByteArray(generateUserId()))
                        .build())
                    .authenticatorSelection(
                        AuthenticatorSelectionCriteria.builder()
                            .residentKey(ResidentKeyRequirement
                                .PREFERRED) // for passkeys
                            .userVerification(
                                UserVerificationRequirement
                                .PREFERRED)
                            .build())
                    .build());
        session.setAttribute("reg-request", options);
        return options;
    }

    @PostMapping("/webauthn/register/finish")
    public String finishRegistration(
            @RequestBody PublicKeyCredential<
                AuthenticatorAttestationResponse,
                ClientRegistrationExtensionOutputs> credential,
            HttpSession session) throws Exception {
        PublicKeyCredentialCreationOptions saved =
            (PublicKeyCredentialCreationOptions)
            session.getAttribute("reg-request");
        RegistrationResult result = relyingParty
            .finishRegistration(FinishRegistrationOptions
                .builder()
                .request(saved)
                .response(credential)
                .build());
        credRepo.save(result);
        return "Registered";
    }
}
```

---

*Authentication category: ATH | Entry: ATH-037 | v5.0*