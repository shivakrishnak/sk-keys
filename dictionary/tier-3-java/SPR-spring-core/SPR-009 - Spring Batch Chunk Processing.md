---
version: 2
layout: default
title: "Spring Batch Chunk Processing"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /spring/spring-batch-chunk-processing/
id: SPR-009
category: Spring Core
difficulty: ★★★
depends_on: Spring Batch ItemReader / ItemProcessor / ItemWriter, Spring Batch Job / Step / Tasklet
used_by: Spring Batch, Data Fundamentals
related: Transaction Management, Idempotency, Retry Pattern
tags:
  - java
  - spring
  - dataengineering
  - advanced
  - reliability
---

# SPR-009 - Spring Batch Chunk Processing

⚡ **TL;DR -** Chunk processing is the read-N-process-N-write-N-commit cycle that makes Spring Batch restartable, transactional, and memory-bounded for large-scale data processing.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Batch ItemReader / ItemProcessor / ItemWriter, Spring Batch Job / Step / Tasklet |
| **Used by** | Spring Batch, Data Fundamentals |
| **Related** | Transaction Management, Idempotency, Retry Pattern |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You write a batch job that reads 5 million records and writes them inside a single database transaction. For 4 hours everything seems fine. Then the database times out. The transaction rolls back - 5 million records, 4 hours of work, all lost. You start again from record 1.

**THE BREAKING POINT:** Two extremes exist for batch transactions: one transaction per record (safe but catastrophically slow - N commits for N records) or one transaction for all records (fast but catastrophic on failure - full rollback, no restart). Neither is acceptable for real workloads.

**THE INVENTION MOMENT:** The chunk model is the middle path: commit every N records (one transaction per N-record batch). If the job fails at record 5,000,001, the Job Repository records the last committed chunk at record 5,000,000. Restart resumes from record 5,000,001. Memory is bounded at N items, transaction cost is amortized over N records, and restart granularity is one chunk.

---

### 📘 Textbook Definition

**Spring Batch Chunk Processing** is the core execution model of a `ChunkOrientedTasklet`. It reads items one at a time from an `ItemReader`, optionally transforms them through an `ItemProcessor`, accumulates them into a buffer until the configured `commit-interval` (chunk size) is reached, then calls `ItemWriter.write(list)` and commits the transaction. This read-process-write-commit cycle repeats until the reader returns `null`. Skip and retry policies operate at the chunk boundary, and the `ExecutionContext` persists the reader's position after each commit for crash-safe restart.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Read N records, transform them, write them all in one transaction, commit, repeat.

> Imagine filling a shopping bag: you pick up items one at a time (read), check each for damage (process), and when the bag is full (chunk size), you place it on the conveyor and pay (write + commit). If the register breaks, you resume from the next full bag - not from the empty trolley.

**One insight:** The chunk size is the fundamental trade-off knob: larger chunks = higher throughput + higher rollback cost on failure; smaller chunks = lower throughput + finer restart granularity. There is no universally optimal chunk size - it must be tuned per workload.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **One transaction per chunk** - the write and commit are atomic; failure rolls back only the current chunk, not the entire job
2. **Restart resumes from last committed chunk offset** - the `ExecutionContext` stores the reader's position after each commit
3. **Chunk size bounds memory** - at most N items exist in the in-process buffer at any time
4. **Skip operates at item granularity within a chunk** - a single bad item triggers binary-search re-processing to isolate and skip it
5. **Retry operates at chunk granularity** - the entire write is retried up to `retryLimit` times before skip is attempted

**DERIVED DESIGN:**

The retry-then-skip cascade emerges from invariants 4 and 5: first try to make the whole chunk succeed (retry), and only if that fails repeatedly, narrow down to the individual bad item (skip via binary search). This minimizes the overhead of per-item re-processing on the common success path.

**THE TRADE-OFFS:**

**Gain:** Crash-safe processing; tunable throughput via chunk size; declarative skip/retry without custom error-handling code; memory-bounded processing regardless of dataset size.

**Cost:** Chunk size tuning is workload-specific and requires empirical measurement; transactions add latency overhead proportional to chunk count; skip's binary-search mechanism re-processes items up to log2(N) times, which matters for expensive processors.

---

### 🧪 Thought Experiment

**SETUP:** A chunk step with `commit-interval=1000` processes a 10,000-record dataset. Record 5,432 has a malformed value that causes a `DataIntegrityViolationException` when written to the database.

**WHAT HAPPENS WITHOUT skip/retry config:** The write of chunk 6 (records 5,001–6,000) fails. The whole chunk rolls back. The step fails. The job is marked FAILED. On restart, Spring Batch resumes from record 5,001 - but hits the same error again. The job never completes.

**WHAT HAPPENS WITH skip config (`.skip(DataIntegrityViolationException.class).skipLimit(10)`):** Chunk 6 write fails. Spring Batch retries the write (if `retryLimit > 0`). On exhausting retries, it triggers skip: chunks down to single-item re-processing via binary search. Item 5,432 is identified as the bad item, logged via `SkipListener`, excluded from the write. The remaining 999 items of the chunk are committed. Processing continues from record 6,001.

**THE INSIGHT:** Skip is the mechanism that converts "this job can never complete" into "this job completes with known exceptions." The binary search isolation ensures that one bad record doesn't silently poison an entire chunk - Spring Batch isolates it precisely.

---

### 🧠 Mental Model / Analogy

> An assembly line quality control process: workers process 50 items at a time (chunk). After processing, the tray goes to inspection (write + commit). If the whole tray fails inspection, the inspector examines items one by one to find the defective one, removes it, and approves the rest. A supervisor logs every rejected item. The line never stops for one bad item.

- **50-item tray** → chunk (commit-interval = 50)
- **Tray approval** → successful `write()` + TX commit
- **Tray rejection** → write failure, TX rollback
- **Per-item inspection** → skip's binary-search isolation
- **Defective item log** → `SkipListener.onSkipInWrite()`
- **Inspector retries** → `retryLimit` (try the full tray again before inspection)
- **Supervisor's logbook** → `ExecutionContext` (last approved tray number)

Where this analogy breaks down: Real inspection examines each item once; Spring Batch's binary search may process items multiple times (up to log2(N) passes) to isolate the bad one, which matters if item processing has side effects.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of saving one record at a time or saving everything at once, Spring Batch saves data in batches of N. If something goes wrong, you only lose the current batch and resume from the last successful save point.

**Level 2 - How to use it (junior developer):**
Set chunk size on the `StepBuilder`: `.<T,T>chunk(1000, transactionManager)`. Add `.faultTolerant()` then `.skipLimit(100).skip(SomeException.class)` for error tolerance. Add `.retryLimit(3).retry(TransientException.class)` for transient errors. That's the full chunk configuration for most production jobs.

**Level 3 - How it works (mid-level engineer):**
`ChunkOrientedTasklet.execute()` is called in a loop by `RepeatTemplate`. Each call: `ChunkProvider.provide()` calls `reader.read()` N times to fill a `Chunk<I>`; `ChunkProcessor.process(chunk)` calls `processor.process()` on each item, filtering nulls; then `writer.write(outputList)` is called inside the active `PlatformTransactionManager` transaction. On `write()` failure with retry configured, `RetryTemplate` re-invokes the write up to `retryLimit` times. On persistent failure, `FaultTolerantChunkProcessor` switches to single-item re-processing to binary-search for the skippable item. Each chunk commit calls `reader.update(executionContext)` to save the reader's position.

**Level 4 - Why it was designed this way (senior/staff):**
The binary-search skip implementation is a deliberate performance optimization. A naive skip would re-execute every item in the failed chunk one by one - O(N) re-processing. Binary search is O(log2 N) sub-chunk re-executions. For a chunk of 1,000 items, naive skip requires re-processing 1,000 items; binary search requires at most 10 sub-chunk executions. This matters when processors call expensive external services. The trade-off: binary search assumes processors are idempotent - re-processing the same item multiple times must be safe.

---

### ⚙️ How It Works (Mechanism)

```
[RepeatTemplate calls ChunkOrientedTasklet]
        │
        ▼
[TX BEGIN (PlatformTransactionManager)]
        │
        ▼
[ChunkProvider.provide()]
  ┌──────────────────────────────────────┐
  │ for i in 0..commitInterval:          │
  │   item = reader.read()               │
  │   if null → break                    │
  │   chunk.add(item)                    │
  └──────────────────────────────────────┘
        │
        ▼
[ChunkProcessor.process(chunk)]
  ┌──────────────────────────────────────┐
  │ for item in chunk:                   │
  │   out = processor.process(item)      │
  │   if out != null → outList.add(out)  │
  └──────────────────────────────────────┘
        │
        ▼
[writer.write(outList)]
  → success: TX COMMIT
  → failure: check retryLimit
        │
  ┌─────┴─────────────────────────────┐
  │ retryable? → retry up to N times  │
  │ retry exhausted / skippable?      │
  │ → binary search skip isolation    │
  │   → SkipListener.onSkipInWrite()  │
  │   → write remaining items         │
  │   → TX COMMIT                     │
  └───────────────────────────────────┘
        │
        ▼
[reader.update(executionContext)]
[ExecutionContext persisted to Job Repository]
        │
        ▼
[Loop: next chunk]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Step starts → StepExecution created]
      │ ← YOU ARE HERE
      ▼
[Chunk 1: read×1000 → process×1000 → write(~1000)]
  TX COMMIT → ExecutionContext: {lineCount: 1000}
      │
      ▼
[Chunk 2: read×1000 → process×1000 → write(~1000)]
  TX COMMIT → ExecutionContext: {lineCount: 2000}
      │
      ▼
[... repeat ...]
      │
      ▼
[Final chunk: read() returns null → partial chunk]
  TX COMMIT → StepExecution: COMPLETED
```

**FAILURE PATH:**
```
[Chunk 5: write() throws ConstraintViolationException]
      │
      ▼ [TX ROLLBACK]
[RetryTemplate: retry write (attempt 1/3) → still fails]
[RetryTemplate: retry write (attempt 2/3) → still fails]
[RetryTemplate: retry write (attempt 3/3) → still fails]
      │
      ▼ [Skip binary search activated]
[Sub-chunk [0..499]: write → FAIL → rollback]
[Sub-chunk [0..249]: write → OK → commit]
[Sub-chunk [250..499]: write → FAIL → rollback]
[Sub-chunk [250..374]: write → OK → commit]
[... binary search narrows to item 312 ...]
[Item 312: write → FAIL → SkipListener called]
[Remaining items: write → OK → commit]
[skipCount++ on StepExecution]
      │
      ▼ [Continue from chunk 6 if skipLimit not exceeded]
```

**WHAT CHANGES AT SCALE:**
For multi-threaded steps (`TaskExecutor` on the step), multiple `ChunkOrientedTasklet` instances run concurrently - each processing its own chunk in parallel. The `ItemReader` must be thread-safe (`SynchronizedItemStreamReader` wrapper or `JdbcPagingItemReader`). The `ItemWriter` must be thread-safe for concurrent writes. Skip/retry semantics per thread are independent. Chunk ordering is not guaranteed in multi-threaded mode - never use multi-threaded steps when output order matters.

---

### 💻 Code Example

**BAD - no fault tolerance, no chunk transaction control:**
```java
@Bean
public Step loadStep(
        JobRepository repo,
        PlatformTransactionManager tm,
        ItemReader<Customer> reader,
        ItemWriter<Customer> writer) {
    return new StepBuilder("loadStep", repo)
        .<Customer, Customer>chunk(10000, tm)  // too large
        .reader(reader)
        .writer(writer)
        // No faultTolerant → any error kills the step
        // No skip → one bad record aborts all 10M
        // No retry → transient DB error = permanent failure
        .build();
}
```

**GOOD - production-grade chunk step with full fault tolerance:**
```java
@Bean
public Step loadStep(
        JobRepository repo,
        PlatformTransactionManager tm,
        ItemReader<Customer> reader,
        ItemProcessor<Customer, Customer> processor,
        ItemWriter<Customer> writer,
        SkipListener<Customer, Customer> skipListener,
        ChunkListener chunkListener) {
    return new StepBuilder("loadStep", repo)
        .<Customer, Customer>chunk(1000, tm)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        // Skip: data errors are skipped with audit log
        .skipLimit(500)
        .skip(DataIntegrityViolationException.class)
        .skip(ValidationException.class)
        // Retry: transient errors retried with backoff
        .retryLimit(3)
        .retry(TransientDataAccessException.class)
        .retry(ResourceAccessException.class)
        // Never retry non-transient errors
        .noRetry(DataIntegrityViolationException.class)
        // Never rollback on skip-classified exceptions
        .noRollback(ValidationException.class)
        .listener(skipListener)
        .listener(chunkListener)
        .build();
}

// Skip audit: log and persist every skipped item
@Bean
public SkipListener<Customer, Customer> skipListener(
        DeadLetterRepository dlRepo) {
    return new SkipListener<>() {
        public void onSkipInRead(Throwable t) {
            log.warn("Read skip: {}", t.getMessage());
        }
        public void onSkipInProcess(
                Customer item, Throwable t) {
            log.warn("Process skip id={}", item.getId());
            dlRepo.save(item, "PROCESS", t.getMessage());
        }
        public void onSkipInWrite(
                Customer item, Throwable t) {
            log.warn("Write skip id={}", item.getId());
            dlRepo.save(item, "WRITE", t.getMessage());
        }
    };
}

// Chunk metrics: log chunk timing for performance tuning
@Bean
public ChunkListener chunkListener(
        MeterRegistry registry) {
    return new ChunkListener() {
        private long start;
        public void beforeChunk(ChunkContext ctx) {
            start = System.currentTimeMillis();
        }
        public void afterChunk(ChunkContext ctx) {
            long duration = System.currentTimeMillis() - start;
            registry.timer("batch.chunk.duration",
                "step", ctx.getStepContext().getStepName())
                .record(duration, TimeUnit.MILLISECONDS);
        }
        public void afterChunkError(ChunkContext ctx) {
            log.error("Chunk error in step: {}",
                ctx.getStepContext().getStepName());
        }
    };
}
```

---

### ⚖️ Comparison Table

| Chunk Size | Throughput | Memory Usage | Rollback Cost | Restart Granularity |
|---|---|---|---|---|
| 1 (record-by-record) | Very low | Minimal | Minimal | Per record |
| 100 | Low | Low | Low | Per 100 records |
| 1,000 | Good | Moderate | Moderate | Per 1,000 records |
| 10,000 | High | High | High | Per 10,000 records |
| Unbounded | Maximum | OOM risk | Full rerun | None |

| Fault Tolerance Option | When to Use | Trade-off |
|---|---|---|
| `skip` (data exception) | Bad records in input | Silently drops items; needs `SkipListener` |
| `retry` (transient exception) | DB timeouts, API flaps | Re-processes chunk N times; adds latency |
| `noRollback` | Non-TX exceptions | Commits despite exception; use carefully |
| `noRetry` | Permanent data errors | Fail-fast to skip, skip binary search |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Chunk size of 1 is the safest option" | It's the slowest - N transactions for N records. Restart granularity is per-record, but at the cost of N× commit overhead. |
| "Skip means the item is silently lost" | Skip triggers `SkipListener.onSkipInWrite/Process/Read()`. You are responsible for persisting skipped items in that listener for reconciliation. |
| "Retry retries individual items" | Retry retries the entire chunk write operation, not individual items. Only skip (via binary search) isolates individual items. |
| "faultTolerant() is always needed" | Only when you want skip or retry. For jobs where any error must abort the step, omit `faultTolerant()`. |
| "Multi-threaded steps are always faster" | Multi-threaded steps introduce thread-safety requirements on readers/writers, lose ordering guarantees, and complicate skip/retry. Profile first - often I/O is the bottleneck, not CPU. |
| "noRollback means the exception is ignored" | `noRollback(ExceptionClass.class)` tells Spring Batch not to mark the transaction for rollback when that exception occurs during write - the chunk is committed despite the exception. Use only for truly ignorable write errors. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Infinite retry loop - job never progresses**

**Symptom:** Step runs for hours; readCount stays at zero; no writes committed; CPU pegged.
**Root Cause:** A non-transient exception (e.g., `ConstraintViolationException`) is classified as retryable without a `noRetry` exclusion. Spring Batch retries the same failing chunk indefinitely until the process is killed.
**Diagnostic:**
```sql
-- Check StepExecution for write errors and zero progress
SELECT read_count, write_count, rollback_count,
       exit_message
FROM batch_step_execution
WHERE job_execution_id = ?;
-- rollback_count >> write_count indicates retry loop
```
**Fix:**
```java
.faultTolerant()
.retryLimit(3)
.retry(TransientDataAccessException.class)
// Explicitly exclude non-transient errors from retry
.noRetry(DataIntegrityViolationException.class)
.noRetry(ConstraintViolationException.class)
.skipLimit(100)
.skip(DataIntegrityViolationException.class)
```
**Prevention:** Always pair `retry()` with `noRetry()` for permanent data errors. Classify exceptions into transient (retry) and permanent (skip or fail) categories before configuring fault tolerance.

**Mode 2: Binary search skip causes `ItemProcessor` side effects**

**Symptom:** After a skip event, duplicate entries appear in an audit table or external system.
**Root Cause:** Spring Batch's binary-search skip re-processes items in the failed chunk multiple times. If the `ItemProcessor` writes to an audit log or calls an external API, those calls are made multiple times for items that are eventually written successfully.
**Diagnostic:**
```bash
# Enable Spring Batch debug logging to trace re-processing
logging.level.org.springframework.batch=DEBUG
# Look for repeated "Processing item" log lines for same ID
```
**Fix:**
```java
// Make ItemProcessor idempotent for re-processing
@Bean
public ItemProcessor<Customer, Customer> processor() {
    return item -> {
        // Use idempotency key to prevent duplicate audit
        if (!auditService.exists(item.getId())) {
            auditService.log(item);
        }
        return transform(item);
    };
}
```
**Prevention:** All `ItemProcessor` implementations in fault-tolerant steps must be idempotent - re-processing the same item N times must produce the same result with no duplicate side effects.

**Mode 3: Chunk performance degradation on large datasets**

**Symptom:** First 100 chunks process in 5 seconds each; after 500 chunks, each takes 30+ seconds.
**Root Cause:** `JdbcCursorItemReader` with an unbounded result set degrades as the JDBC cursor advances; or `JpaPagingItemReader` with dirty first-level cache growing over time.
**Diagnostic:**
```bash
# Monitor chunk duration via actuator metrics
curl http://localhost:8080/actuator/metrics/ \
  batch.chunk.duration?tag=step:loadStep

# Or add explicit timing in ChunkListener.afterChunk()
# and export to Prometheus / Grafana
```
**Fix:**
```java
// For JPA: clear EntityManager context after each chunk
@Bean
public ItemWriteListener<Customer> clearCacheListener(
        EntityManagerFactory emf) {
    return new ItemWriteListener<>() {
        public void afterWrite(List<? extends Customer> c) {
            emf.createEntityManager().clear();
        }
    };
}

// Or switch to JdbcPagingItemReader which avoids cursor
```
**Prevention:** Monitor `batch.chunk.duration` metric per step. Clear JPA first-level cache periodically. Prefer `JdbcPagingItemReader` over `JdbcCursorItemReader` for large tables.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Batch ItemReader / ItemProcessor / ItemWriter (2122) - the I/O interfaces that participate in chunk processing
- Spring Batch Job / Step / Tasklet (2121) - step configuration context

**Builds On This (learn these next):**
- Spring Batch (2120) - overview of partitioned step scale-out patterns
- Transaction Management - the underlying ACID semantics of chunk commits

**Alternatives / Comparisons:**
- Transaction Management - the Spring abstraction wrapping each chunk commit
- Idempotency - required property for processors in fault-tolerant chunk steps
- Retry Pattern - the Resilience4j/Spring Retry pattern underlying chunk retry semantics

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ Read-N-process-N-write-N-commit   │
│ PROBLEM      │ Safe, restartable bulk processing │
│ KEY INSIGHT  │ TX boundary = chunk, not job      │
│ USE WHEN     │ Any high-volume batch step        │
│ AVOID WHEN   │ Event-driven or streaming data    │
│ TRADE-OFF    │ Chunk size: throughput vs restart │
│ ONE-LINER    │ Fail one chunk → skip it → resume │
│ NEXT EXPLORE │ Spring Cloud Overview             │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(B - Scale)** You have a 10M-record chunk step with commit-interval=1000 and `retryLimit=3`. In the worst case (every chunk has one skippable item), how many total `write()` calls does Spring Batch make, and how does this affect your database write throughput calculation?

2. **(C - Design Trade-off)** `noRollback(SomeException.class)` allows committing a chunk even when a write throws that exception. Under what data consistency requirements would this be acceptable, and what compensating mechanism would you add to maintain audit integrity?

3. **(D - Root Cause)** A fault-tolerant step reports `rollback_count=450` but `skip_count=0` after processing 5M records. What does this combination tell you about the exception classification configuration, and what is likely happening in the retry/skip decision tree?
