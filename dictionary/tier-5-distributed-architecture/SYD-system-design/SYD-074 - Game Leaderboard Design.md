---
id: SYD-074
title: Game Leaderboard Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-010
used_by: ""
related: SYD-031, SYD-010, SYD-069, SYD-052, SYD-019
tags:
  - architecture
  - leaderboard
  - redis
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 74
permalink: /syd/game-leaderboard-design/
---

# SYD-074 - Game Leaderboard Design

⚡ TL;DR - A leaderboard ranks millions of players by
score in real time. The naive approach (SQL ORDER BY
score LIMIT 100) becomes catastrophic at scale: sorting
10 million rows on every read. The correct approach:
Redis Sorted Sets. A sorted set maintains an ordered
collection of members (player IDs) by score, supporting
O(log N) inserts/updates and O(log N + K) range queries
(top-K players). Key operations: ZADD (add/update score),
ZRANK (get rank of a player), ZRANGE (get top-K players).
For global leaderboards with 100M+ players: partition
by score range (sharding by segment) and merge the top
results at read time.

| #074 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching (System Design), Consistent Hashing | |
| **Related:** | Caching, Consistent Hashing, Cache Invalidation Strategies, Distributed Cache Design, Database Replication (System) | |

---

### 🔥 The Problem This Solves

A mobile game has 50 million active players. Each
player scores points in real time. The game shows:
(1) the global top 100 leaderboard (updated every 5s);
(2) the player's own rank (instantaneous response).
SQL query: `SELECT id, score FROM players ORDER BY score
DESC LIMIT 100` on 50M rows. Even with an index:
O(log N) to find the top entry + O(K) to scan 100 rows.
At 50M concurrent score updates per minute: index
maintenance overwhelms the database. Redis Sorted Set:
ZADD O(log N) for updates, ZRANGE O(log N + K) for top-K.
Redis at 100K ops/second on a single instance: trivial.

---

### 📘 Textbook Definition

**Leaderboard:** A ranked list of players (or entities)
ordered by a score metric, showing relative performance.
May be global (all players) or scoped (friends, region,
weekly).

**Redis Sorted Set (ZSET):** A Redis data structure
mapping members (strings) to scores (float64). Members
are automatically ordered by score. Supports O(log N)
insert/update (ZADD), rank query (ZRANK), and range
query (ZRANGE with WITHSCORES).

**ZADD:** Redis command to add a member with a score,
or update the score of an existing member.
`ZADD leaderboard:global 1500 "player:123"`

**ZRANK:** Get the 0-indexed rank of a member (ascending).
`ZRANK leaderboard:global "player:123"` → 42 (rank 43rd)
`ZREVRANK` for descending (highest score = rank 0).

**ZRANGE:** Get members by rank range.
`ZRANGE leaderboard:global 0 99 WITHSCORES REV`
→ Top 100 players (highest scores first).

**Score sharding:** For leaderboards too large for a
single Redis instance: partition players into score
buckets. Players with scores 0-999 → shard 1; 1000-9999
→ shard 2. Count from higher shards to determine rank.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redis Sorted Set = O(log N) score updates + O(log N + K)
top-K queries. Global leaderboard that updates in
real time for millions of players.

**One analogy:**
> An Olympic medal tally:
>
> Without Redis: stack of index cards sorted by total
> medals. Every new medal: re-sort all 200 cards.
> Slow.
>
> With Redis Sorted Set: a pre-sorted binary tree
> (skip list internally). Add/update a country's
> score: tree re-balances automatically. O(log N).
> Show top 10: read first 10 from sorted tree. O(10).
> Find rank of USA: binary search. O(log N).
>
> The tree maintains sorted order as a side effect of
> insertion - no explicit re-sort needed.

**One insight:**
Redis Sorted Sets use a skip list (not a B-tree or
heap) internally. This gives O(log N) for all key
operations (insert, delete, rank lookup, range query).
Unlike a heap (which gives O(1) max but O(log N) for
arbitrary rank), the skip list gives fast rank queries
for any rank. Unlike a B-tree (which is for disk storage),
the skip list is in-memory and has better cache locality
for sequential range reads. This makes it ideal for
leaderboards where you need both rank lookup (what is
player X's rank?) and range queries (who are ranks
50-100?).

---

### 🔩 First Principles Explanation

**REDIS SORTED SET CORE OPERATIONS:**
```
Data structure internals:
  Skip list: probabilistic data structure.
  O(log N) average for all operations.
  Members ordered by score. Ties broken by
  lexicographic order of member string.

Key operations:
  ZADD leaderboard:global 1500 "player:123"
  → Insert/update player:123 with score 1500.
  → O(log N). N = number of players in set.
  
  ZREVRANK leaderboard:global "player:123"
  → Returns 0-indexed rank in descending order.
  → Rank 0 = highest score. Rank N-1 = lowest.
  → O(log N).
  
  ZRANGE leaderboard:global 0 99 WITHSCORES REV
  → Top 100 players, highest score first.
  → Returns [(player_id, score), ...].
  → O(log N + K) where K=100.
  
  ZSCORE leaderboard:global "player:123"
  → Returns score of player:123.
  → O(1) hash lookup.
  
  ZCARD leaderboard:global
  → Total number of players in leaderboard.
  → O(1).
  
  ZRANGEBYSCORE leaderboard:global 1000 2000
  → All players with scores between 1000-2000.
  → O(log N + K).

Leaderboard types:
  Global: ZADD/ZREVRANK on single key.
  Daily: ZADD leaderboard:2024-01-15 → expire at midnight.
  Weekly: ZADD leaderboard:2024-W03 → expire at week end.
  Friends: ZADD leaderboard:friends:{user_id} (per user).
  Regional: ZADD leaderboard:us-east, leaderboard:eu-west.
```

**SCORE UPDATE FLOW:**
```
Player completes a game. Scores 150 new points.

1. Game server: POST /api/scores
   {player_id: 123, points_earned: 150}

2. Score service:
   a. Update DB (source of truth):
      UPDATE players 
      SET score = score + 150 WHERE id = 123;
      RETURNING new_score → 1650
   
   b. Update Redis:
      ZADD leaderboard:global 1650 "player:123"
      ZADD leaderboard:{daily} 150 "player:123"
      (Note: daily might track incremental points)
   
   c. Optionally: publish event for downstream:
      {player_id: 123, new_score: 1650}

3. Client requests leaderboard:
   GET /api/leaderboard/top100
   
   Leaderboard service:
     ZRANGE leaderboard:global 0 99 WITHSCORES REV
     Returns [(player_id, score), ...] in O(log N + 100)
     
     Enrich with player names (batch DB lookup or cache).

4. Client requests own rank:
   GET /api/leaderboard/rank/123
   
   ZREVRANK leaderboard:global "player:123"
   → Returns rank. O(log N). < 1ms.
```

**NEAR-REAL-TIME LEADERBOARD UPDATE:**
```
Problem: 50M players. Score updates: 1M/second.
Redis single-threaded: handles 100K ops/sec per instance.
1M score updates → need 10 Redis instances (sharded).

But: global leaderboard requires merging 10 shards.
ZRANGE from each shard → merge top-100 → expensive.

Alternative: tiered leaderboard.

Architecture:
  Hot tier (Redis): Top 1% of players (500K).
  Only players in top 1% update the Redis ZSET.
  Others: update DB only (their rank is not on leaderboard).
  
  DB query for own rank (non-top player):
    SELECT COUNT(*) + 1 FROM players 
    WHERE score > {my_score}
    (Or: SELECT rank FROM player_ranks 
         WHERE player_id = 123 - materialized)
    Refreshed hourly via background job.
    
  This reduces Redis write volume dramatically.
  Top 1% of 50M = 500K players.
  500K score updates/second (most updates are non-top).
  Redis handles 500K/second easily on 5 shards.

Leader-follow approximation:
  For rank > 100: show approximate rank.
  "You are in the top 5%" (from DB snapshot hourly).
  Exact rank: Redis ZREVRANK O(log N) for top players.
  Approximate rank: precomputed buckets. 
  (Users don't need to know they're rank 4,523,891
  vs 4,523,892. "Top 10%" is sufficient.)
```

**SHARDING FOR EXTREME SCALE:**
```
Leaderboard: 100M players. One Redis instance: 
  100M entries × ~50 bytes per entry = 5GB.
  Redis can hold this (64GB RAM server).
  But: single-threaded ops at 1M/sec → queue builds up.

Score-range sharding:
  Shard 0: scores 0-999       → ~10M players
  Shard 1: scores 1000-9999   → ~30M players
  Shard 2: scores 10000-99999 → ~50M players
  Shard 3: scores 100000+     → ~10M players
  
Get top 100:
  1. Query shard 3 (highest scores): ZRANGE 0 99 REV
     Got: 80 players (shard 3 has 10M, top 100 = top 100
     of that shard).
     Wait: shard 3 might have more than 100 players with
     high scores. Take top 100 from shard 3.
  2. If shard 3 has < 100 players total:
     Take all from shard 3, then top K from shard 2.
  3. Merge and re-sort the candidates. Return top 100.

More common: virtual node sharding by player_id modulo.
  player_id % 10 → shard 0-9.
  Get top 100 globally: query top 100 from each shard,
  merge 10 × 100 = 1000 candidates, return top 100.
  Merge cost: O(K × S) where K=100, S=10 shards. Fast.
```

---

### 🧪 Thought Experiment

**Daily vs. All-Time Leaderboard**

All-time leaderboard:
  ZADD leaderboard:alltime {total_score} "player:{id}"
  Score accumulates indefinitely.
  Player added once; score updated on each game.
  
Daily leaderboard:
  Key: leaderboard:daily:{YYYYMMDD}
  ZADD leaderboard:daily:20240115 {daily_score} "player:{id}"
  EXPIRE leaderboard:daily:20240115 86400 × 2 (2 days TTL)
  
  Reset: TTL handles cleanup automatically.
  Daily score: only points earned today.
  
  Problem: how to compute "daily score" atomically?
  Player's last daily score must be tracked.
  
  ZADD with INCR flag:
    ZADD leaderboard:daily:20240115 INCR 150 "player:123"
    → Atomically increments player's daily score by 150.
    → Returns new daily score (e.g., 450).
    → No race condition on concurrent score updates.

Weekly leaderboard:
  Key: leaderboard:weekly:{year}:W{week_num}
  Same ZADD + INCR pattern.
  TTL: 14 days.

Friends leaderboard:
  Key: leaderboard:friends:{user_id}
  Members: user_id's friends.
  Populated: when user adds a friend, add to set.
  Score: same score as global leaderboard.
  
  Fan-out on friend add (expensive for high-follower users):
    On friend add: ZADD leaderboard:friends:{user_id}
                   {friend_score} "player:{friend_id}"
  
  Read: ZRANGE leaderboard:friends:{user_id} 0 9 REV
  → Top 10 friends by score.

---

### 🧠 Mental Model / Analogy

> A leaderboard is like a sorted phone book (by rank):
>
> Phone book (sorted by name = insertion order).
> Leaderboard (sorted by score = dynamic order).
>
> Adding a new entry: find the right position, insert.
> Finding rank of an entry: binary search.
> Top-10 entries: read first 10 pages.
>
> Redis Sorted Set = highly optimized sorted phone book.
> Updates and queries both O(log N).
> In-memory: microsecond response times.
> Phone book: can't do this in-memory for 50M entries.
> Redis: 50M entries = ~2.5GB RAM. Easily fits.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A leaderboard ranks players by their score. The
challenge: updating ranks instantly when scores
change, and looking up any player's rank quickly.
Redis is used because it keeps a sorted list in memory,
making both operations very fast.

**Level 2 - How to use it (junior developer):**
Use Redis Sorted Set. ZADD to update scores, ZREVRANK
to get a player's rank, ZRANGE with REV to get top-K.
Keep a SQL database as the source of truth for scores
(Redis is a cache). Expire daily/weekly leaderboard
keys using TTL. Batch-enrich player names after
fetching leaderboard from Redis.

**Level 3 - How it works (mid-level engineer):**
Redis Sorted Set: skip list internally, O(log N) all
operations. ZADD with INCR: atomic increment (no race
condition). Score update: write to SQL first, then ZADD
to Redis. Player rank: ZREVRANK in O(log N). Top-100:
ZRANGE O(log N + 100). For multiple leaderboard types:
separate ZSET keys per scope (global, daily, weekly,
friends). Daily leaderboard: key per day with TTL.
Sharding for scale: score-range or modulo sharding.

**Level 4 - Why it was designed this way (senior/staff):**
Why a skip list and not a B-tree or binary heap for
sorted sets? Heaps: O(1) for max/min, but O(N) for
arbitrary rank queries (must scan). B-trees: O(log N)
for all operations but have poor cache locality in
sequential reads (pointer chasing). Skip lists: O(log N)
for all operations, good cache locality for sequential
access (level-0 of skip list is a linked list = cache-
friendly scan for ZRANGE). Additionally, skip lists
are simpler to implement with lock-free concurrency
(important for Redis's single-threaded+pipeline model).
The key insight: leaderboards need both random rank
access (ZRANK) and sequential range access (ZRANGE).
Skip lists excel at both.

**Level 5 - Mastery (distinguished engineer):**
Riot Games (League of Legends) published their leaderboard
architecture at 100M+ players. Key challenge: combining
a global leaderboard with friends leaderboard efficiently.
Naive approach: maintain a separate ZSET per user of
their friends (fan-out-on-write). For users with 1M
followers, every score update requires 1M ZADD operations.
Their solution: fan-out-on-read. A user's friends
leaderboard is computed at read time by querying
friends' scores from the global leaderboard. This is
O(num_friends × log N) per read. For typical users
(100-500 friends): fast. For celebrity accounts:
precompute and cache. The hybrid approach: precompute
friends leaderboards for users with > 10K friends;
compute-on-read for everyone else.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ LEADERBOARD SYSTEM                                  │
│                                                      │
│ Score update:                                       │
│   Game server → Score API                         │
│   Score API → DB UPDATE score = score + pts       │
│   Score API → ZADD leaderboard:global {score} {id}│
│   Score API → ZADD leaderboard:daily INCR pts {id}│
│                                                      │
│ Top 100 read:                                       │
│   API → Redis ZRANGE leaderboard:global 0 99 REV  │
│   Redis → [(id1, score1), ..., (id100, score100)] │
│   API → batch DB lookup: player names, avatars    │
│   → Return enriched leaderboard                   │
│                                                      │
│ Player rank:                                        │
│   API → ZREVRANK leaderboard:global "player:123"  │
│   → returns 0-indexed rank (add 1 for display)   │
│   Response: < 1ms (in-memory skip list lookup)   │
│                                                      │
│ Daily cleanup:                                      │
│   Key: leaderboard:daily:YYYYMMDD                 │
│   EXPIRE set to midnight UTC                      │
│   (or: cron job at 00:00 UTC to RENAME and EXPIRE)│
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Redis leaderboard operations (Python)**
```python
import redis
from datetime import datetime, timezone
from typing import List, Tuple

r = redis.Redis(
    host='redis.internal', port=6379,
    decode_responses=True)

GLOBAL_LB = "leaderboard:global"

def update_score(player_id: int, points_earned: int):
    """
    Update player score in both DB and Redis.
    Atomic increment in Redis (ZADD INCR flag).
    """
    # 1. Update source of truth (DB)
    new_score = db.execute(
        "UPDATE players "
        "SET total_score = total_score + %s "
        "WHERE id = %s RETURNING total_score",
        [points_earned, player_id]
    )['total_score']
    
    # 2. Update global leaderboard (absolute score)
    r.zadd(GLOBAL_LB, {f"player:{player_id}": new_score})
    
    # 3. Update daily leaderboard (incremental)
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    daily_key = f"leaderboard:daily:{today}"
    r.zadd(daily_key, {f"player:{player_id}": points_earned},
           incr=True)  # Atomic increment: no race condition
    # Set TTL: 48 hours (covers date boundary edge cases)
    r.expire(daily_key, 48 * 3600)
    
    return new_score

def get_top_players(
        n: int = 100,
        leaderboard: str = GLOBAL_LB
) -> List[dict]:
    """
    Get top N players from leaderboard.
    Returns list of {rank, player_id, score}.
    """
    # ZRANGE with REV=True returns highest scores first
    results: List[Tuple[str, float]] = r.zrange(
        leaderboard, 0, n - 1,
        withscores=True,
        rev=True  # highest score first
    )
    
    # Extract player IDs for batch DB enrichment
    player_ids = [int(m.split(":")[1]) for m, _ in results]
    
    # Batch fetch player names/avatars
    players = db.query(
        "SELECT id, username, avatar_url "
        "FROM players WHERE id = ANY(%s)",
        [player_ids]
    )
    player_map = {p['id']: p for p in players}
    
    return [
        {
            "rank": rank + 1,
            "player_id": player_ids[rank],
            "username": player_map.get(
                player_ids[rank], {}).get('username'),
            "score": score
        }
        for rank, (member, score) in enumerate(results)
    ]

def get_player_rank(player_id: int,
                    leaderboard: str = GLOBAL_LB
                    ) -> dict:
    """
    Get a player's rank and score.
    O(log N). < 1ms response time.
    """
    member = f"player:{player_id}"
    
    # 0-indexed rank in descending order (0 = highest)
    rank = r.zrevrank(leaderboard, member)
    score = r.zscore(leaderboard, member)
    total_players = r.zcard(leaderboard)
    
    if rank is None:
        return {"rank": None,
                "score": 0,
                "percentile": 0}
    
    percentile = round(
        (1 - rank / total_players) * 100, 1)
    
    return {
        "rank": rank + 1,  # Convert to 1-indexed
        "score": score,
        "total_players": total_players,
        "percentile": percentile  # e.g., "top 0.1%"
    }

def get_surrounding_players(
        player_id: int,
        radius: int = 5) -> List[dict]:
    """
    Get players ranked just above and below a player.
    (e.g., "You are rank 1,423. Nearby players:")
    """
    member = f"player:{player_id}"
    rank = r.zrevrank(GLOBAL_LB, member)
    if rank is None:
        return []
    
    start = max(0, rank - radius)
    end = rank + radius
    
    results = r.zrange(
        GLOBAL_LB, start, end,
        withscores=True, rev=True
    )
    
    return [
        {
            "rank": start + i + 1,
            "player_id": int(m.split(":")[1]),
            "score": score,
            "is_self": m == member
        }
        for i, (m, score) in enumerate(results)
    ]
```

**Example 2 - Friends leaderboard (fan-out on write)**
```python
def on_friend_added(user_id: int, friend_id: int):
    """
    When user_id adds friend_id:
    Add friend's score to user's friends leaderboard.
    Also add user's score to friend's friends leaderboard.
    """
    friends_lb_user = f"leaderboard:friends:{user_id}"
    friends_lb_friend = f"leaderboard:friends:{friend_id}"
    
    # Get current scores from global leaderboard
    friend_score = r.zscore(GLOBAL_LB,
                             f"player:{friend_id}") or 0
    user_score = r.zscore(GLOBAL_LB,
                          f"player:{user_id}") or 0
    
    # Add each other to each other's friends boards
    r.zadd(friends_lb_user,
           {f"player:{friend_id}": friend_score})
    r.zadd(friends_lb_friend,
           {f"player:{user_id}": user_score})

def on_score_update(player_id: int, new_score: float):
    """
    On score update: update in all friends leaderboards.
    BAD for users with many friends (fan-out amplification).
    Consider compute-on-read for users with > 10K friends.
    """
    member = f"player:{player_id}"
    
    # Get all users who have this player as a friend
    # (stored in a separate set per player)
    friend_of_set = f"friend_of:{player_id}"
    fans = r.smembers(friend_of_set)  # Could be huge
    
    pipeline = r.pipeline()
    for fan_id in fans:
        pipeline.zadd(
            f"leaderboard:friends:{fan_id}",
            {member: new_score}
        )
    pipeline.execute()  # Batch Redis operations
    # Warning: if len(fans) = 1M, this is 1M ZADD ops.
    # Limit: fan-out-on-write only for < 10K fans.
    # For > 10K: compute leaderboard on read.
```

---

### ⚖️ Comparison Table

| Approach | Top-K Query | Rank Lookup | Score Update | Scale |
|---|---|---|---|---|
| **SQL ORDER BY** | O(N log N) scan | O(N) count query | O(log N) index | Poor for read-heavy |
| **Redis Sorted Set** | O(log N + K) | O(log N) | O(log N) | 100K ops/sec per instance |
| **Materialized view (SQL)** | O(K) | O(1) | Write overhead | Good if refresh acceptable |
| **Redis + Score sharding** | O(log N + K × S) | O(log N + S) | O(log N × S) | Near-infinite |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SQL can handle leaderboard queries at scale | `SELECT rank() OVER (ORDER BY score DESC)` for every page view on 50M players requires scanning the entire players table or maintaining a large index. At 100 requests/second for the leaderboard: 100 full-table window function computations per second. Even with a covering index, 50M rows sorted for every request is unsustainable. Redis Sorted Set pushes this to O(log N + K) per read. The read path is the critical path. |
| Redis Sorted Set scores must be integers | Redis Sorted Set scores are float64 (double precision). Scores can be any floating-point number (including integers stored as floats). For games, integer scores are typical. For ranking by time (e.g., fastest completion), float scores work perfectly. Important: float64 has limited precision (15-16 significant decimal digits). For very large integer scores (> 2^53), use score normalization or string keys. |
| A single Redis instance is a single point of failure | Use Redis Sentinel (automatic failover) or Redis Cluster (horizontal sharding + HA). For leaderboards: Redis Cluster with 3 master + 3 replica shards provides both horizontal scale and high availability. If a master fails: replica is promoted in < 30 seconds. For read-heavy leaderboards: route read requests to replicas, write to master. |

---

### 🚨 Failure Modes & Diagnosis

**Redis Memory Exhaustion: Leaderboard OOM**

**Symptom:**
Redis starts evicting keys. Leaderboard data becomes
incomplete. Some players lose their rank. Memory usage:
96% of Redis maxmemory. OOM errors in Redis logs.

**Root Cause:**
Friends leaderboards created per-user are never
cleaned up. Each user has a ZSET for their friends.
100M users × 100 friends × 50 bytes = 500GB. Redis
runs out of memory. Evicts keys with LRU/LFU policy.
Friends leaderboard keys are evicted = stale data.

**Fix:**
```python
# Diagnosis: find large ZSET keys
# Redis CLI: memory profiling

# Find top 20 largest keys by memory usage:
# redis-cli --bigkeys -n 0 -i 0.01 | head -50

# Count keys by pattern:
# redis-cli --scan --pattern "leaderboard:friends:*" 
# | wc -l

# Fix 1: Set TTL on friends leaderboards
def get_or_build_friends_leaderboard(user_id: int):
    key = f"leaderboard:friends:{user_id}"
    
    if not r.exists(key):
        # Build on demand (compute on read)
        friend_ids = db.query(
            "SELECT friend_id FROM friendships "
            "WHERE user_id = %s",
            [user_id])
        
        scores = {}
        for row in friend_ids:
            score = r.zscore(GLOBAL_LB,
                             f"player:{row['friend_id']}")
            if score:
                scores[f"player:{row['friend_id']}"] = score
        
        if scores:
            r.zadd(key, scores)
        
        # Expire after 10 minutes (rebuilt on next access)
        r.expire(key, 600)
    
    return r.zrange(key, 0, 9,
                    withscores=True, rev=True)

# Fix 2: Set maxmemory-policy to allkeys-lfu
# (evict least frequently used keys when memory full)
# redis.conf: maxmemory-policy allkeys-lfu
# This automatically evicts cold friends leaderboards.
# Hot (active user) leaderboards: retained.
# Cold (inactive) leaderboards: evicted, rebuilt on access.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching (System Design)` - Redis is the core
  technology; caching fundamentals apply
- `Consistent Hashing` - sharding Redis instances
  for a global leaderboard at extreme scale

**Builds On This (learn these next):**
- `Cache Invalidation Strategies` - ensuring leaderboard
  data stays consistent with the source of truth (DB)
- `Distributed Cache Design` - Redis cluster setup,
  replica reads, HA configuration for leaderboard
- `Database Replication (System)` - score updates
  must be durable in DB; Redis is the read layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DATA STRUCT │ Redis Sorted Set (ZSET). Skip list.       │
│             │ O(log N) all operations.                 │
├─────────────┼──────────────────────────────────────────  │
│ KEY OPS     │ ZADD: update score (or INCR for daily).  │
│             │ ZREVRANK: player's rank. O(log N).       │
│             │ ZRANGE REV: top-K. O(log N + K).        │
├─────────────┼──────────────────────────────────────────  │
│ MULTI-SCOPE │ Global: one ZSET.                        │
│             │ Daily: ZSET with TTL. ZADD with INCR.   │
│             │ Friends: ZSET per user (with TTL).      │
├─────────────┼──────────────────────────────────────────  │
│ SOURCE TRUTH│ DB = truth. Redis = leaderboard cache.  │
│             │ Score update: DB first, then ZADD.      │
├─────────────┼──────────────────────────────────────────  │
│ SCALE       │ Top 1%: Redis. Others: DB rank (hourly).│
│             │ Redis Cluster for > 100M players.       │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Redis ZADD + ZREVRANK + ZRANGE.        │
│             │  DB source of truth. TTL for daily."   │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Booking and Reservation System Design    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Redis Sorted Set: ZADD to update scores (O(log N)),
   ZREVRANK to get a player's rank (O(log N)), ZRANGE
   with REV to get top-K players (O(log N + K)).
   All in-memory = microsecond latency. SQL ORDER BY
   on millions of rows is catastrophically slow for this.
2. DB is source of truth. Redis is the read cache.
   Score update: write to DB first, then ZADD to Redis.
   If Redis fails: rebuild from DB. If DB has the score
   but Redis doesn't, the score is not lost.
3. Daily leaderboard: separate ZSET key per day with TTL.
   Use ZADD with INCR flag to atomically add today's
   points without a read-modify-write race condition.

**Interview one-liner:**
"Leaderboard: Redis Sorted Set (skip list, O(log N) all operations). Score update:
DB first (source of truth), then ZADD to Redis. Top-100: ZRANGE 0 99 WITHSCORES REV
O(log N + 100). Player rank: ZREVRANK O(log N) < 1ms. Daily: separate ZSET key
(leaderboard:daily:YYYYMMDD) with TTL, ZADD INCR for atomic increment. Friends
leaderboard: ZSET per user with TTL (compute-on-read for inactive users).
Scale to 100M+ players: top 1% in Redis, approximate rank from DB for everyone
else (hourly materialized view). Redis Cluster for horizontal sharding."
