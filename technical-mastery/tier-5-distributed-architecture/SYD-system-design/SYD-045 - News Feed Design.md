---
id: SYD-045
title: News Feed Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-035, SYD-031
used_by: ""
related: SYD-035, SYD-031, SYD-008, SYD-036
tags:
  - architecture
  - social
  - feed
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/syd/news-feed-design/
---

⚡ TL;DR - A news feed aggregates posts from accounts
a user follows into a ranked, paginated timeline. Two
fundamental architectures: fan-out on write (pre-compute
each follower's feed on post creation - fast reads, slow
writes, expensive for celebrities) vs fan-out on read
(compute the feed on each request - fast writes, slow
reads, expensive at large scale). Production systems
use a hybrid: fan-out on write for regular users, fan-out
on read for celebrity accounts (high follower count).

| #045 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Fan-Out on Write vs Read, Sharding | |
| **Related:** | Fan-Out, Sharding, Caching, Push vs Pull Architecture | |

---

### 🔥 The Problem This Solves

Twitter has 500M users. A user follows 300 accounts.
When they open the app, they expect to see the latest
posts in < 200ms. A celebrity has 100M followers.
When the celebrity posts, the system must somehow make
that post appear in 100M feeds quickly.

**Naive approach fails both ways:**
- Pre-compute all feeds on every post: celebrity post
  triggers 100M write operations. Database cannot keep up.
- Compute feeds on read: user's feed requires querying
  300 followed accounts' posts, sorting by time, ranking -
  all in real-time. Hundreds of DB queries per feed load.

---

### 📘 Textbook Definition

**News feed:** A personalized, chronologically (or
algorithmically) ordered list of posts from accounts
a user follows, served when the user opens the
application.

**Core design decisions:**
1. **Fan-out strategy:** When to aggregate posts into
   feeds (on write vs on read vs hybrid).
2. **Storage:** Where to store feed entries (dedicated
   feed store, cache, or computed on-the-fly).
3. **Ranking:** Simple reverse-chronological vs ML-based
   ranking (engagement prediction, freshness, diversity).
4. **Pagination:** Cursor-based (stable across new posts)
   vs offset-based (simple but skips posts on page 2+).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Aggregate posts from N followed accounts → rank → serve
as a paginated timeline to each user.

**One analogy:**
> A physical newspaper:
>
> Fan-out on write = printing a personalized newspaper
> for each reader at 5am. Each reader's paper is ready
> instantly when they want it. But printing 1M personalized
> papers is expensive, and if a celebrity is added to
> the front page (celebrity post), ALL 1M papers must
> be reprinted.
>
> Fan-out on read = a shared newspaper rack. Each reader
> assembles their own paper by picking sections they want.
> No pre-printing cost, but each reader spends 10 minutes
> assembling their paper every time.
>
> Hybrid = pre-print for regular subscribers, assemble-on-
> demand for the celebrity supplement (added by 100M
> subscribers who each pick it up separately).

**One insight:**
The celebrity problem is the critical design insight.
Accounts with millions of followers make fan-out on write
impractical (100M writes per post). Accounts with few
followers make fan-out on read expensive (compute feed
from 1,000 follows every 30 seconds as the user scrolls).
Production systems split by follower count threshold.

---

### 🔩 First Principles Explanation

**FAN-OUT ON WRITE (PUSH MODEL):**
```
When User A posts:
  1. Write post to Posts table
  2. Fetch all followers of User A
  3. For each follower, write post_id to their feed
  
Feed store entry: {user_id, post_id, timestamp}

Read path:
  Load user's feed: SELECT post_id FROM feed
    WHERE user_id = X ORDER BY timestamp DESC
    LIMIT 20
  → 1 query, pre-sorted, fast
  
Problem: User A has 10M followers:
  10M write operations per post
  Writing to 10M feed entries at peak: 
    200K posts/day × 10M followers = 2 trillion
    feed writes/day - not feasible for all accounts
```

**FAN-OUT ON READ (PULL MODEL):**
```
When user opens their feed:
  1. Fetch list of accounts they follow
  2. For each followed account, query their latest posts
  3. Merge all posts, sort by timestamp
  4. Apply ranking
  5. Return top 20

Problem: User follows 500 accounts:
  500 DB queries per feed load
  100ms × 500 serial queries = 50 seconds
  Even parallel: fan-out to 500 queries per request
  Database load: proportional to active users × follows
  Very expensive at scale
```

**HYBRID MODEL (production approach):**
```
On post creation:
  if poster.follower_count <= 10_000:
    # Fan-out on write: push to follower feeds
    for follower in poster.followers:
      write_to_feed_cache(follower.id, post.id)
  else:
    # Celebrity: don't push to feeds
    # Only write post to posts table
    pass

On feed load:
  # Core feed: from pre-computed cache
  feed = read_feed_cache(user_id, limit=20)
  
  # Celebrity posts: inject in real-time
  celebrities = get_followed_celebrities(user_id)
  for celeb in celebrities:
    recent_posts = get_recent_posts(celeb.id, limit=3)
    feed.extend(recent_posts)
  
  # Merge and rank all posts
  feed.sort(key=ranking_score, reverse=True)
  return feed[:20]

Result:
  - Regular users: fast reads (pre-computed)
  - Celebrities: fan-out avoided (pulled on read)
  - Complexity: must track which accounts are
    "celebrities" and update when thresholds change
```

---

### 🧪 Thought Experiment

**SIZING: Design a news feed at Twitter scale**

Users: 500M registered, 100M daily active (DAU)
Average follows: 300 per user
Average posting rate: 500M tweets/day = 5,787 tweets/sec
Read:write = 100:1 (feeds read much more than posted)
Feed reads: 100M DAU × 10 feed loads/day = ~11,574/sec

**Fan-out on write writes/second:**
5,787 tweets/sec × avg 300 followers = 1.7M feed
writes/second. Feasible with a distributed feed store
(Redis Cluster or Cassandra), but only for non-celebrity
accounts (< 10K followers).

**Celebrity threshold impact:**
0.01% of accounts (500K) have > 10K followers.
Those 500K accounts generate: 5,787 × 0.01% = ~0.6
tweets/sec from celebrities. With 10M avg followers for
celebrities: 0.6 × 10M = 6M fan-out writes/sec if we
pushed them. Too high. Fan-out on read for celebrities:
each of 100M daily users checks ~10 celebrity accounts
= 1B celebrity post lookups/day. Manageable with cache.

**Feed storage:**
100M active users × 1,000 feed entries × 8 bytes (post_id)
= 800GB. Fits in Redis Cluster.
TTL: evict feeds not accessed in 24 hours.
Cold users: recompute feed from follows on next visit.

---

### 🧠 Mental Model / Analogy

> Think of a news feed system like a postal service:
>
> Fan-out on write = direct mail: for every letter sent,
> print and mail a copy to each of the sender's subscribers.
> Fast delivery (already in mailbox). But a celebrity
> sender with 1M subscribers = 1M envelopes to print,
> address, and mail per letter.
>
> Fan-out on read = a public notice board. Letters go to
> a central board. Each subscriber checks the board for
> letters from people they follow. No printing overhead,
> but each check is expensive (must search the entire board).
>
> Hybrid = magazine subscription model: pre-print and mail
> for regular contributors (manageable volume). But for
> national newspapers (celebrities), subscribers pick
> them up at the newsstand (read on demand from a shared
> source - the posts table).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A news feed shows you the latest posts from people you
follow. When you follow someone, their new posts appear
in your feed. The system must show you these posts quickly
even if millions of other users follow the same person.

**Level 2 - How to use it (junior developer):**
Two approaches: (1) When someone posts, write to each
follower's feed cache. Feed reads are fast (pre-sorted).
(2) Compute the feed on each read by querying all
followed accounts. Reads are flexible but expensive.

**Level 3 - How it works (mid-level engineer):**
Hybrid model: fan-out on write for regular users (push
post_id to each follower's feed in Redis). For celebrity
accounts (> threshold followers), skip fan-out. On feed
read: load pre-computed feed from cache, then merge in
celebrity posts queried in real-time. Sort and rank the
merged result. Use cursor-based pagination for stability.

**Level 4 - Why it was designed this way (senior/staff):**
The threshold between "regular" and "celebrity" is not
static. As an account gains followers, it transitions
from fan-out on write to fan-out on read dynamically.
This transition must be managed: when an account crosses
the threshold, existing feeds must be retroactively
cleaned (or left to expire naturally). Ranking adds
complexity: ML ranking models run asynchronously; the
feed served from cache is scored by freshness + predicted
engagement. Real-time ranking on every feed load would
add 100-200ms per request.

**Level 5 - Mastery (distinguished engineer):**
The news feed at Meta/Twitter scale is not just a data
aggregation problem. The ranking model is trained on
user behavior (clicks, shares, time spent) and updated
hourly. Feature engineering requires low-latency feature
stores (pre-computed engagement metrics per post, per-
user relationship strength). The feed is not just "posts
from follows" - it includes recommendations, ads, and
re-shares. Operational challenge: when a major celebrity
with 100M followers deletes a post, you must remove it
from feeds cached in 100M Redis entries - fan-out delete
is even more expensive than fan-out write. Solution:
tombstone (mark deleted in the posts table, filter at
read time) rather than deleting from each feed cache.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ HYBRID NEWS FEED                                    │
│                                                      │
│ WRITE PATH (post creation):                         │
│                                                      │
│  User posts ──► Post Service                       │
│  ──► Save to Posts DB                              │
│  ──► Check follower count                          │
│       < 10K? ──► Fan-out: write post_id to each    │
│                  follower's feed in Redis Cluster   │
│       > 10K? ──► Skip fan-out (celebrity mode)     │
│                  Post saved to Posts DB only        │
│                                                      │
│ READ PATH (load feed):                              │
│                                                      │
│  User requests feed ──► Feed Service               │
│  ──► Load pre-computed feed from Redis (20 IDs)    │
│  ──► Identify followed celebrities from             │
│       Celebrity Registry                            │
│  ──► Fetch last 3-5 posts from each celebrity      │
│       (Posts DB or celebrity post cache)            │
│  ──► Merge regular feed + celebrity posts          │
│  ──► Apply ranking (freshness + engagement score)  │
│  ──► Return top 20, cursor for next page            │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Hybrid feed generation (Python pseudocode)**
```python
import redis
import json
from typing import List, Dict

r = redis.Redis()
CELEBRITY_THRESHOLD = 10_000

def on_post_created(user_id: int, post_id: int,
                     ts: float):
    """Called when a user creates a new post."""
    # Always store in Posts DB
    save_post_to_db(user_id, post_id, ts)

    follower_count = get_follower_count(user_id)

    if follower_count <= CELEBRITY_THRESHOLD:
        # Fan-out on write: push to follower feeds
        followers = get_followers(user_id)  # up to 10K
        pipe = r.pipeline()
        for follower_id in followers:
            feed_key = f"feed:{follower_id}"
            # Sorted set: score=timestamp, member=post_id
            pipe.zadd(feed_key, {str(post_id): ts})
            # Keep only latest 1000 posts in feed
            pipe.zremrangebyrank(feed_key, 0, -1001)
            # TTL: discard feeds not accessed in 24h
            pipe.expire(feed_key, 86400)
        pipe.execute()

def get_feed(user_id: int, cursor: float = None,
              limit: int = 20) -> Dict:
    """Load and merge feed for user."""
    feed_key = f"feed:{user_id}"

    # Fetch pre-computed feed (most recent 20 entries)
    # Sorted set: ZREVRANGEBYSCORE (newest first)
    max_score = cursor if cursor else "+inf"
    post_ids = r.zrevrangebyscore(
        feed_key, max_score, "-inf",
        start=0, num=limit, withscores=True
    )

    # Fetch celebrity posts (fan-out on read)
    followed_celebrities = get_followed_celebrities(
        user_id)  # Users with > CELEBRITY_THRESHOLD
    celeb_posts = []
    for celeb_id in followed_celebrities:
        # Recent posts from celebrity's own timeline
        recent = get_user_recent_posts(celeb_id, n=3)
        celeb_posts.extend(recent)

    # Merge: combine pre-computed + celebrity posts
    all_post_ids = [
        (int(pid), score) for pid, score in post_ids
    ] + celeb_posts

    # Deduplicate (user may follow a non-celebrity
    # who re-shared a celebrity post)
    seen = set()
    unique_posts = []
    for pid, score in sorted(
        all_post_ids, key=lambda x: x[1], reverse=True
    ):
        if pid not in seen:
            seen.add(pid)
            unique_posts.append((pid, score))

    # Rank (simplified: freshness score)
    ranked = sorted(
        unique_posts[:limit * 2],
        key=lambda x: ranking_score(x[0], x[1]),
        reverse=True
    )[:limit]

    # Cursor for next page: lowest timestamp seen
    next_cursor = ranked[-1][1] - 0.001 if ranked else None

    return {
        "posts": [fetch_post(pid) for pid, _ in ranked],
        "next_cursor": next_cursor,
    }
```

**Example 2 - Celebrity threshold anti-pattern (fan-out for all)**
```python
# BAD: Fan-out on write for ALL accounts
def on_post_created_bad(user_id: int, post_id: int):
    followers = get_followers(user_id)  # Could be 100M!
    for follower_id in followers:
        # 100M Redis writes for a single celebrity post
        r.zadd(f"feed:{follower_id}", {post_id: time.time()})
    # Result: system is unavailable for minutes after
    # a celebrity posts during peak hours

# GOOD: Hybrid approach (see on_post_created above)
# Check follower count before deciding to fan-out.
# Mark accounts as "celebrity" in a registry.
# Read celebrity posts on demand at feed load time.
```

---

### ⚖️ Comparison Table

| Strategy | Write Cost | Read Cost | Best For | Celebrity Problem |
|---|---|---|---|---|
| **Fan-out on write** | High (N writes per post) | Low (1 cache lookup) | Small follower counts | Catastrophic |
| **Fan-out on read** | Low (1 DB write) | High (N queries per read) | Celebrity accounts | None |
| **Hybrid** | Medium (N writes for regular) | Low-Medium | All scales | Solved |
| **Pull from follows** | None (no fan-out) | Highest (N parallel queries) | Prototype only | None |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Fan-out on write is always better for read performance | At celebrity scale (100M followers), fan-out on write generates 100M writes per post, exhausting write capacity. The read benefit (1 cache lookup) does not justify this write cost. Hybrid is necessary. |
| Feed ordering should always be reverse-chronological | Reverse-chronological is simple but not optimal for engagement. ML ranking (predicting what the user is most likely to engage with) consistently outperforms chronological ordering in A/B tests at platforms like Facebook and Instagram. The trade-off: ML ranking requires feature computation and model inference, adding latency and complexity. |
| The celebrity threshold is a fixed number | The threshold should be dynamic based on system capacity. During traffic spikes, you may lower the threshold (more accounts treated as celebrities, less fan-out). During low traffic, raise it. Make it a tunable parameter, not a hardcoded constant. |

---

### 🚨 Failure Modes & Diagnosis

**Feed Out of Sync After Unfollow**

**Symptom:**
User unfollows a celebrity account. After unfollowing,
posts from the celebrity still appear in the user's feed
for several minutes/hours. Other users complain that
"unfollowed" accounts still appear in their feeds.

**Root Cause:**
Fan-out on write populated the user's feed cache in
Redis. On unfollow, the post_ids from the unfollowed
account are still in the feed's sorted set. They expire
naturally (24h TTL), but interim they appear in feeds.

**Fix:**
```python
def on_unfollow(follower_id: int, unfollowed_id: int):
    # Remove unfollowed user's posts from follower's feed
    feed_key = f"feed:{follower_id}"
    
    # Fetch recent post_ids from unfollowed user
    recent_posts = get_user_recent_posts(
        unfollowed_id, n=1000)  # Posts in feed window
    
    if recent_posts:
        # Remove all their post_ids from the feed sorted set
        pipe = r.pipeline()
        for post_id in recent_posts:
            pipe.zrem(feed_key, str(post_id))
        pipe.execute()
    
    # Update celebrity registry if needed
    update_follow_graph(follower_id, unfollowed_id,
                         action="unfollow")

# Alternative: use tombstoning
# Mark relationship as "unfollowed" in follow graph.
# At feed read time, filter out posts from unfollowed
# accounts. Slower read but simpler write-side logic.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Fan-Out on Write vs Read` - the core design trade-off
  that news feed is built around
- `Sharding` - feed storage must be sharded by user_id

**Builds On This (learn these next):**
- `Push vs Pull Architecture` - fan-out on write is push;
  fan-out on read is pull
- `Caching` - Redis sorted sets as feed store

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE CHOICE │ Fan-out write (push) vs read (pull).      │
│             │ Production: hybrid by follower count.    │
├─────────────┼──────────────────────────────────────────┤
  │
│ HYBRID RULE │ follower_count <= 10K: fan-out on write  │
│             │ follower_count > 10K: fan-out on read    │
├─────────────┼──────────────────────────────────────────┤
  │
│ FEED STORE  │ Redis sorted set: key=feed:{user_id}     │
│             │ score=timestamp, member=post_id          │
├─────────────┼──────────────────────────────────────────┤
  │
│ READ MERGE  │ Pre-computed feed + celebrity posts,     │
│             │ ranked by freshness + engagement score   │
├─────────────┼──────────────────────────────────────────┤
  │
│ PAGINATION  │ Cursor-based (ZREVRANGEBYSCORE with      │
│             │ max_score). Stable when new posts added. │
├─────────────┼──────────────────────────────────────────┤
  │
│ FAILURE     │ Unfollow: ZREM unfollowed user's posts   │
│             │ from feed cache immediately on unfollow  │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Fan-out write for regular users,       │
│             │  fan-out read for celebrities, merge    │
│             │  at read time. Redis sorted sets."      │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ Search Autocomplete → Notification System│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Fan-out on write (push post_id to each follower's
   feed cache) is fast for reads but breaks down for
   celebrity accounts with millions of followers. The
   hybrid: fan-out on write for accounts under a
   threshold (e.g., 10K followers), fan-out on read
   for celebrities (merge at read time).
2. Store feeds in Redis sorted sets keyed by user_id.
   Score = timestamp (enables ZREVRANGEBYSCORE for
   cursor pagination). Keep only the latest 1,000 post
   IDs per feed (ZREMRANGEBYRANK on write). Expire
   feeds after 24 hours of inactivity.
3. Pagination should be cursor-based (not offset-based).
   Offset pagination skips posts when new content is
   added between page loads. Cursor (timestamp of the
   last seen post) stays stable.

**Interview one-liner:**
"News feed design: hybrid fan-out. Threshold (e.g., 10K followers):
below → fan-out on write (push post_id to each follower's Redis sorted
set feed). Above (celebrities) → fan-out on read (skip write-time push;
merge celebrity posts at read time). Feed store: Redis sorted sets,
score=timestamp, member=post_id. Read: load pre-computed feed + merge
celebrity posts + rank by freshness/engagement. Cursor pagination
(ZREVRANGEBYSCORE) for stable scrolling. On unfollow: ZREM unfollowed
user's post_ids from the feed cache to prevent stale posts appearing."
