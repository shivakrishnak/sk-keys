---
layout: default
title: "Bridge"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /design-patterns/bridge/
id: DPT-013
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - advanced
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-013 - Bridge

⚡ TL;DR - Bridge decouples an abstraction from its implementation so both can vary independently, connected only through a composition relationship.

| DPT-013 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Abstraction, Composition over Inheritance, Interface, Object-Oriented Programming (OOP) | |
| **Used by:** | Cross-platform UI frameworks, Device drivers, Rendering engines | |
| **Related:** | Adapter, Strategy, Abstract Factory, Decorator | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A rendering library supports two shapes (Circle, Square) and two rendering backends (OpenGL, DirectX). Using pure inheritance: `OpenGLCircle`, `DirectXCircle`, `OpenGLSquare`, `DirectXSquare` - 4 classes. Add a third shape (Triangle) and a third backend (Vulkan): 9 classes. Add a fourth shape and backend: 16 classes. The number of classes grows as `shapes × backends` - an exponential explosion. Every time the business adds a new shape or a new platform, all existing combinations must be considered and potentially rewritten.

**THE BREAKING POINT:**
The inheritance tree fuses two independent dimensions (shape type and rendering backend) into a single hierarchy. This violates a fundamental principle: a class hierarchy should represent one dimension of variation. When two independent dimensions are bound together in a hierarchy, changing one requires touching all combinations. With 10 shapes and 10 backends, 100 concrete classes must be maintained. A bug fix in DirectX rendering requires fixing 10 classes instead of 1.

**THE INVENTION MOMENT:**
This is exactly why the Bridge pattern was created. Separate the two dimensions into two independent hierarchies connected by composition. Shape holds a reference to a Renderer. `Circle.draw()` calls `renderer.renderCircle(radius)`. The Shape hierarchy and the Renderer hierarchy evolve completely independently. Adding a shape: 1 new class. Adding a backend: 1 new class. No cross-product explosion.

**EVOLUTION:**
Bridge was most valuable when class hierarchies were the primary
extension mechanism in pre-generics Java (pre-2004). With
generics, lambdas, and composition-first thinking, Bridge's
classical inheritance-heavy structure became less necessary.
The pattern's core insight -- decouple abstraction from
implementation via composition -- survived and became
foundational in DI frameworks. Spring's data access layer
is a canonical Bridge: `JdbcTemplate` and `HibernateTemplate`
are abstractions; the JDBC driver or Hibernate session factory
is the implementation -- swappable without touching the
abstraction layer.

---

### 📘 Textbook Definition

The **Bridge** pattern is a structural design pattern that separates the **abstraction** (a high-level control interface) from its **implementation** (the platform-specific or variant-specific operations), placing them in separate class hierarchies. The abstraction holds a reference to an implementation object. The abstraction delegates platform-specific work to its implementation object. This composition relationship (the "bridge") allows both hierarchies to evolve independently. Also known as "Handle/Body."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Two parallel hierarchies connected by composition so each can grow without affecting the other.

**One analogy:**
> A TV remote (abstraction) and a TV (implementation). The remote has buttons - volume up, channel change. The TV has hardware to process those signals. You can buy a new fancy remote (abstraction changes) for the same TV. Or upgrade to a new TV (implementation changes) and use the same remote. The remote doesn't inherit from the TV - it is connected to it.

**One insight:**
The Bridge prevents the "inheritance explosion" by asking: "Why does adding one new shape require adding N new classes?" The answer: because implementation details (backends) are baked into the class hierarchy. Bridge extracts those details into a separate hierarchy, making each addition O(1) instead of O(N).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Two independent dimensions of variation exist (e.g., shape type and rendering backend).
2. Both dimensions will change and grow independently over the software's lifetime.
3. Combining them in a single hierarchy creates O(m×n) classes where O(m+n) would suffice.

**DERIVED DESIGN:**
Given invariant 1+2: the two dimensions must be separate hierarchies. Given invariant 3: they must NOT be connected by inheritance (IS-A), only by composition (HAS-A). The abstraction IS-A a shape. The abstraction HAS-A renderer. Each hierarchy maintains its own polymorphic substitutability.

The connection point (the "bridge") is a field in the abstraction: `private Renderer renderer;`. The abstraction delegates platform-specific work through this field. Client code creates an abstraction and injects a concrete implementation:
```
new Circle(5.0, new OpenGLRenderer()).draw()
```

Neither hierarchy knows about the concrete classes of the other - only about the interface contract.

**THE TRADE-OFFS:**
**Gain:** Independent evolution of both dimensions; linear class growth O(m+n) instead of O(m×n); can switch implementation at runtime; cleaner hierarchies.
**Cost:** More complex initial design - correct identification of the two "dimensions" requires design experience; two interface / abstract class definitions needed; can be overkill when only one implementation exists; direct instantiation requires injecting the implementation, increasing wiring complexity.

---

### 🧪 Thought Experiment

**SETUP:**
A notification system must send messages via SMS and Email. Messages come in two types: Plain and Formatted (with HTML). Initially: 4 classes - start adding push notification, adding Markdown format - you need 6 classes.

**WHAT HAPPENS WITHOUT BRIDGE (pure inheritance):**
```
Notification
  SMSNotification
    PlainSMSNotification
    FormattedSMSNotification
  EmailNotification
    PlainEmailNotification
    FormattedEmailNotification
  PushNotification
    PlainPushNotification
    FormattedPushNotification
    MarkdownPushNotification  ← new combo
  ...
```
Every new combination adds classes. Shared formatting logic must be duplicated or pulled up in complex ways.

**WHAT HAPPENS WITH BRIDGE:**
```
Notification    MessageSender
  Plain         SMSSender
  Formatted     EmailSender
  Markdown      PushSender
```
3 notification types × 3 senders = 6 total classes for 9 combinations. Adding a 4th sender: 1 class, 0 changes to notification side. Adding a 4th format: 1 class, 0 changes to sender side.

**THE INSIGHT:**
Bridge works when you can identify two independent dimensions and articulate each dimension's interface contract cleanly. The pattern fails (adds complexity without benefit) if the two dimensions are actually interdependent - if changing one inherently requires changing the other.

---

### 🧠 Mental Model / Analogy

> Bridge is like a universal power strip adapter. Power strips come in different designs (abstraction: strip with 4 outlets, 6 outlets, surge protector). Plugs come in different types (implementation: US Type A, EU Type C, UK Type G). The adapter (bridge) lets any strip design work with any plug type. Adding a new strip design doesn't require new plugs. Adding a new plug type doesn't require new strip designs. The connection is the adapter in the middle - the bridge.

- "Power strip designs" → abstraction hierarchy (shapes, notification types)
- "Plug types" → implementation hierarchy (renderers, senders)
- "Universal adapter" → the composition relationship (bridge) between them
- "Plugging in" → injecting an implementation into the abstraction
- "Changing strips or plugs independently" → independent evolution of both hierarchies

Where this analogy breaks down: a physical adapter performs a passive connection; the Bridge's `renderer` field is an active call delegation - the abstraction actively calls methods on the implementation, not just passes signals through.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Bridge is like keeping two separate catalogues - one for designs, one for materials - instead of making a separate catalogue entry for every combination of design + material. When you add a new design or a new material, you update only one catalogue, and mix-and-match as needed.

**Level 2 - How to use it (junior developer):**
Identify the two varying dimensions. Create an interface for each: `Shape` and `Renderer`. The `Shape` interface (or abstract class) holds a `Renderer` field: `protected Renderer renderer;`. Concrete shapes (`Circle`, `Square`) implement `Shape.draw()` by calling `renderer.renderCircle(radius)` or `renderer.renderSquare(side)`. Concrete renderers (`OpenGLRenderer`, `DirectXRenderer`) implement `Renderer`. Wire them at construction: `new Circle(5, new OpenGLRenderer())`.

**Level 3 - How it works (mid-level engineer):**
The abstraction (Shape) defines the high-level operations (`draw()`). The implementation interface (Renderer) defines the low-level primitives (`renderCircle`, `renderSquare`). The abstraction's methods are templates that call the implementation's primitives. The two key design constraints: (1) The abstraction should only call methods declared in the Renderer interface - no concrete class references; (2) The Renderer interface should only expose primitives needed by the abstraction, not platform-internal details. Breaking constraint (1) defeats the pattern. Breaking constraint (2) means the abstraction knows about platform specifics.

**Level 4 - Why it was designed this way (senior/staff):**
Bridge was developed partly from the POSA1 (Pattern-Oriented Software Architecture) work on portability. The pattern directly addresses one of the most painful patterns in platform-spanning software: the inability to add platforms or features without combinatorial class growth. Its subtlety is in the identification of "independent dimensions" - a skill that requires design experience. Common misapplication: using Bridge when there is actually only one dimension of variation (the Strategy pattern's territory). Another misapplication: using Bridge when the two dimensions are tightly coupled (adding a shape type requires modifying a renderer method). In modern Java, Bridge appears in JDBC (Connection/Statement abstractions over database implementations), AWT/Swing (platform peers), and Logging facades (SLF4J over Log4j/Logback). The Bridge rarely appears in new greenfield code where DI frameworks and clean interface design achieve the same goal with less structural ceremony.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  BRIDGE PATTERN STRUCTURE                       │
│                                                 │
│  ABSTRACTION HIERARCHY                          │
│  ┌──────────────────────────────────────┐       │
│  │ <<abstract>>                         │       │
│  │ Shape                                │       │
│  │ # renderer: Renderer  ← bridge field │       │
│  │ + draw()                             │       │
│  └────────────┬─────────────────────────┘       │
│               │                                 │
│    ┌──────────┴─────────────┐                   │
│  Circle                  Square                 │
│  draw() {               draw() {                │
│    renderer              renderer               │
│    .renderCircle(r)       .renderSquare(s)       │
│  }                      }                       │
│                                                 │
│  IMPLEMENTATION HIERARCHY                       │
│  ┌──────────────────────────────────────┐       │
│  │ <<interface>>                        │       │
│  │ Renderer                             │       │
│  │ + renderCircle(double r)             │       │
│  │ + renderSquare(double s)             │       │
│  └────────────┬─────────────────────────┘       │
│               │                                 │
│    ┌──────────┴─────────────┐                   │
│  OpenGLRenderer         DirectXRenderer         │
└─────────────────────────────────────────────────┘

Connection (Bridge):
  Shape ---HAS-A--→ Renderer  (composition)
  Shape is NOT an OpenGLRenderer
```

**Runtime interaction:**
```
client → new Circle(5.0, new OpenGLRenderer())
client → circle.draw()
  → Circle.draw():
      renderer.renderCircle(5.0)
      → OpenGLRenderer.renderCircle(5.0):
          glBegin(GL_CIRCLE);
          glCircle(0, 0, 5.0);
          glEnd();
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Configuration/DI
  → creates OpenGLRenderer (implementation)
  → creates Circle(radius=5, renderer=opengl)
                                ← YOU ARE HERE
Client calls circle.draw()
  → Circle.draw() delegates to renderer.renderCircle(5)
  → OpenGLRenderer.renderCircle(5) executes
  → Pixel buffer updated
  → Frame rendered

Platform switch (runtime):
  → circle.setRenderer(new VulkanRenderer())
  → next circle.draw() uses Vulkan, no code change
```

**FAILURE PATH:**
```
Implementation hierarchy method not implemented
  → DirectXRenderer missing renderCircle() override
  → Throws AbstractMethodError at runtime
  → No compile-time error if interface has default

Fix: make Renderer interface methods abstract (no default)
  → Compiler enforces all methods implemented
```

**WHAT CHANGES AT SCALE:**
At production scale with 50+ shapes and 10+ backends, the Bridge pattern's class count advantage (50+10=60 vs 50×10=500) becomes dramatic. However, the Renderer interface becomes a "God Interface" if it must declare primitives for every shape. This leads to a variation: the Renderer exposes generic drawing primitives (`drawPath`, `drawBezier`) that shapes use to compose their appearance - keeping the implementation interface stable. At extreme scale, the implementation side is replaced by a plugin system where renderer implementations are loaded dynamically.

---

### 💻 Code Example

**Example 1 - BAD: Inheritance explosion:**
```java
// BAD: 2 shapes × 2 renderers = 4 classes already
// Adding 3rd shape + 3rd renderer = 9 classes
abstract class Shape { abstract void draw(); }
class OpenGLCircle extends Shape {
    void draw() { /* OpenGL circle */ }
}
class DirectXCircle extends Shape {
    void draw() { /* DirectX circle */ }
}
class OpenGLSquare extends Shape {
    void draw() { /* OpenGL square */ }
}
class DirectXSquare extends Shape {
    void draw() { /* DirectX square */ }
}
```

**Example 2 - GOOD: Bridge pattern:**
```java
// IMPLEMENTATION hierarchy
public interface Renderer {
    void renderCircle(double radius);
    void renderSquare(double side);
}

public class OpenGLRenderer implements Renderer {
    @Override
    public void renderCircle(double radius) {
        System.out.printf(
            "OpenGL: circle(radius=%.1f)%n", radius);
    }
    @Override
    public void renderSquare(double side) {
        System.out.printf(
            "OpenGL: square(side=%.1f)%n", side);
    }
}

public class DirectXRenderer implements Renderer {
    @Override
    public void renderCircle(double radius) {
        System.out.printf(
            "DirectX: circle(r=%.1f)%n", radius);
    }
    @Override
    public void renderSquare(double side) {
        System.out.printf(
            "DirectX: square(s=%.1f)%n", side);
    }
}

// ABSTRACTION hierarchy
public abstract class Shape {
    protected final Renderer renderer; // THE BRIDGE

    protected Shape(Renderer renderer) {
        this.renderer = renderer;
    }

    public abstract void draw();
    public abstract void resize(double factor);
}

public class Circle extends Shape {
    private double radius;

    public Circle(double radius, Renderer renderer) {
        super(renderer);
        this.radius = radius;
    }

    @Override
    public void draw() {
        renderer.renderCircle(radius); // delegates to impl
    }

    @Override
    public void resize(double factor) {
        radius *= factor;
    }
}

public class Square extends Shape {
    private double side;

    public Square(double side, Renderer renderer) {
        super(renderer);
        this.side = side;
    }

    @Override
    public void draw() {
        renderer.renderSquare(side); // delegates to impl
    }

    @Override
    public void resize(double factor) {
        side *= factor;
    }
}

// Client:
Renderer openGL = new OpenGLRenderer();
Shape circle = new Circle(5.0, openGL);
circle.draw();                   // OpenGL circle

// Switch backend - zero changes to shapes:
Renderer directX = new DirectXRenderer();
Shape square = new Square(3.0, directX);
square.draw();                   // DirectX square

// Adding Triangle + Vulkan:
// → 1 new Shape class (Triangle) - no renderer changes
// → 1 new Renderer class (VulkanRenderer) - no shape changes
```

**Example 3 - JDBC: Bridge in the standard library:**
```java
// ABSTRACTION side (java.sql)
Connection conn =          // <- abstraction
    DriverManager.getConnection(jdbcUrl, user, pass);

PreparedStatement ps =
    conn.prepareStatement("SELECT * FROM users");
ResultSet rs = ps.executeQuery();

// Behind the scenes - IMPLEMENTATION side (driver):
// MySQLConnection, OracleConnection, H2Connection
// Each implements java.sql.Connection (the bridge interface)
// Application code never references MySQL/Oracle directly
// Switch database: change JDBC URL + driver JAR
// Zero application code changes = Bridge in action
```

---

### ⚖️ Comparison Table

| Pattern | Problem Solved | Relationship | Dimensions | Best For |
|---|---|---|---|---|
| **Bridge** | Inheritance explosion from 2 dimensions | Composition (permanent) | Two independent | Shapes+renderers, platform+feature |
| Adapter | Incompatible interfaces | Composition (post-hoc) | One (interface mismatch) | Legacy integration |
| Strategy | Interchangeable algorithms | Composition | One (algorithm variation) | Sort algorithms, pricing strategies |
| Abstract Factory | Compatible product families | Creation | One (product family) | Platform-specific object creation |
| Decorator | Add behaviour dynamically | Composition+same interface | One (behaviour addition) | Feature stacking at runtime |

How to choose: use Bridge when you have two independently varying dimensions and want to avoid O(m×n) class explosion. Use Strategy when only the algorithm varies (one dimension). Use Adapter when the problem is existing interface incompatibility, not future extension.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bridge and Adapter solve the same problem | Adapter is a post-hoc fix for existing interface incompatibility. Bridge is a proactive design to prevent inheritance explosion during initial design |
| The "bridge" is a special class or component | The "bridge" is the composition relationship - the field reference from abstraction to implementation. It is not a third class |
| Bridge always requires two abstract classes | The abstraction can be an abstract class OR interface. The implementation must be an interface (for substitutability). Modern Java prefers both as interfaces when possible |
| Bridge is only for UI and graphics | Bridge appears in any domain with two independent variation dimensions: transport × message format, storage medium × encoding, network protocol × data compression |
| You must identify Bridge at design time | Bridge can be refactored in after inheritance explosion is noticed. The refactoring moves one hierarchy out of the class inheritance and into a composition field |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong Dimension Identification - Coupled Dimensions**

**Symptom:** Adding a new `Shape` type requires changing the `Renderer` interface to add a new method. The two hierarchies are not truly independent.

**Root Cause:** The dimensions are not orthogonal. The rendering of a `Pentagon` requires a new rendering primitive that doesn't fit the existing `renderCircle`/`renderSquare` interface. This means shapes and renderers ARE coupled - the pattern was applied incorrectly.

**Diagnostic:**
```java
// Check: does adding a new Shape require a new Renderer method?
// If yes: dimensions are coupled, Bridge is weakly applied
// Solution: use generic drawing primitives instead
public interface Renderer {
    void drawPath(Path path);    // generic - any shape
    void drawBezier(BezierCurve c); // generic primitive
    // NOT: renderCircle, renderSquare - too shape-specific
}
```

**Fix:**
Redesign the Renderer interface with generic drawing primitives that any shape can use. Each shape composes its appearance from these primitives.

**Prevention:** The Renderer interface should describe capabilities, not shape types. If `Renderer` has a method per shape, Bridge was applied prematurely.

---

**2. Implementation Reference Leaked to Client**

**Symptom:** Client code casts to a concrete Renderer: `((OpenGLRenderer) shape.getRenderer()).enableVSync()`. OpenGL-specific code appears in platform-independent client code.

**Root Cause:** The `renderer` field (or getter) exposes the concrete type to clients. Or: the abstraction's interface does not provide a way to access needed functionality, forcing clients to bypass the Bridge.

**Diagnostic:**
```bash
grep -r "OpenGLRenderer\|DirectXRenderer" \
  src --include="*.java" \
  | grep -v "Renderer\.java\|RendererFactory\.java"
# Any concrete renderer reference in other files = leak
```

**Fix:**
Add the needed operation to the Renderer interface (if all renderers support it) or to the Shape abstraction. Never expose the concrete implementation to clients.

**Prevention:** The `renderer` field should be `protected` (accessible to subclasses) or private. No public getter for the implementation field.

---

**3. Bridge Used for Single Dimension (Overkill)**

**Symptom:** The "Bridge" has only one `Shape` and two `Renderer` implementations. No new shapes are anticipated. The Bridge pattern adds two interface files and one composition relationship for no actual benefit over a simple Strategy pattern.

**Root Cause:** Bridge was applied when only one dimension of variation exists.

**Diagnostic:**
```bash
# Count shapes in the abstraction hierarchy:
find src -name "*.java" -exec grep -l \
  "extends Shape" {} \; | wc -l
# If result is 1 (only one shape):
# Bridge is overkill - use Strategy or simple interface
```

**Fix:**
Remove the abstraction hierarchy. Use a plain Strategy pattern: `class ShapeRenderer { private Renderer renderer; ... }`.

**Prevention:** Apply Bridge only when two dimensions are confirmed to vary independently. YAGNI (You Ain't Gonna Need It) if only one dimension currently varies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Abstraction` - Bridge requires identifying what is the "high-level abstraction" versus the "low-level implementation" - a judgment requiring experience
- `Composition over Inheritance` - Bridge's core mechanism is composition (HAS-A) replacing inheritance (IS-A) for one dimension of variation
- `Interface` - both the abstraction and implementation hierarchies are typically interface-based in modern Java

**Builds On This (learn these next):**
- `Abstract Factory` - often paired with Bridge: the Abstract Factory creates matching abstraction+implementation pairs for Bridge-structured code
- `Strategy` - the simpler sibling; use Strategy when only one dimension varies; upgrade to Bridge when a second varies
- `Decorator` - can be layered on the abstraction side of Bridge to add behaviours; the implementation side remains unchanged

**Alternatives / Comparisons:**
- `Adapter` - fixes existing incompatibility; Bridge prevents future expansion problems. Both use composition, but for different goals
- `Strategy` - one dimension of algorithm variation; simpler than Bridge; use when only the "implementation" hierarchy varies with no abstraction hierarchy
- `Abstract Factory` - creates families of objects; Bridge defines how families of abstractions and implementations connect

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two separate hierarchies (abstraction +   │
│              │ implementation) connected by composition  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Adding to two separate dimensions creates │
│ SOLVES       │ O(m×n) class explosion in one hierarchy   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Composition (HAS-A) between hierarchies   │
│              │ replaces inheritance (IS-A) across dims   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Two truly independent dimensions both     │
│              │ need to grow and vary                     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one dimension varies (use Strategy); │
│              │ dimensions are coupled (rethink design)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Linear class growth + runtime flexibility │
│              │ vs upfront complexity in identifying dims │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two hierarchies, one bridge -            │
│              │  each grows without touching the other." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy → Abstract Factory →             │
│              │ Decorator                                 │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Identify two orthogonal dimensions of variation and separate
them into independent hierarchies connected by composition.
Avoid the exponential class count that results from combining
both dimensions in a single hierarchy.

**Where else this pattern appears:**
- **Rendering engines:** A `Shape` abstraction (Circle, Rectangle)
  is decoupled from its `Renderer` implementation (Vector, Raster)
  -- 2 shapes x 2 renderers = 4 combinations, not 4 subclasses.
- **Logging frameworks (SLF4J/Logback):** SLF4J is the abstraction
  (Logger interface); Logback, Log4j2 are the implementations.
  Code uses SLF4J; the implementation is bound at runtime -- a
  textbook Bridge.
- **Payment processing:** `PaymentProcessor` abstraction +
  `PaymentGateway` implementation -- swap between Stripe, PayPal,
  Adyen without changing the domain model.

---

### 💡 The Surprising Truth

SLF4J (Simple Logging Facade for Java) is used in nearly every
Java application but is rarely recognized as a Bridge pattern
implementation. The `Logger` interface is the Abstraction; the
binding jars (`slf4j-simple`, `logback-classic`, `log4j-slf4j`)
are Concrete Implementors. The `LoggerFactory` is the bridge.
This means every time a Java developer writes
`LoggerFactory.getLogger(MyClass.class)`, they are instantiating
a Bridge -- making it one of the most-used GoF patterns in
the Java ecosystem, almost entirely invisibly.
---

### 🧠 Think About This Before We Continue

**Q1.** A payment system uses Bridge: `Transaction` abstraction hierarchy and `PaymentProcessor` (Stripe, PayPal, SEPA) implementation hierarchy. A new requirement: add transaction types `Refund` and `Chargeback`. But Stripe's refund API requires a `chargeId` (the original transaction reference), while SEPA refunds use a bank reference number - the two processors have fundamentally different refund parameters. Trace exactly where the Bridge breaks down and describe what information needs to be added to the `PaymentProcessor` interface to handle this, without leaking processor-specific types to the abstraction side.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** JDBC is cited as a real-world Bridge. The `Connection` interface is the bridge between application code and database-specific drivers. But a developer points out: "The `Connection.getMetaData()` method returns `DatabaseMetaData`, which has 150+ methods, many of which are database-specific (e.g., `supportsStoredProcedures()` returns different values per DB). This means the application CAN depend on database-specific behaviour through the Bridge interface." Is this a Bridge design flaw or an intentional design decision, and how does it relate to the principle that Bridge interfaces should expose generic primitives only?



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A team uses Bridge to decouple
`NotificationService` (Email, SMS, Push) from
`NotificationChannel` (Twilio, SendGrid, Firebase). After
six months, they have 3 services x 3 channels = 9 combinations.
A new requirement: batch notification (different from
single notification). Evaluate whether this new dimension
fits the existing Bridge, requires a second Bridge, or
signals that a different pattern is needed.

*Hint: The First Principles section and the Comparison Table
show when Bridge vs Decorator is appropriate. Count the
axes of variation: 3 axes of change = Bridge struggling;
consider Composite or Strategy for the batch axis.*
