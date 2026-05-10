---
id: DST-028
title: "Two-Phase Commit (2PC)"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-014, DST-022
used_by: DST-017
related: DST-017, DST-016, DST-014, DST-047
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
nav_order: 44
permalink: /distributed-systems/two-phase-commit/
---

# DST-015 - Two-Phase Commit (2PC)

⚡ TL;DR - Two-Phase Commit is the foundational protocol for distributed atomic commitment: a coordinator asks all participants "can you commit?" (Phase 1/Prepare), then issues the global decision (Phase 2/Commit or Abort) — but a coordinator crash between phases leaves participants indefinitely blocked, which is 2PC's fundamental and unsolvable flaw.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-014, DST-022                   |     |
| **Used by:**    | DST-017                            |     |
| **Related:**    | DST-017, DST-016, DST-014, DST-047 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank transfer: debit from Account A (on Database 1) and credit to Account B (on Database 2). Without 2PC: you debit A, then credit B. If the system crashes between the two operations: A is debited but B is never credited. Money vanishes. Alternatively: you credit B, then debit A. If crash between: money is created from nothing. How do you make two separate database operations appear as a single atomic unit?

**THE BREAKING POINT:**
Single-node transactions have ACID atomicity guaranteed by the local database. But when a transaction spans multiple databases/services: no single node can guarantee atomicity for all. Each database can only see its own state. Without a coordination protocol, you can't achieve "all commit OR all abort" across distributed nodes.

**THE INVENTION MOMENT:**
Gray's "Notes on Data Base Operating Systems" (1978) formalized 2PC as the solution to distributed atomic commitment. The protocol's elegance: Phase 1 collects votes ("can everyone commit?") — all must say YES. Phase 2 broadcasts the decision — all follow it. The voting phase ensures durability before the decision; the decision phase ensures agreement. Every distributed transaction system since then is built on 2PC or is explicitly designed around its limitations.

**EVOLUTION:**
1978: Gray's 2PC. 1982: XA standard (distributed transaction interface). 1996: CORBA OTS (2PC in object systems). 2000s: JTA/JTS (Java Transaction API). 2015+: Saga pattern popularized as 2PC alternative in microservices. 2022: Most cloud-native systems avoid 2PC (use Sagas or single-service atomic operations). CockroachDB uses 2PC internally within its Raft-based transaction protocol.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed atomic commitment protocol ensuring that a transaction either commits on all participants or aborts on all, maintaining atomicity across multiple independent nodes. **Phase 1 (Prepare/Voting):** the coordinator sends `Prepare` to all participants. Each participant locks its resources, writes the transaction to its log, and responds with `YES` (can commit) or `NO` (cannot commit). If any participant responds `NO` or times out: coordinator decides Abort. **Phase 2 (Commit/Abort):** coordinator sends `Commit` (if all voted YES) or `Abort` (if any voted NO or timed out). Participants apply the decision and release locks. **Fundamental limitation (blocking problem):** if the coordinator crashes after Phase 1 but before Phase 2: participants who voted YES are stuck — they have locked their resources and cannot unilaterally commit or abort without knowing if all other participants also voted YES. This blocking is indefinite: participants must wait for the coordinator to recover. This is the core reason 2PC is called "blocking."

---

### ⏱️ Understand It in 30 Seconds

**One line:** 2PC is "everyone votes YES to prepare, then follow the coordinator's final decision" — atomic across distributed nodes, but permanently blocked if the coordinator crashes between phases.

> 2PC is like a wedding ceremony. The officiant (coordinator) asks each person "do you take this partner?" (Phase 1). Both must say "I do" (YES vote). Then the officiant declares "I now pronounce you married" (Phase 2 commit). If the officiant collapses between the vows and the declaration: neither person knows if they're married — they're stuck waiting for the officiant to recover.

**One insight:** 2PC's blocking problem is mathematically unavoidable for protocols requiring a single coordinator decision. This is provably non-solvable (the "Two-Phase Commit is non-blocking" problem has no deterministic solution in async networks). Three-Phase Commit and Paxos-based commit mitigate but don't fully eliminate blocking.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Unanimity:** all participants must vote YES for the transaction to commit. A single NO vote causes abort.
2. **Durability before decision:** participants persist their vote to disk BEFORE responding. If coordinator crashes: participant can survive crash and still know its vote.
3. **Decision irreversibility:** once a participant commits (receives and applies the Commit decision), it cannot be rolled back. This is the key ACID durability point.
4. **Coordinator as single point of truth:** only the coordinator knows the complete vote tally. Participants cannot coordinate with each other to determine the outcome — they are only connected to the coordinator.

**DERIVED DESIGN:**
The blocking problem arises from invariant 4: participants must wait for the coordinator because only the coordinator has the full picture. If participants could contact each other, they could determine the outcome without the coordinator — but this would require O(n²) communication.

**THE TRADE-OFFS:**
**Gain:** Distributed atomicity. ACID guarantees across multiple databases. Exactly-once semantics for distributed transactions.
**Cost:** Blocking on coordinator failure (locks held indefinitely). 2 network round-trips minimum (prepare + commit). Coordinator SPOF. Reduced throughput vs. local transactions (coordination overhead).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Distributed atomic commitment fundamentally requires consensus — at least one round-trip to collect votes, one to broadcast the decision. 2 rounds is the minimum.
**Accidental:** The blocking problem is the essential unsolvable limitation. Three-Phase Commit mitigates it via a non-blocking pre-commit phase (at the cost of more rounds). Paxos-based commit (used in CockroachDB) uses Raft consensus internally to make the commit decision fault-tolerant.

---

### 🧪 Thought Experiment

**SETUP:** Bank transfer: debit Account A (DB1, Paris), credit Account B (DB2, London). Coordinator C in Frankfurt.

**NORMAL PATH:**

- C → DB1: `PREPARE tx-1 (debit A €100)` → DB1: locks A, writes to WAL, replies `YES`
- C → DB2: `PREPARE tx-1 (credit B €100)` → DB2: locks B, writes to WAL, replies `YES`
- C: all YES → writes `COMMIT tx-1` to its log → sends `COMMIT` to DB1, DB2
- DB1: applies debit, releases lock, replies `ACK`
- DB2: applies credit, releases lock, replies `ACK`
- C: transaction complete

**COORDINATOR CRASH BETWEEN PHASES:**

- C → DB1: `PREPARE tx-1` → DB1: `YES` (A is LOCKED)
- C → DB2: `PREPARE tx-1` → DB2: `YES` (B is LOCKED)
- C CRASHES (disk failure) → never sends Phase 2
- DB1: "I voted YES. Did others? What's the decision?" → UNKNOWN. A remains LOCKED.
- DB2: "I voted YES. Did others? What's the decision?" → UNKNOWN. B remains LOCKED.
- DB1 and DB2 cannot release the locks without knowing the decision. No other node knows the complete vote.
- Both DBs BLOCKED until C recovers (hours? days? never?).

**THE INSIGHT:** The coordinator crash is the single worst-case for 2PC. Participants have given up their ability to abort (they voted YES), but haven't received permission to commit. This is the blocking window — and it's the reason 2PC is considered problematic for microservices and high-availability systems.

---

### 🧠 Mental Model / Analogy

> 2PC is like a conference call where everyone must agree on a decision, but only the meeting chair knows everyone's vote. Each participant whispers their vote to the chair privately (Phase 1). The chair then announces the final decision to everyone (Phase 2). If the chair loses internet connection between the whispers and the announcement: every participant is frozen — they've privately committed to a position but can't act on it without the chair's announcement.

**Mapping:**

- **Meeting chair** → coordinator
- **Participants whispering votes** → Phase 1 (Prepare)
- **Chair announces decision** → Phase 2 (Commit/Abort)
- **Chair losing connection** → coordinator crash
- **Participants frozen** → blocking problem (locks held indefinitely)

Where this analogy breaks down: in a real meeting, participants could eventually call each other to determine the outcome. In 2PC, participants are deliberately kept isolated (they only know their own vote, not others') to reduce message complexity — making the coordinator indispensable.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
2PC is how distributed systems make multiple database writes happen atomically. Step 1: the coordinator asks all databases "are you ready to commit?" Step 2: if everyone says yes, coordinator says "commit." If anyone says no: "abort." The flaw: if the coordinator crashes between steps 1 and 2, everyone is stuck waiting.

**Level 2 - How to use it (junior developer):**
In Spring with JTA (Java Transaction API): annotate your service with `@Transactional`. If you configure multiple XA datasources: Spring/Atomikos handles 2PC transparently. On coordinator (Spring app) crash after writing to one DB but before the second: JTA recovery kicks in on restart and resolves the in-doubt transactions. Caveat: JTA 2PC adds significant latency. For microservices: prefer Saga pattern (DST-016).

**Level 3 - How it works (mid-level engineer):**
XA protocol (ISO/IEC 11404 standard for 2PC): `xa_prepare(xid)` → `xa_commit(xid)` or `xa_rollback(xid)`. Each database driver implements XA. The application server (coordinator) manages the XID (transaction ID) lifecycle. On crash recovery: the coordinator reads its transaction log, finds in-doubt transactions (in PREPARED state), and resends the commit/abort decision. In-doubt transactions remain locked until coordinator recovery — this is why XA transactions must have bounded coordinator recovery time.

**Level 4 - Why it was designed this way (senior/staff):**
2PC is the minimal protocol for distributed atomic commitment in a fully asynchronous network — proven by Fischer, Lynch, Paterson (FLP, 1985). Any protocol that provides atomic commitment in an asynchronous network must have at least one blocking state (a state where a participant cannot make progress without hearing from another node). 2PC's designers accepted this limitation by minimizing the blocking window: blocking only occurs if the coordinator fails AFTER phase 1 completes but BEFORE phase 2 starts. In practice: this window is small (milliseconds) if the coordinator is healthy. The real problem is coordinator failure DURING this window — rare in normal operation, catastrophic in failure scenarios. Modern alternatives (Saga, Paxos-commit) either accept weaker guarantees (Saga: no atomicity, only eventual consistency) or add fault-tolerant coordinator redundancy (Paxos-commit: coordinator failure is recovered by Raft consensus).

**Expert Thinking Cues:**

- "Our JTA transaction is stuck in PREPARED state" → Coordinator crashed or lost its transaction log. JTA recovery is trying to resolve it. Check coordinator's transaction log: `atomikos-transactions.log` or `narayana objectstore`. Manually roll back if coordinator can't recover.
- "Our microservices use 2PC between services — is that a problem?" → Yes. Network calls between microservices are orders of magnitude less reliable than local DB calls. 2PC between services means any service crash during the prepare window blocks the entire chain.
- "Our XA transactions are much slower than local transactions" → Typical 2PC overhead: 2× network RTTs + coordinator logging. For 3-participant transactions across DCs: 100ms RTT each. 2PC adds 200ms minimum. Alternatives: denormalize data, accept eventual consistency, or use Saga.
- "CockroachDB is '2PC-based' but doesn't have blocking" → CockroachDB uses 2PC over Raft. The coordinator role is itself backed by a Raft group — coordinator failure is recovered by Raft election. The coordinator is not a SPOF because it's replicated. This is "Paxos-based commit" — 2PC with a fault-tolerant coordinator.

---

### ⚙️ How It Works (Mechanism)

**2PC state machine:**

```
Coordinator states:
  INIT → PREPARING → COMMITTING/ABORTING → DONE

Participant states:
  WORKING → PREPARED → COMMITTED/ABORTED
         ↑              ↑
         VOTE_NO → ABORTED (shortcut)

Phase 1 (Prepare):
  C: for each P in participants:
       send Prepare(xid)
       await YES/NO (with timeout)
  if all YES: decision = COMMIT
  if any NO or timeout: decision = ABORT
  C: log decision to disk (CRITICAL: must persist)

Phase 2 (Commit/Abort):
  C: for each P in participants:
       send Commit(xid) or Abort(xid)
       await ACK
  C: marks transaction DONE in log

Participant Phase 1 handling:
  recv Prepare(xid):
    if can commit (resources available, constraints ok):
      write PREPARED to local log (CRITICAL: must fsync)
      lock resources
      send YES
    else:
      send NO (can release immediately)

Participant Phase 2 handling:
  recv Commit(xid): apply changes, release locks, send ACK
  recv Abort(xid): roll back, release locks, send ACK
```

**Blocking window (the fatal flaw):**

```
Timeline showing blocking window:

T=0: C sends Prepare to all
T=1: All participants: fsync PREPARED, reply YES
T=2: C: received all YES votes
     ← BLOCKING WINDOW START →
T=3: C crashes here (WORST CASE)
     All participants: LOCKED, waiting for decision
     No other node knows all voted YES
     Participants CANNOT unilaterally decide
     ← BLOCKING WINDOW (indefinite until C recovers)
T=4: C recovers, reads its log
T=5: If C logged decision before crash: resends it
     If C didn't log: protocol undefined
          (application-specific: usually re-query participants)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (bank transfer across two databases):**

```
Client  Coordinator(C)  DB1(Paris)   DB2(London)
  │         │               │             │
  │─xfer──▶│               │             │
  │         │─Prepare(x)───▶│             │
  │         │─Prepare(x)───────────────▶│
  │         │◀─YES──────────│             │
  │         │               │◀────YES─────│
  │         │ all YES: log COMMIT
  │         │─Commit(x)─────▶│            │
  │         │─Commit(x)────────────────▶│
  │         │◀─ACK──────────│            │
  │         │               │◀────ACK────│
  │◀─done──│ ← YOU ARE HERE: atomically committed
```

**COORDINATOR CRASH FAILURE PATH:**
All participants vote YES. Coordinator crashes before sending Phase 2. Participants hold locks indefinitely. System stalls until coordinator recovers (minutes to hours). This is the "blocking" state that makes 2PC unsuitable for high-availability systems.

**WHAT CHANGES AT SCALE:**
With 100 participants: coordinator sends 100 Prepare messages, awaits 100 YES votes (serialized or parallel). If parallel: Phase 1 latency = slowest participant. Phase 2: 100 Commit messages. Any ONE participant unavailable = abort (all-or-nothing). High fan-out makes 2PC increasingly fragile at scale: N participants = N single points of failure during the prepare window.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
2PC locks resources throughout its duration. Long-running 2PC transactions across geo-distributed databases: locks held for seconds (network RTT × 2). During this window: any other transaction touching the same rows is blocked (serializable isolation). High contention on hot rows (bank accounts) with geo-distributed 2PC can cause lock convoy effects — queue of transactions waiting for the 2PC lock to release.

---

### 💻 Code Example

**BAD - Manual distributed transaction without 2PC (inconsistent on failure):**

```java
// Not using 2PC: debit one DB then credit another
// If crash between: money disappears
public class UnsafeTransfer {
    private DataSource parisDb;
    private DataSource londonDb;

    public void transfer(long amount, long fromId, long toId) {
        // DANGER: no transaction coordinator
        // If crash after debit but before credit:
        // fromId loses amount, toId never gains it
        try (Connection c1 = parisDb.getConnection()) {
            c1.setAutoCommit(false);
            debit(c1, fromId, amount);
            c1.commit();  // Paris committed
        }
        // ← CRASH HERE: Paris debited, London not credited
        try (Connection c2 = londonDb.getConnection()) {
            c2.setAutoCommit(false);
            credit(c2, toId, amount);
            c2.commit();  // London committed (maybe)
        }
        // No atomicity: each DB commits independently
    }
}
```

**GOOD - 2PC via JTA with XA datasources:**

```java
import javax.transaction.UserTransaction;
import javax.sql.XADataSource;

@Service
public class SafeTransfer {
    @Inject
    private UserTransaction userTransaction; // JTA coordinator
    @Inject
    @Qualifier("parisXA")
    private XADataSource parisXaDs; // Paris XA datasource
    @Inject
    @Qualifier("londonXA")
    private XADataSource londonXaDs; // London XA datasource

    public void transfer(long amount, long fromId, long toId)
        throws Exception {
        // JTA manages 2PC automatically:
        // Phase 1: calls xa_prepare on both XADataSources
        // Phase 2: calls xa_commit on both (if all prepared)
        userTransaction.begin();
        try {
            // Both operations participate in same XA transaction
            try (Connection c1 = parisXaDs.getXAConnection()
                    .getConnection()) {
                debit(c1, fromId, amount);
                // c1 is enlisted in JTA transaction
                // xa_prepare will be called on this connection
            }
            try (Connection c2 = londonXaDs.getXAConnection()
                    .getConnection()) {
                credit(c2, toId, amount);
                // c2 is enlisted in same JTA transaction
            }
            userTransaction.commit();
            // JTA: calls xa_prepare on both, then xa_commit
            // If coordinator (JVM) crashes after xa_prepare:
            // JTA recovery (Atomikos/Narayana) replays on restart
        } catch (Exception e) {
            userTransaction.rollback();
            // JTA: calls xa_rollback on all participants
            throw e;
        }
    }
}
```

**Configuring JTA recovery (Atomikos):**

```yaml
# application.yml - Atomikos JTA transaction manager
spring:
  jta:
    atomikos:
      transactions:
        log-base-dir: /var/atomikos/logs
        # CRITICAL: recovery log must persist across restarts
        # Without this: in-doubt transactions unresolvable
        enable-logging: true
      datasource:
        xa-properties:
          # XA connection pool settings
          maxPoolSize: 10
          loginTimeout: 5
```

**How to test / verify correctness:**

```bash
# Test 2PC recovery:
# 1. Start a transaction, prepare both DBs
# 2. Kill the application (coordinator) AFTER prepare
# 3. Restart application
# 4. Verify Atomikos recovery log replays commit:
ls /var/atomikos/logs/
# Should show recovery files
# After restart: transaction should either commit or abort

# Check for stuck XA transactions in MySQL:
mysql -e "XA RECOVER\G"
# If any rows: these transactions are in PREPARED state
# (coordinator hasn't sent Phase 2)
# If stuck for > coordinator restart time: investigate coordinator

# PostgreSQL:
psql -c "SELECT * FROM pg_prepared_xacts;"
# Same: non-empty = coordinator crashed in blocking window
```

---

### ⚖️ Comparison Table

| Protocol     | Blocking on coord. failure | Rounds   | Node count      | Use case                           |
| :----------- | :------------------------- | :------- | :-------------- | :--------------------------------- |
| 2PC          | Yes (indefinite)           | 2 RTTs   | N participants  | RDBMS distributed transactions     |
| 3PC          | No (with sync network)     | 3 RTTs   | N participants  | Avoided in practice                |
| Paxos-Commit | No (Paxos handles coord.)  | 2-4 RTTs | 2f+1 per coord. | CockroachDB, Spanner               |
| Saga         | N/A (no global atomicity)  | Async    | N services      | Microservices eventual consistency |
| XA           | Yes (same as 2PC)          | 2 RTTs   | N XA resources  | Java enterprise apps               |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                                                                                  |
| :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "2PC guarantees no data loss on coordinator failure" | 2PC guarantees atomicity: all commit or all abort. But if the coordinator crashes BETWEEN phases: the outcome is UNKNOWN until the coordinator recovers. The data is not lost — but the transaction is in limbo. Indefinite blocking, not data loss.                                                     |
| "Saga is a drop-in replacement for 2PC"              | Saga provides eventual consistency, not atomicity. With Saga: partial completion is possible — some services commit, others compensate. Saga is appropriate for business-level compensation (cancel order); not for financial transactions requiring strict atomicity (bank transfer).                   |
| "2PC is only used in enterprise Java"                | 2PC is used internally in many distributed databases: CockroachDB, Google Spanner, Amazon Aurora. The difference: they wrap 2PC with Raft-based fault-tolerant coordinators, eliminating the blocking problem at the cost of complexity.                                                                 |
| "Timeout-based abort solves the blocking problem"    | If a participant times out waiting for Phase 2 and aborts: it can release its lock. BUT: if the coordinator actually sent a Commit to other participants (who committed): you now have partial commit (some committed, one aborted). This violates atomicity. Timeout-based abort can break consistency. |
| "2PC latency is just 2 network round-trips"          | Minimum: 2 RTTs (both phases). Realistic: 2 RTTs + coordinator logging (fsync) + participant logging (fsync) + potential retries. For geo-distributed participants (100ms RTT per hop): 2PC adds 200ms minimum, potentially much more with retries and coordinator logging.                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Coordinator Crash Causing Indefinite Lock (Blocking)**

**Symptom:** A critical table in the database has rows locked indefinitely. All writes to those rows are blocked. The application log shows the JTA coordinator crashed 2 hours ago. The `pg_prepared_xacts` table shows pending XA transactions from 2 hours ago.
**Root Cause:** JTA coordinator crashed during the blocking window (after Prepare, before Commit). PostgreSQL (XA participant) has rows locked in PREPARED state. No other node can resolve the transaction without coordinator recovery.
**Diagnostic:**

```bash
# PostgreSQL: find in-doubt prepared transactions:
psql -c "SELECT gid, owner, database, prepared, transaction
         FROM pg_prepared_xacts ORDER BY prepared;"
# gid = XA transaction ID (e.g., "Atomikos:1234567")
# prepared = when it was prepared (how long it's been stuck)

# MySQL: find in-doubt XA transactions:
mysql -e "XA RECOVER\G"
# If output contains rows: XA transactions in PREPARED state

# How long has it been stuck?
# If > coordinator restart time: coordinator log is lost or corrupt
# Manual resolution may be required:
psql -c "COMMIT PREPARED 'transaction_id';"
# OR:
psql -c "ROLLBACK PREPARED 'transaction_id';"
# DANGER: manual resolution — must know the correct outcome
# from application-layer audit logs before choosing
```

**Fix:**
BAD: Manually rolling back all stuck transactions without checking application-layer intent.
GOOD: (1) Restore coordinator (Atomikos/Narayana) from backup and let it replay recovery. (2) Check application audit log to determine intended outcome. (3) Manually commit or abort based on audit log evidence.
**Prevention:** Coordinator's transaction log must be on durable storage (RAID, network storage). Multiple coordinator replicas (active-passive with shared transaction log). Set XA transaction timeouts: auto-rollback if not resolved within N minutes.

**Failure Mode 2: Heuristic Completion Causing Data Inconsistency**

**Symptom:** Database administrator manually resolves a stuck 2PC transaction by "heuristic commit" — assuming the transaction should commit based on the current state. Later: the application coordinator recovers and discovers the transaction was actually ABORTED (one participant voted NO before the crash). Now one participant has committed and another has aborted. Data inconsistency.
**Root Cause:** "Heuristic decision" in XA — databases can be manually forced to commit or abort a stuck prepared transaction (bypassing coordinator authority). If the manual decision contradicts the coordinator's intended outcome: inconsistency.
**Diagnostic:**

```bash
# PostgreSQL: check heuristic decisions:
psql -c "SELECT * FROM pg_prepared_xacts
         WHERE gid LIKE '%heuristic%';"
# Or check DB logs for "heuristic abort/commit" messages:
grep -i "heuristic" /var/log/postgresql/postgresql.log | tail -20

# Atomikos: check for heuristic exceptions in application logs:
grep "HeuristicMixedException\|HeuristicRollbackException" \
  /var/log/app/application.log | tail -20
```

**Fix:**
BAD: Making heuristic decisions without consulting application-layer audit logs.
GOOD: Never make heuristic decisions unless coordinator log is confirmed permanently lost. If forced to: use application-layer audit (event log) to determine intended outcome. After heuristic decision: immediately audit all affected records for consistency.
**Prevention:** Avoid heuristic decisions entirely by: (1) durable coordinator transaction log storage (NFS/SAN), (2) coordinator HA (active-passive pair sharing transaction log), (3) short XA transaction timeouts (minutes, not hours).

**Failure Mode 3: Security - 2PC Coordinator Compromise Allows Transaction Injection**

**Symptom:** An attacker with access to the 2PC coordinator injects a `COMMIT` for a fraudulent transaction. The coordinator sends `COMMIT tx-999 (transfer €1M from victim to attacker)` to all participants. Both participants commit — they each received valid COMMIT messages with the correct XID. Transaction succeeds. No participant can reject a valid COMMIT from the coordinator.
**Root Cause:** 2PC participants are designed to follow the coordinator's Phase 2 decision unconditionally. Once a participant has voted YES in Phase 1: it MUST commit if the coordinator says COMMIT. Participants have no authority to reject a valid Phase 2 decision. Compromising the coordinator = compromising all participants.
**Diagnostic:**

```bash
# Audit coordinator's transaction decisions:
# Atomikos: check transaction log for unexpected XIDs:
grep "commit\|abort" /var/atomikos/logs/*.log | \
  grep -v "known-transaction-ids" | tail -50
# Any unexpected XIDs in commit log = potential injection

# PostgreSQL: audit XA commits:
psql -c "SELECT * FROM pg_stat_activity
         WHERE state = 'idle in transaction'
         AND query_start < now() - interval '1 minute';"
# Unusual activity patterns may indicate injection
```

**Fix:**
BAD: Coordinator with network-accessible management interface (no auth).
GOOD: (1) Coordinator access restricted to application servers only (firewall). (2) Transaction log integrity: sign coordinator log entries with HMAC. (3) Database-level row-level security: transactions can only modify rows the application user owns (no coordinator bypass). (4) Anomaly detection: alert on unusually large transactions.
**Prevention:** Treat the 2PC coordinator as a privileged component. Same security controls as a database: network segmentation, audit logging, anomaly detection on transaction sizes and patterns.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-014 - Failure Modes (2PC handles crash-recovery failures — understanding the failure model is required)
- DST-022 - CAP Theorem (2PC sacrifices availability during coordinator failure — CAP context is essential)

**Builds On This (learn these next):**

- DST-017 - Three-Phase Commit (3PC directly extends 2PC to reduce blocking)

**Alternatives / Comparisons:**

- DST-016 - Two-Phase Commit (practical implementation focus vs. this entry's algorithmic focus)
- DST-017 - Three-Phase Commit (3PC's improvement over 2PC's blocking)
- DST-047 - Paxos (Paxos-commit uses consensus to eliminate coordinator SPOF)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Coordinator asks "prepare?"    |
|                  | then sends global commit/abort |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Distributed atomic commitment  |
|                  | across multiple databases      |
+------------------+--------------------------------+
| KEY INSIGHT      | If coordinator crashes between |
|                  | phases: participants block     |
|                  | indefinitely (unsolvable)      |
+------------------+--------------------------------+
| USE WHEN         | Must have strict atomicity     |
|                  | across multiple RDBMS (legacy) |
+------------------+--------------------------------+
| AVOID WHEN       | High-availability microservices|
|                  | — use Saga instead             |
+------------------+--------------------------------+
| TRADE-OFF        | Distributed atomicity vs.      |
|                  | coordinator SPOF + latency     |
+------------------+--------------------------------+
| ONE-LINER        | All vote YES + coord. commits  |
|                  | = atomic; coord. crash = block |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-017 Three-Phase Commit,    |
|                  | DST-016 2PC practical impl     |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. 2PC = Phase 1 (prepare, collect YES votes) + Phase 2 (broadcast commit/abort). Unanimous YES required for commit.
2. Coordinator crash between phases → participants blocked indefinitely (locks held). This is the blocking problem — mathematically unavoidable in async networks.
3. Modern alternatives: Saga (eventual consistency, no coordinator), Paxos-commit (Raft-backed coordinator eliminates SPOF). XA is 2PC for relational databases.

**Interview one-liner:**
"Two-Phase Commit achieves distributed atomicity by having a coordinator collect YES/NO votes from all participants (Phase 1/Prepare), then broadcasting the commit or abort decision (Phase 2). All participants must vote YES for commit. The fatal flaw: if the coordinator crashes after Phase 1 but before Phase 2, participants are blocked indefinitely — they've locked their resources and cannot commit or abort without the coordinator's decision. This blocking problem is mathematically unavoidable, which is why Saga patterns (eventual consistency) and Paxos-commit (replicated coordinator) have emerged as alternatives."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Consensus always requires a leader phase and a commit phase — you can't do it in one round in an asynchronous network. Any protocol that needs "everyone agrees before we proceed" will have at least two rounds: one to collect intent, one to broadcast decision. The blocking problem emerges because the decision-broadcaster (coordinator) is a single actor. To eliminate blocking: replicate the coordinator (Paxos-commit) or accept weaker guarantees (Saga). The engineering lesson: single-coordinator designs are simpler to implement but fragile to failure; replicated-coordinator designs are complex but fault-tolerant. Choose based on the required availability guarantees.

**Where else this pattern appears:**

- **Git pull request reviews (informal 2PC):** A PR requires all required reviewers to approve (Phase 1: "can you approve?"). When all approve: the merge button is enabled — but the author must still click "Merge" (Phase 2: coordinator issues final commit). If the repo goes offline between all approvals and the merge click: the PR sits in PREPARED state (all approvals, waiting for final merge). This informal 2PC is why some teams configure auto-merge (eliminating the coordinator's Phase 2 delay) and others require manual merge (keeping human coordinator control).
- **Airline baggage check-in (operational 2PC):** Checking in a passenger with connecting flights: each leg's aircraft must "prepare" capacity (baggage weight allocation). The coordinator (check-in agent) asks each aircraft's manifest "can you take 32kg of luggage on leg 1 and 28kg on leg 2?" (Phase 1). Only if both say yes: the agent issues boarding passes (Phase 2 commit). If the agent's system crashes after capacity is allocated but before boarding passes are issued: passenger is stuck — capacity is reserved on planes but no boarding pass exists. Airlines resolve this with database recovery (coordinator log) — same as 2PC recovery.
- **Human decision-making in committees (social 2PC):** A board vote on a resolution. The chair asks each member "do you vote YES?" in sequence (Phase 1). If all say YES: chair announces "the resolution passes" (Phase 2). If the chair suffers a medical emergency between collecting votes and announcing: the vote result is in limbo — each member said YES privately, but the result is never officially declared. Organizations solve this with documented voting records (coordinator log) and deputy chairs (coordinator redundancy) — the same solutions as database 2PC.

---

### 💡 The Surprising Truth

Two-Phase Commit was formalized in 1978, but the distributed transaction systems built on it — Java's JTA, Microsoft's MSDTC, IBM's CICS — remained dominant in enterprise computing for over 30 years. The microservices revolution of the 2010s didn't replace 2PC because of better algorithms (3PC had been known since 1983); it replaced 2PC because the DEPLOYMENT MODEL changed. In monolithic applications: all services share a single 2PC coordinator (the application server) on the same machine — coordinator crash is rare and fast to recover (JVM restart). In microservices: every service is a separate coordinator — a coordinator failure is not a single-machine restart but a service outage in a potentially distributed environment. The Saga pattern's popularity is not about algorithmic superiority over 2PC; it's about operational pragmatics in an environment where coordinators are unreliable services. The surprising truth: 2PC is not inherently broken — it works well when the coordinator is reliable (enterprise app servers had > 99.99% uptime). It fails in microservices not because the algorithm changed but because the reliability assumption about the coordinator was no longer valid.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A Spring Boot application using JTA (Atomikos) is running normally. Suddenly, a PostgreSQL participant becomes unreachable during Phase 1. The coordinator waits 30 seconds (XA timeout), then aborts the transaction. This correctly maintains atomicity. But the PostgreSQL DBA reports: "we're seeing locks held on table T for 30 seconds during every transaction — even successful ones." What is happening, and is this related to the coordinator timeout? If so, why does a SUCCESSFUL transaction also hold locks for 30 seconds?
_Hint:_ Phase 1 locks resources before sending YES. If any participant is slow to respond to Prepare (not down, just slow): the coordinator waits for ALL participants' responses before sending Phase 2. During this wait: ALL participants have locks held. A slow-to-respond participant causes ALL others to hold locks until the slowest one responds or times out. Check: is there a slow XA participant causing a lock convoy? Which service's Phase 1 response is slowest? Use XA prepare timing metrics.

**Q2 (C - Design Trade-off):** CockroachDB implements 2PC internally but claims to have no coordinator SPOF. It uses "parallel commits" as an optimization: the coordinator can return success to the client as soon as a quorum of participants have committed their writes (via Raft), without waiting for all participants to confirm. This appears to violate 2PC's unanimity requirement. How does CockroachDB reconcile this optimization with 2PC correctness? What guarantees does the Raft replication provide that allow this "early return"?
_Hint:_ Standard 2PC: coordinator must receive ACK from ALL participants before marking complete. CockroachDB parallel commits: the coordinator writes its decision (COMMITTED) to the transaction record (via Raft). Any participant that committed its writes AND sees the COMMITTED transaction record can finalize. Participants that haven't finished yet will check the transaction record on their next access and self-finalize. The "early return" works because: the transaction record (coordinator decision) is itself Raft-replicated — durable and discoverable by participants without coordinator involvement. The coordinator is NOT a SPOF because its decision is replicated.

**Q3 (E - First Principles):** The FLP impossibility theorem implies that in an asynchronous network, no deterministic protocol can achieve consensus AND be guaranteed to terminate. 2PC is a consensus protocol (all agree: commit or abort). How does 2PC relate to FLP impossibility? Does 2PC "solve" consensus in the FLP sense? And what does this mean for real-world 2PC deployments — do they violate FLP or make a different assumption?
_Hint:_ 2PC achieves SAFETY (if all commit: no one aborts; if coordinator crashes: nobody commits without authorization) but violates LIVENESS (participants can wait indefinitely for a crashed coordinator). FLP says: no protocol can be both SAFE and LIVE in async networks with crash failures. 2PC chooses SAFETY over LIVENESS — it blocks forever rather than making a potentially wrong decision. Three-Phase Commit improves liveness (non-blocking in synchronous networks) but adds a synchrony assumption. Paxos-commit restores liveness by using consensus (Raft) for the coordinator role. Which aspect of FLP impossibility does each approach address: the synchrony assumption or the safety/liveness trade-off?
