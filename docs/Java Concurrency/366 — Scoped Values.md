---
layout: default
title: "Scoped Values"
parent: "Java Concurrency"
nav_order: 366
permalink: /java-concurrency/scoped-values/
number: "366"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads (Project Loom), ThreadLocal, Continuation, Structured Concurrency
used_by: Structured Concurrency
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
---

# 366 — Scoped Values

`#java` `#concurrency` `#advanced` `#deep-dive`

⚡ TL;DR — Java 21+ mechanism for sharing immutable, bounded-lifetime data with child threads in a thread tree — a safe, efficient alternative to ThreadLocal for virtual threads.

| #366 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Virtual Threads (Project Loom), ThreadLocal, Continuation, Structured Concurrency | |
| **Used by:** | Structured Concurrency | |

---

### 📘 Textbook Definition

`java.lang.ScopedValue<T>` (finalised in Java 21 via JEP 446) is an immutable, per-thread binding that associates a value with both a thread and a bounded lexical scope. A `ScopedValue` is set via `ScopedValue.where(SV, value).run(task)` or `.call(task)` — the binding is visible to the task and all threads it creates within the scope, but is automatically cleared when the scope exits. Unlike `ThreadLocal`, `ScopedValue` bindings are immutable within a scope (cannot be set again), are automatically inherited by virtual child threads in a `StructuredTaskScope`, and impose no cleanup burden on the developer.

### 🟢 Simple Definition (Easy)

Scoped Values let you pass context data (like a user ID or transaction ID) into a thread and all its child tasks automatically, without passing it as a parameter everywhere — and it disappears cleanly when the task finishes.

### 🔵 Simple Definition (Elaborated)

`ThreadLocal` has been the traditional Java way to attach per-thread context (request ID, user credentials, security context). But with millions of virtual threads, `ThreadLocal` has serious problems: it's mutable (can be set multiple times, creating confusion), it must be manually cleaned up (via `remove()`) to prevent memory leaks, and it doesn't automatically propagate to child threads. Scoped Values solve all three: the binding is immutable once set in a scope, it's automatically removed when the scope exits, and it's automatically inherited by all child virtual threads created within the scope — making it the ideal context-propagation mechanism for virtual thread-based systems.

### 🔩 First Principles Explanation

**ThreadLocal's problems with virtual threads:**

1. **Memory leaks:** `ThreadLocal` values survive as long as the thread lives. With platform threads in a pool, the thread may live indefinitely — a stale `ThreadLocal` (user session, request ID) from a past request stays in memory until explicitly removed. With millions of virtual threads, this multiplies dramatically.

2. **Mutability:** Thread A can call `tl.set(valueA)`, then call a library that accidentally calls `tl.set(valueB)` — now A reads B's value. `ThreadLocal` is shared mutable state per thread.

3. **No inheritance by default:** Creating a child thread doesn't automatically give it the parent's `ThreadLocal` values (unless using `InheritableThreadLocal`, which has its own problems with thread pooling).

**ScopedValue design:**

```java
static final ScopedValue<User> CURRENT_USER =
    ScopedValue.newInstance();

// Associate value for a bounded scope
ScopedValue.where(CURRENT_USER, authenticatedUser)
    .run(() -> {
        // CURRENT_USER.get() returns authenticatedUser here
        processRequest();  // and in all tasks spawned here
        // exits → binding automatically cleared
    });
```

**Immutability guarantee:** Within a `where().run()` scope, `CURRENT_USER.get()` always returns the same value. No code within the scope can change it. If inner code needs a different binding, it creates a nested scope with a new `where()`.

**Inheritance by StructuredTaskScope:** When a `StructuredTaskScope.fork()` creates a new virtual thread, the child inherits all the parent's active `ScopedValue` bindings automatically and immutably. No `InheritableThreadLocal` complexity.

**Stack-like binding:** Nested scopes create a stack of bindings:
```java
ScopedValue.where(SV, "outer").run(() -> {
    SV.get(); // "outer"
    ScopedValue.where(SV, "inner").run(() -> {
        SV.get(); // "inner" — shadows outer binding
    });
    SV.get(); // "outer" again — inner scope exited
});
SV.isBound(); // false — outer scope exited
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT ScopedValues (relying on ThreadLocal with virtual threads):

- Millions of virtual threads each with their own `ThreadLocal` maps → memory pressure.
- Developer must call `tl.remove()` at the end of every virtual thread task — easy to forget.
- Library code accidentally mutating `ThreadLocal` values causes subtle bugs.
- No safe automatic propagation of context to child virtual threads.

What breaks without it:
1. Memory leaks: `ThreadLocal` on virtual threads holds references to request context indefinitely if `remove()` is missed.
2. Incorrect audit trail: mutated `ThreadLocal` security context corrupts access control checks.

WITH ScopedValues:
→ Zero memory leak risk — scope exit automatically cleans up.
→ Immutable within scope — no accidental mutation by library code.
→ Automatic inheritance in structured concurrency — no manual propagation.

### 🧠 Mental Model / Analogy

> ScopedValue is like a company-wide announcement board for a meeting room. When a meeting starts (scope opens), the organiser pins a note: "Today's project: Project X, User: Alice" (ScopedValue binding). Everyone in the room (current thread and spawned child tasks) can read the board but cannot change it. When the meeting ends (scope closes), the board is wiped automatically. No one leaves with a stale note. Compare to ThreadLocal — like everyone having their own personal sticky note they can rewrite at any time and forget to throw away.

"Announcement board" = ScopedValue, "scope" = `where().run()` boundary, "room participants" = current thread + child virtual threads, "can't change the board" = immutability, "wiped at meeting end" = automatic cleanup.

### ⚙️ How It Works (Mechanism)

**ScopedValue binding implementation:**

```
ScopedValue.where(SV, value).run(task):
  1. Create a Snapshot binding SV → value onto current thread
  2. Store Snapshot in thread-local binding map (immutable entry)
  3. Execute task:
     - SV.get() reads from binding map → value
     - fork() in StructuredTaskScope copies binding map to child
  4. On task completion (normal or exceptional):
     - Binding map restored to pre-run state (stack pop)
     - SV binding automatically removed
```

**Performance vs ThreadLocal:**

`ThreadLocal` uses a `ThreadLocalMap` per thread — a hash map with open addressing. Lookup is O(1) but involves hash computation and map traversal.

`ScopedValue` uses an immutable linked structure — lookups traverse a short chain. For few (< 10) active scoped values, this is faster than `ThreadLocalMap` because no hashing, no resizing, no capacity management.

### 🔄 How It Connects (Mini-Map)

```
ThreadLocal (mutable, no inheritance, leak risk)
           ↓ replaced by
ScopedValue ← you are here
  (immutable, auto-inherited, auto-cleanup)
           ↓ works with
StructuredTaskScope
  (fork() inherits parent's ScopedValue bindings)
           ↓ on
Virtual Threads
```

### 💻 Code Example

Example 1 — Request context with ScopedValue (Java 21):

```java
public class RequestHandler {
    // Declare once as static constants
    public static final ScopedValue<String> REQUEST_ID =
        ScopedValue.newInstance();
    public static final ScopedValue<User> CURRENT_USER =
        ScopedValue.newInstance();

    public void handle(HttpRequest req) {
        String reqId = req.header("X-Request-ID");
        User user = authenticate(req);

        // Bind values for the duration of request processing
        ScopedValue.where(REQUEST_ID, reqId)
            .where(CURRENT_USER, user)
            .run(() -> {
                processRequest(req); // can call SV.get() anywhere
            });
        // After run() returns: bindings automatically cleared
    }
}

// Deep in call stack — no parameter threading needed
public class AuditService {
    public void log(String action) {
        // Access bound values without passing as parameters
        String reqId = RequestHandler.REQUEST_ID.get();
        User user = RequestHandler.CURRENT_USER.get();
        auditLog.write(reqId, user.getId(), action);
    }
}
```

Example 2 — ScopedValue with StructuredTaskScope (inheritance):

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    // Current thread has REQUEST_ID bound by caller
    String reqId = RequestHandler.REQUEST_ID.get();

    // Both child tasks inherit REQUEST_ID automatically
    var task1 = scope.fork(() -> {
        // REQUEST_ID.get() returns same reqId here!
        return fetchFromServiceA();
    });
    var task2 = scope.fork(() -> {
        // REQUEST_ID.get() returns same reqId here too!
        return fetchFromServiceB();
    });

    scope.join().throwIfFailed();
    return combine(task1.get(), task2.get());
}
```

Example 3 — Nested scope binding:

```java
ScopedValue<String> CONTEXT = ScopedValue.newInstance();

ScopedValue.where(CONTEXT, "admin").run(() -> {
    System.out.println(CONTEXT.get()); // "admin"

    // Inner scope temporarily shadows outer
    ScopedValue.where(CONTEXT, "read-only").run(() -> {
        System.out.println(CONTEXT.get()); // "read-only"
        // Useful for: temporarily downgrading permissions
    });

    System.out.println(CONTEXT.get()); // "admin" again
});
System.out.println(CONTEXT.isBound()); // false
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ScopedValue replaces ThreadLocal entirely | ScopedValue replaces ThreadLocal for context propagation patterns. ThreadLocal is still valid for mutable per-thread caches (e.g., SimpleDateFormat, StringBuilder). |
| ScopedValue works with arbitrary child threads | ScopedValue is inherited automatically only by StructuredTaskScope.fork() child threads. Manually created threads don't inherit bindings unless explicitly passed. |
| ScopedValue.get() can be called anywhere | get() throws NoSuchElementException if called outside a scope where the value was bound (or before any binding). Use isBound() to check. |
| Scoped values are mutable within a scope | They are immutable by design — you cannot call set() within a scope. Create a nested scope with a new where() to use a different value. |
| ScopedValue is only for virtual threads | ScopedValue works with both platform and virtual threads; the automatic inheritance feature is most valuable with virtual threads and StructuredTaskScope. |

### 🔥 Pitfalls in Production

**1. Accessing ScopedValue Outside a Bound Scope**

```java
// BAD: Accessing SV outside any scope
private static final ScopedValue<String> USER_ID =
    ScopedValue.newInstance();
// called without wrapping in ScopedValue.where().run()
String id = USER_ID.get(); // NoSuchElementException!

// GOOD: Always check isBound() or ensure proper scope setup
String id = USER_ID.isBound() ? USER_ID.get() : "anonymous";
```

**2. Storing Mutable Objects in ScopedValues**

```java
// BAD: ScopedValue bound to a mutable object
ScopedValue<Map<String, Object>> ATTRS =
    ScopedValue.newInstance();
ScopedValue.where(ATTRS, new HashMap<>()).run(() -> {
    ATTRS.get().put("key", "value"); // mutates shared map!
    // child threads sharing same map → race condition
});

// GOOD: Bind immutable objects only
ScopedValue.where(ATTRS,
    Map.of("key", "value")).run(...); // immutable map
```

**3. Confusing ScopedValue Inheritance with all Thread Types**

```java
// BAD: Expecting inheritance in manually created threads
ScopedValue.where(USER_ID, "alice").run(() -> {
    Thread.ofPlatform().start(() -> {
        // USER_ID is NOT inherited here!
        USER_ID.get(); // NoSuchElementException
    });
});

// GOOD: Use StructuredTaskScope.fork() for inheritance
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    scope.fork(() -> {
        USER_ID.get(); // "alice" inherited correctly
    });
    scope.join();
}
```

### 🔗 Related Keywords

- `ThreadLocal` — the mutable predecessor; still valid for mutable per-thread caches.
- `Virtual Threads (Project Loom)` — the primary use case for ScopedValues at scale.
- `Structured Concurrency` — the scoping mechanism that enables clean ScopedValue inheritance.
- `Continuation` — virtual thread state that carries ScopedValue bindings across unmount/remount.
- `Thread (Java)` — platform threads can also use ScopedValues, without automatic inheritance.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Immutable, scoped, auto-inherited thread  │
│              │ context — ThreadLocal but safe.           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Request context propagation (IDs, user,  │
│              │ locale) in virtual thread workloads;      │
│              │ StructuredTaskScope child inheritance.    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mutable per-thread state (use ThreadLocal)│
│              │ or passing to non-structured child threads│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ScopedValue: context that lives exactly  │
│              │ as long as the task — no more, no less."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Structured Concurrency → Virtual Threads  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A request-handling service uses `ScopedValue` to bind a `SecurityContext` object containing user permissions. The service uses `StructuredTaskScope` to fan out to 5 child tasks, each of which performs a permissions check via `SECURITY_CTX.get()`. One of the tasks calls a third-party library that creates its own platform thread internally (not via `StructuredTaskScope.fork()`). What happens when that platform thread tries to access the `SecurityContext` via `ScopedValue`, and what are two architectural options to handle this case?

**Q2.** `ThreadLocal` stores values in a `ThreadLocalMap` associated with the thread. When a thread is reused from a pool, its `ThreadLocalMap` persists between tasks unless `remove()` is called. Explain precisely why this "reuse problem" does NOT exist with `ScopedValue` — tracing the exact lifecycle of the binding from scope entry to scope exit, and identifying the data structure that makes automatic cleanup guaranteed.

