---
layout: default
title: "Two-Phase Commit (2PC)"
parent: "Distributed Systems"
nav_order: 595
permalink: /distributed-systems/two-phase-commit/
number: "0595"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Transactions, Distributed Systems, ACID, Consensus
used_by: Distributed Locking, Three-Phase Commit, Saga Pattern, XA Transactions
related: Three-Phase Commit, Saga Pattern, Distributed Locking, ACID, Paxos
tags:
  - distributed
  - transactions
  - consistency
  - algorithm
  - deep-dive
---

# 595 — Two-Phase Commit (2PC)

⚡ TL;DR — Two-Phase Commit is the protocol that makes distributed transactions atomic: a coordinator asks all participants "can you commit?" (vote), then either commits if all agree or aborts if any disagree — but a coordinator crash between phases can leave participants blocked indefinitely.

| #595            | Category: Distributed Systems                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Transactions, Distributed Systems, ACID, Consensus         |                 |
| **Used by:**    | Distributed Locking, Three-Phase Commit, Saga Pattern, XA Transactions |                 |
| **Related:**    | Three-Phase Commit, Saga Pattern, Distributed Locking, ACID, Paxos     |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Distributed transaction: `DEBIT bank A` on Server 1, `CREDIT bank B` on Server 2.
Without coordination, Server 1 commits its debit, then Server 2 crashes before
committing its credit. Money has left one account but not arrived in the other.
A rollback on Server 1 would fix this — but how does Server 1 know Server 2 crashed?
Without a protocol, partial transactions corrupt financial data.

**THE INVENTION MOMENT:**
2PC makes EITHER/OR atomicity possible across multiple independent systems:
either BOTH the debit and credit commit, or NEITHER does. This atomic "all or nothing"
guarantee is the XA protocol that powers distributed databases, message queues with
transactional outboxes, and any operation that must span multiple data stores.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed atomicity protocol with two phases: **Phase 1 (Prepare/Voting)**: the coordinator sends `PREPARE` to all participants; each participant writes an "I can commit" record to its WAL and replies `VOTE-YES` (or `VOTE-NO` if it cannot commit). **Phase 2 (Commit/Abort)**: if all participants voted YES, the coordinator writes `COMMIT` to its log and sends `COMMIT` to all participants; if any voted NO, the coordinator sends `ABORT`. Each participant executes the decision and releases locks. **Blocking problem**: if the coordinator crashes after Phase 1 but before Phase 2, participants that voted YES are stuck holding locks indefinitely — they cannot unilaterally abort (the coordinator might have sent COMMIT to someone else) and cannot commit (the coordinator might have aborted). This is 2PC's fundamental limitation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
2PC asks "can everyone do this?" (phase 1), then either does it everywhere or undoes it everywhere (phase 2) — but if the conductor dies between phases, everyone is frozen.

**One analogy:**

> 2PC is like a wedding ceremony conducted by email. The officiant sends "PREPARE: will you consent to this marriage?" Both parties reply YES. Officiant sends "I pronounce you married." Atomic — both parties are married simultaneously or neither is.
> But if the officiant's laptop dies AFTER receiving both YES replies but BEFORE sending the final declaration, neither party knows if they're married. They must wait for the officiant to recover before proceeding. That waiting is 2PC's blocking problem.

**One insight:**
2PC's blocking problem means it's not fault-tolerant — coordinator failure can leave participants "in-doubt" with locks held, causing availability loss. This is why 3PC, Paxos-based commit, and the Saga pattern were invented: they either eliminate the blocking window (3PC — imperfectly) or abandon distributed atomicity in favour of compensating transactions (Saga).

---

### 🔩 First Principles Explanation

**2PC PROTOCOL FLOW:**

```
Coordinator (C)                  Participant 1 (P1)    Participant 2 (P2)

Phase 1 — PREPARE:
C ──PREPARE──────────────────────▶ P1                  P2
                                   P1 acquires locks   P2 acquires locks
                                   P1 writes WAL entry P2 writes WAL entry
C ◀──VOTE-YES────────────────────── P1
C ◀──VOTE-YES──────────────────────────────────────── P2

Phase 2 — COMMIT (because all voted YES):
C writes COMMIT to its own log (CRITICAL: once written, decision is final)
C ──COMMIT───────────────────────▶ P1                  P2
                                   P1 commits          P2 commits
                                   P1 releases locks   P2 releases locks
C ◀──ACK─────────────────────────── P1
C ◀──ACK────────────────────────────────────────────── P2
Transaction complete.

Phase 2 — ABORT (if any voted NO):
C writes ABORT to its own log
C ──ABORT────────────────────────▶ P1                  P2
                                   P1 rollback         P2 rollback
                                   P1 releases locks
```

**THE BLOCKING SCENARIO:**

```
C sends PREPARE → both P1 and P2 vote YES.
C writes COMMIT to log.
C CRASHES before sending COMMIT to P1 or P2.

State:
  C: has COMMIT in log but is down.
  P1: voted YES, holding locks, waiting for COMMIT or ABORT.
  P2: voted YES, holding locks, waiting for COMMIT or ABORT.

P1 and P2 CANNOT UNILATERALLY DECIDE:
  - Cannot ABORT: C might have sent COMMIT to someone already.
  - Cannot COMMIT: C might have decided ABORT.

P1 and P2 are BLOCKED until C recovers.
```

**WHY P1 CANNOT ASK P2:**

```
P1 asks P2: "What did the coordinator tell you?"
P2: "I got nothing yet."

Can P1 safely ABORT?
  NO — C might have sent COMMIT to P2 (P2 just hasn't received it yet
  due to network delay).

Can P1 COMMIT?
  NO — C might have sent ABORT to P2 (P2 just hasn't received it yet).

P1 and P2's decisions MUST match (atomicity). Without knowing C's decision,
neither can proceed. They're both stuck.

This is NOT solved by P1 and P2 communicating — only the coordinator's
decision can unblock them.
```

**XA (eXtended Architecture) — 2PC in Practice:**

```
XA is the standard API for 2PC in Java EE/Jakarta EE.
  Transaction Manager (TM) = 2PC coordinator
  Resource Managers (RM) = participants (DB, MQ)

Java:
  UserTransaction tx = InitialContext.doLookup(
      "java:comp/UserTransaction");
  tx.begin();
  // Operations on DB1 (RM1), DB2 (RM2), JMS queue (RM3)
  db1Connection.executeUpdate("INSERT INTO orders...");
  db2Connection.executeUpdate("UPDATE inventory...");
  jmsProducer.send(queue, message);
  tx.commit(); // TM runs 2PC across all RMs
```

---

### 🧪 Thought Experiment

**2PC LATENCY ANALYSIS:**
A cross-datacenter 2PC. Coordinator in US-East. Participants in US-East and US-West.
US-West round trip latency: 70ms.

Phase 1: 70ms (PREPARE to US-West) + 70ms (VOTE-YES back) = 140ms
Phase 2: 70ms (COMMIT to US-West) + 70ms (ACK back) = 140ms
Total: 280ms MINIMUM for every cross-region distributed transaction.

Compare to a single-DC transaction: ~1ms round trip → 4ms total.
2PC adds 70× latency for cross-region transactions.

This is why microservices typically AVOID 2PC across service boundaries —
the latency cost and blocking risk make it impractical for high-throughput workloads.

**THE SAGA ALTERNATIVE:**
Instead of 2PC, services execute a sequence of local transactions.
If one fails, compensating transactions undo prior work.
No blocking: each service commits independently.
Trade-off: eventual consistency instead of immediate atomicity.
No locks held across service boundaries.
Preferred for most microservices architectures.

---

### 🧠 Mental Model / Analogy

> 2PC is like a jury deliberation with a judge who might disappear.
> Phase 1: judge asks all jurors "ready to vote?" — all jurors lock their verdict.
> Phase 2: judge announces the verdict — all jurors reveal simultaneously.
> If the judge disappears between phases, all jurors are frozen with their
> locked verdicts, unable to proceed. The trial is stuck until the judge returns.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** 2PC runs a two-step vote to decide if everyone commits or nobody commits. One coordinator asks everyone "can you commit?"; then announces the decision. If the coordinator crashes between asking and announcing, everyone is stuck waiting.

**Level 2:** Phase 1: coordinator sends PREPARE; all participants lock their data and vote YES/NO. Phase 2: if all YES → COMMIT; if any NO → ABORT. The critical flaw: coordinator crash after logging COMMIT but before sending it leaves participants blocked indefinitely with held locks.

**Level 3:** 2PC provides atomicity and durability but sacrifices availability during coordinator failure. The in-doubt period (Phase 1 complete, Phase 2 not started) can block for minutes or hours in production. Timeouts are insufficient — a participant cannot safely time out and roll back because the coordinator might have committed. Recovery requires coordinator crash recovery (replaying its WAL) or a distributed TM with HA failover (XA with a highly available transaction manager).

**Level 4:** 2PC's blocking problem is fundamental — it cannot be solved without adding a third phase (3PC) or changing the failure model. 3PC adds a "pre-commit" phase that allows participants to safely commit unilaterally if the coordinator crashes — but 3PC is not safe under network partitions. Paxos-based distributed commit (used in Google Spanner) replaces the coordinator with a Paxos-replicated decision, eliminating single-point coordinator blocking. The Saga pattern avoids 2PC entirely by using compensating transactions — trading immediate atomicity for eventual consistency and eliminating distributed locks.

---

### ⚙️ How It Works (Mechanism)

**Recovery After Coordinator Crash:**

```
Coordinator recovers, reads its WAL:
  If WAL shows COMMIT logged → re-send COMMIT to all participants
  If WAL shows ABORT logged  → re-send ABORT to all participants
  If WAL shows only PREPARE  → coordinator hadn't decided yet → ABORT

Participant recovery (if participant crashed after voting YES):
  Participant reads its own WAL:
    COMMIT in WAL → apply committed state (already done)
    ABORT in WAL → rollback (already done)
    VOTED-YES in WAL but no COMMIT/ABORT → IN-DOUBT: contact coordinator for decision
```

---

### ⚖️ Comparison Table

| Protocol              | Atomicity               | Blocking Risk           | Latency        | Fault Tolerance           |
| --------------------- | ----------------------- | ----------------------- | -------------- | ------------------------- |
| 2PC                   | Atomic                  | Yes (coord failure)     | 2 RTT          | Low (cord SPOF)           |
| 3PC                   | Atomic                  | Reduced (not zero)      | 3 RTT          | Medium (partition unsafe) |
| Saga                  | Eventual (compensation) | None                    | 1 RTT per step | High                      |
| Paxos-based (Spanner) | Atomic                  | None (replicated coord) | 2 RTT + Paxos  | High                      |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                                                                                                    |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2PC is always slow                 | 2PC latency is 2×RTT per round trip — slow for cross-DC, fast for same-DC (2-4ms)                                                                                          |
| 2PC guarantees progress (liveness) | 2PC guarantees atomicity (safety) but NOT liveness — coordinator failure blocks progress                                                                                   |
| 2PC is obsolete                    | 2PC is still widely used for same-datacenter transactions (JDBC XA, JTA), database sharding, and any operation requiring distributed atomicity across multiple RDBMS       |
| Saga is always better than 2PC     | Saga loses immediate atomicity — it's eventually consistent. For financial transactions where a partially-applied saga is visible to other users, this may be unacceptable |

---

### 🚨 Failure Modes & Diagnosis

**In-Doubt Transactions (Blocked Locks)**

Symptom: Long-running transactions with "in-doubt" status; lock wait timeouts;
queries blocked waiting for locks held by stuck prepared transactions.

Diagnosis:

```sql
-- PostgreSQL — find in-doubt prepared transactions:
SELECT gid, prepared, owner, database, transaction
FROM pg_prepared_xacts;
-- gid = transaction ID; prepared = prepare time
-- If age(prepared) > hours: coordinator is down, tx is stuck

-- MySQL — find stuck XA transactions:
XA RECOVER;  -- shows prepared (Phase 1 complete) transactions

-- Manual resolution (DANGER: only if coordinator is confirmed dead):
-- PostgreSQL:
ROLLBACK PREPARED 'transaction_id';  -- or COMMIT PREPARED
-- Only do this after confirming coordinator's decision from its WAL!
```

---

### 🔗 Related Keywords

- `Three-Phase Commit (3PC)` — addresses the blocking problem at the cost of partition safety
- `Saga Pattern` — alternative to 2PC using compensating transactions; no distributed locks
- `Distributed Locking` — 2PC holds locks across system boundaries during the transaction
- `ACID` — 2PC is the mechanism for extending ACID Atomicity to distributed systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  2PC = Phase 1 (Vote) + Phase 2 (Decide)                 │
│  Phase 1: Coordinator → PREPARE → all participants vote  │
│  Phase 2: All YES → COMMIT; Any NO → ABORT               │
│  BLOCKING: coord crash after Phase 1 → participants stuck│
│  LOCKS: held from Phase 1 until commit/abort ACK         │
│  USE: same-DC distributed transactions (XA/JTA)          │
│  AVOID: for cross-DC or microservices (use Saga instead)  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A coordinator sends PREPARE to 3 participants. P1 and P2 vote YES. P3 votes NO. The coordinator logs ABORT and sends ABORT to P1 and P2, but crashes before sending ABORT to P3. P3 is waiting. P3 contacts P1 to ask what happened. P1 received ABORT and rolled back. P3 knows — safe to ABORT. Now: if P1 had received COMMIT instead (before coordinator crash), and P3 contacts P1: P3 learns COMMIT and commits. But what if P1 also hadn't received the message yet? Trace the exact situation where P3 cannot determine the correct decision from peers alone.

**Q2.** You're designing a payment service that must atomically write to a relational database (deduct balance) AND publish a payment event to Kafka. You cannot use 2PC across the DB and Kafka directly (Kafka doesn't support XA). Describe the Outbox Pattern as an alternative to 2PC here: what tables are needed, how does atomicity and ordering work, and what are the consistency guarantees vs. a proper 2PC solution?
