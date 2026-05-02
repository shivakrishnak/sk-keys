---
layout: default
title: "Async I/O"
parent: "Operating Systems"
nav_order: 106
permalink: /operating-systems/async-io/
number: "0106"
category: Operating Systems
difficulty: ★★☆
depends_on: Non-Blocking I/O, Blocking I/O, System Call (syscall)
used_by: epoll / kqueue / io_uring, Reactive Programming, Node.js
related: Non-Blocking I/O, epoll / kqueue / io_uring, Blocking I/O
tags:
  - os
  - networking
  - internals
  - intermediate
  - performance
---

# 106 — Async I/O

⚡ TL;DR — Async I/O lets you fire off I/O operations and get notified when they complete — no thread blocked, no polling, just a callback when the work is done.

| #0106           | Category: Operating Systems                               | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Non-Blocking I/O, Blocking I/O, System Call (syscall)     |                 |
| **Used by:**    | epoll / kqueue / io_uring, Reactive Programming, Node.js  |                 |
| **Related:**    | Non-Blocking I/O, epoll / kqueue / io_uring, Blocking I/O |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Non-blocking I/O requires the programmer to repeatedly ask "are you done yet?" via epoll events and re-issue read/write calls. The application code becomes a state machine: "started reading… got partial data… got EAGAIN… waiting for epoll… got event… reading more…" The programmer manages every transition manually. For complex protocols with multiple steps (TLS handshake → HTTP request → database call → response), the state machine becomes enormous and error-prone.

**THE BREAKING POINT:**
High-performance databases and storage engines that issue hundreds of I/O operations simultaneously faced this complexity. The Linux `aio` API (POSIX AIO) existed but had severe limitations: it only worked on files, required direct I/O (`O_DIRECT`), and used a thread pool under the hood rather than true async kernel I/O.

**THE INVENTION MOMENT:**
This is exactly why true Async I/O was created — you submit an I/O request, continue doing other work, and are notified via a completion event when the kernel finishes the operation. No polling, no state machines for readiness, no `EAGAIN` handling.

---

### 📘 Textbook Definition

**Asynchronous I/O (Async I/O)** is an I/O model in which the application submits an I/O request to the kernel and immediately receives control back — the operation is performed in the background. When the kernel completes the operation, it notifies the application via a completion event (callback, signal, completion queue, or future/promise). The application never blocks waiting for I/O, and never needs to poll for readiness. The two primary models are: **proactor** (completion-based, as in Windows IOCP and Linux `io_uring`), and **reactor** (readiness-based, as in `epoll` + non-blocking I/O — technically NOT async I/O, but often called that loosely).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Async I/O means: "here's my request, call me when it's done" — your code does other things and gets a callback on completion.

**One analogy:**

> Ordering food for delivery online. You place the order (submit I/O), get an order ID (handle/future), and go about your day. The restaurant calls you when the food arrives (completion notification). Contrast: standing at the counter watching them cook (blocking I/O), or calling every 5 minutes to ask "is it ready?" (non-blocking polling).

**One insight:**
The critical difference between async I/O and non-blocking I/O: non-blocking returns "not ready" (readiness model) — you must do the actual I/O yourself when ready. Async I/O submits the entire operation — the kernel does the actual read/write, copies the data to your buffer, and notifies you when done. You never handle `EAGAIN`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An async I/O call returns immediately after submission — before the I/O completes.
2. The kernel performs the actual I/O operation, writing results directly to the user-supplied buffer.
3. Completion is communicated to the application asynchronously — no polling needed.

**DERIVED DESIGN:**
True async I/O requires the kernel to retain a reference to the user buffer and perform the I/O while the application runs. The kernel maintains a completion queue; when I/O finishes, it places a completion event in the queue. The application either:

- Polls the completion queue periodically (zero-copy, no syscall if events are queued)
- Blocks on the completion queue (`io_uring_enter` with min_complete > 0)
- Registers a callback (IOCP on Windows, signal on POSIX AIO)

`io_uring` (Linux 5.1+) uses two ring buffers shared between user and kernel: submission ring (user writes requests) and completion ring (kernel writes completions). For many operations, zero syscalls are needed after setup.

**THE TRADE-OFFS:**
**Gain:** Maximum I/O throughput; zero blocking; kernel does the copies; simpler application logic (no EAGAIN, no partial reads) than non-blocking I/O.
**Cost:** More complex initial setup; buffer lifetime management is tricky (buffer must live until completion); cancellation is harder; debugging completion-based code is harder than blocking code.

---

### 🧪 Thought Experiment

**SETUP:**
A database must read 1,000 separate 4 KB records from an NVMe SSD simultaneously.

**WHAT HAPPENS WITH blocking I/O (thread per read):**

1. 1,000 threads, each calling `read()` on a different file offset.
2. All 1,000 threads block, OS services them via scheduler.
3. NVMe can service ~200 concurrent requests natively; 800 extra threads add zero throughput.

**WHAT HAPPENS WITH non-blocking + epoll:**

1. 1,000 `read()` calls issued; all return `EAGAIN` (no readiness signal for file I/O).
2. `epoll` doesn't work for regular files — they're always "ready" in `select()`.
3. This model fundamentally doesn't help with disk I/O.

**WHAT HAPPENS WITH async I/O (io_uring):**

1. Submit 1,000 read operations to io_uring submission queue — one `io_uring_enter()` syscall.
2. Kernel dispatches to NVMe block device, which natively parallelises up to 1,000 requests.
3. Completions arrive in the completion ring as reads finish (out of order, as hardware completes them).
4. Application harvests completed reads, processes data.
5. Result: near-hardware-maximum throughput, one thread, near-zero syscall overhead.

**THE INSIGHT:**
Async I/O is the only model that matches the parallelism of modern hardware. NVMe SSDs handle 1M IOPS natively; a single-threaded async application can exploit all of it. Blocking I/O can too, but only if you create as many threads as outstanding I/O operations — which has memory and scheduling overhead.

---

### 🧠 Mental Model / Analogy

> Async I/O is like handing your dry cleaning to a valet service. You give them the clothes (submit I/O with buffer), go about your day (application runs), and they text you when everything is pressed and ready (completion event). You didn't stand at the dry cleaner (blocking), you didn't keep calling them (non-blocking polling) — you simply left a number and continued.

- "Dropping off clothes" → submitting I/O operation with buffer
- "Going about your day" → application continues running other work
- "Text notification" → completion event in io_uring CQ ring
- "Picking up clothes" → reading the completion event and using the data

Where this analogy breaks down: With async I/O, you can submit thousands of operations simultaneously — the valet analogy breaks down at scale, but it captures the fundamental completion-notification model.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Async I/O means you kick off a read or write operation and get a notification when it's done, rather than waiting around. Your program can do other useful work in the meantime. It's like placing an order online and getting a delivery notification instead of standing at the shop.

**Level 2 — How to use it (junior developer):**
In Java, `java.nio.channels.AsynchronousFileChannel` and `AsynchronousSocketChannel` provide async I/O with `CompletionHandler` callbacks or `Future` objects. In Node.js, all I/O is async — `fs.readFile('data.txt', callback)` submits the operation and calls the callback on completion. In C/Linux, `io_uring` is the modern API. Key rule: the buffer you pass to an async read must stay alive until the completion handler fires.

**Level 3 — How it works (mid-level engineer):**
`io_uring_setup()` allocates two shared ring buffers (SQ ring and CQ ring) in memory accessible to both user space and kernel. `io_uring_prep_read(sqe, fd, buf, len, offset)` fills a Submission Queue Entry. `io_uring_submit()` calls `io_uring_enter()` syscall (or is done lazily). The kernel's io_uring worker thread (or polled mode with `IORING_SETUP_SQPOLL`) processes SQEs, submits to the block layer, and places Completion Queue Entries (CQEs) in the CQ ring when done. The application calls `io_uring_wait_cqe()` or polls the CQ ring in a loop. With `IORING_SETUP_SQPOLL`, a kernel thread polls the SQ ring — zero syscalls after setup for submission.

**Level 4 — Why it was designed this way (senior/staff):**
POSIX AIO was the first async I/O standard but was broken: it used a thread pool under the hood (fake async), only worked with `O_DIRECT` (no page cache), and had terrible error reporting. Linux `aio_read()` had the same problems. `io_uring` (Jens Axboe, 2019) was designed from scratch to: (1) truly submit to the block layer without extra threads, (2) work with any file descriptor (sockets, pipes, files), (3) support batching via ring buffers (amortising syscall cost), (4) support fixed buffers (pre-registered user buffers the kernel can DMA directly into). The proactor pattern (completion-based) that io_uring implements was standard on Windows via IOCP for 20 years — io_uring finally brought true async I/O to Linux. Java's Structured Concurrency and virtual threads (JDK 21) use io_uring on Linux under the hood for file I/O, making async I/O transparent to the programmer.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│              io_uring ARCHITECTURE                      │
├─────────────────────────────────────────────────────────┤
│  User Space          │  Kernel                          │
│  ┌────────────────┐  │  ┌────────────────────────────┐  │
│  │ SQ Ring        │  │  │ io_uring kernel thread     │  │
│  │ [SQE0][SQE1]   │→→│→→│ reads SQEs, submits to    │  │
│  │ [SQE2]...      │  │  │ block/net layer            │  │
│  └────────────────┘  │  └────────────────────────────┘  │
│                      │           ↓ I/O completes        │
│  ┌────────────────┐  │  ┌────────────────────────────┐  │
│  │ CQ Ring        │  │  │ Completion placed in CQ    │  │
│  │ [CQE0][CQE1]   │←←│←←│ ring by interrupt handler │  │
│  └────────────────┘  │  └────────────────────────────┘  │
│  App polls CQ ring   │                                  │
│  (no syscall needed) │                                  │
└─────────────────────────────────────────────────────────┘
```

**Steps:**

1. App fills SQE: operation (read/write/accept/connect), fd, buffer, length, offset.
2. App advances SQ tail pointer.
3. `io_uring_enter(fd, to_submit, min_complete, flags)` — optional if SQPOLL enabled.
4. Kernel processes SQEs, dispatches to hardware.
5. On completion: CQE placed in CQ ring with result (bytes read or error code).
6. App reads CQE from CQ head.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[App: io_uring_prep_read(sqe, fd, buf, 4096, 0)]
   → [SQE placed in submission ring]
   → [io_uring_submit() — optional syscall ← YOU ARE HERE]
   → [Kernel: reads SQE, issues block I/O]
   → [NVMe: DMA data directly to buf]
   → [CQE placed in completion ring]
   → [App: io_uring_wait_cqe() → reads result]
   → [buf contains data — no copy needed]
```

**FAILURE PATH:**
[Disk I/O error] → [CQE.res = -EIO (negative errno)] → [App checks CQE result, handles error]

**WHAT CHANGES AT SCALE:**
With 1M IOPS from NVMe, a single io_uring loop can saturate the device. `IORING_SETUP_SQPOLL` eliminates ALL syscall overhead — kernel thread polls the SQ ring continuously (at the cost of one dedicated CPU core). Fixed buffers (`io_uring_register_buffers`) allow the kernel to pin user buffers and DMA directly into them, eliminating all copies. Used by storage engines like RocksDB, Ceph, and SPDK.

---

### 💻 Code Example

Example 1 — io_uring basic read:

```c
#include <liburing.h>

// BAD: blocking read — one thread per operation
int fd = open("data.bin", O_RDONLY);
char buf[4096];
read(fd, buf, 4096);  // thread blocks here

// GOOD: async read with io_uring
struct io_uring ring;
io_uring_queue_init(32, &ring, 0);

int fd = open("data.bin", O_RDONLY);
char buf[4096];

// Submit read operation
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, sizeof(buf), 0);
io_uring_sqe_set_data(sqe, (void*)1);  // user data
io_uring_submit(&ring);

// Do other work here while I/O runs...

// Wait for completion
struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);
if (cqe->res < 0) {
    fprintf(stderr, "read error: %s\n",
            strerror(-cqe->res));
}
// buf now contains data — no copy
io_uring_cqe_seen(&ring, cqe);
io_uring_queue_exit(&ring);
```

Example 2 — Batch submission (1000 reads):

```c
// BAD: 1000 syscalls for 1000 reads
for (int i = 0; i < 1000; i++) {
    pread(fd, bufs[i], 4096, offsets[i]);
}

// GOOD: 1 syscall for 1000 reads with io_uring
struct io_uring ring;
io_uring_queue_init(1024, &ring, 0);

for (int i = 0; i < 1000; i++) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    io_uring_prep_read(sqe, fd, bufs[i],
                       4096, offsets[i]);
    io_uring_sqe_set_data(sqe, (void*)(uintptr_t)i);
}
io_uring_submit(&ring);  // ONE syscall for all 1000

// Harvest completions
int completed = 0;
while (completed < 1000) {
    struct io_uring_cqe *cqe;
    io_uring_wait_cqe(&ring, &cqe);
    int idx = (int)(uintptr_t)io_uring_cqe_get_data(cqe);
    process(bufs[idx], cqe->res);
    io_uring_cqe_seen(&ring, cqe);
    completed++;
}
```

---

### ⚖️ Comparison Table

| Model                    | Blocks Thread | Polling    | Syscalls/op     | Best For               |
| ------------------------ | ------------- | ---------- | --------------- | ---------------------- |
| **Blocking I/O**         | Yes           | No         | 1               | Simple low-concurrency |
| Non-blocking + epoll     | No            | Readiness  | ~2 (epoll+read) | Network servers        |
| **Async I/O (io_uring)** | No            | Optional   | ~0 amortised    | Max I/O throughput     |
| POSIX AIO                | No            | Completion | 1 (thread pool) | Legacy compatibility   |
| Windows IOCP             | No            | Completion | 1               | Windows high-perf I/O  |

How to choose: Use io_uring for new Linux storage-heavy applications needing maximum throughput. Use epoll + non-blocking for network servers where Linux 5.1+ io_uring is not available. Use blocking I/O + virtual threads (Java 21) for simplicity with good concurrency.

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| "Non-blocking I/O = Async I/O"          | Non-blocking (readiness model) returns EAGAIN; async I/O (completion model) completes the operation and notifies you — fundamentally different |
| "Node.js uses async I/O for everything" | Node.js uses epoll (non-blocking) for network; libuv thread pool (fake async, blocking calls) for file I/O on Linux                            |
| "POSIX AIO is real async I/O"           | POSIX AIO on Linux uses a thread pool under the hood — it simulates async I/O, it doesn't use kernel-native async operations                   |
| "Async I/O is always the fastest model" | For low-concurrency or CPU-bound workloads, blocking I/O with threads avoids the complexity overhead with equivalent performance               |
| "io_uring eliminates all syscalls"      | io_uring reduces syscalls to near zero for batched I/O; the `io_uring_enter()` syscall is still needed unless SQPOLL mode is used              |

---

### 🚨 Failure Modes & Diagnosis

**1. Buffer Lifetime Violation (Use-After-Free)**

**Symptom:** Data corruption; intermittent wrong values in read buffer; crashes with SIGSEGV in completion handler.

**Root Cause:** The buffer passed to an async read was freed/reused before the I/O completed; the kernel wrote data to deallocated memory.

**Diagnostic:**

```bash
# Use AddressSanitizer to catch use-after-free
gcc -fsanitize=address ./myapp.c -o myapp
./myapp  # ASAN will report the violation
```

**Fix:** Keep buffer alive until CQE is received. Use reference counting or scoped lifetimes for async I/O buffers.

**Prevention:** In C++, use `std::shared_ptr` to manage buffer lifetime; tie buffer to the async handle that references it.

---

**2. CQ Ring Overflow (Completion Events Dropped)**

**Symptom:** Missing completions; operations submitted but results never received; application hangs waiting for events that already completed.

**Root Cause:** Application not draining the CQ ring fast enough; CQ ring fills up and kernel drops CQEs (io_uring signals this via `IORING_FEAT_CQE_SKIP`).

**Diagnostic:**

```bash
# Check for CQ ring overflow events
cat /proc/<PID>/fdinfo/<io_uring_fd> | grep overflow
```

**Fix:** Drain the CQ ring in a tight loop; increase CQ ring size at `io_uring_setup` time (default: 2× SQ ring size).

**Prevention:** Ensure CQ processing keeps pace with SQ submission; don't submit more operations than the CQ ring can hold.

---

**3. io_uring Security Vulnerability (Privilege Escalation)**

**Symptom:** Container escape or privilege escalation exploiting io_uring kernel bugs; CVE-2022-2602 and similar.

**Root Cause:** io_uring's complex kernel code path has historically had security vulnerabilities; kernel bugs in io_uring's file reference counting allowed privilege escalation.

**Diagnostic:**

```bash
# Check if io_uring is disabled in container
cat /proc/sys/kernel/io_uring_disabled
# 0 = enabled, 1 = disabled for unprivileged, 2 = disabled
```

**Fix:** On container hosts, restrict io_uring: `sysctl -w kernel.io_uring_disabled=2`. In seccomp profiles, block `io_uring_setup` syscall for untrusted workloads.

**Prevention:** Keep kernel updated (io_uring bugs are actively fixed). For containers, apply seccomp profile blocking io_uring until explicitly needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Non-Blocking I/O` — understand the readiness model before learning the completion model
- `Blocking I/O` — the baseline; async I/O solves its scaling problems
- `System Call (syscall)` — async I/O minimises syscall frequency

**Builds On This (learn these next):**

- `epoll / kqueue / io_uring` — the kernel APIs implementing async and non-blocking I/O
- `Reactive Programming` — the programming paradigm built on async I/O completion events
- `Node.js` — the runtime where async I/O is the default programming model

**Alternatives / Comparisons:**

- `Non-Blocking I/O` — readiness model (EAGAIN) vs completion model; different code structure
- `Virtual Threads (JDK 21)` — blocking semantics with async I/O under the hood
- `IOCP (Windows)` — Windows' mature completion-port-based async I/O, analogous to io_uring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Submit I/O, do other work, get notified   │
│              │ when complete — no thread blocked         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Non-blocking I/O still needs poll loops;  │
│ SOLVES       │ async I/O uses kernel completion events   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Kernel does the read/write + copy; you    │
│              │ just submit and collect results           │
├──────────:───┼───────────────────────────────────────────┤
│ USE WHEN     │ Max I/O throughput; storage-heavy apps;   │
│              │ NVMe/DPDK-level performance needed        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple services; when security policy     │
│              │ blocks io_uring in containers             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Max throughput + zero blocking vs buffer  │
│              │ lifetime complexity + security surface    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Place your order and get a text when     │
│              │  it's ready — never wait at the counter"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ io_uring → Reactive Programming → DPDK    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `io_uring` with `IORING_SETUP_SQPOLL` eliminates all syscall overhead by having a kernel thread poll the submission queue. This kernel polling thread runs at high priority and consumes a dedicated CPU core. For a storage-heavy service running on a 4-core VM, what is the performance break-even point (in I/O operations per second) at which dedicating one core to SQPOLL becomes worthwhile — and how does this calculation change if the VM is on a shared host with CPU steal time?

**Q2.** Java's virtual threads (JDK 21) use blocking I/O syntax (`socket.read()`) but internally use non-blocking I/O or io_uring to avoid blocking OS threads. When a virtual thread calls `socket.read()` and no data is available, trace the exact sequence of JVM and OS interactions until the data arrives and the virtual thread resumes. At what point is an OS thread truly released, and what prevents the virtual thread's stack from being collected during the wait?
