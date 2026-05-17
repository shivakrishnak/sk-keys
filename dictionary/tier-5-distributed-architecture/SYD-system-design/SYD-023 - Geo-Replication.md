---
id: SYD-023
title: Geo-Replication
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-019, SYD-021, SYD-022
used_by: SYD-024
related: SYD-018, SYD-020, SYD-021, SYD-022, SYD-024
tags:
  - architecture
  - reliability
  - data-replication
  - global
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /syd/geo-replication/
---

# SYD-023 - Geo-Replication

⚡ TL;DR - Geo-replication copies data across multiple
geographic regions, providing both DR (survive a region
failure) and performance (serve reads from a region
closest to the user). The hard problem is write
consistency: synchronous cross-region replication
eliminates data loss but adds 50-150ms of cross-region
latency per write. Asynchronous replication reduces
latency but risks data loss on regional failover.

| #023 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Redundancy and Failover, Active-Passive, Disaster Recovery | |
| **Used by:** | Multi-Region Architecture | |
| **Related:** | RTO / RPO, Active-Passive, Active-Active, Disaster Recovery, Multi-Region Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A global SaaS product stores all data in us-east-1.
A user in Tokyo reads their dashboard. Every read
goes across the Pacific to Virginia (150ms each way =
300ms round trip). The app feels slow everywhere
outside the east coast. Also: if us-east-1 goes down,
all data is inaccessible globally, regardless of
where users are.

**THE TWO PROBLEMS GEO-REPLICATION SOLVES:**
1. **Performance:** Serve reads from a local region
   (Tokyo reads from Tokyo replica, 5ms latency,
   not 300ms from Virginia).
2. **DR:** If us-east-1 fails, data exists in Tokyo
   and Europe; failover is possible.

---

### 📘 Textbook Definition

**Geo-replication:** The practice of maintaining
synchronized copies of data in multiple geographic
regions (availability zones, regions, or data centers).
Geo-replication serves two distinct purposes: (1)
DR - surviving a full regional outage - and (2)
performance - reducing read latency by serving from
a region close to the user. Geo-replication is
implemented as synchronous (all regions must confirm
writes, guaranteeing zero data loss) or asynchronous
(writes are applied locally and propagated in
background, risking data loss equal to replication lag).
The choice between synchronous and asynchronous
replication is the fundamental geo-replication
tradeoff: consistency vs latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Copy your data to multiple regions so users worldwide
get low-latency reads AND a region failure does not
take down the whole system.

**One analogy:**
> A Google Doc is geo-replicated. When you edit it
> in Tokyo, the change appears for your colleague in
> London within seconds - even though your "primary"
> account server might be in the US. The same document
> exists in multiple regions. Google chooses where
> to serve each read from to minimize latency.
>
> If the US data center caught fire, your document
> would still be accessible from the European or
> Asian copies.

**One insight:**
Geo-replication for reads (read replicas) is easy
and universally beneficial. Geo-replication for
writes (multi-master) is where the hard problems
live: write conflicts, replication lag, and the
fundamental CAP theorem constraint.

---

### 🔩 First Principles Explanation

**SYNC VS ASYNC REPLICATION:**

```
┌──────────────────────────────────────────────────────┐
│ SYNCHRONOUS GEO-REPLICATION                          │
│                                                      │
│  User write: "balance = $100"                        │
│                                                      │
│  us-east-1 primary ──[write]──> local commit        │
│                    │                                  │
│                    └──> ap-northeast-1 replica       │
│                              [await ack]             │
│                    ←─────── ack (150ms RTT) ─────── │
│                                                      │
│  Return to user: success (after 150ms extra)        │
│  RPO = 0 (replica confirmed write)                  │
│  Cost: +150ms per write (cross-region RTT)          │
│                                                      │
│ ASYNCHRONOUS GEO-REPLICATION                         │
│                                                      │
│  User write: "balance = $100"                        │
│                                                      │
│  us-east-1 primary ──[write]──> local commit        │
│                    │            return to user: OK   │
│                    │            (fast, no RTT wait)  │
│                    └──[async]──> ap-northeast-1      │
│                                  (replicates in bg) │
│                                                      │
│  RPO = replication lag (seconds to minutes)         │
│  If us-east-1 fails before replication completes:   │
│  ap-northeast-1 is behind → data loss               │
└──────────────────────────────────────────────────────┘
```

**GEO-REPLICATION TOPOLOGIES:**

```
Single-master:
  One "master" region accepts all writes.
  Other regions are read-only replicas.
  Write path: always goes to master (high latency
  for writes from remote regions).
  Best for: read-heavy workloads; writes are rare.

Multi-master (conflict resolution required):
  Each region accepts writes; replicate to others.
  Conflict resolution: last-write-wins, CRDTs,
  or application-level conflict resolution.
  Best for: write-heavy global workloads.

Hierarchical:
  Primary region → secondary regional primaries
  → local replicas.
  Each level adds replication lag but reduces
  long-distance hops.
  Best for: very low read latency requirements
  at many global locations.
```

**THE TRADE-OFFS:**
**Synchronous replication:**
Gain: RPO = 0 (no data loss on failover).
Cost: write latency = local write + cross-region RTT
(50-150ms per write for same-continent; 150-350ms
for trans-oceanic). Users in the primary region
experience this latency on every write. This can
be a 10x write latency increase for a fast local DB.

**Asynchronous replication:**
Gain: no write latency penalty; primary region
performance unchanged.
Cost: RPO = replication lag (seconds to minutes).
On a regional failure: data written after the last
replicated transaction is lost. For financial systems:
unacceptable. For recommendation data or analytics:
acceptable.

---

### 🧪 Thought Experiment

**SCENARIO: Global e-commerce - read vs write replication**

Orders are written ~1000/second at peak. The team
wants to serve order history reads from the user's
nearest region (latency reduction). But they cannot
lose order records (RPO = 0 for writes).

**Naive approach: synchronous geo-replication everywhere**
Every write waits for 3 regional acknowledgements.
Write latency: 200ms average (cross-region RTTs).
At 1000 writes/sec, this is 200ms per transaction.
Checkout experience: users wait 200ms extra per
order submission. Unacceptable for checkout UX.

**Better approach: write to primary, async to replicas**
Writes go to us-east-1 (synchronous within AZ for HA).
Async replication to eu-west-1 and ap-northeast-1.
RPO: 5-30 seconds (replication lag).
Write latency: unchanged (no cross-region wait).

**Reconciliation on failover:**
For the 5-30 second of orders that were written to
us-east-1 but not yet replicated: these are in the
primary's WAL logs, which were backed up to S3 every
1 minute. On failover: replay the WAL from S3 to
fill the gap. RPO effectively reduced from
"replication lag" to "S3 backup lag" (1-2 minutes)
with a manual replay step. Business decision: 1-2
minutes of orders replayed post-failover = acceptable
for e-commerce. Not acceptable for payments.

**THE INSIGHT:**
Separate read scaling (async geo-replication of all
data for read queries) from write safety (synchronous
within primary AZ + aggressive WAL backups). The two
requirements have different latency constraints and
different acceptable data loss tolerances.

---

### 🧠 Mental Model / Analogy

> Geo-replication is like a newspaper with regional
> printing presses:
> - One editorial team writes content (primary write node)
> - The content is sent to printing presses in
>   multiple cities (geo-replicas)
> - Readers in Tokyo get the Tokyo edition (low latency)
> - Readers in London get the London edition (low latency)
> - If the NYC press catches fire: the other presses
>   can produce the paper (DR)
>
> The lag: Tokyo readers get "yesterday's" news
> if the editorial content was updated after the
> transmission to Tokyo (replication lag).
> Synchronous would require waiting for Tokyo to
> confirm receipt before publishing in NYC - slow.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Copies of your database in multiple countries/regions.
Users in each region read from their local copy
(fast). If one region goes down, another has the data.

**Level 2 - How to use it (junior developer):**
For read scaling: deploy read replicas in each target
region. Use DNS geo-routing to send reads to the
nearest replica. Write still goes to primary region.
For DR: enable cross-region backup replication.
Managed services handle this: AWS RDS Cross-Region
Read Replicas, Azure Geo-Redundant Storage.

**Level 3 - How it works (mid-level engineer):**
Replication lag is the key metric to monitor.
`replication_lag` = time between a write on primary
and that write being visible on replica. Alert if
lag > RPO target. Under high write load, lag can
grow (replica cannot keep up with primary WAL rate).
Design: ensure replica instance is at least as
powerful as primary for write-intensive workloads.

**Level 4 - Why it was designed this way (senior/staff):**
Geo-replication interacts with the CAP theorem
directly. A partition between us-east-1 and
ap-northeast-1 means the system must choose: serve
potentially stale reads from ap-northeast-1
(available but not consistent) or refuse reads
from ap-northeast-1 (consistent but unavailable
under partition). AWS Aurora Global Database
chooses A over C during partition: read replicas
serve potentially stale data during partition,
then catch up when connectivity restores. The
application must be designed to tolerate this
(eventual consistency for reads).

**Level 5 - Mastery (distinguished engineer):**
The new frontier: Google Spanner and CockroachDB
implement synchronous geo-replication with
serializable consistency using TrueTime (Spanner)
or HLC (Hybrid Logical Clocks, CockroachDB). This
was theoretically impossible per CAP until it was
achieved by accepting that "partition" in
practical cloud environments is short-lived (<ms),
not indefinite. By choosing very short partition
assumptions and strong consensus (Paxos/Raft),
these systems achieve external consistency at
continent-scale. The cost: p99 write latency is
50-150ms globally vs <1ms for local DB. Acceptable
for global-writes-require-consistency workloads;
not acceptable for high-frequency writes.

---

### ⚙️ How It Works (Mechanism)

**AWS Aurora Global Database (managed geo-replication):**

```
┌─────────────────────────────────────────────────────┐
│ Aurora Global Database Architecture                 │
│                                                     │
│  Primary Region (us-east-1)                        │
│  ┌─────────────────────────────────────────────┐   │
│  │  Aurora Writer (1) + Readers (up to 15)     │   │
│  └─────────────┬───────────────────────────────┘   │
│                │ Storage-level replication           │
│                │ Latency: < 1 second                │
│                │ (not WAL: storage I/O layer)        │
│                ↓                                    │
│  Secondary Region (eu-west-1)                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  Read-only cluster (up to 16 readers)       │   │
│  │  Serves reads from European users           │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  On failover: promote secondary to primary          │
│  RTO: < 1 minute (automated)                        │
│  RPO: < 1 second (storage-level replication)        │
└─────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Monitoring replication lag (PostgreSQL)**
```sql
-- On primary: check replication lag to each replica
-- Run this as a monitoring query (every 30s)
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    -- Lag in bytes (0 = caught up)
    (sent_lsn - replay_lsn) AS replication_lag_bytes,
    -- Lag in seconds
    EXTRACT(EPOCH FROM (now() - reply_time))
        AS lag_seconds
FROM pg_stat_replication;

-- Alert if lag_seconds > RPO target
-- Example: RPO = 30 seconds → alert if lag > 30
```

**Example 2 - Application: geo-aware routing**
```java
// Route reads to local replica; writes to primary
// Use the closest read replica to reduce latency.

@Configuration
public class DataSourceConfig {

    // Write operations: always primary (us-east-1)
    @Bean
    @Primary
    public DataSource primaryDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(
            "jdbc:postgresql://primary.us-east-1.db:5432/app");
        config.setMaximumPoolSize(20);
        return new HikariDataSource(config);
    }

    // Read operations: use closest region replica
    // Determined at startup from env variable
    // Set by deployment: EU pods use eu-west-1 replica
    @Bean
    public DataSource readReplicaDataSource(
            @Value("${db.read.replica.url}") String url) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        // Tokyo pods: jdbc:..ap-northeast-1.db..
        // London pods: jdbc:..eu-west-1.db..
        config.setReadOnly(true);
        config.setMaximumPoolSize(20);
        return new HikariDataSource(config);
    }
}

@Service
public class ProductService {
    @Autowired DataSource primary;
    @Autowired DataSource readReplica;

    @Transactional(readOnly = true)
    public Product findById(Long id) {
        // Read: served from local regional replica
        // Low latency: 5ms from Tokyo replica vs
        // 300ms from us-east-1 primary
        return replicaJdbcTemplate.queryForObject(...);
    }

    @Transactional
    public Product save(Product product) {
        // Write: always goes to primary
        // This incurs cross-region network hop from
        // Tokyo to us-east-1, but writes are <5% of
        // total queries so acceptable
        return primaryJdbcTemplate.update(...);
    }
}
```

**Example 3 - Conflict detection for multi-master writes**
```python
# Multi-master geo-replication: detect write conflicts
# using vector clocks (simplified)

from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class VectorClock:
    """Track causality for distributed writes"""
    clocks: Dict[str, int] = field(default_factory=dict)

    def tick(self, node_id: str):
        self.clocks[node_id] = (
            self.clocks.get(node_id, 0) + 1
        )
        return self

    def merge(self, other: "VectorClock"):
        for node, ts in other.clocks.items():
            self.clocks[node] = max(
                self.clocks.get(node, 0), ts)

    def happens_before(self, other: "VectorClock") -> bool:
        """True if self is causally before other"""
        return (
            all(self.clocks.get(n, 0) <= other.clocks.get(n, 0)
                for n in set(self.clocks) | set(other.clocks))
            and self.clocks != other.clocks
        )

    def is_concurrent(self, other: "VectorClock") -> bool:
        """True if neither happened-before the other"""
        return (not self.happens_before(other)
                and not other.happens_before(self))

# When replication delivers a write from another region:
def apply_remote_write(local_write, remote_write):
    if remote_write.vc.happens_before(local_write.vc):
        # Remote is older than local: discard remote
        return local_write
    elif local_write.vc.happens_before(remote_write.vc):
        # Local is older: apply remote
        return remote_write
    else:
        # Concurrent writes: conflict!
        # Strategy options:
        # 1. Last-Writer-Wins (simple, may lose data)
        # 2. Application-level merge (CRDTs)
        # 3. Surface conflict to user
        raise ConflictException(local_write, remote_write)
```

---

### ⚖️ Comparison Table

| | Single-Master Async | Single-Master Sync | Multi-Master |
|---|---|---|---|
| **Write location** | Primary region only | Primary region only | Any region |
| **Write latency** | Local (fast) | Local + cross-region RTT (slow) | Local (fast) |
| **RPO on failover** | Seconds-minutes (lag) | Near-zero | Depends on resolution |
| **Read latency** | Low (local replicas) | Low (local replicas) | Low (any region) |
| **Conflict handling** | N/A | N/A | Required (CRDTs, LWW, etc.) |
| **Complexity** | Low | Medium | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Geo-replication means active-active | Read replicas in multiple regions are geo-replication but not active-active for writes. "Active-active geo-replication" (multi-master) is a specific, complex configuration. Most geo-replication deployments are single-master with regional read replicas. |
| Replication lag is always small | Under peak write load, replication lag can grow to minutes if the replica cannot keep up with the primary's write throughput. The replica must be sized to process writes at the primary's peak rate, plus have headroom to catch up if it falls behind. |
| Synchronous cross-region replication is always worth it | For writes < 50ms baseline, synchronous cross-region (adds 100-300ms) creates a 3-6x write latency increase. Most web applications cannot tolerate this on the user-facing write path. Synchronous replication is justified for financial transactions and compliance requirements, not general web applications. |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag Grows Under Load → RPO Violation**

**Symptom:**
Normal operations: replication lag to EU replica = 0.5s.
During a marketing campaign (10x write traffic), lag
grows to 4 minutes. If a regional failure occurs at
peak, 4 minutes of data will be lost - violating the
1-minute RPO target.

**Root Cause:**
The EU replica is an r5.xlarge (4 vCPU). The primary
is an r5.4xlarge (16 vCPU). Under peak load, the
primary generates WAL faster than the replica can
apply it.

**Diagnosis:**
```sql
-- Primary: monitor lag growth over time
SELECT
    NOW() AS check_time,
    EXTRACT(EPOCH FROM (NOW() - reply_time)) AS lag_sec,
    (sent_lsn - replay_lsn) AS lag_bytes
FROM pg_stat_replication
WHERE client_addr = '10.0.2.100';  -- EU replica IP

-- Graph over time: is lag trending up during load?
-- If yes: replica is under-provisioned.
```

**Fix:**
Upgrade EU replica to match primary size. Set a
monitoring alert if lag > RPO target. Consider
horizontal scaling: multiple smaller replicas each
handling a subset of reads reduces per-replica
write pressure.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Active-Passive` - geo-replication extends the
  active-passive pattern across regions
- `Disaster Recovery` - geo-replication is the data
  layer for cross-region DR

**Builds On This (learn these next):**
- `Multi-Region Architecture` - the full system
  design that uses geo-replication for data, with
  multi-region routing and compute

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT DOES  │ Replicates data across geographic        │
│               │ regions for DR + read performance        │
├───────────────┼──────────────────────────────────────────┤
│ SYNC REPLIC.  │ RPO = 0; Cost = +cross-region RTT per    │
│               │ write (50-300ms)                         │
├───────────────┼──────────────────────────────────────────┤
│ ASYNC REPLIC. │ No write latency penalty; RPO = lag      │
│               │ (seconds to minutes under load)          │
├───────────────┼──────────────────────────────────────────┤
│ READ BENEFIT  │ Route reads to nearest replica           │
│               │ 5ms local vs 300ms cross-ocean           │
├───────────────┼──────────────────────────────────────────┤
│ MONITOR       │ Replication lag (alert if > RPO target)  │
│               │ Size replicas to match primary write rate │
├───────────────┼──────────────────────────────────────────┤
│ MULTI-MASTER  │ All regions accept writes; requires      │
│               │ conflict resolution (CRDTs, LWW)         │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Copies data to multiple regions for     │
│               │  DR survival and local read speed.       │
│               │  Sync = no data loss, slower writes.     │
│               │  Async = fast writes, potential loss."   │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Multi-Region Architecture                │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Geo-replication solves two things: DR survival of
   regional failures, and low-latency reads for
   global users.
2. Sync replication = RPO 0 but adds cross-region
   RTT to writes. Async = fast writes but RPO =
   replication lag (can grow under load).
3. Monitor replication lag. If lag regularly exceeds
   RPO target under load, upgrade replica size - it
   cannot keep up with the primary's write rate.

**Interview one-liner:**
"Geo-replication copies data across geographic regions
for two reasons: DR (survive a full region failure) and
performance (serve reads from the nearest regional copy).
The critical design choice is sync vs async: synchronous
replication gives RPO = 0 by waiting for cross-region
acknowledgement (adds 50-300ms to every write), while
asynchronous has no write latency penalty but risks losing
replication lag's worth of data on failover. Most systems
use async replication for read replicas and reserve sync
for critical financial writes. Key metric to monitor:
replication lag - it can grow significantly under peak
write load if replicas are under-provisioned."
