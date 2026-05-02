---
layout: default
title: "Inheritance"
parent: "CS Fundamentals — Paradigms"
nav_order: 19
permalink: /cs-fundamentals/inheritance/
number: "0019"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Abstraction, Encapsulation
used_by: Polymorphism, Design Patterns
related: Composition over Inheritance, Polymorphism, Abstract Classes
tags:
  - foundational
  - mental-model
  - first-principles
  - pattern
  - tradeoff
---

# 019 — Inheritance

⚡ TL;DR — Inheritance lets a class acquire the fields and methods of a parent class, enabling code reuse and establishing "is-a" relationships between types.

| #019 | Category: CS Fundamentals — Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Abstraction, Encapsulation | |
| **Used by:** | Polymorphism, Design Patterns | |
| **Related:** | Composition over Inheritance, Polymorphism, Abstract Classes | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:

You have three classes: `Dog`, `Cat`, `Bird`. Each has `name`, `age`, `eat()`, `sleep()`. They differ only in `speak()` and `move()`. Without a way to share the common parts, you copy-paste the `name`, `age`, `eat()`, `sleep()` implementation three times. When you need to add `owner` to all animals, you make the same change in three places. Miss one: subtle bug. Change the sleep logic: change it three times.

THE BREAKING POINT:

At scale, this copy-paste proliferates — 50 animal types, each duplicating the same 200 lines of shared logic. A single bug fix requires 50 edits. A new capability requires 50 additions. The codebase grows in size but not in complexity — pure duplication. The violation: identical code exists in multiple places, which is the root of maintenance catastrophe.

THE INVENTION MOMENT:

This is exactly why inheritance was created — to let a derived class _inherit_ the shared implementation from a base class, adding or overriding only what differs. Define `Animal` once with shared fields and methods. `Dog`, `Cat`, `Bird` inherit from `Animal` and only implement their specific behaviour.

---

### 📘 Textbook Definition

**Inheritance** is an OOP mechanism by which a class (the _subclass_ or _derived class_) acquires the properties (fields) and behaviours (methods) of another class (the _superclass_ or _base class_). The subclass extends the superclass — it inherits all non-private members and can override methods to provide specialised behaviour. Inheritance establishes an **"is-a" relationship**: `Dog is an Animal`. It enables both code reuse (shared implementation in the superclass) and subtype polymorphism (a `Dog` can be used wherever an `Animal` is expected). Java and most OOP languages support **single inheritance** for classes (one superclass) and **multiple inheritance** for interfaces.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Inheritance means "my class gets everything the parent class has, then I add or change what's different."

**One analogy:**

> A child inherits their parents' physical traits and habits as defaults, then develops their own personality on top. They don't start from scratch — they start with a foundation and build upward. A new employee inherits the company's standard operating procedures as defaults, then adds their role-specific skills.

**One insight:**
Inheritance is powerful for "is-a" relationships where the subclass genuinely is a more specific version of the superclass. It becomes a source of pain when used for "has-a" relationships (composition) or when deep hierarchies make behaviour tracing nearly impossible. The rule: prefer composition over inheritance unless the "is-a" relationship is unambiguous and stable.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. A subclass must honour all contracts of its superclass — it must be substitutable wherever the superclass is expected (Liskov Substitution Principle).
2. Inheritance creates a _compile-time_ dependency: the subclass is bound to the superclass at compile time.
3. Private members of the superclass are not accessible in the subclass — only public/protected members are inherited.

DERIVED DESIGN:

The superclass defines the shared contract and default implementation. Subclasses override specific methods to specialise behaviour while inheriting everything else. The base class provides the template; subclasses fill in the variable parts.

In memory: a `Dog` object contains all `Animal` fields plus its own. The object header points to `Dog`'s vtable, which contains `Dog`'s overridden methods and inherits the rest from `Animal`'s vtable.

THE TRADE-OFFS:

Gain: code reuse (shared implementation in one place), polymorphism (subclass can be used as superclass type), type hierarchy clarity.
Cost: tight coupling (subclass depends on superclass internals — the "fragile base class" problem), violation of encapsulation (protected members expose internals to subclasses), deep hierarchies become impossible to understand, inheritance is a static relationship (set at compile time — can't change at runtime like composition can).

The industry has largely moved toward "favour composition over inheritance" for behaviour reuse, reserving inheritance for true "is-a" type relationships.

---

### 🧪 Thought Experiment

SETUP:
You inherit `Stack` from `ArrayList` because a stack needs storage and ArrayList provides it.

WHAT GOES WRONG:
`ArrayList` has `add(index, element)` and `remove(index)` methods — you inherit them. But a `Stack` should only allow push/pop (LIFO). A user calls `myStack.add(0, item)` — legally inserting at position 0, violating stack semantics. Inheritance brought in methods that should not exist on a `Stack`.

This is the `java.util.Stack` bug — it actually extends `Vector` (an old ArrayList) and inherits `add(index, element)`, `elementAt(index)`, and other non-stack operations. The Liskov Substitution Principle is violated: you cannot use `Stack` everywhere `Vector` is expected without risk, because `Stack` adds the expectation of LIFO ordering that `Vector.add(0, x)` violates.

THE INSIGHT:
Inheritance is appropriate when the "is-a" relationship holds for the _entire_ interface, not just selected parts. `Stack` should _contain_ an `ArrayList` (composition), not _be_ an `ArrayList` (inheritance). If you can imagine calling an inherited method in a way that violates the subclass's contract, inheritance is the wrong model.

---

### 🧠 Mental Model / Analogy

> Inheritance is like an **employee template**. A company has a general "Employee" template: name, salary, vacation days, benefits. A `Manager` is a specific type of Employee who also has `directReports` and `approve()`. A `Contractor` is a different type who doesn't get vacation days — they need to _override_ that field. If you tried to make `Contractor` inherit `Employee.vacationDays`, you'd inherit something that doesn't apply — the model breaks.

**Mapping:**

- "Employee template" → base class / superclass
- "Manager" → derived class that extends the template
- "Override vacationDays for Contractor" → method/field override
- "All managers ARE employees" → the "is-a" relationship
- "Contractor doesn't fit Employee template" → sign inheritance is wrong, composition needed

**Where this analogy breaks down:** In real organisations, an employee can belong to multiple categories (Manager AND Contractor). Java's single inheritance prevents this for classes — interfaces provide the multi-role capability.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Inheritance lets you create a new class that starts with everything from an existing class, then adds or changes things. A `SavingsAccount` inherits from `BankAccount` — it gets all the account behaviour for free, then adds `interestRate` and `applyInterest()`. No need to rewrite deposit, withdraw, or balance tracking.

**Level 2 — How to use it (junior developer):**
In Java, use `extends`: `class Dog extends Animal`. Dog inherits all public/protected methods and fields from Animal. Use `@Override` to replace a method from the parent. Use `super()` to call the parent constructor. Use `super.methodName()` to call the parent's version of an overridden method. Mark superclass fields `protected` if subclasses need direct access; `private` if they should use accessor methods.

**Level 3 — How it works (mid-level engineer):**
At the JVM level, a subclass's class file has a reference to its superclass. The JVM creates a method resolution order (MRO): when a method is called on a subclass object, it looks in the subclass's class, then the superclass, then up the hierarchy until it finds the method. The vtable is constructed by copying the superclass's vtable and replacing entries for overridden methods. Object layout places superclass fields first in memory, then subclass fields — so casting between types changes only the reference type, not the physical object. `instanceof` checks the class hierarchy metadata.

**Level 4 — Why it was designed this way (senior/staff):**
Single inheritance was chosen for Java (and most OOP languages) to avoid the "diamond problem" of multiple inheritance — where class D inherits from B and C (both inheriting from A), and calling D.method() is ambiguous if B and C both override it differently. Java solved this by allowing multiple interface inheritance (pure contracts, no implementation) and single class inheritance. C++ allows multiple class inheritance but requires explicit disambiguation. Go has no inheritance at all — only interface composition. The industry trend is clear: the coupling and fragility of class inheritance is rarely worth the code-reuse benefit, which is better achieved through composition.

---

### ⚙️ How It Works (Mechanism)

**Class hierarchy and vtable:**

```
┌─────────────────────────────────────────────────────┐
│       INHERITANCE HIERARCHY AND VTABLE              │
│                                                     │
│  Animal (superclass)                                │
│  ├── name: String                                   │
│  ├── eat() → Animal.eat impl                        │
│  ├── sleep() → Animal.sleep impl                    │
│  └── speak() → abstract (no impl)                  │
│                                                     │
│  Dog extends Animal (subclass)                      │
│  ├── [inherited] name: String                       │
│  ├── breed: String (new field)                      │
│  ├── [inherited] eat() → Animal.eat impl            │
│  ├── [inherited] sleep() → Animal.sleep impl        │
│  └── speak() → Dog.speak impl (override)            │
│                                                     │
│  Dog vtable:                                        │
│  ┌───────────────────────────────────────┐          │
│  │ eat   → Animal.eat (not overridden)   │          │
│  │ sleep → Animal.sleep (not overridden) │          │
│  │ speak → Dog.speak (overridden)        │          │
│  └───────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

**Constructor chaining:**

```java
class Animal {
    String name;
    Animal(String name) { this.name = name; }
}

class Dog extends Animal {
    String breed;
    Dog(String name, String breed) {
        super(name);       // MUST call superclass constructor first
        this.breed = breed;
    }
}
// Object layout in memory:
// [vtable pointer][name (inherited)][breed (Dog-specific)]
// superclass fields come first
```

**Overriding vs overloading:**

```java
class Animal {
    public String speak() { return "..."; }
}

class Dog extends Animal {
    @Override
    public String speak() {  // OVERRIDE: replaces Animal.speak
        return "Woof!";       // same signature, new implementation
    }

    // OVERLOADING (not inheritance): different signature
    public String speak(int times) {
        return "Woof! ".repeat(times);  // different method entirely
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
Method call: animal.speak()
      ↓
[INHERITANCE / VIRTUAL DISPATCH ← YOU ARE HERE]
  JVM reads object's vtable pointer
  Looks up speak() in vtable
  For Dog: returns Dog.speak
  For Cat: returns Cat.speak
      ↓
Correct implementation executes
      ↓
Result returned — caller never knew the concrete type
```

FAILURE PATH (Liskov Substitution Violation):

```
Developer uses Stack (extends Vector) as Vector
      ↓
Calls stack.add(0, element) — inserts at front
      ↓
Stack LIFO invariant violated — not a programming error
  but a design error: inheritance gave wrong methods
      ↓
Subtle data corruption — stack is no longer LIFO
Observable: stack.pop() returns wrong element
```

WHAT CHANGES AT SCALE:

In large codebases, deep inheritance hierarchies (5+ levels) become impossible to trace. "What does `EnterpriseUserManagerServiceImpl.process()` do?" requires reading 5 superclasses. Google's style guides and many large organisations explicitly limit inheritance depth to 2. At the framework level (Spring, Hibernate), inheritance is used deliberately but shallowly — abstract base classes provide template implementations for extension points, not for reuse.

---

### 💻 Code Example

**Example 1 — Correct use of inheritance for "is-a" relationship:**

```java
// GOOD: SavingsAccount IS-A BankAccount — full contract honoured
public abstract class BankAccount {
    protected String accountId;
    protected int balanceCents;

    public BankAccount(String accountId, int initialBalance) {
        this.accountId = accountId;
        this.balanceCents = initialBalance;
    }

    public void deposit(int amountCents) {
        if (amountCents <= 0) throw new IllegalArgumentException();
        balanceCents += amountCents;
    }

    public abstract void applyMonthlyFee();  // subclass implements
}

public class SavingsAccount extends BankAccount {
    private double annualInterestRate;

    public SavingsAccount(String id, int balance, double rate) {
        super(id, balance);  // parent constructor
        this.annualInterestRate = rate;
    }

    @Override
    public void applyMonthlyFee() {
        // Savings accounts earn interest instead of paying fees
        int monthlyInterest = (int)(balanceCents * annualInterestRate / 12);
        balanceCents += monthlyInterest;
    }
}
```

**Example 2 — Liskov Substitution Principle violation (wrong inheritance):**

```java
// BAD: Rectangle is NOT truly a Square — LSP violated
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int w)  { this.width = w; }
    public void setHeight(int h) { this.height = h; }
    public int area() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        this.width = w;
        this.height = w;  // must keep equal
    }
    @Override
    public void setHeight(int h) {
        this.width = h;   // must keep equal
        this.height = h;
    }
}

// Test that works for Rectangle but fails for Square:
void testRectangle(Rectangle r) {
    r.setWidth(5);
    r.setHeight(4);
    assert r.area() == 20;  // passes for Rectangle
    // FAILS for Square: setHeight(4) sets both to 4 → area = 16
}
// Square cannot substitute Rectangle — LSP violated
// Fix: don't inherit — make both implement a Shape interface
```

**Example 3 — Abstract class as template method pattern:**

```java
// Template Method Pattern: defines algorithm skeleton in base class
public abstract class DataExporter {
    // Template method: algorithm skeleton
    public final void export(List<Record> data) {
        List<Record> filtered = filter(data);    // hook
        List<String> formatted = format(filtered); // hook
        write(formatted);                           // hook
    }

    protected abstract List<Record> filter(List<Record> data);
    protected abstract List<String> format(List<Record> data);
    protected abstract void write(List<String> lines);
}

// Subclass provides specifics without knowing the overall algorithm
public class CsvExporter extends DataExporter {
    @Override
    protected List<Record> filter(List<Record> d) {
        return d.stream().filter(Record::isActive).toList();
    }
    @Override
    protected List<String> format(List<Record> d) {
        return d.stream().map(r -> r.toCSV()).toList();
    }
    @Override
    protected void write(List<String> lines) {
        Files.write(Path.of("output.csv"), lines);
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism       | Coupling | Reuse | Runtime Flexibility | "Is-a" Required | Risk               |
| --------------- | -------- | ----- | ------------------- | --------------- | ------------------ |
| **Inheritance** | High     | High  | None                | Yes             | Fragile base class |
| Composition     | Low      | High  | Yes (swap impls)    | No (has-a)      | Interface design   |
| Interface only  | Very low | None  | Yes                 | No              | No reuse           |
| Mixin/Trait     | Medium   | High  | Limited             | No              | Diamond problem    |
| Delegation      | Low      | High  | Yes                 | No              | Boilerplate        |

**How to choose:** Use inheritance only when there is an unambiguous "is-a" relationship that holds for the _entire_ superclass interface. Use composition for behaviour reuse. Inheritance for type hierarchy; composition for functionality.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                   |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inheritance is for code reuse                         | Inheritance is for "is-a" type relationships. Composition is for code reuse. Using inheritance solely to reuse code creates tight coupling and LSP violations.                                                                                            |
| Deeper hierarchies are more OOP                       | Deep hierarchies (5+ levels) are a code smell. Behaviour becomes impossible to trace. Flat hierarchies with composition are more maintainable.                                                                                                            |
| Overriding a method doesn't break the parent contract | It can and does if the override doesn't maintain the parent's invariants. The Liskov Substitution Principle defines exactly when an override is safe.                                                                                                     |
| Abstract classes are the same as interfaces           | Abstract classes can have state and implementation; they support single inheritance. Interfaces define contracts only (in Java 8+, they can have default methods but no state). Use interfaces for contracts; abstract classes for shared implementation. |
| Private fields are inherited                          | Private fields exist in the object's memory layout but are _not accessible_ in the subclass. The subclass cannot read or write them directly — only through superclass public/protected methods.                                                          |

---

### 🚨 Failure Modes & Diagnosis

**Fragile Base Class**

Symptom:
Changing an `internal` method in the base class breaks a subclass that overrides it. The subclass was calling `super.method()` and the parent changed its sequence of internal calls.

Root Cause:
The superclass's `protected` or overridable methods form an implicit contract with subclasses. Changing the internal call order breaks subclasses that override steps in the sequence.

Diagnostic Command / Tool:

```bash
# Find all overrides of a base class method:
grep -rn "@Override" src/ --include="*.java" | \
  grep -i "methodName"
# All hits are subclasses that will be affected by a base change
```

Fix:
Make internal helper methods `private` to prevent overriding. Use composition — extract the varying part into a strategy object. Make the template method `final` to prevent subclass interference.

Prevention:
"Design and document for inheritance, or prohibit it" (Effective Java). If a class isn't designed for extension, mark it `final`. Document every `protected` method as part of the public API.

---

**Liskov Substitution Principle Violation**

Symptom:
Code that works correctly with the base class fails silently or incorrectly with the subclass. The subclass changes behaviour in a way the caller doesn't expect.

Root Cause:
The subclass overrides a method and weakens preconditions, strengthens postconditions, or throws exceptions not declared by the superclass — violating the substitutability guarantee.

Diagnostic Command / Tool:

```java
// Test: any code that works with Animal should work with Dog
@Test
void dogSatisfiesAnimalContract() {
    Animal a = new Dog("Buddy", "Labrador");  // use as Animal
    assertDoesNotThrow(() -> a.speak());
    assertNotNull(a.speak());
    assertTrue(a.speak().length() > 0);
    // If any assertion fails, Dog violates Animal's contract
}
```

Fix:
Redesign the hierarchy — either strengthen the base class contract, weaken the restriction in the subclass, or switch to composition + interfaces.

Prevention:
Write contract tests for base classes. Run them against all subclasses in CI. Any subclass that fails a base class contract test is an LSP violation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Object-Oriented Programming (OOP)` — inheritance is one of OOP's four pillars; requires understanding classes and objects
- `Encapsulation` — inheritance can breach encapsulation through `protected` members; understanding encapsulation is needed to use inheritance safely
- `Abstraction` — abstract classes are the inheritance mechanism for defining contracts with partial implementations

**Builds On This (learn these next):**

- `Polymorphism` — inheritance enables subtype polymorphism; the vtable is built from the inheritance hierarchy
- `Composition over Inheritance` — the principle that explains when to use inheritance vs composition — the essential counterbalance to this entry
- `Design Patterns` — Template Method, Strategy, and Factory Method use inheritance and polymorphism systematically

**Alternatives / Comparisons:**

- `Composition over Inheritance` — the preferred alternative for code reuse; "has-a" vs "is-a"
- `Mixins / Traits` — language features (Scala traits, Python mixins, Ruby modules) that provide multiple inheritance of behaviour without the diamond problem
- `Delegation` — explicitly forwarding method calls to a composed object — more verbose than inheritance but far less coupled

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Subclass acquires superclass fields and   │
│              │ methods; adds or overrides as needed      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Code duplication across types that share  │
│ SOLVES       │ most behaviour but differ in specifics    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Valid only for "is-a" relationships — the │
│              │ subclass must honour ALL of the parent's  │
│              │ contract (LSP), not just parts of it      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Clear "is-a": Dog is an Animal; Savings   │
│              │ Account is a Bank Account                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using for code reuse only ("has-a") —     │
│              │ use composition instead                   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Code reuse and polymorphism vs tight       │
│              │ coupling and fragile base class           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inherit type; compose behaviour.         │
│              │  Inheritance is not a code-reuse tool."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Composition over Inheritance → SOLID → DDD│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `java.util.Properties` extends `java.util.Hashtable`. This means `Properties` inherits `put(Object key, Object value)` — allowing non-String keys and values, which breaks `Properties`'s contract that all keys and values are Strings. This is a real, shipped LSP violation in the Java standard library. Given that it's too late to change the hierarchy, what workaround patterns would you use if you needed `Properties`-like behaviour without this inherited contamination — and what does this case teach about backward compatibility as a constraint on fixing inheritance mistakes?

**Q2.** A deep inheritance hierarchy: `BaseController → SecureController → AuthenticatedController → UserController → UserProfileController`. A security bug is discovered in `SecureController.validateToken()`. How many classes are affected by this change, and what is the minimum test surface you need to verify the fix doesn't break any of the subclasses? How does this compare to a composition-based design where `TokenValidator` is injected as a dependency into each controller independently?
