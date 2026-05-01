---
layout: default
title: "RTO / RPO"
parent: "System Design"
nav_order: 693
permalink: /system-design/rto-rpo/
number: "693"
category: System Design
difficulty: ★★★
depends_on: "MTTR / MTBF, SLA / SLO / SLI"
used_by: "Disaster Recovery, Geo-Replication"
tags: #advanced, #reliability, #distributed, #architecture, #foundational
---

# 693 — RTO / RPO

`#advanced` `#reliability` `#distributed` `#architecture` `#foundational`

⚡ TL;DR — **RTO** (Recovery Time Objective) is the maximum acceptable downtime before service is restored; **RPO** (Recovery Point Objective) is the maximum acceptable data loss measured in time — both drive disaster recovery architecture decisions.

| #693            | Category: System Design            | Difficulty: ★★★ |
| :-------------- | :--------------------------------- | :-------------- |
| **Depends on:** | MTTR / MTBF, SLA / SLO / SLI       |                 |
| **Used by:**    | Disaster Recovery, Geo-Replication |                 |

---

### 📘 Textbook Definition

**Recovery Time Objective (RTO)** is the maximum tolerable length of time that a system can be unavailable after a disaster or failure before the business suffers unacceptable consequences. RTO defines the target for how quickly recovery must occur: "the system must be operational within 4 hours of a disaster." **Recovery Point Objective (RPO)** is the maximum acceptable amount of data loss measured as time: "we can tolerate losing at most 1 hour of data." RPO drives backup frequency and replication strategy — a 1-hour RPO requires continuous or near-continuous data synchronisation. **RTO drives the recovery infrastructure** (hot standby, warm standby, cold standby), and **RPO drives the data replication strategy** (synchronous replication for near-zero RPO, asynchronous for larger RPO). Tighter (smaller) RTO and RPO require significantly more investment in infrastructure, replication, and operational procedures.

---

### 🟢 Simple Definition (Easy)

RTO: "If a disaster strikes, how long can we be down?" (target: as short as possible). RPO: "If a disaster strikes, how much data can we afford to lose?" (target: as little as possible). RTO=0 means instant recovery. RPO=0 means zero data loss. Both cost money — the closer to zero, the more expensive the architecture.

---

### 🔵 Simple Definition (Elaborated)

Bank database failure at 2 PM. RTO=2 hours → must be online by 4 PM. RPO=15 minutes → can lose at most 15 minutes of transactions. Achieving RTO=2 hours: pre-built warm standby database that can take over quickly. Achieving RPO=15 minutes: database logs replicated to standby every 15 minutes (or continuously). A different business (blog): RTO=24 hours (outage is inconvenient, not catastrophic), RPO=24 hours (daily backup sufficient). Architecture follows requirements.

---

### 🔩 First Principles Explanation

**RTO and RPO drive infrastructure tier selection:**

```
DISASTER RECOVERY TIERS (by RTO/RPO requirements):

TIER 1: COLD STANDBY (Backup and Restore)
  RTO: hours to days (restore from backup)
  RPO: hours to days (last backup time)
  Cost: lowest (only pay for storage, not running infrastructure)

  Implementation:
    - Daily/hourly automated backups to S3 Glacier / Azure Blob
    - On disaster: provision new infrastructure (EC2, RDS), restore backup
    - Time-consuming but cheap

  Use when: non-critical systems, batch processing, dev/test environments
  Example: Internal reporting system. 24-hour outage = tolerable.

  AWS approach:
    RDS: automated snapshots to S3 (point-in-time recovery up to 5 minutes back)
    EC2 AMI: backup AMI + CloudFormation template to recreate stack
    Restore time: 1-4 hours (restore snapshot + boot + warm up)

TIER 2: WARM STANDBY (Pilot Light)
  RTO: minutes to hours
  RPO: minutes (depends on replication lag)
  Cost: moderate (standby infrastructure running but at reduced scale)

  Implementation:
    - DR region: minimal "pilot light" (core services only, low capacity)
    - Primary DB: replication to standby DB (asynchronous, ~1 minute lag)
    - On disaster: promote standby DB to primary, scale up infrastructure
    - DNS failover: update Route53 records to point to DR region

  RTO breakdown:
    DB promotion: 1-2 minutes (read replica → primary)
    Scale up: 5-10 minutes (increase instance count/type)
    DNS propagation: 1-5 minutes (low TTL pre-set)
    Smoke testing: 5 minutes
    Total: 12-22 minutes → RTO target: 30 minutes

TIER 3: HOT STANDBY (Active-Passive)
  RTO: seconds to minutes
  RPO: seconds (synchronous replication) to minutes (async)
  Cost: high (full duplicate infrastructure running in DR region)

  Implementation:
    - DR region: identical full-capacity infrastructure, always running
    - DB: synchronous replication (RTO: seconds, RPO: near-zero)
           or asynchronous (RTO: seconds, RPO: seconds to minutes)
    - Health checks: continuous failover readiness monitoring
    - Auto failover: Route53 health check + weighted routing

  Synchronous vs. Asynchronous Replication:
    SYNCHRONOUS: write committed only when BOTH primary and secondary confirm
      RPO: 0 (zero data loss)
      Write latency: increased by network RTT to DR region
        Primary (us-east-1) → Standby (us-west-2): +60ms per write
      Use when: financial transactions, healthcare records

    ASYNCHRONOUS: write committed on primary; replicated in background
      RPO: seconds to minutes (replication lag)
      Write latency: unchanged (secondary doesn't block primary)
      Use when: e-commerce, social media (some data loss acceptable)

TIER 4: ACTIVE-ACTIVE (Multi-Region)
  RTO: 0 (no recovery needed — traffic fails over automatically)
  RPO: 0 or near-zero (all regions have current data)
  Cost: very high (multiple full-capacity regions)

  Implementation:
    - Both regions: receive live traffic (DNS load balanced)
    - DB: bidirectional replication or global distributed DB (DynamoDB Global Tables, Spanner)
    - On failure: Route53 removes failed region, surviving region absorbs all traffic
    - Users: may notice latency change but no outage

  Use when: global financial systems, critical e-commerce, safety systems

RTO/RPO vs. COST (approximate):

  RTO=24h, RPO=24h → Cold Standby → ~$200/month (storage only)
  RTO=1h,  RPO=15m → Warm Standby → ~$2,000/month (scaled-down replica)
  RTO=5m,  RPO=1m  → Hot Standby  → ~$8,000/month (full replica, async)
  RTO=0,   RPO=0   → Active-Active → ~$20,000/month (multi-region, sync)

  ROI calculation: cost of architecture vs. cost of downtime per hour
  If 1 hour outage = $100,000 revenue lost:
    Warm Standby ($2k/month) is worth it vs. Cold ($200/month) risk.
    Hot Standby ($8k/month) — calculate frequency of disaster scenarios.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT RTO/RPO:

- Disaster recovery architecture based on guesses and gut feel
- Often over-engineered (expensive) or under-engineered (unacceptable recovery)
- No SLA possible without defined recovery commitments

WITH RTO/RPO:
→ Quantified recovery requirements drive architecture decisions
→ Business and engineering aligned: "RTO=4 hours is what we need, here's what it costs"
→ SLA commitments backed by architecture that can actually deliver them

---

### 🧠 Mental Model / Analogy

> Disaster recovery for a physical library. RPO is about the card catalogue: if a fire destroys the library, how old can the backup card catalogue be? If you backed up yesterday (RPO=24 hours), you'll rebuild from yesterday's record — today's new entries are lost. RTO is about reopening: how quickly must the library reopen after a fire? RTO=1 week: rent temporary space and move backup copies. RTO=0: second library already stocked and open (active-active). Both have costs — the better the recovery, the more expensive the preparation.

"Fire destroying the library" = disaster event
"Backup card catalogue age" = RPO (data loss tolerance)
"How long library stays closed" = RTO (recovery time tolerance)
"Renting temporary space" = warm standby
"Second library already open" = active-active architecture

---

### ⚙️ How It Works (Mechanism)

**AWS RDS Multi-AZ + Read Replica for different RTO/RPO scenarios:**

```
RDS MULTI-AZ (within region) — RTO: 1-2 min, RPO: ~0
  Primary DB (us-east-1a) → Synchronous replication → Standby DB (us-east-1b)
  Automatic failover: if primary fails, standby promoted in 60-120 seconds
  RPO: ~0 (synchronous replication — no data loss)
  RTO: ~90 seconds (DNS update to new primary endpoint)
  Use: production databases with strict availability requirements

RDS READ REPLICA (cross-region) — RTO: 10-30 min, RPO: seconds to minutes
  Primary DB (us-east-1) → Asynchronous replication → Read Replica (eu-west-1)
  On disaster: manually promote replica to standalone DB in eu-west-1
  RPO: seconds to minutes (replication lag at time of failure)
  RTO: 5-20 minutes (promotion + DNS update + application config change)

AURORA GLOBAL DATABASE — RTO: <1 min, RPO: <1 second
  Primary cluster (us-east-1) → storage-level replication → Secondary (eu-west-1)
  Replication lag: typically <1 second
  Managed failover: promote secondary in ~60 seconds (or manual in ~30s)
  RPO: typically <1 second worth of transactions
  Use: global applications requiring near-zero RPO

RDS BACKUPS (Cold Standby) — RTO: hours, RPO: 5 min (PITR)
  Automated backups: daily snapshot + transaction logs
  PITR: restore to any point in time within backup retention window (up to 35 days)
  RTO: 1-4 hours (restore snapshot to new instance)
  RPO: 5 minutes (transaction log granularity)
  Use: non-critical systems, cost-sensitive workloads
```

---

### 🔄 How It Connects (Mini-Map)

```
SLA / SLO / SLI           MTTR / MTBF
(reliability targets)      (historical performance)
        │                         │
        └────────────┬────────────┘
                     ▼ (forward-looking disaster targets)
               RTO / RPO ◄──── (you are here)
               (target recovery time and data loss)
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
Disaster Recovery             Geo-Replication
(implementation)              (technique to achieve RPO)
```

---

### 💻 Code Example

**Terraform: RDS with Multi-AZ + cross-region replica for RPO/RTO:**

```hcl
# Primary RDS (Multi-AZ for within-region RTO=90s, RPO=0)
resource "aws_db_instance" "primary" {
  identifier        = "orders-primary"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.r6g.large"

  multi_az          = true        # RTO: 90s, RPO: 0 (sync replication)

  backup_retention_period = 7     # 7 days PITR (backup = RPO of cold restore)
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "orders-primary-final"
}

# Cross-region read replica (for cross-region DR: RTO=20m, RPO=seconds)
resource "aws_db_instance" "dr_replica" {
  provider            = aws.eu-west-1
  identifier          = "orders-dr-replica"
  replicate_source_db = aws_db_instance.primary.arn  # cross-region replica
  instance_class      = "db.r6g.large"

  # On disaster: promote this replica to standalone primary
  # aws rds promote-read-replica --db-instance-identifier orders-dr-replica

  backup_retention_period = 7
  skip_final_snapshot     = false
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RTO and RPO are the same concept                             | RTO is about TIME to recover (how long your system is unavailable). RPO is about DATA loss (how much data is acceptable to lose). A system can have short RTO but high RPO (fast recovery but from an old backup), or vice versa. They require different architectural solutions |
| RTO=0 is achievable with active-active                       | Active-active greatly reduces RTO but rarely achieves true zero. DNS propagation (even with low TTL), connection draining, and in-flight requests mean a brief disruption. "Near-zero RTO" (seconds) is achievable; strict zero is a theoretical construct                       |
| RPO=0 requires synchronous replication across all components | Synchronous replication achieves RPO=0 for the database, but in-memory state (caches, queues), in-flight transactions, and client-side state may still be lost. Full RPO=0 requires all state to be durably committed before acknowledging to clients                            |
| Higher RTO/RPO is always fine for internal tools             | Even "internal" tools can have critical business processes: payroll, financial reporting, customer support systems. GDPR/compliance requirements may mandate specific recovery capabilities. Always validate RTO/RPO against actual business impact                              |

---

### 🔥 Pitfalls in Production

**DR test skipped → RTO target unachievable when needed:**

```
PROBLEM:
  Architecture: Cross-region warm standby.
  Documented RTO: 30 minutes.
  DR runbook: written 2 years ago.
  DR test: never performed.

  Actual disaster (region outage):
  T+00:00  Primary region fails
  T+00:10  On-call engineer paged
  T+00:25  Engineer finds DR runbook (outdated)
  T+01:00  Tries to promote read replica → fails (promotion steps changed)
  T+01:30  Infrastructure script references old AMI (not available)
  T+02:00  DNS records point to old IP (TTL=86400 → 24 hours to propagate)
  T+04:00  Service partially restored (still incorrect DNS for many users)

  Actual RTO: 4 hours. Target RTO: 30 minutes.

FIX: Regular DR testing (Game Day / Fire Drill):

  SCHEDULE: Quarterly DR test (non-production first, then production with notice)

  TEST PROCEDURE:
  1. Simulate primary region failure:
     aws ec2 stop-instances --instance-ids i-xxx,i-yyy (app servers)
     aws rds stop-db-instance --db-instance-identifier orders-primary

  2. Execute DR runbook (time each step):
     Step 1: Promote read replica (target: 2 min) — actual: 3 min ✓
     Step 2: Update Route53 records (target: 5 min) — actual: 1 min ✓
     Step 3: Deploy app servers in DR region (target: 10 min) — actual: 18 min ✗
     Step 4: Smoke tests (target: 5 min) — actual: 7 min ✓

     Total: 29 min (under 30-min RTO target — barely)
     Issue found: app server deployment slower than target → requires fix

  3. Document deviations → update runbook and fix infrastructure

  4. CHAOS ENGINEERING (Netflix approach):
     Randomly fail services in production → teams build auto-recovery
     Reduces MTTR to near-zero for common failure modes

  MINIMUM VIABLE TESTING:
  - Monthly: restore database backup to test instance (verify backup integrity)
  - Quarterly: full DR failover test in staging environment
  - Annually: production DR test (with customer notification and rollback plan)

  "An untested DR plan is not a DR plan."
```

---

### 🔗 Related Keywords

- `MTTR / MTBF` — MTTR is the measured recovery time; RTO is the target for MTTR in DR
- `Disaster Recovery` — the process and architecture that achieves RTO and RPO targets
- `Geo-Replication` — database replication across regions to achieve low RPO
- `Active-Active` — architecture that achieves near-zero RTO and RPO
- `Active-Passive` — simpler multi-region architecture with ~minutes RTO

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ RTO = max acceptable downtime duration    │
│              │ RPO = max acceptable data loss (in time)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing DR architecture; negotiating    │
│              │ SLAs; evaluating backup strategies        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Setting RTO/RPO without business impact   │
│              │ analysis — unanchored targets waste money │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "RTO = how fast must we reopen;           │
│              │  RPO = how old can our backup be."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Active → Active-Passive            │
│              │ → Geo-Replication                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial trading platform processes $10M/hour in transactions. The CTO proposes: RTO=4 hours, RPO=1 hour (daily backup + async replication). Calculate the maximum financial exposure from a 4-hour outage with 1 hour of data loss. Now propose an alternative architecture with RTO=5 minutes and RPO=30 seconds. Estimate the annual infrastructure cost difference between the two approaches (use rough multiples: RTO=4h warm standby ~$3k/month; RTO=5m hot standby ~$15k/month). Calculate the break-even point: how many hours of annual outage makes the investment worth it?

**Q2.** Your RPO is 15 minutes. You use asynchronous replication to a cross-region standby. A network partition occurs: the primary continues accepting writes for 45 minutes before the partition is detected and the standby is promoted (without the last 45 minutes of replication data). Explain: (a) how this violates your RPO, (b) what architectural changes would prevent this from happening (hint: consider synchronous writes, write fencing, and quorum-based commit), and (c) what the write latency trade-off is for each approach.
