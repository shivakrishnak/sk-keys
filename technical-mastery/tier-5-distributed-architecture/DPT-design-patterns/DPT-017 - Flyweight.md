---
id: DPT-017
title: Flyweight
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-010
used_by: DPT-065
related: DPT-010, DPT-011, DPT-006
tags:
  - pattern
  - structural
  - advanced
  - performance
  - memory
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/design-patterns/flyweight/
---

⚡ TL;DR - Flyweight shares common state between large
numbers of fine-grained objects to reduce memory usage -
by splitting "intrinsic" (shared, immutable) state from
"extrinsic" (per-instance, caller-provided) state.

| #17 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-010 | |
| **Used by:** | DPT-065 | |
| **Related:** | DPT-010, DPT-011, DPT-006 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A text editor renders a document with 100,000 characters.
A naive design: one `Character` object per character,
each containing: the character's glyph (font, size, color,
rendering data - ~2KB), the character's position in the
document (x, y - 8 bytes), and the character itself (2 bytes).
100,000 objects x ~2KB each = 200MB just for character
rendering data - unacceptable for a text editor.

**THE BREAKING POINT:**
The rendering data (glyph) is identical for all 'A'
characters in the same font and size. A document with
10,000 'a' characters allocates the same 2KB of glyph
data 10,000 times. The duplication is the problem.

**THE INVENTION MOMENT:**
Flyweight: separate the glyph data (intrinsic - same for
all 'a' characters in Arial-12) from the position
(extrinsic - different for each 'a'). Store one `GlyphFlyweight`
per unique (char, font, size, color) combination. Each
character in the document references the shared flyweight
and provides its own position. Memory: one 2KB flyweight
per unique glyph + 8 bytes per character position =
~10KB for flyweights + 800KB for positions = 810KB vs 200MB.

**EVOLUTION:**
Flyweight appears wherever many fine-grained objects share
large amounts of common state. Java's String interning
is a Flyweight application: `String.intern()` returns
a shared instance from the string pool. Java's `Integer
.valueOf()` caches -128 to 127. The JVM's constant pool
is a Flyweight factory for class literals, string literals,
and numeric constants. Minecraft-style voxel games use
Flyweight for block types: millions of blocks, but only
hundreds of distinct block type objects.

---

### 📘 Textbook Definition

The **Flyweight** pattern is a Structural design pattern
that uses sharing to efficiently support large numbers of
fine-grained objects. A Flyweight is a shared object that
can be used in multiple contexts simultaneously. The
pattern separates object state into INTRINSIC (stored in
the flyweight; context-independent; shareable) and EXTRINSIC
(stored or computed by the client; context-dependent; not
shared). The Flyweight stores only intrinsic state; extrinsic
state is passed to flyweight operations by the client.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Flyweight shares the "heavy" parts of many similar objects
while each object provides its own "light" unique parts.

**One analogy:**
> A chess game has 32 pieces. Each piece has a TYPE (rook,
> bishop, pawn - the shared flyweight: piece rules, visual
> appearance) and a POSITION on the board (extrinsic: changes
> each move). Instead of 32 heavy piece objects, you have
> 12 shared flyweight types and 32 lightweight position
> records. The board stores positions; the flyweight stores
> behavior and appearance.

**One insight:**
Flyweight's key insight: what is "the same" for many objects
(intrinsic state) and what is "different" for each (extrinsic
state)? Once separated, shared intrinsic state is allocated
once regardless of how many instances exist.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Intrinsic state is IMMUTABLE - it cannot be changed
   after the flyweight is created (because it is shared
   by many contexts; mutation would corrupt all sharers).
2. Extrinsic state is NEVER stored in the flyweight - it
   is passed as a parameter to flyweight operations by
   the client.
3. Client objects hold a reference to the flyweight (shared)
   and their own extrinsic state (local).

**DERIVED DESIGN:**
Three participants:
- **Flyweight**: interface for flyweight objects; methods
  accept extrinsic state as parameters
- **ConcreteFlyweight**: stores intrinsic state; implements
  operations using intrinsic + extrinsic state
- **FlyweightFactory**: creates and caches flyweights;
  returns existing flyweight if already created (the key
  to memory savings)

**INTRINSIC vs EXTRINSIC STATE:**
This is the critical design decision:
- Intrinsic: same value across ALL instances sharing this
  flyweight (glyph data, piece rules, block type properties)
- Extrinsic: unique to each use context (character position,
  piece position, block location)

**TRADE-OFFS:**

**Gain:** Dramatic memory reduction when many similar
objects share large common state.

**Cost:** Complexity: state is split between flyweight and
client. Extrinsic state management is the client's
responsibility. If intrinsic state is actually variable
(wrong classification), shared mutation causes bugs.
If objects are not repeated enough times, the factory
overhead negates memory savings.

---

### 🧪 Thought Experiment

**SETUP:**
A traffic simulation with 1,000,000 cars. Each car has:
a 3D model (5MB of geometry and textures, shared by all
cars of the same model type), a color, and a position
(x, y, z). There are 50 car model types.

**WITHOUT FLYWEIGHT:**
1,000,000 car objects x 5MB = 5TB of data (impossible).

**WITH FLYWEIGHT:**
50 car type flyweights x 5MB = 250MB (model + textures).
1,000,000 car instances x 20 bytes (model reference + color
+ position x,y,z) = 20MB.
Total: 270MB vs 5TB - a 99.99% reduction.

**THE INSIGHT:**
The flyweight factory ensures each of the 50 car types
is loaded exactly once. Each car instance is a tiny
record: "I am a model-3 car, red, at coordinates (x,y,z)."
The rendering engine calls `carType.render(x, y, z, color)` -
the flyweight does the expensive rendering; the instance
just provides its position.

---

### 🧠 Mental Model / Analogy

> Flyweight is a STENCIL. Instead of drawing every letter
> in a document by hand (allocating unique state per letter),
> you use letter stencils. Each letter 'A' (flyweight)
> is one stencil used in 10,000 places. The stencil defines
> the shape; the painter (client) provides the position
> and color (extrinsic state) at each use. One stencil,
> many uses, trivial cost per use.

- "Stencil" = Flyweight
- "Letter shape (fixed for all A's)" = intrinsic state
- "Position and color each time" = extrinsic state
- "Stencil library" = FlyweightFactory

**Where this analogy breaks down:**
A stencil is stateless in the analogy. Flyweights can have
rich intrinsic state (rendering algorithms, game logic)
as long as it does not change. The stencil analogy captures
the "shared template" aspect but not the "shared behavior"
aspect.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Flyweight means "one shared copy of the heavy stuff, each
use provides the lightweight unique stuff." Many objects
refer to one shared object instead of each holding their
own copy of the same data.

**Level 2 - How to use it (junior developer):**
Identify what is THE SAME across all similar objects
(intrinsic). Make that data immutable and put it in a
Flyweight class. Identify what is DIFFERENT for each use
(extrinsic). Pass extrinsic state as parameters when using
the Flyweight. Create a FlyweightFactory that caches and
reuses Flyweight instances.

**Level 3 - How it works (mid-level engineer):**
The FlyweightFactory maintains a `Map<Key, Flyweight>`.
`getFlyweight(key)` returns the cached instance if it
exists; creates and caches it if not. Clients call
`flyweight.operation(extrinsicState)` - the flyweight
uses its own intrinsic state plus the provided extrinsic
state to do the work. The key to correctness: intrinsic
state MUST be truly context-independent (same value in
all uses). Any field that varies by use context is
extrinsic.

**Level 4 - Why it was designed this way (senior/staff):**
Flyweight is the structural pattern that makes the difference
between theoretically possible and practically feasible
for systems with millions of objects. Text rendering,
game worlds, network packet processing, and font systems
all hit the Flyweight threshold: the data per object is
large enough that N instances x object size exceeds
available memory. The pattern emerged from the exact
need to render proportional fonts in text editors (the
GoF example): font rendering data is megabytes; documents
have hundreds of thousands of characters; without sharing,
rendering a large document is impossible.

**Level 5 - Mastery (distinguished engineer):**
Flyweight and the JVM's constant pool are structurally
equivalent: the JVM maintains one instance of each string
literal that appears in bytecode (`ldc "hello"` returns
the shared instance from the string pool). `Integer.valueOf(-128)`
to `valueOf(127)` return cached instances. These are JVM-
level Flyweight implementations for common values that
appear millions of times in typical Java programs.
`Enum` types in Java are Flyweights: there is exactly one
instance of `Direction.NORTH` regardless of how many times
it is referenced. Interned strings, cached boxed integers,
and enum constants are all Flyweight in the Java runtime.

---

### ⚙️ How It Works (Mechanism)

```
Flyweight Structure
┌─────────────────────────────────────────────────────────┐
│  FlyweightFactory                                       │
│  - cache: Map<CharKey, CharFlyweight>                   │
│  + getFlyweight(char, font, size): CharFlyweight        │
│    key = CharKey(char, font, size)                      │
│    if (!cache.containsKey(key)):                        │
│      cache.put(key, new CharFlyweight(char, font, size))│
│    return cache.get(key)                                │
│                                                         │
│  CharFlyweight (intrinsic state only - IMMUTABLE)       │
│  - char: char       ← shared by all 'A' in Arial-12     │
│  - font: FontData   ← shared by all Arial-12 chars      │
│  - size: int        ← shared                            │
│  - glyphData: byte[]← expensive; shared                 │
│  + render(x, y, Color color): void                      │
│    // x, y, color are EXTRINSIC - passed in             │
│    // glyphData is INTRINSIC - used from this           │
│                                                         │
│  DocumentChar (client - stores extrinsic state)         │
│  - flyweight: CharFlyweight  ← shared reference         │
│  - x: int                   ← extrinsic (position)      │
│  - y: int                   ← extrinsic (position)      │
│  - color: Color              ← extrinsic (per char)     │
│  + render(): void                                       │
│    flyweight.render(x, y, color)  ← pass extrinsic      │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Document loads 100,000 chars
  → For each char: factory.getFlyweight(char, font, size)
  → Factory returns cached flyweight (or creates once)
  → DocumentChar stores: flyweight ref + x, y, color
Document renders:
  → For each DocumentChar: flyweight.render(x, y, color)
  → Flyweight uses intrinsic glyph data + extrinsic
    pos/color
Memory: N flyweights (small) + 100K DocumentChars (tiny)
```

**FAILURE PATH:**
```
Mutation attempt on shared flyweight:
  flyweight.setColor(Color.RED)
  → Changes color for ALL characters sharing this flyweight
  → Text renders with wrong colors
Detection: make flyweight final, all fields final
Prevention: intrinsic state must be immutable
```

**WHAT CHANGES AT SCALE:**
Flyweight IS the scale optimization. As N (number of
objects) grows, memory consumption grows O(unique types)
instead of O(N). At extreme scale (billions of objects),
consider whether the extrinsic state itself can be compacted
(e.g., use int arrays instead of DocumentChar objects).

---

### 💻 Code Example

**Example 1 - Without Flyweight (memory explosion):**

```java
// BAD: one full char object per character in document
class DocumentChar {
    private char c;
    private String font;
    private int size;
    private byte[] glyphData; // 2KB per char - the problem
    private int x;
    private int y;

    DocumentChar(char c, String font, int size, int x, int y) {
        this.c = c;
        this.font = font;
        this.size = size;
        this.glyphData = loadGlyph(c, font, size); // expensive!
        this.x = x;
        this.y = y;
    }
}
// 100,000 chars x 2KB = 200MB for glyph data alone
```

**Example 2 - Flyweight solution:**

```java
// GOOD: share glyphData across all instances of same char+font+size

// Flyweight: intrinsic state only, IMMUTABLE
final class CharGlyph {
    private final char c;
    private final String font;
    private final int size;
    private final byte[] glyphData; // expensive but shared

    CharGlyph(char c, String font, int size) {
        this.c = c;
        this.font = font;
        this.size = size;
        this.glyphData = loadGlyph(c, font, size); // loaded ONCE
    }

    // Extrinsic state passed as parameters, never stored
    void render(int x, int y, Color color) {
        // Render using glyphData (intrinsic) at x,y (extrinsic)
        GraphicsEngine.draw(glyphData, x, y, color);
    }
}

// FlyweightFactory: cache ensures one instance per unique glyph
class CharGlyphFactory {
    private final Map<String, CharGlyph> cache = new HashMap<>();

    CharGlyph getGlyph(char c, String font, int size) {
        String key = c + "-" + font + "-" + size;
        return cache.computeIfAbsent(key,
            k -> new CharGlyph(c, font, size)); // create once
    }
}

// Client: stores reference to flyweight + extrinsic state
record DocumentChar(CharGlyph glyph, int x, int y, Color color) {
    void render() {
        glyph.render(x, y, color); // pass extrinsic to flyweight
    }
}

// Usage:
CharGlyphFactory factory = new CharGlyphFactory();
List<DocumentChar> doc = new ArrayList<>();

for (int i = 0; i < 100_000; i++) {
    char c = text.charAt(i);
    // Factory returns SAME CharGlyph for same c+font+size
    CharGlyph glyph = factory.getGlyph(c, "Arial", 12);
    doc.add(new DocumentChar(glyph, xPos[i], yPos[i], Color.BLACK));
}
// Memory: ~100 unique glyphs x 2KB = 200KB (not 200MB)
// +  100,000 DocumentChars x ~24 bytes = 2.4MB
// Total: 2.6MB instead of 200MB
```

**Example 3 - Java's built-in Flyweight (Integer cache):**

```java
// RECOGNITION: Integer.valueOf() is a Flyweight factory
Integer a = Integer.valueOf(127);
Integer b = Integer.valueOf(127);
System.out.println(a == b); // true - SAME object (flyweight)

Integer c = Integer.valueOf(128);
Integer d = Integer.valueOf(128);
System.out.println(c == d); // false - outside cache range

// String interning is also Flyweight:
String s1 = "hello"; // string pool flyweight
String s2 = "hello"; // returns same instance from pool
System.out.println(s1 == s2); // true - same flyweight

// Enum constants are Flyweights - exactly one instance:
Direction.NORTH == Direction.NORTH; // always true
```

**How to test/verify correctness:**
Test that the FlyweightFactory returns THE SAME instance
(using `==` identity, not `.equals()`) for the same key.
Test that invoking flyweight with different extrinsic
state does not mutate the flyweight's intrinsic state.
Test memory usage before/after with a memory profiler.

---

### ⚖️ Comparison Table

| Approach           | Memory per obj | Object count | State sharing | Complexity |
| ------------------ | -------------- | ------------ | ------------- | ---------- |
| **Flyweight**      | Tiny (ref only)| N intrinsic  | Yes (explicit)| High       |
| Regular object     | Full           | N total      | No            | None       |
| Object Pool        | Full           | max pool sz  | No (exclusive)| Medium     |
| Singleton          | Full (1)       | 1            | Implicit      | Low        |

**How to choose:** Use Flyweight when: (1) a large number
of objects with shared state are needed, (2) most object
state can be made extrinsic, (3) object identity does not
matter (multiple contexts use the same instance).
Use Object Pool when: objects are expensive to create and
must be used exclusively (one at a time). Use Singleton
when exactly one instance is needed for lifecycle reasons.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Flyweight is the same as Singleton | Singleton: exactly ONE instance exists for lifecycle reasons. Flyweight: ONE instance per unique key exists for MEMORY reasons; there may be many flyweight instances |
| Flyweight requires immutable objects | Flyweight REQUIRES the shared (intrinsic) portion to be immutable; the extrinsic state passed by clients is NOT stored in the flyweight and CAN vary freely |
| Flyweight is only for graphics/text | Flyweight applies to any domain with many fine-grained objects sharing large common state: game entities, network packet processing, rule evaluation, type registries |
| Flyweight and Object Pool are the same | Object Pool: N pre-created objects lent exclusively one at a time; state reset on return. Flyweight: one object shared SIMULTANEOUSLY by many; immutable shared state |
| Integer cache is just an optimization, not a pattern | Integer.valueOf(-128..127) IS Flyweight: a factory (valueOf) returns shared instances from a cache (the flyweight factory) |

---

### 🚨 Failure Modes & Diagnosis

**Mutable Intrinsic State - Shared Corruption**

**Symptom:**
In a game with 10,000 monsters, calling `goblinType.setColor(RED)`
(trying to make one goblin red) makes ALL goblins red.
The change propagates to every monster sharing the goblin
flyweight.

**Root Cause:**
The flyweight's intrinsic state is mutable. A client
mutated shared state believing it was changing only their
instance.

**Diagnostic Signal:**
Any setter method on a flyweight class is a red flag.
Ask: "Is this state intrinsic (shared) or extrinsic (per
instance)?" If intrinsic: mutation must be prevented.

**Fix:**
```java
// BAD: mutable flyweight
class MonsterType {
    private Color color; // mutable!
    public void setColor(Color c) { this.color = c; } // WRONG
}

// GOOD: immutable flyweight; color is extrinsic
final class MonsterType {
    private final String name;
    private final byte[] spriteData; // intrinsic, immutable
    // No color - that's extrinsic

    void render(int x, int y, Color color) { // extrinsic param
        // render spriteData at (x,y) tinted with color
    }
}
```

**Prevention:**
All fields in flyweight classes must be `final`. No setters.
Enforce at code review: flyweight classes fail review if
any field is non-final.

---

**FlyweightFactory Memory Leak - Cache Grows Unbounded**

**Symptom:**
The FlyweightFactory's cache grows continuously. After
24 hours of operation, the factory cache holds millions
of entries and causes OutOfMemoryError. Flyweight was
supposed to reduce memory, not cause OOM.

**Root Cause:**
The flyweight key space is not bounded. Keys include
dynamic data (e.g., a user ID) that is effectively
unbounded. The factory caches an entry per user, not
per unique intrinsic type.

**Diagnostic Signal:**
Monitor `factory.cache.size()` over time. If growing
continuously: the key space is not bounded.

**Fix:**
Review the key design. Flyweight keys should cover only
TRULY REPEATING patterns (character + font + size; block
type; monster type). If user-specific data is in the key:
it is NOT intrinsic state - it is extrinsic state that
should be in the client, not the key.

For caches that must support a large but bounded key
space: use WeakReference values or a bounded LRU cache
(Guava Cache) with eviction.

**Prevention:**
Estimate the maximum unique key count before implementing
a flyweight factory. If max keys > 10,000: consider whether
Flyweight is appropriate or whether a bounded cache with
eviction is needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object Pool` - related pattern; understanding Pool first
  makes the Pool vs Flyweight distinction clear
- `Prototype` - another creational pattern for many similar
  objects; compare to Flyweight's sharing approach

**Builds On This (learn these next):**
- `Patterns in Distributed Systems` - Flyweight applied
  to distributed caches and shared configuration objects

**Alternatives / Comparisons:**
- `Object Pool` - Pool: exclusive temporary use, mutable,
  returned when done. Flyweight: simultaneous shared use,
  immutable, never "returned"
- `Singleton` - one instance for lifecycle uniqueness;
  Flyweight: one instance per key for memory efficiency

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Share common (intrinsic) state across    │
│              │ many objects; each provides own extrinsic│
├──────────────┼──────────────────────────────────────────┤
│ KEY SPLIT    │ Intrinsic = same for all sharing objects │
│              │ Extrinsic = different per use context    │
├──────────────┼──────────────────────────────────────────┤
│ REQUIREMENT  │ Intrinsic state MUST be immutable -      │
│              │ shared by multiple concurrent clients    │
├──────────────┼──────────────────────────────────────────┤
│ FACTORY RULE │ FlyweightFactory returns same instance   │
│              │ (== identity) for same key               │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Mutable intrinsic state → mutation       │
│              │ corrupts ALL objects sharing the flyweigh│
├──────────────┼──────────────────────────────────────────┤
│ JAVA EXAMPLE │ Integer.valueOf(-128..127), String pool, │
│              │ Enum constants = built-in flyweights     │
├──────────────┼──────────────────────────────────────────┤
│ VS POOL      │ Pool: exclusive, mutable, returned       │
│              │ Flyweight: shared, immutable, never retur│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Proxy → Chain of Responsibility → Observe│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Intrinsic state is SHARED and must be IMMUTABLE; extrinsic
   state is per-instance and passed as parameters - this
   split is the entire pattern
2. `Integer.valueOf(127)` == `Integer.valueOf(127)` is true
   (same object); `Integer.valueOf(128)` == `Integer.valueOf(128)`
   is false (outside JVM Flyweight cache range) - this is
   the JVM's Flyweight in action
3. Flyweight and Object Pool look similar but are opposite:
   Pool = exclusive use, mutable; Flyweight = shared use,
   immutable

**Interview one-liner:**
"Flyweight shares immutable common state between many objects
to reduce memory - by splitting intrinsic state (stored once
in the flyweight, shared by all) from extrinsic state (per-
instance, passed as parameters). Java's Integer.valueOf(),
String pool, and Enum constants are built-in JVM flyweights.
The key requirement: intrinsic state must be immutable because
multiple clients share the same object."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When objects have large amounts of common data and vary
only in small unique portions, sharing the common portion
transforms memory complexity from O(N x object size) to
O(unique types x object size + N x extrinsic size). This
is the only pattern that can reduce memory by orders of
magnitude for large object populations.

**Where else this pattern appears:**
- **JVM Constant Pool** - string literals, class literals,
  numeric constants in bytecode are shared flyweights;
  `ldc "hello"` always returns the same String instance
- **CSS class-based styling** - instead of inline styles
  per element (O(N)), CSS classes are shared flyweights
  applied to many elements; changing a CSS class changes
  all elements sharing it
- **Particle systems** - game engines render millions of
  particles; each particle type (fire, smoke, spark)
  is a Flyweight; each particle instance stores only
  position, velocity, age (extrinsic)

**Industry applications:**
- **Netty's ByteBufAllocator** - PooledByteBufAllocator
  maintains a pool of pre-allocated direct memory slabs;
  each ByteBuf allocation is a Flyweight over the slab
  with only the slice offsets as extrinsic state
- **RDBMS buffer pool** - database pages are flyweights:
  one page object per disk page, shared by all queries
  reading that page, with per-query extrinsic state
  (cursor position, lock type)

---

### 💡 The Surprising Truth

Java's `Boolean.TRUE` and `Boolean.FALSE` are Flyweights
that predate the formal pattern definition. `Boolean.valueOf(true)`
always returns `Boolean.TRUE` (a static final singleton
for each boolean value) - there is no way to create a
second `Boolean` that is `true`. Java autoboxing wraps
primitive `boolean` to `Boolean` via `Boolean.valueOf()`,
ensuring the SAME object is used every time. With billions
of boolean operations in a typical JVM session, not
allocating new Boolean objects is a meaningful memory
optimization. Similarly: `Byte.valueOf()`, `Short.valueOf()`,
`Character.valueOf(0..127)` all cache their full value
ranges. The JVM runtime uses Flyweight pervasively for
primitive wrapper types - because the designers understood
that these values repeat billions of times in typical
programs.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Given a game engine with 1M identical enemy
   sprites, calculate the memory savings from applying
   Flyweight: compute N × object_size without Flyweight
   vs (unique_types × intrinsic_size + N × extrinsic_size)
   with Flyweight
2. [CLASSIFY] Given a `Character` class with fields (char,
   font, size, color, x, y, boldness), correctly classify
   each field as intrinsic or extrinsic for a Flyweight
   design - and justify each classification
3. [BUILD] Implement a `TreeTypeFlyweight` factory for a
   forest simulation: intrinsic = species, bark texture,
   leaf texture; extrinsic = x, y, z, age, health
4. [DIAGNOSE] Given a Flyweight implementation where
   `flyweight.setStyle(BOLD)` changes ALL instances to
   bold, identify the mutable intrinsic state bug and
   implement the fix
5. [COMPARE] Explain why `Integer.valueOf(127) == Integer
   .valueOf(127)` is `true` but `Integer.valueOf(128) ==
   Integer.valueOf(128)` is `false`, connecting this to
   the Flyweight pattern

---

### 🧠 Think About This Before We Continue

**Q1.** Java's String pool is a Flyweight. But Strings in
Java are immutable anyway - wouldn't they be safe to share
even WITHOUT the Flyweight pattern (just without the memory
savings)? What is the additional benefit of the String pool
beyond memory savings?

*Hint: Memory is the main benefit. Additional: string
equality by identity (`==`) becomes safe for pooled strings
(though `equals()` should still be used for correctness).
String interning enables identity-based switch statements
and hash map lookups to be faster (identity comparison
is faster than content comparison for large strings).
The pool also reduces GC pressure: fewer objects = fewer
garbage collection cycles.*

**Q2.** The FlyweightFactory's Map is a memory management
concern: if flyweight instances are never evicted, the
map grows with every new unique key. Design a FlyweightFactory
that uses `WeakReference<ConcreteFlyweight>` as the map
value, so flyweights are garbage collected when no clients
hold strong references. What happens when a previously
collected flyweight is requested again?

*Hint: Map<Key, WeakReference<Flyweight>>. getFlyweight(key):
(1) look up WeakReference; (2) if null or WeakReference.get()
returns null: create new flyweight, store new WeakReference.
(3) else: return the existing flyweight. When a flyweight
is collected: the WeakReference holds null; the next
getFlyweight() call creates it again. This is correct:
it means no clients hold the flyweight, so reconstructing
it fresh is safe. Cost: occasional re-creation. Benefit:
memory bounded by live references, not total unique keys.*

**Q3.** A team uses Flyweight for a rule evaluation engine:
1,000 rules, each with a complex compiled predicate tree
(intrinsic) and a per-evaluation context (extrinsic).
After 10 minutes of operation, memory usage grows
continuously. Profiling shows: the FlyweightFactory
cache is stable (1,000 entries), but there are millions
of `EvaluationContext` objects being created and retained.
Is the Flyweight pattern causing the memory leak?

*Hint: No - the Flyweight is working correctly. The EvaluationContext
is the EXTRINSIC state. If clients create a new context
per evaluation but retain the context objects (e.g., store
in a list for auditing), the contexts accumulate. The
Flyweight pattern governs the intrinsic flyweight objects;
extrinsic state lifecycle is the CLIENT's responsibility.
The leak is in client code: storing contexts unnecessarily.
Flyweight reduces intrinsic state overhead; it does not
manage extrinsic state.*

---

### 🎯 Interview Deep-Dive

**Q1: Explain the intrinsic/extrinsic state split in
the Flyweight pattern with a concrete example.**

*Why they ask:* The intrinsic/extrinsic split is the
entire pattern; tests whether the candidate actually
understands it vs just naming it.

*Strong answer includes:*
- Intrinsic: state stored in the flyweight; same for all
  objects sharing this flyweight; must be IMMUTABLE;
  never changes after flyweight creation
- Extrinsic: state NOT stored in the flyweight; unique
  per use context; passed as parameters to flyweight
  methods by the client
- Example: chess piece type (rook, bishop, pawn) as
  flyweight. Intrinsic: piece rules, visual rendering
  data (same for all rooks). Extrinsic: board position,
  owner color (different for each piece on the board).
  32 piece instances; 12 flyweight type objects.
- The test: "Would modifying this field in the flyweight
  corrupt OTHER objects sharing the same flyweight?" If yes:
  it must be extrinsic (not stored in flyweight).

**Q2: Why does `Integer.valueOf(127) == Integer.valueOf(127)`
return `true`, but `Integer.valueOf(128) == Integer.valueOf(128)`
return `false`?**

*Why they ask:* Tests deep Java knowledge and Flyweight
recognition in standard library.

*Strong answer includes:*
- JLS (Java Language Specification) requires JVM to cache
  Integer instances for values -128 to 127
- `Integer.valueOf()` is the FlyweightFactory: it returns
  cached instances for the guaranteed range
- For 127: `valueOf` returns the same cached `Integer`
  object - identity comparison (`==`) is true
- For 128: `valueOf` creates a new `Integer` object each
  call - identity comparison is false
- This is Flyweight: the cache maps int values to Integer
  instances; `valueOf` is the factory method; the cached
  instances are flyweights
- Practical implication: NEVER use `==` to compare Integer
  objects; always use `.equals()` because the Flyweight
  range is an implementation detail

**Q3: How would you decide between Flyweight and Object
Pool for objects that are expensive to create?**

*Why they ask:* Tests ability to distinguish two
memory-optimization patterns that appear similar.

*Strong answer includes:*
- Key question: "Can the object be shared by MULTIPLE
  concurrent clients simultaneously?"
  - YES: Flyweight (shared, immutable intrinsic state)
  - NO: Object Pool (exclusive use, one borrower at a time)
- Flyweight: intrinsic state is immutable; no "return to
  pool" needed; many clients use the same flyweight at once
- Object Pool: objects are stateful (mutable between uses);
  one borrower at a time; must be reset on return
- Database connections: stateful (mid-transaction state,
  session variables) → Object Pool
- Character glyph data: immutable rendering data, shared
  by all characters of same font/size → Flyweight
- Thread objects: stateful (stack, thread-local variables)
  → Object Pool (thread pool)

