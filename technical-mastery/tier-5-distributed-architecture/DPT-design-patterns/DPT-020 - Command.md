---
id: DPT-020
title: Command
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-019
used_by: DPT-064, DPT-065
related: DPT-019, DPT-025, DPT-032
tags:
  - pattern
  - behavioral
  - intermediate
  - undo-redo
  - queuing
  - event-sourcing
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/design-patterns/command/
---

⚡ TL;DR - Command encapsulates a request as a first-class
object, decoupling the invoker from the receiver and
enabling undo/redo, queuing, logging, and transactional
operations on requests themselves.

| #20 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-019 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-019, DPT-025, DPT-032 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A text editor has 50 menu items and 30 keyboard shortcuts,
each wired to specific editing operations. Menu item
"Bold" directly calls `editor.toggleBold()`. Keyboard
shortcut Ctrl+Z must undo the last operation, but there
is no record of what the last operation was - only its
side effects on the document. Adding undo requires every
menu action to save its state before changing it, with
save/restore logic scattered across 80 different handlers.

**THE BREAKING POINT:**
Implementing undo/redo requires every operation to know
its inverse. The toolbar, menu bar, and keyboard shortcut
system are all tightly coupled to the editor object. Adding
a new operation (Insert Table) requires wiring it to
menus, shortcuts, and undo/redo in three places.

**THE INVENTION MOMENT:**
Command: instead of calling `editor.toggleBold()` directly,
create a `ToggleBoldCommand` object that CONTAINS the
action. The invoker (button, menu, shortcut) just calls
`command.execute()`. The undo system keeps a stack of
executed commands; `command.undo()` reverses the action.
Macro recording: save a list of commands; replay them.
Commands can be queued, scheduled, logged, serialized,
and transmitted.

**EVOLUTION:**
Java's `Runnable` interface IS the Command pattern:
one method `run()`, encapsulating a unit of work. The
thread pool (Invoker) executes Runnables (Commands) without
knowing what they do. `java.util.concurrent.Callable`
is Command with a return value. Lambda expressions in
Java 8+ are Command implementations. Event sourcing stores
the sequence of Commands (events) as the source of truth.
CQRS splits reads and writes into separate Command and
Query objects.

---

### 📘 Textbook Definition

The **Command** pattern is a Behavioral design pattern that
turns a request into a stand-alone object containing all
information about the request. This transformation allows
passing requests as method arguments, delaying or queuing
a request's execution, and supporting undo/redo operations.
The pattern separates the INVOKER (triggers the command)
from the RECEIVER (executes the action), with the COMMAND
object mediating between them. The Command interface
declares `execute()`, and optionally `undo()`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Command wraps a request in an object so it can be queued,
logged, undone, or scheduled - not just immediately executed.

**One analogy:**
> A restaurant ORDER (Command). The waiter (Invoker) takes
> an order and passes it to the kitchen (Receiver) through
> the order slip (Command object). The chef executes the
> order. The waiter does not know HOW to cook. The order
> slip can be: queued, canceled (undo), used to reorder
> the same dish, given to a different chef, or printed
> on the receipt.

**One insight:**
The "request as an object" transformation is profound:
it makes requests values that can be stored, transmitted,
composed, and inspected - not just function calls that
evaporate after execution.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A Command encapsulates the WHAT (the operation) and
   the CONTEXT (the receiver and parameters needed).
2. The Invoker knows only the Command interface; it does
   not know what the command does or what its receiver is.
3. The Receiver knows nothing about Command or Invoker;
   it has the actual business logic.

**DERIVED DESIGN:**
Four participants:
- **Command interface**: `execute()`, optionally `undo()`
- **ConcreteCommand**: encapsulates action + receiver +
  parameters; stores state for undo
- **Invoker**: holds a command reference; calls `execute()`
  at the right time; may maintain history stack
- **Receiver**: the object with the actual business logic
  (the editor, the robot, the database writer)

**UNDO/REDO STACK:**
```
Invoker maintains: Deque<Command> history, undone
execute(cmd): cmd.execute(); history.push(cmd)
undo():        cmd = history.pop(); cmd.undo();
  undone.push(cmd)
redo():        cmd = undone.pop(); cmd.execute();
  history.push(cmd)
```

**TRADE-OFFS:**

**Gain:** Undo/redo. Request queuing. Logging and auditing
of executed commands. Macro recording (list of commands).
Deferred execution. Support for transactional command
sequences.

**Cost:** Proliferation of small Command classes (one per
operation) - mitigated by lambdas in Java 8+. Implementing
`undo()` correctly requires saving pre-operation state,
which can be complex for operations with many side effects.
Undo may be impossible for some operations (sent emails,
charged payments).

---

### 🧪 Thought Experiment

**SETUP:**
A text editor operation history. User types 5 characters
"Hello", bolds them, then undoes twice (should become
"Hello" in regular weight, then empty again).

**WITHOUT COMMAND:**
Undo is impossible because the direct calls (`appendText`,
`toggleBold`) left no record of what was done or how to
reverse it.

**WITH COMMAND:**
History stack: [AppendCommand("Hello"), BoldCommand(0,5)]
First undo: `BoldCommand.undo()` removes bold → text is "Hello" (plain)
Stack: [AppendCommand("Hello")] (BoldCommand moved to undo stack)
Second undo: `AppendCommand.undo()` removes "Hello" → text is ""
Stack: [] (empty)

**THE INSIGHT:**
Each Command stores the minimal state needed to reverse
itself. `BoldCommand` stores: the selection range and
previous bold state. `AppendCommand` stores: what was
appended and the cursor position before appending. The
undo system does not need to understand text formatting;
it just pops Commands and calls `undo()`.

---

### 🧠 Mental Model / Analogy

> Command is a WORK ORDER SYSTEM. Instead of a supervisor
> directly telling workers what to do (coupling supervisor
> to worker), the supervisor writes a work order (Command).
> Workers execute work orders. Orders can be: prioritized
> (queue), canceled (undo), repeated (redo), assigned to
> any qualified worker (Receiver), logged for audit, or
> scheduled for tomorrow (deferred execution). The supervisor
> does not know which specific worker will do the job.

- "Supervisor" = Invoker
- "Work order" = Command object
- "Worker" = Receiver
- "Cancel order" = undo()
- "Repeat order" = redo() or re-execute

**Where this analogy breaks down:**
Physical work orders are usually non-reversible (you cannot
un-build something). Command pattern's power is precisely
undo() - making operations reversible by storing enough
context to reverse them. Not all digital commands are
reversible either (sending an email cannot be undone).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Command is the idea of "saving what you want to do as
an object" so you can do it later, undo it, queue it,
or repeat it. Instead of immediately doing the thing,
you write it down (create a Command object) and execute
it when ready.

**Level 2 - How to use it (junior developer):**
Create a `Command` interface with `execute()`. Create one
class per operation: `AddItemCommand`, `RemoveItemCommand`,
etc. Each command holds a reference to the receiver (the
object that does the actual work) and the parameters.
An Invoker (button, scheduler) calls `execute()` on
the command without knowing what it does.

**Level 3 - How it works (mid-level engineer):**
`java.lang.Runnable` is the simplest Command interface:
one method `run()`, no return value. Every use of a thread
pool (`ExecutorService.submit(runnable)`) is the Command
pattern: the Runnable is the Command, the ExecutorService
is the Invoker, the thread is the Receiver. Lambda functions
in Java ARE Commands: `executor.submit(() -> processOrder(order))`
- the lambda is a `Runnable` Command with the `order`
parameter captured in a closure.

**Level 4 - Why it was designed this way (senior/staff):**
Command is what makes event sourcing possible. In event
sourcing (CQRS/ES systems): each state change is stored
as a Command object (event) in an append-only log. To
reconstruct current state: replay all commands from the
log. To audit: inspect the log. To undo: replay commands
up to the desired point. Kafka topics are effectively
Command logs. The event sourcing pattern (which is critical
to financial systems, audit-heavy domains, and temporal
queries) is built on the Command pattern applied to
persistent storage.

**Level 5 - Mastery (distinguished engineer):**
CQRS (Command Query Responsibility Segregation) applies
the Command pattern at the architectural level: WRITES
are Commands (change state, no return value); READS are
Queries (return state, no side effects). Commands flow
through a command bus to command handlers. The command
handler returns either success/failure or domain events.
Domain events are the Command RESULT objects that update
the read model. Axon Framework, MediatR, and Spring CQRS
implementations all follow this: command buses dispatch
typed command objects to handlers, enabling routing,
validation, authorization, and auditing as chain-of-
responsibility handlers before the actual command handler.

---

### ⚙️ How It Works (Mechanism)

```
Command Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ <<interface>>                                           │
│ Command                                                 │
│ + execute(): void                                       │
│ + undo(): void       ← optional                         │
│                                                         │
│ ConcreteCommand implements Command                      │
│ - receiver: Receiver                                    │
│ - params: ...        ← needed to execute + undo         │
│ + execute(): void    ← calls receiver.action(params)    │
│ + undo(): void       ← calls receiver.reverseAction()   │
│                                                         │
│ Invoker                                                 │
│ - command: Command                                      │
│ - history: Deque<Command>                               │
│ + setCommand(cmd): void                                 │
│ + executeCommand(): void                                │
│   history.push(command); command.execute();             │
│ + undoLast(): void                                      │
│   cmd = history.pop(); cmd.undo();                      │
│                                                         │
│ Receiver                                                │
│ + action(params): void   ← actual business logic        │
│ + reverseAction(): void  ← undo logic                   │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TEXT EDITOR COMMAND FLOW:**
```
User presses Ctrl+B (Bold):
  → KeyboardShortcutInvoker creates BoldCommand(editor,
    selection)
  → invoker.executeCommand(boldCmd):
      history.push(boldCmd)
      boldCmd.execute()
        → editor.applyBold(selection) ← actual formatting

User presses Ctrl+Z (Undo):
  → invoker.undoLast():
      boldCmd = history.pop()
      boldCmd.undo()
        → editor.removeBold(selection) ← reversal

User presses Ctrl+Y (Redo):
  → invoker.redo():
      boldCmd from undone stack
      boldCmd.execute() ← re-apply bold
      history.push(boldCmd)
```

**THREAD POOL COMMAND FLOW:**
```
Producer creates: Runnable task = () -> processOrder(order)
ExecutorService (Invoker):
  → submit(task): adds to work queue
  → Worker thread (Receiver) picks up task from queue
  → task.run() executes: processOrder(order)
Producer knows nothing about which thread ran the task
```

---

### 💻 Code Example

**Example 1 - Without Command (tight coupling, no undo):**

```java
// BAD: invoker directly calls receiver methods
class TextEditorToolbar {
    private TextEditor editor;

    // Button click directly calls receiver - no undo possible
    public void onBoldButtonClick() {
        editor.toggleBold(); // no state saved before change
    }

    public void onUndoButtonClick() {
        // How? We don't know what to undo!
        // editor doesn't track what happened
    }
}
```

**Example 2 - Command pattern for undo/redo:**

```java
// GOOD: Command encapsulates action + undo capability

interface Command {
    void execute();
    void undo();
}

// Concrete command: knows what to do and how to undo it
class BoldCommand implements Command {
    private final TextEditor editor;
    private final int start;
    private final int end;
    private boolean previousBoldState; // for undo

    BoldCommand(TextEditor editor, int start, int end) {
        this.editor = editor;
        this.start = start;
        this.end = end;
    }

    @Override
    public void execute() {
        // Save state BEFORE changing it
        previousBoldState = editor.isBold(start, end);
        editor.setBold(start, end, true);
    }

    @Override
    public void undo() {
        // Restore previous state
        editor.setBold(start, end, previousBoldState);
    }
}

class AppendTextCommand implements Command {
    private final TextEditor editor;
    private final String text;
    private int insertedAt; // cursor position for undo

    AppendTextCommand(TextEditor editor, String text) {
        this.editor = editor;
        this.text = text;
    }

    @Override
    public void execute() {
        insertedAt = editor.getCursorPosition();
        editor.insertText(insertedAt, text);
    }

    @Override
    public void undo() {
        editor.deleteText(insertedAt, text.length());
    }
}

// Invoker: orchestrates commands, maintains history
class EditorHistory {
    private final Deque<Command> history = new ArrayDeque<>();
    private final Deque<Command> undone = new ArrayDeque<>();

    public void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
        undone.clear(); // redo stack cleared on new action
    }

    public void undo() {
        if (!history.isEmpty()) {
            Command cmd = history.pop();
            cmd.undo();
            undone.push(cmd);
        }
    }

    public void redo() {
        if (!undone.isEmpty()) {
            Command cmd = undone.pop();
            cmd.execute();
            history.push(cmd);
        }
    }
}

// Usage: toolbar calls history.execute(new BoldCommand(...))
EditorHistory history = new EditorHistory();
history.execute(new AppendTextCommand(editor, "Hello"));
history.execute(new BoldCommand(editor, 0, 5));
history.undo(); // removes bold
history.undo(); // removes "Hello"
history.redo(); // re-inserts "Hello"
```

**Example 3 - Thread pool as Invoker (Runnable as Command):**

```java
// RECOGNITION: Runnable IS the Command interface

// Command interface: java.lang.Runnable { void run(); }

// Concrete command as lambda (Java 8+)
Runnable processOrderCmd = () -> {
    // Receiver logic inline (or delegate to receiver)
    orderProcessor.process(order);
    auditLogger.log("ORDER_PROCESSED", order.id());
};

// Invoker: ExecutorService
ExecutorService executor = Executors.newFixedThreadPool(4);
executor.submit(processOrderCmd); // Queue for async execution

// Invoker does not know what processOrderCmd does
// It just knows: Runnable has run()
// This IS the Command pattern - lambda = ConcreteCommand
```

**Example 4 - Command queue for transactional operations:**

```java
// Macros: list of commands replayed as a unit
class MacroCommand implements Command {
    private final List<Command> commands = new ArrayList<>();

    public void addCommand(Command cmd) {
        commands.add(cmd);
    }

    @Override
    public void execute() {
        for (Command cmd : commands) {
            cmd.execute();
        }
    }

    @Override
    public void undo() {
        // Undo in REVERSE order
        ListIterator<Command> it =
            commands.listIterator(commands.size());
        while (it.hasPrevious()) {
            it.previous().undo();
        }
    }
}

// Create a macro: "Center + Bold + Increase Font"
MacroCommand format = new MacroCommand();
format.addCommand(new CenterCommand(editor, selection));
format.addCommand(new BoldCommand(editor, selection));
format.addCommand(new FontSizeCommand(editor, selection, 16));
history.execute(format); // execute all 3 as one unit
history.undo();          // undo all 3 in reverse order
```

**How to test/verify correctness:**
Test `execute()`: verify receiver state changes correctly.
Test `undo()`: after `execute()`, call `undo()`, verify
state is identical to before `execute()`. Test redo:
execute, undo, redo - final state equals post-execute state.
Test MacroCommand: all sub-commands execute in order;
all sub-commands undo in reverse order.

---

### ⚖️ Comparison Table

| Pattern | Request as object | Undo support | Queue support | Who invokes |
| --- | --- | --- | --- | --- |
| **Command** | Yes | Yes (undo()) | Yes | Invoker (decoupled) |
| Chain of Resp. | No (passes through) | No | N/A | First handler |
| Strategy | No (algorithm only) | No | No | Client directly |
| Observer | No (notification) | No | No | Publisher |

**How to choose:**
- Need undo/redo, queuing, logging of requests as objects:
  Command
- Need to pass a request through multiple handlers in a
  pipeline: Chain of Responsibility
- Need to select between algorithms at runtime: Strategy
- Need to notify multiple parties of a state change: Observer

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Runnable is not a design pattern | Runnable IS Command: `interface Runnable { void run(); }` is the Command interface; every thread pool submission is an Invoker passing a Command to a Receiver (the thread) |
| Command must be a separate class | In Java 8+, lambda expressions ARE Commands - `() -> doSomething()` is a Runnable/Command. Using lambdas reduces the "class explosion" concern of Command |
| Command and Strategy look the same | Strategy: one algorithm is SELECTED from multiple alternatives at runtime. Command: an action is ENCAPSULATED as an object for later/repeated/undoable execution. Strategy = which algorithm; Command = which action to record |
| Undo means going to a previous saved state | Command's undo is NOT a full state snapshot (too expensive). Each ConcreteCommand stores only the DELTA it applied - the minimum needed to reverse itself. This is the efficiency advantage of Command-based undo over full state snapshots |
| CQRS is unrelated to Command pattern | CQRS directly applies Command pattern: "Commands" in CQRS are Command objects (PlaceOrderCommand, UpdatePriceCommand). CQRS is the Command pattern applied to the architecture of an entire application |

---

### 🚨 Failure Modes & Diagnosis

**Undo/Redo Stack State Corruption - Non-reversible Operations**

**Symptom:**
User undoes "Send Email" command - the email was already
sent; undo "removes" the email from the history but the
recipient already received it. The history stack is correct
but the real-world side effect cannot be reversed.

**Root Cause:**
`SendEmailCommand.undo()` was implemented to remove the
entry from a log, but the actual email in the recipient's
inbox cannot be recalled. The command has a non-reversible
side effect.

**Diagnostic Signal:**
Any command that interacts with external systems (email,
payment, SMS, file system on other machines) has potentially
non-reversible side effects.

**Fix:**
Option 1: Make `SendEmailCommand` not undoable - throw
`UnsupportedOperationException` in `undo()` and gray
out the Undo button in the UI when this command is on top.
Option 2: "Send on delay" pattern: `SendEmailCommand.execute()`
schedules the email for 30 seconds; `undo()` cancels the
scheduled send if called within 30 seconds (Gmail's
"Undo Send" works exactly this way).
Option 3: Mark commands with `isUndoable() → boolean`;
Invoker checks before adding to undo stack.

---

**Command Class Explosion in Large Applications**

**Symptom:**
A CRUD application with 40 entity types implements 4
commands per entity (Create, Update, Delete, Archive):
160 command classes. The repository has 160 near-identical
files. Adding a new entity requires creating 4 new command
classes. Maintenance overhead is high.

**Root Cause:**
The pattern was applied too literally. Modern Java can
use lambdas and generics to avoid individual command
classes for simple CRUD operations.

**Fix:**
```java
// BAD: one class per operation
class CreateUserCommand implements Command {
    public void execute() { userRepo.save(user); }
    public void undo() { userRepo.delete(user.id()); }
}

// GOOD: generic command with lambda operations
class ReversibleCommand implements Command {
    private final Runnable execute;
    private final Runnable undo;

    ReversibleCommand(Runnable execute, Runnable undo) {
        this.execute = execute;
        this.undo = undo;
    }

    @Override public void execute() { execute.run(); }
    @Override public void undo() { undo.run(); }
}

// Usage: no new class per operation
Command createUser = new ReversibleCommand(
    () -> userRepo.save(user),
    () -> userRepo.delete(user.id())
);
history.execute(createUser);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Chain of Responsibility` - understand request pipelines
  before Command; the two are commonly used together
  (commands pass through a validation CoR before executing)

**Builds On This (learn these next):**
- `CQRS Pattern` - DPT-052; Command pattern applied
  at the architectural level; writes are Commands, reads
  are Queries; understand Command first
- `Producer-Consumer Pattern` - DPT-032; command queues
  use the producer-consumer pattern for async execution

**Alternatives / Comparisons:**
- `Chain of Responsibility` - CoR: request moves through
  pipeline; Command: request encapsulated as object for
  deferred execution
- `Strategy` - Strategy selects an algorithm; Command
  encapsulates an action for recording/queuing

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Request as a first-class object;         │
│              │ enables undo/redo, queue, log, defer     │
├──────────────┼──────────────────────────────────────────┤
│ 4 PARTS      │ Command (iface), ConcreteCommand,        │
│              │ Invoker (triggers), Receiver (acts)      │
├──────────────┼──────────────────────────────────────────┤
│ JAVA EXAMPLE │ Runnable = Command interface             │
│              │ ExecutorService = Invoker (thread pool)  │
├──────────────┼──────────────────────────────────────────┤
│ UNDO RULE    │ Store pre-operation state in the command │
│              │ Undo reverses the delta, not full state  │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Non-reversible operations (email sent,   │
│              │ payment charged) cannot be undone -      │
│              │ mark commands as non-undoable explicitly │
├──────────────┼──────────────────────────────────────────┤
│ MODERN JAVA  │ Lambda = ConcreteCommand; reduces class  │
│              │ explosion for simple operations          │
├──────────────┼──────────────────────────────────────────┤
│ ARCH LEVEL   │ CQRS = Command pattern applied to system │
│              │ architecture (writes = Commands)         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Iterator → Mediator → Memento → Observer │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `Runnable` IS the Command interface - every thread pool
   submit is Command pattern in action; lambdas are modern
   ConcreteCommands in Java
2. Command's undo stores ONLY THE DELTA to reverse: what
   changed and the previous value - not a full snapshot.
   Full snapshots are Memento, not Command
3. CQRS applies Command pattern at architecture level:
   writes are Commands dispatched to handlers; reads are
   Queries; the split enables independent scaling and
   separate read/write models

**Interview one-liner:**
"Command encapsulates a request as an object, decoupling
the invoker from the receiver and enabling undo/redo, queuing,
and logging. Java's Runnable IS the Command interface - every
ExecutorService submission uses Command pattern. CQRS applies
it architecturally: writes are Commands dispatched to handlers,
reads are Queries."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When an operation needs to be: deferred (scheduled or
queued), recorded (audited or logged), repeated (macro or
retry), or reversed (undo/redo), turn the operation into a
first-class object. This is Command's transformation.
"Operations as objects" is the same insight that enables
functional programming, event sourcing, and CQRS at
progressively larger scales.

**Where else this pattern appears:**
- **Event Sourcing** - domain events ARE commands: each
  represents an operation that changed state.
  `OrderPlaced(orderId, items, total, timestamp)` is a
  Command. Replaying events = calling execute() on each.
  The event log IS the command history stack.
- **Java's CompletableFuture** - `CompletableFuture.supplyAsync(
  supplier)` submits a Supplier (Command variant with
  return value) to the ForkJoinPool (Invoker). The result
  is a future that holds the Command's outcome.
- **Database Transaction Log** - every SQL operation in
  a transactional database is logged as a Command record
  (the WAL - Write-Ahead Log). Transaction rollback =
  applying Command undo operations from the log.

**Industry applications:**
- **Axon Framework (CQRS/ES)** - `@CommandHandler` methods
  are Receivers; command objects (PlaceOrderCommand,
  CancelOrderCommand) are Commands; the CommandGateway
  is the Invoker; Axon's command bus routes to the handler
- **Spring Batch** - each `ItemWriter.write()` call is a
  Command; the `Step` is the Invoker; Spring Batch's
  retry/skip mechanism re-executes or skips failed Commands
- **Kubernetes operators** - a controller's reconciliation
  loop issues Commands (create Pod, update Service, delete
  Deployment); the API server is the Invoker; etcd stores
  the desired state as a Command log

---

### 💡 The Surprising Truth

Gmail's "Undo Send" feature is implemented using the
Command pattern - but with a crucial insight. When you
click Send, Gmail does NOT immediately send the email.
Instead, it creates a `SendEmailCommand` and schedules
it for execution 5-30 seconds in the future (the delay
you configure). If you click "Undo" within that window,
the scheduled command is canceled - the email is never
sent. This is NOT the traditional "undo after execution"
approach: it is "delay execution to enable undo." The
Command pattern makes this natural: `execute()` schedules
a future task; `undo()` cancels the scheduled task. After
the delay elapses, `execute()` actually sends. The email
in your Sent folder is the Command; the delay is the
window for undo; the cancellation is the undo. Most
email clients implement this exactly this way.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Explain why `java.lang.Runnable` is the
   Command pattern, naming the Command interface, the
   Invoker, and the Receiver in a thread pool example
2. [IMPLEMENT] Implement a text editor command system
   with `AppendCommand`, `DeleteCommand`, and `BoldCommand`
   supporting undo/redo, where each command stores only
   the delta needed to reverse itself
3. [DESIGN] Design a `MacroCommand` that composes a list
   of commands and executes/undoes them as a unit - including
   the correct undo order (reverse of execute order)
4. [APPLY] Explain how CQRS uses the Command pattern
   at the architectural level - name the Command objects,
   Invoker, Receiver, and the analogy to the GoF Command
   participants
5. [DIAGNOSE] Given a `SendEmailCommand` with a `undo()`
   implementation that removes the audit log entry but
   cannot recall the sent email, identify the design
   issue and describe two corrective approaches

---

### 🧠 Think About This Before We Continue

**Q1.** The Command pattern separates Invoker from Receiver.
In a typical Spring MVC application: a controller method
calls a service directly (`orderService.placeOrder(order)`).
Is this already the Command pattern? If not, what would
need to change to make it Command-compliant?

*Hint: No - this is NOT Command pattern. The controller
(potential Invoker) directly calls the service (Receiver)
with no Command object mediating. The call is immediate
with no undo/queue/log capability. To apply Command:
create a `PlaceOrderCommand` object with the order data,
pass it to a CommandBus (Invoker), which routes to
`OrderCommandHandler.handle(PlaceOrderCommand)` (Receiver).
Now: commands can be validated before execution (CoR in
the bus), logged, queued asynchronously, and replayed.
CQRS frameworks (Axon) implement exactly this.*

**Q2.** You implement a database migration tool using
Command pattern. Each migration is a Command with `execute()`
(apply migration) and `undo()` (rollback migration). A
migration at step 7 fails. How does the Command pattern
enable: (1) showing the user which migration failed, (2)
rolling back all migrations from 1-7 in reverse order,
and (3) retrying just step 7 after fixing the issue?

*Hint: (1) Each Command has metadata (migration ID, SQL,
description); the Invoker catches the exception and reports
the failed command's metadata. (2) The Invoker maintains
the executed command stack: migrations 1-6 in history.
After step 7 fails: call undo() on the history stack in
LIFO order: undo(6), undo(5), ..., undo(1). (3) After
fixing the issue: call execute() on step-7 command again
(the command object is still available). This is exactly
how Flyway and Liquibase versioned migrations work -
the migration scripts are Commands.*

---

### 🎯 Interview Deep-Dive

**Q1: How is Java's Runnable related to the Command
design pattern?**

*Why they ask:* Tests ability to recognize patterns in
standard library code - a key senior developer skill.

*Strong answer includes:*
- `java.lang.Runnable` with its single method `void run()`
  IS the Command interface
- `Callable<T>` with `T call()` is Command with a return value
- When you call `executor.submit(runnable)`, the ExecutorService
  IS the Invoker; the thread IS the Receiver; the Runnable
  IS the ConcreteCommand
- The thread pool enables: queuing (work queue), deferred
  execution (scheduled executor), and even batching
- Lambda expressions in Java 8+ are syntactic sugar for
  anonymous Command implementations: `() -> processOrder(o)`
  compiles to a `Runnable`
- `Supplier<T>`, `Consumer<T>`, `Function<T,R>` are all
  Command variants for different execution signatures

**Q2: Describe the Command pattern's role in CQRS
(Command Query Responsibility Segregation).**

*Why they ask:* Tests knowledge of how GoF patterns
scale to architectural patterns in distributed systems.

*Strong answer includes:*
- CQRS directly names its write-path after the Command
  pattern: all state changes are expressed as typed Command
  objects (PlaceOrderCommand, ShipOrderCommand)
- The CommandBus (Invoker) receives commands and routes
  to the appropriate CommandHandler (Receiver)
- Commands contain all data needed to perform the operation
  (the ConcreteCommand's parameters)
- The CommandHandler performs the state change and emits
  Domain Events (the result of the command)
- Benefits: commands can be validated, authorized, logged,
  and queued before reaching the handler (CoR in the bus)
- Commands can be replayed for event sourcing; the command
  log IS the history stack in the GoF pattern
- Queries are separate (no Command, no side effects) -
  enabling independent scaling of read and write paths

**Q3: You need to implement a text editor undo system.
How do you decide whether to use Command-based undo
(store delta) vs Memento-based undo (store full state
snapshot)? What are the trade-offs?**

*Why they ask:* Tests ability to compare two patterns
that both enable undo, with different trade-offs.

*Strong answer includes:*
- Command-based undo: each command stores ONLY the delta
  (what changed, previous value of what changed). Undo
  applies the reverse delta. Memory: O(number of operations).
  Requirement: every command must implement `undo()` that
  correctly reverses its specific change.
- Memento-based undo: before each operation, take a
  snapshot of the ENTIRE state. Undo restores the snapshot.
  Memory: O(snapshot size x number of states) - can be
  very large. Advantage: no need to implement undo() per
  command - just restore the snapshot. Any operation is
  automatically undoable.
- Choose Command-based when: operations are well-defined,
  delta is small relative to total state, and implementing
  undo() per command is feasible (text editors, drawing tools)
- Choose Memento-based when: operations are complex with
  many interrelated changes, or state is small enough
  to snapshot cheaply (game saves, simple form editors)
- Combined approach: periodic full snapshots (Memento)
  plus delta commands between snapshots (Command) - reduces
  both memory and implementation complexity

