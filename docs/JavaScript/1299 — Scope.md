---
layout: default
title: "Scope"
parent: "JavaScript"
nav_order: 1299
permalink: /javascript/scope/
number: "1299"
category: JavaScript
difficulty: ★★☆
depends_on: var / let / const, Execution Context, JavaScript Engine (V8)
used_on: Closure, Hoisting, Temporal Dead Zone, IIFE, Module pattern, Lexical Environment
tags: #javascript, #intermediate, #browser, #nodejs, #internals
---

# 1299 — Scope (Global, Function, Block)

`#javascript` `#intermediate` `#browser` `#nodejs` `#internals`

⚡ TL;DR — The set of rules determining where a variable is accessible; JavaScript has three scope types — global, function, and block — resolved using the lexical scope chain at compile time.

| #1299 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | var / let / const, Execution Context, JavaScript Engine (V8) | |
| **Used by:** | Closure, Hoisting, Temporal Dead Zone, IIFE, Module pattern, Lexical Environment | |

---

### 📘 Textbook Definition

**Scope** in JavaScript defines the accessibility and lifetime of a variable binding within a program. JavaScript uses **lexical scoping** (also called static scoping): the scope of a variable is determined by its physical position in the source code, not by the runtime call stack. There are three scope types: **Global scope** (accessible everywhere), **Function scope** (accessible within a function and its nested functions), and **Block scope** (accessible within a `{}` block, applicable to `let` and `const`). Scopes form a **scope chain**: when a variable is not found in the current scope, the engine walks up the chain to enclosing scopes until reaching the global scope.

---

### 🟢 Simple Definition (Easy)

Scope is where a variable lives and who can see it. A variable in a function is only visible inside that function. A variable at the top of the file is visible everywhere. `let` and `const` add a tighter rule — they're only visible inside the `{}` block they're declared in.

---

### 🔵 Simple Definition (Elaborated)

JavaScript determines variable visibility at the time you write the code, not when it runs. This is called lexical scoping. If a function has a variable, only that function (and functions written inside it) can see it. This nesting creates a scope chain — when your code looks up a variable, it starts in the current scope and works its way outward through each enclosing scope. The first match wins. If no scope has the variable, you get a `ReferenceError`. `var` respects function boundaries; `let` and `const` respect `{}` block boundaries — they're more granular.

---

### 🔩 First Principles Explanation

**Problem — global variables are a shared mess:**

Early JavaScript inherited BASIC's model where all variables were global. On a web page with multiple scripts, any variable could accidentally overwrite another:

```javascript
// Script A (analytics.js):
var count = 0;

// Script B (shopping-cart.js):
var count = 0; // silently overwrites A's count!
count++;
// Analytics now counts cart interactions by mistake
```

**Constraint — code needs both private and shared state:**

Functions need private working variables. Some data genuinely needs to be shared. You need a way to define the boundary.

**Solution — lexical scope hierarchy:**

```
┌────────────────────────────────────────────┐
│  GLOBAL SCOPE                              │
│  var g = 'global';                         │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  FUNCTION SCOPE (outer)              │  │
│  │  function outer() {                  │  │
│  │    var o = 'outer';                  │  │
│  │                                      │  │
│  │  ┌──────────────────────────────┐    │  │
│  │  │  FUNCTION SCOPE (inner)      │    │  │
│  │  │  function inner() {          │    │  │
│  │  │    var i = 'inner';          │    │  │
│  │  │    // can see: i, o, g       │    │  │
│  │  │  }                           │    │  │
│  │  └──────────────────────────────┘    │  │
│  │  // can see: o, g (not i)            │  │
│  └──────────────────────────────────────┘  │
│  // can see: g only (not o, not i)         │
└────────────────────────────────────────────┘
```

Variables are visible in their scope and all scopes nested inside — but not in parent or sibling scopes. Parent scopes are visible to children but not vice versa ("outward but not inward").

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT lexical scope:**

```
Without scoping rules (dynamic scope):
  function greet() {
    console.log(name); // which 'name'? caller's? global?
  }

  function runA() {
    var name = 'Alice';
    greet(); // would greet see Alice?
  }

  function runB() {
    var name = 'Bob';
    greet(); // would greet see Bob?
  }

  → Behaviour depends on CALL SITE, not definition site
  → Impossible to reason about a function in isolation
  → All libraries that use var name break each other
```

**WITH lexical scope:**

```
→ A function's variable resolution is determined
  by where it was WRITTEN, not where it was called
→ You can reason about a function independently
  of who calls it
→ Private variables via function scope — module
  pattern, IIFE, closures all depend on this
→ const/let block scope → loop variables isolated
  → async callbacks capture correct value
```

---

### 🧠 Mental Model / Analogy

> Scope works like a **series of one-way mirrors**. Each scope is a room with one-way mirrors facing outward. You can see through the mirror into the room outside (parent scope), but the outer room cannot see in. Inner nested rooms can see through multiple layers of mirrors to grandparent scopes. The global scope is a glass-walled room all other rooms can see into — but no one from global can see into private rooms.

"Room" = a scope (function or block)
"One-way mirror outward" = inner scopes can see outer, but not vice versa
"Glass-walled room" = global scope — visible to all
"Looking through stacked mirrors" = scope chain lookup walking up to global

---

### ⚙️ How It Works (Mechanism)

**The scope chain lookup:**

```
Variable lookup for 'x':

1. Check current scope → not found
2. Check enclosing function scope → not found
3. Check next enclosing scope → found! → use it
4. (If never found → ReferenceError)
```

**Block scope with let/const:**

```javascript
let x = 'outer';

{
  let x = 'inner'; // NEW binding — shadows outer x
  console.log(x);  // 'inner'
}

console.log(x);    // 'outer' — block scope respected
```

**var ignores block boundaries:**

```javascript
var x = 'outer';

{
  var x = 'inner'; // SAME binding — overwrites outer x
  console.log(x);  // 'inner'
}

console.log(x);    // 'inner' — var leaked out of block!
```

**Lexical vs dynamic scoping contrast:**

```javascript
const name = 'global';

function greet() {
  console.log(name); // uses LEXICAL scope — sees 'global'
}

function callGreet() {
  const name = 'local';
  greet(); // even though name='local' here, greet
           // looks up in its DEFINITION context
}

callGreet(); // logs 'global' — lexical scoping
```

**Module scope (ES Modules):**

Each ES module has its own module scope. Top-level `var` in a module does NOT become a property of `window`. Module scope sits between global and function scope in the chain.

---

### 🔄 How It Connects (Mini-Map)

```
Global Scope (window / globalThis)
        ↑
        │  (outer scope visible to inner)
Module Scope (ESM only)
        ↑
Function Scope   ← you are here (one of these)
  (created per function call)
        ↑
Block Scope { }
  (created per { } block — let/const only)
        │
   Scope Chain
   (variable lookup walks up the chain)
        ↓
Closure      ← captures scope chain at def time
Hoisting     ← registers declarations in scope
TDZ          ← let/const blocked until init in scope
IIFE         ← creates isolated function scope
```

---

### 💻 Code Example

**Example 1 — Scope chain lookup in action:**

```javascript
const app = 'myApp';   // global scope

function outer() {
  const version = '1.0'; // function scope

  function inner() {
    const feature = 'dark-mode'; // inner function scope

    // Lookup chain: feature → version → app
    console.log(`${app} v${version}: ${feature}`);
    // myApp v1.0: dark-mode
  }

  inner();
  // console.log(feature); // ReferenceError — not visible
}

outer();
```

**Example 2 — Block scope protecting loop variables:**

```javascript
// var — function-scoped, all closures share same i
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log('var:', i), 0);
}
// var: 3  var: 3  var: 3

// let — block-scoped, each iteration is a new scope
for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log('let:', j), 0);
}
// let: 0  let: 1  let: 2
```

**Example 3 — Module scope isolating globals:**

```javascript
// legacy-script.js (classic <script>):
var sharedState = {}; // on window.sharedState

// module.js (type="module"):
var modulePrivate = {}; // NOT on window
// window.modulePrivate === undefined
```

**Example 4 — Shadowing and pitfall:**

```javascript
const MAX = 100;

function process(items) {
  // BAD: accidentally shadows outer MAX
  const MAX = items.length; // shadows — now 0!
  if (items.length > MAX) { // always false!
    trimItems(items);
  }
}

// GOOD: use distinct names or check intended scope
function process(items) {
  if (items.length > MAX) {   // uses outer MAX = 100
    trimItems(items);
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Scope is determined at runtime (dynamic scope) | JavaScript uses lexical (static) scope — determined by code structure at parse time, not by the call chain at runtime |
| var respects block {} boundaries | var is function-scoped, not block-scoped — a var inside if/for/while is visible throughout the enclosing function |
| The global scope is always window | In Node.js, global scope is `global` / `globalThis`; in ESM, top-level variables are module-scoped and never on the global object |
| Shadowing a variable changes the outer binding | Shadowing creates a new binding in the inner scope; the outer binding is untouched but unreachable by its name from the inner scope |
| A function can see variables declared after it in the same scope | Function declarations are hoisted, but at runtime the values of those variables depend on execution order; a function defined before an assignment can still be called after |

---

### 🔥 Pitfalls in Production

**1. Accidental global variable creation**

```javascript
// BAD: missing var/let/const — sloppy mode global
function calculateTotal(items) {
  total = 0;  // no declaration → becomes window.total
  items.forEach(item => total += item.price);
  return total;
}
// Different calls contaminate each other via global total
// Concurrent async calls race on window.total

// GOOD: always declare
function calculateTotal(items) {
  let total = 0; // scoped to function
  items.forEach(item => total += item.price);
  return total;
}
// Use 'use strict' or ESM to make accidental globals throw
```

**2. Variable shadowing causing silent logic bugs**

```javascript
// BAD: inner function shadows config parameter
function applyConfig(config) {
  return function() {
    const config = loadDefaults(); // shadows outer config!
    return merge(config);          // always uses defaults
    // outer config never applied — silent bug
  };
}

// GOOD: use distinct names
function applyConfig(userConfig) {
  return function() {
    const defaultConfig = loadDefaults();
    return merge(defaultConfig, userConfig); // both used
  };
}
```

**3. Incorrect scope assumption with callbacks**

```javascript
// BAD: var scope outlives the loop intent
function attachHandlers(buttons) {
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function() {
      console.log('Button', i, 'clicked');
      // i is always buttons.length — wrong!
    });
  }
}

// GOOD: let creates a new scope per iteration
function attachHandlers(buttons) {
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function() {
      console.log('Button', i, 'clicked'); // correct
    });
  }
}
```

---

### 🔗 Related Keywords

- `var / let / const` — the declaration keywords that define which scope type a binding uses
- `Closure` — a function that retains access to its lexical scope even after the outer scope exits
- `Lexical Environment` — the internal spec structure that implements scope chains at runtime
- `Hoisting` — registers declarations in the correct scope during the creation phase
- `Temporal Dead Zone` — the period before a let/const binding is initialised within its scope
- `IIFE` — Immediately Invoked Function Expression that creates an isolated function scope
- `Module (ESM)` — creates module scope, which sits between global and function scope

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Lexical scoping: where you WRITE code     │
│              │ determines which variables are visible     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Isolating variables with block/fn scope;  │
│              │ designing private state via closures       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Excessive variable shadowing — obscures   │
│              │ which binding a name refers to            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Where you write the variable             │
│              │  is where it lives — not where you use it."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Closure → Lexical Environment → IIFE      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A library author needs to support both `<script>` (global scope) and ES module (`type="module"`) environments. In classic scripts, `var` at the top level attaches to `window` and can be used for "namespacing" like `window.MyLib = ...`. In modules, this approach breaks. Describe exactly why, trace what scope the top-level `var` in a module belongs to, and explain the pattern the library author should use to expose their API reliably in both environments.

**Q2.** JavaScript's `eval()` in non-strict mode can introduce new variables into the current scope at runtime — breaking lexical scope guarantees. V8 degrades its optimisation level for any function that contains `eval()`. Explain the specific mechanism: why does lexical scope enable V8 to optimise variable access into direct memory offsets, and how does dynamic `eval()` break V8's ability to know at parse time exactly which variables a function accesses?

