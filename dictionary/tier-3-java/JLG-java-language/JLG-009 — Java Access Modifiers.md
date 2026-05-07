---
layout: default
title: "Java Access Modifiers"
parent: "Java & JVM Internals"
nav_order: 9
permalink: /java/java-access-modifiers/
number: "JLG-009"
category: Java & JVM Internals
difficulty: ★☆☆
depends_on: Java Language, Encapsulation
used_by: Spring Core, Java Language, Design Patterns
related: Encapsulation, SOLID Principles, Principle of Least Privilege
tags:
  - java
  - jvm
  - foundational
  - security
---

# JLG-009 — Java Access Modifiers

⚡ TL;DR — Java's four access levels (`private`, package-private, `protected`, `public`) enforce encapsulation by controlling which code can see and call a class member.

| Attribute | Value |
|---|---|
| **Depends on** | Java Language, Encapsulation |
| **Used by** | Spring Core, Java Language, Design Patterns |
| **Related** | Encapsulation, SOLID Principles, Principle of Least Privilege |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** In early languages, every function and variable was globally visible. Any code could call any other code directly. Internal helper functions were invoked by untended callers. Data was mutated by unrelated modules. Changing an internal implementation detail broke distant, unknown code.

**THE BREAKING POINT:** As codebases grow, "public by default" creates an unbounded surface area. Every internal method becomes an implicit API. Refactoring an internal function requires checking the entire codebase. Security-sensitive fields are readable by any calling class. Teams cannot maintain boundaries between modules.

**THE INVENTION MOMENT:** Java's designers encoded the Principle of Least Privilege into the language itself: every member gets the most restrictive access level that still permits intended use. The compiler enforces boundaries — attempting to access a `private` field from another class is a compile error, not a runtime surprise.

---

### 📘 Textbook Definition

**Java access modifiers** are keywords applied to classes, fields, methods, and constructors to restrict their visibility. Java has four levels:

1. **`private`** — visible only within the declaring class
2. **Package-private (default, no keyword)** — visible to all classes in the same package
3. **`protected`** — visible to the declaring class, same package, and all subclasses (regardless of package)
4. **`public`** — visible to all classes everywhere

The compiler enforces these at compile time. The JVM additionally performs runtime access checks when using reflection.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Access modifiers draw circles of visibility around your code — from a locked diary (`private`) to a public notice board (`public`).

> An office building: `private` is your personal desk drawer (only you), package-private is the shared filing cabinet in your team room (colleagues on your floor), `protected` is the parent-company intranet (your company and subsidiaries), `public` is the company website (the whole world).

**One insight:** The default rule should be `private`. Promote to a wider access level only when a specific, justified caller needs access — not speculatively.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Access is checked at compile time by the Java compiler and at runtime by the JVM for reflective access
2. Four levels form a strict hierarchy: `private` ⊂ package-private ⊂ `protected` ⊂ `public`
3. Access modifiers apply to class members (fields, methods, constructors) and to top-level class declarations
4. A top-level class can only be `public` or package-private — never `private` or `protected`
5. Inner (nested) classes can use all four levels including `private`

**DERIVED DESIGN:** Access modifiers implement encapsulation at the language level, separating a class's public API from its internal implementation. This enables the Open/Closed Principle: the internal implementation can change freely without affecting callers, as long as the public API contract is preserved. Package-private is the module-boundary tool in the absence of the Java Module System.

**THE TRADE-OFFS:**
- **Gain:** Enforced encapsulation, smaller public API surface, freedom to refactor internals, security by default
- **Cost:** Over-restricting access forces boilerplate getters/setters and can impede testing (test classes may need package-private access to internals); under-restricting creates implicit APIs that can never be safely removed

---

### 🧪 Thought Experiment

**SETUP:** A `BankAccount` class holds a `balance` field.

**WHAT HAPPENS WITHOUT ACCESS MODIFIERS (public field):** Any class in any package can write `account.balance = -1_000_000`. There is no way to enforce that balance never goes negative. Every caller is a potential mutation site. Adding a validation rule requires finding and auditing every assignment across the entire codebase.

**WHAT HAPPENS WITH `private` + public methods:** `balance` is `private`. The only way to change it is through `deposit(amount)` and `withdraw(amount)`. Both methods validate the amount. The invariant "balance >= 0" is enforced in exactly one place. All callers are automatically protected. Changing the validation rule requires editing one method.

**THE INSIGHT:** `private` fields with public methods is not just a style convention — it is the mechanism that makes invariants enforceable. The access modifier is the lock; the public method is the secure door with a guard.

---

### 🧠 Mental Model / Analogy

> Think of a class as a building with four different badge-access zones. `private` is the server room — only the building's own systems can enter. Package-private is the shared workspace — colleagues in the same office can enter freely. `protected` is the parent-company boardroom — your team and any subsidiary company that acquired your team can enter. `public` is the lobby — anyone from the street can walk in.

- `private` → server room: tightest control, one class only
- Package-private → shared workspace: team access, same `package`
- `protected` → subsidiary boardroom: package + all subclasses
- `public` → lobby: no restriction, entire classpath

Where this analogy breaks down: `protected` is often surprising — it grants access to ALL subclasses anywhere on the classpath, not just subclasses in the same package. This is wider access than most developers expect.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Access modifiers control who can read or change a piece of code. `private` means only the class itself, `public` means anyone. Use `private` for internals, `public` for the things you want other code to call.

**Level 2 — How to use it (junior developer):**
Mark all fields `private`. Provide `public` getters and setters only for fields that genuinely need external access. Mark internal helper methods `private`. Use `public` for methods that are part of your class's API contract. When in doubt, start `private` and widen only when needed — it is easy to promote access; impossible to restrict it once callers depend on it.

**Level 3 — How it works (mid-level engineer):**
The compiler resolves access at each call site using the declared type of the receiver and the access flag stored in the `.class` file. `private` is encoded as `ACC_PRIVATE` in the bytecode. The JVM verifies access on every `invokevirtual`, `invokestatic`, and field access instruction. When you use `Method.setAccessible(true)` in reflection, the JVM bypasses access checks — this requires `ReflectPermission` in a security manager and is blocked by the Java Module System in Java 9+.

**Level 4 — Why it was designed this way (senior/staff):**
Java deliberately chose compile-time access enforcement rather than runtime-only. This pushes access violations to the earliest possible point in the development cycle. Package-private was intended as a module boundary — before the Java Module System (JPMS, Java 9), packages were the primary encapsulation unit for library authors. `protected` grants access to subclasses specifically to support the Template Method pattern — but this coupling is precisely why Bloch advises "favour composition over inheritance": `protected` creates a permanent coupling between superclass and subclass internals. The Java Module System (`module-info.java`) adds a fifth level above `public` — `exports` — controlling which packages are accessible outside the module regardless of their class-level `public` visibility.

---

### ⚙️ How It Works (Mechanism)

**Visibility rules table:**
```
┌─────────────────────────────────────────────────┐
│ Level          │ Same  │ Same  │ Sub-  │ Other  │
│                │ Class │ Pkg   │ class │ Pkg    │
├────────────────┼───────┼───────┼───────┼────────┤
│ private        │  YES  │  NO   │  NO   │  NO    │
│ package-priv.  │  YES  │  YES  │  NO*  │  NO    │
│ protected      │  YES  │  YES  │  YES  │  NO    │
│ public         │  YES  │  YES  │  YES  │  YES   │
└─────────────────────────────────────────────────┘
* unless subclass is in same package
```

**Bytecode representation:**
```
┌──────────────────────────────────────────────────┐
│ Method descriptor in .class file:                │
│   ACC_PUBLIC  ACC_PRIVATE  ACC_PROTECTED         │
│   (no flag = package-private)                    │
│                                                  │
│ JVM access check on invokevirtual:               │
│   caller class → resolve method ref              │
│   → check ACC_* flags vs caller package/class    │
│   → allow or throw IllegalAccessError            │
└──────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (field access through method):**
```
ExternalCaller.java
  │  ← YOU ARE HERE
  │
  ├─ account.getBalance()  → public method
  │       │
  │       └─ BankAccount.getBalance()
  │               └─ return this.balance
  │                     (private field —
  │                      accessible within
  │                      BankAccount only)
  │
  └─ result returned to caller
```

**FAILURE PATH:**
```
ExternalCaller.java
  ├─ account.balance = 999   // compile error!
  │     "balance has private access in BankAccount"
  │
  └─ reflection bypass:
       field.setAccessible(true) // works in unnamed
       // module; blocked by JPMS in Java 9+ modules
```

**WHAT CHANGES AT SCALE:**
- Java 9 Module System adds `exports` / `opens` / `requires` on top of class-level modifiers
- Frameworks like Spring use reflection + `setAccessible(true)` to inject `private` fields — this is why `@Autowired` on private fields works at runtime
- Testing strategies: package-private scope lets test classes in the same package access internals without reflection

---

### 💻 Code Example

**BAD — public fields, no encapsulation:**
```java
// BAD: public fields expose internals directly
public class BankAccount {
    public long balance;      // any code mutates!
    public String ownerId;    // no validation
    public List<Tx> history;  // mutable reference
}

// Any caller can do:
account.balance = -1_000_000L; // invariant broken
account.history.clear();       // audit log destroyed
```

**GOOD — private fields, controlled access:**
```java
// GOOD: private fields with invariant-enforcing
//       public methods
public class BankAccount {

    private long balanceCents;
    private final String ownerId;
    private final List<Tx> history = new ArrayList<>();

    public BankAccount(String ownerId,
                       long initialCents) {
        if (initialCents < 0)
            throw new IllegalArgumentException(
                "Initial balance must be >= 0");
        this.ownerId = Objects.requireNonNull(ownerId);
        this.balanceCents = initialCents;
    }

    // GOOD: read-only access to balance
    public long getBalanceCents() {
        return balanceCents;
    }

    // GOOD: mutation through validated method
    public void deposit(long cents) {
        if (cents <= 0)
            throw new IllegalArgumentException(
                "Deposit must be positive");
        balanceCents += cents;
        history.add(new Tx("DEPOSIT", cents));
    }

    // GOOD: defensive copy prevents mutation
    public List<Tx> getHistory() {
        return Collections.unmodifiableList(history);
    }

    // GOOD: package-private for tests
    void resetForTest() { history.clear(); }

    // GOOD: private helper — not part of API
    private void recordAudit(String event) {
        // internal only
    }
}
```

---

### ⚖️ Comparison Table

| Modifier | Same Class | Same Package | Subclass | Everywhere | Keyword |
|---|---|---|---|---|---|
| Private | ✅ | ❌ | ❌ | ❌ | `private` |
| Package-private | ✅ | ✅ | ❌ | ❌ | *(none)* |
| Protected | ✅ | ✅ | ✅ | ❌ | `protected` |
| Public | ✅ | ✅ | ✅ | ✅ | `public` |

| Level | Typical Use |
|---|---|
| `private` | All fields; internal helper methods |
| Package-private | Package-internal APIs; test hooks |
| `protected` | Template method hooks for subclasses |
| `public` | Public API: service methods, constructors, DTOs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `protected` means "subclass only" | `protected` also grants access to ALL classes in the same package, even non-subclasses |
| Private fields are completely inaccessible from outside | Reflection with `field.setAccessible(true)` can bypass `private` in unnamed modules; the Java Module System restricts this |
| Package-private is the safest default for class members | `private` is safest; package-private should be a deliberate choice when package-level sharing is needed |
| `public` class means all its members are public | A `public` class can have `private`, package-private, and `protected` members; class visibility and member visibility are independent |
| Access modifiers affect performance | Access modifiers have zero runtime performance overhead — they are compile-time constructs only; the JVM does not check them on normal (non-reflective) calls |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Unintentional public API surface**

**Symptom:** A refactor breaks client code in a different team's repository. An internal helper method was `public` and became a de-facto API dependency.

**Root Cause:** Default to `public` habit — developers mark everything public "just in case" or to avoid compiler errors during rapid development, then forget to restrict access.

**Diagnostic:**
```bash
# Find all public methods in a package
javap -p target/classes/com/example/Service.class \
  | grep "public"
# Compare against intended public API contract
# Use ArchUnit to enforce rules programmatically
```

**Fix:**
```java
// BAD: internal helper is accidentally public
public class PaymentProcessor {
    public void validateCard(Card c) { ... }
    public String formatCvv(String cvv) { ... }
}

// GOOD: helper is private; only entry point is public
public class PaymentProcessor {
    public PaymentResult process(Payment p) { ... }
    private void validateCard(Card c) { ... }
    private String formatCvv(String cvv) { ... }
}
```

**Prevention:** Apply ArchUnit or Checkstyle rules to enforce access-level policies at CI time.

---

**Mode 2: `protected` field mutated by unintended subclass**

**Symptom:** A class that extends a library base class accidentally reads or mutates a `protected` field that the base class treats as an internal implementation detail. A library upgrade changes the field's semantics, breaking the subclass silently.

**Root Cause:** `protected` fields couple the subclass to the superclass's internal representation — a violation of encapsulation between parent and child.

**Diagnostic:**
```bash
grep -rn "protected.*=" src/ | grep -v "final"
# Protected non-final fields are candidates for
# accidental mutation by subclasses
```

**Fix:**
```java
// BAD: protected mutable field
public abstract class BaseService {
    protected int retryCount = 3; // subclass mutates!
}

// GOOD: protected accessor method
public abstract class BaseService {
    private int retryCount = 3;

    protected int getRetryCount() {
        return retryCount;
    }
}
```

**Prevention:** Prefer `protected` methods over `protected` fields. Mark `protected` fields `final` wherever possible.

---

**Mode 3: Test unable to access internal state**

**Symptom:** Unit test needs to assert internal state or inject a dependency that is declared `private`. Test uses reflection or production code is modified to `public` just for testing.

**Root Cause:** Test is trying to test internal implementation rather than observable behaviour — a testing strategy problem. Or the class needs package-private test hooks.

**Diagnostic:**
```bash
grep -rn "setAccessible(true)" src/test/
# Each occurrence is a test smell: either
# test the public API, or add a package-private hook
```

**Fix:**
```java
// BAD: reflection to access private in tests
Field f = MyService.class
    .getDeclaredField("counter");
f.setAccessible(true);
int v = (int) f.get(service);

// GOOD option 1: test observable behaviour
myService.process(5_items);
assertEquals(5, myService.getProcessedCount());

// GOOD option 2: package-private test hook
// (test class in same package under src/test/)
// In MyService.java:
int getCounterForTest() { return counter; } // pkg-priv
```

**Prevention:** Write tests against the public API by default. Use package-private hooks sparingly for state verification in complex classes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language — class, field, method declarations
- Encapsulation — the OOP principle access modifiers enforce

**Builds On This (learn these next):**
- Spring Core — `@Autowired` on `private` fields uses reflection; Spring recommends constructor injection which works with any access level
- Design Patterns — Factory Method pattern relies on `protected` constructors; Singleton uses `private` constructor
- SOLID Principles — Open/Closed Principle and Dependency Inversion both depend on well-defined public interfaces

**Alternatives / Comparisons:**
- Java Module System — adds `exports`/`opens` directives for module-level encapsulation above class-level modifiers
- Principle of Least Privilege — security principle that access modifiers implement in code
- Kotlin `internal` modifier — package-private equivalent scoped to the compilation module

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ WHAT IT IS   │ 4-level visibility control system   ║
║ PROBLEM      │ Uncontrolled mutation, implicit APIs║
║ KEY INSIGHT  │ private by default; widen only when ║
║              │ a specific caller justifies it      ║
║ USE WHEN     │ Always — every member needs a level ║
║ AVOID WHEN   │ Public fields (use methods instead) ║
║ TRADE-OFF    │ Safety vs friction (more boilerplate)║
║ ONE-LINER    │ private field + public getter/setter ║
║ NEXT EXPLORE │ Encapsulation, SOLID, Java Modules  ║
╚════════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(E — First Principles)** Java's `protected` modifier grants access to subclasses AND to classes in the same package. These are two very different trust relationships. Why do you think they were combined into a single keyword, and what problems does this create when designing library APIs intended for subclassing?

2. **(A — System Interaction)** Spring Framework injects dependencies into `private` fields using `field.setAccessible(true)`. The Java Module System (Java 9+) blocks this by default unless the package is `open`. How does this interaction between Spring's reflection-based DI, access modifiers, and the module system affect how you should structure a Spring application targeting Java 17+?

3. **(C — Design Trade-off)** A teammate proposes making all DAO fields `package-private` (no modifier) so that integration tests in the same package can directly set up test state. Compare this approach against using the public constructor with valid parameters, test fixtures, or an in-memory database. What are the long-term maintenance costs of each strategy?
