---
id: DST-034
title: "Two-Phase Commit"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-033, DST-032
used_by: DST-035
related: DST-033, DST-035, DST-032
tags:
  - distributed
  - transactions
  - consistency
  - pattern
  - deep-dive
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /distributed-systems/two-phase-commit-practical/
---

# DST-034 - Two-Phase Commit

⚡ TL;DR - Two-Phase Commit (2PC) in practice means XA transactions, JTA/Atomikos coordinators, and database-specific distributed transaction APIs — and it means accepting the operational reality: coordinator recovery, heuristic decisions, and latency overhead that makes 2PC unsuitable for most microservices architectures.

| Metadata | | |
|:---|:---|:---|
| **Depends on:** | DST-033, DST-032 | |
| **Used by:** | DST-035 | |
| **Related:** | DST-033, DST-035, DST-032 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java EE application needs to write to two databases and a JMS queue — atomically. Without a transaction coordinator: three separate commits, each potentially failing independently. One commit fails: partial state. Rollback is manual and error-prone. Without 2PC (XA), every multi-resource operation needs bespoke compensation logic — complex, bug-prone, and untestable.

**THE BREAKING POINT:**
Enterprise applications of the 2000s typically accessed multiple databases, messaging systems, and ERP connectors simultaneously within a single business operation. ACID guarantees across these resources required 2PC. Without it: distributed data integrity violations were common. The XA standard emerged as the solution.

**THE INVENTION MOMENT:**
The XA specification (X/Open Distributed Transaction Processing standard, 1991) defined the interface between a Transaction Manager (coordinator) and Resource Managers (databases, message queues). Java's JTA (Java Transaction API, 1999) brought XA to the Java platform. Application servers (WebLogic, JBoss, IBM WebSphere) became 2PC coordinators. This created the "JTA + XA datasources" stack that ran most enterprise Java for 15 years.

**EVOLUTION:**
1991: XA specification. 1999: JTA 1.0. 2001-2010: JEE application server 2PC hegemony. 2014: Spring Boot popularizes embedded servers — JTA/XA becomes optional. 2015+: Saga pattern popularized in microservices. 2020+: Most new services avoid 2PC entirely (eventual consistency, single-writer per service). Legacy systems still rely on XA for existing multi-database workloads.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC) in practice** refers to the implementation of the distributed atomic commitment protocol (DST-033) via the **XA protocol** and its associated transaction management frameworks. **XA interface:** `xa_prepare(xid)`, `xa_commit(xid)`, `xa_rollback(xid)` — the interface any XA-compliant resource (RDBMS, JMS, CICS) must implement. **Transaction Manager (TM):** the coordinator role (Atomikos, Narayana, JOTM in Java; MSDTC in .NET; IBM Global Transaction Manager). The TM manages the XID (distributed transaction ID), calls `xa_prepare` on all resources, then `xa_commit` or `xa_rollback`. **Recovery:** the TM logs its decision to durable storage (transaction log). On crash recovery: reads log, resends Phase 2 decisions to all participants. **Heuristic decisions:** when recovery fails (TM log lost), resources may make autonomous decisions — "heuristic commit" or "heuristic abort" — violating atomicity. A **"heuristic hazard"** is the risk of inconsistency from unilateral autonomous decisions.

---

### ⏱️ Understand It in 30 Seconds

**One line:** XA is 2PC implemented as a standard API — your app server (coordinator) calls xa_prepare/xa_commit on databases and queues; if the app server crashes, the recovery log is the lifeline.

> The XA standard is like air traffic control for distributed transactions. The control tower (Transaction Manager) sequences every operation. Each airplane (resource: database, queue) follows ATC instructions to land (commit) or go-around (rollback). If the control tower goes offline mid-flight: airplanes hold their position (locks held) until control restores. Without ATC: chaos.

**One insight:** The practical challenge of 2PC is not the algorithm (understood since 1978) — it's the OPERATIONAL burden: transaction log management, coordinator HA, in-doubt transaction resolution, and the latency impact on high-throughput systems.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **XID uniqueness:** every distributed transaction has a globally unique XID. All participants use this XID to coordinate Phase 1 and Phase 2. No two concurrent transactions may share an XID.
2. **TM log durability:** the TM must persist its commit/abort decision BEFORE sending Phase 2. If the TM crashes after persisting: recovery replays Phase 2 from the log. If the TM crashes before persisting: the outcome is undetermined — potentially requiring heuristic decision.
3. **Resource recovery:** each XA resource must support `xa_recover()` — querying which XIDs are currently in PREPARED state. TM uses this on recovery to resolve in-doubt transactions by checking its log.
4. **Single coordinator per transaction:** one TM manages the entire transaction. Multiple TMs managing the same transaction (nested JTA) requires an additional coordination layer (rarely implemented correctly).

**DERIVED DESIGN:**
In JTA: UserTransaction.begin() → {operations on XA resources} → UserTransaction.commit(). The application server's TM enlists all XA connections used during the transaction. On commit: calls xa_prepare on all, then xa_commit. The application never calls XA directly.

**THE TRADE-OFFS:**
**Gain:** Transparent distributed atomicity. Application writes normal local transaction code; TM handles distribution.
**Cost:** 2× latency (2 RTTs). Coordinator SPOF (requires HA setup). xa_prepare calls lock resources prematurely. Recovery complexity. Incompatible with connection pooling (each XA connection is stateful through phases).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** 2 network round-trips for distributed atomicity — mathematically required.
**Accidental:** XA API verbosity. TM configuration complexity (log paths, timeouts, recovery). Connection pool incompatibility. These are implementation accidents, not fundamental requirements.

---

### 🧪 Thought Experiment

**SETUP:** Spring Boot application using Atomikos JTA. Two PostgreSQL databases (DB1, DB2). Transaction: write to DB1 AND DB2 atomically. GCP region outage kills the app server process during commit.

**WITHOUT ATOMIKOS RECOVERY (TM log on ephemeral disk):**
- App writes to DB1 and DB2 (both in PREPARED state)
- App server crashes — TM log on ephemeral disk lost forever
- DB1 and DB2 both have rows locked in PREPARED state
- Neither can commit or abort without TM recovery
- DBA must manually inspect application audit logs, determine intent, issue `COMMIT PREPARED 'xid'` manually
- Risk: wrong manual decision = data inconsistency

**WITH ATOMIKOS RECOVERY (TM log on persistent storage):**
- App server crashes — TM log on persistent disk survives
- Atomikos restarts, reads log, finds in-doubt transactions
- Calls `xa_recover()` on DB1 and DB2 — finds their PREPARED XIDs
- Matches XIDs to log decisions — sends `xa_commit(xid)` to both
- DB1 and DB2 commit, release locks
- System recovers correctly without manual intervention

**THE INSIGHT:** The TM transaction log is not a performance optimization — it's the only mechanism for correct recovery. Placing it on ephemeral or unreliable storage makes 2PC recovery impossible. This is why cloud deployments of JTA must use persistent volumes (EFS, EBS, Azure Files) for TM logs.

---

### 🧠 Mental Model / Analogy

> The XA protocol is like a restaurant with one head waiter (TM) and multiple kitchen stations (resources). A complex order (transaction) requires the waiter to confirm ALL stations are ready (Phase 1: xa_prepare — each kitchen sets aside the ingredients). Then the waiter gives the final "fire!" command (Phase 2: xa_commit — all stations cook simultaneously). If the waiter falls ill between the "ready" and "fire": all kitchen stations hold their reserved ingredients indefinitely. The restaurant manager (recovery process) must use the order ticket (TM log) to determine if the dish should be served (commit) or cleared (rollback).

**Mapping:**
- **Head waiter** → Transaction Manager (Atomikos, Narayana)
- **Kitchen stations** → XA resources (databases, message queues)
- **"Are you ready?"** → xa_prepare
- **"Fire!" command** → xa_commit
- **Order ticket** → TM transaction log (coordinator log)
- **Manager using order ticket after waiter illness** → TM recovery from log

Where this analogy breaks down: kitchens can improvise if the waiter doesn't return (serve the food anyway or clear it). XA resources legally cannot make unilateral decisions without the coordinator — they must wait, except for "heuristic" emergency situations.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
XA is the standard interface for 2PC. When your app uses JTA and XA datasources: the app server automatically handles "prepare both databases, then commit both." If the app crashes during this: the recovery mechanism figures out what was in progress and either completes or rolls back. It's like the "save game" feature for distributed transactions.

**Level 2 - How to use it (junior developer):**
Spring Boot + Atomikos: add `spring-boot-starter-jta-atomikos`. Configure XA datasources (instead of regular datasources). Use `@Transactional` normally. Spring handles enlistment, xa_prepare, xa_commit automatically. Caveat: XA datasources don't work with standard connection pools (HikariCP) — use Atomikos's own pool.

**Level 3 - How it works (mid-level engineer):**
Atomikos flow for `@Transactional commit()`: (1) `begin()` creates XID. (2) All DB operations enlist their XA connections. (3) `commit()` calls `xa_prepare(xid)` on each enlisted resource (sequentially). (4) After all YES votes: Atomikos logs `COMMIT xid` to disk (fsync). (5) Sends `xa_commit(xid)` to each resource. (6) On crash after step 4: recovery reads log, finds `COMMIT xid`, resends xa_commit. Step 4 (fsync) is the critical synchronization point — everything before it is safe to retry.

**Level 4 - Why it was designed this way (senior/staff):**
XA's design is driven by the need for zero-knowledge coordination: the resource (database) doesn't need to know about other resources in the same transaction. Each resource only knows: "I have XID-X in PREPARED state. I'll wait for xa_commit(XID-X) or xa_rollback(XID-X)." This zero-knowledge design means XA resources are completely generic — the same PostgreSQL xa_prepare implementation works for transactions involving MySQL, Oracle, MQ Series, all simultaneously. The TM holds the "whole picture" of which resources are in which transaction. This separation of concerns (resource = zero-knowledge, TM = full-knowledge) is XA's architectural elegance — and its weakness: the TM's full knowledge makes it the single point of failure.

**Expert Thinking Cues:**
- "Atomikos log is growing unboundedly" → In-doubt transactions not resolved. Check `active-transactions.log` — if XIDs accumulate: participants are not responding to recovery. Check network connectivity to all XA resources.
- "JTA transaction spans multiple microservices — is that OK?" → No. Each microservice call in a JTA transaction is a 2PC participant. Any service crash during prepare blocks the whole transaction. Use Saga instead for cross-service operations.
- "Spring @Transactional with JPA and JMS — will they be atomic?" → Only if both JPA datasource and JMS connection factory are XA-capable AND registered with the JTA TM. Standard HikariCP + standard JMS ConnectionFactory = NOT atomic. Must use XA variants.
- "Our XA transactions timeout after 30 seconds" → `DefaultTransactionTimeout` in Atomikos/Narayana. Transaction held open 30s → locks held 30s → other transactions blocked. Reduce transaction scope: keep all XA-participating operations together, no external service calls inside the transaction boundary.

---

### ⚙️ How It Works (Mechanism)

**XA protocol state machine:**
```
TM (Coordinator):
  begin() → allocates XID
  [operations] → enlists XA connections per XID
  commit():
    Phase 1: xa_prepare(xid) on each resource
    if all OK: log "COMMIT xid" to TM log (fsync)
    Phase 2: xa_commit(xid) on each resource
    log "DONE xid" to TM log

  rollback():
    xa_rollback(xid) on each resource
    log "ABORT xid"

Resource (XA-compliant DB/queue):
  xa_start(xid): associate connection with XID
  [SQL operations]
  xa_end(xid): end SQL association
  xa_prepare(xid): lock rows, write PREPARED to WAL
                   return XA_OK or XA_RDONLY (no writes)
  xa_commit(xid): apply PREPARED changes, release locks
  xa_rollback(xid): discard PREPARED changes, release locks
  xa_recover(): return all in-PREPARED-state XIDs

Recovery flow:
  TM restarts → reads TM log → finds in-doubt XIDs
  calls xa_recover() on each resource
  matches XIDs to log decisions
  resends xa_commit or xa_rollback for each in-doubt XID
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL XA FLOW (JTA with two PostgreSQL databases):**

```
App Server (Atomikos TM)  PostgreSQL1  PostgreSQL2
       │                      │              │
  @Transactional.begin()      │              │
       │  XID=abc-123         │              │
  INSERT INTO orders...       │              │
       │─xa_start(abc-123)───▶│              │
       │─INSERT...───────────▶│              │
       │  INSERT INTO inventory               │
       │─xa_start(abc-123)──────────────────▶│
       │─INSERT...──────────────────────────▶│
       │                                      │
  @Transactional.commit()                     │
       │─xa_prepare(abc-123)─▶│              │
       │         ◀─XA_OK──────│              │
       │─xa_prepare(abc-123)────────────────▶│
       │              ◀─XA_OK──────────────── │
  [fsync COMMIT abc-123 to TM log]
       │─xa_commit(abc-123)──▶│              │
       │─xa_commit(abc-123)─────────────────▶│
       ← YOU ARE HERE: atomic commit complete
```

**FAILURE PATH (TM crash after xa_prepare, before xa_commit):**
TM crashes. Both PG1 and PG2 have rows locked in PREPARED state. No commit sent. TM restarts, reads log, finds `COMMIT abc-123`, calls `xa_commit(abc-123)` on both. Both commit. Locks released.

**WHAT CHANGES AT SCALE:**
High-throughput systems: 2PC latency dominates. At 1000 TPS with 10ms 2PC overhead: 10 seconds of cumulative blocking per second of throughput. At 10,000 TPS: 100 seconds of blocking per second. 2PC is fundamentally throughput-limited by coordinator capacity and network RTT. Solutions: avoid 2PC (Saga), reduce XA participant count (single-DB transactions), use async messaging (exactly-once delivery with idempotency keys).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Kubernetes deployment of JTA: multiple replicas of the same Spring Boot service = multiple TMs = conflicting XIDs! JTA with stateless Kubernetes pods requires: (1) shared TM log volume (PVC), (2) single TM instance (not per-pod). OR: use a remote TM service (Atomikos ExtremeTransactions). Standard JTA embedded in each pod = broken 2PC on restart or replication.

---

### 💻 Code Example

**BAD - JTA with non-XA datasource (no actual 2PC):**
```java
// Common mistake: JTA + non-XA datasource
// Spring's @Transactional works but is NOT 2PC
// Only LOCAL transactions on each datasource
@Configuration
public class BadConfig {
    @Bean
    public DataSource parisDb() {
        // WRONG: HikariCP is NOT XA-capable
        // @Transactional spans both but 2PC is NOT active
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:postgresql://paris:5432/db");
        return ds;
        // If crash after parisDb.commit() but before londonDb.commit():
        // Paris commits, London doesn't = inconsistency
    }
}
```

**GOOD - JTA with XA datasources (true 2PC):**
```xml
<!-- pom.xml: Atomikos JTA starter -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-jta-atomikos</artifactId>
</dependency>
```

```java
// Correct: XA-capable datasources registered with JTA TM
@Configuration
public class XAConfig {

    @Bean(name = "parisDataSource")
    @Primary
    public DataSource parisXADataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setUniqueResourceName("parisDB"); // unique XA name
        ds.setXaDataSourceClassName(
            "org.postgresql.xa.PGXADataSource"
        );
        Properties props = new Properties();
        props.put("serverName", "paris-db-host");
        props.put("portNumber", 5432);
        props.put("databaseName", "orders");
        ds.setXaProperties(props);
        ds.setPoolSize(10);
        // Atomikos automatically enlists connections
        // in JTA transaction via XID tracking
        return ds;
    }

    @Bean(name = "londonDataSource")
    public DataSource londonXADataSource() {
        AtomikosDataSourceBean ds = new AtomikosDataSourceBean();
        ds.setUniqueResourceName("londonDB"); // MUST be unique
        ds.setXaDataSourceClassName(
            "org.postgresql.xa.PGXADataSource"
        );
        // ... London DB properties
        return ds;
    }
}

// application.properties for TM log (CRITICAL: persistent volume)
// spring.jta.atomikos.transactions.log-base-dir=/mnt/efs/atomikos/
// spring.jta.atomikos.transactions.default-jta-timeout=30000
// spring.jta.atomikos.transactions.max-timeout=300000

@Service
@Transactional  // JTA transaction (XA-backed)
public class OrderService {
    @Autowired @Qualifier("parisDataSource")
    private JdbcTemplate parisJdbc;

    @Autowired @Qualifier("londonDataSource")
    private JdbcTemplate londonJdbc;

    public void placeOrder(Order order) {
        // Both operations in SAME XA transaction
        // Atomikos calls xa_prepare on both DBs, then xa_commit
        parisJdbc.update(
            "INSERT INTO orders VALUES (?,?,?)",
            order.getId(), order.getAmount(), order.getCustomer()
        );
        londonJdbc.update(
            "UPDATE inventory SET qty=qty-? WHERE sku=?",
            order.getQuantity(), order.getSku()
        );
        // If ANY exception: xa_rollback called on BOTH
        // If success: xa_prepare then xa_commit on BOTH
        // Atomically committed across both DBs
    }
}
```

**How to test / verify correctness:**
```bash
# 1. Verify XA configuration is active:
# Check Atomikos log on application start:
grep "AtomikosDataSourceBean\|XA" /var/log/app/app.log | head -20
# Should show: "AtomikosDataSourceBean: initialized parisDB"

# 2. Simulate coordinator crash during transaction:
# Kill app process after xa_prepare but before xa_commit:
# Check both databases for PREPARED transactions:
psql -h paris-db -c "SELECT * FROM pg_prepared_xacts;"
psql -h london-db -c "SELECT * FROM pg_prepared_xacts;"
# Both should show the in-flight XID

# 3. Restart app → Atomikos recovery should auto-commit:
# After restart:
psql -h paris-db -c "SELECT * FROM pg_prepared_xacts;"
# Should be empty (recovered and committed)
```

---

### ⚖️ Comparison Table

| Approach | Atomicity | Latency | Coordinator SPOF | Best for |
|:---|:---|:---|:---|:---|
| JTA + XA (Atomikos) | Full atomic | +10-50ms | Yes (TM) | Legacy multi-DB enterprise apps |
| CockroachDB 2PC | Full atomic | +5-20ms | No (Raft) | Cloud-native distributed SQL |
| Saga (choreography) | Eventual | Async | No | Microservices with compensation |
| Saga (orchestration) | Eventual | Async | Yes (orchestrator) | Complex multi-step workflows |
| Single-DB transaction | Full atomic | < 1ms | No | Single-DB services (preferred) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Spring @Transactional with multiple datasources = 2PC" | Only if datasources are XA-capable AND JTA is configured. Standard HikariCP datasources with Spring @Transactional use the "Best Efforts 1PC" heuristic (commit in sequence) — NOT 2PC. This looks correct 99.9% of the time but is not atomic. |
| "Atomikos/Narayana TM can be deployed in stateless pods" | JTA TMs must have persistent transaction logs accessible across pod restarts. In Kubernetes: TM log must be on a PersistentVolumeClaim (EFS, EBS). Each pod must access the SAME log directory. Multiple pods running separate TMs for the same transactions = broken recovery. |
| "XA transactions are just slower regular transactions" | XA transactions acquire locks at xa_prepare time (Phase 1) and hold them until xa_commit (Phase 2). This is fundamentally different from local transactions (acquire locks during execution, release at commit). XA locks can be held much longer, causing higher contention than equivalent local transactions. |
| "PostgreSQL doesn't support distributed transactions" | PostgreSQL fully supports the XA protocol via its `PREPARE TRANSACTION` command. `xa_prepare` → `PREPARE TRANSACTION 'xid'`. `xa_commit` → `COMMIT PREPARED 'xid'`. `xa_rollback` → `ROLLBACK PREPARED 'xid'`. `xa_recover` → `SELECT * FROM pg_prepared_xacts`. |
| "2PC is only relevant for SQL databases" | XA extends to JMS message queues (ActiveMQ, IBM MQ), file system transactions (certain implementations), CICS transactions, and any other resource implementing the XA interface. Email sending, legacy ERP writes, and custom resources can all participate in 2PC via XA. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TM Log on Non-Durable Storage Causes Unrecoverable Transactions**

**Symptom:** Kubernetes pod for the Spring Boot application (with JTA) crashes. Pod restarts. Atomikos recovery runs but finds no in-doubt transactions to recover — even though both PostgreSQL databases show PREPARED transactions from the crashed pod. The transactions remain stuck in PREPARED state indefinitely.
**Root Cause:** Atomikos TM log was stored in the pod's local filesystem (ephemeral storage). On pod restart: a NEW pod starts with a CLEAN TM log — Atomikos sees no in-doubt transactions from its perspective. The databases are stuck waiting for a coordinator that has effectively forgotten the transaction.
**Diagnostic:**
```bash
# Check where Atomikos is writing its log:
grep "log-base-dir" /etc/app/application.properties
# If path is inside container (e.g., /tmp/atomikos/):
# PROBLEM: ephemeral storage, lost on pod restart

# Check if PostgreSQL has stuck PREPARED transactions:
psql -h db-host -c "
  SELECT gid, owner, prepared, database 
  FROM pg_prepared_xacts 
  WHERE prepared < now() - interval '5 minutes';"
# Any rows = stuck transactions from dead coordinator

# Check Atomikos log files:
ls -la /tmp/atomikos/  # (wherever configured)
# If empty after pod restart: log was ephemeral
```
**Fix:**
BAD: `spring.jta.atomikos.transactions.log-base-dir=/tmp/atomikos`
GOOD:
```yaml
# kubernetes deployment.yaml
volumes:
  - name: atomikos-log
    persistentVolumeClaim:
      claimName: atomikos-pvc  # EFS or EBS PVC

# application.properties:
# spring.jta.atomikos.transactions.log-base-dir=/mnt/efs/atomikos
```
**Prevention:** Persistent volume (PVC) for TM log is MANDATORY for JTA in Kubernetes. Not optional. Test recovery: crash pod, restart, verify pg_prepared_xacts is empty after restart.

**Failure Mode 2: XA Connection Pool Exhaustion from Long-Lived Prepared Transactions**

**Symptom:** Application connection pool exhausted. All connections in pool are "idle in transaction." No new transactions can start. Application health check fails. Root cause unclear — load seems normal.
**Root Cause:** Long-running xa_prepare calls + coordinator slowness. XA connections cannot be returned to pool while in PREPARED state — they are "checked out" until Phase 2 completes. If coordinator is slow (GC pause, network slowdown): many connections hold PREPARED state simultaneously, exhausting the pool.
**Diagnostic:**
```bash
# Check PostgreSQL for sessions in prepared state:
psql -c "
  SELECT pid, state, query_start, state_change, query
  FROM pg_stat_activity
  WHERE state = 'idle in transaction'
  ORDER BY state_change;"

# Check connection pool usage (Atomikos metrics):
# JMX: com.atomikos:type=Connection Pool for <resourceName>
# Attributes: PoolSize, AvailableSize, TotalConnections
# If AvailableSize = 0 and TotalConnections = PoolSize: exhausted

# Check Phase 2 completion latency:
grep "xa_commit\|xa_prepare" /var/log/app/app.log | \
  awk '/xa_prepare/{start=NR} /xa_commit/{print NR-start}' | \
  sort -n | tail -5
```
**Fix:**
BAD: Large pool (100 connections) masking slow Phase 2 completion.
GOOD: (1) Reduce xa_prepare → xa_commit latency (coordinator proximity to resources). (2) Set `connectionTimeout` in Atomikos pool to fail fast when pool exhausted. (3) Monitor Phase 2 latency as SLO.
**Prevention:** Alert when pool available < 20%. Alert when Phase 2 latency > P99 threshold. Capacity plan: pool size ≥ peak TPS × average Phase 2 duration.

**Failure Mode 3: Security - XID Replay Attack via Stolen XID**

**Symptom:** An attacker captures a valid XID (transaction ID) from network traffic. The attacker sends `xa_commit('stolen-xid')` directly to a database. The database, still holding resources in PREPARED state for that XID, commits the transaction — potentially committing a fraudulent transaction that the coordinator was about to abort.
**Root Cause:** XA interface accessible without authentication on the database network port. XID format is guessable (sequential or timestamp-based). Attacker can issue Phase 2 commands (xa_commit/xa_rollback) that the database will honor.
**Diagnostic:**
```bash
# Check if XA commands are logged in PostgreSQL audit:
psql -c "SHOW log_statements;"
# Should be 'all' or 'ddl' — COMMIT PREPARED must be logged

# Check for unexpected xa_commit from non-TM IPs:
grep "COMMIT PREPARED\|ROLLBACK PREPARED" \
  /var/log/postgresql/postgresql.log | \
  grep -v "<TM-IP-ADDRESS>"
# Any COMMIT PREPARED from unexpected IP = potential attack
```
**Fix:**
BAD: Database accessible from any IP on the network, no row-level TM permissions.
GOOD: (1) TLS + client certificates for database connections (only TM can connect). (2) Database `pg_hba.conf`: allow only TM IP to issue COMMIT PREPARED. (3) Use UUIDs for XIDs (not sequential or time-based). (4) PostgreSQL: `GRANT EXECUTE ON FUNCTION pg_prepared_xact_ids TO tm_role` — limit who can issue COMMIT PREPARED commands.
**Prevention:** Treat XA-participating databases as internal-only services. Firewall at the network level: only TM IPs can connect on the database port. Audit all COMMIT PREPARED / ROLLBACK PREPARED commands.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-033 - Two-Phase Commit (2PC) (the algorithm underlying XA — understand the protocol before the implementation)
- DST-032 - Failure Modes (XA handles crash-recovery failures — failure model determines XA's scope)

**Builds On This (learn these next):**
- DST-035 - Three-Phase Commit (3PC improvement over 2PC's blocking)

**Alternatives / Comparisons:**
- DST-033 - Two-Phase Commit (2PC) (algorithmic view of 2PC vs. this entry's practical/operational view)
- DST-035 - Three-Phase Commit (3PC as 2PC improvement)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | XA/JTA implementation of 2PC   |
|                  | with coordinator recovery log  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Multi-DB/queue atomic ops in   |
|                  | enterprise Java applications   |
+------------------+--------------------------------+
| KEY INSIGHT      | TM log durability = recovery   |
|                  | capability. Ephemeral log =    |
|                  | unrecoverable stuck transactions|
+------------------+--------------------------------+
| USE WHEN         | Legacy multi-datasource apps   |
|                  | requiring strict atomicity     |
+------------------+--------------------------------+
| AVOID WHEN       | Microservices, high-throughput |
|                  | systems, Kubernetes stateless  |
+------------------+--------------------------------+
| TRADE-OFF        | Atomic guarantees vs. latency, |
|                  | operational complexity, SPOF   |
+------------------+--------------------------------+
| ONE-LINER        | XA = standardized 2PC. Durable |
|                  | TM log = correct recovery.     |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-035 Three-Phase Commit,    |
|                  | DST-033 2PC algorithm          |
+------------------+--------------------------------+
```

**If you remember only 3 things:**
1. XA = standard interface for 2PC. xa_prepare → "vote YES". xa_commit/xa_rollback → Phase 2 decision. TM (Atomikos, Narayana) is the coordinator.
2. TM transaction log MUST be on durable persistent storage. Ephemeral storage = unrecoverable transactions on TM restart.
3. JTA + XA is not for microservices. Use Saga for cross-service eventual consistency. Use single-DB transactions wherever possible to avoid 2PC overhead.

**Interview one-liner:**
"XA is the standard protocol that implements 2PC across databases and message queues. The Java TM (Atomikos, Narayana) acts as the coordinator, calling xa_prepare on all enlisted resources, logging its decision to durable storage, then calling xa_commit or xa_rollback. The critical operational requirement: the TM log must survive restarts (persistent volume in Kubernetes) — without it, PREPARED transactions on resources are stuck indefinitely. For new microservice architectures, Saga patterns replace XA to avoid 2PC's coordinator SPOF and latency overhead."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The coordinator's transaction log is not a performance feature — it's a correctness requirement. Any protocol where a coordinator makes a decision that other participants must follow needs the coordinator to PERSIST that decision before broadcasting it. If the coordinator can be replaced (restart, failover): the persisted decision is how the replacement coordinator knows what to do. This "commit log" pattern appears everywhere: database WAL, Raft leader log, Kafka producer idempotency. The pattern: persist the decision, then broadcast; recovery means re-reading the log and re-broadcasting.

**Where else this pattern appears:**
- **Kafka producer exactly-once (transactional producer):** Kafka's transactional producer uses a 2PC-like protocol internally. The Kafka broker (coordinator) logs the transaction state (BEGIN, COMMIT, ABORT) for each transactional producer. On broker restart: the log is replayed to determine in-flight transaction outcomes. The producer ID (PID) + epoch is the XID. Exactly-once Kafka semantics are implemented via XA-like commit log persistence — the same pattern as JTA TM log durability.
- **Database point-in-time recovery (PITR):** A database's WAL (Write-Ahead Log) is the coordinator's transaction log applied to the database itself. On crash recovery: the WAL is replayed to determine which transactions committed before the crash (committed entries in WAL = xa_commit logged). Uncommitted entries are rolled back (not yet committed = xa_rollback). PITR = replaying the WAL up to a point in time, identical to TM log replay for in-doubt 2PC transactions.
- **Distributed saga orchestration log:** A Saga orchestrator maintains a log of which steps have been executed and which compensations have been triggered. This log serves the same role as the 2PC TM log: on orchestrator crash recovery, the log is replayed to determine which compensation actions still need to be triggered. Even Saga, the "alternative to 2PC," uses the same core pattern: persist decisions to a durable log, replay on recovery.

---

### 💡 The Surprising Truth

The XA standard (1991) was designed for mainframe and enterprise systems where the Transaction Manager was a single, highly reliable hardware appliance (IBM mainframe TM with redundant power, ECC memory, specialized hardware). The "coordinator SPOF" problem of 2PC was considered an engineering failure of the implementation (buy better hardware) rather than a protocol flaw. When XA moved to commodity servers in the JEE era (late 1990s-2000s): the hardware reliability assumption broke down. Commodity app servers crashed frequently. The "buy better hardware" solution became "build recovery software." The JTA recovery ecosystem (Narayana, Atomikos) is the result — sophisticated software that replaces the hardware reliability assumption with software durability (persistent logs + recovery replay). The surprising truth: 2PC's "blocking problem" was not considered a fundamental flaw in 1991 because it was expected to be solved by hardware reliability, not software algorithms. Thirty years later, the shift to cloud-native (ephemeral compute, commodity hardware) has finally made the blocking problem inescapable in practice — which is why Saga patterns (not 3PC) became the dominant alternative.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A microservice team wants to maintain strict atomicity between their PostgreSQL database and their Kafka topic (write to DB AND publish Kafka event atomically). Option A: Use JTA + XA (Atomikos + Kafka XA connector). Option B: Transactional Outbox Pattern (write event to an outbox table in same DB transaction, then async relay from outbox to Kafka). Compare: atomicity guarantees, latency, operational complexity, and failure modes for both options. Which would you recommend for a high-throughput service (10,000 TPS)?
*Hint:* Option A: True XA atomicity. Kafka XA connector exists but is complex and adds 2PC latency to every message. Kafka's XA support requires EOS (exactly-once semantics) producer. At 10,000 TPS: 2PC overhead of 20-50ms per transaction = major throughput impact. Option B: Outbox writes in same local DB transaction (no 2PC latency). Relay process runs async. At-least-once delivery to Kafka with idempotency deduplication at consumer. Eventual consistency (Kafka event may lag DB commit by milliseconds). For 10,000 TPS: outbox is significantly better throughput. Which failure modes does outbox introduce that XA does not have?

**Q2 (D - Root Cause):** A production Narayana JTA coordinator is logging slow Phase 2 completion: average xa_commit takes 45ms per resource. With 5 XA resources per transaction: 225ms for Phase 2. Database network latency is < 1ms. Application and databases are in the same datacenter. What are the top 3 root causes of 45ms xa_commit latency when network latency is negligible?
*Hint:* Cause A: xa_commit on each resource is called SEQUENTIALLY (not parallel). 5 resources × 5ms each = 25ms sequential. But if one resource is slow: it blocks all. Cause B: xa_commit triggers a fsync in the database (commit must be durable). fsync on a slow disk (rotational HDD, over-provisioned cloud IOPS) = 20-50ms. Fix: NVMe SSDs for database storage. Cause C: connection overhead. Each xa_commit uses the XA-enlisted connection — if connection is not reused efficiently: reconnection overhead per xa_commit. Which of these explains 45ms when network < 1ms?

**Q3 (A - System Interaction):** In Kubernetes, a Java application with JTA + Atomikos is deployed as a Deployment with `replicas: 3`. All three pods share the same PostgreSQL database. The team placed the Atomikos log on a local emptyDir volume. Describe EXACTLY what happens when: (1) Pod 1 starts a JTA transaction, (2) Pod 1 calls xa_prepare on the DB (gets YES), (3) Pod 1 crashes before xa_commit, (4) Pod 2 (already running) continues serving requests. Will Pod 2 recover Pod 1's transaction? What will happen to the stuck PREPARED transaction in PostgreSQL?
*Hint:* Pod 2 has its OWN Atomikos instance with its OWN log (local emptyDir). Pod 2's Atomikos has NO record of Pod 1's XID. Pod 2's recovery will NOT recover Pod 1's transaction. PostgreSQL will have a PREPARED transaction (XID from Pod 1) that no living Atomikos instance knows about. The PREPARED state holds locks indefinitely. Kubernetes may restart Pod 1 as a new pod (different node) with FRESH emptyDir log — also no recovery. DBA must manually ROLLBACK PREPARED the stuck transaction. How does moving the Atomikos log to a shared PersistentVolumeClaim fix this? What additional problem arises if all 3 pods share the SAME PVC with the SAME Atomikos log directory?


