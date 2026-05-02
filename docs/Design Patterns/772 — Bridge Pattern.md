---
layout: default
title: "Bridge Pattern"
parent: "Design Patterns"
nav_order: 772
permalink: /design-patterns/bridge-pattern/
number: "772"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Adapter Pattern, Composition over Inheritance"
used_by: "Cross-platform UI, Driver layers, Plugin systems, Decoupled hierarchies"
tags: #advanced, #design-patterns, #structural, #oop, #decoupling
---

# 772 — Bridge Pattern

`#advanced` `#design-patterns` `#structural` `#oop` `#decoupling`

⚡ TL;DR — **Bridge** decouples an abstraction from its implementation so both can vary independently — avoiding a cartesian product of subclasses by separating two dimensions of variation (e.g., Shape and Color) into two independent hierarchies connected by composition.

| #772            | Category: Design Patterns                                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Adapter Pattern, Composition over Inheritance |                 |
| **Used by:**    | Cross-platform UI, Driver layers, Plugin systems, Decoupled hierarchies    |                 |

---

### 📘 Textbook Definition

**Bridge** (GoF, 1994): a structural design pattern that decouples an abstraction from its implementation so that the two can vary independently. Solves the problem of class hierarchy explosion when two dimensions of variation are needed. The "abstraction" (high-level control) holds a reference to an "implementor" (low-level operations); subclasses of the abstraction can vary independently from subclasses of the implementor. Key structural move: instead of inheriting from two axes (Shape × Color → 4 subclasses, 3 colors → 9), use composition: Shape holds a reference to Color. GoF intent: "Decouple an abstraction from its implementation so that the two can vary independently." Distinguished from Adapter: Adapter makes incompatible things work together. Bridge is designed upfront to allow independent variation.

---

### 🟢 Simple Definition (Easy)

TV and Remote Control. The TV is the implementation — Sony TV, Samsung TV, LG TV. The Remote is the abstraction — BasicRemote, AdvancedRemote. Any remote works with any TV. Without Bridge, you'd need: SonyBasicRemote, SonyAdvancedRemote, SamsungBasicRemote, SamsungAdvancedRemote — 6 classes for 3 TVs × 2 remotes. With Bridge: 3 TV classes + 2 Remote classes = 5. The remote HOLDS A REFERENCE to the TV (composition) instead of inheriting from it.

---

### 🔵 Simple Definition (Elaborated)

`Shape` abstraction × `Color` implementation. Without Bridge: `RedCircle`, `BlueCircle`, `RedSquare`, `BlueSquare` — 4 classes. Add Purple → 2 more. Add Triangle → 3 more. N shapes × M colors = N×M subclasses. With Bridge: `Circle extends Shape`, `Square extends Shape`; `RedColor implements Color`, `BlueColor implements Color`. `Circle` holds a `Color` reference (composed). 2 shapes + 2 colors = 4 classes. Add Purple: +1. Add Triangle: +1. N + M instead of N×M.

---

### 🔩 First Principles Explanation

**The class explosion problem and how Bridge solves it structurally:**

```
PROBLEM — INHERITANCE CAUSES CLASS EXPLOSION:

  2 DIMENSIONS: Shape type × Rendering platform

  WITHOUT BRIDGE:
  ───────────────
  Circle                 → draw on Vector
  CircleOnRaster         → draw on Raster
  Square                 → draw on Vector
  SquareOnRaster         → draw on Raster

  Add a 3rd platform (OpenGL)?
  CircleOnOpenGL, SquareOnOpenGL — now 6 classes.

  Add Triangle?
  TriangleOnVector, TriangleOnRaster, TriangleOnOpenGL — now 9.

  3 shapes × 3 platforms = 9 classes. Every new shape: +3. Every new platform: +3 shapes.

BRIDGE SOLUTION:

  SEPARATE INTO TWO HIERARCHIES:

  // IMPLEMENTOR hierarchy (platform-specific drawing):
  interface DrawingAPI {
      void drawCircle(double x, double y, double radius);
      void drawRectangle(double x1, double y1, double x2, double y2);
  }

  class VectorDrawingAPI implements DrawingAPI {
      void drawCircle(...)    { /* SVG vector circle */ }
      void drawRectangle(...) { /* SVG vector rectangle */ }
  }

  class RasterDrawingAPI implements DrawingAPI {
      void drawCircle(...)    { /* Pixel-based circle */ }
      void drawRectangle(...) { /* Pixel-based rectangle */ }
  }

  class OpenGLDrawingAPI implements DrawingAPI {
      void drawCircle(...)    { /* OpenGL circle */ }
      void drawRectangle(...) { /* OpenGL rectangle */ }
  }

  // ABSTRACTION hierarchy (shape types):
  abstract class Shape {
      protected DrawingAPI api;  // ← THE BRIDGE: holds reference to implementor

      Shape(DrawingAPI api) { this.api = api; }

      abstract void draw();
      abstract void resize(double factor);
  }

  class Circle extends Shape {
      private double x, y, radius;

      Circle(double x, double y, double radius, DrawingAPI api) {
          super(api);
          this.x = x; this.y = y; this.radius = radius;
      }

      void draw()               { api.drawCircle(x, y, radius); }  // delegates to implementor
      void resize(double factor) { radius *= factor; }
  }

  class Square extends Shape {
      private double x, y, side;

      Square(double x, double y, double side, DrawingAPI api) {
          super(api); this.x = x; this.y = y; this.side = side;
      }

      void draw()                { api.drawRectangle(x, y, x+side, y+side); }
      void resize(double factor)  { side *= factor; }
  }

  // Usage:
  Shape circle = new Circle(5, 5, 10, new VectorDrawingAPI());    // Circle on Vector
  Shape square = new Square(0, 0, 20, new OpenGLDrawingAPI());    // Square on OpenGL

  // Add new shape (Triangle): 1 new class. ALL platforms supported automatically.
  // Add new platform (Metal): 1 new DrawingAPI class. ALL shapes supported automatically.

  // 3 shapes + 3 platforms = 6 classes (not 9). Scales: N + M, not N × M.

BRIDGE WITH DEPENDENCY INJECTION (modern style):

  // Instead of passing api in constructor, inject via DI:
  @Component
  class ShapeRenderer {
      private final DrawingAPI drawingAPI;  // injected (Vector/Raster/OpenGL by config)

      ShapeRenderer(DrawingAPI drawingAPI) { this.drawingAPI = drawingAPI; }

      void render(Shape shape) { shape.drawWith(drawingAPI); }
  }

  // Spring selects which DrawingAPI implementation to inject based on config.
  // Application code never sees concrete DrawingAPI.

BRIDGE vs ADAPTER:

  ADAPTER:
  - Intent: "Make this incompatible interface work with my existing code."
  - AFTER the fact — fixes incompatibility between existing classes.
  - Wraps an existing adaptee to expose a different interface.
  - You don't design with Adapter upfront.

  BRIDGE:
  - Intent: "Design two hierarchies that can vary independently from the start."
  - UPFRONT design decision to avoid class explosion.
  - Both abstraction and implementor are designed to be extended independently.

  ADAPTER: post-hoc compatibility. BRIDGE: proactive separation of concerns.

BRIDGE IN JAVA — JDBC:

  java.sql.Connection/Statement/ResultSet = ABSTRACTION hierarchy
  MySQL Driver / PostgreSQL Driver        = IMPLEMENTOR hierarchy

  Your code uses Connection (abstraction).
  JDBC driver (implementor) handles the actual DB protocol.
  New database (e.g., Oracle): add Oracle driver = new implementor.
  Application code: ZERO changes.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Bridge (inheritance-based):

- N shapes × M platforms = N×M subclasses
- Adding 1 platform: N new classes. Adding 1 shape: M new classes. Combinatorial explosion.

WITH Bridge:
→ N + M classes. Adding 1 platform: 1 new implementor class. Adding 1 shape: 1 new abstraction class.

---

### 🧠 Mental Model / Analogy

> A universal remote control and TVs. The remote (abstraction) has buttons: power, volume, channel. It doesn't know if it's controlling a Sony or Samsung (implementor). Inside, the remote holds a reference to whichever TV it's paired with. New TV model: just implement the TV interface. New remote type (voice remote): just add a new remote class. Remote hierarchy and TV hierarchy evolve independently.

"Remote control" = abstraction (Shape, high-level operations)
"TV (Sony/Samsung)" = implementor (DrawingAPI, low-level platform)
"Remote holds reference to TV" = abstraction's `api` field (the bridge)
- "Power button → TV.power()" = abstraction delegates to implementor
"New TV: just implement TV interface" = new implementor, no abstraction changes

---

### ⚙️ How It Works (Mechanism)

```
BRIDGE STRUCTURE:

  Abstraction              «interface» Implementor
  ─────────────            ─────────────────────────
  -impl: Implementor ──────►  +operationImpl()
  +operation()
      → impl.operationImpl()

  RefinedAbstractionA      ConcreteImplementorA
  RefinedAbstractionB      ConcreteImplementorB

  Abstraction holds reference to Implementor.
  Both hierarchies extend independently.
  New abstractions and new implementors never require cross changes.
```

---

### 🔄 How It Connects (Mini-Map)

```
Two dimensions of variation → class explosion without structural separation
        │
        ▼
Bridge Pattern ◄──── (you are here)
(separate abstraction and implementor hierarchies; connect via composition)
        │
        ├── Adapter: solves post-hoc incompatibility vs Bridge: proactive design
        ├── Strategy: implementor is a strategy; Bridge gives it its own hierarchy
        ├── Abstract Factory: can create Bridge pairs (matching abstraction + implementor)
        └── Dependency Injection: inject the implementor (Bridge's implementor reference)
```

---

### 💻 Code Example

```java
// Notification system: Channel (SMS/Email/Push) × Severity (Normal/Urgent):

// IMPLEMENTOR — HOW to send:
interface NotificationChannel {
    void send(String recipient, String message);
}

class EmailChannel implements NotificationChannel {
    public void send(String recipient, String message) {
        emailService.send(recipient, message);
    }
}

class SmsChannel implements NotificationChannel {
    public void send(String recipient, String message) {
        smsGateway.send(recipient, message);
    }
}

class PushChannel implements NotificationChannel {
    public void send(String recipient, String message) {
        pushService.notify(recipient, message);
    }
}

// ABSTRACTION — WHAT kind of notification:
abstract class Notification {
    protected final NotificationChannel channel;  // ← THE BRIDGE

    Notification(NotificationChannel channel) { this.channel = channel; }

    abstract void notify(String recipient, String content);
}

class NormalNotification extends Notification {
    NormalNotification(NotificationChannel channel) { super(channel); }

    public void notify(String recipient, String content) {
        channel.send(recipient, "[INFO] " + content);
    }
}

class UrgentNotification extends Notification {
    UrgentNotification(NotificationChannel channel) { super(channel); }

    public void notify(String recipient, String content) {
        channel.send(recipient, "🚨 URGENT: " + content.toUpperCase());
        channel.send(recipient, "Confirmation required for: " + content);
    }
}

// 2 notification types + 3 channels = 5 classes (not 6).
// Add SlackChannel: 1 class. Works with Normal AND Urgent immediately.
// Add CriticalNotification: 1 class. Works with Email, SMS, Push immediately.

Notification alert = new UrgentNotification(new SmsChannel());
alert.notify("ops-team@example.com", "Database CPU at 95%");
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bridge and Adapter are the same — both use composition | Key difference is INTENT and timing. Adapter: post-hoc fix for incompatible existing interfaces. Bridge: proactive upfront design to enable independent variation. Adapter wraps an existing class to make it conform. Bridge creates two parallel hierarchies designed to be mixed.                                                                                             |
| Bridge always requires two full class hierarchies      | Sometimes one side has only one implementation or no hierarchy at all. The pattern value comes from enabling independent extension — even if today only one implementor exists, the Bridge structure allows adding more without touching abstractions.                                                                                                                           |
| Bridge is the same as Strategy                         | Strategy: an object whose algorithm can be swapped at runtime; focused on interchangeable behaviors. Bridge: structural pattern focused on separating abstraction from implementation hierarchies. Bridge's implementor is a more fundamental structural concept; Strategy is about behavioral variation. However, in code they look similar — both use composition to delegate. |

---

### 🔥 Pitfalls in Production

**Over-engineering: creating Bridge for single-implementation hierarchies:**

```java
// ANTI-PATTERN: Bridge applied prematurely — only one implementation exists:
interface DatabaseStorage {  // "implementor" — but only MySQL will ever be used
    void store(Record r);
}

abstract class Repository {
    protected DatabaseStorage storage;
    Repository(DatabaseStorage s) { this.storage = s; }
}

class UserRepository extends Repository { ... }
class OrderRepository extends Repository { ... }

// Only MySQLStorage is ever created. The abstraction hierarchy (Repository) varies.
// The implementor (DatabaseStorage) doesn't vary in practice.
// YAGNI: the Bridge overhead (two hierarchies, composition) buys nothing here.

// FIX: Don't add Bridge until you ACTUALLY need two varying hierarchies.
// When a second implementor is added, refactor to Bridge at that point.
// RULE: "Two independent axes of variation + each axis has ≥ 2 variants → consider Bridge."

// ANOTHER PITFALL: Leaking implementor details through abstraction:
abstract class Shape {
    protected DrawingAPI api;

    // BAD: exposes the bridge seam:
    DrawingAPI getDrawingAPI() { return api; }  // clients bypass abstraction!
}
// FIX: Never expose the implementor reference. Keep it protected/private.
// Abstraction should fully encapsulate delegation to implementor.
```

---

### 🔗 Related Keywords

- `Adapter Pattern` — post-hoc interface compatibility (vs Bridge: proactive design-time separation)
- `Strategy Pattern` — behavioral variation via composition (structurally similar but different intent)
- `Abstract Factory` — can create Bridge pairs: matching abstraction + implementor instances
- `Decorator Pattern` — adds behavior to abstraction (both use composition but different structure)
- `Composition over Inheritance` — Bridge is the canonical pattern motivating this principle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Decouple abstraction from implementation. │
│              │ Two independent hierarchies linked via    │
│              │ composition. N + M classes, not N × M.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Two independent dimensions of variation;  │
│              │ inheritance would create class explosion;│
│              │ both hierarchies need to be extensible   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one dimension varies; premature      │
│              │ abstraction before second axis appears;  │
│              │ adds complexity for a single implementor  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Universal remote + any TV brand: remote  │
│              │  hierarchy and TV hierarchy each grow    │
│              │  independently — no new remote per TV."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Adapter Pattern → Strategy Pattern →      │
│              │ Composite Pattern → Abstract Factory      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** JDBC is a real-world Bridge: your code uses `java.sql.Connection` (abstraction), and each database vendor provides a `Driver` implementation (implementor). The JDBC `DriverManager.getConnection(url)` selects the right implementor at runtime. However, JDBC doesn't have a deep abstraction hierarchy — `Connection` is mostly a flat interface. In what ways does JDBC satisfy the Bridge pattern, and in what ways does it differ from the textbook GoF pattern? Is this a "pattern instance" or a "pattern inspiration"?

**Q2.** Spring Data repositories are another Bridge-like structure: `UserRepository extends JpaRepository<User, Long>` (abstraction) is backed by a `JpaRepositoryImplementation` (implementor) that delegates to `EntityManager`. You can swap implementations (JPA → MongoDB → R2DBC) by changing the dependency. How does Spring Data's use of interface proxies (generated at runtime) compare to the manual composition approach of Bridge? What are the advantages of Spring's approach?
