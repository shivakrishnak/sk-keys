---
id: OSY-096
title: io_uring
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-015, OSY-016, OSY-068, OSY-089
used_by: []
related: OSY-095, OSY-097, OSY-090
tags:
  - io_uring
  - async-IO
  - kernel
  - Linux
  - low-latency
  - syscall-reduction
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 96
permalink: /technical-mastery/osy/io-uring/
---

## TL;DR

io_uring (Linux 5.1+, 2019) is a kernel I/O interface that
uses two shared ring buffers (submission and completion)
between user and kernel space. Applications submit I/O
requests without syscalls (via shared memory), and poll
completions without syscalls. Achieves near-DPDK I/O
throughput for disk and network with standard POSIX semantics.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-096 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | io_uring, async I/O, ring buffer, zero syscall, Linux 5.1+ |
| **Prerequisites** | OSY-015, OSY-016, OSY-068, OSY-089 |

---

### The Problem With Traditional I/O Syscalls

```
Traditional async I/O problem (even with epoll):
  
  epoll-based server loop:
    1. epoll_wait() syscall (blocks until fd ready)
    2. fd readable: 
    3. read() syscall (copies data from kernel to user)
    4. Application processes data
    5. write() syscall (copies response to kernel)
    6. Repeat
    
  Each syscall cost:
    User -> kernel mode transition: ~100ns
    (TLB flush, stack switch, privilege check)
    
  At 1M operations/second:
    2-3 syscalls per request = 2-3M syscalls/second
    Total syscall overhead: 200-300ms CPU time wasted on transitions
    
  aio (Linux async I/O, before io_uring):
    Limited to O_DIRECT files only
    Inconsistent: some ops still block despite being "async"
    Complex API; used by few applications
    Not for network sockets at all
    
io_uring solution:
  Two ring buffers in SHARED MEMORY (user + kernel both access):
    SQ (Submission Queue): user writes I/O requests here
    CQ (Completion Queue): kernel writes results here
    
  Submit: write to SQ ring (memory write, no syscall!)
  Poll: read CQ ring (memory read, no syscall!)
  io_uring_enter(): optional syscall to wake kernel if needed
    -> In SQPOLL mode: dedicated kernel thread polls SQ
       User doesn't even need to call io_uring_enter()
```

---

### io_uring Architecture

```
User space                  |  Kernel space
                            |
  Application               |  io_uring kernel thread
      |                     |       (if SQPOLL mode)
      | writes SQE          |       |
      v                     |       | reads SQE
  SQ Ring Buffer ==========>|======> executes I/O
  (shared memory)           |       |
                            |       | writes CQE
  CQ Ring Buffer <=========|<====== completion
  (shared memory)           |
      |
      | reads CQE
      v
  Application processes result
  
  SQE (Submission Queue Entry):
    opcode: IORING_OP_READ, IORING_OP_WRITE, IORING_OP_ACCEPT,
            IORING_OP_CONNECT, IORING_OP_SENDMSG, IORING_OP_RECVMSG,
            IORING_OP_FSYNC, IORING_OP_TIMEOUT, ... (50+ ops)
    fd: file descriptor
    addr: buffer address
    len: buffer length
    offset: file offset (for files)
    user_data: opaque 64-bit value (your request identifier)
    
  CQE (Completion Queue Entry):
    user_data: matches SQE's user_data (identifies which request)
    res: return value (bytes transferred, or -errno on error)
    flags: additional information
    
  Key advantage: batching
    Submit 64 I/O requests in one io_uring_enter() call
    vs: 64 read() syscalls = 64 mode transitions
```

---

### Usage Modes

```
Mode 1: Interrupt-driven (default)
  Submit: write SQE to ring, call io_uring_enter()
  Kernel: processes I/O asynchronously
  Completion: poll CQ ring or use eventfd notification
  Best for: standard async I/O with occasional syscalls
  
Mode 2: SQPOLL (zero-syscall mode)
  # Requires: IORING_SETUP_SQPOLL flag + privileged process
  # Kernel spawns an SQ poller thread (dedicated kernel thread)
  # Poller loops: reads SQEs without application syscall
  # Application: just writes to SQ ring (no syscall)
  # Poll CQ ring for completions (no syscall)
  
  # Result: truly zero-syscall I/O
  # CPU cost: SQ poller thread runs continuously (pinned core)
  # Best for: NVMe with millions IOPS; network at line rate
  
Mode 3: Fixed buffers (io_uring_register)
  Register buffers once: io_uring_register(IORING_REGISTER_BUFFERS)
  Reference by index in SQE (not pointer)
  Kernel pins physical pages: no per-I/O pinning/unpinning
  Benefit: eliminates per-operation page pin/unpin overhead
  Best for: high-IOPS NVMe operations with fixed buffer pool
  
Chaining operations:
  IOSQE_IO_LINK flag: chain SQEs
  Example: read file -> process -> write result
  All 3 submitted at once; kernel executes in sequence
  No application wakeup between steps
```

---

### Performance Numbers

```
Benchmark: single-core NVMe random read (4KB)
  
  sync read() syscall: 200,000 IOPS (1 syscall per read)
  epoll + async: 600,000 IOPS (epoll + read syscall per event)
  io_uring interrupt mode: 900,000 IOPS (batched submits)
  io_uring SQPOLL + fixed buffers: 1,200,000+ IOPS (zero syscall)
  
  Note: actual numbers vary by hardware and kernel version.
    NVMe hardware limit: 800K-1M IOPS typical for consumer NVMe
    io_uring can saturate NVMe; old APIs couldn't
    
Flamegraph comparison:
  epoll + read: syscall overhead = 30-40% of CPU time
  io_uring SQPOLL: syscall overhead near 0%
  Difference: those saved cycles = more application work
```

---

### Java and io_uring

```java
// Java 21 Loom integration (planned/partial):
// Virtual threads benefit from io_uring for blocking I/O
// When a virtual thread blocks on I/O:
//   JVM unmounts from OS thread
//   Submits I/O to io_uring SQ
//   OS thread free to run other virtual threads
//   On completion (CQE received): virtual thread remounted
//
// This is different from Thread.sleep() on virtual threads
// which just unmounts (no real I/O)

// Netty 5.x (unreleased as of 2024): io_uring support planned
// netty-incubator-transport-io_uring:
//   Provides IoUringEventLoopGroup
//   Uses io_uring for all network I/O
//   
// Current usage (experimental):
/*
<dependency>
  <groupId>io.netty.incubator</groupId>
  <artifactId>netty-incubator-transport-io_uring</artifactId>
  <version>0.0.21.Final</version>
</dependency>
*/

// Python: uvloop (Cython) -> libuv -> io_uring on Linux 5.1+
// Rust: tokio with io_uring support via tokio-uring crate
// Node.js: libuv 1.43+ has experimental io_uring support
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "io_uring is just better epoll" | epoll notifies when an fd is READY; you still call read/write syscalls. io_uring submits the actual I/O operation as a work item; the kernel completes the I/O and writes the result to the CQ ring. io_uring eliminates read/write syscalls entirely, not just the notification step. |
| "io_uring requires kernel 5.19+ for all features" | io_uring was introduced in 5.1 (2019). Basic functionality: 5.1. SQPOLL stabilized: 5.12. Most important features: 5.10-5.15. A 5.10+ LTS kernel has excellent io_uring support. The API has grown: newer kernels have more opcodes (accept, multishot recv, etc). |
| "io_uring has no security concerns" | io_uring has had several CVEs. The shared memory model and kernel thread (SQPOLL) have complex security implications. In sandboxed environments: io_uring is often restricted. Docker and Kubernetes security profiles may restrict io_uring syscalls via seccomp. Production environments: test seccomp filters allow `io_uring_setup`, `io_uring_enter`, `io_uring_register`. |

---

### Quick Reference Card

| Concept | io_uring Detail |
|---------|----------------|
| Kernel version | 5.1+ (basic); 5.10+ (recommended) |
| Key rings | SQ (submit), CQ (completions) |
| Zero-syscall mode | IORING_SETUP_SQPOLL |
| Operations | 50+ ops: read, write, accept, connect, fsync, timeout... |
| Java support | Netty incubator; Loom virtual threads (planned) |
| Performance | 1M+ IOPS on NVMe; near-DPDK for networking |
| Security | Restricted in containers; check seccomp filters |
| Rust | tokio-uring crate |
