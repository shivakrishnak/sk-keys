---
id: DST-008
title: Consistency Models
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-006, DST-014
used_by: DST-007, DST-009, DST-010, DST-011, DST-012, DST-013
related: DST-006, DST-007, DST-009, DST-010, DST-011
tags:
  - distributed
  - consistency
  - deep-dive
  - foundational
  - advanced
  - mental-model
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /distributed-systems/consistency-models/
---

# DST-008 - Consistency Models

⚡ TL;DR - Consistency models define the contract between a distributed system and its clients about which writes are visible to reads and in what order; choosing the wrong model causes either correctness bugs or unnecessary performance costs.

| Metadata        |                                                      |     |
| :-------------- | :--------------------------------------------------- | :-- |
| **Depends on:** | DST-006, DST-014                                     |     |
| **Used by:**    | DST-007, DST-009, DST-010, DST-011, DST-012, DST-013 |     |
| **Related:**    | DST-006, DST-007, DST-009, DST-010, DST-011          |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two engineers arguing: "Our database is consistent." "Define consistent." "Uh... reads see writes?" "After how long? From which node? In which order?" Without formal consistency models, "consistent" means nothing. Teams ship systems that silently return stale data, reorder operations in unexpected ways, or expose users to intermediate states. Bugs are labelled as "race conditions" and closed as "works as designed."

**THE BREAKING POINT:**
A banking app uses two microservices: `AccountService` and `LedgerService`, both reading from the same distributed database. `AccountService` writes a $500 debit. `LedgerService` immediately reads the balance — and sees the pre-debit value. It books the debit in the ledger. Now the ledger and account are inconsistent. The database "worked." No error was thrown. The system was "consistent." But which model was it actually implementing?

**THE INVENTION MOMENT:**
Leslie Lamport introduced sequential consistency in 1979 in the context of multiprocessor memory. Maurice Herlihy and Jeannette Wing defined linearizability in 1990 as a stronger property. The 1990s saw formalization of causal consistency, eventual consistency, and others. By 2000s, the "consistency vs. availability" explosion (CAP, BASE, PACELC) forced practitioners to choose among formally-defined models rather than informal "consistent" guarantees.

**EVOLUTION:**
1979: Sequential consistency (Lamport). 1990: Linearizability (Herlihy-Wing). 1994: Causal consistency (Ahamad et al.). 1997: BASE/Eventual consistency (Fox-Brewer, Amazon Dynamo). 2012: Jepsen tests begin empirically verifying claimed consistency levels. 2013: FoundationDB, CockroachDB ship linearizability as product feature. 2017: Azure Cosmos DB formalizes 5 consistency levels as customer-selectable trade-offs.

---

### 📘 Textbook Definition

**Consistency models** specify the rules governing the observable behavior of read and write operations in a distributed data store. They define which values are valid return values for a read, given the history of writes. The principal models, from strongest to weakest, are: **Linearizability** (reads see the most recent write, operations appear atomic at a single real-time moment); **Sequential consistency** (all operations appear in some sequential order consistent with program order, but not necessarily real-time); **Causal consistency** (causally related operations are seen in causal order by all processes); **Eventual consistency** (if no new updates occur, all replicas converge to the same value eventually). Stronger models are safer but costlier; weaker models are faster but require application-level correctness handling.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Consistency models answer "which write does a read see?" — the answer ranges from "always the very latest" to "maybe an old one, but they'll agree eventually."

> Consistency models are like rules for a shared whiteboard in a distributed team. Linearizability: you always see the absolute latest version, no matter who last wrote. Sequential: everyone sees the same version history, but it might lag real-time. Causal: you see things in cause-and-effect order. Eventual: everyone's board will match eventually, but right now it might differ.

**One insight:** You cannot have "the strongest consistency" for free. Every step up the consistency ladder multiplies coordination costs. The art is knowing which data needs which level — and applying the right model per-operation, not per-cluster.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. In a distributed system, multiple physical copies of data exist on different nodes.
2. Writing to one copy does not instantly update others (replication lag).
3. A client reading after a write may contact any replica, which may not yet have the latest write.
4. The system must define: which replicas are valid sources for reads, and when.
5. This definition is the consistency model — a formal contract.

**DERIVED DESIGN:**
The spectrum of consistency models arises from two fundamental constraints: (a) how quickly do all replicas converge? and (b) which replicas may serve reads?

- Linearizability: any replica that served the last write (or has been synchronized to it) may serve reads. Real-time ordering enforced.
- Eventual consistency: any replica may serve reads at any time; convergence is eventual.

**THE TRADE-OFFS:**
**Gain (strong model):** Correctness guarantees. No surprises. Simpler application code.
**Cost (strong model):** Coordination overhead: quorum reads/writes, leader election, consensus protocols. Latency increases, availability decreases under partition.
**Gain (weak model):** High throughput, low latency, geographic distribution without cross-region blocking.
**Cost (weak model):** Application must handle stale reads, conflict resolution, idempotency.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The fundamental impossibility — you cannot have instant cross-node synchronization with zero latency network. Some staleness or some coordination is always required.
**Accidental:** Many systems implement complex bespoke consistency layers (e.g., multi-version concurrency control + application-level conflict resolution) when a simpler model with the right consistency level would suffice.

---

### 🧪 Thought Experiment

**SETUP:** Alice and Bob share a distributed counter (replicated across two nodes N1 and N2). Alice increments it from N1; Bob reads it from N2 immediately after.

**WITHOUT A DEFINED CONSISTENCY MODEL:**
Sometimes Bob sees the old value (0). Sometimes he sees 1. Sometimes — if two writes race — he sees 2. No rule governs which is correct. Every behavior is "valid." Testing becomes impossible because the system makes no promise.

**WITH LINEARIZABILITY:**
If Alice's increment completed (returned success) before Bob's read started, Bob MUST see 1 (or higher). This is a guarantee. Tests can assert `assert(read >= previousWrite)` and it will always pass.

**WITH EVENTUAL CONSISTENCY:**
Bob may see 0 right after Alice's write. But if no new writes occur, both nodes will eventually converge to 1. Bob can't assert the current value, only the eventual state.

**THE INSIGHT:** Consistency models are testable contracts. Jepsen works because linearizability is falsifiable — you can build a history checker that verifies all observed operations are consistent with a single sequential history. Eventual consistency is much harder to test because convergence timing is unbounded.

---

### 🧠 Mental Model / Analogy

> Consistency models are like the return policy of a global bookshop chain. Linearizability: any branch will tell you exactly what's in stock right now, live. Sequential: every branch tells you the same story, but the story might be 5 minutes behind reality — and everyone gets the same 5-minute-old story. Causal: if you asked a specific branch to order a book, that branch will know about it. But a branch you've never visited might not. Eventual: every branch will know eventually, but right now different branches might have conflicting info.

**Mapping:**

- **Branches** → replicas/nodes
- **Book inventory** → data values
- **Return policy** → consistency contract
- **"Right now" stock check** → linearizable read
- **"5-minute lag" policy** → bounded staleness

Where this analogy breaks down: real bookshops don't need to choose consistency under network partition — they can just wait. Distributed systems must decide NOW.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When data is saved in multiple places, the rules about "which copy do you read?" are the consistency model. "Always the freshest copy" is the strictest rule. "Eventually they'll all agree" is the most relaxed. Everything else is in between.

**Level 2 - How to use it (junior developer):**
Match your consistency model to your correctness requirement. Financial balance updates → use a database with linearizability (Spanner, CockroachDB, etcd). User profile updates → sequential or causal is fine. Social media "likes" counter → eventual consistency is perfect. The key question: "Can I afford to read a stale value here, and for how long?"

**Level 3 - How it works (mid-level engineer):**
The models differ in what constraints they impose on observable histories:

- **Linearizability:** Any valid execution is equivalent to some serial execution where each operation appears at some point between its invocation and response. Real-time ordering preserved.
- **Sequential consistency:** Any valid execution is equivalent to some serial execution consistent with each process's program order. No real-time constraint.
- **Causal:** Operations related by happens-before must be seen in that order by all processes. Concurrent operations may be seen in any order.
- **Eventual:** No ordering constraint other than convergence: all replicas will hold the same value if updates cease.

**Level 4 - Why it was designed this way (senior/staff):**
The Herlihy-Wing linearizability definition is composable: if each object in a system is linearizable, the system as a whole is linearizable. This is not true for sequential consistency, which makes it harder to reason about modular systems. This composability property is why linearizability became the standard for building distributed systems out of components — each component (lock, counter, queue) can be independently verified. Causal consistency (COPS, Bolt-on Causal) requires tracking dependency metadata per-operation, which adds per-message overhead. Most "strong" consistency in production systems is actually linearizability (Spanner's "external consistency", ZooKeeper's "sequential consistency" is actually closer to linearizability in practice).

**Expert Thinking Cues:**

- "Is your read-after-write a hard requirement?" → If yes, you need at least Read-Your-Writes, which is weaker than linearizability.
- "Do two clients coordinate?" → If yes, you need linearizability (for mutually exclusive operations like distributed locks).
- "Do you have concurrent conflicting writes?" → Conflict resolution strategy determines which consistency model is sufficient.
- "What does Jepsen say about your database?" → https://jepsen.io/analyses is the empirical reference.

---

### ⚙️ How It Works (Mechanism)

**Linearizability (ZooKeeper, etcd, Spanner):**

- All reads go through a leader or quorum.
- Leader has the latest committed value.
- Read returns the value of the latest committed write as of the time the read was invoked.
- Mechanism: Paxos/Raft consensus + single-leader reads OR quorum reads with epoch checks.

**Sequential Consistency (some DSP systems):**

- All operations appear in some total order consistent with each process's order.
- Mechanism: Global sequencer assigns monotonic sequence numbers to all operations.
- Relaxed: no real-time constraint; a read before a write can appear after it in the global sequence.

**Causal Consistency (COPS, MongoDB causal sessions):**

- Operations carry vector clocks or logical timestamps.
- A replica will not serve a read until all causally-prior writes are visible.
- Mechanism: dependency tracking per operation, multi-version storage.

**Eventual Consistency (Cassandra, DynamoDB, S3):**

- Writes are propagated asynchronously.
- Reads may go to any replica, which may have old data.
- Convergence: anti-entropy, read repair, gossip protocol synchronise replicas over time.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Linearizable read in etcd):**

```
Client
  │
  ├── Write("x", 42) ──▶ Leader (Node 1)
  │                          │
  │                    Paxos: propose(42)
  │                     ├──▶ Node 2 ACK
  │                     └──▶ Node 3 ACK
  │                    commit; return OK
  │
  ├── Read("x") ──────▶ Leader (Node 1)
  │                          │
  │                    Return 42 (latest commit)
  │                          │
  ▼                     ← YOU ARE HERE
  Client sees 42 (linearizable: sees write)
```

**FAILURE PATH (Eventual consistency read during lag):**

```
Write("x", 42) → Node 1 (committed)
Read("x")      → Node 2 (replication lag: still 41)
Result: Client sees 41 (stale read - valid for EC)
Later: anti-entropy → Node 2 updated to 42
```

**WHAT CHANGES AT SCALE:**
At 10k ops/sec, linearizable reads require a leader to handle all reads (single point of throughput). Horizontal read scaling requires followers, which introduces potential staleness. Teams often shard by key space — linearizability within a shard, eventual across shards. Global strong consistency requires atomic broadcast (Paxos/Raft), which scales poorly beyond 5-7 nodes.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent writes to the same key under eventual consistency: Last-Write-Wins (LWW) — lower timestamp write is silently dropped. Under linearizability: second write sees the effect of the first (reads own writes), no silent loss. This is why financial systems require linearizability and social feeds can use eventual.

---

### 💻 Code Example

**BAD - Ignoring consistency model for inventory deduction:**

```java
// Cassandra with default ConsistencyLevel (ONE)
// Two threads race to decrement inventory
// Thread 1: reads 10, deducts 1, writes 9
// Thread 2: reads 10 (stale), deducts 1, writes 9
// Result: inventory is 9, not 8. Oversold by 1.
public boolean reserveItem(String itemId) {
    Row row = session.execute(
        "SELECT quantity FROM inventory WHERE id = ?",
        itemId
    ).one();
    int qty = row.getInt("quantity");
    if (qty > 0) {
        session.execute(
            "UPDATE inventory SET quantity = ? WHERE id = ?",
            qty - 1, itemId
        );
        return true;
    }
    return false;
}
```

**GOOD - Using Cassandra's Lightweight Transactions (linearizable):**

```java
// Uses Paxos (linearizable) for conditional update
// Only succeeds if current quantity matches expected
public boolean reserveItem(String itemId) {
    // LWT: IF quantity > 0 (serialized check-and-set)
    ResultSet rs = session.execute(
        "UPDATE inventory SET quantity = quantity - 1 " +
        "WHERE id = ? IF quantity > 0",
        itemId
    );
    // [applied] column tells if the condition was met
    return rs.one().getBool("[applied]");
}
// Each concurrent call sees the actual current state
// Two concurrent calls: one gets [applied]=true,
// one gets [applied]=false. No oversell.
```

**Eventual consistency with conflict resolution (CRDT counter):**

```java
// G-Counter CRDT: safe for eventual consistency
// Each node has its own increment slot
// Merge = max of each slot → no conflict
public class GCounter {
    private final Map<String, Long> slots = new HashMap<>();
    private final String nodeId;

    public void increment() {
        slots.merge(nodeId, 1L, Long::sum);
    }

    public long value() {
        return slots.values().stream().mapToLong(v -> v).sum();
    }

    // Safe merge: take max of each slot
    public GCounter merge(GCounter other) {
        GCounter merged = new GCounter(nodeId);
        Set<String> allNodes = new HashSet<>(slots.keySet());
        allNodes.addAll(other.slots.keySet());
        for (String node : allNodes) {
            merged.slots.put(node, Math.max(
                slots.getOrDefault(node, 0L),
                other.slots.getOrDefault(node, 0L)
            ));
        }
        return merged;
    }
}
```

**How to test / verify correctness:**

```bash
# Jepsen-style linearizability check:
# Record all invocations and responses with timestamps
# Run Knossos checker to verify linearizability:
# https://github.com/jepsen-io/knossos

# Quick check: write then immediately read from different node
# If eventual: may see old value (add retry + delay check)
# If linearizable: must always see written value
```

---

### ⚖️ Comparison Table

| Model            | Guarantee                   | Real-time Order | Cross-process | Example Systems            |
| :--------------- | :-------------------------- | :-------------- | :------------ | :------------------------- |
| Linearizability  | Reads see latest write      | Yes             | Yes           | etcd, ZooKeeper, Spanner   |
| Sequential       | All ops in consistent order | No              | Yes           | Some GPU memory models     |
| Causal           | Causes before effects       | Partial         | Per-key       | COPS, Mongo causal session |
| Read-Your-Writes | See your own writes         | No              | No            | Sticky sessions, Dynamo    |
| Monotonic Reads  | Reads don't go backward     | No              | No            | DynamoDB session tokens    |
| Eventual         | Convergence guaranteed      | No              | No            | Cassandra, DynamoDB, S3    |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                               |
| :----------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Consistency in ACID and CAP/PACELC mean the same thing"     | ACID consistency = business rules (constraints, foreign keys). CAP/PACELC consistency = linearizability (recency guarantees). Completely different concepts.                                                          |
| "Strong consistency means no bugs"                           | Strong consistency prevents only consistency-class bugs (stale reads, ordering). You can still have ACID violations, logic bugs, network errors. Linearizability is necessary but not sufficient for correctness.     |
| "Eventual consistency is unreliable"                         | Eventual consistency is a formal model with proven convergence properties. DNS has been eventually consistent for 40 years and is one of the most reliable systems on Earth. "Eventual" means convergence, not chaos. |
| "You must pick one consistency model for the whole database" | Most modern databases allow per-operation consistency levels (Cassandra CL, DynamoDB per-read, Cosmos DB per-request). You can use linearizability for inventory and eventual for analytics in the same cluster.      |
| "Causal consistency is exotic and impractical"               | MongoDB 3.6+ sessions implement causal consistency. Many microservice architectures implement it implicitly via request tracing. It's more common than practitioners realise.                                         |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Read-Your-Writes Violation**

**Symptom:** User updates their profile photo. Refreshes page. Old photo still shown. Works fine if they wait 5 seconds and refresh.
**Root Cause:** Write went to primary; read was load-balanced to replica with replication lag (~2 seconds). Application using eventual consistency for profile reads.
**Diagnostic:**

```bash
# In MySQL: check replication lag
SHOW SLAVE STATUS\G | grep Seconds_Behind_Master
# In Cassandra: check consistency level in app logs
grep "ConsistencyLevel" app.log | head -20
# In PostgreSQL: check if reads are going to hot standby
SHOW hot_standby;
```

**Fix:**
BAD: Route all reads to replicas for "performance."
GOOD: User-session reads use primary or sticky session to same replica. Profile photo read uses Read-Your-Writes consistency (route write and read from same session to same node).
**Prevention:** Apply Read-Your-Writes semantics to any user-visible state change. DynamoDB sessions provide this automatically.

**Failure Mode 2: Lost Update Under Concurrent Writes**

**Symptom:** Two users edit the same document simultaneously. One edit is silently overwritten. User reports "my changes disappeared."
**Root Cause:** Both users read the same version (v3), both compute their changes on top of v3, both write their new version. Second write overwrites first. Last-Write-Wins under eventual consistency.
**Diagnostic:**

```bash
# Check if document has version/ETag field:
curl -I https://api.example.com/docs/123
# Look for ETag or Last-Modified headers
# If missing: no optimistic concurrency control

# In DynamoDB: verify ConditionExpression is used:
grep "ConditionExpression" app/ -r
```

**Fix:**
BAD:

```
PUT /doc/123 body={new content}  # no version check
```

GOOD:

```
PUT /doc/123
If-Match: "abc123etag"  # optimistic concurrency
# Returns 412 Precondition Failed if version changed
```

**Prevention:** Every mutable shared resource needs an optimistic lock (ETag, version number, condition expression). This converts eventual consistency into Read-Modify-Write safety.

**Failure Mode 3: Security - Authorization Race Condition**

**Symptom:** A user is banned at 14:00. At 14:02, they log in successfully. The auth service read a cached/stale permission record that hasn't reflected the ban yet.
**Root Cause:** Auth service uses eventually consistent reads for permission checks. Ban propagates with ~2 minute replication lag.
**Diagnostic:**

```bash
# Check consistency level for auth service reads:
grep -r "ConsistencyLevel\|ReadConsistency" auth-service/
# Measure replication lag for permissions table:
nodetool cfstats auth.permissions | grep "Max partition size"
```

**Fix:**
BAD: `ConsistencyLevel.ONE` for auth/permission reads.
GOOD: `ConsistencyLevel.QUORUM` or `ALL` for permission reads. Or: use a strongly-consistent store (Redis with persistence, etcd) exclusively for permission data.
**Prevention:** Classify all data by security sensitivity. Auth, permissions, session invalidation: must use linearizable or strongly consistent reads. A 2-minute ban bypass window is a security incident.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-006 - CAP Theorem (consistency vs. availability under partition)
- DST-014 - Replication Strategies (how data copies are maintained)

**Builds On This (learn these next):**

- DST-009 - Strong Consistency (linearizability deep dive)
- DST-010 - Eventual Consistency (convergence deep dive)
- DST-011 - Causal Consistency (middle-ground model)
- DST-007 - PACELC (latency-consistency trade-off in normal operation)

**Alternatives / Comparisons:**

- DST-006 - CAP Theorem (the theorem that frames why models exist)
- DST-012 - Serializability (ACID consistency vs. distributed consistency)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Contract: which writes are     |
|                  | visible to reads, and when     |
+------------------+--------------------------------+
| PROBLEM SOLVED   | "Consistent" means nothing     |
|                  | without a formal model         |
+------------------+--------------------------------+
| KEY INSIGHT      | Strongest→weakest: Linear →    |
|                  | Sequential→Causal→Eventual     |
+------------------+--------------------------------+
| USE WHEN         | Choosing a database, tuning    |
|                  | per-operation consistency      |
+------------------+--------------------------------+
| AVOID WHEN       | Single-node systems (no        |
|                  | replication = no choice needed)|
+------------------+--------------------------------+
| TRADE-OFF        | Stronger = safe but slow;      |
|                  | Weaker = fast but needs care   |
+------------------+--------------------------------+
| ONE-LINER        | Linearizable=always latest;    |
|                  | Eventual=converges eventually  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-009 Strong Consistency,    |
|                  | DST-010 Eventual Consistency   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Linearizability = every read sees the most recent write; operations appear atomic in real time.
2. Eventual consistency = all replicas converge if writes stop; reads may be stale in the interim.
3. "Consistency" in ACID ≠ "Consistency" in CAP/distributed systems — they're completely different concepts.

**Interview one-liner:**
"Consistency models define what a distributed system promises about which writes are visible to reads — the spectrum from linearizability (reads always see the latest write, real-time atomicity) to eventual consistency (replicas converge eventually, stale reads are valid) represents a direct trade-off between correctness guarantees and coordination cost."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every shared mutable state across processes needs an explicit consistency contract. The contract should be chosen based on the worst-case business impact of a stale read, not based on the default behavior of the database you're already using. Defaulting to eventual consistency for all data because "Cassandra is eventual" is as wrong as defaulting to linearizability for all data because "ZooKeeper is consistent."

**Where else this pattern appears:**

- **CPU memory models (x86 vs. ARM):** x86 offers Total Store Order (close to sequential consistency); ARM offers a weaker model requiring explicit memory barriers. Kernel and JVM developers must understand the CPU's consistency model to write correct lock-free code.
- **Microservice event sourcing:** Events published to Kafka are eventually consistent across consumers. A consumer that reads from the Kafka topic gets eventual consistency semantics. If two services must agree on state NOW, you need synchronous consistency (2PC, Saga with compensation).
- **DNS propagation:** DNS is the canonical eventually consistent system. A domain change propagates globally over TTL windows (minutes to hours). No synchronous global consistency. World's most successful eventual consistency deployment.

---

### 💡 The Surprising Truth

Linearizability is strictly stronger than serializability — but they address different things. Serializability (the "S" in ACID) guarantees transactions execute as if they ran serially, with no interleaving. Linearizability guarantees each operation appears atomic at a single real-time moment. You can have serializable transactions that violate linearizability (if the serial order doesn't match real-time order) — this is called "non-linearizable serializability" and is valid ACID. You can also have linearizable individual operations inside non-serializable transactions. The model that combines both — Strict Serializability (or "strong serializability") — is what systems like Google Spanner implement. Most engineers use "strongly consistent" when they mean "strictly serializable" without knowing the distinction, which leads to subtle bugs when moving between database systems.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A multiplayer game needs a shared leaderboard. Millions of players update their scores concurrently. Two requirements: (1) A player must always see their own score update reflected immediately. (2) The global ranking may lag by up to 30 seconds. Which consistency model satisfies both requirements? Can a single database provide both, or do you need two systems?
_Hint:_ The first requirement is Read-Your-Writes consistency. The second is bounded staleness. Are these independent models? Can you implement Read-Your-Writes on top of eventual consistency without changing the underlying model?

**Q2 (D - Root Cause):** A microservice calls the User Service to get a user's permissions, then immediately calls the Payment Service. The Payment Service also calls User Service internally to verify the same permissions. Both calls happen within 50ms. The User Service is eventually consistent. Under what conditions can the first call and the second call see different permission states? What is the correct architecture to prevent this?
_Hint:_ This is a monotonic read violation — a process sees a newer value then an older value for the same key across two calls. Does routing both calls to the same replica solve this? What if User Service is stateless (no sticky sessions)?

**Q3 (E - First Principles):** Sequential consistency and linearizability both guarantee a consistent serial ordering of all operations. The only difference is linearizability adds real-time constraints. Why does the real-time constraint make linearizability so much harder to implement at scale, and why can't you simply add a timestamp to sequential consistency to make it linearizable?
_Hint:_ In a distributed system, there is no global clock — only logical clocks and physical clocks with bounded skew. Lamport timestamps give causal ordering but not real-time ordering. What would it take to turn a Lamport timestamp into a linearizability proof?
