---
id: DPT-008
title: Abstract Factory
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-007
used_by: DPT-039
related: DPT-007, DPT-009, DPT-039
tags:
  - pattern
  - creational
  - intermediate
  - architecture
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/design-patterns/abstract-factory/
---

⚡ TL;DR - Abstract Factory provides an interface for creating
FAMILIES of related objects without specifying their concrete
classes - ensuring the created objects are compatible with each
other by construction.

| #8 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-007 | |
| **Used by:** | DPT-039 | |
| **Related:** | DPT-007, DPT-009, DPT-039 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A cross-platform GUI application must render buttons, checkboxes,
and text fields for both Windows and macOS. Without Abstract
Factory, the rendering code is littered with `if (windows) new
WindowsButton(); else new MacButton()` checks for EVERY widget
type. The fatal problem is consistency: nothing stops the code
from creating a `WindowsButton` alongside a `MacCheckbox` -
producing a visual inconsistency that is a runtime problem,
not a compile-time error.

**THE BREAKING POINT:**
In a system with 8 widget types across 3 platforms, the
inconsistency problem has 3^8 = 6,561 possible invalid
combinations. Every code review must manually ensure that
all widgets created together belong to the same platform.
Adding a Linux platform multiplies the complexity again.
The family consistency guarantee is entirely manual.

**THE INVENTION MOMENT:**
Abstract Factory was invented to make family consistency a
COMPILE-TIME guarantee: an object that implements
`WindowsFactory` can ONLY create Windows widgets - by
definition. No code that uses `GuiFactory` can mix Windows
and macOS widgets because the factory interface creates all
family members together. Consistency is structural, not
disciplinary.

**EVOLUTION:**
Abstract Factory was central to early UI toolkits (Motif,
OpenStep), where platform widgets had to be consistent within
a family. Today it governs cloud provider SDK families (AWS
vs. Azure vs. GCP client families), database provider
factories (H2 vs. PostgreSQL vs. MySQL in test/staging/prod),
and theme system factories (dark/light/high-contrast widget
families in UI frameworks).

---

### 📘 Textbook Definition

The **Abstract Factory** pattern is a Creational design pattern
that provides an interface for creating families of related or
dependent objects without specifying their concrete classes.
An abstract factory declares creation methods for each distinct
product type in the family. Concrete factories implement these
creation methods to produce a consistent family of concrete
products. Client code works through the abstract factory
interface and is decoupled from all concrete product types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Abstract Factory creates entire FAMILIES of related objects
at once - guaranteed consistent because they all come from
the same factory.

**One analogy:**
> IKEA sells complete room collections (KALLAX collection,
> BILLY collection). Every piece in a collection matches
> every other piece in style and scale. Buying from the
> KALLAX Abstract Factory guarantees consistency - you can
> never accidentally buy a KALLAX shelf with a BILLY drawer
> unit that does not fit. The factory is the consistency
> guarantee.

**One insight:**
The key insight is that Abstract Factory makes WRONG
COMBINATIONS IMPOSSIBLE. You cannot mix Windows and macOS
widgets when the factory enforces family membership.
Consistency is architectural, not a code review convention.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All products created by one concrete factory are
   compatible with each other - they form a consistent family.
2. Client code references only abstract factory and abstract
   product interfaces - never concrete types.
3. Switching the entire product family means swapping one
   concrete factory - all downstream code is unchanged.

**DERIVED DESIGN:**
Five participants:
- **AbstractFactory**: interface declaring creation methods
  (one per product type in the family)
- **ConcreteFactoryA**, **ConcreteFactoryB**: implement all
  creation methods, return family-A or family-B products
- **AbstractProduct**: interface for each product type
  (Button, Checkbox, TextField)
- **ConcreteProductA1, A2, B1, B2**: specific products
  belonging to a family
- **Client**: works through AbstractFactory and AbstractProduct
  only; never names concrete types

**RELATIONSHIP TO FACTORY METHOD:**
Abstract Factory is composed of multiple Factory Methods.
Each creation method in an Abstract Factory IS a Factory
Method. Factory Method solves "how do I create ONE product
polymorphically?" Abstract Factory solves "how do I create
a FAMILY of products where they must be consistent?"

**TRADE-OFFS:**

**Gain:** Consistency guarantee (can't mix incompatible
products). Isolation of concrete classes. Easy platform/family
swap by changing one factory.

**Cost:** Supporting a new product type (e.g., adding TextField
to a Button+Checkbox factory) requires modifying the
AbstractFactory interface AND all ConcreteFactory implementations
- a significant change. Abstract Factory is therefore closed
for extension at the product-type level once defined.

---

### 🧪 Thought Experiment

**SETUP:**
A system must connect to cloud providers for storage, messaging,
and logging. In development: LocalStack (local mock). In
staging: AWS. In production: AWS multi-region. Each environment
uses a different set of concrete clients.

**WHAT HAPPENS WITHOUT ABSTRACT FACTORY:**
Every service class that needs a storage, messaging, or logging
client contains `if (env == "dev") new LocalStorage() else new
AwsS3Storage()`. A developer changes the dev configuration
but forgets one service - that service now uses the staging
messaging bus with local storage. Inconsistent environment
is a runtime debugging nightmare.

**WHAT HAPPENS WITH ABSTRACT FACTORY:**
`CloudFactory` declares `createStorage()`, `createMessaging()`,
`createLogger()`. `LocalStackFactory`, `AwsFactory`,
`AwsMultiRegionFactory` each implement all three creation
methods consistently. The entire environment is selected
once at startup by passing the correct factory. A developer
cannot accidentally mix environments because all three clients
come from one factory call.

**THE INSIGHT:**
Abstract Factory makes environment consistency a STARTUP
DECISION. Once the factory is selected, all subsequent
creation is automatically consistent. The cost is that adding
a new cloud service (e.g., CDN) requires adding `createCdn()`
to the abstract factory AND implementing it in all three
concrete factories.

---

### 🧠 Mental Model / Analogy

> Abstract Factory is a FURNITURE COLLECTION CATALOG. When you
> buy from the "Modern Collection," every piece - sofa, table,
> lamp - shares the same aesthetic. You cannot order a
> "Modern sofa" with a "Victorian table" from the same catalog
> page - the factory (catalog) only produces internally
> consistent combinations.

- "Collection catalog" = AbstractFactory
- "Modern Collection catalog" = ConcreteFactoryA
- "Victorian Collection catalog" = ConcreteFactoryB
- "Furniture type (sofa, table, lamp)" = AbstractProduct
- "Modern sofa, Modern table" = ConcreteProductA (family A)
- "You, the buyer" = Client

**Where this analogy breaks down:**
In real furniture shopping, you CAN mix collections if you
choose to. Abstract Factory makes mixing impossible in code -
it is a structural constraint, not a convention.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Abstract Factory creates matching sets of objects. If you want
a Windows-style application, use the Windows factory and you
get Windows buttons, Windows menus, Windows dialogs - they all
match because they came from the same factory.

**Level 2 - How to use it (junior developer):**
Declare an interface `GuiFactory` with methods `createButton()`,
`createCheckbox()`. Create `WindowsFactory` and `MacFactory`
that implement this interface. Wire the correct factory at
startup based on the OS. All GUI components are created
through `factory.createButton()`, never `new WindowsButton()`.

**Level 3 - How it works (mid-level engineer):**
Abstract Factory is a collection of Factory Methods grouped
into a family contract. Swapping the factory swaps the entire
product family atomically. The key constraint: adding a new
product type to the family requires updating the abstract
factory interface AND all concrete factories. This is Abstract
Factory's biggest weakness and should guide when to apply it:
use it when the product family is STABLE (fixed types) but
the number of families grows (new platforms, themes, providers).

**Level 4 - Why it was designed this way (senior/staff):**
Abstract Factory enforces the Liskov Substitution Principle at
the family level: any ConcreteFactory can substitute any other
ConcreteFactory, and all client code works correctly. This is
stronger than individual product type LSP - it is FAMILY LSP.
The pattern emerged from real problems in cross-platform GUI
toolkits where platform mixing produced visual bugs that were
impossible to detect without running the application on the
target platform. Making the wrong combination unrepresentable
in the type system was the design goal.

**Level 5 - Mastery (distinguished engineer):**
Abstract Factory in modern microservices architecture appears
as "provider factories" - an `InfrastructureFactory` interface
with `createEventBus()`, `createCache()`, `createObjectStore()`
methods, implemented by `LocalDevFactory` (all in-process),
`AwsFactory` (SQS, ElastiCache, S3), `GcpFactory` (Pub/Sub,
Memorystore, GCS). The pattern prevents environment inconsistency
at the architectural level. In Kotlin, factories are often
expressed as sealed interfaces with companion objects. In Java,
they are expressed as interfaces with Spring `@Profile`-specific
`@Configuration` classes as the ConcreteFactories - Spring
context profiles are Abstract Factory applied to the entire
application context.

---

### ⚙️ How It Works (Mechanism)

```
Abstract Factory Structure
┌───────────────────────────────────────────────────────┐
│  <<interface>>                                        │
│  GuiFactory                                           │
│  + createButton(): Button                             │
│  + createCheckbox(): Checkbox                         │
│            ▲                     ▲                    │
│  WindowsFactory          MacFactory                   │
│  createButton()          createButton()               │
│  → WindowsButton         → MacButton                  │
│  createCheckbox()        createCheckbox()             │
│  → WindowsCheckbox       → MacCheckbox                │
│                                                       │
│  <<interface>>     <<interface>>                      │
│  Button            Checkbox                           │
│  + click()         + check()                          │
│       ▲                  ▲                            │
│  WindowsButton    MacButton   WindowsCheckbox ...     │
│                                                       │
│  Client                                               │
│  - factory: GuiFactory    ← only knows interface      │
│  + render()                                           │
│    btn = factory.createButton()                       │
│    chk = factory.createCheckbox()                     │
│    // btn and chk are GUARANTEED to be same family    │
└───────────────────────────────────────────────────────┘
```

**Execution trace:**
1. Application startup reads configuration: Windows platform
2. Creates `WindowsFactory` and passes it to `Application`
3. `Application.render()` calls `factory.createButton()`:
   gets `WindowsButton`
4. `Application.render()` calls `factory.createCheckbox()`:
   gets `WindowsCheckbox`
5. Both objects used through abstract interfaces - no concrete
   names anywhere in Application
6. Swap to macOS: pass `MacFactory` at startup, step 3-5
   now produce `MacButton` and `MacCheckbox` - zero code change

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Startup determines family (OS, env, config)
  → Instantiate ConcreteFactory
  → Inject AbstractFactory into clients
  → Client calls factory.createX()
  → ConcreteFactory.createX() returns ConcreteProductX
  → Client uses ConcreteProductX via AbstractProduct
    interface
  → Family consistency guaranteed by construction
```

**FAILURE PATH:**
```
New product type needed mid-project (e.g., add Tooltip)
  → Must modify AbstractFactory interface
  → Must implement createTooltip() in ALL concrete
    factories
  → Existing concrete factory without implementation is
    incomplete (fails to compile)
  → High cost: changes propagate across all factories
```

**WHAT CHANGES AT SCALE:**
Abstract Factory itself is stateless - no scale concern.
The concern at scale: if factories create expensive objects
(database connections, HTTP clients), the factory method
should return pooled or cached instances. The factory then
transitions from a pure creator to a pool manager, and the
pattern complexity increases.

---

### 💻 Code Example

**Example 1 - Without Abstract Factory (the problem):**

```java
// BAD: Client code knows all concrete types + can mix families
class Application {
    void render(String os) {
        Button btn;
        Checkbox chk;
        if (os.equals("windows")) {
            btn = new WindowsButton();    // family A
            chk = new WindowsCheckbox();  // ok - family A
        } else {
            btn = new MacButton();         // family B
            chk = new WindowsCheckbox();  // BUG: mixing families
        }
        // No compile-time protection against family mixing
        btn.click(); chk.check();
    }
}
```

**Example 2 - Abstract Factory solution:**

```java
// GOOD: Abstract Factory enforces family consistency

interface Button { void click(); }
interface Checkbox { void check(); }

// Abstract Factory - the family contract
interface GuiFactory {
    Button createButton();
    Checkbox createCheckbox();
}

// Family A: Windows
class WindowsFactory implements GuiFactory {
    public Button createButton() {
        return new WindowsButton();
    }
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
}

// Family B: macOS
class MacFactory implements GuiFactory {
    public Button createButton() {
        return new MacButton();
    }
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
}

// Client: knows only interfaces, never concrete types
class Application {
    private final GuiFactory factory;

    Application(GuiFactory factory) {
        this.factory = factory; // family selected at startup
    }

    void render() {
        Button btn = factory.createButton();   // guaranteed family
        Checkbox chk = factory.createCheckbox(); // same family
        // IMPOSSIBLE to mix families here
        btn.click(); chk.check();
    }
}

// Startup: select family once
GuiFactory factory = isWindows()
    ? new WindowsFactory()
    : new MacFactory();
new Application(factory).render();
```

**Example 3 - Spring @Profile as Abstract Factory:**

```java
// GOOD: Spring Profile is Abstract Factory for infrastructure

// Abstract Factory (declared as interface)
interface InfrastructureFactory {
    EventBus createEventBus();
    ObjectStore createObjectStore();
}

// ConcreteFactory A: local development
@Configuration
@Profile("dev")
class LocalInfrastructureFactory implements InfrastructureFactory {
    @Bean public EventBus createEventBus() {
        return new InMemoryEventBus(); // local mock
    }
    @Bean public ObjectStore createObjectStore() {
        return new LocalFileStore();   // local filesystem
    }
}

// ConcreteFactory B: production
@Configuration
@Profile("prod")
class AwsInfrastructureFactory implements InfrastructureFactory {
    @Bean public EventBus createEventBus() {
        return new SqsEventBus();   // AWS SQS
    }
    @Bean public ObjectStore createObjectStore() {
        return new S3ObjectStore(); // AWS S3
    }
}
// Spring selects the profile at startup - the Abstract Factory.
// Service classes inject EventBus and ObjectStore interfaces.
// Guaranteed consistent environment: dev uses both local mocks.
```

**How to test/verify correctness:**
Test client code with a mock `GuiFactory` that returns
predictable mock products. The factory interface makes
injection trivial. Test each ConcreteFactory independently:
verify it returns the correct family type from each creation
method. Test that the Client's logic is independent of the
concrete factory used.

---

### ⚖️ Comparison Table

| Approach              | Family Consistency | Extensibility (new family) | Extensibility (new type) | Complexity |
| --------------------- | ------------------ | -------------------------- | ------------------------ | ---------- |
| **Abstract Factory**  | Compile-time       | Easy (new ConcreteFactory) | Hard (all factories)     | High       |
| Factory Method        | None               | Easy (new subclass)        | N/A (single product)     | Medium     |
| DI container (Spring) | Runtime (profiles) | Easy (@Profile)            | Medium (@Bean)           | Low        |
| Service Locator       | None               | Easy (register)            | Easy (register)          | Medium     |

**How to choose:** Use Abstract Factory when you have a STABLE
family of product types (adding new types is rare) but multiple
FAMILIES (new platforms, environments, themes). Use Factory
Method when you need one creation point to be extensible,
not an entire family. Use Spring @Profile for infrastructure
families - it IS Abstract Factory with framework support.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Abstract Factory and Factory Method are the same pattern | Factory Method creates ONE product polymorphically; Abstract Factory creates a FAMILY of related products with consistency guarantees |
| Abstract Factory makes adding new product types easy | This is its main weakness - adding a new type requires modifying the AbstractFactory interface and ALL ConcreteFactory implementations |
| Abstract Factory requires a formal interface/abstract class | Spring @Profile configuration classes are Abstract Factory implemented via framework conventions, not a formal interface |
| Abstract Factory is only for UI widgets | Any system with multiple consistent environments (dev/staging/prod), themes (dark/light), or providers (AWS/GCP) benefits from Abstract Factory |
| Concrete factories should be singletons | They can be, but it is not required - Abstract Factory does not mandate lifecycle; that is a separate concern |

---

### 🚨 Failure Modes & Diagnosis

**Family Consistency Broken by Missing Factory Usage**

**Symptom:**
A production bug report: "The application shows Windows-style
buttons but macOS-style checkboxes on some screens." Code
review reveals a developer directly instantiated `new
MacCheckbox()` in one rendering method rather than using
the factory.

**Root Cause:**
Abstract Factory consistency guarantee only holds when ALL
product creation goes through the factory. Direct `new`
invocations bypass the family constraint.

**Diagnostic Signal:**
Run grep for `new Windows` and `new Mac` in client code outside
factory classes. Any occurrence outside ConcreteFactory
implementations is a violation.

**Fix:**
```java
// BAD: bypasses factory guarantee
class SomeRenderer {
    Checkbox c = new MacCheckbox(); // direct instantiation
}

// GOOD: always use factory
class SomeRenderer {
    private final GuiFactory factory;
    SomeRenderer(GuiFactory factory) { this.factory = factory; }
    Checkbox c = factory.createCheckbox(); // family guaranteed
}
```

**Prevention:**
Code review checklist: "Does any class outside a ConcreteFactory
implementation use `new` with a concrete product class?" If
yes: it is a factory bypass. Make concrete product constructors
package-private to enforce this structurally.

---

**Abstract Factory Telescope: Too Many Product Types**

**Symptom:**
The `GuiFactory` interface has grown to 47 creation methods:
`createButton()`, `createPrimaryButton()`, `createDangerButton()`,
`createDisabledButton()`, `createIconButton()`, etc. Every
concrete factory must implement all 47 methods. When a designer
requests a new button variant, every factory (Windows, Mac,
Linux, Mobile) must be updated before the feature ships.

**Root Cause:**
Abstract Factory applied at too fine a granularity. Button
variants are not separate product TYPES - they are
parameterized variants of one product type. Factory Method
with parameters (or Builder) is the correct pattern.

**Diagnostic Signal:**
Count creation methods in the AbstractFactory. If >10, or if
multiple methods differ only by a single parameter
(size, color, state), the factory is over-specified.

**Fix:**
```java
// BAD: separate factory method per button variant
interface GuiFactory {
    Button createPrimaryButton();
    Button createDangerButton();
    Button createDisabledButton();
    // ... 44 more methods
}

// GOOD: parameterized factory method
interface GuiFactory {
    Button createButton(ButtonStyle style);
    Checkbox createCheckbox();
}
enum ButtonStyle { PRIMARY, DANGER, DISABLED, ICON }
```

**Prevention:**
Abstract Factory product types should correspond to
semantically distinct UI/domain concepts, not visual variants.
Visual parameterization belongs in the product's constructor
or a Builder, not in separate factory methods.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Factory Method` - the simpler single-product factory;
  Abstract Factory IS multiple Factory Methods grouped into
  a family contract; understand Factory Method first

**Builds On This (learn these next):**
- `Dependency Injection Pattern` - Abstract Factory through
  DI containers: Spring @Profile provides the same family
  consistency with framework support
- `Bridge` - frequently combined: Abstract Factory creates
  families of implementations; Bridge uses those implementations
  via abstraction-implementation separation

**Alternatives / Comparisons:**
- `Builder` - creates a SINGLE complex object step-by-step;
  Abstract Factory creates multiple simple objects from a
  consistent family; both are Creational but solve different
  problems
- `Factory Method` - single product creation; Abstract Factory
  extends this to families

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Interface for creating FAMILIES of       │
│              │ related objects - guaranteed consistent  │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Mixing incompatible product types from   │
│ SOLVES       │ different families (Windows + Mac widgets│
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Consistency is structural - wrong family │
│              │ combinations are impossible by design    │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Multiple families exist; product types   │
│              │ within each family must be consistent    │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Only one family exists, or adding new    │
│              │ product types is frequent                │
├──────────────┼──────────────────────────────────────────┤
│ WEAKNESS     │ Adding a new product type propagates to  │
│              │ ALL concrete factory implementations     │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Family consistency vs product-type       │
│              │ extensibility                            │
├──────────────┼──────────────────────────────────────────┤
│ MODERN EXPR. │ Spring @Profile configuration classes    │
│              │ are Abstract Factory for infrastructure  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Factory Method → Builder → DI Pattern    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Abstract Factory creates FAMILIES - all products from one
   factory are guaranteed compatible; mixing families is
   architecturally impossible, not just a convention
2. Its weakness is adding new PRODUCT TYPES - this requires
   changing the abstract interface and ALL implementations;
   use it when the family is stable but families multiply
3. Spring `@Profile` configuration classes ARE Abstract Factory
   applied to the entire application infrastructure; every
   team using Spring profiles is already using this pattern

**Interview one-liner:**
"Abstract Factory provides one interface for creating a family
of related objects, ensuring consistency by making wrong
combinations structurally impossible. Spring @Profile is the
most common modern expression: the profile selects the factory
(LocalStack vs AWS), all created beans are guaranteed to be
from the same environment family."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a set of objects MUST be used together consistently,
group their creation behind ONE interface. The factory
becomes the consistency contract - making wrong combinations
unrepresentable is more reliable than any code review or
convention.

**Where else this pattern appears:**
- **Test doubles** - TestContainers vs local mocks vs cloud
  resources: a TestFactory interface selects the entire test
  infrastructure family; integration tests use TestContainers
  factory, unit tests use in-memory mock factory
- **Skinning/theming engines** - dark mode vs light mode vs
  high-contrast: each is a factory that creates a consistent
  set of colors, fonts, and icons; switching themes is
  switching factories
- **Multi-tenant SaaS** - different tenants may use different
  storage backends, different billing providers, different
  notification channels; a TenantFactory creates the correct
  infrastructure family for each tenant

**Industry applications:**
- **JDBC** - `java.sql.Connection` is an Abstract Factory
  for `Statement`, `PreparedStatement`, `CallableStatement`.
  The concrete driver (PostgreSQL driver, MySQL driver) is
  the ConcreteFactory. `DriverManager.getConnection()` selects
  the factory; all SQL objects produced are consistent with
  that database dialect
- **Avalon/Plexus IoC** - early Java IoC containers used
  Abstract Factory explicitly for component family creation
  before Spring's annotation-based model became dominant

---

### 💡 The Surprising Truth

JDBC has been an Abstract Factory since Java 1.1 - yet most
Java developers have never recognised it. `java.sql.Connection`
is the AbstractFactory: its methods (`createStatement()`,
`prepareStatement()`, `prepareCall()`) are the factory
methods for the SQL product family. The concrete `Connection`
returned by `DriverManager.getConnection("jdbc:postgresql://...")`
is a `PostgresConnection` (ConcreteFactory). It creates
`PostgresPreparedStatement` objects (ConcreteProducts) that
are guaranteed consistent with the PostgreSQL dialect. You
cannot create a `PostgresPreparedStatement` using a MySQL
connection - family consistency by construction. The most
widely-used Java API in enterprise history has been
implementing Abstract Factory for 25+ years invisibly.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Describe why Abstract Factory makes wrong family
   combinations structurally impossible while a direct `new`
   approach makes them merely conventionally discouraged
2. [DISTINGUISH] State the one key difference between Factory
   Method and Abstract Factory - and give one real library
   example of each
3. [IDENTIFY WEAKNESS] Explain why Abstract Factory is CLOSED
   for adding new product types - and describe what changes
   are required when a new type must be added
4. [RECOGNIZE] Identify that JDBC `java.sql.Connection` is
   an Abstract Factory and name the AbstractFactory, the
   creation methods, and the product family it creates
5. [BUILD] Design an Abstract Factory for cloud infrastructure
   (EventBus + ObjectStore + Cache) with three ConcreteFactories
   (LocalDev, AWS, GCP) and explain what prevents environment
   mixing in the client code

---

### 🧠 Think About This Before We Continue

**Q1.** JDBC `java.sql.Connection` is an Abstract Factory.
But `Connection` is also the product of `DriverManager
.getConnection()`. So `Connection` is simultaneously a
ConcreteFactory AND a Product of a higher-level factory.
What pattern does this reveal about JDBC's layered design?
How does `DriverManager` itself fit into the Abstract Factory
picture?

*Hint: DriverManager is a registry/service locator that
returns the correct ConcreteFactory (Connection). The
Connection (ConcreteFactory) then creates the SQL product
family. This is Abstract Factory NESTED inside a registry.
The two-layer design separates the concern of "which driver?"
(DriverManager) from "which SQL object type?" (Connection).*

**Q2.** A team argues: "We should replace our `GuiFactory`
Abstract Factory with a Spring @Bean setup - it achieves the
same consistency without the ceremony." Evaluate this argument:
what family-consistency guarantee does the abstract interface
provide that Spring @Bean alone does NOT provide? When does the
argument hold and when does it break?

*Hint: Abstract Factory with a Java interface gives compile-time
guarantee: if WindowsFactory exists and implements GuiFactory,
you KNOW it has createButton() and createCheckbox(). A Spring
@Configuration class without an interface can omit a @Bean
method and you only find out at runtime. The argument holds
when the team uses @Profile with a common interface and tests
each profile; it breaks when factories grow independently
without interface enforcement.*

**Q3.** Your cloud infrastructure factory has grown to 15
creation methods (EventBus, ObjectStore, Cache, DNS, CDN,
LoadBalancer, ...). Adding a new cloud provider (OCI, Alibaba)
requires implementing all 15 methods. The team starts "faking"
methods with `throw new UnsupportedOperationException()`.
Design an evolution of this Abstract Factory that handles
optional product support without requiring implementation of
all methods - maintaining family consistency for the methods
that are implemented.

*Hint: Interface Segregation - split the monolith AbstractFactory
into smaller family interfaces: CoreFactory (EventBus, ObjectStore),
NetworkingFactory (CDN, LoadBalancer). A provider implements
the interfaces it supports. Client code depends only on the
factory interface it needs. A FactoryCapabilities registry
lets clients query which interfaces a given provider implements.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the main structural difference between
Factory Method and Abstract Factory?**

*Why they ask:* This is the most common Creational pattern
confusion; tests vocabulary precision and structural understanding.

*Strong answer includes:*
- Factory Method: ONE abstract creation method, ONE product type,
  solved via inheritance - subclass overrides the method
- Abstract Factory: MULTIPLE creation methods grouped in an
  interface, MULTIPLE related product types forming a family,
  solved via composition - client holds a reference to the factory
- Factory Method = "one virtual constructor in a class"
- Abstract Factory = "a complete family catalog interface"
- Structural relationship: Abstract Factory IS multiple
  Factory Methods composed into a consistency contract

**Q2: Why would you choose Abstract Factory over simply
using Spring @Profile and @Bean for environment-specific
infrastructure?**

*Why they ask:* Tests whether the candidate understands the
type-safety and contract enforcement benefit, not just the
pattern names.

*Strong answer includes:*
- Spring @Profile without an interface: no compile-time
  guarantee that all environments provide the same beans;
  missing beans cause runtime failures, not compilation errors
- Abstract Factory with a Java interface: the compiler enforces
  that every ConcreteFactory implements ALL product creation
  methods; missing implementation = compilation error
- Best practice: use both - implement the Abstract Factory
  interface AND use @Profile/@Configuration to select the
  ConcreteFactory; get compile-time safety AND Spring wiring
- Trade-off: the interface adds ceremony; for small teams with
  high test coverage, @Profile alone may be sufficient

**Q3: JDBC has been using Abstract Factory since Java 1.1.
Describe the Abstract Factory structure in JDBC and how it
prevents SQL dialect inconsistency.**

*Why they ask:* Tests whether the candidate can recognise
Abstract Factory in production code outside textbook examples.

*Strong answer includes:*
- AbstractFactory: `java.sql.Connection` (the interface)
- ConcreteFactories: `PostgresConnection`, `MySqlConnection`
  (driver-specific implementations of Connection)
- AbstractProducts: `Statement`, `PreparedStatement`,
  `CallableStatement`
- ConcreteProducts: `PostgresPreparedStatement`, etc.
- Family consistency: all objects created from a
  PostgresConnection use PostgreSQL syntax; you cannot mix
  a MySQL-dialect PreparedStatement with a PostgreSQL connection
- Family selection: `DriverManager.getConnection(url)` selects
  the ConcreteFactory based on the JDBC URL

