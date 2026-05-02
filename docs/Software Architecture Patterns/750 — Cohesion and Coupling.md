---
layout: default
title: "Cohesion and Coupling"
parent: "Software Architecture Patterns"
nav_order: 750
permalink: /software-architecture/cohesion-and-coupling/
number: "750"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "SOLID Principles, Object-Oriented Programming, Modular Monolith"
used_by: "Software design, Refactoring, Architecture review, Module design"
tags: #intermediate, #architecture, #design, #principles, #refactoring
---

# 750 — Cohesion and Coupling

`#intermediate` `#architecture` `#design` `#principles` `#refactoring`

⚡ TL;DR — **Cohesion** measures how related a module's elements are to each other; **Coupling** measures how much modules depend on each other — good design maximizes cohesion (high cohesion) while minimizing coupling (low coupling) for maintainability and changeability.

| #750            | Category: Software Architecture Patterns                         | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | SOLID Principles, Object-Oriented Programming, Modular Monolith  |                 |
| **Used by:**    | Software design, Refactoring, Architecture review, Module design |                 |

---

### 📘 Textbook Definition

**Cohesion** and **Coupling** are fundamental software design metrics originally described by Larry Constantine and Edward Yourdon ("Structured Design," 1979). **Cohesion** (internal quality): the degree to which elements within a module (class, package, service) belong together and serve a single, well-defined purpose. **Coupling** (external quality): the degree of interdependence between modules. Goal: **High Cohesion** — elements within a module are strongly related and serve one clear purpose. **Low Coupling** — modules interact through minimal, well-defined interfaces, with minimal knowledge of each other's internals. The tension: adding responsibilities to one module increases cohesion violations; splitting into many modules increases coupling (more inter-module calls). The art: finding the boundary where elements belong together (cohesion) without creating dependency nightmares (coupling).

---

### 🟢 Simple Definition (Easy)

A kitchen drawer. High cohesion: a drawer with only cooking utensils — spatulas, ladles, whisks. Everything in the drawer serves "cooking." Easy to find what you need. Low coupling: the cooking drawer can be modified (add a new spatula) without affecting the dining drawer. Low cohesion: a drawer with a spatula, a battery, a birthday candle, and a USB cable. Hard to know what's in there or why. High coupling: the cooking drawer is physically attached to the dining drawer — moving one requires moving the other.

---

### 🔵 Simple Definition (Elaborated)

A well-designed payment module: `PaymentService` (processes charges), `PaymentRepository` (stores payments), `RefundCalculator` (computes refunds) — all related to payment. High cohesion: they belong together. `PaymentService` only calls its own module's components. Low coupling: it publishes a `PaymentProcessedEvent` rather than directly calling `OrderService.markAsPaid()`. Compare: a badly designed `UtilityService` with `calculateDiscount()`, `sendEmail()`, `parseDate()`, `logMetrics()` — no cohesion (nothing relates). It's called by 20 different classes (high coupling). Change `parseDate()`: 20 classes potentially affected.

---

### 🔩 First Principles Explanation

**Types of cohesion (from worst to best) and types of coupling (from worst to best):**

```
COHESION TYPES (Constantine & Yourdon hierarchy, worst → best):

  1. COINCIDENTAL COHESION (worst):
     Elements in module: unrelated. Just happened to be put together.

     class UtilityHelper {
         void sendEmail(String to, String body) { ... }
         BigDecimal calculateTax(BigDecimal amount) { ... }
         String formatDate(LocalDate date) { ... }
         void logToConsole(String msg) { ... }
     }
     // Why are these together? No reason. Coincidence.
     // Result: "utility" / "helper" / "manager" named classes → sign of coincidental cohesion.

  2. LOGICAL COHESION:
     Elements perform similar operations. Type switches to determine which.

     class InputHandler {
         void handle(String input, String type) {
             if ("keyboard".equals(type)) handleKeyboard(input);
             else if ("mouse".equals(type)) handleMouse(input);
             else if ("touch".equals(type)) handleTouch(input);
         }
     }
     // "Logically similar" but different in execution. Type flag needed.

  3. PROCEDURAL COHESION:
     Elements follow a fixed sequence. Like a checklist.

     class UserRegistrationProcedure {
         void validate(UserData data) { ... }
         void hash(String password) { ... }
         void save(User user) { ... }
         void sendEmail(String email) { ... }
     }
     // Only makes sense executed in order. Each method: weak in isolation.

  4. COMMUNICATIONAL COHESION:
     Elements operate on the same data.

     class OrderPrinter {
         void printHeader(Order order) { ... }
         void printItems(Order order) { ... }
         void printTotal(Order order) { ... }
     }
     // All work on Order, but purpose is just "printing" not the concept itself.

  5. SEQUENTIAL COHESION:
     Output of one element is input of another. Pipeline.

     class OrderProcessor {
         Order validate(OrderRequest request) { ... }     // returns Order
         Order applyDiscounts(Order order) { ... }        // takes Order
         Order checkInventory(Order order) { ... }        // takes Order
         OrderConfirmation save(Order order) { ... }      // takes Order
     }
     // Better: elements form a coherent pipeline.

  6. FUNCTIONAL COHESION (best):
     Everything serves ONE well-defined purpose. Remove any element: module incomplete.

     class EmailService {
         void send(Email email) { connect(); authenticate(); transmit(email); disconnect(); }
     }
     // All elements serve ONE purpose: sending email. Nothing extraneous.

  In DDD terms: INFORMATIONAL COHESION (often considered superior for OO):

     class Order {
         confirm(payment) { ... }
         cancel(reason)  { ... }
         ship(tracking)  { ... }
         total()         { ... }
     }
     // All elements work on the SAME domain concept (Order). One reason to change.
     // This is what SRP means in OOP: informational/functional cohesion.

COUPLING TYPES (worst → best):

  1. CONTENT COUPLING (worst): A modifies internals of B.

     class OrderProcessor {
         void process(Order order) {
             order.status = "CONFIRMED";  // Directly accesses field! Not via method.
             order.items.clear();         // Directly mutates internal state!
         }
     }

  2. COMMON COUPLING: Multiple modules share global state.

     class GlobalConfig { static String DB_URL = "jdbc:mysql://..."; }
     class OrderRepo { GlobalConfig.DB_URL ... }  // Both modules share global state.
     class UserRepo { GlobalConfig.DB_URL ... }

  3. CONTROL COUPLING: A passes a flag telling B what to do.

     class Processor {
         void process(Order order, boolean isPremium) {
             if (isPremium) { ... } else { ... }
         }
     }
     // Caller controls processor's behavior via flag. Strategy pattern fixes this.

  4. STAMP COUPLING: A passes more data to B than B needs.

     void sendWelcomeEmail(Customer customer) { /* only needs customer.email */ }
     // Should be: sendWelcomeEmail(Email email)

  5. DATA COUPLING (best for procedure-oriented):
     A passes only the data B needs (primitive types, simple DTOs).

     void calculateTax(BigDecimal amount, TaxRate rate) { ... }

  6. MESSAGE COUPLING (best for OO/event-driven):
     A sends a message/event; B reacts. A doesn't know B.

     eventBus.publish(new OrderPlacedEvent(orderId, total));
     // A (OrderService) knows nothing about B (EmailService). Zero coupling.

HIGH COHESION + LOW COUPLING PRINCIPLE:

  "High cohesion within; low coupling between."

  Package/Module design:
    GOOD: Each package owns one concept. Classes within call each other freely.
          Between packages: only through public API.

    BAD: Classes scattered; util package with everything; cross-package imports everywhere.

  Metrics to watch:
    - "Utility" / "Helper" / "Manager" class names → sign of low cohesion.
    - A class imported by 30 other classes → sign of high coupling.
    - A test requires 10 mock objects → sign of high coupling.
    - A PR touches 15 files for a simple feature → sign of low cohesion + high coupling.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding Cohesion/Coupling:

- Feature change requires editing 15 files across 6 packages — high coupling
- `UtilityService` with 50 methods: no one knows what's in it — low cohesion
- Test setup requires 8 mocks: tightly coupled class impossible to test in isolation

WITH High Cohesion + Low Coupling:
→ Feature change touches 2-3 focused classes (high cohesion, low coupling)
→ Each class clearly named: `OrderCancellationService` owns cancellation — everything related
→ Test needs 1-2 mocks: loosely coupled class is easily tested

---

### 🧠 Mental Model / Analogy

> Organs in a body vs. a sack of body parts. High cohesion: the heart — it pumps blood, period. Every part of the heart (ventricles, valves, muscle) contributes to pumping blood. Low coupling: the heart connects to the circulatory system through defined interfaces (aorta, veins) — not directly fused to the liver. Low cohesion: a "utility organ" that sometimes pumps blood, sometimes digests food, and sometimes filters air — no clear purpose. High coupling: the heart directly attached to the liver (change the liver: must change the heart).

"Heart (pumps blood only)" = high cohesion
"Connected via aorta/veins (defined interface)" = low coupling
"Utility organ (multiple unrelated functions)" = low cohesion
"Directly fused to liver" = high coupling (change one, change both)

---

### ⚙️ How It Works (Mechanism)

```
MEASURING COUPLING (Afferent/Efferent):

  Afferent coupling (Ca): how many classes depend ON this class?
    High Ca: this class is hard to change (many dependents will break).

  Efferent coupling (Ce): how many classes does this class depend on?
    High Ce: this class is fragile (depends on many things that can change).

  Instability: I = Ce / (Ca + Ce)
    I = 0: fully stable (others depend on it; it depends on nothing).
    I = 1: fully unstable (depends on others; nothing depends on it).

  Good design: stable classes have low instability (I near 0).
  Good design: volatile classes have high instability (I near 1; they depend on stable abstractions).
```

---

### 🔄 How It Connects (Mini-Map)

```
SOLID Principles (SRP directly addresses cohesion; DIP addresses coupling)
        │
        ▼
Cohesion and Coupling ◄──── (you are here)
(design quality metrics: high cohesion within modules, low coupling between modules)
        │
        ├── Modular Monolith: module design goal is high cohesion per module, low inter-module coupling
        ├── Microservices: service decomposition follows cohesion/coupling principles
        ├── Domain Events: event-driven communication achieves lowest coupling (message coupling)
        └── Refactoring: code smells (God class = low cohesion; feature envy = high coupling)
```

---

### 💻 Code Example

```java
// LOW COHESION (bad) — utility class with unrelated methods:
class ApplicationUtils {
    static BigDecimal calculateVat(BigDecimal amount) { ... }
    static String maskCreditCard(String card) { ... }
    static void sendSlackMessage(String channel, String msg) { ... }
    static Optional<User> parseJwtToken(String token) { ... }
    static List<String> splitCsv(String csv) { ... }
}
// Change VAT rules: touch ApplicationUtils. Everyone using ApplicationUtils recompiles.

// HIGH COHESION (good) — each class has one focused purpose:
class VatCalculator { BigDecimal calculate(BigDecimal amount, VatRate rate) { ... } }
class PaymentMasker { String maskCard(CardNumber card) { ... } }
class SlackNotifier { void send(SlackChannel channel, SlackMessage msg) { ... } }
class JwtParser { Optional<UserClaims> parse(String token) { ... } }

// LOW COUPLING (domain events):
class OrderService {
    void place(PlaceOrderCommand cmd) {
        Order order = Order.place(customer, cart);
        orderRepo.save(order);
        // Publish event — NOT: emailService.send(), loyaltyService.grant(), etc.
        eventBus.publish(new OrderPlacedEvent(order.id(), order.total()));
        // Zero coupling to email, loyalty, analytics services.
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High cohesion always means small classes                | Cohesion is about relatedness, not size. A rich domain entity `Order` with 15 methods all serving "order lifecycle management" has HIGH cohesion despite being a large class. A small `UtilityHelper` with 5 unrelated methods has LOW cohesion                                                                                    |
| Coupling is always bad                                  | SOME coupling is necessary — modules must interact. The goal is LOW coupling (minimal, well-defined interfaces), not ZERO coupling (which means no interaction). Coupling is bad when it's tight: internal details exposed, implementation-level dependencies. Loose coupling (via interfaces, events) is acceptable and necessary |
| Microservices always have lower coupling than monoliths | Microservices can have HIGHER coupling if designed poorly: synchronous REST calls between services create network coupling. A monolith with well-designed module boundaries and in-process event communication can have LOWER coupling than a distributed system where service A synchronously calls B which calls C               |

---

### 🔥 Pitfalls in Production

**Feature envy — sign of high coupling, low cohesion:**

```java
// BAD: CustomerDiscountCalculator "envies" Order's internals — high coupling:
class CustomerDiscountCalculator {
    BigDecimal calculate(Customer customer, Order order) {
        // This method accesses 8 Order fields/methods directly:
        if (order.getItems().size() > 5 &&
            order.getTotal().compareTo(new BigDecimal("100")) > 0 &&
            !order.hasPromoCodeApplied() &&
            order.getCustomer().getMembershipTier() == PREMIUM) {
            return order.getTotal().multiply(new BigDecimal("0.15"));
        }
        // ...
    }
}
// "Feature envy": CustomerDiscountCalculator uses Order more than its own fields.
// Sign: this method belongs ON Order, not in CustomerDiscountCalculator.

// FIX: Move to where the data lives (high cohesion):
class Order {
    BigDecimal calculatePremiumDiscount(Customer customer) {
        // Uses its OWN data. Cohesive. CustomerDiscountCalculator: no longer needed.
        if (items.size() > 5 && total.compareTo(HUNDRED) > 0 && !hasPromoCode) {
            if (customer.isPremium()) return total.multiply(FIFTEEN_PERCENT);
        }
        return BigDecimal.ZERO;
    }
}
```

---

### 🔗 Related Keywords

- `SOLID Principles` — SRP directly addresses cohesion (one reason to change); DIP addresses coupling
- `Domain Model` — high informational cohesion: all elements serve one domain concept
- `Bounded Context` — module boundary where internal cohesion is high, external coupling is low
- `Domain Events` — enable message coupling (loosest form of coupling between modules)
- `Refactoring` — code smells (God class, feature envy) are cohesion and coupling problems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ High cohesion: elements belong together.  │
│              │ Low coupling: modules interact minimally. │
│              │ Design goal: maximize both simultaneously. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Evaluating design: "does this class do one│
│              │ clear thing?" and "how many things depend │
│              │ on this?"                                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Over-splitting into too many tiny classes │
│              │ creates artificial coupling between the   │
│              │ fragments (balance required)              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Heart: pumps blood only (high cohesion), │
│              │  connected via aorta not fused to liver  │
│              │  (low coupling)."                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SOLID Principles → Bounded Context →      │
│              │ Domain Events → Refactoring               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An `OrderService` class has these methods: `placeOrder()`, `cancelOrder()`, `getOrderHistory()`, `calculateLoyaltyPoints()`, `sendOrderConfirmation()`, and `generateMonthlyReport()`. Evaluate this class for both cohesion type and coupling. Which methods should stay together, which should be extracted? After extraction, how does it change the coupling between the resulting classes? Is it possible to reduce coupling while increasing cohesion through the same extraction?

**Q2.** In a microservices architecture, Service A calls Service B synchronously (REST), Service B calls Service C synchronously. This chain introduces data coupling (B depends on A's request format) and temporal coupling (A must wait for B which must wait for C). Compare: if you redesign so A publishes an event, B handles it and publishes another event, C handles that — what changes in coupling? What NEW coupling might you introduce (event schema coupling)? Is event-driven always lower coupling than synchronous?
