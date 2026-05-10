---
id: DST-045
title: PACELC
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-035
used_by: DST-069
related: DST-022, DST-035, DST-036, DST-023
tags:
  - distributed
  - consistency
  - performance
  - deep-dive
  - tradeoff
  - advanced
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 22
permalink: /distributed-systems/pacelc/
---

# DST-034 - PACELC

⚡ TL;DR - PACELC extends CAP by exposing a second trade-off: even with no partition, every distributed system must choose between Latency and Consistency on every replication hop.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-022, DST-035                   |     |
| **Used by:**    | DST-069                            |     |
| **Related:**    | DST-022, DST-035, DST-036, DST-023 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
CAP Theorem changed the conversation in 2002: you can't have consistency, availability, AND partition tolerance. Engineers chose "CP" or "AP" and moved on. But in production, the question surfaced immediately: Cassandra is "AP" - fine. But should a write to Cassandra return AFTER it's replicated to one node (fast, risky) or after two nodes confirmed (slower, safer)? CAP has no answer. Both choices are still "AP".

**THE BREAKING POINT:**
A team building a recommendation engine and a banking ledger both chose Cassandra (AP). The recommendation engine needs sub-10ms writes; the ledger needs every write confirmed before returning. CAP says both are fine — but they need opposite replication behavior. Engineers realise CAP only models partition behavior. The non-partition case (which is 99.99% of operating time) is completely absent from the model.

**THE INVENTION MOMENT:**
Daniel Abadi published PACELC in 2012, extending CAP with the `E` (Else) branch: when there is NO partition, the system still faces a trade-off between Latency and Consistency. A replication operation is fundamentally: you can return fast (before replication completes) or return after confirmation (slow but consistent). There is no third option.

**EVOLUTION:**
2002: CAP (Brewer/Gilbert-Lynch). 2012: PACELC (Abadi) - adds EL/EC axis. 2013: Abadi refines with concrete database classifications. 2015+: Cloud database vendors begin using PACELC vocabulary in docs (DynamoDB, Cosmos DB, CockroachDB). 2020: PACELC influences Cosmos DB's five consistency levels — a direct mapping of the EL↔EC spectrum.

---

### 📘 Textbook Definition

**PACELC** is a theoretical framework by Daniel Abadi (2012) that extends the CAP Theorem. It states: in the presence of a network **P**artition, a distributed system must choose between **A**vailability and **C**onsistency (the CAP trade-off); **E**lse (no partition), the system must choose between **L**atency and **C**onsistency. Systems are classified as PA/EL, PA/EC, PC/EL, or PC/EC based on their choices in both scenarios. PC/EL (partition consistent AND low latency) is theoretically possible but extremely rare in practice.

---

### ⏱️ Understand It in 30 Seconds

**One line:** CAP covers partition behavior; PACELC also covers the normal (non-partition) case where replication latency is the real daily trade-off.

> Think of a relay race with two batons (data copies). During a storm (partition), you decide: wait for both runners to finish (CP) or declare a winner immediately (AP). But even on sunny days (no partition), you still decide: do you wait for the second runner to confirm receipt before signaling success? PACELC adds the sunny-day question.

**One insight:** The EL/EC trade-off exists on EVERY WRITE in a replicated system, every millisecond of every day — regardless of partitions. CAP's partition scenario is rare. PACELC's EL/EC trade-off is constant.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Replication requires communication between nodes over a network.
2. Networks have non-zero latency; replication is never instantaneous.
3. Any write must either: (a) return before replication completes (low latency, possible stale reads) or (b) return after replication confirms (higher latency, consistent reads).
4. These two behaviors are mutually exclusive for a given operation.
5. Partitions are rare; the EL/EC choice applies to 100% of operations.

**DERIVED DESIGN:**
A system classified as PA/EL: during partition, prefer availability; during normal operation, prefer low latency (async replication). Example: Cassandra with `ONE` consistency level.
A system classified as PC/EC: during partition, prefer consistency; during normal operation, wait for quorum before returning. Example: Spanner.

**THE TRADE-OFFS:**
**Gain (EL):** Writes return in microseconds; no waiting for cross-datacenter replication. Throughput is maximized.
**Cost (EL):** A read immediately after a write may see the old value. Conflict resolution required for concurrent writes.
**Gain (EC):** Read-your-writes guaranteed. No stale data visible to any client.
**Cost (EC):** Every write waits for replication acknowledgment. Latency is bounded by slowest replica or network RTT.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The physical delay of replication is irreducible. You must choose when to declare a write "done."
**Accidental:** Many systems add their own consistency protocols on top (vector clocks, Paxos, CRDT merge) that increase complexity beyond the fundamental EL/EC choice.

---

### 🧪 Thought Experiment

**SETUP:** You're building a global key-value store with nodes in US-East and EU-West. Round-trip latency between them is 120ms. Every write goes to both regions.

**WHAT HAPPENS WITHOUT PACELC (CAP-only thinking):**
You pick "AP" (available during partition). Done. But then your product manager asks: "Should writes to the US node immediately return, or wait 120ms for the EU node to confirm?" CAP doesn't answer this. You flip a coin, choose async replication. Six months later, a user in the EU reads a value 200ms after the US write and gets the old value. Incident ticket created. "We're AP, expected!" is an unsatisfying answer.

**WHAT HAPPENS WITH PACELC:**
You explicitly model both choices. PA/EL: US write returns immediately, EU gets the update asynchronously — EU users may see stale data for up to 500ms. PA/EC: US write waits for EU confirmation before returning — 120ms added to every write, but global consistency guaranteed. You make a deliberate choice, document it, and tune your SLAs accordingly.

**THE INSIGHT:** PACELC forces the conversation that CAP deferred. The EL/EC choice is the most frequent architectural decision in distributed system operations — it happens on every write.

---

### 🧠 Mental Model / Analogy

> PACELC is a two-clause contract: the partition clause (CAP) and the normal-operations clause (EL/EC). Most employment contracts have a termination clause AND day-to-day terms. The CAP theorem was only the termination clause. PACELC adds the operational terms.

**Mapping:**

- **Termination clause (partition clause)** → P: A vs C (what happens during crisis)
- **Day-to-day terms (normal operations)** → E: L vs C (what happens every working day)
- **PA/EL employee** → "During a crisis I'll keep working at any cost. Day-to-day I move fast and skip confirmation emails."
- **PC/EC employee** → "During a crisis I'll wait for management sign-off. Day-to-day I CC everyone and wait for approval."

Where this analogy breaks down: a real employee can switch behavior dynamically; most databases have a fixed configuration that determines their PACELC class.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you save data to a cloud app, the app secretly copies that data to backup servers. PACELC asks: does the app tell you "saved!" immediately (fast but the backup might not have it yet) or only after the backup confirms (slower but guaranteed)? You're always making this choice, even when nothing is broken.

**Level 2 - How to use it (junior developer):**
Use the PACELC class of your database to choose the right consistency level. Cassandra (PA/EL) → use `QUORUM` or `ALL` when you need EC-like behavior; use `ONE` for EL-like behavior. DynamoDB → enable strongly consistent reads for EC; use eventually consistent reads for EL. PACELC is why your database has these knobs.

**Level 3 - How it works (mid-level engineer):**
PACELC classifies systems on two axes independently. A system can be PA/EC: AP during partition but synchronous replication during normal ops. MongoDB with `writeConcern: majority` is PC/EC; with `writeConcern: 1` it's PC/EL. The E branch is determined by replication acknowledgment policy: synchronous (EC) vs. asynchronous (EL). Key metric: replication lag. Zero lag = EC; non-zero lag = EL (bounded or unbounded).

**Level 4 - Why it was designed this way (senior/staff):**
CAP's partition scenario is provably rare but theoretically important. Abadi's insight was that EL vs EC is the practical daily trade-off that actually determines user-observable behavior. Spanner's TrueTime eliminates the EL/EC dilemma through external clock synchronization and commit-wait — it's PC/EC without the typical 2x RTT penalty of two-phase commit. Azure Cosmos DB's five consistency levels (Strong, Bounded Staleness, Session, Consistent Prefix, Eventual) are a direct interpolation along the EC→EL spectrum. PACELC provides the theoretical foundation for offering a continuum rather than a binary.

**Expert Thinking Cues:**

- "What's your replication acknowledgment policy?" is the PACELC EL/EC question.
- "What consistency level are you using?" in Cassandra/DynamoDB maps directly to EL/EC.
- "What's your replication lag P99?" quantifies how far from EC the system is.
- "Can you tolerate read-your-writes latency?" determines if EL is acceptable.

---

### ⚙️ How It Works (Mechanism)

**PA/EL (Cassandra, DynamoDB default, CouchDB):**

1. Client sends write to coordinator node.
2. Coordinator writes to local node, returns `200 OK` immediately.
3. Asynchronously replicates to other nodes in the background.
4. Other nodes may have old value for up to `hinted_handoff_window_time`.
5. Reads from any node may return stale data within that window.

**PC/EC (Spanner, etcd, ZooKeeper):**

1. Client sends write to leader node.
2. Leader initiates Paxos/Raft round, replicates to quorum.
3. Only after quorum acknowledges does leader commit and return to client.
4. All subsequent reads see this committed value.
5. Latency = network RTT to quorum (can be 10ms–200ms for cross-region).

**Tunable systems (Cassandra with QUORUM, MongoDB with writeConcern):**
The system is PA/EL by default but can be configured per-operation toward EC:
`consistency_level = QUORUM` → W + R > N → strong consistency guaranteed.
`consistency_level = ONE` → EL: returns after single node write.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (PA/EL - Cassandra QUORUM write):**

```
Client
  │
  ▼
Coordinator Node
  │── Write local commit log ──────────▶ SUCCESS
  │
  ├──▶ Node A (replica) ──▶ ACK
  │                             │
  ├──▶ Node B (replica) ──▶ ACK◄── QUORUM
  │                                  met
  ▼
Return 200 to client (EL: wait
for quorum, not ALL)
  │
  └──▶ Node C (async, eventual)
       ← YOU ARE HERE (EL boundary)
```

**FAILURE PATH:**
If Node A and Node B are both slow (GC pause), the write blocks waiting for quorum. Client timeout. Coordinator: hinted handoff queues the write. When nodes recover, handoff delivers. During outage window: EL read may return stale.

**WHAT CHANGES AT SCALE:**
At 10k writes/sec, the difference between EL (1ms local commit) and EC (120ms cross-region) is 120x write throughput. At continental scale, EC = accepting 120ms minimum write latency. Teams at this scale typically partition data: EL for user activity streams, EC for financial balances. Same database, different consistency levels per operation type.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Concurrent writes to the same key in PA/EL: Last-Write-Wins (LWW) by default. Two clients writing concurrently from US-East and EU-West both "succeed" — the lower timestamp write is silently discarded. In PC/EC: one write blocks the other at the Raft/Paxos layer. No silent data loss.

---

### 💻 Code Example

**BAD - Ignoring PACELC class mismatch:**

```java
// Using Cassandra for financial account balance
// Default: PA/EL (async replication)
PreparedStatement stmt = session.prepare(
    "UPDATE accounts SET balance = ? WHERE id = ?"
);
// No consistency level set → ONE (EL behavior)
session.execute(stmt.bind(newBalance, accountId));
// Immediately read back:
Row row = session.execute(
    "SELECT balance FROM accounts WHERE id = ?",
    accountId
).one();
// DANGER: May read pre-update balance from replica!
// This is EA/EL mismatch for financial data
```

**GOOD - Explicit PACELC classification per operation:**

```java
// PA/EL for non-critical operations (analytics events)
private static final ConsistencyLevel ANALYTICS_CL =
    ConsistencyLevel.ONE;          // EL: fast, can lose

// PC/EC for financial operations
private static final ConsistencyLevel FINANCIAL_CL =
    ConsistencyLevel.QUORUM;       // EC: W+R > N

public void recordPageView(String userId, String page) {
    // EL is fine: losing a pageview is acceptable
    session.execute(
        SimpleStatement.builder(INSERT_PAGEVIEW)
            .setConsistencyLevel(ANALYTICS_CL)
            .build(),
        userId, page
    );
}

public void debitAccount(String accountId, long amount)
    throws InsufficientFundsException {
    // EC required: read-your-writes for balance
    Row current = session.execute(
        SimpleStatement.builder(SELECT_BALANCE)
            .setConsistencyLevel(FINANCIAL_CL)
            .build(),
        accountId
    ).one();
    long balance = current.getLong("balance");
    if (balance < amount) throw new InsufficientFundsException();
    session.execute(
        SimpleStatement.builder(UPDATE_BALANCE)
            .setConsistencyLevel(FINANCIAL_CL)
            .build(),
        balance - amount, accountId
    );
}
```

**How to test / verify correctness:**

```bash
# Measure replication lag (EL evidence):
nodetool tpstats | grep -A5 "ReadRepair"
nodetool cfstats keyspace.table | grep "Bloom filter"

# Verify quorum is achieving EC semantics:
# Write with QUORUM, immediately read with QUORUM
# from a different node — both must return same value
cqlsh -e "CONSISTENCY QUORUM; UPDATE ...; SELECT ...;"
```

---

### ⚖️ Comparison Table

| System        | CAP Class | PACELC Class | EL/EC Default | Tunable?           |
| ------------- | --------- | ------------ | ------------- | ------------------ |
| Cassandra     | AP        | PA/EL        | EL (ONE)      | Yes (per-op CL)    |
| DynamoDB      | AP        | PA/EL        | EL (eventual) | Yes (per-read)     |
| CouchDB       | AP        | PA/EL        | EL            | Limited            |
| MongoDB       | CP        | PC/EC        | EC (primary)  | Yes (writeConcern) |
| ZooKeeper     | CP        | PC/EC        | EC            | No                 |
| etcd          | CP        | PC/EC        | EC            | No                 |
| Spanner       | CP        | PC/EC        | EC (TrueTime) | No                 |
| Cosmos DB     | AP        | PA/EL→PC/EC  | Configurable  | 5 levels           |
| HBase         | CP        | PC/EC        | EC            | No                 |
| Redis Cluster | AP        | PA/EL        | EL (async)    | Limited            |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                              |
| :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "PACELC replaces CAP"                          | PACELC extends CAP; CAP's partition clause is unchanged. PACELC adds the non-partition trade-off. Both models are useful.                                                                                            |
| "PA/EL means the system is unreliable"         | EL means low latency, not unreliable. DNS is PA/EL and is one of the most reliable systems on the internet.                                                                                                          |
| "PC/EC systems are always strongly consistent" | "EC" in PACELC means the system prioritizes consistency during normal ops — but the strength of that consistency (linearizable vs. sequential) is a separate dimension.                                              |
| "You must pick one PACELC class forever"       | Tunable systems (Cassandra, DynamoDB, Cosmos DB) let you choose EL or EC per operation. Your PACELC class is per-request, not per-cluster.                                                                           |
| "Low latency requires eventual consistency"    | Google Spanner achieves PC/EC with median write latency of ~5ms within a region. Bounded staleness in Cosmos DB offers EL-like latency with EC-like guarantees. The trade-off is real but not as binary as it seems. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Silent Data Loss from PA/EL Misconfiguration**

**Symptom:** Users report "I saved my changes but they disappeared after page refresh." Intermittent, affects ~0.1% of operations.
**Root Cause:** Application uses Cassandra with `ConsistencyLevel.ONE` (EL). Write confirmed on one node, that node crashes before replication. Hinted handoff stores the write on coordinator, but coordinator also fails within the hint window.
**Diagnostic:**

```bash
nodetool tpstats | grep HintedHandoff
# Check if hints are being dropped:
grep "HintedHandoffMetrics" system.log | tail -50
nodetool getendpointsnitial  # verify replica count
```

**Fix:**
BAD: `ConsistencyLevel.ONE` for user-visible data.
GOOD: `ConsistencyLevel.QUORUM` for data requiring durability.
**Prevention:** Classify data by durability requirement at design time. Apply minimum consistency level policy in code review.

**Failure Mode 2: Thundering-Herd Latency from EC Under Load**

**Symptom:** Write latency spikes from 5ms to 800ms under peak traffic. P99 breaches SLA. System-wide slowdown.
**Root Cause:** PC/EC system requires quorum acknowledgment. Under load, one replica GC-pauses for 200ms. All writes waiting for that replica's quorum ACK stall. Cascading: slow writes queue up, coordinator timeouts trigger retries, amplifying load.
**Diagnostic:**

```bash
nodetool tpstats | grep -A3 "Mutation"
# Look for large "Pending" counts:
nodetool tpstats | awk '/Mutation/{found=1} found && /Pending/{print; found=0}'
# Check GC logs on replicas:
grep "GC pause" /var/log/cassandra/system.log | tail -20
```

**Fix:**
BAD: Using QUORUM uniformly across all operations during peak load.
GOOD: Implement circuit breaker — degrade to EL under load for non-critical paths, keep EC only for financial operations.
**Prevention:** Load test with EC consistency requirements. Size replicas to absorb GC pauses without quorum impact.

**Failure Mode 3: Security - Stale Data in Authorization Checks**

**Symptom:** A user's access is revoked at 14:00. At 14:01, they still access a protected resource.
**Root Cause:** Authorization service uses PA/EL for permission reads. Revocation written to primary, not yet replicated to the replica serving the auth check. Within the replication window (~500ms), revoked permissions are still served.
**Diagnostic:**

```bash
# Measure replication lag for the permissions table:
# Read from primary and replica, compare timestamps
cqlsh -e "SELECT writetime(permissions) FROM acl.permissions \
  WHERE user_id='<id>' USING CONSISTENCY LOCAL_ONE;"
# Run same query on two hosts and compare
```

**Fix:**
BAD: `ConsistencyLevel.ONE` for security-sensitive reads.
GOOD: `ConsistencyLevel.ALL` or `QUORUM` for permission reads. Or route all auth reads to primary (PC/EC semantics).
**Prevention:** Security-sensitive data paths must use EC consistency. Document this as a security requirement, not a performance option.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - CAP Theorem (the partition trade-off PACELC extends)
- DST-035 - Consistency Models (what EC vs EL consistency actually means)
- DST-024 - Replication Strategies (how data is copied between nodes)

**Builds On This (learn these next):**

- DST-036 - Strong Consistency (deep dive into PC/EC behavior)
- DST-023 - Eventual Consistency (deep dive into PA/EL behavior)
- DST-069 - Consistency Level Selection (practical guide using PACELC)

**Alternatives / Comparisons:**

- DST-022 - CAP Theorem (complementary model, partition-focused)
- DST-035 - Consistency Models (broader consistency taxonomy beyond PACELC)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Extension of CAP: adds EL/EC   |
|                  | trade-off for normal operation |
+------------------+--------------------------------+
| PROBLEM SOLVED   | CAP only models partition case;|
|                  | PACELC covers 99.99% of ops    |
+------------------+--------------------------------+
| KEY INSIGHT      | Every replication must choose: |
|                  | return fast (EL) or wait (EC)  |
+------------------+--------------------------------+
| USE WHEN         | Classifying DB behavior, tuning|
|                  | per-operation consistency level|
+------------------+--------------------------------+
| AVOID WHEN       | Simple single-node systems or  |
|                  | in-memory caches (no repl)     |
+------------------+--------------------------------+
| TRADE-OFF        | EL: ms latency, stale reads    |
|                  | EC: consistent, +100ms writes  |
+------------------+--------------------------------+
| ONE-LINER        | PA/EL = fast+eventually-consis |
|                  | PC/EC = slow+always-consistent |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-035 Consistency Models,    |
|                  | DST-036 Strong Consistency     |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. PACELC = CAP + the normal-operations (Else) trade-off: Latency vs Consistency.
2. PA/EL and PC/EC are the dominant classes; PA/EC and PC/EL exist but are rare.
3. Many databases are tunable — you can choose EL or EC per operation, not just per cluster.

**Interview one-liner:**
"PACELC extends CAP by adding the latency-consistency trade-off that exists even when there's no partition — during normal operation, every replication must choose between returning fast (EL) or waiting for consistency confirmation (EC), and most real-world performance problems are EL/EC mismatches, not CAP partition events."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every system with asynchronous communication has a PACELC-class decision embedded in it, whether acknowledged or not. Making this decision explicit — per operation, per data type, per SLA tier — is the difference between a system that degrades gracefully and one that fails mysteriously. Explicit trade-off decisions are always better than implicit defaults.

**Where else this pattern appears:**

- **Async messaging (Kafka producer acks):** `acks=0` is EL (fire-and-forget); `acks=all` is EC (wait for all ISR replicas). The PACELC trade-off is right there in the Kafka producer config.
- **HTTP caching (Cache-Control headers):** `must-revalidate` is EC (always check origin before serving); `stale-while-revalidate` is EL (serve stale, update in background). Web caching is a PACELC system.
- **Git fetch vs pull:** `git fetch` is EL (get data, don't apply); `git pull` with rebase is closer to EC (consistent local state). Distributed version control has the same latency/consistency trade-off.

---

### 💡 The Surprising Truth

PACELC predicts that PC/EL (partition-consistent AND low-latency during normal ops) should be nearly impossible — yet Google Spanner achieves it. The trick: TrueTime. Spanner uses GPS receivers and atomic clocks to bound clock uncertainty to ±7ms globally. By waiting `2ε` (twice the uncertainty bound) after a write before returning, Spanner guarantees linearizability WITHOUT requiring synchronous cross-datacenter replication ACKs. It's not that Spanner violates PACELC; it's that Spanner engineers bought a GPS infrastructure to shrink the EL/EC trade-off to near-zero. The insight: PACELC trade-offs can be engineered around — at sufficiently high infrastructure cost.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A ride-sharing app needs to track driver locations globally across 3 regions (US, EU, APAC). Location updates arrive 60 times per second per driver. Riders need to see driver locations within 2 seconds. Which PACELC class is most appropriate for the location data store, and why? What happens if you mistakenly choose PC/EC?
_Hint:_ Think about write amplification: 60 writes/sec × number of drivers × cross-region RTT. At what point does the EC latency requirement become physically impossible to satisfy?

**Q2 (A - System Interaction):** Cassandra uses PA/EL by default. When you set `ConsistencyLevel.QUORUM` for both reads and writes (N=3, W=2, R=2), you're forcing EC behavior on a PA/EL system. Is this the same as running a PC/EC system? What edge cases exist where QUORUM on a PA/EL system differs from a native PC/EC system like ZooKeeper?
_Hint:_ Consider what happens during a network partition when using QUORUM on Cassandra vs. ZooKeeper. Which one will accept a QUORUM write from the smaller partition side?

**Q3 (B - Scale):** Azure Cosmos DB offers 5 consistency levels: Strong, Bounded Staleness, Session, Consistent Prefix, and Eventual. Map each level to its approximate PACELC position on the EL↔EC spectrum. Which level best represents the "PC/EC" class? Is "Session" consistency closer to EL or EC, and what makes it useful despite not being EC?
_Hint:_ Session consistency guarantees read-your-writes for a single client session. Is that the same as EC? What happens when two different sessions write to the same key concurrently?
