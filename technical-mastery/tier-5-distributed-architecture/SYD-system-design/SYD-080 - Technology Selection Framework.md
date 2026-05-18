---
id: SYD-080
title: Technology Selection Framework
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001
used_by: ""
related: SYD-001, SYD-002, SYD-003, SYD-079, SYD-052
tags:
  - architecture
  - decision
  - framework
  - trade-offs
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/syd/technology-selection-framework/
---

⚡ TL;DR - Choosing between Redis and Memcached, Kafka
and RabbitMQ, PostgreSQL and Cassandra is not about
preferences - it is about matching technology
characteristics to workload characteristics. Framework:
(1) Define the workload - read:write ratio, latency
requirements, consistency needs, scale target;
(2) Identify the deciding constraint - is it throughput,
latency, consistency, or operational complexity?
(3) Map workload to technology characteristics;
(4) Evaluate trade-offs explicitly (what you gain and
what you give up); (5) Validate with a proof of concept.
The wrong answer in a design interview is "I'd use
[popular technology]" without justification. The right
answer is "This workload has property X, which maps to
technology Y because it handles X better than Z does."

| #080 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | System Design Process | |
| **Related:** | System Design Process, Scalability Fundamentals, High Availability Design, System Design Interview Preparation Guide, Distributed Cache Design | |

---

### 🔥 The Problem This Solves

"We need a database for our new service. Should we use
PostgreSQL or MongoDB?" This is one of the most common
questions in engineering, and one of the most poorly
answered. Bad answer: "MongoDB is more modern / flexible."
Good answer: "What is the access pattern? If we need
complex queries across multiple fields with consistency
guarantees, PostgreSQL. If we need document flexibility
with high write throughput and schema evolution, MongoDB.
What is the QPS? What is the latency requirement? Does
this need strong consistency?" The framework makes
technology selection systematic rather than based on
hype or familiarity.

---

### 📘 Textbook Definition

**Technology selection framework:** A structured process
for choosing between technologies based on workload
characteristics, constraints, and trade-offs rather than
familiarity or popularity.

**Workload characterization:** The process of measuring
or estimating the key properties of a workload: QPS
(queries per second), read:write ratio, data access
patterns (random vs. sequential), data model complexity,
consistency requirements, latency SLO.

**Technology fit:** The degree to which a technology's
design characteristics match the workload's requirements.
High fit = the technology was designed for this workload.
Low fit = the technology can be forced to work, but with
significant operational overhead or performance compromise.

**Decision constraint:** The single most important factor
that determines which technology is most appropriate.
Often: consistency vs. availability, write throughput vs.
query flexibility, operational simplicity vs. performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Define workload → identify deciding constraint → match
to technology characteristics → evaluate trade-offs →
validate with PoC.

**One analogy:**
> Choosing a database is like choosing a vehicle:
>
> You don't choose a Formula 1 car for commuting
> (fast on straight roads, useless in traffic, no trunk).
> You don't choose a minivan for racing.
>
> The right vehicle depends on the workload:
> Daily commute 20 miles: economy car (efficient).
> Moving furniture: pickup truck (capacity).
> Racing: sports car (raw performance).
> Off-road expedition: 4x4 (durability under stress).
>
> Database selection:
> OLTP (user sessions, orders): PostgreSQL (consistency).
> Time series (IoT metrics): InfluxDB or Cassandra.
> Graph (social network): Neo4j.
> Cache (fast reads): Redis.
> Full-text search: Elasticsearch.
>
> Using PostgreSQL for everything "because we know it"
> is like driving a minivan to a race: it technically
> works but is suboptimal.

**One insight:**
The most important question to ask before selecting a
technology is not "what can this technology do?" but
"what is the workload's deciding constraint?" If the
deciding constraint is write throughput at 100K writes/sec,
all technologies that cannot handle 100K writes/sec are
eliminated regardless of their other properties. The
framework is about defining the decision boundary first,
then eliminating technologies that don't meet it,
then choosing among the survivors based on secondary
criteria (operational complexity, cost, team familiarity).

---

### 🔩 First Principles Explanation

**STEP 1: DEFINE THE WORKLOAD**
```
Eight dimensions to measure or estimate:

1. Read:Write ratio
   Read-heavy (>10:1): optimize for reads.
   Write-heavy (1:10): optimize for writes.
   Balanced: need both.

2. QPS (queries per second)
   < 1K: almost any database works.
   1K-10K: need connection pooling, possibly caching.
   10K-100K: need read replicas, horizontal scale.
   > 100K: need distributed DB, aggressive caching.

3. Latency requirement (p99)
   < 10ms: need in-memory or very fast storage.
   < 100ms: standard SSD-backed DB is fine.
   < 1s: batch processing acceptable for non-real-time.

4. Data model complexity
   Simple key-value: Redis, DynamoDB.
   Document (nested JSON): MongoDB, DynamoDB.
   Relational (joins, foreign keys): PostgreSQL, MySQL.
   Time series (timestamp-ordered): InfluxDB, Cassandra.
   Graph (node-edge): Neo4j, Amazon Neptune.
   Full-text search: Elasticsearch, Solr.

5. Consistency requirement
   Strong: every read sees latest write.
   Eventual: reads may be slightly stale (milliseconds).
   Causal: if you write then read, you see your write.

6. Scale target
   Current + 12-month projection + 5-year worst case.
   Factor of 10x headroom minimum.

7. Access pattern
   Random point lookups (by ID): hash index, B-tree.
   Range scans (by time, by range): B-tree, LSM tree.
   Full-text search: inverted index.
   Aggregation: columnar storage.

8. Durability requirement
   Cache (loss tolerable): in-memory, Redis without AOF.
   Important (some loss acceptable): async replication.
   Critical (zero loss): synchronous replication, WAL.
```

**STEP 2: IDENTIFY THE DECIDING CONSTRAINT**
```
The deciding constraint is the requirement that
eliminates the most technology options.

Example 1: "Chat message storage, 1M users, 
            100K message writes/sec."
  The deciding constraint: write throughput (100K/s).
  
  Eliminates: PostgreSQL (single-writer limit ~10K/s),
              MySQL (similar), MongoDB (similar).
  Survives: Cassandra (100K+ writes/s per node),
            HBase (100K+ writes/s), DynamoDB.
  
  Secondary criteria: operational complexity, team
  familiarity, cloud vs. self-hosted.
  → Cassandra (team has experience) or DynamoDB
    (managed, less operational overhead).

Example 2: "E-commerce order storage, 10K orders/sec,
            requires ACID transactions."
  The deciding constraint: ACID transactions.
  
  Eliminates: Cassandra (no multi-row ACID),
              DynamoDB (no cross-partition ACID),
              Redis (no persistence-first ACID).
  Survives: PostgreSQL, MySQL, CockroachDB.
  
  Secondary criteria: 10K orders/sec → read replicas
  for PostgreSQL (single primary handles ~10K writes/s
  with write-ahead logging).
  → PostgreSQL with read replicas for report queries.
```

**STEP 3: DATABASE DECISION MAP**
```
WORKLOAD → TECHNOLOGY CHOICES

Session storage / cache:
  Redis (complex structures: sorted sets, hashes).
  Memcached (simple key-value, multi-thread friendly).
  
  Choose Redis if: need sorted sets (leaderboard),
  pub/sub, atomic increment, expiry per key.
  Choose Memcached if: pure caching, all values same
  type, want simpler ops with better multi-threading.

Time series data (metrics, logs, IoT):
  InfluxDB (purpose-built: retention policies,
            continuous queries, downsampling).
  Cassandra (high write throughput, LSM tree,
             needs custom time-series schema).
  TimescaleDB (PostgreSQL extension: familiar SQL,
               automatic partitioning by time).
  
  Choose InfluxDB: primary use case is metrics.
  Choose Cassandra: already in stack, need 100K+ writes.
  Choose TimescaleDB: team knows SQL, mixed workload.

Document storage:
  MongoDB (flexible schema, rich query, aggregation
            pipeline, change streams).
  DynamoDB (key-value + simple query, managed,
             high QPS, no complex aggregation).
  Couchbase (MongoDB-like but with built-in cache).
  
  Choose MongoDB: complex queries, flexible schema,
  need full-text search (Atlas Search).
  Choose DynamoDB: need managed, high throughput,
  access pattern is mostly key-value.

Search:
  Elasticsearch (full-text search, aggregations,
                  geospatial, near real-time index).
  Algolia (managed, extremely fast, easy to use,
           high cost at scale).
  PostgreSQL full-text search (tsvector): simple
  search needs, no separate service.
  
  Choose Elasticsearch: complex search, analytics.
  Choose Algolia: ease of use > cost.
  Choose PostgreSQL: search is a minor feature.

Message queues:
  Kafka (high throughput, durable, replay, partitioned
         streams, exactly-once semantics).
  RabbitMQ (low latency, complex routing, fanout,
            dead-letter queues, simple setup).
  AWS SQS (managed, at-least-once, FIFO option).
  
  Choose Kafka: need replay, high throughput (100K+/s),
  event streaming, multiple consumers.
  Choose RabbitMQ: task queues, routing, low-latency,
  need dead-letter handling out of the box.
  Choose SQS: AWS-native, don't want to manage infra,
  standard queue needs.
```

**STEP 4: EVALUATE TRADE-OFFS EXPLICITLY**
```
Good trade-off statement format:
"We chose [TECHNOLOGY] over [ALTERNATIVE] because
[DECIDING CONSTRAINT] requires [CHARACTERISTIC].
The trade-off: we gain [BENEFIT] but sacrifice
[COST]. We mitigate [COST] by [MITIGATION]."

Example - Kafka vs. RabbitMQ:
"We chose Kafka over RabbitMQ because our 100K
events/sec write requirement exceeds RabbitMQ's
typical throughput ceiling (10-20K events/sec without
sharding). Kafka's partitioned log design handles
100K+ events/sec per partition. The trade-off: we
gain throughput and replay capability but sacrifice
simplicity. Kafka has higher operational complexity
(ZooKeeper or KRaft, partition management, consumer
group offsets). We mitigate this with a managed
Kafka service (Confluent Cloud or AWS MSK) to reduce
the operational burden."

Example - PostgreSQL vs. Cassandra:
"We chose Cassandra over PostgreSQL for chat message
storage because we need 100K writes/sec with linear
horizontal scaling. PostgreSQL's single-primary
architecture cannot scale writes horizontally.
The trade-off: we gain write throughput but sacrifice
ACID transactions and complex queries. Chat messages
don't require cross-message transactions (each message
is independent), so this trade-off is acceptable.
We lose JOINs: we denormalize by storing messages
with user metadata inline (de-normalized reads)."
```

---

### 🧪 Thought Experiment

**The Notification Service: Kafka vs. SQS vs. RabbitMQ**

Scenario: design a notification service.
100M users. Push notifications (mobile) + email.
~100K notification events/sec at peak.
Notifications must be delivered at least once.
Delivery order: not important (two notifications can
arrive in any order).

Analysis:
  Write throughput: 100K/sec. All three can handle this.
  Replay: not needed (notifications are time-sensitive;
  a 24-hour-old notification is irrelevant after delivery).
  Complex routing: not needed (route by notification type).
  Managed service: preferred (reduce ops burden).
  Multi-consumer: 2 consumers (push and email workers).

Decision matrix:
  Kafka: over-engineered for this use case. Replay is
  not needed. Partition management adds ops complexity.
  Kafka excels at event streaming with replay; this is
  a task queue.
  
  RabbitMQ: good fit. Handles 100K/sec. Dead-letter
  queues for failed deliveries. Easy multi-consumer
  (exchange → push queue + email queue). Needs
  self-hosted ops.
  
  AWS SQS: best fit for managed ops. Fan-out: use SNS
  (Simple Notification Service) to fan out one message
  to both SQS queues (push + email). At-least-once.
  FIFO not needed. Zero ops overhead.

Decision: AWS SQS + SNS fan-out.
  Gain: managed service, zero ops, pay-per-use.
  Lose: no replay (acceptable), slightly higher latency
  than RabbitMQ (acceptable for notifications).

Lesson: the technically impressive answer (Kafka)
is not always the right answer. Match the tool to
the actual requirements.

---

### 🧠 Mental Model / Analogy

> Technology selection is like prescribing medicine:
>
> A doctor doesn't prescribe the same medication for
> every patient just because it worked well before.
> They diagnose the specific condition, identify the
> deciding constraint (severity, allergies, other meds),
> choose the appropriate treatment, and explain the
> trade-offs ("this treats the infection but may cause
> nausea; take with food").
>
> An engineer who defaults to the same technology for
> every project is like a doctor who prescribes the
> same medication to every patient. Sometimes it works.
> Often it's suboptimal. Occasionally it causes harm.
>
> The framework is the diagnosis process:
> Define the workload (symptoms) → identify the deciding
> constraint (root cause) → match to technology
> (treatment) → evaluate trade-offs (side effects).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Choosing the right technology is about matching the
tool to the job. A relational database is great for
orders and transactions. A cache is great for fast
reads. A message queue is great for background processing.
The framework helps you choose by asking: what does
this system need to do, and which tool is best designed
for that?

**Level 2 - How to use it (junior developer):**
Five steps: define workload (read:write, QPS, latency),
identify deciding constraint (what eliminates options),
map workload to technology, evaluate trade-offs, validate
with PoC. Know the basic decision tree: ACID needed?
→ SQL. High write throughput, no joins? → Cassandra.
Fast cache? → Redis. Message queue? → Kafka for streams,
RabbitMQ for task queues, SQS for managed simplicity.

**Level 3 - How it works (mid-level engineer):**
The framework works because each technology was designed
for a specific set of workload characteristics. PostgreSQL:
B-tree indexes, MVCC for concurrent reads, WAL for
durability - optimized for consistent, flexible queries.
Cassandra: LSM tree, consistent hashing, W/R quorum -
optimized for high write throughput and horizontal scale.
Redis: in-memory, single-threaded command execution -
optimized for microsecond reads on hot data. Choosing
correctly means understanding what problem the technology
was designed to solve.

**Level 4 - Why it was designed this way (senior/staff):**
The framework formalizes what experienced engineers do
instinctively: they recognize workload patterns from
experience and immediately know which technology fits.
A senior engineer who has operated Cassandra at scale
knows its failure modes (tombstone accumulation,
write amplification in compaction, read performance on
non-partition-key queries). This knowledge informs
the decision: Cassandra is a great choice for high-write,
key-based access, but painful to operate for ad-hoc
query needs. The framework captures this experiential
reasoning in a structured form that junior engineers
can follow and senior engineers can communicate to
stakeholders who are not distributed systems experts.

**Level 5 - Mastery (distinguished engineer):**
The most sophisticated technology selections account
for the operational dimension that static performance
benchmarks miss. A technology that performs better in
isolation may be the wrong choice if: (1) the team has
deep expertise in the alternative (expertise eliminates
failure modes that would otherwise occur); (2) the
company's existing infrastructure ecosystem has better
tooling for one option (unified monitoring, backup
automation, runbooks for incident response); (3) the
technology's operational model under failure is
unacceptable (Cassandra under network partition with
a non-expert team becomes a data consistency nightmare).
Distinguished engineers weight operational reality as
heavily as performance characteristics.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ TECHNOLOGY SELECTION DECISION FLOW                  │
│                                                      │
│ DEFINE WORKLOAD                                    │
│  → Read:Write ratio, QPS, latency, consistency    │
│  → Data model, access pattern, scale target       │
│                                                      │
│ IDENTIFY DECIDING CONSTRAINT                       │
│  → What eliminates most options?                  │
│  → Write throughput? Consistency? Latency?        │
│    Query complexity? Operational simplicity?      │
│                                                      │
│ ELIMINATE NON-FITS                                 │
│  → List technologies that can't meet the          │
│    deciding constraint.                           │
│  → Remove them from consideration.               │
│                                                      │
│ RANK SURVIVORS                                     │
│  → By secondary criteria: ops complexity,        │
│    team expertise, cost, ecosystem fit.          │
│                                                      │
│ EVALUATE TRADE-OFFS                                │
│  → What does the winner give us?                 │
│  → What does it cost?                            │
│  → How do we mitigate the cost?                 │
│                                                      │
│ VALIDATE                                           │
│  → Proof of concept (PoC) for uncertain choices.  │
│  → Load test at 2x projected peak before commit.  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Database selection decision table**
```
# TECHNOLOGY SELECTION QUICK REFERENCE

## Storage / Databases

### RELATIONAL (ACID, complex queries)
  PostgreSQL:
    Pros: ACID, rich query (joins, CTEs, window funcs),
          mature ecosystem, JSONB for flexible fields,
          excellent for OLTP + light analytics.
    Cons: single-primary write bottleneck (~10K writes/s),
          vertical scale limit (~5-10TB with good
            indexing).
    Choose when: consistency required, complex queries,
                 team knows SQL, < 100K writes/sec.
  
  MySQL:
    Pros: widely known, good replication, Vitess for scale.
    Cons: less feature-rich than PostgreSQL (no partial
          indexes, limited window functions until 8.0).
    Choose when: team is MySQL-first, using Vitess.

### WIDE-COLUMN (high write throughput, horizontal scale)
  Cassandra:
    Pros: 100K+ writes/sec, linear horizontal scale,
          tunable consistency, excellent for time series
          and append-only workloads.
    Cons: no joins, no aggregation, no ACID
      cross-partition,
          tombstone accumulation, compaction overhead.
    Operational: complex (tuning compaction, heap sizing).
    Choose when: 100K+ writes/sec, key-based access only,
                 eventual consistency OK, team has ops
                   expertise.

### DOCUMENT (flexible schema, nested data)
  MongoDB:
    Pros: flexible schema, rich aggregation pipeline,
          geospatial, change streams, full-text search.
    Cons: no cross-document transactions (unless with
          multi-document transaction, which is slower).
    Choose when: document-centric data model, flexible
                 schema needed, complex aggregation.

### CACHE (in-memory, microsecond reads)
  Redis:
    Pros: microsecond latency, rich data structures
          (sorted sets, hashes, streams, pub/sub),
          atomic operations, TTL per key.
    Cons: in-memory = expensive at large scale,
          data loss without AOF/RDB persistence.
    Choose when: hot data cache, leaderboard, session,
                 rate limiting, pub/sub, distributed lock.

  Memcached:
    Pros: simpler, multi-threaded (better CPU utilization),
          slightly lower memory overhead for pure KV.
    Cons: no persistence, no rich data structures,
          no replication built-in.
    Choose when: pure caching, all values are strings,
                 need max throughput per CPU core.

## Message Queues

  Kafka:
    Pros: 100K+ events/sec, durable log (replay),
          partitioned (parallel consumers), exactly-once
          semantics (with transactions), streams API.
    Cons: high operational complexity (partition
          management, consumer group offsets, Zookeeper),
          high latency vs. RabbitMQ (ms vs. sub-ms).
    Choose when: event streaming, need replay, multiple
                 consumers, high throughput.

  RabbitMQ:
    Pros: low latency (sub-millisecond), dead-letter
          queues out of box, complex routing (topic,
          fanout, direct exchanges), simpler ops.
    Cons: no replay (messages deleted after ACK),
          limited throughput (10-20K/sec per queue
          without clustering).
    Choose when: task queues, low latency critical,
                 complex routing, DLQ required.

  AWS SQS / GCP Pub/Sub:
    Pros: fully managed, no ops, scales to millions/sec.
    Cons: no replay (SQS), higher latency than RabbitMQ,
          limited control over delivery semantics.
    Choose when: managed ops > performance, AWS/GCP-native.
```

**Example 2 - Trade-off documentation template**
```
# TECHNOLOGY DECISION RECORD (TDR)
# Use this format when documenting technology choices.

---
Decision: [Technology choice]
Date: [YYYY-MM-DD]
Decided By: [Team/individuals]
Status: [Proposed | Accepted | Deprecated]

## Context
[What workload are we designing for?]
[What are the key requirements and constraints?]

## Workload Characteristics
- Read:Write ratio: ___:1
- Peak QPS: ___K reads/sec, ___K writes/sec
- Latency requirement: < ___ms (p99)
- Consistency: Strong / Eventual / Causal
- Scale target: ___TB data, ___K QPS in 2 years
- Data model: [Relational / Document / Time series / KV]

## Decision Constraint
[What single characteristic eliminates most options?]
Example: "Must handle 100K writes/sec - eliminates
         all single-primary SQL databases."

## Alternatives Considered
| Technology | Eliminates? | Reason |
|---|---|---|
| [Alt 1]    | Yes/No      | [Why eliminated or kept] |
| [Alt 2]    | Yes/No      | [Why eliminated or kept] |
| [Chosen]   | No          | [Best fit - why] |

## Decision
We chose [TECHNOLOGY] because [DECIDING REASON].

## Trade-offs
Gains: [What this choice provides]
Costs: [What this choice sacrifices]
Mitigation: [How we address the costs]

## Validation Plan
[ ] PoC: load test at 2x peak QPS
[ ] Failure test: kill a node, verify recovery
[ ] Monitoring: which metrics indicate degradation?
```

---

### ⚖️ Comparison Table

| Technology | Best For | Deciding Constraint | Avoid When |
|---|---|---|---|
| **PostgreSQL** | OLTP, complex queries | ACID + flexible queries | > 100K writes/sec |
| **Cassandra** | Write-heavy, time series | Write throughput scale | Need complex queries |
| **Redis** | Hot cache, leaderboard | Sub-millisecond latency | Dataset > memory budget |
| **MongoDB** | Document-centric apps | Flexible schema, nested data | Need strict consistency |
| **Kafka** | Event streaming, replay | High throughput + durability | Low-latency task queue |
| **RabbitMQ** | Task queues, routing | Low latency + DLQ | Need replay or 100K+/sec |
| **Elasticsearch** | Full-text search | Rich search queries | Source of truth storage |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Use Kafka for everything that involves events | Kafka is optimized for high-throughput event streaming where consumers need to replay the log and multiple independent consumer groups need the same events. For a simple background task queue (send email after user signup), RabbitMQ or SQS is a better fit: simpler, lower latency, built-in dead-letter handling, no consumer offset management. Kafka for a simple task queue is like using a semi-truck to deliver a letter. It works, but it's over-engineered, more complex to operate, and the operational overhead is disproportionate to the value. |
| Strong consistency is always better than eventual | Strong consistency comes with availability and latency costs. During a network partition, a CP system (strong consistency) becomes unavailable until the partition is resolved. For a shopping cart (slight staleness is acceptable), this means users cannot access their cart during a network event. Eventual consistency (AP) keeps the system available at the cost of potentially stale reads. The right choice depends on the business impact: data staleness vs. unavailability. There is no universally better option - only fit to the use case. |
| Using the technology you know is always safe | "We'll use PostgreSQL because we know it" is reasonable for small scale. At large scale, using a technology outside its design envelope because of familiarity creates worse problems than learning a new technology. A team that is unfamiliar with Cassandra but forces everything into PostgreSQL at 1M writes/sec will spend more time fighting database bottlenecks than they would have spent learning Cassandra. Operational familiarity is a valid selection criterion, but it is one factor, not the only factor. |

---

### 🚨 Failure Modes & Diagnosis

**Using PostgreSQL Beyond Its Write Throughput Limit**

**Symptom:**
Write latency for INSERT/UPDATE climbing from 5ms to
500ms. CPU on the database server at 95%. Connection
pool exhausted (all 200 connections busy). Application
errors: "too many connections" or "statement timeout."
Engineering team: "the database is too slow."

**Root Cause:**
Single-primary PostgreSQL handling 50K+ writes/sec.
B-tree index maintenance (O(log N) per write) and
WAL write amplification create write bottleneck.
Single primary cannot be scaled horizontally.

**Diagnosis:**
```sql
-- PostgreSQL: identify write throughput
SELECT schemaname, tablename,
       n_tup_ins + n_tup_upd + n_tup_del AS total_writes,
       n_live_tup
FROM pg_stat_user_tables
ORDER BY total_writes DESC
LIMIT 10;

-- Check autovacuum: is it keeping up?
SELECT relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- Identify expensive write queries
SELECT query, total_exec_time, calls,
       mean_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%INSERT%' OR query ILIKE '%UPDATE%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

**Fix (progressive scale-up plan):**
```
Phase 1 (immediate relief):
  - Add write-ahead log (WAL) archiving to reduce
    synchronous checkpoint frequency.
  - Tune: max_wal_size, checkpoint_completion_target.
  - Batch writes: instead of 10K individual INSERTs,
    use COPY or multi-row INSERT (1 round trip = N rows).

Phase 2 (medium-term):
  - Partition the high-write table by time or range.
    Each partition is a smaller B-tree: less write
    amplification per partition.
  - Read replicas: move all reads off primary.
    Primary handles only writes.

Phase 3 (long-term):
  - If writes still exceed ~50K/sec after Phase 2:
    evaluate migrating the write-heavy portion to
    Cassandra or DynamoDB (with clear trade-off analysis).
  - The transition: dual-write pattern while migrating.
    New records → Cassandra + PostgreSQL.
    Old records → read from PostgreSQL.
    After validation: cutover reads to Cassandra.
    Deprecate PostgreSQL for this workload.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design Process` - the broader design process
  within which technology selection occurs

**Builds On This (learn these next):**
- `Scalability Fundamentals` - understanding the scale
  characteristics that drive technology selection
- `High Availability Design` - availability requirements
  are a key input to technology selection
- `Distributed Cache Design` - applying the framework
  specifically to cache technology selection
- `System Design Interview Preparation Guide` - how
  to use this framework in interview contexts

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1     │ Define workload: R:W ratio, QPS, latency, │
│            │ consistency, data model, scale target.    │
├────────────┼──────────────────────────────────────────┤
  │
│ STEP 2     │ Identify deciding constraint: what         │
│            │ eliminates most options?                  │
├────────────┼──────────────────────────────────────────┤
  │
│ STEP 3     │ Eliminate non-fits. Rank survivors by      │
│            │ secondary criteria.                       │
├────────────┼──────────────────────────────────────────┤
  │
│ STEP 4     │ Trade-off: gain X, sacrifice Y,           │
│            │ mitigate Y by Z.                         │
├────────────┼──────────────────────────────────────────┤
  │
│ STEP 5     │ Validate: PoC, load test at 2x peak.     │
├────────────┼──────────────────────────────────────────┤
  │
│ CHEAT      │ ACID+complex queries → PostgreSQL.       │
│ SHEET      │ 100K+ writes/sec → Cassandra.           │
│            │ Sub-ms reads/hot data → Redis.          │
│            │ Event streaming+replay → Kafka.         │
│            │ Task queue+DLQ → RabbitMQ.             │
│            │ Full-text search → Elasticsearch.       │
├────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER  │ "Match tool to workload, not to          │
│            │  team preference or hype."              │
├────────────┼──────────────────────────────────────────┤
  │
│ NEXT       │ Microservices vs. Monolith Decision        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always define the workload before choosing a technology.
   Read:write ratio, QPS, latency requirement, consistency
   need, and data model are the five key dimensions.
   Skip this step and you're choosing by familiarity or
   hype, not fitness.
2. Identify the deciding constraint first. The deciding
   constraint is what eliminates the most options. If
   the constraint is 100K writes/sec, PostgreSQL is
   eliminated regardless of how well the team knows it.
   Work from constraints to candidates, not from
   candidates to justifications.
3. Always state trade-offs explicitly: "We gain X but
   sacrifice Y. We mitigate Y by Z." A technology
   selection without trade-off analysis is incomplete.
   Every technology is a compromise. The job is to
   make the right compromise for the specific workload.

**Interview one-liner:**
"Technology selection: define workload (read:write ratio, QPS, latency, consistency,
data model, scale); identify deciding constraint (what eliminates most options); match
to technology: ACID + complex queries → PostgreSQL; 100K+ writes/sec horizontal scale
→ Cassandra; sub-ms hot reads → Redis; event streaming with replay → Kafka; task
queue with DLQ → RabbitMQ; full-text search → Elasticsearch. Always state trade-offs:
'We gain X, sacrifice Y, mitigate Y by Z.' Validate with PoC at 2x projected peak
QPS before committing."
