---
id: SYD-008
title: Search Autocomplete Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-029, SYD-058
used_by: SYD-071
related: SYD-058, SYD-063, SYD-044
tags:
  - architecture
  - design
  - advanced
  - caching
  - algorithm
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /syd/search-autocomplete-design/
---

# SYD-066 - Search Autocomplete Design

⚡ TL;DR - Search autocomplete returns top-N completions for a prefix in under 100ms at high QPS - solved by a trie or inverted index precomputed and cached at prefix granularity.

| SYD-066         | Category: System Design       | Difficulty: ★★★ |
| :-------------- | :---------------------------- | :-------------- |
| **Depends on:** | SYD-029, SYD-058              |                 |
| **Used by:**    | SYD-071                       |                 |
| **Related:**    | SYD-058, SYD-063, SYD-044    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user types "appl" in a search box. The app queries a DB `LIKE 'appl%'` across 10 billion records. The query takes 5+ seconds and blocks search for all other users. By the time results load, the user has already typed "apple" or given up.

**THE BREAKING POINT:**
Search autocomplete has a latency SLA of < 100ms and fires on every keystroke. A user typing at 60 WPM generates 5 keystrokes/second. At 1M concurrent users that is 5M queries/second - impossible to serve with naive DB lookups.

**THE INVENTION MOMENT:**
Precompute the top-N suggestions for every possible prefix. Store them in a fast in-memory structure (trie or sorted set). Autocomplete becomes a simple key lookup: `prefix -> [top-10 suggestions]`.

**EVOLUTION:**
Early autocomplete used server-side trie traversal. Google introduced ranking by search frequency. Modern autocomplete adds personalization (your recent searches), geographic context (nearby places), ML-based completion (semantic continuation), and typo tolerance. The data pipeline shifted from batch precomputation (hourly/daily rebuilds) to near-real-time updates from trending query logs.

---

### 📘 Textbook Definition

**Search autocomplete** is a service that given a string prefix `q`, returns an ordered list of the most likely completions ranked by relevance, frequency, or personalization signals. The core data structure is a trie or prefix-indexed hash map where each prefix key maps to a ranked list of completions. The system serves prefix lookups at very high QPS with strict sub-100ms latency requirements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
"Given the first 4 characters you typed, here are the 10 most likely completions."

**One analogy:**

> Search autocomplete is like a librarian who has memorized the 10 most popular books whose titles start with any given word-beginning. You say "Har-" and she instantly says "Harry Potter, Harold and Maude, Haruki Murakami..." without searching anything.

**One insight:**
Autocomplete is 99% reads, 1% writes (data pipeline updates suggestions). Optimizing for reads means precomputing all prefix -> suggestions mappings and caching them entirely in memory.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every keystroke triggers a prefix lookup - latency must be < 100ms including network.
2. The same prefix returns the same top suggestions for all users (or personalized per user).
3. Suggestions must be ranked by relevance/frequency, not alphabetically.
4. The prefix space is bounded: 26 letters × max 5-char prefix = ~12M possible nodes in a trie.

**DERIVED DESIGN:**
Offline: collect query logs, count frequency, rank by frequency + other signals. For every prefix of every term, store top-N completions. Online: prefix lookup from in-memory trie or Redis sorted set. Return top-10 results.

**THE TRADE-OFFS:**
**Gain:** Sub-millisecond prefix lookups; scales to billions of users with cached prefixes.
**Cost:** Stale suggestions (updated in batch); high memory for deep prefix trees; personalization requires per-user data injection at query time.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Map prefix -> ranked completions cheaply and fast.
**Accidental:** Typo tolerance, personalization, multi-language support, trending queries.

---

### 🧪 Thought Experiment

**SETUP:** Google Search receives 100K queries/second. Every query fires an autocomplete request on each keystroke. Users type 4 characters on average before selecting. That is 400K autocomplete requests/second.

**WHAT HAPPENS WITHOUT PRECOMPUTATION:**
Each autocomplete scans 8.5B indexed queries for prefix matches. Even with indexing, a single prefix scan takes 50ms at database level. 400K × 50ms query time = 20,000 concurrent DB requests. Impossible.

**WHAT HAPPENS WITH PRECOMPUTED TRIE:**
For "appl", the trie node at `a->p->p->l` already has the top-10 suggestions precomputed and cached. Lookup = one memory access. At 400K QPS, each request costs microseconds. The entire global prefix cache fits in ~100GB of RAM.

**THE INSIGHT:**
Autocomplete is a problem of precomputation scope vs freshness trade-off. Computing all prefix -> suggestions offline and serving from memory converts an impossible real-time computation problem into a trivial cache lookup problem.

---

### 🧠 Mental Model / Analogy

> Search autocomplete is like a dictionary with a special index: for every possible prefix, the index lists the 10 most frequently looked-up words starting with that prefix. Looking up "pre" takes microseconds because the precomputed list is right there.

- **Prefix** = key in the trie/hash (e.g., "appl")
- **Completion** = candidate suggestions (e.g., "apple", "application")
- **Frequency rank** = weight used to sort completions
- **Trie node** = storage for one prefix's completions
- **Batch job** = nightly rebuild of all prefix frequencies
- **Near-real-time update** = streaming trending queries into the trie

Where this analogy breaks down: a dictionary doesn't rank by recency or personalization; real-world autocomplete blends historical frequency with recency and user behavior.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
You type a few letters in a search box and a dropdown shows likely completions. The system already knows the most popular searches starting with those letters and shows them instantly.

**Level 2 - How to use it (junior developer):**
Build a trie from your query log (top 10K queries). On prefix query, traverse trie to prefix node, return top-N sorted children. Or use Redis sorted sets: `ZREVRANGEBYSCORE prefix:appl 0 9` returns top completions.

**Level 3 - How it works (mid-level engineer):**
Data pipeline: collect query logs -> aggregate frequency by term -> for every term, for every prefix of that term, insert into prefix -> suggestions map. Online: receives prefix, looks up in-memory trie or Redis, returns top-10. Ranking: frequency score (count), recency weight, geographic signal, personalization overlay.

**Level 4 - Why it was designed this way (senior/staff):**
The precomputed prefix tree is the bottleneck for storage vs freshness. Updating a trie with trending queries requires either full recomputation (batch, slow, stale) or in-place trie update propagation (complex, lock contention). Modern systems use a two-tier approach: a stable base trie (rebuilt daily) + a small delta layer for trending queries (updated every 15 minutes). The delta layer is merged at query time with a small performance cost. Typo tolerance (Levenshtein distance suggestions) is separate from prefix matching - typically served from a different index.

**Expert Thinking Cues:**
- Ask: "What is the acceptable staleness for suggestions? 1 hour? 1 day?"
- Ask: "Do you need per-user personalization? If yes, prefix cache cannot be global."
- Red flag: autocomplete hitting the DB on every keystroke
- Red flag: updating the trie in place on every query write - lock contention

---

### ⚙️ How It Works (Mechanism)

**Data pipeline (batch):**
```
Query logs -> Aggregate(term, count, date)
For each term T with count >= threshold:
  For each prefix P of T (P = T[0:1], T[0:2], ...):
    sorted_sets[P].add(T, score=count)
    sorted_sets[P].trim_to_top_N(10)
Publish to Redis cluster
```

**Autocomplete query:**
```
User types prefix P
  GET prefix:{P} from Redis
  -> [(term, score), ...] top-10
  -> (Optional) merge with personal history
  -> (Optional) merge with trending delta
  Return suggestions ordered by score
```

**Trie structure:**
```
a -> p -> p -> l -> [apple:9.2M, application:5.1M,
                     apply:3.4M, applet:1.1M, ...]
               e -> [apple:9.2M, appended:2.1M, ...]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[User types "appl" keystroke 4]
         |
         v
[Browser debounces 100ms]  <- YOU ARE HERE
         |
         v
[GET /autocomplete?q=appl]
         |
         v
[Redis lookup: prefix:appl]
         |
         v
[Top 10 completions from sorted set]
         |
         v
[Optional: merge personal history]
         |
         v
[Return JSON: ["apple","application",...]]
         |
         v
[Dropdown renders in < 50ms total]
```

**FAILURE PATH:**
```
[Redis unavailable]
         |
[Fallback: in-process LRU cache (most recent 1K)]
         |
[If miss: return empty (graceful degradation)]
         |
[Alert: autocomplete degraded; investigate Redis]
```

**WHAT CHANGES AT SCALE:**
Shard Redis prefix keys by prefix (a-f shard 0, g-m shard 1, etc.). CDN caching of top prefixes (top 1000 prefixes cover 80% of traffic). Edge nodes with in-process prefix cache reduce Redis calls for common prefixes.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Trie rebuild is a batch process that must swap atomically (old trie -> new trie). Use blue-green deployment for the trie store: rebuild into new Redis keys, then swap the routing pointer. During rebuild window, serve the old trie.

---

### 💻 Code Example

**BAD - real-time DB scan per keystroke:**
```python
# BAD: scans 10B queries on every keystroke
@app.get("/autocomplete")
def autocomplete(q: str, limit=10):
    return db.execute(
        "SELECT term, count FROM queries"
        " WHERE term LIKE ? ORDER BY count DESC LIMIT ?",
        f"{q}%", limit
    ).fetchall()
```

**GOOD - precomputed Redis sorted set:**
```python
import redis
r = redis.Redis()

# Build phase (run in batch data pipeline)
def build_prefix_index(query_counts: dict):
    """query_counts: {term: frequency}"""
    pipe = r.pipeline()
    for term, count in query_counts.items():
        for i in range(1, len(term) + 1):
            prefix = term[:i]
            key = f"ac:prefix:{prefix}"
            pipe.zadd(key, {term: count})
            # Keep only top 10 per prefix
            pipe.zremrangebyrank(key, 0, -11)
    pipe.execute()

# Query phase (real-time, < 1ms)
def autocomplete(prefix: str, limit=10) -> list[str]:
    key = f"ac:prefix:{prefix.lower()}"
    results = r.zrevrangebyscore(
        key, "+inf", "-inf",
        start=0, num=limit
    )
    return [r.decode() for r in results]

# Example usage:
# build_prefix_index({"apple": 9_200_000,
#                     "application": 5_100_000, ...})
# autocomplete("appl") -> ["apple", "application", ...]
```

**How to test / verify correctness:**
- Build index from 1M queries. Query "appl" - assert top result is most frequent term starting with "appl".
- Query a prefix with no matches - assert empty list returned, not error.
- Add a new trending term, rebuild index - assert new term appears in suggestions.

---

### ⚖️ Comparison Table

| Approach          | Latency  | Freshness | Personalization | Memory cost |
| ----------------- | -------- | --------- | --------------- | ----------- |
| DB LIKE query     | 50-500ms | Real-time | Hard            | None        |
| Trie in memory    | < 1ms    | Batch     | Overlay         | Moderate    |
| Redis sorted set  | 1-5ms    | Near-RT   | Overlay         | Moderate    |
| Elasticsearch     | 5-20ms   | Near-RT   | Possible        | High        |
| Inverted index    | 2-10ms   | Near-RT   | Hard            | High        |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Just use DB LIKE query with an index" | LIKE 'prefix%' can use a B-tree index, but at hundreds of thousands of QPS with a 100ms SLA, even indexed DB queries cannot keep up. Precomputed in-memory lookups are required. |
| "Trie is the only data structure for autocomplete" | Redis sorted sets are simpler to implement, easier to update, and scale horizontally. Tries are better for in-process serving with lowest possible latency. Both are valid. |
| "Autocomplete results must be alphabetical" | Results must be ranked by frequency, relevance, or personalization score - not alphabetically. Alphabetical ordering feels random to users and lowers engagement. |
| "Updating suggestions in real-time is easy" | Real-time trie updates require careful locking or lock-free data structures. Most production systems use batch rebuilds (hourly/daily) with a small real-time delta layer for trending terms. |
| "The same autocomplete works globally" | Language, locale, and regional popularity make autocomplete highly regional. A global trie serves poor suggestions for non-English queries or regional brand names. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale autocomplete after popular event**

**Symptom:** Users searching for a trending topic (breaking news) see no autocomplete suggestions for 24 hours.

**Root Cause:** Batch trie rebuild runs nightly; trending queries don't appear until the next rebuild.

**Diagnostic:**
```bash
# Check when trie was last rebuilt
redis-cli get autocomplete:last_build_ts
# Compare to trending query volume
```

**Fix:** Add a streaming delta layer: consume trending queries in near-real-time, inject top trending terms into a small overlay sorted set merged at query time.

**Prevention:** Design two-tier autocomplete from the start: stable base + trending delta.

---

**Failure Mode 2: Prefix explosion for long terms**

**Symptom:** Redis memory usage grows 10x after adding longer compound queries.

**Root Cause:** A 50-character query generates 50 prefix entries, each requiring a sorted set entry.

**Diagnostic:**
```bash
redis-cli --bigkeys
# Look for autocomplete:prefix:* keys with high memory
redis-cli memory usage "ac:prefix:superlongprefix"
```

**Fix:** Limit prefix depth to 15 characters - most users don't type more before selecting. Drop prefixes longer than max_prefix_length.

**Prevention:** Set hard limit: only index prefixes up to 15 characters. Accept that very long-prefix queries fall back to non-autocompleted search.

---

**Failure Mode 3: Autocomplete exposes sensitive queries**

**Symptom:** Autocomplete shows private search terms from other users (medical queries, financial searches).

**Root Cause:** Global frequency-ranked autocomplete surfaces terms that small groups of users search privately.

**Diagnostic:** Audit query log sampling to check for PII or sensitive terms in top suggestions.

**Fix:** Filter sensitive term categories from autocomplete index. Apply minimum frequency threshold (suggest only terms searched by > 1000 unique users).

**Prevention:** Build a term classification pipeline that marks terms as "safe to suggest" before adding to the autocomplete index.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-029 - Capacity Planning]] - estimate QPS and memory requirements
- [[SYD-058 - Denormalization for Scale]] - precomputation is a form of denormalization

**Builds On This (learn these next):**
- [[SYD-071 - System Design at Hyperscale]] - autocomplete design at global scale
- [[SYD-063 - Data Partitioning Strategies]] - shard prefix keys across Redis cluster

**Alternatives / Comparisons:**
- [[SYD-044 - URL Shortener Design]] - similar read-heavy design with precomputed lookups

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Prefix to ranked completion      │
│              │ lookup, precomputed offline      │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Keystroke-level latency (< 100ms)│
│ IT SOLVES    │ impossible with live DB queries  │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Precompute all prefix -> top-N   │
│              │ suggestions; serve from memory   │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Search boxes, address lookup,    │
│              │ command palettes, tag input      │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Dataset changes too frequently   │
│              │ for batch precompute (real-time) │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Freshness (batch rebuild) vs     │
│              │ latency (precomputed wins)       │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Precompute prefix->top-N,       │
│              │ serve from Redis in < 5ms."      │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-067 Notification System      │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Precompute prefix -> top-N suggestions offline; never query DB on keystrokes.
2. Rank by frequency/relevance, not alphabetically - alphabetical feels random.
3. Use a two-tier approach: stable base (daily rebuild) + trending delta (near real-time).

**Interview one-liner:** "Autocomplete precomputes every possible prefix -> top-10 completions sorted by frequency, stores in Redis sorted sets, and serves prefix lookups in under 5ms - batch pipeline updates keep it fresh."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When a computation is too expensive to run at query time but inexpensive to precompute, shift to precomputation. The question is not "can we compute this?" but "when do we compute it - at write or at read time?"

**Where else this pattern appears:**
- **Recommendation engines:** "Customers also bought" lists are precomputed nightly, not computed per user per page load.
- **E-commerce faceted search:** Category counts ("Shoes (1,234)") precomputed by category, not counted at query time.
- **Spell correction:** A dictionary of valid words precomputed with Levenshtein distance clusters, not computed per-query.

---

### 💡 The Surprising Truth

The most expensive part of Google's autocomplete is not the prefix lookup - it is deciding which one of several billion possible prefixes to precompute and which to compute on demand. Google serves autocomplete for 4+ billion unique prefixes globally in 100+ languages. No system can precompute every possible prefix. The insight is that the top 1% of prefixes cover 99% of traffic. Precompute those; serve the long tail via a slower fallback path that most users never hit.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user searches for "COVID-19 treatment" at 9 AM Monday. The query becomes the #1 trending term by 10 AM. Your autocomplete batch pipeline runs at 2 AM daily. How would you add a streaming layer to surface this trending query in autocomplete by 9:15 AM?

*Hint:* Model a streaming pipeline: query logs -> Kafka -> Flink aggregation (15-minute windows) -> Redis delta sorted set. Explore how you merge the delta set with the base trie at query time and how you handle the case where the same term is in both.

**Q2 (Scale):** Your autocomplete serves 500K QPS globally. The prefix "a" has 10,000 valid completions but you only return 10. The sorted set for prefix "a" has 10,000 members but you only ZREVRANGE the top 10. What is the memory cost of storing all 10,000 members vs only storing the top 10, and which would you choose?

*Hint:* Calculate memory per sorted set entry (estimate 60 bytes for term + score). For prefix "a" with 10K members: 600KB. For the full prefix tree with 26 top-level nodes and more at each level, the total grows. Explore the trade-off between prefix tree completeness and memory budget.

**Q3 (Design Trade-off):** Your search autocomplete for an e-commerce site shows product names. A seller who sells 1 product named "xyzmaxpro ultra" wants it to appear in autocomplete when users type "xyzmax". But the product has 0 organic search volume so it never appears in the query frequency log. How do you handle seller-submitted autocomplete terms?

*Hint:* Explore a secondary autocomplete index for seller-sponsored terms (separate from organic frequency-ranked terms), how you prevent seller abuse (fake high-volume terms), and how you merge organic vs sponsored suggestions at display time.
