---
id: SYD-019
title: Redundancy and Failover
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008, SYD-003
used_by: SYD-020, SYD-021, SYD-022
related: SYD-003, SYD-004, SYD-008, SYD-018, SYD-020, SYD-021
tags:
  - architecture
  - reliability
  - high-availability
  - infrastructure
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/syd/redundancy-and-failover/
---

⚡ TL;DR - Redundancy means having duplicate components
so one failure does not stop the system. Failover is
the automatic (or manual) switch to the duplicate when
the primary fails. Together they transform a single
point of failure into a high-availability component.
The complexity is not in adding the redundant copy -
it is in detecting failure reliably and switching
without causing a split-brain or thundering herd.

| #019 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Availability | |
| **Used by:** | Active-Active, Active-Passive, Disaster Recovery | |
| **Related:** | Availability, Single Point of Failure, Load Balancing, RTO/RPO, Active-Active, Active-Passive | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single database server handles all writes. It fails.
The entire application stops until an engineer restores
the server - which takes 2 hours. The business lost
2 hours of transactions. No redundancy = every critical
component is a single point of failure. Failures are
not "if" in distributed systems; they are "when."

**THE BREAKING POINT:**
Any component that handles critical work will eventually
fail: hardware dies, processes crash, network partitions
occur. Without redundancy, each such failure is a
full service outage. The architecture must be designed
with the assumption that any single component will fail;
the system should continue operating through that failure.

---

### 📘 Textbook Definition

**Redundancy:** The practice of having multiple copies
of a component so that the failure of one does not
cause system failure. Redundant components may be
active (all serving traffic, like N+1 servers behind
a load balancer) or passive (standby copies waiting
to take over). Redundancy addresses hardware failures,
software crashes, and infrastructure outages by
eliminating single points of failure.

**Failover:** The process of switching traffic or
responsibility from a failed primary component to
a redundant secondary. Failover can be automatic
(triggered by health checks, orchestrators, or
consensus protocols) or manual (triggered by an
operator). Automatic failover reduces MTTR but
introduces split-brain risk. Manual failover is
safer but increases downtime.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redundancy = have spares. Failover = switch to the
spare when the primary fails.

**One analogy:**
> An airplane has two engines. If one fails (the
> failure), the plane continues on one engine
> (failover to the redundant engine). The pilot is
> notified, but the plane does not fall out of the sky.
>
> The redundancy (two engines) plus the failover
> mechanism (the plane's control surfaces handle
> asymmetric thrust) together achieve high availability.
> Just having two engines is not enough - there must
> also be a mechanism to continue operating on one.

**One insight:**
Adding redundancy is easy. Making failover reliable
is hard. The common failure modes are: not detecting
that the primary failed (silent failure, no failover
triggered), false-positive detection (healthy primary
gets failed over, causing unnecessary disruption),
and split-brain (both primary and secondary believe
they are the primary, leading to data corruption).

---

### 🔩 First Principles Explanation

**TYPES OF REDUNDANCY:**

```
┌──────────────────────────────────────────────────────┐
│ REDUNDANCY PATTERNS                                  │
│                                                      │
│ N+1 Redundancy:                                      │
│   N servers needed; N+1 deployed. 1 can fail         │
│   without service impact. Load balancer routes       │
│   around the failed node.                            │
│   Example: 3 servers for 2 required, load balanced   │
│                                                      │
│ N+M Redundancy:                                      │
│   M spare servers. M failures tolerated.             │
│   Example: RAID-6 = N+2 (2 drive failures OK)       │
│                                                      │
│ Active-Active:                                       │
│   All copies serve traffic. Failure of one           │
│   redistributes load to survivors.                   │
│   Best for: stateless services (web servers, APIs)   │
│                                                      │
│ Active-Passive (Warm Standby):                       │
│   Primary serves traffic; secondary is synchronized  │
│   but does not serve traffic until failover.         │
│   Best for: stateful services (databases)            │
│                                                      │
│ Hot Standby:                                         │
│   Both primary and secondary synchronized and        │
│   ready to serve; failover is near-instantaneous.   │
│   Best for: critical stateful services               │
└──────────────────────────────────────────────────────┘
```

**FAILOVER DETECTION METHODS:**

```
1. Health checks (load balancer):
   Load balancer polls each server every N seconds.
   If K consecutive checks fail → server removed.
   Detection time = K × N seconds.
   Tradeoff: smaller N/K = faster detection
             but more false positives.

2. Heartbeat (peer-based):
   Each server sends regular heartbeat to peer/cluster.
   No heartbeat within timeout = assumed failed.
   Risk: heartbeat loss ≠ server failure (network
   partition can split a healthy cluster).

3. Consensus (e.g., Raft, Paxos):
   Leader election via consensus protocol. If leader
   is unreachable by a quorum, a new leader is elected.
   Safe: requires majority agreement before failover.
   Protection against split-brain.

4. External coordination (ZooKeeper, etcd):
   External service manages primary election.
   Servers register; external service declares leader.
   If primary fails to renew lock, secondary takes over.
```

**THE TRADE-OFFS:**

**Active-Active:** Higher complexity (stateful services
must coordinate writes); better resource utilization;
zero failover time.

**Active-Passive:** Simpler coordination; wasted standby
capacity; failover time = detection + promotion.

**Automatic failover:** Faster MTTR; risk of split-brain
or false-positive promotion.

**Manual failover:** Safer; higher MTTR.

---

### 🧪 Thought Experiment

**SCENARIO: Adding failover without understanding
split-brain results in data corruption**

A team adds a secondary database for redundancy.
They set up a heartbeat: if the primary does not
respond within 3 seconds, promote the secondary.
A network partition occurs: the primary is healthy
but unreachable from the secondary's perspective.
The secondary promotes itself. Now there are two
primaries accepting writes.

For 4 minutes (until the partition resolves), both
databases accept writes. When the network heals,
both have diverged. The system does not know which
writes are authoritative. Data corruption.

**THE INSIGHT:**
The heartbeat timeout causes incorrect failover on
network partition. The correct solution: use a
consensus protocol (Raft, Paxos, or a tool like
Patroni for PostgreSQL, or ETCD as external arbiter).
Consensus requires a quorum (majority) to agree that
the primary is down before promoting a secondary.
In a 3-node cluster (1 primary + 2 replicas), at
least 2 must agree the primary is unreachable before
promoting. A simple network partition between primary
and secondary, where the secondary cannot reach the
primary but the primary can still reach other nodes,
will not trigger a spurious failover.

---

### 🧠 Mental Model / Analogy

> Redundancy + Failover is like a relay race baton
> handoff:
> - Redundancy: having a second runner ready on the
>   track at all times.
> - Failover: the process of passing the baton when
>   the first runner stumbles.
>
> Just having a second runner does not help if the
> baton handoff is chaotic (split-brain) or if the
> second runner does not start running until the first
> runner has fully stopped and confirmed the handoff
> (slow manual failover). The reliability of the race
> depends on the handoff protocol, not just the
> existence of the backup runner.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Having backup copies of critical components (redundancy),
and automatically switching to them when the primary
fails (failover). Goal: no single failure causes a
full outage.

**Level 2 - How to use it (junior developer):**
For stateless services: deploy multiple instances
behind a load balancer. The load balancer health check
handles failover automatically - unhealthy instances
are removed from rotation.
For databases: use managed services with built-in
replication and failover (AWS RDS Multi-AZ, Cloud
Spanner). Do not build your own.

**Level 3 - How it works (mid-level engineer):**
Health check tuning matters: check frequency × failure
threshold = detection time. Check too rarely and MTTR
is high. Check too aggressively (every second, fail
after 1 missed check) and healthy nodes get removed
on transient network blips, causing unnecessary
failovers. Typical: 10-30s interval, 2-3 failures
before removal.

**Level 4 - Why it was designed this way (senior/staff):**
The two-generals problem and split-brain make automatic
failover fundamentally difficult. A split-brain in
a database (two nodes both believe they are primary)
causes data divergence that is often impossible to
reconcile without data loss. The solution is a fencing
mechanism (STONITH - Shoot The Other Node In The Head):
when a node is suspected failed, positively disconnect
it from storage/network before the secondary takes
over. Harsh but necessary for data integrity.

**Level 5 - Mastery (distinguished engineer):**
Failover is one of the hardest problems in distributed
systems because the detection mechanism (health checks,
heartbeats) is also subject to the same network issues
that cause legitimate failures. The fundamental insight
from systems like Raft and Zab: do not fail over based
on "we cannot reach the primary." Fail over based on
"a quorum cannot reach the primary AND the quorum
agrees to elect a new leader." This prevents split-brain
without sacrificing availability under real failure.
The Raft paper's key contribution was making this
algorithm understandable and implementable, enabling
systems like etcd and CockroachDB to provide safe
automatic failover at scale.

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL Patroni failover example:**

```
┌──────────────────────────────────────────────────────┐
│ PATRONI CLUSTER (3 nodes)                           │
│                                                      │
│  Primary (node-1)    Replica (node-2)               │
│  streaming WAL ────────────────────>                 │
│       │                    │                         │
│       └──── etcd ──────────┘                        │
│             (consensus)                              │
│                                                      │
│ Failure scenario:                                    │
│ 1. node-1 stops responding to etcd keepalive         │
│ 2. node-1's leader key expires (TTL: 30s)           │
│ 3. node-2 sees expired key → acquires leader key     │
│ 4. node-2 promotes itself to primary                 │
│ 5. Patroni updates service endpoint DNS → node-2     │
│ 6. Application reconnects to new primary             │
│                                                      │
│ Total failover time: ~30-60 seconds                  │
│ Split-brain protection: etcd consensus (only one     │
│ node can hold the leader key at a time)              │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - BAD: Simple heartbeat without fencing**
```python
# BAD: heartbeat-based failover without split-brain
# protection. Can lead to two primaries.
import time
import threading

class SimpleFailover:
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary
        self.is_primary_healthy = True

    def heartbeat_monitor(self):
        """Dangerous: network timeout != server failure"""
        while True:
            try:
                self.primary.ping(timeout=3)
                self.is_primary_healthy = True
            except TimeoutError:
                # PROBLEM: primary might be healthy
                # but network is partitioned.
                # Promoting secondary here causes
                # split-brain if primary keeps accepting
                # writes.
                self.is_primary_healthy = False
                self.secondary.promote()  # DANGEROUS
            time.sleep(5)
```

**Example 2 - GOOD: Consensus-based failover with fencing**
```python
# GOOD: Use etcd distributed lock for safe failover
# Only one node can be primary at a time.
import etcd3
import subprocess

class ConsensusFailover:
    def __init__(self, node_id, etcd_host):
        self.node_id = node_id
        self.etcd = etcd3.client(host=etcd_host)
        self.lease = None

    def run_as_primary(self):
        """Acquire distributed lock before becoming primary.
        Lock expires if not renewed = safe automatic failover.
        """
        # TTL: if we stop renewing (crash/network loss),
        # the lock expires and another node can take over.
        self.lease = self.etcd.lease(ttl=30)

        # Atomic: succeed only if key does not exist
        success = self.etcd.put_if_not_exists(
            "/service/primary",
            self.node_id.encode(),
            lease=self.lease
        )

        if success:
            print(f"{self.node_id}: became primary")
            self._promote_postgres()
            # Keep renewing the lease while healthy
            self._run_renewal_loop()
        else:
            print(f"{self.node_id}: secondary, monitoring")
            self._watch_for_primary_change()

    def _promote_postgres(self):
        """Fence: ensure old primary cannot write before
        promoting. Use pg_promote() only after fencing."""
        # STONITH equivalent: revoke old primary's
        # credentials or send SIGTERM if possible
        subprocess.run(
            ["pg_promote", "--wait"], check=True
        )

    def _run_renewal_loop(self):
        while True:
            try:
                self.etcd.refresh_lease(self.lease.id)
                time.sleep(10)  # Renew every 10s (TTL=30)
            except Exception:
                # Cannot renew: we are partitioned.
                # Step down gracefully.
                self._demote_postgres()
                break
```

**Example 3 - Kubernetes: automatic failover via pod health checks**
```yaml
# Deployment with readiness + liveness for failover
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 3  # N+1 redundancy (2 required, 3 running)
  template:
    spec:
      containers:
      - name: api
        image: api-service:latest
        ports:
        - containerPort: 8080
        # Liveness: restart container if it deadlocks
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3  # restart after 3 failures
          # Detection time: 3 × 10s = 30s
        # Readiness: only send traffic when ready
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          periodSeconds: 5
          failureThreshold: 2
          # Failover time: 2 × 5s = 10s before removal
          # from service endpoints
      # Pod disruption budget: always keep 2 of 3 running
  ---
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: api-service-pdb
  spec:
    minAvailable: 2
    selector:
      matchLabels:
        app: api-service
```

---

### ⚖️ Comparison Table

| Approach | Failover Time | Data Safety | Complexity | Cost |
|---|---|---|---|---|
| Manual failover | Minutes-hours | High (human verifies) | Low | Low |
| Health check + auto | 10-60 seconds | Medium (split-brain risk) | Medium | Medium |
| Consensus-based auto | 30-60 seconds | High (quorum required) | High | Medium |
| Active-active (no failover) | 0 seconds | Architecture-dependent | Very high | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More redundancy = more reliability | Only if the failure modes are independent. If all redundant copies share the same dependency (same power circuit, same availability zone, same NFS mount), a single failure takes down all copies. True redundancy requires independent failure domains. |
| Failover is the same as failback | Failover: switch to the secondary when the primary fails. Failback: switch back to the original primary once it is restored. Failback is often the more dangerous operation - it can cause a second failover if rushed. Many teams choose to keep the secondary as the new primary rather than risk a failback. |
| Health checks prevent false positives | Health checks can report failure due to network congestion, garbage collection pauses, or temporary resource exhaustion - even when the server is healthy. Consensus-based promotion (requires quorum agreement) reduces, but does not eliminate, false positives. |

---

### 🚨 Failure Modes & Diagnosis

**Split-Brain Detection**

**Symptom:**
After a network partition incident, the team discovers
two application instances both believe they are writing
to "the primary database." A subset of transactions
is in one database, the rest in another. Merging
is impossible because both wrote to the same primary
keys with different values.

**Diagnostic:**
```sql
-- After suspected split-brain, check for divergence
-- Run on both nodes and compare:
SELECT pg_current_wal_lsn();  -- WAL positions differ
SELECT count(*) FROM orders
  WHERE created_at > '2024-01-15 14:00:00';
-- If counts differ: data diverged during partition

-- Check when each node believes it became primary:
SELECT * FROM pg_stat_replication;  -- on both nodes
```

**Fix (if occurred):**
There is often no clean technical fix. Requires
business-level reconciliation: which writes are
authoritative? For financial systems, this may require
transaction reversal. Prevention is the only real fix.

**Prevention:**
Use consensus-based leader election (etcd, Patroni,
Raft). Never use simple heartbeat + auto-promote for
databases with strong consistency requirements.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - the mechanism that routes traffic
  around failed instances; the simplest form of failover
- `Availability` - the metric that redundancy + failover
  directly improves

**Builds On This (learn these next):**
- `Active-Active` - both copies serve traffic; no
  failover needed; highest availability design
- `Active-Passive` - one serves, one waits; traditional
  failover model

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ REDUNDANCY    │ Multiple copies → no SPOF               │
│ FAILOVER      │ Switching to backup when primary fails  │
├───────────────┼─────────────────────────────────────────┤
│ PATTERNS      │ N+1, Active-Active, Active-Passive,     │
│               │ Hot Standby                             │
├───────────────┼─────────────────────────────────────────┤
│ HARD PROBLEM  │ Split-brain: two nodes both think they  │
│               │ are primary → data corruption           │
├───────────────┼─────────────────────────────────────────┤
│ SOLUTION      │ Consensus (Raft/etcd) + fencing (STONITH│
│               │ before promoting secondary              │
├───────────────┼─────────────────────────────────────────┤
│ DETECTION     │ Health check: interval × threshold = RTO│
│               │ Consensus: quorum agreement before chang│
├───────────────┼─────────────────────────────────────────┤
│ ANTI-PATTERN  │ Heartbeat-only failover without fencing │
│               │ → split-brain risk on network partition │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Redundancy adds the spare. Failover    │
│               │  switches to it. Split-brain is what    │
│               │  happens when you switch wrong."        │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Active-Active → Active-Passive          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Redundancy eliminates single points of failure;
   failover switches traffic to the redundant copy.
2. Split-brain (two nodes think they are primary) is
   the main risk of automatic failover - use consensus
   protocols (Raft, etcd) to prevent it.
3. Independent failure domains matter: redundancy
   within the same AZ, power circuit, or disk shelf
   does not protect against AZ/power/hardware failure.

**Interview one-liner:**
"Redundancy means having duplicate components so a single
failure does not cause an outage. Failover is switching
to the redundant copy when the primary fails. The hard
problem is not adding the backup - it is detecting failure
reliably without false positives, and switching safely
without split-brain. Consensus protocols (Raft via etcd
or Patroni) solve this for stateful services by requiring
a quorum to agree before promoting a secondary to primary."
