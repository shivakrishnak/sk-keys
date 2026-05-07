---
layout: default
title: "Modular Monolith"
parent: "Microservices"
nav_order: 7
permalink: /microservices/modular-monolith/
number: "MSV-007"
category: Microservices
difficulty: ★★☆
depends_on: Monolith vs Microservices, Domain-Driven Design, Service Decomposition
used_by: Strangler Fig Pattern, Service Decomposition, API Gateway
related: Monolith vs Microservices, Bounded Context, Anti-Corruption Layer
tags:
  - microservices
  - architecture
  - pattern
  - intermediate
  - distributed
---

# MSV-007 — Modular Monolith

⚡ TL;DR — A modular monolith enforces strict module boundaries within a single deployable unit, giving you team autonomy without the operational cost of microservices.

| #627 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Domain-Driven Design, Service Decomposition | |
| **Used by:** | Strangler Fig Pattern, Service Decomposition, API Gateway | |
| **Related:** | Monolith vs Microservices, Bounded Context, Anti-Corruption Layer | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team migrated from a big ball of mud monolith to microservices to solve team autonomy. But now each of 20 engineers spends 30% of their day fighting infrastructure: running 15 Docker containers locally, debugging distributed traces for simple bugs, and waiting for the service mesh to be healthy in the staging environment. The operational overhead has actually slowed the team down — the pain switched from coupling to complexity.

**THE BREAKING POINT:**
You ask the team what the hardest part of their day is. The answer isn't "we can't deploy independently" — it is "I can't run the system locally in under 10 minutes." Microservices solved a scaling problem you don't have yet, but created an operational problem you have every day.

**THE INVENTION MOMENT:**
This is exactly why the Modular Monolith pattern was created — to draw strict, enforced module boundaries (with the same independence guarantees as microservices) while keeping a single deployment unit so you avoid all distributed systems overhead until you genuinely need it.

---

### 📘 Textbook Definition

A **Modular Monolith** is an application architecture where the codebase is partitioned into strongly-encapsulated, cohesive modules — each owning its own domain logic, data access, and public API surface — but the entire application is compiled and deployed as a single process. Modules communicate only through well-defined interfaces, not direct class references across boundaries, making future extraction into microservices straightforward.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One deployable app, but every feature lives in a locked compartment with a guarded entrance.

**One analogy:**
> A cruise ship has one hull (single deployment) but completely separate watertight compartments. If one compartment floods, the others are sealed off. You can navigate the whole ship from the bridge. A modular monolith gives you the same watertight isolatio — without needing a fleet of separate ships.

**One insight:**
The key distinction between a modular monolith and a microservices system is *where* the boundary is enforced: at compile-time/package level vs at the network level. A modular monolith enforces the same conceptual boundary with far less operational overhead.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each module has a single public API (a facade or interface) — all other types are package-private.
2. No module may directly reference another module's internal classes or database tables.
3. The entire application deploys and scales as one process, eliminating network overhead between modules.

**DERIVED DESIGN:**
Given Invariant 1, inter-module calls are routed through the facade only. This means if you want to extract the payments module into its own service, you already have a stable contract; just put an HTTP adapter on the facade. Given Invariant 2, you can change a module's internal data model without breaking anything outside it — the same isolation guarantee microservices provide, achieved at compile time.

The enforcement mechanism varies by language:
- **Java/Kotlin:** Java 9 module system (`module-info.java`), separate Maven/Gradle submodules, or Arch Unit tests.
- **TypeScript/Node:** separate `src/modules/` folders with barrel `index.ts` files and ESLint rules forbidding cross-module imports except through public index.
- **Python:** separate packages with explicit `__all__` exports.

**THE TRADE-OFFS:**
**Gain:** All the design benefits of modular decomposition (clear ownership, independent changeability) with monolith simplicity (single process, single DB transaction, easy local dev).
**Cost:** Still one deployment unit — so one bad memory leak can still take down all modules. Cannot use different technology stacks per module. Harder to scale individual modules independently under extreme load.

---

### 🧪 Thought Experiment

**SETUP:**
You have modules: `orders`, `payments`, `notifications`. In a modular monolith they are all in one JVM process but in separate Maven submodules with enforced boundaries.

**WHAT HAPPENS WITHOUT ENFORCEMENT:**
A developer adds `import com.payments.internal.PaymentRepository` directly into the `orders` module to "just get the data." Six months later, 47 classes in `orders` depend on `payments` internals. Extracting `payments` into a microservice requires rewriting half the `orders` module. The deadline slips by three sprints.

**WHAT HAPPENS WITH MODULAR MONOLITH BOUNDARIES:**
The `payments` module's `PaymentRepository` is in a package not visible outside the module. The developer's import fails to compile. They use `PaymentService.getPaymentStatus(orderId)` — the public API. When the payments module is extracted into a microservice, only the `PaymentService` interface needs an HTTP adapter. Migration takes two days.

**THE INSIGHT:**
Enforced boundaries now means cheap migration later. The modular monolith is not a compromise — it is a staging ground for future microservices, with all the painful design work already done.

---

### 🧠 Mental Model / Analogy

> Think of a government building with many departments (Tax, Licensing, Benefits). Each department has its own reception desk that citizens interact with. Staff in Tax cannot walk uninvited into the Benefits back office. All departments share the same building (process, infrastructure) but are operationally independent.

- "Separate departments" → separate modules with distinct bounded contexts
- "Reception desk" → the module's public API facade
- "Cannot enter the back office" → package-private internal classes, only public API is visible
- "Shared building" → single deployment unit, shared JVM heap

Where this analogy breaks down: unlike government departments, modules in a modular monolith can call each other synchronously without latency — there's no equivalent of "waiting for the other department to open."

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A modular monolith is a single application divided into clearly labelled sections where each section has rules about what it can share with others. It is one app, but the inside is organised like many mini-apps.

**Level 2 — How to use it (junior developer):**
Organise your code into top-level packages by business capability (`orders`, `payments`, `users`). Each package has a public-facing `service` or `facade` class. Never import a class from another module's sub-package directly. Write a test (ArchUnit or ESLint plugin) that fails the build if cross-module internal imports are detected.

**Level 3 — How it works (mid-level engineer):**
The Java 9 JPMS (`module-info.java`) is the strongest enforcement: it makes packages physically invisible across module boundaries unless explicitly exported. Alternatively, use separate Gradle sub-projects: `orders-api`, `orders-impl`. The `impl` module is never a compile dependency for other modules — only the `-api` jar is. This makes circular dependencies impossible at the build level. Each module may own a DB schema namespace (e.g., `orders.*` tables vs `payments.*` tables) even though both use the same physical database. Cross-module DB reads go through the module API, not direct SQL joins.

**Level 4 — Why it was designed this way (senior/staff):**
The modular monolith pattern was popularised by Sam Newman and Martin Fowler as a reaction to organisations adopting microservices prematurely. The key insight is that modular decomposition is about *design*, and microservices are about *deployment*. These are orthogonal concerns. You can have excellent modular design in a monolith, and terrible design in microservices (the "distributed monolith" anti-pattern). The modular monolith proves that team autonomy is achievable without network boundaries. When a module genuinely needs independent scaling or a different technology stack, extract it — the contract is already defined.

---

### ⚙️ How It Works (Mechanism)

**Module boundary enforcement with Maven multi-module:**

```
sk-ecommerce/
├── pom.xml (parent)
├── orders-api/          ← public interfaces only
│   └── OrderService.java   (interface)
├── orders-impl/         ← hidden implementation
│   ├── OrderServiceImpl.java
│   └── OrderRepository.java  (package-private, not visible outside)
├── payments-api/
│   └── PaymentService.java
└── app/                 ← assembles all modules
    └── pom.xml (depends on *-api modules + *-impl modules)
```

The `orders-impl` module depends on `payments-api` only — never on `payments-impl`. This is enforced by Maven dependency declarations.

**ArchUnit test to catch violations:**

```java
@Test
void modulesShouldOnlyCommunicateViaAPIs() {
    JavaClasses classes = new ClassFileImporter()
        .importPackages("com.example");

    noClasses()
        .that().resideInAPackage("..orders..")
        .should().dependOnClassesThat()
        .resideInAPackage("..payments.impl..")
        .check(classes);
    // Fails build if orders imports payments internals
}
```

**Data isolation within single DB:**

```sql
-- Each module owns its schema namespace
CREATE SCHEMA orders;
CREATE SCHEMA payments;

-- Orders module never queries payments tables directly
-- It calls PaymentService.getStatus(orderId) instead
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
HTTP Request → App Entry Point (Controller) → Orders Module API Facade ← YOU ARE HERE → Orders Domain Logic → Orders DB schema → Response

**INTER-MODULE FLOW:**
Orders Module needs payment status → calls `PaymentService.getStatus(orderId)` (in-process, ~50ns) → Payments Module reads its own DB → returns DTO to Orders Module → response composed

**FAILURE PATH:**
Orders module throws uncaught exception → exception propagates to app error handler → 500 returned to client → **other modules unaffected** (same process, but exception is caught at the controller boundary) → no cascading failure within transaction-scoped calls → database rollback if inside a transaction

**WHAT CHANGES AT SCALE:**
At 10x load, all modules share the single process's thread pool and heap. If one module leaks memory, all suffer — the shared-fate problem that microservices solve. At 100x, you can only scale the whole application horizontally, not individual modules. This is the signal to extract the hottest module into its own service.

---

### 💻 Code Example

**Example 1 — BAD: Direct cross-module import (tightly coupled monolith):**

```java
// BAD: orders module reaches into payments internals
// — creates hard coupling, prevents extraction
package com.example.orders.service;

import com.example.payments.impl.PaymentJpaRepository;  // VIOLATION

@Service
public class OrderService {
    @Autowired
    private PaymentJpaRepository paymentRepo; // wrong!

    public void placeOrder(Order order) {
        Payment p = paymentRepo.findByOrderId(order.getId());
        // ...
    }
}
```

**Example 2 — GOOD: Cross-module call via public API only:**

```java
// GOOD: orders depends only on payments public interface
package com.example.orders.service;

import com.example.payments.api.PaymentService; // only the API

@Service
public class OrderService {
    private final PaymentService paymentService;

    public void placeOrder(Order order) {
        PaymentStatus status =
            paymentService.getStatus(order.getId()); // clean API
        // ...
    }
}
```

**Example 3 — Module public API interface (payments-api module):**

```java
// payments-api module — only this jar is visible to other modules
package com.example.payments.api;

public interface PaymentService {
    PaymentStatus getStatus(long orderId);
    PaymentResult charge(long orderId, Money amount);
}

// All implementation details are in payments-impl — invisible outside
```

---

### ⚖️ Comparison Table

| Approach | Deployment | Team Autonomy | Operational Cost | Migration to MSvc |
|---|---|---|---|---|
| **Modular Monolith** | Single unit | High (module ownership) | Low | Easy — contracts pre-defined |
| Big Ball of Mud Monolith | Single unit | None | Low | Very hard |
| Microservices | Per service | Highest | High | N/A — already there |
| Serverless Functions | Per function | Highest | Medium | N/A |

How to choose: choose a modular monolith when team size is 10–50 and deployment independence is not yet a bottleneck; switch to microservices when specific modules need independent scale or different release cadences.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A modular monolith is just a well-organised monolith | No — the key requirement is *enforced* boundaries, not just folder organisation. Without enforcement, it reverts to a big ball of mud within months |
| You must use Java 9 modules to implement this | Any enforcement mechanism works: separate build modules, ArchUnit tests, ESLint plugins, package-private visibility conventions |
| A modular monolith cannot scale | It scales horizontally just like any monolith — all instances of the process scale together. Only *differential* scaling of individual modules is unavailable |
| Module boundaries in code = microservice boundaries | Not necessarily. Two closely collaborating modules may belong in one service; one module with extreme scaling needs becomes its own service |
| The modular monolith is a stepping stone, not a destination | For many teams it is the right permanent architecture — microservices complexity is never worth it unless the team and load genuinely demand it |

---

### 🚨 Failure Modes & Diagnosis

**1. Boundary Erosion Over Time**

**Symptom:** The architecture diagram still shows clean modules but engineers report needing to change 5 files across 3 modules to add one field.

**Root Cause:** Enforcement was neglected — internal classes were made public "just this once" and the pattern proliferated. No automated check exists.

**Diagnostic:**
```bash
# Run ArchUnit tests in CI — they will fail if violations exist
./mvnw test -pl architecture-tests
# or check import counts:
grep -rn "import com.example.payments.impl" \
  src/orders/  src/notifications/
```

**Fix:**
```java
// Add ArchUnit rule that runs in every build
@ArchTest
static final ArchRule noImplImports =
    noClasses()
        .that().resideOutsideOfPackage("..payments..")
        .should().dependOnClassesThat()
        .resideInAPackage("..payments.impl..");
```

**Prevention:** Wire ArchUnit or equivalent into CI from day one; treat boundary violations as build failures.

**2. Shared DB Coupling Between Modules**

**Symptom:** Changing the `payments.payment_methods` table requires updating the `orders` module too.

**Root Cause:** The `orders` module has SQL queries that directly JOIN the `payments` schema tables rather than using the PaymentService API.

**Diagnostic:**
```bash
# Search for cross-schema SQL references in order module
grep -rn "payments\." src/orders/ --include="*.java" \
  --include="*.xml" --include="*.sql"
```

**Fix:**
```java
// BAD: cross-module SQL join
String sql = "SELECT o.*, p.status FROM orders.orders o " +
             "JOIN payments.transactions p ON ..."; // coupling!

// GOOD: call the module API instead
PaymentStatus status = paymentService.getStatus(order.getId());
```

**Prevention:** Use separate DB schemas per module and enforce with DB access controls or schema-ownership conventions documented in ADRs.

**3. Premature Extraction into Microservices**

**Symptom:** A module was extracted into a microservice but it calls back into the monolith 5 times per request, adding 250ms of latency.

**Root Cause:** The extracted service was not truly independent — it had too many dependencies on other modules that remained in the monolith.

**Diagnostic:**
```bash
# Check inter-service call depth in traces
curl http://jaeger:16686/api/traces?service=extracted-service \
  | jq '.data[].spans | length'  # high span count = chatty
```

**Fix:** Before extracting, map all dependencies. A module ready to become a microservice should call back into the monolith in fewer than 2 synchronous hops per user-facing request.

**Prevention:** Use a dependency graph tool (e.g., Structure101, SonarQube module analysis) before extraction decisions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` — establishes the design space this pattern sits in the middle of
- `Domain-Driven Design` — module boundaries should follow bounded contexts from DDD
- `Service Decomposition` — the methodology for finding the right module splits

**Builds On This (learn these next):**
- `Strangler Fig Pattern` — the recommended migration path from modular monolith to microservices, service by service
- `Bounded Context` — the DDD concept that defines what belongs in each module
- `Anti-Corruption Layer` — a boundary-enforcing pattern used when integrating modules with legacy code

**Alternatives / Comparisons:**
- `Monolith vs Microservices` — the starting point and end point of the spectrum this pattern sits between
- `Microservices` — the next step when module independence at the process level becomes necessary

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single-deployable app with enforced       │
│              │ module boundaries — no cross-module       │
│              │ internal access allowed                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Premature microservices complexity for    │
│ SOLVES       │ teams that don't yet need it              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Modular design is about boundaries;       │
│              │ microservices are about deployment —      │
│              │ these are orthogonal concerns             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Team of 10–50, no extreme independent     │
│              │ scaling needs, want clean architecture    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Modules have genuinely different scale    │
│              │ needs (10x difference) or technology      │
│              │ requirements                              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Low ops cost + good design vs no          │
│              │ differential scaling or stack diversity   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Great design without the distributed     │
│              │  systems tax."                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Strangler Fig →         │
│              │ Service Decomposition                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your modular monolith has 12 modules. All is well for 18 months. Then the recommendation engine module starts consuming 80% of CPU during peak hours, starving the checkout module. The team proposes either extracting the recommendation engine into a microservice or scaling the whole monolith. What are the exact steps, trade-offs, and risks of each option, and what data would you gather before deciding?

**Q2.** Two engineers debate module granularity: one proposes splitting the `users` module into `user-profile`, `user-auth`, and `user-preferences` to match future microservice plans. The other argues this adds complexity without benefit today. At what point does further splitting within a modular monolith create more friction than it removes, and what measurable criteria should drive that decision?

