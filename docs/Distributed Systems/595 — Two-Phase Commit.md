---
layout: default
title: "Two-Phase Commit (2PC)"
parent: "Distributed Systems"
nav_order: 595
permalink: /distributed-systems/two-phase-commit/
number: "0595"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Transactions, ACID, Failure Modes
used_by: XA Transactions, Distributed Databases, Saga alternatives
related: Three-Phase Commit, Saga Pattern, Distributed Locking
tags:
  - 2pc
  - two-phase-commit
  - distributed-transactions
  - advanced
---

# 595 — Two-Phase Commit (2PC)

⚡ TL;DR — Two-Phase Commit is a distributed atomic commitment protocol that ensures either all participants commit a transaction or all abort — maintaining atomicity across multiple nodes. Phase 1 (Prepare): coordinator asks all participants "can you commit?" — each locks resources and votes yes/no. Phase 2 (Commit/Abort): if ALL vote yes, coordinator sends commit; any no → coordinator sends abort. The critical flaw: if the coordinator crashes after sending Prepare but before sending Commit/Abort, participants are left in a "blocking" limbo — they cannot proceed without the coordinator.

┌──────────────────────────────────────────────────────────────────────────┐
│ #595         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Distributed Transactions, ACID      │                      │
│ Used by:     │ XA Transactions, Distributed DBs   │                      │
│ Related:     │ 3PC, Saga Pattern, Dist. Locking   │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

A bank transfer: debit Account A on DB-1, credit Account B on DB-2. If debit succeeds but credit fails → money lost. If DB-1 crashes after debit commit but before DB-2 processes credit → inconsistency. 2PC solves this: both DB-1 and DB-2 prepare (lock the funds), coordinate, and COMMIT or ABORT atomically. Either both accounts are updated or neither is.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is an atomic commitment protocol for distributed transactions:

**Phase 1 — Prepare (Voting Phase):**
- Coordinator sends PREPARE to all participants
- Each participant: (1) executes the transaction, (2) writes "prepare" record to durable log, (3) acquires locks, (4) responds VOTE-YES or VOTE-NO
- If VOTE-YES: participant is committed to commit if told to; it cannot abort unilaterally

**Phase 2 — Commit/Abort (Decision Phase):**
- If all VOTE-YES: coordinator writes COMMIT to log, sends COMMIT to all participants
- If any VOTE-NO or timeout: coordinator sends ABORT to all
- Each participant: executes commit or abort, releases locks, ACKs to coordinator

**Blocking problem:** If coordinator crashes after Phase 1 votes are collected but before Phase 2 decision is sent, participants are in "uncertain" state — they hold locks and cannot proceed until coordinator recovers. This is 2PC's fundamental limitation.

---

### ⏱️ Understand It in 30 Seconds

**One line:** All nodes vote to commit; coordinator decides; all commit or all abort — but coordinator crash = blocking.

**Analogy:** Wedding ceremony. Officiant asks "Do you take this person?" (PREPARE). Both say "I do" (VOTE-YES). Officiant says "I now pronounce you..." (COMMIT). If both said yes but the officiant fainted after "Do you..." and before pronouncing: both parties are legally "prepared" but neither married nor free. They must wait for the officiant to recover. The marriage is "uncertain" and cannot proceed unilaterally.

---

### 🔩 First Principles Explanation

```
2PC HAPPY PATH:

  Coordinator           Participant A          Participant B
      │                      │                      │
      │── PREPARE ──────────►│                      │
      │── PREPARE ───────────────────────────────►  │
      │                      │ (execute, lock, log) │
      │                      │ (execute, lock, log) │
      │◄── VOTE-YES ─────────│                      │
      │◄── VOTE-YES ─────────────────────────────── │
      │ (write COMMIT to log)│                      │
      │── COMMIT ───────────►│                      │
      │── COMMIT ────────────────────────────────►  │
      │                      │ (commit, unlock)     │
      │                      │ (commit, unlock)     │
      │◄── ACK ──────────────│                      │
      │◄── ACK ──────────────────────────────────── │
  
  FAILURE — COORDINATOR CRASHES AT ✗:
  
  Coordinator           Participant A          Participant B
      │── PREPARE ──────────►│                      │
      │── PREPARE ───────────────────────────────►  │
      │◄── VOTE-YES ─────────│                      │
      │◄── VOTE-YES ─────────────────────────────── │
      ✗ COORDINATOR CRASHES                         │
  
  Now: A and B have voted YES, hold locks, wait for decision.
  They CANNOT abort: they committed to commit.
  They CANNOT commit: they don't know if all voted yes.
  BLOCKED: until coordinator recovers and resends decision from its log.
  
  WHAT IF PARTICIPANT CRASHES (after VOTE-YES)?
  Participant B crashes and restarts.
  Reads its log: "prepared for transaction XYZ."
  Sends "what was the decision?" to coordinator.
  Coordinator resends COMMIT or ABORT. → B can complete. ✓
```

---

### 🧠 Mental Model / Analogy

> 2PC is like a nuclear launch procedure requiring two keys (both officers must turn their keys simultaneously, exactly once). Phase 1: both officers confirm they're ready and lock their console (PREPARE). Phase 2: command sends "LAUNCH" or "STAND DOWN." If command goes silent after receiving "ready" but before sending the order: both officers are locked at their consoles, unable to stand down (only command can authorize that), unable to launch. Blocking — until command comes back online.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** 2PC = two rounds: vote, then decide. Atomicity: all commit or all abort. Blocking problem: coordinator crash after Phase 1 = participants deadlocked.

**Level 2:** XA transactions (Java EE, JTA) implement 2PC across heterogeneous databases. Spring's `@Transactional` with a JTA transaction manager (Atomikos, Bitronix) uses XA. Each XA resource (DB, message queue) is a participant. The XA coordinator manages the two phases. Performance cost: 2× network round trips minimum; locks held across both phases (high contention for write-heavy workloads).

**Level 3:** Optimizations: (a) Read-only optimization — if a participant only read (no writes), it can VOTE-READONLY in Phase 1, skip Phase 2 entirely. (b) Presumed abort — if coordinator crashes before logging a COMMIT, recovering coordinator assumes ABORT (safe: abort is always the default for uncertain transactions). (c) One-phase commit — if there's only 1 participant, skip Phase 1 and directly commit (coordinator is the only decision maker). Real databases use XA with these optimizations.

**Level 4:** The FLP impossibility result applies: in an asynchronous system with even one crash failure, no protocol can guarantee both safety (all-or-nothing) and liveness (eventual decision) simultaneously. 2PC sacrifices liveness (can block indefinitely) to preserve safety. 3PC sacrifices some safety guarantees in edge cases to avoid blocking. Paxos-based commit protocols (like those used in Spanner) achieve both but require consensus (Paxos) within each participant group, not just at the coordinator.

---

### ⚙️ How It Works (Mechanism)

```
XA TRANSACTION WITH JDBC:

  Application (Coordinator):
  1. xa.start(xid)  ← begin distributed transaction
  2. Resource A: UPDATE accounts SET balance=balance-100 WHERE id=1
  3. Resource B: UPDATE accounts SET balance=balance+100 WHERE id=2
  4. xa.end(xid)
  
  Phase 1 (Prepare):
  5. Resource A: xa.prepare(xid) → XA_OK (locked, logged, ready)
  6. Resource B: xa.prepare(xid) → XA_OK (locked, logged, ready)
  
  Phase 2 (Commit):
  7. xa.commit(xid) on Resource A → apply, release locks
  8. xa.commit(xid) on Resource B → apply, release locks
  
  CRASH RECOVERY:
  If coordinator crashes between step 6 and step 7:
  → Coordinator restarts, reads transaction log: "prepared XID=abc, all votes YES"
  → Reissues xa.commit(xid) to both resources
  Resources implement xa.recover(): return list of in-doubt transactions
  → Coordinator resolves all in-doubt transactions on recovery ✓
```

---

### 💻 Code Example

```java
// Spring Boot with JTA (Atomikos) — 2PC across two databases

@Configuration
@EnableTransactionManagement
public class XAConfig {

    @Bean
    public JtaTransactionManager transactionManager() {
        return new JtaTransactionManager(); // Uses Atomikos UserTransactionManager
    }

    @Bean(name = "primaryDataSource")
    public DataSource primaryDataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setXaDataSourceClassName("org.postgresql.xa.PGXADataSource");
        ds.setUniqueResourceName("PrimaryDB");
        // ... connection properties
        return ds;
    }

    @Bean(name = "secondaryDataSource")
    public DataSource secondaryDataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setXaDataSourceClassName("com.mysql.cj.jdbc.MysqlXADataSource");
        ds.setUniqueResourceName("SecondaryDB");
        return ds;
    }
}

@Service
@Transactional  // JTA transaction — spans both databases atomically via 2PC
public class TransferService {

    @Autowired @Qualifier("primaryDataSource") private DataSource primaryDS;
    @Autowired @Qualifier("secondaryDataSource") private DataSource secondaryDS;

    public void transfer(long fromId, long toId, BigDecimal amount) {
        // Both of these execute within the SAME XA transaction
        // 2PC ensures both commit or both abort atomically
        primaryJdbcTemplate.update(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromId);
        secondaryJdbcTemplate.update(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toId);
        // On method exit: @Transactional triggers xa.commit() across both databases
        // Any exception within: @Transactional triggers xa.rollback() across both
    }
}
```

---

### ⚖️ Comparison Table

| Protocol | Blocking? | Fault Tolerance | Message Rounds | Use Case |
|---|---|---|---|---|
| **2PC** | Yes (coord crash) | Crash-recovery only | 4 (prepare + commit each way) | XA transactions, enterprise ETL |
| **3PC** | Rarely | Crash-recovery + partial network | 6 (extra phase) | Rarely used in practice |
| **Raft-based commit** | No | Crash-recovery (via Raft) | Raft RTT | Spanner, CockroachDB |
| **Saga** | No (compensating txns) | Eventual consistency only | N×2 messages (one per step) | Microservices, long-running workflows |

---

### 🚨 Failure Modes & Diagnosis

```
Symptom: XA transaction stuck in PREPARED state; database locks held indefinitely.
         Application timeout, but DB still shows uncommitted XA transactions.

Diagnosis:
  PostgreSQL: SELECT * FROM pg_prepared_xacts;  ← shows in-doubt XA transactions
  MySQL:      XA RECOVER;                        ← shows prepared but uncommitted

Root Cause: Coordinator (application server) crashed after Phase 1 but before Phase 2.
            Resources are waiting for coordinator's COMMIT or ROLLBACK decision.

Resolution:
  Option 1: Restart coordinator (Atomikos) — it reads transaction log, resends decision
  Option 2: Manual resolution if coordinator log is lost:
    PostgreSQL: COMMIT PREPARED 'transaction-id';  or  ROLLBACK PREPARED 'transaction-id';
  
  Note: Manual resolution risks inconsistency if you guess wrong.
  Always check all participants' status before manually deciding.

Prevention:
  1. Use JTA implementation with persistent transaction log (Atomikos, Narayana)
  2. Monitor for in-doubt transactions: alert if pg_prepared_xacts is non-empty for >1 min
  3. Consider Saga pattern for long-running transactions (no blocking)
```

---

### 🔗 Related Keywords

- `Three-Phase Commit` — adds a pre-commit phase to avoid blocking in some partition scenarios
- `Saga Pattern` — alternative to 2PC for microservices: eventual consistency via compensating transactions
- `Distributed Locking` — 2PC holds locks across phases; prolonged contention is a key cost

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1       │ PREPARE: each participant executes, locks,  │
│               │ writes prepare log, votes YES/NO            │
│ PHASE 2       │ All-YES → COMMIT; any NO → ABORT            │
│ BLOCKING      │ Coordinator crash after Phase 1 = deadlock  │
│ JAVA          │ JTA (@Transactional) + XA DataSources       │
│ ALTERNATIVE   │ Saga pattern for microservices              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A distributed e-commerce system uses 2PC (JTA/XA) across an inventory database and an orders database for order placement. Under high load, order placement p95 latency spikes to 800ms. (1) What phase of 2PC is most likely the bottleneck? Why does 2PC inherently hold more locks than a local transaction? (2) The team proposes migrating to a Saga pattern to eliminate 2PC. What consistency guarantee does Saga sacrifice compared to 2PC? In what scenarios would this compromise cause correctness issues (e.g., double-booking)? (3) Can you design a hybrid: use optimistic concurrency control (version numbers) to avoid lock contention in 2PC Phase 1, while still using 2PC for atomicity? What new failure mode does this introduce?
