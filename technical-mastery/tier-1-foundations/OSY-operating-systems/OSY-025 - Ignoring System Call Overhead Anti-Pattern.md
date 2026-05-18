---
id: OSY-025
title: Ignoring System Call Overhead Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-008
used_by: OSY-039
related: OSY-008, OSY-039, OSY-068
tags:
  - anti-pattern
  - system-calls
  - performance
  - overhead
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/osy/syscall-overhead-anti-pattern/
---

## TL;DR

Each system call crosses the user/kernel boundary
(~100-300ns). Calling syscalls in tight loops or per-item
in high-throughput code creates invisible performance
bottlenecks. Fix: batch I/O operations and minimize
per-item syscall frequency.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-025 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | anti-pattern, syscall overhead, batching |
| **Prerequisites** | OSY-008 |

---

### The Problem

```
User space -> Kernel space transition costs:
  - Save CPU registers, switch stack pointer
  - Change CPU privilege level (Ring 3 -> Ring 0)
  - Validate syscall parameters
  - Execute kernel function
  - Reverse transition back

Per-syscall cost: ~100-300ns (KPTI-patched kernel)
                 ~500ns-1us for I/O syscalls

At 1 million operations/second:
  1,000,000 * 300ns = 300ms of PURE syscall overhead
  (before the actual I/O work!)
```

---

### Anti-Pattern: Syscall Per Item

```java
// BAD: write() syscall for every log line
public class BadLogger {
    private final FileOutputStream out;
    
    public void log(String message) {
        try {
            // Each write() = 1 system call = 100-300ns
            // At 100K logs/sec = 10-30ms pure syscall overhead
            out.write((message + "\n").getBytes());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

// Measured: ~200,000 logs/sec maximum throughput
// Bottleneck: write() syscall per message
```

```java
// GOOD: buffered writes, fewer syscalls
public class GoodLogger {
    // BufferedOutputStream batches writes internally
    // Flushes to kernel when buffer (8KB default) is full
    // Batch of ~100 log lines per write() syscall
    private final BufferedOutputStream out;
    
    public GoodLogger(FileOutputStream raw) {
        // 64KB buffer = fewer syscalls, more throughput
        this.out = new BufferedOutputStream(raw, 65536);
    }
    
    public void log(String message) {
        try {
            // Writes to buffer in user space (very fast)
            // Syscall only when buffer fills (rare)
            out.write((message + "\n").getBytes());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public void flush() throws IOException {
        out.flush(); // Force syscall to write remaining buffer
    }
}

// Measured: ~2,000,000 logs/sec throughput
// 10x improvement from batching
```

---

### Where This Anti-Pattern Appears

```
1. File I/O: per-record write() without buffering
2. Network I/O: per-packet send() without batching
3. Database: N+1 query problem (1 query per item)
4. Redis: per-key GET in a loop instead of pipeline
5. Java NIO: reading 1 byte at a time from Channel

Redis pipeline example:
// BAD: 1000 round trips, 1000 SET syscalls
for (String key : keys) {
    jedis.set(key, value); // network + kernel syscall
}
// Each set: ~100us for network roundtrip

// GOOD: 1 pipeline, ~1-2 kernel calls for the batch
Pipeline pipe = jedis.pipelined();
for (String key : keys) {
    pipe.set(key, value);   // batched in user space
}
pipe.sync();  // 1 network write, 1 read
// Typical speedup: 10-100x
```

---

### Diagnosis

```bash
# Check how many system calls per second a process makes
strace -c -p <PID>
# After 30 seconds, Ctrl+C:
# % time   seconds  usecs/call  calls  syscall
# 60.0    30.000      300     100000  write
# Seeing 100K write() calls = classic per-item anti-pattern

# Confirm with vmstat
vmstat 1 | awk '{print $15}'  # system calls per second (in column)
# Or:
cat /proc/PID/status | grep voluntary_ctxt_switches
# High voluntary context switches = lots of blocking I/O syscalls
```

---

### Textbook Definition

System call overhead anti-pattern occurs when code
invokes operating system calls per-item in high-frequency
loops instead of batching operations. Each syscall incurs
mode switch cost (user to kernel and back). Mitigation:
buffers, batch APIs, pipeline patterns.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "System calls are fast so per-item doesn't matter" | ~100-300ns each. At 1M items/sec = 100-300ms of syscall overhead per second. At 10M items/sec = 1-3 full CPU seconds wasted on mode switching |
| "Buffering only matters for disk I/O" | Network sockets, pipes, and IPC also pay per-call mode switch cost. Redis pipeline, TCP_CORK, and io_uring batch exist for the same reason |

---

### Mastery Checklist

- [ ] Knows per-syscall cost range (~100-300ns on modern hardware)
- [ ] Recognizes per-item I/O in tight loops as the anti-pattern
- [ ] Can apply BufferedOutputStream / pipelining as the fix
- [ ] Can use strace -c to measure syscall frequency
