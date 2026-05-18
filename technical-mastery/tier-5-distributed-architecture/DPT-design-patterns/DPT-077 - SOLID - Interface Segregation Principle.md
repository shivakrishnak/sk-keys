---
id: DPT-077
title: "SOLID: Interface Segregation Principle"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-074, DPT-076
used_by: []
related: DPT-074, DPT-075, DPT-076, DPT-078
tags:
  - concept
  - solid
  - intermediate
  - interface-segregation
  - fat-interface
  - software-design
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/design-patterns/isp/
---

⚡ TL;DR - Clients should not be forced to depend on methods
they do not use. Prefer many small, focused interfaces
over one large "fat" interface. An implementing class
should not be forced to implement methods it has no
use for.

| #77 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074, DPT-076 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-075, DPT-076, DPT-078 | |

---

### 🔥 The Problem This Solves

**THE FAT INTERFACE PROBLEM:**
A printer manufacturer creates a multi-function machine
and puts all capabilities in one interface:

```java
interface Machine {
    void print(Document d);
    void scan(Document d);
    void fax(Document d);
    void copy(Document d);
    void staple(Document d);
}
```

A simple laser printer can only print. To implement
`Machine`, it must implement `scan()`, `fax()`, `copy()`,
and `staple()` - operations it cannot perform. The
implementation: throw `UnsupportedOperationException`.

**THE CASCADE OF PROBLEMS:**
- Every update to `Machine` (adding a new method: `ocr()`)
  forces ALL implementations to change, including the
  laser printer that has no OCR capability.
- Client code that uses `Machine` for printing only
  depends on `scan()`, `fax()`, etc. - methods it never calls.
- Testing: testing the laser printer requires stubs for
  all irrelevant methods.

---

### 📘 Textbook Definition

The **Interface Segregation Principle (ISP)** is the
fourth SOLID principle (Robert C. Martin, 1996):

> "Clients should not be forced to depend upon interfaces
> they do not use."

**Alternative statement:**
> "No client should be forced to implement methods it
> does not need."

**Fat interface (violation):**
An interface with more methods than any single client
needs. Forces all implementors to provide stubs for
operations they do not support.

**Segregated interfaces (correct application):**
Multiple smaller interfaces, each serving a specific
role. Clients depend only on the interfaces they need.
Implementing classes implement only the interfaces
relevant to their capabilities.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split fat interfaces into focused role interfaces.
Implement only what you actually do. Depend only on
what you actually use.

**One analogy:**
> A multi-function printer interface vs. individual
> capability contracts.
>
> Instead of one contract "Machine" that covers ALL
> possible printer operations, use:
> - "Printable" contract: print(Document)
> - "Scannable" contract: scan(Document)
> - "Faxable" contract: fax(Document)
>
> A laser printer: implements Printable only.
> An all-in-one: implements Printable + Scannable + Faxable.
> A fax machine: implements Faxable only.
>
> Each client asks for only what it needs:
> A document sender asks for Faxable. Not Machine.

---

### 🔩 First Principles Explanation

**WHY FAT INTERFACES CAUSE COUPLING:**
A fat interface creates coupling between unrelated clients.
If I implement `Machine` and someone adds `ocr()` to
`Machine`, my simple printer must change even though
OCR is irrelevant to it. I am coupled to changes driven
by OTHER clients' needs.

Segregated interfaces: adding `ocr()` to the `Scannable`
interface only affects classes that NEED OCR. Other
classes are unaffected. Change propagation is bounded.

**ISP AND SINGLE RESPONSIBILITY (SRP):**
ISP for interfaces is the analog of SRP for classes.
SRP: a class should have only one reason to change.
ISP: an interface should have only one reason to change.
A fat interface has MULTIPLE reasons to change (one
per capability group). Splitting it by responsibility
gives each interface a single reason to change.

**INTERFACE COMPOSITION:**
ISP encourages designing interfaces small enough that
classes implementing MULTIPLE roles simply implement
multiple interfaces. Java's multiple interface implementation
is the mechanism: `class AllInOne implements Printable,
Scannable, Faxable {}`. No compromise; no stubs.

---

### 🧪 Thought Experiment

**BEFORE ISP:**
Interface: `UserRepository` with 12 methods:
```
findById / findAll / save / update / delete
findByEmail / findByRole / findByDepartment
count / exists / paginate / search
```
An authentication service only needs `findByEmail`.
A user management UI needs `findAll`, `paginate`, `search`.
An admin script only needs `count`, `exists`.

ALL THREE clients depend on all 12 methods. A change
to the paginate signature forces all three clients to
recompile (even though authentication and admin script
never call paginate).

**AFTER ISP:**
```
AuthUserRepository: findByEmail
SearchableUserRepository: findAll, paginate, search
AdminUserRepository: count, exists
WriteUserRepository: save, update, delete
```
The authentication service depends on `AuthUserRepository`
(1 method). Changes to `SearchableUserRepository`
do not affect it. Change propagation: contained.

---

### 🧠 Mental Model / Analogy

> ISP = "role interfaces" model.
> An employee can have multiple roles: manager, mentor,
> presenter. Each role has specific obligations.
>
> If you need a presenter for an event, you ask for a
> "Presenter" not for a "Full Employee." You don't
> care about the person's managerial obligations.
>
> Role interfaces: each interface represents ONE role.
> A class implements the roles it actually performs.
> A client asks for the role it needs.
>
> Fat interfaces force you to ask for the "Full Employee"
> when you only need the "Presenter." Everything the
> person does in ALL OTHER roles is an unnecessary
> dependency for your use case.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Identifying fat interfaces:**
A fat interface has these signals:
1. Some implementing classes throw `UnsupportedOperationException`
   in some methods.
2. Classes implementing the interface implement many
   methods as empty stubs or no-ops.
3. Different clients use disjoint subsets of the interface's methods.
4. Adding a method to the interface forces many unaffected
   classes to change.

**Level 2 - Designing role interfaces:**
Decompose a fat interface by USAGE PATTERN: identify
distinct client types. Each client type uses a subset
of the interface. Each subset becomes a role interface.
Implementing classes implement the role interfaces
relevant to them.

**Level 3 - ISP in Java standard library:**
`java.util.List` is arguably a fat interface - all lists
implement `add()`, `remove()`, etc., but read-only
list wrappers (`Collections.unmodifiableList()`) throw
`UnsupportedOperationException` for mutating methods.
The better design: separate `ReadableList` and `WriteableList`.
`java.io.Serializable` is a "marker interface" (zero methods)
that enables ISP-like role signaling without method obligations.
`java.util.concurrent.Executor` (one method: `execute()`)
is a role interface done correctly.

---

### ⚙️ How It Works (Mechanism)

```
Fat Interface vs. Segregated Interfaces
┌─────────────────────────────────────────────────────────┐
│ FAT INTERFACE:                                          │
│   interface Machine {                                   │
│     print(); scan(); fax(); copy(); staple(); ocr();   │
│   }                                                     │
│   LaserPrinter implements Machine:                     │
│     print() - real; scan() - STUB; fax() - STUB;      │
│     copy() - STUB; staple() - STUB; ocr() - STUB      │
│                                                         │
│ SEGREGATED INTERFACES:                                  │
│   interface Printable  { print(); }                    │
│   interface Scannable  { scan(); }                     │
│   interface Faxable    { fax(); }                      │
│   interface Copyable   { copy(); }                     │
│   interface Stapleable { staple(); }                   │
│   interface OCRCapable { ocr(); }                      │
│                                                         │
│   LaserPrinter implements Printable:                   │
│     print() - real. No stubs. No fake implementations.│
│                                                         │
│   AllInOne implements                                   │
│     Printable, Scannable, Faxable, Copyable, Stapleable│
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - ISP violation and fix:**

```java
// BAD: Fat interface forces stubs.

interface DataRepository {
    // Read operations:
    Entity findById(long id);
    List<Entity> findAll();
    // Write operations:
    void save(Entity entity);
    void delete(long id);
    // Search operations:
    List<Entity> search(String query);
    // Analytics operations:
    long count();
    Map<String, Long> countByGroup(String field);
}

// A read-only cache implements DataRepository
// but CANNOT write. Forced stubs:
class ReadOnlyCache implements DataRepository {
    public Entity findById(long id) { /* real */ return null; }
    public List<Entity> findAll()   { /* real */ return null; }
    public void save(Entity e) {
        throw new UnsupportedOperationException("Read-only!");
    }
    public void delete(long id) {
        throw new UnsupportedOperationException("Read-only!");
    }
    // search, count, countByGroup also not applicable...
}
// Every DataRepository change forces ReadOnlyCache to change.
```

```java
// GOOD: Segregated role interfaces.

interface ReadableRepository {
    Entity findById(long id);
    List<Entity> findAll();
}

interface WriteableRepository {
    void save(Entity entity);
    void delete(long id);
}

interface SearchableRepository {
    List<Entity> search(String query);
}

interface AnalyticsRepository {
    long count();
    Map<String, Long> countByGroup(String field);
}

// Read-only cache: only implements what it supports.
class ReadOnlyCache implements ReadableRepository {
    public Entity findById(long id) { /* real */ return null; }
    public List<Entity> findAll()   { /* real */ return null; }
    // No save(), delete() - not in the interface. No stubs.
}

// Full database implementation: all roles.
class DatabaseRepository
    implements ReadableRepository, WriteableRepository,
               SearchableRepository, AnalyticsRepository {
    // All methods implemented genuinely.
}

// Clients depend only on what they use:
class AuthService {
    private final ReadableRepository repo; // not WriteableRepository
    AuthService(ReadableRepository repo) { this.repo = repo; }
    // Search and analytics changes: no impact on AuthService.
}
```

---

### ⚖️ ISP and Interface Design Rules

| Context | Approach |
|---|---|
| New interface with 3+ distinct client types | Split by client usage pattern. Each client type gets its own interface |
| Existing fat interface with stub implementations | Decompose by capability groups. Classes implement only relevant groups |
| `UnsupportedOperationException` in implementation | Signal: the interface is too fat for this implementation. Segregate |
| Single small interface | No action needed. ISP = satisfied |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ISP requires one method per interface | ISP requires interfaces to be focused on a role, not infinitely granular. A role may have 2-5 related methods. One method per interface is over-engineering unless the role genuinely has one operation |
| ISP means avoiding large classes | ISP applies to interfaces, not classes. A class implementing multiple role interfaces can be large. The key: each INTERFACE remains focused |
| Composite interfaces violate ISP | A composite interface (`interface FullRepository extends ReadableRepository, WriteableRepository {}`) does not violate ISP. It is an optional convenience for clients that need both roles. Clients that need only one role still use the single-role interface |
| ISP only matters for Java interfaces | ISP applies to any explicit contract: Java interfaces, Python protocols/ABCs, Go interfaces, TypeScript interface types. Any contract that forces unneeded method implementations is a fat interface |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Clients depend only on interfaces they  │
│              │ use. No forced dependencies on unneeded │
│              │ methods.                                │
├──────────────┼──────────────────────────────────────────┤
│ FAT INTERFACE│ One interface, multiple disjoint client │
│ SIGNAL       │ usage patterns, forced stubs in impl.  │
├──────────────┼──────────────────────────────────────────┤
│ SOLUTION     │ Role interfaces. Each interface = one   │
│              │ capability group. Impl = multiple roles │
├──────────────┼──────────────────────────────────────────┤
│ VIOLATION    │ UnsupportedOperationException / stubs / │
│ SIGNALS      │ empty impls / unrelated changes cascade │
├──────────────┼──────────────────────────────────────────┤
│ RELATED      │ SRP (per class), OCP (per module),      │
│              │ LSP (behavioral contract of interface) │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-078: SOLID - DIP                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. ISP = split fat interfaces into role interfaces.
   A fat interface has methods for multiple distinct
   client types. When clients use disjoint subsets:
   split. Each client depends only on the interface
   it actually uses.
2. Fat interface signals: `UnsupportedOperationException`,
   empty stubs, unrelated changes cascading to unaffected
   implementations. Any of these = ISP violation.
3. Java standard library anti-example: `java.util.List`
   (unmodifiable wrappers throw for mutating methods).
   Better design: separate `ReadableList` and `WriteableList`.
   `java.util.concurrent.Executor` = ISP done right (one method).

