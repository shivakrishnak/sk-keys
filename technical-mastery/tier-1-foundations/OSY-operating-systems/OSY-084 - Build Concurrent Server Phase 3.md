---
id: OSY-084
title: Build Concurrent Server Phase 3
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-044, OSY-068, OSY-069, OSY-070
used_by: []
related: OSY-083, OSY-085, OSY-113
tags:
  - build
  - concurrent-server
  - epoll
  - Java
  - hands-on
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 84
permalink: /technical-mastery/osy/build-concurrent-server-phase3/
---

## TL;DR

Phase 3 of the build series: add non-blocking I/O (Java NIO
Selector backed by epoll), worker thread pool separation
(I/O threads vs task threads), and OS-level measurement.
Goal: serve 50K concurrent connections with <1ms overhead
per connection on a single server.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-084 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | build, concurrent server, NIO, epoll, thread pool |
| **Prerequisites** | OSY-044, OSY-068, OSY-069, OSY-070 |

---

### Phase 3: NIO Selector Architecture

```
Phase 1 (OSY-044): thread-per-connection (Thread-Per-Request model)
Phase 2 (OSY-069): basic thread pool + blocking IO
Phase 3 (OSY-084): NIO Selector + epoll + separated thread pools

Goal: 50K connections, < 1 thread per connection,
      < 1ms per-connection overhead.
      
Architecture:
  
  Acceptor Thread (1):
    ServerSocketChannel (non-blocking)
    accept() -> register new channel with Selector
    
  I/O Thread(s) (N = 1 per CPU core):
    Each: Selector backed by epoll
    selector.select() -> blocked until at least 1 ready fd
    Handle: READ events -> deserialize -> hand off to worker pool
    Handle: WRITE events -> flush pending responses
    
  Worker Thread Pool (CPU-bound or blocking work):
    N = number of CPU cores * 2 (if I/O-bound tasks)
    Receives: deserialized request objects
    Sends: responses back via Selector (thread-safe queue per connection)
    
  This is the Reactor pattern:
    Boss/Acceptor: one Selector for accepts
    Worker: one Selector per thread for I/O events
    (Netty's EventLoop is exactly this)
```

---

### Implementation Skeleton

```java
// Phase 3: Single-threaded NIO Reactor (simplified)
// Full production: use Netty or Vert.x

public class Phase3NioServer {

    private static final int PORT = 9090;
    private static final int WORKER_THREADS = 4;

    // Worker pool (separate from I/O thread)
    private final ExecutorService workers =
        Executors.newFixedThreadPool(WORKER_THREADS);

    public void start() throws IOException {
        // Non-blocking server socket
        ServerSocketChannel serverChannel =
            ServerSocketChannel.open();
        serverChannel.configureBlocking(false);
        serverChannel.bind(
            new InetSocketAddress(PORT));

        // Selector (backed by epoll on Linux)
        Selector selector = Selector.open();
        serverChannel.register(
            selector, SelectionKey.OP_ACCEPT);

        System.out.println("Server started on " + PORT);
        ByteBuffer buffer = ByteBuffer.allocateDirect(4096);

        while (true) {
            // Blocks until at least 1 fd is ready
            // (epoll_wait under the hood on Linux)
            selector.select();

            Iterator<SelectionKey> keys =
                selector.selectedKeys().iterator();

            while (keys.hasNext()) {
                SelectionKey key = keys.next();
                keys.remove();

                if (key.isAcceptable()) {
                    handleAccept(serverChannel, selector);
                } else if (key.isReadable()) {
                    handleRead(key, buffer);
                }
            }
        }
    }

    private void handleAccept(
            ServerSocketChannel server,
            Selector selector) throws IOException {
        SocketChannel client = server.accept();
        if (client != null) {
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        }
    }

    private void handleRead(
            SelectionKey key,
            ByteBuffer buffer) {
        SocketChannel channel = (SocketChannel) key.channel();
        buffer.clear();
        int bytesRead;
        try {
            bytesRead = channel.read(buffer);
        } catch (IOException e) {
            key.cancel();
            return;
        }

        if (bytesRead == -1) {
            // Client closed connection
            key.cancel();
            return;
        }

        // Clone buffer before handing to worker thread
        byte[] data = new byte[buffer.flip().remaining()];
        buffer.get(data);

        // Hand off to worker - I/O thread is NOT blocked
        workers.submit(() -> processRequest(channel, data));
    }

    private void processRequest(
            SocketChannel channel,
            byte[] request) {
        // Do business logic (may block) in worker thread
        // ...
        byte[] response = ("Echo: " +
            new String(request) + "\n").getBytes();
        try {
            channel.write(ByteBuffer.wrap(response));
        } catch (IOException e) {
            // log error
        }
    }
}
```

---

### OS-Level Measurement

```bash
# Verify epoll is being used (on Linux)
# Find Java process PID
PID=$(pgrep -f Phase3NioServer)

# Check file descriptors
ls -la /proc/$PID/fd | wc -l    # Total open FDs
ls -la /proc/$PID/fd | grep socket | wc -l  # Socket FDs

# Monitor context switches (should be minimal with epoll)
pidstat -w -p $PID 1 10
# Look at: cswch/s (voluntary) and nvcswch/s (non-voluntary)
# Good: high voluntary (process yields willingly via select)
# Bad: high non-voluntary (preempted mid-work = too few threads or CPU saturation)

# Monitor epoll fd registration
strace -e trace=epoll_create,epoll_ctl,epoll_wait -p $PID 2>&1 | head -50

# Watch: connection count
ss -s  # summary
ss -t state established | grep :9090 | wc -l  # count to our port

# Load test with wrk
wrk -t4 -c10000 -d30s http://localhost:9090/

# Expected results with Phase 3:
# Threads: 2 (acceptor + selector loop) + 4 workers = 6 total
# Handles: thousands of connections
# Context switches: low (selector blocks, wakes on events)
```

---

### Phase Comparison

| Feature | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|
| Threading model | 1 thread/connection | Thread pool | NIO Selector + pool |
| Max connections | ~1K (thread limit) | ~5K (pool queue) | ~50K+ |
| Blocking I/O | Yes (OS thread blocked) | Yes | No (epoll) |
| Context switches | Very high | High | Low |
| OS threads | N per connection | Pool size | Pool + I/O threads |
| Complexity | Low | Medium | High |
| Framework equiv | Raw Java Threads | Tomcat (classic) | Netty, Vert.x |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java NIO is zero-copy" | NIO is non-blocking, not zero-copy. Non-blocking = doesn't block the OS thread. Zero-copy = transferFileChannel uses sendfile(). Different features. |
| "NIO is always faster than blocking IO" | For low concurrency (<100 connections), thread-per-request with blocking IO is simpler and fast enough. NIO complexity is justified only at high connection counts. |

---

### Quick Reference Card

| Question | Answer |
|----------|--------|
| What JDK class wraps epoll? | `Selector` (java.nio.channels) backed by `EPollSelectorImpl` |
| How to verify NIO is using epoll? | `strace -e epoll_wait -p PID` |
| How many threads for 50K connections? | 1 acceptor + N_CPU I/O threads + M worker threads |
| Main risk with single Selector thread | It becomes the bottleneck; use multiple Selectors (one per CPU) |
| How to test without high load? | `ss -t state established \| grep PORT \| wc -l` |
