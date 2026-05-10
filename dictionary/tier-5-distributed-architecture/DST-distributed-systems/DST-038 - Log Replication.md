---
id: DST-053
title: Log Replication
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-046, DST-048, DST-050
used_by: DST-050
related: DST-046, DST-048, DST-050, DST-045
tags:
  - distributed
  - replication
  - algorithm
  - deep-dive
  - reliability
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /distributed-systems/log-replication/
---

# DST-049 - Log Replication

⚡ TL;DR - Log replication is the mechanism by which a leader distributes ordered log entries to all followers before marking them committed, making the replicated log — not any individual node's memory — the durable, authoritative source of truth for distributed state.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-046, DST-048, DST-050          |     |
| **Used by:**    | DST-050                            |     |
| **Related:**    | DST-046, DST-048, DST-050, DST-045 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed database accepts a write on the leader. The leader applies it to its in-memory state and replies "success" to the client. The write is nowhere else. Five milliseconds later, the leader's disk fails. The write is gone. The client received a success response for data that no longer exists anywhere. Without a replicated log, "durability" is a lie — it depends entirely on one node's hardware.

**THE BREAKING POINT:**
Adding replicas doesn't automatically solve the problem. If the leader applies the write and sends it asynchronously to followers — but crashes before any follower receives it — the write still disappears. The fundamental issue: when does a write become durable? The answer must be: when it is on enough nodes that no single failure can lose it. This requires a protocol that defines "committed" as "replicated to a majority of nodes before the client receives success."

**THE INVENTION MOMENT:**
The write-ahead log (WAL) was invented in RDBMS systems (IBM System R, 1976) to make single-node crash recovery safe: write to the log before applying to the data structure. Distributed log replication extends this: the log is replicated to multiple nodes, and a write is only "committed" when it appears in a majority of nodes' logs. This is the central mechanism in Raft (AppendEntries RPC) and all Paxos-based systems.

**EVOLUTION:**
1976: IBM System R WAL (single-node crash recovery). 1989: Oracle redo log shipping to standby. 2004: MySQL binlog replication (statement-based, then row-based). 2007: Apache ZooKeeper's ZAB (log replication with total order). 2013: Raft formalizes distributed log replication with AppendEntries, Log Matching Property, and snapshot compaction. 2015+: etcd, CockroachDB, TiKV, InfluxDB — all use Raft log replication. 2022: Kafka KRaft mode — Raft log replication for Kafka's metadata layer.

---

### 📘 Textbook Definition

**Log replication** is the distributed protocol by which a consensus-based system's leader propagates ordered log entries to all follower nodes, ensuring that: (1) **Log Matching Property:** if two nodes' logs contain an entry with the same (index, term), all preceding entries are also identical. (2) **Commit condition:** an entry is committed only after being written to a majority of nodes' logs. (3) **Applied condition:** an entry is applied to the state machine only after being committed — ensuring all nodes eventually apply the same entries in the same order. The replicated log is the single source of truth — any node can reconstruct its state machine by replaying the log from the beginning. Log compaction (snapshotting) periodically truncates the log, replacing old entries with a point-in-time state machine snapshot.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The leader writes each command to a log, replicates it to a majority, marks it committed, then applies it — and every follower does the same, in the same order.

> Log replication is like a court reporter's transcript. The judge (leader) dictates into the record (log). The transcript is copied to multiple archive locations (followers) before any ruling is official (committed). If the judge is replaced (leader election), the new judge reads from the transcript — the transcript IS the record of truth, not any judge's memory. A ruling can only be entered in the official record when a majority of archive copies have it.

**One insight:** The distinction between "committed" (in a majority's logs) and "applied" (executed against state machine) is fundamental. A committed entry is safe from loss. An applied entry has changed the observable state. These are separate events — entries are always committed first, then applied.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Write-before-apply:** The log entry must be durably written to a node's log before that node applies it to its state machine. If apply fails, the log is the recovery source.
2. **Majority commitment:** An entry at index N is committed only when it appears in ≥ (N/2+1) nodes' logs. No single node failure can lose a committed entry.
3. **Log Matching:** If log[i].term == log[i].term on two nodes, then log[0..i] is identical on both. This follows from: leaders never overwrite their log; AppendEntries consistency check rejects mismatches.
4. **Monotone commit index:** The commit index (highest committed log index) never decreases. Applied index never exceeds commit index.
5. **Snapshot replaces prefix:** A snapshot at index S encodes the state machine state after applying all entries [1..S]. Entries [1..S] can be discarded — the snapshot is equivalent.

**DERIVED DESIGN:**
Raft's AppendEntries carries (prevLogIndex, prevLogTerm) — the fingerprint of the entry immediately before the new entries. A follower rejects AppendEntries if its log doesn't have the matching entry at prevLogIndex. The leader backs up its `nextIndex` for that follower and retries. This "consistency check" ensures log divergences are detected and repaired before new entries are appended.

**THE TRADE-OFFS:**
**Gain:** The log is the single source of truth — state is fully recoverable by replaying. Replicas are byte-for-byte identical in their logs (Log Matching).
**Cost:** Write latency = leader-to-follower network RTT (minimum 1 round trip). Log grows indefinitely without compaction. Large snapshots are expensive to transfer.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Distributed durability requires two round-trips minimum: write to log (on leader), replicate to majority, commit. No algorithm can guarantee durability with fewer steps.
**Accidental:** Protocol complexity of log compaction (when to snapshot, how to install snapshots on lagging followers, snapshot file management) is implementation-specific, not fundamental.

---

### 🧪 Thought Experiment

**SETUP:** 3-node Raft cluster. Client writes A, B, C in sequence. After B is committed, the leader crashes. Replica R1 has [A, B, C] in its log (C not committed). Replica R2 has [A, B] only.

**QUESTION:** Can R1 or R2 win election? What happens to C?

**ANALYSIS:**

- R1 has log [A(T1), B(T1), C(T1)]. R2 has log [A(T1), B(T1)]. B is committed (was on majority: leader + R1).
- R1 can win election: its log is at least as up-to-date as R2's. ✓
- R2 cannot win: R1 won't vote for R2 because R1's log is longer with the same terms.
- If R1 wins: it replicates C to R2. C was NOT committed (wasn't on majority before crash). New leader CAN commit C in the new term by replicating it to R2 and using a new heartbeat to advance the commit index. But it only commits C if it can replicate a new entry (Raft's "leader only commits entries from its own term" rule).
- If R1 can't reach quorum for a new entry: C remains in R1's log but is never committed. C will eventually be overwritten by a leader with a different log.

**THE INSIGHT:** Log replication with majority commit makes committed entries (A, B) completely safe — no election can lose them. Uncommitted entries (C) may survive or may not — they're speculative until a quorum acknowledges them.

---

### 🧠 Mental Model / Analogy

> Log replication is like a newspaper's editorial chain of custody. A reporter (client) submits a story (write). The editor (leader) puts it in the editorial queue (log). Copy editors at multiple offices (followers) receive a copy. Only when the majority of offices have the story in their editorial queue does the editor mark it "ready to print" (committed). The paper (state machine) doesn't print it until then. If the editor is fired (leader crashes), the deputy editor (new leader) continues from the editorial queue — the queue IS the newspaper's memory.

**Mapping:**

- **Editorial queue** → replicated log
- **Editor marking "ready to print"** → commit index advance
- **Printing the paper** → applying entry to state machine
- **Majority of offices having the story** → majority replication
- **Deputy editor reading the queue** → new leader catching up from log

Where this analogy breaks down: a real editorial queue doesn't need to be identical across all offices — Raft's log must be byte-for-byte identical (Log Matching) across all committed entries.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Log replication is how a distributed database keeps all its servers in sync. The "leader" server writes every change to a special log file and sends copies to all other servers. Only after enough servers confirm they have the copy does the leader tell the client "success." If the leader crashes, any other server that has the log can take over — the log is the true memory of the system.

**Level 2 - How to use it (junior developer):**
When using etcd, CockroachDB, or any Raft-based system: writes are automatically replicated via the log — you don't control this directly. Key operational parameters: snapshot threshold (how many log entries before taking a snapshot — default 10,000 in etcd), snapshot interval, and follower catch-up via `InstallSnapshot`. Monitor: applied_index vs. raft_index (lag), snapshot frequency, and log compaction duration. Lagging followers trigger expensive snapshot transfers.

**Level 3 - How it works (mid-level engineer):**
Raft log replication in detail: (1) Leader appends entry to its log: `{index: N, term: T, data: cmd}`. (2) Leader sends AppendEntries to all followers: `{prevLogIndex: N-1, prevLogTerm: T', entries: [{N, T, cmd}], leaderCommit: C}`. (3) Follower's consistency check: if `log[N-1].term != T'`: reject. Leader decrements `nextIndex` for that follower and retries with earlier entries. (4) On success: follower appends entries, updates `commitIndex = min(leaderCommit, lastLogIndex)`. (5) Leader receives majority success → advances commitIndex → applies entry to state machine → responds to client. The `nextIndex` and `matchIndex` per-follower tracking on the leader allows independent replication progress per follower.

**Level 4 - Why it was designed this way (senior/staff):**
The Log Matching Property (if two logs agree on (index, term), they agree on all prior entries) is the invariant that makes log replication correct. It holds by induction: (a) leaders only append entries to their log (never overwrite); (b) AppendEntries consistency check ensures that before appending entry N, the follower has entry N-1 matching the leader's term for that index. The inductive chain ensures that if any two nodes agree on entry N, they agree on all entries 1..N. This makes leader election safe: the new leader, having the most up-to-date log, will replicate all committed entries to followers — and followers' logs, though they may have divergent tails, will adopt the leader's version via the AppendEntries consistency check mechanism.

**Expert Thinking Cues:**

- "A client got success but the entry isn't on the new leader after a failover" → The entry was never committed (replicated to a quorum). This is a client-side retry issue, not a replication bug — but clients should use idempotency keys.
- "My Raft follower's applied_index is way behind raft_index" → State machine apply is slow. Profile the apply logic — it's on the critical path.
- "Log keeps growing even with snapshots" → Check snapshot threshold configuration. `etcd --snapshot-count=10000` means snapshot every 10k entries.
- "New node can't join the cluster" → It needs a snapshot install. If snapshot is very large and times out: increase gRPC message size limit.

---

### ⚙️ How It Works (Mechanism)

**Raft log entry structure:**

```
Log entry: {
  index:   uint64  // position in log (1-based)
  term:    uint64  // leader term when appended
  data:    bytes   // command (opaque to Raft)
}

Leader per-follower tracking:
  nextIndex[i]:  next log index to send to follower i
                 (initialized to leader.lastLogIndex + 1)
  matchIndex[i]: highest known-replicated index on follower i
                 (initialized to 0)

commitIndex: highest log index known committed
lastApplied: highest log index applied to state machine
```

**AppendEntries consistency check + repair:**

```
Leader log: [A,T1][B,T1][C,T2][D,T2]
                             commitIdx=3
Follower lag: [A,T1][B,T1][X,T0]  <- diverged at index 3

Leader sends AppendEntries:
  prevLogIndex=3, prevLogTerm=T2, entries=[D,T2]

Follower: log[3].term = T0 != T2 → REJECT

Leader: decrement nextIndex[follower] to 3
  prevLogIndex=2, prevLogTerm=T1, entries=[C,T2][D,T2]

Follower: log[2].term = T1 == T1 → ACCEPT
  Delete log[3] (X,T0) — overwrite with [C,T2][D,T2]
  Follower log now: [A,T1][B,T1][C,T2][D,T2] ✓
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (write to committed):**

```
Client    Leader(L)    Follower(F1)  Follower(F2)
  │           │               │              │
  │─write X──▶│               │              │
  │           │ append (N,T,X)│              │
  │           │ to WAL/log    │              │
  │           │──AppendEntries(prev=N-1,T)─▶│
  │           │──AppendEntries(prev=N-1,T)───────────▶│
  │           │               │              │
  │           │◀─ ack(N) ─────│              │
  │           │ (majority=2 ACKs: committed!)│
  │           │ apply X to SM │              │
  │◀─success─│               │              │
  │           │ leaderCommit=N on next AE   │
  │           │──AppendEntries(leaderCommit=N)─▶│
  │           │──AppendEntries(leaderCommit=N)──────▶│
  │           │               │ apply X     │
  │           │               │             │ apply X
  │           ← YOU ARE HERE (X committed, applied on all)
```

**FAILURE PATH (leader crashes after commit, before notifying F2):**
F2 doesn't know X is committed. New election: F1 wins (has X in log). F1 sends AppendEntries to F2 with leaderCommit=N. F2 applies X. Correctness: the committed entry always propagates via new leader.

**WHAT CHANGES AT SCALE:**
At 100,000 entries/sec: log grows at ~10MB/sec (100 bytes/entry). Without compaction: 900MB/day log. With `snapshot-count=10000`: snapshot every 10 seconds. Snapshot install on lagging follower: full state machine serialization + network transfer. For CockroachDB at 1TB/range: snapshot transfers take minutes. Use learner mode (non-voting follower) for catch-up before joining the quorum.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Leader applies log entries sequentially — the state machine is single-threaded by design in basic Raft. For concurrency: multi-Raft (each key range has its own Raft group, each with its own log). Parallel apply within one Raft group requires the state machine to be commutative — rare in practice. etcd's v3 API uses a single Raft group with sequential apply; CockroachDB uses one Raft group per 512MB range.

---

### 💻 Code Example

**BAD - Applying writes before they're replicated:**

```java
// Naive replicated "database": write to local,
// then async replicate → client sees success
// but data can be lost if leader crashes before replication
public class UnsafeReplicatedDB {
    private final Map<String, String> store = new HashMap<>();
    private final List<Replica> replicas;

    public void write(String key, String value) {
        store.put(key, value); // Apply locally first
        // ACK to client HERE — before replication!
        // Then async replicate — can fail silently:
        replicas.forEach(r ->
            executor.submit(() -> r.replicate(key, value))
        );
        // Client received "success" — but if this
        // process crashes: replicas may never get it
    }
}
```

**GOOD - WAL-first, commit only after majority replication:**

```java
// Raft-style log replication:
// 1. Append to local WAL
// 2. Replicate to majority
// 3. Commit (mark as durable)
// 4. Apply to state machine
// 5. ACK to client
public class RaftLogReplication {
    private final WriteAheadLog wal;
    private final List<Follower> followers;
    private final StateMachine stateMachine;
    private volatile long commitIndex = 0;

    public CompletableFuture<Void> write(
        String key, String value
    ) {
        // Step 1: Append to local WAL (durable first)
        long entryIndex = wal.append(
            new LogEntry(currentTerm, key, value)
        );

        // Step 2: Replicate to all followers (async)
        List<CompletableFuture<Boolean>> replicationFutures =
            followers.stream()
                .map(f -> f.appendEntries(
                    entryIndex - 1,
                    wal.termAt(entryIndex - 1),
                    List.of(wal.entryAt(entryIndex)),
                    commitIndex
                ))
                .collect(Collectors.toList());

        // Step 3: Wait for majority (quorum = n/2+1)
        int quorum = (followers.size() + 1) / 2 + 1;
        return waitForMajority(replicationFutures, quorum)
            .thenRun(() -> {
                // Step 4: Advance commit index
                commitIndex = entryIndex;
                // Step 5: Apply to state machine
                stateMachine.apply(
                    wal.entryAt(entryIndex)
                );
                // Step 6: ACK to client (implicit:
                // CompletableFuture completes here)
            });
        // Client only hears "success" AFTER step 6
    }

    private CompletableFuture<Void> waitForMajority(
        List<CompletableFuture<Boolean>> futures,
        int quorum
    ) {
        AtomicInteger successCount = new AtomicInteger(1);
        // Count self (leader) as 1 success
        CompletableFuture<Void> result = new CompletableFuture<>();
        futures.forEach(f -> f.whenComplete((ok, err) -> {
            if (ok != null && ok) {
                if (successCount.incrementAndGet() >= quorum) {
                    result.complete(null);
                }
            }
        }));
        return result;
    }
}
```

**How to test / verify correctness:**

```bash
# Check etcd log replication state:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=json | jq \
  '.[].Status | {raftIndex, appliedIndex,
    isLeader: (.leader == .header.member_id)}'

# Verify commit vs apply gap:
# raftIndex = highest appended to log
# appliedIndex = highest applied to state machine
# If raftIndex - appliedIndex > 1000: apply is lagging

# Force a snapshot and check size:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  defrag --cluster
# Monitoring: watch for slow apply:
# etcd_server_apply_duration_seconds{quantile="0.99"}
# Alert if > 10ms
```

---

### ⚖️ Comparison Table

| Replication mechanism    | Ordering              | Commit condition          | Recovery mechanism        | Use case            |
| :----------------------- | :-------------------- | :------------------------ | :------------------------ | :------------------ |
| Raft AppendEntries       | Total (by index)      | Majority quorum           | Snapshot + log replay     | etcd, CockroachDB   |
| MySQL binlog (async)     | Total (by binlog pos) | Local only                | Binlog replay from backup | Web apps, analytics |
| PostgreSQL WAL streaming | Total (by LSN)        | Configurable (sync/async) | WAL replay                | OLTP, read replicas |
| Kafka partition log      | Total per partition   | ISR (in-sync replicas)    | Offset replay             | Event streaming     |
| ZAB (ZooKeeper)          | Total (by zxid)       | Majority quorum           | Snapshot + txn log        | Coordination        |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                        |
| :---------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Committed = applied"                           | Committed means written to a majority of logs. Applied means the state machine has processed the entry. These are separate events: commit first, then apply (asynchronously). Applied lags committed by the time it takes to run the state machine transition. |
| "The leader applies the write, then replicates" | The correct order is: append to local log → replicate to majority → commit → apply → ACK client. Applying before replication is the source of data loss bugs in naive implementations.                                                                         |
| "Log compaction (snapshot) loses history"       | Snapshots replace the log prefix with a point-in-time state. History before the snapshot is gone from the log but the state is encoded in the snapshot. Audit logs must be stored separately if full history is required.                                      |
| "A lagging follower can serve reads safely"     | A follower with a stale applied_index serves stale data. For linearizable reads: use ReadIndex (leader confirms commit index) or only read from leader. Follower reads are only safe for "stale OK" use cases.                                                 |
| "Log entries are idempotent by default"         | Log entries are applied exactly once (by tracking lastApplied). But if a client retries a write (after timeout), the entry may be appended AGAIN as a new log entry. Clients must use idempotency keys (unique request IDs) to prevent double-application.     |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Unbounded Replication Lag Causes OOM**

**Symptom:** A follower is consistently 100,000+ entries behind the leader. Leader's memory grows as it buffers entries waiting for the follower to catch up. Eventually: leader OOM, cluster degraded.
**Root Cause:** Follower is processing entries too slowly (slow disk, CPU contention). Leader buffers in-flight entries per follower in memory. With 100k entries × 1KB each = 100MB buffered per slow follower.
**Diagnostic:**

```bash
# Check follower replication lag:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=json | jq \
  '.[].Status | {endpoint: .header.member_id,
    raftIndex, appliedIndex,
    lag: (.raftIndex - .appliedIndex)}'
# If lag > 10000: follower is significantly behind
# Check follower disk I/O:
iostat -x 1 5 | grep -A2 "Device"
```

**Fix:**
BAD: Increasing leader's in-memory buffer to accommodate slow followers.
GOOD: (1) Add follower as learner (non-voting) while catching up, then promote. (2) Limit per-follower in-flight entries (etcd: `--max-send-bytes` per snapshot transfer). (3) Upgrade follower hardware or move to a faster-disk node.
**Prevention:** Monitor follower lag. Alert when lag > 10,000 entries or > 30 seconds. Use learner mode for new nodes.

**Failure Mode 2: Log Compaction Snapshot Blocks Write Path**

**Symptom:** P99 write latency spikes every 10 minutes. Correlates with snapshot creation events. Other operations during snapshot are delayed.
**Root Cause:** Snapshotting the state machine (serializing the entire state to disk) blocks the apply goroutine/thread. While snapshot is running, new log entries can't be applied. The backup of applied entries causes the commit pipeline to stall.
**Diagnostic:**

```bash
# Check etcd snapshot timing:
grep "saved snapshot\|saving snapshot" \
  /var/log/etcd/etcd.log | \
  awk '{print $1, $2, $NF}' | tail -20
# If "saving snapshot" lines show > 1 second:
# Snapshot is blocking the apply path
# Check etcd metrics:
curl -s http://etcd:2381/metrics | grep \
  "etcd_debugging_snap_save_total_duration"
```

**Fix:**
BAD: Snapshotting synchronously on the apply goroutine.
GOOD: (1) Snapshot asynchronously: copy-on-write snapshot of state machine state while apply continues. (2) Increase `--snapshot-count` to reduce snapshot frequency (trade-off: longer log replay on recovery). (3) Use etcd's `--experimental-snapshot-catchup-entries` to fine-tune.
**Prevention:** Benchmark snapshot duration under production load. Alert if snapshot duration > 500ms.

**Failure Mode 3: Security - Log Entry Injection via Unauthenticated AppendEntries**

**Symptom:** A compromised node sends AppendEntries with fabricated log entries to followers. Followers apply the fabricated entries, corrupting their state machines. Legitimate leader can't override because its term is lower (compromised node set a higher term).
**Root Cause:** AppendEntries RPC is accepted from any node without certificate authentication. A rogue node can claim any term number, override followers, and inject arbitrary commands into the replicated log.
**Diagnostic:**

```bash
# Check if Raft peer traffic uses mTLS:
openssl s_client -connect raft-node1:2380 \
  -cert client.pem -key client-key.pem \
  -CAfile ca.pem 2>&1 | grep "Verification"
# If "Verification error": mTLS not configured
# Check etcd peer auth:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  member list --write-out=json | jq '.[].peerURLs'
# If peerURLs start with "http://": INSECURE
```

**Fix:**
BAD: Raft peer communication without mTLS: `--listen-peer-urls=http://0.0.0.0:2380`
GOOD: Enable peer mTLS for all Raft communication:

```bash
etcd --peer-cert-file=/etc/etcd/peer.crt \
     --peer-key-file=/etc/etcd/peer.key \
     --peer-trusted-ca-file=/etc/etcd/ca.crt \
     --peer-client-cert-auth=true \
     --listen-peer-urls=https://0.0.0.0:2380
```

**Prevention:** All production Raft clusters must use mTLS for peer communication. Audit annually with `openssl s_client` check. Rotate peer certificates before expiry.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-046 - Raft (the consensus protocol that uses log replication as its core mechanism)
- DST-048 - Replication Strategies (log replication is the mechanism behind single-leader strategy)
- DST-045 - Leader Election (leader must be elected before log replication begins)

**Builds On This (learn these next):**

- DST-050 - State Machine Replication (log replication is the transport layer for SMR)

**Alternatives / Comparisons:**

- DST-048 - Replication Strategies (log replication vs. leaderless quorum vs. multi-leader)
- DST-050 - State Machine Replication (log replication as the mechanism enabling SMR)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Leader appends entry to log,   |
|                  | replicates to majority, commits |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Durability without a single    |
|                  | point of failure (one node)    |
+------------------+--------------------------------+
| KEY INSIGHT      | Committed = on majority's logs  |
|                  | Applied = in state machine     |
+------------------+--------------------------------+
| USE WHEN         | Need strong consistency +      |
|                  | automatic crash recovery       |
+------------------+--------------------------------+
| AVOID WHEN       | High-throughput leaderless ok  |
|                  | (BASE semantics acceptable)    |
+------------------+--------------------------------+
| TRADE-OFF        | Durability vs. write latency   |
|                  | (RTT to majority + fsync)      |
+------------------+--------------------------------+
| ONE-LINER        | Log is the source of truth;    |
|                  | commit = majority has it       |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-050 State Machine          |
|                  | Replication                    |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Order: append to local log → replicate to majority → commit → apply → ACK client. Never ACK before commit.
2. Log Matching Property: if two logs agree on (index, term), all prior entries are identical. This invariant enables safe leader election and log divergence repair.
3. Committed ≠ Applied. Committed = durable on majority. Applied = state machine has executed it. Monitor both indices.

**Interview one-liner:**
"Log replication in Raft works by having the leader append each client command as a log entry, send AppendEntries RPCs to all followers (with a consistency check via prevLogIndex/prevLogTerm to detect log divergences), and commit the entry once a majority acknowledges receipt — only then applying it to the state machine and responding to the client. The log is the source of truth: any node can reconstruct its state by replaying all committed log entries."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Make the log the authoritative source of truth and treat the current state as a derived cache of the log. This "log is source of truth" principle appears in every system that needs crash recovery, audit trails, or distributed agreement. The state is always reconstructible from the log; the log is the permanent record. When debugging any distributed system failure: start with the log, not the current state.

**Where else this pattern appears:**

- **Database WAL (crash recovery):** PostgreSQL's WAL is the single-node equivalent of Raft log replication. Every data change is written to the WAL before the data page is modified. On crash: replay the WAL from the last checkpoint. The WAL is the source of truth; the data files are a materialized view of the WAL. Streaming replication to standbys replicates the WAL — the same log-first pattern as Raft.
- **Event sourcing (domain-driven design):** In event sourcing, the event store (append-only log of domain events) is the source of truth. The current state of an aggregate is derived by replaying its events. A "read model" (CQRS projection) is equivalent to an applied state machine — a materialized view of the event log. Event sourcing is the application-layer equivalent of Raft log replication: the log is authoritative, the state is derived.
- **Apache Kafka (distributed commit log):** Kafka's core abstraction is a distributed, replicated, append-only log. Producers append to the log; consumers replay from offsets. Log replication across Kafka brokers uses ISR (In-Sync Replicas) — a quorum-based commit mechanism where an entry is committed when all ISR members have it. Kafka's log is explicitly designed as a general-purpose distributed log — the mechanism is identical to Raft's log replication, generalized beyond consensus.

---

### 💡 The Surprising Truth

The "log as source of truth" pattern — central to Raft, event sourcing, Kafka, and database WAL — was not invented for distributed systems. It comes from accounting. Double-entry bookkeeping (invented in the 13th century) treats the transaction journal (ledger) as the source of truth: account balances are derived by summing journal entries, not stored independently. The journal is append-only (you can't erase a booking; you must make a correcting entry). A balance sheet is a materialized view of the journal — derived state, not authoritative state. Every modern distributed "log-first" system is implementing 700-year-old accounting principles. The irony: distributed systems engineers reinvented the ledger while medieval merchants already had the correct mental model. The pattern is: never trust the current state directly; trust only the immutable sequence of state transitions (the log).

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A Raft cluster is operating normally. The leader crashes. The new leader is elected. Clients retry their in-flight writes. Some clients report that their "acknowledged" write (they received a success response before the crash) is now gone — the data doesn't appear in any query. How is this possible if Raft guarantees durability for committed entries?
_Hint:_ The key word is "acknowledged." Distinguish between: (a) the client received a TCP ACK for its write request (network level), (b) the leader appended the entry to its log (not yet replicated), (c) the entry was committed (replicated to majority), (d) the client received the application-level success response. At which point in this sequence did the leader crash? Which of these guarantees durability? What should clients do when they reconnect and their "acknowledged" write is missing?

**Q2 (C - Design Trade-off):** Raft log compaction uses snapshots: the state machine is serialized to a file, and log entries before the snapshot point are discarded. For a CockroachDB range with 100GB of data: (a) how long does snapshotting take, (b) what happens to writes during a snapshot transfer to a lagging follower, and (c) what is the alternative to full-state snapshots for catching up lagging followers?
_Hint:_ A 100GB snapshot at 100MB/s network throughput = 1000 seconds (~17 minutes). During this time: the lagging follower is non-voting. If the cluster loses another node: only 1 of 3 nodes is healthy — below quorum. The cluster stops accepting writes. What is the production safe strategy: (1) learner nodes that don't count toward quorum until caught up, (2) incremental snapshots (only changed pages), or (3) WAL-based catch-up (replay only the uncommitted suffix)?

**Q3 (A - System Interaction):** Kafka uses ISR (In-Sync Replicas) for log replication: an entry is committed when ALL ISR members have it. Raft uses majority quorum: committed when N/2+1 have it. For a cluster of 3: ISR commit requires 3/3 ACKs (stronger), Raft requires 2/3. What is the availability trade-off between these two approaches, and why did Kafka choose ISR while Raft chose majority quorum?
_Hint:_ With ISR: if 1 of 3 replicas falls behind (slow disk), it's removed from ISR. Now ISR=2: commit requires 2/2 ACKs. If another falls behind: ISR=1: commit requires 1/1 ACK — no durability guarantee! Raft always requires majority (2/3): removing slow followers from the "quorum" would require changing the cluster membership. ISR provides throughput-consistency (no slow replica blocks commit); Raft provides durability-consistency (majority is always required). Which failure mode is more acceptable for Kafka's use case vs. a distributed database?

