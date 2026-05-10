---
version: 2
layout: default
title: "Multi-Master Replication"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /databases/multi-master-replication/
id: DBF-052
category: Database Fundamentals
difficulty: ★★★
depends_on: Master-Slave Replication, Database Replication, Distributed Systems
used_by: Database Sharding, Geographic Distribution, High Availability
related: Master-Slave Replication, Conflict Resolution, CAP Theorem
tags:
  - database
  - replication
  - distributed-systems
  - deep-dive
---

# DBF-052 - Multi-Master Replication

⚡ TL;DR - Multi-master replication allows multiple database nodes to accept writes simultaneously - enabling write scale-out and geographic write distribution - but requires conflict resolution when the same data is written to two nodes concurrently.

| #447            | Category: Database Fundamentals                                     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Master-Slave Replication, Database Replication, Distributed Systems |                 |
| **Used by:**    | Database Sharding, Geographic Distribution, High Availability       |                 |
| **Related:**    | Master-Slave Replication, Conflict Resolution, CAP Theorem          |                 |

---

### 🔥 The Problem This Solves

**MASTER-SLAVE LIMITATION:**
Single primary accepts all writes. US-East primary: users in Tokyo or London have 150–250ms write latency (cross-continent RTT). 10,000 writes/second saturating the single primary's CPU/disk. A single server (even the largest available) cannot keep up. Vertical scaling has reached its limit.

**THE SOLUTION:**
Allow multiple servers to accept writes. Tokyo writes go to Tokyo node. London writes go to London node. Both are authoritative. Both synchronize with each other.

**THE NEW PROBLEM:**
User A in Tokyo updates record 42 to value "X". User B in London updates record 42 to value "Y" at the same time. Tokyo and London haven't synchronized yet. Both committed "their" version. Which wins?

---

### 📘 Textbook Definition

**Multi-master replication** (also called **active-active replication** or **multi-primary**) is a replication topology where two or more nodes can each accept write operations. Changes are propagated to all other masters. When the same data is modified on multiple masters before synchronization, a **write conflict** occurs and must be resolved. Conflict resolution strategies include: **last-write-wins (LWW)** - timestamp determines winner (risk: clock skew); **application-layer resolution** - application logic merges conflicts; **CRDTs (Conflict-free Replicated Data Types)** - data structures designed to merge without conflicts; **manual resolution** - store both versions, flag for human review. Multi-master implementations: **Galera Cluster** (MySQL/MariaDB - synchronous multi-master), **CockroachDB** (distributed SQL), **Cassandra** (LWW), **DynamoDB** (LWW), **Couchbase**, **PostgreSQL BDR** (Bi-Directional Replication).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Multi-master lets every node write - enabling geographic write distribution and write scale-out - but you must decide what happens when two nodes write the same row at the same time.

**One analogy:**

> Two editors (masters) working on the same Wikipedia article simultaneously, in different offices with no internet. Both make changes to the same paragraph. When their networks reconnect, Wikipedia's system must merge or pick between their edits. Last-write-wins: the later timestamp's edit survives. CRDT: both edits are structurally compatible (e.g., appending to a list) - both survive. Manual: an administrator reviews both versions and picks.

- "Two editors" → two master nodes
- "Same paragraph, different offices" → concurrent writes before synchronization
- "Networks reconnect" → inter-master replication (sync)
- "Wikipedia merge" → conflict resolution
- "Later timestamp wins" → last-write-wins (LWW)
- "Both edits appended" → CRDT (conflict-free data structure)

**One insight:**
Multi-master replication doesn't eliminate conflicts - it shifts the problem from "wait for the master" (blocking, latency) to "resolve conflicts after the fact" (non-blocking, but complex). The fundamental theorem: you cannot have strong consistency + high availability + network partition tolerance simultaneously (CAP theorem). Multi-master chooses availability over strong consistency.

---

### 🔩 First Principles Explanation

**CONFLICT TYPES:**

1. **Write-Write Conflict:** Two masters update the same row concurrently. Most common and most dangerous.
2. **Delete-Update Conflict:** Master A deletes a row; Master B updates the same row concurrently. Which wins?
3. **Insert-Insert Conflict:** Two masters insert rows with the same PK (if PKs aren't globally unique).

**CONFLICT RESOLUTION STRATEGIES:**

```
LAST-WRITE-WINS (LWW):
Update timestamped at T1=100ms vs T2=150ms → T2 wins
Problem: clock skew - node clocks differ by 5ms → wrong winner
Solution: use logical clocks (Lamport timestamps) or hybrid logical clocks (HLC)
Used by: Cassandra, DynamoDB (configurable)

FIRST-WRITE-WINS:
First commit wins; subsequent conflicting writes rejected
Used by: Galera Cluster (synchronous multi-master)

APPLICATION-LAYER RESOLUTION:
Application defines merge logic:
  "if both users updated quantity, take MAX(quantity)"
  "if both added to a shopping cart, merge the items"
  "if a record was updated and deleted, flag for human review"
Used by: CouchDB (with application-supplied merge functions)

CRDTs (Conflict-free Replicated Data Types):
Data structures designed to always merge without conflicts:
  G-Counter: grow-only counter; merge = MAX per node; sum for final
  PN-Counter: grow+shrink counter using two G-Counters
  OR-Set: add/remove set where concurrent add+remove = add wins
  LWW-Register: last-write-wins at element level
Used by: Riak, Cassandra (some types), Redis CRDT (Redis Enterprise)
```

**GALERA CLUSTER (MySQL/MariaDB - Synchronous Multi-Master):**

```
All writes are certified before commit:
1. Node 1: user runs UPDATE products SET price=9.99 WHERE id=42
2. Node 1: creates a "write set" (transaction + conflicts detection data)
3. Node 1: broadcasts write set to all cluster nodes (synchronously!)
4. All nodes certify: does this conflict with any concurrent transaction?
5. If conflict detected → one is committed, other is rolled back (first wins)
6. If no conflict → all nodes apply

Result: no async lag; strongly consistent; write latency = RTT between all nodes
Limitation: all nodes must be in same datacenter (RTT must be < 1ms)
            write throughput limited by certification overhead
```

**POSTGRESQL BDR (Bi-Directional Replication):**

```
Async multi-master; conflict resolution via:
  - LWW based on timestamps
  - Custom conflict resolution functions
  - Manual conflict detection and resolution
  - Use column-level tracking for fine-grained conflict detection
BDR nodes can be geographically distributed (async)
Used for: multi-region PostgreSQL deployments
```

**THE TRADE-OFFS:**
**Gain:** Write scale-out (multiple nodes accept writes); geographic write distribution (reduce cross-region write latency); continued write availability during network partition (CAP: choose Availability over Consistency).
**Cost:** Conflict resolution complexity; eventual consistency during network partition; higher operational complexity; potential data loss or merge surprises (LWW silently discards one write).

---

### 🧪 Thought Experiment

**SCENARIO: Account Balance in Multi-Master (LWW)**

Account #42, balance = $1,000.

- Tokyo node: User A deducts $100 at T=1000ms → balance=$900 (LWW timestamp=1000)
- London node: User B deducts $200 at T=1001ms → balance=$800 (LWW timestamp=1001)
- Both writes committed to their respective nodes.
- Nodes synchronize:
  - Tokyo receives London's write: T=1001 > T=1000 → London's write wins
  - Result at Tokyo: balance=$800 (User A's $100 deduction silently LOST)
  - London receives Tokyo's write: T=1000 < T=1001 → London's write wins
  - Result at London: balance=$800
- Final state: balance=$800, but $100 has been lost. INCONSISTENCY.

**CORRECT APPROACH FOR FINANCIAL DATA:**
LWW is NEVER appropriate for financial balances. Options:

1. Use single primary for balance updates; multi-master for non-financial data.
2. Use Galera (synchronous multi-master) - one write rejected on conflict, no silent data loss.
3. Use distributed transactions (2PC / Saga) with explicit conflict detection.
4. Use an append-only ledger (event sourcing): never update balances, only append transactions; balance = sum of transactions. Concurrent appends to the log are always safe (no conflict).

---

### 🧠 Mental Model / Analogy

> Multi-master is like two cashiers at a store with only one item of a rare product. Without communication: both sell it simultaneously to different customers. When the store inventory synchronizes: either conflict (two receipts for one item - last-write-wins → one customer gets it) or the store accepts the loss (both customers get it somehow). Single master: only one cashier has the authority to sell - the other sends customers to the first cashier (write goes to primary). Multi-master: both cashiers can sell, but "selling the same last item" to two people requires a rule to resolve.

- "Two cashiers" → two master nodes
- "Same rare item" → same row being written
- "Customers sent to first cashier" → master-slave write routing
- "Both sell simultaneously" → concurrent conflicting writes
- "Rule to resolve" → conflict resolution strategy (LWW, Galera certification, CRDT)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Multi-master means multiple database servers can each accept writes. The benefit: faster writes if you're in a different country from the main server. The challenge: if two servers change the same data at the same time, someone has to decide which version wins - or find a way to merge both.

**Level 2:** Use multi-master for: geographic distribution of writes (users write to their nearest region), or specific high-write-throughput use cases. Never use LWW conflict resolution for financial data or any field where losing a write is unacceptable. Use synchronous multi-master (Galera) when you need strong consistency within a single datacenter. Use CRDTs for types that naturally merge (counters, sets).

**Level 3:** Galera's certification-based conflict detection: each write set includes "keys" (rows affected). On broadcast, every node checks if any inflight transaction modifies the same keys. If a conflict is detected, the second-arriving transaction is rolled back (applier exception). This is synchronous certification - it happens before commit acknowledgment. Latency = RTT between all Galera nodes (must be low → same DC). Maximum sustainable write throughput ≈ network RTT / transaction size. CockroachDB uses Raft consensus within each "range" (shard): writes within a range go through Raft consensus (majority of Raft nodes must ACK). This is synchronous within the consensus group. Between ranges: cross-range transactions use distributed transactions (2PC over Raft). This gives CockroachDB strong consistency across all writes globally, with geographic distribution - at the cost of cross-region write latency when the consensus group spans regions.

**Level 4:** Multi-master replication is the practical expression of the CAP theorem trade-off. By allowing multiple nodes to accept writes independently (during network partition), multi-master systems choose Availability over Consistency. The price: during the partition, divergent state can accumulate; on reconnection, conflicts must be resolved. LWW is the blunt conflict resolution tool: operationally simple (no application changes), but silently discards writes. For applications where data loss is unacceptable, multi-master with LWW is unsuitable. The principled alternatives: CRDTs (mathematically proven to merge without loss), Saga patterns (compensating transactions for conflict resolution), or accepting that the data is inherently non-conflicting (e.g., separate users own separate rows, so conflicts are structurally impossible). The insight: **multi-master is a network design choice, not just a database choice**. When regions can always communicate (single datacenter, cross-AZ), synchronous multi-master (Galera, CockroachDB) is feasible. When regions may partition (cross-continent), asynchronous with conflict resolution (Cassandra LWW, DynamoDB) is the only practical option.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MULTI-MASTER: ASYNC CONFLICT FLOW                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Tokyo Node          London Node                      │
│ ──────────          ───────────                      │
│ UPDATE row A=X      UPDATE row A=Y  (concurrent)     │
│ Commit (local)      Commit (local)                   │
│                                                      │
│ [Network sync - some milliseconds later]             │
│                                                      │
│ Tokyo receives Y:   London receives X:               │
│ A is X locally      A is Y locally                   │
│ Y has later ts?     X has earlier ts?                │
│ Yes → A=Y (LWW)     No → A=Y (LWW)                  │
│ X was lost!         Consistent with Y                │
│                                                      │
│ GALERA (sync):                                       │
│ Both write sets certified before commit              │
│ Conflict detected: second writer rolled back         │
│ No lost writes: one succeeds, one gets error→retry   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**GEOGRAPHIC WRITE DISTRIBUTION:**

```
User in Tokyo: writes profile update
→ Routes to Tokyo node (nearest)
→ [MULTI-MASTER ← YOU ARE HERE: local write]
→ Tokyo commits immediately (no cross-region RTT)
→ Async replication to London, US-East nodes
→ All nodes eventually consistent (~100ms cross-region lag)
→ Tokyo user: sees their write immediately
→ London user: sees Tokyo's write ~100ms later
```

**CONFLICT PATH:**

```
User A in Tokyo: UPDATE user SET email='a@new.com' WHERE id=42
User B in London: UPDATE user SET email='b@new.com' WHERE id=42 (simultaneous)
Both commit locally → conflict on sync
LWW: later timestamp wins → one email is silently dropped
Application never notified → data loss
Correct design: email update should go to single master (master-slave for this field)
               OR use application-layer conflict resolution
               OR structure data so conflicts are impossible (users own their own rows)
```

**WHAT CHANGES AT SCALE:**
Cassandra multi-datacenter: replication factor 3 per DC; quorum reads/writes require majority within DC. Write to local DC first (LOCAL_QUORUM); replicated to other DCs async. Tunable consistency: `CONSISTENCY LOCAL_QUORUM` = fast local writes, eventual cross-DC. Amazon DynamoDB Global Tables: multi-region active-active; LWW conflict resolution; sub-second cross-region replication. Used for: global user sessions, global inventory (with care about LWW).

---

### ⚖️ Comparison Table

| Feature       | Master-Slave                       | Galera (Sync Multi-Master) | Cassandra/DynoDB (Async Multi-Master) |
| ------------- | ---------------------------------- | -------------------------- | ------------------------------------- |
| Write nodes   | 1                                  | All (certified)            | All (independent)                     |
| Conflict      | Impossible                         | Detected + rolled back     | LWW (one silently lost)               |
| Consistency   | Strong (single master)             | Strong (certified)         | Eventual (async)                      |
| Write latency | Single DC: low; cross-region: high | RTT between all nodes      | Local DC: low; cross-DC async         |
| Availability  | Medium (failover gap)              | High (any node writeable)  | Very High (always writeable)          |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                      |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Multi-master provides perfect write availability        | During network partition with async multi-master, nodes can accept conflicting writes; one will be discarded on merge - not "perfect" availability without data loss risk                    |
| Galera is truly multi-master                            | Galera is synchronous multi-master - writes are certified before commit, so it prevents conflicts; but write throughput is limited by inter-node certification latency                       |
| Multi-master means better performance for all workloads | Only for write-heavy, geographically distributed workloads. For workloads with conflicting writes, multi-master adds conflict resolution overhead                                            |
| CRDTs solve all multi-master problems                   | CRDTs only work for data types that can be designed as CRDTs (counters, sets, registers). Arbitrary relational data with complex invariants (e.g., balance ≥ 0) cannot be expressed as CRDTs |

---

### 🚨 Failure Modes & Diagnosis

**1. LWW Silent Data Loss**

**Symptom:** Audit log shows a record was updated but the current value doesn't reflect all updates; users report their changes being "overwritten" by other users' concurrent changes.

**Root Cause:** LWW conflict resolution discarded a write without notification - the application and user never knew.

**Diagnostic:**

```
Check: is the database multi-master with LWW? (Cassandra, DynamoDB)
Compare: timestamp of conflicting writes in audit log
Result: the later-timestamp write won; earlier write silently lost
```

**Fix (architectural):** For fields where data loss is unacceptable: route writes through a single primary region. Or use append-only semantics (event sourcing) - never update, always append; conflicts are impossible with append-only. Or redesign schema to avoid concurrent writes to the same field.

**Prevention:** LWW is appropriate for idempotent, naturally "last update wins" data (e.g., user presence status, location coordinates). It is NEVER appropriate for financial data, counts, or any field where all writes must be preserved.

---

**2. Galera Cluster Write Stall During Network Hiccup**

**Symptom:** Application experiences sudden write stalls (hanging requests) when a Galera node has a network issue; writes resume after the node is fenced.

**Root Cause:** Galera requires certification acknowledgment from all nodes before committing. If one node is slow or unreachable, writes stall waiting for its certification response (until flow control kicks in or the node is expelled from the cluster).

**Diagnostic:**

```sql
-- Galera status (on any node):
SHOW STATUS LIKE 'wsrep_%';
-- wsrep_cluster_status: Primary (healthy) or Non-Primary (partitioned)
-- wsrep_local_recv_queue_avg: high value → node falling behind
-- wsrep_flow_control_paused: > 0 → flow control active; writes stalled
```

**Fix:** Fence the lagging node (remove from cluster): `SET GLOBAL wsrep_provider_options = 'pc.ignore_sb = yes'` (use with caution). Or configure `wsrep_provider_options = 'evs.suspect_timeout=PT5S'` to eject nodes quickly on failure.

**Prevention:** Ensure all Galera nodes have similar hardware (same latency profile). Set `wsrep_sync_wait` appropriately. Place all Galera nodes in the same datacenter (intra-DC RTT < 1ms).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Master-Slave Replication` - multi-master extends master-slave to multiple write nodes
- `Database Replication` - the mechanism; multi-master is a topology
- `Distributed Systems` - CAP theorem, conflict resolution, eventual consistency

**Builds On This (learn these next):**

- `Database Sharding` - alternative to multi-master for write scale (avoid conflicts by partitioning)
- `CAP Theorem` - the theoretical basis for multi-master's consistency trade-off
- `CRDT` - conflict-free data types that enable multi-master without conflict resolution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multiple writable nodes; writes accepted  │
│              │ anywhere; changes sync between nodes      │
├──────────────┼───────────────────────────────────────────┤
│ CONFLICT     │ LWW: later ts wins (silently drops other) │
│ RESOLUTION   │ Galera: cert-based, one rolled back       │
│              │ CRDT: merge without conflict              │
│              │ App-layer: custom merge logic             │
├──────────────┼───────────────────────────────────────────┤
│ USE FOR      │ Geographic write distribution             │
│              │ Write scale-out (careful: conflict risk)  │
├──────────────┼───────────────────────────────────────────┤
│ NEVER LWW    │ Financial data, balances, counts          │
│              │ Any field where silent loss = unacceptable│
├──────────────┼───────────────────────────────────────────┤
│ CAP TRADE    │ Availability > Consistency during         │
│              │ partition (async multi-master)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Everyone writes, conflicts happen -      │
│              │  your resolution strategy IS your design" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database Sharding → CAP Theorem → CRDTs   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design the replication strategy for a global e-commerce platform that needs: (a) product catalog updates (written by admins, read by everyone) with strong consistency; (b) user cart data (written only by the owning user, read quickly from their nearest region); (c) order placement (financial transaction, must not lose a write). For each data type: choose single-master or multi-master, conflict resolution strategy, and consistency model. Justify the different strategies for different data types.

**Q2.** (TYPE F - Comparison Depth) Compare CockroachDB (consensus-based distributed SQL) vs. Cassandra (async multi-master with LWW) on: (a) write conflict handling, (b) write latency for cross-region writes, (c) consistency guarantee, (d) operational complexity. In what specific use case would you choose each, and what would make you switch from one to the other?
