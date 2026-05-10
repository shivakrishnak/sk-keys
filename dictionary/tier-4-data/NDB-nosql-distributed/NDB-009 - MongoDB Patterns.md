---
version: 2
layout: default
title: "MongoDB Patterns"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /nosql/mongodb-patterns/
id: NDB-014
category: NoSQL & Distributed Databases
difficulty: ★★☆
depends_on: Document Store, Schema Evolution, ORM Patterns
used_by: Polyglot Persistence, System Design, Microservices
related: Document Store, Polyglot Persistence, ORM Patterns
tags:
  - nosql
  - mongodb
  - patterns
  - intermediate
---

# NDB-009 - MongoDB Patterns

⚡ TL;DR - MongoDB schema and access patterns - embed vs. reference, the bucket pattern for time-series, polymorphic schemas, outlier handling, and aggregation pipelines - are the design decisions that determine whether your MongoDB deployment runs at O(1) or degrades to O(N) at scale.

| #461            | Category: NoSQL & Distributed Databases            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Document Store, Schema Evolution, ORM Patterns     |                 |
| **Used by:**    | Polyglot Persistence, System Design, Microservices |                 |
| **Related:**    | Document Store, Polyglot Persistence, ORM Patterns |                 |

---

### 🔥 The Problem This Solves

**GENERIC MONGODB USAGE = POOR PERFORMANCE:**
Many teams use MongoDB as "JSON PostgreSQL" - normalize data into many small documents, use `$lookup` for joins everywhere, no schema design. Result: N+1 query patterns, collection scans, massive aggregation pipelines running on millions of documents, documents bloating with unbounded arrays. MongoDB is blamed for being "slow" when the issue is schema design that ignores MongoDB's data model strengths.

**MONGODB PATTERNS:**
Document schema design patterns solve specific, recurring problems: how to store time-series without unbounded arrays (bucket pattern), how to handle polymorphic entities (polymorphic pattern), how to avoid massive documents from popular data (outlier pattern). These patterns are prescriptions from MongoDB's own engineering team for their most common production performance problems.

---

### 📘 Textbook Definition

**MongoDB patterns** are a set of document schema and access design patterns that optimize MongoDB usage for specific use cases. Developed and documented by MongoDB's engineering team, these patterns address common schema design trade-offs: **Embedding vs. Referencing** (data locality vs. normalization), **Bucket Pattern** (time-series data in fixed-size document buckets), **Polymorphic Pattern** (documents with varying schemas in one collection), **Outlier Pattern** (handling document size outliers like celebrity users), **Computed Pattern** (pre-compute expensive aggregations), **Attribute Pattern** (flexible attributes without mapping explosion), **Schema Versioning Pattern** (evolve schemas incrementally), **Extended Reference Pattern** (embed frequently-read fields from a referenced document). Understanding these patterns is essential for building performant MongoDB systems beyond basic CRUD.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MongoDB patterns are schema recipes - each one solves a specific performance problem (unbounded arrays, heterogeneous data, hot documents) by structuring documents to match how MongoDB actually stores and retrieves data.

**One analogy:**

> Filing organization systems. The "everything in one drawer" approach works for 20 files; fails for 20,000. Specific systems (A-Z tabs, monthly folders, color coding by project) solve specific organization problems. MongoDB patterns are these organization systems - each one optimized for a specific data access pattern (time-series, polymorphic entities, high-volume social data).

- "Everything in one drawer" → naive document embedding (unbounded arrays)
- "A-Z tabs" → bucket pattern (fixed-size time buckets)
- "Monthly folders" → computed pattern (pre-aggregated summaries)
- "Color coding by project" → attribute pattern (flexible tagged fields)
- "Organization system chosen by usage" → schema designed for access pattern

**One insight:**
MongoDB schema design is the opposite of relational normalization. In relational: normalize first (eliminate redundancy), then let the query optimizer figure out access. In MongoDB: design for access patterns first (what queries must be fast?), then choose the schema that makes those queries efficient, accepting redundancy as the cost of performance.

---

### 🔩 First Principles Explanation

**BUCKET PATTERN (time-series):**

```javascript
// PROBLEM: store IoT sensor readings (1 reading/second)
// NAIVE: one document per reading
{ _id: ObjectId(), device: "sensor-42", ts: ISODate("2024-01-15T14:00:00"), temp: 25.1 }
{ _id: ObjectId(), device: "sensor-42", ts: ISODate("2024-01-15T14:00:01"), temp: 25.2 }
// 86,400 documents/day/device × 1000 devices = 86M documents/day
// Massive index, many small documents → poor performance

// BUCKET PATTERN: group N readings per document
{
  device: "sensor-42",
  date: ISODate("2024-01-15"),
  hour: 14,
  // 60 readings in this 1-minute bucket
  readings: [
    { offset: 0, temp: 25.1 },
    { offset: 1, temp: 25.2 },
    // ... up to 60 entries
  ],
  count: 60,
  min_temp: 24.8,
  max_temp: 25.4,
  sum_temp: 1506.0  // pre-aggregated for fast avg calculation
}

// Benefits:
// 1. 60x fewer documents → smaller index → faster range queries
// 2. Pre-aggregated min/max/sum in document → fast aggregations without $group
// 3. Bounded document size (max 60 readings per bucket = predictable)

// Query: average temp for device X in last 1 hour
db.sensor_data.aggregate([
  { $match: { device: "sensor-42", date: today, hour: {$gte: 13} } },
  { $group: { _id: null, avgTemp: { $avg: "$avg_temp" } } }  // use pre-computed avg
])
```

**OUTLIER PATTERN (high-volume documents):**

```javascript
// PROBLEM: "celebrity" problem
// Regular user: 500 followers → embed array in user document
// Celebrity user: 10 million followers → document size explosion

// SOLUTION: use the regular embedding for normal cases;
//           overflow to a separate collection for outliers

// user document
{
  _id: "user-celebrity",
  name: "BigStar",
  has_extras: true,  // signal: overflow documents exist
  followers: [ ... up to 1000 ... ]  // first 1000 embedded
}

// overflow documents (linked)
{ user_id: "user-celebrity", page: 1, followers: [ ... next 1000 ... ] }
{ user_id: "user-celebrity", page: 2, followers: [ ... next 1000 ... ] }

// Application:
function getFollowers(userId) {
  const user = db.users.findOne({_id: userId});
  const followers = [...user.followers];
  if (user.has_extras) {
    const extras = db.user_followers_extras.find({user_id: userId}).toArray();
    extras.forEach(doc => followers.push(...doc.followers));
  }
  return followers;
}
// Regular users: single document read
// Celebrities: multiple reads (but only for celebrities, not for all users)
```

**ATTRIBUTE PATTERN (flexible attributes):**

```javascript
// PROBLEM: product catalog with heterogeneous attributes
// NAIVE: sparse document with many null fields
{
  name: "Sony WH-1000XM5",
  cpu: null, ram: null, ssd: null,  // laptop fields (null for headphones)
  driver_mm: 30, impedance: 48,     // headphone fields
  // 40+ attributes, most null per product
}

// ATTRIBUTE PATTERN: normalize attributes into array
{
  name: "Sony WH-1000XM5",
  specs: [
    { k: "driver_mm",  v: 30,    u: "mm" },
    { k: "impedance",  v: 48,    u: "ohm" },
    { k: "wireless",   v: true   },
    { k: "anc",        v: true   }
  ]
}

// Index: compound on specs.k and specs.v
db.products.createIndex({ "specs.k": 1, "specs.v": 1 })
// Query: find headphones with ANC = true
db.products.find({ specs: { $elemMatch: { k: "anc", v: true } } })

// Benefits: no sparse nulls; indexable; new attributes need no schema change
```

**POLYMORPHIC PATTERN:**

```javascript
// PROBLEM: different subtypes with shared behavior
// One collection: "vehicles"
// Cars, trucks, and motorcycles share: make, model, year, price
// But have different type-specific fields

// POLYMORPHIC: store all types in one collection with a discriminator
{
  _id: ObjectId(),
  type: "car",       // discriminator
  make: "Toyota", model: "Camry", year: 2023, price: 28000,
  doors: 4, engine_cc: 2500     // car-specific
}
{
  _id: ObjectId(),
  type: "motorcycle",
  make: "Honda", model: "CBR600", year: 2023, price: 11000,
  engine_cc: 600, abs: true     // motorcycle-specific
}

// Application: route to appropriate handler by type
// Query all vehicles: one collection, one query
// Query cars only: { type: "car" }
// Avoids JOIN (no separate car/motorcycle/truck collections to query + merge)
```

**COMPUTED PATTERN:**

```javascript
// PROBLEM: expensive aggregation runs on every request
// e.g., "total order value for a user's cart"

// NAIVE: calculate on every read
db.orders.aggregate([
  { $match: { user_id: userId, status: "cart" } },
  { $unwind: "$items" },
  { $group: { _id: null, total: { $sum: "$items.price" } } },
]);
// Runs on every cart view → expensive as cart grows

// COMPUTED PATTERN: maintain pre-computed field, update on write
// On add-to-cart:
db.carts.updateOne(
  { user_id: userId },
  {
    $push: { items: newItem },
    $inc: { total: newItem.price, item_count: 1 }, // maintain total
  },
);

// On read:
db.carts.findOne({ user_id: userId }, { total: 1, item_count: 1 });
// Instant: no aggregation needed

// Trade-off: write-time cost (updating total on every add/remove)
//            vs. read-time cost (aggregating on every view)
// For read-heavy carts: computed pattern wins
```

---

### 🧪 Thought Experiment

**THE $LOOKUP (JOIN) TRAP**

A developer coming from SQL models an e-commerce system in MongoDB as:

```
users collection: {_id, name, email, ...}
orders collection: {_id, userId, items: [...], total, ...}
products collection: {_id, name, price, ...}
```

To display an order detail page, they write:

```javascript
db.orders.aggregate([
  { $match: { _id: orderId } },
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user",
    },
  },
  { $unwind: "$user" },
  {
    $lookup: {
      from: "products",
      localField: "items.productId",
      foreignField: "_id",
      as: "products",
    },
  },
]);
```

This works for small data. At scale:

- `$lookup` in MongoDB is a correlated subquery, not a hash join
- Each document in orders must be joined with users (one additional query per doc)
- 10,000 orders in the result: 10,000 user lookups + 10,000 product lookups
- Under load: N+1 query pattern at the DB level → severe performance degradation

**FIX (Extended Reference Pattern):**
At order creation time, embed a snapshot of the user's display fields:

```javascript
{
  _id: orderId,
  user_id: "u42",
  user_snapshot: { name: "Alice", email: "alice@example.com" },  // snapshot at order time
  items: [
    {
      product_id: "p123",
      product_name: "Laptop",     // snapshot at order time
      product_price: 1299.99,     // snapshot at order time (historical price)
      quantity: 1
    }
  ],
  total: 1299.99
}
```

Order detail page: single document read. No `$lookup`. Product price and user name are historical snapshots (correct for the order receipt). Trade-off: if the user changes their name, past orders show the old name (which is actually correct for legal receipts). This is the extended reference pattern - denormalize what you read together.

---

### 🧠 Mental Model / Analogy

> MongoDB patterns are like kitchen organization strategies. "Keep everything in one drawer" (naive embedding with unbounded arrays) works for small kitchens; fails for large ones. "Junk drawer + organized drawers" (outlier pattern: embed for most, overflow for outliers) keeps things manageable. "Prep and store chopped vegetables" (computed pattern: pre-compute aggregations) saves time when cooking. "Label everything consistently" (attribute pattern: key-value specs array) lets you find any tool by its property. The right strategy depends on what you cook (your access patterns), not on kitchen aesthetics (normalization theory).

- "Prep and store" → computed pattern (pre-compute aggregations at write time)
- "Junk drawer + organized drawers" → outlier pattern (regular + overflow)
- "Label everything consistently" → attribute pattern (k-v specs)
- "What you cook" → access patterns (what queries must be fast)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** MongoDB schema design starts with: "what queries do I need to answer quickly?" Embed related data that you always read together. Keep arrays bounded in size. Pre-compute expensive aggregations rather than recalculating every read. These three rules prevent 90% of MongoDB performance problems.

**Level 2:** Apply specific patterns by problem: IoT/time-series → bucket pattern. Heterogeneous product attributes → attribute pattern. Celebrity/high-follower-count users → outlier pattern. Display name + email alongside order → extended reference (snapshot). Multiple vehicle/product types in one collection → polymorphic. Pre-compute totals, counts, ratings → computed pattern. Use Change Streams to trigger computed field updates asynchronously.

**Level 3:** MongoDB schema versioning: use a `schemaVersion` field in documents. Application reads `schemaVersion` and applies different parsing logic: version 1 parses one way, version 2 another. Background migration: query documents with old schema version → update to new version → mark as migrated. No big-bang migration. This is the equivalent of the database migration tool pattern but at application level (since MongoDB has no enforced schema). Atlas Schema Advisor (MongoDB Atlas): analyzes collection access patterns and recommends indexes and schema improvements. MongoDB Change Streams: subscribe to document changes (built on oplog) for event-driven patterns (trigger computed field updates on write, CDC to other systems).

**Level 4:** MongoDB patterns reveal a fundamental tension in document databases: the impedance mismatch isn't between objects and relations (as in ORM) - it's between access patterns and data structure. A document database is fast when the query's data access pattern matches the document structure: one query → one document (or a small, bounded number of documents). It degrades when queries require spanning many documents or computing aggregates over large result sets. The patterns are essentially formulas for pre-answering the question "what queries will be made?" and encoding the answers into the document structure itself. This is the "materialized query" principle: pre-materialize query results into the document for read-heavy access patterns; accept write-time overhead to avoid read-time computation. The optimal MongoDB schema for a given application is not static - it should evolve as access patterns evolve. The schema versioning pattern + Change Streams enables this evolution without downtime.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ BUCKET PATTERN: WRITE + QUERY                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│ New reading arrives: {device: "s42", ts: T, temp: 25}│
│ Calculate bucket: bucket_id = device + date + hour   │
│                                                      │
│ Upsert (atomic update with $push + $inc):            │
│ db.sensor_buckets.updateOne(                         │
│   { device: "s42", date: today, hour: 14 },          │
│   { $push: { readings: { offset: 45, temp: 25.1 } },│
│     $inc: { count: 1, sum_temp: 25.1 },              │
│     $min: { min_temp: 25.1 },                        │
│     $max: { max_temp: 25.1 } },                      │
│   { upsert: true }                                   │
│ )                                                    │
│                                                      │
│ [MONGODB PATTERNS ← YOU ARE HERE: bucket pattern]    │
│                                                      │
│ Query: avg temp for device s42, last 6 hours         │
│ db.sensor_buckets.aggregate([                        │
│   { $match: { device: "s42", date: today,            │
│               hour: { $gte: 8 } } },                 │
│   { $group: { _id: null,                             │
│     avgTemp: { $avg: "$avg_temp" },    // pre-computed│
│     maxTemp: { $max: "$max_temp" } } } // pre-computed│
│ ])                                                   │
│ → 6 documents read (6 hours) + instant aggregation  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**E-COMMERCE ORDER CREATION (Extended Reference + Computed):**

```
User adds item to cart:
→ db.carts.updateOne({user_id}, {
    $push: { items: {product_id, name_snapshot, price_snapshot, qty} },
    $inc: { total: price, item_count: 1 }
  })
→ [MONGODB PATTERNS ← YOU ARE HERE: extended ref + computed]

User views cart:
→ db.carts.findOne({user_id})
→ Returns: items array + pre-computed total + count
→ No $lookup, no aggregation pipeline
→ Single document read in < 1ms

User places order:
→ db.orders.insertOne({
    user_snapshot: {name, email},   // extended reference
    items: cart.items,              // already have name/price snapshots
    total: cart.total,             // pre-computed
    status: "placed"
  })
→ Atomic, single write, no joins needed
```

---

### ⚖️ Comparison Table

| Pattern                | Problem Solved                   | Trade-off                                      |
| ---------------------- | -------------------------------- | ---------------------------------------------- |
| **Bucket**             | Unbounded arrays (time-series)   | More complex write logic                       |
| **Outlier**            | Huge documents for popular items | Application must handle two code paths         |
| **Computed**           | Expensive read-time aggregations | Write overhead; potential stale computed field |
| **Attribute**          | Sparse/heterogeneous attributes  | Less intuitive than named fields               |
| **Extended Reference** | Repeated $lookup joins           | Data duplication; snapshot semantics           |
| **Polymorphic**        | Multiple types in one collection | Application-level type routing                 |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                              |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "MongoDB $lookup is as fast as a SQL JOIN"                     | MongoDB $lookup is a correlated subquery, not a hash join. For large result sets, it degrades quadratically. Avoid in hot paths; use embedding instead               |
| "You should model MongoDB like SQL with references everywhere" | MongoDB performs best with denormalized documents. References are appropriate for large, unbounded, or independently-queried data - not as default                   |
| "MongoDB has no schema - anything goes"                        | "No enforced schema" doesn't mean "no schema." Inconsistent schemas cause application bugs. Use schema versioning and optional $jsonSchema validation                |
| "The bucket pattern is premature optimization"                 | For IoT/time-series with > 1 reading/second/device at scale, the bucket pattern is necessary from day one - retrofitting it later requires full collection migration |

---

### 🚨 Failure Modes & Diagnosis

**1. Unbounded Array Growth**

**Symptom:** Specific documents grow to several MB. Queries against those documents slow dramatically. Eventually: `document size (X bytes) is larger than maximum (16793600 bytes)`.

**Diagnostic:**

```javascript
// Find large documents
db.collection.aggregate([
  { $project: { size: { $bsonSize: "$$ROOT" } } },
  { $sort: { size: -1 } },
  { $limit: 10 },
]);
```

**Fix:** Migrate the unbounded array field to a separate collection with a reference. Use the bucket pattern for time-series. Use the outlier pattern for social data.

---

### 🔗 Related Keywords

**Prerequisites:** Document Store, Schema Evolution, ORM Patterns
**Builds On This:** Polyglot Persistence, System Design
**Related:** Document Store, Polyglot Persistence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY PATTERNS │ Bucket (time-series), Outlier (celebs)    │
│              │ Attribute (sparse), Computed (pre-agg)    │
│              │ Extended Ref (denorm joins), Polymorphic  │
│ EMBED RULE   │ 1:few; always read together; bounded size │
│ REFERENCE    │ 1:many; unbounded; queried independently  │
│ AVOID        │ $lookup in hot paths; unbounded arrays    │
│ ONE-LINER    │ "Design for access patterns, not          │
│              │  normalization - pre-compute what you read"│
│ NEXT EXPLORE │ Redis Data Structures → Redis Persistence │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design the MongoDB schema for a Q&A platform (like Stack Overflow): questions (with tags, votes), answers (with votes), comments on questions and answers, users with reputation scores. Define which data you embed vs. reference. Apply at least 3 of the patterns discussed. Identify which queries will be single-document reads vs. require aggregation.

**Q2.** (TYPE D - Failure Scenario) A social app stores user posts with a `likes` array (user IDs of all who liked). A popular influencer's post accumulates 5 million likes. Developers notice: liking this post takes 3 seconds; querying this post crashes the app server. MongoDB operations on the document fail intermittently. What are the two immediate problems (document size limit + contention)? Design a solution using the outlier pattern + computed pattern to fix both issues.
