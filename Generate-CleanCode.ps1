
# Generate-CleanCode.ps1
# Generates all 10 Clean Code dictionary entries

$outDir = "C:\ASK\MyWorkspace\sk-keys\docs\Clean Code"
if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────
function Write-Entry($num, $name, $filename, $tags, $difficulty, $dependsOn, $usedBy, $tldr,
    $textbook, $easy, $elaborated, $firstPrinciples, $whyExist, $mentalModel,
    $howItWorks, $howItConnects, $codeExample, $flow, $misconceptions,
    $pitfalls, $related, $qrc, $thinkAbout) {

    $path = Join-Path $outDir $filename
    $content = @"
---
number: $num
category: Clean Code
difficulty: $difficulty
depends_on: $dependsOn
used_by: $usedBy
tags: $tags
---

# 🧹 $num — $name

$tags

⚡ TL;DR — $tldr

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #$num        │ Category: Clean Code                 │ Difficulty: $difficulty         │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ $dependsOn                                               │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ $usedBy                                             │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

$textbook

---

## 🟢 Simple Definition (Easy)

$easy

---

## 🔵 Simple Definition (Elaborated)

$elaborated

---

## 🔩 First Principles Explanation

$firstPrinciples

---

## ❓ Why Does This Exist (Why Before What)

$whyExist

---

## 🧠 Mental Model / Analogy

$mentalModel

---

## ⚙️ How It Works (Mechanism)

$howItWorks

---

## 🔄 How It Connects (Mini-Map)

$howItConnects

---

## 💻 Code Example

$codeExample

---

## 🔁 Flow / Lifecycle

$flow

---

## ⚠️ Common Misconceptions

$misconceptions

---

## 🔥 Pitfalls in Production

$pitfalls

---

## 🔗 Related Keywords

$related

---

## 📌 Quick Reference Card

``````
$qrc
``````

---

## 🧠 Think About This Before We Continue

$thinkAbout
"@
    Set-Content -Path $path -Value $content -Encoding UTF8
    Write-Host "  ✅ Created: $filename"
}

# ──────────────────────────────────────────────────────────────────────────────
# 424 — Cohesion
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "424" "Cohesion" "🧹 424 — Cohesion.md" `
  "#cleancode #architecture #foundational" "★★☆" "SRP, Module Design" "Coupling, Refactoring" `
  "How focused and related the responsibilities inside a single module are." `
  "Cohesion is the degree to which the elements of a module (class, method, package) belong together — how logically related and focused they are on a single purpose or concept." `
  "Cohesion is about **how well a module sticks to one job**. High cohesion = everything inside the class belongs together. Low cohesion = class does many unrelated things." `
  "High cohesion means a class has a clear, single purpose. Every method and field directly supports that purpose. Low cohesion means the class juggles unrelated responsibilities — it becomes hard to understand, test, and change. Cohesion and coupling are the two fundamental dimensions of module quality." `
  @"
**The core problem:**
Classes that grew over time by adding unrelated responsibilities become hard to understand and maintain.

**The insight:**
> "A module should have one reason to change" — if everything inside serves one purpose, changes stay local.

Low cohesion:
  UserService { login(), sendEmail(), generateReport(), resizeImage() }

High cohesion:
  UserService { login(), logout(), changePassword() }
  EmailService { sendEmail(), sendBulkEmail() }
"@ `
  "Without cohesion, changes to one feature accidentally break unrelated features in the same class. Tests become enormous. Reuse becomes impossible." `
  "> Think of a Swiss Army knife vs a chef's knife. The chef's knife does one thing perfectly — that's high cohesion. The Swiss Army knife does many things adequately — that's low cohesion." `
  @"
Types of cohesion (weakest → strongest):

  Coincidental  - elements grouped randomly
  Logical       - elements do similar things (e.g., all I/O)
  Temporal      - elements run at the same time (e.g., startup)
  Procedural    - elements follow a sequence
  Communicational - elements work on the same data
  Sequential    - output of one feeds the next
  Functional    - elements all contribute to a single task  ← IDEAL
"@ `
  @"
         [SRP]
            ↓
[Low Cohesion] → [Refactor] → [High Cohesion]
                                    ↑
                               [Coupling ↓]
"@ `
  @"
```java
// LOW cohesion — class does too many unrelated things
class UserManager {
    void createUser(String name) { /* ... */ }
    void sendWelcomeEmail(String email) { /* ... */ }   // email concern
    void generateUserReport() { /* ... */ }             // reporting concern
    byte[] resizeProfilePicture(byte[] img) { /* ... */ } // image concern
}

// HIGH cohesion — each class has one focused purpose
class UserService {
    void createUser(String name) { /* ... */ }
    void deactivateUser(long id) { /* ... */ }
    Optional<User> findById(long id) { /* ... */ }
}

class UserEmailService {
    void sendWelcomeEmail(String email) { /* ... */ }
    void sendPasswordReset(String email) { /* ... */ }
}
```
"@ `
  @"
1. Class starts with one responsibility
        ↓
2. Features get added to the same class (convenience)
        ↓
3. Class becomes a "god class" with low cohesion
        ↓
4. Refactor: extract responsibilities into focused classes
        ↓
5. High cohesion restored
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| More methods = better cohesion | Fewer, focused methods = higher cohesion |
| Cohesion is about class size | Cohesion is about relatedness, not size |
| High cohesion means small classes | A class can be large and cohesive |
| It only applies to classes | Cohesion applies at method, class, and package level |
"@ `
  @"
**Pitfall 1: God Classes**
Gradually adding methods to an existing class is the most common cause of low cohesion.
Refactor: identify distinct responsibilities and extract them into separate classes.

**Pitfall 2: Utility Classes**
A class named `Utils` or `Helper` is almost always low cohesion. Split into focused helpers.

**Pitfall 3: Over-splitting**
Don't sacrifice cohesion for tiny classes — a class with 1 method per class can be worse. Balance is key.
"@ `
  @"
- **SRP (Single Responsibility Principle)** — formal principle that enforces high cohesion
- **Coupling** — the opposite dimension; reduce both for clean modules
- **Refactoring** — the activity of improving cohesion without changing behavior
- **God Class** — anti-pattern resulting from low cohesion
- **Package/Module Design** — cohesion applies at higher levels too
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Everything inside a module belongs together   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Designing or reviewing class responsibilities  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't over-split — tiny 1-liner classes hurt  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Cohesion = how much a module sticks to one   │
│              │  single, clear purpose"                        │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Coupling → SRP → Refactoring                  │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** Can a class have high cohesion but also high coupling? What would that look like?
**Q2.** What is the difference between functional cohesion and sequential cohesion?
**Q3.** How does package-level cohesion differ from class-level cohesion?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 425 — Coupling
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "425" "Coupling" "🧹 425 — Coupling.md" `
  "#cleancode #architecture #foundational" "★★☆" "Cohesion, Module Design" "Dependency Injection, DIP, Refactoring" `
  "The degree to which one module depends on the internals of another." `
  "Coupling is the measure of interdependence between software modules. Tight (high) coupling means modules depend heavily on each other's internal details, making changes risky. Loose (low) coupling means modules interact through stable interfaces, making them independently changeable and testable." `
  "Coupling is about **how much modules know about each other**. Tight coupling = change one thing, break another. Loose coupling = change freely without fear." `
  "When modules are tightly coupled, a change in one ripples through many others. Loose coupling is achieved by depending on abstractions (interfaces) rather than concrete implementations, minimizing the number of dependencies, and keeping what each module exposes to a minimum." `
  @"
**The core problem:**
Systems where classes directly instantiate and call other concrete classes become rigid — you cannot change one module without changing all its callers.

**The insight:**
> "Depend on abstractions, not concretions." (DIP)

Tight coupling:
  class OrderService {
      PayPalGateway gateway = new PayPalGateway();  // concrete dependency
  }

Loose coupling:
  class OrderService {
      PaymentGateway gateway;  // depends on interface
      OrderService(PaymentGateway gw) { this.gateway = gw; }
  }
"@ `
  "Without loose coupling, you cannot unit test in isolation (can't mock), cannot swap implementations (PayPal → Stripe), and cannot reuse modules independently." `
  "> Think of electrical outlets and plugs. The outlet (module) doesn't know what device is plugged in — it only exposes a standard interface (socket). Any device with the right plug works. That's loose coupling." `
  @"
Coupling types (loosest → tightest):

  Message       - communicate via messages only
  Data          - share only primitive parameters
  Stamp         - share composite data structures
  Control       - one module controls another's flow (flag passing)
  External      - both depend on same external format/tool
  Common        - both access shared global data
  Content       - one directly modifies another's internals  ← WORST
"@ `
  @"
        [DIP]
           ↓
[Concrete Dep] → [Interface] → [Loose Coupling]
                                      ↑
                                [Cohesion ↑]
"@ `
  @"
```java
// TIGHT coupling — OrderService depends on concrete PayPalGateway
class OrderService {
    private PayPalGateway gateway = new PayPalGateway(); // hard dependency

    void placeOrder(Order order) {
        gateway.charge(order.total()); // cannot swap, cannot mock
    }
}

// LOOSE coupling — depends on interface, injected externally
interface PaymentGateway {
    void charge(double amount);
}

class OrderService {
    private final PaymentGateway gateway;

    OrderService(PaymentGateway gateway) {  // DI = loose coupling
        this.gateway = gateway;
    }

    void placeOrder(Order order) {
        gateway.charge(order.total()); // works with any PaymentGateway impl
    }
}
```
"@ `
  @"
1. Module A needs Module B
        ↓
2. Option A: A directly instantiates B (tight coupling)
   Option B: A depends on interface I, B implements I (loose coupling)
        ↓
3. Loose: A never imports B; B can be swapped freely
        ↓
4. Testing A: inject a mock of I — no real B needed
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Coupling is always bad | Some coupling is unavoidable; minimize it |
| Use interfaces everywhere | Interfaces for external boundaries; pragmatic for internals |
| Coupling = number of imports | Coupling = dependency on internals, not just count |
| DI frameworks eliminate coupling | They manage coupling — you still design it |
"@ `
  @"
**Pitfall 1: Circular Dependencies**
A depends on B, B depends on A. Even with interfaces. Break cycles by introducing a third module or an event.

**Pitfall 2: Leaking Implementation Details**
Returning a concrete `ArrayList` instead of `List` from a public API couples callers to the implementation.

**Pitfall 3: God Object as Hub**
One class that everything else imports creates a star-topology coupling. Any change to it breaks everything.
"@ `
  @"
- **Cohesion** — the twin dimension; aim for high cohesion + low coupling
- **DIP (Dependency Inversion Principle)** — the principle that enforces loose coupling
- **Dependency Injection** — the technique that implements loose coupling
- **SOLID** — coupling and cohesion underpin all 5 SOLID principles
- **Interface** — the mechanism for decoupling in OOP
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Modules should know as little as possible     │
│              │ about each other's internals                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always — loose coupling is the goal           │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Over-engineering tiny scripts with interfaces  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Depend on interfaces, not implementations"    │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Cohesion → DIP → Dependency Injection         │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** What is the difference between afferent coupling (Ca) and efferent coupling (Ce)?
**Q2.** How does event-driven architecture reduce coupling compared to direct calls?
**Q3.** Can you have zero coupling in a real system? Why or why not?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 426 — Abstraction
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "426" "Abstraction" "🧹 426 — Abstraction.md" `
  "#cleancode #oop #foundational" "★☆☆" "Interface, Polymorphism" "Encapsulation, Coupling, API Design" `
  "Hiding implementation details and exposing only what is necessary through a simplified interface." `
  "Abstraction is the process of hiding internal complexity and exposing only a relevant interface to the outside world. It allows users to work with concepts at a higher level without needing to understand underlying implementations." `
  "Abstraction means **showing what a thing does, not how it does it**. You use a car without knowing how the engine works — the steering wheel is the abstraction." `
  "Abstraction occurs at many levels in software: a method hides lines of code, a class hides data and logic, an interface hides implementations, a microservice hides an entire subsystem. Each layer lets you work at the right level of detail without getting lost in lower-level concerns." `
  @"
**The core problem:**
Without abstraction, every caller must understand all implementation details. Any internal change breaks all callers.

**The insight:**
> "Separate what a thing IS from what it DOES from HOW it does it."

  What it IS  → type / interface
  What it DOES → public methods (contract)
  HOW it does it → private implementation (hidden)
"@ `
  "Without abstraction, you cannot change how something is implemented without rewriting all its callers. Code becomes tightly coupled to implementation details." `
  "> A TV remote is an abstraction. You press 'Volume Up' without knowing whether the TV uses IR, RF, or Bluetooth, or any circuit details. The interface is stable; the implementation can change." `
  @"
Levels of abstraction in software:

  High   [Business Logic: processOrder()]
         [Service Layer: OrderService]
         [Repository: OrderRepository (interface)]
         [JPA/SQL Implementation]
  Low    [JDBC / Database Driver]

Each level only communicates with the level directly below it.
"@ `
  @"
[Implementation Details]
          ↓ hidden
    [Abstraction Layer]  ← public interface
          ↓ used by
    [Client Code]
"@ `
  @"
```java
// Without abstraction: client knows HOW sorting works
int[] arr = {3, 1, 2};
// manual bubble sort...

// With abstraction: client knows WHAT, not HOW
Arrays.sort(arr);  // implementation hidden

// Interface as abstraction
interface MessageSender {
    void send(String message, String recipient);
}

class EmailSender implements MessageSender { /* hidden SMTP details */ }
class SmsSender  implements MessageSender { /* hidden Twilio details */ }

// Client only depends on abstraction
class NotificationService {
    MessageSender sender; // doesn't know or care which implementation
    void notify(String msg, String to) { sender.send(msg, to); }
}
```
"@ `
  @"
1. Identify what callers actually need (contract)
        ↓
2. Define interface — public methods only
        ↓
3. Hide all implementation details (private)
        ↓
4. Allow multiple implementations of same interface
        ↓
5. Client code never changes when implementation changes
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Abstraction = interface keyword | Abstraction is a principle; interfaces are one tool |
| More abstraction = better code | Wrong abstraction is worse than none (leaky abstractions) |
| Abstract classes = abstraction | Abstract classes are one mechanism; true abstraction is conceptual |
| Abstraction hides everything | It hides details irrelevant to the caller, not everything |
"@ `
  @"
**Pitfall 1: Leaky Abstractions**
An abstraction that forces callers to know implementation details (e.g., IOException from a high-level API).
Fix: translate low-level exceptions and data into the right abstraction level.

**Pitfall 2: Wrong level of abstraction**
Mixing low-level details (SQL) with high-level business logic in the same method.
Fix: separate layers — one layer per level of abstraction.

**Pitfall 3: Over-abstraction**
Three layers of interfaces for a feature used in one place — adds complexity with no benefit.
Fix: abstract at natural seams, not everywhere.
"@ `
  @"
- **Encapsulation** — hides state; abstraction hides behavior complexity
- **Polymorphism** — multiple implementations of one abstraction
- **Interface** — primary Java mechanism for defining abstractions
- **Coupling** — good abstraction reduces coupling
- **Leaky Abstraction** — when hidden details bleed through the interface
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Show WHAT, hide HOW                          │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Defining boundaries between modules/layers    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Over-abstracting trivial one-off code        │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Abstractions let you change the HOW without  │
│              │  touching the WHO uses it"                    │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Encapsulation → Polymorphism → Interface      │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** What makes an abstraction "leaky"? Give an example from a standard library.
**Q2.** How does the Repository pattern use abstraction to isolate business logic from database details?
**Q3.** At what layer should you break the abstraction barrier intentionally, and why?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 427 — Encapsulation
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "427" "Encapsulation" "🧹 427 — Encapsulation.md" `
  "#cleancode #oop #foundational" "★☆☆" "Abstraction, Class Design" "Cohesion, Information Hiding" `
  "Bundling data and the methods that operate on it together, while restricting direct access to the internal state." `
  "Encapsulation is the OOP principle of bundling data (fields) and the behavior that operates on it (methods) into a single unit (class), and controlling access to the internal state through visibility modifiers. It enforces invariants by ensuring state can only be changed through controlled methods." `
  "Encapsulation means **keeping the inside of a class private and only allowing access through defined doors (methods)**. It prevents external code from corrupting the object's state." `
  "Without encapsulation, any code anywhere can read and modify an object's fields directly — leading to invalid states, hard-to-find bugs, and fragile code. Encapsulation enforces invariants by putting all state changes through methods that validate preconditions." `
  @"
**The core problem:**
If fields are public, anyone can set name = null, age = -5, balance = -1000000. Invariants cannot be enforced.

**The insight:**
> "An object should be responsible for maintaining its own invariants. External code should not be able to put it into an invalid state."

  public int balance;  // anyone can set to -∞
  vs.
  private int balance;
  public void withdraw(int amount) {
      if (amount > balance) throw new InsufficientFundsException();
      balance -= amount;
  }
"@ `
  "Without encapsulation, objects cannot enforce the rules about what values they hold. Every caller must remember to validate — and eventually someone won't." `
  "> Think of a vending machine. You interact with it through buttons and a coin slot — the internal mechanism is hidden. You cannot directly grab items from the shelf. The machine controls its own state." `
  @"
Visibility levels (Java):

  private    → only this class
  (package)  → this class + same package
  protected  → this class + subclasses
  public     → everyone

The rule: make everything as private as possible.
Expose only what callers strictly need.
"@ `
  @"
     [External Code]
           ↓ calls public methods
   [setter/getter with validation]
           ↓ controls access to
     [private fields]  ← invariants enforced here
"@ `
  @"
```java
// BAD — no encapsulation, anyone can corrupt state
class BankAccount {
    public int balance;  // anyone can set balance = -999
}

// GOOD — encapsulated; invariants enforced
class BankAccount {
    private int balance;         // hidden
    private final String owner;  // immutable

    public BankAccount(String owner, int initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("Negative balance");
        this.owner = owner;
        this.balance = initialBalance;
    }

    public void deposit(int amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        balance += amount;
    }

    public void withdraw(int amount) {
        if (amount > balance) throw new IllegalStateException("Insufficient funds");
        balance -= amount;
    }

    public int getBalance() { return balance; }  // read-only access
}
```
"@ `
  @"
1. Define object's invariants (rules that must always hold)
        ↓
2. Make fields private
        ↓
3. Provide controlled access via methods that enforce invariants
        ↓
4. Validate all inputs in setters / constructors
        ↓
5. Object can never be in an invalid state externally
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Encapsulation = just adding getters/setters | Getters/setters on everything breaks encapsulation |
| Private means secure | Private is about design boundaries, not security |
| Encapsulation = hiding everything | Expose what callers need; hide what they shouldn't change |
| Records violate encapsulation | Records are immutable — their exposure is safe |
"@ `
  @"
**Pitfall 1: Anemic Domain Model**
Classes with all-public getters/setters and no behavior are not encapsulated. Any caller can build invalid state.
Fix: push behavior INTO the class; remove setters where possible.

**Pitfall 2: Returning Mutable Internals**
```java
public List<Item> getItems() { return items; }  // caller can add/remove!
public List<Item> getItems() { return Collections.unmodifiableList(items); } // safe
```

**Pitfall 3: Exposing Internal Types**
Returning a private nested type exposes the implementation; wrap it in a DTO or interface.
"@ `
  @"
- **Abstraction** — encapsulation implements abstraction for state
- **Cohesion** — encapsulated classes tend to be more cohesive
- **Immutability** — extreme encapsulation where state never changes
- **Information Hiding** — the broader principle; encapsulation is one mechanism
- **Anemic Domain Model** — anti-pattern that breaks encapsulation
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Bundle data + behavior; protect state via     │
│              │ controlled access                             │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always in OOP — make fields private by default│
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ DTOs / value objects: expose all, change none │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "An object owns its state; callers interact   │
│              │  through methods that enforce the rules"       │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Abstraction → Polymorphism → Immutability     │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** Why is a class with only public getters/setters considered to have broken encapsulation?
**Q2.** How do Java Records handle encapsulation differently from regular classes?
**Q3.** What is the difference between encapsulation and information hiding?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 428 — Polymorphism
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "428" "Polymorphism" "🧹 428 — Polymorphism.md" `
  "#cleancode #oop #foundational" "★★☆" "Abstraction, Inheritance, Interface" "Strategy Pattern, OCP, Dispatch" `
  "The ability of different types to be treated as the same type through a shared interface, each responding differently to the same message." `
  "Polymorphism allows objects of different classes to be treated uniformly through a shared supertype (interface or abstract class). At runtime, the correct implementation is selected dynamically — enabling extensibility without modifying existing code." `
  "Polymorphism means **one interface, many implementations**. You call the same method on different objects and each responds in its own way." `
  "Polymorphism enables replacing `if-else` / `switch` chains with a clean type hierarchy. Instead of checking the type at runtime, you call the same method and let each class decide what to do. This is the mechanism that makes the Open/Closed Principle possible." `
  @"
**The core problem:**
Code littered with type-checking (instanceof / switch on type) breaks whenever a new type is added.

**The insight:**
> "Don't ask what type something is — just call the method. Each type knows what to do."

  // WITHOUT polymorphism
  if (shape instanceof Circle) drawCircle((Circle)shape);
  else if (shape instanceof Square) drawSquare((Square)shape);

  // WITH polymorphism
  shape.draw();  // each type handles it — new types added without touching caller
"@ `
  "Without polymorphism, adding a new type means finding and updating every if-else chain that checks for types — a maintenance nightmare that grows linearly with new types." `
  "> Think of a power outlet. A phone charger, laptop charger, or lamp — they all plug into the same outlet (same interface). The outlet just delivers power; each device handles it differently (polymorphism)." `
  @"
Types of polymorphism:

  Subtype    - method overriding in class hierarchy (runtime dispatch)
  Parametric - generics: List<T> works for any T
  Ad-hoc     - method overloading: same name, different parameter types

Runtime dispatch (subtype polymorphism):
  Shape ref = new Circle();
  ref.draw();  // JVM looks up Circle.draw() at runtime via vtable
"@ `
  @"
[Interface / Abstract Class]
           ↓ implemented by
   [ClassA]  [ClassB]  [ClassC]
           ↓ called as
   shape.draw() → JVM picks right implementation
"@ `
  @"
```java
// Abstract type
interface Shape {
    double area();
    void draw();
}

// Multiple implementations
class Circle implements Shape {
    double radius;
    @Override public double area() { return Math.PI * radius * radius; }
    @Override public void draw() { System.out.println("Drawing circle"); }
}

class Rectangle implements Shape {
    double w, h;
    @Override public double area() { return w * h; }
    @Override public void draw() { System.out.println("Drawing rectangle"); }
}

// Polymorphic usage — caller doesn't care about concrete type
List<Shape> shapes = List.of(new Circle(), new Rectangle());
for (Shape s : shapes) {
    s.draw();           // runtime dispatch
    System.out.println(s.area());
}
// Adding Triangle? Just implement Shape — no existing code changes.
```
"@ `
  @"
1. Define interface / abstract class with contract
        ↓
2. Implement concrete classes
        ↓
3. Caller holds reference to interface type
        ↓
4. At runtime: JVM uses vtable to dispatch to actual implementation
        ↓
5. New type? Implement interface — no existing caller code changes
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Polymorphism requires inheritance | Interfaces (no inheritance) also give polymorphism |
| It's only useful in large systems | Eliminates if-else chains even in small code |
| Overloading is the main use | Subtype polymorphism (overriding) is the powerful form |
| It has runtime overhead | JVM vtable dispatch is near-zero cost in practice |
"@ `
  @"
**Pitfall 1: Instanceof checks defeat polymorphism**
If you're doing `instanceof` to pick different behavior, you're not using polymorphism.
Fix: move the behavior into the class itself via overriding.

**Pitfall 2: Fragile base class problem**
When a superclass changes, all subclasses may break unexpectedly.
Fix: favor interfaces over inheritance; use composition.

**Pitfall 3: Violating LSP**
Overriding a method with behavior inconsistent with the parent breaks the polymorphism contract.
Fix: follow the Liskov Substitution Principle.
"@ `
  @"
- **Abstraction** — polymorphism is how abstraction is realized at runtime
- **Inheritance** — one mechanism for achieving subtype polymorphism
- **Interface** — the cleanest mechanism for polymorphism in Java
- **Strategy Pattern** — classic design pattern built entirely on polymorphism
- **OCP (Open/Closed Principle)** — polymorphism is the key enabler
- **LSP (Liskov Substitution Principle)** — defines the contract for valid polymorphism
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One interface, many implementations, runtime  │
│              │ dispatch selects the right one                │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Multiple types share behavior, or type-check  │
│              │ if-else chains are growing                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Only 1 implementation exists (no benefit yet) │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Same call, different behavior — the type     │
│              │  decides at runtime"                          │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → OCP → LSP                  │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** What is the difference between compile-time (static) and runtime (dynamic) polymorphism?
**Q2.** How does the Strategy pattern use polymorphism to replace conditional logic?
**Q3.** Why does using `instanceof` in a method indicate a missing polymorphism opportunity?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 429 — Inheritance
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "429" "Inheritance" "🧹 429 — Inheritance.md" `
  "#cleancode #oop #foundational" "★★☆" "Polymorphism, Abstraction" "LSP, Composition over Inheritance, Fragile Base Class" `
  "A mechanism where a class acquires the properties and behavior of a parent class, enabling code reuse and subtype relationships." `
  "Inheritance is the OOP mechanism by which a class (subclass) extends another class (superclass), inheriting its fields and methods. It establishes an IS-A relationship and enables subtype polymorphism. Java supports single class inheritance and multiple interface inheritance." `
  "Inheritance means **one class gets the capabilities of its parent for free**, plus can add or override behavior. It's a code-reuse mechanism and a way to say 'this is a kind of that'." `
  "Inheritance creates a compile-time relationship between classes. The subclass IS-A superclass — it can be used anywhere the superclass is expected. However, inheritance is a strong coupling — changing the superclass can break all subclasses. Favor composition for code reuse; use inheritance only for genuine IS-A relationships." `
  @"
**The core problem:**
Duplicating methods across multiple similar classes leads to maintenance nightmares.

**The insight:**
> "Extract shared behavior into a parent class. Subclasses inherit and specialize."

But: the insight has a trap. Inheritance couples subclass to superclass details forever.
Modern wisdom: "Favor composition over inheritance."
Use inheritance only when the IS-A relationship is genuine and stable.
"@ `
  "Without inheritance, you'd duplicate code across similar classes. But overusing inheritance creates fragile, deeply-coupled hierarchies where a change to the base class breaks everything below it." `
  "> Think of an employee hierarchy: Manager IS-A Employee. But be careful — a ContractEmployee might also be an Employee in payroll terms but shouldn't inherit the 'apply for promotion' behavior. The IS-A must be truly behavioral, not just conceptual." `
  @"
Inheritance hierarchy:

  Animal          (superclass)
  ├── Dog         (subclass — inherits speak(), move())
  │   └── Poodle  (sub-subclass — overrides speak())
  └── Cat         (subclass — overrides speak())

Method resolution order (MRO):
  Poodle.speak() → found? use it
  No? → Dog.speak() → found? use it
  No? → Animal.speak() → found? use it
"@ `
  @"
     [Animal]
        ↓ extends
     [Dog] ← inherits Animal methods
        ↓ extends
     [Poodle] ← overrides some methods
"@ `
  @"
```java
// Superclass
class Vehicle {
    protected int speed;
    protected String fuel;

    void accelerate(int delta) { speed += delta; }
    void brake(int delta)      { speed = Math.max(0, speed - delta); }
    String info() { return "Speed: " + speed + ", Fuel: " + fuel; }
}

// Subclass — IS-A Vehicle
class ElectricCar extends Vehicle {
    private int batteryLevel;

    ElectricCar() { this.fuel = "Electric"; }

    @Override
    String info() {
        return super.info() + ", Battery: " + batteryLevel + "%";
    }

    void charge(int percent) { batteryLevel = Math.min(100, batteryLevel + percent); }
}

// usage
Vehicle v = new ElectricCar();  // polymorphism
v.accelerate(60);
System.out.println(v.info());   // ElectricCar.info() called
```
"@ `
  @"
1. Subclass declared: class Dog extends Animal
        ↓
2. subclass gets all non-private fields and methods of Animal
        ↓
3. Subclass can OVERRIDE methods (runtime polymorphism)
        ↓
4. Subclass can EXTEND with new methods
        ↓
5. super keyword accesses parent's implementation
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Use inheritance for code reuse | Prefer composition for reuse; inheritance for IS-A |
| Deep hierarchies = good OOP | Deep hierarchies = fragile code |
| Override anything you want | Obey LSP or you break polymorphism |
| Multiple inheritance is bad in Java | Java disallows multi-class inheritance but has default methods in interfaces |
"@ `
  @"
**Pitfall 1: Fragile Base Class**
Changing a public method in a superclass silently breaks all subclasses.
Fix: favor composition; design for extension (sealed/final where appropriate).

**Pitfall 2: Overriding for convenience, not behavior**
Overriding a method just to change a side effect violates LSP.
Fix: if the subclass cannot satisfy the parent's contract, it should not extend it.

**Pitfall 3: Deep Hierarchy**
More than 2-3 levels of inheritance becomes unreadable.
Fix: flatten hierarchies; use interfaces + composition.
"@ `
  @"
- **Polymorphism** — inheritance enables subtype polymorphism
- **LSP (Liskov Substitution Principle)** — defines correct use of inheritance
- **Composition over Inheritance** — preferred modern alternative for code reuse
- **Abstract Class** — partially implemented superclass meant for extension
- **Super keyword** — access parent's implementation from a subclass
- **Fragile Base Class** — the main pitfall of deep inheritance
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ IS-A relationship: subclass acquires and      │
│              │ specializes parent behavior                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ True IS-A relationship that won't change      │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Just reusing code (use composition instead)   │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Inherit for IS-A relationships, compose for  │
│              │  HAS-A and code reuse"                        │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ LSP → Composition over Inheritance → Mixins   │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** What is the Fragile Base Class problem and how does `final` help?
**Q2.** Why does Java not support multiple class inheritance, and how do default methods partial address this?
**Q3.** When is it correct to choose composition over inheritance even when an IS-A relationship exists?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 430 — Command-Query Separation (CQS)
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "430" "Command-Query Separation (CQS)" "🧹 430 — Command-Query Separation (CQS).md" `
  "#cleancode #pattern #intermediate" "★★☆" "CQRS, API Design" "CQRS, Functional Programming, Idempotency" `
  "Every method should either change state (command) or return data (query) — never both at the same time." `
  "Command-Query Separation (CQS) is a design principle (Bertrand Meyer) stating that every method in a class should be either a Command (changes state, returns void) or a Query (returns data, produces no side effects). Mixing both makes behavior harder to reason about." `
  "CQS says: **a method should either DO something or ANSWER something — never both**. If it returns a value, it shouldn't change the world. If it changes the world, it shouldn't return a value." `
  "CQS makes code predictable. Queries can be called multiple times safely (they're side-effect free). Commands always change state. When you call a method and it BOTH modifies state AND returns a value, callers cannot safely call it twice or reason about order of calls without understanding internals." `
  @"
**The core problem:**
Methods that do both: user = userRepository.findAndMarkAccessed(id) — did it return the user? Did it increment a counter? Can I call it twice safely?

**The insight (Bertrand Meyer):**
> "Asking a question should not change the answer."

  Command: void markAccessed(long id)     → changes state, returns nothing
  Query:   Optional<User> findById(long id) → returns data, changes nothing
"@ `
  "Without CQS, calling a query method has invisible side effects. Tests become order-dependent. Caching queries is risky (the cache now blocks state changes). Concurrency becomes harder to reason about." `
  "> Like asking a librarian for a book vs returning a book. 'Where is book X?' (query — no change). 'Return this book' (command — changes state). If 'Where is book X?' also automatically checked it out to you, that would be surprising and problematic." `
  @"
Classification:
  Query   → returns value, no state change, safe to call multiple times
  Command → changes state (DB write, file write, event publish), returns void

  // VIOLATES CQS — does both
  User pop() { User u = queue.first(); queue.remove(u); return u; }

  // CQS-compliant split:
  User peek() { return queue.first(); }   // query
  void remove() { queue.removeFirst(); }  // command
"@ `
  @"
[Query]  → reads → [State]  (State unchanged)
[Command] → writes → [State]  (no return value)
"@ `
  @"
```java
// VIOLATES CQS — method changes state AND returns data
class UserService {
    // Bad: increments login count AND returns the user
    User loginAndGet(String username) {
        User user = findByUsername(username);
        user.incrementLoginCount();         // side effect
        userRepository.save(user);          // side effect
        return user;                        // also returns data
    }
}

// CQS-COMPLIANT split
class UserService {
    // Command: changes state, returns nothing
    void recordLogin(String username) {
        User user = findByUsername(username);
        user.incrementLoginCount();
        userRepository.save(user);
    }

    // Query: reads data, no side effects — safe to call multiple times
    Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }
}

// Caller:
userService.recordLogin("alice");              // command
User u = userService.findByUsername("alice")  // query — safe to call again
            .orElseThrow();
```
"@ `
  @"
1. Look at each method: does it mutate state? Does it return data?
        ↓
2. If it does both → violation
        ↓
3. Split into: void command() + T query()
        ↓
4. Queries = pure reads, safe to cache, safe to repeat
   Commands = writes, events, return void
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CQS = CQRS | CQS is a method-level principle; CQRS is an architectural pattern |
| It means nothing can return status | Commands can throw exceptions; status via events/exceptions is fine |
| Stack.pop() violates CQS | Yes — it's a known pragmatic exception for performance |
| CQS is only for domain layer | It applies everywhere: service methods, repository, controllers |
"@ `
  @"
**Pitfall 1: Incrementing counters inside queries**
`findUser()` that also updates `lastAccessedAt` — now you can't safely call queries in tests.
Fix: separate the access tracking into an explicit command.

**Pitfall 2: Builder patterns**
`builder.setName("x")` returning `this` is a CQS violation for chaining.
This is a pragmatic accepted exception — document it.

**Pitfall 3: Transactional "fetch-and-lock" patterns**
`SELECT ... FOR UPDATE` both reads and locks. CQS must be relaxed here for correctness.
Document the exception explicitly.
"@ `
  @"
- **CQRS (Command Query Responsibility Segregation)** — architectural extension of CQS at system level
- **Idempotency** — queries must be idempotent (CQS enforces this structurally)
- **Functional Programming** — pure functions = queries in CQS terms
- **Side Effects** — commands have them; queries must not
- **Event Sourcing** — often paired with CQRS, separates command/query data stores
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Methods either change state (void) or return  │
│              │ data (no side effects) — never both           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Designing service, repository, domain methods │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Known pragmatic exceptions: pop(), iterators  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Asking a question should not change the      │
│              │  answer"                                      │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Event Sourcing → Idempotency           │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** How does CQS enable safe caching of query results?
**Q2.** What is the difference between CQS (method level) and CQRS (architectural level)?
**Q3.** `Iterator.next()` violates CQS — it advances AND returns. Is this a design mistake?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 431 — Feature Flags
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "431" "Feature Flags" "🧹 431 — Feature Flags.md" `
  "#cleancode #devops #intermediate" "★★☆" "CI/CD, Canary Deployment" "Canary Releases, A/B Testing, Technical Debt" `
  "Configuration-driven switches that enable or disable features at runtime without deploying new code." `
  "Feature flags (also called feature toggles or feature switches) are a technique that lets you control the visibility and behavior of features in a running system through configuration — without requiring a code deployment. This decouples code deployment from feature release." `
  "Feature flags are **on/off switches for features in running software**. You can deploy code but keep a feature hidden until you're ready, then flip the switch to release it — no redeployment needed." `
  "Feature flags decouple deployment from release. Code can be deployed to production at any time (even if not ready), hidden behind a flag. When ready, the flag is flipped. This enables trunk-based development, dark launches, A/B testing, canary releases, kill switches for faulty features, and gradual rollouts." `
  @"
**The core problem:**
Feature branches diverge from main for weeks/months. Merging is painful. Testing in isolation misses integration issues. You can't release partial features.

**The insight:**
> "Deploy everything, release by configuration."
> Code goes to production in every commit. The flag controls who sees it.

  if (featureFlags.isEnabled("new-checkout-flow", user)) {
      return newCheckoutService.process(cart);
  } else {
      return legacyCheckoutService.process(cart);
  }
"@ `
  "Without feature flags, every incomplete feature needs its own long-lived branch. Merging these branches late is risky. Feature flags allow continuous integration with all code on main — features are just hidden until ready." `
  "> Think of a light switch that someone installed but left off. The wiring (code) is in the wall (production), fully deployed. The switch (flag) controls whether the light (feature) is on. You can inspect, test, even rewire — without the light disturbing anyone." `
  @"
Types of feature flags:

  Release Toggle    → hide incomplete features (short-lived)
  Experiment Toggle → A/B testing
  Ops Toggle        → kill switch for production incidents (long-lived)
  Permission Toggle → enable for specific users/roles/plans
  Infrastructure    → behind-the-scenes tech swaps

Lifecycle:
  Deploy → (flag=off) → QA → (flag=on for internal) → (gradual rollout) → (flag=on for all) → remove flag
"@ `
  @"
[Code deployed to prod]
         ↓
  [Feature Flag Service]
   is_enabled("feature-x", user)?
         ↓ YES         ↓ NO
  [New Feature]  [Old Behavior]
"@ `
  @"
```java
// Simple feature flag check
@Service
public class CheckoutService {
    private final FeatureFlagService flags;
    private final NewCheckout newCheckout;
    private final LegacyCheckout legacyCheckout;

    public OrderResult processCart(Cart cart, User user) {
        if (flags.isEnabled("new-checkout-v2", user)) {
            return newCheckout.process(cart);        // new code path
        }
        return legacyCheckout.process(cart);         // safe fallback
    }
}

// Using LaunchDarkly / Unleash / Spring Boot
// application.yml:
features:
  new-checkout-v2:
    enabled: false        # default off
    rollout-percentage: 0 # 0% of users

// Ops toggle (kill switch pattern)
if (!flags.isEnabled("payment-service-v2")) {
    throw new ServiceUnavailableException("Payment temporarily unavailable");
}
```
"@ `
  @"
1. Wrap new feature in flag check
        ↓
2. Deploy to production (flag=OFF for all)
        ↓
3. Test in production with internal users (flag=ON for internal)
        ↓
4. Gradual rollout: flag=ON for 5% → 20% → 50% → 100%
        ↓
5. Monitor metrics/errors at each step
        ↓
6. Full rollout → REMOVE the flag (clean up technical debt)
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Feature flags = environment variables | Env vars are static; flags are dynamic, per-user, runtime |
| They add performance overhead | Properly implemented: negligible (in-memory map lookup) |
| You can keep them forever | Old flags = permanent technical debt; clean them up |
| Only for big companies | Any team doing CI/CD benefits from feature flags |
"@ `
  @"
**Pitfall 1: Flag Debt**
Accumulating old, dead flags nobody dares remove. Every flag = 2 code paths that must be tested.
Fix: set a TTL for each flag at creation; remove within 1 sprint of full rollout.

**Pitfall 2: Testing Matrix Explosion**
N flags = 2^N combinations. Only some combinations are valid.
Fix: limit simultaneous flags; document incompatible combinations.

**Pitfall 3: Flag in Wrong Layer**
Flags in domain/business logic instead of at the edge (controller/service boundary).
Fix: keep flags at the entry point; the feature itself should have no flag awareness.
"@ `
  @"
- **Canary Deployment** — gradual rollout at infrastructure level; flags do this at code level
- **A/B Testing** — experiment toggles used for measuring user behavior
- **Technical Debt** — every unused flag is debt; remove promptly
- **Trunk-Based Development** — short-lived branches; flags enable this at scale
- **Kill Switch** — ops toggle that disables a feature during incidents
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Decouple code deployment from feature release  │
│              │ using runtime configuration switches           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ CI/CD, gradual rollouts, A/B tests, kill      │
│              │ switches, dark launches                        │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Using them to replace proper versioning or    │
│              │ to avoid removing dead code                    │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Ship code continuously; release features      │
│              │  deliberately"                                 │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment → A/B Testing → CI/CD       │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** How do feature flags enable trunk-based development for large teams?
**Q2.** What is the difference between a release toggle and a kill switch?
**Q3.** How would you test a feature that's behind a flag — what testing strategy would you use?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 432 — Technical Debt
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "432" "Technical Debt" "🧹 432 — Technical Debt.md" `
  "#cleancode #architecture #intermediate" "★★☆" "Refactoring, Code Quality" "Refactoring, Code Smells, Architecture" `
  "The accumulated cost of shortcuts, workarounds, and deferred decisions in a codebase — debt that must eventually be repaid with interest." `
  "Technical debt is a metaphor (Ward Cunningham) for the implied cost of future rework caused by choosing an easy/fast solution now instead of a better approach that would take longer. Like financial debt, it accrues interest — the longer it's unaddressed, the harder it is to work around." `
  "Technical debt is the **price you pay later for moving fast today**. A quick fix that works now will cost you double the time to fix later — plus all the bugs and slowdowns along the way." `
  "Some technical debt is deliberate (a known shortcut to meet a deadline) and some is accidental (poor design discovered later). Both compound over time: working around bad code takes longer, understanding it takes longer, testing it takes longer. The interest rate compounds the longer you wait." `
  @"
**The core problem:**
Fast shortcuts now create slow, painful future work. A 2-hour hack today may consume 20 hours of debugging, rework, and onboarding pain over the next 6 months.

**Ward Cunningham's insight:**
> "Shipping first-time code is like going into debt. A little debt speeds development... but debt must eventually be repaid."

Types:
  Deliberate/Prudent:  "We know this is not ideal, we'll refactor after the launch"
  Deliberate/Reckless: "We don't have time for design"
  Inadvertent/Prudent: "Now we know how we should have done it"
  Inadvertent/Reckless: "What's layering?"
"@ `
  "Without technical debt awareness, teams perpetually 'move fast' while actually slowing down — each shortcut adds to a mountain of complexity that makes every future change harder, riskier, and slower." `
  "> Technical debt is like a credit card. A little debt is fine — it lets you move fast now. But if you never pay it off, the interest (slowdowns, bugs, onboarding pain) eventually exceeds the original borrowing. At maximum debt, every change becomes a risk." `
  @"
Technical Debt Quadrant (Martin Fowler):

              Deliberate         Inadvertent
  Reckless  | "No time for    | "What's           |
            |  design"        |  layering?"       |
  ----------|-----------------|-------------------|
  Prudent   | "Ship now,      | "Now we know      |
            |  refactor later"|  how to do it"    |

Ideal: minimize reckless debt; manage prudent debt consciously.
"@ `
  @"
[Quick Fix / Shortcut]
       ↓ creates
[Technical Debt] → [Interest: bugs, slow changes, high risk]
       ↓ if unpaid
[Degraded Velocity] → [Big Bang Rewrite temptation]
       ↓ pay down with
[Refactoring] → [Clean Code]
"@ `
  @"
```java
// TECHNICAL DEBT example: hardcoded magic values, no abstraction
// This was "quick" — now it's in 47 places across the codebase
if (user.getRole().equals("ADMIN") || user.getRole().equals("SUPER_ADMIN")) {
    // duplicated role check everywhere — change needed? Update 47 places.
}

// PAYING DOWN THE DEBT: refactor to a clean abstraction
enum Role { USER, ADMIN, SUPER_ADMIN }

interface Permission {
    boolean canManageUsers();
}

// Now change the rule once:
class AdminPermission implements Permission {
    public boolean canManageUsers() { return true; }
}

// Usage — clean, single source of truth
if (permissionService.hasPermission(user, Permission::canManageUsers)) { ... }
```
"@ `
  @"
1. Shortcut taken (either deliberate or accidental)
        ↓
2. Code ships — works for now
        ↓
3. Interest accrues: working around it, understanding it, testing it
        ↓
4. Feature velocity slows noticeably
        ↓
5. Team must invest in refactoring to pay down debt
        ↓
6. Refactoring restores velocity — cycle starts fresh
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| All technical debt is bad | Prudent/deliberate debt can be a conscious business decision |
| Rewrite = paying off debt | Rewrites rarely work; incremental refactoring does |
| Technical debt = bugs | Debt is structural; bugs are symptoms of it |
| More code coverage = less debt | Tests don't fix architectural debt |
"@ `
  @"
**Pitfall 1: Debt Blindness**
Teams don't track debt explicitly — it's invisible until velocity collapses.
Fix: maintain a debt register; include refactoring tasks in every sprint.

**Pitfall 2: Big Bang Rewrite**
"Let's just rewrite it clean" — almost always fails or takes 3x longer than expected.
Fix: Strangler Fig pattern — incrementally replace parts while the old system runs.

**Pitfall 3: 100% Coverage Illusion**
Adding tests to bad code makes it safer but doesn't reduce structural debt.
Fix: refactor the structure; tests enable safe refactoring.
"@ `
  @"
- **Refactoring** — the activity of paying down technical debt
- **Code Smells** — indicators of where technical debt lives
- **Boy Scout Rule** — "Always leave the code a little cleaner than you found it"
- **Strangler Fig Pattern** — safe way to incrementally replace legacy systems
- **Velocity** — the business metric that technical debt degrades over time
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Shortcuts now = compounding cost later        │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ All teams carry some — manage it consciously  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Never accumulate reckless/inadvertent debt    │
│              │ without a plan to address it                  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Move fast now, pay double later — track it,  │
│              │  name it, and plan to repay it"               │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Refactoring → Code Smells → Boy Scout Rule    │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** What is the difference between deliberate prudent debt and reckless inadvertent debt?
**Q2.** How do you identify technical debt in a codebase you've just joined?
**Q3.** Why is a "big bang rewrite" usually a worse solution than incremental refactoring?
"@

# ──────────────────────────────────────────────────────────────────────────────
# 433 — Refactoring
# ──────────────────────────────────────────────────────────────────────────────
Write-Entry `
  "433" "Refactoring" "🧹 433 — Refactoring.md" `
  "#cleancode #intermediate #pattern" "★★☆" "Technical Debt, Unit Test" "Technical Debt, Code Smells, Clean Code" `
  "Restructuring existing code without changing its external behavior — improving design while keeping all tests green." `
  "Refactoring (Martin Fowler) is the process of changing a software system in a way that does not alter the external behavior of the code yet improves its internal structure. It transforms working-but-messy code into cleaner design through a series of small, safe, behavior-preserving steps." `
  "Refactoring is **improving the inside of code without changing what it does**. You make it cleaner, simpler, and easier to understand — while every test keeps passing." `
  "Refactoring is not rewriting. Each refactoring step is tiny — extract a method, rename a variable, introduce an abstraction — and after each step the tests are green. The safety net of tests is what makes refactoring possible without fear." `
  @"
**The core problem:**
Code that worked fine 6 months ago is now painful to work with. Features take longer, bugs appear in unexpected places. The code needs to improve — but you can't stop and rewrite.

**Martin Fowler's insight:**
> "Refactoring is a series of small behavior-preserving transformations."

  Step 1: Extract Method → all tests pass
  Step 2: Rename Variable → all tests pass
  Step 3: Introduce Parameter Object → all tests pass
  (Never: change behavior mid-refactoring)
"@ `
  "Without refactoring, code can only degrade over time. The only way to improve a codebase safely — without risking new bugs — is through systematic refactor-as-you-go using tests as a safety net." `
  "> Refactoring is like reorganizing your kitchen. You don't stop cooking (producing features). You move things around step-by-step while making sure every meal you cook still comes out right. The kitchen works better after, but no recipes changed." `
  @"
Common refactoring techniques:

  Extract Method          → turn code block into a named method
  Inline Method           → remove a trivial method, inline its body
  Rename Variable/Method  → improve expressiveness
  Extract Class           → split a class doing too much
  Move Method             → method belongs in a different class
  Replace Temp with Query → replace variable with method call
  Introduce Parameter Obj → bundle related params into object
  Replace Conditional with Polymorphism → eliminate if/switch chains
"@ `
  @"
[Failing Tests / No Tests]
         ↓ cannot safely refactor
[Write Tests First]
         ↓ now safe
[Small Refactoring Step]
         ↓ run tests
[All Green] ← repeat until clean
         ↓
[Commit]
"@ `
  @"
```java
// BEFORE REFACTORING — hard to read, magic numbers, mixed concerns
double calculateFinalPrice(Order order) {
    double base = order.getItems().stream()
        .mapToDouble(i -> i.getPrice() * i.getQty()).sum();
    double disc = order.getCustomer().isPremium() ? base * 0.15 : 0;
    double tax  = (base - disc) * 0.08;
    return base - disc + tax;
}

// AFTER REFACTORING — named methods, clear flow, no magic numbers
private static final double TAX_RATE     = 0.08;
private static final double PREMIUM_DISC = 0.15;

double calculateFinalPrice(Order order) {
    double subtotal  = calculateSubtotal(order);
    double discount  = calculateDiscount(order, subtotal);
    double tax       = calculateTax(subtotal - discount);
    return subtotal - discount + tax;
}

private double calculateSubtotal(Order order) {
    return order.getItems().stream()
        .mapToDouble(i -> i.getPrice() * i.getQty()).sum();
}

private double calculateDiscount(Order order, double subtotal) {
    return order.getCustomer().isPremium() ? subtotal * PREMIUM_DISC : 0;
}

private double calculateTax(double taxableAmount) {
    return taxableAmount * TAX_RATE;
}
```
"@ `
  @"
1. Ensure test coverage exists (write tests if needed)
        ↓
2. Identify code smell (long method, magic number, duplication…)
        ↓
3. Apply one named refactoring technique
        ↓
4. Run tests — must stay green
        ↓
5. Commit
        ↓
6. Repeat for next smell
"@ `
  @"
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Refactoring = rewriting | Refactoring = small steps, behavior unchanged |
| Refactoring is a phase | It's continuous — the Boy Scout Rule |
| Tests slow down refactoring | Tests are what ENABLE safe refactoring |
| Refactoring adds features | By definition, refactoring changes NO behavior |
"@ `
  @"
**Pitfall 1: Refactoring without tests**
Changing structure without a safety net — you won't know if you broke something.
Fix: write characterization tests on legacy code before refactoring.

**Pitfall 2: Refactoring + feature at the same time**
Mixing structural and behavioral changes in one commit makes bugs impossible to pinpoint.
Fix: strict rule — refactoring commits and feature commits are always separate.

**Pitfall 3: Never shipping**
Infinite refactoring loop instead of delivering value.
Fix: timebox refactoring; follow the Boy Scout Rule (leave it a little better, not perfect).
"@ `
  @"
- **Technical Debt** — what refactoring pays down
- **Code Smells** — indicators that guide where to refactor
- **Unit Tests** — the safety net that makes refactoring possible
- **Boy Scout Rule** — "Leave the code better than you found it"
- **Strangler Fig** — large-scale refactoring / system replacement pattern
- **Extract Method** — the most common single refactoring technique
"@ `
  @"
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Improve internal structure without changing    │
│              │ external behavior — tests stay green always   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Continuously — especially before adding       │
│              │ new features to messy code                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ No tests exist yet — write them first         │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Small, safe, behavior-preserving steps that  │
│              │  accumulate into a cleaner design"            │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Code Smells → TDD → Boy Scout Rule            │
└─────────────────────────────────────────────────────────────┘
"@ `
  @"
**Q1.** Why must refactoring and feature development be in separate commits?
**Q2.** What is the difference between Extract Method and Extract Class refactoring?
**Q3.** How do characterization tests enable safe refactoring of legacy code with no tests?
"@

Write-Host ""
Write-Host "✅ All 10 Clean Code files generated in: $outDir"

