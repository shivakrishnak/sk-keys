---
layout: default
title: "Hoisting"
parent: "JavaScript"
nav_order: 549
permalink: /javascript/hoisting/
number: "549"
category: JavaScript
difficulty: ★★☆
depends_on: var / let / const, Execution Context, Scope
used_by: Temporal Dead Zone, Closure, Function Declarations, var scoping
tags: #javascript, #intermediate, #browser, #nodejs, #internals
---

# 549 — Hoisting

`#javascript` `#intermediate` `#browser` `#nodejs` `#internals`

⚡ TL;DR — JavaScript's pre-execution phase that registers all declarations (var, function, let, const) in their scope before any code runs, with different initialisation rules per declaration type.

| #549 | Category: JavaScript | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | var / let / const, Execution Context, Scope | |
| **Used by:** | Temporal Dead Zone, Closure, Function Declarations, var scoping | |

---

### 📘 Textbook Definition

**Hoisting** is the behaviour by which the JavaScript engine registers variable and function declarations in their enclosing scope during the creation phase of the execution context — before the execution phase begins. `var` declarations are hoisted and initialised to `undefined`. Function declarations (`function fn() {}`) are hoisted and fully initialised with their function object, making them callable before their textual position. `let` and `const` declarations are hoisted but remain in the **Temporal Dead Zone (TDZ)** — they exist in the scope but are inaccessible until the declaration line is executed.

---

### 🟢 Simple Definition (Easy)

Hoisting means JavaScript reads all variable and function declarations before running any code. So `var x` and `function fn()` are "known" from the very start of their scope — but only `function` declarations are ready to use early. `var` starts as `undefined`.

---

### 🔵 Simple Definition (Elaborated)

Before JavaScript executes a block of code, the engine scans it and registers every declaration — `var`, `let`, `const`, and `function`. It's as if declarations are moved ("hoisted") to the top of their scope. However, the details differ: `var` is hoisted and immediately available (as `undefined`), while `let` and `const` are hoisted but locked in a dead zone — using them before the declaration line throws an error. Function declarations are the best deal: they are fully hoisted including their body, so you can call `fn()` before the `function fn()` line appears in code.

---

### 🔩 First Principles Explanation

**How the JS engine processes a scope:**

JavaScript execution happens in two phases per execution context:

```
┌─────────────────────────────────────────────┐
│  EXECUTION CONTEXT LIFECYCLE                │
│                                             │
│  Phase 1: CREATION (Hoisting)               │
│  ─────────────────────────────              │
│  Scan the scope for declarations            │
│  var → create + init to undefined           │
│  function → create + init to function obj   │
│  let/const → create + TDZ (no init)         │
│                                             │
│  Phase 2: EXECUTION                         │
│  ────────────────                           │
│  Run code line by line                      │
│  Assignment statements execute here         │
│  let/const TDZ lifted when line reached     │
└─────────────────────────────────────────────┘
```

**Why this distinction matters:**

```javascript
// Phase 1: var x created, init to undefined
//          function greet created, init to body
// Phase 2: running starts

console.log(x);      // undefined (var hoisted)
console.log(y);      // ReferenceError (let TDZ)
greet('Alice');      // "Hello Alice" (fn hoisted fully)

var x = 5;
let y = 10;
function greet(name) { console.log('Hello', name); }
```

**var vs function declaration hoisting race:**

When both a `var` and a function share the same name, the function wins — its initialisation happens after var's. Then code runs:

```javascript
console.log(typeof foo); // "function" — fn wins over var

var foo = 1;
function foo() {}

console.log(typeof foo); // "number" — assignment ran
```

---

### ❓ Why Does This Exist (Why Before What)

**What problem hoisting solves:**

Mutual recursion — functions that call each other — would be impossible if declarations weren't registered before execution:

```javascript
// This works because both are hoisted:
function isEven(n) {
  if (n === 0) return true;
  return isOdd(n - 1);   // isOdd not declared yet textually
}

function isOdd(n) {
  if (n === 0) return false;
  return isEven(n - 1);
}

isEven(4); // works — both functions hoisted before exec
```

**What hoisting causes — footguns:**

```
Problem 1: Accidental undefined reads
  console.log(x); // undefined — not a bug signal!
  var x = 5;

Problem 2: var leaking past intended use
  for (var i = 0; i < 5; i++) {}
  console.log(i); // 5 — leaks from loop

Problem 3: Hard to audit code flow
  fn(); // called here
  // ... 200 lines of code ...
  function fn() {} // defined here
  // This is legal but hard to review
```

---

### 🧠 Mental Model / Analogy

> Imagine a movie director receiving a script. Before filming begins, the director reads the entire script and **casts all roles** (registers declarations). Only then does filming (execution) begin. With `var`, the actor shows up on day one but doesn't know their lines yet — they just say "uh..." (undefined). With `function`, the actor is fully prepared and ready to perform from the first day. With `let`/`const`, the actor's contract is signed on day one but they aren't allowed on set until their specific scene (the declaration line is reached).

"Reading the script before filming" = creation phase (hoisting)
"Casting roles" = registering declarations in scope
"Actor saying 'uh...'" = `var` initialised to `undefined`
"Fully prepared actor" = function declaration fully initialised
"Barred from set until their scene" = Temporal Dead Zone for `let`/`const`

---

### ⚙️ How It Works (Mechanism)

**var hoisting:**

```javascript
// What you write:
function fn() {
  console.log(x); // undefined
  var x = 5;
  console.log(x); // 5
}

// What the engine sees (conceptually):
function fn() {
  var x;           // hoisted — var created, init undefined
  console.log(x);  // undefined
  x = 5;           // assignment stays in place
  console.log(x);  // 5
}
```

**Function declaration vs function expression hoisting:**

```javascript
// Function DECLARATION — fully hoisted
sayHi(); // ✅ works — "Hi!"
function sayHi() { console.log('Hi!'); }

// Function EXPRESSION — only the var is hoisted
sayHello(); // ❌ TypeError: sayHello is not a function
var sayHello = function() { console.log('Hello!'); };
// At the call site, var sayHello = undefined
// Calling undefined() → TypeError
```

**let/const — hoisted to TDZ:**

```javascript
{
  // TDZ begins here for x
  console.log(x); // ReferenceError
  let x = 5;      // TDZ ends here
  console.log(x); // 5
}
// x does not exist here (block scope)
```

**Class declarations are also hoisted (TDZ):**

```javascript
new Foo(); // ReferenceError — Foo in TDZ
class Foo {}
// Same TDZ rules as let/const
```

---

### 🔄 How It Connects (Mini-Map)

```
Source Code enters Execution Context
        ↓
  CREATION PHASE — HOISTING  ← you are here
  ┌─────────────────────────────────────┐
  │  var  → scope + init = undefined    │
  │  fn() → scope + init = function obj │
  │  let  → scope + TDZ (no init)       │
  │  const→ scope + TDZ (no init)       │
  └─────────────────────────────────────┘
        ↓
  EXECUTION PHASE
  (assignments, expressions run line by line)
        ↓
  TDZ lifted when let/const line reached
        ↓
  Affects: Closure (captures hoisted bindings)
           Temporal Dead Zone (let/const TDZ)
           Scope Chain (where lookup happens)
```

---

### 💻 Code Example

**Example 1 — var vs let silent difference:**

```javascript
// BAD: var inside if — leaks and confuses
function processUser(user) {
  if (user.isAdmin) {
    var permissions = 'all';  // var — hoisted to fn
  }
  console.log(permissions);   // undefined for non-admin
  // No error, but permissions is meaninglessly undefined
  // Instead of "permissions is not defined" error
}

// GOOD: let — scoped to block, clear error on misuse
function processUser(user) {
  if (user.isAdmin) {
    const permissions = 'all'; // block scoped
  }
  // console.log(permissions); // ReferenceError — clear!
}
```

**Example 2 — function declaration hoisting in practice:**

```javascript
// This is valid — mutual recursion via hoisting
function parseExpression(tokens) {
  if (isPrimary(tokens[0])) return parsePrimary(tokens);
  return parseBinary(tokens);  // not yet declared textually
}

function parseBinary(tokens) {
  const left  = parsePrimary(tokens);
  const op    = tokens.shift();
  const right = parsePrimary(tokens);
  return { left, op, right };
}

function parsePrimary(tokens) {
  return { value: tokens.shift() };
}
```

**Example 3 — typeof safety with var vs let:**

```javascript
// typeof on undeclared var — safe (returns "undefined")
console.log(typeof undeclaredVar); // "undefined" — safe

// typeof on let in TDZ — still throws!
console.log(typeof letVar);        // ReferenceError in TDZ
let letVar = 1;
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Hoisting physically moves code | Hoisting is a mental model for the engine's two-phase execution; the source code is not rewritten. Declarations are registered during parsing |
| let and const are not hoisted | They ARE hoisted — they exist in the scope from the start. The difference is they're in the TDZ until the declaration line runs |
| Function expressions are hoisted like function declarations | Only the var binding is hoisted (to undefined); the function body is not available until the assignment line executes |
| Hoisting applies to all JavaScript environments equally | Module scope (`type="module"`) and class bodies have stricter rules; hoisting behaviour can appear different in async module evaluation |
| typeof is always safe to call on any identifier | typeof on a let/const in TDZ throws a ReferenceError — it's not universally safe the way it was in the pre-let era |
| Class declarations can be used before their definition | Classes use TDZ like let/const — `new MyClass()` before the class declaration throws ReferenceError |

---

### 🔥 Pitfalls in Production

**1. Function expression called before assignment**

```javascript
// BAD: var function expression — only var is hoisted
const handlers = {
  click: handleClick,  // undefined here!
  // handleClick var exists but = undefined
};
// TypeError when click fires: undefined is not a function

var handleClick = function(e) { /* ... */ };

// GOOD: use function declaration or define before use
function handleClick(e) { /* ... */ }
// OR move the assignment before the handlers object
```

**2. var in switch cases sharing a scope**

```javascript
// BAD: var in switch cases all share function scope
switch (action.type) {
  case 'LOGIN':
    var user = action.payload; // hoisted to function
    break;
  case 'LOGOUT':
    var user = null;  // same var — redeclaration OK for var
    break;
}

// GOOD: use let inside block or create block scope
switch (action.type) {
  case 'LOGIN': {    // explicit block for let scope
    const user = action.payload;
    break;
  }
  case 'LOGOUT': {
    const user = null;
    break;
  }
}
```

**3. Relying on function hoisting across conditional blocks**

```javascript
// BAD: function declarations in if blocks
// — behaviour is non-standard in sloppy mode
if (condition) {
  function process() { return 'v1'; }
} else {
  function process() { return 'v2'; }
}
// In sloppy mode: non-standard, varies by engine
// In strict mode: block-scoped (less surprising)

// GOOD: use function expression with const
const process = condition
  ? () => 'v1'
  : () => 'v2';
```

---

### 🔗 Related Keywords

- `var / let / const` — the declaration keywords whose hoisting rules differ
- `Temporal Dead Zone (TDZ)` — the state let/const bindings are in from hoisting until initialisation
- `Execution Context` — the two-phase (creation + execution) model that produces hoisting behaviour
- `Scope` — hoisting registers declarations in the correct scope during the creation phase
- `Closure` — closures capture the hoisted binding, not the value at declaration time
- `Function Declarations` — fully hoisted including body; can be called before textual definition
- `Class` — follows TDZ rules like let/const; cannot be constructed before its declaration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Declarations registered before execution; │
│              │ var=undefined, fn=ready, let/const=TDZ    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Mutual recursion (fn declarations); never │
│              │ rely on var hoisting — it hides bugs      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Calling var function expressions before   │
│              │ assignment; using var expecting TDZ safety │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JS reads declarations first,             │
│              │  then executes — but only fn is ready."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Temporal Dead Zone → Scope → Closure      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Consider a module-level `var` declaration inside a `if (false) {}` block. In a classic `<script>` the var is hoisted to global scope and visible as a property on `window`. In an ES module (`type="module"`) the same code runs in strict mode. Trace exactly what happens to that `var` in both environments — is it on `window`? Is it accessible outside the block? — and explain why the module system changes the semantics even though the hoisting rules for `var` are the same in both.

**Q2.** V8's optimiser (TurboFan) can JIT-compile function declarations to highly optimised machine code because their shape is known at parse time. Explain how hoisting enables this early optimisation — and then describe the specific case where hoisting a function declaration inside a `try/catch` block or a loop body degrades V8's ability to optimise the outer function, and how you would restructure the code to fix it.

