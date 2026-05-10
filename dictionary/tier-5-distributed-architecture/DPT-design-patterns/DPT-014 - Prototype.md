---
layout: default
title: "Prototype"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /design-patterns/prototype/
id: DPT-018
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
  - performance
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-016 - Prototype

⚡ TL;DR - Prototype creates new objects by cloning an existing instance, avoiding expensive re-initialisation when object construction is costly.

| DPT-016 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Cloning, Deep Copy vs Shallow Copy | |
| **Used by:** | Object Caching, Game Entity Systems, Document Templates | |
| **Related:** | Factory Method, Builder, Singleton, Object Pool | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A game engine has 5,000 "enemy" entities on screen. Each enemy is created via `new Enemy()`, which loads a 3D model from disk, parses JSON configuration, allocates a physics body, and initialises a pathfinding graph - 120 milliseconds per enemy. Creating 5,000 enemies at level load takes 10 minutes. The game's level designer wants to spawn 100 additional enemies mid-game when a trigger fires - 12 more seconds of freezing.

**THE BREAKING POINT:**
Most of that 120 ms is redundant. Every enemy of the same "type" has identical model data, identical configuration, identical initial physics parameters. Only a handful of values (position, unique ID, health variation) differ instance to instance. The `new Enemy()` constructor re-reads the same file from disk and re-parses the same JSON every time - paying the full construction cost for data that could be shared from the first enemy created.

**THE INVENTION MOMENT:**
This is exactly why the Prototype pattern was created. Create one "prototype" enemy by doing the full 120 ms initialisation once. Clone the prototype for each new enemy - copying its state in-memory, which takes microseconds. Only patch the per-instance values (position, ID) after cloning. 5,000 enemies: 120 ms once + 4,999 × 0.1 ms = 620 ms total. Level loads in under a second.

**EVOLUTION:**
Prototype was critical in languages without stack allocation and
in environments where object construction was expensive. Modern
JVM JIT compilation and object pooling reduced the performance
motivation significantly. Today Prototype survives in JavaScript
(prototype-chain inheritance), serialization-based cloning, and
copy-with semantics in immutable object libraries. Lombok's
`@Builder(toBuilder=true)` and Kotlin's `data class copy()`
provide the same "clone-with-modifications" pattern without
manual `clone()` implementation.

---

### 📘 Textbook Definition

The **Prototype** pattern is a creational design pattern that specifies the kinds of objects to create using a prototypical instance and creates new objects by copying this prototype. Implementors declare a `clone()` method (or equivalent) that returns a copy of the object. The pattern avoids the overhead of class-specific creation logic by delegating duplication to the object being copied. It decouples the client from the concrete class of the object being created and supports runtime registration of new prototype types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Copy an already-built object instead of building a new one from scratch.

**One analogy:**
> A photocopier. Instead of handwriting a new letter every time, you write it once perfectly and photocopy it for each recipient. Each copy starts identical; you then personalise each with the recipient's name.

**One insight:**
The Prototype pattern inverts the normal creation assumption. Normally: "I need a new object, so I construct it." Prototype: "I already have a fully valid object - the cheapest way to get another is to duplicate it." This is correct when construction is expensive and duplication is cheap.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Object construction is expensive (I/O, complex computation, resource allocation).
2. Many objects share the same initial state - only a small set of fields varies per instance.
3. The class and its construction details should be hidden from the client creating copies.

**DERIVED DESIGN:**
Given invariant 1+2: pay the construction cost once, then clone in-memory. Given invariant 3: the clone operation is declared through an interface (`Cloneable` in Java, or a custom `copy()` method), hiding the concrete class from callers.

Two critical decisions arise at design time:
- **Shallow clone**: copy field values directly. Reference fields point to the same objects as the original. Fast, but mutations in the clone affect the original (shared state bug).
- **Deep clone**: recursively copy all referenced objects. More expensive, but fully independent. Correct when cloned instances must not share mutable state.

For immutable fields (String, int, final objects), shallow clone is safe. For mutable connected objects (lists, maps, object graphs), deep clone is required.

**THE TRADE-OFFS:**
**Gain:** Avoids expensive recreation; supports runtime prototype registration (new object types added without changing client code); reduces subclassing by parameterising object state at clone time.
**Cost:** Deep clone is complex to implement correctly (transitive object graphs, cycles); Java's `Object.clone()` is shallow by default and poorly designed (`CloneNotSupportedException`, protected visibility); serialisation-based deep clone is safe but slow; breaks encapsulation (cloning requires reading all state including private fields).

---

### 🧪 Thought Experiment

**SETUP:**
A document editor supports complex page templates: each template has pre-loaded fonts, pre-rendered graphic assets, pre-computed style tables, and a default content structure. Loading a template takes 800 ms. Users frequently create new documents from the same template.

**WHAT HAPPENS WITHOUT PROTOTYPE:**
Each "New Document from Template" re-runs the 800 ms initialisation. User creates 10 documents from the same template: 8 seconds of waiting plus 10x disk reads for the same font files. The application feels sluggish; users complain.

**WHAT HAPPENS WITH PROTOTYPE:**
Template is loaded once (800 ms) and stored as a registry entry. "New Document from Template" clones the stored prototype (deep copy, 5 ms). 10 documents: 800 ms + 10 × 5 ms = 850 ms total. First document loads as before; subsequent ones are nearly instant. Template library holds 20 prototypes; all are pre-loaded at startup.

**THE INSIGHT:**
Prototype shifts the cost model from pay-per-use to pay-once-reuse-many. The pattern is most powerful when the object graph is large but most of it is read-only after construction - meaning shallow clone is sufficient for the expensive shared parts.

---

### 🧠 Mental Model / Analogy

> Prototype is like a Xerox machine for objects. You build the master copy perfectly. Every subsequent request gets a fresh Xerox - identical to the master, independent enough to be personalised (write on it, add sticky notes). You never hand out the master itself; always a copy.

- "Master document" → the prototype instance
- "Xerox copy" → the cloned object
- "Writing on the copy" → setting per-instance fields post-clone
- "Not handing out the master" → clients receive clones, never the prototype itself
- "Changing the master" → modifying the prototype changes future clones (beware: intended or bug?)

Where this analogy breaks down: a real Xerox shares ink physically - in software, shared mutable state between clone and original is a bug. Deep clone is the mechanism that ensures copies are truly independent.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Prototype is "copy-then-modify." Instead of starting from scratch, you take something that already exists and fully works, copy it, and only change the few things that differ. It is faster because most of the work (loading, initialising, configuring) was already done in the original.

**Level 2 - How to use it (junior developer):**
In Java, implement `Cloneable` and override `clone()`: `return (EnemyEntity) super.clone();`. Register "template" prototypes in a `PrototypeRegistry` (a `Map<String, EnemyEntity>`). When a new enemy is needed: `EnemyEntity e = registry.get("troll").clone(); e.setPosition(x, y);`. In modern Java, prefer a manual copy constructor or `copy()` factory method over `Object.clone()` - Java's built-in clone is buggy and hard to use correctly.

**Level 3 - How it works (mid-level engineer):**
Java's `Object.clone()` performs a bit-for-bit shallow copy. For primitive fields this is correct. For reference fields, both the original and the clone point to the same heap object - mutating that object from the clone affects the original. Deep clone requires manually copying every mutable reference field recursively. Serialisation-based deep clone (write to `ByteArrayOutputStream`, deserialise back) gives a correct deep copy for any serialisable object graph, including cyclic references, at the cost of serialisation overhead. Libraries like Apache Commons' `SerializationUtils.clone()` encapsulate this. For performance-critical use, write a manual deep clone that copies only the mutable parts.

**Level 4 - Why it was designed this way (senior/staff):**
Prototype was coined in the context of graphical object systems in the late 1980s (particularly Self and early GUI toolkits). The insight was that class hierarchies were not the only way to create variation - you could prototype objects at runtime by cloning and patching, enabling more flexible object creation without defining new classes for every variant. In modern systems, the pattern appears in: game engines (entity templates), document editors, configuration templates, and test fixture factories. Java's `Object.clone()` design is widely considered a mistake (Joshua Bloch, Effective Java, Item 13: "Clone judiciously") because it uses the Cloneable marker interface rather than declaring clone() in the interface. The recommended modern approach is a copy constructor or static factory: `new Enemy(existingEnemy)`.

---

### ⚙️ How It Works (Mechanism)

**Shallow vs Deep Clone:**
```
┌─────────────────────────────────────────────────┐
│  SHALLOW CLONE                                  │
│                                                 │
│  Original:  [ health=100, model=→ModelObj ]     │
│  Clone:     [ health=100, model=→ModelObj ]     │
│                                  ↑              │
│              Both point to SAME ModelObj        │
│              Mutation via clone affects original│
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  DEEP CLONE                                     │
│                                                 │
│  Original:  [ health=100, model=→ModelObj1 ]    │
│  Clone:     [ health=100, model=→ModelObj2 ]    │
│                                  ↑              │
│              ModelObj2 is a NEW copy of Obj1    │
│              Mutations in clone are independent │
└─────────────────────────────────────────────────┘
```

**Prototype Registry pattern:**
```
PrototypeRegistry {
  Map<String, Entity> prototypes = {
    "troll"  → TrollEntity (loaded, 120ms cost)
    "dragon" → DragonEntity (loaded, 350ms cost)
    "goblin" → GoblinEntity (loaded, 80ms cost)
  }

  getClone(name) {
    return prototypes.get(name).clone();
  }
}
```
New entity in 0.1 ms; first load paid once at startup or first access.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Startup: load prototypes for each entity type
  → full construction cost (120ms) paid once each

Game event: spawn 100 trolls
  → PrototypeRegistry.getClone("troll") × 100
                                    ← YOU ARE HERE
  → each: clone() executes in ~0.1ms
  → post-clone: set position, unique ID, health variance
  → 100 trolls spawned in ~10ms total
  → entities added to game scene
```

**FAILURE PATH:**
```
Shallow clone used on entity with mutable weapon list
  → clone shares weapon list reference with prototype
  → clone picks up weapon → prototype's list mutates
  → all future clones inherit weapon modification
  → bug: every troll starts with previous troll's loot
Fix: deep-clone the weapon list in clone()
```

**WHAT CHANGES AT SCALE:**
At 10,000+ entities, even 0.1 ms per clone adds up (1 second per 10,000 spawns). Parallel cloning on worker threads is possible if deep-clone is thread-safe. Object pools are often used alongside Prototype: the pool holds pre-cloned entities ready to be patched and reused, eliminating clone allocation entirely. At extreme scale (server-side entity simulation), the prototype registry is backed by an in-memory store and clones are distributed to worker nodes.

---

### 💻 Code Example

**Example 1 - BAD: Java's Object.clone() misuse:**
```java
// BAD: Cloneable is a marker - it does not declare clone()
// protected clone() requires unsafe cast
// shallow copy silently shares mutable state
public class Enemy implements Cloneable {
    private List<Item> inventory; // mutable!

    @Override
    public Object clone() {
        try {
            return super.clone(); // SHALLOW - shares inventory!
        } catch (CloneNotSupportedException e) {
            throw new AssertionError(); // cannot happen
        }
    }
}
```

**Example 2 - GOOD: Copy constructor (preferred modern approach):**
```java
public final class EnemyEntity {
    private final String type;
    private final Model model;      // immutable - safe to share
    private final PhysicsBody body; // mutable - must deep copy
    private List<Item> inventory;   // mutable - must deep copy
    private int health;
    private Vector2 position;

    // Full constructor (expensive - used for prototype only)
    public EnemyEntity(String type) {
        this.type      = type;
        this.model     = ModelLoader.load(type);  // 120ms
        this.body      = PhysicsEngine.create();
        this.inventory = ItemLoader.defaults(type);
        this.health    = 100;
    }

    // Copy constructor (cheap - used for cloning)
    public EnemyEntity(EnemyEntity prototype) {
        this.type      = prototype.type;
        this.model     = prototype.model;  // immutable: share
        this.body      = prototype.body.copy(); // deep copy
        this.inventory =
            new ArrayList<>(prototype.inventory); // deep copy
        this.health    = prototype.health;
        this.position  = null; // set by caller after clone
    }

    public EnemyEntity clone() {
        return new EnemyEntity(this);
    }
}
```

**Example 3 - Prototype registry with lazy loading:**
```java
public class EntityRegistry {
    private final Map<String, EnemyEntity> prototypes
        = new ConcurrentHashMap<>();

    // Lazy: load prototype on first request for its type
    public EnemyEntity getClone(String type) {
        EnemyEntity proto = prototypes.computeIfAbsent(
            type,
            t -> new EnemyEntity(t)  // 120ms, paid once
        );
        return proto.clone();   // ~0.1ms, paid every time
    }
}

// Usage:
EntityRegistry registry = new EntityRegistry();
// First troll: 120ms (loads prototype)
EnemyEntity t1 = registry.getClone("troll");
t1.setPosition(10, 20);
// Subsequent trolls: 0.1ms (clones cached prototype)
EnemyEntity t2 = registry.getClone("troll");
t2.setPosition(30, 40);
```

---

### ⚖️ Comparison Table

| Approach | Creation Cost | Memory | Mutability Risk | Best For |
|---|---|---|---|---|
| **Prototype** | Very low (clone) | Shared immutable parts | Deep copy required | Many instances of same template |
| Factory Method | Full constructor | None shared | None | One-off objects, polymorphic types |
| Object Pool | Zero (recycled) | Pre-allocated pool | Must reset state | Short-lived, high-turnover objects |
| Singleton | Once ever | Minimal | Shared state = risk | Exactly one instance needed |
| Direct new | Full constructor | None | None | Simple, cheap construction |

How to choose: use Prototype when construction is expensive and many similar instances are needed. Use Object Pool when instances are recycled rather than discarded. Use Factory Method when polymorphic creation is needed without shared baseline state.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Prototype and Object.clone() are the same | Object.clone() is one Java implementation mechanism. Prototype is a design pattern achievable via copy constructors, serialisation, or any other copy mechanism |
| Cloning is always faster than constructing | Only when construction is expensive. For simple POJOs, `new` is faster than clone() because clone() still allocates and copies all fields |
| Shallow clone is safe for read-only use | Safe only if ALL callers treat the shared object as immutable. If any caller later mutates the shared object, all clones are corrupted |
| Prototype guarantees independent objects | Only if correctly deep-cloned. Shallow clone creates objects that appear independent but share mutable state - the most common Prototype bug |
| You must implement Cloneable to use Prototype | No. Copy constructors, copy-factory static methods, and serialisation-based copy are all valid Prototype implementations. `Cloneable` is a specific Java mechanism, not the pattern itself |

---

### 🚨 Failure Modes & Diagnosis

**1. Shallow Clone Mutates Shared State**

**Symptom:** After cloning an entity and modifying the clone's inventory, the prototype's inventory is also modified. All subsequently spawned entities start with unexpected items.

**Root Cause:** The `inventory` field is a `List` reference. Shallow clone copies the reference - both prototype and clone point to the same `ArrayList`. Mutating it via either reference affects both.

**Diagnostic:**
```java
// After cloning, check object identity:
EnemyEntity proto = registry.getPrototype("troll");
EnemyEntity clone = proto.clone();
System.out.println(
  proto.getInventory() == clone.getInventory());
// true = shallow clone bug (same reference)
// false = deep clone correct (different reference)
```

**Fix:**
In the copy constructor (or clone method): `this.inventory = new ArrayList<>(prototype.inventory);` for a shallow copy of the list (safe if Items are immutable). For mutable Items: `this.inventory = prototype.inventory.stream().map(Item::copy).toList();`.

**Prevention:** For every mutable reference field in the prototype class, verify the copy constructor explicitly copies it.

---

**2. Prototype Modified After Cloning Corrupts Derived Objects**

**Symptom:** A configuration change to the prototype (e.g., adjusting default health) unexpectedly changes the health of entities that were cloned before the change - via a shared mutable sub-object.

**Root Cause:** A field shared between prototype and existing clones was mutated. Either a shallow-cloned reference was mutated on the prototype, or a deliberately shared mutable object was changed.

**Diagnostic:**
```bash
# Log prototype mutations:
# Add logging to prototype setters to track who modifies it:
public void setBaseStats(Stats s) {
    log.warn("Prototype modified: {}",
        Thread.currentThread().getStackTrace()[2]);
    this.baseStats = s;
}
```

**Fix:**
Make the prototype immutable after construction. If the prototype must be updatable, ensure all shared mutable fields are deep-cloned at clone time.

**Prevention:** Design prototypes as effectively immutable. If updates are needed, create a new prototype version.

---

**3. Clone of Subclass Returns Superclass Type**

**Symptom:** `ArmouredTroll extends TrollEntity`. `ArmouredTroll.clone()` is not overridden. The cloned entity is a `TrollEntity` instance, not `ArmouredTroll`. Attempts to cast to `ArmouredTroll` throw `ClassCastException`.

**Root Cause:** The superclass `clone()` creates an instance of the superclass, not the invoking subclass. `super.clone()` uses reflection to create the correct runtime type, but only if `clone()` is properly overridden in every subclass.

**Diagnostic:**
```java
// After cloning, check runtime type:
EnemyEntity clone = proto.clone();
System.out.println(clone.getClass().getName());
// Expected: ArmouredTroll
// Actual:   TrollEntity - subclass clone broken
```

**Fix:**
Every subclass must override `clone()`. With copy constructors, the subclass's copy constructor calls `super(prototype)` and adds its own fields.

**Prevention:** Use copy constructors instead of `Object.clone()` - they are explicitly typed and force each class to manage its own copy logic.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` - Prototype relies on class hierarchy and method overriding for polymorphic cloning
- `Deep Copy vs Shallow Copy` - the most critical implementation decision in Prototype; misunderstanding this causes the most common bugs
- `Cloning` - Java's `Object.clone()` mechanism is the native language support for Prototype; understanding its limitations drives correct implementation

**Builds On This (learn these next):**
- `Object Pool` - common companion to Prototype; pools hold pre-cloned entities ready for immediate use, eliminating even clone allocation cost
- `Flyweight` - shares immutable state between instances without cloning; useful when memory is more constrained than CPU

**Alternatives / Comparisons:**
- `Factory Method` - creates objects via subclass override; better when each new instance needs fresh construction, not a copy of existing state
- `Builder` - constructs objects step-by-step; better when configuration varies significantly per instance rather than sharing a common baseline
- `Abstract Factory` - creates families of related objects; use when groups of compatible objects are needed, not copies of one object

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Create objects by cloning a pre-built     │
│              │ prototype instead of constructing anew    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Expensive construction repeated for       │
│ SOLVES       │ many objects with shared initial state    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pay construction cost once; share         │
│              │ immutable parts; deep-copy mutable parts  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object construction is expensive and      │
│              │ many similar instances are needed         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Construction is cheap; or objects differ  │
│              │ significantly - cloning offers no savings │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast clone performance vs complexity      │
│              │ of correct deep-clone implementation      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pay the construction tax once;           │
│              │  photocopy the rest."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Deep Copy vs Shallow Copy → Object Pool   │
│              │ → Flyweight                               │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When creating a new thing that is mostly like an existing thing,
start from the existing thing and change only the differences.
Duplication of the common state is wasteful; copying and
modifying is efficient.

**Where else this pattern appears:**
- **Git branching:** A new branch starts from the current HEAD
  (the prototype) and diverges only with new commits -- the
  shared history is not duplicated.
- **Database row versioning (temporal tables):** A new record
  version is created by copying the current row and applying
  only the changed columns -- not recomputing the whole record.
- **Container images (Docker layers):** Each layer is a
  prototype -- new images inherit all layers from the base
  and add only the new layer on top.

---

### 💡 The Surprising Truth

Java's `Object.clone()` method -- the built-in mechanism for
Prototype -- is widely considered one of Java's worst design
decisions. Joshua Bloch dedicated an entire item in Effective
Java to advising against it: `clone()` creates objects without
calling a constructor, bypassing all constructor validation, and
requires implementors to understand a complex contract that is
"extralinguistic." The GoF Prototype pattern is sound; Java's
`clone()` mechanism for implementing it is so broken that Bloch
recommends copy constructors or copy factories instead.
---

### 🧠 Think About This Before We Continue

**Q1.** A game entity prototype holds a `pathfindingGraph` object (a cyclic graph of 50,000 nodes representing the level map). You want all enemies to share this graph (read-only), but each enemy's path state (current path, next waypoint) must be independent. Design the copy strategy for `pathfindingGraph` in the clone operation - considering immutability, memory usage, and the risk of one enemy's state corrupting another's - and identify which parts must be deep-copied and which can be safely shallow-copied.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** In a distributed system, a service creates `RequestContext` objects by cloning a prototype that includes a database connection pool reference. The service runs 50 instances (pods), each with its own prototype and connection pool. A developer proposes storing the prototype in a shared distributed cache (Redis) and cloning from it on each pod, claiming it will "share the expensive prototype state cluster-wide." What specific failure will occur with the database connection pool reference when clones are deserialised from Redis onto a different pod, and what architectural rule does this violate?



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A team implements deep cloning of
a complex `OrderGraph` (Order → LineItems → Products → Suppliers)
using Prototype/clone. A performance test shows the deep clone
takes 8ms per call at 1000 req/s. Identify two alternative
approaches that avoid the deep clone entirely while preserving
the required immutability guarantees.

*Hint: Consider the Complete Picture section's "what changes
at scale" note -- persistent data structures and structural
sharing (as in functional languages) are the key insight.*
