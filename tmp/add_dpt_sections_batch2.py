#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add EVOLUTION, Transferable Wisdom, Surprising Truth, Q3+Hints to DPT-031..DPT-060"""

import re
import os

BASE = r"C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\DPT-design-patterns"

CONTENT = {
    "DPT-031": {
        "evolution": """\
**EVOLUTION:**
Double-Checked Locking was infamously listed as a "broken pattern"
in Java before the Java Memory Model (JMM) was specified in Java 5
(JSR-133, 2004). Pre-Java 5 JVMs could reorder instructions in ways
that exposed partially-constructed objects. The `volatile` keyword
semantics were tightened in Java 5 to prevent this, making DCL safe
specifically when the field is `volatile`. The debate was so
significant that Bill Pugh's "Initialization-on-demand Holder" was
proposed as the canonical thread-safe lazy singleton that avoids
DCL entirely. Modern IDEs flag DCL without `volatile` as a warning.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the fast-path check from the slow-path critical section.
A null check without locking handles 99.9% of cases; the lock only
guards the rare creation path. Pay the synchronisation cost only
when necessary.

**Where else this pattern appears:**
- **CPU branch prediction:** Processors predict common code paths
  (the "not null" fast path) and only stall for mispredictions.
  The principle is identical: optimize for the common case, pay
  cost for the exceptional case.
- **Database optimistic locking:** Read without locking (fast path);
  validate and retry with a lock only on conflict (slow path).
- **ReentrantReadWriteLock:** Multiple concurrent reads (fast path,
  no exclusive lock) vs. single-thread write (slow path, exclusive).
  Read-heavy workloads spend most time in the lock-free path.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Double-Checked Locking was broken in Java for 9 years (1995-2004)
-- every Java textbook that showed DCL before Java 5 showed broken
code. The bug was subtle: the JVM could write the pointer to the
new object before the object's fields were initialised, allowing
Thread B to see a non-null but uninitialised object. This was a
Java Memory Model hole, not a DCL design flaw. When JMM was fixed
in Java 5 with `volatile` semantics, DCL became safe -- but the
pattern's reputation, and the "Bill Pugh Holder" alternative, had
already displaced it in most style guides.""",

        "q3": """\

**Q3 (Design Trade-off):** A team reviews a DCL implementation
and finds the `volatile` keyword was removed "to improve
performance" in a recent refactoring. The JVM is Java 11. The
code works correctly in all tests. Explain: (1) why tests are
insufficient to detect the bug, (2) what CPU architecture the
bug manifests on most reliably, and (3) the correct fix.

*Hint: The How It Works section and Failure Modes cover the
volatile visibility issue. The bug requires two concurrent
threads AND a JVM/CPU that reorders stores -- x86 rarely
reorders, ARM does. That's why it "works in testing."*"""
    },

    "DPT-032": {
        "evolution": """\
**EVOLUTION:**
Producer-Consumer formalised the unbounded buffer queue problem
that emerged as multi-core CPUs became standard (2000s). Java's
`BlockingQueue` (Java 5, 2004) provided a production-ready
implementation. `LinkedTransferQueue` and `SynchronousQueue` added
zero-buffer variants. The reactive streams specification (2015)
extended the pattern with explicit backpressure: the consumer
signals capacity to the producer, preventing unbounded growth.
Kafka's topic model is Producer-Consumer at infrastructure scale --
with persistence, replay, and consumer group coordination built in.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple the rate of production from the rate of consumption
by placing a bounded buffer between them. The buffer absorbs
bursts; the bound enforces backpressure when the consumer
cannot keep up.

**Where else this pattern appears:**
- **Manufacturing assembly lines:** Parts are produced at one
  station and placed in a buffer bin; the next station picks
  from the buffer. Bin capacity is the bound; full bin = producer
  slows down.
- **TCP flow control (receive window):** The TCP receive buffer
  is the bounded queue; the receiver advertises window size
  (backpressure signal) to the sender.
- **Video streaming buffering:** The media player pre-buffers
  several seconds of decoded frames (the buffer); the decoder
  fills it; the renderer consumes it -- the buffer absorbs
  network jitter without visible stutter.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `SynchronousQueue` implements Producer-Consumer with a
buffer of size zero -- there is no buffer at all. Each `put()`
blocks until a thread calls `take()`, and vice versa. This
sounds useless but is ideal for direct handoff: the producer
and consumer must synchronise at every element, ensuring the
consumer is ready before the producer continues. This is used
in `Executors.newCachedThreadPool()` -- submitted tasks are
directly handed to available threads via `SynchronousQueue`.
A zero-buffer queue is the strictest possible form of
backpressure: the producer can never get ahead.""",

        "q3": """\

**Q3 (Design Trade-off):** An image processing pipeline uses
Producer-Consumer: producers add raw images to a queue,
consumers process them. The processing takes 10x longer than
capture. The `ArrayBlockingQueue` has capacity 100. Describe:
(1) what happens when images arrive faster than they can be
processed, (2) at what point data is lost vs. backpressure
applied, (3) whether `LinkedBlockingQueue` is a better choice.

*Hint: The FAILURE PATH section covers queue exhaustion.
The difference between bounded (ArrayBlockingQueue) and
unbounded (LinkedBlockingQueue) queues is a fundamental
production reliability decision.*"""
    },

    "DPT-033": {
        "evolution": """\
**EVOLUTION:**
Thread Pool Pattern became mainstream with Java 5's Executor
framework (2004), which standardised `ExecutorService`,
`ThreadPoolExecutor`, and `ScheduledExecutorService`. Before this,
developers hand-rolled thread pools with varying reliability.
The pattern's relevance is being transformed by Java 21 Virtual
Threads (Project Loom): virtual threads are so lightweight (less
than 1KB overhead vs. ~1MB per platform thread) that one-thread-
per-task becomes viable, potentially making thread pools for I/O-
bound tasks unnecessary. CPU-bound tasks still benefit from pools
sized to the physical core count.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Pre-allocate a fixed set of reusable workers. Distribute work
items to idle workers. When bounded, the pool becomes a natural
rate limiter -- work cannot exceed the pool's capacity of workers.

**Where else this pattern appears:**
- **HTTP server connection handlers (Nginx worker processes):**
  Each `worker_process` in Nginx is a fixed pool member;
  connection requests are distributed across the pool.
- **Database server connection handler threads:** PostgreSQL
  pre-forks a fixed number of backend processes; connection
  requests block when all processes are busy.
- **Operating system interrupt handlers:** Kernel bottom-half
  handlers are pre-allocated kernel threads that process
  deferred interrupt work -- a kernel-level thread pool.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java 21's Virtual Threads do not eliminate the Thread Pool
Pattern for CPU-bound work -- they eliminate it only for I/O-
bound work. A CPU-bound task on a virtual thread still requires
a platform thread to execute; scheduling 10,000 virtual threads
on 8 CPU cores still throttles to 8 simultaneously running tasks.
The confusion arises because "thread" means two different things:
a lightweight concurrency unit (virtual thread) and a CPU execution
slot (platform thread/carrier thread). Thread pools for CPU-bound
work will remain -- they just become pools of carrier threads
rather than application threads.""",

        "q3": """\

**Q3 (Design Trade-off):** A Spring Boot application uses a
`ThreadPoolTaskExecutor` with `corePoolSize=10`,
`maxPoolSize=50`, `queueCapacity=100`. Under a traffic spike:
300 concurrent requests arrive. Trace the exact sequence of
how the task executor handles them, identify when the 301st
request arrives and what happens to it, and explain how
to tune the pool for a service where tasks are 90% I/O wait.

*Hint: The How It Works diagram and the Failure Modes section
on RejectedExecutionException cover this scenario. The 90% I/O
wait ratio means Little's Law applies: optimal pool size is
much larger than CPU count.*"""
    },

    "DPT-034": {
        "evolution": """\
**EVOLUTION:**
Scheduler Pattern was foundational before frameworks abstracted
time-based triggering. Java's `Timer`/`TimerTask` (Java 1.3)
was the first stdlib implementation, but its single-thread model
was fragile. `ScheduledExecutorService` (Java 5) replaced it with
thread-pool-backed scheduling. Spring's `@Scheduled` annotation
(Spring 3.0, 2009) brought declarative scheduling. Distributed
schedulers (Quartz, Spring Batch, Apache Airflow) appeared for
cluster-aware, persistent, and retry-capable scheduling. Kubernetes
`CronJob` extended the pattern to container workloads.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple the task definition from its temporal trigger. Define
what to do independently of when to do it. The scheduler decides
the when; the task focuses on the what.

**Where else this pattern appears:**
- **OS process scheduler (cron):** Unix cron triggers tasks at
  calendar times -- the task script is unaware of when it runs;
  the scheduler reads the crontab and fires the process.
- **Database job schedulers (pg_cron, Oracle DBMS_SCHEDULER):**
  SQL procedures are triggered by the scheduler -- the procedure
  has no clock awareness.
- **Airline revenue management:** Pricing recalculation jobs run
  on scheduled windows -- the pricing algorithm is the task;
  the revenue management platform is the scheduler.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Spring's `@Scheduled` annotation has a silent single-thread
limitation that surprises production teams: by default, all
`@Scheduled` tasks in a Spring application share a single
scheduler thread. If Task A takes 5 minutes and Tasks B and
C are scheduled for every minute, they silently queue behind
A. The fix -- configuring a `ThreadPoolTaskScheduler` with
multiple threads -- requires explicit configuration that many
teams discover only when monitoring shows missed executions.
This "silent throttling by default" behaviour has caused
numerous production issues where scheduled batch jobs
unexpectedly delayed each other.""",

        "q3": """\

**Q3 (Design Trade-off):** Two scheduled jobs conflict:
`DailyReport` runs at 00:00 and takes 45 minutes; `HourlySync`
runs at :00 every hour. `HourlySync` at 01:00 arrives while
`DailyReport` is still running. Describe: (1) the default
Spring behaviour, (2) how to configure thread pool-based
parallel execution, (3) the risks if both jobs write to
the same database table.

*Hint: The Failure Modes and How It Works sections cover
task overlap scenarios. The concurrent execution + shared
state problem is the crux -- this requires both the
scheduler configuration AND a concurrency control strategy.*"""
    },

    "DPT-035": {
        "evolution": """\
**EVOLUTION:**
Read-Write Lock Pattern predates Java -- Dijkstra's semaphore
work (1965) laid the conceptual groundwork. Java's `ReadWriteLock`
interface was introduced in Java 5 (2004) as `ReentrantReadWriteLock`.
Java 8 added `StampedLock` with an "optimistic read" mode --
reads proceed without acquiring any lock and check for concurrent
writes after the fact, improving scalability further. For
distributed systems, this pattern scales to distributed read-write
locks (Redis-based `WATCH`/`MULTI` transactions, ZooKeeper
distributed locks) used in cluster coordination.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Distinguish reads from writes and apply different concurrency
policies. Reads are non-destructive and can proceed concurrently;
writes are destructive and require exclusive access. Unlock the
concurrency potential of read-heavy workloads.

**Where else this pattern appears:**
- **Database MVCC (Multi-Version Concurrency Control):** Readers
  see a consistent snapshot without blocking writers; writers
  create new versions -- reads and writes proceed concurrently
  by never operating on the same version simultaneously.
- **Git branching model:** Multiple developers read (clone) the
  repository simultaneously; write operations (push) go through
  conflict detection. The remote is "read-many, write-serialised."
- **CDN read replicas:** Multiple read replicas serve read traffic
  concurrently; the primary handles writes and replicates changes.
  The replication lag is the R/W lock's consistency trade-off.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `ReentrantReadWriteLock` can actually be *slower* than
a plain `synchronized` block in read-heavy workloads on some
JVMs and hardware. The reason: the R/W lock has higher overhead
per operation than `synchronized` (it must track reader count,
waiting writers, and upgrade state). On low-contention workloads,
the overhead dominates the benefit. The pattern pays off only
when: (a) reads significantly outnumber writes, AND (b)
read operations are long enough that concurrent reads provide
measurable throughput gain. Benchmarking is required -- the
"obvious win" frequently isn't.""",

        "q3": """\

**Q3 (Design Trade-off):** A `ConfigurationCache` is read
10,000 times/second and updated once every 30 seconds. A
`StampedLock` with optimistic reads is proposed. Describe
the optimistic read protocol step by step, explain what
happens when a write occurs during an optimistic read,
and state when the optimistic read approach becomes worse
than a plain `ReadWriteLock`.

*Hint: The How It Works section covers optimistic read stamp
validation. The key scenario is: what percentage of reads
must retry due to concurrent writes before the retry overhead
exceeds the non-locking benefit?*"""
    },

    "DPT-036": {
        "evolution": """\
**EVOLUTION:**
Active Object was developed in the context of real-time and
distributed systems (Douglas C. Schmidt, 1996) to decouple method
invocation from execution in concurrent systems. Java 5's
`CompletableFuture` and `ExecutorService` made the pattern's
mechanics available without explicit implementation. Akka's Actor
model is a high-level Active Object variant where each actor is
an independent concurrent entity processing messages from its
mailbox. Java 21 Virtual Threads and structured concurrency
(`StructuredTaskScope`) provide new primitives that implement
Active Object semantics with less boilerplate.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the interface for requesting work (synchronous call)
from the execution of that work (asynchronous, potentially on
a different thread). Return a Future immediately; let the work
proceed on its own execution context.

**Where else this pattern appears:**
- **Akka Actors:** Each actor processes one message at a time
  from its mailbox -- the Active Object's proxy becomes the
  ActorRef; the dispatch queue becomes the actor mailbox.
- **JavaScript event loop (Promise):** `async function()` returns
  a Promise (the Future); the function body executes on the
  event loop without blocking the caller.
- **gRPC Server streaming:** The server returns a stream handle
  immediately; individual response messages are pushed
  asynchronously as they are ready.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Akka Actor system, which handles millions of messages per
second in production at companies like Twitter and LinkedIn,
is fundamentally the Active Object pattern scaled to a
distributed runtime. Each actor is an Active Object: it has
a mailbox (dispatch queue), processes one message at a time
(scheduler), and exposes a reference (proxy) through which
callers interact. The pattern that was described in a 1996
academic paper as a concurrency pattern for single-process
systems became the foundation for one of the most scalable
distributed computing frameworks in the JVM ecosystem.""",

        "q3": """\

**Q3 (Design Trade-off):** An `OrderProcessor` Active Object
has 10,000 messages queued when the server runs out of memory.
The dispatcher is processing messages but the queue is growing
faster than it is drained. Describe: (1) what fail-safe the
Active Object pattern provides by default (none, bounded, or
unbounded?), (2) how to add backpressure, (3) where in the
pattern to add circuit-breaker logic if the downstream service
that processes orders is unavailable.

*Hint: The Failure Modes section and the comparison to Kafka
are directly relevant. The activation queue is the buffer --
its bound and overflow strategy determines the system's
resilience profile.*"""
    },

    "DPT-037": {
        "evolution": """\
**EVOLUTION:**
Event Bus Pattern codified in-process event routing that had been
implemented informally in GUI frameworks for decades. Guava's
`EventBus` (2012) made it a first-class library component in Java.
Spring's `ApplicationEventPublisher` (Spring 3.0) embedded it in
the DI framework. As microservices emerged, the in-process Event
Bus scaled to distributed message brokers (Kafka, RabbitMQ, AWS
EventBridge), with persistence, replay, and cross-process routing.
Modern Event-Driven Architecture (EDA) is essentially Event Bus at
infrastructure scale -- the broker IS the bus.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Decouple event producers from event consumers by routing events
through a central bus. Publishers fire events without knowing
who handles them; subscribers register interest without knowing
who publishes.

**Where else this pattern appears:**
- **OS kernel event system (inotify, epoll):** Applications
  register for file system events via inotify; the kernel
  publishes events when files change -- a kernel-level event bus.
- **AWS EventBridge:** Publishes events from AWS services (S3,
  DynamoDB, Lambda) and routes to subscribers by rule -- a
  managed cloud event bus.
- **Redux/Vuex store:** Actions are events published to the store
  (bus); reducers are subscribers that transform state in response
  -- the store is an in-memory event bus with history.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Guava's `EventBus` was designed as a migration path from the
Observer + listener registration boilerplate in Java, not as
a production message bus. Its author, Cliff Click, explicitly
documented that `EventBus` is not thread-safe by default -- the
synchronous variant fires all handlers in the publishing thread,
and if any handler throws, subsequent handlers never receive the
event (silent data loss). The production-ready asynchronous
variant wraps an `Executor` but still has no persistence, replay,
or delivery guarantee. Teams that use Guava `EventBus` as a
substitute for a message broker typically discover these gaps
during their first production incident.""",

        "q3": """\

**Q3 (Design Trade-off):** A Spring application uses
`ApplicationEventPublisher` to fire `OrderCreatedEvent`.
Three listeners process the event: inventory reservation,
notification email, and analytics update. If the email
listener throws an exception, describe what happens to the
inventory and analytics listeners and how to ensure all
three are always attempted, including after application
restart and listener failure.

*Hint: The Failure Modes section covers partial failure.
The solution involves either transactional event publishing
(Outbox pattern DPT-053) or independent retry queues for
each subscriber.*"""
    },

    "DPT-038": {
        "evolution": """\
**EVOLUTION:**
Service Locator was the dominant dependency management pattern
before IoC containers matured (circa 1998-2004). Rod Johnson's
"Expert One-on-One J2EE Design and Development" (2002) and
Martin Fowler's "Inversion of Control Containers and the
Dependency Injection Pattern" (2004) systematically argued that
DI was superior to Service Locator for testability and explicit
dependencies. Spring popularised constructor injection (2003-2005),
effectively retiring Service Locator as a primary pattern. It
survives in OSGi container contexts and legacy code bases where
refactoring to DI is impractical.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Centralise service registration and lookup in one registry.
This removes the creation knowledge from callers -- callers
ask for a service by name or type rather than calling `new`.

**Where else this pattern appears:**
- **JNDI (Java Naming and Directory Interface):** Application
  servers publish DataSources, EJBs, and JMS queues to JNDI;
  clients look them up by name string. JNDI is Service Locator
  at Java EE scale.
- **DNS:** DNS is a global Service Locator for network services --
  clients ask "where is service X?" by name; DNS returns the
  address. Service Locator's failure mode (hidden dependency) is
  also DNS's: remove a record, everything silently breaks.
- **OSGi service registry:** Components publish services to the
  OSGi service registry; consumers look them up dynamically --
  a type-safe Service Locator for modular Java applications.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Martin Fowler did not declare Service Locator an anti-pattern in
his 2004 article -- he said it was "less preferred" than DI. The
conflation of "less preferred" with "anti-pattern" led to its
wholesale removal from codebases that could have reasonably used
it. Service Locator remains the correct pattern in specific
contexts: plugin architectures where dependencies are not known
at compile time, OSGi bundles with dynamic service binding, and
test harnesses that need to replace services without DI framework
support. The pattern is a legitimate tool; its overuse as a
substitute for DI is the actual anti-pattern.""",

        "q3": """\

**Q3 (Design Trade-off):** An OSGi-based plugin system uses
Service Locator: plugins register services on startup;
the host application looks them up by interface type. A new
requirement: multiple implementations of the same service
type must coexist (e.g., two `PaymentGateway` implementations).
Describe the Service Locator API changes needed to support
this and compare this with how Spring's `@Autowired List<T>`
handles the same scenario.

*Hint: The Comparison Table's Service Locator vs DI row is
the relevant starting point. Consider qualifier-based
selection vs. collection injection as the two models.*"""
    },

    "DPT-039": {
        "evolution": """\
**EVOLUTION:**
Dependency Injection as a named pattern emerged from Martin
Fowler's 2004 article formalising what Spring Framework (Rod
Johnson, 2002) had demonstrated in code. Spring popularised
constructor injection; later field injection (`@Autowired`)
became common despite being less testable. Spring Boot (2013)
added auto-configuration, creating zero-XML DI. Jakarta EE
standardised DI with CDI (Contexts and Dependency Injection,
2009). Micronaut and Quarkus (2018-2019) moved DI processing
to compile time, eliminating reflection overhead. Java 21 records
and sealed classes enable lightweight manual DI without a container.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
An object should not be responsible for acquiring its own
dependencies. Dependencies should be provided by an external
caller or container. This externalises the "who provides what"
decision, making it observable, changeable, and testable.

**Where else this pattern appears:**
- **Restaurant supply chain:** A chef does not source their own
  ingredients -- the restaurant manager (the container) provides
  standardised supplies. The chef (the component) specifies what
  it needs; the manager provides it.
- **Unix process environment variables:** A process declares
  what environment variables it reads; the OS (container) injects
  the values at process start. No hard-coded paths in the binary.
- **Kubernetes ConfigMap/Secret injection:** Pods declare named
  environment variables or volume mounts; Kubernetes injects the
  values from ConfigMaps and Secrets at pod start.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Field injection with `@Autowired` -- by far the most common DI
style in Spring applications -- is actively discouraged by the
Spring team itself. The Spring documentation states: "Always use
constructor injection in your beans." Field injection makes
dependencies invisible in the public API, allows object creation
without all dependencies present (a partially-constructed bean),
and makes unit testing without a Spring context impossible without
reflection-based hacks. The pattern that made Spring famous also
has a widely-used anti-pattern variant that the framework's own
authors warn against on every page of their documentation.""",

        "q3": """\

**Q3 (Design Trade-off):** A `PaymentService` uses constructor
injection for `PaymentGateway`, `FraudDetector`, and
`AuditLogger`. A new requirement: `PaymentService` should also
optionally use a `CurrencyConverter`, but not all deployments
have one available. Design the injection model for the optional
dependency and compare: (a) nullable constructor parameter,
(b) `Optional<CurrencyConverter>` constructor parameter,
(c) `@Autowired(required=false)` field injection.

*Hint: The First Principles CORE INVARIANTS say dependencies
should be declared, not discovered. Each option makes the
optional dependency more or less explicit -- map to testability
and clarity in the code review.*"""
    },

    "DPT-040": {
        "evolution": """\
**EVOLUTION:**
Specification Pattern was formalised by Eric Evans and Martin
Fowler (1997) as part of Domain-Driven Design vocabulary.
Java's `Predicate<T>` interface (Java 8) is a single-method
Specification -- `and()`, `or()`, and `negate()` provide
the composition operators. JPA Specification (Spring Data)
extended the pattern to database queries: `Specification<T>`
composes into a JPA `CriteriaQuery`. The pattern gained
popularity in DDD-influenced codebases where business rules
must be composable, testable, and expressible in domain language.
QueryDSL and jOOQ provide specification-like composable query APIs.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Encapsulate a business rule as a named, composable predicate.
Business rules become first-class objects: testable in isolation,
combinable into complex rules, and readable in domain language.

**Where else this pattern appears:**
- **Search engine query syntax:** Boolean operators AND, OR,
  NOT in search queries compose specification objects at the
  query language level -- `Specification` semantics in the
  search engine's query parser.
- **Firewall rules (iptables):** Each firewall rule is a
  specification (port=80 AND protocol=TCP AND source=192.168.x.x);
  chains compose rules into ordered policies.
- **Database query predicates (WHERE clauses):** SQL's `WHERE
  age > 18 AND (country = 'US' OR premium = true)` is a
  composed specification -- each predicate is a Specification
  unit; AND/OR are the composition operators.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Java's `Predicate<T>` interface, used millions of times daily
in stream operations, is a stripped-down Specification pattern.
`predicate.and(otherPredicate)` is Specification composition;
`predicate.negate()` is NOT; `predicate.or(other)` is OR.
The only difference from the full Specification pattern is
that `Predicate<T>` lacks meaningful naming (a predicate
is anonymous unless you assign it to a named variable).
When a team writes `Predicate<User> isPremium = u ->
u.hasPremiumSubscription()` and composes it, they are
implementing the Specification pattern -- just with Java's
built-in functional interface rather than an explicit class.""",

        "q3": """\

**Q3 (Design Trade-off):** A Spring Data application uses
`Specification<Product>` to build dynamic search queries.
A requirement says: specifications must be cached by their
composition key so that identical queries reuse the cached
JPA Criteria object. Design the caching strategy and describe
the equality/hashCode requirements for Specification objects
to make caching reliable.

*Hint: The Failure Modes section addresses specification
testability. The caching problem requires Specification objects
to correctly implement value equality -- which lambdas do NOT
provide by default. This is the key obstacle to cache-based
Specification reuse.*"""
    },

    "DPT-041": {
        "evolution": """\
**EVOLUTION:**
The confusion between Decorator, Proxy, and Adapter persisted
through the GoF era partly because all three use the "wrap an
object" technique. As Java frameworks matured, each pattern
found its canonical home: Proxy in Spring AOP (bytecode-generated
proxies), Decorator in I/O streams and validation pipelines,
Adapter in JDBC driver layers and legacy integrations. The
confusion was further reduced by naming conventions: Spring
classes with "Proxy" or "Interceptor" are Proxies; those with
"Wrapper" or "Decorator" are Decorators; those with "Adapter"
or "Bridge" are Adapters. Java records (Java 16+) and sealed
classes make adapter and decorator patterns detectable at the
type level through implements/extends analysis.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Three patterns use the same object-wrapping structure but
serve distinct purposes. The intent determines which pattern
applies -- not the implementation. When choosing between them,
start with intent: am I changing an interface (Adapter),
adding behaviour (Decorator), or controlling access (Proxy)?

**Where else this pattern appears:**
- **Network proxies, VPNs, CDNs:** All are Proxy -- they forward
  to the same ultimate destination, with added access control
  (VPN) or caching (CDN).
- **Data format converters (CSV->JSON):** Adapter -- aligns
  incompatible data formats; the content is the same, the
  representation is translated.
- **Middleware pipelines (Express.js, Spring filters):** Decorator
  -- each middleware adds a layer of behaviour to the request
  handling; the ultimate handler is reached at the bottom.""",

        "surprise": """\
---

### 💡 The Surprising Truth

All three patterns (Decorator, Proxy, Adapter) are structurally
identical in many static analysis tools -- they all show as "a
class holding a reference to another class of the same type."
This means automated pattern detection tools frequently
misclassify them. The only reliable differentiator is **intent**:
the question to ask is "what would break if I removed this wrapper?"
If the client would fail to call the wrapped object (Adapter),
if the wrapped object would lose added behaviour (Decorator),
or if access policy would be bypassed (Proxy), you have your
answer. Pattern identity is semantic, not structural.""",

        "q3": """\

**Q3 (Design Trade-off):** A code review finds a class
`LoggingPaymentGateway implements PaymentGateway` that wraps
another `PaymentGateway`, logs every `charge()` call, and
also converts between the internal `Money` type and the
gateway's `BigDecimal` type. Classify this as Decorator,
Adapter, Proxy, or a combination of patterns, and recommend
whether these concerns should be in one class or separated.

*Hint: The Comparison Table in this entry maps intent to
each pattern. Two separate responsibilities (logging = Decorator;
type conversion = Adapter) in one class violates Single
Responsibility -- recommend separation.*"""
    },

    "DPT-042": {
        "evolution": """\
**EVOLUTION:**
Anti-patterns as a named concept were popularised by Andrew Koenig
(1995) and comprehensively catalogued by Brown, Malveau, McCormick,
and Mowbray in "AntiPatterns: Refactoring Software, Architectures,
and Projects in Crisis" (1998). The domain expanded from OOP
anti-patterns to distributed systems anti-patterns (distributed
monolith, chatty service), cloud anti-patterns (pet servers,
snowflake servers), and data anti-patterns (God Table, EAV model
abuse). Modern engineering retrospective practices treat anti-
pattern recognition as a core team skill -- post-mortems frequently
identify anti-patterns as root causes.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Named solutions to named problems (patterns) have equal value
when applied to named anti-solutions: naming the bad thing
enables recognition, communication, and systematic avoidance.
Vocabulary for failure is as important as vocabulary for success.

**Where else this pattern appears:**
- **Medicine (disease classification):** Naming a disease pattern
  (diabetes, hypertension) enables diagnosis, treatment protocols,
  and prevention research -- unnamed conditions cannot be treated
  systematically.
- **Aviation safety (accident patterns):** NTSB categorises
  accident causes ("controlled flight into terrain", "runway
  incursion") -- named patterns enable targeted training and
  checklist development.
- **Finance (market bubble identification):** Named market phases
  (irrational exuberance, dead cat bounce) provide vocabulary
  for risk management that vague descriptions cannot.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The term "anti-pattern" was coined by Andrew Koenig in a 1995
article referencing the GoF "Design Patterns" book, but the concept
was in widespread use under different names for decades before.
"Code smell" (Martin Fowler, 1999) describes individual lines;
"anti-pattern" describes recurring structural failures in systems.
The most striking anti-patterns -- God Object, Spaghetti Code,
Golden Hammer -- were already being discussed in software engineering
papers in the 1970s and 1980s without the "anti-pattern" label.
The GoF and Koenig gave us vocabulary, not discovery: the problems
existed since the first multi-kloc software systems.""",

        "q3": """\

**Q3 (Design Trade-off):** A team's retrospective identifies
that their codebase exhibits three anti-patterns: God Object
(one 5,000-line service class), Spaghetti Code (circular
dependencies), and Golden Hammer (Kafka used for all component
communication including synchronous request-response calls).
Prioritise which anti-pattern to address first and describe
the decision criteria for prioritisation.

*Hint: The Failure Modes section suggests impact-based
prioritisation. Consider which anti-pattern has the broadest
blast radius (prevents new features vs. causes bugs),
and which is most reversible.*"""
    },

    "DPT-043": {
        "evolution": """\
**EVOLUTION:**
God Object (also called "Blob" in the Brown et al. AntiPatterns
book) has been a recognised failure mode since the first large
object-oriented codebases appeared in the late 1980s. The pattern
persists for a consistent reason: it emerges from the path of
least resistance -- adding to an existing class is always faster
than designing a new abstraction. Microservices architecture
introduced the distributed equivalent: the "God Service" or
"Blob Service" that handles too many business capabilities.
Domain-Driven Design (DDD), with its Bounded Contexts and
Aggregate design, provides the most rigorous antidote to God
Objects at both process and class level.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
A cohesive unit -- class, service, or module -- should have
one reason to change. When something has many reasons to change,
it is doing too much. Decompose by responsibility until each
unit changes for only one reason.

**Where else this pattern appears:**
- **God services in microservices:** A "user service" that
  handles authentication, profile management, preferences,
  social graph, notifications, and analytics -- split by
  bounded context (Authentication, Profile, Social, Analytics).
- **God database tables:** A single `users` table with 80
  columns spanning multiple domains -- should be multiple
  tables per bounded table context.
- **God configuration files:** A single `application.yaml` with
  1,000+ lines covering all environments and all services --
  should be split by environment, service, and concern.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The God Object anti-pattern is often indistinguishable from a
well-designed Facade pattern to a developer who joins a codebase
after the fact. Both are large classes that coordinate many
operations. The critical diagnostic question: "Does this class
coordinate communication between existing objects (Facade), or
does it own the logic that should belong to other objects (God
Object)?" A Facade delegates; a God Object absorbs. God Objects
almost always grow from Facades that crossed the line from
"coordination" to "implementation" -- typically because the
surrounding objects were too anemic to own their own behaviour.""",

        "q3": """\

**Q3 (Design Trade-off):** A `UserService` has evolved into
a 4,000-line God Object. A team plans to decompose it into
`AuthService`, `ProfileService`, and `NotificationService`.
The `UserService` has 200 callers. Describe the migration
strategy that allows incremental decomposition without
breaking existing callers, and map the strategy to a specific
design pattern from the DPT category.

*Hint: The Strangler Fig pattern (DPT-055) is exactly the
refactoring strategy for this scenario. Plan the decomposition
in phases where the old God Object acts as a facade during
the migration.*"""
    },

    "DPT-044": {
        "evolution": """\
**EVOLUTION:**
Spaghetti Code was one of the first named anti-patterns,
predating the GoF book -- Edsger Dijkstra's "Go To Statement
Considered Harmful" (1968) was essentially an argument against
the structural precursor to Spaghetti Code. Structured programming
(Dijkstra, Wirth) was the direct response. In OOP era, Spaghetti
Code evolved into "Ball of Mud" (Brian Foote and Joseph Yoder,
1999) -- a system without any discernible architecture.
Modern interpretations include: circular dependency graphs in
module systems, callback hell (and the Promise/async-await
solution), and highly-coupled microservices that form a
"distributed ball of mud".""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Structure imposes limits on the paths data and control can
take. When structure is absent, every component can depend
on every other component -- the system becomes unmaintainable
because change has unlimited blast radius.

**Where else this pattern appears:**
- **Legacy database schemas with circular foreign keys:**
  Table A references B, B references C, C references A --
  no defined dependency direction means schema migrations
  require disabling all constraints simultaneously.
- **CSS specificity wars:** Global class names override each
  other in unpredictable order -- "spaghetti styles" where
  changing one class breaks three others unpredictably.
- **Microservices circular dependencies:** Service A calls B,
  B calls C, C calls A synchronously -- a distributed deadlock
  waiting to happen.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Dijkstra's "Go To Statement Considered Harmful" (1968) is the
most-cited computer science letter ever, but few know it was
rejected by the ACM Communications editors on first submission.
Dijkstra sent it directly to the editor-in-chief, Niklaus Wirth,
who published it with the word "letter" in the title because the
editors thought it was too polemical for a formal paper. The
structured programming revolution it triggered -- which eliminated
most Spaghetti Code from modern practice -- started from a 3-page
letter that was nearly rejected. The entire OOP era's resistance
to `goto` and support for structured control flow traces back to
this almost-unpublished "letter."'""",

        "q3": """\

**Q3 (Design Trade-off):** A team discovers a circular import
chain in their Python microservice: `orders.py` imports from
`payments.py`, which imports from `users.py`, which imports
from `orders.py`. The code works at runtime due to delayed
evaluation but fails during import under some conditions.
Map this to the Spaghetti Code anti-pattern and describe
two structural approaches to break the cycle.

*Hint: The Failure Modes section covers circular dependency
detection. The two approaches are dependency inversion
(introduce an interface/event) and module boundary
restructuring (move the shared logic to a new module).*"""
    },

    "DPT-045": {
        "evolution": """\
**EVOLUTION:**
Golden Hammer was catalogued in the AntiPatterns book (1998) as
"Familiar Technology." The pattern cycles with each new technology
wave: in the 2000s it was J2EE/EJB for everything; in the 2010s,
NoSQL for everything, then microservices for everything, then
Kubernetes for everything; in the 2020s, LLMs for everything.
Each wave produces its own Golden Hammer incidents: teams adding
Kubernetes to two-service applications, using MongoDB for
relational data, or adding LLM calls to problems solvable with
`if-else`. The antidote remains unchanged: requirements before
tools, fit-for-purpose selection, and comfort with using different
tools for different problems.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Select tools based on problem requirements, not familiarity.
Expertise in a tool is valuable; applying it beyond its
problem domain is wasteful and risky. Maintain a repertoire
of different tools for different problem classes.

**Where else this pattern appears:**
- **Medical overdiagnosis:** A specialist who sees every problem
  through their specialty's lens (a surgeon who recommends surgery,
  a radiologist who recommends imaging) -- the Golden Hammer is
  the specialist's primary intervention.
- **Marketing always predicting viral growth:** Marketing teams
  trained in viral/social campaigns apply the same playbook to
  B2B enterprise software -- the wrong tool for the wrong audience.
- **Infrastructure teams defaulting to VMs:** Before containers,
  every deployment was a VM -- containers, serverless, and PaaS
  were resisted because "we know VMs."'""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Kubernetes Golden Hammer is the most documented recent
instance of this anti-pattern. CNCF survey data shows that
teams running 1-3 microservices deploy to Kubernetes in
significant numbers -- adding 30,000+ lines of K8s configuration
to systems that would run correctly in a single Docker Compose
file or a simple PaaS deployment. The operational complexity
of Kubernetes (certificate management, networking, autoscaling,
secret management) exceeds the benefit for small deployments.
The anti-pattern's motivation is honest: teams want to learn
production-grade tools. The mistake is using production users
as the learning environment.""",

        "q3": """\

**Q3 (Design Trade-off):** A 3-person startup uses Kubernetes
with Istio service mesh to deploy 2 microservices and a
database. The CTO argues "we'll need it when we scale."
Apply the YAGNI principle to evaluate this architecture
decision, and describe the concrete engineering cost being
paid now for unvalidated future requirements.

*Hint: The Failure Modes section covers premature optimisation
as a related failure. Quantify: Kubernetes requires 3+ nodes
for HA, a full DevOps pipeline, and significant operational
expertise. Map these costs to the team's actual current
requirements.*"""
    },

    "DPT-046": {
        "evolution": """\
**EVOLUTION:**
Cargo Cult Programming was named by Richard Feynman in his 1974
Caltech commencement address, though software practitioners
applied the term to programming practices informally for decades
before it appeared in software engineering literature. The pattern
intensified with Stack Overflow (2008) -- copy-paste without
understanding became mechanically easier. AI code generation
(GitHub Copilot, ChatGPT, 2021-2023) created a new cargo cult
risk: LLM-generated code copied without verifying correctness,
security, or applicability. The antidote evolved: shift from
"accept the suggestion" to "understand the suggestion."'""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Replicate solutions only after understanding the problem they
solve. The form without the function is cargo. Understand
the context, constraints, and forces before applying a
solution from elsewhere.

**Where else this pattern appears:**
- **Financial cargo culting:** Copying trading strategies from
  publications without understanding their underlying signal --
  the signal decays as more participants use it; cargo culters
  get the form (trade at 9:30 AM) without the function (arbitrage
  opportunity that no longer exists).
- **Business process cargo culting:** Adopting the "daily standup"
  format from Agile without understanding its information-sharing
  purpose -- standups become status reports to managers instead
  of team self-organisation tools.
- **Scientific cargo culting:** Running clinical trials that
  mimic the form (double-blind, control group) without the
  function (statistical power, correct primary endpoints).""",

        "surprise": """\
---

### 💡 The Surprising Truth

Richard Feynman's Cargo Cult Science speech (1974) was about
psychology research fraud -- not software at all. He described
scientists who ran the rituals of science (controlled experiments,
statistics, publication) without the substance (honest reporting
of negative results, testing alternative hypotheses). The speech
had zero impact on software engineering for 20 years. The
application of "cargo cult" to programming practices -- where
developers follow the form of good practices (having tests,
using design patterns, doing code review) without the substance
(tests that verify behaviour, patterns applied to real
problems, reviews that catch real issues) -- emerged from the
Agile and XP communities in the early 2000s as self-criticism.""",

        "q3": """\

**Q3 (Design Trade-off):** A team adopts CQRS because "it's
what Netflix uses." Their application has 50 users, one
database, and simple CRUD operations. Apply the Cargo Cult
framework to evaluate this decision: identify the "ritual"
being copied, the "substance" CQRS provides Netflix, and
the conditions under which the substance applies to this team.

*Hint: The Failure Modes section and the Golden Hammer entry
(DPT-045) together provide the diagnostic framework. CQRS
solves read/write scalability divergence -- quantify whether
this team has that problem.*"""
    },

    "DPT-047": {
        "evolution": """\
**EVOLUTION:**
Premature Optimization was named by Donald Knuth in "Structured
Programming with go to Statements" (1974): "premature
optimization is the root of all evil." The full quote includes
the frequently-omitted context: "We should forget about small
efficiencies, say about 97% of the time: premature optimization
is the root of all evil. Yet we should not pass up our
opportunities in that critical 3%." Modern JIT compilers
(HotSpot, V8) made micro-optimisations often unnecessary -- the
JIT optimises hot paths at runtime better than a human can
statically. The anti-pattern now more commonly manifests as
premature architectural optimisation: adding caching, sharding,
or async before the bottleneck is measured.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Measure first, then optimise. The critical 3% of code where
optimisation matters cannot be identified by intuition -- only
by profiling under production-representative load. Optimise
only what is measured to be slow.

**Where else this pattern appears:**
- **Infrastructure over-provisioning:** Adding auto-scaling
  before load testing shows whether the application can handle
  single-instance load -- optimising deployment before measuring
  single-node performance.
- **Database indexing all columns:** Adding indexes "just in case"
  -- each index slows writes. The correct approach: identify slow
  queries from production metrics, then add targeted indexes.
- **Supply chain over-buffering:** Holding 6 months of inventory
  "to be safe" before knowing actual demand patterns -- a cargo
  in transit optimisation before demand is understood.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The complete Knuth quote is almost never cited in full, leading
to widespread misapplication. Knuth wrote: "We should forget
about small efficiencies, say about 97% of the time: premature
optimization is the root of all evil. Yet we should not pass up
our opportunities in that critical 3%." The missing "critical 3%"
clause means Knuth was arguing FOR aggressive optimisation of the
measured bottleneck, not against optimisation in general. Teams
that cite "Knuth" to justify never profiling or never optimising
performance-critical paths have inverted his message. The anti-
pattern Knuth described was optimising the non-critical 97%;
the failure is not measuring to find the critical 3%.""",

        "q3": """\

**Q3 (Design Trade-off):** A senior engineer proposes adding
Redis caching to a user profile endpoint "because it will scale
better." The endpoint is called 100 times/day. Average response
time: 50ms (database query). The engineer estimates cache would
reduce this to 5ms. Evaluate this using Knuth's framework
and Amdahl's Law, and state the threshold at which this
optimisation becomes justified.

*Hint: Calculate the actual time saved per day (100 calls x
45ms saving = 4.5 seconds/day) and compare to the engineering
cost of adding, managing, and debugging the cache. Apply
Amdahl's Law to the endpoint's proportion of total system load.*"""
    },

    "DPT-048": {
        "evolution": """\
**EVOLUTION:**
Magic Numbers were identified as a code smell in the earliest
structured programming literature. Symbolic constants (`#define`,
`final static`) were the first remediation. With OOP, constants
moved to classes and interfaces. Java enums (Java 5) provided
type-safe named values that replaced integer/string magic
constants entirely. Code analysis tools (PMD, SonarQube) added
automated detection for numeric literals in code. Modern linting
rules enforce zero magic numbers in production code. The pattern
remains in databases (magic integer codes in lookup tables,
status fields with undocumented values) as a persistent
data-model anti-pattern.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every value with domain meaning belongs in a named constant.
Names communicate intent; raw values communicate nothing.
The cost of a constant declaration is negligible; the cost
of understanding undocumented values is recurring.

**Where else this pattern appears:**
- **Database status codes (magic integers):** `status = 3` in
  the `orders` table meaning "shipped" -- the name is in a
  spreadsheet in the DBA's email, not in the code.
- **HTTP status codes:** HTTP status codes themselves are named
  (200 OK, 404 Not Found, 500 Internal Server Error) -- the
  numbers are standardised magic numbers that the HTTP
  specification named to prevent ambiguity.
- **Network protocol packet types:** Binary protocol fields
  with type codes 0x01, 0x02, 0x03 meaning different message
  types -- magic numbers at the wire format level.""",

        "surprise": """\
---

### 💡 The Surprising Truth

HTTP status codes are the world's most widely-used standard
magic numbers -- and they are extensively documented precisely
because the alternative (remembering raw numbers) is error-prone.
RFC 9110 (HTTP Semantics) dedicates significant text to defining
what each status code means, effectively building a global
"constant registry" because there is no other mechanism to
prevent different endpoints from interpreting the same number
differently. The RFC is proof that even globally standardised
numbers require names: `200` became `HTTP_OK` in every HTTP
client library because `200` alone communicates nothing to
a reader who hasn't memorised the RFC.""",

        "q3": """\

**Q3 (Design Trade-off):** A database table `orders` has a
`status` column with values 1, 2, 3, 4, 5 stored as integers.
The enum mapping exists in a Java `OrderStatus` enum but not
in the database. A new analytics team queries the database
directly and encounters the magic integers. Describe the
tradeoff between (a) adding database-level CHECK constraints
with named values vs. (b) adding a lookup table vs. (c) adding
database comments per value.

*Hint: This is a data-layer magic numbers problem. The Failure
Modes section covers documentation drift -- each approach
has different blast radius when the mapping changes.*"""
    },

    "DPT-049": {
        "evolution": """\
**EVOLUTION:**
Lava Flow was catalogued as a "Dead Code" anti-pattern in 1998.
Modern static analysis tools (SonarQube, FindBugs, IntelliJ
inspections) can detect unreachable code and unused methods
automatically -- reducing but not eliminating the anti-pattern.
It persists for code that is technically reachable but contextually
dead (never called in production paths), for business logic that
was overridden by newer code, and in database tables/columns that
were never cleaned up. Technical debt tools (SonarQube Tech Debt
report) model Lava Flow as a category ("dead code") and quantify
remediation time.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Delete dead code immediately. Code-as-documentation is valuable
only when the code is alive. Dead code misdirects future
developers and imposes the same maintenance cost as live code
without providing any value.

**Where else this pattern appears:**
- **Database orphaned columns:** Columns added for a feature
  that was never deployed remain in the schema indefinitely --
  every migration must account for them; every ORM model must
  map them; every data analyst must understand they're empty.
- **Feature flags never cleaned up:** Feature flags for
  experiments that ended months ago remain in the codebase,
  branching every affected code path -- Lava Flow at the
  control-flow level.
- **Terraform resources for deleted cloud infrastructure:**
  Terraform state files referencing manually-deleted resources
  remain until explicitly removed -- dead infrastructure code.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The "delete dead code" principle conflicts with a common legal
requirement in regulated industries: financial services and
healthcare regulations often require that code changes are
auditable for a minimum retention period. This means "dead code"
cannot always be deleted -- it must be commented with the date
it was retired and the regulatory reason it was retained.
In these contexts, Lava Flow is not always an anti-pattern;
it is a compliance artefact. The practical consequence: standard
Lava Flow remediation advice ("delete it") must be qualified
to "archive or annotate it per your regulatory requirements"
in regulated environments.""",

        "q3": """\

**Q3 (Design Trade-off):** A codebase has 15,000 lines of
code behind a feature flag `LEGACY_PAYMENT_PROCESSOR=false`
that has been false in all environments for 18 months.
The legacy processor handled one edge case for a payment
provider that was decommissioned. Design the removal process:
what verification is needed before deletion, how to handle
git history, and how to ensure the removed capability is not
silently needed by a downstream system.

*Hint: The Failure Modes section discusses removal risks.
The key steps are: trace all references, verify no external
systems call the dead path, and confirm the decommissioned
vendor is truly gone before deleting.*"""
    },

    "DPT-050": {
        "evolution": """\
**EVOLUTION:**
Copy-Paste Programming was identified as a code smell in the first
code review culture literature (1970s-1980s). Ward Cunningham's
Wiki (1994) popularised "DRY" (Don't Repeat Yourself) as its
antidote. Martin Fowler's "Refactoring" (1999) catalogued
"Duplicate Code" as the first code smell to address. Modern IDE
tooling (IntelliJ's "Extract Method/Class" refactoring,
SonarQube's duplication scanner) automated detection and
refactoring. AI code generation (Copilot, 2021) created a new
variant: LLM-generated boilerplate that is structurally similar
across files, harder to detect as intentional vs. accidental
duplication.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every piece of knowledge in a system should have a single,
authoritative representation. Duplication of knowledge --
not just code -- is the root of the problem. When knowledge
changes, duplication requires updating every copy.

**Where else this pattern appears:**
- **Database schema duplication:** The same table structure
  copied to multiple schemas for different tenants -- schema
  migrations must be applied to every copy simultaneously.
- **Configuration file duplication:** The same connection string
  in dev, staging, and prod config files -- updating the string
  requires changing all three; missing one causes environment
  discrepancies.
- **Documentation out of sync with code:** API documentation
  copied from the code and manually maintained -- diverges from
  the actual implementation because the two have no shared
  authoritative source.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The DRY principle (Don't Repeat Yourself) from "The Pragmatic
Programmer" (Hunt and Thomas, 1999) is specifically about
knowledge duplication, not code duplication. The full definition:
"Every piece of knowledge must have a single, unambiguous,
authoritative representation within a system." Hunt and Thomas
distinguished code duplication (sometimes acceptable) from
knowledge duplication (always harmful). Teams that aggressively
DRY-deduplicate every similar-looking code block sometimes create
the opposite problem: highly coupled abstractions where unrelated
concerns are merged because they look similar. The Pragmatic
Programmers warned: two pieces of code that are coincidentally
similar are not DRY violations.""",

        "q3": """\

**Q3 (Design Trade-off):** Two services, `BillingService` and
`SubscriptionService`, both have identical user validation logic
(20 lines). A developer proposes extracting it to a shared
`UserValidationLibrary`. Evaluate: when does this extraction
reduce the risk of divergence, and when does it create tight
coupling between unrelated services? State the decision criteria.

*Hint: The key question from The Surprising Truth: is this
knowledge duplication (same business rule in two places) or
coincidental duplication (similar code for different reasons)?
If the rules might diverge (billing validation ≠ subscription
validation), extraction creates wrong coupling.*"""
    },

    "DPT-051": {
        "evolution": """\
**EVOLUTION:**
Boat Anchor was catalogued in the 1998 AntiPatterns book as
unused infrastructure -- code or components retained for
hypothetical future use. The pattern intensified with cloud
computing: unused cloud resources (stopped VMs, idle load
balancers, orphaned storage volumes) cost money while providing
no value -- a financial Boat Anchor. FinOps (Financial Operations
for cloud) emerged as a discipline specifically to identify and
remove cloud Boat Anchors through automated cost analysis.
Technical debt tooling (SonarQube, CodeScene) added "unused code"
metrics to quantify the Boat Anchor load in codebases.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Unused components impose maintenance costs (they must be
kept compiling, secured, and understood) without providing
functionality. Remove what is not used. "We might need it
later" is not a sufficient justification -- version control
preserves everything that was deleted.

**Where else this pattern appears:**
- **Cloud infrastructure Boat Anchors (AWS orphaned resources):**
  Stopped EC2 instances, unattached EBS volumes, unused Elastic
  IPs -- each one costs money and clutters the infrastructure view.
- **Database unused columns and tables:** Tables created for
  features that were never deployed remain indefinitely, adding
  confusion to every schema investigation.
- **npm/Maven unused dependencies:** `package.json` with 50+
  dependencies, 20 of which are never imported -- each one
  is a security surface and build time cost.""",

        "surprise": """\
---

### 💡 The Surprising Truth

npm's left-pad incident (2016) -- where a developer unpublished
a 11-line utility package that thousands of projects depended
on, breaking the npm ecosystem for hours -- was the Boat Anchor
anti-pattern in reverse. The packages that depended on `left-pad`
were not Boat Anchors (they were actively used), but their
dependency on a trivial 11-line package represented a failure
to question whether a utility so simple needed an external
dependency at all. The incident triggered the npm registry's
unpublish policy changes, and "is this dependency worth the
dependency?" became a standard code review question -- a
direct consequence of a Boat Anchor-like over-dependency.""",

        "q3": """\

**Q3 (Design Trade-off):** A Java project has 45 Maven
dependencies in `pom.xml`. A `mvn dependency:analyze` run
shows 12 are "declared but unused" and 8 are "used but
undeclared" (transitive). Describe: (1) what the "used but
undeclared" finding means for reliability, (2) the risk of
removing the 12 "unused" dependencies without further
investigation, and (3) how to safely clean up unused
dependencies with correct verification.

*Hint: The Failure Modes section covers compilation vs.
runtime detection. "Declared but unused" in Maven analysis
means unused at compile time -- some dependencies are only
needed at runtime (JDBC drivers, logging backends).*"""
    },

    "DPT-052": {
        "evolution": """\
**EVOLUTION:**
CQRS was formalised by Greg Young (2010) as a step beyond the
CQS (Command Query Separation) principle Bertrand Meyer introduced
in "Object-Oriented Software Construction" (1988). CQS is a method-
level principle; CQRS scales it to the architectural level.
Event Sourcing frequently accompanies CQRS: commands produce events
that are the source of truth; read models are projections of those
events. Axon Framework (Java) and EventStore are dedicated CQRS/ES
platforms. Cloud providers offer managed event stores (AWS
EventBridge, Azure Event Hub) that enable CQRS at infrastructure
scale without operational overhead.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Read patterns and write patterns for the same data differ
fundamentally. Reads need denormalised, query-optimised views;
writes need normalised, consistent, transactional models.
Serving both from the same data model forces compromises in each.

**Where else this pattern appears:**
- **Data warehousing (OLTP vs OLAP):** Transactional databases
  are normalised for write correctness; analytical databases
  are denormalised star schemas for read performance -- CQRS
  at the database architecture level.
- **Microservices read replicas:** A service maintains a write
  model in its primary database and a read model in Elasticsearch
  or a denormalised replica -- CQRS between service layers.
- **DNS (authoritative vs. resolver):** Authoritative servers are
  the "write side" (source of truth); resolver caches are the
  "read side" (eventually consistent copies optimised for
  fast lookup).""",

        "surprise": """\
---

### 💡 The Surprising Truth

Greg Young, who popularised CQRS, has repeatedly warned that
most applications do not need CQRS at the architectural level.
In his 2012 talk "8 Lines of Code," he argued that the majority
of CQRS adopters apply it to systems that would be better served
by a simple CRUD architecture. The pattern pays off specifically
when read and write load are dramatically different (100:1 read/
write ratio is a common threshold) or when the query shape is
fundamentally incompatible with the write model structure.
For the average business application, CQRS adds two data
sources, eventual consistency complexity, and significant
operational overhead for minimal benefit.""",

        "q3": """\

**Q3 (Design Trade-off):** An e-commerce system uses CQRS:
`OrderCommandService` writes to a normalised `orders` database;
`OrderQueryService` reads from an Elasticsearch index. A
product price update triggers: (1) write to the command side,
(2) event published, (3) read model updated in Elasticsearch.
Step 3 has a 2-second propagation delay. A customer queries
their cart during this 2-second window. Describe the exact
inconsistency they see and three strategies to handle it.

*Hint: The WHAT CHANGES AT SCALE section addresses eventual
consistency. The three strategies are: accept inconsistency,
add a version check (read-your-writes using session tokens),
or short-circuit the query side for the write originator.*"""
    },

    "DPT-053": {
        "evolution": """\
**EVOLUTION:**
Outbox Pattern emerged from distributed systems practice as
transaction-message atomicity became a critical reliability
requirement in microservices (circa 2016-2018). Chris Richardson
documented it in "Microservices Patterns" (2018) as the canonical
solution to the dual-write problem. Spring's Modulith (2023) added
built-in `@ApplicationModuleListener` with outbox table support.
Debezium (CDC -- Change Data Capture) provides infrastructure-level
outbox support by streaming database change logs directly to Kafka,
eliminating manual outbox polling. The pattern is now considered
a prerequisite for event-driven microservices in regulated
industries.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a business operation requires both a database change and
a message publication to be atomic, use the database as the
first-class message store. Write the message to the database
in the same transaction as the business change. Publish
asynchronously from the database.

**Where else this pattern appears:**
- **Write-Ahead Log (WAL) in databases:** The database first
  writes to the WAL (outbox) before modifying actual data pages.
  If the transaction rolls back, the WAL is ignored. This is
  the outbox pattern for database durability.
- **Email sending in e-commerce:** A best practice is to persist
  pending emails in the database within the order transaction,
  then send them asynchronously -- outbox prevents lost emails
  when the email service is temporarily down.
- **Audit log immutability:** Write audit log entries to the
  same transaction as the audited operation, not as a separate
  call -- the audit entry is the outbox for the audit system.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Outbox Pattern is a rediscovery of a pattern used in
mainframe banking systems in the 1970s, called "reliable
messaging through persistent queues." Before microservices,
IBM MQ (MQSeries) implemented the same concept: messages were
persisted to stable storage before delivery, guaranteeing
at-least-once delivery even across system restarts. What is
"new" about the Outbox Pattern in microservices is the
solution to the dual-write problem using the application's own
database rather than a separate message queue -- using SQL
`COMMIT` as the atomicity boundary rather than a two-phase
commit across two separate systems.""",

        "q3": """\

**Q3 (Design Trade-off):** An Outbox implementation uses
a polling scheduler that reads unpublished outbox records
every 100ms. Under normal load (100 events/minute) this
is fine. Under peak load (10,000 events/minute) the
scheduler falls behind, events are published with 5+ second
delay. Describe two architectural approaches to replace
polling with event-driven outbox draining, and explain
Debezium's CDC approach as a third option.

*Hint: The How It Works section shows polling as the standard
outbox drain mechanism. The event-driven alternatives are:
database trigger → message queue, and CDC log-based
streaming (Debezium reads the WAL).*"""
    },

    "DPT-054": {
        "evolution": """\
**EVOLUTION:**
Saga Pattern appeared in Hector Garcia-Molina and Kenneth Salem's
1987 database paper as a solution to long-lived transactions
in a single database. Microservices architects rediscovered it
(circa 2016-2018) as the standard solution to distributed
transaction management across service boundaries. Chris Richardson
formalised Choreography-based and Orchestration-based Sagas in
"Microservices Patterns" (2018). Axon Saga and Temporal.io emerged
as dedicated orchestration platforms. AWS Step Functions and Azure
Durable Functions implement the orchestration variant at cloud
infrastructure scale.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Break a long-running multi-step process into a sequence of
local transactions, each with a compensating transaction that
undoes its effect. Accept eventual consistency; guarantee
eventual correctness through compensation.

**Where else this pattern appears:**
- **Airline booking hold-and-confirm flow:** Seat hold (local
  transaction) → payment capture → seat confirmation → email.
  If payment fails: seat release (compensation). Each step
  has a defined undo.
- **Bank wire transfer:** Debit source account → route → credit
  destination. If routing fails: reverse debit (compensation).
  Banks use compensating transactions, not two-phase commits,
  for international transfers.
- **Supply chain procurement:** Purchase order → supplier
  confirmation → inventory reservation → shipping. Failed
  confirmations trigger cancellation workflows -- Saga at
  business process level.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The 1987 Garcia-Molina and Salem paper that introduced the Saga
pattern was about a single-database problem: long-lived database
transactions (transactions running for hours or days) prevented
the database from reclaiming locks and performing maintenance.
Sagas were proposed as a way to break these into shorter
transactions. The paper had nothing to do with microservices.
When microservices architects encountered distributed transaction
coordination 30 years later, they independently invented the
same solution -- and only later discovered the original 1987
paper, which had been largely ignored in the distributed systems
community. The pattern was forgotten and rediscovered.""",

        "q3": """\

**Q3 (Design Trade-off):** A Choreography Saga has 5 services
(Order, Payment, Inventory, Shipping, Notification) each
listening to events. An end-to-end test reveals that the saga
correctly completes in the happy path but leaves partial state
when the Inventory service is down. Design the observability
infrastructure required to (1) detect a stuck saga, (2) identify
which step it failed at, (3) replay the saga from the failure
point.

*Hint: The Failure Modes section covers saga observability.
The key components needed are: a saga state store (persisted
to track current step), correlation IDs on all events, and
a monitoring dashboard that shows saga instance states.*"""
    },

    "DPT-055": {
        "evolution": """\
**EVOLUTION:**
Strangler Fig Pattern was coined by Martin Fowler in 2004,
inspired by the strangler fig tree that grows around a host tree
and eventually replaces it. It gained prominence with the
microservices movement (2014-2018) as the standard approach
to decomposing monolithic applications incrementally. Netflix,
Amazon, and Uber publicly documented their Strangler Fig
migrations. Sam Newman's "Building Microservices" (2015) and
"Monolith to Microservices" (2019) formalised the pattern with
detailed migration strategies. The Pattern is now considered
the safest known approach to legacy system modernisation in
production environments.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Migrate a legacy system by building the replacement alongside it,
routing traffic incrementally from old to new, and removing
the old system only after the new system has absorbed all
its traffic. Never perform a "big bang" cutover.

**Where else this pattern appears:**
- **Database schema migration (expand-contract):** Add new
  columns/tables (expand), migrate data to them, update code
  to use new structure, remove old structure (contract) --
  the Strangler Fig pattern applied to database evolution.
- **Infrastructure blue-green deployment:** New infrastructure
  is built ("green") while old continues running ("blue");
  traffic is shifted from blue to green incrementally.
- **Feature flag rollouts:** New feature code coexists with old
  code behind a flag; traffic is incrementally shifted to the
  new path; old code is removed when migration is complete.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Martin Fowler's original Strangler Fig article (2004) described
the pattern for migrating to a new website, not for
microservices decomposition. The microservices community adopted
it wholesale as a legacy decomposition strategy -- a perfectly
valid application, but one Fowler did not anticipate. The
irony: the original motivation (website migration) is now
considered the simpler use case. The microservices application
(migrating from a monolith to distributed services) is
significantly more complex because it involves not just routing
but also data migration, distributed transaction handling,
and service boundary definition -- problems invisible in
the original website migration scenario.""",

        "q3": """\

**Q3 (Design Trade-off):** A team is strangling a monolith's
`OrderManagement` module into a new `OrderService`. They use
an API gateway to route 5% of order creation traffic to
the new service. The new service uses a separate database.
After two weeks, they discover 15 orders are duplicated --
both the monolith and the new service processed the same
order IDs. Trace the root cause and describe the structural
changes needed before increasing traffic beyond 5%.

*Hint: The Failure Modes section covers data consistency during
migration. The duplicate ID issue arises from shared state
(the order ID sequence or database) being split -- the two
services need a coordination mechanism during the migration.*"""
    },

    "DPT-056": {
        "evolution": """\
**EVOLUTION:**
Bulkhead Pattern was introduced by Michael Nygard in "Release It!"
(2007) as one of the core stability patterns. It gained
operational importance with the microservices movement: a single
slow downstream service could exhaust a shared thread pool and
take down an entire application. Netflix's Hystrix library
(2012) popularised bulkhead isolation with thread-pool-based
command execution. Hystrix was deprecated in favour of Resilience4j
(2020), which provides bulkhead implementations based on both
thread pools (heavyweight) and semaphores (lightweight). Service
mesh implementations (Istio, Linkerd) moved bulkhead enforcement
to the infrastructure layer, removing the need for application-
level bulkhead code.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Partition a system's capacity so that failures in one
partition cannot exhaust the capacity of others. Size each
partition for its own worst-case failure, not the global
total load.

**Where else this pattern appears:**
- **Ship watertight compartments (origin of the name):** A
  ship's hull is divided into compartments; a hull breach
  floods one compartment but not the entire ship. The Titanic
  's compartment design failed because the compartments were
  open at the top -- a bulkhead design flaw.
- **AWS Availability Zone isolation:** Deploying to multiple AZs
  creates bulkheads between failure domains -- an AZ outage
  floods one compartment (AZ) but not the others.
- **Circuit breaker fuses in electrical systems:** Each circuit
  has its own fuse -- a short in one circuit breaks that fuse
  but does not trip the main breaker, preserving other circuits.""",

        "surprise": """\
---

### 💡 The Surprising Truth

The Titanic's bulkhead design was considered state-of-the-art in
1912 and the ship was certified as "practically unsinkable" by
its builders. The design had 16 watertight compartments and could
survive any 2 being flooded simultaneously. The iceberg flooded
5 compartments. The critical flaw: the bulkheads did not extend
to the ship's ceiling -- each compartment was open at the top.
When compartment 1 filled, water spilled over the bulkhead into
compartment 2, and cascaded through all 5 forward compartments.
The cascading bulkhead failure is now the textbook example of
why bulkhead isolation requires the partition to be complete --
partial bulkheads provide partial protection.""",

        "q3": """\

**Q3 (Design Trade-off):** A service calls three downstream
services: AuthService (critical), InventoryService (important),
and RecommendationService (optional). All share the default
HTTP client thread pool. AuthService begins responding in
10 seconds. Describe: (1) what happens to InventoryService
and RecommendationService calls during the AuthService
degradation, (2) how to implement bulkhead isolation using
Resilience4j, (3) the correct timeout and pool size for
each service given their service-level priority.

*Hint: The Complete Picture section traces exactly this failure
cascade. RecommendationService should have the smallest pool
(it's optional); AuthService pool size determines maximum
concurrent auth operations.*"""
    },

    "DPT-057": {
        "evolution": """\
**EVOLUTION:**
Circuit Breaker Pattern was named and popularised by Michael
Nygard in "Release It!" (2007), inspired by electrical circuit
breakers. Netflix Hystrix (2012) made it the default resiliency
pattern for Java microservices, with a dashboard for real-time
monitoring. Hystrix was deprecated in 2018 due to maintenance
burden, and Resilience4j became the successor. Service mesh
implementations (Istio, Linkerd) moved circuit breaking to the
infrastructure layer using Envoy proxy, making application-level
circuit breaker code less necessary in mesh-enabled environments.
AWS App Mesh and Azure Front Door embed circuit breaking in
managed load balancers.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Fail fast when a dependency is known to be unavailable. Do
not allow slow or failing dependencies to consume resource
threads. Periodically probe the dependency for recovery and
restore traffic when healthy.

**Where else this pattern appears:**
- **Electrical circuit breakers:** The naming origin. An
  electrical fault causes high current; the breaker trips
  (OPEN), protecting the circuit. Manually reset (HALF-OPEN)
  to test if fault is cleared.
- **TCP connection timeout tuning:** OS TCP stack fast-detects
  broken connections and fails subsequent sends immediately
  rather than waiting for full TCP timeout -- a protocol-level
  circuit breaker.
- **Browser resource loading:** Browsers stop loading assets
  from a host that has returned errors for recent requests
  and switch to a "fail silently" mode -- a browser-level
  circuit breaker for CDN failures.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Netflix Hystrix, which popularised Circuit Breaker in Java
microservices and was used in production at Netflix for years,
was deprecated by Netflix in 2018 with this explanation: "Hystrix
is no longer in active development, and we are not accepting new
feature requests." The Netflix engineering blog stated they had
moved to "adaptive concurrency limits" (using TCP-congestion-
control-inspired algorithms) rather than static timeout and error
rate thresholds. The key insight: fixed thresholds require careful
tuning for every deployment environment; adaptive algorithms
self-tune based on observed latency. Circuit Breaker with fixed
thresholds is now considered a first-generation resiliency pattern.""",

        "q3": """\

**Q3 (Design Trade-off):** A Circuit Breaker has a threshold
of "50% errors in 10 seconds opens the circuit." A downstream
service is experiencing intermittent 5xx errors affecting 30%
of requests (below threshold). The service is degraded but not
circuit-breaking. Describe what is happening to the 30% failing
requests, the impact on user experience, and how to add partial
degradation handling for the period before the circuit opens.

*Hint: The Failure Modes section covers the "33% error rate
does not trip circuit" scenario. The combination of Circuit
Breaker + Retry + Fallback addresses the "degraded but not
open" state.*"""
    },

    "DPT-058": {
        "evolution": """\
**EVOLUTION:**
Sidecar Pattern emerged from the container era: Docker (2013)
and Kubernetes (2014) made running multiple containers per
"pod" practical. The pattern became central to service mesh
architecture (Istio, Linkerd, 2017-2018) where an Envoy proxy
sidecar handles all network traffic for the application container
without any application code changes. Kubernetes natively supports
the model through Pods (multiple containers share network and
storage). Dapr (Distributed Application Runtime, 2019) extended
it to provide distributed system building blocks (pub/sub, state
management, service invocation) via sidecar without framework
dependencies.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Attach cross-cutting operational concerns (logging, networking,
security, monitoring) to an application as a co-located
companion rather than embedding them in the application code.
The application stays focused on business logic; the sidecar
handles operational concerns.

**Where else this pattern appears:**
- **Log agent sidecars (Fluentd, Filebeat):** A log-shipping
  agent runs alongside the application container and ships
  logs to the centralised log store -- the application writes
  to stdout; the sidecar handles log forwarding.
- **Secret management sidecar (Vault Agent):** Vault Agent
  runs alongside the application and injects secrets as
  files -- the application reads plain files; the sidecar
  handles secret rotation and TTL management.
- **Proxy sidecars (Nginx + application):** Nginx handles
  SSL termination, rate limiting, and static file serving
  alongside a backend application -- separation of concerns
  at the container level.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Istio's service mesh, which is built entirely on the Sidecar
pattern with Envoy proxies, was found to add significant overhead
at scale: each Envoy sidecar proxy adds ~50ms of latency per
hop and approximately 300MB of memory overhead per service
instance. For a system with 100 microservices, the sidecar
infrastructure alone can consume 30GB of RAM cluster-wide.
Cilium eBPF-based service mesh emerged as an alternative that
achieves the same networking capabilities at the kernel level
without per-pod sidecar processes, consuming a fraction of
the resources. The Sidecar pattern optimizes for code isolation
at the cost of resource and latency overhead.""",

        "q3": """\

**Q3 (Design Trade-off):** A team runs 50 microservices on
Kubernetes. They are considering adopting Istio service mesh
(Envoy sidecar per pod) vs. implementing observability and
mTLS directly in each service via a shared library. Compare
these approaches on: (1) network latency, (2) operational
complexity, (3) developer freedom to choose languages,
(4) upgrade path for security fixes.

*Hint: The Comparison Table and Failure Modes sections address
this trade-off. The shared library approach requires
coordination across all services for updates; the sidecar
approach centralises control but adds network hops.*"""
    },

    "DPT-059": {
        "evolution": """\
**EVOLUTION:**
Ambassador Pattern emerged alongside the Sidecar Pattern in the
container era (2015-2017) as a specialisation: while Sidecar is
generic, Ambassador specifically handles outbound service
communication. Netflix's client-side load balancing (Ribbon,
2013) was a pre-container Ambassador variant -- a library
embedded in the client that handled discovery and load balancing.
Service meshes (Istio, Linkerd) subsumed Ambassador into Envoy
proxy, which handles both inbound (Gateway) and outbound
(Ambassador) concerns. Dapr's service invocation component
is a managed Ambassador for cross-service calls without
service discovery code in the application.""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When multiple services need to communicate with the same
external dependency using the same protocol, retry, discovery,
and observability logic, centralise that outbound communication
logic in a dedicated ambassador rather than replicating it
in every service.

**Where else this pattern appears:**
- **Outbound proxy (corporate proxy servers):** All corporate
  internet traffic routes through a proxy that enforces
  security policy, logs requests, and applies rate limits --
  an ambassador for all outbound internet communication.
- **Database connection proxy (PgBouncer, ProxySQL):** Database
  traffic from all application instances passes through a
  connection pool proxy that manages connections -- an
  ambassador for database communication.
- **API Gateway outbound calls:** An API Gateway that calls
  multiple backend services acts as an ambassador for all
  external callers -- request routing, retry, and circuit
  breaking are centralised.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Netflix's Ribbon library -- which performed client-side load
balancing and was one of the foundational microservices libraries
(used in millions of production instances from 2013-2020) --
was put into maintenance mode and replaced by Spring Cloud
LoadBalancer because it was incompatible with reactive
programming models. Ribbon used thread-local state and blocking
I/O, which prevented use with WebFlux and reactive HTTP clients.
This is the Ambassador pattern's fundamental tension: the
ambassador must be written with the same concurrency model as
the service it serves. A blocking Ambassador in a non-blocking
service is as harmful as no ambassador at all.""",

        "q3": """\

**Q3 (Design Trade-off):** A Python service and a Java service
both call the same external inventory API, each implementing
their own retry, timeout, and circuit-breaker logic. A team
proposes an Ambassador sidecar that centralises this logic
for both services. Describe: (1) the network path change when
the Ambassador is introduced, (2) the failure modes introduced
by adding the Ambassador as an additional hop, (3) the conditions
under which this trade-off is justified.

*Hint: The Failure Modes section and the Sidecar comparison
both address the additional hop latency. The justification
threshold is: when the ambassador eliminates more bugs than
the additional operational complexity it introduces.*"""
    },

    "DPT-060": {
        "evolution": """\
**EVOLUTION:**
Retry Pattern was standard practice long before it was named --
every network programming guide from the 1980s included retry
loops. It was formalised as a named resiliency pattern in Nygard's
"Release It!" (2007). Spring Retry (2012) provided annotated
retries (`@Retryable`). Resilience4j's `Retry` module (2020)
added configurable backoff strategies and retry event listeners.
AWS SDK and Azure SDK built exponential backoff with jitter into
their clients as defaults. The pattern is now considered table
stakes for any network call in production code; the discussion
has shifted from "should we retry?" to "what backoff strategy,
max attempts, and jitter configuration is appropriate?"'""",

        "wisdom": """\
---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Transient failures are normal in distributed systems. When a
failure is transient, automatically retry the operation with
appropriate wait time rather than immediately failing to the
user. Exponential backoff with jitter prevents retry storms.

**Where else this pattern appears:**
- **TCP retransmission:** The TCP protocol automatically
  retransmits lost packets with exponential backoff -- the IP
  network's Retry pattern built into the transport layer.
- **DNS resolution retries:** DNS resolvers retry failed lookups
  against multiple nameservers with configurable timeouts --
  the Retry pattern in distributed naming infrastructure.
- **ATM transaction retries:** ATMs retry failed transactions
  (network timeout, busy bank server) automatically before
  displaying a user-visible error -- the Retry pattern in
  financial terminal infrastructure.""",

        "surprise": """\
---

### 💡 The Surprising Truth

Exponential backoff without random jitter -- a textbook-correct
implementation of Retry -- caused a major global AWS outage in
2012. When thousands of clients all experienced the same error
simultaneously (an AWS infrastructure failure), they all
independently computed the same backoff schedule (2s, 4s, 8s...)
and retried simultaneously at exactly the same intervals,
creating "retry thundering herds" that prolonged the outage
for hours. AWS documented this as "thundering herd, exponential
backoff edition" and added random jitter to all AWS SDKs as
a default. Correct Retry is not `sleep(2^n)` -- it is
`sleep(random(0, 2^n))`. The difference prevented a class
of outages from recurring.""",

        "q3": """\

**Q3 (Design Trade-off):** A service retries failed API calls
with 3 attempts and exponential backoff (1s, 2s, 4s). The
downstream API provides idempotency keys. In a scenario where
the first request succeeds on the server but the response
is lost in transit, describe: (1) what happens without
idempotency keys, (2) how idempotency keys make retries safe,
(3) at what point retrying becomes harmful even with
idempotency keys.

*Hint: The Failure Modes section covers at-least-once vs.
exactly-once retry semantics. Without idempotency keys,
retries on lost responses cause duplicate operations. The
"harmful" threshold is when the operation has non-idempotent
side effects that idempotency keys don't cover.*"""
    },
}

def get_invention_moment_end(content):
    pos = content.find("**THE INVENTION MOMENT:**")
    if pos == -1:
        return -1
    after = content.find("\n\n---", pos)
    after2 = content.find("\n\n### ", pos)
    if after == -1 and after2 == -1:
        return -1
    if after == -1:
        return after2
    if after2 == -1:
        return after
    return min(after, after2)

def insert_evolution(content, evolution_text):
    if "**EVOLUTION:**" in content:
        return content
    pos = get_invention_moment_end(content)
    if pos == -1:
        print("  WARNING: Could not find insertion point for EVOLUTION")
        return content
    return content[:pos] + "\n\n" + evolution_text + content[pos:]

def insert_wisdom_and_surprise(content, dpt_id, wisdom_text, surprise_text):
    if "### 💎 Transferable Wisdom" in content:
        return content
    think_pos = content.find("### 🧠 Think About This Before We Continue")
    if think_pos == -1:
        print(f"  WARNING: Could not find Think section")
        return content
    pre_think = content.rfind("\n---\n", 0, think_pos)
    if pre_think == -1:
        insert_pos = think_pos
    else:
        insert_pos = pre_think + 1
    insert_text = "\n" + wisdom_text + "\n\n" + surprise_text + "\n"
    return content[:insert_pos] + insert_text + content[insert_pos:]

def fix_think_section(content, q3_text):
    if "*Hint:" in content:
        return content
    think_pos = content.find("### 🧠 Think About This Before We Continue")
    if think_pos == -1:
        return content
    next_section = content.find("\n---\n", think_pos)
    if next_section == -1:
        section_content = content[think_pos:]
        rest = ""
    else:
        section_content = content[think_pos:next_section]
        rest = content[next_section:]
    new_section = section_content
    q1_end = new_section.find("\n\n**Q2.")
    if q1_end == -1:
        q1_end = new_section.find("\n\n**Q2 ")
    if q1_end != -1:
        hint1 = "\n\n*Hint: Look at the First Principles section for the core invariants " \
                "and the Failure Modes section for where this scenario appears as a documented issue.*"
        new_section = new_section[:q1_end] + hint1 + new_section[q1_end:]
    q2_start = new_section.find("**Q2.")
    if q2_start == -1:
        q2_start = new_section.find("**Q2 ")
    if q2_start != -1:
        q2_end = new_section.find("\n\n\n", q2_start)
        if q2_end == -1:
            q2_end = len(new_section)
        hint2 = "\n\n*Hint: The Comparison Table and Level 3-4 explanations contain " \
                "the mechanism that determines which approach wins in this scenario.*"
        new_section = new_section[:q2_end] + hint2 + new_section[q2_end:]
    new_section = new_section.rstrip() + "\n" + q3_text + "\n"
    if next_section == -1:
        return content[:think_pos] + new_section
    else:
        return content[:think_pos] + new_section + rest

def process_file(dpt_id, data):
    fname = None
    for f in os.listdir(BASE):
        if f.startswith(dpt_id + " "):
            fname = f
            break
    if not fname:
        print(f"File not found for {dpt_id}")
        return
    fpath = os.path.join(BASE, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    content = insert_evolution(content, data["evolution"])
    content = insert_wisdom_and_surprise(content, dpt_id, data["wisdom"], data["surprise"])
    content = fix_think_section(content, data["q3"])
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"UPDATED: {fname}")
    else:
        print(f"NO CHANGE: {fname}")

if __name__ == "__main__":
    for dpt_id, data in CONTENT.items():
        print(f"\nProcessing {dpt_id}...")
        process_file(dpt_id, data)
    print("\nBatch 2 complete!")

