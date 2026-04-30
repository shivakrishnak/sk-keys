---
layout: default
title: "First-Class Functions"
parent: "JavaScript"
nav_order: 26
permalink: /javascript/first-class-functions/
number: "26"
category: JavaScript
difficulty: ★☆☆
depends_on: Functions, var / let / const, Scope
used_by: Higher-Order Functions, Callbacks, Closure, Currying, Functional Programming
tags: #javascript, #foundational, #browser, #nodejs, #pattern
---

# 26 — First-Class Functions

`#javascript` `#foundational` `#browser` `#nodejs` `#pattern`

⚡ TL;DR — Functions in JavaScript are values: they can be assigned to variables, passed as arguments, returned from other functions, and stored in data structures.

| #26 | Category: JavaScript | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Functions, var / let / const, Scope | |
| **Used by:** | Higher-Order Functions, Callbacks, Closure, Currying, Functional Programming | |

---

### 📘 Textbook Definition

A programming language is said to have **first-class functions** when functions are treated as first-class citizens — they have the same rights as any other value in the language. In JavaScript, functions can be: assigned to variables and object properties, passed as arguments to other functions, returned as the result of a function call, stored in arrays and other data structures, and compared by reference. Functions in JavaScript are objects — they are instances of `Function.prototype` — and can have properties added to them.

---

### 🟢 Simple Definition (Easy)

In JavaScript, a function is just a value — like a number or a string. You can store it in a variable, pass it around, and return it from another function. You can treat it exactly like any other piece of data.

---

### 🔵 Simple Definition (Elaborated)

In many older languages, functions are special — you can call them, but you can't pass them as data. JavaScript (and other functional languages) treats functions as ordinary values. This enables powerful patterns: you can pass a function to `setTimeout` (callback), to `Array.map` (transformation), or return a function from another function (factory / closure). Almost every async pattern in JavaScript — callbacks, Promises, event listeners — relies on the ability to pass functions as arguments. First-class functions are what makes JavaScript's functional programming patterns work.

---

### 🔩 First Principles Explanation

**What "first-class" means formally:**

A type is "first-class" if it can appear in any context where any other value can appear. For functions in JavaScript:

```
Can a function...

  Be stored in a variable?     const fn = () => {};         ✅
  Be stored in an array?       const arr = [fn, fn2];       ✅
  Be stored in object?         const obj = { method: fn }; ✅
  Be passed as argument?       setTimeout(fn, 1000);        ✅
  Be returned from function?   return () => {};             ✅
  Have properties added?       fn.maxRetries = 3;           ✅
  Be compared by reference?    fn === fn2                   ✅
```

**Why this matters — the patterns it enables:**

```
┌────────────────────────────────────────────────────────┐
│  WHAT FIRST-CLASS FUNCTIONS UNLOCK                     │
├────────────────────────────────────────────────────────┤
│  Callbacks: pass fn to setTimeout, fetch, addEventListener│
│  HOFs: map, filter, reduce take fn as argument         │
│  Closures: return fn that remembers its scope          │
│  Currying: return fn that waits for more arguments     │
│  Memoization: cache results via closure over Map        │
│  Strategy pattern: swap behaviour at runtime via fn ref│
│  Middleware: chain of fns (Express, Redux)             │
└────────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT first-class functions:**

```
Without first-class functions (function-as-value):

  Cannot do: setTimeout(handler, 1000)
  → Must use language-level "later" construct
  → Every async pattern requires compiler support

  Cannot do: [1,2,3].map(x => x * 2)
  → Must write explicit for-loop every time
  → Can't abstract over iteration behaviour

  Cannot do: Express middleware chain
  app.use(fn1, fn2, fn3)
  → Each middleware must be hard-coded, not composable

  Real languages without FCF: early BASIC, COBOL
  → No callbacks, no event handlers, no functional style
```

**WITH first-class functions:**

```
→ Event-driven programming: pass handler to listener
→ Array methods: map, filter, reduce all take fn args
→ async/Promises: .then(callback) is first-class passing
→ Dependency injection: pass strategy as function
→ Compose complex behaviour from simple functions
```

---

### 🧠 Mental Model / Analogy

> Think of functions as **tools in a toolbox**. In languages without first-class functions, tools are fixed to their workbench — you can only use a drill when you're at the drilling station. In JavaScript, each tool is a portable object — you can pick up a drill, hand it to a colleague, put it in a bag, or attach it to a robot arm. The drill's *capability* is the same regardless of who holds it or where it is.

"Tool fixed to workbench" = non-first-class function (call-only)
"Portable tool" = first-class function (can be passed, stored, returned)
"Handing drill to colleague" = passing function as argument
"Attaching to robot arm" = returning function from a factory function

---

### ⚙️ How It Works (Mechanism)

**Functions as values — all the forms:**

```javascript
// 1. Function expression stored in variable
const add = function(a, b) { return a + b; };

// 2. Arrow function stored in variable
const multiply = (a, b) => a * b;

// 3. Function stored in an object
const math = {
  add: (a, b) => a + b,
  sub: (a, b) => a - b,
};

// 4. Function stored in an array
const operations = [
  (a, b) => a + b,
  (a, b) => a - b,
  (a, b) => a * b,
];
operations[0](3, 4); // 7

// 5. Function passed as argument
[1, 2, 3].map(x => x * 2); // [2, 4, 6]

// 6. Function returned from function
function multiplier(factor) {
  return (value) => value * factor; // returns function
}
const triple = multiplier(3);
triple(5); // 15

// 7. Function with properties
function request(url) { fetch(url); }
request.timeout = 5000;
request.retries = 3;
```

---

### 🔄 How It Connects (Mini-Map)

```
Functions defined in JavaScript
        ↓
  FIRST-CLASS FUNCTIONS  ← you are here
  (functions are values)
        ↓
  ┌───────────────────────────────────────────┐
  │  Enables:                                 │
  │  Higher-Order Functions → map/filter/HOFs │
  │  Callbacks → async patterns               │
  │  Closures → captured scope               │
  │  Currying → partial application          │
  │  Strategy Pattern → swappable behaviour  │
  │  Middleware chains → Express, Redux       │
  └───────────────────────────────────────────┘
        ↓
  Foundation of JavaScript's
  functional programming style
```

---

### 💻 Code Example

**Example 1 — Passing functions as arguments:**

```javascript
// Strategy pattern: swap behaviour without if/else
function processItems(items, strategy) {
  return items.map(strategy);
}

const double  = x => x * 2;
const square  = x => x ** 2;
const negate  = x => -x;

processItems([1, 2, 3], double); // [2, 4, 6]
processItems([1, 2, 3], square); // [1, 4, 9]
processItems([1, 2, 3], negate); // [-1, -2, -3]
```

**Example 2 — Returning functions:**

```javascript
// Factory: creates specialised functions
function createValidator(min, max) {
  return function(value) {       // returns a function
    return value >= min && value <= max;
  };
}

const isValidAge     = createValidator(0, 120);
const isValidPercent = createValidator(0, 100);

isValidAge(25);     // true
isValidAge(200);    // false
isValidPercent(75); // true
```

**Example 3 — Functions as object methods + references:**

```javascript
const button = { label: 'Submit' };

function onClick() {
  console.log(`${this.label} clicked`);
}

button.handler = onClick; // store reference
button.handler();         // "Submit clicked"

// Same function reference:
console.log(button.handler === onClick); // true
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "First-class function" means functions are special | It means the opposite — functions are NOT special. They're ordinary values like strings and numbers, with all the same rights |
| Passing a function as an argument copies it | Functions are passed by reference. The caller and callee reference the same function object |
| Functions are objects, so they're slow | V8 heavily optimises function calls. The first-class nature enables caching and inlining by the JIT compiler |
| Only functional programming languages have first-class functions | Python, Ruby, Go, Kotlin, Rust, Swift — all modern languages support first-class functions to some degree |

---

### 🔥 Pitfalls in Production

**1. Passing unbound methods as callbacks**

```javascript
// BAD: method loses this when passed as callback
class Logger {
  prefix = '[LOG]';
  log(msg) { console.log(`${this.prefix} ${msg}`); }
}
const logger = new Logger();

// this lost — log is first-class but this = undefined
setTimeout(logger.log, 0, 'hello');
// TypeError: Cannot read properties of undefined

// GOOD: pass bound version
setTimeout(logger.log.bind(logger), 0, 'hello');
// Or: setTimeout(() => logger.log('hello'), 0);
```

**2. Accidental call vs pass confusion**

```javascript
// BAD: calling the function instead of passing it
button.addEventListener('click', handleClick()); // calls now!
// handleClick() runs immediately, returns undefined
// undefined is registered as the listener → does nothing

// GOOD: pass the reference, don't call
button.addEventListener('click', handleClick);   // ✅
// Or with args: () => handleClick(arg)
```

---

### 🔗 Related Keywords

- `Higher-Order Functions` — functions that take or return other functions; possible only with FCF
- `Callbacks` — functions passed as arguments to be called later; the most common FCF use
- `Closure` — a function returned from another function, retaining access to its scope
- `Currying` — returning nested functions that accumulate arguments; enabled by returning functions
- `Arrow Functions` — the modern concise syntax for function values

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Functions are values — assign, pass,      │
│              │ return, store, compare by reference       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — callbacks, HOFs, factories,      │
│              │ strategy pattern, middleware chains       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — it's a language property; avoid     │
│              │ accidental fn call when passing reference  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A function is just a value with          │
│              │  parentheses that make things happen."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Higher-Order Functions → Closure →        │
│              │ Currying                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Redux's middleware signature is `store => next => action => { ... }` — three levels of returned functions. Explain what property of first-class functions makes this pattern possible, what each level of the returned function captures via closure, and why this specific three-level curried form enables middleware to be composed in a pipeline without any of them having to know about each other at definition time.

**Q2.** In V8, frequently called functions are JIT-compiled into optimised machine code. But when a first-class function is called via a variable (`const fn = getStrategy(); fn(x)`), V8 may issue a "polymorphic call" if different strategies are stored in `fn` over time. Explain what makes a call site polymorphic vs monomorphic in V8's terms, how this impacts JIT compilation, and what code pattern you would use to keep a hot strategy-function call site monomorphic.

