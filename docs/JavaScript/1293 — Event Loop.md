---
layout: default
title: "Event Loop"
parent: "JavaScript"
nav_order: 1293
permalink: /javascript/event-loop/
number: "1293"
category: JavaScript
difficulty: ★★☆
depends_on: JavaScript Engine (V8), Call Stack, Web APIs, Task Queue, Microtask Queue
used_by: Promise, async/await, setTimeout, Web Workers, Node.js I/O
tags: #javascript, #browser, #nodejs, #concurrency, #internals, #intermediate
---

# 1293 — Event Loop

`#javascript` `#browser` `#nodejs` `#concurrency` `#internals` `#intermediate`

⚡ TL;DR — The mechanism enabling single-threaded JavaScript to handle async I/O non-blocking by cycling between the call stack, microtask queue, and task queue.

| #1293 | category: JavaScript
|:---|:---|:---|
| **Depends on:** | JavaScript Engine (V8), Call Stack, Web APIs, Task Queue, Microtask Queue | |
| **Used by:** | Promise, async/await, setTimeout, Web Workers, Node.js I/O | |

---

### 📘 Textbook Definition

The **Event Loop** is the concurrency model at the heart of JavaScript runtimes (browsers and Node.js) that enables a single-threaded engine to perform non-blocking asynchronous operations. It continuously monitors the call stack and the task queues — on each iteration ("tick"), it drains the entire microtask queue, then picks one task from the macrotask queue and pushes its callback onto the call stack for execution. This model relies on the host environment (Web APIs in browsers, libuv in Node.js) to execute I/O and timer operations off the main thread, notifying the event loop when results are ready.

---

### 🟢 Simple Definition (Easy)

JavaScript can only do one thing at a time. The Event Loop is the traffic cop that decides what runs next — it keeps checking: "Is the current task done? OK, run the next one."

---

### 🔵 Simple Definition (Elaborated)

JavaScript runs on a single thread — there is exactly one call stack and one execution context active at any moment. The Event Loop solves the problem of waiting for slow operations (network requests, file reads, timers) without freezing everything else. When you call `setTimeout` or `fetch`, the browser's Web APIs handle the actual wait. Once the result is ready, the callback is placed in a queue. The Event Loop's job is to pick callbacks from those queues and push them onto the call stack when the stack is empty. Critically, there are two kinds of queues — **microtasks** (Promises) which drain completely before the loop moves on, and **macrotasks** (timers, I/O) which execute one at a time.

---

### 🔩 First Principles Explanation

**Problem — blocking I/O on a single thread:**

Early JavaScript was designed for the browser where UI responsiveness is everything. A naive design would look like:

```javascript
// BAD: synchronous blocking (hypothetical)
const data = readFileSync('/large-file'); // freezes browser
renderUI();                               // never reached
```

If the JS engine blocked waiting for I/O, the entire browser tab freezes — no scrolling, no clicks, no rendering. The user sees a white screen. On a server (Node.js), one slow request blocks every other client.

**Constraint — one thread, but many events:**

Browsers have always had exactly one JS thread per tab. Adding more threads would mean sharing DOM state across threads — a well-known source of race conditions that would make correct browser programming significantly harder.

**Insight — offload the waiting, keep the execution:**

```
┌─────────────────────────────────────────────────┐
│  KEY INSIGHT                                    │
│                                                 │
│  The JS engine doesn't need to WAIT for I/O.   │
│  It just needs to be NOTIFIED when it's done.  │
│                                                 │
│  Waiting  → handled by host env (C++/libuv)    │
│  Notified → callback placed in queue            │
│  Executed → event loop picks it up              │
└─────────────────────────────────────────────────┘
```

**Solution — the event loop + task queues:**

1. Async work (timers, I/O, network) is handed off to the host environment
2. The JS thread continues executing synchronous code uninterrupted
3. When async work completes, a callback is enqueued
4. When the call stack empties, the event loop picks the next callback

This gives you the *appearance* of concurrency with the *safety* of single-threaded execution. No mutexes, no race conditions on shared state, no deadlocks — because only one piece of JavaScript ever runs at once.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT the Event Loop:**

```
Without a non-blocking async model:

  Problem 1: Sequential blocking destroys UX
    fetch('/api/data') // hangs for 300ms
    → browser unresponsive, scroll frozen,
      animations stop, user thinks it crashed

  Problem 2: One slow operation blocks all others
    // Node.js without event loop:
    handleRequest(req1) // DB query takes 50ms
    → req2, req3, req4 all wait in line
    → 100 concurrent users = 5 second wait

  Problem 3: Multi-threaded DOM is unsafe
    Thread A: elem.style.color = 'red'
    Thread B: elem.remove()
    → race condition, undefined behaviour
    → requires locks = complex, error-prone

  Problem 4: No natural async primitive
    Callbacks, Promises, async/await all
    depend on the event loop contract
    → none of these patterns are possible
```

**What breaks without it:**

1. Browser UX — every network call freezes the tab
2. Server throughput — Node.js serves one request at a time
3. Animation — `requestAnimationFrame` has no execution model
4. Promises — `.then()` callbacks have nowhere to queue

**WITH the Event Loop:**

```
→ UI stays responsive during all async work
→ Node.js handles 10,000 concurrent connections
  on a single thread (non-blocking I/O)
→ Promise chains execute predictably and
  in a well-defined order
→ Single-threaded model keeps DOM safe
  without locks
```

---

### 🧠 Mental Model / Analogy

> Imagine a **restaurant with one waiter** (the JS thread). The waiter takes your order (executes your code) and passes it to the kitchen (Web APIs / libuv). While the kitchen prepares your food, the waiter doesn't stand at the kitchen window waiting — they go serve other tables (execute other synchronous code). When the kitchen rings a bell (async callback ready), the completed order goes to a pickup counter (the task queue). Between serving tables, the waiter checks the pickup counter and delivers the next completed order.
>
> VIP orders (Promises — microtasks) go to a priority counter that the waiter always clears completely before checking the regular pickup counter (macrotask queue).

"The waiter" = the JS call stack and engine
"The kitchen" = Web APIs / libuv (C++ layer doing actual I/O)
"The bell" = callback enqueued when async work completes
"VIP counter" = microtask queue (Promises)
"Regular counter" = macrotask queue (setTimeout, I/O)
"Checking counters between tables" = one event loop tick

---

### ⚙️ How It Works (Mechanism)

**The three players:**

```
┌─────────────────────────────────────────────────┐
│           JAVASCRIPT RUNTIME                    │
│  ┌──────────────┐    ┌────────────────────────┐ │
│  │  CALL STACK  │    │  HOST ENVIRONMENT      │ │
│  │              │    │  (Web APIs / libuv)    │ │
│  │ main()       │    │  setTimeout            │ │
│  │ fn()         │    │  fetch / XHR           │ │
│  │              │    │  fs.readFile           │ │
│  └──────┬───────┘    └──────────┬─────────────┘ │
│         │                       │               │
│         ↓                       ↓               │
│  ┌──────────────────────────────────────────┐   │
│  │  MICROTASK QUEUE  (Promises, nextTick*)  │   │
│  ├──────────────────────────────────────────┤   │
│  │  MACROTASK QUEUE  (setTimeout, I/O)      │   │
│  └──────────────────────────────────────────┘   │
│                    ↑                            │
│              EVENT LOOP                         │
└─────────────────────────────────────────────────┘
* nextTick is Node.js-specific
```

**The tick algorithm — exact execution order:**

```
EACH EVENT LOOP TICK:

  1. Execute all synchronous code on call stack
     until stack is empty

  2. Drain ENTIRE microtask queue:
     a. Run all Promise .then / .catch / .finally
     b. Run all queueMicrotask() callbacks
     c. If new microtasks are added during step 2,
        run those too — never leave microtask queue
        with pending items

  3. [Browser only] Run requestAnimationFrame
     callbacks if a repaint is scheduled

  4. [Browser only] Perform rendering / paint

  5. Pick ONE callback from the macrotask queue
     (setTimeout, setInterval, I/O, MessageChannel)
     and push it onto the call stack

  6. Go back to step 1
```

**Concrete execution trace:**

```javascript
console.log('A');                          // sync

setTimeout(() => console.log('B'), 0);    // macrotask

Promise.resolve()
  .then(() => console.log('C'));          // microtask

console.log('D');                          // sync

// Output: A  D  C  B
//         ^  ^  ^  ^
//     sync sync micro macro
```

**Node.js event loop phases (libuv):**

```
┌─────────────────────────────────────────────┐
│  NODE.JS EVENT LOOP PHASES (one iteration)  │
├─────────────────────────────────────────────┤
│  1. timers        setTimeout / setInterval  │
│  2. pending I/O   deferred I/O callbacks    │
│  3. idle/prepare  internal libuv use        │
│  4. poll          wait for new I/O events   │
│  5. check         setImmediate callbacks    │
│  6. close         socket close callbacks    │
├─────────────────────────────────────────────┤
│  process.nextTick() runs BEFORE microtasks  │
│  (between every phase transition)           │
└─────────────────────────────────────────────┘
```

**setImmediate vs setTimeout(fn, 0) in Node.js:**

When called from the main module (outside I/O), the order of `setImmediate` vs `setTimeout(fn, 0)` is non-deterministic because it depends on process performance. When called from within an I/O callback, `setImmediate` always fires before `setTimeout(fn, 0)` because the check phase comes before the timers phase in the next iteration.

---

### 🔄 How It Connects (Mini-Map)

```
JavaScript Source Code
        ↓
  V8 Engine (parses + compiles)
        ↓
  Call Stack  ←──────────────────────┐
        │                            │
        │ async call (fetch, timer)  │
        ↓                            │
  Web APIs / libuv ──────────────────┤
  (C++ layer, off-thread work)       │
        │                            │
        ↓                            │
  ┌─────────────┐                    │
  │  Microtask  │ ← Promise.then     │
  │   Queue     │ ← queueMicrotask   │
  └──────┬──────┘                    │
         │ drained first             │
  ┌──────▼──────┐                    │
  │  Macrotask  │ ← setTimeout       │
  │   Queue     │ ← I/O callbacks    │
  └──────┬──────┘                    │
         │                           │
  EVENT LOOP ────────────────────────┘
  (checks queues, pushes to stack)
        ↓
  async/await, Promise, Callback
  (user-facing async abstractions)
        ↓
  Web Workers (parallel threads,
  communicate via postMessage →
  macrotask queue)
```

---

### 💻 Code Example

**Example 1 — Microtask vs macrotask execution order:**

```javascript
// Understanding queue priority
console.log('1 - sync start');

setTimeout(() => {
  console.log('4 - macrotask (setTimeout)');
}, 0);

Promise.resolve()
  .then(() => console.log('3 - microtask 1'))
  .then(() => console.log('3b - microtask 2'));

queueMicrotask(() => console.log('3c - microtask 3'));

console.log('2 - sync end');

// Output order:
// 1 - sync start
// 2 - sync end
// 3 - microtask 1     ← microtask queue drains
// 3b - microtask 2    ← chained .then also microtask
// 3c - microtask 3    ← queueMicrotask also microtask
// 4 - macrotask (setTimeout)  ← only after micro-drain
```

**Example 2 — Starving the event loop with microtasks:**

```javascript
// BAD: infinite microtask loop starves macrotasks
function infiniteMicrotasks() {
  Promise.resolve().then(infiniteMicrotasks);
}
infiniteMicrotasks();
setTimeout(() => {
  // This NEVER runs — microtask queue never empties
  console.log('I am starved');
}, 0);

// GOOD: use setImmediate (Node.js) or setTimeout
// to yield control back to the event loop
function yieldingWork() {
  setImmediate(yieldingWork); // macrotask — yields
}
```

**Example 3 — Measuring event loop lag in production:**

```javascript
// BAD: long synchronous operation blocks event loop
app.get('/data', (req, res) => {
  const result = heavyCpuWork(); // 500ms sync
  res.json(result);
  // All other requests blocked for 500ms
});

// GOOD: offload CPU work to worker thread
const { Worker } = require('worker_threads');

app.get('/data', (req, res) => {
  const worker = new Worker('./heavy-work.js');
  worker.on('message', result => res.json(result));
  // Event loop free to handle other requests
});
```

**Example 4 — Node.js: process.nextTick vs Promise:**

```javascript
// Node.js-specific queue priority
setImmediate(() => console.log('5 - setImmediate'));
setTimeout(() => console.log('4 - setTimeout'), 0);

Promise.resolve()
  .then(() => console.log('2 - Promise.then'));

process.nextTick(() => console.log('1 - nextTick'));

console.log('0 - sync');

// Output:
// 0 - sync
// 1 - nextTick     ← runs before Promise microtasks
// 2 - Promise.then
// 4 - setTimeout   (order vs setImmediate non-deterministic
// 5 - setImmediate  from main module)
```

---

### 🔁 Flow / Lifecycle

```
APPLICATION START
       ↓
  Execute top-level synchronous code
  (module evaluation, event listeners setup)
       ↓
┌──────────────────────────────────────────┐
│         EVENT LOOP ITERATION             │
│                                          │
│  ┌── 1. SYNCHRONOUS PHASE ──────────┐   │
│  │  Execute current call stack      │   │
│  │  until empty                     │   │
│  └──────────────────────────────────┘   │
│                  ↓                       │
│  ┌── 2. MICROTASK DRAIN ────────────┐   │
│  │  Run ALL pending microtasks      │   │
│  │  (Promise.then, queueMicrotask)  │   │
│  │  Loop until queue empty          │   │
│  └──────────────────────────────────┘   │
│                  ↓                       │
│  ┌── 3. RENDER (browser only) ──────┐   │
│  │  requestAnimationFrame callbacks │   │
│  │  Layout + Paint if needed        │   │
│  └──────────────────────────────────┘   │
│                  ↓                       │
│  ┌── 4. MACROTASK ──────────────────┐   │
│  │  Pick ONE task from queue        │   │
│  │  (setTimeout, I/O callback, etc) │   │
│  │  Push callback onto call stack   │   │
│  └──────────────────────────────────┘   │
│                  ↓                       │
│         ← loop back to step 1           │
└──────────────────────────────────────────┘
       ↓
  No more tasks → process idle
  (browser waits for user events;
   Node.js process exits)
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `setTimeout(fn, 0)` executes immediately after the current line | It queues a macrotask — at minimum, all synchronous code AND all pending microtasks run first |
| async/await makes JavaScript multi-threaded | `async/await` is syntactic sugar over Promises — still single-threaded, still uses the event loop |
| Promises are faster than setTimeout because they're async | Promises are faster to schedule because microtasks are drained before macrotasks, not because they bypass the event loop |
| The event loop runs between every line of synchronous code | The event loop only runs when the call stack is completely empty — a 10,000-iteration sync loop blocks it entirely |
| `setImmediate` and `setTimeout(fn, 0)` are equivalent | In Node.js they use different queue phases; `setImmediate` is always preferred inside I/O callbacks for deterministic ordering |
| Long Promise chains are non-blocking | `.then()` callbacks are microtasks, but CPU-heavy code inside them still blocks the thread — async scheduling ≠ non-blocking execution |

---

### 🔥 Pitfalls in Production

**1. Long synchronous tasks blocking the event loop**

```javascript
// BAD: blocks event loop for entire duration
app.post('/process', (req, res) => {
  // synchronous JSON processing of 50MB payload
  const result = JSON.parse(req.body.largePayload);
  const processed = heavyTransform(result); // 800ms
  res.json(processed);
  // ALL other requests stall for 800ms
});

// GOOD: stream or offload to worker thread
const { Worker, isMainThread } =
  require('worker_threads');

app.post('/process', (req, res) => {
  const worker = new Worker('./transform.js', {
    workerData: req.body.largePayload
  });
  worker.on('message', result => res.json(result));
  worker.on('error', err => res.status(500).json(err));
  // event loop free — handles other requests
});
```

**Diagnostic:** use `clinic.js` or `--prof` flag. Event loop lag > 100ms indicates blocking code. `perf_hooks.monitorEventLoopDelay()` measures lag directly.

**2. Microtask queue starvation via recursive Promises**

```javascript
// BAD: recursive Promise prevents macrotasks
// (timers, I/O callbacks) from ever running
function recursivePromise() {
  return Promise.resolve().then(recursivePromise);
}
recursivePromise();
// setTimeouts, I/O, HTTP responses — all starved

// GOOD: use setImmediate to yield between chunks
function processChunk(items, index = 0) {
  if (index >= items.length) return;
  processOne(items[index]);
  setImmediate(() => processChunk(items, index + 1));
}
```

**3. process.nextTick recursion in Node.js**

```javascript
// BAD: process.nextTick stacks ahead of Promises
// and can starve the I/O poll phase
function badRecursion() {
  process.nextTick(badRecursion); // never yields
}

// GOOD: prefer setImmediate for recursive async
function goodRecursion(done) {
  setImmediate(() => {
    if (moreWorkToDo()) goodRecursion(done);
    else done();
  });
}
```

`process.nextTick` callbacks run before Promise microtasks AND before any I/O. Recursive use starves disk reads and network sockets.

**4. Assuming `await` yields to the event loop**

```javascript
// BAD: async function with sync-heavy body
async function processAll(items) {
  for (const item of items) {
    await Promise.resolve(); // yields, but...
    heavyCpuWork(item);       // still blocks thread
  }
}
// The await yields to the microtask queue, but the
// CPU work ON EACH ITERATION still holds the thread.
// 10,000 items × 1ms = 10s of blocking.

// GOOD: batch and yield at macrotask boundary
async function processAll(items) {
  const BATCH = 100;
  for (let i = 0; i < items.length; i += BATCH) {
    const batch = items.slice(i, i + BATCH);
    batch.forEach(heavyCpuWork);
    // yield to macrotask queue — allows I/O callbacks
    await new Promise(r => setTimeout(r, 0));
  }
}
```

---

### 🔗 Related Keywords

- `JavaScript Engine (V8)` — executes JS code on the call stack that the event loop feeds into
- `Call Stack` — the single execution stack the event loop monitors and pushes callbacks onto
- `Task Queue (Macrotask)` — holds setTimeout/I/O callbacks; event loop picks one per tick
- `Microtask Queue` — holds Promise callbacks; drained completely before each macrotask
- `Web APIs` — the browser's C++ layer that handles async operations off the main thread
- `Promise` — schedules `.then()` callbacks as microtasks, fundamental to event loop priority
- `async/await` — syntactic sugar over Promises that makes event loop scheduling readable
- `setTimeout` — the classic macrotask scheduler; timer managed by Web APIs / libuv
- `setImmediate` — Node.js macrotask scheduled in the check phase, after I/O polling
- `process.nextTick` — Node.js microtask variant that runs before Promise callbacks
- `Web Workers` — true parallel JS threads; communicate with main thread via macrotask postMessage
- `requestAnimationFrame` — browser callback scheduled between microtasks and rendering paint

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Single-threaded JS stays non-blocking     │
│              │ by delegating async work to host APIs     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Reasoning about async execution order,    │
│              │ diagnosing latency, tuning Promise chains  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-heavy work — use Worker Threads;      │
│              │ event loop is not a parallelism primitive  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JavaScript does one thing at a time,     │
│              │  but never waits for anything."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Microtask Queue → Promise → async/await   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Node.js HTTP server under load. You notice that `p99` response latency spikes to 800ms periodically — the GC logs show no pressure, CPU is at 30%, and all database queries are fast (< 5ms). A flamegraph shows a JSON serialisation function taking 200ms synchronously during those spikes. Explain precisely which phase of the event loop is blocked, what happens to other in-flight requests during those 200ms, and what two architectural approaches could fix it — with their trade-offs.

**Q2.** Consider this code running in the browser: a `click` handler triggers a long `Promise` chain (50 `.then()` callbacks each doing light work), and midway through the chain a `setTimeout(fn, 0)` is registered. Trace exactly when the setTimeout callback executes relative to the Promise chain — and then explain how your answer would differ if the same code ran in Node.js using `process.nextTick` instead of Promises.

