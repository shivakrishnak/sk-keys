---
id: SYD-007
title: News Feed Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-059, SYD-063
used_by: SYD-071
related: SYD-059, SYD-058, SYD-051
tags:
  - architecture
  - design
  - advanced
  - caching
  - scalability
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /syd/news-feed-design/
---

# SYD-065 - News Feed Design

⚡ TL;DR - A news feed aggregates content from followed accounts and presents it ranked by relevance or time - the core challenge is fanout strategy at scale when celebrities have millions of followers.

| SYD-065         | Category: System Design       | Difficulty: ★★★ |
| :-------------- | :---------------------------- | :-------------- |
| **Depends on:** | SYD-059, SYD-063              |                 |
| **Used by:**    | SYD-071                       |                 |
| **Related:**    | SYD-059, SYD-058, SYD-051    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A social network stores posts. When a user opens their feed, the app queries every followed account's posts and merges them in reverse-chronological order. For a user following 500 accounts who each post 10 times/day, that is 500 queries and 5,000 result rows to merge - every single time the feed is opened.

**THE BREAKING POINT:**
Naive feed generation does not scale. At 100M users each opening their feed 10 times/day, the query load is astronomical. Worse: a celebrity with 5M followers posting once forces 5M feed updates. If done synchronously, the celebrity's post takes 5 million DB writes before the API responds.

**THE INVENTION MOMENT:**
Pre-compute feeds. On post creation, fan out the post to each follower's feed cache (fan-out on write). When the user opens their feed, simply read their pre-computed cache (fan-in on read). The write cost is paid once; the read cost is O(1).

**EVOLUTION:**
Early social networks used fan-out-on-read (query at read time). Facebook, Twitter, and Instagram all evolved to hybrid approaches: fan-out on write for normal users (< 1000 followers), fan-out on read for celebrities (millions of followers). Modern feeds add machine learning ranking (not just reverse-chronological), real-time updates via WebSocket, and multi-media content serving through CDNs.

---

### 📘 Textbook Definition

A **news feed system** is a personalized content aggregation service that collects posts from accounts a user follows, ranks them, and presents the most relevant content. The primary technical challenge is the **fanout problem**: efficiently distributing a new post to all followers' feeds at write time (fan-out on write) or reconstructing the feed at read time (fan-out on read), at scale with millions of users and celebrities with millions of followers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pre-built personalized reading list, updated when followed accounts post new content.

**One analogy:**

> A news feed is like a personalized newspaper assembled on your doorstep each morning. The assembly happens overnight (fan-out on write), so you don't wait for it to be built when you pick it up. But if the President writes a front-page story (celebrity post), it's added to everyone's paper at the distribution center (fan-out on read to avoid writing to 1M doorsteps individually).

**One insight:**
Fan-out on write is fast to read but expensive to write for celebrities. Fan-out on read is cheap to write but expensive to read at scale. The key insight is to apply different strategies to different follower count ranges.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each user's feed is unique - it depends on who they follow.
2. A post created by account A must appear in every follower's feed.
3. Feed reads massively outnumber post writes (1000:1 ratio).
4. Celebrities (high follower count) have fundamentally different fanout costs than normal users.

**DERIVED DESIGN:**
For normal users: fan-out on write. When user publishes, push post_id to each follower's feed list in Redis. Feed read = Redis LRANGE, O(1).
For celebrities: fan-out on read. When user opens feed, merge their regular pre-built feed with any new celebrity posts. Avoid writing to 10M follower feeds on each celebrity post.

**THE TRADE-OFFS:**
**Gain (fan-out write):** O(1) feed reads; consistent freshness.
**Cost (fan-out write):** O(followers) write amplification per post; unacceptable for celebrities.
**Gain (fan-out read):** O(1) per post regardless of follower count.
**Cost (fan-out read):** O(followed accounts) per feed read; slower, harder to rank.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You must distribute posts to followers efficiently. Fanout direction determines cost model.
**Accidental:** Celebrity threshold detection, ML ranking on pre-built feeds, real-time update delivery.

---

### 🧪 Thought Experiment

**SETUP:** Twitter user @BigStar has 50M followers. They post twice/day. Normal users have 300 followers on average.

**WHAT HAPPENS WITH PURE FAN-OUT ON WRITE:**
@BigStar posts. System enqueues 50M feed insertions. At 100K insertions/second, that takes 8 minutes to fully propagate. During those 8 minutes, half of @BigStar's followers don't see the post. Storage: 50M Redis entries per post × 2 posts/day = 100M entries/day just for one celebrity.

**WHAT HAPPENS WITH HYBRID APPROACH:**
Normal user posts: fan-out to 300 followers - trivial. @BigStar posts: stored in @BigStar's post list only, not pushed to follower feeds. When a follower opens their feed: server fetches their pre-built feed (normal users' posts) + fetches latest posts from all followed celebrities (fan-out-on-read for celebrity posts only) + merges. Follower set for celebrity posts is small (just the latest few posts from followed celebrities), so read merge is fast.

**THE INSIGHT:**
The celebrity problem is not a failure of scale - it is a fundamental mismatch between fanout strategies. The hybrid approach uses each strategy where it is optimal: write fanout for low-follower accounts, read fanout for high-follower celebrities.

---

### 🧠 Mental Model / Analogy

> A news feed is like a personal mailbox with a pre-sorted stack of letters from friends (fan-out on write) PLUS a kiosk at the corner where you pick up today's popular newspaper (fan-out on read). Most of your reading comes from the pre-sorted mailbox; you only check the kiosk for a few important sources.

- **Pre-sorted mailbox** = user's feed cache in Redis
- **Letters from friends** = posts from normal followed users
- **Kiosk** = celebrity post store
- **Mail delivery** = fan-out write worker
- **Picking up newspaper** = fan-out read on feed open
- **Celebrity threshold** = mailbox vs kiosk decision boundary

Where this analogy breaks down: real mailboxes aren't ranked by relevance; ML-ranked feeds sort by predicted engagement, not delivery order.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you open Instagram or Twitter, you see posts from people you follow. Your phone isn't searching all of those peoples' profiles right now - the server pre-built your reading list so it appears instantly.

**Level 2 - How to use it (junior developer):**
Store followed accounts. On post, write to followers' feed lists. On feed read, return LRANGE of user's feed list. Paginate with cursor or offset. For simplicity, use reverse-chronological sort (newest first).

**Level 3 - How it works (mid-level engineer):**
Fan-out write worker: on post create event, look up follower list, enqueue batch insert of (post_id, ts) into each follower's Redis sorted set. Feed read: ZREVRANGE user_feed:{user_id} 0 19 (top 20 posts), hydrate with full post data from post store (Redis or DB). Hybrid: followers > 1M threshold gets celebrity fan-out-on-read treatment.

**Level 4 - Why it was designed this way (senior/staff):**
Twitter used to be pure fan-out-on-write, which caused the "Fail Whale" under celebrity load. They moved to a hybrid model. Facebook uses a ranked feed with an ML model re-ranking pre-built candidates. The combination of fan-out strategy + ranking strategy + delivery mechanism (WebSocket for real-time updates vs pull on page open) is the full system design. At extreme scale (1B DAU), even the follower lookup is sharded and cached - the social graph itself becomes a service.

**Expert Thinking Cues:**
- Ask: "What is the acceptable feed staleness? 1 second? 5 minutes?"
- Ask: "Do you rank by time or by ML relevance? Ranking requires more complex pipeline."
- Red flag: no celebrity threshold - fan-out to 10M followers on every post
- Red flag: hydrating post data on feed read from DB (not cache) - N+1 problem at scale

---

### ⚙️ How It Works (Mechanism)

**Post creation flow:**
```
User posts (text/media)
  1. Store post in post_store (DB + cache)
  2. Publish event: {user_id, post_id, ts}
  3. Fan-out worker consumes event:
     - If poster follows < 1M: fan-out on write
       GET followers_list:{poster_id}
       FOR each follower:
         ZADD feed:{follower_id} ts post_id
         LTRIM feed:{follower_id} 0 999 (keep 1000)
     - If poster is celebrity: skip fan-out
       (handled at read time)
```

**Feed read flow:**
```
User opens feed:
  1. ZREVRANGE feed:{user_id} 0 19 -> post_ids
  2. FOR each celebrity_id in followed_celebrities:
       ZREVRANGEBYSCORE posts:{celebrity_id} ... limit 5
  3. Merge, deduplicate, sort
  4. Hydrate post_ids -> full post objects (Redis/DB)
  5. (Optional) ML ranking pass on top 50 candidates
  6. Return top 20 posts
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[User A (1000 followers) creates post]
         |
         v
[Post stored in post_store]  <- YOU ARE HERE
         |
         v
[Fan-out event: push to 1000 follower feeds]
         |
         v
[Follower opens feed]
         |
         v
[Redis: ZREVRANGE feed:user_B -> post_ids]
         |
         v
[Hydrate posts, merge celebrity posts]
         |
         v
[Return ranked feed to client]
```

**FAILURE PATH:**
```
[Fan-out queue backs up (e.g., database slow)]
         |
[Follower receives stale feed]
         |
[Alert: fan-out lag > 30 seconds]
         |
[Design: accept eventual consistency for feeds]
```

**WHAT CHANGES AT SCALE:**
At 1B users, social graph is itself a distributed service. Fan-out queue is Kafka at 10M events/sec. Feed cache evicts older posts. Separate read and write paths entirely. CDN serves media referenced in posts.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Fan-out is inherently a write-heavy distributed pattern. Parallel fan-out workers handle follower batches concurrently. At millions of followers, a single post generates millions of DB/cache writes - design for this write amplification as the system's primary cost driver.

---

### 💻 Code Example

**BAD - fan-out on read at scale:**
```python
# BAD: O(followed_accounts * posts_each) on every read
def get_feed(user_id, limit=20):
    following = db.get_following(user_id)  # N accounts
    all_posts = []
    for account_id in following:           # N queries!
        posts = db.get_posts(account_id, limit=100)
        all_posts.extend(posts)
    all_posts.sort(key=lambda p: p.ts, reverse=True)
    return all_posts[:limit]
```

**GOOD - pre-built fan-out write feed:**
```python
import redis, json
from datetime import datetime

r = redis.Redis()
FEED_MAX_SIZE = 1000
CELEBRITY_THRESHOLD = 1_000_000

def on_post_created(poster_id: str, post_id: str):
    """Fan-out on write for normal users."""
    follower_count = get_follower_count(poster_id)
    if follower_count >= CELEBRITY_THRESHOLD:
        return  # Celebrity: handle at read time
    ts = datetime.utcnow().timestamp()
    # Batch follower lookup (paginated from DB/cache)
    cursor = 0
    while True:
        followers, cursor = get_followers_page(
            poster_id, cursor, page_size=1000
        )
        pipe = r.pipeline()
        for follower_id in followers:
            feed_key = f"feed:{follower_id}"
            pipe.zadd(feed_key, {post_id: ts})
            pipe.zremrangebyrank(feed_key, 0, -(FEED_MAX_SIZE+1))
        pipe.execute()
        if cursor == 0:
            break

def get_feed(user_id: str, page=0, size=20):
    """Read pre-built feed + celebrity merge."""
    start = page * size
    stop = start + size - 1
    feed_key = f"feed:{user_id}"
    post_ids = r.zrevrange(feed_key, start, stop)

    # Merge in celebrity posts (fan-out on read)
    celebrity_ids = get_followed_celebrities(user_id)
    recent_celebrity_posts = []
    for cid in celebrity_ids[:10]:  # top 10 celebrities
        posts = r.zrevrangebyscore(
            f"posts:{cid}", "+inf", "-inf",
            start=0, num=5
        )
        recent_celebrity_posts.extend(posts)

    # Merge and sort
    all_ids = list(post_ids) + recent_celebrity_posts
    all_ids = list(dict.fromkeys(all_ids))  # dedupe
    return hydrate_posts(all_ids[:size])
```

**How to test / verify correctness:**
- User A follows 100 accounts. One posts. Assert post appears in A's feed within 1 second.
- Celebrity (1M+ followers) posts. Assert no fan-out writes happen. Assert post appears in follower's feed via read-time merge.
- Fan-out worker goes down for 5 minutes. Assert posts created during downtime appear in feeds after worker recovers.

---

### ⚖️ Comparison Table

| Strategy          | Write cost          | Read cost    | Freshness  | Celebrity handling |
| ----------------- | ------------------- | ------------ | ---------- | ------------------ |
| Fan-out on write  | O(followers)        | O(1)         | Immediate  | Explodes at scale  |
| Fan-out on read   | O(1)                | O(following) | Immediate  | No problem         |
| Hybrid (Twitter)  | O(followers < 1M)   | O(celebrities) | Near RT  | Celebrity read-merge |
| Pull-on-open      | None                | O(following) | Immediate  | Scanning problem   |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Fan-out on write is always better for reads" | Fan-out on write becomes prohibitively expensive for celebrities. A 50M follower celebrity posting 10 times/day generates 500M write operations/day from a single account. |
| "The feed just needs to be sorted by time" | Chronological feeds were replaced at every major platform with ML-ranked feeds because engagement metrics showed ranked feeds significantly outperform chronological on user retention. |
| "Pre-building feeds wastes storage" | The storage cost of pre-built feeds (post_ids per user per 1000 posts) is much smaller than the compute cost of rebuilding the feed from scratch on every open. Precompute is almost always cheaper. |
| "Feed updates must be real-time" | Most users accept feeds that are slightly stale (seconds to minutes). Real-time updates via WebSocket are costly - most systems only push new post badges, not full feed refreshes. |
| "One fan-out strategy fits all" | The celebrity problem requires hybrid strategies. Design for the distribution of follower counts in your system, not just the average. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Fan-out queue backup causing stale feeds**

**Symptom:** New posts don't appear in followers' feeds for minutes after creation.

**Root Cause:** Fan-out worker queue depth is growing; worker throughput < post rate × avg followers.

**Diagnostic:**
```bash
# Check Kafka consumer lag for fan-out topic
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --group fanout-workers \
  --describe | grep LAG
```

**Fix:** Scale fan-out workers horizontally. Increase Kafka partition count for parallelism.

**Prevention:** Alert on fan-out lag > 10 seconds; auto-scale workers at 80% queue depth.

---

**Failure Mode 2: N+1 hydration on feed read**

**Symptom:** Feed API response time is 2+ seconds even with warm cache.

**Root Cause:** Fetching each post's full data with a separate DB/cache query per post_id.

**Diagnostic:**
```bash
# Check DB query count during feed load
# Look for "SELECT * FROM posts WHERE id = X" × 20 times
# in APM trace for a single feed request
```

**Fix:** Use `MGET` or `pipeline` to batch-fetch all post data in one Redis call.

**Prevention:** Profile feed endpoint under load; assert ≤ 3 Redis calls per feed page.

---

**Failure Mode 3: Feed cache eviction of followed accounts**

**Symptom:** Some users see empty sections of their feed for accounts that haven't posted recently.

**Root Cause:** Feed cache evicts entries when followers haven't opened the app in weeks. Fan-out worker doesn't push to cold feeds.

**Diagnostic:** Check feed cache TTL settings; measure percentage of feed reads that result in empty feeds.

**Fix:** On app open after long absence, trigger a background job to rebuild the feed from post history.

**Prevention:** Implement lazy feed rebuild: if feed cache is empty, fall back to fan-out-on-read temporarily while rebuilding.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-059 - Fan-Out on Write vs Read]] - the fundamental algorithmic choice
- [[SYD-063 - Data Partitioning Strategies]] - partitioning the feed cache and post store

**Builds On This (learn these next):**
- [[SYD-071 - System Design at Hyperscale]] - extends this to billion-user scale
- [[SYD-066 - Search Autocomplete Design]] - another read-heavy system design

**Alternatives / Comparisons:**
- [[SYD-058 - Denormalization for Scale]] - related technique of pre-computing read views

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-computed personalized post   │
│              │ aggregation with fanout workers  │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Real-time feed assembly at scale │
│ IT SOLVES    │ is too slow for 100M+ users      │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Fan-out on write for normal      │
│              │ users; fan-out on read for       │
│              │ celebrities (hybrid)             │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Social feeds, activity streams,  │
│              │ personalized content             │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Content is not personalized -    │
│              │ use a simple ranked timeline     │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Write amplification (fan-out     │
│              │ write) vs read complexity        │
│              │ (fan-out read)                   │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Pre-build feeds on write; merge │
│              │ celebrity posts on read."        │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-066 Search Autocomplete      │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Fan-out on write for normal users; fan-out on read for celebrities - the hybrid approach.
2. Store post_ids in the feed cache; hydrate post data separately (don't store full posts).
3. Design for the tail of follower distribution - the celebrity with 50M followers defines your write amplification ceiling.

**Interview one-liner:** "News feed uses fan-out on write for high-frequency reads but fan-out on read for celebrities - the hybrid threshold (e.g., 1M followers) prevents catastrophic write amplification from celebrity accounts."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When read frequency vastly exceeds write frequency, precompute at write time. When write amplification becomes unacceptable (celebrity problem), accept read-time computation for a small subset. The optimal solution recognizes both patterns simultaneously.

**Where else this pattern appears:**
- **Email inboxes:** Emails are "fanned out" to recipient mailboxes at delivery time (fan-out on write); spam filters run at read time (fan-out on read equivalent).
- **E-commerce recommendations:** "Users also bought" lists are pre-computed nightly (fan-out on write) but live inventory is checked at display time (read merge).
- **Notification systems:** User notifications use pre-built per-user notification lists with real-time push for new events.

---

### 💡 The Surprising Truth

Twitter's original architecture was pure fan-out on write, which was the direct cause of the "Fail Whale" outages around 2008-2012. Posts from accounts like @BarackObama or @TaylorSwift would trigger tens of millions of simultaneous fan-out writes, saturating the database. The solution - the celebrity/hybrid threshold - was added years after launch as an emergency fix, not a planned design. The lesson: the celebrity distribution of follower counts is non-obvious early on and requires explicit design when you reach scale.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user unfollows an account. Their pre-built feed still contains all posts from that account. Describe the exact approach to "cleaning" the feed: remove all past posts of the unfollowed account, stop future post delivery, and handle the case where the user re-follows before the cleanup completes.

*Hint:* Consider lazy deletion (filter unfollowed account's posts at read time) vs eager deletion (scan and remove from Redis sorted set). The re-follow case creates a race condition - explore how idempotent operations handle this.

**Q2 (Scale):** Instagram has 1B users, average 300 following, average 50 posts/day per followed account. Calculate the total daily fan-out operations at the 75th-percentile user and the celebrity celebrity producing 10x engagement. How many Kafka messages/second does the fan-out pipeline handle at peak (8 PM)?

*Hint:* Start with daily operations = users x avg_following x posts_per_day, then model peak hour concentration (typically 20% of daily traffic in 1 hour). Then multiply by average followers per poster to get total fan-out writes.

**Q3 (Design Trade-off):** Facebook moved from chronological feeds to ML-ranked feeds in 2009. The ML model predicts which posts you will engage with. What happens to your feed if the model has a bug that gives all posts a score of 0? What happens if a feed post from 3 years ago scores higher than a post from 5 minutes ago?

*Hint:* Explore the concept of feed freshness constraints (maximum post age in ranked feed), the fallback to chronological ordering when scoring fails, and how A/B testing infrastructure validates ranking model changes before full rollout.
