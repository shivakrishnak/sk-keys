---
layout: default
title: "Fencing and Epoch"
parent: "Distributed Systems"
nav_order: 593
permalink: /distributed-systems/fencing-and-epoch/
number: "593"
category: Distributed Systems
difficulty: ★★★
depends_on: "Split Brain, Leader Election"
used_by: "Raft, ZooKeeper, Distributed Locks, HDFS"
tags: #advanced, #distributed, #safety, #consensus, #correctness
---

# 593 — Fencing and Epoch

`#advanced` `#distributed` `#safety` `#consensus` `#correctness`

⚡ TL;DR — **Fencing** is the guarantee that an old leader's writes are rejected after a new leader is elected, enforced via monotonically increasing **Epoch** (generation) numbers — preventing ghost-leader data corruption in distributed systems.

| #593            | Category: Distributed Systems            | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Split Brain, Leader Election             |                 |
| **Used by:**    | Raft, ZooKeeper, Distributed Locks, HDFS |                 |

---

### 📘 Textbook Definition

**Fencing** in distributed systems is the mechanism that prevents a previously authoritative node (old leader, old lock holder) from causing damage after it has been superseded, by making its subsequent writes be rejected by all other nodes. **Epoch** (also: term in Raft, zxid epoch in ZooKeeper, fencing token in distributed locks) is a monotonically increasing number tied to a leadership generation: each new leader election increments the epoch; followers and storage systems reject any request with an epoch number lower than the most recently seen. This handles the **zombie leader** problem: a slow/GC-paused/network-isolated leader that recovers and resumes sending writes, unaware that a new leader has been elected. Without fencing: the zombie leader's stale writes corrupt data maintained by the new leader. With fencing: the zombie leader's writes are tagged with old epoch N; storage has already seen epoch N+1 (from new leader); storage rejects epoch N writes. Implementations: Raft terms (leader's AppendEntries tagged with term; followers reject lower terms), ZooKeeper zxid epoch (upper 32 bits = epoch; changes on leader election), distributed lock fencing tokens (monotonic integer returned with lock; storage accepts writes only with current token), HDFS generation stamps on block replicas.

---

### 🟢 Simple Definition (Easy)

Fencing: ensuring an old boss can't issue orders after a new boss was appointed. Epoch: the "generation number" of the current boss. Old boss has generation 3. New boss has generation 4. Old boss (zombie, woke up from GC pause) tries to write: "I'm generation 3, write this." Storage says: "I've already seen generation 4. Your generation 3 commands are rejected." The old boss's writes are silently ignored — no damage. Like a president whose term expired still trying to sign laws: the courts reject bills signed with an expired seal.

---

### 🔵 Simple Definition (Elaborated)

Why fencing is necessary: in distributed systems, a node can appear dead (GC pause, network partition, extreme load) and then REVIVE. If it was a leader, it still believes it's a leader. It will try to write. Without fencing: storage accepts these stale writes, corrupting data. Example: old Kafka partition leader (generation N) recovers after 30-second GC pause. New leader (generation N+1) was elected and accepted many new writes. Old leader sends writes from 30 seconds ago tagged with generation N. Storage has generation N+1. Storage rejects N. Data integrity maintained. Fencing is the safety mechanism that makes consensus algorithms correct even in the presence of slow/zombie nodes.

---

### 🔩 First Principles Explanation

**Zombie leader problem and fencing mechanisms:**

```
ZOMBIE LEADER PROBLEM:

  Timeline:
    T=0: N1 is leader (term=5). N2, N3 are followers.
    T=0 → T=30: N1 experiences 30-second GC pause (full GC, Stop-The-World).
                 N1: frozen. Sends no heartbeats.
    T=10: N2, N3: miss heartbeats. N2 wins election. N2 becomes leader (term=6).
    T=10 → T=30: N2 accepts writes from clients. Commits entries at index 50-100 (term=6).
    T=30: N1 GC pause ends. N1 RESUMES.
          N1 thinks: "I'm still leader (term=5). Let me send AppendEntries."
          N1 → N2, N3: AppendEntries(term=5, prevLogIndex=49, entries=[{50, term5, write_X}])

  WITHOUT FENCING:
    N2: "term=5 is valid (I'm term=6, but maybe this is a legitimate AppendEntries?)"
    N2 applies write_X from N1 (old leader).
    N2's log: [... 50(term5,write_X), 51(term5,write_Y), ...] — mixed with N2's own writes.
    CORRUPTION: N2's term=6 writes at indices 50-100 now conflict with N1's term=5 writes.

  WITH FENCING (Raft term-based):
    N2: receives AppendEntries(term=5).
    N2: "I'm term=6. term=5 < term=6. This is STALE. REJECT."
    N2: responds with {currentTerm: 6, success: false}.
    N1: receives rejection with term=6. N1: "term=6 > term=5. A new leader was elected."
    N1: IMMEDIATELY reverts to FOLLOWER state. Stops sending AppendEntries.
    N1: updates currentTerm = 6. Accepts N2 as leader. FENCED.

  Raft's term number IS the fencing mechanism:
    - Monotonically increasing per cluster lifetime.
    - All messages carry the sender's term.
    - Recipients reject messages with lower term.
    - Recipients update their term and step down if they see higher term.

EPOCH IN ZOOKEEPER (ZXID):

  ZooKeeper transaction ID (zxid): 64-bit integer.
  Upper 32 bits: epoch (incremented on each leader election).
  Lower 32 bits: counter (transaction sequence within this epoch).

  Example:
    Epoch 5, transaction 100: zxid = 0x0000000500000064
    Leader crashes. New election. Epoch 6, transaction 1: zxid = 0x0000000600000001
    Old leader (epoch 5) recovers: sends proposal with zxid = 0x0000000500000101.
    Followers: current epoch = 6. zxid epoch=5 < epoch=6. REJECT.

  ZAB epoch synchronization:
    New ZooKeeper leader: first runs DISCOVERY phase.
    DISCOVERY: sends LEADERINFO(epoch=new_epoch) to all followers.
    Followers: promise to never accept proposals with epoch < new_epoch.
    This is equivalent to Raft's Phase 1 (Prepare in Paxos) — establishing epoch leadership.

FENCING TOKENS FOR DISTRIBUTED LOCKS:

  Problem: GC pause causes lock holder to appear dead. Lock manager grants lock to another node.
           GC pause ends. Original node (with expired lock) resumes writing.

  Traditional distributed lock (WRONG — no fencing):
    Client A acquires lock at T=0. Lock timeout = 30s.
    Client A: GC pause for 40 seconds.
    T=30: Lock expires. Client B acquires lock.
    T=40: Client A resumes. Thinks it still has the lock!
    Client A: writes to storage. Client B: also writing.
    SIMULTANEOUS WRITE. Data corruption.

  Fencing token (CORRECT):
    Client A acquires lock. Lock manager returns {lock, token=1}.
    Client A: sends writes to storage with token=1.
    Client A: GC pause for 40 seconds.
    T=30: Lock expires. Client B acquires lock. Token=2 (monotonically increasing).
    Client B: sends writes with token=2. Storage: records "I've seen token=2."
    T=40: Client A resumes. Sends write with token=1.
    Storage: "I've seen token=2 > 1. Reject token=1 write." CLIENT A FENCED.
    Data integrity maintained.

  Implementation:
    Storage layer: records the highest token seen. Rejects writes with token ≤ max_seen.
    This requires STORAGE to understand tokens (not just the lock manager).
    "The storage is the last line of defense, not the lock."

  Implementation in practice:
    ZooKeeper: monotonic zxid as token.
    etcd: revision number as token.
          etcd.Put(key, value, etcd.WithLease(leaseId), etcd.WithModRevision(expectedRevision))
          If key's modRevision ≠ expectedRevision: Put rejected (someone else wrote since we read).
    Redis (Redlock): does NOT have built-in fencing tokens. Use revision-based approach instead.

HDFS GENERATION STAMPS:

  HDFS block: data stored across 3 DataNodes.
  Each block has a generation stamp (monotonically increasing integer).

  Scenario: block 12345 has generation stamp = 1001.
  DataNode DN1 crashes. DN1 recovers. DN1 has an old copy of block 12345 (generation 1001).
  During DN1's absence: block was re-replicated to DN4 with generation stamp = 1002.

  Without generation stamps:
    DN1 rejoins. NameNode: "Use DN1's copy of block 12345."
    DN1's copy: generation 1001 (stale). New writes applied to generation 1002 are missing.
    Client reads stale data.

  With generation stamps:
    NameNode: "current generation of block 12345 = 1002."
    DN1 reports block 12345 with generation 1001.
    NameNode: "1001 < 1002. DN1's copy is stale. Mark DN1's copy as INVALID."
    DN1: discards its stale copy. Re-replicates generation 1002 from DN3 or DN4.

  HDFS generation stamps increment on: block creation, append, recovery from failed write.
  This ensures: if two DataNodes have different copies of a block, NameNode can determine which is correct.

EPOCH IN KAFKA:

  Kafka partition leader epoch: monotonically increasing per partition.

  Scenario: Partition P1 has leader at broker B1 (epoch=3). B1 network partition.
            New leader B2 elected (epoch=4).
            B1 recovers. B1 thinks it's leader (epoch=3).
            B1 receives produce request from client.

  B1 → ZooKeeper (or KRaft controller): "I'm leader of P1, epoch=3. I'll write."
  ZooKeeper: "Current epoch for P1 is 4. Epoch 3 is stale. B1 is NOT the leader."
  B1: returns NOT_LEADER_FOR_PARTITION error to client.
  Client: retries to correct leader (B2).

  Leader Epoch Fence (KIP-101, Kafka 1.0+):
    Each log segment is tagged with the leader epoch when it was written.
    On leader failover: new leader uses epoch logs to determine which records are safe to serve.
    Records from old epoch that weren't replicated to quorum: truncated (not served to consumers).
    This prevents consumers from seeing data that was later lost due to leader failover.

IMPLEMENTING EPOCH-BASED FENCING:

  Pattern: every operation includes a "generation claim."
  Receivers: reject if claim's epoch < known current epoch.

  Epoch must be:
    1. MONOTONICALLY INCREASING: never decreases (N+1 > N always).
    2. DURABLE: persisted to disk; survives node restarts.
    3. GLOBALLY ORDERED: when a new epoch is established, ALL nodes adopt it.
       (Raft: term stored in currentTerm on all nodes. ZAB: epoch stored in all followers.)

  Common epoch sources:
    Raft term (durably stored, incremented on election).
    ZooKeeper zxid epoch (durably stored, incremented on leader election).
    Monotonic database sequence (if using external storage for epoch).
    etcd revision number (globally monotonic — good for fencing token).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT fencing/epoch:

- Zombie leaders: GC-paused or partitioned leader recovers, writes stale data
- Silent corruption: old leader's writes accepted alongside new leader's writes
- Undecipherable state: storage has interleaved writes from two "leaders" — recovery impossible

WITH fencing/epoch:
→ Zombie detection: old epoch rejected by all storage/followers immediately
→ Clean handoff: new leader's epoch > old → all writes automatically routed to new leader
→ Recovery clarity: only one epoch's writes are valid — recovery is deterministic

---

### 🧠 Mental Model / Analogy

> A presidential seal on executive orders. Each presidential term has a unique seal number (epoch). An outgoing president (went offline — "GC pause") signs orders with seal #44. New president elected: seal #45. National archives (storage): only accepts orders bearing the current seal. If ex-president (zombie) returns with order bearing seal #44: "This seal is retired. Rejected." The current president's seal #45 is the only valid authority.

"Presidential seal number" = epoch/term number
"Outgoing president signing orders" = zombie leader sending stale writes
"National archives rejecting retired seals" = storage rejecting old-epoch writes
"New president's seal becomes valid" = new leader's epoch accepted by all nodes

---

### ⚙️ How It Works (Mechanism)

**etcd revision-based fencing tokens:**

```go
// etcd: use revision number as fencing token.
// Revision = globally monotonic integer across all etcd operations.
// Use as fencing token: storage rejects writes with revision < current.

package main

import (
    "context"
    "fmt"
    clientv3 "go.etcd.io/etcd/client/v3"
    "go.etcd.io/etcd/client/v3/concurrency"
)

type FencedWriter struct {
    etcdClient  *clientv3.Client
    lockKey     string
    fencingToken int64  // revision when lock was acquired
}

func (fw *FencedWriter) AcquireLockWithFencing(ctx context.Context) error {
    session, _ := concurrency.NewSession(fw.etcdClient, concurrency.WithTTL(30))
    mutex := concurrency.NewMutex(session, fw.lockKey)

    if err := mutex.Lock(ctx); err != nil {
        return err
    }

    // Fencing token = revision at time of lock acquisition.
    // Monotonically increasing: each new lock acquisition gets higher revision.
    fw.fencingToken = mutex.Header().Revision
    fmt.Printf("Acquired lock. Fencing token: %d\n", fw.fencingToken)
    return nil
}

func (fw *FencedWriter) WriteWithFencing(ctx context.Context, key, value string) error {
    // Write to storage with fencing: only succeed if no one has written
    // with a higher revision (i.e., we're still the current lock holder).
    txn := fw.etcdClient.Txn(ctx)

    // Check: key's modRevision must be <= our fencing token.
    // If someone with a higher token wrote: our modRevision check fails.
    resp, err := txn.
        If(clientv3.Compare(clientv3.ModRevision(key), "<=", fw.fencingToken)).
        Then(clientv3.OpPut(key, value)).
        Commit()

    if err != nil {
        return err
    }
    if !resp.Succeeded {
        return fmt.Errorf("fencing: write rejected (another node wrote with higher revision)")
    }
    return nil
}

// Usage:
// writer1 acquires lock: fencingToken=100.
// writer1: GC pause for 35s. Lock expires.
// writer2 acquires lock: fencingToken=150.
// writer2 writes: modRevision check passes (no one else wrote).
// writer1 resumes. fencingToken=100 (stale).
// writer1 tries to write: modRevision check fails (writer2's write has revision 151).
// writer1: write rejected. FENCED. Data integrity maintained.
```

---

### 🔄 How It Connects (Mini-Map)

```
Split Brain (two primaries without fencing = data corruption)
        │
        ▼
Fencing and Epoch ◄──── (you are here)
(reject old-epoch writes; monotonic epoch = fencing token)
        │
        ├── Raft (term = epoch; followers reject lower-term messages)
        ├── Distributed Locks (fencing token returned with lock; storage enforces)
        └── Leader Election (new election increments epoch; old leader's writes rejected)
```

---

### 💻 Code Example

**Raft term-based fencing in Java:**

```java
// RaftNode: demonstrates term-based fencing.
public class RaftNode {

    // Raft persistent state (must survive restarts):
    private volatile int currentTerm = 0;      // Epoch. Persisted to disk.
    private volatile String votedFor = null;    // Voted for in currentTerm.
    private volatile RaftRole role = RaftRole.FOLLOWER;

    // On receiving ANY Raft RPC (AppendEntries, RequestVote):
    public void onReceiveRpc(int senderTerm, RpcType type, RpcPayload payload) {
        // FENCING: reject if sender's term is stale.
        if (senderTerm < currentTerm) {
            // This sender is a zombie (old leader, stale follower, etc.).
            // Reject their message immediately. Return our current term so they step down.
            sendReply(RpcReply.rejected(currentTerm));
            return;
        }

        // If we see a HIGHER term: update our term. Step down if we were leader.
        if (senderTerm > currentTerm) {
            log.info("Observed higher term {}. Stepping down from {}.", senderTerm, role);
            currentTerm = senderTerm;  // UPDATE EPOCH. Persisted to disk.
            role = RaftRole.FOLLOWER;
            votedFor = null;
            persistState(); // CRITICAL: persist before responding.
        }

        // Now process the RPC normally (terms are equal).
        processRpc(type, payload);
    }

    // Zombie leader detection on AppendEntries reply:
    public void onAppendEntriesReply(String followerId, int replyTerm, boolean success) {
        if (replyTerm > currentTerm) {
            // Follower has higher term → we (old leader) are zombie.
            // IMMEDIATELY step down. Stop sending AppendEntries.
            log.warn("Received term {} > currentTerm {}. Stepping down.", replyTerm, currentTerm);
            currentTerm = replyTerm;
            role = RaftRole.FOLLOWER;
            persistState();
            return;
        }
        if (!success && role == RaftRole.LEADER) {
            // Handle log inconsistency (not term mismatch).
            decrementNextIndex(followerId);
        }
    }

    // Persistent state to survive restarts (fencing survives restarts):
    private void persistState() {
        // Write currentTerm + votedFor to durable storage (WAL, fsync).
        // On restart: load currentTerm → node immediately knows its epoch.
        // Even after restart: will reject messages from zombie leaders with lower term.
        storage.persist("currentTerm", currentTerm);
        storage.persist("votedFor", votedFor);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fencing is only needed for distributed locks        | Fencing is needed any time a node can become a "zombie" (old leader/writer that recovers unaware of its demotion). Raft uses term-based fencing for all inter-node messages. ZooKeeper uses zxid epoch fencing. HDFS uses generation stamps for block replicas. Distributed locks use fencing tokens. Any distributed system where "authoritative" roles can change must implement some form of fencing                                                               |
| If a lock expires, the old holder immediately stops | Lock expiry is from the LOCK MANAGER's perspective, not the holder's. The holder may not know the lock expired (GC pause, network partition). After expiry: lock manager grants lock to new holder. Old holder resumes assuming it still has the lock. Without fencing tokens at the STORAGE layer: both old and new holders write simultaneously. The lock manager expiry alone is insufficient — the storage must also enforce fencing                              |
| Raft term and ZooKeeper epoch are the same concept  | Conceptually similar but implemented differently. Raft term: incremented per election, stored as a single integer per node, embedded in every RPC. ZooKeeper epoch: upper 32 bits of a 64-bit zxid; includes a counter within each epoch (per-transaction ordering within an epoch). The epoch in ZooKeeper also serves as a transaction ID space (all transactions in epoch E have zxid 0xExxxxxxx), making it both a fencing mechanism and a total order identifier |
| Fencing prevents all write ordering problems        | Fencing prevents writes from OLD epochs from being accepted. But within the SAME epoch (valid leader), write ordering still depends on the consensus mechanism (Raft log ordering). Fencing is a coarse-grained safety net ("ignore everything from the past") not a fine-grained ordering mechanism. For total order within an epoch: you still need the replicated log (AppendEntries with prevLogIndex checks)                                                     |

---

### 🔥 Pitfalls in Production

**Distributed lock without fencing token causes race condition:**

```
SCENARIO: Job scheduler service acquires a distributed lock to run a "monthly billing job."
          Only one instance should run at a time (expensive: charges all users).

  T=0:  Instance A acquires lock from Redis (SETNX billing-lock, TTL=60s).
  T=0 → T=55: Instance A processes 50% of users (slow due to DB load).
  T=55: Instance A: JVM GC pause (55 seconds — OutOfMemoryError GC overhead).
  T=60: Redis lock TTL expires. Lock released.
  T=61: Instance B: acquires billing-lock (new TTL=60s). Starts billing from beginning.
  T=110: Instance A: GC pause ends. Resumes. Checks Redis: still has lock?
         Redis: lock key exists (B has it, but A doesn't know A's lock expired).
         A: reads lock value — it's B's token, but A doesn't check. Continues billing.
  T=110-170: BOTH A and B billing. Users charged TWICE.

BAD: Lock check without fencing token:
  String lockToken = UUID.randomUUID().toString();
  Boolean acquired = redis.setNX("billing-lock", lockToken, Duration.ofSeconds(60));
  if (acquired) {
      for (User user : users) {
          billingService.chargeUser(user);  // No fencing check during long operation.
          // If lock expired mid-operation: another instance also runs this loop.
      }
  }

FIX: Use fencing token checked before each write:
  // Acquire lock AND get monotonically increasing token:
  LockAcquisition lock = redissonClient.getLock("billing-lock").acquireWithToken();
  long fencingToken = lock.getToken(); // Monotonically increasing integer.

  for (User user : users) {
      // Before charging: verify lock is still valid with our token.
      // Database (the actual resource) tracks the latest fencing token seen.
      boolean lockStillValid = db.execute(
          "UPDATE billing_lock SET last_token = ? WHERE last_token < ? RETURNING 1",
          fencingToken, fencingToken
      ).affectedRows > 0;

      if (!lockStillValid) {
          // Another instance took over (has higher token). STOP immediately.
          log.warn("Fencing token {} rejected. Stopping billing job.", fencingToken);
          throw new LockExpiredException("Lock was taken by another instance during operation.");
      }

      billingService.chargeUser(user);
  }
  // Result: Instance B (token > A's token) takes over. B's writes accepted.
  // A's writes rejected immediately upon B's acquisition. No double-charging.
```

---

### 🔗 Related Keywords

- `Split Brain` — the failure mode fencing prevents (zombie leader writes corrupting new leader's data)
- `Leader Election` — each election increments epoch; fencing enforces the new epoch
- `Distributed Locking` — fencing tokens prevent zombie lock holders from writing
- `Raft` — uses term as epoch; all nodes reject messages with lower term than current

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Monotonic epoch = generation counter;    │
│              │ old-epoch writes rejected by storage.    │
│              │ Zombie leaders can't corrupt new state.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed locks with long critical     │
│              │ sections; consensus (Raft term); any     │
│              │ leader-election-based system             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ — (Always implement fencing in systems  │
│              │ with ephemeral authority roles)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Retired presidential seal: national     │
│              │  archives reject orders bearing it."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Locking → Split Brain →      │
│              │ Raft → ZooKeeper → Leader Election       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Redis's Redlock algorithm uses 5 Redis nodes and requires acquiring a lock from at least 3. The paper (Martin Kleppmann's analysis) argues Redlock is NOT safe without fencing tokens even with 5 nodes. The argument: a client acquires locks on 3 nodes, then experiences GC pause; the lock expires; another client acquires the lock on 3 nodes; first client resumes and proceeds. Why can't Redlock's "validity time" check reliably prevent this? What is the correct solution?

**Q2.** Raft's term acts as a fencing mechanism against zombie leaders. But can a Raft FOLLOWER become a zombie? Scenario: follower F1 is 500ms behind due to network delay. Leader L1 commits entry at index 100. F1 only has index 99. Client reads from F1 (using serialisable consistency). Is F1's response correct? Is it a "zombie"? How does this differ from a zombie leader scenario? What Raft mechanism ensures followers don't serve arbitrarily stale reads?
