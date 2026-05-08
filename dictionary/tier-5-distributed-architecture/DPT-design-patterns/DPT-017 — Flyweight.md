---
layout: default
title: "Flyweight"
parent: "Design Patterns"
nav_order: 17
permalink: /design-patterns/flyweight/
id: DPT-017
category: Design Patterns
difficulty: ★★★
depends_on: Object-Oriented Programming (OOP), Immutability, Object Pool, Caching
used_by: String Interning, Character Rendering, Particle Systems, Icon Caching
related: Object Pool, Singleton, Prototype, Composite
tags:
  - pattern
  - deep-dive
  - performance
  - memory
  - java
---

# DPT-017 — Flyweight

⚡ TL;DR — Flyweight reduces memory usage by sharing immutable intrinsic state among many fine-grained objects, storing only extrinsic (context-specific) state externally.

| #777 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Immutability, Object Pool, Caching | |
| **Used by:** | String Interning, Character Rendering, Particle Systems, Icon Caching | |
| **Related:** | Object Pool, Singleton, Prototype, Composite | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A rich text editor displays 10,000 characters. Each `CharacterObject` holds: the glyph data (font face, font size, rendering hints: 2 KB), the character code (2 bytes), and position (8 bytes). Total: 10,000 × ≈2050 bytes = **20 MB** for 10,000 characters — most of it duplicated glyph data. Scale to a million-character document: 2 GB just for character objects. The editor runs out of heap and crashes. 99% of memory stores the same "A" glyph data 5,000 times.

**THE BREAKING POINT:**
In graphical applications, game engines, and text rendering systems, tens of thousands to millions of fine-grained objects are needed simultaneously. If each carries its full state (including shared visual data like glyphs, textures, colours), memory consumption becomes prohibitive. GC pressure from millions of large objects causes pause time spikes. The application cannot scale to realistic data sizes.

**THE INVENTION MOMENT:**
This is exactly why the Flyweight pattern was created. Separate object state into: **intrinsic** (shared, immutable — the glyph data for "A") and **extrinsic** (per-instance, context-dependent — position, selection state). The intrinsic state is shared: one object for all "A"s. The extrinsic state is passed in at use time. 10,000 characters use at most 256 Flyweight glyph objects. Memory: 256 × 2 KB + 10,000 × 10 bytes = ≈512 KB + 100 KB = **612 KB** vs 20 MB.

---

### 📘 Textbook Definition

The **Flyweight** pattern is a structural design pattern that uses sharing to support a large number of fine-grained objects efficiently. A Flyweight stores intrinsic state — information independent of context and shared across instances. Extrinsic state — information that varies by context — is stored externally and passed to flyweight methods when needed. A `FlyweightFactory` manages the pool of shared flyweight instances, returning an existing one when a matching one exists. The pattern enables object-like semantics for large populations at fraction of the memory cost.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Share the expensive unchanging part of many objects; store only unique per-instance data separately.

**One analogy:**
> A theatre wardrobe. Instead of each actor owning their own suit of armour (expensive, heavy), the wardrobe has one set of each armour type. When an actor needs armour, they borrow from the wardrobe. The armour (intrinsic state) is shared. The actor wearing it (extrinsic state) changes per scene.

**One insight:**
Flyweight is not about the same object being used at the same time — it IS the same object. All 5,000 letter "A"s on screen share a single `CharGlyph` object. The position and colour of each "A" is not IN the flyweight — it is passed as a parameter when the flyweight is asked to render.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An application needs a very large number of similar objects.
2. Most object state can be made extrinsic (context-dependent, stored externally).
3. Object identity (each character is a distinct object) is less important than the values each object represents.

**DERIVED DESIGN:**
Given invariant 1+2: extract the intrinsic (shared) state into a single shared object per unique state value. The client stores only an identifier to the flyweight and the extrinsic data. Given invariant 3: all objects with the same intrinsic state share one flyweight — client code treats them as logically distinct but they are physically identical.

The `FlyweightFactory` is a factory + cache: `Map<StateKey, Flyweight>`. On `getOrCreate(key)`: look up the key; if found, return the cached flyweight; if not, create and cache. The factory is often a Singleton (one cache per application).

Key design constraint: **Flyweights must be immutable.** If the intrinsic state could be modified, one modification would affect every logical object sharing that flyweight — catastrophically corrupting all of them.

**THE TRADE-OFFS:**
**Gain:** Dramatic memory reduction for large populations of similar objects; GC pressure reduced (fewer, longer-lived objects instead of many short-lived ones); cache locality improved (shared objects stay hot in CPU cache).
**Cost:** Extrinsic state management complexity (callers must pass context at every method call); code is harder to reason about (the flyweight object is not "the character" — it's a shared representation); not applicable if intrinsic and extrinsic state are deeply intertwined; thread-safety of the factory required.

---

### 🧪 Thought Experiment

**SETUP:**
A particle system simulates 1,000,000 rain particles. Each particle has: texture (1 KB), colour (4 bytes), size (4 bytes), position (16 bytes), velocity (16 bytes), lifetime (4 bytes). With unique objects: 1,000,000 × 1,044 bytes = **1,044 MB** (1 GB). The GPU runs out of drawcall budget.

**WHAT HAPPENS WITHOUT FLYWEIGHT:**
Each particle is an independent `RainParticle` object holding its own copy of the raindrop texture. 1 GB of RAM for textures alone — all identical copies of the same 1 KB bitmap. GC can never reclaim this because all objects are alive. Simulation runs at 3 FPS due to memory bandwidth saturation.

**WHAT HAPPENS WITH FLYWEIGHT:**
One `RainDropFlyweight` holds the texture (1 KB). 1,000,000 `ParticleState` structs hold position+velocity+lifetime (36 bytes each). Memory: 1 KB for texture + 1,000,000 × 36 bytes = **36 MB** — a 29× reduction. GC sees one long-lived flyweight and 1M small value structs. Simulation runs at 60 FPS.

**THE INSIGHT:**
Flyweight's memory saving is proportional to how much state is shared versus unique. If 99% of an object's bytes are shared (texture), Flyweight gives 100× savings. If only 10% is shared, the savings are modest.

---

### 🧠 Mental Model / Analogy

> Flyweight is like font rendering. The letter "A" in Arial 12pt is drawn from one shared glyph definition. When placed at different positions on screen, the glyph is not recreated — it is stamped at each position. The glyph (flyweight) is shared; the stamping location (extrinsic state: x, y coordinate) is unique per occurrence.

- "Glyph definition" → flyweight (intrinsic state: shape, rendering hints)
- "Position on screen" → extrinsic state (passed at render time)
- "All 'A's sharing one glyph" → flyweight sharing
- "Font cache" → FlyweightFactory (Map<Character, Glyph>)
- "Rendering 'A' at position (100,200)" → `glyph.render(canvas, 100, 200)`

Where this analogy breaks down: a font glyph is visually identical at every position. A flyweight can have extrinsic state that changes its appearance (colour, scale) — so each shared instance CAN look different when rendered with different extrinsic state.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Flyweight is "share the original, stamp copies everywhere." Instead of making 10,000 separate "A" objects, you have one "A" object and stamp it at 10,000 positions. Each stamp looks independent to the viewer. Only one actual object exists in memory.

**Level 2 — How to use it (junior developer):**
Identify the intrinsic state (same for all instances of this type) and extrinsic state (varies per instance). Create a `Flyweight` class with only the intrinsic state. Its methods take extrinsic state as parameters. Create a `FlyweightFactory` with a `Map<Key, Flyweight>` cache method. Client code calls `factory.getFlyweight(key)` and then `flyweight.operation(extrinsicState)`. Store only the key + extrinsic data per logical object, not the full flyweight.

**Level 3 — How it works (mid-level engineer):**
The factory uses lazy initialisation (`computeIfAbsent`) for thread safety. The `Map` key must implement `equals` and `hashCode` correctly — a wrong key can cause distinct flyweights to be returned for the same logical state (no sharing). `ConcurrentHashMap` with `computeIfAbsent` is thread-safe for the factory. The objects returned by the factory must be immutable — if any field is mutated, all logical objects using that flyweight are affected. In Java, this is enforced via `final` fields and no setters. Java's `String.intern()` is a built-in flyweight: `"hello".intern()` returns a canonical shared `String` instance from the JVM's string pool.

**Level 4 — Why it was designed this way (senior/staff):**
Flyweight predates modern JVM optimisations but remains relevant. Java's string pool and small integer cache (`Integer.valueOf(-128 to 127)`) are built-in application of Flyweight. In game engines, the Entity-Component-System (ECS) architecture uses Flyweight implicitly: component types (the archetype data) are shared via component arrays; entity-level customisation is stored in separate data columns. The key theoretical insight: Flyweight moves the definition of "object identity" from physical (each object is unique) to logical (objects with identical intrinsic state are the same flyweight). This CAN violate expectations in equals/hashCode: two `CharacterGlyph` flyweights for 'A' are the SAME object — `==` is true. Two "A" characters at different positions are logically different but physically equal. This confusion requires careful API design.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  FLYWEIGHT PATTERN — MEMORY LAYOUT                   │
│                                                      │
│  WITHOUT FLYWEIGHT (1M particles):                   │
│  [Particle1: texture(1KB) + pos(16B) + vel(16B)]    │
│  [Particle2: texture(1KB) + pos(16B) + vel(16B)]    │
│  ... × 1,000,000                                     │
│  = ~1 GB                                             │
│                                                      │
│  WITH FLYWEIGHT:                                     │
│  FlyweightFactory:                                   │
│    "rain" → RainFlyweight [texture(1KB)]  ← SHARED   │
│                                                      │
│  Client-side storage (extrinsic, per particle):      │
│  [flyweightKey="rain", pos(16B), vel(16B)] × 1M      │
│  = ~36MB                                             │
└──────────────────────────────────────────────────────┘
```

**Factory lookup flow:**
```
Client.getParticle("rain"):
  factory.getFlyweight("rain")
    → map.computeIfAbsent("rain", k ->
          new RainFlyweight(textureLoader.load("rain.png")))
    → returns SAME RainFlyweight for all "rain" requests

Client renders the particle:
  flyweight.render(canvas, particle.x, particle.y,
                   particle.velocity, particle.lifetime)
  ↑ extrinsic state passed as parameters each time
```

**Immutability enforcement:**
```java
public final class CharGlyph {   // FINAL class
    private final char character; // FINAL field
    private final Font font;      // FINAL field
    // No setters. Shared safely across all usages.

    void render(Graphics g, int x, int y) {
        // x, y are extrinsic — passed in each render call
        g.drawGlyph(character, font, x, y);
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Application starts up
  → FlyweightFactory initialised (empty cache)

User types "Hello World"
  → For each character:
     factory.getGlyph(char, font)  ← YOU ARE HERE
     → cache hit? return existing flyweight
     → cache miss? create, cache, return flyweight
  → 8 unique flyweights for 11 chars (space counted once)

Render:
  → for each position: glyph.render(ctx, x, y)
  → 11 renders, 8 distinct flyweights
  → memory for glyphs: 8 objects (not 11)
```

**FAILURE PATH:**
```
Flyweight state accidentally mutated
  → setFont() called on flyweight
  → ALL 5000 'A' characters in document change font
  → No error — silent corruption
Fix: make Flyweight immutable (final class, final fields)
```

**WHAT CHANGES AT SCALE:**
At 1M+ objects (game particle systems, large document editors), Flyweight is critical. The factory cache grows proportionally to unique intrinsic state values (not total object count). If there are only 256 distinct character glyphs, the cache stays at 256 entries regardless of document size. At 100M objects, profiling will reveal whether the flyweight factory's `Map` lookup is a bottleneck — in that case, array-indexed flyweights (array position = flyweight key) provide O(1) lookup without HashMap overhead.

---

### 💻 Code Example

**Example 1 — BAD: Each object holds full state:**
```java
// BAD: each tree object holds full 1MB texture
public class Tree {
    private final BufferedImage texture; // 1MB per tree!
    private double x, y;
    private double height;
    private String species;

    public Tree(String species, double x, double y) {
        this.texture = loadTexture(species); // 1MB per tree
        this.x = x; this.y = y;
    }
}
// 1,000,000 trees = 1 TB of texture data
```

**Example 2 — GOOD: Flyweight separating intrinsic and extrinsic:**
```java
// FLYWEIGHT: immutable intrinsic state — shared
public final class TreeType {
    private final String species;
    private final BufferedImage texture; // 1MB, shared
    private final Color trunkColour;

    public TreeType(String species) {
        this.species     = species;
        this.texture     = loadTexture(species); // once only
        this.trunkColour = deriveColour(species);
    }

    // Extrinsic state passed as parameters — NOT stored here
    public void render(Graphics g, double x, double y,
                       double height) {
        g.drawImage(texture, (int)x, (int)y,
                    null);    // uses shared texture
        drawTrunk(g, x, y, height, trunkColour);
    }
}

// FLYWEIGHT FACTORY: cache per species
public class TreeFactory {
    private static final Map<String, TreeType> cache
        = new HashMap<>();

    public static TreeType getTreeType(String species) {
        return cache.computeIfAbsent(
            species, TreeType::new);
    }
}

// CLIENT: stores reference + extrinsic state only
public class Tree {
    private final TreeType type; // reference to flyweight
    private double x, y, height; // extrinsic state only

    public Tree(String species, double x, double y,
                double height) {
        // Reuse shared flyweight — no texture duplication
        this.type   = TreeFactory.getTreeType(species);
        this.x      = x;
        this.y      = y;
        this.height = height;
    }

    public void render(Graphics g) {
        // pass extrinsic state to flyweight's method
        type.render(g, x, y, height);
    }
}

// Usage: 1,000,000 trees, 3 TreeType flyweights
List<Tree> forest = new ArrayList<>();
for (int i = 0; i < 1_000_000; i++) {
    forest.add(new Tree(
        randomSpecies(), randomX(), randomY(),
        randomHeight()));
}
// Memory: 3 × 1MB (textures) + 1M × 40B (Tree fields)
// = 3 MB + 40 MB = ~43 MB (vs 1 TB without flyweight)
```

**Example 3 — Java String pool (built-in Flyweight):**
```java
// Java's String.intern() is Flyweight
String a = new String("hello").intern(); // canonical
String b = new String("hello").intern(); // SAME object
System.out.println(a == b);  // true (same flyweight)

// String literals are automatically interned:
String c = "hello";
String d = "hello";
System.out.println(c == d);  // true (string pool)

// Integer cache: flyweight for -128 to 127
Integer x = Integer.valueOf(100);
Integer y = Integer.valueOf(100);
System.out.println(x == y);  // true (cached flyweight)

Integer p = Integer.valueOf(200);
Integer q = Integer.valueOf(200);
System.out.println(p == q);  // false (outside cache range)
```

---

### ⚖️ Comparison Table

| Pattern | Sharing Type | Mutability | Per-instance state | Best For |
|---|---|---|---|---|
| **Flyweight** | Intrinsic state value-shared | Must be immutable | Extrinsic, stored outside | 1M+ similar fine-grained objects |
| Object Pool | Object reference shared | Reset between uses | None (reset on return) | Expensive-to-create reusable objects |
| Singleton | Single instance | Can be mutable | None (one global) | One shared resource manager |
| Prototype | Clone once per use | Independent per clone | Per-clone | Expensive construction, disposable |
| Cached Factory | Object cached by key | Often immutable | Per factory entry | Moderate reuse, keyed by parameter |

How to choose: use Flyweight when you need millions of similar objects and most of their state is identical (shareable). Use Object Pool when objects are expensive to CREATE (not just store), have per-use mutable state, and are returned after use. Use Singleton when exactly one instance is needed, not millions.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Flyweight and Object Pool are the same | Object Pool reuses objects over time (borrow then return). Flyweight shares an object simultaneously across many users simultaneously. An Object Pool has idle objects; a Flyweight has no "idle" concept |
| Flyweight objects can be modified | Flyweight MUST be immutable. Any mutation corrupts all logical objects sharing it. Making a Flyweight mutable violates the pattern's core invariant |
| Flyweight is only useful for text/graphics | Flyweight applies to any domain with many similar objects: database connection metadata, read-only configuration objects, currency denomination objects, shared lookup tables |
| The extrinsic state must be primitive types | Extrinsic state can be any type — but passing complex mutable objects as extrinsic state risks unintended coupling between the flyweight and external state |
| Flyweight always requires a FlyweightFactory | The factory is the standard mechanism. For bounded, known sets (like 26 letters), a simple array of flyweights works without a factory at all |

---

### 🚨 Failure Modes & Diagnosis

**1. Flyweight State Mutated — Silent Corruption**

**Symptom:** After a UI theme change, ALL document characters change colour, not just the selected ones. No exceptions — the change is instant and global.

**Root Cause:** The `CharGlyph` flyweight's `setFontColour()` was called for one character, mutating the shared object and affecting all instances using it.

**Diagnostic:**
```java
// Verify flyweight is correctly shared and immutable:
CharGlyph glyph1 = factory.getGlyph('A', font);
CharGlyph glyph2 = factory.getGlyph('A', font);
assert glyph1 == glyph2; // same reference = sharing
// If this assert holds, mutation on glyph1 affects glyph2
```

**Fix:**
Remove all mutating methods from the `Flyweight` class. Make all fields `final`. Declare the class `final` to prevent mutating extensions.

**Prevention:** Design rule: flyweights are value objects — no setters, all fields final, equals/hashCode based on value.

---

**2. Incorrect Cache Key Causes Duplicate Flyweights**

**Symptom:** Memory measurements show 10,000 flyweight objects instead of expected 256 (one per character). Sharing is not occurring.

**Root Cause:** The cache key in the factory uses `==` reference equality instead of `.equals()`. Each call with a new `String` key creates a new flyweight even if the string content is identical.

**Diagnostic:**
```java
// Print factory map size vs expected unique entries:
System.out.println("Flyweights: " + factory.size());
// If >> expected unique values: cache key equality broken

// Test key equality:
String key1 = new String("Arial");
String key2 = new String("Arial");
System.out.println(key1 == key2);     // false (wrong!)
System.out.println(key1.equals(key2)); // true (correct)
```

**Fix:**
Use `HashMap` (uses `.equals()`) not identity-based map. Ensure cache key class implements `equals` and `hashCode` based on value, not reference.

**Prevention:** Test factory: verify `factory.get(k1) == factory.get(k2)` when `k1.equals(k2)`.

---

**3. Extrinsic State Accidentally Stored in Flyweight**

**Symptom:** Two "A" characters at different positions both jump to the same position after a position update. Extrinsic state "leaked into" the flyweight.

**Root Cause:** The `position` field was added to the `Glyph` flyweight during development ("just for convenience"), violating intrinsic-only rule.

**Diagnostic:**
```bash
# Audit flyweight class for mutable or per-instance state:
grep -n "private.*=" src/CharGlyph.java \
  | grep -v "final"
# Any non-final field in a Flyweight is a red flag
```

**Fix:**
Move `position` to the client-side `Character` record. Pass it as a parameter to `glyph.render(g, x, y)`.

**Prevention:** Flyweight field checklist: every field must be final AND have the same value for all logical instances that share this flyweight.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Immutability` — flyweights must be immutable; understanding Java's immutability mechanisms (final, defensive copies) is required
- `Caching` — the FlyweightFactory is essentially a cache; understanding cache key design prevents the most common factory bugs
- `Object Pool` — frequently confused with Flyweight; understanding the difference (simultaneous sharing vs sequential borrowing) clarifies both

**Builds On This (learn these next):**
- `String Interning` — Java's built-in Flyweight application; understanding how the JVM string pool works reinforces Flyweight concepts
- `Composite` — Flyweights are often leaf nodes in a Composite tree; a document tree where leaves are shared glyphs is the canonical Flyweight + Composite combination
- `Entity-Component-System (ECS)` — modern game architecture applying Flyweight at scale; archetype arrays are the flyweight mechanism

**Alternatives / Comparisons:**
- `Object Pool` — reuses objects over time (one at a time); Flyweight shares objects simultaneously (many at once)
- `Prototype` — creates independent copies from a template; opposite of Flyweight's goal (sharing, not copying)
- `Value Object` — immutable carriers of values; Flyweights are cached Value Objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared immutable objects for the common   │
│              │ state; per-instance state passed at call  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Millions of similar objects each storing  │
│ SOLVES       │ the same expensive data → RAM exhaustion  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Flyweight = immutable shared intrinsic +  │
│              │ caller-managed extrinsic (passed in)      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 100K+ objects where >50% of state is      │
│              │ identical across instances                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Each "instance" has fully unique state;   │
│              │ or object count is small (< 10,000)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dramatic memory savings vs complexity of  │
│              │ separating intrinsic/extrinsic state      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Share the blueprint; stamp it            │
│              │  at each unique location."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ String Interning → Composite →            │
│              │ Object Pool                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A game has 5 types of projectiles (bullet, arrow, rocket, fireball, ice). Each projectile type has a shared visual (texture: 500 KB), audio clip (200 KB), and hit detection polygon (10 KB). Per-instance state: position (16 bytes), velocity (16 bytes), damage (4 bytes), owner (8 bytes). Using Flyweight, calculate: (a) memory for 100,000 simultaneous projectiles with and without Flyweight, (b) the exact threshold (number of projectiles) above which Flyweight becomes beneficial, (c) what happens to memory calculations if the hit detection polygon must be mutated per-instance (e.g., deformed on impact).

**Q2.** Java's `Integer.valueOf(int)` returns cached flyweight instances for values -128 to 127. A developer writes: `Integer a = 1000; Integer b = 1000; if (a == b) sendPayment();`. The payment is never sent despite `a` and `b` representing the same value. Then the developer changes `1000` to `100` and the payment IS sent. Explain the exact mechanism causing this inconsistency, why the flyweight cache boundary at 127 makes this particularly dangerous in financial code, and what the correct comparison should always be.

