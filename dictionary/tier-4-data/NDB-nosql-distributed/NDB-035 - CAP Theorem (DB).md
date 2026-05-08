---
layout: default
title: "CAP Theorem (DB)"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /nosql/cap-theorem-db/
id: NDB-035
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Distributed Systems, Eventual Consistency in NoSQL, Column Family
used_by: System Design, Distributed Transactions, Polyglot Persistence
related: Eventual Consistency in NoSQL, PACELC, Distributed Systems
tags:
  - nosql
  - cap-theorem
  - distributed-systems
  - deep-dive
---

# NDB-035 - CAP Theorem (DB)

⚡ TL;DR - The CAP theorem states that during a network partition, a distributed system must choose between Consistency (every read reflects the latest write) and Availability (every request receives a response) - you cannot have both simultaneously; **PACELC** extends this: even without partitions, there's a trade-off between Latency and Consistency.

| #469            | Category: NoSQL & Distributed Databases                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Eventual Consistency in NoSQL, Column Family |                 |
| **Used by:**    | System Design, Distributed Transactions, Polyglot Persistence     |                 |
| **Related:**    | Eventual Consistency in NoSQL, PACELC, Distributed Systems        |                 |

---

### 🔥 The Problem This Solves

**NETWORK PARTITIONS HAPPEN:**
In a distributed database with multiple nodes across data centers, network failures are not hypothetical - they're inevitable. When a network partition occurs (some nodes can't communicate with others), the system faces a binary choice: should the remaining reachable nodes continue accepting writes (availability) and risk diverging from the isolated nodes (losing consistency)? Or should they refuse writes (consistency) until the partition heals (losing availability)?

**CAP THEOREM:**
Eric Brewer's CAP theorem (2000, proved by Gilbert and Lynch 2002) formalizes this: a distributed system can guarantee at most 2 of 3 properties: Consistency, Availability, Partition Tolerance. Since partition tolerance is mandatory in any real distributed system (networks fail), the real choice is: CP (sacrifice availability during partitions) vs. AP (sacrifice consistency during partitions). Understanding this drives database selection for specific use cases.

---

### 📘 Textbook Definition

**CAP Theorem** states that any distributed data store can guarantee at most two of three properties: **Consistency (C)** - every read returns the most recent write or an error (all nodes see the same data at the same time; equivalent to linearizability); **Availability (A)** - every request (to a non-failed node) receives a response (not an error, but not necessarily the most recent write); **Partition Tolerance (P)** - the system continues operating despite arbitrary network partitions (messages delayed or dropped between nodes). Since partition tolerance is required in any practical distributed system (network partitions are a physical reality), the effective choice is: **CP systems** - remain consistent, sacrifice availability during partitions (HBase, Zookeeper, etcd, CockroachDB, Spanner); **AP systems** - remain available, sacrifice consistency during partitions (Cassandra, CouchDB, DynamoDB default, Riak). **PACELC** (Daniel Abadi, 2012): extends CAP by acknowledging that even without partitions (P), there's a trade-off between **Latency (L)** and **Consistency (C)**. Most real-world distributed database design decisions are about the PACELC trade-off (latency vs. consistency) more than the CAP partition scenario.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CAP: when a network partition occurs, pick consistency (CP: refuse writes to stay correct) or availability (AP: accept writes and risk divergence); PACELC adds: even without partitions, you choose lower latency or stronger consistency.

**One analogy:**

> Two bank branches with a direct phone line. Branch A (New York) and Branch B (London). Normally: call each other for every transaction (consistent, but slower due to cross-Atlantic delay). During a phone outage (partition): Branch A must choose: (1) stop accepting transactions until the line is restored (CP: consistent but unavailable), or (2) continue accepting transactions and reconcile later (AP: available but potentially inconsistent). PACELC adds: even with the phone working, the cross-Atlantic call takes 100ms. Trade: accept local inconsistency risk for lower latency (serve from local state) vs. always call London (consistent but slower).

- "Phone line outage" → network partition
- "Stop accepting transactions" → CP (consistency over availability)
- "Continue accepting and reconcile later" → AP (availability over consistency)
- "Cross-Atlantic call = 100ms delay" → PACELC latency trade-off
- "Serve from local state" → PACELC: EL (Else Latency)

**One insight:**
"CA system" (consistent + available, no partition tolerance) is effectively a fiction for distributed systems. Every system with multiple network-connected nodes can experience a partition. Calling a single-node PostgreSQL "CA" is technically correct but practically useless - you can't horizontally scale without introducing P. The meaningful choice is: during a partition, prefer CP or AP. PACELC is more useful for day-to-day database selection because it covers the common case (no partition, but latency/consistency trade-off).

---

### 🔩 First Principles Explanation

**THE PARTITION SCENARIO:**

```
Distributed database: 3 nodes (N1, N2, N3) in 3 data centers
Normal operation:
  Write to N1 → N1 replicates to N2, N3 → all nodes consistent
  Read from any node → returns same value ✓

Network partition: N1 isolated from N2, N3
  Client writes "balance = $500" to N1
  N1 cannot replicate to N2, N3 (partition)

[CAP THEOREM ← YOU ARE HERE: partition occurs, must choose]

CP CHOICE (ZooKeeper, etcd, HBase, Spanner):
  N2 and N3: refuse writes (cannot reach quorum of nodes)
  Return: ServiceUnavailableException
  N1: also refuses writes (cannot reach quorum)
  Effect: system is UNAVAILABLE during partition
  Guarantee: when partition heals, all nodes agree on same value
  No split-brain, no data divergence

AP CHOICE (Cassandra, CouchDB, DynamoDB default):
  N1: accepts write, "balance = $500"
  N2, N3: accept writes independently, e.g., "balance = $600"
  Different values on different nodes during partition
  When partition heals: conflict resolution needed (Last Write Wins, CRDT, etc.)
  Effect: AVAILABLE during partition
  Compromise: consistency (reads may return stale/conflicting values)
```

**CASSANDRA CONSISTENCY LEVELS (AP WITH TUNABLE CONSISTENCY):**

```
Cassandra (RF=3): AP system by default, but tunable

CL = ONE (AP extreme):
  Write: ack when 1 replica writes → fast, survives partition (1 node enough)
  Read: read from 1 replica → may be stale (replica may be behind)

CL = QUORUM (AP balanced):
  Write: ack when majority (⌈3/2⌉+1 = 2) of replicas write
  Read: read from majority (2) of replicas
  Read-write quorum overlap: W(2) + R(2) > RF(3) → guaranteed to read latest write
  Effectively consistent for most scenarios (unless 2 replicas are partitioned)

CL = ALL (CP-like):
  Write: ack when ALL 3 replicas write → any node outage = unavailable
  Read: read from all 3 replicas → fails if any node is down
  Consistent but sacrifices availability (loses AP nature)

"Tunable consistency" = the real power of Cassandra:
  Time-series data (OK to read slightly stale): CL = ONE
  Financial ledger queries (must be consistent): CL = QUORUM
  Critical audit read (must be absolutely consistent): CL = ALL
  Different consistency per operation within the same cluster
```

**PACELC FRAMEWORK:**

```
PACELC: If (Partition) then (Availability vs. Consistency) else (Latency vs. Consistency)

During partition: same as CAP (A vs. C)
Without partition: Latency vs. Consistency

Without partition, you want to read from N1 (local, fast).
But N2 may have a more recent write (slightly inconsistent).

Latency trade-off:
  EL (prefer Latency): serve reads from nearest/fastest replica
    → may return stale data (1-2 replica lag)
    → fast response (no cross-region round trip)
  EC (prefer Consistency): read from primary, wait for cross-region replica to confirm
    → always returns latest write
    → higher latency (cross-region RTT: 100-200ms)

Database PACELC Classification:
  DynamoDB: PA/EL  (AP during partition; Eventual Consistency = low latency by default)
  Cassandra: PA/EL  (AP during partition; configurable; default = EL)
  CRDB/Spanner: PC/EC (CP during partition; Strong Consistency = higher latency)
  VoltDB: PC/EC   (CP during partition; always consistent = higher latency)
  MongoDB (primary): PC/EC (CP; primary read = consistent but no latency benefit)
  MongoDB (secondary reads): PC/EL (reads from secondary = potentially stale, lower latency)
```

**SPLIT-BRAIN PROBLEM:**

```
Network partition: Cluster A (N1, N2) isolated from Cluster B (N3, N4, N5)
AP system: both clusters accept writes
  Cluster A: updates user balance to $800
  Cluster B: updates user balance to $600

Both clusters believe they are the authoritative partition.
This is SPLIT-BRAIN: two sub-clusters both believing they are "the truth."

When partition heals: conflict resolution:
  LWW (Last Write Wins): keep the write with the higher timestamp
    → Risk: clock skew (N1 clock is 1s ahead of N3) → wrong write wins

  CRDT: merge by mathematical law (G-Counter: sum all per-node increments)
    → Correct merge, no data loss, but only works for specific data types

  Manual conflict resolution: application sees conflicting versions, must resolve
    → Riak: exposes conflicts to application
    → Amazon shopping cart: "add wins" semantics (never lose an item)

CP systems prevent split-brain:
  Raft / Paxos: only the leader (majority partition) accepts writes
  Minority partition: refuses writes
  → No conflicting writes to resolve
  → Cost: minority partition is unavailable
```

---

### 🧪 Thought Experiment

**BANKING TRANSFER DURING NETWORK PARTITION**

Bank has 3 data center nodes. User transfers $1,000 from Account A to Account B.
Network partition: DC3 is isolated from DC1 and DC2.

**AP SYSTEM (e.g., Cassandra CL=ONE):**

- DC1 accepts debit from Account A: A.balance = A.balance - 1000
- DC3 (isolated) accepts credit to Account B: B.balance = B.balance + 1000
- Partition heals: what happened?
  - Account A has been debited (correct)
  - Account B has been credited (correct, but we need to verify A was actually debited)
  - But: what if the client retried the transfer on DC3 thinking it failed?
  - Double credit? Or double debit + credit?
- For banking: **AP is WRONG**. Loss of money or double-crediting is unacceptable.

**CP SYSTEM (e.g., CockroachDB QUORUM write):**

- DC3 isolated from DC1+DC2 (DC3 is minority = 1 of 3 nodes)
- CockroachDB: DC3 refuses writes (cannot achieve quorum)
- DC1+DC2: quorum achieved (2 of 3), accept the transfer
- Transfer succeeds atomically on DC1+DC2
- DC3 remains read-only until partition heals
- User in DC3's region: gets ServiceUnavailableException (temporarily)
- Partition heals: DC3 syncs from DC1+DC2; all nodes consistent
- **No double spend, no lost money**

**THE LESSON:**
For money and other value-transfer operations: CP is the only correct choice. The temporary unavailability (ServiceUnavailableException during partition) is far preferable to inconsistent financial data. For profile pictures, recommendation feeds, like counts: AP is fine - users can tolerate seeing a slightly stale feed.

---

### 🧠 Mental Model / Analogy

> CAP is like a three-way light switch that controls: (C) all lights show the same color, (A) any light responds when you flip it, (P) lights still work when wires are cut. During a wiring cut (partition), you can't guarantee both A (all switches respond) and C (they all show the same color). CP: the system refuses to respond unless it can confirm the color with all other switches (consistent but may be unresponsive). AP: each switch responds with whatever color it last knew, and they may not agree (available but may be inconsistent). PACELC: even without wiring cuts, fast response (local state) vs. correct color (wait for all switches to confer) is a trade-off.

- "Wire cut" → network partition
- "All lights same color" → Consistency (all nodes same value)
- "Any light responds" → Availability (every node responds)
- "Wires work even if some cut" → Partition Tolerance
- "Refuse to respond without confirming color" → CP (sacrifice availability)
- "Respond with last known color" → AP (sacrifice consistency)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** CAP: in a distributed system, when the network breaks, choose consistency (refuse operations to stay correct) or availability (keep operating and risk stale data). Banks need CP (no wrong balances). Social feeds are fine with AP (slightly stale is OK). PACELC: even without breaks, fast-but-maybe-stale vs. slow-but-correct is a choice you make daily in system design.

**Level 2:** Apply to real databases: Cassandra = AP (configurable toward CP with ALL); DynamoDB = AP by default (use ConsistentRead: true for CP); ZooKeeper/etcd = CP; CockroachDB/Spanner = CP (Raft consensus). QUORUM reads/writes in Cassandra give effectively consistent behavior for most cases without sacrificing full availability. Use CAP to justify database choice to stakeholders: "We chose Cassandra (AP) because 1-second stale is acceptable for feed; we chose PostgreSQL (effectively CP) for financial records."

**Level 3:** The formal CAP theorem (Gilbert-Lynch 2002) uses linearizability for C and total availability for A. In practice, systems don't achieve either extreme. "Consistency" in CAP = linearizability (stronger than sequential consistency, causally consistency, eventual consistency). Most AP databases provide eventual consistency or causal consistency (weaker). PACELC is more practically useful: it acknowledges that the real-world trade-off is latency vs. consistency in the common (no partition) case. Multi-version Concurrency Control (MVCC): both CP and AP systems use MVCC internally; MVCC enables snapshot reads without blocking, but doesn't resolve the AP vs. CP partition-time choice. Amazon's Dynamo paper (2007) introduced the shopping cart "add wins" semantics as a domain-specific conflict resolution strategy (more nuanced than LWW).

**Level 4:** The CAP theorem is often misunderstood in two ways. First: "CA systems exist" - this is only true for single-node systems. Any multi-node system where the network can fail must tolerate partitions or it's not a distributed system. The "CA" classification refers to what properties the system prioritizes _absent partitions_, not the impossible claim of guaranteeing both C and A _during_ a partition. Second: CAP's "Consistency" is linearizability - the strongest consistency model. Most systems don't aim for linearizability; they provide weaker models (sequential, causal, eventual). PACELC maps more directly to real-world trade-offs: EC databases (strong consistency, higher latency): CockroachDB, Spanner, etcd; EL databases (lower latency, weaker consistency): Cassandra, DynamoDB, Couchbase. Database selection should be driven by: what is the weakest consistency model my application can tolerate? The weakest tolerable model → choose the database that provides it (often the one with lower latency). Only if the application requires strong consistency should you pay the latency cost of EC databases.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CAP: PARTITION HANDLING                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Normal: N1 ↔ N2 ↔ N3 (all connected)               │
│   Write → N1 → replicates to N2, N3 → consistent    │
│                                                      │
│ Partition: N1 | N2 ↔ N3 (N1 isolated)               │
│                                                      │
│ [CAP THEOREM ← YOU ARE HERE: partition, must choose] │
│                                                      │
│ CP CHOICE (Raft/ZooKeeper/etcd/CRDB):                │
│   Quorum = majority = 2 of 3 nodes                   │
│   N2+N3: can reach quorum → accept writes            │
│   N1: cannot reach quorum → REFUSES writes (503)     │
│   Result: N1 is unavailable; N2+N3 are consistent   │
│                                                      │
│ AP CHOICE (Cassandra CL=ONE):                        │
│   N1: accepts write → local write succeeds           │
│   N2,N3: accept writes independently                 │
│   Potential: conflicting values on N1 vs N2+N3       │
│   On partition heal: LWW or CRDT merge               │
│   Result: always available; sometimes inconsistent   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CASSANDRA READ-YOUR-OWN-WRITES WITH QUORUM:**

```
User updates profile: name = "Alice Smith"
→ Cassandra WRITE CL=QUORUM:
   N1: writes locally (MemTable)
   N2: writes locally (MemTable)
   ACK when 2 of 3 replicas confirm (QUORUM = ⌈3/2⌉ = 2)
   N3: may still be applying write asynchronously

→ User immediately reads their profile (read-your-own-writes)
→ Cassandra READ CL=QUORUM:
   Reads from N1 + N2 (quorum = 2 of 3)
   Both have "Alice Smith" (they just wrote it)
   Returns: "Alice Smith" ✓

→ Another user reads from N3 (before N3 has synced):
   CL=ONE: may return old value "Alice Jones" (stale)
   CL=QUORUM: reads N1+N2 (or N2+N3 if N3 has now synced)
               returns "Alice Smith" ✓ (quorum overlap guarantees latest)

[CAP THEOREM ← YOU ARE HERE: quorum = read-after-write consistency]
```

---

### ⚖️ Comparison Table

| Database          | CAP | PACELC | Consistency Model                             | Example Use              |
| ----------------- | --- | ------ | --------------------------------------------- | ------------------------ |
| Apache Cassandra  | AP  | PA/EL  | Eventual (CL=ONE) to Strong (CL=ALL)          | IoT, time-series         |
| DynamoDB          | AP  | PA/EL  | Eventual (default) or Strong (ConsistentRead) | General NoSQL            |
| ZooKeeper / etcd  | CP  | PC/EC  | Strong (linearizable)                         | Distributed coordination |
| CockroachDB       | CP  | PC/EC  | Serializable                                  | Global OLTP              |
| Google Spanner    | CP  | PC/EC  | External Consistency                          | Enterprise, finance      |
| MongoDB (primary) | CP  | PC/EC  | Strong (primary read)                         | Entity management        |
| HBase             | CP  | PC/EC  | Strong (HDFS-backed)                          | Hadoop ecosystem         |
| Riak              | AP  | PA/EL  | Eventual (tunable)                            | Fault-tolerant KV        |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                       |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CA systems exist and are useful"                              | In distributed systems with networks that can fail, P is mandatory. "CA" = single-node database. For all practical distributed scenarios, the choice is CP vs. AP, not C vs. A vs. P                                          |
| "AP means the database is always wrong"                        | AP means the database may return stale data during a partition, not random wrong data. After the partition heals, the data converges (eventual consistency). For many use cases (social feed, like count), this is acceptable |
| "Cassandra is always inconsistent"                             | Cassandra with CL=QUORUM + RF=3 provides effective consistency for most read-write scenarios. It's tunable. "AP" describes behavior during partitions, not all the time                                                       |
| "CAP theorem means you can't have strong consistency at scale" | CockroachDB and Google Spanner prove otherwise: CP systems can scale horizontally with strong consistency. The cost is latency, not scalability                                                                               |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale Read After Write in AP System**

**Symptom:** User updates their email address (via API → AP database). They immediately navigate to their profile page. The profile page shows the old email address. User is confused/angry.

**Root Cause:** Write went to primary replica; profile page read went to a different (lagging) replica. Replication lag = the write hasn't propagated yet. Classic "read-your-own-writes" violation in AP system.

**Diagnostic:**

```bash
# Check replication lag (Cassandra):
nodetool netstats  # look for "Outbound" queue sizes

# Check if read was from wrong replica:
# Application: log which replica was used for each read
# Enable coordinator logging in Cassandra or track via driver

# Check CRDB/primary lag for MongoDB:
db.runCommand({ "serverStatus": 1 }).repl.lag
```

**Fix:** For AP databases: use QUORUM reads (Cassandra) or ConsistentRead:true (DynamoDB) for read-after-write consistency. Alternatively: implement client-side "read-your-own-writes" using a session-consistent sticky routing (route the same user's reads to the primary for N seconds after a write).

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Systems, Eventual Consistency in NoSQL, Column Family
**Builds On This:** System Design, Distributed Transactions
**Related:** Eventual Consistency in NoSQL, PACELC, Distributed Systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CAP P=True  │ Choose: Consistency OR Availability        │
│ CP examples │ etcd, ZooKeeper, CRDB, Spanner, HBase      │
│ AP examples │ Cassandra, DynamoDB, Riak, CouchDB         │
│ PACELC      │ PA/EL or PC/EC (latency vs. consistency)   │
│ QUORUM RULE │ W + R > RF → effective strong consistency  │
│ REAL CHOICE │ "What consistency can my app tolerate?"    │
│ BANK = CP   │ No stale balance reads ever acceptable     │
│ FEED = AP   │ 1-second stale feed is fine               │
│ ONE-LINER   │ "During partition: consistent or available │
│             │  - choose based on your consistency need"  │
│ NEXT EXPLORE│ Distributed Transactions → Two-Phase Commit│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design the consistency model for a healthcare appointment booking system: patients book appointments (must not double-book), doctors view their schedule (must be current), notifications are sent when appointments are created/cancelled. For each component: choose CP or AP, justify, and specify what "failure mode" is acceptable (which is worse: missing an appointment in the schedule, or booking failing with a 503?).

**Q2.** (TYPE F - Comparison Depth) Amazon DynamoDB and ZooKeeper are both distributed databases, but one is AP and one is CP. Compare their CAP and PACELC classification, typical use cases, failure behavior during partition, and consistency guarantees. Why is DynamoDB AP appropriate for Amazon's shopping cart, and why is ZooKeeper CP appropriate for distributed leader election? Could you use DynamoDB for leader election or ZooKeeper for a shopping cart?
