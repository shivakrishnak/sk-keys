---
layout: default
title: "Consistency Models"
parent: "Distributed Systems"
nav_order: 573
permalink: /distributed-systems/consistency-models/
number: "573"
category: Distributed Systems
difficulty: ★★★
depends_on: "CAP Theorem, PACELC"
used_by: "Strong Consistency, Eventual Consistency, Database Selection"
tags: #advanced, #distributed, #consistency, #theory, #replication
---

# 573 — Consistency Models

`#advanced` `#distributed` `#consistency` `#theory` `#replication`

⚡ TL;DR — **Consistency Models** define the contract a distributed system makes about when writes become visible across nodes — from **linearisability** (instantly, globally) to **eventual consistency** (eventually, no order guarantees) — forming a spectrum that guides database selection and distributed system design.

| #573            | Category: Distributed Systems                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | CAP Theorem, PACELC                                          |                 |
| **Used by:**    | Strong Consistency, Eventual Consistency, Database Selection |                 |

---

### 📘 Textbook Definition

A **Consistency Model** is a formal contract between a distributed system and its clients that specifies which values a read operation may legally return given the history of preceding writes. Consistency models form a hierarchy from strongest to weakest: **Linearisability** (aka Strong Consistency) — every operation appears to take effect atomically at a single point in time between its invocation and response; **Sequential Consistency** — operations take effect in an order consistent with each process's program order, but globally agreed-upon; **Causal Consistency** — writes that are causally related are seen in causal order by all processes; **Monotonic Reads** — once you've seen a value, you'll never see an older version; **Read-Your-Writes** — you always see your own most recent writes; **Eventual Consistency** — given no new updates, all replicas converge to the same value. Stronger models provide better programmer guarantees but cost higher latency (more coordination required). Weaker models allow higher availability and lower latency but push complexity to applications.

---

### 🟢 Simple Definition (Easy)

Consistency Models: a promise the database makes about what you'll see when reading data after a write. The strictest promise (linearisability): "you'll see the absolute latest value, always." The weakest promise (eventual): "at some point all nodes will agree, but right now some might be behind." Most databases offer something in between. Stronger promise = slower database (more coordination). Weaker promise = faster database (less coordination needed).

---

### 🔵 Simple Definition (Elaborated)

Alice posts "Just arrived in Paris!" at 10:00 AM. Bob reads Alice's profile at 10:00:05 AM and sees the post. Bob's response: "How exciting! Is the Eiffel Tower beautiful?" — this CAUSES the response, so it's causally after Alice's post. Carol reads Alice's profile at 10:00:10 AM. Under causal consistency: Carol must see Alice's post before Bob's response (causal order preserved). Under eventual consistency: Carol might briefly see Bob's response but not Alice's post (confusing — response without original). Causal consistency prevents this nonsensical ordering.

---

### 🔩 First Principles Explanation

**Consistency models: definitions, examples, and implementation costs:**

```
CONSISTENCY MODELS FROM STRONGEST TO WEAKEST:

1. LINEARISABILITY (Strict/Strong Consistency):

   Definition: Every read returns the most recent committed write.
               All operations appear atomic at a single instant.
               Global total order respected.

   Example:
     T=1: Alice writes x=10 (committed)
     T=2: Bob reads x → must return 10 (not 5, not 7 — the LATEST value)
     T=2: Carol reads x simultaneously → must also return 10

   Implementation:
     - Synchronous replication: every write must reach all nodes before ACK
     - OR: single leader handles all reads/writes (no stale replica reads)
     - OR: quorum reads + writes (DynamoDB strong reads, Cassandra QUORUM)

   Cost: 1 RTT to quorum for every operation.
         Cross-region: 200ms RTT → every write/read takes 200ms.

   Used by: ZooKeeper, etcd, Google Spanner (global), Redis (single-node)

   Real-world test (herlihy & wing): "A linearisable bank: if two clients simultaneously
   withdraw $100 from a $100 account, one must succeed and one must fail."

2. SEQUENTIAL CONSISTENCY:

   Definition: All operations appear in SOME sequential order that is:
               (a) consistent with the real-time order within each PROCESS
               (b) the SAME order seen by all processes

   Difference from linearisability: sequential order may not match global wall-clock time.
   All nodes agree on the same order, but that order may not be real-time.

   Example:
     Process A: writes x=1, then x=2
     Process B: writes y=1, then y=2

     Legal sequential order: A:x=1, B:y=1, A:x=2, B:y=2
     Also legal: B:y=1, A:x=1, B:y=2, A:x=2
     Illegal: A:x=2, A:x=1 (violates process A's program order)

   Used by: Some message queues, Kafka (within a partition — total order per partition)

3. CAUSAL CONSISTENCY:

   Definition: Operations that are causally related must be seen in causal order.
               Concurrent (causally unrelated) operations: no ordering required.

   Causal relationship: A causes B if:
     - A happened before B on the SAME process
     - A's effects were READ by B's process before B wrote

   Example:
     Alice: POST "Just arrived in Paris!" (write A)
     Bob: reads Alice's post (reads A) → replies "Beautiful city!" (write B, caused by A)
     Carol: must see Alice's post BEFORE Bob's reply.
     Alice and Dave post independently (no causal link) → order between them undefined.

   Implementation: vector clocks track causal dependencies between operations.

   Used by: Amazon DynamoDB (some modes), Cassandra (recently added), MongoDB (sessions)

4. MONOTONIC READS:

   Definition: If process P reads a value v at time T, all subsequent reads by P return
               v or a value more recent than v.

   Problem it solves: user reads their tweet, then refreshes and the tweet disappears
                      (happened when different replicas had different lag).

   Example:
     Request 1: read from Replica A → sees tweets up to T=100
     Request 2: read from Replica B → must NOT see tweets before T=100

   Implementation: sticky sessions (always route same user to same replica).
                   Cassandra: monotonic reads within a session if consistency_level ≥ LOCAL_QUORUM.

   Used by: Sticky-session load balancing, any DB with session consistency

5. READ-YOUR-WRITES (Session Consistency):

   Definition: If process P writes value v, subsequent reads by P must return v or newer.

   Problem: user updates their profile photo → refreshes page → still sees old photo.

   Implementation:
     After write: route reads for this data to the SAME replica that handled the write.
     OR: after write to primary, wait for replica to be current before routing reads there.
     OR: read from primary for 1 second after any write by the user.

   Example in practice:
     POST /update-profile → writes to primary
     GET /profile → force to primary (not replica) for 1 second after write
     After 1 second: replica has caught up → safe to read from replica

   Used by: PostgreSQL application logic, user-session-aware routing

6. EVENTUAL CONSISTENCY (Weakest model):

   Definition: Given no new updates, all replicas will EVENTUALLY converge to the same value.
               No guarantees about ORDER or TIMING.

   Example:
     Alice writes x=10 on Replica A.
     Bob immediately reads x from Replica B → may see x=5 (before replication).
     After some time → both replicas converge to x=10.

   "Eventual" = could be milliseconds (fast network) or hours (network partition).

   Implementation: asynchronous replication. Anti-entropy repair processes.
                   Read repair: inconsistency detected on read → background sync.

   Used by: DNS, Cassandra (default), DynamoDB (default), CDN caches

CONSISTENCY HIERARCHY:

  Linearisability (strongest)
      │ ⊂ (is a subset of)
  Sequential Consistency
      │ ⊂
  Causal Consistency
      │ ⊂
  Monotonic Reads + Read-Your-Writes + Monotonic Writes
  (PRAM / Pipeline RAM Consistency — all session guarantees)
      │ ⊂
  Eventual Consistency (weakest)

  Stronger model: satisfies all properties of weaker models + more.
  Application guarantee: stronger model = simpler application logic.
  Cost: stronger model = higher coordination overhead.

IMPLEMENTATION COST COMPARISON:

  Model               | Coordination Required         | Typical Latency
  ────────────────────────────────────────────────────────────────────────
  Linearisability     | All reads/writes to quorum    | ~50-200ms (cross-region)
  Sequential          | Global consensus per operation | ~50ms (single-region)
  Causal              | Vector clock propagation       | ~10-20ms
  Monotonic Reads     | Sticky routing / session token | ~1-5ms overhead
  Read-Your-Writes    | Post-write routing for 1-2s    | ~1ms overhead
  Eventual            | None                          | ~1ms

REAL-WORLD DATABASE CHOICES:

  PostgreSQL synchronous_commit=on + replica reads:
    Strong reads (from primary): Linearisable
    Replica reads: Monotonic Reads + Read-Your-Writes (if session-tracked)

  Cassandra:
    QUORUM reads/writes: Linearisability (if RF/2 < QUORUM ≤ RF)
    ONE reads: Eventual consistency
    SERIAL: CAS (Compare-And-Set) = Linearisability for individual keys

  DynamoDB:
    Default: Eventual consistency
    ConsistentRead=true: Linearisability for reads
    Transactions (TransactWriteItems): Serialisability
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding consistency models:

- Database returns "wrong" data — engineers confused why
- Race conditions in distributed systems without understanding the guarantees
- Over-engineering: using expensive linearisability for data that only needs eventual consistency

WITH consistency models:
→ Intentional choice: select the weakest model that meets business requirements (save latency)
→ Debugging: "is this a consistency model violation or a bug?" — answer requires knowing the model
→ Application simplicity: strong models = less application-level conflict resolution code

---

### 🧠 Mental Model / Analogy

> A library's book catalog with multiple branches. Linearisability: call the central catalog before every borrowing — guaranteed latest status but takes longer. Sequential consistency: all branches agree on a single order of transactions, but this order may lag behind wall-clock time slightly. Causal consistency: if a reader wrote a review after reading the book, you'll always see the book before the review (causal order preserved). Read-Your-Writes: after you return a book, you'll always see it marked "returned" in your account. Eventual consistency: branches update each other nightly — during the day, branches may have inconsistent catalogs, but by morning they converge.

"Call central catalog before every borrowing" = linearisability (highest cost, guaranteed fresh)
"All branches agree on transaction order" = sequential consistency (agreed order, not real-time)
"Book before review (causal)" = causal consistency (cause before effect always visible)
"You see your own return" = read-your-writes (your own operations always visible)
"Updates sync nightly" = eventual consistency (converge eventually, inconsistent briefly)

---

### ⚙️ How It Works (Mechanism)

**Demonstrating consistency model violations:**

```python
# Demonstrating Read-Your-Writes violation (common in naive replica routing):

import redis
import time

# Two Redis clients, one per replica:
primary = redis.Redis(host='primary', port=6379)
replica = redis.Redis(host='replica', port=6379)

def update_profile_photo(user_id: str, new_photo_url: str):
    # Write to primary:
    primary.set(f"user:{user_id}:photo", new_photo_url)
    print(f"Wrote photo for {user_id}: {new_photo_url}")

def get_profile_photo(user_id: str, use_replica: bool = True):
    if use_replica:
        # Read from replica (may have replication lag):
        photo = replica.get(f"user:{user_id}:photo")
    else:
        # Read from primary (always fresh):
        photo = primary.get(f"user:{user_id}:photo")
    return photo.decode() if photo else None

# Without Read-Your-Writes guarantee:
update_profile_photo("alice", "https://cdn/alice_new.jpg")
# Replica has ~10ms replication lag:
time.sleep(0.005)  # 5ms — replication not yet complete
photo = get_profile_photo("alice", use_replica=True)
print(f"Alice sees: {photo}")  # May still see old photo! → Read-Your-Writes violation

# FIX: Route Alice's reads to primary for N seconds after her writes:
class SessionAwareReader:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.last_write_time = None
        self.CONSISTENCY_WINDOW = 2.0  # seconds

    def mark_write(self):
        self.last_write_time = time.time()

    def get_photo(self) -> str:
        if (self.last_write_time and
            time.time() - self.last_write_time < self.CONSISTENCY_WINDOW):
            # Within 2s of a write: read from primary (guarantee read-your-writes)
            return get_profile_photo(self.user_id, use_replica=False)
        else:
            # Safe to read from replica (write has replicated):
            return get_profile_photo(self.user_id, use_replica=True)
```

---

### 🔄 How It Connects (Mini-Map)

```
CAP Theorem (C = linearisability)
        │
        ▼
Consistency Models ◄──── (you are here)
(spectrum: linearisability → eventual)
        │
        ├── Strong Consistency (linearisability implementation)
        ├── Eventual Consistency (weakest model, highest availability)
        └── Causal Consistency (vector clocks, social media ordering)
```

---

### 💻 Code Example

**Causal consistency with vector clocks:**

```java
// Simplified vector clock for causal consistency tracking:

public class VectorClock {
    private final Map<String, Integer> clock = new ConcurrentHashMap<>();

    public void increment(String nodeId) {
        clock.merge(nodeId, 1, Integer::sum);
    }

    // VC1 "happens before" VC2 if all entries of VC1 ≤ VC2's entries
    // and at least one entry of VC1 < VC2's corresponding entry:
    public boolean happensBefore(VectorClock other) {
        Set<String> allKeys = new HashSet<>();
        allKeys.addAll(this.clock.keySet());
        allKeys.addAll(other.clock.keySet());

        boolean anySmaller = false;
        for (String key : allKeys) {
            int myVal = this.clock.getOrDefault(key, 0);
            int otherVal = other.clock.getOrDefault(key, 0);
            if (myVal > otherVal) return false;  // this entry is bigger → not before
            if (myVal < otherVal) anySmaller = true;
        }
        return anySmaller;
    }

    // Merge: take max of each entry (for receiving replicated message):
    public void merge(VectorClock other) {
        other.clock.forEach((key, val) ->
            clock.merge(key, val, Math::max));
    }
}

// Usage in distributed message store with causal ordering:
// Alice's post: VC = {alice: 1}
// Bob's reply (after reading Alice's post): VC = {alice: 1, bob: 1} (merged alice's VC + incremented bob)
// Rule: before displaying Bob's reply, verify Alice's post (VC {alice:1}) is already visible.
// If Alice's post is not yet visible on this node: buffer Bob's reply until Alice's post arrives.
// → Causal consistency: reply always displayed after original post.
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Eventual consistency means data is eventually wrong | Eventual consistency means data is eventually CORRECT — all replicas converge to the same value given no new writes. The "eventual" refers to the convergence timeline (milliseconds to seconds), not the final state. The final state is always the correct latest write                                                                                                                                                        |
| Strong consistency requires a single master         | Strong consistency (linearisability) can be achieved with a quorum protocol (majority of replicas agree) without a single master. Raft and Paxos achieve linearisability with fault-tolerant quorum consensus. Single-master is one way to implement linearisability, not the only way                                                                                                                                           |
| ACID = linearisability                              | ACID (Atomicity, Consistency, Isolation, Durability) and linearisability are different concepts. ACID Isolation levels range from Read Uncommitted (very weak) to Serialisability (strong). ACID "Consistency" means the database transitions between valid states (application invariants maintained), not linearisability. A database can be ACID but NOT linearisable (e.g., ACID with asynchronous replication across nodes) |
| Choosing eventual consistency means no anomalies    | Different consistency models permit different anomalies. Eventual consistency allows: stale reads, write conflicts (same key written concurrently on two replicas), read skew (different reads in same transaction see different versions). Applications using eventual consistency must implement conflict resolution (last-write-wins, CRDTs, application merges) to handle these anomalies                                    |

---

### 🔥 Pitfalls in Production

**Read-Your-Writes violation in user-facing feature:**

```
PROBLEM: User updates profile → immediately redirected to profile page → sees old profile

  User: PUT /api/profile {name: "Alice Smith", bio: "Software Engineer"}
  Server: writes to primary MySQL → 200 OK
  Client: redirect to GET /api/profile

  Routing: read request → load balancer → replica (replication lag: 500ms)
  Replica: still has old profile (bio: "Software Developer")
  User: sees OLD bio after just updating!
  User experience: "The update didn't save!" → hits refresh, still old → support ticket.

BAD SETUP: All reads go to replica regardless of recent writes:
  # Load balancer: write → primary, read → replica (naive read/write split)
  upstream write_backend { server primary:5432; }
  upstream read_backend { server replica:5432; }

  # After write: redirect to read_backend → stale data

FIX 1: POST-WRITE REDIRECT TO PRIMARY (simplest):
  # After successful profile update: redirect with flag
  response.headers["X-Use-Primary-Read"] = "true"

  # Middleware checks header:
  if (request.headers.get("X-Use-Primary-Read")):
      use_primary_for_this_request()

FIX 2: CACHE INVALIDATION ON WRITE:
  After write: SET user_profile:{user_id} {new_profile} EX 10  (10 second cache)
  On subsequent reads: check cache first → returns fresh data from cache.
  After 10 seconds: cache expires → reads from replica (replication has caught up).

FIX 3: MIN_VALID_REPLICA_LSN COOKIE:
  After write: server sets cookie: min_lsn=1234567
  On subsequent reads: read server checks replica's current LSN.
  If replica_lsn < min_lsn: route to primary (replica hasn't caught up).
  If replica_lsn ≥ min_lsn: safe to serve from replica.

  This is how AWS Aurora implements read-your-writes with Aurora read replicas.
```

---

### 🔗 Related Keywords

- `Strong Consistency` — linearisability: the strongest consistency model (every read = latest write)
- `Eventual Consistency` — weakest model: replicas converge eventually, no ordering guarantees
- `Causal Consistency` — causally related writes always visible in causal order
- `CAP Theorem` — C in CAP = linearisability; AP systems provide weaker consistency

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Spectrum from linearisability (strong,    │
│              │ expensive) to eventual (weak, cheap)      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Choosing consistency level per operation; │
│              │ debugging stale read anomalies            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Applying same consistency level to all    │
│              │ data (over-engineering or under-protecting)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library catalog: call HQ every time vs   │
│              │  branches sync nightly — pick the right  │
│              │  trade-off per book type."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strong Consistency → Eventual Consistency │
│              │ → Causal Consistency → Vector Clocks      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed social media platform uses eventual consistency for posts and likes. Alice posts a photo (post P). Bob likes the photo (like L, causally after P). The system must decide: can Carol see Bob's like without seeing Alice's post? Under eventual consistency: possibly yes (no causal ordering). Under causal consistency: no (L causally depends on P). What user-facing bug does this cause? How do you implement causal consistency in a post-like system? What data must be tracked per message to enforce causal ordering?

**Q2.** Compare Serialisability (from database ACID theory) with Linearisability (from distributed systems theory). Both sound like "strong consistency." What is the exact difference? Can a system be serialisable but NOT linearisable? Can it be linearisable but NOT serialisable? Give a concrete example of a scenario where the distinction matters in a distributed system (not a single-node database).
