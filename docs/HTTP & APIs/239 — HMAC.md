---
layout: default
title: "HMAC"
parent: "HTTP & APIs"
nav_order: 239
permalink: /http-apis/hmac/
number: "0239"
category: HTTP & APIs
difficulty: ★★★
depends_on: Cryptographic Hash Functions, Symmetric Cryptography, HTTP
used_by: Webhook Verification, API Request Signing, AWS Signature V4, JWT (HS256)
related: API Keys, SHA256, JWT, Webhook, AWS S3
tags:
  - api
  - hmac
  - cryptography
  - security
  - signing
  - advanced
---

# 239 — HMAC (Hash-based Message Authentication Code)

⚡ TL;DR — HMAC is a cryptographic technique that combines a secret key with a hash function (e.g., SHA-256) to produce a fixed-length authentication tag proving both message integrity (content wasn't modified) and authenticity (sender knows the shared secret) — used to sign webhook payloads, verify API requests, and as the HS256 algorithm in JWTs.

┌──────────────────────────────────────────────────────────────────────────┐
│ #239 │ Category: HTTP & APIs │ Difficulty: ★★★ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ Cryptographic Hash Functions, │ │
│ │ Symmetric Crypto, HTTP │ │
│ Used by: │ Webhook Verification, API Signing, │ │
│ │ AWS Sig V4, JWT HS256 │ │
│ Related: │ API Keys, SHA256, JWT, Webhook │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An API sends back a webhook: `POST /webhook { "amount": 100, "status": "paid" }`.
You (the receiver) need to know:

1. Did this actually come from Stripe, or is it spoofed?
2. Was the payload modified in transit?

Sending just an API key in the header doesn't work — anyone who knows the key can
forge a request. TLS encryption proves the channel is secure but doesn't prove which
application sent the message. You need proof that whoever sent this message was in
possession of a secret that you don't share publicly.

**THE INVENTION MOMENT:**
HMAC (defined in RFC 2104, 1997 by Bellare, Canetti, and Krawczyk) provides exactly
this: given a shared secret `K`, compute `HMAC(K, message)` — a fixed-size tag that
is computationally infeasible to forge without knowing `K`. Both sender and receiver
compute the HMAC independently. If the tags match, the receiver knows: (1) the message
came from someone who knows `K` (authenticity), and (2) the message wasn't modified
(integrity). This is used in Stripe's webhook signing, AWS Signature V4, GitHub
webhook signatures, and the HS256 algorithm in JWT.

---

### 📘 Textbook Definition

**HMAC (Hash-based Message Authentication Code)** is a cryptographic construction
defined in RFC 2104 that uses a cryptographic hash function (such as SHA-256) and
a secret key to produce a fixed-length authentication code. The HMAC construction is:

$$\text{HMAC}(K, m) = H\bigl((K' \oplus \text{opad}) \,\|\, H((K' \oplus \text{ipad}) \,\|\, m)\bigr)$$

where $H$ is the hash function, $K'$ is the key padded to the block size, $\oplus$ is
XOR, and $\text{ipad}$/$\text{opad}$ are fixed constants. This double-hash construction
resists length-extension attacks that would affect naive `H(K || message)`.
HMAC provides: **integrity** (any modification to the message changes the HMAC) and
**authenticity** (only parties with the key $K$ can produce a valid HMAC). It does NOT
provide confidentiality (the message is still readable — combine with encryption for that).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HMAC is a tamper-evident seal: mix a secret key with message content through a hash
function — producing a tag that proves "this exact message was sent by someone who
knows the secret."

**One analogy:**

> HMAC is like a wax seal on a letter, combined with a secret pattern.
> The pattern can only be produced by the sender who knows the seal design (key).
> The recipient verifies: the pattern matches AND the letter content is intact
> (breaking the seal would change the visible pattern).
> Unlike a regular seal (just stamp), the HMAC seal is tied to the exact words in
> the letter. Change even one word → the seal looks different → fraud detected.

**One insight:**
The key insight is that HMAC uses the secret key in BOTH an outer and inner hash
(via the ipad/opad construction). This is not just `SHA256(key + message)` — that
construction is vulnerable to length-extension attacks. The double-hash HMAC construction
is why it's suitable for security applications where naive `H(K||m)` is not.

---

### 🔩 First Principles Explanation

**WHY NOT JUST `SHA256(key + message)`?**

```
Naive construction: H(K || message) — BROKEN by length-extension attack:
  SHA-256 (Merkle-Damgård construction) has an internal state.
  If you know H(K || message), you can compute H(K || message || padding || extra)
  WITHOUT knowing K!

  Attack:
  Attacker knows: SHA256(key || "amount=100")
  Attacker forges: SHA256(key || "amount=100" || padding || "&admin=true")
  They don't need K — they extend the hash state.

HMAC construction PREVENTS this:
  HMAC(K, m) = H(K ⊕ opad || H(K ⊕ ipad || m))
  The outer hash wraps a SEPARATE inner hash.
  You cannot extend the outer hash without computing an inner hash that requires K.
  → Length-extension attack impossible.
```

**STEP BY STEP — HMAC-SHA256:**

```
Given:
  K = shared secret (e.g., "stripe_webhook_secret_abc123")
  m = message body (e.g., timestamp + "." + json_body)

Computation:
  1. If len(K) > block_size (64 bytes for SHA-256): K = SHA256(K)
     If len(K) < block_size: K = K || zero_bytes (pad to 64 bytes)
     Result: K' (64 bytes)

  2. inner_key = K' XOR ipad    (ipad = 0x36 repeated 64 times)
  3. outer_key = K' XOR opad    (opad = 0x5C repeated 64 times)

  4. inner_hash = SHA256(inner_key || m)    ← hash of key+message
  5. hmac = SHA256(outer_key || inner_hash) ← hash of key+inner_hash

Result: 32-byte (256-bit) HMAC tag, encoded as hex or Base64

In practice:
  import javax.crypto.Mac;
  Mac mac = Mac.getInstance("HmacSHA256");
  mac.init(new SecretKeySpec(key.getBytes(), "HmacSHA256"));
  byte[] hmac = mac.doFinal(message.getBytes());
  String hex = Hex.encodeHexString(hmac);
```

**REPLAY PROTECTION (timestamps):**

```
HMAC alone proves authenticity but NOT freshness.
An attacker who captures a valid webhook can replay it later.

Solution: include timestamp in the signed message.
Stripe webhook signing:
  signed_content = timestamp + "." + body
  signature = HMAC_SHA256(webhook_secret, signed_content)
  header: Stripe-Signature: t=<timestamp>,v1=<signature>

Receiver:
  1. Parse: t = 1630000000, v1 = abc123def...
  2. Verify: |now - t| < 300 seconds (5-minute window)
     → reject if outside window (replay would be too old)
  3. Compute expected = HMAC_SHA256(secret, t + "." + body)
  4. Compare: expected == v1? → accept. Mismatch → reject.

Without timestamp check:
  Attacker replays the same valid request 1 hour later → accepted (bad)
With timestamp check:
  Same replay 1 hour later → t is too old → rejected (good)
```

---

### 🧪 Thought Experiment

**SCENARIO:** Webhook signature verification in 3 steps.

```
Setup:
  Stripe webhook secret: "whsec_test_abc123xyz456" (shared with you at registration)
  Webhook payload:
    body = '{"id":"evt_1","type":"payment_intent.succeeded","data":{"amount":2000}}'
  Stripe-Signature header:
    t=1630000000,v1=abc123def456ghi789jkl012mno345pqr678stu901vwx234

VERIFICATION:

Step 1 — Reconstruct signed content:
  signed = "1630000000" + "." + body
  = "1630000000.{"id":"evt_1","type":"payment_intent.succeeded",...}"

Step 2 — Compute expected HMAC:
  expected = HMAC_SHA256("whsec_test_abc123xyz456", signed)
  = "abc123def456ghi789jkl012mno345pqr678stu901vwx234"

Step 3 — Compare (constant-time):
  expected == "abc123def456ghi789jkl012mno345pqr678stu901vwx234"? → MATCH ✓

Also check: |now - 1630000000| < 300 seconds → NOT EXPIRED ✓

ATTACK SCENARIOS:
  Scenario A: Attacker modifies amount to 200000:
    Modified body changes HMAC: computed HMAC ≠ header HMAC → REJECT ✓

  Scenario B: Attacker replays old webhook (7 minutes ago):
    t=1629999580 → |now - 1629999580| = 420s > 300s → REJECT ✓

  Scenario C: Attacker forges a new payment_intent.succeeded with amount=1:
    No secret = can't compute valid HMAC → forged sig ≠ expected → REJECT ✓
```

---

### 🧠 Mental Model / Analogy

> HMAC is like a secret handshake that only two people know, applied to a document.
>
> Alice and Bob pre-agree on a secret handshake sequence (the key).
> When Alice sends a document to Bob, she adds a handshake "imprint" to the document
> — a code derived from the document content AND the handshake sequence.
> Bob verifies: can I reproduce this code from this document using our handshake?
> If yes: Alice sent this exact document. If no: it's forged or modified.
>
> The critical property: the handshake sequence is secret. Even if an attacker sees
> thousands of (document, imprint) pairs, they cannot figure out the handshake
> sequence and cannot create a new valid imprint for a forged document.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
HMAC is a mathematical stamp you put on a message using a secret key. The stamp changes
if the message changes or if the secret is different. It proves "I made this stamp" and
"this message hasn't been changed since I stamped it."

**Level 2 — How to use it (junior developer):**
Use `javax.crypto.Mac` (Java), `crypto.createHmac` (Node.js), or `hmac.new` (Python).
Give it your secret key and the message, get a hex/Base64 string back.
When verifying: compute your own HMAC and compare using a constant-time comparison
function (`MessageDigest.isEqual` in Java, `hmac.compare_digest` in Python).
NEVER use string equality (`==`) for HMAC comparison — timing attacks.

**Level 3 — How it works (mid-level engineer):**
Include a timestamp in the signed payload (not just the body) to prevent replay attacks.
Verify the timestamp is recent before verifying the HMAC (fail fast). Use
`MessageDigest.isEqual()` or `hmac.compare_digest()` — constant-time comparison
ensures the comparison takes the same time regardless of how many bytes match
(variable-time comparison leaks partial match information via timing). Consider
multiple valid signatures during key rotation: Stripe allows v0 and v1 signatures
simultaneously during rotation window.

**Level 4 — Why it was designed this way (senior/staff):**
The HMAC construction (`H(K⊕opad || H(K⊕ipad || m))`) was specifically designed to
be secure with any Merkle-Damgård hash function (MD5, SHA-1, SHA-256) while resisting
length-extension attacks inherent in that hash construction. The ipad/opad constants
(0x36 and 0x5C) are chosen to be different in many bits (preventing both keys from
colliding). HMAC is provably secure under reasonable assumptions about the underlying
hash function — its security reduces to the PRF (pseudorandom function) properties of
the hash, unlike naked H(K||m). HMAC remains the standard choice for message
authentication codes in protocols (TLS PRF, S3 Signature V4, JWT HS256) because of
this provable security and its resistance to the known attacks on simpler constructions.

---

### ⚙️ How It Works (Mechanism)

```
HMAC-SHA256 COMPUTATION (simplified):

Input:
  K = secret key bytes
  m = message bytes

1. Normalize key to block size (64 bytes for SHA-256):
   K' = len(K) > 64 ? SHA256(K) : K, then zero-pad to 64 bytes

2. Inner hash:
   ikey = K' XOR [0x36 × 64]    ← ipad
   inner = SHA256(ikey || m)    ← SHA256 of (inner-keyed | message)

3. Outer hash:
   okey = K' XOR [0x5C × 64]    ← opad
   hmac = SHA256(okey || inner) ← SHA256 of (outer-keyed | inner_hash)

4. Returns: 32 bytes (256 bits) of HMAC tag

WHY TWO PASSES?
  First pass (inner): binds the message to the key
  Second pass (outer): seals the inner hash under a differently-keyed hash
  This prevents length-extension: an attacker would need the outer key to extend
  the computation, which they don't have
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
STRIPE WEBHOOK SIGNING/VERIFICATION:

STRIPE (SENDER):
  1. Stripe fires event: payment_intent.succeeded
  2. Stripe: timestamp = unix_now() = 1630000000
  3. Stripe: signed_payload = "1630000000" + "." + json_body
  4. Stripe: sig = HMAC_SHA256(webhook_secret, signed_payload)
  5. Stripe: POST /webhook (body=json_body, Stripe-Signature: t=1630000000,v1=sig)

YOUR SERVER (RECEIVER):
  1. Extract raw body (BEFORE parsing JSON — many frameworks consume body stream)
  2. Extract header: Stripe-Signature: t=1630000000,v1=abc123...
  3. Check timestamp: |now - 1630000000| < 300s? ✓ (within window)
  4. Reconstruct signed_payload: "1630000000" + "." + raw_body_string
  5. Compute expected = HMAC_SHA256(webhook_secret, signed_payload)
  6. constant_time_compare(expected, "abc123...") → TRUE → VERIFIED
  7. Parse JSON, process event, return 200

KEY DETAIL: Extract raw body string BEFORE JSON parsing
  If you parse JSON first and re-serialize, even a single whitespace difference
  will change the HMAC and cause verification failure
```

---

### 💻 Code Example

```java
// HMAC-SHA256 webhook verification (Stripe-style)
public class HmacWebhookVerifier {

    public static boolean verifyStripeSignature(
            String payload,         // raw request body string (before JSON parsing)
            String sigHeader,       // "t=1630000000,v1=abc123..."
            String webhookSecret) {

        // Parse signature header
        Map<String, String> params = parseSignatureHeader(sigHeader);
        String timestampStr = params.get("t");
        String receivedSig = params.get("v1");

        if (timestampStr == null || receivedSig == null) {
            return false;
        }

        // Replay attack check: reject if timestamp is > 5 minutes old
        long timestamp = Long.parseLong(timestampStr);
        long now = Instant.now().getEpochSecond();
        if (Math.abs(now - timestamp) > 300) {
            return false; // Timestamp too old or too far in future
        }

        // Reconstruct signed content: "timestamp.body"
        String signedContent = timestampStr + "." + payload;

        // Compute expected HMAC
        String expectedSig = computeHmacSha256(webhookSecret, signedContent);

        // Constant-time comparison (CRITICAL: prevents timing attacks)
        return MessageDigest.isEqual(
            expectedSig.getBytes(StandardCharsets.UTF_8),
            receivedSig.getBytes(StandardCharsets.UTF_8)
        );
    }

    private static String computeHmacSha256(String secret, String message) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(
                secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(keySpec);
            byte[] hmacBytes = mac.doFinal(message.getBytes(StandardCharsets.UTF_8));
            return Hex.encodeHexString(hmacBytes); // Apache Commons Codec
        } catch (Exception e) {
            throw new RuntimeException("HMAC computation failed", e);
        }
    }
}

// Usage in Spring controller
@PostMapping("/webhooks/stripe")
public ResponseEntity<Void> handleStripe(
        @RequestBody String rawBody,           // raw string, not object
        @RequestHeader("Stripe-Signature") String sig) {

    if (!HmacWebhookVerifier.verifyStripeSignature(rawBody, sig, webhookSecret)) {
        return ResponseEntity.status(401).build();
    }

    // Safe to parse JSON now
    StripeEvent event = objectMapper.readValue(rawBody, StripeEvent.class);
    processEvent(event);
    return ResponseEntity.ok().build();
}
```

---

### ⚖️ Comparison Table

| Approach                          | Authenticity   | Integrity | Non-repudiation | Key Type    | Use Case                      |
| --------------------------------- | -------------- | --------- | --------------- | ----------- | ----------------------------- |
| **HMAC**                          | ✅             | ✅        | ❌ (shared key) | Symmetric   | Webhook signing, JWT HS256    |
| **Digital Signature (RSA/ECDSA)** | ✅             | ✅        | ✅              | Asymmetric  | JWT RS256/ES256, code signing |
| **Plain Hash (SHA256)**           | ❌             | ✅        | ❌              | None needed | Integrity only (checksum)     |
| **API Key in Header**             | ✅ (if secret) | ❌        | ❌              | Symmetric   | Identity only                 |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                   |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SHA256(key + message)` is equivalent to HMAC | This is broken by length-extension attacks. Always use the HMAC construction                                                                              |
| HMAC provides confidentiality                 | HMAC provides authenticity and integrity — the message is still readable. Add encryption separately                                                       |
| Use `==` to compare HMAC strings              | Variable-time string comparison leaks partial match info via timing. Always use constant-time comparison (`MessageDigest.isEqual`)                        |
| HMAC with MD5 is insecure                     | HMAC-MD5 is still technically secure as an authentication code (MD5's collision weaknesses don't apply to HMAC-MD5). However, use SHA-256 for new systems |

---

### 🚨 Failure Modes & Diagnosis

**Timing Attack on HMAC Comparison**

Symptom:
Security audit finds the webhook verification uses string equality (`signature.equals(expected)`).

Root Cause:
Java's `String.equals()` short-circuits on the first differing character — if the
first character matches, comparison takes longer; if not, it returns fast. Over many
requests, an attacker can statistically infer the correct HMAC one character at a time.

Fix:

```java
// WRONG:
if (computedSig.equals(receivedSig)) { ... }

// CORRECT — constant-time comparison:
if (MessageDigest.isEqual(
    computedSig.getBytes(StandardCharsets.UTF_8),
    receivedSig.getBytes(StandardCharsets.UTF_8))) { ... }

// Also correct:
if (HmacUtils.hmacSha256Hex(key, message).equals(receivedSig)) {
  // HmacUtils from Apache Commons Codec is fine IF
  // the outer comparison is constant-time (see above)
}
```

---

### 🔗 Related Keywords

- `Webhook` — the primary API context where HMAC verification is used
- `JWT` — uses HMAC-SHA256 (HS256) as one of its signing algorithms
- `API Keys` — HMAC adds message integrity on top of API key identification
- `SHA-256` — the hash function most commonly used in HMAC constructions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hash(key ⊕ opad, Hash(key ⊕ ipad, msg)) │
│              │ Proves: authenticity + integrity          │
├──────────────┼───────────────────────────────────────────┤
│ THREE THINGS │ 1. shared key → authenticity              │
│ IT PROVES    │ 2. hash of content → integrity           │
│              │ 3. Does NOT provide confidentiality      │
├──────────────┼───────────────────────────────────────────┤
│ USE WITH     │ Timestamp in signed payload → replay     │
│ TIMESTAMP    │ protection (check |now-t| < 5min)        │
├──────────────┼───────────────────────────────────────────┤
│ COMPARISON   │ ALWAYS constant-time (MessageDigest.     │
│              │ isEqual) — never String.equals()         │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ SHA256(key + msg) — use HMAC() instead   │
│              │ (length-extension attack vulnerability)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Secret key + hash = tamper-evident seal"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JWT → Webhook → Digital Signatures        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** HMAC proves that both parties share a secret key. But if two microservices share the same HMAC key, a compromised service A can forge messages that appear to come from service B (since both use the same key). Design a request signing architecture for 20 microservices that: (1) gives each service a unique signing identity, (2) allows any service to verify any other service's messages without holding every service's key, (3) supports key rotation without downtime. Hint: compare symmetric (HMAC) vs asymmetric (RSA/ECDSA) approaches.
