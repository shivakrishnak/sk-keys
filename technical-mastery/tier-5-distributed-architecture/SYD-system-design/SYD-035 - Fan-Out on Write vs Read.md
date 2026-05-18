---
id: SYD-035
title: Fan-Out on Write vs Read
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-033
used_by: ""
related: SYD-031, SYD-033, SYD-034, SYD-036, SYD-045
tags:
  - architecture
  - social-systems
  - scalability
  - design-tradeoff
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/syd/fan-out-on-write-vs-read/
---

⚡ TL;DR - Fan-out determines when a post's content is
delivered to followers. Fan-out on write (push model):
when a user posts, immediately write to every follower's
feed inbox. Read is O(1). Fan-out on read (pull model):
when a user requests their feed, fetch posts from all
followed accounts at read time. Write is O(1). Neither
is universally better - the right choice depends on
follower count distribution and read-to-write ratios.
Twitter, Instagram, and Facebook all use hybrid models.

| #035            | Category: System Design                                                                                     | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Sharding, Read-Heavy vs Write-Heavy Design                                                                  |                 |
| **Used by:**    | (News Feed Design)                                                                                          |                 |
| **Related:**    | Sharding, Read-Heavy vs Write-Heavy, Denormalization for Scale, Push vs Pull Architecture, News Feed Design |                 |

---

### 🔥 The Problem This Solves

**THE FEED PROBLEM:**
A social network has 100 million users. User Alice
(1M followers) posts a photo. The system must deliver
this photo to the feed of all 1M followers. Two choices:

**Choice A (push/fan-out on write):**
At post time, write Alice's photo to 1M feed inboxes.
Read: each user's feed is pre-populated; O(1) read.
Problem: 1 post creates 1M database writes instantly.
At peak (1M posts/min from all users): catastrophic.

**Choice B (pull/fan-out on read):**
At post time, write only one record to the posts table.
Read: each user's feed fetches from all accounts they
follow at read time. O(following_count) reads per feed.
Problem: a user following 5,000 accounts triggers 5,000
DB reads per feed refresh. At 100M users refreshing
feeds: catastrophic.

Neither extreme works. The hybrid model is used in
practice. This is the fan-out design problem.

---

### 📘 Textbook Definition

**Fan-out on write (push model):** When content is
created, immediately distribute it to all consumers
(followers' feed inboxes). Reading is O(1) (fetch the
pre-built inbox). Writing is O(followers) (one write
per follower). Write-heavy; read-fast.

**Fan-out on read (pull model):** When content is
created, write only once. When a consumer requests
their feed, pull from all content creators they follow
and merge at read time. Reading is O(following_count).
Writing is O(1). Read-heavy; write-fast.

**Hybrid model:** Use fan-out on write for normal users.
Use fan-out on read for celebrity users (too many
followers to write to all at post time). Merge at
read time: pre-built inbox + real-time celebrity posts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Push (fan-out on write): pre-deliver to inboxes at post
time. Pull (fan-out on read): assemble feed at read time.
Each trades write work for read work.

**One analogy:**

> A newspaper:
>
> Fan-out on write (push): The publisher prints a copy
> for every subscriber and delivers it to their door
> by 6am. Reading is instant (paper is already there).
> Printing cost: proportional to subscriber count.
> Taylor Swift publishes a paper: 50M copies printed.
>
> Fan-out on read (pull): No printing. Reader drives
> to the publisher's warehouse on demand and reads.
> Publisher's cost: O(1) per article. Reader's cost:
> O(publishers_subscribed_to) - drive to each publisher.
>
> Hybrid: Pre-print for most subscribers (casual users).
> Taylor Swift's paper: only print on demand for a few.

**One insight:**
Fan-out on write moves work from read time to write time
(and from the reader to the system). Fan-out on read moves
work from write time to read time (and from the system
to the reader). The right model depends on whether you
have more readers or more writers, and whether celebrity
users (high fanout) are common.

---

### 🔩 First Principles Explanation

**MATH OF EACH APPROACH:**

```
System parameters:
  N_users = 100M users
  avg_followers = 200 per user
  celebrity_followers = 1M (top 0.1% users)
  writes/sec = 10K posts/sec
  reads/sec = 100K feed requests/sec

FAN-OUT ON WRITE:
  Cost per write = avg_followers = 200 DB writes
  Total writes/sec = 10K × 200 = 2M DB writes/sec
  Celebrity write = 1M DB writes per post (spike)
  Cost per read = 1 DB read (pre-built inbox)
  Total reads/sec = 100K × 1 = 100K DB reads/sec

  Issue: celebrity creates 1M writes in <1 second
  → write throughput spike, hot shard on their followers

FAN-OUT ON READ:
  Cost per write = 1 DB write
  Total writes/sec = 10K × 1 = 10K DB writes/sec
  Cost per read = avg_following = 200 DB reads
  Total reads/sec = 100K × 200 = 20M DB reads/sec

  Issue: user following 5,000 accounts → 5,000 reads
  per feed page → slow if not cached

HYBRID MODEL (Twitter's approach):
  Normal users (< 5K followers): fan-out on write
  Celebrity users (> 5K followers): fan-out on read

  Writes/sec for normal: 9,999 × 200 = ~2M writes/sec
  Writes/sec for celebrities: 1 write per post (no fan-out)
  Reads: pre-built inbox for normal user posts
         + real-time fetch for celebrity posts
         + merge at read time

  Eliminates celebrity write spike
  Keeps read fast for most content
  Small merge overhead for celebrity posts at read time
```

**IMPLEMENTATION DETAILS:**

**Fan-out on write (push):**

```
Post created → Kafka message "new_post" →
Fan-out workers consume message:
  1. Fetch list of post.user_id's followers
  2. For each follower_id:
       RPUSH feed:follower_id {post_id, ts}
  3. Trim list: LTRIM feed:follower_id 0 999
     (keep most recent 1000 posts)

Read feed: LRANGE feed:user_id 0 19
           (fetch post IDs)
           MGET post:{id} for each
           (fetch post details from post cache)
```

**Fan-out on read (pull):**

```
Post created → write to posts:{user_id} sorted set
              ZADD posts:{user_id} {timestamp} {post_id}

Read feed:
  1. SMEMBERS following:{user_id} → [account1, account2,
    ...]
  2. For each followed account:
       ZREVRANGEBYSCORE posts:{account_id} MAX MIN LIMIT 0
         5
  3. Merge-sort all posts by timestamp (k-way merge)
  4. Return top 20

Problem: following 2000 accounts → 2000 Redis calls
Solution: pipeline all calls; async assembly with timeout
```

---

### 🧪 Thought Experiment

**SCENARIO: Instagram stories delivery**

Instagram has 2B users. Story expiry: 24 hours.
A story is viewed by a fraction of followers (not all).
Should Instagram use fan-out on write or read for stories?

**Consideration 1: Unread stories waste work**
A celebrity has 50M followers. Most won't view the story
within 24 hours. If fan-out on write: write 50M feed
entries for a story that 40M followers will never view.
60M writes wasted per celebrity story.

**Consideration 2: Fan-out on read at 2B users**
If fan-out on read: every user's story feed requires
pulling from all accounts they follow. 2B users, even
once/hour = 2B/3600 = 555K requests/sec pulling from
up to 500 accounts each.

**Instagram's solution (known from engineering blog):**
For stories: fan-out on read with aggressive caching.
Stories are naturally time-bounded (24h expiry). Read
path: pull from followed accounts + cache story metadata
at CDN. The pull model works because: (a) story metadata
is small, (b) CDN caches reduce origin hits significantly,
(c) celebrity story reads are served from CDN not DB.

**The lesson:** Fan-out strategy depends on content
lifetime, view probability, and read/write ratio. Stories
(time-bounded, not always viewed) favor pull. Permanent
feed posts (always in feed) favor push for normal users.

---

### 🧠 Mental Model / Analogy

> Email newsletter vs search results:
>
> Fan-out on write = email newsletter:
> Publisher sends to every subscriber at publish time.
> Inbox is pre-built. Opening email: instant.
> Cost: proportional to subscriber count at send time.
>
> Fan-out on read = search results:
> Search query assembled at read time from
> all indexed sources. Writing: index one article.
> Reading: combine sources on demand.
> Cost: proportional to sources at read time.
>
> Google Search is fan-out on read.
> Gmail newsletter is fan-out on write.
> Twitter's timeline is hybrid.
> LinkedIn's feed is hybrid.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you post something, the system can either send
it to everyone's feeds immediately (fan-out on write)
or wait for each person to request their feed and
assemble it then (fan-out on read).

**Level 2 - How to use it (junior developer):**
For small systems: fan-out on read is simpler to
implement (write one record; query at read time).
For medium systems with read-heavy feeds: fan-out on
write with Redis list-based inboxes. For large systems
with celebrities: hybrid model required.

**Level 3 - How it works (mid-level engineer):**
Fan-out on write uses a message queue (Kafka) for
async fan-out. A pool of fan-out workers reads the
queue and writes to follower inboxes (Redis sorted
sets or lists). This decouples post creation latency
from fan-out latency. The post is visible in the author's
own feed immediately; follower feeds updated within seconds.

**Level 4 - Why it was designed this way (senior/staff):**
The celebrity problem (high-follower users) breaks fan-out
on write because it creates extreme write amplification
spikes. A tweet from a 100M-follower account creates 100M
inbox writes in a short window. The hybrid model with fan-out
on read for celebrities elegantly solves this: celebrities
represent <0.1% of users but >50% of fanout write volume.
By switching them to on-read, you eliminate the worst spikes.
The read-time merge cost is small (fetch 10-20 celebrity
latest posts on each feed request; cache their posts
separately).

**Level 5 - Mastery (distinguished engineer):**
The fan-out problem is a specific case of the more general
"materialization vs computation" tradeoff: is it cheaper
to precompute (materialize) a result and store it, or to
compute it on demand? The answer depends on:

- Read frequency vs write frequency
- Fan-out factor (followers per writer)
- Content popularity distribution (Zipf: top 0.1% creates
  most content views)
- Acceptable staleness (can a feed be 5 seconds stale?)

The hybrid model is essentially a cache-aside pattern
applied to feed assembly: pre-materialize feeds for
most users (cache = inbox), invalidate/update on write,
fall back to on-demand computation for uncached data
(celebrity posts, new followers, etc.).

---

### ⚙️ How It Works (Mechanism)

**Hybrid fan-out architecture:**

```
┌────────────────────────────────────────────────────────┐
│ HYBRID FAN-OUT FLOW                                   │
│                                                        │
│  User Alice posts (10K followers, normal user):       │
│    Write post → Kafka → Fan-out workers               │
│    Workers: RPUSH feed:{follower_id} post_id          │
│    (10K writes, fast)                                 │
│                                                        │
│  Taylor Swift posts (50M followers, celebrity):       │
│    Write post → only posts:{taylor_id} sorted set    │
│    NO fan-out to follower inboxes                     │
│    (0 fan-out writes)                                 │
│                                                        │
│  User Bob reads feed:                                 │
│    1. LRANGE feed:{bob_id} 0 199                      │
│       (Bob's pre-built inbox: normal user posts)      │
│    2. For each celebrity Bob follows:                 │
│       ZREVRANGE posts:{celebrity_id} 0 9             │
│       (On-demand fetch: celebrity latest posts)       │
│    3. Merge-sort both lists by timestamp             │
│    4. Return top 20                                   │
│                                                        │
│ RESULT: Bob's feed is fast (inbox pre-built +        │
│   small merge overhead for celebrities)               │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Fan-out on write (push model in Python/Redis)**

```python
import redis
from kafka import KafkaConsumer
import json

r = redis.Redis(host="redis", port=6379)

FEED_MAX_SIZE = 1000  # max inbox size per user

def fan_out_post(user_id: int, post_id: int, ts: float):
    """
    Fan-out worker: distribute post to all followers.
    Called by Kafka consumer, not in the hot write path.
    """
    # Get follower list (could be millions)
    follower_ids = get_followers(user_id)

    # Batch pipeline to Redis for efficiency
    pipe = r.pipeline()
    for follower_id in follower_ids:
        feed_key = f"feed:{follower_id}"
        # ZADD: sorted set score = timestamp (for ordering)
        pipe.zadd(feed_key, {str(post_id): ts})
        # ZREMRANGEBYRANK: keep only N most recent
        pipe.zremrangebyrank(feed_key, 0, -(FEED_MAX_SIZE + 1))
    pipe.execute()

def get_feed(user_id: int, limit: int = 20) -> list:
    """Read pre-built feed inbox. O(1) per user."""
    feed_key = f"feed:{user_id}"
    # Get post IDs ordered by timestamp (newest first)
    post_ids = r.zrevrange(feed_key, 0, limit - 1)
    return [fetch_post(pid.decode()) for pid in post_ids]

# Kafka consumer: async fan-out (does not block post creation)
consumer = KafkaConsumer("new_posts",
    bootstrap_servers=["kafka:9092"])
for message in consumer:
    post = json.loads(message.value)
    fan_out_post(post["user_id"], post["post_id"], post["ts"])
```

**Example 2 - Fan-out on read (pull model)**

```python
def get_feed_pull(user_id: int, limit: int = 20) -> list:
    """
    Fan-out on read: fetch from followed accounts at read time.
    Simpler to implement but expensive at scale.
    """
    # Step 1: get accounts this user follows
    following_ids = get_following(user_id)  # could be 5000

    if not following_ids:
        return []

    # Step 2: for each followed account, fetch recent posts
    # Use Redis pipeline for parallel fetching
    pipe = r.pipeline()
    for fid in following_ids:
        pipe.zrevrange(f"posts:{fid}", 0, 4)  # latest 5 each
    all_post_ids = pipe.execute()  # [[ids], [ids], ...]

    # Step 3: flatten and sort by timestamp
    flat = [pid for sublist in all_post_ids for pid in sublist]
    posts = [fetch_post(pid.decode()) for pid in flat]
    posts.sort(key=lambda p: p["created_at"], reverse=True)
    return posts[:limit]

# Problem: following 2000 accounts = 2000 Redis ZREVRANGE
# At 100K users/sec: 200M Redis ops/sec (too expensive)
# Solution: use hybrid model (below)
```

**Example 3 - Hybrid model: celebrity detection**

```python
CELEBRITY_THRESHOLD = 5_000  # followers > 5K = celebrity

def is_celebrity(user_id: int) -> bool:
    """Check if user is a celebrity (too many followers)."""
    return get_follower_count(user_id) > CELEBRITY_THRESHOLD

def get_feed_hybrid(user_id: int, limit: int = 20) -> list:
    """
    Hybrid: pre-built inbox for normal users +
    on-demand pull for celebrity posts.
    """
    # Step 1: get inbox (pre-built from fan-out on write)
    inbox_post_ids = r.zrevrange(f"feed:{user_id}", 0, 99)
    inbox_posts = [fetch_post(pid) for pid in inbox_post_ids]

    # Step 2: find celebrity accounts this user follows
    following = get_following(user_id)
    celebrities = [uid for uid in following
                   if is_celebrity(uid)]

    # Step 3: on-demand fetch of celebrity posts
    pipe = r.pipeline()
    for celeb_id in celebrities:
        pipe.zrevrange(f"posts:{celeb_id}", 0, 9)
    celeb_post_ids = pipe.execute()
    celeb_posts = [
        fetch_post(pid)
        for ids in celeb_post_ids
        for pid in ids
    ]

    # Step 4: merge-sort and return top N
    all_posts = inbox_posts + celeb_posts
    all_posts.sort(key=lambda p: p["created_at"], reverse=True)
    return all_posts[:limit]
```

---

### ⚖️ Comparison Table

| Property              | Fan-Out on Write             | Fan-Out on Read       | Hybrid                    |
| --------------------- | ---------------------------- | --------------------- | ------------------------- |
| **Write cost**        | O(followers)                 | O(1)                  | O(normal_followers)       |
| **Read cost**         | O(1)                         | O(following)          | O(1) + O(celebrity_count) |
| **Celebrity problem** | Catastrophic (write spike)   | None                  | Solved (pull celebrities) |
| **Freshness**         | Slight delay (async fan-out) | Real-time             | Mixed                     |
| **Storage**           | High (N copies per post)     | Low (1 copy per post) | Medium                    |
| **Implementation**    | Complex (fan-out workers)    | Simple                | Most complex              |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                               |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fan-out on write is always faster for reads | Read latency depends on both the feed fetch AND the post detail fetch. If fan-out on write inboxes store only post IDs, the read must still fetch each post separately. The inbox fetch is O(1) but the post hydration is O(limit). Fan-out on read with a post cache can have similar total latency. |
| Fan-out on read is always simpler           | For users following 5,000 accounts, fan-out on read requires 5,000 database queries per feed request. Without caching, this is slower than a pre-built inbox.                                                                                                                                         |
| The threshold for "celebrity" is fixed      | Celebrity threshold is tunable and load-dependent. Under heavy write load, lower the threshold (more users become "celebrities" and are excluded from write fan-out). Under heavy read load, raise it (more users get pre-built inboxes). This is an operational knob.                                |

---

### 🚨 Failure Modes & Diagnosis

**Fan-Out Lag (Delayed Feed Delivery)**

**Symptom:**
A user posts a message. Their followers' feeds do not
show the post for 5-10 minutes. The fan-out queue
(Kafka topic) has a growing consumer lag of 5 million
messages.

**Root Cause:**
Fan-out worker throughput is insufficient to process
the Kafka backlog. A celebrity with 10M followers posted,
creating 10M fan-out tasks in the queue. Workers process
100K/sec → 100 seconds to clear the backlog.

**Diagnosis:**

```bash
# Check Kafka consumer group lag
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe \
  --group fanout-worker

# Output shows LAG column growing
# TOPIC    PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG
# new_posts 0       5000000       15000000     10000000

# Identify which post caused the spike:
# Check which user_id generated the largest fan-out
# in the last 10 minutes
```

**Fix:**

```python
# Add celebrity bypass in fan-out publisher
# (prevents large fan-out tasks from entering queue)

def on_post_created(user_id: int, post_id: int):
    if is_celebrity(user_id):
        # Celebrity: publish to posts sorted set only
        # No fan-out; followers will pull on demand
        r.zadd(f"posts:{user_id}", {post_id: time.time()})
    else:
        # Normal user: publish to Kafka for fan-out
        kafka.send("new_posts",
                   {"user_id": user_id, "post_id": post_id})
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Sharding` - feed inboxes are sharded by user_id
- `Read-Heavy vs Write-Heavy Design` - fan-out
  determines which path is more expensive

**Builds On This (learn these next):**

- `News Feed Design` - applies fan-out strategy in
  a full system design answer
- `Push vs Pull Architecture` - the same push/pull
  tradeoff applied to broader system design

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ FAN-OUT WRITE │ Write O(followers); Read O(1)           │
│               │ Celebrity problem: spike on post        │
├───────────────┼─────────────────────────────────────────┤
│ FAN-OUT READ  │ Write O(1); Read O(following)           │
│               │ Scale problem: 5K follows = 5K queries  │
├───────────────┼─────────────────────────────────────────┤
│ HYBRID        │ Push for normal; pull for celebrities   │
│               │ Merge at read time; standard in practice│
├───────────────┼─────────────────────────────────────────┤
│ CELEBRITY     │ Threshold: follower count (tunable)     │
│               │ Exclude from write fan-out              │
│               │ Fetch latest posts on read (on-demand)  │
├───────────────┼─────────────────────────────────────────┤
│ ASYNC FAN-OUT │ Kafka + fan-out workers (decouple)      │
│               │ Monitor: Kafka consumer lag             │
├───────────────┼─────────────────────────────────────────┤
│ INBOX         │ Redis sorted set: score = timestamp     │
│               │ ZREVRANGE for newest-first reads        │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Push = pre-built inbox; Pull = on-deman│
│               │  assembly. Hybrid: push for normal,     │
│               │  pull for celebrities."                 │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Push vs Pull → News Feed Design         │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Fan-out on write: pre-build inbox at post time.
   Read is O(1). Celebrity problem: 1 post creates
   50M writes. Solved by hybrid.
2. Fan-out on read: assemble feed on demand. Write
   is O(1). Following 5,000 accounts = 5,000 reads
   per feed. Solved by caching.
3. Hybrid (standard): fan-out on write for normal users,
   fan-out on read for celebrities. Celebrities identified
   by follower threshold. Merge at read time. Used by
   Twitter, Instagram, Facebook.

**Interview one-liner:**
"Fan-out on write pre-delivers posts to all followers' inboxes
at write time. Read is O(1). But a celebrity posting to 50M
followers creates 50M writes per post - catastrophic write
amplification. Fan-out on read assembles the feed dynamically,
but following 5,000 accounts requires 5,000 queries per feed
request. The hybrid model solves both problems: fan-out on
write for normal users, fan-out on read for celebrities above
a follower threshold. At read time, merge the pre-built inbox
with on-demand celebrity posts. Implemented with Kafka for
async fan-out, Redis sorted sets for inboxes (score =
timestamp for ordering), and a configurable celebrity
threshold that can be tuned based on write load."
