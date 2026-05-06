---
layout: default
title: "Spring Batch ItemReader / ItemProcessor / ItemWriter"
parent: "Spring Core"
nav_order: 2122
permalink: /spring/spring-batch-reader-processor-writer/
number: "2122"
category: Spring Core
difficulty: ★★★
depends_on: Spring Batch Job / Step / Tasklet, Spring Batch
used_by: Spring Batch Chunk Processing
related: Strategy Pattern, Pipeline Pattern, ETL
tags:
  - java
  - spring
  - dataengineering
  - advanced
  - pattern
---

# 2122 — Spring Batch ItemReader / ItemProcessor / ItemWriter

⚡ **TL;DR —** Three Strategy-pattern interfaces that decouple data source reading, transformation logic, and output sink writing in a Spring Batch chunk step.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Batch Job / Step / Tasklet, Spring Batch |
| **Used by** | Spring Batch Chunk Processing |
| **Related** | Strategy Pattern, Pipeline Pattern, ETL |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your batch job reads from CSV, transforms records, and writes to a database — all in one method. Changing from CSV to XML input means rewriting the whole method. Swapping PostgreSQL for Oracle means touching transformation code. Unit-testing the enrichment logic requires spinning up a real database connection.

**THE BREAKING POINT:** Real-world batch pipelines need: swappable input sources per environment (file in dev, DB in prod), chainable transformation layers, independently testable business logic, and reusable I/O adapters across different jobs. A monolithic batch method makes none of this achievable without full rewrites.

**THE INVENTION MOMENT:** Spring Batch applies the **Strategy** and **Pipeline** patterns to batch I/O. `ItemReader<T>` is the source strategy; `ItemProcessor<I,O>` is the transform strategy; `ItemWriter<T>` is the sink strategy. Each is independently injectable, testable, and replaceable. The chunk loop wires them together without coupling them to each other.

---

### 📘 Textbook Definition

**`ItemReader<T>`** is a Spring Batch interface with a single method `T read()` that returns one item per call, or `null` to signal the data source is exhausted. **`ItemProcessor<I,O>`** transforms a single input item of type `I` to output type `O`, or returns `null` to filter the item from the pipeline. **`ItemWriter<T>`** receives a `List<T>` — the entire accumulated chunk — and writes all items in one call. Together they implement the **chunk-oriented pipeline**: read one, process one, accumulate N, write N as a batch.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Reader supplies items one at a time; Processor transforms each; Writer receives the full chunk at once.

> Think of a mail sorting facility: a conveyor belt (Reader) delivers one envelope at a time, a worker (Processor) re-labels each envelope, and a postbox (Writer) accepts the whole tray of re-labeled envelopes at once for bulk dispatch.

**One insight:** The asymmetry between reading/processing (one at a time) and writing (whole chunk at once) is intentional — it matches hardware reality: CPUs process sequentially, but I/O is efficient only in batches.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **`read()` returns one item or null** — null terminates the read loop; no null items are processed or written
2. **`process()` returning null filters the item** — it is silently removed from the output list; no error is raised
3. **`write()` receives the entire accumulated chunk** — enables JDBC batch inserts, not row-by-row round-trips
4. **`ItemStream` is for stateful readers/writers** — `open()`, `update()`, `close()` enable cursor position to be saved in `ExecutionContext` for restart
5. **`@StepScope` binds beans to the step execution** — enables late-binding of `JobParameters` into reader/writer configuration

**DERIVED DESIGN:**

The `write(List<T>)` signature is a deliberate performance decision. A naive design would call `write(T)` per item, requiring N database round-trips per chunk. Batching the list enables a single JDBC batch update statement — N inserts in one round-trip. The cost is that the writer receives a list it must buffer; for very large chunk sizes this increases memory pressure.

**THE TRADE-OFFS:**

**Gain:** Strategy pattern enables swapping I/O adapters without touching business logic; null-return filtering is a first-class mechanism requiring no separate filter step; batch write is the correct default for throughput.

**Cost:** `ItemProcessor` cannot depend on write success (write hasn't happened when process runs); `ItemWriter` receives a list that must fit in memory for the chosen chunk size; stateful readers must implement `ItemStream` or restarts produce duplicates.

---

### 🧪 Thought Experiment

**SETUP:** You're writing a job that reads 200,000 customer records from a CSV, validates each, enriches with a score, and writes valid enriched records to a database. Some records have missing email fields.

**WHAT HAPPENS WITHOUT ItemProcessor:** Your `ItemWriter` must validate and enrich each item before writing — mixing domain logic with persistence code. Changing validation rules requires modifying the writer. Testing validation requires a live database. The writer becomes a god class.

**WHAT HAPPENS WITH ItemProcessor:** The Processor validates and enriches each record, returning `null` for invalid ones (filtered automatically). The Writer receives only valid, enriched records and does pure persistence. Validation is unit-tested with a simple list — no database needed. The CSV Reader is swapped for a JDBC Reader with zero Writer changes.

**THE INSIGHT:** `ItemProcessor` is the dependency inversion point in the batch pipeline. It's where domain logic lives, isolated from I/O. The null-return contract is the framework's built-in filter mechanism — no `FilterItemProcessor` wrapper needed.

---

### 🧠 Mental Model / Analogy

> A water purification plant: raw water arrives one sample at a time (ItemReader delivers items), each sample passes through filtration (ItemProcessor transforms or rejects), and clean water is pumped into a storage tank in bulk (ItemWriter fills with the whole chunk).

- **Raw water tap** → ItemReader (file, DB, queue as data source)
- **Each water sample** → one item returned by `read()`
- **Filter membrane** → ItemProcessor (transform or null-reject)
- **Bulk tank fill** → ItemWriter (receives entire chunk at once)
- **Tank capacity** → commit-interval (chunk size before flush)
- **Purification log** → ExecutionContext (records last sample processed for restart)

Where this analogy breaks down: In a real plant, filtration is continuous and immediate. In Spring Batch, the processor runs per item but the writer only runs when the full chunk is assembled — so items sit in a buffer between processing and writing, meaning a writer failure rolls back all chunk items, not just the last one.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Reader fetches data one record at a time. Processor transforms or rejects each record. Writer saves a full group of records together in one batch operation. Three separated responsibilities.

**Level 2 — How to use it (junior developer):**
Implement each interface or use Spring Batch's built-in implementations. Wire them into a `StepBuilder.chunk()`. Use `@StepScope` when your reader/writer configuration depends on `JobParameters`. Use `FlatFileItemReader` for CSV, `JdbcCursorItemReader` or `JdbcPagingItemReader` for relational data, and `JdbcBatchItemWriter` for efficient bulk inserts.

**Level 3 — How it works (mid-level engineer):**
The chunk loop calls `reader.read()` repeatedly, building a `List<I>` until chunk size is reached or null is returned. It then iterates the list calling `processor.process(item)`, filtering out nulls, producing `List<O>`. Finally `writer.write(List<O>)` is called inside the active transaction — success commits, failure triggers skip/retry. Stateful readers implement `ItemStream`: `open(ctx)` restores cursor position from saved `ExecutionContext`; `update(ctx)` saves current position after each read; `close()` releases resources.

**Level 4 — Why it was designed this way (senior/staff):**
The `CompositeItemProcessor` pattern lets you chain multiple processors without framework changes — a `List<ItemProcessor>` is composed into a pipeline, each processor's output feeding the next. The decision to make `ItemProcessor` optional was deliberate: many ETL steps are pure load operations with no transformation, and forcing an identity processor adds call overhead for millions of records. The `ItemStream` separation from `ItemReader` follows the Interface Segregation Principle — not all readers need stateful lifecycle management; stateless API-backed readers should not be forced to implement unused methods.

---

### ⚙️ How It Works (Mechanism)

```
[ChunkOrientedTasklet.execute()]
        │
        ▼
[SimpleChunkProvider.provide(contribution)]
  loop until chunk size or null:
  ┌────────────────────────────────────┐
  │ item = itemReader.read()           │
  │ if item == null → break (done)     │
  │ if item != null → add to chunk     │
  └────────────────────────────────────┘
        │
        ▼
[SimpleChunkProcessor.process(chunk)]
  for each item in chunk:
  ┌────────────────────────────────────┐
  │ out = itemProcessor.process(item)  │
  │ if out != null → add to outList    │
  │ if out == null → filter (skip)     │
  └────────────────────────────────────┘
        │
        ▼
[itemWriter.write(outList)]
  → JDBC batch update / file flush / etc.
        │
        ▼
[TX COMMIT]
[itemReader.update(executionContext)]
[ExecutionContext persisted to Job Repository]
```

**Built-in ItemReaders:**
- `FlatFileItemReader` — CSV / fixed-width files with `LineMapper`
- `JdbcCursorItemReader` — single JDBC `ResultSet` cursor (holds one connection)
- `JdbcPagingItemReader` — paged SQL queries (safe for large tables, thread-safe)
- `JpaPagingItemReader` — JPA entity paging with `EntityManager`
- `StaxEventItemReader` — streaming XML with JAXB/XStream `Unmarshaller`
- `KafkaItemReader` — reads committed records from Kafka topic partitions

**Built-in ItemWriters:**
- `JdbcBatchItemWriter` — `NamedParameterJdbcTemplate` batch insert/update
- `FlatFileItemWriter` — CSV / fixed-width output files
- `JpaItemWriter` — `EntityManager.merge()` for each item in chunk
- `KafkaItemWriter` — batch produce to Kafka topic

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[FlatFileItemReader.open() — file handle opened]
      │ ← YOU ARE HERE
      ▼
[read() × 1000 → chunk of 1000 raw items]
      │
      ▼
[ItemProcessor: validate + enrich each item]
  15 items returned null → filtered out
  985 valid items in output list
      │
      ▼
[JdbcBatchItemWriter.write(985 items)]
  JDBC batch: INSERT ... (985 rows, 1 round-trip)
      │
      ▼
[TX COMMIT]
[ExecutionContext: {reader.lineCount: 1000} saved]
      │
      ▼
[Repeat until read() returns null]
[FlatFileItemReader.close() — file handle released]
```

**FAILURE PATH:**
```
[write() throws DataIntegrityViolationException]
      │
      ▼ [TX ROLLBACK — all 985 items not written]
[If .skip(DataIntegrityViolationException.class) set]
  → binary search: re-process items 1 by 1
  → item 412 causes violation → SKIP
  → retry remaining 984 items → COMMIT
[If no skip configured → StepExecution FAILED]
      │ (restart)
      ▼
[FlatFileItemReader.open() → restores lineCount=N000]
[Seeks to last committed position]
```

**WHAT CHANGES AT SCALE:**
`JdbcCursorItemReader` holds a single DB connection for the step's entire duration. For parallel multi-threaded steps, each thread needs its own reader instance. Use `@StepScope` to ensure Spring creates a new reader bean per `StepExecution`. For truly large tables (100M+ rows), use `JdbcPagingItemReader` which releases the connection between pages, keeping connection pool usage bounded.

---

### 💻 Code Example

**BAD — monolithic read-process-write in one class:**
```java
@Component
public class CustomerLoader {
    public void load(String csvPath) throws Exception {
        try (BufferedReader br =
                new BufferedReader(new FileReader(csvPath))) {
            String line;
            // Everything mixed: read, validate, enrich, write
            while ((line = br.readLine()) != null) {
                Customer c = parseLine(line);
                if (c.getEmail() == null) continue;
                c.setScore(scoreService.score(c));
                // Row-by-row: N separate DB round-trips
                jdbc.update("INSERT INTO customers ...", c);
                // No restart checkpoint — crash = full rerun
            }
        }
    }
}
```

**GOOD — separated Reader / Processor / Writer:**
```java
// READER — CSV with late-bound file path from JobParams
@Bean
@StepScope
public FlatFileItemReader<RawCustomer> customerReader(
        @Value("#{jobParameters['input.file']}") String path) {
    return new FlatFileItemReaderBuilder<RawCustomer>()
        .name("customerReader")
        .resource(new FileSystemResource(path))
        .delimited().delimiter(",")
        .names("id", "name", "email", "country")
        .targetType(RawCustomer.class)
        .linesToSkip(1)   // skip header row
        .build();
}

// PROCESSOR — validate + enrich; null = filter out
@Bean
public ItemProcessor<RawCustomer, Customer> processor(
        ScoreService scoreService) {
    return raw -> {
        if (raw.getEmail() == null
                || raw.getEmail().isBlank()) {
            return null;  // filtered — won't reach writer
        }
        Customer c = new Customer();
        c.setId(raw.getId());
        c.setName(raw.getName());
        c.setEmail(raw.getEmail().toLowerCase());
        c.setScore(scoreService.score(raw));
        return c;
    };
}

// COMPOSITE PROCESSOR — chain validate → map → enrich
@Bean
public CompositeItemProcessor<RawCustomer, Customer>
        compositeProcessor(
        ItemProcessor<RawCustomer, RawCustomer> validator,
        ItemProcessor<RawCustomer, Customer> mapper,
        ItemProcessor<Customer, Customer> enricher) {
    var proc = new CompositeItemProcessor<
        RawCustomer, Customer>();
    proc.setDelegates(List.of(validator, mapper, enricher));
    return proc;
}

// WRITER — JDBC batch insert (1 round-trip per chunk)
@Bean
public JdbcBatchItemWriter<Customer> customerWriter(
        DataSource ds) {
    return new JdbcBatchItemWriterBuilder<Customer>()
        .dataSource(ds)
        .sql("INSERT INTO customers " +
             "(id, name, email, score) " +
             "VALUES (:id, :name, :email, :score)")
        .beanMapped()
        .assertUpdates(true)
        .build();
}
```

---

### ⚖️ Comparison Table

| Built-in Reader | Data Source | Restart Support | Key Consideration |
|---|---|---|---|
| `FlatFileItemReader` | CSV / fixed-width | Yes (line count) | Header/footer skip; delimiter config |
| `JdbcCursorItemReader` | JDBC ResultSet | Yes (WHERE offset) | Holds DB connection entire step |
| `JdbcPagingItemReader` | JDBC paged query | Yes (page tracking) | Thread-safe; preferred for large tables |
| `JpaPagingItemReader` | JPA entity | Yes | EntityManager per page; JPA overhead |
| `StaxEventItemReader` | XML streaming | Yes (event count) | JAXB/XStream required |
| `KafkaItemReader` | Kafka topic | Yes (partition offset) | Manual offset commit |

| Built-in Writer | Target | Batch Support | Key Consideration |
|---|---|---|---|
| `JdbcBatchItemWriter` | JDBC | Yes — batch update | Best throughput; `assertUpdates` |
| `FlatFileItemWriter` | File | Yes — line buffer | Append vs overwrite mode |
| `JpaItemWriter` | JPA entity | Via flush | `EntityManager.merge()` per item |
| `KafkaItemWriter` | Kafka | Yes — batch produce | Async by default |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`ItemProcessor` is mandatory" | It's optional. Many steps use only Reader + Writer for pure load operations with no transformation. |
| "Returning `null` from `process()` causes an error" | Null is the filter contract — the item is silently excluded from the writer's list. This is the intended way to filter records. |
| "`JdbcCursorItemReader` is always better than paging" | Cursor holds a DB connection for the step's full duration, consuming a pool slot. Paging acquires/releases connections per page — safer for long-running steps. |
| "All built-in readers are thread-safe" | Most readers (cursor, file) are NOT thread-safe. Use `SynchronizedItemStreamReader` or `@StepScope` with partitioned steps. |
| "`ItemWriter` receives items one at a time" | No — `write(List<T>)` receives the entire chunk. This is the key performance design enabling bulk insert rather than row-by-row inserts. |
| "Custom readers don't need `ItemStream`" | If your reader has any state (file position, DB cursor, page index), you must implement `ItemStream` or restart will reprocess from the beginning. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Reader not restarting from correct position**

**Symptom:** After job restart, records are duplicated in the target database.
**Root Cause:** Custom `ItemReader` doesn't implement `ItemStream` — cursor position is never saved to `ExecutionContext`, so restart always reads from the beginning.
**Diagnostic:**
```sql
-- Check if any reader state keys exist in context
SELECT short_context
FROM batch_step_execution_context
WHERE step_execution_id = ?;
-- If no reader.* keys present, ItemStream not implemented
```
**Fix:**
```java
public class MyReader<T>
        implements ItemReader<T>, ItemStream {
    private int currentIndex = 0;
    private static final String INDEX_KEY = "reader.index";

    @Override
    public void open(ExecutionContext ctx) {
        if (ctx.containsKey(INDEX_KEY)) {
            currentIndex = ctx.getInt(INDEX_KEY);
            // Seek data source to currentIndex
        }
    }
    @Override
    public void update(ExecutionContext ctx) {
        ctx.putInt(INDEX_KEY, currentIndex);
    }
    @Override
    public void close() { /* release resources */ }
}
```
**Prevention:** Any stateful custom reader must implement `ItemStream`. Wrap in `SynchronizedItemStreamReader` for multi-threaded steps.

**Mode 2: Connection pool exhaustion from `CursorItemReader`**

**Symptom:** `HikariPool - Connection is not available` after running several concurrent batch steps.
**Root Cause:** Each `JdbcCursorItemReader` holds a JDBC connection for the entire step. With N concurrent steps, N connections are permanently occupied.
**Diagnostic:**
```bash
# Monitor active connections during job execution
curl http://localhost:8080/actuator/metrics/ \
  hikaricp.connections.active
```
**Fix:**
```java
// Switch to paging reader — acquires/releases per page
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
**Prevention:** Use `JdbcPagingItemReader` for steps running longer than 30 seconds or in concurrent execution contexts.

**Mode 3: `assertUpdates` fails on upsert / idempotent inserts**

**Symptom:** `EmptyResultDataAccessException: Item 0 of 1 did not update any rows` on `JdbcBatchItemWriter`.
**Root Cause:** `assertUpdates(true)` is the default. An `INSERT ... ON CONFLICT DO NOTHING` that finds an existing row updates 0 rows — triggering the assertion even though the intent is idempotent.
**Diagnostic:**
```properties
# Enable SQL debug logging to inspect actual statements
logging.level.org.springframework.jdbc.core=DEBUG
```
**Fix:**
```java
return new JdbcBatchItemWriterBuilder<Customer>()
    .sql("INSERT INTO customers (id, name, score) " +
         "VALUES (:id, :name, :score) " +
         "ON CONFLICT (id) DO UPDATE " +
         "SET score = EXCLUDED.score")
    .assertUpdates(false)   // allow 0-row "no-op" updates
    .dataSource(ds)
    .beanMapped()
    .build();
```
**Prevention:** Disable `assertUpdates` for upsert / idempotent patterns; keep enabled for strict insert-only writers to detect missing rows early.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Batch (2120) — framework overview and chunk model architecture
- Spring Batch Job / Step / Tasklet (2121) — how steps are configured and executed

**Builds On This (learn these next):**
- Spring Batch Chunk Processing (2123) — how Reader/Processor/Writer are orchestrated with transactions, skip, and retry

**Alternatives / Comparisons:**
- Strategy Pattern — the design pattern underlying Reader/Processor/Writer interfaces
- Pipeline Pattern — the architectural pattern for chaining ItemProcessors
- ETL — the broader Extract-Transform-Load category that Spring Batch implements

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Strategy interfaces for batch I/O  │
│ PROBLEM      │ Decouple source, logic, and sink   │
│ KEY INSIGHT  │ write() receives the full chunk    │
│ USE WHEN     │ Any chunk-oriented batch step      │
│ AVOID WHEN   │ Single-record event processing     │
│ TRADE-OFF    │ Stateful readers need ItemStream   │
│ ONE-LINER    │ read()×N → process()×N → write(N) │
│ NEXT EXPLORE │ Spring Batch Chunk Processing      │
└────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A — System Interaction)** A `JdbcCursorItemReader` is used in a multi-threaded step with a `TaskExecutor` running 4 threads. What failure mode will you encounter, and what are the two approaches Spring Batch provides to make reading thread-safe?

2. **(C — Design Trade-off)** Your `ItemProcessor` calls a REST API with 50ms average latency per record. With chunk size 1,000 and single-threaded processing, total API overhead per chunk is ~50 seconds. How would you redesign the processor to batch API calls and what contract changes would be required?

3. **(E — First Principles)** `ItemWriter` receives `List<T>` rather than `T`. If you need a writer that must fail-fast on the first error (never batch), how does this conflict with the chunk commit model, and what alternative step design would you use?
