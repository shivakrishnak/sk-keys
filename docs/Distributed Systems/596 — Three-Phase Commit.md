---
layout: default
title: "Three-Phase Commit"
parent: "Distributed Systems"
nav_order: 596
permalink: /distributed-systems/three-phase-commit/
number: "596"
category: Distributed Systems
difficulty: ★★★
depends_on: "Two-Phase Commit, Failure Modes"
used_by: "Theoretical reference; rarely used in production directly"
tags: #advanced, #distributed, #transactions, #consistency, #atomicity
---

# 596 — Three-Phase Commit

`#advanced` `#distributed` `#transactions` `#consistency` `#atomicity`

⚡ TL;DR — **Three-Phase Commit (3PC)** extends 2PC with a "Pre-Commit" phase to eliminate the blocking problem — but remains unsafe under network partitions, which is why Paxos Commit and Saga patterns are preferred in practice.

| #596 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Two-Phase Commit, Failure Modes | |
| **Used by:** | Theoretical reference; rarely used in production directly | |

---

### 📘 Textbook Definition

**Three-Phase Commit (3PC)** is a distributed atomic commit protocol proposed by Skeen (1982) to overcome the blocking problem of 2PC. 3PC adds a **Pre-Commit phase** between the Prepare/Vote phase and the final Commit phase. The protocol has three phases: **Phase 1 (CanCommit)** — coordinator asks all participants if they can commit; participants respond yes/no; **Phase 2 (PreCommit)** — if all said yes: coordinator sends PreCommit; participants enter a "prepared to commit" state and ACK; **Phase 3 (DoCommit)** — coordinator sends DoCommit; participants commit. Key property: if a participant has received PreCommit (Phase 2), it knows the coordinator will eventually commit — so if the coordinator crashes after PreCommit, participants can independently proceed with commit (non-blocking). If coordinator crashes before PreCommit (in Phase 1), participants time out and abort. **Safety requirement**: 3PC is safe under crash-stop failures but NOT under network partitions. If a partition occurs after some participants receive PreCommit and others don't — the two partitions may disagree (some commit, some abort). This is why 3PC is primarily of theoretical interest; in practice, Paxos Commit (non-blocking AND partition-safe) or the Saga pattern are preferred.

---

### 🟢 Simple Definition (Easy)

3PC vs 2PC: 2PC blocks if the coordinator dies in the "uncertainty window" (after votes but before commit). 3PC adds a middle step: "Pre-Commit" tells everyone "we're definitely going to commit." If coordinator then dies: everyone knows they should commit and can proceed without the coordinator. Like a wedding: Phase 1: "Do you?" Phase 2: "You've both said yes — we're proceeding" (pre-commit). Phase 3: "You're married." If officiant fainted after Phase 2: attendees know both agreed, so the ceremony is complete. Problem: if a network blackout split the room in Phase 2 (some heard it, some didn't) — half the room thinks it happened, half doesn't.

---

### 🔵 Simple Definition (Elaborated)

Why 3PC is not used in practice: it eliminates blocking under crash-stop failures. But the real world has network partitions, not just crashes. Under partition: a participant in partition A received PreCommit → commits. Participant in partition B didn't get PreCommit → times out → aborts. Two participants now have different states = exactly what 2PC prevents. The fix would require quorum (majority agreement) — which is what Paxos Commit does. Paxos Commit is both non-blocking (tolerates coordinator failure) AND partition-safe (majority quorum). When you see "3PC" in architecture discussions: it usually means "we want non-blocking 2PC" — the actual solution should be Paxos Commit or Saga.

---

### 🔩 First Principles Explanation

**3PC phases and the blocking vs. partition safety trade-off:**

```
3PC PROTOCOL:

  PARTICIPANTS: P1, P2, P3.
  COORDINATOR: C.
  
  ─── PHASE 1: CAN-COMMIT ─────────────────────────────────────────────
  
  C → P1, P2, P3: CANCOMMIT?(txn_id=T1)
  
  Each participant:
    If can execute (constraints satisfied, resources available): replies YES.
    If cannot (constraint violation, resource unavailable): replies NO.
    State: "uncertain" (neither committed nor aborted).
  
  C: receives responses.
    If all YES: proceed to Phase 2.
    If any NO or timeout: send ABORT to all. Transaction aborted. 
    (Participants are in "uncertain" state → can abort safely.)
  
  ─── PHASE 2: PRE-COMMIT ─────────────────────────────────────────────
  
  C: all participants said YES. Sends PRECOMMIT to all.
  
  Each participant receiving PRECOMMIT:
    Writes PRECOMMIT record to WAL.
    State: "prepared" (committed to committing if coordinator commits).
    Replies: ACK.
    
  KEY INSIGHT: A participant in "prepared" state KNOWS that all others also voted YES
  (because coordinator only sends PRECOMMIT if all voted YES).
  Therefore: if coordinator crashes NOW, a prepared participant can infer 
  that COMMIT was the decision (everyone voted yes, coordinator was about to commit).
  
  C: receives all ACKs. Proceeds to Phase 3.
  
  ─── PHASE 3: DO-COMMIT ──────────────────────────────────────────────
  
  C → P1, P2, P3: DOCOMMIT(txn_id=T1)
  
  Each participant: applies transaction. Releases locks. ACKs coordinator.
  
  C: transaction complete. Cleanup.

FAILURE SCENARIOS IN 3PC:

  SCENARIO A: Coordinator crashes after sending PRECOMMIT to P1, P2, P3 (all got PRECOMMIT).
    C crashes. P1, P2, P3: all in "prepared" state.
    P1, P2, P3: wait T seconds for DOCOMMIT (timeout).
    
    Recovery protocol (TERMINATION PROTOCOL):
      P1 (or any prepared participant): becomes temporary coordinator.
      P1 contacts P2, P3: "Are you prepared?"
      P2: YES. P3: YES. All prepared.
      P1: "All prepared. Decision = COMMIT." Sends DOCOMMIT to P2, P3.
      All commit. NON-BLOCKING. 
      
    KEY: all are prepared → safe to commit independently. No ambiguity.
    
  SCENARIO B: Coordinator crashes after CANCOMMIT, before any PRECOMMIT.
    C crashes. P1, P2, P3: all in "uncertain" state.
    
    Recovery protocol:
      P1 contacts P2, P3: "Are you prepared?"
      P2: "No, I'm uncertain." P3: "No, I'm uncertain."
      Nobody is prepared. Decision = ABORT (safe: nobody has committed anything).
      P1 sends ABORT to P2, P3. All abort. NON-BLOCKING.
      
  SCENARIO C: Coordinator crashes after PRECOMMIT to P1, P2 but before P3 gets PRECOMMIT.
    C crashes. P1: prepared. P2: prepared. P3: uncertain.
    
    Recovery protocol:
      P1 contacts P2, P3: "Are you prepared?"
      P2: YES. P3: NO (uncertain).
      
      WHAT SHOULD P1 DECIDE?
        P1 and P2 are prepared → commit would be correct.
        P3 is uncertain → doesn't know if PRECOMMIT was going to be sent.
        
      3PC RULE: if ANY participant is prepared → COMMIT.
        Reason: coordinator only sends PRECOMMIT if ALL voted YES (Phase 1).
                 P1 and P2 being prepared proves all voted YES.
                 Therefore: correct decision is COMMIT (coordinator would have committed).
      
      P1 sends PRECOMMIT to P3. P3 enters prepared state. P1 sends DOCOMMIT to all.
      All commit. Correct.
      
  SCENARIO D: NETWORK PARTITION DURING PHASE 2. (3PC FAILS HERE)
    C sends PRECOMMIT to P1, P2 (received). C sends PRECOMMIT to P3, P4 (network drops).
    
    Network partitions: {P1, P2} and {P3, P4}.
    
    {P1, P2}: both prepared. Termination protocol: all prepared → COMMIT. COMMIT.
    {P3, P4}: both uncertain. Termination protocol: nobody prepared → ABORT. ABORT.
    
    Partition heals:
    P1, P2: COMMITTED.
    P3, P4: ABORTED.
    
    TWO DIFFERENT OUTCOMES. DATA INCONSISTENCY. 3PC FAILS UNDER PARTITION.
    
  WHY PARTITION SAFETY REQUIRES QUORUM:
    For non-blocking AND partition-safe: need Paxos Commit.
    Paxos Commit: each participant's vote is a Paxos consensus instance.
    Commit = when all participants' Paxos instances choose "commit."
    Partition: only the majority partition can make progress (Paxos quorum requirement).
    Minority partition: blocked (can't achieve quorum) → doesn't commit or abort.
    Only one outcome possible. Safe.

3PC vs 2PC vs PAXOS COMMIT COMPARISON:

  Protocol       | Blocks on crash? | Safe under partition? | Message rounds | Complexity
  ───────────────┼──────────────────┼───────────────────────┼────────────────┼───────────
  2PC            | YES              | YES (safe: blocks)    | 2             | Low
  3PC            | NO               | NO (unsafe: diverges) | 3             | Medium
  Paxos Commit   | NO               | YES (quorum)          | 4+ (Paxos)    | High
  Saga           | NO               | YES (compensations)   | N local txns  | Medium-High
  
  Note: 2PC under partition: BLOCKS (doesn't diverge). Blocking is unavailability, not inconsistency.
  3PC under partition: DIVERGES (inconsistency). Inconsistency is much worse than unavailability.
  3PC trades a BAD problem (blocking) for a WORSE problem (inconsistency).
  
  Paxos Commit trades complexity for correctness under all failure modes.
  Saga trades ACID isolation for availability (no distributed locks, eventual consistency).

3PC IN PRODUCTION:

  Rarely used directly. Why:
    1. Network partitions are common in cloud environments.
    2. 3PC is unsafe under partition (partition divergence > blocking).
    3. Higher message count (3 phases vs 2) = higher latency per transaction.
    4. Paxos Commit achieves the non-blocking goal more safely.
    
  Where you might encounter 3PC concepts:
    - NuoDB uses a "3PC-like" commit with quorum (effectively Paxos Commit).
    - PostgreSQL global transactions use a variant.
    - FoundationDB uses a custom multi-phase commit with Paxos.
    
  The CONCEPTS of 3PC (pre-commit phase, termination protocol) appear in:
    - Optimistic locking protocols.
    - Distributed transaction frameworks that add pre-commit state tracking.
    - Understanding trade-offs for interview discussions.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT 3PC (only 2PC):
- Coordinator crash in uncertainty window → indefinite blocking of participants and locks
- Availability: unavailable until coordinator recovers (minutes to hours)
- Manual intervention required if coordinator log is lost

WITH 3PC:
→ Non-blocking under crash-stop: prepared participants can resolve independently
→ Theoretical completion: 3PC shows how to add non-blocking at the cost of partition safety
→ Academic foundation: motivated Paxos Commit (the production-safe version)

---

### 🧠 Mental Model / Analogy

> A relay race where the baton must be passed atomically. 2PC: Runner A must stop at the exact moment of handoff, waiting indefinitely if Coach (coordinator) collapses mid-handoff. 3PC: adds a "pre-handoff signal" — Coach signals "ready for baton transfer" first; if Coach collapses AFTER the signal, both runners know to complete the handoff. But if Coach collapses in a rain shower (network partition) and ONLY Runner A heard the signal while Runner B didn't — they disagree on whether to continue the race.

"Coach signaling pre-handoff" = coordinator sending PreCommit
"Runner A completing handoff without Coach" = participant resolving independently after PreCommit
"Rain shower splitting the team" = network partition causing 3PC divergence

---

### ⚙️ How It Works (Mechanism)

**3PC state machine:**

```
PARTICIPANT STATE MACHINE:

  INITIAL → (receive CANCOMMIT) → UNCERTAIN
    If can commit: reply YES, stay UNCERTAIN.
    If cannot: reply NO, go ABORTED.
  
  UNCERTAIN → (receive PRECOMMIT) → PREPARED
    Write PRECOMMIT to WAL.
    Reply ACK.
    Set timeout for DOCOMMIT.
  
  UNCERTAIN → (timeout waiting for PRECOMMIT) → ABORTED
    No PRECOMMIT received in time → coordinator failed in Phase 1.
    Safe to abort (no one prepared).
  
  PREPARED → (receive DOCOMMIT) → COMMITTED
    Apply transaction. Release locks.
  
  PREPARED → (timeout waiting for DOCOMMIT) → run termination protocol
    Contact all other participants.
    If all prepared: commit.
    If any uncertain: abort.
    (Cannot determine outcome if any participant unknown/crashed.)

TERMINATION PROTOCOL (when coordinator is down):

  Each participant: tries to become temporary coordinator.
  Contacts all others: "What is your state?"
  
  State mapping to decision:
    ANY participant is COMMITTED: → COMMIT (it already committed, must match).
    ANY participant is ABORTED: → ABORT (it already aborted, must match).
    ALL participants are PREPARED: → COMMIT (coordinator would have committed).
    ANY participant is UNCERTAIN (not yet prepared): → ABORT (safe: nothing committed yet).
    
  If a participant is unreachable: wait or elect new coordinator to decide.
  (If unreachable participant MIGHT be committed: cannot safely abort → BLOCKS. Same as 2PC!)
```

---

### 🔄 How It Connects (Mini-Map)

```
Two-Phase Commit (blocks on coordinator failure — uncertainty window)
        │
        ▼
Three-Phase Commit ◄──── (you are here)
(adds pre-commit; non-blocking on crash; unsafe on partition)
        │
        ├── Paxos Commit (non-blocking + partition-safe — production solution)
        └── Saga Pattern (avoids distributed commit entirely — compensating transactions)
```

---

### 💻 Code Example

**3PC state tracking:**

```java
public enum ParticipantState {
    INITIAL,    // Before CANCOMMIT received
    UNCERTAIN,  // Voted YES in Phase 1, waiting for PRECOMMIT
    PREPARED,   // Received PRECOMMIT, ready to commit
    COMMITTED,  // Committed
    ABORTED     // Aborted
}

public class ThreePhaseParticipant {
    
    private volatile ParticipantState state = ParticipantState.INITIAL;
    private final String participantId;
    private final TransactionLog txLog;
    
    // Phase 1: Can we commit?
    public VoteResponse onCanCommit(String txnId, Operation operation) {
        if (canExecute(operation)) {
            state = ParticipantState.UNCERTAIN;
            txLog.write(txnId, state);
            return VoteResponse.YES;
        }
        state = ParticipantState.ABORTED;
        return VoteResponse.NO;
    }
    
    // Phase 2: Coordinator confirmed all voted YES.
    public void onPreCommit(String txnId) {
        state = ParticipantState.PREPARED;
        txLog.write(txnId, state); // Durable: even on crash, we know we were prepared.
        scheduleTimeout(txnId, 30000, this::onPhase3Timeout); // 30s timeout for Phase 3.
    }
    
    // Phase 3: Coordinator says commit.
    public void onDoCommit(String txnId) {
        cancelTimeout(txnId);
        applyTransaction(txnId);
        state = ParticipantState.COMMITTED;
        txLog.write(txnId, state);
    }
    
    // TERMINATION PROTOCOL: coordinator failed, we decide independently.
    private void onPhase3Timeout(String txnId) {
        // Contact all other participants:
        List<ParticipantState> peerStates = queryAllPeers(txnId);
        
        if (peerStates.contains(ParticipantState.COMMITTED)) {
            // Someone committed → we commit too.
            onDoCommit(txnId);
        } else if (peerStates.contains(ParticipantState.ABORTED)) {
            // Someone aborted → we abort.
            state = ParticipantState.ABORTED;
            txLog.write(txnId, state);
        } else if (peerStates.stream().allMatch(s -> s == ParticipantState.PREPARED)) {
            // All prepared → coordinator would have committed → commit.
            onDoCommit(txnId);
        } else if (peerStates.contains(ParticipantState.UNCERTAIN)) {
            // Someone uncertain → coordinator died in Phase 1 → abort.
            state = ParticipantState.ABORTED;
            txLog.write(txnId, state);
        } else {
            // Unknown state (peer crashed) → BLOCKS. Same limitation as 2PC in this case.
            log.error("Cannot determine outcome for txn {}. Waiting for peer recovery.", txnId);
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 3PC is strictly better than 2PC | 3PC improves over 2PC only under crash-stop failures. Under network partitions: 3PC is WORSE than 2PC. 2PC under partition: blocks (unavailability, recoverable). 3PC under partition: diverges (inconsistency, catastrophic). In cloud environments where network partitions are common, 3PC is arguably more dangerous than 2PC. 2PC's blocking is a known, manageable failure; 3PC's partition divergence is harder to detect and recover from |
| 3PC is used in production distributed databases | Very rarely. Most production systems use: (1) 2PC with HA coordinators (mitigates blocking via quick failover); (2) Paxos Commit for truly non-blocking distributed commit; (3) Saga pattern for microservices. The academic contribution of 3PC is demonstrating the trade-off between blocking and partition safety — motivating Paxos Commit, which solves both |
| The pre-commit phase makes 3PC slower than 2PC | The pre-commit phase adds one round-trip per transaction. For cross-region transactions (80ms RTT): 2PC = 2 rounds = ~320ms; 3PC = 3 rounds = ~480ms. For same-datacenter: 2PC = ~4ms; 3PC = ~6ms. Whether the non-blocking benefit justifies the 50% latency increase depends on the failure model. Since 3PC is unsafe under partition anyway, the latency cost without the full correctness benefit makes it unattractive |
| 3PC's termination protocol is always non-blocking | The termination protocol of 3PC still blocks if a participant is UNREACHABLE (crashed). If participant P3 is in an unknown state and also unreachable: the termination protocol cannot safely determine the outcome (P3 might have committed, might not). In this case, 3PC's termination still blocks — waiting for P3 to recover. The non-blocking property only holds when all participants can be contacted (even if some are prepared and some uncertain) |

---

### 🔥 Pitfalls in Production

**3PC partition divergence — why it's not used:**

```
THEORETICAL SCENARIO showing why 3PC is dangerous in practice:

  5-node cluster. Coordinator C. Participants P1, P2, P3, P4.
  Network: 50ms latency between AZ-East and AZ-West.
  
  T=0: C sends PRECOMMIT to P1, P2 (in AZ-East). Both receive. State: PREPARED.
  T=10ms: C sends PRECOMMIT to P3, P4 (in AZ-West). 
  T=20ms: Network partition. AZ-East ↔ AZ-West: disconnected.
  T=30ms: P3, P4 haven't received PRECOMMIT. State: UNCERTAIN.
  
  T=60ms: P1's DOCOMMIT timeout expires. P1 contacts P2 (same AZ): PREPARED.
           P1: "All I can contact are PREPARED. COMMIT." P1, P2 COMMIT. ← WRONG SIDE
           
  T=60ms: P3's PRECOMMIT timeout expires. P3 contacts P4 (same AZ): UNCERTAIN.
           P3: "Someone uncertain. ABORT." P3, P4 ABORT. ← WRONG SIDE
           
  Network heals at T=120ms:
    P1, P2: COMMITTED.
    P3, P4: ABORTED.
    Data diverged. Inconsistency. No automatic resolution.
    
  REAL WORLD: This is why you don't use 3PC in geographically distributed systems.
  
WHAT TO USE INSTEAD:

  Option 1: 2PC with HA coordinator (fast failover).
    Run coordinator on Raft cluster (3 nodes). If coordinator fails: Raft elects new coordinator < 1s.
    Participants block for < 1s (vs minutes for crash recovery of single-node coordinator).
    Partition: 2PC blocks (minority partition) or serves (majority). Always consistent.
    This is what Google Spanner does for global transactions.
    
  Option 2: Paxos Commit.
    Each participant's vote = one Paxos instance. Commit = all instances choose "commit."
    Coordinator failure: other participants can drive Paxos completion.
    Partition: minority partition can't achieve Paxos quorum → blocks (doesn't diverge).
    Non-blocking AND partition-safe.
    
  Option 3: Saga (for microservices).
    No distributed commit. Local transactions + compensating transactions.
    Failure: execute compensation. No locks. No coordinator.
    Trade-off: eventual consistency. Visible intermediate states.
    Best for: multi-step business processes with tolerable compensation.
```

---

### 🔗 Related Keywords

- `Two-Phase Commit` — 2PC: 3PC's predecessor that blocks on coordinator failure
- `Saga Pattern` — preferred production alternative to 3PC (no distributed locking, eventual consistency)
- `Distributed Locking` — 3PC still requires locks during Phase 1 and Phase 2 (until Phase 3)
- `FLP Impossibility` — theoretical limit: no deterministic protocol is both safe and live in async systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Phase1:canCommit + Phase2:preCommit +    │
│              │ Phase3:doCommit. Non-blocking on crash;  │
│              │ diverges under partition. Rarely used.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding distributed commit trade-  │
│              │ offs; interview discussions; foundation  │
│              │ for Paxos Commit understanding           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Production systems with network         │
│              │ partition risk (= all cloud deployments).│
│              │ Use 2PC+HA coordinator or Saga instead.  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Adds a pre-handoff signal — great until │
│              │  the rain splits the relay team."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Two-Phase Commit → Saga Pattern →        │
│              │ Paxos → FLP Impossibility               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** 3PC is non-blocking under crash-stop failures but diverges under network partitions. Paxos Commit is both non-blocking and partition-safe. What is the key mechanism Paxos adds that 3PC lacks? (Hint: think about what happens when two partitions both try to run the termination protocol.) How does the quorum requirement in Paxos prevent both partitions from reaching different conclusions?

**Q2.** Some distributed databases (like FoundationDB) use a custom multi-phase commit protocol that achieves non-blocking and partition safety. They do this by: (1) using Paxos for the commit decision, and (2) storing transaction state in a replicated log (like Raft). How does storing the commit decision in a replicated log solve the 3PC partition problem? Is this effectively "3PC + Raft as coordinator"?
