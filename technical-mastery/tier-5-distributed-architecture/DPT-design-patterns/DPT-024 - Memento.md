---
id: DPT-024
title: Memento
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-020
used_by: DPT-064
related: DPT-020, DPT-026
tags:
  - pattern
  - behavioral
  - advanced
  - undo
  - state-snapshot
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/design-patterns/memento/
---

⚡ TL;DR - Memento captures and externalizes an object's
internal state without violating encapsulation, enabling
state restoration (undo/rollback) while preserving the
boundary between originator and caretaker.

| #24 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-020 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-020, DPT-026 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A game needs checkpoints: before a difficult boss fight,
save the player's position, health, inventory, skills,
and quest state. One approach: make all these fields
`public` so an external saver can copy them. Another
approach: write a `save()` method that copies state to
a raw `Map<String, Object>`. Either way: the character's
internal state is exposed to the saving mechanism.
The saver must know the character's implementation details
to correctly save and restore.

**THE BREAKING POINT:**
Adding a new character field (stamina): update the public
API, update the saver, update the restorer, update all
tests that read character state. The internal state
representation is leaked to external savers.

**THE INVENTION MOMENT:**
Memento: the Character (Originator) creates a `CharacterMemento`
snapshot - an opaque object containing its state. The
game saver (Caretaker) stores mementos but CANNOT READ
them; it only holds them. When restoring, the Character
receives its own memento and restores from it. Encapsulation
is preserved: the saver has no idea what is inside the
memento.

**EVOLUTION:**
Java's `Serializable` is a Memento mechanism: serializing
an object captures its state to bytes; deserializing
restores it. JVM's JVMTI Heap Dumps are mementos of the
entire JVM state. Database transaction rollback stores
undo log entries (mementos of changed pages). Spring
WebFlux's subscription state can be snapshotted similarly.

---

### 📘 Textbook Definition

The **Memento** pattern is a Behavioral design pattern
that captures and externalizes an object's internal state
so that the object can be restored to this state later,
without violating encapsulation. Three roles: the Originator
(creates and restores from mementos), the Memento (the
state snapshot - opaque to outsiders), and the Caretaker
(holds mementos but cannot inspect them). The key invariant:
only the Originator can write to or read from a Memento.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Memento is a "save-state capsule" - the object packages
its own state; an external holder stores the capsule but
cannot read it; the object can later restore from it.

**One analogy:**
> A sealed envelope (Memento). You write your own letter
> (Originator creates state). You seal the envelope
> (Memento is opaque). A friend (Caretaker) holds the
> envelope but cannot open it. Later, you take back your
> envelope, open it, and restore what you wrote. The friend
> never knows what was in the letter.

**One insight:**
The "encapsulation preserved" aspect is what distinguishes
Memento from simply exposing state as a public DTO.
The Caretaker holds the state but is intentionally prevented
from reading or modifying it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The Originator creates the Memento from its private
   state; only the Originator knows how to create or
   read a Memento.
2. The Caretaker stores and retrieves Mementos but
   CANNOT access Memento's contents.
3. Restoring from a Memento sets the Originator's state
   to exactly what it was when the Memento was created.

**DERIVED DESIGN:**
Three participants:
- **Originator**: the object whose state is saved.
  Creates mementos; restores from mementos.
- **Memento**: the state snapshot. Wide interface to
  Originator (can read/write state). Narrow interface
  to Caretaker (no access to state).
- **Caretaker**: manages the lifecycle of mementos (stores,
  retrieves). Cannot access or modify Memento contents.

**JAVA IMPLEMENTATION CHALLENGE:**
Java has no "friend classes" to enforce Caretaker cannot
read Memento. Common approaches:
- Memento is a package-private inner class of Originator -
  only Originator can read it
- Memento implements a narrow public interface; internal
  state is accessible only to Originator via its full type

**TRADE-OFFS:**

**Gain:** Undo without exposing implementation. Originator
controls what constitutes its "state." Caretaker has no
coupling to Originator's implementation.

**Cost:** Memory: storing many mementos consumes memory
proportional to (memento size × number of snapshots).
For large-state objects, snapshots are expensive.
Memento captures state at a POINT IN TIME - referenced
objects may change independently.

---

### 🧪 Thought Experiment

**SETUP:**
A database transaction: before updating 5 rows, save their
current values. If the transaction fails, restore all
5 rows to their saved values.

**WITHOUT MEMENTO:**
Save state: copy each row to a separate variable (6 lines).
Restore: assign each variable back (6 lines). Each new
field in the row: update both save and restore code.

**WITH MEMENTO:**
`row.createMemento()` captures the row's state.
Caretaker (transaction manager) stores 5 mementos.
On rollback: `row.restore(memento)` for each row.
Adding a new row field: `createMemento()` and `restore()`
automatically capture/restore it (if implemented correctly
inside Row). The transaction manager's rollback code
is UNCHANGED regardless of schema changes.

---

### 🧠 Mental Model / Analogy

> Memento is GAME SAVE STATE. Before a hard boss fight,
> press "Save." The game engine (Originator) writes your
> entire character state to a save file (Memento). The
> save file manager (Caretaker) stores the file. If you
> die, the game engine reads the save file back and
> restores your character. The save file manager
> does not know what's in the file - it just stores and
> returns it.

- "Game engine" = Originator
- "Save file" = Memento
- "Save file manager" = Caretaker
- "Save game" = createMemento()
- "Load game" = restore(memento)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Memento is the "save game" button. The object saves its
own state into a capsule; an external holder stores the
capsule without being able to read it; the object can
later restore from the capsule.

**Level 2 - How to use it (junior developer):**
Create a `Memento` inner class inside the Originator.
Give it private constructor and fields; only the Originator
can create/read it. The `createMemento()` method creates
a snapshot. The `restoreFromMemento(Memento m)` method
restores. The Caretaker receives mementos from Originator,
stores them, and returns them when requested.

**Level 3 - How it works (mid-level engineer):**
Java's `Serializable` is Memento in practice. `ObjectOutputStream
.writeObject(obj)` creates a byte-array memento of `obj`.
`ObjectInputStream.readObject()` restores from the memento.
The serialized bytes are opaque to anything that is not
the serialization framework. Spring's `HttpSession`
stores the session as a Memento: the session contains
arbitrary objects (state); when distributed sessions are
used (Spring Session + Redis), the session is serialized
(memento created) and stored in Redis (Caretaker). On
the next request, the session is deserialized and restored.

**Level 4 - Why it was designed this way (senior/staff):**
Memento is the pattern that makes the Originator's
implementation details private to the undo/restore system.
Without Memento, implementing undo requires either: (1)
exposing ALL state as public (breaks encapsulation), or
(2) a tight coupling between the saver and the object's
internal structure (saver must know all fields). Memento
gives Originator full control over what "its state" means:
it can choose to save derived fields, skip transient
fields, or compact the state representation - without
any external knowledge.

**Level 5 - Mastery (distinguished engineer):**
Database MVCC (Multi-Version Concurrency Control) is
the most important Memento application in production
systems. In PostgreSQL: when a row is updated, the old
version is kept as a "tuple" (Memento) in the heap.
Transactions reading at an earlier snapshot see the old
tuple (Caretaker retrieves the correct Memento). When
the transaction commits, the old tuple becomes a dead
tuple (Memento no longer needed). `VACUUM` reclaims
dead tuples. MVCC enables non-blocking reads at the cost
of storing multiple Mementos per row. The storage
overhead of Memento (old row versions) is the central
concern in high-write PostgreSQL systems.

---

### ⚙️ How It Works (Mechanism)

```
Memento Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ Originator (TextEditor)                                 │
│ - content: String     ← internal state                  │
│ + createMemento(): EditorMemento                        │
│     return new EditorMemento(content)  ← snapshot now   │
│ + restore(EditorMemento m): void                        │
│     this.content = m.getContent() ← only Originator can│
│                                                         │
│ EditorMemento (opaque to outsiders)                     │
│ - content: String       ← package-private or private    │
│ + EditorMemento(String) ← package-private constructor   │
│ + getContent(): String  ← package-private method        │
│ // Caretaker CANNOT call getContent()                   │
│ // Only TextEditor (same package) can                   │
│                                                         │
│ Caretaker (EditorHistory)                               │
│ - mementos: Deque<EditorMemento>                        │
│ + save(TextEditor e):                                   │
│     mementos.push(e.createMemento()) ← call Originator  │
│ + undo(TextEditor e):                                   │
│     e.restore(mementos.pop()) ← pass Memento back       │
│     // Caretaker cannot read the Memento contents       │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Text editor: content = "Hello"

User types " World": content becomes "Hello World"
History.save(editor): mementos = [Memento("Hello World")]

User types "!": content becomes "Hello World!"
History.save(editor): mementos = [Memento("Hello World!"),
                                   Memento("Hello World")]

User presses Ctrl+Z (undo):
History.undo(editor):
  memento = mementos.pop() → Memento("Hello World!")  ←
    wrong!
  Wait - we saved AFTER typing, so pop returns latest...
  
  Actually the correct pattern:
  save BEFORE each change:
  Before " World": save("Hello") → push Memento("Hello")
  After " World": content = "Hello World"
  Before "!": save("Hello World") → push Memento("Hello
    World")
  After "!": content = "Hello World!"
  
Undo: pop Memento("Hello World") → restore → content =
  "Hello World"
Undo: pop Memento("Hello") → restore → content = "Hello"
```

---

### 💻 Code Example

**Example - Text editor with undo via Memento:**

```java
// Originator: manages its own state; creates/restores mementos
class TextEditor {
    private String content = "";

    public void type(String text) {
        content += text;
    }

    public String getContent() {
        return content;
    }

    // Creates snapshot of current state
    public EditorMemento save() {
        return new EditorMemento(content);
    }

    // Restores from snapshot
    public void restore(EditorMemento memento) {
        this.content = memento.getContent();
    }

    // Memento: inner class - only TextEditor can access internals
    // Package-private makes getContent() inaccessible outside
    static class EditorMemento {
        private final String content; // captured state

        // Package-private: only accessible within same package
        EditorMemento(String content) {
            this.content = content;
        }

        // Package-private: Caretaker CANNOT call this
        String getContent() {
            return content;
        }
    }
}

// Caretaker: stores and returns mementos; cannot read them
class EditorHistory {
    private final Deque<TextEditor.EditorMemento> history
        = new ArrayDeque<>();

    // Save BEFORE a change
    public void save(TextEditor.EditorMemento memento) {
        history.push(memento);
    }

    public TextEditor.EditorMemento undo() {
        if (history.isEmpty())
            throw new IllegalStateException("Nothing to undo");
        return history.pop();
    }

    public boolean canUndo() {
        return !history.isEmpty();
    }
}

// Usage
TextEditor editor = new TextEditor();
EditorHistory history = new EditorHistory();

// Save before each change
history.save(editor.save()); // save ""
editor.type("Hello");
System.out.println(editor.getContent()); // Hello

history.save(editor.save()); // save "Hello"
editor.type(" World");
System.out.println(editor.getContent()); // Hello World

// Undo: restore to "Hello"
editor.restore(history.undo());
System.out.println(editor.getContent()); // Hello

// Undo: restore to ""
editor.restore(history.undo());
System.out.println(editor.getContent()); // (empty)
```

**How to test/verify correctness:**
Test that `save()` captures state correctly. Test `restore()`
returns to captured state exactly. Test multiple undo
levels. Test that the Caretaker CANNOT access Memento
state (compilation error if trying to call package-private
methods). Test edge case: undo when history is empty.

---

### ⚖️ Comparison Table

| Pattern | State storage | Who manages state | Encapsulation | Undo focus |
|---|---|---|---|---|
| **Memento** | External snapshot | Caretaker (opaque) | Preserved | Full state |
| Command | Delta in command | History stack | Preserved | Operation delta |
| Prototype | Full clone | Client | Exposed | Optional |
| Serialization | Byte array | Any system | Depends | Restore focus |

**Command vs Memento for undo:**
- Command: store what CHANGED (delta). Small memory, requires
  undo logic per command.
- Memento: store full state SNAPSHOT. Large memory, no
  undo logic per operation needed.
- Combination: periodic Memento snapshots + Commands between
  snapshots (best of both).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Memento and Command both enable undo, so they're similar | Different mechanisms: Command stores the DELTA (operation that was applied); Memento stores a FULL STATE SNAPSHOT. Command requires implementing undo() per operation; Memento requires no per-operation undo logic but uses more memory |
| The Caretaker can read Memento contents | The pattern's invariant: Caretaker CANNOT read Memento. In Java, this is enforced by making Memento an inner class with package-private accessors - only the Originator class can call them |
| Serialization is not Memento | Java Serialization IS the most common Memento implementation: serialize() captures the object's state (Memento creation); deserialize() restores it (Memento restoration). The byte array is the Memento; the object deserializer is the restoration mechanism |
| Memento is only for undo/redo | Memento applies anywhere an object needs to be restored to a previous state: database row version snapshots (MVCC), game save states, distributed transaction rollback, circuit breaker state checkpointing |

---

### 🚨 Failure Modes & Diagnosis

**Memory Exhaustion from Unbounded Memento History**

**Symptom:**
A text editor stores a Memento after every keystroke.
After 30 minutes of editing, the application uses 2GB
of memory storing thousands of full-document snapshots.

**Root Cause:**
Mementos for large objects accumulate without eviction.
Every snapshot is a full copy of the entire document.

**Diagnostic Signal:**
Heap dump shows thousands of EditorMemento instances
each holding a large string or byte array. Memory grows
linearly with the number of edits.

**Fix:**
Apply bounded undo history: keep only the last N mementos
(use a fixed-size Deque or LRU eviction).
Or: switch to Command-based undo (store only deltas)
for frequent small changes; save Mementos only at
significant checkpoints (every 50 changes or on save).

**Prevention:**
Set an explicit maximum history depth at design time.
For large objects, estimate: `max_undo_levels * avg_snapshot_size`
= acceptable memory budget. If budget exceeds available
memory, use Command-based undo for intermediate changes.

---

**Shallow Copy Memento Shares Mutable References**

**Symptom:**
After restoring from a Memento, the restored state still
reflects changes made after the snapshot was taken.
Undo restores the reference but not the object it pointed
to.

**Root Cause:**
The Memento captures a shallow copy of the Originator's
state. If the state includes references to mutable objects
(e.g., `List<Item>` in a shopping cart), the Memento
stores the reference, not a deep copy. Subsequent changes
to the List (adding/removing items) change the Memento's
captured state.

```java
// BAD: shallow copy - memento shares the list reference
class ShoppingCart {
    private List<Item> items; // mutable!

    CartMemento save() {
        return new CartMemento(items); // reference copy!
    }
}
// After save(), modifying 'items' also changes the memento
```

**Fix:**
```java
// GOOD: deep copy - memento has its own list
CartMemento save() {
    return new CartMemento(new ArrayList<>(items)); // copy list
}
// Or use unmodifiable wrapper + copy on restore
```

**Prevention:**
Memento creation must defensively copy all mutable state.
For complex objects: consider serialization-based snapshots
(serialize to bytes) which inherently do deep copy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Command` - DPT-020; understand delta-based undo before
  snapshot-based undo; both solve undo but with different
  trade-offs

**Builds On This (learn these next):**
- `State` - DPT-026; State pattern manages state transitions;
  Memento captures state at a point in time; they complement
  each other in state-machine undo systems

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Opaque state snapshot; Originator creates│
│              │ and restores; Caretaker stores but can't │
│              │ read the memento contents                │
├──────────────┼──────────────────────────────────────────┤
│ KEY PROPERTY │ Encapsulation preserved: Caretaker holds │
│              │ the snapshot but cannot inspect it       │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Java Serialization, game save states,    │
│              │ PostgreSQL MVCC row versions             │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Shallow copy → mutable state changes     │
│              │ affect "saved" snapshot; use deep copy   │
├──────────────┼──────────────────────────────────────────┤
│ VS COMMAND   │ Command: stores delta, requires undo()   │
│              │ Memento: stores full snapshot, no per-op │
│              │ undo logic; more memory intensive        │
├──────────────┼──────────────────────────────────────────┤
│ MEMORY RULE  │ Bound the history depth; large objects   │
│              │ + many snapshots = OOM risk              │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Observer → State → Strategy              │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Originator creates and restores its own Memento;
   Caretaker holds the Memento but CANNOT read it -
   encapsulation is the key invariant
2. Memento stores FULL STATE; Command stores DELTA -
   this is the core trade-off: Memento needs no per-operation
   undo logic but uses more memory
3. Shallow copy bug: if Memento contains references to
   mutable objects, changes after snapshotting affect the
   "saved" state - always deep copy mutable state

**Interview one-liner:**
"Memento captures an object's state as an opaque snapshot
without violating encapsulation - the Originator creates
and restores from mementos; the Caretaker stores them
without reading them. Java Serialization is the most common
Memento implementation. Key trade-off vs Command: Memento
captures full state (no per-operation undo logic needed,
but more memory); Command captures only the delta."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Describe the three roles (Originator, Memento,
   Caretaker) and why the Caretaker's inability to read
   the Memento is the pattern's defining invariant
2. [DISTINGUISH] Explain Command-based vs Memento-based
   undo with their respective memory and implementation
   trade-offs
3. [DIAGNOSE] Given a Memento implementation where restoring
   still shows changes made after the snapshot, identify
   the shallow copy bug and fix it with defensive copying
4. [IDENTIFY] Explain how Java Serialization and PostgreSQL
   MVCC are both Memento pattern implementations

