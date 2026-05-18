---
id: NET-057
title: "epoll and io_uring (Network I/O Models)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-020, NET-029, NET-056
used_by: NET-058, NET-060
related: NET-029, NET-056, NET-058
tags:
  - networking
  - epoll
  - io-uring
  - async-io
  - linux-kernel
  - performance
  - event-loop
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/net/epoll-and-io-uring/
---

**⚡ TL;DR** - epoll is the Linux kernel mechanism for
monitoring thousands of file descriptors simultaneously
with O(1) event notification. It is the foundation of
every high-performance event loop: Node.js, nginx,
Redis, Netty. io_uring (Linux 5.1+) goes further:
zero-copy I/O with a shared ring buffer between kernel
and userspace, enabling submitting thousands of I/O
operations without system call overhead. The progression:
select (O(n)) → poll (O(n)) → epoll (O(1) ready events) →
io_uring (batch async, near-zero syscall overhead).

| #057 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Deep Dive (NET-020), Socket Programming (NET-029), Nagle's Algorithm (NET-056) | |
| **Used by:** | eBPF for Networking (NET-058), Anycast Routing (NET-060) | |
| **Related:** | Socket Programming, Nagle's Algorithm, eBPF for Networking | |

---

### 🔥 The Problem This Solves

A server handles 10,000 concurrent connections.
Polling model: for each connection, call `poll()` or
`select()` with all 10,000 file descriptors. Kernel
checks all 10,000 on every call. CPU usage: O(n²) at
high connection count. epoll: register once, kernel tells
you only which FDs are ready. CPU: O(1) per event. This
is why nginx handles 50,000+ concurrent connections where
Apache (thread-per-connection) tops out at ~1,000.

---

### 🧠 Intuition: Don't Check - Be Notified

```
Bad model (select/poll):
  "Are you ready? Are you ready? Are you ready?"
  Ask every connection on every iteration
  Even if 9,999 are idle, you still check all 9,999

epoll model:
  "Let me know when you're ready."
  Register interest with kernel once
  Kernel puts ready FDs in a list
  You get: only the ready ones, instantly
  
  Like: a waiter asking every table every 30 seconds
  "Is your food ready? Is your food ready?"
  vs: kitchen calls waiter only when plate is ready

io_uring model (next level):
  "Here are 1,000 operations I want done."
  Submit all to kernel at once (one syscall)
  Kernel processes asynchronously
  You check completion queue for results
  
  Like: submitting a restaurant order for the whole week
  and picking up completed orders as they're done
```

---

### ⚙️ select and poll: Why They Don't Scale

```c
// select() - classic POSIX, terrible at scale
#include <sys/select.h>

fd_set readfds;
FD_ZERO(&readfds);
FD_SET(fd1, &readfds);
FD_SET(fd2, &readfds);
// ... add all 10,000 FDs

// Every call: kernel scans ALL file descriptors
// Returns: which ones are ready
int ready = select(max_fd + 1, &readfds, NULL, NULL, NULL);

// Problems:
// 1. O(n) per call - scan all FDs every time
// 2. FD_SETSIZE limit: usually 1024 (hardcoded!)
// 3. After each select(), must rebuild FD_SET from scratch
// 4. Returned set is modified: must reset before next call

// poll() - same concept, no FD_SETSIZE limit
#include <poll.h>

struct pollfd fds[10000];
fds[0].fd = fd1; fds[0].events = POLLIN;
// ... fill all 10,000

// Every call: kernel still scans ALL file descriptors
int ready = poll(fds, 10000, -1);
// After call: check each fds[i].revents manually
// O(n) per call - no improvement over select at scale
```

---

### ⚙️ epoll: The Right Way

```c
#include <sys/epoll.h>

// 1. Create epoll instance (one per event loop)
int epfd = epoll_create1(0);

// 2. Register file descriptors (done ONCE per FD)
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLET;  // ET = edge-triggered
ev.data.fd = client_fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);
// O(1) per registration

// 3. Wait for events (replaces poll loop)
struct epoll_event events[64];
int nready = epoll_wait(epfd, events, 64, -1);
// Returns ONLY ready FDs (events array filled)
// O(1) for notification: kernel maintains ready list

// 4. Process only ready events
for (int i = 0; i < nready; i++) {
    int fd = events[i].data.fd;
    if (events[i].events & EPOLLIN) {
        // This FD has data to read
        handle_read(fd);
    }
}
// O(k) where k = number of ready events
// 10,000 connections, 5 active: processes 5, ignores 9,995

// Key options:
// EPOLLIN:  readable (data available)
// EPOLLOUT: writable (send buffer has space)
// EPOLLET:  edge-triggered (notify on state change, not level)
// EPOLLONESHOT: notify once, then remove
```

---

### ⚙️ Level-Triggered vs Edge-Triggered

```
Level-Triggered (LT) - default:
  "Notify me AS LONG AS this FD is in the ready state"
  If data in buffer and you don't read all of it:
  → Next epoll_wait() will notify AGAIN
  Simpler: works like poll/select
  Risk: if you miss it, you're notified again

Edge-Triggered (ET) - EPOLLET flag:
  "Notify me when state CHANGES from not-ready to ready"
  FD becomes readable → ONE notification
  If you don't read all data: NO further notification
  Must: read until EAGAIN/EWOULDBLOCK (drain completely)
  Higher performance (fewer kernel wakeups)
  Higher complexity (must handle partial reads)

ET example (read loop):
  while (true) {
      ssize_t n = read(fd, buf, sizeof(buf));
      if (n == -1 && errno == EAGAIN) break; // all read
      if (n <= 0) { handle_close(fd); break; }
      process(buf, n);
  }
  // Must loop until EAGAIN - no re-notification in ET mode

LT is safer for most applications.
ET is used in performance-critical paths (nginx, Redis).
```

---

### ⚙️ io_uring: Zero-Copy Async I/O

```c
#include <liburing.h>

// io_uring: shared memory ring buffer between kernel/userspace
// Submission Queue (SQ): app writes I/O requests here
// Completion Queue (CQ): kernel writes results here
// No system call needed per operation!

struct io_uring ring;
io_uring_queue_init(256, &ring, 0);  // 256-entry queue

// Submit multiple read operations in one syscall:
for (int i = 0; i < 100; i++) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    io_uring_prep_read(sqe, fds[i], bufs[i], BUF_SIZE, 0);
    sqe->user_data = i;  // tag to identify completion
}
// Submit ALL 100 operations with ONE syscall:
io_uring_submit(&ring);

// ... do other work ...

// Collect completions:
struct io_uring_cqe *cqe;
int completed = io_uring_peek_batch_cqe(&ring, &cqe_arr, 100);
for (int i = 0; i < completed; i++) {
    int idx = cqe_arr[i]->user_data;
    int result = cqe_arr[i]->res;  // bytes read
    process(bufs[idx], result);
    io_uring_cqe_seen(&ring, cqe_arr[i]);
}

// For 1,000 operations:
// Traditional: 1,000 syscalls (read × 1000)
// io_uring: 1 submit syscall + 0 per completion (polling mode)
// Speedup: 2-4x for I/O-heavy workloads (measured)
```

---

### ⚙️ Event Loop Architecture Using epoll

```python
# Simplified event loop using Python's select module
# (which wraps epoll on Linux via selectors.EpollSelector)
import selectors
import socket

sel = selectors.DefaultSelector()  # uses epoll on Linux

def accept(sock, mask):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1000)
    if data:
        conn.sendall(data)  # echo
    else:
        sel.unregister(conn)
        conn.close()

sock = socket.socket()
sock.bind(("localhost", 9999))
sock.listen()
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

# Event loop:
while True:
    events = sel.select()  # epoll_wait() under the hood
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)

# This handles THOUSANDS of connections with ONE thread
# Node.js, Redis, nginx work exactly this way
# But: no CPU parallelism without multiple processes/threads
```

---

### ⚙️ Wrong vs Right: Blocking I/O in Event Loop

```python
# BAD: blocking I/O in an event loop callback
import selectors
import requests  # blocking HTTP library

sel = selectors.DefaultSelector()

def handle_request(conn, mask):
    data = conn.recv(1024)
    # THIS IS BLOCKING: entire event loop stalls
    # while waiting for external HTTP response
    result = requests.get("http://external-api.com/data")
    conn.sendall(result.content)
    # During this blocking call: NO other connections
    # can be handled. All 10,000 clients wait.

# GOOD: use async I/O library (don't block event loop)
# Option 1: Python asyncio (cooperative multitasking)
import asyncio
import aiohttp

async def handle_request(reader, writer):
    data = await reader.read(1024)  # non-blocking read
    async with aiohttp.ClientSession() as session:
        async with session.get("http://external-api.com/data") as r:
            result = await r.read()  # non-blocking
    writer.write(result)
    await writer.drain()

# asyncio.start_server() uses epoll internally
# One event loop, one thread, handles many connections
# "Blocking" calls yield control to event loop (await)

# Option 2: run blocking work in thread pool
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

async def handle_with_blocking():
    # Move blocking calls to thread pool
    result = await asyncio.get_event_loop().run_in_executor(
        executor, blocking_function
    )
    return result
```

---

### 📐 Scale Considerations

```
Connection count vs I/O model performance:

select:
  10 connections: fine
  100 connections: starting to slow
  10,000 connections: ~100ms per select() call
  Max: 1,024 FDs (FD_SETSIZE)

poll:
  1,000 connections: reasonable
  10,000 connections: 10ms per poll() call
  100,000 connections: unusable
  No FD limit, but O(n) kernel scan

epoll:
  1,000 connections: <0.1ms per wait
  100,000 connections: still <0.1ms per wait (only ready FDs)
  Max: system file descriptor limit (ulimit -n)
  Linux default: 1,024 per process (increase: ulimit -n 65536)

io_uring:
  Best for: disk I/O (files), network at high operation rate
  Network: reduces syscall overhead for batch operations
  Used by: RocksDB, some game servers, storage engines
  Not yet in mainstream network servers (epoll still dominant)

The C10K problem (10,000 concurrent connections):
  - Thread-per-connection: 10,000 × 8MB stack = 80GB
  - Thread pool + select: O(n) kernel overhead per wakeup
  - epoll + event loop: O(1), handles C10K trivially
  - C1M (1 million): needs tuning (sysctl, ulimits, ports)
```

---

### 🧭 Decision Guide

```
Which I/O model to use:

select/poll:
  NEVER for production network servers
  Acceptable: simple scripts, test code, < 10 connections
  
epoll (directly):
  When: writing a high-performance C/C++/Rust server
  Libraries: libevent, libuv (Node.js), boost.asio, tokio

epoll (via framework):
  Java/Kotlin: Netty, Vert.x, Project Reactor
  Python: asyncio (built-in since 3.4)
  Node.js: built-in (everything is epoll-based)
  Rust: tokio (epoll on Linux, kqueue on macOS)
  Go: Go runtime manages goroutines on OS threads with epoll

io_uring:
  When: you need maximum disk I/O performance
  Available: Linux 5.1+ (check: uname -r)
  Libraries: liburing, Rust's tokio-uring
  Not yet: wide adoption in network-facing servers (2024)

Thread-per-connection:
  Acceptable: connection count < 1,000
  Java: old-style Java servers (Tomcat blocking mode)
  
When frameworks handle it for you:
  Nginx: epoll (event-driven, one worker per CPU core)
  Node.js: epoll via libuv (single-threaded event loop)
  Redis: epoll (single-threaded event loop)
  Netty: epoll or NIO (NioEventLoop)
  → Most developers don't touch epoll directly
  → Choose the right framework and model
```
