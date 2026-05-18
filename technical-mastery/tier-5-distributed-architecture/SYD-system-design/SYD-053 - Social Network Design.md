---
id: SYD-053
title: Social Network Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-045
used_by: ""
related: SYD-031, SYD-045, SYD-008, SYD-039
tags:
  - architecture
  - social
  - graph
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/syd/social-network-design/
---

⚡ TL;DR - A social network stores and traverses a
user relationship graph (follows, friendships, mutual
connections) at scale. Key features: user profiles,
connections, news feed, messaging, notifications. The
core data model is a graph: users are nodes, relationships
are edges. Graph queries (second-degree connections,
mutual friends) are expensive at scale - precompute
results where possible. Storage: relational DB for
profiles, graph store (Neo4j) or adjacency list in
a key-value store for the social graph, Redis for
presence and counters.

| #053 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sharding, News Feed Design | |
| **Related:** | Sharding, News Feed Design, Caching, Distributed Locks | |

---

### 🔥 The Problem This Solves

Facebook has 3B users. Displaying "people you may know"
requires finding users who share mutual friends with you.
At 3B users with an average of 200 friends each:
- Naively: 200 friends × 200 friends-of-friends = 40,000
  candidate second-degree connections (per user)
- If computed on demand for 100M daily active users:
  4 trillion operations per day. Clearly infeasible.

The social graph must be partitioned, cached, and queried
with precomputed indexes for most traversal operations.

---

### 📘 Textbook Definition

**Social network:** A platform centered on a user
relationship graph where users create connections
(follows, friendships) and interact through shared content.
Core features are built on traversing this graph efficiently.

**Adjacency list:** For each user, store their list of
followers/friends. Stored in a key-value map:
`user:{id}:friends → [id1, id2, id3, ...]`. O(1) to
retrieve direct friends. O(degree) to traverse 1 hop.

**Graph partitioning:** Dividing the social graph across
shards. The challenge: a user and their friends should
ideally be on the same shard (co-location) to minimize
cross-shard hops for friend queries. Near-impossible
at scale (celebrity with 100M followers spans all shards).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Social graph = users (nodes) + relationships (edges).
Store adjacency lists; cache hot traversals; precompute
mutual connections; shard by user_id.

**One analogy:**
> Think of LinkedIn as a map of roads between cities:
> Users are cities; friendships are roads.
> Finding "all cities within 2 roads of New York" is
> a graph traversal problem (2-hop BFS).
> At scale: you pre-draw the map (precompute)
> rather than walking every road on demand.

**One insight:**
Social networks are fundamentally different from other
systems because the most expensive queries are graph
traversals (multi-hop). A "users you may know" query
at 2 hops touches millions of nodes. The engineering
insight: precompute these traversals offline (batch
job), store results, serve from cache. Never compute
multi-hop graph queries in real-time at scale.

---

### 🔩 First Principles Explanation

**CORE DATA MODELS:**
```
1. User profiles:
   Postgres/MySQL: users table
   Sharded by user_id (range or hash)
   Cached in Redis: profile:{user_id}

2. Social graph (adjacency list):
   For follows (Twitter-like, directed):
     followers:{user_id} → sorted set of follower IDs
     following:{user_id} → sorted set of followed IDs
   
   For friendships (Facebook-like, bidirectional):
     friends:{user_id} → set of friend IDs
     (symmetric: if A → B, also B → A)

3. Mutual connections (precomputed):
   Batch job runs nightly:
     mutuals:{A}:{B} → count of mutual friends
   Too expensive to compute on every request.

4. Counters (Redis):
   followers_count:{user_id} → INT
   posts_count:{user_id} → INT
   Use INCR/DECR for atomic updates.
   Avoid counting every time from relations table.

5. News feed: → (see SYD-045 News Feed Design)
```

**FOLLOW/UNFOLLOW OPERATIONS:**
```
Follow user A → user B:
  1. Check if already following (avoid duplicate)
     SISMEMBER following:{A} {B}
  2. Add to A's following set:
     ZADD following:{A} {timestamp} {B}
  3. Add to B's followers set:
     ZADD followers:{B} {timestamp} {A}
  4. Increment counters:
     INCR followers_count:{B}
     INCR following_count:{A}
  5. Fan-out: if B is not a celebrity (< 10K followers):
     add B's recent posts to A's feed (fan-out on write)

Unfollow A → B:
  1. ZREM following:{A} {B}
  2. ZREM followers:{B} {A}
  3. DECR followers_count:{B}
  4. Remove B's posts from A's feed (or let TTL expire)
```

**MUTUAL FRIENDS (PRECOMPUTED):**
```
For "mutual friends" between users A and B:
  Naive: SINTER friends:{A} friends:{B}
  Works for small friend lists (< 1,000 friends each).
  At Facebook: 5,000 friends max → SINTER of two
  5,000-element sets: fast (Redis intersects in < 1ms).
  
  For "people you may know" (friend-of-friend):
  Batch job (runs nightly or on a schedule):
    For each user A:
      For each friend B of A:
        For each friend C of B (if C is not already A's
          friend):
          Increment PYMK score for (A, C)
    Store top-50 PYMK suggestions per user.
  
  Result: pymk:{user_id} → sorted set of suggested users
  Serve "people you may know" from this precomputed set.
  Much faster than real-time graph traversal.
```

---

### 🧪 Thought Experiment

**SIZING: Social network at LinkedIn scale**

Users: 900M registered, 300M DAU.
Average connections: 300 per user.
Total edges (connections): 900M × 300 / 2 = 135B edges.
At 8 bytes per edge: 135B × 8 = 1.08TB of edge data.
With overhead (adjacency list keys): ~3-5TB total.

**Sharding:**
Shard by user_id (hash). 100 shards: 30M users/shard.
Each shard: 30M users × 300 connections × 8B = 72GB edge data.
Plus profile data: 30M users × 1KB = 30GB.
Total per shard: ~102GB → fits in a large Redis instance
or Cassandra node.

**Graph traversal (1-hop):**
"All connections of user X": single shard lookup.
O(degree) = O(300). Very fast.

**Graph traversal (2-hop):**
"All second-degree connections of user X":
  300 friends × 300 friends = 90,000 candidates.
  90,000 lookups across potentially 100 shards.
  Cross-shard = network calls. Too slow for real-time.
  Solution: precompute + batch. Never real-time.

---

### 🧠 Mental Model / Analogy

> A social network is like a complex web of
> telephone directories:
>
> Each user's page in the directory lists their friends
> (adjacency list). Finding "common friends between
> A and B": look up A's friends, look up B's friends,
> find names that appear in both lists.
>
> "People you may know": look up all of A's friends'
> directories (second-degree), count which names appear
> most frequently. Very expensive if done while the
> customer waits - so the phone company computes this
> overnight and mails you a "suggested connections" card.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A social network lets people connect with each other
(follow, friend), share content, and see each other's
posts in a feed. The system keeps track of who is
friends with whom and shows you relevant connections
and content.

**Level 2 - How to use it (junior developer):**
Store users in a database. Store friend/follow
relationships in a separate table or adjacency list.
Use Redis for counters (follower count) and sets
(friend lists). Feed is built from the connections
graph (see News Feed Design).

**Level 3 - How it works (mid-level engineer):**
User profiles: Postgres sharded by user_id. Social
graph: Redis sorted sets (following:{id}, followers:{id}).
Counters: Redis INCR (faster than COUNT(*) in DB).
Mutual friends: SINTER for small lists, precomputed
batch for large networks. "People you may know":
batch job computes 2-hop suggestions nightly, stores
in Redis sorted set. Feed: hybrid fan-out (see SYD-045).

**Level 4 - Why it was designed this way (senior/staff):**
The social graph is split between a relational database
(source of truth) and Redis (fast access). The DB stores
the canonical relationship (with timestamps, metadata).
Redis stores denormalized, query-optimized views (sorted
sets for follower lists). This duplication is intentional:
Redis answers "how many followers?" in < 1ms; the DB
answers "when did A follow B?" for audit purposes.
Batch precomputation of multi-hop traversals (PYMK,
degree-of-separation) is necessary because real-time
graph traversal at 3B-user scale is infeasible. The
batch cadence (nightly for PYMK) is a product decision:
freshness vs cost.

**Level 5 - Mastery (distinguished engineer):**
Meta uses a specialized graph database (TAO - The
Associations and Objects) to store the social graph.
TAO is a cache + database system optimized for social
graph reads: fast association (edge) queries, read-through
caching with write-through to MySQL, distributed across
hundreds of data centers globally. The key insight:
social graph reads vastly outnumber writes. The system
is optimized for high-throughput reads with eventual
consistency. LinkedIn uses a distributed graph store
(Voldemort + custom graph index) with Hadoop-based batch
processing for graph analytics (Spark for PYMK, community
detection). The hardest distributed systems problem in
social networks is the "celebrity" edge case: Justin Bieber
has 100M followers. Every one of those 100M followers'
feeds needs to include his posts. This one user's data
touches every cache shard, every feed shard.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SOCIAL GRAPH STORAGE                                │
│                                                      │
│ User: {user_id: 123}                               │
│                                                      │
│ Redis keys:                                         │
│   profile:123    → JSON {name, bio, ...}           │
│   following:123  → ZSET {user_id → follow_ts}      │
│   followers:123  → ZSET {user_id → follow_ts}      │
│   following_count:123 → INT                        │
│   followers_count:123 → INT                        │
│   feed:123       → ZSET {post_id → post_ts}        │
│   pymk:123       → ZSET {user_id → mutual_count}   │
│                                                      │
│ 2-hop traversal for PYMK (batch job):              │
│   FOR user A:                                       │
│     GET following:A → friends list                 │
│     FOR each friend B:                             │
│       GET following:B → friend-of-friend list      │
│       For each FOF C (not already followed by A):  │
│         ZINCRBY pymk:A 1 {C}  → rank by mutual cnt│
│     Keep top 50 in pymk:A                         │
│   Run nightly for all active users                 │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Follow, unfollow, and mutual friends**
```python
import redis
from typing import List, Set

r = redis.Redis()

def follow(follower_id: int, followee_id: int):
    """User follower_id follows followee_id."""
    import time
    ts = time.time()

    # Check not already following (idempotent)
    already = r.zscore(
        f"following:{follower_id}", str(followee_id))
    if already:
        return  # Already following

    pipe = r.pipeline()
    # Bidirectional: following and followers sets
    pipe.zadd(f"following:{follower_id}",
              {str(followee_id): ts})
    pipe.zadd(f"followers:{followee_id}",
              {str(follower_id): ts})
    # Increment counters
    pipe.incr(f"following_count:{follower_id}")
    pipe.incr(f"followers_count:{followee_id}")
    pipe.execute()

def unfollow(follower_id: int, followee_id: int):
    """User follower_id unfollows followee_id."""
    pipe = r.pipeline()
    pipe.zrem(f"following:{follower_id}", str(followee_id))
    pipe.zrem(f"followers:{followee_id}", str(follower_id))
    pipe.decr(f"following_count:{follower_id}")
    pipe.decr(f"followers_count:{followee_id}")
    pipe.execute()

def get_mutual_followers(user_a: int,
                          user_b: int) -> List[int]:
    """
    Find mutual followers between user_a and user_b.
    Works for small-to-medium follower counts.
    SINTER returns the intersection of two sets.
    """
    # Create temporary sets for SINTER
    # (followers sets are sorted sets, need plain set)
    followers_a = set(r.zrange(
        f"followers:{user_a}", 0, -1))
    followers_b = set(r.zrange(
        f"followers:{user_b}", 0, -1))
    mutual = followers_a & followers_b
    return [int(uid) for uid in mutual]

def get_people_you_may_know(user_id: int,
                               limit: int = 10) -> List[int]:
    """
    Return pre-computed PYMK suggestions.
    Populated nightly by batch job.
    """
    suggestions = r.zrevrange(
        f"pymk:{user_id}", 0, limit - 1)
    return [int(uid) for uid in suggestions]
```

**Example 2 - Real-time 2-hop traversal (BAD)**
```python
# BAD: Real-time 2-hop traversal at scale
def get_pymk_realtime_bad(user_id: int) -> list:
    """
    Real-time 2-hop traversal.
    DO NOT use in production at scale.
    """
    # Get all friends (may be 5,000 for heavy users)
    friends = r.zrange(f"following:{user_id}", 0, -1)
    
    pymk = {}
    for friend_id in friends:
        # For EACH friend: fetch THEIR friends
        # 5,000 friends × 5,000 friends-of-friends
        # = 25,000,000 Redis calls per PYMK request
        # = multiple seconds latency per user
        friends_of_friend = r.zrange(
            f"following:{friend_id}", 0, -1)
        for fof in friends_of_friend:
            if fof not in friends and fof != str(user_id):
                pymk[fof] = pymk.get(fof, 0) + 1

    return sorted(pymk, key=pymk.get, reverse=True)[:10]
    # At 300 DAU × 300 friends average:
    # 300M PYMK calculations at 90K Redis calls each
    # = 27 trillion Redis calls/day. Impossible.

# GOOD: Precompute nightly via batch job (shown above).
# Serve from pymk:{user_id} sorted set.
```

---

### ⚖️ Comparison Table

| Data | Storage | Query Pattern | Why |
|---|---|---|---|
| **User profiles** | Postgres (sharded) | Single user by ID | Relational, transactional updates |
| **Social graph (edges)** | Redis sorted sets | Follower lists, mutual | In-memory, fast O(1) set operations |
| **Counters** | Redis INCR | Follower/following count | Atomic increment, no locking |
| **PYMK suggestions** | Redis sorted set | Pre-computed, serve top-K | Expensive to compute; cache results |
| **News feed** | Redis sorted set | Paginated timeline | Fast sorted reads, TTL eviction |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Social graph should be stored in a graph database (Neo4j) | Neo4j is excellent for graph traversals but does not scale to 3B users without significant sharding complexity. Most large social networks (Facebook, Twitter, LinkedIn) use custom distributed key-value and column stores for the graph, not general-purpose graph databases. Neo4j is appropriate for smaller social graphs (< 100M nodes) or enterprise knowledge graphs. |
| Follower count can be derived from the followers table at query time | COUNT(*) on a 100M-row followers table is expensive. Use a pre-maintained counter (Redis INCR/DECR) for every follow/unfollow. The counter is the source of truth for display. Reconcile with the actual count periodically (nightly batch) to fix any counter drift from edge cases. |
| All social graph queries need real-time consistency | "People you may know" can be up to 24 hours stale (batch refresh). "Mutual friends" for a profile view can be seconds stale (TTL on cache). "Follower count" should be near-real-time (Redis counter). Different features have different freshness requirements; do not build everything with strong consistency. |

---

### 🚨 Failure Modes & Diagnosis

**Follow Graph Desync (Counter vs Actual Count)**

**Symptom:**
User profile shows "1,247 followers" but the followers
tab loads 892 users. The counter is wrong. Users report
follower counts jumping up and down unpredictably.

**Root Cause:**
The `DECR followers_count:{id}` in the unfollow handler
was executing even when the user was not actually
following (idempotent check was missing). Negative
decrements made the counter drift.

**Fix:**
```python
def follow_safe(follower_id: int, followee_id: int):
    """Idempotent follow with counter consistency."""
    import time
    # Lua script: atomic check + follow + counter increment
    lua_script = """
    local already = redis.call(
        'ZSCORE', KEYS[1], ARGV[1])
    if already then
        return 0  -- Already following, no-op
    end
    redis.call('ZADD', KEYS[1], ARGV[2], ARGV[1])
    redis.call('ZADD', KEYS[2], ARGV[2], ARGV[3])
    redis.call('INCR', KEYS[3])
    redis.call('INCR', KEYS[4])
    return 1  -- Success
    """
    script = r.register_script(lua_script)
    ts = time.time()
    script(
        keys=[
            f"following:{follower_id}",
            f"followers:{followee_id}",
            f"following_count:{follower_id}",
            f"followers_count:{followee_id}",
        ],
        args=[str(followee_id), ts, str(follower_id)]
    )

def reconcile_follower_count(user_id: int):
    """
    Reconciliation job (run nightly or on-demand):
    Set counter to actual count from the graph.
    """
    actual_count = r.zcard(f"followers:{user_id}")
    r.set(f"followers_count:{user_id}", actual_count)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sharding` - social graph data partitioned across shards
- `News Feed Design` - feeds are built on the social graph
  (fan-out from followed accounts)

**Builds On This (learn these next):**
- `Caching` - profile cache, PYMK results, follower lists
- `Distributed Locks` - atomic operations on shared
  graph state (follow/unfollow)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ GRAPH       │ Adjacency list in Redis sorted sets.      │
│             │ following:{id}, followers:{id}, ZSET.    │
├─────────────┼──────────────────────────────────────────┤
  │
│ COUNTERS    │ Redis INCR/DECR. Never COUNT(*) at query. │
│             │ Reconcile with actual count nightly.     │
├─────────────┼──────────────────────────────────────────┤
  │
│ MUTUAL      │ SINTER for small lists (< 5K).           │
│             │ Precompute for large-scale mutual checks. │
├─────────────┼──────────────────────────────────────────┤
  │
│ PYMK        │ Batch job (nightly). 2-hop BFS.          │
│             │ Store top-50 in pymk:{id} sorted set.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ CELEBRITY   │ > 10K followers: fan-out on read for feed.│
│             │ followers set may be on multiple shards. │
├─────────────┼──────────────────────────────────────────┤
  │
│ FAILURE     │ Counter drift: Lua atomic check+INCR.    │
│             │ Nightly reconciliation job.              │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Redis sorted sets for graph edges;     │
│             │  batch precompute for multi-hop queries" │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ E-Commerce Platform Design               │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Store the social graph as adjacency lists in Redis
   sorted sets (following:{id}, followers:{id}).
   Use Lua scripts for atomic follow/unfollow operations
   that update both directions and counters simultaneously.
2. Never compute multi-hop traversals (2nd-degree
   connections, "people you may know") in real-time.
   Run nightly batch jobs and store precomputed results
   in Redis sorted sets (pymk:{user_id}).
3. Maintain counters (followers_count, following_count)
   as separate Redis keys using INCR/DECR. Reconcile
   with actual set cardinality (ZCARD) nightly to fix
   any drift from missed updates.

**Interview one-liner:**
"Social network: user profiles in Postgres (sharded by user_id). Social graph:
Redis sorted sets - following:{id} and followers:{id}, bidirectional. Counters:
Redis INCR/DECR (avoid COUNT(*) at query time). Follow operation: Lua script
for atomic ZADD + INCR on both sides. Multi-hop graph traversal (PYMK, degree
of separation): never real-time. Run batch jobs nightly to compute 2-hop
suggestions, store top-50 per user in pymk:{id} sorted set. Celebrity accounts:
fans are distributed across shards; their feed is built with fan-out on read.
Nightly reconciliation job fixes counter drift."
