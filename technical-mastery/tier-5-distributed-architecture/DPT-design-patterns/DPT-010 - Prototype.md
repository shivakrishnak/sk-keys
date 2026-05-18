---
id: DPT-010
title: Prototype
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-007
used_by: DPT-032
related: DPT-007, DPT-008, DPT-009, DPT-011
tags:
  - pattern
  - creational
  - intermediate
  - java
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/design-patterns/prototype/
---

⚡ TL;DR - Prototype creates new objects by CLONING an existing
object (the prototype), instead of calling a constructor - used
when construction is expensive, when the exact class is unknown
at runtime, or when you need slightly-varied copies of a
complex configuration.

| #10 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-007 | |
| **Used by:** | DPT-032 | |
| **Related:** | DPT-007, DPT-008, DPT-009, DPT-011 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A game engine needs to spawn 1,000 enemy units. Each unit
starts with the same complex configuration: a loaded mesh,
a pre-parsed behavior tree, 50+ stat values, and a resolved
asset dependency graph. The constructor for each unit
re-runs all initialization: loads the mesh from disk,
parses the behavior tree XML, computes the stat baseline -
100ms per unit, 100 seconds total for 1,000 units.

**THE BREAKING POINT:**
The bottleneck is not the unit's logic - it is construction:
the expensive initialization is repeated for every unit
even though every unit starts identically. The constructor
is doing work that only needs to be done ONCE for the
initial prototype.

**THE INVENTION MOMENT:**
Prototype: do the expensive initialization ONCE, on a master
instance (the prototype). Spawn new units by CLONING the
prototype - a shallow or deep memory copy is orders of
magnitude faster than re-running initialization. Construction
cost is amortized across all clones.

**EVOLUTION:**
Prototype predates OOP patterns - binary memory copying
for fast object creation is a hardware optimization from
the 1970s. In Java, `Object.clone()` (protected, native)
is the built-in mechanism but carries significant design
problems (see Failure Modes). Modern Java favors copy
constructors or factory methods that accept a source
instance. JavaScript's prototype chain IS the Prototype
pattern at the language level - every object has a prototype
reference and inherits through it.

---

### 📘 Textbook Definition

The **Prototype** pattern is a Creational design pattern
that specifies the kinds of objects to create using a
prototypical instance, and creates new objects by copying
(cloning) this prototype. The pattern avoids the cost of
creating objects from scratch when an equivalent object
already exists and can be copied. The pattern requires the
copyable objects to implement a cloning interface, and clients
create new instances by asking the prototype to clone itself.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Prototype creates new objects by copying an existing one
instead of running the constructor again.

**One analogy:**
> A cookie cutter (the prototype) defines the shape once.
> Every new cookie is pressed from the cutter - same shape,
> no redesign. Varying the toppings after pressing is how
> you get different flavors from the same mold.

**One insight:**
Prototype's key advantage is cost: cloning can be 100-1000x
faster than construction when the constructor loads external
resources. The key danger is correctness: cloning is
structurally identical to the original, which means shared
mutable references between prototype and clone can produce
subtle bugs that only appear when one clone mutates state
it shares with another.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The prototype is a fully constructed, valid object - the
   clone inherits a valid state.
2. Each clone must be INDEPENDENT: mutating a clone must not
   affect the prototype or other clones.
3. Independence requires a DEEP COPY for any mutable nested
   objects; shallow copy is only safe when nested objects
   are immutable.

**DERIVED DESIGN:**
Two participants:
- **Prototype**: interface declaring a `clone()` method
- **ConcretePrototype**: implements `clone()`, performs deep
  copy of mutable state

Optional: **PrototypeRegistry** - a map from name/type to
prototype instances; clients look up a prototype by key
and clone it, without knowing the concrete type.

**SHALLOW COPY vs DEEP COPY:**
- Shallow copy: copies primitive fields and references.
  Prototype and clone share references to the same nested
  objects. Fast. Only safe if nested objects are immutable.
- Deep copy: recursively copies all nested mutable objects.
  Clone is fully independent. Slower. Correct when nested
  objects are mutable.

**TRADE-OFFS:**

**Gain:** Avoids expensive constructor work for objects
derived from the same initial state. Enables polymorphic
copying: `prototype.clone()` creates the right concrete
type without knowing it.

**Cost:** Every class must implement `clone()` correctly.
Deep copy is complex. Circular references in the object
graph cause infinite recursion in naive deep copy.

---

### 🧪 Thought Experiment

**SETUP:**
A configuration system maintains a base `AppConfig` object
with 200 loaded settings, resolved environment variables,
and parsed YAML. Different request handlers need slightly
different views of the config (one handler needs
`debug=true`, another needs `timeout=5s`, all others
use defaults). Construction cost: 200ms per config
(file I/O, parsing).

**WHAT HAPPENS WITHOUT PROTOTYPE:**
Each request handler constructs its own `AppConfig` from
scratch. 10 handlers = 2 seconds of construction at startup.
When configuration is refreshed, all 10 reconstruct.

**WHAT HAPPENS WITH PROTOTYPE:**
One base `AppConfig` is constructed (200ms). Each handler
clones the base and overrides its 1-2 specific fields.
Cloning: <1ms. 10 handlers = <10ms total. Configuration
refresh: reconstruct base once, re-clone for each handler.

**THE INSIGHT:**
Prototype is the right tool when most of an object's
state is shared and only a small portion varies between
instances. The pattern separates "shared expensive state"
(in the prototype) from "per-instance variation" (applied
after cloning).

---

### 🧠 Mental Model / Analogy

> Prototype is a MASTER DOCUMENT pattern. A company creates
> one master employment contract (the prototype): all 20
> pages, standard clauses, correct formatting. Each new
> hire gets a photocopy (clone) of the master with only
> their name, start date, and salary filled in (mutation
> after clone). Creating each contract from scratch would
> require a lawyer every time.

- "Master contract" = the prototype
- "Photocopy" = the clone() call
- "Fill in employee details" = mutations after clone
- "20 pages standard content" = shared state (cheap to copy)
- "Employee-specific fields" = per-instance variation

**Where this analogy breaks down:**
A photocopy and the master are independent paper documents -
there is no shared-reference problem. In code, a shallow
clone and the prototype SHARE references to mutable objects.
The photocopy analogy gives the intent but not the deep-copy
requirement.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Prototype means "make a copy." Instead of building an object
from scratch, you start with a pre-built object and copy it,
then adjust what's different. Faster and simpler when the
starting state is expensive to compute.

**Level 2 - How to use it (junior developer):**
Implement a `Cloneable` interface (or your own `clone()`
method). In `clone()`, copy all fields. For mutable nested
objects, create new copies of those too (deep copy). Use
the prototype by calling `prototype.clone()`, then set
any per-instance fields.

**Level 3 - How it works (mid-level engineer):**
Java's `Object.clone()` is a shallow copy by default: it
copies field values, which means references are shared.
If the object contains a `List<String> tags`, both prototype
and clone share the SAME List object. Mutating the clone's
tags list mutates the prototype's list too - a bug.
Deep copy requires creating new collections and copying
their contents recursively. Always verify: for each mutable
field in the class, does the clone() implementation create
a new independent copy?

**Level 4 - Why it was designed this way (senior/staff):**
GoF Prototype was designed for environments where object
classes are loaded dynamically and the exact class may not
be known at compile time. `prototype.clone()` creates the
correct concrete type (polymorphic creation) without naming
the class. This use case - dynamic type cloning - is the
GoF motivation. The "expensive construction" optimization
is a derived benefit. Java's `Object.clone()` implementation
is problematic: it breaks encapsulation (clone() is called
on the object, not a factory), requires `implements Cloneable`
as a marker interface with no method signature, and produces
shallow copies by default with no warning. Bloch (Effective
Java, Item 13) advises: prefer a copy constructor or copy
factory over `Object.clone()`.

**Level 5 - Mastery (distinguished engineer):**
Prototype in distributed systems appears as "template
configuration" patterns: a Kubernetes Pod template is a
Prototype - the template is defined once; each Pod creation
clones the template and applies per-pod overrides (node
selector, environment variables). Spring's prototype bean
scope (`@Scope("prototype")`) is Factory Method returning
a clone-equivalent: each `getBean()` creates a new instance
that starts from the same initial state as configured in
the context. Deep copy for complex object graphs in Java is
best implemented with serialization-based copy (serialize
to bytes, deserialize a new instance) or using a library
like Kryo. Cloning via copy constructor is preferred for
classes you own.

---

### ⚙️ How It Works (Mechanism)

```
Prototype Mechanism
┌───────────────────────────────────────────────────────┐
│  <<interface>> Prototype                              │
│  + clone(): Prototype                                 │
│         ▲                                             │
│  ConcretePrototype                                    │
│  - primitive: int      ← copied by value (safe)      │
│  - immutable: String   ← ref copy safe (immutable)   │
│  - mutableList: List   ← MUST be deep copied         │
│  + clone(): Prototype                                 │
│    result = new ConcretePrototype()                   │
│    result.primitive   = this.primitive   (ok)         │
│    result.immutable   = this.immutable   (ok)         │
│    result.mutableList = new ArrayList<>(this.list) ✓ │
│    return result                                      │
│                                                       │
│  PrototypeRegistry (optional)                         │
│  - registry: Map<String, Prototype>                   │
│  + register(key, proto)                               │
│  + create(key): Prototype                             │
│    return registry.get(key).clone()                   │
└───────────────────────────────────────────────────────┘
```

**Shallow vs Deep copy visualization:**
```
SHALLOW COPY (dangerous with mutable refs)
┌────────────┐        ┌────────────┐
│ prototype  │        │  clone     │
│ tags ──────┼──────→ │ tags ──────┼──→ [same List object!]
└────────────┘        └────────────┘

DEEP COPY (correct with mutable refs)
┌────────────┐        ┌────────────┐
│ prototype  │        │  clone     │
│ tags ──────┼──→[L1] │ tags ──────┼──→ [L2 - new copy]
└────────────┘        └────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
System starts: constructs prototype once (expensive)
  → Each new instance: calls prototype.clone() (cheap)
  → clone() performs deep copy of all mutable fields
  → Returns new independent object with same initial state
  → Caller modifies clone for per-instance differences
  → Original prototype unchanged
```

**FAILURE PATH:**
```
Shallow copy clone() called:
  → Clone and prototype share mutableList reference
  → Caller modifies clone.mutableList.add("x")
  → prototype.mutableList now also contains "x"
  → All subsequent clones inherit the mutation
  → Silent data corruption - no exception thrown
```

**WHAT CHANGES AT SCALE:**
Prototype is designed for scale. 1 construction + N clones
amortizes construction cost across all N instances. At very
large N (millions), verify that deep copy is not
re-creating large object graphs - consider lazy copy
(copy-on-write semantics) where nested objects are shared
until a mutation occurs.

---

### 💻 Code Example

**Example 1 - The wrong way: Java Object.clone() shallow copy:**

```java
// BAD: Object.clone() gives shallow copy - mutable state shared
class EnemyConfig implements Cloneable {
    private int hp;
    private List<String> abilities; // mutable!

    @Override
    public EnemyConfig clone() {
        try {
            return (EnemyConfig) super.clone(); // shallow!
            // abilities list is SHARED with original
        } catch (CloneNotSupportedException e) {
            throw new AssertionError(); // never happens
        }
    }
}

EnemyConfig proto = new EnemyConfig(100, List.of("fly", "bite"));
EnemyConfig clone = proto.clone();
clone.abilities.add("poison"); // BUG: also mutates proto.abilities
```

**Example 2 - Correct: copy constructor (Bloch's recommendation):**

```java
// GOOD: copy constructor is clearer and safer than Object.clone()
class EnemyConfig {
    private final int hp;
    private final List<String> abilities;

    // Normal constructor
    public EnemyConfig(int hp, List<String> abilities) {
        this.hp = hp;
        // Defensive copy of mutable input
        this.abilities = List.copyOf(abilities);
    }

    // Copy constructor - the "Prototype" creation method
    public EnemyConfig(EnemyConfig source) {
        this.hp = source.hp;
        // Deep copy: new list with same contents
        this.abilities = List.copyOf(source.abilities);
    }
}

// Usage: Prototype pattern via copy constructor
EnemyConfig prototype = new EnemyConfig(100, List.of("fly"));
EnemyConfig boss      = new EnemyConfig(prototype); // clone
EnemyConfig minion    = new EnemyConfig(prototype); // clone
// boss and minion are independent - prototype unchanged
```

**Example 3 - Prototype Registry:**

```java
// GOOD: Registry maps names to prototypes for polymorphic creation
class EnemyRegistry {
    private final Map<String, EnemyConfig> registry =
        new HashMap<>();

    public void register(String name, EnemyConfig proto) {
        registry.put(name, proto);
    }

    // Returns a clone - caller does not know EnemyConfig subtype
    public EnemyConfig createEnemy(String name) {
        EnemyConfig proto = registry.get(name);
        if (proto == null)
            throw new IllegalArgumentException(
                "Unknown enemy type: " + name);
        return new EnemyConfig(proto); // copy constructor
    }
}

// Setup at startup (expensive construction once):
EnemyRegistry reg = new EnemyRegistry();
reg.register("boss",   new EnemyConfig(500, loadBossBehaviors()));
reg.register("minion", new EnemyConfig(50, loadMinionBehaviors()));

// Runtime: cheap cloning from registry
EnemyConfig e1 = reg.createEnemy("minion"); // <1ms (clone)
EnemyConfig e2 = reg.createEnemy("minion"); // <1ms (clone)
// loadMinionBehaviors() was called ONCE total
```

**Example 4 - Spring Prototype scope (framework Prototype):**

```java
// Spring prototype scope: each getBean() call is a Prototype clone
@Component
@Scope("prototype") // Not singleton - each request = new instance
public class ReportGenerator {
    private ReportConfig config;
    // Spring creates a fresh instance for each injection point
}

// In contrast, @Scope("singleton") = shared instance (not Prototype)
```

**How to test/verify correctness:**
Test independence: clone from prototype, mutate a mutable
field in the clone, verify the prototype's field is unchanged.
This is the critical test for any Prototype implementation.

---

### ⚖️ Comparison Table

| Approach              | Creation Cost | Independence | Complexity | Best For                         |
| --------------------- | ------------- | ------------ | ---------- | -------------------------------- |
| **Prototype (clone)** | Very low      | Must verify  | Medium     | Expensive init, many similar objs|
| Regular constructor   | Normal        | Yes          | None       | Cheap construction               |
| Object Pool           | None (reuse)  | Must reset   | High       | Very expensive objects, fixed N  |
| Factory Method        | Normal        | Yes          | Medium     | Type polymorphism, not cost      |
| Serialization copy    | Low           | Yes          | Medium     | Complex object graphs, deep copy |

**How to choose:** Use Prototype when construction is
measurably expensive AND you need many instances with the
same initial state. Use Object Pool when you need to REUSE
the same objects (Prototype creates new copies; Object Pool
reuses existing ones). Use serialization-based copy when
the object graph is complex and manual deep copy is error-prone.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java's `implements Cloneable` ensures correct cloning | `Cloneable` is a marker interface with no method signature; Object.clone() without proper deep copy override produces a dangerous shallow copy |
| Prototype is the same as Object Pool | Prototype creates NEW independent copies; Object Pool REUSES the same objects, returning them to the pool when done |
| Prototype requires a formal `clone()` interface | A copy constructor or factory method `EnemyConfig(EnemyConfig source)` is a Prototype implementation without the Java Cloneable baggage |
| Deep copy is always required | If all mutable nested objects are themselves immutable (e.g., using `List.of()`), a shallow copy IS a deep copy - there is nothing that can be mutated through a shared reference |
| Prototype is only for performance optimization | The GoF motivation was polymorphic creation - cloning a prototype when the concrete type is not known. Performance is a secondary benefit |

---

### 🚨 Failure Modes & Diagnosis

**Shallow Clone Corrupting Prototype State**

**Symptom:**
After spawning 100 enemies from a prototype, some enemies
have abilities that were not in the original prototype
configuration. Debugging shows the prototype's ability list
has grown over time. The first enemy spawned has no extra
abilities; the 50th does.

**Root Cause:**
`clone()` performs a shallow copy. All clones share the SAME
`List<String> abilities` object reference as the prototype.
When any clone calls `abilities.add("poison")`, it mutates
the shared list, which all other clones and the prototype
read as their own.

**Diagnostic Signal:**
```java
EnemyConfig proto = new EnemyConfig(100, new ArrayList<>());
EnemyConfig clone = proto.clone();
System.out.println(proto.abilities == clone.abilities);
// BAD output: true  (same object - shallow copy)
// GOOD output: false (different objects - deep copy)
```

**Fix:**
```java
// BAD: shallow copy
public EnemyConfig clone() {
    return (EnemyConfig) super.clone(); // abilities shared
}

// GOOD: deep copy mutable fields
public EnemyConfig clone() {
    try {
        EnemyConfig copy = (EnemyConfig) super.clone();
        // Create a new independent list with same contents
        copy.abilities = new ArrayList<>(this.abilities);
        return copy;
    } catch (CloneNotSupportedException e) {
        throw new AssertionError();
    }
}
```

**Prevention:**
Rule: for every mutable field in a class that implements
clone(), write an explicit assertion test:
`assert proto.mutableField != clone.mutableField`
Run this test as part of the clone() unit test.

---

**Prototype Mutation - Shared Prototype Modified After Cloning**

**Symptom:**
A prototype registry is populated at startup. After the
application runs for a while, newly cloned enemies have
different stats than enemies cloned during startup. The
prototype itself has been mutated.

**Root Cause:**
A method returns the prototype object (not a clone) and
the caller mutates it, believing it received a personal
copy. Or the prototype has setters that are called
accidentally after registration.

**Diagnostic Signal:**
Log `System.identityHashCode(proto)` when registering and
when cloning. If the hash of the object returned by
`createEnemy()` matches the registered prototype's hash:
the registry is returning the prototype directly, not a clone.

**Fix:**
- Make the prototype immutable after registration (remove
  setters, use final fields or a defensive copy constructor)
- Verify the registry's `createEnemy()` returns a clone,
  never the prototype reference

**Prevention:**
Store prototypes as immutable value objects where possible.
After registering a prototype, mark it as "sealed" in a
comment or by wrapping in an unmodifiable view.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Factory Method` - simpler creation pattern; understand
  single-step creation vs Prototype's copy-based creation
- `Builder` - another Creational pattern; Builder creates
  via step-by-step assembly; Prototype creates via copying

**Builds On This (learn these next):**
- `Object Pool` - related Creational pattern; Pool reuses
  the same objects; Prototype creates new independent copies;
  both optimize creation cost
- `Flyweight` - shares immutable state across many instances;
  where Prototype copies all state, Flyweight shares all
  state - the opposite approach

**Alternatives / Comparisons:**
- `Builder` - constructs from scratch with validation;
  prefer Builder when objects have varied initial states
  and construction is not expensive
- `Object Pool` - reuses instances; prefer Pool when
  objects are expensive to both create AND discard

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Create new objects by copying (cloning)  │
│              │ a prototype instead of using constructor │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Expensive construction when many similar │
│ SOLVES       │ instances are needed                     │
├──────────────┼──────────────────────────────────────────┤
│ KEY DANGER   │ Shallow copy shares mutable state:       │
│              │ mutating clone mutates prototype         │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Construction is expensive; many instances│
│              │ start from the same initial state        │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Construction is cheap; each instance     │
│              │ needs significantly different initial sta│
├──────────────┼──────────────────────────────────────────┤
│ JAVA CAVEAT  │ Prefer copy constructor over             │
│              │ Object.clone() - safer, clearer          │
├──────────────┼──────────────────────────────────────────┤
│ TEST IT      │ mutate clone, verify prototype unchanged │
├──────────────┼──────────────────────────────────────────┤
│ IN FRAMEWORK │ Spring @Scope("prototype") = new         │
│              │ instance per injection point             │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Object Pool → Flyweight → Factory Method │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Shallow copy is the default and is WRONG for any mutable
   nested object; deep copy mutable fields explicitly in
   the clone() / copy constructor implementation
2. Test independence: `mutate clone → assert prototype unchanged`
   is the only correct test for any Prototype implementation
3. Prefer copy constructor over `Object.clone()` in Java;
   `Cloneable` and `super.clone()` have design problems that
   Bloch documents in Effective Java Item 13

**Interview one-liner:**
"Prototype creates objects by cloning a pre-built instance
instead of running the constructor again - key use cases are
expensive construction and polymorphic copy when the concrete
type is unknown. The critical implementation requirement is
deep copy of mutable fields: shallow copy corrupts the
prototype. Java's Object.clone() is problematic; prefer copy
constructors."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When the cost of initialization dominates object creation,
separate "initialize once" from "configure per instance."
Prototype is the Creational expression of this principle:
do expensive work once (build the prototype), amortize it
across many lightweight copies.

**Where else this pattern appears:**
- **Kubernetes Pod templates** - a PodTemplate defines the
  prototype; each Pod created from the template is a clone
  with overrides (node affinity, env vars); the template
  is the prototype; `kubectl apply` with a template IS
  prototype-pattern object creation at the infrastructure level
- **Document templates** - Office / Google Docs templates
  are prototypes; a new document created from a template
  is a clone; editing the new document does not change
  the template
- **Virtual Machine snapshots** - a golden image VM snapshot
  is a prototype; spinning up 50 VMs from the snapshot is
  cloning; the snapshot's state (OS, packages, config) is
  shared starting state; per-VM customization is applied
  after clone

**Industry applications:**
- **Spring prototype beans** - each `getBean()` or injection
  creates a new bean instance; the bean definition IS the
  prototype; Spring's BeanFactory.createBean() is the clone()
  equivalent
- **JavaScript prototype chain** - JS objects have a
  `[[Prototype]]` internal link; property lookup traverses
  this chain; `Object.create(proto)` creates a new object
  using `proto` as its prototype - Prototype pattern at the
  language level

---

### 💡 The Surprising Truth

Java's `Object.clone()` method was designed by the Java
language team and is documented by Joshua Bloch (who was
on that team) as "a deeply broken facility" in Effective Java.
The problems: `Cloneable` is a marker interface with no
`clone()` method - implementing `Cloneable` does not actually
declare anything meaningful. `super.clone()` works via
native memory copying that bypasses constructors entirely.
If any class in the inheritance hierarchy fails to override
`clone()` correctly, the mechanism silently returns a broken
shallow copy. Bloch's conclusion: "Given all the problems
associated with Cloneable, new interfaces should not extend
it, and new extendable classes should not implement it."
The pattern intent (copying a prototype) is correct and
valuable - Java's mechanism for achieving it is flawed.
Use copy constructors instead.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Distinguish shallow copy from deep copy with a
   concrete Java example showing the exact line where shallow
   copy goes wrong, and the exact fix
2. [DEBUG] Given a bug report "enemies are gaining abilities
   they shouldn't have," identify the shallow-clone root cause,
   write the diagnostic test, and implement the deep-copy fix
3. [COMPARE] Choose between Prototype and Object Pool for
   a given scenario, stating the deciding criterion: when
   to create new copies (Prototype) vs reuse existing ones (Pool)
4. [BUILD] Implement a `ConfigPrototype` copy constructor
   in Java that correctly deep-copies a `Map<String, List<String>>`
   field without corrupting the source
5. [RECALL] Explain Bloch's argument against `Object.clone()`
   and why copy constructors are preferred - give one concrete
   implementation flaw of `Object.clone()` that copy constructors
   avoid

---

### 🧠 Think About This Before We Continue

**Q1.** JavaScript's `Object.create(proto)` implements
Prototype at the language level, but differently from GoF:
it does NOT copy the prototype's state - it creates a
prototype CHAIN, where the new object DELEGATES to the
prototype for missing properties. How is this different from
GoF Prototype? Which is "cloning" and which is "delegation"?
When does the distinction matter in practice?

*Hint: GoF Prototype = COPY state (new object is independent
after copy). JS Object.create = DELEGATE (new object shares
state through the chain; reading a property on the new object
returns the prototype's value until overridden). Consequence:
in GoF, mutating the clone does not change the prototype.
In JS object.create, reading a non-overridden property reads
the prototype's current value - if the prototype changes,
the "child" sees the new value. These are opposite behaviors.*

**Q2.** A game engine's EnemyPrototype contains a reference
to a `BehaviorTree` object that is both expensive to construct
AND effectively immutable once built (it is never modified
after construction). The prototype also contains a `Stats`
object that IS mutated (HP changes during combat). Design
a clone() strategy that shares the BehaviorTree (safe, it's
immutable) but deep-copies the Stats (required for independence).

*Hint: This is called "copy-on-write" or "selective deep copy."
In clone(): copy the BehaviorTree reference (shallow, safe
because immutable). Create new Stats(this.stats) (deep, because
Stats are mutable). This is more efficient than deep-copying
everything and more correct than shallow-copying everything.
The deciding criterion: is the nested object mutable? If yes:
deep copy. If no: share the reference safely.*

**Q3.** You need to implement a prototype registry for a
system with 200 entity types. Some prototypes are expensive
to build (100ms+), some are cheap (<1ms). Design a registry
that: (1) builds expensive prototypes lazily (only when first
requested), (2) ensures thread-safe initialization (no two
threads build the same prototype simultaneously), (3) serves
clones for all requests after the first.

*Hint: This is a combination of Prototype + Lazy Initialization
+ Thread-safe Singleton initialization. The tools:
ConcurrentHashMap.computeIfAbsent() with a supplier lambda
for the prototype construction - computeIfAbsent() is atomic
for a given key, so the expensive supplier runs only once
per key. The returned value is the prototype; clone it
before returning to the caller.*

---

### 🎯 Interview Deep-Dive

**Q1: When would you use Prototype instead of simply
calling the constructor? What makes cloning faster?**

*Why they ask:* Tests understanding of the performance
motivation and when the pattern is applicable vs over-engineering.

*Strong answer includes:*
- Use Prototype when: (a) the constructor performs expensive
  work (I/O, parsing, network calls, heavy computation)
  AND you need many instances starting from the same state,
  OR (b) the concrete type is unknown at compile time
  (polymorphic copy)
- Cloning is faster because: a native memory copy of the
  object's fields (what super.clone() does internally) is
  O(field count), while the constructor may be O(external
  resource cost) - file I/O is orders of magnitude slower
  than memory copy
- When NOT to use: simple objects with no expensive
  initialization; when each instance needs a significantly
  different starting state

**Q2: Why does Bloch recommend copy constructors over
Object.clone()? What specific flaw does Object.clone() have?**

*Why they ask:* Tests Effective Java knowledge and deep
Java understanding.

*Strong answer includes:*
- `Cloneable` has no `clone()` method: the interface is
  a marker that enables `Object.clone()`'s behavior change
  (it throws CloneNotSupportedException if not implemented)
  but provides no type-safe guarantee in the interface
- `super.clone()` bypasses constructors entirely: side effects
  in constructors are not run for clones; validation logic
  in constructors is skipped
- Shallow copy by default with no warning: silently shares
  mutable references unless overridden
- Copy constructor advantages: works with final fields,
  runs constructor validation, visible in the type signature,
  does not require implementing a marker interface

**Q3: How does Spring's @Scope("prototype") relate to the
Prototype design pattern? What exactly does Spring do
when a prototype-scoped bean is requested?**

*Why they ask:* Tests ability to connect patterns to
framework behavior.

*Strong answer includes:*
- Spring prototype scope: each call to `applicationContext
  .getBean(MyBean.class)` or each injection point for a
  prototype-scoped bean creates a NEW bean instance
- Spring's BeanFactory.createBean() constructs a fresh
  instance from the bean definition (constructor args,
  dependencies) - NOT by cloning a prototype object
- This is "Prototype in spirit" (new independent instance
  each time) but NOT Prototype by implementation (Spring
  uses construction, not clone())
- Contrast: Spring prototype scope = creation; GoF Prototype
  = cloning; same goal (independent instances) different mechanism
- Key difference matters: Spring prototype re-injects
  dependencies fresh; GoF clone copies them from the prototype

