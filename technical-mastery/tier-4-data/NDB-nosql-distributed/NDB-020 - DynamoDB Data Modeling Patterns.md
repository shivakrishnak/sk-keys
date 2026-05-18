---
version: 2
layout: default
title: "DynamoDB Data Modeling Patterns"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/nosql/dynamodb-data-modeling-patterns/
id: NDB-023
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: DynamoDB, NoSQL, Distributed Systems
used_by: DynamoDB Single-Table Design, AWS
related: DynamoDB Single-Table Design, MongoDB Document Schema Design, Key-Value Store
tags:
  - database
  - aws
  - distributed
  - advanced
  - pattern
---

⚡ TL;DR - DynamoDB data modeling starts with access patterns, not entities; partition key design prevents hot partitions, and GSI/LSI provide alternate query dimensions without table scans.

| Relation | Keywords |
|---|---|
| Depends on | DynamoDB, NoSQL, Distributed Systems |
| Used by | DynamoDB Single-Table Design, AWS |
| Related | DynamoDB Single-Table Design, MongoDB Document Schema Design, Key-Value Store |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A developer models a DynamoDB table the same way they would model a relational database - one table per entity, `userId` as the partition key. The application launches. User reads are fast. Then the analytics team adds a query: "get all orders for a user sorted by date." This requires a GSI that was never planned. Next month: "get all pending orders across all users." This is an impossible query in DynamoDB without a table scan or a pre-designed secondary index. The team is constantly adding GSIs reactively, never getting the access patterns right.

**THE BREAKING POINT:** A social media platform uses `userId` as the partition key for a `posts` table. A celebrity with 100 million followers creates 50 posts per day. All writes for that user's posts land on the same partition - the same physical shard. DynamoDB's partition throughput limit (3 000 RCUs, 1 000 WCUs per partition) is exhausted. Other users on the same physical shard experience throttling. This is the hot partition problem - and it cannot be fixed without re-modeling the partition key.

**THE INVENTION MOMENT:** DynamoDB data modeling is a discipline that starts from a list of access patterns (every query the application will ever need) and designs partition keys, sort keys, and GSIs specifically to serve those patterns at scale. The partition key design must distribute traffic uniformly. The sort key design must enable range queries within a partition. GSIs must be pre-planned - they cannot be retrofit without data cost.

---

### 📘 Textbook Definition

**DynamoDB Data Modeling Patterns** are the systematic techniques for designing tables, partition keys, sort keys, Global Secondary Indexes (GSIs), and Local Secondary Indexes (LSIs) to serve all application access patterns at scale in Amazon DynamoDB. Key patterns include: **write sharding** (appending random suffixes to high-traffic partition keys), **sparse indexes** (GSIs that index only a subset of items), **time-series patterns** (separate tables per time period), the **adjacency list pattern** (representing graph relationships in a single table), and **overloaded GSI attributes** (a GSI partition key that holds different entity-type-specific values). All patterns derive from the principle that DynamoDB queries must be predictable, partition-local, and access-pattern-driven.

---

### ⏱️ Understand It in 30 Seconds

**One line:** In DynamoDB, your schema is your query plan - design the partition key to distribute traffic, the sort key to filter within a partition, and GSIs to handle every access pattern you need before you ship.

> Think of DynamoDB partitions like mailboxes in a post office. If every letter is addressed to the same mailbox (hot partition key), one postal worker is overwhelmed while the rest are idle. The fix is not a bigger mailbox - it is redesigning the address scheme so letters are distributed uniformly.

**One insight:** DynamoDB has no query planner. Unlike SQL databases that optimize any query at runtime, DynamoDB requires you to design all query paths at schema design time. There is no "add an index later" option without cost - GSIs consume write capacity on every item write.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Partition key determines physical placement**: all items with the same partition key (PK) are co-located on the same physical partition (up to 10 GB of data per partition key value).
2. **Each physical partition has a fixed throughput ceiling**: 3 000 Read Capacity Units (RCUs) and 1 000 Write Capacity Units (WCUs) per second. Hot partitions cannot be scaled independently - they must be redesigned.
3. **Sort keys enable range queries within a partition**: `query(PK="user:123", SK begins_with "ORDER#")` retrieves all orders for a user in one efficient request. Without a sort key, each item requires a separate `GetItem` call.
4. **GSIs consume write capacity**: every item write is replicated to all GSIs. A table with 5 GSIs performs 6 writes per item write (1 base + 5 GSIs). This adds cost and latency.
5. **DynamoDB scans are O(n)**: a table scan reads every item - equivalent to a SQL full table scan. It is expensive and must be avoided in production read paths.

**DERIVED DESIGN:**

- Choose partition keys with high cardinality (many unique values) and uniform access distribution.
- Use composite primary keys (PK + SK) to support hierarchical queries (parent → child) within one partition.
- Pre-define all access patterns before table design - each unsupported access pattern requires a GSI or denormalization.
- Use sparse GSIs: define a GSI on an attribute that only some items have - only those items appear in the GSI, making it small and efficient.

**THE TRADE-OFFS:**

**Gain:** Millisecond latency at any scale; predictable performance because all queries are key-based; horizontal scalability with automatic partition splitting; no operational maintenance of indexes (AWS manages GSI backfill automatically).

**Cost:** Schema must encode all access patterns upfront; changing access patterns after launch requires expensive table migrations; multi-item ACID transactions are limited to 100 items and cost 2× the write capacity; no ad-hoc queries or aggregations - DynamoDB is an OLTP store, not an analytics engine.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce application needs to: (1) get a user's profile by ID, (2) get all orders for a user sorted by date, (3) get all pending orders across all users for fulfillment, (4) get all items in an order.

**WHAT HAPPENS WITH NAIVE DESIGN (one table per entity):**
- `users` table: PK = `userId`. Access pattern 1: works.
- `orders` table: PK = `orderId`. Access pattern 2: FAILS - `orderId` partition key means you cannot query all orders for a user without a scan.
- Access pattern 3: GSI was never planned - requires a full scan of orders.
- `orderItems` table: PK = `orderId`. Access pattern 4: works.
Three tables, one impossible access pattern, one requiring a scan. One `$lookup`-equivalent is needed.

**WHAT HAPPENS WITH ACCESS-PATTERN-FIRST DESIGN:**
Single table (or two) with these primary keys:
- User profile: PK = `USER#<userId>`, SK = `PROFILE`
- User's orders: PK = `USER#<userId>`, SK = `ORDER#<date>#<orderId>`
- Order items: PK = `ORDER#<orderId>`, SK = `ITEM#<itemId>`
- GSI1: PK = `status` (for pending orders), SK = `createdAt`

Access pattern 1: `GetItem(PK=USER#123, SK=PROFILE)` ✓
Access pattern 2: `Query(PK=USER#123, SK begins_with ORDER#)` ✓
Access pattern 3: `GSI1 Query(PK=pending)` ✓ (sparse: only pending orders have `status = pending`)
Access pattern 4: `Query(PK=ORDER#456, SK begins_with ITEM#)` ✓

**THE INSIGHT:** The access pattern list is the schema. Every query must be writable as a `GetItem` or `Query` operation - never a `Scan`. If you cannot express a query as a key operation, you need a GSI or you need to denormalize.

---

### 🧠 Mental Model / Analogy

> DynamoDB data modeling is like designing a filing cabinet for a very specific office. You know in advance every type of document anyone will ever need to retrieve. You design the folder labels and drawer organization specifically for those retrieval needs. A relational database is like a library with a professional librarian who can find anything by any criteria - but costs more and takes longer. DynamoDB is like a perfectly labeled filing cabinet - instant retrieval for known patterns, but useless for retrieval patterns you didn't plan for.

- **Filing cabinet drawers** = DynamoDB partitions (keyed by partition key)
- **Tabs within a drawer** = sort key values within a partition
- **Extra copies filed under different labels** = GSIs (denormalized copies under alternate key)
- **Office reorganization** = table migration (expensive, disruptive)

Where this analogy breaks down: a filing cabinet is limited by physical space; DynamoDB partitions automatically split when data grows beyond 10 GB, distributing items across new partitions - but the partition key design cannot be changed after splitting, so a bad key design is permanent until a table rebuild.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
DynamoDB data modeling means planning how you label and organize your data before storing it, based on how your application needs to find it. Unlike SQL where you can always add a new search criteria later, in DynamoDB you need to plan upfront.

**Level 2 - How to use it (junior developer):**
List every query your application needs. For each query: (1) identify the "main entity" being queried → make it part of the partition key. (2) Identify the "filter or sort" → make it the sort key with a well-chosen prefix. (3) If a query needs a different "main entity" than the table's partition key → create a GSI. Test each access pattern before going to production.

**Level 3 - How it works (mid-level engineer):**
DynamoDB's internal architecture routes each request to a partition via consistent hashing of the partition key. Each partition is backed by 3 replicas across AZs (one leader, two followers). The partition key determines which replicas serve the request - hot partition key means all requests go to the same three machines. GSIs are asynchronously replicated tables - writes to the base table propagate to GSI replicas; reads from GSIs go to dedicated GSI replicas (not the base table replicas). LSIs share the same partition as the base table - they support sort-key range queries with different attributes but are limited to the base table's partition capacity (10 GB maximum per partition key).

**Level 4 - Why it was designed this way (senior/staff):**
DynamoDB was designed at Amazon to serve the Dynamo paper's core principle: infinite scalability at the cost of query flexibility. The design deliberately trades SQL's general query capability for predictable sub-10ms latency at any scale. The partition key is not just a lookup mechanism - it is the sharding key that determines horizontal distribution. DynamoDB's throughput guarantees are per-partition, not per-table, because the underlying hardware is partitioned: adding more capacity means adding more partitions, not bigger machines (there are no machines - it is a serverless distributed system at AWS's scale). The GSI's asynchronous replication means GSI reads can be slightly stale (typically milliseconds) - this is the eventual consistency trade-off inherent in a system designed for partition tolerance and availability over strict consistency.

---

### ⚙️ How It Works (Mechanism)

**Access Pattern → Schema Mapping:**

```
Access Pattern         PK Design         SK Design
─────────────────────────────────────────────────────
Get user by ID         USER#<userId>      PROFILE
Get orders by user     USER#<userId>      ORDER#<date>
Get items by order     ORDER#<orderId>    ITEM#<itemId>
Get product by ID      PRODUCT#<prodId>  METADATA
Get pending orders     GSI1: status       createdAt

Write Sharding (hot partition fix):
─────────────────────────────────────────────────────
Original PK: CELEBRITY_POSTS    ← hot partition
Sharded PK: CELEBRITY_POSTS#3  ← 1 of N shards
  (N = 10, random 0-9 appended)
Read: query all N shards, merge results
```

**GSI vs LSI Comparison:**

```
Local Secondary Index (LSI):
  - Same PK as base table, different SK
  - Max 10 GB per partition key
  - Strongly consistent reads available
  - Cannot add after table creation

Global Secondary Index (GSI):
  - Different PK (and optional SK)
  - Unlimited size
  - Eventually consistent by default
  - Can add after table creation
  - Consumes separate WCU provisioning
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
List all access patterns
          │
          ▼
Design primary key (PK + SK)
  to serve highest-traffic patterns
          │
          ▼
Design GSIs for remaining patterns
  Check: GSI cardinality + write cost
          │
          ▼
Write item → base table             ← YOU ARE HERE
  → async replication to all GSIs
          │
          ▼
Read: Query(PK, SK condition)
  → consistent sub-10ms read
          │ or
Read: GSI Query(GSI_PK, GSI_SK)
  → eventually consistent
```

**FAILURE PATH:**
- Hot partition: one PK receives > 1 000 WCU/s → `ProvisionedThroughputExceededException` → requests throttled
- Missing GSI: application needs `Query(status=pending)` → no GSI → `Scan` → O(n) cost
- LSI limit: partition key grows > 10 GB → `ItemCollectionSizeLimitExceededException` → writes rejected
- GSI write amplification: 5 GSIs × 1 000 writes/s = 5 000 GSI WCUs/s in addition to 1 000 base WCUs

**WHAT CHANGES AT SCALE:**
- Adaptive capacity (DynamoDB standard): DynamoDB automatically reallocates partition capacity to hot partitions - up to 3× burst. This does not fix structural hot partition design, only absorbs temporary spikes.
- On-demand capacity mode: no pre-provisioned WCU/RCU - AWS scales automatically; cost per-request; good for unpredictable workloads; can be 5× more expensive at sustained high throughput than provisioned mode.

---

### 💻 Code Example

**BAD - naive design, impossible queries, hot partition risk:**
```python
# Table: orders
# PK: orderId (bad - can't query by userId)
# No SK - every access is a GetItem by orderId only

# Writing
table.put_item(Item={
    'orderId': 'ORD-001',
    'userId': 'user-123',
    'status': 'pending',
    'total': 99.99
})

# "Get all orders for user-123" - IMPOSSIBLE without scan
response = table.scan(  # full table scan - never do this
    FilterExpression=Attr('userId').eq('user-123')
)
```

**GOOD - composite keys, GSI for alternate access pattern:**
```python
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('orders')

# Write: composite PK supports both entity and user queries
table.put_item(Item={
    'PK': 'ORDER#ORD-001',           # base table PK
    'SK': 'METADATA',                # base table SK
    'GSI1PK': 'USER#user-123',       # GSI1 partition key
    'GSI1SK': '2024-01-15T10:30:00', # GSI1 sort key
    'GSI2PK': 'STATUS#pending',      # GSI2 for fulfillment
    'GSI2SK': '2024-01-15T10:30:00',
    'total': 99.99,
    'userId': 'user-123',
    'status': 'pending'
})

# Access pattern 1: get order by ID
response = table.get_item(Key={
    'PK': 'ORDER#ORD-001',
    'SK': 'METADATA'
})

# Access pattern 2: get all orders for user, newest first
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression=(
        Key('GSI1PK').eq('USER#user-123') &
        Key('GSI1SK').begins_with('2024')
    ),
    ScanIndexForward=False  # descending sort
)

# Access pattern 3: get all pending orders (sparse GSI2)
# Only pending orders have GSI2PK set → sparse index
response = table.query(
    IndexName='GSI2',
    KeyConditionExpression=Key('GSI2PK').eq('STATUS#pending'),
    ScanIndexForward=True
)
```

**Write sharding for hot partition keys:**
```python
import random

SHARD_COUNT = 10

def write_with_sharding(celebrity_id: str, post: dict):
    shard = random.randint(0, SHARD_COUNT - 1)
    table.put_item(Item={
        'PK': f'CELEBRITY#{celebrity_id}#{shard}',
        'SK': f'POST#{post["timestamp"]}',
        **post
    })

def read_all_posts(celebrity_id: str):
    # Must query all shards and merge
    all_posts = []
    for shard in range(SHARD_COUNT):
        response = table.query(
            KeyConditionExpression=(
                Key('PK').eq(
                    f'CELEBRITY#{celebrity_id}#{shard}'
                )
            )
        )
        all_posts.extend(response['Items'])
    return sorted(all_posts, key=lambda x: x['SK'],
                  reverse=True)
```

---

### ⚖️ Comparison Table

| Pattern | Use Case | Trade-off | Example |
|---|---|---|---|
| Composite PK+SK | Hierarchical queries | Sort key must be designed carefully | User → Orders |
| GSI | Alternate query dimension | Async replication, additional WCU cost | Status → Orders |
| LSI | Same partition, different sort | 10 GB limit per PK | Order items by price |
| Write sharding | Hot partition key relief | Scatter-gather reads (query all shards) | Celebrity posts |
| Sparse GSI | Query items with a specific attribute | Only matching items in GSI | Active users GSI |
| Time-series table | High-volume append-only | Table per period, no backfill needed | IoT sensor readings |
| Adjacency list | Graph relationships | Complex query patterns | Friend relationships |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "DynamoDB auto-scales hot partitions" | Adaptive capacity absorbs temporary spikes (up to 3× burst), but a structurally hot partition key (low cardinality or celebrity problem) cannot be auto-scaled - it must be redesigned |
| "You can always add a GSI later" | GSIs can be added at any time, but they consume WCUs on every existing item during backfill and ongoing writes - adding GSIs after launch increases operational cost |
| "LSI and GSI are interchangeable" | LSI shares the base table partition → co-location, strong consistency, but 10 GB limit; GSI is independent → no size limit, but eventual consistency and separate throughput |
| "On-demand capacity mode eliminates hot partition problems" | On-demand mode does not change the underlying partition architecture - a hot partition still has a ceiling, managed by DynamoDB's internal adaptive capacity, which has limits |
| "DynamoDB supports any query with enough GSIs" | Some queries are structurally impossible regardless of GSI count (e.g., range queries across all users on a non-primary key without a very carefully designed GSI or table design) |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Hot Partition Throttling**

**Symptom:** `ProvisionedThroughputExceededException` on writes for specific items; CloudWatch `SystemErrors` or `ThrottledRequests` metrics spike; only some users/items experience errors.

**Root Cause:** A partition key value receives disproportionate write traffic - either a high-traffic entity (celebrity user, popular product) or a low-cardinality key (e.g., date-based PK with all writes going to today's value).

**Diagnostic:**
```bash
# Check throttled requests per table
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ThrottledRequests \
  --dimensions Name=TableName,Value=orders \
    Name=Operation,Value=PutItem \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 300 --statistics Sum

# Enable DynamoDB contributor insights to identify hot keys
aws dynamodb enable-kinesis-streaming-destination \
  --table-name orders \
  --stream-arn <contributor-insights-arn>
```
**Fix:** Implement write sharding (append random suffix to PK). For date-based keys, shard by `DATE#<yyyy-mm-dd>#<shard>` where shard is a random 0–N value.

**Prevention:** At design time, estimate maximum traffic per partition key value. If any key value could receive > 1 000 WCUs/second, implement sharding before launch.

---

**Failure Mode 2: ItemCollectionSizeLimitExceededException (LSI Overflow)**

**Symptom:** `ItemCollectionSizeLimitExceededException: Item collection too large for table orders`; writes to a specific partition key fail; the PK has accumulated over 10 GB of items.

**Root Cause:** An LSI is defined on the table; a single partition key value's total item size across all items (base table + LSI projections) exceeds 10 GB.

**Diagnostic:**
```python
# Check partition key collection size
response = dynamodb_client.describe_table(TableName='orders')
# Manually calculate: query all items for the hot PK
# and sum their sizes (there's no direct API for this)

# Or: enable CloudWatch metric on ItemCollectionSize
```
**Fix:** Remove the LSI (requires table migration) and replace with a GSI (no size limit). Alternatively, redesign the partition key to reduce item count per PK value.

**Prevention:** If a single partition key value may accumulate > 10 GB of items, do not use LSIs on that table. Use GSIs instead.

---

**Failure Mode 3: GSI Consuming Unexpected WCU**

**Symptom:** DynamoDB WCU consumption is 3–5× higher than expected; cost spikes after adding new GSIs; write performance degrades.

**Root Cause:** Multiple GSIs project large item attributes; each GSI write replicates the projected attributes. A table with 5 GSIs projecting `ALL` attributes effectively performs 6× the write work per item.

**Diagnostic:**
```bash
# Check WCU consumption per GSI
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedWriteCapacityUnits \
  --dimensions \
    Name=TableName,Value=orders \
    Name=GlobalSecondaryIndexName,Value=GSI1
  --period 3600 --statistics Sum

# Check GSI projection type in table description
aws dynamodb describe-table --table-name orders \
  | jq '.Table.GlobalSecondaryIndexes[] |
    {IndexName, Projection}'
```
**Fix:** Change GSI projection from `ALL` to `INCLUDE` with only the attributes needed for the GSI query. Drop unused GSIs that have zero read activity.

**Prevention:** When designing GSIs, project only the attributes actually needed by the GSI's read access pattern. Each additional projected attribute adds to the write cost.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DynamoDB - the underlying service; partition model, RCU/WCU capacity units, and primary key concepts
- NoSQL - the design philosophy that prioritizes access pattern design over normalization
- Distributed Systems - consistent hashing, partition replication, and eventual consistency that underpin DynamoDB's architecture

**Builds On This (learn these next):**
- DynamoDB Single-Table Design - the advanced technique of co-locating multiple entity types in one table using these patterns
- AWS - IAM permissions, VPC endpoints, DynamoDB Streams, and CloudWatch integration for production operations

**Alternatives / Comparisons:**
- DynamoDB Single-Table Design - the opinionated extension of these patterns using overloaded keys
- MongoDB Document Schema Design - equivalent access-pattern-first design discipline for MongoDB
- Key-Value Store - the abstract data model that DynamoDB's primary key access pattern implements

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    Design techniques for DynamoDB    │
│               tables, keys, and indexes         │
│ PROBLEM       SQL schema habits → hot partitions│
│               + impossible queries at scale     │
│ KEY INSIGHT   List access patterns first;       │
│               design schema to serve each one   │
│ USE WHEN      Every DynamoDB table design;      │
│               before adding a GSI or LSI        │
│ AVOID WHEN    Application needs ad-hoc queries  │
│               or analytics → use Redshift/Athena│
│ TRADE-OFF     Sub-10ms at unlimited scale vs    │
│               rigid pre-planned access patterns │
│ ONE-LINER     No scan, no problem; hot partition│
│               = wrong PK; GSI = new query       │
│ NEXT EXPLORE  DynamoDB Single-Table Design      │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** DynamoDB Adaptive Capacity automatically increases the throughput allocated to a hot partition. A developer relies on this to handle a viral product launch instead of implementing write sharding. Explain the exact physical mechanism by which Adaptive Capacity works, why it cannot solve a sustained hot partition problem (as opposed to a temporary burst), and at what point Adaptive Capacity stops helping.

2. **(C - Design Trade-off)** You need to query orders by `status` (pending, shipped, delivered) and by `createdAt` range. The `status` field has only 3 values (low cardinality). A GSI with `PK=status` would create only 3 partitions. Describe the hot partition risk, two alternative GSI designs that mitigate it, and the query complexity trade-off of each alternative.

3. **(A - System Interaction)** A DynamoDB table has a GSI that projects `ALL` attributes. A background job performs 1 000 PutItem operations per second. An engineer notices that the consumed WCU rate is 4 500/second against a provisioned rate of 5 000/second - much higher than the 1 000 item writes suggest. Walk through the exact calculation of why this WCU consumption is correct, including the GSI write multiplier and item size effects.
