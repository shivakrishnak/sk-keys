---
id: DST-033
title: Two-Phase Commit
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-011, DST-027, DST-029
used_by: DST-042, DST-043
related: DST-011, DST-029, DST-031, DST-035
tags:
  - distributed
  - transactions
  - consistency
  - coordination
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/distributed-systems/two-phase-commit/
---

⚡ TL;DR - Two-Phase Commit (2PC) is a distributed
protocol that coordinates a transaction across multiple
nodes by separating the decision into a prepare phase
(all participants vote can-commit) and a commit phase
(coordinator sends final decision); it provides atomicity
across nodes but blocks indefinitely if the coordinator
fails after the prepare phase, making it unsafe for
long-running or high-availability workloads.

---

### 📋 Entry Metadata

| #033 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Fault Tolerance, Read/Write Quorums, Linearizability | |
| **Used by:** | Distributed Transactions, Saga Pattern | |
| **Related:** | Fault Tolerance, Linearizability, Vector Clocks, Retry Logic | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce order involves two database operations:
(1) deduct inventory from the inventory DB, and (2)
charge the customer's payment. If (1) succeeds and then
(2) fails, you have deducted inventory for an order that
was never paid for. If (2) succeeds and then (1) fails,
you have charged the customer for an item you can no
longer fulfill. Neither outcome is acceptable.

In a single database, ACID transactions solve this.
But inventory and payment live in different systems
(different databases, different services). A single
ACID transaction spanning both systems does not exist
by default. You need a protocol that coordinates
"commit or rollback" across multiple independent
participants.

**THE CORE INSIGHT:**
Two-Phase Commit provides all-or-nothing atomicity across
multiple independent systems. All participants either
commit or all roll back - no partial execution is visible.
The trade-off: a coordinator failure at the wrong moment
can block all participants indefinitely.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed protocol
for achieving atomic commitment across multiple nodes:

**Phase 1 - Prepare (Voting):**
1. Coordinator sends PREPARE to all participants
2. Each participant:
   - Writes the transaction to its local WAL/redo log
   - Verifies it CAN commit (locks acquired, constraints
     satisfied)
   - Responds VOTE-YES (ready to commit) or VOTE-NO
     (cannot commit)

**Phase 2 - Commit/Abort:**
3. If ALL participants voted YES:
   - Coordinator writes COMMIT to its own log
   - Sends COMMIT to all participants
   - Each participant commits and releases locks
4. If ANY participant voted NO (or timed out):
   - Coordinator sends ABORT to all participants
   - Each participant rolls back

**Atomicity guarantee:** every node commits, or none do.

---

### ⏱️ Understand It in 30 Seconds

**The sequence:**
```
Coordinator      Participant A    Participant B
    │                 │                │
    │── PREPARE ──►   │                │
    │◄── YES ─────    │                │
    │── PREPARE ─────────────────►    │
    │◄── YES ─────────────────────    │
    │                 │                │
    │ (all YES: decide COMMIT)         │
    │                 │                │
    │── COMMIT ──►    │                │
    │◄── ACK ─────    │                │
    │── COMMIT ─────────────────►     │
    │◄── ACK ─────────────────────    │
    │                 │                │
    DONE: both committed atomically
```

**The critical failure window:**
```
    │── PREPARE ──► (all vote YES)     │
    │ << COORDINATOR CRASHES HERE >>   │
    │                 │                │
    A: "I voted YES.  B: "I voted YES.
       I can't commit   I can't commit
       or abort until   or abort until
       coordinator      coordinator
       recovers."       recovers."
    → BLOCKED INDEFINITELY
```

---

### 🔩 First Principles Explanation

**THE BLOCKING PROBLEM IN DETAIL:**

After a participant votes YES in Phase 1, it has:
1. Acquired all necessary locks for the transaction
2. Written the transaction to its redo log
3. Committed to committing (cannot unilaterally abort)

The participant is now in an "uncertain" state. It cannot:
- Commit (has not received COMMIT from coordinator)
- Abort (it voted YES; aborting without coordinator
  could leave other participants committed)

This is the "uncertain period" - the participant must
wait for coordinator recovery. In practice, this means
holding locks for the duration of the coordinator outage
(could be minutes or hours).

**THE SAFETY GUARANTEES:**

```
2PC is SAFE (never commits if any participant aborts)
2PC is LIVE only if coordinator always recovers

If coordinator crashes:
  - If before PREPARE: safe to abort (no votes cast)
  - If after PREPARE, before decision logged:
    participants are blocked until recovery
  - If after decision logged: recovery sends the
    logged decision to blocked participants
```

**THE DECISION LOG:**

Before sending COMMIT or ABORT, the coordinator durably
writes the decision to its own stable storage. On
recovery, the coordinator reads its decision log and
re-sends the decision. This ensures the decision is
not lost across coordinator crashes. This is why the
prepare phase forces participants to durably log their
votes - so recovery is always possible.

---

### 🧠 Mental Model / Analogy

> 2PC is a wedding ceremony. The officiant (coordinator)
> asks each party (participants): "Do you take...?"
> Each party says "I do" (VOTE-YES) or refuses (VOTE-NO).
> Only after BOTH say "I do" does the officiant declare
> them married (COMMIT). If the officiant collapses
> right after both said "I do" but before the declaration,
> both parties are stuck: neither married nor free to
> walk away. They must wait for the officiant to recover
> (or for a new officiant who knows what the first one
> decided).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A protocol for making multiple databases commit or
rollback together as one atomic operation. Prepare
phase: everyone says "ready." Commit phase: coordinator
says "go." If anyone says "not ready" or the coordinator
crashes, everyone rolls back.

**Level 2 - When it is used:**
2PC is used in:
- XA transactions (Java JTA, JDBC XA): cross-database
  atomic commits
- Distributed SQL databases (MySQL Cluster, early
  CockroachDB): cross-shard atomic writes
- Message queue + database atomic operations
  (ActiveMQ, RabbitMQ XA connector)

Rarely used in modern microservices: the blocking issue
and tight coupling between services make it impractical
for long-running business transactions.

**Level 3 - Performance implications:**
2PC adds at least 2 network round trips to every
distributed transaction (prepare + commit). With N
participants, it is O(N) network calls per phase.
Under normal conditions (no failures), 2PC adds
~2×RTT latency. The real cost is lock contention:
locks held from PREPARE until COMMIT ACK, spanning
the network round trip. For a 50ms RTT, every row
lock is held for 50ms minimum per transaction.
This severely limits throughput for high-contention
tables.

**Level 4 - Three-Phase Commit (3PC):**
3PC adds a "pre-commit" phase between prepare and
commit, allowing participants to safely abort if
the coordinator crashes after prepare but before
the pre-commit (they know the decision has NOT been
made yet). 3PC is non-blocking in certain failure
models but requires 3 round trips per transaction
and is more complex. It also has its own issues
(network partitions can make participants disagree
on the coordinator's state). Almost no production
systems use 3PC; most use 2PC with recovery mechanisms.

**Level 5 - Modern alternatives:**
Google Spanner uses 2PC internally for cross-shard
transactions, but with Paxos groups at each shard.
The coordinator is itself a Paxos group (not a single
point), eliminating the coordinator SPOF. CockroachDB
uses a similar pattern. For microservices, the Saga
pattern (DST-043) replaces 2PC: instead of atomic
commits, a sequence of local transactions with
compensating actions on failure. Sagas are available
(no blocking) but only achieve eventual consistency
(not atomicity).

---

### ⚙️ Mechanism - 2PC with WAL

```
COORDINATOR:
  1. BEGIN DISTRIBUTED TRANSACTION txn-001
  2. Send PREPARE(txn-001) to all participants
  3. Collect votes:
     - If all YES: log COMMIT(txn-001) to stable storage
                   send COMMIT(txn-001) to all
     - If any NO:  log ABORT(txn-001) to stable storage
                   send ABORT(txn-001) to all
  4. Wait for all ACKs
  5. Log DONE(txn-001)

PARTICIPANT (on PREPARE):
  1. Acquire all locks for txn-001
  2. Write redo log (WAL entry for txn-001)
  3. Write PREPARED(txn-001) to stable storage
  4. Send VOTE-YES to coordinator

PARTICIPANT (on COMMIT/ABORT):
  1. If COMMIT: apply WAL, release locks, ACK
  2. If ABORT:  discard WAL, release locks, ACK

COORDINATOR RECOVERY:
  1. Read decision log
  2. For all txns without DONE:
     - If logged COMMIT: resend COMMIT to all participants
     - If logged ABORT:  resend ABORT to all participants
     - If no decision logged: send ABORT (safe: no one
       committed)
```

---

### 💻 Code Example

**Naive 2PC vs Correct 2PC with Recovery**

```python
# BAD: 2PC without durable decision log
# Coordinator crash = permanent blocking

class FragileCoordinator:
    def commit_distributed(
        self,
        participants: list,
        transaction: dict
    ) -> bool:
        # Phase 1: Prepare
        votes = []
        for p in participants:
            vote = p.prepare(transaction)
            votes.append(vote)

        if all(v == "YES" for v in votes):
            # BUG: COMMIT decision not logged durably.
            # Coordinator crash HERE = participants blocked
            for p in participants:
                p.commit(transaction)  # Some may succeed
            return True
        else:
            for p in participants:
                p.abort(transaction)
            return False
```

```python
# GOOD: 2PC with durable decision log for recovery

import json
from pathlib import Path
from enum import Enum

class TxnState(Enum):
    PREPARING = "PREPARING"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    DONE = "DONE"

class DurableCoordinator:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)

    def _log_decision(
        self,
        txn_id: str,
        state: TxnState
    ) -> None:
        """Durably write decision before sending it."""
        entry = {"txn_id": txn_id, "state": state.value}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            import os
            os.fsync(f.fileno())  # Force to disk

    def commit_distributed(
        self,
        txn_id: str,
        participants: list
    ) -> bool:
        self._log_decision(txn_id, TxnState.PREPARING)

        # Phase 1: Prepare
        votes = {}
        for p in participants:
            try:
                vote = p.prepare(txn_id)
                votes[p.id] = vote
            except Exception:
                votes[p.id] = "NO"

        # Decide and log BEFORE sending
        if all(v == "YES" for v in votes.values()):
            # Log COMMIT durably FIRST
            self._log_decision(txn_id, TxnState.COMMITTED)
            # Now send - safe to crash: recovery will resend
            for p in participants:
                self._send_commit(p, txn_id)
            self._log_decision(txn_id, TxnState.DONE)
            return True
        else:
            # Log ABORT durably FIRST
            self._log_decision(txn_id, TxnState.ABORTED)
            for p in participants:
                self._send_abort(p, txn_id)
            self._log_decision(txn_id, TxnState.DONE)
            return False

    def recover(self, participants: list) -> None:
        """On startup: replay uncommitted decisions."""
        if not self.log_path.exists():
            return
        decisions: dict[str, str] = {}
        with open(self.log_path) as f:
            for line in f:
                entry = json.loads(line)
                decisions[entry["txn_id"]] = entry["state"]
        for txn_id, state in decisions.items():
            if state == TxnState.COMMITTED.value:
                # Resend COMMIT - some participants may need it
                for p in participants:
                    self._send_commit(p, txn_id)
            elif state == TxnState.ABORTED.value:
                for p in participants:
                    self._send_abort(p, txn_id)
            # DONE = no action needed
            # PREPARING = no decision yet = safe to ABORT
```

---

### ⚖️ Comparison Table

| Protocol | Atomic? | Blocking? | Fault Tolerant? | Use Case |
|---|---|---|---|---|
| **2PC** | Yes | Yes (coordinator SPOF) | Partial (recovery needed) | Short transactions, same DC |
| **3PC** | Yes | No (with assumptions) | Better (specific failures) | Rarely used in practice |
| **Paxos/Raft** | Yes | No (majority quorum) | Yes | Consensus, leader election |
| **Saga** | Eventually | No | Yes (compensating txns) | Microservices long txns |
| **Single DB ACID** | Yes | No | Yes (WAL-based) | Single-system transactions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "2PC guarantees no data loss" | 2PC guarantees atomicity (all or nothing), not durability. Durability requires each participant to use WAL/durable storage. If a participant crashes BEFORE writing PREPARED to disk, the transaction is lost from that participant's perspective. |
| "2PC blocking is rare - coordinators rarely crash" | In practice, coordinators are restarted for maintenance, upgrades, and configuration changes. Any planned restart causes the same blocking issue as a crash. 2PC blocking is a real operational concern. |
| "Sagas replace 2PC completely" | Sagas are NOT atomic. They achieve eventual consistency via compensating transactions. If a compensation fails, you have a partial state. 2PC provides stronger guarantees but with higher latency and availability risk. |
| "3PC is always better than 2PC" | 3PC requires 3 network round trips vs 2PC's 2. Under network partitions, 3PC can still block. Its advantages apply only under specific failure models (no partitions). Complexity outweighs benefits in most cases. |

---

### 🚨 Failure Modes & Diagnosis

**Coordinator Crash: Participants Blocked**

**Symptom:** Database connection pool exhaustion.
Locks on tables held for extended periods. Queries
timing out. Monitoring shows: "prepared transaction
count" on databases increasing and not decreasing.

**Diagnosis:**
```sql
-- PostgreSQL: check stuck prepared transactions:
SELECT
    gid,
    state,
    prepared,
    now() - prepared AS age,
    owner,
    database
FROM pg_prepared_xacts
ORDER BY prepared;
-- Any row with age > 5 seconds = likely stuck

-- MySQL: check XA transactions in prepared state:
XA RECOVER;
-- Shows: formatID, gtrid_length, bqual_length, data
-- Any entry = transaction waiting for coordinator

-- Force rollback a stuck prepared transaction (emergency):
-- ONLY if coordinator has definitively crashed and
-- you confirm no COMMIT was logged:
ROLLBACK PREPARED 'transaction-id';
```

**Resolution:**
1. Recover coordinator from backup
2. Coordinator reads decision log and resends decisions
3. If coordinator log is lost and recovery is impossible:
   - Investigate if any participant committed
   - If none: ROLLBACK PREPARED on all participants
   - If some: COMMIT PREPARED on remaining (dangerous!)

---

### 🔗 Related Keywords

**Prerequisites:**
- `Fault Tolerance` (DST-011), `Linearizability` (DST-029)

**Builds On This:**
- Distributed Transactions, Saga Pattern (DST-043)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1    │ PREPARE: all participants vote YES/NO      │
│ PHASE 2    │ COMMIT (all YES) or ABORT (any NO)        │
├────────────┼────────────────────────────────────────────┤
│ ATOMIC     │ Yes: all commit or all abort               │
│ BLOCKING   │ Yes: coordinator crash = all blocked       │
├────────────┼────────────────────────────────────────────┤
│ RECOVERY   │ Coordinator logs decision BEFORE sending   │
│            │ On restart: resend logged decision         │
├────────────┼────────────────────────────────────────────┤
│ POSTGRES   │ pg_prepared_xacts: detect stuck txns       │
│ MYSQL      │ XA RECOVER: show prepared transactions     │
├────────────┼────────────────────────────────────────────┤
│ WHEN       │ Short cross-DB txns, same datacenter       │
│ NOT WHEN   │ Long txns, high availability, microservices│
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "2PC commits everywhere or nowhere -       │
│            │  but coordinator crash blocks everyone."   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

2PC embodies a fundamental tension in distributed systems:
atomicity and availability are in conflict. To guarantee
"all or nothing" across N nodes, at least one node must
be the authority - the coordinator. The coordinator's
failure is the system's failure. This is not a fixable
implementation bug; it is a provable consequence of
the consensus problem. Any distributed commitment
protocol that provides full atomicity must have some
blocking scenario. The engineering challenge is:
(1) make the coordinator highly available (replicated
via Paxos), (2) keep distributed transactions short,
or (3) relax atomicity (Saga pattern) for business
processes that can tolerate partial execution.

---

### 💡 The Surprising Truth

Google Spanner's "externally consistent transactions"
use 2PC internally, but with a critical difference:
the coordinator is a Paxos group (3-5 nodes with
automatic leader election), not a single server.
If the coordinator "crashes," the Paxos group elects
a new leader and continues. This effectively eliminates
the 2PC blocking problem - at the cost of 2PC running
on top of Paxos, which itself requires 2+ round trips.
Spanner's cross-shard transactions typically take 10-14ms
globally, of which ~7ms is the TrueTime commit-wait.
The lesson: 2PC's blocking problem is not inherent to
the protocol - it is a consequence of having a single-
point coordinator. Replicate the coordinator via consensus
and the problem disappears, at the cost of additional
latency.

---

### ✅ Mastery Checklist

1. [TRACE] Draw the sequence diagram for a successful
   2PC across 3 participants. Then draw the failure
   diagram when the coordinator crashes after receiving
   all YES votes but before sending COMMIT.
2. [IMPLEMENT] Write a DurableCoordinator with decision
   logging. Verify recovery correctly resends COMMIT
   after a simulated coordinator restart.
3. [DIAGNOSE] Given `pg_prepared_xacts` showing a
   transaction prepared 15 minutes ago, determine the
   correct recovery action (and when NOT to ROLLBACK
   PREPARED).
4. [COMPARE] Design the same cross-service order+payment
   transaction using 2PC and using the Saga pattern.
   Identify what guarantees each provides and what
   each sacrifices.
5. [EXPLAIN] Why 3PC does not fully solve 2PC's blocking
   problem under network partitions, and why production
   systems rarely use 3PC.
