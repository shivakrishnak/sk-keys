---
id: SYD-035
title: "Fan-Out on Write vs Read"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-033, SYD-034
used_by: SYD-045, SYD-047
related: SYD-034, SYD-036, SYD-045
tags:
  - architecture
  - distributed
  - advanced
  - tradeoff
  - pattern
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /syd/fan-out-on-write-vs-read/
---

# SYD-035 - Fan-Out on Write vs Read

⚡ TL;DR - The core trade-off in social feed design: pre-distribute content to followers at write time (fast reads, expensive writes) vs assemble feeds on demand at read time (cheap writes, slow reads).

| SYD-035         | Category: System Design     | Difficulty: ★★★ |
| :-------------- | :-------------------------- | :-------------- |
| **Depends on:** | SYD-033, SYD-034            |                 |
| **Used by:**    | SYD-045, SYD-047            |                 |
| **Related:**    | SYD-034, SYD-036, SYD-045   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are building Twitter. A user with 10M followers posts a tweet. Do you: (a) write one record and let all reads query it dynamically (10M queries hit the source on timeline load), or (b) write 10M copies of the tweet to each follower's inbox (one write triggers 10M db operations)? Both extremes cause failures at scale. Getting this wrong means either reads are unacceptably slow or writes take minutes.

**THE BREAKING POINT:**
Social feeds create a multiplier problem: one write (post) may need to reach N readers (followers). This N-multiplier can be 1 (no followers) or 100M (celebrity). The moment this multiplier hits thousands, naive architectures break in one of two ways: fan-out on write explodes write latency; fan-out on read explodes read latency.

**THE INVENTION MOMENT:**
Twitter engineers designed the "pull model" and "push model" for tweet delivery in 2012 and published "The Infrastructure Behind Twitter: Scale." They discovered that neither pure model works for all accounts and introduced a hybrid: push model for non-celebrity accounts (fast reads, manageable writes), pull model for celebrity accounts (immediate writes, merged at read time).

**EVOLUTION:**
Facebook's news feed, Instagram's feed, and LinkedIn's feed all use variants of this hybrid approach. Modern implementations use Kafka for async fan-out, Redis timeline caches, and real-time merger of celebrity content at read time to balance write and read costs.

---

### 📘 Textbook Definition

**Fan-out on write** (push model): When a user creates content, it is immediately copied (fanned out) to all followers' inboxes/caches. Reads are fast (pre-assembled inbox), but writes are expensive for high-follower users. **Fan-out on read** (pull model): Content is stored once at creation; each follower's feed is assembled by querying all followed users' recent posts at read time. Writes are cheap but reads are expensive (O(followed_count) queries). **Hybrid** models use fan-out on write for normal users and fan-out on read for celebrities/high-follower accounts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Trade expensive writes (fan-out on write) for fast reads, or cheap writes (fan-out on read) for expensive reads - most production systems use both.

**One analogy:**
> Newspaper home delivery (fan-out on write) vs news stand (fan-out on read). Home delivery: one press run creates thousands of copies delivered to each subscriber (write-expensive, read-instant). News stand: one pile of papers; each reader comes to get theirs (write-cheap, read requires trip to stand). Celebrity news is already at every home; niche news is only at the news stand.

**One insight:**
The correct model depends entirely on follower count. Fan-out on write becomes unacceptable when any single user has millions of followers. Most real systems need both models simultaneously.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. One post can reach N followers; N varies by user from 0 to 100M.
2. Fan-out on write: write cost = O(followers), read cost = O(1).
3. Fan-out on read: write cost = O(1), read cost = O(followed_count).
4. Users with many followers have expensive writes (fan-out); users following many people have expensive reads (pull).
5. A hybrid requires detecting which users cross the threshold between models.

**DERIVED DESIGN:**
Threshold-based hybrid: for users with followers < threshold (e.g., 10,000), use fan-out on write. For users with followers >= threshold, store posts centrally and merge into followers' feeds at read time. Threshold determined by write latency budget and acceptable write queue depth.

**THE TRADE-OFFS:**
**Fan-out on write:** Gain: O(1) read time, low read latency, pre-built feed. Cost: O(followers) write cost, write queue depth for celebrities, storage proportional to total (user × follower) pairs.
**Fan-out on read:** Gain: O(1) write time, no redundant storage. Cost: O(followed_count) read time, read latency scales with follows, expensive for highly social users.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The N multiplier between content creators and consumers is a fundamental property of social graphs.
**Accidental:** Implementing separate pipelines for celebrity vs normal accounts introduces operational complexity, but this complexity is unavoidable at scale.

---

### 🧪 Thought Experiment

**SETUP:**
Twitter has 100M users. Average user follows 300 people and has 300 followers. But 1,000 users (celebrities) have 10M+ followers each.

**WHAT HAPPENS WITH PURE FAN-OUT ON WRITE:**
Normal user posts: copy to 300 followers = 300 writes (fine). Celebrity posts: copy to 10M followers = 10M writes. Each celebrity post requires a 10M-write fan-out. At 100 celebrity posts/hour, the write queue never empties. Celebrity feed delivery takes hours.

**WHAT HAPPENS WITH PURE FAN-OUT ON READ:**
Normal user loads feed: query 300 followed users' recent posts = 300 DB lookups + merge. Latency: 3-5 seconds. Unacceptable. Every feed load is expensive regardless of social graph size.

**WHAT HAPPENS WITH HYBRID:**
Normal users: fan-out on write (feed available in Redis in <100ms). Celebrities: posts stored centrally. On feed load: read pre-built Redis feed (milliseconds) + real-time merge of any celebrity posts (one lookup per celebrity followed). Total: <200ms.

**THE INSIGHT:**
The key metric is not average follower count - it is the maximum follower count in your system. One user with 100M followers ruins pure fan-out on write for everyone.

---

### 🧠 Mental Model / Analogy

> Fan-out on write vs read is like broadcast email vs mailing list with subscription. Broadcast email (write): you send 10M emails when you post - high write cost, instant inbox. Mailing list subscription (read): subscribers check the mailing list on demand - one post stored once, each subscription pull reads it. Celebrity newsletters use broadcast (high write, instant read). Niche blogs use RSS/subscription (cheap write, pull-when-read).

**Mapping:**
- Send email to each subscriber → fan-out on write (push each follower's feed)
- Post to mailing list server → fan-out on read (single post, pulled by subscribers)
- Email inbox → user's pre-built Redis feed cache
- Opening email vs checking mailing list → read speed difference
- Unsubscribing from celebrities → hybrid threshold

Where this analogy breaks down: email is asynchronous delivery with no consistency requirements; feed systems often need ordering guarantees and pagination that complicate both models.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you post on Instagram, does Instagram copy your post to every follower's feed right away (fan-out on write), or does each follower's app collect posts from everyone they follow when they open the app (fan-out on read)? Real systems do both: regular users push; celebrities pull.

**Level 2 - How to use it (junior developer):**
For a basic implementation: on post creation, publish event to Kafka. Fan-out service reads from Kafka and writes to Redis sorted set for each follower (high follower limit: 10K). For CEO/celebrity accounts, skip fan-out on write; instead, at feed read time, merge their posts from a separate celebrity store.

**Level 3 - How it works (mid-level engineer):**
Fan-out service architecture: (1) Post event → Kafka topic. (2) N fan-out worker processes consume from topic. (3) Each worker writes to Redis sorted set keyed by follower's user_id, value = post_id, score = timestamp. (4) Feed read: ZREVRANGE(user_id:feed, 0, 99) returns 100 most recent post IDs. (5) Multi-get from post store for content. Celebrity merge: flag accounts above threshold; at feed read time, additional lookup from celebrity-posts store, merge by timestamp.

**Level 4 - Why it was designed this way (senior/staff):**
The pure push/pull decision is a data volume vs operation latency trade-off on a Pareto-distributed social graph. The Pareto (80/20) rule means 20% of users generate 80% of content seen; within that 20%, a tiny celebrity tier generates a disproportionate share. Hybrid design is optimal under Pareto distributions: push optimises for the common 99.9% case, pull optimises for the rare celebrity case. Senior engineers also consider: timeline consistency (what ordering guarantee do you provide?), infrastructure cost (Redis storage for N follower timelines × posts), and operational complexity of the celebrity threshold system.

**Expert Thinking Cues:**
- "What is the maximum follower count in my system, and how does that drive write latency?"
- "What follower threshold triggers a switch from push to pull model?"
- "How do I handle a user growing from 100K to 10M followers transparently?"
- "What is the storage cost of pre-materialised timelines vs on-demand query?"

---

### ⚙️ How It Works (Mechanism)

```
FAN-OUT ON WRITE
════════════════
User Post Event
    │
    ▼
Kafka: post_events topic
    │
    ▼
Fan-out Workers (parallel)
    │
    └──→ Redis: user:follower1:feed  ← YOU ARE HERE
    └──→ Redis: user:follower2:feed
    └──→ Redis: user:followerN:feed

FAN-OUT ON READ
════════════════
User Loads Feed
    │
    ▼
App Server
    │
    ├──→ Query: posts by user1 recent 20
    ├──→ Query: posts by user2 recent 20
    └──→ Query: posts by userN recent 20
    │
    ▼
Merge + Sort by timestamp

HYBRID
════════
User Loads Feed  ← YOU ARE HERE
    │
    ├──→ Redis: user:feed (pre-built, normal users)
    │
    └──→ Celebrity Store (live merge)
    │
    ▼
Merged, sorted feed
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User A (10K followers) creates post
    │
    ▼
Post stored in Posts table
    │
    ▼
Kafka event published          ← YOU ARE HERE
    │
    ▼
Fan-out workers: write to 10K
follower Redis feeds (async)
    │
    ▼
User B loads feed:
  Redis ZREVRANGE → post IDs in 5ms
```

**FAILURE PATH:**
Fan-out workers fall behind (celebrity post storm) → follower Redis feeds not updated → users see stale feed → backpressure on Kafka queue → eventual delivery once workers catch up → users see posts appear "late."

**WHAT CHANGES AT SCALE:**
The celebrity threshold must be continuously recalculated. A user who crosses the threshold mid-operation requires atomic migration: move from push to pull model while in-flight fan-outs are still completing.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Fan-out workers process partitioned by follower user_id to prevent race conditions on individual Redis sorted sets. At very high scale, fan-out is sharded across fan-out worker groups, each handling a range of follower IDs.

---

### 💻 Code Example

```python
# Fan-out on write implementation
import redis

r = redis.Redis(host='localhost')

def fan_out_on_write(post_id: str,
                     creator_id: str,
                     timestamp: float,
                     follower_ids: list):
    """Write post to all follower Redis feeds."""
    pipe = r.pipeline()
    for follower_id in follower_ids:
        feed_key = f"feed:{follower_id}"
        # Sorted set: score=timestamp, member=post_id
        pipe.zadd(feed_key,
                  {post_id: timestamp})
        # Keep last 1000 posts per feed
        pipe.zremrangebyrank(feed_key, 0, -1001)
    pipe.execute()

def read_feed(user_id: str,
              page: int = 0,
              per_page: int = 20) -> list:
    """Read pre-built feed from Redis."""
    feed_key = f"feed:{user_id}"
    start = page * per_page
    end = start + per_page - 1
    # O(1) lookup from pre-built feed
    return r.zrevrange(feed_key, start, end)

# Celebrity hybrid: merge at read time
CELEBRITY_THRESHOLD = 10_000

def read_feed_hybrid(user_id: str,
                     followed_ids: list) -> list:
    normal_feed = read_feed(user_id)  # from Redis

    # Merge celebrity posts at read time
    celebrities = [uid for uid in followed_ids
                   if get_follower_count(uid)
                   >= CELEBRITY_THRESHOLD]
    celeb_posts = get_recent_posts(celebrities)

    return merge_by_timestamp(
        normal_feed, celeb_posts)[:20]
```

**How to test / verify correctness:**
- Write correctness: verify post_id appears in all N follower feeds after fan-out.
- Celebrity merge: follow a celebrity-flagged user; verify their posts merge into feed at read time.
- Load test: simulate 1000 concurrent posts from a 1M-follower user; measure fan-out throughput and latency.

---

### ⚖️ Comparison Table

| Model | Write Cost | Read Cost | Storage | Best For |
|---|---|---|---|---|
| **Fan-out on write** | O(followers) | O(1) | O(users × follows) | Normal accounts, fast feed |
| **Fan-out on read** | O(1) | O(follows) | O(posts) | Low follower count systems |
| **Hybrid** | O(followers) for normal | O(celebrity count) | Both | Production social apps |
| **Event sourcing + CQRS** | O(1) write | O(1) read model | Event log + read model | Complex social graphs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Fan-out on write scales linearly" | It scales with follower count per creator, which is Pareto-distributed - celebrities cause super-linear write cost. |
| "Fan-out on read is always cheaper" | Read cost is O(followed_count). Highly social users following 10K accounts have expensive feeds. |
| "Hybrid routing is just an optimisation" | Hybrid is the only viable architecture for general social networks at scale; both pure models fail for some users. |
| "Redis fan-out is instantaneous" | Async fan-out has latency. Users expect near-real-time but fan-out workers may lag under load. |
| "Celebrity threshold is fixed" | Threshold must be dynamic: A user grows from 1K to 10M followers gradually. Migration between models mid-growth must be handled. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Celebrity Post Write Storm**
**Symptom:** Fan-out Kafka queue backs up for hours; followers see posts with multi-hour delay.
**Root Cause:** Celebrity with 100M followers posted; 100M fan-out writes queued but workers can't keep up.
**Diagnostic:**
```bash
# Check Kafka consumer lag for fan-out group
kafka-consumer-groups.sh --describe \
  --group feed-fanout-workers
# LAG in millions = celebrity storm
```
**Fix:** Immediately flag the celebrity for pull model; drain queue; verify no new fan-outs generated.
**Prevention:** Automatic celebrity detection before threshold is breached; hybrid routing for any user > threshold.

**Mode 2: Redis Feed Cache Eviction**
**Symptom:** Inactive users open the app; their pre-built feed is empty (Redis evicted their key).
**Root Cause:** Redis ran out of memory; LRU eviction deleted inactive users' pre-built feeds.
**Diagnostic:**
```bash
redis-cli info memory | grep evicted_keys
# Large evicted_keys count = memory pressure
redis-cli info memory | grep used_memory_human
```
**Fix:** On empty feed, fall back to on-demand read query to rebuild feed. Increase Redis memory allocation.
**Prevention:** Set Redis eviction policy to `volatile-lru`; set feed keys with TTL + rebuild on miss.

**Mode 3: Feed Missing Celebrity Posts**
**Symptom:** User follows a celebrity but never sees their posts in feed.
**Root Cause:** Celebrity flagged for pull model but read merge logic has a bug; celebrity posts not merged.
**Diagnostic:**
```bash
# Check if user follows celebrity in DB
SELECT * FROM follows WHERE follower=? AND followee=?;
# Check celebrity flag
SELECT follower_count FROM users WHERE id=?;
```
**Fix:** Debug merge function; ensure celebrity post fetch executes for all followed celebrities.
**Prevention:** Integration test: follow a celebrity-flagged account; assert their posts appear in feed read response.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-033 - Read-Heavy vs Write-Heavy Design]] - Fan-out is the core read/write trade-off of social feeds
- [[SYD-034 - Denormalization for Scale]] - Fan-out on write is a form of denormalization

**Builds On This (learn these next):**
- [[SYD-045 - News Feed Design]] - End-to-end system design applying this pattern
- [[SYD-047 - Notification System Design]] - Related fanout pattern for notifications

**Alternatives / Comparisons:**
- [[SYD-036 - Push vs Pull Architecture]] - The generalised version of this pattern

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Core social feed trade-off: ║
║               distribute at write vs      ║
║               assemble at read time       ║
╠══════════════════════════════════════════╣
║ PROBLEM       One write reaching N        ║
║ IT SOLVES     followers efficiently       ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Use both: push for normal   ║
║               users, pull for celebrities ║
╠══════════════════════════════════════════╣
║ FAN-OUT WRITE O(followers) write cost;    ║
║               O(1) read cost              ║
╠══════════════════════════════════════════╣
║ FAN-OUT READ  O(1) write cost;            ║
║               O(follows) read cost        ║
╠══════════════════════════════════════════╣
║ HYBRID        Celebrity threshold > 10K   ║
║               triggers pull model         ║
╠══════════════════════════════════════════╣
║ ONE-LINER     Pre-build feeds for normal  ║
║               users; merge celebrity      ║
║               content at read time        ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-036: Push vs Pull       ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Fan-out on write is O(followers) write cost - unacceptable for celebrity accounts.
2. Fan-out on read is O(follows) read cost - unacceptable for users following thousands of accounts.
3. Production social apps always use hybrid: push model below a follower threshold, pull model above.

**Interview one-liner:**
"Fan-out on write pre-distributes posts to follower feeds at write time for O(1) reads but O(followers) writes; fan-out on read queries all followed users at read time; production systems use a hybrid with celebrity threshold."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
In asymmetric fan-out scenarios (one-to-many relationships), the optimal distribution strategy depends on the ratio distribution. When the multiplier is bounded and low (followers < 10K), paying the fan-out cost at write time (rare) is better than paying it at read time (frequent). When the multiplier is unbounded (celebrities), you must invert the model.

**Where else this pattern appears:**
- **Email newsletters:** Transactional email services pre-render and deliver (fan-out on write) vs RSS feeds which pull on demand.
- **CDN edge caching:** Origin pushes popular content to edge nodes (fan-out on write) vs pulling content on first request (fan-out on read).
- **Database read models in CQRS:** Event sourcing fans-out write events to multiple read model projections.

---

### 💡 The Surprising Truth

Twitter originally built a pure fan-out on write system and it worked perfectly until a few extremely high-follower users broke it. The celebrity problem is not a theoretical edge case - it is a mathematical certainty for any social network that reaches sufficient scale. Zipf's law guarantees that in any network of N users, there will be users with O(N) followers. This means the hybrid model is not an optimisation that mature systems adopt - it is the only architecture that can work at all for general social networks.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user with 5M followers creates a post at exactly midnight on New Year's Day when all their followers open the app. Walk through the exact failure cascade if you are using pure fan-out on write.
*Hint:* Model the write queue depth (5M writes queued simultaneously), the time to drain (fan-out worker throughput), and the thundering herd effect of 5M followers doing read requests while the queue hasn't drained yet.

**Q2 (Scale):** Your social network has 100M users. Average follows = 200, average followers = 200. 0.01% of users (10K celebrities) have 1M+ followers. Calculate the total Redis storage required for fan-out-on-write timelines assuming 100 posts per user per year and 50 bytes per post ID entry.
*Hint:* Total timeline entries = sum over all users of (their follower count × their posts per year). For celebrities, this dominates - calculate celebrity contribution vs non-celebrity contribution separately.

**Q3 (Design Trade-off):** You are building a professional network (like LinkedIn) where users follow companies (which have millions of followers) and people (who have hundreds). Should companies use fan-out on write or read? Should people? What happens when a company posts vs when a person posts?
*Hint:* Apply the follower threshold analysis to each entity type - companies naturally have many followers (fan-out on read candidates) while people have few (fan-out on write candidates), and explore how the hybrid model requires entity-type-aware routing logic.
