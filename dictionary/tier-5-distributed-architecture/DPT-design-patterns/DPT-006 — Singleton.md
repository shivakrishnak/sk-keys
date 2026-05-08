---
layout: default
title: "Singleton"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /design-patterns/singleton/
id: DPT-006
category: Design Patterns
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Classes and Objects, Static Methods
used_by: Object Pool, Service Locator, Dependency Injection Pattern
related: Factory Method, Object Pool, Dependency Injection Pattern
tags:
  - pattern
  - foundational
  - architecture
  - java
  - bestpractice
---

# DPT-006 — Singleton

⚡ TL;DR — Singleton ensures a class has exactly one instance and provides a global access point to it.

| #766 | Category: Design Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Classes and Objects, Static Methods | |
| **Used by:** | Object Pool, Service Locator, Dependency Injection Pattern | |
| **Related:** | Factory Method, Object Pool, Dependency Injection Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a logging system in a large Java application. Every class that needs logging creates its own `Logger` instance: `new Logger("app.log")`. Each instance opens the same file. Twenty threads write simultaneously. The log file becomes corrupted with interleaved characters. File handles accumulate — eventually the OS refuses to open more. Database connection managers face the same fate: each DAO creates its own connection, exhausting the database's connection limit within minutes of startup.

**THE BREAKING POINT:**
The concrete failure is resource exhaustion and state inconsistency. Multiple instances of what should be a single resource manager (logger, connection pool, configuration reader) compete for the same external resource. There is no shared state — each instance thinks it alone controls the resource. At production scale, this causes file corruption, connection timeouts, and configuration drift where different parts of the application read conflicting values.

**THE INVENTION MOMENT:**
This is exactly why the Singleton pattern was created. By guaranteeing that only one instance of a class exists and providing a single controlled access point, all clients share the same state and the same resource handle. The OS sees one file handle, the database sees one connection manager, and the configuration is read once.

---

### 📘 Textbook Definition

The **Singleton** pattern is a creational design pattern that restricts instantiation of a class to exactly one object and provides a global access point to that instance. It is implemented by making the constructor private, holding the sole instance in a static field, and exposing it through a static accessor method. The pattern guarantees single-instance semantics within a single JVM (or process), but not across distributed systems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One instance of a class, accessible from anywhere, created only once.

**One analogy:**
> Think of the President of a country. There is always exactly one President at a time. Anyone who needs to "talk to the President" uses the same person — they don't create a new one. The President's office has only one occupant.

**One insight:**
The Singleton's power is not the single instance itself — it is the guaranteed single state. All callers get the same object, so changes made by one caller are immediately visible to all others. This is both the pattern's greatest strength and its most dangerous trap.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Exactly one instance must exist at any time within a process.
2. The instance must be accessible globally without requiring clients to know how to create it.
3. Creation must happen at most once, and must be thread-safe.

**DERIVED DESIGN:**
Given invariant 1: the constructor must be private — no external code can call `new`. Given invariant 2: a static method (`getInstance()`) acts as the controlled access point — static methods are accessible without an instance. Given invariant 3: the static field holding the instance must be initialised safely in a multi-threaded environment.

The simplest thread-safe approach is the **class-loading guarantee**: Java's class loader guarantees that static field initialisation runs exactly once. This leads to the "eager initialisation" variant — the instance is created when the class is loaded, not when first requested. The "lazy initialisation" variant defers creation but requires synchronisation.

**THE TRADE-OFFS:**
**Gain:** Guaranteed single instance; controlled access; lazy or eager initialisation options; acts as a namespace-free global.
**Cost:** Hidden global state makes testing hard (can't inject a mock without reflection); violates single responsibility (the class manages both its own logic AND its own lifecycle); causes tight coupling; in distributed systems, each JVM has its own Singleton — it is NOT distributed-global.

---

### 🧪 Thought Experiment

**SETUP:**
A web application has a `ConfigurationManager` that reads `application.properties` from disk. Multiple servlets each need the database URL from this config. The application handles 500 requests/second.

**WHAT HAPPENS WITHOUT SINGLETON:**
Each servlet request creates `new ConfigurationManager()`. With 500 requests/second and 10 concurrent threads, 10 instances simultaneously open and parse `application.properties`. The file is read from disk 500 times per second — adding 5 ms of I/O per request. After a config change, some instances hold the old values (not yet recreated) while others hold new values. Two requests processed at the same millisecond get different database URLs and route to different database shards unexpectedly.

**WHAT HAPPENS WITH SINGLETON:**
`ConfigurationManager.getInstance()` returns the same object on every call. The file is read once at startup. All 500 requests/second share the same parsed config. A config change is applied in one place and immediately visible to all requests. I/O overhead: 0 after startup.

**THE INSIGHT:**
The Singleton transforms a per-request resource consumption into a one-time startup cost. The pattern is correct when the "single" semantics matches the domain — when there genuinely is only one configuration, only one log file, only one thread pool for the application.

---

### 🧠 Mental Model / Analogy

> A Singleton is like the single copy of a company's master employee directory. Every department that needs to look up an employee uses the same binder — they don't photocopy it and maintain separate versions. The receptionist controls access: when you ask for "the directory," you always get the same binder back.

- "Company master directory" → the singleton instance
- "Receptionist controlling access" → the static `getInstance()` method
- "Private binder locked in the receptionist's drawer" → private constructor
- "Departments using the directory" → client classes calling `getInstance()`
- "Looking up an employee" → reading or modifying shared state

Where this analogy breaks down: in a multi-office company (distributed system), each office has its own binder — there is no single global copy. The Singleton is process-local, not cluster-global.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Singleton is a special class that can only be created once. No matter how many times you ask for it, you always get back the exact same object — like a single master remote control for the TV. Nobody creates a second remote; everyone shares the one.

**Level 2 — How to use it (junior developer):**
Make the constructor `private` so nobody outside the class can call `new`. Add a `private static` field to hold the one instance. Add a `public static getInstance()` method that returns the held instance, creating it if it does not yet exist. In Java, the safest pattern is the **enum Singleton** (`enum MySingleton { INSTANCE; }`) — the JVM guarantees enum constants are created once and are inherently serialization-safe.

**Level 3 — How it works (mid-level engineer):**
The thread-safety challenge: if two threads simultaneously call `getInstance()` when the instance is `null`, both can enter the creation block and create two instances — breaking the invariant. The **double-checked locking** pattern mitigates this: check `null` outside the `synchronized` block (fast path), then re-check inside (safe creation). The `volatile` keyword on the instance field is required to prevent instruction reordering in the JVM. Alternatively, the **initialization-on-demand holder** (Bill Pugh Singleton) uses a nested static class — Java loads inner classes lazily and guarantees thread-safe static initialisation without `synchronized`.

**Level 4 — Why it was designed this way (senior/staff):**
The GoF Singleton was designed for single-process, single-JVM applications of the 1990s. In 2024, global shared mutable state is an architectural smell: it prevents horizontal scaling (each pod has its own Singleton), makes unit testing painful (tests share state), and hides dependencies (callers don't declare their need for the Singleton through their API). Modern frameworks (Spring, Guice) solve the same problem via **dependency injection with singleton scope** — same single-instance guarantee, but the container manages lifecycle and tests can inject alternatives. For new code, prefer `@Singleton`-scoped DI beans over hand-rolled Singletons.

---

### ⚙️ How It Works (Mechanism)

Three implementation variants, from simple to production-grade:

**Variant 1 — Eager Initialisation (simplest, thread-safe):**
```
┌─────────────────────────────────────────┐
│  CLASS LOADING (once, by JVM)           │
│                                         │
│  static final INSTANCE = new Singleton()│
│         ↓                               │
│  Constructor runs ONCE here             │
│         ↓                               │
│  INSTANCE field is permanently set      │
└─────────────────────────────────────────┘
Any call to getInstance() → returns INSTANCE
```
Thread-safe because JVM static initialisation is guaranteed to run once. Downside: instance created even if never used.

**Variant 2 — Double-Checked Locking (lazy + thread-safe):**
```
┌─────────────────────────────────────────┐
│  getInstance() called                   │
│         ↓                               │
│  if (instance == null)  ← check 1       │
│    synchronized(lock) {                 │
│      if (instance == null)  ← check 2   │
│        instance = new Singleton()       │
│    }                                    │
│  return instance                        │
└─────────────────────────────────────────┘
```
`volatile` on the field prevents CPU reordering that could expose a partially-constructed object to thread 2 between the allocation and the constructor completion.

**Variant 3 — Initialization-on-Demand Holder (preferred):**
```
┌─────────────────────────────────────────┐
│  outer class Singleton                  │
│    private static class Holder {        │
│      static final INSTANCE =            │
│           new Singleton()               │
│    }                                    │
│    static getInstance() {               │
│      return Holder.INSTANCE             │
│    }                                    │
└─────────────────────────────────────────┘
```
`Holder` is loaded only when `getInstance()` is first called. JVM class loading is inherently synchronised. No `synchronized` keyword needed at runtime — zero overhead for the common case.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client code
  → Singleton.getInstance()          ← YOU ARE HERE
  → returns existing instance (or creates once)
  → client uses instance methods
  → state shared across all clients
```

**FAILURE PATH:**
```
Singleton used in distributed system
  → Pod 1 has Instance A
  → Pod 2 has Instance B
  → State changes in A not visible in B
  → Data inconsistency errors, silent bugs
```

**WHAT CHANGES AT SCALE:**
In a single JVM, the Singleton scales perfectly — one instance serves unlimited callers with zero contention on the instance itself (only on the data inside). At 100x scale across multiple pods/containers, each pod has its own Singleton instance, effectively turning a "global resource" into per-pod local state. Any state the Singleton holds must be externalised to a shared store (Redis, database) at this scale.

---

### 💻 Code Example

**Example 1 — BAD: Not thread-safe lazy initialisation:**
```java
// BAD: two threads can both see null and create two instances
public class Config {
    private static Config instance;

    private Config() { loadFromDisk(); }

    public static Config getInstance() {
        if (instance == null) {           // race condition here
            instance = new Config();      // two objects possible
        }
        return instance;
    }
}
```

**Example 2 — GOOD: Initialization-on-demand holder (preferred):**
```java
// GOOD: lazy, thread-safe, no synchronisation overhead
public final class Config {

    private final String dbUrl;

    private Config() {
        // reads application.properties once at creation
        this.dbUrl = System.getProperty("db.url");
    }

    // Holder loaded only when getInstance() is first called
    private static final class Holder {
        static final Config INSTANCE = new Config();
    }

    public static Config getInstance() {
        return Holder.INSTANCE;
    }

    public String getDbUrl() { return dbUrl; }
}

// Usage:
String url = Config.getInstance().getDbUrl();
```

**Example 3 — BEST for modern Java: Enum Singleton:**
```java
// BEST: serialization-safe, reflection-safe, concise
public enum AppConfig {
    INSTANCE;

    private final String dbUrl =
        System.getProperty("db.url", "jdbc:h2:mem:test");

    public String getDbUrl() { return dbUrl; }
}

// Usage:
String url = AppConfig.INSTANCE.getDbUrl();
```

**Example 4 — Spring alternative (preferred in frameworks):**
```java
// In Spring: use @Component with default singleton scope
// No hand-rolling needed — Spring manages lifecycle

@Component          // singleton by default in Spring context
public class ConfigService {
    private final String dbUrl;

    public ConfigService(
        @Value("${db.url}") String dbUrl) {
        this.dbUrl = dbUrl;
    }

    public String getDbUrl() { return dbUrl; }
}
// Spring creates exactly one instance per ApplicationContext
// Testable: inject a mock ApplicationContext in tests
```

---

### ⚖️ Comparison Table

| Approach | Thread-Safe | Lazy | Overhead | Testable | Best For |
|---|---|---|---|---|---|
| **Singleton (Holder)** | Yes | Yes | None | Hard | Single-process globals |
| Enum Singleton | Yes | No | None | Medium | Config, registries |
| Spring @Component | Yes | Configurable | Container | Excellent | Application services |
| Static utility class | Yes (if immutable) | N/A | None | Hard | Stateless helpers |
| Global variable | No | N/A | None | Hard | Avoid entirely |

How to choose: prefer Spring (or another DI container) singleton scope when operating in a framework context — it gives the same single-instance guarantee with full testability. Use enum Singleton for truly standalone utilities (no DI container available). Avoid hand-rolled double-checked locking unless on a constrained platform.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Singleton makes state globally consistent in a distributed system | Singleton is process-local. Each JVM/pod has its own instance. Distributed state requires Redis, a database, or distributed caching |
| Singleton and static class are the same thing | A static class cannot be subclassed, polymorphically extended, or passed as a dependency. A Singleton is an object that can implement interfaces and be mocked |
| Double-checked locking without volatile is safe in Java 5+ | Only if the field is declared `volatile`. Without it, the JVM may publish a reference to a partially-constructed object due to instruction reordering |
| Singletons are always bad and should never be used | They are problematic when they hold mutable state in DI-free contexts. Immutable Singletons (enum, config reader that never changes) are fine and common |
| The enum Singleton is a hack | Joshua Bloch endorsed enum Singleton in Effective Java as the best approach — it handles serialisation and reflection attacks that other patterns don't |

---

### 🚨 Failure Modes & Diagnosis

**1. Broken Singleton in Multi-Classloader Environments**

**Symptom:** Two distinct instances of the "Singleton" coexist in the same JVM. State changes visible to code loaded by ClassLoader A are invisible to code loaded by ClassLoader B.

**Root Cause:** Java's Singleton guarantee is per-ClassLoader, not per-JVM. Application servers (Tomcat, WildFly) use separate ClassLoaders per deployed application. If the Singleton class is loaded by multiple ClassLoaders, each gets its own static field — and therefore its own instance.

**Diagnostic:**
```bash
# Add to Singleton constructor to detect duplicates
System.out.println("Singleton created by: "
  + Thread.currentThread()
    .getContextClassLoader()
    .getClass().getName());
# If this prints more than once, ClassLoader isolation is the cause
```

**Fix:**
Move the Singleton class to the parent ClassLoader (the server's lib directory), not the application's WEB-INF/lib. Alternatively, use a JNDI registry or the application's DI container to share the single instance across classloaders.

**Prevention:** Never rely on class-level statics for shared state across deployment units. Use an external store or a DI container's singleton scope.

---

**2. Thread-Unsafe Lazy Initialisation Race**

**Symptom:** Application works in development (single thread, deterministic order) but fails intermittently in production. Two instances are created, causing inconsistent state in the resource the Singleton manages (e.g., two log files opened).

**Root Cause:** The `getInstance()` check-then-act is not atomic. Two threads both pass `if (instance == null)` before either completes the constructor.

**Diagnostic:**
```java
// Add to constructor to catch if called twice:
private static final AtomicInteger count =
    new AtomicInteger(0);
private Singleton() {
    if (count.incrementAndGet() > 1) {
        throw new IllegalStateException(
            "Singleton created twice!");
    }
}
```

**Fix:**
```java
// BAD: race condition
if (instance == null) { instance = new Singleton(); }

// GOOD: use holder pattern (no lock at steady state)
private static class Holder {
    static final Singleton INSTANCE = new Singleton();
}
```

**Prevention:** Never use unsynchronised lazy initialisation. Default to the holder pattern or eager initialisation.

---

**3. Singleton Bleeding State Between Tests**

**Symptom:** Tests pass individually but fail when run together. A test that passes in isolation fails when run after another test that configured the Singleton differently.

**Root Cause:** The Singleton's static field holds state across test boundaries. JUnit does not reload classes between tests by default; the static field persists between test methods.

**Diagnostic:**
```bash
# Run tests in random order to expose ordering dependency
mvn test -Dsurefire.runOrder=random
# If failures appear only in certain orderings: Singleton state leak
```

**Fix:**
```java
// Add a reset method for test use only
@VisibleForTesting
static void resetForTest() {
    Holder.INSTANCE = null; // reflection required for final
}
// Better: refactor to use DI and inject in tests
```

**Prevention:** Prefer DI container singletons — Spring's `@SpringBootTest` resets context between test classes. Avoid static mutable fields in application code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` — Singleton is a class-level pattern; OOP fundamentals (constructors, static members) are required
- `Static Methods` — the `getInstance()` accessor is a static method; understanding class-level vs instance-level methods is essential
- `Thread Safety` — production Singleton implementations require understanding of race conditions and the Java Memory Model

**Builds On This (learn these next):**
- `Object Pool` — extends Singleton with a managed pool of pre-created instances for performance-critical resources
- `Dependency Injection Pattern` — the modern alternative to Singleton for managing single instances in testable, decoupled architectures
- `Service Locator` — combines Singleton with a registry of named services; an alternative (often anti-pattern) to DI

**Alternatives / Comparisons:**
- `Factory Method` — creates new instances on demand rather than reusing one; use when each caller needs its own independent instance
- `Monostate Pattern` — all instances share the same state via static fields; achieves Singleton-like semantics without restricting instance count

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Class that creates exactly one instance   │
│              │ and provides a global access point        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multiple instances of a shared resource   │
│ SOLVES       │ manager cause state conflicts             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The guarantee is process-local, not       │
│              │ distributed — each JVM has its own        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Exactly one shared resource exists:       │
│              │ config reader, log manager, thread pool   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mutable state in testable code; or in a  │
│              │ distributed / multi-JVM environment       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple global access vs hidden coupling   │
│              │ and hard-to-test shared mutable state     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One instance — everyone shares state,   │
│              │  but only within this process."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Object Pool → Dependency Injection →      │
│              │ Service Locator                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Singleton `CacheManager` that holds 500 MB of in-memory cached data. Your application is deployed to a Kubernetes cluster that auto-scales from 2 to 20 pods under load. A user updates a product price, which should invalidate the product's cache entry. Trace exactly what happens to cache consistency across all 20 pods, and describe two different architectural approaches to solve this without removing the Singleton from each pod.

**Q2.** A junior engineer argues: "I'll use a Singleton for our `UserSessionStore` because there should only ever be one session store." You know the application runs behind a load balancer across 4 servers. What specific failure will occur when User A's session is written on Server 1 and User A's next request is routed to Server 2? What is the fundamental design error in the engineer's reasoning, and what should they use instead?

