---
layout: default
title: "Parallel Streams"
parent: "Java Concurrency"
nav_order: 92
permalink: /java-concurrency/parallel-streams/
number: "092"
category: Java Concurrency
difficulty: ★★☆
depends_on: ForkJoinPool, Stream API, Spliterator
used_by: Bulk Data Processing, CPU-bound Collections, Arrays.parallelSort
tags: #java, #concurrency, #parallel-streams, #forkjoin, #streams
---

# 092 — Parallel Streams

`#java` `#concurrency` `#parallel-streams` `#forkjoin` `#streams`

⚡ TL;DR — `stream.parallel()` splits the stream's source, processes chunks in parallel across ForkJoinPool.commonPool() threads, then merges results — easy to add but only beneficial for CPU-bound work on large datasets with no shared state.

| #092 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ForkJoinPool, Stream API, Spliterator | |
| **Used by:** | Bulk Data Processing, CPU-bound Collections, Arrays.parallelSort | |

---

### 📘 Textbook Definition

A **parallel stream** is created via `collection.parallelStream()` or `stream.parallel()`. The stream pipeline is executed using the **fork-join framework**: the data source is split by a `Spliterator` into chunks; each chunk is processed as a `RecursiveTask` in `ForkJoinPool.commonPool()`; partial results are combined via the stream's reduce/collect terminal operation. Parallel streams are best suited for stateless, associative operations on large, splittable datasets. They use the JVM-wide `commonPool` — blocking I/O inside a parallel stream pollutes this shared pool.

---

### 🟢 Simple Definition (Easy)

Instead of processing a list one element at a time (sequential), parallel streams divide the list among all CPU cores and process each chunk simultaneously. Just add `.parallel()` to a stream. Potential speedup: up to N× where N = number of CPU cores.

---

### 🔵 Simple Definition (Elaborated)

Parallel streams are syntactic sugar over ForkJoinPool. The trade-offs are non-obvious: parallelism has overhead (splitting, thread scheduling, merging). For small datasets or I/O-heavy operations, parallelism HURTS. For CPU-bound operations on large arrays (millions of elements), it can give near-linear speedup. Always benchmark before adding `.parallel()` — it is NOT "free performance" and can cause subtle bugs with stateful operations.

---

### 🔩 First Principles Explanation

```
Sequential stream:
  [1,2,3,4,5,6,7,8] → process each in order → result

Parallel stream:
  [1,2,3,4,5,6,7,8]
       ↓ Spliterator splits
  [1,2] [3,4] [5,6] [7,8]
    ↓     ↓     ↓     ↓
  Thread1 Thread2 Thread3 Thread4  (ForkJoinPool workers)
    ↓     ↓     ↓     ↓
  result1 result2 result3 result4
       ↓ merge/combine
       final result

Cost analysis:
  Sequential: N * elementCost
  Parallel  : (N / cores) * elementCost + splittingCost + mergeCost + scheduling

  Parallel wins when:
    elementCost is HIGH (CPU-bound, e.g. complex calculation)
    N is LARGE (millions of elements)
    mergeCost is LOW (simple sum, max → not complex aggregation)

  Parallel loses when:
    elementCost is LOW (simple lookup)
    N is SMALL (< thousands)
    Source is not easily splittable (LinkedList, I/O stream)
    Operations have side effects or shared state
```

---

### 🧠 Mental Model / Analogy

> Parallel streams are like splitting a large document between 8 people to each highlight key phrases (process), then merging all highlighted copies into one document (reduce). Splitting and merging takes time — only worth it if each person's chunk takes significant time to process.

---

### ⚙️ How It Works

```
Source splitting: Spliterator
  ArrayList → splits by index (O(1), excellent)
  LinkedList → splits poorly (O(n) to split)
  HashSet   → moderate splitting
  IntStream.range() → perfect splitting

Execution: ForkJoinPool.commonPool()
  Default parallelism = Runtime.getRuntime().availableProcessors() - 1
  All parallel stream operations share this pool
  BLOCKING inside parallel stream → starves other parallel streams globally

Combining: terminal operation's combiner
  .sum() → add partial sums (associative, easy)
  .collect(toList()) → merge sublists (requires combiner in Collector)
  .reduce(identity, accumulator, combiner) → explicit combiner
```

---

### 🔄 How It Connects

```
Parallel Streams
  │
  ├─ Uses           → ForkJoinPool.commonPool() 
  ├─ vs ForkJoinPool → parallel stream = automatic; FJP = manual control
  ├─ Stateless ops  → map, filter, mapToInt — safe for parallel
  ├─ Stateful ops   → sorted, distinct, limit — may break or reduce speedup
  └─ Custom pool    → new ForkJoinPool(N).submit(() -> stream.parallel()...)
```

---

### 💻 Code Example

```java
// ✅ Good use: CPU-bound, large, stateless
long sum = LongStream.rangeClosed(1, 10_000_000)
    .parallel()
    .filter(n -> isPrime(n))  // expensive CPU operation
    .count();
// Likely 4-8× faster on multicore vs sequential

// ❌ Bad use: I/O-bound, small collection
List<String> result = smallList.parallelStream()
    .map(id -> dbQuery(id))  // BLOCKS commonPool threads
    .collect(Collectors.toList());
// Slower than sequential + pollutes commonPool
```

```java
// Custom ForkJoinPool — isolate from commonPool
ForkJoinPool customPool = new ForkJoinPool(8);
List<Result> results = customPool.submit(() ->
    items.parallelStream()
         .map(item -> process(item))
         .collect(Collectors.toList())
).get();
customPool.shutdown();
```

```java
// Stateful operation bug — shared mutable state
List<Integer> results = new ArrayList<>();
// ❌ Race condition: multiple threads write to results simultaneously
IntStream.range(0, 1000).parallel().forEach(i -> results.add(i));
// results may have duplicates, nulls, or wrong size

// ✅ Fix: use thread-safe collection or collect properly
List<Integer> safe = IntStream.range(0, 1000)
    .parallel()
    .boxed()
    .collect(Collectors.toList()); // Collectors.toList() is thread-safe in this context
```

```java
// Benchmarking parallel vs sequential (always measure!)
// Sequential:
Instant start = Instant.now();
long seqSum = LongStream.rangeClosed(1, 1_000_000).filter(n -> n % 2 == 0).sum();
long seqMs = Duration.between(start, Instant.now()).toMillis();

// Parallel:
start = Instant.now();
long parSum = LongStream.rangeClosed(1, 1_000_000).parallel().filter(n -> n % 2 == 0).sum();
long parMs = Duration.between(start, Instant.now()).toMillis();

System.out.printf("Sequential: %dms, Parallel: %dms%n", seqMs, parMs);
// For small, simple operations: parallel is often SLOWER due to overhead
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `.parallel()` always makes code faster | Parallel has overhead; small/simple streams are often slower in parallel |
| Parallel streams are thread-safe for all ops | Stateful operations (e.g., writing to shared list) still cause race conditions |
| `sorted()` on parallel stream is efficient | `sorted()` requires all elements to merge → negates parallel benefit |
| Parallel stream doesn't affect other streams | All parallel streams share `commonPool()` — blocking one starves others globally |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Blocking I/O in parallel stream → commonPool starvation**

```java
// ❌ All commonPool threads blocked on DB → all parallel streams across JVM blocked
userIds.parallelStream()
    .map(id -> userRepository.findById(id).orElseThrow())  // blocks!
    .collect(Collectors.toList());

// ✅ Use separate pool for I/O or use virtual threads
ForkJoinPool ioPool = new ForkJoinPool(50);
ioPool.submit(() -> userIds.parallelStream()
    .map(id -> userRepository.findById(id).orElseThrow())
    .collect(Collectors.toList())).get();
```

**Pitfall 2: forEach with shared mutable state**

```java
Map<String, Integer> map = new HashMap<>(); // not thread-safe!
stream.parallel().forEach((k, v) -> map.put(k, v)); // ❌ race condition

// ✅ Fix: use thread-safe collector or ConcurrentHashMap
Map<String, Integer> result = stream.parallel()
    .collect(Collectors.toConcurrentMap(k -> k, v -> 1)); // thread-safe
```

---

### 🔗 Related Keywords

- **[ForkJoinPool](./084 — ForkJoinPool.md)** — the execution engine for parallel streams
- **[Race Condition](./072 — Race Condition.md)** — stateful parallel stream ops create race conditions
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — thread-safe collector for parallel streams
- **[Virtual Threads](./085 — Virtual Threads.md)** — better choice for I/O-bound parallel work

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Split-process-merge on ForkJoinPool.commonPool│
│              │ — easy but only beneficial for large CPU work │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Large (>10K), CPU-bound, stateless operations:│
│              │ sorting, filtering with heavy predicates      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Small collections; I/O-bound; stateful ops;   │
│              │ shared mutable state; ordered output required │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Divide the list across cores and combine —   │
│              │  only win if the per-element work is heavy"   │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ForkJoinPool → Spliterator → Arrays.parallelSort│
│              │ → Virtual Threads (for I/O) → Project Reactor │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `LinkedList` splits poorly for parallel streams (O(n) traversal to split). What `Spliterator` property is checked to determine splitability? What collections have the best characteristics for parallel streams?

**Q2.** You run `stream.parallel().sorted().limit(10)` on a list of 10 million elements. Why does `sorted()` hurt parallelism here specifically? What optimisation could you apply to still get speedup?

**Q3.** `Stream.parallel()` and `Stream.sequential()` can be called at any point in the pipeline. If you call `.parallel()` midway and `.sequential()` at the end, what is the final execution mode? Why?

