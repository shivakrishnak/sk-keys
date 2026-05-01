---
layout: default
title: "BASE"
parent: "Distributed Systems"
nav_order: 579
permalink: /distributed-systems/base/
number: "579"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Eventual Consistency, CAP Theorem"
used_by: "NoSQL Databases, Cassandra, DynamoDB"
tags: #intermediate, #distributed, #consistency, #nosql, #availability
---

# 579 — BASE

`#intermediate` `#distributed` `#consistency` `#nosql` `#availability`

⚡ TL;DR — **BASE** (**B**asically **A**vailable, **S**oft state, **E**ventually consistent) is the design philosophy of NoSQL distributed systems that trades ACID's strong consistency for high availability and partition tolerance.

| #579            | Category: Distributed Systems        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Eventual Consistency, CAP Theorem    |                 |
| **Used by:**    | NoSQL Databases, Cassandra, DynamoDB |                 |

---

### 📘 Textbook Definition

**BASE** is an acronym coined by Eric Brewer (2000) describing the consistency model adopted by many distributed databases as an alternative to ACID: **Basically Available** — the system guarantees availability (per the CAP theorem) even during partial failures, though some data may be inconsistent; **Soft state** — the state of the system may change over time even without input, as background replication and convergence processes update replicas; **Eventually consistent** — given no new writes, all replicas will converge to the same value. BASE systems embrace the observation that strong consistency (the ACID model) requires coordination that is expensive in distributed environments, while many real-world applications can tolerate brief inconsistencies in exchange for dramatically higher availability, lower latency, and better partition tolerance. BASE is not a formal correctness condition but a design philosophy guiding the architecture of systems like Apache Cassandra, Amazon DynamoDB, and CouchDB.

---

### 🟢 Simple Definition (Easy)

BASE vs ACID: the two philosophies for distributed databases. ACID: "always correct, sometimes unavailable" (waits for all replicas to agree before answering). BASE: "always available, eventually correct" (answers immediately from local data, syncs later). ACID = banking. BASE = social media feed. Most applications can tolerate seeing a slightly stale tweet count but cannot tolerate the app being down while servers negotiate.

---

### 🔵 Simple Definition (Elaborated)

BASE properties in practice: Basically Available — even if 2 of 10 nodes are down, the remaining 8 nodes still serve requests (perhaps with stale data). Soft state — the system's state isn't static; replication is ongoing, background compaction runs, read repair updates stale replicas — the state changes even without client writes. Eventually consistent — after Alice updates her profile photo, some servers show the new photo immediately, some show the old one for a few seconds, then all converge to the new photo. The Amazon Dynamo paper (2007) formalised this trade-off and showed it was the right choice for shopping cart data where availability beats consistency.

---

### 🔩 First Principles Explanation

**BASE vs ACID: trade-offs with concrete system behavior:**

```
ACID PROPERTIES (Traditional RDBMS):

  A — Atomicity: all operations in a transaction succeed or all fail.
  C — Consistency: database transitions between valid states (invariants preserved).
  I — Isolation: concurrent transactions don't see each other's intermediate states.
  D — Durability: committed transactions survive failures.

  Cost in distributed systems:
    Atomicity across nodes: requires 2-Phase Commit (2PC).
    Isolation: requires distributed locks or SSI.
    Both: require coordination → latency proportional to number of nodes × RTT.

  Multi-region ACID example (CockroachDB):
    Write to 3 regions (US, EU, APAC):
    2PC: prepare phase (3× RTT) + commit phase (3× RTT) = 6× RTT minimum.
    US-APAC RTT: ~180ms. Total commit: ~360ms per transaction.
    For a social media platform: 360ms per post write → unacceptable.

BASE PROPERTIES (NoSQL / Distributed):

  B — Basically Available:
    System continues to function even during partial failures.
    NOT "always fully available" — some data may be unavailable during extreme failures.
    "Basic" = core read/write functionality preserved; some anomalies may occur.

    Example (Cassandra):
      RF=3, 1 node down. Writes with ONE consistency: still succeed (2 nodes available).
      Reads with ONE consistency: still succeed (may return stale data from remaining nodes).
      System remains operational. Write throughput unaffected.

  S — Soft State:
    State changes without user input due to background processes:
    - Asynchronous replication: new writes arrive at replicas minutes after primary write.
    - Anti-entropy (Cassandra nodetool repair): background full reconciliation.
    - Read repair: stale replicas updated on read queries.
    - Hinted handoff: writes to down nodes buffered and replayed on recovery.
    - Compaction: SSTables merged in background, physical state constantly changing.

    "Soft" = not frozen, always in motion toward consistency.
    Contrast with ACID: state changes only when transactions commit (hard state transitions).

  E — Eventually Consistent:
    Given no new writes: all replicas converge to the same value.
    Timing: no SLA on "eventual" in the abstract model.
    In practice: Cassandra within-DC: seconds. Cross-DC: 10s of seconds.

    Convergence mechanisms:
    1. Gossip protocol: nodes exchange data via peer-to-peer rumor spreading.
    2. Read repair: reads contact multiple replicas; stale ones are updated.
    3. Anti-entropy: nodetool repair compares Merkle trees; syncs differences.
    4. Hinted handoff: writes buffered for down nodes; replayed when node recovers.

BASE SYSTEM DESIGN IMPLICATIONS:

  Application must handle inconsistency:

  1. STALE DATA:
     Read may return data seconds behind the latest write.
     Application: display with "as of X minutes ago" timestamp.
     Example: Twitter follower count may be temporarily off by 1-2.

  2. CONCURRENT WRITE CONFLICTS:
     Two users write same key on different replicas simultaneously.
     Resolution: LWW (Last Write Wins), CRDTs, or application merge.
     Application must understand conflict resolution strategy.

  3. MISSING WRITES (Read-Before-Write):
     Application reads, modifies, writes back → Read-Modify-Write pattern.
     Under eventual consistency: two concurrent RMWs lose updates (lost update problem).
     Application: use atomic operations (CRDT increments), or switch to CAS (Cassandra LWT).

  4. CROSS-ENTITY CONSISTENCY:
     BASE: no transactions across entities (keys).
     Application: cannot assume "balance deducted ↔ payment recorded" atomically.
     Solution: compensating transactions, Saga pattern, Outbox pattern.

CHOOSING BETWEEN ACID AND BASE:

  Choose ACID when:
    - Data integrity critical (financial: double-spend, balance errors unacceptable)
    - Complex transactions spanning multiple entities (transfer A→B atomically)
    - Compliance requirements mandate consistency (financial regulations)
    - Write contention low enough for coordination cost to be acceptable

  Choose BASE when:
    - High throughput, low write latency critical (social feeds, analytics events)
    - Geographic distribution (global writes, avoid cross-region coordination)
    - Availability > consistency (service must stay up even during partial failures)
    - Data conflicts have natural resolution (LWW for user profile, CRDT for counters)

  Hybrid approaches:
    - BASE for writes, ACID-like for reads (read quorum = quasi-strong consistency)
    - ACID within a service (single database), BASE across services (eventual consistency between services)
    - CockroachDB: distributed ACID (higher latency) for when both needed

MEASURING "EVENTUAL" IN PRACTICE:

  Cassandra: typically converges within 1-10ms within a datacenter.
  DynamoDB: typically < 1 second for global table propagation.
  DNS: minutes to hours (TTL-bounded).
  Git (distributed repos): hours to days (human-initiated pull/push).

  Monitoring: "replication lag" metric tracks how far behind replicas are.
    Cassandra: metrics via nodetool netstats (total pending ranges, total streaming bytes).
    PostgreSQL async replication: pg_stat_replication.replay_lag.
    MySQL: SHOW SLAVE STATUS: Seconds_Behind_Master.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT BASE (strict ACID everywhere):

- Global distributed systems impossible (cross-continent coordination = 360ms+ per write)
- Availability suffers: any partition = system down (CP choice in CAP)
- Write throughput bottlenecked: every write waits for all replicas globally

WITH BASE:
→ Globally distributed writes at low latency (no cross-region coordination)
→ Always available: partial failures don't take the system down
→ Enables systems like Amazon, Netflix, Twitter at their scale

---

### 🧠 Mental Model / Analogy

> Wikipedia: anyone can edit any article from anywhere, and the change appears on some servers before others. Within seconds, all servers converge to the same article content. During the brief convergence period: some readers see the old article, some the new. This is "basically available" (Wikipedia never goes down for edits), "soft state" (servers are constantly syncing in the background), and "eventually consistent" (all servers converge). Contrast with a bank's balance: the bank cannot be "basically available" with "soft state" — both sides of a transfer must be atomic or money is created/destroyed.

"Anyone can edit from anywhere, change spreads" = basically available writes
"Servers constantly syncing in background" = soft state (replication always in progress)
"All servers converge to same article" = eventual consistency
"Bank balance cannot use this model" = when ACID (not BASE) is the right choice

---

### ⚙️ How It Works (Mechanism)

**Cassandra: BASE in action with Cassandra's tunable consistency:**

```python
# Cassandra demonstrates BASE with tunable consistency per operation.
# System: social media post storage. RF=3, 3 nodes in same datacenter.

from cassandra.cluster import Cluster
from cassandra.policies import ConsistencyLevel
from cassandra.query import SimpleStatement

cluster = Cluster(['node1', 'node2', 'node3'])
session = cluster.connect('social')

# BASIC AVAILABILITY: write even if 1 node is down (ONE consistency):
# System remains operational with 2 of 3 nodes.
write_stmt = SimpleStatement(
    "INSERT INTO posts (user_id, post_id, content) VALUES (%s, uuid(), %s)",
    consistency_level=ConsistencyLevel.ONE  # Write to 1 node; async to rest
)
session.execute(write_stmt, ('alice', 'Hello from Paris!'))
# Returns immediately after 1 node ACKs. Other 2 nodes receive async.
# → Basically Available: works even with 1 node down.

# SOFT STATE: replica may still have old data seconds after write:
# Read immediately after write from a different node may return old data:
read_stmt = SimpleStatement(
    "SELECT content FROM posts WHERE user_id = %s LIMIT 5",
    consistency_level=ConsistencyLevel.ONE  # May read from any single replica
)
result = session.execute(read_stmt, ('alice',))
# May return posts WITHOUT the one we just wrote if this request hits the
# replica that hasn't yet received the async replication → soft state.

# EVENTUALLY CONSISTENT: after a few ms, all replicas converge:
# Re-read with QUORUM after some time → guaranteed to see all committed writes:
read_quorum = SimpleStatement(
    "SELECT content FROM posts WHERE user_id = %s LIMIT 5",
    consistency_level=ConsistencyLevel.QUORUM  # Contact 2 of 3 replicas
)
result = session.execute(read_quorum, ('alice',))
# Quorum reads pick up latest from at least 2 nodes → convergence visible.
```

---

### 🔄 How It Connects (Mini-Map)

```
CAP Theorem (A = Availability in BASE)
        │
        ▼
BASE ◄──── (you are here)
(philosophy: Basically Available, Soft State, Eventually Consistent)
        │
        ├── Eventual Consistency (the E in BASE)
        ├── Gossip Protocol (mechanism for soft state propagation)
        └── ACID (the opposite philosophy)
```

---

### 💻 Code Example

**DynamoDB BASE behavior: soft state in Global Tables:**

```python
import boto3
import time

# DynamoDB Global Tables: multi-region BASE system.
# Write in US-East → replicates async to EU-West → eventual consistency cross-region.

us_east = boto3.client('dynamodb', region_name='us-east-1')
eu_west = boto3.client('dynamodb', region_name='eu-west-1')

# BASICALLY AVAILABLE WRITE in US-East:
us_east.put_item(
    TableName='UserProfiles',
    Item={
        'user_id': {'S': 'alice-123'},
        'bio': {'S': 'Software Engineer in Paris'},
        'updated_at': {'N': str(int(time.time() * 1000))}
    }
)
print("Write succeeded in US-East")

# SOFT STATE: Immediately reading from EU-West may return old data:
time.sleep(0.1)  # 100ms — replication may not be complete yet
response = eu_west.get_item(
    TableName='UserProfiles',
    Key={'user_id': {'S': 'alice-123'}},
    ConsistentRead=False  # Eventual consistency (default for Global Tables)
)
item = response.get('Item', {})
bio = item.get('bio', {}).get('S', 'NOT FOUND')
print(f"EU-West immediately after write: {bio}")  # May show OLD bio → soft state

# EVENTUALLY CONSISTENT: After replication completes (~1 second typical):
time.sleep(2)  # Wait for DynamoDB Global Tables replication (~200-400ms typical)
response = eu_west.get_item(
    TableName='UserProfiles',
    Key={'user_id': {'S': 'alice-123'}},
    ConsistentRead=False
)
bio = response['Item']['bio']['S']
print(f"EU-West after 2 seconds: {bio}")  # Now shows "Software Engineer in Paris" → converged
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BASE means the database is unreliable                               | BASE databases are highly reliable — they're designed for extreme availability. The "soft state" and "eventual consistency" don't mean data is lost; they describe the replication model. DynamoDB has 99.999% availability SLA. Cassandra is used for banking, healthcare, and financial systems. The trade-off is about consistency models, not reliability of data storage                                                           |
| BASE and ACID are mutually exclusive                                | Many systems blend both. PostgreSQL can use read replicas (eventually consistent reads) while transactions are fully ACID on the primary. DynamoDB supports ACID transactions (TransactWriteItems) for critical operations while offering BASE behavior for normal reads/writes. The right approach is to use ACID where required and BASE where acceptable                                                                             |
| "Basically Available" means 99% uptime                              | "Basically Available" means the system continues functioning during partial failures, serving some subset of requests — not a specific uptime percentage. During a network partition: a Cassandra cluster with a down node still serves reads and writes (with reduced redundancy). A PostgreSQL cluster may stop accepting writes during primary failure. The difference is about behavior under failure, not annual uptime percentage |
| Eventual consistency is the only consistency option in BASE systems | Most BASE systems support tunable consistency. Cassandra supports QUORUM and ALL reads (quasi-strong or strong consistency). DynamoDB supports strongly consistent reads. The BASE label describes the system's default behavior and architecture, not its only mode. Applications choose stronger consistency for critical reads at the cost of latency                                                                                |

---

### 🔥 Pitfalls in Production

**Treating BASE system as ACID for financial operation:**

```
PROBLEM: Developer uses Cassandra (BASE) for wallet balance without extra safeguards.
         Concurrent deductions from same wallet → negative balance.

  Wallet: user_id=alice, balance=100.
  Two concurrent deduction requests: -60 and -70.

  Request 1 (Node A): SELECT balance → 100. 100 ≥ 60 → OK. UPDATE balance=40.
  Request 2 (Node B): SELECT balance → 100 (soft state: B hasn't received Request 1 yet)
                      100 ≥ 70 → OK. UPDATE balance=30.

  After LWW reconciliation: balance = 30 (last writer wins by timestamp).
  Reality: 60 + 70 = 130 deducted from balance of 100 → account balance in negative.

  Root cause: Read-Modify-Write in eventually consistent system without atomic check.

BAD: Read-then-write on eventually consistent Cassandra:
  SELECT balance FROM wallets WHERE user_id='alice';  -- returns 100 (possibly stale)
  UPDATE wallets SET balance = 40 WHERE user_id='alice';  -- not atomic

FIX 1: CASSANDRA LIGHTWEIGHT TRANSACTIONS (LWT) — Compare-And-Swap:
  -- LWT uses Paxos consensus per key → linearisable for this key:
  UPDATE wallets SET balance = 40 WHERE user_id = 'alice'
      IF balance = 100;  -- Only apply if balance is still 100 (no concurrent modification)
  -- Returns applied=true/false. If false: another transaction modified balance → retry.
  -- LWT: ~4-5× slower than normal writes (Paxos rounds) → use ONLY for critical ops.

FIX 2: MOVE BALANCE TO ACID DATABASE:
  -- Cassandra: user profile, activity feed, analytics (BASE appropriate).
  -- PostgreSQL: wallet balance (ACID required).
  -- Microservices pattern: WalletService owns balance in PostgreSQL.
  -- All balance operations: through WalletService with proper transactions.
  -- Cassandra: stores non-financial data that can tolerate eventual consistency.

FIX 3: EVENT-DRIVEN WITH IDEMPOTENT OPERATIONS:
  -- Each deduction = immutable event with UUID.
  -- INSERT INTO deductions (id=uuid, user_id='alice', amount=60) IF NOT EXISTS;
  -- Balance = computed from sum of deductions (never updated in place).
  -- Concurrent inserts: safe (immutable events, no update conflicts).
  -- Duplicate detection: IF NOT EXISTS prevents duplicate events.
```

---

### 🔗 Related Keywords

- `ACID` — the opposite philosophy: strong consistency for transactional data
- `Eventual Consistency` — the E in BASE; the specific consistency model
- `CAP Theorem` — BASE systems make the AP choice in CAP
- `Cassandra` — canonical BASE system; tunable consistency

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Basically Available, Soft State, Eventually│
│              │ Consistent — trade consistency for        │
│              │ availability and low latency              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Social feeds, analytics events, user      │
│              │ profiles — brief staleness acceptable     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Financial balances; distributed locks;    │
│              │ operations requiring strict invariants    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wikipedia: always editable, converges    │
│              │  globally — bank balance is the opposite."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ACID → CAP Theorem → Eventual Consistency │
│              │ → Cassandra → CRDTs                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A ride-sharing app uses Cassandra (BASE) for driver location data (updated every 5 seconds per driver). The app also uses Cassandra for ride booking (assigning driver to passenger). Explain why BASE is appropriate for driver location data but potentially problematic for ride booking. What specific BASE anomaly could cause two passengers to be assigned the same driver simultaneously? How would you fix this with Cassandra Lightweight Transactions?

**Q2.** The Amazon Dynamo paper describes a "shopping cart" use case where BASE with vector clocks is the right choice — conflicts are resolved by merging (union of items). However, if the system used a "quantity" field (user has 3 of item X in cart), Last-Write-Wins for quantity updates could silently lose a quantity change. Design a conflict-free data model for a shopping cart with quantities that works correctly under BASE (eventual consistency + concurrent writes on different replicas).
