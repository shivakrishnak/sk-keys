---
id: DST-070
title: Consistency Model Selection Framework
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - dst
  - advanced
  - architecture
  - bestpractice
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /distributed-systems/consistency-model-selection-framework/
---

# DST-069 - Consistency Model Selection Framework

⚡ TL;DR - Choosing a consistency model is a business decision: strong consistency prevents anomalies at the cost of latency and availability; eventual consistency maximises availability at the cost of stale reads and application-level conflict resolution.

| DST-069         | Category: Distributed Systems               | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | DST-022, DST-035, DST-036, DST-023, DST-037 |                 |
| **Used by:**    | DST-068, DST-078                            |                 |
| **Related:**    | DST-035, DST-036, DST-023, DST-078          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers default to eventual consistency because it's
"simpler" or "more scalable" without asking whether
stale reads are acceptable for their workload. Financial
services with eventual consistency find that two
concurrent withdrawals can both succeed against a stale
balance. Social apps with strong consistency find their
like buttons have 200ms latency.

**THE BREAKING POINT:**
A team builds a ride-sharing platform with eventual
consistency. Two drivers accept the same ride
simultaneously (both read the same stale "unassigned"
status). The platform double-books the customer. Fixing
this requires redesigning the entire write path for
the ride-assignment domain.

**THE INVENTION MOMENT:**
Paolo Viotti and Marko Vukolic (2016) mapped 50+
consistency models into a formal hierarchy. Eric Brewer's
CAP theorem (2000) created the foundational trade-off
framework. Werner Vogels' "Eventually Consistent" (2008)
popularized the term and its practical implications.

**EVOLUTION:**
Modern databases offer tunable consistency (Cassandra's
consistency levels, MongoDB's read/write concerns)
rather than a single model. This enables per-operation
consistency selection: strong for writes; eventual for reads.

---

### 📘 Textbook Definition

**Consistency model selection** is the process of
choosing, for each data domain, the minimum consistency
model that satisfies the correctness requirements,
weighed against latency, availability, and operational
complexity costs. **Strong consistency** (linearizability):
every read reflects the latest write; requires coordination.
**Causal consistency**: reads reflect causally related
writes. **Eventual consistency**: reads eventually
reflect all writes; no coordination required. The
selection framework maps data anomalies the application
cannot tolerate to the minimum consistency level that
prevents them.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Select consistency model by asking: what data anomalies are unacceptable? The consistency model is the minimum level that prevents those anomalies.

**One analogy:**

> Choosing a consistency model is like choosing a payment
> method. Cash (strong consistency): always accurate, but
> slow. Credit (causal consistency): usually accurate,
> faster, occasionally disputes. Cryptocurrency via text
> message (eventual consistency): very fast, but
> confirmation takes time; you might spend funds that
> are already committed elsewhere. Each is right for
> different transaction types.

**One insight:**
You don't need to choose one consistency model for
the entire system. Use strong for write paths where
anomalies are unacceptable; use eventual for read-heavy
paths where stale data is acceptable. Tunable consistency
is the practical answer.

---

### 🔩 First Principles Explanation

**SELECTION FRAMEWORK:**

```
Step 1: List the anomalies that would be bugs
  - Stale read (read data that doesn't reflect recent write)
  - Dirty read (read uncommitted data)
  - Lost update (two concurrent writes; one wins silently)
  - Write skew (two reads; both see X; both write based on X)
  - Phantom read (range query returns different rows)

Step 2: Map anomalies to minimum consistency level
  Eventual consistency prevents: nothing (all anomalies possible)
  Monotonic read consistency: prevents going backward in time
  Read-your-writes: prevents reading stale after your own write
  Causal consistency: prevents seeing effects before causes
  Sequential consistency: prevents reordering across clients
  Linearizability (strong): prevents all of the above

Step 3: Choose minimum level that prevents your anomalies
  If stale reads acceptable: eventual (Cassandra, DynamoDB)
  If lost updates unacceptable: at least causal / serializable
  If write skew unacceptable: serializable (Postgres, Spanner)
  If any anomaly unacceptable: linearizable (Spanner, etcd)

Step 4: Verify cost is acceptable
  Linearizable write: ~5-10ms cross-AZ coordination
  Eventual write: sub-ms (no coordination)
  Serializable: transaction abort rate under contention
```

**DECISION TABLE:**

```
Domain            Anomaly Budget  -> Model
-------------------------------------------------
Financial ledger  None            -> Linearizable
Inventory (buy)   None (oversell) -> Linearizable
User profile      Stale OK (1s)   -> Eventual + read-your-writes
Social feed       Stale OK (30s)  -> Eventual
DNS records       Stale OK (300s) -> Eventual
Session token     None (security) -> Strong / read-your-writes
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Different data domains have different correctness requirements; one consistency model cannot fit all.
**Accidental:** Using strong consistency everywhere (performance cost) or eventual everywhere (correctness risk).

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce system has these data domains:

1. Account balance (payment)
2. Product description (catalogue)
3. Cart contents
4. Order status

**CONSISTENCY SELECTION:**

```
1. Account balance:
   Anomaly: double-spend -> unacceptable
   -> Linearizable required
   Cost: ~10ms on every debit/credit
   DB: Postgres with serializable transactions

2. Product description:
   Anomaly: stale price (5 minutes old)
   Business: acceptable (price cache, clear on update)
   -> Eventual consistency
   Cost: near-zero coordination
   DB: Cassandra or CDN-cached

3. Cart contents:
   Anomaly: lose item added in other tab
   -> Read-your-writes minimum
   (don't need global strong; just see your own adds)
   Cost: sticky sessions or session-consistent read
   DB: Redis with session affinity

4. Order status:
   Anomaly: see old status after payment confirmed
   -> Causal consistency
   (see your payment confirmation -> see order processing)
   Cost: modest; causal tokens (not global coordination)
   DB: Cassandra with causal consistency option
```

**THE INSIGHT:**
Four domains; four different consistency models.
Using linearizable everywhere would work but be 10-50x
more expensive for domains where stale reads are fine.
Using eventual everywhere would work for 2-4 but cause
double-spend bugs in domain 1.

---

### 🧠 Mental Model / Analogy

> Consistency model selection is like choosing the
> update frequency of a stock ticker. Real-time price:
> linearizable (every trade visible immediately; required
> for trading). End-of-day price: eventual (acceptable
> for a personal finance dashboard). Both are correct
> for their use case; end-of-day for trading would cause
> real financial harm.

**Element mapping:**

- Stock price update = consistency model
- Real-time trading = domain requiring linearizability
- Personal dashboard = domain accepting eventual
- Financial harm from stale price in trading = bug from wrong consistency model

Where this analogy breaks down: stocks have one update
rate; distributed systems can tune per-operation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Consistency model = how stale can your data be? Strong
consistency = never stale. Eventual = sometimes stale
but eventually correct. Choose based on whether stale
data would cause a bug (double-charge, double-booking).

**Level 2 - How to use it (junior developer):**
For any data domain you work on: ask "what is the worst
thing that could happen if someone reads stale data?"
If the answer is "they charge the card twice" or "they
buy the same seat twice," you need strong consistency.
If the answer is "they see yesterday's like count,"
eventual is fine.

**Level 3 - How it works (mid-level engineer):**
Tunable consistency in Cassandra: `QUORUM` write +
`QUORUM` read = strong consistency (majority overlap).
`ONE` write + `ONE` read = eventual. `LOCAL_QUORUM` =
strong within one data centre; eventual across DCs.
You pay the latency cost only for operations that need
the guarantee, not all operations.

**Level 4 - Why it was designed this way (senior/staff):**
Google Spanner achieves external consistency (stronger
than linearizability: globally consistent across all
transactions) by combining TrueTime (bounded clock
uncertainty), Paxos consensus per shard, and 2-phase
commit across shards. The cost: every commit waits for
TrueTime uncertainty interval (7ms). For financial
services that need global ACID, this is the justified
cost. For social media likes, it would be wildly
over-engineered.

**Expert Thinking Cues:**

- When reviewing a service: ask "what consistency model does this use, and is it the minimum sufficient for the anomalies that matter?"
- Tunable consistency per operation is the production answer; all-or-nothing models are over-simplifications.
- "Eventual consistency" does not mean the application is wrong; it means the application handles temporary stale state correctly.

---

### ⚙️ How It Works (Mechanism)

**Cassandra tunable consistency:**

```cql
-- Strong consistency (quorum): read sees latest write
-- Requires: QUORUM write AND QUORUM read
-- QUORUM = floor(N/2)+1 nodes must respond

-- WRITE with QUORUM (strong write path)
INSERT INTO payments (id, amount, status)
VALUES (uuid(), 100.00, 'COMPLETED')
USING CONSISTENCY QUORUM;

-- READ with QUORUM (strong read path)
SELECT * FROM payments WHERE id = ?
USING CONSISTENCY QUORUM;

-- Eventual consistency (ONE): fast, may be stale
SELECT product_description FROM catalogue WHERE id = ?
USING CONSISTENCY ONE;  -- fastest; eventual

-- For cross-DC: LOCAL_QUORUM = strong within DC
INSERT INTO sessions (user_id, token) VALUES (?, ?)
USING CONSISTENCY LOCAL_QUORUM;
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Consistency model selection flow:**

```
Data domain identified:              <- YOU ARE HERE
  e.g., "user account balance"
  |
List anomalies that are bugs:
  |-> Double-spend = bug
  |-> Stale balance (1s) = bug?
  |-> Lost concurrent update = bug
  |
Select minimum consistency level:
  |-> Prevents all listed anomalies?
  |-> Yes: continue
  |-> No: go one level higher
  |
Cost assessment:
  |-> Latency impact acceptable?
  |-> Availability impact acceptable?
  |-> Operational complexity acceptable?
  |
Document in ADR:
  |-> Model chosen; anomalies it prevents;
  |-> Anomalies still possible (explicitly accepted)
  |-> Review trigger
```

---

### ⚖️ Comparison Table

| Model        | Prevents             | Cost                           | Use Case             |
| ------------ | -------------------- | ------------------------------ | -------------------- |
| Linearizable | All anomalies        | High latency; low availability | Financial, inventory |
| Serializable | Write skew, phantoms | Transaction abort rate         | Booking, allocation  |
| Causal       | Causality violations | Moderate                       | Session data, social |
| Eventual     | Nothing              | Near-zero                      | Profiles, feeds, DNS |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| "Strong consistency is always safer"             | Over-strong consistency can cause availability failures under contention                               |
| "Eventual consistency means bugs"                | Eventual consistency is correct for domains where stale reads are acceptable                           |
| "You must choose one model for the whole system" | Tunable consistency per operation is the production answer                                             |
| "QUORUM in Cassandra is always linearizable"     | QUORUM + QUORUM is strongly consistent only if there's no concurrent topology change                   |
| "Serializability = linearizability"              | Serializable prevents transaction anomalies; linearizable ensures real-time ordering across operations |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Oversell from Eventual Consistency**
**Symptom:** Item shows as in-stock; two customers buy last unit.
**Root Cause:** Inventory reads from eventual replica; both see stock > 0.
**Fix:** Write path: linearizable decrement with reservation pattern. Read path: can remain eventual for display.

**Mode 2: Stale Session Token Read**
**Symptom:** User logs out; can still use old session token from another tab.
**Root Cause:** Session invalidation written to one replica; read returns stale token from another.
**Fix:** Read-your-writes consistency for session operations; or write invalidation to all replicas synchronously.

**Mode 3: Write Skew in Concurrent Bookings**
**Symptom:** Two users book the last available slot simultaneously.
**Root Cause:** Both read "1 slot available"; both write "booked"; neither sees the other's write.
**Fix:** Serializable isolation (Postgres `SERIALIZABLE`); or optimistic locking with version check.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-022 - CAP Theorem]]
- [[DST-035 - Consistency Models]]
- [[DST-036 - Strong Consistency]]
- [[DST-023 - Eventual Consistency]]

**Builds On This (learn these next):**

- [[DST-078 - Consistency Trade-off Framing]]

**Alternatives / Comparisons:**

- Jepsen analysis (empirical consistency verification)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Framework for choosing the minimum  |
|                 consistency model per data domain   |
| PROBLEM         Wrong model: double-spend or 200ms  |
| IT SOLVES       latency on like buttons             |
| KEY INSIGHT     Select by anomaly intolerance, not  |
|                 by default or "safest"              |
| USE WHEN        Designing any data-bearing service  |
| AVOID           One model for the whole system      |
| TRADE-OFF       Latency + availability vs safety    |
| ONE-LINER       Anomaly intolerance -> min model    |
| NEXT EXPLORE    DST-078, DST-039, DST-038          |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Select consistency by the worst anomaly you cannot tolerate, not by default.
2. Tunable consistency per operation (Cassandra QUORUM vs ONE) is the production approach.
3. Four domains in one service can have four different consistency models; that's correct, not inconsistent.

**Interview one-liner:**
"Consistency model selection maps the anomalies a business cannot tolerate (double-spend, double-booking) to the minimum consistency level that prevents them; using strong consistency everywhere is over-engineered; using eventual everywhere risks correctness — tunable per-operation is the production answer."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Always specify the minimum requirement that satisfies
correctness, not the maximum that eliminates all
concerns. This applies to consistency models, locking
granularity, caching TTLs, and API security scopes.
Over-specifying costs performance; under-specifying
costs correctness.

**Where else this pattern appears:**

- **Database isolation levels** — read committed vs serializable; choose minimum needed
- **Cache TTLs** — choose maximum acceptable staleness; not "always fresh" or "never expire"
- **Security scopes** — minimum privilege principle; not "give everything" or "give nothing"

---

### 💡 The Surprising Truth

In a famous 2013 experiment, Kyle Kingsbury ("Jepsen")
tested 11 distributed databases under network partitions.
Almost every database that claimed strong consistency
actually allowed anomalies under specific failure conditions.
MongoDB 2.4 allowed dirty reads; Riak allowed lost
updates; PostgreSQL in certain configurations allowed
non-serializable anomalies under network partition.
The lesson: consistency guarantees are only as strong
as they are verified under failure. A database's
documented consistency model is a claim; Jepsen testing
is the verification.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A banking system uses Cassandra
with `CONSISTENCY ONE` for both reads and writes to
maximise performance. Describe all the consistency
anomalies that are now possible, and for each anomaly,
describe the real-world bug it would cause in a
bank account balance context.

_Hint:_ Stale read: read balance before a recent debit
reflects -> can spend same money twice. Lost update:
two concurrent ATM withdrawals at different nodes;
both see $100; both allow $80 withdrawal; $160 debited
from $100 balance. Cassandra ONE is not appropriate
for financial balances.

**Q2 (Design Trade-off):** Google Spanner provides
external consistency (linearizability + real-time ordering
across all shards globally). The cost is a 7ms wait per
commit for TrueTime uncertainty. For a global e-commerce
platform with 100ms P99 target, at what percentage of
operations would the 7ms Spanner overhead be acceptable?

_Hint:_ 7ms overhead is ~7% of a 100ms budget. For write-
heavy operations (checkout, payment): 7ms is acceptable.
For read-heavy operations (product browse): 7ms would
dominate; use eventual. Apply Spanner only to the write
path; serve reads from replicas.

**Q3 (System Interaction):** CRDTs (Conflict-free Replicated
Data Types) achieve strong eventual consistency without
coordination. What class of data types can be modelled
as CRDTs, and what class fundamentally cannot? Where
does a user's account balance fall?

_Hint:_ CRDTs work for: monotonically increasing counters,
sets with add-only, last-write-wins registers. Cannot
be CRDT: balance (debit+credit with overdraft constraint).
Balance requires coordination to prevent going negative.
A like count can be CRDT; a bank balance cannot.
