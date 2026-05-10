---
id: SPR-059
title: Spring Architecture at Scale
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-001, SPR-002, SPR-003, SPR-046, SPR-050
used_by:
related: SPR-060, SPR-061, SPR-063
tags:
  - spring
  - java
  - advanced
  - architecture
  - bestpractice
  - production
status: complete
version: 2
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /spr/spring-architecture-at-scale/
---

# SPR-059 - Spring Architecture at Scale

⚡ TL;DR - Scaling Spring means structuring modules, managing cross-cutting concerns centrally, and treating startup time, memory, and connection pool tuning as first-class design concerns.

| Field          | Value                                                                                                                                                                                                                             |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-001 - What Is Spring - History and Philosophy]], [[SPR-002 - The Spring Ecosystem Map]], [[SPR-003 - Why Spring Boot Changed Java Development]], [[SPR-046 - Spring Boot Startup Lifecycle]], [[SPR-050 - Spring Security]] |
| **Used by**    | -                                                                                                                                                                                                                                 |
| **Related**    | [[SPR-060 - Spring Migration Strategy (MVC → WebFlux)]], [[SPR-061 - Spring Boot Configuration Strategy]], [[SPR-063 - Microservice Decomposition with Spring Cloud]]                                                             |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Spring Boot monolith starts as a single well-structured application. After two years it has 800 classes, 40 developers, 200 beans, three `@Configuration` classes each with 50 `@Bean` methods, all mixing domain logic, infrastructure concerns, and cross-cutting plumbing into a single component scan boundary. Build time is 3 minutes. Tests share a single `@SpringBootTest` context that takes 45 seconds to start. Feature changes routinely cause unexpected failures in unrelated modules.

**THE BREAKING POINT:**

Scale in Spring is not about traffic - it is about _team scale_ and _code scale_. At 5 developers, a single monolith is fine. At 50 developers, the same monolith becomes a bottleneck: context loading time affects every developer's inner loop, circular dependencies become more frequent, and bean naming collisions cause subtle bugs.

**THE INVENTION MOMENT:**

The solution is applying _bounded contexts_ from Domain-Driven Design to the Spring container model: separate `ApplicationContext` hierarchies for each domain module, explicit public APIs between modules, shared contexts for infrastructure, and test slices that load only what each test needs.

**EVOLUTION:**

- **2012:** Spring modular applications emerge via `parent` and `child` `ApplicationContext` hierarchies
- **2016:** Spring modulith concept (before the library) - manual module boundaries via package conventions
- **2022:** Spring Modulith 1.0 GA - first-class support for modular Spring Boot applications with event-driven module boundaries and architectural verification tests

---

### 📘 Textbook Definition

**Spring Architecture at Scale** refers to the structural patterns and operational practices required when Spring Boot applications grow beyond a single-team, single-module scope. Key concerns include: **module boundaries** (preventing cross-domain coupling), **context hierarchy** (parent/child `ApplicationContext` for isolation), **platform starters** (shared infrastructure defaults), **test architecture** (sliced contexts for fast feedback), and **operational scale** (JVM tuning, connection pool sizing, memory per instance).

---

### ⏱️ Understand It in 30 Seconds

**One line:** At scale, Spring's default of "everything in one context" becomes a liability - bounded modules, shared infrastructure, and test slices restore control.

> A large Spring monolith without module boundaries is like a city that grew without zoning laws: everything works until the density creates gridlock. Module boundaries are the zoning laws.

**One insight:** The most impactful architectural change in a large Spring application is rarely technical - it is making implicit module boundaries explicit by enforcing package-level encapsulation and event-driven inter-module communication.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A single `ApplicationContext` is a flat namespace - every bean is visible to every other bean
2. Large flat namespaces produce accidental coupling over time
3. `ApplicationContext` hierarchies allow parent contexts (shared infra) and child contexts (isolated domains)
4. Cross-module calls should go through explicit interfaces, not direct bean injection
5. Test isolation requires loading only the beans relevant to the test

**DERIVED DESIGN:**

From invariants 1+2 → Spring Modulith enforces module boundaries at the package level; module-internal classes are inaccessible to other modules.
From invariant 3 → infrastructure beans (`DataSource`, `TransactionManager`, `SecurityFilterChain`) live in a shared parent context; domain modules load as child contexts.
From invariant 4 → `ApplicationEventPublisher` for cross-module communication without direct import dependencies.
From invariant 5 → `@WebMvcTest`, `@DataJpaTest`, `@ServiceTest` (custom slice) load only the relevant beans.

**THE TRADE-OFFS:**

**Gain:** Smaller test context startup times; clear module ownership; cross-module changes require explicit API decisions; easier parallel team development.

**Cost:** More upfront structure; event-driven inter-module communication is harder to trace than direct method calls; context hierarchies add configuration complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Large systems with many teams genuinely require separation of concerns at the module level.

**Accidental:** The need to manually configure parent/child context hierarchies is an accidental complexity Spring Modulith reduces.

---

### 🧪 Thought Experiment

**SETUP:** You have a 600-class Spring Boot application with Order, Payment, Inventory, and Notification domains, all in the same component scan.

**WHAT HAPPENS WITHOUT module boundaries:**

`OrderService` injects `NotificationService` directly. `InventoryService` injects `OrderRepository`. A change to `Order` affects `Notification`, `Inventory`, and `Payment` simultaneously. A test of `OrderService` must load all 600 beans. 8 teams make changes and every merge produces bean naming conflicts. Test suite takes 12 minutes to run.

**WHAT HAPPENS WITH module boundaries:**

Each domain has a public API (interface package) and private internals (impl package). `Order` module publishes `OrderPlacedEvent`. `Notification` and `Inventory` modules listen via `@EventListener`. No direct injection crosses module boundaries. `@DataJpaTest` for Order loads 40 beans, not 600. Test suite runs in 3 minutes. Teams deploy modules independently.

**THE INSIGHT:**

Module boundaries are not about microservices or different JVMs - they can exist within a single Spring Boot application. The boundary is enforced by access rules, not network calls. This is the Spring Modulith value proposition.

---

### 🧠 Mental Model / Analogy

> A large Spring application without module boundaries is a single large open-plan office where every desk can see every other desk. Module boundaries are the glass walls of individual meeting rooms: teams work in their own space, communicate through defined channels (doors / events), and share common facilities (kitchen / infrastructure context).

**Element mapping:**

- Open-plan office → single flat `ApplicationContext`
- Glass-walled meeting room → Spring Modulith module with package-private internals
- Shared kitchen → parent `ApplicationContext` (DataSource, Security, etc.)
- Door → module's public API (interface package)
- Internal meeting room conversations → module-internal bean interactions
- Intercom between rooms → `ApplicationEventPublisher`

Where this analogy breaks down: unlike office rooms, Spring Modulith modules share the same JVM thread pool and heap; isolation is logical, not physical.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a Spring app gets big, you need rules about which parts of the code can talk to which other parts. Without rules, everything gets tangled together. Spring at scale means adding those rules so that teams can work independently without constantly breaking each other.

**Level 2 - How to use it (junior developer):**
Use Spring Modulith: add `org.springframework.modulith:spring-modulith-starter-core`. Organise code into packages like `com.app.order`, `com.app.payment`. Make internal classes package-private. Only expose public interfaces. Use `ApplicationEventPublisher` for cross-module notifications. Run `ApplicationModules.of(App.class).verify()` in a test to enforce the rules.

**Level 3 - How it works (mid-level engineer):**
Spring Modulith uses Jdeps-style analysis to build a module graph from the classpath at test time. It detects when a class in `com.app.order.internal` is imported by `com.app.payment`. Module verification tests assert no cross-module internal dependencies exist. For runtime, Modulith's `@ApplicationModuleListener` wraps `@EventListener` with transactional publishing and optional async execution. It integrates with `spring-modulith-starter-jpa` to provide module-scoped event publication tables.

**Level 4 - Why it was designed this way (senior/staff):**
Spring Modulith deliberately chose package-based (not class-based or annotation-based) module boundaries because packages are the natural Java visibility scope. `package-private` classes are invisible outside the package without any framework involvement - the JVM enforces the boundary. The library _verifies_ boundaries at test time rather than _enforcing_ at runtime, which avoids adding runtime overhead while still catching violations before deployment. This is the same philosophy as ArchUnit: fail fast in tests, not in production.

**Expert Thinking Cues:**

- `@NamedInterface` in Modulith allows multiple public interfaces within a single package root
- `ApplicationModules.of(App.class).forEach(System.out::println)` shows the full detected module graph
- Modulith's event publication log table (`event_publication`) supports transactional outbox pattern

---

### ⚙️ How It Works (Mechanism)

```
[Spring Modulith Architecture]

  com.app
  ├── order/               ← Module: Order
  │   ├── OrderApi.java    (public - module boundary)
  │   ├── OrderPlacedEvent.java (public event)
  │   └── internal/
  │       ├── OrderService.java  (package-private)
  │       └── OrderRepository.java (package-private)
  │
  ├── payment/             ← Module: Payment
  │   ├── PaymentApi.java  (public)
  │   └── internal/
  │       └── PaymentService.java
  │
  └── notification/        ← Module: Notification
      └── internal/
          └── NotificationListener.java
              @ApplicationModuleListener
              void on(OrderPlacedEvent event) { ... }

[Verification Test]
  ApplicationModules.of(App.class).verify();
  // Fails if notification imports order.internal
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Order Module - OrderService]
     |
     ├─ Processes order business logic
     |        ← YOU ARE HERE
     ├─ Publishes OrderPlacedEvent via
     |    ApplicationEventPublisher
     |
[Spring Event Bus]
     ├─ Notification module listener fires
     |    (async, transactional)
     ├─ Inventory module listener fires
     |    (sync, same transaction)
     |
[Modulith Event Publication Log]
     └─ Records published event for
        reliability (outbox pattern)
```

**FAILURE PATH:**

- Cross-module internal import → `ApplicationModules.verify()` fails in CI (caught before deployment)
- Event listener throws → depends on `@ApplicationModuleListener` error handling; can be retried via publication log
- Circular module dependency → Modulith reports cycle in verification test

**WHAT CHANGES AT SCALE:**

At 100+ developers, Spring Modulith modules map to separate Git repositories (microservices) or separate Maven/Gradle sub-modules with explicit `api` and `impl` source sets. The same principles (public API packages, event-driven cross-module communication) apply whether modules are in one JVM or many.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**

Event-driven module communication via `@ApplicationModuleListener(async = true)` uses a shared thread pool. Under high load, a slow notification module can exhaust the pool and delay order module processing. Use separate thread pool executors (`@Async` with dedicated `Executor` beans) per domain when async throughput must be isolated.

---

### 💻 Code Example

**BAD - direct cross-module internal coupling:**

```java
// payment module directly importing order internals
import com.app.order.internal.OrderRepository; // VIOLATION

@Service
public class PaymentService {
    // Breaks module boundary: accesses internal
    private final OrderRepository orderRepo;

    public void pay(Long orderId) {
        Order o = orderRepo.findById(orderId)
            .orElseThrow();
        // ...
    }
}
```

**GOOD - event-driven decoupling through module API:**

```java
// order/OrderApi.java (public module API)
public interface OrderApi {
    Optional<OrderSummary> findById(Long id);
}

// order/OrderPlacedEvent.java (public event)
public record OrderPlacedEvent(Long orderId,
    BigDecimal amount) {}

// payment/internal/PaymentService.java
@ApplicationModuleListener
void handleOrderPlaced(OrderPlacedEvent event) {
    processPayment(event.orderId(),
        event.amount());
}
```

**How to test / verify correctness:**

```java
// Architectural verification - runs in CI
@Test
void moduleStructureIsValid() {
    ApplicationModules.of(App.class).verify();
}

// Scenario test across module boundary
@ApplicationModuleTest
class OrderScenarioTest {
    @Test
    void orderPlaced_triggersPaymentAndNotification(
            Scenario scenario) {
        scenario.stimulate(orderApi ->
                orderApi.placeOrder(new PlaceOrderCmd()))
            .andWaitForEventOfType(
                OrderPlacedEvent.class)
            .toComplete()
            .andVerify(event ->
                assertThat(event.orderId())
                    .isNotNull());
    }
}
```

---

### ⚖️ Comparison Table

| Approach                          | Team Scale  | Deployment           | Coupling               | Complexity  |
| --------------------------------- | ----------- | -------------------- | ---------------------- | ----------- |
| Flat monolith (no modules)        | 1-5 devs    | Single JAR           | High over time         | Low         |
| Spring Modulith (logical modules) | 5-50 devs   | Single JAR           | Low (enforced)         | Medium      |
| Maven/Gradle multi-module         | 20-100 devs | Multi-JAR monolith   | Low (build boundary)   | Medium-High |
| Microservices                     | 50+ devs    | Separate deployments | Low (network boundary) | High        |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                               |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| "At scale you must use microservices"                          | Spring Modulith enables modular monoliths that provide most team-scale benefits without distributed systems complexity.                               |
| "Module boundaries require separate JVMs"                      | Package-based access control enforced at test time is sufficient for logical module separation in a single JVM.                                       |
| "Events are always better than direct calls"                   | Events introduce asynchrony and ordering complexity. Use direct calls for commands with a response; events for notifications with no response needed. |
| "Parent/child ApplicationContext hierarchies are the standard" | Context hierarchies are complex to configure and maintain. Spring Modulith's package-based approach is simpler and recommended for new applications.  |
| "Scale means more instances, not better structure"             | Horizontal scaling fixes traffic scale. Code structure fixes team scale. They are different problems.                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Module boundary violation accumulates undetected**

**Symptom:** `order` module changes break `payment` module builds or tests unexpectedly.

**Root Cause:** Cross-module internal imports crept in without enforcement.

**Diagnostic:**

```java
// Add this test - it will fail if violations exist
@Test
void verifyModularity() {
    ApplicationModules.of(App.class).verify();
}
// Output shows violating imports:
// "Module 'payment' depends on internal type
//  'com.app.order.internal.OrderRepository'"
```

**Fix:** Replace direct internal import with module public API or event.

**Prevention:** Run `verify()` in CI as a gating test; treat it as an architecture linting step.

---

**Mode 2: Event listener overloads shared thread pool**

**Symptom:** Under load, `@ApplicationModuleListener(async=true)` events are delayed by seconds; order processing latency spikes.

**Root Cause:** All async listeners share the Spring default `SimpleAsyncTaskExecutor` with no thread limit.

**Diagnostic:**

```bash
curl http://localhost:8080/actuator/metrics/\
executor.active?tag=name:applicationTaskExecutor
# High active thread count relative to pool size
```

**Fix:**

```java
@Bean("notificationExecutor")
public Executor notificationExecutor() {
    ThreadPoolTaskExecutor exec =
        new ThreadPoolTaskExecutor();
    exec.setCorePoolSize(5);
    exec.setMaxPoolSize(20);
    exec.setQueueCapacity(100);
    return exec;
}
```

**Prevention:** Define named executors per domain; monitor thread pool queue depth with Micrometer alerts.

---

**Mode 3: Internal module beans accessible via reflection (Security failure mode)**

**Symptom:** A test or external code instantiates a module-internal class directly via `ApplicationContext.getBean()`, bypassing module API.

**Root Cause:** `package-private` access control only affects compile-time; Spring's `ApplicationContext` can still expose all beans by type regardless of visibility.

**Diagnostic:**

```java
// This will succeed even for package-private beans:
ctx.getBean(OrderRepository.class); // accessible!
```

**Fix:** Use `@ApplicationModuleTest` which scopes the context to the module's public API. Do not expose internal beans via `@Primary` or explicit `@Bean` methods in shared configuration.

**Prevention:** Add ArchUnit rules asserting that internal packages are not referenced from outside the module in production code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-001 - What Is Spring - History and Philosophy]] - the container model being structured
- [[SPR-046 - Spring Boot Startup Lifecycle]] - what is being optimised for large apps
- [[SPR-021 - ApplicationContext]] - the container that module boundaries partition

**Builds On This (learn these next):**

- [[SPR-063 - Microservice Decomposition with Spring Cloud]] - when modules need network boundaries
- [[SPR-061 - Spring Boot Configuration Strategy]] - managing config at module scale
- [[SPR-060 - Spring Migration Strategy (MVC → WebFlux)]] - architecture migration patterns

**Alternatives / Comparisons:**

- ArchUnit - test-time architecture enforcement (complements Modulith)
- Hexagonal Architecture (Ports & Adapters) - alternative structural pattern for module isolation
- Jakarta EE CDI Alternatives - `@Alternative` beans for module-level substitution

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Structural patterns for large Spring apps |
| PROBLEM       | Accidental coupling as team + code scales |
| KEY INSIGHT   | Module boundaries = package visibility +  |
|               | event-driven communication               |
| USE WHEN      | >5 developers; >200 beans; multiple teams |
| AVOID WHEN    | Small single-team apps (adds overhead)    |
| TRADE-OFF     | Structure overhead vs coupling prevention |
| ONE-LINER     | Spring Modulith: bounded contexts in one  |
|               | JAR with enforced access rules            |
| NEXT EXPLORE  | SPR-063 (Spring Cloud), SPR-061 (Config)  |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Package-private visibility + `ApplicationModules.verify()` enforces module boundaries without microservices overhead
2. `ApplicationEventPublisher` is the module-to-module communication channel; direct injection across modules is the anti-pattern
3. Test slices (`@WebMvcTest`, `@DataJpaTest`) and `@ApplicationModuleTest` are the key to keeping test feedback fast at scale

**Interview one-liner:** "Spring at scale means enforcing module boundaries via package visibility and event-driven communication, verified by Spring Modulith's architecture tests, to prevent accidental coupling as codebases and teams grow."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Explicit boundaries prevent implicit coupling._ Whether you use packages, modules, services, or namespaces, the pattern is the same: clearly define what is public, test the boundary exists, and route cross-boundary communication through explicit channels.

**Where else this pattern appears:**

- **Java Platform Module System (JPMS)** - `module-info.java` enforces the same public/private boundary at the JVM level for library authors
- **Nx monorepo tooling** - enforces library boundaries in TypeScript/JavaScript monorepos with lint rules
- **Go packages** - capitalisation is the visibility boundary; unexported symbols are the module internals

---

### 💡 The Surprising Truth

Spring Modulith's architectural verification test (`ApplicationModules.of(App.class).verify()`) runs in under 200 milliseconds regardless of application size - it analyses bytecode, not the running application. This means you can enforce strict architectural rules on a 500,000-line codebase in the same time it takes to blink. The cost of not enforcing those rules is not measured in milliseconds - a single cross-module coupling that survives for six months can cost weeks of untangling during the next major refactor.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** Spring Modulith's event-driven inter-module communication uses the transactional outbox pattern via the `event_publication` table. What happens to events published inside a transaction that rolls back, and how does Modulith's design prevent ghost notifications?

_Hint:_ Look at how `ApplicationEventPublisher.publishEvent()` behaves within `@Transactional` methods - specifically whether the event is dispatched before or after the transaction commits.

**Question 2 (B - Scale):** At what point does a Spring Modulith modular monolith justify being split into actual microservices, and what signals in the module's operational metrics should trigger that decision?

_Hint:_ Consider independent deployability requirements, team autonomy, traffic scaling needs per module, and database ownership in [[SPR-063 - Microservice Decomposition with Spring Cloud]].

**Question 3 (C - Design Trade-off):** Spring Modulith uses package-based boundaries but the JVM's `ApplicationContext` can still access package-private beans at runtime. Compared to Java 9+ JPMS strong encapsulation, what are the security and encapsulation implications of Modulith's test-time-only enforcement model?

_Hint:_ Think about what a compromised dependency could do with reflective `ApplicationContext.getBean()` access in a Modulith application vs a JPMS-modularised application.
