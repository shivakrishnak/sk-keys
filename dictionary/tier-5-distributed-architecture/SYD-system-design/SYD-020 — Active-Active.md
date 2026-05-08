---
layout: default
title: "Active-Active"
parent: "System Design"
nav_order: 20
permalink: /system-design/active-active/
id: SYD-020
category: System Design
difficulty: ★★★
depends_on: Load Balancing, Replication, Distributed Systems
used_by: High Availability Architecture, Multi-Region Systems
related: Active-Passive, Load Balancing, Geo-Replication
tags:
  - high-availability
  - advanced
  - distributed-systems
  - scalability
  - fault-tolerance
---

# SYD-020 — Active-Active

⚡ TL;DR — Both primary and backup systems simultaneously serve traffic (not standby). Eliminates failover delay and increases throughput, but requires careful handling of data consistency and distributed consensus.

| #695            | Category: System Design                              | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Replication, Distributed Systems     |                 |
| **Used by:**    | High Availability Architecture, Multi-Region Systems |                 |
| **Related:**    | Active-Passive, Load Balancing, Geo-Replication      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Active-passive setup: primary serves traffic, backup sits idle. If primary fails, switch to backup. But switchover takes time (5-15 seconds). Meanwhile, SLA clock running.

**THE BREAKING POINT:**
Idle backup resources = wasted capacity. Failover delay = downtime. Need both systems to serve traffic simultaneously.

**THE INVENTION MOMENT:**
"Both systems active, both serving traffic. If one fails, the other keeps going. No switchover needed, no downtime."

---

### 📘 Textbook Definition

**Active-Active:** Two or more systems simultaneously handling requests, with automatic failover if one system fails. Unlike active-passive (where backup is dormant), active-active distributes load across both systems continuously. Requires careful handling of data synchronization to avoid inconsistency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Both systems always serving traffic. If one fails, the other continues without pause.

**One analogy:**

> Two checkout lanes at a grocery store, both open. Customers split between them. If lane 1 breaks down, customers seamlessly use lane 2. No queuing, no "switching" — it was already distributed.

**One insight:**
Active-active is ideal for throughput and resilience, but complicated for data consistency. Not always worth the complexity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Both systems receive traffic simultaneously
2. Both can accept writes (data consistency challenge)
3. If one fails, others must handle full load
4. Requires distributed consensus (avoid split-brain)

**DERIVED DESIGN:**
For active-active to work:

- **Stateless layer (web tier):** Easy—both servers fully independent, load balancer routes to either
- **Stateful layer (database tier):** Hard—both must handle writes, must replicate synchronously to avoid data loss

Active-active strategies:

- Multi-master replication (all nodes can write, conflict resolution required)
- Sharding (each system owns portion of data, no conflicts)
- Event sourcing (write to log, replay to both systems)

**THE TRADE-OFFS:**
**Gain:** No failover delay. Full utilization of resources. Scale horizontally. More resilient.

**Cost:** Data consistency complexity. Conflict resolution. Network overhead (constant sync). Harder to debug. Not all data structures compatible.

---

### 🧪 Thought Experiment

**SETUP:**
A payment API. Transaction counter: current value = 1000 (for auditing).

**Active-Passive (Standby):**

- Primary handles all writes
- Secondary (backup) receives replication
- Counter: +1 → Primary = 1001, replicated to Secondary = 1001
- Primary fails
- Failover to Secondary: Counter = 1001, no loss, but 10-second downtime

**Active-Active (Multi-Master):**

- Both systems accept writes simultaneously
- TX1: System A receives "+1" → A counter = 1001, replicates to B
- TX2: System B receives "+1" → B counter = 1001, replicates to A
- Conflict! Both systems have 1001, but should be 1002
- Solution: One system wins (total loss or conflict resolution), or use CRDT (conflict-free data structure)

**THE INSIGHT:**
Active-active trades simpler failover for harder consistency. Only use when consistency challenges solvable (sharding, event sourcing, CRDTs).

---

### 🧠 Mental Model / Analogy

> Two banks in a city, same brand. Each has the customer database. Customers can bank at either location. If one burns down, the other keeps running.

But conflict arises: Customer withdraws $100 from Branch A. Simultaneously withdraws $100 from Branch B (before replication syncs). Now branch A has $-100 and branch B has $-100 (total $-200, but should be $-100).

Solution: (1) Require replication sync before allowing withdrawals (essentially serial), or (2) Accept temporary inconsistency, reconcile later (eventual consistency), or (3) Shard: Branch A owns accounts 1-5000, Branch B owns 5001-10000 (no conflict possible).

- "Two bank branches" → Two systems
- "Customers banking at either" → Requests routed to either (active-active)
- "If one burns down" → Failure, other continues
- "Withdrawal conflict" → Data consistency problem in active-active

**Where analogy breaks down:** Real banks have central ledger (single source of truth). Computer systems trying to be fully active-active must avoid this bottleneck.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Two servers both serving traffic. If one fails, the other keeps going. No downtime, no switchover needed.

**Level 2 — How to use it (junior developer):**
For stateless services (web servers), deploy to both regions/datacenters. Load balancer routes requests to both. If one region fails, traffic continues to the other. For databases, active-active is harder—data consistency issues arise.

**Level 3 — How it works (mid-level engineer):**
Stateless: Both servers independent, no shared state, load balancer distributes traffic. Stateful: More complex. Options: (A) Multi-master replication with conflict resolution, (B) Sharding (each system owns part of data), (C) Event sourcing (write to shared log, replay to both). Each has tradeoffs. Implement monitoring to detect when one system down, ensure other handles full load.

**Level 4 — Why it was designed this way (senior/staff):**
Active-active emerged from high-availability and scale requirements. With active-passive, backup capacity wasted. Active-active utilizes all capacity, but data consistency becomes challenge. Multi-master replication (naive) caused conflicts. Modern solutions: CRDTs (conflict-free data structures), event sourcing (write to log), sharding (partition by key). Google, Netflix use active-active for multi-region resilience. Key insight: active-active works well for stateless services and perfectly-partitioned stateful services, but not for fully-replicated state.

---

### ⚙️ How It Works (Mechanism)

Active-active architecture:

```
STATELESS TIER (Easy):
  Region-1: [WEB-A] ──┐
  Region-2: [WEB-B] ──┼─ Load Balancer ── Clients

  Both regions:
    - Same code
    - No local state (all state in database tier)
    - Can handle 100% of traffic if one fails

  Failure: Region-1 fails
    → Load balancer removes WEB-A
    → WEB-B handles all traffic
    → No downtime, no data loss

STATEFUL TIER (Hard):

  Option A: Multi-Master Replication
  ────────────────────────────────────
  [DB-MASTER-A] ←→ (bidirectional replication) ←→ [DB-MASTER-B]

  Write from Region-1: "UPDATE counter = counter + 1"
  → Executed on DB-A
  → Replicated to DB-B
  → DB-A: counter = 1001
  → DB-B: counter = 1001

  But what if simultaneous writes?
  → DB-A: counter += 1 (→ 1001)
  → DB-B: counter += 1 (→ 1001)
  → Both have 1001, should be 1002
  → Conflict! Need resolution.

  Option B: Sharding (Conflict-Free)
  ──────────────────────────────────
  [DB-A owns data 0-50M] ←→ (no replication needed) ←→ [DB-B owns data 50M-100M]

  Write to Region-1 → goes to DB-A (owns that range)
  Write to Region-2 → goes to DB-B (owns that range)

  No conflicts (different data owned by each).
  Tradeoff: If DB-A fails, lose data for range 0-50M (until recovery).

  Option C: Event Sourcing
  ────────────────────────
  [Event Log (shared)]
    ↑ ↑ (both append)
  [DB-A] [DB-B]

  All writes go to shared log first
  Both DB-A and DB-B replay events
  Guarantees both databases eventually consistent
  Tradeoff: Shared log is bottleneck (unless replicated itself)

  Option D: CRDT (Conflict-Free Data Structure)
  ──────────────────────────────────────────────
  Counter with vector clock:
  [DB-A] counter = {A: 10, B: 5} (sum = 15)
  [DB-B] counter = {A: 10, B: 5} (sum = 15)

  A increments: {A: 11, B: 5} (sum = 16)
  B increments: {A: 10, B: 6} (sum = 16)

  After replication:
  Both have {A: 11, B: 6} (sum = 17)
  No conflict, no data loss.
```

**Choice of Strategy:**

- **Multi-master + conflict resolution**: For small, easy conflicts (last-write-wins, application logic)
- **Sharding**: For large datasets, clear partitioning key (user_id, tenant_id)
- **Event sourcing**: For audit trail, complex business logic
- **CRDT**: For highly available, partition-tolerant systems (trade: write amplification)

---

### 🔄 The Complete Picture — End-to-End Flow

```
Request Arrives
    ↓
Load Balancer decides: Route to Region-A or Region-B?
    └─ Round-robin, or latency-based, or user-affinity
    ↓
Request processed in chosen region
    ├─ If stateless: Handle entirely in that region (no problem)
    └─ If stateful: Update database in that region
    ↓
Replication (if applicable):
    ├─ Multi-master: Replicate write to other region (may cause conflict)
    ├─ Sharding: No replication (other region doesn't own that data)
    ├─ Event sourcing: Write to shared log (other region replays)
    └─ CRDT: Merge concurrent updates (conflict-free)
    ↓
Response returned to client
    ↓
If Region-A fails:
    ├─ Requests still arriving
    ├─ Load balancer removes Region-A from pool
    ├─ All traffic → Region-B
    ├─ Region-B continues serving (but at higher load, may slow down)
    ├─ No downtime, no failover pause
    └─ Data loss depends on replication choice:
        ├─ Multi-master + quorum: minimal loss
        ├─ Sharding: loss of data owned by Region-A (until recovery)
        ├─ Event sourcing: no loss (shared log survives)
        └─ CRDT: no loss (eventually consistent)
```

---

### 💻 Code Example

Implementing active-active:

**Example 1 — Stateless Active-Active (Web Tier):**

```yaml
# Kubernetes deployment: stateless web servers in 2 regions
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 10 # 5 in region-a, 5 in region-b
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - podAffinityTerm:
            labelSelector:
              matchExpressions:
                - key: app
                  operator: In
                  values:
                    - api-server
            topologyKey: topology.kubernetes.io/region
          weight: 100 # Spread across regions

---
# Load balancer: route to both regions
apiVersion: v1
kind: Service
metadata:
  name: api-lb
spec:
  type: LoadBalancer
  selector:
    app: api-server
  ports:
    - port: 80
      targetPort: 8080
  sessionAffinity: None # Don't stick to one region
```

**Example 2 — Event Sourcing (Active-Active for Stateful):**

```python
from datetime import datetime
import json

class EventLog:
    """Shared event log (write-ahead log)"""
    def __init__(self):
        self.events = []
        self.version = 0

    def append(self, event):
        """Append event to log (all regions write here)"""
        self.version += 1
        event['version'] = self.version
        event['timestamp'] = datetime.now().isoformat()
        self.events.append(event)
        # Persist to replicated storage (e.g., S3, database)

    def get_since(self, version):
        """Get all events since version"""
        return [e for e in self.events if e['version'] > version]

class ReplicatedDatabase:
    """Database in each region, replays events from shared log"""
    def __init__(self, region):
        self.region = region
        self.counter = 0
        self.local_version = 0

    def apply_event(self, event):
        """Apply event from shared log"""
        if event['type'] == 'increment':
            self.counter += 1
        self.local_version = event['version']

    def write(self, event_log, event):
        """Write locally, then append to shared log"""
        # Apply to local database first
        self.apply_event(event)
        # Append to shared log (for replication to other regions)
        event_log.append(event)

    def sync_from_log(self, event_log):
        """Catch up with events from log"""
        new_events = event_log.get_since(self.local_version)
        for event in new_events:
            self.apply_event(event)

# Usage
event_log = EventLog()
db_region_a = ReplicatedDatabase('us-east')
db_region_b = ReplicatedDatabase('us-west')

# Region A writes
db_region_a.write(event_log, {'type': 'increment', 'region': 'us-east'})
print(f"Region A counter: {db_region_a.counter}")  # 1

# Region B writes
db_region_b.write(event_log, {'type': 'increment', 'region': 'us-west'})
print(f"Region B counter (before sync): {db_region_b.counter}")  # 1

# Region A syncs to get Region B's write
db_region_a.sync_from_log(event_log)
print(f"Region A counter (after sync): {db_region_a.counter}")  # 2

# Both regions consistent, no conflicts
```

**Example 3 — CRDT Vector Clock (Conflict-Free):**

```python
from typing import Dict

class VectorClockCounter:
    """Counter using vector clocks (CRDT)"""
    def __init__(self, region_id: str):
        self.region_id = region_id
        self.vector = {}  # {region_id: count}

    def increment(self):
        """Increment counter locally"""
        if self.region_id not in self.vector:
            self.vector[self.region_id] = 0
        self.vector[self.region_id] += 1

    def value(self):
        """Total value (sum of all region counts)"""
        return sum(self.vector.values())

    def merge(self, other_vector: Dict):
        """Merge with vector from other region (conflict-free)"""
        for region, count in other_vector.items():
            if region not in self.vector:
                self.vector[region] = count
            else:
                # For counter, take max (assuming no concurrent decrements)
                self.vector[region] = max(self.vector[region], count)

# Usage
counter_a = VectorClockCounter('region-a')
counter_b = VectorClockCounter('region-b')

# Region A increments twice
counter_a.increment()  # {a: 1}
counter_a.increment()  # {a: 2}

# Region B increments once
counter_b.increment()  # {b: 1}

# Replicate to both (eventual consistency)
counter_a.merge(counter_b.vector)  # A now has {a: 2, b: 1} (value = 3)
counter_b.merge(counter_a.vector)  # B now has {b: 1, a: 2} (value = 3)

print(f"Both consistent: A={counter_a.value()}, B={counter_b.value()}")  # Both = 3
```

---

### ⚖️ Comparison Table

| Aspect               | Active-Passive                | Active-Active                       |
| -------------------- | ----------------------------- | ----------------------------------- |
| **Failover Time**    | 5-15 seconds                  | 0 seconds (immediate)               |
| **Utilization**      | 50% (backup idle)             | 100% (both active)                  |
| **Data Consistency** | Simple (one writer)           | Complex (multi-master needed)       |
| **Complexity**       | Low                           | High                                |
| **Cost**             | Lower (backup not processing) | Higher (full infrastructure active) |
| **Suitable For**     | Traditional HA                | High-traffic, low-latency systems   |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                      |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| "Active-active is always better than active-passive"     | No. Active-active more complex, only worth it if failover delay costly or if load benefits justify complexity.               |
| "Active-active means no data loss"                       | No. Depends on replication strategy. Sharding can lose data owned by failed region. Multi-master can lose concurrent writes. |
| "All databases support active-active"                    | No. Requires multi-master replication (not all DBs support this well). Simpler: event sourcing or sharding.                  |
| "Active-active and multi-region are the same"            | No. Multi-region systems can be active-passive. Active-active is a specific HA pattern.                                      |
| "If one region fails, requests auto-redirect seamlessly" | Mostly. But if affinity/sharding used, requests to failed region are lost (client must retry).                               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Split-Brain (Both Think They're Primary)**

**Symptom:**
Network partition between regions. Region A still sees Region B as healthy (cached). Region B sees partition. Both accept writes. Data divergence.

**Root Cause:**
Network partition between regions. Insufficient consensus checks. Both regions think they're primary.

**Diagnostic Command:**

```bash
# Check consistency between regions
curl https://region-a/api/state | jq '.counter' > state_a.json
curl https://region-b/api/state | jq '.counter' > state_b.json

diff state_a.json state_b.json
# If different: split-brain detected
```

**Fix:**
Implement quorum: require majority vote to accept writes. If region A can't reach B and C, it stops accepting writes (self-isolates). Prevents divergence.

**Prevention:**
Test network partitions during chaos engineering. Implement fencing logic. Require 3+ regions for voting.

---

**Failure Mode 2: Thundering Herd (Region Failure Overloads Other Region)**

**Symptom:**
Region A has 10K requests/sec. Region B also has 10K requests/sec. Region A fails. All 20K requests suddenly go to Region B. Region B overwhelmed, timeouts, cascading failure.

**Root Cause:**
Region B not sized to handle 100% of traffic. Active-active assumes balanced load, but one region alone insufficient.

**Diagnostic Command:**

```bash
# Monitor request rate during region failure
watch -n 1 'curl https://region-b/metrics | jq .requests_per_sec'

# If jumps from 10K to 20K→ overload imminent
```

**Fix:**
Size each region to handle 100% of traffic (costly). Or implement load shedding: if region under load, return 503 (service unavailable), clients retry elsewhere.

**Prevention:**
Capacity planning: each region must handle full traffic. Or use adaptive load shedding (reduce feature flags, degraded mode).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Load Balancing` — distributes traffic to both regions
- `Replication` — keeps data synchronized
- `Distributed Systems` — consensus challenges

**Builds On This (learn these next):**

- `Event Sourcing` — one strategy for active-active
- `CRDT` — conflict-free data structures for active-active
- `Sharding` — another active-active strategy

**Alternatives / Comparisons:**

- `Active-Passive` — simpler, but less resilient
- `Multi-Region Architecture` — broader pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Both systems serve traffic; if one    │
│              │ fails, other continues (no failover   │
│              │ delay)                                │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Active-passive wastes backup          │
│ SOLVES       │ capacity; active-active uses both     │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Stateless easy; stateful hard         │
│              │ (data consistency challenges)         │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ High-traffic systems; low latency     │
│              │ required; multi-region deployment     │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Simple systems; single region; data   │
│              │ consistency critical                  │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [No failover delay, full capacity]    │
│              │ vs [complexity, consistency issues]   │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Both systems active, no switchover   │
│              │ needed, but data consistency hard."   │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Sharding → Event Sourcing → CRDT      │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have active-active across 2 regions, 50K requests/sec each. Region 1 fails. Region 2 only sized for 50K, now gets 100K. What happens? How do you prevent meltdown?

**Q2.** Implementing multi-master database replication for active-active. Two regions simultaneously write the same counter. How do you avoid data loss or conflicts?
