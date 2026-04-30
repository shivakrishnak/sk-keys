---
layout: default
title: "Task Queue (Macrotask)"
parent: "JavaScript"
nav_order: 545
permalink: /javascript/task-queue-macrotask/
number: "545"
category: JavaScript
difficulty: ★★☆
depends_on: Event Loop, Web APIs, Call Stack
used_by: setTimeout, setInterval, I/O callbacks, MessageChannel, Web Workers
tags: #javascript, #browser, #nodejs, #concurrency, #internals, #intermediate
---

# 545 — Task Queue (Macrotask)

`#javascript` `#browser` `#nodejs` `#concurrency` `#internals` `#intermediate`

⚡ TL;DR — The queue holding async callbacks (setTimeout, I/O, events) that the event loop processes one per tick, always after draining the microtask queue.

| #545 | Category: JavaScript | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Event Loop, Web APIs, Call Stack | |
| **Used by:** | setTimeout, setInterval, I/O callbacks, MessageChannel, Web Workers | |

---

### 📘 Textbook Definition

The **Task Queue** (also called the **Macrotask Queue** or simply the **Message Queue**) is a FIFO queue maintained by the JavaScript runtime that holds callback functions queued by host environment APIs — `setTimeout`, `setInterval`, I/O operations, UI events, and `MessageChannel`. During each event loop iteration, the loop picks exactly **one** task from the front of the task queue, pushes it onto the call stack, and executes it to completion. Before picking the next macrotask, the event loop always drains the entire microtask queue first.

---

### 🟢 Simple Definition (Easy)

The task queue is JavaScript's waiting room for async callbacks. When a timer fires or a network response arrives, its callback waits in this queue. The event loop serves one callback at a time from this queue.

---

### 🔵 Simple Definition (Elaborated)

When you call `setTimeout(fn, 1000)`, the browser's timer mechanism waits 1 second, then puts `fn` in the task queue. The event loop continuously checks: "Is the call stack empty? Is there a task waiting?" If yes to both, it takes the first task and runs it. Only one task runs per event loop tick — even if ten timers fire simultaneously, their callbacks queue up and execute one at a time. This "one at a time" model is what keeps JavaScript free from race conditions on shared data.

---

### 🔩 First Principles Explanation

**Problem — multiple async operations completing at different times:**

```
setTimeout(fn1, 100);
setTimeout(fn2, 100);
fetch('/api').then(fn3);

// All three complete "around the same time."
// How does a single-threaded runtime decide order?
// What if they all arrive at exactly the same millisecond?
```

**Constraint — one thread, one execution context:**

JavaScript can only run one function at a time. There is no "concurrent execution" of callbacks. The runtime needs a structure that serialises multiple incoming async results.

**Insight — FIFO queue + one-at-a-time processing:**

```
┌───────────────────────────────────────────────┐
│  TASK QUEUE — FIFO ORDER                      │
│                                               │
│  Callback from setInterval  ← enqueued first │
│  Callback from fetch I/O    ← enqueued second │
│  Callback from click event  ← enqueued third  │
│                                               │
│  Event Loop takes ONE → runs it → check again │
│  → no concurrent access to shared state       │
└───────────────────────────────────────────────┘
```

**The "one task per tick" contract:**

Each macrotask runs to completion. While it runs, no other macrotask or microtask can interrupt. This is what makes JavaScript code safe from data races without locks — but it's also why a long-running task blocks everything else.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT the Task Queue:**

```
Without serialised task queuing:

  Problem 1: Concurrent callback execution
    Two timers fire simultaneously →
    both callbacks try to modify DOM at once →
    race condition, corrupted state

  Problem 2: No ordering guarantees
    fetch + setTimeout both complete at t=100ms
    Which runs first? Undefined without a queue

  Problem 3: Call stack interruption
    Callback arrives while current function runs →
    must interrupt mid-execution →
    reentrancy bugs, stack corruption
```

**WITH the Task Queue:**

```
→ Callbacks serialised — never concurrent
→ Ordering: FIFO within same priority level
→ Non-interruptible execution per task
→ No locks needed — data races structurally
  impossible within a single JS thread
```

---

### 🧠 Mental Model / Analogy

> Think of the task queue as a **numbered ticket system at a government office** (like the DMV). Async operations take a ticket when they complete. The event loop calls the next ticket number only when the current customer (task) has been fully served. No matter how many people (callbacks) are waiting, only one goes to the counter at a time — and they never interrupt each other mid-service.

"Taking a ticket" = callback placed in task queue when async work completes
"Calling the next number" = event loop picks the next macrotask
"Being served fully" = task runs to completion on the call stack
"People waiting" = queued macrotask callbacks

---

### ⚙️ How It Works (Mechanism)

**Task queue sources (browser):**

```
┌──────────────────────────────────────────────┐
│  MACROTASK SOURCES                           │
├──────────────────────────────────────────────┤
│  setTimeout(fn, delay)                       │
│  setInterval(fn, interval)                   │
│  I/O event callbacks (click, input, etc.)    │
│  MessageChannel.postMessage()                │
│  Web Worker postMessage()                    │
│  XHR/fetch (completion callback)             │
│  requestIdleCallback                         │
└──────────────────────────────────────────────┘
```

**Event loop tick — full sequence:**

```
┌──────────────────────────────────────────────┐
│  ONE EVENT LOOP TICK                         │
│                                              │
│  1. Run synchronous code                     │
│     (call stack drains)                      │
│              ↓                               │
│  2. Drain ALL microtasks                     │
│     (Promise.then, queueMicrotask)           │
│     Repeat until microtask queue empty       │
│              ↓                               │
│  3. [Browser] Run rAF callbacks if paint due │
│              ↓                               │
│  4. [Browser] Render / paint                 │
│              ↓                               │
│  5. Pick ONE macrotask from task queue       │
│     → push callback to call stack            │
│     → execute to completion                  │
│              ↓                               │
│  6. Go back to step 1                        │
└──────────────────────────────────────────────┘
```

**Timer accuracy — setTimeout(fn, 0) is a lie:**

```javascript
const start = Date.now();
setTimeout(() => {
  console.log(Date.now() - start, 'ms');
}, 0);
// Typical output: 1–4ms (not 0ms)
// Minimum clamping: browsers clamp nested timers
// to ≥ 4ms after 5 levels of nesting (HTML spec)
// Node.js: ≥ 1ms
```

---

### 🔄 How It Connects (Mini-Map)

```
Web APIs / libuv
(timers, I/O, events complete)
        ↓
  TASK QUEUE  ← you are here
  (macrotasks waiting)
        ↑
  setTimeout, setInterval,
  I/O callbacks, UI events
        ↓
  Event Loop
  (picks ONE task per tick,
   AFTER microtask queue drains)
        ↓
  Call Stack
  (executes the macrotask)
        ↓
  Microtask Queue
  (drains completely before
   next macrotask is picked)
```

---

### 💻 Code Example

**Example 1 — One macrotask per tick:**

```javascript
setTimeout(() => console.log('macro 1'), 0);
setTimeout(() => console.log('macro 2'), 0);

Promise.resolve().then(() => console.log('micro 1'));
Promise.resolve().then(() => console.log('micro 2'));

console.log('sync');

// Output:
// sync         ← synchronous first
// micro 1      ← microtasks drain completely
// micro 2
// macro 1      ← ONE macrotask
// macro 2      ← then the NEXT macrotask (next tick)
```

**Example 2 — Long macrotask blocks rendering:**

```javascript
// BAD: 200ms sync work inside a macrotask
// blocks render, input events, other timers
setTimeout(() => {
  const start = Date.now();
  while (Date.now() - start < 200) {}
  // UI is frozen for 200ms
}, 0);

// GOOD: split into smaller macrotasks
function doWorkInChunks(items, i = 0) {
  const end = Math.min(i + 100, items.length);
  for (; i < end; i++) process(items[i]);
  if (i < items.length)
    setTimeout(() => doWorkInChunks(items, i), 0);
  // yields to render + other tasks between chunks
}
```

**Example 3 — MessageChannel for faster macrotask:**

```javascript
// MessageChannel posts a macrotask faster than
// setTimeout — no 1-4ms minimum clamp
const { port1, port2 } = new MessageChannel();
port1.onmessage = () => {
  console.log('MessageChannel macrotask');
};
port2.postMessage(null); // queues macrotask immediately

// Used internally by React's scheduler for
// high-frequency task scheduling
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All async operations use the task queue | Promises use the microtask queue, which has higher priority and drains completely before the next macrotask |
| setTimeout(fn, 0) means "run immediately" | It means "run as soon as the call stack is empty and microtasks are drained" — minimum ~1–4ms delay |
| Multiple timers firing at the same time execute simultaneously | They all queue into the task queue and execute sequentially, one per event loop tick |
| The task queue is first-in-first-out globally | Within a single source type it's FIFO, but browsers have multiple task queues with different priorities (e.g., user input can jump ahead) |
| setTimeout with the same delay always runs in registration order | The HTML spec does not guarantee order when delays collide — implementations vary |

---

### 🔥 Pitfalls in Production

**1. Single long macrotask freezing UI or blocking I/O**

```javascript
// BAD: one giant task holds the thread
app.on('message', (data) => {
  // 500ms of JSON parsing + transformation
  const result = JSON.parse(data).items
    .map(expensiveTransform);
  respond(result);
  // Nothing else (health checks, other messages)
  // can run for 500ms
});

// GOOD: stream or use Worker Threads
const { Worker } = require('worker_threads');
app.on('message', (data) => {
  const w = new Worker('./transform-worker.js',
    { workerData: data });
  w.on('message', respond);
});
```

**2. setInterval drift under load**

```javascript
// BAD: setInterval doesn't account for execution time
setInterval(() => {
  expensiveOperation(); // takes 80ms
}, 100);
// Intended: fire every 100ms
// Actual: fire every ~180ms under load
// (80ms exec + 100ms wait, but next interval
// fired BEFORE exec finished → queued behind)

// GOOD: use recursive setTimeout for precise spacing
function scheduleNext() {
  setTimeout(() => {
    expensiveOperation();
    scheduleNext(); // schedule AFTER completion
  }, 100);
}
scheduleNext();
```

**3. Starvation of macrotasks by microtask flood**

```javascript
// BAD: recursive Promise chain prevents macrotasks
// from ever running (timers, I/O, health endpoints)
function infiniteChain() {
  Promise.resolve().then(infiniteChain);
}
infiniteChain();
// The macrotask queue (and thus your HTTP server)
// is completely starved

// GOOD: use setImmediate / setTimeout to yield
function yieldingLoop(i = 0) {
  setImmediate(() => {    // macrotask — yields loop
    doWork(i);
    yieldingLoop(i + 1);
  });
}
```

---

### 🔗 Related Keywords

- `Event Loop` — the orchestrator that picks tasks from this queue and pushes them to the call stack
- `Microtask Queue` — the higher-priority queue that fully drains before any macrotask is picked
- `Web APIs` — the source of most macrotasks; timers and I/O are managed here
- `setTimeout` — the primary API for scheduling a macrotask after a minimum delay
- `setInterval` — schedules recurring macrotasks at a specified interval
- `MessageChannel` — a lower-latency way to post macrotasks without setTimeout's minimum clamp
- `Call Stack` — where each macrotask actually executes when the event loop picks it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ FIFO queue of async callbacks; event loop │
│              │ takes ONE per tick after microtasks drain  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Scheduling deferred work, yielding to     │
│              │ the render, spacing out heavy operations  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Work needing < 1ms precision or needing   │
│              │ to run before the next render frame       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Microtasks clear the table;              │
│              │  macrotasks take one seat at a time."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Microtask Queue → Promise → Event Loop    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** React's concurrent renderer uses `MessageChannel` instead of `setTimeout(fn, 0)` for scheduling work units. Given that both are macrotasks, why does React prefer `MessageChannel`? What specific browser behaviour makes `setTimeout(fn, 0)` unsuitable for scheduling 60fps work that needs to run before the next paint — and why doesn't `queueMicrotask` solve the problem either?

**Q2.** You instrument a Node.js event loop with `perf_hooks.monitorEventLoopDelay()` and observe p99 delay of 350ms despite no individual request handler taking more than 10ms. How is this possible? Trace the specific event loop mechanics that could produce this lag without any single long-running task, and name one diagnostic tool that would confirm your hypothesis.

