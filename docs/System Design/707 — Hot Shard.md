---
layout: default
title: "Hot Shard"
parent: "System Design"
nav_order: 707
permalink: /system-design/hot-shard/
number: "707"
category: System Design
difficulty: â˜…â˜…â˜…
depends_on: "Sharding (System), Consistent Hashing"
used_by: "Data Partitioning Strategies, Read-Heavy vs Write-Heavy Design"
tags: #advanced, #distributed, #database, #architecture, #reliability
---

# 707 â€” Hot Shard

`#advanced` `#distributed` `#database` `#architecture` `#reliability`

âš¡ TL;DR â€” **Hot Shard** is a database performance problem where one shard receives disproportionately more traffic than others (due to a poor shard key, celebrity users, or viral content), becoming a bottleneck while other shards sit underutilised.

| #707            | Category: System Design                                        | Difficulty: â˜…â˜…â˜… |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Sharding (System), Consistent Hashing                          |                 |
| **Used by:**    | Data Partitioning Strategies, Read-Heavy vs Write-Heavy Design |                 |

---

### ðŸ“˜ Textbook Definition

**Hot Shard** (also called a hot partition or hot key problem) is a load imbalance in a sharded database system where one or a few shards receive a disproportionately high volume of read or write traffic relative to other shards. The affected shard becomes a bottleneck, experiencing high CPU, memory exhaustion, or throughput limits while other shards remain largely idle â€” negating the benefits of sharding. Hot shards arise from three root causes: (1) **poor shard key choice** (sequential keys like timestamps, celebrity users with high fan counts); (2) **Zipf distribution in access patterns** (the top 1% of items receive 50%+ of traffic â€” common in social media, e-commerce); (3) **known high-traffic events** (product launches, viral posts). Solutions include: shard splitting, key randomisation with suffix, read replicas for hot shards, caching, and dedicated shard tiers.

---

### ðŸŸ¢ Simple Definition (Easy)

Hot Shard: you split data across 10 database servers to distribute load, but 90% of requests all go to server #3 because that's where the popular items (or celebrity users) live. Server #3 is overwhelmed; the other 9 are idle. Sharding didn't help because the data isn't evenly accessed â€” popular items concentrate traffic on one shard.

---

### ðŸ”µ Simple Definition (Elaborated)

Twitter celebrity problem: Elon Musk has 100M followers. Each tweet creates 100M fan-out writes. His data is on Shard 42. Shard 42: overwhelmed by all activity related to one high-traffic user. Shards 1-41, 43-100: normal load. Shard 42 becomes the hot shard â€” the bottleneck that limits the entire system's performance despite having 100 other shards available. The solution: don't try to store Elon's data on a single shard the same way as a user with 100 followers. Treat high-traffic users (celebrities) differently at the architecture level.

---

### ðŸ”© First Principles Explanation

**Root causes and solutions for hot shard:**

```
ROOT CAUSE 1: SEQUENTIAL SHARD KEYS

  Shard key: user_id (auto-increment: 1, 2, 3, ...)
  Hash: user_id % 10

  New users registered:
    user_id 1001: hash 1001 % 10 = 1 â†’ shard 1
    user_id 1002: hash 1002 % 10 = 2 â†’ shard 2
    user_id 1003: hash 1003 % 10 = 3 â†’ shard 3
    ...seemingly even!

  PROBLEM: All writes of new content go to the current time range shard.
  If posts sharded by timestamp:
    All new posts (right now) â†’ current_day shard.
    Historical shards: read-only, low load.
    Current shard: 100% of write load.
    Solution: Use content_id (UUID-based) as shard key, not timestamp.

ROOT CAUSE 2: CELEBRITY / VIRAL CONTENT (Zipf's Law)

  Zipf's law: in social systems, a tiny fraction of users/items
  receive the majority of traffic.

  Example (e-commerce):
    Product A: 1,000,000 views/day (viral TikTok product)
    Products B-Z: average 100 views/day each

    Product A on Shard 3: Shard 3 handles 1,000,000 / (1,000,000 + 25Ã—100) = 97.5% of all requests.
    Shards 1,2,4-10: 0.25% each.

  HOT SHARD: Shard 3.

  SOLUTION 1: ADD READ REPLICAS FOR THE HOT SHARD
    Shard 3 hot (reads): add 5 read replicas of Shard 3.
    Route reads: round-robin across 5 replicas.
    Effect: 1,000,000 reads / 6 instances = 166,667 reads each (manageable).

  SOLUTION 2: CACHE (application-level)
    Cache product A in Redis:
    On product page request: check Redis first.
    Cache hit rate: 99% (product A is same data always) â†’ DB sees only 10,000 req/day.
    Effect: hot shard reads reduced 99% by caching.
    Works best for read-heavy hot keys (not write-heavy).

  SOLUTION 3: KEY SUFFIX RANDOMISATION (for write hot keys)
    Viral product A has shard_key = product_id = 12345.
    Technique: append random suffix to shard key:
      shard_key = product_id + "#" + random_int(1, 10)
      â†’ 10 artificial shard keys for the same product
      â†’ 10Ã— write distribution: each shard gets 10% of product A's writes

    COST: reads must now query all 10 suffix keys and aggregate:
      product_A_count = sum(count for suffix 1-10)
      Acceptable for aggregation queries.
      Bad for unique constraint enforcement or exact lookups.

ROOT CAUSE 3: HOT PARTITION IN TIME-SERIES DATA

  IoT sensor data sharded by sensor_id:
    Normal sensors: 1 reading/minute
    High-frequency sensor: 1,000 readings/second

  High-frequency sensor's shard: 1,000 readings/sec vs. 1 reading/min.
  Shard for sensor X: 60,000Ã— hotter than average shard.

  SOLUTION: SUB-SHARDING the hot partition
    Shard for hot_sensor: split into N sub-shards.
    Route: sensor_id = "hot_sensor_001" â†’ hash(sensor_id + reading_id) % N
    â†’ Hot sensor's data spread across N shards.
    N = 10 â†’ hot shard load divided by 10.

DETECTION (how to find hot shards):

  Monitor per-shard metrics:
  - CPU per shard (hot shard: CPU >> other shards)
  - QPS per shard (hot shard: QPS >> avg Ã— 5)
  - Replication lag per shard (hot shard writes backing up)
  - Queue depth per shard (hot shard: requests queuing)

  Alert: if any_shard_QPS > 3 Ã— avg_shard_QPS â†’ hot shard alert.

  // Prometheus alert:
  // (shard_qps - avg(shard_qps)) / avg(shard_qps) > 2.0 â†’ fire alert
  // (shard QPS is 2Ã— above average â†’ potential hot shard)

SHARD SPLITTING (reactive solution):

  Hot shard detected â†’ split it into 2 smaller shards:

  Before: Shard 3 (range: user_id 300K-400K) â€” hot
  After:
    Shard 3A: user_id 300K-350K
    Shard 3B: user_id 350K-400K

  Process:
    1. Create Shard 3B (new DB server)
    2. Double-write: writes go to both 3A and 3B
    3. Backfill: copy 350K-400K records from Shard 3 to Shard 3B
    4. Cutover: update routing table: 350K-400K â†’ Shard 3B
    5. Stop double-write
    6. Remove 350K-400K records from Shard 3A (cleanup)

  This is a live migration â€” complex but necessary for production hot shard relief.
```

---

### â“ Why Does This Exist (Why Before What)

WITHOUT Hot Shard awareness:

- Sharding deployed: looks like 10Ã— capacity
- In practice: 90% of traffic â†’ 1 shard â†’ that shard overwhelmed â†’ system no better than un-sharded
- False sense of scale: "we have 10 shards" but 1 is doing all the work

WITH Hot Shard mitigation:
â†’ True load distribution: each shard handles proportional traffic
â†’ Sharding delivers promised throughput gains
â†’ Single shard failure: proportional impact (not catastrophic)

---

### ðŸ§  Mental Model / Analogy

> A shopping mall has 10 checkout lanes. One lane (lane 5) is right next to the entrance and the popular food court â€” 90% of shoppers queue there. Lanes 1-4 and 6-10 are largely empty. The mall has 10Ã— the checkout capacity, but effectively only 1Ã— is being used (lane 5). Fix: add more cashiers to lane 5 (read replicas), or reroute food court traffic to multiple lanes (key suffix distribution), or reserve lane 5 for VIP customers only (caching + dedicated tier).

"Shopping mall checkout lanes" = database shards
"Lane 5 near the entrance" = shard with popular/celebrity data
"90% of shoppers queue at lane 5" = hot shard (disproportionate traffic)
"Add more cashiers to lane 5" = add read replicas for the hot shard
"Reroute traffic to multiple lanes" = key suffix randomisation (distribute hot key across shards)
"10 lanes, but only 1 used effectively" = sharding without hot shard mitigation

---

### âš™ï¸ How It Works (Mechanism)

**Hot shard detection and mitigation pipeline:**

{% raw %}
```
MONITORING PIPELINE:

1. Per-shard metrics collection (Prometheus + Grafana):

  // Java: custom shard metrics with Micrometer
  @Component
  public class ShardMetrics {
      private final MeterRegistry meterRegistry;

      public void recordShardQuery(int shardId, long durationMs) {
          meterRegistry.counter("shard.queries.total",
              "shard_id", String.valueOf(shardId)
          ).increment();

          meterRegistry.timer("shard.query.duration",
              "shard_id", String.valueOf(shardId)
          ).record(durationMs, TimeUnit.MILLISECONDS);
      }
  }

2. Hot shard detection alert (Prometheus alerting rule):

   # Alert: shard QPS > 3Ã— average QPS
   alert: HotShardDetected
   expr: |
     (shard_queries_total:rate5m / avg(shard_queries_total:rate5m)) > 3
   for: 5m
   labels:
     severity: warning
   annotations:
     description: "Shard {{ $labels.shard_id }} is {{ $value }}Ã— the average QPS"

3. Auto-mitigation: route hot shard reads to replicas

   public DataSource getReadDataSource(String shardKey) {
       int shardId = hash(shardKey) % numShards;
       double shardLoad = metricsService.getShardQPS(shardId);
       double avgLoad = metricsService.getAvgShardQPS();

       if (shardLoad > avgLoad * 2.5) {
           // Hot shard: use read replica pool
           return hotShardReadReplicas.get(shardId)
                                      .getRandomReplica();
       }
       return shards.get(shardId);  // normal shard
   }
```
{% endraw %}

---

### ðŸ”„ How It Connects (Mini-Map)

```
Sharding (System) â€” foundation
        â”‚ (uneven traffic distribution problem)
        â–¼
Hot Shard â—„â”€â”€â”€â”€ (you are here)
(one shard overwhelmed)
        â”‚
        â”œâ”€â”€ Consistent Hashing (better initial distribution)
        â”œâ”€â”€ Caching (reduce reads to hot shard)
        â””â”€â”€ Read-Heavy vs Write-Heavy Design (different strategies per access pattern)
```

---

### ðŸ’» Code Example

**Redis hot key detection and mitigation:**

```python
import redis
import random
from collections import defaultdict

r = redis.Redis()

# Hot key mitigation: key suffix randomisation
NUM_COPIES = 10  # split hot key across 10 redis keys

def set_hot_key(key: str, value: str, ttl: int = 300):
    """Write to all 10 copies of a hot key."""
    for suffix in range(NUM_COPIES):
        r.setex(f"{key}#{suffix}", ttl, value)

def get_hot_key(key: str) -> str:
    """Read from a random copy (distributes reads across 10 keys)."""
    suffix = random.randint(0, NUM_COPIES - 1)
    return r.get(f"{key}#{suffix}")

# Usage: viral product data
product_id = "product:viral_001"
set_hot_key(product_id, '{"name":"Trending Item","price":29.99}')

# Each read goes to a random copy:
data = get_hot_key(product_id)

# Result: 100,000 reads/sec spread across 10 Redis keys
# Each key: ~10,000 reads/sec (Redis can handle 100K-1M ops/sec per node)
# vs 100,000 reads/sec on single key (potential Redis CPU bottleneck)
```

---

### âš ï¸ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| More shards prevent hot shard problems     | More shards reduce the probability of hot shards but don't eliminate them. If the top 1% of users generate 50% of traffic (Zipf distribution), 1% of shards will always be disproportionately loaded regardless of how many shards exist. The problem is data skew, not shard count                          |
| Hash-based sharding eliminates hot shards  | Hash-based sharding distributes data evenly by ID, but doesn't distribute access evenly. User 12345 (1M followers) and User 67890 (10 followers) both get one shard each â€” but User 12345's shard gets 1MÃ— more traffic. Even distribution of data â‰  even distribution of access                             |
| Hot shards only affect write-heavy systems | Hot shards are equally problematic for read-heavy systems. A viral product in e-commerce or a celebrity profile on social media causes hot reads on the respective shard's replicas. Read replicas help scale reads, but the primary shard for write coordination remains a bottleneck                       |
| Caching always solves hot shard problems   | Caching effectively mitigates read hot shards. But write hot shards (viral content receiving thousands of likes/comments per second) cannot be mitigated by caching â€” those writes must hit the database. Write hot shards require shard splitting, write queue/batching, or eventual consistency approaches |

---

### ðŸ”¥ Pitfalls in Production

**Celebrity user causes shard failure:**

```
PROBLEM: Single celebrity user overwhelms primary shard

  Architecture: social network, users sharded by user_id % 100
  Celebrity: user_id = 55 â†’ Shard 55
  Normal user: 100 followers â†’ 100 fanout operations per post
  Celebrity: 50M followers â†’ 50M fanout operations per post

  Celebrity posts: Shard 55 receives 50M write operations in seconds.
  Shard 55 CPU: 100%. Write queue: 500,000 pending.
  Write latency: 10ms â†’ 30,000ms (30 seconds!).
  Shard 55 primary: eventually crashes (OOM from write queue).

  Impact: ALL users with user_id % 100 = 55 affected (not just the celebrity).
  10,000 ordinary users: cannot access their profiles.

SOLUTION 1: PUSH vs PULL HYBRID (fan-out on read for celebrities)

  For normal users: pre-compute fan-out on write (push model)
    User posts â†’ writes to all followers' feeds immediately.
    Fast reads; expensive writes (acceptable for small follower count).

  For celebrities (>1M followers): don't fan out on write.
    User posts â†’ stored only on celebrity's shard.
    Follower's feed read: fetch follower's pre-computed feed PLUS
    check celebrity accounts they follow for recent posts (pull for celebrities).
    Read is slightly slower; write is not catastrophic.

  Threshold: if follower_count > 500,000 â†’ switch to pull model.
  Twitter's actual solution: tiered fan-out based on follower count.

SOLUTION 2: CELEBRITY TIER (dedicated shards for high-traffic users)

  Detect high-traffic users: follower_count > 100,000.
  Move to dedicated celebrity shard (higher-spec hardware).
  Each celebrity: gets their own shard (extreme case) or shares a
  celebrity-tier shard with other celebrities.
  Ordinary shards: no celebrity traffic contamination.
```

---

### ðŸ”— Related Keywords

- `Sharding (System)` â€” hot shard is the primary operational problem in sharded databases
- `Consistent Hashing` â€” virtual nodes help distribute load more evenly and reduce hot shards
- `Read-Heavy vs Write-Heavy Design` â€” different hot shard mitigation strategies per access type
- `Caching` â€” most effective mitigation for read hot shards
- `Fan-Out on Write vs Read` â€” fundamental trade-off in social systems for handling celebrity data

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ One shard overwhelmed while others idle   â”‚
â”‚              â”‚ â€” negates sharding benefits               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Detecting with per-shard QPS monitoring;  â”‚
â”‚              â”‚ designing shard key selection criteria    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Timestamp / sequential shard keys;        â”‚
â”‚              â”‚ no celebrity/viral-content handling       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "10 checkout lanes â€” 90% queue at lane 5  â”‚
â”‚              â”‚  near the food court."                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Consistent Hashing â†’ Fan-Out on Write     â”‚
â”‚              â”‚ â†’ Read-Heavy vs Write-Heavy Design        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** Design the data storage strategy for a Twitter-like platform that must handle celebrity users (>1M followers) without hot shards. Specifically: (a) how would you detect that a specific shard has become "hot" in production? (b) for the fan-out write problem (celebrity posts to 50M followers), describe a hybrid push/pull architecture with a clear threshold for switching between modes; (c) what happens to Shard 42 (containing the celebrity's profile data) during a viral event â€” what mitigation do you apply?

**Q2.** Your Redis cluster has 16 shards using key-based hashing. A product goes viral and 500,000 reads/second all target the key `product:SKU-001`. The Redis shard holding this key can handle 100,000 ops/sec. Describe three different mitigation strategies: (a) key suffix randomisation with 10 copies, (b) local in-process caching at the application tier, (c) read replicas for the hot Redis shard. For each strategy: what changes to read code, write code? What consistency guarantees does each approach sacrifice?
