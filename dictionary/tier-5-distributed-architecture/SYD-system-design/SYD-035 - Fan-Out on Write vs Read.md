---
layout: default
title: "Fan-Out on Write vs Read"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /system-design/fan-out-on-write-vs-read/
id: SYD-035
category: System Design
difficulty: ★★★
depends_on: Caching, Database Design, Distributed Systems
used_by: Feed Systems, Notification Services, Real-Time Systems
related: Push vs Pull, Caching, Denormalization
tags:
  - architecture
  - advanced
  - messaging
  - scalability
  - design-pattern
---

# SYD-035 - Fan-Out on Write vs Read

⚡ TL;DR - Two strategies for distributing content (tweets, notifications). Fan-out on write: push to all followers on tweet (slow write, fast read). Fan-out on read: compute feed dynamically at read time (fast write, slow read). Choose based on read/write ratio.

| #710            | Category: System Design                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Caching, Database Design, Distributed Systems          |                 |
| **Used by:**    | Feed Systems, Notification Services, Real-Time Systems |                 |
| **Related:**    | Push vs Pull, Caching, Denormalization                 |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
User tweets. 100M followers read feed. When to compute feed? When tweet posted (fan-out write)? Or when user refreshes (fan-out read)?

**TRADE-OFF:**
Write latency vs. read latency.

---

### 📘 Textbook Definition

**Fan-Out on Write vs Read:** Architecture pattern decision for content distribution. Fan-out on write: pre-compute and cache feed on write (slow write, fast read). Fan-out on read: compute feed dynamically on read request (fast write, slow read).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Tweet → push to all followers' feeds (fan-out write). OR user refresh → compute feed dynamically (fan-out read).

**One analogy:**

> Newspaper: (1) Fan-out write: print 1M copies on publication day (slow production, instant delivery). (2) Fan-out read: print on-demand per request (fast production, slow delivery).

**One insight:**
Choose based on read/write ratio.

---

### 🧠 Mental Model

```
FAN-OUT ON WRITE (Eager):
  Tweet posted → immediately push to 100M followers' feeds
  Data flow:
    DB → Cache layer → all follower caches (broadcast)
  Cost: Write: 100M pushes (slow). Read: instant lookup.
  Good for: Read-heavy (Twitter: 1000 reads per tweet)

FAN-OUT ON READ (Lazy):
  User opens feed → dynamically compute from all 5000 follows
  Data flow:
    DB ← all 5000 follows (scan) ← rank/sort
  Cost: Read: compute + scan (slow). Write: instant insert.
  Good for: Write-heavy, or few followers per user

HYBRID (Smart):
  Celebrity with 100M followers: fan-out write (too expensive)
  Normal user with 500 followers: fan-out write (feasible)
  Switch strategy based on follower count
```

---

### 📶 Gradual Depth

**Level 1:** Tweet = write once. Feed read = compute from tweets. Choose when.

**Level 2:** Fan-out write: slow write, fast read. Fan-out read: fast write, slow read.

**Level 3:** Twitter uses hybrid: normal users (fan-out write), celebrities (fan-out read). Rationale: celebrities have too many followers to push individually.

**Level 4:** Fan-out on write emerged from social media (Twitter 2009 era). Initially all write-fanout, then became bottleneck with celebrity tweets. Switched to hybrid. Fan-out on read used for edge cases (celebrities) to avoid broadcast storms.

---

### ⚙️ How It Works

```
SCENARIO: Twitter
─────────────────

FAN-OUT ON WRITE (Original)
  Alice tweets "Hello" (5000 followers)

  Time 1 (Write): 5 seconds
    Alice → DB insert
    Fanout: push to all 5000 followers' Redis caches
    (iterate followers, set key "feed:follower_id": [tweet, ...])
    Time: ~5 sec (fanout heavy)

  Time 2 (Read): 10ms
    Bob opens feed: lookup "feed:bob" in Redis
    Result: instant (already pre-computed)

  Problem: celebrity (100M followers)
    Fanout: 100M updates (network hell, 50+ seconds)
    Not viable!

FAN-OUT ON READ (Workaround for celebrities)
  Elon tweets "SpaceX launch" (100M followers)

  Time 1 (Write): 10ms
    Elon → DB insert tweet
    No fanout (instant)

  Time 2 (Read): 1-2 seconds
    Bob opens feed: lookup followers (5000)
    Scan tweets from all 5000 (database query)
    Sort by timestamp and engagement
    Return top 50
    Time: ~1-2 sec (slow but acceptable)

  Trade: reads slower, but write instant

HYBRID DECISION LOGIC
─────────────────────
if follower_count < 1000:
  use_fan_out_write()  # Push to all caches
elif follower_count < 100_000:
  use_fan_out_write_batched()  # Batch push asynchronously
else:
  use_fan_out_read()  # Compute on read
```

---

### 💻 Code Example

```python
class FeedSystem:
    def __init__(self):
        self.db = Database()
        self.cache = Redis()

    # FAN-OUT ON WRITE
    def tweet_with_fanout_write(self, user_id, content):
        """Write tweet, push to all follower caches"""
        tweet_id = self.db.insert(f"tweets", {
            'user_id': user_id,
            'content': content,
            'timestamp': time.time()
        })

        # Get followers
        followers = self.db.query(f"SELECT follower_id FROM follows WHERE user_id = {user_id}")

        # Fanout: update each follower's feed cache
        for follower in followers:
            cache_key = f"feed:{follower['follower_id']}"
            self.cache.lpush(cache_key, tweet_id)  # Add to front of feed

        return tweet_id

    def get_feed_from_cache(self, user_id):
        """Get feed instantly (pre-computed)"""
        cache_key = f"feed:{user_id}"
        tweet_ids = self.cache.lrange(cache_key, 0, 49)  # Top 50
        return tweet_ids

    # FAN-OUT ON READ
    def tweet_with_fanout_read(self, user_id, content):
        """Write tweet instantly (no fanout)"""
        tweet_id = self.db.insert("tweets", {
            'user_id': user_id,
            'content': content,
            'timestamp': time.time()
        })
        return tweet_id

    def get_feed_from_db(self, user_id):
        """Get feed by scanning all follows (slower)"""
        # Get all follows
        follows = self.db.query(f"SELECT user_id FROM follows WHERE follower_id = {user_id}")
        follow_ids = [f['user_id'] for f in follows]

        # Get tweets from all followed users
        tweets = self.db.query(f"""
            SELECT * FROM tweets
            WHERE user_id IN ({','.join(map(str, follow_ids))})
            ORDER BY timestamp DESC
            LIMIT 50
        """)

        return tweets

    # HYBRID
    def tweet_hybrid(self, user_id, content):
        """Smart selection based on follower count"""
        follower_count = self.db.query(
            f"SELECT COUNT(*) FROM follows WHERE user_id = {user_id}"
        )['count']

        tweet_id = self.db.insert("tweets", {
            'user_id': user_id,
            'content': content,
            'timestamp': time.time()
        })

        if follower_count < 10_000:
            # Fanout write for normal users
            followers = self.db.query(f"SELECT follower_id FROM follows WHERE user_id = {user_id}")
            for follower in followers:
                cache_key = f"feed:{follower['follower_id']}"
                self.cache.lpush(cache_key, tweet_id)
        else:
            # Fanout read for celebrities (compute on read)
            pass

        return tweet_id

# Usage
feed_system = FeedSystem()

# Normal user: fanout on write (fast reads)
feed_system.tweet_with_fanout_write(user_id=1, content="Hello")
tweets = feed_system.get_feed_from_cache(user_id=2)  # Instant

# Celebrity: fanout on read (fast writes)
feed_system.tweet_with_fanout_read(user_id=12345, content="SpaceX launch")
tweets = feed_system.get_feed_from_db(user_id=2)  # Slower, but write instant
```

---

### ⚠️ Common Misconceptions

| Misconception                  | Reality                                                  |
| ------------------------------ | -------------------------------------------------------- |
| "Always fanout write"          | No. Doesn't scale for celebrities. Use hybrid.           |
| "Fanout on read = always slow" | No. Acceptable for write-heavy or small follower counts. |

---

### 🚨 Failure Modes

**Failure Mode 1: Cache Explosion on Fanout Write**

**Symptom:**
Celebrity tweet fans out to 100M followers. Redis memory exhausted.

**Prevention:**
Detect celebrity. Switch to fanout read. Or batch fanout asynchronously.

---

**Failure Mode 2: Feed Computation Too Slow**

**Symptom:**
User has 5000 follows. Feed computation takes 10 seconds. Unacceptable.

**Prevention:**
Limit follows per user. Or use pre-computed feed (fanout write) for subset.

---

### 📌 Quick Reference

```
Fan-Out Decision:

FAN-OUT ON WRITE:
  Use when: Read-heavy, small follower count (<10K)
  Cost: Slow write, fast read

FAN-OUT ON READ:
  Use when: Write-heavy, large follower count (>100K)
  Cost: Fast write, slow read

HYBRID:
  Use when: Mixed (normal + celebrity users)
  Strategy: Switch based on follower count threshold
```

---

### 🧠 Questions

**Q1.** User has 50M followers. Tweet takes 100 seconds to fanout. How to fix?

**Q2.** Feed computation on read takes 5 seconds. Too slow. How to optimize?
