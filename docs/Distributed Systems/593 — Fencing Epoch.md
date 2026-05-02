---
layout: default
title: "Fencing / Epoch"
parent: "Distributed Systems"
nav_order: 593
permalink: /distributed-systems/fencing-epoch/
number: "0593"
category: Distributed Systems
difficulty: ★★★
depends_on: Split Brain, Leader Election, Distributed Locking, Clock Skew
used_by: Distributed Locking, Raft, Split Brain prevention, STONITH
related: Split Brain, Distributed Locking, Clock Skew, Raft, Quorum
tags:
  - distributed
  - reliability
  - algorithm
  - deep-dive
  - pattern
---

# 593 — Fencing / Epoch

⚡ TL;DR — Fencing uses monotonically increasing epoch/token numbers to ensure that a recovered stale leader or expired lock-holder is prevented from writing to shared resources, even if it doesn't know its authority has expired.

| #593            | Category: Distributed Systems                                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Split Brain, Leader Election, Distributed Locking, Clock Skew |                 |
| **Used by:**    | Distributed Locking, Raft, Split Brain prevention, STONITH    |                 |
| **Related:**    | Split Brain, Distributed Locking, Clock Skew, Raft, Quorum    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Node N1 holds a distributed lock, starts a long operation. N1 suffers a GC pause
for 15 seconds. The lock's TTL is 10 seconds — it expires. N2 acquires the lock.
N2 starts its own operation on the shared resource. N1's GC pause ends. N1 resumes,
still believing it holds the lock (it has no way to know it expired during the pause).
N1 also writes to the shared resource. Two nodes with "the lock" write concurrently.
Data is corrupted. The lock failed its entire purpose.

**THE INVENTION MOMENT:**
The root problem: the lock holder doesn't know when its lock expired. Fencing solves this
by adding a check at the RESOURCE LEVEL. The resource refuses all writes from any holder
whose epoch/token is not the most recent. Even a node that doesn't know it was evicted will
have its writes rejected before they reach the data.

---

### 📘 Textbook Definition

**Fencing** is a mechanism to ensure that a stale or expired lock-holder or leader cannot successfully perform operations on a shared resource. A **fencing token** is a monotonically increasing integer issued by the lock service with each new lock grant. Each write to the protected resource must include the current fencing token. The resource's storage layer tracks the highest token seen and rejects any write with a lower token. An **epoch** (or **term number** in Raft) is the same principle applied to leader elections: each election increments a global epoch; messages from previous epochs are ignored. Both mechanisms guarantee mutual exclusion at the storage/decision layer, independent of whether the old holder knows its authority has expired.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A fencing token is like an expiring key card with an ever-increasing serial number — the door only opens for the highest serial number it has seen, so old cards become permanently invalid.

**One analogy:**

> A fencing epoch is like a "Generation N" royal dynasty. The King of Generation 5 makes proclamations. During a political crisis, a regent is appointed as Generation 6. The King of Generation 5 returns from exile and tries to issue Generation 5 royal decrees. The bureaucracy has a rule: only Generation 6+ decrees are valid; Generation 5 documents are automatically rejected, regardless of what the king believes about his own authority.

**One insight:**
The key insight of fencing: the resource/storage layer is the ultimate arbiter of which writes are accepted, not the lock service and not the lock holder. Even perfect lock services can have holders that outlive their token due to GC pauses, network partitions, or process suspension. Moving the enforcement to the resource makes correctness independent of the holder's knowledge of its own lock state.

---

### 🔩 First Principles Explanation

**THE GC PAUSE PROBLEM (THE SPECIFIC FAILURE FENCING SOLVES):**

```
Timeline:
  T=0:   Client 1 acquires lock, receives fencing token=33
  T=5:   Client 1 starts operation, holds lock
  T=10:  Lock expires (TTL=10s). Client 1 hasn't noticed (GC running)
  T=10:  Client 2 acquires same lock, receives fencing token=34
  T=15:  Client 1's GC pause ends. Client 1 resumes.
         Client 1 thinks: "I have the lock (token=33). Writing now."
         Client 1 sends write + token 33 to storage.

WITH NO FENCING:
  Storage accepts write (doesn't know about tokens). CORRUPTION.

WITH FENCING:
  Storage tracks: highest_seen_token = 34 (from Client 2's write)
  Storage checks: Client 1's token (33) < highest_seen (34)
  Storage REJECTS Client 1's write. Returns: "FENCING REJECTED: token expired"
  Client 1 gets an error → must re-acquire lock and retry the operation.
  Client 2's write is unaffected. SAFE.
```

**RAFT TERM AS EPOCH:**

```
Raft terms are fencing epochs for leader authority:
  Term 1: N1 is leader (epoch=1)
  N1 network partition. N2 elected in term 2 (epoch=2).
  N1 recovers, still thinks it's leader of term 1.

  N1 sends AppendEntries{term=1} to followers.
  Followers: current term = 2. 1 < 2 → REJECT.
  N1 receives rejection with term=2 → N1 immediately steps down as leader.
  N1 becomes follower of term 2.

  N1's "old term" writes are automatically fenced out.
  No split brain. No corruption.
```

**FENCING TOKEN FLOW:**

```
┌─────────────────────────────────────────────────────────┐
│  Lock Service (ZooKeeper / etcd)                        │
│       Token counter: 34                                 │
│              │ grant lock + token 34                    │
│              ▼                                          │
│  Client 2 (new lock holder)                             │
│              │ write request + token 34                 │
│              ▼                                          │
│  Storage Layer                                          │
│  highest_seen_token = 34                                │
│  Accepts writes with token ≥ 34                         │
│  Rejects writes with token < 34                         │
│              ▲                                          │
│              │ write request + token 33 (REJECTED)      │
│  Client 1 (stale lock holder, expired)                  │
└─────────────────────────────────────────────────────────┘
```

**IMPLEMENTATION REQUIREMENTS:**

```
LOCK SERVICE:
  - Issue monotonically increasing token on every new lock grant
  - No reuse of tokens (even after crash recovery: persist last issued token)

STORAGE LAYER (the fenced resource):
  - Persist highest_seen_token durably (on disk, not just in memory)
  - Reject and return error for any write with token < highest_seen_token
  - Idempotent: same token can be used multiple times (for retries)

LOCK HOLDER (client):
  - Include token in every write request to the fenced resource
  - Handle "FENCING REJECTED" error by re-acquiring the lock before retrying
```

---

### 🧪 Thought Experiment

**WHAT IF THE STORAGE LAYER DOESN'T SUPPORT FENCING?**
Some storage systems (legacy databases, file systems, S3) don't natively support
fencing token checks. Can you still implement fencing?

**APPROACH 1: CONDITIONAL WRITES (Compare-And-Swap):**
Add an `if_epoch = N` condition to writes: "only write if
current_epoch = N." The storage layer performs the epoch check atomically.
S3 and many databases support conditional writes: `IF epoch = :expected_epoch`.

**APPROACH 2: LEASE-BASED FENCING:**
The lock service issues leases with explicit expiry times AND epoch. The fenced
resource enforces both: `if epoch == current_epoch AND now < lease_expiry`. If
epoch is stale OR lease has expired: reject. This requires clock synchronisation
(see Clock Skew) — hence why a pure fencing token (no time component) is safer.

**APPROACH 3: WRITE SERIALISATION THROUGH LOCK SERVICE:**
All writes go through the lock service itself, which enforces serial ordering.
This turns the lock service into the write path bottleneck — acceptable for
low-write-rate coordination data, not for high-throughput storage.

---

### 🧠 Mental Model / Analogy

> Fencing is like a nightclub with a guest list policy where each night the
> list gets a new version number. The bouncer only accepts ID cards from the
> CURRENT night's version. If you were on last night's list (version 42) but
> not tonight's (version 43), you're turned away — regardless of whether you
> were told you got removed. The bouncer's job is to enforce the current version,
> not to communicate with every ex-guest.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A fencing token is a number that increases every time a distributed lock is granted. All writes must include the current token. The database rejects writes with old token numbers. This stops a slow/crashed/paused node from writing after it's been replaced.

**Level 2:** Fencing tokens decouple "who thinks they have authority" from "who the resource acknowledges as having authority." Even if a node doesn't know its lock expired, its writes are rejected at the storage layer. This is the only safe way to implement distributed locking on systems with GC pauses, network jitter, or process suspension.

**Level 3:** Fencing requires storage-layer enforcement. The client must include the token with every write; the storage layer must persists the highest-seen token and reject lower ones atomically. Raft uses the same principle via term numbers — messages with term < currentTerm are rejected. The key difference: Raft's epoch check is in the protocol layer; storage-level fencing is an application-level mechanism for non-Raft systems.

**Level 4:** Production fencing implementations must handle replay: an expired lock-holder retrying the same token multiple times must get consistent rejections (idempotent). They must handle overflow: once the token counter becomes very large it must not wrap around (use 64-bit integers). And they must handle partial writes: if a write is fenced AFTER partial data has been written (page-level writes), the partial write must be rolled back. This is why fencing is implemented at the transaction boundary, not at the byte level. ZooKeeper epoch + ZXID (transaction ID) combination provides this: only writes with the current epoch and a ZXID greater than the last accepted are applied.

---

### ⚙️ How It Works (Mechanism)

**ZooKeeper Fencing Implementation:**

```java
// Client acquires lock with fencing token (epoch):
ZooKeeper zk = new ZooKeeper("localhost:2181", 3000, null);

// Create ephemeral sequential znode:
String lockNode = zk.create("/locks/my-lock-",
    new byte[0], ZooDefs.Ids.OPEN_ACL_UNSAFE,
    CreateMode.EPHEMERAL_SEQUENTIAL);

// ZooKeeper ZXID (transaction ID) serves as fencing token:
long fencingToken = zk.getSessionId();  // session epoch

// Include fencing token in write to storage:
storageClient.write("key", value, fencingToken);

// Storage layer (your implementation):
void write(String key, byte[] value, long epoch) {
    if (epoch < highestSeenEpoch.get(key)) {
        throw new FencingException(
            "Write rejected: epoch " + epoch +
            " < highest seen " + highestSeenEpoch.get(key));
    }
    highestSeenEpoch.put(key, epoch);
    dataStore.put(key, value);
}
```

**Kubernetes Pod Disruption via Epoch:**

```yaml
# Kubernetes uses lease objects with lease duration as epoch mechanism:
# LeaseHolder must renew within leaseDurationSeconds.
# If not renewed, new leader elected with higher resourceVersion.
# ResourceVersion is the K8s fencing token equivalent.
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: my-controller-leader
  namespace: default
spec:
  acquireTime: "2024-01-15T10:00:00Z"
  leaseDurationSeconds: 15 # epoch TTL
  holderIdentity: "pod-abc123" # current holder
  leaseTransitions: 7 # how many times leadership changed (epoch count)
  renewTime: "2024-01-15T10:00:12Z"
```

---

### ⚖️ Comparison Table

| Mechanism               | Level of Enforcement  | Needs Storage Support | GC Pause Safe            | Use Case                               |
| ----------------------- | --------------------- | --------------------- | ------------------------ | -------------------------------------- |
| Lock TTL only           | Lock service          | No                    | No (stale holder writes) | Simple, low-stakes coordination        |
| Fencing Token           | Storage layer         | Yes                   | Yes                      | Distributed locks, lease-based systems |
| Raft Term               | Protocol layer        | Built into Raft       | Yes                      | Consensus-based clusters               |
| STONITH                 | Hardware layer        | No (physical)         | Yes                      | HA database clusters                   |
| Conditional Write (CAS) | Storage layer atomics | Conditional write API | Yes                      | Cloud storage (S3, DynamoDB)           |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                               |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lock TTL alone prevents split brain          | TTL only reclaims the lock after expiry. It doesn't prevent the expired holder from writing AFTER expiry (the holder doesn't know it expired)                         |
| Fencing requires a special storage system    | Any storage that supports CAS (compare-and-swap) or conditional writes can implement fencing token checks                                                             |
| The lock service issues the fencing check    | The fencing check must be in the STORAGE layer, not the lock service. If the client bypasses the lock service, the fencing token check at storage still protects data |
| Fencing token wrapping is not a real concern | In production systems with 64-bit tokens, overflow requires 2^64 lock grants — practically impossible. But 32-bit counters DO overflow in long-running systems        |

---

### 🚨 Failure Modes & Diagnosis

**Stale Leader Writes After GC Pause**

**Symptom:** Intermittent data corruption; write audit log shows two different nodes
writing the same record within a short time window; post-mortem shows one node had
a GC pause at the exact time of the write collision.

**Root Cause:** Lock TTL expired during GC pause; new holder acquired lock; old holder
resumed and wrote without fencing check at storage layer.

**Fix:** Implement fencing token enforcement at the storage write path. Add metrics:
`lock_fencing_rejections_total` counter — non-zero value means fencing is working
correctly (expected during failovers); sudden spike means frequent stale writes.

---

### 🔗 Related Keywords

- `Split Brain` — the failure mode fencing prevents; two nodes simultaneously believing they're authoritative
- `Distributed Locking` — the application context where fencing tokens are most commonly used
- `Clock Skew / Clock Drift` — the problem that fencing solves (don't use wall-clock time for lock expiry enforcement at the resource level)
- `Raft` — uses term number as a built-in fencing epoch for leader transitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  FENCING TOKEN: monotonically increasing integer         │
│  ISSUED: by lock service on each new grant               │
│  USED: attached to every write to the fenced resource    │
│  ENFORCED: storage layer rejects token < highest_seen    │
│  PERSISTED: storage must durably store highest_seen      │
│  EPOCH: same concept in Raft/Paxos (term numbers)       │
│  KEY: enforcement at RESOURCE, not at lock-holder        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Client A holds a distributed lock with fencing token=50. It performs a large write operation that involves multiple storage calls (1. open transaction, 2. write row 1, 3. write row 2, 4. commit). Between step 2 and step 3, the lock expires and Client B acquires the lock with token=51. Client B writes to the same resource with token=51, which is accepted. Now Client A resumes with token=50 and attempts step 3. The storage layer rejects step 3 (token 50 < 51). But step 2 is already written. Describe the resulting state and what application behavior is needed to handle partial writes under fencing rejection.

**Q2.** You're designing a distributed job scheduler where at most one worker should process each job at a time. Workers acquire a lease on a job (1 minute TTL). A worker crashes mid-job. The lease expires, a new worker acquires the job, and starts processing. The crashed worker recovers 2 minutes later and tries to resume. Design the complete fencing mechanism: what token is issued, where is it checked, what happens to the recovered worker's attempts, and how does the system ensure the job is processed exactly once?
