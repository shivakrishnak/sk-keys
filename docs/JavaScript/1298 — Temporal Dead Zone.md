---
layout: default
title: "Temporal Dead Zone (TDZ)"
parent: "JavaScript"
nav_order: 1298
permalink: /javascript/temporal-dead-zone-tdz/
number: "1298"
category: JavaScript
difficulty: ★★☆
depends_on: Hoisting, var / let / const, Scope, Execution Context
used_by: let / const initialisation, Class declarations, Block scoping
tags: #javascript, #intermediate, #browser, #nodejs, #internals
---

# 1298 — Temporal Dead Zone (TDZ)

`#javascript` `#intermediate` `#browser` `#nodejs` `#internals`

⚡ TL;DR — The period between a let or const binding being registered in scope and its initialisation line being executed, during which any access throws a ReferenceError.

| #1298 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | Hoisting, var / let / const, Scope, Execution Context | |
| **Used by:** | let / const initialisation, Class declarations, Block scoping | |

---

### 📘 Textbook Definition

The **Temporal Dead Zone (TDZ)** is the region of a program scope in which a `let`, `const`, or `class` binding has been registered by the hoisting mechanism but has not yet been initialised. Any read or write access to the variable while it is in the TDZ results in a `ReferenceError`. The TDZ begins at the start of the enclosing block (where the binding is registered) and ends at the precise source-code position of the declaration statement. This behaviour is specified in the ECMAScript 2015 specification and is intentional — it makes use-before-declare a runtime error rather than the silent `undefined` produced by `var`.

---

### 🟢 Simple Definition (Easy)

The TDZ is the "off-limits" period for a `let` or `const` variable. From the moment a block starts until the declaration line runs, the variable exists but touching it throws an error — by design.

---

### 🔵 Simple Definition (Elaborated)

When JavaScript sees a `let x = 5` declaration, it does two things: first, during hoisting, it marks that `x` exists in this scope; second, when the actual line runs, it initialises `x` to `5`. The TDZ is the gap between these two moments. Unlike `var` (which is silently `undefined` during this gap), `let` and `const` throw a `ReferenceError` if you try to read them during the TDZ. This is intentional — it turns a common class of bugs (using a variable before you've set it up) into loud errors rather than silent `undefined` surprises.

---

### 🔩 First Principles Explanation

**The problem with var's silent undefined:**

```javascript
// Classic var bug — no error signal
function getDiscount(user) {
  console.log(level); // undefined — no error!
  // Developer expects ReferenceError
  // but gets undefined — bugs slip through

  if (user.isPremium) {
    var level = 'gold';
  }
  return level; // undefined for non-premium users
}
```

**Constraint — hoisting is necessary (mutual recursion), but initialisation order should be explicit:**

The engine needs to know all bindings in a scope before execution starts (for correct scope chain resolution). But initialising them early creates the "undefined before declaration" footgun.

**Insight — split registration from initialisation:**

```
┌──────────────────────────────────────────────┐
│  TDZ DESIGN                                  │
│                                              │
│  Hoist: register binding in scope            │
│  ← this must happen for scope chain to work  │
│                                              │
│  Init: assign initial value                  │
│  ← this should NOT happen until the line     │
│  runs — keep the variable inaccessible first │
│                                              │
│  TDZ = gap between hoist and init            │
│  Access in TDZ = ReferenceError (intentional)│
└──────────────────────────────────────────────┘
```

This turns the silent `undefined` of `var` into a loud `ReferenceError` for `let`/`const` — much easier to debug.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT TDZ (hypothetical — if let behaved like var):**

```
Same code as var — silent undefined bugs:

  function setup() {
    onClick(() => process(config));  // captures config

    // ... many lines ...

    let config = loadConfig(); // intended to be the
                               // config used by onClick
    // Without TDZ: config = undefined in closure
    // at time of onClick call — silent bug
    // With TDZ: ReferenceError at the capture point
    //            → explicit error → fix it
  }
```

**WITH TDZ:**

```
→ Use-before-declare is a loud ReferenceError
  not silent undefined
→ Blocks express clear intent: variables are
  valid only after declaration
→ Class constructors correctly throw if
  super() not called before this access
  (extends + TDZ enforces proper init order)
→ Encourages declaration-at-use-site style
  → cleaner code structure
```

---

### 🧠 Mental Model / Analogy

> Imagine a hotel room that's been **booked but not yet checked into**. The room exists in the hotel's system (it's registered) but you cannot enter it yet — the front desk will stop you. The moment you complete check-in (the declaration line executes), the room is yours to use. The TDZ is the period between the booking and check-in. Trying to enter before check-in is a hard error, not a "hmm, the room seems empty" (undefined) situation.

"Hotel room booked" = binding registered during hoisting
"Can't enter yet" = TDZ — ReferenceError on access
"Check-in completes" = declaration line executes, binding initialised
"Room is yours" = variable accessible and holds its value
"var's behaviour" = the room is just empty (undefined) during the wait — no hard error

---

### ⚙️ How It Works (Mechanism)

**TDZ scope — starts at block open, ends at declaration:**

```javascript
// Block starts here: y enters TDZ
{
  // TDZ for y — access throws ReferenceError
  console.log(y); // ReferenceError!

  // TDZ ends here ↓
  let y = 10;
  // y is now initialised

  console.log(y); // 10 ✅
}
// y out of scope here
```

**TDZ with temporal (time), not textual (space):**

The name "temporal" refers to execution time, not code position. A closure can capture a TDZ variable and avoid the error if it's called after initialisation:

```javascript
function outer() {
  // x in TDZ here
  const fn = () => x; // captures x — not yet accessed

  let x = 42;         // TDZ ends
  return fn;
}

outer()(); // 42 — fn called after x initialised → OK
```

**TDZ applies to destructuring and default parameters:**

```javascript
// TDZ in default parameter — subtle!
function fn(a = b, b = 1) {
  // a's default (b) is evaluated when a is needed
  // at that moment, b is still in TDZ
  // → ReferenceError
}
fn(); // ReferenceError

function fn(b = 1, a = b) { // safe — b inited first
  return [a, b];
}
fn(); // [1, 1] ✅
```

**TDZ and classes:**

```javascript
// Class declaration is TDZ (like const)
const obj = new MyClass(); // ReferenceError
class MyClass { constructor() {} }

// Inside a subclass constructor:
class Animal {
  constructor() { this.type = 'animal'; }
}
class Dog extends Animal {
  constructor() {
    console.log(this); // ReferenceError — this in TDZ
    super();           // super() MUST come first
    console.log(this); // OK after super()
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Block / Function starts executing
        ↓
  Hoisting phase:
  let/const bindings registered in scope
  var → init to undefined (no TDZ)
  let/const → registered but NOT initialised
        ↓
  ┌─────────────────────────────────┐
  │  TDZ ACTIVE  ← you are here    │
  │  Any access → ReferenceError   │
  └─────────────────────────────────┘
        ↓
  Declaration line executes in code
  (let x = 5;  or  const y = [];)
        ↓
  TDZ LIFTED — variable initialised
  and accessible normally
        ↓
  Block ends → binding destroyed
  (block scope ends)
```

---

### 💻 Code Example

**Example 1 — TDZ basics:**

```javascript
// let TDZ:
{
  // y is hoisted but in TDZ
  console.log(y); // ReferenceError

  let y = 5;      // TDZ ends here, y = 5
  console.log(y); // 5
}

// contrast with var:
{
  console.log(z); // undefined (no error)
  var z = 5;
  console.log(z); // 5
}
```

**Example 2 — Closure captures TDZ binding safely:**

```javascript
let initialised = false;

function makeGetter() {
  // count is in TDZ at this point in the block
  const get = () => count; // safe — not calling yet
  let count = 0;           // TDZ ends
  initialised = true;
  return get;
}

const getCount = makeGetter();
getCount(); // 0 — safe, count is initialised
```

**Example 3 — typeof with TDZ (a gotcha):**

```javascript
// typeof with undeclared var — safe, returns "undefined"
console.log(typeof undeclaredVar); // "undefined"

// typeof with let in TDZ — NOT safe
{
  console.log(typeof x); // ReferenceError — x in TDZ!
  let x = 1;
}
// typeof is NOT a safe check for let/const variables
```

**Example 4 — Class TDZ enforcing super() call order:**

```javascript
class Base {
  constructor() { this.x = 1; }
}

class Child extends Base {
  constructor() {
    // `this` is in TDZ until super() is called
    this.y = 2;  // ReferenceError: must call super first
    super();
  }
}

class CorrectChild extends Base {
  constructor() {
    super();     // initialises `this`
    this.y = 2;  // ✅ safe now
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| let and const are not hoisted (that's why TDZ exists) | They ARE hoisted — TDZ exists precisely because they are hoisted but not initialised. The binding is in scope from block start |
| typeof is always safe to call on any identifier | typeof on a let/const in TDZ still throws ReferenceError — it's only safe for genuinely undeclared (non-hoisted) identifiers |
| TDZ only matters when you write code in wrong order | TDZ also affects closures that capture variables and default parameter evaluation — order-of-execution matters, not just code order |
| The TDZ is a performance optimisation | TDZ is a correctness and safety feature — it exists to surface use-before-declare bugs, not for performance reasons |
| class declarations can be used before they appear | class declarations follow TDZ rules like const — constructing before declaration throws ReferenceError |

---

### 🔥 Pitfalls in Production

**1. TDZ bug hiding in module initialisation order**

```javascript
// moduleA.js
import { config } from './moduleB.js';
export const value = config.timeout * 2;
// If moduleB imports back from moduleA (circular):
// config may be in TDZ when value is computed
// → ReferenceError at module load time

// GOOD: break circular dependency OR use
// lazy evaluation
export const getValue = () => config.timeout * 2;
// Function is defined immediately; config only
// read when called — after all modules initialised
```

**2. Default parameter TDZ order error**

```javascript
// BAD: default uses a later parameter
function createClient(
  timeout = retries * 1000, // retries in TDZ here!
  retries = 3
) {}
createClient(); // ReferenceError

// GOOD: put dependencies before their dependents
function createClient(
  retries = 3,
  timeout = retries * 1000  // retries already init
) {}
createClient(); // ✅ timeout = 3000
```

**3. Destructuring with TDZ**

```javascript
// BAD: confusing TDZ in destructuring
let { a, b } = { a: 1, b: 2 };  // OK

// But:
let x = x + 1; // ReferenceError — x in TDZ on right side
// The left-side x is being declared;
// the right-side x references it while in TDZ

// GOOD: break into two statements
let x = 0;
x = x + 1; // ✅
```

---

### 🔗 Related Keywords

- `Hoisting` — the mechanism that creates the TDZ by registering bindings before initialisation
- `var / let / const` — var has no TDZ; let and const both have TDZ until declaration line
- `Execution Context` — the creation phase of execution contexts is where TDZ bindings are registered
- `Scope` — TDZ exists within the scope where the let/const is declared, from block start
- `Class` — class declarations use the same TDZ rules; `super()` in subclass constructors is TDZ-enforced

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ let/const hoisted but blocked until init; │
│              │ access before declaration = ReferenceError│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding why let/const throw before  │
│              │ declaration; debugging circular imports   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — TDZ is engine behaviour, not a      │
│              │ feature you opt into; understand it        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The variable exists but it's not         │
│              │  yours to touch yet."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Scope → Execution Context → Closure       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two ES modules have a circular dependency: module A imports `config` from module B for use in a top-level `const`, and module B imports `handler` from module A. The runtime evaluates module A first. When does `config` exit its TDZ, and why might `handler` still be in TDZ when module B evaluates? Trace the exact evaluation order and explain what change to the exports would make both modules load safely.

**Q2.** Consider a `switch` statement with `let` declarations in multiple cases and no `break` statements (fall-through). Explain how the TDZ interacts with fall-through: if case B declares `let x = 2` and the code falls-through to case C which also accesses `x`, does case C see the TDZ error or the value `2`? What does this reveal about the mental model of "block scope" and where the actual block boundaries are in a `switch`?

