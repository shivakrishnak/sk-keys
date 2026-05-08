---
layout: default
title: "Ports and Adapters"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /software-architecture/ports-and-adapters/
id: SAP-020
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Hexagonal Architecture, Dependency Inversion Principle, Interface Segregation Principle
used_by: Hexagonal Architecture, Clean Architecture, Microservices, Domain-Driven Design
related: Hexagonal Architecture, Clean Architecture, Repository Pattern, Anti-Corruption Layer
tags:
  - architecture
  - pattern
  - deep-dive
  - advanced
  - first-principles
---

# SAP-020 — Ports and Adapters

⚡ TL;DR — Ports and Adapters is the original name for Hexagonal Architecture: ports are interfaces the domain defines; adapters are the concrete implementations that plug into those interfaces.

---

### 📊 Entry Metadata

| #733            | Category: Software Architecture Patterns                                                | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Hexagonal Architecture, Dependency Inversion Principle, Interface Segregation Principle |                 |
| **Used by:**    | Hexagonal Architecture, Clean Architecture, Microservices, Domain-Driven Design         |                 |
| **Related:**    | Hexagonal Architecture, Clean Architecture, Repository Pattern, Anti-Corruption Layer   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application's domain logic is littered with calls to `jdbcTemplate.query(...)`, `restTemplate.getForObject(...)`, and `kafkaTemplate.send(...)`. These are scattered through every service class. When you want to run a unit test for a business rule, the test requires a live database connection, a running Kafka broker, and a real external API. Test setup takes 30 seconds. Tests take 5 minutes. When you need to swap from JDBC to JPA, you hunt for JDBC calls across the entire application.

**THE BREAKING POINT:**
The domain is completely untestable in isolation because it has no isolation. The business logic and the infrastructure calls are the same code. There is no seam where you can replace real infrastructure with a test double.

**THE INVENTION MOMENT:**
This is exactly why Ports and Adapters was created — to introduce explicit seams (ports) where real infrastructure can be swapped for any alternative, including test doubles, giving the domain complete independence from how it talks to the world.

---

### 📘 Textbook Definition

Ports and Adapters (the original name coined by Alistair Cockburn for Hexagonal Architecture) is an architectural pattern that defines two types of boundary objects: Ports — interfaces that define the communication contract between the domain and external systems — and Adapters — concrete classes that implement a Port for a specific technology. The domain interacts only with Ports. Adapters translate between the Port's abstract contract and the specific external system's API. This produces a domain that is completely technology-agnostic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Define a plug socket specification (port); build different plugs for each device (adapters).

**One analogy:**

> A standard 3-pin UK wall socket is a port — it defines a contract (voltage, shape, pinout). Every device that wants to receive power must have a matching plug (adapter). The house wiring doesn't need to change when you replace your toaster with a kettle — the port contract stays fixed; only the adapter (plug) is specific to the device.

**One insight:**
The profound shift: it is the domain — not the infrastructure — that defines the contract. The database adapter must conform to the domain's `UserRepository` interface, not the other way around. This inverts the typical dependency: instead of "my code depends on MySQL," it becomes "MySQL's adapter depends on my code's contract."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A Port is an interface owned and defined by the domain — it expresses a capability the domain needs or offers.
2. An Adapter is a class owned by the infrastructure — it implements a Port by translating calls to/from a specific technology.
3. The domain never imports or references adapter classes — only port interfaces.

**PORT TYPES:**
There are two kinds of ports, corresponding to two directions of interaction:

**Primary (Driving) Ports:**
The domain exposes these — external callers drive the application through them.

- Example: `OrderApplicationService` interface — HTTP controller, CLI, and test harnesses call it.
- The controller is the adapter on the driving side.

**Secondary (Driven) Ports:**
The domain calls through these — the domain drives external systems via them.

- Example: `OrderRepository`, `PaymentGateway`, `EmailPort`.
- JPA, Stripe SDK, and SMTP are adapters on the driven side.

```
┌──────────────────────────────────────────────────────────┐
│            PORTS AND ADAPTERS OVERVIEW                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Driving Adapters      DOMAIN      Driven Adapters       │
│  (call the domain)     (Core)      (called by domain)    │
│                                                          │
│  HTTP Controller ──→ [PRIMARY  ──→ SECONDARY] ──→ JPA   │
│  CLI ──────────→ [   PORT     │   PORT     ] ──→ SMTP   │
│  Test Harness ──→ [           │            ] ──→ Redis  │
│                   (interface  │ (interface             │
│                   exposed)    │  required)             │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Any adapter can be swapped for any other implementing the same port. Tests use in-memory adapters. Real adapters are used in production. The domain is tested independently of infrastructure.
**Cost:** Every interaction requires a port interface and at least one adapter — more files and indirection. For simple CRUD applications this overhead produces no tangible benefit.

---

### 🧪 Thought Experiment

**SETUP:**
Your domain needs to send a notification when an order is placed. Currently this calls an SMTP email service directly.

**WHAT HAPPENS WITHOUT PORTS AND ADAPTERS:**
`OrderService.placeOrder()` contains: `smtpClient.sendEmail("order-confirmation@co.com", ...)`. Test requires a real SMTP server or a complex mock. When you add push notifications alongside email, you modify `OrderService` — a business logic class — to add push notification infrastructure code. When Slack is added as a third channel, `OrderService` grows again.

**WHAT HAPPENS WITH PORTS AND ADAPTERS:**
`OrderService.placeOrder()` calls `notificationPort.notify(new OrderConfirmation(order))`. `NotificationPort` is an interface with a single `notify()` method. Three adapters implement it: `SmtpNotificationAdapter`, `PushNotificationAdapter`, `SlackNotificationAdapter`. Tests use `RecordingNotificationAdapter` — zero SMTP infrastructure needed. Adding Slack means writing one new adapter class — `OrderService` never changes. A composite adapter can notify via all three simultaneously.

**THE INSIGHT:**
When you define the port (the contract) before the adapter (the implementation), you discover the minimal interface your domain actually needs — not the full API of the infrastructure system you happen to be using today.

---

### 🧠 Mental Model / Analogy

> Think of audio equipment: a guitar (domain) outputs a 1/4-inch jack signal (port). The amplifier input (adapter) accepts a 1/4-inch jack. The guitar doesn't know whether it's plugged into a Fender amp, a practice amp, or a recording interface — the port contract is the same. Change the adapter (amp) without changing the guitar.

- "Guitar output jack specification" → Primary port (what the domain offers)
- "Amp input" → Driving adapter (HTTP controller, CLI, test)
- "Effects pedal input socket" → Secondary port (what domain needs from world)
- "Reverb effect unit" → Driven adapter (database, email, external API)
- "Instrument cable" → Dependency injection binding

Where this analogy breaks down: Audio adapters are passive signal converters; software adapters may perform complex translation including data format changes, protocol conversion, and error handling.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Your app's logic talks to the world using plug-socket agreements. Any device (database, email, test) that fits the plug shape can connect. The logic never needs to know what's plugged in.

**Level 2 — How to use it (junior developer):**
Write an interface for everything your domain needs from outside: `UserRepository`, `EmailSender`, `PaymentGateway`. Implement each interface once for production (JPA, SMTP, Stripe) and once for tests (in-memory HashMap, recording list). Inject whichever implementation is appropriate at startup. The domain only imports the interface.

**Level 3 — How it works (mid-level engineer):**
Port design is the critical skill. A poor port design leaks infrastructure: `UserRepository.executeQuery(String sql)` leaks SQL concepts into the domain. A good port design speaks domain language: `UserRepository.findByEmail(Email email)`. The adapter translates `findByEmail(email)` into `SELECT * FROM users WHERE email = ?` — the SQL is entirely in the adapter. Port interfaces should be defined by what the domain needs, not by what the technology can do.

**Level 4 — Why it was designed this way (senior/staff):**
Cockburn's fundamental insight was that there is no meaningful difference between "the test harness" and "the HTTP interface" from the domain's perspective — both are driving adapters that call the domain. This symmetry means the domain can be tested by substituting the test harness adapter for the HTTP adapter. The hexagonal shape was chosen precisely because it conveys "many interchangeable sides" — emphasising that there is no "main" interface and no "special" side. In microservices, ports define the service's API contract independent of protocol — the same port can be exposed via REST, gRPC, and message broker simultaneously through three different adapters.

---

### ⚙️ How It Works (Mechanism)

**Binding adapters at application startup:**

```
Startup sequence:
1. Create infrastructure adapters:
   JpaUserRepository jpaRepo = new JpaUserRepository(em)
   SmtpEmailAdapter smtp = new SmtpEmailAdapter(config)
   StripePaymentAdapter stripe = new StripePaymentAdapter(key)

2. Inject adapters into domain services:
   UserDomainService svc = new UserDomainService(
     jpaRepo,   // implements UserRepository (port)
     smtp,      // implements EmailSender (port)
     stripe     // implements PaymentGateway (port)
   )

3. Wrap domain services in driving adapters:
   UserHttpController http = new UserHttpController(svc)
   UserCli cli = new UserCli(svc)

4. Domain never references JPA, SMTP, or Stripe
```

**Test binding (substituting adapters):**

```
Test setup:
1. Create in-memory adapters:
   InMemoryUserRepository repo = new InMemoryUserRepository()
   RecordingEmailSender email = new RecordingEmailSender()
   FakePaymentGateway payment = new FakePaymentGateway()

2. Inject into domain service (same code as production):
   UserDomainService svc = new UserDomainService(
     repo, email, payment
   )

3. Test harness acts as driving adapter:
   svc.registerUser(cmd)  // no HTTP, no test containers
   assertThat(email.sent()).hasSize(1)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
HTTP POST /users
  → HTTP Adapter (driving) parses request
  → UserApplicationService.register(cmd)  ← YOU ARE HERE
  → User.create() [domain rules]
  → UserRepository [driven port]
  → JpaUserRepository [driven adapter] → PostgreSQL
  → EmailSender [driven port]
  → SmtpEmailAdapter [driven adapter] → SMTP
  → HTTP 201 response
```

**FAILURE PATH:**

```
SmtpEmailAdapter throws EmailDeliveryException
  → Domain catches EmailSendingException (port-translated)
  → Application service decides: fail or log and continue
  → HTTP adapter returns 201 if email is non-critical
Domain never saw SMTP-specific exception
```

**WHAT CHANGES AT SCALE:**
At scale, driven adapters may be replaced with async versions. `EmailSender.send()` adapter publishes to a queue instead of sending synchronously — the domain doesn't change. Multiple instances of the application share the same port contracts; each runs its own adapter instances. An API gateway adapter can replace the HTTP controller adapter for edge deployments.

---

### 💻 Code Example

**Example 1 — Defining a driven port (domain owns this):**

```java
// Secondary (driven) port — domain defines its needs
// No SMTP, no Kafka, no framework imports
public interface NotificationPort {
    void notifyOrderPlaced(OrderPlacedNotification note);
    void notifyOrderCancelled(OrderId orderId, String reason);
}

// Domain calls this — doesn't know what's behind it
public class OrderApplicationService {
    private final NotificationPort notifier;

    public void placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd);
        notifier.notifyOrderPlaced(
            new OrderPlacedNotification(
                order.id(), order.customerId()
            )
        );
    }
}
```

**Example 2 — Production adapter (infrastructure owns this):**

```java
// Driven adapter — implements domain port using SMTP
@Component
@RequiredArgsConstructor
public class EmailNotificationAdapter
        implements NotificationPort {
    private final JavaMailSender mailSender;  // SMTP

    @Override
    public void notifyOrderPlaced(
            OrderPlacedNotification note) {
        SimpleMailMessage msg = new SimpleMailMessage();
        msg.setTo(resolveEmail(note.customerId()));
        msg.setSubject("Order Confirmed: "
            + note.orderId().value());
        msg.setText("Your order has been placed.");
        mailSender.send(msg);
    }

    @Override
    public void notifyOrderCancelled(
            OrderId orderId, String reason) {
        // ... SMTP implementation
    }
}
```

**Example 3 — Test adapter (in-memory, zero infrastructure):**

```java
// Test adapter — implements same port, zero SMTP
class RecordingNotificationAdapter
        implements NotificationPort {
    private final List<Object> sent = new ArrayList<>();

    @Override
    public void notifyOrderPlaced(
            OrderPlacedNotification note) {
        sent.add(note);
    }

    @Override
    public void notifyOrderCancelled(
            OrderId orderId, String reason) {
        sent.add(new CancelledNote(orderId, reason));
    }

    public List<Object> getSent() {
        return Collections.unmodifiableList(sent);
    }
}

// Test runs in milliseconds — no SMTP required
class OrderApplicationServiceTest {
    @Test
    void placingOrderSendsNotification() {
        var notifier = new RecordingNotificationAdapter();
        var service = new OrderApplicationService(
            new InMemoryOrderRepository(), notifier
        );
        service.placeOrder(aPlaceOrderCommand());
        assertThat(notifier.getSent()).hasSize(1);
        assertThat(notifier.getSent().get(0))
            .isInstanceOf(OrderPlacedNotification.class);
    }
}
```

---

### ⚖️ Comparison Table

| Concept                  | Owns interface? | Where defined          | Technology coupling    |
| ------------------------ | --------------- | ---------------------- | ---------------------- |
| **Port**                 | Domain          | Domain package         | None                   |
| **Adapter**              | Infrastructure  | Infrastructure package | Specific technology    |
| Repository Pattern       | Domain          | Domain package         | ORM/DB abstraction     |
| DAO (Data Access Object) | Infrastructure  | Varies                 | Specific DB technology |

**How to choose:** Ports and Adapters is the naming framework for Hexagonal Architecture — if you're implementing Hexagonal Architecture, you're implementing Ports and Adapters. The Repository Pattern is a specific instance of a driven port applied to persistence concerns.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Ports and Adapters is different from Hexagonal Architecture | They are the same pattern — different names for the same concept                                                         |
| Any interface is a port                                     | Interfaces inside the domain (e.g., between domain services) are not ports — ports cross the domain boundary             |
| Adapters should be thin translators only                    | Adapters can contain complex translation logic, retry logic, and error handling — they own all infrastructure complexity |
| Ports and Adapters requires a specific framework            | It's a design principle — implementable with plain Java interfaces and constructor injection, no framework needed        |
| The driving adapter is more important than the driven       | Both are equal — the pattern's power comes from symmetry; tests are just driving adapters                                |

---

### 🚨 Failure Modes & Diagnosis

**Infrastructure-flavoured port design**

**Symptom:** Port methods look like SQL calls or HTTP calls: `UserRepository.executeQuery(String sql)`, `ExternalApiPort.post(String url, Map<String, String> headers)`.

**Root Cause:** Port designed by starting from the technology API and wrapping it, instead of starting from domain need and designing the contract.

**Diagnostic Command / Tool:**

```bash
# Find ports with infrastructure-flavoured signatures
grep -rn "String sql\|HttpEntity\|MultiValueMap\
\|PreparedStatement" \
  src/main/java/**/domain/ \
  src/main/java/**/port/
```

**Fix:** Redesign ports starting from domain vocabulary. `UserRepository.findActiveCustomersByRegion(RegionId)` not `executeQuery("SELECT ...")`.

**Prevention:** The "newspaper test" — can a domain expert read the port interface and understand its purpose without knowing the implementation technology?

---

**Adapter leak into domain**

**Symptom:** Domain service class imports an adapter class directly. Tests require the adapter's infrastructure dependency.

**Root Cause:** Shortcut — developer imports the concrete class instead of the port interface.

**Diagnostic Command / Tool:**

```bash
# Domain importing adapter implementations
grep -rn "import.*Adapter\|import.*Repository\
\|import.*Impl" \
  src/main/java/**/domain/
```

**Fix:** Replace all concrete class references with interface references in domain classes. Enforce via ArchUnit.

**Prevention:** Domain package should have zero imports from the infrastructure or adapter packages.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Hexagonal Architecture` — the architectural pattern of which Ports and Adapters is the naming convention
- `Dependency Inversion Principle` — the SOLID principle that makes ports point inward

**Builds On This (learn these next):**

- `Repository Pattern` — a specific application of a driven port to persistence
- `Anti-Corruption Layer` — a more complex driven adapter that translates between domain models

**Alternatives / Comparisons:**

- `DAO (Data Access Object)` — a simpler access pattern without domain-first port ownership
- `Service Locator` — an alternative to injection; ports avoid the need for service locator

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Ports = domain-defined interfaces;        │
│              │ Adapters = technology implementations     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Domain logic coupled to infrastructure — │
│ SOLVES       │ untestable, inflexible, fragile           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The domain owns the contract; the world   │
│              │ must conform to the domain's terms        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need to swap infrastructure; need fast    │
│              │ domain tests without infrastructure       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple scripts; trivial CRUD apps with    │
│              │ no need for infrastructure independence   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Infrastructure independence + testability │
│              │ vs more files and abstraction overhead    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The domain sets the plug shape;          │
│              │  the world provides the plug"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Repository Pattern → Anti-Corruption      │
│              │ Layer → Hexagonal Architecture            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `PaymentPort` driven port with method `charge(Money amount, PaymentDetails details)`. Your business rules say: "If the payment provider is unavailable, retry up to 3 times with exponential backoff." Should this retry logic live in the Port definition, in the Adapter, or in the Domain Service that calls the port? What architectural principle determines the answer, and what changes if the retry is a business rule ("our policy is to retry") versus an infrastructure concern ("the network is flaky")?

**Q2.** A microservice exposes its business logic via three protocols simultaneously: REST HTTP for external clients, gRPC for internal service-to-service calls, and Kafka messages for event-driven consumers. How do Ports and Adapters handle this scenario? How many ports exist, how many adapters, and where does the protocol-specific behaviour live relative to the domain?
