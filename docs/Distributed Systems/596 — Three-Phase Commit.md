---
layout: default
title: "Three-Phase Commit (3PC)"
parent: "Distributed Systems"
nav_order: 596
permalink: /distributed-systems/three-phase-commit/
number: "0596"
category: Distributed Systems
difficulty: ★★★
depends_on: Two-Phase Commit, Distributed Transactions, Failure Modes
used_by: Rarely in production; academic basis for Paxos Commit
related: Two-Phase Commit, Saga Pattern, Consensus
tags:
  - 3pc
  - three-phase-commit
  - distributed-transactions
  - advanced
---

# 596 — Three-Phase Commit (3PC)

⚡ TL;DR — Three-Phase Commit adds a "Pre-Commit" phase between 2PC's Prepare and Commit phases to eliminate the blocking problem in one common crash scenario. In 2PC, coordinator crash after votes leaves participants blocked. In 3PC, participants know whether the decision was unanimous-yes (pre-commit) before committing, allowing them to make a safe unilateral decision if the coordinator fails. However, 3PC is NOT safe under network partition (which 2PC handles better) — making it rarely used in production compared to Raft/Paxos-based commit.

┌──────────────────────────────────────────────────────────────────────────┐
│ #596         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Two-Phase Commit                    │                      │
│ Related:     │ 2PC, Saga Pattern, Consensus        │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

In 2PC: coordinator crashes after collecting all YES votes but before sending COMMIT. Participants are doomed to wait — they can't abort (they voted yes) and can't commit (no official COMMIT received). 3PC adds a PRE-COMMIT phase: after collecting all votes, coordinator broadcasts PRE-COMMIT (ack that all voted yes). If coordinator then crashes: a participant in PRE-COMMIT state knows all voted yes → can safely commit unilaterally (since unanimous-yes is guaranteed). No blocking under coordinator crash.

---

### 📘 Textbook Definition

**Three-Phase Commit (3PC)** adds a PRE-COMMIT phase to 2PC:

**Phase 1 — CanCommit (same as 2PC Prepare):**
- Coordinator: "can you commit?"
- Participants: vote YES or NO (acquire locks, validate)

**Phase 2 — PreCommit:**
- If all YES: coordinator sends PRE-COMMIT to all; each participant ACKs
- PRE-COMMIT receipt = "I know everyone voted yes; safe to commit even without coordinator"
- If any NO: coordinator sends ABORT immediately

**Phase 3 — DoCommit:**
- Coordinator sends COMMIT; participants execute and release locks

**Non-blocking property:** If coordinator crashes after Phase 2, a participant that received PRE-COMMIT can unilaterally commit (it knows all participants voted yes). A participant that did NOT receive PRE-COMMIT should abort (safe default).

**Fatal limitation:** Under network partition, two participants may make different unilateral decisions — one commits (received PRE-COMMIT), one aborts (didn't receive it) — violating atomicity. This makes 3PC non-safe under network partition.

---

### ⏱️ Understand It in 30 Seconds

**One line:** 3PC adds a "yes, everyone voted yes" signal before the final commit, allowing participants to decide unilaterally on coordinator crash — but breaks under network partition.

**Analogy:** 2PC = voters commit their ballots (locked), wait for official announcement. If announcer crashes: votes locked, no winner declared (blocking). 3PC = after collecting all "yes" votes, announcer first distributes pre-printed "unanimous yes" cards to everyone, THEN announces the win. If announcer crashes after cards distributed: everyone can independently declare the result (they all have the evidence). But if a network delay means some people got the pre-printed card and some didn't → some declare win, some declare loss → contradiction.

---

### 🔩 First Principles Explanation

```
2PC vs 3PC BLOCKING DIFFERENCE:

  2PC: After Phase 1 (all vote YES), if coordinator crashes:
       Participants are UNCERTAIN — they voted yes (can't abort) but no COMMIT (can't commit)
       → BLOCKED waiting for coordinator recovery
  
  3PC: Phase 2 (PRE-COMMIT) creates a SHARED commitment record:
       If participant has PRE-COMMIT: knows all voted yes → can commit unilaterally ✓
       If participant has no PRE-COMMIT: knows abort is safe → aborts ✓
       → NOT BLOCKED
  
  BUT: NETWORK PARTITION flaw in 3PC:
  
  5 participants: {A, B, C, D, E}
  Coordinator: sends PRE-COMMIT to A, B, C but crashes.
  Network partition: A,B,C in one group; D,E in another.
  
  A,B,C: "We all got PRE-COMMIT → new coordinator among us → COMMIT" ✓
  D,E:   "We never got PRE-COMMIT → timeout → ABORT" ← PROBLEM
  
  Network heals: A,B,C committed; D,E aborted → INCONSISTENCY! ✗
  
  2PC UNDER SAME PARTITION:
  A,B,C: cannot form quorum (need all 5 or coordinator) → BLOCKED (but safe!)
  D,E:   same → BLOCKED
  When partition heals: coordinator recovers, sends decision to all. Consistent. ✓
```

---

### 🧠 Mental Model / Analogy

> 3PC vs 2PC is the blocking vs. partition safety trade-off. 2PC is a synchronous democracy: no decision without the central coordinator (safe but blocking). 3PC is a representative democracy: if the president disappears after passing a unanimous pre-vote notice to representatives, they can still act — but two groups of representatives cut off from each other might enact contradictory laws simultaneously.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** 3PC adds a pre-commit confirmation to allow non-blocking termination when coordinator crashes. But introduces inconsistency risk under network partition. Tradeoff: availability (non-blocking) vs. partition safety.

**Level 2:** Why 3PC is rarely used in production: (a) network partitions are as common as coordinator crashes in cloud environments, (b) 3PC has more message rounds (6 vs 4) = more latency, (c) FLP impossibility means no algorithm can be both safe and live with even 1 crash — 3PC chooses liveness (non-blocking) over safety (inconsistency possible). Modern practice: use Raft-based commit (Spanner, CockroachDB) which handles both crash and partition via consensus.

**Level 3:** Paxos Commit (Gray & Lamport 2006): instead of a single coordinator, use a separate Paxos instance for each transaction phase. Each participant's vote is agreed upon via Paxos (replicated). Coordinator crash: new coordinator can re-derive the decision from committed Paxos log. No blocking, no partition inconsistency. This is what Google Spanner uses (with TrueTime for external consistency). The downside: significant complexity and latency overhead from multiple Paxos rounds.

**Level 4:** 3PC's timeout-based termination protocol: if a participant times out waiting for PRE-COMMIT, it initiates a termination protocol — contacts all other participants to determine their state. If ANY participant has COMMIT state or PRE-COMMIT: commit. If NO participant has any record beyond PREPARE: abort. This requires reliable peer-to-peer communication. In practice, network partitions make this termination consultation unreliable — exactly the source of 3PC's inconsistency risk.

---

### ⚙️ How It Works (Mechanism)

```
3PC PHASE DIAGRAM:

  Coordinator → Participants:
  
  Phase 1: CANCOMMIT
  ┌─────────────────────────────────────────────────────────────┐
  │  Coord → P1: "Prepare TXN-42"                               │
  │  Coord → P2: "Prepare TXN-42"                               │
  │  P1 → Coord: VOTE-YES (locks acquired)                      │
  │  P2 → Coord: VOTE-YES (locks acquired)                      │
  └─────────────────────────────────────────────────────────────┘
  
  Phase 2: PRECOMMIT (new vs 2PC)
  ┌─────────────────────────────────────────────────────────────┐
  │  Coord → P1: "Pre-Commit TXN-42 (all voted yes)"            │
  │  Coord → P2: "Pre-Commit TXN-42 (all voted yes)"            │
  │  P1 → Coord: ACK                                            │
  │  P2 → Coord: ACK                                            │
  │  [COORDINATOR CRASHES HERE]                                  │
  │  → P1, P2 received PRE-COMMIT → elect new coordinator among │
  │    them → new coordinator sends DOCOMMIT → both commit ✓    │
  └─────────────────────────────────────────────────────────────┘
  
  Phase 3: DOCOMMIT
  ┌─────────────────────────────────────────────────────────────┐
  │  Coord → P1: "Commit TXN-42"                                │
  │  Coord → P2: "Commit TXN-42"                                │
  │  P1 → Coord: ACK (commits, releases locks)                  │
  │  P2 → Coord: ACK (commits, releases locks)                  │
  └─────────────────────────────────────────────────────────────┘
  
  COORDINATOR CRASH RECOVERY TABLE:
  ┌──────────────────────────────────┬──────────────────────────┐
  │ Participant State                │ Safe Unilateral Action   │
  ├──────────────────────────────────┼──────────────────────────┤
  │ INIT (before CANCOMMIT)          │ ABORT                    │
  │ PREPARED (voted YES)             │ ABORT (blocking in 2PC!) │
  │ PRE-COMMITTED                    │ COMMIT                   │
  │ COMMITTED                        │ Already done             │
  │ ABORTED                          │ Already done             │
  └──────────────────────────────────┴──────────────────────────┘
```

---

### 💻 Code Example

```java
// 3PC state machine (conceptual implementation — rarely used in production as is)
// Illustrates the state transitions and non-blocking property

public enum ThreePhaseState {
    INIT, PREPARED, PRE_COMMITTED, COMMITTED, ABORTED
}

public class ThreePhaseParticipant {
    private ThreePhaseState state = ThreePhaseState.INIT;
    private final TransactionLog log;

    // Phase 1: receive CANCOMMIT from coordinator
    public Vote onCanCommit(Transaction txn) {
        try {
            txn.execute();       // Try executing the transaction
            txn.acquireLocks();  // Acquire all required locks
            log.write("PREPARED", txn.getId()); // Durable log
            state = ThreePhaseState.PREPARED;
            return Vote.YES;
        } catch (Exception e) {
            state = ThreePhaseState.ABORTED;
            return Vote.NO;
        }
    }

    // Phase 2: receive PRECOMMIT from coordinator
    public void onPreCommit(String txnId) {
        log.write("PRE_COMMITTED", txnId); // Durable: can now safely commit unilaterally
        state = ThreePhaseState.PRE_COMMITTED;
        // ACK back to coordinator
    }

    // Phase 3: receive DOCOMMIT from coordinator (or decide unilaterally)
    public void onDoCommit(String txnId) {
        txn.commit();  // Apply changes durably
        txn.releaseLocks();
        log.write("COMMITTED", txnId);
        state = ThreePhaseState.COMMITTED;
    }

    // Called on coordinator timeout — non-blocking termination
    public void onCoordinatorTimeout() {
        switch (state) {
            case PRE_COMMITTED:
                // Safe to commit: we know all voted yes (PRE_COMMITTED state)
                onDoCommit(currentTxnId);
                break;
            case PREPARED:
                // Coordinate with other participants to determine decision
                consultPeers(); // If any peer is PRE_COMMITTED → commit; else → abort
                break;
            case INIT:
                state = ThreePhaseState.ABORTED;
                break;
            default:
                break; // Already committed or aborted
        }
    }
}
```

---

### ⚖️ Comparison Table

| Property | 2PC | 3PC | Raft/Paxos Commit |
|---|---|---|---|
| **Coordinator crash blocking** | YES (blocks participants) | NO (non-blocking) | NO (replicated coordinator) |
| **Network partition safe** | YES (blocks, but consistent) | NO (can diverge) | YES |
| **Message rounds** | 4 | 6 | Raft RTT + 2 |
| **Production usage** | Common (XA) | Rare | Common (Spanner, CockroachDB) |
| **Complexity** | Medium | High | Very High |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ PHASES        │ CanCommit → PreCommit → DoCommit            │
│ NON-BLOCKING  │ Crash after Phase 2: PRE-COMMITTED → commit │
│ FATAL FLAW    │ Network partition: two groups decide        │
│               │ differently → inconsistency                 │
│ RULE          │ Use 3PC only in crash-only environments     │
│               │ (no network partitions) — rare in practice  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Consider a distributed financial transaction across 3 nodes (A, B, C). The system uses 3PC. During Phase 2 (PreCommit), node A receives PRE-COMMIT but nodes B and C do not due to a message drop. The coordinator then crashes. (1) What does node A do? What do B and C do when they time out? (2) If A, B, C can communicate peer-to-peer (termination protocol): will they reach a consistent decision? (3) If a network partition also isolates A from B,C during the termination protocol: what happens? (4) How does Google Spanner avoid this problem (hint: Paxos per-participant, TrueTime)?
