---
id: OSY-068
title: epoll Linux Event Polling
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-015, OSY-016, OSY-034
used_by: OSY-095, OSY-096
related: OSY-015, OSY-069, OSY-096
tags:
  - epoll
  - event-driven
  - non-blocking-IO
  - C10K
  - Netty
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/osy/epoll/
---

## TL;DR

epoll is Linux's scalable I/O event notification mechanism.
Unlike `select/poll` (which scan all FDs each call), epoll
maintains a kernel-space set of watched FDs and returns
ONLY ready FDs. O(1) per event; scales to 100K+ connections.
The mechanism behind Nginx, Node.js, Netty, and all modern
high-connection servers. Solves the C10K problem.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-068 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | epoll, select, poll, C10K, edge-triggered, level-triggered |
| **Prerequisites** | OSY-015, OSY-016, OSY-034 |

---

### Evolution: select -> poll -> epoll

```
select() (POSIX, 1983):
  Limitations:
    FD_SETSIZE = 1024 maximum FDs (hard limit!)
    O(N) scan: kernel checks ALL N FDs on every call
    FD set must be reconstructed each call (copied to kernel)
    
  Usage:
    fd_set readfds;
    FD_SET(sock_fd, &readfds);
    select(max_fd + 1, &readfds, NULL, NULL, &timeout);

poll() (POSIX, improvement over select):
  No hard FD limit (uses dynamic array)
  Still O(N): kernel scans all FDs in array each call
  Still copies array to kernel on every call
  Impractical for > 10K FDs: O(N) dominates
  
  1000 connections * 1000 polls/sec = 1M O(N) scans/sec
  
epoll() (Linux 2.6, 2002 - Davide Libenzi):
  Key insight: "tell the kernel which FDs to watch, not which to check"
  
  Architecture:
    epoll_create(): create epoll instance (returns epoll fd)
    epoll_ctl():    add/remove/modify FD registration (O(1))
    epoll_wait():   block until events; returns only ready FDs (O(ready))
    
  Performance:
    O(1) for each event
    No copy of FD set each call (registered in kernel)
    Returns only READY FDs: process only what needs attention
    10K connections, 100 active: process 100, not 10K
```

---

### epoll Deep Dive: ET vs LT

```
Level-Triggered (LT, default):
  epoll_wait() returns FD as ready:
    - As long as data remains in socket buffer
  Re-reports FD each call until all data is read
  Safe: easy to use, no data left behind
  
  Example: 1KB data in buffer
    Call 1: epoll_wait -> returns fd
    Read 512 bytes
    Call 2: epoll_wait -> returns fd AGAIN (500 bytes remain)
    Read remaining 512 bytes
    Call 3: epoll_wait -> fd no longer ready (buffer empty)

Edge-Triggered (ET):
  epoll_wait() returns FD as ready:
    - ONLY when new data arrives (state change)
  Reports FD ONCE; must read ALL data before next event
  
  If data arrives while reading: another edge event
  If you read only partial data: MISSED event -> hang!
  
  Must use with non-blocking sockets:
    Set O_NONBLOCK on FD
    Read in a loop until EAGAIN (no more data)
    Only then return to epoll_wait
    
  EAGAIN means: you've read all available data
    Next call would block -> stop, return to event loop
    
  Performance: fewer epoll_wait calls (each call does real work)
  Use: Nginx, io_uring, very high performance systems
```

---

### Java and epoll

```java
// Java NIO Selector: wraps epoll on Linux
// - Single thread handles thousands of connections
// - SelectionKey represents one registered channel+events

// Netty (uses epoll selector internally):
// EpollEventLoopGroup -> Java epoll JNI bindings
// NioEventLoopGroup   -> Java NIO Selector (wraps epoll on Linux)
// Netty recommends EpollEventLoopGroup for Linux (direct epoll JNI)

// Java NIO Selector pattern:
public class EchoServer {
    public static void serve(int port) throws IOException {
        ServerSocketChannel server = ServerSocketChannel.open();
        server.bind(new InetSocketAddress(port));
        server.configureBlocking(false);
        
        Selector selector = Selector.open();  // epoll_create
        server.register(selector, SelectionKey.OP_ACCEPT);  // epoll_ctl
        
        ByteBuffer buf = ByteBuffer.allocate(1024);
        
        while (true) {
            selector.select();  // epoll_wait
            
            Set<SelectionKey> ready = selector.selectedKeys();  // READY FDs only
            Iterator<SelectionKey> it = ready.iterator();
            
            while (it.hasNext()) {
                SelectionKey key = it.next();
                it.remove();  // must remove manually
                
                if (key.isAcceptable()) {
                    SocketChannel client = server.accept();
                    client.configureBlocking(false);
                    client.register(selector, SelectionKey.OP_READ);
                } else if (key.isReadable()) {
                    SocketChannel client = (SocketChannel) key.channel();
                    int bytesRead = client.read(buf);
                    if (bytesRead == -1) {
                        client.close();  // connection closed
                    } else {
                        buf.flip();
                        client.write(buf);  // echo back
                        buf.clear();
                    }
                }
            }
        }
    }
}
// One thread: handles thousands of connections
// No thread-per-connection overhead
// Scales to C10K+ (10K concurrent connections)
```

---

### epoll Performance Characteristics

```
Connection count vs CPU:

  Thread-per-connection (Java pre-NIO):
    1000 connections: 1000 threads
    Thread stack: 1MB each = 1GB RAM
    Context switches: O(1000) per request cycle
    At 10K: 10GB RAM, impractical
    
  epoll single-thread:
    100K connections: 1 thread
    Memory: just socket buffers (few KB each)
    Context switches: nearly zero (no thread waiting)
    
  epoll with thread pool (real production pattern):
    Event loop threads: 1 per CPU (Netty NIO workers)
    Accept connections -> dispatch reads to thread pool
    Handler thread: do work, write response
    Total threads: CPUs + worker pool (e.g., 8 + 50 = 58)
    
  Throughput:
    select/poll: ~10K connections (O(N) kills performance beyond)
    epoll: tested to 1M+ connections (O(1) per event)
    
Level vs Edge triggered in production:
  Nginx: uses edge-triggered + non-blocking loops
  Java NIO Selector: uses level-triggered (simpler API)
  io_uring: edge-triggered based, even more efficient
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java threads can't handle 10K connections" | Java's thread-per-connection model struggles, but Java NIO with Selector (backed by epoll) handles 100K+ connections in a single thread. Netty and modern Java (virtual threads in Java 21) make this even easier. The C10K problem was a thread model problem, not a Java problem |
| "Edge-triggered epoll is always better than level-triggered" | Edge-triggered is more efficient (fewer epoll_wait calls) but requires careful implementation: must read until EAGAIN every time, or events are lost. One bug means missed data and a hung connection. Level-triggered is safer and easier to implement correctly. Only switch to ET if profiling shows LT epoll overhead is significant |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| select limitation | Max 1024 FDs; O(N) scan per call |
| epoll complexity | O(1) per event; O(ready) per epoll_wait call |
| Level-triggered (LT) | Reports FD ready until buffer drained; safe default |
| Edge-triggered (ET) | Reports FD once on state change; must read until EAGAIN |
| Java API | `Selector` (NIO); wraps epoll on Linux |
| C10K solution | 1 thread + epoll + non-blocking I/O handles 100K connections |
