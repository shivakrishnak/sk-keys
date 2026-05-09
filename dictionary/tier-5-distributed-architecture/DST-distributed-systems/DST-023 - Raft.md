---
id: DST-023
title: Raft
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-026, DST-028
used_by: DST-027
related: DST-024, DST-026, DST-027
tags:
  - distributed
  - consensus
  - algorithm
  - deep-dive
  - reliability
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /distributed-systems/raft/
---

# DST-023 - Raft

⚡ TL;DR - Raft is a consensus algorithm designed for understandability that solves replicated log agreement by decomposing the problem into three independently-reasoned subproblems: leader election, log replication, and safety.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-022, DST-026, DST-028 |     |
| **Used by:**    | DST-027                   |     |
| **Related:**    | DST-024, DST-026, DST-027 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a replicated database. Five nodes. The primary accepts all writes and asynchronously replicates to replicas. The primary crashes. Which replica has the most up-to-date data? How do you elect a new primary without data loss? How do you ensure no two replicas believe they're the primary simultaneously? Without a formal consensus protocol, these questions have no safe answers — every implementation either loses data, creates split-brain, or requires manual operator intervention.

**THE BREAKING POINT:**
Paxos (the dominant consensus algorithm from 1989-2013) is notoriously difficult to understand and implement correctly. Google's Paxos implementation took years and required writing a clarifying paper ("Paxos Made Live") that still didn't fully specify the algorithm. Independent implementations diverged in subtle ways. The distributed systems community lacked a reference algorithm that engineers could implement correctly from the specification alone.

**THE INVENTION MOMENT:**
Diego Ongaro and John Ousterhout at Stanford published "In Search of an Understandable Consensus Algorithm" (USENIX ATC 2014 — originally a PhD dissertation). Raft's core insight: decompose consensus into three independent subproblems — leader election, log replication, safety — each specified in complete, unambiguous terms. The paper included a formal safety proof and a TLA+ specification. Undergraduate students with no distributed systems background could implement a correct Raft node from the paper alone.

**EVOLUTION:**
2014: Raft paper published. 2015: etcd adopts Raft (powers all Kubernetes state). 2015: CockroachDB adopts Raft (multi-Raft per range). 2015: TiKV adopts Raft. 2016: JRaft (Java Raft library). 2018: InfluxDB uses Raft. 2022: Apache Kafka KRaft mode (Kafka-native Raft, replaces ZooKeeper). 2023: FoundationDB, Rook, numerous cloud-native databases use Raft. Raft is now the most widely-deployed consensus algorithm in production distributed systems.

---

### 📘 Textbook Definition

**Raft** is a consensus algorithm that manages a replicated log: a sequence of commands that all servers apply to their state machines in the same order, producing identical state on all replicas. Raft guarantees: (1) **Election Safety:** at most one leader per term. (2) **Leader Append-Only:** a leader never overwrites or deletes entries in its log; it only appends. (3) **Log Matching:** if two logs contain an entry with the same index and term, the logs are identical in all entries up through that index. (4) **Leader Completeness:** if a log entry is committed in a given term, that entry will be present in the logs of all leaders for higher-numbered terms. (5) **State Machine Safety:** if a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for that index. These five properties together guarantee safety even under arbitrary server failures.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Raft elects a leader to sequence all writes, replicates each write to a majority before confirming it, and re-elects automatically when the leader fails.

> Raft is like a company with a single authorized signer. Only the CEO (leader) can sign contracts (commit entries). Every contract must be co-signed by a majority of board members (replicated to quorum) before it's legally binding (committed). If the CEO becomes incapacitated, the board holds an emergency election and picks a new CEO. The new CEO only signs contracts from their tenure onward — old CEO's unsigned contracts are either ratified or discarded.

**One insight:** The key to Raft's correctness is that committed entries are never lost because: (a) a majority must replicate before commit, and (b) the new leader must have gotten votes from a majority — which overlaps with the majority that received the committed entries. This intersection means the new leader always has all committed entries.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **One leader per term:** The leader sequences all operations. Two leaders in the same term would create conflicting logs. The quorum requirement makes this impossible.
2. **Commit only after majority replication:** An uncommitted entry can be lost if the leader fails before replication. Once replicated to a majority and committed: the quorum overlap invariant guarantees any future leader has the entry.
3. **Leader log is authoritative:** Leaders never change their own committed entries. Followers adopt the leader's log by overwriting conflicting entries (after learning the leader's log matching point).
4. **Log Matching Property:** If two nodes have an entry with the same (index, term): all preceding entries are also identical. This follows from: leaders append one entry at a time, and AppendEntries consistency check rejects divergent logs.

**DERIVED DESIGN:**
Three subproblems with independent specifications: (1) Leader election (DST-022): who sequences? (2) Log replication: how does the sequence propagate? (3) Safety: what invariants are maintained under all failure scenarios? By specifying each independently, Raft becomes implementable in stages without conflating concerns.

**THE TRADE-OFFS:**
**Gain:** Formally specified, implementable from paper, proven correct, strong safety properties.
**Cost:** Leader is a bottleneck (all writes route through one node). Leader failure causes write unavailability for election duration. Multi-Raft required for horizontal throughput scaling.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Consensus in an asynchronous network with crash failures (Fischer-Lynch-Paterson: impossible to solve deterministically). Raft is a practical solution: it provides safety always, liveness only when a stable majority can communicate.
**Accidental:** Paxos's ambiguity about leadership, multi-Paxos, the role of acceptors vs. learners — Raft eliminates all of this through explicit design.

---

### 🧪 Thought Experiment

**SETUP:** 3-node Raft cluster. Leader L replicates entry E to Node A (success) but NOT Node B before crashing. Quorum = 2. Was E committed?

**ANALYSIS:**

- E replicated to L + A = 2 nodes = majority of 3. L committed E and responded "success" to client.
- L crashes after committing but before sending "committed" to A and B.
- New election: A or B can win (both are candidates for next term).
- If A wins: A has E in its log. A sends AppendEntries to B (with E). B adopts A's log. E is now on all nodes. Correct.
- If B wins: B's log is missing E. But B CANNOT win: A has a more up-to-date log (has E). A won't vote for B. Only A can win (has log at least as complete as itself). A wins. E survives.

**THE INSIGHT:** The quorum overlap between "nodes that replicated E" and "nodes that can vote for the new leader" guarantees that committed entries always survive leader failure. This is the most important correctness argument in Raft — the intersection of two majorities is always non-empty in a cluster of N ≥ 2f+1 nodes.

---

### 🧠 Mental Model / Analogy

> Raft is like a committee that uses a designated chairperson to reach decisions. The chair (leader) proposes motions (log entries). A motion passes only when a majority of members acknowledge it (replicated to quorum). The chair announces passed motions to all members. If the chair is absent (leader crash), the committee elects a new chair. The new chair only has authority for new motions — but will first check with members to see if there are pending passed-but-not-announced motions from the previous chair.

**Mapping:**

- **Chairperson** → Raft leader
- **Motion proposal** → AppendEntries RPC
- **Motion passed (majority acknowledge)** → log entry committed
- **New chair election** → leader election (new term)
- **Checking for pending passed motions** → new leader learning committed entries from quorum
- **Chair tenure number** → term number

Where this analogy breaks down: in committees, all members vote on all motions. In Raft, only the leader proposes — followers only replicate and acknowledge.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Raft ensures that 3 (or 5) servers all agree on the same sequence of operations. One server is the "leader" — it accepts all requests and makes sure at least half the servers record each request before confirming it to the client. If the leader crashes, the remaining servers automatically elect a new one and continue without any data loss.

**Level 2 - How to use it (junior developer):**
Use Raft through a library: etcd for cluster coordination and key-value storage, CockroachDB or TiKV for distributed SQL/NoSQL, Consul for service discovery. Key operational parameters: heartbeat interval (default 100-500ms), election timeout (10× heartbeat), snapshot threshold (how many log entries before compaction). Monitor: leader election frequency (>1/hour is a problem), replication lag (followers' commit index vs. leader's commit index), snapshot size.

**Level 3 - How it works (mid-level engineer):**
Raft's log replication: (1) Client sends command to leader. (2) Leader appends command to its log (with current term). (3) Leader sends AppendEntries to all followers (in parallel). (4) Followers append entry to their log, reply "success." (5) Once leader receives success from a majority: marks entry as committed, applies to state machine, responds to client. (6) Leader includes commit index in next AppendEntries — followers apply committed entries. Consistency check in AppendEntries: leader sends (prevLogIndex, prevLogTerm) for the preceding entry. Follower rejects if its (prevLogIndex) entry doesn't match prevLogTerm. Leader backs up and retries with earlier entries until a match is found.

**Level 4 - Why it was designed this way (senior/staff):**
Raft's "Leader Append-Only" and "Log Matching" invariants work together: the leader never modifies its log (Append-Only) → all forks in follower logs are resolved by adopting the leader's version → Log Matching holds by induction on AppendEntries. This is in contrast to Paxos where the prepare phase allows the leader to learn about uncommitted entries from acceptors and decide their fate — introducing a third party role (acceptors) that Raft eliminates by making the leader the authoritative source. Raft's joint consensus for cluster membership changes (adding/removing servers) solves the otherwise-treacherous problem of configuration changes during normal operation by requiring a two-phase transition through an intermediate configuration.

**Expert Thinking Cues:**

- "Is my write safely committed?" → Check commit index, not just leader acknowledgment. An acknowledged-but-not-committed entry can be lost in a crash.
- "Why is my Raft throughput limited?" → Single leader = single sequencer. Use multi-Raft (shard-level leaders) for horizontal scaling.
- "Why does my follower have a shorter log than the leader?" → Normal: replication is async. Check `match_index` on leader to see replication progress.
- "What happens during a network partition?" → Majority partition: continues normally. Minority partition: stops accepting writes (no leader can be elected). After healing: minority adopts majority's log.

---

### ⚙️ How It Works (Mechanism)

**Raft log replication state machine:**

```
Leader receives client request "cmd":
  1. Append (term=T, index=N, cmd) to leader log
  2. Broadcast AppendEntries to all followers:
       prevLogIndex=N-1, prevLogTerm=T',
       entries=[(T,N,cmd)], leaderCommit=C

Follower receives AppendEntries:
  a. if msg.term < currentTerm: reject
  b. if log[prevLogIndex].term != prevLogTerm:
       reject (consistency check failure)
       [leader will decrement nextIndex and retry]
  c. Append entries to log (delete conflicting entries)
  d. if leaderCommit > commitIndex:
       commitIndex = min(leaderCommit, lastLogIndex)
  e. Reply success

Leader receives majority success:
  commitIndex = N
  Apply cmd to state machine
  Reply to client
  Next AppendEntries will carry leaderCommit=N
  (followers will apply cmd on receipt)

Log compaction (snapshot):
  When log exceeds threshold:
  Take snapshot of state machine at index S
  Discard log entries [1..S]
  InstallSnapshot RPC for lagging followers
```

**AppendEntries consistency check:**

```
Leader log:  [1,T3]─[2,T3]─[3,T5]─[4,T5]
Follower:    [1,T3]─[2,T3]─[3,T4]  (diverges at index 3)

Leader sends: prevLogIndex=2, prevLogTerm=T3
Follower: log[2].term == T3 → MATCH at index 2
Leader: sends entries [3,T5][4,T5]
Follower: deletes [3,T4], appends [3,T5][4,T5]
Logs now identical.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (write request to committed response):**

```
Client      Leader(L)    Follower(A)   Follower(B)
  │             │              │              │
  │──write X──▶│              │              │
  │            │──AppendEntry─▶│              │
  │            │──AppendEntry──────────────▶│
  │            │              │              │
  │            │◀─── ack ────│              │
  │            │◀─── ack ──────────────────│
  │            │ (majority=2 acks: commit!) │
  │            │ apply X to state machine   │
  │◀─success──│              │              │
  │            │──AppendEntry─▶│ (leaderCommit=N)
  │            │              │ apply X     │
  │            │──AppendEntry──────────────▶│
  │            │              │        apply X
  │            ← YOU ARE HERE (write is committed and applied)
```

**FAILURE PATH (leader crashes after commit, before notifying followers):**
Followers don't know X is committed. New election. New leader has X (was replicated to majority, so new leader has it by quorum overlap). New leader replicates X with its term number. X gets committed again under new term. Followers apply X. Idempotent: state machine applies X only once (by index tracking). Client may retry (received no response) — idempotent write semantics required.

**WHAT CHANGES AT SCALE:**
At 1000 keys/sec: single Raft leader handles all writes. At 100,000 keys/sec: need multi-Raft. CockroachDB splits data into 512MB ranges, each range has its own Raft group. 100 ranges × 1000 writes/range/sec = 100,000 writes/sec total. Leader count = number of ranges (hot ranges are rebalanced). Key metric: p99 Raft apply latency — should be < 10ms for most workloads.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Read scalability: followers can serve stale reads (eventual consistency). For linearizable reads: (1) ReadIndex: leader checks its commit index, ensures no newer leader by getting quorum heartbeats, returns read from state machine at that index. (2) Lease reads: leader uses a time-bounded lease (no new leader can be elected for this duration) to serve reads without quorum heartbeat. Lease reads break if leader's clock runs fast — mitigate with TrueTime (Spanner) or conservative lease margins.

---

### 💻 Code Example

**BAD - Manual leader tracking without Raft safety guarantees:**

```java
// Ad-hoc "leader" election: last writer wins
// No quorum check → split-brain if network partitions
public class UnsafeReplicatedMap {
    private final Map<String, String> store = new HashMap<>();
    private String leaderIp;

    public void write(String key, String value) {
        // Any node can accept writes
        // No consensus → diverging state
        store.put(key, value);
        broadcastToReplicas(key, value); // async, best-effort
        // Client receives "success" — but:
        // 1. Replication may fail silently
        // 2. Two nodes may both accept different values
        // 3. No way to determine which value is "correct"
    }
}
```

**GOOD - Using etcd (Raft-backed) for safe replicated state:**

```java
// etcd provides Raft consensus via its gRPC API
// All writes are linearizable by default
import io.etcd.jetcd.Client;
import io.etcd.jetcd.KV;
import io.etcd.jetcd.kv.PutResponse;
import io.etcd.jetcd.ByteSequence;

public class RaftBackedConfig {
    private final KV kvClient;

    public RaftBackedConfig(String etcdEndpoints) {
        Client client = Client.builder()
            .endpoints(etcdEndpoints.split(","))
            .build();
        this.kvClient = client.getKVClient();
        // etcd uses Raft internally — this client
        // automatically routes to leader
    }

    // Linearizable write (Raft-committed before returning)
    public void setConfig(String key, String value)
        throws Exception {
        ByteSequence k = ByteSequence.from(key.getBytes());
        ByteSequence v = ByteSequence.from(value.getBytes());
        // Only returns after Raft commits to majority
        PutResponse resp = kvClient.put(k, v).get();
        // resp.getHeader().getRevision() = Raft index
        // Use this for causal ordering of subsequent reads
        System.out.printf(
            "Committed at Raft index: %d%n",
            resp.getHeader().getRevision()
        );
    }

    // For compare-and-swap (atomic update):
    public boolean compareAndSet(
        String key, String expected, String newValue
    ) throws Exception {
        ByteSequence k = ByteSequence.from(key.getBytes());
        ByteSequence exp =
            ByteSequence.from(expected.getBytes());
        ByteSequence nv =
            ByteSequence.from(newValue.getBytes());
        // Raft-safe CAS using etcd transactions
        return kvClient.txn().If(
            new Cmp(k, Cmp.Op.EQUAL,
                CmpTarget.value(exp))
        ).Then(
            Op.put(k, nv, PutOption.DEFAULT)
        ).commit().get().isSucceeded();
    }
}
```

**How to test / verify correctness:**

```bash
# Verify Raft cluster health and leader state:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=table
# Output shows: leader, term, raft index, applied index
# applied_index should equal raft_index (no lag)

# Simulate leader failure and measure recovery:
LEADER_EP=$(ETCDCTL_API=3 etcdctl endpoint status \
  --write-out=json | jq -r \
  '.[] | select(.Status.leader != 0) | .Endpoint')
# Kill leader container, measure write recovery time:
docker kill $(docker ps | grep etcd | head -1 | awk '{print $1}')
time ETCDCTL_API=3 etcdctl put recovery-test 1 \
  --endpoints=$ETCD_ENDPOINTS 2>&1
# Expected: < 500ms (Raft election + leader commit)
```

---

### ⚖️ Comparison Table

| Property                   | Raft                    | Paxos                    | ZAB (ZooKeeper)   |
| :------------------------- | :---------------------- | :----------------------- | :---------------- |
| Understandability          | High (designed for it)  | Low                      | Medium            |
| Leader role                | Explicit, central       | Implicit (varies)        | Explicit primary  |
| Log replication            | AppendEntries RPC       | Accept phase             | Broadcast         |
| Leader election            | Term-based, quorum      | Prepare phase            | Epoch-based       |
| Cluster membership changes | Joint consensus         | Not specified            | Separate protocol |
| Production use             | etcd, CockroachDB, TiKV | Google Chubby (historic) | ZooKeeper         |
| Formal spec                | TLA+ available          | Multiple, conflicting    | Incomplete        |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                   |
| :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Raft is faster than Paxos"                    | Raft and Paxos have equivalent latency (both require 1 round-trip for normal operation after leader established). Raft's advantage is correctness and understandability, not speed.                                       |
| "Followers can serve read requests safely"     | Followers serve STALE reads. Linearizable reads require ReadIndex (leader confirmation) or lease reads. A follower 100ms behind the leader may return old data.                                                           |
| "Raft guarantees no data loss"                 | Raft guarantees committed data is not lost. Acknowledged-but-not-committed data (client received "success" but leader crashed before quorum replication) CAN be lost. Distinguish acknowledged vs. committed.             |
| "Raft requires 3 nodes minimum"                | Raft works with 1 node (trivially), 2 nodes (no fault tolerance — any failure loses quorum), or 3+ nodes. A 3-node cluster tolerates 1 failure; 5-node tolerates 2. Most production deployments use 3 or 5.               |
| "Increasing cluster size improves performance" | Larger clusters tolerate more failures but DECREASE write throughput (more nodes to replicate to) and INCREASE election time. 5 nodes is the most common production choice for 2-fault tolerance with acceptable latency. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Follower Replication Lag Causes Stale Reads**

**Symptom:** Users see stale data — a read returns a value that was already overwritten seconds ago. "I just updated this and it shows the old value."
**Root Cause:** Read routed to a Raft follower whose `applied_index` is behind the leader's `commit_index`. Follower is replicating but applying entries slowly (CPU-bound state machine, slow disk).
**Diagnostic:**

```bash
# Check replication lag across cluster nodes:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=json | jq \
  '.[].Status | {endpoint: .header.member_id,
    raftIndex: .raftIndex,
    appliedIndex: .appliedIndex}'
# If appliedIndex << raftIndex on a follower:
# That follower is lagging — route reads to leader
# Or: use ReadIndex for linearizable reads
```

**Fix:**
BAD: Routing all reads to followers without checking their applied_index.
GOOD: For linearizable reads, use etcd's `--consistency=l` flag (ReadIndex) or configure application to always read from leader. For acceptable staleness: monitor replication lag and alert if > SLA.
**Prevention:** Monitor `etcd_server_apply_duration_seconds` — if p99 > 10ms, applier is too slow.

**Failure Mode 2: Log Divergence After Incorrect Cluster Resize**

**Symptom:** After adding a new node to the cluster, the new node's log diverges from the leader. `applied_index` on the new node never catches up. Requests return errors intermittently.
**Root Cause:** New node added to cluster before leader has compacted old log entries. New node can't replay from log entry 1 (already compacted). Leader should send a snapshot via InstallSnapshot, but snapshot size exceeds RPC timeout.
**Diagnostic:**

```bash
# Check if new member is receiving snapshot:
grep "InstallSnapshot" /var/log/etcd/etcd.log | tail -20
# If InstallSnapshot repeatedly fails:
# Snapshot too large for default gRPC message size limit
# Check:
grep "grpc: received message larger than" \
  /var/log/etcd/etcd.log
```

**Fix:**
BAD: Increasing snapshot send rate without increasing gRPC message size limit.
GOOD: Increase etcd `--max-request-bytes` (default 1.5MB). Use etcd's learner mode: add new member as learner (non-voting), let it catch up via snapshot, promote to voter after caught up.
**Prevention:** Always add nodes as learners first. Monitor learner catch-up time before promotion.

**Failure Mode 3: Security - etcd Raft Cluster Without mTLS**

**Symptom:** Audit reveals that inter-node Raft traffic (port 2380) is unencrypted. A man-in-the-middle can inject AppendEntries messages with crafted log entries, corrupting the replicated state machine.
**Root Cause:** etcd deployed without `--peer-cert-file` / `--peer-key-file` / `--peer-trusted-ca-file` configuration. Peer traffic on port 2380 uses plain HTTP.
**Diagnostic:**

```bash
# Check if peer communication uses TLS:
curl -v http://etcd-node1:2380/members 2>&1 | \
  grep "Connected to"
# If it responds without TLS error: NOT secured
# Check etcd startup flags:
ps aux | grep etcd | grep peer-cert
# If no peer-cert in output: mTLS not configured
```

**Fix:**
BAD: Running etcd cluster without peer TLS: `etcd --listen-peer-urls http://0.0.0.0:2380`
GOOD: Enable peer mTLS:

```bash
etcd \
  --peer-cert-file=/etc/etcd/peer.crt \
  --peer-key-file=/etc/etcd/peer.key \
  --peer-trusted-ca-file=/etc/etcd/ca.crt \
  --peer-client-cert-auth=true \
  --listen-peer-urls=https://0.0.0.0:2380
```

**Prevention:** Kubeadm and managed Kubernetes (EKS, GKE, AKS) configure etcd mTLS by default. Self-managed etcd clusters must configure this manually. Audit with `etcdctl endpoint health` — if it requires TLS flags, the cluster is correctly secured.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - Leader Election (Raft's first subproblem — who sequences operations)
- DST-026 - Log Replication (Raft's second subproblem — how operations propagate)
- DST-028 - Quorum (the mathematical basis for Raft's safety guarantees)

**Builds On This (learn these next):**

- DST-027 - State Machine Replication (Raft as the consensus layer for SMR)
- DST-024 - Paxos (the alternative consensus algorithm; compare trade-offs)

**Alternatives / Comparisons:**

- DST-024 - Paxos (equivalent safety properties, different design philosophy)
- DST-026 - Log Replication (the mechanism Raft uses for state propagation)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Consensus algorithm: replicated|
|                  | log with leader-based ordering |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Safe distributed state machine |
|                  | with automatic failure recovery|
+------------------+--------------------------------+
| KEY INSIGHT      | Quorum overlap: committed      |
|                  | entry always on next leader    |
+------------------+--------------------------------+
| USE WHEN         | Replicated databases, config   |
|                  | stores, distributed locks      |
+------------------+--------------------------------+
| AVOID WHEN       | Leaderless Dynamo-style is ok  |
|                  | (BASE semantics acceptable)    |
+------------------+--------------------------------+
| TRADE-OFF        | Strong consistency + safety vs |
|                  | write throughput (single leader)|
+------------------+--------------------------------+
| ONE-LINER        | Leader sequences, quorum       |
|                  | commits, logs replicate safely |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-024 Paxos,                 |
|                  | DST-027 State Machine Replication|
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Raft = leader election + log replication + safety. Leader sequences all writes; a write is committed only after replication to a majority.
2. Quorum overlap guarantees committed entries survive any leader failure: majority-replicated + majority-votes = new leader always has committed entries.
3. Leader failure = write unavailability for election duration (150-500ms). Use multi-Raft for horizontal write scaling; use ReadIndex for linearizable reads from followers.

**Interview one-liner:**
"Raft is a consensus algorithm that decomposes replicated log agreement into leader election, log replication, and safety invariants. The leader appends each client request to its log, replicates it to a majority via AppendEntries, and commits (applies to state machine and responds to client) only after majority acknowledgment — guaranteeing that committed entries survive any leader failure due to the quorum intersection of replication majority and election majority."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decompose complex distributed problems into independent, separately-specifiable subproblems. Raft's success came not from a fundamentally different algorithm (Paxos achieves the same safety guarantees) but from recognizing that consensus has three distinct concerns (who leads, how state replicates, what invariants must hold) and designing each independently. When a distributed problem seems impossibly complex: look for the hidden subproblems and separate them.

**Where else this pattern appears:**

- **Two-Phase Commit (2PC) vs. Raft:** 2PC decomposes distributed transactions into "prepare" (can you commit?) and "commit" (do commit) — two independent phases with independent protocols. The coordinator failure problem in 2PC is analogous to leader failure in Raft — both require a recovery protocol for the "who decides?" subproblem. Raft solves "who decides?" elegantly; 2PC punts it to external recovery mechanisms.
- **TCP connection lifecycle:** TCP decomposes reliable byte stream delivery into: (1) connection establishment (SYN/ACK handshake), (2) data transfer (sliding window, acknowledgment, retransmission), (3) connection teardown (FIN/ACK sequence). Each phase has its own state machine. This decomposition into phases is structurally identical to Raft's subproblem decomposition — same engineering insight applied to transport-layer reliability.
- **Kubernetes controller pattern:** The Kubernetes controller decomposition separates: (1) leadership (who runs the controller — etcd Raft leader election), (2) state observation (watch API for current state), (3) reconciliation (drive current state to desired state). Three independently-specifiable subproblems. The same principle that made Raft understandable makes Kubernetes controllers testable and composable.

---

### 💡 The Surprising Truth

Raft was originally considered too simple to be publishable. Multiple reviewers at OSDI 2013 (where it was first submitted) rejected it on the grounds that it was "not novel enough" — Paxos already solved consensus. Ongaro resubmitted to USENIX ATC 2014, where it was accepted and went on to become the most-cited systems paper of the 2010s. The surprising truth: the most impactful algorithmic contribution of the decade was nearly rejected because it was "too easy to understand." Correctness and usability are treated as engineering concerns in systems research — but Raft proved they're research contributions of the highest order. The ~50 production Raft implementations deployed globally (powering Kubernetes, CockroachDB, TiKV, Consul, and dozens more) exist because one paper prioritized "can an engineer implement this correctly?" over "can we publish a novel algorithm?" The practical impact per citation ratio of Raft may be higher than any distributed systems paper in history.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** Raft requires all writes to go through a single leader. Multi-Raft (as used in CockroachDB and TiKV) partitions data into ranges, each with its own Raft group. A transaction that spans multiple ranges requires coordinating across multiple Raft leaders. What problem does cross-range coordination introduce, and how does it relate to the classic distributed transaction problem?
_Hint:_ A cross-range transaction must atomically commit to multiple Raft groups. Each group independently commits or rolls back. If one commits and another fails: partial commit. This is the distributed transaction problem. CockroachDB uses a two-phase commit (2PC) protocol coordinated by a "transaction coordinator" across Raft groups. How is this 2PC coordinator's failure handled? What happens to in-flight transactions if the coordinator crashes between prepare and commit?

**Q2 (B - Scale):** A Raft cluster has 5 nodes. The leader is handling 50,000 writes/second. You want to scale to 500,000 writes/second. What are the options, and what are their trade-offs?
_Hint:_ Option A: Add more nodes to the Raft group → increases replication fan-out, makes each write SLOWER (more ACKs needed). Option B: Use multi-Raft (shard the data, each shard has its own 3-node Raft group) → scales writes horizontally but introduces cross-shard transaction complexity. Option C: Switch to leaderless replication (Dynamo-style) → loses strong consistency. Which option preserves strong consistency while scaling writes?

**Q3 (D - Root Cause):** You're debugging a CockroachDB cluster where some transactions are taking 10-30 seconds instead of the expected <100ms. Raft replication lag is normal (< 5ms). No disk I/O issues. CPU is normal. What is the most likely cause, and what specific metric would pinpoint it?
_Hint:_ If Raft replication is fast but transaction latency is high: the bottleneck is likely not in the Raft log replication layer. CockroachDB uses distributed transactions with MVCC and a transaction coordinator. High transaction latency with normal Raft latency often indicates: (1) lock contention — a transaction is waiting for a lock held by a slow transaction, (2) intent resolution — many uncommitted intents in the MVCC layer, (3) clock skew between nodes forcing transaction restarts. What CockroachDB metric specifically tracks transaction restart count due to clock skew?

