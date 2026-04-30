---
layout: default
title: "Closure"
parent: "JavaScript"
nav_order: 1300
permalink: /javascript/closure/
number: "1300"
category: JavaScript
difficulty: ★★★
depends_on: Scope, Lexical Environment, Execution Context, var / let / const, Functions
used_by: Memoization, Module Pattern, Currying, React Hooks, Callbacks, Event Handlers
tags: #javascript, #advanced, #browser, #nodejs, #internals, #deep-dive
---

# 1300 — Closure

`#javascript` `#advanced` `#browser` `#nodejs` `#internals` `#deep-dive`

⚡ TL;DR — A function that retains a live reference to the variables of its enclosing lexical scope even after that scope has finished executing.

| #1300 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | Scope, Lexical Environment, Execution Context, var / let / const, Functions | |
| **Used by:** | Memoization, Module Pattern, Currying, React Hooks, Callbacks, Event Handlers | |

---

### 📘 Textbook Definition

A **closure** is the combination of a function and the **lexical environment** in which it was defined. When a function is created, it captures a reference to its outer scope's variables. These captured references remain live even after the outer function has returned and its execution context has been popped from the call stack. The garbage collector cannot reclaim heap-allocated variables captured by a closure as long as the closure itself is reachable. Closures are a direct consequence of JavaScript's lexical scoping model and first-class functions.

---

### 🟢 Simple Definition (Easy)

A closure is a function that remembers the variables from the place where it was created — even after the outer function has finished. The inner function carries its birthplace with it wherever it goes.

---

### 🔵 Simple Definition (Elaborated)

In most languages, when a function finishes, its local variables are destroyed. JavaScript is different: if a function creates and returns another function (or passes it as a callback), the inner function keeps a living reference to the outer function's variables — even though the outer function is gone. This "memory" is a closure. The inner function doesn't just remember the value — it captures the actual variable, so it sees the variable's latest value. Closures are the foundation of JavaScript patterns like private state, factory functions, memoization, and how React's `useState` hooks maintain component state between renders.

---

### 🔩 First Principles Explanation

**Problem — functions need persistent private state:**

Without a mechanism to keep local variables alive beyond a function call, you're forced to use global variables or objects to share state between related operations — which is fragile and leaky.

**Constraint — JavaScript is lexically scoped and has first-class functions:**

Since functions can be returned and passed around, and scope is determined by where functions are written, a function written inside another function "knows" about the outer variables — and must continue to know them even after the outer function finishes.

**What happens in memory:**

```
┌──────────────────────────────────────────────┐
│  EXECUTION                                   │
│                                              │
│  outer() runs:                               │
│  ┌──────────────────────────┐                │
│  │ Execution Context        │                │
│  │  count = 0  ←────────────┼─────┐          │
│  │  returns inner fn ──┐    │     │ closure  │
│  └──────────────────────┘   │     │ reference│
│  outer() frame popped       │     │          │
│  (but count NOT GC'd)       │     │          │
│                             ↓     │          │
│  inner fn on heap:     ┌─────────────────┐   │
│  (reachable via ref)   │ fn + [[Scope]]──┘   │
│                        └─────────────────┘   │
│                                              │
│  count stays alive as long as inner fn lives │
└──────────────────────────────────────────────┘
```

**The closure captures the binding (not the value):**

This is the most critical distinction. The closure holds a reference to the variable itself, not a snapshot of its value at capture time. If the variable changes later, the closure sees the new value.

```javascript
function makeCounter() {
  let count = 0;
  return {
    increment: () => ++count,
    get: () => count,
  };
}

const c = makeCounter();
c.increment(); // count becomes 1
c.increment(); // count becomes 2
c.get();       // 2 — sees the CURRENT binding, not 0
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT closures (hypothetical — no captured scope):**

```
Without closures:

  Problem 1: No private state without objects
    // Only option for stateful operations:
    let globalCount = 0; // leaks to everyone
    function increment() { globalCount++; }
    // Multiple "counters" would share state

  Problem 2: Callbacks can't close over context
    const user = { id: 42 };
    fetch('/profile').then(function(data) {
      // Without closure: user.id is 'undefined' here
      // The context of user is lost without closure
      updateUI(user.id, data); // broken
    });

  Problem 3: No factory functions
    // Can't create independent instances with
    // private state — every invocation shares state
    // Forces class-based OOP for all stateful code

  Problem 4: Memoization impossible
    // Can't cache results without persisting
    // the cache between calls
```

**WITH closures:**

```
→ Private state without objects or classes
→ Factory functions produce independent instances
  each with their own isolated variables
→ Callbacks safely capture their creation context
  (user, config, DOM node — all retained)
→ Module pattern: expose API, hide internals
→ Memoization: cache persists across calls
→ React hooks: useState/useEffect "remember"
  state between renders via closure over the
  hook's internal state variable
```

---

### 🧠 Mental Model / Analogy

> Imagine a **spy who leaves on a mission** with a briefcase full of mission-specific secrets (outer function's local variables). The spy's handler (outer function) retires after briefing the spy, but the spy carries the briefcase everywhere. Any time the spy needs to reference their mission details, they open the briefcase — they don't call headquarters again. The briefcase is the closure: the spy (inner function) has everything they need, independently of whether the handler (outer function) still exists.

"Spy" = the inner function (closure)
"Handler who retires" = outer function that returned and exited
"Briefcase full of secrets" = the captured lexical environment
"Opening the briefcase" = accessing closed-over variables

The closed-over variables are not copies — it's the original classified file. If headquarters (some other code) updates those files before the spy reads them, the spy sees the update.

---

### ⚙️ How It Works (Mechanism)

**The `[[Environment]]` internal slot:**

Every function object in V8 has an internal `[[Environment]]` slot that stores a reference to the Lexical Environment (scope) in which the function was created. When the function executes, variable lookup starts in the function's own scope and then follows the `[[Environment]]` chain upward.

```
Function Object (on heap):
┌──────────────────────────────────┐
│  code: () => count++             │
│  [[Environment]] ──────────────→ Lexical Environment
│                                  {
│                                    count: 0,
│                                    outer: GlobalEnv
│                                  }
└──────────────────────────────────┘
```

**All closures in the same scope share bindings:**

```javascript
function makeMultiOps() {
  let x = 0;
  const inc = () => ++x;  // both close over
  const dec = () => --x;  // the SAME x
  const get = () => x;
  return { inc, dec, get };
}

const ops = makeMultiOps();
ops.inc(); // x = 1
ops.inc(); // x = 2
ops.dec(); // x = 1
ops.get(); // 1 — all three share one binding
```

**let in loops creates per-iteration closures:**

```javascript
const fns = [];
for (let i = 0; i < 3; i++) {
  // Each iteration creates a NEW let binding
  // Each fn closes over its own i
  fns.push(() => i);
}
fns.map(fn => fn()); // [0, 1, 2]

// vs var — all share the SAME binding:
const varFns = [];
for (var j = 0; j < 3; j++) {
  varFns.push(() => j);
}
varFns.map(fn => fn()); // [3, 3, 3]
```

---

### 🔄 How It Connects (Mini-Map)

```
Lexical Scope
(where function is WRITTEN determines
 which variables it can see)
        ↓
First-Class Functions
(functions as values — passable, returnable)
        ↓
  CLOSURE  ← you are here
  (function + captured lexical environment)
        ↓
  ┌──────────────────────────────────────────┐
  │  Enables:                                │
  │  Module Pattern  → private state         │
  │  Memoization     → cache persistence     │
  │  Currying        → partial application   │
  │  React Hooks     → state across renders  │
  │  Event Handlers  → capturing DOM context │
  │  Callbacks       → async context capture │
  └──────────────────────────────────────────┘
        ↓
  GC: closure keeps captured variables alive
  → Memory Leaks if closures not released
```

---

### 💻 Code Example

**Example 1 — Counter factory (classic closure demo):**

```javascript
function makeCounter(initial = 0) {
  let count = initial; // private, per-counter state

  return {
    increment: () => ++count,
    decrement: () => --count,
    reset:     () => (count = initial),
    value:     () => count,
  };
}

const c1 = makeCounter(10);
const c2 = makeCounter(); // independent instance

c1.increment(); // 11
c1.increment(); // 12
c2.increment(); // 1
console.log(c1.value()); // 12
console.log(c2.value()); // 1
```

**Example 2 — Module pattern (encapsulation):**

```javascript
const UserSession = (() => {
  // private — not accessible outside IIFE
  let _token = null;
  let _expires = null;

  // public API
  return {
    login(token, ttl) {
      _token = token;
      _expires = Date.now() + ttl;
    },
    getToken() {
      if (Date.now() > _expires) {
        _token = null;
        return null;
      }
      return _token;
    },
    logout() {
      _token = null;
      _expires = null;
    },
  };
})();

UserSession.login('abc123', 3600_000);
UserSession.getToken(); // 'abc123'
// _token is completely inaccessible from outside
```

**Example 3 — Memoization via closure:**

```javascript
function memoize(fn) {
  const cache = new Map(); // captured by returned fn

  return function(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key); // O(1) cache hit
    }
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

const expensiveFib = memoize(function fib(n) {
  if (n <= 1) return n;
  return expensiveFib(n - 1) + expensiveFib(n - 2);
});

expensiveFib(40); // computed once
expensiveFib(40); // cache hit — instant
```

**Example 4 — React useState mental model:**

```javascript
// React's useState is conceptually a closure
// over the component's internal state slot:

function useState(initial) {
  // state lives on a per-component "hook slot"
  // (simplified — actual impl uses a fiber cursor)
  let state = initial;

  const setState = (newValue) => {
    state = newValue;  // update captured binding
    rerender();        // trigger re-execution of component
  };

  return [state, setState];
}

// In a component:
function Counter() {
  const [count, setCount] = useState(0);
  // count and setCount are closures over the same slot
  // setCount "remembers" which slot to update
  return <button onClick={() => setCount(count + 1)}>
    {count}
  </button>;
}
```

**Example 5 — Diagnosing closure with Chrome DevTools:**

```javascript
function outer() {
  const secret = 'hidden';
  return function inner() {
    debugger; // pause here in DevTools
    // In Scope panel:
    // Closure (outer): { secret: "hidden" }
    // Local: {}
    // Global: window
    return secret;
  };
}
const fn = outer();
fn();
// Chrome DevTools Scope panel shows the captured
// environment explicitly as "Closure (outer)"
```

---

### 🔁 Flow / Lifecycle

```
1. outer() CALLED
   └── Execution context created
   └── Variables (count, etc.) allocated on heap
   └── Inner function object created
       └── [[Environment]] → points to outer's Lexical Env

2. outer() RETURNS inner function
   └── outer's execution context POPPED
   └── outer's stack frame GONE
   └── BUT: outer's heap variables NOT GC'd
       (inner fn's [[Environment]] holds reference)

3. inner fn IS CALLED (later)
   └── Execution context created for inner
   └── Variable lookup: check inner scope
       → not found → follow [[Environment]]
       → finds outer's Lexical Env → reads count

4. inner fn IS DEREFERENCED (let fn = null)
   └── No more references to inner fn
   └── [[Environment]] reference dropped
   └── outer's heap variables NOW eligible for GC
   └── GC reclaims count, etc.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A closure copies the variable's value at creation time | Closures capture the variable binding (reference), not the value. Changes to the variable after closure creation are visible to the closure |
| Every function in JS is a closure | Technically true — all functions have an [[Environment]]. In practice, "closure" means a function that captures variables from an outer scope that has returned |
| Closures cause memory leaks by default | Closures only cause leaks when the closure is reachable but no longer needed (e.g. event listener not removed). When the closure is released, GC can collect the captured variables |
| The module pattern requires class syntax | The module pattern predates ES6 classes and is built entirely on closures — no class needed |
| React's useState stores state in the component function's local variables | React stores state in a Fiber node; useState/useEffect access it via closures over the hook dispatcher and fiber cursor |
| Closures are slow and should be avoided for performance | V8 heavily optimises closures. The performance concern is heap pressure if large objects are captured unnecessarily — not closure dispatch cost |

---

### 🔥 Pitfalls in Production

**1. Event listener retaining large heap objects**

```javascript
// BAD: each click handler closes over full response
function init() {
  fetch('/config').then(response => {
    const fullPayload = response.json(); // 2MB object
    document.querySelector('#btn')
      .addEventListener('click', () => {
        // Captures entire fullPayload on heap
        // forever (while button exists in DOM)
        useOnlyOneField(fullPayload.settings.theme);
      });
  });
}

// GOOD: extract only what you need
function init() {
  fetch('/config').then(response => {
    const fullPayload = response.json();
    const theme = fullPayload.settings.theme; // extract
    // fullPayload now eligible for GC after this block
    document.querySelector('#btn')
      .addEventListener('click', () => {
        useOnlyOneField(theme); // captures 10 bytes
      });
  });
}
```

**2. Closures in loops capturing the wrong binding**

```javascript
// BAD: var — all closures share one binding
const handlers = [];
for (var i = 0; i < 5; i++) {
  handlers.push(function() {
    return i; // all return 5 — closed over same var
  });
}

// FIX option 1: let (per-iteration binding)
for (let i = 0; i < 5; i++) {
  handlers.push(() => i); // each has its own i
}

// FIX option 2: IIFE to create scope (pre-ES6)
for (var i = 0; i < 5; i++) {
  handlers.push((function(captured) {
    return () => captured; // captured is a new binding
  })(i));
}
```

**3. Accidental closure over mutable shared state**

```javascript
// BAD: multiple users of a "factory" share state
const counter = {
  count: 0,
  make: function() {
    return () => ++this.count; // closes over shared obj
  }
};

const a = counter.make();
const b = counter.make();
a(); // 1
b(); // 2 — both mutate counter.count!

// GOOD: each call creates independent state
function makeCounter() {
  let count = 0;           // per-instance
  return () => ++count;
}
const a = makeCounter();   // independent
const b = makeCounter();   // independent
a(); // 1
b(); // 1
```

**4. Closure preventing GC in long-lived caches**

```javascript
// BAD: memoize used on a per-request handler
// The cache closure accumulates forever
const memoized = memoize(expensiveQuery);

app.get('/search', async (req, res) => {
  // Cache key space: every unique query string
  // Memory grows unboundedly for N unique queries
  const result = await memoized(req.query.q);
  res.json(result);
});

// GOOD: bounded cache with TTL
function memoizeWithTTL(fn, ttlMs = 60_000) {
  const cache = new Map();
  return async function(...args) {
    const key = JSON.stringify(args);
    const cached = cache.get(key);
    if (cached && Date.now() < cached.expires) {
      return cached.value;
    }
    const value = await fn.apply(this, args);
    cache.set(key, { value, expires: Date.now() + ttlMs });
    return value;
  };
}
```

---

### 🔗 Related Keywords

- `Scope` — the lexical scope rules that make closure possible; closures capture scope chains
- `Lexical Environment` — the internal spec object that closures hold a reference to via `[[Environment]]`
- `Execution Context` — created and destroyed per function call; closures keep heap vars alive after destruction
- `Garbage Collection (JS)` — cannot collect heap variables while any closure references them
- `Module Pattern` — the primary pre-ESM pattern for encapsulation, built entirely on closures
- `Currying` — returns functions that close over partially-applied arguments
- `Memoization (JS)` — caches results in a closed-over Map/object that persists across calls
- `React Hooks` — useState and useEffect rely on closure semantics to capture component state
- `IIFE` — creates a function scope specifically to form a closure over the init-time state
- `Memory Leaks (JS)` — closures that capture large objects and are accidentally kept reachable

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Function + its captured lexical scope;    │
│              │ captured vars stay alive as long as fn    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Private state, factory functions,         │
│              │ memoization, callbacks needing context    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Capturing large objects unnecessarily;    │
│              │ avoid in hot loops if GC pressure is high │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A closure is a function with a           │
│              │  backpack full of live variables."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lexical Env → Prototype Chain → Currying  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A React component renders a list of 1000 items, each with a click handler `() => handleClick(item.id)`. Every render creates 1000 new closure objects, each capturing `item.id` from the map callback. A senior engineer claims this causes "closure GC pressure" and wants to switch to a single delegated event listener. Evaluate this claim: are these closures genuinely expensive compared to the re-render cost, what does V8's Scavenge (minor GC) do with short-lived closures, and under what specific conditions would the delegation approach actually provide a measurable benefit?

**Q2.** You have a long-running Node.js worker function that processes a stream of messages. Each message handler is created with `function createHandler(config) { return msg => process(msg, config); }` where `config` is a 50KB object. After processing 100,000 messages, heap analysis shows 50KB × 100,000 = 5GB retained. Given that each handler should have allowed GC of the previous config, trace exactly what could cause all 100,000 closure environments to remain live — name at least two distinct root-retention mechanisms — and describe how you would use Chrome DevTools heap snapshot to confirm which one applies.

