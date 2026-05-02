---
layout: default
title: "Abstract Factory Pattern"
parent: "Design Patterns"
nav_order: 769
permalink: /design-patterns/abstract-factory-pattern/
number: "769"
category: Design Patterns
difficulty: ★★★
depends_on: "Factory Method Pattern, Object-Oriented Programming, SOLID Principles"
used_by: "Cross-platform UI, Theme engines, Database drivers, GUI frameworks"
tags: #advanced, #design-patterns, #creational, #oop, #polymorphism
---

# 769 — Abstract Factory Pattern

`#advanced` `#design-patterns` `#creational` `#oop` `#polymorphism`

⚡ TL;DR — **Abstract Factory** provides an interface for creating **families of related objects** without specifying concrete classes — like a UI factory that creates matching Windows-style (or Mac-style) buttons, checkboxes, and dialogs, ensuring all created components belong to the same consistent family.

| #769            | Category: Design Patterns                                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Factory Method Pattern, Object-Oriented Programming, SOLID Principles |                 |
| **Used by:**    | Cross-platform UI, Theme engines, Database drivers, GUI frameworks    |                 |

---

### 📘 Textbook Definition

**Abstract Factory** (GoF, 1994): a creational design pattern that provides an interface for creating families of related or dependent objects without specifying their concrete classes. The "factory of factories." Abstract Factory declares factory methods for each type of product in the family; each Concrete Factory implements these methods to produce a specific family of products. Key invariant: all products from one factory are compatible (belong to the same family). Contrasted with Factory Method: Factory Method uses subclassing to create ONE type of product; Abstract Factory uses composition to create MULTIPLE related types that must be consistent with each other. GoF intent: "Provide an interface for creating families of related or dependent objects without specifying their concrete classes."

---

### 🟢 Simple Definition (Easy)

A furniture store has two collections: Modern and Victorian. If you want Modern furniture, you get: Modern Chair, Modern Sofa, Modern Table — all matching. If you want Victorian furniture, you get: Victorian Chair, Victorian Sofa, Victorian Table — all matching. You can't accidentally get a Modern Chair with a Victorian Sofa. The "Modern Collection" and "Victorian Collection" are the abstract factories — each one creates a complete, consistent family of related products.

---

### 🔵 Simple Definition (Elaborated)

Cross-platform GUI framework. `GUIFactory` interface declares: `createButton()`, `createCheckbox()`, `createDialog()`. `WindowsFactory` implements all three to return Windows-style components. `MacFactory` implements all three to return Mac-style components. Your application code uses `GUIFactory` — never knows if it's Windows or Mac. The factory is chosen at startup based on the OS. All created components are guaranteed to be consistent because they all come from the same factory — no mixing of styles.

---

### 🔩 First Principles Explanation

**Why families of products need a factory that ensures consistency:**

```
THE PROBLEM — INCONSISTENCY WITHOUT ABSTRACT FACTORY:

  // Without Abstract Factory: mixing products from different families:
  Button  button   = new WindowsButton();   // Windows style
  Checkbox checkbox = new MacCheckbox();    // Mac style ← INCONSISTENT!
  Dialog  dialog   = new WindowsDialog();   // Windows style

  // Nothing in the type system prevents mixing. UI looks broken.

ABSTRACT FACTORY STRUCTURE:

  // 1. ABSTRACT PRODUCTS (interfaces for each product type):
  interface Button {
      void render();
      void onClick();
  }

  interface Checkbox {
      void render();
      boolean isChecked();
  }

  // 2. ABSTRACT FACTORY (interface declaring all factory methods):
  interface GUIFactory {
      Button   createButton();    // factory method for each product type
      Checkbox createCheckbox();
  }

  // 3. CONCRETE PRODUCTS for Family A (Windows):
  class WindowsButton implements Button {
      void render()  { System.out.println("Rendering Windows button [▣]"); }
      void onClick() { /* Windows click behavior */ }
  }

  class WindowsCheckbox implements Checkbox {
      void render()    { System.out.println("Rendering Windows checkbox [☑]"); }
      boolean isChecked() { return state; }
  }

  // 4. CONCRETE PRODUCTS for Family B (Mac):
  class MacButton   implements Button   { void render() { /* Mac button styling */ } ... }
  class MacCheckbox implements Checkbox { void render() { /* Mac checkbox styling */ } ... }

  // 5. CONCRETE FACTORIES (one per product family):
  class WindowsFactory implements GUIFactory {
      Button   createButton()   { return new WindowsButton(); }   // same family!
      Checkbox createCheckbox() { return new WindowsCheckbox(); } // same family!
  }

  class MacFactory implements GUIFactory {
      Button   createButton()   { return new MacButton(); }
      Checkbox createCheckbox() { return new MacCheckbox(); }
  }

  // 6. CLIENT CODE (works with factory interface — never knows family):
  class Application {
      private final Button   button;
      private final Checkbox checkbox;

      Application(GUIFactory factory) {      // inject factory (DI)
          this.button   = factory.createButton();    // guaranteed consistent
          this.checkbox = factory.createCheckbox();  // same family as button
      }

      void render() { button.render(); checkbox.render(); }
  }

  // STARTUP:
  GUIFactory factory = detectOS() == WINDOWS
      ? new WindowsFactory()
      : new MacFactory();
  Application app = new Application(factory);  // inject factory

ADDING A NEW FAMILY (Linux) — OCP:

  class LinuxButton   implements Button   { ... }
  class LinuxCheckbox implements Checkbox { ... }
  class LinuxFactory  implements GUIFactory {
      Button   createButton()   { return new LinuxButton(); }
      Checkbox createCheckbox() { return new LinuxCheckbox(); }
  }
  // GUIFactory interface: ZERO changes. Application code: ZERO changes.
  // Only add: 3 new classes.

ADDING A NEW PRODUCT TYPE (Dialog) — OPEN/CLOSED VIOLATION:

  // Adding Dialog to GUIFactory forces ALL existing concrete factories to implement it:
  interface GUIFactory {
      Button   createButton();
      Checkbox createCheckbox();
      Dialog   createDialog();  // ← NEW: WindowsFactory, MacFactory, LinuxFactory ALL change!
  }
  // Abstract Factory is NOT OCP for new product types — only for new families.
  // This is the key tradeoff of the pattern.

ABSTRACT FACTORY IN JAVA ECOSYSTEM:

  // javax.xml.parsers.DocumentBuilderFactory — creates XML parsers:
  DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
  DocumentBuilder builder = factory.newDocumentBuilder();
  Document doc = builder.newDocument();

  // java.sql (JDBC) — Connection, Statement, ResultSet are products from a factory:
  DataSource dataSource = ...;  // Abstract Factory
  Connection conn  = dataSource.getConnection();   // product 1
  Statement  stmt  = conn.createStatement();        // product 2
  ResultSet  rs    = stmt.executeQuery("...");      // product 3
  // MySQL DataSource creates MySQL Connection/Statement/ResultSet (consistent family)
  // PostgreSQL DataSource creates PostgreSQL-compatible family
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Abstract Factory:

- Code creates products from different families: `new WindowsButton()` + `new MacCheckbox()` — inconsistent UI
- Adding a new family requires modifying all the if/switch creation logic across the codebase

WITH Abstract Factory:
→ Inject one factory; all products are created from it — guaranteed family consistency
→ Add new family: add concrete factory class + concrete product classes. Client code: zero changes

---

### 🧠 Mental Model / Analogy

> An IKEA collection. IKEA sells "KALLAX" and "BILLY" collections. If you furnish a room entirely from KALLAX, everything matches. If you mix KALLAX shelves with BILLY desks — they clash. IKEA as a brand is the Abstract Factory. KALLAX collection and BILLY collection are Concrete Factories. The individual items (shelf, desk, bookcase) are products. Choosing "shop in KALLAX collection" is choosing which concrete factory to use — after that, every item you get is KALLAX.

"IKEA brand" = GUIFactory (abstract interface)
"KALLAX collection" = WindowsFactory (concrete factory)
"BILLY collection" = MacFactory (concrete factory)
"shelf/desk/bookcase" = Button/Checkbox/Dialog (product families)
"room furnished entirely from KALLAX" = all products from one factory (consistent family)

---

### ⚙️ How It Works (Mechanism)

```
ABSTRACT FACTORY STRUCTURE:

  «interface»          «interface»         «interface»
  GUIFactory           Button              Checkbox
  ─────────────        ──────────          ──────────
  createButton()       render()            render()
  createCheckbox()     onClick()           isChecked()
       ▲                   ▲                   ▲
       │            ┌──────┴──────┐    ┌───────┴───────┐
  WindowsFactory  WinButton   MacButton  WinCheckbox  MacCheckbox
  MacFactory

  Client uses GUIFactory interface only.
  Concrete factory determines entire product family.
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to create families of related objects with guaranteed consistency
        │
        ▼
Abstract Factory Pattern ◄──── (you are here)
(interface with multiple factory methods; one per product in the family)
        │
        ├── Factory Method: Abstract Factory often USES Factory Methods for each product
        ├── Dependency Injection: inject the abstract factory into client code
        ├── Bridge Pattern: both separate abstraction from implementation
        └── Strategy Pattern: concrete factory = strategy for creating a product family
```

---

### 💻 Code Example

```java
// Database abstraction with Abstract Factory:
// Products:
interface Connection { PreparedStatement prepareStatement(String sql); void close(); }
interface Transaction { void commit(); void rollback(); }

// Abstract Factory:
interface DatabaseFactory {
    Connection  createConnection(String url);
    Transaction createTransaction(Connection conn);
}

// Concrete products — MySQL:
class MySqlConnection  implements Connection  { ... }
class MySqlTransaction implements Transaction { ... }

// Concrete products — PostgreSQL:
class PostgresConnection  implements Connection  { ... }
class PostgresTransaction implements Transaction { ... }

// Concrete factories:
class MySqlFactory implements DatabaseFactory {
    public Connection  createConnection(String url)         { return new MySqlConnection(url); }
    public Transaction createTransaction(Connection conn)   { return new MySqlTransaction(conn); }
}

class PostgresFactory implements DatabaseFactory {
    public Connection  createConnection(String url)         { return new PostgresConnection(url); }
    public Transaction createTransaction(Connection conn)   { return new PostgresTransaction(conn); }
}

// Client — works with DatabaseFactory only, never knows MySQL vs Postgres:
class UserRepository {
    private final DatabaseFactory db;

    UserRepository(DatabaseFactory db) { this.db = db; }

    void save(User user) {
        Connection conn = db.createConnection(url);
        Transaction tx  = db.createTransaction(conn);  // consistent with conn
        try {
            conn.prepareStatement("INSERT INTO users ...").execute();
            tx.commit();
        } catch (Exception e) {
            tx.rollback();
        }
    }
}

// Wiring: inject factory (production vs test):
DatabaseFactory factory = isProduction() ? new MySqlFactory() : new InMemoryDbFactory();
UserRepository repo = new UserRepository(factory);
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Abstract Factory is just multiple Factory Methods | The distinction is INTENT. Multiple Factory Methods in a class becomes an Abstract Factory when the factory methods form a coherent CONTRACT — all created products are meant to be used together (they form a family). The key constraint: products from one factory must be compatible with each other |
| Adding a new product to Abstract Factory is easy  | Adding a new product type (e.g., adding Dialog to GUIFactory) forces ALL concrete factories to be updated. Abstract Factory is open to new FAMILIES, but closed to new PRODUCT TYPES within the family — the opposite of what you might expect. This is the primary tradeoff                             |
| Abstract Factory must be an interface             | Can be an abstract class with some default implementations. Modern Java sometimes uses interface with default methods. But the pattern's contract — one factory creates all products in a family — is the key, not the specific Java construct used                                                      |

---

### 🔥 Pitfalls in Production

**Factory with too many product types becomes unwieldy:**

```java
// ANTI-PATTERN: Abstract Factory with too many product types:
interface UIFactory {
    Button     createButton();
    Checkbox   createCheckbox();
    RadioButton createRadioButton();
    Dropdown   createDropdown();
    TextField  createTextField();
    TextArea   createTextArea();
    Dialog     createDialog();
    Tooltip    createTooltip();
    // ... 15 more product types
}
// Every new concrete factory must implement ALL 18 methods.
// Adding new product type → modify all factories.

// FIX OPTION 1: Split into smaller, cohesive factories:
interface InputFactory  { Button createButton(); Checkbox createCheckbox(); }
interface TextFactory   { TextField createTextField(); TextArea createTextArea(); }
interface ModalFactory  { Dialog createDialog(); Tooltip createTooltip(); }

// FIX OPTION 2: Default method stubs (Java 8+) to avoid breaking all implementations:
interface UIFactory {
    Button createButton();
    default Dialog createDialog() {
        throw new UnsupportedOperationException("Dialog not supported by this factory");
    }
}
// Trade-off: you lose the compile-time guarantee that all products are supported.
```

---

### 🔗 Related Keywords

- `Factory Method` — Abstract Factory uses Factory Methods; difference: family vs. single product
- `Dependency Injection` — inject abstract factory into clients; Spring injects concrete implementation
- `Bridge Pattern` — also separates abstraction from implementation; different structure
- `Strategy Pattern` — concrete factory is a strategy for creating a product family
- `Facade Pattern` — often works with Abstract Factory to simplify the creation interface

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Create FAMILIES of related objects.       │
│              │ One factory = one family. All products   │
│              │ from a factory are guaranteed consistent. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ System must work with multiple families   │
│              │ of products; must guarantee consistency  │
│              │ within a family (e.g., cross-platform UI) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Few product types (overkill); family      │
│              │ product types change frequently (adding  │
│              │ product type breaks all concrete factories)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "IKEA collection: furnish the whole room  │
│              │  from KALLAX — everything matches.       │
│              │  Can't mix KALLAX shelves with BILLY desk."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Factory Method → Dependency Injection →   │
│              │ Bridge Pattern → Strategy Pattern         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's application context is often described as an Abstract Factory — `getBean(Button.class)` returns whatever concrete type is registered. But Spring also supports profiles (`@Profile("windows")` vs `@Profile("mac")`) which activate different sets of beans. How does Spring's profile mechanism relate to the Abstract Factory pattern? Can you model a "product family" with Spring profiles, and what are the advantages and limitations compared to a manually coded Abstract Factory?

**Q2.** In the database example, suppose you need to add a new product: `ConnectionPool` (manages a pool of connections). This requires modifying the `DatabaseFactory` interface, which breaks the existing `MySqlFactory` and `PostgresFactory`. How would you evolve the Abstract Factory interface without breaking existing implementations? Consider using interface default methods (Java 8+), an adapter class, or a separate factory extension interface — and discuss the tradeoffs of each approach.
