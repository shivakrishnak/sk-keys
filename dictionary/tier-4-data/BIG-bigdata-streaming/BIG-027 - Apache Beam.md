---
version: 2
layout: default
title: "Apache Beam"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /big-data-streaming/apache-beam/
id: BIG-037
category: Big Data & Streaming
difficulty: ★★★
depends_on: Batch vs Stream Processing, Lambda Architecture, Apache Flink
used_by: Portable Streaming Pipelines, Unified Batch/Stream Processing
related: Batch vs Stream Processing, Lambda Architecture, Apache Flink
tags:
  - apache-beam
  - portable-pipelines
  - pcollection
  - ptransform
  - batch-stream-unified
---

# BIG-032 - Apache Beam

⚡ TL;DR - **Apache Beam** is a **unified programming model** for batch AND stream processing - you write one pipeline using Beam's SDK (Java, Python, Go), and it runs on any **runner** (Google Dataflow, Apache Flink, Spark, Samza); core abstractions: **PCollection** (distributed dataset, bounded or unbounded), **PTransform** (operation on PCollection), **Pipeline** (DAG of transforms); solves Lambda's two-codebase problem by abstracting over execution engines; widely used on **Google Dataflow** for managed serverless streaming.

| #561            | Category: Big Data & Streaming                                | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Batch vs Stream Processing, Lambda Architecture, Apache Flink |                 |
| **Used by:**    | Portable Streaming Pipelines, Unified Batch/Stream Processing |                 |
| **Related:**    | Batch vs Stream Processing, Lambda Architecture, Apache Flink |                 |

---

### 🔥 The Problem This Solves

**WRITE ONCE, RUN ANYWHERE (BATCH OR STREAM):**
Lambda Architecture requires maintaining two codebases (Spark batch + Flink stream). But even with Flink alone, switching cloud providers means rewriting your pipeline. Apache Beam's promise: write one pipeline using Beam SDK → run it as batch on Spark, stream on Flink, serverless on Google Dataflow, or locally for testing. Change the execution engine by changing one line (the runner). One codebase, multiple execution targets.

---

### 📘 Textbook Definition

**Apache Beam** (Batch + strEAM) is an open-source, unified programming model for data processing pipelines:

- **PCollection**: the core data abstraction. A distributed, potentially unbounded collection of elements. Can be bounded (batch) or unbounded (streaming).
- **PTransform**: an operation that transforms one or more PCollections into other PCollections. `ParDo`, `GroupByKey`, `Combine`, `Flatten`, `Partition`.
- **Pipeline**: a DAG of PTransforms that reads from sources, applies transforms, and writes to sinks.
- **Runner**: the execution engine. `DirectRunner` (local testing), `FlinkRunner`, `SparkRunner`, `DataflowRunner` (Google Cloud), `SamzaRunner`.
- **Windowing**: event-time windows via `Window.into()`. Same windowing semantics as Flink (tumbling, sliding, session), but written in a portable way.
- **Triggers**: when to fire window results (default: on watermark; can be on count, on element count + time, etc.).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Beam = write pipeline once in Java/Python → run as batch (Spark) or stream (Flink/Dataflow) by changing the runner; PCollection + PTransform = the pipeline model.

**One analogy:**

> Apache Beam is like a universal recipe. You write "make pasta" (the pipeline). The chef (runner) adapts: in an Italian restaurant (Flink): hand-made pasta. At a cafeteria (Spark batch): industrial pasta machine. At a cooking lab (Google Dataflow): automated sous vide. Same recipe, different execution. You don't rewrite the recipe for each kitchen.

**One insight:**
Beam is most commonly used in two scenarios: (1) **Google Cloud Dataflow**: the managed Beam runner. If you're on GCP, Dataflow provides auto-scaling, serverless execution, and no infrastructure management. Beam = the programming model; Dataflow = the execution engine. (2) **Portable pipelines**: organizations that need to run the same ETL on-premises (Flink) AND in the cloud (Dataflow) without code changes. For teams fully committed to Flink or Spark, Beam adds abstraction overhead with limited practical benefit.

---

### 🔩 First Principles Explanation

**BEAM PIPELINE BASICS:**

```java
// Maven dependency:
// <dependency>
//   <groupId>org.apache.beam</groupId>
//   <artifactId>beam-sdks-java-core</artifactId>
// </dependency>
// Runner: beam-runners-flink-1.16 OR beam-runners-google-cloud-dataflow-java

public class WordCountPipeline {

    public static void main(String[] args) {
        // OPTION 1: Local testing (DirectRunner)
        PipelineOptions options = PipelineOptionsFactory.create();

        // OPTION 2: Run on Flink (FlinkRunner)
        // FlinkPipelineOptions options = PipelineOptionsFactory.as(FlinkPipelineOptions.class);
        // options.setRunner(FlinkRunner.class);
        // options.setFlinkMaster("flink-jobmanager:8081");

        // OPTION 3: Google Dataflow (serverless)
        // DataflowPipelineOptions options = PipelineOptionsFactory.as(DataflowPipelineOptions.class);
        // options.setRunner(DataflowRunner.class);
        // options.setProject("my-gcp-project");
        // options.setRegion("us-central1");
        // options.setTempLocation("gs://my-bucket/temp");

        Pipeline pipeline = Pipeline.create(options);

        // PCollection: read from text file (bounded = batch)
        PCollection<String> lines = pipeline.apply(
            "ReadLines",
            TextIO.read().from("gs://my-bucket/input/*.txt")
        );

        // PTransform: split lines into words
        PCollection<String> words = lines.apply(
            "SplitWords",
            FlatMapElements.into(TypeDescriptors.strings())
                .via((String line) -> Arrays.asList(line.split("\\s+")))
        );

        // PTransform: filter empty words
        PCollection<String> filtered = words.apply(
            "FilterEmpty",
            Filter.by((String word) -> !word.isEmpty())
        );

        // PTransform: count occurrences
        PCollection<KV<String, Long>> wordCounts = filtered.apply(
            "CountWords", Count.perElement()
        );

        // PTransform: format output
        PCollection<String> formatted = wordCounts.apply(
            "FormatOutput",
            MapElements.into(TypeDescriptors.strings())
                .via((KV<String, Long> wc) -> wc.getKey() + ": " + wc.getValue())
        );

        // Sink: write results
        formatted.apply("WriteResults", TextIO.write().to("gs://my-bucket/output/wordcount"));

        // Execute:
        pipeline.run().waitUntilFinish();
        // Change to DataflowRunner: run on Google Cloud (no code change above)
    }
}
```

**STREAMING PIPELINE WITH KAFKA + WINDOWING:**

```java
public class KafkaStreamingPipeline {

    public static void main(String[] args) {
        PipelineOptions options = PipelineOptionsFactory.fromArgs(args).create();
        Pipeline pipeline = Pipeline.create(options);

        // SOURCE: read from Kafka (unbounded PCollection = streaming)
        PCollection<KV<String, String>> kafkaMessages = pipeline.apply(
            "ReadFromKafka",
            KafkaIO.<String, String>read()
                .withBootstrapServers("kafka:9092")
                .withTopic("order-events")
                .withKeyDeserializer(StringDeserializer.class)
                .withValueDeserializer(StringDeserializer.class)
                .withoutMetadata()
        );

        // PARSE: JSON → Order object
        PCollection<Order> orders = kafkaMessages.apply(
            "ParseOrders",
            ParDo.of(new DoFn<KV<String, String>, Order>() {
                @ProcessElement
                public void processElement(@Element KV<String, String> kv,
                                           OutputReceiver<Order> out) {
                    try {
                        Order order = objectMapper.readValue(kv.getValue(), Order.class);
                        out.output(order);
                    } catch (JsonProcessingException e) {
                        // Dead-letter pattern: route bad records to side output
                        log.error("Failed to parse order: {}", kv.getValue());
                    }
                }
            })
        );

        // WINDOWING: assign event-time timestamps + 5-minute tumbling windows
        PCollection<Order> windowedOrders = orders
            .apply("AssignTimestamps",
                WithTimestamps.of((Order order) -> new Instant(order.getEventTimestamp()))
            )
            .apply("TumblingWindows",
                Window.<Order>into(
                    FixedWindows.of(Duration.standardMinutes(5))
                )
                .withAllowedLateness(Duration.standardSeconds(30))
                .triggering(AfterWatermark.pastEndOfWindow())
                .discardingFiredPanes()
            );

        // AGGREGATE: sum revenue per product per 5-minute window
        PCollection<KV<String, Double>> revenueByProduct = windowedOrders
            .apply("KeyByProduct",
                WithKeys.of((Order order) -> order.getProductId())
            )
            .apply("SumRevenue",
                Combine.perKey(Sum.ofDoubles())
                    // Custom combiner (order.amount):
                    // Actually: use a simple CombineFn
            );

        // SINK: write to BigQuery (streaming inserts)
        revenueByProduct.apply("WriteToBigQuery",
            BigQueryIO.<KV<String, Double>>write()
                .withCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
                .withWriteDisposition(WriteDisposition.WRITE_APPEND)
                .to("project:dataset.product_revenue")
        );

        // Run on Flink: add FlinkPipelineOptions
        // Run on Dataflow: add DataflowPipelineOptions + project/region/tempLocation
        pipeline.run();  // non-blocking for streaming
    }
}
```

**CUSTOM DOFN (CORE BEAM TRANSFORM):**

```java
// DoFn is the fundamental processing unit in Beam
// Similar to Flink's ProcessFunction
public class FraudDetectionDoFn extends DoFn<Order, FraudAlert> {

    // State (only available in Beam with state-capable runners: Flink, Dataflow)
    @StateId("transaction-count")
    private final StateSpec<ValueState<Integer>> countSpec = StateSpecs.value();

    @TimerId("window-cleanup")
    private final TimerSpec cleanupTimer = TimerSpecs.timer(TimeDomain.EVENT_TIME);

    @ProcessElement
    public void processElement(
            @Element Order order,
            @StateId("transaction-count") ValueState<Integer> countState,
            @TimerId("window-cleanup") Timer cleanupTimer,
            OutputReceiver<FraudAlert> out) {

        Integer count = MoreObjects.firstNonNull(countState.read(), 0) + 1;
        countState.write(count);

        // Set timer to expire in 5 minutes (cleanup state)
        cleanupTimer.set(Instant.now().plus(Duration.standardMinutes(5)));

        if (count > 5) {
            out.output(new FraudAlert(order.getUserId(), count, order));
        }
    }

    @OnTimer("window-cleanup")
    public void onTimer(@StateId("transaction-count") ValueState<Integer> countState) {
        countState.clear();  // reset count after 5 minutes of inactivity
    }
}
```

---

### 🧪 Thought Experiment

**WHEN BEAM IS OVERKILL:**

For a team that:

1. Already uses Flink exclusively for streaming
2. Never needs to run on Spark or Dataflow
3. Wants direct access to Flink APIs (low-level ProcessFunction, custom windowing)

Apache Beam adds: abstraction overhead, less access to Flink-specific features, and another layer to debug.

For a team that:

1. Uses Google Cloud Dataflow (managed, serverless, auto-scaling)
2. Needs portability (run locally with DirectRunner, production on Dataflow)
3. Has Python data engineers who want the Python Beam SDK

Beam is the natural choice - Dataflow IS the managed Beam runner.

---

### 🧠 Mental Model / Analogy

> Apache Beam is like SQL. SQL defines WHAT you want to query (the pipeline logic). The database engine (MySQL, PostgreSQL, BigQuery) decides HOW to execute it. You write one SQL query; you can run it on different databases. Similarly: write one Beam pipeline; run it on Flink (stream), Spark (batch), or Dataflow (managed cloud).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Beam = unified batch+stream SDK. PCollection + PTransform + Runner. Change runner → change execution engine. Solves Lambda's two-codebase problem. Used with Google Dataflow.

**Level 2:** PCollection: bounded (batch) or unbounded (stream). PTransform types: `ParDo`, `GroupByKey`, `Combine`, `Flatten`, `Partition`. Windowing: `FixedWindows`, `SlidingWindows`, `Sessions`. Triggers: `AfterWatermark`, `AfterProcessingTime`, `AfterCount`.

**Level 3:** Stateful processing in Beam (requires Flink/Dataflow runners): `@StateId`, `@TimerId` annotations in DoFn. Splittable DoFn (SDF): for reading from I/O sources in parallel (Kafka, files). Side inputs: broadcast small data to all DoFn instances (like broadcast joins). Cross-language transforms: Python Beam pipeline can call Java transforms via Beam's cross-language infrastructure.

**Level 4:** Beam portability: runs on any runner via Runner API (gRPC-based). Python SDK runs Java runners via cross-language (Beam portable runner). Flink Runner: Beam pipeline compiled to Flink JobGraph → runs as native Flink job. Dataflow v2 (streaming engine): Dataflow backend uses Apache Beam pipeline representation. The Dataflow shuffle service: managed external shuffle for GroupByKey operations (not in-memory → scales to petabytes without OOM). Production Dataflow: auto-scaling workers, exactly-once semantics, managed checkpointing - no Flink cluster to manage.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ APACHE BEAM ARCHITECTURE                             │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Beam SDK (Java/Python/Go):                          │
│   PCollection → ParDo → GroupByKey → Combine → Sink │
│         ↓ submit to Runner                           │
│ [BEAM ← YOU ARE HERE: portable pipeline model]      │
│                                                      │
│ Runner A: DirectRunner (local testing)              │
│   Runs in single JVM, no cluster needed             │
│                                                      │
│ Runner B: FlinkRunner (Flink cluster)               │
│   Compiles Beam pipeline → Flink JobGraph           │
│   Runs as native Flink job                          │
│                                                      │
│ Runner C: DataflowRunner (Google Cloud)             │
│   Serializes pipeline → sends to Dataflow service  │
│   Dataflow: auto-scales workers, manages cluster   │
│                                                      │
│ SAME Beam code, DIFFERENT runners                   │
│ Change: options.setRunner(DataflowRunner.class)     │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ETL pipeline: Kafka → Beam → BigQuery (Google Dataflow)

1. Developer writes Beam pipeline (Java SDK):
   Read Kafka → Parse JSON → Filter → Aggregate (5-min windows) → Write BigQuery

2. Local test: DirectRunner
   options.setRunner(DirectRunner.class);
   pipeline.run().waitUntilFinish();
   → Test with sample data → verify output

3. Deploy to Google Dataflow:
   options.setRunner(DataflowRunner.class);
   options.setProject("my-project");
   options.setRegion("us-central1");
   options.setTempLocation("gs://bucket/temp");
   pipeline.run();
   → Beam SDK serializes pipeline graph → sends to Dataflow API
   → Dataflow: provisions workers (auto-scaled), runs pipeline
   → No Flink/Spark cluster to manage

4. At 1M events/sec (Black Friday):
   Dataflow: auto-scales from 10 → 50 workers automatically
   → Handles increased load without manual intervention

5. Future: migrate to on-premises Flink:
   options.setRunner(FlinkRunner.class);
   options.setFlinkMaster("flink:8081");
   pipeline.run();
   → SAME code, different runner
   → Zero code changes to the ETL logic
```

---

### ⚖️ Comparison Table

| Feature                  | Beam                      | Flink Direct              | Spark Direct    |
| ------------------------ | ------------------------- | ------------------------- | --------------- |
| Multi-runner portability | YES                       | NO (Flink only)           | NO (Spark only) |
| API complexity           | Medium (abstraction)      | Higher (Flink APIs)       | Medium          |
| Low-level control        | Limited                   | Full                      | Full            |
| Google Dataflow          | Native                    | Via Flink runner          | NO              |
| Python support           | YES                       | Limited                   | YES             |
| State API                | Yes (limited)             | Full                      | Limited         |
| Best for                 | GCP/Dataflow, portability | Complex streaming, custom | Batch + ML      |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                                                     |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Beam is a stream processing engine"   | Beam is a programming MODEL (SDK + pipeline specification). It's NOT an execution engine. The execution is done by the runner (Flink, Spark, Dataflow). Beam without a runner does nothing                  |
| "Beam = Google Dataflow"               | Dataflow is the MANAGED runner for Beam. Beam can run on Flink, Spark, and locally too. Google created Beam (donated to Apache in 2016) to abstract over Dataflow                                           |
| "Beam is more feature-rich than Flink" | Beam has less direct access to underlying features (Flink's ProcessFunction, custom windowing implementations). For Flink-specific features, use Flink directly. Beam trades expressiveness for portability |

---

### 🚨 Failure Modes & Diagnosis

**1. Pipeline Works Locally (DirectRunner) but Fails on Dataflow**

**Symptom:** DirectRunner tests pass. Dataflow job fails with serialization errors or class not found.

**Root Cause A:** Lambda capturing non-serializable state. Beam DoFns must be serializable (sent to remote workers).

```java
// WRONG: capturing non-serializable field
private ObjectMapper mapper = new ObjectMapper();  // not serializable!
DoFn<...> fn = new DoFn<...>() {
    @ProcessElement
    public void process(...) { mapper.readValue(...); }  // captures outer mapper
};

// RIGHT: create within DoFn @Setup:
public class ParseDoFn extends DoFn<String, Order> {
    private transient ObjectMapper mapper;

    @Setup
    public void setup() {
        mapper = new ObjectMapper();  // created per-worker, not serialized
    }

    @ProcessElement
    public void process(@Element String json, OutputReceiver<Order> out) {
        out.output(mapper.readValue(json, Order.class));
    }
}
```

**Root Cause B:** Dependency missing from worker classpath.
**Fix:** Ensure all dependencies in Maven `<scope>runtime</scope>` are included in the fat JAR or Dataflow template.

---

### 🔗 Related Keywords

**Prerequisites:** Batch vs Stream Processing, Lambda Architecture
**Builds On This:** Google Dataflow, Portable Pipelines
**Related:** Batch vs Stream Processing, Lambda Architecture, Apache Flink

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PCOLLECTION │ Distributed dataset (bounded or unbounded) │
│ PTRANSFORM  │ Operation on PCollection                   │
│ DOFN        │ Custom processing function (ParDo)         │
│ PIPELINE    │ DAG of PTransforms                         │
│ RUNNER      │ DirectRunner, Flink, Spark, Dataflow       │
│ CHANGE ENG  │ options.setRunner(...) → different system  │
│ DATAFLOW    │ Managed serverless Beam runner (GCP)       │
│ WINDOWING   │ FixedWindows, SlidingWindows, Sessions     │
│ vs FLINK    │ Beam: portable; Flink: more control/speed  │
│ ONE-LINER   │ "Write pipeline once; run on Flink,       │
│             │  Spark, or Dataflow by changing runner"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What are the core abstractions in Apache Beam? What is the difference between a runner and the Beam SDK? Why was Apache Beam created and what problem does it solve compared to using Flink or Spark directly?

**Q2.** (TYPE C - Design) A company currently runs Spark batch jobs on their on-premises cluster and wants to eventually migrate to Google Cloud Dataflow for managed streaming. They also want to add real-time processing without rewriting their ETL logic. How would you use Apache Beam to achieve this migration? What are the tradeoffs compared to directly adopting Flink?
