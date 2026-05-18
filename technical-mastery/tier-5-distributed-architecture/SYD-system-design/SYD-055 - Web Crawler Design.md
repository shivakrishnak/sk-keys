---
id: SYD-055
title: Web Crawler Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-031
used_by: ""
related: SYD-008, SYD-031, SYD-028, SYD-051
tags:
  - architecture
  - crawler
  - distributed
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/syd/web-crawler-design/
---

⚡ TL;DR - A web crawler systematically browses the
web by: starting with seed URLs, downloading pages,
extracting new links, adding undiscovered links to a
queue, and repeating. Scale challenges: billions of
URLs to crawl, politeness (don't overload servers),
deduplication (don't crawl the same URL twice), and
prioritization (crawl important pages first). Architecture:
URL frontier (priority queue), fetcher workers, parser,
dedup filter (Bloom filter), and content store. Respects
robots.txt and rate-limits per domain.

| #055 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Sharding | |
| **Related:** | Caching, Sharding, Rate Limiting, Search System Design | |

---

### 🔥 The Problem This Solves

Google indexes 30+ trillion web pages. A crawler must
discover and fetch all of them continuously (pages
change, new pages are created daily). Without careful
design:
- Duplicate crawling: same page fetched 100 times
  from different URL representations
- Spider traps: infinite loops from dynamically
  generated URLs (?page=1, ?page=2, ... ?page=∞)
- Server abuse: crawling a single domain at 1,000
  requests/second, causing DoS
- Prioritization: crawling low-quality spam pages
  instead of authoritative content

---

### 📘 Textbook Definition

**Web crawler (spider):** A program that automatically
browses the web, downloading pages and extracting
hyperlinks to discover new pages. Used for building
search engine indexes, monitoring website changes,
and data collection.

**URL frontier:** The set of URLs discovered but not
yet fetched. Typically implemented as a priority queue,
with URLs ordered by importance or freshness.

**Bloom filter:** A probabilistic data structure that
tests whether an element is a member of a set. Answers
"is this URL already seen?" with a small probability
of false positives (reports "seen" when it has not been)
but zero false negatives. Used to deduplicate URLs
without storing every URL individually.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Start with seed URLs → fetch → parse links →
deduplicate → add new to queue → repeat.

**One analogy:**
> A library that wants to catalog every book in the world:
> Start with a few known books. Note down every book
> mentioned in their bibliographies. Find those books,
> note their bibliographies too. Repeat until no new books.
> Track which books you have already cataloged (dedup).
> Be polite: do not demand 1,000 books from the same
> publisher at once.

**One insight:**
The two hardest problems in web crawling at scale are:
1. Deduplication: billions of URLs, many of which are
   equivalent (with/without www, different query parameter
   orders). A Bloom filter provides O(1) lookup without
   storing every URL.
2. Politeness: if you crawl 1 page per second per domain,
   and have 100M domains, you need 100M crawler threads.
   Group URLs by domain in the frontier; use per-domain
   rate limiting.

---

### 🔩 First Principles Explanation

**CRAWLER ARCHITECTURE:**
```
Seed URLs
    │
    ▼
URL Frontier (Priority Queue)
    │   ▲ (new URLs extracted from pages)
    │   │
    ▼   │
Fetcher Workers (distributed)
    │
    ▼
DNS Cache + robots.txt Cache
    │
    ▼
HTTP Request to Target Server
    │
    ▼
Raw Page Content
    │
    ├──► Content Store (S3/HDFS)
    │    [save raw HTML + metadata]
    │
    └──► Link Extractor + Parser
         │
         ▼
         URL Normalizer
         │
         ▼
         Bloom Filter (dedup check)
         │
         ▼
         If new URL: add to URL Frontier
```

**URL FRONTIER DESIGN:**
```
Simple queue: FIFO - crawl in order found.
Problem: if many URLs from the same domain
  are discovered, they all queue together.
  Crawling 100 pages/second from one domain
  = effectively a DoS attack.

Better: per-domain queues + politeness enforcer.
  One queue per domain.
  Selector picks URLs from different domain queues
  in round-robin (or priority-weighted) fashion.
  Per-domain delay: min 1 second between requests.
  
  Priority: PageRank, freshness, update frequency.
  High-priority domains (news sites): frequent re-crawl.
  Low-priority (static pages): re-crawl weekly or monthly.

Implementation:
  Priority queue: "which domain should be fetched next?"
  Domain buckets: queue of URLs per domain
  
  Structure:
    priority_queue: [(priority, domain)]
    domain_queues: {domain: [url1, url2, ...]}
    domain_delay: {domain: next_allowed_fetch_time}
```

**DEDUPLICATION:**
```
URL normalization (before dedup check):
  - Lowercase scheme and host: HTTP://Example.com →
    http://example.com
  - Remove trailing slash: /page/ → /page
  - Sort query parameters: ?b=2&a=1 → ?a=1&b=2
  - Remove fragment: /page#section → /page
  - Remove default ports: :80 → (nothing)
  
After normalization, check:
  1. Bloom filter: "Have we seen this URL?"
     False positive rate: ~1% (tolerable - skip 1% of
     new pages; never re-crawl already-seen pages).
     Memory: 1 billion URLs × ~10 bits/URL = 1.25GB
  
  2. Exact dedup (for content): fingerprint of page content
     (SimHash or MD5). If content matches a known page:
     different URL, same content. Skip indexing.
```

**ROBOTS.TXT:**
```
Crawlers MUST respect robots.txt.
  https://example.com/robots.txt
  
  User-agent: *
  Disallow: /private/
  Crawl-delay: 2
  
Before crawling any URL from a domain:
  Fetch robots.txt (once per domain, cache for 24 hours).
  Check if the URL path matches any Disallow rule.
  Respect Crawl-delay directive.
  
Violating robots.txt: legal/ethical risk.
Many sites block IP ranges that violate robots.txt.
```

---

### 🧪 Thought Experiment

**SIZING: Google-scale web crawler**

Goal: crawl 15 billion URLs in 30 days.
Rate: 15B / (30 × 86,400) = 5,787 URLs/second.
Peak (accounting for failures, retries): ~10,000 URLs/sec.

**Fetchers:**
Each fetcher: limited by network I/O (HTTP round-trip).
Average page fetch: 200ms (including DNS lookup).
1 fetcher thread: 5 fetches/second.
For 10,000 fetches/second: 2,000 fetcher threads.
At 100 threads/server: 20 servers for fetching.

**Storage:**
Average page size: 100KB HTML.
15B pages × 100KB = 1.5PB raw HTML.
Compressed (~5x): 300TB. Stored in HDFS/S3.

**URL frontier:**
15B URLs × 50 bytes/URL = 750GB.
Too large for in-memory queue. Use disk-backed queue
(Apache Kafka or a B-tree on SSD).
Hot frontier (top priority URLs): Redis (in-memory),
~10M URLs × 50 bytes = 500MB.

**Bloom filter:**
15B URLs × 10 bits = 150 billion bits = ~18GB.
Fits in RAM on one server (64GB server).
Replicate for availability.

---

### 🧠 Mental Model / Analogy

> A web crawler is like an explorer charting an unknown map:
>
> Start with a few known landmarks (seed URLs).
> From each landmark, note all roads leading away (links).
> Add all unexplored roads to your exploration queue.
> Visit each road in order of importance (priority queue).
> Before visiting a road, check your notes: have I been
> here before? (Bloom filter dedup).
> Be polite: do not revisit the same neighborhood
> 10 times in a row - spread out your exploration
> (per-domain rate limiting).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A web crawler reads web pages and follows links to
discover new pages, over and over. This is how search
engines discover all the pages on the internet and keep
their index up to date.

**Level 2 - How to use it (junior developer):**
Start with seed URLs. Fetch each URL. Parse HTML for
links. Add new links to a queue. Repeat. Store seen
URLs to avoid fetching the same page twice. Respect
robots.txt.

**Level 3 - How it works (mid-level engineer):**
Distributed fetcher workers pull URLs from a priority
queue (URL frontier). Normalize URLs before adding to
frontier. Use a Bloom filter for O(1) dedup check.
Per-domain queues with politeness delays. Store content
in S3/HDFS. Parse links in a separate worker. Re-crawl
schedule: high-frequency for news (daily), low-frequency
for static content (monthly).

**Level 4 - Why it was designed this way (senior/staff):**
The Bloom filter is the right tool for URL dedup because
it is space-efficient (10 bits per URL regardless of URL
length) and O(1) for both insert and lookup. The 1% false
positive rate is acceptable: it causes 1% of new URLs to
be mistakenly treated as already-seen (skipped). The
alternative (a hash set) stores the full URL and requires
orders of magnitude more memory. The per-domain queue
architecture is critical: without it, a crawler can
inadvertently DoS a server by queuing thousands of its
pages at the front of the queue. Domain-level throttling
spreads load evenly across the web.

**Level 5 - Mastery (distinguished engineer):**
Google's crawler architecture is Caffeine (2010+): a
continuous streaming pipeline that updates the index
in near-real-time instead of batch processing. Fresh
content (news, live scores) is re-crawled within seconds
via a priority system that detects content change
frequency. The "fetch rate budget" per site is negotiated:
sites with fresh, high-quality content get a higher
crawl budget (fetched more frequently). Sites with
little new content get a low budget. PageRank and
historical change frequency both influence the budget.
The crawler also handles: JavaScript execution (dynamic
content loaded by React/Angular requires a headless
browser - Chromium - to render), mobile vs desktop
crawling (separate user agents, Google uses mobile-first
indexing), and international character sets (normalize
IDN domains to punycode).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ DISTRIBUTED WEB CRAWLER                             │
│                                                      │
│ URL Frontier (Priority Queue):                      │
│  High priority: news, frequently-updated pages     │
│  Low priority: static, infrequently-updated pages  │
│                                                      │
│ Fetcher Worker (20 servers, 100 threads each):      │
│  1. Get next URL from frontier (priority-weighted)  │
│  2. Check domain delay (politeness)                 │
│  3. Fetch robots.txt (cached 24h)                  │
│  4. If disallowed: skip URL                        │
│  5. Fetch URL (HTTP GET with crawler user-agent)   │
│  6. On 200: store HTML in S3                       │
│  7. Update crawl status in metadata DB             │
│                                                      │
│ Parser Worker:                                      │
│  1. Read raw HTML from S3                          │
│  2. Extract all href links                         │
│  3. Normalize each URL                             │
│  4. Check Bloom filter                             │
│  5. If new: add to URL frontier + Bloom filter     │
│  6. Extract text for search index                  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Crawler with Bloom filter and robots.txt**
```python
import hashlib
import time
import urllib.robotparser
from collections import defaultdict
from urllib.parse import urlparse, urljoin, urlunparse
import requests
from bs4 import BeautifulSoup

class BloomFilter:
    """Simplified Bloom filter for URL dedup."""
    def __init__(self, capacity: int, error_rate: float = 0.01):
        import math
        self.size = int(
            -capacity * math.log(error_rate) / (math.log(2)**2))
        self.num_hashes = max(1, int(
            (self.size / capacity) * math.log(2)))
        self.bits = bytearray(self.size // 8 + 1)

    def _positions(self, item: str):
        for seed in range(self.num_hashes):
            h = int(hashlib.md5(
                f"{seed}{item}".encode()).hexdigest(), 16)
            yield h % self.size

    def add(self, item: str):
        for pos in self._positions(item):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item: str) -> bool:
        return all(
            self.bits[pos // 8] & (1 << (pos % 8))
            for pos in self._positions(item)
        )

def normalize_url(url: str, base: str = None) -> str:
    """Normalize URL for deduplication."""
    if base:
        url = urljoin(base, url)
    parsed = urlparse(url.lower())
    # Remove fragment, normalize path
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip("/") or "/",
        "",
        "&".join(sorted(
            parsed.query.split("&")
        )) if parsed.query else "",
        ""  # Remove fragment
    ))
    return normalized

class WebCrawler:
    def __init__(self, seed_urls: list):
        self.frontier = list(seed_urls)
        self.seen = BloomFilter(capacity=10_000_000)
        self.robots_cache = {}  # domain → RobotFileParser
        self.domain_delay = defaultdict(float)
        # domain → next_allowed_time
        self.DELAY_SECONDS = 1.0

    def is_allowed(self, url: str) -> bool:
        """Check robots.txt before fetching."""
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain not in self.robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            try:
                rp.set_url(robots_url)
                rp.read()
            except Exception:
                rp = None
            self.robots_cache[domain] = rp
        rp = self.robots_cache[domain]
        if rp:
            return rp.can_fetch("MyCrawler/1.0", url)
        return True

    def crawl(self, max_pages: int = 100):
        """Main crawl loop."""
        pages_fetched = 0
        while self.frontier and pages_fetched < max_pages:
            url = self.frontier.pop(0)
            norm_url = normalize_url(url)

            if norm_url in self.seen:
                continue  # Already crawled
            if not self.is_allowed(url):
                continue  # robots.txt disallows

            # Politeness: enforce per-domain delay
            domain = urlparse(url).netloc
            wait = self.domain_delay[domain] - time.time()
            if wait > 0:
                time.sleep(wait)

            # Fetch page
            try:
                resp = requests.get(
                    url, timeout=10,
                    headers={"User-Agent": "MyCrawler/1.0"})
                resp.raise_for_status()
            except Exception:
                continue

            self.seen.add(norm_url)
            self.domain_delay[domain] = (
                time.time() + self.DELAY_SECONDS)
            pages_fetched += 1

            # Parse links
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup.find_all("a", href=True):
                new_url = normalize_url(
                    tag["href"], base=url)
                if new_url not in self.seen:
                    self.frontier.append(new_url)

        return pages_fetched
```

**Example 2 - Crawl without dedup (BAD)**
```python
# BAD: No URL deduplication or robots.txt
def crawl_bad(seed_url: str):
    import requests
    from bs4 import BeautifulSoup

    to_crawl = [seed_url]
    while to_crawl:
        url = to_crawl.pop()
        # No dedup: same URL can appear 1000 times
        # No robots.txt: may crawl disallowed paths
        # No rate limit: crawls target at full speed
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            to_crawl.append(tag["href"])
    # Result: infinite loop (pages link to each other),
    # massive DoS to target servers, potentially illegal.

# GOOD: Bloom filter dedup + robots.txt + per-domain delay
# (shown in WebCrawler class above)
```

---

### ⚖️ Comparison Table

| Component | Simple Approach | Production Approach |
|---|---|---|
| Deduplication | Set of visited URLs (memory) | Bloom filter (10 bits/URL) + exact content hash |
| URL queue | Python list | Priority queue + per-domain bucket queues |
| Rate limiting | None | Per-domain delay (1 req/sec default) |
| robots.txt | None | Fetch + parse + cache per domain (24h TTL) |
| Content storage | Local disk | S3/HDFS with metadata in a database |
| Scale | Single machine | Distributed (20+ fetcher workers) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A Bloom filter guarantees no duplicate crawls | Bloom filters have a false positive rate (typically ~1%). Some new URLs will be incorrectly treated as "already seen" and skipped. This is an acceptable trade-off for the 1,000x memory savings over a hash set. False negatives (treating a seen URL as new) are not possible with Bloom filters. |
| All pages should be re-crawled at the same frequency | Pages have very different update frequencies. News articles may update hourly; Wikipedia articles monthly; static documentation rarely. An intelligent re-crawl scheduler uses historical change frequency to set crawl priority. Crawling a static page daily wastes resources; crawling news hourly is necessary for freshness. |
| JavaScript-rendered content is automatically crawled | Early web crawlers (and many simple ones) only parse static HTML. Single-page applications (React, Angular, Vue) render content via JavaScript - the raw HTML is a near-empty shell. To crawl these, the crawler must execute JavaScript (headless browser like Chromium). This is 5-10x more expensive per page than static HTML parsing. |

---

### 🚨 Failure Modes & Diagnosis

**Spider Trap (Infinite URL Space)**

**Symptom:**
Crawler discovers a domain that generates infinite
URLs: `/calendar/2025-01-01`, `/calendar/2025-01-02`,
..., `/calendar/9999-12-31`. The frontier grows without
bound. Memory exhausted. Crawler stalls.

**Root Cause:**
Dynamically-generated URLs with no natural termination
(date ranges, paginated content, session tokens). The
crawler keeps adding new URLs and never exhausts them.

**Fix - URL depth limit + pattern detection:**
```python
MAX_PATH_DEPTH = 5  # Max URL path depth
MAX_QUERY_PARAMS = 3  # Max query parameters in URL

def is_spider_trap(url: str) -> bool:
    """Detect common spider trap patterns."""
    parsed = urlparse(url)
    path_depth = len([p for p in parsed.path.split("/")
                      if p])
    if path_depth > MAX_PATH_DEPTH:
        return True

    # Too many query params = likely dynamic/session URL
    query_params = len(parsed.query.split("&")) if parsed.query else 0
    if query_params > MAX_QUERY_PARAMS:
        return True

    # Detect repeated path segments (infinite nesting)
    parts = [p for p in parsed.path.split("/") if p]
    if len(set(parts)) < len(parts) * 0.7:
        # More than 30% repeated: likely a trap
        return True

    return False

# Also: limit total pages crawled per domain per day
# Aggressive crawling = possible ban from the domain
MAX_PAGES_PER_DOMAIN = 10_000  # per day
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - DNS cache, robots.txt cache per domain;
  crucial for crawl performance
- `Sharding` - URL frontier sharded by domain hash
  for parallel processing

**Builds On This (learn these next):**
- `Rate Limiting (System)` - per-domain rate limiting
  is the same as the general rate limiting pattern
- `Search System Design` - crawler feeds the indexer
  in a search engine pipeline

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEDUP       │ Bloom filter: ~10 bits/URL. O(1) check.  │
│             │ 15B URLs = 18GB. Acceptable FP rate 1%.  │
├─────────────┼──────────────────────────────────────────┤
  │
│ POLITENESS  │ 1 req/sec per domain (default).          │
│             │ Per-domain delay queue. Respect Crawl-   │
│             │ delay in robots.txt.                     │
├─────────────┼──────────────────────────────────────────┤
  │
│ ROBOTS.TXT  │ Fetch once per domain, cache 24h.        │
│             │ Check before EVERY request to that domain│
├─────────────┼──────────────────────────────────────────┤
  │
│ FRONTIER    │ Priority queue (PageRank/freshness).     │
│             │ Per-domain buckets for politeness.       │
├─────────────┼──────────────────────────────────────────┤
  │
│ SPIDER TRAP │ Max depth limit + max query params.      │
│             │ Max pages per domain per day.            │
├─────────────┼──────────────────────────────────────────┤
  │
│ NORMALIZE   │ Lowercase, sort params, remove fragment, │
│             │ remove trailing slash before dedup.      │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Frontier → fetch → parse → normalize  │
│             │  → Bloom dedup → add new → repeat"     │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ API Gateway Design → Event-Driven Arch   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Bloom filter for deduplication: ~10 bits per URL
   (15B URLs = 18GB), O(1) lookup, 1% false positive
   rate is acceptable (skip a few new URLs, never
   recrawl a seen URL). Far more memory-efficient
   than storing all URLs in a hash set.
2. Per-domain rate limiting (politeness): group URLs
   by domain in the frontier. Enforce a minimum delay
   (1 second) between requests to the same domain.
   Violating this causes target servers to ban the
   crawler and constitutes a DoS attack.
3. Spider traps: impose depth limits (max 5 path
   levels), maximum query parameters, and maximum
   pages per domain per day. These prevent the frontier
   from growing unboundedly from dynamically-generated
   URL spaces.

**Interview one-liner:**
"Web crawler: start with seed URLs, fetch, parse links, normalize (lowercase,
sort query params, remove fragments), check Bloom filter (10 bits/URL, O(1)
dedup, 1% FP rate) → if new: add to URL frontier. URL frontier: priority queue
(PageRank + freshness) with per-domain buckets for politeness (1 req/sec per
domain, respect robots.txt Crawl-delay). Fetchers: distributed workers with
domain delay enforcement. Spider trap prevention: max path depth (5), max query
params (3), max pages per domain per day. Content stored in S3/HDFS."
