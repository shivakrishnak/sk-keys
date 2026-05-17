---
id: SYD-051
title: Search System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-014
used_by: ""
related: SYD-008, SYD-014, SYD-046, SYD-031
tags:
  - architecture
  - search
  - elasticsearch
  - inverted-index
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /syd/search-system-design/
---

# SYD-051 - Search System Design

⚡ TL;DR - A search system indexes documents so users
can find relevant results for any query in < 100ms.
The core data structure is an inverted index: for
each term, a list of documents that contain it.
Elasticsearch (built on Lucene) is the standard
production search engine: distributed, horizontally
scalable, with relevance scoring (BM25), fuzzy matching,
and aggregations. Design: indexing pipeline (crawl/ingest
→ tokenize/analyze → write to inverted index), query
pipeline (parse query → retrieve candidates → score
and rank → return top-K), and replication for availability.

| #051 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, CDN | |
| **Related:** | Caching, CDN, Sharding, Search Autocomplete Design | |

---

### 🔥 The Problem This Solves

Amazon has 350 million products. A user searches for
"wireless noise cancelling headphones under $100".
Without a search system, the database query is:
`SELECT * FROM products WHERE description LIKE '%wireless%'
AND description LIKE '%noise%' AND price < 100`.
At 350M rows: this query takes minutes. With full-text
indexing: the system returns the top 10 most relevant
results in 50ms.

---

### 📘 Textbook Definition

**Search system:** A platform that enables full-text
querying across a large corpus of documents, returning
ranked relevant results. Built on an inverted index:
a mapping of terms → document IDs that contain them.

**Inverted index:** A data structure mapping each
unique term to the list of documents containing it.
Query evaluation: look up each query term, intersect
the document lists, rank by relevance score.

**BM25 (Best Match 25):** The standard relevance
scoring function. Scores documents based on term
frequency (how often the term appears in the document),
inverse document frequency (how rare the term is
across all documents), and document length normalization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build an inverted index (term → doc list), then score
and rank documents by relevance at query time.

**One analogy:**
> The index in the back of a textbook:
> "photosynthesis......pages 45, 67, 112"
> "protein................pages 23, 67, 201"
>
> To find chapters discussing both photosynthesis AND
> protein: look up both terms, find the intersection
> (page 67), return that chapter.
>
> The inverted index is this back-of-book index, but
> for billions of documents and millions of terms.

**One insight:**
The key performance insight is that an inverted index
converts a full-document scan into a term lookup +
set intersection. Without the index: O(N) per query
(scan all documents). With the index: O(matches) -
proportional to how many documents contain the query
terms, not the total number of documents. For rare
terms: nearly O(1).

---

### 🔩 First Principles Explanation

**INVERTED INDEX MECHANICS:**
```
Document corpus:
  doc1: "wireless headphones for music"
  doc2: "noise cancelling wireless earbuds"
  doc3: "bluetooth headphones bass"

Tokenization + analysis:
  "wireless headphones for music"
  → tokens: ["wireless", "headphone", "music"]
     (stop words removed: "for"
      stemming applied: "headphones" → "headphone")

Inverted index:
  "wireless":  [doc1, doc2]
  "headphone": [doc1, doc3]
  "music":     [doc1]
  "noise":     [doc2]
  "cancel":    [doc2]
  "earbud":    [doc2]
  "bluetooth": [doc3]
  "bass":      [doc3]

Query: "wireless headphones"
  → tokens: ["wireless", "headphone"]
  → doc list for "wireless": [doc1, doc2]
  → doc list for "headphone": [doc1, doc3]
  → intersection: [doc1]
  → score doc1 by BM25: return as top result

  If no intersection (no exact match):
    → score by union (OR): return docs with ANY term
    → ranking resolves best match
```

**ELASTICSEARCH ARCHITECTURE:**
```
Elasticsearch cluster:
  Cluster: multiple nodes
  Index: logical collection of documents (like a table)
  Shard: a single Lucene instance; physical partition of index
  Replica: copy of a shard (for availability)

Example: 100M product documents
  1 index, 10 primary shards, 1 replica per shard
  = 20 shard instances across the cluster

Write flow:
  PUT /products/_doc/123 {...}
  → Routing: shard = hash(doc_id) % num_shards
  → Write to primary shard → replicate to replica
  → Indexed: available for search after ~1 second
    (Elasticsearch is near-real-time, not real-time)

Query flow:
  GET /products/_search {"query": {"match": ...}}
  → Scatter: query sent to all 10 primary (or replica) shards
  → Each shard searches its local inverted index
  → Gather: coordinator collects results from all shards
  → Merge: rank and return top 10 globally
```

---

### 🧪 Thought Experiment

**SIZING: E-commerce search at Amazon scale**

Products: 350M. Avg product document: 2KB (title,
description, category, attributes).
Index size: 350M × 2KB × 3 (inverted index overhead)
= ~2.1TB. Distributed across 20 shards: ~105GB per shard.
Modern servers with 256GB RAM: shards fit in memory
(hot data). Cold shards: SSDs. Replicas: 1 replica = 4.2TB total.

**Query volume:**
Amazon: 2 billion searches/day = ~23,000 searches/sec.
Peak (Prime Day): 10x = 230,000 searches/sec.
With 20 shards, each shard handles: 230K / 20 = 11,500/sec.
Elasticsearch shard throughput: 10-30K queries/sec per shard.
Cluster can handle peak: ✓

**Indexing rate:**
New/updated products: ~1M/day = ~12/sec.
Elasticsearch write throughput: easily 10K writes/sec.
Near-real-time indexing (1-second delay): acceptable.
For price updates: dedicated price shard or in-memory
overlay (avoid full re-index for single field changes).

---

### 🧠 Mental Model / Analogy

> Building a search engine is like building a library
> catalog system:
>
> Step 1 (Indexing): For every book, read it, extract
> all keywords, and write a card in the card catalog
> under each keyword pointing to that book.
>
> Step 2 (Querying): When someone searches "space exploration",
> pull the cards for "space" and "exploration". Find books
> that appear on both cards. Sort those books by relevance
> (how prominent the words are, how rare they are across
> the library).
>
> The "analysis" step is the librarian deciding that
> "exploring" and "exploration" should be filed under
> the same card (stemming), and that "the" and "and"
> don't need cards at all (stop words).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A search system lets users find documents, products,
or web pages by typing keywords. It returns the most
relevant results instantly. Without it, searching
millions of items would take minutes.

**Level 2 - How to use it (junior developer):**
Use Elasticsearch (ES). Index documents via REST API.
Query with match or multi_match. ES handles tokenization,
relevance scoring, and distribution. Index documents as
they are created or updated. Run a periodic re-index
for bulk changes.

**Level 3 - How it works (mid-level engineer):**
ES shards the index across nodes. Each shard is a Lucene
instance with its own inverted index. On write: routed
to primary shard → replicated. On query: scatter to all
shards → each scores locally → gather + global rank.
Configure analyzers (tokenizer + filters: lowercasing,
stop words, stemming, synonyms) per field. Use
`multi_match` for cross-field queries; `function_score`
for boosting by popularity or recency.

**Level 4 - Why it was designed this way (senior/staff):**
ES's near-real-time (1 second delay) vs real-time:
Lucene segments are immutable. New documents are written
to a new in-memory segment, then periodically flushed
to disk (default: 1 second). Flushed segments are
searchable. The 1-second window is the indexing latency.
For most use cases (products, articles), this is fine.
For truly real-time (trading systems, chat search):
use a separate index for recent documents or reduce the
refresh interval (resource cost: more frequent merges).
The BM25 scoring is a production formula (not "naive"
TF-IDF) because it accounts for document length
normalization (long documents naturally have higher
term counts, which TF-IDF does not correct for).

**Level 5 - Mastery (distinguished engineer):**
At Google/Bing scale, a distributed inverted index is
only the beginning. The ranking pipeline (the part that
turns 1M matching documents into a ranked top-10) is
a multi-stage ML pipeline: (1) candidate retrieval
(inverted index → top-100K by BM25), (2) feature
extraction (200+ features per document-query pair:
PageRank, freshness, click-through rate, semantic
similarity), (3) LambdaMART/LTR model scoring (top-100K
→ top-100), (4) diversity re-ranking (avoid showing
10 results from the same domain), (5) spam filtering.
Vector search (approximate nearest neighbor for semantic
similarity) is now a standard component alongside the
inverted index: hybrid retrieval combines keyword match
(exact terms) with semantic match (meaning similarity).
Elasticsearch 8.x supports vector search natively (ANN
with HNSW index). The engineering challenge is keeping
vector indexes fresh as documents are updated.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SEARCH SYSTEM FLOW                                  │
│                                                      │
│ INDEXING PIPELINE:                                  │
│  Source (DB/events) ──► Indexing Service           │
│  ──► Fetch document data                           │
│  ──► Apply analyzers:                              │
│       lowercase → stop words → stem → synonyms     │
│  ──► PUT /_doc to Elasticsearch                    │
│  ──► Routed to primary shard                       │
│  ──► Replicated to replica shards                  │
│  ──► Available for search in ~1 second             │
│                                                      │
│ QUERY PIPELINE:                                     │
│  User: "wireless headphones" ──► Search API        │
│  ──► Parse query + apply analyzers                 │
│  ──► Scatter: send to all shards                   │
│  ──► Each shard: inverted index lookup + BM25 score│
│  ──► Gather: coordinator collects shard results    │
│  ──► Merge: global sort by score                   │
│  ──► Return top 10 + pagination cursor             │
│                                                      │
│ CACHE:                                              │
│  Popular queries: Redis cache (TTL: 30s-5min)      │
│  Shielding ES from repeated identical queries      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Elasticsearch indexing and querying**
```python
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch(["http://localhost:9200"])

# Create index with custom analyzer
def create_product_index():
    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "product_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",        # Remove "and", "the", etc.
                            "porter_stem", # Stem: "running" → "run"
                            "synonym_filter"
                        ]
                    }
                },
                "filter": {
                    "synonym_filter": {
                        "type": "synonym",
                        "synonyms": [
                            # "earbuds" treated same as "headphones"
                            "earbuds, headphones",
                            "tv, television",
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "product_analyzer",
                    "boost": 3.0  # Title matches rank higher
                },
                "description": {
                    "type": "text",
                    "analyzer": "product_analyzer"
                },
                "price": {"type": "float"},
                "category": {"type": "keyword"},
                "popularity_score": {"type": "float"},
                "indexed_at": {"type": "date"},
            }
        }
    }
    es.indices.create(index="products",
                       body=mapping, ignore=400)

def index_product(product: dict):
    """Index a product document."""
    doc = {
        "title": product["title"],
        "description": product["description"],
        "price": product["price"],
        "category": product["category"],
        "popularity_score": product.get("sales_rank", 0),
        "indexed_at": datetime.utcnow().isoformat(),
    }
    es.index(index="products",
              id=str(product["id"]),
              body=doc)

def search_products(query: str, min_price: float = None,
                     max_price: float = None,
                     page: int = 0, size: int = 10):
    """Full-text product search with optional filters."""
    must_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description"],
                "type": "best_fields",
                "fuzziness": "AUTO",  # Handle typos
            }
        }
    ]

    price_filter = {}
    if min_price is not None:
        price_filter["gte"] = min_price
    if max_price is not None:
        price_filter["lte"] = max_price

    search_body = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "filter": (
                            [{"range": {"price": price_filter}}]
                            if price_filter else []
                        )
                    }
                },
                # Boost popular products in ranking
                "field_value_factor": {
                    "field": "popularity_score",
                    "factor": 0.1,
                    "modifier": "log1p"
                }
            }
        },
        "from": page * size,
        "size": size,
    }

    result = es.search(index="products", body=search_body)
    return [hit["_source"] for hit in result["hits"]["hits"]]
```

**Example 2 - LIKE scan vs inverted index**
```sql
-- BAD: Full-table LIKE scan (no search index)
-- 350M product rows, no index on description

SELECT id, title, price FROM products
WHERE description LIKE '%wireless%'
  AND description LIKE '%headphones%'
  AND price < 100
ORDER BY sales_rank DESC
LIMIT 10;
-- Query time: 8+ minutes on 350M rows.
-- Cannot use B-tree indexes (LIKE with leading wildcard).
-- Kills database performance for all concurrent queries.

-- GOOD: Delegate full-text search to Elasticsearch.
-- Store only IDs and filter columns in the DB index.
-- Use ES for text search; JOIN back to DB for
-- additional data if needed (or store full doc in ES).
-- Query time: < 50ms at scale.
```

---

### ⚖️ Comparison Table

| Approach | Latency | Scale | Full-Text | Maintenance |
|---|---|---|---|---|
| **LIKE scan (SQL)** | Minutes at scale | Not scalable | Limited | None needed |
| **DB full-text search (Postgres tsvector)** | Seconds to minutes | Limited (single node) | Good | Index maintenance |
| **Elasticsearch** | 10-100ms | Horizontal (PB scale) | Excellent | Index management, cluster ops |
| **Custom inverted index** | Sub-ms | Depends on impl | Basic | High (custom code) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Elasticsearch is a database | ES is a search engine and analytics tool, not a primary database. It has eventual consistency, limited transaction support, and no referential integrity. Use ES for search and analytics; use a primary database (Postgres, MySQL) as the source of truth. Keep ES in sync via change data capture (CDC) or event streaming. |
| More shards = better performance | Shards have overhead: each query scans all shards (scatter-gather). Too many shards (especially small ones) increases coordination overhead, memory usage (each shard has its own Lucene instance), and query latency. Rule of thumb: shard size 10-50GB. Calculate: if index will be 500GB → 10-50 shards. Avoid creating dozens of shards for small indexes. |
| Elasticsearch can replace a database for all queries | ES supports filters and aggregations, but it is not optimized for relational queries, arbitrary joins, or ACID transactions. Never use ES as the primary data store for business-critical data. A common pattern: primary store in Postgres, indexed in ES for search. |

---

### 🚨 Failure Modes & Diagnosis

**Index Out of Sync with Database**

**Symptom:**
Products updated in the database (price changes, stock
updates) do not appear in search results. Users see
incorrect prices in search results. Stale data persists
in ES for hours.

**Root Cause:**
The indexing pipeline (writes to ES on DB change) failed
silently. A deployment removed the Kafka consumer
that published DB change events to ES. ES index was
not updated for 12 hours.

**Fix - CDC-based indexing with monitoring:**
```python
# Use Debezium/CDC to capture DB changes → Kafka
# Consumer writes changes to ES
# Monitor: alert if consumer lag exceeds threshold

def monitor_es_freshness():
    """
    Compare latest updated_at in DB vs ES.
    Alert if ES is more than 60 seconds behind.
    """
    # Most recently updated product in DB
    db_latest = db.execute(
        "SELECT MAX(updated_at) FROM products"
    ).scalar()

    # Most recently indexed product in ES
    es_result = es.search(
        index="products",
        body={
            "size": 1,
            "sort": [{"indexed_at": "desc"}],
            "_source": ["indexed_at"]
        }
    )
    es_latest_str = (
        es_result["hits"]["hits"][0]["_source"]["indexed_at"]
        if es_result["hits"]["hits"] else None
    )

    if es_latest_str:
        from datetime import datetime, timezone
        es_latest = datetime.fromisoformat(es_latest_str)
        lag_seconds = (db_latest - es_latest).total_seconds()
        if lag_seconds > 60:
            alert_pagerduty(
                f"ES index lag: {lag_seconds:.0f}s behind DB")
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - query results cached in Redis for popular
  searches; reduces ES load significantly
- `CDN Architecture Pattern` - search result pages
  may be cached at CDN for common queries

**Builds On This (learn these next):**
- `Sharding` - ES sharding follows the same principles
  as database sharding
- `Search Autocomplete Design` - autocomplete complements
  full-text search for the typeahead UX

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INDEX       │ Inverted index: term → [doc_ids].         │
│             │ Build via analyzers: tokenize, stem,      │
│             │ synonyms, stop words.                    │
├─────────────┼──────────────────────────────────────────  │
│ SCORING     │ BM25: term frequency + IDF + doc length  │
│             │ norm. Boost with function_score.         │
├─────────────┼──────────────────────────────────────────  │
│ SHARDING    │ Shard size: 10-50GB. Scatter-gather.     │
│             │ Avoid too many small shards.             │
├─────────────┼──────────────────────────────────────────  │
│ FRESHNESS   │ Near-real-time: ~1s indexing delay.      │
│             │ Monitor ES lag vs DB. Alert > 60s.       │
├─────────────┼──────────────────────────────────────────  │
│ ES vs DB    │ ES = search engine, not primary DB.      │
│             │ DB = source of truth. ES = search index. │
├─────────────┼──────────────────────────────────────────  │
│ FAILURE     │ Index out of sync: CDC + lag monitoring. │
│             │ Auto-alert when lag > threshold.         │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Inverted index + BM25 scoring =        │
│             │  full-text search in < 100ms at scale"  │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Distributed Cache Design → Social Network│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. An inverted index maps terms → document IDs. Query
   evaluation: look up each query term, intersect/union
   the lists, rank by BM25 relevance score. This converts
   O(N) full-scan to O(matches) per query - enabling
   sub-100ms search across hundreds of millions of docs.
2. Elasticsearch is a search engine, not a database. Use
   a primary DB (Postgres) as the source of truth; keep
   ES synchronized via CDC/events. Monitor the sync lag
   and alert when ES is more than 60 seconds behind.
3. Configure analyzers (tokenizer + stop words + stemming
   + synonyms) per field at index creation time. The
   analyzer determines what is indexed. Wrong analyzer =
   wrong search results. Synonyms ("earbuds" = "headphones")
   dramatically improve recall for e-commerce search.

**Interview one-liner:**
"Search system: inverted index maps terms → document ID lists. Query: look up each
term, intersect lists, rank by BM25 (term freq × inverse doc freq × length norm).
Elasticsearch shards the index across nodes: scatter query to all shards → gather
scores → global rank → return top-K. Write path: analyzer pipeline (tokenize →
lowercase → stem → synonyms) → primary shard → replicated. ES is near-real-time
(~1s index delay). ES is a search engine, not a DB: keep Postgres as source of
truth, sync to ES via CDC/Kafka. Monitor ES-DB lag; alert at > 60 seconds."
