---
id: DST-035
title: "Three-Phase Commit (3PC)"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-033, DST-032
used_by:
related: DST-033, DST-034, DST-024
tags:
  - distributed
  - transactions
  - consistency
  - algorithm
  - deep-dive
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /distributed-systems/three-phase-commit/
---

# DST-035 - Three-Phase Commit (3PC)

⚡ TL;DR - Three-Phase Commit adds a PreCommit phase between 2PC's Prepare and Commit to eliminate blocking on coordinator failure — but the non-blocking guarantee requires a synchronous network assumption that real asynchronous networks violate, making 3PC unsafe under network partitions and almost unused in production.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-033, DST-032          |     |
| **Used by:**    |                           |     |
| **Related:**    | DST-033, DST-034, DST-024 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two-Phase Commit (2PC) has a fatal blocking problem: if the coordinator crashes between Phase 1 (Prepare) and Phase 2 (Commit/Abort), all participants are stuck indefinitely. They voted YES and locked their resources — but cannot determine the correct outcome without the coordinator. This indefinite blocking is the defining weakness of 2PC in high-availability systems.

**THE BREAKING POINT:**
By the early 1980s, 2PC was well-understood but its blocking problem was recognized as fundamental to its design. Any high-availability distributed system that relied on 2PC would stall whenever the coordinator failed — unacceptable for systems requiring continuous availability. The question: can we modify 2PC to eliminate blocking while preserving atomicity?

**THE INVENTION MOMENT:**
Dale Skeen's 1981 dissertation "Nonblocking Commit Protocols" introduced 3PC as the first practical non-blocking distributed commitment protocol. The key insight: if participants know "every other participant also voted YES and received the PreCommit," they can safely commit unilaterally if the coordinator disappears after PreCommit. The PreCommit phase propagates the "unanimous YES" knowledge to all participants — enabling autonomous decision without the coordinator.

**EVOLUTION:**
1981: Skeen's 3PC. 1983: theoretical analysis showing 3PC safe only in synchronous networks (Hadzilacos). 1985: FLP impossibility — reinforces that all commit protocols face fundamental limits in async networks. 1990s: 3PC largely abandoned in practice; XA/2PC dominates. 2000s: Paxos-based commit (Lamport) emerges as practical non-blocking alternative. 2015+: CockroachDB/Spanner use Raft-commit (Paxos-based) rather than 3PC. 3PC remains a theoretical milestone — almost never deployed.

---

### 📘 Textbook Definition

**Three-Phase Commit (3PC)** is a distributed atomic commitment protocol that extends 2PC with an additional phase to eliminate the blocking state on coordinator failure. The three phases: **Phase 1 (CanCommit/Prepare):** coordinator asks each participant "can you commit?". Unanimous YES required to proceed. **Phase 2 (PreCommit):** coordinator broadcasts PreCommit to all participants. Each participant acknowledges. After receiving PreCommit, a participant enters a state where it is SAFE to commit unilaterally if the coordinator fails. **Phase 3 (DoCommit):** coordinator broadcasts the final Commit (or Abort). Participants apply the decision. **Non-blocking property:** after a participant receives PreCommit: it knows all other participants also received PreCommit (the coordinator verified unanimous YES before sending PreCommit). If the coordinator crashes after PreCommit: every participant knows that all participants are in the "can-commit" state. A timeout recovery protocol can then allow participants to commit unilaterally without violating atomicity. **The critical limitation:** the non-blocking guarantee assumes a SYNCHRONOUS network (bounded message delays). In asynchronous networks (where messages can be arbitrarily delayed or lost): a network partition can split participants — some receive PreCommit, some don't — creating a scenario where one side commits and the other aborts, violating atomicity.

---

### ⏱️ Understand It in 30 Seconds

**One line:** 3PC adds a middle phase ("PreCommit: everyone knows everyone voted YES") so participants can commit unilaterally if the coordinator fails — but this only works if the network delivers messages before timeouts expire.

> 3PC is like an emergency committee vote with a two-step confirmation. The chair asks "can you all vote YES?" (Phase 1). If yes, the chair announces "everyone voted YES — be ready to finalize" (Phase 2, PreCommit). Now every member knows everyone is aligned. If the chair collapses after Phase 2: members can independently finalize the decision because they all know everyone was aligned. But: if a fire alarm rings between Phase 1 and Phase 2 (splitting the room): some members heard Phase 2 and will finalize; others didn't — chaos.

**One insight:** 3PC replaces the blocking problem with the partition problem. In synchronous networks: no blocking. In asynchronous networks (all real networks): partitions can cause one side to commit while the other aborts — a worse outcome than blocking. This is why 3PC was abandoned.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Unanimous YES before PreCommit:** coordinator sends PreCommit ONLY after receiving YES from all participants. PreCommit is a guarantee: "I (coordinator) have verified unanimous consent."
2. **PreCommit propagates knowledge:** when a participant receives PreCommit: it knows all other participants voted YES (the coordinator verified this). This shared knowledge enables autonomous decision.
3. **Timeout-based recovery:** if a participant times out waiting for Phase 3 (after receiving PreCommit): it contacts other participants. If all others also have PreCommit: safely commit. If any lacks PreCommit: abort.
4. **Synchrony assumption:** recovery timeouts are meaningful ONLY if the network is synchronous — messages arrive within bounded time. In async networks: "timeout" could mean "delayed message" not "coordinator failure."

**DERIVED DESIGN:**
The blocking problem in 2PC: after voting YES, a participant cannot distinguish "coordinator crashed" from "coordinator is slow." Adding PreCommit: a participant that received PreCommit knows the coordinator has full YES votes. If coordinator doesn't send Phase 3 within timeout: participant can safely commit (because all others who received PreCommit will also commit via the same timeout logic).

**THE TRADE-OFFS:**
**Gain:** Non-blocking on coordinator failure (in synchronous networks). Participants can always make progress after coordinator failure.
**Cost:** Third network round-trip (higher latency than 2PC). Complex recovery protocol. Unsafe under network partitions. No major RDBMS implements 3PC. Real networks are asynchronous — the safety guarantee is theoretical.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Eliminating blocking requires participants to share enough knowledge to make autonomous decisions — the PreCommit phase is the minimal way to achieve this.
**Accidental:** The synchrony assumption is not an accident of 3PC's design — it is essential to its correctness. Any non-blocking commit protocol must make some synchrony assumption or use consensus (Paxos/Raft), which 3PC does not. The accidental complexity: implementing 3PC without recognizing the synchrony assumption leads to subtle safety violations under partitions.

---

### 🧪 Thought Experiment

**SETUP:** 3 databases (DB1, DB2, DB3). Coordinator C. All in the same data center. No network issues.

**COORDINATOR CRASH BETWEEN PHASE 2 AND PHASE 3 (3PC shines):**

- C sends PreCommit to DB1, DB2, DB3 (all ACK)
- C crashes before sending DoCommit
- DB1 times out → contacts DB2: "did you get PreCommit?" → "yes"
- DB1 contacts DB3: "did you get PreCommit?" → "yes"
- All got PreCommit → unanimous YES + all in PreCommit state
- DB1, DB2, DB3: each independently commits
- No coordinator needed. Non-blocking.

**NETWORK PARTITION BETWEEN PHASE 1 AND PHASE 2 (3PC fails):**

- C: all YES votes received → sends PreCommit
- Partition: DB1 gets PreCommit; DB2, DB3 do not (network split)
- DB1 side: "I got PreCommit" → timeout → contacts DB2: "did you get PreCommit?" → cannot reach (partition)
- DB1 interprets timeout as "coordinator failed after PreCommit" → commits unilaterally
- DB2, DB3 side: "never got PreCommit" → timeout → can only see each other → no PreCommit → abort
- DB1: COMMITTED. DB2+DB3: ABORTED. Data inconsistency.

**THE INSIGHT:** 3PC's non-blocking guarantee is only valid when "timeout" reliably distinguishes "coordinator failed" from "message delayed by partition." In a synchronous network: this distinction is valid (if message doesn't arrive within bounded time: coordinator must be down). In real asynchronous networks: timeout could mean either — 3PC cannot distinguish them, causing split-brain commits.

---

### 🧠 Mental Model / Analogy

> 3PC is like a group text message vote. The organizer asks "can everyone make Saturday?" (Phase 1). If all say "yes," the organizer sends a follow-up "Confirmed: everyone is free Saturday" (Phase 2, PreCommit — everyone now knows everyone agreed). If the organizer's phone dies before sending the final "OK, event is on Saturday" (Phase 3): each person knows everyone agreed — they can each put Saturday in their calendar independently. BUT: if a phone carrier outage prevents some people from receiving the "Confirmed" message (Phase 2): some people know everyone agreed (they'll commit to Saturday) while others don't (they'll cancel). The calendar is inconsistent.

**Mapping:**

- **Group text organizer** → coordinator
- **"Can everyone make it?"** → Phase 1 (CanCommit)
- **"Confirmed: everyone free"** → Phase 2 (PreCommit — shared knowledge)
- **"OK, event is on"** → Phase 3 (DoCommit)
- **Organizer phone dies after Phase 2** → coordinator crash (3PC handles correctly)
- **Carrier outage during Phase 2** → network partition (3PC fails)

Where this analogy breaks down: people can call each other using different channels if the group text fails. In 3PC: participants can query each other via the recovery protocol, but in a partition, some participants are unreachable — same split-brain problem.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
3PC is a fix for 2PC's "stuck waiting" problem. It adds a middle step where everyone is told "we all agreed, get ready." Now if the coordinator disappears after that middle step: everyone can independently proceed — they already know everyone agreed. The catch: it only works if the network is reliable enough that "no response within N seconds" definitely means the coordinator is down, not just delayed.

**Level 2 - How to use it (junior developer):**
3PC is rarely implemented in any database or framework you'll encounter. If you need distributed transactions without blocking: use CockroachDB (Raft-based 2PC, no SPOF coordinator), Saga pattern (eventual consistency), or design for single-DB transactions. 3PC is primarily academic — know the concept for interviews and distributed systems reading, not for implementation.

**Level 3 - How it works (mid-level engineer):**
3PC protocol: Phase 1 (CanCommit): coordinator sends "can you commit?" to all. Each responds YES or NO. Phase 2 (PreCommit): if all YES, coordinator sends PreCommit. Participants acknowledge. State: PREPARED. Phase 3 (DoCommit): coordinator sends Commit. Participants commit, release locks. Recovery timeout: participant in PREPARED state contacts others. If all PREPARED: commit. If any INIT (never got PreCommit): abort. The state machine ensures: if ANY participant is in INIT state during recovery: no participant has committed. If ALL are in PREPARED: all will commit. No mixed state is possible IF recovery runs correctly.

**Level 4 - Why it was designed this way (senior/staff):**
3PC's PreCommit phase introduces a critical state (PREPARED) that enables the recovery invariant: "a participant commits unilaterally if and only if all reachable participants are in PREPARED state." This invariant holds ONLY if the network is synchronous — every message either arrives or is definitively lost within bounded time T. In a synchronous network: a participant that timeouts at time T+epsilon knows the coordinator failed, not just delayed. But real networks are asynchronous: messages can be delayed arbitrarily (GC pause, TCP retransmission, congestion). When a partition occurs during Phase 2: some participants receive PreCommit, some don't. Participants on the PreCommit side timeout and commit. Participants on the non-PreCommit side timeout and abort. The states are mixed — 3PC's recovery invariant is violated. Paxos-commit solves this by replacing the coordinator with a Paxos group — the coordinator's decision is itself replicated via consensus (requiring 2f+1 replicas). Coordinator failure is now "Paxos election" not "single point of failure." This is the correct solution: not a different number of phases, but a fault-tolerant coordinator.

**Expert Thinking Cues:**

- "Someone suggests 3PC instead of 2PC for our database" → Ask: "What is our network's synchrony model? How do we handle network partitions?" If they can't answer: 3PC is inappropriate. Real networks are async.
- "We need non-blocking distributed transactions" → Use Paxos-commit (CockroachDB, Spanner), not 3PC. Paxos-commit provides non-blocking without the synchrony assumption.
- "3PC has a third round-trip but is still faster than 2PC in the failure case" → False. 3PC has 3 round-trips ALWAYS (even normal path). 2PC has 2 round-trips (normal path). 3PC is always slower than 2PC for successful transactions.
- "3PC is theoretically correct — why not implement it?" → It's correct only under synchrony assumptions. No major RDBMS (PostgreSQL, MySQL, Oracle, SQL Server) implements 3PC. Even academic distributed databases prefer Raft-commit. 3PC's theoretical elegance hasn't translated to production adoption.

---

### ⚙️ How It Works (Mechanism)

**3PC state machine:**

```
Coordinator states:
  INIT → WAIT → PREPARED → COMMIT/ABORT

Participant states:
  INIT → PREPARED → COMMIT/ABORT

Phase 1 (CanCommit):
  C: send CanCommit(xid) to all
  await YES/NO (with timeout T1)
  if all YES: proceed to Phase 2
  if any NO or timeout: send Abort → done

Phase 2 (PreCommit):
  C: send PreCommit(xid) to all
  await ACK from all (with timeout T2)
  all ACK: proceed to Phase 3
  if any timeout: implementation-specific
    (typically: send Abort if not all ACK'd)

Phase 3 (DoCommit):
  C: send DoCommit(xid) to all
  await ACK
  all ACK: transaction complete

Participant PreCommit handling:
  recv PreCommit(xid):
    state = PREPARED (key state change)
    persist to disk
    send ACK

Recovery (participant times out waiting for DoCommit):
  If state = INIT: safe to abort (no one committed)
  If state = PREPARED:
    query all other participants
    if all PREPARED: commit unilaterally
    if any INIT: abort
    if partition (can't reach all): WAIT (cannot decide)
    ← this wait IS blocking under partition
```

**The partition problem:**

```
Normal (no partition):
  C: PreCommit → DB1 (ACK), DB2 (ACK), DB3 (ACK)
  C crashes before DoCommit
  DB1 contacts DB2, DB3: all PREPARED → commit

Partition during Phase 2:
  C: PreCommit → DB1 (ACK, PREPARED)
                  Network split
               → DB2 (never received, stays INIT)
               → DB3 (never received, stays INIT)
  C crashes
  DB1 side: I'm PREPARED, query others
            cannot reach DB2, DB3 (partition)
            → BLOCKED (cannot determine)
  DB2+DB3 side: we're INIT, query each other
                both INIT → abort
  Result if DB1 timeout and commits:
    DB1: COMMITTED, DB2+DB3: ABORTED
    ← inconsistency
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL 3PC FLOW:**

```
Client  Coordinator  DB1          DB2
  │         │          │            │
  │─begin──▶│          │            │
  │         │─CanCommit▶│           │
  │         │─CanCommit──────────▶│
  │         │◀─YES──────│           │
  │         │           │◀───YES────│
  │         │─PreCommit─▶│          │
  │         │─PreCommit──────────▶│
  │         │◀─ACK──────│           │
  │         │           │◀───ACK────│
  │         │─DoCommit──▶│          │
  │         │─DoCommit───────────▶│
  │         │◀─ACK──────│           │
  │         │           │◀───ACK────│
  │◀─done──│ ← YOU ARE HERE (3 RTTs vs 2PC's 2)
```

**FAILURE PATH (coordinator crashes after PreCommit):**
Both DB1 and DB2 are in PREPARED state. DB1 queries DB2 on timeout. Both PREPARED. Both commit unilaterally. Correct outcome — the non-blocking property works here.

**WHAT CHANGES AT SCALE:**
Every successful transaction pays 3 RTTs instead of 2PC's 2. For geo-distributed participants (100ms per RTT): 3PC = 300ms minimum vs 2PC = 200ms. This 50% latency increase for ALL transactions, not just failure cases. At scale: this overhead is prohibitive. CockroachDB's parallel commits achieve non-blocking behavior with approximately 2PC latency by using Raft replication rather than a third protocol phase.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
3PC participants hold resource locks from Phase 1 through Phase 3 — same as 2PC, but for longer (3 RTTs). Under high contention: lock hold time scales with network latency × 3, not × 2. In geo-distributed databases: 3PC increases lock contention 50% vs 2PC even in the normal (non-failure) path.

---

### ⚖️ Comparison Table

| Property                   | 2PC              | 3PC               | Paxos-Commit       | Saga   |
| :------------------------- | :--------------- | :---------------- | :----------------- | :----- |
| Blocking on coord. failure | Yes (indefinite) | No (sync network) | No                 | N/A    |
| Safe under partitions      | Yes              | No                | Yes                | N/A    |
| Network rounds (normal)    | 2 RTTs           | 3 RTTs            | 2-4 RTTs           | Async  |
| Synchrony assumption       | No               | Yes               | No                 | No     |
| Production adoption        | Wide (XA)        | Near zero         | High (CockroachDB) | High   |
| Global atomicity           | Yes              | Yes               | Yes                | No     |
| Practical complexity       | Medium           | High              | High               | Medium |

---

### ⚠️ Common Misconceptions

| Misconception                                                                | Reality                                                                                                                                                                                                                                                                                                                            |
| :--------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "3PC fixes 2PC's blocking problem"                                           | 3PC fixes blocking ONLY in synchronous networks. In asynchronous networks (all real networks), 3PC can commit on one partition side while aborting on the other — a WORSE outcome than 2PC's blocking (inconsistency vs. temporary unavailability).                                                                                |
| "3PC is the algorithm used by distributed databases that claim non-blocking" | CockroachDB, Spanner, and other modern distributed databases use Paxos-based (Raft-based) commit, NOT 3PC. They replicate the coordinator role via consensus — eliminating coordinator SPOF without the synchrony assumption.                                                                                                      |
| "3PC is 2PC with one extra round-trip"                                       | 3PC adds a round-trip to EVERY transaction (including successful ones), not just failure scenarios. 2PC has 2 RTTs for normal flow. 3PC has 3 RTTs ALWAYS. 3PC makes every transaction 50% slower than 2PC.                                                                                                                        |
| "3PC is safer than 2PC under partitions"                                     | 3PC is LESS safe than 2PC under partitions. 2PC blocks (temporary unavailability). 3PC can split-commit (permanent inconsistency). Inconsistency is worse than unavailability for correctness-critical systems. CAP theorem: 3PC chooses availability over consistency under partition; 2PC chooses consistency over availability. |
| "Real databases will implement 3PC as hardware gets more reliable"           | Hardware reliability doesn't eliminate network partitions (different failure model). The synchrony assumption required by 3PC is a network model assumption, not a hardware assumption. Even infinitely reliable nodes can be partitioned by a network switch failure. Paxos/Raft solved this correctly; 3PC did not.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Partition During PreCommit Causes Split-Brain Commit**

**Symptom:** Financial transaction shows balance deducted on Database A but NOT added to Database B. Both databases claim no active transactions. No error in application logs. The inconsistency is discovered during end-of-day reconciliation.
**Root Cause:** A network partition occurred during Phase 2 (PreCommit) of a 3PC transaction. DB A received PreCommit (state=PREPARED), timed out, found no other reachable participants, and committed unilaterally. DB B never received PreCommit (state=INIT), timed out, and aborted. Result: split-brain commit.
**Diagnostic:**

```bash
# Check for brief network partition during the transaction window:
# (If 3PC were in use — hypothetical)
# Look for network drop in infrastructure logs:
grep "network\|timeout\|connection reset" \
  /var/log/syslog | grep "2024-01-15 14:30" | head -20

# Check for brief disconnect on database connections:
psql -c "
  SELECT client_addr, state, query, query_start
  FROM pg_stat_activity
  WHERE query_start BETWEEN
    '2024-01-15 14:30:00' AND '2024-01-15 14:31:00';"

# Audit: did both databases apply the transaction?
psql -h dbA -c "SELECT * FROM audit_log
               WHERE xid='abc-123';"
psql -h dbB -c "SELECT * FROM audit_log
               WHERE xid='abc-123';"
# If dbA has COMMITTED and dbB has ABORTED: split-brain
```

**Fix:**
BAD: Implementing 3PC for production distributed transactions.
GOOD: Use 2PC (blocks, doesn't split) or Paxos-commit (non-blocking AND partition-safe). For the inconsistency: requires manual data reconciliation and application-layer audit to determine which state is correct.
**Prevention:** Don't use 3PC in asynchronous networks. Use 2PC for strict atomicity with blocking trade-off, or Paxos-commit (CockroachDB) for non-blocking with partition safety.

**Failure Mode 2: False Coordinator Failure — Participant Commits While Coordinator Is Alive**

**Symptom:** 3PC participant detects coordinator timeout (long GC pause on coordinator). Participant queries others: all PREPARED. Participant commits unilaterally. Coordinator recovers from GC, sends DoCommit — which is correct. But coordinator never receives ACK (participant already committed and cleaned up state). Coordinator marks transaction as pending — attempts recovery — eventually rolls back its side (thinking participant failed).
**Root Cause:** The participant's timeout fired during coordinator GC pause (not a crash). Participant's autonomous commit was correct, but coordinator state machine diverged. This is the "false timeout" problem — async networks make timeout-based failure detection unreliable.
**Diagnostic:**

```bash
# Check coordinator GC logs for pauses > participant timeout:
grep "GC\|pause\|Full GC\|stop-the-world" \
  /var/log/coordinator/gc.log | \
  awk '$NF > 30000 {print}'
# GC pauses > 30s (hypothetical participant timeout)
# = risk of false coordinator failure detection

# Check transaction state divergence:
# Participant log: committed at 14:30:45
# Coordinator log: still pending at 14:30:45
# (GC pause 14:30:30 to 14:31:15 = coordinator unavailable 45s)
```

**Fix:**
BAD: Short timeout values in environments with JVM GC pauses.
GOOD: (1) Don't use 3PC. (2) If using 3PC: set participant timeout > worst-case GC pause. (3) Use GC algorithms that minimize stop-the-world (G1, ZGC). (4) Use Paxos-based commit where coordinator failure = Raft leader election, not timeout-based.
**Prevention:** Monitor coordinator GC pause times. Alert if pause > half the participant timeout threshold. Consider this a category of problem unique to 3PC's timeout-based recovery.

**Failure Mode 3: Security - 3PC's Recovery Protocol Exposes Inter-Participant Queries**

**Symptom:** During recovery (after coordinator timeout), a participant contacts other participants directly to determine PREPARED/INIT state. An attacker intercepts these queries and responds with false state ("all PREPARED") causing a participant to commit a transaction that should have been aborted.
**Root Cause:** 3PC's recovery requires inter-participant communication — participants must query each other's state. If this channel is not authenticated: an attacker can inject false state responses, manipulating transaction outcomes. In 2PC: participants only communicate with the coordinator (single trusted channel). In 3PC: participants communicate with each other during recovery — expanding the attack surface.
**Diagnostic:**

```bash
# Check if inter-participant recovery communication is authenticated:
# Wireshark capture on participant-to-participant recovery port:
tcpdump -i eth0 -w /tmp/recovery.pcap \
  port 5432 and host participant2-ip

# Analyze: are recovery queries using TLS with cert auth?
openssl s_client -connect participant2-ip:5432 \
  -cert /etc/ssl/client.crt -key /etc/ssl/client.key
# If connection succeeds without certs: unauthenticated channel
```

**Fix:**
BAD: Recovery protocol running over unencrypted, unauthenticated connections.
GOOD: (1) mTLS between all participants for recovery protocol. (2) Hardware-backed certificate authentication. (3) Network-level isolation: participants only reachable from each other and the coordinator, not from arbitrary network hosts.
**Prevention:** 3PC's expanded attack surface (participant-to-participant communication) is an additional reason to avoid it. 2PC's simpler coordinator-only communication is easier to secure.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-033 - Two-Phase Commit (2PC) (3PC is a direct extension of 2PC — understanding 2PC is mandatory)
- DST-032 - Failure Modes (understanding crash vs. partition failures explains why 3PC fails in async networks)

**Builds On This (learn these next):**

- Nothing directly in this category — 3PC is a dead end in practice

**Alternatives / Comparisons:**

- DST-033 - Two-Phase Commit (2PC blocking vs. 3PC non-blocking trade-off)
- DST-034 - Two-Phase Commit practical (XA implementations that use 2PC, not 3PC)
- DST-024 - Paxos (Paxos-commit is the practical non-blocking alternative to 3PC)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | 3-phase distributed commit:    |
|                  | CanCommit + PreCommit + Commit |
+------------------+--------------------------------+
| PROBLEM SOLVED   | 2PC coordinator-crash blocking |
|                  | (in synchronous networks only) |
+------------------+--------------------------------+
| KEY INSIGHT      | PreCommit propagates "all voted|
|                  | YES" knowledge — enables       |
|                  | autonomous participant decision |
+------------------+--------------------------------+
| USE WHEN         | Synchronous network (theory)   |
|                  | Rarely used in practice        |
+------------------+--------------------------------+
| AVOID WHEN       | Async networks (always)        |
|                  | Use Paxos-commit instead       |
+------------------+--------------------------------+
| TRADE-OFF        | Non-blocking (sync network) vs |
|                  | unsafe under partition + 3 RTT |
+------------------+--------------------------------+
| ONE-LINER        | Fixes 2PC blocking by adding   |
|                  | PreCommit, but breaks under    |
|                  | network partitions             |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-024 Paxos (correct fix),   |
|                  | DST-033 Two-Phase Commit       |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. 3PC adds PreCommit phase: "everyone knows everyone voted YES." This allows participants to commit autonomously if coordinator crashes after PreCommit.
2. 3PC is only safe in synchronous networks. Real networks are asynchronous — partitions cause split-brain commits (inconsistency), which is worse than 2PC's blocking.
3. Almost no production system uses 3PC. Modern alternative: Paxos-commit (Raft-replicated coordinator) — non-blocking AND partition-safe. Use Saga for eventual consistency without 2PC/3PC complexity.

**Interview one-liner:**
"Three-Phase Commit adds a PreCommit phase to 2PC to eliminate blocking on coordinator failure: after PreCommit, all participants know everyone voted YES, so they can autonomously commit if the coordinator fails. But this non-blocking property requires a synchronous network — bounded message delays that make 'timeout' a reliable indicator of coordinator failure. Real networks are asynchronous: a partition during PreCommit can cause some participants to commit while others abort, violating atomicity — a worse outcome than 2PC's blocking. This is why 3PC is almost never used in production; Paxos-commit (used in CockroachDB, Spanner) achieves non-blocking atomicity correctly by replicating the coordinator via Raft."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Adding protocol phases to eliminate one failure mode often introduces a new, harder failure mode in a different scenario. 2PC blocks on coordinator failure — 3PC eliminated this by adding PreCommit, but introduced split-brain under partition. The correct fix for blocking was not a third phase but a fault-tolerant coordinator (Paxos/Raft replication). When designing protocols: identify the COMPLETE failure space before proposing fixes. A fix that handles failure mode A while introducing failure mode B may be worse, especially if B is less detectable than A (inconsistency is harder to detect than blocking).

**Where else this pattern appears:**

- **TCP three-way handshake (not 3PC, but three-phase coordination):** TCP's SYN → SYN-ACK → ACK establishes bidirectional communication with three messages. Each phase ensures the other party is ready before committing resources (ports, buffers). Like 3PC's PreCommit, the SYN-ACK propagates "I received your readiness signal" before the final ACK completes the handshake. Unlike 3PC: TCP handles half-open connections explicitly (timeout + RST) — TCP's recovery protocol is more robust than 3PC's because TCP does NOT assume a synchronous network.
- **Distributed lock release protocols (ticket + grant + confirm):** Some distributed lock managers use a 3-phase grant: (1) request lock (CanCommit), (2) coordinator grants tentatively / notifies all waiters "lock will be granted" (PreCommit — prevents new lock requests from racing), (3) coordinator confirms grant to requester (DoCommit). The PreCommit-equivalent prevents lock convoy races. But under partition: same split-brain risk as 3PC — two requesters may both believe they have the lock. Production lock managers (Redlock, ZooKeeper) use quorum-based approaches (Raft-like) rather than 3PC-like protocols.
- **Atomic broadcast protocols in cluster management:** Cluster managers (Pacemaker, Kubernetes leader election) use a "propose → prepare → commit" sequence when electing a new leader. The "prepare" phase corresponds to PreCommit: once a majority acknowledges "I'm prepared to accept this leader," the cluster can proceed even if the original proposer fails. Unlike 3PC: these systems use quorum (majority of nodes, not all nodes) — eliminating the unanimity requirement that makes 3PC fragile. This is Paxos's key improvement over 3PC's all-or-nothing unanimity assumption.

---

### 💡 The Surprising Truth

Three-Phase Commit has been known since 1981 and provably eliminates 2PC's blocking in synchronous networks. Yet in over 40 years of distributed systems engineering, no major relational database (Oracle, PostgreSQL, MySQL, SQL Server, DB2) has ever implemented 3PC. This is remarkable: 2PC's blocking problem is well-documented and has caused real production outages at major companies. Why was 3PC never adopted? The answer is not purely theoretical: database vendors chose to solve 2PC's blocking problem with OPERATIONAL solutions (better TM recovery, HA coordinators, faster crash detection) rather than algorithmic solutions (3PC). And the practical reality: real-world distributed transactions typically involve at most 2-3 participants, coordinator crashes are rare (TMs are carefully engineered), and when blocking occurs — it is DETECTABLE (DBAs can see stuck pg_prepared_xacts). Split-brain commits (3PC's failure mode) are UNDETECTABLE until business-level reconciliation finds discrepancies. A problem you can detect and fix is better than one you discover too late. This is perhaps the deepest lesson: operational detectability of failure modes matters as much as theoretical correctness when choosing protocols.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** 3PC's safety guarantee requires that all participants can determine their recovery action (commit or abort) by querying other participants' state after coordinator failure. This requires "communication reliability" — participants can eventually reach each other. But the FLP impossibility theorem (1985) states that in an asynchronous network with even one possible crash failure: no deterministic protocol can guarantee both safety AND liveness. How does FLP apply to 3PC? Specifically: does 3PC satisfy safety (consistency) and/or liveness (termination) in an async network? Where does 3PC fail relative to FLP's conditions?
_Hint:_ 3PC in asynchronous network: under partition, some participants can be permanently unreachable. Participant in PREPARED state that cannot reach others is STUCK (liveness violation) — cannot determine commit/abort without knowing others' state. If it commits unilaterally after timeout: safety violation (others may abort). 3PC cannot satisfy BOTH safety AND liveness in async network: safety violation under partition commit scenario, liveness violation in permanent partition without timeout unilateral commit. FLP says this is unavoidable — 3PC chose neither correctly (violates both in different failure scenarios). Paxos: sacrifices liveness under partition (waits for quorum) but preserves safety. Compare: which failure is more tolerable for your system?

**Q2 (F - Comparison):** Compare 3PC and Paxos-commit on three dimensions: (1) protocol complexity (number of messages, phases), (2) safety guarantees under network partitions, (3) failure recovery mechanism. Why did production distributed databases choose Paxos-commit (CockroachDB, Spanner) over 3PC, given both provide non-blocking commitment? What specific property of Paxos makes it better than 3PC for the partition case?
_Hint:_ 3PC recovery: participant queries others, needs response from ALL to determine state — unanimity required even in recovery. Paxos-commit recovery: coordinator role (Paxos leader) is re-elected by QUORUM (majority) — no need for ALL nodes to respond, only majority. Under partition: Paxos can elect a new leader on the majority side and proceed — liveness maintained for the majority partition. Minority partition blocks (cannot make progress without majority) — safety maintained. 3PC requires all participants in recovery — under partition, recovery blocks on unreachable participants, leading to timeout-based autonomous decision — safety violation possible. The key Paxos property: quorum (majority, not unanimity) for progress decisions. How does this single change (unanimity → quorum) eliminate 3PC's partition problem?

**Q3 (B - Scale):** At 100,000 transactions per second (TPS), each transaction involving 3 XA participants geo-distributed across 3 data centers (100ms RTT each): calculate the theoretical minimum latency for (a) 2PC, (b) 3PC. Then calculate the total system throughput impact: how many concurrent transactions must be in-flight at any moment to sustain 100,000 TPS for each protocol? What does this imply about lock contention on hot rows?
_Hint:_ 2PC latency: 2 RTTs × 100ms = 200ms minimum. 3PC latency: 3 RTTs × 100ms = 300ms minimum. Little's Law: N = TPS × latency. For 100,000 TPS: 2PC: 100,000 × 0.2s = 20,000 concurrent transactions. 3PC: 100,000 × 0.3s = 30,000 concurrent transactions. Lock contention: 30,000 concurrent transactions each holding locks on rows. If any rows are "hot" (accessed by multiple transactions): 30,000 contenders vs 20,000. 50% more concurrent lock holders = significantly higher contention probability. How does this latency/concurrency relationship explain why even a non-blocking protocol (3PC) can reduce throughput compared to a blocking one (2PC) in high-throughput scenarios?
