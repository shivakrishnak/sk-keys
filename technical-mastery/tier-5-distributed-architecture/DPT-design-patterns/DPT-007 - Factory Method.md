---
id: DPT-007
title: Factory Method
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-006
used_by: DPT-008, DPT-039
related: DPT-008, DPT-006, DPT-039
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
nav_order: 7
permalink: /technical-mastery/design-patterns/factory-method/
---

⚡ TL;DR - Factory Method defers the creation of an object to
subclasses, letting you use an object without knowing or naming
its concrete class - separating object creation from object use.

| #7 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-006 | |
| **Used by:** | DPT-008, DPT-039 | |
| **Related:** | DPT-008, DPT-006, DPT-039 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A framework needs to create objects, but the framework's authors
do not know in advance which concrete objects the framework's
users will need. Consider a UI framework that creates dialog
boxes: the framework's `Application` class needs to create a
`Dialog`, but the type of dialog (Windows dialog, Web dialog,
macOS dialog) is determined by the platform running the app.
The framework cannot hard-code `new WindowsDialog()` without
coupling itself to a specific platform.

**THE BREAKING POINT:**
The framework's code contains `if (platform == WINDOWS) new
WindowsDialog() else if (platform == WEB) new WebDialog()`.
Every time a new platform is added, the framework's core code
must be modified. The framework's core and the platform-specific
code are tightly coupled. Extending the framework requires
modifying the framework's internals - a violation of the
Open/Closed Principle.

**THE INVENTION MOMENT:**
This is exactly why Factory Method exists: define a method in
the framework that CREATES the object, but make that method
abstract so subclasses decide WHICH concrete type to create.
The framework uses the object through an interface without
naming the concrete class.

**EVOLUTION:**
Factory Method emerged from early OOP frameworks that needed
to define generic algorithms while deferring implementation
specifics to users. It is the pattern underlying most
"plug-in" and "extension point" frameworks. Java's
`Iterator` creation via `Collection.iterator()` is a
Factory Method - each concrete collection (ArrayList,
LinkedList, TreeSet) creates its own concrete Iterator
without the caller needing to know the type. Spring's
`FactoryBean<T>` is a direct Factory Method implementation
for bean creation.

---

### 📘 Textbook Definition

The **Factory Method** pattern is a Creational design pattern
that defines an interface for creating an object but lets
subclasses decide which class to instantiate. Factory Method
lets a class defer instantiation to its subclasses. The
"creator" class declares an abstract factory method that returns
an object of an abstract product type; concrete creator
subclasses override the factory method to return concrete
product instances.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Factory Method says "I need an object - but let my subclass
decide exactly which one."

**One analogy:**
> A staffing agency says "send me a skilled worker." The agency
> (the creator) calls the factory method "hire()." The specific
> branch office (the concrete creator subclass) decides whether
> to send a carpenter, electrician, or plumber. The company
> using the agency only knows it gets a skilled worker -
> it never knows which trade is coming.

**One insight:**
Factory Method's power is in INVERSION: the framework code
calls a method to get an object, and the user's code (the
subclass) decides what object is created. The framework stays
open for extension without modification. This is the Open/Closed
Principle in a single pattern.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The creator knows what to DO with the product but not WHICH
   specific product to create.
2. The product implements a known interface - the creator uses
   it through the interface only, never a concrete type.
3. The decision of which concrete type to create belongs to
   the concrete creator subclass, not the framework.

**DERIVED DESIGN:**
Four participants:
- **Product**: the abstract interface the creator works with
- **ConcreteProduct**: the specific type the concrete creator creates
- **Creator**: the class with the abstract `createProduct()` method
- **ConcreteCreator**: the subclass that overrides `createProduct()`
  to return a `ConcreteProduct`

The `Creator.execute()` method calls `createProduct()` to get
a `Product`, then uses it through the `Product` interface.
The creator never names the concrete type.

**THE TRADE-OFFS:**

**Gain:** Open/Closed: new product types are added by creating
new ConcreteCreator subclasses, zero modification to framework.
Decoupling: creator is coupled to `Product` interface only.

**Cost:** Every new product type requires a new ConcreteCreator
subclass. The class hierarchy grows with the product catalog.
For simple cases, a direct `if-else` or switch statement is
simpler with less overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The problem of creating objects without knowing
their type is fundamental to framework design. Factory Method
is the minimal correct solution.

**Accidental:** In Java 8+, the concrete creator's factory method
is often a lambda or method reference rather than a subclass
override. The pattern's intent is preserved; the class hierarchy
is replaced by a functional interface.

---

### 🧪 Thought Experiment

**SETUP:**
A logging framework must write log entries to different outputs:
console in development, cloud storage in staging, a message
queue in production. The core logging logic (format, timestamp,
level filtering) is the same regardless of output.

**WHAT HAPPENS WITHOUT FACTORY METHOD:**
The logging framework's core class does:
```
if (env == DEV) new ConsoleWriter()
else if (env == STAGING) new CloudWriter()
else new QueueWriter()
```
Adding a new target (database, Splunk, Elasticsearch) requires
modifying the framework core. Users of the framework cannot add
their own targets without forking the code.

**WHAT HAPPENS WITH FACTORY METHOD:**
The framework defines `createLogWriter()` as abstract in its
base Logger class. Concrete loggers (DevLogger, StagingLogger,
ProdLogger) override `createLogWriter()` to return their
specific writer. Adding Elasticsearch: create ElasticLogger,
override `createLogWriter()` to return ElasticWriter. Zero
changes to the framework core.

**THE INSIGHT:**
Factory Method moves the creation decision OUT of the framework
and INTO the user's extension point. The framework remains
stable; the product catalog grows through extension alone.

---

### 🧠 Mental Model / Analogy

> Factory Method is like a franchise contract. The franchise
> headquarters defines the menu (Product interface) and the
> cooking process (Creator's algorithm using the product).
> Each franchise outlet (ConcreteCreator) decides which
> ingredients supplier to use (which ConcreteProduct to create).
> The headquarters' recipe never names the specific supplier.

- "Franchise headquarters" - the abstract Creator class
- "Cooking process" - the template algorithm in Creator
- "Menu item" - the Product interface
- "Specific ingredient" - ConcreteProduct
- "Franchise outlet" - ConcreteCreator subclass

**Where this analogy breaks down:** Franchise contracts are
rigid; Factory Method overrides are entirely flexible. The
ConcreteCreator can return any implementation of Product,
including one that the framework authors never anticipated.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Factory Method is a way to say "make me an object, but let
a subclass decide which specific object." It separates asking
for an object from deciding which exact object to create.

**Level 2 - How to use it (junior developer):**
Declare an abstract method `createX()` in a base class.
The return type is an interface or abstract class. Subclasses
override `createX()` and return a specific type. The base class
uses only the interface. Call the factory method rather than
`new ConcreteProduct()` directly.

**Level 3 - How it works (mid-level engineer):**
Factory Method is the simplest of the Creational patterns.
It is a single abstract method whose return type is a product
interface. It is the building block of Abstract Factory (which
uses multiple factory methods for a family of products). In Java,
`Collection.iterator()` is the canonical example: ArrayList
creates `ArrayList.Itr`, TreeSet creates `TreeSet.Itr`, but
the for-each loop calls `iterator()` on the abstract interface
and never names the concrete iterator type.

**Level 4 - Why it was designed this way (senior/staff):**
Factory Method solves the Open/Closed Principle violation
for object creation specifically. The GoF presented it as
the "virtual constructor" concept from C++: a constructor cannot
be virtual, but a factory method can be overridden, giving the
same polymorphic behavior for object creation that virtual
methods give for object use. The pattern exists because
constructors are concrete - they must name the exact class.
Factory methods are polymorphic - they can be overridden to
return any subtype.

**Level 5 - Mastery (distinguished engineer):**
Factory Method in Java 8+ is most cleanly expressed as a
`Supplier<T>` function parameter or a method reference, not a
subclass override. This is the idiom-level expression of the
same pattern intent. `Supplier<Dialog> dialogFactory = config
.isWeb() ? WebDialog::new : WindowsDialog::new;` achieves
the same separation of creation from use without the class
hierarchy. Expert engineers reach for the functional idiom
for simple cases and the full class hierarchy only when the
concrete creator needs significant state or additional behavior
beyond the factory method itself.

---

### ⚙️ How It Works (Mechanism)

```
Factory Method Structure
┌─────────────────────────────────────────────────────┐
│  Creator (abstract)                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │  + createProduct(): Product  ← abstract     │   │
│  │  + execute(): void                          │   │
│  │    product = createProduct()  ← calls FM    │   │
│  │    product.use()              ← via iface   │   │
│  └─────────────────────────────────────────────┘   │
│            ▲               ▲                        │
│  ConcreteCreatorA  ConcreteCreatorB                 │
│  createProduct()   createProduct()                  │
│  → new ProductA()  → new ProductB()                 │
│                                                     │
│  Product (interface)                                │
│    + use(): void                                    │
│            ▲              ▲                         │
│      ProductA           ProductB                   │
│      implements         implements                  │
│      use()              use()                       │
└─────────────────────────────────────────────────────┘
```

**Execution trace:**
1. Caller creates `ConcreteCreatorA` (which IS-A Creator)
2. Caller calls `creatorA.execute()`
3. `execute()` internally calls `this.createProduct()`
4. `createProduct()` is overridden in ConcreteCreatorA - returns
   `new ProductA()`
5. `execute()` uses `product.use()` through the Product interface
6. `ConcreteCreatorA` is substituted by `ConcreteCreatorB`:
   same call to `execute()`, different product created, same
   product interface used - zero change to execute() code

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Caller selects ConcreteCreator (A or B)
  → Instantiates ConcreteCreator
  → Calls creator.execute()
  → execute() calls this.createProduct() ← YOU ARE HERE
  → ConcreteCreator.createProduct() returns ConcreteProduct
  → execute() uses product.doWork() via interface
  → Result returned to caller
```

**FAILURE PATH:**
```
createProduct() returns null
  → execute() calls null.doWork()
  → NullPointerException in execute()
  → Hard to trace: exception in Creator, bug in
    ConcreteCreator
```

**WHAT CHANGES AT SCALE:**
Factory Method is a class-level pattern; scale does not change
its behavior. However, if the factory method is called millions
of times, object allocation cost matters: consider pooling
products or using flyweight for stateless products returned
from the factory method.

---

### 💻 Code Example

**Example 1 - Framework without Factory Method (the problem):**

```java
// BAD: Framework coupled to concrete platform types
abstract class Application {
    public void buildUI() {
        Dialog dialog;
        // Coupled to specific platforms - OCP violation
        if (System.getProperty("os.name").contains("Win")) {
            dialog = new WindowsDialog();  // concrete name
        } else {
            dialog = new WebDialog();      // concrete name
        }
        dialog.render();
    }
}
```

**Example 2 - Factory Method solution:**

```java
// GOOD: Factory Method defers concrete type decision
abstract class Application {
    // Factory Method - abstract, subclass decides
    protected abstract Dialog createDialog();

    public void buildUI() {
        // Creator uses Product through interface only
        Dialog dialog = createDialog(); // no concrete name
        dialog.render();
    }
}

interface Dialog {
    void render();
    Button createButton(); // Dialog is also a creator
}

// ConcreteCreator A
class WindowsApplication extends Application {
    @Override
    protected Dialog createDialog() {
        return new WindowsDialog(); // only place naming concrete
    }
}

// ConcreteCreator B
class WebApplication extends Application {
    @Override
    protected Dialog createDialog() {
        return new WebDialog();
    }
}
// Adding macOS: new MacApplication extending Application,
// zero change to Application.buildUI()
```

**Example 3 - Java idiom: Supplier as Factory Method:**

```java
// GOOD: Java 8+ idiom for simple Factory Method cases
// Same pattern intent, no class hierarchy needed

class DialogFactory {
    // Factory Method expressed as a Supplier function
    static Dialog create(Supplier<Dialog> factory) {
        Dialog d = factory.get(); // calls the factory method
        d.initialize();
        return d;
    }
}

// Usage: inject the concrete creation decision as a lambda
Dialog d = DialogFactory.create(
    isWeb ? WebDialog::new : WindowsDialog::new
);
// The Supplier IS the ConcreteCreator - no subclass needed
```

**Example 4 - Java's own Factory Method (java.util):**

```java
// RECOGNITION: Collection.iterator() is a Factory Method
List<String> arrayList = new ArrayList<>();
List<String> linkedList = new LinkedList<>();

// Both return Iterator<String>, but:
// ArrayList.iterator() creates ArrayList.Itr (concrete)
// LinkedList.iterator() creates LinkedList.ListItr (concrete)
// The for-each loop only knows Iterator<String>
for (String s : arrayList) { /* uses Iterator without naming it */ }
for (String s : linkedList) { /* same call, different concrete */ }
```

**How to test/verify correctness:**
Test that the creator's `execute()` works correctly with each
concrete creator. Test that adding a new ConcreteCreator
produces the correct product behavior without modifying any
existing Creator or ConcreteCreator code. Use a mock product
to test the Creator's logic independently of any ConcreteCreator.

---

### ⚖️ Comparison Table

| Approach               | Coupling | Extensibility | Complexity | Best For                            |
| ---------------------- | -------- | ------------- | ---------- | ----------------------------------- |
| **Factory Method**     | Low      | High          | Medium     | Framework extension points          |
| Direct `new` statement | High     | None          | None       | Simple objects, no extension needed |
| Abstract Factory       | Low      | High          | High       | Families of related products        |
| Supplier / lambda      | Low      | High          | Low        | Simple factory, Java 8+             |
| Service Locator        | Low      | Medium        | Medium     | Avoid: testability problems         |

**How to choose:** Use Factory Method when you are writing a
framework and need to define a creation point that users will
override. Use Supplier/lambda when the factory logic is simple
(just `new`) and no ConcreteCreator needs state. Use Abstract
Factory when you need a family of related products to be
created consistently.

**Decision Tree:**
Do you need users to override which product is created? - Factory Method
Is it just `new ProductType()`? - Use Supplier<T> lambda
Do you need multiple related products from one factory? - Abstract Factory
Is the type known at compile time and won't change? - Use `new` directly

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Any method named "create" or "make" is a Factory Method | Factory Method requires polymorphism - the method must be overridable; a static factory method is not Factory Method pattern |
| Factory Method and Abstract Factory are the same | Factory Method creates one type; Abstract Factory creates a family of related types using multiple factory methods |
| Factory Method requires an abstract class | It can be implemented with an interface default method (Java 8+) or as a Supplier<T> parameter; the subclass override is the essence, not the abstract class |
| Factory Method prevents using `new` | ConcreteCreators use `new` internally; they just encapsulate the `new` call so the creator class does not |
| Factory Method is only for framework design | It applies anywhere the code that USES an object should not know WHICH object it uses |

---

### 🚨 Failure Modes & Diagnosis

**Static Factory Method Confusion**

**Symptom:**
A class has a static method named `create()` that the team
calls "the Factory Method." The method is not overridable,
is not defined in a base class, and returns a hard-coded
type. Team uses "Factory Method pattern" in design docs for
any method named `create*`.

**Root Cause:**
Confusion between "factory method" (any creation method) and
"Factory Method pattern" (the GoF polymorphic creation pattern).
Joshua Bloch popularised static factory methods in "Effective
Java" as an alternative to public constructors - these are
NOT the Factory Method pattern.

**Diagnostic Signal:**
Ask: "Is this method abstract (or overridable) in a base class?"
If no: it is a static factory method (a useful idiom, not the
GoF pattern). If yes: it is Factory Method pattern.

**Fix:**
Use correct terminology: "static factory method" for static
creation methods, "Factory Method pattern" for the GoF
polymorphic creation pattern. Update design documents to
distinguish the two.

**Prevention:**
Code review checklist item: when a design document mentions
"Factory Method pattern," verify that the implementation
includes a base class with an overridable creation method.

---

**ConcreteCreator Class Explosion**

**Symptom:**
A system with 15 product types has 15 ConcreteCreator subclasses,
each with trivial one-line factory methods that differ only in
the `new ProductN()` call. The class hierarchy is 15 files
deep with no meaningful logic in any ConcreteCreator beyond
the factory method.

**Root Cause:**
Factory Method is applied where Abstract Factory or a registry-
based approach would better suit the scale. For 15+ product
types with no additional ConcreteCreator logic, the subclass
hierarchy is ceremony.

**Diagnostic Signal:**
Count ConcreteCreators. If >5 and each contains only a one-line
factory method with no other logic, consider a registry pattern:
Map<ProductType, Supplier<Product>> registry - the same extensibility
with a fraction of the class count.

**Fix:**
Replace the class hierarchy with a registered factory map:
```java
Map<String, Supplier<Dialog>> registry = new HashMap<>();
registry.put("web", WebDialog::new);
registry.put("windows", WindowsDialog::new);
// Adding a new type: one registration, no new class
```

**Prevention:**
Apply Factory Method subclass hierarchy when ConcreteCreators
have significant additional behavior beyond the factory method.
Use a registry/map approach when the only difference between
ConcreteCreators is the `new` call.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - the vocabulary
  foundation
- `Singleton` - often used inside Abstract Factory; the simplest
  Creational pattern, providing the baseline for comparison

**Builds On This (learn these next):**
- `Abstract Factory` - Factory Method extended to families of
  products; uses multiple Factory Methods together
- `Dependency Injection Pattern` - the modern replacement for
  most Factory Method use cases in Spring-based code

**Alternatives / Comparisons:**
- `Builder` - another Creational pattern; where Factory Method
  creates in one step, Builder creates in multiple steps with
  a final build() call
- `Prototype` - another Creational alternative; instead of a
  factory method returning new instances, Prototype clones
  an existing instance

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Creational pattern: abstract creation    │
│              │ method overridden by subclasses          │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Framework must create objects without    │
│ SOLVES       │ knowing which concrete type to create    │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Creator uses Product via interface only; │
│              │ ConcreteCreator decides the actual type  │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ A base class needs to create objects but │
│              │ must let subclasses choose the type      │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Only one concrete type ever exists;     │
│              │ a Supplier lambda is simpler             │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Calling a static create() method "the   │
│              │ Factory Method pattern" - it is not      │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Extensibility vs class hierarchy growth  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "I need something - let my subclass      │
│              │  decide what something is"               │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstract Factory → Builder → DI Pattern  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Factory Method is defined on a base class as an ABSTRACT
   (overridable) method - a static `create()` method is not
   the GoF Factory Method pattern
2. The creator uses the product ONLY through its interface;
   the concrete creator is the only place that names the
   concrete product class
3. In Java 8+, a Supplier<T> parameter is the idiomatic
   expression of Factory Method for simple cases - same
   decoupling, no class hierarchy needed

**Interview one-liner:**
"Factory Method defines an abstract creation method in a base
class, letting subclasses decide which concrete type to
instantiate. The creator never names the concrete class - it
uses the product through an interface. Java's Collection
.iterator() is the canonical library example: each collection
creates its own concrete iterator type, but for-each loops
only know Iterator."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate WHAT you do with an object from WHICH object you get.
Any system where the consumer of a thing should not know the
concrete type of the thing benefits from this separation -
it is the inversion of control applied to object creation.

**Where else this pattern appears:**
- **Dependency injection containers** - the DI container IS
  a Factory Method implementation: it knows what interface
  to provide but lets configuration (the "ConcreteCreator")
  decide which concrete implementation to instantiate
- **Plugin architectures** - plugin loaders define a factory
  interface; each plugin registers its ConcreteCreator; the
  host application creates plugins through the interface
  without knowing which plugin is loaded
- **Cloud provider SDKs** - AWS, Azure, GCP SDKs define
  `createClient()` factory methods; the SDK's concrete
  implementation creates region-specific, credential-specific
  concrete clients; callers work through the interface

**Industry applications:**
- **ORM frameworks** - Hibernate's `SessionFactory.openSession()`
  is a Factory Method; the specific Session implementation
  depends on the configured database dialect without callers
  knowing the type
- **Logger frameworks** - SLF4J's `LoggerFactory.getLogger()`
  is a Factory Method: the concrete Logger implementation
  (Log4j, Logback, java.util.logging) is determined by the
  classpath configuration, not by callers

---

### 💡 The Surprising Truth

Java's standard library is full of Factory Method implementations
that most engineers do not recognise as GoF patterns. Every call
to `Collections.unmodifiableList()` is Factory Method: the caller
gets a List interface, but the concrete type is a non-public
inner class `UnmodifiableRandomAccessList` or `UnmodifiableList`
depending on the input - the caller never knows which. Every
call to `Path.of()` (Java 11) returns an OS-specific path
implementation. Java's NIO `Files.newInputStream()` returns
a concrete InputStream subtype determined by the file system
provider. The pattern is everywhere in the JDK - engineers just
do not recognise it because the method names do not always match
the textbook "createX()" convention.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Distinguish Factory Method pattern from a static
   factory method in one sentence, giving a concrete example
   of each from Java's standard library
2. [DEBUG] Given a framework class with a hard-coded `if-else`
   block that creates different concrete product types, identify
   that this is a Factory Method opportunity, and sketch the
   refactored design with correct participant names
3. [DECIDE] Determine whether to use the full Factory Method
   subclass hierarchy or a Supplier<T> lambda for a specific
   creation problem, stating the criterion for each choice
4. [BUILD] Implement Factory Method from memory for a notification
   sender: abstract base Notifier with abstract `createChannel()`
   method, EmailNotifier and SmsNotifier as ConcreteCreators,
   NotificationChannel as the Product interface
5. [EXTEND] Map Factory Method to Java's Collection.iterator()
   implementation: identify the Creator (Collection), the
   abstract factory method (iterator()), the ConcreteCreators
   (ArrayList, LinkedList), and the Product interface (Iterator)

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `Iterator` is created via a Factory Method
in each Collection implementation. Yet modern Java code
uses `Stream` instead of `Iterator` for most traversal.
Does Stream replace the Factory Method pattern in this
context, or does Stream itself use a Factory Method pattern
internally? Trace the Stream creation path from
`Collection.stream()` to understand which pattern governs
stream creation.

*Hint: `Collection.stream()` returns a `Stream<E>` - the
concrete type depends on the collection. Is this a Factory
Method? Look at `AbstractCollection.stream()` and `Spliterator`
- the stream creation delegates to `spliterator()`, which IS
a Factory Method. The pattern is still present, just
one layer deeper.*

**Q2.** A team proposes replacing a Factory Method class
hierarchy (15 ConcreteCreator subclasses) with a
`Map<String, Supplier<Product>>` registry. The senior
engineer says the registry loses type safety and the
subclass hierarchy provides compile-time verification.
Evaluate both arguments: when is the senior engineer right,
and when does the registry provide equivalent or better safety?

*Hint: Class hierarchy: adding a new product type requires
a new subclass - the compiler enforces the factory method
override. Registry: adding a new product type is a runtime
registration - no compile-time check that all types are
registered. But: GenericTypeSafe registry patterns (using
bounded wildcards) can recover type safety. When is the
runtime registration flexibility worth the safety trade-off?*

**Q3.** You need to implement a plugin architecture where
external JAR files can add new report types to a reporting
system. The host application only knows the ReportFactory
interface. Each plugin JAR provides its own ConcreteCreator.
Design the plugin registration mechanism: how does the host
discover plugins at runtime, how does it call the factory
method, and what happens when a plugin creates a broken
ConcreteProduct (exception in the factory method)?

*Hint: Java ServiceLoader is the standard mechanism for
plugin discovery - it IS a Factory Method registry at the
JAR level. What happens if a plugin's `createReport()` throws
a RuntimeException? How does the host handle partial plugin
loading failures while still working with the loaded plugins?*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Factory Method pattern
and a static factory method? Why does the distinction matter?**

*Why they ask:* This is the most common Factory Method
misconception; distinguishing them tests vocabulary precision.

*Strong answer includes:*
- Factory Method pattern: abstract method in a base class,
  overridden by subclasses, polymorphic - the GoF Creational
  pattern
- Static factory method: a static method on any class that
  constructs and returns an object, like `Integer.valueOf()`
  or `LocalDate.of()` - Joshua Bloch's "Effective Java" idiom
- The distinction matters because they solve different problems:
  Factory Method enables framework extension points; static
  factory methods enable name, caching, and type flexibility
  at the method level without polymorphism
- Mixing them up in design reviews produces architectural confusion

**Q2: Your notification service needs to send messages via
Email, SMS, or Push. New channels will be added quarterly.
Walk me through applying Factory Method pattern to this design.**

*Why they ask:* Tests whether pattern application is concrete
and correct, not just named.

*Strong answer includes:*
- Product interface: `NotificationChannel` with `send(Message)`
- ConcreteProducts: `EmailChannel`, `SmsChannel`, `PushChannel`
- Creator: abstract `NotificationService` with abstract
  `createChannel(): NotificationChannel`
- ConcreteCreators: `EmailNotificationService`,
  `SmsNotificationService`, `PushNotificationService`
- Adding a new channel (Slack): one new `NotificationChannel`
  implementation + one new `NotificationService` subclass,
  zero changes to `NotificationService`
- In Java 8+: consider `Supplier<NotificationChannel>` for
  simpler cases where ConcreteCreators have no additional state

**Q3: How does Java's Collection.iterator() method demonstrate
the Factory Method pattern in the standard library?**

*Why they ask:* Tests whether the candidate can recognise
patterns in real production code rather than just textbook examples.

*Strong answer includes:*
- Creator: `Collection<E>` interface or `AbstractCollection`
- Abstract factory method: `iterator(): Iterator<E>`
- ConcreteCreators: `ArrayList`, `LinkedList`, `TreeSet`, etc.
- Products: `ArrayList.Itr`, `LinkedList.ListItr`, etc.
- Consumer (for-each): only knows `Iterator<E>` - never the
  concrete iterator type
- Evidence that it IS Factory Method and not just any method:
  each ConcreteCreator returns a different Iterator subtype;
  the caller is decoupled from all concrete types

