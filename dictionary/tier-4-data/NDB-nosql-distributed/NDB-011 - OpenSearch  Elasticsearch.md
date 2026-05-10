---
version: 2
layout: default
title: "OpenSearch  Elasticsearch"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /nosql/opensearch-elasticsearch/
id: NDB-011
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: NoSQL, Distributed Systems, Inverted Index
used_by: Observability & SRE, Big Data & Streaming
related: MongoDB Aggregation Pipeline, AWS CloudWatch Log Insights, Kibana
tags:
  - database
  - distributed
  - observability
  - advanced
  - search
---

# NDB-011 - OpenSearch  Elasticsearch

⚡ TL;DR - OpenSearch and Elasticsearch are distributed search engines built on Apache Lucene's inverted index; sharding, replication, and mapping design determine whether they scale or collapse under real workloads.

| Relation | Keywords |
|---|---|
| Depends on | NoSQL, Distributed Systems, Inverted Index |
| Used by | Observability & SRE, Big Data & Streaming |
| Related | MongoDB Aggregation Pipeline, AWS CloudWatch Log Insights, Kibana |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Full-text search on a SQL `LIKE '%keyword%'` clause cannot use indexes - it is a full table scan on every query. A PostgreSQL `orders` table with 100 million rows returns a `SELECT * WHERE description LIKE '%widget%'` in 45 seconds. A dedicated search table can help, but aggregating search results across multiple fields, boosting by relevance score, and faceting by category simultaneously are features that relational databases fundamentally cannot provide efficiently.

**THE BREAKING POINT:** An e-commerce site adds product search. Users type partial words, misspellings, and multi-field queries simultaneously ("red running shoes size 10 under $100"). The database engineer adds a full-text index - Postgres `tsvector` or MySQL FULLTEXT - but it cannot handle fuzzy matching, field-level boosting, multi-language analyzers, or real-time aggregated facets (category counts, price range histograms). Search quality is poor; performance degrades with scale.

**THE INVENTION MOMENT:** Elasticsearch (2010, built on Lucene) introduced a distributed, schema-aware, REST-API-first search engine that pre-inverts text into token-to-document mappings. Queries become lookups, not scans. Relevance scoring is built-in. Aggregations run in parallel across shards. OpenSearch (AWS fork, 2021) maintains API compatibility while adding features independently.

---

### 📘 Textbook Definition

**Elasticsearch** is a distributed search and analytics engine built on Apache Lucene. It stores documents as JSON, indexes text fields using configurable **analyzers** that tokenize, normalize, and stem text into an **inverted index** (a mapping from tokens to document IDs and positions). It distributes data across **shards** (horizontal partitions) and **replicas** (copies for fault tolerance and read scaling). The **Query DSL** provides a JSON-based query language supporting full-text, fuzzy, phrase, range, geo, and compound queries with relevance scoring. **Aggregations** compute metrics (sum, avg, min/max), bucket data (terms, date histogram, range), and pipeline metrics in parallel across shards. **OpenSearch** is the AWS-maintained fork of Elasticsearch 7.10, maintaining Query DSL and API compatibility while diverging in features (OpenSearch Dashboards, security plugins, ML Commons).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Elasticsearch pre-builds a "reverse lookup" from words to documents so that "find all docs containing 'widget'" is O(1) not O(n).

> Think of the index at the back of a textbook vs reading every page. The inverted index is that back-index, but built for millions of documents and millions of words simultaneously - "widget" → [doc 4, doc 17, doc 301]; "red" → [doc 4, doc 22, doc 301]; intersection = [doc 4, doc 301].

**One insight:** Elasticsearch's power comes from analyzer design, not just indexing. The same word "running", "runs", "ran" should all match a search for "run" - this is stemming, performed by the analyzer at index time and query time. Wrong analyzer design is the most common cause of poor search quality in production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An **inverted index** maps every token to the sorted list of document IDs containing it - enabling set-intersection queries (AND) and union queries (OR) in O(k) time where k is the result set size.
2. Each **shard** is a complete Lucene index - a self-contained search engine. Documents are routed to shards via `hash(routing_key) % numPrimaryShards`.
3. Shard count is **immutable** after index creation (without reindexing) - over-sharding or under-sharding at creation time has permanent consequences.
4. **Mapping** is the schema definition for a field - its type (`text`, `keyword`, `date`, `integer`) determines how it is analyzed and stored; incorrect mapping cannot be changed without reindexing.
5. **Mapping explosion** occurs when dynamic mapping auto-creates fields from arbitrary key-value data (e.g., log metadata) - thousands of dynamically generated fields exhaust heap memory in the cluster.

**DERIVED DESIGN:**

- Text fields for full-text search → `text` type with an analyzer (standard, language-specific, or custom).
- Exact-match and aggregation fields → `keyword` type (not analyzed; stored as-is).
- Most fields need both: use `fields` multi-field mapping (`text` + inner `keyword`).
- Shard count: 20–50 GB per primary shard is the operational sweet spot; over-sharding wastes resources.
- Disable dynamic mapping in production (`dynamic: false` or `dynamic: strict`) to prevent mapping explosion.

**THE TRADE-OFFS:**

**Gain:** Near-real-time full-text search with relevance scoring, distributed horizontal scalability, powerful aggregations (facets, histograms, cardinality), and a rich query DSL that supports 30+ query types including fuzzy, geo-distance, and percolate queries.

**Cost:** Near-real-time means a 1-second default refresh interval - writes are not immediately searchable. Elasticsearch is not an ACID database; `_id`-based get operations are consistent, but search results are eventually consistent across replicas. Mapping changes require full reindex operations. Memory requirements are substantial - heap should be 50% of available RAM, up to 32 GB (compressed OOPs limit).

---

### 🧪 Thought Experiment

**SETUP:** You index 10 million product descriptions in Elasticsearch. A user searches for "wireless headphones noise cancelling".

**WHAT HAPPENS WITHOUT INVERTED INDEX (SQL LIKE):**
`SELECT * FROM products WHERE description LIKE '%wireless%' AND description LIKE '%headphones%' AND description LIKE '%noise%'` - three full table scans, no relevance scoring, no stemming, no fuzzy matching. Result: either 0 results (too strict) or 10 000 results (too broad), none ranked by relevance. Time: 60+ seconds.

**WHAT HAPPENS WITH ELASTICSEARCH:**
1. Analyzer tokenizes the query: `[wireless, headphone, nois, cancel]` (stemmed).
2. Inverted index lookup for each token returns sorted document ID lists.
3. BM25 relevance algorithm scores documents based on term frequency (TF), inverse document frequency (IDF), and field-level boosts.
4. Top 10 results return in 12 ms with a relevance score that reflects how well each product matches all four terms.
5. Aggregation runs in parallel: `terms` aggregation on `brand.keyword` returns facet counts for the result set.

**THE INSIGHT:** The inverted index transforms "does this document contain this word?" from a per-document question (O(n) scan) to a per-word question (O(log m) B-tree lookup in the terms dictionary), where m is the vocabulary size - which is vastly smaller than the number of documents.

---

### 🧠 Mental Model / Analogy

> The inverted index is like a concert venue's seating chart flipped inside out. The normal chart maps seat numbers to patrons (document → words). The inverted index maps patron names to all their seats across every concert (word → document IDs). "Who has seat 4B?" is a document lookup. "Where is Alice sitting across all concerts?" is an inverted index lookup - instant, regardless of how many concerts there are.

- **Each concert** = each document
- **Patron in a seat** = a word appearing in a document
- **Inverted map** = the index: word → [doc1, doc5, doc301, ...]
- **Finding Alice's seats** = searching for a word across all documents

Where this analogy breaks down: a seating chart has one patron per seat; an inverted index maps one word to potentially millions of document positions, with frequency counts and position offsets that enable phrase queries ("noise cancelling" as an exact phrase).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Elasticsearch is a search engine you send documents to. It builds a super-fast lookup table so that "find all documents about X" returns in milliseconds even across millions of documents. OpenSearch is the same thing, maintained by AWS.

**Level 2 - How to use it (junior developer):**
Index a document with `PUT /products/_doc/1 { "title": "...", "description": "..." }`. Search with `GET /products/_search { "query": { "match": { "description": "wireless headphones" } } }`. Use `keyword` type for fields you filter/sort/aggregate on, `text` type for fields you full-text search. Always define an explicit mapping - never rely on dynamic mapping in production.

**Level 3 - How it works (mid-level engineer):**
Each write passes through: parse JSON → route to primary shard via `hash(id) % shards` → Lucene writes to an in-memory buffer → periodically flushed to a Lucene **segment** on disk → segments are merged in the background to reduce file count. Searches query all primary or replica shards in parallel; each shard returns its top-K results; the coordinating node merges and re-ranks them globally. The 1-second refresh interval controls when in-memory buffers are flushed to a searchable segment - this is the "near-real-time" delay.

**Level 4 - Why it was designed this way (senior/staff):**
Elasticsearch's eventual consistency is a deliberate trade-off for distributed write throughput. Making writes immediately searchable across all replicas would require synchronous replication and a distributed consensus protocol - adding latency proportional to replica count. Instead, Elasticsearch uses asynchronous replication (primary writes first, replicas catch up) and the 1-second refresh (configurable) to batch Lucene segment flushes. Segments are immutable once flushed - they are never updated in-place, only merged and replaced. This immutability is the reason why updates in Elasticsearch are actually delete-then-insert operations at the Lucene level (the old document is soft-deleted in the segment; a new document is written; the soft-delete is cleaned up during segment merge). The immutability enables lock-free concurrent reads at the segment level - a key performance property for search workloads.

---

### ⚙️ How It Works (Mechanism)

**Index and Search Flow:**

```
Document Write:
  Client → REST API → Coordinating Node
    → hash(id) → Primary Shard (Node 2)
      → Lucene in-memory buffer
      → refresh (1s): new segment
      → replica async replication
      → document now searchable

Document Search:
  Client → REST API → Coordinating Node
    → broadcast to all shards (primary or replica)
    → each shard: term lookup → BM25 score → top-K
    → coordinating node: merge, re-rank, return top-N
```

**Analyzer Pipeline:**

```
Input text: "Running SHOES for Runners"
     │
     ▼
Char Filter:   "Running SHOES for Runners"
     │
     ▼
Tokenizer:     ["Running","SHOES","for","Runners"]
     │
     ▼
Token Filters: lowercase → ["running","shoes","for","runners"]
               stop words → ["running","shoes","runners"]
               stemmer   → ["run","shoe","runner"]
     │
     ▼
Indexed tokens: run, shoe, runner
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Application indexes product document
          │
          ▼
Coordinating node routes to primary shard
  based on document _id hash
          │
          ▼
Primary shard: write to translog + buffer
          │
          ▼
Async replica replication (ms latency)
          │
          ▼  ← YOU ARE HERE (1s refresh default)
Lucene segment flushed → document searchable
          │
          ▼
Search query: coordinating node fans out
  to all shards → collect top-K → merge
          │
          ▼
Response: hits with _score, _source, aggs
```

**FAILURE PATH:**
- Primary shard fails mid-write → replica promoted → translog replay ensures durability
- All shards for an index are on one node → node failure = data loss if no replicas
- Mapping explosion → heap OOM → cluster goes red → all writes rejected
- Query on high-cardinality `keyword` field with `terms` aggregation → JVM heap exhausted → circuit breaker trips

**WHAT CHANGES AT SCALE:**
- Hot shards: uneven document routing (poor routing key choice) creates hotspot shards while others sit idle
- Index lifecycle management (ILM): time-series indexes (logs) must age from hot nodes to warm to cold to frozen to reduce costs
- Cross-cluster search: federate queries across multiple clusters for geo-distribution or tenant isolation

---

### 💻 Code Example

**BAD - dynamic mapping, no keyword for aggregation:**
```json
PUT /products/_doc/1
{
  "title": "Wireless Headphones",
  "brand": "SoundMax",
  "price": 149.99
}
// brand auto-mapped as "text" - cannot aggregate on it
// price stored as float - aggs work but no explicit mapping
// New fields auto-create mappings → mapping explosion risk
```

**GOOD - explicit mapping, multi-field for text+keyword:**
```json
PUT /products
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.mapping.total_fields.limit": 200
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "brand": {
        "type": "keyword"
      },
      "price": { "type": "float" },
      "createdAt": { "type": "date" }
    }
  }
}
```

**Query DSL - multi-field search with aggregations:**
```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "wireless headphones" } }
      ],
      "filter": [
        { "range": { "price": { "lte": 200 } } },
        { "term": { "brand": "SoundMax" } }
      ]
    }
  },
  "aggs": {
    "by_brand": {
      "terms": { "field": "brand", "size": 10 }
    },
    "price_histogram": {
      "histogram": { "field": "price", "interval": 50 }
    }
  },
  "size": 10,
  "_source": ["title", "brand", "price"]
}
```

---

### ⚖️ Comparison Table

| Feature | Elasticsearch / OpenSearch | MongoDB Atlas Search | Postgres Full-Text | Solr |
|---|---|---|---|---|
| Inverted index | Native (Lucene) | Native (Lucene) | tsvector | Native (Lucene) |
| Relevance scoring | BM25, custom | BM25 | Rank only | BM25, TF-IDF |
| Aggregations | Rich (terms, histogram, pipeline) | Limited | Via SQL | Rich |
| Distributed sharding | Native | Managed by Atlas | No | Native |
| Mapping flexibility | Medium (explicit needed) | Synced from MongoDB | Low | Medium |
| Operational complexity | High | Low (managed) | None (co-located) | High |
| Best for | Dedicated search + analytics | MongoDB-native search | Simple OLTP search | Legacy enterprise |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Elasticsearch is a primary database" | It lacks ACID transactions, has eventual consistency, and soft-deletes updates - it is a search index, not a source of truth |
| "More shards = better performance" | Over-sharding wastes heap (metadata per shard) and CPU (fan-out cost per shard); 20–50 GB/shard is the recommended range |
| "Writes are immediately searchable" | The 1-second default refresh interval means there is always up to a 1-second lag; for real-time needs, set `refresh=wait_for` on write |
| "Dynamic mapping is safe for logs" | Log metadata with variable keys (e.g., user-supplied tags) causes mapping explosion - each unique key becomes a mapped field, exhausting JVM heap |
| "OpenSearch and Elasticsearch are interchangeable" | API-compatible at the Query DSL level, but features diverge significantly past 7.10; OpenSearch has its own ML, security, and dashboards ecosystem |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Mapping Explosion → Cluster OOM**

**Symptom:** Cluster health turns RED; master node becomes unresponsive; logs show `java.lang.OutOfMemoryError: Java heap space`; new index creations fail.
**Root Cause:** Dynamic mapping on a log or event index auto-created thousands of field mappings from variable user-supplied keys or JSON metadata.
**Diagnostic:**
```bash
# Check field count per index
GET /my_logs/_mapping?include_type_name=false \
  | python3 -c "
import json,sys
m = json.load(sys.stdin)
for idx, body in m.items():
    props = body['mappings'].get('properties', {})
    print(f'{idx}: {len(props)} fields')
"

# Check cluster-wide field count
GET /_cluster/stats?human&pretty \
  | grep total_field_count
```
**Fix:** Create a new index with `"dynamic": "strict"` mapping and explicit fields only. Use `object` type with `enabled: false` for arbitrary metadata blobs.
**Prevention:** Always set `"dynamic": "strict"` in production index templates. Set `index.mapping.total_fields.limit: 200` as a circuit-breaker.

---

**Failure Mode 2: Hot Shard Imbalance**

**Symptom:** One data node has CPU at 95% while others sit at 10%; query latency is determined by the slowest (hottest) shard; re-routing shards does not help because the documents are unevenly distributed.
**Root Cause:** Documents are routed using a low-cardinality routing key (e.g., routing by `countryCode` where 80% of documents are `US`) causing all US documents to land on one or two shards.
**Diagnostic:**
```bash
# Check shard-level document counts
GET /_cat/shards/my_index?v&h=index,shard,prirep,docs,store,node

# Look for massive imbalance in docs column
# e.g., shard 0: 8M docs vs shard 1: 100k docs
```
**Fix:** Re-index with a higher-cardinality routing key or remove custom routing to use the default `_id`-based hash (which distributes uniformly).
**Prevention:** Before using a custom routing key, verify its cardinality distribution. For time-series data, route by date (daily/weekly) to distribute load over time.

---

**Failure Mode 3: Slow Aggregations Due to High-Cardinality Terms Aggregation**

**Symptom:** Dashboard queries time out; `terms` aggregation on a `keyword` field with 10 million unique values causes JVM heap to spike; circuit breaker trips with `EsRejectedExecutionException`.
**Root Cause:** `terms` aggregation on a high-cardinality field (user IDs, session IDs) loads all values into a hash map in JVM heap - memory grows proportionally to cardinality.
**Diagnostic:**
```bash
# Check field cardinality before aggregating
GET /my_index/_search
{
  "size": 0,
  "aggs": {
    "unique_count": {
      "cardinality": { "field": "userId" }
    }
  }
}
# If result > 10000, terms agg will be expensive
```
**Fix:** Replace `terms` aggregation on high-cardinality fields with `cardinality` aggregation (HyperLogLog approximation, O(1) memory) or use `sampler` aggregation to limit input documents.
**Prevention:** Reserve `terms` aggregation for fields with < 10 000 unique values. High-cardinality analytics belong in a data warehouse (Snowflake, Redshift), not Elasticsearch.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- NoSQL - the category of databases that includes search engines like Elasticsearch alongside document stores
- Distributed Systems - sharding, replication, and consistency models that underpin Elasticsearch cluster behavior
- Inverted Index - the fundamental data structure that makes Elasticsearch's search performance possible

**Builds On This (learn these next):**
- Observability & SRE - the ELK/OpenSearch stack (Elasticsearch/OpenSearch + Logstash/Fluent Bit + Kibana/Dashboards) is the industry-standard log analytics platform
- Big Data & Streaming - Kafka → Logstash/Beats → Elasticsearch is the standard log pipeline for streaming data

**Alternatives / Comparisons:**
- MongoDB Aggregation Pipeline - document-oriented aggregations contrasted with Elasticsearch's search-first aggregation model
- AWS CloudWatch Log Insights - managed log search for AWS-native workloads
- Kibana - the visualization layer that typically pairs with Elasticsearch

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    Distributed search engine on      │
│               Lucene inverted index             │
│ PROBLEM       SQL LIKE queries can't do         │
│               full-text search at scale         │
│ KEY INSIGHT   Inverted index = word→doc map;    │
│               queries are set intersections     │
│ USE WHEN      Full-text search, log analytics,  │
│               faceted search, geo queries       │
│ AVOID WHEN    Primary database (no ACID);       │
│               very high cardinality aggs        │
│ TRADE-OFF     Near-real-time (1s lag) vs        │
│               millisecond search performance    │
│ ONE-LINER     Explicit mapping + dynamic:strict │
│               = stable production cluster       │
│ NEXT EXPLORE  Snowflake (Cloud Data Warehouse)  │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** Two documents both contain the word "run". Document A has "run" 5 times in a 10-word description. Document B has "run" 1 time in a 1-word title. BM25 scoring considers both term frequency and field length normalization. Which document should score higher for the query "run", and why does the answer change depending on whether you are searching a product catalog vs a news archive?

2. **(B - Scale)** You are indexing 1 billion log documents per day across a 10-node Elasticsearch cluster. Shard size guidelines suggest 40 GB/shard. Walk through the shard sizing calculation: how many primary shards per daily index, how many total shards in a 7-day hot tier, and what happens to query fan-out latency as the number of shards grows?

3. **(A - System Interaction)** An Elasticsearch cluster is used as both a search engine (user-facing, latency-sensitive) and a log aggregation store (batch analytics, throughput-sensitive). How does the `refresh_interval` setting create a fundamental conflict between these two use cases, and what index-level configuration strategy resolves it?
