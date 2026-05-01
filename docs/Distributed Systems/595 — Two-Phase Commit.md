---
layout: default
title: "Two-Phase Commit"
parent: "Distributed Systems"
nav_order: 595
permalink: /distributed-systems/two-phase-commit/
number: "595"
category: Distributed Systems
difficulty: ★★★
depends_on: "Distributed Locking, Failure Modes"
used_by: "XA Transactions, MySQL Distributed, JTA, MSDTC"
tags: #advanced, #distributed, #transactions, #consistency, #atomicity
---

# 595 — Two-Phase Commit

`#advanced` `#distributed` `#transactions` `#consistency` `#atomicity`

⚡ TL;DR — **Two-Phase Commit (2PC)** is the classic atomic commit protocol ensuring all participants in a distributed transaction either ALL commit or ALL abort — at the cost of blocking when the coordinator crashes after Phase 1.

| #595            | Category: Distributed Systems                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Locking, Failure Modes             |                 |
| **Used by:**    | XA Transactions, MySQL Distributed, JTA, MSDTC |                 |

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed atomic commit protocol ensuring ACID atomicity across multiple database shards or heterogeneous data stores. **Phase 1 (Prepare/Vote)**: the coordinator sends Prepare to all participants; each participant durably logs the transaction and responds Vote-Commit (ready to commit) or Vote-Abort (cannot commit, e.g., constraint violation); if any participant aborts: coordinator decides global abort. **Phase 2 (Commit/Abort)**: coordinator durably logs its decision and sends Commit or Abort to all participants; each participant applies the decision and releases locks. Safety: all participants reach the same outcome (all commit or all abort). The critical failure scenario: coordinator crashes after all participants vote Commit but before sending the Commit message. Participants are **blocked** — they hold locks and cannot proceed without the coordinator's decision. This is the **blocking problem** of 2PC: availability depends on coordinator recovery. The **uncertainty window** is between participants' Prepare ACK and the coordinator's Commit/Abort message. Solutions: **3PC (Three-Phase Commit)** — adds a pre-commit phase to eliminate uncertainty (at the cost of complexity); **Paxos Commit** (Gray & Lamport) — runs Paxos on the commit decision (non-blocking, requires 2f+1 coordinators); **Saga pattern** — replaces 2PC with compensating transactions for long-running workflows.

---

### 🟢 Simple Definition (Easy)

Two-Phase Commit: "are you ready to commit? OK, now commit." A coordinator asks all participants: "Can you commit this transaction?" All say yes → coordinator says "commit." Any says no → coordinator says "abort." It's like a wedding: the officiant (coordinator) asks both people "Do you?" before saying "You may kiss." If either says no → no wedding. Problem: if the officiant collapses after both say "yes" but before saying "you're married" → both people are frozen waiting. That's 2PC's blocking problem.

---

### 🔵 Simple Definition (Elaborated)

Where 2PC is needed: transferring money from Bank A to Bank B (two separate databases). You need BOTH the debit AND the credit to succeed or fail atomically. Without 2PC: debit Bank A (success) → credit Bank B (failure) → money disappears. With 2PC: coordinator prepares BOTH (holds locks), then commits both or aborts both. The problem: if the coordinator dies between "prepare" and "commit" — Bank A and Bank B are frozen holding locks, waiting for a decision that never comes. 2PC is the foundation of XA transactions (JTA, MySQL distributed transactions) and is widely used despite its blocking limitation.

---

### 🔩 First Principles Explanation

**2PC phases, failure scenarios, and XA protocol:**

```
2PC PROTOCOL (nominal case):

  PARTICIPANTS: P1 (Bank A shard), P2 (Bank B shard).
  COORDINATOR: C (Transaction Manager).
  TRANSACTION: TRANSFER $100 from AccountA (on P1) to AccountB (on P2).

  ─── PHASE 1: PREPARE (VOTING) ───────────────────────────────────────

  C → P1: PREPARE(txn_id=T1, operations=[DEBIT AccountA $100])
  C → P2: PREPARE(txn_id=T1, operations=[CREDIT AccountB $100])

  P1 actions:
    1. Check: can I execute DEBIT AccountA $100?
       - AccountA balance = $200. $200 ≥ $100. OK.
       - Integrity constraints: none violated.
    2. Write to WAL: "I'm prepared to commit T1. Will execute DEBIT AccountA $100."
    3. Acquire LOCKS on AccountA record (hold until Phase 2).
    4. DO NOT APPLY the change yet (just staged).
    5. Reply: VOTE-COMMIT (I'm prepared, I promise to commit if asked).

  P2 actions (similar):
    1. Check: can I CREDIT AccountB $100? (Simple credit — always possible.)
    2. Write to WAL: "Prepared for T1, will execute CREDIT AccountB $100."
    3. Acquire LOCKS on AccountB.
    4. Reply: VOTE-COMMIT.

  C receives both VOTE-COMMITs:
    Decision: COMMIT (all voted yes).
    C: writes COMMIT decision to its WAL (CRITICAL: durable before Phase 2).

  ─── PHASE 2: COMMIT ────────────────────────────────────────────────

  C → P1: COMMIT(txn_id=T1)
  C → P2: COMMIT(txn_id=T1)

  P1: applies DEBIT (AccountA: $200 → $100). Releases locks. Writes COMMITTED to WAL.
  P2: applies CREDIT (AccountB: +$100). Releases locks. Writes COMMITTED to WAL.

  P1 → C: ACK.
  P2 → C: ACK.

  C: cleans up T1 state. Transaction complete.

FAILURE SCENARIOS:

  SCENARIO A: P2 votes ABORT in Phase 1.
    C → P1: PREPARE. P1: VOTE-COMMIT.
    C → P2: PREPARE. P2: AccountB is closed → VOTE-ABORT.
    C: receives VOTE-ABORT from P2 → global decision = ABORT.
    C → P1: ABORT. P1: releases locks, rolls back staged changes.
    C → P2: ABORT. P2: releases locks.
    Result: no money moved. Consistent. CORRECT.

  SCENARIO B: Coordinator C crashes after COMMIT decision but before sending COMMIT.
    [COMMIT decision written to C's WAL]
    C crashes.
    P1 and P2: waiting for Phase 2 message. BLOCKED.
    P1 and P2: holding locks on AccountA and AccountB.

    Duration: until C recovers (could be minutes, hours, or manual intervention).

    Consequence: AccountA and AccountB records LOCKED. No other transaction can modify them.
    In practice: SELECT (read) may succeed (read locks). INSERT/UPDATE on same rows: BLOCKED.
    Other transactions waiting on AccountA or AccountB locks: also blocked.
    Cascading lock contention.

    C recovers: reads WAL → "I had decided COMMIT for T1." → resends COMMIT to P1, P2.
    P1, P2: apply commit. Locks released. Transaction complete.

    This is the BLOCKING PROBLEM: 2PC is BLOCKING during coordinator failure.

  SCENARIO C: P1 crashes after voting COMMIT but before receiving Phase 2.
    P1 crashes. C: detects P1 unavailable (timeout).
    C: has already committed decision (decision written to WAL).
    C: continues sending COMMIT to P2. P2 commits.
    C: P1 recovery: reads WAL → "I prepared T1 but never received Commit/Abort decision."
       P1 CANNOT make independent decision (it might have been ABORT).
       P1 must QUERY the coordinator: "What was the decision for T1?"
       C: "COMMIT." P1: applies commit. Done.

  SCENARIO D: Both C and P1 crash simultaneously. P2 has voted COMMIT.
    P2: prepared. Holding locks. Waiting for Phase 2.
    C and P1 both down. P2 cannot query C (C is down).
    P2: INDEFINITELY BLOCKED. Cannot commit or abort independently.

    Manual intervention required:
      DBA checks C's WAL on recovered C. If COMMIT decision found: tell P2 to commit.
      If no decision in WAL: decision was ABORT (or never reached). Tell P2 to abort.

    This is the theoretical worst case of 2PC: requires human intervention.

  SCENARIO E: Network partitions (C can't reach P1 to send COMMIT).
    C: decided COMMIT. Sends COMMIT to P1 (timeout). Sends COMMIT to P2. P2 commits.
    C: retries COMMIT to P1 (exponential backoff until P1 reachable).
    P1: receives COMMIT eventually. Applies. Done.

    P1 in the meantime: holding locks. Lock timeout may trigger manual investigation.

XA PROTOCOL (distributed transactions in JDBC):

  XA = standard interface for 2PC across heterogeneous data stores.
  Defined by The Open Group. Implemented by: MySQL, PostgreSQL, Oracle, IBM MQ, etc.

  Components:
    XAResource: each database/queue that participates in the transaction.
    Transaction Manager (TM): the coordinator (JBoss, WebLogic, Atomikos, Narayana).
    Application Server: starts transaction, enlists XAResources.

  XA Operations:
    xa_start(xid): start transaction branch on this resource.
    xa_prepare(xid): Phase 1 — prepare to commit (returns XA_OK or XA_RDONLY or error).
    xa_commit(xid): Phase 2 — commit (after all xa_prepare returned XA_OK).
    xa_rollback(xid): Phase 2 — rollback (after any xa_prepare failure or global abort).
    xa_recover(): list all in-doubt (prepared but not committed/aborted) transactions.

  XA transaction flow in JDBC:
    XAConnection xaConnA = mysqlDataSourceA.getXAConnection();
    XAConnection xaConnB = postgresDataSourceB.getXAConnection();

    UserTransaction utx = ... ; // JTA Transaction Manager
    utx.begin(); // TM starts global transaction.

    // Enlist both XAResources with TM:
    txManager.enlistResource(xaConnA.getXAResource());
    txManager.enlistResource(xaConnB.getXAResource());

    // Business logic on both connections:
    xaConnA.getConnection().prepareStatement("UPDATE accounts SET balance=balance-100 WHERE id=1").execute();
    xaConnB.getConnection().prepareStatement("UPDATE accounts SET balance=balance+100 WHERE id=2").execute();

    utx.commit(); // TM: Phase 1 (xa_prepare on both), Phase 2 (xa_commit on both).

  XA_RDONLY optimization:
    If P2 only reads (no writes): xa_prepare returns XA_RDONLY.
    TM: P2 doesn't need Phase 2 (no write to commit). Only send Phase 2 to P1.

  In-doubt transactions:
    TM crashes after Phase 1, before Phase 2.
    Database: "I prepared T1 but never got commit/abort."
    On TM recovery: xa_recover() lists in-doubt transactions.
    TM: replays Phase 2 from persistent transaction log.
    Manual: if TM log lost → DBA manually commits/rolls back via xa_commit(xid, onePhase=false).

BLOCKING PROBLEM SOLUTIONS:

  1. THREE-PHASE COMMIT (3PC):
     Adds "PRE-COMMIT" phase between Prepare and Commit.
     Pre-commit: coordinator sends PRE-COMMIT before final COMMIT.
     If coordinator crashes after PRE-COMMIT: participants know the decision was COMMIT.
     (They can proceed with commit independently — no blocking.)

     Phase 1: Prepare → Vote-Commit/Abort.
     Phase 2: Pre-Commit (coordinator sends; participants ACK).
     Phase 3: Commit → ACK.

     If coordinator crashes after Phase 2: participants proceed with COMMIT (non-blocking!).
     If coordinator crashes in Phase 1 uncertainty: participants time out → ABORT.

     Problem: 3 phases = more messages, more latency.
     Also: 3PC is not safe under network partitions (participants may diverge on pre-commit).
     Used rarely in practice. Mostly theoretical.

  2. PAXOS COMMIT (Gray & Lamport, 2004):
     Run Paxos on the commit decision.
     N acceptors replace single coordinator.
     Non-blocking: if f acceptors fail, remaining 2f+1 can still decide.
     More complex to implement. Spanner uses a variant.

  3. SAGA PATTERN:
     Replace 2PC with a series of local transactions + compensating transactions.
     No distributed locking. No blocking.
     Trade-off: only eventual consistency. Compensations add complexity.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT 2PC:

- Distributed transactions are best-effort: partial failures leave inconsistent state
- Money transfer: debit succeeds, credit fails → money disappears
- Inventory: reservation committed, payment failed → inventory incorrect

WITH 2PC:
→ Atomic distributed transactions: all-or-nothing across multiple data stores
→ ACID guarantees: cross-shard consistency maintained
→ Standard protocol: XA standardises 2PC across heterogeneous systems (MySQL + PostgreSQL + MQ)

---

### 🧠 Mental Model / Analogy

> A wedding ceremony. Phase 1 (Prepare): officiant asks both partners "Do you take...?" and awaits both "I do." If either says "I don't" or collapses → no wedding (global abort). Phase 2 (Commit): officiant says "By the power vested in me, I now pronounce you..." The blocking problem: if the officiant faints between "I do" and "I now pronounce" — both partners are frozen mid-ceremony, holding hands, unable to leave or proceed. The ceremony cannot continue or be abandoned without the officiant recovering and finishing.

"Officiant" = 2PC coordinator
"Both partners saying I do" = participants voting VOTE-COMMIT
"Officiant pronouncing marriage" = coordinator sending COMMIT in Phase 2
"Officiant fainting mid-ceremony, partners frozen" = blocking problem when coordinator crashes

---

### ⚙️ How It Works (Mechanism)

**MySQL XA distributed transaction:**

```sql
-- TWO DATABASES: db1 (Bank A shard), db2 (Bank B shard).
-- Coordinator: application code acting as TM.

-- SESSION 1: Connected to db1.
XA START 'txn-transfer-001';
UPDATE accounts SET balance = balance - 100 WHERE id = 1001;  -- Debit $100
XA END 'txn-transfer-001';
XA PREPARE 'txn-transfer-001';  -- Phase 1: write to WAL, hold locks, ready to commit.
-- Returns: Query OK (if prepared successfully).

-- SESSION 2: Connected to db2.
XA START 'txn-transfer-001';  -- Same XID across both databases.
UPDATE accounts SET balance = balance + 100 WHERE id = 2001;  -- Credit $100
XA END 'txn-transfer-001';
XA PREPARE 'txn-transfer-001';  -- Phase 1 on db2.

-- COORDINATOR LOGIC (application):
-- Both prepared successfully → Phase 2: COMMIT.
-- If either failed → Phase 2: ROLLBACK.

-- Phase 2 (if both XA PREPARE succeeded):
-- SESSION 1:
XA COMMIT 'txn-transfer-001';  -- Apply debit on db1. Release locks.
-- SESSION 2:
XA COMMIT 'txn-transfer-001';  -- Apply credit on db2. Release locks.

-- If coordinator crashes: find in-doubt transactions:
XA RECOVER;  -- Returns list of prepared-but-not-committed XA transactions.
-- Result: 'txn-transfer-001' shown as in-doubt.
-- DBA decision: XA COMMIT 'txn-transfer-001'; or XA ROLLBACK 'txn-transfer-001';
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed Transactions (atomicity across multiple nodes/databases)
        │
        ▼
Two-Phase Commit ◄──── (you are here)
(Phase 1: prepare/vote; Phase 2: commit/abort; blocking on coordinator failure)
        │
        ├── Three-Phase Commit (non-blocking variant — adds pre-commit phase)
        ├── Saga Pattern (alternative: no 2PC, uses compensating transactions)
        └── Distributed Locking (2PC acquires locks in Phase 1, releases in Phase 2)
```

---

### 💻 Code Example

**2PC coordinator implementation:**

```java
public class TwoPhaseCommitCoordinator {

    private final List<XAParticipant> participants;
    private final TransactionLog txLog; // Durable transaction log

    public void executeDistributedTransaction(String txnId, List<Operation> operations) {
        // PHASE 1: PREPARE
        List<XAParticipant> preparedParticipants = new ArrayList<>();
        boolean allPrepared = true;

        for (int i = 0; i < participants.size(); i++) {
            XAParticipant p = participants.get(i);
            Operation op = operations.get(i);
            try {
                VoteResult vote = p.prepare(txnId, op);
                if (vote == VoteResult.COMMIT) {
                    preparedParticipants.add(p);
                } else {
                    allPrepared = false; // One participant voted abort.
                    break;
                }
            } catch (ParticipantException e) {
                allPrepared = false; // Participant unavailable → abort.
                break;
            }
        }

        if (allPrepared) {
            // WRITE COMMIT DECISION TO DURABLE LOG BEFORE PHASE 2.
            // This is the "commit point" — if coordinator crashes here,
            // it will re-read log and re-send COMMIT on recovery.
            txLog.write(txnId, Decision.COMMIT); // FSYNC — must be durable.

            // PHASE 2a: COMMIT
            for (XAParticipant p : preparedParticipants) {
                commitWithRetry(p, txnId); // Retry forever until participant ACKs.
            }
        } else {
            // WRITE ABORT DECISION TO LOG.
            txLog.write(txnId, Decision.ABORT); // Durable.

            // PHASE 2b: ABORT (only prepared participants need abort message)
            for (XAParticipant p : preparedParticipants) {
                abortWithRetry(p, txnId);
            }
        }

        txLog.cleanup(txnId); // Transaction complete.
    }

    // Retry Phase 2 indefinitely (participants block until they receive decision):
    private void commitWithRetry(XAParticipant p, String txnId) {
        int attempt = 0;
        while (true) {
            try {
                p.commit(txnId);
                return;
            } catch (Exception e) {
                attempt++;
                long delay = Math.min(1000L * (1L << attempt), 30000L); // Exponential backoff, max 30s
                log.warn("Commit to {} failed (attempt {}). Retrying in {}ms.", p.getId(), attempt, delay);
                Thread.sleep(delay);
            }
        }
    }

    // Recovery: called on coordinator restart.
    public void recover() {
        List<String> inDoubtTxns = txLog.getInDoubt();
        for (String txnId : inDoubtTxns) {
            Decision decision = txLog.getDecision(txnId);
            if (decision == Decision.COMMIT) {
                for (XAParticipant p : participants) commitWithRetry(p, txnId);
            } else if (decision == Decision.ABORT) {
                for (XAParticipant p : participants) abortWithRetry(p, txnId);
            }
            // If no decision in log: coordinator crashed before Phase 1 complete → ABORT.
            else {
                txLog.write(txnId, Decision.ABORT);
                for (XAParticipant p : participants) abortWithRetry(p, txnId);
            }
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2PC provides full ACID guarantees across distributed systems | 2PC provides atomicity (all commit or all abort) and, combined with locking, isolation. But it cannot provide the full ACID properties that a single-node database can. Specifically: durability is only as strong as each participant's durability guarantee; consistency is enforced by each participant's constraints, not by 2PC itself. Also: 2PC does NOT guarantee availability (it blocks during coordinator failure). It trades availability for atomicity |
| 2PC is always needed for cross-service transactions          | 2PC is one solution. Alternatives: (1) Saga pattern — use compensating transactions (no distributed locking, eventual consistency); (2) design to avoid cross-service transactions — keep data that must be transactional in the same service; (3) outbox pattern + event-driven — accept eventual consistency. In microservices: 2PC across service boundaries is generally discouraged because it introduces tight coupling and blocking                          |
| The "Two-Phase" in 2PC refers to Prepare and Commit          | Correct for the nominal protocol, but the "two phases" refers specifically to the voting phase (Phase 1) and the execution phase (Phase 2). The "prepare" in Phase 1 is the critical step — it's a PROMISE by the participant to commit (or abort) whatever the coordinator decides. Once a participant sends VOTE-COMMIT, it can NEVER unilaterally abort — it must wait for the coordinator's decision (this is the source of the blocking problem)               |
| 3PC solves all of 2PC's problems                             | 3PC eliminates blocking under node failures but is still unsafe under network partitions. If the network partitions between Phase 2 and Phase 3, a pre-committed node in one partition may proceed with commit while nodes in the other partition time out and abort — achieving exactly the split-brain commit inconsistency that 2PC prevents. This is why 3PC is not used in practice; Paxos Commit or Saga are the preferred alternatives                       |

---

### 🔥 Pitfalls in Production

**XA transaction coordinator crash leaving in-doubt transactions:**

```
PRODUCTION INCIDENT:
  JTA transaction manager (Atomikos) crashed during peak load.
  In-doubt XA transactions: 47 transactions prepared on MySQL + PostgreSQL but not committed.
  All 47 transactions: holding row locks.
  Downstream: queue of 10,000 requests blocked on locked rows. Customer-facing timeout.
  Manual recovery: DBA investigated each XA transaction, decided commit or rollback.
  Recovery time: 45 minutes. Revenue impact: significant.

ROOT CAUSE: Atomikos transaction log stored on local disk. Server disk failure = log lost.
  Lost log → coordinator cannot recover → participants block indefinitely.

BAD: JTA Transaction Manager with local disk-only log:
  # atomikos-config.properties:
  com.atomikos.icatch.log_base_dir=/var/log/atomikos  # Local disk only — single point of failure.
  com.atomikos.icatch.enable_logging=true
  # If this disk fails: coordinator cannot recover in-doubt transactions.
  # All participants block until manual DBA intervention.

FIX 1: Replicated transaction log:
  # Use shared storage for TM log:
  com.atomikos.icatch.log_base_dir=/mnt/nfs/atomikos-logs  # NFS/EFS shared storage.
  # Or: use a database as TM log (Narayana can use JDBC for object store).

FIX 2: Avoid 2PC for most operations — use Saga pattern:
  // Instead of XA transactions across services:
  // Use Saga: local transactions + compensating transactions.

  @SagaOrchestrator
  public class TransferSaga {
      @SagaStep
      public void debitAccount(TransferCommand cmd) {
          accountService.debit(cmd.getSourceAccount(), cmd.getAmount()); // Local transaction
      }

      @Compensate("debitAccount")
      public void reverseDebit(TransferCommand cmd) {
          accountService.credit(cmd.getSourceAccount(), cmd.getAmount()); // Compensate on failure
      }

      @SagaStep(after = "debitAccount")
      public void creditAccount(TransferCommand cmd) {
          accountService.credit(cmd.getTargetAccount(), cmd.getAmount()); // Local transaction
      }

      @Compensate("creditAccount")
      public void reverseCredit(TransferCommand cmd) {
          accountService.debit(cmd.getTargetAccount(), cmd.getAmount()); // Compensate
      }
  }
  // No distributed locks. No blocking. Eventual consistency (in-flight saga is not isolated).
  // Visible intermediate states: after debit but before credit — compensating transaction handles failure.
```

---

### 🔗 Related Keywords

- `Three-Phase Commit` — non-blocking extension of 2PC (adds pre-commit to eliminate uncertainty)
- `Saga Pattern` — alternative to 2PC using compensating transactions (eventually consistent)
- `Distributed Locking` — 2PC acquires locks on all participants during Phase 1
- `Failure Modes` — coordinator crash in 2PC causes blocking (timeout failure leads to indefinite block)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Phase 1: prepare+vote; Phase 2:          │
│              │ commit/abort. Atomic across N databases. │
│              │ BLOCKS if coordinator crashes mid-txn.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ ACID transactions across 2 databases     │
│              │ (XA); short transactions; coordinator HA │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-running transactions (lock duration)│
│              │ Microservices (tight coupling + blocking)│
│              │ High availability required during TM fail│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wedding: both I-dos before pronouncing — │
│              │  officiant fainting freezes the ceremony."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Three-Phase Commit → Saga Pattern →      │
│              │ Outbox Pattern → Distributed Locking     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservices architecture has Order Service (MySQL) and Inventory Service (PostgreSQL). An order creation must atomically: (1) create the order record, and (2) reserve inventory. The team proposes using XA 2PC. What are the risks? What alternative (non-2PC) approach maintains atomicity and avoids distributed locking? Sketch the approach using the Outbox pattern or Saga.

**Q2.** 2PC requires the coordinator to write its COMMIT decision to durable storage BEFORE sending the COMMIT message to participants. Why is this step critical? What happens if the coordinator sends COMMIT to P1 first, P1 commits, then coordinator crashes before writing to log AND before sending to P2? Can P2 ever learn the correct decision? How does this illustrate the relationship between durability of the coordinator log and overall 2PC correctness?
