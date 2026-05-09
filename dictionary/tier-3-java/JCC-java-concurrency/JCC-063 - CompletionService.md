---
id: JCC-063
title: CompletionService
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★☆
depends_on: JCC-029, JCC-013, JCC-059
used_by: JCC-066
related: JCC-058, JCC-030, JCC-014
tags:
  - java
  - concurrency
  - async
  - pattern
  - intermediate
status: complete
version: 1
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 63
permalink: /java-concurrency/completionservice/
---

# JCC-063 - COMPLETIONSERVICE

⚡ **TL;DR** - Submit N tasks and consume results in the order they
*finish*, not the order they were submitted - eliminating head-of-line
blocking.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-029 ExecutorService, JCC-013 Future, JCC-059 CompletableFuture Composition |
| Used by    | JCC-066 Thread Pinning                             |
| Related    | JCC-058 ScheduledExecutorService, JCC-030 ThreadPoolExecutor, JCC-014 CompletableFuture |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You submit 10 tasks to an `ExecutorService` and hold their
`Future` objects in a list. To process results as they arrive, you
call `future.get()` on each in submission order. If task 1 takes
10 seconds but tasks 2-10 complete in 1 second, you wait 10 seconds
on task 1 before ever reading the fast results. This is *head-of-line
blocking* at the application level.

**THE BREAKING POINT:**
An image resizer submits 50 resize tasks. Tasks vary from 50ms to
5s depending on image complexity. The results consumer calls
`get()` on futures in submission order. It blocks on a slow image,
while 40 already-completed fast images wait in completed futures
with results ready but unread. Throughput is determined by the
slowest task encountered first, not by the average.

**THE INVENTION MOMENT:**
`CompletionService` (Java 5) decouples submission from result
consumption using an internal `BlockingQueue`. Completed tasks
enqueue their results; the consumer calls `take()` or `poll()` to
dequeue results in completion order.

**EVOLUTION:**
- **Java 5:** `CompletionService`, `ExecutorCompletionService`
- **Java 8:** `CompletableFuture.anyOf()` as lightweight alternative
  for small numbers of tasks
- **Java 21:** Structured concurrency `StructuredTaskScope` handles
  result collection more explicitly with cancellation support

---

### 📘 Textbook Definition

**`CompletionService<V>`** is an interface in `java.util.concurrent`
that combines `ExecutorService` task submission with a `BlockingQueue`
to deliver results in *completion order* (not submission order).

Key methods:

| Method | Behaviour |
|--------|-----------|
| `submit(Callable)` | Submit task; returns `Future` |
| `take()` | Block until any task completes; return its `Future` |
| `poll()` | Return completed `Future` or null if none ready (non-blocking) |
| `poll(timeout, unit)` | Wait up to timeout for a completed `Future` |

The standard implementation is `ExecutorCompletionService<V>`,
which wraps an existing `ExecutorService`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Like an `ExecutorService` with a results queue: tasks
enqueue themselves when done, and you dequeue whichever finishes
first.

**One analogy:**
> A restaurant with a pass-through counter. Chefs (threads) place
> completed dishes on the counter (BlockingQueue) as soon as they
> finish. The waiter (consumer) picks up dishes in the order they
> appear on the counter - the fastest chef's dish first - without
> waiting for a specific chef's dish.

**One insight:** `CompletionService` transforms the "wait for each
future in submission order" anti-pattern into "process whichever
result is ready" throughput.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Completed tasks place their `Future` onto the internal
   `BlockingQueue` via a `FutureTask` completion hook.
2. `take()` dequeues from the `BlockingQueue`; order = completion
   order, not submission order.
3. The underlying `Executor` is unchanged - `CompletionService`
   only adds a result-routing layer.
4. The consumer must call `take()` exactly as many times as tasks
   were submitted, or `poll()` with a loop until nil.
5. Exceptions from tasks are accessible via `future.get()` which
   re-throws them as `ExecutionException`.

**DERIVED DESIGN:**
`ExecutorCompletionService` wraps each `Callable` in a `QueueingFuture`
that overrides `FutureTask.done()` to call `completionQueue.add(this)`
upon completion. This is the completion hook pattern.

**THE TRADE-OFFS:**

**Gain:** Process results as they arrive; maximise consumer
throughput; no head-of-line blocking.

**Cost:** Must track how many tasks were submitted to know when to
stop calling `take()`. Cannot cancel individual tasks easily once
in the queue. Less composable than `CompletableFuture` chains.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Decouple completion notification from submission
order to enable first-come-first-served result processing.

**Accidental:** The consumer must manually count tasks submitted vs
consumed - there is no "all done" signal built into the interface.

---

### 🧪 Thought Experiment

**SETUP:** Submit 5 tasks with varying runtimes: 5s, 1s, 3s, 2s, 4s.

**WHAT HAPPENS WITHOUT CompletionService:**
```
Submit all 5 tasks, hold futures in a list.
Call future[0].get() -> blocks 5 seconds
Call future[1].get() -> already done (was done in 1s), returns
Call future[2].get() -> returns (done at 3s)
...
Total time to process all results: 5 seconds (wall clock)
BUT you waited 5 seconds for the FIRST result when task 2
finished in 1 second and was ignored.
```

**WHAT HAPPENS WITH CompletionService:**
```
Submit all 5 tasks.
take() -> task 2 completes (1s), process result immediately
take() -> task 4 completes (2s), process result
take() -> task 3 completes (3s), process result
take() -> task 5 completes (4s), process result
take() -> task 1 completes (5s), process result last
```
Consumer gets results at 1s, 2s, 3s, 4s, 5s - not 5s, 5s, 5s, 5s, 5s.

**THE INSIGHT:** `CompletionService` makes the consumer's throughput
bounded by the *average* task time, not the max of whatever
submitted first.

---

### 🧠 Mental Model / Analogy

> Imagine a carwash queue with 5 cars. Without `CompletionService`:
> you stand at the exit of bay 1, watching bay 1 finish regardless
> of whether bays 2-5 are already done. With `CompletionService`:
> there is a single collection window; any car that finishes rolls
> to that window, and you collect cars in the order they park there.

**Element mapping:**
- Cars entering bays = tasks submitted to executor
- Bays = thread pool workers
- Cars parking at collection window = futures added to `BlockingQueue`
- Collector window = `CompletionService.take()`
- You collecting cars = consumer processing results

Where this analogy breaks down: a real carwash collection window
has only one exit lane; the `BlockingQueue` can have many items
queued and the consumer processes one at a time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Submit tasks to a pool; instead of checking which ones are done in
the order you submitted them, you get results in the order the
tasks actually finish.

**Level 2 - How to use it (junior developer):**
```java
ExecutorService executor =
    Executors.newFixedThreadPool(4);
CompletionService<String> cs =
    new ExecutorCompletionService<>(executor);

int count = 10;
for (int i = 0; i < count; i++) {
    cs.submit(() -> doWork());
}

for (int i = 0; i < count; i++) {
    Future<String> f = cs.take(); // blocks until any done
    System.out.println(f.get());  // process in finish order
}
executor.shutdown();
```

**Level 3 - How it works (mid-level engineer):**
`ExecutorCompletionService` wraps each submitted `Callable` in a
`QueueingFuture extends FutureTask<V>`. `FutureTask.done()` is a
hook called after every completion (success or failure). The
`QueueingFuture` overrides `done()` to call
`completionQueue.add(this)`. Workers execute normally; the only
difference is that upon `run()` completion, the result is pushed to
the queue rather than only stored in the `FutureTask` internally.

**Level 4 - Why it was designed this way (senior/staff):**
The design uses the existing `FutureTask.done()` extension hook
rather than post-processing callbacks. This keeps execution logic
in the executor and result routing in a pure data structure
(`BlockingQueue`). The `CompletionService` is thus just a thin
adapter between run-completion events and a queue, with no
scheduler or executor behaviour of its own - maximising composability
with any `Executor` implementation.

**Expert Thinking Cues:**
- Prefer `CompletionService` over iterating `future.get()` whenever
  tasks have variable completion times and results can be processed
  independently.
- Use `poll(timeout)` to implement a "process available results
  within a time budget" pattern.
- Handle `ExecutionException` per-future inside the consume loop -
  one failed task should not discard all remaining results.
- `CompletableFuture.anyOf` and `allOf` are alternatives for small,
  known sets of tasks where composability is more important than
  throughput.

---

### ⚙️ How It Works (Mechanism)

**Internal architecture:**
```
CompletionService wraps ExecutorCompletionService
  |
  +--> internal BlockingQueue<Future<V>>
  |
  +--> submit(callable):
  |       wraps in QueueingFuture
  |       submits to underlying Executor
  |
  +--> QueueingFuture.done(): (called by worker on complete)
  |       completionQueue.add(this)
  |
  +--> take():
          return completionQueue.take() (blocks if empty)
```

**Timeline comparison:**
```
Submission order: T1(5s), T2(1s), T3(3s)

Without CS (future list, get in order):
  t=0     submit all
  t=5     get(f0) returns  <- blocks 5s on t1
  t=5     get(f1) returns  <- already done
  t=5     get(f2) returns  <- already done

With CS (completion queue):
  t=0     submit all
  t=1     take() -> f1 result (t2 done first)
  t=3     take() -> f2 result
  t=5     take() -> f0 result (slowest last)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Create CompletionService(executor)  <- YOU ARE HERE
       |
  Submit N tasks
       |
  Workers execute tasks concurrently
       |
  First task completes:
    QueueingFuture.done() -> queue.add(future)
       |
  Consumer: take() -> dequeues first completed future
       |
  future.get() -> process result
       |
  Repeat N times
       |
  executor.shutdown()
```

**FAILURE PATH:**
Task throws exception -> `QueueingFuture` still enqueues itself
(done() is called regardless of outcome) -> consumer calls
`take()`, gets the future -> `future.get()` throws
`ExecutionException` -> consumer must handle per-task exception.

**WHAT CHANGES AT SCALE:**
- High submission rate: `BlockingQueue` backpressure holds submitted-
  but-not-consumed results in memory; monitor queue size to avoid
  heap pressure.
- With virtual threads: `CompletionService` works identically;
  virtual thread workers complete and enqueue just like platform
  threads.

---

### 💻 Code Example

**BAD - head-of-line blocking with future list:**
```java
// BAD: blocks on task[0] even if tasks[1..9] done
List<Future<Result>> futures = new ArrayList<>();
for (Task t : tasks) {
    futures.add(executor.submit(t));
}
for (Future<Result> f : futures) {
    Result r = f.get(); // blocks on EACH in submission order
    process(r);
}
```

**GOOD - CompletionService for completion-order processing:**
```java
ExecutorService executor =
    Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors());
CompletionService<ImageResult> cs =
    new ExecutorCompletionService<>(executor);

List<Task> tasks = loadTasks(); // variable-time tasks
tasks.forEach(cs::submit);

int remaining = tasks.size();
while (remaining-- > 0) {
    try {
        Future<ImageResult> f = cs.take();
        ImageResult result = f.get();
        saveResult(result); // process as soon as ready
    } catch (ExecutionException e) {
        log.error("Task failed", e.getCause());
        // continue processing other tasks
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        break;
    }
}

executor.shutdown();
```

**GOOD - time-bounded result collection:**
```java
// Process results for up to 10 seconds total
long deadline = System.nanoTime()
    + TimeUnit.SECONDS.toNanos(10);

for (int i = 0; i < taskCount; i++) {
    long remaining = deadline - System.nanoTime();
    if (remaining <= 0) break;

    Future<Result> f =
        cs.poll(remaining, TimeUnit.NANOSECONDS);
    if (f == null) break; // timeout reached

    try {
        process(f.get());
    } catch (ExecutionException e) {
        log.warn("Task failed", e.getCause());
    }
}
```

**How to test / verify correctness:**
```java
@Test
void resultsArrivedInCompletionOrder() throws Exception {
    ExecutorService exec =
        Executors.newFixedThreadPool(3);
    CompletionService<Integer> cs =
        new ExecutorCompletionService<>(exec);

    cs.submit(() -> { Thread.sleep(300); return 1; });
    cs.submit(() -> { Thread.sleep(100); return 2; });
    cs.submit(() -> { Thread.sleep(200); return 3; });

    List<Integer> order = new ArrayList<>();
    for (int i = 0; i < 3; i++) {
        order.add(cs.take().get());
    }
    exec.shutdown();

    // Task 2 finishes first (100ms), then 3 (200ms), then 1
    assertThat(order).containsExactly(2, 3, 1);
}
```

---

### ⚖️ Comparison Table

| Feature | `CompletionService` | List of `Future.get()` | `CompletableFuture.anyOf` |
|---------|--------------------|-----------------------|--------------------------|
| Result order | Completion order | Submission order | First-completed only |
| Head-of-line blocking | Eliminated | Present | N/A (not for N results) |
| Exception per task | Yes (`f.get()`) | Yes (`f.get()`) | Yes |
| "All done" signal | Caller tracks count | Caller tracks count | Explicit `allOf` |
| Composable pipeline | No | No | Yes |
| Best for | N tasks with variable time | Uniform task times | First-result-wins pattern |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`CompletionService` creates its own thread pool" | No. It wraps an existing `Executor`. The pool must be managed separately. |
| "`take()` returns results in the order tasks complete, starting with submission" | It returns in *completion* order - the fastest task returns first, regardless of when it was submitted. |
| "I can cancel a task after submitting to CompletionService" | The returned `Future.cancel()` works, but the cancelled future still appears in the queue (as done with cancelled state). The consumer must check `future.isCancelled()`. |
| "`CompletionService` handles the 'all done' signal automatically" | There is no built-in termination signal. You must track how many tasks you submitted and call `take()` exactly that many times. |
| "It's always better than a list of futures" | Only when tasks have variable completion times and you can process results independently. Uniform-time tasks gain little from it. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Consumer calls take() fewer times than submitted**

**Symptom:** Tasks pile up in the completion queue; memory grows;
executor threads stay alive indefinitely.

**Root Cause:** Consumer breaks out of the loop (e.g., on first
exception) without consuming all enqueued futures.

**Diagnostic:**
```java
// Cast to ExecutorCompletionService to inspect queue
ExecutorCompletionService<T> ecs =
    (ExecutorCompletionService<T>) cs;
// Not directly accessible - use size tracking instead:
AtomicInteger submitted = new AtomicInteger(0);
// Increment on each submit(), decrement on each take()
```

**Fix:** Always consume as many futures as submitted, even on error:
```java
while (pending-- > 0) {
    Future<T> f = cs.take();  // always drain
    try { process(f.get()); }
    catch (ExecutionException e) { logError(e); }
}
```

---

**Failure Mode 2: ExecutionException ignored, data silently lost**

**Symptom:** Some results never appear in output; no error logged.

**Root Cause:** Consumer calls `f.get()` without try-catch;
`ExecutionException` propagates out of the drain loop, stopping
remaining `take()` calls.

**Diagnostic:** Add logging around `f.get()` and count processed
results vs submitted tasks.

**Fix:** Wrap `f.get()` in try-catch inside the drain loop and
continue to the next result.

---

**Failure Mode 3: Executor shutdown before queue drained**

**Symptom:** Some tasks' results lost; `executor.shutdown()` called
mid-drain.

**Root Cause:** `executor.shutdown()` was called before all `take()`
calls completed. Running tasks still finish and enqueue, but the
consumer exited early.

**Fix:** Call `executor.shutdown()` only after the drain loop
completes, or use `executor.awaitTermination()` as a safety net.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-029 - ExecutorService]] - the underlying thread pool
- [[JCC-013 - Future]] - the result type returned by `take()`
- [[JCC-059 - CompletableFuture Composition Patterns]] - the
  modern alternative for smaller task sets

**Builds On This (learn these next):**
- [[JCC-066 - Thread Pinning (Virtual Threads Problem)]] - how
  virtual threads affect task throughput
- [[JCC-030 - ThreadPoolExecutor]] - tune the underlying pool

**Alternatives / Comparisons:**
- [[JCC-014 - CompletableFuture]] - richer composability for
  small known task sets
- [[JCC-044 - Structured Concurrency]] - Java 21 replacement with
  built-in result collection and cancellation

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | ExecutorService + BlockingQueue:   |
|              | results arrive in completion order |
+--------------+------------------------------------+
| PROBLEM      | future.get() in submission order   |
|              | causes head-of-line blocking       |
+--------------+------------------------------------+
| KEY INSIGHT  | Fastest task's result is available |
|              | first, regardless of submit order  |
+--------------+------------------------------------+
| USE WHEN     | N tasks with variable runtimes,    |
|              | independent results to process     |
+--------------+------------------------------------+
| AVOID WHEN   | Tasks have uniform time, or you    |
|              | need composable pipelines (use CF) |
+--------------+------------------------------------+
| TRADE-OFF    | Eliminates HOL blocking / must     |
|              | manually track submit/consume count|
+--------------+------------------------------------+
| ONE-LINER    | cs.submit(task); f = cs.take();    |
|              | process(f.get())                   |
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-044 Structured Concurrency,    |
|              | JCC-014 CompletableFuture          |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. `take()` blocks until *any* task completes - results come in
   completion order, not submission order.
2. Always call `take()` exactly as many times as you submitted tasks
   - don't break the loop on first exception.
3. `CompletionService` wraps an existing executor - you still own
   the pool lifecycle and must shut it down.

**Interview one-liner:** "`CompletionService` eliminates head-of-line
blocking by routing completed futures into a `BlockingQueue`; `take()`
returns results in completion order regardless of submission order."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When processing N independent
items whose processing times vary, consume results as they become
available rather than waiting for a fixed ordering. First-available
consumption maximises throughput by eliminating artificial serialisation.

**Where else this pattern appears:**
- **Event-driven architectures (Kafka consumer):** The consumer
  reads messages as they arrive on partitions rather than waiting
  for a specific partition's message first - completion-order
  consumption at the messaging layer.
- **Hospital emergency triage:** Patients are seen in order of
  severity (fastest to stabilise), not arrival time - completion-
  order scheduling of the most urgent work first.
- **TCP out-of-order packet reassembly:** The OS receives packets
  and buffers them; the application layer reads in sequence number
  order, but the network delivers in arrival order - the inverse
  problem, requiring reordering.

---

### 💡 The Surprising Truth

`CompletionService` does not actually guarantee that results are
processed in *exact* completion order when multiple tasks complete
simultaneously. Two tasks finishing within the same nanosecond
window will be enqueued in an arbitrary order by the
`LinkedBlockingQueue`'s internal lock. In practice this matters
only in benchmarks and tests that expect strict timing - real-world
usage (where "completion order" means "whichever finishes first
in human-observable time") is unaffected. The more common surprise
is that cancelled futures also appear in the queue: `take()` will
return a future where `isCancelled()` is true, and calling `get()`
on it throws `CancellationException` rather than returning a value.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** You use `CompletionService`
to process 1,000 images. 10 images consistently fail with
`ExecutionException`. If your consumer catches these exceptions
and skips to the next `take()`, what happens to consumer memory
over time if the exception objects hold references to the failed
images (10 MB each)?

*Hint:* Investigate where `ExecutionException.cause` is held in
the `Future` and whether it is eligible for GC after `take()`
returns and you exit the catch block.

---

**Question 2 (Design Trade-off):** You need to return the result
of whichever of 3 downstream API calls responds first, ignoring
the other two. Should you use `CompletionService`, `anyOf`, or
`StructuredTaskScope.ShutdownOnSuccess`? What are the exact
cancellation semantics of each option for the losing two calls?

*Hint:* Check whether `anyOf` cancels the other futures, whether
`CompletionService` has any cancellation concept, and what
`ShutdownOnSuccess.close()` does to in-progress subtasks.

---

**Question 3 (Scale):** A service submits 10,000 tasks to a
`CompletionService`-backed pool of 100 threads. Processing each
result takes 5ms. Tasks complete at an average rate of 200/s.
At what queue depth does the `BlockingQueue` stabilise, and what
happens to heap usage if the consumer goes slower than 200/s?

*Hint:* Model as a producer-consumer queue where production rate
is task completion rate and consumption rate is result processing
speed. Research `LinkedBlockingQueue` default capacity and whether
bounded queues are appropriate here.

