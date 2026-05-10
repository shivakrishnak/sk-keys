---
id: DST-011
title: Causal Consistency
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-008, DST-010, DST-016
used_by: DST-013, DST-067
related: DST-008, DST-009, DST-010, DST-015, DST-016
tags:
  - distributed
  - consistency
  - deep-dive
  - advanced
  - algorithm
  - mental-model
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /distributed-systems/causal-consistency/
---

# DST-011 - Causal Consistency

⚡ TL;DR - Causal consistency guarantees that operations with a cause-and-effect relationship are seen in causal order by all nodes; unrelated concurrent operations may be seen in any order, enabling stronger guarantees than eventual consistency without the cost of full linearizability.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-008, DST-010, DST-016                   |     |
| **Used by:**    | DST-013, DST-067                            |     |
| **Related:**    | DST-008, DST-009, DST-010, DST-015, DST-016 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A social network uses eventual consistency for posts and comments. User Alice posts: "Great news - I got the job!" User Bob comments: "Congratulations!" User Carol, refreshing the page, sees Bob's comment "Congratulations!" — but not Alice's original post. The comment makes no sense without its context. Carol is confused. This is causality inversion: an effect (the comment) is visible before its cause (the post). Eventual consistency permits this.

**THE BREAKING POINT:**
A collaborative document editing system uses eventual consistency. Editor A writes paragraph 1. Editor B reads paragraph 1 and writes paragraph 2 based on it. Under eventual consistency, users in another region may see paragraph 2 before paragraph 1 — the dependent text without its context. The document is incoherent. The system cannot even guarantee that "if you read it, you'll understand it" — because the read order might not match the write order.

**THE INVENTION MOMENT:**
Mustaque Ahamad and colleagues at Georgia Tech formalized causal consistency in 1994 ("Causal Memory: Definitions, Implementation, and Programming"). The core insight: applications don't need a total ordering of all operations (full linearizability), they need operations linked by happens-before (causality) to be seen in causal order. Unrelated concurrent operations can be seen in any order — and this relaxation makes the model much more scalable.

**EVOLUTION:**
1978: Lamport defines "happens-before" (DST-015). 1994: Causal memory formalized. 1995: Causal+ consistency proposed. 2011: COPS (Causal+ with convergent conflict handling) — key scalable implementation. 2013: MongoDB 3.6+ adds causal sessions. 2017: Facebook's Causal Multicast systems for distributed social graphs. 2020+: CockroachDB's causal reverse for follower reads.

---

### 📘 Textbook Definition

**Causal consistency** is a consistency model guaranteeing that operations related by the happens-before relation (causality) are seen in causal order by all processes. Specifically: if operation A happens-before operation B (A caused B, or A was observed before B was issued), then every process must see A before B. Concurrent operations (neither happened-before the other) may be observed in any order. Causal consistency is strictly weaker than linearizability and sequential consistency, but strictly stronger than eventual consistency. It is implemented using vector clocks or dependency tracking metadata propagated with each operation.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Operations that are causally related must be seen in causal order by every node; unrelated concurrent operations can be seen in any order.

> Causal consistency is like email threads. If you reply to an email, your reply only makes sense after the original. Any system that shows your reply before the email you're replying to is broken. But two entirely unrelated emails sent simultaneously can arrive in any order — that's fine. Causal consistency says: replies always come after what they're replying to; unrelated emails can arrive in any order.

**One insight:** Causal consistency is the "minimum sensible guarantee" for collaborative systems. It's cheaper than strong consistency (no global consensus needed) but prevents the most confusing failure modes of eventual consistency (reading an effect before its cause).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. If write A happens-before write B (A caused B), any process that sees B must have already seen A.
2. Happens-before is a partial order: not all pairs of operations are related by it.
3. Concurrent operations (no happens-before relationship) can be seen in any order.
4. Implementation requires tracking causal dependencies per operation (vector clock or dependency metadata).
5. No global coordinator is required — causal dependencies are tracked and propagated locally.

**DERIVED DESIGN:**
Each write carries a vector clock (or set of dependency IDs). A replica delays serving a read until all causal dependencies of the requested data have been applied locally. This "causal barrier" ensures a read never returns data whose causal context is missing.

**THE TRADE-OFFS:**
**Gain:** Prevents causality inversion (seeing effect before cause). Better UX in collaborative systems. No global coordination required — scales horizontally. Available under partition (AP in CAP).
**Cost:** Dependency metadata overhead per operation. Read latency on replicas that haven't received causal dependencies yet. Implementation complexity (vector clock management). Cross-session causality requires metadata propagation between clients.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Tracking causal dependencies requires metadata (vector clocks, dependency lists). This overhead is irreducible.
**Accidental:** Many systems implement causal consistency at the application layer via request headers (X-Correlation-ID, request chains) rather than database-level vector clocks — adding fragility and inconsistency across service boundaries.

---

### 🧪 Thought Experiment

**SETUP:** Three nodes (N1, N2, N3) store a social media feed. Alice writes `Post-A` to N1. Bob reads `Post-A` from N1, then writes `Comment-B` to N2.

**WITHOUT CAUSAL CONSISTENCY (eventual only):**
Carol reads from N3. N3 has `Comment-B` (replicated from N2) but not yet `Post-A` (replication from N1 is delayed). Carol sees: `"Congratulations!"` with no context. Causality inverted. `Comment-B` is visible before `Post-A` that caused it.

**WITH CAUSAL CONSISTENCY:**
N3 receives `Comment-B`. `Comment-B` carries a causal dependency on `Post-A`. N3 checks: "Do I have `Post-A`?" No. N3 buffers `Comment-B` until `Post-A` arrives. When `Post-A` arrives from N1, N3 applies both in order. Carol reads: `Post-A` then `Comment-B` — causal order preserved.

**THE INSIGHT:** Causal consistency requires that N3 knows what `Comment-B` depends on. This is why dependency metadata (vector clock) must travel with every write. The dependency graph is the price of causally-consistent reading.

---

### 🧠 Mental Model / Analogy

> Causal consistency is like a crime procedural: the witness testimony only makes sense after the crime is established. A court would never show a witness testifying about an event before the event has been established as fact. Causal consistency ensures the "evidence" (causal context) always precedes the "testimony" (dependent data).

**Mapping:**

- **Crime** → the causal write (Post-A)
- **Testimony** → the dependent write (Comment-B)
- **Court** → a replica serving reads
- **"Establish the crime first"** → apply causal dependencies before serving dependent data
- **Unrelated cases** → concurrent writes (can be seen in any order)

Where this analogy breaks down: a court has a global sequencer (judge). Causal consistency works without a central authority — dependencies are tracked per-operation via vector clocks.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
If you reply to someone's comment, your reply only makes sense after their comment. Causal consistency ensures every reader sees the original comment before seeing your reply — no matter which server they connect to.

**Level 2 - How to use it (junior developer):**
Causal consistency is used in collaborative apps (Google Docs, Figma), social networks (Facebook, Twitter), and messaging systems. In MongoDB, enable causal sessions: `ClientSession.startSession({causalConsistency: true})`. In CockroachDB, use follower reads with a causal reverse token. The database handles dependency tracking; your code just uses sessions correctly.

**Level 3 - How it works (mid-level engineer):**
Implementation uses vector clocks or dependency lists. Each write carries a version vector (one entry per node). A replica delays applying a write until all entries in its version vector are satisfied locally. For reads: the client sends its latest seen version; the replica ensures it has applied all causally prior writes before returning data. This is the "causal barrier." Performance depends on how many dependencies each write tracks — COPS limits this to a bounded dependency set per operation.

**Level 4 - Why it was designed this way (senior/staff):**
COPS (Causal+ Consistency with Convergent Conflict Handling, Lloyd et al. SOSP 2011) is the key scalable design. The "+" in Causal+ means: when concurrent writes conflict, a convergent merge function is applied (like LWW or application merge). This combines causal consistency (for related writes) with eventual consistency's conflict resolution (for concurrent writes). COPS achieves causal+ consistency in a single round trip for reads — O(1) coordination, not O(n). The design insight: tracking only direct causal dependencies (not transitive closure) keeps metadata bounded and practical. MongoDB's implementation (causal sessions with cluster time + operation time) is a production-grade version of this principle.

**Expert Thinking Cues:**

- "Is the data semantically dependent on other data?" → If yes, causal consistency prevents nonsense reads.
- "Does your system show comments, replies, or reactions?" → Causal consistency is the minimum correct model.
- "What's the vector clock size?" → Grows with number of nodes; COPS bounds it to direct dependencies only.
- "What happens when a causal dependency is permanently missing (node failure)?" → The dependent write can never be applied → BLOCK. Need recovery strategy.

---

### ⚙️ How It Works (Mechanism)

**Vector clock assignment:**

1. Each node maintains a local counter.
2. Each write event: `VC[node_id]++`. Write carries full VC at time of issue.
3. Each node tracks `received[node] = max_VC_received_from_node`.
4. A write W with VC_W can be applied on replica R if: for all i, `R.received[i] >= VC_W[i]`.
5. If not ready: buffer W until all dependencies are satisfied.

**Causal read:**

1. Client reads key K; server returns value V with VC_V.
2. Client remembers VC_V as its "causal context."
3. Next read from any server: client sends VC_V.
4. Server delays response until it has applied all writes up to VC_V.
5. Client always sees a causally consistent view of the world.

**MongoDB causal sessions:**

- Client session tracks `operationTime` (cluster time of last write seen).
- Next read sends `afterClusterTime: operationTime`.
- Server waits for its oplog to reach `afterClusterTime` before serving.
- Guarantees read-your-writes and causal consistency within the session.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (post → comment → causal read):**

```
Alice: Write Post-A to N1
  N1: VC = {N1:1, N2:0, N3:0}
  Post-A.vc = {N1:1, N2:0, N3:0}

Bob: Read Post-A from N1 (sees VC={N1:1...})
Bob: Write Comment-B to N2
  Comment-B.depends_on = {N1:1}  (saw Post-A)
  N2: VC = {N1:1, N2:1, N3:0}

Carol: Read from N3
  N3 receives Comment-B (depends_on={N1:1})
  N3 checks: received[N1] >= 1? → N3.received[N1]=0 → NO
  N3 BUFFERS Comment-B
  N3 receives Post-A (VC={N1:1}) → applied
  N3 received[N1]=1 >= 1 → APPLY Comment-B
  ← YOU ARE HERE: Carol reads Post-A then Comment-B
```

**FAILURE PATH:**
N1 is permanently down before Post-A reaches N3. N3 has Comment-B buffered indefinitely — it can never apply it. System stalls for Carol's reads of that key. Recovery: timeout + manual intervention, or mark N1's writes as lost and skip the dependency.

**WHAT CHANGES AT SCALE:**
With 100 nodes, vector clocks are 100-dimensional vectors. Per-operation metadata is O(n). COPS optimizes: only track DIRECT causal parents (not transitive closure). Bounded metadata regardless of cluster size. At Facebook scale: causal metadata is propagated via request headers in the application layer, not at the database level.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent writes to the same key (neither happened-before the other): both are applied via their respective convergent merge functions (LWW, OR-Set, etc.). The causal consistency guarantee says only: writes that are causally related must be ordered. Concurrent writes can be merged in any order — as long as the merge is deterministic (CRDT-like).

---

### 💻 Code Example

**BAD - Eventual consistency allowing causality inversion:**

```java
// Two separate writes, no dependency tracking
// Reader may see Comment before Post
cassandraSession.execute(
    "INSERT INTO posts(id, content) VALUES(?, ?)",
    postId, "Got the job!"
);
// Separate session, different coordinator
cassandraSession2.execute(
    "INSERT INTO comments(post_id, content) VALUES(?, ?)",
    postId, "Congratulations!"
);
// Another client may read Comment before Post
// (replication lag on posts table > comments table)
```

**GOOD - MongoDB causal session tracking:**

```java
import com.mongodb.ClientSessionOptions;
import com.mongodb.client.ClientSession;

MongoClient client = MongoClients.create(connectionString);
MongoDatabase db = client.getDatabase("social");

// Start a causally consistent session
ClientSessionOptions sessionOptions =
    ClientSessionOptions.builder()
        .causallyConsistent(true)
        .build();

try (ClientSession session = client.startSession(sessionOptions)) {
    // Write the post
    db.getCollection("posts").insertOne(
        session,
        new Document("_id", postId)
            .append("content", "Got the job!")
    );

    // Session now tracks operationTime of the post write
    BsonTimestamp operationTime = session.getOperationTime();

    // Write comment - causally after the post
    db.getCollection("comments").insertOne(
        session,
        new Document("post_id", postId)
            .append("content", "Congratulations!")
    );

    // Any subsequent read in this session or with this
    // operationTime will see both post and comment in order
    System.out.println("Causal time: " + operationTime);
}
// Any other session using operationTime as afterClusterTime
// is guaranteed to see both writes in causal order
```

**How to test / verify correctness:**

```bash
# Test causality preservation: write A, then B (dependent on A)
# from separate processes; read from a third process
# B must never be visible without A

# MongoDB: test causal session
mongosh --eval "
  const session = db.getMongo().startSession({causallyConsistent: true});
  const db2 = session.getDatabase('test');
  db2.posts.insertOne({id: 1, text: 'Post A'});
  db2.comments.insertOne({post_id: 1, text: 'Comment B'});
  // Now read from a secondary:
  db2.comments.find({post_id: 1}).readPref('secondaryPreferred').toArray();
  // Must return Comment B only after Post A is visible
"
```

---

### ⚖️ Comparison Table

| Property             | Eventual      | Causal           | Sequential       | Linearizable    |
| :------------------- | :------------ | :--------------- | :--------------- | :-------------- |
| Causality preserved  | No            | Yes              | Yes (ordered)    | Yes             |
| Global ordering      | No            | No (partial)     | Yes              | Yes (real-time) |
| Coordination needed  | None          | Per-op metadata  | Global sequencer | Consensus       |
| Cross-session causal | No            | With tokens      | N/A              | Yes             |
| Implementation       | Gossip only   | Vector clocks    | Sequencer        | Paxos/Raft      |
| Example systems      | Cassandra ONE | MongoDB sessions | Some GPU models  | etcd, Spanner   |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                           |
| :---------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Causal consistency prevents all stale reads"         | Causal consistency only prevents causality inversions. You can still read stale data, as long as the stale value doesn't causally depend on data you haven't seen yet. Stale reads of causally unrelated data are still possible.                                 |
| "Vector clocks are required for causal consistency"   | Vector clocks are one implementation. Dependency lists (COPS), operation timestamps (MongoDB cluster time), and request tracing headers can all implement causal consistency at different layers.                                                                 |
| "Causal consistency is available in all databases"    | Most NoSQL databases (Cassandra, DynamoDB) do NOT provide causal consistency by default. MongoDB added it in 3.6. Spanner provides linearizability (stronger). Genuine causal consistency outside of MongoDB sessions and research systems is rare in production. |
| "Causal consistency means total ordering of events"   | Causal consistency is a PARTIAL order — only causally related events must be ordered. Concurrent (causally unrelated) events can be seen in any order by different processes.                                                                                     |
| "My read-your-writes policy gives causal consistency" | Read-your-writes (a client sees its own writes) is a weaker guarantee than causal consistency. Causal consistency extends this to: a client sees any writes that causally preceded the writes it observed.                                                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Causal Barrier Deadlock on Node Failure**

**Symptom:** Reads for certain keys hang indefinitely. No error returned, no timeout (or very long timeout). Affects only a subset of data.
**Root Cause:** A write with a causal dependency on a permanently failed node is buffered indefinitely on all replicas. The causal barrier can never be satisfied because the dependency node is gone. No replica will apply the buffered write until the dependency is resolved.
**Diagnostic:**

```bash
# MongoDB: check for replication lag / stuck operations:
db.adminCommand({serverStatus: 1}).opLatencies
# Check replica set lag:
rs.printReplicationInfo()
rs.printSlaveReplicationInfo()
# Look for operations stuck in "applying" state
```

**Fix:**
BAD: Waiting for the failed node to recover (may never happen).
GOOD: Implement causal dependency timeout: if a dependency is unresolvable after TTL, mark the buffered write as "dependency-lost" and either apply it anyway (weakening to eventual) or drop it (accept data loss). Expose this as an observable metric.
**Prevention:** Monitor causal buffer queue depth. Alert on queue growth above threshold. Design causal dependency graphs to avoid deep chains (bounded depth = bounded failure impact).

**Failure Mode 2: Cross-Session Causality Violation**

**Symptom:** User A edits a document and shares a link. User B opens the link 200ms later and sees the document without User A's edits. Refreshing after 1 second shows the edits.
**Root Cause:** User A's session has causal consistency. But the "share link" action opened a NEW session for User B — which starts with no causal context. User B's session doesn't know it needs to have seen User A's edits.
**Diagnostic:**

```bash
# Check if the application passes the operationTime/causal token
# from User A's session to User B's link:
grep -r "operationTime\|causalToken\|afterClusterTime" frontend/ api/
# If absent: cross-session causality is broken
```

**Fix:**
BAD: Each user session starts fresh with no causal context from other sessions.
GOOD: Encode the current `operationTime` in the shared URL or in the API response. User B's client uses this as `afterClusterTime` for initial reads, establishing causal context from User A's session.
**Prevention:** Define explicit causal handoff protocol for any cross-session data sharing (share links, notifications, API webhooks).

**Failure Mode 3: Security - Information Leakage via Causal Side Channel**

**Symptom:** A user who was just banned can still determine their ban status by observing the system's behavior — specifically, whether their writes are being buffered or rejected.
**Root Cause:** Causal buffering creates observable timing differences. If a banned user's writes are causally dependent on the ban event, the system buffers responses (waiting for the ban to propagate). The delay itself is information leakage.
**Diagnostic:** This is a side-channel, not a logging issue. Requires security review of timing behaviors under access control changes.
**Fix:**
BAD: Revealing causal buffer status via error messages or timeouts.
GOOD: Return consistent, opaque responses for all writes regardless of causal buffer state. Apply the same timeout behavior for all clients.
**Prevention:** Security review of observable timing behaviors when implementing causal consistency for user-facing features.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-008 - Consistency Models (causal consistency in the broader spectrum)
- DST-010 - Eventual Consistency (the weaker model causal consistency extends)
- DST-016 - Vector Clocks (the mechanism for tracking causality)

**Builds On This (learn these next):**

- DST-013 - CRDTs (data types designed for causal + conflict-free consistency)
- DST-015 - Lamport Clock (logical time foundation for causal ordering)
- DST-067 - Consistency Level Selection (practical decision guide)

**Alternatives / Comparisons:**

- DST-009 - Strong Consistency (stronger: linearizability vs causal ordering)
- DST-010 - Eventual Consistency (weaker: no causality guarantee)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Partial ordering: causally     |
|                  | related ops seen in causal ord.|
+------------------+--------------------------------+
| PROBLEM SOLVED   | Reading effect before cause    |
|                  | (comment before post)          |
+------------------+--------------------------------+
| KEY INSIGHT      | Causally linked = ordered;     |
|                  | concurrent = any order OK      |
+------------------+--------------------------------+
| USE WHEN         | Social feeds, messaging, docs, |
|                  | any "reply/reaction" pattern   |
+------------------+--------------------------------+
| AVOID WHEN       | Simple analytics (eventual     |
|                  | fine) or finance (need linear.)|
+------------------+--------------------------------+
| TRADE-OFF        | Better UX than eventual;       |
|                  | cheaper than linearizability   |
+------------------+--------------------------------+
| ONE-LINER        | Causes always before effects;  |
|                  | unrelated ops free to reorder  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-016 Vector Clocks,         |
|                  | DST-013 CRDTs                  |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Causal consistency prevents causality inversion: an effect (comment, reply) is never visible before its cause (the original post).
2. Implementation requires causal metadata (vector clock or dependency tracking) to travel with every write.
3. Concurrent unrelated operations can still be seen in any order — causal consistency is a partial order, not total ordering.

**Interview one-liner:**
"Causal consistency guarantees that if operation A causally precedes operation B, all nodes see A before B — preventing nonsensical orderings like seeing a reply before the original message — while allowing concurrent unrelated operations to appear in any order, making it cheaper than linearizability and safer than eventual consistency for collaborative systems."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any system where data items have semantic dependencies (parent-child, cause-effect, version-revision) needs at least causal consistency for correct behavior. Applying eventual consistency to semantically-dependent data doesn't just create bugs — it creates _incoherent state_ that no amount of application logic can recover from, because the application can't know what it hasn't seen.

**Where else this pattern appears:**

- **Event sourcing (event streams):** A `OrderShipped` event must be seen after `OrderPlaced`. Event consumers must apply events in causal order. Kafka partitioning (all events for an order in the same partition) is a simple causal consistency implementation for ordered events.
- **Database foreign keys:** A row in `comments` with `post_id = 123` can only exist if `posts.id = 123` exists. This is enforced synchronously in SQL (write-time causality). Causal consistency does this asynchronously across replicas.
- **Build systems (dependency graphs):** A compiled artifact cannot be produced before its dependencies are compiled. Build tools like Maven and Bazel enforce causal ordering (dependency graph = causal graph). A "distributed build cache" that ignores causality would serve broken artifacts.

---

### 💡 The Surprising Truth

Causal consistency and linearizability are incomparable in terms of implementation cost at global scale — but not in the way most engineers assume. Linearizability requires O(1) coordination (one consensus round per operation). Causal consistency requires O(1) metadata per operation, but O(k) network delay per read (where k is the causal chain depth). At Facebook's scale (billions of posts with unlimited reply chains), deep causal chains make causal consistency reads progressively more expensive — eventually more expensive than linearizability with optimized consensus. This is why Facebook's social graph uses a hybrid: causal consistency within a datacenter (bounded chain depth), eventual consistency across datacenters (no chain depth limit). The lesson: causal consistency doesn't scale uniformly — the cost grows with causal chain depth, not cluster size.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A live-streaming comment system shows comments in real-time to 10 million concurrent viewers. Comments are posted from thousands of locations globally. Should the system use causal consistency or eventual consistency for comment display? What is the exact failure mode of using eventual consistency, and how frequently would users actually observe it?
_Hint:_ In live streaming, comments are typically independent (rarely direct replies in real-time). How does the frequency of causally-linked comments affect the practical need for causal consistency? Is there a threshold below which eventual consistency is "good enough"?

**Q2 (D - Root Cause):** A microservice architecture has 5 services: User, Order, Inventory, Payment, Notification. An order is placed → Payment is processed → Notification is sent. The notification arrives before the payment record exists. Developers say "we have eventual consistency between services." What specifically broke? Is this a causal consistency violation? What would the correct implementation look like using existing tools (Kafka, event sourcing)?
_Hint:_ Each service event has a causal dependency on the previous event. If services communicate via Kafka topics, how does Kafka's consumer ordering guarantee (within a partition) relate to causal consistency? What is the role of partition keys in ensuring causal order?

**Q3 (E - First Principles):** The COPS system achieves causal+ consistency with a single round-trip read (O(1) coordination). Traditional causal consistency implementations require a read to wait for all causal dependencies to be satisfied (potentially O(k) delays). What is the COPS insight that makes O(1) reads possible? What restriction does COPS impose on the causal dependency graph to achieve this?
_Hint:_ COPS tracks only direct (one-hop) causal dependencies, not the full transitive closure. What does a replica need to do differently to apply this rule? Does bounding dependency depth change the correctness of the causal consistency guarantee?

