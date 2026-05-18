---
id: OSY-037
title: Blocking vs Non-Blocking vs Asynchronous IO
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-015, OSY-034
used_by: OSY-042, OSY-068, OSY-069
related: OSY-015, OSY-068, OSY-069
tags:
  - blocking-io
  - non-blocking-io
  - async-io
  - NIO
  - io_uring
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/osy/blocking-nonblocking-async-io/
---

## TL;DR

Blocking I/O: thread waits until I/O completes. Non-
blocking I/O: returns immediately (EAGAIN if no data).
Async I/O: kernel notifies you when I/O completes (no
polling). Java NIO uses non-blocking + select/epoll.
Java NIO.2 AIO uses async. io_uring (Linux 5.1+) is the
modern async I/O interface for high-throughput servers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-037 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | blocking IO, non-blocking IO, async IO, epoll, io_uring |
| **Prerequisites** | OSY-015, OSY-034 |

---

### Three I/O Models

```
BLOCKING I/O (Traditional):
  
  Application    Kernel         Disk/Network
      |          |               |
      |--read()-->|               |
      | (blocked) |--I/O request->|
      |           |    wait...    |
      |           |<-- data ready-|
      |<--data----|               |
      | (unblocked)               |
  
  Thread state: BLOCKED during entire I/O
  Simple to code, wastes thread while waiting
  Problem: 1000 connections = 1000 blocked threads

NON-BLOCKING I/O:
  
  Application    Kernel         Disk/Network
      |          |               |
      |--read()-->| (EAGAIN)      |  <- no data yet, return immediately
      | (not blocked, can do work)|
      |--poll()-->|               |  <- check again
      | (EAGAIN)  |               |
      |--read()-->|               |
      | (EAGAIN)  |               |
      |--read()-->| (data ready)  |
      |<--data----|               |
  
  Thread state: RUNNABLE (polling, not sleeping)
  Problem: busy-polling wastes CPU (spin-wait)
  Solution: combine with I/O multiplexing (select/epoll)

ASYNCHRONOUS I/O:
  
  Application    Kernel         Disk/Network
      |          |               |
      |--aio_read(callback)-->|   |  <- initiate, return immediately
      | (continues other work)|   |
      |           |--I/O request->|
      |           |    wait...    |
      |           |<-- data ready-|
      |<--callback(data)----------|  <- kernel calls back when done
  
  Thread state: RUNNABLE (doing other work)
  Most efficient: no polling, no blocking
  Java AIO: AsynchronousFileChannel, AsynchronousSocketChannel
  Linux: io_uring (Linux 5.1+), posix aio_read() (limited)
```

---

### I/O Multiplexing (select, poll, epoll)

```
Problem solved: monitor many sockets without blocking
  on any one of them.

select() (old, O(N)):
  fd_set readfds; FD_SET(fd1, &readfds); FD_SET(fd2, &readfds);
  select(maxfd+1, &readfds, NULL, NULL, &timeout);
  // Kernel checks ALL FDs in set every call -> O(N) per call
  // Limit: 1024 FDs (FD_SETSIZE)

poll() (similar to select, no FD limit but still O(N)):
  struct pollfd fds[2];
  fds[0] = {fd1, POLLIN, 0};
  fds[1] = {fd2, POLLIN, 0};
  poll(fds, 2, timeout);

epoll (Linux, O(1) for active FDs):
  int epfd = epoll_create1(0);
  struct epoll_event ev = {EPOLLIN, {.fd = fd}};
  epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);  // register fd
  
  struct epoll_event events[100];
  int n = epoll_wait(epfd, events, 100, timeout);  // wait
  // Returns only READY FDs (not all registered FDs!)
  // O(1): scales to millions of connections
  
  Java NIO Selector uses epoll under the hood on Linux.
  Nginx, Redis, Node.js all use epoll for event loop.
```

---

### Java I/O Comparison

```java
// BLOCKING I/O (java.io) - one thread per connection
public class BlockingServer {
    public void handleClient(Socket socket) {
        // This thread blocks until data arrives:
        BufferedReader in = new BufferedReader(
            new InputStreamReader(socket.getInputStream()));
        String line = in.readLine(); // BLOCKED here
        // Thread sleeps in kernel, wastes OS resources
    }
}
// Scale: 1000 connections = 1000 threads = ~1GB stack RAM

// NON-BLOCKING I/O (java.nio) - one thread many connections
public class NioServer {
    public void run() throws IOException {
        Selector selector = Selector.open();  // epoll
        ServerSocketChannel server = ServerSocketChannel.open();
        server.configureBlocking(false);  // non-blocking!
        server.bind(new InetSocketAddress(8080));
        server.register(selector, SelectionKey.OP_ACCEPT);
        
        while (true) {
            selector.select();  // epoll_wait: blocks until activity
            Set<SelectionKey> keys = selector.selectedKeys();
            for (SelectionKey key : keys) {
                if (key.isAcceptable()) {
                    accept(selector, key);
                } else if (key.isReadable()) {
                    read(key);  // data available, won't block
                }
            }
            keys.clear();
        }
    }
}
// Scale: 10,000 connections, 1-2 threads

// VIRTUAL THREADS (Java 21) - blocking syntax, NIO performance
public class VirtualThreadServer {
    public void handleClient(Socket socket) {
        // Looks like blocking IO but virtual thread parks:
        BufferedReader in = new BufferedReader(
            new InputStreamReader(socket.getInputStream()));
        String line = in.readLine(); // virtual thread parks, not OS thread
        // OS carrier thread is free to run other virtual threads!
    }
}
// Scale: 1M connections, minimal OS threads
```

---

### Comparison Table

| Model | Thread Blocks | CPU Usage | Complexity | Scale |
|-------|-------------|-----------|-----------|-------|
| Blocking I/O | YES | Low (sleep) | Simple | ~10K threads |
| Non-blocking + poll | No | HIGH (spin) | Medium | Unlimited |
| Non-blocking + epoll | No | Low (wait) | High | Millions |
| Async I/O (AIO) | No | Low (callback) | Highest | Millions |
| Virtual Threads | No (parks) | Low | Simple | Millions |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Non-blocking IO is always faster than blocking IO" | Non-blocking with busy-polling (EAGAIN loop) uses 100% CPU with no I/O. It's only efficient when combined with epoll/select for multiplexing. The combination (NIO Selector) is what scales |
| "Java NIO is complicated; use blocking IO for simplicity" | Java 21 virtual threads give blocking-IO simplicity with NIO-level scalability. For new code, virtual threads are the pragmatic choice. NIO Selector is for frameworks and infrastructure code |

---

### Quick Reference Card

| Model | Syscall | Java API | Best For |
|-------|---------|---------|---------|
| Blocking | read() (blocks) | java.io.InputStream | Simple, low concurrency |
| Non-blocking | read() + EAGAIN | FileChannel (non-blocking) | Event loops |
| Multiplexed | epoll_wait | NIO Selector | Many connections, few threads |
| Async | io_uring | AsynchronousFileChannel | High-throughput disk I/O |
| Virtual threads | read() (parks) | java.io (Java 21+) | High concurrency, simple code |
