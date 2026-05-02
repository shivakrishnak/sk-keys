---
layout: default
title: "Consistency Models"
parent: "Distributed Systems"
nav_order: 573
permalink: /distributed-systems/consistency-models/
number: "0573"
category: Distributed Systems
difficulty: ★★★
depends_on: CAP Theorem, PACELC, Replication Strategies
used_by: Database Selection, API Design, Distributed Transactions
related: Linearizability, Serializability, Eventual Consistency, Causal Consistency
tags:
  - consistency-models
  - linearizability
  - eventual-consistency
  - distributed-systems
  - advanced
---

# 573 — Consistency Models

⚡ TL;DR — Consistency models define the rules for what values a read operation is allowed to return in a distributed system. They form a spectrum from strongest (strict/linearizable — reads always see the absolute latest write) to weakest (eventual — reads eventually converge but may temporarily return stale data), with causal, sequential, and monotonic consistency in between.

| #573 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP Theorem, PACELC, Replication Strategies | |
| **Used by:** | Database Selection, API Design, Distributed Transactions | |
| **Related:** | Linearizability, Serializability, Eventual Consistency, Causal Consistency | |

### 🔥 The Problem This Solves

**WORLD WITHOUT CONSISTENCY MODELS:**
You have three data center replicas. User A writes x=5 to Replica 1. User B reads x from Replica 2. What does B get? "It depends" — on propagation speed, replication mode, read routing. Without consistency models, database vendors would have no vocabulary to describe their guarantees. Developers would have no framework to choose the right database for each workload. Consistency models provide a precise, formal vocabulary: each model is a contract between the database and the application about exactly which re-orderings and staleness scenarios are permitted.

---

### 📘 Textbook Definition

A **consistency model** (or **memory consistency model**) is a specification that defines the legal observable behaviors of a distributed data store: which values a read may return, given a history of preceding writes. Weaker models allow more re-orderings and staleness (better performance, availability); stronger models enforce tighter constraints (higher coordination cost, lower latency).

The principal models in order from weakest to strongest:
1. **Eventual Consistency** — replicas converge if no new updates occur
2. **Monotonic Read** — reads never go backward in time (for a single client)
3. **Read-Your-Own-Writes** — after a write, the same client reads its own write
4. **Causal Consistency** — causally related operations are seen in causal order by all
5. **Sequential Consistency** — all operations appear in one global order honoring per-process order
6. **Linearizability** — operations appear instantaneous and in real-time order
7. **Strict Consistency** — reads see the absolute latest write (theoretical — requires single, instantaneous global clock)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A consistency model is a promise about what a read can return — from "eventually the same answer" to "always the exact latest answer."

**One analogy:**
> Imagine a collaborative Google Doc with 100 contributors.
> Eventual Consistency: you might see an old version for a few seconds after someone edits.
> Read-Your-Own-Writes: you always immediately see your own last edit.
> Causal Consistency: if Alice replies to Bob's comment, everyone sees Bob's comment before Alice's reply.
> Linearizability: everyone sees every edit instantly, in the exact moment-by-moment order they happened — as if typing on the same screen.

---

### 🔩 First Principles Explanation

**THE CORE TRADE-OFF:**

```
STRONGER CONSISTENCY MODEL:
  Requires coordination before acknowledging writes/reads
  → Coordination requires network round-trips across replicas
  → Network round-trips add latency
  → Latency reduces throughput
  → Impact grows with geography (cross-datacenter = 50-200ms RTT)
  
WEAKER CONSISTENCY MODEL:
  Allows reads/writes to proceed without global coordination
  → Low latency, high throughput
  → Replicas may diverge temporarily
  → Application must handle stale or anomalous reads

THE IRMA LEMMA (Informal):
  "You can't have both global ordering guarantees and low latency 
   in a geographically distributed system."
  → You must choose where on the spectrum to sit.
  → Different tables, even different operations, can use different models.
```

---

### 🧪 Thought Experiment

**SCENARIO:** You're building a collaborative document editor. Three users are editing simultaneously:
- Alice writes: paragraph 1 = "Hello"
- Bob writes: paragraph 2 = "World"
- Carol writes: paragraph 3 = "!"

Under EVENTUAL CONSISTENCY:
Dave opens the document. Depending on which replica he hits and propagation speed,
he might see: {Hello, World, !} or just {Hello} or {Hello, World} — all eventually converge.
→ Fine for non-critical real-time collaboration with conflict-free edits.

Under CAUSAL CONSISTENCY:
Alice responds to Bob's comment (causal dependency). All users see Bob's original
comment BEFORE Alice's response, in that order. Concurrent edits (no causal dependency)
may appear in different orders for different users.
→ Correct for comment threads, message replies — preserves semantic meaning.

Under LINEARIZABILITY:
Every user sees every edit in the exact global real-time order they happened.
→ Requires cross-datacenter coordination → high latency → battles slow internet connection.
→ Overkill for shared document editing; required for bank ledger or distributed lock.

---

### 🧠 Mental Model / Analogy

> Think of a distributed system's replicas as branches of a large bank.
> 
> Eventual Consistency: You deposit $100 at Branch A. Branch B's balance might show the old balance for a few minutes (anti-ATM of the 1990s).
> Read-Your-Own-Writes: After your deposit, YOUR account always shows the new balance when YOU query.
> Causal Consistency: If you deposit $100 then transfer $50, those two events appear in that order for everyone.
> Sequential Consistency: All customers worldwide see all transactions in one consistent global history — but the history might not match the real clock (transaction ordering is logical, not wall-clock).
> Linearizability: All transactions appear to complete atomically at the exact real-time moment they were requested — requires atomic clocks (Spanner TrueTime).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** There are six major guarantees a database can offer about reads: from "stale but eventually right" to "always the most recent value." Picking the right one depends on your use case — financial transactions need strong consistency; social media timelines can tolerate staleness.

**Level 2:** The key attributes to evaluate are: (a) does a read ever return a value older than a previously observed value? (b) can two clients reading at the same time see different values? (c) is there any wall-clock relationship between write time and read visibility? Stronger models say "no" to all three; weaker models allow some.

**Level 3:** Practical database mappings: MySQL (auto-commit) = Read-Committed (prevents dirty reads, allows non-repeatable reads). Postgres (REPEATABLE READ) = Snapshot Isolation (prevents non-repeatable reads, allows write skew anomaly). Spanner = Linearizable (prevents all anomalies). Cassandra (ONE) = Eventual. Cassandra (QUORUM) = monotonic with eventual convergence. Redis single-instance = Strong (but single node, not distributed). Redis Cluster = Eventual (async replication between nodes). ZooKeeper/etcd = Linearizable (leader-based, consensus-backed reads).

**Level 4:** The formal hierarchy: Strict ⊃ Linearizability ⊃ Sequential ⊃ Causal ⊃ FIFO (PRAM) ⊃ Eventual. Each outer model implies all inner models. Linearizability ≠ Serializability: Linearizability is about single-object, real-time ordering; Serializability is about multi-object transaction ordering. Strict Serializability = both (the strongest practical model, used by Spanner). The Herlihy & Wing 1990 paper defines linearizability; the Lamport 1979 paper defines sequential consistency. They are orthogonal on the "follows-real-time" vs "respects-process-order" axes.

---

### ⚙️ How It Works (Mechanism)

```
CONSISTENCY MODEL SPECTRUM — VISUAL:

WEAKEST                                                    STRONGEST
   │                                                            │
Eventual  Monotonic  Read-Your-  Causal  Sequential  Linearizable  Strict
           Read      Own-Writes                      (Linearizable)
   │                                                            │
  HIGH     ◄──────── PERFORMANCE (throughput, availability) ────────────►
AVAILABILITY                                            LOW LATENCY, LOW
                                                        AVAILABILITY

WHAT EACH PERMITS:
Model              | Time-travel reads | Divergent replicas | Out-of-causal-order
───────────────────┼───────────────────┼────────────────────┼───────────────────
Eventual           | YES               | YES (temporarily)  | YES
Monotonic Read     | NO                | YES                | YES
Read-Your-Writes   | Only for others   | YES                | YES
Causal             | NO (causal chain) | YES (non-causal)   | NO (causal)
Sequential         | NO                | NO                 | Possible (logical order differs from clock)
Linearizable       | NO                | NO                 | NO
Strict             | NO (wall clock)   | NO                 | NO (theoretical, impractical)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
SYSTEM DESIGN DECISION FLOWCHART:

  Q1: Can the workload tolerate brief staleness?
    NO → Go to Q2 (strong consistency required)
    YES → Choose Eventual or Causal based on Q3
  
  Q2: Is linearizability (real-time global ordering) required?
    YES → Use Spanner, etcd, ZooKeeper (PC/EC, PACELC)
    NO → Sequential or Causal may suffice
  
  Q3: Is there a causal dependency between operations?
    YES → Use Causal Consistency (Meta TAO, MongoDB causally consistent sessions)
    NO → Use Eventual Consistency (DynamoDB, Cassandra ONE)
  
  Q4: Is it multi-object transaction isolation?
    YES → You need Serializability, not just Linearizability
    → Use Postgres (SSI), Spanner (strict-ser), FoundationDB

EXAMPLES MAPPED:
  Bank balance check before debit → Linearizable
  Social media feed          → Eventual Consistency
  Comment reply ordering     → Causal Consistency
  Distributed lock           → Linearizable
  Shopping cart              → Eventual (with CRDT conflict resolution)
  Inventory during checkout  → Can upgrade to strong consistent read just for that call
```

---

### 💻 Code Example

```java
// MongoDB: per-session consistency model selection
@Service
public class ConsistencyModelDemoService {

    private final MongoClient mongoClient;

    // Eventual consistency (fastest) — for non-critical reads
    public List<Post> getRecentPosts() {
        return mongoClient.getDatabase("blog")
            .getCollection("posts", Post.class)
            .find()
            .sort(Sorts.descending("createdAt"))
            .limit(10)
            .into(new ArrayList<>());
        // MongoCollection default: reads from secondary (may be stale)
    }

    // Causal consistency — read-your-own-writes for a session
    public Post createAndVerify(Post post, ClientSession session) {
        // Establish causal consistency session
        mongoClient.getDatabase("blog")
            .getCollection("posts", Post.class)
            .insertOne(session, post);   // write

        // Read in same session: guaranteed to see the write above
        return mongoClient.getDatabase("blog")
            .getCollection("posts", Post.class)
            .find(session, Filters.eq("_id", post.getId())) // session token ensures causal read
            .first();
    }

    // Majority read/write for linearizable-equivalent guarantee
    public Post getPostLinearizable(ObjectId postId) {
        return mongoClient.getDatabase("blog")
            .withReadConcern(ReadConcern.LINEARIZABLE)  // strongest MongoDB readConcern
            .withWriteConcern(WriteConcern.MAJORITY)
            .getCollection("posts", Post.class)
            .find(Filters.eq("_id", postId))
            .first();
        // Note: linearizable readConcern reads only from primary after confirming leadership
    }
}
```

---

### ⚖️ Comparison Table

| Model | Staleness | Coordination | User Impact | Database Examples |
|---|---|---|---|---|
| **Eventual** | Yes (seconds) | None | Briefly stale reads | DynamoDB, Cassandra ONE, DNS |
| **Read-Your-Writes** | For others | Minimal (session routing) | Own writes always visible | Mongo sessions, Cassandra LOCAL_QUORUM |
| **Causal** | For non-causals | Vector clocks | Replies in order | MongoDB, COPS, Meta TAO |
| **Sequential** | No | Moderate | All see same order | Zab (ZooKeeper) |
| **Linearizable** | No | Full consensus | Real-time global order | etcd, ZooKeeper, Spanner |
| **Strict Serializable** | No | Maximum | Perfect isolation | Spanner, FoundationDB |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Consistency in ACID = Consistency in CAP | These are different. ACID consistency = application invariants preserved within a transaction. CAP/consistency model consistency = read freshness across distributed replicas |
| Linearizability and serializability are the same | Linearizability = single-object real-time ordering. Serializability = multi-object transaction ordering. Both together = strict serializability |
| Eventual consistency is always unsafe | Eventual consistency is safe for many workloads: social feeds, search indexes, product catalogs, recommendation data. It's only unsafe when immediate read-after-write accuracy is required |

---

### 🚨 Failure Modes & Diagnosis

**Stale Read After Write (Eventual Consistency Violation)**

```
Symptom:
User changes username. Next page load shows old username.

Diagnosis:
1. Request was routed to a different read replica than write route
2. Replica lag > inter-request time (user acted faster than replication)

Detection:
SELECT * FROM replication_lag_view WHERE replica_id = X;  -- check lag
-- or: check SHOW SLAVE STATUS (MySQL); \dr in psql for replication slots

Fix Options:
a) Read-after-write: route user's reads to write-path primary for 1s after the write
b) Cache update: invalidate/update cache on write completion
c) Upgrade specific reads to strong consistency (EC in PACELC):
   DynamoDB: consistentRead=true; Cassandra: LOCAL_QUORUM; Mongo: readConcern.MAJORITY
```

---

### 🔗 Related Keywords

- `CAP Theorem` — the availability vs consistency theorem that motivates this spectrum
- `Linearizability` — the strongest practical consistency model
- `Eventual Consistency` — the weakest model, used in most large-scale NoSQL systems
- `Causal Consistency` — the middle-ground that preserves semantic ordering
- `PACELC` — the framework for choosing consistency trade-offs in both partitioned and normal operation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WEAKEST (fastest)     │ Eventual Consistency                 │
│                       │ DynamoDB, Cassandra ONE, DNS         │
├───────────────────────┼─────────────────────────────────────┤
│ COMMON (practical)    │ Read-Your-Writes, Causal             │
│                       │ MongoDB sessions, Facebook TAO       │
├───────────────────────┼─────────────────────────────────────┤
│ STRONGEST (slowest)   │ Linearizable, Strict Serializable   │
│                       │ Spanner, etcd, FoundationDB          │
├───────────────────────┼─────────────────────────────────────┤
│ KEY RULE              │ ACID consistency ≠ distributed       │
│                       │ consistency — completely different   │
└───────────────────────┴─────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A microservices application has two services: a User Service (updates username, stores in Postgres) and a Notification Service (reads username to personalize push notification messages, queries a read replica). A user changes their username and then immediately triggers an action that creates a notification. The notification shows the old name. The team says "just use strong consistency everywhere." Analyze why blanket strong consistency would fail (latency, cost, architecture changes required), and design a consistency-model-aware solution that solves the stale-read problem specifically for the "user changes setting → reads setting within 1 second" window without globally upgrading all reads.
