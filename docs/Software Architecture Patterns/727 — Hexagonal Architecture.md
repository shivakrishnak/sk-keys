---
layout: default
title: "Hexagonal Architecture"
parent: "Software Architecture Patterns"
nav_order: 727
permalink: /software-architecture/hexagonal-architecture/
number: "0727"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Layered Architecture, Dependency Inversion Principle, Ports and Adapters, Domain Model
used_by: Clean Architecture, Onion Architecture, Microservices, Domain-Driven Design
related: Clean Architecture, Onion Architecture, Ports and Adapters, Layered Architecture
tags:
  - architecture
  - pattern
  - deep-dive
  - advanced
  - first-principles
---

# 727 — Hexagonal Architecture

⚡ TL;DR — Hexagonal Architecture isolates your domain from all external systems by routing every interaction through defined ports and adapters.

---

### 📊 Entry Metadata

| #727            | Category: Software Architecture Patterns                                               | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Layered Architecture, Dependency Inversion Principle, Ports and Adapters, Domain Model |                 |
| **Used by:**    | Clean Architecture, Onion Architecture, Microservices, Domain-Driven Design            |                 |
| **Related:**    | Clean Architecture, Onion Architecture, Ports and Adapters, Layered Architecture       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application's business logic is inextricably coupled to a specific database vendor, a specific HTTP framework, a specific message broker. You want to test whether a payment rule correctly rejects insufficient funds — but to run that test you must start a PostgreSQL instance, spin up a Spring context, and mock seventeen HTTP endpoints. A single business rule test takes 8 seconds. The full suite takes 45 minutes.

**THE BREAKING POINT:**
A new requirement arrives: the system must now accept commands via a Kafka topic in addition to HTTP. But every piece of business logic has `@RestController` annotations woven through it. Kafka means rewriting half the application. The "business logic" and the "transport layer" are the same code.

**THE INVENTION MOMENT:**
This is exactly why Hexagonal Architecture was created — to draw an absolute boundary around the domain so that it is completely unaware of how it is called or how it stores data. The domain is the application. Everything else is a plug-in.

---

### 📘 Textbook Definition

Hexagonal Architecture (coined by Alistair Cockburn in 2005, also called Ports and Adapters) is an architectural pattern that places the application domain at the centre and enforces that all communication with the outside world — databases, UIs, message queues, external APIs — passes through explicitly defined interfaces called Ports. Concrete implementations of those interfaces are called Adapters. The domain defines Ports as abstract interfaces; Adapters implement them. This inversion ensures the domain has zero dependencies on infrastructure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Your business logic talks to the world only through plug-socket interfaces it defines itself.

**One analogy:**

> A laptop has a hexagonal ring of standard ports: USB-C, HDMI, headphone jack. The laptop's internals don't care whether you plug in a Dell monitor or an LG monitor — as long as the plug fits the port. Hexagonal Architecture makes your domain the laptop, and every external system (database, HTTP, Kafka) a peripheral that must fit your port.

**One insight:**
The radical shift is that the domain defines the interface — not the infrastructure. The database adapter must conform to the `UserRepository` interface the domain declares. This inverts the traditional dependency: previously the domain depended on the database; now the database depends on the domain's contract.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The domain contains all business rules and has zero imports from infrastructure (no `javax.persistence`, no `org.springframework.web`).
2. Ports are interfaces defined by the domain expressing what it needs (driven ports: "I need to load users") or what it offers (driving ports: "I offer a method to process orders").
3. Adapters are concrete implementations that translate between the domain's language and the external system's language.

**DERIVED DESIGN:**
Given these invariants, the architecture has two sides:

- **Driving side (left):** Things that drive the application — HTTP controllers, CLI commands, test harnesses. They call the domain through driving ports.
- **Driven side (right):** Things the application drives — databases, email services, message queues. The domain calls them through driven ports, and adapters implement those ports.

```
┌───────────────────────────────────────────────────┐
│  HEXAGONAL ARCHITECTURE OVERVIEW                  │
├───────────────────────────────────────────────────┤
│                                                   │
│  Driving Side        Domain         Driven Side   │
│  (Callers)           (Core)         (Called)      │
│                                                   │
│  HTTP Adapter  ──→ [Port] ──→ Domain ──→ [Port]   │
│  Kafka Adapter ──→ [Port]    Logic  ──→ [Port] ──→ DB Adapter    │
│  CLI Adapter   ──→ [Port]           ──→ [Port] ──→ Email Adapter │
│  Test Harness  ──→ [Port]                         │
│                                                   │
└───────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** The domain is independently testable (no infrastructure needed), deployable with any delivery mechanism (HTTP, Kafka, CLI), and swappable infrastructure (change the DB without touching domain).
**Cost:** More code. Every interaction requires a port interface and at least one adapter. Simple CRUD applications pay a high complexity tax for minimal benefit. The pattern shines when there are multiple delivery mechanisms or when domain logic is rich enough to justify isolation.

---

### 🧪 Thought Experiment

**SETUP:**
You are building an order processing system. The rule is: orders above €5,000 require manager approval. You need to test this rule.

**WHAT HAPPENS WITHOUT HEXAGONAL ARCHITECTURE:**
The `OrderService` directly calls `orderRepository.save(order)` (JPA) and `httpClient.post("/notifications/manager")` (REST). To test the approval rule, you must: start a PostgreSQL container, configure JPA mappings, start the notification service (or mock it via WireMock), set up an HTTP test server. The test code runs for 12 seconds. When the notification service changes its API contract, your business rule test breaks.

**WHAT HAPPENS WITH HEXAGONAL ARCHITECTURE:**
The domain defines `OrderRepository` and `NotificationPort` as interfaces. The test provides in-memory implementations: `InMemoryOrderRepository` (a HashMap) and `RecordingNotificationPort` (records what was called). The test runs in 4 milliseconds, has zero external dependencies, and survives any change to the database or notification service. The same domain code, unchanged, runs in production connected to real JPA and real HTTP adapters.

**THE INSIGHT:**
Testability is not a quality bolt-on — it is the direct consequence of correct dependency direction. When the domain defines its own contracts, tests become the simplest possible adapter.

---

### 🧠 Mental Model / Analogy

> Think of a universal power supply. The device's core circuitry doesn't care whether it receives 110V US power or 220V European power — it just needs a stable 5V DC input. Adapters (the plug converters) translate external voltage to the device's internal contract.

- "Device circuitry" → Domain (business rules)
- "5V DC input requirement" → Port interface
- "110V/220V plug converter" → Adapter (HTTP, Kafka, CLI)
- "Power socket" → External system (database, message broker, external API)
- "Universal standard plug" → Defined port contract

Where this analogy breaks down: Power adapters are passive; in Hexagonal Architecture, driving adapters actively call the domain, not merely convert signals. The analogy holds better for driven adapters (database, external services).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Hexagonal Architecture keeps your application's business rules in a protected core. Anything that talks to the outside world — the website, the database, the email service — connects through defined plug-sockets. The core only knows about its own plug-sockets, not about what's plugged into them.

**Level 2 — How to use it (junior developer):**
Define your domain logic in plain classes with no framework imports. Create interface definitions (Ports) for everything the domain needs to do with the outside world. Create Adapter classes that implement those interfaces using real infrastructure (JPA, REST clients). Wire everything together in a configuration layer. The domain package should have zero transitive dependencies on Spring, JPA, or any vendor library.

**Level 3 — How it works (mid-level engineer):**
Ports come in two flavours. Primary (driving) ports are interfaces the domain exposes to callers — for example, `OrderApplicationService` with a `processOrder(command)` method. Secondary (driven) ports are interfaces the domain calls for infrastructure — `OrderRepository`, `PaymentGateway`. Dependency injection (Spring's `@Autowired`, or explicit constructor injection) binds the correct adapter to each port at startup. The domain never uses `new ConcreteAdapter()`. The configuration layer owns all wiring decisions.

**Level 4 — Why it was designed this way (senior/staff):**
Cockburn's original insight was that the "inside" and "outside" are symmetric — both use the same pattern. This symmetry means you can flip the application: use it from tests as easily as from HTTP. The hexagon shape was illustrative, not structural — it represents "many equivalent sides." The real constraint is the dependency rule: domain code may not reference infrastructure packages, enforced statically via ArchUnit or module-system rules. At scale, this architecture enables teams to evolve delivery mechanisms (REST → gRPC → event-driven) without touching domain logic — a critical capability in microservices migrations.

---

### ⚙️ How It Works (Mechanism)

**Dependency wiring at startup:**

1. The application configuration creates a concrete `JpaUserRepository` and a concrete `SmtpEmailAdapter`.
2. It injects these into the domain service via constructor: `new UserDomainService(jpaRepo, smtpAdapter)`.
3. The domain service holds references to `UserRepository` (interface) and `EmailPort` (interface) — it never sees the concrete classes.

**Request processing flow:**

```
┌──────────────────────────────────────────────────────┐
│           HEXAGONAL ARCHITECTURE — REQUEST           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  HTTP Request                                        │
│      ↓                                               │
│  ┌─────────────────────────────────────────────┐     │
│  │ HTTP Adapter (Spring @Controller)           │     │
│  │ Maps HTTP → Command object                  │     │
│  └────────────────────┬────────────────────────┘     │
│                       ↓ calls driving port           │
│  ┌─────────────────────────────────────────────┐     │
│  │      DOMAIN (NO FRAMEWORK IMPORTS)          │     │
│  │  OrderApplicationService.process(cmd)       │     │
│  │  → validates → applies rules → calls ports  │     │
│  └────────┬───────────────────┬────────────────┘     │
│           ↓ calls driven port  ↓ calls driven port   │
│  ┌────────────────┐  ┌────────────────────────────┐  │
│  │ DB Adapter     │  │ Notification Adapter       │  │
│  │ (JPA/Mongo)    │  │ (SMTP/Slack/PushNotify)    │  │
│  └────────────────┘  └────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Port definition (domain owns this):**

```java
// Domain package — no framework imports
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}

public interface NotificationPort {
    void notifyManager(ManagerNotification notification);
}
```

**Adapter implementation (infrastructure owns this):**

```java
// Infrastructure package — implements domain port
@Repository
public class JpaOrderRepository
        implements OrderRepository {
    // JPA annotations here — domain never sees them
    @PersistenceContext
    private EntityManager em;

    @Override
    public Order findById(OrderId id) {
        // maps JPA entity to domain Order object
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
HTTP POST /orders
  → HTTP Adapter (parse DTO, map to Command)
  → OrderApplicationService.placeOrder(cmd)  ← YOU ARE HERE
  → Order domain object (apply business rules)
  → OrderRepository.save(order) [via driven port]
  → JpaOrderRepository [adapter] → PostgreSQL
  → NotificationPort.notify() [via driven port]
  → EmailAdapter [adapter] → SMTP server
  → HTTP 201 Created
```

**FAILURE PATH:**

```
JpaOrderRepository throws DataAccessException
  → domain receives RepositoryException (translated)
  → OrderApplicationService propagates
  → HTTP Adapter maps to HTTP 503
  → Client receives error
Domain never saw SQLException — infrastructure detail hidden
```

**WHAT CHANGES AT SCALE:**
At scale, driven adapters become bottlenecks while the domain stays stable. You can introduce a caching adapter that wraps the DB adapter without the domain knowing — the domain still calls `OrderRepository` but gets cached results. At very high scale, you can run the domain in multiple processes simultaneously, each with its own adapter set, because the domain is stateless and pure.

---

### 💻 Code Example

**Example 1 — Wrong: domain importing JPA (coupling):**

```java
// BAD — domain is coupled to JPA
import javax.persistence.EntityManager; // VIOLATION!

public class OrderService {
    @Autowired
    private EntityManager em; // direct infrastructure dep

    public void placeOrder(OrderRequest req) {
        // SQL/JPA in business logic — untestable
        em.persist(new OrderEntity(req));
    }
}
```

**Example 2 — Right: domain with ports:**

```java
// Domain — zero infrastructure imports
public class OrderApplicationService {
    private final OrderRepository orderRepo;  // port
    private final PaymentGateway paymentGw;   // port

    // Constructor injection — framework-free
    public OrderApplicationService(
            OrderRepository orderRepo,
            PaymentGateway paymentGw) {
        this.orderRepo = orderRepo;
        this.paymentGw = paymentGw;
    }

    public OrderId placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(
            cmd.customerId(),
            cmd.items()
        );
        PaymentResult result =
            paymentGw.charge(order.total());
        order.confirmPayment(result);
        orderRepo.save(order);
        return order.id();
    }
}
```

**Example 3 — Production pattern: in-memory adapter for tests:**

```java
// Test adapter — no database needed
class InMemoryOrderRepository
        implements OrderRepository {
    private final Map<OrderId, Order> store =
        new HashMap<>();

    @Override
    public void save(Order order) {
        store.put(order.id(), order);
    }

    @Override
    public Order findById(OrderId id) {
        return store.get(id);
    }
}

// Test runs at microsecond speed, no DB required
class OrderApplicationServiceTest {
    @Test
    void highValueOrderRequiresApproval() {
        var repo = new InMemoryOrderRepository();
        var payment = new RecordingPaymentGateway();
        var service = new OrderApplicationService(
            repo, payment
        );
        service.placeOrder(highValueCommand());
        assertThat(repo.findById(...).status())
            .isEqualTo(PENDING_APPROVAL);
    }
}
```

---

### ⚖️ Comparison Table

| Pattern                     | Domain isolation | Complexity | Testability | Best For                                        |
| --------------------------- | ---------------- | ---------- | ----------- | ----------------------------------------------- |
| **Hexagonal Architecture**  | Total            | High       | Excellent   | Rich domain + multiple delivery mechanisms      |
| Layered Architecture        | Partial          | Low        | Good        | CRUD apps, team organised by technical role     |
| Clean Architecture          | Total            | Very High  | Excellent   | Enterprise systems requiring explicit use-cases |
| Vertical Slice Architecture | Per-slice        | Medium     | Good        | Feature-team organisations                      |

**How to choose:** Use Hexagonal Architecture when your domain logic is rich, when you need multiple delivery mechanisms (HTTP + Kafka + CLI), or when infrastructure changes are likely. Avoid it for simple CRUD systems where the overhead of port/adapter wiring outweighs the benefit.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                    |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Hexagonal means exactly 6 sides              | The hexagon is symbolic — it means "many equivalent interaction points," not literally 6                   |
| Ports are the same as interfaces             | All ports are interfaces but not all interfaces are ports — a port represents a boundary-crossing contract |
| Adapters live inside the domain              | Adapters are always outside the domain; they import infrastructure libraries the domain must not see       |
| Hexagonal architecture prevents using Spring | Spring is used in adapters and configuration — just not in the domain core                                 |
| You need hexagonal for all microservices     | Only services with rich domain logic benefit; pure data-passing services don't need the overhead           |

---

### 🚨 Failure Modes & Diagnosis

**Domain contamination (infrastructure leaking in)**

**Symptom:** Domain service classes have `@Entity`, `@Transactional`, or `import org.springframework` in their imports. Tests require Spring context startup.

**Root Cause:** Developer adds convenience annotations to domain classes to avoid writing adapters, gradually eroding the boundary.

**Diagnostic Command / Tool:**

```bash
# Check domain package for infrastructure imports
grep -rn "import org.springframework\|import javax.persistence\
\|import jakarta.persistence" \
  src/main/java/com/example/domain/
```

**Fix:** Move all framework annotations to adapter and configuration classes.

**Prevention:** Use ArchUnit to enforce import rules: `noClasses().that().resideInPackage("..domain..").should().dependOnClassesThat().resideInPackage("org.springframework..")`.

---

**Missing port translation (leaking domain objects)**

**Symptom:** Database schema changes break domain objects directly. A column rename causes domain tests to fail.

**Root Cause:** Adapter uses domain objects as JPA entities directly, merging the domain model and persistence model into one class.

**Diagnostic Command / Tool:**

```bash
# Find @Entity in domain package
grep -rn "@Entity" src/main/java/com/example/domain/
```

**Fix:** Separate domain objects (`Order`) from persistence entities (`OrderEntity`). The adapter translates between them.

**Prevention:** Enforce that no `@Entity` annotation appears in domain packages via ArchUnit or package structure reviews.

---

**Port proliferation (over-engineering)**

**Symptom:** Every single method has its own interface. There are 47 port interfaces for 47 methods. Configuration code is larger than domain code.

**Root Cause:** Misapplication of the pattern — ports should represent logical boundaries (e.g., `OrderRepository`), not individual method signatures.

**Diagnostic Command / Tool:**

```bash
# Count interfaces in domain vs adapters
find . -name "*.java" -path "*/domain/*" \
  | xargs grep -l "interface" | wc -l
```

**Fix:** Merge related single-method interfaces into cohesive port definitions.

**Prevention:** Define ports around roles, not methods: "What role does this external collaborator play for the domain?"

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Dependency Inversion Principle` — the SOLID principle that underpins port direction
- `Layered Architecture` — the simpler predecessor that Hexagonal Architecture evolved from
- `Domain Model` — the rich business objects that live at the centre of the hexagon

**Builds On This (learn these next):**

- `Clean Architecture` — applies similar isolation with explicit use-case ring
- `Onion Architecture` — another concentric ring variant with the same dependency rule
- `Domain-Driven Design` — the design methodology most naturally paired with hexagonal architecture

**Alternatives / Comparisons:**

- `Ports and Adapters` — the original name for Hexagonal Architecture (they are the same)
- `Layered Architecture` — simpler; allows infrastructure to influence domain design
- `Vertical Slice Architecture` — organises by feature rather than by domain/infrastructure boundary

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Domain at centre; all external I/O via    │
│              │ defined port interfaces + adapters        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business logic coupled to framework,      │
│ SOLVES       │ database, and transport — untestable      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The domain defines its contracts; infra   │
│              │ conforms to them — dependency inverted    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Rich domain logic + multiple delivery     │
│              │ mechanisms + infrastructure may change    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD, single delivery mechanism,   │
│              │ no complex business rules                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Total domain isolation vs higher upfront  │
│              │ wiring and abstraction overhead           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The domain defines the plug shape;       │
│              │  the world must fit it"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Ports & Adapters → Clean Arch → DDD      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Hexagonal Architecture application with a driving port `OrderApplicationService`. A new requirement arrives: the same `placeOrder` logic must be callable from an HTTP endpoint AND from a Kafka consumer AND from a scheduled batch job. How does Hexagonal Architecture handle this requirement? What is the exact relationship between the three adapters, and how much domain code must change?

**Q2.** A colleague argues: "Hexagonal Architecture is just dependency injection with extra marketing." At what precise technical point does Hexagonal Architecture provide something that dependency injection alone cannot guarantee? Be specific: what can break with DI that cannot break with proper hexagonal discipline?
