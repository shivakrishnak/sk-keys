---
layout: default
title: "Command"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /design-patterns/command/
id: DPT-037
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
  - bestpractice
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-051 - Command

⚡ TL;DR - Command encapsulates a request as an object so it can be queued, logged, undone, or parameterised independently of the sender.

| DPT-051 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Encapsulation, Queue Data Structure | |
| **Used by:** | Undo/Redo Systems, Task Queues, Macro Recording, Transaction Logs | |
| **Related:** | Chain of Responsibility, Strategy, Observer, Memento | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A text editor has Bold, Italic, Copy, Paste, and 50 other operations. Each toolbar button, keyboard shortcut, and menu item calls the operation directly: `document.setBold()`, `document.setItalic()`. There is no undo system - to add undo, every single operation must be duplicated with a reverse operation, and a history stack manually managed. To add "macro recording" (replay a sequence of user actions), every operation must be interceptable and serialisable. These features require touching 50+ methods across the codebase.

**THE BREAKING POINT:**
Three distinct problems emerge from calling operations directly: (1) **No undo** - reversing requires knowing what was done, but by the time you want to undo, the original state is gone. (2) **No queuing** - background operations cannot be deferred or ordered. (3) **No audit trail** - logging "what the user did" requires separate logging in each of 50 operations. All three require modifying the same 50 operation methods.

**THE INVENTION MOMENT:**
This is exactly why the Command pattern was created. Each operation becomes a `Command` object: `BoldCommand`, `ItalicCommand`. The command encapsulates the receiver (`document`), all parameters needed to execute, and optionally the state needed to undo. Undo: call `command.undo()`. Queue: put commands in a `BlockingQueue`. Audit log: log `command.getClass().getName()` before execution. Every capability lives in the command object - no changes to the 50 operation methods.

**EVOLUTION:**
Command was critical in GUI applications for undo/redo and
macro recording -- the primary Use Cases in GoF (1994). Java
Swing's `Action` interface and `UndoManager` implement it
directly. In modern backend systems, Command evolved into:
CQRS write commands (capturing user intent as a named
command object), task queues (serialised commands sent to
workers), and event sourcing (persisting commands as the
source of truth). JavaScript's promise chains and async/
await are also conceptually Command-based: each `.then()`
is a deferred command. Today Command is foundational in
messaging and distributed systems.

---

### 📘 Textbook Definition

The **Command** pattern is a behavioural design pattern that turns a request into a stand-alone object that contains all information about the request: the receiver (the object performing the action), the method to call, and the parameters. This encapsulation allows requests to be parameterised, queued, logged, undone, or transmitted over a network. A command object implements a common interface (typically `execute()` and optionally `undo()`) that decouples the invoker (who triggers the command) from the receiver (who executes the operation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Wrap an action into an object so it can be stored, queued, replayed, or undone.

**One analogy:**
> A restaurant order slip. The waiter (invoker) writes your order on a slip (command object). The slip goes to the kitchen (queue). The chef (receiver) reads the slip and cooks. The slip can be cancelled (undo), the kitchen can prioritise slips, and the manager can review all slips for the night (audit log). The waiter never cooks; the chef never takes orders.

**One insight:**
Command decouples the WHAT (the action) from the WHEN, WHERE, and HOW it is executed. Before Command, calling `document.setBold()` meant "execute now, on this thread, by this caller." After Command, `new BoldCommand(document)` means "here is an action - do it now, schedule it, undo it, or log it - your choice."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An operation must be callable after the original caller has finished (decoupled in time and location).
2. An operation must be reversible (undo) - requiring that its pre-execution state is captured or its reverse operation defined.
3. Operations must be composable - a macro is a sequence of commands; a transaction is an atomic sequence of commands.

**DERIVED DESIGN:**
Given invariant 1: the operation is packaged with all the data it needs into an object - it carries its own context. Given invariant 2: the command object can store the state needed to reverse the action in fields. Given invariant 3: a `MacroCommand` implements `Command` and holds a list of sub-commands - executing it executes each in turn; undoing it reverses in reverse order.

The structure:
- **Command** interface: `execute()`, optionally `undo()`, `isUndoable()`
- **ConcreteCommand**: implements `Command`, holds reference to receiver, holds pre-execute state for undo
- **Invoker**: holds command(s); calls `execute()` at the appropriate time
- **Receiver**: the object that actually performs the work when called by the command

**THE TRADE-OFFS:**
**Gain:** Undo/redo for free (store executed command history); queuing and scheduling; logging/audit (log commands, not individual method calls); macro recording; transactional batching.
**Cost:** Proliferation of small command classes (one per operation); state capture for undo adds memory overhead; complex commands require complex undo logic; receiver must be serialisable if commands are distributed.

---

### 🧪 Thought Experiment

**SETUP:**
A 3D modelling application lets users move objects. Without Command, `object.moveTo(newPosition)` is called directly. Undo is requested.

**WHAT HAPPENS WITHOUT COMMAND:**
`object.moveTo(newPosition)` changes the position. At undo time: what was the old position? It was discarded when overwritten. Two options: (a) every operation stores the old state externally - global mutable history not tied to the operations themselves; (b) add `saveOldPosition()` before every `moveTo` call at every call site - 20 places in the codebase.

**WHAT HAPPENS WITH COMMAND:**
```java
MoveCommand cmd = new MoveCommand(object, newPosition);
// cmd captures: object, newPosition, AND oldPosition now
cmd.execute();       // moves to newPosition
// Undo:
cmd.undo();         // restores oldPosition from cmd.oldPosition
```
The command owns the state transition. Undo is trivially implemented because the command captured both old and new state at construction time.

**THE INSIGHT:**
Command makes the state transition explicit and self-contained. The `execute()` moves forward; the `undo()` moves backward. No external state tracking is needed - the command IS the state transition.

---

### 🧠 Mental Model / Analogy

> The Command pattern is like a recipe card. The recipe card (command object) contains: what to cook (the action), the ingredients (parameters), and the steps (receiver calls). You hand the recipe to the chef (invoker) who executes it. You can store recipe cards (queue), replay a favourite meal (redo), or reverse-cook it (undo - imagine defrost). The recipe is separate from whoever cooks it.

- "Recipe card" → command object
- "Chef" → invoker (calls `command.execute()`)
- "Cooking instructions" → `execute()` method
- "Ingredient list" → parameters stored in the command
- "The kitchen equipment and pantry" → receiver object
- "Stack of recipe cards done today" → command history (for undo)

Where this analogy breaks down: unmaking a cooked meal (undo) is physically impossible for real food. In software, undo requires the command to capture reversible state - not all operations are truly undoable in the domain.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Command wraps an action in a package you can hand around, store, and open later. Instead of doing something immediately, you describe what to do (with all its details) and hand the description to someone else. They decide when to act on it. You can cancel it before they open the package, or have them "undo" it afterward.

**Level 2 - How to use it (junior developer):**
Create a `Command` interface with `void execute()`. Optionally add `void undo()`. For each operation: create a class implementing `Command` that holds the receiver and parameters. In the constructor, capture state needed for undo. In `execute()`, perform the action. In `undo()`, reverse it. Build an `undoStack: Deque<Command>`. After executing a command, push it onto the stack. For undo: pop the stack and call `undo()` on the popped command.

**Level 3 - How it works (mid-level engineer):**
The Invoker holds the command reference and decides when to execute. Classic pattern: Button + Command. The button (Invoker) has a `setCommand(Command c)` method. Pressing the button calls `command.execute()`. The button doesn't know what the command does - it knows only the interface. For task queues: commands implement `Runnable` or `Callable` (Java's built-in Command interfaces); `ExecutorService` is the Invoker. In Spring Batch: `ItemProcessor` and `Step` are Commands executed by the `Job` (the Invoker). For distributed commands: commands must be serialisable - they are transmitted as messages and executed by remote consumers (e.g., a Kafka consumer executing `Command.execute()` on the consuming service).

**Level 4 - Why it was designed this way (senior/staff):**
Command is one of the most reused patterns because it solves the fundamental problem of "deferred execution" - the same problem that `Runnable`, `Callable`, `Future`, `CompletableFuture`, message queues, and event sourcing all address. In event sourcing, every state change is stored as a Command (event); replaying the event log rebuilds any past state - this is Command at the architectural level. Command's `execute()` + `undo()` is the minimal API for a transaction log: apply the command; if rollback needed, reverse it. Database transactions implement exactly this. The deepest connection: Command + Memento = undo/redo stack. Command + Queue = task scheduler. Command + Log = event sourcing. Command is the atomic unit of "an action that happened."

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  COMMAND PATTERN - UNDO/REDO STACK                   │
│                                                      │
│  User presses Bold:                                  │
│    cmd = new BoldCommand(document, selection)        │
│    cmd.execute() → document.setBold(selection, true) │
│    undoStack.push(cmd)                               │
│                                                      │
│  User presses Ctrl+Z (Undo):                         │
│    cmd = undoStack.pop()                             │
│    cmd.undo() → document.setBold(selection, false)   │
│                                                      │
│  User presses Ctrl+Y (Redo):                         │
│    redoStack: cmd pushed from undoStack on undo      │
│    cmd = redoStack.pop()                             │
│    cmd.execute() → reapplies bold                    │
│                                                      │
│  Undo Stack (LIFO):                                  │
│  [BoldCmd] ← [ItalicCmd] ← [MoveCmd] ← TOP          │
└──────────────────────────────────────────────────────┘
```

**Task queue variant:**
```
Producer thread:
  queue.offer(new ResizeImageCommand(image, 800, 600))
  queue.offer(new AddWatermarkCommand(image, "© 2024"))

Worker thread (Invoker):
  while (running):
    cmd = queue.take()  // blocks until available
    cmd.execute()       // processes asynchronously
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (editor with undo):**
```
User action (Bold button click)
  → Button.onClick()
  → Creates BoldCommand(doc, selection)
                          ← YOU ARE HERE
  → Calls commandHistory.execute(cmd)
  → CommandHistory: cmd.execute()
  → BoldCommand.execute():
      saves oldState = doc.getFormatting(selection)
      doc.setBold(selection, true)
  → Command pushed to undoStack
  → UI updates

User presses Ctrl+Z:
  → CommandHistory.undo()
  → pops BoldCommand from undoStack
  → BoldCommand.undo():
      doc.setFormatting(selection, oldState)
  → UI updates (bold removed)
```

**FAILURE PATH:**
```
BoldCommand.execute() throws DocumentLockedException
  → Command NOT pushed to undoStack
  → Undo state is not corrupted
  → User sees error; document unchanged
Fix: execute() must be atomic - all or nothing
```

**WHAT CHANGES AT SCALE:**
At 10,000 commands/second (high-frequency trading, game engine), command object allocation pressure becomes significant. Object pooling of command instances reduces GC. At distributed scale, commands are serialised to messages (Kafka events) and deserialized on consumers. Command objects must be idempotent (safe to re-execute if the consumer crashes mid-processing). Distributed command IDs (UUIDs) enable deduplication.

---

### 💻 Code Example

**Example 1 - BAD: Direct method calls, no undo:**
```java
// BAD: direct calls - no way to undo or queue
button.addActionListener(e -> {
    document.setBold(editor.getSelection(), true);
    // Undo? No record of what was done
});
```

**Example 2 - GOOD: Command pattern with undo:**
```java
// Command interface
public interface Command {
    void execute();
    void undo();
}

// Concrete command with pre-execute state
public class BoldCommand implements Command {
    private final TextDocument document;
    private final TextSelection selection;
    private FontStyle previousStyle; // captured for undo

    public BoldCommand(TextDocument doc,
                       TextSelection sel) {
        this.document  = doc;
        this.selection = sel;
    }

    @Override
    public void execute() {
        // Capture state BEFORE changing
        this.previousStyle =
            document.getStyle(selection);
        document.setStyle(selection,
            previousStyle.withBold(true));
    }

    @Override
    public void undo() {
        document.setStyle(selection, previousStyle);
    }
}

// Command history (Invoker + history manager)
public class CommandHistory {
    private final Deque<Command> undoStack
        = new ArrayDeque<>();
    private final Deque<Command> redoStack
        = new ArrayDeque<>();

    public void execute(Command cmd) {
        cmd.execute();
        undoStack.push(cmd);
        redoStack.clear(); // new action clears redo
    }

    public void undo() {
        if (undoStack.isEmpty()) return;
        Command cmd = undoStack.pop();
        cmd.undo();
        redoStack.push(cmd);
    }

    public void redo() {
        if (redoStack.isEmpty()) return;
        Command cmd = redoStack.pop();
        cmd.execute();
        undoStack.push(cmd);
    }
}

// Wiring:
CommandHistory history = new CommandHistory();
Button boldButton = new Button("Bold");
boldButton.addActionListener(e ->
    history.execute(
        new BoldCommand(document,
                        editor.getSelection())));

// Undo triggered by Ctrl+Z shortcut:
keyboard.onCtrlZ(() -> history.undo());
```

**Example 3 - Async command queue (task scheduling):**
```java
// Command carries all context for async execution
public class ResizeImageCommand implements Runnable {
    private final String inputPath;
    private final String outputPath;
    private final int targetWidth;
    private final int targetHeight;

    public ResizeImageCommand(String in, String out,
                               int w, int h) {
        this.inputPath   = in;
        this.outputPath  = out;
        this.targetWidth = w;
        this.targetHeight = h;
    }

    @Override
    public void run() { // Runnable IS a Command interface
        ImageProcessor.resize(
            inputPath, outputPath,
            targetWidth, targetHeight);
        log.info("Resized {} to {}x{}",
            inputPath, targetWidth, targetHeight);
    }
}

// Submit to thread pool (= async Invoker)
ExecutorService executor =
    Executors.newFixedThreadPool(4);
executor.submit(
    new ResizeImageCommand("input.jpg", "out.jpg",
                            800, 600));
// Command executes on a worker thread - decoupled in time
```

---

### ⚖️ Comparison Table

| Pattern | Encapsulates | Decouples | Key Feature | Best For |
|---|---|---|---|---|
| **Command** | A request as object | Invoker from receiver | Undo, queue, log | Editor actions, task queues |
| Strategy | An algorithm | Context from algorithm | Interchangeable algos | Sort, pricing, formatting |
| Chain of Responsibility | A handler chain | Sender from receiver | Conditional routing | Approval, middleware |
| Observer | An event notification | Publisher from subscriber | Broadcast | Events, reactive updates |
| Template Method | Algorithm skeleton | Algorithm from steps | Fixed sequence, var steps | Processing pipelines |

How to choose: use Command when the request itself must be stored, queued, logged, or reversed. Use Strategy when the algorithm varies per context but does not need to be stored or undone. Use Observer when the request is a notification broadcast to multiple subscribers.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Command and Strategy are the same | Command encapsulates a REQUEST with its parameters and context for deferred execution. Strategy encapsulates an ALGORITHM that is swapped at runtime to change behaviour. Commands are stored/queued; strategies are selected |
| Command requires an undo() method | `undo()` is optional. Many commands (read-only operations, one-way messages) have no meaningful undo. The `execute()` method is the only required operation |
| Java's Runnable/Callable are not Command pattern | They ARE Command pattern implementations. `Runnable` is the `Command` interface; `run()` is `execute()`. `ExecutorService` is the Invoker. Thread pools are a Command queue |
| Command inflates code with too many classes | This is true for simple CRUD operations where undo/queue/log are not needed. Apply Command when at least one of its benefits (undo, queue, audit) is actually needed |
| All commands must be undoable | Only undoable operations need `undo()`. Destructive operations (file delete, email send) may not have a meaningful undo - document this explicitly |

---

### 🚨 Failure Modes & Diagnosis

**1. Undo Stack Grows Unboundedly**

**Symptom:** Text editor memory usage grows steadily over hours. Eventually the heap is exhausted and the application crashes.

**Root Cause:** The undo stack is an `ArrayDeque` with no size limit. Every user action pushes a command. A user working for 4 hours generates tens of thousands of commands, each potentially holding document state snapshots.

**Diagnostic:**
```java
// Add monitoring to the undo stack:
log.info("Undo stack size: {}", undoStack.size());
// If growing without bound: cap needed

// Memory check:
Runtime rt = Runtime.getRuntime();
log.info("Heap used: {}MB",
    (rt.totalMemory() - rt.freeMemory()) / 1024 / 1024);
```

**Fix:**
Cap the undo stack: when it exceeds `MAX_UNDO_LEVELS` (e.g., 100), remove the oldest entry from the bottom. Use `ArrayDeque` with explicit size check, or `LinkedList` with `removeLast()`.

**Prevention:** Design rule: always define `MAX_UNDO_LEVELS` at initialisation time. Treat the undo stack as a fixed-size circular buffer.

---

**2. Stale Receiver Reference in Queued Command**

**Symptom:** A command is queued and executed 2 seconds later. The document it was created to modify has been closed and replaced. The command's `execute()` modifies a closed document, causing `ObjectClosedException`.

**Root Cause:** The command holds a direct reference to the receiver. If the receiver's lifecycle ends before the command executes, the reference becomes stale.

**Diagnostic:**
```java
// Check receiver validity before execution:
@Override
public void execute() {
    if (document.isClosed()) {
        log.warn("Skipping command: document closed");
        return;
    }
    // ... execute action
}
```

**Fix:**
Commands should validate receiver state at execution time. For distributed commands, use IDs (not references) and resolve the receiver at execution time from a live registry.

**Prevention:** Commands targeting long-lived resources should store IDs + resolve via repository. Commands targeting short-lived objects should check liveness before acting.

---

**3. Non-Idempotent Command Executed Twice**

**Symptom:** An amount is debited twice from a customer account after a network retry. The payment command was retried because the first acknowledgment was lost.

**Root Cause:** The payment command is not idempotent. Re-executing it produces a side effect (duplicate debit) even though the first execution succeeded.

**Diagnostic:**
```bash
# Check command execution logs for duplicate IDs:
grep "command_id=abc123" application.log
# Two "executed" entries for the same ID = duplicate execution
```

**Fix:**
Add a unique command ID. Before executing, check if this ID was already processed:
```java
if (commandLog.wasExecuted(command.getId())) {
    log.info("Skipping duplicate: {}", command.getId());
    return;
}
commandLog.markExecuted(command.getId());
command.execute();
```

**Prevention:** All externally-triggered commands (from queues, APIs) must be idempotent or use deduplication by command ID.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Encapsulation` - Command encapsulates a request with all its context; understanding what encapsulation means for behaviour (not just data) is required
- `Interface` - the `Command` interface is the abstraction that enables Invokers to work with any command type without knowing its concrete class
- `Queue Data Structure` - command queuing relies on FIFO structures; understanding queue semantics drives correct task queue design

**Builds On This (learn these next):**
- `Memento` - frequently paired with Command for undo/redo; Memento captures the state snapshot that Command's `undo()` restores
- `Event Sourcing` - architectural-scale Command: every state change is stored as an immutable command (event); replaying events rebuilds state
- `Task Queue / Message Queue` - the distributed form of Command queuing; Kafka, RabbitMQ, and SQS are Command queues at scale

**Alternatives / Comparisons:**
- `Strategy` - encapsulates an algorithm, not a request; Strategies are swapped, not stored or undone
- `Chain of Responsibility` - routes a request through conditional handlers; doesn't encapsulate the request as an object for storage
- `Memento` - captures state for restoration; Command captures the action that caused the state change (complementary, not competing)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A request wrapped as an object with all  │
│              │ context needed to execute, queue, or undo│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Actions called directly cannot be stored │
│ SOLVES       │ deferred, audited, or reversed           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Command separates WHAT to do from WHEN   │
│              │ and WHERE it executes                     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Actions need undo/redo, queuing, logging, │
│              │ retry, or deferred execution              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Actions are simple, immediate, not undone;│
│              │ overhead of a class per operation is high │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Undo + queue + audit vs class proliferation│
│              │ and state-capture complexity              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrap the action in a box - open it       │
│              │  whenever, wherever, however you need."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Memento → Event Sourcing →                │
│              │ Task Queue                                │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Encapsulate a request as an independent object. This separates
the *what* (the command object) from the *when* and *where*
(the invoker and timing). Commands become first-class values:
storable, serialisable, queueable, and replayable.

**Where else this pattern appears:**
- **Message queues (Kafka, RabbitMQ):** Messages are
  serialised Command objects sent asynchronously to consumers
  -- the producer issues the command; the consumer executes it
  at its own pace.
- **SQL transactions:** BEGIN → commands (INSERT, UPDATE) →
  COMMIT forms a command log -- transactions can be replayed
  from the log, which is how replication works.
- **CI/CD pipelines:** Each pipeline stage (build, test, deploy)
  is a Command object -- stages are queued, retried, and their
  output stored independently of execution order.

---

### 💡 The Surprising Truth

Java's `Runnable` and `Callable` interfaces are stripped-down
Command objects -- they encapsulate "a unit of work" as an
object that can be passed to an `Executor`. Every
`ExecutorService.submit(Runnable)` call is therefore a Command
pattern instantiation at the system level. The `Future`
returned represents the command's eventual result. This means
Java's concurrency model is built on Command, and every
`CompletableFuture` chain is a composed sequence of Command
objects -- a fact rarely acknowledged when teaching `Runnable`
to beginners.
---

### 🧠 Think About This Before We Continue

**Q1.** A text editor uses Command+Memento for undo. A user types 10,000 characters in one session. Each `TypeCommand` stores the full document snapshot in its Memento before executing so that `undo()` can restore it. Calculate the memory used by the undo stack if the document averages 50 KB after each keypress. Then redesign the state capture strategy to reduce memory usage by at least 10× without sacrificing undo correctness.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** An e-commerce platform implements order placement as a Command queued to Kafka. The `PlaceOrderCommand` includes: deduct inventory, charge payment, create shipping label. Network failure occurs between the payment charge and the shipping label creation. The command is retried by Kafka. Trace exactly which operations execute on the second attempt, which produce duplicate effects (and what the user experiences), and describe an idempotency mechanism that prevents the double-charge without making the command non-retryable.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** An order processing system uses
Command pattern with undo. An `PlaceOrderCommand.undo()` must
reverse a `PaymentCharge`, a `StockReservation`, and an
`EmailConfirmation`. The email was already sent.
What are the fundamental limits of undo for commands with
irreversible side effects, and what alternative pattern
addresses this without breaking the Command interface?

*Hint: Look at the WHAT CHANGES AT SCALE section and the
Failure Modes -- the Saga pattern (DPT-054) exists precisely
because "compensation" (not true undo) is required for
distributed irreversible actions.*
