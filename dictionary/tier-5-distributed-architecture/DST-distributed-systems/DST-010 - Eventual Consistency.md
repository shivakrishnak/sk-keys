---
id: DST-010
title: Eventual Consistency
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-006, DST-008, DST-014
used_by: DST-011, DST-013, DST-067
related: DST-006, DST-007, DST-008, DST-009, DST-011
tags:
  - distributed
  - consistency
  - foundational
  - intermediate
  - tradeoff
  - production
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /distributed-systems/eventual-consistency/
---

# DST-010 - Eventual Consistency

⚡ TL;DR - Eventual consistency guarantees all replicas will converge to the same value if writes stop; reads may see stale data in the interim, enabling high throughput and geographic distribution at the cost of application-level conflict resolution.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-006, DST-008, DST-014                   |     |
| **Used by:**    | DST-011, DST-013, DST-067                   |     |
| **Related:**    | DST-006, DST-007, DST-008, DST-009, DST-011 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A global e-commerce site wants to run a "like" counter on every product page. 10 million concurrent users across 6 continents. If every "like" click requires a globally synchronised write (strong consistency), every user on the US-East coast must wait for the write to replicate to EU-West and APAC before getting a response. At 180ms RTT: 180ms added to every click. Throughput collapses. The "like" button becomes slow. Users stop clicking. The feature is abandoned.

**THE BREAKING POINT:**
Amazon's shopping cart service processes millions of cart additions per second. Requiring strong consistency on cart additions (wait for all replicas to confirm) means: any network hiccup between US datacenters causes cart additions to fail or hang. During the 2003 US East Coast blackout, strongly consistent systems in affected datacenters went unavailable. Amazon's engineers realised: for shopping carts, "slightly stale" or even "temporarily conflicting" is infinitely better than "unavailable." The cart can be merged later.

**THE INVENTION MOMENT:**
Werner Vogels (Amazon CTO) popularised the term in his 2007 ACM Queue article "Eventually Consistent." The formal concept traces to the Dynamo paper (2007) — Amazon's highly available key-value store. The key insight: for many real-world use cases, the business requirement is convergence over time, not instantaneous global agreement. DNS had been "eventually consistent" for 20 years before anyone named the model.

**EVOLUTION:**
1983: DNS designed with TTL-based propagation (eventual consistency in practice). 2007: Amazon Dynamo paper + Vogels "Eventually Consistent" article. 2012: CRDTs (Conflict-free Replicated Data Types) provide eventual consistency with automatic conflict resolution. 2013-2020: Cassandra, DynamoDB, CouchDB, Riak mature as production eventually consistent systems. 2020+: Eventual consistency + CRDTs underpin real-time collaborative editing (Google Docs, Figma, Notion).

---

### 📘 Textbook Definition

**Eventual consistency** is a consistency model guaranteeing that, if no new updates are made to a given data item, all replicas will eventually converge to the same value. In the interim, different replicas may serve different values for the same key. The model makes no guarantee about _when_ convergence occurs or _which_ value concurrent writes will converge to (unless an explicit conflict resolution policy is defined). It is the weakest consistency model that still provides a convergence guarantee. Systems using eventual consistency trade consistency recency for high availability, low write latency, and geographic distribution — the BASE (Basically Available, Soft-state, Eventually consistent) alternative to ACID.

---

### ⏱️ Understand It in 30 Seconds

**One line:** If you stop updating a value, all servers will eventually agree on what it is — but right now, different servers might show different values.

> Eventual consistency is like a rumor spreading through a crowd. If Alice tells Bob "the concert is cancelled," Bob tells Carol, and Carol tells Dave — eventually everyone knows. But right after Alice tells Bob, Carol and Dave still think the concert is on. The message will reach everyone eventually, but there's a window where the crowd is inconsistent.

**One insight:** "Eventual" is not a bug — it's a design choice. DNS has been eventually consistent for 40 years. It is one of the most reliable systems on Earth. Eventual consistency is suitable for data where the business cost of brief staleness is lower than the business cost of unavailability.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Write propagation between replicas is asynchronous — writes complete locally, replicas update in the background.
2. A read may contact any replica, which may not yet have received the latest write.
3. If writes cease, background synchronization will cause all replicas to converge.
4. Concurrent writes to the same key on different replicas require a merge/conflict resolution strategy.
5. The system makes no promise about the staleness window — it's bounded by replication throughput and network conditions.

**DERIVED DESIGN:**
Eventual consistency enables: (a) writes to succeed even if some replicas are unreachable; (b) reads from geographically local replicas without cross-region blocking; (c) full availability during partition (AP in CAP). These properties require: explicit conflict resolution (LWW, CRDTs, multi-value register), anti-entropy protocols (read repair, Merkle-tree-based sync), and gossip protocols for replica health.

**THE TRADE-OFFS:**
**Gain:** Near-zero write latency (local commit + async replication). Full availability during network partitions. Horizontal read scaling (any replica can serve reads). Geographic distribution without cross-region write blocking.
**Cost:** Application must handle stale reads. Concurrent writes require conflict resolution. No distributed lock or mutual exclusion possible. Read-your-writes not guaranteed without additional mechanisms.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Asynchronous propagation lag is irreducible — physics constrains cross-datacenter replication. Some staleness window always exists.
**Accidental:** Many systems add application-level "eventual consistency workarounds" (retry loops, stale flags, cache invalidation hacks) that could be replaced by proper CRDT data types or read-your-writes session tokens.

---

### 🧪 Thought Experiment

**SETUP:** A social network's "followers count" is stored in an eventually consistent database. User Alice has 1,000 followers. 500 new users follow her in a 10-second burst, writes distributed across 3 replicas.

**WITHOUT EVENTUAL CONSISTENCY (strong consistency required):**
All 500 follows must serialize through a Raft leader. Each follow: network round-trip to leader, Raft replication to 2 followers, commit. At 5ms per round-trip: 500 × 5ms = 2.5 seconds for 500 follows to process. Under viral load (100k follows in 10s): 100,000 × 5ms / (parallelism factor) = severe backpressure. The feature degrades or goes unavailable.

**WITH EVENTUAL CONSISTENCY:**
All 500 follows write to their local replica immediately. Returns `200 OK` in 1ms each. Background replication propagates all writes to other replicas within 500ms. During that 500ms, Alice sees "1,200 followers" on replica 1 and "1,050 followers" on replica 2 — depending on which replica her profile page hits. After 500ms: all replicas converge to 1,500.

**THE INSIGHT:** For a follower count, staleness of 500ms is imperceptible and harmless. The 1,499x throughput improvement is not. The right model depends on what the data _means_ to the business, not on a blanket "consistent or not" policy.

---

### 🧠 Mental Model / Analogy

> Eventual consistency is like synchronising a shared playlist between your phone and your laptop over WiFi. When you add a song on your phone offline, it syncs when you reconnect. In the window between adding and syncing, your laptop's playlist is "wrong." But given enough time, both devices will agree. If you and a friend both add songs to the same shared playlist while offline, the merge happens when you reconnect — either by keeping both (additive merge, like a G-Counter CRDT) or by applying some merge rule.

**Mapping:**

- **Phone/laptop** → replicas
- **Song addition** → write operation
- **WiFi sync** → replication / anti-entropy
- **Offline window** → replication lag (staleness window)
- **Both adding the same song** → concurrent conflicting write
- **Merge rule** → conflict resolution policy (LWW, CRDT, manual)

Where this analogy breaks down: playlist sync can involve a human to resolve conflicts. Distributed systems need deterministic, automatic merge rules — manual resolution doesn't scale to millions of ops/sec.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Eventual consistency means: if you update something, other people might see the old version for a little while. But after some time passes, everyone will see the new version. It's fine for things like "how many likes does this photo have" but not fine for "what's my bank balance."

**Level 2 - How to use it (junior developer):**
Use eventually consistent systems for: social features (likes, follows, views), analytics counters, product catalog browsing, DNS, content distribution. Avoid for: financial transactions, distributed locks, inventory during peak sales, anything requiring read-your-writes. In practice: DynamoDB default reads, Cassandra `ONE` consistency level, S3 eventual consistency (now upgraded to strong), CouchDB, Couchbase.

**Level 3 - How it works (mid-level engineer):**
Eventual consistency is implemented through: (1) **Anti-entropy**: Background process compares replica state using Merkle trees, syncs differences. (2) **Read repair**: When a read goes to multiple replicas and they disagree, the freshest value is returned and the stale replicas are updated. (3) **Hinted handoff**: If a write's target replica is unavailable, the write is stored on a coordinator as a "hint" and replayed when the replica recovers. (4) **Gossip protocol**: Nodes periodically exchange state information, propagating writes that haven't yet reached all nodes.

**Level 4 - Why it was designed this way (senior/staff):**
The Amazon Dynamo paper (2007) made the key architectural decision: always-writeable is more valuable than always-consistent for e-commerce. This led to the "leaderless replication" design (no single master, any node can accept writes) which maximises availability but requires client-side conflict resolution. The breakthrough insight in modern systems: CRDTs (Conflict-free Replicated Data Types, Shapiro et al. 2011) give mathematical proof that certain data types (G-Counter, OR-Set, LWW-Register) can be merged automatically without human conflict resolution. This made "eventually consistent + correct" achievable without application-level merge logic.

**Expert Thinking Cues:**

- "What's your conflict resolution strategy?" → If you don't have one, you're silently losing writes.
- "What's your replication lag P95?" → This is your "eventual" staleness bound in practice.
- "Can this operation afford to see the old value?" → The answer determines your consistency requirement.
- "Is this a monotonically increasing operation?" → If yes, CRDTs (G-Counter, G-Set) provide correct eventually consistent semantics automatically.

---

### ⚙️ How It Works (Mechanism)

**Write path (leaderless, Cassandra-style):**

1. Client writes to coordinator node.
2. Coordinator writes to N replica nodes asynchronously.
3. With `ConsistencyLevel.ONE`: returns after 1 node ACKs. Others update in background.
4. With `ConsistencyLevel.ALL`: returns after all N nodes ACK — stronger but less available.

**Read repair:**

1. Client reads from R replicas.
2. Coordinator compares values: if they differ, take the freshest (highest timestamp).
3. Coordinator sends the fresh value to the stale replicas in the background.
4. Next read to any replica: will see the fresh value.

**Anti-entropy (Merkle tree sync):**

1. Each node maintains a Merkle tree over its key space.
2. Background job: compare Merkle tree root hashes with peers.
3. If hashes differ: traverse tree to find differing subtrees, sync only the differing keys.
4. Eventually: all nodes have identical Merkle tree → fully converged.

**Conflict resolution strategies:**

- **Last-Write-Wins (LWW):** Timestamp on each write; highest timestamp wins. Simple but loses concurrent writes.
- **Multi-value register (MV-register):** Keep all concurrent versions, return all to client for application-level merge. Used by Riak, DynamoDB.
- **CRDTs:** Data type designed for automatic, correct, conflict-free merge. G-Counter, OR-Set, LWW-Map.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Cassandra write with ONE, eventual read):**

```
Client
  │
  ├── Write("views", 1042) ──▶ Coordinator (Node 1)
  │                                │
  │                          Local commit + return OK
  │                           (ConsistencyLevel.ONE)
  │                           │
  │                           ├──▶ Node 2 (async replication)
  │                           └──▶ Node 3 (async replication)
  │
  ├── Read("views") ──────▶ Node 2 (may have old value!)
  │                              │
  │                         Return 1041 (stale: lag 200ms)
  │                              │
  ▼                         ← YOU ARE HERE (staleness window)

Later (200ms):
  Node 2 and Node 3 both updated to 1042 via replication.
  Fully converged.
```

**FAILURE PATH:**
Node 3 goes offline during write. Coordinator stores hint for Node 3. When Node 3 recovers, hinted handoff delivers the write. Convergence delayed by Node 3's downtime. During this period: reads from Node 3 may return pre-failure values. Anti-entropy will eventually sync.

**WHAT CHANGES AT SCALE:**
At global scale (US, EU, APAC), replication lag can be 200-500ms between regions. Within a region: typically <50ms. Tuning: reduce `hinted_handoff_window_time` to fail fast on dead replicas instead of accumulating hints. Increase `read_repair_chance` to heal stale replicas on reads. Monitor `ReplicaFilteringProtection` metrics.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two clients simultaneously increment a counter: both read 100, both write 101. Result: 101 (not 102). The increment from one client is lost. This is the fundamental challenge of eventual consistency with read-modify-write operations. Solution: use atomic operations (Cassandra counters, Redis INCR) or CRDTs (G-Counter).

---

### 💻 Code Example

**BAD - Read-Modify-Write on eventually consistent store (lost update):**

```java
// Two threads race on Cassandra with ConsistencyLevel.ONE
// Both read 100, both write 101, one update is lost
public void incrementViewCount(String articleId) {
    Row row = session.execute(
        "SELECT views FROM articles WHERE id = ?",
        articleId
    ).one();
    long views = row.getLong("views");
    // Race: another thread already incremented to 101
    session.execute(
        "UPDATE articles SET views = ? WHERE id = ?",
        views + 1,  // ← stale read: will write 101, not 102
        articleId
    );
}
```

**GOOD - Using Cassandra counter (eventually consistent, correct):**

```java
// Cassandra counters use distributed counter protocol
// Correct under eventual consistency (no lost updates)
public void incrementViewCount(String articleId) {
    session.execute(
        "UPDATE article_counters " +
        "SET views = views + 1 WHERE id = ?",
        articleId
    );
    // Cassandra serializes counter increments per partition
    // No read-modify-write race; atomic increment
}
```

**GOOD - CRDT G-Counter for multi-datacenter counts:**

```java
// G-Counter CRDT: each node has its own slot
// Merge = take max of each slot → no conflicts possible
public class DistributedViewCounter {
    private final Map<String, Long> nodeSlots =
        new ConcurrentHashMap<>();
    private final String nodeId;

    public DistributedViewCounter(String nodeId) {
        this.nodeId = nodeId;
    }

    // Thread-safe local increment
    public void increment() {
        nodeSlots.merge(nodeId, 1L, Long::sum);
    }

    // Total view count
    public long count() {
        return nodeSlots.values().stream()
            .mapToLong(Long::longValue).sum();
    }

    // Merge from another node (safe, idempotent)
    public void merge(Map<String, Long> remoteSlots) {
        remoteSlots.forEach((node, count) ->
            nodeSlots.merge(node, count, Math::max)
        );
    }
}
// merge() is commutative, associative, idempotent
// → safe to call in any order, any number of times
// → convergence guaranteed regardless of message order
```

**How to test / verify correctness:**

```bash
# Test convergence: write to one node, read from another
# with increasing delay, verify convergence time
for delay in 0 100 500 1000 5000; do
  sleep $((delay/1000))
  val=$(cqlsh node2 -e "SELECT views FROM articles WHERE id='1'")
  echo "After ${delay}ms: $val"
done

# Test conflict resolution: concurrent writes to same key
# from two nodes; verify final state matches expected merge
cqlsh node1 -e "UPDATE t SET val='a' WHERE id='1';" &
cqlsh node2 -e "UPDATE t SET val='b' WHERE id='1';" &
wait; sleep 2
cqlsh node1 -e "SELECT val FROM t WHERE id='1';"
cqlsh node2 -e "SELECT val FROM t WHERE id='1';"
# Both should return same value after convergence
```

---

### ⚖️ Comparison Table

| Property                     | Eventual                | Causal                 | Sequential       | Linearizable    |
| :--------------------------- | :---------------------- | :--------------------- | :--------------- | :-------------- |
| Stale reads                  | Yes (bounded by lag)    | Causally related: No   | No (in sequence) | Never           |
| Concurrent write handling    | Conflict resolution     | Causal ordering        | Serialized       | Serialized      |
| Write latency                | Lowest (local)          | Low                    | Medium           | Highest         |
| Availability under partition | Highest (AP)            | High                   | Low              | Low (CP)        |
| Application complexity       | High (handle staleness) | Medium                 | Low              | Lowest          |
| Use case                     | Counters, DNS, CDN      | Social feeds, comments | GPU memory       | Locks, balances |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                            |
| :---------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Eventual consistency means data loss"                      | Data is not lost — writes are queued for replication. Eventual consistency means reads may be temporarily stale, not that writes are discarded. Data loss only occurs if a node fails permanently before replication completes.                                    |
| "Eventual consistency is only for unimportant data"         | DNS runs the internet on eventual consistency. Amazon's product catalog, Netflix's viewing history, Facebook's social graph — all eventual consistency. "Unimportant" conflates importance with correctness requirements.                                          |
| "You can't have read-your-writes with eventual consistency" | Read-your-writes is a separate property. You can implement it on top of eventual consistency with sticky sessions (route client reads to the same replica they wrote to) or with session tokens (DynamoDB's consistent read for your own session).                 |
| "Eventual consistency means you can't use transactions"     | Transactions and consistency models are orthogonal. You can have ACID transactions within a single node that is part of an eventually consistent cluster. The transaction ensures atomic local operations; eventual consistency governs cross-replica propagation. |
| "CRDTs solve all eventual consistency problems"             | CRDTs solve conflict resolution for certain data types (counters, sets, maps). They don't solve read-your-writes, causal ordering across keys, or correctness for arbitrary business logic. They're a tool, not a silver bullet.                                   |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Silent Data Loss via Last-Write-Wins**

**Symptom:** Users report saved data "disappeared." Log analysis shows the write was acknowledged successfully. Data existed momentarily and then vanished after the next write from a different node.
**Root Cause:** Two concurrent writes to the same key on different replicas. LWW (Last-Write-Wins) on timestamp: the write with the lower wall-clock time is silently discarded. If clocks are not perfectly synchronized (NTP skew), the "first" write (by real-time) loses.
**Diagnostic:**

```bash
# Check clock skew across Cassandra nodes:
nodetool describecluster | grep "Schema versions"
# Check for multiple schema versions (sign of clock issues)

# In Cassandra: check for ghost writes using WRITETIME:
cqlsh -e "SELECT WRITETIME(field) FROM table WHERE id='x';"
# Compare WRITETIME across replicas for same key
```

**Fix:**
BAD: Relying on wall-clock LWW for user-editable data.
GOOD: Use optimistic locking (ETag/version in DynamoDB ConditionExpression, Cassandra LWT). Or use CRDTs for data types that support them.
**Prevention:** Require conflict resolution strategy to be explicitly chosen at schema design time. Default = explicit choice, not inherited LWW.

**Failure Mode 2: Permanent Divergence (Split-Brain Convergence Failure)**

**Symptom:** After a network partition heals, two nodes continue to show different values for the same key indefinitely. Neither updates to the other's value. Manual inspection required.
**Root Cause:** Anti-entropy disabled or broken. Hinted handoff queue overflowed and hints were dropped. The nodes are "technically converged" from the system's perspective (no error), but the values differ because the winning version was decided incorrectly.
**Diagnostic:**

```bash
# Check if anti-entropy is running:
nodetool repair --full <keyspace>
# Check for hint queue backlog:
nodetool tpstats | grep -A5 HintedHandoff
# Check for overflowed hints (silent data loss):
grep "Discarding" /var/log/cassandra/system.log | grep -i hint
```

**Fix:**
BAD: Waiting for anti-entropy to heal naturally when it's broken.
GOOD: Run `nodetool repair` manually to force Merkle tree sync. Investigate root cause of anti-entropy failure.
**Prevention:** Schedule regular `nodetool repair` runs. Monitor hint queue depth. Alert on hint drops (each hint drop = a lost write for an unavailable node).

**Failure Mode 3: Security - Privilege Escalation via Stale Read**

**Symptom:** An attacker with read access to an eventually consistent store times requests to exploit the replication window. They read their own permission record immediately after an admin REVOKES their access, getting the pre-revocation permissions from a stale replica. They use these to pass an auth check.
**Root Cause:** Permission store uses eventual consistency. Revocation write propagates in ~500ms. Attacker issues auth requests within 500ms of revocation.
**Diagnostic:**

```bash
# Identify auth reads using eventually consistent path:
grep -r "ConsistencyLevel.ONE\|consistency=eventual" auth-service/
# Measure permission store replication lag:
cqlsh node1 -e "SELECT WRITETIME(permissions) FROM acl WHERE user='attacker';"
cqlsh node2 -e "SELECT WRITETIME(permissions) FROM acl WHERE user='attacker';"
# Compare WRITETIMEs
```

**Fix:**
BAD: Permission reads using eventual consistency.
GOOD: Route all security-sensitive reads (permissions, session validity, revocations) to strongly consistent reads. Use a separate strongly consistent store (etcd, Redis with persistence) for auth data.
**Prevention:** Never use eventual consistency for security-sensitive data. Document this as an immutable requirement in the data classification policy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-006 - CAP Theorem (why eventual consistency is the AP choice)
- DST-008 - Consistency Models (eventual consistency in the broader spectrum)
- DST-014 - Replication Strategies (how async replication enables eventual consistency)

**Builds On This (learn these next):**

- DST-011 - Causal Consistency (stronger model preserving cause-effect ordering)
- DST-013 - CRDTs (data types enabling correct eventual consistency without conflicts)
- DST-067 - Consistency Level Selection (practical per-operation guide)

**Alternatives / Comparisons:**

- DST-009 - Strong Consistency (the stronger trade-off: correctness at coordination cost)
- DST-011 - Causal Consistency (intermediate: preserves causality, not full ordering)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Replicas converge eventually;  |
|                  | reads may be temporarily stale |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Strong consistency unavailable |
|                  | for high-write, global systems |
+------------------+--------------------------------+
| KEY INSIGHT      | "Eventual" is a convergence    |
|                  | guarantee, not chaos           |
+------------------+--------------------------------+
| USE WHEN         | Counters, social graphs, DNS,  |
|                  | CDN, analytics, product views  |
+------------------+--------------------------------+
| AVOID WHEN       | Balances, locks, inventory,    |
|                  | permissions, any mutual exclus.|
+------------------+--------------------------------+
| TRADE-OFF        | High throughput + availability |
|                  | vs. possible stale reads       |
+------------------+--------------------------------+
| ONE-LINER        | Highest availability + lowest  |
|                  | write latency; staleness window|
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-013 CRDTs,                 |
|                  | DST-011 Causal Consistency     |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Eventual consistency = all replicas converge if writes stop; reads may return stale values during the convergence window.
2. Concurrent writes need explicit conflict resolution: LWW (lossy), CRDT (safe), multi-value register (application-resolved).
3. Never use eventual consistency for security, financial, or mutual exclusion data — use strong consistency there.

**Interview one-liner:**
"Eventual consistency guarantees that all replicas will converge to the same value if updates stop — enabling maximum write availability and low latency through async replication — at the cost of potential stale reads during convergence and requiring explicit conflict resolution strategies for concurrent writes."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Before applying any consistency model, classify the data by its _business convergence requirement_, not its _technical staleness tolerance_. The question is not "can we handle reading old data?" but "what is the worst-case business outcome if two clients see different values for the next 500ms?" If the answer is "acceptable" — eventual consistency is correct. If the answer is "a security breach or financial loss" — strong consistency is required, regardless of throughput cost.

**Where else this pattern appears:**

- **Git distributed version control:** Each developer's local repo is "eventually consistent" with the remote. You commit locally (writes succeed immediately), then push (propagation). Concurrent changes create merge conflicts — exactly the concurrent-write conflict of eventual consistency. Git's merge strategies are conflict resolution policies.
- **Browser IndexedDB + Service Workers (offline-first):** A web app writes to IndexedDB while offline. When online, it syncs to the server. The app is "eventually consistent" with the server. Conflict resolution happens on sync. This is exactly the Dynamo pattern applied to frontend development.
- **Email delivery (SMTP):** An email is accepted by your MTA immediately (local commit). It propagates to the recipient's MTA asynchronously (eventual delivery). "Email sent" ≠ "email received." The system converges eventually.

---

### 💡 The Surprising Truth

The Amazon Dynamo paper (2007) that popularised eventual consistency describes the shopping cart as "always writeable" — you can always add items to your cart, even during failures. But the implementation secretly uses **multi-value registers** (storing all concurrent versions, not just the latest). When you next visit your cart, the application code merges the conflicting versions by taking the union of all items. This means: Dynamo doesn't implement Last-Write-Wins for the cart — it implements application-level merge. The "eventual" in Dynamo isn't "eventually one value wins" — it's "eventually all conflicting versions are presented to the application for merging." Most engineers who use eventually consistent databases have never implemented this application-level merge, which means their systems silently discard concurrent writes via LWW — losing customer data exactly when eventual consistency is most stressed (during failures).

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A distributed ticket booking system for concert seats must handle 100k concurrent purchases at ticket-on-sale moment. Two options: (A) eventually consistent (all requests succeed instantly, merge conflicts later, some buyers get refunds), (B) strongly consistent (correct reservations, but system may queue/reject under load). What factors determine the right choice, and is there a hybrid that handles the "flash sale" peak without being purely eventually consistent?
_Hint:_ The cost of the "merge" in option A is refund processing + customer dissatisfaction. The cost of option B's queue is abandoned checkouts. Is there a middle ground where you use AP for the first 80% of inventory and CP for the last 20%? What does this imply about PACELC?

**Q2 (D - Root Cause):** A team migrates from MySQL (synchronous replication, read-your-writes) to Cassandra (eventual consistency, `ONE` consistency level). The migration passes all functional tests. In production, 0.1% of users report "my profile update didn't save." The team confirms the writes succeeded (Cassandra acknowledged them). What is the likely failure mechanism, and what two architectural changes would eliminate it?
_Hint:_ The profile update writes to Node 1. The subsequent profile page load reads from Node 2 (load-balanced). Node 2 has replication lag. The user refreshes — sees old data. This is a read-your-writes violation. What are two ways to get read-your-writes semantics on an eventually consistent system without changing the database?

**Q3 (E - First Principles):** CRDTs are described as "eventual consistency with automatic conflict resolution." A G-Counter CRDT is provably correct for concurrent increments — no updates are lost. Is a G-Counter also eventually consistent? What makes it so? And why can't you build a G-Counter-equivalent for account balances (which require both increment and decrement)?
_Hint:_ A G-Counter's merge function (take max of each slot) is monotonically increasing — once a slot value increases, it never decreases. This is the key to convergence proofs. Balances require decrement, which is a non-monotonic operation. What breaks the CRDT convergence guarantee when the merge function is not monotone?
