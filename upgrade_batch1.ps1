$enc = [System.Text.UTF8Encoding]::new($false)
$base = "C:\ASK\MyWorkspace\sk-keys\docs"

# ─── FILE 001 ───────────────────────────────────────────────────────────────
$f001 = @'
---
layout: default
title: "Imperative Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 1
permalink: /cs-fundamentals/imperative-programming/
number: "0001"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Variables, Control Flow, Functions
used_by: Procedural Programming, Object-Oriented Programming, Functional Programming
related: Declarative Programming, Procedural Programming, Structured Programming
tags:
  - foundational
  - pattern
  - architecture
---

# 0001 — Imperative Programming

⚡ TL;DR — Tell the computer **exactly how** to do something step by step by mutating state with explicit commands.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0001        │ Category: CS Fundamentals — Paradigms │ Difficulty: ★☆☆         │
├──────────────┼───────────────────────────────────────┼─────────────────────────┤
│ Depends on:  │ Variables, Control Flow, Functions    │                         │
│ Used by:     │ Procedural, OOP, Functional           │                         │
│ Related:     │ Declarative, Procedural, Structured   │                         │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Early computers required engineers to hand-wire circuits or write raw binary
machine codes. There was no vocabulary, no structure, no way to express
"add these numbers and store the result." Every computation required knowing
exact opcodes, register addresses, and memory locations. Adding two numbers
meant understanding the entire hardware state at that moment.

THE BREAKING POINT:
As programs grew beyond trivial calculations, the gap between human intent
and machine instructions became unmanageable. Engineers needed a vocabulary
that maps directly to what machines do — but expressed in terms humans can
read, write, and reason about without memorising binary encodings.

THE INVENTION MOMENT:
This is exactly why Imperative Programming was created. It gave engineers
named variables, assignment, loops, and conditionals — a structured
vocabulary that maps one-to-one onto machine instructions while remaining
readable by humans. It was the first bridge between human thought and
machine execution.

### 📘 Textbook Definition

Imperative Programming is a paradigm in which the programmer specifies an
explicit sequence of statements that change the program's state. The program
describes **how** to compute a result through ordered instructions —
assignments, loops, and branches — that directly manipulate named memory
locations. It is the foundational model underlying hardware architecture
and the majority of modern programming languages.

### ⏱️ Understand It in 30 Seconds

**One line:**
Write step-by-step instructions telling the computer exactly what to do and when.

**One analogy:**
> Imperative programming is like turn-by-turn driving directions: "Go straight
> 500m, turn left at the light, turn right into the car park." The driver
> executes every instruction exactly — no judgment, no inference.

**One insight:**
Imperative code is fundamentally about **state changes**. Every assignment,
every loop iteration is a mutation of a value somewhere in memory. The
program IS the ordered history of those mutations — and every bug is an
unexpected or missing mutation somewhere in that sequence.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. State is explicit and mutable — variables hold values that change over time.
2. Execution is sequential — statements run top to bottom unless a branch occurs.
3. Control flow is explicit — the programmer specifies every branch and loop.

DERIVED DESIGN:
Hardware CPUs execute instructions sequentially and read/write memory registers
directly. A language that mirrors this model maps cleanly to machine operations.
Assignment (`x = 5`) becomes a `MOV` instruction. A `for` loop becomes a `CMP`
+ `JMP` instruction pair. The language is a thin, human-readable layer over the
hardware's native sequential execution model.

THE TRADE-OFFS:
Gain: Full, precise control over what happens, when, and in what exact order.
Cost: Complexity grows linearly with state. Tracking every variable's value at
      every moment becomes cognitively expensive as programs scale in size.

### 🧪 Thought Experiment

SETUP:
You want to compute the sum 1 + 2 + 3 + 4 + 5. You have a helper who will
only execute written, step-by-step instructions — no interpretation allowed.

WHAT HAPPENS WITHOUT IMPERATIVE STYLE:
You write "sum(1..5)" and hand it to the helper. They stare at it. There are
no instructions to follow. The expression states an intent but describes no
steps. The helper returns the paper blank.

WHAT HAPPENS WITH IMPERATIVE STYLE:
You write:
  total = 0
  total = total + 1   → total is now 1
  total = total + 2   → total is now 3
  total = total + 3   → total is now 6
  total = total + 4   → total is now 10
  total = total + 5   → total is now 15
The helper executes each line mechanically. After line 6, total = 15.

THE INSIGHT:
Imperative programming converts a desired outcome into an ordered list of
state mutations that any mechanical executor can follow without intelligence,
inference, or understanding of purpose.

### 🧠 Mental Model / Analogy

> Imperative programming is a **cooking recipe**. Each line tells the chef
> (the CPU) exactly what to do: "Boil water. Add pasta. Wait 8 minutes.
> Drain." The chef executes without deciding anything.

"Chef" → CPU / runtime executor
"Recipe step" → program statement / machine instruction
"Pot temperature" → variable / mutable program state
"8 minutes" → loop condition / wait
"Drain" → side effect (mutation observable outside the local scope)

Where this analogy breaks down: unlike a chef, the CPU never misreads or
skips a step — execution is perfectly deterministic every time.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Imperative programming means giving the computer a numbered to-do list and
having it execute every item, in order. Nothing is assumed; everything is stated.

**Level 2 — How to use it (junior developer):**
You write variables to hold data, `if`/`else` to make decisions, `for`/`while`
to repeat steps, and functions to bundle reusable instruction sequences. Java,
Python, C, C++, JavaScript — most languages are imperative by default. You
describe exactly what should happen at each step.

**Level 3 — How it works (mid-level engineer):**
Each statement maps to CPU instructions: `MOV` (assignment), `ADD`/`MUL`
(arithmetic), `CMP` (comparison), `JMP`/`JE`/`JNE` (branch). The program
counter advances through the instruction sequence. Branches modify it; loops
reset it to an earlier address. All values live in registers or named memory
locations that are readable and writable at any point during execution.

**Level 4 — Why it was designed this way (senior/staff):**
Von Neumann architecture stores both program instructions and data in the same
memory, executing sequentially. Imperative programming is the direct software
model of this hardware design. Every alternative paradigm — functional,
declarative, reactive — is a higher abstraction that ultimately compiles to
imperative machine code. Imperative programming is not one paradigm among
equals; it is the substrate on which all other paradigms are built.

### ⚙️ How It Works (Mechanism)

An imperative program executes as a deterministic state machine:

┌──────────────────────────────────────────────┐
│         IMPERATIVE EXECUTION MODEL           │
├──────────────────────────────────────────────┤
│  Program Counter (PC) → instruction[0]       │
│            ↓                                 │
│  Fetch instruction from memory               │
│            ↓                                 │
│  Decode: what operation? what operands?      │
│            ↓                                 │
│  Execute: mutate register or memory          │
│            ↓                                 │
│  Advance PC → instruction[1]                 │
│            ↓                                 │
│  Branch? → update PC to target address       │
│  Loop?   → reset PC to earlier instruction   │
│            ↓                                 │
│  Repeat until HALT or return instruction     │
└──────────────────────────────────────────────┘

**Assignment**: `x = 10` writes the value 10 into the memory slot named `x`.
At the machine level this is a `MOV` instruction targeting a register or
RAM address.

**Sequence**: Statements execute in written order. The program counter
advances by one instruction width after each execution unless modified.

**Branch**: `if (x > 0)` becomes `CMP x, 0` + `JLE skip_block`. One of
two code paths is entered; the other is skipped entirely.

**Loop**: A backwards jump: the program counter resets to an earlier
instruction and re-executes until the condition stops being true.

Everything else — objects, closures, coroutines, exceptions — compiles
down to permutations of these four primitives.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
[Developer writes source code]
→ [Compiler / interpreter translates to instructions]
→ [OS loads program into memory]
→ [CPU fetches instruction[0] ← YOU ARE HERE]
→ [Operands loaded from RAM into registers]
→ [ALU performs operation]
→ [Result written back to memory / register]
→ [PC advances to instruction[1]]
→ [Repeat until program exit]
→ [Output / side effects produced]

FAILURE PATH:
[Incorrect state mutation at step N]
→ [Wrong branch taken at step N+3]
→ [Corrupt data passed to output layer]
→ [Incorrect result / exception / crash]

WHAT CHANGES AT SCALE:
Shared mutable state becomes the primary bottleneck. Multiple threads
simultaneously mutating the same variables produce data races visible only
under load. At 100+ concurrent threads, unguarded imperative mutation
produces non-deterministic, unreproducible results — the fundamental
scaling weakness of the imperative model without synchronisation.

### 💻 Code Example

Example 1 — Basic accumulation (naming matters):

```java
// BAD: opaque variable hides programmer intent
int a = 0;
for (int i = 0; i < nums.length; i++) {
    a = a + nums[i];
}

// GOOD: name reveals the mutation's purpose
int total = 0;
for (int number : nums) {
    total += number; // explicit: we are accumulating
}
System.out.println(total);
```

Example 2 — Shared mutation causes a silent bug:

```java
// BAD: helper mutates caller's list silently
List<String> items = new ArrayList<>();
addDefaults(items);   // mutates items as a side effect
processAll(items);    // sees unexpected items — hard to debug

// GOOD: return new value; caller controls all state
List<String> items = new ArrayList<>();
List<String> withDefaults = addDefaults(new ArrayList<>());
processAll(withDefaults);
```

### ⚖️ Comparison Table

| Paradigm | State | Control | Readability | Best For |
|---|---|---|---|---|
| **Imperative** | Mutable | Explicit step-by-step | Sequential logic | Systems, algorithms |
| Declarative | Often immutable | Implicit (engine decides) | Intent-focused | Queries, config |
| Functional | Immutable | Explicit + pure functions | Mathematical correctness | Data pipelines |
| Object-Oriented | Encapsulated mutable | Message-passing | Domain modelling | Business logic |

How to choose: Use imperative when you need precise control over execution
order and performance. Use declarative or functional styles when correctness
and readability matter more than granular control over every step.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Imperative programming is outdated or inferior | It is the foundation — all paradigms ultimately compile to imperative machine instructions |
| OOP replaces imperative programming | OOP organises imperative code; it does not eliminate mutable state |
| More explicit statements mean more control | Excess statements increase mutation surface area and bug probability |
| Loops are inherently imperative | forEach in functional style uses imperative CPU iteration under the hood |
| Immutable variables make code non-imperative | Immutability constrains state mutation; the execution model remains sequential |

### 🚨 Failure Modes & Diagnosis

**1. Unintended State Mutation**

Symptom: Program produces wrong results intermittently; values change
unexpectedly between method calls with no obvious cause.

Root Cause: A variable is mutated by a code path the developer did not
account for — typically a shared object reference modified inside a helper.

Diagnostic:
```bash
# IntelliJ: Right-click field → Add Field Watchpoint
# Breaks on any write to the field regardless of call site
# With jdb:
jdb -attach 5005
> watch field com.example.MyService counter
```

Fix:
```java
// BAD: helper method mutates caller's collection in place
void addDefaults(List<String> list) {
    list.add("default"); // surprise side effect
}

// GOOD: return new object; caller decides about mutation
List<String> addDefaults(List<String> original) {
    List<String> copy = new ArrayList<>(original);
    copy.add("default");
    return copy;
}
```

Prevention: Treat method arguments as read-only by convention. Return
new values; do not mutate inputs.

**2. Off-by-One Loop Error**

Symptom: Loop processes one element too many or too few; may throw
`ArrayIndexOutOfBoundsException` or silently skip the last element.

Root Cause: Incorrect loop boundary — `<=` instead of `<`, or loop
initialised at 1 instead of 0 for zero-indexed collections.

Diagnostic:
```bash
# Java runtime prints exact line and index:
# java.lang.ArrayIndexOutOfBoundsException: Index 5
# Enable assertions for additional boundary checks:
java -ea MyApplication
```

Fix:
```java
// BAD: i == array.length is out of bounds
for (int i = 0; i <= array.length; i++) {
    process(array[i]); // crashes at i == length
}

// GOOD: i < array.length is always in bounds
for (int i = 0; i < array.length; i++) {
    process(array[i]);
}
```

Prevention: Prefer enhanced for-each loops when the index is not
needed. Always ask: "what is the last valid value of `i`?"

**3. Infinite Loop**

Symptom: Program hangs indefinitely; CPU usage climbs to 100%;
no progress in output or logs.

Root Cause: The loop's termination variable is never updated inside
the loop body, or updated only in a branch that is never taken.

Diagnostic:
```bash
# Find the spinning thread on Linux:
top -H -p $(pgrep -f MyApp)
# Capture thread dump to see which loop is running:
jstack $(pgrep -f MyApp) | grep -B2 -A15 "RUNNABLE"
```

Fix:
```java
// BAD: i never changes; loop runs forever
int i = 0;
while (i < 10) {
    process(i);
    // forgot to write: i++
}

// GOOD: i updated on every iteration
int i = 0;
while (i < 10) {
    process(i);
    i++;
}
```

Prevention: Prefer `for` loops — the update expression (`i++`) is
always visible in the loop header, making it hard to forget.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Variables` — imperative programs are sequences of mutations to named variables
- `Control Flow` — branches and loops are the core control structures of imperative code
- `Functions` — group sequences of statements into named, reusable instruction blocks

**Builds On This (learn these next):**
- `Procedural Programming` — organises imperative code into named, callable procedures
- `Object-Oriented Programming` — encapsulates imperative mutable state inside objects
- `Functional Programming` — constrains and controls mutation to improve correctness

**Alternatives / Comparisons:**
- `Declarative Programming` — describes WHAT to compute, lets the engine decide HOW
- `Structured Programming` — imperative programming with disciplined, goto-free control flow
- `Assembly Language` — imperative programming at the raw machine-instruction level

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Sequence of explicit state-mutating       │
│              │ instructions executed in written order    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Machines need unambiguous, step-by-step   │
│ SOLVES       │ instructions to produce deterministic     │
│              │ results from any input                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every program ultimately executes as      │
│              │ imperative machine instructions —         │
│              │ all paradigms are abstractions on top     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ You need precise control over execution   │
│              │ order, performance, or low-level hardware │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Shared mutable state is your primary bug  │
│              │ source; switch to functional/declarative  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full execution control vs increasing      │
│              │ complexity of reasoning about mutable     │
│              │ state across a large codebase             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell the computer every step — like a    │
│              │ recipe where nothing is left to chance."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Declarative Programming →                 │
│              │ Functional Programming →                  │
│              │ Procedural Programming                    │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A distributed system has 10 services all mutating the same
counter in a shared database using imperative "read-increment-write"
logic. At 100 requests/second it works correctly. At 10,000
requests/second it produces wrong counts. What specific property of
imperative mutation causes this failure, and what does it reveal about
the assumptions the imperative model makes about execution context?

**Q2.** You are designing a language that presents a purely declarative
interface to programmers but compiles to imperative machine instructions.
What invariants of the imperative execution model must your compiler
preserve in every compilation, and what source-level transformations
become impossible because of those invariants?
'@
[System.IO.File]::WriteAllText("$base\CS Fundamentals — Paradigms\001 — Imperative Programming.md", $f001, $enc)
Write-Host "001 done"

# ─── FILE 002 ───────────────────────────────────────────────────────────────
$f002 = @'
---
layout: default
title: "Declarative Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 2
permalink: /cs-fundamentals/declarative-programming/
number: "0002"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming
used_by: Functional Programming, SQL, React, CSS
related: Imperative Programming, Functional Programming, Domain-Specific Languages
tags:
  - foundational
  - pattern
  - architecture
---

# 0002 — Declarative Programming

⚡ TL;DR — Describe **what** you want; let the system figure out **how** to produce it.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0002        │ Category: CS Fundamentals — Paradigms │ Difficulty: ★☆☆         │
├──────────────┼───────────────────────────────────────┼─────────────────────────┤
│ Depends on:  │ Imperative Programming                │                         │
│ Used by:     │ Functional Programming, SQL, React    │                         │
│ Related:     │ Imperative, Functional, DSLs          │                         │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Before declarative interfaces existed, every operation required spelling out
every step. To retrieve records from a database you had to write loops to
scan files, manual comparisons to match conditions, and sorting routines to
order results. You wrote hundreds of lines of imperative code every time
you wanted to ask a question of your data. The "how" completely obscured the "what."

THE BREAKING POINT:
Business users needed to query data. They understood the question ("show me
all orders over $100 from last month") but had no ability to write the loop
logic required to answer it. Even experienced developers spent most of their
time writing mechanical traversal code rather than expressing business logic.

THE INVENTION MOMENT:
This is exactly why Declarative Programming was created. SQL, regular
expressions, HTML, CSS, Kubernetes manifests — they all let you state what
outcome you want and delegate how to achieve it to an engine optimised for
that domain.

### 📘 Textbook Definition

Declarative Programming is a paradigm in which the programmer expresses the
desired result or constraints of a computation without specifying the
step-by-step procedure to achieve it. The underlying execution engine
determines the optimal implementation strategy. Examples include SQL (what
data to retrieve), HTML (what structure to render), CSS (what styles to
apply), and Kubernetes manifests (what cluster state to maintain).

### ⏱️ Understand It in 30 Seconds

**One line:**
State what you want; the system figures out how to give it to you.

**One analogy:**
> Declarative programming is like ordering food at a restaurant. You say
> "I'd like the salmon with salad" — you don't walk into the kitchen and
> instruct the chef step by step. The kitchen figures out the how.

**One insight:**
The power of declarative programming is that it **separates intent from
implementation**. The same SQL query can be optimised differently by
PostgreSQL and MySQL because neither locks you into a specific execution
plan. The "how" is the engine's problem, not yours.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The programmer expresses desired state or result, not procedure.
2. An execution engine interprets the expression and decides how to execute.
3. The same declarative expression may execute differently on different engines.

DERIVED DESIGN:
Because the programmer does not specify control flow, the engine is free to
choose any correct implementation. A SQL query planner can choose between a
full table scan, an index lookup, or a hash join — whichever is faster for
the current data. This optimisation is impossible in imperative code where
the programmer has already committed to one traversal strategy.

THE TRADE-OFFS:
Gain: Expressiveness, readability, engine-level optimisation, and portability.
Cost: Less control over execution path. Performance surprises when the engine
      chooses a strategy you didn't anticipate. Harder to debug "why the
      engine did it this way."

### 🧪 Thought Experiment

SETUP:
You have a list of 10,000 orders. You want those placed in 2024 with total
> $500, sorted by date. You must solve this two ways.

WHAT HAPPENS WITH IMPERATIVE APPROACH:
You write: iterate the list, check year == 2024, check total > 500,
add to result list, then sort by date. 25 lines of code. The database
engine is bypassed entirely; your traversal runs in the application layer.

WHAT HAPPENS WITH DECLARATIVE APPROACH (SQL):
```
SELECT * FROM orders
WHERE YEAR(date) = 2024 AND total > 500
ORDER BY date;
```
3 lines. The database engine decides: use the date index, filter in the
engine, sort using a merge sort on indexed fields. It runs 100x faster
because the engine has context you don't.

THE INSIGHT:
Declarative programming lets domain-specific engines apply optimisations
that are invisible to the programmer — and impossible when the programmer
controls every step.

### 🧠 Mental Model / Analogy

> Declarative programming is like a **restaurant order form**: you tick
> what you want; the kitchen figures out preparation order, timing, and
> technique. You never enter the kitchen.

"Order form" → declarative expression (SQL, CSS, HTML)
"Kitchen" → execution engine (query planner, browser renderer, scheduler)
"Menu item" → declarative construct (SELECT, display:flex, replicas:3)
"Preparation method" → execution plan chosen by the engine
"You never enter the kitchen" → you have no control over execution order

Where this analogy breaks down: you can hint to the engine (SQL hints,
CSS specificity, priority classes) — but cannot fully control it.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Declarative programming means telling the computer what you want without
explaining how to get it. Like specifying the destination on a GPS — you
don't give turn-by-turn directions, the GPS figures out the route.

**Level 2 — How to use it (junior developer):**
SQL, HTML, CSS, React JSX, Kubernetes YAML, Terraform — you write these
declaratively every day. `SELECT name FROM users WHERE active = true` is
declarative. `<Button variant="primary">Submit</Button>` is declarative.
You describe the desired structure or result; the framework builds it.

**Level 3 — How it works (mid-level engineer):**
Under the hood, every declarative expression is parsed into an intermediate
representation (AST or DAG), then compiled or interpreted by an engine into
an imperative execution plan. A SQL query becomes a physical query plan
with specific join algorithms. React JSX becomes a virtual DOM tree that
React's reconciler maps to DOM mutation calls.

**Level 4 — Why it was designed this way (senior/staff):**
The separation of intent from implementation enables independent evolution.
The SQL standard has remained stable for 40 years while database engines
have changed execution strategies radically (columnar storage, vectorised
execution, GPU acceleration). If SQL were imperative, every schema change
would break every query. Declarative interfaces are stable contracts between
user intent and engine capability.

### ⚙️ How It Works (Mechanism)

┌──────────────────────────────────────────────┐
│      DECLARATIVE EXECUTION PIPELINE          │
├──────────────────────────────────────────────┤
│  Declarative expression (SQL / HTML / YAML)  │
│            ↓                                 │
│  Parser → Abstract Syntax Tree (AST)         │
│            ↓                                 │
│  Semantic analysis / validation              │
│            ↓                                 │
│  Optimizer / planner selects strategy        │
│  (indexes, join order, cache, etc.)          │
│            ↓                                 │
│  Execution plan → imperative instructions    │
│            ↓                                 │
│  Engine executes and returns result          │
└──────────────────────────────────────────────┘

The critical step is the **optimizer**: it knows statistics about data
distribution, available indexes, and hardware resources that you do not.
It can choose a plan orders of magnitude faster than a hand-written loop.

**SQL example path**:
`SELECT * FROM orders WHERE total > 500`
→ Parser: AST with SELECT node, WHERE node
→ Planner: finds index on `total` → index scan, not full scan
→ Executor: fetches only matching rows via index
→ Returns result set

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
[Developer writes declarative expression]
→ [Parser validates syntax]
→ [Semantic analyser checks types/schema]
→ [Optimizer selects execution strategy ← YOU ARE HERE]
→ [Engine executes optimised plan]
→ [Result returned to caller]

FAILURE PATH:
[Declarative expression is valid but inefficient]
→ [Optimizer chooses full scan instead of index]
→ [Query runs for 30 seconds instead of 30ms]
→ [Timeout / user impact]

WHAT CHANGES AT SCALE:
At scale the optimizer's decisions dominate performance. A query that
returns 10 rows from 1,000 is fast regardless of strategy. At 100M rows,
the difference between a full scan and an indexed lookup is seconds vs
milliseconds. Declarative interfaces require understanding your engine's
optimiser to avoid performance cliffs.

### 💻 Code Example

Example 1 — Imperative vs declarative data retrieval:

```java
// BAD (imperative): you control every step, engine cannot optimise
List<Order> result = new ArrayList<>();
for (Order o : allOrders) {
    if (o.getYear() == 2024 && o.getTotal() > 500) {
        result.add(o);
    }
}
result.sort(Comparator.comparing(Order::getDate));

// GOOD (declarative SQL): engine optimises with indexes
String sql = """
    SELECT * FROM orders
     WHERE YEAR(date) = 2024
       AND total > 500
     ORDER BY date
    """;
```

Example 2 — Declarative UI with React:

```jsx
// BAD (imperative DOM): you control every mutation
const btn = document.createElement('button');
btn.className = 'btn-primary';
btn.textContent = 'Submit';
btn.disabled = !isValid;
container.appendChild(btn);

// GOOD (declarative JSX): describe desired state
<Button variant="primary" disabled={!isValid}>
  Submit
</Button>
```

Example 3 — Declarative infrastructure (Kubernetes):

```yaml
# Declare desired state — k8s figures out how to achieve it
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3          # I want 3 running instances
  template:
    spec:
      containers:
      - name: api
        image: myapp:1.2.3
```

### ⚖️ Comparison Table

| Style | Who controls "how" | Optimisable | Debug difficulty | Best For |
|---|---|---|---|---|
| **Declarative** | Engine | Yes — engine can change plan | Hard (engine is a black box) | Queries, config, UI structure |
| Imperative | Developer | No — path is fixed in code | Easy (you wrote every step) | Algorithms, performance-critical paths |
| Functional | Developer (constrained) | Partial | Medium | Data transformation pipelines |

How to choose: Use declarative when you trust the engine more than your
own hand-optimised loop, or when the domain has a well-designed DSL (SQL,
HTML, CSS, YAML). Use imperative when you need exact control over execution.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Declarative means no underlying imperative execution | Every declarative expression compiles to imperative machine instructions |
| Declarative code is always faster | A poorly written SQL query can be slower than a good Java loop if it prevents index use |
| You cannot debug declarative code | You can use EXPLAIN PLAN (SQL), browser DevTools (CSS), and diff tools (React) |
| HTML is not a programming language | HTML is a declarative language for describing document structure |
| Declarative = functional | Functional is one flavour of declarative; SQL and HTML are declarative but not functional |

### 🚨 Failure Modes & Diagnosis

**1. Query Optimiser Chooses Wrong Plan (SQL)**

Symptom: Query that was fast in development runs for 30+ seconds in
production. `EXPLAIN` shows a full table scan on a 50M-row table.

Root Cause: Table statistics are stale; optimiser estimates 100 rows but
the actual table has 50M. Or an expression prevents index use (e.g.,
`WHERE YEAR(date) = 2024` prevents the date index from being used).

Diagnostic:
```sql
-- PostgreSQL: see chosen execution plan with actual row counts
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders
 WHERE YEAR(created_at) = 2024 AND total > 500;

-- Update stale statistics
ANALYZE orders;
```

Fix:
```sql
-- BAD: function on indexed column prevents index use
WHERE YEAR(created_at) = 2024

-- GOOD: range condition allows index scan
WHERE created_at >= '2024-01-01'
  AND created_at <  '2025-01-01'
```

Prevention: Always run `EXPLAIN ANALYZE` on queries against large tables.
Avoid wrapping indexed columns in functions.

**2. CSS Specificity Conflict (Declarative UI)**

Symptom: A CSS rule appears correct but another rule overrides it silently.
Style is applied inconsistently across browsers.

Root Cause: CSS specificity determines which rule wins when two rules target
the same element. A more-specific selector always wins regardless of order.

Diagnostic:
```bash
# Chrome DevTools → Elements → Computed tab
# Shows which rule is applied and which are overridden (struck through)
# No CLI tool — use browser inspector
```

Fix:
```css
/* BAD: two rules conflict; which wins? */
.button { color: blue; }
div .button { color: red; }  /* wins — higher specificity */

/* GOOD: use consistent specificity level */
.button { color: blue; }
.button--primary { color: red; }  /* BEM — same specificity */
```

Prevention: Use a naming methodology (BEM, CSS Modules) that keeps all
selectors at the same specificity level.

**3. Kubernetes Desired State Not Converging**

Symptom: `kubectl get pods` shows pods stuck in `Pending` or
`CrashLoopBackOff` despite a valid-looking manifest.

Root Cause: The declared desired state is unachievable — insufficient
node resources, wrong image tag, missing ConfigMap, or failing health check.

Diagnostic:
```bash
kubectl describe pod <pod-name>
# Shows: Events section with exact reason (ImagePullBackOff, OOMKilled, etc.)

kubectl logs <pod-name> --previous
# Shows: crash output from the last container run
```

Fix: Address the specific event cause shown in `kubectl describe`. Common
fixes: add resource limits, correct image tag, create missing secrets.

Prevention: Test manifests in a staging namespace. Use `kubectl dry-run`
before applying to production.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Imperative Programming` — declarative is best understood as the contrast to imperative
- `Domain-Specific Languages` — SQL, CSS, HTML are all declarative DSLs

**Builds On This (learn these next):**
- `Functional Programming` — the most influential form of declarative programming
- `SQL` — the canonical example of a successful declarative language
- `React` — declarative UI: describe desired state, React figures out DOM mutations

**Alternatives / Comparisons:**
- `Imperative Programming` — you control every step; no engine to delegate to
- `Functional Programming` — declarative + pure functions + immutable data
- `Configuration as Code` — declarative infrastructure (Terraform, Ansible)

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Express the desired result; let the       │
│              │ engine decide how to produce it           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Imperative code forces developers to      │
│ SOLVES       │ specify every step, obscuring intent and  │
│              │ preventing engine-level optimisation      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The same declarative expression can be    │
│              │ executed differently on different engines  │
│              │ — the optimiser is the real advantage     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ A trusted engine exists for the domain    │
│              │ (database, browser, orchestrator)         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ You need precise control over the         │
│              │ execution path or cannot trust the engine │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Expressiveness + optimisability vs        │
│              │ less control and opaque execution paths   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Order from the menu — don't enter        │
│              │ the kitchen."                             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SQL → Functional Programming →            │
│              │ React (declarative UI)                    │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A SQL query runs in 50ms on a table with 1M rows. After a data
migration the same query runs in 45 seconds on 10M rows. The schema,
indexes, and query are unchanged. What layer of the declarative
execution pipeline is most likely responsible, and what specific
mechanism caused the degradation?

**Q2.** React re-renders a component tree on every state change, using
a virtual DOM diff algorithm to determine what to actually change in the
real DOM. How does this differ from a purely imperative UI approach, and
what trade-off does React make at 10,000 DOM nodes that makes the
declarative model less attractive?
'@
[System.IO.File]::WriteAllText("$base\CS Fundamentals — Paradigms\002 — Declarative Programming.md", $f002, $enc)
Write-Host "002 done"

# ─── FILE 003 ───────────────────────────────────────────────────────────────
$f003 = @'
---
layout: default
title: "Object-Oriented Programming (OOP)"
parent: "CS Fundamentals — Paradigms"
nav_order: 3
permalink: /cs-fundamentals/object-oriented-programming-oop/
number: "0003"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Imperative Programming, Procedural Programming, Variables, Functions
used_by: Encapsulation, Inheritance, Polymorphism, Abstraction, Design Patterns
related: Functional Programming, Procedural Programming, SOLID Principles
tags:
  - foundational
  - pattern
  - architecture
  - java
---

# 0003 — Object-Oriented Programming (OOP)

⚡ TL;DR — Organise code as a collection of **objects** that bundle data and behaviour together, communicating through well-defined interfaces.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0003        │ Category: CS Fundamentals — Paradigms │ Difficulty: ★★☆         │
├──────────────┼───────────────────────────────────────┼─────────────────────────┤
│ Depends on:  │ Imperative, Procedural, Variables,    │                         │
│              │ Functions                             │                         │
│ Used by:     │ Encapsulation, Inheritance,           │                         │
│              │ Polymorphism, Design Patterns         │                         │
│ Related:     │ Functional, Procedural, SOLID         │                         │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
In large procedural programs, shared global state became the dominant source
of bugs. Any function anywhere in the codebase could read or mutate any
variable. When a bug appeared — wrong customer balance, corrupted order — you
had no reliable way to find which of 500 functions was responsible. Adding a
feature required understanding all existing state to avoid breaking something.

THE BREAKING POINT:
A 100,000-line procedural codebase with 2,000 global variables and 1,000
functions is effectively unmaintainable. No engineer can hold the full state
model in their head. Changes have unpredictable ripple effects. The program
becomes too fragile to evolve.

THE INVENTION MOMENT:
This is exactly why Object-Oriented Programming was created. By bundling data
and the functions that operate on it into a single unit (an object), and
restricting access to that data through defined interfaces, OOP made large
codebases navigable. Each object owns its state and the only way to change
it is through its methods.

### 📘 Textbook Definition

Object-Oriented Programming (OOP) is a paradigm that organises software as
a collection of **objects** — units that encapsulate state (fields) and
behaviour (methods). Objects interact by sending messages (calling methods).
OOP is characterised by four core principles: **Encapsulation** (hiding
internal state), **Inheritance** (deriving specialised types from general
ones), **Polymorphism** (treating objects of different types uniformly
through shared interfaces), and **Abstraction** (exposing only relevant
complexity).

### ⏱️ Understand It in 30 Seconds

**One line:**
Bundle data and the code that works on it into objects with public interfaces.

**One analogy:**
> OOP is like a vending machine. You press a button (call a method). You get
> a snack (result). You cannot reach inside and grab the mechanism directly.
> The internal state is yours to affect only through the defined interface.

**One insight:**
The key insight of OOP is not inheritance or polymorphism — it is
**encapsulation**. By restricting what can touch an object's state, you
drastically reduce the surface area of bugs. When a balance is wrong, only
the `Account` class can be responsible — not any of 1,000 functions.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. An object owns its state — external code cannot directly mutate its fields.
2. Behaviour is co-located with state — methods live on the object they operate on.
3. Objects communicate through interfaces — callers depend on contracts, not implementations.

DERIVED DESIGN:
Given these invariants, large codebases become navigable: to understand what
can change `Account.balance`, you look only at `Account`'s methods. To change
how interest is calculated, you modify one class, not search 1,000 functions.
Polymorphism falls naturally from invariant 3: if callers depend only on an
interface (`Payment`), you can swap implementations (`CreditCard`, `PayPal`)
without changing callers.

THE TRADE-OFFS:
Gain: Encapsulation, maintainability, and reusability at large scale.
Cost: Accidental complexity from deep inheritance hierarchies. Object graphs
      are hard to serialise, parallelise, and test in isolation without
      careful design.

### 🧪 Thought Experiment

SETUP:
A bank application manages 10,000 accounts. Each account has a balance.
Transactions can credit or debit any account. Imagine two implementations.

WHAT HAPPENS WITHOUT OOP (procedural global state):
`balance` is a global `Map<AccountId, Double>`. Any function can write to it.
A bug deposits money twice. You search 300 functions for who wrote to the map.
After two days, you find a loop that ran twice. The map has no concept of
"who is allowed to modify me."

WHAT HAPPENS WITH OOP:
`Account` class has a private `balance` field. The only way to change it is
`account.credit(amount)` or `account.debit(amount)`. Both methods validate
the transaction and log it. The bug immediately narrows: only two methods can
change balance. You find the double-credit in `credit()` in 20 minutes.

THE INSIGHT:
Encapsulation is a bug-surface-area reduction tool. By restricting mutation
to a defined set of methods, OOP makes the search space for bugs proportional
to the object's method count, not the whole codebase.

### 🧠 Mental Model / Analogy

> OOP is a city of **departments in a company**. Each department owns its
> records. If you want HR data, you ask HR through their defined process —
> you don't walk into their filing room and change records yourself.

"Department" → class / object
"Department's records" → private fields / encapsulated state
"Official request process" → public methods / API
"Hiring a specialist role" → inheritance / specialisation
"Any department that can handle invoices" → polymorphism / interface

Where this analogy breaks down: real departments have politics and
inconsistency; objects execute deterministically and enforce access control
perfectly.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OOP means grouping related data and actions together into "objects." A
`Car` object has colour and speed (data) and can `accelerate()` or `brake()`
(actions). You interact with the car through its controls, not by wiring
its engine directly.

**Level 2 — How to use it (junior developer):**
You create classes as blueprints, instantiate objects, call methods, and use
`extends` for specialisation and `implements` for contracts. In Java:
`BankAccount account = new BankAccount(1000); account.debit(200);` — the
internal balance is private; you can only interact through the API.

**Level 3 — How it works (mid-level engineer):**
Objects are memory allocations (heap in Java) with a reference to their class
metadata (vtable for method dispatch). Method calls are dispatched through the
vtable, enabling runtime polymorphism — the JVM resolves which concrete method
to call at runtime based on the actual object type. `final` methods skip vtable
lookup (direct call), which is faster. Interfaces add an extra level of
indirection through an itable.

**Level 4 — Why it was designed this way (senior/staff):**
Simula 67 and Smalltalk invented objects as a modelling tool, not a performance
optimisation. Alan Kay's original vision was message-passing between autonomous
objects — closer to microservices than to modern Java. Java's "everything is a
class" model created the accidental complexity of deep inheritance hierarchies
and the Fragile Base Class problem. The industry reaction is evident in
Go (no inheritance, only composition) and Rust (traits, no class hierarchy).

### ⚙️ How It Works (Mechanism)

┌──────────────────────────────────────────────┐
│         OOP OBJECT LAYOUT IN MEMORY          │
├──────────────────────────────────────────────┤
│  Object Header                               │
│  ├── Mark word (GC/lock info)                │
│  └── Class pointer → vtable                 │
│  ─────────────────────────────────────────  │
│  Instance fields (in declaration order)      │
│  ├── private int balance = 1000             │
│  ├── private String owner = "Alice"         │
│  └── private List<Transaction> history      │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│       METHOD DISPATCH (virtual call)         │
├──────────────────────────────────────────────┤
│  account.credit(200)                         │
│         ↓                                    │
│  Load class pointer from object header       │
│         ↓                                    │
│  Look up credit() in vtable                  │
│         ↓                                    │
│  If account is SavingsAccount → savings impl │
│  If account is CurrentAccount → current impl │
│         ↓                                    │
│  Execute the resolved method                 │
└──────────────────────────────────────────────┘

**Encapsulation** enforced at compile time: `private` fields are rejected
by the compiler if accessed from outside the class. No runtime cost.

**Inheritance**: the subclass vtable extends the parent's vtable. Overridden
methods replace the parent's entry. Calling `super.method()` skips the vtable
and calls the parent entry directly.

**Polymorphism**: callers hold a reference typed as `Payment`. At runtime the
JVM inspects the actual object type and dispatches to the correct `pay()`.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
[Client code calls account.debit(amount)]
→ [JVM resolves concrete method via vtable ← YOU ARE HERE]
→ [Method validates: amount > 0, balance >= amount]
→ [Updates private balance field]
→ [Creates Transaction record, appends to history]
→ [Returns updated balance to caller]

FAILURE PATH:
[Subclass overrides debit() and removes validation]
→ [Balance goes negative]
→ [Downstream reports show negative account]
→ [Liskov Substitution Principle violated — classic OOP failure]

WHAT CHANGES AT SCALE:
Deep object graphs become serialisation bottlenecks. Hibernate/JPA must
traverse relationships to produce SQL. N+1 query problems emerge when
collection fields are lazily loaded inside loops. At 10,000 objects per
request, object allocation pressure increases GC frequency.

### 💻 Code Example

Example 1 — Encapsulation preventing invalid state:

```java
// BAD: public field, anyone can corrupt balance
public class Account {
    public double balance; // any code can set this to -999999
}

// GOOD: private field, only valid mutations allowed
public class Account {
    private double balance;

    public void debit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException();
        if (amount > balance) throw new InsufficientFundsException();
        this.balance -= amount;
    }

    public double getBalance() { return balance; }
}
```

Example 2 — Polymorphism enabling open/closed extension:

```java
// Interface defines the contract
interface Payment {
    void pay(double amount);
}

// Multiple implementations — caller never changes
class CreditCardPayment implements Payment {
    public void pay(double amount) { /* charge card */ }
}
class PayPalPayment implements Payment {
    public void pay(double amount) { /* call PayPal API */ }
}

// Caller depends on interface, not implementation
void checkout(Payment payment, double total) {
    payment.pay(total); // works for any Payment
}
```

Example 3 — Fragile Base Class (the classic OOP pitfall):

```java
// BAD: subclass breaks parent's invariant
class Counter {
    private int count = 0;
    public void increment() { count++; }
    public void incrementBy(int n) {
        for (int i = 0; i < n; i++) increment(); // calls overridable method!
    }
}
class LoggingCounter extends Counter {
    private int totalCalls = 0;
    @Override public void increment() {
        super.increment();
        totalCalls++; // called n+1 times due to parent's loop — bug!
    }
}

// GOOD: make incrementBy call a private helper, not the overridable method
```

### ⚖️ Comparison Table

| OOP Principle | What it prevents | Cost if misused |
|---|---|---|
| **Encapsulation** | Uncontrolled state mutation | Getter/setter explosion adds boilerplate |
| **Inheritance** | Code duplication | Fragile base class, deep hierarchies |
| **Polymorphism** | Type-switch conditionals | Vtable dispatch overhead (minor) |
| **Abstraction** | Coupling to implementation details | Over-abstraction hides simple logic |

How to choose: Favour composition over inheritance for code reuse. Use
interfaces + polymorphism as the primary extension mechanism. Inheritance
should model true IS-A relationships, not reuse.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OOP = inheritance | Encapsulation and polymorphism are the core; inheritance is often the most misused feature |
| Getters/setters = encapsulation | A getter+setter pair with no validation is a public field with extra steps |
| More classes = better OOP | Excessive class proliferation (AbstractSingletonProxyFactoryBean) is over-engineering |
| OOP is best for all problems | Functional and procedural styles outperform OOP for data pipelines and numerical code |
| Private means thread-safe | Private restricts access scope; it has no effect on concurrent mutation |

### 🚨 Failure Modes & Diagnosis

**1. Fragile Base Class**

Symptom: Subclass method produces wrong output after parent class changes a
method body that the subclass overrides. Breaks silently with no compile error.

Root Cause: Parent's `incrementBy` calls `increment()` internally. Subclass
overrides `increment()`. Parent's `incrementBy` now calls the subclass version,
violating the parent's invariant.

Diagnostic:
```bash
# Java: unit test the subclass in isolation
# Add logging to both increment() implementations temporarily
# IntelliJ: "Find Usages" on the parent method
```

Fix: Make internally-called methods `private` or `final` in the parent class
to prevent subclass overriding from breaking the parent's own logic.

Prevention: Apply the Template Method pattern deliberately. Never call
overridable methods from within the same class's non-overridable methods.

**2. N+1 Query in OOP + ORM**

Symptom: A page takes 30 seconds to load. Profiler shows 1,000 SQL queries
instead of expected 1.

Root Cause: A loop calls `order.getItems()` on each of 1,000 orders. Each
call lazily loads the items collection, triggering a separate SQL query.

Diagnostic:
```bash
# Hibernate: enable SQL logging
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG
# Count SELECT statements in logs — if count == N+1, you found it
```

Fix:
```java
// BAD: N+1 — each order triggers a separate items query
List<Order> orders = orderRepo.findAll();
for (Order o : orders) {
    System.out.println(o.getItems().size()); // lazy load per order
}

// GOOD: fetch join — one query loads orders + items together
@Query("SELECT o FROM Order o JOIN FETCH o.items")
List<Order> findAllWithItems();
```

Prevention: Use `JOIN FETCH` or `@EntityGraph` for all collection fields
accessed in loops. Enable SQL logging during development.

**3. Object Graph Serialisation Failure**

Symptom: `StackOverflowError` or `JsonMappingException: Infinite recursion`
when serialising an entity to JSON.

Root Cause: Bidirectional relationships — `Order` references `Customer`,
`Customer` references `List<Order>` — create a cycle that the serialiser
follows infinitely.

Diagnostic:
```bash
# Stack trace shows Jackson or Gson alternating between two class names
# e.g. Order → Customer → Order → Customer ...
```

Fix:
```java
// BAD: bidirectional JPA relationship without serialisation annotation
@Entity class Order {
    @ManyToOne Customer customer; // triggers cycle
}

// GOOD: break cycle with annotation or DTO
@JsonManagedReference   // serialize this side
@OneToMany List<Order> orders;

@JsonBackReference      // do NOT serialize this side
@ManyToOne Customer customer;
```

Prevention: Use dedicated DTO classes for API responses. Never serialise
JPA entities directly to JSON in production APIs.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Imperative Programming` — OOP organises imperative code; you need to understand it first
- `Procedural Programming` — the paradigm OOP replaced in large systems
- `Variables` — object fields are the OOP-encapsulated form of variables

**Builds On This (learn these next):**
- `Encapsulation` — the most important OOP principle; restricts who can mutate state
- `Inheritance` — mechanism for creating specialised classes from general ones
- `Design Patterns` — reusable solutions to recurring OOP design problems

**Alternatives / Comparisons:**
- `Functional Programming` — avoids mutable state entirely; compositional alternative
- `Procedural Programming` — functions over data structures without encapsulation
- `SOLID Principles` — five rules for keeping OOP codebases maintainable

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Paradigm that bundles state + behaviour   │
│              │ into objects communicating via interfaces │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Global mutable state in procedural code   │
│ SOLVES       │ makes large codebases unmaintainable —    │
│              │ any function can corrupt any variable     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Encapsulation is a bug-surface-area tool  │
│              │ — it limits WHO can mutate state, making  │
│              │ faults local and searchable               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Modelling domain entities with state,     │
│              │ behaviour, and lifecycle (users, orders,  │
│              │ accounts, sessions)                       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data pipelines, numerical computation,    │
│              │ pure transformation logic — use FP        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Encapsulated, navigable code vs object    │
│              │ graph complexity, serialisation friction, │
│              │ and ORM impedance mismatch                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Objects own their state; the only        │
│              │ way in is through the front door."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Encapsulation → Polymorphism →            │
│              │ Design Patterns → SOLID Principles        │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Two OOP codebases both have a `PaymentService` class. Codebase A
has `PaymentService` depend on a concrete `StripeClient`. Codebase B
depends on a `PaymentGateway` interface. A year later, both need to add
PayPal support. Trace step-by-step what changes in each codebase, and
explain precisely which OOP principle codebase B applied that codebase A
violated.

**Q2.** The Liskov Substitution Principle says any subclass must be
substitutable for its parent without breaking the program. Design a
`Rectangle` → `Square` inheritance where this is violated, trace exactly
what breaks, and then redesign it so the principle holds — or argue that
it cannot hold for these two shapes and explain why.
'@
[System.IO.File]::WriteAllText("$base\CS Fundamentals — Paradigms\003 — Object-Oriented Programming (OOP).md", $f003, $enc)
Write-Host "003 done"

Write-Host "Batch 1 (001-003) written OK"
