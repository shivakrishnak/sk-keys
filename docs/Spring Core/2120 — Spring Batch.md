---
layout: default
title: "Spring Batch"
parent: "Spring Core"
nav_order: 2120
permalink: /spring/spring-batch/
number: "2120"
category: Spring Core
difficulty: ★★★
depends_on: Spring Core, Spring Boot, JDBC
used_by: ETL, Data Fundamentals, CI-CD
related: Spring Batch Job / Step / Tasklet, Quartz Scheduler, AWS Step Functions
tags:
  - java
  - spring
  - dataengineering
  - advanced
  - production
---

# 2120 — Spring Batch

⚡ **TL;DR —** Spring Batch is a framework for building robust, restartable batch jobs that read, process, and write large datasets with transactional integrity.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Core, Spring Boot, JDBC |
| **Used by** | ETL, Data Fundamentals, CI-CD |
| **Related** | Spring Batch Job / Step / Tasklet, Quartz Scheduler, AWS Step Functions |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You need to process 10 million customer records nightly — migrate them, enrich them, and write them to a data warehouse. You write a simple `while` loop with JDBC. It runs for 6 hours. On hour 5, the database connection drops. You start over. Four nights later, you still haven't completed the job successfully.

**THE BREAKING POINT:** Enterprise batch processing demands more than a script. You need: restartability (resume from failure point), transaction management per chunk, skip-and-log bad records, parallel partitioning across threads, and an auditable job execution history. None of this exists in plain Java loops.

**THE INVENTION MOMENT:** Spring Batch (born from a 2007 collaboration between SpringSource and Accenture) codified the **chunk-oriented processing model** — read N records, process them, write them in one transaction, commit, repeat. If the job fails at record 50,001, restart from record 50,001. Job metadata is persisted in a **Job Repository** database so crashes are fully recoverable.

---

### 📘 Textbook Definition

**Spring Batch** is a lightweight, comprehensive batch processing framework for Java. It provides reusable components for reading, transforming, and writing large volumes of data with: chunk-oriented processing, skip/retry policies, restart/resume capability, parallel and partitioned step execution, and a persistent Job Repository for execution metadata. It follows the Batch Application Reference Architecture aligned with JSR-352 and is widely adopted in enterprise Java ETL and data pipeline engineering.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring Batch turns bulk data processing into restartable, transactional, auditable pipelines.

> Imagine a factory assembly line with a supervisor keeping a logbook. Every 100 items processed get a stamp. If the line breaks, you restart exactly at the last stamp — not from the beginning.

**One insight:** Spring Batch's key innovation is that **the transaction boundary is the chunk, not the job**. This makes terabyte-scale processing feasible because you never hold the whole dataset in memory or in a single database transaction.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Read one, process one, accumulate N, write N** — the chunk contract is immutable
2. **Every chunk is one database transaction** — commit on success, rollback on failure
3. **Job Repository is the single source of truth** — execution state lives in DB, never in memory
4. **Jobs are idempotent by JobParameters** — the same job with same parameters cannot run twice simultaneously
5. **Steps are sequential or conditional** — control flow is explicit and declared, not inferred

**DERIVED DESIGN:**

The chunk model follows from these invariants. If each write is transactional (invariant 2) and state is persisted after each commit (invariant 3), then crash recovery is simply querying the Job Repository for the last committed offset and resuming from there — no custom recovery logic needed.

**THE TRADE-OFFS:**

**Gain:** Crash-safe processing with no re-processing of committed chunks; auditable execution history; declarative skip/retry logic; built-in parallelism primitives; separation of I/O from business logic.

**Cost:** Requires a relational database for the Job Repository (30+ schema tables); adds infrastructure complexity; chunk-oriented model doesn't fit streaming or event-driven problems; startup overhead makes Spring Batch overkill for fewer than 1,000 records.

---

### 🧪 Thought Experiment

**SETUP:** You have a nightly job that reads 5 million rows from Oracle, enriches each row via a REST API call, and writes results to PostgreSQL. The job runs for 3 hours.

**WHAT HAPPENS WITHOUT SPRING BATCH:** At 2h 47m, the PostgreSQL connection pool exhausts. Your job dies. You have no record of how far it got. The next night you run it again from scratch — 3 hours wasted, data potentially duplicated, angry DBAs.

**WHAT HAPPENS WITH SPRING BATCH:** The Job Repository records every 1,000-record chunk commit. At 2h 47m, the job fails at chunk 9,872. The next night, Spring Batch queries the Job Repository: last committed chunk = 9,871,000 rows processed. It resumes from row 9,871,001. Total recovery processing time: 13 minutes.

**THE INSIGHT:** Spring Batch converts a stateless loop into a stateful, checkpointed pipeline. The Job Repository is the checkpoint journal. The business logic doesn't change — the framework adds recoverability as infrastructure.

---

### 🧠 Mental Model / Analogy

> Imagine a bank's overnight cheque-clearing process. Thousands of cheques arrive in batches. Tellers process 100 cheques at a time, stamping each completed batch in the ledger. If a teller gets sick mid-shift, the supervisor sees exactly which stamp is last and assigns a fresh teller to continue from there. No cheque is processed twice; no cheque is skipped.

- **Bank ledger** → Job Repository (persistent execution state)
- **Batch of 100 cheques** → Chunk (commit-interval)
- **Teller** → ItemProcessor (transforms each item)
- **Incoming cheque pile** → ItemReader data source
- **Accounting system update** → ItemWriter
- **Shift supervisor** → JobLauncher + JobOperator

Where this analogy breaks down: A real teller stamps each ledger entry immediately per cheque. Spring Batch's reader and processor work record-by-record, but the *write* is batched — the whole tray is dispatched at once rather than one-by-one.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Spring Batch is a tool that processes massive amounts of data in an organized, resumable way — like an assembly line that keeps a diary so it can pick up exactly where it left off if something goes wrong.

**Level 2 — How to use it (junior developer):**
Annotate a class `@Configuration`, define a `Job` bean with one or more `Step` beans. Each step either runs a `Tasklet` (arbitrary code) or uses chunk-oriented processing with `ItemReader`, optional `ItemProcessor`, and `ItemWriter`. Add `spring-boot-starter-batch` and a datasource — Spring Boot auto-configures the Job Repository schema.

**Level 3 — How it works (mid-level engineer):**
When a Job launches, Spring Batch creates a `JobExecution` row in the repository. Each Step creates a `StepExecution`. In chunk mode, the step reads items one at a time into a `Chunk` buffer until `commit-interval` is reached, then calls `ItemProcessor` on each item, then passes the whole list to `ItemWriter.write()`. This runs inside a `PlatformTransactionManager` transaction — success commits, failure triggers skip/retry logic. The `ExecutionContext` stores cursor positions so restarts seek to the last committed offset automatically.

**Level 4 — Why it was designed this way (senior/staff):**
The chunk model is a deliberate middle path between streaming and bulk. Streaming (record-by-record transactions) is safe but destroys throughput due to per-record commit overhead. Unbounded transactions (all-at-once) are fast but non-restartable and risk OOM. The chunk model amortizes transaction overhead over N records, bounds memory to chunk size, and sets restart granularity at one chunk. The Job Repository design externalizes state intentionally — it decouples batch runtime from process lifecycle, enabling multi-JVM deployments, remote partitioning, and external monitoring without changing any business logic.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│            JobLauncher                  │
│  launch(job, params) → JobExecution     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│                Job                      │
│  ┌────────┐  ┌────────┐  ┌──────────┐  │
│  │ Step 1 │→ │ Step 2 │→ │ Step 3   │  │
│  └───┬────┘  └────────┘  └──────────┘  │
└──────┼──────────────────────────────────┘
       │ (Chunk Step internals)
       ▼
┌──────────────────────────────────────┐
│  ItemReader.read() → item            │
│  (loop N times)                      │
│  ItemProcessor.process(item) → item  │
│  (after N items)                     │
│  ItemWriter.write(List<item>)        │
│  └── TX Commit ─────────────────┘   │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│          Job Repository              │
│  JobInstance · JobExecution          │
│  StepExecution · ExecutionContext    │
└──────────────────────────────────────┘
```

**Key components:**
- `JobRepository` — persists all execution metadata in a relational DB
- `JobLauncher` — creates `JobExecution`, invokes the job
- `JobInstance` — unique combination of Job name + `JobParameters`
- `JobExecution` — one run attempt; multiple per instance on retry
- `StepExecution` — per-step record with read/write/skip counts
- `ExecutionContext` — key-value state bag serialized to DB per chunk commit

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Scheduler / cron trigger]
      │
      ▼
[JobLauncher.run(job, params)]
      │ creates JobInstance (or finds existing)
      ▼
[JobRepository] ← YOU ARE HERE
      │ persists JobExecution (STARTED)
      ▼
[Step 1 begins → StepExecution STARTED]
      │
      ▼
[Chunk loop: read×N → process×N → write(N)]
  → TX COMMIT → StepExecution counts updated
      │
      ▼ (loop until read() returns null)
[Step 1 StepExecution: COMPLETED]
      │
      ▼
[Step 2 ... Step N]
      │
      ▼
[JobExecution: COMPLETED]
```

**FAILURE PATH:**
```
[Chunk N — write() throws exception]
      │
      ▼ (skip policy checked)
[If retryable → retry up to maxRetry times]
      │
      ▼ (if skip limit not exceeded)
[Item skipped → SkipListener notified]
      │
      ▼ (if skip limit exceeded)
[StepExecution FAILED → JobExecution FAILED]
      │ (next launch with same JobParameters)
      ▼
[JobRepository: existing failed execution found]
[Step 1: COMPLETED → SKIP]
[Step 2: resume from last committed chunk offset]
```

**WHAT CHANGES AT SCALE:**
Single-threaded chunk processing becomes a bottleneck at millions of records. Three scale-out strategies: (1) **Multi-threaded step** — `TaskExecutor` on the step runs chunks in parallel threads within the same JVM; (2) **Partitioned step** — `Partitioner` splits the dataset into non-overlapping ranges, each run as a separate `StepExecution` on a remote worker; (3) **Remote chunking** — the manager JVM reads items and sends them to distributed worker JVMs via a message queue. Partitioned steps are the most common pattern for database-backed jobs.

---

### 💻 Code Example

**BAD — naive batch without Spring Batch:**
```java
// No restart, no chunk transactions, no skip logic
@Scheduled(cron = "0 0 1 * * ?")
public void processCustomers() {
    // OOM risk: loads all 10M records at once
    List<Customer> all = jdbc.query(
        "SELECT * FROM customers", customerMapper);
    for (Customer c : all) {
        Customer enriched = restApi.enrich(c);
        // Row-by-row insert: N round-trips to DB
        jdbc.update("INSERT INTO enriched ...", enriched);
        // One giant transaction — restart = full rerun
    }
}
```

**GOOD — Spring Batch chunk-oriented job:**
```java
@Configuration
@EnableBatchProcessing
public class CustomerJobConfig {

    @Bean
    public Job customerJob(
            JobRepository repo, Step enrichStep) {
        return new JobBuilder("customerJob", repo)
            .start(enrichStep)
            .build();
    }

    @Bean
    public Step enrichStep(
            JobRepository repo,
            PlatformTransactionManager tm,
            ItemReader<Customer> reader,
            ItemProcessor<Customer, Customer> processor,
            ItemWriter<Customer> writer) {
        return new StepBuilder("enrichStep", repo)
            .<Customer, Customer>chunk(1000, tm)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            .skipLimit(500)
            .skip(DataAccessException.class)
            .retryLimit(3)
            .retry(RestClientException.class)
            .build();
    }

    // @StepScope = new instance per StepExecution
    @Bean
    @StepScope
    public JdbcCursorItemReader<Customer> reader(
            DataSource ds) {
        return new JdbcCursorItemReaderBuilder<Customer>()
            .name("customerReader")
            .dataSource(ds)
            .sql("SELECT * FROM customers ORDER BY id")
            .rowMapper(new BeanPropertyRowMapper<>(
                Customer.class))
            .build();
    }

    @Bean
    public ItemProcessor<Customer, Customer> processor(
            EnrichmentService svc) {
        return customer -> svc.enrich(customer);
    }

    @Bean
    public JdbcBatchItemWriter<Customer> writer(
            DataSource ds) {
        return new JdbcBatchItemWriterBuilder<Customer>()
            .sql("INSERT INTO enriched_customers " +
                 "VALUES (:id, :name, :score)")
            .dataSource(ds)
            .beanMapped()
            .build();
    }
}
```

**application.yml:**
```yaml
spring:
  batch:
    job:
      enabled: false      # don't auto-run on startup
    jdbc:
      initialize-schema: always
  datasource:
    url: jdbc:postgresql://localhost/batchdb
    hikari:
      maximum-pool-size: 10
```

---

### ⚖️ Comparison Table

| Feature | Spring Batch | Quartz Scheduler | AWS Step Functions | Apache Spark |
|---|---|---|---|---|
| **Primary purpose** | Batch ETL/processing | Job scheduling | Workflow orchestration | Distributed compute |
| **Restart/resume** | Built-in (Job Repository) | Manual | Built-in | Manual |
| **Chunk processing** | Native | None | None | RDD partitions |
| **Transaction mgmt** | Per-chunk, declarative | Per-job | N/A (managed) | None built-in |
| **Skip/retry** | Declarative | None | State machine retry | Manual |
| **Scale model** | Partitioned steps | Clustered triggers | Parallel states | Executor cluster |
| **Monitoring** | Spring Batch Admin / Actuator | Quartz Web UI | CloudWatch Console | Spark UI |
| **Best for** | JVM ETL pipelines | Triggering jobs | Multi-service flows | Petabyte analytics |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Spring Batch is a scheduler" | Spring Batch executes jobs — it doesn't schedule them. Pair it with Quartz, Spring `@Scheduled`, or a cron trigger. |
| "The same job cannot run twice" | `JobInstance` = job name + parameters. Different parameters (e.g., different date) = new instance that can run. Same parameters = same instance that can only COMPLETE once. |
| "Bigger chunks are always faster" | Larger chunks reduce commit overhead but increase rollback cost on failure and memory pressure. 100–1,000 is typical; tune empirically. |
| "Spring Batch requires XML config" | XML was the original style. Java `@Configuration` builders have been standard since Spring Batch 3.x. XML is still supported but discouraged in new projects. |
| "ItemProcessor is mandatory" | It's optional. A Reader → Writer step with no transformation is completely valid and common for pure load operations. |
| "Spring Batch only reads databases" | Built-in readers cover flat files (CSV/fixed-width), XML, JSON, JPA, MongoDB, AMQP, Kafka, and any custom `ItemReader` implementation. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Job silently completes without processing records**

**Symptom:** `JobLauncher.run()` returns immediately; no records processed; no errors.
**Root Cause:** `spring.batch.job.enabled=true` (default) caused the job to run on application startup with empty `JobParameters`. A previous run with the same empty parameters already COMPLETED — Spring Batch prevents re-running a completed `JobInstance`.
**Diagnostic:**
```sql
SELECT job_instance_id, status, exit_code, create_time
FROM batch_job_execution
WHERE job_name = 'customerJob'
ORDER BY create_time DESC
LIMIT 5;
```
**Fix:**
```java
// BAD: same empty params → same JobInstance → no-op
jobLauncher.run(job, new JobParameters());

// GOOD: unique param → new JobInstance every run
jobLauncher.run(job, new JobParametersBuilder()
    .addLong("run.id", System.currentTimeMillis())
    .toJobParameters());
```
**Prevention:** Always add a timestamp or run-ID parameter; set `spring.batch.job.enabled=false`.

**Mode 2: OutOfMemoryError during chunk read phase**

**Symptom:** JVM crashes with OOME during the read phase on large tables.
**Root Cause:** `JdbcCursorItemReader` fetches the full ResultSet into the JDBC driver buffer on some drivers (e.g., MySQL without `useCursorFetch`), or chunk size is set too large.
**Diagnostic:**
```bash
# Capture heap histogram during job run
jmap -histo:live <pid> | head -30
# Look for large byte[] or ResultSet wrapper instances
```
**Fix:**
```java
// Switch to paged reader for safe memory-bounded reads
return new JdbcPagingItemReaderBuilder<Customer>()
    .name("customerReader")
    .dataSource(ds)
    .selectClause("SELECT *")
    .fromClause("FROM customers")
    .sortKeys(Map.of("id", Order.ASCENDING))
    .pageSize(1000)
    .rowMapper(new BeanPropertyRowMapper<>(Customer.class))
    .build();
```
**Prevention:** Use `JdbcPagingItemReader` for large tables; tune `fetchSize` on cursor readers; monitor heap during initial sizing.

**Mode 3: Skip limit exceeded — job aborts with no audit trail**

**Symptom:** Job FAILED with `SkipLimitExceededException` after processing 40% of records; no log showing which records were bad.
**Root Cause:** A non-zero `skipLimit` was configured without a `SkipListener` — bad records are silently dropped until the limit is hit, then the job fails.
**Diagnostic:**
```sql
SELECT skip_count, read_count, write_count, status
FROM batch_step_execution
WHERE step_name = 'enrichStep'
ORDER BY start_time DESC
LIMIT 1;
```
**Fix:**
```java
.faultTolerant()
.skipLimit(1000)
.skip(Exception.class)
.listener(new SkipListener<Customer, Customer>() {
    public void onSkipInRead(Throwable t) {
        log.error("Read skip: {}", t.getMessage());
    }
    public void onSkipInProcess(Customer i, Throwable t) {
        log.error("Process skip id={}: {}", i.getId(), t);
    }
    public void onSkipInWrite(Customer i, Throwable t) {
        log.error("Write skip id={}: {}", i.getId(), t);
        deadLetterRepo.save(i, t.getMessage());
    }
})
```
**Prevention:** Always attach a `SkipListener` when using fault tolerance; persist skipped items to a dead-letter table for later reprocessing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Core — IoC, DI, `@Configuration`, bean lifecycle
- Spring Boot — auto-configuration, datasource setup
- JDBC — cursors, paging queries, batch updates

**Builds On This (learn these next):**
- Spring Batch Job / Step / Tasklet (2121) — the building blocks inside a batch job
- Spring Batch ItemReader / ItemProcessor / ItemWriter (2122) — the I/O contracts
- Spring Batch Chunk Processing (2123) — the core execution model deep dive

**Alternatives / Comparisons:**
- Quartz Scheduler — scheduling trigger for batch jobs; not a processing framework
- AWS Step Functions — managed workflow orchestration; no chunk processing
- Apache Spark — distributed analytics compute; not a batch ETL framework

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ Chunk-oriented batch framework    │
│ PROBLEM      │ Restartable, auditable ETL        │
│ KEY INSIGHT  │ Transaction boundary = chunk      │
│ USE WHEN     │ >100K records; restart required   │
│ AVOID WHEN   │ <1K records or event-driven work  │
│ TRADE-OFF    │ Job Repository DB required        │
│ ONE-LINER    │ Read N → Process N → Write N → TX │
│ NEXT EXPLORE │ Spring Batch Job / Step / Tasklet │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(B — Scale)** Your Spring Batch job processes 50M rows single-threaded in 8 hours but must complete in 1 hour. What are the three scale-out strategies available in Spring Batch, and what are the ordering and idempotency guarantees each provides?

2. **(C — Design Trade-off)** The Job Repository requires a relational database, adding operational overhead. Under what circumstances would you accept this overhead versus implementing a lightweight custom checkpoint store, and what would you lose by doing so?

3. **(D — Root Cause)** A Spring Batch job ran successfully yesterday and today `JobLauncher.run()` returns immediately without executing any steps. What are the two most likely root causes and how would you diagnose each using the Job Repository schema?
