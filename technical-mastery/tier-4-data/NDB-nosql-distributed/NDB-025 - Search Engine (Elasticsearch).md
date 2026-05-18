---
version: 2
layout: default
title: "Search Engine (Elasticsearch)"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/nosql/search-engine-elasticsearch/
id: NDB-028
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Inverted Index, Document Store, Distributed Systems
used_by: Observability & SRE, Polyglot Persistence, RAG & Agents
related: Document Store, Inverted Index, Vector Database
tags:
  - nosql
  - elasticsearch
  - search
  - deep-dive
---

⚡ TL;DR - Elasticsearch is a distributed search and analytics engine built on an inverted index - enabling sub-second full-text search, faceted filtering, and log analytics across billions of documents, at the cost of near-real-time (not real-time) indexing and eventual consistency within shards.

| #456            | Category: NoSQL & Distributed Databases                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Inverted Index, Document Store, Distributed Systems     |                 |
| **Used by:**    | Observability & SRE, Polyglot Persistence, RAG & Agents |                 |
| **Related:**    | Document Store, Inverted Index, Vector Database         |                 |

---

### 🔥 The Problem This Solves

**RELATIONAL FULL-TEXT SEARCH:**
`SELECT * FROM products WHERE description LIKE '%wireless noise-cancelling headphones%'`. PostgreSQL: sequential scan or trigram index. Works for small datasets. 10 million products: slow. Add typo tolerance ("headphones" vs. "headphone"): impossible. Rank by relevance (exact phrase > partial match > any word): impossible. Faceted navigation ("filter by brand: Sony, count: 342"): requires GROUP BY + count on millions of rows.

**ELASTICSEARCH:**
Index "wireless noise-cancelling headphones" → inverted index maps each word to document IDs. Query: each word → intersect document ID lists → relevance score (BM25). Results in milliseconds. Typo tolerance (fuzzy): built-in. Faceted navigation: `aggregations` → fast because pre-computed. Billion documents: horizontal scale via shards. This is why Elasticsearch powers Amazon, Wikipedia, LinkedIn search.

---

### 📘 Textbook Definition

**Elasticsearch** is a distributed, RESTful search and analytics engine built on **Apache Lucene**. Data is stored as JSON documents; each document is indexed by an **inverted index** - a mapping of each term to the list of documents containing that term. Elasticsearch adds distributed capabilities on top of Lucene: **shards** (horizontal partitioning of an index across nodes), **replicas** (copies for fault tolerance and read scaling), **near-real-time search** (documents are searchable ~1 second after indexing, not immediately). The query DSL supports: full-text search (match, multi_match), term/range filters, aggregations (facets, histograms, metrics), and vector search (kNN). The **ELK Stack** / **Elastic Stack**: Elasticsearch (storage + search) + Logstash / Beats (ingestion) + Kibana (visualization). Used for: application search, log analytics, security information and event management (SIEM), APM.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Elasticsearch inverts the index - instead of "document → words," it stores "word → documents" - enabling instant lookup of all documents containing any word, with relevance ranking and fuzzy matching.

**One analogy:**

> The index at the back of a textbook. Instead of reading every page to find "transformer architecture" (sequential scan), you look up "transformer" in the index → page 142, 281, 394. Look up "architecture" → page 89, 142, 281, 310. Intersection: pages 142, 281 mention both. Elasticsearch does this at massive scale, across millions of documents, in milliseconds.

- "Index at back of textbook" → inverted index
- "Look up 'transformer' → pages" → term → document ID list
- "Intersection of word lists" → Boolean query result
- "Sorted by how often the word appears" → relevance scoring (TF-IDF / BM25)
- "Multiple textbook volumes on multiple shelves" → shards across nodes

**One insight:**
Elasticsearch shines when your query is about the CONTENT of the data - "find me documents that talk about X, ranked by relevance." It's terrible when your query is about exact values - "find the user with id=42" (use a relational DB or key-value store for that). The inverted index optimizes for "given a set of words, find all matching documents." It doesn't optimize for "given a row ID, find the row."

---

### 🔩 First Principles Explanation

**INVERTED INDEX:**

```
Documents:
  doc1: "elasticsearch is a distributed search engine"
  doc2: "search engines use inverted indexes for fast
    queries"
  doc3: "distributed systems require careful design"

Inverted index (simplified):
  "elasticsearch" → [doc1]
  "distributed"   → [doc1, doc3]
  "search"        → [doc1, doc2]
  "engine"        → [doc1]
  "engines"       → [doc2]  (or "engine" with stemming)
  "inverted"      → [doc2]
  "indexes"       → [doc2]
  "design"        → [doc3]

Query: "distributed search"
  "distributed" → [doc1, doc3]
  "search"      → [doc1, doc2]
  Intersection: [doc1] → doc1 matches both → highest score
  doc2 matches "search" only; doc3 matches "distributed"
    only
  → Ranked: doc1 (2 matches), doc2/doc3 (1 match each)
```

**ELASTICSEARCH INDEX + SHARD DESIGN:**

```
Index = logical collection of documents (like a table)
Shard = a Lucene instance; an index is split into N shards
  Primary shard: handles writes
  Replica shard: copy of primary; handles reads; failover

CREATE INDEX:
PUT /products
{
  "settings": {
    "number_of_shards": 3,    // CANNOT change after
      creation
    "number_of_replicas": 1   // can change anytime
  },
  "mappings": {
    "properties": {
      "name":        { "type": "text", "analyzer":
        "english" },
      "price":       { "type": "float" },
      "category":    { "type": "keyword" },  // exact
        match (not analyzed)
      "description": { "type": "text" },
      "created_at":  { "type": "date" }
    }
  }
}

// text → analyzed (tokenized, lowercased, stemmed) →
  inverted index
// keyword → exact match, stored as-is → for
  sorting/filtering/aggregations
```

**QUERY DSL:**

```json
// Full-text search + filter + aggregation
POST /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "description": "wireless noise-cancelling" } }
      ],
      "filter": [
        { "term":  { "category": "headphones" } },
        { "range": { "price": { "gte": 100, "lte": 500 } } }
      ]
    }
  },
  "aggs": {
    "brands": {
      "terms": { "field": "brand.keyword", "size": 10 }
    },
    "avg_price": {
      "avg": { "field": "price" }
    }
  },
  "sort": [
    { "_score": "desc" },
    { "price": "asc" }
  ],
  "size": 20,
  "from": 0
}
```

**NEAR-REAL-TIME (NRT) INDEXING:**

```
Why "near" real-time?
  Document indexed → written to Lucene in-memory buffer
  Lucene refresh (default: 1 second) → segment written to
    disk → searchable
  fsync (flush/commit): every 30s or on explicit call

  Gap: document indexed → 0 to 1 second → searchable
  (vs. relational DB: committed transaction → immediately
    queryable)

  Adjust: "index.refresh_interval": "30s" for bulk
    indexing (throughput)
          "index.refresh_interval": "-1" for fastest bulk
            import
          "index.refresh_interval": "1s" for
            near-real-time search
```

**LOG ANALYTICS (ELK STACK):**

```
Beats/Logstash → Elasticsearch → Kibana

Filebeat on each server:
  Tails /var/log/app/*.log
  Parses log lines → JSON events
  Ships to Logstash (or directly to Elasticsearch)

Logstash:
  filter { grok { match => { "message" =>
    "%{TIMESTAMP_ISO8601:ts} %{LOGLEVEL:level}
      %{GREEDYDATA:msg}" } } }

Elasticsearch:
  Index: logs-2024.01.15 (daily index pattern → easy
    retention management)
  Auto-rollover: create new index daily; delete indices >
    30 days old (ILM)

Kibana:
  Discover: search all logs across time range
  Dashboard: error rate by service, P99 latency, top error
    messages
  Alerting: "more than 100 errors/minute → PagerDuty"
```

---

### 🧪 Thought Experiment

**MAPPING EXPLOSION: THE DYNAMIC MAPPING TRAP**

Elasticsearch, by default, discovers field types automatically from JSON documents:

```json
{ "user_id": 42, "action": "login",
    "metadata": { "browser": "Chrome" } }
```

Fields auto-mapped: `user_id` (long), `action` (text + keyword), `metadata.browser` (text + keyword). Fine.

Now a developer adds arbitrary key-value pairs to metadata:

```json
{ "metadata": { "custom_field_abc123": "value",
    "session_xyz789": "active" } }
```

Each unique key becomes a new field in the mapping. With 1 million unique metadata keys: 1 million fields in the mapping. Elasticsearch stores the mapping in cluster state (in-memory on all nodes). 1 million fields = gigabytes of cluster state → master node OOM → cluster instability → outage.

**FIX:**

```json
// Option 1: Map metadata as a flat object with no subfields indexed
"metadata": { "type": "object", "enabled": false }
// → stored but not searchable; no mapping explosion

// Option 2: Flatten to known fields only; validate before indexing

// Option 3: Use "flattened" type (ES 7.3+)
"metadata": { "type": "flattened" }
// → all subfields treated as keywords; stored in one field; no
// explosion
```

This is one of the most common Elasticsearch production disasters: unconstrained dynamic mapping from application-controlled JSON.

---

### 🧠 Mental Model / Analogy

> Elasticsearch is like a library catalog card system (the Dewey Decimal System + card catalog). For each word in every book, there's a card (inverted index entry) listing every book that contains that word. Finding books about "quantum mechanics": look up both cards → see which books appear on both → those are your best matches. The librarian (relevance scoring) ranks results by how prominently each book discusses these terms. New books added: a cataloger creates new cards within ~1 second (near-real-time indexing). The catalog itself spans multiple buildings (shards).

- "Card for each word" → inverted index entry
- "Books listed on the card" → document IDs
- "Books on both cards" → Boolean query intersection
- "Prominently discussed" → TF-IDF / BM25 relevance score
- "Multiple buildings" → shards across Elasticsearch nodes

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Elasticsearch stores documents (JSON) and lets you search by their content. Instead of scanning every document, it pre-builds an index that maps words to documents - like the index at the back of a book. It ranks results by relevance and scales across many servers. Used for: product search, log search, autocomplete.

**Level 2:** Use `text` for searchable full-text fields; `keyword` for exact match, sorting, aggregations. Design index mappings explicitly (don't rely on dynamic mapping for production). Use `bool` queries: `must` (affects score), `filter` (doesn't affect score, cached). Use `index.refresh_interval: 30s` during bulk indexing for throughput. Use ILM (Index Lifecycle Management) for log rotation (hot → warm → cold → delete). Don't use Elasticsearch as a primary database - it lacks ACID transactions and update semantics are awkward.

**Level 3:** Lucene segments: an Elasticsearch shard = a Lucene index = multiple segment files. New documents go to in-memory buffer → refresh creates a new segment. Over time, many small segments → segment merges (background, like LSM compaction). During merge: old segments deleted, new merged segment created. Merges consume I/O; control with `index.merge.policy.max_merge_at_once`. The BM25 relevance scoring formula: `score = IDF × TF × field length norm`. IDF (inverse document frequency): rarer terms score higher. TF (term frequency within document): more occurrences = higher score. Field length norm: shorter fields score higher (mentioning "elastic" in a 5-word title is more relevant than in a 1,000-word description). kNN vector search (ES 8.x): each document can have a `dense_vector` field; `knn` queries find nearest neighbors via HNSW (Hierarchical Navigable Small World) graph. Used for semantic search with embedding models.

**Level 4:** The tension at the heart of Elasticsearch in production: it's designed as a search and analytics tool, but it gets used as a primary database. The subtle semantic difference: in Elasticsearch, document updates are implemented as delete + re-index (the old document is marked as deleted, a new version is indexed). This means: (1) high update rates cause rapid segment growth (many deleted documents taking space until merge), (2) there's no SQL UPDATE; the "update" API does a GET + merge + PUT (not atomic), (3) cross-document transactions don't exist. The "database" appearance (REST API, CRUD, query results) masks these semantics. Production discipline: Elasticsearch as a secondary index (primary data in PostgreSQL/Cassandra; CDC pipeline syncs to Elasticsearch) avoids these pitfalls entirely. The primary DB provides durability and transactions; Elasticsearch provides search; they're synchronized asynchronously.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ ELASTICSEARCH WRITE + SEARCH FLOW                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ PUT /products/_doc/1 { "name": "Sony WH-1000XM5" }   │
│   → Routing: hash(doc_id) % num_shards = Shard 2    │
│   → Primary Shard 2 (Node B):                        │
│     1. Write to translog (WAL, immediate durability) │
│     2. Add to Lucene in-memory buffer                │
│     3. Replicate to Replica Shard 2 (Node C)         │
│     4. ACK to client                                 │
│   → After 1s: Lucene refresh → new segment           │
│      → document now SEARCHABLE                       │
│   → After 30s or explicit flush: translog fsynced    │
│                                                      │
│ GET /products/_search { "match": { "name": "Sony" }} │
│   → Coordinating node routes to all 3 primary shards │
│   → Each shard: inverted index lookup "sony"         │
│   → Each shard returns top-N hits + scores           │
│   → Coordinating node: merge + re-rank all results   │
│   → Return final top-N to client                     │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCT SEARCH FLOW:**

```
User types: "wireless headphones under $300"
→ Frontend sends: GET /products/_search
→ Elasticsearch bool query:
  must: match "wireless headphones" in description/name
  filter: category=headphones, price < 300
→ [ELASTICSEARCH ← YOU ARE HERE: inverted index query]
→ 3 primary shards queried in parallel
→ Each returns top 20 results with BM25 scores
→ Coordinating node merges 60 results → top 20 by score
→ Aggregations: brand facets computed on all matching docs
→ Response: 20 products + brand counts in < 50ms
```

---

### ⚖️ Comparison Table

| Feature             | Elasticsearch              | PostgreSQL FTS     | Solr                |
| ------------------- | -------------------------- | ------------------ | ------------------- |
| Horizontal scale    | ✅ Native sharding         | ❌ Single node     | ✅ SolrCloud        |
| Relevance ranking   | ✅ BM25 + custom           | Limited            | ✅ BM25             |
| Aggregations/facets | ✅ Native                  | ✅ SQL GROUP BY    | ✅ Native           |
| ACID transactions   | ❌ None                    | ✅ Full            | ❌ None             |
| Real-time updates   | Near-RT (~1s)              | ✅ Immediate       | Near-RT (~1s)       |
| Vector search       | ✅ kNN (8.x+)              | ✅ pgvector        | ✅ Limited          |
| Best for            | Product search, logs, SIEM | Small corpus + SQL | Solr-legacy systems |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                 |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Elasticsearch is a real-time database"                | Documents are searchable ~1 second after indexing (near-real-time, not real-time). `GET /index/_doc/{id}` returns the latest committed version; `_search` may miss documents indexed in the last second |
| "More shards = better performance"                     | Too many shards increases overhead: each shard is a Lucene instance with its own memory and file handles. Rule of thumb: aim for 10-50GB per shard. More shards > more nodes (not just more per node)   |
| "Elasticsearch is ACID and safe as a primary database" | Elasticsearch has no cross-document transactions, no foreign keys, and updates are non-atomic (get + merge + put). Use it as a search index, not as a source of truth                                   |
| "You don't need to define mappings"                    | Dynamic mapping is convenient in development but dangerous in production. Unexpected fields create new mappings (mapping explosion). Always define explicit mappings for production indices             |

---

### 🚨 Failure Modes & Diagnosis

**1. Split Brain - Cluster Status RED**

**Symptom:** Elasticsearch cluster shows RED health. Some shards are unassigned. Nodes cannot communicate with the master. Data may be inaccessible.

**Root Cause:** Master election failure (insufficient `discovery.zen.minimum_master_nodes`), or network partition causes two sub-clusters to each elect a master - each believes it's the only master (split-brain).

**Diagnostic:**

```bash
GET /_cluster/health?pretty
# status: red → one or more primary shards unassigned
# unassigned_shards: N

GET /_cat/shards?v
# Look for UNASSIGNED primary shards

GET /_cluster/allocation/explain
# Explains why a shard is unassigned (disk space, node left, etc.)
```

**Fix:** Ensure `discovery.seed_hosts` and `cluster.initial_master_nodes` are correctly configured. For production: minimum 3 master-eligible nodes with `cluster.election.strategy: supports_voting_only` (ES 7+). Use dedicated master nodes (not data nodes) for large clusters.

---

### 🔗 Related Keywords

**Prerequisites:** Inverted Index, Document Store, Distributed Systems

**Builds On This:** Observability & SRE, Vector Database, RAG & Agents

**Related:** Document Store, Vector Database

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ MODEL        │ JSON docs + inverted index (Lucene)      │
│ QUERY        │ bool/match/filter/aggs + PromQL-like DSL │
│ NEAR-RT      │ Searchable ~1s after indexing            │
│ FIELD TYPES  │ text (analyzed) vs keyword (exact)       │
│ ANTI-PATTERN │ Dynamic mapping + high-cardinality fields│
│              │ Primary DB for transactional data        │
│ ONE-LINER    │ "Inverted index at distributed scale -   │
│              │  relevance search in milliseconds"       │
│ NEXT EXPLORE │ Eventual Consistency in NoSQL → CRDTs    │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design an e-commerce product search using Elasticsearch: 10 million products, 50 languages, fields: name, description, brand, category hierarchy, price, stock_status, ratings. Requirements: full-text search with typo tolerance, faceted navigation (brand, price range, category), personalized ranking (user's purchase history boosts certain brands), and autocomplete for the search bar. Design the index mapping, shard count, query structure, and how to handle multilingual content.

**Q2.** (TYPE D - Failure Scenario) Your Elasticsearch cluster hosts log data for 3 months. Disk usage reaches 95% on data nodes. Elasticsearch starts rejecting index writes with "disk usage exceeded flood watermark." What happens to in-flight indexing? What does Elasticsearch do automatically at 85%, 90%, 95% disk thresholds? What immediate actions can you take to recover? What architectural change prevents recurrence?
