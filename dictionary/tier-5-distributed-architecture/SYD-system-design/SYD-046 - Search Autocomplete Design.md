---
id: SYD-046
title: Search Autocomplete Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-014
used_by: ""
related: SYD-008, SYD-014, SYD-031, SYD-028
tags:
  - architecture
  - search
  - trie
  - autocomplete
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /syd/search-autocomplete-design/
---

# SYD-046 - Search Autocomplete Design

⚡ TL;DR - Search autocomplete returns the top-K
matching suggestions as the user types each character.
The data structure is a trie (prefix tree) augmented
with popularity scores for ranking. At scale, the trie
is precomputed and stored in cache; suggestions are
served from cache with sub-10ms latency. Key design
decisions: how to rank suggestions (frequency, recency,
personalization), how to update the trie as search
popularity changes (batch update vs real-time), and
how to handle billions of queries with consistent
latency.

| #046 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, CDN | |
| **Related:** | Caching, CDN, Sharding, Rate Limiting | |

---

### 🔥 The Problem This Solves

Google processes 5.6 billion searches per day.
As users type "how to cook pas...", they expect to see
"how to cook pasta" suggestions within 100ms of each
keystroke. The challenge:
- ~6.5 billion keystrokes/day (each triggering a query)
- Sub-100ms response required (before the next keystroke)
- Suggestions must reflect recent trending searches
- Personalized suggestions add another layer of computation

Without careful design, each keystroke triggers a full-
text search query against billions of past search entries.

---

### 📘 Textbook Definition

**Search autocomplete (typeahead):** A feature that
returns a ranked list of suggested completions for a
partial search query as the user types. Suggestions
are derived from historical search popularity, trending
queries, or personalization signals.

**Trie (prefix tree):** A tree data structure where
each node represents one character of a string. All
strings with the same prefix share the same ancestor
path. Enables O(prefix_length) lookup of all strings
with a given prefix.

**Augmented trie:** A trie where each node stores the
top-K suggestions for that prefix, pre-ranked by
popularity score. Lookup: O(prefix_length) = O(1)
effectively (bounded by max query length, ~50 chars).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Given "appl", return ["apple pie", "apple music",
"apple stock"] - the top completions with the highest
popularity scores for this prefix.

**One analogy:**
> A dictionary index: looking up words starting with "pre"
> means flipping to the "P" tab, then "PR" page, then
> "PRE" section. All words are grouped by prefix.
> The autocomplete trie does the same, but also stores
> a popularity ranking for each prefix so the most
> common words appear first.

**One insight:**
The key optimization is precomputing the top-K
suggestions at each trie node. Without precomputation,
every lookup must traverse all descendants of the
prefix node to find the top-K (O(N) per query for N
descendants). With precomputation, it's O(1) per node
lookup. The trade-off: precomputation must be refreshed
when query popularity changes.

---

### 🔩 First Principles Explanation

**TRIE STRUCTURE:**
```
Query: "apple"
         root
          |
          a
          |
          p
          |
          p (top-K: ["app store", "apple", "apply"])
         / \
        l   s
        |   |
        e   t
        |   |
        [top-K at "appl": ["apple","apple pie","apple music"]]
        |
        e
        [top-K at "apple": ["apple","apple pie","apple watch"]]

Node structure:
  char: 'p'
  children: {'l': ..., 's': ...}
  top_suggestions: [
    {"query": "apple pie", "score": 95000},
    {"query": "apple music", "score": 87000},
    {"query": "apple watch", "score": 71000},
  ]
```

**WHY STORE TOP-K AT EVERY NODE:**
```
Without precomputed top-K:
  Query: "appl"
  Navigate to node "appl"
  DFS all descendants to find all queries starting with "appl"
  Sort by score
  Return top 5
  
  Cost: O(N) where N = all queries with prefix "appl"
  (can be millions for common prefixes)

With precomputed top-K at each node:
  Query: "appl"
  Navigate to node "appl" → 4 character hops
  Read top_5 list at node "appl" → O(1)
  Return immediately
  
  Cost: O(prefix_length) = O(4)
  Always fast, regardless of how many queries match.
```

**UPDATE STRATEGY:**
```
Option A: Real-time trie updates
  When a user submits a search, immediately update
  all node scores along the query's prefix path.
  
  Problem: Trie is a global shared data structure.
  Updating it on every search requires distributed
  locking or CRDT-based merge. Too complex and slow.

Option B: Batch update (recommended)
  Collect all search queries in a log (Kafka stream).
  Aggregation job (runs every 1-24 hours):
    - Count query frequencies in the batch window
    - Recompute top-K at each affected trie node
    - Build a new trie snapshot
    - Swap in the new trie (blue/green)
  
  Result: Suggestions are 1-24 hours behind trending
  queries. Acceptable for most use cases.

Option C: Hybrid
  Batch update (base trie) + trending override
  A separate "trending" store tracks queries from
  the last 10 minutes. Top-K for a prefix blends
  the base trie score with the trending score.
```

---

### 🧪 Thought Experiment

**SIZING: Google-scale autocomplete**

Searches/day: 5.6 billion
Keystrokes/search (average query 3-4 words at ~15 chars):
  5.6B × 15 = 84 billion keystrokes/day = ~1M QPS

**Latency requirement:** < 100ms per suggestion response
(users type faster than 200ms per keystroke - need to
respond before next keystroke arrives)

**Data volume:**
Unique queries in the trie: ~1 billion distinct queries
Average query length: 15 chars
Trie node count: bounded by total character count in
all queries (with sharing): ~100 million nodes
Per node: char (1B) + children refs (8B × 26 avg 3) + 
  top-5 suggestions (5 × 30 bytes avg = 150B) = ~200 bytes
Total trie size: 100M × 200B = 20GB

20GB fits in memory (Redis cluster or in-process cache).
Each region maintains a full copy of the trie in memory.

**Read path:**
1M QPS → CDN handles ~80% for common prefixes
(CDN TTL: 30-60 seconds for trending stability)
Remaining 200K QPS → distributed trie servers
(each region has trie in memory; no DB reads)

---

### 🧠 Mental Model / Analogy

> The autocomplete trie is like a well-organized bookstore:
>
> Books are organized by genre (first letter), then topic
> (first few letters). Finding "science fiction / space opera"
> books: walk to Sci-Fi section, then to "Space Opera"
> subsection. You do not search every shelf.
>
> The precomputed top-K at each node is like a bestseller
> display at each section entrance: "Top 5 Science Fiction
> books this month" is posted at the Sci-Fi entrance. You
> do not need to scan all shelves to know the bestsellers.
>
> The batch update is like the bookstore updating the
> bestseller display monthly (not after every sale).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you type in a search box, you see suggestions for
what you might be looking for. The system has learned
what people commonly search for, and shows you the most
popular matches for what you've typed so far.

**Level 2 - How to use it (junior developer):**
Build a trie where each node represents a character.
Store the top-K most popular suggestions at each node.
When a user types a prefix, traverse the trie to the
last character, return the top-K suggestions stored
there. Update the trie periodically with fresh popularity
data from a batch aggregation job.

**Level 3 - How it works (mid-level engineer):**
The trie is serialized and stored in Redis (or an in-
process hash map). Each key = prefix string, value =
JSON array of top-K suggestions with scores. Lookup:
GET prefix → return value. Update: batch job runs
hourly, recomputes frequencies, writes new top-K
values per prefix, atomically swaps the trie (RENAME
in Redis, or blue/green deployment for in-process).
CDN caches common prefix responses with a 30-60 second
TTL.

**Level 4 - Why it was designed this way (senior/staff):**
The trie structure maps perfectly to the lookup pattern:
prefix → top suggestions. Any other structure (inverted
index, full-text search engine) would require scanning
more data per lookup. The precomputed top-K at each node
is the key trade-off: it trades storage (one top-K list
per node) for lookup time (O(1) instead of O(descendants)).
Batch updates are preferred over real-time because the
trie is a shared global structure; real-time updates
require complex coordination. The 1-hour lag in
suggestion freshness is acceptable because query
popularity changes slowly (trending topics are
exceptions, handled separately).

**Level 5 - Mastery (distinguished engineer):**
At Google scale, the "global trie" is impractical to
fit on one machine (100+ GB for all languages). The
trie is sharded: query prefixes mapped to shards by
the first 2-3 characters. A query for "ap" routes to
the "ap" shard. Personalization adds another dimension:
the top-K for a prefix is blended with the user's search
history and location. This blending happens in real-time
at the API layer (trie provides population-level top-K;
personalization layer reranks based on user features).
Multi-language support: separate tries per language,
or a unified Unicode trie with language detection to
route the prefix. The hardest problem: suggestions for
rare prefixes (long, unusual queries). The trie may
not have any history for "quantum entanglement observa".
Fallback: fuzzy matching or prefix-tolerant search.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ AUTOCOMPLETE SYSTEM                                 │
│                                                      │
│ BUILD (batch, every 1 hour):                        │
│  Search logs ──► Aggregation Job                   │
│  ──► Count frequencies by query (last 7 days)      │
│  ──► For each prefix in trie:                      │
│       Compute top-5 by frequency score              │
│  ──► Serialize trie to Redis/storage               │
│  ──► Atomic swap (new trie becomes live)           │
│                                                      │
│ SERVE (real-time):                                  │
│  User types "app" ──► CDN cache HIT (cached 30s)  │
│    ──► Return ["apple", "app store", ...]          │
│                                                      │
│  User types rare prefix ──► CDN cache MISS         │
│    ──► API server ──► Redis lookup("trie:app_sl")  │
│    ──► Return suggestions                          │
│    ──► CDN caches response for 30s                 │
│                                                      │
│ SCALE HANDLING:                                     │
│  1M QPS → CDN absorbs ~80% (common prefixes)      │
│  200K QPS → Redis Cluster (trie in memory)        │
│  Trie servers: stateless, horizontal scale        │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Trie with precomputed top-K (Python)**
```python
import heapq
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children: dict = {}
        # Precomputed top-K for this prefix
        # List of (score, query) tuples, descending by score
        self.top_k: list = []

class AutocompleteTrie:
    def __init__(self, k: int = 5):
        self.root = TrieNode()
        self.k = k

    def insert(self, query: str, score: int):
        """Insert a query with its frequency score."""
        node = self.root
        for char in query.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            # Update top-K at this prefix node
            # Add new entry and keep top-K
            self._update_top_k(node, query, score)

    def _update_top_k(self, node: TrieNode,
                       query: str, score: int):
        """Keep only top-K entries by score."""
        # Check if query already exists (update score)
        existing = next(
            (i for i, (s, q) in enumerate(node.top_k)
             if q == query), None)
        if existing is not None:
            node.top_k[existing] = (score, query)
        else:
            node.top_k.append((score, query))

        # Sort descending by score, keep top-K
        node.top_k.sort(key=lambda x: x[0], reverse=True)
        node.top_k = node.top_k[:self.k]

    def search(self, prefix: str) -> list:
        """Return top-K suggestions for prefix."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []  # No match for this prefix
            node = node.children[char]
        # Return top-K precomputed at this node
        return [query for _, query in node.top_k]

# Build trie from historical data
trie = AutocompleteTrie(k=5)
search_data = [
    ("apple pie", 95000),
    ("apple music", 87000),
    ("apple watch", 71000),
    ("apple stock", 65000),
    ("apple store", 60000),
    ("application form", 45000),
    ("apply for job", 30000),
]
for query, score in search_data:
    trie.insert(query, score)

# Query
print(trie.search("app"))
# ["apple pie", "apple music", "apple watch",
#  "apple stock", "apple store"]
print(trie.search("appl"))
# ["apple pie", "apple music", "apple watch",
#  "apple stock", "apple store"]
```

**Example 2 - Redis-backed trie (production pattern)**
```python
import redis
import json

r = redis.Redis()
TRIE_KEY_PREFIX = "ac:"  # autocomplete

def build_trie_in_redis(queries: list):
    """
    Batch-build trie in Redis from query-score list.
    queries: list of (query, score) tuples.
    Called hourly by batch aggregation job.
    """
    prefix_scores = defaultdict(list)

    for query, score in queries:
        query = query.lower()
        # For each prefix of this query
        for i in range(1, len(query) + 1):
            prefix = query[:i]
            prefix_scores[prefix].append((score, query))

    # Write top-5 for each prefix to Redis
    pipe = r.pipeline()
    for prefix, scores in prefix_scores.items():
        scores.sort(key=lambda x: x[0], reverse=True)
        top5 = [q for _, q in scores[:5]]
        pipe.set(
            f"{TRIE_KEY_PREFIX}{prefix}",
            json.dumps(top5),
            ex=7200  # 2-hour TTL
        )
    pipe.execute()

def get_suggestions(prefix: str) -> list:
    """Look up top-K suggestions for prefix."""
    key = f"{TRIE_KEY_PREFIX}{prefix.lower()}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return []
```

---

### ⚖️ Comparison Table

| Approach | Lookup Speed | Update Complexity | Storage | Freshness |
|---|---|---|---|---|
| **Augmented trie (precomputed top-K)** | O(prefix_len) = ~O(1) | High (rebuild on update) | Medium (one list per node) | Batch (hourly) |
| **Plain trie (no precomputed top-K)** | O(all descendants) | Simple (insert) | Small | Real-time |
| **Prefix in Elasticsearch** | ~10-50ms | Simple (index) | Large | Real-time |
| **Redis sorted sets per prefix** | O(log N) | Simple (ZADD) | Large | Real-time |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Elasticsearch can serve autocomplete suggestions sub-10ms | Elasticsearch's prefix queries (match_phrase_prefix, completion suggester) typically return results in 5-50ms at moderate load. For 1M QPS with sub-5ms requirement, a precomputed in-memory trie is significantly faster. Use Elasticsearch for full-text search; use an in-memory trie for autocomplete latency requirements. |
| The trie must be in a database | At 20GB, the trie fits entirely in memory on a single server (or Redis cluster). In-memory lookup is orders of magnitude faster than any database read. Serialize the trie to storage for durability and reconstruction after restarts, but serve it from memory for production traffic. |
| Real-time updates are necessary for good suggestions | For most queries, frequencies change slowly (hourly batch is fine). The exception is trending topics (suddenly popular within minutes). Handle trending separately: a lightweight trending service tracks queries from the last 10-15 minutes and injects top trending queries into the autocomplete response, overriding the hourly trie for those specific terms. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Suggestions After High-Profile Event**

**Symptom:**
A major news event happens (e.g., earthquake). Within
minutes, "earthquake california 2025" is being searched
millions of times. But autocomplete still shows old
suggestions for "earthquake" prefix (last updated 1 hour
ago). Users see stale suggestions for trending queries.

**Root Cause:** Batch trie update runs hourly. Trending
queries within the last hour are not reflected.

**Fix - Trending overlay:**
```python
import redis
import time
import json

r = redis.Redis()
TRENDING_WINDOW = 600  # 10 minutes in seconds

def record_search_query(query: str):
    """Record a query in the trending sorted set."""
    ts = time.time()
    # Use sorted set: score=count, member=query
    r.zincrby("trending:queries", 1, query.lower())
    # Expire old entries periodically (separate job)

def get_suggestions_with_trending(prefix: str) -> list:
    """Return suggestions blended with trending."""
    # Base suggestions from hourly trie
    key = f"ac:{prefix.lower()}"
    base = json.loads(r.get(key) or "[]")

    # Trending queries matching this prefix
    # (simplified: scan trending set for prefix match)
    all_trending = r.zrevrangebyscore(
        "trending:queries", "+inf", 0, start=0, num=100)
    trending_matches = [
        q.decode() for q in all_trending
        if q.decode().startswith(prefix.lower())
    ][:2]  # Inject top 2 trending matches

    # Merge: trending first, then base (deduplicated)
    merged = trending_matches.copy()
    for s in base:
        if s not in merged:
            merged.append(s)
    return merged[:5]  # Return top 5
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - trie served from in-memory cache; CDN
  caches common prefix responses
- `CDN Architecture Pattern` - CDN absorbs 80% of
  autocomplete traffic for common prefixes

**Builds On This (learn these next):**
- `Sharding` - trie sharded by prefix first-chars
  for horizontal scale
- `Rate Limiting (System)` - protect the autocomplete
  API from excessive per-user request rates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DATA STRUCT │ Trie + precomputed top-K at each node.    │
│             │ Lookup: O(prefix_len) ≈ O(1). Fast.      │
├─────────────┼──────────────────────────────────────────  │
│ STORAGE     │ 20GB for 1B queries. Fits in Redis.       │
│             │ Serve from in-memory. Batch build hourly. │
├─────────────┼──────────────────────────────────────────  │
│ SCALE       │ CDN caches 80% (common prefixes).        │
│             │ 1M QPS → 200K hits trie servers.          │
├─────────────┼──────────────────────────────────────────  │
│ FRESHNESS   │ Hourly batch (base). + Trending overlay  │
│             │ (last 10 min, injected at read time).    │
├─────────────┼──────────────────────────────────────────  │
│ UPDATE      │ Batch: aggregate query log → recompute  │
│             │ top-K per prefix → atomic Redis swap.   │
├─────────────┼──────────────────────────────────────────  │
│ FAILURE     │ Stale for trending: overlay trending     │
│             │ sorted set queries at read time.         │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Augmented trie: precomputed top-K per  │
│             │  node; hourly batch + trending overlay" │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Notification System → Chat System Design │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use a trie with precomputed top-K suggestions at
   each node. Lookup is O(prefix_length) - independent
   of the number of matching queries. This is the key
   optimization over scanning all descendants.
2. Store the trie in memory (Redis or in-process). 20GB
   fits on one machine for 1 billion queries. Update
   hourly via a batch aggregation job (atomic swap to
   replace the old trie with the new one).
3. For trending queries (high-frequency within the last
   10 minutes), maintain a separate sorted set and
   inject trending matches into the top-K result at
   read time. This overcomes the 1-hour batch lag for
   time-sensitive trending topics.

**Interview one-liner:**
"Search autocomplete: augmented trie where each node stores the
precomputed top-K suggestions for that prefix (sorted by frequency).
Lookup is O(prefix_length) - constant time per character, no descendant
scan needed. Trie built hourly by a batch aggregation job (count
frequencies from search logs, recompute top-K per node, atomic Redis
swap). 20GB for 1B queries - fits in memory. At scale: CDN caches
common prefix responses (30-60s TTL) to absorb 80% of traffic.
Trending topics: separate Redis sorted set for last-10-minute queries,
injected at read time to override stale hourly trie results."
