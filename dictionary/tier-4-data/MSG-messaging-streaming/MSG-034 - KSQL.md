---
version: 2
layout: default
title: "KSQL"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /messaging-streaming/ksql/
id: MSG-039
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Kafka Streams, Apache Kafka
used_by: Real-Time Stream Analytics, Event Filtering, Streaming ETL
related: Kafka Streams, KTable vs KStream, Kafka Topic / Partition / Offset
tags:
  - ksql
  - ksqldb
  - streaming-sql
  - kafka-streams
  - deep-dive
---

# MSG-020 - KSQL

⚡ TL;DR - **ksqlDB** (formerly KSQL) is a **SQL engine for Apache Kafka** - write standard SQL queries against Kafka topics as if they were database tables or event streams; runs on the Kafka Streams library; provides **STREAM** (append-only, event semantics) and **TABLE** (current state, upsert semantics) abstractions; supports **persistent queries** (continuously running), **pull queries** (point-in-time state lookup), and **materialized views** - no Java required to build streaming pipelines.

| #547            | Category: Big Data & Streaming                                     | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Kafka Streams, Apache Kafka                                        |                 |
| **Used by:**    | Real-Time Stream Analytics, Event Filtering, Streaming ETL         |                 |
| **Related:**    | Kafka Streams, KTable vs KStream, Kafka Topic / Partition / Offset |                 |

---

### 🔥 The Problem This Solves

**KAFKA STREAM PROCESSING WITHOUT JAVA CODE:**
Kafka Streams is powerful but requires Java expertise. A data engineer who knows SQL shouldn't need to write `KStream.join(KTable, ...)` Java code to filter events or join streams. ksqlDB provides a SQL interface: `CREATE STREAM suspicious_transactions AS SELECT * FROM transactions WHERE amount > 10000` - this creates a continuously running Kafka Streams pipeline without any Java. Anyone who knows SQL can build streaming ETL, real-time alerts, and materialized views on Kafka data.

---

### 📘 Textbook Definition

**ksqlDB** is a streaming database built on top of Kafka, providing:

- **STREAM**: maps to a Kafka topic. Unbounded append-only sequence of events (KStream internally).
- **TABLE**: maps to a Kafka topic with compaction. Stores the latest value per key (KTable internally). Queryable as a current-state snapshot.
- **Persistent queries** (`CREATE STREAM AS SELECT` / `CREATE TABLE AS SELECT`): continuously running SQL queries that read from one Kafka topic and write results to another. Run indefinitely.
- **Pull queries** (`SELECT * FROM my_table WHERE key = '...'`): point-in-time synchronous queries against a materialized table. Like querying a database.
- **Push queries** (`SELECT * FROM my_stream EMIT CHANGES`): continuous subscription - streams new results to the client as they arrive.
- Runs as a standalone server (ksqlDB Server), deployed alongside Kafka.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ksqlDB = SQL on Kafka Streams - write SQL to filter/join/aggregate Kafka events continuously; no Java needed; STREAM (events) + TABLE (current state) = KStream + KTable under the hood.

**One analogy:**

> ksqlDB is like giving a non-programmer a SQL interface to control an assembly line. Instead of writing Java code to program the conveyor belt (Kafka Streams), you write: "Filter items where color=red and weight>5, send them to the red-heavy bin." ksqlDB translates your SQL instruction into the conveyor belt logic. The assembly line keeps running forever, filtering items as they arrive.

**One insight:**
The distinction between **persistent queries** (SQL that keeps running, writes to Kafka) and **pull queries** (SQL that asks "what's the current state?") is fundamental to ksqlDB. Persistent queries are the streaming ETL pipeline - they create new Kafka topics continuously. Pull queries are like hitting a REST API - they query the materialized state store. This makes ksqlDB usable both as a streaming processor AND as a queryable state database.

---

### 🔩 First Principles Explanation

**KSQLDB CORE OPERATIONS:**

```sql
-- Connect to ksqlDB CLI:
-- docker run --interactive --tty --rm confluentinc/ksqldb-cli:latest ksql http://ksqldb-server:8088

-- 1. Register existing Kafka topic as a STREAM (insert/event semantics):
CREATE STREAM orders_stream (
    order_id VARCHAR KEY,
    user_id VARCHAR,
    amount DOUBLE,
    status VARCHAR,
    event_time TIMESTAMP
) WITH (
    KAFKA_TOPIC='orders',
    VALUE_FORMAT='JSON',
    TIMESTAMP='event_time'  -- use event_time field as event timestamp
);

-- 2. Register as TABLE (upsert/state semantics, backed by compacted topic):
CREATE TABLE user_profiles (
    user_id VARCHAR PRIMARY KEY,
    email VARCHAR,
    tier VARCHAR,
    credit_limit DOUBLE
) WITH (
    KAFKA_TOPIC='user-profiles',
    VALUE_FORMAT='JSON'
);

-- 3. PERSISTENT QUERY: filter high-value orders (runs forever, writes to new topic)
CREATE STREAM high_value_orders AS
    SELECT
        order_id,
        user_id,
        amount,
        status
    FROM orders_stream
    WHERE amount > 1000
    EMIT CHANGES;
-- Creates new Kafka topic "HIGH_VALUE_ORDERS" populated continuously

-- 4. STREAM-TABLE JOIN: enrich each order event with current user profile
CREATE STREAM enriched_orders AS
    SELECT
        o.order_id,
        o.user_id,
        o.amount,
        u.email,
        u.tier,
        u.credit_limit
    FROM orders_stream o
    INNER JOIN user_profiles u ON o.user_id = u.user_id
    EMIT CHANGES;
-- Enriched stream continuously produced; uses latest profile for each join

-- 5. WINDOWED AGGREGATION: count orders per user per 5-minute window
CREATE TABLE order_counts_5min AS
    SELECT
        user_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_amount,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end
    FROM orders_stream
    WINDOW TUMBLING (SIZE 5 MINUTES)
    GROUP BY user_id
    EMIT CHANGES;

-- 6. FRAUD DETECTION: users with > 5 orders in 1 minute
CREATE TABLE rapid_buyers AS
    SELECT
        user_id,
        COUNT(*) AS order_count
    FROM orders_stream
    WINDOW TUMBLING (SIZE 1 MINUTES, GRACE PERIOD 30 SECONDS)
    GROUP BY user_id
    HAVING COUNT(*) > 5
    EMIT CHANGES;
-- GRACE PERIOD: wait 30s for late events before closing the window
```

**PULL QUERIES vs PUSH QUERIES:**

```sql
-- PULL QUERY (point-in-time, synchronous, returns immediately):
-- Use for: REST API responses, user-facing queries
SELECT * FROM order_counts_5min WHERE user_id = 'user-42';
-- Returns current count for user-42 from local RocksDB state store
-- Returns a finite result set (like a regular SQL query)

-- PUSH QUERY (continuous, subscribes to updates):
-- Use for: real-time dashboards, live monitoring feeds
SELECT user_id, order_count FROM order_counts_5min
WHERE order_count > 10
EMIT CHANGES;
-- Streams results continuously as counts update
-- Runs until client disconnects
-- Like a server-sent event stream from a database

-- Check query status:
SHOW QUERIES;
-- QUERY ID    | STATUS  | SINK TOPIC              | SINK SCHEMA
-- CSAS_HIGH_VALUE_ORDERS_0 | RUNNING | HIGH_VALUE_ORDERS | ...

-- Terminate a persistent query:
TERMINATE CSAS_HIGH_VALUE_ORDERS_0;
-- Note: this doesn't delete the output topic
```

**REST API - EMBED IN SPRING BOOT:**

```java
// ksqlDB exposes a REST API - query it from Java without ksql CLI
// Maven: io.confluent.ksql:ksqldb-api-client

@Service
public class KsqlDbService {

    private final Client ksqlDbClient;

    public KsqlDbService() {
        ClientOptions options = ClientOptions.create()
            .setHost("ksqldb-server")
            .setPort(8088);
        this.ksqlDbClient = Client.create(options);
    }

    // PULL query: get current state for a user
    public UserOrderStats getUserStats(String userId) throws ExecutionException, InterruptedException {
        String sql = "SELECT user_id, order_count, total_amount " +
                     "FROM order_counts_5min " +
                     "WHERE user_id = '" + userId + "';";
        // SECURITY NOTE: use parameterized queries or sanitize input!

        BatchedQueryResult result = ksqlDbClient.executeQuery(sql).get();
        if (result.isEmpty()) {
            return UserOrderStats.empty(userId);
        }
        Row row = result.getRows().get(0);
        return UserOrderStats.builder()
            .userId(row.getString("USER_ID"))
            .orderCount(row.getLong("ORDER_COUNT"))
            .totalAmount(row.getDouble("TOTAL_AMOUNT"))
            .build();
    }

    // PUSH query: subscribe to fraud alerts
    public void subscribeToFraudAlerts(Consumer<Row> alertHandler) {
        String sql = "SELECT * FROM rapid_buyers EMIT CHANGES;";
        ksqlDbClient.streamQuery(sql)
            .thenAccept(streamedQueryResult -> {
                streamedQueryResult.subscribe(new BaseSubscriber<Row>() {
                    @Override
                    public void onNext(Row row) {
                        alertHandler.accept(row);
                        request(1);  // request next row
                    }
                });
            });
    }
}
```

---

### 🧪 Thought Experiment

**WHEN KSQLDB vs KAFKA STREAMS vs FLINK:**

| Scenario                       | Best Tool                               |
| ------------------------------ | --------------------------------------- |
| Simple filter + project events | ksqlDB (SQL, no Java needed)            |
| Complex stateful custom logic  | Kafka Streams (Java) or Flink           |
| Stream-table join with SQL     | ksqlDB (native JOIN syntax)             |
| Machine learning inference     | Flink or Spark Streaming (ML libraries) |
| Ad-hoc SQL exploration         | ksqlDB interactive CLI                  |
| Low-latency fraud detection    | Flink (ksqlDB latency ~100ms+)          |
| Non-Kafka sources (S3, DB)     | Spark, Flink (ksqlDB is Kafka-only)     |

---

### 🧠 Mental Model / Analogy

> ksqlDB is like giving a data analyst a SQL query tool for a live database that never stops growing. Traditional SQL: query a static table. ksqlDB: query an ever-flowing event stream. "Give me all customers who spent > $100 in the last 5 minutes" - in traditional SQL, you'd query a materialized table updated periodically. In ksqlDB, you write a persistent SQL query that continuously maintains this result as new orders arrive.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** ksqlDB = SQL on Kafka. STREAM (events) + TABLE (state) maps to KStream + KTable. Persistent queries run forever (create new Kafka topics). Pull queries get current state. No Java needed. Use for simple streaming ETL.

**Level 2:** Persistent vs pull vs push queries. Stream-table join = event enrichment. Windowed aggregation: TUMBLING (fixed time), HOPPING (sliding), SESSION (activity-bounded). HAVING filters on aggregated results. GRACE PERIOD for late data.

**Level 3:** ksqlDB compiles SQL to Kafka Streams topology under the hood. Each persistent query = one Kafka Streams application. Scaling: ksqlDB server cluster → distribute query tasks across nodes. Connector integration: ksqlDB can manage Kafka Connect connectors (source/sink) via SQL: `CREATE SOURCE CONNECTOR ...`.

**Level 4:** ksqlDB REST API enables microservices to do pull queries without maintaining a KTable state store themselves - the ksqlDB server maintains the state, services query it. This creates an operational dependency (ksqlDB server must be available for pull queries). Tradeoff: operational simplicity (no state management in each service) vs. availability coupling. Production: ksqlDB server cluster with multiple nodes; queries are distributed, state is replicated. Monitoring: ksqlDB server exposes JMX + REST metrics. Common production issue: persistent query consumer lag - monitor `show queries` LAG metric.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KSQLDB ARCHITECTURE                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ksqlDB CLI / REST Client                           │
│       │ CREATE STREAM enriched_orders AS ...        │
│       ↓                                              │
│  [ksqlDB Server]                                     │
│   → Parse SQL                                        │
│   → Compile to Kafka Streams Topology               │
│   → Submit as persistent query                       │
│  [KSQLDB ← YOU ARE HERE: SQL→KafkaStreams compiler]  │
│                                                      │
│  Kafka Cluster:                                      │
│   "orders" (source) → [persistent query running     │
│                         as KafkaStreams internally]  │
│                       → "enriched_orders" (output)  │
│                                                      │
│  ksqlDB state stores (RocksDB): TABLE materializations│
│  Pull query → query RocksDB in ksqlDB server        │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Real-time fraud monitoring with ksqlDB:

1. Create stream (once):
   CREATE STREAM txns (user_id VARCHAR KEY, amount DOUBLE, ts TIMESTAMP)
   WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT='JSON');

2. Create persistent fraud detection query (runs forever):
   CREATE TABLE fraud_alerts AS
   SELECT user_id, COUNT(*) as txn_count
   FROM txns
   WINDOW TUMBLING (SIZE 1 MINUTES)
   GROUP BY user_id
   HAVING COUNT(*) > 5;
   → Creates Kafka topic "FRAUD_ALERTS" updated continuously

3. At T=12:00:00, user-42 sends 6 transactions within 1 minute:
   ksqlDB: COUNT(*) for user-42 in window [12:00,12:01] reaches 6 → HAVING clause met
   → Record written to "FRAUD_ALERTS" topic: {user_id: user-42, txn_count: 6}

4. Fraud response service consumes "FRAUD_ALERTS" topic:
   → Blocks user-42's card

5. REST API pull query (user portal):
   GET /query → SELECT * FROM fraud_alerts WHERE user_id='user-42'
   → Returns current count in RocksDB state store
   → Response in <5ms
```

---

### ⚖️ Comparison Table

| Feature           | ksqlDB                       | Kafka Streams                      | Apache Flink                   |
| ----------------- | ---------------------------- | ---------------------------------- | ------------------------------ |
| Language          | SQL                          | Java/Scala                         | Java/Scala/Python/SQL          |
| Learning curve    | Low (SQL)                    | Medium (streaming concepts + Java) | High                           |
| Flexibility       | Limited (SQL expressiveness) | High (full Java)                   | Very high                      |
| Latency           | 100ms+                       | 1-100ms                            | 1-10ms                         |
| Deployment        | Separate ksqlDB server       | Library in app                     | Separate cluster               |
| Non-Kafka sources | No                           | No                                 | Yes                            |
| Best for          | SQL-savvy teams, simple ETL  | Java teams, medium complexity      | Complex real-time, low latency |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "ksqlDB is a real-time OLAP database" | ksqlDB is a stream processor with SQL syntax. Pull queries can query current state, but it's not a general-purpose analytics database (no ad-hoc historical queries)       |
| "ksqlDB replaces Kafka Streams"       | ksqlDB compiles to Kafka Streams. Complex logic requiring custom stateful operators, ML, or Java libraries can't be expressed in SQL - use Kafka Streams or Flink directly |
| "ksqlDB handles any SQL"              | ksqlDB is a streaming SQL dialect - not ANSI SQL. Subqueries have limitations, some JOIN types aren't supported, and temporal semantics differ from batch SQL              |

---

### 🚨 Failure Modes & Diagnosis

**1. Persistent Query Falls Behind (Consumer Lag)**

**Symptom:** `SHOW QUERIES` shows `LAG` growing. Real-time alerts are delayed by 10+ minutes.

**Root Cause:** Persistent query processes events slower than they're produced. Could be complex SQL (expensive join), slow state store access (too large), or insufficient ksqlDB server capacity.

**Diagnosis:**

```sql
SHOW QUERIES EXTENDED;
-- Look at: CONSUMER_OFFSET_LAG per query
-- Also: ksqlDB JMX metrics: ksql.query.status.QUERY_ID.*
```

**Fix:**

1. Scale ksqlDB cluster: add more server nodes, partitions redistribute.
2. Simplify query: remove expensive operations (large state join, multiple aggregations).
3. Increase ksqlDB heap: `KSQL_HEAP_OPTS=-Xmx4g` for more state store caching.
4. Upgrade to ksqlDB 0.26+ for performance improvements.

---

### 🔗 Related Keywords

**Prerequisites:** Kafka Streams, Apache Kafka
**Builds On This:** KTable vs KStream
**Related:** Kafka Streams, KTable vs KStream, Kafka Topic / Partition / Offset

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STREAM      │ Kafka topic as event stream (INSERT)        │
│ TABLE       │ Kafka compacted topic as state (UPSERT)    │
│ PERSISTENT  │ CREATE STREAM/TABLE AS SELECT → new topic │
│ PULL QUERY  │ SELECT WHERE → current state from RocksDB │
│ PUSH QUERY  │ SELECT EMIT CHANGES → continuous stream    │
│ WINDOWING   │ TUMBLING / HOPPING / SESSION windows       │
│ GRACE PERIOD│ Wait N seconds for late events             │
│ vs KSTREAMS │ ksqlDB is SQL; KStreams is Java library     │
│ LATENCY     │ ~100ms+ (not for sub-10ms requirements)    │
│ ONE-LINER   │ "SQL on Kafka: persistent queries filter  │
│             │  and aggregate streams into new topics"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between a push query and a pull query in ksqlDB? When would you use each? How do they map to underlying Kafka Streams concepts?

**Q2.** (TYPE C - Design) A logistics company tracks shipment events (PICKED_UP, IN_TRANSIT, DELIVERED) in Kafka. Build a ksqlDB solution to: (1) maintain current status of all shipments, (2) alert when a shipment has been IN_TRANSIT for > 48 hours, (3) expose a REST endpoint for tracking a specific shipment.
