---
layout: default
title: "Factory Method"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /design-patterns/factory-method/
id: DPT-007
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on:
used_by: DPT-008, DPT-039
related: DPT-008, DPT-009, DPT-010
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
status: complete
version: 2
---

# DPT-007 - Factory Method

⚡ TL;DR - Factory Method lets subclasses decide which class to instantiate, decoupling object creation from the code that uses the object.

| DPT-007 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Polymorphism, Inheritance, Interface | |
| **Used by:** | Abstract Factory, Dependency Injection Pattern, Framework Extension Points | |
| **Related:** | Abstract Factory, Builder, Prototype, Abstract Class | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A GUI framework is being developed. The framework's base `Dialog` class needs to create a `Button` for each platform. Without a factory method, the code is: `Button b = new WindowsButton();` hardcoded inside a base class that is supposed to be platform-independent. When a developer wants to create a `MacDialog`, they must subclass `Dialog` and override everything - or worse, add `if (platform == MAC)` conditionals scattered throughout the code. Adding a new platform means touching every place a `Button`, `TextBox`, or `Spinner` is created.

**THE BREAKING POINT:**
The framework's entire value is reusability. But `new WindowsButton()` in the base class destroys reusability - the base class now **knows about** a specific subclass. Every `new ConcreteType()` is a hardcoded dependency that makes the class impossible to subclass cleanly. In frameworks that ship to third-party developers, this is fatal: the developer cannot swap in their own `Button` implementation without forking the framework source.

**THE INVENTION MOMENT:**
This is exactly why the Factory Method pattern was created. Instead of calling `new Button()` directly, the base class calls an abstract method `createButton()`. Subclasses override `createButton()` to return the specific type they need. The base class stays generic; subclasses stay specific.

**EVOLUTION:**
In classic Java (pre-2004), Factory Method required inheritance — a
subclass was mandatory. Java 5 generics, Java 8 lambda expressions,
and DI frameworks changed the calculus: `DriverManager.getConnection()`
in JDBC is a static factory method without inheritance. Spring's
`BeanFactory` uses the pattern but injects via configuration rather
than subclassing. Modern Java prefers static factory methods
(`List.of()`, `Optional.of()`) and provider-style interfaces over
the classical inheritance-based variant.

---

### 📘 Textbook Definition

The **Factory Method** pattern is a creational design pattern that defines an interface for creating an object but defers the actual instantiation to subclasses. The pattern introduces a factory method - an abstract or virtual method in a base class - that subclasses override to return the concrete object type appropriate for their context. The base class calls the factory method to obtain its objects, making it independent of the concrete types it works with. Sometimes called "Virtual Constructor."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A method that says "I need an object" but lets subclasses decide exactly which object to create.

**One analogy:**
> Think of a restaurant franchise. The corporate recipe says "add a bread roll" to every meal. But each location (France, Japan, USA) decides what kind of bread that is - baguette, rice ball, or dinner roll. The corporate recipe (base class) never changes; the local franchise (subclass) decides the specific item.

**One insight:**
The key insight is what gets inverted. Normally, a class decides its own dependencies by calling `new`. With Factory Method, the class declares what it *needs* (a Button, a Logger, a Serializer) but delegates who *provides* it to subclasses. This is the first step toward Dependency Inversion.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A base class needs to create objects but should not depend on their concrete types.
2. The type of object to create varies based on context - and different subclasses represent different contexts.
3. Object creation logic and object usage logic must be separable so each can evolve independently.

**DERIVED DESIGN:**
Given invariant 1+2: the base class declares a method (the factory method) whose return type is an interface or abstract class - the most general type the base class needs. Given invariant 3: the factory method is abstract (or has a default implementation), and concrete subclasses override it to return the specific type they want to provide.

The factory method is typically called inside a **template method** in the base class - a method that defines an algorithm using the factory-created object:
```
Base.someOperation() {
    Product p = createProduct();   // factory method call
    p.doSomething();               // uses the product
}
```
The base class defines the algorithm; the subclass provides the tools.

**THE TRADE-OFFS:**
**Gain:** Base class stays independent of concrete types; adding a new product variant only requires a new subclass of the creator - open/closed principle satisfied; third-party developers can extend the framework by subclassing.
**Cost:** Each new product type requires a new creator subclass - class count grows; inheritance-based (subclassing is required, not composition); if only one concrete type ever exists, the pattern adds indirection with no benefit.

---

### 🧪 Thought Experiment

**SETUP:**
A cross-platform notification framework must send notifications via Email, SMS, or Push. The `NotificationService` base class handles formatting, retry logic, and logging - the same for all channels. Only the actual sending mechanism differs.

**WHAT HAPPENS WITHOUT FACTORY METHOD:**
`NotificationService` has `sendViaEmail()`, `sendViaSMS()`, `sendViaPush()` methods. To add a new channel (Slack), every calling class must be updated. A `UniversalNotificationService` class grows to 800 lines with repeated formatting and retry logic for each channel. Testing one channel requires instantiating the entire service.

**WHAT HAPPENS WITH FACTORY METHOD:**
`NotificationService` declares abstract `Notifier createNotifier()`. `EmailNotificationService` overrides `createNotifier()` to return `new EmailNotifier()`. `SMSNotificationService` returns `new SMSNotifier()`. Adding Slack: create `SlackNotifier` and `SlackNotificationService` - zero changes to the base class or existing services.

**THE INSIGHT:**
Factory Method converts "which class?" from a hardcoded answer into a deferred question. The base class asks the question; subclasses answer it. Adding a new answer never changes the question.

---

### 🧠 Mental Model / Analogy

> A Factory Method is like a job posting that says "we need a developer" without specifying which developer. The HR department (calling code) uses the posting (factory method) without knowing WHO will fill the role. Each regional office (subclass) fills the role with their local hire (concrete class). Corporate headquarters (base class) gets a developer - it doesn't care from where.

- "Job posting" → the abstract factory method declaration
- "Regional offices" → concrete creator subclasses
- "Local hire" → concrete product class
- "Corporate headquarters using the developer" → base class using the product via its interface
- "HR posting process" → the template method that calls the factory method

Where this analogy breaks down: in a real company, HR might hire the same person repeatedly. In Factory Method, a new instance is typically created each time the factory method is called.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A Factory Method is a "fill in the blank" instruction. The base class says "create a widget here," and each subclass fills in its own specific type of widget. The base class never needs to know which specific widget it got - it just knows it's a widget.

**Level 2 - How to use it (junior developer):**
Declare an abstract method in the base class: `protected abstract Button createButton();`. In the base class's `render()` method, call `Button b = createButton(); b.paint();`. Create `WindowsDialog extends Dialog` and override `createButton()` to return `new WindowsButton()`. Create `MacDialog` and return `new MacButton()`. The `render()` logic is written once and inherited by all.

**Level 3 - How it works (mid-level engineer):**
The factory method is the "hook" in a Template Method pattern. The invariant part (algorithm structure) lives in the base class's template method. The variant part (object creation) is delegated to the factory method. At runtime, the JVM dispatches the factory method call polymorphically - calling the overriding subclass's version. This is standard virtual method dispatch. The creator and product hierarchies are parallel: `DialogCreator → WindowsDialog, MacDialog` mirrors `Button → WindowsButton, MacButton`.

**Level 4 - Why it was designed this way (senior/staff):**
Factory Method is the simplest form of the Dependency Inversion Principle applied to object creation. It separates "who uses the object" (base class) from "who creates the object" (subclass), allowing each to evolve independently. Its limitation is that it relies on inheritance - every variation requires a subclass pair (creator + product). This becomes unwieldy when there are multiple dimensions of variation (multiple product families). That is exactly the pain that drives the next pattern: Abstract Factory. Factory Method is a stepping stone; at scale, Abstract Factory or DI containers replace it.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│  FACTORY METHOD STRUCTURE               │
│                                         │
│  <<abstract>>                           │
│  Dialog (Creator)                       │
│  + render()                             │
│  # createButton(): Button  ← hook       │
│                                         │
│  render() {                             │
│    Button b = createButton();           │
│    b.paint();                           │
│  }                                      │
└──────────────┬──────────────────────────┘
               │ inherits
    ┌──────────┴──────────────┐
    │                         │
WindowsDialog              MacDialog
# createButton() {        # createButton() {
    return new                return new
    WindowsButton();          MacButton();
  }                         }
    │                         │
    ▼                         ▼
WindowsButton            MacButton
+ paint()                + paint()
```

The caller creates `new WindowsDialog()` and calls `dialog.render()`. The `render()` method in the base class calls `createButton()` - which dispatches polymorphically to `WindowsDialog.createButton()`, returning a `WindowsButton`. The base class only knows it has a `Button`; the concrete type is invisible to it.

**Parameterised Factory Method:** Some implementations pass a type parameter to the factory method - `createProduct(ProductType type)` - removing the need for a subclass per variant. The factory method uses a registry or switch statement to return the right type. This blurs into the Abstract Factory or Registry patterns.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client creates WindowsDialog
  → calls dialog.render()
  → base Dialog.render() calls createButton()
                          ← YOU ARE HERE
  → JVM dispatches to
    WindowsDialog.createButton()
  → returns WindowsButton instance
  → base Dialog.render() calls button.paint()
  → WindowsButton.paint() executes
  → dialog is rendered correctly
```

**FAILURE PATH:**
```
Subclass forgets to override createButton()
  → base class provides default returning null
  → render() calls null.paint()
  → NullPointerException at runtime
  → No compile-time error (if method has default)
```
Use `abstract` (not just `protected`) on the factory method to force subclass implementation - the compiler enforces the contract.

**WHAT CHANGES AT SCALE:**
In a framework deployed to thousands of developers, Factory Method is the primary extension point mechanism. Each developer creates one `CreatorSubclass` + one `ProductSubclass` pair to add functionality. The factory method registry approach (parameterised factory with a `Map<String, Supplier<Product>>`) avoids subclass explosion when there are 50+ product types. At extreme scale, reflection-based factories or DI containers replace explicit factory methods entirely.

---

### 💻 Code Example

**Example 1 - BAD: Hardcoded instantiation in base class:**
```java
// BAD: base class coupled to concrete WindowsButton
public class Dialog {
    public void render() {
        // Hardcoded - can never create MacButton here
        Button button = new WindowsButton();
        button.paint();
    }
}
```

**Example 2 - GOOD: Factory Method pattern:**
```java
// Product interface
public interface Button {
    void paint();
}

// Concrete products
public class WindowsButton implements Button {
    public void paint() {
        System.out.println("Rendering Windows button");
    }
}
public class MacButton implements Button {
    public void paint() {
        System.out.println("Rendering Mac button");
    }
}

// Creator (base class) - uses factory method
public abstract class Dialog {

    // Template method - unchanged across all dialogs
    public void render() {
        Button button = createButton(); // factory method
        button.paint();
    }

    // Factory method - subclasses decide what to create
    protected abstract Button createButton();
}

// Concrete creators - only override the factory method
public class WindowsDialog extends Dialog {
    @Override
    protected Button createButton() {
        return new WindowsButton();
    }
}

public class MacDialog extends Dialog {
    @Override
    protected Button createButton() {
        return new MacButton();
    }
}
```

**Example 3 - Production: Parameterised factory with registry:**
```java
// Avoids subclass explosion for many product types
public class NotifierFactory {
    private static final Map<String,
        Supplier<Notifier>> REGISTRY = new HashMap<>();

    static {
        REGISTRY.put("email",  EmailNotifier::new);
        REGISTRY.put("sms",    SmsNotifier::new);
        REGISTRY.put("push",   PushNotifier::new);
        REGISTRY.put("slack",  SlackNotifier::new);
    }

    // Register new notifiers at runtime (extension without
    // modifying this class - Open/Closed principle)
    public static void register(
            String channel, Supplier<Notifier> factory) {
        REGISTRY.put(channel, factory);
    }

    public static Notifier create(String channel) {
        Supplier<Notifier> factory = REGISTRY.get(channel);
        if (factory == null) throw new IllegalArgumentException(
            "Unknown channel: " + channel);
        return factory.get();
    }
}
// Usage:
Notifier n = NotifierFactory.create("email");
n.send(message);
```

---

### ⚖️ Comparison Table

| Pattern | Scope | Flexibility | Coupling | Best For |
|---|---|---|---|---|
| **Factory Method** | Single product | Subclass-per-variant | Low (interface) | Framework extension points |
| Abstract Factory | Product families | Multiple products | Very Low | Platform-spanning families |
| Builder | Complex construction | Step-by-step | Low | Multi-field object assembly |
| Constructor (direct) | Single type | None | High | Simple, fixed types |
| DI Container | Any object | Configuration-driven | Minimal | Application services |

How to choose: use Factory Method when the base class needs one variable product and subclassing is the natural extension mechanism. Graduate to Abstract Factory when multiple related products must be created together. Use DI for application-layer services where testability matters more than subclass flexibility.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Factory Method and static factory method are the same | Static factory (`String.valueOf()`) is just a static method that creates objects. Factory Method (GoF) is a polymorphic pattern requiring inheritance and overriding |
| Factory Method always returns a new instance | Not required. The factory method CAN return a cached or pooled instance - the pattern specifies *who decides* what to create, not whether to cache it |
| You must always override the factory method in subclasses | The base class can provide a default implementation (concrete factory method). It becomes a hook that subclasses optionally override, not an abstract requirement |
| Factory Method is only useful in frameworks | Any class that creates objects it then uses is a candidate. Controller + DAO creation, parser + tokenizer creation - all benefit from Factory Method when the concrete type varies |
| Factory Method violates the Single Responsibility Principle | It can, if the creator class does too much. Best practice: the creator's only job is algorithm + delegation to factory. Split if the creator has unrelated responsibilities |

---

### 🚨 Failure Modes & Diagnosis

**1. Factory Method Returns Null (Forgotten Default)**

**Symptom:** `NullPointerException` at the line where the factory-created object is first used. Stack trace points to base class code, but the actual bug is in a subclass.

**Root Cause:** A non-abstract factory method has `return null;` as default. A subclass was added but did not override the factory method, or the override has a conditional that returns `null` for unexpected types.

**Diagnostic:**
```bash
# Add null check assertion in the base class:
protected Button createButton() {
    throw new UnsupportedOperationException(
        "createButton must be overridden in: "
        + getClass().getName());
}
# Or use Objects.requireNonNull after calling:
Button b = Objects.requireNonNull(createButton(),
    "Factory method returned null in "
    + getClass().getName());
```

**Fix:**
Declare the factory method `abstract` when there is no sensible default. Use `Objects.requireNonNull` as a defensive check in the template method.

**Prevention:** Prefer `abstract` factory methods. Only provide a default when a meaningful fallback exists.

---

**2. Subclass Explosion**

**Symptom:** The project has 40 `*Creator` subclasses and 40 matching `*Product` subclasses for what started as a simple variation. Adding one new product type requires touching two class files in multiple packages.

**Root Cause:** Factory Method was applied without considering the expansion to parametric variation. Each new variant added a creator + product pair instead of a parameterised approach.

**Diagnostic:**
```bash
# Count creator subclasses:
find src -name "*Dialog*.java" | wc -l
find src -name "*Button*.java" | wc -l
# If close to equal and both > 10: subclass explosion
```

**Fix:**
Refactor to a registry-based parameterised factory (Example 3 above). Replace subclass pairs with `Map<String, Supplier<Product>>` entries.

**Prevention:** When more than 3–4 product variants exist, evaluate switching to a registry or Abstract Factory.

---

**3. Leaking Concrete Types Through the Factory Method**

**Symptom:** The factory method return type is a concrete class (`WindowsButton`) rather than an interface (`Button`). Callers use `WindowsButton`-specific methods directly, re-coupling them to the concrete type.

**Root Cause:** The factory method was declared with the wrong return type, or the interface was never extracted.

**Diagnostic:**
```bash
grep -r "WindowsButton b =" src/
# If this appears outside WindowsDialog: concrete type leaked
```

**Fix:**
Ensure the factory method return type is the interface/abstract class. Callers only use interface methods.

**Prevention:** The factory method return type must always be the most abstract type callers need - never the concrete type being created.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` - the pattern is built on inheritance, polymorphism, and interface contracts
- `Polymorphism` - the factory method's power comes from runtime dispatch to the correct subclass override
- `Interface` - the product returned by the factory method should be typed as an interface, not a concrete class

**Builds On This (learn these next):**
- `Abstract Factory` - extends Factory Method to create entire *families* of related products through a coordinated set of factory methods
- `Template Method` - Factory Method is frequently the variable step inside a Template Method that defines the algorithm skeleton
- `Dependency Injection Pattern` - DI generalises Factory Method by externalising object creation to a container rather than a subclass

**Alternatives / Comparisons:**
- `Builder` - creates complex objects step-by-step rather than in a single factory call; better when the product has many optional parameters
- `Prototype` - creates objects by cloning an existing instance rather than calling a creation method; useful when creation is expensive and cloning is cheap

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Abstract method in base class that        │
│              │ subclasses override to create objects     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Base class hardcoded to concrete types    │
│ SOLVES       │ it creates - blocks extension             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "Who uses the object" and "who creates    │
│              │  it" are separated via overriding         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Framework base class needs variable       │
│              │ objects; subclasses decide the type       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one concrete type ever exists;       │
│              │ or variation is runtime-config-driven     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Open/closed extensibility vs subclass     │
│              │ proliferation with many variants          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The base class asks what to create;      │
│              │  the subclass decides the answer."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstract Factory → Template Method →      │
│              │ Dependency Injection Pattern              │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define an interface for creating something but let the user of that
interface decide what to create. Defer decisions downward to the
most knowledgeable party.

**Where else this pattern appears:**
- **HTTP frameworks:** `HttpHandler` in Java's `HttpServer` is a
  factory — the framework calls `handle(HttpExchange)` and the
  developer provides the response type.
- **CI/CD pipelines:** A pipeline defines stages (build, test,
  deploy); each team provides their own implementation of each
  stage without changing the pipeline contract.
- **Database drivers:** JDBC's `DriverManager.getConnection()`
  returns a `Connection` whose concrete type (MySQL, PostgreSQL)
  is decided by the registered driver — callers never use `new`.

---

### 💡 The Surprising Truth

Java's standard library uses Factory Method far more than Abstract
Factory or Builder, yet most developers never recognise it.
`Collections.unmodifiableList()`, `List.of()`, `Optional.of()`,
`Path.of()` — these are all static factory methods, the modern
descendant of Factory Method. The pattern evolved from an OOP
inheritance mechanism into the language's preferred alternative
to `new`, eliminating the need for subclasses entirely while
keeping the core principle intact: the caller asks for an object
without knowing its concrete type.

---

### 🧠 Think About This Before We Continue

**Q1.** A logging framework uses Factory Method:
`Logger createLogger()` is abstract in `BaseAppender`, with
`FileAppender` returning `FileLogger` and `ConsoleAppender`
returning `ConsoleLogger`. A performance test shows that
`ConsoleAppender.createLogger()` is called 10,000 times/second,
creating 10,000 `ConsoleLogger` objects. Trace the memory and GC
impact, and describe how to modify the pattern to avoid it
without changing the caller's interface.

*Hint: The How It Works section shows the factory method is called
per-operation. The Object Pool pattern (DPT-011) addresses exactly
this problem — look at how pooling composes with creation patterns.*

**Q2.** A developer says: "I'll use `if-else` on a config string
to decide which database driver to instantiate — simpler than
Factory Method." Compare maintainability of `if-else` versus
Factory Method as the app grows from 2 database types to 12 over
three years. At what specific point does each approach break down?

*Hint: The Failure Modes section addresses OCP violations. Count
the `if-else` branches needed for 12 types and compare to the
class count in the Factory Method approach — which scales linearly?*

**Q3 (Design Trade-off):** Java's `ServiceLoader` mechanism lets
plugins register factory implementations at runtime via
`META-INF/services` files. Is `ServiceLoader` an implementation of
Factory Method, Abstract Factory, or neither? Justify by mapping
its participants to the pattern's roles.

*Hint: Map `ServiceLoader` to the pattern structure in How It Works
— identify the Creator, the ConcreteCreator, and the Product roles.
Then check whether Abstract Factory's multi-product-family
constraint is satisfied.*
