---
id: ATH-062
title: "FIDO Alliance Protocol Design Rationale"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-028, ATH-037, ATH-038, ATH-061
used_by: ATH-063, ATH-065
related: ATH-037, ATH-038, ATH-061
tags:
  - security
  - authentication
  - fido
  - protocol-design
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/authentication/fido-alliance-protocol-design-rationale/
---

**TL;DR:** The FIDO Alliance designed FIDO2 (WebAuthn + CTAP2)
to solve three problems with passwords: they are phishable
(user types into attacker-controlled form), reusable across
sites (breach at one site = breach at all), and guessable.
Key design decisions: origin binding (credentials are scoped
to a specific origin, defeating phishing), per-site key pairs
(no cross-site correlation), user verification at the device
(biometric or PIN, not transmitted), and attestation (device
can prove its authenticator model to the server, enabling
enterprise trust decisions). These are not arbitrary choices
but direct responses to the known attack surface of passwords.

---

### Textbook Definition

The FIDO Alliance (Fast IDentity Online) developed FIDO U2F
(2012), FIDO2 = WebAuthn + CTAP2 (2018), and the Passkey
spec (2022). Design goals: (1) Phishing resistance: relying
party ID binding makes credential assertions only valid for
the exact registered origin; (2) No shared secrets: server
stores only public key, not credential or hash; (3) User
verification: biometric/PIN is local to device, never transmitted;
(4) Privacy: per-site credentials, no cross-site user tracking;
(5) Attestation: authenticators can prove their model/factory
certification to enable enterprise policy (e.g., "only hardware
security keys certified to FIDO L2 are allowed"). CTAP2 is
the protocol for cross-device communication (phone as roaming
authenticator over Bluetooth/NFC).

---

### Design Rationale Summary

```
PROBLEM: Passwords are phishable
FIDO SOLUTION: Origin binding
How: clientDataJSON.origin is set by the browser to the
     ACTUAL current origin. Attacker on fake-bank.com
     gets assertions with origin=fake-bank.com, not
     origin=bank.com. Server rejects: origin mismatch.
Cannot be spoofed: browser sets origin, not JS code.

PROBLEM: Password reuse across sites = breach amplification
FIDO SOLUTION: Per-site key pairs
How: Each registration creates a new key pair per RP.
     Credential for bank.com != credential for email.com
     Even if bank.com leaks public keys: email.com safe

PROBLEM: Server breach exposes credentials
FIDO SOLUTION: Server stores only public key
How: Private key never leaves the authenticator hardware.
     Server has only public key. Breach: public key leaked.
     Attacker cannot authenticate: needs private key.

PROBLEM: Biometrics transmitted = permanent breach
FIDO SOLUTION: User verification is local
How: Biometric/PIN never leaves the authenticator.
     Device verifies, then uses private key to sign.
     Server receives assertion, not biometric.
```

---

### Code Examples

**Example - Attestation verification (enterprise policy)**

```java
// Enterprise: only allow authenticators certified FIDO L2
// FIDO MDS (Metadata Service) provides authenticator info
@Service
public class AttestationPolicyService {

    // FIDO Metadata Service (MDS3) - authenticator catalog
    private final FidoMetadataService mds;

    public void verifyAttestationPolicy(
            String aaguid,  // authenticator model ID
            AttestationStatement attStmt) {
        // Look up authenticator in FIDO MDS
        MetadataStatement metadata =
            mds.findByAaguid(UUID.fromString(aaguid));
        if (metadata == null) {
            // Unknown authenticator model
            // Policy: reject unknown authenticators
            throw new PolicyViolationException(
                "Authenticator model not in FIDO MDS");
        }
        // Check: is this authenticator FIDO L2 certified?
        boolean isCertified = metadata
            .getStatusReports()
            .stream()
            .anyMatch(report ->
                AuthenticatorStatus.FIDO_CERTIFIED_L2
                    .equals(report.getStatus()));
        if (!isCertified) {
            throw new PolicyViolationException(
                "Authenticator " + aaguid +
                " is not FIDO L2 certified. " +
                "Enterprise policy requires L2.");
        }
        // Authenticator meets policy
    }
}
// Use case: enterprise "no software authenticators" policy
// AAGUID identifies model: "YubiKey 5C NFC" vs "platform"
// Policy allows hardware keys, denies platform/software
```

---

*Authentication category: ATH | Entry: ATH-062 | v5.0*