---
layout: default
title: "Polymorphism"
parent: "CS Fundamentals — Paradigms"
nav_order: 18
permalink: /cs-fundamentals/polymorphism/
number: "0018"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Abstraction, Encapsulation, Inheritance
used_by: Design Patterns, Dependency Injection, Software Architecture Patterns
related: Inheritance, Interfaces, Duck Typing
tags:
  - foundational
  - mental-model
  - first-principles
  - pattern
---

# 018 — Polymorphism

⚡ TL;DR — Polymorphism lets you write code that works with many different types through a shared interface, without knowing the concrete type at compile time.

| #018 | Category: CS Fundamentals — Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Abstraction, Encapsulation, Inheritance | |
| **Used by:** | Design Patterns, Dependency Injection, Software Architecture Patterns | |
| **Related:** | Inheritance, Interfaces, Duck Typing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

You build a notification system. It sends emails. Later you add SMS. Now you have `if (type == EMAIL) { sendEmail() } else if (type == SMS) { sendSMS() }`. Add push notifications: another branch. Add Slack: another branch. Every time a new notification type is added, every `if/else` block in the codebase must be found and updated. Miss one: partial notification. The business rule about "notify all channels" is scattered across the entire codebase.

**THE BREAKING POINT:**

This pattern — branching on type to decide behaviour — is called the "type code" smell. As the number of types grows, every feature that operates on those types contains the full switch statement. A new type requires 50 edits across 50 files. The code is a maintenance disaster. Adding a type should be a one-file change, not a surgical search-and-replace across the codebase.

**THE INVENTION MOMENT:**

This is exactly why polymorphism was created — to let you define a single shared interface (`Notifier.send()`) and have each implementation (`EmailNotifier`, `SmsNotifier`, `SlackNotifier`) define its own version. The caller writes `notifier.send(message)` once. Adding a new type is one new class, zero changes to existing code.

---

### 📘 Textbook Definition

**Polymorphism** is the ability for different types to be treated as instances of a common type, allowing a single interface to be used with multiple implementations. In OOP, polymorphism is typically realised through: **subtype polymorphism** (a variable of type `Animal` can hold a `Dog` or `Cat` — the method called at runtime depends on the actual object type, not the declared type); **parametric polymorphism** (generics — a `List<T>` works for any type `T`); and **ad-hoc polymorphism** (method overloading — the same method name resolves to different implementations based on argument types at compile time). The term "polymorphism" in OOP most commonly refers to subtype polymorphism via virtual method dispatch.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Polymorphism means "one interface, many implementations" — the same call does different things depending on the actual object.

**One analogy:**

> A TV remote has a "power" button that works on every TV — Samsung, LG, Sony. You press the same button; each TV responds correctly for its model. The remote doesn't know or care which brand it's controlling. Each TV implements the "respond to power button" contract in its own way.

**One insight:**
Polymorphism is what makes the Open/Closed Principle possible: "Open for extension, closed for modification." You can add new types (new TV brands, new notification channels) without modifying the code that calls through the interface. The caller is permanently stable; only new implementations are added.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The caller only needs to know what an object _does_ (its interface), not what it _is_ (its concrete type).
2. The same operation can have different correct implementations for different types.
3. The decision of _which_ implementation to call should be based on the object's actual type, not the caller's assumption.

**DERIVED DESIGN:**

Define a common interface that captures what all types must do. Each concrete type provides its own implementation. The caller holds a reference to the interface type — it never knows or cares which concrete class it's working with.

At runtime, virtual method dispatch resolves the call: the JVM (or runtime) looks up the actual object's class, finds its method table, and calls the correct implementation. This lookup happens at runtime — not compile time — which is why it's called _runtime polymorphism_.

```
Caller                Interface       Concrete Implementation
────────              ─────────       ─────────────────────────
notifier.send(msg) → Notifier.send() → EmailNotifier.send()
                                    → SmsNotifier.send()
                                    → SlackNotifier.send()
The caller writes this once. Each implementation is independent.
```

**THE TRADE-OFFS:**

**Gain:** Open/Closed — add new types without touching existing code; the caller is permanently stable; enables dependency injection and testability (swap in mocks via interface).
**Cost:** virtual dispatch is slightly slower than direct calls (~1–5ns overhead); too many levels of polymorphism can make tracing execution difficult; requires careful interface design upfront.

---

### 🧪 Thought Experiment

**SETUP:**
A rendering engine must draw `Circle`, `Rectangle`, and `Triangle` shapes. Each has a different drawing algorithm.

**WHAT HAPPENS WITHOUT POLYMORPHISM:**

```java
void render(List<Object> shapes) {
    for (Object shape : shapes) {
        if (shape instanceof Circle c) {
            drawCircle(c.radius, c.x, c.y);
        } else if (shape instanceof Rectangle r) {
            drawRect(r.width, r.height, r.x, r.y);
        } else if (shape instanceof Triangle t) {
            drawTriangle(t.p1, t.p2, t.p3);
        }
        // Add new shape → add new else-if HERE
        // And in every other method that processes shapes
    }
}
```

Adding `Star` shape: find every `instanceof` chain in the codebase and add a new branch.

**WHAT HAPPENS WITH POLYMORPHISM:**

```java
interface Shape { void draw(); }

class Circle implements Shape {
    public void draw() { /* draw circle logic */ }
}
class Rectangle implements Shape {
    public void draw() { /* draw rectangle logic */ }
}

void render(List<Shape> shapes) {
    for (Shape shape : shapes) {
        shape.draw();  // ONE LINE — forever stable
    }
}
```

Adding `Star` shape: write `class Star implements Shape { public void draw() { ... } }`. The `render()` method never changes.

**THE INSIGHT:**
Polymorphism moves the branching from "scattered if/else at every call site" to "isolated inside each class." Adding a type is additive (new class), not modifying (changing existing code). This is the difference between a system that scales and one that degrades with every new requirement.

---

### 🧠 Mental Model / Analogy

> Polymorphism is like a **universal socket adapter**. You plug in any device — US plug, UK plug, European plug — and the adapter makes it work. The device doesn't know it's going through an adapter; the outlet doesn't know which plug format is coming. The contract is: "provide power." How each device uses power is its own business.

**Mapping:**

- "Universal socket adapter" → interface / abstract type
- "US/UK/European plug" → concrete implementation (EmailNotifier, SmsNotifier)
- "Device" → caller that uses the interface
- "Outlet" → the system that provides the interface
- "Power contract" → the interface method signatures
- "How each device uses power" → each class's implementation of the interface method

**Where this analogy breaks down:** Adapters are physical objects that add overhead. Polymorphism via interface adds virtually no overhead at the hardware level — the overhead is virtual dispatch (a pointer dereference), which is nanoseconds.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Polymorphism means "same action, different behaviour." Press `play` on a music player: if it's a song, it plays audio. If it's a video, it plays video. The button is the same; the result depends on what kind of file it is. In code: call the same method, get different results depending on which object you called it on.

**Level 2 — How to use it (junior developer):**
Define an interface with the method(s) all types must implement. Each class implements the interface with its specific logic. In your calling code, hold a reference to the interface type. When you call the method, Java/Python/etc. automatically calls the right version based on the actual object. For tests: create a `MockNotifier implements Notifier` that records calls instead of sending real messages.

**Level 3 — How it works (mid-level engineer):**
Subtype polymorphism is implemented via virtual dispatch tables (vtables). Every class has a vtable — a table mapping method names to function pointers for that class's implementations. An object holds a pointer to its class's vtable. When you call `shape.draw()`, the JVM:

1. Loads the vtable pointer from the object header
2. Looks up `draw` in the vtable
3. Calls the function pointer
   This adds one pointer dereference (~1–5ns) compared to a direct call. The JIT can devirtualise calls where the concrete type is known at compile time, eliminating the overhead.

**Level 4 — Why it was designed this way (senior/staff):**
Polymorphism is the mechanism that enables the Dependency Inversion Principle: high-level modules depend on abstractions (interfaces), not concrete implementations. This breaks the compile-time dependency, allowing a payment processing module to depend on `PaymentGateway` (interface) and work with Stripe, PayPal, or a test stub — without any change to the module itself. At the architectural level, polymorphism via interfaces is how hexagonal architecture (ports and adapters) is implemented: the domain model depends on port interfaces; adapters implement them. The domain never changes when you swap databases, message queues, or UI frameworks.

---

### ⚙️ How It Works (Mechanism)

**Virtual dispatch table:**

```
┌─────────────────────────────────────────────────────┐
│          VIRTUAL DISPATCH TABLE (VTABLE)            │
│                                                     │
│  Object: EmailNotifier instance                     │
│  ┌──────────────────────┐                           │
│  │ vtable pointer ──────┼──→ EmailNotifier vtable   │
│  │ fields...            │    ┌──────────────────┐   │
│  └──────────────────────┘    │ send → EmailImpl │   │
│                              │ close → EmailClose│  │
│  Object: SmsNotifier instance└──────────────────┘   │
│  ┌──────────────────────┐                           │
│  │ vtable pointer ──────┼──→ SmsNotifier vtable     │
│  │ fields...            │    ┌──────────────────┐   │
│  └──────────────────────┘    │ send → SmsImpl   │   │
│                              │ close → SmsClose │   │
│                              └──────────────────┘   │
│                                                     │
│  Notifier n = getSomeNotifier();                    │
│  n.send(msg);  → look up vtable → call right impl  │
└─────────────────────────────────────────────────────┘
```

**Three forms of polymorphism:**

```java
// 1. SUBTYPE POLYMORPHISM (runtime — most common)
Notifier n = new EmailNotifier();  // runtime type: EmailNotifier
n.send(msg);                       // calls EmailNotifier.send()

// 2. PARAMETRIC POLYMORPHISM (generics — compile time)
// T can be any type — one implementation, all types
public <T> List<T> filter(List<T> list, Predicate<T> pred) {
    return list.stream().filter(pred).collect(Collectors.toList());
}
// Works for List<String>, List<Integer>, List<User>

// 3. AD-HOC POLYMORPHISM (overloading — compile time)
public void process(String s)  { /* string handling */ }
public void process(Integer i) { /* integer handling */ }
public void process(User u)    { /* user handling */  }
// Compiler selects based on argument type at compile time
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
New notification type "Push" needs to be added
      ↓
[POLYMORPHISM ← YOU ARE HERE]
  Developer creates: class PushNotifier implements Notifier
  Implements send() for push notification logic
      ↓
Register in DI container:
  @Bean PushNotifier implements Notifier
      ↓
All existing NotificationService code unchanged
  for (Notifier n : notifiers) { n.send(msg); }
  ← sends to Email, SMS, Slack, Push — automatically
      ↓
Unit test: MockNotifier captures calls without side effects
```

**FAILURE PATH:**

```
Interface design is too narrow or wrong
      ↓
New type can't implement the interface cleanly
  (e.g., Notifier.send(String) but Push needs title+body)
      ↓
Interface must be changed → breaks all existing implementations
      ↓
The "closed for modification" principle is violated
Observable: git blame shows interface file changed repeatedly
            as new types are added — sign of unstable abstraction
```

**WHAT CHANGES AT SCALE:**

At 100 microservices, polymorphism operates at the network level: services implement the same API contract (OpenAPI specification) and can be swapped behind a gateway. A payment service can route to Stripe or PayPal based on region — the client calls the same endpoint, gets the same response schema, without knowing which provider handled it. This is polymorphism at architecture scale.

---

### 💻 Code Example

**Example 1 — Wrong: type branching (anti-polymorphism):**

```java
// BAD: adding NotificationType.PUSH requires editing this method
//      and every other method that processes notifications
public void sendNotification(Object notifier, String msg) {
    if (notifier instanceof EmailNotifier e) {
        e.sendEmail(msg);
    } else if (notifier instanceof SmsNotifier s) {
        s.sendText(msg);
    }
    // DANGER: adding Slack requires adding else-if here
    // This code is NOT Open/Closed
}
```

**Example 2 — Right: polymorphism via interface:**

```java
// GOOD: define the contract once
public interface Notifier {
    void send(String message);
}

// Each type has its own implementation
public class EmailNotifier implements Notifier {
    @Override
    public void send(String message) {
        emailService.send("to@example.com", message);
    }
}

public class SmsNotifier implements Notifier {
    @Override
    public void send(String message) {
        smsGateway.sendText("+1234567890", message);
    }
}

// Caller — NEVER changes regardless of how many notifiers exist
public class AlertService {
    private final List<Notifier> notifiers;  // interface reference

    public AlertService(List<Notifier> notifiers) {
        this.notifiers = notifiers;
    }

    public void alert(String message) {
        notifiers.forEach(n -> n.send(message));
        // This line is permanent — new Notifiers = new class only
    }
}

// Add PushNotifier:
public class PushNotifier implements Notifier {
    @Override
    public void send(String message) {
        pushService.notify(message);
    }
}
// AlertService.alert() works with PushNotifier immediately.
// Zero changes to existing code.
```

**Example 3 — Polymorphism for testing (test doubles):**

```java
// PRODUCTION: real email is sent
List<Notifier> notifiers = List.of(
    new EmailNotifier(smtpConfig),
    new SmsNotifier(twilioConfig)
);

// TEST: nothing is sent, calls are recorded
public class CapturingNotifier implements Notifier {
    private final List<String> sentMessages = new ArrayList<>();

    @Override
    public void send(String message) {
        sentMessages.add(message);  // capture instead of send
    }

    public List<String> getSentMessages() {
        return Collections.unmodifiableList(sentMessages);
    }
}

@Test
void alertSendsToAllNotifiers() {
    CapturingNotifier capture = new CapturingNotifier();
    AlertService service = new AlertService(List.of(capture));
    service.alert("test message");
    assertThat(capture.getSentMessages()).contains("test message");
}
// Polymorphism makes this test trivial — swap real for fake via interface
```

---

### ⚖️ Comparison Table

| Mechanism                | When Resolved               | Overhead | Flexibility                       | Example                             |
| ------------------------ | --------------------------- | -------- | --------------------------------- | ----------------------------------- |
| **Subtype polymorphism** | Runtime (vtable)            | ~1–5ns   | High — add types at runtime       | `List<Notifier>`                    |
| Method overloading       | Compile time                | None     | Low — types fixed at compile time | `process(String)` vs `process(int)` |
| Generics (parametric)    | Compile time (type erasure) | None     | High — type-safe for any T        | `List<T>`, `Optional<T>`            |
| Duck typing (Python)     | Runtime                     | None     | Very high — no declaration needed | Python `len()` on any iterable      |
| `instanceof` branching   | Runtime                     | None     | None — manual and brittle         | `if (x instanceof Foo)`             |

**How to choose:** Use subtype polymorphism (interfaces) as the default — it enables Open/Closed and testability. Use generics when the operation is type-independent. Avoid `instanceof` branching — it's the symptom that polymorphism is missing.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Polymorphism requires inheritance              | Subtype polymorphism can be achieved via interfaces (Java, TypeScript) or structural typing (Go, duck typing in Python) without inheritance. Inheritance is one mechanism; interfaces are another.                                   |
| Polymorphism is the same as method overloading | Overloading is resolved at compile time — it's "ad-hoc polymorphism." Runtime polymorphism via virtual dispatch is what OOP usually means by polymorphism. They're different mechanisms.                                             |
| Polymorphism is always better than if/else     | For 2–3 simple, stable cases, an if/else is clearer. Polymorphism adds value when: (a) types are added over time, (b) the same branching appears in multiple places, (c) you need testability via swapping implementations.          |
| Virtual dispatch is expensive                  | Modern CPUs with branch predictors and JIT devirtualisation make virtual dispatch nearly free in practice. The JIT identifies monomorphic call sites (one concrete type) and compiles them as direct calls.                          |
| Duck typing is not polymorphism                | Duck typing is structural polymorphism — "if it has a `send()` method, treat it as a Notifier." Python's `len()` works on strings, lists, and dicts without any declared interface. Same principle, different enforcement mechanism. |

---

### 🚨 Failure Modes & Diagnosis

**Fragile Base Class Problem**

**Symptom:**
Changing a method in a superclass breaks subclasses in unexpected ways. Subclass overrides behave incorrectly because the superclass's template method calls the overridden method in a specific order the subclass doesn't know about.

**Root Cause:**
Polymorphism via inheritance creates tight coupling between base and derived classes. The superclass's internal method call structure becomes a hidden contract that derived classes must not violate.

**Diagnostic Command / Tool:**

```bash
# Find all subclasses of a base class:
grep -rn "extends BaseClass" src/ --include="*.java"
# Each subclass is a risk point for fragile base class violations

# In Java: use @Override annotation to ensure you're overriding,
# not accidentally creating a new method:
# javac -Xlint:all *.java  # warns on missing @Override
```

**Fix:**
Prefer interface-based polymorphism over inheritance-based. Make the base class `final` for methods that shouldn't be overridden. Use composition (Strategy pattern) instead of inheritance for behaviour variation.

**Prevention:**
Favour interfaces over abstract classes. "Favour composition over inheritance." Use `final` on methods that form the template's backbone.

---

**Interface Bloat**

**Symptom:**
An interface has 20 methods. Most implementations only meaningfully implement 5 of them. The other 15 are implemented with empty bodies or `throw UnsupportedOperationException`.

**Root Cause:**
The interface was designed too broadly. It violates the Interface Segregation Principle (ISP): one fat interface forces all implementors to implement all methods, even those irrelevant to them.

**Diagnostic Command / Tool:**

```bash
# Find empty or stub implementations:
grep -A3 "@Override" src/ --include="*.java" | \
  grep -B1 "throw new UnsupportedOperationException"
# Each hit: the method belongs in a separate, smaller interface
```

**Fix:**
Split the large interface into smaller, focused interfaces. Classes implement only the interfaces relevant to them. Callers depend on the smallest interface they need.

**Prevention:**
Apply ISP: each interface should have a single cohesive responsibility. Start with small, focused interfaces — merging is easier than splitting.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Abstraction` — polymorphism is the runtime realisation of abstraction; you must understand interfaces before understanding polymorphism
- `Encapsulation` — each polymorphic implementation hides its specific logic behind the shared interface
- `Inheritance` — one mechanism for achieving polymorphism (subclassing); often less preferred than interfaces

**Builds On This (learn these next):**

- `Design Patterns` — Strategy, Command, Observer, Factory — all use polymorphism as their core mechanism
- `Dependency Injection` — injects the right concrete implementation via the interface; polymorphism makes DI possible
- `SOLID Principles` — Open/Closed Principle and Dependency Inversion Principle are direct applications of polymorphism

**Alternatives / Comparisons:**

- `Duck Typing` — structural polymorphism in Python/Go: "if it has the method, it qualifies" — no interface declaration needed
- `Generics / Parametric Polymorphism` — type-safe code that works with any type; Java `List<T>`, TypeScript `Promise<T>`
- `Pattern Matching` — functional programming's alternative: explicit type branching that's exhaustive and compiler-checked (`sealed` classes + `switch` in Java 21+)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One interface, many implementations —     │
│              │ correct behaviour chosen at runtime       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Type-branching if/else scattered across   │
│ SOLVES       │ codebase; every new type requires 50 edits│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Adding a new type is ONE new class —      │
│              │ zero changes to existing calling code     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple types must respond to the same   │
│              │ operation in type-specific ways           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ 2 fixed types that will never change:     │
│              │ simple if/else is clearer                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Open/Closed extensibility vs vtable       │
│              │ indirection and upfront interface design  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same method name; the right code runs.   │
│              │  The caller doesn't know or care."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Design Patterns → SOLID → DI Containers   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment processing system uses polymorphism: `PaymentGateway` interface with `StripeGateway` and `PaypalGateway` implementations. The caller does `gateway.charge(amount)`. A new requirement: some gateways support `refund()` and others don't. Extending the `PaymentGateway` interface to add `refund()` forces all existing implementations to implement it. What are the three design options for handling this evolution, and what are the architectural trade-offs of each — specifically around backward compatibility and the Interface Segregation Principle?

**Q2.** Java's `List.sort()` method accepts a `Comparator<T>` — a functional interface (single-method interface). In Java 8+, you can pass a lambda: `list.sort((a, b) -> a.compareTo(b))`. The lambda is polymorphic — it implements `Comparator`. A traditional anonymous class `new Comparator<String>() { public int compare(String a, String b) {...} }` achieves the same polymorphism with more syntax. At what point does this reveal that polymorphism is fundamentally about _behaviour substitution_, not _type hierarchies_ — and what does this mean for how you should think about functional programming's approach to the same problems OOP uses polymorphism for?
