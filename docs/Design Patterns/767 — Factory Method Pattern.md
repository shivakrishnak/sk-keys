---
layout: default
title: "Factory Method Pattern"
parent: "Design Patterns"
nav_order: 767
permalink: /design-patterns/factory-method-pattern/
number: "767"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, SOLID Principles, Polymorphism"
used_by: "Object creation, Framework design, Plugin Architecture, OCP"
tags: #intermediate, #design-patterns, #creational, #oop, #polymorphism
---

# 767 — Factory Method Pattern

`#intermediate` `#design-patterns` `#creational` `#oop` `#polymorphism`

⚡ TL;DR — **Factory Method** defines an interface for creating objects but lets subclasses decide which class to instantiate — decoupling the object creation logic from the code that uses the created objects, enabling subclasses to override the type of object that will be created.

| #767 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, SOLID Principles, Polymorphism | |
| **Used by:** | Object creation, Framework design, Plugin Architecture, OCP | |

---

### 📘 Textbook Definition

**Factory Method** (GoF, 1994): a creational design pattern that defines an interface (abstract method) for creating an object, but defers the instantiation to subclasses. Also called "Virtual Constructor." The creator class declares a factory method; subclasses override it to return instances of different concrete classes. This lets the creator work with objects through their interface without knowing their concrete type. Distinguished from: (1) **Simple Factory** — a static method that creates objects based on a parameter (not GoF, not a full Factory Method); (2) **Abstract Factory** — creates families of related objects (multiple factory methods together). GoF intent: "Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses."

---

### 🟢 Simple Definition (Easy)

A pizza franchise. The parent company (creator) defines: "We make pizza" — but HOW the pizza is made (which dough, which sauce, which toppings) is decided by each franchise location (subclass). New York store makes NY-style pizza. Chicago store makes deep-dish. The parent company's process (`orderPizza()`) is the same for both. The CREATION of the pizza is defined in each store (factory method overridden in each subclass).

---

### 🔵 Simple Definition (Elaborated)

A logging framework: abstract `Logger` class with factory method `createAppender()`. Subclass `FileLogger` overrides `createAppender()` to return `FileAppender`. Subclass `CloudLogger` overrides it to return `CloudAppender`. The base class uses `createAppender()` to get the appender — it doesn't know or care which concrete type. You can add `DatabaseLogger` that returns `DatabaseAppender` without touching the base class. The base class is the "template" — subclasses customize via the factory method.

---

### 🔩 First Principles Explanation

**Factory Method structure and how it achieves OCP:**

```
THE PROBLEM:

  // Without Factory Method — creator hardcoded to concrete type:
  class ReportGenerator {
      Report generate(ReportType type) {
          Report report;
          if (type == PDF) {
              report = new PdfReport();        // hardcoded
          } else if (type == EXCEL) {
              report = new ExcelReport();      // hardcoded
          } else if (type == HTML) {
              report = new HtmlReport();       // hardcoded
          }
          report.addData(fetchData());
          report.format();
          return report;
      }
  }
  // Add CSV: modify ReportGenerator (OCP violated).
  
FACTORY METHOD SOLUTION:

  // CREATOR (abstract — defines factory method):
  abstract class ReportGenerator {
      // Factory method — creates the right type of report:
      protected abstract Report createReport();  // ← Factory Method
      
      // Template method uses factory method (doesn't know concrete type):
      public Report generate() {
          Report report = createReport();  // Polymorphic creation
          report.addData(fetchData());
          report.format();
          return report;
      }
  }
  
  // CONCRETE CREATORS (subclasses override factory method):
  class PdfReportGenerator extends ReportGenerator {
      protected Report createReport() { return new PdfReport(); }
  }
  
  class ExcelReportGenerator extends ReportGenerator {
      protected Report createReport() { return new ExcelReport(); }
  }
  
  class CsvReportGenerator extends ReportGenerator {
      protected Report createReport() { return new CsvReport(); }
  }
  
  // Add new type: add new subclass. ReportGenerator: ZERO changes. OCP.
  
  // PRODUCT HIERARCHY:
  interface Report {
      void addData(Data data);
      void format();
  }
  class PdfReport implements Report { ... }
  class ExcelReport implements Report { ... }
  class CsvReport implements Report { ... }
  
FACTORY METHOD VARIANTS:

  1. PARAMETERIZED FACTORY METHOD:
  
     // Factory method with parameter to decide what to create:
     abstract class Transport {
         abstract Vehicle createVehicle(int capacity);
         
         void deliver(Cargo cargo, int capacity) {
             Vehicle v = createVehicle(capacity);
             v.load(cargo);
             v.drive();
         }
     }
     
  2. STATIC FACTORY METHOD (NOT the GoF pattern — but widely used):
  
     // A static method that creates objects — often called "Factory Method" colloquially:
     class Money {
         static Money of(BigDecimal amount, Currency currency) { return new Money(amount, currency); }
         static Money zero(Currency currency) { return new Money(BigDecimal.ZERO, currency); }
         static Money parse(String expression) { ... }
     }
     
     // These are STATIC FACTORY METHODS (Joshua Bloch, Effective Java):
     // - Can have descriptive names
     // - Can return cached/shared instances
     // - Can return subtypes
     // Not the same as GoF Factory Method, but frequently called that.
     
  3. FACTORY METHOD IN INTERFACES (Java 8+):
  
     interface ButtonFactory {
         Button createButton();
         
         static ButtonFactory forPlatform(Platform p) {
             return switch (p) {
                 case WINDOWS -> new WindowsButtonFactory();
                 case MAC     -> new MacButtonFactory();
             };
         }
     }
     
FACTORY METHOD vs. SIMPLE FACTORY vs. ABSTRACT FACTORY:

  Simple Factory:    One class, one static method, switch/if to decide type.
                     Not a GoF pattern. Centralizes creation but violates OCP.
                     
  Factory Method:    Abstract method in base class. Subclass overrides.
                     Achieves OCP through inheritance/polymorphism.
                     
  Abstract Factory:  Interface with MULTIPLE factory methods.
                     Creates FAMILIES of related objects (Button + Dialog + Panel).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Factory Method:
- Add a new product type: modify the creator class (OCP violation)
- Creator tightly coupled to all concrete product types via if/switch

WITH Factory Method:
→ Add new product type: add new subclass, override factory method, zero changes to creator
→ Creator works through product interface — never knows concrete types

---

### 🧠 Mental Model / Analogy

> A cookie-cutter factory. The factory machine (creator) runs the same process: heat dough, press cutter, bake. The CUTTER (factory method) is swappable: star-shaped, round, snowflake. You don't modify the machine to make snowflake cookies — you swap the cutter. The machine is the template; the cutter is the factory method; each specific cutter is a subclass overriding the cutter shape.

"Factory machine process (heat, press, bake)" = creator class's template logic
"Cutter shape" = factory method (createCookie())
"Star cutter / round cutter" = concrete creator subclasses overriding factory method
"Swap cutter, not the machine" = add new subclass, don't modify creator

---

### ⚙️ How It Works (Mechanism)

```
FACTORY METHOD STRUCTURE:

  Creator (abstract)                    Product (interface/abstract)
  ─────────────────                     ──────────────────────────────
  +createProduct(): Product ← FM        +use(): void
  +anOperation()
      Product p = createProduct()
      p.use()
      
  ConcreteCreatorA                      ConcreteProductA
  ───────────────                       ────────────────
  +createProduct(): Product             +use(): void
      → new ConcreteProductA()
      
  ConcreteCreatorB                      ConcreteProductB
  ───────────────                       ────────────────
  +createProduct(): Product             +use(): void
      → new ConcreteProductB()
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to create objects without hardcoding concrete types in creator
        │
        ▼
Factory Method Pattern ◄──── (you are here)
(abstract creation method overridden by subclasses)
        │
        ├── Abstract Factory: multiple factory methods for families of related objects
        ├── Template Method: Factory Method is often used inside Template Method patterns
        ├── Open/Closed Principle: add new product type via new subclass, not modification
        └── Prototype: alternative creational pattern (copy vs. subclass)
```

---

### 💻 Code Example

```java
// PRODUCT:
interface Parser {
    Document parse(String input);
}

class JsonDocument implements Document { ... }
class XmlDocument implements Document { ... }

// CONCRETE PRODUCTS:
class JsonParser implements Parser {
    public Document parse(String input) { return JsonParser.parse(input); }
}
class XmlParser implements Parser {
    public Document parse(String input) { return XmlParser.parse(input); }
}

// CREATOR (abstract — uses factory method):
abstract class DataProcessor {
    protected abstract Parser createParser();  // ← Factory Method
    
    public ProcessedData process(String raw) {
        Parser parser = createParser();        // Polymorphic — doesn't know concrete type
        Document doc = parser.parse(raw);
        return transform(doc);
    }
    
    private ProcessedData transform(Document doc) { ... }
}

// CONCRETE CREATORS (override factory method):
class JsonDataProcessor extends DataProcessor {
    protected Parser createParser() { return new JsonParser(); }
}

class XmlDataProcessor extends DataProcessor {
    protected Parser createParser() { return new XmlParser(); }
}

// Adding YAML support: add YamlParser + YamlDataProcessor. DataProcessor: zero changes.
DataProcessor processor = new YamlDataProcessor();
ProcessedData result = processor.process(yamlInput);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Static Factory Methods (like `Money.of()`) are Factory Method pattern | Static factory methods are a Java idiom (Bloch's Effective Java Item 1) and are often colloquially called "factory methods," but they are NOT the GoF Factory Method pattern. GoF Factory Method: abstract/overridable method in a class hierarchy. Static factory: a static method on a class. Both create objects but serve different purposes and have different structure |
| Factory Method requires inheritance | The classic GoF Factory Method uses inheritance (subclass overrides the factory method). However, a similar decoupling can be achieved with interfaces and composition (inject a factory as a strategy). The core idea — separate creation from use — can be implemented without classic inheritance in languages with first-class functions or interfaces |
| Factory Method and Abstract Factory are interchangeable | Factory Method: single factory method, typically in a class hierarchy. Creates ONE type of product. Abstract Factory: an interface with MULTIPLE factory methods, creating a FAMILY of related products. Abstract Factory often USES Factory Methods in its implementations |

---

### 🔥 Pitfalls in Production

**Proliferation of subclasses for each variant:**

```java
// ANTI-PATTERN: Factory Method leading to class explosion:
// Every combination requires a new subclass:
abstract class ReportGenerator { abstract Report createReport(); }

class PdfEnglishReportGenerator extends ReportGenerator { ... }
class PdfFrenchReportGenerator  extends ReportGenerator { ... }
class ExcelEnglishReportGenerator extends ReportGenerator { ... }
class ExcelFrenchReportGenerator  extends ReportGenerator { ... }
// Add Spanish: 2 more classes. Add CSV: 3 more. 12 subclasses for 3 formats × 4 languages.

// FIX: Use strategy/composition instead of inheritance:
class ReportGenerator {
    private final ReportFormat format;
    private final Language language;
    
    ReportGenerator(ReportFormat format, Language language) {
        this.format = format;
        this.language = language;
    }
    
    Report generate() {
        Report report = format.createReport();  // Factory Method replaced by Strategy
        report.translate(language);
        return report;
    }
}
// Add Spanish: new Language("Spanish"). No new subclass.
// Add CSV: new CsvFormat(). No new subclass.
```

---

### 🔗 Related Keywords

- `Abstract Factory` — multiple factory methods creating families of objects
- `Template Method` — Factory Method is often part of a Template Method structure
- `Strategy Pattern` — alternative: inject a factory as a strategy object (composition over inheritance)
- `Open/Closed Principle` — Factory Method enables adding new products without modifying creator
- `Builder Pattern` — alternative creational pattern for complex object construction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Abstract creation method; subclass decides│
│              │ what to create. Creator works through     │
│              │ product interface — never concrete type.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Framework needs to create objects but     │
│              │ wants subclasses to control the type;     │
│              │ adding new product types without changing │
│              │ creator code                              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one concrete product type (no need  │
│              │ for polymorphism); leads to class explosion│
│              │ with many dimensions of variation        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cookie-cutter machine: same process,     │
│              │  swap the cutter (factory method) to make │
│              │  star or snowflake without changing the  │
│              │  machine."                                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstract Factory → Builder Pattern →      │
│              │ Template Method → Strategy Pattern        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `FactoryBean<T>` interface is literally a Factory Method pattern in the framework. `getObject()` is the factory method that Spring calls to get the bean instance. How does this differ from a regular `@Bean` method? When would you use `FactoryBean` instead of `@Bean`? Give a concrete example (e.g., creating a proxy, or creating a complex object that requires a multi-step build process).

**Q2.** The GoF say Factory Method promotes "code to interfaces, not implementations." But if you have `class PdfReportGenerator extends ReportGenerator`, clients who instantiate `new PdfReportGenerator()` still know about the concrete creator. How does this affect the value of the Factory Method pattern? What pattern (Abstract Factory, Dependency Injection) would you combine with Factory Method to ensure clients ALSO don't know which concrete creator they're using?
