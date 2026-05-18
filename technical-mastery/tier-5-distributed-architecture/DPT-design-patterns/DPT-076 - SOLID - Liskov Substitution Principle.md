---
id: DPT-076
title: "SOLID: Liskov Substitution Principle"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-074, DPT-075
used_by: []
related: DPT-074, DPT-075, DPT-077, DPT-078
tags:
  - concept
  - solid
  - advanced
  - liskov
  - substitutability
  - type-theory
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 76
permalink: /technical-mastery/design-patterns/lsp/
---

⚡ TL;DR - If S is a subtype of T, then objects of type T
may be replaced with objects of type S without altering
the correctness of the program. LSP violations are detected
by: client code that checks the subtype before calling
a method, or subtypes that throw exceptions for operations
the parent type declares as valid.

| #76 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074, DPT-075 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-075, DPT-077, DPT-078 | |

---

### 🔥 The Problem This Solves

**THE BROKEN INHERITANCE HIERARCHY:**
A `Square` class extends `Rectangle`. Both have `setWidth()`
and `setHeight()` methods. For a `Rectangle`, setting
width and height independently is valid. For a `Square`,
setting them independently breaks the invariant (a square
has equal sides).

When client code calls `setWidth(5)` and `setHeight(10)`
on a `Rectangle` object: area = 50. Correct.
When the SAME client code receives a `Square` object
(passed as a `Rectangle`): setting width to 5 also sets
height to 5. Setting height to 10 also sets width to 10.
Final area = 100. The client's invariant (area = width × height)
is broken by the substitution.

**THE CONSEQUENCE:**
Client code must check: "is this actually a Square?" before
assuming width and height are independent. This instanceof
check IS the LSP violation: the substitution is not transparent.

---

### 📘 Textbook Definition

The **Liskov Substitution Principle (LSP)** was introduced
by Barbara Liskov in 1987:

> "If for each object o1 of type S there is an object o2 of
> type T such that for all programs P defined in terms of T,
> the behavior of P is unchanged when o1 is substituted for
> o2, then S is a subtype of T."

**Practical statement (Robert C. Martin):**
> "Functions that use pointers to base classes must be able
> to use objects of derived classes without knowing it."

**Behavioral preconditions:**
A subtype may have WEAKER preconditions (accept more than
the parent), not stronger.

**Behavioral postconditions:**
A subtype must have STRONGER postconditions (guarantee
at least as much as the parent), not weaker.

**Invariants:**
A subtype must maintain all the invariants that the parent
class maintains.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A subtype should work correctly everywhere its parent
type is expected, without the caller needing to know
the difference.

**One analogy:**
> A type contract is a promise. If a `Rectangle` promises:
> "setWidth and setHeight are independent operations,"
> then a `Square` that CANNOT honor this promise should
> not be a subtype of `Rectangle`.
>
> LSP: subclasses must HONOR all the promises made by
> the parent class. A subclass that breaks a parent's
> promise is not a valid subtype - regardless of what
> `extends` says in the code.
>
> LSP is about behavioral contracts, not syntactic inheritance.

---

### 🔩 First Principles Explanation

**BEHAVIORAL SUBTYPING:**
LSP distinguishes SYNTACTIC inheritance (extends/implements
in Java) from BEHAVIORAL subtyping (actually honoring
the parent type's contract). Syntactic inheritance is
trivial; behavioral subtyping is the requirement.

**LISKOV'S THREE RULES:**

1. **Precondition rule (contravariance):**
   The subtype's method may have WEAKER preconditions
   than the parent's (accept more). It MUST NOT have
   stronger preconditions (be more restrictive than the parent).
   Example: If parent accepts any string, the subtype
   may accept any string + null (weaker). It must not
   require non-empty strings (stronger than parent = LSP violation).

2. **Postcondition rule (covariance):**
   The subtype's method may have STRONGER postconditions
   than the parent's (guarantee more). It MUST NOT have
   weaker postconditions (guarantee less than the parent).
   Example: If parent guarantees a sorted return list,
   the subtype must also return a sorted list (at minimum).

3. **Invariant rule:**
   The subtype must preserve all invariants the parent
   maintains. If parent maintains "width × height = area,"
   the subtype must also maintain this invariant for
   all inherited methods.

**EXCEPTION RULE:**
A subtype should not throw exceptions that the parent
does not declare. If `save()` in the parent never throws
`ReadOnlyException`, a subtype that throws `ReadOnlyException`
in `save()` violates LSP.

---

### 🧪 Thought Experiment

**THE CLASSIC SQUARE-RECTANGLE PARADOX:**

Is a Square a subtype of Rectangle geometrically? Yes.
Is a Square a behavioral subtype of Rectangle in code? No.

Rectangle invariant: width and height are independently settable.
Square invariant: width == height always.

These invariants are incompatible. A Square cannot
honor the Rectangle invariant without violating its
own invariant. Therefore: Square is NOT a valid subtype
of Rectangle in code, regardless of the geometric
"is-a" relationship.

The solution: neither extends the other. Both implement
a `Shape` interface with `getArea()`. The specific
dimension-setting contracts are not shared.

**THE CORRECT HIERARCHY:**
```
Shape (interface) - getArea()
  ↑ implements       ↑ implements
Rectangle             Square
(setWidth + setHeight)  (setSide)
```
No inheritance between Rectangle and Square. LSP preserved.

---

### 🧠 Mental Model / Analogy

> LSP = the "contract inheritance" model.
> A service contract between a company and its customers.
> If Company A acquires Company B and promises: "all
> Company A contracts are honored," then customers can
> transparently switch from Company A service to Company
> B service without any change in what they receive.
>
> If Company B cannot honor some of Company A's promises:
> customers would need to check "is this Company A
> or Company B?" before relying on those promises.
> That check is the LSP violation.
>
> Subclass promises: must be at least as reliable as
> parent class promises. Customers (client code) should
> never need to check which specific subclass they have.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Identifying LSP violations:**
Two signals:
1. Client code contains `instanceof` checks to handle
   a specific subtype differently from the parent.
2. A subtype throws an exception that the parent does
   not declare (especially `UnsupportedOperationException`).

**Level 2 - Precondition/postcondition analysis:**
For each method override in a subtype: does the override
have STRONGER preconditions than the parent? (rejects
inputs the parent would accept) → LSP violation.
Does the override have WEAKER postconditions than the parent?
(guarantees less than the parent) → LSP violation.

**Level 3 - Design-by-contract:**
Eiffel (Bertrand Meyer's language) implements Design by
Contract (DbC) with explicit preconditions, postconditions,
and invariants enforced at runtime. Java does not have
built-in DbC, but `Assertions`, `@PreCondition` annotations
(from Apache Commons), and unit tests can verify behavioral
subtyping. LSP is a contract specification; DbC is its
runtime enforcement mechanism.

---

### ⚙️ How It Works (Mechanism)

```
LSP Behavioral Contract Check
┌─────────────────────────────────────────────────────────┐
│ For each method override in Subtype:                    │
│                                                         │
│ PRECONDITION CHECK:                                     │
│   Parent accepts: input I                              │
│   Subtype must accept: I or more (not less)            │
│   If Subtype rejects a valid parent input → VIOLATION  │
│                                                         │
│ POSTCONDITION CHECK:                                    │
│   Parent guarantees: output O                          │
│   Subtype must guarantee: O or more (not less)         │
│   If Subtype provides less guarantee → VIOLATION       │
│                                                         │
│ INVARIANT CHECK:                                        │
│   Parent maintains: invariant V                        │
│   Subtype must maintain: V                             │
│   If Subtype breaks V → VIOLATION                      │
│                                                         │
│ EXCEPTION CHECK:                                        │
│   Parent declares: throws E1, E2                       │
│   Subtype must not throw: E3 (not declared by parent)  │
│   If Subtype adds undeclared exception → VIOLATION     │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Classic LSP violation and fix:**

```java
// BAD: Square extends Rectangle - LSP violated.

class Rectangle {
    protected int width, height;

    // Parent invariant: width and height are independent.
    public void setWidth(int width)   { this.width = width; }
    public void setHeight(int height) { this.height = height; }
    public int getArea()              { return width * height; }
}

class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width; // Forces height == width.
    }
    @Override
    public void setHeight(int height) {
        this.height = height;
        this.width = height; // Forces width == height.
    }
}

// Client code - valid for Rectangle:
void testArea(Rectangle r) {
    r.setWidth(5);
    r.setHeight(10);
    assert r.getArea() == 50; // FAILS if r is a Square!
    // Square: setHeight(10) also sets width to 10.
    // getArea() = 100, not 50.
    // Client must check: if (r instanceof Square) ...
    // That instanceof check = the LSP violation.
}
```

```java
// GOOD: Neither extends the other. Common interface only.

interface Shape {
    int getArea();
}

class Rectangle implements Shape {
    private int width, height;
    Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }
    // Setters available; no invariant conflict.
    public int getArea() { return width * height; }
}

class Square implements Shape {
    private int side;
    Square(int side) { this.side = side; }
    // No width/height setter conflict. Square invariant: side only.
    public int getArea() { return side * side; }
}

// Client code: works transparently with any Shape.
void printArea(Shape s) {
    System.out.println(s.getArea()); // No instanceof. LSP satisfied.
}
```

**Example 2 - UnsupportedOperationException as LSP violation:**

```java
// BAD: ReadOnlyList violates LSP.

class ReadOnlyList extends ArrayList<String> {
    @Override
    public boolean add(String element) {
        // Parent (ArrayList) guarantees: add returns true.
        // This subtype throws instead (new exception not
        // declared by parent). LSP violated.
        throw new UnsupportedOperationException("Read only!");
    }
}

// Client code using a List:
void appendItem(List<String> list, String item) {
    list.add(item); // Unexpectedly throws for ReadOnlyList.
    // Client must check: if (!(list instanceof ReadOnlyList)) ...
    // That instanceof = the LSP violation.
}

// GOOD: Use composition + different interface.
interface ReadableList<T> { List<T> getAll(); }
interface WriteableList<T> extends ReadableList<T> {
    void add(T element);
}
// ReadOnlyList implements ReadableList (not WriteableList).
// No add() promised. No LSP violation.
```

---

### ⚖️ LSP Violation Detection Guide

| Signal | What it indicates |
|---|---|
| `instanceof` check in client code before calling method | Subtype requires different handling than parent - LSP violation |
| `UnsupportedOperationException` in a method | Subtype does not honor parent's operational contract |
| Subtype method with tighter precondition | Rejects inputs parent would accept - precondition violation |
| Subtype method with looser postcondition | Guarantees less than parent - postcondition violation |
| Test that passes for parent but fails for subtype | Behavioral subtyping failure |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "is-a" relationship in domain = valid subtype in code | Geometric "is-a" (Square is a Rectangle) does not imply behavioral subtyping. Code subtypes must honor behavioral contracts, not just domain relationships |
| LSP only matters for inheritance | LSP applies to interface implementations too. An interface makes behavioral promises. An implementation that violates those promises (throws unexpected exceptions, returns weaker guarantees) violates LSP |
| An `interface` with `default` methods cannot violate LSP | It can. If a `default` method in an interface has a behavioral contract, an implementing class that overrides it to violate the contract (throws an exception the contract doesn't declare, weakens a postcondition) violates LSP |
| LSP violations are always detectable at compile time | Only type-system violations (wrong return type, unchecked exceptions) are compile-time errors. Behavioral violations (weaker postconditions, broken invariants) are runtime failures detected only by testing or runtime assertions |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Subtypes must be substitutable for their │
│              │ parent types without breaking behavior  │
├──────────────┼──────────────────────────────────────────┤
│ PRECONDITION │ Subtype may accept MORE (weaker).        │
│              │ May NOT accept LESS (stronger = violation│
├──────────────┼──────────────────────────────────────────┤
│ POSTCONDITION│ Subtype may guarantee MORE (stronger).   │
│              │ May NOT guarantee LESS (weaker = violatio│
├──────────────┼──────────────────────────────────────────┤
│ INVARIANT    │ Subtype must maintain all parent         │
│              │ invariants.                             │
├──────────────┼──────────────────────────────────────────┤
│ VIOLATION    │ instanceof check / UnsupportedOperation  │
│              │ Exception / stronger precondition       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-077: SOLID - ISP                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. LSP = behavioral subtyping. A subtype must honor ALL
   the behavioral contracts of the parent (preconditions
   no stronger, postconditions no weaker, invariants
   preserved, no new unchecked exceptions).
2. LSP violation signal: `instanceof` in client code,
   or `UnsupportedOperationException` in an overriding
   method. If you're checking "is this actually a subtype?"
   before calling a method - LSP is violated.
3. Square is NOT a Rectangle in code (even though it
   is geometrically). Their behavioral contracts for
   dimension-setting are incompatible. Both should
   implement a common `Shape` interface without sharing
   the setWidth/setHeight contract.

