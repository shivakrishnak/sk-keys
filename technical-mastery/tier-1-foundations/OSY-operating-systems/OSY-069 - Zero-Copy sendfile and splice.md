---
id: OSY-069
title: Zero-Copy sendfile and splice
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-013, OSY-015, OSY-056, OSY-068
used_by: []
related: OSY-056, OSY-068, OSY-096
tags:
  - zero-copy
  - sendfile
  - splice
  - DMA
  - Kafka
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 69
permalink: /technical-mastery/osy/zero-copy-sendfile-splice/
---

## TL;DR

Zero-copy transfers data between file and socket without
copying it through userspace. `sendfile()` sends a file
to a socket entirely in-kernel (2 DMA copies, 0 CPU
copies). Kafka's throughput at scale depends on sendfile
for consumer reads. Java's `transferTo()` calls sendfile
on Linux. DMA: Direct Memory Access allows hardware to
copy data without CPU involvement.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-069 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | zero-copy, sendfile, splice, DMA, FileChannel.transferTo |
| **Prerequisites** | OSY-013, OSY-015, OSY-056, OSY-068 |

---

### Traditional Copy vs Zero-Copy

```
Traditional: read() + write() (4 copies, 2 context switches)
  
  User application:
    fd = open("file.txt")
    buf = new byte[65536]
    n = read(fd, buf)      // syscall 1 (user -> kernel)
    write(socket, buf, n)  // syscall 2 (user -> kernel)
    
  Under the hood:
    Copy 1: Disk -> DMA -> Kernel page cache     (hardware DMA)
    Copy 2: Kernel page cache -> user buffer      (CPU copy)
    [context switch: kernel -> user]
    Copy 3: user buffer -> socket kernel buffer   (CPU copy)
    Copy 4: Socket buffer -> NIC tx buffer        (hardware DMA)
    
  Cost: 4 copies, 2 context switches, 2 syscalls
  CPU involvement: copies 2 and 3 (memcpy in kernel)
  
sendfile() (Linux 2.2+): 2 copies, 0 CPU copies
  
  sendfile(socket, file_fd, offset, length);
  
  Under the hood:
    Copy 1: Disk -> DMA -> Kernel page cache     (hardware DMA)
    Copy 2: Kernel page cache -> NIC tx buffer   (hardware DMA or copy)
    [no user-space involvement!]
    
  sendfile() with scatter-gather DMA (NIC supports it):
    NIC reads directly from page cache via DMA gather
    Only ONE DMA pass: disk -> page cache -> NIC
    True zero-copy: no CPU data movement at all
    
  Cost: 2 DMA copies (hardware), 0 CPU copies, 1 syscall
  CPU: sets up DMA descriptors only; no data touching
```

---

### Java transferTo() and Kafka

```java
// Java FileChannel.transferTo() -> sendfile() on Linux
public class ZeroCopyFileServer {
    public static void sendFile(Path filePath,
                                 SocketChannel socket) throws IOException {
        try (FileChannel fileChannel = FileChannel.open(filePath)) {
            long size = fileChannel.size();
            long position = 0;
            
            // Loop because transferTo may not transfer all bytes at once
            while (position < size) {
                long transferred = fileChannel.transferTo(
                    position, size - position, socket);
                if (transferred <= 0) break;
                position += transferred;
            }
        }
        // On Linux: this compiles to sendfile() syscall
        // No data passes through JVM heap!
        // No byte[] buffer allocated
        // CPU: near-zero for data path
    }
}

// Kafka consumer read flow (sendfile is the key):
//
// Producer:
//   Write to Kafka topic -> stored in log segment file
//
// Consumer fetch:
//   1. Fetch request arrives (via network)
//   2. Kafka: look up log segment file + offset
//   3. sendfile(socket, log_fd, offset, length)
//   4. Kernel: page cache -> NIC (zero CPU copy)
//   5. Consumer receives bytes
//
// Why Kafka throughput scales:
//   1. Sequential writes (appended log files -> page cache warm)
//   2. sendfile() for reads (no deserialization, no user-space copy)
//   3. Batching (many messages per sendfile call)
//
// Without sendfile:
//   Kafka would read bytes -> Java heap -> write to socket
//   At 1GB/s network: CPU would be 100% just copying data
//
// With sendfile:
//   Kafka achieves near-NIC-line-rate throughput on reads
//   CPU usage remains low
```

---

### splice() and tee()

```
splice() (Linux 2.6.17): zero-copy between two kernel objects

  splice(fd_in, off_in, fd_out, off_out, length, flags);
  
  Transfers data: pipe -> socket, socket -> pipe, pipe -> pipe
  (sendfile is restricted to file -> socket)
  
  Example: proxy server zero-copy
    Client request arrives on socket_in
    Forward to backend: splice(socket_in, pipe_fd[1]) read side
                        splice(pipe_fd[0], socket_out) write side
    No data in user-space!
    
  The pipe is used as a "kernel buffer" connector
  
tee() (Linux 2.6.17): duplicate pipe data without consuming
  
  tee(pipe_fd[0], pipe_fd2[1], length, flags)
  Copies pipe data to another pipe without consuming original
  
  Use case: T-split a network stream for logging:
    Original stream -> tee -> logger pipe
                    -> unchanged -> processor
    
  All in-kernel: no user-space copies

io_uring (Linux 5.1+):
  Submits I/O via shared memory ring buffer (no syscall per I/O)
  Supports zero-copy splice-like operations
  Designed for: ultra-high IOPS NVMe workloads
  Java support: io_uring is used by Netty 5.x (planned)
```

---

### Measuring Zero-Copy Benefits

```bash
# Compare throughput: cp vs sendfile approach

# Method 1: cp (read() + write() internally)
time cp large_file /dev/null
# Baseline: standard 4-copy approach

# Method 2: sendfile approach (cat uses read/write, not sendfile)
# Use dd with direct I/O:
time dd if=large_file bs=1M | nc -q 0 localhost 12345

# Method 3: strace to observe sendfile usage:
strace -e sendfile,read,write java SendFileTest 2>&1 | grep -c sendfile
# Count of sendfile calls = actual zero-copy operations

# Monitor CPU during transfer:
# Traditional: iostat shows both iowait AND usr CPU
# sendfile: iostat shows iowait only (no usr CPU for data copy)
iostat 1

# Network card zero-copy check (GRO/GSO offload):
ethtool -k eth0 | grep scatter-gather
# If "scatter-gather: on": NIC supports gather DMA
# sendfile + scatter-gather = TRUE zero-copy (1 DMA pass)
# sendfile without scatter-gather: 2 DMA + 1 kernel buffer copy
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "FileChannel.transferTo() always uses sendfile()" | `transferTo()` calls `sendfile()` on Linux when transferring to a socket. When transferring to another FileChannel (file-to-file), it may use sendfile or a fallback implementation. On Windows, it uses `TransmitFile()`. On macOS, it uses `sendfile()` (different signature). Always verify with strace on the target OS |
| "Zero-copy means no CPU usage during transfer" | Zero-copy means no CPU for DATA COPYING. CPU is still needed for: setting up DMA descriptors, network stack processing (TCP checksums, etc.), I/O scheduler operations, and system call overhead. For NIC offload (checksum, segmentation offload), the NIC handles more, reducing CPU further |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Traditional read+write | 4 copies: disk->page cache->user->socket buf->NIC |
| sendfile() | 2 DMA copies; 0 CPU copies; 1 syscall |
| Java API | `FileChannel.transferTo()` -> sendfile on Linux |
| Kafka zero-copy | Consumer reads use transferTo = sendfile |
| splice() | Zero-copy between two kernel objects via pipe |
| scatter-gather NIC | TRUE zero-copy: 1 DMA pass disk -> NIC directly |
