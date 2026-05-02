---
layout: default
title: "Visitor Pattern"
parent: "Design Patterns"
nav_order: 787
permalink: /design-patterns/visitor-pattern/
number: "787"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Double Dispatch, Open-Closed Principle"
used_by: "AST traversal, compilers, tax calculations, report generation, serialization"
tags: #advanced, #design-patterns, #behavioral, #oop, #double-dispatch, #ast
---

# 787 — Visitor Pattern

`#advanced` `#design-patterns` `#behavioral` `#oop` `#double-dispatch` `#ast`

⚡ TL;DR — **Visitor** lets you add new operations to object structures without modifying the objects — separating the algorithm from the objects it operates on via double dispatch, so new behaviors can be added without touching existing element classes.

| #787            | Category: Design Patterns                                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Double Dispatch, Open-Closed Principle          |                 |
| **Used by:**    | AST traversal, compilers, tax calculations, report generation, serialization |                 |

---

### 📘 Textbook Definition

**Visitor** (GoF, 1994): a behavioral design pattern that lets you define a new operation without changing the classes of the elements on which it operates. Separates algorithm from object structure. Components: **Visitor interface** — declares `visit(ConcreteElementA)`, `visit(ConcreteElementB)` for each element type. **Concrete visitors** — implement operations for each element type. **Element interface** — declares `accept(Visitor)`. **Concrete elements** — implement `accept()` by calling `visitor.visit(this)`. The double dispatch trick: `element.accept(visitor)` dispatches on element type; `visitor.visit(element)` dispatches on visitor type. GoF intent: "Represent an operation to be performed on elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates."

---

### 🟢 Simple Definition (Easy)

A tax inspector visiting different types of businesses. The inspector (visitor) knows how to compute taxes for each business type: restaurant, software company, factory. Each business (element) calls `inspector.visit(this)`. The inspector's `visit(Restaurant r)` method computes restaurant taxes; `visit(SoftwareCompany s)` computes tech taxes. Adding a new tax report (another operation): create a new visitor class. No changes to Restaurant, SoftwareCompany, or Factory classes.

---

### 🔵 Simple Definition (Elaborated)

AST (Abstract Syntax Tree) in compilers: nodes are `NumberNode`, `BinaryOpNode`, `VariableNode`. Operations: evaluate, pretty-print, type-check, optimize, compile to bytecode. Without Visitor: every operation would need a big `instanceof` chain, or every node class would need methods for every operation (adding evaluate, print, typecheck — modifying all node classes each time). With Visitor: `EvalVisitor`, `PrintVisitor`, `TypeCheckVisitor`, each knows what to do for each node type. Add new operation: new Visitor class only. AST node classes: untouched.

---

### 🔩 First Principles Explanation

**Double dispatch — how Visitor solves the "new operation on closed hierarchy" problem:**

```
THE PROBLEM WITHOUT VISITOR:

  // You have a fixed set of shape classes (from a library — can't modify):
  class Circle { double radius; }
  class Rectangle { double width, height; }
  class Triangle { double base, height; }

  // You want to add: area calculation, perimeter, serialization, SVG export.
  // Without Visitor: instanceof switch in every operation:

  double calculateArea(Shape shape) {
      if (shape instanceof Circle c)     { return Math.PI * c.radius * c.radius; }
      if (shape instanceof Rectangle r)  { return r.width * r.height; }
      if (shape instanceof Triangle t)   { return 0.5 * t.base * t.height; }
      throw new UnsupportedOperationException();
  }

  // Add new operation (perimeter): write another instanceof chain.
  // Add new shape: update EVERY instanceof chain.

VISITOR SOLUTION — DOUBLE DISPATCH:

  // ELEMENT INTERFACE — each shape accepts a visitor:
  interface Shape {
      <T> T accept(ShapeVisitor<T> visitor);
  }

  // CONCRETE ELEMENTS — each calls visitor.visit(this) — first dispatch on type:
  class Circle implements Shape {
      double radius;
      @Override
      public <T> T accept(ShapeVisitor<T> visitor) {
          return visitor.visitCircle(this);   // "this" is typed as Circle
      }
  }

  class Rectangle implements Shape {
      double width, height;
      @Override
      public <T> T accept(ShapeVisitor<T> visitor) {
          return visitor.visitRectangle(this);
      }
  }

  class Triangle implements Shape {
      double base, height;
      @Override
      public <T> T accept(ShapeVisitor<T> visitor) {
          return visitor.visitTriangle(this);
      }
  }

  // VISITOR INTERFACE — one method per element type:
  interface ShapeVisitor<T> {
      T visitCircle(Circle circle);
      T visitRectangle(Rectangle rect);
      T visitTriangle(Triangle tri);
  }

  // CONCRETE VISITOR 1: area calculation
  class AreaCalculator implements ShapeVisitor<Double> {
      @Override
      public Double visitCircle(Circle c)      { return Math.PI * c.radius * c.radius; }
      @Override
      public Double visitRectangle(Rectangle r){ return r.width * r.height; }
      @Override
      public Double visitTriangle(Triangle t)  { return 0.5 * t.base * t.height; }
  }

  // CONCRETE VISITOR 2: SVG serializer (NEW operation — zero changes to shape classes!)
  class SvgSerializer implements ShapeVisitor<String> {
      @Override
      public String visitCircle(Circle c) {
          return "<circle r=\"" + c.radius + "\"/>";
      }
      @Override
      public String visitRectangle(Rectangle r) {
          return "<rect width=\"" + r.width + "\" height=\"" + r.height + "\"/>";
      }
      @Override
      public String visitTriangle(Triangle t) {
          return "<polygon points=\"...\"/>";
      }
  }

  // DOUBLE DISPATCH EXPLAINED:
  Shape shape = new Circle(5.0);           // runtime type: Circle
  ShapeVisitor<Double> calc = new AreaCalculator();

  shape.accept(calc);
  // Step 1: shape.accept() — Java dispatches on shape's runtime type → Circle.accept()
  // Step 2: Circle.accept() calls visitor.visitCircle(this)
  //         → Java dispatches on visitor's runtime type → AreaCalculator.visitCircle()
  // TWO dispatches → "double dispatch" — overloading alone doesn't achieve this.

  // Adding new operation (perimeter): create PerimeterCalculator implements ShapeVisitor.
  // Shape classes: untouched.

  // Weakness: adding new element type (Ellipse):
  // → Must add visitEllipse() to ShapeVisitor interface → ALL existing visitors must implement it.
  // Visitor trades easy operation extension for harder element extension (Extensibility vs Stability tradeoff).

JAVA 17+ PATTERN MATCHING ALTERNATIVE:

  // Java's switch expressions with sealed interfaces eliminate Visitor in many cases:
  sealed interface Shape permits Circle, Rectangle, Triangle {}

  double area(Shape shape) {
      return switch (shape) {
          case Circle c     -> Math.PI * c.radius() * c.radius();
          case Rectangle r  -> r.width() * r.height();
          case Triangle t   -> 0.5 * t.base() * t.height();
      };
  }
  // Compiler enforces exhaustiveness — same safety as Visitor, less boilerplate.
  // When element hierarchy is sealed/controlled, sealed switch > Visitor.
  // When element hierarchy is open/third-party, Visitor still valuable.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Visitor:

- New operation on N element types: write `instanceof` chain in N places OR add method to N element classes
- Both violate OCP and SRP

WITH Visitor:
→ New operation: add one `Visitor` class with one `visit()` method per element type. Element classes: untouched.

---

### 🧠 Mental Model / Analogy

> A tax system with different tax rules per entity type. Tax Inspector (Visitor) visits companies: Restaurant, Factory, SoftwareCompany. Each company calls `inspector.visit(this)`. Inspector knows restaurant tax rules, factory tax rules, tech company tax rules. Add new inspector (AuditInspector): new class, no changes to company classes. This is Visitor: inspector brings the algorithm; company exposes itself for inspection.

"Tax Inspector" = Visitor (carries the operation)
"Company.accept(inspector)" = Element.accept(visitor) — first dispatch
"inspector.visitRestaurant(restaurant)" = visitor.visit(concreteElement) — second dispatch
"Add new inspector (AuditInspector)" = add new Visitor class — no changes to element classes
"Tax rules per company type" = different visit() methods for each element type

---

### ⚙️ How It Works (Mechanism)

```
VISITOR DOUBLE DISPATCH:

  element.accept(visitor)
  → element's type dispatched → ConcreteElement.accept()
  → calls visitor.visit(this)  [this is typed as ConcreteElement]
  → visitor's type dispatched → ConcreteVisitor.visitConcreteElement()

  Two levels of polymorphism → correct method for both element AND visitor type.
  Plain method overloading doesn't work (resolves at compile time on static type).
  Visitor.visit(Element) would always call the base interface overload.
  Double dispatch = runtime dispatch on BOTH receiver and argument type.
```

---

### 🔄 How It Connects (Mini-Map)

```
Add new operations to object hierarchy without modifying element classes
        │
        ▼
Visitor Pattern ◄──── (you are here)
(double dispatch; visitor carries operation; elements accept visitors)
        │
        ├── Composite: Visitor often traverses Composite tree structures
        ├── Iterator: Visitor can use Iterator to traverse elements
        ├── Template Method: visitor logic often uses template method within visit()
        └── Java sealed classes + switch: modern alternative to Visitor in controlled hierarchies
```

---

### 💻 Code Example

```java
// Compiler AST traversal with Visitor:
sealed interface AstNode permits NumberNode, BinaryOpNode, VariableNode {
    <T> T accept(AstVisitor<T> visitor);
}

record NumberNode(double value) implements AstNode {
    public <T> T accept(AstVisitor<T> v) { return v.visitNumber(this); }
}

record BinaryOpNode(String op, AstNode left, AstNode right) implements AstNode {
    public <T> T accept(AstVisitor<T> v) { return v.visitBinaryOp(this); }
}

record VariableNode(String name) implements AstNode {
    public <T> T accept(AstVisitor<T> v) { return v.visitVariable(this); }
}

interface AstVisitor<T> {
    T visitNumber(NumberNode n);
    T visitBinaryOp(BinaryOpNode n);
    T visitVariable(VariableNode n);
}

// Visitor 1: evaluate expression
class EvalVisitor implements AstVisitor<Double> {
    private final Map<String, Double> variables;
    EvalVisitor(Map<String, Double> vars) { this.variables = vars; }

    public Double visitNumber(NumberNode n) { return n.value(); }
    public Double visitVariable(VariableNode n) {
        return variables.getOrDefault(n.name(), 0.0);
    }
    public Double visitBinaryOp(BinaryOpNode n) {
        double l = n.left().accept(this), r = n.right().accept(this);
        return switch (n.op()) {
            case "+" -> l + r;   case "-" -> l - r;
            case "*" -> l * r;   case "/" -> l / r;
            default  -> throw new UnsupportedOperationException(n.op());
        };
    }
}

// Visitor 2: pretty-print (new operation — zero changes to AST nodes)
class PrettyPrintVisitor implements AstVisitor<String> {
    public String visitNumber(NumberNode n)   { return String.valueOf(n.value()); }
    public String visitVariable(VariableNode n) { return n.name(); }
    public String visitBinaryOp(BinaryOpNode n) {
        return "(" + n.left().accept(this) + " " + n.op() + " " + n.right().accept(this) + ")";
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Visitor requires modifying element classes      | ONLY the `accept(Visitor)` method needs to be added to elements. If elements are in a library you can't modify, Visitor is not applicable — use `instanceof` chains or reflection-based dispatch. Visitor requires cooperation from element classes (they must implement `accept()`). The pattern works best when you own the element hierarchy.                                         |
| Visitor is always better than instanceof chains | Java 17+ sealed interfaces + switch expressions with exhaustiveness checking give compile-time safety similar to Visitor, without the boilerplate. For controlled, sealed hierarchies, the switch approach is often cleaner. Visitor adds value when: the hierarchy is open/extensible, you need to pass state between visits (visitor instance fields), or operations are very complex. |
| Double dispatch is only achievable via Visitor  | Java's sealed switch expressions achieve similar dispatch without explicit Visitor. Other languages (Kotlin when expression, Scala match) also provide exhaustive dispatch on sealed types. Visitor is the pre-Java-17 workaround for Java's single dispatch and open class hierarchies.                                                                                                 |

---

### 🔥 Pitfalls in Production

**Visitor breaking when new element types are added:**

```java
// PROBLEM: Adding new element type to hierarchy forces ALL existing visitors to update:
interface ShapeVisitor<T> {
    T visitCircle(Circle c);
    T visitRectangle(Rectangle r);
    // Step 1: Add Ellipse element
}

class Ellipse implements Shape {
    public <T> T accept(ShapeVisitor<T> v) {
        return v.visitEllipse(this);    // ← requires new method in EVERY visitor
    }
}

// Must add visitEllipse() to ShapeVisitor interface
// → AreaCalculator, SvgSerializer, PerimeterCalculator, ALL visitors must implement visitEllipse()
// 20 existing visitors × 1 new element = 20 files to update.

// MITIGATION 1: Provide default implementation in interface (Java 8+):
interface ShapeVisitor<T> {
    T visitCircle(Circle c);
    T visitRectangle(Rectangle r);
    default T visitEllipse(Ellipse e) {
        throw new UnsupportedOperationException("Ellipse not supported by this visitor");
    }
}
// Existing visitors compile; fail at runtime if they encounter an Ellipse.

// MITIGATION 2: Abstract base visitor with default no-ops:
abstract class BaseShapeVisitor<T> implements ShapeVisitor<T> {
    protected T defaultVisit(Shape s) { return null; }
    public T visitCircle(Circle c)   { return defaultVisit(c); }
    public T visitRectangle(Rectangle r) { return defaultVisit(r); }
    public T visitEllipse(Ellipse e) { return defaultVisit(e); }
}
// Subclass only overrides methods it cares about.
```

---

### 🔗 Related Keywords

- `Composite Pattern` — Visitor commonly traverses Composite tree structures (ASTs, file hierarchies)
- `Double Dispatch` — the underlying mechanism Visitor uses to resolve both element and visitor type at runtime
- `Iterator Pattern` — iterate elements; Visitor defines what to do at each element
- `Template Method Pattern` — visitor logic often uses template method patterns within visit() methods
- `Sealed Interfaces (Java 17)` — modern alternative to Visitor for controlled, exhaustive hierarchies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Visitor carries operations; elements      │
│              │ accept visitors. Add operations without  │
│              │ modifying element classes. Double dispatch│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fixed element hierarchy; many unrelated  │
│              │ operations on elements; new operations   │
│              │ added frequently; elements can't be modified│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Element hierarchy changes frequently;    │
│              │ Java 17+ sealed switch is available;     │
│              │ hierarchy is open/extensible by design   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tax inspector visits companies: inspector│
│              │  brings the tax rules; companies just    │
│              │  open their doors (accept)."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Double Dispatch → Composite Pattern →    │
│              │ Sealed Interfaces → Java 17 switch       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java compilers (javac, ECJ) use Visitor extensively for AST traversal — type checking passes, optimization passes, code generation passes are all separate `AstVisitor` implementations traversing the same AST node tree. This is the "open operations, closed elements" tradeoff. The Java grammar has ~100 AST node types; adding a new AST node is rare; adding new compiler passes is frequent. This makes Visitor ideal. What would happen to a compiler's architecture if it used `instanceof` chains instead of Visitor? How would adding a new optimization pass differ?

**Q2.** Java 21's sealed interfaces with `switch` exhaustiveness checking provide compile-time guarantees similar to Visitor — if you forget to handle a sealed subtype in a switch, the compiler errors. But unlike Visitor, `switch` is a single dispatch on one type. The Visitor achieves dispatch on BOTH element type AND visitor type. In what real scenario do you actually need two-dimensional dispatch (the full Visitor benefit)? Give a concrete example where single dispatch (sealed switch) is insufficient and Visitor's double dispatch is necessary.
