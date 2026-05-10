---
id: DST-006
title: CAP Theorem
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-001, DST-008
used_by: DST-007, DST-067
related: DST-007, DST-008, DST-010, DST-014
tags:
  - distributed
  - consistency
  - availability
  - intermediate
  - tradeoff
  - foundational
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /distributed-systems/cap-theorem/
---

# DST-006 - CAP Theorem

⚡ TL;DR - A distributed system can guarantee at most two of Consistency, Availability, and Partition tolerance simultaneously; since partitions are inevitable, the real choice is between consistency and availability during a partition.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-001, DST-008                   |     |
| **Used by:**    | DST-007, DST-067                   |     |
| **Related:**    | DST-007, DST-008, DST-010, DST-014 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed database team debates: "Can we have strong consistency, 100% availability, and survive network failures?" Without CAP, teams write contradictory requirements ("MUST always return current data AND must always respond AND must handle network partitions"). Engineers spend months trying to satisfy all three, building systems that subtly fail under partition scenarios no one anticipated.

**THE BREAKING POINT:**
A financial system deployed across two data centers loses inter-DC connectivity for 45 seconds. During that window, both nodes accept writes independently. When connectivity restores, the system has two conflicting ledger states - neither node knows which writes are authoritative. The system was designed with no partition policy. Nobody had decided: during this 45 seconds, should we refuse writes (CP) or accept them and reconcile (AP)?

**THE INVENTION MOMENT:**
Eric Brewer proposed the CAP conjecture at SOSP 1999 and PODC 2000. Seth Gilbert and Nancy Lynch formally proved it in 2002. The theorem gives the definitive answer: no distributed system over an asynchronous network can simultaneously guarantee all three properties. This transformed vague "reliability" discussions into a precise trade-off framework with exact vocabulary.

**EVOLUTION:**
2000: Brewer's conjecture. 2002: Gilbert-Lynch formal proof. 2012: Daniel Abadi publishes PACELC - extending CAP to cover the latency-consistency trade-off even in the absence of partitions. 2013: Brewer himself acknowledges CAP is often misapplied and "C" specifically means linearizability, not weaker consistency forms. 2017+: Kyle Kingsbury's Jepsen tests empirically verify CAP properties for dozens of databases.

---

### 📘 Textbook Definition

**CAP Theorem** (Brewer's Theorem) states that a distributed data store can provide at most two of: **Consistency (C)** - every read returns the most recent write or an error; **Availability (A)** - every request receives a non-error response (not guaranteed to be the most recent data); **Partition Tolerance (P)** - the system operates correctly despite network partitions. Since network partitions are inevitable in any real distributed system, P is mandatory. The practical choice is always CP vs AP during a partition event. CAP "C" specifically means linearizability - the strongest consistency model.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When the network fails between nodes, you must choose: refuse requests until consistent (CP) or answer with possibly stale data (AP). You cannot do both.

**One analogy:**

> CAP is like two bank branches cut off from each other. Branch A and Branch B lose their connection. Option CP: both branches freeze all transactions until the connection restores - consistent but unavailable. Option AP: both branches continue operating independently - available but possibly serving stale balances and allowing overdrafts. You cannot be simultaneously consistent and available during that outage.

**One insight:**
"P" is not a design choice - it's a fact of networked systems. Networks partition. The only choice is how your system responds when a partition occurs. "CA" is only possible in a single-node system - the moment you distribute data, P becomes mandatory.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Network partitions are inevitable:** Any distributed system over a real network will experience partitions (packet loss, link failures, datacenter disconnects).
2. **Consistency in CAP = linearizability:** Every read observes the effect of all previously completed writes. This is the strongest consistency model.
3. **Availability in CAP = every non-failing node responds:** Every request to a non-failed node must return a non-error response within bounded time.
4. **The conflict:** During a partition, if node A cannot reach node B, it cannot know if B has newer writes. To be consistent, A must either refuse the read (CP) or return stale data (AP).

**DERIVED DESIGN:**
The Gilbert-Lynch proof works by contradiction: assume a system satisfies all three. During a partition, node A receives a write. Node B receives a read for the same key. They cannot communicate. For A to be available (respond without error) and consistent (return the latest write), B would need to see A's write - impossible without communication. Contradiction: at least one property must be violated.

**THE TRADE-OFFS:**
**CP choice - Gain:** Reads always see the latest committed write. **Cost:** During a partition, the system returns errors rather than potentially stale data. Users experience unavailability.
**AP choice - Gain:** The system always responds, even during partitions. **Cost:** Reads may return stale data. Conflicting writes must be reconciled after the partition heals.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any system distributing state across nodes must define a partition policy. This complexity cannot be eliminated.
**Accidental:** "CA" system design that ignores partitions - the system appears to work until a real partition occurs, at which point behavior is undefined.

---

### 🧪 Thought Experiment

**SETUP:**
An inventory system for limited-edition sneakers (1,000 units, 50,000 concurrent buyers) is deployed across US-East and EU-West. A transatlantic network failure occurs during the sale.

**WHAT HAPPENS WITH CP:**
Both regions detect they cannot reach each other. Under CP policy, both refuse to process purchases: "Service unavailable - please try again." The 1,000 units are not oversold. Users see errors. Amazon loses revenue for the duration of the partition (~30 seconds). Result: consistent, slightly unavailable.

**WHAT HAPPENS WITH AP:**
Both regions continue accepting purchases independently. US-East sells 800 units. EU-West sells 700 units. Total: 1,500 units sold from 1,000 in stock. After partition heals, the inventory is 500 units negative. Oversell detected. Result: available, inconsistent - expensive reconciliation required.

**THE INSIGHT:**
The "right" answer depends on business context. For sneakers (oversell is catastrophic): CP. For a shopping cart (adding a duplicate item is minor): AP. CAP forces you to articulate your partition policy explicitly before you encounter the partition - not during it.

---

### 🧠 Mental Model / Analogy

> CAP is like a distributed banking system's policy during a communication outage. Before designing the system, the bank must answer: "If our two datacenters lose connectivity, should we (A) stop all transactions until connection restores, or (B) continue processing and reconcile discrepancies after?" This is a business decision masquerading as a technical one. CAP gives you the vocabulary to have that conversation explicitly. The theorem tells you: you cannot avoid making this choice. The only question is whether you make it deliberately or accidentally.

Element mapping:

- **Network partition** = datacenter connectivity loss
- **CP policy** = freeze all transactions during outage
- **AP policy** = continue and reconcile later
- **Reconciliation** = conflict resolution after partition heals

Where this analogy breaks down: real banks often accept "eventual consistency" for some operations (ATMs can overdraft) while requiring strong consistency for others (wire transfers). CAP applies per-operation, not per-system.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a distributed system's nodes can't talk to each other, it must choose: refuse requests (be safe but unavailable) or answer with possibly outdated info (be available but possibly wrong). You can't be both perfectly correct and always available when the network fails.

**Level 2 - How to use it (junior developer):**
Use CAP to choose your database. Financial data, inventory counts, reservations → CP (ZooKeeper, HBase, Spanner). Shopping carts, social feeds, session state → AP (Cassandra, DynamoDB, CouchDB). Cassandra lets you tune per-query: `ConsistencyLevel.ALL` → CP-like. `ConsistencyLevel.ONE` → AP.

**Level 3 - How it works (mid-level engineer):**
In Cassandra with N=3 replicas: setting `W=2, R=2` gives `W+R > N` → strong consistency (QUORUM). Setting `W=1, R=1` gives fast AP behavior. During a partition where 1 node is unreachable: QUORUM still works (majority=2 reachable). If 2 nodes unreachable: QUORUM fails → CP behavior kicks in, reads/writes return errors. The system shifts from AP to CP automatically when quorum is lost.

**Level 4 - Why it was designed this way (senior/staff):**
CAP "C" is specifically linearizability. Many systems claiming "CP" actually provide weaker forms (sequential consistency, snapshot isolation). Jepsen testing reveals this gap. PACELC extends CAP: even without partitions, latency vs. consistency is a trade-off. A CP system that takes 500ms to achieve consensus under normal operation sacrifices latency for consistency. TrueTime (Spanner's GPS+atomic-clock approach) narrows uncertainty to ~7ms, enabling globally consistent transactions with bounded (not zero) latency cost. Google Spanner is effectively "CP with very short partition windows" - the gold standard for globally distributed CP systems.

**Expert Thinking Cues:**

- "Which operations in this system require linearizability? Which can tolerate eventual consistency?"
- "What is our partition policy? Have we documented it explicitly, or will we discover it during an incident?"
- "Are we using CAP 'C' (linearizability) or a weaker form? Does our choice match our consistency requirements?"

---

### ⚙️ How It Works (Mechanism)

**CASSANDRA CONSISTENCY TUNING (CP vs AP per-operation):**

```java
@Repository
public class InventoryRepository {

    private final CqlSession session;

    // BAD: AP consistency for critical inventory - allows oversell
    public int getAvailableStock(String productId) {
        Statement q = QueryBuilder.selectFrom("inventory")
            .column("stock")
            .whereColumn("product_id")
            .isEqualTo(literal(productId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.ONE); // stale ok?
        return session.execute(q).one().getInt("stock");
    }

    // GOOD: QUORUM for inventory reads/writes - strong consistency
    public boolean reserveStock(String productId, int qty) {
        // Lightweight transaction (Paxos) for CAS semantics
        Statement cas = QueryBuilder.update("inventory")
            .setColumn("stock", QueryBuilder.raw(
                "stock - " + qty))
            .whereColumn("product_id")
            .isEqualTo(literal(productId))
            .ifColumn("stock").isGreaterThanOrEqualTo(literal(qty))
            .build()
            .setConsistencyLevel(ConsistencyLevel.SERIAL); // Paxos
        Row result = session.execute(cas).one();
        return result.getBoolean("[applied]");
    }
}
```

**PARTITION BEHAVIOR BY SYSTEM:**

```
ZooKeeper (CP):
  Leader election: requires quorum (n/2 + 1 nodes)
  Write: routed to leader, replicated to quorum, then confirmed
  Partition scenario: minority partition returns errors
  → Client sees: ConnectionLoss or SessionExpired

Cassandra (AP default, tunable):
  Partition scenario with W=1, R=1:
  → Both sides of partition accept reads/writes independently
  → Hinted handoff stores writes for unavailable node
  → Anti-entropy reconciles after partition heals
  → Last-Writer-Wins (LWW) or CRDT resolves conflicts
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PARTITION SCENARIO - DECISION FLOW:**

```
Normal: Node A <-------> Node B (replicating)

Partition detected: A and B cannot communicate
                              <- YOU ARE HERE

Decision point per system:
  CP system (ZooKeeper, HBase):
    A: quorum lost -> refuse reads/writes -> error to client
    B: quorum lost -> refuse reads/writes -> error to client

  AP system (Cassandra ONE):
    A: accepts writes, stores locally, enqueues for hinted handoff
    B: accepts writes, stores locally, enqueues for hinted handoff
    Both serve reads from local state (possibly stale)

Partition heals:
  CP: resumes normal operation, no conflicts
  AP: reconciliation phase (anti-entropy, read repair, LWW)
      Conflict resolution determines final state
```

**FAILURE PATH:**
Treating an AP system as CP (assuming reads are always fresh): inventory system on Cassandra `ConsistencyLevel.ONE` allows two nodes in a partition to each sell the last item. After reconciliation: -1 inventory. Fix: use `SERIAL` (Paxos) for inventory, or switch to a CP system.

**WHAT CHANGES AT SCALE:**
At global scale (multi-region), partition latency is measured in milliseconds to seconds (not just packet loss). Google Spanner uses TrueTime to minimize the unavailability window during partitions. CockroachDB uses Raft per range. At planetary scale, CAP trade-offs dominate every design decision.

---

### 💻 Code Example

```java
// Choosing consistency level based on operation criticality
@Service
public class CartService {

    // BAD: same consistency for all cart operations
    public void addItemCart(UUID cartId, Item item) {
        // Using ONE for everything - inconsistent under partition
        Statement s = buildAddStatement(cartId, item)
            .setConsistencyLevel(ConsistencyLevel.ONE);
        session.execute(s);
    }

    // GOOD: differentiate by business criticality
    public void addItemToCart(UUID cartId, Item item) {
        // Cart additions: AP ok (duplicates reconcilable)
        Statement s = buildAddStatement(cartId, item)
            .setConsistencyLevel(ConsistencyLevel.ONE);
        session.execute(s);
    }

    public boolean processPayment(UUID cartId, BigDecimal amount) {
        // Payment: CP required (no double-charge acceptable)
        Statement debit = buildPaymentStatement(cartId, amount)
            .setConsistencyLevel(ConsistencyLevel.SERIAL); // Paxos
        Row result = session.execute(debit).one();
        return result.getBoolean("[applied]");
    }
}
```

**How to test / verify correctness:**
Use Jepsen (https://jepsen.io) to test partition behavior. Run `jepsen.db.cassandra` with network partition injection. Verify that under partition, your consistency level produces the expected behavior (errors for CP, stale reads for AP).

---

### ⚖️ Comparison Table

| System         | CAP Type               | Partition Behavior                        | Best Use Case                      |
| -------------- | ---------------------- | ----------------------------------------- | ---------------------------------- |
| ZooKeeper      | CP                     | Returns error if quorum lost              | Leader election, config management |
| HBase          | CP                     | Pauses writes during region split         | Time-series with ACID              |
| Google Spanner | CP (bounded)           | Waits for TrueTime uncertainty            | Global financial transactions      |
| Cassandra      | AP (tunable)           | Serves stale, reconciles later            | Social feeds, user sessions        |
| DynamoDB       | AP default / CP option | Eventually consistent by default          | Shopping cart (AP), payments (CP)  |
| CouchDB        | AP                     | Multi-master, application-level conflicts | Offline-first apps                 |
| etcd           | CP                     | Requires Raft quorum                      | Kubernetes cluster state           |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CA is a valid option for distributed systems" | CA is only possible for single-node systems. Any distributed system has network communication that can partition. P is mandatory for distributed systems. CA = not distributed.                                               |
| "CAP 'C' means any form of consistency"        | CAP "C" specifically means linearizability - the strongest model. Many "consistent" databases provide weaker forms (snapshot isolation, read-your-writes) that don't qualify as CAP-C.                                        |
| "AP systems are always inconsistent"           | AP systems are eventually consistent - they converge to the correct state after partition heals. The window of inconsistency can be very short (milliseconds) with good conflict resolution.                                  |
| "You must choose CP or AP globally"            | Cassandra and DynamoDB allow per-operation tuning. The same cluster can serve AP reads (ConsistencyLevel.ONE) and CP writes (ConsistencyLevel.QUORUM). Different operations can have different policies.                      |
| "PACELC replaces CAP"                          | PACELC extends CAP by adding the latency-consistency trade-off during normal operation (no partition). They address different scenarios. CAP addresses partition behavior; PACELC covers both partition and normal operation. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Oversell on AP Inventory System**
**Symptom:** Inventory goes negative. Customers with confirmed orders can't receive product. Refunds issued.
**Root Cause:** Inventory decrement using AP consistency (ConsistencyLevel.ONE). Two nodes in a partition both serve the last unit to different customers.
**Diagnostic:**

```bash
# Cassandra: check consistency level used in queries
nodetool tpstats | grep "Dropped Messages"
# Audit application logs for ConsistencyLevel used in inventory ops
grep -r "ConsistencyLevel" src/ | grep -i "inventory\|stock"
```

**Fix:**

```java
// BAD: AP for inventory (allows oversell)
Statement s = deductStock()
    .setConsistencyLevel(ConsistencyLevel.ONE);

// GOOD: SERIAL (Paxos) for CAS - prevents oversell
Statement s = deductStock()
    .setConsistencyLevel(ConsistencyLevel.SERIAL);
// or: use CP system (Spanner, CockroachDB) for inventory
```

**Prevention:** Classify each data type as CP-required or AP-acceptable before system design. Inventory, payments → CP. Sessions, carts → AP.

---

**Failure Mode 2: ZooKeeper Leader Election Stalls on Partition**
**Symptom:** Service discovery stops working. Microservices can't find each other. Health check endpoints show timeouts.
**Root Cause:** ZooKeeper cluster loses quorum (more than n/2 nodes unreachable). ZooKeeper is CP: returns error rather than serve stale leader information.
**Diagnostic:**

```bash
# Check ZooKeeper quorum state
echo ruok | nc zookeeper-host 2181
# Should return: imok
# If no response: quorum lost
echo stat | nc zookeeper-host 2181 | grep Mode
# "follower" or "leader" = healthy; no response = partitioned
```

**Fix:** Restore network connectivity or bring enough ZooKeeper nodes back to quorum (n/2 + 1). For resilience: use odd-numbered ZooKeeper ensembles across failure domains (3 across 2 AZs is NOT sufficient - use 5 across 3 AZs).
**Prevention:** Deploy ZooKeeper ensemble across 3+ availability zones. Use 5-node ensemble for tolerance of 2 simultaneous failures.

---

**Failure Mode 3: False CP Claim Under Real Partition**
**Symptom:** Database claiming to be "strongly consistent" returns stale reads during a network partition in production. Data corruption discovered after partition heals.
**Root Cause:** Database marketing claims CP but actual implementation has edge cases (timing windows, asynchronous replication gaps) that allow stale reads under partition.
**Diagnostic:**

```bash
# Jepsen partition test (if running Jepsen CI):
lein run test --db cassandra --workload bank --nemesis partition
# Look for: "linearizability violations" in output
# Kyle Kingsbury's reports: https://jepsen.io/analyses
```

**Fix:** Run Jepsen tests against your database under your specific consistency configuration before relying on CP guarantees for critical data.
**Prevention:** Verify database consistency guarantees with Jepsen or equivalent partition testing in pre-production environments. Don't rely on vendor documentation alone.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-001 - What Is a Distributed System]] - why distribution introduces this trade-off
- [[DST-008 - Consistency Models]] - the spectrum of consistency CAP's "C" sits at the top of

**Builds On This (learn these next):**

- [[DST-007 - PACELC]] - extends CAP with the latency-consistency trade-off
- [[DST-067 - Consistency Model Selection Framework]] - applying CAP to system design decisions

**Alternatives / Comparisons:**

- [[DST-010 - Eventual Consistency]] - the AP choice's consistency model
- [[DST-014 - BASE]] - the philosophical alternative to ACID for AP systems

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ At most 2 of C, A, P simultaneously│
│               │ P is mandatory: choose C or A      │
│ PROBLEM       │ Contradictory requirements for     │
│               │ distributed system behavior        │
│ KEY INSIGHT   │ "CA" = single-node. Distributed =  │
│               │ must choose CP or AP during fault  │
│ USE WHEN      │ Choosing databases, defining       │
│               │ partition behavior policy          │
│ AVOID WHEN    │ Misapplying: CAP "C" = linearize-  │
│               │ ability, not generic "consistent"  │
│ TRADE-OFF     │ CP: error during partition vs AP:  │
│               │ stale data during partition        │
│ ONE-LINER     │ Network partitions happen; define  │
│               │ your policy before the incident    │
│ NEXT EXPLORE  │ DST-007 PACELC                     │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. P (partition tolerance) is not a choice - it's mandatory for any distributed system.
2. CP = refuses requests during partition (consistent, possibly unavailable). AP = serves stale data during partition (available, possibly inconsistent).
3. CAP "C" = linearizability specifically, not weaker consistency forms.

**Interview one-liner:**
"CAP Theorem proves that during a network partition, a distributed system must choose between consistency (refuse requests rather than serve stale data) or availability (always respond, possibly with stale data) - since partitions are inevitable, the real design decision is your partition policy: CP or AP."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every distributed system has a partition policy - whether you define it or not. An undefined partition policy is discovered during your worst production incident. The discipline of explicitly naming your partition behavior (CP or AP, per operation) before building the system is the same principle as defining error handling before writing happy-path code: correctness requires explicit handling of the failure case.

**Where else this pattern appears:**

- **Database isolation levels:** Serializable (CP-like: blocks concurrent conflicting transactions) vs. Read Committed (AP-like: allows some stale reads for throughput). Same trade-off, different layer.
- **Git merge strategy:** Rebase (linear history, CP-like: refuse to merge until all conflicts are resolved) vs. merge commit (AP-like: always produces a commit, conflicts resolved later). Distributed version control is a distributed system.
- **Network protocol design:** TCP (CP-like: requires acknowledgment, retries on loss) vs. UDP (AP-like: fire-and-forget, application handles loss). The OSI stack makes the CP/AP trade-off at the transport layer.

---

### 💡 The Surprising Truth

Eric Brewer, who proposed CAP, publicly stated in 2012 that "CAP is more subtle than it appears" and that the theorem is often misused. The biggest misconception: treating CAP as a 3-way binary choice (pick two) rather than a spectrum. Modern systems like Google Spanner are "CP with bounded partition windows" - they're not CP-or-nothing; the partition duration is measured in milliseconds. Additionally, CAP's "A" (availability) has a very specific definition (every non-failing node must respond) that most "highly available" systems don't actually satisfy - what they offer is "high availability" (99.9%+ uptime), not CAP-A. The practical insight: CAP is a theoretical framework, not a product label. Measure actual behavior under partition with Jepsen rather than trusting vendor claims.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A distributed inventory system for limited-edition sneakers (1,000 units, 50,000 concurrent buyers) must decide: CP or AP. Overselling 200 units costs $10,000 in refunds. Refusing 200 legitimate purchases costs $10,000 in lost revenue. Both failures cost the same. What does this imply about the CAP choice, and is there a hybrid approach that minimizes total cost?
_Hint:_ When both failure modes cost equally, the choice depends on which is easier to detect and recover from. Consider SERIAL (Paxos) for the last N% of inventory and AP for the bulk. What does this imply about CAP being a per-operation choice?

**Q2 (A - System Interaction):** Cassandra with `ConsistencyLevel.QUORUM` for both reads and writes (N=3, W=2, R=2) is often described as "strongly consistent." Is this CAP-consistent (linearizable)? What happens if one node returns a stale value during the quorum read - does QUORUM guarantee the latest value?
_Hint:_ QUORUM ensures overlap between write and read quorums. But consider: if a write completed on W=2 nodes and then a read contacts R=2 nodes that include 1 stale node and 1 fresh node, which value is returned? Is "latest timestamp wins" the same as linearizability?

**Q3 (E - First Principles):** The Gilbert-Lynch CAP proof assumes an asynchronous network model. In a fully synchronous network (bounded message delay), can you achieve all three CAP properties simultaneously? What does this tell you about the relationship between CAP and network assumptions?
_Hint:_ In a synchronous model with bounded delay, you can distinguish partition from slow response. This changes the fundamental impossibility. What happens to the proof when message delays have a known upper bound?
