---
id: ATH-064
title: "Post-Quantum Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-040, ATH-045, ATH-061, ATH-063
used_by: ATH-065
related: ATH-045, ATH-063, ATH-065
tags:
  - security
  - authentication
  - post-quantum
  - cryptography
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/authentication/post-quantum-authentication/
---

**TL;DR:** Quantum computers running Shor's algorithm will break
RSA, ECDSA, and Diffie-Hellman - the cryptographic foundations
of JWT (RS256/ES256), TLS certificates, and public-key-based
authentication. NIST finalized post-quantum cryptography (PQC)
standards in 2024: ML-DSA (CRYSTALS-Dilithium) for signatures,
ML-KEM for key exchange. Authentication systems relying on RS256
JWTs, ECDSA certificate chains, or FIDO2 ECDSA keys must plan
migrations. The timeline: "harvest now, decrypt later" attacks
make migration urgent even before quantum computers exist.

---

### Textbook Definition

Post-quantum authentication replaces classical public-key
cryptographic algorithms (RSA, ECDSA, ECDH) with lattice-based
or other quantum-resistant algorithms. The threat: Shor's
algorithm (1994) can factorize large integers and solve discrete
logarithm problems in polynomial time on a quantum computer.
This breaks RSA (integer factorization), ECDSA, and ECDH
(elliptic curve discrete logarithm). Authentication systems
that are affected: JWT RS256/ES256 token signatures, TLS
client certificates (ECDSA/RSA), FIDO2 ES256 public keys,
SSH RSA/ECDSA keys, and SAML signatures. NIST PQC standards
(2024): FIPS 204 (ML-DSA, signature), FIPS 203 (ML-KEM,
key encapsulation), FIPS 205 (SLH-DSA, stateless hash-based).

---

### How It Works (Mechanism)

```
THREAT TIMELINE:
"Harvest now, decrypt later" (HNDL) attacks:
  Adversary records encrypted TLS sessions today
  When quantum computer available: decrypt all stored data
  Authentication tokens from today: breakable tomorrow
  This makes migration urgent NOW, not when QC exists

AFFECTED AUTHENTICATION SYSTEMS:
System               Algorithm        PQC Replacement
JWT (RS256)          RSA-2048 sign    ML-DSA (Dilithium)
JWT (ES256)          P-256 ECDSA      ML-DSA or SLH-DSA
TLS Certs            RSA/ECDSA        ML-DSA + hybrid TLS
FIDO2 (ES256)        P-256 ECDSA      Working group in FIDO
SSH keys             RSA/ECDSA        ssh-ed25519-dilithium
mTLS certs           ECDSA P-256      ML-DSA certs (hybrid)
SAML XML sig         RSA-2048         ML-DSA (FIPS 204)

MIGRATION STRATEGY:
Phase 1 (now): inventory all authentication systems
  What algorithms? Where are keys stored?
Phase 2: hybrid crypto (both classical + PQC)
  JWT: dual-signed (RS256 + ML-DSA)
  TLS: hybrid key exchange (X25519 + ML-KEM)
  Accept both: verifiers accept either signature
Phase 3: drop classical (after all verifiers upgraded)
  Full PQC: ML-DSA signatures only
Phase 4: update key management for PQC key sizes
  ML-DSA keys: ~1300 bytes (vs 32 bytes for P-256)
  Signature: ~2700 bytes (vs 64 bytes for ES256)
  JWT size increase: significant, cache accordingly
```

---

### Code Examples

**Example - Hybrid JWT migration approach (conceptual)**

```java
// Hybrid JWT: signed with BOTH classical (ES256)
// AND post-quantum (ML-DSA) for migration period
// Verifiers can accept either signature

// Current ES256 JWT header:
// {"alg":"ES256","typ":"JWT"}

// Hybrid JWT header (conceptual, not standardized yet):
// {"alg":"ES256+ML-DSA","typ":"JWT"}
// Body: standard claims
// Signature: concat(ES256_sig, ML-DSA_sig)

// Migration plan for JWT-based systems:
// Step 1: Generate ML-DSA key pair alongside existing EC key
//         Store both private keys in HSM/secrets manager
// Step 2: Issue hybrid-signed JWTs
//         Verifiers that know only ES256: still work
//         Verifiers that know ML-DSA: can verify PQC sig
// Step 3: Verifiers upgraded to require ML-DSA
// Step 4: Drop ES256, issue ML-DSA-only JWTs

// Size impact:
// Current ES256 JWT: ~200-400 bytes
// ML-DSA signature: 2701 bytes (Dilithium3)
// Post-migration JWT: ~3000+ bytes
// Action: check Authorization header size limits
// Nginx default: 8KB header limit (should be fine)
// But: reduce JWT payload size to compensate

// Key size reference:
// ES256 private key: 32 bytes
// ML-DSA-65 private key: 4032 bytes
// Storage, backup, and rotation complexity increases

System.out.println("PQC migration: plan for 2027-2030 target");
// NIST recommends: migrate cryptographic infrastructure
// before 2030 for high-value/long-lived systems
```

---

*Authentication category: ATH | Entry: ATH-064 | v5.0*