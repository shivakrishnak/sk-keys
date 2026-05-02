---
layout: default
title: "Fencing / Epoch"
parent: "Distributed Systems"
nav_order: 593
permalink: /distributed-systems/fencing-epoch/
number: "0593"
category: Distributed Systems
difficulty: ★★★
depends_on: Leader Election, Split Brain, Distributed Locking
used_by: HDFS, ZooKeeper, etcd, Database HA
related: Split Brain, Distributed Locking, Leader Election
tags:
  - fencing
  - epoch
  - distributed-systems
  - advanced
---

# 593 — Fencing / Epoch

⚡ TL;DR — Fencing is a technique to neutralize a "zombie" node (old leader that was partitioned, slow, or paused but is now back) that might issue stale operations. A fencing token is a monotonically increasing number (epoch, term, generation) issued with each lease/leadership grant. Any operation must include its fencing token; storage/services reject operations with a token lower than the latest seen. This prevents an old leader's delayed writes from corrupting a system that has already elected a new leader.

┌──────────────────────────────────────────────────────────────────────────┐
│ #593         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Leader Election, Split Brain        │                      │
│ Used by:     │ HDFS, ZooKeeper, etcd, DB HA        │                      │
│ Related:     │ Split Brain, Distributed Locking    │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

A distributed lock server grants a lease to node A. Network partition: node A pauses (GC stop-the-world for 30 seconds). Lease expires. Node B gets the lease. Node A's GC completes: it thinks it still holds the lock. Node A writes to the shared resource. Node B simultaneously writes. Without fencing: both writes succeed, data corruption. With fencing tokens: Node A's token = 33, Node B's token = 34. Storage rejects Token 33 once it has seen Token 34. Node A's stale write is rejected by the storage layer.

---

### 📘 Textbook Definition

**Fencing token:** A monotonically increasing number assigned each time a lock or leadership is granted. Every operation sent to a shared resource must include the current fencing token. The resource tracks the highest token it has seen and rejects any operation with a lower (stale) token.

**Epoch/Term:** More general form — a monotonically increasing number representing a "generation" of leadership. In Raft: "term". In ZooKeeper: "zxid epoch". In Kafka: "leader epoch". Any node receiving a message from a lower epoch knows the sender is a zombie and ignores/rejects it.

**STONITH vs Fencing:** STONITH proactively kills the zombie (before it can act). Fencing reactively rejects stale operations from the zombie (without proactively killing it). Both can coexist.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Include a generation counter with every operation; the resource refuses operations from old generations.

**Analogy:** Bank authorization token. Your card is frozen (token 5 revoked). Bank issues a replacement card (token 6). You use old card to try to withdraw — the ATM sees "card generation 5, last valid generation = 6" → rejects. You can't drain your account with an old card, no matter how fast you type.

---

### 🔩 First Principles Explanation

```
FENCING TOKEN SEQUENCE:

  1. Lock service grants lock to Client A → Token = 33
  2. Client A takes token 33, sends request to Storage: WRITE data WITH token=33
  3. Storage notes: highest_token_seen = 33. Write accepted.
  
  4. Client A pauses (GC, network issue). Lease expires.
  5. Lock service grants lock to Client B → Token = 34
  6. Client B sends request to Storage: WRITE new_data WITH token=34
  7. Storage notes: highest_token_seen = 34. Write accepted.
  
  8. Client A resumes (thinks it still holds lock, has token=33)
  9. Client A sends: WRITE old_data WITH token=33
  10. Storage: token 33 < highest_token_seen=34 → REJECT (stale fencing token)
  
  ∴ Client B's write is preserved. Client A's zombie write is silently discarded. ✓
  
  EPOCH IN RAFT:
  Term = Raft's fencing epoch. Each election increments term.
  Old leader (term=5) receives an AppendEntries request from a follower:
  The follower includes term=6 (new leader's term).
  Old leader sees term=6 > term=5 → immediately steps down ✓ (zombie neutralized)
```

---

### 🧠 Mental Model / Analogy

> Fencing token = security clearance generation counter. When your clearance is revoked and re-issued to someone else, the clearance level increments. Presenting an old clearance badge to a door: "Level 3 issued at generation 5, current generation = 6" → door refuses entry. Even the most persistent zombie general cannot issue orders: every checkpoint verifies generation and rejects outdated credentials.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Fencing token = monotonic counter in every operation. Storage rejects smaller tokens than it has already seen. Prevents zombie writes from stale leaders.

**Level 2:** HDFS fencing: when a NameNode fails over, new NameNode increments the "generation stamp" (epoch). All DataNode writes must include the current epoch. Old NameNode writes are rejected at the DataNode level via epoch comparison. Additionally, HDFS issues SSH-based STONITH: new NameNode tries to SSH-kill the old NameNode before taking over, preventing simultaneous metadata writes.

**Level 3:** Implementation challenge: fencing only works if ALL storage backends that the zombie might write to enforce the token check. If there is any path (direct DB write, external API call, S3 write) that doesn't check the fencing token, the zombie can still cause corruption through that path. Real-world violations: application code that bypasses the distributed lock and writes directly to S3 (no fencing tokens in S3 PutObject). Solution: use conditional requests (S3 PutObject with IfMatch/ETag, SQL conditional updates with version checks).

**Level 4:** Fencing tokens in distributed locking (Redlock critique by Martin Kleppmann): Redlock (Redis-based distributed lock) does not provide fencing tokens. If the Redis clock skews or a Redis instance restarts with stale state, a client can hold an "expired" lock without knowing it. The only safe distributed lock in the face of process pauses is one backed by a linearizable store (Zookeeper, etcd) that provides fencing tokens guaranteed to be monotonically increasing even across leader elections.

---

### ⚙️ How It Works (Mechanism)

```
ZOOKEEPER FENCING VIA EPHEMERAL + SEQUENTIAL ZNODE:

  Leader election candidate → creates /election/leader-00000001 (ephemeral, sequential)
  ZooKeeper assigns sequential number = fencing token
  Lowest-sequence node = leader
  
  Leader A: created /election/leader-00000005 (token=5) ← lowest, becomes leader
  
  Leader A network partition → node expires, ZooKeeper deletes 00000005
  Leader B: created /election/leader-00000006 (token=6) ← new leader
  
  Leader A resumes, still has token=5 in memory, tries to write to database:
  Database checks ZooKeeper: current epoch = 6. Token 5 < 6 → REJECT.
  
  OR SIMPLER — monotonic fencing token from ZooKeeper:
  ZooKeeper: getEpoch() → returns monotonically increasing counter
  Lock acquisition sets epoch=N. All calls include epoch=N in request header.
  Resource (DB, file system) checks: IF epoch < known_max_epoch → 403 Forbidden
```

---

### 💻 Code Example

```java
// Fencing token implementation with etcd lease
// Resource (database proxy) enforces fencing token ordering

@Service
public class FencedResourceProxy {

    private final AtomicLong highestTokenSeen = new AtomicLong(0);
    private final DataSource dataSource;

    public FencedResourceProxy(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    // Every write must include a fencing token
    public void write(String key, String value, long fencingToken) {
        // CAS: only update if fencingToken >= highestTokenSeen
        long current;
        do {
            current = highestTokenSeen.get();
            if (fencingToken < current) {
                throw new StaleTokenException(
                    "Fencing token " + fencingToken + " is stale; current = " + current);
            }
        } while (!highestTokenSeen.compareAndSet(current, fencingToken));

        // Token is valid — proceed with the write
        try (Connection conn = dataSource.getConnection()) {
            conn.prepareStatement(
                "INSERT INTO kv_store (key, value, epoch) VALUES (?, ?, ?) " +
                "ON CONFLICT (key) DO UPDATE SET value=?, epoch=? " +
                "WHERE kv_store.epoch <= ?")
                .setString(1, key).setString(2, value).setLong(3, fencingToken)
                .setString(4, value).setLong(5, fencingToken).setLong(6, fencingToken)
                .executeUpdate();
        }
    }
}

// Client using etcd lease as fencing token source
@Component
public class FencedLeaderClient {

    private final io.etcd.jetcd.Client etcd;
    private volatile long myFencingToken;

    public void acquireLeadership() throws Exception {
        // Lease creation returns a monotonically increasing leaseId = fencing token
        LeaseGrantResponse lease = etcd.getLeaseClient().grant(15).get();
        myFencingToken = lease.getID();  // etcd leaseId is monotonically increasing
        // Always pass myFencingToken with every write operation
    }

    public void writeToResource(FencedResourceProxy proxy, String key, String value) {
        proxy.write(key, value, myFencingToken);
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism | What It Prevents | Requirement |
|---|---|---|
| **Fencing token** | Stale writes from zombie nodes | Storage must enforce token checks |
| **STONITH** | Zombie from acting at all | Out-of-band management channel |
| **Lease TTL only** | NOT sufficient (process pause > TTL = zombie still alive) | Only a start; need fencing too |
| **Raft term** | Zombie leader from committing | Quorum won't ACK old-term operations |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WHAT          │ Monotonic generation counter in every op     │
│ TOKEN SOURCE  │ Lock service, etcd leaseId, Raft term        │
│ ENFORCEMENT   │ Storage rejects token < max_seen_token       │
│ RAFT TERM     │ Raft's built-in fencing: leader immediately  │
│               │ steps down on seeing higher term             │
│ GOTCHA        │ All write paths must enforce — no bypasses   │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your team uses a Redis-based distributed lock (SETNX + EXPIRE). A node acquires the lock, does work, and releases it. During a GC pause, the TTL expires and another node acquires the lock. Both nodes now hold the lock simultaneously. (1) Would adding a fencing token (from a separate monotonic counter in Redis INCR) fully solve this? What is the remaining risk? (2) The Redlock algorithm uses 5 Redis nodes to improve lock safety. Does Redlock provide fencing tokens? What is Kleppmann's core critique? (3) What would be the safest implementation for a critical distributed lock that requires both safety (no split ownership) and liveness (no deadlock)?
