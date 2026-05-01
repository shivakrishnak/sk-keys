---
layout: default
title: "Composite Pattern"
parent: "Design Patterns"
nav_order: 773
permalink: /design-patterns/composite-pattern/
number: "773"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Recursion, Tree Data Structure"
used_by: "File systems, UI component trees, Organization hierarchies, XML/HTML DOM"
tags: #intermediate, #design-patterns, #structural, #oop, #recursion, #tree
---

# 773 — Composite Pattern

`#intermediate` `#design-patterns` `#structural` `#oop` `#recursion` `#tree`

⚡ TL;DR — **Composite** lets you treat individual objects and compositions of objects uniformly — by organizing them in a tree structure where both leaf nodes and branch nodes implement the same interface, so clients don't need to know if they're dealing with one item or a nested group.

| #773 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Recursion, Tree Data Structure | |
| **Used by:** | File systems, UI component trees, Organization hierarchies, XML/HTML DOM | |

---

### 📘 Textbook Definition

**Composite** (GoF, 1994): a structural design pattern that composes objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects (leaves) and compositions of objects (composites) uniformly. The key structural element: both leaf and composite implement the same interface. Leaf: has no children; performs work directly. Composite: has children (list of Component); delegates work to children (typically recursively). GoF intent: "Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly." Canonical examples: file system (File and Folder both implement FileSystemItem), UI component trees (Button and Panel both implement Component), HTML DOM.

---

### 🟢 Simple Definition (Easy)

A file system. You want to know: "How big is this?" Whether "this" is a single text file (leaf) or a folder containing hundreds of files and subfolders (composite), the answer is `item.getSize()`. For a file, it returns the file's size. For a folder, it sums all children recursively. You call the same method on both — you don't check "is this a file or a folder?" The folder IS composed of items that each answer `getSize()`.

---

### 🔵 Simple Definition (Elaborated)

An HTML DOM: `<div>` contains `<p>`, `<span>`, other `<div>` elements — composites containing leaves and other composites. Every element implements `render()`. When you call `render()` on a `<div>`, it calls `render()` on all its children. When you call `render()` on a `<span>` (leaf), it renders its own content. The browser's rendering engine calls `document.render()` — it doesn't care if the element is a simple text node or a nested div containing 50 elements.

---

### 🔩 First Principles Explanation

**How the uniform interface enables recursive tree operations:**

```
COMPOSITE STRUCTURE:

  «interface» Component
  ─────────────────────
  +getSize(): long
  +getName(): String
  +print(indent: int): void
  
  Leaf: File                    Composite: Folder
  ──────────────────            ─────────────────────────
  -name: String                 -name: String
  -size: long                   -children: List<Component>
  
  +getSize(): long              +getSize(): long
      return size;                  return children.stream()
                                             .mapToLong(Component::getSize)
  +print(indent):                            .sum();        // recursive!
      print(" ".repeat(indent) + name)
                                +add(Component c)
                                +remove(Component c)
                                +print(indent):
                                    print(" ".repeat(indent) + name + "/")
                                    for each child: child.print(indent + 2)
  
RECURSIVE TREE OPERATIONS:

  FileSystemItem root = new Folder("root");
  FileSystemItem docs = new Folder("docs");
  FileSystemItem src  = new Folder("src");
  
  docs.add(new File("readme.md",  1200));
  docs.add(new File("design.pdf", 50000));
  
  src.add(new File("Main.java",   3000));
  src.add(new File("Util.java",   1500));
  
  root.add(docs);
  root.add(src);
  root.add(new File("pom.xml",    800));
  
  // Single call works regardless of depth or structure:
  root.getSize();     // 1200 + 50000 + 3000 + 1500 + 800 = 56500
  root.print(0);      // prints tree:
                      // root/
                      //   docs/
                      //     readme.md
                      //     design.pdf
                      //   src/
                      //     Main.java
                      //     Util.java
                      //   pom.xml
  
  docs.getSize();     // 51200 — same method, subtree scope
  
COMPOSITE TRANSPARENCY vs. SAFETY:

  TWO DESIGN CHOICES:
  
  1. TRANSPARENCY (GoF default): Component interface includes add()/remove()/getChildren()
     Leaf: add() throws UnsupportedOperationException (or does nothing)
     ✓ Client code uniform — can call add() on any Component
     ✗ Leaf violates Liskov: throws exception for valid interface method
     
  2. SAFETY: add()/remove() only in Composite, not in Component interface
     Client must cast to Composite before calling add():
     if (component instanceof Folder folder) folder.add(child);
     ✓ No unexpected exceptions from Leaf
     ✗ Client must distinguish Composite from Leaf (breaks uniformity somewhat)
     
  Java consensus: prefer SAFETY. Only put shared behavior in Component interface.
  
COMPOSITE PATTERN IN JAVA ECOSYSTEM:

  java.awt.Container extends Component:
    Component: paint(), setVisible(), getPreferredSize()
    Container: add(Component), remove(Component), getComponents()
    JPanel is a Container (composite). JButton is a Component (leaf).
    
  org.w3c.dom.Node (XML/HTML DOM):
    Node has: getNodeName(), getChildNodes(), appendChild()
    Element is a Node that can have children (composite).
    Text is a Node with no children (leaf).
    
  Spring Security GrantedAuthority:
    Simple string authorities (leaf).
    CompositeGrantedAuthority wrapping multiple (composite).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Composite:
- Client code: `if (item instanceof File) processFile(file); else if (item instanceof Folder) processFolder(folder)` everywhere
- Add new node type (SymLink): modify all client switch/if blocks (OCP violation)

WITH Composite:
→ `item.process()` — same call for File, Folder, SymLink, ZIP, any tree node
→ Add new node type: implement Component, add it to tree. Client code: zero changes.

---

### 🧠 Mental Model / Analogy

> An organizational hierarchy. A company has a CEO. The CEO has departments. Each department has teams. Each team has employees. You want to know: "What's the total payroll cost?" Whether you ask about an individual employee (leaf), a team, a department, or the whole company (composites), the answer is `node.payrollCost()`. Employee returns salary. Manager returns salary + sum of all reports' costs. Composite pattern.

"Employee" = Leaf (no children, returns own value)
"Manager / Department / Company" = Composite (has children, sums recursively)
"payrollCost()" = the uniform Component interface method
"Ask any level, get subtree total" = client doesn't distinguish leaf from composite

---

### ⚙️ How It Works (Mechanism)

```
COMPOSITE TREE:

         Component (interface)
              ↑
    ┌─────────┴──────────┐
  Leaf                Composite
  (no children)       (has children: List<Component>)
  implements          implements
  Component           Component
  directly            by delegating to children (recursion)
  
  Operation on Composite = Operation on each child + combine results
```

---

### 🔄 How It Connects (Mini-Map)

```
Part-whole tree structure where leaves and branches need uniform treatment
        │
        ▼
Composite Pattern ◄──── (you are here)
(leaf and composite implement same interface; recursive tree operations)
        │
        ├── Decorator: also wraps component; Decorator = chain of 1; Composite = tree of N
        ├── Iterator: traverse composite tree nodes uniformly
        ├── Visitor: add operations to Composite tree without modifying nodes
        └── Flyweight: share leaf objects in large Composite trees to save memory
```

---

### 💻 Code Example

```java
// UI component tree (Swing-like):
interface UIComponent {
    void render(int depth);
    int getPreferredWidth();
    int getPreferredHeight();
}

// LEAF — renders itself, no children:
class Button implements UIComponent {
    private final String label;
    
    Button(String label) { this.label = label; }
    
    public void render(int depth) {
        System.out.println("  ".repeat(depth) + "[Button: " + label + "]");
    }
    public int getPreferredWidth()  { return label.length() * 8 + 20; }
    public int getPreferredHeight() { return 30; }
}

class TextField implements UIComponent {
    private final int columns;
    TextField(int columns) { this.columns = columns; }
    
    public void render(int depth) {
        System.out.println("  ".repeat(depth) + "[TextField: " + columns + " cols]");
    }
    public int getPreferredWidth()  { return columns * 8; }
    public int getPreferredHeight() { return 25; }
}

// COMPOSITE — delegates to children:
class Panel implements UIComponent {
    private final String id;
    private final List<UIComponent> children = new ArrayList<>();
    
    Panel(String id) { this.id = id; }
    
    public void add(UIComponent component) { children.add(component); }
    
    public void render(int depth) {
        System.out.println("  ".repeat(depth) + "[Panel: " + id + "]");
        for (UIComponent child : children) {
            child.render(depth + 1);   // recursive delegation
        }
    }
    
    public int getPreferredWidth() {
        return children.stream().mapToInt(UIComponent::getPreferredWidth).max().orElse(0) + 10;
    }
    
    public int getPreferredHeight() {
        return children.stream().mapToInt(UIComponent::getPreferredHeight).sum() + 5;
    }
}

// Build tree:
Panel loginForm = new Panel("login-form");
loginForm.add(new TextField(30));
loginForm.add(new Button("Login"));
loginForm.add(new Button("Cancel"));

Panel mainWindow = new Panel("main-window");
mainWindow.add(loginForm);
mainWindow.add(new Button("Help"));

// Uniform call — no instanceof checks:
mainWindow.render(0);
System.out.println("Total height: " + mainWindow.getPreferredHeight());
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Composite Pattern requires that all tree operations are recursive | Not all operations are recursive. A leaf's `getSize()` is not recursive — it returns its own size. Only the composite's `getSize()` recurses over children. The COMPOSITE delegates to children recursively; the LEAF implements directly. The pattern just ensures both respond to the same method. |
| add()/remove() should be in the Component interface for full uniformity | This is the "transparency vs. safety" tradeoff. Putting add()/remove() in Component means leaves must implement them (throwing UnsupportedOperationException — a Liskov violation). Many modern implementations put management methods only in Composite. Client code that needs to build the tree casts to Composite; code that traverses the tree uses Component. |
| Composite is for binary trees | Composite is for N-ary trees: each composite can have any number of children (0 to N). A folder can contain 0 files or 1000. The canonical examples (file systems, UI hierarchies, DOM) are all N-ary trees. |

---

### 🔥 Pitfalls in Production

**Infinite recursion from circular references:**

```java
// ANTI-PATTERN: Adding a composite to itself (or creating a cycle):
Panel outerPanel = new Panel("outer");
Panel innerPanel = new Panel("inner");

outerPanel.add(innerPanel);
innerPanel.add(outerPanel);  // CYCLE: outer → inner → outer → ...

outerPanel.render(0);  // → StackOverflowError! Infinite recursion.

// FIX: Prevent cycles in add():
public void add(UIComponent component) {
    if (component == this) throw new IllegalArgumentException("Cannot add to itself");
    // For deeper cycle detection: check if `this` is a descendant of `component`:
    if (isDescendantOf(component)) {
        throw new IllegalArgumentException("Would create a cycle");
    }
    children.add(component);
}

// ALSO: Performance pitfall for deep trees — computing size/height traverses
// the entire subtree on every call:
// FIX: Cache computed values and invalidate on structural changes:
private int cachedHeight = -1;

public int getPreferredHeight() {
    if (cachedHeight == -1) {
        cachedHeight = children.stream()
            .mapToInt(UIComponent::getPreferredHeight).sum() + 5;
    }
    return cachedHeight;
}

void add(UIComponent c) {
    children.add(c);
    cachedHeight = -1;  // invalidate cache
}
```

---

### 🔗 Related Keywords

- `Decorator Pattern` — wraps a component to add behavior (Composite = tree; Decorator = chain of 1)
- `Iterator Pattern` — traverse a Composite tree's nodes uniformly
- `Visitor Pattern` — add new operations to Composite tree without changing node classes
- `Flyweight Pattern` — share leaf objects in large composite trees (e.g., shared character glyphs in text)
- `Tree Data Structure` — Composite is the OOP pattern for representing and operating on trees

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Tree structure: leaves and branches share │
│              │ one interface. Client calls same method  │
│              │ regardless of leaf or composite node.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Part-whole tree hierarchy; need uniform  │
│              │ treatment of individual items and groups;│
│              │ recursive tree operations                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Not a tree structure; operations differ   │
│              │ too much between leaf and composite to  │
│              │ share a meaningful interface             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "File system: getSize() on a file returns │
│              │  its size; on a folder returns the sum  │
│              │  of all contents — same method call."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Decorator Pattern → Visitor Pattern →     │
│              │ Iterator Pattern → Flyweight Pattern      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The DOM (Document Object Model) is a textbook Composite implementation. `document.getElementById("main").querySelectorAll(".btn")` traverses the composite tree and returns all matching leaf/composite nodes. How does the Composite pattern enable the uniformity of DOM traversal APIs? Consider: can `querySelectorAll` be implemented with the same interface whether called on `document` (root) or a specific `<div>` (subtree)?

**Q2.** Spring Security's authorization uses a hierarchical role/authority system. Consider implementing "role groups" where `ADMIN` implies all permissions of `USER`, and a custom `SUPER_ADMIN` implies `ADMIN` + `FINANCE_VIEWER`. How would you use the Composite pattern to model a tree of roles/authorities where `hasAuthority("X")` checks if X is contained anywhere in the tree — handling both leaf authorities and composite authority groups?
