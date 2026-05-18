---
id: DST-071
title: Compliance and SLAs in Distributed Systems
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-005, DST-055
used_by: []
related: DST-005, DST-006, DST-055, DST-056
tags:
  - distributed
  - compliance
  - sla
  - slo
  - sre
  - availability
  - data-residency
  - gdpr
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/distributed-systems/compliance-and-slas/
---

⚡ TL;DR - SLA (Service Level Agreement) is a
contract with a customer; SLO (Service Level
Objective) is an internal engineering target always
stricter than SLA; error budget = (1 - SLO) * time,
the amount of downtime you can spend before breaching
the SLO; compliance in distributed systems adds
data residency (data must stay in X region),
audit logging (immutable, tamper-evident), and
retention/deletion requirements that constrain
architecture choices for sharding, replication,
and storage tiering.

---

### 📋 Entry Metadata

| #071 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Availability, Observability | |
| **Used by:** | N/A (architectural considerations) | |
| **Related:** | Availability Patterns, Observability, Performance Tuning | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed system is designed for performance and
availability but ignores compliance. GDPR requires
EU user data to stay in EU. The system replicates
globally without geographic constraints. A data
residency audit finds EU data replicated to US nodes.
Regulatory fine: 4% of global annual revenue.

Alternatively: the engineering team commits to 99.99%
uptime in the SLA. Internally, the SLO is also 99.99%.
The system hits exactly 99.99% uptime. Every incident
consumes the entire error budget. Engineers are
perpetually on the edge of SLA breach, with no buffer
for planned maintenance, testing, or unexpected events.

Good SLA/SLO/compliance design is architecture design:
data residency constrains sharding strategies;
SLOs constrain release processes; error budgets
create the right incentives for reliability work.

---

### 📘 Textbook Definition

**SLA (Service Level Agreement):** a legally binding
contract between a service provider and a customer
specifying the minimum service level (availability,
latency, support response time). Breach triggers
penalties (credits, refunds, contract termination).

**SLO (Service Level Objective):** an internal
engineering target, always stricter than the SLA.
If SLA = 99.9%, SLO = 99.95%. The gap between SLO
and SLA is the buffer that prevents SLA breach.

**SLI (Service Level Indicator):** the metric used
to measure whether the SLO is being met. Common SLIs:
availability (successful requests / total requests),
latency (P99 response time), error rate.

**Error budget:** `(1 - SLO) * duration`
For SLO 99.9% over 30 days: 0.1% * 30 days = 43.2 minutes
of allowed downtime.

---

### ⏱️ Understand It in 30 Seconds

```
SLA/SLO/SLI HIERARCHY:

SLA: 99.9% availability (customer contract)
  SLO: 99.95% availability (internal target)
    SLI: measured availability (what we observe)

Error budget (monthly, SLO 99.95%):
  = (1 - 0.9995) * 30 * 24 * 60 = 21.6 minutes

If SLI drops below SLO threshold:
  Error budget is consuming.
  Feature freeze: no new deploys until budget recovers.
  This is the "error budget policy" incentive.

COMPLIANCE CONSTRAINTS ON ARCHITECTURE:

DATA RESIDENCY (GDPR, CCPA, LGPD):
  "EU user data must stay in EU."
  Constraint: cannot replicate EU user data to US nodes.
  Architecture: separate partition key by region.
    user_id → hash → EU nodes only (for EU users).
  
AUDIT LOGGING:
  "All data access must be logged immutably."
  Constraint: audit logs must be tamper-evident.
  Architecture: append-only log to separate storage
    (e.g., AWS CloudTrail, immutable S3 bucket).

RETENTION / RIGHT TO ERASURE (GDPR Art. 17):
  "User can request data deletion."
  Constraint: must delete from ALL replicas, backups,
    and caches within 30 days.
  Architecture: logical deletion (mark deleted),
    periodic compaction, crypto erasure for backups
    (encrypt with per-user key; delete key = delete data).
```

---

### 🔩 First Principles Explanation

**ERROR BUDGET AS AN INCENTIVE SYSTEM:**

```
PROBLEM: Two teams in conflict.
  Dev team: wants to ship fast (more deploys).
  SRE team: wants stability (fewer deploys = fewer risks).
  
  With no error budget: SRE team always says no.
  This is adversarial. Innovation slows.

ERROR BUDGET SOLUTION:
  Error budget = the amount of risk you are allowed to
    take.
  If budget is full: you can ship faster.
  If budget is empty: you must slow down.
  The rule is automatic and applies equally to everyone.
  
  SLO: 99.95%/month = 21.6 min error budget.
  
  January: no incidents. Budget full.
  → Dev team can ship daily. SRE approves. Budget allows
    it.
  
  February: 15-minute incident. Budget: 6.6 min remaining.
  → Error budget policy kicks in: freeze all but critical
    deploys. Focus on reliability improvements.
  
  March: reliability work pays off. Budget refills.
  → Normal deploy cadence resumes.

THE KEY PROPERTY:
  Error budget removes the "SRE says no" dynamic.
  The policy (not the SRE team) says no.
  Both teams are aligned: preserve the budget.
  This creates shared incentives.
```

**DATA RESIDENCY ARCHITECTURE:**

```
REQUIREMENT: EU user data must not leave the EU.
  This is a "data residency" constraint.
  
NAIVE APPROACH (WRONG):
  Global cluster with Cassandra geo-replication.
  Consistent hashing places data on random nodes.
  EU user data may land on US nodes.
  GDPR violation.

CORRECT APPROACH: PARTITION BY REGION:

Physical setup:
  EU cluster: eu-west-1 (Ireland), eu-central-1 (Frankfurt)
  US cluster: us-east-1, us-west-2
  APAC cluster: ap-southeast-1, ap-northeast-1

Routing rule:
  user.region = "EU" → route to EU cluster
  user.region = "US" → route to US cluster
  
Data model: shard key includes region prefix.
  EU key format: "EU:user_id:data_type"
  EU consistent hash ring → only EU nodes

CROSS-REGION REFERENCES:
  When EU user references US user (e.g., shared document):
  Store a reference (not a copy) in EU.
  Reference: "us_user_id=abc123 (US cluster)".
  Don't replicate US user's data to EU.

COMPLIANCE AUDIT:
  Regular scan: verify no EU-keyed data exists on US nodes.
  Automated check in CI/CD: any schema change that
  affects partitioning must pass data-residency test.
```

**AUDIT LOGGING FOR COMPLIANCE:**

```python
# Tamper-evident audit log using hash chain
# (simplified; production uses WORM storage or
# AWS CloudTrail which provides similar guarantees)

import hashlib
import json
import time
from dataclasses import dataclass, field

@dataclass
class AuditEntry:
    timestamp: float
    actor: str          # who performed the action
    action: str         # what was done
    resource: str       # what was acted upon
    details: dict       # additional context
    previous_hash: str  # hash of previous entry
    entry_hash: str = field(default="", init=False)

    def compute_hash(self) -> str:
        content = json.dumps({
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "details": self.details,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def __post_init__(self):
        self.entry_hash = self.compute_hash()


class AuditLog:
    """
    Append-only, tamper-evident audit log.
    Each entry chains to the previous (like blockchain).
    Tampering with any entry breaks the chain.
    """

    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._genesis_hash = "0" * 64  # Empty chain start

    def append(
        self, actor: str, action: str,
        resource: str, details: dict
    ) -> AuditEntry:
        previous_hash = (
            self._entries[-1].entry_hash
            if self._entries
            else self._genesis_hash
        )
        entry = AuditEntry(
            timestamp=time.time(),
            actor=actor,
            action=action,
            resource=resource,
            details=details,
            previous_hash=previous_hash
        )
        self._entries.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """
        Verify the audit log has not been tampered with.
        Check: each entry's hash is correct AND matches
        the next entry's previous_hash.
        """
        prev_hash = self._genesis_hash
        for entry in self._entries:
            # Recompute and compare:
            recomputed = entry.compute_hash()
            if recomputed != entry.entry_hash:
                return False  # Entry data was altered
            if entry.previous_hash != prev_hash:
                return False  # Chain was broken
            prev_hash = entry.entry_hash
        return True


# Usage:
log = AuditLog()
log.append("user:alice", "READ", "document:doc-123",
           {"ip": "10.0.0.1"})
log.append("user:alice", "UPDATE", "document:doc-123",
           {"field": "title", "old": "Draft", "new": "Final"})
log.append("admin:bob", "DELETE", "document:doc-123",
           {"reason": "user-requested-erasure"})

print("Integrity:", log.verify_integrity())  # True
```

**CRYPTO ERASURE FOR GDPR RIGHT TO ERASURE:**

```python
# Problem: How do you delete user data from backups?
# Backups cannot be selectively edited.
# Solution: Encrypt per-user; delete the key.
# Without the key: data is unintelligible = effectively
# deleted (crypto erasure).

import os
from cryptography.fernet import Fernet

class CryptoErasureStore:
    """
    Per-user encryption keys stored in a key store.
    "Deleting" a user = revoking their key.
    Backup data remains encrypted but unreadable.
    """

    def __init__(self):
        self._keys: dict[str, bytes] = {}  # user_id → key

    def create_user_key(self, user_id: str) -> None:
        """Generate and store a per-user encryption key."""
        self._keys[user_id] = Fernet.generate_key()

    def encrypt_for_user(
        self, user_id: str, data: bytes
    ) -> bytes:
        """Encrypt data using the user's key."""
        key = self._keys.get(user_id)
        if not key:
            raise KeyError(f"No key for user {user_id}")
        return Fernet(key).encrypt(data)

    def decrypt_for_user(
        self, user_id: str, ciphertext: bytes
    ) -> bytes:
        """Decrypt data using the user's key."""
        key = self._keys.get(user_id)
        if not key:
            raise PermissionError(
                f"Key not found for {user_id}: "
                "user may have been erased"
            )
        return Fernet(key).decrypt(ciphertext)

    def erase_user(self, user_id: str) -> None:
        """
        GDPR Right to Erasure: delete the user's key.
        All encrypted data for this user is now
        cryptographically inaccessible. Backups
        containing encrypted data are effectively erased.
        """
        self._keys.pop(user_id, None)


# Usage:
store = CryptoErasureStore()
store.create_user_key("user:alice")
ct = store.encrypt_for_user("user:alice", b'{"name":"Alice"}')
print("Encrypted:", ct[:30], "...")

# GDPR erasure request:
store.erase_user("user:alice")

try:
    store.decrypt_for_user("user:alice", ct)
except PermissionError as e:
    print(f"Data erased: {e}")
```

---

### 🧠 Mental Model / Analogy

> An SLO with an error budget is like a fuel gauge
> for reliability. Your car has a full tank (full
> error budget). You can drive fast (deploy often,
> take risks). As the tank empties (incidents consume
> budget), you must drive more carefully (freeze
> deploys, focus on reliability). When the tank
> is empty (budget depleted), you stop driving
> (release freeze) and refuel (reliability sprint).
> The fuel gauge gives the whole team visibility
> into how much risk-taking capacity remains.
> Data residency is like a passport: each user's
> data has a "nationality" (residency requirement)
> and can only travel to authorized countries (regions).
> Your routing layer is border control.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The SLO buffer:**
SLA is the customer commitment. SLO is stricter.
The gap = buffer. You can have incidents up to the
SLO limit without breaching the SLA commitment.

**Level 2 - Error budget as incentive:**
Error budget creates shared incentives. When the
budget is full, everyone can take risks. When empty,
everyone must be conservative. This resolves the
dev vs SRE conflict without politics.

**Level 3 - Data residency constrains architecture:**
GDPR and similar regulations require user data to
stay in specific regions. This is not an afterthought
- it must be designed into the partitioning strategy
(shard key includes region), routing layer, and
replication configuration from the beginning.

**Level 4 - Audit logging must be tamper-evident:**
Compliance audit logs must be append-only and
tamper-evident. A hash chain (like Dynamo paper's
Merkle trees but applied to audit logs) ensures
that altering any historical entry breaks the chain
and is detectable.

**Level 5 - Crypto erasure solves the backup dilemma:**
GDPR's right to erasure requires deleting data from
backups within 30 days. Backups can't be selectively
edited. Crypto erasure (encrypt per-user; delete key)
means backups contain only ciphertext; without the key,
they are unintelligible. Compliance is achieved
without modifying any backup files.

---

### 💻 Code Example

*See Audit Logging and Crypto Erasure examples above
in First Principles Explanation.*

---

### ⚖️ Comparison Table

| Requirement | Architecture Implication | Wrong Approach | Correct Approach |
|---|---|---|---|
| **SLA 99.9%** | Need SLO at 99.95%+ | SLO = SLA (no buffer) | SLO = SLA + buffer (0.05-0.1%) |
| **Data residency** | Shard key must include region | Global consistent hash ignoring region | Separate regional clusters + region-prefixed keys |
| **Audit logging** | Append-only, tamper-evident storage | Logs in mutable DB table | Hash chain or WORM storage (S3 Object Lock) |
| **Right to erasure** | Crypto erasure for backups | Try to edit backup files | Per-user encryption keys; deletion = key revocation |
| **Data retention** | Tiered storage + compaction | Keep everything forever | TTL + archival + scheduled deletion |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "99.9% SLA means 99.9% SLO" | If your SLO equals your SLA, any incident immediately risks SLA breach. SLOs must be stricter than SLAs to provide a safety buffer. Best practice: SLO = SLA + 0.05% to 0.1%. |
| "GDPR compliance is just a database config" | Data residency requires architecture changes: regional partitioning, routing rules, backup policies, and ensuring cross-region references don't accidentally copy data. It's an architectural constraint, not a setting. |
| "Audit logs are just regular application logs" | Audit logs have specific properties: append-only, tamper-evident, actor identified, action logged, timestamp. Regular logs can be deleted or modified. Compliance audit logs must use WORM storage or hash chains. |
| "Deleting from all databases satisfies GDPR right to erasure" | You also need to delete from: backups, caches (Redis TTL), analytics warehouses (Redshift), logs that contain PII, and CDN edge caches. Crypto erasure is often more reliable than hunting all copies. |

---

### 🚨 Failure Modes & Diagnosis

**SLA Breach: Budget Depleted but No Alert**

**Symptom:** Customer raises SLA breach claim.
Engineering checks: monthly availability was 99.87%
(SLA = 99.9%). SLA was breached. But no alert fired.

**Root Cause:** The error budget alert threshold was
set to "alert when 50% of monthly budget consumed"
(21.6 minutes) but the single long incident
consumed 57 minutes without the alert triggering.
The alert was computing a 5-minute sliding window;
the incident was spread across two calendar periods.

**Diagnosis:**
```python
# Correct error budget alert: cumulative in period
# NOT based on a short sliding window

# WRONG:
# alert when: rate(errors_total[5m]) > threshold
# (this alerts on the RATE, not cumulative budget)

# CORRECT: track cumulative availability in period
#
# Prometheus recording rule for SLO tracking:
# record: job:slo_error_rate:30d
# expr: (
#   1 - (
#     sum(increase(http_requests_total{code!~"5.."}[30d]))
#     /
#     sum(increase(http_requests_total[30d]))
#   )
# )
#
# Alert when budget > 50% consumed:
# expr: job:slo_error_rate:30d > (1-0.9995) * 0.5
# This fires when you have used 50% of your monthly budget.
```

**Fix:** Use SLO tracking based on cumulative windows
(7-day, 30-day), not instantaneous rate windows.
Implement a multi-window alert: fast (1h) for
immediate incidents, slow (30d) for budget tracking.

---

### 🔗 Related Keywords

**Prerequisites:** `Availability Patterns` (DST-005),
`Observability in Distributed Systems` (DST-055)

**Related:** `Distributed Systems Performance Tuning`
(DST-056)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SLA → SLO → SLI HIERARCHY                               │
│   SLA: customer contract (99.9%)                        │
│   SLO: internal target (99.95%) - STRICTER              │
│   SLI: measured metric (actual availability %)          │
│   Error budget: (1-SLO) * period = allowed downtime    │
├─────────────────────────────────────────────────────────┤
│ DATA RESIDENCY: shard key includes region              │
│   EU user → EU cluster only; no cross-region copy      │
├─────────────────────────────────────────────────────────┤
│ AUDIT LOG: append-only + hash chain                    │
│   WORM storage (S3 Object Lock) or hash chain          │
├─────────────────────────────────────────────────────────┤
│ GDPR ERASURE: crypto erasure                           │
│   Per-user key → delete key → data unintelligible      │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The error budget framework reveals a general principle:
quantify the risk you are willing to take, then
create incentives that automatically enforce it.
Without an error budget, reliability vs velocity
is a human negotiation with no objective standard.
With an error budget, the question "can we deploy
today?" has a measurable answer. This principle
transfers to other system design decisions: capacity
planning (quantify headroom as a budget: 70%
utilization = 30% capacity budget remaining),
security vulnerability response (CVSS score = risk
budget; critical vulnerabilities consume budget
immediately), and technical debt (quantify as
a "complexity budget" that slows feature velocity
as it grows). Wherever humans make trade-off
decisions under time pressure, a quantified budget
with visible consumption creates better decisions
than individual judgment.

---

### 💡 The Surprising Truth

Many engineering teams conflate SLA and SLO, setting
both to the same value. This is the worst possible
configuration. If your SLO equals your SLA, every
incident that consumes any availability puts you
at risk of SLA breach. You have no buffer. You cannot
run any planned maintenance without risking breach.
You cannot take any risk at all.

Google SRE discovered that the gap between SLO and
SLA is as important as the SLO itself. They found
that setting SLO 10-50% stricter than SLA (in error
budget terms) created the right balance: enough
buffer for planned maintenance and unexpected events,
while still requiring genuine reliability work to
maintain. For a 99.9% SLA, a 99.95% SLO gives you
21.6 minutes vs 43.2 minutes of monthly budget -
a meaningful safety net. Most teams discover this
the hard way when a single incident that seemed
within normal bounds triggers an SLA credit.

---

### ✅ Mastery Checklist

1. [CALCULATE] Your SLA is 99.9% monthly. What SLO
   gives you a 50% buffer? How many minutes of
   downtime does this allow? How many incidents of
   5 minutes each?
2. [DESIGN] A multi-region system with EU and US
   users. How do you partition data to comply with
   GDPR data residency? What happens when an EU user
   shares a document with a US user?
3. [IMPLEMENT] Add a hash chain to an audit log.
   Verify that altering any historical entry is
   detectable by the integrity check.
4. [EXPLAIN] GDPR right-to-erasure. Why can't you
   just delete from the database? What about S3
   backups from 15 days ago? How does crypto erasure
   solve this?
5. [DECIDE] A team wants to use a 1-hour sliding
   window to track SLO compliance. Why is this
   insufficient? What window(s) are required for
   proper SLO tracking?
