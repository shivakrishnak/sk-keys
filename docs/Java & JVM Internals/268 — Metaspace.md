---
layout: default
title: "Metaspace"
parent: "Java & JVM Internals"
nav_order: 268
permalink: /java/metaspace/
number: "0268"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: JVM, Class Loader, Heap Memory
used_by: GraalVM, JIT Compiler, Reflection
related: Heap Memory, Stack Memory, Class Loader, PermGen
tags:
  - java
  - jvm
  - memory
  - internals
  - intermediate
---

# 268 — Metaspace

⚡ TL;DR — Metaspace is the JVM's native memory region where class metadata lives — it replaced PermGen in Java 8 and grows dynamically instead of hitting a fixed cap.

| #268 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Class Loader, Heap Memory | |
| **Used by:** | GraalVM, JIT Compiler, Reflection | |
| **Related:** | Heap Memory, Stack Memory, Class Loader, PermGen | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In Java 7 and earlier, class metadata (the compiled description of every class — its methods, fields, constant pool) was stored in the Permanent Generation (PermGen), which was part of the Java heap. PermGen had a fixed maximum size (default: 64 MB, tunable with `-XX:MaxPermSize`). In application servers and frameworks that heavily used dynamic class generation (CGLIB, Groovy, JSP compilation, Hibernate), PermGen would fill up with class metadata and throw `java.lang.OutOfMemoryError: PermGen space` — one of the most infamous JVM errors.

**THE BREAKING POINT:**
PermGen being heap-managed created an absurd situation: you had to tune two heap parameters (`-Xmx` for objects, `-XX:MaxPermSize` for classes) independently, and getting both right required guessing how many classes your application would load. In microservices and app servers with hot-deploy, every redeployment loaded new classes without fully unloading old ones — filling PermGen inevitably.

**THE INVENTION MOMENT:**
Moving class metadata out of the Java heap into native memory (OS-managed) with auto-sizing removed the fixed cap entirely. This is exactly why Metaspace replaced PermGen in Java 8.

---

### 📘 Textbook Definition

Metaspace is a JVM memory region introduced in Java 8 that stores class metadata: class structures, method bytecode, constant pools, method descriptors, and static variables. Unlike its predecessor PermGen, Metaspace is allocated from native (OS) memory rather than the Java heap, and it grows dynamically up to the available native memory (or an explicit `-XX:MaxMetaspaceSize` limit). Metaspace is managed by a separate allocator from the Java heap GC but is collected when its ClassLoader becomes unreachable. Excessive growth is the primary symptom of ClassLoader leaks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Metaspace is where the JVM stores the blueprint of every class — outside the Java heap, in native memory.

**One analogy:**
> A library contains both books (Java objects, on the heap) and the library's card catalogue (Metaspace — class metadata). The card catalogue describes every book: author, genre, location. When a book is discarded (object GC'd), the catalogue entry stays. Only when an entire section closes (ClassLoader GC'd) does the catalogue section for all those books get removed.

**One insight:**
Metaspace growing indefinitely is almost always a ClassLoader leak, not a class count problem. When old ClassLoader instances are not GC'd (because something still holds a reference to one of their classes), their Metaspace allocations are never freed — a silent memory leak that only manifests under repeated deployment cycles.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every class loaded into the JVM requires metadata storage (its structure, bytecode, constant pool).
2. Class metadata lifetimes are tied to ClassLoader lifetimes — when a ClassLoader is GC'd, its classes are unloaded.
3. The number of live classes in a long-running application server can grow unboundedly with ClassLoader leaks.

**DERIVED DESIGN:**
Invariant 1 requires a dedicated storage region. Invariant 2 means metadata cannot be stored in the main object heap (which is GC'd based on object reachability, not ClassLoader lifecycle). Invariant 3 means a fixed-cap region (PermGen) will eventually run out. Moving to native memory (Metaspace) removes the cap, turning PermGen OOM into a visible native memory growth problem instead.

**THE TRADE-OFFS:**
**Gain:** No more `PermGen OOM` from a fixed cap; auto-sizing; simpler tuning.
**Cost:** Metaspace can grow and consume all native memory if ClassLoader leaks exist — an uncapped leak is worse than a capped one for some production scenarios; must set `-XX:MaxMetaspaceSize` explicitly for safety.

---

### 🧪 Thought Experiment

**SETUP:**
A Tomcat server hot-deploys 10 iterations of a web application. Each deploy loads 500 classes. Each undeploy should unload those 500 classes (their ClassLoader becomes garbage).

**WHAT HAPPENS WITH PERMGEN (Java 7):**
Deploy 1: 500 classes loaded, 32 MB of PermGen. Deploy 2: another 500 new proxy classes (because the ClassLoader isn't fully GC'd — a static JDBC driver registration holds a reference). PermGen now has 64 MB of metadata. By Deploy 4, PermGen hits 128 MB limit: `OutOfMemoryError: PermGen space`. Tomcat crashes. The deployment that was supposed to fix a bug in production is now the cause of an outage.

**WHAT HAPPENS WITH METASPACE (Java 8+):**
Same scenario, but Metaspace grows dynamically. The leak still exists — old classes aren't unloaded. But instead of a hard crash, Metaspace slowly grows toward native memory limits. The administrator notices via monitoring (`jcmd VM.native_memory`) and investigates the ClassLoader leak before it becomes critical. With `-XX:MaxMetaspaceSize=256m`, a hard cap provides safety.

**THE INSIGHT:**
Moving from a hard-cap fixed region to auto-sizing native memory doesn't fix ClassLoader leaks — it trades a hard crash for a gradual leak. Explicit monitoring and a safety cap are still required.

---

### 🧠 Mental Model / Analogy

> Metaspace is like a city's building permit archive. Every time a new building (class) is constructed, a permit (class metadata) is filed in the archive. When a building is demolished (class unloaded with its ClassLoader), the permit is removed. But if the demolition company (ClassLoader) never completes demolition (is never GC'd), the permits accumulate forever, and the archive grows until it fills the filing building (native memory).

- "Filing building" → native memory
- "Permit" → class metadata entry in Metaspace
- "Building demolished" → ClassLoader GC'd → class unloaded
- "Demolition company that never completes" → ClassLoader leak

Where this analogy breaks down: unlike physical filing space, Metaspace doesn't have a physical limit — it grows until the OS says "no more memory". With `-XX:MaxMetaspaceSize`, you impose an artificial limit.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When Java loads a class, it needs to remember information about that class — what methods it has, what fields it contains, what instructions make up each method. This class information lives in Metaspace. It's separate from the objects your program creates, and it grows automatically as more classes are loaded.

**Level 2 — How to use it (junior developer):**
You don't interact with Metaspace directly. Set `-XX:MetaspaceSize=128m` (initial allocation) and `-XX:MaxMetaspaceSize=256m` (safety cap) in production to prevent unbounded growth. In Java 8, if you see `OutOfMemoryError: Metaspace`, it usually means a ClassLoader leak. Check for repeated hot deploys without proper ClassLoader cleanup.

**Level 3 — How it works (mid-level engineer):**
Metaspace is allocated from native memory using `mmap`. Each ClassLoader has its own Metaspace allocator (Chunk). When a ClassLoader becomes unreachable and GC collects it, all of its Metaspace chunks are returned to the OS. The JVM triggers a Metaspace GC (class unloading) during Full GC cycles. The `-XX:MetaspaceSize` flag sets the threshold for the first Metaspace GC (not the initial size), which is confusingly named.

**Level 4 — Why it was designed this way (senior/staff):**
The PermGen-to-Metaspace transition involved a subtle design choice: class metadata was moved to native memory, but string interning (`String.intern()`) was moved from PermGen to the Java heap. This is why `OutOfMemoryError: Java heap space` can now be caused by string interning that previously caused `PermGen space`. The OpenJDK engineers debated whether to leave string interning in PermGen or move it; the heap was chosen because strings are normal objects subject to GC, while class metadata has a fundamentally different lifecycle.

---

### ⚙️ How It Works (Mechanism)

**JVM Memory Layout Including Metaspace:**

```
┌─────────────────────────────────────────────┐
│        JVM MEMORY REGIONS                   │
├─────────────────────────────────────────────┤
│ Java Heap (-Xms to -Xmx)                    │
│   Young Generation (Eden + Survivors)        │
│   Old Generation (Tenured)                  │
├─────────────────────────────────────────────┤
│ Metaspace [native memory]                   │
│   Class metadata (per ClassLoader chunk)    │
│   ┌─────────────────────────────────────┐   │
│   │ ClassLoader A's Metaspace chunk     │   │
│   │  ├─ com.example.ServiceA metadata   │   │
│   │  ├─ com.example.DaoA metadata       │   │
│   │  └─ ... (500+ classes)             │   │
│   ├─────────────────────────────────────┤   │
│   │ ClassLoader B's Metaspace chunk     │   │
│   └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│ Code Cache [native memory]                  │
│   JIT-compiled native code                  │
├─────────────────────────────────────────────┤
│ Stack Memory (per thread) [native]          │
└─────────────────────────────────────────────┘
```

**What Metaspace Contains Per Class:**
- Class name, superclass, interfaces
- Field descriptors (name, type, access flags)
- Method descriptors + bytecode
- Constant pool (string literals in UTF-8, class/method references)
- Annotations
- Static field values (moved to heap in some JVM versions)

**Class Unloading (Metaspace collection):**
When a ClassLoader becomes unreachable (no strong references from GC roots), during the next Full GC:
1. JVM marks the ClassLoader as collectable.
2. All classes loaded by that ClassLoader are unloaded.
3. Their Metaspace chunks are freed back to the OS.
4. Metaspace size decreases.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Application starts
  → Bootstrap ClassLoader loads JDK classes
    → Metaspace allocated for java.lang.*, etc.
  → App ClassLoader loads app classes
    → Metaspace allocated ← YOU ARE HERE
  → Application runs
  → Hot redeploy: old ClassLoader → garbage
    → Full GC: old ClassLoader GC'd
    → Metaspace chunks freed
  → New ClassLoader loads new classes
    → Metaspace reallocated
```

**FAILURE PATH:**
```
ClassLoader leak (old loader not GC'd)
  → Metaspace grows each deployment
  → Hits -XX:MaxMetaspaceSize or native memory
  → OutOfMemoryError: Metaspace
  → Application crashes
  → Diagnosis: heap dump → find stuck ClassLoader
```

**WHAT CHANGES AT SCALE:**
At scale with microservices and rolling deployments, class loading patterns stabilise — the same classes are loaded once and remain for the JVM lifetime. Metaspace is not a scaling concern in this model. The risk scenario is application servers with hot-reload under heavy deployment frequency — Metaspace then grows with each deployment, making monitoring essential.

---

### 💻 Code Example

Example 1 — Configure Metaspace in production:
```bash
# BAD: No Metaspace cap — can grow unboundedly
java -jar myapp.jar

# GOOD: Set initial + cap for safety
java -XX:MetaspaceSize=128m \
     -XX:MaxMetaspaceSize=256m \
     -jar myapp.jar
# Note: MetaspaceSize = threshold to trigger first GC
# MaxMetaspaceSize = hard cap (prevents OOM crashing OS)
```

Example 2 — Monitor Metaspace:
```bash
# Check Metaspace usage live
jcmd <pid> VM.native_memory summary | grep Metaspace
# Output:
# Metaspace (reserved=XXXmb, committed=YYmb)
#   class space (reserved=1020MB, committed=8MB)

# Detailed Metaspace stats
jcmd <pid> VM.native_memory detail | grep Metaspace
```

Example 3 — Detect ClassLoader leak causing Metaspace growth:
```bash
# Enable Metaspace tracking (before JVM start)
java -XX:NativeMemoryTracking=detail \
     -jar myapp.jar

# After several hot deploys, check growth
jcmd <pid> VM.native_memory baseline
# (do hot deploy cycle)
jcmd <pid> VM.native_memory summary.diff
# Look for growing "Class" section after each deploy

# Heap dump analysis for stuck ClassLoaders:
jmap -dump:format=b,file=/tmp/heap.hprof <pid>
# In Eclipse MAT: search for ClassLoader instances
# that have large retained heap = leak candidates
```

Example 4 — JDBC driver causing ClassLoader leak (common pattern):
```java
// BAD: JDBC driver registers itself in DriverManager
// using a static reference — prevents ClassLoader GC
// (This is the #1 cause of Metaspace leaks in Tomcat)
public class MyServletContextListener
        implements ServletContextListener {
    @Override
    public void contextDestroyed(
            ServletContextEvent sce) {
        // Missing: deregister JDBC drivers!
    }
}

// GOOD: deregister on webapp undeploy
@Override
public void contextDestroyed(
        ServletContextEvent sce) {
    // Prevent ClassLoader leak from JDBC driver
    Enumeration<Driver> drivers =
        DriverManager.getDrivers();
    while (drivers.hasMoreElements()) {
        Driver driver = drivers.nextElement();
        if (driver.getClass().getClassLoader()
                == getClass().getClassLoader()) {
            try {
                DriverManager.deregisterDriver(driver);
            } catch (SQLException e) {
                // log
            }
        }
    }
}
```

---

### ⚖️ Comparison Table

| Memory Region | Java Version | Stores | GC Managed | Hard Cap | Notes |
|---|---|---|---|---|---|
| PermGen | Java ≤ 7 | Class metadata + intern strings | Yes (heap) | Yes (MaxPermSize) | Famous for PermGen OOM |
| **Metaspace** | Java ≥ 8 | Class metadata only | Via Full GC | Optional (MaxMetaspace) | Auto-sizing native memory |
| Java Heap | All | Objects, arrays, intern strings (Java 8+) | Yes (GC) | Yes (Xmx) | Main GC-managed area |
| Code Cache | All | JIT-compiled native code | Rare | Yes (ReservedCodeCache) | Separate from Metaspace |

How to choose: You don't choose Metaspace — it's automatic. You tune it: set `-XX:MaxMetaspaceSize` as a safety cap in production to prevent native memory exhaustion from ClassLoader leaks.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Metaspace is part of the Java heap" | Metaspace uses native OS memory, completely separate from the Java heap (-Xmx has no effect on Metaspace). |
| "OutOfMemoryError: Metaspace means I have too many classes" | More often it means a ClassLoader leak — old ClassLoaders not being GC'd, accumulating class metadata without releasing it. |
| "-XX:MetaspaceSize sets the initial Metaspace allocation" | It sets the threshold at which the JVM triggers the first Metaspace GC — not the initial size. Initial size is much smaller. |
| "Metaspace cannot be limited" | You can cap it with -XX:MaxMetaspaceSize. Without a cap, it can consume all native memory. Always set this in production. |
| "String literals are stored in Metaspace" | Since Java 8, String literals and interned strings are on the Java heap (moved from PermGen). Metaspace contains only class/method metadata. |

---

### 🚨 Failure Modes & Diagnosis

**1. OutOfMemoryError: Metaspace from ClassLoader Leak**

**Symptom:** `java.lang.OutOfMemoryError: Metaspace` after multiple hot deployment cycles in an application server.

**Root Cause:** Old ClassLoader instances not garbage collected because static references (JDBC drivers, logging frameworks, ThreadLocals) hold references to classes from the old ClassLoader.

**Diagnostic:**
```bash
# Monitor Metaspace growth across redeploys
jcmd <pid> VM.native_memory summary | grep Class
# If "committed" keeps growing with each deploy → leak

# Heap dump → Eclipse MAT → ClassLoader instances
jmap -dump:format=b,file=/tmp/heap.hprof <pid>
# In MAT: List Objects → com.*.classloader types
# Check retained heap for old ClassLoader objects
```

**Prevention:** Deregister JDBC drivers, thread locals, and logging on webapp undeploy. Use static analysis tools to detect common leak patterns.

**2. Metaspace Consuming Unexpected Native Memory**

**Symptom:** JVM process uses significantly more native memory than `-Xmx` + stack + Metaspace estimate suggests.

**Root Cause:** Metaspace fragmentation — native allocations leave gaps that are not reusable. Or: high class loading caused by reflection-heavy frameworks (Hibernate, Spring).

**Diagnostic:**
```bash
# Detailed native memory breakdown
java -XX:NativeMemoryTracking=detail \
     -jar myapp.jar
jcmd <pid> VM.native_memory detail > /tmp/nmt.txt
grep -A 5 "Class" /tmp/nmt.txt
```

**Prevention:** Set `-XX:MaxMetaspaceSize`; profile class loading with `-verbose:class` to find unexpected class loading.

**3. Unexpected Metaspace GC Causes Latency Spike**

**Symptom:** Periodic latency spikes not correlated with heap GC logs; Metaspace GC not visible in standard GC logs.

**Root Cause:** When Metaspace reaches the `-XX:MetaspaceSize` threshold, the JVM triggers a Full GC (which includes class unloading), causing a stop-the-world pause unrelated to heap pressure.

**Diagnostic:**
```bash
# Enable GC logging including Metaspace events
java -Xlog:gc*:file=/var/log/gc.log:time \
     -jar myapp.jar
grep "Metaspace" /var/log/gc.log
```

**Prevention:** Set `-XX:MetaspaceSize` large enough that the threshold is never reached in normal operation (set it above the expected steady-state class metadata size).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — Metaspace is one of the JVM's memory regions
- `Class Loader` — ClassLoader lifecycle determines when Metaspace entries are freed
- `Heap Memory` — the Java heap is a separate region from Metaspace; understanding the distinction is critical

**Builds On This (learn these next):**
- `GraalVM` — uses Metaspace differently for native image compilation; class metadata is processed at build time
- `JIT Compiler` — JIT-compiled native code goes to the Code Cache, not Metaspace
- `Reflection` — heavily uses Metaspace-stored class metadata for runtime type introspection

**Alternatives / Comparisons:**
- `PermGen` — Metaspace's predecessor in Java 7 and earlier; fixed-cap heap region for class metadata
- `Off-heap` — another form of native memory usage for data, not metadata

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Native memory region for class metadata;  │
│              │ replaced PermGen in Java 8                │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ PermGen had a fixed cap causing OOM on    │
│ SOLVES       │ class-heavy app servers                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Metaspace OOM = ClassLoader leak, not too │
│              │ many classes. Find the leaked ClassLoader │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — automatic. Tune with             │
│              │ -XX:MaxMetaspaceSize in production        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — cannot avoid. Monitor it with       │
│              │ NativeMemoryTracking in production        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Auto-sizing flexibility vs risk of        │
│              │ unbounded native memory growth from leaks │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Metaspace: the JVM's class blueprint     │
│              │ archive — grows freely until a leak fills  │
│              │ native memory"                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Class Loader → GC Roots → Full GC         │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application running in Tomcat is hot-redeployed 50 times during a CI/CD stress test. After deployment 20, `OutOfMemoryError: Metaspace` appears. The team increases `-XX:MaxMetaspaceSize` from 256m to 512m — the error disappears temporarily but returns at deployment 40. Why does increasing MaxMetaspaceSize only delay rather than fix the problem, and what is the correct diagnostic approach to find the root cause?

**Q2.** In Java 7, `String.intern()` stored interned strings in PermGen. In Java 8, they moved to the Java heap (Metaspace stores only class metadata). How does this change affect the `OutOfMemoryError` you would observe if your application interned millions of unique strings? Which OOM message would you see in Java 7 vs Java 8, and which is easier to diagnose and fix using standard heap analysis tooling?

