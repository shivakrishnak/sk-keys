---
layout: default
title: "Flyweight Pattern"
parent: "Design Patterns"
nav_order: 776
permalink: /design-patterns/flyweight-pattern/
number: "776"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Prototype Pattern, Immutable Objects"
used_by: "Text rendering, Game entities, String interning, Icon libraries"
tags: #advanced, #design-patterns, #structural, #oop, #memory-optimization, #caching
---

# 776 — Flyweight Pattern

`#advanced` `#design-patterns` `#structural` `#oop` `#memory-optimization` `#caching`

⚡ TL;DR — **Flyweight** reduces memory by sharing common state among many fine-grained objects — separating **intrinsic state** (shared, immutable, stored in flyweight) from **extrinsic state** (unique per context, passed in at runtime), enabling millions of logical objects while only storing a handful of actual objects.

| #776            | Category: Design Patterns                                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Prototype Pattern, Immutable Objects |                 |
| **Used by:**    | Text rendering, Game entities, String interning, Icon libraries   |                 |

---

### 📘 Textbook Definition

**Flyweight** (GoF, 1994): a structural design pattern that uses sharing to efficiently support large numbers of fine-grained objects. A flyweight is a shared object that can be used in multiple contexts simultaneously. The flyweight acts as an independent object in each context — it's indistinguishable from a non-shared object. Key concept: separate shared state (intrinsic) from context-dependent state (extrinsic). Intrinsic state: stored in the flyweight, shared, independent of flyweight's context, typically immutable. Extrinsic state: varies with context, provided by the client at call time, not stored in flyweight. GoF intent: "Use sharing to efficiently support large numbers of fine-grained objects." Flyweight is often implemented with a factory/cache that returns existing instances.

---

### 🟢 Simple Definition (Easy)

A forest of 1,000,000 trees in a game. Each tree type (Oak, Pine, Birch) has a mesh and texture — 50MB each. 1 million Oak trees × 50MB = 50 TB. UNWORKABLE. Flyweight: store ONE OakTree flyweight with the mesh and texture (intrinsic state). Each actual tree in the world stores only: which flyweight (OakTree), and its position/scale/rotation (extrinsic state). Memory: 3 flyweights × 50MB = 150MB + 1M × small position records ≈ manageable.

---

### 🔵 Simple Definition (Elaborated)

Java `String` interning is Flyweight. `String.intern()` returns the shared canonical instance from the string pool. All string literals `"hello"` refer to the same object. Character rendering in a word processor: each character type (glyph for 'a', 'b', 'c' in font "Arial 12pt") is a flyweight — stores the glyph image, metrics, kerning. Extrinsic: position on page (row, column). 10,000 'e' characters in a document → one `GlyphE` flyweight + 10,000 position records.

---

### 🔩 First Principles Explanation

**Intrinsic vs. extrinsic state — the architectural division:**

```
FLYWEIGHT STRUCTURE:

  // FLYWEIGHT (intrinsic state — shared, immutable):
  class TreeType {
      private final String name;           // "Oak", "Pine"
      private final String color;          // "#3A5A40"
      private final byte[] texture;        // 50MB mesh data — stored ONCE

      TreeType(String name, String color, byte[] texture) {
          this.name    = name;
          this.color   = color;
          this.texture = texture;   // immutable — safe to share
      }

      // Extrinsic state (position) passed in at draw time:
      void draw(Canvas canvas, int x, int y, double scale) {
          canvas.drawImage(texture, x, y, scale);  // uses shared texture + per-tree position
      }
  }

  // FLYWEIGHT FACTORY (cache — returns existing instances):
  class TreeTypeFactory {
      private static final Map<String, TreeType> types = new HashMap<>();

      static TreeType getTreeType(String name, String color, byte[] texture) {
          String key = name + "_" + color;
          return types.computeIfAbsent(key, k -> new TreeType(name, color, texture));
          // computeIfAbsent: only creates new if not cached.
      }
  }

  // CONTEXT (stores extrinsic state + reference to flyweight):
  class Tree {
      private final int x;               // extrinsic — unique per tree
      private final int y;               // extrinsic
      private final double scale;        // extrinsic
      private final TreeType type;       // flyweight reference (shared)

      Tree(int x, int y, double scale, TreeType type) { ... }

      void draw(Canvas canvas) {
          type.draw(canvas, x, y, scale);  // pass extrinsic to flyweight
      }
  }

  // FOREST:
  class Forest {
      private final List<Tree> trees = new ArrayList<>();

      void plantTree(int x, int y, double scale, String name, String color, byte[] texture) {
          TreeType type = TreeTypeFactory.getTreeType(name, color, texture);  // cached!
          trees.add(new Tree(x, y, scale, type));  // Tree is small — just extrinsic + ref
      }

      void render(Canvas canvas) {
          trees.forEach(t -> t.draw(canvas));
      }
  }

  // Memory analysis:
  // 1,000,000 trees: 3 TreeType flyweights × 50MB = 150MB (mesh/texture data)
  //                + 1,000,000 Tree contexts × ~20 bytes = ~20MB (position/scale/type-ref)
  // TOTAL: ~170MB vs naive approach (1M × 50MB = 50TB)

FLYWEIGHT IN JAVA STANDARD LIBRARY:

  // 1. String Pool (String interning):
  String a = "hello";
  String b = "hello";
  a == b;   // true — same instance from string constant pool

  // String.intern():
  String c = new String("hello");   // forces new object on heap
  String d = c.intern();            // returns pooled instance
  d == a;   // true

  // 2. Integer cache (-128 to 127):
  Integer x = 100;  Integer y = 100;  x == y;   // true — cached
  Integer p = 200;  Integer q = 200;  p == q;   // false — not cached (> 127)

  // 3. Boolean.TRUE / Boolean.FALSE — singleton flyweights

  // 4. java.awt.Font: shared font metrics objects

FLYWEIGHT vs. PROTOTYPE vs. SINGLETON:

  SINGLETON:   One global instance. Represents a single entity (config, logger).
               Not about memory — about one-instance constraint.

  PROTOTYPE:   Copies a template. Each copy is INDEPENDENT — can be modified.

  FLYWEIGHT:   Shared instances of fine-grained objects. Intrinsic state shared (immutable).
               Extrinsic state NOT stored in flyweight — passed at call time.
               About MEMORY EFFICIENCY with many small objects.

THREAD SAFETY:

  Flyweight objects are shared across many contexts (often many threads).
  They MUST be immutable or thread-safe.
  If intrinsic state is mutable, concurrent modification = data corruption.

  // SAFE: TreeType.texture is final byte[] — immutable reference (though bytes mutable)
  // Better: use genuinely immutable types for intrinsic state.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Flyweight:

- 1M trees × 50MB texture = 50TB memory (impossible)
- Each character in a word processor = full glyph object (millions of objects, huge heap)

WITH Flyweight:
→ 3 tree type flyweights × 50MB + 1M small context objects ≈ 170MB (manageable)
→ 1 glyph per character type × 26 characters + 1M position records (tiny)

---

### 🧠 Mental Model / Analogy

> A library with books. The library has ONE physical copy of "War and Peace." Many borrowers have a library card referencing "War and Peace" (flyweight reference) plus their own bookmark/annotation notes (extrinsic: which page they're on, their notes). The library doesn't print a copy per reader. Each reader has the same shared book + their own reading state. The book = flyweight (shared, intrinsic content). Bookmark position = extrinsic state (per reader, not in the book).

"ONE physical book" = flyweight object (intrinsic state: the text)
"Many borrowers" = many contexts using the same flyweight
"Library card + bookmark" = context object (flyweight reference + extrinsic state)
"Page number (unique per reader)" = extrinsic state (not stored in flyweight)
"Library catalog/factory" = Flyweight factory (returns same book for same ISBN)

---

### ⚙️ How It Works (Mechanism)

```
FLYWEIGHT PATTERN:

  Client → FlyweightFactory.get(key)
           → if cached: return existing flyweight
           → if not: create, cache, return

  Client stores: flyweight reference + extrinsic state (in Context object)

  Client → context.operation(extrinsicState)
           → flyweight.operation(extrinsicState)   // passes extrinsic
           → uses intrinsic + extrinsic to do work
```

---

### 🔄 How It Connects (Mini-Map)

```
Need millions of similar objects → huge memory cost
        │
        ▼
Flyweight Pattern ◄──── (you are here)
(share intrinsic state; pass extrinsic at runtime)
        │
        ├── String Pool: Java's built-in Flyweight for strings
        ├── Composite: large Composite trees often use Flyweight for shared leaf nodes
        ├── Singleton: one instance (not for performance); Flyweight: many shared instances by type
        └── Object Pool: pool and reuse mutable objects; Flyweight: share immutable objects
```

---

### 💻 Code Example

```java
// Particle system: each particle type shares a flyweight:

// FLYWEIGHT — shared intrinsic state:
record ParticleType(String name, Color color, BufferedImage texture, double baseSize) {
    // record fields are final (immutable) — safe to share across threads
}

// FLYWEIGHT FACTORY:
class ParticleTypeFactory {
    private static final Map<String, ParticleType> cache = new ConcurrentHashMap<>();

    static ParticleType get(String name, Color color, BufferedImage texture, double size) {
        return cache.computeIfAbsent(name,
            k -> new ParticleType(name, color, texture, size));
    }
}

// CONTEXT — stores extrinsic state + flyweight reference:
class Particle {
    private double x, y;         // extrinsic — unique per particle
    private double velocityX, velocityY;  // extrinsic
    private double scale;        // extrinsic
    private final ParticleType type;      // flyweight — shared

    Particle(double x, double y, double vx, double vy, ParticleType type) {
        this.x = x; this.y = y; this.velocityX = vx; this.velocityY = vy;
        this.scale = 1.0;
        this.type = type;
    }

    void update() { x += velocityX; y += velocityY; scale *= 0.99; }

    void render(Graphics2D g) {
        // type.texture is SHARED — not copied:
        g.drawImage(type.texture(), (int)x, (int)y, (int)(type.baseSize() * scale), null);
    }
}

// USAGE:
ParticleType fire  = ParticleTypeFactory.get("fire",  Color.ORANGE, fireTexture,  8.0);
ParticleType smoke = ParticleTypeFactory.get("smoke", Color.GRAY,   smokeTexture, 12.0);

// 100,000 fire particles — all share ONE ParticleType (one texture in memory):
List<Particle> particles = new ArrayList<>();
for (int i = 0; i < 100_000; i++) {
    particles.add(new Particle(random(), random(), random(), random(), fire));
}
```

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Flyweight is the same as caching           | Caching stores previously computed results to avoid recomputation. Flyweight shares object instances to reduce memory. A Flyweight factory uses a cache-like structure internally, but the goal is structural sharing of object state, not computation memoization. The shared flyweight objects are not "cached results" — they are the canonical shared objects. |
| All state in a flyweight must be immutable | Intrinsic state MUST be immutable (shared across contexts/threads). Extrinsic state is NOT stored in the flyweight at all — it's passed at call time. The flyweight object itself should be immutable for thread safety.                                                                                                                                           |
| Flyweight always requires a factory        | In theory, clients could manage flyweight instances directly. In practice, a Flyweight Factory is almost always used — it encapsulates the caching/sharing logic, ensuring clients get the shared instance rather than creating new ones. Without a factory, clients might accidentally create new instances instead of reusing shared ones.                       |

---

### 🔥 Pitfalls in Production

**Accidentally storing mutable extrinsic state in the flyweight:**

```java
// ANTI-PATTERN: Flyweight stores mutable extrinsic state:
class TreeType {
    String name;
    byte[] texture;

    // BAD: position is EXTRINSIC state — must NOT be stored in flyweight:
    int x, y;  // ← shared object now stores per-tree position!

    void draw(Canvas c) {
        c.drawImage(texture, x, y);  // x, y are "this tree's position" — but shared!
    }
}

// Tree A uses this flyweight and sets x=100, y=200.
// Tree B uses same flyweight and sets x=300, y=400.
// Now Tree A renders at (300, 400) — wrong! Data race if multithreaded.

// FIX: Flyweight stores ONLY intrinsic state (immutable, shared).
//      Extrinsic state passed at call time:
class TreeType {
    final String name;
    final byte[] texture;

    // NO position fields! Extrinsic state is a PARAMETER:
    void draw(Canvas c, int x, int y) {   // ← extrinsic passed as parameter
        c.drawImage(texture, x, y);
    }
}
// Each tree (context) stores its own x, y. Flyweight is stateless re: position.
```

---

### 🔗 Related Keywords

- `String Interning` — Java's built-in Flyweight for String objects
- `Object Pool` — reuses mutable objects (vs Flyweight: shares immutable intrinsic state)
- `Immutable Objects` — Flyweight intrinsic state must be immutable for thread safety
- `Composite Pattern` — large composite trees benefit from Flyweight for shared leaf nodes
- `Integer Cache` — Java's built-in Flyweight for Integer values -128 to 127

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Share intrinsic (immutable) state across  │
│              │ many objects. Pass extrinsic (per-context)│
│              │ state at call time. N+M not N×M objects.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Millions of similar objects; memory is    │
│              │ the bottleneck; objects can be split into │
│              │ shared intrinsic + context extrinsic      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Few object instances (sharing overhead    │
│              │ exceeds savings); shared state is hard   │
│              │ to separate from context state            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library: one copy of the book, many      │
│              │  readers — each tracks their own page,   │
│              │  but the text is shared."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Object Pool Pattern → String Interning →  │
│              │ Immutable Objects → Composite Pattern     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `String.intern()` places strings in the string pool — a Flyweight factory. However, the string pool in older JVMs was in the PermGen (fixed size → `OutOfMemoryError: PermGen space`). In Java 8+, the string pool moved to the heap. When is `intern()` worth using, and when is it counterproductive? What modern alternatives (e.g., using `Map<String, String>` as a manual intern cache) exist, and when should you use them vs. JVM's string pool?

**Q2.** In a word processor with millions of characters, each character position needs: which glyph (flyweight — 'a' in Arial 12pt), row index, column index, foreground color, background color, bold/italic flags. If color and bold/italic vary per character (extrinsic state), how do you decide what goes in the flyweight vs. what stays extrinsic? If 90% of characters use the same color (black) and style (regular), would you include those in the flyweight to avoid passing them every time, even though technically they can vary?
