---
id: DST-027
title: Fencing / Epoch
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-045, DST-012
used_by: DST-045
related: DST-012, DST-045, DST-051
tags:
  - distributed
  - reliability
  - algorithm
  - deep-dive
  - pattern
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /distributed-systems/fencing-epoch/
---

# DST-013 - Fencing / Epoch

⚡ TL;DR - Fencing tokens are monotonically increasing numbers issued on each leadership change (epoch); storage rejects any write from a node whose fencing token is lower than the maximum token seen, making stale leaders physically incapable of corrupting data even after a GC pause or network delay.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-045, DST-012          |     |
| **Used by:**    | DST-045                   |     |
| **Related:**    | DST-012, DST-045, DST-051 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Quorum and STONITH prevent most split-brain cases. But there is a subtle failure scenario they don't cover: what if the old leader's process was paused (garbage collection, OS scheduling), the quorum correctly elected a new leader, but then the old leader's process resumes before it notices it's been replaced? For a brief window: the old leader attempts to write data. STONITH didn't fire (the old leader's hardware is fine). Quorum correctly elected a new leader (the old leader lost its lease). Yet the old leader's in-progress write can still land on storage.

**THE BREAKING POINT:**
A Java-based distributed lock manager. Leader holds a lock for 30 seconds. A GC stop-the-world pause lasting 40 seconds hits the leader process. The DCS (etcd/ZooKeeper) lease expires after 30 seconds. A new leader is elected. The new leader acquires the lock and begins its protected operation. The old leader's JVM GC pause ends. The old leader's process resumes — from ITS perspective, it was just paused for a moment and still holds the lock. Both leaders are now simultaneously executing the "protected" operation. Quorum didn't prevent this: the old leader just woke up from a pause, it's not in a separate partition.

**THE INVENTION MOMENT:**
Martin Kleppmann's "Designing Data-Intensive Applications" (2017) formalized the fencing token pattern as the solution to the "process pause problem." ZooKeeper's `zxid` (Zookeeper Transaction ID) and Chubby's sequencer are the production implementations. The key insight: the storage system (not the client) must enforce recency. If the storage layer rejects writes from tokens below the current epoch: stale leaders cannot write, regardless of their own belief about their status.

**EVOLUTION:**
2000s: ZooKeeper sequencer / `zxid` as fencing primitive. 2006: Google Chubby — distributed lock with sequencer for fencing. 2012: etcd lease with revision ID. 2017: Kleppmann's formalization of the fencing token pattern. 2019+: Google Spanner TrueTime commit-wait — time-based fencing. Kubernetes: leader election via `lease.coordination.k8s.io` objects with resourceVersion fencing.

---

### 📘 Textbook Definition

A **fencing token** (also called an **epoch number**, **term**, **generation**, or **sequencer**) is a monotonically increasing integer issued to a node when it acquires leadership or a distributed lock. The token represents the current "epoch" of authority. The storage layer (or the resource being protected) maintains `max_token_seen`. Before accepting any write, it checks: `if token < max_token_seen: reject(stale_leader)`. Since tokens are monotonically increasing and new leaders receive higher tokens than old ones: any write from an old leader will have a token lower than the current `max_token_seen` — and will be rejected automatically. **Why it works:** The storage rejection mechanism is synchronous and atomic — there is no window where both old and new leader writes can succeed. **Key invariant:** Token monotonicity is guaranteed by the consensus service (etcd/ZooKeeper) that issues tokens. Every new leader gets a strictly higher token than any previous leader.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Give each leader a number (epoch); storage rejects writes with a lower number than the latest — a woken-up stale leader can't overwrite the new leader's data.

> A fencing token is like a parking ticket with a sequence number. The parking attendant only accepts the highest-numbered ticket as valid. If a driver was issued ticket #5 and came back three hours later, finding ticket #7 was issued to someone else in the same spot: the attendant rejects ticket #5. The driver can't dispute it — the number is lower.

**One insight:** Fencing tokens solve the "process resume after GC pause" problem that quorum cannot. A quorum correctly transfers leadership while the process is paused. Fencing tokens prevent the paused process from successfully writing AFTER it resumes — because the storage system has already seen the new leader's higher-numbered token.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Monotone token generation:** Epoch numbers strictly increase. If the current epoch is 5, the next leader gets epoch 6. The consensus service (etcd, ZooKeeper) guarantees this via atomic compare-and-swap.
2. **Storage-side enforcement:** The storage system — not the leader — is responsible for rejecting stale writes. A leader cannot be trusted to check its own recency (it may be paused, partitioned, or have a stale view of the world).
3. **Token transmission:** Every write request includes the sender's current epoch token. The storage system checks `token >= max_token_seen` before applying the write.
4. **Monotone max tracking:** On receiving a write with token T: if `T > max_token_seen`: update max, apply write. If `T < max_token_seen`: reject write (stale leader). If `T == max_token_seen`: apply write (same leader continuing).

**DERIVED DESIGN:**
Fencing tokens are composable with any lease/lock system. The lease/lock grants authority. The token encodes WHEN that authority was granted. The storage system uses the token to enforce recency without knowing anything about the lease protocol.

**THE TRADE-OFFS:**
**Gain:** Storage-level guarantee that a stale leader's writes are rejected, even if the leader's own software fails to detect it's been replaced.
**Cost:** Storage system must be modified to check fencing tokens on every write (not always possible with legacy storage). Token must be passed through the entire call stack (application → client → storage layer).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The storage rejection mechanism (check token, reject if stale) is the irreducible core. This cannot be delegated to the leader.
**Accidental:** Different token sources (etcd revision, ZooKeeper zxid, Raft term+index) are implementation choices. All provide the same monotonicity guarantee.

---

### 🧪 Thought Experiment

**SETUP:** ZooKeeper-based distributed lock. Leader L1 holds lock with token 5. JVM GC pause hits L1 for 40 seconds. ZooKeeper session timeout = 30 seconds. New leader L2 is elected with token 6.

**WITHOUT FENCING:**

- L2 acquires lock, begins writing to shared storage: `PUT account=1000`
- L1's GC pause ends. L1 resumes. L1's code: "I hold the lock, writing..." `PUT account=500`
- Storage receives both. Last write wins. `account=500` (wrong!).
- L2 thinks it wrote 1000. L1 thinks it wrote 500. Neither knows about the other's write.
- Data corruption: the correct final value should have been 1000 (L2's write).

**WITH FENCING TOKENS:**

- L2 acquires lock with token=6. L2 writes: `PUT account=1000 (token=6)`
- Storage: `max_token_seen = 6`. Applies write. `account=1000`.
- L1 resumes. L1's code: "writing..." `PUT account=500 (token=5)`
- Storage: `5 < max_token_seen (6)`. REJECTED. `account=1000` unchanged.
- L2's write is safe. Data integrity preserved.

**THE INSIGHT:** The storage layer's `max_token_seen` tracking is the final safety net. Even if the application layer (L1's code) is completely unaware it's been replaced, the storage-layer fencing token rejection prevents data corruption.

---

### 🧠 Mental Model / Analogy

> A fencing token is like the revision number on a legal document. When a lawyer (leader) sends document revision #5 for signature, but the office has already processed revision #7 (from the new authorized lawyer): they reject revision #5 without even reading it. The rejection is automatic — based solely on the revision number — not on the content of the document.

**Mapping:**

- **Document revision number** → fencing token (epoch)
- **Lawyer** → distributed leader/lock holder
- **Office** → storage system
- **New authorized lawyer** → new elected leader with higher epoch
- **Automatic rejection by revision number** → storage checking `token < max_token_seen`

Where this analogy breaks down: legal document revision checks require human judgment. Fencing token rejection is algorithmic — no judgment needed, no exceptions allowed. That's what makes it reliable.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a distributed system changes leaders, the new leader gets a bigger ID number (epoch). Any server that receives an operation checks: "is this the latest leader's ID, or an old one?" If it's an old one: the operation is rejected. This means a leader that was stuck (due to a software pause) can't corrupt data when it wakes up and tries to operate.

**Level 2 - How to use it (junior developer):**
Using etcd distributed locks: when you acquire the lock, etcd returns a `LeaseID` and a `revision`. Pass both with every write to the protected resource. The protected resource checks that the revision is the latest it's seen. etcd's `txn` (transaction) with `version` checks provides compare-and-swap with built-in fencing. Example: `txn if (version(key) == expected_version) then set(key, value) else fail`.

**Level 3 - How it works (mid-level engineer):**
In Raft: each term is an epoch. When a follower receives a request from a leader with `term < currentTerm`: it rejects the request (leader is stale). When a leader receives a response with a higher term: it immediately steps down. This is fencing built into the Raft protocol itself — the term IS the fencing token. In ZooKeeper: the `zxid` (ZooKeeper transaction ID) is a 64-bit number where the high 32 bits are the epoch (leader generation) and low 32 bits are the transaction counter. A node that proposes a write with an old epoch's zxid will be rejected. In etcd distributed locks: the `revision` (Raft log index) is the fencing token — it strictly increases with every operation.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental insight is that in an asynchronous system, a node cannot determine its own current authority from local state alone. Local state can be arbitrarily stale (GC pause, OS scheduling, network delay). The ONLY source of truth about current authority is external to the node — specifically, the consensus service that issued the fencing token AND the storage system that tracks `max_token_seen`. Fencing tokens create a chain of authority verification: consensus service issues tokens monotonically → leader presents token with each write → storage verifies token recency. This chain means that even if the consensus service's decision is slow to propagate to the leader's local state (e.g., during a GC pause), the storage system's token check catches it. The storage check is the "last line of defense" that requires no cooperation from the leader. Google Spanner extends this concept with TrueTime: instead of a discrete epoch token, Spanner uses a time-bounded commit-wait (`TrueTime + uncertainty bound`) as a continuous fencing mechanism — no write is committed until the commit timestamp is provably in the past for all nodes.

**Expert Thinking Cues:**

- "My ZooKeeper-based leader is writing stale data after a GC pause" → Pass the ZooKeeper `sessionId + epoch` as a fencing token with every storage write. Storage must reject writes with lower epoch. ZooKeeper's `zxid` provides the epoch.
- "How does Kubernetes prevent two pods from claiming leadership?" → Kubernetes leader election uses `lease.coordination.k8s.io` objects. The leader acquires a Lease with `resourceVersion`. Before updating: it checks that the current Lease `resourceVersion` matches (compare-and-swap). If another pod updated the Lease: the old leader's write fails — this IS fencing via resourceVersion.
- "HDFS NN HA uses fencing scripts — what is that?" → HDFS NameNode HA (without Raft) uses external fencing scripts (SSH to kill old NN process, revoke Kerberos credentials). This is STONITH-style fencing, not token-based. Token-based fencing for HDFS would require the DataNodes to check NN epoch tokens before accepting block writes.
- "What's a generation number in Kafka?" → Kafka consumer group has a `generation` — a monotonically increasing epoch assigned by the group coordinator on each rebalance. Consumers include their generation in fetch requests. If a consumer's generation is stale: the broker rejects the request. This is fencing applied to consumer group membership.

---

### ⚙️ How It Works (Mechanism)

**Fencing token lifecycle:**

```
Consensus Service (etcd/ZooKeeper)
  ├── Leader L1 elected: issues token=5
  │     L1 → writes with token=5
  │     Storage: max_token_seen=5, OK
  │
  ├── L1 GC pause starts (40s pause)
  ├── L1 lease expires (30s TTL)
  ├── L2 elected: issues token=6
  │     L2 → writes with token=6
  │     Storage: 6>5, max_token_seen=6, OK
  │
  └── L1 GC pause ends, L1 resumes:
        L1 → writes with token=5
        Storage: 5 < max_token_seen(6), REJECT
        L1 write fails safely. No corruption.

Token monotonicity guarantee (etcd):
  Leader election key: "leader-lock"
  etcd revision is a global monotone counter.
  On acquire: revision=10 (epoch=10)
  On re-acquire by new leader: revision=11 (epoch=11)
  revision 11 > 10 always (etcd atomicity guarantee)
```

**ZooKeeper sequencer (fencing built-in):**

```
ZooKeeper lock with sequencer:
  L1 creates: /lock/lock-0000000005 (sequence node)
  L1 gets token: zxid=0x300000012
               (epoch=3, txcount=18)

  L1 passes zxid=0x300000012 to storage
  Storage: max_zxid_seen = 0x300000012, OK

  ZooKeeper epoch increments (L1 session expires):
  New epoch: 4. L2 creates: /lock/lock-0000000006
  L2 gets token: zxid=0x400000001
               (epoch=4, txcount=1)

  L1 resumes, passes old zxid=0x300000012
  Storage: 0x300000012 < max_zxid_seen=0x400000001
           epoch 3 < epoch 4 → REJECT
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (etcd distributed lock with fencing):**

```
etcd (Raft)    Lock Client L1      Storage System
    │                │                   │
    │◀─acquire lock──│                   │
    │─grant: token=7─▶│                  │
    │                │──write(key, t=7)──▶│
    │                │    max_seen=7      │
    │                │◀────OK─────────────│
    │                │                   │
GC PAUSE HITS L1 (45 seconds)
L1 lease expires│                   │
    │           │                   │
    │◀─acquire──────────────L2      │
    │─grant: token=8──────▶L2      │
    │                L2──write(key, t=8)─▶│
    │                    max_seen=8  │
    │                L2◀──OK─────────│
    │                   │           │
GC PAUSE ENDS. L1 resumes.
    │                │                   │
    │       L1 (thinks it has lock)       │
    │                │──write(key, t=7)──▶│
    │                │  7 < max_seen(8)   │
    │                │◀──REJECT (stale)───│
    │ ← YOU ARE HERE: L1's write rejected │
    │                │ L2's data intact   │
```

**FAILURE PATH (fencing without storage cooperation):**
L1 writes directly to a storage system that doesn't check fencing tokens (e.g., a plain POSIX filesystem). L1's write succeeds. Fencing requires BOTH: (1) the leader passes the token, AND (2) the storage system checks it. If either is missing: fencing doesn't work.

**WHAT CHANGES AT SCALE:**
At scale: the fencing token check adds one integer comparison per write (negligible). The critical scaling concern: every write must carry the token through the entire call stack (API layer → business logic → storage layer). In microservice architectures: a fencing token from the service's leader election must be propagated through all downstream service calls. Missing the token at any hop breaks the fencing chain. Distributed tracing headers are a natural carrier for fencing tokens in microservice environments.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multi-region: a node in US-East holds token=10. Failover to EU-West: token=11. If US-East region recovers and tries to re-assert leadership with token=10: any storage system in EU-West (which has seen token=11) will reject US-East's writes. But if US-East has its own storage with max_seen=10: US-East can still write locally (no epoch check from EU-West storage). This is the "fencing only works within a single storage boundary" limitation. Cross-region fencing requires a global storage layer (Spanner, DynamoDB Global Tables) that maintains a single `max_token_seen` across all regions.

---

### 💻 Code Example

**BAD - Distributed lock without fencing (GC pause vulnerable):**

```java
// No fencing token passed to storage
// Vulnerable to process pause between lock check and write
public class UnsafeLockClient {
    private final ZooKeeper zk;
    private final Storage storage;

    public void doProtectedWrite(String key, String value)
        throws Exception {
        // Acquire lock (ZooKeeper session-based)
        String lockPath = zk.create("/lock/lock-",
            new byte[0], ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.EPHEMERAL_SEQUENTIAL);

        // Check if we have the lowest sequence (we hold lock)
        if (weHoldLock(lockPath)) {
            // DANGER: GC pause can happen HERE (40+ seconds)
            // By the time we resume:
            // - Our ZK session may have expired
            // - Another leader may have been elected
            // - But we still proceed to write:
            storage.write(key, value);  // NO TOKEN CHECK
            // This write may corrupt data if a new leader
            // also wrote after our session expired
        }
        zk.delete(lockPath, -1);
    }
}
```

**GOOD - Distributed lock with fencing token (GC-pause safe):**

```java
// Fencing token passed with every storage write
// Storage rejects writes with stale tokens
public class SafeLockClient {
    private final ZooKeeper zk;
    private final FencedStorage storage;

    public void doProtectedWrite(String key, String value)
        throws Exception {
        // Acquire lock AND get fencing token in one atomic op
        LockResult lock = acquireLockWithToken();
        long fencingToken = lock.getToken();
        // token = ZooKeeper zxid at time of lock acquisition
        // Strictly monotone: newer locks always get higher token

        try {
            // GC pause can happen here — doesn't matter!
            // When we resume: we pass our (now stale) token
            // FencedStorage checks: token < max_seen → REJECT

            FencedWriteResult result = storage.writeWithFence(
                key, value, fencingToken
            );
            // Result: OK (if token is current)
            //         STALE_LEADER (if new leader took over)

            if (!result.isSuccess()) {
                throw new StaleLeaderException(
                    "Fencing token " + fencingToken
                    + " rejected — newer leader exists. "
                    + "Current max: " + result.getMaxToken()
                );
            }
        } finally {
            releaseLock(lock);
        }
    }

    // etcd-based implementation with built-in fencing
    public void etcdFencedWrite(
        EtcdClient etcd, String protectedKey, String value) {
        // Get current revision (this IS the fencing token)
        GetResponse leaderInfo = etcd.get(
            ByteSequence.from("leader-lock", UTF_8)
        ).get();
        long fencingToken = leaderInfo.getKvs().get(0)
            .getModRevision(); // monotone revision = epoch

        // Write with compare-and-swap using revision as fence
        // If another leader wrote with higher revision:
        // this txn will fail (version check fails)
        TxnResponse txn = etcd.txn()
            .If(new Cmp(
                ByteSequence.from(protectedKey, UTF_8),
                Cmp.Op.LESS,  // current version < our token
                CmpTarget.VERSION(fencingToken)
            ))
            .Then(Op.put(
                ByteSequence.from(protectedKey, UTF_8),
                ByteSequence.from(value, UTF_8),
                PutOption.DEFAULT
            ))
            .Else(/* fail — our token is stale */)
            .commit().get();

        if (!txn.isSucceeded()) {
            throw new StaleLeaderException(
                "Fencing token " + fencingToken + " is stale"
            );
        }
    }
}

// Storage layer: MUST validate fencing tokens
public class FencedStorage {
    private final AtomicLong maxTokenSeen = new AtomicLong(0);
    private final Map<String, String> store = new ConcurrentHashMap<>();

    public FencedWriteResult writeWithFence(
        String key, String value, long token) {
        // Atomic compare-and-update of max token
        long currentMax = maxTokenSeen.updateAndGet(
            current -> token > current ? token : current
        );

        if (token < currentMax) {
            // Stale write: token is lower than max seen
            // This leader's authority has been superseded
            return FencedWriteResult.stale(currentMax);
        }

        // Token is current (or equal) — apply write
        store.put(key, value);
        return FencedWriteResult.success(token);
    }
}
```

**How to test / verify correctness:**

```bash
# Simulate GC pause scenario with etcd + fencing:

# 1. Acquire lock (note revision as fencing token):
ETCDCTL_API=3 etcdctl lease grant 30
# Output: lease X granted with TTL(30s)
ETCDCTL_API=3 etcdctl put --lease=X leader "node1"
# Note the revision in the output: e.g., revision: 42

# 2. Simulate "pause" by revoking lease manually
#    (simulates GC pause causing lease expiry):
ETCDCTL_API=3 etcdctl lease revoke X

# 3. New leader acquires with higher revision:
ETCDCTL_API=3 etcdctl lease grant 30
ETCDCTL_API=3 etcdctl put --lease=Y leader "node2"
# New revision: e.g., revision: 47

# 4. Old leader tries to write with old token (rev 42):
#    Using txn with version check:
ETCDCTL_API=3 etcdctl txn \
  --interactive=false <<'EOF'
version("protected-key") = "42"

put protected-key "stale-value"

EOF
# Expected: "FAILURE" — version check fails
# New leader (token 47) already updated — old token rejected
```

---

### ⚖️ Comparison Table

| Fencing mechanism                | Token source        | Enforcement point         | Handles GC pause | Complexity      |
| :------------------------------- | :------------------ | :------------------------ | :--------------- | :-------------- |
| ZooKeeper sequencer / zxid       | ZK transaction ID   | Storage checks zxid       | Yes              | Medium          |
| etcd revision                    | Raft log index      | etcd txn version check    | Yes              | Low             |
| Raft term                        | Leader term number  | Built-in to Raft protocol | Yes              | None (built-in) |
| STONITH                          | N/A (physical kill) | Hardware power control    | Yes              | High            |
| Kubernetes lease resourceVersion | etcd revision       | kube-apiserver CAS        | Yes              | Low             |
| TrueTime (Spanner)               | GPS/atomic clock    | Commit-wait timestamp     | Yes              | Very high       |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                     |
| :---------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Quorum makes fencing unnecessary"                          | Quorum prevents two majorities from proceeding DURING a partition. But a process paused by GC, then resumed, doesn't need a partition to cause damage — it just needs the storage system to not check its token. Quorum and fencing solve different threat scenarios and are complementary.                                 |
| "The leader can check if it's still current before writing" | This check is inherently racy. Between "check current leadership" and "execute write": arbitrary time can pass (GC pause, OS scheduling). The check can return "yes, still leader" and then the write lands after a new leader has been elected. Only storage-side token verification (synchronous with the write) is safe. |
| "HDFS NN fencing is fencing tokens"                         | HDFS NameNode HA fencing is STONITH-style fencing (SSH to kill old NN, revoke Kerberos credentials, network port fencing). It is NOT token-based fencing. HDFS DataNodes don't check epoch tokens from the NameNode — they rely on STONITH having killed the old NN before the new one accepts writes.                      |
| "A fencing token is the same as a session ID"               | Session IDs identify WHO is communicating but don't encode WHEN authority was granted. Two session IDs can be active simultaneously. A fencing token encodes a monotone sequence number — only the HIGHEST token is valid. The comparison is the key: `token < max_seen → reject`. Session IDs have no such ordering.       |
| "Fencing only applies to distributed locks"                 | Fencing tokens apply to any resource with a single-authority requirement: Kafka consumer group generation (fencing stale consumers), Kubernetes leader election (fencing stale controllers), database cluster primary epoch (fencing stale primaries). The pattern is universal, not limited to lock managers.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale Leader Writes Data After GC Pause (No Token Check in Storage)**

**Symptom:** A distributed lock is held by a process that experiences a long JVM GC pause. After recovery: monitoring shows two "successful" writes to the same key at nearly the same time. The stored value alternates between two values on successive reads. Data corruption confirmed.
**Root Cause:** Storage system does not validate fencing tokens. When the GC-paused process resumed: it wrote with its (now stale) lock. The new leader had already written with the current lock. Both writes landed on storage (no epoch check). Last-write-wins by wall-clock timestamp — non-deterministic result.
**Diagnostic:**

```bash
# Check if your storage layer validates fencing tokens:
# In etcd: use txn with version check — built-in fencing
# In a custom store: check if writes include token and
# the store validates it.

# Check JVM GC pause duration (was a long pause the trigger?):
# On JVM process: enable GC logging:
java -Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20m
grep "Pause Full" gc.log | awk '{print $NF}' | sort -n | tail -5
# If pauses > lease TTL (e.g., >30s): GC pause is the cause.
# Fix: tune GC (G1GC, ZGC for < 10ms pauses), increase lease TTL,
# or implement fencing tokens in the storage layer.
```

**Fix:**
BAD: Storage write with no fencing check: `storage.put(key, value)`.
GOOD: Storage write with fencing: `storage.putIfTokenCurrent(key, value, fencingToken)` — throws `StaleLeaderException` if `fencingToken < max_seen_token`.
**Prevention:** Use ZGC or Shenandoah GC for Java lock holders (pause < 10ms). Set lease TTL well above P99 GC pause time (100x safety margin). Always pass fencing tokens with protected writes.

**Failure Mode 2: Fencing Token Not Propagated Through Call Stack**

**Symptom:** etcd-based leader election with fencing tokens. A failover correctly issues a new token to the new leader. But the protected resource still receives writes from the old leader — the fencing check passes when it shouldn't.
**Root Cause:** The fencing token was not propagated through the full call chain. The leader service received the token from etcd and validated it on the first hop. But it called a downstream microservice that wrote to the protected resource WITHOUT passing the token. The downstream service has no token to check and accepts all writes.
**Diagnostic:**

```bash
# Trace fencing token propagation through request headers:
# In distributed tracing: check if "X-Fencing-Token" header
# is present at all service hops:
grep "X-Fencing-Token" access.log | tail -20
# If missing in downstream service logs:
# Token is not being forwarded

# Check storage layer logs for rejected vs accepted writes:
grep "fencing_token" /var/log/storage/writes.log | \
  grep "REJECTED" | wc -l
# If zero rejections even during failovers: storage is
# likely not checking tokens at all
```

**Fix:**
BAD: Token validated only at the entry point, not forwarded.
GOOD: Pass fencing token as a propagated header (HTTP: `X-Fencing-Token`, gRPC: metadata field) through every service hop. Final storage write includes the token; storage validates it.
**Prevention:** Enforce fencing token in a middleware layer (interceptor/filter) that all writes must pass through. Add integration test: failover → write via all service hops → verify old epoch writes are rejected by storage.

**Failure Mode 3: Security - Fencing Token Forgery via Unsecured Consensus Service API**

**Symptom:** An attacker with access to the internal network connects directly to the etcd API and issues `put leader-lock "<malicious-payload>"`, receiving a high revision number (fencing token). The attacker then uses this token to issue writes to the protected resource — writes that are accepted as "current" by the storage fencing check.
**Root Cause:** etcd API (port 2379) is exposed without authentication on the internal network. The attacker can issue arbitrary etcd operations, including acquiring fencing tokens. The fencing mechanism is only as secure as the token issuer.
**Diagnostic:**

```bash
# Check if etcd requires client certificate authentication:
curl -s http://etcd-endpoint:2379/v3/kv/put \
  -X POST \
  -d '{"key":"bGVhZGVyLWxvY2s=","value":"aGFja2Vk"}'
# If returns: {"header":{"revision":...}} (not auth error):
# etcd accepts unauthenticated writes → fencing tokens unsafe

# Check etcd auth status:
ETCDCTL_API=3 etcdctl auth status \
  --endpoints=$ETCD_ENDPOINTS
# Expected: "Authentication Status: true"
# If false: authentication is disabled → security issue
```

**Fix:**
BAD: `etcd --listen-client-urls=http://0.0.0.0:2379` (no TLS, no auth).
GOOD: (1) Enable client mTLS: `--client-cert-auth=true --trusted-ca-file=ca.crt`. (2) Enable RBAC: `etcdctl auth enable`. (3) Restrict etcd API access to Kubernetes control plane nodes only (NetworkPolicy, security group). (4) Audit all etcd write operations via audit logging.
**Prevention:** Treat etcd as the root of trust for your cluster. Compromise of etcd = compromise of all fencing tokens = split-brain attacks possible. Security scanning: verify etcd requires mTLS before each production deployment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-045 - Leader Election (fencing tokens are issued per leadership term — you must understand leader election to understand what an epoch represents)
- DST-012 - Split Brain (fencing tokens are the storage-level defense mechanism after split brain begins — understand the threat before the solution)

**Builds On This (learn these next):**

- DST-045 - Leader Election (Raft terms are built-in fencing tokens — the connection between leader election and fencing is fundamental)

**Alternatives / Comparisons:**

- DST-012 - Split Brain (STONITH is an alternative fencing mechanism at the hardware level)
- DST-045 - Leader Election (Raft terms as built-in fencing vs. external token-based fencing)
- DST-051 - Quorum (quorum prevents split brain before it starts; fencing tokens prevent damage after a stale leader resumes)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Monotone epoch number issued   |
|                  | per leadership; storage rejects|
|                  | writes below max seen          |
+------------------+--------------------------------+
| PROBLEM SOLVED   | GC-paused stale leader resumes |
|                  | and writes after replacement   |
+------------------+--------------------------------+
| KEY INSIGHT      | Storage (not leader) enforces  |
|                  | recency — leader can't be      |
|                  | trusted to detect own staleness|
+------------------+--------------------------------+
| USE WHEN         | Any distributed lock, leader,  |
|                  | or primary-replica with writes |
+------------------+--------------------------------+
| AVOID WHEN       | Storage system can't validate  |
|                  | tokens (legacy/external stores)|
+------------------+--------------------------------+
| TRADE-OFF        | Stale writes rejected (safety) |
|                  | vs. one extra integer check    |
|                  | per write (negligible cost)    |
+------------------+--------------------------------+
| ONE-LINER        | Higher epoch = newer authority;|
|                  | storage rejects lower epochs   |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-045 Leader Election,       |
|                  | DST-012 Split Brain            |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Fencing token = monotonically increasing number issued per leadership epoch. The storage system rejects writes from any node whose token is lower than the highest token it has seen. A stale leader CANNOT write — regardless of whether it knows it's stale.
2. The storage system must validate the token on every write. The leader cannot be trusted to self-report its own staleness (it may be paused, slow, or simply wrong). Storage-side enforcement is the invariant.
3. Quorum prevents two leaders from being elected. Fencing prevents a stale leader from writing AFTER it's been replaced. Both are needed: quorum for election safety, fencing for write safety.

**Interview one-liner:**
"Fencing tokens (epochs) are monotonically increasing numbers issued by a consensus service (etcd/ZooKeeper) to each new leader. Every write to the protected resource includes the leader's current token. The storage system maintains `max_token_seen` and rejects any write with a lower token. This prevents a leader that was paused by GC and then resumed from corrupting data — even if it doesn't know it's been replaced. Quorum prevents two leaders from being elected; fencing prevents the old leader from writing after it's been replaced."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Never let an actor be the sole judge of its own current authority. In any system where authority can change hands, build verification of current authority into the resource being protected — not into the actor claiming authority. The actor's self-assessment may be arbitrarily stale (pauses, delays, bugs). The resource's check is synchronous with the operation and cannot be bypassed. This is the "external enforcement" principle: put the invariant check at the boundary where it is physically impossible to bypass, not in the code of the potentially-compromised actor.

**Where else this pattern appears:**

- **OAuth2 token revocation and JWT expiry:** When a user's session is revoked (logout, password change), their JWT token may still be "valid" by its own embedded claims (not yet expired). The resource server (API) must check a token revocation list or short expiry — the JWT itself cannot be trusted to report its own invalidity. The JWT `iat` (issued-at) claim is a fencing token: if the server's revocation timestamp for this user is higher than `iat`, the token is rejected. Same pattern: monotone timestamp, resource-side enforcement, actor-side claims can't be trusted.
- **Optimistic concurrency control (database `version` column):** An entity update includes the entity's current `version`. The database applies: `UPDATE entity SET ..., version=version+1 WHERE id=X AND version=<expected>`. If another writer incremented `version`: this update fails. The `version` column is a fencing token for database row updates — prevents stale writes from overwriting concurrent modifications. Same monotone-counter + resource-side-check pattern applied to rows instead of leaders.
- **Kubernetes controller reconciliation (ResourceVersion):** A Kubernetes controller reads a resource (`Pod`, `Deployment`) and writes an update. The update includes the resource's current `resourceVersion`. The kube-apiserver applies the update only if `resourceVersion` matches the current stored version. If another controller or user updated the resource concurrently: the `resourceVersion` has changed → the update is rejected. The Kubernetes `resourceVersion` is a fencing token for controller updates — the API server enforces it, not the controller.

---

### 💡 The Surprising Truth

The GC pause problem that fencing tokens solve — a process pausing for longer than its lease TTL and then resuming believing it still holds authority — was famously described by Martin Kleppmann using a real scenario from a major distributed systems failure. But the most striking real-world example predates the formalization: it's a common JVM behavior. The HotSpot JVM with Concurrent Mark Sweep (CMS) GC could produce stop-the-world pauses of 10-60+ seconds in production systems due to "concurrent mode failure" — when the GC couldn't complete before the old generation filled up. This means: any JVM-based distributed system (HBase, Cassandra, ZooKeeper, Kafka, Elasticsearch) running CMS GC was routinely susceptible to stale-leader writes. The surprising truth: for over a decade, every major JVM-based distributed system was vulnerable to exactly the failure mode that fencing tokens solve — and the fix wasn't algorithmic but pragmatic: either move to ZGC (pause < 10ms), use Go or Rust (no stop-the-world GC), set lease TTL >> P99 GC pause, or implement fencing tokens in the storage layer. Most production systems solved it by tuning GC and lease TTL, not by implementing proper fencing tokens.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** Raft terms are described as "built-in fencing tokens" in this entry. But Raft followers also reject AppendEntries from leaders with stale terms (`if term < currentTerm: reject`). How does this Raft behavior differ from storage-level fencing? Specifically: what happens if a Raft leader with term=5 sends a write to a follower that has already seen term=6? And what does the follower do next — just reject or also inform the leader?
_Hint:_ Raft follower rejects and responds with its current term (6). The stale leader (term=5) receives a response with `term=6 > 5`. Per Raft protocol: the leader immediately sets `currentTerm=6` and steps down to follower. This is "self-fencing" — the leader uses the rejection response to learn it's stale and removes itself from authority. Storage-level fencing (in external storage systems outside Raft) does NOT have this self-notification mechanism — the stale leader must detect failure through the rejected write alone. What implications does this have for retry logic in systems that don't implement Raft's self-step-down?

**Q2 (C - Design Trade-off):** Google Spanner uses TrueTime commit-wait as its fencing mechanism: before a transaction is committed, Spanner waits until the commit timestamp is provably in the past for all nodes (i.e., `now().latest < commit_timestamp`). This eliminates discrete epoch tokens in favor of continuous time-based fencing. What is the advantage of TrueTime fencing over discrete epoch fencing for global distributed transactions? And what is the fundamental requirement (hardware) that makes TrueTime possible but unachievable in most datacenters?
_Hint:_ Discrete epoch fencing requires a coordinator (etcd, ZooKeeper) to assign tokens — the coordinator is a bottleneck and a potential SPOF. TrueTime fencing is peer-to-peer: each node knows its own committed writes are "earlier" than any future commit from any other node (within error bounds). The hardware requirement: GPS receivers and atomic clocks in every datacenter to bound clock uncertainty to ±7ms. Standard NTP has ±100ms uncertainty — too large for commit-wait (you'd wait 100ms per transaction). What does this mean for emulating Spanner-style TrueTime in a standard cloud datacenter without GPS hardware?

**Q3 (D - Root Cause):** A Kubernetes controller (controller-manager) is running leader election via the `lease.coordination.k8s.io` API. During a Kubernetes API server upgrade: there is a 30-second window where the API server is restarting. The controller-manager cannot renew its lease. After the API server restarts: the controller-manager reconnects and successfully renews the lease. A second controller-manager pod (running in another AZ) noticed the lease renewal failure and tried to acquire the lease — but the API server came back before the second controller could complete acquisition. Is there a risk of dual-leadership during the 30-second outage window? What prevents the second controller from acting as leader during the window, even though it successfully detected the first controller's lease renewal failure?
_Hint:_ The second controller can only act as leader AFTER it has SUCCESSFULLY acquired the lease — i.e., AFTER it has written its identity to the Lease object in etcd AND received a successful response from the API server. If the API server is down: neither controller can confirm leadership. Both should be in "waiting" state. The first controller continues executing its reconciliation loop using its LOCAL state (it thinks it's leader). The second controller also may continue executing (it also thinks it's leader, based on local state). The Lease object hasn't been updated — but both controllers' LOCAL lease-check timers may have expired. This is the "client-side lease check is not fencing" problem.
