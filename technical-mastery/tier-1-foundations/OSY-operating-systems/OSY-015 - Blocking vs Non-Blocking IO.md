---
id: OSY-015
title: Blocking vs Non-Blocking I/O
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-008, OSY-006
used_by: OSY-037, OSY-068
related: OSY-037, OSY-068, OSY-096
tags:
  - foundational
  - io-model
  - blocking
  - non-blocking
  - async
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/osy/blocking-nonblocking-io/
---

## TL;DR

Blocking I/O suspends the calling thread until data is
ready. Non-blocking I/O returns immediately with EAGAIN
if data isn't ready. Asynchronous I/O notifies the caller
when data is ready. The choice determines thread count,
latency, and throughput.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-015 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | I/O model, blocking, non-blocking, async |
| **Prerequisites** | OSY-008, OSY-006 |

---

### The Three I/O Models

```
BLOCKING I/O (default):
  Thread calls read() -> thread suspends -> data arrives
  -> thread resumes -> read() returns
  
  Thread state during wait: BLOCKED (not using CPU)
  Implication: need 1 thread per concurrent I/O operation
  Java default: InputStream.read(), Socket.getInputStream()

NON-BLOCKING I/O:
  Thread calls read() -> if no data: EAGAIN returned instantly
  Thread can do other work -> loop back to try again
  
  Thread state: always RUNNING (busy poll loop)
  Problem: CPU burns 100% checking "is data ready yet?"
  Use case: combined with epoll (select read when ready)

ASYNCHRONOUS I/O (async):
  Thread registers callback -> kernel does I/O -> kernel
  calls callback when done
  
  Thread state: can do other work while I/O completes
  Java: CompletableFuture, WebFlux, NIO AsynchronousChannel
  OS: io_uring (Linux), IOCP (Windows)
```

---

### I/O Model Comparison

| Model | Thread blocks? | CPU during wait | Use case |
|-------|---------------|-----------------|---------|
| Blocking | Yes | No (thread sleeps) | Simple, few connections |
| Non-blocking + poll | No | Yes (busy loop) | Low-latency trading (rare) |
| Non-blocking + epoll | No | No (sleeps in epoll) | High-connection servers |
| Async (io_uring) | No | No | Highest throughput |

---

### Why This Matters for Java

```java
// BLOCKING (traditional):
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket conn = server.accept();    // blocks
    new Thread(() -> handle(conn)).start(); // 1 thread per conn
}
// Problem: 10,000 connections = 10,000 threads = ~10GB stack
//          + 10,000 context switches per request

// NON-BLOCKING + epoll (Netty, NIO under the hood):
Selector selector = Selector.open();
serverChannel.register(selector, SelectionKey.OP_ACCEPT);
while (true) {
    selector.select();  // blocks until any FD is ready
    // Handle only the ready connections (1-2 threads total)
    // Internally: OS epoll_wait() - efficient event notification
}
// 10,000 connections, 1-2 event loop threads
// Much less memory, much fewer context switches

// ASYNC (Java 21 Virtual Threads - best of both worlds):
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> handle(conn));  // looks blocking
    // Internally: virtual thread parks during I/O
    // OS thread is not blocked - handles other virtual threads
}
```

---

### Textbook Definition

Blocking I/O suspends the calling thread in the OS
BLOCKED state until the I/O operation completes. Non-
blocking I/O returns immediately with EAGAIN/EWOULDBLOCK
if data is not ready. Asynchronous I/O initiates an
operation and returns; the kernel notifies the caller
via callback, signal, or completion queue when done.

---

### Understand It in 30 Seconds

Blocking = waiting at the post office counter until
your package arrives. Non-blocking = checking the
counter, finding nothing, going home, checking again
later. Async = leaving your phone number; they call
you when the package arrives.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Non-blocking is always faster than blocking" | Non-blocking without event notification (busy polling) wastes CPU. Non-blocking + epoll is faster for high-concurrency. For low-concurrency (< 100 connections), blocking is simpler and often as fast |
| "Virtual threads (Java 21) are async I/O" | Virtual threads use cooperative scheduling with blocking system calls. When a virtual thread blocks on I/O, the JVM unparks the OS thread to serve another virtual thread. It looks like blocking, works like async |

---

### Mastery Checklist

- [ ] Can explain the 3 I/O models with a concrete analogy
- [ ] Knows why blocking I/O requires 1 thread per connection
- [ ] Understands epoll as efficient non-blocking event notification
- [ ] Knows where Java 21 virtual threads fit in this model
