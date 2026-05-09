---
layout: default
title: "Composite"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /design-patterns/composite/
id: DPT-014
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - datastructure
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-014 - Composite

⚡ TL;DR - Composite lets you treat individual objects and compositions of objects uniformly by placing them in a tree structure with a shared interface.

| DPT-014 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Recursion, Tree Data Structure, Polymorphism | |
| **Used by:** | File System Trees, UI Component Hierarchies, XML/JSON Parsing, Menu Systems | |
| **Related:** | Decorator, Iterator, Visitor, Composite Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A file system browser must calculate the total size of a folder. Folders contain files and sub-folders. Without a unified interface, the code must handle two distinct types with `instanceof` checks:

```java
for (Object item : folder.getContents()) {
    if (item instanceof File) {
        total += ((File) item).getSize();
    } else if (item instanceof Folder) {
        total += calculateFolderSize((Folder) item);
    }
    // What about symlinks? Archives? Mounts? More branches...
}
```

Every operation that traverses the tree (size calculation, search, deletion, permission change) must duplicate this `instanceof` branching. Adding a new node type (symbolic link, network mount) requires finding and updating every traversal in the codebase.

**THE BREAKING POINT:**
The cascading `instanceof` pattern signals that the type system is fighting the domain. The domain says "a folder contains items." The code says "a folder contains things I must identify by type." Every traversal repeats the same type-checking ceremony. New node types break existing traversals - a regression everywhere at once.

**THE INVENTION MOMENT:**
This is exactly why the Composite pattern was created. Both `File` and `Folder` implement a common `FileSystemNode` interface with `getSize()`. `File.getSize()` returns its own size. `Folder.getSize()` recursively calls `getSize()` on all its children and sums them. Client code uses `node.getSize()` without knowing or caring whether `node` is a file or a folder. No `instanceof`. No branching. Adding new node types: implement the interface, zero changes to existing traversals.

**EVOLUTION:**
Composite was the dominant pattern for tree structures before
Java generics and the Collections Framework matured. Modern
Java uses `List<Component>` and stream operations naturally,
making the pattern more about the recursive structure than
the class hierarchy. XML/HTML DOM, file system APIs, and
AST (Abstract Syntax Trees) in compilers remain canonical
uses. Reactive frameworks (RxJava, Project Reactor) model
async operation trees with Composite-derived structures.
JSON/YAML parsing libraries universally use Composite
to represent nested object graphs.

---

### 📘 Textbook Definition

The **Composite** pattern is a structural design pattern that composes objects into tree structures to represent part-whole hierarchies. It lets clients treat individual objects (leaves) and compositions of objects (composites) uniformly through a common interface. A composite holds a collection of children (each of which may be a leaf or another composite) and implements the shared interface by delegating to its children recursively. The pattern is the canonical solution for hierarchical object structures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Treat a single item and a container of items identically through one common interface.

**One analogy:**
> A corporate org chart. You can ask "what is the total headcount of this unit?" of a single employee (1 person) or an entire division (hundreds of people). The question is identical. The division recursively asks each sub-unit, which asks each team, which asks each individual. You never need to know if you're asking a person or an organisation.

**One insight:**
The Composite pattern's power is that recursion becomes implicit in the interface contract. The client calls `getSize()` on a root node and the entire tree computes itself. No explicit loops or type checks in client code - the polymorphism IS the tree traversal.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A domain model has part-whole hierarchies: things that are either atomic or composed of other things.
2. Operations on the hierarchy should apply uniformly regardless of whether a node is atomic (leaf) or composite.
3. The hierarchy can be arbitrarily deep - hardcoding depth limits is never correct.

**DERIVED DESIGN:**
Given invariant 1+2: define a `Component` interface with the operations clients need. Implement it in `Leaf` (atomic node) and `Composite` (branch node). Given invariant 3: `Composite` holds a `List<Component>` - each child is a `Component`, so it can be a `Leaf` or another `Composite`. The recursive call in `Composite.operation()` traverses the tree without any depth knowledge.

The key design tension: should `Component` declare child-management methods (`add(Component)`, `remove(Component)`, `getChildren()`)? If yes: clients can treat everything uniformly including adding children. If no: only `Composite` declares these methods, requiring a cast to add children. The trade-off is between interface uniformity (all through `Component`) and type safety (casts reveal incorrect use of leaves).

**THE TRADE-OFFS:**
**Gain:** Uniform treatment of leaves and composites (no `instanceof`); recursive operations are natural and concise; adding new component types is open/closed; tree traversal logic centralised in `Composite.operation()`.
**Cost:** Hard to restrict component types - if the `Component` interface is general, any `Component` can be added as a child, including nonsensical combinations (file inside a file); leaf nodes must implement or stub out child-management methods if declared on the interface; recursive calls on very deep trees risk stack overflow.

---

### 🧪 Thought Experiment

**SETUP:**
A permission system where permissions can be granted individually (`ReadPermission`) or grouped (`PermissionGroup` which contains multiple permissions or sub-groups). The goal: check if a permission is granted, given a root group.

**WHAT HAPPENS WITHOUT COMPOSITE:**
```java
boolean hasPermission(Object ctx, String perm) {
    if (ctx instanceof Permission) {
        return ((Permission) ctx).getName().equals(perm);
    } else if (ctx instanceof PermissionGroup) {
        for (Object child : ((PermissionGroup) ctx).children) {
            if (hasPermission(child, perm)) return true; // recursive call, messy
        }
    }
    return false;
}
```
Every caller must handle both types. This function is reimplemented throughout the codebase for different operations (list all permissions, serialise to JSON, check expiry).

**WHAT HAPPENS WITH COMPOSITE:**
```java
interface PermissionNode {
    boolean has(String name);
}
class SinglePermission implements PermissionNode {
    boolean has(String n) { return name.equals(n); }
}
class PermissionGroup implements PermissionNode {
    boolean has(String n) {
        return children.stream().anyMatch(c -> c.has(n));
    }
}
```
Every operation on the tree is a method on `PermissionNode`. No `instanceof` anywhere.

**THE INSIGHT:**
Composite eliminates the `instanceof` tax on tree operations. The trade-off of the recursive implementation is paid once - in the Composite class itself.

---

### 🧠 Mental Model / Analogy

> Composite is like the nested bullet points in a document. Each bullet can be a leaf (just text) or a parent (contains sub-bullets). The "render all bullets" operation doesn't distinguish - it recursively renders every node. Adding a sub-bullet to any level just adds a child node. The rendering logic is the same for every level.

- "Each bullet point" → `Component` (interface)
- "Leaf bullet (just text)" → `Leaf` implementation
- "Parent bullet with sub-bullets" → `Composite` implementation
- "Render operation" → any `Component.operation()` method
- "Adding sub-bullets" → `composite.add(child)`
- "Arbitrary nesting depth" → tree recursion handles it without limit

Where this analogy breaks down: in a document, a leaf bullet cannot have children. In a poorly designed Composite, a leaf could be added as a child of another leaf if child-management methods are on the Component interface - leading to confusing state.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Composite lets you build a tree where every node looks the same from the outside. Whether a node is a single item or a container of many items, you call the same method on it. The tree figures out the rest by passing the call down through each level.

**Level 2 - How to use it (junior developer):**
Create a `Component` interface with the operations you need (`getSize()`, `render()`, `getPrice()`). Implement `Leaf` for atomic nodes - the operation works directly. Implement `Composite` with a `List<Component> children` - the operation iterates over children and aggregates. Client code uses `Component` references everywhere. Build the tree by calling `composite.add(leaf)` or `composite.add(anotherComposite)`.

**Level 3 - How it works (mid-level engineer):**
The recursion in Composite is depth-first by default: `Composite.getSize()` calls `getSize()` on each child in list order; children that are composites recurse further before returning. Breadth-first traversal requires explicit queue management. Thread safety: `List<Component> children` is not thread-safe; use `CopyOnWriteArrayList` for read-heavy concurrent traversal, or synchronise `add`/`remove` operations. Stack overflow risk: trees deeper than ~5,000 levels (JVM default stack depth) will overflow. Use explicit stack or convert to iterative traversal for deep trees. The Iterator and Visitor patterns are the standard companions - Iterator for uniform traversal, Visitor for adding operations without modifying component classes.

**Level 4 - Why it was designed this way (senior/staff):**
Composite is directly inspired by hierarchical file systems and UI widget toolkits - both domains where the part-whole relationship is fundamental and arbitrarily deep. Its deepest implication is in API design: forcing leaf and composite to share an interface is an intentional uniformity that trades type precision for behavioural convenience. In XML/JSON parsing (`org.w3c.dom.Node`), every node in the DOM - elements, text nodes, attributes, documents - implements the same `Node` interface. The price: you must check `getNodeType()` to understand what you actually have - a vestige of the `instanceof` problem repackaged as an enum check. This trade-off is the central tension in Composite design: uniformity vs type safety. Kotlin sealed classes and Java sealed classes (Java 17+) offer a newer approach: exhaustive pattern matching that is type-safe without `instanceof` cascades - a modern alternative to Composite for cases where the type set is Fixed.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  COMPOSITE PATTERN STRUCTURE                    │
│                                                 │
│  <<interface>>                                  │
│  FileSystemNode                                 │
│  + getSize(): long                              │
│  + getName(): String                            │
│  + display(indent: int)                         │
│      │                                          │
│   ┌──┴──────────────────────────────────┐       │
│   │                                     │       │
│ File (Leaf)                   Folder (Composite)│
│ - name: String                - name: String   │
│ - size: long                  - children:      │
│                                 List<FSNode>   │
│ getSize() {                                    │
│   return size;      getSize() {                │
│ }                     return children.stream() │
│                          .mapToLong(           │
│                             FSNode::getSize)   │
│                          .sum();               │
│                       }                        │
└─────────────────────────────────────────────────┘
```

**Tree traversal example:**
```
Root (Folder, no direct size)
├── src (Folder)
│   ├── Main.java (File, 2048 bytes)  ← Leaf
│   └── util (Folder)
│       └── Helper.java (File, 1024 bytes) ← Leaf
└── README.md (File, 512 bytes)  ← Leaf

root.getSize():
  src.getSize():
    Main.java.getSize() → 2048
    util.getSize():
      Helper.java.getSize() → 1024
    → 2048 + 1024 = 3072
  README.md.getSize() → 512
→ 3072 + 512 = 3584 bytes
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User selects root Folder in file browser
  → app calls rootFolder.getSize()
                        ← YOU ARE HERE
  → Folder.getSize() iterates children
  → each child.getSize() called recursively
  → leaf Files return their own size
  → sub-Folders aggregate their children
  → total size returned to UI
  → status bar shows "3.5 KB selected"
```

**FAILURE PATH:**
```
Circular reference in tree (folder A contains B,
  B contains A - e.g., via symlinks)
  → getSize() recurses infinitely
  → StackOverflowError after ~5000 levels
  → No detection in base Composite
Fix: track visited nodes in a Set<Component>
  → detect cycle, throw or skip duplicate nodes
```

**WHAT CHANGES AT SCALE:**
For a file system with 10 million files, recursive `getSize()` traverses all nodes synchronously - potentially seconds of wall time. At scale: (1) cache size at composite level, invalidating when children change; (2) lazy computation with `CompletableFuture` for parallel sub-tree evaluation; (3) precomputed aggregate columns in a database (for catalogues). The tree structure is correct; the traversal strategy needs to evolve at scale.

---

### 💻 Code Example

**Example 1 - BAD: instanceof-based traversal:**
```java
// BAD: every operation requires instanceof branching
long calculateSize(Object node) {
    if (node instanceof FileNode) {
        return ((FileNode) node).getSize();
    } else if (node instanceof FolderNode) {
        long total = 0;
        for (Object child :
             ((FolderNode) node).getContents()) {
            total += calculateSize(child); // recursion buried
        }
        return total;
    }
    throw new IllegalArgumentException("Unknown: " + node);
}
```

**Example 2 - GOOD: Composite pattern:**
```java
// Component interface - uniform for leaves and composites
public interface FileSystemNode {
    long getSize();
    String getName();
    void display(int indentLevel);
}

// Leaf - no children
public class FileNode implements FileSystemNode {
    private final String name;
    private final long size;

    public FileNode(String name, long size) {
        this.name = name;
        this.size = size;
    }

    @Override public long getSize() { return size; }
    @Override public String getName() { return name; }
    @Override public void display(int indent) {
        System.out.println(" ".repeat(indent * 2)
            + "📄 " + name + " (" + size + "B)");
    }
}

// Composite - holds children
public class FolderNode implements FileSystemNode {
    private final String name;
    private final List<FileSystemNode> children
        = new ArrayList<>();

    public FolderNode(String name) { this.name = name; }

    public void add(FileSystemNode node) {
        children.add(node);
    }
    public void remove(FileSystemNode node) {
        children.remove(node);
    }

    @Override
    public long getSize() {
        // Recursion - no instanceof needed
        return children.stream()
            .mapToLong(FileSystemNode::getSize)
            .sum();
    }

    @Override public String getName() { return name; }

    @Override
    public void display(int indent) {
        System.out.println(" ".repeat(indent * 2)
            + "📁 " + name + "/");
        // Each child displays itself - no type check
        children.forEach(c -> c.display(indent + 1));
    }
}

// Usage:
FolderNode root = new FolderNode("project");
FolderNode src  = new FolderNode("src");
src.add(new FileNode("Main.java",   2048));
src.add(new FileNode("Helper.java", 1024));
root.add(src);
root.add(new FileNode("README.md", 512));

root.display(0);
System.out.println("Total: " + root.getSize() + "B");

// Adding new type (SymLink): implement FileSystemNode
// Zero changes to FolderNode, FileNode, or client code
```

**Example 3 - Price calculation for product bundles:**
```java
// Composite for e-commerce product structures
public interface PriceComponent {
    BigDecimal getPrice();
    String getDescription();
}

// Leaf: individual product
public class ProductItem implements PriceComponent {
    private final String name;
    private final BigDecimal price;

    public ProductItem(String name, double price) {
        this.name = name;
        this.price = BigDecimal.valueOf(price);
    }

    @Override public BigDecimal getPrice() { return price; }
    @Override public String getDescription() { return name; }
}

// Composite: bundle (can contain products or sub-bundles)
public class ProductBundle implements PriceComponent {
    private final String name;
    private final BigDecimal discount; // flat discount
    private final List<PriceComponent> items
        = new ArrayList<>();

    public ProductBundle(String name, double discount) {
        this.name = name;
        this.discount = BigDecimal.valueOf(discount);
    }

    public void add(PriceComponent item) {
        items.add(item);
    }

    @Override
    public BigDecimal getPrice() {
        // Sum children - they may be single items or bundles
        BigDecimal subtotal = items.stream()
            .map(PriceComponent::getPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        return subtotal.subtract(discount);
    }

    @Override public String getDescription() { return name; }
}

// Usage:
ProductBundle officeBundle = new ProductBundle("Office", 10.0);
officeBundle.add(new ProductItem("Keyboard", 79.99));
officeBundle.add(new ProductItem("Mouse", 49.99));

ProductBundle gamingBundle = new ProductBundle("Gaming", 20.0);
gamingBundle.add(new ProductItem("Headset", 149.99));
gamingBundle.add(officeBundle); // bundle in bundle!

System.out.println(gamingBundle.getPrice()); // 249.97
```

---

### ⚖️ Comparison Table

| Pattern | Structure | Uniformity | Operations | Best For |
|---|---|---|---|---|
| **Composite** | Tree (part-whole) | Total (leaf = composite) | Recursive aggregation | File systems, UI trees, org charts |
| Decorator | Chain (linear) | Total (wraps same interface) | Sequential augmentation | Feature stacking on one object |
| Iterator | External traversal | Partial (traversal only) | Sequential access | Traversing without recursion |
| Visitor | External operations | Object-specific | Multiple unrelated ops | Adding operations to fixed structure |

How to choose: use Composite for tree-shaped hierarchies where operations naturally aggregate (sum, search, render). Use Decorator when you want to add responsibilities to a single object at runtime without a tree. Use Visitor when you have a stable Composite structure but need to add many operations without modifying component classes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Composite always uses a list for children | Children can be any collection. A Map is used for named children (directory entries); a Set for unordered unique children; a List for ordered children |
| Composite and Decorator are the same because both wrap objects | Composite creates tree structures (one parent, many children). Decorator adds behaviour to a single object. Both use composition, but for different structural purposes |
| Leaf nodes should throw UnsupportedOperationException for add/remove | Only if add/remove are declared on the Component interface. Better design: only Composite declares child management methods, avoiding stub implementations on leaves |
| Composite is only for file systems | Composite appears wherever part-whole hierarchies exist: UI component trees (HTML DOM, Swing), expression trees (compilers), permission structures, menu hierarchies, project task breakdowns |
| Adding a cycle detection check makes Composite always safe | Cycle detection only prevents infinite loops. It doesn't prevent logical inconsistencies (a folder containing itself shows up in parent AND child listings) |

---

### 🚨 Failure Modes & Diagnosis

**1. Circular Reference Causing Stack Overflow**

**Symptom:** `StackOverflowError` during tree traversal (getSize, render, search). Occurs only for certain nodes in the tree, not all.

**Root Cause:** A composite directly or indirectly contains itself (cycle in the object graph). Recursive traversal follows the cycle indefinitely.

**Diagnostic:**
```java
// Add cycle detection to traversal:
public long getSize(Set<FileSystemNode> visited) {
    if (!visited.add(this)) {
        log.warn("Cycle detected at: {}", getName());
        return 0L;  // break cycle
    }
    return children.stream()
        .mapToLong(c -> c instanceof FolderNode
            ? ((FolderNode) c).getSize(visited)
            : c.getSize())
        .sum();
}
```

**Fix:**
Pass a `Set<Component>` through recursive calls to track visited nodes. On encountering a visited node, skip it and log a warning.

**Prevention:** Enforce acyclicity in `add(Component)`: traverse the new child's subtree and reject if `this` is found in it.

---

**2. Deep Recursion Causing Stack Overflow on Large Trees**

**Symptom:** `StackOverflowError` during directory scan on a file system with 15,000 levels of nesting. Works in development (shallow trees) but fails in production.

**Root Cause:** JVM default stack depth is ~500–5,000 frames depending on method complexity. Recursive `getSize()` creates one stack frame per tree level.

**Diagnostic:**
```bash
# Check full stack trace depth at crash:
jcmd <PID> Thread.print | grep -A 100 "StackOverflow"
# Count frames for the recursive method to see depth
```

**Fix:**
Convert deep recursion to iterative traversal using an explicit `Deque` (stack):
```java
public long getSizeIterative() {
    long total = 0;
    Deque<FileSystemNode> stack = new ArrayDeque<>();
    stack.push(this);
    while (!stack.isEmpty()) {
        FileSystemNode node = stack.pop();
        if (node instanceof FolderNode) {
            ((FolderNode) node).children
                .forEach(stack::push);
        } else {
            total += node.getSize();
        }
    }
    return total;
}
```

**Prevention:** For trees with potential depth > 1,000 levels, use iterative traversal. Document maximum expected depth.

---

**3. Thread-Unsafe Concurrent Modification**

**Symptom:** `ConcurrentModificationException` during tree traversal when another thread modifies the tree simultaneously. Occurs intermittently under load.

**Root Cause:** `ArrayList<FileSystemNode>` in `FolderNode.children` is modified (add/remove) while another thread iterates over it in `getSize()` or `display()`.

**Diagnostic:**
```bash
jstack <PID> | grep -A 20 "ConcurrentModification"
# Look for one thread in getSize() and another in add()
# on the same FolderNode
```

**Fix:**
```java
// Option 1: CopyOnWriteArrayList (read-heavy trees)
private final List<FileSystemNode> children
    = new CopyOnWriteArrayList<>();

// Option 2: ReadWriteLock (frequent writes)
private final ReadWriteLock lock = new ReentrantReadWriteLock();
public long getSize() {
    lock.readLock().lock();
    try { /* iteration */ }
    finally { lock.readLock().unlock(); }
}
public void add(FileSystemNode n) {
    lock.writeLock().lock();
    try { children.add(n); }
    finally { lock.writeLock().unlock(); }
}
```

**Prevention:** Decide at design time whether the tree is read-heavy or write-heavy. Use `CopyOnWriteArrayList` for rare-write trees; `ReadWriteLock` for balanced read-write trees.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` - Composite's `Composite.operation()` is inherently recursive; comfort with recursive algorithms is required to implement and debug
- `Tree Data Structure` - Composite implements a tree; understanding tree properties (parent, children, leaves, depth) is foundational
- `Polymorphism` - the uniform interface is polymorphism in action; method dispatch to Leaf or Composite determines the behaviour

**Builds On This (learn these next):**
- `Iterator` - external iteration over Composite trees; standard companion for when traversal order must be controlled externally
- `Visitor` - adds new operations to a Composite without modifying component classes; the canonical way to separate operations from structure
- `Decorator` - a structural sibling; shares the "wrapping via composition" technique but for single objects, not trees

**Alternatives / Comparisons:**
- `Decorator` - adds behaviour to a single object in a chain; use for wrapping one object, not building a tree
- `Visitor` - adds operations to a Composite; use when new operations are frequent but the tree structure is stable
- `Sealed classes (Java 17+)` - type-safe alternative to Composite for fixed-set hierarchies using exhaustive pattern matching

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Tree of objects all sharing one interface │
│              │ so leaves and containers look identical   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Type-checking branching (instanceof)      │
│ SOLVES       │ required for every tree operation         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Composite.operation() = recurse;         │
│              │ Leaf.operation() = base case              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Part-whole hierarchies where clients      │
│              │ must treat leaf and container the same   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Tree node types are fixed and few (use   │
│              │ sealed classes + pattern matching instead)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Uniform treatment + extensibility vs      │
│              │ loss of type safety on tree contents     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask the root, the tree answers itself." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Iterator → Visitor → Decorator           │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When individual objects and compositions of those objects
must be treated uniformly, define a common interface. Let
recursive structure be a first-class part of the type system,
not an afterthought handled by instanceof checks.

**Where else this pattern appears:**
- **File systems:** Files and directories share `list()`,
  `size()`, `delete()` -- a directory delegates to its
  children recursively. The client code doesn't distinguish
  between a file tree and a single file.
- **DOM trees (HTML/XML):** Element nodes and text nodes
  both implement `Node` -- traversal, serialization, and
  event propagation work uniformly on any node type.
- **Arithmetic expressions:** `1 + (2 * 3)` is a tree where
  numbers are leaves and operators are composites -- the
  `evaluate()` method recurses naturally from root to leaves.

---

### 💡 The Surprising Truth

The Composite pattern has a well-known asymmetry that the GoF
acknowledged as a fundamental trade-off: you cannot safely
add type-safe leaf-only or composite-only operations without
either violating the uniform interface (by putting operations
only on Composite) or breaking type safety (by returning null
from Leaf for composite operations). The GoF themselves
called this "one of the fundamental trade-offs in Composite"
and noted there is no perfect solution -- every Composite
implementation involves a conscious choice about how to
handle leaf-composite asymmetry.
---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform models its category hierarchy with Composite: `Category` can contain `Product` items (leaves) or sub-`Category` nodes. A new search requirement: "find all products matching a keyword within this category subtree." Two engineers propose different designs: Engineer A adds `search(String keyword)` to the `Component` interface (Composite approach). Engineer B uses the Visitor pattern with a `SearchVisitor`. Compare both approaches for: (1) testability, (2) adding a second operation (`countProducts()`), and (3) adding a new node type (`Bundle`). Which is better, and under what specific conditions does the other become better?

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A compiler represents its Abstract Syntax Tree (AST) using Composite: `Expression` interface with `Literal` (leaf) and `BinaryExpression`, `UnaryExpression`, `FunctionCall` (composites). The semantic analysis phase must type-check each node. The type-checking logic for `BinaryExpression` depends on the types of BOTH children - but the Composite interface's `typeCheck()` method takes no arguments. Trace the full calling sequence where `BinaryExpression.typeCheck()` must communicate the inferred types upward and receive them from children, and identify why this is an architectural limitation of the pure Composite approach.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A menu system uses Composite:
`MenuItem` (leaf) and `Menu` (composite with `addItem()`).
A requirement says: calculate the total calorie count of
a meal (sum of all selected items recursively). But also:
for gluten-free mode, filter out all items containing
gluten at any level. Map these two operations to the
Visitor pattern vs direct Composite traversal and decide
which is appropriate for each operation.

*Hint: The Comparison Table entry linking Composite to Visitor
is the key. Visitor externalises operations; Composite
internalises them. The gluten filter is a tree transformation
(Visitor candidate); the calorie sum is a pure accumulation
(natural recursive descent on Composite).*
