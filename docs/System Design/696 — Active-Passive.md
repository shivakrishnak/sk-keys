---
layout: default
title: "Active-Passive"
parent: "System Design"
nav_order: 696
permalink: /system-design/active-passive/
number: "696"
category: System Design
difficulty: ★★☆
depends_on: "Redundancy / Failover, RTO / RPO"
used_by: "Disaster Recovery"
tags: #intermediate, #reliability, #distributed, #architecture, #pattern
---

# 696 — Active-Passive

`#intermediate` `#reliability` `#distributed` `#architecture` `#pattern`

⚡ TL;DR — **Active-Passive** keeps one primary node handling all traffic while a standby replica sits ready; on primary failure, the passive node is promoted, trading some switchover time (~seconds to minutes) for architectural simplicity.

| #696 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Redundancy / Failover, RTO / RPO | |
| **Used by:** | Disaster Recovery | |

---

### 📘 Textbook Definition

**Active-Passive** (also called primary-standby, master-slave, or primary-replica) is a high-availability pattern where one primary (active) node handles all read and write requests, while one or more passive (standby) nodes replicate data from the primary and remain ready to take over if the primary fails. The passive node does not serve traffic under normal conditions. When the primary fails — detected by health checks, heartbeats, or monitoring — an automatic or manual **failover** promotes the passive node to primary, redirects traffic (via DNS change, floating IP, or load balancer reconfiguration), and the system resumes. Active-Passive is simpler than Active-Active because there is always a single authoritative source for writes, eliminating the conflict-resolution challenges of multi-master systems. The cost: some standby capacity is idle, and there is a brief failover window (seconds to minutes) during which traffic is disrupted.

---

### 🟢 Simple Definition (Easy)

Active-Passive: one server works (active), one server waits on standby (passive). If the active server fails, the passive one takes over. Simpler than Active-Active but with a short switchover delay and wasted standby capacity. Like a driver and a co-pilot: the co-pilot isn't driving but can take over immediately if the driver is incapacitated.

---

### 🔵 Simple Definition (Elaborated)

Primary database server handles all reads and writes. It continuously replicates changes to a standby server (passive). The standby accepts no user requests — it just stays in sync. When the primary fails, a health check detects it within 10-30 seconds. Failover begins: promote standby to primary, update DNS or VIP, application reconnects. Total time: 30-120 seconds. Users see a brief error during this window. Then normal operation resumes. Advantage: no conflict resolution needed — there's always one primary. Disadvantage: standby is "wasted" capacity and there's a switchover delay.

---

### 🔩 First Principles Explanation

**Active-Passive mechanics — detection, promotion, re-routing:**

```
NORMAL OPERATION:
  Client → Load Balancer → Primary (Active)
                               │
                        Replication (sync or async)
                               │
                            Standby (Passive)
                            [no client traffic]

FAILURE DETECTION:
  Method 1: Health check polling (LB or external monitor)
    Health checker: pings primary every 5s
    Primary fails: 2 consecutive failures → marked DOWN (10s detection)
    
  Method 2: Heartbeat (standby watches primary)
    Standby: sends heartbeat to primary every 1s
    No response for 3s → declares primary dead → initiates failover
    
  Method 3: Agent-based (monitoring daemon on primary)
    Agent detects local failure → sends signal to orchestrator
    Fastest detection (sub-second) but adds complexity

FAILOVER SEQUENCE:
  T+00s: Primary failure detected by health checker
  T+10s: Primary marked as failed (after N consecutive failures)
  T+11s: Failover initiated:
    1. FENCING: ensure primary is truly dead (STONITH or terminate EC2)
    2. PROMOTION: standby becomes read-write primary
    3. TRAFFIC REDIRECT:
       DNS: update A record to standby IP (TTL=60 → propagates in 60s)
       OR
       Floating IP / VIP: reassign IP to standby (instant, no DNS needed)
       OR
       Load Balancer: remove primary, add standby to pool (instant)
    4. VERIFICATION: health check confirms standby accepting requests
  T+30-90s: Service restored at standby
  
  Total RTO: 30-90 seconds (automated) or 15-30 minutes (manual)

SYNCHRONOUS vs. ASYNCHRONOUS REPLICATION effect on RPO:

  SYNCHRONOUS (RPO = 0):
    Primary: write committed only after standby confirms receipt.
    Standby always has all committed data.
    Failover: no data loss.
    Cost: each write waits for network RTT to standby.
    Typical: +1-5ms for same-AZ, +50ms for cross-region.
    
  ASYNCHRONOUS (RPO = seconds to minutes):
    Primary: write committed immediately.
    Replication: happens in background.
    Lag at failure time: 0-N seconds of uncommitted writes.
    Failover: up to N seconds of data loss.
    Cost: no write latency overhead.
    
    Example: PostgreSQL with streaming replication
    pg_stat_replication: shows lag
    In synchronous mode: synchronous_standby_names = 'standby1'
    In async mode: lag can be monitored but not bounded

ACTIVE-PASSIVE FOR COMPUTE (stateless app servers):
  Primary: all traffic
  Standby: identical instance, running but not in LB pool
  Failover: LB health check removes primary, adds standby
  Data: no replication needed (stateless — state in shared DB)
  RTO: < 10 seconds (LB health check cycle)
  
  Note: for stateless services, Active-Active is usually preferred
  (wastes no capacity, no failover delay). Active-Passive for compute
  is only common in very specific legacy or compliance scenarios.

ACTIVE-PASSIVE FOR DATABASES (stateful — most common use case):
  PostgreSQL: primary + streaming replica
  MySQL: primary + replica (semi-sync or async)
  Redis: master + replica with Sentinel for auto-failover
  RDS: Multi-AZ (AWS manages promotion automatically)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Active-Passive (single node):
- Any hardware/software failure = complete downtime (full SPOF)
- MTTR: hours to provision replacement + restore backup

WITH Active-Passive:
→ Single node failure handled with brief switchover (30-90s) instead of hours
→ Simple: always one authoritative primary — no conflict resolution
→ Data safety with synchronous replication: zero data loss on failover

---

### 🧠 Mental Model / Analogy

> A spacecraft with a primary computer and a backup computer. The primary handles all navigation and control. The backup receives copies of all state updates but executes no commands. If the primary fails, mission control (or automatic detection) switches control to the backup. The backup is identical and current. A brief window of manual switching or detection. Then the backup takes over seamlessly. Simpler than two computers trying to steer simultaneously (Active-Active for spacecraft would cause chaos).

"Primary computer" = active node
"Backup computer" = passive standby
"Mission control switching" = failover orchestration (DNS, VIP, LB)
"State update copies" = replication from primary to standby

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL streaming replication + Patroni auto-failover:**

```yaml
# Patroni: distributed HA for PostgreSQL (Active-Passive with auto-failover)
# Uses etcd/Consul/ZooKeeper for distributed consensus (prevent split-brain)

scope: postgres-cluster
namespace: /service/
name: node1  # change per node (node1, node2, node3)

etcd:
  hosts: 10.0.0.1:2379,10.0.0.2:2379,10.0.0.3:2379

bootstrap:
  dcs:
    ttl: 30                           # leader lock TTL: 30 seconds
    loop_wait: 10                     # check every 10 seconds
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB max replication lag for failover
  
  postgresql:
    parameters:
      synchronous_commit: "on"         # synchronous replication (RPO=0)
      synchronous_standby_names: "*"   # wait for any one standby

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.1.1:5432
  data_dir: /data/postgres
  authentication:
    replication:
      username: replicator
      password: secretpass

# FAILOVER FLOW (Patroni):
# 1. Primary loses etcd lock (TTL expires after 30s of no heartbeat)
# 2. Replica with most up-to-date WAL is elected as new primary
# 3. Patroni promotes it (pg_ctl promote)
# 4. Other replicas reconfigure to follow new primary
# 5. HAProxy detects change via Patroni REST API (health endpoint)
#    GET /primary → 200 if node is primary, 503 if not
# 6. HAProxy routes writes only to node responding 200 on /primary
#    HAProxy routes reads to all nodes responding 200 on /replica
```

---

### 🔄 How It Connects (Mini-Map)

```
Redundancy / Failover
(the general concept)
        │
        ├── Active-Passive ◄──── (you are here)
        │   + Simple: single authoritative primary
        │   + Synchronous replication → RPO=0
        │   - Standby capacity idle
        │   - Failover time: 30-90 seconds
        │
        └── Active-Active
            + All nodes serving traffic
            + Zero failover delay
            - Complex conflict resolution for databases
```

---

### 💻 Code Example

**Redis Sentinel: Active-Passive with automatic failover:**

```
# Redis Sentinel: 1 master + 2 replicas + 3 Sentinel monitors

# redis-master.conf:
port 6379
bind 0.0.0.0
requirepass yourpassword

# redis-replica.conf (replica 1 and 2):
port 6379
bind 0.0.0.0
replicaof 10.0.1.1 6379           # replicate from master
masterauth yourpassword
requirepass yourpassword
replica-read-only yes              # replicas: read-only (passive)

# sentinel.conf (run on 3 separate nodes for quorum):
sentinel monitor mymaster 10.0.1.1 6379 2   # quorum: 2 sentinels must agree
sentinel auth-pass mymaster yourpassword
sentinel down-after-milliseconds mymaster 5000   # fail after 5s no response
sentinel failover-timeout mymaster 10000         # RTO target: 10 seconds
sentinel parallel-syncs mymaster 1              # 1 replica syncs at a time

# FAILOVER FLOW:
# 1. Master unresponsive for 5,000ms
# 2. Sentinel marks master as subjectively DOWN (S_DOWN)
# 3. 2 Sentinels agree → objectively DOWN (O_DOWN) — quorum prevents split-brain
# 4. Sentinel leader elected (among sentinels)
# 5. Leader promotes replica with least replication lag to new master
# 6. Other replicas reconfigure to follow new master
# 7. Application (Jedis/Lettuce): discovers new master via Sentinel API
#    JedisSentinelPool: subscribes to Sentinel events → automatic reconnect
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Active-Passive wastes 50% of resources | Passive nodes aren't fully idle: they handle replication processing, can serve read traffic (read replicas), run monitoring and health checks, and may handle reporting queries. Database read replicas in Active-Passive are common: writes to primary, reads distributed across replicas |
| Active-Passive provides the same availability as Active-Active | Active-Active: no failover delay, node failure is absorbed instantly. Active-Passive: 30-90 second failover window. For many applications this difference is acceptable; for zero-tolerance latency, Active-Active is needed |
| You should always use synchronous replication for zero RPO | Synchronous replication adds write latency equal to the network RTT to the standby. For same-AZ: 1-2ms (usually acceptable). For cross-region: 50-200ms (often unacceptable for write-heavy apps). Asynchronous replication accepts a small RPO (seconds) in exchange for no write latency overhead |
| Active-Passive is outdated — everyone uses Active-Active now | Active-Passive remains the default pattern for most databases in production (RDS Multi-AZ, Redis Sentinel, PostgreSQL with Patroni). Active-Active for databases is significantly harder to operate correctly and is only needed when the simpler approach's failover time or single-region availability is insufficient |

---

### 🔥 Pitfalls in Production

**Promoting stale standby → data loss beyond RPO:**

```
PROBLEM: Async replication + forced failover → unexpected data loss

  Deployment: PostgreSQL primary (us-east-1a) + async replica (us-east-1b)
  Replication mode: asynchronous (no write latency overhead)
  Typical lag: 50ms-500ms (acceptable RPO)
  
  Scenario: primary server OS panic at T=0.
  Primary: last committed write at T=-30ms.
  Replica lag at time of failure: 2 MINUTES (backlog due to heavy write load)
  
  Failover initiated at T+10s (detection time).
  Standby state: 2 minutes behind primary at time of failure.
  Forced promotion: standby becomes primary with 2-minute-old data.
  
  Data loss: 2 minutes of transactions (RPO violation if target was 30s).
  
  Why did lag reach 2 minutes?
  - Heavy batch job running: 50,000 writes/second
  - Replication slot: standby couldn't keep up with WAL generation
  - Monitoring: replication lag metric existed but no alert set!
  
FIX 1: Monitor and alert on replication lag
  PostgreSQL: pg_stat_replication.replay_lag
  Alert: replay_lag > 30s (target RPO threshold) → PagerDuty
  
  # Prometheus PostgreSQL exporter:
  pg_replication_lag > 30   # alert if replica > 30 seconds behind
  
FIX 2: Replication slot + pg_replication_slots monitoring
  Replication slot: prevents WAL from being deleted until replica consumes it.
  Risk: disk space exhaustion if replica is very far behind.
  Alert: pg_replication_slots.active = false (disconnected replica)
         pg_replication_slots.lag_bytes > 5GB (getting dangerous)
  
FIX 3: Synchronous replication for RPO-critical systems
  synchronous_commit = on
  synchronous_standby_names = 'replica1'
  → Writes only committed when replica confirms
  → Lag: guaranteed 0 (at cost of +1-2ms write latency per write)
  → On replica disconnect: primary blocks writes (availability trade-off)
  
  COMPROMISE: synchronous_commit = remote_write
  → Primary waits for replica to receive WAL (not execute it)
  → Slightly weaker consistency guarantee, but prevents data loss
  → Slightly less write latency overhead than full synchronous
```

---

### 🔗 Related Keywords

- `Active-Active` — the more complex alternative; all nodes serve traffic
- `Redundancy / Failover` — the parent concept; Active-Passive is an implementation
- `RTO / RPO` — Active-Passive achieves RTO=30-90s; RPO depends on replication mode
- `Disaster Recovery` — cross-region Active-Passive is the most common DR pattern
- `Load Balancing` — redirects traffic to promoted standby after failover

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One active node, one passive standby:     │
│              │ simple, consistent, brief failover window │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Database HA; simple, correct behaviour    │
│              │ more important than zero failover time    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Zero-failover-time required; passive      │
│              │ capacity waste is unacceptable            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Driver and co-pilot: one steers,         │
│              │  one is ready — no confusion over         │
│              │  who has the wheel."                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Active → Geo-Replication           │
│              │ → Disaster Recovery                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a PostgreSQL Active-Passive cluster (synchronous replication). Primary is in us-east-1a, standby in us-east-1b. The AZ-to-AZ network becomes congested: write latency spikes from 5ms to 500ms (synchronous replication waits for standby ACK). Your application P99 write latency SLO is 100ms. What do you do? Evaluate three options: (a) switch to asynchronous replication (what RPO does this accept?), (b) set `synchronous_commit = remote_write` (what's the difference?), (c) accept the latency spike until network resolves. What monitoring would you have in place to detect this scenario?

**Q2.** A critical financial ledger system uses Active-Passive with asynchronous replication. The primary crashes. Before initiating failover, you must decide: force-promote the standby immediately (possible data loss) or wait for primary recovery (RTO increases). The last known replication lag was 45 seconds. The business team says: "Transactions in the last 45 seconds represent $200,000 in payments." Design a decision framework with specific criteria for when to force-promote vs. attempt primary recovery, including how to handle the $200,000 in potentially lost transactions if you do force-promote.
