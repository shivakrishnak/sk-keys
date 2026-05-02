---
layout: default
title: "State Machine Replication"
parent: "Distributed Systems"
nav_order: 590
permalink: /distributed-systems/state-machine-replication/
number: "0590"
category: Distributed Systems
difficulty: ★★★
depends_on: Log Replication, Raft, Distributed Consensus, Total Order Broadcast
used_by: Distributed Databases, ZooKeeper, etcd, CockroachDB
related: Log Replication, Raft, Total Order Broadcast, Consensus
tags:
  - state-machine-replication
  - consensus
  - distributed-systems
  - advanced
---

# 590 — State Machine Replication

⚡ TL;DR — State Machine Replication (SMR) is a technique for making a distributed system fault-tolerant by: (1) representing the system as a deterministic state machine, (2) replicating the sequence of commands (inputs) to multiple nodes via a total order broadcast, and (3) ensuring all replicas apply the same commands in the same order. If the state machine is deterministic and all replicas start from the same state, they will reach identical states after applying the same command history. This is the theoretical foundation for etcd, ZooKeeper, CockroachDB, and all Raft/Paxos-based systems.

| #590 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Log Replication, Raft, Distributed Consensus, Total Order Broadcast | |
| **Used by:** | Distributed Databases, ZooKeeper, etcd, CockroachDB | |
| **Related:** | Log Replication, Raft, Total Order Broadcast, Consensus | |

---

### 🔥 The Problem This Solves

**DISTRIBUTED FAULT TOLERANCE WITHOUT SMR:**
You have a key-value database. You want 3 replicas for fault tolerance. Approach 1: "just copy data." But which copy is authoritative? What happens when two replicas receive two different writes simultaneously? Approach 2: "route all writes to primary, replicate asynchronously." But what if the primary fails mid-write? The replicas may be in different states. State Machine Replication solves this with a formal model: ALL nodes run the SAME state machine, ALL receive commands in the SAME TOTAL ORDER (via consensus/Raft), and ALL deterministically arrive at the SAME state. The key insight: if every replica applies commands in exactly the same order, and the state machine is deterministic (same input in same state → same output + same next state), then all replicas are always identical.

---

### 📘 Textbook Definition

**State Machine Replication (SMR)** (Lamport 1978, Schneider 1990) is a general method for implementing a fault-tolerant service by ensuring all replicas maintain identical copies of a state machine:

**Requirements:**
1. **Determinism:** Given a state S and an input I, the state machine always produces the same output O and next state S'. All non-determinism must be eliminated or agreed upon (e.g., random number seeds, timestamps agreed via consensus before use).

2. **Total Order:** All replicas receive the same commands in the same global order. Achieved via Total Order Broadcast (implemented by Raft/Paxos/Zab).

3. **Identical initial state:** All replicas start from the same initial state (empty DB, or the same snapshot).

**Result:** If these three conditions hold, all live replicas will always be in the same state after applying the same set of committed commands. A client can read from any replica. Writes go through consensus (to establish total order).

**Fault tolerance:** With 2f+1 replicas, the system tolerates f crash failures (Raft/Paxos) or f Byzantine failures (with 3f+1 replicas and BFT protocol).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SMR = all replicas run the same deterministic program in the same order → they always produce identical state.

**One analogy:**
> State Machine Replication is like synchronized cooking. Give 5 identical chefs the same recipe and the same ingredients in the same order — each chef independently produces an identical dish. The "recipe" is the log (total order of commands). The "dish" is the resulting state. If steps are applied in the same order by deterministic chefs: identical outputs guaranteed. One chef failing doesn't matter — the others still have the dish.

---

### 🔩 First Principles Explanation

```
STATE MACHINE MODEL:

  State Machine: {States S, Inputs I, Outputs O, Transition Function δ, Output Function λ}
  - δ(S, I) → S': given state S and input I, produces new state S'
  - λ(S, I) → O: given state S and input I, produces output O
  
  EXAMPLE: Key-Value Store State Machine
  S = {key1: "v1", key2: "v2"}  ← current state
  
  Input commands:
  I₁ = PUT(key3, "v3")
  I₂ = GET(key1)
  I₃ = DELETE(key2)
  
  Command sequence (total order from consensus):
  [I₁, I₂, I₃]
  
  All replicas apply in order:
  After I₁: S' = {key1:"v1", key2:"v2", key3:"v3"}  [all replicas]
  After I₂: S unchanged, output = "v1"               [all replicas return "v1"]
  After I₃: S'' = {key1:"v1", key3:"v3"}             [all replicas]
  
  DETERMINISM REQUIREMENT:
  δ(S, I) must be deterministic: same state + same input = ALWAYS same result
  
  PROBLEMS WITH NON-DETERMINISM:
  δ(S, "EXPIRE OLD KEYS") uses System.currentTimeMillis() on each replica:
  Replica 1 clock: T=1000ms → key(created at 999ms, TTL=0ms) expires
  Replica 2 clock: T=998ms  → same key hasn't expired yet
  → Replicas DIVERGE. Non-determinism is the enemy of SMR.
  
  FIX: timestamp must be part of the command (agreed via consensus BEFORE applying):
  Command: "EXPIRE OLD KEYS as of T=1000ms"  ← T determined by leader, replicated
  → All replicas use T=1000ms → identical expiry decisions ✓
```

---

### 🧪 Thought Experiment

**SCENARIO:** A distributed counter service needs to support increment, decrement, and reset. With SMR.

```
INITIAL STATE: {counter: 0}

CLIENT OPERATIONS (concurrent):
  Client A: INCREMENT (at T=100ms)
  Client B: INCREMENT (at T=101ms)
  Client C: RESET_TO(10) (at T=102ms)
  Client D: INCREMENT (at T=103ms)

TOTAL ORDER established by Raft (consensus decides ordering):
  Log Entry 1: INCREMENT  (Client A)
  Log Entry 2: INCREMENT  (Client B)
  Log Entry 3: RESET_TO(10) (Client C)
  Log Entry 4: INCREMENT  (Client D)

ALL REPLICAS apply in this order:
  After entry 1: {counter: 1}
  After entry 2: {counter: 2}
  After entry 3: {counter: 10}  ← reset overrides previous increments
  After entry 4: {counter: 11}

Regardless of which replica serves Client D's read: returns 11. ✓

FAULT SCENARIO:
  Replica 3 crashes after applying entry 2. State: {counter: 2}.
  Leader continues to replicate entries 3 and 4 to replicas 1 and 2.
  Replica 3 recovers: receives entries 3 and 4 via AppendEntries.
  Applies them in order → {counter: 11}. ✓

This is SMR in action: crash and recovery does not create divergence.
```

---

### 🧠 Mental Model / Analogy

> State Machine Replication is like a legal code system. Every law (state) is derived from all prior legislation (commands) applied in chronological order. If you start with the same constitution (initial state) and apply the same laws in the same order (total order): every courthouse (replica) derives the same legal outcome (identical state). A courthouse that was closed for a month (crashed replica) catches up by replaying all laws passed during its absence — it then reaches the same current state as all other courthouses.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** SMR = every replica runs the same program, receives the same commands in the same order, and produces the same state. Raft (or Paxos) provides the total order. The "program" is your state machine. Used in every fault-tolerant database, consensus store, and coordination service.

**Level 2:** The crucial implementation detail: what counts as "non-determinism"? Random numbers (seed from command, not local generator), current time (timestamp in command, consensus-assigned), external API calls (results in command payload), I/O operations (write to disk, not rely on disk state), thread scheduling (single-threaded state machine application). Raft/etcd state machines are careful to avoid all non-determinism — they apply log entries in a single-threaded loop, never use `System.currentTimeMillis()` inside the state machine, and embed all inputs in the log entries themselves.

**Level 3:** Performance considerations: since SMR requires ALL commands to go through consensus (total order), write throughput is bounded by the Raft/Paxos write latency × concurrency. Optimizations: (a) Pipelining — leader sends multiple log entries without waiting for each to commit; (b) Batching — many client writes batched into one log entry; (c) Read optimization — linearizable reads confirmed via ReadIndex without full consensus; (d) Multi-Raft partitioning — each shard has its own independent Raft group, allowing horizontal scaling of write throughput (CockroachDB, TiKV). Without partitioning, a single Raft group is bounded to ~50,000-100,000 writes/sec (etcd's measured throughput).

**Level 4:** SMR and linearizability are equivalent in expressive power for crash-fail systems. Implementing SMR gives you linearizable operations for free (since all operations go through total-order consensus). The formal proof: any linearizable object can be implemented via SMR; any SMR system provides linearizable semantics. This is why etcd (SMR-based) guarantees linearizability: it's a consequence of the SMR model, not an additional feature. Reconfiguration (adding/removing nodes) is the hardest part of practical SMR: you can't just add a node while the system is running, because the new node must be integrated into the consensus quorum atomically. Raft handles this via joint-consensus: a transitional configuration that includes both old and new members, ensuring safety during the configuration change.

---

### ⚙️ How It Works (Mechanism)

```
SMR ARCHITECTURE — COMPONENTS:

  ┌─────────────────────────────────────────────────────────────┐
  │                    CLIENT                                   │
  └──────────────────────────┬──────────────────────────────────┘
                             │ Write Request
  ┌──────────────────────────▼──────────────────────────────────┐
  │              CONSENSUS LAYER (Raft)                         │
  │  ┌─────────┐   ┌─────────┐   ┌─────────┐                  │
  │  │ Node 1  │   │ Node 2  │   │ Node 3  │                  │
  │  │(Leader) │   │(Follower│   │(Follower│                  │
  │  │         │──►│         │   │         │                  │
  │  │  Raft   │──►│  Raft   │   │  Raft   │                  │
  │  │  Log    │   │  Log    │   │  Log    │                  │
  │  └────┬────┘   └────┬────┘   └────┬────┘                  │
  │       │             │              │                        │
  │       │   Committed (majority ACK) │                        │
  └───────┼─────────────┼──────────────┼────────────────────────┘
          │             │              │
  ┌───────▼─────────────▼──────────────▼────────────────────────┐
  │              STATE MACHINE LAYER (deterministic)            │
  │   applyLogEntry(index=43, command="PUT key=val")            │
  │   ┌─────────────────────────────────────────────────────┐   │
  │   │ State: {key: value, ...}   MVCC Storage            │   │
  │   │ Apply: δ(state, PUT key=val) → new state           │   │
  │   │ Output: OK                                         │   │
  │   └─────────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────────────┘
  
  KEY INVARIANT: State Machine Layer is identical on ALL replicas after applying log[0..i].
  This invariant is maintained as long as:
  1. All nodes apply log entries in index order (enforced by Raft)
  2. State machine is deterministic (enforced by implementation)
  3. No entries are skipped (enforced by Raft Log Matching Property)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
ZOOKEEPER — STATE MACHINE REPLICATION IN PRACTICE:

  ZooKeeper's state machine:
  State S = ZNode tree {/config/db-url: "...", /leaders/job-store: "N2", ...}
  Commands: CREATE, DELETE, SETDATA, SETACL, CHECK
  
  Client: SETDATA /config/db-url "postgres://prod2:5432/mydb"
  
  1. ZooKeeper leader receives SETDATA request
  2. Leader converts to ZooKeeper transaction: {zxid=0x00001042, op=SETDATA, path=..., value=...}
  3. Leader runs Zab (ZooKeeper Atomic Broadcast — like Multi-Paxos):
     Sends PROPOSE(zxid=1042, ...) to followers
     Waits for majority ACKs
     Sends COMMIT(zxid=1042) to all
  4. ALL ZooKeeper nodes apply SETDATA in zxid order:
     State machine: δ(S, SETDATA /config/db-url "...") → S'
     S'.config.db-url = "postgres://prod2:5432/mydb"
  5. Leader responds to client: OK + new zxid
  
  WATCHER NOTIFICATION (state machine side effect):
  When client SET a watch on /config/db-url:
  ZooKeeper delivers a WatchEvent notification to the watching client.
  This notification is also part of the state machine (watchers are state).
  Because SMR ensures all replicas have identical state, ANY ZooKeeper node
  can handle the watch — the registered watchers are consistent.
  
  STATE SNAPSHOT (periodic compaction, equivalent to Raft snapshot):
  ZooKeeper takes periodic fuzzy snapshots of the ZNode tree.
  New joining server: receives latest snapshot + all subsequent transaction log entries.
  Replays from snapshot + log to reach current state. ✓
```

---

### 💻 Code Example

```java
// Implementing a simple State Machine in a Raft-based system (Spring Boot)
// Demonstrates the SMR pattern: state machine + log entry application

@Component
public class KeyValueStateMachine {

    // THE STATE — must be deterministic, no external side effects
    private final Map<String, String> store = new ConcurrentHashMap<>();
    private final AtomicLong lastApplied = new AtomicLong(0);

    // Apply log entry: MUST be deterministic given same state + command
    public StateMachineResult apply(long logIndex, Command command) {
        // Safety check: apply only in order
        if (logIndex != lastApplied.get() + 1) {
            throw new IllegalStateException(
                "Out-of-order apply: expected " + (lastApplied.get() + 1) + " got " + logIndex);
        }

        StateMachineResult result = switch (command.type()) {
            case PUT -> {
                // Deterministic: same state + PUT(k,v) = always same result
                store.put(command.key(), command.value());
                yield StateMachineResult.success(command.value());
            }
            case GET -> {
                // Deterministic: same state + GET(k) = always same result
                String value = store.get(command.key());
                yield value != null ? StateMachineResult.success(value)
                                   : StateMachineResult.notFound();
            }
            case DELETE -> {
                String prev = store.remove(command.key());
                yield prev != null ? StateMachineResult.success(prev)
                                   : StateMachineResult.notFound();
            }
            case COMPARE_AND_SWAP -> {
                // Linearizable atomic operation — deterministic given current state
                String current = store.get(command.key());
                if (Objects.equals(current, command.expectedValue())) {
                    store.put(command.key(), command.newValue());
                    yield StateMachineResult.success("swapped");
                }
                yield StateMachineResult.failure("expected value mismatch");
            }
        };

        lastApplied.set(logIndex);
        return result;
    }

    // Create a snapshot (for compaction / new member catch-up)
    public StateMachineSnapshot snapshot() {
        return new StateMachineSnapshot(lastApplied.get(), new HashMap<>(store));
    }

    // Restore from snapshot (InstallSnapshot RPC in Raft)
    public void installSnapshot(StateMachineSnapshot snapshot) {
        store.clear();
        store.putAll(snapshot.data());
        lastApplied.set(snapshot.lastIncludedIndex());
    }
}

// IMPORTANT: Anything that would make this non-deterministic MUST be moved OUT:
// - DO NOT: store.put(key, UUID.randomUUID().toString())     ← random = non-deterministic
// - DO NOT: store.put(key, Instant.now().toString())          ← time = non-deterministic
// - DO    : let the client send the UUID/timestamp as part of the command
//           The command itself carries pre-computed random/time values
//           so all replicas use the same values when applying.
```

---

### ⚖️ Comparison Table

| Property | SMR | Simple Primary Replication |
|---|---|---|
| **Fault tolerance** | f failures with 2f+1 nodes | Often 1 failure (primary fails, manual failover) |
| **Consistency** | Linearizable (all replicas identical) | Possible stale reads from replicas |
| **Write latency** | Consensus RTT (1-5ms single DC) | Primary write only (0.1-1ms) |
| **Automatic failover** | Yes (leader election built-in) | Often manual or slow |
| **Complexity** | High (consensus, elections, log gaps) | Low (primary/replica pattern) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All distributed databases use SMR | Many use simpler primary/replica replication without full consensus (MySQL async replication, Cassandra). SMR is for systems that need linearizability + automatic failover |
| SMR is infinitely scalable | A single Raft group is bounded by write throughput (~50K writes/s). Scale beyond this requires multi-Raft partitioning (CockroachDB, TiKV sharding) or different architectures |
| The state machine can use any programming model | The state machine MUST be deterministic. This rules out many common Java patterns: Dates, Random, non-deterministic HashMap iteration order, etc. This constraint drives architectural choices |

---

### 🚨 Failure Modes & Diagnosis

**Non-Deterministic State Machine (Replica Divergence)**

```
Symptom:
After a node restarts and replays its log, it has different data than the leader.
etcd endpoint status shows different "dbHash" values across nodes (etcd's corruption check).

Root Cause:
State machine applied a non-deterministic operation:
  - Used System.nanoTime() inside the state machine for a key TTL
  - Applied a sorting operation on a HashMap (Java HashMap iteration is non-deterministic)
  - Called an external service (HTTP call) from inside the state machine

Detection:
  etcdctl endpoint hashkv  → compare hash across nodes (etcd computes XOR of state)
  Different hashes: divergence detected → SMR invariant violated

Root Cause Analysis:
  Review the state machine apply() function for:
  1. Any time-dependent operations
  2. Random number generators
  3. External I/O (network, non-log filesystem)
  4. Non-deterministic collection iteration

Fix:
  1. All sources of non-determinism MUST be in the log entry (pre-computed by leader)
  2. State machine must be a pure function of (state, command)
  3. Use deterministic data structures (TreeMap instead of HashMap if iteration order matters)
  4. Add assertion: hash state before and after apply; compare with peers periodically
```

---

### 🔗 Related Keywords

- `Log Replication` — the mechanism that delivers commands in total order to all state machines
- `Raft` — the consensus algorithm that implements SMR for fault-tolerant systems
- `Total Order Broadcast` — the abstract communication primitive that SMR requires
- `Linearizability` — the consistency guarantee that SMR provides for reads and writes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ All replicas run same deterministic program  │
│               │ in same command order → identical state      │
├───────────────┼─────────────────────────────────────────────┤
│ 3 REQUIREMENTS│ 1. Deterministic state machine              │
│               │ 2. Total order of commands (via consensus)  │
│               │ 3. Same initial state on all replicas       │
├───────────────┼─────────────────────────────────────────────┤
│ TOLERANCE     │ 2f+1 nodes → f crash failures (Raft)        │
│               │ 3f+1 nodes → f Byzantine failures (BFT)     │
├───────────────┼─────────────────────────────────────────────┤
│ NON-DETM.     │ Random, currentTime, external I/O MUST NOT  │
│               │ be in state machine → put in log entry      │
├───────────────┼─────────────────────────────────────────────┤
│ SYSTEMS       │ etcd, ZooKeeper, CockroachDB, TiKV          │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** An engineering team wants to build a rate limiter using State Machine Replication (backed by etcd). The rate limiter logic: "allow request if current_count < limit; increment current_count; return allowed/denied." They implement this as a Lua script in Redis (not SMR) and as a transaction in etcd (SMR). Compare the two approaches: (1) Does the Redis Lua script guarantee linearizability for the read-modify-write operation? Under what failure scenario does it break? (2) The etcd SMR solution requires two network round-trips (Raft consensus round-trip) per rate limit check. At 100,000 req/s, is this viable? (3) Design a hybrid approach that uses the etcd SMR (for authoritative limit tracking) but avoids the full Raft round-trip for most requests (hint: consider token bucket replenishment as a background SMR operation + local token cache per service instance).
