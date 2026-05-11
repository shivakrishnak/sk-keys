#!/usr/bin/env python3
"""Fill TODO sections for Java - Java 21 and Beyond.md (3 keywords)."""
import re

FILE = "interview/java/Java - Java 21 and Beyond.md"

KEYWORDS = [
    "Virtual Threads",
    "Scoped Values",
    "Structured Concurrency",
]

# ── Level 5 ──────────────────────────────────────────────

LEVEL5 = {
    "Virtual Threads": (
        "Virtual threads are the JVM's implementation of the "
        "universal lightweight concurrency primitive that "
        "exists in every modern runtime: Go goroutines, Kotlin "
        "coroutines, Erlang processes, Rust tokio tasks. The "
        "cross-domain insight: all of these solve the same "
        "problem - OS threads are too expensive (1MB stack, "
        "kernel scheduling overhead) to model one-thread-per-"
        "request at scale. Virtual threads solve this by "
        "decoupling the Java thread (the programming model) "
        "from the OS thread (the execution resource). A "
        "virtual thread is mounted on a carrier (platform) "
        "thread only while it has CPU work; during blocking IO, "
        "it unmounts, freeing the carrier for other virtual "
        "threads. At extreme scale (millions of concurrent "
        "connections), virtual threads eliminate the need for "
        "reactive programming (Project Reactor, RxJava) for "
        "IO-bound workloads while keeping the simple "
        "thread-per-request model. If redesigning today, "
        "virtual threads would be the ONLY thread type, and "
        "platform threads would be an implementation detail "
        "never exposed to developers.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this IO-bound or CPU-bound?\" - virtual threads "
        "help IO-bound; CPU-bound needs platform threads\n"
        "- \"Are we pinning?\" - synchronized blocks and native "
        "calls pin virtual threads to carriers\n"
        "- \"Is thread-per-request viable now?\" - with virtual "
        "threads, yes - even at millions of requests"
    ),
    "Scoped Values": (
        "Scoped values are the successor to ThreadLocal that "
        "solves its fundamental design flaws: unbounded lifetime, "
        "memory leaks, and incompatibility with virtual threads. "
        "The same scoped-context pattern appears in Go's "
        "`context.Context`, Rust's task-local storage, and "
        "React's Context API. The cross-domain insight: when "
        "you need to pass contextual data (user identity, "
        "correlation ID, transaction context) through a deep "
        "call stack without parameter threading, you need a "
        "scope-bound, immutable, inheritable container. "
        "ThreadLocal's mutability and unbounded lifetime make "
        "it a memory leak factory in virtual thread scenarios "
        "(millions of threads = millions of ThreadLocal copies). "
        "Scoped values fix this by being immutable, bound to a "
        "structured scope (runs only within a `where().run()` "
        "block), and automatically cleaned up when the scope "
        "exits. If redesigning today, scoped values would be "
        "the only mechanism for thread-contextual data, and "
        "ThreadLocal would not exist.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this data per-request or per-thread?\" - scoped "
        "values model per-scope, which aligns with per-request\n"
        "- \"Is this mutable?\" - if yes, scoped values won't "
        "work; rethink the design\n"
        "- \"How many threads will exist?\" - if millions "
        "(virtual threads), ThreadLocal is a memory bomb"
    ),
    "Structured Concurrency": (
        "Structured concurrency applies the structured "
        "programming principle (every block has one entry, one "
        "exit) to concurrent tasks. Just as structured "
        "programming replaced goto with blocks, structured "
        "concurrency replaces fire-and-forget threads with "
        "scoped task groups. This same pattern appears in "
        "Kotlin's coroutineScope, Swift's TaskGroup, Python's "
        "trio nurseries, and Go's errgroup. The cross-domain "
        "insight: unstructured concurrency (raw thread creation) "
        "is the concurrent equivalent of goto - it creates "
        "invisible control flow paths that leak resources, "
        "orphan tasks, and make error handling impossible. "
        "Structured concurrency guarantees: if a scope exits, "
        "all child tasks have completed (or been cancelled). "
        "This makes concurrent code as predictable as sequential "
        "code. At extreme scale, structured concurrency composes "
        "with virtual threads and scoped values to form a "
        "complete concurrency model: lightweight threads "
        "(virtual), scoped context (scoped values), and "
        "lifetime management (structured concurrency). If "
        "redesigning today, `Thread.start()` would not exist - "
        "only structured task submission.\n\n"
        "**Expert thinking cues:**\n"
        "- \"What happens to child tasks when the parent fails?\" "
        "- structured concurrency guarantees cancellation\n"
        "- \"Can tasks outlive their scope?\" - structured = no, "
        "unstructured = yes (and that's the bug)\n"
        "- \"How do I compose concurrent operations?\" - "
        "StructuredTaskScope is the composition primitive"
    ),
}

# ── Quick Reference Card ─────────────────────────────────

QUICKREF = {
    "Virtual Threads": (
        "**WHAT IT IS:** Lightweight threads managed by the JVM "
        "(not OS), enabling millions of concurrent threads for "
        "IO-bound workloads (JDK 21)\n"
        "**PROBLEM IT SOLVES:** OS thread limits (~10K) force "
        "complex async/reactive code for high-concurrency "
        "IO workloads\n"
        "**KEY INSIGHT:** Virtual threads decouple the Java "
        "thread (programming model) from the OS thread "
        "(execution resource)\n"
        "**USE WHEN:** IO-bound workloads (HTTP servers, DB "
        "queries, microservice calls) needing high concurrency "
        "with simple code\n"
        "**AVOID WHEN:** CPU-bound computation (use platform "
        "thread pools), or when using synchronized blocks "
        "extensively (pinning)\n"
        "**ANTI-PATTERN:** Pooling virtual threads - they are "
        "cheap to create and should be one-per-task, never "
        "pooled\n"
        "**TRADE-OFF:** Simplicity (thread-per-request) vs "
        "control (reactive gives more backpressure control)\n"
        "**ONE-LINER:** \"Virtual threads make thread-per-request "
        "viable at million-connection scale with blocking code\""
    ),
    "Scoped Values": (
        "**WHAT IT IS:** Immutable, scope-bound context values "
        "that replace ThreadLocal for passing data through "
        "call stacks (JDK 21 preview)\n"
        "**PROBLEM IT SOLVES:** ThreadLocal memory leaks and "
        "unbounded lifetime in virtual thread scenarios with "
        "millions of threads\n"
        "**KEY INSIGHT:** Scoped values are immutable, bound to "
        "a structured scope, and automatically cleaned up - "
        "unlike ThreadLocal\n"
        "**USE WHEN:** Passing request context (user ID, "
        "correlation ID, transaction) through deep call stacks "
        "without parameters\n"
        "**AVOID WHEN:** Mutable per-thread state is needed "
        "(scoped values are immutable), or on JDK versions "
        "before 21\n"
        "**ANTI-PATTERN:** Using ThreadLocal with virtual "
        "threads - millions of threads create millions of "
        "ThreadLocal copies\n"
        "**TRADE-OFF:** Immutability constraint vs memory "
        "safety and predictable lifecycle\n"
        "**ONE-LINER:** \"Scoped values are ThreadLocal done "
        "right: immutable, scoped, and safe for virtual "
        "threads\""
    ),
    "Structured Concurrency": (
        "**WHAT IT IS:** API for managing concurrent subtasks "
        "as a unit with guaranteed lifetime and cancellation "
        "semantics (JDK 21 preview)\n"
        "**PROBLEM IT SOLVES:** Fire-and-forget threads leak "
        "resources, orphan tasks, and make error handling in "
        "concurrent code impossible\n"
        "**KEY INSIGHT:** If a scope exits, ALL child tasks "
        "have completed or been cancelled - concurrent code "
        "becomes as predictable as sequential\n"
        "**USE WHEN:** Fan-out/fan-in patterns, parallel API "
        "calls, any concurrent work that should have a bounded "
        "lifetime\n"
        "**AVOID WHEN:** Truly independent background tasks "
        "that should outlive the request, or fire-and-forget "
        "scenarios\n"
        "**ANTI-PATTERN:** Using raw Thread.start() or "
        "ExecutorService.submit() without lifetime management "
        "- tasks can leak\n"
        "**TRADE-OFF:** Strict lifetime control vs flexibility "
        "of unstructured fire-and-forget concurrency\n"
        "**ONE-LINER:** \"Structured concurrency is to threads "
        "what structured programming was to goto\""
    ),
}

# ── Comparison Table ─────────────────────────────────────

COMPARISON = {
    "Virtual Threads": (
        "| Aspect | Virtual Threads | Platform Threads | "
        "Reactive (Reactor) |\n"
        "|--------|----------------|-----------------|"
        "-------------------|\n"
        "| Stack size | ~1KB (grows) | ~1MB fixed | "
        "N/A (callback) |\n"
        "| Max count | Millions | ~10K | "
        "N/A (event loop) |\n"
        "| Blocking IO | Unmounts carrier | Blocks OS thread | "
        "Non-blocking |\n"
        "| Code style | Imperative/blocking | "
        "Imperative/blocking | Reactive/functional |\n"
        "| Debugging | Standard stack traces | "
        "Standard stack traces | Complex (async) |\n"
        "| Best for | IO-bound, high concurrency | "
        "CPU-bound | IO-bound, backpressure |"
    ),
    "Scoped Values": (
        "| Aspect | ScopedValue | ThreadLocal | "
        "Parameter passing |\n"
        "|--------|------------|-------------|"
        "------------------|\n"
        "| Mutability | Immutable | Mutable | "
        "Immutable (by convention) |\n"
        "| Lifetime | Scope-bound | Unbounded | "
        "Call stack |\n"
        "| Cleanup | Automatic | Manual (remove()) | "
        "Automatic |\n"
        "| Inheritance | StructuredTaskScope | "
        "InheritableThreadLocal | Explicit |\n"
        "| Virtual thread safe | Yes | "
        "No (memory leak) | Yes |\n"
        "| Performance | Optimized | Hash lookup | "
        "Zero overhead |"
    ),
    "Structured Concurrency": (
        "| Aspect | StructuredTaskScope | ExecutorService | "
        "CompletableFuture |\n"
        "|--------|-------------------|----------------|"
        "------------------|\n"
        "| Lifetime | Scope-bound | Unbounded | "
        "Unbounded |\n"
        "| Cancellation | Automatic on failure | Manual | "
        "Manual |\n"
        "| Error handling | ShutdownOnFailure | "
        "try-catch per task | exceptionally() |\n"
        "| Task leaks | Impossible | Common | "
        "Common |\n"
        "| Debugging | Clear parent-child | "
        "Disconnected | Disconnected |\n"
        "| Virtual thread aware | Yes | "
        "Partially | No |"
    ),
}

# ── Misconceptions ───────────────────────────────────────

MISCONCEPTIONS = {
    "Virtual Threads": [
        ("Virtual threads are faster than platform threads",
         "Virtual threads are not faster per-task. They are "
         "more scalable - you can have millions of them. A "
         "single virtual thread runs at the same speed as a "
         "platform thread."),
        ("Virtual threads replace reactive programming entirely",
         "For IO-bound workloads, yes. But reactive frameworks "
         "still provide backpressure, which virtual threads "
         "don't. CPU-bound work still needs bounded thread "
         "pools."),
        ("Virtual threads should be pooled",
         "Never pool virtual threads. They are cheap to create "
         "(~1KB) and meant to be one-per-task. Pooling adds "
         "complexity without benefit."),
        ("synchronized works fine with virtual threads",
         "synchronized blocks PIN virtual threads to carrier "
         "threads, blocking the carrier. Replace synchronized "
         "with ReentrantLock to allow unmounting during "
         "contention."),
    ],
    "Scoped Values": [
        ("Scoped values are just immutable ThreadLocals",
         "Scoped values have fundamentally different semantics: "
         "scope-bound lifetime (auto-cleanup), no set() method, "
         "and optimized for virtual threads. They're a new "
         "abstraction, not a ThreadLocal variant."),
        ("Scoped values can replace all ThreadLocal uses",
         "Scoped values are immutable within a scope. If you "
         "need mutable per-thread state (counters, buffers), "
         "ThreadLocal is still necessary."),
        ("Scoped values are only for virtual threads",
         "Scoped values work with both platform and virtual "
         "threads. They are beneficial for any code that needs "
         "scoped context, regardless of thread type."),
        ("Scoped values have high overhead",
         "Scoped values are optimized by the JVM to be faster "
         "than ThreadLocal for read-heavy patterns. The "
         "immutability enables caching optimizations."),
    ],
    "Structured Concurrency": [
        ("Structured concurrency is just a try-with-resources for threads",
         "It's deeper: structured concurrency guarantees that "
         "ALL subtasks complete before the scope exits, "
         "propagates cancellation to children, and creates "
         "a parent-child relationship visible in debugging."),
        ("Structured concurrency prevents all task leaks",
         "Within a StructuredTaskScope, yes. But code can still "
         "create unstructured threads outside the scope. "
         "Discipline is needed to use structured concurrency "
         "consistently."),
        ("Structured concurrency is only for fan-out patterns",
         "It applies to any concurrent work with bounded "
         "lifetime: parallel API calls, concurrent validation, "
         "map-reduce, timeout handling, and competitive "
         "execution (first-to-complete)."),
        ("You need structured concurrency for simple parallelism",
         "For embarrassingly parallel, independent tasks with "
         "no error correlation, a simple parallel stream or "
         "ExecutorService may be simpler. Structured concurrency "
         "shines when tasks are related."),
    ],
}

# ── Failure Modes ────────────────────────────────────────

FAILURES = {
    "Virtual Threads": r"""**Failure Mode 1: Thread pinning due to synchronized blocks**
**Symptom:** Virtual thread pool carriers are all blocked. Throughput drops to number of carrier threads. Thread dump shows virtual threads stuck in synchronized.
**Root Cause:** `synchronized` blocks pin virtual threads to carrier (platform) threads. The carrier cannot be reused until the synchronized block exits, even during IO waits inside it.
**Diagnostic:**

```
# JDK 21+: detect pinning with JFR events
# -Djdk.tracePinnedThreads=short (or =full)
# Look for jdk.VirtualThreadPinned events in JFR
jcmd <pid> JFR.start name=pin duration=60s
```

**Fix:**
```java
// BAD: synchronized pins virtual thread
synchronized (lock) {
    var result = httpClient.send(req, handler);
    // Carrier is pinned during entire HTTP call
}

// GOOD: use ReentrantLock instead
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    var result = httpClient.send(req, handler);
    // Virtual thread can unmount during IO
} finally {
    lock.unlock();
}
```
**Prevention:** Replace all `synchronized` with `ReentrantLock` in code that runs on virtual threads. Use `-Djdk.tracePinnedThreads=short` to detect pinning.

**Failure Mode 2: Memory exhaustion from millions of virtual threads**
**Symptom:** OutOfMemoryError. Each virtual thread holds request state, accumulated objects fill heap.
**Root Cause:** Creating millions of virtual threads, each holding significant state (large request bodies, database result sets). Virtual threads are cheap but their stack/state is not free.
**Diagnostic:**

```
# Count active virtual threads
jcmd <pid> Thread.dump_to_file -format=json threads.json
# Check heap usage per thread
jmap -histo:live <pid> | head -20
```

**Fix:**
```java
// BAD: unlimited virtual threads with large state
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var req : millionsOfRequests) {
        exec.submit(() -> processLargePayload(req));
    }
}

// GOOD: use semaphore to bound concurrency
Semaphore permits = new Semaphore(10_000);
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var req : millionsOfRequests) {
        permits.acquire();
        exec.submit(() -> {
            try { processLargePayload(req); }
            finally { permits.release(); }
        });
    }
}
```
**Prevention:** Bound concurrency with Semaphore when memory per task is significant. Monitor heap usage. Virtual threads are cheap but not free.

**Failure Mode 3: ThreadLocal memory leaks at scale**
**Symptom:** Heap grows linearly with virtual thread count. GC can't reclaim ThreadLocal-attached objects.
**Root Cause:** Each virtual thread gets its own ThreadLocal copies. With millions of virtual threads, ThreadLocal storage becomes a significant memory consumer.
**Diagnostic:**

```
# Heap dump analysis
jmap -dump:live,format=b,file=heap.hprof <pid>
# In Eclipse MAT: find ThreadLocal instances
# Look for ThreadLocal$ThreadLocalMap entries
```

**Fix:**
```java
// BAD: ThreadLocal with virtual threads
private static final ThreadLocal<ExpensiveObj> cache =
    ThreadLocal.withInitial(ExpensiveObj::new);
// Millions of virtual threads = millions of objects

// GOOD: use ScopedValue or shared cache
private static final ScopedValue<RequestCtx> CTX =
    ScopedValue.newInstance();
ScopedValue.where(CTX, new RequestCtx(userId))
    .run(() -> handleRequest());
```
**Prevention:** Replace ThreadLocal with ScopedValue for virtual threads. Audit all ThreadLocal usage before migrating to virtual threads.""",

    "Scoped Values": r"""**Failure Mode 1: Accessing scoped value outside its scope**
**Symptom:** `NoSuchElementException` when calling `scopedValue.get()` outside a `where().run()` block.
**Root Cause:** Scoped values are only bound within their scope. Accessing them from a thread or code path not within the `where().run()` scope throws an exception.
**Diagnostic:**

```
# Look for ScopedValue.get() calls
grep -rn "\.get()" src/ | grep -i scoped
# Ensure every get() is within a where().run() scope
```

**Fix:**
```java
// BAD: accessing outside scope
static final ScopedValue<String> USER =
    ScopedValue.newInstance();
void process() {
    String u = USER.get(); // NoSuchElementException!
}

// GOOD: always access within scope
ScopedValue.where(USER, "alice").run(() -> {
    process(); // USER.get() works here
});
// Or check: if (USER.isBound()) { USER.get(); }
```
**Prevention:** Always check `isBound()` before `get()` in code that might run outside a scope. Design APIs to require scoped context.

**Failure Mode 2: Trying to mutate a scoped value**
**Symptom:** Compilation error or design confusion when trying to change a scoped value within its scope.
**Root Cause:** Scoped values are immutable within a scope. There is no `set()` method. To change the value, you must create a new nested scope.
**Diagnostic:**

```
# Look for attempts to reassign scoped values
grep -rn "ScopedValue" src/ | grep "set\|assign\|="
```

**Fix:**
```java
// BAD: trying to mutate scoped value
static final ScopedValue<String> ROLE =
    ScopedValue.newInstance();
ScopedValue.where(ROLE, "user").run(() -> {
    // ROLE.set("admin"); // No set() method!

    // GOOD: create a nested scope
    ScopedValue.where(ROLE, "admin").run(() -> {
        // ROLE.get() returns "admin" here
    });
    // ROLE.get() returns "user" here
});
```
**Prevention:** Design for immutability. If value needs to change, use nested scopes. If mutable state is required, scoped values are not the right tool.

**Failure Mode 3: ScopedValue not inherited by child threads**
**Symptom:** Child threads spawned with `Thread.start()` cannot access parent's scoped values. `NoSuchElementException` in child.
**Root Cause:** Scoped values are only inherited through `StructuredTaskScope`. Raw `Thread.start()` creates unstructured threads that don't inherit scoped values.
**Diagnostic:**

```
# Find thread creation inside scoped value scopes
grep -rn "Thread(" src/ | grep -v "test"
# These won't inherit scoped values
```

**Fix:**
```java
// BAD: raw thread doesn't inherit scoped values
ScopedValue.where(USER, "alice").run(() -> {
    new Thread(() -> {
        USER.get(); // NoSuchElementException!
    }).start();
});

// GOOD: use StructuredTaskScope for inheritance
ScopedValue.where(USER, "alice").run(() -> {
    try (var scope = new StructuredTaskScope<>()) {
        scope.fork(() -> {
            USER.get(); // Works! Inherited via scope
            return null;
        });
        scope.join();
    }
});
```
**Prevention:** Always use StructuredTaskScope to spawn child tasks when scoped values need to be inherited. Never use raw Thread creation.""",

    "Structured Concurrency": r"""**Failure Mode 1: Forgetting to call join() before processing results**
**Symptom:** `IllegalStateException` when calling `subtask.get()` or scope methods before `join()` completes.
**Root Cause:** StructuredTaskScope requires `join()` to be called before accessing results. This ensures all subtasks have completed.
**Diagnostic:**

```
# Look for result access before join()
grep -rn "subtask.get\|scope.result" src/
# Ensure join() is called before any result access
```

**Fix:**
```java
// BAD: accessing result before join
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task = scope.fork(() -> fetchData());
    String data = task.get(); // IllegalStateException!
    scope.join();
}

// GOOD: join first, then access results
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task = scope.fork(() -> fetchData());
    scope.join();
    scope.throwIfFailed();
    String data = task.get(); // Safe after join
}
```
**Prevention:** Always follow the pattern: fork -> join -> throwIfFailed -> get results. Never access subtask results before join.

**Failure Mode 2: Task leak when not using try-with-resources**
**Symptom:** Subtasks continue running after the logical scope has ended. Resource leaks, orphaned operations.
**Root Cause:** StructuredTaskScope implements AutoCloseable. Without try-with-resources, close() is not called, and subtasks may not be cancelled on scope exit.
**Diagnostic:**

```
# Find scope creation without try-with-resources
grep -rn "StructuredTaskScope" src/ | grep -v "try"
# These are potential task leak sites
```

**Fix:**
```java
// BAD: manual scope management, easy to leak
var scope = new StructuredTaskScope.ShutdownOnFailure();
scope.fork(() -> riskyOperation());
// If exception thrown here, scope never closed!
scope.join();
scope.close();

// GOOD: try-with-resources guarantees cleanup
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    scope.fork(() -> riskyOperation());
    scope.join();
    scope.throwIfFailed();
} // Automatically cancels and closes
```
**Prevention:** ALWAYS use try-with-resources with StructuredTaskScope. Never manually manage scope lifecycle.

**Failure Mode 3: Using ShutdownOnSuccess when all results are needed**
**Symptom:** Some subtasks are cancelled before completing. Missing results from cancelled tasks.
**Root Cause:** `ShutdownOnSuccess` cancels remaining subtasks when the FIRST one succeeds. If you need ALL results, this policy is wrong.
**Diagnostic:**

```
grep -rn "ShutdownOnSuccess" src/
# Verify that only one result is actually needed
# If all results needed, use ShutdownOnFailure
```

**Fix:**
```java
// BAD: ShutdownOnSuccess when all needed
try (var scope = new StructuredTaskScope
        .ShutdownOnSuccess<String>()) {
    var t1 = scope.fork(() -> fetchFromDB());
    var t2 = scope.fork(() -> fetchFromAPI());
    scope.join();
    // t2 might be cancelled if t1 finished first!
}

// GOOD: ShutdownOnFailure to wait for ALL
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    var t1 = scope.fork(() -> fetchFromDB());
    var t2 = scope.fork(() -> fetchFromAPI());
    scope.join();
    scope.throwIfFailed();
    combine(t1.get(), t2.get()); // Both available
}
```
**Prevention:** Use `ShutdownOnFailure` when you need ALL results. Use `ShutdownOnSuccess` only for competitive execution (first-to-complete wins).""",
}

# ── Related Keywords ─────────────────────────────────────

RELATED = {
    "Virtual Threads": r"""**Prerequisites (understand these first):**

- Java threading and concurrency - Thread, Runnable, ExecutorService, thread pools
- Blocking IO vs non-blocking IO - understanding why blocking wastes OS threads

**Builds on this (learn these next):**

- Structured Concurrency - managing virtual thread lifetimes with StructuredTaskScope
- Scoped Values - replacing ThreadLocal for virtual thread-safe context propagation

**Alternatives / Comparisons:**

- Project Reactor / RxJava - reactive streams for IO-bound work with backpressure (more complex)
- Kotlin Coroutines - similar lightweight concurrency with suspend functions (Kotlin-specific)""",

    "Scoped Values": r"""**Prerequisites (understand these first):**

- ThreadLocal - understanding per-thread storage, its API, and its memory leak problems
- Virtual Threads - why ThreadLocal is problematic at million-thread scale

**Builds on this (learn these next):**

- Structured Concurrency - scoped values inherit through StructuredTaskScope, not raw threads
- Context propagation - how scoped values replace MDC, SecurityContext in frameworks

**Alternatives / Comparisons:**

- ThreadLocal - mutable, unbounded lifetime, works everywhere but leaks with virtual threads
- Parameter passing - explicit, refactor-friendly, but verbose in deep call stacks""",

    "Structured Concurrency": r"""**Prerequisites (understand these first):**

- Virtual Threads - the lightweight thread primitive that structured concurrency manages
- CompletableFuture / ExecutorService - the unstructured concurrency APIs that this replaces

**Builds on this (learn these next):**

- Scoped Values - context propagation through structured task scopes
- Error handling in concurrent systems - how structured concurrency simplifies error aggregation

**Alternatives / Comparisons:**

- ExecutorService + Future - unstructured, more flexible but prone to task leaks
- CompletableFuture chains - functional composition but complex error handling and debugging""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
