---
layout: default
title: "Linearizability"
parent: "Distributed Systems"
nav_order: 577
permalink: /distributed-systems/linearizability/
number: "0577"
category: Distributed Systems
difficulty: ★★★
depends_on: Consistency Models, Strong Consistency, Consensus, Raft
used_by: Distributed Locks, Leader Election, CAS Operations, etcd
related: Serializability, Sequential Consistency, CAP Theorem, Raft
tags:
  - linearizability
  - strong-consistency
  - consensus
  - distributed-systems
  - advanced
---

# 577 — Linearizability

⚡ TL;DR — Linearizability is the strongest single-object consistency model: every operation appears to take effect instantaneously at some point between its invocation and response, and all operations respect real-clock time ordering. A linearizable system looks exactly like a single-node system to any external observer. It is the formal foundation of what most engineers call "strong consistency" and is implemented by etcd, ZooKeeper, and Google Spanner.

| #577 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistency Models, Strong Consistency, Consensus, Raft | |
| **Used by:** | Distributed Locks, Leader Election, CAS Operations, etcd | |
| **Related:** | Serializability, Sequential Consistency, CAP Theorem, Raft | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT LINEARIZABILITY:**
A distributed lock service that is "strongly consistent" but not linearizable could allow this:
- Process A acquires lock at T=10 (response received by A at T=15)
- Process B reads the lock state (query started at T=12, response at T=20)
- B's read returns "lock is free" — even though A's write at T=10 should be visible
This is possible in sequential consistency (which only orders by process, not real-time clock).
With linearizability, the guarantee is stricter: since A's write was invoked at T=10 and completed at T=15, and B's read started at T=12 and completed at T=20, and these intervals overlap, there is a possible linearization. But if B's read started AFTER A's response (T=16), then linearizability guarantees B sees the lock as held. Linearizability makes distributed systems behave like single-node systems with respect to timing — essential for distributed locking, leader election, and compare-and-swap operations.

---

### 📘 Textbook Definition

**Linearizability** (Herlihy & Wing, 1990) is a correctness condition for concurrent data structures and distributed systems. A history H is linearizable if it can be extended to a complete history H' where there exists a legal sequential history S such that:
1. Each operation in H' has a linearization point within its real-time interval (between invocation and response)
2. The legal sequential history S, when all operations are ordered by their linearization points, is consistent with the sequential specification of the data type

Informally: every operation appears to execute atomically at exactly one instant during its real-time window. The operations' real-time order is preserved: if operation A completes before operation B begins, A's linearization point is before B's.

**Linearizability ≠ Serializability:** Linearizability is a single-object, real-time property. Serializability is a multi-object transaction property. "Strict Serializability" = both.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Linearizability = the distributed system behaves exactly like a single fast computer with a single copy of the data, observable from the outside.

**One analogy:**
> A perfectly synchronized clock that everyone in the world reads. Regardless of whether you ask the time in New York or Tokyo, everyone gets the same time to the millisecond. The time "happened" at a single instantaneous point. Contrast with clocks that drift: you might read 3:00:01 in New York and 2:59:59 in Tokyo for the same real instant — not linearizable.

---

### 🔩 First Principles Explanation

```
LINEARIZABILITY — FORMAL VISUALIZATION:

  Time ──────────────────────────────────────────────────────►
  
  Client A: [─────── WRITE(x=5) ─────────]  (invoked T=10, response T=15)
  Client B:         [─── READ(x) ────]      (invoked T=12, response T=20)
  Client C:                    [─── READ(x) ────]  (invoked T=17, response T=25)
  
  A's write interval: [10, 15]
  B's read interval: [12, 20]  ← overlaps with A's write interval
  C's read interval: [17, 25]  ← starts AFTER A's write COMPLETED (T=15)
  
  LINEARIZABILITY REQUIREMENT:
  A's linearization point (where write "took effect") ∈ [10, 15]
  B's read: overlaps with write → MAY see x=5 OR x=OLD (either is valid for B)
  C's read: started after write COMPLETED → MUST see x=5 (no valid linearization exists otherwise)
  
  If C returns x=OLD: LINEARIZABILITY VIOLATION
  → The system failed to appear as if the write was instantaneous
  → This is what non-linearizable systems (sequential consistency) might allow
  
  SEQUENTIAL CONSISTENCY (weaker): 
  Only requires ordering to respect per-process order, NOT real-time.
  C could READ x=OLD if there's a valid sequential ordering where C's read precedes A's write
  (even though in wall-clock time A's write finished first) — sequential allows this.
  Linearizability does NOT allow this.
```

---

### 🧪 Thought Experiment

**SCENARIO:** Distributed counter for a rate limiter. Goal: never allow more than 100 requests/second.

```
WITHOUT LINEARIZABILITY (eventual/sequential consistency):
  Time T=0: counter = 95 (5 remaining credits)
  Request burst: 10 concurrent requests hit 10 different replicas
  Each replica reads counter = 95 (stale — writes not yet visible)
  All 10 rate limit checks pass (95 < 100 → all allowed)
  Counter intended value: 105 (over limit!) but all 10 passed.
  
  Result: 10 requests allowed when only 5 should have been.
  Security boundary violated.

WITH LINEARIZABILITY (using atomic increment in etcd/Redis):
  Each request performs ATOMIC_INCREMENT(counter)
  Linearizable: only one increment takes effect at each point in time
  Request 96,97,98,99,100: all succeed (counter 96→100)
  Requests 101→105: see counter ≥ 100, all rejected ✓
  
  At most 100 pass. Guaranteed by linearizability of the atomic increment.

REDIS SCRIPT (linearizable single-node atomic operation):
  local count = redis.call('INCR', KEYS[1])
  if count > 100 then
    redis.call('DECR', KEYS[1])
    return 0   -- rejected
  end
  return 1     -- allowed
  -- Redis single-instance executes Lua scripts atomically = linearizable for that key
```

---

### 🧠 Mental Model / Analogy

> Linearizability is the "single register" illusion. Imagine a register (a variable holding one value) accessed by 100 people simultaneously. Linearizability says: even though the register is physically distributed across 10 servers, it must LOOK like there is a single register in a single location, operated one request at a time.
> 
> Whenever you write, the write "happens" at exactly one instant. Any read that starts after that instant sees the write. Any read that finished before the write started does not see it. Any read that temporally overlaps with the write may or may not see it — but must pick one value and be consistent with it.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Linearizability means the system behaves like one computer. After a write completes, every subsequent read (from any node) sees that write. The "completes" is key — it's about real wall-clock time ordering, not just logical ordering.

**Level 2:** The difference between linearizability and sequential consistency is subtle but vital. Sequential consistency guarantees a global order respecting each process's program order — but that global order need not match wall-clock time. Linearizability adds the real-time constraint. Example: if you call a distributed service to write X, and the write returns to you, then you call another service that reads X — linearizability guarantees the second service sees your write. Sequential consistency does not (the second call might read an older value if it happened to hit a "logical cycle" in the ordering). This is why linearizability is required for synchronization primitives.

**Level 3:** Linearizability in practice requires: (a) leader-based reads (reads go through the Raft/Paxos leader to ensure the latest committed value), OR (b) lease-based reads (leader maintains a time-bounded lease, reads served from leader without re-confirming, expires when lease times out to prevent serving stale reads after leader failure), OR (c) quorum reads with vector-clock-based freshness check. etcd supports linearizable and serializable (non-linearizable) reads per request. Linearizable reads in etcd involve a round-trip to confirm the leader's committed index before serving the read — adds ~1 RTT of latency. The trade-off is configurable per use case.

**Level 4:** Linearizability is compositionally safe: if you have two linearizable objects A and B, operations on A ∪ B are also linearizable. This makes it useful as a building block. Sequential consistency is NOT compositional: two sequentially consistent objects together may produce non-sequentially-consistent behavior. This composability is why linearizability is used as the correctness condition for distributed primitives (registers, CAS, queues) — they can be combined safely. The Jepsen test suite (Kyle Kingsbury) verifies linearizability of distributed systems using the Knossos checker: records all operation histories under fault injection, then checks if any valid linearization of the history exists.

---

### ⚙️ How It Works (Mechanism)

```
RAFT — HOW LINEARIZABLE READS WORK:

  Goal: serve a read that is guaranteed to reflect all committed writes.
  
  NAIVE READ (not linearizable):
    Client reads from Raft follower
    Follower might be behind on committed entries
    Returns stale value ← LINEARIZABILITY VIOLATION
    
  LINEARIZABLE READ — Raft ReadIndex protocol:
    1. Client sends read request to leader
    2. Leader records current commit index (called readIndex)
    3. Leader broadcasts heartbeat to ensure it is still the leader
       (prevents "deposed leader" from serving stale reads with old committed state)
    4. Wait for majority of followers to acknowledge heartbeat ✓
    5. Leader applies any pending entries up to readIndex
    6. Leader serves read from state machine (guaranteed at least as fresh as readIndex)
    7. Return to client ✓
    
  COST: 1 extra heartbeat round-trip per read (to verify leadership)
  Alternative: Lease-based reads (skip heartbeat, trust leader lease — ~1ms cheaper but
               requires clock assumptions)
  
  etcd: GET request with --consistency=l (linearizable) uses ReadIndex protocol
        GET request with --consistency=s (serializable) skips the heartbeat (faster, may be stale)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
DISTRIBUTED LOCK WITH LINEARIZABLE GUARANTEE (etcd):

  Service A wants to become leader/acquire lock:
  
  A: etcd.Put("/leader", "A", PrevExist=false, LeaseID=lease1)
     → Raft: AppendEntries to followers
     → Majority ACK → committed at log index 42
     → etcd returns: success, new leader = A ✓
  
  Service B simultaneously tries same:
  B: etcd.Put("/leader", "B", PrevExist=false, LeaseID=lease2)
     → Raft: concurrent write arrives
     → Raft consensus: one of them wins (say A wins, committed first)
     → B's operation fails: precondition violated (key already exists)
     → etcd returns: 412 Precondition Failed to B
  
  Service C reads leader immediately after A's write completes:
  C: etcd.Get("/leader", consistency=linearizable)
     → Leader performs ReadIndex (confirms leadership)
     → Returns "A" ✓ (sees A's write even though C started read at same time)
  
  RESULT: Exactly one service holds the lock at any time.
  This is only possible with linearizability.
  Eventual/sequential consistency → two services might both "see no lock" and both acquire it.
```

---

### 💻 Code Example

```java
// etcd Java client: linearizable operations for distributed lock
@Service
public class DistributedLockService {

    private final Client etcdClient;
    private static final String LOCK_KEY = "/locks/payment-processor";

    // Acquire lock using linearizable CAS (Compare-And-Swap)
    public Optional<LockHandle> tryAcquireLock(String ownerId, Duration ttl) {
        try {
            // Create a lease (TTL-bounded lock)
            LeaseGrantResponse lease = etcdClient.getLeaseClient()
                .grant(ttl.getSeconds())
                .get();

            // Linearizable Put with prevExist=false: atomically creates only if absent
            // This is a CAS operation — linearizable by etcd's Raft consensus
            TxnResponse txnResponse = etcdClient.getKVClient()
                .txn()
                .If(new Cmp(ByteSequence.from(LOCK_KEY, StandardCharsets.UTF_8),
                            Cmp.Op.EQUAL, CmpTarget.CREATE_REVISION(0)))  // key does not exist
                .Then(Op.put(
                    ByteSequence.from(LOCK_KEY, StandardCharsets.UTF_8),
                    ByteSequence.from(ownerId, StandardCharsets.UTF_8),
                    PutOption.newBuilder().withLeaseId(lease.getID()).build()))
                .commit()
                .get();

            if (txnResponse.isSucceeded()) {
                return Optional.of(new LockHandle(LOCK_KEY, lease.getID(), etcdClient));
            } else {
                // Someone else acquired the lock first (CAS failed)
                etcdClient.getLeaseClient().revoke(lease.getID());
                return Optional.empty();
            }
        } catch (Exception e) {
            throw new LockAcquisitionException("Failed to acquire lock", e);
        }
    }

    // Linearizable read: guaranteed to see latest committed value
    public Optional<String> getCurrentLockHolder() throws Exception {
        GetResponse response = etcdClient.getKVClient()
            .get(ByteSequence.from(LOCK_KEY, StandardCharsets.UTF_8))
            // etcd default: linearizable get (ReadIndex protocol)
            .get();
        return response.getKvs().isEmpty()
            ? Optional.empty()
            : Optional.of(response.getKvs().get(0).getValue().toString(StandardCharsets.UTF_8));
    }
}
```

---

### ⚖️ Comparison Table

| Property | Linearizability | Sequential Consistency | Causal Consistency | Eventual Consistency |
|---|---|---|---|---|
| **Real-time ordering** | Yes — respects wall clock | No | Causal chains only | No |
| **Global order** | Yes | Yes (logical) | Causal chains only | No |
| **Coordination cost** | High | High | Low | None |
| **Use cases** | Locks, leader election, CAS | Rarely used alone | Social graphs, feeds | DNS, shopping cart |
| **Examples** | etcd, ZooKeeper, Spanner | (rare in practice) | MongoDB sessions | DynamoDB, Cassandra ONE |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Linearizability = Serializability | Different properties. Linearizability is single-object + real-time. Serializability is multi-object + transaction isolation. Strictly serializable = both |
| QUORUM reads are always linearizable | Only if W+R>N AND you take the value with the highest version/timestamp AND you have a single-leader or atomic timestamp mechanism. Without these, quorum can still be non-linearizable |
| Linearizability is always necessary for safety | Many safety properties only need causal consistency or read-your-own-writes. Reserve linearizability for operations that truly need real-time global ordering: locks, CAS, counters with upper bounds |

---

### 🚨 Failure Modes & Diagnosis

**Stale Leader Serving Non-Linearizable Reads (Split-Brain)**

```
Symptom:
In a Raft cluster, after a network partition heals, old leader (now isolated)
continues to serve reads for 500ms before realizing it was deposed.
Reads return stale data — linearizability violated.

Root Cause:
Leader serving reads without confirming leadership (lease expired / heartbeat skipped)
After partition, new leader is elected while old leader still serves reads.

Detection:
etcd: enable metrics for leader_changes_total — spike = leader flap
      linearizability violation: Jepsen testing, or track write timestamps vs. read timestamps

Fix:
1. Use ReadIndex (re-confirm leadership before serving reads) — default in etcd
2. Tune leader lease TTL to be < election timeout to prevent stale-leader reads
3. Do NOT use serializable reads (etcd --consistency=s) for safety-critical operations
4. In Raft: follower reads must forward to leader, or use leases with strict clock assumptions
```

---

### 🔗 Related Keywords

- `Serializability` — the multi-object transaction analog of linearizability
- `Raft` — the primary consensus protocol used to implement linearizable distributed registers
- `Strong Consistency` — the practical term most engineers use for linearizability
- `CAP Theorem` — linearizable systems are CP; they sacrifice availability during partitions
- `etcd` — the canonical production-grade linearizable key-value store

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ DEFINITION    │ Ops appear instantaneous; real-time order    │
│               │ respected (Herlihy & Wing 1990)             │
├───────────────┼─────────────────────────────────────────────┤
│ KEY RULE      │ If A's write COMPLETED before B's read      │
│               │ STARTED, B must see A's write               │
├───────────────┼─────────────────────────────────────────────┤
│ vs SEQUENTIAL │ Sequential needs per-process order only;    │
│               │ Linearizability adds real-time constraint   │
├───────────────┼─────────────────────────────────────────────┤
│ MECHANISM     │ Raft ReadIndex (heartbeat before read),     │
│               │ leader-only reads, atomic-broadcast         │
├───────────────┼─────────────────────────────────────────────┤
│ USE CASES     │ Distributed locks, leader election,         │
│               │ compare-and-swap, rate limiters (strict)    │
├───────────────┼─────────────────────────────────────────────┤
│ SYSTEMS       │ etcd, ZooKeeper, Google Spanner, VoltDB     │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Two engineers debate linearizability for a distributed inventory system. Engineer A says: "We have QUORUM writes (W=2, R=2, N=3) in Cassandra, so we have linearizability." Engineer B says: "We don't — we have strong consistency for reads (always see a recent write) but not linearizability." Who is correct, and why? Then: design a test (a specific sequence of operations and assertions) that would DETECT a linearizability violation in the inventory system if Engineer A is wrong. Finally, explain what additional mechanism would actually make the Cassandra quorum system linearizable for the "decrement inventory and return new count" operation.
