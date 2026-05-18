---
id: SEC-010
title: "Hashing vs Encryption vs Encoding"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-002, SEC-009
used_by: SEC-038, SEC-054, SEC-069
related: SEC-001, SEC-002, SEC-009, SEC-038, SEC-054, SEC-069, SEC-141
tags:
  - security
  - hashing
  - encryption
  - encoding
  - cryptography-basics
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/sec/hashing-vs-encryption-vs-encoding/
---

⚡ TL;DR - These three are commonly confused, but they solve
completely different problems. Encoding (Base64, URL encoding)
is NOT security - it is a data format transformation. Anyone
can decode it. Hashing is a one-way irreversible transformation
(SHA-256, bcrypt) - verifying integrity or storing passwords
(where you verify but never need to recover the original).
Encryption is a two-way reversible transformation (AES, RSA) -
protecting data that must be recovered later (encrypted at-rest
database, TLS in-transit). The most common mistake in security:
using encoding (Base64) and thinking it is security, using
fast hashing (SHA-256) for passwords (reversible via brute force),
or using encryption where hashing was needed (storing an
"encrypted" password that can be decrypted if the key is stolen).
Each tool has exactly one correct use case. Using the wrong
tool is a critical security vulnerability.

---

| #010 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, CIA Triad, Password Storage Anti-Pattern | |
| **Used by:** | Bcrypt, Secrets Management, TLS Basics | |
| **Related:** | CIA Triad, Password Storage, Bcrypt, TLS Basics, Cryptography Fundamentals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CLEAR DISTINCTION:**
Three real-world security failures from using the wrong tool:

(1) **Encoding used as security:** Developer stores sensitive
config values in Base64 in a config file. "It's not plain
text." Anyone who opens the file and runs `base64 -d`:
full decoding in 0.1 seconds. Not security.

(2) **Fast hash for passwords:** Developer uses SHA-256 for
password storage. "It's hashed!" SHA-256 GPU speed: 82 billion/
second. A $500 GPU cracks common 8-character passwords in
hours. SHA-256 is not designed for passwords.

(3) **Encryption where hashing needed:** Developer stores
password hashes as AES-encrypted values. "It's encrypted,
not just hashed!" When the AES key is found (environment
variable, config file, deployed alongside the application):
all "encrypted" passwords instantly decrypted. Encryption
requires secure key management. If the key lives near the
data: encryption provides minimal additional security.

The distinction determines whether your security control
is actually providing the intended protection.

---

### 📘 Textbook Definition

**Encoding:** A format transformation with no security property.
Converts data between representations for compatibility.
Base64, URL encoding (percent-encoding), HTML encoding.
Reversible by anyone with zero knowledge of any key or secret.
Purpose: transmit binary data over text channels, make
data URL-safe, escape special characters.
Security property: NONE. Anyone can decode Base64.

**Hashing:** A deterministic one-way function.
Takes arbitrary input, produces fixed-length output.
Same input always produces same output (deterministic).
Cannot be reversed to recover input (one-way - for secure hashes).
Different inputs (almost) always produce different outputs
(collision resistance - for cryptographic hashes).
Types: General-purpose (SHA-256, SHA-3) for integrity and
digital signatures. Password-specific (bcrypt, Argon2id)
for credentials. MAC (HMAC-SHA256) for integrity with
authentication (proves who created the hash).
Purpose: verify integrity, store passwords, build Merkle trees,
generate digital signatures.
Security property: integrity, password storage.

**Encryption:** A reversible transformation using a key.
Takes plaintext + key, produces ciphertext.
Given ciphertext + correct key: recovers plaintext.
Without the key: computationally infeasible to recover plaintext.
Types: Symmetric (AES-256-GCM: same key encrypts and decrypts),
Asymmetric (RSA/ECDSA: public key encrypts, private key decrypts).
Purpose: protect data confidentiality (at rest and in transit)
where the original data must be recoverable.
Security property: confidentiality.

**Decision Framework:**
- "I need to VERIFY something without storing the original" → Hash
- "I need to STORE and RECOVER the original later" → Encrypt
- "I need to TRANSMIT data in a compatible format" → Encode

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Encoding (Base64) = format change, zero security.
Hashing (SHA-256/bcrypt) = one-way, use for integrity or passwords.
Encryption (AES) = reversible with key, use for confidentiality.
Wrong tool = critical vulnerability.

**One analogy:**
> Encoding = writing in a different alphabet (Greek):
>   looks scrambled, but anyone who knows Greek reads it.
> Hashing = putting documents in a shredder:
>   original is gone. You can only verify a new document
>   by shredding it and comparing the output.
> Encryption = putting documents in a safe:
>   need the combination to retrieve them. Original preserved.

---

### 🔩 First Principles Explanation

**Why "one-way" matters for hashing:**

```
HASH FUNCTION PROPERTIES (cryptographic requirements):

1. DETERMINISTIC: hash(X) always = same output.
   Why needed: verification (hash stored password, compare).

2. ONE-WAY (preimage resistance):
   Given hash H, computationally infeasible to find X where hash(X) = H.
   Why needed: if reversed → passwords reconstructed from hashes.

3. COLLISION RESISTANCE:
   Computationally infeasible to find X1 ≠ X2 where hash(X1) = hash(X2).
   Why needed: signature forgery (sign document A, forge document B
   with same hash = valid signature on B).

4. AVALANCHE EFFECT:
   Small change in input → large change in output.
   "password" → completely different hash from "password1".
   Why needed: prevents partial information leakage from hash.

SHA-256 satisfies all 4 properties for general-purpose use.
But: property 1 (deterministic) + GPU speed = password cracking.
bcrypt/Argon2 add: computational cost + per-use salt.

ENCRYPTION PROPERTIES (additional requirements):
5. REVERSIBILITY (with key): decrypt(encrypt(X, K), K) = X
   Hashes don't have this (by design). Encryption requires it.

6. KEY SECRECY: security depends on key being secret.
   If encryption key is compromised: all ciphertext decryptable.
   Hashing: if algorithm is known, only brute force applies
   (no "key compromise" vector - salt is not secret).

PRACTICAL DECISION:
  Need to verify without recovering? → Hash.
  Need to recover? → Encrypt (+ solve key management problem).
  SHA-256 for password storage is wrong because the data
  doesn't NEED to be recovered - just verified. But the
  computational cheapness of SHA-256 allows brute force.
  bcrypt: verification possible, recovery computationally
  infeasible even for the server.
```

---

### 🧪 Thought Experiment

**SCENARIO: Where does each belong in a real application?**

```
REAL APPLICATION: E-commerce platform

ENCODING USE CASES:
  - Base64: encode binary profile photos for JSON API responses
  - URL encoding: encode special characters in redirect URLs
  - HTML encoding: escape user-generated content in HTML
    (<script> becomes &lt;script&gt; to prevent XSS)
  - JWT base64url: encode header + payload in JWT token
    (NOT security - the payload is readable, only the
     signature provides security)
  NOTE: None of these are security controls. They are
  format compatibility transformations.

HASHING USE CASES:
  - Passwords: bcrypt cost 12 or Argon2id (never MD5/SHA-256)
  - HMAC-SHA256: sign webhook payloads (verify origin + integrity)
  - SHA-256: hash file contents for integrity verification
    (compare file hash against known-good hash)
  - HMAC: sign API request parameters (prevent tampering)
  - Merkle tree: hash blocks of transaction data (blockchain,
    certificate transparency logs)
  - Idempotency keys: hash (user_id + product_id + timestamp)
    to generate unique request identifier

ENCRYPTION USE CASES:
  - AES-256-GCM: encrypt PII columns (SSN, credit card)
    stored in database (key in KMS, not in app code)
  - TLS 1.3: encrypt all data in transit (AES-256-GCM)
  - Envelope encryption: KMS data key encrypts data,
    KMS master key encrypts data key (key hierarchy)
  - Application secrets: encrypted in Vault or AWS SSM
    Parameter Store (encryption at rest, decrypted in memory)

COMMON MISTAKES SPOTTED:
  - Base64 of a password in a cookie → encoding, not security
  - SHA-256 of a password in a database → hashing, wrong algo
  - "Encrypting" a password with AES in ECB mode →
    encryption with terrible mode (ECB reveals patterns)
  - bcrypt of a credit card number → hashing, wrong use case
    (can never recover the number for processing - should encrypt)
```

---

### 🧠 Mental Model / Analogy

> The three operations form a decision tree:
>
> Q1: "Is this about security at all?"
>   NO → Use encoding (format compatibility only)
>   YES → Q2
>
> Q2: "Do I need to RECOVER the original data later?"
>   NO → Use hashing (passwords, integrity verification)
>   YES → Q3
>
> Q3: "Do I have a secure key management solution?"
>   NO → Rethink (encryption without key management is
>         barely better than plain text)
>   YES → Use encryption (AES-256-GCM for symmetric,
>         RSA/ECDH for asymmetric)
>
> This decision tree prevents all three common mistakes.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Three different tools that look similar but do different things.
Encoding: change format but anyone can change it back (not safe).
Hashing: scramble data so it cannot be unscrambled (safe for passwords).
Encryption: scramble data and only someone with the key can unscramble (safe for secret data you need back later).

**Level 2 - How to use it (junior developer):**
Three decision questions: Do I need the original back? Yes = encryption.
Is this a password? Yes = bcrypt/Argon2. Is this about data format
compatibility? Yes = encoding. If a config value labeled "base64" makes
you think it's "secured" - it is not. Base64 is a transport format.

**Level 3 - How it works (mid-level engineer):**
For integrity: HMAC-SHA256 (keyed hash = only key-holder can create
valid hash - proves origin). For data at rest: AES-256-GCM (authenticated
encryption = encrypts AND verifies integrity). For data in transit:
TLS 1.3 (ECDH key exchange + AES-256-GCM symmetric encryption). The
"GCM" in AES-256-GCM: Galois/Counter Mode provides both encryption and
authentication - every ciphertext includes an authentication tag that
detects tampering (unlike AES-ECB or AES-CBC without HMAC).

**Level 4 - Why it was designed this way (senior/staff):**
The distinction emerged from different cryptographic needs.
Hash functions (Shannon 1949, Merkle-Damgard construction, SHA family)
were designed for message authentication and integrity verification.
Block ciphers (DES 1977, AES 2001) were designed for data confidentiality.
Encoding formats (Base64: MIME email, 1987) were designed for transport
compatibility before any security consideration. The fact that all three
look like "scrambled data" to non-technical observers is the source of
confusion. Security engineers must be precise about which property
(integrity, confidentiality, authenticity, compatibility) they need
and which tool provides it.

**Level 5 - Mastery (distinguished engineer):**
Modern cryptography combines tools: AES-GCM = encryption (AES) + integrity
(GCM authentication tag). TLS record protocol: key exchange (ECDH) +
symmetric encryption (AES-256-GCM) + MAC (GCM auth tag). JWT: encoding
(Base64url header and payload) + hashing/signing (HMAC-SHA256 or RS256).
None of these are purely one category. Understanding the layered
composition is necessary for: protocol design (which primitives to
combine), vulnerability analysis (which layer a specific attack targets),
and implementation (using AES in a mode that provides both confidentiality
AND integrity - never AES-ECB or AES-CBC without HMAC).

---

### ⚙️ How It Works (Mechanism)

**Quick property comparison across concrete examples:**

```
                  ENCODING        HASHING         ENCRYPTION
                  (Base64)        (SHA-256)        (AES-256-GCM)

Input:            "secret"        "secret"         "secret"
Output:           "c2VjcmV0"     "2bb80d537..."   "a4f2c9d8..." (varies)
Output length:    Input × 4/3    Fixed (256 bits)  Input + 16B (auth tag)
Reversible?       YES (always)    NO               YES (with key only)
Key required?     No             No (HMAC: yes)    Yes (AES key)
Same input →      Always same    Always same       Different each time
same output?      output         output            (random IV/nonce)
Security purpose: NONE           Integrity/auth    Confidentiality
                                 (integrity w/     (+ integrity in GCM)
                                  HMAC)
Performance:      Microseconds   Microseconds      Microseconds (AES-NI)
                                 (bcrypt: 300ms)
Detect tampering? No             Yes (w/ HMAC)     Yes (GCM auth tag)
Crackable?        Instantly      Fast hashes: yes  Only key brute-force
                  (decode)       bcrypt: no

NOTES ON "SAME INPUT → SAME OUTPUT":
  Encryption uses a random IV/nonce for each encryption.
  AES-256-GCM("secret", key) produces different ciphertext
  each time because IV is random. This is a FEATURE:
  prevents ciphertext patterns (if "hello" always encrypts to
  the same ciphertext: attacker can detect when "hello" is sent).
  The IV is stored alongside the ciphertext (not secret).
  Decryption: AES-GCM decrypt(ciphertext, key, IV) = "secret".
```

---

### 💻 Code Example

**All three in practice:**

```python
import base64, hashlib, hmac, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ENCODING: Base64 (NOT security)
def encode_for_transport(data: bytes) -> str:
    """Encode binary data for JSON transport."""
    return base64.b64encode(data).decode()

def decode_from_transport(encoded: str) -> bytes:
    """Decode base64 back to binary."""
    return base64.b64decode(encoded)

# Demo: not secure - anyone can call decode_from_transport
profile_photo_base64 = encode_for_transport(b"[binary photo data]")
# base64 → just a format. No secret. No security.

# HASHING: HMAC-SHA256 (integrity + authentication)
WEBHOOK_SECRET_KEY = os.environ.get("WEBHOOK_SECRET").encode()

def sign_payload(payload: bytes) -> str:
    """Create HMAC signature for webhook payload."""
    sig = hmac.new(WEBHOOK_SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature to prove origin + integrity."""
    expected = sign_payload(payload)
    # Constant-time comparison prevents timing attacks
    return hmac.compare_digest(signature, expected)

# ENCRYPTION: AES-256-GCM (confidentiality + integrity)
AES_KEY = bytes.fromhex(os.environ.get("AES_KEY_HEX"))  # 32 bytes

def encrypt_pii(plaintext: str) -> str:
    """Encrypt PII for database storage."""
    nonce = os.urandom(12)     # 96-bit random nonce (new per encryption)
    aesgcm = AESGCM(AES_KEY)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    # Store nonce + ciphertext (nonce not secret, needed for decrypt)
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_pii(stored: str) -> str:
    """Decrypt stored PII."""
    data = base64.b64decode(stored)
    nonce = data[:12]          # Extract nonce (first 12 bytes)
    ciphertext = data[12:]
    aesgcm = AESGCM(AES_KEY)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()

# BAD patterns (ALL of these are security failures):
# base64.b64encode(password)   → encoding, not security
# hashlib.sha256(ssn).hex()    → hashing, but must RECOVER SSN → encrypt
# hashlib.sha256(password)     → hash but too fast → use bcrypt
# AES with static IV           → same plaintext = same ciphertext → pattern leakage
```

---

### ⚖️ Comparison Table

| Use Case | Encoding | Fast Hash | HMAC | bcrypt/Argon2 | Encryption (AES) |
|:---|:---|:---|:---|:---|:---|
| **Password storage** | NEVER | NEVER | No | YES | Never (key = exposed) |
| **Message integrity (no secret)** | No | Partially | No | No | No |
| **Message integrity (with key)** | No | No | YES | No | Partially (GCM) |
| **Data confidentiality** | NEVER | No | No | No | YES |
| **File checksum** | No | YES | No | No | No |
| **Webhook signature** | No | No | YES | No | No |
| **PII storage in DB** | NEVER | NEVER | No | No | YES + key mgmt |
| **Data in transit** | No | No | Partially | No | YES (via TLS) |
| **API transport (binary → JSON)** | YES | No | No | No | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Base64 is "encoded" - that means it's somewhat secure | Base64 is entirely reversible by anyone with no secret knowledge. `echo "c2VjcmV0" | base64 -d` → "secret". It is a binary-to-text encoding used because many protocols (HTTP, JSON, email) were originally text-only. Security property: zero. "Encoded" does not imply "secured." Treating Base64 as a security control is equivalent to treating whitespace formatting as encryption. |
| SHA-256 is "strong" so it's fine for any security use | SHA-256 is strong for its designed purpose: general-purpose integrity verification, digital signatures, and building Merkle trees. It is wrong for password storage because it was designed to be FAST (for rapid file integrity checking). That same speed enables 82 billion password guesses per second on modern hardware. "Cryptographically strong" does not mean "appropriate for any security use case." Strength is relative to the use case and threat model. |

---

### 🚨 Failure Modes & Diagnosis

**Failure: Encryption used where hashing was needed (decryptable passwords)**

**Pattern:** Application stores passwords encrypted with AES.
The encryption key is stored in an environment variable on
the same server. Developer's reasoning: "encrypted is better
than hashed - hashes can be brute-forced."

**The fatal flaw:**
```
Hashing (bcrypt): attacker must brute force each password.
  8-char random password: 231 years per GPU.
  Key exposure: N/A (no key). Attack vector: brute force only.

Encryption (AES): attacker decrypts instantly with the key.
  Key location: environment variable on same server.
  Attack vector: any server access (web shell, SSRF to metadata
  API, leaked config) → get key → decrypt ALL passwords instantly.
  Time to crack with key: microseconds.
  Time to crack without key: brute force AES-256 = 2^256 ops
    = computationally infeasible.

COMPARISON:
  bcrypt: attacker needs to brute force. Key: N/A.
  AES-encrypted passwords: attacker needs the key.
    If key is well-protected (HSM, KMS, separate system):
    AES provides confidentiality. If key is near the data:
    single breach = all passwords decrypted instantly.

VERDICT: For passwords - bcrypt > AES unless you have
  a proper HSM/KMS infrastructure AND you can guarantee
  the key is never near the database. In practice:
  bcrypt is almost always better for passwords.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Password Storage Anti-Pattern` - hashing applied to passwords
- `CIA Triad` - which tool serves which CIA property

**Builds on this:**
- `Bcrypt` - password hashing algorithm deep dive
- `TLS Basics` - how encryption is used in transport
- `Secrets Management` - key management for encryption

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ENCODING     │ Format change only. Zero security.        │
│ (Base64)     │ Use: transport compatibility, NOT security │
├──────────────┼───────────────────────────────────────────┤
│ HASHING      │ One-way. Cannot recover original.         │
│ (SHA-256,    │ Use: integrity, checksum, password hash   │
│  bcrypt)     │ bcrypt for passwords. SHA-256 for files.  │
├──────────────┼───────────────────────────────────────────┤
│ ENCRYPTION   │ Two-way. Requires key. Can recover.       │
│ (AES-256-GCM)│ Use: PII at rest, data in transit        │
│              │ Key management required.                  │
├──────────────┼───────────────────────────────────────────┤
│ DECISION     │ Need back later? → Encrypt                │
│ TREE         │ Just verify? → Hash (bcrypt for passwords)│
│              │ Format compat? → Encode                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ Encoding = open book. Hash = shredder.    │
│              │ Encryption = safe with combination.       │
│              │ Wrong tool = vulnerable by design.        │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Choose tools based on the exact property required."
In data engineering: not all storage formats are equal
(Parquet vs CSV vs JSON each optimized for different access
patterns). In networking: not all protocols are equal
(TCP for reliability, UDP for low latency). In cryptography:
not all "scrambling" operations are equal (encoding for
format, hashing for integrity, encryption for confidentiality).
The pattern: when a domain has multiple tools with similar
names but different properties, learn the exact property
each tool provides, then match the required property to
the correct tool. Using any tool outside its designed property
domain is a class of engineering error that appears across
every discipline.

---

### 💡 The Surprising Truth

The security of AES-256 encryption is not in the algorithm -
it is in the key. AES-256 with a key of "password123" is
trivially breakable (brute force the key space of common
passwords). AES-256 with a proper 256-bit random key is
computationally unbreakable. The algorithm provides the
mechanism; the key provides the security. This is why
cryptographers say "never roll your own crypto" - not because
the algorithm is hard to implement (you can implement AES
from a spec), but because key generation, key storage, key
rotation, and key access control are where real deployments
fail. The most sophisticated encryption is worthless if the
key is stored in a `.env` file committed to a public GitHub
repository (which happens thousands of times per year,
detected by tools like GitGuardian). In practice: encryption
security = key management security.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CLASSIFY** any "scrambling" operation: is it encoding
   (reversible by anyone), hashing (one-way), or encryption
   (reversible with key)?
2. **EXPLAIN** why Base64 in a JWT payload is not security
   (JWT header + payload are just base64url - readable by anyone).
3. **CHOOSE** the right tool for: password storage (bcrypt/Argon2),
   webhook integrity verification (HMAC-SHA256), PII encryption
   (AES-256-GCM + KMS key management), file integrity check (SHA-256).
4. **IDENTIFY** the encryption-for-password anti-pattern:
   encrypted passwords are weaker than bcrypt if the key is
   stored near the data.

---

### 🎯 Interview Deep-Dive

**Q: What is the difference between hashing, encryption,
and encoding? When would you use each?**

*Why they ask:* Foundational security knowledge question.
A developer who confuses these will make critical security
mistakes in any feature that handles sensitive data.

*Strong answer includes:*
- Encoding (Base64, URL encoding): format transformation,
  no security, anyone can reverse. Use for: binary data
  in JSON/HTTP, special character escaping. Never for: making
  data "safe" or "hidden."
- Hashing (SHA-256, bcrypt): one-way transformation. Cannot
  recover original. Same input = same output. Use for:
  file integrity checking (SHA-256), storing passwords (bcrypt),
  webhook signatures (HMAC-SHA256). Never for: data you need
  to recover (credit cards, PII).
- Encryption (AES-256-GCM): reversible with key. Use for:
  any data you must recover (PII in database, data in transit).
  Requires proper key management (KMS, HSM, Vault).
- Specific example: e-commerce database. Passwords: bcrypt
  (never need to recover). Credit card numbers: encrypted
  with AES-256-GCM (need to process charges). Email addresses:
  could be either (encrypted if must recover for sending emails;
  hashed if only need to look up by email without storing).
  Profile photos: Base64 in JSON API response (format compat).
- Advanced: JWT uses encoding (Base64url) for payload +
  hashing (HMAC-SHA256) for signature. The payload is readable.
  The signature is the security. This is a concrete example
  of combining all three correctly.