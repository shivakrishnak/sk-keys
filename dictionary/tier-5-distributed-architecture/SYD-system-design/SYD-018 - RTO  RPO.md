---
id: SYD-018
title: "RTO / RPO"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-015, SYD-017
used_by: SYD-022
related: SYD-015, SYD-016, SYD-017, SYD-022, SYD-023
tags:
  - architecture
  - reliability
  - disaster-recovery
  - data
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /syd/rto-rpo/
---

# SYD-018 - RTO / RPO

⚡ TL;DR - RTO (Recovery Time Objective) is the maximum
acceptable downtime after a failure; RPO (Recovery Point
Objective) is the maximum acceptable data loss measured
in time. These two numbers dictate the disaster recovery
architecture: low RTO requires hot standby or fast
failover; low RPO requires synchronous replication
or continuous backup. Each zero adds a zero to the cost.

| #018 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | SLA / SLO / SLI, MTTR / MTBF | |
| **Used by:** | Disaster Recovery | |
| **Related:** | SLA / SLO / SLI, Error Budget, MTTR / MTBF, Disaster Recovery, Geo-Replication | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A business says: "our data cannot be lost." An engineer
says: "OK, we will back up hourly." A disaster happens,
they restore from a 59-minute-old backup. The business
loses an hour of transactions and is furious. The
engineer thought "backup hourly" satisfied the
requirement. The business meant "no data loss."
Without explicit, numeric RTO and RPO definitions,
the disaster recovery investment is misaligned with
business expectations. The conversation about
acceptable loss never happened until after the loss.

**THE BREAKING POINT:**
Building the wrong DR architecture is expensive in
both directions: over-engineer (synchronous multi-region
replication for a weekly batch job) or under-engineer
(single daily backup for a financial transaction system).
Without RTO and RPO, there is no objective criteria
for "enough" disaster recovery investment.

---

### 📘 Textbook Definition

**RTO (Recovery Time Objective):** The maximum
acceptable time from the start of a disaster to full
service restoration. The business-agreed answer to:
"how long can we be down?" Expressed in time units
(minutes, hours, days). Drives recovery mechanism
design: short RTO requires warm/hot standby; long RTO
allows cold backups and manual restoration.

**RPO (Recovery Point Objective):** The maximum
acceptable data loss measured in time. The answer to:
"how much data can we lose?" An RPO of 1 hour means
the system can tolerate losing at most the last 1 hour
of data. Drives replication strategy: RPO of 0 requires
synchronous replication; RPO of 1 hour allows hourly
backups. Expressed in time units.

**Relationship to cost:**
As RTO and RPO approach zero, cost approaches infinity.
They represent the business's risk tolerance translated
into architecture constraints.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
RTO: how fast do we recover? RPO: how much data do we
lose? Both drive how much DR infrastructure to build.

**One analogy:**
> Saving a document:
> - RPO: how often you press Ctrl+S. If the power
>   fails, you lose work since the last save.
>   "Autosave every 5 minutes" = RPO of 5 minutes.
> - RTO: how long to reopen the app and restore
>   the file after the power comes back.
>   "Reboot + restore = 3 minutes" = RTO of 3 minutes.
>
> To reduce RPO to 0: save every keystroke (continuous
> sync, expensive). To reduce RTO to 0: never close
> the app (always-on standby, expensive).

**One insight:**
RTO and RPO are independent. You can have low RPO
(synchronous replication keeps all data) but high RTO
(failover is manual, takes 4 hours). Or high RPO but
low RTO (hot standby ready instantly, but last 1-hour
transactions may be lost). Design each independently
based on business requirements.

---

### 🔩 First Principles Explanation

**THE COST-FUNCTION RELATIONSHIP:**

```
┌──────────────────────────────────────────────────────┐
│ RTO vs DR Architecture Cost                         │
│                                                      │
│ RTO > 24 hours: Cold backup/restore                  │
│   Cost: $        (storage only)                      │
│   Mechanism: restore from nightly backup to new host │
│                                                      │
│ RTO 1-24 hours: Warm standby                         │
│   Cost: $$       (secondary running, not serving)    │
│   Mechanism: sync replica, manual failover           │
│                                                      │
│ RTO < 1 hour: Warm standby + automation              │
│   Cost: $$$      (auto-failover, runbooks)           │
│   Mechanism: read replica, automated DNS switch      │
│                                                      │
│ RTO < 5 minutes: Hot standby / multi-active          │
│   Cost: $$$$     (full capacity in both regions)     │
│   Mechanism: active-active or instant failover       │
│                                                      │
│ RTO = 0 (zero): Active-active multi-region           │
│   Cost: $$$$$    (2x+ infrastructure everywhere)    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ RPO vs Replication Strategy                          │
│                                                      │
│ RPO > 24 hours: Daily backup                         │
│   Risk: up to 24 hours of data loss                  │
│   Mechanism: daily dump to object storage            │
│                                                      │
│ RPO 1-24 hours: Hourly / incremental backup          │
│   Risk: up to 1 hour of data loss                    │
│   Mechanism: WAL archiving or logical replication    │
│                                                      │
│ RPO 1-60 minutes: Continuous replication             │
│   Risk: minutes of data loss                         │
│   Mechanism: async streaming replication             │
│                                                      │
│ RPO < 1 minute: Synchronous replication              │
│   Risk: seconds of data loss (replication lag)       │
│   Mechanism: synchronous writes to replica(s)        │
│   Cost: write latency penalty = sync ack overhead    │
│                                                      │
│ RPO = 0 (zero): Synchronous multi-region writes      │
│   Risk: no data loss                                 │
│   Mechanism: distributed transaction / consensus     │
│   Cost: significantly higher write latency           │
└──────────────────────────────────────────────────────┘
```

**INTERACTION BETWEEN RTO AND RPO:**
They are often set by different business stakeholders:
- RPO is set by data owners ("we cannot lose a
  financial transaction" → RPO = 0)
- RTO is set by operations/product ("users can wait
  5 minutes" → RTO = 5 minutes)
- Architecture must satisfy both independently.

**THE TRADE-OFFS:**
**Low RPO (synchronous replication):**
Gain: near-zero data loss.
Cost: write latency penalty (must wait for replica
acknowledgement before returning to caller). A
cross-region synchronous write adds 50-150ms per
write transaction.

**Low RTO (hot standby):**
Gain: instant failover; users barely notice.
Cost: full duplicate capacity required in standby
region. 2x infrastructure cost at minimum.

**Zero RPO + Zero RTO:** Near-impossible without
distributed consensus protocols. Systems that claim
this (some cloud DB offerings) achieve it at 5-10x
cost of standard deployments.

---

### 🧪 Thought Experiment

**SCENARIO: Four different services, same company,
vastly different RTO/RPO requirements**

**Payment processing API:**
- Business requirement: "We cannot lose a payment"
- RPO = 0 (no transactions can be lost)
- RTO = 5 minutes (payments are critical; brief
  outage acceptable; fraud impact is bigger)
- Architecture: synchronous multi-region DB writes
  + hot standby + automated failover

**Marketing analytics dashboard:**
- Business requirement: "If it is down for a day,
  we will use exports"
- RPO = 24 hours (daily data loss acceptable)
- RTO = 8 hours (business hours only)
- Architecture: daily backup to S3 + restore playbook

**User profile service:**
- Business requirement: "Don't lose account data;
  can be slow for a few minutes"
- RPO = 5 minutes (recent profile changes acceptable)
- RTO = 30 minutes (login issues acceptable briefly)
- Architecture: async streaming replication
  + semi-automated failover

**Real-time trading platform:**
- Business requirement: "Every millisecond offline
  costs money; every lost order is a legal issue"
- RPO = 0, RTO < 30 seconds
- Architecture: active-active multi-region, zero-RPO
  distributed consensus, instant health-check-driven
  failover

**THE INSIGHT:** The four services co-exist in the
same company. Applying payment-grade DR to the marketing
dashboard wastes money. Applying marketing-grade DR
to payments creates business risk. Explicit RTO/RPO
per service is the only principled way to allocate
the DR budget.

---

### 🧠 Mental Model / Analogy

> RTO and RPO are the "acceptable loss" parameters
> for a business. They convert vague requirements
> like "we need reliability" into measurable engineering
> constraints.
>
> Think of them as the parameters in an insurance
> policy:
> - RPO = the deductible (data loss you agree to
>   absorb before the "insurance" kicks in via backup)
> - RTO = the maximum claim settlement time (how long
>   before service is restored)
>
> Low deductible (RPO) = higher premium (infrastructure
> cost). Faster settlement (RTO) = higher premium.
> The business sets the risk tolerance; the architect
> builds the policy.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
RTO: how long the service can be down. RPO: how much
data can be lost. Both are set by the business and
dictate the disaster recovery plan.

**Level 2 - How to use it (junior developer):**
For each service, get explicit answers from the product
team: "If a disaster happened right now, how long
would be acceptable to be unavailable? How much data
loss would be acceptable?" Translate to an integer
in minutes. Design backup/replication strategy to
meet those numbers. Document the SLA.

**Level 3 - How it works (mid-level engineer):**
RTO determines architecture (cold/warm/hot standby);
RPO determines replication strategy (async/sync/
continuous). Measure actual recovery times in DR
drills. If actual MTTR exceeds RTO in drills, the
architecture is under-built. Run DR tests at least
quarterly; document results.

**Level 4 - Why it was designed this way (senior/staff):**
The critical question: are RTO/RPO objectives or SLAs?
If they are SLAs (contractual), violating them has
financial consequences. If they are objectives, they
guide architecture. Most companies treat them as
internal targets. Enterprise contracts (B2B, financial,
healthcare) codify RTO/RPO as SLAs with penalties.
Architecture decisions must then account for the
cost of failing vs the cost of meeting the commitment.

**Level 5 - Mastery (distinguished engineer):**
Modern cloud services blur the RTO/RPO boundary.
Multi-region active-active deployments with consensus
protocols (Spanner, CockroachDB) effectively provide
RPO = 0 and RTO measured in seconds - but at the cost
of write latency and complexity. The real tradeoff
is no longer "cost vs availability" but "latency vs
consistency vs availability": CAP theorem applied
to DR. Zero-RPO requires strong consistency (CP in
CAP), which limits availability under partition.
Understanding the system's tolerance for each failure
mode guides the optimal point on the CAP triangle
for DR design.

---

### ⚙️ How It Works (Mechanism)

**DR Tier Model by RTO/RPO:**

```
┌─────────────────────────────────────────────────────┐
│                  DR TIERS                           │
│                                                     │
│ Tier 4 - Cold Standby (RTO: hours, RPO: hours)     │
│   - Backups in object storage (S3/GCS)             │
│   - No standby infrastructure running              │
│   - Recovery: provision + restore from backup      │
│   - Use case: dev/test, low-criticality batch jobs │
│                                                     │
│ Tier 3 - Warm Standby (RTO: 1h, RPO: minutes)     │
│   - Secondary region with reduced capacity running │
│   - Async replication (streaming WAL/binlog)       │
│   - Recovery: promote replica, update DNS           │
│   - Use case: internal tools, low-traffic apps     │
│                                                     │
│ Tier 2 - Hot Standby (RTO: minutes, RPO: seconds) │
│   - Full-capacity secondary, auto-failover          │
│   - Async or near-sync replication                  │
│   - Recovery: automated via health checks + DNS    │
│   - Use case: customer-facing web apps             │
│                                                     │
│ Tier 1 - Active-Active (RTO: 0, RPO: 0)            │
│   - All regions serve traffic simultaneously        │
│   - Synchronous replication or consensus protocol  │
│   - No "failover" - traffic routes around failures │
│   - Use case: payment systems, trading platforms   │
└─────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - BAD: assuming backup = DR requirement met**
```python
# BAD: set daily backup, assume RTO/RPO satisfied
# Business said "no data loss" - but this is RPO=24h
import boto3
import subprocess

def backup_database():
    """Daily cron job - runs at 2am"""
    subprocess.run([
        "pg_dump", "-U", "postgres", "mydb",
        "-f", "/tmp/backup.sql"
    ])
    s3 = boto3.client("s3")
    s3.upload_file(
        "/tmp/backup.sql",
        "my-backups",
        f"backup-{today}.sql"
    )
    # Problem: RPO = 24 hours (last backup to now)
    # RTO = time to provision new DB + restore = hours
    # Business expectation: "no data loss" = RPO = 0
    # This architecture does NOT meet that requirement
```

**Example 2 - GOOD: architect to explicit RTO/RPO targets**
```yaml
# GOOD: DR strategy explicitly linked to RTO/RPO

# service: payment-api
# RPO requirement: 0 (no transaction loss)
# RTO requirement: 5 minutes (auto-failover required)

# RDS Multi-AZ with synchronous replication = RPO ~0
resource "aws_db_instance" "payment_db" {
  identifier        = "payment-db-primary"
  engine            = "postgres"
  instance_class    = "db.r5.xlarge"

  # Synchronous standby = RPO ~0
  multi_az          = true

  # Automated backups for point-in-time recovery
  # RPO for PITR: 5-minute transaction log retention
  backup_retention_period = 7
  backup_window    = "02:00-03:00"

  # Auto-failover to standby = RTO ~2-5 minutes
  # AWS initiates automatically on primary failure
}

# Route53 health check triggers DNS failover
resource "aws_route53_health_check" "payment" {
  fqdn              = "payment-db.internal"
  type              = "TCP"
  port              = 5432
  failure_threshold = 3  # fail 3 checks before failover
  request_interval  = 10 # check every 10 seconds
  # Max time to detect: 3 × 10s = 30 seconds
  # Then DNS propagation: ~30 seconds
  # Total RTO: ~60 seconds (well under 5-min target)
}
```

**Example 3 - DR drill validation script**
```bash
#!/bin/bash
# Validate actual RTO meets target via DR drill
# Run quarterly; do not just plan - measure

set -e
TARGET_RTO_SECONDS=300  # 5-minute RTO target
TARGET_RPO_TRANSACTIONS=0  # Zero data loss target

echo "=== DR Drill: $(date) ==="

# Record test transaction just before simulated failure
LAST_TXN=$(psql -t -c "SELECT MAX(txn_id) FROM orders")
echo "Last transaction before failure: $LAST_TXN"

# Simulate primary failure (failover-only drill)
FAILOVER_START=$(date +%s)
echo "Initiating failover..."
aws rds failover-db-cluster --db-cluster-id payment-db

# Wait for new primary to become available
until aws rds describe-db-instances \
    --db-instance-identifier payment-db-secondary \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text | grep -q "available"; do
  sleep 5
done

FAILOVER_END=$(date +%s)
ACTUAL_RTO=$((FAILOVER_END - FAILOVER_START))
echo "Actual RTO: ${ACTUAL_RTO}s (target: ${TARGET_RTO_SECONDS}s)"

# Verify data integrity (RPO check)
NEW_LAST_TXN=$(psql -t -c \
    "SELECT MAX(txn_id) FROM orders" \
    --host=payment-db-secondary)
if [ "$NEW_LAST_TXN" -eq "$LAST_TXN" ]; then
    echo "RPO: PASS - no data loss"
else
    echo "RPO: WARN - last txn $LAST_TXN, found $NEW_LAST_TXN"
fi

if [ "$ACTUAL_RTO" -le "$TARGET_RTO_SECONDS" ]; then
    echo "RTO: PASS"
else
    echo "RTO: FAIL - $ACTUAL_RTO > $TARGET_RTO_SECONDS"
    # Action: escalate to architecture review
fi
```

---

### ⚖️ Comparison Table

| DR Tier | RTO | RPO | Architecture | Cost |
|---|---|---|---|---|
| Cold standby | Hours-days | Hours-days | Backup + restore | Low ($) |
| Warm standby | 1-4 hours | Minutes | Async replica | Medium ($$) |
| Hot standby | < 15 min | Seconds | Near-sync + auto-failover | High ($$$) |
| Active-active | < 1 min | Near-zero | Synchronous multi-region | Very high ($$$$) |
| Zero RTO/RPO | ~0 | 0 | Consensus protocol (Spanner-type) | Extreme ($$$$$) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| RPO = 0 requires real-time backup | RPO = 0 requires synchronous replication: the write is not acknowledged until at least one replica has confirmed it. Backup (even continuous) always has a gap. |
| RTO and RPO are the same thing | RTO = time to recover (downtime duration). RPO = data loss tolerance (how old is the oldest surviving data point). A system can have RTO = 10 minutes (fast failover) but RPO = 1 hour (async replication with 1-hour lag). |
| Setting RTO = 0 is achievable with modern cloud | Zero-RTO in the strict sense (zero downtime, no disruption) requires active-active architecture with traffic routing around failures. Most "zero downtime" claims rely on load balancer health checks, which have detection latency (10-60s). Honest claim: RTO < 60 seconds. |

---

### 🚨 Failure Modes & Diagnosis

**RPO Violation: Async Replication Lag**

**Symptom:**
After a primary DB failure, the team fails over to the
replica. On inspection, 8 minutes of transactions are
missing. RPO target was 1 minute.

**Root Cause:**
Async replication was running fine (low lag normally),
but under peak write load before the failure, the
replica had fallen 8 minutes behind. The failure
occurred exactly at a peak traffic moment.

**Diagnosis:**
```bash
# Monitor replica lag continuously, not just at rest
# PostgreSQL async replica lag:
psql -c "SELECT now() - pg_last_xact_replay_timestamp()
          AS replication_lag;"

# Alert threshold: if lag > RPO target, alert
# Do NOT wait for a disaster to check lag
# If lag is regularly > RPO target under load,
# the async replication architecture cannot
# meet the RPO requirement.
```

**Fix:**
If async lag regularly exceeds the RPO target, switch
to synchronous replication (PostgreSQL `synchronous_commit
= on`) or set an alert that blocks traffic to the
primary if replica lag exceeds the RPO threshold,
forcing the system to fail before losing more data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SLA / SLO / SLI` - RTO/RPO are often codified
  as SLAs in contracts; SLO is the internal target
- `MTTR / MTBF` - MTTR is the measured actual recovery
  time; RTO is the objective. They must align.

**Builds On This (learn these next):**
- `Disaster Recovery` - the full strategy that RTO
  and RPO define the requirements for
- `Geo-Replication` - the mechanism for meeting
  low RPO across regions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RTO            │ Max acceptable downtime                  │
│                │ Drives: failover architecture            │
├────────────────┼─────────────────────────────────────────┤
│ RPO            │ Max acceptable data loss (in time)       │
│                │ Drives: replication strategy             │
├────────────────┼─────────────────────────────────────────┤
│ COST LAW       │ Each zero added to RTO or RPO target     │
│                │ adds significant cost (10x rule of thumb)│
├────────────────┼─────────────────────────────────────────┤
│ RPO = 0        │ Requires synchronous replication         │
│                │ (write not acked until replica confirms) │
├────────────────┼─────────────────────────────────────────┤
│ RTO = 0        │ Requires active-active multi-region      │
│                │ (no failover = always serving)           │
├────────────────┼─────────────────────────────────────────┤
│ KEY INSIGHT    │ Independent axes: can have low RPO       │
│                │ (sync replication) + high RTO (manual    │
│                │ failover). Design each separately.       │
├────────────────┼─────────────────────────────────────────┤
│ ONE-LINER      │ "RTO: how fast do we recover?            │
│                │  RPO: how much data can we lose?         │
│                │  Both drive architecture + cost."        │
├────────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE   │ Disaster Recovery → Geo-Replication      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. RTO = downtime tolerance; RPO = data loss tolerance.
   Different business requirements; different solutions.
2. Lower RTO needs hot standby/active-active. Lower
   RPO needs synchronous replication. Each costs more.
3. Test actual RTO/RPO in DR drills. Targets on paper
   are not the same as reality under load.

**Interview one-liner:**
"RTO is the maximum acceptable downtime after a failure;
RPO is the maximum acceptable data loss measured in time.
They drive completely different architectural choices: RTO
drives failover architecture (cold/warm/hot standby or
active-active); RPO drives replication strategy (backup
frequency or sync vs async replication). They are
independent: a payment system might need RPO=0 but can
tolerate RTO=5min; a dashboard might tolerate RPO=24h
but needs RTO=1h for business hours. Each zero added to
either target adds significant infrastructure cost."
