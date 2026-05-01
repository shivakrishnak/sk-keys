---
layout: default
title: "SOLID Principles"
parent: "Software Architecture Patterns"
nav_order: 749
permalink: /software-architecture/solid-principles/
number: "749"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Design Patterns"
used_by: "Clean Code, Refactoring, Spring DI, Domain Model"
tags: #advanced, #architecture, #oop, #design, #principles
---

# 749 — SOLID Principles

`#advanced` `#architecture` `#oop` `#design` `#principles`

⚡ TL;DR — **SOLID** is five object-oriented design principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) that, applied together, produce code that is easier to change, extend, and test.

| #749 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Design Patterns | |
| **Used by:** | Clean Code, Refactoring, Spring DI, Domain Model | |

---

### 📘 Textbook Definition

**SOLID** (Robert C. Martin, "Agile Software Development: Principles, Patterns, and Practices") is an acronym for five design principles: **(S) Single Responsibility Principle (SRP)**: a class should have only one reason to change — one responsibility. **(O) Open/Closed Principle (OCP)**: classes should be open for extension, closed for modification — add behavior by adding code, not changing existing code. **(L) Liskov Substitution Principle (LSP)**: objects of a subtype should be substitutable for objects of the parent type without breaking correctness. **(I) Interface Segregation Principle (ISP)**: clients should not be forced to depend on interfaces they don't use — many small interfaces over one large interface. **(D) Dependency Inversion Principle (DIP)**: high-level modules should not depend on low-level modules — both should depend on abstractions; abstractions should not depend on details. SOLID principles are not laws — they're guidelines. Misapplied: they create over-engineered, overly abstract code. Applied with judgment: they produce maintainable, extensible systems.

---

### 🟢 Simple Definition (Easy)

Five rules for building with LEGO bricks instead of carving from stone. S: each LEGO brick does one thing. O: add new structures by adding bricks, not reshaping existing bricks. L: any standard LEGO brick fits where another standard LEGO brick fits. I: bricks have the specific connector they need, not every possible connector. D: your design blueprint uses "standard LEGO connector" not "specific red 2x4 brick" — anything meeting the standard works. Together: your LEGO model is easy to extend and modify.

---

### 🔵 Simple Definition (Elaborated)

A `UserService` that handles: user registration, email sending, password hashing, profile updates, and user deletion. One class, five responsibilities. Violates SRP. Fix: `UserRegistrationService`, `EmailService`, `PasswordHasher` — each owns one job. Now adding a new email provider: only `EmailService` changes. Adding a new hashing algorithm: only `PasswordHasher` changes. OCP: `EmailService` has `send(email)` — add SMS without touching EmailService (extend by adding `SmsService`, not modifying `EmailService`). DIP: `UserRegistrationService` depends on `EmailPort` interface, not `SendGridEmailService` directly — swap email providers without changing registration logic.

---

### 🔩 First Principles Explanation

**Each principle with violation, fix, and real benefit:**

```
S — SINGLE RESPONSIBILITY PRINCIPLE (SRP):

  "A class should have only one reason to change."
  
  VIOLATION:
    class OrderReport {
        Order loadOrder(Long id) { return orderRepo.findById(id); } // Data access
        BigDecimal calculateDiscount(Order order) { ... }           // Business logic
        String formatAsPdf(Order order) { ... }                     // Presentation
        void sendByEmail(Order order, String email) { ... }         // Infrastructure
    }
    // Changes when: data access changes, discount rules change, PDF format changes, or email changes.
    // 4 reasons to change = 4 responsibilities.
    
  FIX:
    class OrderRepository { Order findById(Long id) { ... } }
    class DiscountCalculator { BigDecimal calculate(Order order) { ... } }
    class OrderPdfFormatter { String format(Order order) { ... } }
    class OrderEmailSender { void send(Order order, Email to) { ... } }
    // Each: 1 reason to change. Change email provider: touch only OrderEmailSender.
    
  NOTE: SRP ≠ "one method per class". Responsibility = "one reason to change."
    A rich domain entity (Order) with methods confirm(), cancel(), ship(): ONE responsibility.
    All those methods serve "maintaining order lifecycle" — one reason to change.

O — OPEN/CLOSED PRINCIPLE (OCP):

  "Open for extension, closed for modification."
  
  VIOLATION:
    class DiscountCalculator {
        BigDecimal calculate(Order order, CustomerType type) {
            if (type == REGULAR) return order.total().multiply(0.05);
            if (type == PREMIUM) return order.total().multiply(0.10);
            if (type == VIP)     return order.total().multiply(0.15);
            // Add new customer type? MODIFY this method. Risk: break existing types.
        }
    }
    
  FIX (Strategy pattern / polymorphism):
    interface DiscountStrategy {
        Money calculateDiscount(Order order);
    }
    
    class RegularCustomerDiscount implements DiscountStrategy {
        public Money calculateDiscount(Order order) { return order.total().times(0.05); }
    }
    
    class PremiumCustomerDiscount implements DiscountStrategy {
        public Money calculateDiscount(Order order) { return order.total().times(0.10); }
    }
    
    // Add new customer type: ADD new class. Don't modify existing classes.
    class EnterpriseCustomerDiscount implements DiscountStrategy {
        public Money calculateDiscount(Order order) { return order.total().times(0.20); }
    }
    
L — LISKOV SUBSTITUTION PRINCIPLE (LSP):

  "Subtypes must be substitutable for their base types."
  
  VIOLATION:
    class Rectangle {
        void setWidth(int w) { this.width = w; }
        void setHeight(int h) { this.height = h; }
        int area() { return width * height; }
    }
    
    class Square extends Rectangle {
        void setWidth(int w) { this.width = w; this.height = w; }  // Forces square constraint
        void setHeight(int h) { this.width = h; this.height = h; } // Both dimensions change
    }
    
    // Code that works with Rectangle:
    void resizeToExpectedArea(Rectangle r) {
        r.setWidth(5);
        r.setHeight(3);
        assert r.area() == 15;  // FAILS for Square: setting height to 3 also set width to 3
        // Square is NOT a substitutable Rectangle. LSP violated.
    }
    
  FIX: Don't inherit Square from Rectangle. Use a common interface (Shape.area()).
    Or: make both immutable (value objects: no setters; constructor-based).
    
I — INTERFACE SEGREGATION PRINCIPLE (ISP):

  "Clients should not depend on interfaces they don't use."
  
  VIOLATION:
    interface UserService {
        User findById(Long id);
        void register(RegisterRequest req);
        void updateProfile(Long id, ProfileUpdate update);
        void delete(Long id);
        void sendPasswordReset(String email);
        List<User> findAll();
        void exportToCsv(OutputStream stream);
    }
    // Admin panel: needs findAll() + exportToCsv().
    // Registration form: needs register().
    // Both implement/depend on ALL 7 methods. Change exportToCsv: admin and registration affected.
    
  FIX: Multiple small interfaces:
    interface UserQueryService { User findById(Long id); List<User> findAll(); }
    interface UserRegistrationService { void register(RegisterRequest req); }
    interface UserAdminService extends UserQueryService { void exportToCsv(OutputStream out); }
    // Admin panel: implements UserAdminService (3 methods). Registration: UserRegistrationService.
    
D — DEPENDENCY INVERSION PRINCIPLE (DIP):

  "Depend on abstractions, not concretions."
  
  VIOLATION:
    class OrderService {
        private final MySqlOrderRepository repo;  // Concrete class! Hardwired to MySQL.
        private final SendGridEmailService email; // Concrete class! Hardwired to SendGrid.
        
        // Test: must use real MySQL + real SendGrid. Slow. Expensive. Fragile.
        // Swap to PostgreSQL: must change OrderService. Swap email: must change OrderService.
    }
    
  FIX: Depend on interfaces (abstractions):
    class OrderService {
        private final OrderRepository repo;        // Interface.
        private final EmailPort emailPort;          // Interface.
        
        // Test: inject MockOrderRepository, MockEmailPort. Fast. No network.
        // Production: inject JpaOrderRepository + SendGridEmailAdapter.
        // Swap MySQL → PostgreSQL: only the implementation changes; OrderService unchanged.
    }
    
    // Spring DI: the framework injects the concrete implementation at runtime.
    @Service
    class OrderService {
        OrderService(OrderRepository repo, EmailPort email) { ... }  // DIP via constructor injection.
    }
    
APPLYING SOLID TOGETHER:

  class OrderFulfillmentService {
      private final OrderRepository orderRepo;        // DIP: interface, not JPA class
      private final FulfillmentStrategy fulfillment; // DIP + OCP: strategy for fulfillment
      private final OrderEventPublisher events;       // DIP: interface, not Kafka class
      
      // SRP: this class does ONE thing — orchestrate fulfillment.
      // ISP: depends on focused interfaces (not a giant "OrderService" interface).
      // LSP: any OrderRepository substitutable; any FulfillmentStrategy substitutable.
      // OCP: add new fulfillment strategy — extend, don't modify this class.
      
      void fulfill(OrderId orderId) {
          Order order = orderRepo.findById(orderId).orElseThrow();
          fulfillment.fulfill(order);
          events.publish(new OrderFulfilledEvent(orderId));
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT SOLID:
- God classes: one class changes when anything in the system changes
- Modification requires understanding the whole system (high coupling)
- Tests require real databases, real email servers (dependencies not inverted)

WITH SOLID:
→ Change discount rules: touch only `DiscountCalculator` (SRP)
→ Add new discount type: add class, don't modify existing (OCP)
→ Test `OrderService` without a real database: inject mock repository (DIP)

---

### 🧠 Mental Model / Analogy

> SOLID as five rules for a good toolbox. SRP: one tool per job — screwdriver just screws, not saws. OCP: add new tools to the box, don't reshape the screwdriver into a drill. LSP: any Phillips #2 bit fits any Phillips #2 driver (interchangeable). ISP: a carpenter's toolbox, not a toolbox with hospital surgical tools (use only what's relevant). DIP: the carpenter asks for "something that drives screws" (abstraction), not "specifically the DeWalt DCD777" — any compatible driver works.

"One tool per job" = SRP (one responsibility per class)
"Add tools, don't reshape existing ones" = OCP
"Any compatible bit fits any driver" = LSP (substitutable subtypes)
"Carpenter's toolbox, not surgeon's" = ISP (relevant interfaces)
"Something that drives screws" = DIP (interface, not concrete class)

---

### ⚙️ How It Works (Mechanism)

```
DEPENDENCY INJECTION (DIP in practice — Spring):

  High-level: OrderService
  Abstraction: OrderRepository (interface)
  Low-level:   JpaOrderRepository (implements OrderRepository)
  
  Spring creates and injects:
    new OrderService(new JpaOrderRepository(entityManager))
    // OrderService never sees JpaOrderRepository. Only the interface.
    
  Test injection:
    new OrderService(mock(OrderRepository.class))
    // Instant unit test: no DB, no network.
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming (inheritance, encapsulation, polymorphism)
        │
        ▼ (principles for using OOP well)
SOLID Principles ◄──── (you are here)
(SRP, OCP, LSP, ISP, DIP — guidelines for maintainable OOP design)
        │
        ├── Design Patterns: many patterns implement SOLID (Strategy → OCP, Factory → DIP)
        ├── Dependency Injection Pattern: the practical implementation of DIP
        ├── Clean Architecture: built on SOLID; DIP enforces layer independence
        └── Refactoring: SOLID violations identify what to refactor (God class → SRP)
```

---

### 💻 Code Example

```java
// All 5 principles in one well-designed notification system:

// ISP: separate notification interfaces:
interface EmailNotifier { void sendEmail(Email to, EmailContent content); }
interface SmsNotifier { void sendSms(PhoneNumber to, String message); }
interface PushNotifier { void sendPush(DeviceToken token, PushMessage message); }

// OCP: add new channel by adding class, not modifying existing:
class SendGridEmailNotifier implements EmailNotifier {
    public void sendEmail(Email to, EmailContent content) { /* SendGrid API */ }
}
class TwilioSmsNotifier implements SmsNotifier {
    public void sendSms(PhoneNumber to, String message) { /* Twilio API */ }
}

// SRP: each class does one thing:
class OrderConfirmationNotifier { // Sends order confirmations only.
    private final EmailNotifier email; // DIP: depends on interface
    private final SmsNotifier sms;     // DIP: depends on interface
    
    // LSP: any EmailNotifier subtype works (SendGrid, SES, Mailgun)
    void notifyOrderConfirmed(Order order, Customer customer) {
        email.sendEmail(customer.email(), OrderConfirmationEmail.for(order));
        if (customer.hasSmsPreference()) {
            sms.sendSms(customer.phone(), "Order #" + order.id() + " confirmed.");
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SOLID means one method per class / interface per class | SRP: one REASON TO CHANGE, not one method. A rich domain object with 10 methods all serving its single domain responsibility satisfies SRP. Over-applying SRP creates a fragmented codebase with dozens of trivial classes. Use judgment: "does this class have multiple reasons to change?" If no: it's fine |
| DIP means always using an interface | DIP: depend on abstractions. In many cases: a well-designed abstract class, a concrete class that won't change, or a simple function serves as the abstraction. Not every dependency needs a Java interface. Rule: interface needed when (1) multiple implementations possible, (2) need to mock in tests, or (3) implementation might change |
| SOLID is always worth applying | Misapplied SOLID produces over-engineered code. A simple 3-class application doesn't need the Strategy pattern for every if/else. SOLID principles are DESIGN PRINCIPLES for managing COMPLEXITY. Apply them where code IS complex and likely to change. A simple CRUD form with 1 rule doesn't need an Abstract Factory |

---

### 🔥 Pitfalls in Production

**ISP violation — fat interface causes unintended dependencies:**

```java
// BAD: Fat interface — clients depend on methods they don't use:
interface OrderService {
    Order findById(OrderId id);         // Needed by: queries, API
    void place(PlaceOrderCommand cmd);  // Needed by: checkout flow
    void cancel(CancelOrderCommand cmd); // Needed by: customer support
    void ship(ShipOrderCommand cmd);    // Needed by: warehouse system
    List<Order> findAll();              // Needed by: admin panel only
    void exportOrdersCsv(OutputStream stream); // Needed by: finance only
}

// Result: Warehouse system implements OrderService.
// When exportOrdersCsv changes: warehouse system must be recompiled/retested.
// Warehouse never calls exportOrdersCsv — but depends on it via the interface.

// FIX: Focused interfaces per client:
interface OrderQueryPort { Order findById(OrderId id); }
interface OrderCommandPort { void place(PlaceOrderCommand cmd); void cancel(CancelOrderCommand cmd); }
interface OrderShippingPort { void ship(ShipOrderCommand cmd); }
interface OrderAdminPort extends OrderQueryPort { List<Order> findAll(); void exportCsv(OutputStream out); }

// Warehouse: only OrderShippingPort. Finance: only OrderAdminPort.
// Change export format: only finance code affected. Warehouse: unaffected.
```

---

### 🔗 Related Keywords

- `Dependency Injection Pattern` — practical implementation of the Dependency Inversion Principle
- `Strategy Pattern` — enables Open/Closed Principle (add new strategies without modification)
- `Refactoring` — identifying SOLID violations guides what to refactor
- `Clean Architecture` — builds on SOLID, especially DIP for layer independence
- `Design Patterns` — many GoF patterns are solutions to applying SOLID principles

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ S: one reason to change. O: extend,       │
│              │ don't modify. L: subtypes substitutable.  │
│              │ I: focused interfaces. D: depend on       │
│              │ abstractions.                             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Class has multiple reasons to change;     │
│              │ adding features requires modifying stable │
│              │ code; testing requires real dependencies  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Over-engineering: applying all 5 to every │
│              │ simple class creates abstraction overhead │
│              │ without benefit. Use with judgment.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Five rules for a good toolbox: one tool  │
│              │  per job; add tools, don't reshape;       │
│              │  compatible parts; relevant tools only;  │
│              │  ask for what you need, not what brand." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Injection → Strategy Pattern → │
│              │ Clean Architecture → Refactoring          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `ReportService` generates monthly reports. It loads data, formats it as HTML or PDF, and emails or uploads to S3. It's one class with 200 lines. Applying SRP: identify ALL reasons it could change. Then split it into classes such that each class has exactly one reason to change. What interfaces do you define, and how do DIP and ISP apply to your split?

**Q2.** A `Bird` superclass has `fly()` method. `Penguin extends Bird` overrides `fly()` to throw `UnsupportedOperationException`. Code that does `bird.fly()` breaks when given a penguin — LSP violated. But the business requirement is real: penguins are birds. How do you redesign the `Bird` hierarchy to satisfy both requirements (penguins are birds AND code that calls bird.fly() works without special cases)? What does this tell you about when inheritance is appropriate vs. when composition is better?
