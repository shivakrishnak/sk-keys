---
layout: default
title: "Abstract Factory"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /design-patterns/abstract-factory/
id: DPT-008
category: Design Patterns
difficulty: ★★☆
depends_on: Factory Method, Interface, Polymorphism, Object-Oriented Programming (OOP)
used_by: Dependency Injection Pattern, Cross-platform UI frameworks, Plugin systems
related: Factory Method, Builder, Prototype, Dependency Injection Pattern
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
---

# DPT-008 — Abstract Factory

⚡ TL;DR — Abstract Factory provides an interface for creating families of related objects without specifying their concrete classes, ensuring compatible products are always created together.

| #768 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Factory Method, Interface, Polymorphism, Object-Oriented Programming (OOP) | |
| **Used by:** | Dependency Injection Pattern, Cross-platform UI frameworks, Plugin systems | |
| **Related:** | Factory Method, Builder, Prototype, Dependency Injection Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A UI framework supports Windows and macOS. It creates `WindowsButton`, `WindowsCheckbox`, `WindowsScrollbar` — and their Mac counterparts. Without Abstract Factory, the application code is peppered with: `if (os == WINDOWS) new WindowsButton(); else new MacButton();`. This appears dozens of times. A developer building a new dialog creates a `WindowsButton` and a `MacCheckbox` by accident — they compile and run, but the UI is visually inconsistent (mixed styles). Testing requires mocking every concrete class individually.

**THE BREAKING POINT:**
The guarantee that "all UI components in the same dialog belong to the same style family" cannot be enforced. Each call site makes an independent decision about which concrete class to instantiate. A new platform (Linux) requires searching the entire codebase for every `if (os == WINDOWS)` block and adding a third branch. Maintenance is error-prone — missing one branch produces a runtime crash on Linux, not a compile error.

**THE INVENTION MOMENT:**
This is exactly why the Abstract Factory pattern was created. A single `UIFactory` interface declares `createButton()`, `createCheckbox()`, `createScrollbar()`. A `WindowsFactory` implements all three to return Windows-style components. A `MacFactory` returns Mac-style components. The application code receives a `UIFactory` and creates all components through it — guaranteed consistent, with no per-call conditionals.

---

### 📘 Textbook Definition

The **Abstract Factory** pattern is a creational design pattern that provides an interface with multiple factory methods — one per product type — for creating families of related or dependent objects. Concrete factory classes implement this interface for each product family (e.g., Windows, Mac, Linux). Clients interact only with the abstract factory interface, ensuring that the objects they create are always compatible with each other. It is also known as "Kit" in some literature.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One factory interface that creates a whole consistent family of related objects together.

**One analogy:**
> Think of a furniture showroom that carries "styles" — Modern, Victorian, and Industrial. If you walk in and say "give me Modern furniture," the showroom gives you a Modern sofa, Modern chair, and Modern table — all matching. You never get a Victorian chair with an Industrial table by accident; the style system guarantees consistency.

**One insight:**
The critical difference from Factory Method is the constraint of **consistency across a family**. Factory Method creates one product; Abstract Factory creates a *set* of products that must work together. The pattern moves the coordination logic from the caller's code into the factory itself.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Multiple product types must always be instantiated from the same family — mixing families at runtime causes incompatibility.
2. The application code must be independent of which concrete product family is in use.
3. Switching between families must be achievable by changing a single decision point, not by searching for every `new ConcreteProduct()` call.

**DERIVED DESIGN:**
Given invariant 1: a factory must produce *all* products in a family — not just one. So the factory interface declares one method per product type. Given invariant 2: the application accepts a `UIFactory` parameter (interface), never `WindowsFactory` (concrete). Given invariant 3: the single decision point is where the concrete factory is instantiated — at application startup or configuration time.

The structure has two parallel hierarchies:
- **Factory hierarchy:** `UIFactory` → `WindowsFactory`, `MacFactory`
- **Product hierarchies:** `Button` → `WinButton`, `MacButton`; `Checkbox` → `WinCheckbox`, `MacCheckbox`

The factory hierarchy cross-cuts the product hierarchies: `WindowsFactory` creates objects from the Windows column across all product hierarchies.

**THE TRADE-OFFS:**
**Gain:** Product family consistency enforced at the type system level; adding a platform requires only a new factory class — all call sites are unchanged; Open/Closed Principle satisfied at the factory level.
**Cost:** Adding a new product type (e.g., `Scrollbar`) requires modifying the abstract factory interface AND all concrete factory classes — this is the hardest extension point; class count grows as O(platforms × product types).

---

### 🧪 Thought Experiment

**SETUP:**
A game engine support two rendering backends: OpenGL and DirectX. Every frame, the engine creates a `Mesh`, `Shader`, and `Texture`. These three objects must come from the same backend — an OpenGL Mesh cannot work with a DirectX Shader.

**WHAT HAPPENS WITHOUT ABSTRACT FACTORY:**
The rendering loop: `Mesh m = new OpenGLMesh(); Shader s = new DirectXShader();`. This compiles. At runtime, binding the DirectX shader to an OpenGL mesh causes a driver error. The error is miles from the `new` calls and notoriously hard to diagnose. Adding Vulkan support requires searching for every `new OpenGLMesh()` and `new DirectXShader()` and adding conditionals.

**WHAT HAPPENS WITH ABSTRACT FACTORY:**
`RenderFactory factory = new OpenGLFactory();` (set once at startup). The rendering loop: `Mesh m = factory.createMesh(); Shader s = factory.createShader();`. Both come from `OpenGLFactory` — guaranteed compatible. Switching to DirectX: replace `new OpenGLFactory()` with `new DirectXFactory()` at startup. The rendering loop is unchanged.

**THE INSIGHT:**
Abstract Factory concentrates all platform-specific `new` calls into one class. The rest of the application becomes platform-blind. The factory is the firewall between platform-specific and platform-generic code.

---

### 🧠 Mental Model / Analogy

> An Abstract Factory is like a brand's product catalogue. Apple's catalogue lists iPhone, iPad, MacBook — all Apple products that work together (iCloud sync, same cable standards, same ecosystem). Samsung's catalogue lists their compatible set. You pick a catalogue (factory), and everything you order from it is guaranteed compatible. You never cross-catalogue accidentally.

- "Apple product catalogue" → `AppleFactory` (concrete factory)
- "Samsung product catalogue" → `SamsungFactory` (concrete factory)
- "The section headers: Phone, Tablet, Laptop" → abstract factory methods: `createPhone()`, `createTablet()`, `createLaptop()`
- "Specific Apple iPhone" → `ApplePhone` (concrete product)
- "Choosing a catalogue" → injecting a specific factory at startup

Where this analogy breaks down: product catalogues don't enforce you can't buy Apple iPhone + Samsung tablet. Abstract Factory does — if you use one factory, all products come from that factory.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Abstract Factory is a way of saying "I want everything in the same style." Instead of choosing each item individually, you pick a style supplier, and every item you request comes from that same style — guaranteed to match. You can swap the entire style by swapping the supplier.

**Level 2 — How to use it (junior developer):**
Define a `UIFactory` interface with methods: `Button createButton()`, `Checkbox createCheckbox()`. Create `WindowsUIFactory implements UIFactory` and `MacUIFactory implements UIFactory`. In `Application`, accept a `UIFactory` in the constructor. Call `factory.createButton()` and `factory.createCheckbox()` throughout — never call `new WindowsButton()` directly. At startup: `Application app = new Application(new WindowsUIFactory())`.

**Level 3 — How it works (mid-level engineer):**
The two extension axes are: (1) product types (rows in the matrix) — adding a row requires changing the interface and all implementations; (2) product families (columns in the matrix) — adding a column requires only a new factory class. This asymmetry is the key design insight. If product types change rarely but platforms increase over time, Abstract Factory is well-suited. If product types change frequently, the interface updates cascade to all concrete factories. The runtime behaviour is pure polymorphism: the application only calls interface methods; the JVM dispatches to the concrete factory's implementation.

**Level 4 — Why it was designed this way (senior/staff):**
Abstract Factory was formalised in the GoF book for GUIs because the cross-product dimension (platform × component) is the exact structure the pattern handles optimally. Its Achilles heel — interface changes cascade — is mitigated in modern Java with default methods in interfaces (Java 8+): a new product type can have a default `throw new UnsupportedOperationException()` implementation, allowing incremental rollout. In Spring Boot, the equivalent is `@ConditionalOnProperty` beans and `@Profile` — the DI container acts as the Abstract Factory, selecting the right concrete beans based on environment configuration at startup.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│  ABSTRACT FACTORY STRUCTURE                      │
│                                                  │
│  <<interface>>                                   │
│  UIFactory                                       │
│  + createButton(): Button                        │
│  + createCheckbox(): Checkbox                    │
└───────────────┬──────────────────────────────────┘
                │ implements
    ┌───────────┴──────────────┐
    │                          │
WindowsFactory             MacFactory
+ createButton(){          + createButton(){
    return new WinBtn()        return new MacBtn()
  }                          }
+ createCheckbox(){        + createCheckbox(){
    return new WinCb()         return new MacCb()
  }                          }

Product hierarchies (parallel):
Button    ←  WindowsButton | MacButton
Checkbox  ←  WindowsCheckbox | MacCheckbox

Application:
  UIFactory f = new WindowsFactory(); // one decision
  Button b = f.createButton();         // always Windows
  Checkbox c = f.createCheckbox();     // always Windows
```

The matrix view makes the structure clear:

| Factory | createButton() | createCheckbox() |
|---|---|---|
| WindowsFactory | WindowsButton | WindowsCheckbox |
| MacFactory | MacButton | MacCheckbox |
| LinuxFactory | LinuxButton | LinuxCheckbox |

Each row is a factory class. Each column is a product hierarchy. Adding a row (new platform) is easy — implement a new factory. Adding a column (new product type) means adding a method to the interface and all rows.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Configuration / Startup
  → reads os.name property
  → creates WindowsFactory    ← YOU ARE HERE
  → injects factory into Application

Application.run()
  → calls factory.createButton()
  → returns WindowsButton (via WindowsFactory)
  → calls factory.createCheckbox()
  → returns WindowsCheckbox (via WindowsFactory)
  → renders UI — all components compatible
```

**FAILURE PATH:**
```
Wrong factory injected (e.g., test stub missing method)
  → factory.createButton() returns null
  → NullPointerException on first render
  → No compile error — interface satisfied by null return
Fix: use Objects.requireNonNull in factory methods
```

**WHAT CHANGES AT SCALE:**
At enterprise scale, Abstract Factory is replaced by DI container configuration (`@Profile("windows")` on `WindowsButton` bean). The container selects the right bean graph at startup based on environment. Adding a platform is a new `@Profile` annotation — no interface change required. At 100+ product types, explicit interface methods become unmaintainable; a registry pattern or DI is used instead.

---

### 💻 Code Example

**Example 1 — BAD: Scattered conditionals creating incompatible mixes:**
```java
// BAD: two separate decisions — can produce mismatch
String os = System.getProperty("os.name");
Button b;
Checkbox c;
if (os.startsWith("Windows")) {
    b = new WindowsButton();
} else {
    b = new MacButton();
}
// Developer forgets to update this block — mismatch!
c = new WindowsCheckbox();  // always Windows — bug!
```

**Example 2 — GOOD: Abstract Factory enforcing consistency:**
```java
// Product interfaces
public interface Button   { void paint(); }
public interface Checkbox { void render(); }

// Abstract factory interface
public interface UIFactory {
    Button   createButton();
    Checkbox createCheckbox();
}

// Windows family
public class WindowsFactory implements UIFactory {
    public Button   createButton()   {
        return new WindowsButton();
    }
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
}

// Mac family
public class MacFactory implements UIFactory {
    public Button   createButton()   {
        return new MacButton();
    }
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
}

// Application: accepts factory, never knows platform
public class Application {
    private final UIFactory factory;

    public Application(UIFactory factory) {
        this.factory = factory;
    }

    public void buildUI() {
        // ALWAYS matching family — type system enforces it
        Button b = factory.createButton();
        Checkbox c = factory.createCheckbox();
        b.paint();
        c.render();
    }
}

// Startup: ONE decision point
UIFactory factory = System.getProperty("os.name")
    .startsWith("Windows")
        ? new WindowsFactory()
        : new MacFactory();
Application app = new Application(factory);
app.buildUI();
```

**Example 3 — Spring equivalent using @Profile:**
```java
// Spring selects the right bean graph per environment
@Configuration
@Profile("windows")
public class WindowsConfig {
    @Bean public Button button() {
        return new WindowsButton();
    }
    @Bean public Checkbox checkbox() {
        return new WindowsCheckbox();
    }
}

@Configuration
@Profile("mac")
public class MacConfig {
    @Bean public Button button() {
        return new MacButton();
    }
    @Bean public Checkbox checkbox() {
        return new MacCheckbox();
    }
}
// Activate: -Dspring.profiles.active=windows
// Spring ApplicationContext IS the Abstract Factory
```

---

### ⚖️ Comparison Table

| Pattern | Products Created | Consistency Guarantee | Extension | Best For |
|---|---|---|---|---|
| **Abstract Factory** | Multiple related | Enforced by factory | New family = new class | Platform/theme families |
| Factory Method | Single product | Per-call | New variant = new subclass | Framework extension points |
| Builder | One complex object | Explicit step order | New step = method | Multi-param object assembly |
| DI Container | Any type graph | Container-managed | Configuration-driven | Application-layer services |

How to choose: use Abstract Factory when you need groups of objects to always be mutually compatible and the grouping dimension is a "platform" or "family." Use Factory Method when only one product type varies. Use DI (Spring) when you're inside a framework context — it provides the same guarantee with less ceremony.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Abstract Factory and Factory Method are interchangeable | Factory Method creates one product type via subclass override. Abstract Factory creates multiple product types via an interface with many methods — they solve different problems |
| Adding a new product type is easy | Adding a new product type (new method on interface) requires updating EVERY concrete factory — this is the hardest extension point of the pattern |
| Abstract Factory prevents mixing families | It prevents mixing if all creation goes through the factory. If someone calls `new WindowsButton()` directly, the factory's guarantee is violated |
| Abstract Factory == Abstract Class | The factory can be an interface (preferred in Java) or an abstract class. Modern Java favours interface because it allows multiple implementation without inheritance constraints |
| You need Abstract Factory whenever you have multiple implementations | Only when those implementations form *families* that must be used together. Unrelated implementations use Factory Method or plain DI |

---

### 🚨 Failure Modes & Diagnosis

**1. Interface Rigid to New Product Types**

**Symptom:** Adding a `Tooltip` component to the UI framework requires modifying `UIFactory` interface and all 8 concrete factories. Four factories throw `UnsupportedOperationException` for Tooltip — crashing UI at runtime only for those platforms.

**Root Cause:** The abstract factory interface has no default for the new product type. All implementors must be updated simultaneously — even platforms that don't support Tooltip.

**Diagnostic:**
```bash
# Find all UIFactory implementors:
grep -r "implements UIFactory" src --include="*.java"
# Count methods implemented in each vs interface methods:
javap -p WindowsFactory.class | grep "public"
```

**Fix:**
```java
// Add default to interface (Java 8+) for graceful fallback:
public interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
    // Default prevents breaking existing factories:
    default Tooltip createTooltip() {
        return new DefaultTooltip();  // or throw
    }
}
```

**Prevention:** Use default interface methods for new product types when not all factories can support them. Or use a DI container with optional bean wiring.

---

**2. Factory Injection Bypassed — Direct `new` Calls Leak In**

**Symptom:** UI is inconsistent on Mac — some components have Windows styling. Code review finds scattered `new WindowsButton()` calls in the application layer.

**Root Cause:** Developers bypass the factory and call `new ConcreteProduct()` directly, defeating the consistency guarantee.

**Diagnostic:**
```bash
# Find concrete product instantiation outside factory classes:
grep -r "new Windows" src --include="*.java" \
  | grep -v "Factory.java"
# Any results indicate a pattern violation
```

**Fix:**
Move concrete product classes to package-private visibility. Only the factory class in the same package can call `new WindowsButton()`. External code is forced through the factory.

**Prevention:** Package-private concrete classes + sealed interfaces (Java 17+) enforce factory-only instantiation at compile time.

---

**3. Factory Instantiated Multiple Times — Family Inconsistency**

**Symptom:** Parts of the UI use Windows style, parts use Mac style — in the same application run.

**Root Cause:** Different modules each instantiate their own factory with different logic: `new WindowsFactory()` in module A and `new MacFactory()` in module B.

**Diagnostic:**
```bash
# Find all factory instantiations:
grep -rn "new WindowsFactory\|new MacFactory" src \
  --include="*.java"
# Should appear exactly once (at startup config)
```

**Fix:**
Instantiate the factory exactly once at application startup and inject it via constructor or DI into all consumers.

**Prevention:** Abstract Factory should be a singleton within the application. Use a DI container to enforce this automatically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Factory Method` — Abstract Factory extends Factory Method to multiple product types; understanding Factory Method first is essential
- `Interface` — the abstract factory is declared as an interface; Java interface contracts must be understood
- `Polymorphism` — all factory interaction is through interface types; runtime dispatch selects the concrete implementation

**Builds On This (learn these next):**
- `Dependency Injection Pattern` — DI containers are runtime Abstract Factories; Spring's `@Profile` and `@Conditional` beans implement Abstract Factory semantics declaratively
- `Composite` — Abstract Factory is often combined with Composite to build complex object trees from a consistent product family
- `Builder` — when products in a family require complex multi-step construction, Builder is used inside Abstract Factory methods

**Alternatives / Comparisons:**
- `Factory Method` — simpler, single product; use when only one product type varies and family consistency across multiple types is not needed
- `Builder` — creates one complex object with many optional parts; use when construction steps vary, not product families
- `Prototype` — creates objects by cloning; useful when factory-created objects need to be customised after creation without subclassing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Interface with one factory method per     │
│              │ product type — creates consistent family  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Code creates incompatible product mixes   │
│ SOLVES       │ because each creation is independent      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Easy to add new families (columns);       │
│              │ hard to add new product types (rows)      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple related objects must always be   │
│              │ created from the same compatible family   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Product set changes frequently; DI        │
│              │ container already manages bean scope      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Family consistency and open extension     │
│              │ vs interface rigidity on adding products  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One factory catalogue, all products      │
│              │  guaranteed to match the same style."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Builder → Dependency Injection →          │
│              │ Composite                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your application uses a `DatabaseFactory` (Abstract Factory) with `createConnection()` and `createQueryBuilder()` methods. A new requirement: support read replicas, so `createConnection()` must return either a write or read connection based on context. The current interface signature is `Connection createConnection()`. Describe the exact interface change needed, which concrete factories break, and the minimum change to each — without breaking existing callers that don't care about read/write distinction.

**Q2.** A team argues that Spring's `@Profile` mechanism is a better solution than Abstract Factory for platform-specific object creation, and they want to remove all manual Abstract Factory code and replace it with Spring profiles. Identify the exact scenario where the Spring profile approach produces a different runtime behaviour than the Abstract Factory pattern, and describe a case where the Abstract Factory pattern is genuinely superior — not just equivalent under a different syntax.

