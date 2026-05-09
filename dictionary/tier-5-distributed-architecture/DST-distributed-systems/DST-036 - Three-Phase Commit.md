---
id: DST-036
title: "Three-Phase Commit"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-035, DST-032
used_by:
related: DST-035, DST-033, DST-024
tags:
  - distributed
  - transactions
  - consistency
  - algorithm
  - deep-dive
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /distributed-systems/non-blocking-distributed-commit/
---

# DST-036 - Three-Phase Commit

⚡ TL;DR - Three-Phase Commit's non-blocking guarantee requires a synchronous network that real systems don't have; production non-blocking distributed commitment is achieved instead via Paxos/Raft-replicated coordinators (CockroachDB parallel commits, Spanner TrueTime) that eliminate coordinator SPOF without the synchrony assumption.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-035, DST-032          |     |
| **Used by:**    |                           |     |
| **Related:**    | DST-035, DST-033, DST-024 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three-Phase Commit (3PC) was proposed to solve 2PC's blocking problem. But 3PC introduced a new failure — split-brain under network partitions (see DST-035). The real problem remained: how do production systems achieve non-blocking distributed commitment while remaining safe under partitions?

**THE BREAKING POINT:**
By the late 1980s, the theoretical landscape was clear: 2PC blocks, 3PC splits under partitions, FLP says you can't have both safety and liveness in async networks with crash failures. The field was stuck: the "non-blocking commit" problem seemed theoretically unsolvable without synchrony assumptions that real networks didn't satisfy.

**THE INVENTION MOMENT:**
Paxos (Lamport, 1989/1998) and its applications to commit protocols offered the breakthrough: don't make the coordinator non-blocking — make the coordinator REPLICATED. If the coordinator role is backed by a consensus group (Paxos/Raft), coordinator failure is handled by consensus election — not by a special recovery protocol. This "Paxos-commit" approach achieves non-blocking distributed commitment without any synchrony assumption, at the cost of running a consensus protocol per transaction.

**EVOLUTION:**
1981: 3PC (Skeen) — theoretical non-blocking solution. 1985: FLP impossibility — proves limits of async protocols. 1989/1998: Paxos (Lamport) — practical consensus. 2012: Google Spanner — non-blocking geo-distributed transactions via TrueTime. 2015: CockroachDB — Raft-based 2PC without coordinator SPOF. 2017: CockroachDB parallel commits — 2PC with Raft, latency approaching single round-trip. Today: 3PC is nearly unused; Paxos-commit/Raft-commit dominates non-blocking distributed commitment.

---

### 📘 Textbook Definition

**The non-blocking distributed commitment problem** asks: can a distributed atomic commitment protocol guarantee that all participants always eventually commit or abort — even after any single coordinator failure — without requiring a synchronous network? Three-Phase Commit (3PC) answers YES, but only under the synchrony assumption. **Paxos-commit** (Lamport, 2004) answers YES unconditionally: replace the single coordinator with a Paxos group of 2f+1 replicas. The group elects a leader; the leader drives 2PC. On leader failure: Paxos re-elects a new leader from the surviving replicas. The coordinator role is now fault-tolerant — coordinator failure is O(election latency), not O(coordinator recovery). **CockroachDB parallel commits** is a practical variant: the coordinator writes its COMMITTED decision to a transaction record via Raft before sending Phase 2 to participants. Participants read the transaction record to determine the outcome — coordinator failure is handled by any participant reading the Raft-replicated record.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The real fix for 2PC blocking is not 3PC (3 phases + sync network) but a replicated coordinator (Paxos/Raft): coordinator failure triggers an election, not a blocked state.

> 3PC tried to fix the "building manager goes offline" problem by teaching tenants to vote among themselves. But tenants couldn't communicate if there was a building-wide network outage (partition). The real fix: hire three building managers (Paxos quorum). If one goes offline: the other two elect a replacement immediately. Tenants always have a responsive manager — no voting among themselves required.

**One insight:** The synchrony assumption is the crack in 3PC's foundation. Paxos/Raft don't require synchrony for safety — only for liveness (progress requires a quorum of nodes to be reachable). This distinction is why Paxos-based systems dominate non-blocking distributed commitment.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Non-blocking requires replicated decision authority:** if one node holds the commit decision and it fails, progress requires either replication (Paxos) or an alternative decision mechanism (3PC's timeout-based autonomy). Timeout-based autonomy requires synchrony; replication does not.
2. **Quorum vs unanimity:** 3PC's recovery requires ALL participants to agree (unanimity in recovery). Paxos requires MAJORITY (quorum in all decisions). Quorum survives minority failures; unanimity does not. This is Paxos's fundamental advantage over 3PC.
3. **Replicated coordinator vs replicated participants:** 2PC replicates nothing. 3PC adds recovery protocol. Paxos-commit replicates the coordinator itself. The location of replication determines fault tolerance scope.
4. **TrueTime (Spanner):** instead of replicating the coordinator per transaction, Spanner uses GPS/atomic clock synchronization (bounded clock uncertainty) to allow coordinators to commit without waiting for acknowledgment from all replicas — using time as the ordering mechanism.

**DERIVED DESIGN:**
Paxos-commit for a transaction with N participants: for each participant, run a Paxos instance to record that participant's vote. The coordinator proposal is itself Paxos-replicated — coordinator failure = new Paxos leader drives the existing proposals to conclusion.

**THE TRADE-OFFS:**
**Gain:** Non-blocking without synchrony assumption. Partition-safe. Correct in FLP-model async networks.
**Cost:** Running Paxos per transaction: 2f+1 replicas, additional round-trips vs simple 2PC. Higher latency than 2PC in the normal path. Complexity of implementing Raft correctly.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Non-blocking distributed commitment requires either synchronous network (3PC) or consensus-backed coordinator (Paxos-commit). There is no simpler correct solution.
**Accidental:** CockroachDB's parallel commits optimization reduces Paxos-commit's latency overhead by overlapping the Raft write with Phase 1, approaching single-RTT in the normal path — reducing but not eliminating the Paxos overhead.

---

### 🧪 Thought Experiment

**SETUP:** Two distributed commitment protocols in the same network. Both processing 1000 transactions/second. Network partitioned for 30 seconds.

**2PC DURING PARTITION:**
Coordinator unreachable from half the participants. Transactions in Phase 1 → blocked until partition heals or coordinator recovers. All transactions touching blocked rows are stalled. 30 seconds of blocking = 30,000 transactions in limbo. Participants eventually time out → coordinator recovery needed. SAFE (no inconsistency) but UNAVAILABLE.

**3PC DURING PARTITION:**
Participants split. Side A has PreCommit → times out → commits. Side B never got PreCommit → times out → aborts. 30 seconds of partition = thousands of split-brain commits. Both sides served their local clients with success responses. When partition heals: data inconsistency detected in reconciliation. AVAILABLE but UNSAFE.

**PAXOS-COMMIT DURING PARTITION:**
Coordinator is a Raft group (3 nodes). Partition isolates one Raft node. Remaining 2 form a quorum. New Raft leader elected within seconds. Transaction continues on the majority side. Minority side blocks (cannot form quorum) — safe. After partition heals: minority catches up from Raft log. AVAILABLE (majority) + SAFE (minority blocks rather than splits).

**THE INSIGHT:** Paxos-commit makes the correct CAP trade-off: minority partition blocks (CP behavior, same as 2PC) but the majority makes progress (better availability than 2PC's coordinator SPOF). 3PC trades safety for availability — the wrong trade-off for financial or strongly-consistent systems.

---

### 🧠 Mental Model / Analogy

> 3PC is like trying to achieve consensus in a town meeting by teaching everyone a voting procedure to use if the mayor is absent. It works if everyone can still see each other. But if a storm splits the town in two: the two groups each follow the procedure and make contradictory decisions. Paxos-commit is like electing three co-mayors: if one is absent, the remaining two continue with full authority. The town always has a functioning government — as long as a majority is reachable.

**Mapping:**

- **Single mayor** → 2PC coordinator (SPOF)
- **"Teach everyone to vote if mayor is absent"** → 3PC recovery protocol
- **Storm splitting the town** → network partition
- **Two groups making contradictory decisions** → 3PC split-brain commit
- **Three co-mayors (quorum)** → Paxos/Raft-replicated coordinator
- **Majority co-mayors governing without the absent one** → Raft leader election on coordinator failure

Where this analogy breaks down: in a real town, the two groups would eventually reconcile after the storm. In distributed databases: data once committed on both sides requires manual reconciliation — a much more serious problem.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The real fix to "distributed transactions blocking when the coordinator crashes" is to stop having a single coordinator. Modern systems like CockroachDB run 3 or 5 coordinator replicas. If one crashes: the others elect a replacement in seconds. Transactions continue. No blocking. 3PC tried a more clever approach (teach participants to decide themselves) but it breaks when the network splits.

**Level 2 - How to use it (junior developer):**
If you need non-blocking distributed transactions: use CockroachDB (cockroachdb.com — single-table and cross-table transactions are non-blocking by default via Raft). Or YugabyteDB. Or Google Cloud Spanner. These systems handle non-blocking distributed commitment internally. You write normal SQL transactions; the database handles the non-blocking guarantee. Don't implement 3PC yourself — or 2PC, for that matter.

**Level 3 - How it works (mid-level engineer):**
CockroachDB parallel commits: (1) Transaction coordinator starts a transaction, writes all intents (staging writes via Raft). (2) Coordinator writes a COMMITTED transaction record to the transaction record range (via Raft). (3) Returns success to client. (4) Async cleanup: coordinator resolves all intents from COMMITTED transaction record. If coordinator crashes between steps 2 and 3: any node that reads the transaction record sees COMMITTED — the transaction is committed regardless of who executes cleanup. If coordinator crashes between steps 1 and 2: the transaction is PENDING — any reader that discovers PENDING intents can: (a) check if coordinator is alive (push transaction) and (b) if coordinator unreachable, use Raft-replicated transaction record as source of truth.

**Level 4 - Why it was designed this way (senior/staff):**
Paxos-commit's elegance: it reuses consensus (Paxos/Raft) — which is already needed for replication — to also solve coordinator fault tolerance. The insight: "replicated state machine" (the Raft log) is a general mechanism for any fault-tolerant decision. If the commit decision is written to a Raft log: it's fault-tolerant by construction. Any node can read the Raft log and determine the commit outcome — no special recovery protocol needed. This is "convergent outcome": the commit decision converges to a single value (COMMITTED or ABORTED) once written to Raft, regardless of which coordinator node executes Phase 2. 3PC tried to achieve convergent outcome via participant protocol — Paxos achieves it via log replication. Log replication is simpler, more general, and provably correct.

**Expert Thinking Cues:**

- "CockroachDB says it uses 2PC — how is that non-blocking?" → CockroachDB's 2PC coordinator is Raft-backed. Coordinator crash = Raft election (seconds). Not a SPOF. The 2PC algorithm is unchanged; the coordinator's fault tolerance is Raft's responsibility.
- "Is Spanner 3PC or 2PC?" → Spanner uses 2PC with Paxos for each shard's coordinator. TrueTime provides the clock synchronization that allows external consistency without extra round-trips. Spanner is 2PC + Paxos, not 3PC.
- "When is 3PC ever the right choice?" → Almost never. In a controlled, synchronous network (industrial control systems with bounded latency guarantees): 3PC's non-blocking property is valid. But even there: modern consensus libraries (etcd, ZooKeeper) provide better guarantees with Raft/Zab.

---

### ⚙️ How It Works (Mechanism)

**Comparison: recovery protocols**

```
2PC Recovery (coordinator crash after Phase 1):
  Participants: STUCK — wait for coordinator
  Duration: until coordinator restarts
  Correct: YES (no inconsistency)
  Available: NO (blocks)

3PC Recovery (coordinator crash after PreCommit):
  Participants: query each other's state
  If all PREPARED: commit unilaterally
  If any INIT: abort
  Correct: YES (in synchronous network)
  Available: YES (in synchronous network)
  Under partition: split-brain possible
    → incorrect + inconsistency

Paxos-Commit Recovery (Raft leader crash):
  Raft election: new leader in ~election timeout
  New leader: reads existing Paxos proposals
  Drives in-flight decisions to conclusion
  Correct: YES (Paxos safety)
  Available: YES (for majority partition)
  Under partition: minority blocks (safe)
    → correct + majority available
```

**CockroachDB Parallel Commits flow:**

```
Client → Coordinator(C, Raft-backed)
  │
C: Begin txn, allocate TxnID
C: Write all intents to participant ranges
   (each write via Raft — durable)
C: Write COMMITTED to transaction record
   (via Raft — durable, atomic with Raft)
   ← coordinator can return SUCCESS here
   ← client receives response
C (async): resolve intents in participant ranges
   (marks intents as committed values)

If C crashes AFTER writing COMMITTED record:
  Any node reading transaction record: sees COMMITTED
  Cleanup runs async from any live node
  No information loss — Raft has the truth

If C crashes BEFORE writing COMMITTED record:
  Transaction record: PENDING or ABORTED
  Any reader finding PENDING intents: pushes txn
  Coordinator re-elected → resumes from PENDING state
  Recovery: deterministic from Raft log
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW — CockroachDB parallel commits:**

```
Client  Coordinator(Raft group)  RangeA  RangeB
  │           │                    │        │
  │─BEGIN────▶│                    │        │
  │           │─write intent A─────▶│        │
  │           │─write intent B──────────────▶│
  │           │ both via Raft: durable
  │           │─write COMMITTED TxnRecord─▶│
  │           │ (Raft-replicated decision)
  │◀─SUCCESS─│  ← YOU ARE HERE: client done
  │           │ (async cleanup begins)
  │           │─resolve intent A───▶│        │
  │           │─resolve intent B─────────────▶│
```

**FAILURE PATH (Coordinator crashes after COMMITTED record):**
Any node accessing RangeA or RangeB finds the intents. Reads transaction record: COMMITTED. Resolves intents autonomously. No coordinator needed. Non-blocking.

**WHAT CHANGES AT SCALE:**
At scale, the Raft leader for the transaction record range can become a bottleneck (hot range). CockroachDB distributes transaction records across ranges. Hot transactions concentrate traffic — load balancing, range splitting, and lease transfers become critical performance variables.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Intent-based locking (CockroachDB) vs lock-based (traditional 2PC): intents are discoverable by other transactions (via read intent resolution). Write-write conflicts: later writer pushes earlier writer. Read-write conflicts: reader can push old uncommitted write. This is multi-version concurrency control (MVCC) + lock-free in the common case — higher throughput than traditional 2PC lock holding.

---

### ⚖️ Comparison Table

| Property                   | 3PC               | Paxos-Commit      | CockroachDB Parallel | Spanner                |
| :------------------------- | :---------------- | :---------------- | :------------------- | :--------------------- |
| Blocking on coord. failure | No (sync network) | No                | No                   | No                     |
| Partition safety           | No (split-brain)  | Yes (quorum)      | Yes (Raft)           | Yes (Paxos)            |
| Synchrony assumption       | Yes               | No                | No                   | No (TrueTime)          |
| Normal-path latency        | 3 RTTs            | 2-4 RTTs          | ~1-2 RTTs            | 2 RTTs + TrueTime wait |
| Production adoption        | Near zero         | High              | High                 | High (Google)          |
| Open source                | N/A               | etcd, CockroachDB | CockroachDB          | Cloud only             |

---

### ⚠️ Common Misconceptions

| Misconception                                                                            | Reality                                                                                                                                                                                                                                                                                                                                     |
| :--------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "3PC is the correct theoretical solution — production systems just need to implement it" | 3PC is correct only under a synchrony assumption that real networks don't satisfy. Hadzilacos (1983) showed 3PC fails under partitions in asynchronous networks. It's not an implementation problem — it's a fundamental model mismatch.                                                                                                    |
| "Paxos-commit is more complex than 3PC"                                                  | 3PC's recovery protocol (participants querying each other) is complex and requires careful implementation. Paxos-commit delegates complexity to the consensus library (Raft) — which is already present in most distributed databases for replication. Reusing Raft for commit coordination adds no new complexity.                         |
| "Google Spanner uses 3PC for external consistency"                                       | Spanner uses 2PC with Paxos-backed coordinators per shard. TrueTime provides a globally consistent clock with bounded uncertainty — enabling commit timestamp selection without extra round-trips. No 3PC involved.                                                                                                                         |
| "CockroachDB's parallel commits are different from 2PC"                                  | Parallel commits are an optimization of 2PC where Phase 2 is driven by the Raft-replicated transaction record, not by coordinator explicitly notifying every participant. The protocol is still 2PC (prepare intents = Phase 1, write COMMITTED record = Phase 2 decision) — the optimization is in how Phase 2 is discovered and executed. |
| "Non-blocking distributed commitment is a solved problem"                                | It is solved for crash failures (use Raft). It remains partially constrained by CAP for partition failures: minority partitions still block (cannot form quorum). "Non-blocking" in Paxos-commit means non-blocking for the MAJORITY partition — the minority blocks until partition heals.                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Raft Leader Hotspot on Transaction Record Range**

**Symptom:** CockroachDB shows high latency on all write transactions. CRDB admin UI shows one range (the transaction record range) with disproportionately high request rate. P99 transaction latency spikes when that range's Raft leader is co-located with a slow node.
**Root Cause:** All transactions whose IDs hash to the same transaction record range converge to one Raft leader. Hot Raft leader = bottleneck for all affected transactions. This is a "hot range" problem specific to Paxos-commit architectures.
**Diagnostic:**

```bash
# CockroachDB: identify hot ranges:
cockroach debug zip --url="postgresql://user@host:26257/db" \
  --redact > debug.zip
# Or via SQL:
SELECT range_id, lease_holder, write_qps
FROM crdb_internal.ranges
ORDER BY write_qps DESC
LIMIT 10;

# Check node performance for Raft leader node:
SELECT node_id, sql_queries_total, sys_cpu_sys_percent
FROM crdb_internal.node_metrics
ORDER BY sql_queries_total DESC;
```

**Fix:**
BAD: Single-node CRDB or ranges without load balancing.
GOOD: Enable automatic range splitting (`SET CLUSTER SETTING kv.range_split.by_load_enabled = true`). Add nodes to allow Raft leader redistribution via lease transfers.
**Prevention:** Monitor hot range count as an SLO. Alert when any range sustains > 10,000 req/s for > 5 minutes.

**Failure Mode 2: Raft Election Latency Causes Transaction Timeout Storm**

**Symptom:** After a CockroachDB node failure: spike in transaction timeouts lasting 3-10 seconds. After that window: normal operation resumes. Pattern repeats on each node failure.
**Root Cause:** Raft leader election takes 1-3 election timeouts (default: 1.5-3 seconds). During election: all transactions whose record Raft group is electing are blocked. The 3-10s window = election + warmup. This is the "blocking window" in Paxos-commit — much shorter than 2PC's indefinite block, but non-zero.
**Diagnostic:**

```bash
# Check CRDB Raft election events:
SELECT timestamp, event_type, info
FROM system.eventlog
WHERE event_type IN ('raft_leader_change', 'node_decommissioned')
ORDER BY timestamp DESC
LIMIT 20;

# Measure election latency:
# raft_leader_transfers metric in CRDB time-series:
cockroach sql --execute="
  SELECT node_id, metrics->>'raft.leader.transfers' as transfers
  FROM crdb_internal.node_metrics;"
```

**Fix:**
BAD: Long Raft election timeouts (10s+) — increases blocking window.
GOOD: Tune Raft election timeout (`COCKROACH_RAFT_ELECTION_TIMEOUT_TICKS`) to reduce blocking window. Default is well-tuned for LAN; adjust for geo-distributed clusters.
**Prevention:** Ensure 3+ CRDB nodes per range (default) for fast Raft quorum. Avoid running with exactly 2 nodes (can't form quorum on one failure).

**Failure Mode 3: Security - Raft Log Tampering via Compromised Node**

**Symptom:** A compromised CRDB node writes malicious committed transactions to the Raft log. Since Raft followers replicate all writes from the leader without cryptographic verification of content: malicious data is replicated to all followers before detection.
**Root Cause:** Raft is a crash fault-tolerant protocol — it assumes nodes are honest. A Byzantine (malicious) node that becomes Raft leader can append arbitrary entries to the log. Other nodes replicate these entries faithfully. Paxos/Raft is not Byzantine fault-tolerant (BFT) — it requires 3f+1 nodes and additional cryptographic verification for Byzantine tolerance.
**Diagnostic:**

```bash
# Monitor for unusual transaction patterns:
SELECT txn_id, count(*) as writes, sum(value_size_bytes)
FROM crdb_internal.ranges
GROUP BY txn_id
HAVING sum(value_size_bytes) > 10000000  -- 10MB
ORDER BY sum(value_size_bytes) DESC;

# Audit Raft leader history for unexpected leaders:
SELECT timestamp, node_id, range_id
FROM crdb_internal.ranges
WHERE lease_holder != expected_leader_node
AND timestamp > now() - interval '1 hour';
```

**Fix:**
BAD: Permissive node trust (any node can become Raft leader without additional verification).
GOOD: (1) Mutual TLS between CRDB nodes (only authorized nodes can join the cluster). (2) Network segmentation: database nodes not accessible from the public internet. (3) Monitor for Raft leader churn (unexpected leader changes = potential compromise). (4) For Byzantine threat model: use BFT consensus (e.g., Tendermint) rather than Raft.
**Prevention:** Treat each CRDB node as a high-value security asset. Server-level security: TPM-backed node identity, immutable boot (dm-verity), runtime integrity monitoring. Node compromise detection before Raft leader election prevents log tampering.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-035 - Three-Phase Commit (3PC) (the algorithm that motivated Paxos-commit — understand its limitations first)
- DST-032 - Failure Modes (crash vs partition distinction is critical for understanding why Paxos-commit wins)

**Builds On This (learn these next):**

- Nothing directly required in DST category (this is a capstone comparison entry)

**Alternatives / Comparisons:**

- DST-035 - Three-Phase Commit (3PC algorithm and safety analysis)
- DST-033 - Two-Phase Commit (2PC) (the baseline that both 3PC and Paxos-commit improve upon)
- DST-024 - Paxos (the consensus primitive used in Paxos-commit and Raft-commit)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Why 3PC failed + what replaced |
|                  | it: Paxos-commit / Raft-commit |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Non-blocking distributed commit|
|                  | that is also partition-safe    |
+------------------+--------------------------------+
| KEY INSIGHT      | Replicate the coordinator      |
|                  | (Raft) instead of adding 3PC's |
|                  | participant recovery protocol  |
+------------------+--------------------------------+
| USE WHEN         | Choosing non-blocking dist.    |
|                  | commit: pick CockroachDB/Spanner|
+------------------+--------------------------------+
| AVOID WHEN       | 3PC itself: always avoid in    |
|                  | production asynchronous systems|
+------------------+--------------------------------+
| TRADE-OFF        | Paxos-commit: non-blocking for |
|                  | majority, blocks for minority  |
+------------------+--------------------------------+
| ONE-LINER        | Non-blocking distributed commit|
|                  | = replicated coordinator (Raft)|
|                  | not 3-phase participant voting  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-035 3PC algorithm,         |
|                  | DST-024 Paxos                  |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. 3PC's non-blocking guarantee fails under network partitions (async networks). This is why 3PC is almost never used in production.
2. The correct fix: replicate the coordinator via Raft/Paxos. Coordinator failure = Raft election (seconds), not indefinite blocking.
3. CockroachDB parallel commits and Google Spanner implement non-blocking distributed commitment via Raft-backed coordinators — not 3PC.

**Interview one-liner:**
"Three-Phase Commit's non-blocking guarantee requires a synchronous network — which real networks don't provide. Under partitions, 3PC can split-brain commit, creating data inconsistency. Production non-blocking distributed commitment uses Paxos-commit instead: the coordinator role is replicated via Raft (CockroachDB, YugabyteDB) or Paxos (Spanner). Coordinator failure triggers a Raft leader election (seconds), not indefinite blocking. This provides both non-blocking progress and partition safety — at the cost of running Paxos per transaction."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a protocol fails because a single decision-maker (coordinator) is a SPOF: the correct fix is usually to replicate that decision-maker, not to redesign the protocol to eliminate it. Adding more phases or more complex participant behavior (3PC) tries to remove the coordinator's role — but introduces new failure modes. Replicating the coordinator (Paxos-commit) preserves the simple 2-phase structure while adding fault tolerance. The engineering lesson: before redesigning a protocol to be coordinator-free, ask whether replicating the coordinator would be simpler, more correct, and reuse existing infrastructure (Raft).

**Where else this pattern appears:**

- **Database primary failover (leader election):** Instead of redesigning the database protocol to work without a primary (complex, error-prone), systems like PostgreSQL + Patroni replicate the primary role: one primary at a time, promoted from a replica pool via Raft/etcd. Primary failure → election of a new primary from replicas. The protocol (primary writes, replica replication) is unchanged; only the role is replicated. Same pattern as Paxos-commit.
- **Kubernetes controller manager:** Instead of redesigning Kubernetes to work without a controller manager (complex, coordinator-free architecture), Kubernetes runs multiple controller managers in active-passive mode using lease-based leader election (etcd). Controller manager failure → lease expiry → new manager acquires lease. The controller logic is unchanged; only the role is replicated.
- **Load balancer HA (VRRP/Keepalived):** Instead of making backend services handle load distribution without a load balancer (complex), VRRP runs two load balancers in primary/backup. Primary failure → backup assumes the VIP. The load balancing protocol is unchanged; the load balancer role is replicated. Same pattern as Paxos-commit at the infrastructure layer.

---

### 💡 The Surprising Truth

CockroachDB's "parallel commits" optimization — which reduces distributed transaction latency from 2 RTTs to approximately 1 RTT in the common case — was not invented as a fundamental protocol advance. It emerged from a practical observation: in CockroachDB's Raft-based architecture, writing the transaction record and writing the transaction intents are both Raft operations. If both can be initiated in the same Raft round: the coordinator can return success to the client as soon as the Raft write completes — even before all intents are cleaned up. This is not a new protocol; it's a batching optimization within the existing 2PC framework. The surprising truth: the most significant latency advances in distributed commitment (parallel commits, Spanner's TrueTime-based 2PC, FoundationDB's commit mechanism) have all come from HARDWARE and INFRASTRUCTURE advances (SSDs, GPS clocks, NVMe over Fabric) and BATCHING optimizations within existing protocols — not from new commit protocols like 3PC. The 45-year-old 2PC protocol, when implemented with modern replicated coordinators and hardware, outperforms the theoretically superior 3PC in every practical dimension.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** CockroachDB's parallel commits writes transaction intents and the COMMITTED transaction record in the same Raft round. A reader concurrently accessing one of the intents before the COMMITTED record is written sees a PENDING intent. The reader must decide: wait, push the transaction, or abort. Describe the complete protocol the reader follows when discovering a PENDING intent from an in-progress parallel commit. What information does the reader need? Where does it get it? What are the possible outcomes?
_Hint:_ Reader discovering PENDING intent: (1) reads the intent's transaction record. (2) If transaction record = COMMITTED: resolve the intent as committed — return the committed value to the reader. (3) If transaction record = PENDING: check if the coordinator (identified in the intent) is still alive (heartbeat check). If alive and recent heartbeat: wait for coordinator to finish. If dead or stale heartbeat: "push transaction" — abort the coordinator's transaction (write ABORTED to transaction record) and proceed. (4) If transaction record = ABORTED: resolve the intent as aborted — ignore the value, read the previous version.

**Q2 (B - Scale):** Google Spanner processes 2 billion transactions per day across 10 data centers on 3 continents. Spanner uses TrueTime: a globally synchronized clock with bounded uncertainty (epsilon: typically 1-7ms). On commit: a coordinator waits for `TrueTime.now().latest` before assigning a commit timestamp — ensuring the timestamp is definitely in the past for all nodes. This introduces 0-7ms of additional latency per transaction. Calculate: what is the total time lost globally per day to TrueTime commit-wait at 2 billion transactions/day with average epsilon of 4ms? Why does Google accept this cost?
_Hint:_ Total wait: 2×10^9 × 0.004s = 8×10^6 seconds = 92.6 days of wait time per calendar day (across all transactions in parallel). But these are PARALLEL waits, not sequential. The actual latency impact per individual transaction is 4ms. Google accepts this because: (1) TrueTime wait enables external consistency WITHOUT extra cross-datacenter round-trips (which would add 50-200ms). 4ms TrueTime wait is much cheaper than a cross-DC confirmation round-trip. (2) Spanner's workloads are reads-heavy (reads don't require TrueTime wait). (3) The 4ms is a maximum — often less. TrueTime vs. traditional distributed timestamp (Paxos clock, logical clock): which scenarios is each approach better for?

**Q3 (C - Design Trade-off):** FoundationDB uses a completely different approach to distributed transactions: a single serialization point (the "sequencer" cluster) assigns transaction IDs and commit versions. This is NOT Paxos-commit (sequencer is a cluster of nodes, not Paxos) and NOT 3PC. FoundationDB achieves ACID distributed transactions with remarkably low latency by making everything flow through the sequencer cluster. Compare: CockroachDB's distributed Paxos-commit approach vs FoundationDB's centralized sequencer approach. Which is better for: (a) geo-distributed deployments, (b) high-throughput same-DC deployments, (c) operational simplicity?
_Hint:_ FoundationDB sequencer: all transactions route through it → single-DC optimization (sequencer latency = DC-internal). Geo-distributed: all geo clients must reach the sequencer DC → 50-200ms latency regardless of transaction locality. CockroachDB: transaction record range is closest to the data → geo-distributed works well (client near data = near transaction record). Same-DC: both work well; FoundationDB's sequencer can be a bottleneck at extreme TPS (100K+ TPS). FoundationDB's operational model: sequencer cluster is the critical path — must be highly available. CockroachDB: no single critical path — Raft groups are distributed. Operational simplicity differs significantly.

