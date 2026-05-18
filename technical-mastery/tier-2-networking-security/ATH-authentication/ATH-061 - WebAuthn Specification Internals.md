---
id: ATH-061
title: "WebAuthn Specification Internals"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-037, ATH-038, ATH-040
used_by: ATH-062, ATH-063, ATH-065
related: ATH-037, ATH-038, ATH-062
tags:
  - security
  - authentication
  - webauthn
  - specification
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/authentication/webauthn-specification-internals/
---

**TL;DR:** WebAuthn (Web Authentication API, W3C standard) is
the browser/platform API for FIDO2 authentication. The spec
defines two operations: `navigator.credentials.create()` for
registration (binding a new credential to a user account) and
`navigator.credentials.get()` for authentication (asserting
an existing credential). Both return cryptographically signed
attestation/assertion objects that the server must verify. The
security properties: the private key never leaves the device
(hardware-bound), and every assertion is bound to the exact
origin (replying party ID) - making phishing impossible since
a fake domain gets a signature that the server rejects.

---

### Textbook Definition

WebAuthn is the W3C Web Authentication API specification (Level
1: 2019, Level 2: 2021, Level 3: 2023-present). It enables
strong cryptographic authentication using public-key credentials
stored in authenticators (hardware security keys, platform
authenticators like Touch ID / Face ID). Registration flow:
server generates challenge -> client calls `create()` ->
authenticator generates key pair and attestation statement
(proving the authenticator model and key generation) -> server
verifies attestation, stores public key. Authentication flow:
server generates challenge -> client calls `get()` -> authenticator
signs assertion with stored private key -> server verifies
signature against stored public key. Key security guarantee:
private key is hardware-bound and never transmitted.

---

### How It Works (Mechanism)

```
REGISTRATION:
1. Server: generate random 32-byte challenge
   Store: pendingChallenge[sessionId] = challenge
2. Browser: navigator.credentials.create({
     publicKey: {
       challenge: challenge,
       rp: {id: "example.com", name: "My App"},
       user: {id: userId, name: "alice"},
       pubKeyCredParams: [
         {type: "public-key", alg: -7}   // ES256
         {type: "public-key", alg: -257}  // RS256
       ]
     }
   })
3. Authenticator: generates key pair
   Returns: clientDataJSON, attestationObject
   clientDataJSON contains: challenge, origin, type
   attestationObject: fmt, authData, attStmt (optional)
4. Server verification:
   - Verify challenge == pendingChallenge[sessionId]
   - Verify origin == "https://example.com"
   - Verify rpIdHash == SHA-256("example.com")
   - Parse attestation: get credentialId + publicKey
   - Store: credentialId + publicKey for this user

AUTHENTICATION:
1. Server: new random challenge
2. Browser: navigator.credentials.get({
     publicKey: { challenge, rpId: "example.com",
                  allowCredentials: [credentialId] }
   })
3. Authenticator: signs assertion
   Returns: clientDataJSON, authenticatorData, signature
4. Server: verify signature(authData + hash(clientDataJSON))
   using stored public key
   Verify: challenge, origin, rpIdHash, signCount (replay)
```

---

### Code Examples

**Example - Server-side WebAuthn verification (Java)**

```java
@Service
public class WebAuthnVerifier {

    public void verifyAssertion(
            AuthenticatorAssertionResponse response,
            String sessionChallenge,
            StoredCredential storedCred) throws Exception {
        // 1. Verify client data
        ClientDataJSON clientData = parseClientData(
            response.getClientDataJSON());
        // type must be "webauthn.get"
        if (!"webauthn.get".equals(clientData.getType())) {
            throw new WebAuthnException("Invalid type");
        }
        // challenge must match server-issued challenge
        if (!Arrays.equals(
                Base64.getUrlDecoder().decode(
                    clientData.getChallenge()),
                Base64.getUrlDecoder().decode(
                    sessionChallenge))) {
            throw new WebAuthnException(
                "Challenge mismatch");
        }
        // origin must be exact match
        if (!"https://example.com".equals(
                clientData.getOrigin())) {
            throw new WebAuthnException(
                "Origin mismatch - possible phishing");
        }

        // 2. Verify authenticator data
        AuthenticatorData authData = parseAuthData(
            response.getAuthenticatorData());
        // rpIdHash must match SHA-256(rpId)
        byte[] expectedRpIdHash = MessageDigest
            .getInstance("SHA-256")
            .digest("example.com".getBytes(UTF_8));
        if (!Arrays.equals(authData.getRpIdHash(),
                expectedRpIdHash)) {
            throw new WebAuthnException("rpId mismatch");
        }
        // UP (user present) flag must be set
        if (!authData.isUserPresent()) {
            throw new WebAuthnException(
                "User not present");
        }
        // signCount: must be > stored count (anti-replay)
        if (authData.getSignCount()
                <= storedCred.getSignCount()) {
            throw new WebAuthnException(
                "Sign count replay detected");
        }

        // 3. Verify signature
        byte[] verificationData = concat(
            response.getAuthenticatorData(),
            sha256(response.getClientDataJSON()));
        PublicKey publicKey = storedCred.getPublicKey();
        Signature sig = Signature.getInstance("SHA256withECDSA");
        sig.initVerify(publicKey);
        sig.update(verificationData);
        if (!sig.verify(response.getSignature())) {
            throw new WebAuthnException(
                "Signature verification failed");
        }

        // Update sign count in storage (anti-replay)
        storedCred.setSignCount(authData.getSignCount());
        credentialRepository.save(storedCred);
    }
}
```

---

*Authentication category: ATH | Entry: ATH-061 | v5.0*