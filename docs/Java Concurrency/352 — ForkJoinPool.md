---
layout: default
title: "ForkJoinPool"
parent: "Java Concurrency"
nav_order: 352
permalink: /java-concurrency/forkjoinpool/
number: "352"
category: Java Concurrency
difficulty: ★★★
depends_on: ExecutorService, RecursiveTask, Thread, Parallel Streams
used_by: Parallel Streams, CompletableFuture, Arrays.parallelSort
tags: #java, #concurrency, #fork-join, #parallel, #work-stealing
---

# 352 — ForkJoinPool

`#java` `#concurrency` `#fork-join` `#parallel` `#work-stealing`

⚡ TL;DR — ForkJoinPool is a thread pool optimised for divide-and-conquer recursive tasks via work-stealing: idle threads steal subtasks from busy threads' queues, maximising CPU utilisation for decomposable parallel workloads.

| #352 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | ExecutorService, RecursiveTask, Thread, Parallel Streams | |
| **Used by:** | Parallel Streams, CompletableFuture, Arrays.parallelSort | |

---

### 📘 Textbook Definition

`java.util.concurrent.ForkJoinPool` is a specialized `ExecutorService` that implements the **fork-join** framework for parallel recursive decomposition. Tasks implement `RecursiveTask<V>` (returns a result) or `RecursiveAction` (void). `fork()` submits a subtask asynchronously; `join()` waits for and retrieves its result. The pool uses **work-stealing**: each worker thread has a deque; idle threads steal from the tail of busy threads' deques — minimising idle time. The `commonPool()` static instance is shared by `parallelStream()` and default `CompletableFuture` operations.

---

### 🟢 Simple Definition (Easy)

ForkJoinPool is for "divide and conquer" problems: split a big task into smaller tasks, compute them in parallel, combine results. The clever part (work-stealing): if one thread finishes early, it steals pending work from another busy thread — nobody sits idle.

---

### 🔵 Simple Definition (Elaborated)

Regular thread pools are great for independent tasks. But recursive algorithms (merge sort, tree traversal, sum over large array) create unpredictable numbers of subtasks with dependencies. ForkJoinPool handles this elegantly: each thread has its own deque of tasks; it processes its own tasks LIFO (which keeps parent tasks near the top — good for cache); idle threads steal FIFO from other threads' deques (which grabs oldest/biggest subtasks first — good for load balancing). This makes work-stealing highly efficient for tree-shaped computations.

---

### 🔩 First Principles Explanation

```
Problem: sum 1 million integers in parallel

Sequential: for (int x : array) sum += x;  → uses 1 CPU

Naive ExecutorService approach:
  Divide 1M into N chunks → N tasks → all submitted upfront
  Works but inflexible chunk size calculation needed

ForkJoinPool approach (flexible recursion):
  sumTask(0, 1_000_000):
    if size <= threshold: compute directly
    else:
      left  = fork sumTask(0, 500_000)    ← async
      right = fork sumTask(500_000, 1M)   ← async
      return left.join() + right.join()

Binary tree of tasks: created dynamically, sized by threshold
Work-stealing: idle thread steals "left" subtasks while parent does "right"
→ Near-linear speedup up to core count
```

**Work-stealing mechanics:**

```
Thread 1 queue: [task_A, task_B, task_C]  (LIFO own deque)
Thread 2: idle → steals task_C from T1's tail (FIFO steal)
                                      ↑
                        Steal from TAIL (oldest tasks, smallest subtrees)
                        → avoids syncing on frequently-used HEAD
```

---

### 🧠 Mental Model / Analogy

> A team of workers solving a jigsaw puzzle. Each worker takes a section, breaks it into smaller pieces, and works on one while handing off the other. Workers who finish their piece look around and **steal** a piece from the busiest worker's pile. Nobody waits — everyone is always working on something. The puzzle (computation) completes as fast as the hardware allows.

---

### ⚙️ How It Works

```
Key classes:
  ForkJoinPool              → the executor (use commonPool() usually)
  RecursiveTask<V>          → task with a return value
  RecursiveAction           → task without a return value

Key methods in RecursiveTask:
  fork()                    → submit THIS task async to pool (returns immediately)
  join()                    → wait for result (may help execute other tasks while waiting)
  invoke()                  → fork + join in one call (use for root task)
  invokeAll(task1, task2)   → fork both, join both (balanced split pattern)

ForkJoinPool:
  commonPool()              → shared pool; size = available processors - 1
  new ForkJoinPool(N)       → custom parallelism level
  pool.invoke(task)         → submit root task and wait for result
  pool.submit(task)         → submit and get ForkJoinTask (like Future)
  pool.getParallelism()     → configured thread count
```

---

### 🔄 How It Connects

```
ForkJoinPool
  │
  ├─ Used by Parallel Streams (Stream.parallel()) → uses commonPool
  ├─ Used by CompletableFuture default executor   → uses commonPool
  ├─ Used by Arrays.parallelSort()                → uses commonPool
  │
  ├─ vs ExecutorService  → FJP is for recursive decomposition; ES for independent tasks
  ├─ Common Pool warning → long-blocking tasks in commonPool starve parallel streams
  └─ Custom pool         → for isolation: new ForkJoinPool(parallelism)
```

---

### 💻 Code Example

```java
// RecursiveTask — parallel array sum
public class SumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 10_000;
    private final int[] array;
    private final int start, end;

    public SumTask(int[] array, int start, int end) {
        this.array = array; this.start = start; this.end = end;
    }

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            // Base case: compute directly
            long sum = 0;
            for (int i = start; i < end; i++) sum += array[i];
            return sum;
        }
        // Recursive case: split in half
        int mid = (start + end) / 2;
        SumTask left  = new SumTask(array, start, mid);
        SumTask right = new SumTask(array, mid,   end);

        left.fork();                        // submit left async
        long rightResult = right.compute(); // compute right in THIS thread
        long leftResult  = left.join();     // retrieve left result
        return leftResult + rightResult;
    }
}

// Usage:
int[] data = IntStream.rangeClosed(1, 1_000_000).toArray();
ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(data, 0, data.length));
System.out.println("Sum: " + total); // 500000500000
```

```java
// Parallel stream — uses ForkJoinPool.commonPool() under the hood
long sum = IntStream.rangeClosed(1, 1_000_000)
    .parallel()       // switches to commonPool
    .asLongStream()
    .sum();

// Custom ForkJoinPool for parallel stream (isolation from commonPool)
ForkJoinPool customPool = new ForkJoinPool(4);
long result = customPool.submit(() ->
    IntStream.rangeClosed(1, 1_000_000).parallel().asLongStream().sum()
).get();
customPool.shutdown();
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| ForkJoinPool is always better than ExecutorService | FJP excels at recursive decomposition; ES is better for independent tasks |
| commonPool is safe for blocking I/O | Blocking in commonPool starves parallel streams across the JVM; use separate pool |
| fork() + join() is the only pattern | `invokeAll(left, right)` and `right.compute(); left.join()` are idiomatic variations |
| RecursiveTask creates one thread per task | Tasks are lightweight — many tasks share few threads via work-stealing |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Blocking I/O in ForkJoinPool (or parallel streams)**

```java
// ❌ Blocking DB call in parallel stream → starves commonPool → all parallel streams slow
list.parallelStream().map(id -> dbQuery(id)).collect(toList());

// ✅ Use a dedicated pool for I/O-bound parallel work
ForkJoinPool ioPool = new ForkJoinPool(50);
ioPool.submit(() -> list.parallelStream().map(id -> dbQuery(id)).collect(toList())).get();
```

**Pitfall 2: Too-small threshold → too many tasks (overhead > benefit)**

```java
// ❌ Threshold of 1 → 1M tasks for 1M elements → scheduling overhead dominates
if (end - start <= 1) { return array[start]; }

// ✅ Profile and set threshold: typically 1000–10000 elements
if (end - start <= 10_000) { /* sequential */ }
```

---

### 🔗 Related Keywords

- **[ExecutorService](./074 — ExecutorService.md)** — simpler pool for independent tasks
- **[Virtual Threads](./085 — Virtual Threads.md)** — Java 21 I/O alternative
- **[CompletableFuture](./075 — Future and CompletableFuture.md)** — uses commonPool by default
- **Parallel Streams** — syntactic sugar over ForkJoinPool

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Divide-and-conquer pool with work-stealing    │
│              │ idle threads steal from busy: max CPU use     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ CPU-bound recursive tasks (sort, sum, search, │
│              │ tree traversal); parallel algorithms          │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Blocking I/O in commonPool; independent tasks │
│              │ (use ExecutorService); tiny sub-task overhead  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Fork it, steal it, join it —                 │
│              │  every CPU always has something to do"        │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ RecursiveTask → Parallel Streams →            │
│              │ CompletableFuture → Virtual Threads           │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The `right.compute(); left.join()` pattern (compute right in current thread, fork left, then join left) is preferred over `left.fork(); right.fork(); left.join(); right.join()`. Why? What happens to the current thread in the second pattern?

**Q2.** `ForkJoinPool.commonPool()` has parallelism = available processors - 1 by default. What happens when you run a blocking operation in the pool (e.g. `Thread.sleep(1000)`)? How does `ManagedBlocker` solve this?

**Q3.** How does the work-stealing deque prevent contention between the thread owning the deque and the stealing threads? (Hint: think about which end of the deque is used by each.)

