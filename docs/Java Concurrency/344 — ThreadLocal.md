---
layout: default
title: "ThreadLocal"
parent: "Java Concurrency"
nav_order: 344
permalink: /java-concurrency/threadlocal/
---
# 344 — ThreadLocal

`#java` `#concurrency` `#threading` `#memory` `#thread-safety`

⚡ TL;DR — ThreadLocal gives each thread its own independent copy of a variable — eliminating sharing without synchronization — but causes memory leaks in thread pools if not explicitly removed after use.

| #344 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, Race Condition, GC Roots, Thread Pool | |
| **Used by:** | Security Context, DB Connections, Request Scoping, MDC | |

---

### 📘 Textbook Definition

`ThreadLocal<T>` provides thread-local storage: each thread that accesses a `ThreadLocal` variable gets its own independently initialized copy, stored in the thread's own `ThreadLocalMap`. The value is not shared between threads. `InheritableThreadLocal` additionally propagates the parent thread's value to child threads at creation time. Because thread pool threads are reused and never die, ThreadLocal values survive between tasks — requiring explicit `remove()` calls to prevent leaks.

---

### 🟢 Simple Definition (Easy)

`ThreadLocal` is like giving each thread its own locker. Thread 1's locker has Thread 1's stuff. Thread 2's locker has Thread 2's stuff. They never share or interfere. No synchronization needed because there's nothing to synchronize — nobody else can see your locker.

---

### 🔵 Simple Definition (Elaborated)

Instead of passing context data (current user, database connection, trace ID) as method parameters through every layer of your code, `ThreadLocal` stores that data in the thread itself. Any code running on that thread can retrieve it without needing to pass it around. Spring's transaction management, SLF4J's MDC (Mapped Diagnostic Context), and database connection holders all use ThreadLocal internally. The catch: thread pool threads never die — if a task sets a ThreadLocal and doesn't clean it up, the next task on THAT thread inherits the value, causing subtle bugs and memory leaks.

---

### 🔩 First Principles Explanation

**The problem: per-request context in a multi-threaded server**

```
Request comes in → server assigns a thread → request handler calls:
  Controller → Service → Repository → DAO → Audit logger

Each layer needs: current user, transaction context, request ID
Options:
  Option 1: pass as parameters       → 20+ methods all take "UserContext"
  Option 2: static variable          → shared → race condition
  Option 3: ThreadLocal              → stored in thread, no parameters, no sharing

ThreadLocal = ambient context per thread
```

**Internal structure:**

```
Thread object
   └──→ ThreadLocalMap (internal hash map)
            ├── ThreadLocal<User>    → User{name="Alice"}
            ├── ThreadLocal<Conn>    → Connection{url="..."}
            └── ThreadLocal<String> → "request-123"

Each ThreadLocal key is a WeakReference
Each value is strongly referenced
→ If ThreadLocal key is GC'd but value stays in ThreadLocalMap
→ The value is a memory leak (key gone, value unreachable but not collected)
```

**Why leaks in thread pools:**

```
Without ThreadLocal.remove():

Request 1 → Thread A:
  tl.set(user1)       // Thread A's map: user1 stored
  ... handle request ...
  // forgot tl.remove()
  Thread A returns to pool

Request 2 → Thread A:  (same thread reused!)
  tl.get()            // returns user1 ← WRONG! Not user2
  // also: user1 object never GC'd — reachable from thread A's map
```

---

### ❓ Why Does This Exist — Why Before What

```
Without ThreadLocal:
  Option A: synchronized static var
    → Thread-safe but blocks other threads → kills performance

  Option B: pass context as parameters
    → Every method signature polluted:
      void save(Entity e, UserContext ctx, TxContext tx, AuditContext audit)
    → Unworkable at scale

  Option C: thread-local storage
    → Store context in thread itself
    → Any code on that thread retrieves it
    → No sharing, no locking, no parameter pollution

Used everywhere:
  Spring:    TransactionSynchronizationManager (transaction context)
  SLF4J:     MDC.put/get (trace IDs in log output)
  Hibernate: SessionFactory current session
  Servlet:   Spring's RequestContextHolder (current request)
  Security:  SecurityContextHolder (Spring Security — current principal)
```

---

### 🧠 Mental Model / Analogy

> ThreadLocal is like a **hotel room safe** — each guest (thread) gets their own safe in their own room. What you put in your safe stays in your safe. Other guests can't access it. The receptionist (your code) always finds the right safe because it's identified by the room occupant (current thread). But if a guest checks out (request ends) without clearing their safe, the next guest finds someone else's valuables inside.

---

### ⚙️ How It Works

```
Class: java.lang.ThreadLocal<T>

Key methods:
  tl.set(T value)       → stores value in current thread's ThreadLocalMap
  tl.get()              → retrieves value from current thread's ThreadLocalMap
  tl.remove()           → removes entry from current thread's map (ALWAYS call this)
  tl.initialValue()     → override to provide a default value (or use withInitial())

ThreadLocal.withInitial(Supplier):
  ThreadLocal<List<String>> tl = ThreadLocal.withInitial(ArrayList::new);
  → Each thread gets its own ArrayList on first access

InheritableThreadLocal:
  Parent thread's value copied to child threads at creation time
  → Useful for passing context into newly spawned threads
  → Does NOT propagate to thread pool threads (they predate the request)
```

---

### 🔄 How It Connects

```
ThreadLocal
  │
  ├─ Stored in ──→ Thread's internal ThreadLocalMap (not the heap directly)
  ├─ Key is    ──→ WeakReference<ThreadLocal> (allows GC of ThreadLocal itself)
  ├─ Value is  ──→ Strong reference → ① weak key GC'd → value stranded = leak
  │
  ├─ Safe context passing: SecurityContextHolder, MDC, TransactionManager
  ├─ Thread pool risk: always call remove() in finally block
  └─ vs ScopedValue (Java 21) → structured, no-leak alternative
```

---

### 💻 Code Example

```java
// Basic usage — per-thread user context
public class UserContextHolder {
    private static final ThreadLocal<String> USER =
        ThreadLocal.withInitial(() -> "anonymous");

    public static void setUser(String userId) { USER.set(userId); }
    public static String getUser()            { return USER.get(); }
    public static void   clear()             { USER.remove(); }
}

// In a web filter (runs before and after each request on same thread):
public void doFilter(HttpServletRequest request, ...) {
    try {
        UserContextHolder.setUser(request.getHeader("X-User-Id"));
        chain.doFilter(request, response);
    } finally {
        UserContextHolder.clear();  // ✅ ALWAYS remove — thread returns to pool
    }
}

// In service layer — no parameters needed:
public void processOrder(Order order) {
    String user = UserContextHolder.getUser(); // "alice"
    auditLog.record(user + " placed order " + order.getId());
}
```

```java
// ThreadLocal with initialValue — each thread gets its own DateFormat
// (SimpleDateFormat is NOT thread-safe, but ThreadLocal makes it safe)
private static final ThreadLocal<SimpleDateFormat> DATE_FORMAT =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));

public String format(Date date) {
    return DATE_FORMAT.get().format(date);  // each thread has its own instance
}
```

```java
// Demonstrating the leak — DON'T do this in a thread pool
ExecutorService pool = Executors.newFixedThreadPool(2);
ThreadLocal<byte[]> bigData = new ThreadLocal<>();

// Task leaks 10MB per thread — pool has 2 threads → 20MB stuck forever
pool.submit(() -> {
    bigData.set(new byte[10 * 1024 * 1024]);  // 10MB
    processAndForget();
    // bigData.remove() MISSING → 10MB stuck in this thread's map forever
});
```

```java
// InheritableThreadLocal — child thread inherits parent's value
InheritableThreadLocal<String> traceId = new InheritableThreadLocal<>();
traceId.set("trace-abc-123");

Thread child = new Thread(() -> {
    System.out.println(traceId.get()); // "trace-abc-123" — inherited!
});
child.start();
// Note: doesn't work for thread pool threads (they're pre-created)
// Use TransmittableThreadLocal (TTL) library for thread pools
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| ThreadLocal stores data in thread's stack | Stored in `Thread.threadLocals` — a heap-allocated `ThreadLocalMap` |
| WeakReference key prevents leaks automatically | Weak key only helps if ThreadLocal itself is GC'd; in common patterns the ThreadLocal is static → never GC'd → leak unless remove() called |
| `remove()` is optional if value is small | Thread pool threads live forever → even small values accumulate; always remove |
| ThreadLocal is always the right tool for context | Java 21 ScopedValue provides structured, auto-cleaned context propagation |
| InheritableThreadLocal works with thread pools | Thread pool threads are created once — not when your request arrives → not inherited |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Missing remove() in a thread pool**

```java
// In a Spring @Service or Servlet filter
threadLocal.set(expensiveObject);
doWork();
// ❌ Missing: threadLocal.remove()
// Thread returns to Tomcat thread pool → next request inherits expensiveObject
// → wrong data served to next user
// → object never GC'd → OOM in production after hours of load

// ✅ Always use try/finally:
try {
    threadLocal.set(expensiveObject);
    doWork();
} finally {
    threadLocal.remove();
}
```

**Pitfall 2: Assuming ThreadLocal propagates to thread pool tasks**

```java
threadLocal.set("request-123");
executorService.submit(() -> {
    System.out.println(threadLocal.get()); // null! Pool thread has no inheritance
});
// Fix: capture value and pass explicitly, or use TransmittableThreadLocal library
String value = threadLocal.get();
executorService.submit(() -> {
    threadLocal.set(value); // set on pool thread explicitly
    try { doWork(); } finally { threadLocal.remove(); }
});
```

---

### 🔗 Related Keywords

- **[Thread](./066 — Thread.md)** — ThreadLocal stored inside Thread's internal map
- **[Race Condition](./072 — Race Condition.md)** — ThreadLocal eliminates sharing → no race
- **[GC Roots](../Java/016 — GC Roots.md)** — thread's ThreadLocalMap values reachable from thread root → memory leak
- **[ExecutorService](./074 — ExecutorService.md)** — thread reuse makes remove() critical
- **ScopedValue (Java 21)** — structured, no-leak replacement for ThreadLocal

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Per-thread variable copy — no sharing, no     │
│              │ sync needed; but thread pools reuse threads   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Per-request context (user, trace ID, conn);   │
│              │ non-thread-safe objects (SimpleDateFormat)    │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Sharing data BETWEEN threads; using in thread │
│              │ pool without guaranteed remove() in finally   │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Each thread's own locker — but empty it      │
│              │  before the next guest checks in"             │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ GC Roots → Thread Lifecycle → ExecutorService │
│              │ → ScopedValue (Java 21) → MDC (SLF4J)        │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `SecurityContextHolder` uses ThreadLocal to store the authentication object per thread. In a Servlet container with a thread pool, what must happen at the END of every HTTP request to prevent security context bleed between requests? What class in Spring handles this automatically?

**Q2.** `ThreadLocal` uses a `WeakReference` for the key. Under what specific conditions does this weak reference allow GC? Give a concrete scenario where the lack of `remove()` still causes a leak even with a weak key.

**Q3.** Java 21 introduced `ScopedValue` as a ThreadLocal alternative. What structural problem does it solve that ThreadLocal cannot? (Hint: think about virtual threads and structured concurrency.)

