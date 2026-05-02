---
layout: default
title: "Causal Consistency"
parent: "Distributed Systems"
nav_order: 576
permalink: /distributed-systems/causal-consistency/
number: "0576"
category: Distributed Systems
difficulty: ★★★
depends_on: Consistency Models, Eventual Consistency, Vector Clock, Happened-Before
used_by: Social Networks, Messaging Systems, Collaborative Editing
related: Linearizability, Eventual Consistency, Vector Clock, COPS
tags:
  - causal-consistency
  - vector-clocks
  - happened-before
  - distributed-systems
  - advanced
---

# 576 — Causal Consistency

⚡ TL;DR — Causal Consistency ensures that operations with a causal relationship (where one operation happened-before another) are seen in that order by all nodes. Causally unrelated (concurrent) operations may appear in any order. It is stronger than eventual consistency (captures semantic ordering), weaker than sequential consistency (doesn't require global order for concurrent ops), and achievable without global coordination — making it practical for geo-distributed systems.

| #576 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistency Models, Eventual Consistency, Vector Clock, Happened-Before | |
| **Used by:** | Social Networks, Messaging Systems, Collaborative Editing | |
| **Related:** | Linearizability, Eventual Consistency, Vector Clock, COPS | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CAUSAL CONSISTENCY (pure eventual):**
Alice posts on Bob's wall: "Happy Birthday, Bob!" (write W1).
Bob reads and replies: "Thanks, Alice! Great to hear from you!" (write W2).
Carol loads the page in a eventually consistent system. She sees Bob's reply (W2) before Alice's original post (W1). The page looks like:
  > Bob: "Thanks, Alice! Great to hear from you!"
  > ← (no original post visible yet)
The response appears without its cause — semantically incoherent. With causal consistency, the system guarantees that W2 (caused by W1) can never be seen before W1. This ordering of causally dependent operations is the core guarantee: not all operations must be globally ordered, only causally related ones.

---

### 📘 Textbook Definition

**Causal Consistency** is a consistency model in which operations are guaranteed to be seen in causal order by all processes: if operation A causally precedes operation B (A happened-before B), then every node sees A before B. Causally unrelated (concurrent) operations may be seen in any order by different nodes.

The **happened-before** relation (→) from Lamport (1978): A → B if
- A and B are in the same process and A executed before B, OR
- A is a send event and B is the corresponding receive event, OR
- there exists C such that A → C and C → B (transitivity)

Causal consistency is typically tracked using **vector clocks** or **dependency metadata** attached to each write. A replica delays serving a write until all writes it causally depends on are visible — this is the **visibility protocol**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Causal consistency = if B was caused by A, everyone sees A before B. Unrelated operations can appear in any order.

**One analogy:**
> Email threading. If Bob replies to Alice's email, you always see Alice's email before Bob's reply — even if Alice's email arrived at your mail server later than Bob's reply. Email clients enforce causal order for threads. Messages not in the same thread (not causally related) can appear in any order. The "thread" is the causal chain.

---

### 🔩 First Principles Explanation

```
CAUSAL RELATIONSHIP DETECTION — VECTOR CLOCKS:

  System: 3 nodes [N1, N2, N3], each with vector clock [n1_ts, n2_ts, n3_ts]
  
  SCENARIO:
  N1 writes W1: x = "post" → vector clock [1, 0, 0]
  N2 receives W1 (vc = [1, 0, 0]), processes, then writes W2: y = "reply"
    W2 depends on W1 → W2's vc = [1, 1, 0] (includes W1's timestamp)
  
  N3 receives W2 [1, 1, 0] before W1 [1, 0, 0]:
    N3 sees W2 depends on N1's timestamp 1, but N3 has N1's timestamp = 0 (hasn't seen W1 yet)
    N3 HOLDS W2 in a pending queue (visibility protocol)
    N3 receives W1 [1, 0, 0] → N3 now has N1's timestamp = 1
    N3 sees W2 can now be served (dependency satisfied)
    N3 delivers W2 → x="post" is visible, then y="reply"
  
  RESULT: N3 always sees W1 (post) before W2 (reply) ✓
  
  NON-CAUSAL (CONCURRENT) OPERATIONS:
  N1 writes W3: z = "cat photo" [2, 0, 0]
  N2 writes W4: a = "news article" [1, 2, 0]
  W3 and W4 are concurrent (neither's vc dominates the other)
  N3 may see W3 before W4 OR W4 before W3 — both are valid ✓
```

---

### 🧪 Thought Experiment

**SCENARIO:** Facebook post + comment visibility on a geo-distributed system.

```
Alice writes post "I got a promotion!" at T=0.
  → W1 stored at us-west-2, vc = {alice: 1}

Bob reads the post (happens at T=50ms) — knows about Alice's post.
Bob writes "Congratulations!" comment at T=100ms.
  → W2 vc = {alice: 1, bob: 1} — causally depends on W1

Carol opens Facebook in eu-west-1, which received:
  W2 "Congratulations!" but NOT YET W1 (network lag, eu got W2 first)

WITHOUT CAUSAL CONSISTENCY:
  Carol sees: Bob: "Congratulations!" (with no visible original post)
  → Incoherent experience

WITH CAUSAL CONSISTENCY:
  eu-west-1 sees W2 depends on alice:1, but eu hasn't applied W1 yet
  eu-west-1 DELAYS displaying W2 to Carol until W1 arrives
  W1 arrives 50ms later → eu-west-1 shows:
    Alice: "I got a promotion!"
    Bob: "Congratulations!"
  → Semantically correct ✓
  
Like/comment counts, thread ordering — all causal consistency problems.
Meta's TAO system (graph cache) implements causal consistency for exactly this.
```

---

### 🧠 Mental Model / Analogy

> Causal consistency is like Wikipedia edit history enforced on reading.
> If Editor B's edit says "corrected the spelling from X to Y", then anyone reading B's edit must first see the original X that B was correcting — otherwise B's edit is meaningless.
> Wikipedia's edit system maintains causal order for edits (each edit is a delta against a specific parent version). You can't apply a child diff before applying the parent. Concurrent edits to unrelated sections can be applied in any order — no causal relationship between them.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Causal consistency preserves the "A caused B" relationship across all nodes. If you read A and then write B based on A, everyone else will see A before B. Concurrent operations (no causal link) can appear in any order.

**Level 2:** Causal consistency is achievable with low coordination overhead compared to linearizability. Instead of a global lock or quorum for every read/write, each operation carries a dependency set (vector clock). Replicas defer serving operations whose dependencies aren't yet visible. The overhead is: extra metadata per write (vector clock ~N integers for N nodes) + brief delay for out-of-order delivery. For typical replication lag patterns, this delay is negligible.

**Level 3:** COPS (Clusters of Order-Preserving Servers, Lloyd et al. 2011) is the seminal protocol achieving causal consistency at scale across data centers. Key insight: local writes are fast (applied to local datacenter), remote replication carries causal metadata, remote replicas apply in causal order. MongoDB's causally consistent sessions use a "cluster time" and "operation time" mechanism: the driver sends these tokens with reads to ensure the replica has applied all causally prior writes before serving the read. This is practical causal consistency in a production NoSQL system.

**Level 4:** The formal ordering: Linearizability ⊃ Sequential ⊃ Causal ⊃ FIFO (PRAM) ⊃ Eventual. Causal is strictly between sequential and eventual in the hierarchy. Causal consistency IS NOT composable by default: if you have causally consistent operations on key X and causally consistent operations on key Y independently, operations spanning both keys (A writes X, B reads X and writes Y, C reads Y) may not maintain causality without cross-key tracking. This is the "causal+ consistency" problem. Systems like Spanner sidestep this by using real-time for causal tracking (TrueTime commit wait). MongoDB addresses it with session tokens that span operations.

---

### ⚙️ How It Works (Mechanism)

```
META TAO — CAUSAL CONSISTENCY FOR FACEBOOK SOCIAL GRAPH:

  TAO is Facebook's distributed graph cache (billions of nodes/edges: users, posts, comments)
  Causal consistency is enforced through version IDs and cache invalidation.

  Write path:
  1. Social action (user comments on post) → write to MySQL master
  2. MySQL binlog → TAO leader cache in same datacenter (applied synchronously)
  3. TAO leader → TAO follower caches in other DCs (async replication)
       Each replication message carries: {entity_id, new_version, causal_dependencies[]}

  Read path at follower cache:
  4. Application reads entity → follower TAO checks if causal_dependencies are satisfied
  5. If not: follower waits for dependencies to propagate (or falls back to leader)
  6. Once satisfied: serve the causally consistent read

  RESULT: No user ever sees a reply before the post it replies to, globally, at Facebook scale.
  
  KEY: TAO doesn't use vector clocks by default (too expensive at Facebook scale).
  Instead uses a weaker "causal dependency" list per write — only the immediate dependencies,
  not the full transitive closure. This is a practical trade-off (almost causal — covers the
  90% case without full vector clock O(N) overhead).
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CAUSAL CONSISTENCY WITH VECTOR CLOCKS — STEP BY STEP:

  Node A         Node B         Node C
  ──────         ──────         ──────
  VC=[1,0,0]     VC=[0,0,0]     VC=[0,0,0]
  
  A: write(x=5)  [VC={A:1}]
                 ←─────────── A→B replication (carries VC={A:1})
  B: read(x)=5   [VC={A:1, B:0}]  (after receiving A's write)
  B: write(y=10, "because x=5") [VC={A:1, B:1}]
                                  ────────────────→ B→C replication (carries VC={A:1,B:1})
                              A→C replication (carries VC={A:1}) [arrives late]
  
  C receives B's write first [VC={A:1,B:1}]:
    B's write depends on A:1
    C's VC for A is 0 (hasn't received A's write yet)
    C HOLDS B's write in pending buffer ⏸

  C receives A's write [VC={A:1}]:
    C updates its VC for A to 1
    C re-checks pending writes: B's write needs A:1 ✓
    C applies A's write: x=5 visible
    C applies B's write: y=10 visible
  
  C now has x=5, y=10 in causal order ✓
  Any reader of node C sees x=5 before y=10 (the reply sees the post)
```

---

### 💻 Code Example

```java
// MongoDB Causally Consistent Session — Spring Data MongoDB
@Service
public class SocialPostService {

    private final MongoClient mongoClient;
    private final MongoCollection<Document> posts;
    private final MongoCollection<Document> comments;

    // Without causal consistency: comment may be served before the post it references
    public void replyToPost(String postId, String userId, String replyText) {

        // Causal consistency session: all operations in this session are causally ordered.
        // MongoDB tracks cluster time and operation time per session.
        // Reads in this session will not be served until the replica has caught up
        // to the point reflected by the session's cluster time.
        try (ClientSession session = mongoClient.startSession(
                ClientSessionOptions.builder()
                    .causallyConsistent(true)   // ← key flag
                    .build())) {

            // Read the post (this records the current cluster time in the session)
            Document post = posts.find(session, Filters.eq("_id", new ObjectId(postId))).first();

            if (post == null) {
                throw new PostNotFoundException(postId);
            }

            // Write the reply (causally after the read above)
            Document comment = new Document()
                .append("postId", new ObjectId(postId))
                .append("author", userId)
                .append("text", replyText)
                .append("createdAt", new Date());

            comments.insertOne(session, comment);
            // session now carries: "I've written after I've read post X"

            // If any other service reads in a session that has seen this session's token:
            // it will always see BOTH the post AND this reply, in order.
        }
    }

    // Passing causal consistency context across services (via session token)
    public List<Document> getPostWithComments(String postId, BsonDocument sessionToken) {
        // Client passes in a cluster time token (received from a previous write operation)
        // This ensures the read-your-writes guarantee across services
        try (ClientSession session = mongoClient.startSession(
                ClientSessionOptions.builder()
                    .causallyConsistent(true)
                    .build())) {

            // Advance session clock to at least the provided token
            session.advanceClusterTime(sessionToken);

            List<Document> result = new ArrayList<>();
            result.addAll(posts.find(session, Filters.eq("_id", new ObjectId(postId))).into(new ArrayList<>()));
            result.addAll(comments.find(session, Filters.eq("postId", new ObjectId(postId))).into(new ArrayList<>()));
            return result;
        }
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Causal Consistency | Eventual Consistency | Linearizability |
|---|---|---|---|
| **Ordering guarantee** | Causal chains respected | No ordering guarantee | Total real-time order |
| **Concurrent ops** | Any order | Any order | Global real-time order |
| **Coordination cost** | Low (metadata tracking) | None | High (quorum/consensus) |
| **Staleness** | For non-causal reads | Yes | Never |
| **Use case** | Social graphs, messaging, comments | Feed timelines, counters | Locks, ledger, inventory |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Causal consistency = read-your-own-writes | Read-your-own-writes is a property of causal consistency, but causal is broader: it also ensures OTHER users see causally ordered operations, not just the writer |
| Causal consistency requires vector clocks | Practical systems use lighter mechanisms: dependency lists (Facebook TAO), session tokens (MongoDB), or logical timestamps. Full vector clocks are one implementation, not the only one |
| Causal consistency is always sufficient | For financial transactions spanning multiple accounts, causal is insufficient — you need serializability to prevent phantom reads and write skew across multiple keys |

---

### 🚨 Failure Modes & Diagnosis

**Causal Violation: Comment Appears Before Post**

```
Symptom: User sees a reply in their feed before the original post.
         Or: "likes" count is non-zero before the liked entity is visible.

Diagnosis:
1. Check if the system has any causally consistent sessions enabled
2. Verify replication type: async without dependency tracking = no causal guarantees
3. Check if writes and reads are using the SAME session token (MongoDB)
   or routed to the SAME coordinator (in COPS-based systems)

Detection code (integration test):
  1. Write post (W1) → get write timestamp T1
  2. Write comment (W2, depends on W1) → get write timestamp T2
  3. From a DIFFERENT node/replica, read comment first
  4. Assert: post must be visible before comment
  5. If post is NOT visible → causal violation

Fix:
  MongoDB: enable causally consistent sessions; pass session token between services
  Cassandra: use lightweight transactions for causal chains
  Custom: attach dependency vectors to writes; replicas delay application until deps satisfied
  Alternative: use a message queue with ordering guarantees for the causal chain
```

---

### 🔗 Related Keywords

- `Vector Clock` — the primary data structure for tracking causal dependencies
- `Happened-Before` — the Lamport relation that defines causal ordering
- `Consistency Models` — causal sits between eventual and sequential in the hierarchy
- `Eventual Consistency` — the weaker model that causal consistency extends
- `Linearizability` — the stronger model that also enforces real-time order (not just causal)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ RULE          │ If A causally precedes B, ALL nodes see A    │
│               │ before B. Concurrent ops: any order OK.     │
├───────────────┼─────────────────────────────────────────────┤
│ MECHANISM     │ Vector clocks / dependency metadata /       │
│               │ session tokens track causal relationships   │
├───────────────┼─────────────────────────────────────────────┤
│ STRENGTH      │ Stronger than eventual, weaker than         │
│               │ sequential/linearizable                     │
├───────────────┼─────────────────────────────────────────────┤
│ PRACTICAL USE │ MongoDB sessions, Facebook TAO, COPS       │
│               │ protocol, messaging systems                 │
├───────────────┼─────────────────────────────────────────────┤
│ ONE-LINER     │ "Replies always follow posts they reply to" │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A distributed messaging system (think WhatsApp-scale) stores messages in an eventually consistent database. Each message has an optional "reply to message ID" field. Currently, users sometimes see a reply ("That's amazing!") before the original message ("I got the job!") appears in their message thread. The team wants to add causal consistency. However, the system handles 1 million messages/second globally, and adding full vector clocks (with N=100 nodes → 100-integer vector per message) would add significant metadata overhead. Design a causal consistency implementation that solves the reply-before-post problem with minimal metadata overhead — specifically: what is the minimum causal dependency information you need to track per message, and how does a receiving replica determine whether it's safe to display a message to the user?
