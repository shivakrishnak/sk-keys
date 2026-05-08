---
layout: default
title: "WebFlux  Reactive"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /spring/webflux-reactive/
id: SPR-052
category: Spring Core
difficulty: ★★★
depends_on: Reactor, Event Loop, Non-blocking I/O, Spring MVC
used_by: High-Throughput APIs, Microservices, Streaming
related: Mono / Flux, Spring MVC, Netty, Backpressure
tags:
  - spring
  - java
  - performance
  - deep-dive
  - reactive
---

# SPR-052 — WebFlux  Reactive

⚡ TL;DR — Spring WebFlux replaces the one-thread-per-request model with an event-loop that handles thousands of concurrent I/O operations on a handful of threads, trading blocking simplicity for non-blocking scalability.

| #404            | Category: Spring Core                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Reactor, Event Loop, Non-blocking I/O, Spring MVC |                 |
| **Used by:**    | High-Throughput APIs, Microservices, Streaming    |                 |
| **Related:**    | Mono / Flux, Spring MVC, Netty, Backpressure      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Spring MVC service calls three downstream APIs to build a response. Each API call takes 100ms. Sequentially: 300ms total. To make them parallel, you use `CompletableFuture` and a thread pool. With 1,000 concurrent requests, that's 3,000 threads just for downstream calls — plus your worker threads. At 3,000 threads, the JVM is burning 3GB of memory (1MB stack per thread) and spending more time on context switching than on actual work. The system runs at 30% CPU utilization but is "busy" — all threads are blocked waiting on I/O.

**THE BREAKING POINT:**
The thread-per-request model hits a wall at I/O-bound services: threads sit idle waiting for network responses while consuming memory. The hardware can handle far more concurrent I/O operations than you have threads. You're leaving capacity on the table.

**THE INVENTION MOMENT:**
"This is exactly why reactive programming and Spring WebFlux were created."

---

### 📘 Textbook Definition

**Spring WebFlux** is Spring's reactive-stack web framework, introduced in Spring 5. It is built on **Project Reactor** (which implements the Reactive Streams specification) and runs on non-blocking servers such as **Netty** (default), Undertow, or Servlet 3.1+ containers. Instead of dedicating a thread to each request for the duration of its handling, WebFlux uses an event loop model: a small fixed thread pool (typically `nCPU * 2` threads) processes events — incoming requests, I/O completions, timer fires — one at a time, without blocking. Handler methods return `Mono<T>` (0 or 1 element) or `Flux<T>` (0 or N elements) — reactive types that describe asynchronous computation pipelines. WebFlux is functionally equivalent to Spring MVC for REST APIs but uses a non-blocking execution model throughout the stack.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
WebFlux handles many requests with few threads by never blocking — each thread always has work to do.

**One analogy:**

> A waiter in a traditional restaurant (Spring MVC) takes an order, goes to the kitchen, STANDS THERE WAITING for the food, then brings it back — doing nothing while the kitchen cooks. A waiter in a reactive restaurant (WebFlux) takes an order, gives the kitchen a ticket, immediately serves the next table, gets notified when the food is ready, then delivers it. Same one waiter can serve many tables simultaneously.

**One insight:**
The key trade-off: blocking code is easy to read and debug (stack traces are meaningful); non-blocking reactive code is efficient but requires a mental shift to "describe what to do with results when they arrive" instead of "wait for the result."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. No blocking calls on event-loop threads — any blocking I/O (JDBC, thread sleep, synchronous HTTP client) defeats the non-blocking model and starves the event loop.
2. Handler methods declare their output as `Mono<T>` or `Flux<T>` — reactive pipelines are assembled first, executed later when subscribed.
3. Backpressure propagates from subscriber to publisher — a slow consumer can signal a fast producer to slow down.

**DERIVED DESIGN:**
The event loop (Netty's `NioEventLoop`) uses Java NIO's `Selector` to multiplex thousands of connections onto a single thread. When a network packet arrives, the selector notifies the event loop, which reads the data and passes it downstream. The event loop thread never blocks — it handles the event and immediately picks up the next. This means a single thread can manage thousands of concurrent connections.

When a WebFlux handler method makes an outbound HTTP call using `WebClient`, it registers a callback with the event loop rather than blocking a thread. When the response arrives, the event loop fires the callback, which continues processing on the same (or another) event loop thread.

**THE TRADE-OFFS:**
**Gain:** 10–20x more concurrent connections per CPU core vs. thread-per-request; eliminates thread-per-request memory overhead (1MB stack per thread); natural streaming of large responses.
**Cost:** Reactive code is harder to read, write, and debug. Stack traces show `subscribe()` chains instead of your code. Any blocking call (JDBC, legacy library) on an event-loop thread corrupts performance. Debugging requires reactive-aware tools (Hooks.onOperatorDebug). Not all Java libraries are non-blocking.

---

### 🧪 Thought Experiment

**SETUP:**
Two Spring services, identical logic: receive a request, call two external APIs in parallel, combine results, return response. Each external API call takes 200ms. Service A uses Spring MVC (blocking). Service B uses Spring WebFlux (non-blocking).

**AT 100 CONCURRENT REQUESTS:**
Spring MVC: 100 requests × 2 parallel API calls = 200 threads all blocked on I/O for 200ms. Thread overhead: 200MB RAM. CPU: minimal (all waiting). Works fine.

Spring WebFlux: 1–8 event loop threads handle all 100 requests. 200 non-blocking I/O callbacks registered. CPU: minimal. RAM: MB not GB. Works fine.

**AT 10,000 CONCURRENT REQUESTS:**
Spring MVC: 20,000 threads blocked on I/O. At 1MB per thread: 20GB RAM just for stacks. JVM GC pauses from stack memory. Context switching overhead dominates. System becomes unresponsive.

Spring WebFlux: Still 8 event loop threads. 20,000 non-blocking I/O callbacks registered. Same RAM footprint as 100 requests. System handles load.

**THE INSIGHT:**
WebFlux's advantage is not request-processing speed — a single request is often slower (overhead of reactive pipeline assembly). The advantage is concurrency density: how many concurrent requests can run with a given RAM budget.

---

### 🧠 Mental Model / Analogy

> WebFlux is like a restaurant kitchen with a single highly-skilled chef using a professional range with 20 burners. Each burner has a dish going. The chef doesn't stand at one burner waiting — they stir dish 1, flip dish 2, check temperature on dish 3, come back to dish 1. Every second the chef is actively doing something. Traditional MVC is a separate chef standing at each burner, doing nothing while the dish simmers.

- "One skilled chef" → small fixed event-loop thread pool
- "20 burners simultaneously" → 20 (or thousands) of concurrent I/O operations
- "Stirring/flipping/checking" → processing I/O events as they complete
- "Dish recipe" → `Flux` or `Mono` pipeline — describes what to do at each step
- "Dish being delivered" → reactive publisher emitting values

Where this analogy breaks down: if the chef has to perform a 10-minute task that requires their full attention (a blocking operation), all other dishes burn. Same with blocking on an event-loop thread.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Spring WebFlux is a way to write web services that can handle many more simultaneous users using the same hardware, by never making threads wait around doing nothing.

**Level 2 — How to use it (junior developer):**
Use `@RestController` and `@GetMapping` exactly as in Spring MVC, but return `Mono<ResponseEntity<T>>` or `Flux<T>` instead of plain objects. Inject `WebClient` instead of `RestTemplate` for outbound HTTP calls. Use reactive repositories (Spring Data Reactive) for database access. Never call `Thread.sleep()`, `Future.get()`, or blocking JDBC inside a WebFlux handler.

**Level 3 — How it works (mid-level engineer):**
WebFlux uses Netty as its default HTTP server. Netty runs an `NioEventLoopGroup` with `nCPU * 2` threads. Each thread runs a `Selector` loop that monitors registered NIO channels for read/write readiness. When a request arrives, Netty reads the bytes and passes them to the WebFlux `DispatcherHandler`. The handler maps the request to a `RouterFunction` or `@Controller`, calls the handler method, and subscribes to the returned `Mono`/`Flux`. Subscription triggers the pipeline to execute. Each operator in the pipeline (map, flatMap, filter) is non-blocking. When the pipeline needs to call an external service via `WebClient`, the `WebClient` registers a callback on Netty's event loop for the response; the event loop thread is immediately available for other events. When the response arrives, the callback fires and continues the pipeline.

**Level 4 — Why it was designed this way (senior/staff):**
The Reactive Streams specification (which Reactor implements) was designed by a consortium including Netflix, Pivotal, Red Hat, and Twitter to solve the cross-library interoperability problem: each reactive library (RxJava, Akka Streams, Reactor) had incompatible types. Reactive Streams defines `Publisher`, `Subscriber`, `Subscription`, and `Processor` — 4 interfaces that all reactive libraries implement. WebFlux chose Reactor (Pivotal's implementation) as its native reactive library but via the RS spec can interoperate with RxJava and others. The decision to build WebFlux as a parallel stack (not replace Spring MVC) reflects pragmatism: most Spring MVC applications don't need reactive; migrating is high-cost and high-risk. WebFlux is opt-in for greenfield high-concurrency services.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ SPRING WEBFLUX REQUEST FLOW (Netty)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Client HTTP request                                    │
│    ↓                                                    │
│  NioEventLoop Thread (1 of nCPU*2)                      │
│    ↓ reads bytes, decodes HTTP                          │
│  DispatcherHandler.handle(exchange)                     │
│    ↓ route to @Controller                               │
│  Handler method → returns Mono<Response>                │
│    │ (pipeline ASSEMBLED but NOT yet executed)          │
│    ↓ DispatcherHandler subscribes                       │
│  Pipeline EXECUTES:                                     │
│    ↓                                                    │
│  flatMap(id → WebClient.get("/user/"+id))               │
│    │ registers NIO callback on event loop               │
│    │ event loop thread RELEASED — handles other reqs    │
│    │                                                    │
│    │  [... 200ms later: response bytes arrive ...]      │
│    │                                                    │
│    ↓ NIO callback fires on event loop thread            │
│  pipeline continues: map, filter, serialize             │
│    ↓                                                    │
│  HTTP response written to channel                       │
│                                                         │
│  SAME event loop thread may handle 1000s of requests   │
│  concurrently — never blocking                         │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — BAD: blocking inside WebFlux handler:**

```java
// BAD: Thread.sleep() on event-loop thread!
// Blocks ALL concurrent requests for 1 second
@GetMapping("/user/{id}")
public Mono<User> getUser(@PathVariable String id) {
    Thread.sleep(1000); // NEVER do this in WebFlux!
    return userRepository.findById(id);
}

// BAD: RestTemplate is blocking — use WebClient
@GetMapping("/user/{id}")
public Mono<User> getUser(@PathVariable String id) {
    // RestTemplate.getForObject blocks the event loop
    UserDto dto = restTemplate.getForObject(
        "/users/" + id, UserDto.class);
    return Mono.just(toUser(dto));
}
```

**Example 2 — GOOD: non-blocking WebFlux handlers:**

```java
@RestController
@RequestMapping("/api")
public class UserController {

    private final WebClient webClient;
    private final ReactiveUserRepository userRepository;

    public UserController(WebClient.Builder webClientBuilder,
                          ReactiveUserRepository repo) {
        this.webClient = webClientBuilder
            .baseUrl("http://user-service").build();
        this.userRepository = repo;
    }

    // Single item response
    @GetMapping("/users/{id}")
    public Mono<ResponseEntity<User>> getUser(
            @PathVariable String id) {
        return userRepository.findById(id)
            .map(user -> ResponseEntity.ok(user))
            .defaultIfEmpty(ResponseEntity
                .notFound().build());
    }

    // Stream response (SSE / streaming)
    @GetMapping(value = "/users/stream",
        produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<User> streamUsers() {
        return userRepository.findAll()
            .delayElements(Duration.ofMillis(100));
        // Client receives users one at a time as streamed events
    }

    // Parallel outbound calls — non-blocking
    @GetMapping("/dashboard/{userId}")
    public Mono<Dashboard> getDashboard(
            @PathVariable String userId) {
        Mono<Profile> profile = webClient.get()
            .uri("/profile/" + userId)
            .retrieve()
            .bodyToMono(Profile.class);

        Mono<Orders> orders = webClient.get()
            .uri("/orders/" + userId)
            .retrieve()
            .bodyToMono(Orders.class);

        // Both calls execute in parallel — combined when both complete
        return Mono.zip(profile, orders,
            (p, o) -> new Dashboard(p, o));
    }
}
```

**Example 3 — Offload blocking work to dedicated scheduler:**

```java
// When you MUST do blocking work (legacy JDBC, etc.)
@GetMapping("/legacy/{id}")
public Mono<User> getLegacyUser(@PathVariable String id) {
    // subscribeOn moves execution to boundedElastic scheduler
    // (thread pool for blocking ops) — event loop thread freed
    return Mono.fromCallable(() ->
            jdbcTemplate.queryForObject(
                "SELECT * FROM users WHERE id=?",
                userRowMapper, id))
        .subscribeOn(Schedulers.boundedElastic());
        // Result flows back to event loop when DB call completes
}
```

---

### ⚖️ Comparison Table

| Dimension           | Spring MVC (Servlet)                       | Spring WebFlux (Reactive)                             |
| ------------------- | ------------------------------------------ | ----------------------------------------------------- |
| Thread model        | 1 thread per request                       | Event loop (nCPU × 2)                                 |
| I/O model           | Blocking                                   | Non-blocking (NIO)                                    |
| Concurrency ceiling | ~200–500 threads                           | Thousands of connections                              |
| Code style          | Imperative (easy to read)                  | Declarative (reactive pipelines)                      |
| Stack traces        | Clear, sequential                          | Reactive chain (harder)                               |
| Default server      | Tomcat                                     | Netty                                                 |
| Database support    | JPA/JDBC (blocking)                        | R2DBC / Reactive drivers                              |
| When to choose      | Most services, CRUD, teams new to reactive | High I/O concurrency, streaming, microservice gateway |

How to choose: Start with Spring MVC unless you have a measured concurrency problem or need streaming. Migrate to WebFlux only when thread-per-request is your actual bottleneck, not a hypothetical one.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                             |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| WebFlux is always faster than Spring MVC            | WebFlux is faster under HIGH concurrency with I/O-bound workloads; for low concurrency or CPU-bound tasks, MVC may be faster                        |
| You can mix blocking code with WebFlux              | You can, but blocking on an event-loop thread defeats the model; use `subscribeOn(Schedulers.boundedElastic())` to isolate blocking code            |
| `@Async` in Spring MVC achieves the same as WebFlux | `@Async` offloads work to another thread pool but both threads are still blocked; WebFlux event loops are never blocked                             |
| WebFlux requires Netty                              | WebFlux works on Servlet 3.1+ containers (Tomcat, Jetty) in async mode; Netty is the default for full non-blocking                                  |
| Reactive Repositories work with any database        | Reactive repositories require a reactive driver (R2DBC for relational, reactive MongoDB driver); standard JPA/JDBC is blocking and must be isolated |

---

### 🚨 Failure Modes & Diagnosis

**1. Event Loop Thread Blocked — System Unresponsive**

**Symptom:** Application handles first few requests, then becomes completely unresponsive; all subsequent requests time out; CPU near zero.

**Root Cause:** Blocking call (JDBC, Thread.sleep, synchronous HTTP) on an event-loop thread. The fixed event-loop thread pool is fully occupied waiting, so no new events can be processed.

**Diagnostic:**

```bash
# Thread dump — look for event loop threads in WAITING/TIMED_WAITING
jstack <pid> | grep -B2 -A20 "reactor-http-nio"

# Enable BlockHound in tests to detect blocking calls
# (Reactor's BlockHound throws exception on blocking in reactive context)
# build.gradle: testImplementation 'io.projectreactor.tools:blockhound'
```

**Fix:**

```java
// BAD: JDBC on event loop
return Mono.fromCallable(() -> jdbcTemplate.query(...));

// GOOD: move to blocking scheduler
return Mono.fromCallable(() -> jdbcTemplate.query(...))
    .subscribeOn(Schedulers.boundedElastic());
```

**Prevention:** Enable BlockHound in development and test environments to catch blocking calls at development time.

---

**2. "subscribeOn has no effect" — Operator Ordering**

**Symptom:** Despite using `subscribeOn(Schedulers.boundedElastic())`, blocking code still runs on event-loop thread; application still becomes unresponsive.

**Root Cause:** `subscribeOn` affects only the subscription thread, not the operator thread. If blocking code is in a `map()` rather than a `Mono.fromCallable()`, `subscribeOn` may not cover it.

**Diagnostic:**

```java
// Add checkpoint for debugging operator execution context
Mono.fromCallable(() -> blockingCall())
    .checkpoint("before subscribeOn")
    .subscribeOn(Schedulers.boundedElastic())
    .checkpoint("after subscribeOn")
    .map(result -> transform(result));
```

**Fix:**

```java
// BAD: blocking in map() — runs on calling thread, not bounded
Mono.just(id)
    .map(i -> jdbcTemplate.query(i)) // blocking in map!
    .subscribeOn(Schedulers.boundedElastic()); // too late

// GOOD: wrap blocking call in fromCallable, then subscribeOn
Mono.fromCallable(() -> jdbcTemplate.query(id))
    .subscribeOn(Schedulers.boundedElastic()); // correct
```

---

**3. Reactive Pipeline Assembly Without Subscription**

**Symptom:** Handler method returns a `Mono` but nothing is executed; no database call, no log output, no response.

**Root Cause:** Reactive pipelines in Reactor are lazy — nothing executes until subscribed. If a pipeline is assembled but `subscribe()` is never called (which WebFlux does automatically, but manual code may forget), nothing happens.

**Diagnostic:**

```java
// BAD: pipeline assembled but not subscribed
// (common in fire-and-forget code)
@GetMapping("/process/{id}")
public Mono<Void> process(@PathVariable String id) {
    orderService.processAsync(id); // returns Mono, not subscribed!
    return Mono.empty(); // finishes without processing
}

// GOOD: subscribe or chain
@GetMapping("/process/{id}")
public Mono<Void> process(@PathVariable String id) {
    return orderService.processAsync(id); // WebFlux subscribes
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Non-blocking I/O` — NIO's Selector model is the hardware foundation that WebFlux's event loop is built on
- `Event Loop` — the scheduling pattern at the core of Netty that WebFlux runs on top of
- `Spring MVC` — understand the blocking model first to appreciate what WebFlux replaces and when each is appropriate

**Builds On This (learn these next):**

- `Mono / Flux` — the reactive types you work with in WebFlux; master these to be productive
- `Backpressure (Spring)` — the mechanism that prevents fast publishers from overwhelming slow consumers in a WebFlux pipeline
- `R2DBC` — the reactive JDBC replacement that enables fully non-blocking database access with WebFlux

**Alternatives / Comparisons:**

- `Spring MVC + Virtual Threads (Project Loom)` — Java 21's approach to same problem: synchronous code + no thread-per-request cost; simpler mental model than reactive
- `Vert.x` — event-loop based JVM framework; similar model to WebFlux but not Spring ecosystem
- `Node.js` — pioneered the event-loop model for web servers; WebFlux brings the same pattern to the JVM

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Non-blocking Spring web framework using   │
│              │ event-loop instead of thread-per-request  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Thread-per-request can't scale to         │
│ SOLVES       │ thousands of concurrent I/O operations    │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ NEVER block on event-loop threads;        │
│              │ use Schedulers.boundedElastic() for it    │
├──────────────┼───────────────────────────────────────────┤
│ RETURN TYPES │ Mono<T> = 0 or 1 element;                 │
│              │ Flux<T> = 0 or N elements                 │
├──────────────┼───────────────────────────────────────────┤
│ WHEN TO USE  │ High I/O concurrency, streaming, gateway  │
│ AVOID WHEN   │ CPU-bound, JDBC/ORM, team not in reactive │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ 10x concurrency density vs. harder code,  │
│              │ harder debugging, blocking library limits │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One event-loop chef managing 1000        │
│              │  burners beats 1000 blocking waiters"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mono/Flux → Backpressure → R2DBC         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE F — Comparison) Spring WebFlux and Java 21 Virtual Threads both claim to solve the "too many blocked threads" problem. A tech lead says "Virtual Threads are strictly better — same scalability, simpler code, no reactive overhead." Under what specific workload profile is this claim true? Under what specific workload does WebFlux still have a genuine advantage that Virtual Threads cannot match?

**Q2.** (TYPE D — Debugging) A WebFlux service starts handling requests normally but after 2 hours of production traffic, response times climb from 5ms to 45 seconds and new requests begin timing out. Thread dumps show all `reactor-http-nio` threads in `TIMED_WAITING` state. What is the most likely root cause? Walk through your exact diagnostic steps and the specific configuration change that would have prevented this scenario.
