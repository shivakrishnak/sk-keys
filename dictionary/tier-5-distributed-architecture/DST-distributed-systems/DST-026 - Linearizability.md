---
id: DST-049
title: Linearizability
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-035, DST-036, DST-040
used_by: DST-008, DST-043, DST-044
related: DST-035, DST-036, DST-039, DST-040, DST-011
tags:
  - distributed
  - consistency
  - deep-dive
  - advanced
  - foundational
  - algorithm
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /distributed-systems/linearizability/
---

# DST-038 - Linearizability

⚡ TL;DR - Linearizability is the formal definition of "strong consistency": every operation appears to take effect atomically at a single point in real time, making a distributed system's behavior identical to a single-server system observed by any external client.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-035, DST-036, DST-040                   |     |
| **Used by:**    | DST-008, DST-043, DST-044                   |     |
| **Related:**    | DST-035, DST-036, DST-039, DST-040, DST-011 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Herlihy and Wing (1990), engineers described concurrent data structures as "correct" without a formal definition of correctness. A concurrent queue was "correct" if it "seemed to work." Testing found obvious bugs, but subtle race conditions in distributed settings were labeled "edge cases." Without a formal model, you couldn't PROVE correctness — only observe failures. Systems that "worked in testing" shipped with silent race conditions.

**THE BREAKING POINT:**
A distributed compare-and-swap (CAS) operation is used for distributed locking. Two clients call CAS simultaneously. Without a formal correctness criterion, you cannot tell whether the implementation is correct — "it seems to work most of the time" is not a specification. You need a precise, verifiable definition: "what does it mean for CAS to be correct in a distributed setting?"

**THE INVENTION MOMENT:**
Maurice Herlihy and Jeannette Wing defined linearizability in their 1990 ACM TOPLAS paper "Linearizability: A Correctness Condition for Concurrent Objects." Their key insight: correctness for a concurrent object means there exists a legal sequential history that is consistent with the actual concurrent history, where each operation appears to take effect at some point between its invocation and its response. This gave computer science a precise, formal, and checkable definition of strong consistency.

**EVOLUTION:**
1990: Herlihy-Wing define linearizability. 1998: Chubby (Google) implements linearizable distributed lock service. 2007: ZooKeeper provides linearizable read/write for distributed coordination. 2012: Spanner provides global external consistency (linearizability). 2013: Kyle Kingsbury launches Jepsen — practical linearizability testing for real distributed databases. 2020+: Jepsen has tested 30+ databases; most have found linearizability violations.

---

### 📘 Textbook Definition

**Linearizability** (also called atomic consistency or external consistency) is a correctness condition for concurrent shared objects defined by Herlihy and Wing (1990). A history H of a concurrent execution is linearizable if: (1) it is possible to insert a linearization point for each completed operation between its invocation and response; (2) the resulting sequential history (operations ordered by linearization points) is a legal history for the object's sequential specification. Informally: every operation appears to take effect instantaneously at some single moment between when it was called and when it returned. Linearizability is the strongest commonly used consistency model and is composable: a system of linearizable components is itself linearizable.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Each operation appears to happen all-at-once at a single instant — no partial states, no stale reads, no reordering — exactly as if the system were a single computer.

> Linearizability is the guarantee of a magic "transaction window." When you call a function, you pick up a "start ticket" when the call begins and a "finish ticket" when it returns. Linearizability says: there exists exactly one instant between your start and finish tickets when the operation "happened." Every other process that looks at the system during that instant sees the result. Before that instant: old state. After: new state. No gray area.

**One insight:** Linearizability is the only consistency model that makes distributed systems compositionally safe. If every piece of your system is linearizable, the whole system is linearizable — you can reason about modules independently. This is not true for sequential consistency or weaker models.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every completed operation has a linearization point — one atomic instant between call and return.
2. The linearization point of op A is before that of op B if A completed before B began (real-time order).
3. The resulting sequential history must obey the object's sequential specification (e.g., a register: the most recent write determines the read value).
4. Concurrent operations' linearization points can be ordered in any way (as long as the sequential spec is satisfied).
5. Linearizability is a safety property — it says what cannot happen, not when events occur.

**DERIVED DESIGN:**
Implementing linearizability requires: (a) a mechanism to order operations (consensus or leader-based serialization); (b) ensuring reads see the latest committed write. Common implementations: Raft (all ops through leader), Paxos (quorum-based agreement), single-master replication with synchronous reads from master.

**THE TRADE-OFFS:**
**Gain:** Complete safety: no stale reads, no ordering anomalies, no phantom reads. Composable: build complex systems from linearizable primitives. Testable with Jepsen/Knossos.
**Cost:** Every operation requires coordination (at least one network round-trip to leader/quorum). Under partition: must choose unavailability over violating linearizability (CAP). Leader is a throughput bottleneck.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Ordering operations across distributed nodes requires communication. The network round-trip delay is physically irreducible.
**Accidental:** Many implementations add 2-round-trip overhead (Paxos phase 1 + phase 2) when single-RTT Raft leader reads would suffice. Or implement global locks when per-key linearizability is sufficient.

---

### 🧪 Thought Experiment

**SETUP:** A counter starts at 0. Client A calls `increment()`. Simultaneously, Client B calls `read()`. Both operations are concurrent (B started before A finished).

**WITHOUT LINEARIZABILITY:**
B reads 0 (the value before A incremented). Is this valid? Under linearizability: only if A's linearization point is AFTER B's linearization point. If A's increment is ordered before B's read in the linearized sequence, B MUST return 1. The key: we get to choose where A's linearization point falls — as long as it's between A's call and A's return. If A's call overlaps with B's read, we can choose either ordering — and both are valid depending on which sequential history we construct.

**WITH LINEARIZABILITY VIOLATED:**
A returns "incremented to 1." B started after A completed. B reads 0 (old value). This VIOLATES linearizability: A's linearization point must be before B's (A completed before B started — real-time ordering). Any read after A's completion must see 1, not 0.

**THE INSIGHT:** Linearizability is violated exactly when a read returns a value from before a completed write that causally precedes the read in real time. The "completed before" relationship is what creates the hard ordering constraint.

---

### 🧠 Mental Model / Analogy

> Linearizability is the guarantee of an atomic transaction at a bank teller. You hand over your passbook, the teller processes your withdrawal, stamps the passbook, and hands it back. At some point during that interaction, the money "moved." The next customer at ANY branch in the world who checks your account will see the post-withdrawal balance. There's no window where some branches think you have the old balance and others think you have the new one.

**Mapping:**

- **Handing passbook to teller** → operation invocation
- **Teller stamps passbook** → linearization point (the instant the operation takes effect)
- **Getting passbook back** → operation response
- **Any branch seeing new balance** → any process reads post-linearization-point value
- **No branch ever seeing old balance after stamp** → linearizability guarantee

Where this analogy breaks down: a real bank can have propagation delay between branches (replication lag). True linearizability would require any branch in any country to immediately see the new balance — which is physically expensive to achieve.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Linearizability means: when you do something to shared data, it happens all-at-once. Nobody sees half-done operations, nobody sees old values after the operation is complete. The whole world agrees: before the operation, old state; after the operation, new state.

**Level 2 - How to use it (junior developer):**
Use linearizable stores for distributed locks, leader election, CAS operations, and configuration. In practice: etcd (all operations are linearizable), ZooKeeper (with `sync()` before reads), Redis (single-node, not Sentinel), CockroachDB, Spanner. The database guarantees linearizability; your code just needs to choose the right system.

**Level 3 - How it works (mid-level engineer):**
A distributed system achieves linearizability by funneling all reads and writes through a single authoritative point (the Raft leader) or through quorum consensus (Paxos). The leader always has the latest committed state. Key constraint: reads must also go through the leader — follower reads are NOT linearizable unless the leader confirms its leadership (heartbeat-based read lease). Raft's ReadIndex mechanism: leader verifies it has the latest commit by checking a quorum heartbeat before serving a read, ensuring no stale leader can respond.

**Level 4 - Why it was designed this way (senior/staff):**
Herlihy and Wing proved that linearizability is _local_: a history is linearizable if and only if each object's projection (history restricted to operations on that object) is linearizable. This locality makes it compositional: you don't need to reason about the whole system at once — just each object independently. This is the key engineering property: you can build linearizable systems from linearizable components (Raft registers → linearizable counters → linearizable locks → linearizable leader election) without re-proving correctness at each layer. Sequential consistency LACKS this locality — it's not compositional — which is why linearizability became the standard for distributed systems building blocks.

**Expert Thinking Cues:**

- "Does your read go to a follower?" → Then you're NOT linearizable (unless read leases are implemented).
- "Does your CAS operation go through consensus?" → Necessary (not sufficient) for linearizability.
- "Has Jepsen tested your database?" → Check jepsen.io/analyses before trusting "linearizable" claims.
- "Is your distributed lock service linearizable?" → If not, your "distributed lock" is not a lock.

---

### ⚙️ How It Works (Mechanism)

**Raft-based linearizable reads (etcd):**

1. Client sends ReadIndex request to leader.
2. Leader records current commit index (CI).
3. Leader sends heartbeat to quorum to confirm it's still the leader.
4. Once quorum responds: leader applies all log entries up to CI, serves the read.
5. Result: read returns the value as of commit index CI — guaranteed to be the latest committed state.

**Paxos-based linearizable writes:**

1. Client sends write to any acceptor (proposer picks leader).
2. Phase 1: proposer gets highest promised ballot from quorum.
3. Phase 2: proposer proposes write with ballot, gets quorum acceptance.
4. Write committed: all future reads from any quorum will see this value.
5. Linearization point = moment of Phase 2 quorum acceptance.

**Single-leader with synchronous followers (MySQL semisync):**

1. All writes go to leader (primary).
2. Leader writes to binlog, waits for at least one follower to ACK.
3. Leader commits, returns to client.
4. Any subsequent read from leader: sees committed value.
5. Reads from un-ACK'd follower: NOT linearizable.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (linearizable CAS in etcd):**

```
Client A                   Client B
  │                            │
  ├── CAS("lock", "", "A")     ├── CAS("lock", "", "B")
  │        │                   │        │
  │   Raft leader receives both simultaneously
  │        │
  │   Leader serializes via Raft log:
  │   Log[42]: CAS("lock","","A") ← linearization point A
  │   Log[43]: CAS("lock","","B") ← linearization point B
  │        │
  │   Quorum ACK for log[42], commit
  ▼        │
  Client A returns TRUE (lock acquired)
           │
  Quorum ACK for log[43], commit
  ▼
  Client B returns FALSE (lock was "A", not "")
  ← YOU ARE HERE: atomically serialized, no ambiguity
```

**FAILURE PATH (split brain - linearizability violated without care):**

```
Network partitions: Leader N1 isolated from N2, N3.
N2, N3 elect new leader.
N1 (old leader): still serves reads for 5s (election timeout).
During this 5s: N1 serves old values; N2/N3 have new values.
VIOLATION: different clients see different "latest" values.
FIX: ReadIndex heartbeat — N1 can't confirm quorum → stops serving reads.
```

**WHAT CHANGES AT SCALE:**
100k writes/sec saturates a single Raft leader. Solution: shard data across multiple Raft groups (each key range has its own leader). Cross-shard linearizability requires distributed transactions (2PC over Raft) — much more expensive. CockroachDB and Spanner implement this with bounded overhead. Design principle: minimize cross-shard operations.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Linearizability guarantees are per-object by default. A system can be linearizable per-key but not serializable across keys. For multi-key atomic transactions (transfer from A to B), you need distributed transactions (serializability) on top of linearizable single-key ops. Linearizability ≠ full ACID — it addresses recency and ordering, not multi-key atomicity.

---

### 💻 Code Example

**BAD - Non-linearizable distributed lock (Redis Sentinel):**

```java
// Redis Sentinel: not linearizable
// In a failover, the new primary may not have the latest lock
// Two clients can both hold the "lock" simultaneously
public boolean tryAcquireLock(String key) {
    // SET NX on Redis Sentinel: appears atomic per node
    // but Sentinel failover can lose this write
    Boolean result = redis.set(key, clientId,
        SetArgs.Builder.nx().ex(30));
    return Boolean.TRUE.equals(result);
}
// DANGER: during Sentinel failover, two clients can
// both get TRUE — critical section violated
```

**GOOD - Linearizable distributed lock (etcd):**

```java
import io.etcd.jetcd.Client;
import io.etcd.jetcd.Lock;
import io.etcd.jetcd.lock.LockResponse;

// etcd: all operations linearizable via Raft
public class LinearizableLock {
    private final Lock lockClient;
    private final ByteSequence lockKey;

    public LinearizableLock(Client etcdClient, String key) {
        this.lockClient = etcdClient.getLockClient();
        this.lockKey = ByteSequence.from(key, UTF_8);
    }

    // Acquires a distributed lock with linearizability
    // guarantee: only ONE client holds the lock at a time,
    // even during leader elections and network partitions
    public LockToken acquire(long ttlSeconds)
        throws Exception {
        LockResponse resp = lockClient
            .lock(lockKey, ttlSeconds)
            .get(5, TimeUnit.SECONDS);
        // resp.getKey() is a fencing token
        // — use in downstream operations to detect stale locks
        return new LockToken(resp.getKey(), resp.getHeader());
    }

    public void release(LockToken token) throws Exception {
        lockClient.unlock(token.lockKey()).get();
    }
}
```

**How to test / verify correctness:**

```bash
# Jepsen linearizability test:
# https://github.com/jepsen-io/jepsen
# Runs a register workload (read/write/cas),
# records history with timestamps, checks Knossos

# Quick manual test: write, force leader failover, read
etcdctl put key1 value1
# Kill the etcd leader:
kill -9 $(pgrep -f "etcd --name leader")
# Immediately read on new leader:
etcdctl get key1
# Must return "value1" (linearizability) not "" (not found)
```

---

### ⚖️ Comparison Table

| Property               | Linearizability | Serializability    | Sequential | Causal           | Eventual  |
| :--------------------- | :-------------- | :----------------- | :--------- | :--------------- | :-------- |
| Real-time ordering     | Yes             | No                 | No         | Partial          | No        |
| Composable             | Yes             | No                 | No         | Yes (partial)    | Yes       |
| Multi-object atomicity | No (per-key)    | Yes (transactions) | No         | No               | No        |
| Coordination cost      | High            | High               | Medium     | Low              | None      |
| Jepsen testable        | Yes             | Yes                | Partial    | Partial          | No        |
| Example                | etcd, Spanner   | Spanner (strict)   | Rare       | MongoDB sessions | Cassandra |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                           |
| :------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Linearizability and serializability are the same" | They're orthogonal. Linearizability: single operations appear atomic at a real-time point. Serializability: transactions on multiple objects appear in some serial order. A system can have one without the other. Strict serializability = both. |
| "Quorum reads give linearizability"                | Quorum reads (R+W > N) guarantee overlap but NOT linearizability without additional mechanisms. Concurrent writes can still violate linearizability under LWW. Jepsen has confirmed this on Cassandra with QUORUM.                                |
| "A CP system is linearizable"                      | CAP's "C" means linearizability, but many systems marketed as "CP" don't implement it correctly. "CP" means "consistent when partition happens." "Linearizable" means correct for all operations at all times.                                    |
| "Linearizability is only about reads"              | Linearizability applies to all operations: reads, writes, and CAS. A linearizable CAS: either succeeds and is visible to all future reads, or fails because another write intervened — no ambiguity.                                              |
| "Reads from primary in MySQL are linearizable"     | Primary reads avoid replica lag, but don't guarantee linearizability during failover. Semi-synchronous replication + AFTER_SYNC binlog is needed. Even then, MySQL's primary-secondary isn't formally proven linearizable.                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale Leader Serving Non-Linearizable Reads**

**Symptom:** After a leader election, some clients get stale reads for 5-10 seconds. The new leader has newer data; the old leader continues to serve old values before timing out.
**Root Cause:** Old Raft leader hasn't received recent heartbeats (due to partition). It doesn't know a new leader was elected. It serves reads from its own log — which may not have the latest commits from the new leader.
**Diagnostic:**

```bash
# etcd: check leader term and revision:
etcdctl endpoint status --cluster -w table
# Look for two nodes with different "raft term" or "db size"
# Check leader history:
etcdctl endpoint status -w json | jq '.[].Status.leader'
```

**Fix:**
BAD: Using `--consistency=s` (serializable) in etcd during mixed leader state.
GOOD: Always use `--consistency=l` (linearizable) for correctness-critical reads. This forces a ReadIndex heartbeat check, detecting stale leadership.
**Prevention:** Configure etcd clients to use linearizable reads by default. Only use serializable reads explicitly for performance-sensitive non-critical reads.

**Failure Mode 2: False CAS Success During Network Partition**

**Symptom:** Two services both successfully acquired a distributed lock. Critical section executed twice. Data corruption.
**Root Cause:** Distributed lock based on non-linearizable CAS (Redis Sentinel, or leader failover without fencing). Old leader acknowledged CAS before failing; new leader didn't replicate the CAS result; new leader allowed another CAS on the same key.
**Diagnostic:**

```bash
# Check Redis Sentinel failover logs:
tail -100 /var/log/redis/sentinel.log | grep "failover"
# Look for: "+switch-master", "+slave-reconf-inprog"
# If you see these during the lock acquisition window:
# lock safety was violated
```

**Fix:**
BAD: Using Redis Sentinel for distributed locks without fencing tokens.
GOOD: Use etcd with fencing tokens (etcd's LockResponse.getKey() is a fencing token). Pass the token to downstream operations; they reject requests with old tokens.
**Prevention:** Never use non-linearizable stores for distributed locks. Mandate Jepsen test results for any new locking library.

**Failure Mode 3: Security - Authorization Bypass via Non-Linearizable Read**

**Symptom:** A permission revocation takes effect on the primary. An immediately subsequent authorization check reads from a non-linearizable secondary and approves an operation that should be denied.
**Root Cause:** Auth service reads permissions with serializable (not linearizable) consistency. The serializable read can go to any node — including one with replication lag. Permission revocation hasn't propagated.
**Diagnostic:**

```bash
# Check auth service read consistency:
grep -r "consistency=s\|serializable" auth-service/ config/
# Check etcd endpoint each auth read hits:
etcdctl get /permissions/user123 --consistency=l
etcdctl get /permissions/user123 --consistency=s
# If these return different values: gap exists
```

**Fix:**
BAD: Permission reads with serializable consistency.
GOOD: All security-sensitive reads (permissions, revocations, ban status) use linearizable consistency (`--consistency=l`). This is non-negotiable.
**Prevention:** Classify data by security impact. Permissions data: always linearizable reads. Document this constraint in the service contract.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-035 - Consistency Models (linearizability in the broader spectrum)
- DST-036 - Strong Consistency (practical strong consistency = linearizability)
- DST-040 - Lamport Clock (logical time ordering underpins linearizability reasoning)

**Builds On This (learn these next):**

- DST-008 - Leader Election (requires linearizability to be safe)
- DST-043 - Distributed Locking (linearizable CAS = correct distributed lock)
- DST-044 - Consensus Algorithms (the mechanism implementing linearizability)

**Alternatives / Comparisons:**

- DST-039 - Serializability (transaction-level correctness vs. single-op linearizability)
- DST-011 - Raft (a specific consensus algorithm implementing linearizability)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Formal definition of strong    |
|                  | consistency: atomic real-time  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | "Correct" without a proof;     |
|                  | race conditions in dist. CAS   |
+------------------+--------------------------------+
| KEY INSIGHT      | Each op has one linearization  |
|                  | point; real-time order enforced|
+------------------+--------------------------------+
| USE WHEN         | Distributed locks, CAS, leader |
|                  | election, critical sections    |
+------------------+--------------------------------+
| AVOID WHEN       | Analytics, social counters,    |
|                  | high-write non-critical data   |
+------------------+--------------------------------+
| TRADE-OFF        | Compositional safety vs.       |
|                  | coordination latency overhead  |
+------------------+--------------------------------+
| ONE-LINER        | Every op appears instantaneous |
|                  | at one point between call/resp |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-011 Raft,                  |
|                  | DST-043 Distributed Locking    |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Linearizability = every operation appears to take effect at a single instant between its call and return; real-time ordering of non-overlapping operations is preserved.
2. It is the ONLY composable consistency model — a system of linearizable components is linearizable.
3. Quorum reads alone (Cassandra QUORUM) do NOT give linearizability — you need consensus (Raft/Paxos) or single-leader reads.

**Interview one-liner:**
"Linearizability is the formal correctness condition for strong consistency: every operation appears to take effect atomically at a single real-time point between its invocation and response, making a distributed system appear identical to a single-server system to any external observer — and it's the only consistency model that is compositional, enabling safe reasoning about complex systems built from linearizable components."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The definition of "correct" must precede the implementation. Linearizability's power is not in what it implements, but in what it specifies: a precise, checkable, formal definition of correctness. Without this definition, you can't test correctness, you can't prove it, and you can't reason about it compositionally. Every complex system needs its correctness criterion formally stated before implementation — linearizability is the model for how to do this.

**Where else this pattern appears:**

- **Hardware transactional memory (HTM):** CPU instructions like `LOCK XCHG` implement linearizable compare-and-swap at the hardware level. The CPU's cache coherence protocol (MESI) is the physical implementation of linearizability across cores. Database linearizability is the distributed analog of this hardware guarantee.
- **File system rename operations:** `rename()` is linearizable on POSIX file systems — it either succeeds and the new name is visible, or fails and the old name remains. No observer sees a partial state. File system designers borrowed the concept from concurrent object theory.
- **Blockchain finality:** A "finalized" block in Ethereum (after the Casper FFG checkpoint) provides linearizability at the blockchain level — all nodes agree on the finalized state, and no future block can revert it. "Finality" is blockchain terminology for linearizability.

---

### 💡 The Surprising Truth

Linearizability was originally defined for concurrent objects on a SINGLE MACHINE (shared memory multiprocessors), not for distributed systems. Herlihy and Wing's 1990 paper was about proving correctness of concurrent data structures on parallel CPUs. The concept was later adopted (and generalized) for distributed systems — but with a critical additional challenge: in shared memory, there IS a global clock (CPU cycles); in distributed systems, there is no global clock. This means linearizability in distributed systems requires an explicit mechanism to create the appearance of a global clock (Raft's monotonic log, Spanner's TrueTime, Lamport clocks). When engineers say "we implement linearizability," they are solving a harder problem than Herlihy and Wing originally defined — they are implementing global clock semantics over an asynchronous network where clock skew and message delays are unbounded without explicit coordination.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A high-frequency trading system processes 500,000 stock price updates per second. The system requires linearizable reads (always see the latest price). With a Raft-based system, every read adds a leader heartbeat round-trip (~2ms). At 500k reads/sec, this is 1,000,000 network messages/sec just for reads. What techniques can reduce this overhead while preserving linearizability? What is the minimum coordination required?
_Hint:_ Raft's "read lease" optimization: after a leader wins an election, it can serve reads without a heartbeat for up to `election_timeout / 2` milliseconds (within which no other leader can exist). Does a read lease give linearizability? Under what failure scenario does it break?

**Q2 (D - Root Cause):** A team claims their etcd-backed distributed lock is linearizable. During a chaos engineering test, they kill the etcd leader. A new leader is elected. Two services acquired the lock simultaneously during the failover window. What exactly went wrong? Is etcd's lock service not linearizable, or was the implementation of the lock protocol incorrect?
_Hint:_ etcd's lock uses leases (TTL-based). When the leader dies, a client holding a lock's lease may not know the lease has been lost (no heartbeat to old leader). The client continues to act as if it holds the lock. What is a "fencing token" and how does it make distributed locks safe even when the lock service fails?

**Q3 (E - First Principles):** Herlihy proved that linearizability is "local": a history is linearizable iff each object's sub-history is linearizable. Sequential consistency is NOT local. Why does locality matter for building real systems? Give a concrete example of a system that is locally (per-object) linearizable but globally violates sequential consistency — is such a system "safe" to use?
_Hint:_ A system of two linearizable registers (X and Y) where two clients perform concurrent reads of both values — is the combined read history necessarily consistent? Consider: client A reads X=1, Y=0; client B reads X=0, Y=1. Both reads are within their respective linearizable windows. Is this a valid linearizable history for the pair (X, Y)?

