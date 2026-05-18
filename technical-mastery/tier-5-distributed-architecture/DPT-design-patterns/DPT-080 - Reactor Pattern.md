---
id: DPT-080
title: Reactor Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-039
used_by: []
related: DPT-039, DPT-040, DPT-065, DPT-084
tags:
  - pattern
  - concurrency
  - advanced
  - event-loop
  - non-blocking
  - io
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/design-patterns/reactor-pattern/
---

⚡ TL;DR - The Reactor Pattern handles service requests
that are delivered concurrently by one or more inputs
using an event loop that demultiplexes requests and
dispatches them synchronously to associated request
handlers. It enables high-concurrency I/O on a single
thread: the foundation of Node.js, Nginx, Redis, Netty.

| #80 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-039 | |
| **Used by:** | N/A | |
| **Related:** | DPT-039, DPT-040, DPT-065, DPT-084 | |

---

### 🔥 The Problem This Solves

**THE THREAD-PER-CONNECTION PROBLEM:**
A traditional web server creates one thread per connection.
With 10,000 simultaneous connections (C10K problem):
- 10,000 threads × ~1MB stack = ~10GB RAM just for stacks
- OS scheduling overhead for 10,000 threads
- Most threads blocked, waiting for network I/O

The threads are mostly idle, blocked waiting for:
- The network packet to arrive
- The database to respond
- The file system to read the requested file

The CPU is available but threads are sleeping. This
is waste: memory consumed by idle stacks, scheduler
overhead for blocked threads.

**THE REACTOR INSIGHT:**
Use a SINGLE THREAD with an event loop. Instead of
blocking while waiting for I/O, register interest in
I/O events. When I/O is ready: dispatch to a handler.
One thread handles thousands of connections: it never
blocks waiting for any one connection.

---

### 📘 Textbook Definition

The **Reactor Pattern** (Douglas C. Schmidt, 1995) is
a concurrent architectural pattern for event-driven
systems:

> "The Reactor Pattern handles service requests that
> are delivered concurrently to an application by one
> or more clients. The application can register specific
> handlers for processing which are called by initiation
> dispatcher when a specific event occurs."

**Core components:**
- **Handle (File Descriptor):** an I/O resource from
  the OS (socket, file descriptor, timer). Events occur
  on handles.
- **Synchronous Event Demultiplexer:** OS mechanism
  (`select`, `poll`, `epoll`, `kqueue`) that waits for
  events on a set of handles without blocking indefinitely.
- **Reactor/Initiation Dispatcher:** the event loop.
  Registers handlers, waits for events via the demultiplexer,
  dispatches to the appropriate handler.
- **Event Handler (interface):** callback interface
  registered for specific events on handles.
- **Concrete Event Handler:** implements the callback;
  contains the actual business logic for handling the event.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One thread waits for I/O events on many connections
simultaneously. When a connection has data ready: call
the registered handler. Never block waiting for one connection.

**One analogy:**
> An airport gate agent.
>
> Thread-per-connection model: one agent per passenger,
> each agent waiting at their specific passenger's seat
> until that passenger is ready to board. 400 passengers
> = 400 agents waiting, most doing nothing.
>
> Reactor model: ONE gate agent watching the boarding
> area. When a passenger is ready (event: passenger
> arrives at gate), the agent processes them (dispatch
> to handler). The agent never waits blocked for any
> one passenger; they serve whoever is ready.
>
> The gate display board = the demultiplexer (shows which
> passenger is ready). The agent = the event loop.
> The boarding procedure = the event handler.

---

### 🔩 First Principles Explanation

**SYNCHRONOUS EVENT DEMULTIPLEXING:**
The OS kernel knows which file descriptors have data
ready. `epoll` (Linux), `kqueue` (BSD/macOS), `IOCP`
(Windows) are kernel interfaces that let a single thread
ask: "which of these 10,000 sockets has data ready?"
The kernel returns the READY sockets immediately.
The thread only processes ready sockets. It never
blocks waiting for a specific socket.

This is the "demultiplexing" step: many input streams
multiplexed into one event loop; the demultiplexer
separates them and tells the loop which is ready.

**EVENT DISPATCH:**
After demultiplexing, the reactor dispatches to the
registered handler. Each handle (socket) has a registered
handler. The reactor calls the handler's callback.
The handler processes the data synchronously (should
be fast; long-running processing would block the event loop).

**WHY SINGLE-THREADED REACTOR WORKS:**
The assumption: I/O operations dominate execution time.
CPU processing (per request) is fast. I/O wait is long.
A single thread can handle thousands of connections
because it is only "busy" (processing a handler) for
the brief CPU-intensive portion. During I/O waits:
the thread serves OTHER connections.

**WHEN SINGLE-THREADED REACTOR BREAKS:**
If handlers do CPU-intensive work (image processing,
complex computation): the event loop blocks. All other
connections wait. Solution: offload CPU work to a
worker thread pool (hybrid model: Reactor for I/O,
thread pool for CPU-bound work). Node.js implements
exactly this hybrid with its libuv thread pool.

---

### 🧪 Thought Experiment

**1000 CONNECTIONS, 1 THREAD:**
At any instant: 999 connections are waiting for data.
1 connection has data available.

Thread-per-connection: 1000 threads, 999 sleeping.
Reactor: 1 thread, calls `epoll_wait` (returns immediately
with the 1 ready socket), processes that socket,
calls `epoll_wait` again. 999 sleeping threads = 0.
Memory: 1 thread stack instead of 1000.
Context switches: near zero (no idle threads to schedule).

The connection count limit shifts: from
"how many threads can the OS schedule?" to
"how many file descriptors can the OS track?" (millions).

---

### 🧠 Mental Model / Analogy

> Reactor = the "select" at a restaurant model.
>
> Thread-per-connection: one waiter permanently assigned
> to each table. 100 tables = 100 waiters, mostly standing
> at their table waiting for the customer to decide.
>
> Reactor model: ONE waiter watching all tables.
> When a table raises their hand (I/O ready event):
> the waiter goes over (dispatch to handler), takes
> the order (processes the event), returns to watching.
>
> The waiter serves WHOEVER IS READY. They do not stand
> blocked at any one table waiting.
>
> The kitchen (CPU-bound work) gets tickets from the waiter.
> Long cooking (slow CPU work) goes to kitchen workers
> (worker thread pool), not to the waiter (event loop).
> The waiter stays free to serve new tables.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - The event loop concept:**
The reactor is an infinite loop: wait for events,
dispatch to handlers, repeat. The loop sleeps inside
`epoll_wait` (or equivalent) when no events are ready,
consuming zero CPU. When an event arrives: dispatched
and processed. Then back to sleep.

**Level 2 - Reactor implementations:**
- **Node.js**: V8 + libuv. Single-threaded event loop.
  I/O via libuv (epoll on Linux). Async callbacks/Promises.
- **Netty (Java)**: `EventLoopGroup` with multiple event
  loops (multi-reactor). NIO Selector = the demultiplexer.
- **Nginx**: master process + worker processes. Each
  worker: single-threaded reactor using epoll.
- **Redis**: single-threaded reactor for command processing.
  `ae` event loop library with platform-specific demultiplexer.
- **Project Loom (Java)**: virtual threads reduce the need
  for explicit reactor design; the JVM implements the
  reactor internally.

**Level 3 - Reactor variants:**
- **Single-Reactor Single-Thread**: classic (Node.js):
  one event loop, all handling on one thread.
- **Single-Reactor Multi-Thread**: one event loop (I/O),
  handler dispatched to a thread pool (CPU work).
- **Multi-Reactor (Boss/Worker model)**: one "boss" reactor
  accepts connections; multiple "worker" reactors handle
  read/write events. Netty's `NioEventLoopGroup` with
  bossGroup and workerGroup implements this. The boss
  reactor's sole job: accept new connections, distribute
  to worker reactors. Worker reactors: handle all data
  for their assigned connections.

---

### ⚙️ How It Works (Mechanism)

```
Reactor Pattern - Event Loop
┌─────────────────────────────────────────────────────────┐
│                    EVENT LOOP (1 thread)                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Registered handles: [sock1, sock2, ..., sock10K]│   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│           epoll_wait() ←── blocks until any ready      │
│                    │                                    │
│       ┌────────────▼──────────────────┐                │
│       │ Ready: [sock42, sock1337]      │                │
│       └────────────┬──────────────────┘                │
│                    │                                    │
│       ┌────────────▼──────────────────┐                │
│       │ Dispatch to registered handler│                │
│       │  sock42.handler.onReadable()  │                │
│       │  sock1337.handler.onReadable()│                │
│       └────────────┬──────────────────┘                │
│                    │                                    │
│              back to epoll_wait()                      │
└─────────────────────────────────────────────────────────┘
│ CRITICAL RULE: Handlers MUST be fast (non-blocking).   │
│ Long-running handler = event loop blocked = ALL         │
│ connections stalled.                                    │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Java NIO as a manual Reactor:**

```java
// BAD: Thread-per-connection (does not scale to thousands).

class ThreadPerConnectionServer {
    void start() throws IOException {
        ServerSocket ss = new ServerSocket(8080);
        while (true) {
            Socket client = ss.accept();
            // Each connection: a new thread.
            // 10,000 connections = 10,000 threads.
            new Thread(() -> handle(client)).start();
        }
    }
    void handle(Socket client) {
        // Blocks this thread waiting for data.
        // Thread sleeps while client is idle.
    }
}
```

```java
// GOOD: Java NIO Reactor (manual implementation).

import java.nio.*;
import java.nio.channels.*;
import java.util.*;

class NioReactor {

    private final Selector selector;   // demultiplexer

    NioReactor() throws IOException {
        this.selector = Selector.open();
    }

    void register(ServerSocketChannel ssc) throws IOException {
        ssc.configureBlocking(false);
        ssc.register(selector, SelectionKey.OP_ACCEPT,
            new AcceptHandler(ssc, selector));
    }

    // Event loop: single thread
    void run() throws IOException {
        while (!Thread.interrupted()) {
            // Waits for any registered event (blocks only if
            // zero events are ready - no CPU spin).
            selector.select();
            Set<SelectionKey> keys = selector.selectedKeys();
            Iterator<SelectionKey> it = keys.iterator();
            while (it.hasNext()) {
                SelectionKey key = it.next();
                it.remove();
                EventHandler handler =
                    (EventHandler) key.attachment();
                // Dispatch: each handler must be fast!
                handler.handle(key);
            }
        }
    }
}

class AcceptHandler implements EventHandler {
    private final ServerSocketChannel ssc;
    private final Selector selector;

    AcceptHandler(ServerSocketChannel ssc, Selector selector) {
        this.ssc = ssc; this.selector = selector;
    }

    @Override
    public void handle(SelectionKey key) throws IOException {
        SocketChannel client = ssc.accept();
        if (client != null) {
            client.configureBlocking(false);
            // Register read event for new connection:
            client.register(selector, SelectionKey.OP_READ,
                new ReadHandler(client)); // delegate to read handler
        }
    }
}

class ReadHandler implements EventHandler {
    private final SocketChannel client;
    ReadHandler(SocketChannel client) { this.client = client; }

    @Override
    public void handle(SelectionKey key) throws IOException {
        ByteBuffer buf = ByteBuffer.allocate(1024);
        int bytesRead = client.read(buf);
        if (bytesRead == -1) {
            client.close(); // connection closed
        } else {
            // Process data here. MUST be fast.
            // Long processing: submit to ExecutorService.
            String request = new String(buf.array(),
                0, bytesRead);
            processRequest(request);
        }
    }
    // processRequest must NOT block the event loop.
}
```

---

### 🔥 Failure Scenarios

**BLOCKING IN THE EVENT LOOP:**
```java
// BAD: Blocking call inside handler blocks event loop.
class ReadHandler implements EventHandler {
    @Override
    public void handle(SelectionKey key) throws IOException {
        String data = readData(key.channel());
        // DISASTER: synchronous DB call in event loop.
        String result = database.query(data); // blocks 50ms
        // During these 50ms: ALL connections are stalled.
        sendResponse(key.channel(), result);
    }
}
```
**Symptom**: latency spikes on ALL connections when any
single connection's handler does slow work. Request
rate drops. All connections wait for the slow handler.
**Fix**: Submit CPU/IO-bound work to an external thread pool.
```java
executorService.submit(() -> {
    String result = database.query(data);    // off event loop
    eventLoop.schedule(() -> sendResponse(result)); // re-enter
});
```

**MEMORY LEAK FROM UN-CANCELLED KEYS:**
```java
// BAD: Not cancelling selection key on disconnect.
void handle(SelectionKey key) throws IOException {
    int bytesRead = channel.read(buf);
    if (bytesRead == -1) {
        channel.close(); // socket closed but key still in selector
        // key NOT cancelled: selector still watches dead socket
        // Accumulates over time: memory leak + "ready" events
        // for dead socket on every select() call.
    }
}
// FIX: key.cancel() + channel.close() on disconnect.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Single-threaded = slow | Single-threaded reactor can handle 100K+ connections efficiently because I/O wait is parallelized by the OS kernel. The bottleneck is CPU processing per request, not the thread count |
| Reactor requires Node.js or async/await syntax | The Reactor Pattern is a structural pattern. It can be implemented in any language. Java NIO (Selector), Netty, Vert.x, and Reactor/Project Reactor all implement variants in Java |
| Blocking in a handler is OK if it is fast | Even brief blocking in the event loop affects ALL connections. For high-throughput systems: any I/O in a handler (even "fast" DB queries at 5ms) should be non-blocking or offloaded. At 100K RPS with 5ms blocking: the event loop is perpetually stalled |
| Multi-reactor = multi-threading defeats the point | Multi-reactor (boss/worker groups) is NOT about giving each connection a thread. It distributes event loops across CPU cores (each loop is single-threaded). Worker reactors still handle thousands of connections per thread. Reactor multiplies with CPU cores, not with connections |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Single thread, event loop, handles many │
│              │ I/O connections via demultiplexer.      │
├──────────────┼──────────────────────────────────────────┤
│ DEMULTIPLEXER│ epoll (Linux), kqueue (BSD), IOCP (Win)  │
│              │ Java: Selector. Returns READY handles.  │
├──────────────┼──────────────────────────────────────────┤
│ GOLDEN RULE  │ NEVER block in the event loop handler.  │
│              │ CPU/IO work → executor/worker pool.     │
├──────────────┼──────────────────────────────────────────┤
│ IMPLEMENTATIONS│ Node.js, Nginx, Redis, Netty, Vert.x  │
│              │ Java NIO Selector, libuv, Tokio (Rust)  │
├──────────────┼──────────────────────────────────────────┤
│ MULTI-REACTOR│ Boss accepts, workers handle. Netty:    │
│              │ bossGroup + workerGroup pattern.        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-081: Anti-Pattern - Shotgun Surgery │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Reactor = one thread, many connections, non-blocking I/O.
   The event loop sleeps in `epoll_wait` (zero CPU) until
   an event is ready. Only the ready connections are
   processed. Thousands of idle connections consume
   near-zero resources.
2. Golden rule: NEVER block in the event loop handler.
   A blocking call (DB, file I/O, sleep) stops ALL
   connections for the duration. Offload to a thread pool.
   Return control to the loop immediately.
3. Real implementations: Node.js (JavaScript + libuv),
   Netty (Java NIO + boss/worker reactor groups),
   Nginx (worker processes each running a reactor),
   Redis (single-threaded ae event loop). All use the
   same core principle: one event loop per thread,
   epoll/kqueue for demultiplexing.

