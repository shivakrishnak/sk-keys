---
layout: default
title: "Virtual Threads"
parent: "Java Concurrency"
nav_order: 353
permalink: /java-concurrency/virtual-threads/
number: "353"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread, ExecutorService, Platform Threads, ForkJoinPool
used_by: I/O-bound Services, High-concurrency HTTP, JDBC blocking
tags: #java, #java21, #concurrency, #virtual-threads, #loom
---

# 353 — Virtual Threads (Java 21)

`#java` `#java21` `#concurrency` `#virtual-threads` `#loom`

⚡ TL;DR — Virtual threads are JVM-managed lightweight threads (megabytes → kilobytes; millions possible) designed to make blocking I/O cheap — a virtual thread that blocks on I/O is unmounted from its carrier platform thread, freeing it for other virtual threads.

| #353 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, ExecutorService, Platform Threads, ForkJoinPool | |
| **Used by:** | I/O-bound Services, High-concurrency HTTP, JDBC blocking | |

---

### 📘 Textbook Definition

A **virtual thread** (`Thread.ofVirtual()`) is a lightweight thread managed by the JVM rather than the OS. Virtual threads are **multiplexed** onto a small pool of OS **carrier threads** (platform threads). When a virtual thread performs a blocking operation (I/O, `sleep`, `synchronized`, etc.), the JVM **unmounts** it from the carrier thread, allowing the carrier to run another virtual thread. When the blocking operation completes, the virtual thread is **remounted** onto a (possibly different) carrier. This makes blocking operations effectively non-blocking at the OS level, enabling millions of concurrent virtual threads.

---

### 🟢 Simple Definition (Easy)

Platform threads map 1:1 to OS threads — each costs ~1 MB and you can realistically have ~10,000. Virtual threads are JVM-internal — they don't have their own OS thread. When one blocks, the JVM "parks" it and uses that OS thread for another virtual thread. You can have millions. The code looks the same as before — just use a virtual thread executor.

---

### 🔵 Simple Definition (Elaborated)

Traditional server design: thread-per-request. HTTP request arrives → assign a platform thread → thread blocks waiting for DB/file/HTTP → OS thread idle → wasted. Fix: reactive programming (callback hell + hard to read). Virtual threads give a third option: write simple blocking code, but the JVM "recycles" the OS thread behind the scenes when the virtual thread is blocked. Millions of concurrent requests with simple synchronous code.

---

### 🔩 First Principles Explanation

```
Platform thread model:
  OS thread ←→ Java Platform Thread (1:1)
  Each costs 1–2 MB of stack + OS metadata
  OS can schedule ~10,000–30,000 before thrashing
  I/O call: platform thread sleeps → OS thread blocked → wasted

Virtual thread model:
  Many Virtual Threads (millions)
       ↕ mount/unmount on blocking  
  Few Carrier Threads (= CPU count, usually 8–32)
       ↕
  OS Threads (= Carrier Thread count)

When virtual thread blocks:
  1. VT hits blocking point (I/O, sleep, lock...)
  2. JVM saves VT's stack (to heap — cheap)
  3. VT unmounted from carrier thread
  4. Carrier thread picks up another runnable VT
  5. When I/O completes, VT is rescheduled (remounted)
  6. VT stack restored, execution continues

Effect:
  10,000 concurrent DB queries → 10,000 virtual threads
  Each blocks waiting for DB → unmounted
  8 carrier threads handle all 10,000 → never blocked
  Total OS threads: 8, not 10,000 → massive reduction
```

---

### ❓ Why Does This Exist — Why Before What

```
Without virtual threads:
  Blocking I/O = thread blocked = OS thread wasted
  Fix option 1: thread pool (still limited by OS, ~thousands max)
  Fix option 2: reactive (non-blocking) code → callback hell, hard to read/debug

With virtual threads:
  ✅ Write simple blocking code (same as before)
  ✅ Scales to millions of concurrent threads
  ✅ No callbacks, no reactive complexity
  ✅ Existing blocking APIs (JDBC, Files, HttpURLConnection) work transparently
  ✅ Thread.sleep() = unmount (not OS block); socket read = unmount
```

---

### 🧠 Mental Model / Analogy

> Imagine a hotel with 8 receptionists (carrier threads) handling a million guests (virtual threads). Each guest needs service but spends most of their visit waiting (I/O). Instead of each guest tying up a dedicated receptionist, they use a numbered ticket. When they need to wait (blocked), they sit in the lobby (heap). When they're next, a free receptionist picks up their ticket and resumes service. 8 receptionists, 1 million guests, fluent service.

---

### ⚙️ How It Works

```
Creating virtual threads:
  Thread vt = Thread.ofVirtual().start(() -> handleRequest());
  Thread.startVirtualThread(() -> handleRequest()); // shorthand

  // Virtual thread executor (one-per-task)
  ExecutorService exec = Executors.newVirtualThreadPerTaskExecutor();
  exec.submit(() -> httpFetch("https://..."));  // one VT per task

Carrier threads:
  ForkJoinPool.commonPool() by default (parallelism = CPU count)
  Carrier threads are platform threads
  VT is mounted/unmounted transparently

Blocking operations that support unmounting:
  ✅ I/O: socket, file, network, pipes
  ✅ Thread.sleep()
  ✅ Future.get(), BlockingQueue.take()
  ✅ Object.wait()
  ✅ java.util.concurrent.locks.Lock (ReentrantLock, etc.)

Pinning — VT stays mounted (blocks carrier thread):
  ❌ synchronized block/method (Java 21) — fixed in Java 24
  ❌ native method frames (JNI)
  Monitor: -Djdk.tracePinnedThreads=full to detect pinning
```

---

### 🔄 How It Connects

```
Virtual Threads
  │
  ├─ Solves  → I/O-bound throughput bottleneck (replaces reactive for many cases)
  ├─ Uses    → ForkJoinPool as carrier thread pool
  ├─ Not for → CPU-bound tasks (still need platform threads / parallelism)
  │
  ├─ ThreadLocal → works but avoid large values (millions of VTs → large heap use)
  ├─ synchronized → pinning issue in Java 21 (avoid in hot paths); fixed in Java 24
  └─ Structured Concurrency → companion feature for managing VT lifetimes
```

---

### 💻 Code Example

```java
// Spring Boot 3.2+: one line to enable virtual threads
@Bean
public TomcatProtocolHandlerCustomizer<?> virtualThreads() {
    return handler -> handler.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
}
// Every HTTP request now handled by its own virtual thread — no thread pool needed

// Manual virtual thread creation
Thread.startVirtualThread(() -> {
    String data = Files.readString(Path.of("/data/large.csv")); // blocks → VT unmounted
    processData(data); // resumes here when I/O done
});
```

```java
// 10,000 concurrent HTTP calls with virtual threads
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
List<Future<String>> futures = new ArrayList<>();

for (int i = 0; i < 10_000; i++) {
    final int id = i;
    futures.add(executor.submit(() -> httpGet("https://api.example.com/item/" + id)));
}

// Collect all results
for (Future<String> f : futures) {
    System.out.println(f.get()); // waits per future, but all run "in parallel"
}
// Platform threads: would need 10,000 threads → ~10 GB memory
// Virtual threads: microsecond creation, kilobyte stack, millisecond context switch
```

```java
// Checking pinning — diagnostic flags
// Run with: -Djdk.tracePinnedThreads=full
// Pinning happens with synchronized blocks in Java 21:
synchronized (lock) {
    networkCall(); // ← VT is PINNED here — carrier thread blocked during I/O
}
// Fix (Java 21): replace synchronized with ReentrantLock
lock.lock();
try { networkCall(); } finally { lock.unlock(); }
// ReentrantLock → VT unmounts correctly
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Virtual threads are faster than platform threads | Same CPU speed; benefit is multiplexing I/O — not faster computation |
| Virtual threads replace ForkJoinPool for CPU tasks | Virtual threads shine for blocking I/O; use platform threads for CPU-bound |
| Virtual threads eliminate all synchronization | Shared state issues (races, deadlocks) still apply — VTs just scale better |
| `synchronized` works seamlessly with virtual threads | `synchronized` causes pinning in Java 21; use ReentrantLock for best results |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Thread-local holding large objects → huge heap under millions of VTs**

```java
// 1M virtual threads × 1MB ThreadLocal = 1TB heap!
static ThreadLocal<byte[]> buffer = ThreadLocal.withInitial(() -> new byte[1024 * 1024]);
// Fix: use ScopedValue (Java 21 preview) or don't use ThreadLocal with VTs
```

**Pitfall 2: synchronized block pinning — defeats the purpose**

```java
// ❌ Java 21: synchronized pins VT to carrier thread during I/O
synchronized (conn) {
    ResultSet rs = stmt.executeQuery(); // I/O blocks carrier thread!
}
// Fix: use ReentrantLock
conn.lock.lock();
try { ResultSet rs = stmt.executeQuery(); }
finally { conn.lock.unlock(); }
```

---

### 🔗 Related Keywords

- **[Thread](./066 — Thread.md)** — platform thread (the carrier for virtual threads)
- **[ExecutorService](./074 — ExecutorService.md)** — `newVirtualThreadPerTaskExecutor()` creates VT per task
- **[ForkJoinPool](./084 — ForkJoinPool.md)** — carrier thread pool for virtual threads
- **[ThreadLocal](./073 — ThreadLocal.md)** — use with care; high memory cost with millions of VTs
- **Structured Concurrency** — companion for managing VT lifetimes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Lightweight JVM threads: block = unmount from │
│              │ carrier, not OS block; millions concurrent    │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ High-concurrency I/O services (HTTP, DB, file)│
│              │ replacing thread pools for blocking code      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-bound tasks (use platform threads + FJP); │
│              │ avoid synchronized in VT hot paths (Java 21)  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Write blocking code; JVM makes it free —     │
│              │  each I/O wait parks the thread, not the CPU" │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Structured Concurrency → ScopedValue →        │
│              │ ForkJoinPool → Reactive (Reactor) comparison  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Virtual threads are scheduled on carrier threads via ForkJoinPool. If a virtual thread is pinned (e.g. inside a `synchronized` block), the carrier thread is blocked. How does this affect other virtual threads that are ready to run? What is the maximum number of threads blocked in this scenario?

**Q2.** You migrate a Spring MVC application to virtual threads but still see poor throughput. Investigation shows all virtual threads are pinned. Where would you look in the code? What JVM flag helps you identify pinning?

**Q3.** Reactive frameworks (Project Reactor, RxJava) also solve the thread-per-request bottleneck. What are the trade-offs between virtual threads and reactive programming? When would you still choose reactive over virtual threads?

