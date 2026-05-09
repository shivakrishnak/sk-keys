---
version: 1
layout: default
title: "MongoDB Indexing Strategies"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /nosql/mongodb-indexing-strategies/
id: NDB-009
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: MongoDB Document Schema Design, Indexing, Query Optimization
used_by: MongoDB Aggregation Pipeline, MongoDB Schema Evolution
related: B-Tree Index, Compound Index, Text Index
tags:
  - database
  - distributed
  - performance
  - advanced
---

# NDB-009 - MongoDB Indexing Strategies

⚡ TL;DR - MongoDB indexes are B-trees; the compound index ESR rule (Equality, Sort, Range), covered queries, and `explain("executionStats")` are the three tools that separate slow from fast queries.

| Relation | Keywords |
|---|---|
| Depends on | MongoDB Document Schema Design, Indexing, Query Optimization |
| Used by | MongoDB Aggregation Pipeline, MongoDB Schema Evolution |
| Related | B-Tree Index, Compound Index, Text Index |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A MongoDB collection grows from 100 k to 50 million documents. Queries that took 2 ms now take 8 seconds. Adding more RAM and CPU helps briefly, then the pain returns. The development team adds random indexes "to make queries faster" - now writes are slow, the index cache is exhausted, and some indexes are never used. Nobody knows which indexes matter.

**THE BREAKING POINT:** A production incident occurs at 2 AM: a query that filters by `status`, sorts by `createdAt`, and returns the first 20 results runs as a full collection scan. The `explain()` output shows `COLLSCAN` on a 40 million document collection. Latency: 12 seconds. The on-call engineer adds an index - query drops to 3 ms - but the wrong index was added: a single-field index on `createdAt` that is never used once a better compound index exists.

**THE INVENTION MOMENT:** MongoDB provides `explain("executionStats")`, the **ESR compound index rule** (Equality fields first, Sort fields second, Range fields last), covered queries (index-only reads), and specialized index types (TTL, partial, text, wildcard) that turn indexing from guesswork into a systematic engineering discipline.

---

### 📘 Textbook Definition

**MongoDB indexing** stores a sorted B-tree structure on one or more document fields, enabling the query engine to locate matching documents without scanning the entire collection. A **compound index** on multiple fields follows the ESR rule for optimal use. A **covered query** returns all requested fields from the index without touching the document itself. **Partial indexes** cover only documents matching a filter expression, reducing index size. **TTL indexes** automatically expire documents after a time interval. **Multi-key indexes** on array fields index each element separately. The `explain("executionStats")` method reveals whether queries use `IXSCAN` (index scan) or `COLLSCAN` (full collection scan) and quantifies documents examined versus returned.

---

### ⏱️ Understand It in 30 Seconds

**One line:** An index is a sorted shortcut that lets MongoDB find documents without reading the whole collection - the wrong index helps nothing; the right compound index makes a 12-second query take 3 ms.

> Think of a book index. Without it, you read every page to find "concurrency." With a good index, you jump to the exact pages. A bad index - alphabetized by middle name when everyone searches by last name - wastes the same time as reading the whole book.

**One insight:** The ESR rule (Equality → Sort → Range) is the single most actionable compound index design principle. Violating it causes MongoDB to use only part of the index and fall back to an in-memory sort for the rest.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. MongoDB's default index type is a **B-tree** - keys are stored sorted, enabling O(log n) point lookups and O(k) range scans where k is the number of matching entries.
2. The **compound index prefix rule**: a compound index on `{a, b, c}` supports queries on `{a}`, `{a, b}`, `{a, b, c}` but NOT on `{b}`, `{c}`, or `{b, c}` alone.
3. A query is **covered** when the index contains all fields in the query predicate AND the projection - no document fetch (`FETCH` stage) is needed.
4. Each additional index increases write cost (every insert/update/delete must update all indexes) and increases the working set pressure (indexes consume RAM in the WiredTiger cache).
5. The query planner runs multiple candidate plans simultaneously for up to 101 documents and caches the winning plan for subsequent similar queries.

**DERIVED DESIGN:**

- Design indexes for your query shapes, not for your schema shape.
- For queries with both equality and range conditions, put equality fields first in the compound index.
- A covered query requires `_id: 0` in the projection if `_id` is not in the index.
- Partial indexes are strictly better than full indexes when only a subset of documents is ever queried (e.g., `status: "pending"` queries on an `orders` collection where 99% of orders are `completed`).

**THE TRADE-OFFS:**

**Gain:** Index-based lookups reduce query complexity from O(n) collection scan to O(log n) B-tree traversal, enabling consistent low-latency queries regardless of collection size.

**Cost:** Each index adds write overhead, consumes RAM in the WiredTiger cache (indexes must be hot to be effective), and adds storage. An over-indexed collection can be *slower* on writes than an under-indexed one and can cause cache eviction of document data.

---

### 🧪 Thought Experiment

**SETUP:** An `orders` collection has 50 million documents. A query finds orders where `status = "pending"`, sorted by `createdAt` descending, limited to 20. Three index options are proposed.

**WITHOUT ANY INDEX:** Full collection scan: 50 million documents examined, 20 returned. `docsExamined / docsReturned = 2 500 000`. Time: 15 seconds. Unacceptable.

**WITH WRONG INDEX - `{createdAt: -1}` only:** MongoDB must scan all documents sorted by `createdAt` and filter for `status = "pending"` in memory. Examined: 50 million. Time: 10 seconds. Index used for sort but not for selectivity. Still bad.

**WITH ESR-CORRECT COMPOUND INDEX - `{status: 1, createdAt: -1}`:** MongoDB uses the equality condition on `status` to scan only the `"pending"` subset (0.1% of documents = 50 000), already sorted by `createdAt` descending. Documents examined: 50 000. Returned: 20. Time: 2 ms. A 7 500× improvement.

**THE INSIGHT:** Index design is not about indexing "important" fields - it is about designing indexes that match the *exact query shape* and eliminate examined documents. The ESR rule is the mechanical formula for doing this correctly.

---

### 🧠 Mental Model / Analogy

> Think of a library catalog as a compound index. The catalog is organized first by subject area (Equality: "Science"), then by author last name (Sort), then by publication year range (Range). To find all Physics books by authors starting with "K" published after 2000, you navigate directly to Science→K→>2000. Without this order, you'd scan all Science books for K authors, or worse, all books in the library.

- **Subject area** = equality field (most selective, highest cardinality pruning)
- **Author last name** = sort field (enables sorted traversal without in-memory sort)
- **Publication year** = range field (scanned after equality+sort narrow the set)
- **Catalog card** = B-tree index entry pointing to document `_id`

Where this analogy breaks down: a library catalog is static; MongoDB's query planner dynamically caches winning execution plans per query shape and invalidates the cache when collection statistics change significantly (index rebuilds, large data changes).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An index in MongoDB is like the index at the back of a textbook - instead of reading every page, you look up the word and go directly to the right page. The database uses it to find documents fast.

**Level 2 - How to use it (junior developer):**
Always create indexes for every field that appears in a query's `filter`, `sort`, or `projection`. For multiple fields, put equality fields first, sort fields second, range fields last (ESR rule). Run `explain("executionStats")` after creating an index and verify `IXSCAN`, not `COLLSCAN`.

**Level 3 - How it works (mid-level engineer):**
MongoDB's WiredTiger engine stores B-tree index files separately from collection data files. A B-tree index entry contains the indexed field value(s) and a pointer to the document's `RecordId` (physical location). Compound index entries are sorted lexicographically by the key tuple `(field1, field2, ...)` - this is why the prefix rule works. A covered query reads only the B-tree leaf pages (which contain field values) and never loads the heap page (the actual BSON document), eliminating a random I/O per document. Multi-key indexes on arrays store one B-tree entry per array element - a document with a 100-element array contributes 100 index entries.

**Level 4 - Why it was designed this way (senior/staff):**
MongoDB's index architecture closely mirrors PostgreSQL's B-tree implementation, which itself derives from the Bayer & McCreight (1972) B-tree paper. The choice of B-tree over hash indexes for the default type reflects the need to support both point lookups (O(log n)) AND range scans (O(k)) with the same structure. WiredTiger stores indexes in its own cache (separate from the document cache), which means a heavily indexed collection competes for RAM between index pages and document pages - this is why index count must be budgeted, not maximized. The query planner's plan caching (invalidated by significant data changes) reflects the empirical observation that query shapes on a given collection cluster - the same query shape is re-executed thousands of times before the data distribution changes enough to warrant a new plan.

---

### ⚙️ How It Works (Mechanism)

**The ESR Rule for Compound Index Design:**

```
Query: status = "pending"            ← Equality
       ORDER BY createdAt DESC       ← Sort
       WHERE amount > 100            ← Range

ESR Index: { status: 1,             ← E first
             createdAt: -1,         ← S second
             amount: 1 }            ← R last

B-tree traversal:
  1. Seek to status = "pending"     (equality: O(log n))
  2. Scan in createdAt DESC order   (sort: no in-mem sort)
  3. Filter amount > 100 inline     (range: sequential scan)
```

**Index Types Reference:**

| Type | Syntax | Purpose |
|---|---|---|
| Single field | `{field: 1}` | Basic equality/range |
| Compound | `{a:1, b:-1, c:1}` | Multi-field ESR queries |
| Multi-key | `{tags: 1}` (array field) | Array element queries |
| Text | `{desc: "text"}` | Full-text word search |
| Wildcard | `{"$**": 1}` | Dynamic field schemas |
| Partial | `{field:1}`, `partialFilterExpression` | Subset of documents |
| TTL | `{createdAt: 1}`, `expireAfterSeconds` | Auto-expiry |
| 2dsphere | `{location: "2dsphere"}` | Geospatial queries |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Application query: find pending orders,
  sorted by date, limit 20
          │
          ▼
Query planner: inspect available indexes
  Candidates: {status:1} and
  {status:1, createdAt:-1}
          │
          ▼
Plan evaluation: run both for 101 docs
  Winner: {status:1, createdAt:-1}  ← YOU ARE HERE
          │
          ▼
IXSCAN: seek to status="pending"
  traverse createdAt DESC
          │
          ▼
FETCH: load 20 document RecordIds
  (if not covered query)
          │
          ▼
Return 20 documents to application
```

**FAILURE PATH:**
- Index not on filter field → COLLSCAN → latency spike at scale
- Compound index field order violates ESR → partial index use + in-memory sort → `sort stage exceeded memory limit`
- Multi-key index on high-cardinality array (1000 elements/doc) → index size explodes → cache eviction → overall slowdown
- Too many indexes → insert/update writes update all indexes → write throughput collapses

**WHAT CHANGES AT SCALE:**
- At 100 M+ documents, index build time becomes significant - use `background: true` (pre-4.2) or rolling index builds in replica sets
- Index size must fit in WiredTiger cache (`db.collection.stats().totalIndexSize`); if indexes exceed RAM, every query triggers disk I/O
- Partial indexes reduce index size dramatically for collections with heavily skewed access patterns (e.g., query only `status: "active"` documents when 98% are `status: "archived"`)

---

### 💻 Code Example

**BAD - no index strategy, relying on collection scan:**
```javascript
// Query with no supporting index - COLLSCAN on 50M docs
db.orders.find({
  status: "pending",
  createdAt: { $gte: ISODate("2024-01-01") }
}).sort({ createdAt: -1 }).limit(20)
// explain shows: "stage": "COLLSCAN", docsExamined: 50M
```

**GOOD - ESR compound index + verify with explain:**
```javascript
// Create ESR-ordered compound index
db.orders.createIndex(
  { status: 1, createdAt: -1 },
  { name: "idx_status_createdAt" }
)

// Verify with executionStats
const stats = db.orders.find({
  status: "pending",
  createdAt: { $gte: ISODate("2024-01-01") }
}).sort({ createdAt: -1 }).limit(20)
 .explain("executionStats")

// Assert IXSCAN and low docsExamined:
console.log(stats.executionStats.executionStages.stage)
// → "LIMIT" wrapping "FETCH" wrapping "IXSCAN"
console.log(stats.executionStats.totalDocsExamined) // << 1000
console.log(stats.executionStats.totalDocsReturned) // == 20
```

**Partial index - only index active users:**
```javascript
// BAD: full index on 100M user docs when 99% are inactive
db.users.createIndex({ email: 1 })

// GOOD: partial index covers only active users
db.users.createIndex(
  { email: 1 },
  {
    partialFilterExpression: { status: "active" },
    name: "idx_email_active_users_only"
  }
)
// Index size: 1% of full index; query must include
// { status: "active" } to use this index
```

**TTL index for automatic document expiry:**
```javascript
// Auto-delete session documents 24 hours after creation
db.sessions.createIndex(
  { createdAt: 1 },
  {
    expireAfterSeconds: 86400,  // 24 hours
    name: "idx_sessions_ttl"
  }
)
// mongod background thread runs every 60 seconds
// and deletes documents where createdAt < now - 24h
```

---

### ⚖️ Comparison Table

| Index Type | Query Shape | Write Overhead | Size | Use Case |
|---|---|---|---|---|
| Single field | `{a: value}` | Low | Small | Simple equality/range |
| Compound (ESR) | `{a:v, b:v}` + sort | Medium | Medium | Multi-field filtered+sorted |
| Multi-key | `{arr: value}` | High (per element) | Large | Array element queries |
| Partial | `{a:v}` with subset | Very Low | Very Small | Skewed access patterns |
| TTL | time-based expiry | Low | Small | Session/event expiry |
| Text | keyword search | High | Large | Full-text search |
| Wildcard | dynamic fields | Very High | Very Large | Schema-variable documents |
| 2dsphere | `$near`, `$geoWithin` | Medium | Medium | Location queries |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More indexes = faster reads" | More indexes = slower writes + more RAM consumed + risk of cache eviction for document data; index count must be balanced |
| "An index on `{a, b}` automatically helps queries on just `{b}`" | The prefix rule: `{a, b}` helps `{a}` and `{a, b}` queries but NOT `{b}`-only queries - a separate `{b}` index is needed |
| "A covered query requires all document fields in the index" | A covered query requires only the fields in the *projection* and *filter* to be in the index - not all document fields |
| "`_id` index covers all queries" | `_id` index helps only queries filtering on `_id`; all other queries require explicit indexes |
| "explain() with no argument shows the full execution plan" | `explain()` alone returns the query plan without running it; `explain("executionStats")` actually executes the query and returns real metrics like `totalDocsExamined` |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: COLLSCAN on Large Collection**

**Symptom:** Query latency > 5 seconds; `db.currentOp()` shows long-running queries; `explain()` shows `COLLSCAN`.
**Root Cause:** No index exists for the query's filter or sort fields.
**Diagnostic:**
```javascript
// Check current query execution plan
db.orders.find({ status: "pending" })
  .sort({ createdAt: -1 })
  .explain("executionStats")

// Key fields to check:
// executionStats.executionStages.stage → "COLLSCAN" = bad
// executionStats.totalDocsExamined  → should be << collection size
// executionStats.totalDocsReturned  → ratio matters
```
**Fix:** Create an ESR compound index matching the query shape, then re-run `explain()` to confirm `IXSCAN`.
**Prevention:** Before deploying any new query to production, run `explain("executionStats")` and assert `IXSCAN` with `docsExamined / docsReturned < 10`.

---

**Failure Mode 2: In-Memory Sort Exceeds 100 MB Limit**

**Symptom:** `MongoServerError: Exceeded memory limit for $sort stage`; queries fail during sort when dealing with large result sets.
**Root Cause:** The sort field is not covered by the compound index (ESR violation - range field placed before sort field), forcing an in-memory sort of all matching documents.
**Diagnostic:**
```javascript
db.orders.find({ status: "pending",
  amount: { $gt: 100 } })
  .sort({ createdAt: -1 })
  .explain("executionStats")

// Look for: "stage": "SORT" (in-memory sort)
// vs "stage": "IXSCAN" with sort direction matching index
const stages = stats.executionStats.executionStages
// SORT stage means index is not serving the sort
```
**Fix:** Rebuild the compound index following ESR: `{status: 1, createdAt: -1, amount: 1}` - equality first, then sort direction, then range.
**Prevention:** When designing compound indexes, explicitly map each query clause to E, S, or R and verify field order before creating the index.

---

**Failure Mode 3: Index Cache Eviction Causing Latency Spikes**

**Symptom:** Query performance is good at low traffic but degrades under load; `db.serverStatus().wiredTiger.cache` shows high eviction rate; indexes that were fast become slow sporadically.
**Root Cause:** Too many indexes compete with document data for WiredTiger cache space; under load, index pages are evicted and must be re-read from disk on next access.
**Diagnostic:**
```javascript
// Check index sizes vs available cache
const stats = db.orders.stats()
console.log({
  totalIndexSizeMB: stats.totalIndexSize / 1e6,
  avgObjSizeMB: (stats.avgObjSize * stats.count) / 1e6
})

// Check cache utilisation
db.serverStatus().wiredTiger.cache[
  "bytes currently in the cache"
]
// Also check: db.collection.aggregate([{$indexStats:{}}])
// to find indexes with zero or near-zero accesses
```
**Fix:** Drop unused indexes identified by `$indexStats` (ops count = 0). Consolidate redundant indexes (e.g., if `{a,b,c}` exists, `{a}` and `{a,b}` are redundant).
**Prevention:** Monthly review of `$indexStats` output; budget total index size to < 30% of available RAM.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- MongoDB Document Schema Design - the document structure determines which fields are queryable and index-worthy
- Indexing - the general B-tree index concept underlying MongoDB's index implementation
- Query Optimization - the broader discipline of analyzing and improving query execution plans

**Builds On This (learn these next):**
- MongoDB Aggregation Pipeline - pipeline stage index use depends on index design; `$match` and `$sort` leverage these indexes
- MongoDB Schema Evolution - index changes during schema evolution require careful rolling rebuild strategies

**Alternatives / Comparisons:**
- B-Tree Index - the underlying data structure MongoDB's indexes are built on
- Compound Index - the general relational database concept; MongoDB's implementation adds multi-key and partial extensions
- Text Index - MongoDB's full-text search index; contrasts with OpenSearch/Elasticsearch inverted indexes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    B-tree sorted shortcuts to docs;  │
│               compound, partial, TTL types      │
│ PROBLEM       COLLSCAN on large collections     │
│               causes seconds-long query latency │
│ KEY INSIGHT   ESR rule: Equality→Sort→Range;    │
│               covered queries skip doc fetch    │
│ USE WHEN      Any field appears in filter,      │
│               sort, or projection of hot query  │
│ AVOID WHEN    Collection is small (<10k docs);  │
│               write throughput > read frequency │
│ TRADE-OFF     Faster reads vs slower writes,    │
│               more RAM, more disk               │
│ ONE-LINER     explain("executionStats") →       │
│               IXSCAN good, COLLSCAN bad         │
│ NEXT EXPLORE  MongoDB Aggregation Pipeline      │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** A compound index `{status: 1, amount: 1, createdAt: -1}` exists. A query filters on `status` and `createdAt` but NOT `amount`. Does MongoDB use this index, and if so, does it satisfy the sort on `createdAt` without an in-memory sort? Walk through the B-tree key structure to justify your answer.

2. **(B - Scale)** A multi-key index on a `tags` array field exists on a 50 million document collection. Average array size is 20 tags per document. The index has 1 billion entries. What concrete problems does this cause in terms of write amplification, index cache size, and memory budget, and what index strategy resolves this?

3. **(D - Root Cause)** After a large data import (10 million new documents), previously fast queries degrade and never recover even after the import finishes. `explain()` still shows `IXSCAN`. What has changed in MongoDB's query planner that could cause this, and what operation restores the correct plan?
