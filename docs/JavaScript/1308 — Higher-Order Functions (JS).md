---
layout: default
title: "Higher-Order Functions"
parent: "JavaScript"
nav_order: 562
permalink: /javascript/higher-order-functions/
number: "562"
category: JavaScript
difficulty: ★★☆
depends_on: First-Class Functions, Closure, Arrow Functions, Array methods
used_by: Functional Programming, Currying, Memoization, Callbacks, React patterns
tags: #javascript, #intermediate, #browser, #nodejs, #pattern, #algorithm
---

# 562 — Higher-Order Functions

`#javascript` `#intermediate` `#browser` `#nodejs` `#pattern` `#algorithm`

⚡ TL;DR — Functions that accept other functions as arguments, return functions, or both — enabling abstraction over actions, not just values.

| #562 | Category: JavaScript | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | First-Class Functions, Closure, Arrow Functions, Array methods | |
| **Used by:** | Functional Programming, Currying, Memoization, Callbacks, React patterns | |

---

### 📘 Textbook Definition

A **Higher-Order Function (HOF)** is a function that satisfies at least one of these criteria: (1) it accepts one or more functions as arguments, or (2) it returns a function as its result. Higher-order functions are a fundamental abstraction mechanism in functional programming and are central to JavaScript's built-in Array methods (`map`, `filter`, `reduce`, `sort`), Promise-based APIs, event systems, and middleware patterns. They enable parameterisation over behaviour — you can vary what a function does, not just what data it operates on.

---

### 🟢 Simple Definition (Easy)

A higher-order function is a function that works with other functions — either it takes a function as input, or it gives you a function as output (or both).

---

### 🔵 Simple Definition (Elaborated)

Normally, functions take data (numbers, strings, objects) as input and return data as output. Higher-order functions go one step further — they take other functions as input or return functions as output. This lets you abstract over behaviour. Instead of writing "sort these items by name" and "sort these items by date" as two separate functions, you write one `sort` function that takes a comparison function as an argument and lets the caller decide the logic. JavaScript's `Array.prototype.map`, `filter`, and `reduce` are the most used examples, but the same principle drives callbacks, middleware chains, decorators, and React hooks.

---

### 🔩 First Principles Explanation

**Abstraction over data vs abstraction over behaviour:**

```
Low-level code: repeat logic, vary only data
  function doubleFirst(arr)  { return arr[0] * 2; }
  function doubleSecond(arr) { return arr[1] * 2; }
  // duplicate logic — only index differs

Medium: abstract over data
  function doubleAt(arr, i)  { return arr[i] * 2; }
  // better — one function, index as param

High: abstract over behaviour (HOF)
  function transform(arr, fn) { return arr.map(fn); }
  transform([1,2,3], x => x * 2);   // double
  transform([1,2,3], x => x ** 2);  // square
  // behaviour itself is a parameter
```

**The power: functions compose:**

Because HOFs accept and return functions, you can build complex pipelines from simple pieces without coupling them:

```javascript
const pipeline = (...fns) => x => fns.reduce((v, f) => f(v), x);

const processUser = pipeline(
  normalise,   // string → normalised
  validate,    // add validation flags
  formatOutput // format for API response
);

users.map(processUser);
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT higher-order functions:**

```
Without HOFs — every variation requires new code:

  function sumPositives(arr) {
    let t = 0;
    for (let i of arr) if (i > 0) t += i;
    return t;
  }
  function sumNegatives(arr) {
    let t = 0;
    for (let i of arr) if (i < 0) t += i;
    return t;
  }
  function sumEven(arr) {
    let t = 0;
    for (let i of arr) if (i % 2 === 0) t += i;
    return t;
  }
  // Three functions, 80% duplicate code

  WITH HOF (filter + reduce):
  arr.filter(x => x > 0).reduce((t, x) => t + x, 0);
  arr.filter(x => x < 0).reduce((t, x) => t + x, 0);
  arr.filter(x => x % 2 === 0).reduce((t, x)=>t+x, 0);
  // Same logic, behaviour from caller
```

**WITH higher-order functions:**

```
→ Extract patterns once (map/filter/reduce)
→ Swap behaviour without rewriting structure
→ Compose complex pipelines from simple functions
→ Middleware chains (Express, Redux, Koa)
→ Decorator pattern without class boilerplate
→ Async control flow (retry, debounce, throttle)
```

---

### 🧠 Mental Model / Analogy

> A higher-order function is like a **contract worker template**. A regular function is a fixed contract: "clean the office." A HOF is an **HOF framework**: "here's a building — supply your own cleaning staff and supplies, we handle the schedule." The HOF provides structure (iterate over array, handle timing, manage retries) while the caller provides the specific behaviour (what to do per item, what to do on failure).

"Building + schedule" = the HOF structure (iteration, control flow)
"Your own cleaning staff" = the function argument (the callback)
"Result of hiring" = the HOF's return value or side effects
"Providing a new HOF template" = a HOF that returns a function

---

### ⚙️ How It Works (Mechanism)

**The three categories of HOFs:**

```
┌───────────────────────────────────────────────┐
│  HOF CATEGORIES                               │
├───────────────────────────────────────────────┤
│  1. TAKES fn as argument                      │
│     array.map(fn)                             │
│     array.filter(predicate)                   │
│     array.reduce(reducer, initial)            │
│     array.sort(comparator)                    │
│     setTimeout(fn, delay)                     │
│     element.addEventListener(event, fn)       │
│                                               │
│  2. RETURNS a function                        │
│     function multiplier(n) { return x=>x*n } │
│     bind(context, ...args)                    │
│     memoize(fn) → memoised fn                 │
│     debounce(fn, ms) → debounced fn           │
│                                               │
│  3. BOTH (takes and returns)                  │
│     function compose(...fns) {                │
│       return x => fns.reduceRight((v,f)=>f(v),x)│
│     }                                        │
│     Redux middleware signature               │
└───────────────────────────────────────────────┘
```

**Composing HOFs:**

```javascript
// Each step returns a new array/function — chainable
const result = employees
  .filter(e => e.isActive)              // HOF: takes predicate
  .map(e => ({ ...e, tax: e.salary * 0.2 })) // HOF: transforms
  .sort((a, b) => b.salary - a.salary); // HOF: comparator
```

---

### 🔄 How It Connects (Mini-Map)

```
First-Class Functions
(functions as values — prerequisite)
        ↓
  HIGHER-ORDER FUNCTIONS  ← you are here
  (take fn as arg OR return fn)
        ↓
  ┌──────────────────────────────────────────┐
  │  Built-in HOFs: map, filter, reduce      │
  │  Custom HOFs: debounce, memoize, retry   │
  │  Composition: compose, pipe              │
  │  Middleware: Express/Redux chain         │
  └──────────────────────────────────────────┘
        ↓
  Currying     (pure HOF-returns-fn pattern)
  Closure      (HOF captures via closure)
  Callbacks    (HOF takes fn as arg)
  Decorators   (HOF wraps another fn)
```

---

### 💻 Code Example

**Example 1 — map, filter, reduce (built-in HOFs):**

```javascript
const orders = [
  { id: 1, amount: 200, status: 'paid' },
  { id: 2, amount: 450, status: 'pending' },
  { id: 3, amount: 150, status: 'paid' },
  { id: 4, amount: 800, status: 'paid' },
];

const totalPaid = orders
  .filter(o => o.status === 'paid')    // HOF: predicate
  .map(o => o.amount)                   // HOF: transform
  .reduce((sum, n) => sum + n, 0);      // HOF: accumulate

totalPaid; // 1150
```

**Example 2 — Custom HOF: retry with backoff:**

```javascript
function withRetry(fn, maxTries = 3, delayMs = 500) {
  return async function(...args) {
    let lastErr;
    for (let attempt = 1; attempt <= maxTries; attempt++) {
      try {
        return await fn(...args);     // calls the wrapped fn
      } catch (err) {
        lastErr = err;
        if (attempt < maxTries) {
          await new Promise(r =>
            setTimeout(r, delayMs * attempt) // backoff
          );
        }
      }
    }
    throw lastErr;
  };
}

const fetchUser = withRetry(
  (id) => fetch(`/api/users/${id}`).then(r => r.json()),
  3,
  200
);
await fetchUser(42); // auto-retries up to 3 times
```

**Example 3 — Function composition:**

```javascript
// compose: right-to-left application
const compose = (...fns) =>
  x => fns.reduceRight((v, f) => f(v), x);

// pipe: left-to-right application (more readable)
const pipe = (...fns) =>
  x => fns.reduce((v, f) => f(v), x);

const transform = pipe(
  str => str.trim(),
  str => str.toLowerCase(),
  str => str.replace(/\s+/g, '-'),
);

transform('  Hello World  '); // 'hello-world'
```

**Example 4 — Decorator HOF pattern:**

```javascript
// Cross-cutting concern: logging any function
function withLogging(fn, name = fn.name) {
  return function(...args) {
    console.time(name);
    const result = fn.apply(this, args);
    console.timeEnd(name);
    return result;
  };
}

const slowSort = arr => [...arr].sort();
const loggedSort = withLogging(slowSort, 'sort');
loggedSort([3, 1, 2]); // logs: "sort: 0.123ms"
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| map/filter/reduce are the only higher-order functions | Any function that takes or returns a function is a HOF — setTimeout, addEventListener, Promise.then, Redux middleware, React's useCallback all qualify |
| HOFs are a functional programming concept irrelevant to OOP | HOFs are pervasive in OOP JS too — event listeners, middleware, decorators all use HOFs in class-based code |
| HOFs are always slower than explicit loops | V8 optimises built-in array method HOFs well; explicit loops are marginally faster only in specific benchmark scenarios. Profile before optimising |
| HOFs must be pure (no side effects) | HOFs can have side effects (logging, network, DOM mutations). Purity is a separate concept from higher-order |

---

### 🔥 Pitfalls in Production

**1. Accidentally mutating in map() instead of transforming**

```javascript
// BAD: map callback mutates original — surprise!
const users = [{ name: 'Alice', active: true }];
users.map(u => {
  u.processed = true; // mutates ORIGINAL object
  return u;
});
// users[0].processed === true — side effect in map

// GOOD: create new objects
users.map(u => ({ ...u, processed: true }));
// Original users unchanged — pure transformation
```

**2. reduce used where map/filter is clearer**

```javascript
// BAD: reduce doing simple filtering job — obscure
const activeNames = users.reduce((acc, u) => {
  if (u.active) acc.push(u.name);
  return acc;
}, []);

// GOOD: filter + map — readable chain
const activeNames = users
  .filter(u => u.active)
  .map(u => u.name);
```

**3. Creating new HOF wrappers in render paths**

```javascript
// BAD: withLogging creates new fn on every render
function Component({ items }) {
  const handleClick = withLogging(
    (item) => selectItem(item) // new fn every render
  );
  return items.map(i =>
    <Item onClick={() => handleClick(i)} key={i.id} />
  );
}

// GOOD: memoize the wrapped function
const handleClick = useMemo(
  () => withLogging(selectItem),
  [] // stable reference
);
```

---

### 🔗 Related Keywords

- `First-Class Functions` — the prerequisite property that enables HOFs to exist
- `Closure` — HOFs that return functions rely on closures to capture their creation-time state
- `Array.prototype.map/filter/reduce` — the most-used built-in HOFs in JavaScript
- `Currying` — a pattern where a function returns functions to enable partial application
- `Callbacks` — the most common form of "function as argument" HOF usage
- `Memoization (JS)` — a HOF that wraps a function and adds a cache layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Takes fn as arg or returns fn;            │
│              │ abstracts over behaviour, not just data   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Abstracting iteration, decorating fns,    │
│              │ building composable pipelines             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Deep chained maps over huge arrays where  │
│              │ one explicit reduce is significantly faster│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Give me the logic, I'll provide          │
│              │  the structure."                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Currying → Partial Application →          │
│              │ Function Composition                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** React's `useCallback(fn, deps)` is a HOF (it takes a function and returns one) that memoises the function reference across renders. Explain the specific problem it solves — not "performance" generally, but the exact mechanism by which a new function reference on each render causes child re-renders — and describe the precise condition under which `useCallback` genuinely helps vs the common case where it adds complexity with no benefit.

**Q2.** `Array.prototype.reduce` is Turing-complete — `map`, `filter`, `find`, `some`, `every`, and `flat` can all be implemented using `reduce`. This seems to suggest `reduce` is the "universal" HOF and others are redundant. Argue the case for NOT using `reduce` for everything, specifically in terms of: (a) readability cost, (b) intermediate garbage collection behaviour when compared to chained map+filter, and (c) the one case where `reduce` is the correct tool with no readable alternative.

