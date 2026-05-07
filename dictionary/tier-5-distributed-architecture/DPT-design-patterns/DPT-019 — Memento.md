---
layout: default
title: "Memento"
parent: "Design Patterns"
nav_order: 19
permalink: /design-patterns/memento/
number: "DPT-019"
category: Design Patterns
difficulty: ★★★
depends_on: Encapsulation, Object-Oriented Programming (OOP), Command, Immutability
used_by: Undo/Redo Systems, State Snapshots, Transaction Rollback, Game Save States
related: Command, Prototype, Iterator, State
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - bestpractice
---

# DPT-019 — Memento

⚡ TL;DR — Memento captures and externalises an object's internal state so it can be restored to that state later, without violating encapsulation.

| #784 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Encapsulation, Object-Oriented Programming (OOP), Command, Immutability | |
| **Used by:** | Undo/Redo Systems, State Snapshots, Transaction Rollback, Game Save States | |
| **Related:** | Command, Prototype, Iterator, State | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A text editor supports undo. The `Document` class holds the entire document state (content, formatting, cursor position, selection ranges). To implement undo naively, a `DocumentHistory` class stores `List<Document>` — full document copies. But `Document` has private fields that can't be set externally. To give `DocumentHistory` access, you must either: (1) expose all private fields via getters/setters (breaking encapsulation — anyone can now corrupt state), or (2) make `DocumentHistory` an inner class of `Document` (tight coupling), or (3) add an `exportState()` method that returns raw data (still breaks encapsulation — the raw data IS the private state).

**THE BREAKING POINT:**
Every approach to external state capture compromises encapsulation. If the `Document` exposes enough state for external parties to reconstruct it, that same access can be used to maliciously or accidentally corrupt it. The undo system needs to save and restore state — but that should not make the state permanently accessible to all callers.

**THE INVENTION MOMENT:**
This is exactly why the Memento pattern was created. The `Document` creates a `Memento` object — an opaque state container. Only `Document` knows how to interpret its own Memento (how to create it and how to restore from it). `DocumentHistory` stores Mementos but cannot read or modify state from them — it holds opaque objects. Encapsulation is preserved: the history system can save/restore state without ever seeing what the state contains.

---

### 📘 Textbook Definition

The **Memento** pattern is a behavioural design pattern that captures an object's internal state in a separate object (the Memento) so the originator can be restored to this state later, without revealing its implementation details. Three roles: the **Originator** (the object whose state is saved), the **Memento** (the snapshot of originator state), and the **Caretaker** (stores Mementos but cannot read them). The Memento provides a narrow interface to caretakers (opaque) and a wide interface to the originator (full access).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Take a snapshot of an object's private state that only the object knows how to read.

**One analogy:**
> A sealed envelope system at a notary. You write your will (your private state), seal it in an envelope (Memento), and hand it to the notary (Caretaker) for safe keeping. The notary can store the envelope, label it, and return it to you, but cannot read it. Only you can open it and use its contents.

**One insight:**
The Memento pattern separates the RIGHT TO HOLD a state snapshot from the RIGHT TO READ it. The Caretaker has the right to hold. Only the Originator has the right to read. This is a fine-grained access control mechanism built into the pattern's structure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An object's internal state must be capturable and restorable without exposing that state publicly.
2. The entity managing the history of states (Caretaker) must not be able to interpret the state.
3. The Originator must be able to restore itself to any previously captured state.

**DERIVED DESIGN:**
Given invariant 1+2: the Memento is a value object created by the Originator's private logic. In Java, this can be implemented as a public class with package-private or private content — only the Originator (in the same package) can create or read the Memento. Given invariant 3: the Originator's `restore(Memento m)` method extracts the state from the Memento and applies it to the internal fields.

The Memento can be: (1) an inner class of the Originator (Java access control blocks caretaker from reading inner class fields); (2) a package-private class in the Originator's package; (3) an immutable record with public fields if the state being stored is considered public domain (less strict variant).

**THE TRADE-OFFS:**
**Gain:** Encapsulation of state preserved; undo/redo without exposing internals; state rollback without coupling the history system to the originator's internals; Originator alone controls snapshot format.
**Cost:** Memory overhead — each Memento is a (potentially large) copy of state; deep object graphs require deep copy in Memento creation; serialisation cost for persistence of Mementos; if the Originator's state structure changes, stored Mementos may be incompatible.

---

### 🧪 Thought Experiment

**SETUP:**
A spreadsheet application has a `Spreadsheet` class with a 10,000-cell grid (each cell has value, formula, format). The user makes 20 changes and wants to undo all of them.

**WHAT HAPPENS WITHOUT MEMENTO:**
The undo system stores full `Spreadsheet` copies. Each copy is a deep clone of 10,000 cells. 20 undos = 20 copies in memory. If average cell data is 100 bytes, each copy is 1 MB; 20 undos = 20 MB just for undo history. Additionally, since `Spreadsheet.cells` is a private `Cell[][]`, the undo system must use reflection or expose the array — breaking encapsulation.

**WHAT HAPPENS WITH MEMENTO:**
`Spreadsheet` creates `SpreadsheetMemento` — which captures only the cells that changed since the last snapshot (delta encoding). Each delta Memento is 100× smaller than a full copy. The Caretaker (undo history) stores opaque `SpreadsheetMemento` objects with no access to cell data. On undo, `spreadsheet.restore(memento)` applies the delta in reverse. 20 undos use a fraction of the full-copy approach's memory.

**THE INSIGHT:**
Memento gives the Originator full control over what constitutes a "snapshot" — it can choose full copy, delta, or compressed representation. The Caretaker gets none of these choices. This control is what enables memory optimisation.

---

### 🧠 Mental Model / Analogy

> Memento is like a save-game file. The game (Originator) writes a save file (Memento) — only the game knows the file format and can decode it. The file system (Caretaker) stores the save files with names and timestamps but can't "cheat" from them because it doesn't understand the format. When you load the game, it reads its own save file and restores its state.

- "Game state" → Originator's internal fields
- "Save game file" → Memento object
- "The game writing saves" → `originator.save()` creating Memento
- "File system" → Caretaker storing Mementos
- "Loading the save" → `originator.restore(memento)`
- "File system can't cheat" → Caretaker can't read Memento contents

Where this analogy breaks down: a save file may be editable with a hex editor (breaking the opaque guarantee). In Java, this is analogous to using reflection to access private fields — Memento's encapsulation guarantee can be violated with reflection, but that requires explicit intent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Memento is a snapshot save system. The object that has state creates its own "backup copy" in a sealed box. Someone else (the undo system) holds the sealed box. When you need to go back, you give the box back to the original object. Only the original knows how to open and use the box.

**Level 2 — How to use it (junior developer):**
Implement `Originator`: add `save()` returning a `Memento` object (creates a snapshot of current state), and `restore(Memento m)` method (restores state from memento). Implement `Memento`: an immutable holder of the originator's state. In Java, make it a nested class in the Originator to leverage access control. Implement `Caretaker`: maintains a `Deque<Memento>` history; add `push(memento)` and `pop()` for undo.

**Level 3 — How it works (mid-level engineer):**
Java access control for Memento: declaring `Memento` as a nested class in `Originator` means `Memento`'s private fields are accessible to `Originator` (in Java, enclosing class can access nested class private members). External classes (Caretaker) can only hold a `Memento` reference — they cannot access its fields. This is clean encapsulation enforcement. Alternatively: package-private Memento fields + Originator+Memento in the same package, with Caretaker in a separate package. For persistence (save to disk), Memento must be serialisable — this exposes the serialised format externally, requiring versioning strategy for future Originator changes.

**Level 4 — Why it was designed this way (senior/staff):**
Memento solves a fundamental tension in object-oriented programming: state must be accessible enough to be saved, but private enough to be protected. The pattern's solution — the wide/narrow interface duality — exploits language-specific access control mechanisms. In Java, nested class and package-private visibility are the primary tools. This makes Memento one of the most language-specific GoF patterns — its ideal implementation differs significantly between Python (no access control), Kotlin (data class copy()), and Java (nested class). In distributed systems, Memento manifests as event sourcing snapshots: the aggregate (Originator) creates a state snapshot Memento periodically to avoid replaying 10M events from the beginning. The snapshot is stored opaquely (serialised) by the infrastructure (Caretaker), decoded only by the aggregate itself on load.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  MEMENTO PATTERN — UNDO SYSTEM                       │
│                                                      │
│  TextEditor (Originator)                             │
│  ┌─────────────────────────────────────────────┐    │
│  │ private String content;                     │    │
│  │ private int    cursorPos;                   │    │
│  │                                             │    │
│  │ save():                                     │    │
│  │   return new Memento(content, cursorPos)    │    │
│  │                                             │    │
│  │ restore(Memento m):                         │    │
│  │   this.content   = m.content;               │    │
│  │   this.cursorPos = m.cursorPos;             │    │
│  │                                             │    │
│  │ class Memento {   ← nested class            │    │
│  │   final String content;  ← private access  │    │
│  │   final int cursorPos;                     │    │
│  │                                             │    │
│  │   Memento(String c, int p) {               │    │
│  │     this.content   = c;                    │    │
│  │     this.cursorPos = p;                    │    │
│  │   }                                         │    │
│  │ }                                           │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  UndoHistory (Caretaker)                             │
│  Deque<TextEditor.Memento> history                   │
│  — holds opaque Mementos, cannot read content field  │
└──────────────────────────────────────────────────────┘
```

**Undo sequence:**
```
User types "Hello":
  editor.content = "Hello"
  Before typing: history.push(editor.save())
  
User types " World":
  editor.content = "Hello World"
  Before typing: history.push(editor.save())

User presses Ctrl+Z:
  memento = history.pop()   // most recent "Hello World" state? No —
  // wait: save() was called BEFORE the action
  editor.restore(memento)
  // editor.content = "Hello" (state before " World" was typed)
```

Note: save timing matters. The snapshot must be taken BEFORE the action for correct undo semantics.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
User types a character in text editor
  → Before applying: editor.save()
                               ← YOU ARE HERE (Memento created)
  → Caretaker: history.push(memento)
  → editor.applyChange(character)
  → UI updates with new content

User presses Ctrl+Z:
  → Caretaker: memento = history.pop()
  → editor.restore(memento)
  → editor.content and cursorPos restored
  → UI updates to previous state

User presses Ctrl+Z again:
  → Caretaker: memento = history.pop()
  → editor state rolls back one more step
```

**FAILURE PATH:**
```
history stack is empty (nothing to undo)
  → history.pop() returns null
  → editor.restore(null) → NullPointerException
Fix: check history.isEmpty() before pop
  → disable Undo menu item when history is empty
  → notify user "Nothing to undo"
```

**WHAT CHANGES AT SCALE:**
In a collaborative editor (Google Docs style), Memento is replaced by Operational Transformations (OT) or CRDTs — state cannot be restored by a single actor when multiple editors are modifying simultaneously. For large single-user state objects (game worlds, large spreadsheets), delta Mementos (capture only changed state) reduce memory dramatically. For persistence across sessions, Mementos are serialised — requiring versioning for backwards compatibility.

---

### 💻 Code Example

**Example 1 — BAD: Exposing state for external snapshot:**
```java
// BAD: exposes private state to enable external undo
public class TextEditor {
    private String content;
    private int cursorPos;

    // Forces exposing internals for undo system
    public String getContent()    { return content; }
    public int getCursorPos()     { return cursorPos; }
    public void setContent(String c) { content = c; }
    public void setCursorPos(int p) { cursorPos = p; }
}

// UndoHistory must manually reconstruct state
// Any class can now corrupt editor state via setters
```

**Example 2 — GOOD: Memento pattern with nested class:**
```java
public class TextEditor {
    private String content    = "";
    private int    cursorPos  = 0;
    private String selection  = "";

    // === Originator operations ===
    public void type(String text) {
        content = content.substring(0, cursorPos)
            + text
            + content.substring(cursorPos);
        cursorPos += text.length();
    }

    public String getContent() { return content; }

    // === Memento creation (full snapshot) ===
    public Memento save() {
        return new Memento(content, cursorPos, selection);
    }

    // === State restoration ===
    public void restore(Memento m) {
        this.content   = m.content;   // access nested field
        this.cursorPos = m.cursorPos;
        this.selection = m.selection;
    }

    // === Nested Memento class ===
    // Caretaker can hold but cannot read fields
    public static final class Memento {
        // package-private: accessible by TextEditor only
        private final String content;
        private final int    cursorPos;
        private final String selection;

        private Memento(String c, int p, String s) {
            this.content   = c;
            this.cursorPos = p;
            this.selection = s;
        }

        // Caretaker can only use this for labelling:
        @Override
        public String toString() {
            return "Snapshot[chars=" + c.length() + "]";
        }
        // NO getters for content, cursorPos, selection
    }
}

// Caretaker: manages history, cannot read state
public class UndoHistory {
    private static final int MAX_UNDO = 50;
    private final Deque<TextEditor.Memento> history
        = new ArrayDeque<>();

    public void save(TextEditor editor) {
        if (history.size() >= MAX_UNDO) {
            // FIFO: remove oldest when limit reached
            ((ArrayDeque<?>)history).removeLast();
        }
        history.push(editor.save());
    }

    public boolean canUndo() {
        return !history.isEmpty();
    }

    public void undo(TextEditor editor) {
        if (history.isEmpty()) return;
        editor.restore(history.pop());
    }
}

// Usage:
TextEditor editor  = new TextEditor();
UndoHistory undoMgr = new UndoHistory();

undoMgr.save(editor);     // snapshot before change
editor.type("Hello");

undoMgr.save(editor);
editor.type(" World");

undoMgr.undo(editor);     // → "Hello"
undoMgr.undo(editor);     // → ""
```

**Example 3 — Delta Memento for large state:**
```java
// Full snapshot is too large; capture only changes
public class Spreadsheet {
    private final Map<CellRef, CellData> cells = new HashMap<>();

    // Delta Memento: only changed cells
    public DeltaMemento saveChanges(Set<CellRef> changedCells) {
        Map<CellRef, CellData> snapshot = new HashMap<>();
        for (CellRef ref : changedCells) {
            snapshot.put(ref, cells.get(ref).copy());
        }
        return new DeltaMemento(snapshot);
    }

    public void restore(DeltaMemento m) {
        m.snapshot.forEach((ref, data) ->
            cells.put(ref, data));
    }

    public static final class DeltaMemento {
        private final Map<CellRef, CellData> snapshot;

        private DeltaMemento(Map<CellRef, CellData> snap) {
            this.snapshot = Collections.unmodifiableMap(snap);
        }
    }
}
// 10 changes → 10 cell snapshots (not 10,000 cell copies)
```

---

### ⚖️ Comparison Table

| Approach | Encapsulation | Memory | Granularity | Best For |
|---|---|---|---|---|
| **Memento** | Preserved (opaque) | Snapshot size | Per-save | Undo/redo with encapsulation |
| Full clone (Prototype) | Broken (state exposed) | Full copy | Per-clone | When state is public |
| Serialisation | Preserved (opaque bytes) | Full serialised | Per-save | Persistence + network transport |
| Delta-only Memento | Preserved | Delta size | Changed fields | Large state with incremental changes |
| Event Sourcing | N/A (events not state) | All events | Per-event | Audit trails, full replay |

How to choose: use Memento when the object has private state that must be saved/restored and the Caretaker must remain ignorant of the state details. Use Prototype (clone) when the state is public and a simple deep copy suffices. Use Event Sourcing when audit trails matter more than compactness.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Memento requires the state to be serialisable | Only if Mementos are persisted. In-memory undo (transient Mementos) requires no serialisation |
| Memento is the same as cloning the object | `clone()` creates a fully accessible copy of the object (same type, same accessible fields). Memento creates an opaque snapshot — the state is inaccessible to third parties |
| Memento must store the ENTIRE object state | Delta Mementos (storing only changed state) are a valid and often more efficient variant |
| The Caretaker can use Mementos to inspect state | By design, the Caretaker should hold Mementos as opaque objects with no access to the state they contain |
| Memento is only for UI undo/redo | Memento applies to any rollback scenario: database transactions, game state saves, workflow checkpoints, configuration rollbacks |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory Exhaustion from Unbounded Memento History**

**Symptom:** Application heap grows steadily. Memory profiler shows thousands of large Memento objects. Application crashes with OOM after extended use.

**Root Cause:** Caretaker holds an unbounded `Deque<Memento>`. In a code editor, each keypress creates a Memento. After an hour of coding (10,000 keystrokes on large files), 10,000 full state snapshots are in memory.

**Diagnostic:**
```bash
jmap -histo:live <PID> | grep Memento
# Shows: count and total bytes of Memento instances
# If growing unboundedly: cap missing
```

**Fix:**
Cap the history in Caretaker: `if (history.size() >= MAX_UNDO) history.removeLast()`. Switch from full Mementos to delta Mementos to reduce per-snapshot size.

**Prevention:** Set `MAX_UNDO_LEVELS` at design time. Monitor Memento memory with JVM heap profiling in production.

---

**2. Memento State Shared Between Instances**

**Symptom:** Restoring from a Memento changes the current state, and the restored state continues to change as the object's fields mutate. Undo seemingly has no effect.

**Root Cause:** The Memento holds references to mutable objects (not deep copies). When the Originator changes `content` (a `StringBuilder`), the Memento's reference sees the changes too.

**Diagnostic:**
```java
// Check if Memento holds value or reference:
Memento m = editor.save();
editor.type("X"); // mutate
// If m.content is now "X" — shallow copy bug
```

**Fix:**
The Memento must hold deep copies (or create an immutable snapshot) of all mutable state. For `String`: immutable by default (safe). For `List`: `new ArrayList<>(original)`. For custom objects: copy-constructor or explicit deep copy.

**Prevention:** Memento constructor must defensively copy all mutable fields. Code review: verify that every mutable object in Memento's constructor is copied.

---

**3. Memento Incompatibility After Refactoring**

**Symptom:** After adding a field to `TextEditor`, saved Mementos from before the refactoring cannot be restored. Old session saves are worthless.

**Root Cause:** Memento was designed for runtime undo (discarded on application shutdown). Now it is persisted to disk/database. The Memento's structure changed with the Originator.

**Diagnostic:**
```java
// Add a version field to persisted Mementos:
public static final class Memento {
    private final int    version = 2; // increment on change
    private final String content;
    // ... other fields ...
}
// On restore: check version, apply migration if needed
```

**Fix:**
Add Memento versioning. `restore(Memento m)` checks `m.version` and applies migration logic for old versions.

**Prevention:** If Mementos are persisted (game saves, session snapshots), design versioning from the start. Use explicit migration paths when the originator's state schema changes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Encapsulation` — Memento's purpose is preserving encapsulation during state capture; understanding what encapsulation means drives the pattern's design decisions
- `Command` — frequently paired with Memento; Command captures the action, Memento captures the pre-action state for undo
- `Immutability` — Memento state should be immutable after creation; understanding immutability guarantees correct Memento behaviour

**Builds On This (learn these next):**
- `Event Sourcing` — architectural-scale Memento; the aggregate's state is reconstructed from replaying events (commands), with periodic Memento snapshots for performance
- `Command + Memento (Undo System)` — the canonical pair: Command defines the action and undo action; Memento stores the state needed to undo
- `Serialisation` — enables persisting Mementos across sessions; understanding serialisation strategies is required for durable Mementos

**Alternatives / Comparisons:**
- `Prototype (clone)` — captures full state via object clone; less encapsulated (clone IS the object, all state accessible)
- `State` — the State pattern manages state transitions; Memento captures state snapshots for restoration
- `Event Sourcing` — stores events (what changed) rather than states (what it became); complementary approach at different scale requirements

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Opaque snapshot of an object's state      │
│              │ that only the object knows how to read    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Saving state for undo requires exposing   │
│ SOLVES       │ private fields — breaking encapsulation   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Wide interface (originator reads/writes)  │
│              │ + narrow interface (caretaker holds only) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object state must be captured/restored    │
│              │ without exposing private fields externally│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ State is already public; or object graph  │
│              │ is too large for full snapshot            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Encapsulation preserved vs memory cost    │
│              │ of storing state snapshots                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sealed envelope: only the sender         │
│              │  knows what's inside."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Command + Memento → Event Sourcing →       │
│              │ CQRS                                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A game "CheckpointSystem" uses Memento to save the player's full game state (position, inventory, health, quest state). The inventory contains 500 items; each item has mutable attributes (weapon durability degrades). On save, the CheckpointSystem calls `game.save()` which creates a Memento storing references to the 500 item objects (not copies). The player loads the checkpoint and continues playing — item durability keeps degrading. Two game sessions later, the checkpoint shows items at their CURRENT (degraded) values, not their values AT SAVE TIME. Trace the exact object reference chain that causes this, prove it with a minimal code example, and provide the one-line fix.

**Q2.** A cloud database service uses Memento to implement point-in-time recovery. Every 5 minutes, a full database state Memento is serialised and stored in S3. The database has 1 TB of data. Calculate the storage cost of 30 days of 5-minute Mementos. Then redesign the snapshot strategy to achieve the same recovery objective (restore to any 5-minute interval in the last 30 days) with at least 90% less storage — without changing the recovery interface.

