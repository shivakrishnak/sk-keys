---
layout: default
title: "Fan-Out on Write vs Read"
parent: "System Design"
nav_order: 710
permalink: /system-design/fan-out-on-write-vs-read/
number: "710"
category: System Design
difficulty: ★★★
depends_on: "Denormalization for Scale, Read-Heavy vs Write-Heavy Design, Caching"
used_by: "News Feed Design, Push vs Pull Architecture"
tags: #advanced, #distributed, #architecture, #social, #performance
---

# 710 — Fan-Out on Write vs Read

`#advanced` `#distributed` `#architecture` `#social` `#performance`

⚡ TL;DR — **Fan-Out on Write** pre-computes and pushes content to followers' feeds when published; **Fan-Out on Read** computes feeds on-demand at read time — the choice determines write vs. read cost, with read-heavy systems favouring write fan-out and celebrity users requiring a hybrid.

| #710 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Denormalization for Scale, Read-Heavy vs Write-Heavy Design, Caching | |
| **Used by:** | News Feed Design, Push vs Pull Architecture | |

---

### 📘 Textbook Definition

**Fan-Out on Write** (Push Model): when a user publishes content, the system immediately writes copies (or references) of that content to the feeds of all followers. Reads are fast (pre-computed feed is ready in a cache), but writes are expensive and proportional to follower count. For a user with 10M followers, one post triggers 10M fan-out writes. **Fan-Out on Read** (Pull Model): when a user reads their feed, the system dynamically queries all accounts the user follows, merges and sorts their recent content, and returns the result. Writes are cheap (one write per post), but reads are expensive (N queries to merge N followed accounts' posts). In practice, large-scale social platforms (Twitter, Facebook, Instagram) use **hybrid fan-out**: pre-compute feeds for non-celebrities (fan-out on write), inject celebrity posts at read time (fan-out on read for high-follower-count accounts), since pre-computing feeds for Beyoncé's 20M followers on every tweet is prohibitively expensive.

---

### 🟢 Simple Definition (Easy)

Fan-Out on Write: when you post a photo, Instagram immediately puts a copy in every follower's inbox. When they open the app, their inbox is already full — instant read. Fan-Out on Read: when a follower opens the app, the app fetches posts from every account they follow, combines them, and shows the result. Slow to read, but no work was done at post time. Trade: fast reads (write fan-out) vs. fast writes (read fan-out).

---

### 🔵 Simple Definition (Elaborated)

Twitter read path in 2012: 600K QPS on a MySQL cluster. Engineers realised: 99% of users just read; writing one tweet causes 300+ reads (all followers check for new tweets). Switched to pre-computed Redis timeline caches (fan-out on write). Result: user opens app → read one Redis key → instant timeline. The write path sends one tweet → writes to N followers' timeline caches. Problem: celebrity with 10M followers posts → 10M Redis write operations instantly → Redis overloaded → switched to hybrid: regular users = fan-out on write; celebrities = not pre-fanned-out → injected at read time.

---

### 🔩 First Principles Explanation

**Three fan-out strategies with implementation details:**

```
STRATEGY 1: FAN-OUT ON WRITE (Push Model)

  At write time:
    1. User Alice (500 followers) posts tweet T1
    2. Write T1 to Alice's post store (primary)
    3. For each follower F1...F500:
       - Write reference to T1 in F's timeline cache (Redis sorted set)
    4. Return 200 OK to Alice
    
  At read time:
    1. User Bob opens app (follows Alice)
    2. Read Bob's timeline cache (Redis ZRANGE key 0 99 REV):
       → Returns pre-sorted list of tweet IDs
    3. Fetch tweet content for those IDs (Redis or post store)
    4. Render feed — typically < 10ms total
    
  DATA STRUCTURE (Redis Sorted Set per user):
    Key: "timeline:user:{user_id}"
    Score: tweet creation timestamp (for time-ordering)
    Member: tweet_id
    
    ZADD timeline:user:bob 1700000001 tweet_123   # Alice's tweet
    ZADD timeline:user:bob 1700000050 tweet_456   # Carol's tweet
    ZRANGE timeline:user:bob 0 99 REV             # Bob's feed: newest first
    
  WRITE COST:
    500 followers → 500 ZADD operations per tweet
    Twitter peak (6,000 tweets/sec × avg 200 followers) = 1.2M Redis writes/sec
    
  READ COST:
    1 ZRANGE operation → O(log(N) + M) where N=timeline size, M=results returned
    Very fast. Redis: 100K+ ops/sec per node.
    
  ADVANTAGES:
    - Read path: O(1) per user (single Redis read)
    - Read latency: predictable, sub-10ms
    - No real-time aggregation needed at read time
    
  DISADVANTAGES:
    - Write amplification: 1 tweet → N fan-out writes (N = follower count)
    - Celebrity problem: celebrity with 10M followers → 10M writes per tweet
    - Inactive users: timeline cache written even for users who never open app
    - Storage: N timelines × M items per timeline → large Redis memory usage

STRATEGY 2: FAN-OUT ON READ (Pull Model)

  At write time:
    1. User Alice posts tweet T1
    2. Write T1 to Alice's post store only
    3. Return 200 OK — done (cheap write)
    
  At read time:
    1. User Bob opens app
    2. Query: who does Bob follow? → follows table: [Alice, Carol, Dave]
    3. For each followed user: fetch their recent posts:
       SELECT * FROM posts WHERE user_id = Alice_id AND created_at > ? LIMIT 50
       SELECT * FROM posts WHERE user_id = Carol_id AND created_at > ? LIMIT 50
       SELECT * FROM posts WHERE user_id = Dave_id AND created_at > ? LIMIT 50
    4. Merge and sort all results by time
    5. Return top 50 posts
    
  WRITE COST: O(1) — one database write per post regardless of followers
  READ COST: O(N) — N queries where N = number of accounts user follows
  
  PROBLEM at scale:
    Bob follows 1,000 accounts.
    Read path: 1,000 database queries → merge sort 50,000 posts → return 50.
    At 1M users × 1,000 queries each = 1B DB queries for one feed refresh.
    Latency: 1,000 sequential queries × 10ms = 10 seconds (unacceptable).
    
  WHEN FAN-OUT ON READ IS ACCEPTABLE:
    - Small follower/following counts (< 50 per user)
    - Low traffic systems
    - Internal tools, private social networks

STRATEGY 3: HYBRID (industry standard for large-scale social platforms)

  DECISION RULE:
    if followed_user.follower_count < CELEBRITY_THRESHOLD:   # e.g., 1,000,000
      use FAN-OUT ON WRITE (pre-compute their posts into followers' feeds)
    else:
      use FAN-OUT ON READ (inject celebrity posts at read time)
      
  READ PATH (hybrid):
    1. User Bob opens app
    2. Fetch Bob's pre-computed timeline cache (fan-out on write: normal users)
    3. Fetch posts from celebrity accounts Bob follows (fan-out on read: celebrities)
    4. Merge: pre-computed timeline + celebrity posts (usually 2-3 celebrities max)
    5. Return top 50 sorted by time
    
  Timeline merge (Redis + DB):
    // Pre-computed (ZADD for normal followed users):
    timeline_ids = redis.ZRANGE("timeline:bob", 0, 499, REV)
    
    // Celebrities: real-time query (only a few per user):
    celebrity_posts = celebrities_bob_follows.map(celeb =>
      db.query("SELECT id FROM posts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", celeb.id)
    )
    
    // Merge and sort:
    all_post_ids = merge_sort(timeline_ids, celebrity_posts)
    posts = db.batchGet("SELECT * FROM posts WHERE id IN (?)", all_post_ids[0:50])
    
  CELEBRITY THRESHOLD TUNING:
    Too low (100): too many "celebrities" → too much fan-out on read computation
    Too high (10M): many high-follower users doing fan-out on write → Redis overloaded
    Twitter: ~1M followers threshold (approximate)
    Instagram: similar hybrid threshold

INACTIVE USER OPTIMISATION:
  
  Problem: fan-out on write writes to inactive users' caches (wasteful).
  
  Solution: LAZY FAN-OUT
    Don't fan-out to users inactive for > 7 days.
    When inactive user returns: rebuild timeline by fan-out on read (one-time catch-up).
    Mark user active again → resume fan-out on write.
    
  Storage savings: 30% of social media users inactive on any given day.
  Fan-out writes reduced by 30%.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Fan-Out on Write (pure fan-out on read):
- Feed read: 1,000 DB queries per user → 10-second load time → unusable
- Database overwhelmed: 1M concurrent feed reads × 1,000 queries = 1B DB operations

WITH Fan-Out on Write:
→ Feed read: 1 Redis operation → 10ms response → smooth user experience
→ Write amplification accepted: 1 post × 500 followers = 500 Redis writes (fast, async)
→ Celebrities handled separately: hybrid prevents 10M-write storms per celebrity tweet

---

### 🧠 Mental Model / Analogy

> Newspaper delivery (fan-out on write): every morning, the press prints 500,000 newspapers and delivers one to every subscriber before they wake up. When subscribers open their door, the paper is ready instantly. Cost: 500,000 deliveries per edition (proportional to subscribers). vs. Library model (fan-out on read): no home delivery. Readers go to the library, browse all sections, find today's relevant articles themselves. Cost: each reader must browse everything. One newspaper printed; N readers do the work themselves.

"Newspaper press printing 500,000 copies" = fan-out on write (write time work)
"Pre-delivered to every door" = pre-computed timeline in each user's Redis cache
"Instant read when subscriber opens door" = O(1) feed read from pre-computed cache
"Library: one copy, readers browse" = fan-out on read (read time work)
"Celebrity = newspaper edition seen by millions" = celebrity fan-out exception (too expensive to pre-deliver)

---

### ⚙️ How It Works (Mechanism)

**Fan-out on write with Kafka + async workers:**

```java
// POST endpoint: create a tweet
@RestController
public class TweetController {
    
    @PostMapping("/tweets")
    public ResponseEntity<Tweet> createTweet(
            @RequestBody CreateTweetRequest request,
            @AuthenticationPrincipal User author) {
        
        // 1. Save tweet to primary store (fast):
        Tweet tweet = tweetService.saveTweet(author.getId(), request.getContent());
        
        // 2. Async fan-out: publish to Kafka (non-blocking):
        kafkaTemplate.send("tweet-created", new TweetCreatedEvent(
            tweet.getId(), author.getId(), tweet.getCreatedAt()
        ));
        
        // 3. Return immediately — fan-out happens asynchronously:
        return ResponseEntity.ok(tweet);
    }
}

// Fan-out worker (Kafka consumer):
@KafkaListener(topics = "tweet-created", groupId = "timeline-fanout")
public class TimelineFanoutWorker {
    
    @Autowired private FollowerRepository followerRepository;
    @Autowired private RedisTemplate<String, String> redisTemplate;
    @Autowired private UserService userService;
    
    private static final int CELEBRITY_THRESHOLD = 1_000_000;
    
    public void handleTweetCreated(TweetCreatedEvent event) {
        User author = userService.findById(event.getAuthorId());
        
        // Don't fan-out celebrities (handled at read time):
        if (author.getFollowerCount() >= CELEBRITY_THRESHOLD) {
            return;  // Read path will inject celebrity posts dynamically
        }
        
        // Fan-out to all followers:
        List<Long> followerIds = followerRepository.findFollowerIds(event.getAuthorId());
        
        followerIds.forEach(followerId -> {
            // Add to follower's timeline (Redis sorted set, score = timestamp):
            String timelineKey = "timeline:" + followerId;
            redisTemplate.opsForZSet().add(
                timelineKey,
                String.valueOf(event.getTweetId()),
                event.getCreatedAt().toEpochMilli()
            );
            // Trim to last 1000 tweets per timeline:
            redisTemplate.opsForZSet().removeRange(timelineKey, 0, -1001);
        });
    }
}

// READ endpoint: get user's feed
@GetMapping("/feed")
public List<Tweet> getFeed(@AuthenticationPrincipal User user) {
    // 1. Get pre-computed timeline:
    Set<String> tweetIds = redisTemplate.opsForZSet()
        .reverseRange("timeline:" + user.getId(), 0, 49);
    
    // 2. Get celebrity posts (real-time query — small list):
    List<Long> celebrityIds = userService.getCelebrityFollows(user.getId());
    List<Tweet> celebrityPosts = tweetService.getRecentPosts(celebrityIds, 10);
    
    // 3. Merge and return:
    List<Tweet> feedTweets = tweetService.batchGet(tweetIds);
    return mergeSortByTime(feedTweets, celebrityPosts).subList(0, 50);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
User posts content
        │
        ▼
Fan-Out on Write vs Read ◄──── (you are here)
        │
        ├── Fan-Out on Write → Redis timeline cache (push to followers)
        ├── Fan-Out on Read  → DB scatter-gather (compute at read time)
        └── Hybrid → pre-compute normal users, inject celebrities at read
                │
                ▼
        News Feed Design, Push vs Pull Architecture
```

---

### 💻 Code Example

**Redis timeline simulation (Python):**

```python
import redis
import time

r = redis.Redis()

def post_tweet(author_id: int, tweet_id: int, followers: list[int]):
    """Fan-out on write: push tweet to all followers' timelines."""
    timestamp = time.time()
    
    # Save tweet (primary store — simplified):
    r.hset(f"tweet:{tweet_id}", mapping={
        "author_id": author_id,
        "content": f"Tweet {tweet_id} by user {author_id}",
        "created_at": timestamp
    })
    
    # Fan-out to followers (fan-out on write):
    for follower_id in followers:
        timeline_key = f"timeline:{follower_id}"
        r.zadd(timeline_key, {str(tweet_id): timestamp})
        r.zremrangebyrank(timeline_key, 0, -1001)  # keep last 1000

def get_feed(user_id: int, page: int = 0, per_page: int = 20) -> list:
    """Fan-out on write read: single Redis ZRANGE."""
    start = page * per_page
    end = start + per_page - 1
    
    tweet_ids = r.zrevrange(f"timeline:{user_id}", start, end)
    
    # Batch fetch tweet content:
    return [r.hgetall(f"tweet:{tid.decode()}") for tid in tweet_ids]

# Simulation:
# Alice (user 1) posts tweet 101, has followers [2, 3, 4, 5]:
post_tweet(author_id=1, tweet_id=101, followers=[2, 3, 4, 5])

# Bob (user 2) reads his feed:
feed = get_feed(user_id=2)
print(feed)  # [{'author_id': b'1', 'content': b'Tweet 101 by user 1', ...}]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Fan-out on write is always better because reads are faster | For celebrities (millions of followers), fan-out on write is prohibitively expensive and creates write storms. Hybrid approaches are used by all major social platforms precisely because neither pure strategy works at scale with highly skewed follower distributions |
| Fan-out on read is obsolete/bad | Fan-out on read is appropriate for: small-scale systems, private networks, apps with small average following counts, enterprise tools. It's simple, consistent, and storage-efficient. The complexity of fan-out on write is only justified when feed read latency is clearly the bottleneck |
| Timeline caches are the source of truth for tweets | Timeline caches are derived data (like a materialised view). The source of truth is the primary tweet store. Caches can be lost and rebuilt from the primary store. A lost timeline cache means a user's feed looks empty until rebuilt — not that tweets are lost |
| Fan-out on write requires synchronous writes to all followers | Fan-out should always be asynchronous (Kafka queue + workers). The user posting a tweet should NOT wait for all followers' caches to be updated. Accept eventual consistency: followers' feeds update within seconds (typically < 5s at Twitter/Instagram scale) |

---

### 🔥 Pitfalls in Production

**Synchronous fan-out blocks tweet publishing:**

```
PROBLEM: Fan-out done synchronously in tweet POST endpoint

  @PostMapping("/tweets")
  public ResponseEntity<Tweet> createTweet(...) {
    Tweet tweet = tweetService.save(...);
    
    // WRONG: synchronous fan-out
    List<Long> followers = followerRepository.findAll(author.getId());  // 500K followers
    followers.forEach(fid -> redisTemplate.zadd("timeline:" + fid, ...));  // 500K Redis writes
    
    return ResponseEntity.ok(tweet);
    // User waits: 500K × 0.1ms = 50 seconds!!
  }
  
CORRECT: Async fan-out via Kafka

  @PostMapping("/tweets")
  public ResponseEntity<Tweet> createTweet(...) {
    Tweet tweet = tweetService.save(...);
    kafkaTemplate.send("tweet-created", event);  // non-blocking: 1ms
    return ResponseEntity.ok(tweet);             // returns in ~5ms
    // Fan-out: happens asynchronously over the next 1-5 seconds
  }
  
  ADDITIONAL PROTECTION: Fan-out worker rate limiting
  
  Celebrity with 10M followers posts a tweet:
  Without throttling: 10M fan-out writes in < 1 second → Redis overloaded.
  
  With throttling: 
    Fan-out worker: processes 10K fan-outs/sec per partition.
    10M / 10K = 1,000 seconds to complete fan-out.
    
  For celebrities: don't fan-out at all (hybrid approach):
    if (followerCount > CELEBRITY_THRESHOLD) publishAsyncCelebrityPost(tweet);
    // Readers fetch celebrity posts directly at read time.
```

---

### 🔗 Related Keywords

- `Denormalization for Scale` — fan-out on write is denormalization of the timeline (redundant copies per follower)
- `Read-Heavy vs Write-Heavy Design` — fan-out choice directly affects which path is optimised
- `Push vs Pull Architecture` — fan-out on write = push; fan-out on read = pull
- `News Feed Design` — applies fan-out strategy as core architecture decision
- `Hot Shard` — celebrity fan-out causes hot shard on the celebrity's data shard

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Write fan-out: fast reads, slow writes;   │
│              │ Read fan-out: fast writes, slow reads     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Write fan-out: normal users (<1M follows);│
│              │ Read fan-out: celebrities, small systems  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sync fan-out (always async via queue);    │
│              │ write fan-out for 10M+ follower accounts  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Newspaper delivery vs library — choose   │
│              │  who does the work: publisher or reader." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ News Feed Design → Push vs Pull           │
│              │ → Hot Shard                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the fan-out system for an Instagram-scale platform: 1 billion users, average 300 followers each, 500M posts per day (6,000 posts/second). For a user with 300 followers posting a photo: (a) how many Redis write operations does fan-out on write require per second at peak? (b) At 0.1ms per Redis operation, how long does fan-out take per post, and how does Kafka async fan-out change the user experience? (c) Design the celebrity threshold: at what follower count does fan-out on write become impractical? Calculate based on acceptable Redis write operations per second.

**Q2.** You're building the "For You" feed for a new social platform. Unlike a simple timeline (showing only content from followed accounts), the For You feed shows algorithmically ranked content from all users. How does fan-out on write fail completely for this use case? What architecture would you use instead? Does fan-out on read work, or does this require a completely different approach (hint: think about offline compute, ML ranking, and pre-scored content pools)?
