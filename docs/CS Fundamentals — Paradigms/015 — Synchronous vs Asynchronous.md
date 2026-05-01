---
layout: default
title: "Synchronous vs Asynchronous"
parent: "CS Fundamentals — Paradigms"
nav_order: 15
permalink: /cs-fundamentals/synchronous-vs-asynchronous/
number: "15"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming, Procedural Programming
used_by: Concurrency vs Parallelism, Event-Driven Programming, Reactive Programming, Node.js
tags: #foundational, #concurrency, #performance, #pattern
---

# 15 — Synchronous vs Asynchronous

`#foundational` `#concurrency` `#performance` `#pattern`

⚡ TL;DR — Synchronous operations block until complete; asynchronous operations return immediately and notify the caller when done.

| #15             | Category: CS Fundamentals — Paradigms                                               | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Imperative Programming, Procedural Programming                                      |                 |
| **Used by:**    | Concurrency vs Parallelism, Event-Driven Programming, Reactive Programming, Node.js |                 |

---

### 📘 Textbook Definition

A **synchronous** operation is one where the caller blocks — suspending further execution — until the operation completes and returns a result. A **asynchronous** operation is one where the caller initiates the operation and immediately regains control; the result is delivered later via a callback, promise, future, or event. Synchronous code is simpler to reason about (sequential, predictable) but wastes CPU time waiting during I/O. Asynchronous code enables a thread (or single event loop) to initiate many I/O operations and handle results as they arrive, dramatically improving throughput for I/O-bound workloads.

---

### 🟢 Simple Definition (Easy)

Synchronous means "wait here until it's done." Asynchronous means "start it and I'll come back when it's ready — tell me when."

---

### 🔵 Simple Definition (Elaborated)

When you call a synchronous function, your code stops at that line until the function finishes. If that function makes a database query taking 50ms, your thread does nothing for 50ms. Asynchronous code avoids this: you start the database query and immediately move on to other work; when the query finishes, a callback runs or a promise resolves to give you the result. For servers handling thousands of simultaneous users, the difference is enormous: a synchronous server with 200 threads can serve only 200 concurrent requests; an asynchronous server with a handful of threads can serve tens of thousands because no thread ever sits idle waiting.

---

### 🔩 First Principles Explanation

**The problem: I/O is orders of magnitude slower than the CPU.**

| Operation          | Approximate time | CPU cycles wasted (3GHz) |
| ------------------ | ---------------- | ------------------------ |
| L1 cache read      | 0.5 ns           | 1                        |
| RAM access         | 100 ns           | 300                      |
| SSD read           | 100 µs           | 300,000                  |
| Network round-trip | 1 ms             | 3,000,000                |
| Database query     | 10 ms            | 30,000,000               |

A thread blocked on a database query wastes 30 million CPU cycles doing nothing.

**Synchronous model — one thread per blocked operation:**

```
Thread 1: send DB query ────────────────── wait ──────────────► receive result
Thread 2:                  send DB query ─────── wait ─────────► receive result
Thread 3:                                 send DB ─── wait ────► receive result

3 threads tied up. With 10,000 concurrent requests: 10,000 threads × ~1MB stack = 10 GB RAM.
```

**Asynchronous model — one thread, many in-flight operations:**

```
Thread 1: send DB query 1  →  send DB query 2  →  send DB query 3
                                      ↓                ↓               ↓
                             result 2 handler   result 3 handler  result 1 handler
                             (called when done) (called when done)(called when done)

1 thread handles all three. 10,000 requests: still ~1–4 threads.
```

**The insight:** a thread's _time_ is the scarce resource, not its _count_. Async frees threads from waiting so they handle more work.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT async (all synchronous, thread-per-request):

```java
// Spring MVC, synchronous: one thread per request
@GetMapping("/user/{id}")
public User getUser(@PathVariable Long id) {
    return userRepository.findById(id).orElseThrow(); // thread blocks ~10ms
}
// 10,000 concurrent requests = 10,000 blocked threads = OOM
```

What breaks without async:

1. Thread stacks exhaust heap memory under high concurrency.
2. OS context switches between thousands of threads add latency overhead.
3. A slow downstream service causes all threads to pile up — cascade failure.
4. Throughput ceiling = thread pool size, not hardware capacity.

WITH async:
→ Threads never block on I/O — a pool of 10–50 threads serves 10,000 concurrent users.
→ Slow downstream services slow their own response, not all other responses.
→ Memory proportional to active work, not pending waits.
→ Throughput scales to I/O parallelism capacity.

---

### 🧠 Mental Model / Analogy

> Think of two restaurant styles. **Synchronous**: one waiter per table. The waiter stands beside you from the moment you sit until you finish eating and pay — doing nothing else the whole time. 200 customers need 200 waiters. **Asynchronous**: one waiter serves many tables. They take your order (initiate request), bring someone else's food (handle other work), check on a third table (handle another callback), then bring your food when it's ready (callback fires). 200 customers need 5–10 waiters.

"Waiter standing idle waiting for you to eat" = thread blocked on I/O
"Waiter taking order and moving on" = initiating an async operation
"Kitchen calling the waiter when food is ready" = callback / promise resolution
"Number of waiters" = thread pool size

Asynchronous is not about speed — one meal still takes the same time. It is about the _waiter's utilisation_ — the same thread can serve far more concurrent operations.

---

### ⚙️ How It Works (Mechanism)

**Synchronous call — blocking:**

```
┌─────────────────────────────────────────────────────┐
│             Synchronous Execution                   │
│                                                     │
│  Thread:  ─── call DB ────────────────── return ──► │
│                       │ blocked: waiting │           │
│                       └──────────────────┘           │
│  Thread does NOTHING during the wait period         │
└─────────────────────────────────────────────────────┘
```

**Asynchronous call — non-blocking with callback:**

```
┌─────────────────────────────────────────────────────┐
│            Asynchronous Execution                   │
│                                                     │
│  Thread: ── initiate DB call ──► continue other work│
│                │                                    │
│                └── OS/NIO kernel handles I/O ───┐   │
│                                                 │   │
│  Thread: ◄─── callback invoked when done ───────┘   │
│  (thread was free to do other work in between)      │
└─────────────────────────────────────────────────────┘
```

**Java async mechanisms — evolution:**

```
Java 1.0: Thread.start() — raw threads (heavyweight)
Java 5:   Future / ExecutorService — submit tasks, get results
Java 8:   CompletableFuture — composable async pipelines
Java 21:  Virtual Threads (Project Loom) — write sync-style
          code, JVM makes it async under the hood
```

**CompletableFuture pipeline:**

```java
CompletableFuture
    .supplyAsync(() -> userService.findUser(id))    // async
    .thenApply(user -> orderService.findOrders(user)) // chain
    .thenApply(orders -> orders.stream()
        .filter(Order::isActive).count())
    .exceptionally(ex -> {
        log.error("Failed", ex);
        return 0L;
    })
    .thenAccept(count -> response.send(count));
```

---

### 🔄 How It Connects (Mini-Map)

```
Imperative / Procedural Programming (sequential by default)
        │
        ▼
Synchronous vs Asynchronous  ◄──── (you are here)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
Concurrency vs Parallelism          Event-Driven Programming
        │                                      │
        ▼                                      ▼
Java Concurrency                        Node.js (event loop)
(CompletableFuture, Virtual Threads)   (async/await, Promises)
        │
        ▼
Reactive Programming (async streams)
```

---

### 💻 Code Example

**Example 1 — Sync vs async HTTP calls in Java:**

```java
// SYNCHRONOUS: thread blocks for each response
RestTemplate rest = new RestTemplate();
User user     = rest.getForObject("/users/1", User.class);   // block
Profile prof  = rest.getForObject("/profiles/1", Profile.class); // block
// Total time: user-time + profile-time (sequential)

// ASYNCHRONOUS: both calls in-flight simultaneously
WebClient client = WebClient.create();
Mono<User>    userMono = client.get().uri("/users/1")
    .retrieve().bodyToMono(User.class);
Mono<Profile> profMono = client.get().uri("/profiles/1")
    .retrieve().bodyToMono(Profile.class);

Mono.zip(userMono, profMono)
    .subscribe(tuple -> respond(tuple.getT1(), tuple.getT2()));
// Total time ≈ max(user-time, profile-time) — run in parallel
```

**Example 2 — JavaScript async/await:**

```javascript
// SYNCHRONOUS (blocking — never do this in Node.js)
const data = fs.readFileSync("data.json"); // blocks event loop!

// ASYNCHRONOUS with async/await (non-blocking, reads clearly)
async function loadData() {
  const data = await fs.promises.readFile("data.json");
  return JSON.parse(data); // only runs after file is read
}

// Two operations in parallel
async function loadBoth() {
  const [users, orders] = await Promise.all([
    loadUsers(), // both started simultaneously
    loadOrders(), // neither blocks the other
  ]);
  return { users, orders };
}
```

**Example 3 — Java 21 virtual threads (sync code, async behaviour):**

```java
// Virtual threads: write synchronous-style code,
// JVM suspends the virtual thread during I/O (not the OS thread)
try (ExecutorService exec =
        Executors.newVirtualThreadPerTaskExecutor()) {

    for (int i = 0; i < 100_000; i++) {
        exec.submit(() -> {
            // This LOOKS synchronous but is backed by a virtual thread
            String result = httpClient.send(request,
                BodyHandlers.ofString()).body(); // "blocks" — actually suspends
            process(result);
        });
    }
}
// 100,000 "blocking" tasks on a handful of OS threads
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                               |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Async code is always faster                             | Async adds overhead (callback allocation, context switching, scheduler); for CPU-bound work with no I/O waits, synchronous code is simpler and equally fast           |
| async/await means non-blocking                          | `await` suspends the _current coroutine/virtual thread_, not necessarily the OS thread; on a thread pool, the OS thread may be reused for another task while awaiting |
| Async eliminates the need for multiple threads          | For CPU-bound parallelism, you still need multiple threads; async handles I/O concurrency on fewer threads, not CPU-bound work                                        |
| Synchronous code cannot be concurrent                   | Java's Virtual Threads allow synchronous-looking code to run with async efficiency — the JVM handles the non-blocking I/O underneath                                  |
| Promises / Futures and async/await are different things | `async/await` is syntactic sugar over Promises (JavaScript) or CompletableFuture (Java); both represent the same asynchronous computation model                       |

---

### 🔥 Pitfalls in Production

**Mixing blocking calls into async frameworks**

```java
// BAD: blocking JDBC call inside reactive WebFlux handler
@GetMapping("/users/{id}")
public Mono<User> getUser(@PathVariable Long id) {
    // findByIdBlocking() blocks the Netty I/O thread!
    return Mono.just(userRepository.findByIdBlocking(id));
}

// GOOD: use reactive repository or wrap in boundedElastic
@GetMapping("/users/{id}")
public Mono<User> getUser(@PathVariable Long id) {
    return Mono.fromCallable(() -> userRepository.findByIdBlocking(id))
               .subscribeOn(Schedulers.boundedElastic());
}
```

---

**Not handling async errors — silent failure**

```javascript
// BAD: unhandled promise rejection — error silently swallowed
async function processOrder(id) {
  const order = await fetchOrder(id); // if this throws, nobody knows
  return order.total;
}

// GOOD: explicit error handling
async function processOrder(id) {
  try {
    const order = await fetchOrder(id);
    return order.total;
  } catch (err) {
    logger.error("fetchOrder failed", { id, err });
    throw err; // re-throw so caller can handle
  }
}
```

---

**Async in a loop creating unbounded concurrency**

```javascript
// BAD: fires 10,000 parallel requests — exhausts connections
const results = await Promise.all(
  ids.map((id) => fetchFromApi(id)), // 10,000 simultaneous requests
);

// GOOD: batch with a concurrency limit
import pLimit from "p-limit";
const limit = pLimit(20); // max 20 concurrent
const results = await Promise.all(
  ids.map((id) => limit(() => fetchFromApi(id))),
);
```

---

### 🔗 Related Keywords

- `Concurrency vs Parallelism` — async is the mechanism that enables concurrency; parallelism requires multiple cores
- `Event-Driven Programming` — the paradigm built entirely on asynchronous event handling
- `Reactive Programming` — extends async to composable, backpressured streams of events
- `Callback` — the original async notification mechanism; superseded by Promises, async/await
- `CompletableFuture` — Java 8's composable async computation pipeline
- `Virtual Threads` — Java 21 feature enabling synchronous-style code with async efficiency
- `Node.js` — the most prominent single-threaded async runtime based on an event loop
- `Blocking I/O vs Non-Blocking I/O` — the OS-level mechanism underlying synchronous vs async

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sync: caller waits, thread blocked.       │
│              │ Async: caller continues, notified later.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sync: simple scripts, CPU-bound work,     │
│              │ low-concurrency services                  │
│              │ Async: high-concurrency I/O-bound servers │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Async for CPU-bound: adds overhead,       │
│              │ no blocking to avoid                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Async is not about speed — it's about    │
│              │ never leaving a thread idle while waiting."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Concurrency vs Parallelism → Event Loop   │
│              │ → CompletableFuture → Virtual Threads     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot service uses `@Async` methods backed by a `ThreadPoolTaskExecutor` with a pool size of 50. Under load, 50 threads are all blocked on JDBC calls averaging 200ms. New requests queue behind them. A colleague suggests switching to Spring WebFlux with R2DBC. Describe exactly what changes in the threading model, why throughput increases without changing the database query time, and what specific code changes the migration requires.

**Q2.** JavaScript's `async/await` makes async code look synchronous. A developer writes `await fetch(url)` inside a `for` loop processing 1,000 URLs. The total time is approximately 1,000 × (network latency). Rewrite the logic to reduce total time to approximately 1 × (network latency), explain which JavaScript scheduling guarantees make this safe, and identify one scenario where sequential `await` in a loop is intentionally correct.
