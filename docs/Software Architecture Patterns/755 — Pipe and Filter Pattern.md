---
layout: default
title: "Pipe and Filter Pattern"
parent: "Software Architecture Patterns"
nav_order: 755
permalink: /software-architecture/pipe-and-filter-pattern/
number: "755"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Plugin Architecture, Functional Programming, Stream Processing"
used_by: "Data pipelines, ETL, Compiler design, Stream Processing, CI-CD"
tags: #advanced, #architecture, #data-pipeline, #functional, #streaming
---

# 755 — Pipe and Filter Pattern

`#advanced` `#architecture` `#data-pipeline` `#functional` `#streaming`

⚡ TL;DR — **Pipe and Filter** structures a processing system as a sequence of independent **filters** (each transforms data) connected by **pipes** (data channels) — enabling composable, reusable processing stages where each filter is unaware of its neighbors and can be reordered, replaced, or parallelized independently.

| #755            | Category: Software Architecture Patterns                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Plugin Architecture, Functional Programming, Stream Processing |                 |
| **Used by:**    | Data pipelines, ETL, Compiler design, Stream Processing, CI-CD |                 |

---

### 📘 Textbook Definition

**Pipe and Filter** (POSA Vol. 1 — "Pattern-Oriented Software Architecture," Buschmann et al., 1996): a data flow architectural pattern in which a system is decomposed into a series of **filters** (processing steps), each of which: reads input from a pipe, transforms it, and writes output to a pipe. Filters are independent: each knows only its own transformation, not its source or sink. Pipes carry data between filters: buffers, channels, queues, or in-memory streams. Properties: filters are independently reusable and composable; the pipeline can be reconfigured without changing filters; filters can be parallelized (multiple instances of the same filter); filters can be distributed (data flows over network pipes). Classical implementation: Unix shell pipelines (`cat file | grep error | sort | uniq -c`). Modern equivalents: Java Streams, Apache Kafka Streams, Apache Beam, CI/CD pipeline stages, compiler phases (lexer → parser → AST → optimizer → code generator).

---

### 🟢 Simple Definition (Easy)

An assembly line for water. Raw water enters → Filter 1: remove large particles → Filter 2: add chlorine → Filter 3: remove chemicals → Filter 4: add minerals → Pure drinking water exits. Each filter does one thing. The filters don't know about each other: "particle filter" doesn't know that "mineral filter" comes after it. Swap out one filter without touching the others. Add a new filter step: insert it between two pipes.

---

### 🔵 Simple Definition (Elaborated)

A log processing pipeline: raw log files → Filter 1: parse log format (text → structured LogEntry) → Filter 2: filter by severity (keep ERROR and WARN only) → Filter 3: enrich with hostname from IP → Filter 4: deduplicate within 5-second windows → Filter 5: format as JSON → output to Elasticsearch. Each filter: a single, testable transformation. The parse filter doesn't know about deduplication. The deduplication filter doesn't know about JSON formatting. Reconfigure: insert a new "mask PII" filter between enrich and deduplicate. The other filters are untouched.

---

### 🔩 First Principles Explanation

**The composability principle and filter design:**

```
FILTER CONTRACT:

  A filter is a function: Input → Output

  Properties a filter must have:
  1. Single responsibility: one transformation only.
  2. Stateless (ideally): output depends only on current input.
     (Stateful filters exist but complicate parallelism and reorder safety.)
  3. Black box: no knowledge of preceding or following filters.
  4. Consistent interface: output type matches next filter's expected input type.

  interface Filter<IN, OUT> {
      OUT process(IN input);
      // Or for streaming:
      Flux<OUT> process(Flux<IN> input);
  }

  A pipe is just the channel between filters:
    In Unix: stdout → stdin (OS pipe, character stream)
    In Java: java.util.stream.Stream<T>
    In reactive: Flux<T> / Observable<T>
    In async: Kafka topic, RabbitMQ queue, in-memory BlockingQueue

COMPOSITION MODELS:

  1. SEQUENTIAL (simple pipeline):

     Data → [F1] → [F2] → [F3] → Result

     F1 → F2 → F3 run in order. Each waits for previous to finish.
     Synchronous: simple, debuggable.

  2. PARALLEL (fan-out / fan-in):

     Data → [Splitter] → [F2a] → [Merger] → Result
                       → [F2b] →
                       → [F2c] →

     Splitter distributes work across parallel filter instances.
     Merger collects and combines results.
     Use: CPU-bound transformations that don't have ordering dependencies.

  3. STREAMING (continuous, unbounded input):

     ─────────────────────────────────────────────────►  (continuous stream)
     Events → [Parse] → [Filter] → [Enrich] → [Sink]

     Each filter processes events as they arrive. No batch boundary.
     Kafka Streams, Flink, Spark Streaming, RxJava.

  4. PULL vs. PUSH:

     PUSH: upstream filter pushes data to downstream filter when ready.
           Reactive streams (Flux): upstream pushes events, downstream backpressures.

     PULL: downstream filter pulls data from upstream when ready to process.
           Iterator pattern: downstream controls pace.

     Java Stream API: pull-based (terminal operation triggers evaluation).
     Reactive (Project Reactor): push with backpressure signaling.

FILTER CATEGORIES:

  1. TRANSFORMER: changes structure/format of data.
     Example: TextParser converts String → LogEntry

  2. FILTER (in the narrow sense): selects/rejects items.
     Example: SeverityFilter keeps only ERROR records

  3. ENRICHER: adds data to the record.
     Example: IPEnricher adds hostname field from IP

  4. SPLITTER: one record → many records (fan-out).
     Example: OrderLineSplitter: one Order → N OrderLine records

  5. AGGREGATOR: many records → one record (fan-in / window).
     Example: WindowAggregator: 5-second window of events → summary

  6. SINK: terminal filter; writes to external system.
     Example: ElasticsearchSink writes final records to ES

  7. SOURCE: entry filter; reads from external system.
     Example: KafkaSource reads events from Kafka topic

BACKPRESSURE (critical for streaming):

  If Filter 1 produces 10,000 records/sec and Filter 3 can only process 1,000/sec:

  Without backpressure: Pipe between F2 and F3 fills → OutOfMemoryError.

  Backpressure: F3 signals "I can only accept 1,000/sec" upstream.
  F2 slows down. F1 slows down. System operates at the rate of the slowest filter.

  Reactive Streams specification (Java): defines standard backpressure protocol.
  Project Reactor Flux, RxJava, Akka Streams all implement it.

UNIX PIPE ANATOMY:

  cat access.log | grep "ERROR" | awk '{print $5}' | sort | uniq -c | sort -rn

  Filter 1: cat  — SOURCE: reads file, writes to stdout
  Pipe:    |     — OS pipe, buffers data between processes
  Filter 2: grep — FILTER: only lines containing "ERROR"
  Pipe:    |
  Filter 3: awk  — TRANSFORMER: extract field 5 (IP address)
  Pipe:    |
  Filter 4: sort — SORTER: alphabetical sort for dedup preparation
  Pipe:    |
  Filter 5: uniq -c — AGGREGATOR: count duplicate lines
  Pipe:    |
  Filter 6: sort -rn — SORTER: numerical sort descending (most frequent first)

  Each Unix command: knows only stdin and stdout. No knowledge of neighbors.
  Replace any step: pipeline still works.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Pipe and Filter:

- One large `processLogs()` method: 300 lines handling parsing + filtering + enrichment + output — impossible to test steps independently
- Change one step: risk breaking others (all interleaved)

WITH Pipe and Filter:
→ Each filter: a small, independently testable unit
→ Reconfigure pipeline: reorder, add, remove filters without touching others
→ Parallelize the slow filter without changing adjacent filters

---

### 🧠 Mental Model / Analogy

> A car assembly line. Station 1: weld the chassis. Station 2: install engine. Station 3: install electrical. Station 4: paint. Station 5: install interior. Station 6: quality check. Each station (filter) does one job. The conveyor belt (pipe) moves the car between stations. Station 3 doesn't know what Station 1 did. Add a new step (install sunroof): insert a new station between 3 and 4. The other stations are unchanged. Speed up painting: add parallel painting stations without changing welding or quality check.

"Assembly line station" = filter (one transformation)
"Conveyor belt" = pipe (data channel between filters)
"Car moving between stations" = data flowing through the pipeline
"Parallel painting stations" = parallelizing a slow filter (fan-out/fan-in)

---

### ⚙️ How It Works (Mechanism)

```
PIPELINE ASSEMBLY:

  // Builder pattern for assembling a pipeline:
  Pipeline<String, ProcessedEvent> pipeline = Pipeline
      .source(kafkaSource)              // Filter 1: SOURCE
      .then(new LogParser())            // Filter 2: TRANSFORMER
      .then(new SeverityFilter("ERROR"))// Filter 3: FILTER
      .then(new IPEnricher(geoIpSvc))  // Filter 4: ENRICHER
      .then(new PIIMasker())            // Filter 5: TRANSFORMER
      .then(new JsonFormatter())        // Filter 6: TRANSFORMER
      .sink(elasticsearchSink);         // Filter 7: SINK

  pipeline.start();

  DATA FLOW:

  Kafka → "ERROR 2024-01-15 10:23:45 192.168.1.100 Payment failed"
       ↓ (parse)
       LogEntry{level=ERROR, timestamp=..., ip="192.168.1.100", msg="Payment failed"}
       ↓ (severity filter — passes ERROR)
       LogEntry{...}
       ↓ (enrich: 192.168.1.100 → hostname="payment-svc-3")
       LogEntry{..., hostname="payment-svc-3"}
       ↓ (mask PII — payment details masked)
       LogEntry{..., msg="Payment [MASKED]"}
       ↓ (format as JSON)
       {"level":"ERROR","hostname":"payment-svc-3","msg":"Payment [MASKED]",...}
       ↓
       Elasticsearch
```

---

### 🔄 How It Connects (Mini-Map)

```
Raw data input (logs, events, records, bytes)
        │
        ▼ (each transformation stage)
Pipe and Filter Pattern ◄──── (you are here)
(independent filters connected by pipes, composable processing stages)
        │
        ├── Stream Processing: Pipe and Filter at scale (Kafka Streams, Flink, Spark)
        ├── ETL (Extract-Transform-Load): classic pipe and filter: source → transform → sink
        ├── CI-CD Pipeline: each stage is a filter (build → test → scan → deploy)
        ├── Compiler: lexer → parser → semantic analysis → optimizer → code generator
        └── Reactive Programming: Flux/Observable operators ARE pipe-and-filter
```

---

### 💻 Code Example

```java
// Java Streams IS pipe-and-filter (pull-based, in-memory):
List<String> topErrors = Files.lines(Paths.get("app.log"))       // SOURCE
    .filter(line -> line.contains("ERROR"))                        // FILTER
    .map(LogParser::parse)                                         // TRANSFORMER
    .filter(entry -> entry.timestamp().isAfter(oneHourAgo))       // FILTER
    .map(LogEntry::message)                                        // TRANSFORMER
    .distinct()                                                    // AGGREGATOR (dedup)
    .limit(10)                                                     // FILTER (cap)
    .collect(Collectors.toList());                                 // SINK

// ────────────────────────────────────────────────────────────────────

// Custom Filter interface for a configurable pipeline:
@FunctionalInterface
interface DataFilter<T> {
    Flux<T> apply(Flux<T> stream);
}

// Each filter independently defined and testable:
DataFilter<LogEntry> errorFilter = stream -> stream.filter(e -> e.level() == Level.ERROR);
DataFilter<LogEntry> enricher   = stream -> stream.map(e -> geoIpService.enrich(e));
DataFilter<LogEntry> piMasker   = stream -> stream.map(PIIMasker::mask);

// Assemble pipeline (each filter unaware of others):
Flux<LogEntry> pipeline = Flux.from(kafkaSource)
    .transform(errorFilter)
    .transform(enricher)
    .transform(piMasker);

pipeline.subscribe(elasticSink::write);

// Testing filter in isolation (no pipeline needed):
StepVerifier.create(errorFilter.apply(Flux.just(errorEntry, debugEntry, warnEntry)))
    .expectNext(errorEntry)  // only ERROR passes
    .verifyComplete();
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pipe and Filter is only for stream/real-time processing | Pipe and Filter is a general pattern applicable to any sequential data transformation — batch ETL (read CSV → transform → load database), request processing (middleware stacks in Express, Spring's filter chain), compiler phases, and HTTP interceptor chains. Real-time streaming is one application                                                             |
| Filters must be stateless                               | Filters CAN be stateful (e.g., a windowing aggregator maintains state between events). However, stateful filters: (1) cannot be trivially parallelized, (2) complicate failure recovery (state must be checkpointed). Stateless filters are strongly preferred for parallelism and fault tolerance; use stateful filters only when the transformation requires state |
| Order of filters doesn't matter                         | Order matters significantly. Put cheap filters (simple boolean checks) FIRST to reduce data volume before expensive filters (network enrichment, ML inference). Filtering early reduces work for all downstream filters. This is the "predicate pushdown" optimization: filter as early and as aggressively as possible                                              |

---

### 🔥 Pitfalls in Production

**Shared mutable state between filters (breaks isolation):**

```java
// ANTI-PATTERN: filters sharing mutable state:
class Pipeline {
    private List<LogEntry> processedEntries = new ArrayList<>(); // shared state!

    void parse(String raw) {
        LogEntry entry = parser.parse(raw);
        processedEntries.add(entry);  // Filter 1 writes to shared list
    }

    void filter() {
        // Filter 2 reads AND MODIFIES the shared list:
        processedEntries.removeIf(e -> e.level() != Level.ERROR);
    }

    void enrich() {
        processedEntries.forEach(e -> e.setHostname(geoIp.lookup(e.ip()))); // mutates!
    }
}
// Parallelizing any filter: race conditions. Order dependency: brittle.

// FIX: filters are pure functions; data is immutable between steps:
Flux<String> rawLines = ...;
Flux<LogEntry> parsed   = rawLines.map(parser::parse);           // new object each time
Flux<LogEntry> filtered = parsed.filter(e -> e.level() == ERROR); // no mutation
Flux<LogEntry> enriched = filtered.map(e -> e.withHostname(geoIp.lookup(e.ip())));
// e.withHostname() returns a new LogEntry — original untouched.
// Any filter can be safely parallelized: .parallel().runOn(Schedulers.parallel())
```

---

### 🔗 Related Keywords

- `Stream Processing` — Pipe and Filter at scale with frameworks (Kafka Streams, Flink, Spark)
- `ETL` — Extract-Transform-Load: the classic pipe-and-filter application for data warehousing
- `Reactive Programming` — Flux/Observable operators implement pipe-and-filter in memory
- `CI-CD Pipeline` — each CI stage (build, test, scan, deploy) is a filter in a pipeline
- `Chain of Responsibility` — behavioral design pattern similar in structure but different intent (request handling vs. data transformation)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Independent filters connected by pipes;   │
│              │ each filter does one transformation;      │
│              │ composable, reorderable, parallelizable.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sequential data transformation with       │
│              │ multiple independent steps; ETL/streaming;│
│              │ stages need to be reused or recombined    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Filters have complex state dependencies   │
│              │ on each other; tight latency budget where │
│              │ serialization between stages adds overhead│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Assembly line: each station does one job,│
│              │  conveyor belt moves the work between     │
│              │  stations without stations knowing each  │
│              │  other."                                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Stream Processing → Kafka Streams →       │
│              │ Reactive Programming → ETL               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a Pipe and Filter pipeline for processing payment transactions: raw event (JSON string from Kafka) → parse → validate (reject malformed) → enrich with customer data → fraud score (ML model) → route: HIGH risk → fraud queue, LOW risk → continue → apply currency conversion → write to database. Identify which stages are transformers, filters, enrichers, and splitters/routers. Which stage is the likely bottleneck (fraud scoring via ML model), and how would you parallelize it without breaking ordering guarantees?

**Q2.** In a compiler, the Pipe and Filter stages are: Lexer → Parser → Semantic Analyzer → Optimizer → Code Generator. Each stage is a filter. The Optimizer often runs multiple sub-passes internally. Why do compilers use Pipe and Filter for their architecture? What's the benefit of keeping Lexer and Parser separate (vs. integrating them)? At which stage does "data" change its type most dramatically, and what does this tell you about the pipe contracts between stages?
