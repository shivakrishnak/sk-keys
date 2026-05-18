---
id: SYD-021
title: Active-Passive
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008, SYD-019
used_by: SYD-022
related: SYD-008, SYD-018, SYD-019, SYD-020, SYD-022
tags:
  - architecture
  - reliability
  - high-availability
  - disaster-recovery
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/syd/active-passive/
---

⚡ TL;DR - Active-passive keeps one node (primary)
handling all requests while a secondary is synchronized
and on standby. When the primary fails, the secondary
is promoted to take over - but there is a failover
window (seconds to minutes) during which the service
is unavailable. It is simpler than active-active for
stateful services and is the standard pattern for
database high availability.

| #021 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Redundancy and Failover | |
| **Used by:** | Disaster Recovery | |
| **Related:** | Load Balancing, RTO / RPO, Redundancy and Failover, Active-Active, Disaster Recovery | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database runs on a single server. When it fails,
the team manually provisions a new server and restores
from backup. This takes 4 hours. During that time,
the application is completely down.

**THE CORE NEED:**
For stateful services (databases, session stores,
message brokers), active-active is complex because
of write coordination. Active-passive provides high
availability without that complexity: only one node
accepts writes at a time; the secondary is synchronized
but passive. Failover promotes the secondary to primary.
The RTO window (30-120 seconds) is acceptable for
most non-critical services.

---

### 📘 Textbook Definition

**Active-passive** (also called primary/standby or
hot standby): a high-availability pattern where one
node (the active/primary) handles all traffic while
one or more secondary nodes are synchronized and
ready to take over if the primary fails. The secondary
nodes do not serve production traffic. On primary
failure: a health check or consensus system detects
the failure and promotes the secondary to primary,
redirecting traffic via DNS update, VIP switchover,
or load balancer reconfiguration. Typical RTO: 30-120
seconds. RPO depends on replication mode (async = some
data loss possible; sync = near zero data loss).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One server handles all traffic. A synchronized backup
sits on standby. When the primary dies, the backup
takes over after a short failover window.

**One analogy:**
> A Broadway show with a lead actor and an understudy.
> The lead performs every night (active). The understudy
> knows every line and is ready (passive). If the lead
> falls ill mid-show, the understudy goes on after a
> brief intermission (failover window). The show
> resumes - but there was a pause. Compare to active-
> active: two leads alternate performances; if one
> cannot go on, the other picks up mid-scene without
> any intermission.

**One insight:**
Active-passive is the right pattern for stateful
services that cannot tolerate write conflicts. The
single active writer guarantees consistency. The
standby provides availability. The tradeoff is the
failover window and the wasted standby capacity.

---

### 🔩 First Principles Explanation

**THE FAILOVER FLOW:**

```
┌──────────────────────────────────────────────────────┐
│ NORMAL OPERATION                                     │
│                                                      │
│  Client → VIP/DNS → Primary (DB-1)                  │
│                         │                            │
│                    streaming WAL                      │
│                         │                            │
│                    Standby (DB-2) [passive, synced]  │
│                                                      │
│ FAILURE + FAILOVER                                   │
│                                                      │
│  t=0:  Primary fails (hardware fault)                │
│  t=10: Health check detects failure (10s interval)  │
│  t=30: 3 consecutive failures confirmed (30s)       │
│  t=31: Consensus/orchestrator promotes DB-2          │
│  t=35: DNS/VIP updated to point to DB-2             │
│  t=60: DNS TTL expires; clients reconnect to DB-2   │
│                                                      │
│  Total RTO: ~60 seconds (health check + DNS TTL)    │
└──────────────────────────────────────────────────────┘
```

**SYNC VS ASYNC REPLICATION IMPACT:**

```
Synchronous replication (RPO = near 0):
  Primary waits for standby to confirm write receipt
  before returning to client.
  Tradeoff: write latency increases by 1 network RTT
  Typical: +1-5ms for same-region; +30-150ms cross-region

Asynchronous replication (RPO = replication lag):
  Primary commits write locally, replicates in background.
  No write latency penalty.
  Risk: standby may lag behind (seconds to minutes).
  On failover: data written to primary but not yet
  replicated is LOST.
  Acceptable for: non-transactional workloads,
  read-replica serving, data that can be replayed.
```

**THE TRADE-OFFS:**

**Vs active-active:** Active-passive is simpler for
stateful services (no write conflict), but wastes
standby capacity and has a failover window.

**Vs no redundancy:** Active-passive eliminates the
single point of failure and reduces RTO from hours
(restore from backup) to seconds/minutes (promote
standby).

**Sync vs async replication:** Sync reduces RPO to
near zero but adds write latency. Async eliminates
latency penalty but risks data loss on failover.

---

### 💻 Code Example

**Example 1 - AWS RDS Multi-AZ: managed active-passive**
```terraform
# GOOD: Managed active-passive via RDS Multi-AZ
# AWS handles replication, detection, failover
resource "aws_db_instance" "primary" {
  identifier        = "myapp-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.r6g.xlarge"
  allocated_storage = 100

  # Active-passive: synchronous standby in another AZ
  multi_az = true
  # Failover: AWS-managed, ~60-120 seconds
  # Replication: synchronous (RPO = near 0)
  # The standby never receives read traffic (passive)

  # Automated backups for additional RPO protection
  backup_retention_period    = 7
  delete_automated_backups   = false
  skip_final_snapshot        = false
  final_snapshot_identifier  = "myapp-db-final"
}
# Failover trigger: AWS detects primary failure
# Action: promotes standby, updates endpoint DNS
# Application: use the RDS endpoint (abstract, not IP)
# → automatically resolves to new primary after failover
```

**Example 2 - PostgreSQL Patroni: active-passive with auto-failover**
```yaml
# Patroni config: active-passive PostgreSQL cluster
# Primary: accepts reads and writes
# Replica: streaming replication, does not serve clients
# Failover: Patroni promotes replica if primary fails

scope: myapp-cluster
name: db-node-1  # change per node

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.1.11:8008

etcd3:
  hosts: 10.0.1.20:2379,10.0.1.21:2379,10.0.1.22:2379
  # etcd provides consensus for leader election

bootstrap:
  dcs:
    ttl: 30              # Leader key TTL: 30 seconds
    loop_wait: 10        # Check interval: 10 seconds
    retry_timeout: 10    # Election timeout
    maximum_lag_on_failover: 1048576  # ~1MB: max lag
    # If replica is >1MB behind, it is not eligible
    # to be promoted (prevents data loss on failover)

    postgresql:
      use_pg_rewind: true  # Allow old primary to rejoin
      parameters:
        # Synchronous replication for RPO=0
        synchronous_commit: "on"
        synchronous_standby_names: "ANY 1 (*)"
```

**Example 3 - Health check for failover detection**
```python
# Active-passive failover orchestrator (simplified)
# Real implementations use etcd/ZooKeeper for consensus

import time
import socket

class FailoverOrchestrator:
    def __init__(self, primary_host, standby_host):
        self.primary = primary_host
        self.standby = standby_host
        self.failure_count = 0
        self.FAILURE_THRESHOLD = 3  # 3 consecutive fails
        self.CHECK_INTERVAL = 10    # seconds

    def is_primary_healthy(self):
        try:
            # TCP health check: can we connect?
            sock = socket.create_connection(
                (self.primary, 5432), timeout=3)
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    def run(self):
        while True:
            if self.is_primary_healthy():
                self.failure_count = 0
            else:
                self.failure_count += 1
                print(f"Primary unhealthy "
                      f"({self.failure_count}/"
                      f"{self.FAILURE_THRESHOLD})")

                if self.failure_count >= self.FAILURE_THRESHOLD:
                    # IMPORTANT: In production, use
                    # consensus (etcd) here before promoting
                    # to prevent split-brain.
                    print("Promoting standby to primary")
                    self.promote_standby()
                    break

            time.sleep(self.CHECK_INTERVAL)

    def promote_standby(self):
        # 1. Fence old primary (prevent split-brain)
        # 2. Promote standby DB
        # 3. Update DNS/VIP to point to standby
        # 4. Alert team
        print(f"Promoting {self.standby} to primary")
```

---

### ⚖️ Comparison Table

| | Active-Passive | Active-Active |
|---|---|---|
| **Standby utilization** | 0% (idle, waiting) | 100% (serving traffic) |
| **Failover window (RTO)** | 30-120 seconds | ~0 (load rebalance) |
| **Write coordination** | None (single writer) | Required (complex) |
| **Stateful services** | Natural fit | Complex (conflict risk) |
| **Stateless services** | Works but wastes capacity | Better fit |
| **Split-brain risk** | Moderate (mitigated by consensus) | Higher (all active) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Active-passive means the standby is off | The standby is running and synchronized (warm standby = running at reduced capacity; hot standby = running at full capacity). "Passive" refers to not serving client traffic, not to being powered down. |
| Failover is instantaneous | Failover involves: failure detection (10-30s), confirmation (multiple checks), promotion (seconds), DNS/VIP update (30-60s for TTL). Total: 60-120 seconds is typical. "Near-zero RTO" requires active-active, not active-passive. |
| The standby can serve read traffic | Traditional active-passive has a passive standby that serves no traffic. However, many modern setups use the standby for read replicas (reads go to standby; writes go to primary). This is a hybrid, not pure active-passive. |

---

### 🚨 Failure Modes & Diagnosis

**Stale DNS Causing Traffic to Dead Primary**

**Symptom:**
Primary fails. Standby is promoted in 45 seconds.
But the application continues to send requests to
the old primary's IP for 5 minutes after failover.
Users get connection errors for 5 minutes despite
the standby being ready.

**Root Cause:**
DNS TTL for the database endpoint was set to 300
seconds (5 minutes). Applications cached the old
IP. Even after the DNS record was updated to point
to the new primary, applications continue using the
cached IP for up to 5 minutes.

**Fix:**
```bash
# Set DNS TTL low for database endpoints
# Not too low (causes DNS amplification), but
# low enough for failover to be fast

# AWS RDS: endpoint DNS TTL is ~5s (managed service)
# Self-managed: set TTL to 30-60 seconds

# Check current TTL:
dig myapp-db.internal +short | head -1
# Or with TTL display:
dig myapp-db.internal

# Also: configure application connection pool with
# a max connection lifetime to force reconnect:
# HikariCP: maxLifetime=600000 (10 minutes)
# This ensures connections to old primary expire
# within 10 minutes even if DNS is cached.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Redundancy and Failover` - active-passive is the
  classic form of redundancy + failover for stateful
  services
- `RTO / RPO` - the metrics that quantify how good
  the active-passive configuration is

**Builds On This (learn these next):**
- `Disaster Recovery` - extends active-passive across
  regions; active-passive is the DR building block
- `Active-Active` - contrast: no failover window,
  but higher complexity for stateful services

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PATTERN       │ Primary serves all traffic.             │
│               │ Standby synchronized but passive.       │
├───────────────┼─────────────────────────────────────────┤
│ FAILOVER      │ Health check detects failure.           │
│               │ Consensus promotes standby.             │
│               │ DNS/VIP updated.                        │
├───────────────┼─────────────────────────────────────────┤
│ RTO           │ Typical: 60-120 seconds                 │
│               │ (detection + promotion + DNS TTL)       │
├───────────────┼─────────────────────────────────────────┤
│ RPO           │ Sync replication: near-zero             │
│               │ Async replication: seconds-to-minutes   │
├───────────────┼─────────────────────────────────────────┤
│ BEST FIT      │ Stateful services (databases, brokers)  │
│               │ where write coordination is too complex │
├───────────────┼─────────────────────────────────────────┤
│ MANAGED TOOLS │ AWS RDS Multi-AZ, Patroni, MHA, Galera  │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Primary takes all writes. Standby waits│
│               │  Primary dies → standby promotes (60s)."│
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Disaster Recovery → Geo-Replication     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Primary handles all writes. Standby is synchronized
   but idle. Failover = promote standby (RTO: ~60-120s).
2. Sync replication = near-zero RPO (write latency penalty).
   Async replication = no latency penalty but data loss
   possible on failover.
3. Use consensus (etcd, Patroni) for promotion to prevent
   split-brain. Never use heartbeat-only promotion.

**Interview one-liner:**
"Active-passive runs one primary that accepts all writes,
with a synchronized standby that takes over on failure.
RTO is typically 60-120 seconds - the failover window.
RPO depends on replication mode: synchronous gives near-
zero data loss at the cost of write latency; asynchronous
eliminates the latency but risks losing the replication
lag's worth of data on failure. It is the standard HA
pattern for databases because it avoids write conflicts -
only one node is ever the authoritative writer."
