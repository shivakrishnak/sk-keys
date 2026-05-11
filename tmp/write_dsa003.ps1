# Run with: pwsh -ExecutionPolicy Bypass -File tmp\write_dsa003.ps1
Set-Location "c:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-1-foundations\DSA-data-structures"

$content = @'
---
id: DSA-003
title: "DSA in Real Systems - Where They Appear"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-001
used_by: DSA-006, DSA-010, DSA-019
related: DSA-002, DSA-004
tags:
  - dsa
  - foundational
  - production
  - mental-model
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /dsa/dsa-in-real-systems-where-they-appear/
---

# DSA-003 - DSA in Real Systems - Where They Appear

⚡ TL;DR - Every production system you use daily — databases, browsers, social networks, GPS — is built on a small set of DSA primitives that most engineers never consciously recognise.

| #3 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DSA-001 | |
| **Used by:** | DSA-006, DSA-010, DSA-019 | |
| **Related:** | DSA-002, DSA-004 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A junior engineer learns DSA in isolation — sorting algorithms, tree traversals, graph searches. They pass the interview. On their first day, they're handed a service that "manages the event queue," "maintains the friend graph," and "indexes documents by keyword." They can implement a heap from scratch on a whiteboard. But they cannot see that the event queue *is* a heap, the friend graph *is* an adjacency list, and the keyword index *is* an inverted index backed by a hash map. The DSA knowledge sits inert, disconnected from the production systems they maintain every day.

**THE BREAKING POINT:**
When a production incident occurs — the event queue backs up, the graph query times out, the document search slows — the engineer has no mental model connecting the symptom to the underlying structure. They treat it as an infrastructure problem when it is an algorithmic one. The fix takes weeks instead of hours.

**THE INVENTION MOMENT:**
This is exactly the gap DSA-in-real-systems closes. Every production primitive has a DSA analog. Recognising that analog gives engineers the theoretical backing to predict behaviour, diagnose failures, and choose improvements. DSA is not interview preparation — it is the vocabulary for understanding every system you will ever maintain.

**EVOLUTION:**
In the 1960s-80s, engineers who built operating systems and databases explicitly designed their own data structures from first principles. Today, those structures are packaged in libraries and cloud services. The structures are still there — just invisible under abstraction layers. As systems grow more complex, the ability to see through the abstraction to the underlying DSA primitive is increasingly the differentiator between a senior and a distinguished engineer.

---

### 📘 Textbook Definition

**DSA in real systems** refers to the direct mapping between theoretical computer science constructs — arrays, hash maps, trees, graphs, heaps, queues — and the concrete implementations powering production software. Every major software system uses these primitives as its core data organisation and processing strategy. Understanding the mapping allows engineers to predict system behaviour, diagnose anomalies, and evaluate design trade-offs using the formal properties of the underlying structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every production system is a DSA structure with a brand name on it.

**One analogy:**
> A car's dashboard shows speed and fuel. Understanding the engine, transmission, and fuel injection system lets a mechanic fix what the driver only observes. DSA is the mechanic's model of what is actually running beneath the abstraction.

**One insight:**
When you understand that a Redis sorted set is a skip list + hash map, you instantly know why range queries are fast (O(log n)) but membership checks require both structures — without reading Redis documentation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every production system stores data in some structure — that structure determines what operations are fast and what are slow.
2. The structure is determined by the dominant access pattern at design time — lookup-heavy systems use hash maps; order-sensitive systems use trees; relationship-heavy systems use graphs.
3. Cloud abstractions hide structures but do not change their complexity — S3 key lookups are still O(1); DynamoDB scans are still O(n).

**DERIVED DESIGN:**
Because every system inherits the trade-offs of its underlying DSA primitive, engineers who can see through abstractions to the underlying structure can reason about performance, failure modes, and scaling limits without needing to instrument and measure everything empirically.

**THE TRADE-OFFS:**
**Gain:** Ability to predict system behaviour and diagnose failures from first principles rather than trial and error.
**Cost:** Requires building and maintaining a mental map of structure → system. This knowledge must be updated as new systems (e.g., Bloom filter-based caches) emerge.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The fundamental access-pattern trade-offs of each structure — hash maps give O(1) lookup but no ordering; sorted trees give O(log n) lookup with ordering. These are invariant regardless of the system wrapping them.
**Accidental:** The API surface, configuration options, and operational concerns specific to each cloud service or library — these vary and can be learned separately once the DSA foundation is understood.

---

### 🧪 Thought Experiment

**SETUP:**
You are on-call. An alert fires: "Elasticsearch query P99 latency spiked from 50ms to 8,000ms." You have no context.

**WHAT HAPPENS WITHOUT DSA KNOWLEDGE:**
You increase the Elasticsearch cluster size, restart nodes, clear caches. Latency drops temporarily, returns at the next load spike. Three on-call rotations later, the issue recurs. An SRE eventually traces it to a wildcard prefix query (`*keyword*`) that forces a full inverted-index scan — O(n) documents — rather than a prefix lookup — O(log n). The fix is a query change, not more hardware.

**WHAT HAPPENS WITH DSA KNOWLEDGE:**
You recognise that Elasticsearch's core is an inverted index — a hash map of term → document list. A leading wildcard breaks the index because the hash map can only fast-path on exact-key or prefix lookups, not suffix lookups. You immediately suspect a wildcard-prefix query pattern, confirm with a slow-query log, and change the query to a prefix match. Latency returns to 50ms.

**THE INSIGHT:**
Production incident resolution speed is directly proportional to the engineer's ability to map the symptom to the underlying DSA structure. DSA knowledge is the fastest debugging tool you have.

---

### 🧠 Mental Model / Analogy

> Every production system is a building. The DSA structures are the load-bearing walls, floors, and plumbing — invisible after construction but determining everything about what the building can do. The brand-name feature ("real-time notifications," "friend recommendations," "full-text search") is the interior decoration. An architect who only knows the decoration cannot redesign the floor plan.

- "Load-bearing wall" → the underlying data structure (hash map, tree, graph)
- "Plumbing" → the algorithm (BFS for graph traversal, binary search for index lookup)
- "Interior decoration" → the product feature name (notifications, search, recommendations)
- "Redesigning the floor plan" → changing the data structure to support new access patterns

Where this analogy breaks down: unlike buildings, software systems can restructure their data stores dynamically — but the cost of doing so at scale is similarly large.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The apps and services you use every day — Google Search, Twitter's timeline, Uber's routing — are not magic. They are built from a small set of building-block data structures and algorithms that computer scientists have studied for decades. Understanding those building blocks lets you understand how any system works and why it behaves the way it does.

**Level 2 - How to use it (junior developer):**
When you encounter a new system or service, ask: "What is the dominant access pattern, and what structure is most likely powering it?" A cache is almost always a hash map. A feed is almost always a priority queue or sorted list. A routing system is almost always a weighted graph. This mental habit accelerates both learning and debugging.

**Level 3 - How it works (mid-level engineer):**
Specific mappings: database B-tree index → O(log n) range queries; Redis hash → O(1) field lookup; Kafka topic partition → append-only log for O(1) writes; DNS cache → hash map for O(1) domain resolution; Git history → directed acyclic graph for O(n) traversal. Knowing these mappings lets you reason about performance limits without instrumentation.

**Level 4 - Why it was designed this way (senior/staff):**
System designers chose their underlying structures based on access-pattern analysis performed before any code was written. PostgreSQL chose B+ trees for indexes (not hash maps) because range queries are frequent in relational data. Redis chose skip lists for sorted sets (not balanced BSTs) because concurrent skip lists have better lock-free properties. Understanding *why* these choices were made is prerequisite to designing new systems correctly.

**Level 5 - Mastery (distinguished engineer):**
At mastery level you evaluate systems by their structural trade-offs, not their marketing. When evaluating a new time-series database, you ask: "Is the primary index a sorted log, a B-tree, or an LSM tree? What does that choice imply about write amplification, read latency, and compaction cost?" You can predict failure modes of systems you have never used by analysing their structure from documentation.

*Expert Thinking Cues: For any system, ask: "What structure powers the hot path?" Then ask: "What operations does that structure make expensive?" The answer predicts every performance limit and failure mode.*

---

### ⚙️ How It Works (Mechanism)

**The DSA-to-system mapping follows a pattern:**

1. **Identify the dominant access pattern** — what does the system do most? (lookup, insert, range-query, traverse, prioritize)
2. **Map to the DSA primitive** — the structure is selected to make the dominant operation O(1) or O(log n)
3. **Accept the structural trade-off** — the structure makes other operations expensive; the system design works around them

**Key mappings every engineer should internalize:**

| System/Feature | Underlying DSA Primitive | Why That Structure |
|---|---|---|
| Database index (PostgreSQL, MySQL) | B+ Tree | O(log n) range queries + sorted traversal |
| Key-value cache (Redis GET/SET) | Hash Map | O(1) lookup and insert |
| Priority queue / task scheduler | Binary Heap | O(log n) insert + O(1) min/max |
| Social graph (friend-of-friend) | Adjacency List Graph | O(V+E) traversal, sparse edges |
| Full-text search (Elasticsearch) | Inverted Index (Hash Map) | O(1) term lookup → doc list |
| URL routing (routers, HTTP) | Trie | O(k) prefix lookup, k = URL length |
| LRU cache eviction | Hash Map + Doubly Linked List | O(1) lookup + O(1) eviction |
| Network packet routing (BGP) | Weighted Graph + Dijkstra | O(E log V) shortest path |
| Git commit history | Directed Acyclic Graph | O(n) history traversal |
| DNS resolution | Hash Map + TTL | O(1) cached lookup |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User action (search, click, route) → API call
→ System identifies operation type
→ [UNDERLYING DSA STRUCTURE ← YOU ARE HERE]
→ O(1)/O(log n) fast-path executes → Response returned
```

**FAILURE PATH:**
Query pattern bypasses index → Structure falls back to scan → O(n) execution at production N → Latency spike → Alert fires → Engineer without DSA knowledge adds hardware → Problem returns

**WHAT CHANGES AT SCALE:**
At small scale, even scans are fast enough. At production scale, only operations that match the structure's fast path (O(1) or O(log n)) remain within latency budgets. Scale reveals which system queries are hitting the fast path and which are not.

---

### 💻 Code Example

```python
# Demonstrating three production DSA primitives in one
# mini URL-shortener service

from collections import defaultdict
import heapq

# 1. HASH MAP — O(1) URL lookup (Redis GET equivalent)
url_store = {}

def shorten(long_url: str, short_code: str):
    url_store[short_code] = long_url  # O(1) insert

def resolve(short_code: str) -> str:
    return url_store.get(short_code)  # O(1) lookup

# 2. MIN-HEAP — priority queue for scheduled sends
# (task-scheduler equivalent)
scheduled = []  # heap: (timestamp, url)

def schedule_send(url: str, at_ts: int):
    heapq.heappush(scheduled, (at_ts, url))  # O(log n)

def next_due() -> str:
    if scheduled:
        return heapq.heappop(scheduled)[1]  # O(log n)

# 3. GRAPH — link relationship tracking
# (social graph / backlink equivalent)
link_graph = defaultdict(set)

def record_click(from_url: str, short_code: str):
    link_graph[from_url].add(short_code)  # O(1)

def referrers(short_code: str) -> list:
    # O(V+E) — must scan all sources
    return [src for src, codes in link_graph.items()
            if short_code in codes]
```

**How to test / verify correctness:**
Time `resolve()` at 1K, 1M, and 10M entries — it should stay flat (hash map O(1)). Time `next_due()` at 1K and 1M entries — it should grow as log(n). Time `referrers()` at 1M entries — it will grow linearly, confirming this is the O(n) scan that would need re-design at scale.

---

### ⚖️ Comparison Table

| System capability | DSA primitive | O(lookup) | Limitation |
|---|---|---|---|
| Key-value cache | Hash Map | O(1) | No ordering, no range queries |
| Relational index | B+ Tree | O(log n) | Slower insert than hash map |
| Full-text search | Inverted Index | O(1) term | Wildcard prefix is O(n) |
| Task scheduling | Binary Heap | O(log n) | No O(1) arbitrary deletion |
| Graph traversal | Adjacency List | O(V+E) | Memory grows with edge count |

How to choose: Match the dominant access pattern. Need exact-key fast lookup? Hash map. Need range queries? B+ tree. Need shortest path in a graph? Adjacency list + Dijkstra.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Cloud services abstract away the DSA — I don't need to know it" | Cloud services wrap DSA but do not change it. DynamoDB scans are still O(n); choosing a hash key still determines O(1) vs O(n) lookup. |
| "Production systems are too complex to map to simple structures" | Every complex system decomposes into a small number of DSA primitives at the hot path. Finding the primitive is the skill. |
| "If it has an API, the implementation doesn't matter" | The implementation determines the cost of every API call. Knowing the structure lets you predict costs without instrumentation. |
| "I only need DSA for interview questions" | Every on-call incident, every capacity planning exercise, and every system design review is a DSA problem in production clothing. |

---

### 🚨 Failure Modes & Diagnosis

**1. Query bypasses the index (full scan instead of O(log n) lookup)**

**Symptom:** A query that was fast at small data volumes becomes catastrophically slow at production volume; EXPLAIN PLAN shows "Seq Scan" instead of "Index Scan."

**Root Cause:** The query predicate does not match the index structure — e.g., applying a function to an indexed column, or using a leading wildcard that breaks prefix ordering.

**Diagnostic:**
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE LOWER(email) = 'user@x.com';
-- If you see Seq Scan: index is bypassed (function applied to indexed col)
-- Fix: create a functional index or rewrite the query
```

**Fix:** Rewrite the query to match the index structure, or create a structure (functional index, search engine) that supports the actual access pattern.

**Prevention:** During query authoring, always EXPLAIN ANALYZE against a production-scale dataset to confirm the index is used.

---

**2. Graph query without depth limit causes memory explosion**

**Symptom:** A "find all connections" query hangs or OOMs; the social graph has unexpected depth.

**Root Cause:** BFS or DFS traversal of a graph without depth limit visits exponentially more nodes as the graph grows. A 6-degree-of-separation traversal on a 1M-node graph can visit millions of nodes.

**Diagnostic:**
```python
# Instrument traversal to count nodes visited
visited_count = 0
def bfs_with_limit(graph, start, max_depth=3):
    global visited_count
    queue = [(start, 0)]
    visited = {start}
    while queue:
        node, depth = queue.pop(0)
        visited_count += 1
        if depth >= max_depth:
            continue
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append((neighbour, depth + 1))
```

**Fix:** Always apply a depth limit (max_depth) or result size limit to graph traversals in production. Use pagination for large result sets.

**Prevention:** Graph queries in production must specify explicit traversal bounds at query design time.

---

**3. Heap used for arbitrary deletion (not supported efficiently)**

**Symptom:** A task scheduler using a priority queue is slow when tasks are cancelled — cancellation causes O(n) scan.

**Root Cause:** Binary heaps support O(log n) insert and O(log n) extract-min, but O(n) arbitrary deletion. Cancellation of arbitrary tasks is not a heap fast path.

**Diagnostic:** If task cancellation is frequent, measure time per cancellation at N=1K, 10K, 100K. Linear growth confirms O(n) scan.

**Fix:** Use a lazy-deletion pattern (mark as cancelled, skip at extraction) or switch to a structure that supports O(log n) arbitrary deletion (Fibonacci heap, or a heap + hash map hybrid).

**Prevention:** Before selecting a heap, confirm all required operations and verify each is in the heap's fast path.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `DSA-001 Why DSA Matter` - the motivation for connecting DSA theory to production practice
- `DSA-002 The Problem of Efficiency` - the formal vocabulary for discussing system performance

**Builds On This (learn these next):**
- `DSA-006 Array` - the most foundational structure, present in every system
- `DSA-010 HashMap` - the single most-used production DSA primitive
- `DSA-019 Graph` - powers social networks, routing, and dependency management

**Alternatives / Comparisons:**
- `DSA-004 How to Think About Problems Algorithmically` - the complementary skill of mapping problems to structures, not just recognising existing mappings

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mapping between DSA theory and the        │
│              │ production systems engineers maintain     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Engineers who can code DSA on whiteboards │
│ SOLVES       │ but cannot diagnose production failures   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every production system is a DSA          │
│              │ structure with a brand name on it         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing production incidents, doing    │
│              │ system design, evaluating new services    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ The abstraction is genuinely opaque and   │
│              │ the vendor SLA covers your use case       │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ "It's a managed service — I don't need    │
│              │ to understand what's running inside"      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Deeper understanding costs learning time  │
│              │ but pays back in every incident response  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The fastest way to fix a system is to    │
│              │ understand what data structure it is."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HashMap → Graph → B-Tree                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Every production system is a DSA primitive behind an API — the primitive determines performance limits.
2. When a system slows down, ask "what is the underlying structure and what operation just became O(n)?"
3. Cloud abstractions hide DSA but do not change it — DynamoDB scans are still O(n).

**Interview one-liner:**
"Production systems are DSA structures with brand names. Recognising the structure behind the abstraction is what lets me predict performance limits and diagnose failures before running a single query."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every abstraction has a hidden cost model determined by its implementation. Ignoring the implementation and trusting only the interface leads to surprises at scale. See through the abstraction to the structure; reason from the structure to the behaviour.

**Where else this pattern appears:**
- Finance: options pricing models are probability tree structures — understanding the tree reveals the assumptions and failure modes of the model
- Operations: a manufacturing assembly line is a pipeline (linked list of stages); a bottleneck in one stage is an O(n) scan in disguise
- Org design: a flat team with open communication is O(n²) communication overhead; a hierarchy introduces O(log n) routing at the cost of information loss

**Industry applications:**
- Database engineering: every decision about index type (B-tree vs hash vs GiST) is a direct DSA trade-off — teams that understand the mapping choose indexes 10x faster than those consulting documentation alone
- On-call engineering at scale: Netflix, Google, and Amazon's SRE teams systematically train engineers to identify the underlying data structure driving each system — it is the single biggest accelerator for incident mean-time-to-resolution

---

### 💡 The Surprising Truth

The internet's DNS system — which resolves billions of domain names per day — is fundamentally a distributed hash map with TTL-based eviction (exactly like an LRU cache). Every DNS lookup you've ever made was an O(1) hash map lookup if cached, or a recursive tree traversal of the DNS hierarchy if not. The engineering that makes billions of websites reachable in milliseconds is not exotic distributed computing — it is a hash map and a tree, operating at planetary scale.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given any production system name (Redis, Elasticsearch, Kafka, PostgreSQL), explain to a junior engineer what DSA primitive powers its primary access pattern and what that implies about performance limits.
2. [DEBUG] Given a latency spike alert on a production system, form a hypothesis about which DSA operation became O(n) and design one diagnostic query or command to confirm or deny it.
3. [DECIDE] During a system design interview, choose the correct backing data structure for each component (cache, queue, index, graph) and justify the choice in terms of the dominant access pattern.
4. [BUILD] Implement a simplified version of an LRU cache using only a hash map and a doubly linked list, demonstrating that both get and put are O(1).
5. [EXTEND] Evaluate a new database or caching system you have never used before by identifying its underlying data structure from its documentation and predicting its performance characteristics for three access patterns.

---

### 🧠 Think About This Before We Continue

**Q1.** Elasticsearch queries on a field with a leading wildcard (`*keyword`) are dramatically slower than suffix queries (`keyword*`). Without reading documentation, explain why, based on the data structure powering Elasticsearch's index.
*Hint: Consider what operation a leading wildcard requires on the inverted index structure and why that operation cannot use the hash key.*

**Q2.** Redis sorted sets support O(log n) range-by-score queries. A team proposes replacing their sorted set with a regular list sorted at insert time to "simplify the code." At what scale does this decision become a production problem, and why?
*Hint: Think about the insert cost of maintaining sorted order in a list vs a skip list, and what happens to both insert and range-query costs as the set grows.*

**Q3.** (TYPE G) Pick any production system you interact with daily (database, cache, message queue, search engine). Using only its documentation, identify the primary data structure powering its main read path. Then: describe one query pattern that will use the fast path (O(1) or O(log n)) and one that will bypass it (O(n)). Verify by running EXPLAIN or a profiling query in a test environment.
*Hint: Most systems expose a query planner or explain utility that shows whether an index is used. The "full scan" label in any planner output is the O(n) signal.*

---

### 🎯 Interview Deep-Dive

**Q1: You're designing the "Who viewed your profile" feature for a social network with 500 million users. What data structure would you use, and why?**
*Why they ask:* Tests whether you can map a product requirement to a DSA choice, considering both access patterns and scale constraints.
*Strong answer includes:*
- Per-user view history: hash map (user_id → list of viewer_ids with timestamps) for O(1) lookup
- For "top viewers in the last 30 days": a sliding window with a sorted structure (priority queue or sorted set) for O(log n) top-K queries
- Storage concern: 500M users × 1000 recent viewers × ~10 bytes = ~5TB — hash map must be distributed (sharded), not in-memory on one machine
- Note write-heavy vs read-heavy ratio: if views are 100x more frequent than reads, the write path (append to list) must be O(1); if reads dominate, a pre-aggregated sorted set makes more sense

**Q2: A cache hit rate drops from 95% to 60% after a deployment. What is your diagnostic process, and which data structures are involved in an LRU cache that could cause this?**
*Why they ask:* Tests practical knowledge of LRU cache internals and the ability to diagnose a caching failure from first principles.
*Strong answer includes:*
- LRU cache = hash map (O(1) key lookup) + doubly linked list (O(1) eviction of least-recently-used)
- A drop in hit rate post-deployment likely means: new code creates new cache keys not previously in cache (cold start), or cache capacity is now too small for the expanded key space
- Diagnostic: check cache key cardinality before and after deployment; check eviction rate (if evictions spiked, cache is too small for the new access pattern)
- Also check for cache key construction bugs: if a cache key includes a timestamp, every request is a miss (key is unique per second)

**Q3: Describe the data structure underlying PostgreSQL's B-tree index and explain why it is preferred over a hash index for most queries in a relational database.**
*Why they ask:* Tests depth of knowledge about real production database internals and the ability to reason about data structure trade-offs in a specific context.
*Strong answer includes:*
- B-tree: a balanced, sorted tree with branching factor B, giving O(log_B N) lookup and range traversal — leaves linked for efficient sequential reads
- Hash index: O(1) exact-match lookup, but cannot support range queries, ordering, or prefix matches
- Relational queries frequently use ORDER BY, BETWEEN, and range predicates — the B-tree's sorted structure makes all of these O(log n) operations
- Hash indexes break on range predicates: `WHERE age BETWEEN 20 AND 30` requires a full scan with a hash index
- PostgreSQL supports both: use hash index only for pure equality predicates on high-cardinality columns where range queries will never be needed
'@

$f = Join-Path $base "DSA-003 - DSA in Real Systems - Where They Appear.md"
[System.IO.File]::WriteAllText($f, $content, [System.Text.UTF8Encoding]::new($false))
$lines = (Get-Content $f -Encoding UTF8).Count
Write-Host "Written: $lines lines -> $f"
$bytes = [IO.File]::ReadAllBytes($f)
Write-Host "BOM check: $($bytes[0]),$($bytes[1]),$($bytes[2])  (must NOT be 239,187,191)"
