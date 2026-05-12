#!/usr/bin/env python3
"""Upgrade batch 1a: files 001-003 to v2 spec"""
import os, glob

def find(prefix):
    pattern = os.path.join(r"C:\ASK\MyWorkspace\sk-keys\docs", "**", f"{prefix} *.md")
    matches = [f for f in glob.glob(pattern, recursive=True) if os.path.basename(f) != "index.md"]
    return matches[0] if matches else None

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {os.path.basename(path)}")

# ─── 001 — Imperative Programming ───────────────────────────────────────────
c001 = """\
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
meant understanding the entire hardware state at that exact moment.

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
every loop iteration is a mutation of a value somewhere in memory. The program
IS the ordered history of those mutations — and every bug is an unexpected or
missing mutation somewhere in that sequence.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. State is explicit and mutable — variables hold values that change over time.
2. Execution is sequential — statements run top to bottom unless a branch occurs.
3. Control flow is explicit — the programmer specifies every branch and loop.

DERIVED DESIGN:
Hardware CPUs execute instructions sequentially and read/write memory registers
directly. A language that mirrors this model maps cleanly to machine operations.
Assignment (`x = 5`) becomes a `MOV` instruction. A `for` loop becomes a `CMP`
+ `JMP` instruction pair. The language is a thin, human-readable layer over
the hardware's native sequential execution model.

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
no instructions to follow. The expression states intent but describes no steps.
The helper returns the paper blank.

WHAT HAPPENS WITH IMPERATIVE STYLE:
You write:
  total = 0
  total = total + 1   (total is now 1)
  total = total + 2   (total is now 3)
  total = total + 3   (total is now 6)
  total = total + 4   (total is now 10)
  total = total + 5   (total is now 15)
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
"8 minutes" → loop condition
"Drain" → side effect (mutation visible outside the local scope)

Where this analogy breaks down: unlike a chef, the CPU never misreads or
skips a step — execution is perfectly deterministic every single time.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Imperative programming means giving the computer a numbered to-do list and
having it execute every item in order. Nothing is assumed; everything is stated.

**Level 2 — How to use it (junior developer):**
You write variables to hold data, `if`/`else` to make decisions, `for`/`while`
to repeat steps, and functions to bundle reusable sequences. Java, Python, C,
JavaScript — most languages are imperative by default. You describe exactly what
should happen at each step.

**Level 3 — How it works (mid-level engineer):**
Each statement maps to CPU instructions: `MOV` (assignment), `ADD` (arithmetic),
`CMP` (comparison), `JMP` (branch). The program counter advances through the
instruction sequence. Branches modify it; loops reset it to an earlier address.
All values live in registers or named memory locations readable and writable at
any point during execution.

**Level 4 — Why it was designed this way (senior/staff):**
Von Neumann architecture stores both program instructions and data in the same
memory, executing sequentially. Imperative programming is the direct software
model of this design. Every other paradigm — functional, declarative, reactive —
is a higher abstraction that ultimately compiles to imperative machine code.
Imperative programming is the substrate on which all other paradigms are built.

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

**Assignment**: `x = 10` writes 10 into the memory slot named `x`. At the
machine level this is a `MOV` instruction targeting a register or RAM address.

**Sequence**: Statements execute in written order. The program counter advances
by one instruction width after each execution unless modified.

**Branch**: `if (x > 0)` becomes `CMP x, 0` + `JLE skip`. One of two code paths
is entered; the other is skipped entirely.

**Loop**: A backwards jump — the program counter resets to an earlier instruction
and re-executes until the condition stops being true.

Everything else — objects, closures, coroutines — compiles down to permutations
of these four primitives.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
[Developer writes source code]
→ [Compiler / interpreter translates to instructions]
→ [OS loads program into memory]
→ [CPU fetches instruction[0] ← YOU ARE HERE]
→ [Operands loaded from RAM into registers]
→ [ALU performs operation]
→ [Result written back to memory]
→ [PC advances to instruction[1]]
→ [Repeat until program exit]

FAILURE PATH:
[Incorrect state mutation at step N]
→ [Wrong branch taken at step N+3]
→ [Corrupt data passed to output]
→ [Incorrect result / exception / crash]

WHAT CHANGES AT SCALE:
Shared mutable state becomes the primary bottleneck. Multiple threads
simultaneously mutating the same variables produce data races visible only
under load. At 100+ concurrent threads, unguarded imperative mutation produces
non-deterministic results — the fundamental scaling weakness of the imperative
model without explicit synchronisation.

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
| Functional | Immutable | Explicit + pure functions | Mathematical | Data pipelines |
| Object-Oriented | Encapsulated mutable | Message-passing | Domain modelling | Business logic |

How to choose: Use imperative when you need precise control over execution order
and performance. Use declarative or functional when correctness and readability
matter more than granular control over every step.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Imperative programming is outdated or inferior | It is the foundation — all paradigms ultimately compile to imperative machine instructions |
| OOP replaces imperative programming | OOP organises imperative code; it does not eliminate mutable state |
| More statements mean more control | Excess statements increase mutation surface area and bug probability |
| Loops are inherently imperative | forEach in functional style uses imperative CPU iteration under the hood |
| Immutable variables make code non-imperative | Immutability constrains state mutation; the execution model remains sequential |

### 🚨 Failure Modes & Diagnosis

**1. Unintended State Mutation**

Symptom: Program produces wrong results intermittently; values change
unexpectedly between method calls with no obvious cause in the caller.

Root Cause: A variable is mutated by a code path the developer did not account
for — typically a shared object reference modified inside a helper method.

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
// BAD: helper mutates caller's collection in place
void addDefaults(List<String> list) {
    list.add("default"); // surprise side effect on caller's state
}

// GOOD: return new object; caller decides about mutation
List<String> addDefaults(List<String> original) {
    List<String> copy = new ArrayList<>(original);
    copy.add("default");
    return copy;
}
```

Prevention: Treat method arguments as read-only by convention. Return new
values; do not mutate inputs.

**2. Off-by-One Loop Error**

Symptom: Loop processes one element too many or too few; may throw
`ArrayIndexOutOfBoundsException` or silently skip the last element.

Root Cause: Incorrect loop boundary — `<=` instead of `<`, or loop initialised
at 1 instead of 0 for zero-indexed collections.

Diagnostic:
```bash
# Java runtime prints exact line and index:
# ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 5
# Enable assertions:
java -ea MyApplication
```

Fix:
```java
// BAD: i == array.length is out of bounds
for (int i = 0; i <= array.length; i++) {
    process(array[i]); // crashes when i == length
}

// GOOD: i < array.length is always valid
for (int i = 0; i < array.length; i++) {
    process(array[i]);
}
```

Prevention: Prefer enhanced for-each loops when the index is not needed.
Always ask: "what is the last valid value of i?"

**3. Infinite Loop**

Symptom: Program hangs indefinitely; CPU usage climbs to 100%; no progress
in output or logs.

Root Cause: The loop's termination variable is never updated inside the loop
body, or updated only in a branch that is never taken.

Diagnostic:
```bash
# Find spinning thread on Linux:
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
    // forgot i++
}

// GOOD: i updated on every iteration
int i = 0;
while (i < 10) {
    process(i);
    i++;
}
```

Prevention: Prefer `for` loops — the update expression is always visible in
the loop header, making it hard to forget.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Variables` — imperative programs are sequences of mutations to named variables
- `Control Flow` — branches and loops are the core control structures
- `Functions` — group sequences of statements into named, reusable instruction blocks

**Builds On This (learn these next):**
- `Procedural Programming` — organises imperative code into named, callable procedures
- `Object-Oriented Programming` — encapsulates imperative mutable state inside objects
- `Functional Programming` — constrains and controls mutation to improve correctness

**Alternatives / Comparisons:**
- `Declarative Programming` — describes WHAT to compute, lets the engine decide HOW
- `Structured Programming` — imperative with disciplined, goto-free control flow
- `Assembly Language` — imperative programming at raw machine-instruction level

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
│              │ source; switch to functional / declarative│
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

**Q1.** A distributed system has 10 services all mutating the same counter
in a shared database using imperative "read-increment-write" logic. At 100
requests/second it works correctly. At 10,000 requests/second it produces
wrong counts. What specific property of imperative mutation causes this
failure, and what does it reveal about the assumptions the imperative model
makes about execution context?

**Q2.** You are designing a language that presents a purely declarative
interface to programmers but compiles to imperative machine instructions.
What invariants of the imperative execution model must your compiler
preserve in every compilation, and what source-level transformations become
impossible because of those invariants?
"""

# ─── 002 — Declarative Programming ─────────────────────────────────────────
c002 = """\
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
order results. You wrote hundreds of lines of imperative code every time you
wanted to ask a simple question of your data. The "how" completely obscured
the "what."

THE BREAKING POINT:
Business users needed to query data. They understood the question ("show me
all orders over $100 from last month") but had no ability to write the traversal
logic. Even experienced developers spent most of their time writing mechanical
iteration code rather than expressing actual business intent.

THE INVENTION MOMENT:
This is exactly why Declarative Programming was created. SQL, regular
expressions, HTML, CSS, Kubernetes manifests — they all let you state what
outcome you want and delegate how to achieve it to an engine optimised for
that domain.

### 📘 Textbook Definition

Declarative Programming is a paradigm in which the programmer expresses the
desired result or constraints of a computation without specifying the
step-by-step procedure to achieve it. The underlying execution engine determines
the optimal implementation strategy. Examples include SQL (what data to
retrieve), HTML (what structure to render), CSS (what styles to apply), and
Kubernetes manifests (what cluster state to maintain).

### ⏱️ Understand It in 30 Seconds

**One line:**
State what you want; let the engine figure out how to give it to you.

**One analogy:**
> Declarative programming is like ordering at a restaurant. You say "I'd like
> the salmon with salad" — you do not walk into the kitchen and direct the chef
> step by step. The kitchen figures out the how.

**One insight:**
The power of declarative programming is that it **separates intent from
implementation**. The same SQL query can be optimised differently by PostgreSQL
and MySQL because neither locks you into a specific execution plan. The engine
chooses the optimal "how" — and that optimisation is its core advantage.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The programmer expresses desired state or result, not procedure.
2. An execution engine interprets the expression and decides how to execute.
3. The same expression may execute differently on different engines.

DERIVED DESIGN:
Because the programmer does not specify control flow, the engine is free to
choose any correct implementation. A SQL query planner can choose between a
full table scan, an index lookup, or a hash join — whichever is fastest for
the current data. This optimisation is impossible in imperative code where the
programmer has already committed to one traversal strategy.

THE TRADE-OFFS:
Gain: Expressiveness, readability, engine-level optimisation, and portability.
Cost: Less control over execution path. Performance surprises when the engine
      chooses a strategy you didn't anticipate. Harder to debug when the engine
      behaves unexpectedly.

### 🧪 Thought Experiment

SETUP:
You have 10,000 orders. You want those from 2024 with total > $500, sorted by
date. Solve it imperatively vs declaratively.

WHAT HAPPENS WITH IMPERATIVE APPROACH:
Iterate the list, check year == 2024, check total > 500, add to result list,
then sort by date. 20+ lines of code. Runs entirely in the application layer.
The database engine is bypassed; it cannot use its indexes.

WHAT HAPPENS WITH DECLARATIVE APPROACH (SQL):
  SELECT * FROM orders
   WHERE created_at >= '2024-01-01'
     AND total > 500
   ORDER BY created_at;
3 lines. The database engine uses the date index and a B-tree sort. It runs
100x faster because the engine has statistics and index structures you lack.

THE INSIGHT:
Declarative programming lets domain-specific engines apply optimisations that
are invisible to the programmer — and impossible when the programmer controls
every step of execution.

### 🧠 Mental Model / Analogy

> Declarative programming is like a **restaurant order form**. You tick what
> you want; the kitchen figures out preparation order, timing, and technique.
> You never enter the kitchen.

"Order form" → declarative expression (SQL, CSS, HTML, YAML)
"Kitchen" → execution engine (query planner, browser renderer, scheduler)
"Menu item" → declarative construct (SELECT clause, display:flex, replicas:3)
"Preparation method" → execution plan chosen by the engine
"You never enter the kitchen" → you have no control over execution order

Where this analogy breaks down: you can hint to the engine (SQL hints, CSS
specificity) but cannot fully override it.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Declarative programming means telling the computer what you want without
explaining how to get it. Like using a GPS — you enter the destination; the
GPS figures out the route. You don't give turn-by-turn instructions.

**Level 2 — How to use it (junior developer):**
SQL, HTML, CSS, React JSX, Kubernetes YAML, Terraform — you write declaratively
every day. `SELECT name FROM users WHERE active = true` is declarative.
`<Button variant="primary">Submit</Button>` is declarative. You describe the
desired structure or result; the framework builds it.

**Level 3 — How it works (mid-level engineer):**
Every declarative expression is parsed into an AST or DAG, then compiled by
an engine into an imperative execution plan. A SQL query becomes a physical
query plan with specific join algorithms. React JSX becomes a virtual DOM diff
that React maps to actual DOM mutations. The "declarative" nature is a
compile-time abstraction over imperative execution.

**Level 4 — Why it was designed this way (senior/staff):**
The separation of intent from implementation enables independent evolution. The
SQL standard has been stable for 40+ years while database engines changed
execution strategies radically (columnar storage, vectorised execution). If SQL
were imperative, every engine upgrade would break every query. Declarative
interfaces are stable contracts between user intent and engine capability —
the interface remains stable; the implementation improves underneath.

### ⚙️ How It Works (Mechanism)

┌──────────────────────────────────────────────┐
│       DECLARATIVE EXECUTION PIPELINE         │
├──────────────────────────────────────────────┤
│  Declarative expression (SQL / HTML / YAML)  │
│            ↓                                 │
│  Parser → Abstract Syntax Tree (AST)         │
│            ↓                                 │
│  Semantic analysis / type validation         │
│            ↓                                 │
│  Optimizer selects execution strategy        │
│  (indexes, join order, cache plan, etc.)     │
│            ↓                                 │
│  Execution plan → imperative instructions    │
│            ↓                                 │
│  Engine executes and returns result          │
└──────────────────────────────────────────────┘

The critical step is the **optimizer**: it uses statistics about data
distribution, available indexes, and hardware resources that you do not have
at development time. It can choose a plan orders of magnitude faster than
a hand-written loop.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
[Developer writes declarative expression]
→ [Parser validates syntax]
→ [Semantic analyser checks types and schema]
→ [Optimizer selects execution strategy ← YOU ARE HERE]
→ [Engine executes optimised plan]
→ [Result returned to caller]

FAILURE PATH:
[Expression is valid but prevents index use]
→ [Optimizer falls back to full table scan]
→ [Query runs in 30 seconds instead of 30ms]
→ [Timeout / user impact]

WHAT CHANGES AT SCALE:
At scale the optimizer's decisions dominate performance. A query returning
10 rows from 1,000 is fast regardless of strategy. At 100M rows, the
difference between a full scan and an indexed lookup is minutes vs
milliseconds. Declarative interfaces require understanding your engine's
optimiser to avoid performance cliffs.

### 💻 Code Example

Example 1 — Imperative vs declarative data retrieval:

```java
// BAD (imperative): engine cannot optimise; runs in application layer
List<Order> result = new ArrayList<>();
for (Order o : allOrders) {
    if (o.getYear() == 2024 && o.getTotal() > 500) {
        result.add(o);
    }
}
result.sort(Comparator.comparing(Order::getDate));

// GOOD (declarative SQL): engine uses indexes
String sql = """
    SELECT * FROM orders
     WHERE created_at >= '2024-01-01'
       AND total > 500
     ORDER BY created_at
    """;
```

Example 2 — Declarative React UI vs imperative DOM:

```jsx
// BAD (imperative DOM manipulation)
const btn = document.createElement('button');
btn.className = 'btn-primary';
btn.textContent = 'Submit';
btn.disabled = !isValid;
container.appendChild(btn);
// On state change: find element, update each property manually

// GOOD (declarative React): describe desired state
<Button variant="primary" disabled={!isValid}>
  Submit
</Button>
// On state change: React diffs virtual DOM and patches only what changed
```

Example 3 — Declarative infrastructure:

```yaml
# Kubernetes: declare desired state; k8s figures out how to achieve it
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3        # I want 3 running instances
  template:
    spec:
      containers:
      - name: api
        image: myapp:1.2.3
```

### ⚖️ Comparison Table

| Style | Who controls "how" | Engine-optimisable | Debug difficulty | Best For |
|---|---|---|---|---|
| **Declarative** | Engine | Yes | Hard (engine is a black box) | Queries, config, UI |
| Imperative | Developer | No — path is fixed | Easy (you wrote every step) | Algorithms, perf-critical code |
| Functional | Developer (constrained) | Partial | Medium | Data transformation |

How to choose: Use declarative when you trust the engine more than your own
loop, or when a well-designed DSL exists (SQL, HTML, CSS). Use imperative
when you need exact control over the execution path.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Declarative means no underlying imperative execution | Every declarative expression compiles to imperative machine instructions |
| Declarative code is always faster | A poorly written SQL query can be slower than a good Java loop if it prevents index use |
| You cannot debug declarative code | Use EXPLAIN PLAN (SQL), browser DevTools (CSS/HTML), React DevTools |
| HTML is not a programming language | HTML is a declarative language for describing document structure |
| Declarative and functional are the same thing | Functional is one style of declarative; SQL and HTML are declarative but not functional |

### 🚨 Failure Modes & Diagnosis

**1. Query Optimiser Chooses Wrong Plan (N+1 Full Scan)**

Symptom: Query that was fast in dev runs for 30+ seconds in production.
EXPLAIN shows a full table scan on a 50M-row table.

Root Cause: Table statistics are stale, or a function wrapped around an
indexed column prevents the optimiser from using the index.

Diagnostic:
```sql
-- PostgreSQL: see actual execution plan with row counts
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
 WHERE YEAR(created_at) = 2024 AND total > 500;

-- Refresh stale statistics
ANALYZE orders;
```

Fix:
```sql
-- BAD: YEAR() function prevents index use on created_at
WHERE YEAR(created_at) = 2024

-- GOOD: range condition allows index scan
WHERE created_at >= '2024-01-01'
  AND created_at <  '2025-01-01'
```

Prevention: Always run EXPLAIN ANALYZE on queries against large tables
during development. Avoid wrapping indexed columns in functions.

**2. CSS Specificity Conflict**

Symptom: A CSS rule appears correct but is silently overridden by another.
Styles apply inconsistently or not at all.

Root Cause: The CSS engine applies the rule with higher specificity, not
the rule that appears last in the file.

Diagnostic:
```bash
# Chrome DevTools → Elements panel → Computed tab
# Shows which rule is applied and which are struck through (overridden)
# No CLI — browser inspector is the only tool
```

Fix:
```css
/* BAD: specificity conflict */
.button { color: blue; }
div .button { color: red; }  /* wins — higher specificity */

/* GOOD: consistent specificity with BEM */
.button { color: blue; }
.button--primary { color: red; }  /* same level; last one wins */
```

Prevention: Use BEM or CSS Modules to keep all selectors at the same
specificity level. Avoid `!important`.

**3. Kubernetes Desired State Not Converging**

Symptom: Pods stuck in `Pending`, `CrashLoopBackOff`, or `ErrImagePull`
despite a valid-looking manifest.

Root Cause: The declared desired state is unachievable — insufficient node
resources, wrong image tag, missing ConfigMap, or failing health probe.

Diagnostic:
```bash
# See exact failure reason in the Events section
kubectl describe pod <pod-name>

# See crash output from the previous container run
kubectl logs <pod-name> --previous
```

Fix: Address the specific event shown in `kubectl describe`. Most common:
correct the image tag, create missing secrets/ConfigMaps, reduce resource
requests, or fix the health probe endpoint.

Prevention: Test manifests with `kubectl apply --dry-run=server` before
applying to production. Use a staging namespace for validation.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Imperative Programming` — declarative is best understood as its contrast
- `Domain-Specific Languages` — SQL, CSS, HTML are all declarative DSLs

**Builds On This (learn these next):**
- `Functional Programming` — the most mathematically rigorous declarative style
- `SQL` — the canonical example of a successful, durable declarative language
- `React` — declarative UI: describe desired state; React handles DOM mutations

**Alternatives / Comparisons:**
- `Imperative Programming` — you control every step; engine delegates nothing
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
│              │ executed differently by different engines  │
│              │ — the optimiser is the real advantage     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ A trusted engine exists for the domain    │
│              │ (database, browser, orchestrator)         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ You need precise control over the         │
│              │ execution path or cannot trust the engine │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Expressiveness + engine optimisation vs   │
│              │ less control and opaque execution paths   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Order from the menu —                    │
│              │ don't walk into the kitchen."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SQL → Functional Programming →            │
│              │ React (declarative UI)                    │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A SQL query runs in 50ms on a table with 1M rows. After a data
migration, the same query runs in 45 seconds on the same 10M-row table. The
schema, indexes, and query are unchanged. What layer of the declarative
execution pipeline is most likely responsible, and what specific mechanism
caused the degradation?

**Q2.** React re-renders a component tree on every state change, using a
virtual DOM diff to determine what to actually change in the real DOM. How
does this differ from a purely imperative DOM approach, and what trade-off
does React's declarative model make at 10,000 DOM nodes that makes the
purely declarative approach less attractive?
"""

p001 = find("001")
p002 = find("002")

if p001:
    write(p001, c001)
else:
    print("ERROR: could not find 001")

if p002:
    write(p002, c002)
else:
    print("ERROR: could not find 002")

print("Batch 1a (001-002) complete.")
