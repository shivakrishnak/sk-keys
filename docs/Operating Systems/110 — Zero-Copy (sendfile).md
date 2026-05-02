---
layout: default
title: "Zero-Copy (sendfile)"
parent: "Operating Systems"
nav_order: 110
permalink: /operating-systems/zero-copy-sendfile/
number: "0110"
category: Operating Systems
difficulty: ★★★
depends_on: Page Cache, File Descriptor, epoll / kqueue, Virtual Memory
used_by: Kafka, Nginx, Netty, HTTP file serving
related: DMA, mmap, splice, io_uring, sendfile
tags:
  - os
  - networking
  - performance
  - internals
  - deep-dive
---

# 110 — Zero-Copy (sendfile)

⚡ TL;DR — Zero-copy eliminates redundant memory copies between kernel and user space when serving files over a network; `sendfile()` moves file pages directly from page cache to socket buffer without touching user memory.

| #0110           | Category: Operating Systems                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Page Cache, File Descriptor, epoll / kqueue, Virtual Memory |                 |
| **Used by:**    | Kafka, Nginx, Netty, HTTP file serving                      |                 |
| **Related:**    | DMA, mmap, splice, io_uring, sendfile                       |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
To serve a file over a network with traditional I/O: `read()` the file into a user-space buffer, then `write()` to the socket. This requires 4 data copies: (1) disk → kernel page cache, (2) page cache → user buffer, (3) user buffer → kernel socket buffer, (4) socket buffer → NIC. Copies 2 and 3 cross the kernel/user boundary — they're pure overhead. For a file-serving application, this means 2× unnecessary copies for 100% of traffic.

THE BREAKING POINT:
In 2003, Kafka's designers ran benchmarks: at 600MB/s throughput (their SSD speed), traditional `read`/`write` consumed one full CPU core doing memory copies. With zero-copy `sendfile`, that CPU overhead dropped by 65%. At modern NVMe speeds (7GB/s), the waste is even more extreme — the copies become the bottleneck, not the storage.

THE INVENTION MOMENT:
`sendfile()` was introduced in Linux 2.2 (1999) and was used by the Solaris kernel even earlier. The insight: the OS already has the file data in the page cache AND controls the socket buffers — there's no reason to route the data through user space. The kernel can move it internally.

---

### 📘 Textbook Definition

**Zero-copy** refers to OS mechanisms that transfer data between I/O devices without requiring the CPU to copy data through user-space buffers. The canonical Linux mechanism is `sendfile(out_sock_fd, in_file_fd, &offset, count)`, which instructs the kernel to transfer `count` bytes from a file to a socket starting at `offset`, using a kernel-internal path that avoids copying to user space. In "true" zero-copy with hardware support (DMA gather), even the copy from page cache to the NIC's DMA buffer is eliminated: the NIC reads directly from page cache pages, achieving literally zero CPU copies for the data path.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
sendfile tells the kernel "move file data to this socket yourself" — data never touches user-space memory.

**One analogy:**

> Traditional: you're a relay runner — the file data runs from the disk to a staging area (user buffer), and you carry it to the finish line (network). Zero-copy: the track official (kernel) signals the file data to run directly from start to finish — you're bypassed.

**One insight:**
Every copy is CPU time and memory bandwidth consumed. At 10 Gbps, copying 1.25 GB/s through user space consumes ~50% of a CPU core just for memory bandwidth. `sendfile` moves that cost from CPU to the memory bus with zero user-space involvement.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Data must traverse a path; the question is how many copies that path requires.
2. The kernel controls both the source (page cache) and destination (socket buffer/NIC).
3. Any copy through user space is avoidable if both endpoints are kernel-controlled.

DERIVED DESIGN:
**Traditional path (4 copies, 2 context switches):**

```
disk → [DMA] → page cache
page cache → [CPU copy] → user buffer       ← copy 1 (kernel→user)
user buffer → [CPU copy] → socket buffer    ← copy 2 (user→kernel)
socket buffer → [DMA] → NIC
```

**sendfile path (2 copies, 0 user-space context switches):**

```
disk → [DMA] → page cache
page cache → [CPU copy] → socket buffer     ← copy 1 (kernel internal)
socket buffer → [DMA] → NIC
```

**sendfile + scatter-gather DMA ("true zero-copy", Linux 2.4+):**

```
disk → [DMA] → page cache
page cache → [DMA descriptor] → NIC         ← 0 CPU copies
```

Only the file descriptor (pointer + length) is sent to the NIC; the NIC DMA-reads directly from page cache pages. Requires NIC with `SG_IO` scatter-gather capability.

THE TRADE-OFFS:
Gain: Up to 65% reduction in CPU usage for file serving; higher throughput per CPU; less memory bandwidth consumed.
Cost: Data cannot be modified in flight (no TLS without additional mechanism); requires both source and destination to be kernel-managed; `mmap`+`write` is more flexible but has different trade-offs; sendfile is Linux/Unix specific (no Windows sendfile equivalent — use `TransmitFile`).

---

### 🧪 Thought Experiment

SETUP:
Serve 1 million 10KB files in one second (10 GB/s) on a server with a 10 Gbps NIC and NVMe SSD.

TRADITIONAL read/write:

- 10 GB/s of data × 4 copies = 40 GB/s memory bandwidth required
- Modern CPU: ~50 GB/s peak memory bandwidth → 80% consumed just for copies
- No CPU left for request parsing, headers, connection management

SENDFILE (with scatter-gather DMA):

- 10 GB/s of data × 0 CPU copies = ~0 GB/s memory bandwidth for data
- NIC DMA handles data movement
- CPU free for request handling, TLS, etc.
- Same 10 Gbps throughput achievable at < 20% CPU

THE INSIGHT:
Zero-copy is not about speed of individual transfers — it's about keeping the data path off the CPU, leaving CPU cycles for actual application logic.

---

### 🧠 Mental Model / Analogy

> Traditional I/O: a warehouse worker reads each item off a truck (disk read to page cache), writes it in a log book (copies to user buffer), then carries it to the shipping dock (copies to socket buffer), where another worker loads it on the delivery truck (DMA to NIC). Three handoffs, two involving the log book clerk (user space) who adds no value.

> sendfile: the warehouse supervisor (kernel) directly relabels the delivery truck's manifest. Goods go from receiving dock to delivery truck without anyone opening boxes. The log book clerk (user space) is never involved.

> True zero-copy (scatter-gather DMA): the delivery truck (NIC) is given the dock locations (page cache addresses) and loads itself.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Normally, to send a file over the network, the OS copies it twice through memory — once to your program, once back to the network. `sendfile` skips your program entirely — the OS handles everything internally. It's faster and uses less CPU.

**Level 2 — How to use it (junior developer):**
In Java, `FileChannel.transferTo()` uses `sendfile` on Linux and `TransmitFile` on Windows. In Kotlin/JVM, Spring's `ResourceHttpRequestHandler` does this automatically for static content. In Nginx, `sendfile on;` is the config directive. Kafka uses `FileChannel.transferTo()` for message delivery — the key reason Kafka is faster than a simple log reader for consumers.

**Level 3 — How it works (mid-level engineer):**
`sendfile(out_fd, in_fd, &offset, count)` is a syscall. Kernel: 1) checks page cache for in_fd pages (reads from disk if missed), 2) calls `splice_from_file()` to create a pipe-based internal buffer that references (not copies) the page cache pages, 3) calls `tcp_sendmsg()` on the socket to DMA those references to the NIC. With `MSG_ZEROCOPY` flag on the socket (Linux 4.14+), even TCP retransmit uses the original page cache pages. Without scatter-gather: one CPU copy from page cache to socket SKB. With scatter-gather (most modern NICs): zero CPU copies.

**Level 4 — Why it was designed this way (senior/staff):**
`sendfile` was a pragmatic API addition — the kernel already had both endpoints but the POSIX model had no cross-descriptor operation. The challenge is TLS: `sendfile` bypasses user space where TLS encryption normally happens. Kernel TLS (`kTLS`, Linux 4.13+) solves this: TLS state is pushed into the kernel, and `sendfile` can encrypt in-place at the kernel layer. Nginx supports `ssl_sendfile on;` using kTLS. This is the frontier of zero-copy in production: `sendfile` → `kTLS` → scatter-gather DMA = zero CPU involvement in serving encrypted static content.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│      TRADITIONAL read/write vs sendfile                │
├────────────────────────────────────────────────────────┤
│  Traditional:                                          │
│  read(file_fd, user_buf, n)                            │
│    disk ─[DMA]→ page_cache ─[CPU]→ user_buf            │
│  write(sock_fd, user_buf, n)                           │
│    user_buf ─[CPU]→ socket_buf ─[DMA]→ NIC             │
│                                                        │
│  Copies: 4 (2 DMA, 2 CPU)  Context switches: 4        │
│                                                        │
├────────────────────────────────────────────────────────┤
│  sendfile:                                             │
│  sendfile(sock_fd, file_fd, &off, n)                   │
│    disk ─[DMA]→ page_cache ─[CPU]→ socket_buf          │
│                             ─[DMA]→ NIC                │
│                                                        │
│  Copies: 3 (2 DMA, 1 CPU)  Context switches: 2        │
│                                                        │
├────────────────────────────────────────────────────────┤
│  sendfile + scatter-gather DMA:                        │
│  sendfile(sock_fd, file_fd, &off, n)                   │
│    disk ─[DMA]→ page_cache                             │
│              └─[DMA descriptor]→ NIC                  │
│                                                        │
│  Copies: 2 (2 DMA, 0 CPU)  Context switches: 2        │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

KAFKA CONSUMER FLOW (zero-copy):

```
Consumer fetches messages for topic partition
  → Broker: sendfile(socket_fd, log_file_fd, &offset, batch_size)
  → Kernel: page cache hit (log pages cached from last write)
  → NIC scatter-gather: read page cache pages directly
  → TCP/IP headers added by kernel
  → Data sent to consumer NIC
  → Consumer: receives bytes directly in receive buffer
  → 0 copies in broker user space
  → Broker CPU: parses request + builds sendfile args only
```

FAILURE PATH:

```
sendfile with TLS (without kTLS):
  → Can't use sendfile for encrypted connections
  → Must fall back to read() + SSL_write() (2 extra copies)
  → Solution: kTLS (Kernel TLS) — push TLS state to kernel
  → Then sendfile works for TLS too
```

---

### 💻 Code Example

Example 1 — Java FileChannel.transferTo (zero-copy):

```java
// BAD: traditional copy — data touches user space
try (FileInputStream fis = new FileInputStream(file);
     OutputStream os = socket.getOutputStream()) {
    byte[] buf = new byte[8192];
    int n;
    while ((n = fis.read(buf)) != -1) {
        os.write(buf, 0, n);  // User-space copy
    }
}

// GOOD: zero-copy via FileChannel.transferTo
try (FileChannel src = FileChannel.open(file.toPath(), READ);
     WritableByteChannel dest = Channels.newChannel(
                                    socket.getOutputStream())) {
    long position = 0;
    long remaining = src.size();
    while (remaining > 0) {
        long transferred = src.transferTo(position, remaining, dest);
        position += transferred;
        remaining -= transferred;
    }
    // Uses sendfile() on Linux, TransmitFile on Windows
}
```

Example 2 — Nginx zero-copy config:

```nginx
http {
    sendfile on;          # Use sendfile() syscall
    tcp_nopush on;        # Batch small headers + first part
    tcp_nodelay on;       # Disable Nagle for interactive streams
    # Combined: headers bundled with first sendfile chunk
    # then switch to tcp_nodelay for streaming

    server {
        location /static/ {
            root /var/www;
            # Nginx serves files using sendfile — zero user-space copies
        }
    }
}
```

Example 3 — C sendfile:

```c
#include <sys/sendfile.h>

void serve_file(int sock_fd, const char *path) {
    int file_fd = open(path, O_RDONLY);
    if (file_fd < 0) { perror("open"); return; }

    struct stat st;
    fstat(file_fd, &st);
    off_t offset = 0;
    ssize_t remaining = st.st_size;

    // Build HTTP headers (these go through user space — small and OK)
    char headers[256];
    int hlen = snprintf(headers, sizeof(headers),
        "HTTP/1.1 200 OK\r\nContent-Length: %ld\r\n\r\n",
        st.st_size);
    send(sock_fd, headers, hlen, 0);

    // File body: zero-copy sendfile
    while (remaining > 0) {
        ssize_t sent = sendfile(sock_fd, file_fd, &offset, remaining);
        if (sent <= 0) break;  // EAGAIN: retry or use epoll
        remaining -= sent;
    }
    close(file_fd);
}
```

Example 4 — Check if sendfile is being used:

```bash
# Trace sendfile syscalls in Kafka broker
strace -e trace=sendfile64 -p $(pgrep -f kafka) 2>&1 | head -20
# Should see: sendfile64(sock_fd, file_fd, NULL, count) = bytes

# Nginx sendfile confirmation
strace -e trace=sendfile -p $(pgrep nginx) 2>&1 | head -20
```

---

### ⚖️ Comparison Table

| Technique         | CPU Copies | User-Space | Modifiable | TLS       | Use For                           |
| ----------------- | ---------- | ---------- | ---------- | --------- | --------------------------------- |
| `read`+`write`    | 2          | Yes        | Yes        | Yes       | General I/O with transforms       |
| `mmap`+`write`    | 1          | Virtual    | Yes        | Yes       | Random-access + write flexibility |
| **`sendfile`**    | 0–1        | No         | No         | kTLS only | Static file serving, Kafka        |
| `splice`          | 0–1        | No         | No         | No        | Pipe-to-socket or pipe-to-pipe    |
| `io_uring splice` | 0          | No         | No         | No        | Async zero-copy chains            |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| "sendfile is always zero CPU copies" | Without scatter-gather DMA NIC support, one CPU copy (page cache → socket buffer) remains; true zero-copy needs modern NIC hardware |
| "mmap is zero-copy"                  | mmap reduces user-space copies but still requires a copy to the socket buffer; it's not zero-copy for network sends                 |
| "sendfile works with SSL/TLS"        | Standard sendfile doesn't go through user-space OpenSSL; kTLS + sendfile works for TLS but requires kernel TLS support              |
| "sendfile is only for files"         | `splice()` is the more general form — works between any two fds backed by a pipe                                                    |
| "Java NIO always uses sendfile"      | FileChannel.transferTo() attempts sendfile but falls back to read+write if the OS or configuration doesn't support it               |

---

### 🚨 Failure Modes & Diagnosis

**1. sendfile Silently Falling Back to read/write in Java**

Symptom: Java file server has high CPU despite using `FileChannel.transferTo()`; profiler shows time in `read`/`write` syscalls.

Root Cause: `transferTo` falls back if: destination is not a `SocketChannel` (e.g., `SSLEngine` wrapping), file is on network filesystem (NFS), or OS sendfile unsupported for the file type.

Diagnostic:

```bash
strace -e trace=sendfile,sendfile64,read,write -p <PID> 2>&1 | head -50
# If you see read+write instead of sendfile64, it's fallen back
```

Fix: Ensure destination is a `SocketChannel` directly (not wrapped). For TLS, use Netty with OpenSSL + zero-copy TLS or upgrade to kernel with kTLS.

---

**2. sendfile with O_DIRECT Conflict**

Symptom: `sendfile()` returns `EINVAL` or falls back to copy path.

Root Cause: Source file was opened with `O_DIRECT`; sendfile requires page-cache-backed files.

Diagnostic:

```bash
# Check open flags on fd
cat /proc/<PID>/fdinfo/<fd>
# Look for: flags: 0100002 (O_RDONLY|O_DIRECT = 0x8002)
```

Fix: Remove O_DIRECT from files used with sendfile; use O_DIRECT only for database buffer pool fds.

---

**3. TLS Throughput Bottleneck**

Symptom: HTTPS file server saturates CPU at ~2 Gbps on a 10 Gbps NIC; non-HTTPS uses < 5% CPU for same traffic.

Root Cause: TLS requires user-space encrypt/decrypt; sendfile can't be used; every HTTPS byte goes through user space twice.

Diagnostic:

```bash
perf top -p <nginx_pid>
# High time in: SSL_write, EVP_EncryptUpdate = TLS copy bottleneck
```

Fix: Enable kTLS in kernel (5.2+) + Nginx with `ssl_sendfile on` + OpenSSL 3.0 kTLS provider.

Prevention: Benchmark TLS throughput during capacity planning; plan for 3–5× more CPU for TLS vs plaintext at line rate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Page Cache` — sendfile moves data from page cache to socket; understanding what page cache is is essential
- `File Descriptor` — sendfile takes two fds (file and socket) as arguments
- `epoll / kqueue` — typically used with sendfile in non-blocking I/O event loops

**Builds On This (learn these next):**

- `Async I/O` — io_uring's splice operations extend zero-copy to the async model
- `Kafka internals` — Kafka's consumer throughput advantage is entirely based on sendfile
- `Netty` — uses FileChannel.transferTo (sendfile) for static content in its HTTP server

**Alternatives / Comparisons:**

- `mmap + write` — alternative: maps file pages to virtual address space then writes; one less copy than read+write but more complex and not zero-copy
- `splice` — more general form of sendfile: works between any two fds via an intermediate pipe
- `io_uring IORING_OP_SPLICE` — async splice; avoids even the splice syscall overhead

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ OS mechanism to send file data to network │
│              │ without copying through user space        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ read+write requires 2 CPU copies of       │
│ SOLVES       │ every byte; zero-copy eliminates them     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Kernel controls both page cache and       │
│              │ socket buffer — no user space needed      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Serving static files, Kafka log shipping, │
│              │ any high-throughput file-to-network path  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data must be transformed (encrypt,        │
│              │ compress) before sending (except kTLS)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Throughput + CPU efficiency vs            │
│              │ no in-flight modification of data         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell the kernel to move file → socket;   │
│              │  your code never touches the bytes"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ kTLS → io_uring splice → Kafka internals  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Apache Kafka guarantees that producers writing to a topic are isolated from consumer reads — no consumer can read bytes not yet acknowledged. Kafka's consumer reads use `FileChannel.transferTo()` (sendfile) reading from the same log file the producer is appending to. If the producer appends 1MB while a consumer's `sendfile` is in flight for an offset range just before that 1MB, what happens at the OS level? Does sendfile "see" the new data, and why? What kernel guarantee prevents a consumer from reading a partial message?

**Q2.** Consider a CDN edge node serving 100,000 small (1–10KB) files per second over HTTPS using kTLS + sendfile. Each file has a unique TLS session. How does kTLS manage per-session TLS state in the kernel for 100,000 concurrent sessions? What is the memory overhead per session, and at what point does the number of concurrent kTLS sessions become a bottleneck? Compare this to a user-space TLS approach (OpenSSL per-thread) to identify the cross-over point.
