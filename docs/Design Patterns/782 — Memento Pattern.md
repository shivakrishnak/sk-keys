---
layout: default
title: "Memento Pattern"
parent: "Design Patterns"
nav_order: 782
permalink: /design-patterns/memento-pattern/
number: "782"
category: Design Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Command Pattern, Encapsulation"
used_by: "Undo/redo systems, Snapshots, Save/restore state, Game checkpoints"
tags: #advanced, #design-patterns, #behavioral, #oop, #undo-redo, #state-management
---

# 782 — Memento Pattern

`#advanced` `#design-patterns` `#behavioral` `#oop` `#undo-redo` `#state-management`

⚡ TL;DR — **Memento** captures and externalizes an object's internal state so it can be restored later — without violating encapsulation by allowing only the originator to create and restore from mementos, while the caretaker stores mementos without knowing their contents.

| #782 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Command Pattern, Encapsulation | |
| **Used by:** | Undo/redo systems, Snapshots, Save/restore state, Game checkpoints | |

---

### 📘 Textbook Definition

**Memento** (GoF, 1994): a behavioral design pattern that, without violating encapsulation, captures and externalizes an object's internal state so that the object can be restored to this state later. Three roles: **Originator** — the object whose state needs to be saved; creates and uses mementos. **Memento** — stores a snapshot of the originator's state; only the originator can read its contents. **Caretaker** — holds mementos; never peeks inside them; asks originator to save/restore. GoF intent: "Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later." Alternative to Command pattern undo (Command: reversal logic per command; Memento: state snapshot approach).

---

### 🟢 Simple Definition (Easy)

A save game slot in a video game. Your character: level 42, 3000 HP, 450 gold, at position (100, 200). You hit Save → game captures all this state into a save slot (memento). You play more, die, lose progress. You load the save → character restored to exactly the state at save time. The save slot is the memento: it holds the state snapshot. The game engine is the originator: it creates and restores from save slots. The save/load menu is the caretaker: it stores save slots but doesn't interpret them.

---

### 🔵 Simple Definition (Elaborated)

Text editor: typing history with Ctrl+Z undo. Every keystroke creates a state snapshot (`TextEditorMemento`): cursor position, full text content, selection state. Snapshots are stored in a stack (caretaker: `UndoStack`). Ctrl+Z: pop snapshot from stack, call `editor.restore(memento)` — editor returns to that exact state. The caretaker (`UndoStack`) holds the snapshots but doesn't know what's inside them. Only the `TextEditor` (originator) can create and interpret the snapshots.

---

### 🔩 First Principles Explanation

**The encapsulation contract and why only originator can access memento internals:**

```
MEMENTO STRUCTURE:

  ORIGINATOR: TextEditor
  ───────────────────────
  -text: String
  -cursorPos: int
  -selection: Range
  
  +save(): TextEditorMemento
      return new TextEditorMemento(text, cursorPos, selection)
      
  +restore(TextEditorMemento m):
      this.text      = m.getText()        // only Originator calls getText()
      this.cursorPos = m.getCursorPos()
      this.selection = m.getSelection()
  
  MEMENTO: TextEditorMemento
  ───────────────────────────
  -text: String              // package-private or nested class in Originator
  -cursorPos: int            // Caretaker cannot access these fields
  -selection: Range
  
  // Constructor: package-private (only Originator can create)
  TextEditorMemento(String text, int cursorPos, Range selection) { ... }
  
  // Getters: package-private or only accessible to Originator
  String getText()      { return text; }
  int getCursorPos()    { return cursorPos; }
  Range getSelection()  { return selection; }
  
  CARETAKER: UndoStack
  ────────────────────
  -history: Deque<TextEditorMemento>
  
  +push(TextEditorMemento m): history.push(m)
  +pop(): TextEditorMemento:  return history.pop()
  // Caretaker stores mementos but NEVER reads their contents!
  
ENCAPSULATION IN JAVA:

  // Java doesn't have "friend" access like C++, so the pattern uses:
  // 1. INNER CLASS: Memento is a private inner class of Originator
  //    Only Originator can access its internals.
  
  public class TextEditor {
      private String text;
      private int cursorPos;
      
      // Memento as PRIVATE INNER CLASS — Caretaker holds it as opaque object:
      public class Memento {
          private final String text;
          private final int cursorPos;
          
          private Memento(String text, int cursorPos) {
              this.text = text;
              this.cursorPos = cursorPos;
          }
          // No public getters! Only TextEditor (outer class) can access fields.
      }
      
      public Memento save() {
          return new Memento(text, cursorPos);   // creates memento (encapsulated)
      }
      
      public void restore(Memento m) {
          this.text      = m.text;           // outer class accesses private fields
          this.cursorPos = m.cursorPos;      // of inner class — Java allows this
      }
  }
  
  // Caretaker:
  class UndoManager {
      private final Deque<TextEditor.Memento> history = new ArrayDeque<>();
      
      void save(TextEditor editor) {
          history.push(editor.save());  // holds Memento but can't inspect it
      }
      
      void undo(TextEditor editor) {
          if (!history.isEmpty()) editor.restore(history.pop());
      }
  }
  
MEMENTO vs COMMAND FOR UNDO:

  COMMAND UNDO:
  - Each command knows how to reverse itself.
  - InsertCommand.undo() → delete what was inserted.
  - DeleteCommand.undo() → re-insert what was deleted.
  - Compact: only stores what changed.
  - Better for: operations where reversal logic is simple and state changes are small.
  
  MEMENTO UNDO:
  - Save full state snapshot before each operation.
  - Restore full state on undo.
  - Simpler undo logic: just restore snapshot.
  - More memory: stores full state for each step (even if only 1 char changed, stores all text).
  - Better for: complex state where computing reversal is hard; state is small; snapshots are cheap.
  
INCREMENTAL SNAPSHOTS (optimization):

  // For large state: don't snapshot entire state each time — store diffs (deltas):
  
  class GameStateMemento {
      private final Map<String, Object> changedFields;   // only changed fields
      private final GameStateMemento previous;           // link to previous (for full restore)
      
      GameStateMemento(Map<String, Object> changed, GameStateMemento previous) {
          this.changedFields = changed;
          this.previous      = previous;
      }
  }
  
  // Full restore = apply all deltas from oldest to newest.
  // This is the basis of event sourcing: each event is a delta memento.
  
  // Git commit = Memento: stores diff (delta) against parent commit.
  // Full file content = replay all diffs from initial commit.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Memento:
- Undo: expose internal state in getters → break encapsulation (caretaker reads internals)
- OR: give caretaker the full state copy → caretaker becomes coupled to originator's internals

WITH Memento:
→ Originator creates an opaque snapshot (only originator can read it). Caretaker stores it without knowing internals.
→ Encapsulation preserved: state captured and restored without external coupling.

---

### 🧠 Mental Model / Analogy

> A sealed time capsule. You (originator) put exactly what you choose into the capsule and seal it. A vault (caretaker) stores your capsule for you — the vault manager doesn't know what's inside, doesn't read it, doesn't modify it. When you want to return to that past state, you open your OWN capsule. The vault gives it back to you, but only you can open it and interpret its contents. The vault just stores it safely.

"You (originator)" = TextEditor, game, or any stateful object
"What you put in capsule" = internal state (text, cursor, player data)
"Sealed capsule" = Memento (opaque to others, meaningful only to originator)
"Vault manager" = Caretaker (holds capsules, never opens them)
"You open your capsule" = originator.restore(memento) — only originator interprets

---

### ⚙️ How It Works (Mechanism)

```
MEMENTO FLOW:

  Save:
  Originator.save() → creates Memento(copy of internal state)
  Caretaker.push(memento) → stores opaque Memento
  
  Restore:
  Caretaker.pop() → returns Memento to Originator
  Originator.restore(memento) → reads Memento contents, restores internal state
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to save and restore object state without exposing internals
        │
        ▼
Memento Pattern ◄──── (you are here)
(originator creates opaque snapshot; caretaker stores; only originator restores)
        │
        ├── Command: alternative undo strategy (reversal logic vs state snapshot)
        ├── Iterator: iterate through history of mementos
        ├── Prototype: both create copies of state; Memento: for temporal restore; Prototype: for new instance
        └── Event Sourcing: architectural Memento — event log as append-only state history
```

---

### 💻 Code Example

```java
// Game character state with undo/checkpoint:

public class GameCharacter {
    private String name;
    private int health;
    private int level;
    private int gold;
    private Position position;
    
    // MEMENTO — private nested class; only GameCharacter can access internals:
    public class Checkpoint {
        private final int health;
        private final int level;
        private final int gold;
        private final Position position;
        private final String timestamp;
        
        private Checkpoint(int health, int level, int gold, Position position) {
            this.health    = health;
            this.level     = level;
            this.gold      = gold;
            this.position  = position.copy();   // defensive copy
            this.timestamp = Instant.now().toString();
        }
        
        public String getTimestamp() { return timestamp; }
        // NOTE: other fields are private — only GameCharacter can access them
    }
    
    // ORIGINATOR creates memento:
    public Checkpoint save() {
        return new Checkpoint(health, level, gold, position);
    }
    
    // ORIGINATOR restores from memento:
    public void restore(Checkpoint cp) {
        this.health   = cp.health;     // inner class field — accessible to outer class
        this.level    = cp.level;
        this.gold     = cp.gold;
        this.position = cp.position.copy();
    }
    
    // Game methods:
    public void takeDamage(int dmg) { this.health -= dmg; }
    public void gainGold(int amount) { this.gold += amount; }
    public void move(Position pos) { this.position = pos; }
}

// CARETAKER — stores checkpoints, knows nothing about their contents:
class SaveSlotManager {
    private final Map<String, GameCharacter.Checkpoint> slots = new LinkedHashMap<>();
    
    void save(String slotName, GameCharacter character) {
        slots.put(slotName, character.save());
        System.out.println("Saved to: " + slotName);
    }
    
    void load(String slotName, GameCharacter character) {
        GameCharacter.Checkpoint cp = slots.get(slotName);
        if (cp != null) {
            character.restore(cp);
            System.out.println("Loaded from: " + slotName + " (" + cp.getTimestamp() + ")");
        }
    }
    
    List<String> listSlots() { return new ArrayList<>(slots.keySet()); }
}

// Usage:
GameCharacter hero = new GameCharacter("Aria", 100, 1, 0, Position.of(0, 0));
SaveSlotManager saves = new SaveSlotManager();

saves.save("start", hero);       // hero: 100 HP, level 1, 0 gold

hero.gainGold(500);
hero.takeDamage(20);             // hero: 80 HP, level 1, 500 gold

saves.save("slot1", hero);       // save current state

hero.takeDamage(90);             // hero: -10 HP — dead!

saves.load("slot1", hero);       // restore: 80 HP, 500 gold ← back from save
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Memento and Command undo are interchangeable | They solve the same problem (undo) differently. Command undo: each command knows how to reverse itself (compact; only stores delta). Memento undo: save full state snapshot (simpler; potentially more memory). Choose Command when reversal logic is straightforward. Choose Memento when state is complex/hard to reverse programmatically, or when state is small enough that snapshots are cheap. |
| Caretaker can read memento contents for its own purposes | Violates the pattern's encapsulation contract. Caretaker is an opaque holder — no business logic based on memento contents. If caretaker needs to display "last saved at 3pm," use a single descriptive string exposed from the memento (as in `getTimestamp()` above). But caretaker must not access the originator's internal data. |
| Memento must save ALL internal state | Partial state mementos are valid if you only need to restore a subset of state. Example: save only the undo-relevant text without UI layout state. The key is that what's saved is sufficient to restore the originator to a correct previous state. Optimization: save only the changed fields (delta memento). |

---

### 🔥 Pitfalls in Production

**Memory exhaustion from unlimited undo history:**

```java
// ANTI-PATTERN: Unlimited undo stack — each keystroke saves full document text:
class UndoManager {
    private final Deque<TextEditor.Memento> history = new ArrayDeque<>();
    
    void saveState(TextEditor editor) {
        history.push(editor.save());  // no limit! 
        // Document: 1MB text × 10,000 keystrokes = 10GB of undo history!
    }
}

// FIX 1: Bounded history (most common):
class UndoManager {
    private static final int MAX_HISTORY = 100;
    private final Deque<TextEditor.Memento> history = new ArrayDeque<>();
    
    void saveState(TextEditor editor) {
        if (history.size() >= MAX_HISTORY) {
            history.pollLast();  // remove oldest to make room
        }
        history.push(editor.save());
    }
}

// FIX 2: Delta mementos (only save what changed):
class TextEditorMemento {
    private final int changeStart;
    private final String oldText;      // text that was replaced
    private final String newText;      // what replaced it
    private final int cursorPos;
    
    // Restore: apply inverse delta — much smaller than full snapshot
}

// FIX 3: Merge fine-grained mementos (debounce):
// Don't save a memento every single keystroke.
// Save a memento when user pauses for 500ms, or every N characters.
// "Word-level" undo granularity instead of character-level.
```

---

### 🔗 Related Keywords

- `Command Pattern` — alternative undo: each command stores its own reversal logic
- `Prototype Pattern` — both create copies; Memento: temporal snapshots; Prototype: new instances
- `Iterator Pattern` — iterate through history of stored mementos
- `Event Sourcing` — architectural Memento: event log as immutable history of state changes
- `Snapshot Pattern` — periodic full-state snapshots (performance optimization for event sourcing)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Capture originator's state in opaque     │
│              │ Memento. Caretaker stores it without     │
│              │ knowing contents. Originator restores.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need undo/redo; save/restore game state;  │
│              │ snapshot before risky operation; state   │
│              │ reversal logic would be complex in Command│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ State objects are large (memory cost);   │
│              │ Command pattern reversal is simpler;     │
│              │ state has references to external resources│
│              │ that can't be meaningfully snapshotted   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sealed time capsule: you fill it, seal  │
│              │  it; vault stores it blindly; only you  │
│              │  open and interpret when needed."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Command Pattern → Event Sourcing →        │
│              │ Prototype Pattern → Iterator Pattern      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Event sourcing is often described as an architectural application of the Memento pattern. Instead of storing current state, the system stores an append-only sequence of events (state changes). Current state = replay all events. This is conceptually similar to having a Memento for every state transition. How does event sourcing's "snapshot + event replay" optimization map to the Memento pattern? In event sourcing, what is the "Originator," what is the "Memento," and what is the "Caretaker"?

**Q2.** Java's serialization (`ObjectOutputStream`) can be used to implement Memento by serializing the originator's state to a byte array and restoring by deserializing. What are the advantages and risks of this approach? Consider: class evolution (if fields change between save and restore), security (deserialization vulnerabilities), and performance. When would you prefer this approach over manually coding a Memento? What is the recommended modern Java alternative (e.g., Jackson, records, custom serialization)?
