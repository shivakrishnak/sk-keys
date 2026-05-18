---
id: DPT-016
title: Facade
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-012
used_by: DPT-064, DPT-042
related: DPT-012, DPT-015, DPT-018, DPT-038
tags:
  - pattern
  - structural
  - intermediate
  - architecture
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/design-patterns/facade/
---

⚡ TL;DR - Facade provides a simplified interface to a
complex subsystem - shielding clients from subsystem
complexity and reducing coupling between clients and the
subsystem's internal structure.

| #16 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-012 | |
| **Used by:** | DPT-064, DPT-042 | |
| **Related:** | DPT-012, DPT-015, DPT-018, DPT-038 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order fulfillment system must coordinate: inventory
reservation, payment processing, shipping carrier selection,
notification sending, audit log writing, and warehouse
job scheduling. Each of these is a separate service with
its own API. The checkout controller must know and directly
call all six services in the correct sequence, handling
each one's exceptions, and rolling back correctly if any
step fails.

**THE BREAKING POINT:**
The checkout controller has 150 lines of coordination
logic. Testing it requires mocking all six services.
A new "express checkout" feature needs the same
coordination with slight variations - the developer
duplicates 150 lines. The subsystem APIs change
independently; every change may require updating the
controller. The controller is tightly coupled to the
internal structure of the entire subsystem.

**THE INVENTION MOMENT:**
Facade: create one `OrderFacade` class that knows how to
coordinate the six services to fulfill an order. The
checkout controller calls `orderFacade.placeOrder(order)`.
The facade handles the coordination, sequence, error
handling, and rollback internally. The controller does
not know the subsystem exists.

**EVOLUTION:**
Facade is one of the most universally applied patterns.
Every "service" in a microservices system is a Facade:
it provides a simplified API over internal complexity.
Spring's `JdbcTemplate` is a Facade over JDBC's verbose
API. Spring Data Repository is a Facade over JPA. AWS SDK's
high-level APIs (S3TransferManager, DynamoDBMapper) are
Facades over the low-level SDK.

---

### 📘 Textbook Definition

The **Facade** pattern is a Structural design pattern that
provides a simplified interface to a library, framework,
or complex subsystem. A Facade is a class that aggregates
the complex functionality of the subsystem and exposes a
small, focused interface for common use cases. Clients
use the Facade rather than calling subsystem classes
directly, reducing the number of objects clients interact
with and making the subsystem easier to use. The subsystem
classes remain accessible directly for clients needing
advanced functionality.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Facade is a "simple front door" to a complex building -
one interface, many rooms hidden behind it.

**One analogy:**
> A hotel concierge (Facade). Guests ask "I need a taxi
> to the airport at 6am." The concierge calls the car
> service, books the wake-up call, arranges the luggage
> porter, charges the room. Guests interact with ONE person;
> all the hotel subsystems are hidden behind that one interface.

**One insight:**
Facade's value is not just simplification - it is
DECOUPLING. The client does not know WHICH subsystems
exist, so it does not need to change when subsystems
change internally. Facade is the pattern that makes
refactoring subsystems safe.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Facade does not ADD behavior - it ORCHESTRATES existing
   subsystem behavior to fulfill high-level requests.
2. Facade does not HIDE the subsystem - it provides a
   simpler path. Advanced clients can still use subsystem
   classes directly.
3. Facade depends on subsystem classes; subsystem classes
   do NOT depend on Facade (dependency direction matters).

**DERIVED DESIGN:**
Two participants:
- **Facade**: the simplified interface; knows the subsystem;
  orchestrates subsystem calls
- **Subsystem classes**: the existing complex classes;
  they implement the actual functionality; they do not
  know the Facade exists

**LAYERING:**
Multiple Facades can coexist for different use cases:
a `SimpleFacade` for common operations, an `AdminFacade`
for administration operations. Facades can have facades:
`OrderFacade` uses `InventoryFacade` which uses the raw
inventory subsystem.

**TRADE-OFFS:**

**Gain:** Decoupling. Simplified API for common use cases.
Enables independent subsystem refactoring. Reduces
cognitive load for new developers.

**Cost:** Facade may become a "God object" if it accumulates
too many responsibilities. Facade adds a layer of indirection
for clients that need fine-grained subsystem control.
If Facade is poorly designed, subsystem changes may still
propagate to client code through Facade's interface.

---

### 🧪 Thought Experiment

**SETUP:**
A mobile app must display a product page: load product
details, check inventory, load user reviews, compute
price with discounts. Each is a separate API call. Without
Facade, the mobile client makes 4 API calls and assembles
the result. Network latency x4. Complex client-side
error handling.

**WHAT HAPPENS WITHOUT FACADE:**
Mobile client: call ProductService, call InventoryService,
call ReviewService, call PricingService. Handle timeouts
and errors for each. 4x network round trips. Version 2
of any service changes the mobile app's code. Testing
the mobile app requires mocking 4 services.

**WHAT HAPPENS WITH FACADE:**
`ProductPageFacade.getProductPage(productId, userId)`:
calls all 4 services in parallel, assembles result,
handles partial failures gracefully. Mobile client makes
ONE API call, receives ONE assembled response. Subsystem
changes happen in the facade; mobile app is unchanged.

**THE INSIGHT:**
The facade is also the natural place to add client-specific
orchestration (parallelism, circuit breaking, caching)
that is inappropriate to put in individual subsystem
services.

---

### 🧠 Mental Model / Analogy

> Facade is a REMOTE CONTROL for a home theater. The theater
> has a projector, speakers, receiver, streaming box,
> lighting, and screen controller - six separate systems.
> The remote has one "Movie Mode" button: it dims the
> lights, lowers the screen, turns on the projector and
> receiver, selects HDMI-2, adjusts speaker volume. One
> button, six coordinated actions.

- "Movie Mode button" = Facade interface
- "Six systems" = subsystem classes
- "Remote control" = Facade class
- "Advanced users with separate remotes" = clients who
  bypass Facade for direct subsystem access

**Where this analogy breaks down:**
A physical remote control is a "one-size-fits-all" device.
A Facade can be designed to take parameters and orchestrate
differently based on context. Facades can be composed,
layered, and specialized.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Facade gives you one simple function to call that does
a lot of complicated things behind the scenes. You do
not need to know all the steps; you just ask the facade
and it coordinates everything.

**Level 2 - How to use it (junior developer):**
Identify the complex subsystem (multiple classes to
coordinate). Create a new class with methods that express
what clients actually WANT (high-level operations).
Inside each method, call the subsystem classes in the
right order with the right parameters. Clients inject
the Facade, not the subsystem classes.

**Level 3 - How it works (mid-level engineer):**
Facade is the simplest of the Structural patterns: it
is literally a class that wraps a set of other classes
and calls them in a sequence. The pattern's value is
entirely in the design decision: where to draw the
boundary between what clients need to know and what
the facade absorbs. `JdbcTemplate.queryForList(sql)` is
a 3-line method call; the underlying JDBC code requires
15+ lines (Connection, PreparedStatement, ResultSet,
exception handling, resource cleanup). JdbcTemplate IS
a Facade for that complexity.

**Level 4 - Why it was designed this way (senior/staff):**
Facade enables the Dependency Inversion Principle at the
system level: high-level modules (checkout controller)
depend on an abstraction (OrderFacade interface); low-level
subsystems are behind the facade. When subsystems are
refactored (inventory moves from SQL to Kafka-backed
CQRS), only the Facade implementation changes. All
high-level clients are unaffected. Facade is the DIP
applied to subsystem integration.

**Level 5 - Mastery (distinguished engineer):**
In microservices, the Backend for Frontend (BFF) pattern
IS the Facade pattern applied at the service level: a
BFF service aggregates multiple microservice calls to
provide a mobile-optimized API. The BFF is a Facade;
the downstream microservices are the subsystem. Each
client type (mobile, web, partner API) may have its
own BFF Facade with appropriate aggregation, field
selection, and protocol optimization. GraphQL resolvers
are Facades: a single GraphQL query is resolved by
orchestrating multiple downstream service calls. The
resolver IS the Facade.

---

### ⚙️ How It Works (Mechanism)

```
Facade Structure
┌────────────────────────────────────────────────────────┐
│  Client                                                │
│    → facade.placeOrder(order)                          │
│                                                        │
│  OrderFacade                   ← the FACADE            │
│    + placeOrder(order): Result                         │
│        inventory.reserve(order)   → InventoryService   │
│        payment.charge(order)      → PaymentService     │
│        shipping.schedule(order)   → ShippingService    │
│        notify.sendConfirmation()  → NotificationService│
│        audit.log(order, SUCCESS)  → AuditService       │
│        return result                                   │
│                                                        │
│  Subsystem Classes (clients don't know these exist):  │
│  InventoryService  PaymentService  ShippingService     │
│  NotificationService  AuditService                     │
│                                                        │
│  Note: Subsystems do NOT reference OrderFacade         │
│  Dependency direction: Facade → Subsystems only        │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client calls facade.placeOrder(order)
  → Facade: reserve inventory
  → Facade: charge payment
  → Facade: schedule shipping (parallel with next two)
  → Facade: send confirmation
  → Facade: write audit log
  ← Facade returns success result
Client receives one response object
```

**FAILURE PATH:**
```
Payment charge fails:
  → Facade catches PaymentException
  → Facade rolls back inventory reservation
  → Facade records failed attempt in audit
  → Facade returns OrderResult.PAYMENT_FAILED
  ← Client receives structured failure result
Client handles OrderResult type; never sees
  PaymentException
```

**WHAT CHANGES AT SCALE:**
At scale, Facade orchestration may introduce latency if
calls are sequential. Solution: parallel calls for
independent subsystems. Resilience4j CircuitBreaker in
the Facade prevents one slow subsystem from blocking
the others. Caching in the Facade (read-path only) can
absorb subsystem load.

---

### 💻 Code Example

**Example 1 - Without Facade (controller knows everything):**

```java
// BAD: controller coupled to all subsystem internals
@PostMapping("/checkout")
ResponseEntity<OrderResult> checkout(Order order) {
    // Step 1: inventory
    boolean reserved = inventoryService.reserve(
        order.items(), order.warehouseId());
    if (!reserved)
        return ResponseEntity.ok(OrderResult.OUT_OF_STOCK);

    // Step 2: payment
    try {
        paymentService.charge(
            order.customerId(), order.total(),
            order.currency(), order.paymentToken());
    } catch (PaymentException e) {
        inventoryService.release(order.items());  // rollback
        return ResponseEntity.ok(OrderResult.PAYMENT_FAILED);
    }
    // Steps 3-5: shipping, notification, audit
    // ... 80 more lines
    return ResponseEntity.ok(OrderResult.success());
}
// Adding express checkout: must duplicate all 100 lines
// Changing InventoryService API: must change controller
```

**Example 2 - Facade solution:**

```java
// GOOD: Facade encapsulates all orchestration

@Service
class OrderFacade {
    private final InventoryService inventory;
    private final PaymentService payment;
    private final ShippingService shipping;
    private final NotificationService notify;
    private final AuditService audit;

    // Constructor injection...

    public OrderResult placeOrder(Order order) {
        // 1. Reserve inventory
        if (!inventory.reserve(order.items())) {
            return OrderResult.OUT_OF_STOCK;
        }

        // 2. Charge payment - rollback on failure
        try {
            payment.charge(order);
        } catch (PaymentException e) {
            inventory.release(order.items()); // compensate
            audit.log(order, "PAYMENT_FAILED");
            return OrderResult.PAYMENT_FAILED;
        }

        // 3. Fulfill (can be async/parallel)
        shipping.schedule(order);
        notify.sendConfirmation(order);
        audit.log(order, "SUCCESS");
        return OrderResult.success(order.id());
    }
}

// Controller: knows nothing about subsystems
@PostMapping("/checkout")
ResponseEntity<OrderResult> checkout(Order order) {
    // One line - all complexity in facade
    return ResponseEntity.ok(orderFacade.placeOrder(order));
}

// Express checkout: same facade, different parameters
@PostMapping("/express-checkout")
ResponseEntity<OrderResult> express(Order order) {
    order = order.withExpressShipping();
    return ResponseEntity.ok(orderFacade.placeOrder(order));
}
```

**Example 3 - Spring JdbcTemplate as canonical Facade:**

```java
// RECOGNITION: JdbcTemplate IS a Facade over JDBC

// Without Facade (raw JDBC - 15+ lines):
Connection conn = dataSource.getConnection();
PreparedStatement ps = null;
try {
    ps = conn.prepareStatement(
        "SELECT * FROM users WHERE id = ?");
    ps.setInt(1, userId);
    ResultSet rs = ps.executeQuery();
    List<User> users = new ArrayList<>();
    while (rs.next()) {
        users.add(mapRow(rs));
    }
    return users;
} catch (SQLException e) {
    throw new RuntimeException(e);
} finally {
    if (ps != null) ps.close();
    conn.close();
}

// With Facade (JdbcTemplate - 3 lines):
return jdbcTemplate.query(
    "SELECT * FROM users WHERE id = ?",
    (rs, row) -> mapRow(rs),
    userId);
// JdbcTemplate handles connection, PreparedStatement,
// ResultSet iteration, exception translation, resource cleanup
```

**How to test/verify correctness:**
Test the Facade by mocking all subsystem services - verify
the correct subsystem methods are called in the correct
order with the correct arguments. Test rollback paths:
when step N fails, verify steps 1..N-1 are compensated.
Test the Facade interface with integration tests
separately from subsystem unit tests.

---

### ⚖️ Comparison Table

| Pattern      | Wraps      | Simplifies | New interface? | Access to internals |
| ------------ | ---------- | ---------- | -------------- | ------------------- |
| **Facade**   | Subsystem  | Yes        | Yes (simpler)  | Still available     |
| Adapter      | One class  | No         | Yes (different)| Loses Adaptee API   |
| Proxy        | One class  | No         | No (same)      | Controlled by Proxy |
| Mediator     | Interaction| No         | Yes (central)  | Peers talk to medi. |

**How to choose:**
- Simplify a complex SUBSYSTEM with a new interface? Facade
- Convert one incompatible interface to another? Adapter
- Control access to one object? Proxy
- Decouple many objects from knowing each other? Mediator

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Facade prevents direct access to subsystem | Facade does NOT prevent direct access - it provides a simpler path for common use cases; advanced clients may still use subsystem classes directly |
| Facade is the same as Adapter | Adapter converts ONE interface to another; Facade provides a SIMPLER interface over MULTIPLE classes in a subsystem |
| Facade must be a single class | Multiple Facades for the same subsystem are valid (SimpleFacade, AdminFacade, TestFacade); Facades can be interfaces with multiple implementations |
| Service classes in Spring are not Facades | Spring Service classes that orchestrate multiple repositories or external calls ARE Facade implementations - the pattern is extremely common in Spring applications |
| Facade hides subsystem bugs | Facade orchestrates; it does not hide bugs. If a subsystem throws an exception, the Facade must handle it - wrapping it in a cleaner exception is appropriate, swallowing it is not |

---

### 🚨 Failure Modes & Diagnosis

**God Facade - Facade Accumulates Everything**

**Symptom:**
The `OrderFacade` starts with order placement. Over two
years, order status checks, refunds, fraud detection,
subscription renewals, and coupon redemption are added.
The Facade is 1,500 lines, has 40 methods, and 12
injected dependencies. New developers cannot understand
it; every feature request touches it.

**Root Cause:**
Facade did not have a defined boundary. Any "orchestration"
code landed in the one Facade. The Facade became a God
Object.

**Diagnostic Signal:**
Facade class > 500 lines, > 6 injected dependencies,
> 10 public methods. Method names cover unrelated domains.

**Fix:**
Split the Facade: `OrderPlacementFacade`, `OrderManagementFacade`,
`OrderRefundFacade`. Each has a single cohesive
responsibility. Existing callers: update injection to
use the specific facade they need.

**Prevention:**
Define the Facade's responsibility before writing it.
Name it specifically: `OrderFulfillmentFacade`, not
`OrderFacade`. When a new unrelated operation is requested,
create a NEW Facade rather than extending the existing one.

---

**Facade Interface Leaks Subsystem Details**

**Symptom:**
`OrderFacade.placeOrder(order)` returns
`InventoryReservationId` (an internal subsystem object).
Clients must import and use `InventoryReservationId` even
though the facade was supposed to hide the inventory system.
When the inventory system is replaced, `InventoryReservationId`
changes, breaking client code.

**Root Cause:**
Facade method signatures expose subsystem types rather
than facade-level domain types.

**Diagnostic Signal:**
Import statements in Facade clients reference subsystem
packages (e.g., `import com.company.inventory.*` in the
checkout controller).

**Fix:**
Replace subsystem types in Facade's API with facade-level
types:
```java
// BAD: leaks subsystem type
InventoryReservationId placeOrder(Order order);

// GOOD: facade-level type
OrderResult placeOrder(Order order);
// OrderResult is defined in the facade's package
```

**Prevention:**
Facade method signatures should use only types from the
facade's own package or from the domain model. If a
subsystem class appears in a Facade's public API: it is
a leakage candidate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Adapter` - related structural pattern; understanding
  Adapter's single-class wrapping vs Facade's subsystem
  wrapping is the key distinction

**Builds On This (learn these next):**
- `Mediator` - related pattern for object interaction
  decoupling; where Facade simplifies CLIENT-TO-SUBSYSTEM
  communication, Mediator simplifies OBJECT-TO-OBJECT
  communication within a subsystem
- `Service Locator` - an alternative orchestration approach
  with different trade-offs; often confused with Facade

**Alternatives / Comparisons:**
- `Adapter` - converts one interface; Facade simplifies
  many interfaces
- `Mediator` - centralizes communication between peers;
  Facade simplifies client access to a subsystem

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Simplified interface to a complex        │
│              │ subsystem; one door, many rooms behind   │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Clients coupled to all subsystem         │
│ SOLVES       │ internals; high-level operations require │
│              │ manual coordination of many classes      │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ Subsystem classes do NOT know the Facade │
│              │ (dependency goes Facade → Subsystem only)│
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ God Facade: all orchestration lands in   │
│              │ one class - split by responsibility      │
├──────────────┼──────────────────────────────────────────┤
│ VS ADAPTER   │ Adapter: wraps ONE class, converts iface │
│              │ Facade: wraps SYSTEM, simplifies API     │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ JdbcTemplate (Facade over JDBC),         │
│              │ Spring Data Repository, AWS TransferMgr  │
├──────────────┼──────────────────────────────────────────┤
│ IN MICRO.SVC │ BFF (Backend for Frontend) = Facade      │
│              │ GraphQL resolvers = Facade               │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Flyweight → Proxy → Mediator             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Facade provides a simpler interface to a SYSTEM (multiple
   classes); Adapter converts ONE interface to another -
   this is the core distinction
2. Dependency direction is ONE-WAY: Facade knows the
   subsystem; the subsystem does NOT know the Facade.
   Any reverse dependency is a design error
3. `JdbcTemplate` IS a Facade: it converts 15+ lines of
   raw JDBC into 3-line template calls - the most-used
   Facade in Java enterprise applications

**Interview one-liner:**
"Facade provides a simplified interface to a complex subsystem,
shielding clients from internal complexity. JdbcTemplate
is the canonical Java example: it reduces 15+ lines of
JDBC boilerplate to 3-line template calls. Spring Service
classes that orchestrate repositories and external APIs
are Facade implementations. BFF (Backend for Frontend)
microservices are Facade at the service level."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define your application's boundaries by what clients
NEED to express, not by what subsystems happen to provide.
The Facade interface is the specification of client intent;
the subsystem is the implementation detail. When the
client interface and subsystem interface diverge, Facade
is the correct bridging mechanism.

**Where else this pattern appears:**
- **Backend for Frontend (BFF)** - a microservice that
  aggregates multiple downstream service calls for one
  client type (mobile, web); the BFF IS the Facade
- **AWS SDK high-level APIs** - `S3TransferManager` (Facade
  over low-level S3 transfer operations with multipart
  upload, retry, progress tracking), `DynamoDBMapper`
  (Facade over DynamoDB low-level API with object mapping)
- **Spring's RestTemplate and WebClient** - Facades over
  Java's `HttpURLConnection` / Reactor Netty with simplified
  request building, response mapping, and error handling

**Industry applications:**
- **GraphQL layer** - a GraphQL schema resolver is a Facade:
  one query, one resolver, N downstream service calls
  aggregated and returned as a single structured response
- **Domain Anti-Corruption Layer** - in DDD, the
  Anti-Corruption Layer IS a Facade: it provides the
  domain model's clean interface over the legacy system's
  messy API

---

### 💡 The Surprising Truth

The most famous Facade in Java is so commonly used that
virtually no one calls it a pattern: `System.out.println()`.
`System.out` is a `PrintStream`. `PrintStream` is a Facade
over OutputStreams, buffering, character encoding, newline
handling, and flush semantics. `println()` is a Facade
method that calls `print(x)` which calls `String.valueOf(x)`,
which calls `toCharArray()`, which calls `write(char[])`,
which calls the underlying `OutputStream.write(byte[])`.
Five layers of complexity behind one method call. Every
Java programmer's first program (`Hello World`) uses a
Facade without knowing it. This illustrates Facade's
fundamental value: profound complexity made trivially
simple for the common case.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] State the difference between Facade and
   Adapter in one sentence: Facade wraps a SYSTEM
   (multiple classes); Adapter wraps ONE class to change
   its interface
2. [IDENTIFY] Recognize `JdbcTemplate`, Spring Data
   Repository, and RestTemplate as Facade implementations -
   state what "complex subsystem" each one hides
3. [DESIGN] Sketch an `OrderFulfillmentFacade` for an
   e-commerce system with inventory, payment, shipping,
   notification, and audit subsystems - include the
   rollback path when payment fails
4. [DIAGNOSE] Given an `OrderFacade` that has grown to
   1,500 lines and 40 methods covering orders, refunds,
   subscriptions, and fraud - identify the anti-pattern
   and sketch the split into cohesive smaller facades
5. [APPLY] Explain why Backend for Frontend (BFF) in
   microservices is the Facade pattern applied at the
   service level - naming the Facade, the subsystem
   classes, and the client

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `JdbcTemplate` is a Facade over JDBC.
But Spring also provides `NamedParameterJdbcTemplate` which
is a Facade over `JdbcTemplate`. This is a "layered facade."
Is this a design smell (too many layers) or is it justified?
What principle determines when layering facades is correct?

*Hint: `NamedParameterJdbcTemplate` solves a specific
problem (`?`-positional parameters vs :name-named params)
that JdbcTemplate does not solve. The layer is justified
because it addresses a NEW CONCERN on top of an existing
facade. The principle: each facade layer should address
exactly ONE additional concern or simplification. If the
new layer addresses the same concern as the existing one
(just differently), it is redundant. If it addresses a
new concern, it is justified.*

**Q2.** A team says: "Our OrderFacade should return raw
domain objects from subsystem services (InventoryItem,
PaymentTransaction, ShipmentRecord) to the client, because
the client needs all that data." Evaluate this proposal.
What is the Facade's responsibility for its return type?

*Hint: Returning subsystem objects from the Facade violates
the Facade's decoupling purpose: clients now depend on
subsystem types. If InventoryItem changes (a field is
added/renamed), all clients of the Facade must change.
The Facade's responsibility: return FACADE-LEVEL types
(OrderResult, OrderSummary) that represent what the CLIENT
cares about, not what the subsystem returns. Map subsystem
types to facade types inside the Facade.*

**Q3.** You are implementing a Facade for a payment
subsystem that involves 5 sequential steps. Step 3 fails
for 0.1% of requests due to a transient network issue.
Design the Facade to handle this: (1) retry step 3 up to
3 times before propagating failure, (2) if step 3 fails
after retries, compensate steps 1 and 2, (3) ensure the
facade is idempotent (calling placeOrder with the same
order twice does not double-charge). What design patterns
complement Facade here?

*Hint: (1) Retry: Decorator on the step-3 service call
(or Resilience4j @Retryable). (2) Compensation: saga-style
rollback in the Facade's catch block. (3) Idempotency:
the Facade checks if an order with the same ID was already
processed (an idempotency key) and returns the stored
result if so. Additional patterns: Saga Pattern (DPT-054),
Idempotency Pattern (DPT-085), Retry Pattern (DPT-060).*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Facade and Adapter?
They both wrap something and provide a new interface.**

*Why they ask:* Most common Facade confusion in interviews.

*Strong answer includes:*
- Adapter: wraps ONE class; converts its incompatible
  interface to the interface the client expects; the interface
  change is the goal (same behavior, different API)
- Facade: wraps a SYSTEM (multiple classes); provides a
  simpler, higher-level interface for common operations;
  the simplification is the goal (same end result, less
  complexity exposed)
- Adapter: the adaptee's full capability is preserved
  (just re-interfaced); Facade may not expose all subsystem
  capabilities - only the common-case subset
- JdbcTemplate is Facade (simplifies many JDBC classes);
  InputStreamReader is Adapter (converts InputStream to Reader)

**Q2: Where have you seen the Facade pattern in Spring
Framework or Java EE?**

*Why they ask:* Tests real-world recognition beyond textbook.

*Strong answer includes:*
- `JdbcTemplate`: Facade over JDBC Connection, Statement,
  ResultSet (15+ lines to 3 lines)
- `Spring Data Repository` (e.g., `JpaRepository<User, Long>`):
  Facade over JPA EntityManager, criteria API, JPQL
- `RestTemplate` / `WebClient`: Facade over Java's
  HttpURLConnection / Reactor Netty
- Spring Boot `@SpringApplication.run()`: Facade over
  Spring ApplicationContext bootstrap (environment, beans,
  listeners, embedded server startup)
- AWS SDK `S3TransferManager`: Facade over S3 multipart
  upload, progress tracking, retry

**Q3: A service class that orchestrates multiple repository
and external API calls - is it a Facade? Should it implement
an interface?**

*Why they ask:* Tests practical architecture judgment.

*Strong answer includes:*
- Yes, a Service class that orchestrates multiple lower-level
  components IS a Facade - it provides a simplified
  orchestration interface to the controller/client
- Should it implement an interface? Yes, for testability:
  the interface enables mocking in controller tests;
  the service implementation can be swapped
- The interface defines WHAT the service does (the facade
  contract); the implementation defines HOW (the orchestration)
- Spring @Service + interface = Facade + testable design

