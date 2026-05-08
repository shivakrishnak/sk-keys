---
layout: default
title: "AWS KMS (Key Management Service)"
parent: "Cloud — AWS"
nav_order: 14
permalink: /cloud-aws/aws-kms/
id: AWS-014
category: Cloud — AWS
difficulty: ★★★
depends_on: Encryption, AWS, Security
used_by: AWS Secrets Manager, Cloud — AWS
related: AWS Secrets Manager, HSM, Envelope Encryption
tags:
  - aws
  - cloud
  - security
  - advanced
  - cryptography
---

# AWS-014 — AWS KMS (Key Management Service)

⚡ **TL;DR —** A managed AWS service for creating and controlling cryptographic keys used to encrypt data across AWS services and applications, with full CloudTrail auditability.

| | |
|---|---|
| **Depends on** | Encryption, AWS, Security |
| **Used by** | AWS Secrets Manager, Cloud — AWS |
| **Related** | AWS Secrets Manager, HSM, Envelope Encryption |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You encrypt data with keys stored in your application code, environment variables, or S3 buckets. Managing key rotation means rewriting code. Auditing who decrypted what is impossible. When a key is compromised, re-encrypting terabytes of data is a manual disaster.

**THE BREAKING POINT:** Compliance frameworks (PCI DSS, HIPAA, SOC 2) require cryptographic key management with separation of duties — the people who use data must not be able to manage the keys that protect it. You cannot achieve this with application-level key storage.

**THE INVENTION MOMENT:** AWS built KMS to answer: what if key material never left a hardened hardware boundary, all usage was audited, and rotation happened without application changes?

---

### 📘 Textbook Definition

**AWS KMS (Key Management Service)** is a managed cryptographic service that creates and stores symmetric and asymmetric encryption keys in FIPS 140-2 validated hardware security modules (HSMs). It provides APIs for encrypt, decrypt, sign, verify, and key generation operations, with all activity logged to AWS CloudTrail and access controlled through key policies and IAM.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A managed HSM service where you control who can use keys but never see the key material itself.

**One analogy:**
> KMS is like a bank vault where the vault's owner (AWS) never gives you the physical key — instead, you present your badge (IAM credentials), a guard (KMS API) checks your access list (key policy), and the vault performs the operation internally while writing every action in a permanent log.

**One insight:** KMS performs encryption on your behalf — your data travels to KMS, gets encrypted, and returns. The plaintext key never leaves the HSM.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. KMS key material never leaves the HSM in plaintext form.
2. Every cryptographic operation is an API call — authenticated, authorised, and audited.
3. Envelope encryption scales KMS to arbitrary data sizes using data keys.
4. Key policy is the primary access control mechanism; IAM is secondary.

**DERIVED DESIGN:** KMS generates a data key for bulk encryption. The data key encrypts your data locally. KMS then encrypts the data key itself with the KMS master key (CMK), producing an encrypted data key stored alongside the ciphertext. Decryption reverses: KMS decrypts the data key, the data key decrypts the data. The CMK never directly touches bulk data — only data keys do.

**THE TRADE-OFFS:**
**Gain:** Hardware-backed key security, automatic audit, compliance-ready, separation of duties, key rotation without re-encryption of data.
**Cost:** API latency (~5ms per call), per-request charges ($0.03/10K requests), 5,500 requests/second default limit per key per region.

---

### 🧪 Thought Experiment

**SETUP:** You store PII in S3. You encrypt each object using a symmetric key stored in an environment variable in your application.

**WHAT HAPPENS WITHOUT KMS:** A developer with S3 read access copies the environment variable from the deployment config. They download every encrypted S3 object and decrypt it locally. No audit trail. No revocation mechanism. Compliance audit fails.

**WHAT HAPPENS WITH KMS:** The environment variable is gone. Every decrypt call hits KMS. The developer's IAM role doesn't have `kms:Decrypt` on the PII key. They get `AccessDeniedException`. The attempted access appears in CloudTrail. Security is alerted within minutes.

**THE INSIGHT:** Separating key custody from data custody means compromising one doesn't compromise the other. KMS makes this separation the default, not an architectural afterthought.

---

### 🧠 Mental Model / Analogy

> KMS is like a notary stamp machine that you can never take home. You bring your document (data), the machine stamps it (encrypts or decrypts), and every stamp is recorded in a public log. The machine's stamp pattern (key material) is never revealed — only the stamped documents leave the building.

- **Stamp machine** = KMS key (CMK)
- **The stamp pattern** = key material inside the HSM
- **Bringing your document** = calling `Encrypt` or `Decrypt` API
- **The public log** = CloudTrail records
- **Who's allowed to use the machine** = key policy + IAM

Where this analogy breaks down: a real notary uses their key directly on documents; KMS uses envelope encryption so the CMK only ever encrypts small data keys, not bulk data.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
KMS is like a super-secure key cabinet managed by AWS. Your apps ask it to lock and unlock sensitive data, and every request is recorded — no one can secretly access your data without a trace.

**Level 2 — How to use it (junior developer):**
Create a KMS key in the console. When writing encrypted data, call `GenerateDataKey` to get a plaintext + encrypted data key. Encrypt your data with the plaintext key in memory. Store the encrypted data + encrypted data key together. On read, call `Decrypt` on the encrypted data key to recover the plaintext key, then decrypt your data.

**Level 3 — How it works (mid-level engineer):**
KMS uses envelope encryption. The CMK (Customer Master Key) lives in an HSM and only encrypts and decrypts small data keys (up to 4 KB). Data keys perform the actual bulk AES-256 encryption in your application memory. This splits the key hierarchy: CMK → data key → data. Annual key rotation replaces the CMK backing material but re-wraps existing data keys automatically without decrypting any data.

**Level 4 — Why it was designed this way (senior/staff):**
Envelope encryption solves two fundamental problems simultaneously. First, asymmetric performance: symmetric AES is orders of magnitude faster than RSA/EC but you still need the security properties of a hardware-backed key hierarchy. Second, key rotation scalability: re-encrypting terabytes of data on every rotation is infeasible. By rotating only the top-level CMK and re-wrapping data keys on demand, the rotation is effectively free of data movement. This mirrors the AES key wrapping standard (RFC 3394) used in hardware security modules industry-wide.

---

### ⚙️ How It Works (Mechanism)

1. **Key types** — AWS managed keys (free, per-service, no user control) vs. customer managed keys (CMKs, $1/month, full policy control).
2. **Key policy** — JSON document attached to the KMS key. The root account is always a principal. Without an explicit key policy statement, IAM policies have no effect.
3. **IAM policy** — supplements key policy. Both must allow the operation for the call to succeed (AND gate).
4. **Grants** — temporary, delegated permissions for specific operations. Services like Secrets Manager use grants internally to rotate keys on your behalf.
5. **Envelope encryption** — `GenerateDataKey` returns plaintext + encrypted data key. Store encrypted data key with the ciphertext.
6. **Key rotation** — AWS rotates backing key material annually (CMK). Data keys encrypted under old material can still be decrypted transparently.
7. **Multi-region keys** — same key material replicated across regions. Decrypt ciphertext encrypted in us-east-1 from us-west-2 without cross-region API calls.
8. **CloudTrail logging** — every API: `Encrypt`, `Decrypt`, `GenerateDataKey`, `DescribeKey` — all logged with caller identity and timestamp.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (envelope encryption):**
```
Application              KMS (HSM)         S3 / Storage
     |                      |                   |
     |-- GenerateDataKey --> |                   |
     |<- {plaintext_dk,      |                   |
     |    encrypted_dk} -----|                   |
     |                       |  ← YOU ARE HERE   |
     | [encrypt data with plaintext_dk in memory]|
     | [zero out plaintext_dk]                   |
     |-- PutObject(ciphertext + encrypted_dk) -->|
     |                                           |
     |-- GetObject(ciphertext + encrypted_dk) <--|
     |-- Decrypt(encrypted_dk) -------> |        |
     |<- plaintext_dk ----------------- |        |
     | [decrypt ciphertext in memory]            |
```

**FAILURE PATH:**
- Caller not in key policy → `AccessDeniedException`
- Key in `PendingDeletion` state → `KMSInvalidStateException`
- Cross-account call without explicit trust → `AccessDeniedException`

**WHAT CHANGES AT SCALE:**
At high throughput, per-key API limits (5,500 req/s symmetric) become a bottleneck. Use multiple CMKs across workloads, cache data keys in memory for short periods, and use `GenerateDataKeyWithoutPlaintext` for write-path optimisation.

---

### 💻 Code Example

**BAD — key stored in application code:**
```python
# Never store encryption keys in source
SECRET_KEY = b"hardcoded-aes-key-do-not-do-this"
cipher = AES.new(SECRET_KEY, AES.MODE_GCM)
```

**GOOD — envelope encryption with KMS:**
```python
import boto3, os
from cryptography.hazmat.primitives.ciphers.aead \
    import AESGCM

kms = boto3.client("kms", region_name="us-east-1")
KEY_ID = "alias/myapp-data-key"

def encrypt_data(plaintext: bytes) -> dict:
    # Generate a data key
    response = kms.generate_data_key(
        KeyId=KEY_ID,
        KeySpec="AES_256"
    )
    plaintext_dk = response["Plaintext"]
    encrypted_dk = response["CiphertextBlob"]

    # Encrypt data locally
    nonce = os.urandom(12)
    aesgcm = AESGCM(plaintext_dk)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # Zero out the plaintext data key
    plaintext_dk = b"\x00" * len(plaintext_dk)

    return {
        "ciphertext": ciphertext,
        "nonce": nonce,
        "encrypted_dk": encrypted_dk
    }

def decrypt_data(blob: dict) -> bytes:
    # Decrypt the data key via KMS
    resp = kms.decrypt(
        CiphertextBlob=blob["encrypted_dk"]
    )
    plaintext_dk = resp["Plaintext"]
    aesgcm = AESGCM(plaintext_dk)
    return aesgcm.decrypt(
        blob["nonce"], blob["ciphertext"], None
    )
```

**AWS CLI — key management operations:**
```bash
# Create a CMK with alias
aws kms create-key \
  --description "MyApp PII encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT

aws kms create-alias \
  --alias-name alias/myapp-pii \
  --target-key-id <key-id>

# Enable annual automatic rotation
aws kms enable-key-rotation \
  --key-id alias/myapp-pii

# Encrypt a small value directly
aws kms encrypt \
  --key-id alias/myapp-pii \
  --plaintext "mysecretvalue" \
  --query CiphertextBlob \
  --output text

# Check who has access (key policy)
aws kms get-key-policy \
  --key-id alias/myapp-pii \
  --policy-name default
```

---

### ⚖️ Comparison Table

| Feature | AWS KMS CMK | AWS Managed Key | AWS CloudHSM |
|---|---|---|---|
| **Cost** | $1/month + requests | Free | ~$1.60/hr/HSM |
| **Key control** | Full key policy | AWS-defined | Full (you manage) |
| **Rotation** | Annual auto or manual | Annual auto | Manual |
| **Multi-region** | Yes | No | No |
| **FIPS 140-2 level** | Level 2 | Level 2 | Level 3 |
| **Custom algorithms** | No | No | Yes |
| **Use case** | Most AWS workloads | Default AWS service encryption | Strict compliance, custom crypto |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Enabling KMS encryption means my data is secure" | KMS provides encryption at rest. You still need TLS in transit, proper IAM policies, and network controls. Encryption is one layer. |
| "Key rotation changes the key — my old data breaks" | KMS keeps all previous backing key versions. Old encrypted data keys can still be decrypted after rotation. No re-encryption of data is needed. |
| "IAM policy alone controls KMS access" | The key policy is the primary gate. IAM policies on the caller supplement it, but if the key policy doesn't grant access, IAM can't override it for CMKs. |
| "AWS managed keys are as flexible as CMKs" | AWS managed keys have AWS-controlled policies. You cannot share them cross-account, restrict specific principals, or assign grants. CMKs are required for fine-grained control. |
| "KMS encrypts large files directly" | KMS `Encrypt` has a 4 KB limit. For larger data, use envelope encryption: KMS encrypts the data key, and you encrypt the data locally with that data key. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: AccessDeniedException on Decrypt**
**Symptom:** Application fails to decrypt data; `AccessDeniedException` in logs, even though the IAM role has `kms:Decrypt` in its IAM policy.
**Root Cause:** The key policy does not grant the role access. IAM policy without key policy grant = access denied for CMKs.
**Diagnostic:**
```bash
# View the key policy
aws kms get-key-policy \
  --key-id alias/myapp-pii \
  --policy-name default \
  --query Policy \
  --output text | python3 -m json.tool

# Check CloudTrail for the denial
aws cloudtrail lookup-events \
  --lookup-attributes \
    AttributeKey=EventName,AttributeValue=Decrypt \
  --query 'Events[?ErrorCode!=null]'
```
**Fix:** Add the IAM role ARN as a principal in the key policy with `kms:Decrypt` permission.
**Prevention:** Use a key policy template that includes application role ARNs from the start. Test with `kms:Decrypt` dry-run in staging.

**Mode 2: KMSInvalidStateException on scheduled key deletion**
**Symptom:** All decryption operations fail with `KMSInvalidStateException: arn:aws:kms:...:key/... is pending deletion`.
**Root Cause:** A key was scheduled for deletion while data encrypted with it still exists in production.
**Diagnostic:**
```bash
# List keys pending deletion
aws kms list-keys --query \
  'Keys[*].KeyId' --output text | \
  xargs -I{} aws kms describe-key \
    --key-id {} \
  --query 'KeyMetadata.[KeyId,KeyState]' \
  --output text | grep PendingDeletion
```
**Fix:** Cancel the deletion immediately. The minimum waiting period (7 days) provides recovery time.
**Prevention:** Enable the `kms-cmk-backing-key-rotation-enabled` AWS Config rule. Never delete a KMS key without verifying no data is encrypted under it. Use key grants and CloudTrail to audit usage.

**Mode 3: API throttling on GenerateDataKey**
**Symptom:** `ThrottlingException` on write-heavy workloads; 5,500 request/second limit for symmetric keys per region.
**Root Cause:** Each write operation generates a new data key. At scale, this saturates the per-key API rate.
**Diagnostic:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/KMS \
  --metric-name NumberOfRequestsThrottled \
  --dimensions Name=KeyId,Value=<key-id> \
  --period 60 \
  --statistics Sum \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z
```
**Fix:** Cache data keys for short-lived reuse (1–5 minutes). Use multiple CMKs distributed across key aliases. Request a quota increase.
**Prevention:** Design data key generation to happen at session or batch level, not per-record. Monitor `NumberOfRequestsThrottled` in CloudWatch with alarms.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Encryption — understand symmetric vs asymmetric encryption, AES, and key hierarchy concepts before KMS makes sense.
- Security — IAM, least privilege, and audit requirements are the context in which KMS operates.
- AWS IAM — KMS access control combines key policies with IAM; IAM mastery is prerequisite.

**Builds On This (learn these next):**
- AWS Secrets Manager — uses KMS CMKs to encrypt secrets; understanding KMS unlocks advanced Secrets Manager configuration.
- AWS S3 — SSE-KMS encrypts objects using CMKs; KMS knowledge is needed to configure per-bucket encryption policies.
- AWS CloudTrail — all KMS API calls appear in CloudTrail; pairing KMS with CloudTrail insights enables full cryptographic audit.

**Alternatives / Comparisons:**
- AWS CloudHSM — dedicated single-tenant HSM hardware, FIPS 140-2 Level 3, for workloads requiring full key custody.
- HashiCorp Vault Transit — application-level encryption-as-a-service, cloud-agnostic, with dynamic key management.
- GCP Cloud KMS — Google's equivalent service with similar envelope encryption patterns but different key hierarchy model.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Managed HSM-backed key service     |
|                  | for encrypt/decrypt/sign/verify     |
| PROBLEM IT SOLVES| App-level key storage, no audit,   |
|                  | no separation of duties             |
| KEY INSIGHT      | Key material never leaves HSM;      |
|                  | envelope encryption scales it       |
| USE WHEN         | Encrypting AWS data at rest,        |
|                  | compliance requirements, PII        |
| AVOID WHEN       | Custom crypto algorithms (use       |
|                  | CloudHSM); very high throughput     |
|                  | without data key caching            |
| TRADE-OFF        | $1/month + latency vs hardware-    |
|                  | backed security and full audit      |
| ONE-LINER        | kms:GenerateDataKey + local AES    |
| NEXT EXPLORE     | Envelope Encryption, CloudHSM      |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** KMS enforces that the key policy is the primary access control gate — not IAM. Why was this architectural decision made? What security property would break if IAM alone could grant `kms:Decrypt` access without a corresponding key policy statement?

2. **(Scale)** Your analytics pipeline writes 50,000 records/second to DynamoDB with SSE-KMS using a single CMK. Each write generates a `GenerateDataKey` call. The per-key API limit is 5,500 requests/second. Without code changes, what architectural patterns reduce this to well within the limit?

3. **(Design Trade-off)** Annual automatic key rotation in KMS creates a new backing key version but doesn't re-encrypt existing data. An auditor argues that data encrypted under a 3-year-old key version is "not adequately protected." How do you respond, and under what real-world conditions would the auditor's concern be valid?
