---
layout: default
title: "Read Repair"
parent: "Distributed Systems"
nav_order: 624
permalink: /distributed-systems/read-repair/
number: "624"
category: Distributed Systems
difficulty: ★★★
depends_on: "Eventual Consistency, Quorum Reads, Anti-Entropy"
used_by: "Cassandra, DynamoDB, Riak, Voldemort"
tags: #advanced, #distributed, #consistency, #repair, #replication
---

# 624 — Read Repair

`#advanced` `#distributed` `#consistency` `#repair` `#replication`

⚡ TL;DR — **Read repair** is an inline consistency mechanism: when a read coordinator queries multiple replicas, detects stale data on some replicas, and immediately repairs them — **foreground** (blocking, before responding) or **background** (async, after responding).

| #624            | Category: Distributed Systems                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Eventual Consistency, Quorum Reads, Anti-Entropy |                 |
| **Used by:**    | Cassandra, DynamoDB, Riak, Voldemort             |                 |

---

### 📘 Textbook Definition

**Read repair** is a consistency mechanism in distributed databases where the read path coordinator — after querying multiple replicas to satisfy a quorum read — compares the returned values, detects divergence, and writes the most recent value back to any replicas that returned stale data. It is a **reactive, on-the-read-path** repair (complementing **anti-entropy**, which is proactive and background). Two modes: (1) **Foreground read repair** — the coordinator blocks the client response until all replicas are repaired. Stronger consistency guarantee; higher read latency. (2) **Background read repair** — coordinator returns the most recent value to the client immediately, then asynchronously repairs stale replicas. Lower latency; eventual consistency. Cassandra: `read_repair_chance` (per table) controls probability of background read repair on non-coordinator-specified reads. DynamoDB: read repair is internal, automatic. Limitation: read repair only fixes data that's actually read — cold data never read may remain divergent (anti-entropy handles that).

---

### 🟢 Simple Definition (Easy)

You have 3 copies of a document. When you read it, the system checks all 3 copies. Copy 2 is outdated. The system has two options: (1) Fix copy 2 before giving you the document (foreground — correct, slower). (2) Give you the document immediately, then fix copy 2 in the background (background — faster, eventually consistent). Either way: next person to read the document gets consistent data from all 3 copies. Problem: if no one reads the document for 6 months, copy 2 stays outdated — that's why anti-entropy (background repair) also runs periodically.

---

### 🔵 Simple Definition (Elaborated)

Read repair only fires during reads. For hot data (frequently read): read repair keeps replicas in sync quickly. For cold data (rarely read): replicas can diverge indefinitely — only anti-entropy catches it. Read repair is "free" repair: you're already reading from multiple replicas for quorum; comparing responses and repairing costs minimal extra work. Key configuration: read_repair_chance = 0.1 means 10% of qualifying reads trigger background repair. Balance: too high = extra write I/O on every read (read-heavy clusters impacted). Too low = cold replicas stay stale longer (rely on anti-entropy).

---

### 🔩 First Principles Explanation

**Quorum read, divergence detection, repair decision, and Cassandra internals:**

```
READ REPAIR MECHANICS:

  SETUP:
    Replication factor (RF) = 3. Read consistency = QUORUM (needs ceil(3/2) = 2 responses).
    Key: "user:alice". Replica nodes: A, B, C.

    State of replicas:
      Node A: user:alice = {name: "Alice Smith", version: 5}
      Node B: user:alice = {name: "Alice Smith", version: 5}  ← consistent
      Node C: user:alice = {name: "Alice Jones", version: 3}  ← STALE (missed write at version 4, 5)

  QUORUM READ REQUEST:
    Client: READ user:alice WITH QUORUM.
    Coordinator: sends read request to ALL 3 replicas (not just 2, to enable repair).
    Wait: for all 3 to respond (or timeout).

  DIVERGENCE DETECTION:
    Node A: returns version 5.
    Node B: returns version 5.
    Node C: returns version 3.

    Coordinator compares: A and B agree (version 5). C differs (version 3).
    Most recent = version 5 (highest version/timestamp). Return to client.

  REPAIR DECISION:
    Node C: stale. Must be repaired with version 5 data.

  FOREGROUND READ REPAIR:
    Coordinator: writes {name: "Alice Smith", version: 5} to Node C.
    WAITS for Node C to confirm write.
    THEN: returns version 5 to client.
    Latency: read latency + repair write latency. Slower.
    Stronger guarantee: by the time client gets response, ALL replicas are consistent.

  BACKGROUND READ REPAIR:
    Coordinator: immediately returns version 5 to client.
    Async: sends repair write to Node C in background.
    Latency: just read latency. Faster.
    Eventual: Node C repaired shortly after, but client may read stale data from C briefly.

  DIGEST READ (OPTIMIZATION):
    Full read repair as above: sends full data to coordinator from all replicas. Expensive.

    Optimization: Coordinator sends 1 full read request (to fastest replica) + 2 digest requests.
    Digest request: replica returns HASH of data, not full data.

    If digest matches: data is consistent. Return full data from primary. No repair needed.
    If digest differs: coordinator fetches full data from all replicas. Identifies stale node. Repairs.

    BENEFIT: 90%+ of reads consistent → only digest transferred (small). Full data fetched rarely.
    Cassandra: uses digest reads by default.

READ_REPAIR_CHANCE IN CASSANDRA:

  Two settings per table:

  1. read_repair_chance (DEPRECATED in Cassandra 4.0+):
     Probability (0.0 to 1.0) of doing background repair on reads below consistency requirement.
     e.g., 0.1 = 10% of reads trigger background repair.

  2. dclocal_read_repair_chance (DEPRECATED in Cassandra 4.0+):
     Same but limited to local datacenter replicas.

  CASSANDRA 4.0+ CHANGE:
     read_repair_chance removed (always 0). Rationale:
     - Background repair interferes with performance unpredictably.
     - Relies on read traffic to repair cold data (wrong approach).
     - Better: run explicit anti-entropy repair on schedule.

     Foreground read repair: still happens automatically on quorum+ reads that detect divergence.

  ALTER TABLE users WITH read_repair_chance = 0.1;  -- Cassandra 3.x
  -- Cassandra 4.0: this setting has no effect.

WHEN READ REPAIR TRIGGERS:

  Conditions for read repair in Cassandra:
    1. Consistency level requires reading from multiple replicas (QUORUM, ALL, LOCAL_QUORUM).
    2. Coordinator fetches from all replicas, not just required quorum.
    3. Divergence detected on comparison.

  Consistency = ONE: reads from single replica. No comparison. No read repair. (Even if other replicas stale.)
  Consistency = QUORUM: reads from 2 (of 3). Reads from all 3. Compares. Repairs stale if found.
  Consistency = ALL: reads from all 3. Compares. Repairs stale if found.

READ REPAIR VS ANTI-ENTROPY COMPARISON:

  Feature               | Read Repair            | Anti-Entropy
  ----------------------|------------------------|----------------------------
  Trigger               | On read                | Scheduled background job
  Data covered          | Only data that's read  | ALL data (including cold)
  Latency impact        | Yes (reads)            | Yes (background I/O)
  Mechanism             | Compare quorum results | Merkle tree comparison
  Repairs               | Single key/row         | Token range (batch)
  Best for              | Hot data               | Cold data, full coverage
  Guarantees            | Active data consistent | All data consistent

  COMPLEMENTARY: run BOTH. Read repair: keeps hot data consistent in real time.
  Anti-entropy: ensures cold data doesn't drift forever.

DYNAMODB READ REPAIR:

  DynamoDB: 3 replicas per partition (partition keys map to physical partitions).
  Strongly consistent reads: reads from leader replica. No read repair needed.
  Eventually consistent reads: reads from any replica.

  Internal read repair:
    DynamoDB: automatically detects stale replicas.
    Background: repairs stale replicas without client involvement.
    Transparent to user. Not configurable.

PERFORMANCE IMPLICATIONS:

  Read repair cost: extra write per repair.
  For write-heavy clusters: reads infrequently trigger repair (data usually consistent).
  For read-heavy clusters: reads may frequently trigger repair writes → extra I/O.

  MONITORING:
    Cassandra JMX metric: ReadRepair.Attempted, ReadRepair.Repaired.
    Alert: high ReadRepair.Repaired / ReadRepair.Attempted ratio → frequent divergence → investigate replica lag or node issues.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT read repair:

- Quorum reads: client gets correct data (majority agrees), but stale replicas stay stale indefinitely
- Next reader that hits the stale replica: gets outdated data
- Only full anti-entropy repair (expensive, scheduled) would fix it

WITH read repair:
→ Each read automatically heals stale replicas as a side effect
→ Hot data keeps all replicas consistent with minimal extra overhead
→ Complements anti-entropy: hot path is self-healing; cold path handled by scheduled repair

---

### 🧠 Mental Model / Analogy

> A pharmacist filling a prescription checks three copies of the patient's medication record. Two say "penicillin allergy." One says no allergies (outdated). The pharmacist uses the two-agree version (penicillin allergy), and immediately updates the outdated record before proceeding. Or: fills the prescription immediately and leaves a note for staff to update the outdated record later. Either way: the next pharmacist won't encounter the wrong record.

"Three medication records" = three replicas
"Two agree on penicillin allergy" = quorum agreement on most recent value
"Outdated record" = stale replica
"Update before proceeding" = foreground read repair
"Leave note for staff" = background read repair

---

### ⚙️ How It Works (Mechanism)

```
READ REPAIR FLOW (CASSANDRA, QUORUM READ):

  1. Client: READ key="user:alice" CONSISTENCY QUORUM.
  2. Coordinator: sends read to ALL replicas (not just quorum subset).
  3. Full read from 1 replica + digest read from others.
  4. Digest comparison: match → return full read result. Done.
  5. Digest mismatch → coordinator fetches full data from all replicas.
  6. Compare timestamps/versions: identify most recent.
  7. Return most recent to client.
  8. Foreground: write most recent to stale replicas. Wait. (Higher latency.)
     Background: write most recent to stale replicas async. (Lower latency.)
```

---

### 🔄 How It Connects (Mini-Map)

```
Quorum Reads (read from multiple replicas → enables comparison)
        │
        ▼ (detects divergence inline)
Read Repair ◄──── (you are here)
(reactive, on read path — repairs active/hot data)
        │
        ├── Anti-Entropy: proactive, background — repairs ALL data (including cold)
        ├── Hinted Handoff: reactive, on write path — repairs missed writes on node recovery
        └── Digest Reads: optimization — hash comparison before full data fetch
```

---

### 💻 Code Example

```java
// Simplified read-repair-aware quorum read:
public Value readWithRepair(String key, List<Replica> replicas) {
    int quorum = (replicas.size() / 2) + 1;

    // Fetch from ALL replicas (not just quorum) to enable repair:
    List<ReplicaResponse> responses = replicas.parallelStream()
        .map(r -> r.read(key))
        .collect(Collectors.toList());

    // Need at least quorum responses to proceed:
    long successCount = responses.stream().filter(r -> r.success).count();
    if (successCount < quorum) throw new ConsistencyException("Quorum not met");

    // Find most recent value (highest timestamp):
    Value mostRecent = responses.stream()
        .filter(r -> r.success)
        .map(r -> r.value)
        .max(Comparator.comparing(v -> v.timestamp))
        .orElseThrow();

    // Identify stale replicas (returned an older value):
    List<Replica> staleReplicas = new ArrayList<>();
    for (int i = 0; i < replicas.size(); i++) {
        if (responses.get(i).success &&
            responses.get(i).value.timestamp < mostRecent.timestamp) {
            staleReplicas.add(replicas.get(i));
        }
    }

    // Background repair: repair stale replicas asynchronously:
    if (!staleReplicas.isEmpty()) {
        executorService.submit(() -> {
            for (Replica stale : staleReplicas) {
                stale.write(key, mostRecent); // Repair with most recent value.
                repairCounter.increment();    // Track repair rate.
            }
        });
    }

    return mostRecent; // Return to client immediately (background repair).
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read repair ensures strong consistency                                 | Read repair is an eventually-consistent mechanism. Background read repair: client gets a correct value, but the stale replica isn't repaired before the next read from another client may hit it. Foreground read repair: ensures all replicas consistent BEFORE responding, but still doesn't prevent stale reads from other clients that already sent a request before repair completes. For strong consistency: use linearizable reads (Cassandra LWT, ZooKeeper, Raft) |
| Setting read_repair_chance=1.0 is a good idea for a read-heavy cluster | read_repair_chance=1.0 means every read triggers a background write to all stale replicas. In a read-heavy cluster: this converts every read into a read+write, potentially doubling I/O. Also: most reads won't find stale data (most data is consistent), so most repair writes are wasted. Anti-entropy repair on schedule: more efficient for ensuring consistency of cold data                                                                                        |
| Read repair works with consistency ONE reads                           | Consistency ONE reads query only one replica. No comparison. No divergence detection. No read repair. Read repair requires reading from multiple replicas to detect divergence. If you need read repair: use QUORUM or higher consistency                                                                                                                                                                                                                                  |

---

### 🔥 Pitfalls in Production

**Read repair causes write amplification on a read-heavy cluster:**

```
SCENARIO:
  Cassandra cluster with 3 replicas, RF=3, read_repair_chance=0.1 (default).
  Load: 100,000 reads/second. 10% trigger background read repair = 10,000 repair checks/sec.
  Typical divergence: 2% of those actually need repair = 200 repair writes/sec.

  Seems small: 200 writes/sec.

  But: repair write = write to potentially 2 stale replicas each = 400 write operations/sec.
  Plus: read repair first fetches FULL data from all replicas (not digest) when mismatch detected.
  Total extra I/O per repair event: read 3x + write 2x = 5x the normal read I/O.

  At 10,000 repair checks/sec where 2% trigger: 200 * 5x = 1000 equivalent reads/sec extra I/O.
  On a 100k read/sec cluster: 1% overhead. Fine.

  But: during traffic spike (500k reads/sec): 50k repair checks/sec, 1000 repair writes/sec, 5k equivalent I/O.
  Repair I/O: 5% of total. Noticeable latency increase during already-peak load.

BAD: read_repair_chance=0.1 on a 500k reads/sec cluster with frequent divergence.
  -- Background repair writes pile up. Compaction triggered more often.
  -- Read latency spikes during peak (repair writes block on compaction).

FIX 1: Lower or disable read_repair_chance and rely on nodetool repair:
  ALTER TABLE high_traffic_table WITH read_repair_chance = 0.0;
  -- Foreground read repair: still fires automatically when quorum reads detect divergence.
  -- Background read_repair_chance: disabled. No random extra writes.
  -- Schedule nodetool repair: daily (incremental). Covers cold data.

FIX 2: Use Cassandra 4.0+:
  -- read_repair_chance deprecated. No longer supported. Forced to 0.0.
  -- Foreground read repair: still happens on divergence detection.
  -- Scheduled repair: use Reaper for automated incremental repair.

FIX 3: If foreground read repair latency is a problem:
  -- Move to eventual consistency: read_repair = false (Cassandra read repair setting in some configs).
  -- Accept slight divergence on reads. Run anti-entropy more frequently to compensate.
  -- Trade: lower read latency vs. slightly looser consistency window.

MONITORING REPAIR RATE:
  JMX: org.apache.cassandra.metrics:type=ReadRepair,name=RepairedBlocking  // Foreground repairs
  JMX: org.apache.cassandra.metrics:type=ReadRepair,name=RepairedBackground // Background repairs
  JMX: org.apache.cassandra.metrics:type=ReadRepair,name=ReconcileRead       // Repair events

  Alert: RepairedBlocking rate increasing → replicas diverging → investigate.
  Alert: ReadRepair rate > 5% of reads → replica health issue.
```

---

### 🔗 Related Keywords

- `Anti-Entropy` — proactive background repair (counterpart to reactive read repair)
- `Hinted Handoff` — reactive repair for writes missed by temporarily down nodes
- `Quorum Reads` — reads from multiple replicas (prerequisite for read repair)
- `Digest Reads` — optimization: compare hashes instead of full data to minimize network usage
- `Eventual Consistency` — the consistency model read repair helps maintain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ On a quorum read, compare all replicas.  │
│              │ Stale replicas → repair inline (foreground│
│              │ blocks) or async (background).           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Quorum or higher consistency + replicas  │
│              │ may have missed writes (lag, partitions) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Consistency = ONE (no comparison);       │
│              │ avoid high read_repair_chance on read-   │
│              │ heavy clusters (write amplification)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pharmacist checks 3 records: 2 agree,  │
│              │  updates the outdated one on the spot." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Entropy → Hinted Handoff → Digest  │
│              │ Reads → Cassandra nodetool repair        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra cluster has a node that was slow (high GC pause) for 20 minutes. During that time, 50,000 writes succeeded at quorum (written to 2 out of 3 replicas) but missed the slow node. The node recovers. Now there are 50,000 stale keys on that node. For keys that are read frequently (hot data): read repair will fix them quickly. For keys that are never read again (cold data): how do they get repaired? If you don't run anti-entropy repair for 15 days and gc_grace_seconds is 10 days, what happens to any tombstones among those 50,000 missed writes?

**Q2.** Cassandra read repair requires reading from ALL replicas (not just quorum) to detect divergence. With RF=3 and consistency=QUORUM: normally only 2 replicas are read. For repair, all 3 are read. Quantify: how does this change the read amplification (number of replica reads per client read)? For a cluster serving 1 million reads/second, what additional read load does this generate? Is the trade-off worth it? Under what circumstances would you disable read repair entirely?
