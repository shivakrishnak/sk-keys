---
layout: default
title: "Non-Blocking I/O"
parent: "Operating Systems"
nav_order: 105
permalink: /operating-systems/non-blocking-io/
number: "0105"
category: Operating Systems
difficulty: ★★☆
depends_on: Blocking I/O, File Descriptor, System Call (syscall)
used_by: epoll / kqueue / io_uring, Async I/O, Reactive Programming
related: Blocking I/O, Async I/O, epoll / kqueue / io_uring
tags:
  - os
  - networking
  - internals
  - intermediate
  - performance
---

# 105 — Non-Blocking I/O

⚡ TL;DR — Non-blocking I/O returns immediately with "no data yet" instead of sleeping — letting one thread manage thousands of connections without blocking on any of them.

| #0105           | Category: Operating Systems                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Blocking I/O, File Descriptor, System Call (syscall)       |                 |
| **Used by:**    | epoll / kqueue / io_uring, Async I/O, Reactive Programming |                 |
| **Related:**    | Blocking I/O, Async I/O, epoll / kqueue / io_uring         |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
With blocking I/O, a server handling 10,000 simultaneous clients needs 10,000 threads — each blocked waiting for their client to send data. Thread stacks consume ~10 GB RAM and the scheduler thrashes between 10,000 runnable/sleeping threads. The server maxes out at around 10,000 connections regardless of actual network throughput.

THE BREAKING POINT:
In 1999, the "C10K problem" paper formally documented that web servers couldn't scale to 10,000 simultaneous connections using the thread-per-client model. With the rise of long-lived connections (push notifications, streaming, WebSockets), 100,000+ concurrent idle connections became common requirements.

THE INVENTION MOMENT:
This is exactly why Non-Blocking I/O was created — by setting `O_NONBLOCK` on a file descriptor, I/O operations return instantly with `EAGAIN` if no data is ready, freeing one thread to service all connections by checking which ones are ready.

---

### 📘 Textbook Definition

**Non-blocking I/O** is an I/O mode where syscalls such as `read()`, `write()`, `accept()`, and `connect()` on a file descriptor marked with `O_NONBLOCK` (or `SOCK_NONBLOCK`) return immediately, regardless of data availability. If the operation cannot be completed (no data to read, send buffer full), the syscall returns `-1` with `errno = EAGAIN` (or `EWOULDBLOCK`). The caller must retry later — typically by using a readiness-notification mechanism (`select`, `poll`, `epoll`, `kqueue`) to know when the descriptor is ready before attempting the operation again.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Non-blocking I/O asks "is there data?" — if not, it immediately says "no" and lets you go do something else.

**One analogy:**

> Instead of waiting at the door until your food is delivered, you set a timer and check periodically. "Food here yet? No." … "Food here yet? No." … "Food here yet? Yes!" You can do other things between checks. Efficient with many deliveries happening simultaneously — one person can track a hundred orders.

**One insight:**
Non-blocking I/O alone is insufficient — you need a multiplexer (epoll/kqueue) to efficiently tell you WHICH descriptors are ready without polling all of them in a loop. `O_NONBLOCK` + `epoll` is the combination that enables a single thread to handle 100,000 simultaneous connections.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. A non-blocking syscall never sleeps — it returns immediately whether data is available or not.
2. `EAGAIN` means "try again later" — not an error, a signal to defer and retry.
3. Non-blocking I/O is inherently callback/event-driven — you need notification of when to retry.

DERIVED DESIGN:
Setting `O_NONBLOCK` via `fcntl(fd, F_SETFL, O_NONBLOCK)` changes the kernel's behaviour in the socket/file state machine. When `read()` is called on a non-blocking socket and the receive buffer is empty, instead of adding the thread to the wait queue, the kernel immediately returns `EAGAIN`. The application must then use `select()`/`poll()`/`epoll()` to block efficiently on a SET of descriptors, waking only when at least one is ready. This inverts the blocking model: the application blocks on "which descriptor is ready?" not "wait for this specific operation to complete."

THE TRADE-OFFS:
Gain: One thread can multiplex thousands of connections; no wasted thread stacks; deterministic throughput.
Cost: Code complexity increases dramatically — sequential code becomes a state machine; every operation must handle `EAGAIN`; partial reads/writes must be handled explicitly.

---

### 🧪 Thought Experiment

SETUP:
A WebSocket server monitors 1,000 connections. Any of them might send a message at any moment.

WHAT HAPPENS WITH blocking I/O (1 thread per connection):

1. 1,000 threads, each blocking on their connection's `read()`.
2. All 1,000 threads sleeping — zero CPU, but 1 GB of stack memory.
3. When connection #247 sends data, thread #247 wakes up, handles it.
4. Simple to reason about, but 1 GB wasted for idle connections.

WHAT HAPPENS WITH non-blocking I/O (1 thread, O_NONBLOCK):
Without multiplexer: thread spins through all 1,000 connections calling `read()`, getting `EAGAIN` 999 times, 60,000 times per second — CPU at 100% doing nothing useful.

WHAT HAPPENS WITH non-blocking I/O + epoll:

1. Thread calls `epoll_wait()` — blocks until any connection has data.
2. Connection #247 sends data → kernel notifies via epoll event.
3. Thread reads from connection #247 only — others untouched.
4. Back to `epoll_wait()`. CPU idle until events arrive.
5. Memory: 1 thread stack + ~200 bytes state per connection = ~200 KB vs 1 GB.

THE INSIGHT:
Non-blocking I/O + a multiplexer converts the "wait for one" model to a "which of many is ready?" model. This is the foundation of every high-performance server: Nginx, Node.js, Redis, Netty.

---

### 🧠 Mental Model / Analogy

> A restaurant with one experienced waiter who handles 20 tables. Each table's order (I/O) is placed with the kitchen. The waiter doesn't stand at any table waiting — they check each table quickly ("ready?"), skip tables still being cooked (EAGAIN), and attend to tables where food has arrived. `epoll` is the waiter's peripheral vision — telling them exactly which tables need attention without checking all 20.

"Checking each table" → non-blocking `read()` returning `EAGAIN`
"Peripheral vision for ready tables" → `epoll_wait()` event notification
"Table with food ready" → socket with data in receive buffer
"Waiter stands at one table waiting" → blocking I/O model

Where this analogy breaks down: In real event loops, the "waiter" processes one table at a time (single-threaded event loop); with CPU-bound tasks (heavy computation per event), this model stalls. Node.js worker threads address this.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of waiting for data to arrive before your code moves on, non-blocking I/O lets your code ask "is there data?" and if not, immediately move on to check other connections. Your single thread can manage thousands of connections by quickly checking each one.

**Level 2 — How to use it (junior developer):**
In Java, use `java.nio.channels.SocketChannel` with `configureBlocking(false)`. In Node.js, all I/O is non-blocking by default (event loop handles it). In Python, use `asyncio`. Never use raw non-blocking sockets without a multiplexer — always combine with `select`/`epoll`/`kqueue`. Key rule: when you get `EAGAIN` on a write, buffer the remaining data and retry when `epoll` signals write-readiness.

**Level 3 — How it works (mid-level engineer):**
`fcntl(fd, F_SETFL, flags | O_NONBLOCK)` sets the file status flag. In the kernel, the socket's `tcp_recvmsg()` checks `sk->sk_rcvbuf`; if empty and `O_NONBLOCK` is set, it returns `-EAGAIN` immediately without calling `sk_wait_data()`. The application then calls `epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event)` to register interest in `EPOLLIN` events, and `epoll_wait()` to block until any registered fd is ready. Edge-triggered (`EPOLLET`) mode fires once per state change (must read until EAGAIN); level-triggered (default) fires as long as data is available.

**Level 4 — Why it was designed this way (senior/staff):**
The `O_NONBLOCK` flag design predates Linux — it's part of POSIX. The decision to use `EAGAIN` as the "not ready" signal (rather than returning 0) allows the caller to distinguish "no data yet" from "EOF" (which returns 0). `epoll`'s level-triggered default was chosen for correctness — edge-triggered is an optimisation that trades simplicity for performance, and edge-triggered bugs (missing data due to not fully draining a socket) are notoriously hard to debug. Linux `io_uring` supersedes `epoll` for most I/O: it submits and completes I/O asynchronously without any readiness-notification loop — the application never needs to handle `EAGAIN` at all.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│          NON-BLOCKING I/O + epoll FLOW                  │
├─────────────────────────────────────────────────────────┤
│  Setup:                                                 │
│  fd = socket(...); O_NONBLOCK set via fcntl             │
│  epfd = epoll_create1(0)                                │
│  epoll_ctl(epfd, ADD, fd, EPOLLIN)                      │
│                                                         │
│  Event Loop:                                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  events = epoll_wait(epfd, events, 64, -1)       │  │
│  │  // Blocks here until fd(s) are readable         │  │
│  │  for each event:                                 │  │
│  │    n = read(event.fd, buf, sizeof(buf))          │  │
│  │    if (n > 0): process data                      │  │
│  │    if (n == -1 && errno == EAGAIN): done reading │  │
│  │    if (n == 0): connection closed                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Edge-triggered vs Level-triggered:**

- Level-triggered (default): `epoll_wait` returns as long as data is available. Safe but slightly less efficient.
- Edge-triggered (`EPOLLET`): `epoll_wait` returns ONCE when state changes from "not ready" to "ready". Must read until `EAGAIN` to avoid missing data.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[1000 clients connected]
   → [epoll_wait: all idle, no events]
   → [Client #247 sends "GET /"]
   → [epoll returns: fd=247, EPOLLIN ← YOU ARE HERE]
   → [read(247, buf): returns request data]
   → [Process request, write response]
   → [Back to epoll_wait]
```

FAILURE PATH:
[read() returns -1, errno=EAGAIN] → [no data in buffer, must wait for epoll event] → [register EPOLLOUT if write buffer also full] → [retry on next event]

WHAT CHANGES AT SCALE:
At 1M concurrent connections (C1M problem), even epoll has overhead: 1M file descriptors × ~64 bytes kernel state = 64 MB. The main bottleneck shifts from thread memory to the OS scheduler and interrupt coalescing. Kernel bypass (DPDK, io_uring with registered buffers) eliminates the kernel event loop overhead entirely.

---

### 💻 Code Example

Example 1 — Setting O_NONBLOCK and handling EAGAIN:

```c
// BAD: blocking socket — one thread stuck per connection
int fd = socket(AF_INET, SOCK_STREAM, 0);
// read() will block indefinitely

// GOOD: set non-blocking mode
int fd = socket(AF_INET, SOCK_STREAM, 0);
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);

ssize_t n;
do {
    n = read(fd, buf, sizeof(buf));
} while (n == sizeof(buf));  // drain until EAGAIN
if (n == -1 && errno == EAGAIN) {
    // No more data for now — register for epoll
}
```

Example 2 — epoll event loop:

```c
#define MAX_EVENTS 64
int epfd = epoll_create1(0);

struct epoll_event ev;
ev.events = EPOLLIN | EPOLLET;  // edge-triggered
ev.data.fd = listen_fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

struct epoll_event events[MAX_EVENTS];
while (1) {
    int nfds = epoll_wait(epfd, events,
                          MAX_EVENTS, -1);
    for (int i = 0; i < nfds; i++) {
        if (events[i].data.fd == listen_fd) {
            // New connection
            int conn = accept4(listen_fd, NULL,
                               NULL, SOCK_NONBLOCK);
            ev.data.fd = conn;
            epoll_ctl(epfd, EPOLL_CTL_ADD, conn, &ev);
        } else {
            // Data on existing connection
            handle_connection(events[i].data.fd);
        }
    }
}
```

---

### ⚖️ Comparison Table

| Approach                 | Concurrency | Complexity | CPU Use (idle) | Best For                 |
| ------------------------ | ----------- | ---------- | -------------- | ------------------------ |
| **Non-blocking + epoll** | 100K+       | High       | Very low       | High-conn Linux servers  |
| Blocking + threads       | ~10K        | Low        | Low (sleeping) | Simple internal services |
| Non-blocking + select    | ~1K         | Medium     | Low            | Portable POSIX code      |
| Non-blocking + io_uring  | 1M+         | Very high  | Near zero      | Kernel-bypass I/O        |
| Virtual threads (JDK 21) | 100K+       | Low        | Low            | JVM high-concurrency     |

How to choose: Use epoll for high-connection Linux servers (Nginx/Node.js style). Use virtual threads for JVM services needing simplicity + scale. Use io_uring for maximum I/O throughput.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| "Non-blocking means async"                           | Non-blocking means the syscall returns immediately; async means completion is notified later. They're different models |
| "You can set O_NONBLOCK on any fd and it works"      | Regular file I/O is always immediate (page cache); O_NONBLOCK mainly affects sockets and pipes                         |
| "EAGAIN means an error occurred"                     | EAGAIN means "operation would block, try later" — it's a normal status, not an error                                   |
| "Edge-triggered epoll is safer than level-triggered" | Level-triggered is safer (harder to miss events); edge-triggered is faster but requires careful draining               |
| "Node.js uses O_NONBLOCK everywhere"                 | Node.js uses libuv which uses epoll for network sockets; file I/O uses a thread pool (blocking) on Linux               |

---

### 🚨 Failure Modes & Diagnosis

**1. Busy-Poll Loop (Spinning on EAGAIN)**

Symptom: CPU stuck at 100% despite no meaningful work; `strace` shows rapid succession of `read()` → `EAGAIN` cycles.

Root Cause: Non-blocking I/O used without a multiplexer; code retries immediately on `EAGAIN` instead of waiting for readiness notification.

Diagnostic:

```bash
strace -c -p <PID> 2>&1 | sort -k4 -n | tail -10
# If read/EAGAIN dominates: busy-poll loop
```

Fix: Always pair non-blocking fds with `epoll`/`select`; never retry immediately on `EAGAIN`.

Prevention: Code review: every `EAGAIN` path must lead to event registration, not a retry loop.

---

**2. Edge-Triggered Event Miss (Lost Data)**

Symptom: Connection appears to hang; server received partial request; no further events from `epoll_wait`.

Root Cause: Using `EPOLLET` (edge-triggered) but not draining the socket buffer completely; `epoll_wait` only fires once per state transition — if you didn't read all available data, no new event fires.

Diagnostic:

```bash
# Check socket receive buffer fill
ss -tnp | grep <port>
# Recv-Q > 0 while no read happening = missed edge trigger
```

Fix: In edge-triggered mode, loop on `read()` until `EAGAIN`:

```c
while ((n = read(fd, buf, sizeof(buf))) > 0) {
    process(buf, n);
}
// Only exit loop on EAGAIN (not error)
```

Prevention: Default to level-triggered (`EPOLLIN`) unless profiling proves edge-triggered is necessary.

---

**3. Partial Write Not Handled**

Symptom: Response truncated; client receives incomplete data; no error on the server side.

Root Cause: `write()` on a non-blocking socket may write fewer bytes than requested if the send buffer is full; code doesn't loop on partial writes.

Diagnostic:

```bash
# Monitor send buffer fullness
ss -tn | grep <port>  # Send-Q > 0 = partial writes possible
```

Fix:

```c
// BAD: assumes all bytes written
write(fd, response, len);

// GOOD: loop on partial writes
size_t sent = 0;
while (sent < len) {
    ssize_t n = write(fd, response + sent,
                      len - sent);
    if (n == -1 && errno == EAGAIN) {
        // Register EPOLLOUT, retry on event
        break;
    }
    sent += n;
}
```

Prevention: Use a write-buffer abstraction that handles partial writes automatically; test with artificially small socket send buffers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Blocking I/O` — the model non-blocking I/O replaces; contrast is essential
- `File Descriptor` — non-blocking mode is set per file descriptor
- `System Call (syscall)` — non-blocking changes syscall return semantics

**Builds On This (learn these next):**

- `epoll / kqueue / io_uring` — the readiness-notification mechanisms that make non-blocking I/O practical
- `Async I/O` — the next evolution: completion notification rather than readiness notification
- `Reactive Programming` — the programming model built on non-blocking, event-driven I/O

**Alternatives / Comparisons:**

- `Blocking I/O` — simpler code, one thread per connection, doesn't scale beyond ~10K connections
- `Async I/O (io_uring)` — no EAGAIN handling needed; kernel completes I/O and notifies
- `Virtual Threads (JDK 21)` — blocking I/O semantics with non-blocking scalability in the JVM

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ I/O mode where syscalls return EAGAIN     │
│              │ instead of sleeping when not ready        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Blocking I/O requires one thread per      │
│ SOLVES       │ connection — can't scale to 100K+         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Non-blocking alone is useless — must      │
│              │ combine with epoll for efficiency         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High-concurrency servers with many        │
│              │ simultaneous idle connections             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Low concurrency (< 500 conns); use        │
│              │ blocking I/O for simplicity               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Thread efficiency vs code complexity      │
│              │ (state machines instead of sequential)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check if ready, skip if not, never       │
│              │  sit and wait"                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ epoll → io_uring → Async I/O              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Node.js uses a single-threaded event loop with non-blocking I/O for networking, but a thread pool (via libuv) for file system operations — even though the kernel supports `O_NONBLOCK` on file descriptors. Why doesn't Node.js use non-blocking I/O for file operations, and what fundamental difference between network sockets and regular files makes `O_NONBLOCK` on files ineffective in practice?

**Q2.** An edge-triggered epoll server handles 50,000 connections. During a traffic spike, 5,000 connections all become readable simultaneously. The event loop processes them sequentially. What is the precise latency experienced by the last connection to be handled, and how does this compare to a thread-per-connection model where all 5,000 threads wake up simultaneously? What architectural pattern addresses this head-of-line blocking in event loops?
