---
id: DST-024
title: Paxos
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-028
used_by: DST-023, DST-027
related: DST-023, DST-027, DST-028
tags:
  - distributed
  - consensus
  - algorithm
  - deep-dive
  - reliability
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /distributed-systems/paxos/
---

# DST-024 - Paxos

⚡ TL;DR - Paxos is the foundational distributed consensus algorithm that solves agreement on a single value (single-decree) via a two-phase Prepare/Promise/Accept/Accepted protocol, which Multi-Paxos extends to a replicated log — the basis of all modern consensus systems.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-022, DST-028          |     |
| **Used by:**    | DST-023, DST-027          |     |
| **Related:**    | DST-023, DST-027, DST-028 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
1989: Distributed systems need to solve "agreement." Multiple servers must agree on a value — a primary server, a configuration, a transaction decision — despite server crashes and network message loss. No formal algorithm exists. Every system uses ad-hoc protocols with subtle bugs: split-brain primaries, lost configuration decisions, conflicting transaction commits. The problem seems simple but resists elegant solution.

**THE BREAKING POINT:**
Lamport (1978) proved the theoretical impossibility of consensus in asynchronous networks with a single crash failure (FLP impossibility). But real systems need practical consensus. The challenge: build an algorithm that is (1) safe (never decide conflicting values) under all failures, (2) live (eventually decides) under partial synchrony, and (3) correct without requiring global coordination or atomic message delivery.

**THE INVENTION MOMENT:**
Lamport circulated "The Part-Time Parliament" in 1989 — introducing Paxos as a formal protocol for the "Part-Time Parliament of the island of Paxos" (a fictional metaphor). The paper was rejected as too whimsical and only published in 1998. Lamport rewrote it as "Paxos Made Simple" in 2001 — a 14-page informal description that became the canonical reference. The name "Paxos" (from the fictional Greek island) stuck. Google deployed Paxos in Chubby (2006), establishing it as the foundation of distributed coordination.

**EVOLUTION:**
1989/2001: Paxos (single-decree). 2006: Multi-Paxos (Chubby paper, Google). 2007: ZAB (ZooKeeper Atomic Broadcast — Paxos variant). 2012: Raft (Paxos made understandable). 2016: Flexible Paxos (varying quorum sizes per phase). 2019: Hotstuff (BFT variant, used in Libra/Diem blockchain). Today: Paxos remains the theoretical foundation; Raft is the practical implementation of choice.

---

### 📘 Textbook Definition

**Paxos** is a family of consensus algorithms for deciding on a single value among a distributed set of processes. In **single-decree Paxos**: a set of _proposers_, _acceptors_, and _learners_ cooperate to choose exactly one value from a set of proposed values. A value is **chosen** (decided) when it has been accepted by a majority (quorum) of acceptors. The protocol runs in two phases: **Phase 1 (Prepare/Promise)** — a proposer sends Prepare(n) for a proposal number n; acceptors promise not to accept lower-numbered proposals and return any value they've previously accepted. **Phase 2 (Accept/Accepted)** — the proposer sends Accept(n, v) where v is the highest-numbered value from Phase 1 responses (or the proposer's own value if none received); acceptors accept if they haven't promised a higher proposal number; a quorum of acceptors accepting constitutes a decision. **Multi-Paxos** optimizes by electing a stable leader (proposer) to skip Phase 1 for subsequent instances, enabling efficient log replication.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Paxos is a two-phase protocol: first, lock out old proposals (Prepare/Promise); second, drive a specific value to majority acceptance (Accept/Accepted).

> Paxos is like an auction with a twist. Bidder (proposer) first announces: "I'm bidding with number 42 — promise me you won't accept lower bids." Auctioneers (acceptors) promise. If any auctioneer already accepted a bid, they tell the bidder. Bidder uses the highest previously-accepted bid (or their own choice) in the real bid: "Accept bid 42 with value X." Majority acceptance = item sold (value decided). A new bidder with a higher number can interrupt and start over.

**One insight:** Paxos's safety invariant is maintained by this single rule: in Phase 2, the proposer must use the highest-numbered accepted value from Phase 1 responses (if any). This ensures that if any value was previously chosen by a quorum, the new proposer will propagate it — never deciding a conflicting value.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Majority intersection:** Any two majorities of acceptors share at least one member. This member enforces consistency between concurrent proposals.
2. **Proposal number uniqueness:** Each proposer uses a globally-unique, monotonically-increasing proposal number. Higher-numbered proposals override lower ones.
3. **Promise durability:** Once an acceptor promises not to accept proposals < n, it must honor this even after crashes (by writing the promise to durable storage).
4. **Value preservation:** If a value v has been accepted by a majority (potentially chosen), any proposer with a higher proposal number MUST propose v (not a different value). This is the key safety invariant.

**DERIVED DESIGN:**
Phase 1 solves "who has the latest state?" — proposers learn if any value was previously chosen (by seeing accepted values from acceptors). Phase 2 solves "commit that state to a majority" — once the proposer knows the authoritative value (or determines no value was previously chosen), it drives that value to majority acceptance. Two phases with majority quorums each → value preservation + eventual decision.

**THE TRADE-OFFS:**
**Gain:** Provably correct consensus under crash failures in asynchronous networks. Minimal assumptions — no global clocks, no perfect failure detectors.
**Cost:** Two round trips per value in the common case. Phase 1 required again after leader failure. Multi-Paxos needed for efficient log replication (not specified in original Paxos).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Agreement in an asynchronous network with crash failures requires at least two message delays (proved by lower bounds). Phase 1 + Phase 2 is the minimum protocol.
**Accidental:** Paxos's role separation (proposers, acceptors, learners) is flexible but creates implementation ambiguity. Raft eliminates this by merging roles and specifying a concrete node state machine.

---

### 🧪 Thought Experiment

**SETUP:** 3 acceptors (A1, A2, A3). Two proposers (P1, P2) concurrently propose different values. P1 proposes "X" with proposal number 1. P2 proposes "Y" with proposal number 2.

**PHASE 1 - PREPARE:**
P1 sends Prepare(1) → A1, A2, A3. A1, A2, A3 promise (no prior promises). P1 gets quorum. P2 sends Prepare(2) → A1, A2, A3. A1, A2, A3 promise (override promise 1 with promise 2). P1's Phase 2 may now be rejected by acceptors with higher promise.

**PHASE 2 - ACCEPT:**
P1 sends Accept(1, "X") → A1, A2. A1 rejects (promised 2 > 1). A2 rejects. P1 fails. P2 gets Promise responses (no prior accepted values). P2 sends Accept(2, "Y") → A1, A2, A3. All accept. "Y" is chosen.

**IF P1 HAD ALREADY ACCEPTED ON ONE NODE:**
Suppose Accept(1, "X") reached A1 BEFORE Prepare(2). A1 accepted "X" at proposal 1. When P2 sends Prepare(2): A1 responds "promised 2, previously accepted X at proposal 1." P2 MUST use X in Phase 2. P2 sends Accept(2, "X") — even though P2 originally wanted "Y". Value "X" is chosen. Safety preserved: P1 set "X" in motion; P2 is forced to continue it.

**THE INSIGHT:** The critical safety moment is Phase 1 response: if ANY acceptor in the Phase 1 quorum returns a previously-accepted value, the proposer is OBLIGATED to use the highest-numbered one. This obligation is the mechanism that ensures chosen values propagate — never conflicting values.

---

### 🧠 Mental Model / Analogy

> Paxos is like passing a constitutional amendment. Phase 1: the sponsor announces "I'm opening Amendment Session 42 — all senators must promise not to vote on sessions older than 42." Senators who voted in a prior session tell the sponsor what they voted for. Phase 2: the sponsor proposes the amendment — if any senator reported a prior vote, the sponsor must use the most recently voted-on text. If no prior votes: the sponsor's original text. A majority vote (acceptance) ratifies the amendment.

**Mapping:**

- **Amendment session number** → proposal number n
- **Senator's promise not to vote in older sessions** → acceptor's promise not to accept proposals < n
- **Senator reporting prior vote** → acceptor returning previously-accepted value in Phase 1
- **Sponsor must use the highest prior-voted text** → proposer must propose highest-numbered accepted value
- **Majority vote ratifies amendment** → quorum acceptance = value chosen

Where this analogy breaks down: senators can communicate with each other; in Paxos, acceptors are passive — they only respond to proposers.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Paxos is a protocol that lets distributed servers agree on a single value (like "Server B is the new primary") even if some servers crash. It works in two rounds: in the first round, a leader "locks out" older attempts. In the second round, it drives a specific value to agreement. If a majority of servers agree, the value is decided — forever.

**Level 2 - How to use it (junior developer):**
Don't implement Paxos directly — use a battle-tested library. Apache ZooKeeper uses a Paxos variant (ZAB). etcd uses Raft (a Paxos-equivalent with better specification). If you need distributed locking, leader election, or replicated configuration: use etcd or ZooKeeper. Understand Paxos conceptually to reason about the guarantees these systems provide.

**Level 3 - How it works (mid-level engineer):**
Single-decree Paxos details: Proposer chooses unique n, sends Prepare(n) to all acceptors. Acceptors respond: "I promise not to accept proposals < n. I previously accepted value v at proposal m (if any)." Proposer waits for majority. If any acceptor returned an accepted value: proposer uses the one with the highest proposal number. Sends Accept(n, v) to all acceptors. Acceptors accept if they haven't promised a higher proposal number. Majority acceptance = value chosen. Multi-Paxos: once a stable leader is established (Phase 1 run once), it can run Phase 2 repeatedly for consecutive log slots — skipping Phase 1 for each slot. This is the efficiency optimization that makes Multi-Paxos a practical log replication protocol.

**Level 4 - Why it was designed this way (senior/staff):**
The two-phase structure is a consequence of a fundamental impossibility: you can't determine if a previous proposal was "chosen" without asking a majority (since any majority could contain all the nodes that accepted it). Phase 1 solves this: by querying a majority, you're guaranteed to find out about any previously-chosen value (the quorum intersection ensures you'll hit at least one node that accepted it). Phase 2 then drives the chosen (or new) value to another majority. The invariant that proposers must use the highest-accepted-value from Phase 1 is what prevents conflicting decisions: if value v was chosen (accepted by majority M1) and a new proposer queries majority M2 (which overlaps M1), the overlap node reports v, and the new proposer is obligated to propose v — ensuring only v can ever be chosen.

**Expert Thinking Cues:**

- "Why can't Paxos decide in one round?" → FLP impossibility: one round can't distinguish between "majority accepted" and "minority accepted" without a quorum query.
- "Why does Multi-Paxos skip Phase 1?" → With a stable leader, Phase 1 is amortized over all log slots. Phase 2 alone is sufficient per slot since no competing proposers can interfere (leader has established its authority).
- "What breaks Multi-Paxos when the leader fails?" → Phase 1 must be re-run (the new leader needs to discover any in-flight proposals from the old leader). This is the election + catchup phase in every Paxos-based system.
- "Is Raft just Multi-Paxos?" → Essentially yes. Raft makes explicit what Multi-Paxos leaves implicit: log entries, term numbers, the leader's authority per term. The safety properties are equivalent.

---

### ⚙️ How It Works (Mechanism)

**Single-decree Paxos — full message flow:**

```
PHASE 1: PREPARE / PROMISE
Proposer (P):
  n = unique proposal number (higher than any seen)
  send Prepare(n) → all acceptors

Acceptor (A) on receiving Prepare(n):
  if n > promisedN:
    promisedN = n  // persist to durable storage
    send Promise(n, acceptedN, acceptedV) to P
    // acceptedN=0, acceptedV=null if never accepted
  else:
    send Nack(promisedN) to P  // reject stale proposal

PHASE 2: ACCEPT / ACCEPTED
Proposer (P) after receiving majority Promises:
  if any Promise returned acceptedV:
    v = acceptedV with highest acceptedN
  else:
    v = proposer's own proposed value
  send Accept(n, v) → all acceptors

Acceptor (A) on receiving Accept(n, v):
  if n >= promisedN:
    acceptedN = n
    acceptedV = v  // persist to durable storage
    send Accepted(n, v) → learners (and proposer)
  else:
    send Nack(promisedN) to P

Value CHOSEN when: majority of acceptors
  sent Accepted(n, v) for the same n
```

**Multi-Paxos optimization (Phase 1 amortized):**

```
Leader established (Phase 1 done for term T):
  For each log slot i:
    Leader sends: Accept(T, i, cmd)  // skip Prepare
    Majority accept: slot i committed
    Leader sends: Commit(i) to all followers
    // or piggybacks leaderCommit in next Accept

Phase 1 re-run only when:
  - Leader crashes (new leader must discover in-flight)
  - Network partition causes leader change
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Multi-Paxos with stable leader, log slot i):**

```
Proposer(L)   Acceptor(A1)  Acceptor(A2)  Acceptor(A3)
    │               │              │              │
    │──Accept(T,i,X)──────────────▶│              │
    │──Accept(T,i,X)───────────────────────────▶│
    │──Accept(T,i,X)─────▶│              │        │
    │               │              │              │
    │◀──Accepted(T,i,X)───│              │        │
    │◀──Accepted(T,i,X)────────────│              │
    │ (majority=2 Accepted: slot i committed)    │
    │ apply X to state machine                   │
    │──Commit(i)──────────────────▶│             │
    │──Commit(i)───────────────────────────────▶│
    │──Commit(i)──────────▶│                     │
    │               ← YOU ARE HERE                │
    │ (value X decided in slot i, all learn it)  │
```

**FAILURE PATH (leader crashes during Phase 2):**
Leader sends Accept(T, i, X) to A1 only. Crashes. A1 accepted X. A2, A3: X not accepted. New leader (term T+1): runs Phase 1 (Prepare(T+1)). A1 responds with acceptedN=T, acceptedV=X. New leader MUST propose X for slot i (highest-accepted). New leader sends Accept(T+1, i, X) to majority. X is committed. Correctness: if X had been chosen (majority accepted), the new leader would have found it via Phase 1 quorum overlap. If X was not chosen (only A1): new leader propagates X anyway — ensuring the one node that accepted it is consistent with the final decision.

**WHAT CHANGES AT SCALE:**
At high throughput: Phase 1 round-trip is the bottleneck during leader changes. Multi-Paxos amortizes Phase 1 over the entire term. With Flexible Paxos: use quorum size 1 for Phase 1 and quorum size n-f for Phase 2 (Phase 1 is fast but Phase 2 is durable). Trade-off: faster reconfiguration at the cost of higher Phase 2 quorum. Key metric: proposal number collision rate — high collision means many competing proposers, which is a liveness threat.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multiple proposers cause "Paxos dueling" (livelock): P1 gets Phase 1 majority, P2 gets higher proposal number and phases out P1's Phase 2, P1 increments proposal number and phases out P2's Phase 2 — indefinitely. Solution: elect a single distinguished proposer (leader). This is exactly what Multi-Paxos and Raft do — turning a theoretically livelock-prone algorithm into a practical, stable protocol.

---

### 💻 Code Example

**BAD - Single-round "consensus" that can't handle concurrent proposers:**

```java
// Attempting consensus with a single round-trip:
// If two proposers send simultaneously → both may
// get different values accepted → split decision
public class UnsafeConsensus {
    private String decidedValue = null;

    // Single round: no proposal number,
    // no Phase 1 → unsafe with concurrent proposers
    public synchronized boolean propose(String value) {
        if (decidedValue == null) {
            decidedValue = value; // Only works for 1 proposer
            return true;
        }
        return false; // Too late — but: what if 2 nodes
        // call propose() simultaneously on different replicas?
        // Both see null, both set value → conflicting decisions
    }
}
```

**GOOD - Single-decree Paxos acceptor state machine:**

```java
import java.util.concurrent.atomic.AtomicInteger;

// Persistent acceptor state: must survive crashes
// In production: write to disk before responding
public class PaxosAcceptor {
    // Persisted to durable storage before every update
    private volatile int promisedN = 0;
    private volatile int acceptedN = 0;
    private volatile String acceptedValue = null;

    // Phase 1: Respond to Prepare(n)
    public synchronized PrepareResponse prepare(int n) {
        if (n > promisedN) {
            int prevPromisedN = promisedN;
            promisedN = n;
            persist(); // Must persist BEFORE responding
            return PrepareResponse.promise(
                n, acceptedN, acceptedValue
            );
        }
        // Reject: already promised higher n
        return PrepareResponse.nack(promisedN);
    }

    // Phase 2: Respond to Accept(n, value)
    public synchronized AcceptResponse accept(
        int n, String value
    ) {
        if (n >= promisedN) {
            acceptedN = n;
            acceptedValue = value;
            persist(); // Must persist BEFORE responding
            return AcceptResponse.accepted(n, value);
        }
        // Reject: promised to a higher proposal
        return AcceptResponse.nack(promisedN);
    }

    private void persist() {
        // Write promisedN, acceptedN, acceptedValue
        // to durable storage (disk/WAL) BEFORE returning
        // If this crashes: on recovery, state is correct
        // Omitting this → safety violation on crash+restart
        storage.write(promisedN, acceptedN, acceptedValue);
    }
}
```

**Paxos proposer (phase 1 + phase 2):**

```java
public class PaxosProposer {
    private final List<PaxosAcceptor> acceptors;
    private final int quorum; // majority = (n/2)+1
    private int proposalNumber = 0;

    public Optional<String> runPaxos(String myValue)
        throws InterruptedException {
        while (true) {
            proposalNumber = generateUniqueHigherN();

            // Phase 1: Prepare
            List<PrepareResponse> promises =
                broadcastPrepare(proposalNumber);
            if (promises.size() < quorum) {
                continue; // Retry with higher n
            }

            // Choose value: use highest-acceptedN value
            // from promises, or own value if none
            String valueToPropose = promises.stream()
                .filter(p -> p.getAcceptedN() > 0)
                .max(Comparator.comparingInt(
                    PrepareResponse::getAcceptedN))
                .map(PrepareResponse::getAcceptedValue)
                .orElse(myValue);
            // KEY SAFETY INVARIANT: must use highest
            // previously-accepted value if any returned

            // Phase 2: Accept
            List<AcceptResponse> accepted =
                broadcastAccept(proposalNumber,
                    valueToPropose);
            if (accepted.size() >= quorum) {
                notifyLearners(valueToPropose);
                return Optional.of(valueToPropose);
            }
            // Split — retry with higher proposal number
        }
    }
}
```

**How to test / verify correctness:**

```bash
# Test with Jepsen (distributed systems correctness testing):
# Jepsen has Paxos/etcd/ZooKeeper test suites
# that inject network partitions and verify linearizability:
# https://github.com/jepsen-io/jepsen

# For ZooKeeper (ZAB = Paxos variant):
# Run Jepsen ZooKeeper test:
lein run test --test zookeeper \
  --nemesis partition-random-halves \
  --time-limit 120
# Verify: 0 linearizability violations in results
```

---

### ⚖️ Comparison Table

| Property                   | Single-decree Paxos     | Multi-Paxos             | Raft                     |
| :------------------------- | :---------------------- | :---------------------- | :----------------------- |
| What it decides            | One value               | A log (sequence)        | A log (sequence)         |
| Phase 1 frequency          | Every proposal          | Once per leader term    | Once per election        |
| Leader role                | Optional (any proposer) | Stable leader preferred | Mandatory                |
| Specification completeness | Partial (theory)        | Partial (many variants) | Complete (paper)         |
| Livelock risk              | Yes (dueling)           | Low (stable leader)     | Low (randomized timeout) |
| Production use             | Foundation only         | Chubby, Spanner         | etcd, CockroachDB, TiKV  |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                              |
| :-------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Paxos can decide any value a proposer wants" | If a value was previously accepted by any acceptor in the Phase 1 quorum: the proposer MUST use the highest-numbered one. Proposers lose control of the value whenever a prior proposal partially succeeded.                         |
| "Paxos guarantees liveness"                   | Paxos guarantees SAFETY (never two conflicting values chosen) always. Liveness (eventually decides) only under partial synchrony and with at most one active proposer. With two competing proposers: livelock (dueling) is possible. |
| "Multi-Paxos is fully specified"              | Multi-Paxos is not fully specified by Lamport. Different implementations make different choices for log slot assignment, leader election, and catchup after leader failure. This ambiguity is why Raft was created.                  |
| "Acceptors must communicate with each other"  | In standard Paxos: acceptors are passive — they only respond to proposers. No acceptor-to-acceptor communication is required. This is both a strength (simple acceptors) and a weakness (proposers are a bottleneck).                |
| "Paxos requires 3 nodes minimum"              | Single-decree Paxos requires 2f+1 nodes to tolerate f failures. With 1 node: trivially works. With 2 nodes: one failure loses quorum (can't decide). Minimum for 1 fault tolerance: 3 nodes.                                         |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Paxos Dueling (Livelock)**

**Symptom:** No progress in the consensus layer. Proposal numbers keep incrementing (P1 uses n=1, P2 uses n=2, P1 uses n=3, P2 uses n=4...). System makes no decisions for seconds or minutes. "Progress stuck" alert fires.
**Root Cause:** Two competing proposers keep preempting each other's Phase 1 with higher proposal numbers. Each proposer invalidates the other's Phase 2 before it completes. Theoretically, this can run forever (livelock).
**Diagnostic:**

```bash
# Check ZooKeeper for proposal number escalation:
grep "LOOKING\|FOLLOWING\|LEADING" /var/log/zookeeper/zookeeper.log \
  | tail -50
# Rapid LOOKING/LEADING transitions = election dueling
# Check etcd for term escalation (Raft equivalent):
ETCDCTL_API=3 etcdctl endpoint status \
  --write-out=json | jq '.[].Status.raftTerm'
# Rapidly incrementing term = election livelock
```

**Fix:**
BAD: Multiple active proposers without a leader election mechanism.
GOOD: Elect a single stable proposer (leader). Use randomized backoff before retrying a failed proposal. Use Multi-Paxos where Phase 1 is run once per leader tenure.
**Prevention:** Never allow concurrent proposers in production without leader election. All practical Paxos deployments use a distinguished leader.

**Failure Mode 2: Acceptor Loses Persisted State (Safety Violation)**

**Symptom:** After a crash + restart, an acceptor's state is reset (promisedN = 0, acceptedValue = null). The acceptor then accepts a lower-numbered proposal that it had previously promised not to accept. Two different values are chosen for the same consensus slot.
**Root Cause:** Acceptor state not persisted to durable storage before responding. In-memory state only. Crash wipes state. Restarted acceptor violates its own promise.
**Diagnostic:**

```bash
# If running a custom Paxos implementation:
# Check if acceptor writes to disk before responding:
grep -r "persist\|fsync\|write.*promise\|write.*accept" \
  src/paxos/ -l
# If zero matches: state is not persisted → unsafe
# Check disk write pattern during Paxos operations:
strace -e trace=write,fsync -p $(pidof paxos_acceptor) 2>&1 \
  | grep -c fsync
```

**Fix:**
BAD: Responding to Prepare/Accept before persisting state changes.
GOOD: Write promisedN (and acceptedN/acceptedValue) to durable storage (WAL, disk) with fsync BEFORE sending the response. On crash+restart: recover state from disk before rejoining.
**Prevention:** Paxos acceptor state persistence is non-negotiable for correctness. This is why production systems (etcd, ZooKeeper) use WAL (Write-Ahead Log) for all Raft/ZAB state.

**Failure Mode 3: Security - Proposal Number Injection**

**Symptom:** A compromised node sends Prepare messages with very high proposal numbers (n = MAX_INT), forcing all acceptors to promise not to accept the legitimate proposer's proposals. The legitimate proposer can't make progress — effective denial of service on the consensus layer.
**Root Cause:** Proposal numbers accepted without authentication. Any node can claim any proposal number. A malicious node can monopolize proposal number space.
**Diagnostic:**

```bash
# Check if Paxos messages are authenticated:
# For etcd (Raft): check peer TLS:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint health --cacert ca.pem
# For custom Paxos: check if proposer IDs are signed:
grep -r "signature\|hmac\|auth\|verify" \
  src/paxos/proposer/ -l
```

**Fix:**
BAD: Accepting Prepare messages from any node with any proposal number.
GOOD: Authenticate all inter-node messages with mTLS or HMAC. Validate proposer identity against an allowlist. Rate-limit Prepare messages per proposer to prevent proposal number exhaustion.
**Prevention:** Use mTLS for all Raft/Paxos inter-node communication. etcd: `--peer-client-cert-auth=true`. Never expose Raft/Paxos ports to untrusted networks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - Leader Election (Multi-Paxos requires a stable leader for Phase 1 amortization)
- DST-028 - Quorum (Paxos safety depends on majority quorum intersection)

**Builds On This (learn these next):**

- DST-023 - Raft (practical, understandable reimplementation of Multi-Paxos concepts)
- DST-027 - State Machine Replication (Paxos/Multi-Paxos as the consensus layer for SMR)

**Alternatives / Comparisons:**

- DST-023 - Raft (equivalent safety properties, better specified and more widely deployed)
- DST-028 - Quorum (the mathematical foundation shared by all consensus algorithms)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Two-phase consensus: Prepare/  |
|                  | Promise then Accept/Accepted   |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Distributed agreement on one   |
|                  | value despite crashes          |
+------------------+--------------------------------+
| KEY INSIGHT      | Proposer must use highest      |
|                  | prior-accepted value (safety!) |
+------------------+--------------------------------+
| USE WHEN         | Reasoning about consensus      |
|                  | foundations; Google Chubby     |
+------------------+--------------------------------+
| AVOID WHEN       | Implementing from scratch: use |
|                  | Raft library instead           |
+------------------+--------------------------------+
| TRADE-OFF        | Provably correct vs. complex   |
|                  | to implement correctly         |
+------------------+--------------------------------+
| ONE-LINER        | Phase1: lock, learn prior vote |
|                  | Phase2: drive majority accept  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-023 Raft,                  |
|                  | DST-027 State Machine Replication|
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Paxos has two phases: Prepare/Promise (lock out old proposals, discover prior accepted values) and Accept/Accepted (drive a specific value to majority acceptance). A value is chosen when a majority of acceptors accept it.
2. The key safety invariant: if any Phase 1 response contains a previously-accepted value, the proposer MUST use the one with the highest proposal number. This prevents conflicting decisions.
3. Single-decree Paxos decides ONE value. Multi-Paxos extends it to a log by electing a stable leader and skipping Phase 1 for each log slot. Raft is Multi-Paxos made explicit and implementable.

**Interview one-liner:**
"Paxos is a two-phase consensus algorithm: Phase 1 (Prepare/Promise) has a proposer lock out lower-numbered proposals and learn any previously-accepted values; Phase 2 (Accept/Accepted) drives the highest-previously-accepted value (or the proposer's own) to majority acceptance. Safety is guaranteed by the invariant that proposers must use the highest-numbered prior-accepted value — ensuring that if any value was chosen, subsequent proposers will propagate it, never decide a conflicting value."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you need consensus in a distributed system, Phase 1 (asking "what has been decided before?") and Phase 2 (driving "commit this decision to a majority") is the minimum structure. This two-phase pattern appears wherever distributed systems need to make a binding decision: 2PC (prepare + commit), distributed locks (lock request + lock grant), distributed snapshots (barrier + collect). Each is a specific application of the Prepare/Accept pattern. The underlying reason: in an asynchronous network, you can't decide without first learning the current state from a majority (Phase 1) and then writing new state to a majority (Phase 2).

**Where else this pattern appears:**

- **Two-Phase Commit (2PC) in distributed transactions:** 2PC's prepare phase (coordinator asks all participants "can you commit?") maps directly to Paxos's Phase 1 (proposer asks acceptors "promise me you'll honor proposal n"). 2PC's commit phase maps to Paxos's Phase 2. The coordinator failure problem in 2PC (blocking if coordinator crashes between prepare and commit) is absent in Paxos because Paxos allows any node to re-run Phase 1 and take over — 2PC has no such recovery mechanism, which is why it's "blocking" and Paxos is not.
- **Distributed snapshot algorithms (Chandy-Lamport):** The Chandy-Lamport snapshot algorithm uses a two-phase approach: Phase 1 — initiate snapshot (equivalent to Prepare: announce snapshot is starting), Phase 2 — collect channel states (equivalent to Accept: gather state from all processes). The "happened-before" ordering invariant in Chandy-Lamport serves the same role as Paxos's proposal number ordering: ensuring no state is captured from the wrong phase of the execution.
- **Google Spanner's TrueTime Commit Wait:** Spanner uses Paxos (Multi-Paxos) for log replication within each tablet group. But for external consistency (linearizability across tablet groups), it adds TrueTime commit wait — a third "phase" that waits until the commit timestamp is in the past before acknowledging. This extends the two-phase Paxos structure with a time-based waiting phase to achieve global linearizability. The same "lock-then-commit" structure, extended with a real-time safety margin.

---

### 💡 The Surprising Truth

Lamport's original Paxos paper ("The Part-Time Parliament") was submitted to ACM TOCS in 1989 and was rejected. The reviewers found the "Paxos parliament" metaphor too whimsical and the algorithm too simple to be an interesting contribution. The paper sat in Lamport's drawer until 1998, when it was published 9 years late because Lamport happened to mention it in conversation and was surprised that colleagues hadn't read it. He then wrote "Paxos Made Simple" (2001) — an informal 14-page description — after realizing the original paper was incomprehensible to most readers. The remarkable consequence: the most foundational algorithm in distributed systems was suppressed for nearly a decade by peer reviewers who thought it was too trivial. Meanwhile, every production distributed system continued to struggle with ad-hoc, incorrect consensus implementations that Paxos would have solved — because the algorithm was sitting in a desk drawer. Google independently discovered Multi-Paxos in the early 2000s and deployed it in Chubby (2006), only later learning it was essentially rediscovering what Lamport had already proved correct in 1989.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** Paxos requires acceptors to persist their promise (promisedN) to durable storage before responding to Prepare messages. If an acceptor crashes AFTER sending the promise response but BEFORE the promise is persisted to disk (a crash in the network stack after write, before fsync): the acceptor restarts with no record of its promise. Is this a safety violation? Under what conditions?
_Hint:_ If the acceptor responds "promised n" to a proposer, but then crashes and restarts with promisedN=0, it could accept a proposal with a lower number that it already promised to reject. Whether this is a safety violation depends on whether the proposer used that promise to make a Phase 2 decision. What is the window between "promise sent" and "promise durable" and how does it interact with the proposer's Phase 2 decision?

**Q2 (C - Design Trade-off):** Multi-Paxos skips Phase 1 for log slots after a stable leader is established. But "stable leader" is not formally defined — it's an optimization that works in practice but not always. What happens if the network partitions the leader from a minority of acceptors for 30 seconds, then reconnects? The leader never knew it was partitioned. Which log slots might have incorrect decisions? How does the leader's catchup phase discover and repair them?
_Hint:_ During the partition: the leader could not replicate to the minority acceptors. The minority acceptors may have participated in a new leader's Phase 1 for some log slots (if the minority elected a new leader — but they can't, they're a minority). So no new decisions were made on those slots by the minority. The old leader's Phase 2 decisions (to the majority) are valid. When reconnecting: the minority acceptors receive the committed log from the majority, adopt it. What if the network partition allowed one minority acceptor to have accepted a value from an OLD Phase 2 — before the partition — that was committed?

**Q3 (B - Scale):** Paxos's quorum size is n/2+1. For a cluster of 100 nodes, each write requires 51 ACKs — 51 network round-trips from the proposer's perspective. Flexible Paxos allows different quorum sizes per phase: Phase 1 quorum = 1, Phase 2 quorum = n. What is the safety guarantee of this configuration, and when would you actually use it?
_Hint:_ Flexible Paxos's safety invariant: Q1 + Q2 > n (where Q1 = Phase 1 quorum, Q2 = Phase 2 quorum). With Q1=1 and Q2=100 (n=100): 1+100=101 > 100. Valid! Phase 1 needs only 1 node's response (very fast leader election). Phase 2 needs ALL 100 nodes (extremely durable). When would Q1=1, Q2=n be useful? What happens if any node in Q2 is unavailable during Phase 2?
