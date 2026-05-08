---
layout: default
title: "MapReduce"
parent: "Big Data & Streaming"
nav_order: 7
permalink: /big-data-streaming/mapreduce/
id: BIG-007
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Distributed Computing, Data Structures
used_by: Apache Hadoop, Apache Spark, Distributed Computing
related: Apache Hadoop, Apache Spark, Distributed Computing
tags:
  - mapreduce
  - batch-processing
  - hadoop
  - parallel-processing
  - deep-dive
---

# BIG-007 — MapReduce

⚡ TL;DR — MapReduce is a **programming model** for processing large datasets in parallel across a distributed cluster — the **Map** phase applies a function to each input record independently (parallelizable), and the **Reduce** phase aggregates results by key; Google published it in 2004, Apache Hadoop implemented it, and it became the foundation of big data batch processing — though Apache Spark has largely superseded it for most workloads.

| #532            | Category: Big Data & Streaming                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Computing, Data Structures             |                 |
| **Used by:**    | Apache Hadoop, Apache Spark, Distributed Computing |                 |
| **Related:**    | Apache Hadoop, Apache Spark, Distributed Computing |                 |

---

### 🔥 The Problem This Solves

**LARGE-SCALE DATA PROCESSING ON COMMODITY HARDWARE:**
Processing a 10TB log file to count errors by type. On one machine: 20,000 seconds. Google in 2004 needed to process web crawl data (petabytes) in hours, not weeks. The solution: split the data across thousands of commodity servers, apply the same logic to each piece in parallel, then combine results. The challenge: automatically handling failures, distributing work, and collecting results — without requiring developers to write distributed systems code for every new computation.

---

### 📘 Textbook Definition

**MapReduce** is a distributed programming model with two user-defined functions:

1. **Map(key1, value1) → list(key2, value2)**: applies to each input record, emits key-value pairs.
2. **Reduce(key2, list(value2)) → list(key3, value3)**: receives all values for a given key, aggregates them.

The **framework** handles: splitting input data across nodes, running Map tasks in parallel, **shuffling** (grouping all values for the same key to the same Reducer node), sorting, and running Reduce tasks. The developer writes only the Map and Reduce logic. **Shuffle phase**: after Map, all key-value pairs with the same key must be sent to the same Reducer — this involves network transfer and is the most expensive phase. **Combiner**: an optional local mini-reducer that runs on each Mapper node before the shuffle, reducing network transfer. Combiner applies the same Reduce function locally first (only valid when the operation is associative and commutative — sum, count, max/min, not average).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MapReduce = Map (apply function to each record, emit key-value pairs) → Shuffle (group by key) → Reduce (aggregate values per key) — all parallelized automatically.

**One analogy:**

> Counting votes in a national election. Map phase (local counting): each precinct (Mapper) counts its own ballots and produces partial totals: {"Candidate A": 150, "Candidate B": 200}. Shuffle: all partial totals for the same candidate are sent to the same aggregation station. Reduce phase: the aggregation station sums all partial totals: {"Candidate A": 15M, "Candidate B": 12M}.

- "Each precinct counts its own ballots" → Map: each node processes its data partition
- "Partial totals" → emitted (key, value) pairs from Map
- "All totals for same candidate to same station" → Shuffle by key
- "Aggregation station sums all totals" → Reduce: combine values for each key

**One insight:**
MapReduce's killer feature isn't the model itself — it's **automatic fault tolerance**. If a Mapper node fails mid-job, the framework re-runs that node's Map task on another machine. If a Reducer fails, re-run it. The developer writes simple sequential functions (Map and Reduce); the framework handles all distributed execution complexity. This democratized big data processing: domain experts (biologists, economists, analysts) could write MapReduce jobs without knowing distributed systems.

---

### 🔩 First Principles Explanation

**WORD COUNT — THE HELLO WORLD OF MAPREDUCE:**

```java
// Classic Hadoop MapReduce word count example

// MAPPER: reads lines, emits (word, 1) for each word
public class WordCountMapper
    extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final Text word = new Text();
    private final IntWritable one = new IntWritable(1);

    @Override
    protected void map(LongWritable key,  // byte offset in file (input key)
                       Text value,          // one line of text (input value)
                       Context context) throws IOException, InterruptedException {
        // key = file offset (e.g., 0, 512, 1024...)
        // value = "the quick brown fox jumps over the lazy dog"

        StringTokenizer tokenizer = new StringTokenizer(value.toString());
        while (tokenizer.hasMoreTokens()) {
            word.set(tokenizer.nextToken().toLowerCase());
            context.write(word, one);
            // Emits: ("the", 1), ("quick", 1), ("brown", 1), ...
        }
    }
}

// REDUCER: receives (word, [1,1,1,...]) and sums the counts
public class WordCountReducer
    extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable result = new IntWritable();

    @Override
    protected void reduce(Text key,                    // "the"
                          Iterable<IntWritable> values, // [1, 1, 1, 1, ...]
                          Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
        // Emits: ("the", 5), ("quick", 2), ...
    }
}

// JOB DRIVER: configure and submit the MapReduce job
public class WordCount {
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(WordCount.class);
        job.setMapperClass(WordCountMapper.class);

        // COMBINER: local mini-reducer (optional but important for performance)
        // Runs on each mapper BEFORE shuffle — reduces network traffic
        // Valid only for associative+commutative operations (sum is both)
        job.setCombinerClass(WordCountReducer.class);  // Same as Reducer

        job.setReducerClass(WordCountReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));  // HDFS input path
        FileOutputFormat.setOutputPath(job, new Path(args[1]));  // HDFS output path

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
```

**THE SHUFFLE PHASE — THE BOTTLENECK:**

```
Map Phase:
  Node 1 processes lines 1-10M → emits: ("the",1)×50K, ("fox",1)×100, ...
  Node 2 processes lines 10M-20M → emits: ("the",1)×45K, ("fox",1)×80, ...
  Node 3 processes lines 20M-30M → emits: ("the",1)×55K, ("fox",1)×120, ...

  With Combiner (local pre-aggregation ON EACH MAPPER):
  Node 1: ("the",50000), ("fox",100)  ← 1 pair/word instead of 50K pairs
  Node 2: ("the",45000), ("fox",80)
  Node 3: ("the",55000), ("fox",120)

Shuffle + Sort (network transfer):
  All keys starting with [a-m] → Reducer 1
  All keys starting with [n-z] → Reducer 2
  (or: hash(key) % num_reducers determines assignment)

  Reducer 1 receives: all ("fox", ...) from all mappers
  Reducer 1 sorts by key → ("fox", [100, 80, 120])

Reduce Phase:
  Reducer 1: ("fox", [100, 80, 120]) → sum → ("fox", 300)

WITHOUT Combiner: network transfer = 50K+100+45K+80+55K+120 = ~150K pairs
WITH Combiner:    network transfer = 3 pairs per word = ~3 pairs
Performance difference for "the": 50,000× less network traffic
```

---

### 🧪 Thought Experiment

**AVERAGE SALARY BY DEPARTMENT — WHY COMBINER CAN'T ALWAYS BE USED:**

Naive attempt: Map emits (department, salary). Combiner: average salaries locally. Reducer: average the averages from all Mappers.

Why this is WRONG: Average of averages ≠ average. If Node 1 has salaries [100, 200] (avg=150) and Node 2 has [300] (avg=300), the combined average should be (100+200+300)/3 = 200, not (150+300)/2 = 225.

**Correct approach:** Map emits (department, (salary, 1)). Combiner: sum salaries and counts: (department, (sum, count)). Reducer: divide total_sum / total_count. This is associative and commutative — Combiner can safely pre-aggregate.

---

### 🧠 Mental Model / Analogy

> MapReduce is like a library. A researcher (developer) writes two instructions: "How to summarize one book" (Map) and "How to combine summaries" (Reduce). The library (framework) assigns books to assistants (Mappers), collects summaries, groups them by topic (Shuffle), and hands topic-grouped summaries to senior researchers (Reducers) for final synthesis. The researcher doesn't manage the assistants, track who has which book, or handle an assistant calling in sick (failure) — the library framework does.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** MapReduce = Map (process each record, emit key-value) → Shuffle (group by key) → Reduce (aggregate per key). Automatically parallelized and fault-tolerant. Classic example: word count.

**Level 2:** Combiner: local pre-aggregation on each Mapper before shuffle (reduces network traffic). Only valid for associative+commutative operations (sum, count, max, min). Shuffle is the most expensive phase — minimize it with Combiner. Output is deterministic (same input → same output) because shuffle sorts by key.

**Level 3:** Hadoop MapReduce writes intermediate results to disk after Map phase (disk-based shuffle). This is why Spark (in-memory) is 10-100× faster for iterative algorithms — Spark keeps intermediate data in RAM. MapReduce on disk = safe (survives node failure between Map and Reduce) but slow. For ML algorithms requiring 100 iterations (gradient descent, PageRank): MapReduce = 100 disk reads/writes = very slow. Spark = 100 in-memory passes = fast.

**Level 4:** MapReduce was revolutionary because it separated the **what** (user-written Map and Reduce functions) from the **how** (distributed execution, fault tolerance, scheduling). This is the **programming model** design pattern: define a simple API (Map/Reduce) that the framework can optimize and parallelize automatically. The limitation: MapReduce forces ALL computation into Map→Shuffle→Reduce. Complex algorithms require chaining many MapReduce jobs, each writing to disk. SQL queries require translation (Hive translates SQL → MapReduce). Spark's DAG engine solved this: arbitrary computation graphs, not just linear Map→Reduce chains.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MAPREDUCE PIPELINE                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ INPUT: 10TB log file split into 1000 × 10GB chunks  │
│                                                      │
│ MAP PHASE (parallel, 1000 Mappers):                  │
│  Mapper 1: reads chunk 1 → emits (ERROR, 1)×5000   │
│  Mapper 2: reads chunk 2 → emits (ERROR, 1)×3000   │
│  ...                                                 │
│  Each Mapper runs independently (no coordination)   │
│                                                      │
│ COMBINER (optional, on each Mapper):                │
│  Mapper 1: locally sums → emits (ERROR, 5000)       │
│  [MAPREDUCE ← YOU ARE HERE: local pre-aggregation]   │
│                                                      │
│ SHUFFLE + SORT (network, most expensive):           │
│  All (ERROR, ...) → Reducer N                       │
│  All (WARN, ...)  → Reducer M                       │
│  Sorted by key within each Reducer's input          │
│                                                      │
│ REDUCE PHASE:                                        │
│  Reducer N: (ERROR, [5000, 3000, ...]) → sum        │
│  Output: (ERROR, 892000), (WARN, 1200000), ...      │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Hadoop MapReduce Execution on HDFS:
Input: 10TB log file stored on HDFS (replicated 3× across 1000 data nodes)

1. JobClient submits job to ResourceManager (YARN)
2. ResourceManager: allocates containers on data nodes (compute near data = locality)
3. ApplicationMaster (coordinator): assigns Map tasks to nodes closest to their data

4. Map Phase:
   DataNode 1: runs Mapper on its local HDFS chunk (data locality = no network read)
   DataNode 2: runs Mapper on its local chunk
   ...1000 Mappers in parallel...

5. Combiner: on each Mapper, pre-aggregate to reduce shuffle traffic

6. Shuffle + Sort:
   Mappers write intermediate output to local disk (not HDFS)
   Reducers: pull intermediate data from all Mappers (network transfer)
   Sort intermediate data by key

7. Reduce Phase:
   3 Reducers run in parallel (on 3 nodes)
   Each Reducer processes 1/3 of the key space

8. Output: written to HDFS

Fault tolerance:
   If a Mapper fails → ApplicationMaster re-runs that Map task on another node
   If Reducer fails → ApplicationMaster re-runs that Reduce task (re-pulls map output)
   If ApplicationMaster fails → YARN restarts it (job resumes from checkpoint)
```

---

### ⚖️ Comparison Table

| Aspect               | Hadoop MapReduce       | Apache Spark                 |
| -------------------- | ---------------------- | ---------------------------- |
| Intermediate storage | Disk (HDFS)            | Memory (RAM)                 |
| Speed                | Baseline (1×)          | 10-100× faster for iterative |
| Computation model    | Map → Shuffle → Reduce | DAG (arbitrary graph)        |
| Real-time support    | No (batch only)        | Yes (Spark Streaming)        |
| Ease of use          | Verbose Java API       | SQL, Python, Scala APIs      |
| Fault tolerance      | Task re-execution      | RDD lineage (re-compute)     |
| Still used?          | Legacy, declining      | Industry standard            |

---

### ⚠️ Common Misconceptions

| Misconception                    | Reality                                                                                                                                                                                                               |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "MapReduce is Hadoop"            | MapReduce is a programming model; Hadoop is a framework that implements it. Spark also implements MapReduce-like operations but with a richer API and in-memory execution                                             |
| "Combiner is always safe to use" | Combiner is only safe for associative+commutative functions. Average, median, and percentile operations cannot use Combiners safely without transformation                                                            |
| "MapReduce is obsolete"          | MapReduce the programming model lives on in Spark's `map()` and `reduce()` operations. Hadoop MapReduce the framework is largely replaced by Spark, but the concept is fundamental to all distributed data processing |

---

### 🚨 Failure Modes & Diagnosis

**1. Reducer Straggler (One Slow Reducer Delays the Whole Job)**

**Symptom:** MapReduce job is 95% complete for 2 hours. Never finishes. One Reducer is still running.

**Root Cause:** One key has vastly more values than others (data skew). "ERROR" type: 90% of all log lines. One Reducer handles all ERROR entries — 1000× more work than others.

**Fix:** Redistribute work by adding a salt to the key: `(ERROR_shard_1, count)`, `(ERROR_shard_2, count)` → multiple reducers handle ERROR. Then add a second MapReduce job to combine the shards.

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Computing, Data Structures
**Builds On This:** Apache Hadoop, Apache Spark
**Related:** Apache Hadoop, Apache Spark, Distributed Computing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MAP         │ Apply function to each record → (k, v) pairs│
│ SHUFFLE     │ Group all values by key (network transfer)  │
│ REDUCE      │ Aggregate values per key → final output     │
│ COMBINER    │ Local pre-reduce (only for assoc+commut ops)│
│ BOTTLENECK  │ Shuffle phase (network transfer)            │
│ vs SPARK    │ Spark: in-memory, 10-100× faster, DAG       │
│ DATA SKEW   │ Hot key → straggler Reducer → salt keys     │
│ ONE-LINER   │ "Map each record, group by key, reduce     │
│             │  groups — all parallelized and fault-tolerant"│
│ NEXT EXPLORE│ Apache Hadoop → HDFS                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the Combiner optimization in MapReduce? Under what mathematical condition is it safe to use? Give an example where using a Combiner would produce incorrect results and explain why.

**Q2.** (TYPE C — Design) Given a 50TB clickstream dataset with user_id, page_id, timestamp: design a MapReduce pipeline to compute, for each user, the page they visit most frequently. Consider: multi-stage approach, data skew (power-law user activity distribution), and output format.
