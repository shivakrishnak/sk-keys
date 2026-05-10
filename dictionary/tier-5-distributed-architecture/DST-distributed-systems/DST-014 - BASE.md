---
id: DST-014
title: BASE
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-006, DST-010, DST-024
used_by: DST-010, DST-067
related: DST-006, DST-007, DST-010, DST-024, DST-025
tags:
  - distributed
  - consistency
  - foundational
  - intermediate
  - tradeoff
  - mental-model
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /distributed-systems/base/
---

# DST-014 - BASE

⚡ TL;DR - BASE (Basically Available, Soft-state, Eventually consistent) is the theoretical alternative to ACID for distributed systems, describing how high-scale systems trade immediate consistency for continuous availability and horizontal scalability.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-006, DST-010, DST-024                   |     |
| **Used by:**    | DST-010, DST-067                            |     |
| **Related:**    | DST-006, DST-007, DST-010, DST-024, DST-025 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The internet's early scaling challenges: a single relational database with full ACID transactions processes all requests. Peak load arrives: 100x normal traffic. The single RDBMS becomes a bottleneck. Transactions queue up. Locks pile up. Response times climb from 10ms to 10,000ms. The site returns 503s. Amazon, eBay, and Google face this exact wall in the early 2000s.

**THE BREAKING POINT:**
Engineers discover: to handle internet-scale traffic, you MUST distribute data across hundreds of nodes. But distributed ACID transactions (2PC across 100 nodes) have O(n) coordination cost — each write touches all nodes. At 100 nodes, the coordination overhead exceeds the actual work. Full ACID becomes mathematically incompatible with internet-scale distribution.

**THE INVENTION MOMENT:**
Eric Brewer coined the term "BASE" (contrasting with "ACID") in his 2000 PODC keynote introducing the CAP conjecture. Pat Helland at Microsoft Research developed the "Life beyond Distributed Transactions" paper (2007). Vogels (Amazon) published "Eventually Consistent" (2007). Together, these formalized BASE as the design philosophy underlying Dynamo, BigTable, Cassandra, and the NoSQL movement.

**EVOLUTION:**
2000: Brewer coins "BASE" at PODC. 2007: Amazon Dynamo paper; Vogels "Eventually Consistent." 2009: NoSQL movement formalizes around BASE principles. 2012: NewSQL databases (Spanner, CockroachDB) attempt ACID at scale via distributed consensus. 2015-2020: Tension between BASE NoSQL and ACID NewSQL; practitioners recognize both have valid use cases. Today: most large-scale systems use BASE for the bulk of data and ACID for critical financial/transactional data.

---

### 📘 Textbook Definition

**BASE** is an acronym describing the consistency model of highly available distributed systems, contrasted with ACID (Atomicity, Consistency, Isolation, Durability) of traditional relational databases. BASE stands for: **Basically Available** — the system guarantees availability in the CAP theorem sense (every request receives a response, though it may be stale or inconsistent); **Soft-state** — the system's state may change over time even without input, due to eventual consistency propagation and expiry; **Eventually consistent** — the system will become consistent over time if no new updates are made, but consistency is not guaranteed at any given moment. BASE is not a replacement for ACID — it's a deliberate trade-off designed for systems where availability is the primary constraint.

---

### ⏱️ Understand It in 30 Seconds

**One line:** BASE systems always respond (even if stale), accept that state is fluid (soft), and will eventually agree on values — trading ACID's immediate correctness for unlimited scalability.

> BASE is the philosophy of a post office vs. a bank vault. A post office (BASE): always accepts your letter (available), letters may be in transit or lost (soft-state), everyone will eventually get their mail (eventually consistent). A bank vault (ACID): either your transaction succeeds completely or doesn't happen at all; everyone always sees the exact current balance.

**One insight:** "BASE" is not a database feature — it's an architectural philosophy. A system that is BASE has made a deliberate decision: availability is more important than immediate consistency, and the application layer will handle the residual inconsistency window.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Basically Available:** Nodes always respond to requests. Partial failures (some nodes down) don't make the whole system unavailable. Responses may be stale or degraded, but always present.
2. **Soft-state:** Unlike ACID's "durable state" (committed = permanent), BASE's state is fluid. Background processes (gossip, anti-entropy) continuously update state. Caches expire. Replica states drift and converge.
3. **Eventually consistent:** Given time without new updates, all replicas will converge to the same value. "Eventually" is undefined — could be milliseconds or minutes depending on network and load.
4. **No cross-entity ACID transactions:** BASE systems typically offer atomicity within a single entity/document, not across multiple. Compensating transactions handle cross-entity corrections.

**DERIVED DESIGN:**
BASE systems architect for: leaderless replication (any node can accept writes), conflict resolution policies (LWW, CRDTs, multi-value), application-level idempotency, and compensation over rollback.

**THE TRADE-OFFS:**
**Gain:** Linear horizontal scalability (no global coordinator bottleneck). Full availability under partition. Geographic distribution without cross-region write blocking.
**Cost:** Application complexity for handling stale reads and conflicts. No multi-entity atomicity. Conflict resolution must be explicitly designed. Debugging inconsistencies is harder.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** In a distributed system, you cannot have both unlimited availability and immediate global consistency. BASE's trade-off is physically irreducible.
**Accidental:** Many systems implement BASE without acknowledging it — they use an eventually consistent cache (Redis) in front of an ACID database without defining what happens when they diverge. This "accidental BASE" is the worst of both worlds: no explicit conflict policy, no monitoring for divergence.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce product catalog has 10 million items. 50,000 reads per second. Stock levels update 1,000 times per second.

**WITH ACID ONLY:**
All reads and writes go through a primary RDBMS. 50,000 concurrent readers + 1,000 writers. Row-level locks on stock count updates. Readers blocked by writers (or vice versa, depending on isolation). At scale: deadlocks, lock contention, queue buildup. P99 read latency: 500ms. System can't handle peak load.

**WITH BASE:**
Reads served from 50 Cassandra nodes (any node, no coordination). Writes go to local node, async replicate. P99 read latency: 2ms. System handles 50,000 reads/sec easily. Trade-off: a product page may show stock=1 even after the last item sold (for ~200ms). The "oversell risk" is managed in the order confirmation layer with ACID database check.

**THE INSIGHT:** BASE is not "we gave up on correctness." It's "we moved correctness responsibility to the right layer." Catalog browsing needs BASE (speed + availability). Order confirmation needs ACID (correctness). Most large-scale systems use BOTH — BASE for the read-heavy user-facing layer, ACID for the write-critical business layer.

---

### 🧠 Mental Model / Analogy

> BASE is the philosophy of Wikipedia vs. a legal notary. Wikipedia (BASE): always available, articles may be in flux (soft-state), eventually all facts will be corrected and agreed upon. A legal notary (ACID): every document is exactly correct at the moment of signing, witnessed, and irrevocable. Wikipedia works for encyclopedia knowledge; a notary is required for property deeds. Neither is "wrong" — they serve different needs.

**Mapping:**

- **Wikipedia articles** → BASE data (product descriptions, social posts, analytics)
- **Legal documents** → ACID data (financial transactions, signed contracts, inventory commitments)
- **Article edits "in flight"** → soft-state (replication in progress)
- **Edit wars converging** → eventual consistency
- **"Any Wikipedia server can answer"** → basically available

Where this analogy breaks down: Wikipedia has human editors resolving conflicts; BASE systems need automated conflict resolution (LWW, CRDT) without human intervention.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
BASE systems always give you an answer (even if slightly old), can handle massive traffic by distributing the work, and will eventually have all their servers agree on the latest data. They trade "always exactly right" for "always available and fast."

**Level 2 - How to use it (junior developer):**
Use BASE-oriented systems (Cassandra, DynamoDB, MongoDB with eventual reads) for: product catalogs, social feeds, user activity, recommendation systems, analytics. Use ACID systems (PostgreSQL, MySQL, CockroachDB) for: payments, orders, inventory commitments, account balances. The architecture rule: BASE for the 95% of read-heavy, tolerance-for-staleness data; ACID for the 5% of write-critical, correctness-required data.

**Level 3 - How it works (mid-level engineer):**
BASE's three properties map to concrete mechanisms: "Basically Available" → leaderless replication (Dynamo-style), any-node writes. "Soft-state" → TTL-based caching, background anti-entropy, gossip protocol convergence, read repair. "Eventually consistent" → async replication with configurable replication factor, hinted handoff for failed nodes, Merkle tree sync for replica divergence detection. Application implications: idempotent write APIs (duplicate writes must be safe), read-your-writes via session tokens, explicit stale-read handling (show "last updated at" timestamps).

**Level 4 - Why it was designed this way (senior/staff):**
BASE is the explicit naming of what the internet's first-generation scale systems discovered empirically. Amazon's Dynamo, Google's BigTable, Facebook's Cassandra — all independently arrived at the same design: accept stale reads for availability and scale. The contribution of the "BASE" label is making the philosophy EXPLICIT. An architect who says "this is a BASE system, soft-state window is ≤500ms, conflict resolution is LWW by timestamp" has made the trade-offs visible, monitorable, and testable. An architect who silently uses eventual consistency without naming it has hidden a major correctness assumption from the team.

**Expert Thinking Cues:**

- "What is the soft-state window for this data?" → If you can't answer, BASE is accidental.
- "What's your conflict resolution policy?" → Required for any BASE system with concurrent writes.
- "Is your staleness observable to the user?" → If yes: show staleness indicator or increase replication consistency level.
- "What requires ACID in your system?" → Identify explicitly. Everything else can be BASE candidate.

---

### ⚙️ How It Works (Mechanism)

**Basically Available — Dynamo-style leaderless:**

1. Any node accepts writes (no single master).
2. Write is replicated asynchronously to N-1 peers.
3. If some peers are unavailable: hinted handoff stores the write for later delivery.
4. Client gets acknowledgment after W nodes confirm (W=1 for maximum availability, W=ALL for durability).
5. Read from R nodes (R=1 for maximum availability).

**Soft-state — continuous background updates:**

1. Gossip protocol: each node periodically exchanges state with a random peer.
2. Anti-entropy: Merkle tree comparison detects diverged keys; missing writes are synced.
3. TTL-based expiry: cache entries age out; soft-state by design.
4. Read repair: reads comparing replicas trigger background updates to stale replicas.

**Eventually consistent — convergence guarantee:**

1. Given no new writes to a key, gossip + anti-entropy ensures all replicas converge.
2. Convergence time = function of gossip interval, anti-entropy frequency, replication factor.
3. In practice: 99th percentile convergence in <500ms for same-datacenter; <5s cross-datacenter.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Cassandra BASE read path):**

```
Client request: GET /product/123/stock

Load balancer → API server (any)
  │
  ▼
Cassandra (leaderless, any coordinator)
  │
  ├──▶ Replica 1: stock = 5 (latest)
  ├──▶ Replica 2: stock = 6 (stale, 100ms lag)
  └──▶ Replica 3: stock = 5 (latest)
  │
  │ ConsistencyLevel.ONE: return first response
  │ ConsistencyLevel.QUORUM: return majority (5)
  ▼
  ← YOU ARE HERE: Client sees stock = 5 or 6
  (depending on CL and timing)

Background: Read repair updates Replica 2 to stock=5
After 100ms: all replicas = 5 (converged)
```

**FAILURE PATH (Node 1 unavailable):**
Write arrives for product/123. Node 1 (replica) is down. Coordinator stores hint on Node 2: "deliver to Node 1 when it recovers." Hint stored for up to `hinted_handoff_window_time` (default: 3 hours). Node 1 recovers within 3h: hint delivered, Node 1 updated. Node 1 recovers after 3h: hint discarded; rely on anti-entropy repair to sync.

**WHAT CHANGES AT SCALE:**
At 1M writes/sec: gossip protocol traffic scales O(log N) — 1000-node cluster gossips to ~10 nodes per round. Anti-entropy Merkle trees cover full keyspace but only sync diverged ranges. Key monitoring: replication lag P99, hint queue depth, dropped hint rate. Alert on: P99 replication lag > 1s (acceptable = typically <200ms intra-DC).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent writes to the same key from different DCs: LWW (Last-Write-Wins) by default — lower-timestamp write is silently discarded. Application implication: client A's write may vanish. Mitigations: CRDTs (data types designed for concurrent merge), application-level version checks, or use QUORUM consistency to force cross-DC coordination (sacrificing pure BASE behavior for this key).

---

### 💻 Code Example

**BAD - Ignoring BASE implications (treating Cassandra as ACID):**

```java
// Treating BASE store as if it's ACID — no staleness handling
@GetMapping("/checkout")
public CheckoutResult checkout(String userId, String itemId) {
    // May read stale stock (Cassandra ONE consistency)
    int stock = inventoryRepo.getStock(itemId);
    if (stock > 0) {
        // Race: another thread deducted stock since read
        inventoryRepo.decrementStock(itemId);
        orderRepo.createOrder(userId, itemId);
        // Order created but stock may now be negative!
        return CheckoutResult.SUCCESS;
    }
    return CheckoutResult.OUT_OF_STOCK;
}
```

**GOOD - BASE for catalog, ACID for commitment:**

```java
// BASE layer: fast product catalog read (Cassandra)
// ACID layer: order commitment (PostgreSQL)
@Service
public class CheckoutService {

    // FAST: BASE catalog read (may be ~200ms stale)
    public ProductInfo getProductInfo(String itemId) {
        return cassandraProductRepo.findById(itemId);
        // OK: stale description/image is harmless
    }

    // CRITICAL: ACID inventory reservation
    @Transactional  // PostgreSQL SERIALIZABLE
    public ReservationResult reserveItem(
        String userId, String itemId, int quantity
    ) {
        // Strong consistency: read from RDBMS primary
        Inventory inv = inventoryRepo.findForUpdate(itemId);
        if (inv.getAvailable() < quantity) {
            return ReservationResult.OUT_OF_STOCK;
        }
        // Atomic decrement (ACID guarantee)
        inv.decrement(quantity);
        inventoryRepo.save(inv);
        orderRepo.createOrder(userId, itemId, quantity);
        // Both operations atomic — no partial commit
        return ReservationResult.RESERVED;
    }
}
// Architecture: 99% of requests hit the BASE catalog
// 1% of checkout requests hit the ACID reservation path
```

**How to test / verify correctness:**

```bash
# Test eventual consistency (convergence time):
# Write to one node, poll all replicas until consistent:
cqlsh node1 -e "UPDATE products SET stock=10 WHERE id='A';"
for node in node1 node2 node3; do
  echo -n "$node: "
  cqlsh $node -e "SELECT stock FROM products WHERE id='A';"
done
# Repeat with 1s delay until all show 10 — measure convergence

# Test basically available (partition handling):
# Block replication between nodes, verify both accept writes:
iptables -I INPUT -s node2 -j DROP   # partition node2
cqlsh node1 -e "UPDATE products SET stock=8 WHERE id='A';"
cqlsh node2 -e "SELECT stock FROM products WHERE id='A';"
# node2 should still respond (Basically Available)
# and show stock=10 (stale — pre-partition value)
```

---

### ⚖️ Comparison Table

| Property               | ACID                               | BASE                            |
| :--------------------- | :--------------------------------- | :------------------------------ |
| Availability           | Reduced (locks, coordination)      | Maximized (any node serves)     |
| Consistency            | Immediate, strong                  | Eventual, soft                  |
| Partition behavior     | CP (refuse or block)               | AP (serve, converge later)      |
| Horizontal scalability | Limited (coordination overhead)    | Linear (no global coordinator)  |
| Write latency          | Higher (coordination)              | Lower (local commit)            |
| Application complexity | Lower (DB handles consistency)     | Higher (app handles staleness)  |
| Use case               | Financial, transactional, critical | Social, analytics, catalog, IoT |
| Examples               | PostgreSQL, MySQL, CockroachDB     | Cassandra, DynamoDB, CouchDB    |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                 |
| :------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "BASE means no consistency"                  | BASE means EVENTUAL consistency — a formal guarantee that replicas converge. This is NOT "no consistency" — it's a weaker but still-guaranteed model. DNS has been BASE for 40 years and is extremely reliable.         |
| "BASE and ACID are mutually exclusive"       | Most large systems use BOTH. BASE for high-volume catalog/analytics reads; ACID for transactional writes. They coexist at different layers of the same architecture.                                                    |
| "NoSQL = BASE"                               | NoSQL databases vary widely. MongoDB (with write concerns) can approach ACID. CockroachDB (NewSQL) is fully ACID. "NoSQL" describes the data model, not the consistency model.                                          |
| "Soft-state means data can disappear"        | Soft-state means state can CHANGE over time (via background convergence processes). It does NOT mean data is lost. Replication factor (typically 3) ensures durability. Soft-state = mutable background, not ephemeral. |
| "BASE is for startups who can't afford ACID" | Google, Amazon, and Facebook — the world's largest engineering organizations — use BASE systems for their core data. BASE is a sophisticated architectural choice, not a cost-cutting measure.                          |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale Product Information Causing Incorrect Orders**

**Symptom:** Customers order products at prices that were updated hours ago. Revenue impact. Customer complaints about "bait-and-switch."
**Root Cause:** Product catalog (pricing, descriptions) stored in BASE (eventually consistent) system. Price update propagated with 4-hour replication lag to regional CDN cache. Orders processed against stale price.
**Diagnostic:**

```bash
# Check cache staleness for pricing data:
curl -I https://api.example.com/product/123/price
# Look for: Age header, Last-Modified, Cache-Control max-age
# If Age > acceptable staleness window: cache is too stale

# Check Cassandra replication lag for pricing table:
nodetool cfstats catalog.prices | grep "Read Latency"
nodetool tpstats | grep "Read Stage"
```

**Fix:**
BAD: Using BASE (cached) pricing for order confirmation.
GOOD: Use BASE pricing for catalog browsing (performance). Use ACID pricing (read from primary DB) for order checkout confirmation. Never confirm an order against a BASE-cached price.
**Prevention:** Classify data by mutation risk. Frequently-mutating data (prices, inventory) needs short TTL or ACID reads for critical operations.

**Failure Mode 2: Conflicting Writes Creating Phantom Updates**

**Symptom:** User saves their preference settings. Refreshes page. Old settings shown. Refreshes again. New settings shown. Intermittent. No error.
**Root Cause:** User's write hit Node A. Subsequent read hit Node B (replication lag ~800ms). BASE system with LWW: if the user wrote twice quickly (double-save), the second write's timestamp was lower (clock skew) and was discarded. User sees first (older) version because second write (newer version by intent, older by timestamp) was LWW-discarded.
**Diagnostic:**

```bash
# Check WRITETIME for the key across replicas:
cqlsh node_a -e "SELECT WRITETIME(preference) FROM user_prefs WHERE id=?;"
cqlsh node_b -e "SELECT WRITETIME(preference) FROM user_prefs WHERE id=?;"
# If timestamps differ: LWW discarded one write
# Check NTP sync:
chronyc tracking | grep "RMS offset"
```

**Fix:**
BAD: Using wall-clock LWW for user-editable data.
GOOD: Use client-side version counter (monotonic) instead of wall clock for LWW. Or use Cassandra's Lightweight Transactions (Paxos) for user preference writes. Or use CRDTs.
**Prevention:** Never rely on wall-clock timestamps for LWW conflict resolution in distributed systems. Logical clocks (Lamport, vector) are more reliable.

**Failure Mode 3: Security - Stale Permission Read in BASE Auth Layer**

**Symptom:** User's API key is revoked. 30-90 seconds later, requests with the revoked key still succeed. Security incident window is up to 90 seconds.
**Root Cause:** API gateway caches authentication results from a BASE auth service (Cassandra). Cache TTL = 90 seconds. Revocation written to Cassandra is soft-state — hasn't propagated to all gateway instances yet.
**Diagnostic:**

```bash
# Check auth cache TTL:
grep -r "authCacheTTL\|AUTH_CACHE_TTL" gateway/ config/
# Check Cassandra replication for auth table:
cqlsh -e "SELECT WRITETIME(revoked) FROM auth.api_keys WHERE key='?';"
# Compare WRITETIME across nodes
```

**Fix:**
BAD: Caching auth results with long TTL in a BASE system.
GOOD: Auth data uses ACID + strong consistency reads (zero cache or very short TTL <1s). Alternatively: revocation list pushed to all gateways via strong-consistency pub/sub (not async replication).
**Prevention:** Security policy: auth, sessions, and revocations are NEVER BASE. Zero-tolerance for staleness on security-critical data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-006 - CAP Theorem (why BASE exists: AP systems in CAP)
- DST-010 - Eventual Consistency (the "E" in BASE)
- DST-024 - ACID Properties (what BASE contrasts with)

**Builds On This (learn these next):**

- DST-010 - Eventual Consistency (deep dive into BASE's consistency model)
- DST-067 - Consistency Level Selection (practical guide for choosing BASE vs ACID per operation)

**Alternatives / Comparisons:**

- DST-024 - ACID Properties (the opposite pole: immediate consistency + atomicity)
- DST-025 - Distributed Transactions (attempts to bring ACID to distributed BASE systems)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Design philosophy: Always      |
|                  | available, soft-state, eventual |
+------------------+--------------------------------+
| PROBLEM SOLVED   | ACID can't scale horizontally  |
|                  | to internet-scale distribution |
+------------------+--------------------------------+
| KEY INSIGHT      | "Basically" + "Soft" + "Evtl." |
|                  | are deliberate trade-off names |
+------------------+--------------------------------+
| USE WHEN         | Catalog, analytics, social,    |
|                  | IoT, recommendation systems    |
+------------------+--------------------------------+
| AVOID WHEN       | Financial txns, inventory      |
|                  | commits, access control, locks |
+------------------+--------------------------------+
| TRADE-OFF        | Availability + scale vs.       |
|                  | immediate consistency          |
+------------------+--------------------------------+
| ONE-LINER        | Always responds, state is      |
|                  | fluid, will converge eventually|
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-010 Eventual Consistency,  |
|                  | DST-024 ACID Properties        |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. BASE = Basically Available (always responds) + Soft-state (state changes without input, via background sync) + Eventually consistent (convergence guaranteed, timing undefined).
2. BASE and ACID coexist in mature systems — BASE for high-volume reads, ACID for critical writes.
3. "BASE" is an architectural choice that must be explicit: define your staleness window, conflict resolution policy, and monitoring before deploying a BASE system.

**Interview one-liner:**
"BASE describes the design philosophy of highly available distributed systems: Basically Available (every request gets a response, possibly stale), Soft-state (state can change over time via background convergence), and Eventually consistent (all replicas will agree eventually) — the deliberate alternative to ACID when horizontal scalability and availability outweigh the need for immediate consistency."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The most dangerous version of BASE is the accidental one — using an eventually consistent system without explicitly defining your staleness window, conflict resolution strategy, and data classification policy. An explicit BASE system (with defined TTLs, monitored replication lag, documented conflict policies) is orders of magnitude safer than an ACID system with an implicit eventually-consistent cache layer added "for performance." Make every BASE trade-off visible.

**Where else this pattern appears:**

- **CDN cache design:** A CDN is a BASE system for static assets. Files are "Basically Available" (served from the nearest edge), "Soft-state" (cached with TTL, may be stale), and "Eventually consistent" (when origin updates, caches propagate within TTL window). CDN design is applied BASE thinking for content delivery.
- **Microservice sagas:** In a distributed transaction spanning 5 services, you can't have ACID across all. A Saga pattern is the BASE equivalent: each step is atomic locally, but the aggregate state is "soft" (partially committed saga), and the system "eventually" reaches a consistent state via compensating transactions. Sagas make BASE explicit for business process transactions.
- **Replicated config files (Chef, Puppet, Ansible):** Configuration changes pushed to 10,000 servers are eventually consistent. Some servers have the new config; others have the old. State is "soft" during rollout. Eventually all servers converge. This is BASE thinking applied to infrastructure configuration management.

---

### 💡 The Surprising Truth

Eric Brewer, who coined the CAP theorem, has publicly stated that the "CA" portion of CAP is largely irrelevant for real distributed systems — because network partitions are unavoidable and P is always required. The real choice is "CP vs AP." BASE is the architectural response to choosing AP. But the more surprising truth: BASE doesn't mean "forget about consistency." Amazon's Dynamo — the canonical BASE system — includes BOTH eventual consistency AND optional strong consistency (via quorum W+R > N) in the same API. The Dynamo paper describes BASE as the default but explicitly supports per-operation consistency level selection. "BASE" as a label risks obscuring this nuance: production BASE systems are typically tunable, not uniformly eventually consistent. Every "BASE" system should be thought of as a consistency spectrum, not a fixed point.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A ride-sharing app stores driver locations using a BASE system (Cassandra, updated 60x per second per driver). The staleness window is up to 1 second. A rider requests a car — the app shows a driver 0.5 km away. The driver actually moved 1 km away in the last second (stale data). What is the UX and safety impact of this staleness? Is there a threshold of staleness that changes the BASE→ACID decision for driver location data?
_Hint:_ Consider: at 60 km/h, a car moves 16m per second. 1-second staleness = 16m position error. Is 16m acceptable for routing? For ETA calculation? What about emergency vehicle dispatching?

**Q2 (D - Root Cause):** An e-commerce system uses BASE (Cassandra) for inventory counts and ACID (PostgreSQL) for order commitments. The architects assume: "Cassandra shows approximate stock; PostgreSQL is the source of truth for actual reservations." In production, they discover some SKUs have negative inventory in PostgreSQL despite the system "working." What is the failure mechanism, and what is the correct architecture to prevent it?
_Hint:_ Customers see stock > 0 in Cassandra (stale) and proceed to checkout. PostgreSQL enforces the constraint... unless the `CHECK (stock >= 0)` is implemented at the application layer (not as a DB constraint) and uses an optimistic read from the PostgreSQL replica (not the primary). Two separate bugs, but the root is ACID boundary leakage.

**Q3 (E - First Principles):** BASE states that systems are "basically" (not fully) available. What does "basically" mean formally? Is there a precise definition of "basically available" that distinguishes it from "sometimes available" or "99.9% available"? How does CAP theorem's definition of availability (every request to a non-failing node returns a response) relate to BASE's "basically"?
_Hint:_ CAP availability is binary: a non-failing node MUST respond. BASE's "basically" is a softer claim — degraded responses are acceptable. Where is the boundary between "basically available" and "unavailable"? Is a response of "data may be stale" considered available? Is a 503 "service unavailable" ever compatible with BASE?

