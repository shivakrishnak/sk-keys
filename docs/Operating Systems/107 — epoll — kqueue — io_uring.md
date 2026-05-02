---
layout: default
title: "epoll / kqueue / io_uring"
parent: "Operating Systems"
nav_order: 107
permalink: /operating-systems/epoll-kqueue-io-uring/
number: "0107"
category: Operating Systems
difficulty: ★★★
depends_on: Non-Blocking I/O, File Descriptor, System Call (syscall)
used_by: Async I/O, Reactive Programming, Node.js, Netty
related: Async I/O, Non-Blocking I/O, select / poll
tags:
  - os
  - networking
  - internals
  - performance
  - deep-dive
---

# 107 — epoll / kqueue / io_uring

⚡ TL;DR — epoll/kqueue/io_uring are OS interfaces that efficiently tell you which of thousands of I/O descriptors are ready — the engine powering every high-performance server.

| #0107           | Category: Operating Systems                              | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Non-Blocking I/O, File Descriptor, System Call (syscall) |                 |
| **Used by:**    | Async I/O, Reactive Programming, Node.js, Netty          |                 |
| **Related:**    | Async I/O, Non-Blocking I/O, select / poll               |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
The original Unix `select()` call accepts a set of file descriptors and tells you which are ready for I/O. But it has a hard limit (FD_SETSIZE = 1024 on most systems), iterates through every descriptor on every call (O(n) in the number of descriptors), and the descriptor set must be rebuilt from scratch on each call. At 10,000 connections, every `select()` call scans all 10,000 descriptors even if only 1 is ready.

THE BREAKING POINT:
In 1999, the "C10K problem" paper showed that web servers needed to handle 10,000 concurrent connections. With `select()`, the O(n) scan meant the server spent most of its time checking connections that had nothing to do, not serving requests. `poll()` fixed the FD_SETSIZE limit but kept the O(n) scan.

THE INVENTION MOMENT:
This is exactly why epoll (Linux), kqueue (BSD/macOS), and io_uring (Linux 5.1+) were created — O(1) notification of ready descriptors, no per-call scan, no descriptor set rebuilding.

---

### 📘 Textbook Definition

**epoll** (Linux), **kqueue** (BSD/macOS/iOS), and **io_uring** (Linux 5.1+) are OS-level I/O event notification mechanisms that allow a single thread to monitor thousands of file descriptors efficiently. They maintain an internal interest list (descriptors registered by the application) and a ready list (descriptors with pending events). The application blocks on a single syscall (`epoll_wait`, `kevent`, or `io_uring_enter`) which returns only when one or more registered descriptors are ready — in O(1) or O(events) time. `io_uring` extends this to support asynchronous I/O submission and completion via shared ring buffers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
epoll/kqueue registers interest once and notifies you exactly when something is ready — no repeated scanning.

**One analogy:**

> Old approach (`select`): every hour, call each of your 10,000 employees to ask "do you have work for me?" epoll: give each employee a buzzer. They press it when they have something. You sit waiting; the buzzers tell you who needs attention. You go directly to that person — you never scan the others.

**One insight:**
The key innovation is that registration and waiting are separated. You register once (`epoll_ctl ADD`), then wait many times (`epoll_wait`). The kernel maintains the ready list internally — you only pay for events that actually occurred, not for the total number of monitored descriptors.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Registration is O(1): adding an fd to the watch set is done once, not per-wait.
2. Wait is O(ready events), not O(monitored fds): you pay only for what happened.
3. The kernel maintains state: it knows which descriptors have data without polling them.

DERIVED DESIGN:
epoll uses a red-black tree to store registered fds (O(log n) insertion/deletion) and a doubly-linked list for ready fds. When data arrives on a socket (network interrupt → TCP stack), the kernel adds the socket's epoll entry to the ready list. `epoll_wait` copies events from the ready list to user space and returns — O(ready events). The entire architecture shifts work from user space (scan all fds) to kernel space (add to ready list on event).

THE TRADE-OFFS:
Gain: O(events) wait time; handles hundreds of thousands of connections with minimal CPU; kernel maintains registration state.
Cost: epoll is Linux-specific (kqueue for BSD/macOS); io_uring has a large attack surface with a history of CVEs; the event-loop programming model is harder to reason about than blocking I/O; edge-triggered epoll bugs are subtle.

---

### 🧪 Thought Experiment

SETUP:
A server monitors 100,000 connections. At any moment, 100 connections have incoming data.

WHAT HAPPENS WITH select():

1. Build a bitmap of 100,000 fds (12.5 KB).
2. `select()` copies bitmap to kernel, scans all 100,000 fds.
3. Returns with 100 fds marked ready.
4. User code scans all 100,000 bits to find the 100 ready ones.
5. 200,000 operations per event batch — 99.9% wasted work.

WHAT HAPPENS WITH epoll:

1. 100,000 fds pre-registered with `epoll_ctl(EPOLL_CTL_ADD)`.
2. `epoll_wait()` returns with exactly 100 events.
3. User code processes 100 events directly.
4. 100 operations per event batch — zero wasted work.
5. As connections increase from 100K to 1M, wait time stays proportional to ready events (100), not total connections.

THE INSIGHT:
The performance difference between `select` and `epoll` is not about speed — it's about algorithmic complexity. select is O(max_fd); epoll is O(ready_events). At scale, these are incomparably different.

---

### 🧠 Mental Model / Analogy

> epoll is like a hotel front desk with call lights (one per room). Instead of the concierge calling every 1,000 rooms to ask "do you need anything?", each room presses a button when they need service. The concierge waits at the desk — when a light appears, they go to that room. Registration = install the call button. epoll_wait = wait at the desk. Ready event = a light turns on.

"Call button installed" → `epoll_ctl(EPOLL_CTL_ADD, fd, EPOLLIN)`
"Concierge waiting at desk" → `epoll_wait()`
"Light turns on" → data arrives on socket, kernel adds to ready list
"Concierge services room" → `read()` on the ready fd

Where this analogy breaks down: io_uring goes further — the concierge doesn't need to wait at the desk at all; they submit a list of tasks and get notified when each is done, even while doing other work.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of checking every connection to see if it has data (slow), epoll lets you register all connections once, then the OS tells you exactly which ones have data. You only work on connections that actually need attention.

**Level 2 — How to use it (junior developer):**
In Java, `java.nio.Selector` wraps OS-specific mechanisms (epoll on Linux, kqueue on macOS). In Node.js, libuv uses epoll/kqueue internally for all network I/O. In C, create with `epoll_create1(0)`, add fds with `epoll_ctl()`, wait with `epoll_wait()`. io_uring requires the `liburing` library. Netty, Nginx, Redis, and Node.js all use epoll/kqueue under the hood.

**Level 3 — How it works (mid-level engineer):**
`epoll_create1()` returns a file descriptor representing an epoll instance. `epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event)` inserts `fd` into the epoll's red-black tree (O(log n)). The kernel's socket layer calls `ep_poll_callback()` when data arrives, adding the fd to the ready list. `epoll_wait(epfd, events, maxevents, timeout)` sleeps until the ready list is non-empty, then copies up to `maxevents` entries to user space. Level-triggered (default): fd stays in ready list as long as data is available. Edge-triggered (`EPOLLET`): fd removed from ready list on return; re-added only on next state transition.

**Level 4 — Why it was designed this way (senior/staff):**
The separation of `epoll_ctl` (register) from `epoll_wait` (wait) was a deliberate design choice to amortise registration cost. `select`/`poll` re-register on every wait, making them O(n) per call. epoll's registration is persistent, making `epoll_wait` O(ready_events). The level/edge-triggered duality was included because level-triggered is safe (impossible to miss events) while edge-triggered is more efficient (fires only on change). io_uring (2019) supersedes epoll for many use cases: rather than "which fds are ready to do I/O?", io_uring asks "here are 1000 I/O operations — do them and tell me when each is done." This proactor vs reactor distinction is fundamental. io_uring's shared ring buffer design was inspired by SPDK and DPDK's userspace driver ring buffers.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│                 epoll ARCHITECTURE                      │
├─────────────────────────────────────────────────────────┤
│  User Space                                             │
│  epoll_ctl(ADD, sock1, EPOLLIN) ───→ Red-Black Tree     │
│  epoll_ctl(ADD, sock2, EPOLLIN) ───→ [sock1][sock2]...  │
│                                                         │
│  epoll_wait()   ←─── Kernel Ready List                  │
│    blocks here         ↑ [sock3] ← data arrived        │
│    returns 1 event                                      │
│                                                         │
│  Kernel:                                                │
│  NIC interrupt → TCP stack → sk_data_ready(sock3)       │
│               → ep_poll_callback() → ready list push   │
│               → epoll_wait() unblocked                  │
└─────────────────────────────────────────────────────────┘
```

**io_uring flow:**

```
┌─────────────────────────────────────────────────────────┐
│               io_uring RING BUFFER DESIGN               │
├─────────────────────────────────────────────────────────┤
│  User space writes SQEs (operations) to SQ ring         │
│  Kernel reads SQEs, executes I/O                        │
│  Kernel writes CQEs (results) to CQ ring                │
│  User space reads CQEs (completions)                    │
│  No per-operation syscall needed with SQPOLL mode       │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[10,000 connections registered with epoll_ctl]
   → [epoll_wait() — thread sleeps ← YOU ARE HERE]
   → [Packets arrive on 50 connections]
   → [Kernel: ready list fills with 50 entries]
   → [epoll_wait returns: 50 events]
   → [Thread: read() on each of 50 ready fds]
   → [Process requests, send responses]
   → [Loop back to epoll_wait()]
```

FAILURE PATH:
[fd closed while in epoll interest set] → [EPOLLHUP/EPOLLERR events on next epoll_wait] → [must remove fd with EPOLL_CTL_DEL]

WHAT CHANGES AT SCALE:
At 1M connections (C1M), epoll ready list processing itself becomes a bottleneck. nginx uses a multi-worker model (one process per CPU core, each with its own epoll) to parallelise. io_uring's ring buffer approach avoids any per-event syscall overhead, enabling single-thread throughput beyond 1M I/O ops/sec on NVMe.

---

### 💻 Code Example

Example 1 — epoll server loop:

```c
int epfd = epoll_create1(EPOLL_CLOEXEC);

// Register listening socket
struct epoll_event ev = {.events = EPOLLIN,
                          .data.fd = listen_fd};
epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

#define MAX_EVENTS 128
struct epoll_event events[MAX_EVENTS];

while (1) {
    // Blocks until events arrive — O(ready_events)
    int n = epoll_wait(epfd, events, MAX_EVENTS, -1);
    for (int i = 0; i < n; i++) {
        int fd = events[i].data.fd;
        if (fd == listen_fd) {
            // New connection
            int conn = accept4(listen_fd, NULL, NULL,
                               SOCK_NONBLOCK|SOCK_CLOEXEC);
            ev.events = EPOLLIN | EPOLLET;
            ev.data.fd = conn;
            epoll_ctl(epfd, EPOLL_CTL_ADD, conn, &ev);
        } else {
            handle_data(fd);  // read until EAGAIN
        }
    }
}
```

Example 2 — Java NIO Selector (wraps epoll/kqueue):

```java
// BAD: blocking accept — one thread per connection
ServerSocket ss = new ServerSocket(8080);
while (true) {
    Socket s = ss.accept();  // blocks
    new Thread(() -> handle(s)).start();
}

// GOOD: NIO Selector — one thread, many connections
Selector selector = Selector.open();
ServerSocketChannel ssc = ServerSocketChannel.open();
ssc.configureBlocking(false);
ssc.bind(new InetSocketAddress(8080));
ssc.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select();  // epoll_wait internally
    for (SelectionKey key : selector.selectedKeys()) {
        if (key.isAcceptable()) {
            SocketChannel sc = ssc.accept();
            sc.configureBlocking(false);
            sc.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            handle((SocketChannel) key.channel());
        }
    }
    selector.selectedKeys().clear();
}
```

Example 3 — io_uring batch reads:

```c
struct io_uring ring;
io_uring_queue_init(256, &ring, 0);

// Submit 100 read operations at once
for (int i = 0; i < 100; i++) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    io_uring_prep_read(sqe, fds[i], bufs[i], 4096, 0);
    io_uring_sqe_set_data(sqe, (void*)(uintptr_t)i);
}
io_uring_submit(&ring);  // ONE syscall for 100 reads

// Harvest completions
struct io_uring_cqe *cqe;
while (io_uring_peek_cqe(&ring, &cqe) == 0) {
    int idx = (int)(uintptr_t)io_uring_cqe_get_data(cqe);
    process_result(bufs[idx], cqe->res);
    io_uring_cqe_seen(&ring, cqe);
}
```

---

### ⚖️ Comparison Table

| Mechanism    | Max FDs   | Complexity | Platform   | Best For                |
| ------------ | --------- | ---------- | ---------- | ----------------------- |
| select       | 1,024     | O(max_fd)  | POSIX      | Legacy, portability     |
| poll         | Unlimited | O(n)       | POSIX      | Portable, small fd sets |
| **epoll**    | Millions  | O(events)  | Linux      | High-conn Linux servers |
| kqueue       | Millions  | O(events)  | BSD/macOS  | High-conn macOS/BSD     |
| **io_uring** | Millions  | O(events)  | Linux 5.1+ | Max I/O throughput      |

How to choose: Use epoll for any Linux server with > 1,000 concurrent connections. Use kqueue on macOS/BSD. Use io_uring for I/O-intensive workloads (databases, storage) needing maximum throughput. Use Java NIO Selector or Netty for JVM portability.

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                             |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| "epoll is faster than select on small fd sets"  | For < 100 fds, select/poll can be faster due to simpler setup; epoll's advantage is at scale                        |
| "io_uring replaces epoll completely"            | io_uring targets I/O completion; epoll targets readiness notification — they solve related but different problems   |
| "epoll is thread-safe"                          | epoll_wait on a shared epfd from multiple threads can cause double-delivery; use one epfd per thread                |
| "EPOLLET is always better than level-triggered" | Edge-triggered is faster but any bug that misses a drain causes the connection to permanently stop receiving events |
| "io_uring works in all container environments"  | io_uring is restricted/disabled in many container security profiles due to CVEs                                     |

---

### 🚨 Failure Modes & Diagnosis

**1. Missed Edge-Triggered Events (Stalled Connection)**

Symptom: Connection stops receiving data after a burst; no error; client appears hung.

Root Cause: `EPOLLET` used but socket not fully drained (read until `EAGAIN` not implemented); edge fires only on state change — if data remains but no new data arrives, no further events fire.

Diagnostic:

```bash
ss -tn | grep <port>
# Non-zero Recv-Q on a connection that appears idle = missed drain
```

Fix: Always read until `EAGAIN` in edge-triggered mode; re-register with `EPOLL_CTL_MOD` if needed.

Prevention: Default to level-triggered; only use `EPOLLET` with rigorous drain loops verified by testing.

---

**2. EPOLLHUP Not Handled (FD Leak)**

Symptom: epoll_wait returns events with `EPOLLHUP` or `EPOLLERR` that aren't handled; fd stays in interest set forever; eventually exhausts fd limit.

Root Cause: Connection closed by peer triggers `EPOLLHUP`; code only handles `EPOLLIN` and ignores error events.

Diagnostic:

```bash
ls /proc/<PID>/fd | wc -l  # growing fd count
cat /proc/<PID>/fdinfo/<fd>  # check epoll registered fds
```

Fix:

```c
if (events[i].events & (EPOLLHUP | EPOLLERR)) {
    epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL);
    close(fd);
    continue;
}
```

Prevention: Always check for EPOLLHUP/EPOLLERR in the event loop alongside EPOLLIN.

---

**3. io_uring CVE / Security Restriction**

Symptom: Application using io_uring works locally but fails in Kubernetes/Docker with `EPERM` or `ENOSYS`.

Root Cause: Container security profile restricts `io_uring_setup` syscall (default in many container runtimes since io_uring CVEs in 2022–2023).

Diagnostic:

```bash
# Check if io_uring is available
python3 -c "import socket; \
    import ctypes; \
    print(ctypes.CDLL(None).syscall(425, 0,0,0))"
# -1 with errno=EPERM = restricted
```

Fix: In seccomp profile, explicitly allow `io_uring_setup`, `io_uring_enter`, `io_uring_register`. Or fall back to epoll when io_uring is unavailable.

Prevention: Design I/O layer to detect capability and fall back: try io_uring, fall back to epoll if EPERM.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Non-Blocking I/O` — epoll/kqueue are the readiness notification layer on top of O_NONBLOCK
- `File Descriptor` — the unit that is registered with epoll/kqueue
- `System Call (syscall)` — epoll_wait/kevent are syscalls; io_uring minimises them

**Builds On This (learn these next):**

- `Async I/O` — io_uring extends the model from readiness to completion
- `Reactive Programming` — the application-level pattern built on epoll event loops
- `Node.js` — uses libuv which wraps epoll/kqueue for all network I/O

**Alternatives / Comparisons:**

- `select / poll` — POSIX alternatives; portable but O(n) at scale
- `IOCP (Windows)` — Windows' completion-port mechanism, analogous to io_uring
- `DPDK` — kernel bypass that eliminates even epoll overhead for packet processing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ OS mechanism: register fd set once,       │
│              │ get notified O(events) when data is ready │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ select/poll scan all fds O(n) per call;   │
│ SOLVES       │ epoll fires only on actual events         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Registration is persistent; you pay per   │
│              │ event, not per monitored descriptor       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ > 1,000 concurrent connections; any       │
│              │ high-performance network server           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ io_uring for disk I/O; use kqueue on      │
│              │ macOS; io_uring blocked in containers     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(events) efficiency vs Linux-specific    │
│              │ API (need kqueue for portability)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Register once, be notified exactly when  │
│              │  something happens — never scan"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ io_uring → Async I/O → Reactor Pattern    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Nginx uses multiple worker processes (one per CPU core), each with its own epoll instance. When a new TCP connection arrives, the kernel delivers the `accept()` event to one worker — but which one? If all workers are `epoll_wait()`-ing on the same listening socket, the kernel may wake all of them (the "thundering herd" problem). What Linux kernel feature solves this, and how does it change the semantics of `accept()` for multiple epoll instances watching the same fd?

**Q2.** io_uring's `IORING_OP_SPLICE` operation can chain I/O operations: read from socket, transform data, write to socket — all without data touching user space. Design a file server using `IORING_OP_SPLICE` chaining to serve static files with zero user-space copies. What are the precise conditions under which the zero-copy guarantee holds, and when would the kernel be forced to create a copy anyway?
