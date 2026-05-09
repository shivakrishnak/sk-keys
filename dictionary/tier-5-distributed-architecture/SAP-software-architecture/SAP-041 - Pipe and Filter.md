---
id: SAP-041
title: Pipe and Filter
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-043, SAP-050
used_by:
related: SAP-040, SAP-042
tags:
  - architecture
  - pattern
  - deep-dive
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /software-architecture/pipe-and-filter/
  - advanced
---

# SAP-041 - Pipe and Filter

⚡ TL;DR - Pipe and Filter decomposes processing into a sequence of independent, single-responsibility transformation steps (filters) connected by data channels (pipes) - each filter reads from its input pipe and writes to its output pipe, enabling composable, testable, and parallelizable data processing.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-043, SAP-050 |
| **Used by**    | -                |
| **Related**    | SAP-040, SAP-042 |

---

### 🔥 The Problem This Solves

**THE PROCESSING CHAIN PROBLEM:**
An image processing service needs to: resize, convert to greyscale, apply sharpening, add watermark, compress, and upload. Written as a single method, this is a 200-line function with deeply nested logic. Hard to test each step independently. Impossible to reorder steps. Can't parallelize steps. Can't reuse the watermark step in another pipeline.

**THE PIPE AND FILTER SOLUTION:**
Each processing step is an independent filter: `ResizeFilter`, `GreyscaleFilter`, `SharpenFilter`, `WatermarkFilter`, `CompressFilter`, `UploadFilter`. Each filter does one thing and passes its output to the next. Assemble the pipeline by connecting filters with pipes. Test each filter in isolation. Reorder steps by reconnecting pipes. Reuse filters in different pipelines. Parallelize independent filters.

**EVOLUTION:**
Ken Thompson invented Unix pipes in 1973, creating the physical manifestation of Pipe and Filter: `cat file | grep pattern | sort | uniq`. Douglas McIlroy's Unix philosophy - "write programs that do one thing and do it well; write programs that work together" - IS the Pipe and Filter pattern stated as a design philosophy. Buschmann et al. documented it formally in "Pattern-Oriented Software Architecture" (POSA, 1996). Java 8 Streams (2014) brought Pipe and Filter to in-process OOP as `stream().filter().map().collect()`. Apache Kafka Streams (2016) and Flink/Spark brought the pattern to distributed event processing at scale.

---

### 📘 Textbook Definition

Pipe and Filter is an architectural pattern that structures a system as a series of processing steps (filters) connected by data channels (pipes). Each filter is an independent processing component that: receives data from an input pipe, transforms or filters the data, and emits the result to an output pipe. Filters are stateless (or have isolated state) and know nothing about upstream or downstream filters. Pipes are connectors that carry data between filters - they may be in-memory queues, message queues, streams, or files. The pattern was formalized in POSA (Pattern-Oriented Software Architecture, Buschmann et al., 1996) and is the architectural model behind Unix pipelines, compiler passes, ETL systems, and modern stream processing frameworks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data flows through independent transformation stages connected by channels - each stage reads, transforms, and writes; none know about each other.

**One analogy:**

> A water treatment plant. Raw water enters a series of treatment chambers: screening, coagulation, sedimentation, filtration, disinfection, pH adjustment. Each chamber (filter) does one thing. The water (data) flows between chambers through pipes. Each treatment stage is independent - you can add, remove, or replace a stage without redesigning the whole plant. The output of each stage is the input to the next.

**One insight:**
Unix pipes are the most famous example: `cat log.txt | grep ERROR | cut -d' ' -f3 | sort | uniq -c | sort -rn`. Each command is a filter; `|` is the pipe. You composed powerful processing from simple, single-purpose tools. Pipe and Filter brings this composability to application architecture.

---

### 🔩 First Principles Explanation

**PIPE AND FILTER COMPONENTS:**

```
┌──────────────────────────────────────────────────────────┐
│         PIPE AND FILTER - COMPONENTS                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  FILTER (processing component):                          │
│    - Has exactly one input and one output (typically)    │
│    - Processes incrementally or in bulk                  │
│    - Self-contained: no knowledge of other filters       │
│    - Stateless (preferred) or isolated state             │
│    - Example: parse, validate, transform, enrich         │
│                                                          │
│  PIPE (data channel):                                    │
│    - Connects one filter's output to next filter's input │
│    - Buffering: decouples producer/consumer speeds       │
│    - Types: in-memory queue, file, socket, Kafka topic   │
│    - Passive: carries data, no transformation            │
│                                                          │
│  DATA SOURCE (origin):                                   │
│    - Produces data for the first filter                  │
│    - Example: file reader, HTTP request, Kafka consumer  │
│                                                          │
│  DATA SINK (terminus):                                   │
│    - Consumes output of last filter                      │
│    - Example: database writer, HTTP response, S3 upload  │
└──────────────────────────────────────────────────────────┘
```

**FILTER TOPOLOGY OPTIONS:**

```
┌──────────────────────────────────────────────────────────┐
│           PIPELINE TOPOLOGY VARIANTS                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Linear pipeline:                                        │
│    A → B → C → D → Sink                                 │
│    Sequential, all data flows through all stages         │
│                                                          │
│  Fan-out (split):                                        │
│    A → B → [C, D] → E (merge)                           │
│    Parallel branches, recombined downstream              │
│                                                          │
│  Conditional routing:                                    │
│    A → Router → B (if condition X)                       │
│              → C (if condition Y)                        │
│    Different filters for different data types            │
│                                                          │
│  Feedback loop:                                          │
│    A → B → C → [done OR retry → A]                      │
│    Retry failed items by feeding back to start           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**COMPILER AS PIPE AND FILTER:**
A compiler is a textbook Pipe and Filter system:

```
Source Code
    → Lexer (tokenize: characters → tokens)
    → Parser (tokens → AST)
    → Semantic Analyzer (AST → typed AST)
    → Optimizer (typed AST → optimized AST)
    → Code Generator (optimized AST → bytecode/assembly)
    → Bytecode output
```

Each pass is a filter. The intermediate representation is the pipe (data). Each pass can be tested independently. New optimization passes can be inserted without changing other passes. This is not a design coincidence - compiler writers have been using Pipe and Filter since the 1960s.

---

### 🧠 Mental Model / Analogy

> Pipe and Filter is like an assembly line that processes information instead of physical goods. Each workstation (filter) on the assembly line does one specialized operation. The conveyor belt (pipe) carries work items between stations. No workstation knows what the previous or next station does. Stations can run at different speeds (buffering handles rate mismatch). Stations can be reorganized or replaced without redesigning the whole line.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Processing broken into independent steps connected in sequence. Each step does one thing. Data flows from step to step through channels.

**Level 2 - How to build one (junior):**
Define a `Filter<I, O>` interface with a `process(I input): O` method. Implement each transformation step as a class implementing this interface. Build a `Pipeline` that holds an ordered list of filters and runs them in sequence. Pass the output of each filter as input to the next.

**Level 3 - Asynchronous pipelines (mid-level):**
For high-throughput pipelines, use asynchronous processing with buffered pipes (queues) between filters. Each filter runs in its own thread (or thread pool). The queue between filters decouples producer and consumer speeds - fast upstream filters don't block on slow downstream filters. Back-pressure: if the downstream queue is full, block the upstream filter until there's capacity. Java implementations: `ExecutorService` + `BlockingQueue`, Project Loom virtual threads, Reactive Streams (RxJava, Project Reactor) with built-in backpressure.

**Level 4 - Distributed pipelines (senior/staff):**
Distributed Pipe and Filter uses message queues (Kafka, RabbitMQ, SQS) as the pipes and separate microservices as the filters. Apache Kafka Streams, Apache Flink, and Apache Spark Structured Streaming are distributed Pipe and Filter frameworks. Design considerations: 1) Exactly-once semantics - ensure each record is processed exactly once even with retries (idempotent filters + transactional messaging). 2) Checkpoint/restart - maintain processing state between stages so failures can be resumed from last checkpoint. 3) Ordering guarantees - parallel filters may deliver results out of order; use sequence numbers or event timestamps to reorder. 4) Dead-letter queues - messages that fail after N retries go to a DLQ for investigation, not infinite retry loops.

---

### ⚙️ How It Works (Mechanism)

**Synchronous pipeline execution:**

```
┌──────────────────────────────────────────────────────────┐
│      PIPELINE EXECUTION - SYNC (IN PROCESS)             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  input  → Filter1 → pipe1 → Filter2 → pipe2 → output    │
│                                                          │
│  Execution model (push):                                 │
│    1. Source produces item                               │
│    2. Filter1.process(item) → result1                    │
│    3. Filter2.process(result1) → result2                 │
│    4. Sink.consume(result2)                              │
│    5. Repeat for next item                               │
│                                                          │
│  Execution model (pull/streaming):                       │
│    - Downstream filter requests data from upstream       │
│    - Used in Java Streams, Python generators             │
│    - Lazy evaluation: only process what downstream needs │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**ETL pipeline example:**

```
┌──────────────────────────────────────────────────────────┐
│    ETL PIPELINE - PIPE AND FILTER IN PRACTICE            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  CSV File Source                                         │
│       ↓ raw lines                                        │
│  CsvParseFilter       (string → CsvRecord)               │
│       ↓ CsvRecord                                        │
│  ValidationFilter     (reject invalid records → DLQ)    │
│       ↓ valid CsvRecord                                  │
│  NormalizationFilter  (lowercase, trim, standardize)     │
│       ↓ NormalizedRecord                                 │
│  EnrichmentFilter     (lookup zip → city, state)         │
│       ↓ EnrichedRecord                                   │
│  TransformFilter      (CsvRecord → DatabaseRow)          │
│       ↓ DatabaseRow                                      │
│  DeduplicationFilter  (skip if already in DB)            │
│       ↓ new DatabaseRow                                  │
│  BatchInsertSink      (bulk insert to database)          │
│                                                          │
│  Each filter: independently testable                     │
│  Each filter: independently replaceable                  │
│  Each filter: independently parallelizable               │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Generic pipeline builder:**

```java
// Filter interface - the building block
@FunctionalInterface
public interface Filter<I, O> {
    O process(I input);

    // Compose: this filter then next filter
    default <R> Filter<I, R> then(Filter<O, R> next) {
        return input -> next.process(this.process(input));
    }
}

// Concrete filters - each does ONE thing
public class ParseFilter implements Filter<String, CsvRecord> {
    @Override
    public CsvRecord process(String line) {
        return CsvRecord.parse(line);
    }
}

public class ValidateFilter
        implements Filter<CsvRecord, CsvRecord> {
    @Override
    public CsvRecord process(CsvRecord record) {
        if (!record.hasRequiredFields()) {
            throw new InvalidRecordException(record);
        }
        return record;
    }
}

public class NormalizeFilter
        implements Filter<CsvRecord, CsvRecord> {
    @Override
    public CsvRecord process(CsvRecord record) {
        return record.withNormalizedFields();
    }
}

// Compose pipeline using then()
Filter<String, CsvRecord> pipeline =
    new ParseFilter()
        .then(new ValidateFilter())
        .then(new NormalizeFilter());

// Process data through pipeline
List<CsvRecord> results = rawLines.stream()
    .map(pipeline::process)
    .collect(toList());
```

---

### ⚖️ Comparison Table

| Pattern                 | Step awareness   | Composability | State sharing      | Best for                     |
| ----------------------- | ---------------- | ------------- | ------------------ | ---------------------------- |
| **Pipe and Filter**     | None (blind)     | High          | None               | Data transformation chains   |
| Chain of Responsibility | Next handler     | Medium        | None               | Request handling, middleware |
| Decorator               | Wraps known type | Medium        | Shared wrapped obj | Layered behaviour            |
| Strategy                | Caller chooses   | Low           | None               | Interchangeable algorithms   |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Pipe and Filter = sequential only                        | Filters can run in parallel (fan-out) or be pipelined (async stages)                                                |
| Filters must be stateless                                | Filters can have local state (e.g., deduplication cache) as long as state is isolated to the filter                 |
| Pipe and Filter = low throughput (sequential bottleneck) | Async pipelines with buffered pipes allow stages to run at their natural throughput; parallel filters scale further |
| Only for batch processing                                | Used in real-time stream processing (Kafka Streams, Flink) - processes events as they arrive                        |

---

### 🚨 Failure Modes & Diagnosis

**Slow filter bottleneck**

**Symptom:** Upstream filters are idle; downstream filters are backlogged. Pipeline throughput equals the slowest filter's throughput.

**Root Cause:** Pipeline stages are synchronous; fast upstream filters block waiting for the slow filter.

**Fix:** Identify the bottleneck filter. Options: a) Parallelize the slow filter (run multiple instances). b) Optimize the slow filter. c) Cache expensive lookups in the enrichment filter. d) Switch to async pipeline model with bounded queue between stages.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Decompose complex processing into independent, single-responsibility stages connected by well-defined data contracts. Each stage is testable in isolation, recomposable into different sequences, and replaceable without affecting other stages.

**Where else this pattern appears:**

- **Industrial assembly lines:** Henry Ford's assembly line is Pipe and Filter at industrial scale - each worker (filter) adds one component, then the car (data) moves to the next worker. No worker knows what the previous or next worker does.
- **Compilers:** Lexer → Parser → Semantic Analysis → Optimization → Code Generation. Each compiler stage transforms the data representation (tokens → AST → annotated AST → IR → machine code). Classic Pipe and Filter.
- **Unix shell pipelines:** `cat access.log | grep 404 | awk '{print $7}' | sort | uniq -c | sort -rn | head -20`. Each program reads stdin, transforms, writes stdout. Programs don't know about each other - only the data format (text lines) matters.

---

### 💡 The Surprising Truth

The Pipe and Filter pattern trades flexibility for order-dependency. Filters must agree on their data contracts - what comes in and what goes out. When a filter changes its output format, every downstream filter breaks. This is exactly the same coupling problem that Pipe and Filter supposedly solves (it decouples the LOGIC of each stage, but couples the DATA FORMAT between stages). The mature solution is to make the data flowing through pipes a "schema-versioned" Published Language - the same DDD pattern that governs API evolution. Unix pipes solved this by making the data format "text lines" (maximally simple and stable). Apache Kafka Avro/Protobuf solves it for distributed pipelines with schema evolution.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-043 - SOLID Principles (specifically SRP: each filter has one responsibility; OCP: new processing stages are added as new filters, not by modifying existing ones)
- SAP-050 - Cohesion (each filter should be highly cohesive - one transformation only; understanding cohesion explains why filters should be small)

**Builds On This (learn these next):**

- SAP-040 - Plugin Architecture (filters are often implemented as plugins to a pipeline framework; the framework defines the filter interface, implementations are plugins)
- SAP-042 - Blackboard Pattern (an alternative for non-sequential, opportunistic processing; contrasting with Pipe and Filter clarifies when order matters versus when it doesn't)

**Alternatives / Comparisons:**

- SAP-042 - Blackboard Pattern (for problems where processing order is not predetermined and specialists activate opportunistically based on available data)
- Chain of Responsibility design pattern (similar chain structure but for request handling with optional pass-through; filters always transform, chain of responsibility may stop processing)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Processing = chain of independent        │
│              │ filters connected by data pipes          │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Each filter blind to others;             │
│              │ knows only its input and output types    │
├──────────────┼───────────────────────────────────────────┤
│ UNIX EXAMPLE │ cat f | grep X | sort | uniq             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-stage data processing, ETL,        │
│              │ compilers, stream processing             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Water treatment plant: each chamber     │
│              │  does one purification step"              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing an order fraud detection pipeline: Parse → ValidateSchema → EnrichWithCustomerHistory → ScoreRisk → RouteHighRisk → Persist. The `EnrichWithCustomerHistory` filter calls an external customer service (50ms latency). At 1,000 events/second, this enrichment step is the bottleneck. Describe three different strategies to increase the pipeline's throughput, and what trade-offs each introduces.

_Hint:_ Research (1) Parallel filter execution: run `EnrichWithCustomerHistory` in a thread pool so multiple enrichments happen concurrently; trade-off: increased memory pressure and latency variance. (2) Async filter with Reactive Streams: use `CompletableFuture` or Project Reactor to make the enrichment non-blocking; trade-off: complexity of backpressure handling. (3) Pre-fetching/batching: batch multiple records and call `getCustomerHistoryBatch()` once; trade-off: increases latency per record but reduces I/O overhead. Also research Apache Kafka Streams's `asyncProcessorSupplier` for handling async external calls in streaming pipelines.

**Q2.** Your ETL pipeline has a `DeduplicationFilter` that checks if a record already exists in a Redis cache. For this filter to work correctly across restarts, the deduplication state must survive application restarts. But if the Redis cache grows without bound, it becomes a memory problem. How do you design the deduplication filter to be: a) durable across restarts, b) bounded in memory, and c) still eventually correct (no duplicates) over a sliding time window?

_Hint:_ Research Redis's TTL (Time To Live) feature for key expiry - specifically setting a TTL of N hours on each deduplication key. Records seen in the last N hours are deduplicated; records older than N hours may be re-processed (acceptable if the source system doesn't resend old records after N hours). Research Bloom filters as an alternative: probabilistic data structure with bounded memory that has no false negatives (never misses a duplicate) but accepts a small false positive rate (may flag unique records as duplicates).

**Q3.** A financial transactions processing pipeline has 7 filters. A regulatory requirement now mandates that every transaction must be audited with: (1) a record of the input to each filter, (2) the output from each filter, and (3) which filter version processed it. How do you add audit logging to all 7 filters without modifying any of the existing filter implementations?

_Hint:_ Research the "Decorator" design pattern applied to pipeline filters - specifically wrapping each filter in an `AuditingFilterDecorator` that (1) captures the input, (2) calls the wrapped filter, (3) captures the output, (4) writes both to an audit store, then passes the output to the next filter. The decorator is transparent to the pipeline framework - it implements the same filter interface as the wrapped filter. Research how Spring's `HandlerInterceptor` and Servlet Filters implement this pattern for HTTP request auditing.
