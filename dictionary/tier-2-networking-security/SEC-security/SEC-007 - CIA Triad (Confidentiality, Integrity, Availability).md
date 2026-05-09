---
layout: default
parent: "Security"
grand_parent: "Technical Dictionary"
nav_order: 7
id: SEC-007
title: CIA Triad (Confidentiality, Integrity, Availability)
category: Security
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on:
used_by: SEC-002, SEC-004, SEC-005, SEC-006, SEC-008
related: SEC-002, SEC-005, SEC-008, SEC-055
tags:
  - security
  - foundational
  - mental-model
  - architecture
status: complete
version: 1
---

# SEC-007 - CIA Triad (Confidentiality, Integrity, Availability)

⚡ **TL;DR** - The three core security goals every system must balance: keep data secret, keep it accurate, and keep it accessible.

| Attribute  | Details                                                                                                                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Depends on | -                                                                                                                                                                                          |
| Used by    | [[SEC-002 - Authentication vs Authorization]], [[SEC-004 - Principle of Least Privilege]], [[SEC-005 - Defense in Depth]], [[SEC-006 - Security by Design]], [[SEC-008 - Threat Modeling]] |
| Related    | [[SEC-002 - Authentication vs Authorization]], [[SEC-005 - Defense in Depth]], [[SEC-008 - Threat Modeling]], [[SEC-055 - OWASP Top 10]]                                                   |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Early networked systems had no unified security framework. Each team made ad hoc decisions: encrypt this file but not that one, restrict this endpoint but leave that API open. When breaches occurred, there was no shared language to describe what failed or why. Defenders spent time arguing about scope instead of fixing problems.

**THE BREAKING POINT:** As systems scaled, ad hoc security collapsed. A hospital database gets silently corrupted - medication dosages are wrong (Integrity). A competitor intercepts financial wire data in transit (Confidentiality). A bank's payment service goes down on payroll Friday (Availability). Three entirely different classes of failure with no common vocabulary to reason about them.

**THE INVENTION MOMENT:** NIST and US Department of Defense frameworks in the 1970s–80s crystallized security requirements into exactly three orthogonal dimensions. The CIA Triad was not invented in one moment - it was distilled from operational failures into the simplest model that covers every class of security failure.

**EVOLUTION:** The Parkerian Hexad (1998) extended the triad with Possession, Authenticity, and Utility. NIST CSF, ISO 27001, CIS Controls, and the OWASP ASVS all map their controls back to CIA properties. Modern cloud architectures (AWS Well-Architected, Google SRE) embed CIA as foundational design constraints. The triad remains the entry point for every security conversation.

---

### 📘 Textbook Definition

The **CIA Triad** is a widely accepted model in information security that identifies three fundamental properties any secure system must maintain:

- **Confidentiality** - Information is disclosed only to parties authorized to access it.
- **Integrity** - Information is accurate, complete, and modified only by authorized processes.
- **Availability** - Information and systems are accessible to authorized users whenever needed.

Every security control, policy, audit requirement, and risk assessment maps to one or more of these three properties. Every known security incident violates at least one of them.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Secret, correct, accessible - security means guaranteeing all three simultaneously.

> Think of a bank vault: only authorized staff can open it (Confidentiality), the cash inside matches the ledger exactly (Integrity), and the vault opens reliably every business day (Availability).

**One insight:** The triad is a design framework, not a checklist. Adding encryption improves Confidentiality but risks Availability if key management fails. Replicating data everywhere improves Availability but increases the Confidentiality attack surface. The triad forces these trade-offs into the open so teams decide deliberately rather than accidentally.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Confidentiality: No unauthorized entity learns the contents of protected information.
2. Integrity: No unauthorized entity modifies protected information, and all modifications by authorized entities are traceable.
3. Availability: Authorized entities can access protected information within the agreed service level at all times.

**DERIVED DESIGN:**

- Encryption → Confidentiality
- Cryptographic hashes, digital signatures → Integrity
- Replication, load balancing, circuit breakers → Availability
- Access control (RBAC, ABAC) → Confidentiality + Integrity
- Audit logs → Integrity (non-repudiation)
- Rate limiting → Availability (against DoS)

**THE TRADE-OFFS:**

- **Gain:** A complete, orthogonal classification of every security requirement. No security failure falls outside the triad.
- **Cost:** The three properties conflict. Perfect encryption with customer-managed keys destroys Availability if keys are lost. Maximizing uptime through broad replication expands the Confidentiality attack surface.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** The conflict between secrecy, correctness, and accessibility is mathematically fundamental. A system cannot maximize all three simultaneously - choices must be made.
- **Accidental:** Complex HSM key management, multi-region replication topologies, and zero-downtime deployment pipelines are engineering implementations of CIA properties - they can be simplified with better tooling.

---

### 🧪 Thought Experiment

**SETUP:** You are building a medical records system serving 5,000 doctors across 200 hospitals, storing 10 million patient records.

**WHAT HAPPENS WITHOUT CIA TRIAD:** You optimize purely for developer convenience. Records stored in plaintext in a single database. All authenticated users can read all records. No checksums, no audit log. A disgruntled employee exports 500,000 records - Confidentiality breached. A software bug silently changes medication dosages - Integrity breached. A hardware failure during peak hours takes the system down for 6 hours - Availability breached. You have no framework to anticipate, detect, or explain any of these failures during design.

**WHAT HAPPENS WITH CIA TRIAD:** At design time, the CIA Triad forces three explicit conversations. Confidentiality: Who is authorized to see which records? Use field-level encryption and RBAC. Integrity: How do we know records haven't been tampered with? Use audit logs with tamper-evident hashing. Availability: What is the acceptable downtime? Design for 99.99% with active-active DB replication.

**THE INSIGHT:** The CIA Triad converts vague "we need security" requirements into concrete, testable design decisions. Each property generates a set of controls, and each control can be verified independently.

---

### 🧠 Mental Model / Analogy

> Think of a national archive: access is restricted to credentialed researchers only (Confidentiality), documents are stored in original form with tamper-evident seals and chain-of-custody logs (Integrity), and the archive has backup power, redundant storage facilities, and clear disaster recovery plans so researchers can always access what they need (Availability).

Element mapping:

- Access restrictions for credentialed researchers → Confidentiality (ACLs, encryption)
- Tamper-evident seals and chain-of-custody → Integrity (checksums, digital signatures, audit logs)
- Backup power and redundant sites → Availability (HA clusters, replication, failover)
- Librarian verifying credentials → Authentication, serving all three properties

Where this analogy breaks down: a physical archive operates at human speed; digital systems must enforce all three CIA properties simultaneously at millisecond latency under millions of concurrent requests, which creates engineering challenges that have no physical analog.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Security has three goals: keep secrets secret, keep data correct, and keep systems working. "CIA" is just the initials for these three goals: Confidentiality, Integrity, and Availability. If any one of these fails, you have a security problem.

**Level 2 - How to use it (junior developer):**
Use CIA as a review checklist for every feature. Does this change affect who can see the data? (Confidentiality) Could it corrupt or alter data unexpectedly? (Integrity) Could it cause downtime or degrade performance? (Availability) Run these three questions against every PR that touches security-sensitive paths.

**Level 3 - How it works (mid-level engineer):**
CIA is a control classification system. Map every security control you implement to the property it addresses. TLS protects Confidentiality and Integrity in transit. Database transactions protect Integrity. Auto-scaling protects Availability. Threat modeling maps attacker actions to CIA violations: a SQL injection attack violates both Confidentiality (data exfiltration) and Integrity (data modification). This mapping lets you identify gaps - if a threat has no countermeasure, a CIA property is unprotected.

**Level 4 - Why it was designed this way (senior/staff):**
The CIA Triad's power comes from its orthogonality: no property implies the other two. A system can have perfect Confidentiality (all data encrypted at rest and in transit) while having zero Integrity protection (encrypted data is silently corrupted with no detection) and poor Availability (single point of failure). This means every property must be verified independently. At the organizational level, CIA drives security investment: HIPAA and GDPR mandate Confidentiality; PCI DSS mandates Integrity; SLAs and operational requirements mandate Availability. Understanding which CIA property drives a compliance requirement helps you scope security work precisely.

**Expert Thinking Cues:**

- When evaluating a new third-party library, ask: what does it do to each CIA property if it is compromised?
- SLAs are Availability commitments with financial penalties. Treat them as security requirements.
- Ransomware attacks all three CIA properties simultaneously: it encrypts your data (Confidentiality violated by attacker holding the key), corrupts your access (Integrity of the access control system violated), and locks you out (Availability destroyed).

---

### ⚙️ How It Works (Mechanism)

Each CIA property is enforced through a distinct class of mechanisms:

**Confidentiality mechanisms:**

- Symmetric encryption at rest (`AES-256-GCM`)
- Transport encryption (`TLS 1.3`)
- Access control lists (ACL), RBAC, ABAC
- Data masking, tokenization, pseudonymization
- Network segmentation, VPCs, zero-trust micro-segmentation

**Integrity mechanisms:**

- Cryptographic hash functions (`SHA-256`, `SHA-3`)
- Digital signatures (`RSA`, `ECDSA`, `Ed25519`)
- ACID database transactions with constraint enforcement
- HMAC for message authentication
- Append-only, tamper-evident audit logs
- Code signing and artifact verification in CI/CD

**Availability mechanisms:**

- Active-active and active-passive clustering
- Geographic load balancing (DNS-level)
- Auto-scaling groups with health checks
- Circuit breakers and bulkhead patterns
- Rate limiting and DDoS mitigation (CDN, WAF)
- Backup and recovery with defined RTO and RPO

Controls frequently serve multiple properties simultaneously. TLS provides Confidentiality (encryption) and Integrity (HMAC on each record). Strong authentication feeds all three: it prevents unauthorized reads (C), unauthorized writes (I), and resource exhaustion by anonymous users (A).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client sends request
    |
    v
[TLS handshake]          (C: encrypted channel, I: MAC)
    |
    v
[Authentication]         (C: only known users proceed)
    |
    v
[Authorization check]    (C+I: only permitted operations)
    |
    v
[Business logic]         <- YOU ARE HERE
    |
    v
[DB write with txn]      (I: ACID, audit log appended)
    |
    v
[Encrypted response]     (C: data masked to caller scope)
    |
    v
[Replicated to standby]  (A: data durable if primary fails)
```

**FAILURE PATH:**

- TLS misconfiguration → Confidentiality breach (cleartext data in transit)
- Skipped auth check → Confidentiality + Integrity breach (unauthorized access)
- Missing transaction → Integrity breach (partial writes corrupt state)
- No replication → Availability breach (single point of failure)

**WHAT CHANGES AT SCALE:**
At 1M req/s, Availability becomes the dominant engineering challenge. CAP theorem forces a choice between Consistency (Integrity) and Availability under network partition. Confidentiality at scale requires a distributed key management system (KMS, HashiCorp Vault) - a new availability dependency. Integrity at scale requires distributed audit pipelines that do not become bottlenecks.

---

### 💻 Code Example

**BAD - No CIA controls:**

```python
# No encryption, no auth, no audit, no redundancy check
def get_patient_record(patient_id):
    return db.execute(
        f"SELECT * FROM patients WHERE id={patient_id}"
    ).fetchone()
```

Problems: SQL injection violates Integrity and Confidentiality. No authentication check. No audit trail. No error handling for DB unavailability.

**GOOD - CIA-aware implementation:**

```python
def get_patient_record(
    patient_id: str,
    user: AuthenticatedUser,
    db: DBConnection
) -> PatientRecord:
    # Confidentiality: enforce authorization before data access
    if not user.has_permission("read:patients"):
        raise PermissionError("Access denied")

    # Integrity: parameterized query prevents injection
    record = db.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    if record is None:
        raise NotFoundError(f"Patient {patient_id} not found")

    # Integrity: append-only audit trail
    audit_log.record(
        actor=user.id,
        action="READ",
        resource=f"patient:{patient_id}",
        timestamp=utcnow()
    )

    # Confidentiality: return only fields permitted for this role
    return record.project(user.allowed_fields)
```

**How to test / verify correctness:**

- **C:** Call without valid auth token → expect `403 Forbidden`
- **I:** Send `patient_id="1 OR 1=1"` → verify query is parameterized, not injected
- **A:** Kill primary DB replica → verify read succeeds on standby within SLA

---

### ⚖️ Comparison Table

| Property        | Threat Countered          | Primary Controls              | Breach Example               |
| --------------- | ------------------------- | ----------------------------- | ---------------------------- |
| Confidentiality | Eavesdropping, data theft | Encryption, RBAC              | Unencrypted S3 bucket leaked |
| Integrity       | Tampering, corruption     | Hashing, signatures           | Altered financial records    |
| Availability    | DoS, hardware failure     | Redundancy, HA, rate limiting | DB outage on peak day        |

| Model           | Extends CIA With                                |
| --------------- | ----------------------------------------------- |
| Parkerian Hexad | Possession, Authenticity, Utility               |
| NIST CSF        | Identify, Protect, Detect, Respond, Recover     |
| ISO 27001       | 93 controls mapped to CIA properties            |
| OWASP ASVS      | Application-layer CIA verification requirements |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| "Security is only about hackers"               | Accidental failures (bugs, hardware faults, misconfiguration) violate CIA properties just as attacks do                         |
| "Encryption solves security"                   | Encryption addresses only Confidentiality; Integrity and Availability require entirely separate controls                        |
| "Availability is an ops concern, not security" | DDoS is a security attack targeting Availability; it is firmly within the security domain                                       |
| "The three properties always align"            | They frequently conflict - stronger encryption without key backup can destroy Availability                                      |
| "CIA is outdated; use NIST CSF instead"        | NIST CSF, ISO 27001, and every modern framework is built on top of CIA - they are extensions, not replacements                  |
| "A system is secure if it has a firewall"      | A firewall addresses Confidentiality and Integrity; it does nothing for Availability against insider threats or data corruption |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Confidentiality Breach**

- **Symptom:** Sensitive data appears in application logs, error messages, or HTTP responses visible to unauthorized users. Reported in breach notifications.
- **Root Cause:** Missing encryption, over-broad IAM permissions, or sensitive data logged for debugging.
- **Diagnostic:**

```bash
# Find unencrypted S3 buckets in AWS account
aws s3api list-buckets --query 'Buckets[].Name' \
  --output text | xargs -I {} aws s3api \
  get-bucket-encryption --bucket {} 2>&1

# Find public RDS snapshots
aws rds describe-db-snapshots \
  --query 'DBSnapshots[?PubliclyAccessible==`true`]'
```

- **Fix:** Enable server-side encryption; audit and restrict IAM policies; strip sensitive fields from logs.
- **Prevention:** Automated compliance scanning (AWS Config rules, Checkov, tfsec) in every CI/CD pipeline run.

**Mode 2 - Integrity Violation**

- **Symptom:** Data inconsistencies discovered by users; checksums fail; audit log shows unexpected modifications; financial totals do not reconcile.
- **Root Cause:** Missing input validation, no write integrity checks, compromised privileged account writing directly to the database.
- **Diagnostic:**

```bash
# Verify critical file has not been tampered with
sha256sum /etc/passwd | diff - /var/security/passwd.sha256

# Find unexpected DB writes outside application account
SELECT actor, action, resource, timestamp
FROM audit_log
WHERE action IN ('UPDATE','DELETE')
  AND actor NOT IN (SELECT id FROM app_service_accounts)
ORDER BY timestamp DESC LIMIT 50;
```

- **Fix:** Add HMAC or digital signatures to critical records; enforce write access only through the application service account; enable point-in-time recovery.
- **Prevention:** Immutable audit logs stored in separate account; database-level triggers for sensitive tables; signed artifacts throughout the build pipeline.

**Mode 3 - Availability Failure (Security Angle)**

- **Symptom:** System unreachable; response times spike to timeouts; health checks all fail simultaneously; dashboards show zero traffic inbound but high CPU.
- **Root Cause:** DDoS volumetric attack, or cascading failure triggered by a single dependency with no circuit breaker.
- **Diagnostic:**

```bash
# Check connection flood signatures
ss -s
netstat -an | grep SYN_RECV | wc -l

# Check WAF rule hits (AWS WAF)
aws wafv2 get-sampled-requests \
  --web-acl-arn <arn> \
  --rule-metric-name <metric> \
  --scope CLOUDFRONT \
  --time-window StartTime=<ts>,EndTime=<ts> \
  --max-items 100
```

- **Fix:** Enable CDN-level DDoS protection (CloudFront + AWS Shield); implement circuit breakers with Resilience4j or similar; auto-scale on traffic surge metrics.
- **Prevention:** Load test to establish baselines; chaos engineering for failure injection; auto-scaling policies; DDoS runbook with escalation contacts.

**Security Failure Mode - Ransomware (all three violated):**

- **Symptom:** Files replaced with encrypted versions; ransom note appears; backups targeted and deleted before encryption.
- **Root Cause:** Malware executing with write-all privileges; no immutable backup strategy; no EDR detection.
- **Fix:** Restore from immutable offline backup (S3 Object Lock COMPLIANCE mode). Rotate all credentials. Invoke incident response plan.
- **Prevention:** Least-privilege for service accounts; immutable backups with MFA-delete disabled; endpoint detection and response (EDR); network segmentation to limit blast radius.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Basic networking: what TCP/IP, HTTP, and TLS are
- What a database, file system, and web server are at a high level
- What the word "authentication" means colloquially

**Builds On This (learn these next):**

- [[SEC-002 - Authentication vs Authorization]] - the primary mechanism for enforcing Confidentiality and Integrity at the identity layer
- [[SEC-005 - Defense in Depth]] - applies CIA properties across multiple independent security layers
- [[SEC-008 - Threat Modeling]] - uses CIA as the classification system for attacker capabilities and impacts

**Alternatives / Comparisons:**

- [[SEC-055 - OWASP Top 10]] - a complementary classification of the most common web application vulnerabilities, many of which map to CIA violations
- Parkerian Hexad - extends CIA with Possession, Authenticity, and Utility (used in some academic contexts)
- NIST Cybersecurity Framework - organizes security functions (Identify, Protect, Detect, Respond, Recover) around CIA as the underlying property set

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS   | Three core security properties: C, I, A   |
| PROBLEM      | No shared vocabulary for security goals    |
| KEY INSIGHT  | Every breach violates C, I, or A (or all)  |
| USE WHEN     | Designing, reviewing, or auditing systems   |
| AVOID WHEN   | Used as a substitute for a threat model     |
| TRADE-OFF    | C, I, A conflict - choose trade-offs wisely |
| ONE-LINER    | Secret, correct, accessible - guarantee all |
| NEXT EXPLORE | SEC-008 Threat Modeling                    |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Every security failure maps to a violation of Confidentiality, Integrity, or Availability.
2. The three properties conflict - maximizing one can harm another; decide deliberately.
3. CIA is a design framework: use it to justify every security control you add or skip.

**Interview one-liner:** "The CIA Triad is the foundation of information security: Confidentiality ensures only authorized parties access data, Integrity ensures data is accurate and unmodified, and Availability ensures authorized users can access systems when needed - every security requirement maps to one of these three."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Any system protecting a shared resource must explicitly address three orthogonal questions: who can access it, can the content be trusted as unmodified, and is it reliably reachable? This pattern repeats across every domain that manages shared, valuable resources.

**Where else this pattern appears:**

- **Physical security systems:** Lock and access badge (C) + tamper-evident seals and change logs (I) + backup power and redundant access routes (A)
- **Financial systems:** PIN and encryption (C) + double-entry bookkeeping and reconciliation (I) + 24/7 ATM uptime SLA (A)
- **Distributed databases:** Encryption in transit and at rest (C) + consensus protocol ensuring consistent writes (I) + multi-region replication (A)

---

### 💡 The Surprising Truth

The most frequently violated CIA property - measured by business impact - is not **Confidentiality** but **Availability**. Ransomware's primary weapon is availability destruction: locking files so the business cannot operate. Most high-profile incidents (hospital diversions, airline groundings, payment outages) involve availability failures. Yet security budgets in most organizations are allocated predominantly to confidentiality controls (encryption, DLP, SIEM), leaving availability as the chronically underfunded property. The irony is that an availability failure is often more immediately visible and costly than a data breach, which can go undetected for months.

---

### 🧠 Think About This Before We Continue

1. **[A - System Interaction]** If you encrypt every field in a production database with a customer-managed key (BYOK), and the customer permanently loses access to that key, which CIA property is violated - and how does this interact with the organization's legal obligation to retain audit records?
   _Hint:_ Think about what "authorized access" means when the authorized party themselves cannot decrypt the data, and consider the GDPR right to erasure vs. the requirement to retain audit trails.

2. **[B - Scale]** At 10 million concurrent users, the CAP theorem forces a choice between Consistency and Availability during a network partition. Which CIA properties are in direct conflict in this scenario, and what are the business consequences of choosing each side?
   _Hint:_ Look up the CAP theorem and map its C and A to the CIA Triad's I (Integrity requires consistency) and A (Availability requires uptime regardless of partition).

3. **[F - Comparison]** Ransomware attacks all three CIA properties simultaneously. If you had to defend against ransomware using only controls targeting a single CIA property, which property's controls would give you the best overall protection - and why?
   _Hint:_ Think about immutable backups (A), file integrity monitoring (I), and endpoint access control (C), and consider which one makes the attack completely reversible.
