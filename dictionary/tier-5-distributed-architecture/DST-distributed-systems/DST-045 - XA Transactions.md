---
id: DST-029
title: XA Transactions
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-015, DST-039, DST-014
used_by: DST-017, DST-052
related: DST-015, DST-017, DST-056
tags:
  - distributed
  - transactions
  - database
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /distributed-systems/xa-transactions/
---

# DST-016 - XA Transactions

⚡ **TL;DR** — XA is the industry-standard interface for Two-Phase
Commit across heterogeneous resource managers (databases, queues,
message brokers), allowing atomic commits spanning multiple systems.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-015, DST-039, DST-014               |         |
| **Used by:**    | DST-017, DST-052                        |         |
| **Related:**    | DST-015, DST-017, DST-056               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank transfer spans a PostgreSQL database (debit) and a message
queue (send notification). Without coordination, the debit commits
but the broker crashes before the message is enqueued. Or the
message is sent but the DB rollback leaves the account credited.
Each system has ACID locally, but the cross-system operation is
not atomic.

**THE BREAKING POINT:**
1990s enterprise Java applications connected to databases,
message brokers, and ERP systems simultaneously. Every vendor
had their own proprietary transaction API. Each application had
to hand-code retry and rollback logic for every combination of
resource types — a combinatorial maintenance nightmare.

**THE INVENTION MOMENT:**
The X/Open Consortium (1991) published the XA specification:
a common C interface (`xa_start`, `xa_end`, `xa_prepare`,
`xa_commit`, `xa_rollback`) that any transaction-capable resource
manager could implement. The Transaction Manager (TM) could then
coordinate 2PC across any combination of XA-compliant resources.

**EVOLUTION:**
XA was standardized into Java via JTA (Java Transaction API,
JSR-907). Frameworks like Atomikos, Bitronix, and Narayana
implement the Transaction Manager role. Spring's `@Transactional`
annotation can delegate to a JTA TM for cross-resource atomicity.
Modern microservices architectures largely replace XA with the
Saga pattern (DST-056) due to XA's performance and coupling costs.

---

### 📘 Textbook Definition

**XA** (eXtended Architecture) is the X/Open distributed
transaction processing (DTP) specification. It defines the
interface between a Transaction Manager (TM) and Resource Managers
(RMs — databases, message brokers, JMS providers). XA implements
Two-Phase Commit (DST-015): Phase 1 (`xa_prepare`) asks all RMs
to log and lock their changes; Phase 2 (`xa_commit` or
`xa_rollback`) finalizes atomically. The TM is the coordinator;
the TM log (transaction log) is the source of truth for in-doubt
transactions on crash recovery.

---

### ⏱️ Understand It in 30 Seconds

**One line:** XA is the standard plug for connecting any database
or broker into a coordinated two-phase commit.

> Like a universal power adapter: regardless of which "socket"
> (database vendor) you plug into, the XA standard ensures the
> Transaction Manager can speak the same protocol to all of them.

**One insight:** XA solves the VENDOR HETEROGENEITY problem of
distributed transactions — not the fundamental performance or
availability limits of 2PC. Choosing XA still means choosing 2PC
trade-offs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A Transaction ID (XID) globally identifies a distributed
   transaction across all participating resource managers.
2. `xa_prepare` is a promise: the RM has written its changes to
   durable storage and will not lose them if asked to commit.
3. Once the TM writes "commit" to its log, it will retry forever
   until all RMs acknowledge — the atomic commit point.
4. The TM log is the single source of truth; losing it means
   in-doubt transactions must be resolved manually.

**DERIVED DESIGN:**
Components: Application (starts/ends transaction), TM (coordinates
2PC, owns the log), RM (database or broker, implements xa_*
interface). The TM assigns XIDs; passes them to each RM via
`xa_start`. After application work: TM calls `xa_prepare` on each
RM; on all-OK calls `xa_commit` on each; on any FAIL calls
`xa_rollback` on all.

**THE TRADE-OFFS:**
**Gain:** True atomicity across heterogeneous resources with no
application-level retry logic; compatible with standard JDBC/JTA
frameworks; crash recovery is handled by TM log replay.
**Cost:** Each `xa_prepare` holds locks until `xa_commit` — latency
is 2+ RTTs per transaction; TM is a new SPOF; all RMs must be
reachable at commit time (partition = blocked transactions);
debugging in-doubt transactions requires vendor-specific tools.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Coordinating atomicity across two independent
systems requires at least two communication rounds — you cannot
avoid this.
**Accidental:** The `xa_*` C interface, JTA boilerplate,
JNDI datasource configuration, and TM-specific recovery tools
are accidental complexity added by the specification's age.

---

### 🧪 Thought Experiment

**SETUP:** A flight booking system writes to a reservation DB and
charges a payment processor. Both are XA-capable.

**WHAT HAPPENS WITHOUT XA:**
Two separate JDBC connections, two `commit()` calls. Reservation
commits; payment processor crashes before commit. Booking confirmed
but payment not charged. Or payment charged but DB crashes before
reservation saved. Customer has a receipt but no seat.

**WHAT HAPPENS WITH XA:**
TM starts XA transaction, XID shared with DB and payment
processor. Application performs DB insert + payment charge. TM
calls `xa_prepare` on both: DB locks the row, payment processor
holds the auth token. TM writes "commit" to its log. TM calls
`xa_commit` on both. If payment processor crashes AFTER prepare
but BEFORE commit, TM retries on recovery — the payment processor
will find the prepared transaction in its own log and commit it.
Either both commit or neither does.

**THE INSIGHT:** The power of XA is the prepare phase creating
a durable promise. Once all RMs have prepared, the transaction
WILL commit — even across crashes — because the TM retries.

---

### 🧠 Mental Model / Analogy

> XA is like a wedding officiant (Transaction Manager) overseeing
> two parties (Resource Managers). Phase 1: "Do you, Database, take
> this transaction?" — both say "I do" and sign a pre-nuptial
> contract (xa_prepare). Phase 2: officiant declares the marriage
> complete (xa_commit). If one party faints after signing (crash
> after prepare), the officiant can still complete the ceremony
> when they recover.

Element mapping:
- Wedding officiant = Transaction Manager (TM)
- Parties = Resource Managers (database, broker)
- "I do" + pre-nuptial signing = xa_prepare (durable promise)
- Marriage declaration = xa_commit
- Marriage register = TM log
- Fainting = crash after prepare

Where this analogy breaks down: a wedding can have one party
absent and still proceed legally in some contexts; XA requires
ALL parties to prepare before ANY commit.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
XA is a way to make sure that when your application updates two
different systems at once (a database AND a message queue, for
example), either BOTH updates succeed or NEITHER does — even if
one of the systems crashes in the middle.

**Level 2 - How to use it (junior developer):**
In Spring Boot with JTA: add an XA-capable connection pool
(e.g. Atomikos), configure JTA transaction manager, use
`@Transactional` as normal. Spring handles xa_start/prepare/
commit transparently. Key config:
```yaml
spring.jta.atomikos.datasource.xa-data-source-class-name:
  com.mysql.cj.jdbc.MysqlXADataSource
```

**Level 3 - How it works (mid-level engineer):**
When `@Transactional` method starts: JTA TM calls `xa_start(XID)`
on each enlisted RM (DB connection pool, JMS connection). When
method completes: TM calls `xa_end(XID)` then `xa_prepare(XID)`
on each RM sequentially. On all-OK: TM writes commit record to
its transaction log (fsync), then calls `xa_commit(XID)` on each.
If TM crashes after log write, on restart it reads the log and
retries `xa_commit` on all in-doubt RMs. If any RM fails to
prepare, TM calls `xa_rollback(XID)` on all prepared RMs.

**Level 4 - Why it was designed this way (senior/staff):**
The critical design choice is the TM log (write-ahead log for
commit records). Without it, a TM crash after prepare but before
commit leaves RMs in-doubt forever — they hold locks and cannot
unilaterally decide. The TM log solves this: it is the
authoritative record of the commit decision. However, this makes
the TM log a SPOF: if it is corrupted or lost, in-doubt
transactions become zombies requiring DBA intervention. Modern
XA TMs use replicated logs (e.g. Narayana with shared NFS or
database-backed logs) to mitigate this.

**Expert Thinking Cues:**
- "What is my TM's SPOF story — is its log replicated?"
- "How long will locks be held if one RM is slow to prepare?"
- "Have I tested TM crash-recovery in my staging environment?"

---

### ⚙️ How It Works (Mechanism)

```
Application         TM (Coordinator)     DB (RM1)   Broker (RM2)
    |                    |                  |             |
    |--beginTx()-------->|                  |             |
    |                    |--xa_start(XID)-->|             |
    |                    |--xa_start(XID)-------------->  |
    |--dbInsert()------->|                  |             |
    |--brokerSend()----->|                  |             |
    |--commit()--------->|                  |             |
    |                    |--xa_end(XID)---->|             |
    |                    |--xa_prepare(XID)->|             |
    |                    |<--PREPARED--------|             |
    |                    |--xa_prepare(XID)-------------> |
    |                    |<--PREPARED--------------------- |
    |                    |--[WRITE COMMIT LOG]--fsync      |
    |                    |--xa_commit(XID)->|             |
    |                    |--xa_commit(XID)-------------->  |
    |<--success----------|                  |             |
```

**Crash recovery (TM crashes after COMMIT LOG write):**
```
TM restarts:
  1. Read transaction log -> find committed XID
  2. Call xa_commit(XID) on each RM
  3. RMs either commit (if prepared) or respond XAER_NOTA
     (already committed -> idempotent)
  4. Mark transaction complete in log
```

---

### 💻 Code Example

```java
// BAD: two separate commits -- not atomic
@Service
public class OrderService {
    public void placeOrder(Order order) {
        // If broker crashes between these two commits:
        // order saved but notification never sent
        orderRepo.save(order);          // commit 1
        notificationBroker.send(order); // commit 2
    }
}

// GOOD: XA transaction across DB and JMS broker
@Service
public class OrderService {
    // JtaTransactionManager + XA DataSource + XA JMS configured
    // in application context (Atomikos or Narayana)

    @Transactional // Uses JTA -- coordinates XA across both RMs
    public void placeOrder(Order order) {
        // Both operations in same XA transaction (XID)
        orderRepo.save(order);
        notificationQueue.send(
            session.createObjectMessage(order));
        // On method return: TM xa_prepare both, then xa_commit
        // If anything fails: TM xa_rollback both
    }
}
```

**Spring Boot JTA configuration (Atomikos):**
```yaml
spring:
  jta:
    atomikos:
      datasource:
        unique-resource-name: orderDb
        xa-data-source-class-name:
          org.postgresql.xa.PGXADataSource
        xa-properties:
          serverName: localhost
          portNumber: 5432
          databaseName: orders
      connectionfactory:
        unique-resource-name: notificationQueue
        xa-connection-factory-class-name:
          org.apache.activemq.ActiveMQXAConnectionFactory
```

**How to test / verify correctness:**
```java
@Test
public void testXaRollbackOnBrokerFailure() {
    // Arrange: broker configured to throw after xa_prepare
    brokerRM.setFailOnPrepare(true);

    // Act: attempt order placement
    assertThrows(TransactionSystemException.class,
        () -> orderService.placeOrder(testOrder));

    // Assert: DB should be rolled back
    assertFalse(orderRepo.existsById(testOrder.getId()));
}
```

---

### ⚖️ Comparison Table

| Property             | Local Transaction | XA / JTA       | Saga (DST-056)   |
| -------------------- | ----------------- | --------------- | ---------------- |
| Atomicity scope      | Single RM         | Multiple RMs    | Multiple services|
| Coupling             | None              | Tight (2PC)     | Loose (async)    |
| Latency overhead     | None              | 2+ RTTs         | Multiple RTTs    |
| Lock duration        | Short             | Longer (prepare)| None             |
| Failure handling     | Automatic rollback| TM log recovery | Compensating txns|
| Partition tolerance  | High              | Low (blocks)    | High             |
| Complexity           | Low               | Medium          | High (app logic) |
| Right for            | Single DB         | Same-DC RMs     | Microservices    |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "XA gives you distributed ACID for free" | XA gives atomicity across RMs; isolation is per-RM (global snapshot isolation is not provided); durability depends on TM log integrity |
| "Spring @Transactional always uses XA" | By default, Spring uses the local DataSourceTransactionManager (one DB only); XA requires explicit JTA configuration with an XA-capable TM |
| "XA transactions can span microservices" | XA requires the TM to have direct access to all RM connections; it cannot cross process or network boundaries to external services |
| "XA is obsolete" | XA is still widely used in enterprise Java (banking, telecom, ERP) wherever heterogeneous resources need atomic coordination; it is less common in cloud-native microservices |
| "A crashed RM during xa_prepare causes data loss" | A crash during PREPARE causes a rollback (no data committed yet); data loss risk is only if the TM log is lost after a commit decision |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: In-doubt transactions locking database rows**

**Symptom:** Application queries hang; DB shows long-running
transactions holding row locks; TM log shows "prepared" entries
that never complete.
**Root Cause:** TM crashed after xa_prepare but before xa_commit;
on restart, TM log was not replayed; RMs still hold prepared state.
**Diagnostic:**
```sql
-- PostgreSQL: find prepared XA transactions
SELECT gid, prepared, owner, database
FROM pg_prepared_xacts;

-- MySQL: find in-doubt XA transactions
XA RECOVER;
```
**Fix:** Identify the XID from TM logs; manually commit or
rollback:
```sql
-- PostgreSQL
COMMIT PREPARED 'xid-value';
-- or
ROLLBACK PREPARED 'xid-value';
```
**Prevention:** Configure TM log replication; set `xa_prepare`
timeout so RMs rollback automatically after a bounded wait.

---

**Failure Mode 2: Performance degradation under XA**

**Symptom:** Transaction throughput drops 3-5x after enabling XA;
DB CPU high; many blocked connections.
**Root Cause:** XA doubles the number of roundtrips (prepare +
commit phases) and extends lock hold time across the network RTT
between TM and RMs.
**Diagnostic:**
```bash
# Check transaction rate vs latency
# Prometheus JVM metrics (Atomikos exports these):
atomikos_transaction_duration_seconds_bucket
# Or DB level
SHOW STATUS LIKE 'Innodb_row_lock_waits'; # MySQL
```
**Fix:** Batch operations to reduce XA transaction count; consider
Saga pattern for long-running or high-throughput flows; use XA
only for short, critical transactions (payments, inventory
decrements).
**Prevention:** Benchmark XA vs local transactions in your
specific environment before committing to the architecture.

---

**Failure Mode 3: TM as single point of failure**

**Symptom:** All transactions fail when TM node goes down; no
failover occurs; on TM restart, recovery is slow.
**Root Cause:** TM is deployed as a single instance without
replication or HA; its transaction log is on local disk.
**Diagnostic:**
```bash
# Atomikos: check TM log location and replication
ls -la /var/lib/atomikos/
# Should be on shared or replicated storage
df -h /var/lib/atomikos/
```
**Fix:** Deploy TM in HA mode (Narayana + shared DB log, or
Atomikos Extreme Transactions with active-passive failover);
ensure TM log is on replicated storage.
**Prevention:** Treat the TM as a critical infrastructure
component; apply the same HA treatment as your primary database.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-015 - Two-Phase Commit (2PC) (the algorithm XA implements)
- DST-039 - Serializability (the consistency guarantee XA targets)
- DST-014 - Failure Modes (what XA must recover from)

**Builds On This (learn these next):**
- DST-017 - Three-Phase Commit (3PC) (non-blocking alternative)
- DST-056 - Saga Pattern (modern alternative for microservices)
- DST-052 - Distributed Locking (often used alongside XA)

**Alternatives / Comparisons:**
- Saga pattern (DST-056): no 2PC, higher availability, more
  application complexity for compensation
- Outbox pattern (DST-063): solves DB + broker atomicity without XA
  via a transactional outbox table

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Standard API for 2PC across RMs  |
| PROBLEM SOLVES| Atomic commits across DB+broker  |
| KEY INSIGHT   | xa_prepare = durable promise;    |
|               | TM log = commit source of truth  |
| USE WHEN      | Must atomically coordinate 2 RMs  |
|               | in same DC; JTA/JEE environment  |
| AVOID WHEN    | Microservices across networks;   |
|               | high throughput; long transactions|
| TRADE-OFF     | Atomicity vs latency + coupling  |
| ONE-LINER     | Standard plug for 2PC across any |
|               | XA-compliant DB or broker        |
| NEXT EXPLORE  | DST-056 Saga (modern alternative)|
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. XA = standard interface for 2PC across heterogeneous systems;
   the TM coordinates `xa_prepare` then `xa_commit` on all RMs.
2. The TM log is the atomic commit point; losing it causes in-doubt
   transactions that require manual DBA resolution.
3. XA is correct but expensive; prefer Saga or Outbox pattern for
   microservices or high-throughput scenarios.

**Interview one-liner:** "XA implements 2PC across heterogeneous
resource managers via a standard xa_prepare/xa_commit interface;
the Transaction Manager's write-ahead log is the atomic commit
point, enabling crash recovery without data loss."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** A durable, replicated log that
records a decision BEFORE acting on it is the universal pattern
for atomic, recoverable operations. The TM log in XA, the WAL in
Postgres, and the Raft log in distributed consensus all share this
invariant: write intent first, execute second.

**Where else this pattern appears:**
- **Database WAL:** PostgreSQL writes the intended change to its
  WAL before applying it; crash recovery replays the WAL.
- **Kafka producer idempotency:** Kafka assigns producer IDs and
  sequence numbers (a mini-log) to detect and deduplicate retried
  writes — same "log before action" principle.
- **Distributed saga log:** an explicit saga log records
  compensation actions upfront; on failure, the orchestrator
  replays the log to undo steps in reverse order.

---

### 💡 The Surprising Truth

XA transactions were designed in 1991 when a "distributed system"
meant multiple databases in the same server room connected by a
LAN. The spec assumes tight coupling and low latency between TM
and RMs. When developers try to use XA across AWS regions or
between microservices in different Kubernetes clusters, they
encounter the mismatch: XA requires the TM to hold an open
connection to every RM during the entire prepare phase, which
across a WAN means holding locks for hundreds of milliseconds.
This is why cloud-native architectures moved to Saga — not
because Saga is simpler (it is much harder to implement correctly),
but because XA's coupling model is physically incompatible with
the internet's latency profile.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** If the Transaction Manager
crashes AFTER writing "commit" to its log but BEFORE calling
`xa_commit` on Resource Manager 2, what exactly happens on TM
restart, and why does this not violate atomicity?
*Hint:* Trace the TM recovery procedure: what does it read from
the log, and what does it call on the in-doubt RMs?

**Question B (Scale):** Your service processes 10,000 orders per
second. Each order requires an XA transaction across a DB and a
message broker. Estimate the minimum additional latency per
transaction from XA, and determine at what throughput XA becomes
the bottleneck.
*Hint:* Consider 2 RTTs of 5 ms each (same DC) plus lock hold
time; then model queuing theory as concurrency approaches the
RM connection limit.

**Question C (Design Trade-off):** The Outbox Pattern (DST-063)
claims to solve the same "DB + broker atomicity" problem as XA
without using 2PC. Compare the failure modes of each approach:
when does Outbox win, and when does XA win?
*Hint:* Consider at-least-once vs exactly-once delivery, broker
availability requirements, and the cost of idempotent consumers.