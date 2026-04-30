---
layout: default
title: "Microtask Queue"
parent: "JavaScript"
nav_order: 546
permalink: /javascript/microtask-queue/
number: "546"
category: JavaScript
difficulty: ★★☆
depends_on: Event Loop, Promise, Call Stack, Task Queue (Macrotask)
used_by: async/await, Promise chaining, queueMicrotask, MutationObserver
tags: #javascript, #browser, #nodejs, #concurrency, #internals, #intermediate
---

# 546 — Microtask Queue

`#javascript` `#browser` `#nodejs` `#concurrency` `#internals` `#intermediate`

⚡ TL;DR — The high-priority async queue for Promise callbacks and queueMicrotask, drained completely after every task before the event loop picks the next macrotask.

| #546 | Category: JavaScript | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Event Loop, Promise, Call Stack, Task Queue (Macrotask) | |
| **Used by:** | async/await, Promise chaining, queueMicrotask, MutationObserver | |

---

### 📘 Textbook Definition

The **Microtask Queue** (also called the **Job Queue** in the ECMAScript spec) is a FIFO queue that holds callbacks scheduled by `Promise.then`, `Promise.catch`, `Promise.finally`, `queueMicrotask()`, and `MutationObserver`. After the call stack empties, the event loop drains the **entire** microtask queue before moving to the next macrotask — including any new microtasks enqueued during the drain. This gives microtasks strictly higher priority than macrotasks and guarantees that Promise continuations always run before any timer or I/O callback.

---

### 🟢 Simple Definition (Easy)

The microtask queue is the VIP lane. Promise `.then()` callbacks go here. The event loop empties this lane completely before it even looks at the regular task queue (timers, I/O events).

---

### 🔵 Simple Definition (Elaborated)

When a Promise resolves, its `.then()` callback doesn't run immediately — it's placed in the microtask queue. The event loop has a strict rule: before picking any timer callback or I/O event, it must first drain every single microtask. This means even if a `setTimeout(fn, 0)` was registered before a Promise resolved, the Promise still runs first. The "drain completely" rule also means a Promise `.then()` that creates another Promise will have that new microtask run before any macrotask — microtasks can spawn more microtasks, and all of them run before the loop moves on.

---

### 🔩 First Principles Explanation

**Problem — Promises need "run soon, but not synchronously":**

When a Promise resolves, calling its callbacks synchronously would break the contract that `.then()` is always asynchronous:

```javascript
const p = Promise.resolve(42);
p.then(v => console.log('promise:', v));
console.log('after .then()');

// Required output:
// after .then()
// promise: 42

// NOT:
// promise: 42   ← if .then ran synchronously
// after .then()
```

If Promise callbacks were macrotasks (like setTimeout), they would interleave with I/O events in unpredictable ways. Promises need to run "soon" — logically part of the current task's completion — but asynchronously.

**Insight — a separate, higher-priority queue:**

```
┌──────────────────────────────────────────────┐
│  TWO-TIER QUEUE DESIGN                       │
│                                              │
│  Microtask Queue (Promise.then)              │
│  Priority: HIGH — drain fully per tick       │
│  Semantics: "part of current task's cleanup" │
│                                              │
│  Macrotask Queue (setTimeout, I/O)           │
│  Priority: NORMAL — one per tick             │
│  Semantics: "new independent task"           │
│                                              │
│  Rule: microtask queue ALWAYS drains before  │
│  any macrotask is considered                 │
└──────────────────────────────────────────────┘
```

**Why "drain completely" and not just one?**

Promise chains like `.then().then().then()` are a sequence of micro-steps in a single logical async operation. Allowing a macrotask to interrupt between `.then()` links would split a single logical operation across many event loop ticks — deeply confusing and error-prone. The "drain all" rule keeps Promise chains atomic at the task level.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT the Microtask Queue:**

```
Without a separate high-priority queue:

  Option A: Promise callbacks as macrotasks
    → promise.then fires AFTER next setTimeout
    → Promise chain with 10 .then() steps
       gets interrupted by UI events, timers
    → async/await "pauses" between unrelated
       events → incoherent execution model

  Option B: Promise callbacks run synchronously
    → breaks the always-async .then() contract
    → makes Promise harder to reason about
    → potential stack overflows in long chains
    → re-entrancy bugs: while iterating a
       collection, a sync .then fires and
       modifies the collection mid-iteration
```

**WITH the Microtask Queue:**

```
→ Promise continuations run before any new
  external event can intervene
→ async/await pauses at await and resumes
  before any unrelated timer fires
→ Long promise chains run uninterrupted as
  a coherent logical unit
→ MutationObserver delivers DOM change
  notifications before next render
```

---

### 🧠 Mental Model / Analogy

> Imagine a bank teller (the event loop) serving customers (tasks). Between each customer, the teller is required to handle all internal memos that arrived (microtasks) before allowing the next customer in. Internal memos can generate new memos, and those must also be handled before the next customer. No customer from outside gets served until the memo pile is empty — no matter how long that takes.

"Bank teller" = event loop
"Customers (external queue)" = macrotask queue (timers, I/O)
"Internal memos" = microtasks (Promise.then, queueMicrotask)
"Memo generating a new memo" = .then() callback that returns a new Promise
"Memo pile empty" = microtask queue drained, ready for next macrotask

---

### ⚙️ How It Works (Mechanism)

**Microtask sources:**

```
┌──────────────────────────────────────────────┐
│  MICROTASK SOURCES                           │
├──────────────────────────────────────────────┤
│  Promise.then()                              │
│  Promise.catch()                             │
│  Promise.finally()                           │
│  queueMicrotask(fn)    — explicit enqueue    │
│  MutationObserver      — DOM change callback │
│  async function after  — resumes after await │
│  an awaited promise    resolves              │
├──────────────────────────────────────────────┤
│  Node.js ONLY (runs before other microtasks):│
│  process.nextTick()                          │
└──────────────────────────────────────────────┘
```

**Drain algorithm:**

```
MICROTASK DRAIN (pseudocode):

while (microtaskQueue.length > 0) {
  const task = microtaskQueue.dequeue();
  task();
  // task may enqueue NEW microtasks —
  // they go to END of current queue
  // and will be processed in this loop
}
// Only exit when queue is COMPLETELY EMPTY
```

**Node.js specifics — process.nextTick priority:**

```
Node.js per-tick priority order:

  1. process.nextTick queue (drained fully)
  2. Promise microtask queue (drained fully)
  3. ONE macrotask (timers, I/O, setImmediate)
  4. Repeat
```

---

### 🔄 How It Connects (Mini-Map)

```
Promise.resolve() / async fn completes
        ↓
  MICROTASK QUEUE  ← you are here
  (Promise.then, queueMicrotask,
   process.nextTick in Node.js)
        ↓
  DRAIN (complete) — new microtasks
  added during drain run in same pass
        ↓
  Event Loop checks:
  queue empty? → pick next macrotask
  queue non-empty? → drain more
        ↓
  Task Queue (Macrotask)
  (setTimeout, I/O, events)
```

---

### 💻 Code Example

**Example 1 — Microtasks run before macrotasks:**

```javascript
console.log('1 sync');

setTimeout(() => console.log('5 macro'), 0);

Promise.resolve()
  .then(() => {
    console.log('3 micro 1');
    return Promise.resolve();
  })
  .then(() => console.log('4 micro 2'));

queueMicrotask(() => console.log('3b queueMicrotask'));

console.log('2 sync end');

// Output:
// 1 sync
// 2 sync end
// 3 micro 1       ← microtask queue drains
// 3b queueMicrotask
// 4 micro 2       ← chained .then also microtask
// 5 macro         ← macrotask only after micro drain
```

**Example 2 — Starving the event loop with microtasks:**

```javascript
// BAD: infinite microtask chain — macrotasks starve
function infinite() {
  Promise.resolve().then(infinite);
}
infinite();

setTimeout(() => {
  // NEVER runs — microtask queue never empties
  console.log('I am blocked forever');
}, 0);

// Use this to intentionally yield to macrotask queue:
function yieldToMacrotask() {
  return new Promise(resolve => setTimeout(resolve, 0));
}
async function processChunks(items) {
  for (let i = 0; i < items.length; i++) {
    process(items[i]);
    if (i % 1000 === 0) await yieldToMacrotask();
  }
}
```

**Example 3 — Node.js process.nextTick vs Promise:**

```javascript
// process.nextTick runs BEFORE Promise microtasks
Promise.resolve().then(() => console.log('B: Promise'));
process.nextTick(() => console.log('A: nextTick'));
console.log('0: sync');

// Output:
// 0: sync
// A: nextTick   ← nextTick queue first
// B: Promise    ← then Promise microtasks
```

**Example 4 — async/await is microtask sugar:**

```javascript
async function getData() {
  const result = await fetch('/api');  // suspends here
  console.log('resumes as microtask');
  return result.json();
}

// Equivalent to:
fetch('/api')
  .then(result => {
    console.log('resumes as microtask');
    return result.json();
  });
// Both resume via the microtask queue when
// the awaited Promise resolves
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| queueMicrotask and setTimeout(fn, 0) do the same thing | queueMicrotask schedules a microtask (runs before any macrotask); setTimeout schedules a macrotask (runs after all pending microtasks) |
| async/await is faster because it skips the queue | async/await uses the microtask queue like any other Promise — its priority advantage is over macrotasks only |
| process.nextTick is the same as Promise.then in Node.js | process.nextTick runs before Promise microtasks and before I/O events — it has even higher priority |
| A microtask added during a microtask runs next tick | It runs in the CURRENT microtask drain — same tick, before any macrotask |
| MutationObserver callbacks run synchronously | They are delivered as microtasks, after the current synchronous code completes |

---

### 🔥 Pitfalls in Production

**1. Infinite microtask loop starving the entire server**

```javascript
// BAD: this kills your Node.js server completely
// HTTP server stops responding — no health checks,
// no timers, no I/O callbacks — all starved
async function loop() {
  await Promise.resolve();
  loop(); // tail call NOT optimised — new microtask
}
loop();

// GAP: this is hard to detect — no CPU spike,
// just silent starvation
// Diagnose with: node --inspect → event loop tab
// or: clinic.js bubbleprof
```

**2. process.nextTick recursion starves promises in Node.js**

```javascript
// BAD: nextTick recursive — Promise .then callbacks
// in the same tick NEVER run
function recursiveNextTick() {
  process.nextTick(recursiveNextTick);
}
recursiveNextTick();

// Symptoms: database callbacks (Promises) time out
// despite immediate completion

// GOOD: use setImmediate for recursive yielding
function safeRecursion() {
  setImmediate(safeRecursion);
}
```

**3. Assuming microtask order across unrelated Promises**

```javascript
// BAD assumption: P1.then always runs before P2.then
const p1 = fetchA();  // resolves at t=10ms
const p2 = fetchB();  // resolves at t=5ms

p1.then(a => console.log('P1:', a));
p2.then(b => console.log('P2:', b));

// Actual output:
// P2: ... (resolved earlier, queued earlier)
// P1: ...

// Never assume ordering between Promises that
// depend on external async operations
// Use Promise.all for coordinated results
```

---

### 🔗 Related Keywords

- `Event Loop` — runs the microtask drain algorithm after every task completes
- `Promise` — the primary source of microtasks via `.then()`, `.catch()`, `.finally()`
- `async/await` — syntactic sugar; each `await` resumes as a microtask when the awaited value resolves
- `Task Queue (Macrotask)` — the lower-priority queue; never processed while microtask queue has items
- `queueMicrotask` — the explicit API for directly enqueuing a microtask without a Promise
- `process.nextTick` — Node.js-specific; queues a callback before Promise microtasks
- `MutationObserver` — uses the microtask queue to deliver DOM mutation notifications

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ High-priority queue drained completely    │
│              │ before any macrotask — Promise home       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Scheduling work that must run before      │
│              │ any timer or I/O fires this tick          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Recursive self-scheduling — will starve   │
│              │ all macrotasks (timers, I/O, HTTP)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Microtasks clear the decks before the    │
│              │  next task is even considered."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Promise → async/await → Event Loop        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Promise chain with 10,000 `.then()` links is triggered from a UI click handler. Since all 10,000 microtasks drain before the next macrotask, the browser cannot render or process user input for the entire duration. The chain takes 300ms. Describe two refactoring strategies — one using `queueMicrotask` and one using `MessageChannel` — that allow incremental progress while yielding to rendering between chunks.

**Q2.** In Node.js, explain what happens when a `process.nextTick` callback throws an uncaught exception versus when a Promise rejection is unhandled. Specifically: which is delivered as an `uncaughtException` event and which as `unhandledRejection`, and why does the timing difference (nextTick vs microtask queue) affect which error handler fires — with implications for graceful shutdown logic?

