---
layout: default
title: "Command Pattern"
parent: "Design Patterns"
nav_order: 779
permalink: /design-patterns/command-pattern/
number: "779"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Strategy Pattern, Queue Data Structure"
used_by: "Undo/redo, Job queues, Transaction scripts, Macro recording"
tags: #intermediate, #design-patterns, #behavioral, #oop, #undo-redo, #queuing
---

# 779 — Command Pattern

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#undo-redo` `#queuing`

⚡ TL;DR — **Command** encapsulates a request as an object — decoupling the sender from the receiver, enabling queuing, logging, and undoable operations by packaging all information needed to perform an action (what to do, on what, with what parameters) into a standalone object.

| #779 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Strategy Pattern, Queue Data Structure | |
| **Used by:** | Undo/redo, Job queues, Transaction scripts, Macro recording | |

---

### 📘 Textbook Definition

**Command** (GoF, 1994): a behavioral design pattern that encapsulates a request as an object, thereby allowing you to parameterize clients with different requests, queue or log requests, and support undoable operations. Components: **Command** (interface with `execute()`), **ConcreteCommand** (implements Command, holds receiver + stores parameters), **Receiver** (object that performs the work), **Invoker** (triggers the command, may queue/log), **Client** (creates ConcreteCommand with receiver). GoF intent: "Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations." Also implements: transactional behavior (can roll back), job queues, task scheduling, macro recording.

---

### 🟢 Simple Definition (Easy)

A restaurant order ticket. The waiter (invoker) takes your order (command object: "2 burgers, 1 salad, table 5"). The ticket is passed to the kitchen (receiver). The kitchen executes: makes 2 burgers, 1 salad. The waiter doesn't cook. The kitchen doesn't need to talk to the customer. The ticket (command) decouples the orderer from the cook. Bonus: tickets can be queued (busy kitchen), logged (you can review what was ordered), and potentially cancelled (command can be removed from queue before execution).

---

### 🔵 Simple Definition (Elaborated)

A text editor's undo/redo stack. Each edit is a `Command` object: `InsertTextCommand(text="Hello", position=0)`, `DeleteTextCommand(text="World", position=6)`. Executing adds to an undo stack. Pressing Ctrl+Z: pop last command, call `command.undo()`. Each command knows how to reverse itself: `InsertTextCommand.undo()` deletes the inserted text. `DeleteTextCommand.undo()` re-inserts the deleted text. Without Command pattern, implementing undo would require complex state snapshots — with Command, each command encapsulates its own reversal logic.

---

### 🔩 First Principles Explanation

**How Command enables undo/redo and queuing:**

```
COMMAND PATTERN STRUCTURE:

  «interface» Command
  ──────────────────
  +execute(): void
  +undo():    void   // optional — for undoable commands
  
  «class» TextEditor                    «class» InsertCommand implements Command
  ──────────────────────                ──────────────────────────────────────
  +insertText(text, pos): void          -editor: TextEditor
  +deleteText(pos, length): void        -text: String
  +getText(): String                    -position: int
                   ▲                    
                   │ (receiver)         +execute():
                   └─ InsertCommand         editor.insertText(text, position)
                   └─ DeleteCommand     
                                        +undo():
                                            editor.deleteText(position, text.length())
  
  «class» DeleteCommand implements Command
  ──────────────────────────────────────
  -editor: TextEditor
  -position: int
  -length: int
  -deletedText: String  // saved for undo
  
  +execute():
      deletedText = editor.getText(position, length);  // save for undo
      editor.deleteText(position, length);
      
  +undo():
      editor.insertText(deletedText, position);   // restore
  
  «class» CommandHistory (Invoker)
  ─────────────────────────────────
  -history: Deque<Command>    // undo stack
  -undone: Deque<Command>     // redo stack
  
  +execute(Command cmd):
      cmd.execute();
      history.push(cmd);
      undone.clear();   // new command clears redo stack
      
  +undo():
      if (history.isEmpty()) return;
      Command cmd = history.pop();
      cmd.undo();
      undone.push(cmd);
      
  +redo():
      if (undone.isEmpty()) return;
      Command cmd = undone.pop();
      cmd.execute();
      history.push(cmd);
  
JOB QUEUE / TASK SCHEDULER:

  // Commands as jobs to execute asynchronously:
  interface Job {
      void execute();
  }
  
  class EmailJob implements Job {
      private final String to, subject, body;
      EmailJob(String to, String subject, String body) { ... }
      void execute() { emailService.send(to, subject, body); }
  }
  
  class ReportJob implements Job {
      private final String reportId;
      ReportJob(String reportId) { ... }
      void execute() { reportService.generate(reportId); }
  }
  
  // Queue of commands:
  BlockingQueue<Job> queue = new LinkedBlockingQueue<>();
  
  // Producer:
  queue.put(new EmailJob("user@example.com", "Welcome!", "..."));
  queue.put(new ReportJob("monthly-sales"));
  
  // Worker (invoker):
  Executors.newFixedThreadPool(4).submit(() -> {
      while (true) {
          Job job = queue.take();
          job.execute();
      }
  });
  
  // Worker doesn't know email vs report — just calls execute().
  
COMMAND WITH COMPOSITE (MACRO COMMANDS):

  class MacroCommand implements Command {
      private final List<Command> commands;
      
      MacroCommand(List<Command> commands) { this.commands = commands; }
      
      void execute() { commands.forEach(Command::execute); }
      
      void undo() {
          // Undo in REVERSE order:
          ListIterator<Command> it = commands.listIterator(commands.size());
          while (it.hasPrevious()) it.previous().undo();
      }
  }
  
  // Record a macro:
  MacroCommand macro = new MacroCommand(List.of(
      new InsertCommand(editor, "Hello", 0),
      new InsertCommand(editor, " World", 5),
      new BoldTextCommand(editor, 0, 5)
  ));
  
  history.execute(macro);  // executes all 3 as one undoable unit
  history.undo();          // undoes all 3 in reverse
  
COMMAND IN SPRING (various forms):

  // 1. ApplicationEvent + @EventListener = Command + Observer combo:
  //    Events are command-like objects published and handled asynchronously.
  
  // 2. @Async methods: Spring wraps them in Callable/Runnable (Command).
  
  // 3. Spring Batch Step/Job: each step is a Command with execute() and rollback().
  
  // 4. CompletableFuture: the task passed to supplyAsync() is a Command.
  
COMMAND vs STRATEGY:

  Both: encapsulate behavior as an object.
  
  Strategy:  Defines HOW to do something (algorithm). 
             Injected into a class to vary algorithm behavior.
             No notion of "execute once and remember."
             
  Command:   Defines WHAT to do and to whom, with what params.
             Designed to be stored, queued, logged, undone.
             Encapsulates a specific ACTION with its state.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Command:
- Undo: complex state snapshots of entire application state for each operation
- Job queue: `if (action.equals("email")) sendEmail(to, subject)` — switch/case in worker

WITH Command:
→ Each operation encapsulates its own undo logic; undo stack is just a `Deque<Command>`
→ Worker calls `job.execute()` — never knows if it's email, report, or any other type

---

### 🧠 Mental Model / Analogy

> A pizza delivery ticket. Customer tells the counter: "Large pepperoni, extra cheese, apartment 3B." Counter writes a ticket (command). Ticket is passed to the kitchen. Kitchen reads the ticket, makes the pizza. Counter can review tickets (log), cancel a ticket before kitchen starts (cancel/dequeue), or re-order the same pizza from the same ticket (re-execute). Customer doesn't talk to the kitchen. Kitchen doesn't need to know who the customer is.

"Order ticket" = Command object (encapsulates: what, who, parameters)
"Counter writes ticket" = client creates Command
"Kitchen reads and makes pizza" = receiver executes
"Passes ticket to kitchen" = invoker enqueues/triggers
"Cancel before kitchen starts" = dequeue command before execute
"Log all tickets" = command log

---

### ⚙️ How It Works (Mechanism)

```
COMMAND FLOW:

  Client creates Command → sets receiver + parameters
  Client passes Command to Invoker (or puts in queue)
  Invoker calls command.execute() → Command delegates to Receiver
  
  UNDO FLOW:
  Invoker pushes command to history stack after execute()
  Undo: invoker.undo() → pops stack → calls command.undo() → Command reverses action on Receiver
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to encapsulate requests for queuing, undo, or deferred execution
        │
        ▼
Command Pattern ◄──── (you are here)
(encapsulate request as object; decouple sender/receiver; enable undo/queue)
        │
        ├── Strategy: similar (behavior as object) but different: no undo/queue semantics
        ├── Chain of Responsibility: CoR can process a queue of Command objects
        ├── Composite: MacroCommand is Composite over Commands
        └── Memento: alternative undo strategy (save/restore state snapshots)
```

---

### 💻 Code Example

```java
// Database operation command with undo support:
interface DatabaseCommand {
    void execute();
    void undo();
    String describe();
}

class InsertUserCommand implements DatabaseCommand {
    private final UserRepository repo;
    private final User user;
    
    InsertUserCommand(UserRepository repo, User user) {
        this.repo = repo;
        this.user = user;
    }
    
    public void execute() { repo.save(user); }
    public void undo()    { repo.deleteById(user.getId()); }
    public String describe() { return "INSERT user: " + user.getEmail(); }
}

class UpdateUserEmailCommand implements DatabaseCommand {
    private final UserRepository repo;
    private final String userId;
    private final String newEmail;
    private String oldEmail;  // saved on execute for undo
    
    UpdateUserEmailCommand(UserRepository repo, String userId, String newEmail) {
        this.repo = repo; this.userId = userId; this.newEmail = newEmail;
    }
    
    public void execute() {
        User user = repo.findById(userId).orElseThrow();
        oldEmail = user.getEmail();  // save for undo
        repo.save(user.withEmail(newEmail));
    }
    
    public void undo() {
        User user = repo.findById(userId).orElseThrow();
        repo.save(user.withEmail(oldEmail));  // restore old email
    }
    
    public String describe() { return "UPDATE user " + userId + " email → " + newEmail; }
}

// Invoker with undo/redo:
class DatabaseCommandHistory {
    private final Deque<DatabaseCommand> history = new ArrayDeque<>();
    
    public void execute(DatabaseCommand cmd) {
        cmd.execute();
        history.push(cmd);
        log.info("Executed: {}", cmd.describe());
    }
    
    public void undoLast() {
        if (!history.isEmpty()) {
            DatabaseCommand cmd = history.pop();
            cmd.undo();
            log.info("Undone: {}", cmd.describe());
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Command Pattern requires undo functionality | Undo is one USE CASE of Command, not required. Command is valuable without undo: job queuing (workers call execute(), don't need undo), logging (record all executed commands), transactional batching. Many Command implementations only have execute(). |
| Command and Strategy are the same | Both encapsulate behavior as an object. Key differences: Strategy: configures HOW an algorithm works (injected into a class, varies the algorithm). Command: captures WHAT ACTION to perform (with specific receiver and parameters), designed to be stored/queued/undone. Strategy is about polymorphism; Command is about parameterized actions. |
| Commands must be synchronous | Command is perfect for async execution. The invoker may put commands in a queue, a thread pool, or a message broker. The receiver executes later — worker thread calls `command.execute()`. This is the basis of Actor model, message queues, and reactive programming: messages (commands) are delivered asynchronously to handlers (receivers). |

---

### 🔥 Pitfalls in Production

**Undo breaking on mutable shared state:**

```java
// ANTI-PATTERN: Command stores reference to mutable object — undo gets wrong state:
class UpdateOrderCommand implements DatabaseCommand {
    private final Order order;   // reference to mutable order
    private String oldStatus;
    
    UpdateOrderCommand(Order order, String newStatus) {
        this.order     = order;
        this.oldStatus = order.getStatus();   // saved AT CREATION TIME
    }
    
    public void execute() { order.setStatus("SHIPPED"); }
    
    public void undo() { order.setStatus(oldStatus); }  // restores status saved at creation
}

// BUG: If someone else changes order.setStatus("CANCELLED") between execute() and undo(),
//      oldStatus still holds "PENDING" — undo restores "PENDING" instead of "CANCELLED".
//      This is a race condition in multi-threaded apps.

// FIX: Save state INSIDE execute() to capture state at execution time, not creation:
public void execute() {
    this.oldStatus = order.getStatus();  // ← save at execute time, not construction time
    order.setStatus("SHIPPED");
}

// ALSO: In distributed systems, commands that reference live mutable objects
// cannot be serialized for queuing. Fix: store only IDs + primitive values:
class UpdateOrderCommand implements DatabaseCommand {
    private final String orderId;    // just the ID — not the live object
    private final String newStatus;
    private String oldStatus;
    
    public void execute() {
        Order order = orderRepo.findById(orderId);  // fresh load from DB
        oldStatus = order.getStatus();
        orderRepo.save(order.withStatus(newStatus));
    }
}
```

---

### 🔗 Related Keywords

- `Strategy Pattern` — encapsulates algorithm (vs Command: encapsulates specific action with state)
- `Chain of Responsibility` — chain may process Command objects sequentially
- `Memento Pattern` — alternative undo strategy: save/restore object state snapshots
- `Composite Pattern` — MacroCommand = Composite of Commands
- `CQRS` — Command Query Responsibility Segregation: Command side uses Command pattern at architectural level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Encapsulate request as object. Decouple   │
│              │ sender from receiver. Enable: queue,     │
│              │ log, undo/redo, transactional batching.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need undo/redo; queuing requests;         │
│              │ logging all operations; transactional    │
│              │ behavior with rollback; task scheduling  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple method calls without need for     │
│              │ queuing or undo; over-engineering one-   │
│              │ shot actions into command objects         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Restaurant ticket: captures order,      │
│              │  passes to kitchen, can be queued,       │
│              │  cancelled, or logged — decouples waiter │
│              │  from cook."                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → Memento Pattern →      │
│              │ Chain of Responsibility → CQRS            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Event sourcing stores all state changes as an immutable log of events (Command objects). To reconstruct current state, replay all events from the beginning. Commands are: `UserRegisteredEvent`, `OrderPlacedEvent`, `PaymentProcessedEvent`. How does the Command pattern relate to event sourcing? In event sourcing, are events the same as commands? What is the distinction between a COMMAND (intent: "do X") and an EVENT (fact: "X happened"), and why does this distinction matter in CQRS architectures?

**Q2.** `java.util.concurrent.Callable<V>` and `Runnable` are Command interfaces in Java — `call()` and `run()` are the `execute()` methods. `ExecutorService.submit(Callable)` queues the command for execution by a thread pool. `Future<V>` is the handle to the result. How does this relate to the Command pattern? What is the "invoker" in this context? What does `Future.cancel(true)` do in terms of Command pattern semantics?
