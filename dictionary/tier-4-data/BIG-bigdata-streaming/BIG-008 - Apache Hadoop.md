---
version: 1
layout: default
title: "Apache Hadoop"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /big-data-streaming/apache-hadoop/
id: BIG-008
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Distributed Computing, MapReduce
used_by: HDFS, Apache Spark, Big Data Processing
related: MapReduce, HDFS, Apache Spark
tags:
  - hadoop
  - mapreduce
  - hdfs
  - yarn
  - big-data
---

# BIG-008 - Apache Hadoop

⚡ TL;DR - Apache Hadoop is an **open-source distributed computing framework** consisting of **HDFS** (Hadoop Distributed File System - store petabytes across commodity hardware with replication), **YARN** (Yet Another Resource Negotiator - cluster resource manager), and the **MapReduce engine** (batch processing); introduced by Yahoo in 2006 as an open-source implementation of Google's GFS + MapReduce papers, it became the standard big data platform - largely superseded by Apache Spark for compute, but HDFS remains widely used for storage.

| #533            | Category: Big Data & Streaming          | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Distributed Computing, MapReduce        |                 |
| **Used by:**    | HDFS, Apache Spark, Big Data Processing |                 |
| **Related:**    | MapReduce, HDFS, Apache Spark           |                 |

---

### 🔥 The Problem This Solves

**PETABYTE-SCALE STORAGE + PROCESSING ON COMMODITY HARDWARE:**
Before Hadoop, processing petabytes of data required expensive proprietary systems (mainframes, specialized appliances). Google solved this internally with GFS (storage) + MapReduce (compute) on cheap commodity servers. Apache Hadoop made this available as open-source software, enabling anyone to run a petabyte-scale data cluster using standard x86 servers. The core insight: use software-level replication and fault tolerance instead of expensive hardware RAID - buy 10 cheap servers instead of one expensive reliable server.

---

### 📘 Textbook Definition

**Apache Hadoop** is a distributed computing ecosystem with four core components:

1. **HDFS (Hadoop Distributed File System)**: stores files by splitting them into blocks (default 128MB), replicating each block 3× across different nodes and racks. NameNode: stores metadata (file names, block locations). DataNodes: store actual blocks. Designed for large sequential reads (not random access).
2. **YARN (Yet Another Resource Negotiator)**: cluster resource manager. ResourceManager: global resource allocation (cluster brain). NodeManager: per-node resource management (CPU, memory containers). ApplicationMaster: per-application coordinator (manages tasks within one job).
3. **MapReduce Engine**: executes MapReduce jobs using HDFS data and YARN resources.
4. **Hadoop Common**: shared libraries and utilities.

**Hadoop Ecosystem (broader):** HBase (column-store on HDFS), Hive (SQL on MapReduce/Tez), Pig (dataflow scripting), Oozie (workflow scheduler), ZooKeeper (distributed coordination), Sqoop (relational DB ↔ HDFS), Flume (log ingestion).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Hadoop = HDFS (distributed storage with replication) + YARN (resource management) + MapReduce (batch processing) - the original open-source big data platform, now mostly replaced by Spark for compute.

**One analogy:**

> Hadoop is like a public library system:
>
> - **HDFS** = the library building + shelves (stores copies of every book in multiple branches for redundancy)
> - **YARN** = the librarian who assigns reading rooms and books to researchers (resource allocation)
> - **MapReduce** = the research process (give each researcher a stack of books, they summarize their stack, then combine summaries)
> - **NameNode** = the card catalog master (knows where every book/copy lives - a single critical catalog)

**One insight:**
Hadoop's most important insight was **data locality**: instead of moving data to compute (stream 10TB from storage to compute node = slow), move compute to data (run computation on the node that already has the data = fast). YARN schedules Map tasks on nodes that physically store the HDFS blocks they need - eliminating or reducing network I/O for the most expensive phase.

---

### 🔩 First Principles Explanation

**HDFS ARCHITECTURE:**

```
HDFS Cluster Architecture:

  [NameNode]  ←  single master  →  stores metadata only
     │              (file → blocks → DataNode locations)
     │              NOT actual data
     │
  ┌──┴─────────────────────────────────────┐
  │                                        │
  ↓                                        ↓
[DataNode 1]     [DataNode 2]     [DataNode 3]
rack 1            rack 1            rack 2
stores blocks     stores blocks     stores blocks

FILE: "access.log" (384 MB) → split into 3 × 128MB blocks:
  Block A (bytes 0-128MB)   → replicated to DN1, DN2, DN3
  Block B (bytes 128-256MB) → replicated to DN2, DN3, DN4
  Block C (bytes 256-384MB) → replicated to DN1, DN3, DN5

Replication rule (default):
  1st replica: local node (where writer runs)
  2nd replica: different rack (rack 2)
  3rd replica: same rack as 2nd, different node

  Ensures: survives single node failure + single rack failure
```

**NAMENODE - THE SINGLE POINT OF FAILURE:**

```
NameNode stores metadata:
  /user/john/access.log → [Block A @ DN1,DN2,DN3], [Block B @ DN2,DN3,DN4], [Block C @ DN1,DN3,DN5]

NameNode is IN MEMORY (fast) but:
  Problem: If NameNode dies → cluster is inaccessible (can't find any blocks)

Traditional solution:
  Secondary NameNode: periodically checkpoints NameNode state to disk
  NOT a hot standby - just reduces recovery time from hours to minutes

High-availability solution (Hadoop 2+):
  Active NameNode + Standby NameNode
  Shared edit log (QJM: Quorum Journal Manager) - both see all edits
  ZooKeeper: automatic failover (detects active NN failure → promotes standby)
  Failover time: ~30 seconds

  [Active NN] → writes edits → [Journal Node 1, JN2, JN3] (quorum)
  [Standby NN] → reads from JN → stays current
  → If Active NN dies: ZooKeeper detects → promotes Standby to Active
```

**YARN RESOURCE MANAGEMENT:**

```java
// YARN Container lifecycle (how a MapReduce job runs):
// 1. Client submits job to ResourceManager
// 2. RM allocates container for ApplicationMaster
// 3. ApplicationMaster starts in that container
// 4. AM negotiates more containers with RM for Map tasks
// 5. AM requests containers with locality preference:
//    "I need to run Mapper for Block A → prefer DN1, DN2, or DN3"
// 6. RM: grants container on DN1 (data local)
//    → 0 bytes network transfer for reading Block A
// 7. AM monitors task progress; on failure: requests new container

// YARN container = isolated slice of node resources:
//   <memory=4GB, vcores=2>
// Multiple containers can run on one NodeManager
// NodeManager reports available resources to RM every second (heartbeat)

// spark-submit targeting YARN (still common):
// spark-submit --master yarn --deploy-mode cluster \
//   --num-executors 100 \
//   --executor-memory 8G \
//   --executor-cores 4 \
//   WordCount.jar hdfs:///data/input hdfs:///data/output
```

**HADOOP vs SPARK - THE TRANSITION:**

```
Hadoop MapReduce workflow (e.g., 3-step ML pipeline):

Step 1: Feature engineering
  Input: HDFS       → MapReduce job 1 → Output: HDFS (write to disk)
Step 2: Training
  Input: HDFS (read from disk) → MapReduce job 2 → Output: HDFS (write to disk)
Step 3: Evaluation
  Input: HDFS (read from disk) → MapReduce job 3 → Output: HDFS (write to disk)

Total disk reads/writes: 6 (3 reads + 3 writes to HDFS)
Total time: slow (disk I/O at each step)

Spark equivalent:
  Input: HDFS (read once) → RDD in memory → transform → transform → Output: HDFS
  Total disk reads/writes: 1 read + 1 write
  Total time: 10-100× faster

Spark on YARN: Spark uses YARN for resource management, HDFS for storage
Still uses the Hadoop ecosystem - just replaces the MapReduce engine with Spark's DAG engine
```

---

### 🧪 Thought Experiment

**NAMENODE CAPACITY LIMIT:**
NameNode stores all metadata in RAM (for speed). Each file block record: ~150 bytes.
1 billion files × 1 block average × 150 bytes = 150GB RAM for NameNode metadata.
A $10,000 server has ~512GB RAM → max ~3.4 billion file blocks per NameNode.

Problem: Many small files (1KB each) hit this limit fast - 3.4 billion files × 1KB = 3.4TB of data, wasting the cluster's petabyte capacity. Small files are HDFS's biggest scaling enemy.

**Solution:** Combine small files into larger ones (sequence files, Avro, Parquet). Rule: HDFS is optimized for large files (100MB+), not small files. This is why Hive tables should be stored in Parquet/ORC, not millions of tiny CSVs.

---

### 🧠 Mental Model / Analogy

> YARN is like a hotel concierge that manages all hotel rooms (CPU + memory on each server). Every time a guest (application) arrives: the concierge assigns rooms (containers) based on availability and preferences ("I need a room near the gym" = data locality). The concierge tracks which rooms are occupied, handles checkout (task completion), and reassigns rooms when guests leave unexpectedly (failure).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Hadoop = HDFS (stores big data across many servers, replicated) + YARN (manages cluster resources) + MapReduce (batch processing engine). Foundation of the big data ecosystem.

**Level 2:** HDFS blocks (128MB) are replicated 3× across racks for fault tolerance. NameNode stores metadata in RAM - single master (HA mode adds active/standby). Data locality: YARN schedules compute near data to minimize network I/O.

**Level 3:** Hadoop's limitation: MapReduce writes intermediate results to disk between each stage. Iterative algorithms (ML, graph processing) = many stages = many disk writes = slow. Spark replaced the compute layer (running on YARN) while HDFS remained. Modern Hadoop clusters are often HDFS + YARN + Spark, no MapReduce.

**Level 4:** The Hadoop ecosystem fragmented into competing components: Hive (SQL→MapReduce) vs. Impala (SQL→MPP), HDFS vs. S3/Azure Blob/GCS (cloud object storage), YARN vs. Kubernetes for resource management. Cloud providers offer managed Hadoop (EMR, HDInsight, Dataproc). The trend: replace HDFS with object storage (cheaper, elastic), replace YARN with Kubernetes, keep Spark as the compute engine. "Serverless Spark" on cloud = no Hadoop cluster to manage. Hadoop as a managed service is declining; as an architecture pattern it endures.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ HADOOP CLUSTER ARCHITECTURE                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [HDFS NameNode]        [YARN ResourceManager]       │
│       │                        │                    │
│  (metadata: where blocks are)  (allocates containers)│
│       │                        │                    │
│  ┌────┴──────────────────────┴───────────────────┐  │
│  │  DataNode + NodeManager on same server         │  │
│  │  (data locality: run compute where data lives) │  │
│  │                                                │  │
│  │  [Server 1: DN1 + NM1]  [Server 2: DN2 + NM2] │  │
│  │  [Server 3: DN3 + NM3]  ...1000 servers...     │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Hadoop job submission and execution:

1. hadoop fs -put localfile.txt /user/john/data/
   → NameNode: split file, assign blocks to DataNodes
   → DataNodes: store blocks + replicate to 2 more DataNodes

2. hadoop jar WordCount.jar /user/john/data/ /user/john/output/
   → JobClient: submits to YARN ResourceManager
   → RM: allocates ApplicationMaster container
   → AM: registers with RM, requests Map task containers
   → AM: prefers containers on nodes with data blocks (locality)

3. YARN allocates containers on DataNodes with local blocks
   → Map tasks read HDFS blocks from LOCAL DISK (no network)
   → Map tasks write intermediate (shuffled) output to LOCAL disk

4. Shuffle: Reducers pull intermediate data from all Mappers (network)
5. Reduce tasks write final output to HDFS (replicated)

6. Output available at /user/john/output/ on HDFS
   hadoop fs -get /user/john/output/ localdir/
```

---

### ⚖️ Comparison Table

| Component      | Hadoop MapReduce       | Apache Spark                  |
| -------------- | ---------------------- | ----------------------------- |
| Compute engine | MapReduce (disk-based) | DAG (in-memory)               |
| Speed          | Baseline               | 10-100× faster                |
| Storage        | HDFS                   | HDFS, S3, GCS, Azure Blob     |
| Resource mgmt  | YARN                   | YARN, Kubernetes, Standalone  |
| SQL support    | Hive (slow)            | Spark SQL (fast)              |
| Streaming      | No (batch only)        | Spark Streaming (micro-batch) |
| Status (2024)  | Declining (legacy)     | Industry standard             |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Hadoop is dead"                      | HDFS and YARN are still widely used as infrastructure. The MapReduce engine is largely replaced by Spark. Many production clusters run Spark on YARN on HDFS                                     |
| "Hadoop handles small files well"     | HDFS is optimized for large files (128MB+ blocks). Millions of small files exhaust NameNode memory and create many Map tasks with tiny work. Use sequence files, Parquet, or Avro to consolidate |
| "Secondary NameNode is a hot standby" | It's NOT a failover node. It's a checkpointing service that periodically merges the edit log. For true HA, use active/standby NameNode with ZooKeeper                                            |

---

### 🚨 Failure Modes & Diagnosis

**1. NameNode Out of Memory (OOM)**

**Symptom:** NameNode JVM OOM error. HDFS metadata no longer accessible. Cluster becomes unusable.

**Root Cause:** Too many files stored in HDFS (millions of small files). Each file's block metadata consumes ~150 bytes of NameNode heap. When total metadata exceeds NameNode heap size, OOM occurs.

**Fix:** Increase NameNode heap (`-Xmx50g`). Compact small files into larger Parquet/ORC/Avro files. Monitor: `hdfs dfsadmin -report` shows `Files And Directories`, set alert at 80% of heap capacity.

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Computing, MapReduce
**Builds On This:** HDFS, Apache Spark
**Related:** MapReduce, HDFS, Apache Spark

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HDFS         │ Distributed storage: blocks (128MB) × 3  │
│ NameNode     │ Metadata master (RAM) - HA with standby  │
│ DataNode     │ Stores actual block data                  │
│ YARN         │ Resource manager (containers = CPU+RAM)  │
│ DATA LOC     │ Schedule compute near data (no net I/O)  │
│ SMALL FILES  │ Bad: exhaust NameNode → use Parquet/ORC  │
│ vs SPARK     │ HDFS+YARN still used; MR replaced by Spark│
│ ONE-LINER    │ "Replicated distributed FS + resource    │
│              │  manager + batch engine on commodity HW" │
│ NEXT EXPLORE │ HDFS → Apache Spark                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain HDFS block replication strategy (rack-aware). Why is rack awareness important? What happens if a rack fails?

**Q2.** (TYPE C - Troubleshooting) A Hadoop cluster with 500 DataNodes is running out of HDFS capacity, but monitoring shows only 500TB of 2PB capacity is used. Investigation reveals 2 billion files in HDFS. What is the root cause, what is the immediate impact, and how do you resolve it?
