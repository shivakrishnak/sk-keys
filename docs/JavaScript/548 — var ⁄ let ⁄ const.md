---
layout: default
title: "var / let / const"
parent: "JavaScript"
nav_order: 548
permalink: /javascript/var-let-const/
number: "548"
category: JavaScript
difficulty: ★☆☆
depends_on: Scope, Hoisting, JavaScript Engine (V8)
used_by: Closure, Temporal Dead Zone, Hoisting, Block Scoping, Module pattern
tags: #javascript, #foundational, #browser, #nodejs
---

# 548 — var / let / const

`#javascript` `#foundational` `#browser` `#nodejs`

⚡ TL;DR — Three variable declaration keywords differing in scope (function vs block), hoisting behaviour, and mutability of the binding.

| #548 | Category: JavaScript | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Scope, Hoisting, JavaScript Engine (V8) | |
| **Used by:** | Closure, Temporal Dead Zone, Hoisting, Block Scoping, Module pattern | |

---

### 📘 Textbook Definition

JavaScript provides three variable declaration keywords: **`var`**, **`let`**, and **`const`**. `var` declares a function-scoped variable, is hoisted to the top of its containing function and initialised to `undefined`. `let` declares a block-scoped variable, is hoisted but not initialised (creating a Temporal Dead Zone). `const` declares a block-scoped binding that cannot be reassigned after initialisation, though the value it references (an object or array) may still be mutated. `let` and `const` were introduced in ES2015 (ES6) to address predictability and scoping issues with `var`.

---

### 🟢 Simple Definition (Easy)

`var` is the old way — it leaks out of `if` blocks and `for` loops. `let` and `const` are the modern replacements that stay where you put them. Use `const` for things that won't change, `let` for things that will.

---

### 🔵 Simple Definition (Elaborated)

Before ES6, `var` was the only way to declare variables. Its function-wide scope caused many bugs — a `var` inside an `if` block was visible outside it, and `var` in a `for` loop persisted after the loop finished. ES6 introduced `let` and `const`, which are block-scoped: they exist only within the nearest set of `{}`. `const` additionally prevents reassignment — you can't point the variable at a different value. This doesn't freeze objects though: `const obj = {}; obj.x = 1` still works because you're modifying the object, not changing what `obj` points to.

---

### 🔩 First Principles Explanation

**The problem with function scope:**

```javascript
// var is scoped to the FUNCTION, not the block
function processItems(items) {
  for (var i = 0; i < items.length; i++) {
    var item = items[i]; // var leaks OUT of the loop
  }
  console.log(i);    // 5 — i still exists!
  console.log(item); // last item — still exists!
}

// This looks like it should print 0 and "a":
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// Prints: 3 3 3
// Because all callbacks close over the SAME var i
// which is 3 by the time they execute
```

**Insight — scope should match visual boundaries:**

Code blocks `{}` are natural scope boundaries. Engineers expect a variable inside `if () {}` to not exist outside it. `let` and `const` make this true:

```javascript
// let is scoped to the BLOCK {}
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// Prints: 0 1 2
// Each iteration creates a NEW binding of i
```

**const — communicating intent:**

```
The binding cannot change.
The value may still be mutable.

const x = 5;   x = 6;        // TypeError — reassignment
const arr = []; arr.push(1);  // OK — mutation, not reassignment
const obj = {}; obj.key = 1;  // OK — mutation, not reassignment
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT let/const (only var):**

```
Problem 1: Variable leaking
  if (true) { var x = 1; }
  console.log(x); // 1 — leaks out of if block

Problem 2: Loop variable confusion
  for (var i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 0);
  }
  // Prints 5 5 5 5 5 — not 0 1 2 3 4

Problem 3: Hoisting surprises
  console.log(x); // undefined (not ReferenceError)
  var x = 5;
  // Confusing: x "exists" before declaration

Problem 4: Accidental global
  function fn() { x = 1; } // no var — global!
  fn(); console.log(x); // 1 on global object
```

**WITH let/const:**

```
→ Block scoping — variables live exactly where declared
→ TDZ — access before declaration = ReferenceError
  (not silent undefined as with var)
→ const signals immutable binding — documents intent
→ Loop variables in closures work correctly
→ No accidental hoisting to function top
```

---

### 🧠 Mental Model / Analogy

> `var` is like a **notice board in a break room** — anything you post is visible to everyone in the whole building (function). `let` and `const` are **sticky notes on your own desk** — only visible in the room (block) you're working in. When you leave the room (block ends), the note disappears. `const` is a note written in **permanent marker** — you can't replace it, but if the note says "this box", you can still put things in the box.

"Building" = function scope
"Room (desk)" = block scope `{}`
"Notice board post" = `var` declaration
"Sticky note" = `let` / `const` declaration
"Permanent marker" = `const` binding immutability
"Things in the box" = mutation of the referenced object

---

### ⚙️ How It Works (Mechanism)

**Comparison table:**

```
┌────────────────────────────────────────────────────────┐
│              var         let         const             │
├────────────────────────────────────────────────────────┤
│ Scope        Function    Block       Block             │
│ Hoisted      Yes         Yes (TDZ)   Yes (TDZ)         │
│ Init value   undefined   unset(TDZ)  unset(TDZ)        │
│ Reassign     ✅           ✅           ❌                │
│ Re-declare   ✅ (same fn) ❌           ❌                │
│ Global prop  ✅ (top-lvl) ❌           ❌                │
└────────────────────────────────────────────────────────┘
```

**var hoisting — the silent undefined:**

```javascript
console.log(x); // undefined — var hoisted, not init
var x = 5;
console.log(x); // 5

// Engine sees it as:
var x;          // hoisted to top of function
console.log(x); // undefined
x = 5;
console.log(x); // 5
```

**let/const — Temporal Dead Zone:**

```javascript
console.log(y); // ReferenceError: Cannot access 'y'
                // before initialization
let y = 5;
// y is "hoisted" to block top but not initialized
// The gap between block start and declaration = TDZ
```

**const is not deep immutability:**

```javascript
const config = { retries: 3 };
config.retries = 10;  // ✅ works — mutation
config = {};          // ❌ TypeError — reassignment

// For deep immutability:
const config = Object.freeze({ retries: 3 });
config.retries = 10;  // silently ignored (strict: throws)
```

---

### 🔄 How It Connects (Mini-Map)

```
var/let/const declaration
        ↓
  SCOPE determines visibility:
  ┌──────────────────────┐
  │ var → function scope │
  │ let → block scope    │
  │ const → block scope  │
  └──────────────────────┘
        ↓
  HOISTING determines create-before-use:
  ┌──────────────────────────────────┐
  │ var → hoisted + initialized undf │
  │ let → hoisted + TDZ (no access)  │
  │ const → hoisted + TDZ            │
  └──────────────────────────────────┘
        ↓
  Affects:
  Closure (captures binding, not value)
  Loop variable semantics
  Module pattern design
```

---

### 💻 Code Example

**Example 1 — The classic loop closure bug:**

```javascript
// BAD: var — all timeouts share same i
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log('var:', i), 0);
}
// var: 3
// var: 3
// var: 3

// GOOD: let — each iteration has its own i
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log('let:', i), 0);
}
// let: 0
// let: 1
// let: 2
```

**Example 2 — const in real production code:**

```javascript
// Good convention: const for everything
// let only when reassignment is needed
const MAX_RETRIES = 3;
const BASE_URL = 'https://api.example.com';

async function fetchWithRetry(path) {
  let attempts = 0;  // let because it changes
  while (attempts < MAX_RETRIES) {
    try {
      const res = await fetch(BASE_URL + path);
      const data = await res.json(); // const — no reassign
      return data;
    } catch {
      attempts++;
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| const makes values immutable | const prevents reassigning the binding; object properties can still be changed — use Object.freeze() for shallow immutability |
| let and var behave the same except for scope | var is hoisted and initialised to undefined; let is in the TDZ — accessing let before declaration throws ReferenceError, not undefined |
| var in a block is local to that block | var ignores block boundaries; it's scoped to the enclosing function (or global if no function wraps it) |
| You should never use var anymore | Legacy codebases use it everywhere; understanding var is essential for debugging and code review — ESLint with `no-var` handles new code |

---

### 🔥 Pitfalls in Production

**1. const with mutable objects giving false safety**

```javascript
// BAD: const doesn't protect object contents
const options = { timeout: 5000 };
someLibrary.setOptions(options);
// Library mutates options internally — your const
// won't protect against this

// GOOD: freeze when passing to untrusted code
const options = Object.freeze({ timeout: 5000 });
someLibrary.setOptions(options);
// Library can't modify your config object
```

**2. `var` in async callbacks causing stale closures**

```javascript
// BAD: var in async loop
for (var i = 0; i < urls.length; i++) {
  fetch(urls[i]).then(r => {
    console.log(i, r.status);
    // i is always urls.length when callback fires
  });
}

// GOOD: let — each iteration binds its own i
for (let i = 0; i < urls.length; i++) {
  fetch(urls[i]).then(r => {
    console.log(i, r.status); // correct index
  });
}
```

---

### 🔗 Related Keywords

- `Scope` — defines where a declaration is accessible; block scope is what makes `let`/`const` work
- `Hoisting` — the engine behaviour that makes `var` accessible before its line of code
- `Temporal Dead Zone` — the period between a `let`/`const` binding being created and initialised
- `Closure` — captures variable bindings; `let` in loops creates per-iteration closures correctly
- `Execution Context` — the environment in which variables are resolved; `var` attaches to function context
- `Object.freeze` — provides the shallow immutability that `const` alone does not give objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ var=function-scoped+hoisted; let=block+TDZ│
│              │ const=block+TDZ+no reassignment           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ const by default; let when reassignment   │
│              │ needed; var only in legacy code           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid var in new code — scoping surprises │
│              │ with closures and async callbacks         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "const is a promise to the reader;        │
│              │  let is honesty about mutation."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hoisting → Temporal Dead Zone → Closure   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A React component uses `var` inside a `useEffect` hook with an async loop that fetches user data. After the component unmounts, a fetch completes and tries to call `setState`. Trace why the `var`-based version behaves differently than a `let`-based version when the loop variable is captured in the fetch callback — and explain what additional mechanism (beyond `let` vs `var`) is needed to cleanly abort in-flight fetches on unmount.

**Q2.** JavaScript modules (ESM) implicitly run in strict mode. Explain how `var` behaves differently at the top level of a module versus a classic script — specifically regarding whether it becomes a property of the global object — and why this matters for library code that needs to work in both module and script contexts.

