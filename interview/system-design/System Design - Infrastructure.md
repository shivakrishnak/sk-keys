---
layout: default
title: "System Design - Infrastructure"
parent: "System Design"
grand_parent: "Interview Mastery"
nav_order: 6
permalink: /interview/system-design/infrastructure/
topic: System Design
subtopic: Infrastructure
keywords:
  - Load Balancing
  - CDN
  - Leader Election
  - Bloom Filters
difficulty_range: mixed
status: complete
version: 1
---

# Load Balancing

**TL;DR** - Load balancing distributes incoming traffic across multiple servers to prevent any single server from becoming a bottleneck, improving availability, throughput, and fault tolerance.

---

### The Problem This Solves

**WORLD WITHOUT LOAD BALANCING:**
One server handles all traffic. At 1000 requests/second it's fine. At 10,000 requests/second, it maxes out CPU, starts queuing requests, response times spike from 50ms to 5 seconds, and eventually crashes. You can't scale by making one server infinitely powerful (vertical scaling has limits).

---

### How It Works

```
WITHOUT:
[All Users] ---------> [Single Server]
                          (overloaded)

WITH:
                     +-> [Server 1]
[All Users] -> [LB] -+-> [Server 2]
                     +-> [Server 3]
                     +-> [Server 4]
                          (load shared)
```

---

### Algorithms

| Algorithm                | How it works                                  | Best for                          |
| ------------------------ | --------------------------------------------- | --------------------------------- |
| **Round Robin**          | Rotate through servers sequentially           | Equal-capacity servers, stateless |
| **Weighted Round Robin** | Round robin with weights per server           | Mixed-capacity servers            |
| **Least Connections**    | Send to server with fewest active connections | Varying request durations         |
| **Least Response Time**  | Send to fastest-responding server             | Latency-sensitive apps            |
| **IP Hash**              | Hash client IP to pick server                 | Sticky sessions (soft)            |
| **Consistent Hashing**   | Hash-ring distribution                        | Caching layers, minimal remapping |
| **Random**               | Pick a random server                          | Simple, surprisingly effective    |

---

### Layer 4 vs Layer 7

```
LAYER 4 (Transport - TCP/UDP):
  Sees: IP address, port number
  Routes: Based on connection, not content
  Speed: Very fast (no content inspection)
  Examples: AWS NLB, HAProxy (TCP mode)
  Use when: Raw throughput, TCP passthrough

LAYER 7 (Application - HTTP):
  Sees: URL, headers, cookies, body
  Routes: Based on content (path, host)
  Features: SSL termination, compression,
            URL rewriting, A/B testing
  Examples: AWS ALB, Nginx, HAProxy (HTTP)
  Use when: HTTP routing, microservices
```

```
EXAMPLE L7 ROUTING:
  /api/users/*  -> User Service cluster
  /api/orders/* -> Order Service cluster
  /static/*     -> CDN / Static servers
  Host: admin.* -> Admin Service cluster
```

---

### Health Checks

```
PASSIVE (monitor failures):
  LB counts errors per server
  If error rate > threshold -> remove from pool

ACTIVE (periodic probes):
  GET /health every 10 seconds
  If 3 consecutive failures -> remove from pool
  If health returns -> add back to pool

DEEP HEALTH CHECK:
  /health/ready -> can serve traffic?
  /health/live  -> is the process alive?
  /health/db    -> can reach the database?
```

---

### Quick Recall

**If you remember only 3 things:**

1. Layer 4 LB routes by connection (fast, simple); Layer 7 routes by content (flexible, HTTP-aware)
2. Least Connections is usually the best default for most web applications
3. Always configure health checks - without them, the LB sends traffic to dead servers

**Interview one-liner:**
"I use Layer 7 load balancing (ALB/Nginx) for HTTP services with path-based routing and Least Connections algorithm, with active health checks on /health/ready - for raw TCP throughput, I use Layer 4 (NLB) with passive health monitoring."

---

### Interview Deep-Dive

**Q1: How do you handle sticky sessions with load balancing? What are the trade-offs?**

_Why they ask:_ Tests understanding of stateful vs stateless architectures.

**Answer:**
Sticky sessions (session affinity) route all requests from the same client to the same server. Implementations:

1. **Cookie-based:** LB injects a cookie with server ID. Subsequent requests with the cookie go to the same server. Most common.

2. **IP Hash:** Hash the client IP to determine the server. Breaks with NAT (many clients share one IP).

The trade-offs are significant. Benefits: simpler application (in-memory session, no shared session store). Costs: (1) Uneven load - popular users concentrate on one server. (2) Failed server = lost sessions for all its users. (3) Can't scale down easily - must drain sessions first. (4) Auto-scaling is less effective.

**Better alternative:** Externalize session state to Redis/Memcached. All servers are truly stateless and interchangeable. Any server can handle any request. Server failure affects no sessions.

**Q2: Your system gets 100K requests per second. Design the load balancing layer.**

_Why they ask:_ Tests practical architecture at scale.

**Answer:**
Multi-tier approach:

1. **DNS round-robin** across 2-3 data centers (geographic distribution).
2. **Layer 4 NLB** per data center for TCP-level distribution (handles SSL passthrough, very fast).
3. **Layer 7 ALB** behind NLB for HTTP path-based routing to different microservice clusters.
4. **Service mesh (Envoy sidecar)** for service-to-service load balancing within the cluster.

Key configurations: Connection draining (finish in-flight requests before removing servers). Cross-zone load balancing (distribute across availability zones). Rate limiting at the ALB level to prevent DDoS.

At 100K RPS, a single ALB handles this easily (AWS ALB scales to millions RPS). The bottleneck is usually the application tier, not the load balancer.

---

---

# CDN (Content Delivery Network)

**TL;DR** - A CDN caches content at geographically distributed edge servers, delivering static and dynamic content from the nearest location to reduce latency from hundreds of milliseconds to single digits.

---

### The Problem This Solves

Your server is in US-East. A user in Tokyo requests your web page. The request travels across the Pacific Ocean, hits your server, builds the response, and travels back. Round-trip latency: 200-300ms. For every image, CSS file, and JS bundle, add another 200ms. Page load: 3-5 seconds.

With a CDN edge server in Tokyo: first request is cached, subsequent requests served from Tokyo. Latency: 10-20ms.

---

### How It Works

```
WITHOUT CDN:
[User Tokyo] --200ms--> [Origin US-East]
[User London] --100ms-> [Origin US-East]
[User Sydney] --250ms-> [Origin US-East]

WITH CDN:
[User Tokyo] --10ms--> [CDN Tokyo Edge]
  (cache HIT -> serve immediately)
  (cache MISS -> fetch from origin, cache, serve)

[User London] --10ms-> [CDN London Edge]
[User Sydney] --10ms-> [CDN Sydney Edge]
```

```
CDN ARCHITECTURE:
              [Origin Server]
                    |
                    | (pull on cache miss)
                    |
    +-------+-------+-------+
    |       |       |       |
[Edge NA] [Edge EU] [Edge AP] [Edge SA]
    |       |       |       |
[Users]  [Users]  [Users]  [Users]
```

---

### What to Cache

| Content Type                    | Cache Duration               | CDN Fit      |
| ------------------------------- | ---------------------------- | ------------ |
| Static assets (JS, CSS, images) | Long (1 year + hash busting) | Perfect      |
| API responses (GET, idempotent) | Short (seconds to minutes)   | Good         |
| HTML pages (static/SSG)         | Medium (minutes to hours)    | Good         |
| Personalized content            | Don't cache at CDN           | Poor         |
| Real-time data (chat, stock)    | Don't cache                  | Not suitable |

---

### Cache Invalidation Strategies

```
1. TTL-based (Time To Live):
   Cache-Control: max-age=86400 (24 hours)
   Simple but stale data possible

2. Cache busting (versioned URLs):
   /app.abc123.js (hash in filename)
   New deploy = new hash = new URL = fresh cache
   Best for static assets

3. Purge API:
   POST /purge?url=/api/products
   Immediately removes from all edge caches
   Use for critical content updates

4. Stale-While-Revalidate:
   Cache-Control: max-age=60,
     stale-while-revalidate=300
   Serve stale, fetch fresh in background
   Best of both worlds
```

---

### CDN Providers

| Provider   | Strength                      | Typical use        |
| ---------- | ----------------------------- | ------------------ |
| CloudFront | AWS integration               | AWS-native apps    |
| Cloudflare | DDoS protection, free tier    | Most web apps      |
| Akamai     | Enterprise, largest network   | High-traffic media |
| Fastly     | Edge compute, real-time purge | Dynamic content    |

---

### Quick Recall

**If you remember only 3 things:**

1. CDN caches content at edge servers near users, reducing latency from 200ms to <20ms
2. Use cache busting (hash in filename) for static assets - no staleness, instant updates
3. Never cache personalized content at the CDN level - use `Cache-Control: private`

**Interview one-liner:**
"I put a CDN in front of all static assets with cache-busting hashes for instant invalidation, and cache idempotent API responses at the edge with short TTLs and stale-while-revalidate for the optimal latency-freshness balance."

---

### Interview Deep-Dive

**Q1: How do you handle cache invalidation for a product catalog that updates every few minutes?**

_Why they ask:_ Cache invalidation is one of the "two hard problems" in computer science.

**Answer:**
Layered approach:

1. **Short TTL for listing pages:** `Cache-Control: max-age=60, stale-while-revalidate=300`. Users see data at most 60 seconds stale. In the background, the CDN revalidates with the origin. If the origin is slow, serve stale for up to 5 minutes.

2. **Event-driven purge for critical updates:** When a product price changes, the inventory service publishes a `ProductUpdated` event. A cache invalidation service listens and calls the CDN purge API for that specific product URL.

3. **Cache busting for product images:** Images are stored with content hashes: `/images/product-abc123.jpg`. When the image changes, the hash changes, and the new URL is a cache miss.

4. **Surrogate keys (Fastly/Varnish):** Tag cached responses with product IDs. Purge all cache entries tagged with `product:12345` in one API call - no need to know all URLs.

---

---

# Leader Election

**TL;DR** - Leader election ensures exactly one node in a distributed cluster is designated as the leader to coordinate work, preventing split-brain scenarios where multiple nodes think they're in charge.

---

### The Problem This Solves

You have 5 instances of your scheduler service. Only one should run the daily report. Without leader election, all 5 run it simultaneously. Or worse: a network partition splits the cluster, and both halves elect a leader (split-brain).

---

### How It Works

```
NORMAL OPERATION:
[Node 1 LEADER] <-> [Node 2 FOLLOWER]
                <-> [Node 3 FOLLOWER]
  Leader coordinates work
  Followers are standby

LEADER FAILURE:
[Node 1 DOWN]   [Node 2] -> becomes LEADER
                [Node 3] -> remains FOLLOWER
  Election triggered by heartbeat timeout

SPLIT-BRAIN (the nightmare):
  [Node 1 LEADER] <-X-> [Node 2 LEADER?]
  Both think they're the leader
  Both process work -> duplicates, corruption
```

---

### Implementation Approaches

| Approach           | Mechanism                         | Complexity   |
| ------------------ | --------------------------------- | ------------ |
| **Database**       | `SELECT FOR UPDATE` or unique row | Simple       |
| **ZooKeeper**      | Ephemeral sequential znodes       | Proven       |
| **etcd**           | Lease-based with TTL              | Cloud-native |
| **Redis**          | SETNX with TTL (Redlock)          | Common       |
| **Raft consensus** | Log replication + voting          | Strongest    |
| **K8s Lease**      | Kubernetes Lease objects          | K8s-native   |

---

### Code Example (Database-Based)

```java
// Simple database-based leader election
@Scheduled(fixedRate = 15_000)
public void tryBecomeLeader() {
    try {
        // Try to acquire leadership
        int updated = jdbcTemplate.update(
            "UPDATE leader_election "
            + "SET leader_id = ?, "
            + "    last_heartbeat = NOW() "
            + "WHERE key = 'scheduler' "
            + "AND (leader_id = ? "
            + "     OR last_heartbeat "
            + "        < NOW() - INTERVAL '30s')",
            instanceId, instanceId);

        isLeader = (updated > 0);
        if (isLeader) {
            log.info("I am the leader: {}",
                instanceId);
        }
    } catch (Exception e) {
        isLeader = false;
    }
}

// Only leader executes scheduled work
@Scheduled(cron = "0 0 6 * * *")
public void dailyReport() {
    if (!isLeader) return;
    reportService.generateDaily();
}
```

---

### Raft Consensus (Brief Overview)

```
RAFT ELECTION:
1. Followers have election timeout (random 150-300ms)
2. If no heartbeat from leader, follower becomes
   CANDIDATE and requests votes
3. Candidate that gets majority (3 of 5) becomes LEADER
4. Leader sends periodic heartbeats to maintain authority
5. If leader fails, timeout triggers new election

KEY INSIGHT:
  Randomized timeouts prevent split votes
  Majority quorum prevents split-brain
  (Can't have two leaders with majority of same cluster)
```

---

### Quick Recall

**If you remember only 3 things:**

1. Leader election ensures exactly one coordinator - prevents duplicate work and split-brain
2. Database `UPDATE ... WHERE heartbeat < timeout` is the simplest production-ready approach
3. Raft uses majority quorum + randomized timeouts to guarantee single leader without split-brain

**Interview one-liner:**
"For simple leader election, I use a database row with heartbeat timeout, which is sufficient for most applications - for distributed consensus at the infrastructure level, Raft-based systems like etcd provide stronger guarantees with majority quorum preventing split-brain."

---

---

# Bloom Filters

**TL;DR** - A Bloom filter is a space-efficient probabilistic data structure that tells you "definitely NOT in the set" or "probably in the set" - using minimal memory to avoid expensive lookups for non-existent keys.

---

### The Problem This Solves

Your database has 1 billion user records. A request comes for `user_id=abc123`. To check if this user exists, you query the database. 99% of lookups are for users that DON'T exist (invalid IDs, typos, attacks). Each lookup is a wasted database round-trip.

A Bloom filter sits in front of the database. It uses ~1GB of memory to represent 1 billion keys. For non-existent keys, it immediately says "definitely not here" without touching the database. Database lookups drop by 99%.

---

### How It Works

```
BLOOM FILTER (bit array + hash functions):
  Bit array: [0][0][0][0][0][0][0][0][0][0]

  INSERT "alice":
    hash1("alice") = 2
    hash2("alice") = 5
    hash3("alice") = 8
    Set bits 2, 5, 8 to 1
  Bit array: [0][0][1][0][0][1][0][0][1][0]

  LOOKUP "bob":
    hash1("bob") = 1
    hash2("bob") = 5
    hash3("bob") = 7
    Check bits 1, 5, 7
    Bit 1 = 0 -> DEFINITELY NOT IN SET (done!)

  LOOKUP "alice":
    hash1("alice") = 2, hash2 = 5, hash3 = 8
    All bits are 1 -> PROBABLY IN SET
    (might be a false positive - verify with DB)
```

**Key properties:**

- **No false negatives:** If it says "not in set," it's 100% correct
- **Possible false positives:** If it says "probably in set," it might be wrong (tunable - typically 1% FP rate)
- **No deletion:** Standard Bloom filters don't support removal (use Counting Bloom Filter for that)
- **Space:** ~10 bits per element for 1% FP rate

---

### Real-World Use Cases

| System          | Use                          | Why Bloom Filter       |
| --------------- | ---------------------------- | ---------------------- |
| Google BigTable | Skip SSTables without key    | Avoid disk reads       |
| PostgreSQL      | Hash join optimization       | Skip hash table probes |
| CDN/Cache       | Check if URL is cached       | Avoid origin fetch     |
| Spam filter     | Known spam signatures        | Fast pre-filter        |
| Web crawler     | Already-visited URLs         | Avoid re-crawling      |
| Cryptocurrency  | SPV wallet transaction check | Save bandwidth         |

---

### Quick Recall

**If you remember only 3 things:**

1. "Definitely not in set" or "probably in set" - no false negatives, tunable false positives
2. ~10 bits per element for 1% false positive rate (1 billion elements = ~1.2 GB)
3. Use as a pre-filter to avoid expensive lookups for non-existent keys (databases, disk, network)

**Interview one-liner:**
"I use Bloom filters as a pre-filter in front of expensive lookups - with ~10 bits per element and a 1% false positive rate, they eliminate 99% of unnecessary database queries for non-existent keys, as used by BigTable, PostgreSQL, and CDN caches."
