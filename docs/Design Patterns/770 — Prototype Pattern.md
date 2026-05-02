---
layout: default
title: "Prototype Pattern"
parent: "Design Patterns"
nav_order: 770
permalink: /design-patterns/prototype-pattern/
number: "770"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Builder Pattern"
used_by: "Object copying, Game entities, Test fixtures, Expensive initialization"
tags: #intermediate, #design-patterns, #creational, #cloning, #oop
---

# 770 — Prototype Pattern

`#intermediate` `#design-patterns` `#creational` `#cloning` `#oop`

⚡ TL;DR — **Prototype** creates new objects by **cloning an existing object** (the prototype) rather than constructing from scratch — useful when object creation is expensive, when the exact type is unknown at compile time, or when you need copies of pre-configured objects without re-running their initialization logic.

| #770            | Category: Design Patterns                                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Builder Pattern                           |                 |
| **Used by:**    | Object copying, Game entities, Test fixtures, Expensive initialization |                 |

---

### 📘 Textbook Definition

**Prototype** (GoF, 1994): a creational design pattern that specifies the kinds of objects to create using a prototypical instance and creates new objects by copying (cloning) that prototype. Solves the problem of creating objects when: (1) the class to instantiate is specified at runtime, not compile time; (2) instances of a class can have only a few different combinations of state, and it is more convenient to clone a prototype than to instantiate and configure manually; (3) creation is expensive and cloning from a pre-initialized prototype is cheaper. GoF intent: "Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype." Java: `Cloneable` interface + `Object.clone()`, or copy constructors, or serialization-based cloning.

---

### 🟢 Simple Definition (Easy)

A photocopier. You have an original document (the prototype). Instead of retyping the document for each recipient, you copy it. The copies start as identical clones of the original. You can then make changes to individual copies — editing recipient name, date — without affecting the original. The original is the prototype; each photocopy is a cloned instance.

---

### 🔵 Simple Definition (Elaborated)

Game development: loading a complex enemy character involves reading from disk, processing textures, setting up physics state — takes 200ms. You create one "template goblin" (prototype) with all that initialized. For each new goblin spawned, `goblinTemplate.clone()` — 1ms. Each clone starts with identical state but can then diverge (different position, different HP randomization). Prototype avoids repeating expensive initialization for each new instance.

---

### 🔩 First Principles Explanation

**Deep copy vs. shallow copy — the most critical nuance:**

```
SHALLOW COPY:

  class Config {
      String name;                    // immutable — safe to share
      List<String> allowedHosts;      // mutable — DANGER if shared
  }

  Config original = new Config("production", new ArrayList<>(List.of("api.example.com")));
  Config copy     = original.clone();  // SHALLOW copy

  // After shallow copy:
  // copy.name           → same "production" String (safe — String is immutable)
  // copy.allowedHosts   → SAME LIST OBJECT as original.allowedHosts

  copy.allowedHosts.add("evil.com");   // ← modifies BOTH original AND copy!
  System.out.println(original.allowedHosts);  // ["api.example.com", "evil.com"] OOPS!

DEEP COPY:

  @Override
  protected Config clone() {
      try {
          Config copy = (Config) super.clone();       // copies primitives/refs
          copy.allowedHosts = new ArrayList<>(this.allowedHosts);  // deep copy mutable field
          return copy;
      } catch (CloneNotSupportedException e) {
          throw new AssertionError(); // won't happen if Config implements Cloneable
      }
  }

  // Now: copy.allowedHosts is a NEW list with the same elements.
  // Modifying copy.allowedHosts doesn't affect original. ✓

JAVA CLONEABLE PROBLEMS:

  Problems with Java's Cloneable + Object.clone():
  1. Cloneable is a MARKER INTERFACE — no clone() method in the interface!
     Object.clone() checks if class implements Cloneable at runtime.
     If not: throws CloneNotSupportedException.

  2. Object.clone() creates a SHALLOW copy without calling constructor.
     Final fields cannot be reassigned during clone → deep copy of final fields is impossible.

  3. Must call super.clone() everywhere in the hierarchy — fragile.

  4. Exception handling ceremony: CloneNotSupportedException is checked.

  Joshua Bloch (Effective Java, Item 13): "Cloneable is deeply flawed."

BETTER ALTERNATIVES TO Object.clone():

  1. COPY CONSTRUCTOR:

     class Config {
         String name;
         List<String> allowedHosts;

         Config(Config other) {             // copy constructor
             this.name         = other.name;                        // String is immutable: safe
             this.allowedHosts = new ArrayList<>(other.allowedHosts);  // deep copy
         }
     }

     Config copy = new Config(original);   // clear, explicit, no checked exceptions

  2. COPY FACTORY METHOD:

     class Config {
         static Config copyOf(Config other) {  // static factory for copy
             return new Config(other.name, new ArrayList<>(other.allowedHosts));
         }
     }

     Config copy = Config.copyOf(original);

  3. SERIALIZATION-BASED DEEP COPY (for complex graphs):

     // Java serialization:
     static <T extends Serializable> T deepCopy(T obj) throws Exception {
         ByteArrayOutputStream baos = new ByteArrayOutputStream();
         new ObjectOutputStream(baos).writeObject(obj);
         ByteArrayInputStream bais  = new ByteArrayInputStream(baos.toByteArray());
         return (T) new ObjectInputStream(bais).readObject();
     }
     // Works for complex object graphs.
     // Expensive. Only if all objects in graph are Serializable.

  4. JACKSON DEEP COPY:

     ObjectMapper mapper = new ObjectMapper();
     Config copy = mapper.readValue(mapper.writeValueAsString(original), Config.class);
     // Easy to read. JSON round-trip. OK for DTOs.

PROTOTYPE REGISTRY:

  // Store named prototypes — clone from registry instead of constructing:
  class ShapeRegistry {
      private final Map<String, Shape> prototypes = new HashMap<>();

      void register(String name, Shape shape) { prototypes.put(name, shape); }

      Shape create(String name) {
          Shape prototype = prototypes.get(name);
          if (prototype == null) throw new IllegalArgumentException("Unknown: " + name);
          return prototype.clone();  // or copy constructor
      }
  }

  registry.register("filled-red-circle", new Circle(RED, FILLED, 10));
  registry.register("outlined-blue-rect", new Rectangle(BLUE, OUTLINED, 20, 15));

  Shape circle = registry.create("filled-red-circle");  // cheap clone, pre-configured
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Prototype:

- Creating each game enemy from scratch: 200ms × 50 enemies = 10 seconds of loading
- Re-running complex initialization (disk I/O, texture loading) for every instance

WITH Prototype:
→ Initialize once, clone for each new instance: 1ms per clone
→ Prototype registry: named, pre-configured templates; consumers clone without knowing concrete type

---

### 🧠 Mental Model / Analogy

> A cookie dough and cookie cutters. You spend 30 minutes making the perfect dough (the prototype). Each cookie is stamped from the same dough — instant. If you stamp and then want a chocolate chip variant, you add chips to that specific stamped copy without changing the original dough. Each copy is independent after cloning — it can evolve separately.

"Perfect dough" = prototype (expensive to make once)
"Stamp a cookie" = clone() (cheap)
"Add chips to individual cookie" = modify state of specific clone after creation
"Original dough unchanged" = prototype is not modified by cloning

---

### ⚙️ How It Works (Mechanism)

```
PROTOTYPE PATTERN:

  «interface»
  Prototype
  ──────────
  +clone(): Prototype

  ConcretePrototype
  ──────────────────
  -field1, field2, ...
  +clone(): ConcretePrototype
      → copy constructor OR deep copy

  CLIENT:
  ConcretePrototype p1 = original.clone();  // don't call new!
  p1.setField1("modified");                 // modify clone independently
```

---

### 🔄 How It Connects (Mini-Map)

```
Expensive object construction + need many similar instances
        │
        ▼
Prototype Pattern ◄──── (you are here)
(clone from pre-initialized prototype instead of constructing)
        │
        ├── Builder Pattern: build complex object; Builder = construction; Prototype = copy
        ├── Object Pool: pool reuses instances (reset state); Prototype creates new copies
        ├── Factory Method: Factory creates from scratch; Prototype creates from clone
        └── Flyweight: shares instances (read-only); Prototype creates independent copies
```

---

### 💻 Code Example

{% raw %}
```java
// Copy constructor approach (preferred over Cloneable):
public class EmailTemplate {
    private final String subject;       // immutable — shared safely
    private final List<String> to;      // mutable — must deep copy
    private final Map<String, String> variables;  // mutable — must deep copy

    // Primary constructor:
    public EmailTemplate(String subject, List<String> to, Map<String, String> vars) {
        this.subject   = subject;
        this.to        = List.copyOf(to);    // defensive: immutable list
        this.variables = Map.copyOf(vars);   // defensive: immutable map
    }

    // Copy constructor (Prototype):
    public EmailTemplate(EmailTemplate other) {
        this.subject   = other.subject;                // String: immutable, safe to share
        this.to        = new ArrayList<>(other.to);    // deep copy: mutable list
        this.variables = new HashMap<>(other.variables);  // deep copy: mutable map
    }

    public EmailTemplate withVariable(String key, String value) {
        EmailTemplate copy = new EmailTemplate(this);    // clone
        copy.variables.put(key, value);                  // modify clone
        return copy;
    }
}

// Usage:
EmailTemplate welcomeTemplate = new EmailTemplate(
    "Welcome to {{company}}!",
    List.of("user@example.com"),
    Map.of("company", "Acme Corp")
);

// Create personalized versions without re-building from scratch:
EmailTemplate forAlice = welcomeTemplate
    .withVariable("name", "Alice")
    .withVariable("company", "Acme Corp");

EmailTemplate forBob = welcomeTemplate
    .withVariable("name", "Bob")
    .withVariable("company", "Globex");
```
{% endraw %}

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cloneable is the right way to implement Prototype in Java             | Joshua Bloch (Effective Java, Item 13) explicitly recommends AGAINST `Cloneable` and `Object.clone()`. Cloneable has fundamental design flaws: no method in the interface, constructor is bypassed, final fields can't be reassigned, CloneNotSupportedException ceremony. Prefer copy constructors or copy factory methods                               |
| Shallow copy is fine if fields are immutable                          | Partially true. Fields holding immutable objects (String, Integer, primitive wrappers, records) are safe to share via shallow copy. Fields holding mutable objects (ArrayList, HashMap, custom mutable classes) MUST be deep copied. You must analyze each field                                                                                          |
| Prototype is only about performance (avoiding expensive construction) | Performance is one motivation, but not the only one. Prototype also: (1) enables creating objects when the exact class is unknown at compile time (runtime polymorphism); (2) provides pre-configured "template" objects in a registry; (3) simplifies creating objects with complex initialization state that is hard to reproduce via constructor calls |

---

### 🔥 Pitfalls in Production

**Shared mutable state after shallow copy:**

```java
// ANTI-PATTERN — shallow copy of mutable collection:
class OrderTemplate implements Cloneable {
    List<OrderItem> items;   // mutable

    @Override
    public OrderTemplate clone() {
        try {
            return (OrderTemplate) super.clone();  // SHALLOW copy — items list shared!
        } catch (CloneNotSupportedException e) { throw new AssertionError(); }
    }
}

OrderTemplate template = new OrderTemplate();
template.items.add(new OrderItem("Widget", 1));

OrderTemplate copy = template.clone();
copy.items.add(new OrderItem("Gadget", 2));  // modifies BOTH template AND copy's items!

System.out.println(template.items.size());  // 2 — template polluted! Bug.

// FIX — deep copy mutable fields:
@Override
public OrderTemplate clone() {
    try {
        OrderTemplate copy = (OrderTemplate) super.clone();
        copy.items = this.items.stream()         // deep copy: new list
            .map(OrderItem::copyOf)              // each item also copied if mutable
            .collect(Collectors.toCollection(ArrayList::new));
        return copy;
    } catch (CloneNotSupportedException e) { throw new AssertionError(); }
}

// BEST FIX — avoid Cloneable entirely; use copy constructor:
OrderTemplate copy = new OrderTemplate(template);  // copy constructor handles deep copy explicitly
```

---

### 🔗 Related Keywords

- `Builder Pattern` — builds complex objects step by step; Prototype copies an existing one
- `Object Pool Pattern` — pools and reuses objects (resets state); Prototype creates new independent copies
- `Flyweight Pattern` — shares immutable objects to save memory; Prototype creates independent mutable copies
- `Factory Method` — creates new objects; Prototype clones an existing configured object
- `Deep Copy vs. Shallow Copy` — fundamental concept; Prototype must handle correctly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Clone a pre-initialized prototype instead │
│              │ of constructing from scratch. New object  │
│              │ starts as a copy, can then diverge.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object creation is expensive; need many   │
│              │ similar pre-configured instances; type is │
│              │ unknown at compile time                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Objects have complex deep graphs that are │
│              │ hard to copy correctly; cloning semantics │
│              │ are unclear (which fields are shared?)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cookie stamp: make perfect dough once,   │
│              │  stamp as many cookies as needed — each  │
│              │  starts identical, then evolves on its   │
│              │  own."                                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Builder Pattern → Object Pool Pattern →   │
│              │ Flyweight Pattern → Deep vs Shallow Copy  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java 14+ introduced records: `record Point(int x, int y) {}`. Records are immutable — you can't modify them after creation. They also get auto-generated `equals()`, `hashCode()`, and `toString()` but NO `clone()`. For an immutable record, is Prototype Pattern even necessary? Or does it collapse into something else? How do Java `record` "wither" methods (`withX(newValue)`) relate to the Prototype pattern concept?

**Q2.** In game development, an Entity Component System (ECS) is common. Entities are just IDs; Components are data objects attached to entities. If you want to "spawn 100 enemy goblins," you might have a "prefab" goblin entity (prototype). Cloning the goblin means copying all its component data. However, some components should be shared (read-only mesh data, textures) while others must be independent (health, position). How would you design this partial deep copy / partial shared reference cloning in an ECS? What role does the Flyweight pattern play here?
