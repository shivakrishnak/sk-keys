---
id: DPT-029
title: Visitor
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-014
used_by: DPT-064
related: DPT-014, DPT-028, DPT-019, DPT-027
tags:
  - pattern
  - behavioral
  - advanced
  - double-dispatch
  - ast
  - compiler
  - separation-of-concerns
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/design-patterns/visitor/
---

⚡ TL;DR - Visitor separates an algorithm from the object
structure it operates on - it lets you add new operations
to an existing class hierarchy without modifying the
classes, using double dispatch to call the right method
for each element type.

| #29 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-014 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-014, DPT-028, DPT-019, DPT-027 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A compiler has an AST (Abstract Syntax Tree) with 8 node
types: `LiteralNode`, `BinaryOpNode`, `UnaryOpNode`,
`AssignmentNode`, `IfNode`, `WhileNode`, `MethodCallNode`,
`ReturnNode`. Three operations needed: (1) type checking,
(2) code generation, (3) pretty printing.

**WITHOUT VISITOR:**
Each operation is added as a method to every AST node class.
8 classes x 3 operations = 24 method additions.
Adding a 4th operation (e.g., optimization pass): modify
all 8 AST node classes again. The AST nodes accumulate
unrelated concerns: type checking AND code generation AND
printing are all inside `IfNode`. The core data structure
becomes polluted with every analysis algorithm.

**THE BREAKING POINT:**
New operation (constant folding optimization): open all
8 files and add a `foldConstants()` method to each.
The core AST node classes become modification targets
for every new algorithm - violating OCP.

**THE INVENTION MOMENT:**
Visitor: each algorithm becomes a separate class:
`TypeCheckVisitor`, `CodeGenVisitor`, `PrintVisitor`.
Each AST node gets one method: `accept(Visitor v)`.
The `accept` method calls `v.visit(this)` - dispatching
to the correct `visit` overload in the visitor.
Adding constant folding: create `ConstantFoldVisitor`.
Zero changes to AST node classes.

**EVOLUTION:**
Java compiler uses Visitor for AST operations.
`javax.lang.model.element.ElementVisitor` in Java's
annotation processing API. Eclipse JDT's AST API uses
Visitor. Spring's `BeanDefinitionVisitor`. Checkstyle
and PMD code analysis tools walk AST nodes via Visitor.

---

### 📘 Textbook Definition

The **Visitor** pattern is a Behavioral design pattern
that represents an operation to be performed on elements
of an object structure. Visitor lets you define a new
operation without changing the classes of the elements
on which it operates. The pattern involves two hierarchies:
the Element hierarchy (object structure) and the Visitor
hierarchy (operations). Elements have an `accept(Visitor)`
method; Visitors have a `visit(ConcreteElement)` overload
for each element type. The critical mechanism is double
dispatch: `element.accept(visitor)` triggers `visitor.visit(element)`
dispatching on both the visitor type AND the element type.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Visitor lets you add new operations to a stable class
hierarchy without touching those classes - you put the
algorithm in a separate Visitor class.

**One analogy:**
> A tax inspector (Visitor) visits different types of
> business (Shop, Restaurant, Hotel - all elements). Each
> business type has different tax rules. The inspector
> applies the tax algorithm for the specific business type
> he visits. Adding a new inspector type (health inspector,
> fire inspector): create a new inspector. Zero changes
> to Shop, Restaurant, Hotel.

**One insight:**
The key challenge Visitor solves is the "expression
problem": in Java, adding new TYPES is easy (new class);
adding new OPERATIONS is hard (modify all existing classes).
Visitor flips this: adding new OPERATIONS is easy (new
Visitor class); adding new ELEMENT TYPES is hard
(requires updating all Visitors).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each Element has `accept(Visitor)` - this is the only
   method Visitor adds to the element hierarchy.
2. Each Visitor has `visit(ConcreteElementA)`, `visit(ConcreteElementB)`,
   etc. - one overload per concrete element type.
3. Double dispatch: `element.accept(visitor)` calls
   `visitor.visit(this)` inside the concrete element's
   `accept` - dispatching on both element type (via
   virtual dispatch) and visitor type (via overloading).

**THE EXPRESSION PROBLEM:**
- **Easy to add new Types**: add a new class implementing
  the interface - no changes elsewhere.
- **Easy to add new Operations**: add a new Visitor -
  no changes to element classes.
- Java (and most OOP languages) make Types easy. Visitor
  makes Operations easy - at the cost of making new
  element Types hard (must update all Visitors).

**DOUBLE DISPATCH MECHANISM:**
In single dispatch (normal Java method calls):
the method executed depends on the RUNTIME TYPE of
the RECEIVER ONLY.
```
visitor.visit(element) // one dispatch: on visitor type
// overload selected at COMPILE TIME based on
// declared type of element
```
Double dispatch:
```
element.accept(visitor)    // dispatch #1: on element type
  (virtual)
→ visitor.visit(this)      // dispatch #2: on visitor type
// 'this' has the CONCRETE element type at runtime
// correct visit() overload is selected
```

**TRADE-OFFS:**

**Gain:** Adding operations is easy (new Visitor class).
Operations are kept separate from data structures.
Related operations are grouped in one Visitor class.

**Cost:** Adding new element types is hard: every existing
Visitor must add a new `visit()` method. Breaks if the
element hierarchy is not stable. Requires an `accept()`
method in every element (invasive if the element hierarchy
is from a library).

---

### 🧪 Thought Experiment

**SETUP:**
Document structure: `Heading`, `Paragraph`, `Image`, `Table`
nodes. Operations needed: (1) word count, (2) export to HTML,
(3) export to PDF.

**WITHOUT VISITOR:**
Each node has `countWords()`, `toHtml()`, `toPdf()` methods.
Adding `toMarkdown()`: modify all 4 element classes.

**WITH VISITOR:**
`WordCountVisitor`, `HtmlExportVisitor`, `PdfExportVisitor`.
Adding `MarkdownExportVisitor`: one new class.
`Heading`, `Paragraph`, `Image`, `Table`: never change.

---

### 🧠 Mental Model / Analogy

> Visitor is a BUREAUCRAT who visits locations on a FORM.
> The form (Visitor) has a section for each location type:
> "For shops: [procedure A]. For restaurants: [procedure B].
> For warehouses: [procedure C]." Each location (Element)
> just opens the door (accept). The bureaucrat fills the
> right form section based on the location type. Adding
> a new bureaucrat (fire inspector, tax assessor): create
> a new form. Adding a new location type: update all forms.

- "Bureaucrat with a form" = ConcreteVisitor
- "Location opens the door" = accept(visitor)
- "Filling the right section" = visit(ConcreteElement)
- "Section for each location type" = visit() overloads
- "New bureaucrat type" = new Visitor (zero element changes)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Visitor lets you write new operations on a group of
objects without changing those objects. The objects
say "I accept visitors." Each visitor type knows what
to DO with each object type.

**Level 2 - How to use it (junior developer):**
Step 1: Add `accept(Visitor)` to every element in the
hierarchy - it calls `visitor.visit(this)`.
Step 2: Create a Visitor interface with a `visit()` overload
for each concrete element type.
Step 3: Implement one ConcreteVisitor class per operation.
The visitor's `visit(HeadingNode)` handles headings;
`visit(ParagraphNode)` handles paragraphs, etc.

**Level 3 - How it works (mid-level engineer):**
Java's `javax.lang.model` (annotation processing) uses
Visitor: `TypeVisitor<R, P>` has `visitPrimitive`,
`visitArray`, `visitDeclared`, `visitExecutable`, etc.
When writing an annotation processor, you extend
`SimpleTypeVisitor8` and override only the `visit*` methods
you care about. The processor framework calls `type.accept(visitor)`;
the type dispatches to the correct `visit*` method.
Every compiler plugin, code analysis tool (Checkstyle,
PMD, SpotBugs) walks the AST using Visitor - the AST
nodes never change; only the visitors implementing new
checks are added.

**Level 4 - Why it was designed this way (senior/staff):**
Visitor is the GoF's solution to the expression problem:
given a fixed set of types, add new operations without
modifying those types. When an AST has been carefully
designed and stabilized, adding a new analysis pass
(type checking, optimization, dead code elimination,
null analysis) should not require touching any AST node
class. Each pass is encapsulated in its own Visitor.
The `accept()` method is the one-time cost: once added
to each element, it never changes. The Visitor interface
grows with each new element type - this is the trade-off.
Systems that add element types frequently should not
use Visitor; systems that add operations frequently
(compilers, static analysis tools, document processors)
are ideal candidates.

**Level 5 - Mastery (distinguished engineer):**
Visitor is the pattern that exposes the "dual" of class
extension. In OOP: adding a new CLASS is cheap; adding
a new METHOD to existing classes is expensive. Visitor
inverts this by encoding algorithms (methods) in Visitor
classes instead of element classes. Functional languages
make Operations cheap (pattern matching on algebraic data
types) and Types expensive. Visitor brings functional-style
operation extension to OOP. Java 17's sealed classes and
`switch` expressions with pattern matching (`instanceof`
patterns) make the Visitor boilerplate unnecessary for
some cases:
```java
// Java 21 pattern matching switch = Visitor without accept()
double area = switch (shape) {
    case Circle c    -> Math.PI * c.radius() * c.radius();
    case Rectangle r -> r.width() * r.height();
    case Triangle t  -> 0.5 * t.base() * t.height();
};
```
Adding a new Shape requires updating all switches.
Adding a new operation: add a new switch expression.
Same trade-off as Visitor, zero boilerplate.

---

### ⚙️ How It Works (Mechanism)

```
Visitor Double Dispatch
┌─────────────────────────────────────────────────────────┐
│ <<interface>> AstVisitor                                │
│   visit(LiteralNode n): void                            │
│   visit(BinaryOpNode n): void                           │
│   visit(IfNode n): void                                 │
│                                                         │
│ TypeCheckVisitor implements AstVisitor                  │
│   visit(LiteralNode n)  { ... type checking logic ... } │
│   visit(BinaryOpNode n) { ... type inference ... }      │
│   visit(IfNode n)       { ... condition must be bool ...│
│                                                         │
│ CodeGenVisitor implements AstVisitor                    │
│   visit(LiteralNode n)  { ... emit LOAD_CONST ... }     │
│   visit(BinaryOpNode n) { ... emit ADD/MUL ... }        │
│   visit(IfNode n)       { ... emit JMP_IF_FALSE ... }   │
│                                                         │
│ <<interface>> AstNode                                   │
│   accept(AstVisitor v): void                            │
│                                                         │
│ LiteralNode implements AstNode                          │
│   accept(AstVisitor v) { v.visit(this); }  ← dispatch 2 │
│                                                         │
│ IfNode implements AstNode                               │
│   accept(AstVisitor v) {                                │
│       v.visit(this);                       ← dispatch 2 │
│       condition.accept(v);                 ← recurse    │
│       thenBranch.accept(v);                             │
│       if (elseBranch != null) elseBranch.accept(v);     │
│   }                                                     │
│                                                         │
│ CALL: node.accept(typeCheckVisitor)        ← dispatch 1 │
│ → LiteralNode.accept(v) → v.visit(this)                 │
│ → TypeCheckVisitor.visit(LiteralNode)      ← dispatch 2 │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
source code → Parser → AST
AST = IfNode(
  condition: BinaryOpNode(LiteralNode(5), ">",
    LiteralNode(3)),
  thenBranch: AssignmentNode(...)
)

TypeCheckVisitor v = new TypeCheckVisitor(symbolTable);

ast.accept(v)                     // dispatch 1: IfNode
  → IfNode.accept(v)              // virtual dispatch
  → v.visit(this: IfNode)         // dispatch 2:
    TypeCheckVisitor
  → TypeCheckVisitor.visit(IfNode):
      condition.accept(v)         // recurse into condition
        → BinaryOpNode.accept(v)
        → v.visit(this: BinaryOpNode)
        → TypeCheckVisitor.visit(BinaryOpNode):
            left.accept(v)        // recurse left
              → v.visit(LiteralNode) → type is Integer
            right.accept(v)
              → v.visit(LiteralNode) → type is Integer
            check: operator ">" on Integer, Integer →
              Boolean ok
      check: condition type is Boolean ok

Adding optimization pass:
ConstantFoldVisitor fold = new ConstantFoldVisitor();
ast.accept(fold)
// TypeCheckVisitor, BinaryOpNode, IfNode: UNCHANGED
```

---

### 💻 Code Example

**Example 1 - Without Visitor (operations in element classes):**

```java
// BAD: operations pollute element classes
abstract class DocumentNode {
    abstract int wordCount();     // operation 1
    abstract String toHtml();     // operation 2
    abstract String toPdf();      // operation 3
    // Adding operation 4: modify ALL element classes
}

class Heading extends DocumentNode {
    String text;
    int level;

    @Override
    int wordCount() { return text.split(" ").length; }

    @Override
    String toHtml() {
        return "<h" + level + ">" + text + "</h" + level + ">";
    }

    @Override
    String toPdf() { return "[H" + level + "] " + text + "\n"; }
    // Adding toMarkdown(): modify THIS class
}
```

**Example 2 - Visitor solution:**

```java
// GOOD: operations extracted to Visitor classes

// ELEMENT interface - only accept() added to element hierarchy
interface DocumentNode {
    void accept(DocumentVisitor visitor);
}

// VISITOR interface - one visit() per concrete element type
interface DocumentVisitor {
    void visit(Heading h);
    void visit(Paragraph p);
    void visit(ImageNode img);
    void visit(TableNode t);
}

// ELEMENT implementations - contain ONLY their data
class Heading implements DocumentNode {
    String text;
    int level;

    Heading(int level, String text) {
        this.level = level;
        this.text = text;
    }

    @Override
    public void accept(DocumentVisitor v) {
        v.visit(this); // double dispatch: this = Heading
    }
}

class Paragraph implements DocumentNode {
    String text;

    @Override
    public void accept(DocumentVisitor v) {
        v.visit(this); // this = Paragraph
    }
}

// VISITOR implementations - one class per operation
class WordCountVisitor implements DocumentVisitor {
    private int count = 0;

    @Override
    public void visit(Heading h) {
        count += h.text.split("\\s+").length;
    }

    @Override
    public void visit(Paragraph p) {
        count += p.text.split("\\s+").length;
    }

    @Override
    public void visit(ImageNode img) { /* images: 0 words */ }

    @Override
    public void visit(TableNode t) {
        t.cells.forEach(row -> row.forEach(cell ->
            count += cell.split("\\s+").length));
    }

    int getCount() { return count; }
}

class HtmlExportVisitor implements DocumentVisitor {
    private final StringBuilder sb = new StringBuilder();

    @Override
    public void visit(Heading h) {
        sb.append("<h").append(h.level).append(">")
          .append(h.text)
          .append("</h").append(h.level).append(">\n");
    }

    @Override
    public void visit(Paragraph p) {
        sb.append("<p>").append(p.text).append("</p>\n");
    }

    @Override
    public void visit(ImageNode img) {
        sb.append("<img src=\"").append(img.src).append("\"/>\n");
    }

    @Override
    public void visit(TableNode t) { /* ... table HTML ... */ }

    String getHtml() { return sb.toString(); }
}

// USAGE: same elements, different operations
List<DocumentNode> doc = getDocument();

// Word count operation
WordCountVisitor wc = new WordCountVisitor();
doc.forEach(node -> node.accept(wc));
int total = wc.getCount();

// HTML export operation
HtmlExportVisitor html = new HtmlExportVisitor();
doc.forEach(node -> node.accept(html));
String output = html.getHtml();

// Adding Markdown export: ONE new class
class MarkdownExportVisitor implements DocumentVisitor {
    // visit(Heading), visit(Paragraph), etc.
}
// Heading, Paragraph, ImageNode, TableNode: UNCHANGED
```

**Example 3 - Java's annotation processing (real Visitor):**

```java
// RECOGNITION: javax.lang.model.type.TypeVisitor

// Spring uses similar patterns to process bean types
class TypeScanVisitor extends SimpleTypeVisitor8<String, Void> {
    @Override
    public String visitPrimitive(PrimitiveType t, Void p) {
        return t.getKind().name().toLowerCase();
    }

    @Override
    public String visitArray(ArrayType t, Void p) {
        return visit(t.getComponentType()) + "[]";
    }

    @Override
    public String visitDeclared(DeclaredType t, Void p) {
        TypeElement elem = (TypeElement) t.asElement();
        return elem.getSimpleName().toString();
    }
}

// Annotation processor (framework calls element.accept):
TypeMirror type = element.asType();
String typeName = type.accept(new TypeScanVisitor(), null);
// double dispatch: TypeMirror.accept → visitor.visit(this)
```

---

### ⚖️ Comparison Table

| Aspect | Visitor | Iterator | Decorator |
|---|---|---|---|
| Applies to | Heterogeneous object structure | Homogeneous collection | Single object |
| Operations | Adds new operations externally | Single traversal operation | Wraps behavior |
| New operation cost | New Visitor class | N/A | New Decorator |
| New type cost | Update all Visitors | N/A | Transparent |
| Double dispatch | Yes | No | No |

**Use Visitor when:**
- Object structure is STABLE but operations are added frequently
- Operations on heterogeneous element types (each type
  has different logic)
- Operations need to be grouped per-algorithm (not per-element)

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Visitor is just "walking an object tree" | Walking an object tree is TRAVERSAL (Iterator, Composite's `accept` recursion). The defining feature of Visitor is DOUBLE DISPATCH - the algorithm is in the Visitor class, not the element. Without double dispatch, it's just a tree walk |
| Adding a new element type is easy with Visitor | This is actually the HARD part of Visitor. Adding a new element type requires adding a new `visit(NewElement)` method to EVERY existing Visitor. This is why Visitor is only suitable for stable element hierarchies |
| Visitor is always better than instanceof chains | For small, stable hierarchies, a well-named visitor adds boilerplate. Java 21 sealed classes + switch expressions can be cleaner. Visitor pays off when you have many visitors against a stable element set |
| Visitor requires modifying element classes | YES - you must add `accept(Visitor)` to every element. If the element classes are from a third-party library and cannot be modified, Visitor cannot be applied (use the reflection-based "Acyclic Visitor" variant instead) |

---

### 🚨 Failure Modes & Diagnosis

**New Element Type Added Without Updating All Visitors**

**Symptom:**
`AbstractMethodError` or compilation error when a new
`VideoNode` is added to the document hierarchy and a
Visitor interface adds `visit(VideoNode)`. The existing
`WordCountVisitor` and `HtmlExportVisitor` do not compile
because they do not implement the new method.

**Root Cause:**
Visitor's inherent trade-off: adding a new element type
requires updating every Visitor. This is compile-time
enforced when the new `visit()` method is added to the
interface - a compile error stops deployment until all
Visitors are updated.

**Diagnosis:**
Compile errors: `Class HtmlExportVisitor does not implement
abstract method visit(VideoNode)`.

**Fix:**
Add `visit(VideoNode)` to all concrete Visitors:
```java
// Option 1: required - proper implementation in each visitor
class WordCountVisitor implements DocumentVisitor {
    @Override
    public void visit(VideoNode v) {
        count += v.caption.split("\\s+").length;
    }
}

// Option 2: use adapter/abstract base visitor with defaults
abstract class AbstractDocumentVisitor implements DocumentVisitor {
    @Override
    public void visit(VideoNode v) { /* no-op default */ }
    // Subclass only overrides what it cares about
}
```

---

**Visitor Holding Mutable State in Concurrent Walk**

**Symptom:**
`WordCountVisitor` running concurrently on two document
threads returns incorrect word counts. Visitors are
shared across threads.

**Root Cause:**
Visitors accumulate state (`count` field in `WordCountVisitor`).
If a visitor instance is shared across threads without
synchronization, state is corrupted.

**Fix:**
Create a new Visitor instance per operation, never share:
```java
// BAD: shared visitor (mutable state corrupted)
private final WordCountVisitor sharedWC = new WordCountVisitor();

// GOOD: new visitor per operation
int count = document.stream()
    .reduce(0, (acc, node) -> {
        WordCountVisitor wc = new WordCountVisitor(); // per-call
        node.accept(wc);
        return acc + wc.getCount();
    }, Integer::sum);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Composite` - DPT-014; Visitor is most commonly applied
  to Composite (tree) structures; understanding Composite's
  recursive structure helps understand Visitor traversal

**Builds On This (learn these next):**
- `Pattern Selection Framework` - DPT-061; Visitor vs
  iterator vs decorator decision framework

**Alternatives / Comparisons:**
- `Iterator` - traversal without operation dispatch; simpler
- `Strategy` - single algorithm family; Visitor handles
  heterogeneous element types

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Add operations to stable class hierarchy │
│              │ without modifying the classes            │
├──────────────┼──────────────────────────────────────────┤
│ MECHANISM    │ Double dispatch:                         │
│              │ element.accept(v) → v.visit(this)        │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Java annotation processing TypeVisitor;  │
│              │ compiler AST analysis passes             │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Easy to add Operations (new Visitor);    │
│              │ Hard to add Element Types (update all)   │
├──────────────┼──────────────────────────────────────────┤
│ JAVA 21      │ Sealed classes + switch = Visitor without│
│              │ accept() boilerplate                     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Null Object → Double-Checked Locking     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Double dispatch: `element.accept(visitor)` calls
   `visitor.visit(this)` - dispatches on BOTH the element
   type (virtual method) and the visitor type (overloading).
   Single dispatch (normal Java) dispatches only on the
   receiver type.
2. Visitor trade-off: easy to add Operations (new Visitor
   class, zero element changes), hard to add new Element
   Types (all Visitors must add a new `visit()` method).
   Use Visitor only for stable element hierarchies.
3. Java 21 sealed classes + pattern matching `switch` are
   the modern alternative to Visitor for many cases -
   the same trade-off applies but without `accept()` boilerplate.

**Interview one-liner:**
"Visitor separates operations from the object structure
by placing each algorithm in a Visitor class with one
`visit()` method per element type. Double dispatch -
`element.accept(v)` triggering `v.visit(this)` - ensures
the right visitor method is called for each element type.
The trade-off: adding operations is easy (new Visitor class),
but adding element types is expensive (every Visitor needs
a new method). Java's annotation processing TypeVisitor
is the canonical real-world example."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Explain double dispatch: why `visitor.visit(element)`
   alone does NOT achieve Visitor pattern and why
   `element.accept(v)` → `v.visit(this)` is required
2. [IMPLEMENT] Implement a 3-element, 2-operation Visitor
   pattern from scratch: element hierarchy, Visitor interface,
   two ConcreteVisitors, traversal with accept/visit
3. [EVALUATE] Given a class hierarchy, explain whether
   Visitor is appropriate or whether the element types
   are too unstable for the pattern to be maintainable
4. [CONNECT] Explain why Java 21's sealed classes + switch
   pattern matching can replace Visitor for some cases -
   and when the classic Visitor is still preferable

