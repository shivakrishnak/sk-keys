---
layout: default
title: "Cohesion"
parent: "Software Architecture Patterns"
nav_order: 763
permalink: /clean-code/cohesion/
number: "763"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Single Responsibility Principle, Module Design, Encapsulation
used_by: Coupling, Refactoring, Package Design, Code Review
tags: #architecture, #pattern, #intermediate, #testing
---

# 763 — Cohesion

`#architecture` `#pattern` `#intermediate` `#testing`

⚡ TL;DR — The degree to which the elements inside a module belong together and serve a single, well-defined purpose.

| #763 | category: Software Architecture Patterns
|:---|:---|:---|
| **Depends on:** | Single Responsibility Principle, Module Design, Encapsulation | |
| **Used by:** | Coupling, Refactoring, Package Design, Code Review | |

---

### 📘 Textbook Definition

**Cohesion** is a measure of how strongly related and focused the responsibilities of a single module (class, method, package, or microservice) are. High cohesion means every element within the module directly contributes to a single, clearly defined purpose. Low cohesion means the module juggles multiple unrelated concerns — becoming a "god class" or utility dumping ground. Cohesion is one of the two fundamental metrics of module quality alongside coupling; ideally modules should have high cohesion and low coupling.

---

### 🟢 Simple Definition (Easy)

Cohesion is about how much a class or function "sticks to one job." A highly cohesive class does one thing and does it well — all its methods and fields support that single purpose.

---

### 🔵 Simple Definition (Elaborated)

When you open a class and every method inside it clearly belongs to the same concept, that class has high cohesion. When you open a class and find methods for parsing, UI rendering, database access, and email sending all jumbled together, that's low cohesion. Low cohesion is a warning sign that forces you to understand the entire class to use any part of it, and changes to one concern accidentally break others. The Single Responsibility Principle is the design rule that directly enforces high cohesion.

---

### 🔩 First Principles Explanation

**Problem — the "utility belt" class:**

Early codebases often grow a `Utils`, `Manager`, or `Helper` class that accumulates responsibility over time:

```java
// LOW COHESION — doing unrelated things
class OrderUtils {
  public double calculateDiscount(Order o) { ... }
  public void sendConfirmationEmail(Order o) { ... }
  public String formatAddressLabel(Address a) { ... }
  public boolean validateCreditCard(String cc) { ... }
  public Order parseXmlOrder(String xml) { ... }
}
```

**Problem cascade from low cohesion:**
```
┌─────────────────────────────────────────────────┐
│  LOW-COHESION EFFECTS                           │
│                                                 │
│  Hard to name: "Utils" — what does it do?       │
│  Hard to test: test setup requires all concerns │
│  Hard to change: every PR touches this file     │
│  Hard to reuse: carry unrelated deps with you  │
│  Hard to distribute: which team owns it?        │
└─────────────────────────────────────────────────┘
```

**Insight — group by concept, not by accident:**

The question to ask for every method you add: "Does this belong to the core concept this class represents?" If the answer is "not really, but it's convenient," extract it.

```java
// HIGH COHESION — each class owns one concept
class OrderDiscountCalculator {
  public double calculate(Order o) { ... }
  public double calculateBulk(Order o, int qty) { ... }
}

class OrderConfirmationMailer {
  public void send(Order o) { ... }
}

class CreditCardValidator {
  public boolean validate(String cc) { ... }
}
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT cohesion awareness:**

```
Without enforcing cohesion:

  Problem 1: Merge conflict magnet
    One low-cohesion class touched by every feature
    → 5 engineers merge conflicts daily

  Problem 2: Test coupling
    Unit test for discount calc must mock emailer
    → 15 unrelated mocks per test → fragile tests

  Problem 3: Deployment coupling
    Discount logic and email logic in same module
    → one email bug → redeploy entire order service
    → unnecessary risk

  Problem 4: Cognitive overload
    New engineer must understand 20 concepts
    to change one 3-line method
```

**WITH high cohesion:**

```
→ Each module has one reason to change
→ Tests are simple — only relevant doubles needed
→ Teams own distinct, non-overlapping modules
→ Extraction and reuse is natural
→ Naming becomes trivial — the concept IS the name
```

---

### 🧠 Mental Model / Analogy

> Cohesion is like a **specialist clinic vs a general emergency room**. A cardiologist clinic sees only heart patients — every doctor, every tool, every form is focused on that one domain. A general ER handles broken bones, strokes, childbirth, and poison all in the same space. When you need cardiac care, you want the focused specialist, not the place where everyone is doing different things at once.

"Specialist clinic" = high-cohesion class — one clear purpose
"General emergency room" = low-cohesion class — handles everything
"Domain-specific tools" = methods that directly serve the class's concept
"Mismatched equipment" = methods that don't belong — tell-tale sign of low cohesion

---

### ⚙️ How It Works (Mechanism)

**The cohesion spectrum:**

```
┌────────────────────────────────────────────────────────┐
│  COHESION TYPES (from low to high)                     │
├────────────────────────────────────────────────────────┤
│  Coincidental  → functions grouped by developer whim   │
│  Logical       → grouped by category ("all email fn")  │
│  Temporal      → run at same time (init methods)       │
│  Procedural    → sequential steps in a procedure       │
│  Communicational→ operate on same data                 │
│  Functional    → all elements contribute to one output │
│                  ← THIS is the target                  │
└────────────────────────────────────────────────────────┘
```

**Measuring cohesion — LCOM (Lack of Cohesion of Methods):**

LCOM counts how many method pairs in a class share no instance variables. High LCOM = low cohesion = split candidate.

```java
class Bad {           // LCOM = 2 (two unrelated sets)
  int x;
  int y;
  
  void setX(int v) { x = v; }   // touches x
  void setY(int v) { y = v; }   // touches y — unrelated!
  int maths() { return x + 1; } // touches x
}
// Split into two classes: one for x, one for y
```

**Field-method affinity test:**

Every field should appear in most methods. If you can split the class into group A (uses fields 1-3) and group B (uses fields 4-6) with no overlap — that class should be two classes.

---

### 🔄 How It Connects (Mini-Map)

```
Single Responsibility Principle
(the rule)
        ↓
  COHESION  ← you are here
  (the metric that SRP enforces)
        ↓
  High cohesion → low coupling (natural consequence)
        ↓
  ┌──────────────────────────────────────────────┐
  │  Coupling (the complementary metric)         │
  │  Package Design (cohesion at package level)  │
  │  Microservices (cohesion at service level)   │
  │  Refactoring: Extract Class / Extract Method │
  └──────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — Refactoring low to high cohesion:**

```java
// BAD: low-cohesion service class
class UserService {
  public User findById(long id) { ... }
  public void save(User u) { ... }
  public void sendWelcomeEmail(User u) { ... }  // unrelated
  public String generateAvatarUrl(User u) { ... }// unrelated
  public boolean validatePassword(String pw) { ... }// unrelated
}

// GOOD: split by concept
class UserRepository {
  public User findById(long id) { ... }
  public void save(User u) { ... }
}

class UserOnboardingMailer {
  public void sendWelcome(User u) { ... }
}

class AvatarService {
  public String generateUrl(User u) { ... }
}

class PasswordValidator {
  public boolean validate(String pw) { ... }
}
```

**Example 2 — Method-level cohesion:**

```java
// BAD: method does too much — low cohesion
public Order processOrder(OrderRequest req) {
  // 1. validate
  if (req.getItems().isEmpty()) throw new IllegalArgumentException();
  // 2. calculate
  double total = req.getItems().stream()
      .mapToDouble(i -> i.getPrice() * i.getQty()).sum();
  // 3. persist
  Order order = new Order(req, total);
  orderRepo.save(order);
  // 4. notify
  emailService.sendConfirmation(order);
  // 5. audit
  auditLog.record("ORDER_PLACED", order.getId());
  return order;
}

// GOOD: delegate to cohesive sub-methods
public Order processOrder(OrderRequest req) {
  validate(req);
  Order order = createOrder(req);
  orderRepo.save(order);
  notificationService.orderPlaced(order);
  auditLog.record(PLACED, order.getId());
  return order;
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A small class is automatically cohesive | Size and cohesion are independent. A 3-method class with 3 unrelated concerns has low cohesion. A 30-method class fully focused on one domain can be highly cohesive |
| Cohesion only applies to classes | Cohesion applies at every level: method, class, package, module, microservice, and bounded context |
| High cohesion means fewer classes | It often means MORE classes — each smaller and more focused. The total system is more complex but each piece is simpler |
| Utility classes prove the rule | "Utility" classes are often low-cohesion by nature. Prefer moving methods to the domain objects they operate on |
| Cohesion and coupling are the same | Cohesion is about intra-module relatedness; coupling is about inter-module dependency. They are complementary but distinct metrics |

---

### 🔥 Pitfalls in Production

**1. The "God Service" in microservices**

```java
// BAD: UserService accumulates everything user-related
@Service
class UserService {
  // 847 lines, 60 methods across: auth, profile,
  // preferences, notifications, billing, analytics
  // Every team touches this → constant conflicts
}

// GOOD: split along bounded contexts
class AuthenticationService { ... }  // login/token
class UserProfileService    { ... }  // name/avatar
class UserBillingService    { ... }  // payment methods
class NotificationPrefsService { ... } // alert settings
```

**2. Test class revealing low cohesion**

```java
// Signal: test setup needs 8 mocks for one method test
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
  @Mock EmailService emailService;
  @Mock AvatarService avatarService;
  @Mock PaymentGateway payment;
  @Mock AuditLogger audit;
  @Mock FeatureFlagService flags;
  // ... 3 more mocks
  // → the class under test has low cohesion
  // Test complexity mirrors production complexity
}
```

**3. Package-level low cohesion in large codebases**

```
// BAD: package-by-layer creates low-cohesion packages
com.app.service.UserService
com.app.service.OrderService
com.app.service.PaymentService
// All services in one package: what do they share? Nothing

// GOOD: package-by-feature / bounded context
com.app.user.UserService
com.app.user.UserRepository
com.app.order.OrderService
com.app.order.OrderRepository
// Each package is a cohesive module
```

---

### 🔗 Related Keywords

- `Coupling` — the complementary metric; high cohesion naturally drives coupling down
- `Single Responsibility Principle` — the design rule that enforces cohesion: one reason to change
- `Refactoring` — Extract Class and Extract Method are the primary refactoring moves for low cohesion
- `Encapsulation` — strong encapsulation supports cohesion by hiding internals that belong together
- `Package Design` — cohesion applied at the package/module level; the Stable Dependencies Principle
- `Technical Debt` — low cohesion is one of the most common forms of structural technical debt

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ All elements of a module serve one        │
│              │ purpose — group by concept, not by owner  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing new classes; reviewing code for │
│              │ Extract Class / Extract Method smells     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — always aim for high cohesion;       │
│              │ "Utils" classes are the anti-pattern      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A class should have one reason to exist, │
│              │  not one reason per method."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Coupling → SRP → Refactoring: Extract     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service has grown to 1,200 lines: it handles payment initiation, retry logic, webhook parsing, fraud scoring, receipt generation, and refund processing. The team argues it's cohesive because "everything is payment-related." Evaluate this argument using the field-method affinity test and the LCOM metric — and describe the bounded contexts you would use to split it, explaining how you would avoid introducing excessive coupling between the resulting services.

**Q2.** At the microservice level, "cohesion" means a service owns a complete business capability. The CAP theorem forces distributed systems to trade off consistency, availability, and partition tolerance. Explain how the choice of service cohesion boundaries directly affects which CAP trade-off is acceptable — and give a concrete example where splitting a cohesive service across a consistency boundary creates a worse outcome than keeping it together.

