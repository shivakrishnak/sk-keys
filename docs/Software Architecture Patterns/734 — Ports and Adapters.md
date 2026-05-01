---
layout: default
title: "Ports and Adapters"
parent: "Software Architecture Patterns"
nav_order: 734
permalink: /software-architecture/ports-and-adapters/
number: "734"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Hexagonal Architecture, Dependency Inversion Principle, Interface Segregation"
used_on: "Spring Boot, Quarkus, .NET Core, any DDD application"
tags: #advanced, #architecture, #hexagonal, #ports, #adapters
---

# 734 — Ports and Adapters

`#advanced` `#architecture` `#hexagonal` `#ports` `#adapters`

⚡ TL;DR — **Ports** are the interfaces the application core defines for all external communication; **Adapters** are the concrete implementations that plug in — the pattern that makes the application core technology-agnostic and independently testable.

| #734            | Category: Software Architecture Patterns                                      | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Hexagonal Architecture, Dependency Inversion Principle, Interface Segregation |                 |
| **Used on:**    | Spring Boot, Quarkus, .NET Core, any DDD application                          |                 |

---

### 📘 Textbook Definition

**Ports and Adapters** is the implementation pattern at the heart of Hexagonal Architecture (Alistair Cockburn, 2005). A **Port** is an interface (contract) defined by the application core that specifies how external systems must interact with it, or how the application interacts with external systems. An **Adapter** is the concrete implementation that connects an external technology to a port. Two categories: (1) **Primary (Driving) Adapters** — drive the application (initiate actions): REST controllers, CLI commands, test cases, message queue consumers. They implement or call the application's **Input Ports** (use case interfaces). (2) **Secondary (Driven) Adapters** — driven by the application (respond to its requests): JPA repositories, email senders, S3 file storage, Stripe payment client. They implement the application's **Output Ports** (outbound interfaces). The boundary: the application core contains only ports (interfaces) and domain logic. Adapters contain all technology-specific code. This strict separation enables: testing the application core with mock adapters (no infrastructure), swapping technologies (replace JPA adapter with DynamoDB adapter), and adding new entry points (REST → also Kafka consumer) without touching the core.

---

### 🟢 Simple Definition (Easy)

An electrical outlet (port) and plug (adapter). The wall outlet defines a standard interface (120V, specific shape). Any device with the right adapter can plug in — a lamp, a phone charger, a TV. The outlet doesn't know what's plugged in. A European device with a different plug? Use a plug adapter. Ports: the standard interfaces. Adapters: the connectors that make specific technologies work with those standards. The house's electrical system (application core): works with any compliant device.

---

### 🔵 Simple Definition (Elaborated)

In code: your `OrderService` needs to save orders and send emails. Without ports/adapters: `OrderService` directly uses `JpaOrderRepository` and `SendGridEmailClient`. Changing email provider: rewrite `OrderService`. Changing database: rewrite `OrderService`. With ports/adapters: `OrderService` depends on `OrderRepository` (port, interface) and `EmailSender` (port, interface). `JpaOrderAdapter` implements `OrderRepository`. `SendGridAdapter` implements `EmailSender`. Change email provider: write `MailgunAdapter`, swap the adapter. `OrderService` is unchanged. Tested with mock adapters: no database, no email infrastructure needed.

---

### 🔩 First Principles Explanation

**Primary vs. secondary ports, adapter categories, and technology-agnostic core:**

```
PORT CATEGORIES:

  INPUT PORTS (Primary — how the outside world drives the application):
  ┌──────────────────────────────────────────────────────────┐
  │ interface PlaceOrderUseCase { OrderId execute(cmd) }     │ ← Input Port
  │ interface GetOrderUseCase { OrderDTO execute(query) }    │ ← Input Port
  │ interface CancelOrderUseCase { void execute(id) }        │ ← Input Port
  └──────────────────────────────────────────────────────────┘

  OUTPUT PORTS (Secondary — how the application reaches outside world):
  ┌──────────────────────────────────────────────────────────┐
  │ interface OrderRepository { ... }                        │ ← Output Port
  │ interface PaymentGateway { PaymentResult charge(...) }   │ ← Output Port
  │ interface NotificationSender { void notify(...) }        │ ← Output Port
  │ interface InventoryService { boolean reserve(...) }      │ ← Output Port
  └──────────────────────────────────────────────────────────┘

PRIMARY (DRIVING) ADAPTERS (call input ports):
  ┌────────────────────────────────────────────────────────┐
  │ REST Controller — HTTP request → calls PlaceOrderUseCase│
  │ CLI Command     — command line → calls PlaceOrderUseCase│
  │ Kafka Consumer  — message      → calls PlaceOrderUseCase│
  │ Test Cases      — test input   → calls PlaceOrderUseCase│
  └────────────────────────────────────────────────────────┘
  → All use the same PlaceOrderUseCase input port.
  → Each delivers requests via different technology.
  → Application core: unaware which delivery mechanism was used.

SECONDARY (DRIVEN) ADAPTERS (implement output ports):
  ┌─────────────────────────────────────────────────────────┐
  │ JpaOrderAdapter      implements OrderRepository         │
  │ DynamoOrderAdapter   implements OrderRepository         │
  │ InMemoryOrderAdapter implements OrderRepository  (test) │
  ├─────────────────────────────────────────────────────────┤
  │ StripePaymentAdapter implements PaymentGateway          │
  │ PayPalPaymentAdapter implements PaymentGateway          │
  │ MockPaymentAdapter   implements PaymentGateway   (test) │
  ├─────────────────────────────────────────────────────────┤
  │ SendGridAdapter    implements NotificationSender        │
  │ TwilioSmsAdapter   implements NotificationSender        │
  │ ConsoleAdapter     implements NotificationSender (dev)  │
  └─────────────────────────────────────────────────────────┘

APPLICATION CORE (ONLY ports + domain logic):

  public class PlaceOrderService implements PlaceOrderUseCase {
      private final OrderRepository orderRepo;    // Output port.
      private final PaymentGateway payment;       // Output port.
      private final NotificationSender notifier;  // Output port.

      // Constructor injection — adapters injected at runtime (via DI container).

      @Override
      public OrderId execute(PlaceOrderCommand cmd) {
          Order order = Order.create(cmd.customerId(), cmd.items());

          PaymentResult result = payment.charge(cmd.card(), order.total());
          if (!result.isSuccessful()) throw new PaymentFailedException();

          OrderId id = orderRepo.save(order).id();
          notifier.notify(order.customerId(), NotificationType.ORDER_CONFIRMED);

          return id;
      }
  }
  // No Spring, no JPA, no Stripe, no SendGrid imports. Pure domain + ports.

ADAPTER SWAP (changing technology):

  Initial: JpaOrderAdapter (PostgreSQL).
  New requirement: migrate to DynamoDB.

  Create: DynamoOrderAdapter implements OrderRepository
    // Implements same OrderRepository interface.
    // Uses AWS SDK inside.

  Swap in Spring config:
    // Before:
    @Bean public OrderRepository orderRepo(JpaProductRepository jpa) {
        return new JpaOrderAdapter(jpa);
    }
    // After:
    @Bean public OrderRepository orderRepo(DynamoDbClient dynamo) {
        return new DynamoOrderAdapter(dynamo);
    }

  PlaceOrderService: UNCHANGED. All other core code: UNCHANGED.
  Only new code: DynamoOrderAdapter + Spring config change.

TESTING ADVANTAGE:

  Production: inject real adapters.
  Unit test: inject mock/in-memory adapters.

  @Test
  void placesOrderSuccessfully() {
      // No Spring, no DB, no Stripe:
      OrderRepository orderRepo = new InMemoryOrderRepository();
      PaymentGateway payment = new AlwaysSucceedPaymentGateway();
      NotificationSender notifier = new CaptureNotificationSender();

      PlaceOrderService service = new PlaceOrderService(orderRepo, payment, notifier);

      OrderId id = service.execute(new PlaceOrderCommand(customerId, items, card));

      assertNotNull(id);
      assertTrue(orderRepo.exists(id));
      assertEquals(1, notifier.getSentNotifications().size());
  }
  // Test: 5ms. No infrastructure. No side effects.

PORT GRANULARITY (common mistake):

  BAD: one big port for everything:
    interface ExternalSystemPort {
        void saveOrder(Order order);
        void sendEmail(Email email);
        String processPayment(Card card, Money amount);
        void uploadFile(File file);
    }
    // Too broad. Violates Interface Segregation Principle.
    // Tests: must mock everything even if only one concern is being tested.

  RIGHT: one port per external concern:
    interface OrderRepository { ... }       // Just order persistence.
    interface EmailSender { ... }           // Just email.
    interface PaymentGateway { ... }        // Just payment.
    interface FileStorage { ... }           // Just files.
    // Each port independently mockable. Service only depends on what it uses.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Ports and Adapters:

- Application core imports frameworks and infrastructure libraries directly
- Test requires running database, email server, payment sandbox
- Adding a Kafka consumer alongside REST: must duplicate domain logic

WITH Ports and Adapters:
→ Core: technology-agnostic; test with any adapter (mock, in-memory, real)
→ Multiple delivery mechanisms: REST, Kafka, CLI all use same input port
→ Swap technology: write new adapter, inject it — core untouched

---

### 🧠 Mental Model / Analogy

> A universal audio output (3.5mm jack port) vs. specific adapters (Bluetooth transmitter, USB-C adapter, cassette tape adapter). The phone defines the port standard (3.5mm or USB-C). Each adapter (car stereo, Bluetooth speaker, headphones) implements this standard. The phone doesn't know what audio output device is connected — it just sends audio through the port. Any new audio device: build an adapter to the port standard. The phone's audio system: unchanged.

"3.5mm port interface" = Output Port (interface defined by application core)
"Bluetooth adapter" = Concrete Driven Adapter
"Car stereo adapter" = Alternative Driven Adapter (implements same port)
"USB-C → 3.5mm dongle" = Adapter that makes an incompatible system work with the port
"Phone's audio system" = Application core (knows only the port, not the adapters)

---

### ⚙️ How It Works (Mechanism)

```
PORTS AND ADAPTERS RUNTIME FLOW:

  INCOMING (Primary/Driving):
  HTTP Request
      │
      ▼
  REST Adapter (Primary)    ← Adapter: converts HTTP → domain command
      │
      ▼ (calls Input Port)
  PlaceOrderUseCase [INPUT PORT INTERFACE]
      │
      ▼ (implemented by)
  PlaceOrderService (Application Core)
      │
      ▼ (calls Output Port)
  OrderRepository [OUTPUT PORT INTERFACE]
      │
      ▼ (implemented by)
  JpaOrderAdapter (Secondary)    ← Adapter: converts domain call → JPA/SQL
      │
      ▼
  PostgreSQL Database
```

---

### 🔄 How It Connects (Mini-Map)

```
Hexagonal Architecture (the pattern Ports and Adapters implements)
        │
        ▼ (ports = the interfaces; adapters = the implementations)
Ports and Adapters ◄──── (you are here)
(primary adapters call input ports; secondary adapters implement output ports)
        │
        ├── Repository Pattern: repositories are output port implementations
        ├── Clean Architecture: "interface adapters" ring = adapters; inner rings define ports
        └── Dependency Inversion: ports enable inversion (core defines interface; infra implements)
```

---

### 💻 Code Example

```java
// Complete Ports and Adapters example for a notification system:

// OUTPUT PORT (defined in application core):
public interface NotificationPort {
    void sendOrderConfirmation(CustomerId customerId, OrderId orderId, Money total);
    void sendShippingNotification(CustomerId customerId, String trackingId);
}

// PRIMARY ADAPTER 1: Sends via email (SendGrid):
@Component
@ConditionalOnProperty("notifications.channel", havingValue = "email")
public class SendGridNotificationAdapter implements NotificationPort {
    private final SendGrid sendGrid;

    @Override
    public void sendOrderConfirmation(CustomerId customerId, OrderId orderId, Money total) {
        Email email = new Email(customerEmail(customerId));
        sendGrid.api(new Request()
            .method(Method.POST)
            .body(buildConfirmationPayload(orderId, total)));
    }
}

// PRIMARY ADAPTER 2: Sends via SMS (Twilio):
@Component
@ConditionalOnProperty("notifications.channel", havingValue = "sms")
public class TwilioNotificationAdapter implements NotificationPort {
    private final TwilioClient twilio;
    @Override
    public void sendOrderConfirmation(CustomerId customerId, OrderId orderId, Money total) {
        twilio.messages.create(customerPhone(customerId),
            new MessageCreator("Order " + orderId + " confirmed. Total: " + total));
    }
}

// TEST ADAPTER (for unit tests):
public class CaptureNotificationAdapter implements NotificationPort {
    private final List<String> sent = new ArrayList<>();
    @Override
    public void sendOrderConfirmation(CustomerId id, OrderId orderId, Money total) {
        sent.add("confirmation:" + orderId);
    }
    public List<String> getSent() { return sent; }
}

// APPLICATION CORE: depends only on the port — doesn't know SendGrid or Twilio exists:
public class OrderService {
    private final NotificationPort notifications;  // Port — not SendGrid, not Twilio.

    public void confirm(OrderId orderId) {
        // ... order logic ...
        notifications.sendOrderConfirmation(customerId, orderId, total);
        // Works with SendGrid, Twilio, or the test capture adapter.
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All interfaces are ports             | A port is an interface at the boundary of the application core — it separates the core from infrastructure. An interface between two domain services (within the core) is not a port. Ports specifically mark the hexagonal boundary: crossing from core to infrastructure or infrastructure to core. Not every interface you create is a port                 |
| The REST controller is a port        | The REST controller is an ADAPTER (primary/driving adapter). The port is the use case interface it calls (e.g., `PlaceOrderInputPort`). Ports are technology-agnostic interfaces defined by the core. The REST controller is technology-specific (uses Spring MVC, HTTP concepts). Don't confuse the interface with the adapter that implements it             |
| You need ports for every method call | Only at the hexagonal boundary (where core meets infrastructure). Domain services calling each other within the core: direct calls, no ports needed. Infrastructure talking to infrastructure (JPA adapter calling Redis adapter): direct calls or infrastructure-level interfaces. Ports: specifically the boundary between the hexagon and the outside world |

---

### 🔥 Pitfalls in Production

**Leaky abstraction — port interface exposes infrastructure-specific concepts:**

```
BAD: Port interface leaks JPA/infrastructure-specific concepts:

  // "Port" that's actually a DAO with JPA leaking through:
  public interface OrderPort {
      Page<OrderJpaEntity> findAll(Pageable pageable);     // WRONG: Pageable and Page are Spring Data types.
      Optional<OrderJpaEntity> findById(UUID id);          // WRONG: OrderJpaEntity is an infrastructure type.
      Specification<OrderJpaEntity> getSpecification(...); // WRONG: Specification is JPA/Spring Data.
  }

  PROBLEMS:
    - Application core: must now import Spring Data (Page, Pageable, Specification).
    - Domain: knows about JPA entities (infrastructure concern).
    - Switch to MongoDB: Pageable and Specification are JPA-specific — must rewrite port.
    - The port: not a "port" at all. It's a JPA DAO interface.

  WRONG TEST:
    // Test must create real or mock Spring Data Pageable objects.
    // Can't test without Spring Data on classpath.

FIX: Port defines domain-centric API. Adapter handles pagination and JPA internally:

  // CLEAN PORT: domain types only:
  public interface OrderRepository {
      Optional<Order> findById(OrderId id);          // Domain type.
      OrderPage findRecent(int pageNum, int pageSize); // Domain pagination (custom record).
      List<Order> findByStatus(OrderStatus status);  // Domain enum.
  }

  // Custom domain pagination type (no Spring dependency):
  public record OrderPage(List<Order> orders, int pageNum, int totalPages, long totalItems) {}

  // JPA ADAPTER: handles Spring Data details internally:
  @Repository
  public class JpaOrderAdapter implements OrderRepository {
      private final SpringDataOrderRepo jpa;

      @Override
      public OrderPage findRecent(int pageNum, int pageSize) {
          // Pageable and Page are INSIDE the adapter — not in the port:
          Pageable pageable = PageRequest.of(pageNum, pageSize, Sort.by("createdAt").descending());
          Page<OrderJpaEntity> page = jpa.findAll(pageable);

          List<Order> orders = page.getContent().stream()
              .map(OrderMapper::toDomain).toList();

          // Convert Spring's Page to domain's OrderPage:
          return new OrderPage(orders, pageNum, page.getTotalPages(), page.getTotalElements());
      }
  }

  // NOW: application core depends only on domain types.
  // Test: create InMemoryOrderAdapter, test with domain types only.
  // Switch to MongoDB: write MongoOrderAdapter implementing same OrderRepository port.
  // Port: zero changes.
```

---

### 🔗 Related Keywords

- `Hexagonal Architecture` — the architectural pattern that Ports and Adapters implements
- `Dependency Inversion Principle` — core defines interfaces; infrastructure implements them
- `Repository Pattern` — repositories are the most common output (driven) port
- `Clean Architecture` — same concept; "interface adapters" ring provides adapters
- `Interface Segregation` — ports should be fine-grained (one interface per concern)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Ports = interfaces the core defines.     │
│              │ Primary adapters → call input ports.     │
│              │ Secondary adapters ← implement output    │
│              │ ports. Core: technology-agnostic.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple delivery mechanisms (REST+Kafka);│
│              │ need testable core; technology may change │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple one-delivery-mechanism CRUD app;  │
│              │ overhead outweighs benefit               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Universal power outlet: core defines   │
│              │  the standard; devices adapt to plug in."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hexagonal Architecture → Dependency      │
│              │ Inversion → Repository Pattern →        │
│              │ Clean Architecture                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your application has a `NotificationPort` with three methods: `sendEmail()`, `sendSms()`, and `sendPushNotification()`. Some services only use email, some only use SMS. According to Interface Segregation Principle: should this be three separate ports or one? What changes if you need a service that sends both email AND SMS — how does it receive both ports? Design the correct port granularity.

**Q2.** A team builds a microservice with both a REST adapter (primary) and a Kafka consumer adapter (primary). Both call the same `ProcessPaymentInputPort`. The REST adapter needs synchronous response (HTTP 200/400). The Kafka consumer needs asynchronous processing (just consume and process; no HTTP response). How does the single `ProcessPaymentInputPort` interface serve both use cases? Does the return type of the interface method cause a conflict? Design the interface to handle both.
