---
layout: default
title: "Execution Context"
parent: "JavaScript"
nav_order: 559
permalink: /javascript/execution-context/
number: "559"
category: JavaScript
difficulty: ★★★
depends_on: Call Stack, Lexical Environment, this keyword, Scope, Hoisting
used_by: Closure, Hoisting, this binding, Variable resolution, async/await
tags: #javascript, #internals, #advanced, #deep-dive, #browser, #nodejs
---

# 559 — Execution Context

`#javascript` `#internals` `#advanced` `#deep-dive` `#browser` `#nodejs`

⚡ TL;DR — The internal runtime container created for each code execution unit (global, function, eval) that holds the this binding, variable environment, and lexical environment.

| #559 | Category: JavaScript | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Call Stack, Lexical Environment, this keyword, Scope, Hoisting | |
| **Used by:** | Closure, Hoisting, this binding, Variable resolution, async/await | |

---

### 📘 Textbook Definition

An **Execution Context** is the abstract specification record created by the JavaScript engine whenever code begins executing. It encapsulates: a **LexicalEnvironment** (for identifier resolution, used by `let`, `const`, and function declarations), a **VariableEnvironment** (for `var` declarations, which follows function boundaries), a **this binding** (determined by how the code was invoked), and a **Realm** (the global environment the code belongs to). When a function is called, a new execution context is pushed onto the Call Stack. When it returns, its context is popped. The currently executing context is always at the top of the stack.

---

### 🟢 Simple Definition (Easy)

Every time JavaScript runs a piece of code — the whole program, a function call, or eval — it creates a temporary "workspace" called an execution context. This workspace tracks the current variables, what `this` means right now, and where to look for variables.

---

### 🔵 Simple Definition (Elaborated)

Think of an execution context as the complete state of the JavaScript engine for one "unit of work." When you call a function, a new execution context is created for that call — it knows which variables belong to this call, what `this` refers to, and where to look if it can't find a variable locally. This context lives on the call stack; when the function returns, the context is gone. The three types are: global (for the entire script), function (for each function call), and eval (for eval() invocations). The global context is always at the bottom of the stack — it never pops.

---

### 🔩 First Principles Explanation

**What "context" means:**

A CPU executes instructions. A JavaScript engine executes code units. Each code unit needs a complete description of its execution environment: where to find variables, what `this` points to, what code is running. This description is the Execution Context.

**The two phases every execution context goes through:**

```
┌─────────────────────────────────────────────┐
│  EXECUTION CONTEXT LIFECYCLE                │
│                                             │
│  PHASE 1 — CREATION (before first line)     │
│  ─────────────────────────────────────────  │
│  1. Create LexicalEnvironment               │
│     a. Create Environment Record            │
│     b. Set outer reference                  │
│  2. Create VariableEnvironment              │
│     (same as LexEnv at function start)      │
│  3. Determine this binding                  │
│  4. HOIST:                                  │
│     • var declared, init = undefined        │
│     • fn declarations fully initialized     │
│     • let/const declared, in TDZ            │
│                                             │
│  PHASE 2 — EXECUTION                        │
│  ─────────────────────────────────────────  │
│  Execute code line by line                  │
│  Assignments initialise bindings            │
│  Nested fn calls push new contexts          │
└─────────────────────────────────────────────┘
```

**Why separate LexicalEnvironment from VariableEnvironment:**

In ES6+, block-scoped `let`/`const` need a new environment per `{}` block, but `var` stays function-scoped. The engine achieves this by updating `LexicalEnvironment` to a new block scope env on each `{}` entry, while `VariableEnvironment` stays fixed at the function-level scope.

---

### ❓ Why Does This Exist (Why Before What)

**Without a formal execution context model:**

```
Without an execution context container:

  Problem 1: No isolation per function call
    Recursive calls would overwrite each other's
    variables — no per-call stack frame isolation

  Problem 2: this binding undefined
    No mechanism to determine which object
    a function call is associated with

  Problem 3: Scope chain unimplementable
    'outer' reference in LexicalEnvironment
    is what enables closures and scope chain
    resolution — without it, no closure

  Problem 4: Hoisting unexplainable
    The creation phase is what causes hoisting —
    declarations are registered before execution
    within the context's env record
```

**WITH execution contexts:**

```
→ Per-call isolation: each call has own LexEnv
→ this determined precisely per call site
→ Scope chain: outer LexEnv ref enables lookups
→ Hoisting: creation phase registers before exec
→ async/await: context is suspended on await
  and resumed as microtask on Promise resolve
→ Generators: context suspended/resumed per yield
```

---

### 🧠 Mental Model / Analogy

> An execution context is like a **complete project dossier** handed to each worker when they start a job. It contains: the worker's current ID badge (`this`), their filing cabinet key for their own documents (`LexicalEnvironment`), a reference to the main archive room (outer scope), and a notepad for any temporary variables they declare (`var` on `VariableEnvironment`). When the job is done (function returns), the dossier is filed away (context popped). If the job is suspended (await/yield), the dossier is kept open on a shelf until resumed.

"Project dossier" = execution context
"ID badge" = this binding
"Filing cabinet key" = LexicalEnvironment
"Reference to main archive" = outer scope reference
"Dossier filed away" = context popped from stack
"Dossier on a shelf" = suspended generator/async context

---

### ⚙️ How It Works (Mechanism)

**Execution context components (ECMAScript spec fields):**

```
┌──────────────────────────────────────────────┐
│  EXECUTION CONTEXT RECORD                    │
├──────────────────────────────────────────────┤
│  code evaluation state                       │
│  → for generators/async: yield/await point   │
│                                              │
│  Function (if function context)              │
│  → the Function object being executed        │
│                                              │
│  Realm                                       │
│  → the global context this code belongs to   │
│  → cross-realm: iframes, workers, vm.Context │
│                                              │
│  LexicalEnvironment                          │
│  → current scope env (let/const/fn found)    │
│  → updated as blocks are entered/exited      │
│                                              │
│  VariableEnvironment                         │
│  → function-level scope (var found here)     │
│  → stays fixed for function duration         │
│                                              │
│  this binding                                │
│  → determined at creation time by call site  │
└──────────────────────────────────────────────┘
```

**Three types of execution contexts:**

```
1. GLOBAL EXECUTION CONTEXT
   Created once when script loads
   this = global object (window / global / undefined in ESM)
   Always at bottom of call stack
   VariableEnvironment backed by global object

2. FUNCTION EXECUTION CONTEXT
   Created on every function call
   this determined by call site (4 rules)
   New LexicalEnvironment per call → per-call isolation
   Pushed/popped from call stack

3. EVAL EXECUTION CONTEXT
   Created when eval() is called
   Inherits calling context's variable environment
   Avoids in production — disables V8 optimisations
```

**async/await — suspended execution context:**

```javascript
async function fetchUser(id) {
  // Context created, pushed to stack
  const user = await getUser(id);
  // SUSPENSION POINT:
  // Context state (including local vars, this) saved
  // Context POPPED from call stack
  // Event loop is free to run other tasks
  // When getUser resolves (microtask):
  // Context RESTORED on call stack
  // Execution resumes after `await`
  return user.name;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Script / Function call / eval call
        ↓
  EXECUTION CONTEXT created  ← you are here
  ┌──────────────────────────────────────────┐
  │  Creation phase: hoist, determine this   │
  │  Execution phase: run code line by line  │
  └──────────────────────────────────────────┘
        │
        ├── LexicalEnvironment (let/const/fn)
        │     └── outer → parent LexEnv (scope chain)
        │
        ├── VariableEnvironment (var)
        │
        └── this binding (call-site determined)
        ↓
  Pushed onto CALL STACK
  Popped on return (kept alive if closure exists)
        ↓
  Used by:
  Hoisting  ← happens in creation phase
  Closure   ← LexEnv survives context pop
  async     ← context suspended at await
  Generator ← context suspended at yield
```

---

### 💻 Code Example

**Example 1 — Observing per-call isolation:**

```javascript
function makeId() {
  let id = 0;           // per-context variable
  return {
    next: () => ++id,   // id from THIS call's context
    reset: () => { id = 0; },
  };
}

const gen1 = makeId(); // execution context 1, id=0
const gen2 = makeId(); // execution context 2, id=0

gen1.next(); // 1 (context 1)
gen1.next(); // 2 (context 1)
gen2.next(); // 1 (context 2 — independent)
```

**Example 2 — Creation phase hoisting:**

```javascript
function demo() {
  // CREATION PHASE happens before line 1 runs:
  // var x → registered, init = undefined
  // fn greet → registered, fully initialized

  console.log(x);      // undefined (hoisted)
  console.log(greet);  // function (fully hoisted)

  var x = 5;
  function greet() { return 'hello'; }

  console.log(x);      // 5 (now executed)
}
demo();
```

**Example 3 — Execution context stack trace:**

```javascript
function c() {
  throw new Error('trace me');
}
function b() { c(); }
function a() { b(); }

try {
  a();
} catch(e) {
  console.log(e.stack);
  // Reveals the call stack = ordered execution contexts:
  // Error: trace me
  //   at c (...)  ← top context at throw
  //   at b (...)
  //   at a (...)
  //   at <anonymous> (...)  ← global context
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Execution context and scope are the same | Execution context is the runtime container; scope is the static syntactic region. One scope can map to many execution contexts (one per call) |
| The global execution context is recreated on each script tag | The global context persists for the lifetime of the page/process; multiple `<script>` tags share the same global context |
| Execution context is the same as the call stack | The call stack is the data structure holding execution contexts; contexts are the items on the stack |
| async/await creates new threads for each await | async/await suspends the current execution context and resumes it via microtask — all on the single JS thread |
| eval() is the same as a function call | eval() creates an execution context in its calling context's scope, inheriting variables. A function creates an isolated context with its own scope |

---

### 🔥 Pitfalls in Production

**1. eval() colliding with execution context optimisation**

```javascript
// BAD: eval forces function to opt out of optimisation
function hotPath(input) {
  const x = 1;
  eval(input); // V8: "eval may introduce vars — deopt"
  return x;    // x lookup can't be stack-offsetted
}
// V8 marks this function as "megamorphic" and bails out
// of optimisation for ALL calls to hotPath

// GOOD: never use eval() — JSON.parse for data,
// new Function() with sandboxed scope for rare dynamic code
```

**2. with() statement corrupting execution context variable lookup**

```javascript
// BAD: with() changes which environment is searched first
const config = { timeout: 5000 };
with (config) {
  console.log(timeout); // 5000 — from config
  // But: if config.timeout is deleted mid-execution,
  // lookup falls through to outer scope → wrong value
  // V8 disables ALL optimisations for functions using with()
}

// GOOD: destructure explicitly
const { timeout } = config;
console.log(timeout); // 5000 — direct binding
```

---

### 🔗 Related Keywords

- `Call Stack` — the data structure that holds execution contexts; push on call, pop on return
- `Lexical Environment` — the storage component inside every execution context
- `this keyword` — one of the three key fields of an execution context, set at creation time
- `Hoisting` — the result of the execution context creation phase registering declarations first
- `Closure` — a function retaining a reference to its creation context's LexicalEnvironment
- `async/await` — suspends and restores execution context state at each await point

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runtime container per code unit: LexEnv,  │
│              │ VarEnv, this; creation phase = hoisting   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Explaining hoisting, this, closures,      │
│              │ scope chain, async suspension mechanics   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — system-managed; avoid eval/with     │
│              │ which corrupt context optimisation        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every function call gets a fresh dossier;│
│              │  closures keep the dossier alive."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lexical Environment → Closure → async     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** When `async function f() { await g(); await h(); }` is called, exactly three execution contexts are created and destroyed. Trace each one: when is each context created, when is it pushed/popped from the call stack, and when `await g()` suspends, where does the context's state (local variables, this binding, resume point) live — on the heap or on the stack? Contrast this with how a synchronous recursive call manages the same information.

**Q2.** An iframe embeds a page that has `window.Array` polyfilled to a different version. When the parent frame passes an array to an iframe function, `value instanceof Array` returns `false` even though it is clearly an array. Trace this through the Execution Context model: specifically, which field of the execution context explains the two different `Array` constructors, how the `instanceof` check walks prototype chains using the wrong realm, and what the correct cross-realm check is.

