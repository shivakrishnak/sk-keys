---
version: 2
layout: default
title: "Cassandra Data Modeling"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/nosql/cassandra-data-modeling/
id: NDB-032
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Column Family, Eventual Consistency in NoSQL, CAP Theorem (DB)
used_by: System Design, Polyglot Persistence, Distributed Systems
related: Column Family, Hot Partition Problem, Wide Column vs Document
tags:
  - nosql
  - cassandra
  - data-modeling
  - deep-dive
---

⚡ TL;DR - Cassandra data modeling is **query-first and denormalized by design**: create one table per query pattern, choose partition keys for even data distribution, and use clustering keys for sort order within a partition - the schema is a pre-computed answer to a specific query, not a normalized representation of reality.

| #464            | Category: NoSQL & Distributed Databases                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Column Family, Eventual Consistency in NoSQL, CAP Theorem (DB) |                 |
| **Used by:**    | System Design, Polyglot Persistence, Distributed Systems       |                 |
| **Related:**    | Column Family, Hot Partition Problem, Wide Column vs Document  |                 |

---

### 🔥 The Problem This Solves

**RELATIONAL MODELING IN CASSANDRA = DISASTER:**
Teams new to Cassandra often model like a relational database: normalized tables, secondary indexes, `SELECT WHERE non_pk_column = X`. Result: Cassandra does a full cluster scan (`ALLOW FILTERING`), querying all nodes for every read. At high scale: read performance collapses, latency becomes unpredictable, and `IN` clauses with many values hammer the coordinator node.

**QUERY-FIRST MODELING:**
Cassandra is a query execution engine that returns pre-materialized results. Every table is a materialized view of a specific query. The modeling process starts with: "what queries does the application need?" and works backward to: "what partition key, clustering key, and columns support that exact query?" Each query gets its own table. Data is duplicated across tables. Writes are cheap; reads must be simple and bounded.

---

### 📘 Textbook Definition

**Cassandra data modeling** is the process of designing CQL table schemas where each table is optimized for a specific access pattern. The key decisions: **Partition Key** - the column(s) whose hash value determines which node(s) store the row; all rows with the same partition key are co-located on the same node(s). **Clustering Key** - column(s) that sort rows within a partition; enables efficient range queries within a partition. **Primary Key = Partition Key + Clustering Key**. Core principles: (1) **Denormalization** - duplicate data across tables to serve different queries without joins; (2) **Bounded partitions** - partitions should have a bounded, predictable number of rows (avoid unbounded growth); (3) **Even distribution** - partition key must have high cardinality and uniform access pattern to avoid hot partitions; (4) **Secondary indexes** (local, per-node) - use sparingly, only on low-cardinality columns in small-scale reads; (5) **Materialized Views** (Cassandra 3.0+) - derived tables maintained automatically from a base table; use with caution (write amplification); (6) **SAI (Storage-Attached Index)** - Cassandra 4.0+: global index stored alongside SSTables; more flexible than traditional secondary indexes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
In Cassandra, design your tables to match your queries exactly - one table per query - because Cassandra has no query planner: you are the query planner.

**One analogy:**

> A pre-sorted phonebook for every possible lookup. One phonebook sorted by last name (last_name → address). Another sorted by city (city → all residents). Another sorted by profession (profession → members). In SQL, you have one phonebook and an index; the database plans how to use the index. In Cassandra, you physically print a separate phonebook for each query. Wasteful? Yes. But retrieving any name from any phonebook is instant: flip to the right letter (partition key), scan a short section (clustering key range).

- "Each phonebook" → each Cassandra table (one per query pattern)
- "Right letter" → partition key hash → correct node
- "Short section" → clustering key range scan within partition
- "Physically printing phonebooks" → data duplication (denormalization)
- "No query planner" → you design tables to answer specific queries directly

**One insight:**
Cassandra's write path (MemTable → SSTable, LSM-tree) is extremely fast, which is why denormalization works - writing the same data to 3 tables with different schemas is cheap. The cost is write amplification and the operational burden of keeping multiple tables consistent. Cassandra bets that write throughput is more available than query flexibility.

---

### 🔩 First Principles Explanation

**DESIGNING TABLES FROM QUERIES:**

```cql
-- Use case: messaging application
-- Queries needed:
-- Q1: Get all messages in a conversation, newest first
-- Q2: Get all conversations for a user, newest first
-- Q3: Get a specific message by ID

-- Q1: messages by conversation
CREATE TABLE messages_by_conversation (
    conversation_id  UUID,
               -- partition key: all msgs for a conv on one node
    sent_at          TIMESTAMP,
          -- clustering key: sort order within partition
    message_id       UUID,        -- part of primary key (uniqueness)
    sender_id        UUID,
    content          TEXT,
    PRIMARY KEY ((conversation_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC, message_id ASC);
-- Partition: all messages for conversation X → same nodes
-- Range query: SELECT * FROM messages_by_conversation
--              WHERE conversation_id = ? LIMIT 50
-- Fast: single partition, range scan on sent_at (pre-sorted)

-- Q2: conversations by user (requires a SEPARATE table)
CREATE TABLE conversations_by_user (
    user_id          UUID,
               -- partition key: all convs for user on one node
    last_message_at  TIMESTAMP,   -- clustering key: sorted by recency
    conversation_id  UUID,
    other_user_id    UUID,
    last_message_preview TEXT,
           -- denormalized (duplicated from messages table)
    PRIMARY KEY ((user_id), last_message_at, conversation_id)
) WITH CLUSTERING ORDER BY (last_message_at DESC,
    conversation_id ASC);
-- Fast: SELECT * FROM conversations_by_user WHERE user_id =
    ? LIMIT 20

-- Q3: message by ID (another separate table)
CREATE TABLE messages_by_id (
    message_id   UUID PRIMARY KEY,
         -- simple partition key (UUID = uniform distribution)
    -- ... all message fields
);
```

**PARTITION KEY DESIGN - AVOIDING HOT PARTITIONS:**

```cql
-- BAD: date as partition key (time-series messages)
CREATE TABLE messages (
    day     DATE,        -- partition key
    ts      TIMESTAMP,
    user_id UUID,
    content TEXT,
    PRIMARY KEY (day, ts, user_id)
);
-- Problem: "day = today" partition is constantly written to
-- All writes for today go to the same nodes → HOT PARTITION
-- Yesterday's partitions are cold → uneven node load

-- BETTER: bucket by user + day (if query is per-user timeline)
CREATE TABLE user_feed (
    user_id UUID,
    day     DATE,
    ts      TIMESTAMP,
    content TEXT,
    PRIMARY KEY ((user_id, day), ts)  -- composite partition key
);
-- Now each (user + day) is its own partition
-- Write spread across all users' partitions → even distribution
-- Query: WHERE user_id = ? AND day = ? ORDER BY ts DESC LIMIT 100

-- HIGH-VOLUME: add time bucket to prevent unbounded partition growth
-- Without bucketing: user_id partition grows forever as user posts
-- With bucketing: each user × week = bounded partition
CREATE TABLE user_posts_weekly (
    user_id     UUID,
    week_bucket TEXT,    -- e.g.,
        "2024-W03" - composite partition key part
    created_at  TIMESTAMP,
    post_id     UUID,
    PRIMARY KEY ((user_id, week_bucket), created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id ASC);
-- Application must query multiple week buckets for long time ranges
-- Trade-off: bounded partitions vs. multi-partition reads for long history
```

**SECONDARY INDEXES (use with caution):**

```cql
-- Built-in secondary index (local, per-node)
CREATE INDEX ON users (email);
SELECT * FROM users WHERE email = 'alice@example.com';
-- Problem: Cassandra queries EVERY node for this (full cluster scan)
-- Each node checks its local index → results merged at coordinator
-- For low-cardinality columns (e.g.,
    status: 'active'/'inactive'): O(N nodes)
-- For high-cardinality (email): O(N nodes),
    each node may return 0 results
-- Only appropriate: low-traffic, low-cardinality, not in hot paths

-- SAI (Storage-Attached Index, Cassandra 4.0+)
CREATE CUSTOM INDEX ON users (email) USING 'StorageAttachedIndex';
SELECT * FROM users WHERE email = 'alice@example.com';
-- SAI: global index, more efficient than local secondary index
-- Stored alongside SSTables (not separate table), compacted together
-- Better for: high-cardinality columns, moderate traffic
-- Still: not as efficient as a table designed with email as partition key
```

**DENORMALIZATION IN PRACTICE - DUAL WRITE:**

```java
// Cassandra dual-write: update BOTH tables atomically
// Goal: user sends message → update messages_by_conversation AND
// conversations_by_user

BoundStatement insertMsg = msgByConvStmt.bind(
    convId, Instant.now(), messageId, senderId, content
);
BoundStatement updateConv = convByUserStmt.bind(
    recipientId, Instant.now(), convId, senderId, contentPreview
);

// Option 1: Cassandra BATCH (logged batch = lightweight transaction
// across tables)
BatchStatement batch = BatchStatement.builder(BatchType.LOGGED)
    .addStatement(insertMsg)
    .addStatement(updateConv)
    .build();
session.execute(batch);
// Logged batch: atomic (via Cassandra's batch log mechanism)
// WARNING: don't batch across different partition keys - batches to
// same partition are efficient;
// cross-partition batches add coordinator overhead (anti-pattern for
// large batches)

// Option 2: Write-through cache / event-driven (preferred at scale)
// Write to primary table → Cassandra Change Data Capture / Trigger →
// update secondary tables asynchronously
```

---

### 🧪 Thought Experiment

**TWITTER-LIKE TIMELINE: MODELING CHALLENGE**

Design a Twitter-like timeline: 100M users, users can have up to 100M followers, need to show a user's home timeline (tweets from people they follow, newest first), need to show a user's own tweet history.

**QUERY PATTERNS:**

- Q1: `GET /timeline/{user_id}` - get recent tweets from followed users
- Q2: `GET /users/{user_id}/tweets` - get user's own tweets

**NAIVE APPROACH (fails at scale):**
Single `tweets` table partitioned by `author_id`. Timeline requires fetching tweets from all followed users then merging and sorting. With 10,000 follows: 10,000 partition reads + in-memory sort. Cassandra: each read is a separate partition → 10,000 coordinator round trips. Latency: unusable.

**FAN-OUT-ON-WRITE (works for most users):**
At tweet creation, write the tweet to the timeline of every follower:

```cql
-- Home timeline table (fan-out writes at tweet time)
CREATE TABLE home_timeline (
    user_id     UUID,        -- partition = one user's home timeline
    tweeted_at  TIMESTAMP,
    tweet_id    UUID,
    author_id   UUID,
    content     TEXT,
    PRIMARY KEY ((user_id), tweeted_at, tweet_id)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);

-- On tweet by alice (1000 followers):
-- Write 1000 rows to home_timeline (one per follower)
-- Each follower's timeline partition is updated immediately
-- Timeline read: single partition scan → instant
```

**THE CELEBRITY PROBLEM (hot partition solution):**
Alice has 50M followers. Tweeting = 50M writes. Solution: fan-out-on-read for celebrities. Normal users: fan-out-on-write. Celebrities: store only in author_id timeline. Reader's app merges: their precomputed timeline (fan-out) + last N tweets from followed celebrities.

**THE LESSON:**
Cassandra data modeling is inseparable from application architecture. "Fan-out on write" is a modeling pattern that makes read O(1) at the cost of O(followers) writes. The choice between fan-out-on-write vs. fan-out-on-read is a Cassandra data modeling decision with business implications (write latency for celebrities = unacceptable).

---

### 🧠 Mental Model / Analogy

> Cassandra data modeling is like pre-printing a customized report for every possible query, filed in labeled folders. In a relational database: one master spreadsheet; the database searches it dynamically for any query. In Cassandra: you print "Queries by customer" as a separate sorted stack, "Queries by date" as another stack, "Queries by status" as another. Each stack is instantly retrievable for its purpose. Duplicated data? Yes. But retrieving any report is instant because it was pre-sorted for its query.

- "Customized report for each query" → one Cassandra table per query pattern
- "Filed in labeled folders" → partition key hash (routes to correct node)
- "Pre-sorted within folder" → clustering key (rows sorted within partition)
- "Duplicated data across reports" → denormalization (same data in multiple tables)
- "Master spreadsheet" → relational DB with query optimizer

---

### 📶 Gradual Depth - Four Levels

**Level 1:** In Cassandra, design one table per query. Choose the partition key as the "folder" for related rows (drives which nodes hold the data). Add clustering keys to sort rows within the folder. Copy (denormalize) data into every table that needs it. Never filter on non-key columns without an index.

**Level 2:** Avoid hot partitions: don't use date or status as sole partition key. Add user_id or a hash bucket to spread load. Bound partition size by adding a time bucket to composite partition keys (user_id, week). Use CLUSTERING ORDER BY to avoid in-memory sort. For multi-partition queries (e.g., "last 7 days"): query 7 separate partitions in parallel, merge in application. Test partition sizes: `nodetool tablehistograms` - aim for partitions < 100MB, < 100K rows.

**Level 3:** Cassandra secondary indexes: local (per-node, full-cluster-scan), Materialized Views (auto-maintained, high write amplification - use with caution, MV instability issues in older Cassandra), SAI (Storage-Attached Index in Cassandra 4.0+ - global, stored with SSTables, efficient for high-cardinality columns). Lightweight Transactions (LWT): `INSERT ... IF NOT EXISTS` and `UPDATE ... IF condition` use Paxos consensus - serializable but expensive (4 round trips). Only for uniqueness checks; avoid in hot paths. Counters: special column type (`counter COUNTER`); no tombstones for deletes; cannot be used in non-counter tables; use carefully (atomic increment via CRDT-like semantics). USING TIMESTAMP: write with explicit timestamp - useful for CDC replication, resolving write conflicts with known ordering.

**Level 4:** Cassandra data modeling is a discipline of encoding application invariants into the schema - specifically, encoding the read access patterns as pre-materialized data structures. This is similar to CQRS (Command Query Responsibility Segregation) at the database level: writes update multiple denormalized "read models" simultaneously (dual-write to multiple tables). The challenge is maintaining consistency across denormalized tables during failures: if writing to `table_A` succeeds but `table_B` fails, the application sees inconsistent data. Cassandra LOGGED BATCH provides atomic write to multiple partitions within a single keyspace (via a batch log journal), but it adds coordinator overhead and is often misused as a performance optimization (it isn't). The correct Cassandra architecture often involves an event-driven consistency repair mechanism: Kafka CDC → consumer re-applies failed writes → eventual consistency across all tables. Cassandra's read repair and hinted handoff provide eventual consistency for replica divergence; but cross-table consistency is the application's responsibility.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CASSANDRA READ PATH: QUERY EXECUTION                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ CQL: SELECT * FROM messages_by_conversation          │
│      WHERE conversation_id = 'conv-42'               │
│      ORDER BY sent_at DESC LIMIT 50                  │
│                                                      │
│ [CASSANDRA DATA MODELING ← YOU ARE HERE]             │
│                                                      │
│ 1. Coordinator receives query                        │
│ 2. Hash partition key: murmur3('conv-42') → token    │
│ 3. Token → which nodes own this range (from ring map)│
│ 4. Route query to replication factor (RF) nodes      │
│    e.g., RF=3: nodes N1, N3, N5                      │
│ 5. Read from quorum (2 of 3) - if CL = QUORUM        │
│ 6. Each node: check MemTable + L1/L2 SSTables        │
│    Bloom filter → skip SSTables that don't have key  │
│    Merge results (LSM merge of multiple SSTables)    │
│ 7. Return top 50 rows (already sorted by sent_at)    │
│    No application-side sort: clustering key = disk   │
│    sort order                                        │
│                                                      │
│ If partition_key missing: full cluster scan          │
│ (ALLOW FILTERING = all nodes queried) → AVOID        │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**USER SENDS MESSAGE - DUAL WRITE:**

```
User sends: "Hello" in conversation conv-42 to alice
→ Application: build message entity
→ [CASSANDRA DATA MODELING ← YOU ARE HERE: dual write]
→ Cassandra LOGGED BATCH:
   1. INSERT INTO messages_by_conversation
      (conv-42, now(), msg-uuid, sender_id, "Hello")
   2. INSERT INTO conversations_by_user
      (alice_user_id, now(), conv-42, sender_id, "Hello")
        -- alice's inbox
   3. INSERT INTO conversations_by_user
      (sender_user_id, now(), conv-42, alice_user_id,
        "Hello")  -- sender's outbox
→ Batch committed (atomic via batch log journal)
→ All 3 partitions updated

Alice's inbox query:
→ SELECT * FROM conversations_by_user
  WHERE user_id = alice_uuid
  ORDER BY last_message_at DESC LIMIT 20
→ Single partition scan (alice's partition)
→ Returns 20 most recent conversations, pre-sorted
→ O(log N + 20): instant
```

---

### ⚖️ Comparison Table

| Concept             | Cassandra                              | PostgreSQL                           |
| ------------------- | -------------------------------------- | ------------------------------------ |
| Schema design basis | Query-first (one table per query)      | Data-first (normalized entity model) |
| JOINs               | Not supported (by design)              | Full JOIN support with optimizer     |
| Secondary index     | Expensive (full cluster scan) / SAI    | Efficient B-tree index               |
| Denormalization     | Required and expected                  | Avoided (normalization preferred)    |
| Write path          | Append-only (MemTable → SSTable)       | B-tree in-place + WAL                |
| Scale               | Horizontal (add nodes, auto-rebalance) | Vertical (primarily)                 |
| Query planner       | You are the query planner              | Sophisticated optimizer              |

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                                                                           |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "ALLOW FILTERING is fine for one-time queries"                           | ALLOW FILTERING performs a full cluster scan: it reads every node. Even "one-time" if on a 100-node cluster processing millions of rows, it will cause a latency spike and affect other workloads |
| "Materialized Views are the best way to handle multiple access patterns" | MVs have known stability issues in older Cassandra versions and add significant write amplification. Dual-write in application code is often more reliable                                        |
| "`IN` clause is a good way to query multiple partition keys"             | Large `IN` clauses cause the coordinator node to fan out many sub-queries and aggregate results. Better: parallel async reads from the application                                                |
| "Low-cardinality columns are good partition keys"                        | Low cardinality = few distinct partition values = some nodes handle all traffic (hot partitions). Partition key should have high cardinality AND uniform access                                   |

---

### 🚨 Failure Modes & Diagnosis

**1. Partition Size Too Large - "Wide Row" Problem**

**Symptom:** Queries against specific partition keys take 5-10 seconds; GC pressure on nodes that own those partitions; `nodetool tpstats` shows read stage queue buildup.

**Root Cause:** Unbounded partition growth. Table designed with `user_id` as sole partition key for a highly active user's post history. Active users accumulate millions of rows in a single partition.

**Diagnostic:**

```bash
# Check partition sizes in SSTable
nodetool tablehistograms keyspace.table_name
# Look for: Partition Size (bytes) - P99 and Max values
# Alert threshold: Max > 100MB, P99 > 10MB

# Find large partitions
nodetool getendpoints keyspace table_name partition_key_value
# Then on that node:
nodetool cfstats keyspace.table_name | grep -E "SSTable|Live rows"
```

**Fix:** Add a time bucket to the partition key: `(user_id, month)` instead of `user_id`. For existing data: create a new table with correct schema, backfill using Spark Cassandra Connector, then cut over writes to the new table.

---

### 🔗 Related Keywords

**Prerequisites:** Column Family, Eventual Consistency in NoSQL, CAP Theorem (DB)

**Builds On This:** System Design, Polyglot Persistence

**Related:** Column Family, Hot Partition Problem, Wide Column vs Document

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RULE 1      │ One table per query (query-first design)  │
│ RULE 2      │ Partition key: high cardinality + uniform │
│ RULE 3      │ Clustering key: defines sort order        │
│ RULE 4      │ Add time bucket to bound partition size   │
│ RULE 5      │ Denormalize: duplicate data across tables │
│ AVOID       │ ALLOW FILTERING, large IN, growing arrays │
│             │ low-cardinality partition keys            │
│ TOOL        │ nodetool tablehistograms (partition sizes)│
│ ONE-LINER   │ "You are the query planner in Cassandra - │
│             │  design tables as pre-materialized answers│
│ NEXT EXPLORE│ DynamoDB Patterns → Hot Partition Problem │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a Cassandra schema for a ride-sharing app: drivers have live location updates (every 5 seconds), riders request rides and need to see nearby drivers (within 5km), and each ride has a lifecycle (REQUESTED → MATCHED → IN_PROGRESS → COMPLETED). Identify all access patterns, choose tables + partition/clustering keys, and explain how you'd handle the "find drivers near location" query (hint: Cassandra is not great at geo queries - what's your workaround?).

**Q2.** (TYPE D - Failure Scenario) A Cassandra table was designed with `city` as the sole partition key for a food delivery app. The top 5 cities account for 80% of orders. After 6 months, reads from `city = 'New York'` are taking 8 seconds; nodes that own the 'New York' partition are GC-thrashing. What went wrong? Provide the diagnosis, the schema fix, and a data migration strategy with zero downtime.
