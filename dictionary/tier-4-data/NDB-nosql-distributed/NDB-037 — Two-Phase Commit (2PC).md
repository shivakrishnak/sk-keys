---
layout: default
title: "Two-Phase Commit (2PC)"
parent: "NoSQL & Distributed Databases"
nav_order: 37
permalink: /nosql/two-phase-commit-2pc/
id: NDB-037
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Distributed Transactions, ACID, CAP Theorem (DB)
used_by: NewSQL, Distributed Transactions, System Design
related: Distributed Transactions, Saga Pattern (DB), ACID
tags:
  - nosql
  - 2pc
  - distributed-transactions
  - deep-dive
---

# NDB-037 — Two-Phase Commit (2PC)

⚡ TL;DR — Two-Phase Commit is the canonical protocol for achieving atomic commitment across multiple independent databases: **Phase 1 (Prepare)** — all participants vote yes/no; **Phase 2 (Commit/Abort)** — coordinator sends the unanimous decision; the critical weakness is the **blocking problem** — if the coordinator crashes after Phase 1, participants hold locks indefinitely waiting for the decision.

| #471            | Category: NoSQL & Distributed Databases           | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Transactions, ACID, CAP Theorem (DB)  |                 |
| **Used by:**    | NewSQL, Distributed Transactions, System Design   |                 |
| **Related:**    | Distributed Transactions, Saga Pattern (DB), ACID |                 |

---

### 🔥 The Problem This Solves

**ATOMIC COMMIT ACROSS MULTIPLE INDEPENDENT DATABASES:**
Without a coordination protocol, committing a transaction across two independent databases requires each database to commit independently. If Database A commits but Database B fails before committing, the data is permanently inconsistent — there's no mechanism to roll back Database A once it has committed. 2PC solves this by introducing a coordinator that drives a two-round protocol ensuring all participants make the same commit/abort decision.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed algorithm that coordinates all processes in a distributed transaction to either commit or abort. It consists of two phases: **Phase 1 (Prepare / Voting Phase)**: The **Coordinator** sends a PREPARE message to all **Participants** (resource managers). Each participant writes its prepared state to a durable log, acquires the necessary locks, and responds YES (ready to commit) or NO (cannot commit / aborting unilaterally). **Phase 2 (Commit / Completion Phase)**: If all participants voted YES, the Coordinator writes a COMMIT decision to its log and sends COMMIT to all participants. If any voted NO (or timed out), the Coordinator sends ROLLBACK to all. Each participant applies the decision and releases locks. **Blocking Problem**: If the Coordinator crashes between Phase 1 (after receiving YES votes) and Phase 2 (before sending the decision), participants are "in doubt" — they have prepared (locked resources) but don't know whether to commit or abort. They must wait until the Coordinator recovers. **3PC (Three-Phase Commit)**: adds a "Pre-Commit" phase to allow non-blocking recovery in some failure scenarios, but adds complexity and latency without solving the problem in all cases (asynchronous networks can still cause blocking).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
2PC is a two-round protocol: round 1, all databases vote yes/no; round 2, everyone applies the coordinator's unanimous decision — but if the coordinator crashes between rounds, everyone waits, locked.

**One analogy:**

> A marriage ceremony: the minister (coordinator) asks both parties (participants): "Do you take...?" (Phase 1). If both say "I do," the minister declares: "You are married" (Phase 2). If either says "I don't," the minister declares it off. But if the minister faints between hearing "I do" from both parties and announcing the decision, the couple is stuck at the altar, unable to leave or proceed — waiting for the minister to wake up.

- "Minister asks" → Coordinator sends PREPARE
- "I do" → Participant votes YES
- "You are married" → Coordinator sends COMMIT
- "Minister faints after both say I do" → Coordinator crashes (blocking problem)
- "Stuck at the altar" → Participants holding locks, in-doubt, waiting

**One insight:**
The fundamental problem with 2PC is that the coordinator holds the key to the universe — after Phase 1, only the coordinator knows if all participants voted YES. Participants can't unilaterally decide because they don't know if another participant voted NO. This is the essence of distributed consensus: you can't decide without communication, and the coordinator is the central communication point — making its crash catastrophic.

---

### 🔩 First Principles Explanation

**2PC STATE MACHINE:**

```
COORDINATOR STATE MACHINE:
  INITIAL → [send PREPARE to all participants]
  WAIT     → [wait for all votes]
             If all YES → write COMMIT to log → COMMIT
             If any NO or timeout → write ABORT to log → ABORT
  COMMIT   → [send COMMIT to all participants] → DONE
  ABORT    → [send ABORT/ROLLBACK to all participants] → DONE

PARTICIPANT STATE MACHINE:
  INITIAL  → [receive PREPARE from coordinator]
  PREPARED → [validate, lock resources, write PREPARED to log]
              Send YES or NO to coordinator
  COMMIT   → [receive COMMIT from coordinator]
              Apply transaction, write COMMITTED to log, release locks
  ABORT    → [receive ABORT from coordinator]
              Discard changes, write ABORTED to log, release locks

IN-DOUBT STATE (blocking problem):
  Participant sent YES, waiting for coordinator decision
  Coordinator has not responded (crashed or network partition)
  Participant: cannot commit (don't know if other voted YES or NO)
               cannot abort (coordinator may have decided COMMIT)
               BLOCKED holding all locks until coordinator recovery

  Duration of blocking: depends on coordinator recovery strategy
  - No recovery: indefinitely blocked
  - TM with durable log: recovers and resumes Phase 2 on restart
  - Typical recovery time: seconds to minutes
```

**2PC TIMING DIAGRAM:**

```
                Coordinator        Participant A      Participant B
                    │                    │                    │
  BEGIN TXNS        │────PREPARE────────>│                    │
                    │────PREPARE────────>│──>                 │
                    │                   │                    │
  PHASE 1           │<───YES (prepared)──│                    │
  (VOTING)          │<───YES (prepared)──────────────────────│
                    │                    │                    │
  ════ COORDINATOR WRITES "COMMIT" TO DURABLE LOG ════════════
                    │                    │                    │
  PHASE 2           │────COMMIT─────────>│                    │
  (COMPLETION)      │────COMMIT─────────>│──>                 │
                    │                   │                    │
                    │<───ACK─────────────│                    │
                    │<───ACK─────────────────────────────────│
                    │                    │                    │
                   DONE               COMMITTED           COMMITTED
```

**THE BLOCKING PROBLEM — ILLUSTRATED:**

```
                Coordinator        Participant A      Participant B
                    │                    │                    │
                    │────PREPARE────────>│                    │
                    │────PREPARE────────>│──>                 │
                    │                   │                    │
                    │<───YES (prepared)──│ [A: LOCKED]        │
                    │<───YES (prepared)──────────────────────│ [B: LOCKED]
                    │                    │                    │
           ████████████████
          COORDINATOR CRASHES
           ████████████████
                    │                    │                    │
                    │                   [A: IN-DOUBT, LOCKED] │
                    │                   [B: IN-DOUBT, LOCKED] │
                    │                    │                    │
                    .  (time passes)     .  (blocked)         .  (blocked)
                    .  (A,B waiting...)  .                    .
                    │                    │                    │
          COORDINATOR RESTARTS           │                    │
          Reads durable log: all YES     │                    │
                    │────COMMIT─────────>│                    │
                    │────COMMIT─────────>│──>                 │
                    │                   │                    │
               RECOVERED             COMMITTED           COMMITTED
               (blocking ended)      (locks released)    (locks released)
```

**3PC — THE NON-BLOCKING ATTEMPT:**

```
3PC adds a "Pre-Commit" phase:

Phase 1 (Prepare): same as 2PC (coordinator sends PREPARE, waits for YES)
Phase 2 (Pre-Commit): coordinator sends PRE-COMMIT to all
  Participants can now infer: "if coordinator crashes, I know everyone voted YES"
  → participants can commit unilaterally if they don't hear from coordinator
Phase 3 (Commit): coordinator sends COMMIT (final confirmation)

3PC Improvement:
  If coordinator crashes AFTER Pre-Commit:
    Participants know all voted YES (pre-commit was sent)
    → Can commit unilaterally after timeout
    Non-blocking!

3PC Still Fails:
  In asynchronous networks (real networks): pre-commit sent but some participants
  didn't receive it (network partition mid-protocol)
  → Some participants know everyone voted YES, others don't
  → Still can have divergence

3PC Verdict: too complex for the benefit; rarely used in production
  Real world: 2PC + durable TM log + fast coordinator recovery is the standard
```

**PRACTICAL 2PC RECOVERY WITH ATOMIKOS:**

```java
// Atomikos TM: durable log, automatic recovery
// on crash: TM restarts, reads transaction log, completes in-doubt transactions

// application.yml (Spring Boot + Atomikos):
spring:
  jta:
    atomikos:
      datasource:
        max-pool-size: 20
      transaction-manager:
        default-jta-timeout: 30s  # timeout for in-doubt transactions

# If TM crashes and restarts:
# 1. TM reads: transactions/transactionID.log (durable log in filesystem)
# 2. For each COMMITTED: re-send COMMIT to any non-ACK'd participants
# 3. For each ABORTED: re-send ABORT to any non-ACK'd participants
# 4. For each PREPARED (coordinator crashed between Phase 1 and decision):
#    TM heuristic: either COMMIT (if coordinator had received all YESes before crash)
#                  or ABORT (if decision was uncertain)
# 5. Participants receive Phase 2 message → apply decision → release locks

# Recovery time: typically seconds (TM log is local, fast to read)
# Blocking duration ≈ TM recovery time (not indefinite with good TM)
```

---

### 🧪 Thought Experiment

**WHAT IF WE SKIP 2PC AND JUST COMMIT SEQUENTIALLY?**

Order service needs to update both OrderDB and InventoryDB atomically. A developer says: "2PC is complex. Let's just: (1) commit to InventoryDB, (2) commit to OrderDB. If (2) fails, undo (1)."

**RACE CONDITION:**
After step 1 commits (inventory decremented), another transaction reads "inventory available = false" for this product. That transaction also decrements inventory. Now inventory is negative. Application crashes before step 2 OR the "undo (1)" fails. No compensation mechanism exists.

**THE "UNDO" PROBLEM:**
"Undo (1)" means sending another write to InventoryDB to reverse the first. But: what if InventoryDB is also down? The undo fails. Now inventory is permanently incorrect. Unlike SQL ROLLBACK (which uses an in-transaction undo log), a committed transaction cannot be "uncommitted" — only a new compensating write can reverse it.

**THE 2PC ANSWER:**
2PC solves this by preparing both before committing either. No other transaction sees committed state until all agree. The prepared state is invisible to outside transactions. This isolation is what makes 2PC different from "commit sequentially": during Phase 1, state is prepared but not committed — no other transaction can observe it.

---

### 🧠 Mental Model / Analogy

> 2PC is like a conductor preparing an orchestra to start. Phase 1: conductor signals each section (strings, brass, woodwinds) — each section readies their instruments and raises their bows (PREPARED). All raised? Phase 2: conductor drops the baton — all play simultaneously (COMMIT). Any section not ready? Conductor signals "stand down" — everyone lowers instruments (ABORT). If the conductor faints between "all bows raised" and "baton drop": the orchestra freezes in position, bows raised, waiting. No music plays until a new conductor takes over.

- "Each section readies" → participant writes PREPARED to log, locks resources
- "Bows raised" → all participants in PREPARED state
- "Baton drop" → Coordinator sends COMMIT (Phase 2)
- "Conductor faints" → Coordinator crashes (blocking problem)
- "Orchestra freezes" → participants IN-DOUBT, holding locks
- "New conductor takes over" → TM recovery (reads log, resumes Phase 2)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** 2PC has two rounds: all databases say "ready" (Phase 1), then all apply the coordinator's "go/stop" decision (Phase 2). It guarantees atomic commit across databases. The weakness: if the coordinator crashes after everyone says "ready" but before sending "go/stop," everyone waits.

**Level 2:** Use 2PC for: same organization's databases that both support XA, short-lived transactions (< 1 second), and where the coordinator (TM) has a durable log and fast recovery. Avoid for: microservices with independent database control, long-running transactions (seconds/minutes = long blocking window), or where participant unavailability is common. Add TM monitoring: alert if transactions are in PREPARED state for > 60 seconds (TM may have crashed).

**Level 3:** XA specification: javax.transaction.xa.XAResource in Java. XADataSource implementations: PGXADataSource (PostgreSQL), MysqlXADataSource (MySQL). Transaction managers: Atomikos (lightweight, Spring Boot autoconfiguration), Bitronix, Narayana (JBoss/WildFly), Java EE container TM (WildFly, Payara). Heuristic decisions: if TM recovery is impossible (log lost), participants may make a heuristic decision (commit or rollback unilaterally) after a timeout. This breaks atomicity but resolves the blocked state — requires manual reconciliation. In-doubt transaction query: `pg_prepared_xacts` view in PostgreSQL (shows transactions in PREPARED state from 2PC).

**Level 4:** 2PC is a consensus protocol, but a weaker one than Paxos or Raft. 2PC achieves atomic commitment but requires all participants to agree (no majority quorum — all or nothing). Paxos/Raft achieve consensus with a majority (can tolerate minority failures). The blocking problem is fundamental to 2PC's "all-or-nothing on all" requirement: if you need every participant to commit, you can't tolerate coordinator failure without blocking. NewSQL databases (CockroachDB, Spanner) use 2PC-variants internally but protect against blocking with Raft-replicated transaction managers — the TM itself is replicated (majority quorum), so "TM crash" means one Raft replica crashes, and the majority continues. This is 2PC at the application boundary + Raft for coordinator durability. The insight: distributed atomic commitment is fundamentally unsolvable without blocking in the presence of failures (FLP impossibility applies). Practical systems mitigate but cannot eliminate this; the choice is between blocking (2PC) and inconsistency (Saga).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ 2PC: DURABLE LOG + RECOVERY                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│ COORDINATOR writes to durable log BEFORE Phase 2:   │
│   Before sending COMMIT: log "T1: COMMIT" to disk    │
│   Before sending ABORT:  log "T1: ABORT" to disk    │
│                                                      │
│ [2PC ← YOU ARE HERE: coordinator crash scenario]     │
│                                                      │
│ Crash after Phase 1 (all YES), before log write:    │
│   TM reads log on recovery: T1 not in log           │
│   → Cannot determine what decision was made          │
│   → TM must choose: COMMIT or ABORT heuristically   │
│   → Or: TM contacts participants (are you prepared?) │
│         If all YES: TM can safely COMMIT             │
│                                                      │
│ Crash after log write, before sending Phase 2:      │
│   TM reads log on recovery: T1 = COMMIT             │
│   → TM re-sends COMMIT to all participants           │
│   → Participants apply COMMIT (idempotent: if already│
│     committed, ignore duplicate COMMIT)              │
│   → Locks released, transaction complete             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**BANK TRANSFER WITH 2PC (ATOMIKOS + SPRING):**

```
User: transfer $100 from Account A (BankDB1) to Account B (BankDB2)
→ Spring @Transactional → Atomikos TM: BEGIN GLOBAL TRANSACTION T1

Phase 1:
→ [2PC ← YOU ARE HERE: TM sends PREPARE]
→ Atomikos → BankDB1 (XA): "PREPARE T1: deduct $100 from A"
   BankDB1: validate (balance >= 100), lock row A, write PREPARED to WAL
   BankDB1 → Atomikos: "YES"
→ Atomikos → BankDB2 (XA): "PREPARE T1: credit $100 to B"
   BankDB2: validate (account exists), lock row B, write PREPARED to WAL
   BankDB2 → Atomikos: "YES"

→ Atomikos: all YES → write "T1: COMMIT" to Atomikos durable log (filesystem)

Phase 2:
→ Atomikos → BankDB1: "COMMIT T1"
   BankDB1: applies deduction, releases lock, ACK
→ Atomikos → BankDB2: "COMMIT T1"
   BankDB2: applies credit, releases lock, ACK

→ @Transactional returns: SUCCESS
→ $100 atomically moved from A to B

If BankDB1 unavailable during Phase 1:
→ BankDB1 → Atomikos: "NO" (or timeout)
→ Atomikos writes "T1: ABORT" to log
→ Atomikos → BankDB2: "ABORT T1" → BankDB2 discards prepared state
→ @Transactional throws: TransactionException
→ No changes committed to either database ✓
```

---

### ⚖️ Comparison Table

| Aspect                | 2PC                        | Saga                           | Raft Consensus                        |
| --------------------- | -------------------------- | ------------------------------ | ------------------------------------- |
| Atomicity             | ACID (all-or-nothing)      | Eventual (compensations)       | Per-quorum (majority decides)         |
| Blocking              | YES (coordinator crash)    | NO                             | NO (majority survives)                |
| Participants required | ALL must respond           | Any service can proceed        | Majority (⌈N/2⌉+1)                    |
| Use case              | Multi-DB ACID transactions | Microservice workflows         | Distributed state machine             |
| Failure tolerance     | Coordinator SPOF           | Service failure → compensation | Minority failure → majority continues |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "2PC blocks forever on coordinator crash"  | With a durable TM log (Atomikos, Narayana), the coordinator recovers, reads its log, and completes Phase 2. Blocking is bounded by TM recovery time, typically seconds to minutes               |
| "2PC is obsolete and should never be used" | 2PC is appropriate and widely used for intra-organizational ACID transactions across multiple databases controlled by the same team. Many enterprise applications use XA/2PC reliably           |
| "3PC solves the blocking problem"          | 3PC solves blocking in synchronous network models. In real asynchronous networks (where messages can be delayed or reordered), 3PC can still result in divergence. Rarely used in practice      |
| "Saga is always safer than 2PC"            | Saga is non-blocking but provides weaker consistency (no isolation). Intermediate states are visible. A failed compensation leaves the system in an inconsistent state unless carefully handled |

---

### 🚨 Failure Modes & Diagnosis

**1. In-Doubt Transaction After TM Log Loss**

**Symptom:** Application restarts after a TM host failure. Some database rows are locked and inaccessible. Error: `Transaction X is in PREPARED state and blocking other operations`. TM log was on ephemeral storage (lost on host termination).

**Root Cause:** TM log lost → on restart, TM has no record of T1's prepared state. Participants (databases) still hold locks for T1 (PREPARED state). TM cannot re-issue the Phase 2 decision without knowing if all participants voted YES.

**Diagnosis:**

```sql
-- PostgreSQL: check for prepared transactions
SELECT * FROM pg_prepared_xacts;
-- Shows: gid (transaction ID), owner, database, prepared (timestamp)

-- Oracle: check DBA_2PC_PENDING
SELECT local_tran_id, state, host FROM dba_2pc_pending;
```

**Fix:**

```sql
-- Force commit (if you know all participants were YES):
COMMIT PREPARED 'transaction-gid-from-pg_prepared_xacts';

-- Force rollback (if uncertain or want to unblock):
ROLLBACK PREPARED 'transaction-gid-from-pg_prepared_xacts';

-- Prevention: TM durable log must be on persistent storage
-- Use Atomikos logs on persistent volume, not ephemeral storage
-- Monitor: alert if pg_prepared_xacts has rows older than 60 seconds
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Transactions, ACID, CAP Theorem (DB)
**Builds On This:** NewSQL, Distributed Transactions
**Related:** Distributed Transactions, Saga Pattern (DB), ACID

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASE 1     │ Coordinator sends PREPARE → all vote YES/NO│
│ PHASE 2     │ All YES → COMMIT; any NO → ROLLBACK        │
│ GUARANTEE   │ ACID atomic commit across all participants  │
│ BLOCKING    │ TM crash after Phase 1 = participants wait  │
│ RECOVERY    │ TM durable log → re-issue Phase 2 on restart│
│ CHECK       │ pg_prepared_xacts (PostgreSQL in-doubt txns)│
│ AVOID       │ Long-running txns; TM on ephemeral storage  │
│ PREFER SAGA │ Microservices; long txns; HA required       │
│ ONE-LINER   │ "Phase 1: vote; Phase 2: unanimous apply;   │
│             │  TM crash between = everyone waits"         │
│ NEXT EXPLORE│ Saga Pattern (DB) → Change Data Capture     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Failure Scenario) A 2PC transaction is in progress: TM has sent PREPARE to Participant A (PostgreSQL) and Participant B (MySQL). Both responded YES. The TM crashes before writing its decision to the log. The TM's storage is ephemeral (lost on restart). An hour later, a DBA notices both databases have locked rows. Walk through: (a) what state are the participants in? (b) how do you diagnose this? (c) how do you resolve it? (d) what are the risks of each resolution path?

**Q2.** (TYPE F — Comparison Depth) A financial services company must transfer funds between two internal PostgreSQL databases in different availability zones, and also notify an external payment ledger API. Compare: (a) 2PC for both database operations + async API call, vs. (b) Saga for all three steps. For each: atomicity guarantee, failure recovery, latency impact, and operational complexity. What is your recommendation and why?
