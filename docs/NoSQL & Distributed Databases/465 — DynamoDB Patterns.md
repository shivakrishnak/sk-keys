---
layout: default
title: "DynamoDB Patterns"
parent: "NoSQL & Distributed Databases"
nav_order: 465
permalink: /nosql/dynamodb-patterns/
number: "0465"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Key-Value Store, Document Store, CAP Theorem (DB)
used_by: System Design, Polyglot Persistence, Cloud — AWS
related: Key-Value Store, Hot Partition Problem, NoSQL Patterns
tags:
  - nosql
  - dynamodb
  - aws
  - patterns
  - deep-dive
---

# 465 — DynamoDB Patterns

⚡ TL;DR — DynamoDB's single-table design — putting all entity types in one table using partition key + sort key + GSI combinations — eliminates cross-table JOINs, achieves O(1) reads per access pattern, and enables the full power of DynamoDB's horizontal scale, at the cost of complex, query-driven schema design.

| #465            | Category: NoSQL & Distributed Databases                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Key-Value Store, Document Store, CAP Theorem (DB)      |                 |
| **Used by:**    | System Design, Polyglot Persistence, Cloud — AWS       |                 |
| **Related:**    | Key-Value Store, Hot Partition Problem, NoSQL Patterns |                 |

---

### 🔥 The Problem This Solves

**NAIVE DYNAMODB = EXPENSIVE + SLOW:**
Teams coming from relational databases create a separate DynamoDB table for each entity type (UserTable, OrderTable, ProductTable), then simulate JOINs in application code by making multiple API calls. Result: N+1 patterns, high latency (multiple round trips for one page load), expensive (read capacity units consumed for each table scan), hard to maintain (N tables to manage and provision).

**SINGLE-TABLE DESIGN:**
Store all entities in one table using carefully designed partition key + sort key combinations. An `ORDER#order1` sort key under `USER#user1` partition key stores the order belonging to the user. A GSI with the order_id as partition key enables direct order lookup. One query → one table → one round trip → all related entities. This is the "DynamoDB way" — and understanding it unlocks predictable O(1) performance at any scale.

---

### 📘 Textbook Definition

**DynamoDB** is AWS's fully managed key-value and document database with single-digit millisecond performance at any scale. Core data model: every item has a **Partition Key (PK)** and an optional **Sort Key (SK)**; the PK determines the partition, the SK enables range queries within a partition. **Single-table design**: multiple entity types share one table, distinguished by PK/SK patterns (e.g., `USER#user1` as PK, `PROFILE` as SK for user profile; `USER#user1` as PK, `ORDER#order1` as SK for order ownership). **GSI (Global Secondary Index)**: alternate access pattern using different PK/SK attributes; eventually consistent by default; up to 20 GSIs per table. **LSI (Local Secondary Index)**: same partition key as base table, different sort key; strongly consistent but must be defined at table creation. **Transactions**: `TransactWriteItems` / `TransactGetItems` for multi-item ACID across up to 100 items in one account/region. **TTL**: automatic item expiration by epoch timestamp attribute — no RCU/WCU consumed. **DynamoDB Streams**: ordered log of item-level changes (new image, old image, or both); triggers Lambda functions for event-driven processing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DynamoDB single-table design means one table holds all your entities, encoded with clever PK/SK patterns so that every access pattern is answered by a single, bounded query — no JOINs, no multiple round trips.

**One analogy:**

> A filing cabinet where all company documents (invoices, contracts, employee records, projects) go into ONE drawer, organized by a two-part label system. The first label (partition key) is the "folder" (EMPLOYEE#emp1 for everything about employee 1). The second label (sort key) is the document type (PROFILE, ROLE, PROJECT#proj1, INVOICE#inv1). Need all documents for employee 1? Pull the EMPLOYEE#emp1 folder (one query). Need all PROJECT#proj1 documents regardless of employee? Use the special index (GSI) organized by the second label.

- "One drawer for all documents" → single DynamoDB table
- "Folder label" → partition key (EMPLOYEE#emp1)
- "Document type label" → sort key (PROFILE, PROJECT#proj1)
- "Pull one folder" → `pk = "EMPLOYEE#emp1"` query (single partition)
- "Special index" → GSI (different access pattern, different PK)

**One insight:**
The DynamoDB data model forces you to think about **access patterns before data structures** — more aggressively than even Cassandra. The schema IS the compiled output of your access pattern analysis. If you discover a new access pattern after launch, you need to add a GSI or restructure data — there's no equivalent of "add an index to an existing SQL table and the query optimizer uses it."

---

### 🔩 First Principles Explanation

**SINGLE-TABLE DESIGN — ENTITY TYPES AND KEY PATTERNS:**

```javascript
// E-commerce: Users, Orders, Products, OrderItems in ONE table
// Table name: ecommerce

// Entity: User profile
{ PK: "USER#user-001", SK: "PROFILE",        name: "Alice", email: "alice@example.com" }

// Entity: User's addresses
{ PK: "USER#user-001", SK: "ADDRESS#addr-1", street: "123 Main St", city: "NYC" }

// Entity: Order (owned by user)
{ PK: "USER#user-001", SK: "ORDER#order-555", total: 99.99, status: "SHIPPED",
  GSI1_PK: "ORDER#order-555", GSI1_SK: "ORDER"  }   // GSI for direct order lookup

// Entity: Order item (within an order)
{ PK: "ORDER#order-555", SK: "ITEM#prod-42",  quantity: 2, price: 49.99 }

// Entity: Product catalog
{ PK: "PRODUCT#prod-42", SK: "DETAILS",       name: "Laptop Stand", category: "Tech" }

// Access pattern 1: Get user profile + all orders for user
//   QUERY: PK = "USER#user-001", SK BEGINS_WITH "ORDER#"
//   Returns: all ORDER# items for this user → single partition scan

// Access pattern 2: Get a specific order + all its items
//   QUERY: PK = "ORDER#order-555", SK >= "ITEM#"
//   Returns: all ITEM# items for this order → single partition scan

// Access pattern 3: Get order by order ID (not user ID)
//   GSI QUERY: GSI1_PK = "ORDER#order-555"
//   Returns: the order item → single GSI lookup

// Access pattern 4: Get user profile
//   GET_ITEM: PK = "USER#user-001", SK = "PROFILE"  → O(1)
```

**GSI (GLOBAL SECONDARY INDEX):**

```javascript
// GSI overloading: one GSI serves multiple access patterns
// by using different attribute names as GSI PK/SK per entity type

// GSI1_PK / GSI1_SK attributes on every item (null = not in GSI)

// Sellers: all products by seller
{ PK: "PRODUCT#prod-42", SK: "DETAILS",
  GSI1_PK: "SELLER#seller-99",     // GSI PK = seller
  GSI1_SK: "PRODUCT#prod-42" }     // GSI SK = product ID
// Access: GSI QUERY: GSI1_PK = "SELLER#seller-99" → all products by this seller

// Orders by status (sparse index): only in-progress orders in GSI
{ PK: "USER#user-001", SK: "ORDER#order-555",
  GSI1_PK: "STATUS#IN_PROGRESS",   // only set for in-progress orders
  GSI1_SK: "ORDER#order-555" }
// Completed orders: GSI1_PK not set → not in the GSI (sparse index)
// Access: GSI QUERY: GSI1_PK = "STATUS#IN_PROGRESS" → all in-progress orders
// Efficient: only active orders in GSI (sparse), not all orders ever
```

**TRANSACTIONS (ACID across multiple items):**

```javascript
// Problem: create order + decrement inventory + charge user atomically
// DynamoDB TransactWriteItems: up to 100 items, atomic

await dynamoClient.transactWrite({
  TransactItems: [
    {
      // 1. Insert order (only if it doesn't exist — idempotency)
      Put: {
        TableName: "ecommerce",
        Item: { PK: "USER#user-001", SK: "ORDER#order-555", total: 99.99 },
        ConditionExpression: "attribute_not_exists(PK)", // idempotent
      },
    },
    {
      // 2. Decrement inventory (only if stock >= quantity)
      Update: {
        TableName: "ecommerce",
        Key: { PK: "PRODUCT#prod-42", SK: "INVENTORY" },
        UpdateExpression: "SET stock = stock - :qty",
        ConditionExpression: "stock >= :qty", // guard condition
        ExpressionAttributeValues: { ":qty": 2 },
      },
    },
    {
      // 3. Deduct from user's credit balance
      Update: {
        TableName: "ecommerce",
        Key: { PK: "USER#user-001", SK: "BALANCE" },
        UpdateExpression: "SET balance = balance - :total",
        ConditionExpression: "balance >= :total", // guard condition
        ExpressionAttributeValues: { ":total": 99.99 },
      },
    },
  ],
});
// If any condition fails: entire transaction rolled back
// Cost: 2× WCU for transactional writes (vs. non-transactional)
```

**TTL (TIME-TO-LIVE):**

```javascript
// Automatic item expiration — no WCU consumed for deletes
// Sessions with 24-hour expiry:
const expiresAt = Math.floor(Date.now() / 1000) + 24 * 60 * 60; // epoch seconds

await dynamoClient.put({
  TableName: "sessions",
  Item: {
    PK: "SESSION#session-token",
    SK: "SESSION",
    userId: "user-001",
    ttl: expiresAt, // TTL attribute (must be number type, epoch seconds)
  },
});

// Enable TTL on the table (one-time setup):
// aws dynamodb update-time-to-live --table-name sessions
//   --time-to-live-specification "Enabled=true,AttributeName=ttl"

// DynamoDB: lazily deletes items after TTL (within 48 hours, usually faster)
// Items are "expired" and not returned in reads once past TTL
// But may not be physically deleted immediately → filter in reads if needed:
FilterExpression: "attribute_not_exists(#ttl) OR #ttl > :now";
```

**DYNAMODB STREAMS + LAMBDA (EVENT-DRIVEN):**

```javascript
// DynamoDB Streams: ordered log of item changes
// Lambda trigger: runs for every batch of stream records

exports.handler = async (event) => {
  for (const record of event.Records) {
    const { eventName, dynamodb } = record; // INSERT, MODIFY, REMOVE

    if (eventName === "INSERT") {
      const newItem = AWS.DynamoDB.Converter.unmarshall(dynamodb.NewImage);
      if (newItem.PK.startsWith("ORDER#")) {
        // New order created: send confirmation email, update analytics
        await sendOrderConfirmationEmail(newItem);
        await updateAnalyticsDashboard(newItem);
      }
    }

    if (eventName === "MODIFY") {
      const oldItem = AWS.DynamoDB.Converter.unmarshall(dynamodb.OldImage);
      const newItem = AWS.DynamoDB.Converter.unmarshall(dynamodb.NewImage);
      if (oldItem.status !== "SHIPPED" && newItem.status === "SHIPPED") {
        await sendShipmentNotification(newItem);
      }
    }
  }
};
// Streams: 24-hour retention, at-least-once delivery
// Use for: cache invalidation, CDC to Elasticsearch, async projections
```

---

### 🧪 Thought Experiment

**THE "JUST ADD A GSI" TRAP**

A developer is building a multi-tenant SaaS: each tenant has users, projects, and tasks. The initial single-table design works great for: "get all projects for tenant X" and "get all tasks for project Y". Six months later, new requirements arrive:

**New Q1:** "Get all tasks assigned to a specific user across all projects" — no GSI for this yet.

**New Q2:** "Get all high-priority tasks across all tenants for admin dashboard" — requires scanning all items with `priority = 'HIGH'`.

**New Q3:** "Get all tasks created in the last 24 hours, any tenant" — time-based cross-tenant query.

The developer's instinct: "just add a GSI for each." But:

- DynamoDB allows max 20 GSIs per table
- Each GSI is replicated storage (costs ~1× the table storage)
- 20 GSIs × table size = 21× total storage
- Q2 and Q3 require cross-partition queries — GSI helps, but any query requiring `Scan` on the GSI is O(N)
- Q3's "last 24 hours" is a time-based range across all partitions — fundamentally incompatible with DynamoDB's per-partition model

**Resolution:**

- Q1: Add a GSI with `assigned_to_user_id` as GSI PK, `createdAt` as GSI SK — efficient
- Q2: Build an aggregation pipeline (Streams → Lambda → OpenSearch/Elasticsearch) for admin queries
- Q3: DynamoDB is the wrong tool for cross-tenant time-range queries — export to S3 via DynamoDB Streams + Kinesis, query via Athena

**The lesson:** DynamoDB + single-table design excels at entity-relationship queries (get all X for this Y). It struggles with analytical, cross-entity, or global filter queries. Design the DynamoDB schema for operational queries; delegate analytical queries to a purpose-built analytics system.

---

### 🧠 Mental Model / Analogy

> DynamoDB single-table design is like a well-indexed library where every book combination a reader might request is already pre-shelved together. Need "all books by Author A in Genre B"? They're already in that section (partition). Need "all fantasy books regardless of author"? There's a dedicated genre index (GSI) where they're filed by genre. The library doesn't let you look up books by arbitrary criteria (no full-text search, no SQL-like ad-hoc queries) — but for the pre-defined request types, you can always find what you need in one place, instantly, at any library size.

- "Books pre-shelved by author+genre" → single-table items with PK/SK encoding relationships
- "Genre index" → GSI (different access pattern index)
- "One section for author A" → one partition (all items under PK = author_id)
- "No arbitrary criteria lookups" → no ad-hoc queries; access patterns defined at design time
- "Any library size" → DynamoDB's horizontal scale (unlimited capacity)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** DynamoDB stores items with a partition key (PK) and optional sort key (SK). Related items get the same PK. The SK distinguishes item types within a partition. A "query" returns all items with a given PK (or PK + SK range). GSIs provide additional access patterns. Use TTL for automatic expiration. Use DynamoDB Streams to trigger Lambda on changes.

**Level 2:** Design access patterns first: list every query the application needs. For each query: define which PK+SK combination answers it. Use SK "begins_with" for type-scoped queries (PK="USER#1", SK begins_with "ORDER#"). Add GSIs for alternative access patterns. Use sparse indexes (only some items populate GSI attributes) to limit GSI size. Handle pagination: DynamoDB returns max 1MB per query; use `LastEvaluatedKey` for pagination.

**Level 3:** Write capacity planning: choose between Provisioned (predictable traffic, cheaper, auto-scaling available) and On-Demand (unpredictable spikes, 5× more expensive, no planning needed). TransactWriteItems: 2× WCU cost; max 100 items; use for critical consistency. Avoid "hot partitions": PK should have high cardinality; never use low-cardinality values like "status" as PK. Adaptive capacity (DynamoDB feature): automatically shifts capacity to hot partitions — but this is reactive; still avoid hot partitions by design. Conditional writes for optimistic locking: `ConditionExpression: "version = :expected_version"` + `UpdateExpression: "SET version = version + 1"` — CAS operation for concurrent updates without locks.

**Level 4:** DynamoDB's single-table design is the most polarizing pattern in NoSQL. Proponents (Rick Houlihan, AWS): single-table is the only correct way to use DynamoDB for complex domain models; it eliminates the N+1 pattern, enables co-location of related entities, and achieves consistent < 10ms latency. Critics: single-table design is an opaque schema that requires deep domain knowledge to query; it makes observability and debugging harder (generic PK/SK attributes instead of semantic names); it's over-engineered for simple use cases. The compromise position: single-table design is optimal for well-defined, stable access patterns in high-scale production applications; multi-table is acceptable for lower-scale, simpler, or rapidly-evolving schemas where operational clarity matters. The schema IS the compiled query plan — it requires the same discipline as query plan caching in databases.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ DYNAMODB SINGLE-TABLE QUERY EXECUTION                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ QUERY: Get all orders for user-001                   │
│ params: { PK: "USER#user-001", SK begins_with: "ORDER#" }│
│                                                      │
│ 1. Hash PK="USER#user-001" → partition ID            │
│ 2. Route to 3 storage nodes (replication factor=3)   │
│ 3. Read from 1 node (Eventually Consistent, default) │
│    or 2 nodes (Strongly Consistent, 2× RCU cost)     │
│                                                      │
│ [DYNAMODB PATTERNS ← YOU ARE HERE]                   │
│                                                      │
│ 4. B-tree range scan: SK ∈ ["ORDER#", "ORDER#~"]     │
│    (~ sorts after all printable chars → gets all     │
│    ORDER# prefixed items)                            │
│ 5. Return items (up to 1MB); if more: LastEvaluatedKey│
│ 6. Application paginates if needed                   │
│                                                      │
│ GSI query: Get order by order ID                     │
│ params: { GSI1_PK: "ORDER#order-555" }              │
│ → Routes to GSI partition (eventual consistency)     │
│ → Returns base table items with that GSI PK value    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NEW ORDER FLOW (TRANSACTION + STREAMS):**

```
User places order (order-555, user-001, product-42, qty=2):
→ [DYNAMODB PATTERNS ← YOU ARE HERE: transact write]
→ DynamoDB TransactWriteItems:
   1. PUT order item: {PK:"USER#user-001", SK:"ORDER#order-555", status:"PENDING"}
      Condition: item not exists (idempotent)
   2. UPDATE inventory: {PK:"PRODUCT#prod-42", SK:"INVENTORY"}
      stock = stock - 2; Condition: stock >= 2
   3. UPDATE balance: {PK:"USER#user-001", SK:"BALANCE"}
      balance = balance - 99.99; Condition: balance >= 99.99
→ All 3 conditions pass → Transaction committed (atomic)
→ DynamoDB Stream: 3 new INSERT/MODIFY records appear in stream

→ Lambda (stream consumer):
   Processes new ORDER INSERT
   → Send order confirmation email (async)
   → Update Elasticsearch order index (for admin search)
   → Emit OrderPlaced event to EventBridge (for other microservices)

→ Read user's orders page:
   QUERY: PK="USER#user-001", SK begins_with "ORDER#"
   → Returns all orders including order-555
   → Single query, single partition, < 5ms
```

---

### ⚖️ Comparison Table

| Feature           | DynamoDB                                | Cassandra                                 | MongoDB                    |
| ----------------- | --------------------------------------- | ----------------------------------------- | -------------------------- |
| Managed service   | Fully managed (AWS)                     | Self-managed or managed (Astra)           | Self-managed or Atlas      |
| Schema design     | Single-table, GSI for access patterns   | One table per query, CQL                  | Document, flexible schema  |
| Transactions      | ✅ (up to 100 items, 2× cost)           | LWT (expensive)                           | Multi-document (4.0+)      |
| Auto-scaling      | ✅ On-demand mode                       | ❌ Manual capacity planning               | ✅ Atlas auto-scaling      |
| Global tables     | ✅ Multi-region, active-active          | ✅ Multi-region, tunable                  | ✅ Atlas Global Clusters   |
| Secondary indexes | GSI (global) + LSI (local, at creation) | Secondary index (full cluster scan) + SAI | Compound index, text index |
| Cost model        | Per-request (RCU/WCU) + storage         | Server/node cost                          | Server/node cost           |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Multi-table DynamoDB is simpler so it's better" | Multi-table requires N+1 round trips for related entities. Single-table gets all related entities in one query. Complexity is upfront (schema design) not runtime                             |
| "GSIs are free to use"                           | Each GSI replicates the entire table (or the projected attributes). 5 GSIs ≈ 6× storage cost. GSI writes consume additional WCU on the table. Design GSIs carefully                           |
| "DynamoDB is only for simple key-value"          | DynamoDB supports complex schemas (nested attributes, lists, maps), ACID transactions, streaming, TTL, and full-featured query expressions. Single-table design handles complex domain models |
| "On-demand mode is always better"                | On-demand is 5-7× more expensive per request than provisioned with auto-scaling. For predictable workloads: provisioned + auto-scaling is significantly cheaper                               |

---

### 🚨 Failure Modes & Diagnosis

**1. ProvisionedThroughputExceededException on Hot Partition**

**Symptom:** Intermittent `ProvisionedThroughputExceededException` errors for specific items, even though total table capacity is not exceeded. Affects only requests to specific partition key values.

**Root Cause:** Partition-level throughput limit in DynamoDB: each partition can sustain up to 3,000 RCU or 1,000 WCU per second (independent of table-level limits). If all traffic concentrates on one PK value, the partition cap is hit.

**Diagnostic:**

```bash
# CloudWatch: DynamoDB > Table > Consumed Capacity (partition-level detail)
# Look for: ConsumedWriteCapacityUnits spikes on specific time periods
# DynamoDB contributor insights (enable in console):
# Shows top partition keys consuming most capacity
```

**Fix:** Redesign partition key to have higher cardinality. For write-heavy scenarios: use write sharding (append a random suffix 0-9 to the PK, then query all shards). For DynamoDB On-Demand: adaptive capacity handles some hot partition scenarios automatically, but fundamental hot partition redesign is still needed above limits.

---

### 🔗 Related Keywords

**Prerequisites:** Key-Value Store, Document Store, CAP Theorem (DB)
**Builds On This:** System Design, Polyglot Persistence, Cloud — AWS
**Related:** Key-Value Store, Hot Partition Problem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DESIGN RULE │ One table for all entities (single-table)  │
│ PK/SK       │ "ENTITY#id" patterns for type scoping      │
│ GSI         │ Each new access pattern; max 20 GSIs       │
│ SPARSE IDX  │ Set GSI attrs only on qualifying items     │
│ TRANSACT    │ Up to 100 items, 2× WCU cost               │
│ TTL         │ epoch seconds attr; no cost; ±48hr delete  │
│ HOT PART    │ DynamoDB limit: 3K RCU / 1K WCU per part   │
│ STREAMS     │ CDC via Lambda triggers (24hr retention)   │
│ ONE-LINER   │ "Every access pattern = one table scan;   │
│             │  design the schema as the query plan"      │
│ NEXT EXPLORE│ Hot Partition Problem → Wide Col vs Doc    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a DynamoDB single-table schema for a multi-tenant project management tool (like Jira): Tenants have multiple projects; projects have epics; epics have stories; stories have tasks and comments. Access patterns include: all stories for a project (sorted by priority), all tasks for a story, all comments for a story (newest first), a specific user's assigned tasks across all projects in their tenant. Define PK, SK, and GSI patterns for each entity and each access pattern.

**Q2.** (TYPE F — Comparison Depth) Compare DynamoDB On-Demand vs. Provisioned capacity + Auto-scaling for: (a) a new SaaS with unknown traffic and 100K users, (b) a mature e-commerce site with 10M users and predictable 10am–8pm peak traffic, (c) a batch processing job that runs nightly with high throughput for 2 hours then idles. Calculate approximate cost difference for case (b) at 1,000 WCU average demand.
