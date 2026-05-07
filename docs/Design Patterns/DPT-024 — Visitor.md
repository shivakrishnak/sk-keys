---
layout: default
title: "Visitor"
parent: "Design Patterns"
nav_order: 24
permalink: /design-patterns/visitor/
number: "DPT-024"
category: Design Patterns
difficulty: ★★★
depends_on: Object-Oriented Programming (OOP), Double Dispatch, Polymorphism, Open-Closed Principle
used_by: AST Traversal, Compiler Design, Document Rendering, Report Generation
related: Composite, Iterator, Strategy, Interpreter, Double Dispatch
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - advanced
---

# DPT-024 — Visitor

⚡ TL;DR — Visitor lets you add new operations to an object hierarchy without modifying its classes, by separating algorithms from the objects they operate on.

| #789 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Double Dispatch, Polymorphism, Open-Closed Principle | |
| **Used by:** | AST Traversal, Compiler Design, Document Rendering, Report Generation | |
| **Related:** | Composite, Iterator, Strategy, Interpreter, Double Dispatch | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A compiler's Abstract Syntax Tree (AST) has node types: `IfStatement`, `WhileLoop`, `Assignment`, `BinaryExpression`. You need to perform three distinct operations on the AST: pretty-printing, type-checking, and code-generation. Without Visitor, each node class must implement all three operations — `IfStatement` has `prettyPrint()`, `typeCheck()`, and `generateCode()`. Adding a fourth operation (dead-code elimination) requires modifying all 20 node classes. The node classes, which should only model the tree structure, become bloated with unrelated algorithm implementations.

**THE BREAKING POINT:**
Node classes are extended by dozens of teams across the compiler codebase. Adding an operation requires coordinating changes to all node classes simultaneously — a large merge risk. The node classes violate the Single Responsibility Principle: they model structure AND implement every operation that anyone ever wants to perform on that structure.

**THE INVENTION MOMENT:**
This is exactly why the Visitor pattern was created. Each operation (pretty-printer, type-checker, code-generator) becomes its own class. The node classes remain stable — they only implement `accept(Visitor v)`. Adding a new operation is adding one class; node classes don't change.

---

### 📘 Textbook Definition

The **Visitor** pattern is a behavioural design pattern that separates an algorithm from the objects it operates on. A **Visitor** interface declares a `visit(ConcreteElement)` method for each concrete element type in the object hierarchy. Each **Element** class implements `accept(Visitor v)` which calls `v.visit(this)`. This achieves double dispatch: the specific `visit` method called is determined by BOTH the runtime type of the visitor AND the runtime type of the element. New operations are added as new visitor classes without changing element classes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Let a new "operation object" walk through your objects and do its work without touching the objects themselves.

**One analogy:**
> A tax inspector (Visitor) visits different types of businesses (Elements): a restaurant, a manufacturer, a retailer. Each business knows how to let the inspector in: `accept(inspector)`. The inspector then applies **their own rules** for auditing each business type. Adding a new type of inspector (fire safety, health code) requires no changes to the businesses — they just call `accept()` and the new inspector does their job.

**One insight:**
Visitor solves the expression problem asymmetry: when you have a fixed set of types but an open set of operations. If types change often, adding `accept()` to each type is expensive. If operations change often, Visitor is ideal — each new operation is one new class.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The object hierarchy (element types) is relatively fixed.
2. New operations must be addable without modifying element classes.
3. Each operation's logic for each element type must be separated.

**DERIVED DESIGN:**
Given invariant 1+2: element classes implement `accept(Visitor v)` once and never change. Given invariant 3: each visitor class implements one operation's logic for ALL element types — one `visit(IfStatement)`, one `visit(WhileLoop)`, etc. per visitor.

The mechanism enabling this is **double dispatch**: normal Java dispatch is single (determined by object type). In Visitor, `element.accept(visitor)` → `visitor.visit(this)` — the call to `visit` is dispatched on BOTH the visitor type (which operation) AND the element type (which element's logic to apply). Java's single dispatch alone cannot achieve this; the `accept()` call breaks it into two sequential single-dispatch calls.

**THE TRADE-OFFS:**
**Gain:** New operations added as new visitor classes — zero element modifications; each operation's code for all element types collected in one class (cohesive); algorithms and data structures cleanly separated.
**Cost:** Adding a new element type requires updating all existing visitor classes (all `visit` methods for the new type); visitor and element are tightly coupled — visitor must know all element types; accumulating state within a visitor between `visit` calls requires careful design.

---

### 🧪 Thought Experiment

**SETUP:**
A document has three element types: `Heading`, `Paragraph`, and `Table`. You need two operations: HTML rendering and Markdown rendering.

**WHAT HAPPENS WITHOUT VISITOR:**
`Heading` has `renderHtml()` and `renderMarkdown()`. `Paragraph` has both. `Table` has both. Adding PDF rendering requires touching all three classes. There are 6 methods scattered across 3 classes.

**WHAT HAPPENS WITH VISITOR:**
`Heading`, `Paragraph`, `Table` each have `accept(Visitor v)` only. `HtmlRenderVisitor` has `visit(Heading)`, `visit(Paragraph)`, `visit(Table)` — HTML logic for all elements in one class. `MarkdownRenderVisitor` has the same triple for Markdown. Adding PDF rendering = `PdfRenderVisitor` class with three `visit` methods. Existing classes untouched.

**THE INSIGHT:**
Visitor trades "adding new element types is easy" for "adding new operations is easy." The pattern fits when the set of types is STABLE but the set of operations GROWS. If both change frequently, Visitor may not be the right tool.

---

### 🧠 Mental Model / Analogy

> Visitor is like a team of specialist inspectors sent to a set of fixed facilities. The facilities (Elements) never change structurally — they're the same buildings. Each inspector type (Visitor) knows exactly what to check in each facility type: the fire inspector checks fire exits in offices and restaurants differently; the health inspector checks kitchens and storage rooms. Adding a new inspector type needs no construction changes — buildings just let inspectors in via the same door (`accept`).

- "Fixed set of buildings" → stable element hierarchy (IfStatement, WhileLoop...)
- "Letting inspector in" → `element.accept(visitor)`
- "Inspector checks building" → `visitor.visit(element)`
- "Type of inspector" → Visitor subclass (PrettyPrintVisitor, TypeCheckVisitor)
- "Adding a new inspector" → new Visitor class, zero element changes

Where this analogy breaks down: real inspectors can choose to visit only some buildings. GoF Visitor implementations typically visit ALL element types — a visitor that handles only some types must provide no-op implementations for others, which is verbose.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Visitor lets an "operation object" travel through a group of different objects and do something specific to each type, without the objects needing to know what operation is being performed. The objects just say "come in" — the visitor handles the rest.

**Level 2 — How to use it (junior developer):**
Create a `Visitor` interface with one `visit(ConcreteElement)` overload per element type. Each element class implements `accept(Visitor v)` which calls `v.visit(this)`. Create concrete visitor classes for each operation, implementing all `visit` methods. To perform an operation: create a visitor instance and call `element.accept(visitor)` — or traverse a collection of elements calling `accept` on each.

**Level 3 — How it works (mid-level engineer):**
The double dispatch mechanism: `element.accept(visitor)` is standard polymorphic dispatch — the JVM selects `ConcreteElement.accept()` based on `element`'s runtime type. Inside `accept`, `visitor.visit(this)` is another standard dispatch — `this` has type `ConcreteElement` (not `Element`), so the JVM selects `visitor.visit(ConcreteElement)` — not `visitor.visit(Element)`. The combination of two single dispatches achieves the effect of double dispatch: both the visitor type and the element type are resolved at runtime. Java 21 pattern matching (`instanceof` patterns in switch) offers an alternative to Visitor for open hierarchies, but cannot match the extensibility of Visitor for closed hierarchies.

**Level 4 — Why it was designed this way (senior/staff):**
Visitor is the GoF approach to the Expression Problem (Philip Wadler, 1998): how do you add new operations to existing types, and new types to existing operations, without modifying existing code? Visitor solves the operations axis: new operations via new visitor classes, zero type changes. Sealed classes + pattern matching (Java 17+) solve the types axis: the compiler knows all types, and `switch` exhaustively matches them. The two techniques are complementary. In compilers (LLVM, javac), the Visitor pattern is ubiquitous because AST nodes are fixed after language design but passes (optimisations, analyses, transforms) are added continuously. A key production concern: accumulating visitor state into a composite result (e.g., type inference that builds a symbol table while visiting) requires careful threading of a context object through all `visit` calls — usually via a `VisitorContext` parameter or an instance field on the visitor itself.

---

### ⚙️ How It Works (Mechanism)

**Double dispatch sequence:**
```
┌─────────────────────────────────────────────────┐
│  VISITOR DOUBLE DISPATCH                        │
│                                                 │
│  Client calls:                                  │
│    ifStatement.accept(prettyPrinter)            │
│         ↓ dispatch 1: on ifStatement type       │
│                                                 │
│  IfStatement.accept(Visitor v):                 │
│    v.visit(this)   ← this = IfStatement         │
│         ↓ dispatch 2: on visitor type           │
│           + element type (this = IfStatement)   │
│                                                 │
│  PrettyPrintVisitor.visit(IfStatement stmt):    │
│    print("if (")                                │
│    stmt.condition().accept(this) ← recurse      │
│    print(") {")                                 │
│    stmt.body().accept(this) ← recurse           │
│    print("}")                                   │
└─────────────────────────────────────────────────┘
```

**Visitor interface and element hierarchy:**
```
Visitor interface:
  visit(IfStatement)
  visit(WhileLoop)
  visit(Assignment)
  visit(BinaryExpression)

Element interface:
  accept(Visitor v)

IfStatement implements Element:
  accept(v) { v.visit(this); }

PrettyPrintVisitor implements Visitor:
  visit(IfStatement s) { ... }
  visit(WhileLoop w)   { ... }
  visit(Assignment a)  { ... }
  visit(BinaryExpression b) { ... }

TypeCheckVisitor implements Visitor:
  visit(IfStatement s) { ... different logic ... }
  ...
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Compiler receives source file
  → Parser builds AST (tree of Elements)
  → TypeCheckVisitor v = new TypeCheckVisitor()
                         ← YOU ARE HERE (visitor created)
  → rootNode.accept(v)
  → IfStatement.accept(v) → v.visit(ifStatement)
  → TypeCheckVisitor resolves condition type
  → visits child nodes recursively
  → Returns type-checked AST
  → CodeGenVisitor applied next on same AST
```

**FAILURE PATH:**
```
TypeCheckVisitor.visit(NewNodeType) not implemented
  → If NewNodeType is a new element class added to AST
  → Visitor interface doesn't have visit(NewNodeType)
  → Compile error (if compile-time typed)
  → OR: visitor default method silently skips node
  → TYPE CHECKING INCOMPLETE — silent bug
Fix: adding new element type MUST update all visitors
```

**WHAT CHANGES AT SCALE:**
In a large compiler with 50 AST node types and 30 visitor passes, the Visitor interface has 50 methods. Implementing a new pass (visitor) requires 50 method implementations — many of which may be no-ops. Using an abstract visitor base class with default no-op implementations reduces boilerplate when a pass only cares about a subset of node types.

---

### 💻 Code Example

**Example 1 — AST expression evaluator:**
```java
// Element (AST Node) interface
public interface AstNode {
    int accept(AstVisitor visitor);
}

// Visitor interface
public interface AstVisitor {
    int visit(NumberNode node);
    int visit(AddNode node);
    int visit(MultiplyNode node);
}

// Concrete elements
public class NumberNode implements AstNode {
    public final int value;
    public NumberNode(int v) { this.value = v; }

    @Override
    public int accept(AstVisitor v) {
        return v.visit(this); // dispatch 2 resolves here
    }
}

public class AddNode implements AstNode {
    public final AstNode left, right;

    public AddNode(AstNode l, AstNode r) {
        this.left = l; this.right = r;
    }

    @Override
    public int accept(AstVisitor v) {
        return v.visit(this);
    }
}

public class MultiplyNode implements AstNode {
    public final AstNode left, right;
    @Override
    public int accept(AstVisitor v) { return v.visit(this); }
}

// Concrete visitor: Evaluator
public class EvaluatorVisitor implements AstVisitor {
    @Override
    public int visit(NumberNode n) {
        return n.value; // base case
    }
    @Override
    public int visit(AddNode n) {
        return n.left.accept(this) + n.right.accept(this);
    }
    @Override
    public int visit(MultiplyNode n) {
        return n.left.accept(this) * n.right.accept(this);
    }
}

// Adding new operation: PrettyPrinter
// Zero changes to AstNode, NumberNode, AddNode, etc.
public class PrettyPrintVisitor implements AstVisitor {
    @Override
    public int visit(NumberNode n) {
        System.out.print(n.value);
        return 0;
    }
    @Override
    public int visit(AddNode n) {
        System.out.print("(");
        n.left.accept(this);
        System.out.print(" + ");
        n.right.accept(this);
        System.out.print(")");
        return 0;
    }
    @Override
    public int visit(MultiplyNode n) {
        n.left.accept(this);
        System.out.print(" * ");
        n.right.accept(this);
        return 0;
    }
}

// Usage: (3 + 4) * 2
AstNode tree = new MultiplyNode(
    new AddNode(new NumberNode(3), new NumberNode(4)),
    new NumberNode(2));

int result = tree.accept(new EvaluatorVisitor()); // 14
tree.accept(new PrettyPrintVisitor()); // (3 + 4) * 2
```

**Example 2 — Abstract base visitor (no-op defaults):**
```java
// Base visitor with default no-ops
// Subclasses only override what they care about
public abstract class AbstractAstVisitor implements AstVisitor {
    @Override public int visit(NumberNode n) { return 0; }
    @Override public int visit(AddNode n) { return 0; }
    @Override public int visit(MultiplyNode n) { return 0; }
}

// A pass that only validates number ranges
public class NumberRangeValidator extends AbstractAstVisitor {
    private final List<String> errors = new ArrayList<>();

    @Override
    public int visit(NumberNode n) {
        if (n.value < 0 || n.value > 1000) {
            errors.add("Out of range: " + n.value);
        }
        return 0;
    }
    // AddNode and MultiplyNode use no-op defaults

    public List<String> getErrors() { return errors; }
}
```

---

### ⚖️ Comparison Table

| Pattern | Open Axis | Coupling | Adding New Element | Adding New Operation |
|---|---|---|---|---|
| **Visitor** | Operations | Visitor↔Elements | Update all visitors | New class only |
| Strategy | Algorithms | Context↔Strategy | N/A | New class |
| Iterator | Traversal | Minimal | N/A | Modify traversal |
| Composite + overriding | Elements | Element hierarchy | New subclass | Modify all elements |

How to choose: use Visitor when element types are stable and operations grow frequently (compilers, document processing). Avoid Visitor when new element types are added often — each requires updating all visitors, which defeats the purpose.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Visitor requires modifying element classes often | Element classes implement `accept()` once and never change again; only adding new element types requires updating visitor interfaces |
| Visitor and Iterator solve the same problem | Iterator traverses elements sequentially; Visitor applies type-specific operations to each. They are often combined: Iterator traverses, Visitor operates |
| Visitor is only useful for trees or hierarchies | Visitor works on any collection of elements with different types — not just trees. A flat list of `Shape` objects processed by different geometry visitors is valid |
| Adding a new element type to Visitor is easy | It is NOT — it requires adding a `visit(NewType)` to every visitor class. This is the pattern's main cost |
| Java's instanceof chains are equivalent to Visitor | `instanceof` chains are not double-dispatched; the selection is in the caller, not in the element. Visitor's `accept()` ensures the correct method is called without any instanceof checks |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Visit Method for New Element Type**

**Symptom:** New `FunctionCall` AST node is added. Type checker silently skips all function calls. Generated code crashes at runtime.

**Root Cause:** `FunctionCall` was added to the element hierarchy without adding `visit(FunctionCall)` to the `Visitor` interface or any concrete visitors.

**Diagnostic:**
```bash
# Find all classes implementing Visitor
grep -rn "implements.*Visitor" src/ --include="*.java"
# Check each for visit(FunctionCall) method
grep -l "visit(FunctionCall" src/ --include="*.java"
# Missing = no output → visitors not updated
```

**Fix:**
Add `visit(FunctionCall)` to `Visitor` interface — this forces a compile error in all concrete visitors that don't implement it, surfacing the missing implementations immediately.

**Prevention:** Define the Visitor interface with ALL element types. Let the Java compiler enforce completeness — a compile error for missing `visit` methods is a safety net.

---

**2. Visitor Accumulates Incorrect State Across Nodes**

**Symptom:** Type checker visitor reports wrong types or reports errors for nodes it previously visited correctly.

**Root Cause:** Visitor instance is reused across multiple unrelated AST traversals. State from the first traversal (type table, error list) contaminates the second.

**Diagnostic:**
```java
// Check if visitor has instance fields that are not reset
TypeCheckVisitor visitor = new TypeCheckVisitor();
ast1.accept(visitor); // OK
ast2.accept(visitor); // contaminated by ast1's state!
```

**Fix:**
```java
// BAD: reuse visitor across different traversals
TypeCheckVisitor v = new TypeCheckVisitor();
for (Ast ast : asts) { ast.accept(v); } // state bleeds

// GOOD: fresh visitor per traversal
for (Ast ast : asts) {
    TypeCheckVisitor v = new TypeCheckVisitor();
    ast.accept(v);
    results.add(v.getResult());
}
```

**Prevention:** Document whether visitor instances are single-use or reusable. Prefer single-use visitors with a `reset()` method if reuse is needed.

---

**3. Infinite Recursion in Recursive Element Structures**

**Symptom:** `StackOverflowError` during visitor traversal of a deeply nested AST.

**Root Cause:** A cyclic element structure (graph, not tree) combined with a visitor that recurses without cycle detection.

**Diagnostic:**
```bash
# Check stack depth at StackOverflowError
jstack <PID> | grep "visit" | head -30
# Deep repeating pattern = recursion without base case
```

**Fix:**
```java
// Add visited-node tracking in visitor
public class CycleSafeVisitor implements AstVisitor {
    private final Set<AstNode> visited = new HashSet<>();

    @Override
    public int visit(AddNode n) {
        if (!visited.add(n)) return 0; // already visited
        return n.left.accept(this) + n.right.accept(this);
    }
}
```

**Prevention:** For graph-structured (not strictly tree-structured) elements, always add cycle detection to recursive visitors.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Double Dispatch` — the technical mechanism Visitor is built on; `element.accept(v)` + `v.visit(element)` implements double dispatch in single-dispatch languages
- `Open-Closed Principle` — Visitor realises OCP for the operations axis; adding operations (visitors) without modifying elements (open for extension, closed for modification)
- `Polymorphism` — both dispatches in Visitor use polymorphism; the pattern is polymorphism applied twice in sequence

**Builds On This (learn these next):**
- `Composite` — frequently combined with Visitor; Composite structures the element tree, Visitor traverses and operates on it
- `Interpreter` — uses element hierarchy for grammar rules; Visitor can apply different interpretations to the same grammar
- `Pattern Matching (Java 21+)` — sealed classes + switch expressions are an alternative to Visitor for closed hierarchies in modern Java

**Alternatives / Comparisons:**
- `Strategy` — also separates algorithm from structure, but works on a single object type, not a hierarchy
- `Iterator` — also traverses collections, but applies the same operation to each element; Visitor applies type-specific operations
- `Decorator` — wraps elements to add behaviour; Visitor operates on elements externally without wrapping them

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separate operations from object hierarchy;│
│              │ each operation = one visitor class        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Adding operations to fixed type hierarchy │
│ SOLVES       │ forces changes to all element classes     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Double dispatch: element type AND visitor │
│              │ type both resolved at runtime             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Element types stable; operations grow;    │
│              │ AST traversal, document processing        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Element types change often — new elements │
│              │ require updating every visitor            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Easy new operations vs expensive new      │
│              │ element types                             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Come in and do your work — I won't       │
│              │  change for you."                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Composite → Double Dispatch →             │
│              │ Pattern Matching (Java 21)                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A compiler team uses Visitor for 22 AST node types and 15 visitor passes. A new language feature requires adding 3 new AST node types: `LambdaExpression`, `TryCatch`, and `Yield`. Calculate exactly how many methods must be added across the codebase. Identify which of the 15 passes definitely need real implementations vs which can use no-ops, and describe how an abstract base visitor class changes this maintenance cost calculation.

**Q2.** Java 21 sealed classes allow exhaustive pattern matching in `switch` statements: `switch (node) { case IfStatement s -> ...; case WhileLoop w -> ...; }`. Compare this to Visitor for the operator of "add a new operation (e.g., a linter pass)." Then compare both approaches for the orthogonal operation of "add a new element type." In which dimension does each approach excel, and under what project conditions would you choose Visitor over sealed+switch in a new Java 21 codebase?

