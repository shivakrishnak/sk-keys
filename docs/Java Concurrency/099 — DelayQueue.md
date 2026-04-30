---
layout: default
title: "DelayQueue"
parent: "Java Concurrency"
nav_order: 99
permalink: /java-concurrency/delayqueue/
number: "099"
category: Java Concurrency
difficulty: ★★☆
depends_on: BlockingQueue, PriorityQueue, Delayed
used_by: Scheduled Tasks, Cache Expiry, Rate Limiting, Session Timeout
tags: #java, #concurrency, #queue, #delay, #time-based
---

# 099 — DelayQueue

`#java` `#concurrency` `#queue` `#delay` `#time-based`

⚡ TL;DR — DelayQueue is a BlockingQueue that only releases elements after their individual delay expires — elements implement `Delayed` to specify when they become available; consumers block until the earliest element's time arrives.

| #099 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | BlockingQueue, PriorityQueue, Delayed | |
| **Used by:** | Scheduled Tasks, Cache Expiry, Rate Limiting, Session Timeout | |

---

### 📘 Textbook Definition

`java.util.concurrent.DelayQueue<E extends Delayed>` is an unbounded `BlockingQueue` backed by a `PriorityQueue`. Elements implement the `Delayed` interface (`getDelay(TimeUnit)` and `compareTo`). The queue is ordered by expiry time; `take()` blocks until the element at the head has expired (`getDelay() <= 0`). Elements that have not expired are not accessible. Used internally by `ScheduledThreadPoolExecutor` to store scheduled tasks.

---

### 🟢 Simple Definition (Easy)

DelayQueue is a queue where items have an expiry time. You can only `take()` an item after its time is up. Items added "in the future" wait invisibly in the queue. The next item to expire always comes out first. Like a ticket machine that only dispenses when your number is called — at a scheduled time.

---

### 🔵 Simple Definition (Elaborated)

DelayQueue is ideal for time-based work: session expiry (expire a session object 30 minutes after last access), cache eviction (evict a cache entry after TTL), retries with backoff (schedule retry after 5 seconds), or rate limiting (make tokens available after fixed intervals). The consumer thread blocks cheaply until the next expiry rather than polling in a loop.

---

### 🔩 First Principles Explanation

```
Without DelayQueue — manual polling:
  while (true) {
    for (Entry e : cache.entries())
      if (System.nanoTime() >= e.expiryNanos) evict(e);
    Thread.sleep(100); // poll every 100ms
  }
  → Wasted CPU; imprecise timing; complex

With DelayQueue:
  queue.put(new ExpiringEntry(key, value, 30, TimeUnit.MINUTES));
  ...
  // On consumer thread:
  ExpiringEntry expired = queue.take(); // blocks until expiry time
  evict(expired);
  // Precise: wakes EXACTLY when next item expires
  // No polling overhead; heap-ordered for O(log n) insertion

Internal structure:
  PriorityQueue ordered by getDelay() ascending (smallest delay = earliest expiry)
  take():
    Lock
    head = peek()
    if (head == null) → wait (nothing to expire yet)
    if (head.getDelay(NANOS) > 0) → wait until that delay
    else → return head (expired!)
```

---

### 🧠 Mental Model / Analogy

> A parking lot exit timer. Each car has a parking ticket baked-in expiry time. The attendant (`take()`) checks the front of the queue — if the ticket at the front hasn't expired, they wait. When it does, they process that car and check the next. Cars added with future times queue up invisibly, sorted by expiry.

---

### ⚙️ How It Works

```
Implementing Delayed:
  class ExpiringTask implements Delayed {
    private final long expiryNanos;

    ExpiringTask(long delay, TimeUnit unit) {
      this.expiryNanos = System.nanoTime() + unit.toNanos(delay);
    }

    @Override
    public long getDelay(TimeUnit unit) {
      return unit.convert(expiryNanos - System.nanoTime(), NANOSECONDS);
    }

    @Override
    public int compareTo(Delayed other) {
      return Long.compare(
        this.getDelay(NANOSECONDS),
        other.getDelay(NANOSECONDS)
      );
    }
  }

Key methods:
  put(E e)    → add element (blocks only if capacity limited — DelayQueue is unbounded)
  offer(E e)  → always returns true (unbounded)
  take()      → blocks until head element has expired
  poll()      → returns head if expired, else null (non-blocking)
  poll(timeout, unit) → wait up to timeout for an expired element
  peek()      → returns head (possibly unexpired); null if empty
  drainTo(collection) → drain all EXPIRED elements into collection at once
```

---

### 🔄 How It Connects

```
DelayQueue
  ├─ Backed by     → PriorityQueue (heap-ordered by expiry)
  ├─ Used in       → ScheduledThreadPoolExecutor (stores ScheduledFuture tasks)
  ├─ vs PriorityBlockingQueue → PBQ is order-based; DelayQueue is time-gated
  ├─ vs Timer/ScheduledExecutorService → those schedule execution; DelayQueue stores expirable data
  └─ Use cases     → TTL cache, session expiry, delayed retry, rate limiter tokens
```

---

### 💻 Code Example

```java
// TTL Cache expiry using DelayQueue
public class TTLCache<K, V> {
    private final Map<K, V>              data    = new ConcurrentHashMap<>();
    private final DelayQueue<ExpiryKey<K>> expiry  = new DelayQueue<>();

    public void put(K key, V value, long ttl, TimeUnit unit) {
        data.put(key, value);
        expiry.put(new ExpiryKey<>(key, ttl, unit));
    }

    public V get(K key) { return data.get(key); }

    // Background eviction thread — blocks until next TTL fires
    public void startEviction() {
        new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    ExpiryKey<K> expired = expiry.take(); // precise blocking wait
                    data.remove(expired.key);
                } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            }
        }, "ttl-eviction").start();
    }

    static class ExpiryKey<K> implements Delayed {
        final K    key;
        final long expiryNanos;

        ExpiryKey(K key, long delay, TimeUnit unit) {
            this.key = key;
            this.expiryNanos = System.nanoTime() + unit.toNanos(delay);
        }

        @Override
        public long getDelay(TimeUnit unit) {
            return unit.convert(expiryNanos - System.nanoTime(), TimeUnit.NANOSECONDS);
        }

        @Override
        public int compareTo(Delayed other) {
            return Long.compare(getDelay(TimeUnit.NANOSECONDS), other.getDelay(TimeUnit.NANOSECONDS));
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `put()` blocks until delay expires | `put()` adds immediately; only `take()/poll()` respect the delay |
| DelayQueue is bounded | Unbounded — add any number of elements; only retrieval is time-gated |
| `peek()` returns only expired elements | `peek()` returns the head element regardless of whether it's expired |
| Delays are guaranteed to be millisecond-precise | Precision depends on OS timer resolution and JVM implementation |

---

### 🔥 Pitfalls in Production

**Pitfall: getDelay() returning negative — already expired at insertion**

```java
// If you accidentally pass a past time as expiry:
new ExpiryKey<>(key, -5, TimeUnit.SECONDS); // expiryNanos already in the past
// Element inserted and immediately available — take() returns it right away
// Not a bug, just surprising; ensure delay >= 0 if you want future expiry
```

---

### 🔗 Related Keywords

- **[BlockingQueue](./081 — BlockingQueue.md)** — parent interface
- **[ScheduledExecutorService](./093 — ScheduledExecutorService.md)** — uses DelayQueue internally
- **[PriorityBlockingQueue](./100 — PriorityBlockingQueue.md)** — order-based (not time-based)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Elements only available after their per-item  │
│              │ delay expires; min-heap ordered by expiry     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ TTL cache eviction; session expiry; delayed   │
│              │ retries; rate limiter token refill            │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Scheduling code execution → ScheduledExecutorService;│
│              │ need bounded size → custom implementation     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Each item has its own alarm clock —          │
│              │  take() sleeps until the next alarm rings"    │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ScheduledExecutorService → PriorityBlockingQueue│
│              │ → Caffeine cache (uses DelayQueue internally) │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ScheduledThreadPoolExecutor` uses `DelayQueue` internally. How does it convert a `scheduleAtFixedRate(task, 5, 5, SECONDS)` call into an element in the `DelayQueue`? What happens when the task's delay expires?

**Q2.** Two elements in a `DelayQueue` have the same expiry time. In what order are they returned by `take()`? What does `compareTo()` returning 0 mean for the internal heap?

**Q3.** Your DelayQueue-based TTL cache holds 1 million entries. Each `put()` is O(log n) in the embedded PriorityQueue. What is the performance impact of a sudden burst of 100,000 entries all with the same TTL? How does `drainTo()` help?

