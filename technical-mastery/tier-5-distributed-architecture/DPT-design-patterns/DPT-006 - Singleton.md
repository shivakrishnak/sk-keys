---
id: DPT-006
title: Singleton
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on: DPT-001, DPT-005
used_by: DPT-007, DPT-039
related: DPT-039, DPT-031, DPT-005
tags:
  - pattern
  - creational
  - foundational
  - intermediate
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/design-patterns/singleton/
---

⚡ TL;DR - Singleton guarantees exactly one instance of a class
exists in a JVM process, but it is one of the most misused
patterns because its process-level scope assumption breaks in
distributed and multi-threaded systems.

| #6 | Category: Design Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005 | |
| **Used by:** | DPT-007, DPT-039 | |
| **Related:** | DPT-039, DPT-031, DPT-005 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An application needs a shared configuration object, a connection
pool, or a logging system. Without coordination, every class that
needs these creates its own instance. The application now has
20 connection pools competing for database connections, 8 logger
instances writing to the same log file with interleaved output,
and 15 config objects loaded from disk with inconsistent state.
Resource consumption multiplies. Consistency breaks.

**THE BREAKING POINT:**
Multiple instances of a resource manager produce race conditions
in production that are invisible in testing (single-threaded
tests do not expose the race). The logger writes corrupted
output at peak load. The config object loaded at startup has
different state from the config object loaded in the request
handler. These bugs are hard to reproduce and expensive to find.

**THE INVENTION MOMENT:**
This is exactly why Singleton exists: to guarantee that shared
infrastructure objects exist exactly once, preventing the
resource multiplication problem at the language level.

**EVOLUTION:**
Singleton is the simplest GoF Creational pattern and the first
pattern in the book for historical reasons. Its popularity led
to significant misuse: by the mid-2000s, Singleton had become
a synonym for global state, producing tightly coupled, untestable
code. Martin Fowler's "Patterns of Enterprise Application
Architecture" (2002) noted that Singleton's global state
semantics made it problematic for unit testing. The rise of
Dependency Injection frameworks (Spring, Guice) provided a
better alternative for most Singleton use cases: DI containers
manage instance lifecycle and inject shared instances without
the global state semantics. Today, explicit Singleton
implementations are rare in well-tested codebases; DI-managed
singletons are the standard replacement.

---

### 📘 Textbook Definition

The **Singleton pattern** is a Creational design pattern that
ensures a class has exactly one instance and provides a global
access point to that instance. It restricts instantiation by
making the constructor private, storing the sole instance as a
static field, and exposing it through a static accessor method.
The pattern's guarantee is scoped to a single JVM process -
it provides no uniqueness guarantee across multiple processes,
JVMs, or distributed nodes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Singleton is the "one key for the whole building" pattern -
everyone who needs access gets the same key, pointing to
the same object.

**One analogy:**
> A government issues one official seal - not one per department,
> one per citizen. Every document needing an official seal uses
> the same seal. The seal's uniqueness is guaranteed by the
> government's control over who holds it. Singleton does the
> same for an object: control over construction ensures exactly
> one instance exists.

**One insight:**
The important thing to understand about Singleton is its SCOPE:
one instance per JVM process. In a horizontally scaled service
with 10 pods, each pod has its own Singleton - 10 instances
total in the system. If your "singleton" needs to be truly unique
across the entire distributed system, Singleton is the wrong
pattern - you need a distributed coordination mechanism
(distributed lock, registry, external config service).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Exactly one instance must exist per JVM process.
2. The single instance must be globally accessible from any point
   in the codebase.
3. The instance must be created lazily (on first access) or
   eagerly (at class loading) - both are valid strategies.

**DERIVED DESIGN:**
To enforce invariant 1 and 2: make the constructor private
(prevents external instantiation), store the instance as a static
field (accessible from the class itself), and expose a static
getter. The single construction path plus private constructor
guarantees one instance.

**THE TRADE-OFFS:**

**Gain:** Prevents resource duplication for shared infrastructure
objects. One database pool, one logger, one config.

**Cost:** Global mutable state is hard to test (every test shares
the same instance), hard to replace (cannot inject a mock),
and hard to reason about (any code anywhere can access and
modify it). Singleton violates the Dependency Inversion Principle
by creating a hidden, non-injectable dependency.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Some objects genuinely should exist once per
process: the JVM's GC, an OS-level file descriptor registry.
For these, Singleton's guarantee is correct.

**Accidental:** Most application-level Singletons (services,
repositories, config) exist once because of lifecycle management
requirements, not because having two would be fundamentally wrong.
For these, a DI container managing a single-scope bean is the
correct solution - it provides the same lifecycle behavior without
the global access and untestability problems.

---

### 🧪 Thought Experiment

**SETUP:**
An application initialises a configuration object that reads
from a YAML file at startup. The config is used in 15 different
service classes.

**WHAT HAPPENS WITHOUT SINGLETON:**
Each of the 15 services creates `new Config()`. The YAML file
is read 15 times on startup. If the file is modified between
reads (edge case), different services see different config
state. Memory usage is multiplied. If Config has any caching
or initialization cost, it is paid 15 times.

**WHAT HAPPENS WITH SINGLETON:**
`Config.getInstance()` is called 15 times but only instantiates
once. The YAML file is read once. All 15 services share the
same in-memory state. Memory and initialization cost are paid
once.

**THE INSIGHT:**
For read-only shared infrastructure (config, logging
configuration, connection pool), Singleton's guarantee of
one-instance is genuinely valuable. For mutable business
objects, the same guarantee becomes a liability.

---

### 🧠 Mental Model / Analogy

> Singleton is a master key cabinet. There is one cabinet in the
> building. Anyone who needs a key goes to the cabinet and gets
> the master key. The cabinet ensures only one master key exists.
> If the cabinet is in a locked room, getting the key requires
> permission (the DI container version). If the cabinet is in
> the lobby, anyone can walk up and take it (the static getter
> version).

- "Master key" - the singleton instance
- "Cabinet" - the static field storing the instance
- "Anyone can get it" - global access point (static getter)
- "Locked room cabinet" - DI container-managed singleton
- "Lobby cabinet" - class-level static Singleton

**Where this analogy breaks down:** A master key can be copied;
Singleton (with a private constructor) cannot be instantiated
again. The Singleton's guarantee is enforced at the language
level, not physical security.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Singleton ensures only one copy of an object ever exists in
the application. Like a school with one principal - not one
per class, one for the whole school.

**Level 2 - How to use it (junior developer):**
Implement with private constructor + static instance field +
static `getInstance()` method. For thread safety in modern Java,
use enum-based Singleton or the initialization-on-demand holder
idiom. Never use double-checked locking without understanding
the volatile requirement.

**Level 3 - How it works (mid-level engineer):**
In Java, class loading guarantees that static initializers run
exactly once per ClassLoader. The enum-based Singleton exploits
this: Java guarantees enum instances are constructed exactly once
and are serialization-safe. The holder idiom exploits lazy
class loading: the inner class `Holder` is not loaded until
`getInstance()` is called, providing lazy initialization without
synchronization overhead.

**Level 4 - Why it was designed this way (senior/staff):**
The global access point (static getter) is Singleton's most
problematic feature. It bypasses the Dependency Inversion
Principle: callers directly reference the concrete Singleton
class rather than an injected interface. This makes callers
impossible to test in isolation because the Singleton cannot
be replaced with a test double. The solution is to keep the
lifecycle guarantee (one instance) but remove the global access
point: inject the singleton instance through a DI container.
The instance is still created once; it is now an injectable
dependency rather than a global variable.

**Level 5 - Mastery (distinguished engineer):**
In a JVM, "one instance" scopes to one ClassLoader, not one
JVM. Containers like Tomcat use separate ClassLoaders per
web application, so a Singleton in `webapp-A.jar` and the same
class in `webapp-B.jar` produce two instances. In OSGi
(module system), each bundle has its own ClassLoader. Knowing
the ClassLoader scope determines whether the Singleton guarantee
actually holds. For truly application-wide singletons in a
multi-ClassLoader JVM, use the bootstrap ClassLoader or a
container-managed registry.

---

### ⚙️ How It Works (Mechanism)

```
Singleton Lifecycle
┌─────────────────────────────────────────────────────┐
│  First call to getInstance()                        │
│                                                     │
│  Thread A        Class Loading        Thread B      │
│  calls           ─────────────        calls         │
│  getInstance()   static field = null  getInstance() │
│      │           after class load         │         │
│      ▼                                   ▼          │
│  instance == null?  YES              instance == ?  │
│      │                                   │          │
│  create instance                         │          │
│  assign to static field              wait / read    │
│      │                               from field     │
│      ▼                                   ▼          │
│  return instance                    return SAME     │
│                                     instance        │
└─────────────────────────────────────────────────────┘
```

**Three implementation strategies:**

1. **Eager initialization (simplest, no lazy load):**
```java
public final class Config {
    // Instance created at class loading - thread-safe
    private static final Config INSTANCE = new Config();

    private Config() {}  // prevent external construction

    public static Config getInstance() { return INSTANCE; }
}
```

2. **Initialization-on-demand Holder (lazy + thread-safe):**
```java
public final class Config {
    private Config() {}

    // Holder class loaded only when getInstance() is called
    private static final class Holder {
        // JVM guarantees static init runs exactly once
        static final Config INSTANCE = new Config();
    }

    public static Config getInstance() {
        return Holder.INSTANCE;  // lazy, thread-safe, no sync
    }
}
```

3. **Enum Singleton (serialization-safe, simplest in Java):**
```java
public enum Config {
    INSTANCE;  // Java guarantees exactly one per ClassLoader
    // Add fields and methods normally
    public String getDatabaseUrl() { ... }
}
// Usage: Config.INSTANCE.getDatabaseUrl()
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
Eager initialization and Holder idiom are thread-safe because
JVM class loading is synchronized by the class loading mechanism
itself - no explicit `synchronized` needed. Enum Singleton is
thread-safe and serialization-safe by JVM guarantee. Double-
checked locking without `volatile` is NOT thread-safe due to
instruction reordering; this is a historically common bug in
pre-Java 5 code.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (DI-managed Singleton in Spring):**
```
Application startup
  → Spring container initialisation
  → @Bean method / @Component scan detects Config
  → Spring creates Config instance (singleton scope)
                        [← YOU ARE HERE]
  → Spring stores in ApplicationContext bean registry
  → Each @Autowired Config reference injected with
    the same stored instance
  → Application runs: all callers share one instance
```

**FAILURE PATH:**
```
Singleton created with mutable state
  → Test A modifies Singleton state
  → Test B runs, reads modified state (not reset)
  → Test B fails for non-obvious reasons
  → Debugging: hard to trace because state source is global
```

**WHAT CHANGES AT SCALE:**
In a horizontally scaled service with 10 instances: each JVM
has its own Singleton. A cached value in the Singleton of pod-1
is not visible to pod-2. Cache invalidation must be distributed
(Redis, external config server). Singleton's uniqueness guarantee
is always process-local.

---

### 💻 Code Example

**Example 1 - Wrong: Classic Singleton with testability problem:**

```java
// BAD: Global access breaks DI and testability
public class OrderService {
    public void processOrder(Order order) {
        // Hidden dependency on global Singleton
        Config config = Config.getInstance();
        if (config.isFeatureEnabled("express-checkout")) {
            // ...
        }
    }
}
// Cannot test OrderService with a mock Config
// Cannot test different config values without modifying
// the global Singleton state
```

**Example 2 - Good: DI-managed singleton preserves lifecycle:**

```java
// GOOD: DI container manages the lifecycle (Spring)
@Configuration
public class AppConfig {
    @Bean  // Spring default scope is singleton
    public Config config() {
        return Config.loadFromEnvironment();
    }
}

@Service
public class OrderService {
    private final Config config;  // injected by Spring

    OrderService(Config config) {  // injectable = testable
        this.config = config;
    }

    public void processOrder(Order order) {
        if (config.isFeatureEnabled("express-checkout")) { ... }
    }
}
// Tests inject a mock Config - no global state
```

**Example 3 - Thread-safe lazy Singleton (when DI not available):**

```java
// GOOD: Holder idiom - lazy, thread-safe, no overhead
public final class ConnectionPool {
    private ConnectionPool() { initializePool(); }

    private static final class Holder {
        static final ConnectionPool INSTANCE =
            new ConnectionPool();
    }

    public static ConnectionPool getInstance() {
        return Holder.INSTANCE;
    }
}
```

**How to test/verify correctness:**
In unit tests, always inject via constructor rather than calling
`getInstance()`. For legacy Singleton code under test, use
a test framework feature (Mockito `mockStatic`) or introduce
a seam: add a package-private setter for the instance used
only in tests. Property-test that `getInstance()` returns
the same reference across multiple calls in a single thread
and across multiple threads using `CountDownLatch`.

---

### ⚖️ Comparison Table

| Approach           | Thread-safe | Lazy | Testable | Serialization | Best For           |
| ------------------ | ----------- | ---- | -------- | ------------- | ------------------ |
| Eager static field | Yes         | No   | No       | Needs care    | Simple, no lazy    |
| **Holder idiom**   | Yes         | Yes  | No       | Needs care    | Lazy + thread-safe |
| Enum Singleton     | Yes         | No   | No       | Yes           | Enum-like objects  |
| DI-managed bean    | Yes         | Yes  | Yes      | N/A           | All modern code    |
| Double-checked lock| Needs volatile| Yes| No      | Needs care    | Avoid in new code  |

**How to choose:** In modern Java with a DI framework (Spring,
Quarkus), always prefer DI-managed singletons. They provide
the same lifecycle guarantee with injectable, testable, replaceable
instances. Use explicit Singleton only for infrastructure-level
objects that exist before the DI container starts (e.g.,
the logging framework itself).

---

### 🔁 Flow / Lifecycle

```
Singleton Lifecycle
─────────────────────────────────────────────────────
Phase 1: Class Loading
  JVM loads the Singleton class
  static initializer runs (eager) OR waits (Holder)

Phase 2: First Access
  getInstance() called
  Holder class loaded (lazy) OR static field returned
  Instance constructed (once, guaranteed by class loading)

Phase 3: Steady State
  All calls to getInstance() return the same reference
  No synchronization overhead after initialization

Phase 4: JVM Shutdown
  Singleton instance eligible for GC
  No explicit destroy lifecycle (unlike DI-managed beans)
  Resource cleanup must be registered as shutdown hook
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Singleton guarantees one instance per application | It guarantees one instance per ClassLoader - in Tomcat or OSGi, multiple ClassLoaders can produce multiple instances |
| Singleton is always thread-safe | Only with correct implementation (Holder idiom, enum, or eager); naive double-checked locking without volatile is not thread-safe |
| Singleton and DI container singleton are the same | DI-managed beans with singleton scope are injectable and testable; classic Singleton uses static global access and is not |
| Singleton is always bad | Appropriate for infrastructure objects that genuinely must exist once: logging, connection pool, system config |
| Enum Singleton is a hack | It is the recommended Java implementation: thread-safe, serialization-safe, protected against reflection attacks |

---

### 🚨 Failure Modes & Diagnosis

**Distributed Singleton Illusion**

**Symptom:**
Cache values stored in a Singleton on pod-1 are not visible
on pod-2. Users hitting different pods see different data.
Sticky sessions are added as a workaround, which limits
horizontal scaling.

**Root Cause:**
Singleton's uniqueness is process-local. A horizontally scaled
service with 10 pods has 10 independent Singleton instances.
Any mutable state in the Singleton is not shared across pods.

**Diagnostic Signal:**
If a Singleton contains mutable state (in-memory cache, counter,
feature flag state), check whether the service is horizontally
scaled. Any horizontal scaling produces the per-pod instance
problem.

**Diagnostic Command:**
```bash
# Check how many pods are running
kubectl get pods -l app=my-service

# If count > 1 and Singleton has mutable state:
# the distributed singleton illusion is present
```

**Fix:**
Move shared mutable state out of the Singleton to a distributed
cache (Redis), a distributed config store (Consul, AWS SSM),
or an event-driven state propagation mechanism. The Singleton
becomes read-only after initialization.

**Prevention:**
Design Singletons to be immutable after construction. Any
mutable state that must be consistent across instances must
live in an external shared store.

---

**Singleton Preventing Unit Tests**

**Symptom:**
Unit tests for a service fail intermittently because they
depend on a shared Singleton's state that was modified by
a previous test. Tests pass in isolation, fail in suite.

**Root Cause:**
The Singleton maintains state across test cases. Each test
modifies the Singleton without resetting it, and subsequent
tests run with unexpected state.

**Diagnostic Signal:**
Test failures that only appear when running the full suite,
not in isolation. State-dependent failures that vary with
test execution order.

**Diagnostic Command:**
```bash
# Run specific test in isolation (passes)
mvn test -Dtest=OrderServiceTest#testExpressCheckout

# Run full suite (fails due to Singleton state contamination)
mvn test
```

**Fix:**
For immediate relief: add a reset method to the Singleton
(package-private) and call it in `@BeforeEach`. For proper
fix: migrate to DI-managed beans so the Singleton instance
is injectable and each test can inject a fresh or mock instance.

**Prevention:**
Never use static Singleton access in testable production code.
Always inject shared objects as constructor parameters. The DI
container manages the lifecycle; the tests control the instance.

---

**Reflection-Based Singleton Breaking**

**Symptom:**
A Singleton's private constructor is called via reflection
by a deserialization framework or a malicious class, creating
a second instance and breaking the uniqueness guarantee.

**Root Cause:**
Java reflection (`setAccessible(true)` on the private
constructor) bypasses the private access modifier. Standard
Singleton implementations (static field + private constructor)
are vulnerable.

**Diagnostic Signal:**
`Class.forName("Config").getDeclaredConstructors()[0]
.setAccessible(true).newInstance()` succeeds and returns a
new instance. Deserialization creates new instances
(readObject bypass).

**Fix:**
Use enum-based Singleton - Java's specification prohibits
reflective construction of enum types. Throw from the private
constructor if a second construction is attempted:
```java
private Config() {
    if (Holder.INSTANCE != null) {
        throw new RuntimeException(
            "Singleton: use getInstance()"
        );
    }
}
```

**Prevention:**
For security-sensitive singletons, always use enum-based
implementation. For serializable singletons, implement
`readResolve()` to return the existing instance.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - why Singleton
  exists and what problem it solves at the pattern level
- `Java Class Loading` - ClassLoader scope determines what
  "one instance" means in practice

**Builds On This (learn these next):**
- `Dependency Injection Pattern` - the modern replacement for
  most Singleton use cases; provides the same lifecycle guarantee
  without global state
- `Double-Checked Locking` - the most common (and historically
  buggy) thread-safe Singleton implementation - understand the
  volatile requirement before using it

**Alternatives / Comparisons:**
- `Flyweight` - another Creational pattern for sharing instances;
  differs from Singleton in that Flyweight manages a pool of
  shared instances keyed by intrinsic state, not a single global
- `Service Locator` - an alternative global access mechanism
  for shared objects; shares Singleton's testability problems

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Creational pattern guaranteeing exactly  │
│              │ one instance per JVM process             │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Multiple instances of shared resources   │
│ SOLVES       │ (config, pool, logger) waste memory and  │
│              │ cause inconsistency                      │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ "One per process" - in 10 pods you have  │
│              │ 10 Singletons; it is NOT distributed     │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Infrastructure objects that are expensive│
│              │ to create and must be shared (pool, log) │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Business logic objects, testable code,   │
│              │ or distributed systems needing true      │
│              │ single-instance across nodes             │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Using Singleton for mutable business     │
│              │ state - becomes untestable global state  │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Resource efficiency vs testability and   │
│              │ Dependency Inversion compliance          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "One instance per JVM - not one per      │
│              │  system, not one per test, just one      │
│              │  per ClassLoader"                        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Factory Method → Abstract Factory → DI   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Singleton guarantees one instance per ClassLoader, not per
   JVM, cluster, or distributed system - horizontally scaled
   services each have their own Singleton
2. For modern Java code, prefer DI-managed singletons (Spring
   @Bean default scope) over explicit static Singleton - same
   lifecycle, injectable, testable
3. Enum-based Singleton is the safest Java implementation:
   thread-safe, serialization-safe, reflection-safe by JVM spec

**Interview one-liner:**
"Singleton ensures one instance per JVM process through a private
constructor and static accessor. Its core limitation is scope -
one per ClassLoader, not one per distributed system - and global
state semantics that break testability. In modern code, I replace
it with a DI container singleton scope: same lifecycle guarantee,
injectable and testable."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Resource uniqueness guarantees must specify their scope
precisely. "Exactly one" always requires "exactly one WHERE."
Process, ClassLoader, JVM, cluster, and globally are different
scopes, and the guarantee is only as strong as the scope is
correctly identified and enforced.

**Where else this pattern appears:**
- **Database primary keys** - a primary key guarantees uniqueness
  within one table (one relation), not across tables or databases;
  the scope of uniqueness must be specified
- **Mutex / lock** - a mutex guarantees mutual exclusion within
  one process; a distributed lock guarantees mutual exclusion
  across a distributed system; confusing the scopes produces
  race conditions
- **DNS namespace** - a domain name is globally unique; a
  hostname is unique within a domain; the uniqueness scope
  determines what "unique" means in each context

**Industry applications:**
- **Connection pools** - one pool per application in single-
  process deployments is the correct Singleton use case; each
  pod in a Kubernetes deployment manages its own pool, and the
  total connection count is pods * pool_size
- **Feature flag services** - feature flags need one consistent
  view per request, but not one per system; the Singleton is
  the in-process cache of the distributed flag state, not the
  distributed truth

---

### 💡 The Surprising Truth

The Singleton pattern is the most controversial entry in the GoF
book by a wide margin. Brian Button wrote an influential 2008
post titled "Singletons are Pathological Liars" describing how
Singleton's hidden global dependencies make code impossible to
reason about in isolation. The pattern has been called an
"anti-pattern" by multiple influential engineers. The GoF
themselves noted in the 1994 book that Singleton's global access
semantics was its most problematic aspect. Yet Singleton
implementations appear in virtually every major Java framework
(Log4j, Spring's ApplicationContext, JDBC DriverManager) because
the problem it solves - shared infrastructure objects - is real
and recurs regardless of the pattern's reputation. The lesson:
every pattern has a valid use case and an abuse case; Singleton's
valid use case is narrow and its abuse case is wide.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Explain to a junior engineer why a Singleton in a
   horizontally-scaled Kubernetes deployment does not guarantee
   one instance per deployment, and what the correct scope of
   the guarantee is
2. [DEBUG] Given a test suite with intermittent failures caused
   by Singleton state contamination across tests, identify the
   root cause and prescribe either a test-level reset mechanism
   or a DI migration path
3. [DECIDE] In a code review, identify whether a proposed
   Singleton is a legitimate infrastructure object (connection
   pool, logger) or a business logic object that should be
   DI-managed, and articulate the specific criterion
4. [BUILD] Implement a thread-safe lazy Singleton using the
   Holder idiom from memory, and explain why it is thread-safe
   without explicit synchronization
5. [EXTEND] Explain how Spring's `@Bean` with default scope
   implements the same lifecycle guarantee as a static Singleton
   but without global state access, and demonstrate a test that
   verifies a single instance is shared across multiple injection
   points

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice uses a Singleton to cache the results
of a database query. The cache is populated at startup and
read on every request. The service is deployed as 20 pods.
After a database update, the cache on each pod must be
invalidated. Design the full invalidation mechanism: what
signals the pods, how does each pod's Singleton respond, and
what happens to in-flight requests during invalidation? What
happens if one pod fails to receive the invalidation signal?

*Hint: The 20 Singletons are 20 independent caches. Invalidation
requires a distributed pub/sub or polling mechanism. Consider
the consistency window between the database update and the last
pod's cache invalidation, and what happens to requests reading
stale data during that window.*

**Q2.** Singleton violates the Dependency Inversion Principle
because callers directly reference the concrete class via
`getInstance()`. However, DI-managed beans with singleton scope
also guarantee one instance but DO satisfy DIP because they are
injected via interface. Are these the same pattern? What is
the minimum structural change to a static Singleton that makes
it satisfy DIP without a full DI framework?

*Hint: The static getter is the DIP violation, not the uniqueness
guarantee. Adding a package-private setter for tests introduces
a seam. Extracting an interface and injecting the instance
via constructor satisfies DIP while keeping the lifecycle
management logic in the Singleton.*

**Q3.** Write a test for a service that depends on a Singleton
logger. The test must verify that a specific log message is
written when an order exceeds a risk threshold. The logger
Singleton writes to a file. Without modifying production code,
how do you make this test fast, reliable, and isolated from
the file system?

*Hint: Consider test-level Singleton replacement (mockStatic),
capturing the log output in memory (in-memory appender for
SLF4J/Logback), or introducing a logging abstraction
(interface + adapter) that can be replaced in tests. Evaluate
each approach by testability, production code invasiveness,
and maintenance cost.*

---

### 🎯 Interview Deep-Dive

**Q1: What are the thread-safety concerns with Singleton,
and what is the safest Java implementation?**

*Why they ask:* Singleton thread-safety is a classic Java
concurrency test that reveals whether the candidate understands
the JVM memory model and class loading.

*Strong answer includes:*
- Lazy initialization with naive `if (instance == null)` check
  is not thread-safe: two threads can both see null and both
  create instances
- Double-checked locking without `volatile` is not safe due to
  instruction reordering (Java Memory Model allows publishing
  a partially-constructed object to the static field)
- Safest options: enum-based Singleton (JVM-guaranteed, no
  explicit synchronization, serialization-safe); Holder idiom
  (class loading synchronization, lazy, no volatile needed)
- DI-managed singleton scope is the recommended approach in
  production code: injectable, testable, lifecycle-managed

**Q2: You are reviewing a service that uses a Singleton to
cache database query results. The service is about to be
deployed to a Kubernetes cluster with 5 replicas. What
problems do you foresee and how would you address them?**

*Why they ask:* Tests understanding of Singleton scope
limitations in distributed systems - a critical production
knowledge gap.

*Strong answer includes:*
- 5 pods = 5 independent Singleton instances = 5 independent
  caches; no consistency guarantee between pods
- Staleness risk: database update visible to pod-1's cache
  is invisible to pod-2's cache; requests hitting different
  pods see inconsistent data
- Solution options: remove the Singleton cache entirely (let
  the database handle load), use an external distributed cache
  (Redis) that all pods share, or implement cache invalidation
  via pub/sub (pod receives invalidation event, clears local
  Singleton cache)
- The Singleton must become read-only or store only immutable
  data to be safe in a multi-pod deployment

**Q3: How does Spring's singleton scope differ from the GoF
Singleton pattern? Which would you choose and why?**

*Why they ask:* Tests awareness of modern alternatives to
the classic pattern - the answer reveals whether the candidate
is practicing current engineering standards.

*Strong answer includes:*
- GoF Singleton: private constructor + static getter = global
  access, not injectable, not testable; scope is per ClassLoader
- Spring singleton scope: one instance per ApplicationContext,
  injected via constructor/field injection, replaceable with
  mocks in tests; scope is per Spring container (not per JVM)
- In almost all production Java code: prefer Spring singleton
  scope; the testability and DIP compliance benefits are
  significant
- Only use static GoF Singleton for infrastructure that exists
  before Spring context starts (e.g., the logging framework
  bootstrap, JVM-level shutdown hooks)

