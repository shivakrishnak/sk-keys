---
id: DPT-013
title: Bridge
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-012
used_by: DPT-041, DPT-064
related: DPT-012, DPT-015, DPT-018, DPT-041
tags:
  - pattern
  - structural
  - advanced
  - architecture
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/design-patterns/bridge/
---

⚡ TL;DR - Bridge separates an abstraction from its
implementation so the two can vary independently - preventing
a class hierarchy from exploding when both the abstraction
and implementation have multiple variants.

| #13 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-012 | |
| **Used by:** | DPT-041, DPT-064 | |
| **Related:** | DPT-012, DPT-015, DPT-018, DPT-041 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A shape library needs to render shapes on multiple platforms.
Shapes: Circle, Square, Triangle. Platforms: Windows, Mac,
Linux. Using inheritance to combine both dimensions:
`WindowsCircle`, `MacCircle`, `LinuxCircle`,
`WindowsSquare`, `MacSquare`, `LinuxSquare`,
`WindowsTriangle`, `MacTriangle`, `LinuxTriangle` -
9 classes for 3 shapes x 3 platforms.

**THE BREAKING POINT:**
Adding a 4th shape (Rectangle) adds 3 more classes.
Adding a 4th platform (Web) adds 3 more classes.
With S shapes and P platforms: S x P classes.
A modest 5-shapes x 5-platforms system needs 25 classes,
each a near-copy of the others. This is the "Cartesian
product class explosion" problem.

**THE INVENTION MOMENT:**
Bridge separates the two dimensions: Shapes and Renderers
become independent hierarchies, connected by a "bridge"
reference. Adding a new shape: one Shape class. Adding a
new platform: one Renderer class. Total: S + P classes
instead of S x P.

**EVOLUTION:**
Bridge is less commonly recognized than other patterns because
it addresses a CLASS DESIGN problem that becomes visible
only as systems grow. It is most visible in GUI toolkits
(abstraction = widget behavior, implementation = platform
rendering), driver architectures (abstraction = device
type, implementation = driver), and persistence layers
(abstraction = repository operations, implementation =
SQL dialect).

---

### 📘 Textbook Definition

The **Bridge** pattern is a Structural design pattern that
decouples an abstraction from its implementation so that
the two can vary independently. The pattern involves an
Abstraction class that holds a reference to an
Implementation interface (the "bridge"). The Abstraction
implements high-level behavior using the Implementation
interface. Concrete implementations are independent of
the Abstraction hierarchy - they can be extended, replaced,
or swapped without affecting the Abstraction classes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bridge replaces one big class hierarchy (Shapes x Platforms)
with two small independent hierarchies (Shapes + Platforms)
connected by a reference.

**One analogy:**
> A universal TV remote (Abstraction) has "volume up,"
> "channel change," "power" buttons. The TV model
> (Implementation) decides how these commands actually
> work. You can have any remote with any TV - the remote
> does not care which TV brand it controls; the TV does
> not care which remote sends the commands. Separate
> hierarchies, connected by an IR signal (the bridge).

**One insight:**
Bridge's insight is that inheritance conflates TWO
independent variation dimensions. When you see an
inheritance tree where some subclasses exist to vary
behavior X while others vary platform Y, Bridge is the
solution: make X and Y independent hierarchies.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The Abstraction has a reference to an Implementor
   interface - this reference IS the bridge.
2. Abstraction subclasses extend behavior using the
   Implementor interface only - never the concrete
   implementation.
3. The two hierarchies vary independently - adding to
   one hierarchy does not affect the other.

**DERIVED DESIGN:**
Four participants:
- **Abstraction**: high-level control layer; holds
  reference to Implementor
- **RefinedAbstraction**: extends Abstraction to add
  more specific behavior
- **Implementor**: interface for implementation objects;
  lowest-level operations (primitives that Abstraction
  builds upon)
- **ConcreteImplementor**: specific implementation

**RELATIONSHIP TO ADAPTER:**
Adapter and Bridge both use composition to connect two
interfaces. KEY DIFFERENCE: Adapter retrofits two existing
incompatible interfaces - it is applied after the fact.
Bridge is designed UP FRONT to keep two hierarchies
separate. Adapter = "I need to integrate this." Bridge =
"I will design this so neither side depends on the other."

**TRADE-OFFS:**

**Gain:** Eliminates class count explosion. Independent
variation. Implementation can be switched at runtime.

**Cost:** Added indirection. The design is more complex
upfront. If only one implementation ever exists, Bridge
adds complexity with no benefit. The pattern is correct
when BOTH dimensions genuinely vary independently.

---

### 🧪 Thought Experiment

**SETUP:**
A notification system sends messages through Email, SMS,
or Push channels. Notifications have two variants by
urgency: NormalNotification and UrgentNotification (with
retry logic). Without Bridge:
`EmailNormalNotification`, `SmsNormalNotification`,
`PushNormalNotification`, `EmailUrgentNotification`,
`SmsUrgentNotification`, `PushUrgentNotification` - 6 classes.

**WHAT HAPPENS WITHOUT BRIDGE:**
Adding Slack notifications: 2 more classes.
Adding a ThrottledNotification variant: 3 more classes.
After modest growth: 10+ classes, each nearly identical,
most duplicating the urgency retry logic or the channel
sending logic.

**WHAT HAPPENS WITH BRIDGE:**
`NotificationSender` (Implementor interface): `send(msg)`
`EmailSender`, `SmsSender`, `PushSender`, `SlackSender`
(ConcreteImplementors).
`Notification` (Abstraction): holds `NotificationSender`.
`NormalNotification`, `UrgentNotification`
(RefinedAbstractions).
Total: 4 senders + 2 notifications = 6 classes (same now,
but adding Slack: 1 class; adding Throttled: 1 class).

**THE INSIGHT:**
Bridge pays off when growth in EITHER dimension is expected.
It is an investment: more complexity today for less
complexity as the system grows.

---

### 🧠 Mental Model / Analogy

> Bridge is a PLUG AND SOCKET system. The device (Abstraction)
> has one plug type. The power outlet (Implementor) can be
> any standard type. Different devices plug into the same
> outlet; the same device can be used with different adapters
> to fit different outlets. The plug interface is the bridge.

- "Device" = Abstraction
- "Plug interface" = the bridge (Implementor reference)
- "Wall outlet" = ConcreteImplementor
- "Device variant" = RefinedAbstraction
- "Outlet type" = specific implementation

**Where this analogy breaks down:**
Physical plugs are rigid and incompatible - hence the need
for adapters. Bridge in code means the Abstraction was
DESIGNED to accept any compatible Implementor. The design
intent is flexibility from the start, not after-the-fact
workaround.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Bridge splits a class that varies in two ways into two
separate hierarchies. Instead of one big tree of
"every combination," you have two small trees connected
by a reference. Change one without touching the other.

**Level 2 - How to use it (junior developer):**
Identify the two independent dimensions. Create an interface
for the implementation dimension (Implementor). Create a
base class for the abstraction dimension that HOLDS A
REFERENCE to the Implementor (not inherits). Concrete
implementations implement the Implementor interface.
Concrete abstractions extend the Abstraction and use
the Implementor reference to do their work.

**Level 3 - How it works (mid-level engineer):**
The bridge is the reference from Abstraction to Implementor.
When `Abstraction.operation()` is called, it delegates
primitive operations to `implementor.primitiveOp()`. The
Abstraction composes multiple primitive operations into
higher-level behavior. This composition happens via the
bridge, so any Implementor works with any Abstraction
without either knowing the concrete type of the other.

**Level 4 - Why it was designed this way (senior/staff):**
GoF Bridge addresses the class hierarchy explosion that
occurs when a single hierarchy tries to encode multiple
independent variation axes. The pattern is the structural
equivalent of the Single Responsibility Principle applied
at the hierarchy level: a class hierarchy should have ONE
reason to change. Abstraction varies for one reason
(behavior granularity); Implementation varies for another
(platform, driver, backend). Keeping them separate means
each hierarchy has one reason to change.

**Level 5 - Mastery (distinguished engineer):**
Bridge appears in JDBC at the architectural level:
`java.sql.Connection` defines the Abstraction (SQL
operations: execute, commit, rollback); each JDBC driver
(PostgreSQL, MySQL, H2) is a ConcreteImplementor; DAO
classes using Connection are the RefinedAbstractions that
use Connection operations to implement domain-specific
persistence. Spring Data Repository is a further refinement:
the Repository interface (Abstraction) uses either JPA
or JDBC implementations (Implementors) to fulfill the
same repository contract. The pattern governs the entire
Java persistence layer architecture.

---

### ⚙️ How It Works (Mechanism)

```
Bridge Structure
┌─────────────────────────────────────────────────────────┐
│  Abstraction                                            │
│  - impl: Implementor ← THE BRIDGE REFERENCE            │
│  + feature(): void                                      │
│    impl.primitiveA()  ← uses Implementor               │
│    impl.primitiveB()  ← uses Implementor               │
│         ▲                                               │
│  RefinedAbstraction                                     │
│  + refinedFeature(): void                               │
│    impl.primitiveA()  ← still uses bridge              │
│                                                         │
│  <<interface>> Implementor                              │
│  + primitiveA(): void                                   │
│  + primitiveB(): void                                   │
│         ▲              ▲                                │
│  ConcreteImplA    ConcreteImplB                         │
│  primitiveA()     primitiveA()                          │
│  primitiveB()     primitiveB()                          │
│                                                         │
│  Two hierarchies: Abstraction and Implementor           │
│  Connected by single reference - the "bridge"           │
└─────────────────────────────────────────────────────────┘
```

**Class count comparison:**
```
Inheritance (S shapes x P platforms):
  S=3, P=3: 9 classes
  S=5, P=5: 25 classes  ← explosion

Bridge (S shapes + P platforms):
  S=3, P=3: 3+3 = 6 classes
  S=5, P=5: 5+5 = 10 classes ← linear growth
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client creates ConcreteImplA (e.g., WindowsRenderer)
Client creates RefinedAbstraction (e.g., Circle)
  with impl = WindowsRenderer (injected)
Client calls circle.draw()
  → Circle.draw() calls impl.renderArc() (Implementor
    method)
  → WindowsRenderer.renderArc() executes platform code
Swap to MacRenderer: same circle, different impl injected
  → circle.draw() calls impl.renderArc()
  → MacRenderer.renderArc() executes Mac platform code
Circle code unchanged; only the injected impl differs
```

**FAILURE PATH:**
```
Abstraction.operation() calls a method on Implementor
  that was added to ConcreteImplA but is not in the
  Implementor interface
  → ConcreteImplB does not have that method
  → Casting to ConcreteImplA breaks the abstraction goal
  → Symptom: ClassCastException or missing-method errors
    when swapping implementations
```

**WHAT CHANGES AT SCALE:**
Bridge itself has no scale concerns. At scale, the bridge
reference may be a pooled connection or a proxy to a remote
implementation (as in JDBC). The Abstraction never needs
to know if the Implementor is local, pooled, or remote.

---

### 💻 Code Example

**Example 1 - Class explosion without Bridge:**

```java
// BAD: S x P classes (3 shapes x 3 renderers = 9 classes)
abstract class Shape { abstract void draw(); }
class WindowsCircle extends Shape { void draw() {/*Win circle*/}}
class MacCircle     extends Shape { void draw() {/*Mac circle*/}}
class LinuxCircle   extends Shape { void draw() {/*Lnx circle*/}}
class WindowsSquare extends Shape { void draw() {/*Win square*/}}
// ... 6 more classes. Adding WebRenderer: 3 more. OCP violated.
```

**Example 2 - Bridge solution:**

```java
// GOOD: Bridge separates shape behavior from rendering

// Implementor: platform rendering primitives
interface Renderer {
    void renderCircle(double radius);
    void renderSquare(double side);
}

// ConcreteImplementors: platform-specific
class WindowsRenderer implements Renderer {
    public void renderCircle(double r) {
        System.out.println("Win: circle r=" + r);
    }
    public void renderSquare(double s) {
        System.out.println("Win: square s=" + s);
    }
}

class MacRenderer implements Renderer {
    public void renderCircle(double r) {
        System.out.println("Mac: circle r=" + r);
    }
    public void renderSquare(double s) {
        System.out.println("Mac: square s=" + s);
    }
}

// Abstraction: shape behavior via bridge
abstract class Shape {
    protected Renderer renderer; // THE BRIDGE
    Shape(Renderer renderer) { this.renderer = renderer; }
    abstract void draw();
}

// RefinedAbstractions: specific shapes
class Circle extends Shape {
    private double radius;
    Circle(double r, Renderer renderer) {
        super(renderer);
        this.radius = r;
    }
    public void draw() {
        renderer.renderCircle(radius); // bridge call
    }
}

class Square extends Shape {
    private double side;
    Square(double s, Renderer renderer) {
        super(renderer);
        this.side = s;
    }
    public void draw() {
        renderer.renderSquare(side); // bridge call
    }
}

// Usage: inject any renderer with any shape
Renderer win = new WindowsRenderer();
Renderer mac = new MacRenderer();

Circle c1 = new Circle(5.0, win); // Windows circle
Circle c2 = new Circle(5.0, mac); // Mac circle - same class!
Square s1 = new Square(3.0, win); // Windows square

c1.draw(); // Win: circle r=5.0
c2.draw(); // Mac: circle r=5.0
// Adding WebRenderer: 1 class, no changes to Circle or Square
// Adding Triangle: 1 class, no changes to any Renderer
```

**Example 3 - Bridge at runtime (implementation swap):**

```java
// GOOD: swap implementation at runtime
class Notification {
    private NotificationSender sender; // bridge

    Notification(NotificationSender sender) {
        this.sender = sender;
    }

    // Swap implementation without changing behavior class
    public void setSender(NotificationSender sender) {
        this.sender = sender;
    }

    public void send(String message) {
        sender.deliver(message);
    }
}

// Development: use console sender (no real messages)
Notification n = new Notification(new ConsoleSender());
n.send("Test"); // console output

// Production: swap to email sender
n.setSender(new EmailSender());
n.send("Production"); // actual email sent
```

**How to test/verify correctness:**
Test each RefinedAbstraction with a mock Implementor.
The mock verifies that the correct primitive operations
are called with the correct parameters. Test each
ConcreteImplementor independently from any Abstraction.
Verify that swapping implementations at runtime produces
the expected behavior change.

---

### ⚖️ Comparison Table

| Aspect             | Bridge          | Adapter          | Strategy       |
| ------------------ | --------------- | ---------------- | -------------- |
| **Intent**         | Decouple 2 dims | Convert interface| Algorithm swap |
| **Design time**    | Proactive       | Retroactive      | Proactive      |
| **Class explosion**| Prevents        | Not applicable   | Not applicable |
| **Interface change**| No             | Yes              | No             |
| **Both vary?**     | Yes (key)       | No               | No             |

**How to choose:**
- Two independently varying dimensions? Bridge
- Integrating incompatible existing interfaces? Adapter
- Swapping algorithms at runtime? Strategy
- Bridge and Strategy look similar (both hold a reference
  to an interface); DIFFERENCE: Bridge separates STRUCTURAL
  dimension (implementation platform); Strategy swaps
  BEHAVIORAL algorithm

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bridge and Adapter are the same | Adapter: retroactive fix for incompatible interfaces. Bridge: proactive design to prevent class explosion by separating two variation dimensions |
| Bridge and Strategy are the same | Strategy: one dimension of behavioral variation. Bridge: two structural dimensions varied independently. Both use composition to hold an interface reference but serve different purposes |
| Bridge requires two class hierarchies to exist upfront | Bridge is applied when TWO dimensions will vary; the second hierarchy may be empty (one implementation) initially |
| Bridge is only for UI rendering | Bridge applies anywhere two independent variation axes would produce a Cartesian product class explosion: persistence + database type, notification urgency + delivery channel, etc. |
| Bridge prevents using the concrete implementation | Bridge prevents the ABSTRACTION from needing to know about concrete implementations; the factory or DI container that assembles them can create any combination |

---

### 🚨 Failure Modes & Diagnosis

**Implementor Interface Too Thin - Abstraction Casts Down**

**Symptom:**
`Abstraction.operation()` contains:
`if (impl instanceof ConcreteImplA ca) ca.specificMethod()`.
The bridge reference is cast to a concrete type inside
the abstraction, negating the entire purpose of the pattern.

**Root Cause:**
The Implementor interface is incomplete: ConcreteImplA has
a capability that is not expressed in the Implementor
interface, so the Abstraction casts to access it.

**Diagnostic Signal:**
`instanceof` checks on the Implementor reference inside any
Abstraction class indicate the interface is insufficient.

**Fix:**
Add the capability to the Implementor interface (if ALL
implementations can reasonably support it). OR: create a
second, extended Implementor interface for the enhanced
capability and use separate Abstraction subclasses that
depend on the extended interface.

**Prevention:**
Define the Implementor interface based on everything the
Abstraction hierarchy WILL NEED from it - not just what
the first implementation provides. An incomplete Implementor
interface forces instanceof checks in Abstraction, breaking
the pattern.

---

**Single Implementation Bridge - YAGNI Violation**

**Symptom:**
A codebase has a `Bridge` structure with one ConcreteImplementor,
and the team says "we will add more implementations later."
"Later" never arrives. The Bridge adds indirection with no
benefit realized. New team members find the two-hierarchy
structure confusing without context.

**Root Cause:**
Bridge was applied speculatively. If only one implementation
ever exists, the pattern cost (complexity, indirection) was
paid without the benefit (class count reduction).

**Diagnostic Signal:**
Count ConcreteImplementors. If 1 and no concrete plans to
add more: evaluate whether Bridge is premature.

**Fix:**
Collapse the Bridge to a simpler design if the second
variation dimension never materializes. Refactoring a Bridge
to simpler code is straightforward (move concrete impl
code into the abstraction).

**Prevention:**
Apply Bridge when you have EVIDENCE of two independent
variation axes - ideally when the second axis is already
needed (you have 2+ implementations). YAGNI: do not apply
Bridge for hypothetical future needs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Adapter` - related wrapping pattern; understanding
  Adapter first makes the Bridge vs Adapter distinction
  clearer

**Builds On This (learn these next):**
- `Decorator vs Proxy vs Adapter` - deep structural pattern
  comparison; includes Bridge distinctions
- `Pattern-Driven Architecture Design` - how Bridge governs
  the Hexagonal Architecture layer design

**Alternatives / Comparisons:**
- `Adapter` - retroactive interface fix; Bridge is
  proactive design for independent variation
- `Strategy` - swaps behavioral algorithms; Bridge separates
  structural implementation dimensions

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Decouple abstraction from implementation │
│              │ so both can vary independently           │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ S x P class explosion when two variation │
│ SOLVES       │ dimensions combine via inheritance       │
├──────────────┼──────────────────────────────────────────┤
│ THE BRIDGE   │ A reference from Abstraction to the      │
│              │ Implementor interface                    │
├──────────────┼──────────────────────────────────────────┤
│ VS ADAPTER   │ Adapter = retroactive fix (interfaces    │
│              │ exist, need to connect them)             │
│              │ Bridge = proactive design (prevent       │
│              │ explosion before it happens)             │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Two independent variation axes exist;    │
│              │ class count would be S x P with inherit. │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Only one implementation exists or is     │
│              │ planned (YAGNI)                          │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ JDBC: Connection (Abstraction) + Driver  │
│              │ (ConcreteImplementor per database type)  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Composite → Decorator → Facade           │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Bridge = S + P classes (NOT S x P); the bridge reference
   allows any Abstraction to work with any Implementor
   without either knowing the other's concrete type
2. Bridge is PROACTIVE design; Adapter is RETROACTIVE -
   this timing distinction is the key difference
3. JDBC is the canonical Java Bridge: Connection is the
   Abstraction; each JDBC driver is a ConcreteImplementor;
   DAO code using Connection is the RefinedAbstraction

**Interview one-liner:**
"Bridge separates an abstraction from its implementation
so both can vary independently, preventing Cartesian product
class explosion. It is a proactive design (vs Adapter which
retrofits). JDBC is the canonical example: Connection
defines the SQL operation abstraction; each database driver
is a ConcreteImplementor; the connection IS the bridge."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you detect that a class hierarchy is growing along two
independent axes, the hierarchy is doing too much. Split the
axes into separate hierarchies connected by composition.
The principle: "two reasons to subclass = two hierarchies."

**Where else this pattern appears:**
- **JDBC** - the most complete Bridge in the Java ecosystem:
  `java.sql.Connection` defines the abstraction; PostgreSQL,
  MySQL, Oracle JDBC drivers are ConcreteImplementors;
  Spring's `JdbcTemplate` is a RefinedAbstraction
- **AWT/Swing peer architecture** - Java AWT `Component`
  (Abstraction) delegates rendering to platform-specific
  `ComponentPeer` (Implementor); each OS provides a
  ConcreteImplementor

**Industry applications:**
- **Repository pattern in Spring Data** - `CrudRepository`
  (Abstraction) is implemented by JPA, JDBC, MongoDB, Redis
  implementations (Implementors); the same repository
  interface works with any storage backend
- **Logging frameworks** - SLF4J Logger (Abstraction) bridges
  to Log4j/Logback/JUL implementations (Implementors); any
  application code using SLF4J works with any backend

---

### 💡 The Surprising Truth

The GoF Bridge chapter includes one of the most counterintuitive
statements in the book: "Degenerate cases of the Bridge
pattern, in which the implementor is fixed and only the
abstraction changes, are almost indistinguishable from
pure inheritance." This means: if you only ever have one
Implementor, Bridge and inheritance look identical. The
pattern only reveals its value when both dimensions actually
vary. This is why Bridge is often introduced AFTER the
class explosion problem appears - because with only one
implementation, there is no way to see the pattern's value
in advance. Expert engineers recognize the warning signs
early: "If we add another platform, we will need N new
classes" is the signal to introduce Bridge before the
explosion, not after.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Draw the class count comparison: an S x P
   inheritance hierarchy vs an S + P Bridge hierarchy,
   and explain why Bridge grows linearly while inheritance
   grows quadratically
2. [DISTINGUISH] State the design-time difference between
   Bridge (proactive) and Adapter (retroactive) in one
   sentence, with a concrete example of when each applies
3. [IDENTIFY] Recognize JDBC as a Bridge implementation:
   name the four Bridge participants in JDBC (Abstraction,
   RefinedAbstraction, Implementor, ConcreteImplementor)
4. [BUILD] Implement a Bridge for a notification system
   with urgency levels (Normal, Urgent) and delivery
   channels (Email, SMS), showing the two hierarchies
   and the bridge reference
5. [DECIDE] Given a class with `WindowsCircle`,
   `MacCircle`, `WindowsSquare`, `MacSquare`, diagnose
   the class explosion problem and sketch the Bridge
   refactoring that eliminates the Cartesian product

---

### 🧠 Think About This Before We Continue

**Q1.** JDBC's `java.sql.Connection` is a Bridge. But
Connection also implements AutoCloseable and has many
convenience methods beyond the core primitives. Is
JDBC's Connection a "pure" Bridge, and does it need to
be? What would a "pure" Bridge JDBC Connection look like,
and would it be better or worse than the actual JDBC API?

*Hint: A "pure" Bridge Implementor would contain only
the lowest-level primitives (sendSQL(), receive()). JDBC
Connection includes higher-level operations (commit(),
rollback(), prepareStatement()) that are composed from
lower primitives. This is "RefinedAbstraction" territory
mixed into the Implementor, which is pragmatic but not
pure. Pure Bridge separation would make JDBC more complex
to use without meaningful benefit. Pragmatic pattern
application matters more than purity.*

**Q2.** Spring Data Repository provides `CrudRepository<T,ID>`
as the Abstraction and has JPA, JDBC, MongoDB, Redis,
Elasticsearch implementations. When you define a
custom `interface UserRepository extends CrudRepository<User,
Long>`, where does YOUR interface fit in the Bridge pattern?
Is it Abstraction, RefinedAbstraction, or something new?

*Hint: CrudRepository = Abstraction. Your UserRepository
= RefinedAbstraction (it refines CrudRepository with
domain-specific methods like findByEmail()). Spring Data's
JPA implementation of YOUR interface = ConcreteImplementor.
The @Repository proxy Spring creates = the bridge reference.
Spring Data is Bridge applied at the framework level.*

**Q3.** A team proposes replacing a complex notification
Bridge (4 urgency levels x 5 channels = 20 combinations
handled by Bridge's 9 classes) with a simple
`Map<UrgencyLevel, Map<Channel, NotificationHandler>>`
registry. Evaluate: when is the registry approach better,
and when does Bridge win?

*Hint: Registry wins when the matrix is SPARSE (not all
combinations are valid or needed). Registry wins when
the behavior per cell is SIMPLE (just call a handler).
Bridge wins when Abstraction subclasses have significant
LOGIC that operates on the Implementor (not just dispatch).
Bridge wins when the Abstraction AND Implementor hierarchies
have deep, independent behavior trees. Registry wins for
dispatch-only scenarios with sparse combinations.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Bridge and Adapter?
Why is one "proactive" and the other "retroactive"?**

*Why they ask:* Bridge vs Adapter is a common structural
pattern confusion in senior interviews.

*Strong answer includes:*
- Adapter: TWO pre-existing interfaces are incompatible;
  Adapter makes them work together WITHOUT modifying either
  (retroactive - applied to existing designs)
- Bridge: DESIGNED from the start to separate two variation
  dimensions; the Implementor interface and bridge reference
  are planned before the hierarchy grows (proactive)
- Timing: Adapter = "I have this incompatibility, fix it."
  Bridge = "I can see these two dimensions will grow
  independently; I'll separate them now."
- Real test: in code review, Adapter is used when integrating
  a library; Bridge is used when designing a new subsystem
  with multiple variation axes

**Q2: When would you NOT apply Bridge, even when two
dimensions exist?**

*Why they ask:* Tests engineering judgment - when to avoid
a pattern, not just when to use it.

*Strong answer includes:*
- YAGNI: if only ONE implementation will ever exist, Bridge
  adds indirection with no benefit
- If the two dimensions are NOT truly independent (every
  combination of Shape and Renderer produces different
  behavior that cannot be composed from primitives), Bridge
  may not reduce class count
- Simple cases: if S x P produces only 4 classes (2x2),
  Bridge adds complexity without meaningful benefit
- Rule: apply Bridge when S x P is currently >= 6 and
  growth in either dimension is planned

**Q3: Identify Bridge in Java's standard library or
Spring framework and name all four pattern participants.**

*Why they ask:* Tests ability to recognize patterns in
production code.

*Strong answer includes:*
- **JDBC**: Abstraction = `java.sql.Connection` interface;
  RefinedAbstraction = `JdbcTemplate` (Spring); Implementor =
  internal connection primitives; ConcreteImplementor =
  PostgresConnection, MySQLConnection (driver-specific)
- **SLF4J**: Abstraction = `org.slf4j.Logger`;
  RefinedAbstraction = your application code using Logger;
  Implementor = `org.slf4j.spi.LocationAwareLogger`;
  ConcreteImplementors = Log4j adapter, Logback adapter
- Can name either; explain the four participants correctly
  for full marks

