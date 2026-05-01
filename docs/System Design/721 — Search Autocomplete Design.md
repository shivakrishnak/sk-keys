---
layout: default
title: "Search Autocomplete Design"
parent: "System Design"
nav_order: 721
permalink: /system-design/search-autocomplete-design/
number: "721"
category: System Design
difficulty: ★★★
depends_on: "Caching, Trie Data Structure, Rate Limiting (System)"
used_by: "System Design Interview"
tags: #advanced, #system-design, #interview, #search, #trie
---

# 721 — Search Autocomplete Design

`#advanced` `#system-design` `#interview` `#search` `#trie`

⚡ TL;DR — **Search Autocomplete** serves top-K query suggestions for any prefix using a Trie (offline) + Redis sorted sets (online) + CDN caching, returning results in under 100ms for billions of daily prefix queries.

| #721 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Trie Data Structure, Rate Limiting (System) | |
| **Used by:** | System Design Interview | |

---

### 📘 Textbook Definition

**Search Autocomplete** (also called typeahead or query suggestion) is a feature that provides a ranked list of the top-K (typically 5–10) most relevant search query completions for any prefix the user has typed so far. The system must return results with very low latency (< 100ms to avoid disrupting typing flow) and handle extremely high QPS (every keystroke from every active user generates a request). The core data structure is a **Trie** (prefix tree), where each node represents a character prefix and stores the top-K most frequent completions for that prefix. In production, the raw Trie is pre-computed offline (batch job from search query logs) and served via Redis sorted sets (prefix → top-K completions with frequency scores), with aggressive CDN and in-memory caching for common prefixes. The data freshness cadence (how often the top-K list is updated) balances recency with computational cost.

---

### 🟢 Simple Definition (Easy)

Search Autocomplete: as you type "iphon" in Google's search box, it instantly shows "iphone 15", "iphone 14 review", "iphone price" — before you finish typing. For every 1-2 characters you type, a request goes to a server that looks up: "what are the most common searches that start with 'iphon'?" The answers are precomputed and cached so the response comes back in under 100 milliseconds.

---

### 🔵 Simple Definition (Elaborated)

Google processes 8.5 billion searches per day. Each search involves many keystrokes, each keystroke = one autocomplete request. Total: ~50 billion autocomplete requests per day. The system can't compute "top-10 suggestions for prefix 'iphon'" by scanning all search logs for every request — too slow. Instead: a nightly batch job scans all search logs, builds a Trie with frequency counts, and stores "top-10 completions per prefix" in Redis. Request for "iphon": Redis lookup in <1ms. CDN caches the result at the edge (most "iphon" users are asking the same question). Response: 10ms total.

---

### 🔩 First Principles Explanation

**Autocomplete architecture: Trie design, Redis serving, freshness pipeline:**

```
TRIE DATA STRUCTURE:

  Trie for search suggestions:
  
  Searches (frequency):
    "iphone" (10M)
    "iphone 15" (8M)
    "iphone 14" (5M)
    "ipad" (3M)
    "internet explorer" (1M)
  
  Trie structure:
  
       root
       /  \
      i    ...
      |
      p
     / \
    h   a
    |   |
    o   d → ["ipad": 3M]
    |
    n
    |
    e → ["iphone": 10M, "iphone 15": 8M, "iphone 14": 5M]
     \
      " " → space
       |
       1
      / \
     4   5 → ["iphone 15": 8M]
     |
     → ["iphone 14": 5M]
  
  Each node: stores top-K completions for its prefix.
  Query for "ip": start at root, traverse i→p, read top-K from node p.
  Result: "iphone": 10M, "iphone 15": 8M, "iphone 14": 5M, "ipad": 3M (top 4)

OFFLINE TRIE BUILDING (batch pipeline):

  Every 24 hours:
  
  1. Aggregate search logs (Kafka → Spark):
     Input: raw search events (user_id, query, timestamp)
     Aggregation: count frequency of each normalized query
     Output: (query, frequency) pairs
     
     Normalization:
       Lowercase: "IPhone 15" → "iphone 15"
       Trim: "iphone  15" → "iphone 15"
       Remove special chars: "iphone-15" → "iphone 15"
     
  2. Build Trie:
     For each (query, frequency) sorted by frequency desc:
       Insert into Trie.
       At each prefix node: update top-K if this query's frequency > current min.
     
  3. Serialize Trie to file → upload to S3
  
  4. Push update to Redis:
     For each prefix node in Trie:
       key = "ac:" + prefix
       value = sorted list of (query, frequency) — top K only
       
     // Redis Sorted Set: score=frequency, member=query
     ZADD ac:ip 10000000 "iphone"
     ZADD ac:ip 8000000 "iphone 15"
     ZADD ac:ip 5000000 "iphone 14"
     ZADD ac:ip 3000000 "ipad"
     
  5. TTL: keys expire after 25 hours (next batch updates them)

ONLINE SERVING:

  Client: types "iphon" → sends GET /autocomplete?prefix=iphon
  
  API Server:
  1. Validate and normalize prefix: lowercase, trim, max 25 chars
  2. Rate limit: 10 requests/second per user (prevent bot scraping)
  3. Check CDN cache (prefix in CDN cache? → return immediately)
  4. Check local in-memory cache (last 10,000 prefixes, LRU eviction)
  5. Query Redis: ZREVRANGEBYSCORE ac:iphon +inf -inf LIMIT 0 10
  6. Return top-10 results as JSON
  7. Populate local cache + CDN cache
  
  Redis query:
    ZREVRANGEBYSCORE ac:iphon +inf -inf WITHSCORES LIMIT 0 10
    → ["iphone 15": 8000000, "iphone": 10000000, ...]
    
  Response time:
    CDN hit: < 5ms (served from edge PoP)
    Redis hit: < 20ms (Redis lookup + serialization)
    Redis miss (cold prefix): < 50ms (populate cache)

FRESHNESS vs PERFORMANCE TRADE-OFF:

  Real-time update (expensive):
    Every search → increment counter in Redis for that query's prefix nodes.
    Problem: "iphone 15" → update nodes: "i", "ip", "iph", "ipho", "iphon", "iphone", ...
    Each query = O(len(query)) Redis writes × 10 keystrokes avg = 100+ writes/query
    At 8.5B searches/day = 850B Redis writes/day → too expensive
    
  Batch update (daily):
    Stale by 24 hours. "Breaking news" search term won't appear until next day.
    For most use cases: acceptable. Google recomputes hourly.
    
  Near-real-time (compromise):
    Streaming pipeline (Kafka → Flink): compute top-K per prefix every 15 minutes.
    Update only changed prefix nodes (not full Trie rebuild).
    Cost: much less than real-time, freshness: 15 minutes.
    
    "Breaking news" appears in suggestions within 15 minutes → acceptable for most uses.

SCALE ESTIMATION:

  10 keywords typed per second per active user.
  100M active users during peak hour.
  QPS: 100M × 10 = 1 billion requests/second at peak!
  
  CDN absorbs 90%: 100M requests/second to origin.
  
  Redis cluster sizing:
    Total unique prefixes: 10M unique queries × avg 7 chars/query = 70M unique prefix nodes
    Storage per node: 10 suggestions × 50 bytes = 500 bytes
    Total: 70M × 500 bytes = 35 GB Redis → 5 Redis nodes × 8 GB = feasible
    
  API server fleet:
    100M req/sec. Each server: 10K req/sec.
    Fleet: 10,000 servers. (CDN reduces to manageable level)
    
  REALISTIC scale with CDN:
    CDN hit rate: 95% (common prefixes cached globally)
    Origin QPS: 100M × 5% = 5M req/sec → 500 servers at 10K req/sec each.

MULTI-LANGUAGE / UNICODE SUPPORT:

  Trie character set: not just a-z.
  Chinese (Mandarin): 70,000 characters → Trie needs Unicode nodes.
  Solution: store prefix as UTF-8 string key in Redis (not character array).
  
  Redis key: "ac:" + utf8_prefix
  Works natively for any Unicode prefix.
  
  Separate Trie per language (or per regional cluster):
    ac:en:ip, ac:zh:手机, ac:es:iph → language-specific suggestions

PERSONALIZED AUTOCOMPLETE:

  Global suggestions: "iphone 15" (everyone searches this)
  Personalized suggestions: append user's recent searches to global list
  
  Implementation:
    Global: ZREVRANGE ac:ip 0 7          // top 8 global suggestions
    Personal: ZREVRANGE ac:personal:{user_id}:ip 0 1  // top 2 personal
    Merge: deduplicate, personal first, then global to fill to 10
    
  Personal Trie: built from user's last 90 days of search history.
  Stored per-user: too expensive for all users. Build only for active users (daily active).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Search Autocomplete architecture:
- Naive: scan all search logs for every prefix query → minutes per query
- Simple DB LIKE query: `SELECT query FROM queries WHERE query LIKE 'iphon%'` → full scan, no top-K ordering

WITH Search Autocomplete architecture:
→ Pre-computed Trie + Redis: prefix lookup in < 1ms
→ CDN caching: 95% of requests served at edge, < 5ms globally
→ Batch + streaming pipeline: balance freshness vs computational cost

---

### 🧠 Mental Model / Analogy

> A library's card catalog system with a twist: behind each alphabetical tab (prefix), there's a pre-sorted list of the 10 most-borrowed books starting with that prefix. Librarian lookup: open tab "IPH" → immediately see top 10 books. The list is updated nightly by a batch job that counts all book borrowings. The most popular tabs are laminated (cached at CDN edge). The librarian doesn't search the entire catalog — they read from the pre-sorted card at that tab.

"Alphabetical tab" = Trie prefix node (each unique prefix has a node)
"Pre-sorted list of top 10 books" = top-K completions stored at each prefix node
"Updated nightly" = batch job that rebuilds Trie from search log frequencies
"Laminated tabs" = CDN cache for popular prefixes (served at edge, no server hit)
"Entire catalog search" = naive LIKE query (too slow — O(N) instead of O(prefix_length))

---

### ⚙️ How It Works (Mechanism)

**Trie node with top-K completions in Java:**

```java
public class AutocompleteTrieNode {
    
    private final Map<Character, AutocompleteTrieNode> children = new HashMap<>();
    // Top-K completions for this prefix (sorted by frequency desc):
    private final PriorityQueue<QuerySuggestion> topK;
    private final int K;
    
    public AutocompleteTrieNode(int k) {
        this.K = k;
        // Min-heap: evict the lowest-frequency item when K is exceeded
        this.topK = new PriorityQueue<>(Comparator.comparingLong(QuerySuggestion::frequency));
    }
    
    public void updateTopK(String query, long frequency) {
        // Remove if already present (update frequency):
        topK.removeIf(s -> s.query().equals(query));
        
        topK.offer(new QuerySuggestion(query, frequency));
        
        // Keep only top-K:
        if (topK.size() > K) {
            topK.poll();  // remove lowest frequency
        }
    }
    
    public List<QuerySuggestion> getTopK() {
        return topK.stream()
            .sorted(Comparator.comparingLong(QuerySuggestion::frequency).reversed())
            .collect(Collectors.toList());
    }
    
    public AutocompleteTrieNode getOrCreateChild(char c) {
        return children.computeIfAbsent(c, k -> new AutocompleteTrieNode(K));
    }
    
    public AutocompleteTrieNode getChild(char c) {
        return children.get(c);
    }
}

record QuerySuggestion(String query, long frequency) {}

public class AutocompleteTrie {
    
    private final AutocompleteTrieNode root;
    private final int K;
    
    public AutocompleteTrie(int k) {
        this.K = k;
        this.root = new AutocompleteTrieNode(k);
    }
    
    public void insert(String query, long frequency) {
        AutocompleteTrieNode node = root;
        // Update top-K for root (all prefixes):
        node.updateTopK(query, frequency);
        
        for (char c : query.toCharArray()) {
            node = node.getOrCreateChild(c);
            // Update top-K at every prefix node:
            node.updateTopK(query, frequency);
        }
    }
    
    public List<QuerySuggestion> getSuggestions(String prefix) {
        AutocompleteTrieNode node = root;
        for (char c : prefix.toCharArray()) {
            node = node.getChild(c);
            if (node == null) return Collections.emptyList();  // prefix not found
        }
        return node.getTopK();
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
User types characters (search prefix)
        │
        ▼
Search Autocomplete Design ◄──── (you are here)
(Trie + Redis + CDN + batch pipeline)
        │
        ├── Trie Data Structure (prefix tree for O(prefix_len) lookup)
        ├── Caching (Redis for pre-computed top-K, CDN for common prefixes)
        └── Batch Processing (offline Trie rebuild from search logs)
```

---

### 💻 Code Example

**Redis-based autocomplete serving (Spring Boot):**

```java
@RestController
@RequestMapping("/autocomplete")
public class AutocompleteController {
    
    @Autowired private RedisTemplate<String, String> redis;
    @Autowired private SlidingWindowRateLimiter rateLimiter;
    
    private static final int MAX_PREFIX_LENGTH = 25;
    private static final int NUM_SUGGESTIONS = 10;
    
    @GetMapping
    public ResponseEntity<List<String>> autocomplete(
            @RequestParam String prefix,
            HttpServletRequest request) {
        
        // 1. Rate limiting: 10 requests/sec per IP
        String clientIp = request.getRemoteAddr();
        if (!rateLimiter.check("autocomplete:" + clientIp, 10).isAllowed()) {
            return ResponseEntity.status(429).build();
        }
        
        // 2. Normalize prefix:
        prefix = prefix.toLowerCase().trim();
        if (prefix.isEmpty() || prefix.length() > MAX_PREFIX_LENGTH) {
            return ResponseEntity.ok(Collections.emptyList());
        }
        
        // 3. Query Redis sorted set:
        String key = "ac:" + prefix;
        Set<String> results = redis.opsForZSet()
            .reverseRange(key, 0, NUM_SUGGESTIONS - 1);
        
        if (results == null || results.isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }
        
        // 4. Set cache headers (CDN can cache this response):
        return ResponseEntity.ok()
            .cacheControl(CacheControl.maxAge(300, TimeUnit.SECONDS)  // 5 min CDN cache
                         .cachePublic())
            .body(new ArrayList<>(results));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Trie lookups are O(1) like a hash map | Trie lookup is O(L) where L is the length of the prefix string. In practice: L ≤ 25 characters for autocomplete → fast, but not O(1). Hash map lookup for the same key would also be O(L) due to hash computation on the string. For autocomplete, the Trie's advantage over a hash map is that all keys with the same prefix are co-located in the Trie (prefix traversal finds all completions), while a hash map has no structural relationship between similar keys |
| The Trie must be stored in application memory | In production, the Trie's output (prefix → top-K completions) is stored in Redis sorted sets. Application servers don't hold the full Trie in memory. Redis cluster holds all prefix→top-K mappings. Application servers are stateless and simply query Redis. The in-memory Trie is only used in the offline batch job that builds the data structure and writes to Redis |
| Real-time freshness is required for autocomplete | For most use cases (product search, location search, general web search), hourly or daily updates are sufficient. "Breaking news" may need 15-minute updates for news-related queries. True real-time updates (per-search-event update) are rarely justified: the performance cost (O(query_length) writes per search) overwhelms the benefit (queries are only "new" once; after a few minutes, the batch pipeline catches up) |
| Autocomplete and search are the same problem | Autocomplete is prefix matching with frequency ranking — only searches that START with the prefix are returned. Full-text search (Elasticsearch, Lucene) matches any word in any order. A search for "iPhone buy" should return "buy iPhone" in full-text search but NOT in autocomplete (prefix mismatch). Autocomplete requires a Trie or prefix index; full-text search requires an inverted index |

---

### 🔥 Pitfalls in Production

**Offensive / inappropriate autocomplete suggestions:**

```
PROBLEM: Raw search frequency data includes offensive queries

  Search logs (raw frequency):
    "how to make a bomb" → 50,000 searches (curiosity, research, news context)
    Autocomplete prefix "how to make a": suggests "how to make a bomb" (top result)
    
  This is a LEGAL and REPUTATIONAL risk.
  Google, Bing, YouTube all filter autocomplete suggestions.

BAD: Serving raw frequency data without filtering:
  User types "how to make a" → autocomplete shows "how to make a bomb"
  Headlines: "SearchEngine autocompletes to terrorist instructions"
  
FIX 1: BLOCKLIST FILTERING:
  Maintain a blocklist of exact phrases and regex patterns:
    BLOCKLIST = {"bomb making", "how to make weapons", ...}
    
  During batch Trie building:
    For each (query, frequency) pair:
      if any blocklist pattern matches query:
        skip this query (don't insert into Trie)
        
  Blocklist maintained by: Trust & Safety team, automated ML classifier, legal team.
  
FIX 2: SAFE SEARCH CATEGORIES:
  Classifier: each query → "safe", "adult", "violence" category.
  Default autocomplete: only "safe" queries.
  Users with explicit content enabled: "safe" + "adult" queries.
  Never show: "violence", "illegal" categories.
  
FIX 3: MINIMUM FREQUENCY THRESHOLD:
  Don't suggest queries searched fewer than 10,000 times.
  Very specific attack/offensive queries: rare → below threshold.
  
FIX 4: REAL-TIME BLOCKLIST CACHE:
  Emergency blocking: if offensive query goes viral (news event):
  Don't wait for next batch cycle (24 hours).
  Maintain a real-time Redis blocklist set:
    SADD blocklist "offensive query"
    Check during serving: if SISMEMBER blocklist result → filter out
  Propagates to all servers in seconds.
```

---

### 🔗 Related Keywords

- `Trie Data Structure` — prefix tree enabling O(prefix_length) lookup of all completions
- `Caching` — Redis stores pre-computed top-K per prefix; CDN caches responses at edge
- `Rate Limiting (System)` — prevents bot scraping of autocomplete API (one request per keystroke)
- `Batch Processing` — offline Spark/Flink job rebuilds Trie from search log aggregates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Pre-compute top-K per prefix in Trie;     │
│              │ serve from Redis + CDN in <20ms           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Search suggestions; typeahead; product    │
│              │ search; location search                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Real-time per-search Trie updates;        │
│              │ serving raw frequency data without filter │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Card catalog with pre-sorted top-10 per  │
│              │  tab — laminated tabs served at CDN edge."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Trie Data Structure → Redis Sorted Sets   │
│              │ → Search System Design                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the autocomplete data freshness pipeline for a trending social media platform where new hashtags can go from 0 to 1 million searches in under 30 minutes (e.g., a celebrity scandal breaks). The daily batch pipeline takes 6 hours to rebuild. Describe a streaming/near-real-time pipeline that can reflect trending queries in autocomplete within 5 minutes. What is your data flow (search event → Kafka → ? → Redis)? What is the trade-off between a full Trie rebuild and an incremental update?

**Q2.** A multi-language e-commerce site needs autocomplete for: English product names, Chinese product names (thousands of unique characters), and product SKUs (alphanumeric codes like "B07XJ8C8F5"). Design the Redis key schema and Trie structure for each language/type. How do you handle a user typing a prefix that could match both English and Chinese? How does CDN caching work when the same URL path `/autocomplete?prefix=ip` should return different results for English and Chinese users?
