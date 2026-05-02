---
layout: default
title: "Event-Driven Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 6
permalink: /cs-fundamentals/event-driven-programming/
number: "0006"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Imperative Programming, Functions, Asynchronous Programming
used_by: Reactive Programming, Node.js, JavaScript
related: Reactive Programming, Observer Pattern, Message-Driven Architecture
tags:
  - intermediate
  - pattern
  - mental-model
  - architecture
  - javascript
  - nodejs
---

# 006 — Event-Driven Programming

⚡ TL;DR — Event-driven programming structures code around reacting to events — things that happen — rather than executing a fixed top-to-bottom sequence.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0006 │ Category: CS Fundamentals — Paradigms │ Difficulty: ★★☆ │
├──────────────┼───────────────────────────────────────┼─────────────────────────┤
│ Depends on: │ Imperative Programming, Functions, │ │
│ │ Asynchronous Programming │ │
│ Used by: │ Reactive Programming, Node.js, │ │
│ │ JavaScript │ │
│ Related: │ Reactive Programming, Observer, │ │
│ │ Message-Driven Architecture │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A GUI application needs to respond to user clicks, network
responses, and timer expiry — all at unpredictable times.
Without event-driven programming, the only alternative is
polling: continuously asking "has the button been clicked?
Has the network responded? Has the timer fired?" in a tight
loop. At 60 times per second, this consumes 100% of a CPU
core — just waiting. The application is unresponsive to all
other inputs while blocking on any single check.

THE BREAKING POINT:
Real-world software deals with asynchronous, unpredictable
inputs: user actions, hardware interrupts, network packets,
timer callbacks. Sequential polling is both wasteful (burns
CPU) and incorrect (misses events that occur between polls).
A web server polling for HTTP requests one at a time can
handle ~1 request per second versus 10,000 for an event-driven
Node.js server on the same hardware.

THE INVENTION MOMENT:
This is exactly why Event-Driven Programming was created. By
inverting control — "call me when something happens" instead
of "I'll keep asking if something happened" — programs sleep
cheaply, wake instantly, and handle thousands of concurrent
events on a single thread.

### 📘 Textbook Definition

Event-driven programming is a paradigm in which the flow of
program execution is determined by events — signals produced
by user actions, hardware interrupts, messages, or timer
expiry. Programs register event handlers (callbacks) with an
event loop or dispatcher; when an event fires, the dispatcher
invokes the appropriate handler. Control is inverted: the
framework calls your code, not the other way around. JavaScript
in browsers, Node.js, GUI frameworks (Swing, Qt, WPF), and
messaging systems (Kafka consumers) all use this model.

### ⏱️ Understand It in 30 Seconds

**One line:**
Register what should happen when something happens — the program reacts, it doesn't poll.

**One analogy:**

> A restaurant uses event-driven programming. Waiters don't stand
> over every table asking "are you ready to order?" every 10
> seconds. Instead, you press the call button. The waiter is
> notified (the event fires) and responds. Everyone waits for
> their event, nobody burns energy polling.

**One insight:**
The critical shift is inversion of control: instead of your
code asking "is there work?" in a loop, the event loop asks
"who wants to handle this?" when work arrives. One thread can
handle thousands of concurrent connections because it's
sleeping between events, not busy-waiting.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Events are notifications that something happened — they
   carry a payload (what happened, when, with what data).
2. Handlers (listeners/callbacks) are functions registered
   to respond to specific event types — they run when events
   fire, not in sequence.
3. An event loop (or dispatcher) is the engine — it waits for
   events, routes them to registered handlers, and returns
   to waiting. It never blocks.

DERIVED DESIGN:
Given invariant 3, the event loop must be non-blocking — any
handler that blocks (sleeps, waits for I/O) stalls ALL other
event handling. This is why Node.js's single-threaded event
loop requires async I/O: `fs.readFile(path, callback)` returns
immediately, the OS handles the read, and the callback fires
when complete. The loop is free to handle other events.

The design forces:

- Callbacks or Promises/async-await for I/O
- State must be maintained explicitly (closures, objects)
  because handlers don't share a sequential context
- Error handling becomes per-event, not per-function

THE TRADE-OFFS:
Gain: High concurrency on a single thread; natural fit for
I/O-bound workloads; immediate responsiveness to inputs.
Cost: "Callback hell" / complex async flows; no linear
execution trace to follow when debugging; shared mutable
state between handlers is tricky; CPU-bound tasks
block the event loop.

### 🧪 Thought Experiment

SETUP:
A web server receives 1,000 simultaneous HTTP requests, each
requiring a 10ms database query. You have 1 CPU core.

WHAT HAPPENS WITH THREAD-PER-REQUEST (blocking):
Each request blocks a thread for 10ms waiting for the DB.
With a thread pool of 100 threads, you can handle 100
concurrent requests. Requests 101–1000 queue. Thread overhead:
each thread consumes ~1MB stack. 1000 threads = 1GB RAM.
Throughput: 100 threads × 100 req/s = 10,000 req/s max.

WHAT HAPPENS WITH EVENT-DRIVEN (non-blocking):
1 thread handles all 1,000 requests. When a DB query is
issued, the thread doesn't wait — it registers a callback
and handles the next request. When the DB responds (after
10ms), the event loop fires the callback, sends the response.
All 1,000 queries are in-flight simultaneously. Memory: 1
thread + 1,000 lightweight event registrations ≈ 10MB.
Throughput: 1,000 req / 10ms = 100,000 req/s — 10x better.

THE INSIGHT:
For I/O-bound work, one event-driven thread can outperform
100 blocking threads by keeping the CPU busy between I/O waits
instead of blocking.

### 🧠 Mental Model / Analogy

> An event-driven system is like a smoke detector network.
> Each detector is dormant — it doesn't actively check for fire.
> When smoke is detected (event fires), it sends a signal
> (event payload). The alarm system (event dispatcher) routes
> the signal to the right actions: sound alarm, notify fire
> department, open sprinklers. Nobody polls anything.

"Smoke detector" → event source (button click, HTTP request)
"Smoke detected" → event emitted
"The alarm system" → event dispatcher / event loop
"Sound alarm action" → registered event handler / callback
"The specific room" → event type (click, message, timeout)

Where this analogy breaks down: unlike a smoke detector,
software events can queue up — if handlers are slow, the queue
grows and memory is consumed. A smoke detector doesn't have
a backlog.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Event-driven programming means: "Call this function when this
thing happens." Instead of writing code that runs from top to
bottom, you say "when the user clicks Submit, run `handleSubmit`."
The program sits quietly until something happens, then responds.

**Level 2 — How to use it (junior developer):**
In JavaScript, use `addEventListener('click', handler)` to
register handlers. In Node.js, `fs.readFile(path, callback)`
is non-blocking — the callback fires when the file is ready.
Never put long-running or synchronous-blocking code in a handler
— it will freeze the event loop and block all other handlers.

**Level 3 — How it works (mid-level engineer):**
The Node.js event loop (powered by libuv) has 6 phases: timers
(setTimeout callbacks), pending I/O callbacks, idle/prepare,
poll (wait for I/O events), check (setImmediate), close
callbacks. Each iteration runs callbacks for ready events in
that phase. The OS kernel uses `epoll` (Linux) or `kqueue`
(macOS) — system calls that block the thread until any of
N file descriptors has data ready. This is how one thread
monitors thousands of connections.

**Level 4 — Why it was designed this way (senior/staff):**
The event-driven model emerged from GUI programming in the
1970s (Smalltalk's Model-View-Controller) and was later applied
to networking by Ryan Dahl in Node.js (2009) after observing
that Apache's thread-per-connection model hit memory limits at
C10K (10,000 concurrent connections). The C10K problem (Kegel, 1999) demonstrated that OS thread context switching overhead
made 10K threads infeasible. The event loop avoids context
switching by never blocking — the kernel's `epoll` does the
waiting, not threads. The trade-off: CPU-bound tasks can't
be event-loop-friendly without worker threads.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│         NODE.JS EVENT LOOP CYCLE                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐                                │
│  │  timers       │ setTimeout/setInterval cbs     │
│  └──────┬───────┘                                │
│         ↓                                        │
│  ┌──────────────┐                                │
│  │ pending I/O  │ completed OS I/O callbacks     │
│  └──────┬───────┘                                │
│         ↓                                        │
│  ┌──────────────┐                                │
│  │   poll       │ ← YOU ARE HERE                 │
│  │              │ Wait for I/O (epoll/kqueue)     │
│  │              │ Run ready I/O callbacks         │
│  └──────┬───────┘                                │
│         ↓                                        │
│  ┌──────────────┐                                │
│  │   check      │ setImmediate callbacks          │
│  └──────┬───────┘                                │
│         ↓                                        │
│  ┌──────────────┐                                │
│  │ close events │ socket.close etc.              │
│  └──────┬───────┘                                │
│         └──────────────────────────┐             │
│                        loop again ↑              │
└──────────────────────────────────────────────────┘
```

**Event registration:** `socket.on('data', handler)` stores the
handler function in a map keyed by event type. The OS is told
to monitor the socket's file descriptor.

**Event detection:** The poll phase calls `epoll_wait()` — an OS
system call that blocks the thread until ANY monitored file
descriptor has data. When data arrives, `epoll_wait` returns
immediately with the list of ready descriptors.

**Handler dispatch:** The event loop looks up the handler for
each ready event and calls it synchronously. The handler must
return quickly — it is NOT running in a separate thread.

**Happy path:** Handlers are fast, non-blocking, and async I/O
is used for all I/O operations. The event loop cycles rapidly
and throughput is high.

**Failure path:** A handler performs a synchronous blocking
operation (e.g., `fs.readFileSync`). The loop is blocked for
the duration — ALL other events queue up and are not processed
until the blocking operation completes.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[HTTP request arrives on socket]
  → [OS: epoll signals file descriptor is ready]
  → [Event loop poll phase wakes up]
  → [Routes to HTTP 'request' event handler]
  → [Handler ← YOU ARE HERE]
  → [Handler calls db.query(sql, callback) — non-blocking]
  → [Handler returns immediately]
  → [Event loop processes other events]
  → [DB responds — I/O event fires]
  → [DB callback runs, sends HTTP response]
```

FAILURE PATH:
[Handler calls synchronous sleep(5000)]
→ [Event loop blocked 5 seconds]
→ [All pending requests queue, time out]
→ [Observable: high response latency, request timeouts]

WHAT CHANGES AT SCALE:
At 10x load, a single event loop handles it if handlers are
non-blocking — throughput scales with I/O concurrency, not
thread count. At 100x, CPU-bound handlers become bottlenecks
— Node.js cluster module or worker threads are needed. At
1000x, the event loop model distributes across multiple
processes/machines; event routing must be handled by a message
broker (Kafka, RabbitMQ).

### 💻 Code Example

**Example 1 — Blocking vs. non-blocking (Node.js):**

```javascript
// BAD: synchronous blocking — freezes event loop
const fs = require("fs");

http.createServer((req, res) => {
  // This blocks the ENTIRE server while reading:
  const data = fs.readFileSync("large-file.txt", "utf8");
  res.end(data);
});

// GOOD: async non-blocking — event loop stays free
http.createServer((req, res) => {
  fs.readFile("large-file.txt", "utf8", (err, data) => {
    if (err) {
      res.statusCode = 500;
      res.end();
      return;
    }
    res.end(data); // only called when file is ready
  });
  // returns immediately — loop handles other requests
});
```

**Example 2 — EventEmitter pattern (Node.js):**

```javascript
const EventEmitter = require("events");

class OrderService extends EventEmitter {
  placeOrder(order) {
    // Process order...
    this.emit("orderPlaced", { orderId: order.id });
  }
}

const service = new OrderService();

// Register handlers — decoupled from OrderService
service.on("orderPlaced", ({ orderId }) => {
  console.log(`Sending confirmation for ${orderId}`);
});

service.on("orderPlaced", ({ orderId }) => {
  console.log(`Updating inventory for ${orderId}`);
});

service.placeOrder({ id: "ORD-001" });
// Both handlers fire — neither OrderService knows about them
```

**Example 3 — Promises for cleaner async flow:**

```javascript
// BAD: callback hell (pyramid of doom)
fetchUser(id, (user) => {
  fetchOrders(user.id, (orders) => {
    fetchProducts(orders[0].id, (product) => {
      console.log(product); // deeply nested
    });
  });
});

// GOOD: async/await (event-driven under the hood)
async function getFirstProduct(userId) {
  const user = await fetchUser(userId);
  const orders = await fetchOrders(user.id);
  const product = await fetchProducts(orders[0].id);
  return product; // flat, readable, same async behaviour
}
```

### ⚖️ Comparison Table

| Model              | Concurrency     | CPU-bound?         | Memory           | Best For                     |
| ------------------ | --------------- | ------------------ | ---------------- | ---------------------------- |
| **Event-driven**   | Very high (I/O) | Poor (blocks loop) | Low              | I/O-heavy servers, GUIs      |
| Thread-per-request | Medium          | Good               | High (MB/thread) | CPU-bound workloads          |
| Actor model        | Very high       | Good               | Medium           | Distributed systems          |
| Reactive streams   | Very high       | Good               | Low              | Backpressure-aware pipelines |

How to choose: Use event-driven for I/O-bound servers (APIs,
websockets, file serving). Use thread pools for CPU-bound work
(image processing, encryption). Combine both with worker threads.

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────────┐
│        EVENT HANDLER LIFECYCLE                   │
├──────────────────────────────────────────────────┤
│  [Register] handler = source.on('event', fn)     │
│       ↓                                          │
│  [Dormant] handler is stored in event map        │
│       ↓  (event fires)                           │
│  [Invoked] event loop calls fn(eventData)        │
│       ↓                                          │
│  [Executing] fn runs synchronously in the loop   │
│       ↓  (async I/O issued)                      │
│  [Returns] fn returns — loop continues           │
│       ↓  (I/O completes)                         │
│  [Callback] inner callback fires with result     │
│       ↓                                          │
│  [Deregister] source.off('event', fn) if done    │
└──────────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                          |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Event-driven means multi-threaded            | Node.js is single-threaded; its high concurrency comes from non-blocking I/O, not threads                                        |
| async/await means the code runs in parallel  | async/await is syntactic sugar for event-driven callbacks — it doesn't add threads; code still runs on the event loop            |
| Event-driven is always faster than threaded  | For CPU-bound work, threads are faster; event-driven wins only for I/O-bound work                                                |
| Events are queued in order they were emitted | Different event types have different priorities in the event loop phases; `setImmediate` fires before `setTimeout(0)` in Node.js |

### 🚨 Failure Modes & Diagnosis

**1. Event Loop Blocking**

Symptom:
Server response times spike to seconds; all requests time out
simultaneously; CPU usage drops to near zero (loop is blocked,
not processing).

Root Cause:
A synchronous operation (file read, JSON parse of large payload,
crypto.pbkdf2Sync) is called inside an event handler, blocking
the loop.

Diagnostic:

```bash
# Node.js: detect blocking with --prof
node --prof app.js
node --prof-process isolate-*.log | grep "Heavy"

# Or use clinic.js for live diagnosis
npx clinic doctor -- node app.js
```

Fix:

```javascript
// BAD: blocks the event loop
app.post("/hash", (req, res) => {
  const hash = crypto.pbkdf2Sync(
    // synchronous!
    req.body.password,
    "salt",
    100000,
    64,
    "sha512",
  );
  res.json({ hash: hash.toString("hex") });
});

// GOOD: async version — loop stays free
app.post("/hash", async (req, res) => {
  const hash = await new Promise((resolve, reject) => {
    crypto.pbkdf2(
      req.body.password,
      "salt",
      100000,
      64,
      "sha512",
      (err, key) => (err ? reject(err) : resolve(key)),
    );
  });
  res.json({ hash: hash.toString("hex") });
});
```

Prevention: Never use `*Sync` functions in request handlers;
use `worker_threads` for CPU-bound tasks.

**2. Event Handler Memory Leak**

Symptom:
Memory grows continuously; `process.memoryUsage()` shows
growing `heapUsed`; EventEmitter warning: "MaxListenersExceeded."

Root Cause:
Handlers are registered inside a loop or function that runs
repeatedly, but `off()` is never called. Each registration
holds a closure reference — the references accumulate.

Diagnostic:

```bash
# Node.js: check listener counts
emitter.listenerCount('data')  # should stay constant

# Memory snapshot in Chrome DevTools
node --inspect app.js
# Open chrome://inspect → Memory → Take Heap Snapshot
```

Fix:

```javascript
// BAD: registers a new handler on every request
app.get("/stream", (req, res) => {
  // This handler is NEVER removed:
  dataSource.on("data", (chunk) => res.write(chunk));
});

// GOOD: remove handler when done
app.get("/stream", (req, res) => {
  const handler = (chunk) => res.write(chunk);
  dataSource.on("data", handler);
  req.on("close", () => dataSource.off("data", handler));
});
```

Prevention: Always pair `on()` with `off()` for long-lived
emitters; use `once()` for single-fire handlers.

**3. Unhandled Promise Rejection**

Symptom:
Async operations silently fail; no error in logs; data appears
missing or null unexpectedly.

Root Cause:
A rejected Promise inside an async event handler has no
`.catch()` or `try/catch` — the rejection is swallowed.

Diagnostic:

```bash
# Node.js: enable unhandled rejection detection
node --unhandled-rejections=throw app.js

# Or listen globally
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection:', reason);
});
```

Fix:

```javascript
// BAD: rejection silently swallowed
emitter.on("request", async (req) => {
  const data = await fetchData(req.id); // if this rejects:
  process(data); // never reached, no error logged
});

// GOOD: explicit error handling
emitter.on("request", async (req) => {
  try {
    const data = await fetchData(req.id);
    process(data);
  } catch (err) {
    console.error("Request failed:", err);
    // handle error appropriately
  }
});
```

Prevention: Always add `try/catch` inside async event handlers;
set up a global unhandledRejection listener as a safety net.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Imperative Programming` — event handlers contain imperative code
- `Functions` — handlers are first-class functions/callbacks
- `Synchronous vs Asynchronous` — events are the mechanism for async programming

**Builds On This (learn these next):**

- `Reactive Programming` — composable event streams built on top of EDP
- `Observer Pattern` — the design pattern formalising event registration
- `Node.js` — the most prominent server-side event-driven runtime

**Alternatives / Comparisons:**

- `Reactive Programming` — extends EDP with composable, backpressure-aware streams
- `Actor Model` — independent actors with message passing; similar but with isolation
- `Thread-per-request` — the alternative concurrency model using blocking threads

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Structuring code to REACT to events │
│ │ rather than executing sequentially │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Polling wastes CPU; blocking stalls all │
│ SOLVES │ other work; sequential code can't handle │
│ │ 10K concurrent I/O-bound requests │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Inversion of control: the framework calls │
│ │ your handler — you don't ask for events │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ I/O-bound servers, GUIs, real-time │
│ │ systems, or when inputs are unpredictable │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ CPU-bound computation dominates; handler │
│ │ code is complex sequential logic │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ High I/O concurrency vs. complexity of │
│ │ async flows and shared state management │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "A smoke detector: dormant until needed, │
│ │ instantly responsive when triggered." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reactive Programming → Observer Pattern │
│ │ → Node.js Event Loop │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A Node.js service handles both fast API calls (1ms) and
slow image processing (200ms). Both use the same event loop.
Trace step-by-step what happens to the 1ms API calls when 50
concurrent image processing requests arrive simultaneously —
and design the architectural change that resolves this, without
switching away from Node.js.

**Q2.** An event system allows handlers to register for the
same event type. Handler A modifies shared state; Handler B
reads the same shared state, expecting it to be unmodified.
They both receive `userLoggedIn` events. Describe the exact
conditions under which this produces a bug, and explain why
this problem doesn't exist in a purely functional event-driven
system.
