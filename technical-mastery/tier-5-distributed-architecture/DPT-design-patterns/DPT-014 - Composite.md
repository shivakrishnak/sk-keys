---
id: DPT-014
title: Composite
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005
used_by: DPT-019, DPT-040
related: DPT-015, DPT-019, DPT-022, DPT-029
tags:
  - pattern
  - structural
  - intermediate
  - tree-structure
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/design-patterns/composite/
---

⚡ TL;DR - Composite lets you treat individual objects and
groups of objects through the same interface - enabling
recursive tree structures where a group IS-A member of
the same type it contains.

| #14 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005 | |
| **Used by:** | DPT-019, DPT-040 | |
| **Related:** | DPT-015, DPT-019, DPT-022, DPT-029 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A file system: folders contain files AND other folders.
When you compute the total size of a folder, you need to:
iterate over its contents, check if each item is a File
(compute its size directly) or a Folder (recursively sum
its contents). Every algorithm that operates on the file
system must contain this `if (isFile) ... else (isFolder
recurse...)` logic explicitly.

**THE BREAKING POINT:**
A file viewer, a search, a copy operation, a delete
operation, a permissions scanner - each one must independently
implement the "is it a file or folder?" branching. Adding
a new item type (symbolic link, mount point) requires
modifying every algorithm that processes the tree.

**THE INVENTION MOMENT:**
Composite: define an interface that both File and Folder
implement. The key method (e.g., `size()`) is on the
INTERFACE. `File.size()` returns its own size. `Folder
.size()` recursively sums `child.size()` for all children.
Every algorithm calls `item.size()` - it never asks "file
or folder?" The recursion is INSIDE the data structure,
not in every algorithm.

**EVOLUTION:**
Composite is fundamental to tree processing. UI widget
hierarchies (a Panel contains Buttons and other Panels),
expression trees in compilers, organization hierarchies,
menu systems, bill-of-materials in manufacturing - all
use Composite to enable uniform traversal of tree structures.

---

### 📘 Textbook Definition

The **Composite** pattern is a Structural design pattern
that composes objects into tree structures to represent
part-whole hierarchies. Composite lets clients treat
individual objects (Leaf nodes) and compositions of objects
(Composite nodes) uniformly through a common interface.
The Composite node implements the Component interface AND
maintains a collection of Component children - meaning the
same operations that work on leaves also work on composites,
and composites may contain other composites recursively.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Composite lets you treat a single item and a group of items
exactly the same way - by giving them the same interface.

**One analogy:**
> An org chart: a `Person` (Leaf) has a salary. A
> `Department` (Composite) also has a "salary" - the sum
> of all its members' salaries. Both Person and Department
> implement `getTotalCost()`. Computing the cost of any
> department - no matter how deeply nested - is just
> `department.getTotalCost()`. No "is it a person or a
> department?" check anywhere.

**One insight:**
Composite's insight is that the CONTAINER and the CONTAINED
speak the same language (interface). This means recursive
tree structures are traversed with zero type-checking code
in the algorithms that use them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Leaf and Composite implement the same `Component` interface.
2. Composite holds a collection of `Component` children
   (which may be Leaves or other Composites).
3. Every operation on Component is implemented by both
   Leaf (concretely) and Composite (by delegating to children).

**DERIVED DESIGN:**
Three participants:
- **Component**: the common interface; declares operations
  that apply to both leaves and composites
- **Leaf**: has no children; implements Component directly;
  defines behavior for primitive objects
- **Composite**: has children; implements Component by
  iterating over children and delegating; manages
  child addition/removal

**DESIGN DECISION - WHERE TO PUT CHILD MANAGEMENT:**
Option A: Child management (`add()`, `remove()`, `getChildren()`)
in Component interface - maximum uniformity (client can
add children to any Component). Cost: Leaf must implement
or reject these methods.
Option B: Child management only in Composite - type-safety
(no Leaf.add() confusion). Cost: clients must distinguish
Leaf from Composite when building the tree.

GoF recommends Option A for maximum transparency (clients
never distinguish Leaf and Composite). Modern practice
often prefers Option B for type-safety - the Composite
pattern's intent is preserved either way.

**TRADE-OFFS:**

**Gain:** Uniform interface for tree traversal. No
type-checking in algorithms. Adding new Leaf types does
not affect existing algorithms.

**Cost:** Harder to RESTRICT what children a composite
can contain (any Component can be added to any Composite).
Over-general trees can contain unexpected combinations.

---

### 🧪 Thought Experiment

**SETUP:**
An expression evaluator. Expressions are trees:
`(3 + 4) * (2 - 1)` is a tree with `*` at root, `+` and
`-` as subtrees, and numbers as leaves.

**WITHOUT COMPOSITE:**
```
evaluate(node):
  if (node is Number) return node.value
  if (node is Add) return evaluate(node.left) +
    evaluate(node.right)
  if (node is Multiply) return evaluate(node.left) *
    evaluate(node.right)
```
Every algorithm (evaluate, print, optimize) must enumerate
all possible node types and recurse manually.

**WITH COMPOSITE:**
```java
interface Expr { int evaluate(); }
class Number implements Expr { int evaluate() { return value; }}
class Add implements Expr {
    int evaluate() { return left.evaluate() + right.evaluate(); }
}
class Multiply implements Expr {
    int evaluate() { return left.evaluate() * right.evaluate(); }
}
```
Every algorithm just calls `expr.evaluate()`. Adding a new
operator (Subtract): one new class, zero changes to any
algorithm.

**THE INSIGHT:**
Composite moves the "what type is this node?" question
OUT of the algorithms and INTO the node classes themselves.
Each node knows how to perform the operation; the algorithm
just asks.

---

### 🧠 Mental Model / Analogy

> Composite is a RUSSIAN DOLL (Matryoshka) pattern. Each
> doll has a "how big are you?" operation. The innermost
> doll answers directly. Every outer doll answers: "I am
> the size of all the dolls inside me combined." You ask
> the outermost doll its size and get the total - you never
> open each doll individually from outside.

- "How big are you?" = the Component interface operation
- "Innermost doll" = Leaf
- "Outer doll" = Composite
- "Dolls inside me" = children
- "You, asking" = client code

**Where this analogy breaks down:**
Russian dolls are always nested linearly. Composite trees
can have multiple children at each level (branching trees).
The doll analogy captures depth but not breadth.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Composite makes a single thing and a group of things look
the same. You call the same method whether you have one
item or a million items in a tree, and it "just works."

**Level 2 - How to use it (junior developer):**
Create a Component interface with the operations needed.
Leaf class implements it directly. Composite class
implements it by iterating over its children and combining
their results. The key: Composite holds a `List<Component>`,
not a `List<Leaf>` - so children can be Leaves OR other
Composites.

**Level 3 - How it works (mid-level engineer):**
Composite is the correct pattern for any tree data structure
where the same algorithm applies to every node regardless
of whether it is a leaf or an internal node. The recursion
is structural - it follows the tree structure automatically.
This means implementing a new tree operation (a new method
on Component) requires adding it to the Component interface,
implementing it in Leaf, implementing it in Composite (as
a delegation to children). No algorithm needs to know
about tree structure - the tree knows how to traverse itself.

**Level 4 - Why it was designed this way (senior/staff):**
Composite is the canonical structural pattern for the
Open/Closed Principle on tree-structured data. It is closed
for modification (existing algorithms do not change when
new Leaf types are added) and open for extension (new Leaf
types automatically work with all existing algorithms).
The pattern reflects the principle that data structures
should know how to perform operations on themselves,
not expose their structure to algorithms.

**Level 5 - Mastery (distinguished engineer):**
Composite and Visitor are the two complementary patterns
for tree processing. Composite is preferred when the
number of tree operations is stable and new node types
are added frequently (OCP on node types). Visitor is
preferred when the number of node types is stable and
new operations on the tree are added frequently (OCP on
operations). The choice between them is a fundamental
architectural decision. React's component tree, the DOM,
Spring's Bean Definition hierarchy, and JVM bytecode
instruction sets all use Composite - but expression trees
in compilers often use Visitor for its operation extensibility.

---

### ⚙️ How It Works (Mechanism)

```
Composite Tree Structure
┌─────────────────────────────────────────────────────────┐
│  <<interface>> Component                                │
│  + size(): long                                         │
│  + (optional: add/remove for Composite variant)         │
│         ▲                       ▲                       │
│  Leaf (File)            Composite (Folder)              │
│  - data: byte[]         - children: List<Component>     │
│  + size(): long         + size(): long                  │
│    return data.length     long s = 0;                   │
│                           for (c : children)            │
│                             s += c.size();  ← recurse   │
│                           return s;                     │
│                         + add(Component c)              │
│                         + remove(Component c)           │
│                                                         │
│  Example tree:                                          │
│  root (Folder)                                          │
│    ├── file1 (Leaf)     size=100                        │
│    ├── subdir (Folder)                                  │
│    │   ├── file2 (Leaf) size=200                        │
│    │   └── file3 (Leaf) size=50                         │
│    └── file4 (Leaf)     size=75                         │
│                                                         │
│  root.size() → 100 + subdir.size() + 75                 │
│               = 100 + (200+50) + 75 = 425               │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client calls root.size()
  → Composite.size(): iterate children
    → file1.size(): return 100 (Leaf)
    → subdir.size(): iterate subdir children
      → file2.size(): return 200 (Leaf)
      → file3.size(): return 50 (Leaf)
      ← subdir returns 250
    → file4.size(): return 75 (Leaf)
  ← root returns 100 + 250 + 75 = 425
Client receives 425, never knowing the tree structure
```

**FAILURE PATH:**
```
Circular reference in tree:
  dirA.add(dirB); dirB.add(dirA);
  dirA.size() → recurses forever → StackOverflowError
Detection: track visited nodes in a Set during traversal
Prevention: validate no cycles when add() is called
```

**WHAT CHANGES AT SCALE:**
Deep trees (thousands of levels) risk stack overflow in
recursive traversal. Solution: iterative traversal with
an explicit stack (Deque). Wide trees (millions of
children) require lazy traversal (Stream-based) rather
than eager traversal. Very large trees may benefit from
memoization: cache each Composite's computed value and
invalidate when children change.

---

### 💻 Code Example

**Example 1 - Without Composite (type-checking in algorithms):**

```java
// BAD: every algorithm must type-check nodes
class FileSystemUtils {
    static long totalSize(Object item) {
        if (item instanceof File) {
            return ((File) item).getBytes().length;
        } else if (item instanceof Folder) {
            Folder folder = (Folder) item;
            long sum = 0;
            for (Object child : folder.getContents()) {
                sum += totalSize(child); // recursive, but explicit
            }
            return sum;
        }
        throw new IllegalArgumentException("Unknown type: " + item);
    }
    // Adding SymLink: must modify totalSize() and every other
    // algorithm
}
```

**Example 2 - Composite solution:**

```java
// GOOD: Composite - same interface for File and Folder

// Component: common interface
interface FileSystemNode {
    String name();
    long size();
}

// Leaf
class File implements FileSystemNode {
    private final String name;
    private final byte[] content;

    File(String name, byte[] content) {
        this.name = name;
        this.content = content;
    }

    public String name() { return name; }
    public long size() { return content.length; } // direct answer
}

// Composite
class Folder implements FileSystemNode {
    private final String name;
    // Key: List<FileSystemNode> not List<File>
    private final List<FileSystemNode> children = new ArrayList<>();

    Folder(String name) { this.name = name; }

    public void add(FileSystemNode node) { children.add(node); }
    public void remove(FileSystemNode node) { children.remove(node); }

    public String name() { return name; }

    public long size() { // delegates to children
        return children.stream()
                       .mapToLong(FileSystemNode::size)
                       .sum();
    }
}

// Algorithm: zero type-checking needed
class FileSystemUtils {
    static void printTree(FileSystemNode node, int depth) {
        System.out.println("  ".repeat(depth) + node.name()
            + " (" + node.size() + " bytes)");
        // Adding SymLink: implement FileSystemNode, done
        if (node instanceof Folder f) {
            f.children().forEach(c -> printTree(c, depth + 1));
        }
    }
}

// Building the tree:
Folder root = new Folder("root");
root.add(new File("readme.txt", "Hello".getBytes()));
Folder src = new Folder("src");
src.add(new File("Main.java", new byte[2048]));
src.add(new File("Utils.java", new byte[1024]));
root.add(src);

System.out.println(root.size()); // 5 + 2048 + 1024 = 3077
```

**Example 3 - Composite in Spring Web MVC:**

```java
// RECOGNITION: Spring's CompositeFilter is Composite pattern
// javax.servlet.Filter is the Component interface
// Individual filters are Leaf nodes
// CompositeFilter composes them into a chain

// Spring Security's FilterChainProxy IS Composite:
// It holds a list of SecurityFilterChain (each is a Composite
// of individual security filters). Applying security to a
// request: filterChainProxy.doFilter() iterates the matching
// chain, each filter.doFilter() applies its logic.
// The caller (servlet container) just calls doFilter() on
// the proxy - never knows about the internal tree.
```

**How to test/verify correctness:**
Test Leaf operations directly. Test Composite with a small
tree (1 level, 2 levels). Test deeply nested trees for
correct accumulation. Test edge cases: empty Composite
(returns zero/empty for operations), single-child Composite.
Test with a mock Leaf to verify Composite delegates correctly.

---

### ⚖️ Comparison Table

| Pattern      | Tree structure | Uniform interface | Operation location | New ops |
| ------------ | -------------- | ----------------- | ------------------ | ------- |
| **Composite**| Yes            | Yes               | In each node class | Change all nodes |
| Visitor      | Yes            | Interface only    | In Visitor class   | Add Visitor class|
| Iterator     | Yes (traversal)| Yes (traversal)   | External           | Change iterator |

**How to choose:**
- Operations stable, node types grow? Composite
- Node types stable, operations grow? Visitor
- Need external traversal (lazy, multiple orders)? Iterator
- Composite + Visitor is a common combo: Composite defines
  the tree structure; Visitor adds operations to it

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Composite is only for file systems | Composite applies to any part-whole hierarchy: UI widgets, org charts, expression trees, menu systems, bill-of-materials, JSON/XML document structure |
| Child management should be in the Component interface | This is a GoF preference for transparency; type-safe approach puts child management only in Composite - both are valid; choose based on whether client code distinguishes Leaf from Composite |
| Composite pattern requires parent references | Parent references are optional; they are needed only when upward traversal is required (e.g., "find the containing folder") |
| Composite and Tree are the same thing | A Tree is a data structure; Composite is a design pattern for how operations on a tree are defined and executed. You can have a tree without Composite (with type-checking) |
| Leaf nodes must be immutable | Leaf nodes CAN be mutable; immutability is a separate design concern from the Composite pattern |

---

### 🚨 Failure Modes & Diagnosis

**Circular Reference StackOverflow**

**Symptom:**
`StackOverflowError` in `size()` or any recursive tree
operation. Stack trace shows hundreds of alternating
`Folder.size()` calls.

**Root Cause:**
Two Composite nodes contain each other as children:
`dirA.add(dirB); dirB.add(dirA)`. Every recursive traversal
loops infinitely.

**Diagnostic Signal:**
`StackOverflowError` in any Composite recursive operation.
Log the nodes visited; detect repeated node identities.

**Fix:**
```java
// GOOD: cycle detection during traversal
public long size(Set<FileSystemNode> visited) {
    if (!visited.add(this))
        throw new IllegalStateException(
            "Cycle detected at: " + name);
    return children.stream()
        .mapToLong(c -> {
            if (c instanceof Folder f)
                return f.size(visited);
            return c.size();
        }).sum();
}
```

**Prevention:**
Validate no cycles in `add()`: traverse the new child's
subtree looking for `this`. Reject if found.
Or: prohibit parent references in children entirely by
validating that the added child does not already have
a parent in the tree.

---

**Operation Semantics Differ Between Leaf and Composite**

**Symptom:**
`delete()` on a File removes the file. `delete()` on a
Folder deletes the folder and all its contents. The
uniform interface hides that the operations have
semantically very different consequences, and a caller
deletes a folder believing it was deleting a single file.

**Root Cause:**
The uniform interface is too permissive - dangerous
operations that behave differently at different levels
should not be uniformly accessible without confirmation
or explicit acknowledgment of the composite nature.

**Diagnostic Signal:**
Ask: "Does the same method name have meaningfully different
consequences for Leaf vs Composite?" If yes: the operation
should not be uniformly hidden.

**Fix:**
Add a `isLeaf(): boolean` method or mark Composite operations
with explicit warnings in documentation. For truly dangerous
operations: require callers to call `node.getType() ==
NodeType.FOLDER` before deleting, making the composite
nature explicit.

**Prevention:**
Uniform interface is best applied to READ operations
(size, name, path) that aggregate naturally. WRITE operations
(delete, move, chmod) often have non-uniform consequences
and may benefit from explicit type distinction.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Are Design Patterns and Why They Exist` - vocabulary
  foundation; Composite is one of the clearest pattern examples

**Builds On This (learn these next):**
- `Visitor` - the complementary pattern: Composite defines
  tree structure; Visitor adds operations to an existing tree
- `Iterator` - the traversal pattern; Composite trees are
  often traversed with Iterator (depth-first, breadth-first)

**Alternatives / Comparisons:**
- `Visitor` - trade-off: Composite for new node types,
  Visitor for new operations; decide which changes more
- `Decorator` - also wraps a Component, but Decorator is
  for behavior addition on linear chains, Composite is for
  tree structures

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Uniform interface for Leaf and Composite │
│              │ nodes in a part-whole tree hierarchy     │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Type-checking in every algorithm that    │
│ SOLVES       │ traverses a tree of heterogeneous nodes  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Composite IS-A Component (same interface)│
│              │ AND HAS-A collection of Components       │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Tree structure where same ops apply to   │
│              │ individual and grouped objects           │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Circular references → StackOverflowError │
│              │ in recursive traversal                   │
├──────────────┼──────────────────────────────────────────┤
│ VS VISITOR   │ Composite: new node types = easy (OCP)   │
│              │ Visitor: new operations = easy (OCP)     │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ DOM tree, Swing container hierarchy,     │
│              │ Spring Security FilterChainProxy         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Decorator → Visitor → Iterator           │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Composite IS-A Component AND HAS-A list of Components -
   this self-referential relationship is the structural
   definition of the pattern
2. The recursion is IN THE DATA STRUCTURE, not in the
   calling code - `folder.size()` calls `child.size()` for
   each child; the algorithm never asks "is it a file or
   folder?"
3. Composite vs Visitor trade-off: Composite is OCP for
   new node TYPES; Visitor is OCP for new OPERATIONS -
   choose based on which will change more frequently

**Interview one-liner:**
"Composite creates a tree where Leaf and Composite nodes
share the same interface, letting clients treat individual
objects and groups uniformly. The Composite node delegates
operations to its children recursively. The DOM, Swing
containers, and Spring Security's filter chain are canonical
examples. The key trade-off vs Visitor: Composite is OCP
for new node types; Visitor is OCP for new operations."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a hierarchy is RECURSIVE (the container and contained
are the same type of thing conceptually), give them the
same interface. The recursion then lives in the data, not
in the algorithms. This makes the algorithms clean, simple,
and unaffected by tree structure changes.

**Where else this pattern appears:**
- **DOM (Document Object Model)** - `Node` is the Component;
  `Text`, `Comment`, `CDATASection` are Leaves; `Element`,
  `Document`, `DocumentFragment` are Composites; every DOM
  traversal API treats all nodes uniformly through the
  Node interface
- **Swing UI hierarchy** - `java.awt.Component` is the
  Component interface; buttons, labels are Leaves;
  `Container` (JPanel, JFrame) is the Composite; `paint()`
  recursively paints the entire widget tree
- **Spring Security FilterChainProxy** - each request
  passes through a chain of filters; the chain IS a
  Composite; `SecurityFilterChain` is the Component

**Industry applications:**
- **JSON/XML processing** - JsonNode (Jackson), JsonElement
  (Gson) use Composite: primitive nodes are Leaves; objects
  and arrays are Composites; traversal and transformation
  work uniformly via the JsonNode API
- **Build system task trees** - Gradle's task dependency
  tree, Maven's lifecycle phases - each is a Composite of
  tasks where execution means recursively executing all
  dependencies before the task itself

---

### 💡 The Surprising Truth

Java's own `java.awt.Component` and `java.awt.Container`
were designed with a deliberate Composite asymmetry that
the GoF acknowledge as a known pattern variant: `Component`
is the abstract base; `Container` extends `Component` (is
a Component) AND contains Components. This means child
management is in `Container`, not in `Component` - a
type-safe Composite variant. But here is the surprise:
for over a decade, programmers routinely called
`container.add(new JButton())` and `container.add(new
JPanel())` - adding both Leaves and nested Composites to
the same container - using Composite's core feature
(heterogeneous tree) without knowing the pattern name.
Composite is so embedded in UI programming that it feels
natural - it is not a clever abstraction, it IS the
correct model for any recursive part-whole structure.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] State the Composite self-reference: "Composite
   IS-A Component AND HAS-A List<Component>" and explain
   why this recursive definition enables uniform tree
   traversal
2. [BUILD] Implement a simple expression tree (Number leaf,
   Add composite, Multiply composite) with `evaluate()` as
   the Component interface method, demonstrating zero
   type-checking in any algorithm
3. [DIAGNOSE] Given a `StackOverflowError` in a recursive
   Composite tree operation, identify circular reference as
   the cause and implement cycle detection using a visited Set
4. [COMPARE] Explain the Composite vs Visitor trade-off in
   the context of a compiler's AST: when to choose each
   and what changes when the choice is made
5. [RECOGNIZE] Identify Composite in Spring Security's filter
   chain: name the Component interface, the Leaf, and the
   Composite and explain how `doFilter()` is delegated

---

### 🧠 Think About This Before We Continue

**Q1.** Consider an expression tree using Composite where
`evaluate()` is on the Component interface. Adding a new
operation (e.g., `prettyPrint()`) requires adding a new
method to the Component interface AND implementing it in
EVERY node class. This is the Composite trade-off. Now
consider using Visitor for the same tree: adding a new
operation means adding one Visitor class. However, adding
a new node type (e.g., `TernaryOp`) requires modifying
EVERY visitor. Formalize the trade-off: when would a
compiler team choose Composite, and when would they
choose Visitor?

*Hint: Compiler teams typically choose Visitor because:
(1) AST node types are stable (defined by the grammar);
(2) operations grow constantly (type checker, optimizer,
code generator, linter). The Visitor trade-off is exactly
right for compilers. Composite is better for:
(1) When node types grow frequently (pluggable node types);
(2) When operations are stable (file system: name, size,
permissions). The rule: "What changes more - node types
or operations?" Visitor: OCP for operations. Composite:
OCP for node types.*

**Q2.** A Composite tree representing a product bill-of-
materials (BOM): a `Product` contains `Component`s; each
`Component` may itself be a `Product` (sub-assembly) or
a `RawMaterial` (leaf). The `totalCost()` operation must
include a currency conversion for international sourcing.
Should `totalCost(Currency currency)` be on the Component
interface, or should currency conversion be a separate
concern? Design the cleanest solution.

*Hint: Passing conversion parameters into the component
interface method mixes concerns. The cleaner approach:
Component.totalCost() returns amounts in a canonical
currency (USD). A separate `CurrencyConverter` service
is injected into the Composite's constructor and used
inside Composite.totalCost() to convert each child's
amount to the canonical currency before summing. This
keeps the interface simple and the currency concern in
one place.*

**Q3.** Large Composite trees (millions of nodes, e.g.,
a massive file system) have performance problems with
recursive Java traversal: (1) stack overflow risk from
deep recursion, (2) eager computation of all nodes even
when only a summary is needed. Design a streaming, lazy
Composite traversal that avoids both problems.

*Hint: Stream-based traversal: Component.stream() returns
a Stream<Component> that uses an iterative depth-first
traversal with an explicit Deque<Component> as the stack
(no recursion = no stack overflow). Use flatMap to combine
streams: Composite.stream() = Stream.concat(Stream.of(this),
children.stream().flatMap(Component::stream)). Lazy: the
stream is evaluated only as elements are consumed. This
handles million-node trees without stack overflow.*

---

### 🎯 Interview Deep-Dive

**Q1: Explain the Composite pattern with a real example
from the Java standard library or a common framework.**

*Why they ask:* Tests pattern recognition beyond textbook
examples.

*Strong answer includes:*
- Java AWT/Swing: `java.awt.Component` (Component interface);
  `JButton`, `JLabel` (Leaves); `JPanel`, `JFrame` (Composites
  - extend Container which extends Component AND contains
  a list of Components); `paint()` is the Composite operation
  that recursively paints the widget tree
- DOM: `org.w3c.dom.Node` is the Component; text nodes are
  Leaves; Element/Document are Composites; `getChildNodes()`
  returns the children; DOM traversal uses the Node interface
  without distinguishing text from elements
- Must name all three participants: Component, Leaf, Composite

**Q2: When would you choose Composite over Visitor for
processing a tree structure?**

*Why they ask:* Tests depth of understanding beyond the
basic pattern - the Composite/Visitor trade-off is a
senior-level question.

*Strong answer includes:*
- Composite: preferred when NEW NODE TYPES will be added
  frequently and operations are stable
- Adding a new node type: implement Component interface,
  zero changes to existing classes
- Adding a new operation: add to Component interface, must
  implement in every existing class (expensive)
- Visitor is the reverse: cheap to add operations, expensive
  to add node types
- File system: node types are stable (file, folder, symlink)
  but operations grow (size, search, permissions, backup) -
  Visitor fits better. Expression trees in calculators:
  operations are stable (evaluate) but new expression types
  may be added (sin, cos) - Composite fits better

**Q3: What is the risk of placing child management methods
(add, remove) on the Component interface rather than only
on the Composite class?**

*Why they ask:* Tests understanding of the type-safety
vs transparency trade-off in Composite design.

*Strong answer includes:*
- Risk: Leaf.add() and Leaf.remove() have no meaning;
  they must either throw UnsupportedOperationException
  or do nothing - both are confusing to callers
- Broken LSP: a Leaf IS-A Component but cannot fulfill
  the full Component contract (add/remove)
- Type-safe alternative: child management only on Composite;
  when building the tree, callers must cast to Composite
  to add children - type-safe but less uniform
- GoF recommendation: transparency (child management in
  Component) is better for CLIENT code that never distinguishes
  Leaf and Composite; type-safety is better when the
  calling code must sometimes build the tree AND traverse it

