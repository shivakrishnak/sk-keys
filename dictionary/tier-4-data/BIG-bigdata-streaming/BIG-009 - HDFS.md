---
version: 2
layout: default
title: "HDFS"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /big-data-streaming/hdfs/
id: BIG-009
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Hadoop, Distributed Computing
used_by: Apache Spark, Hive, HBase, Big Data Processing
related: Apache Hadoop, Apache Spark, Distributed File Systems
tags:
  - hdfs
  - hadoop
  - distributed-storage
  - big-data
  - replication
---

# BIG-009 - HDFS

⚡ TL;DR - HDFS (Hadoop Distributed File System) is a **distributed, fault-tolerant file system** that stores large files as **128MB blocks** replicated across multiple DataNodes (default 3× for fault tolerance), with a **NameNode** managing all metadata in RAM; designed for write-once-read-many, high-throughput sequential reads on commodity hardware - **not** for low-latency random access or millions of small files.

| #534            | Category: Big Data & Streaming                        | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Hadoop, Distributed Computing                  |                 |
| **Used by:**    | Apache Spark, Hive, HBase, Big Data Processing        |                 |
| **Related:**    | Apache Hadoop, Apache Spark, Distributed File Systems |                 |

---

### 🔥 The Problem This Solves

**STORING PETABYTES ON COMMODITY HARDWARE:**
A 10PB dataset stored on a single server requires extremely expensive enterprise storage (specialized hardware, RAID, SAN). HDFS replaces hardware RAID with software replication across hundreds of cheap commodity servers - 3 copies of every 128MB block across different nodes and racks. One server fails: its blocks are still available on other nodes. The NameNode (metadata master) knows exactly where every block lives, coordinates read/write across the cluster, and triggers re-replication when a DataNode goes down.

---

### 📘 Textbook Definition

**HDFS** is a distributed file system that organizes data as:

- **Blocks**: files split into fixed-size chunks (default 128MB; up to 256MB). Each block stored independently on DataNodes.
- **Replication factor**: each block copied to N DataNodes (default N=3). Rack-aware placement: 1st replica on local node, 2nd on different rack, 3rd on same rack as 2nd but different node - survives one entire rack failure.
- **NameNode (master)**: stores file system namespace (directory tree, file→block mappings) and block locations. Runs entirely in RAM for speed. **Single master** - no NameNode = no HDFS.
- **DataNodes (workers)**: store blocks on local disks. Send heartbeats + block reports to NameNode every 3 seconds/1 hour. NameNode detects failure if no heartbeat for 10 minutes → triggers re-replication of affected blocks.
- **Client**: interacts with NameNode for metadata, then reads/writes blocks directly from/to DataNodes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HDFS = split large files into 128MB blocks → replicate each block 3× across multiple servers → NameNode tracks all block locations in RAM → fault-tolerant distributed storage.

**One analogy:**

> HDFS is like a distributed library with one master catalog (NameNode) and thousands of branch libraries (DataNodes). Every book chapter (block) is printed in triplicate and stored in 3 different branches (replication). The master catalog knows which branches have which chapters. When a branch burns down (DataNode failure), the catalog detects it, finds the other copies, and prints new copies to different branches (re-replication). You can add infinite branches to store more books (horizontal scaling).

**One insight:**
HDFS was designed for a specific workload pattern: write a file once, read it sequentially many times (web crawl → process → analyze → report). This informs every design decision: large blocks (128MB) for sequential streaming throughput, not small blocks (traditional FSes use 4KB); no random write support (append-only, then only in special cases); NameNode in RAM for fast metadata lookups (many map tasks need to find their blocks quickly). If your access pattern doesn't match this (random access, small files, frequent updates), HDFS is the wrong tool.

---

### 🔩 First Principles Explanation

**BLOCK PLACEMENT - RACK-AWARE REPLICATION:**

```
Cluster topology:
  Rack 1: DataNode A, DataNode B, DataNode C (same physical rack, same TOR switch)
  Rack 2: DataNode D, DataNode E, DataNode F (different rack)

File: access.log (300MB) → split to:
  Block 1 (0-128MB)
  Block 2 (128-256MB)
  Block 3 (256-300MB) [only 44MB, padded to conceptual block]

HDFS placement strategy (default, replication=3):
  Block 1:
    Replica 1: DataNode A (writer's node - no network for first copy)
    Replica 2: DataNode D (different rack - survives rack-1 failure)
    Replica 3: DataNode E (same rack as D, different node - 2 copies in rack-2)

Why this strategy?
  - Write performance: 1st replica is local (writer→local disk, fast)
  - Rack failure resilience: losing rack-1 (A,B,C) → replicas D and E still available
  - Read performance: clients can read from any replica (load distribution)
  - Network bandwidth: 2 rack-crossing writes (writer→D, D→E: local) instead of 3

DataNode failure scenario:
  DataNode D goes offline (hardware failure):
    NameNode detects missing heartbeat after 10 min
    Identifies all blocks with only 2 replicas (A, E)
    Schedules re-replication: copy Block 1 from A → DataNode F
    Block 1 again has 3 replicas: A, E, F
```

**NAMENODE INTERNALS:**

```
NameNode maintains two in-memory data structures:

  1. FsImage (namespace tree):
     /user/
       /john/
         /data/
           access.log → [Block 1 (128MB), Block 2 (128MB), Block 3 (44MB)]
           report.csv → [Block 4 (200MB)]

  2. EditLog (transaction log):
     Every FS operation appended: mkdir, rename, delete, create, append

  3. Block Location Map (in RAM, NOT persisted):
     Block 1 → [DN-A, DN-D, DN-E]
     Block 2 → [DN-B, DN-D, DN-F]
     ...rebuilt from DataNode block reports on startup

  NameNode startup sequence:
  1. Load FsImage from disk into RAM
  2. Replay EditLog (apply all transactions since last checkpoint)
  3. Wait for DataNodes to send block reports (blocks they store)
  4. Build block-location map in RAM from block reports
  5. Enter "safe mode" until block replication is verified → then serve requests

  Safe mode: NameNode refuses writes until it has seen blocks from
  enough DataNodes to verify replication is healthy
```

**HDFS READ PATH:**

```java
// Reading a file from HDFS:
// 1. Client → NameNode: "give me block locations for /data/access.log"
// 2. NameNode → Client: [Block1: DN-A, DN-D, DN-E], [Block2: DN-B, ...]
//    (ordered by topology closeness - prefer local, then same rack)
// 3. Client → DN-A: "send me Block 1"
//    DN-A streams block directly to client (NameNode not involved in data transfer)
// 4. Client → DN-B: "send me Block 2"
// ... (client reads blocks in order, potentially from different DNs)

// HDFS FS Java API usage (usually via Spark/MapReduce, rarely direct):
Configuration conf = new Configuration();
conf.set("fs.defaultFS", "hdfs://namenode:8020");
FileSystem fs = FileSystem.get(conf);

// Open and read a file:
FSDataInputStream in = fs.open(new Path("/user/john/data/access.log"));
byte[] buffer = new byte[64 * 1024 * 1024];  // 64MB read buffer
int bytesRead;
while ((bytesRead = in.read(buffer)) > 0) {
    // process buffer
}
in.close();

// Write a file (from local to HDFS):
FSDataOutputStream out = fs.create(new Path("/user/john/output/result.csv"));
// ... write to out ...
out.close();
```

**HDFS WRITE PATH - PIPELINE REPLICATION:**

```
Write pipeline (replication=3):
  Client wants to write Block 1 (128MB)

  1. Client → NameNode: "I want to create /user/john/file.log"
  2. NameNode → Client: [Write Block 1 to DN-A, DN-D, DN-E]

  3. Client sets up write pipeline:
     Client → DN-A → DN-D → DN-E (chain, not parallel fan-out)

  4. Client sends data in 64KB packets to DN-A
     DN-A: stores locally + forwards to DN-D
     DN-D: stores locally + forwards to DN-E
     DN-E: stores locally + sends ACK to DN-D
     DN-D: sends ACK to DN-A
     DN-A: sends ACK to Client (block written successfully)

  5. NameNode: records Block 1 → [DN-A, DN-D, DN-E] in namespace

  Failure during write:
  DN-D fails mid-write:
    Pipeline reconstructed: Client → DN-A → DN-E (skip DN-D)
    Block 1 only has 2 replicas after write completes (DN-A, DN-E)
    NameNode detects under-replication → triggers async re-replication
    Block eventually reaches 3 replicas
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN HDFS GETS MILLIONS OF SMALL FILES?**

Scenario: 50M log files, each 1KB. Total data: 50GB (trivial). But:

- NameNode RAM: each file = 1 block × 150 bytes metadata = 50M × 150 = 7.5GB just for metadata
- Each file = 1 Map task: 50M tasks × 1-second startup overhead = 50M seconds of wasted overhead
- Each task reads 1KB but the startup overhead (container allocation, JVM start) takes 1-2 seconds = 1,000,000× overhead ratio

HDFS is completely wrong for this workload. The solution: aggregate small files into Parquet/ORC/Avro with 128MB+ file sizes. SequenceFile (Hadoop native) can also bundle many small records into one large file.

---

### 🧠 Mental Model / Analogy

> HDFS is like a distributed post office for very large packages: the NameNode is the central registry that knows which warehouse (DataNode) holds which packages (blocks). Packages are stored in triplicate in different cities (replication across racks). When you request a package, the registry tells you which warehouses have copies, and you go directly to the nearest warehouse (data locality, no middleman for actual data transfer). If one warehouse burns down (node failure), the registry schedules shipment of packages from another warehouse to a new location until full redundancy is restored.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** HDFS stores large files split into 128MB blocks, each replicated 3× across different servers. NameNode tracks block locations. DataNodes store data. Designed for sequential large reads, not random access.

**Level 2:** Rack-aware replication: 2 replicas in one rack, 1 in another - survives rack failure. NameNode single master in RAM - critical. Write pipeline: client→DN1→DN2→DN3 (chain). Read: client talks to NameNode for metadata, then directly to DataNode for data.

**Level 3:** NameNode HA: active/standby with shared journal (QJM). EditLog: all namespace changes persisted; FsImage: checkpoint snapshot. Safe mode on startup. Block reports: DataNodes report their blocks on startup, NameNode rebuilds location map. Balancer: `hdfs balancer` tool redistributes blocks for even utilization.

**Level 4:** HDFS is being replaced by cloud object storage (S3, GCS, Azure Blob) for many use cases. Object stores are cheaper (no 3× replication overhead - cloud manages durability), more elastic (no cluster to size), and scale infinitely. Spark can read from S3 natively. Key difference: HDFS has stronger consistency (read-after-write) and lower latency for local reads. Object stores have eventual consistency (though S3 is now strongly consistent since 2020) and higher latency (HTTP). Open table formats (Delta Lake, Iceberg, Hudi) add ACID transactions and schema evolution on top of object stores, making them competitive with HDFS for analytics workloads.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ HDFS CLUSTER                                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Client]                                            │
│    │                                                 │
│    ├─ metadata ops ─→ [NameNode] (RAM: ns + blocks) │
│    │    (directory list, block locations)            │
│    │                                                 │
│    └─ data ops ──→ [DataNode 1] [DataNode 2] ...    │
│       (read/write blocks directly, no NN in path)   │
│                                                      │
│  [HDFS ← YOU ARE HERE: block storage layer]         │
│                                                      │
│  Each block: 128MB, replicated 3× across nodes      │
│  Block reports: DataNodes → NameNode (every 1 hour) │
│  Heartbeats: DataNodes → NameNode (every 3 seconds) │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
User writes 400MB CSV file to HDFS:
1. Client → NameNode: "create /data/orders.csv"
2. NameNode: allocate blocks:
   Block 1 (0-128MB) → [DN-1, DN-4, DN-7]
   Block 2 (128-256MB) → [DN-2, DN-5, DN-8]
   Block 3 (256-384MB) → [DN-3, DN-6, DN-9]
   Block 4 (384-400MB) → [DN-1, DN-5, DN-8]
3. Client: write Block 1 via pipeline DN-1→DN-4→DN-7
4. Client: write Block 2 via pipeline DN-2→DN-5→DN-8
5. (Blocks 3,4 similar)
6. Client → NameNode: "file complete"

Spark reads /data/orders.csv:
1. Spark → NameNode: "block locations for /data/orders.csv"
2. NameNode: returns 4 block locations (3 replicas each)
3. Spark: schedules 4 tasks, each on a node holding the relevant block
4. Each task reads its block from local disk (data locality)
5. Results aggregated in memory → output
```

---

### ⚖️ Comparison Table

| Feature        | HDFS                                  | Cloud Object Storage (S3/GCS)          |
| -------------- | ------------------------------------- | -------------------------------------- |
| Replication    | 3× hardware-managed                   | Managed by cloud (11 nines durability) |
| Latency (read) | Low (local disk)                      | Medium (HTTP, ~50-150ms)               |
| Consistency    | Strong (read-after-write)             | Strong (S3 since 2020)                 |
| Cost           | Cluster maintenance + 3× storage      | Pay per GB, elastic                    |
| Best for       | On-prem, low-latency sequential reads | Cloud, elastic analytics               |
| Random access  | Not supported                         | Byte-range requests supported          |
| Small files    | Very bad                              | Fine (but batching still helps)        |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "HDFS block size = 128MB means small files waste 128MB" | HDFS blocks are NOT pre-allocated. A 1KB file uses only 1KB of disk space, but requires one NameNode metadata entry (150 bytes). The cost is metadata memory, not disk storage                          |
| "Secondary NameNode provides failover"                  | Secondary NameNode only merges FsImage + EditLog periodically. It's a checkpointing helper, not a hot standby. Use NameNode HA (active/standby with QJM) for true failover                              |
| "HDFS is obsolete"                                      | HDFS is still heavily used on-premises and as the foundation of many data lake architectures. Cloud workloads have largely moved to S3/GCS, but the HDFS API is abstracted so the change is transparent |

---

### 🚨 Failure Modes & Diagnosis

**1. DataNode Under-Replication**

**Symptom:** `hdfs fsck /` reports blocks with replication < 3. HDFS health shows `Under replicated blocks: 50,000`.

**Root Cause:** DataNode(s) went offline (hardware failure, maintenance). Their blocks now have fewer than 3 replicas.

**Diagnosis:** `hdfs dfsadmin -report` shows offline DataNodes. `hdfs fsck / -blocks -locations` shows which blocks are under-replicated and which DataNodes have copies.

**Fix:** Bring the DataNode back online (if possible) or wait - HDFS automatically re-replicates to healthy DataNodes after `dfs.namenode.replication.interval` (default 3 seconds check, re-replication starts immediately for blocks with 0 replicas). Monitor: `hdfs dfsadmin -report` until all blocks show healthy replication.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Hadoop, Distributed Computing
**Builds On This:** Apache Spark, Hive, HBase
**Related:** Apache Hadoop, Apache Spark, Distributed File Systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BLOCK SIZE  │ 128MB (tunable 256MB for large files)      │
│ REPLICATION │ 3× default (rack-aware placement)          │
│ NAMENODE    │ RAM-only metadata master (single master)   │
│ DATANODE    │ Stores blocks; heartbeat every 3s to NN   │
│ WRITE PATH  │ Client→DN1→DN2→DN3 pipeline chain          │
│ READ PATH   │ Client asks NN for locations, reads DND    │
│ WORST CASE  │ Millions of small files → NameNode OOM     │
│ HA MODE     │ Active/Standby NN + QJM (ZooKeeper)        │
│ vs S3       │ Lower latency, stronger consistency, on-prem│
│ ONE-LINER   │ "128MB blocks, 3× replicated, NameNode     │
│             │  metadata master, write-once-read-many"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the HDFS write pipeline. Why does HDFS use a pipeline (client→DN1→DN2→DN3) instead of having the client write to each DataNode directly (fan-out)? What are the performance implications of each approach?

**Q2.** (TYPE C - Production) Your HDFS cluster has 100 DataNodes. Due to a network switch failure, 20 DataNodes in one rack became unreachable. HDFS is in safe mode. Walk through what the NameNode does, why safe mode was triggered, and how you restore normal operation.
