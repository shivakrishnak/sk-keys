---
id: LNX-082
title: "System Call Interface (syscall table, strace)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-022, LNX-011
used_by: LNX-078, LNX-087, LNX-073
related: LNX-022, LNX-078, LNX-073, LNX-087
tags: [syscall, strace, system-call-table, vdso, libc, glibc, kernel-boundary, ptrace, syscall-number, interrupt, sysenter, syscall-instruction, context-switch, user-space, kernel-space]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 82
permalink: /technical-mastery/lnx/system-call-interface/
---

## TL;DR

**System calls** are the ONLY official interface between user-space programs
and the Linux kernel. Every I/O, process creation, network operation, and
file access ultimately uses a syscall. ~400 syscalls on x86-64. Invoked via:
`syscall` instruction (x86-64), or through the vDSO (Virtual Dynamic Shared
Object - kernel-mapped pages for fast syscalls like `gettimeofday`). libc
(glibc/musl) wraps syscalls in C functions (`open()` -> `syscall(SYS_open, ...)`).
`strace` (`ptrace`-based) shows all syscalls a process makes with arguments
and return values. `perf trace` is lower-overhead. Syscall number tables:
`/usr/include/asm/unistd_64.h`. Each syscall: user-space -> SYSENTER/SYSCALL
instruction -> kernel mode -> sys_call_table[nr]() -> return.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-082 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | syscall, strace, system call interface, vDSO, kernel boundary, ptrace, syscall table, context switch |
| **Prerequisites** | LNX-022 (Process management), LNX-011 (Kernel internals) |

---

### The Problem This Solves

**Problem 1**: User-space programs must not have direct access to hardware
(disk, network, CPU registers). If any program could directly manipulate
hardware: one buggy program could corrupt another's memory, overwrite files,
intercept network traffic. The syscall interface is the CONTROLLED gate:
user programs request kernel services through a defined API, the kernel
validates all parameters, enforces permissions, and performs the operation.

**Problem 2**: Debugging an application behaving strangely - it seems to hang,
consume excessive I/O, or fail with cryptic errors. `strace -p PID` reveals
EXACTLY which system calls the application is making: is it spinning on
`futex` (lock contention)? Making thousands of `stat()` calls (filesystem scan)?
Failing with `EACCES` (permission denied)? `strace` gives kernel-level
visibility without modifying source code.

---

### Textbook Definition

**System call (syscall)**: A privileged request from user-space code to the
Linux kernel. The mechanism by which user programs request kernel services:
I/O, process management, memory management, networking. User code runs in
ring 3 (lowest privilege). Kernel runs in ring 0. The syscall instruction
atomically switches to ring 0 and calls the kernel handler.

**Syscall invocation on x86-64:**
1. Set syscall number in `rax` register
2. Set arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`
3. Execute `syscall` instruction
4. CPU: saves user state, switches to ring 0, jumps to `LSTAR` register (kernel entry point)
5. Kernel: dispatches to `sys_call_table[rax]`
6. Kernel executes the syscall handler
7. Return value in `rax`
8. `sysret` instruction: restore user state, return to ring 3

**vDSO (Virtual Dynamic Shared Object)**: A kernel-provided memory region
mapped into every process's address space. Contains optimized implementations
of frequently-called functions that DON'T require a full context switch (e.g.,
`gettimeofday`, `clock_gettime`, `time`). Reading from hardware TSC (timestamp
counter) without entering kernel mode = 10-50x faster than a full syscall.

**strace**: A debugging tool that intercepts and logs all system calls made
by a process. Uses `ptrace` (process tracing syscall) to intercept execution
at each syscall. High overhead (10-100x slowdown) due to ptrace's stop-resume
per-syscall mechanism.

---

### Understand It in 30 Seconds

```bash
# === strace basics ===

# Trace syscalls of a new command:
strace ls /tmp
# execve("/bin/ls", ["ls", "/tmp"], envp) = 0
# brk(NULL) = 0x55d3a8000000
# openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
# ...many library loading syscalls...
# openat(AT_FDCWD, "/tmp", O_RDONLY|O_DIRECTORY|O_CLOEXEC) = 3
# getdents64(3, /* 5 entries */, 32768) = 160
# write(1, "file1\nfile2\n", 12) = 12
# close(3) = 0
# exit_group(0) = ?

# Trace syscalls of a running process:
strace -p 1234    # attach to PID 1234

# Count syscall frequency (-c flag):
strace -c ls /tmp
# % time     seconds  usecs/call     calls    errors syscall
# 31.89    0.000567          39        14           openat
# 28.46    0.000506          36        14           close
# 15.47    0.000275          34         8           mmap
# ...

# Filter to specific syscalls:
strace -e trace=open,read,write,close ls /tmp
# Only shows file I/O syscalls

# Follow child processes (-f):
strace -f -e trace=execve bash -c "ls && echo done"
# Shows execve for each command in the pipeline

# Show timestamps:
strace -T -tt ls /tmp   # -tt: absolute timestamp, -T: syscall duration
# 10:00:00.123456 openat(AT_FDCWD, "/etc/ld.so.cache", ...) = 3 <0.000012>

# Write output to file:
strace -o /tmp/trace.log ls /tmp

# === Identify hung process ===
strace -p $(pidof stuck_process) -e trace=all
# Common findings:
# futex(0x..., FUTEX_WAIT, ...) = -1 ETIMEDOUT (deadlock/lock contention)
# read(5, ...) = ? (blocking on network socket - remote is slow)
# select(...) = 0 (timeout waiting for I/O)
# semop(...) = ? (waiting for semaphore)

# === perf trace (lower overhead than strace) ===
# Trace a command:
perf trace ls /tmp
# Uses tracepoints, not ptrace - much lower overhead

# Count syscalls over time:
perf trace -a --summary sleep 10   # all processes, 10 seconds

# === View syscall numbers ===
# x86-64 syscall table:
cat /usr/include/x86_64-linux-gnu/asm/unistd_64.h | head -30
# #define __NR_read 0
# #define __NR_write 1
# #define __NR_open 2
# #define __NR_close 3
# #define __NR_stat 4
# #define __NR_fstat 5
# ...
# #define __NR_clone 56
# #define __NR_fork 57
# ...

# Or use ausyscall:
ausyscall --dump | head -20
# 0    read
# 1    write
# 2    open
# ...

# === Make a raw syscall in Python ===
import ctypes
import os

# Direct syscall: write to stdout
libc = ctypes.CDLL(None)
SYS_write = 1   # syscall number for write on x86-64
libc.syscall(SYS_write, 1, b"hello from raw syscall\n", 22)

# === View vDSO ===
# Check vDSO mapping in process:
cat /proc/self/maps | grep vdso
# 7ffe8b3fe000-7ffe8b400000 r-xp 00000000 00:00 0  [vdso]

# The vDSO contains:
# clock_gettime, gettimeofday, time, getcpu
# Calling these from libc uses the vDSO mapping (no kernel crossing)
```

---

### First Principles

**The privilege ring boundary:**
```
x86-64 CPU privilege model:
  Ring 0 (kernel mode): full hardware access
    Can execute: privileged instructions (HLT, CLI, STI, IN/OUT)
    Can access: all physical memory, I/O ports, MSRs
    Used by: Linux kernel
  
  Ring 3 (user mode): restricted
    Cannot execute: privileged instructions (SIGILL or #GP fault)
    Cannot access: kernel memory (page table permissions)
    Cannot access: I/O ports directly
    Used by: all user-space programs

Syscall mechanism (x86-64, modern):
  
  User space (ring 3):
    1. Load syscall number into %rax (e.g., rax=1 for write)
    2. Load arguments: %rdi=fd, %rsi=buf, %rdx=count
    3. Execute SYSCALL instruction
       - Saves user %rip (return address) into %rcx
       - Saves user %rflags into %r11
       - Switches to ring 0
       - Jumps to address in IA32_LSTAR MSR (entry_SYSCALL_64)
  
  Kernel space (ring 0):
    4. entry_SYSCALL_64 (arch/x86/entry/entry_64.S):
       - Saves user registers (SAVE_REGS)
       - Validates syscall number
       - Calls: sys_call_table[rax](di, si, dx, r10, r8, r9)
       - e.g., rax=1 -> sys_write(fd, buf, count)
    
    5. sys_write():
       - Validates fd (is it open in current process?)
       - Validates buf pointer (is it in user memory?)
       - Copies count bytes from user buf to kernel buffer
       - Writes to file: VFS -> filesystem -> block layer -> disk
       - Returns bytes written (positive) or error (negative)
  
  Return to user (ring 3):
    6. SYSRET instruction:
       - Restores %rip from %rcx
       - Restores %rflags from %r11
       - Switches back to ring 3
    7. User code: return value is in %rax

Cost breakdown:
  Modern SYSCALL/SYSRET: ~100-300 ns (hardware saves/restores)
  + Kernel handler execution time (varies widely)
  + TLB flush (if kernel page table isolation - KPTI for Meltdown)
  With KPTI: ~200-600 ns just for the boundary crossing
  gettimeofday via vDSO: ~10-30 ns (no boundary crossing!)
  
  High-syscall-rate applications feel this:
    1M syscalls/second * 300ns = 300ms/s of overhead = 30% CPU at 1M/s
    Solutions: io_uring (batch syscalls), zero-copy APIs, vDSO for time

strace internals (ptrace):
  
  strace uses ptrace(PTRACE_SYSCALL) on the tracee process:
  1. strace calls ptrace(PTRACE_SYSCALL, child_pid, ...)
  2. Child runs until NEXT syscall entry
  3. Child stops (SIGTRAP delivered)
  4. strace reads syscall args via ptrace(PTRACE_GETREGS)
  5. strace prints "write(1, ..." entry
  6. strace calls ptrace(PTRACE_SYSCALL, child_pid, ...) again
  7. Child runs the syscall until syscall EXIT
  8. Child stops again
  9. strace reads return value (rax)
  10. strace prints "= 12" exit
  11. Repeat for every syscall
  
  Overhead: 2 stop-resume pairs per syscall = 2 context switches
  + 2 ptrace() calls from strace to kernel
  = 4 kernel crossings per application syscall
  
  10-100x overhead is expected
  perf trace: uses ring buffer (tracepoints), 1 kernel crossing per syscall
  BPF-based tracing: near-zero overhead, configurable sampling
```

---

### Thought Experiment

Diagnosing a performance problem with syscall tracing:

```bash
# Scenario: Python web app is slow on first request after idle
# Hypothesis: it's making many filesystem calls to find imports

# Step 1: Count syscalls:
strace -c -f -p $(pidof uvicorn) &
sleep 10
# After: check output - is openat dominant?

# Step 2: Trace file operations specifically:
strace -f -e trace=file -p $(pidof uvicorn) \
    -o /tmp/file_trace.log &
# Trigger a request in another terminal:
curl http://localhost:8000/api/health

# Examine the trace:
cat /tmp/file_trace.log | grep "ENOENT\|\.py" | head -30
# openat(AT_FDCWD, "/usr/lib/python3.11/site-packages/mymodule.py") = -1 ENOENT
# openat(AT_FDCWD, "/usr/local/lib/python3.11/site-packages/mymodule.py") = 3
# (Python trying multiple paths before finding the module)

# Step 3: Count unique file paths tried:
grep "openat" /tmp/file_trace.log | \
    grep -o '"[^"]*"' | sort | uniq -c | sort -rn | head -20

# Step 4: Profile syscall latency with perf:
perf trace --call-graph dwarf -p $(pidof uvicorn) -- sleep 5
# Shows which syscalls are slow

# Step 5: Root cause - Python searches sys.path for each import
# many ENOENT before finding the module = wasted time
# Fix: PYTHONPATH optimization, .pth files, or precompile with .pyc

# After fix: re-run strace -c to verify reduction in openat calls
```

---

### Mental Model / Analogy

```
System calls = customs checkpoints at a country border

Country = Linux kernel (ring 0)
  Has all the valuable resources:
  Disks, network, CPU registers, hardware

Foreign territory = user space (ring 3)
  Your program runs here
  Has NO direct access to anything valuable inside the country

Crossing the border = making a syscall:
  You fill out a customs form (set registers: rax=syscall#, rdi=arg1, ...)
  Execute the SYSCALL instruction = "I want to cross the border"
  
  Hardware checkpoint (CPU):
    Saves your documents (saves user registers)
    Validates your passport format (validates syscall number)
    Escorts you to the customs officer (jumps to kernel entry point)
  
  Customs officer (kernel):
    Reads your form (reads arguments from registers)
    Checks permissions ("do you have visa for this operation?")
    Performs the service (I/O, memory allocation, etc.)
    Stamps your form (sets return value in %rax)
    Escorts you back (SYSRET)
  
  Back in foreign territory:
    You have the result (read data, new file descriptor, etc.)
    Or you got rejected (negative return value = error)

strace = customs observer who logs every border crossing:
  Writes down: who crossed, what form they filled, what they got
  Overhead: the observer needs to stop each person, copy their forms
  (ptrace stop-resume = the observer physically stopping you each time)
  
vDSO = shared kiosk on the foreign side:
  For very common questions (what time is it?):
    Instead of crossing the border every time...
    The customs office maintains a kiosk ON YOUR SIDE
    Kiosk has a continuously updated clock (kernel updates vDSO)
    You read it directly (no border crossing = 10-50x faster)
  
  clock_gettime(), gettimeofday() use this kiosk (vDSO)
  For most programs: gettimeofday is NOT a real syscall!

io_uring = batch visa application:
  Instead of crossing the border for each file operation:
    Fill out multiple forms at once (submission queue)
    Hand them all to the officer at once (io_uring_enter)
    Pick up all results at once (completion queue)
    Massively reduces border crossings for I/O-intensive apps
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept of user space vs kernel space. Syscall as the boundary crossing.
`strace` for tracing. Common syscalls: `read`, `write`, `open`, `close`,
`fork`, `exec`. strace output format: name(args) = return.

**Level 2:**
`strace -c` for syscall counting. `-e trace=file` filtering. `-p` to attach
to process. `-f` for following forks. vDSO: fast time functions without syscall.
libc wrapping syscalls. Syscall numbers in `unistd_64.h`. Errno codes.

**Level 3:**
Privilege rings (ring 0 vs ring 3). SYSCALL/SYSRET instructions. Register
convention (rax=nr, rdi/rsi/rdx/r10/r8/r9=args). sys_call_table dispatch.
ptrace mechanism (how strace works). `perf trace` as lower-overhead alternative.
KPTI (Kernel Page Table Isolation) and its syscall overhead. Syscall cost
profiling.

**Level 4:**
Kernel entry path: `entry_SYSCALL_64` in `arch/x86/entry/entry_64.S`. SAVE_REGS
macro. Spectre/Meltdown syscall mitigations (retpoline, IBRS). io_uring: submitting
multiple I/O operations with 1-2 syscalls (submission queue, completion queue).
`seccomp-bpf` filters at syscall boundary. VSDO implementation: kernel updates
pages at fixed addresses, user reads without ring switch. Raw syscall in C
(`__NR_write` with inline assembly or `syscall()` libc function).

**Level 5:**
Adding a new syscall to the kernel (syscall table entry, `SYSCALL_DEFINE`
macro, architecture compat layer for 32-bit on 64-bit kernel). Syscall audit
framework: connecting syscalls to `auditd`. x32 ABI: 64-bit Linux with 32-bit
pointers. VDSO compilation: kernel builds the vDSO as a shared library, links
it into every process. Spectre variant 2 mitigation via retpoline in syscall
path. io_uring sqpoll (kernel thread polling submission queue - zero-syscall
I/O). Syscall table randomization (KASLR extension). `SYSCALL_DEFINE` vs
`COMPAT_SYSCALL_DEFINE` for 32-bit compat.

---

### Code Example

**BAD - syscall performance mistakes:**
```bash
# BAD 1: Calling stat() in a loop (common Python/Java pattern):
# Python equivalent:
# for filename in very_long_list:
#     if os.path.exists(filename):  # each = stat() syscall
#         process(filename)
# 10000 files = 10000 stat() syscalls

# Strace shows:
# stat("/data/file0001.txt", {...}) = 0
# stat("/data/file0002.txt", {...}) = 0  <- thousands of these
# stat("/data/file0003.txt", {...}) = -1 ENOENT

# GOOD: Batch with scandir or glob (1-2 syscalls for directory listing):
# Python:
# import os
# with os.scandir('/data') as entries:
#     for entry in entries:    # getdents64: batch of entries per syscall
#         if entry.is_file():
#             process(entry.name)

# BAD 2: Small write() calls in a loop:
# C pseudocode:
# for i in range(1000000):
#     write(fd, &byte, 1)   # 1M syscalls for 1MB!

# strace -c shows:
# write: 1000000 calls  <- 1M context switches

# GOOD: Buffer and write in larger chunks:
# write(fd, buffer, 65536)  # 1 syscall per 64KB = 15 calls for 1MB

# BAD 3: Frequent time checks via syscall:
# // C code that calls gettimeofday in a tight loop:
# while (true) {
#     struct timeval tv;
#     gettimeofday(&tv, NULL);  // each call = syscall if not vDSO-mapped
#     if (tv.tv_usec > threshold) do_something();
# }

# GOOD: gettimeofday uses vDSO on modern Linux (no syscall needed)
# Verify: strace -e trace=gettimeofday myapp
# If vDSO is working: gettimeofday does NOT appear in strace output!
# (because it never crosses the kernel boundary)
```

**GOOD - strace for production debugging:**
```bash
# Diagnose why a process is stuck (hung):
debug_stuck_process() {
    local pid=$1
    
    echo "=== Current syscall state ==="
    # Quick snapshot - what is the process doing RIGHT NOW:
    cat /proc/$pid/wchan     # kernel wait channel
    # futex_wait     <- stuck on mutex
    # pipe_read      <- waiting for pipe data
    # sk_wait_data   <- waiting for socket data
    # ep_poll        <- in epoll_wait (normal for event-driven app)
    
    echo ""
    echo "=== Open file descriptors ==="
    ls -la /proc/$pid/fd/ | head -20
    
    echo ""
    echo "=== Active connections ==="
    cat /proc/$pid/net/tcp6 | awk '
    NR>1 && $4=="01" {  # 01 = ESTABLISHED
        # Convert hex local/remote addresses
        print $2, "->", $3
    }' | head -10
    
    echo ""
    echo "=== Tracing syscalls for 5 seconds ==="
    timeout 5 strace -p "$pid" -e trace=all -T 2>&1 | tail -30
}

debug_stuck_process 1234

# Find which syscalls are taking the most time:
# Use perf trace (lower overhead):
perf trace -p 1234 --summary -- sleep 10 2>&1
# Syscall     calls  errors  total   min    avg    max
# futex        1234       0  5.432   0.001  0.004  2.100
# epoll_wait   567        0  0.234   0.001  0.000  0.050
# futex max=2.100ms is suspicious -> mutex contention!

# Trace only slow syscalls (>1ms):
perf trace -p 1234 -s 2>&1 | awk '$6>1.0'  # filter by syscall time
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "libc functions are syscalls" | libc WRAPS syscalls but often does much more. `printf()` is not a syscall - it buffers output in user-space and calls `write()` (the actual syscall) only when the buffer is full or flushed. `malloc()` uses `mmap()` or `brk()` syscalls for large allocations but manages a user-space heap for small allocations (no syscall per `malloc`). `fopen()`/`fread()` buffer I/O; only `open()`/`read()` are syscalls. A program calling `printf` 1000 times might only make 1-10 `write()` syscalls due to buffering. Use `strace` to see ACTUAL syscalls, not libc function calls. |
| "gettimeofday always makes a syscall" | On modern Linux (kernel 2.6+), `gettimeofday()` and `clock_gettime(CLOCK_REALTIME, ...)` use the VDSO (Virtual Dynamic Shared Object) and do NOT make a kernel crossing. The kernel maps a special memory region into every process. This region contains a fast implementation that reads the CPU's TSC (timestamp counter) and converts to wall clock time using kernel-maintained multipliers. No ring switch, no context switch - just a memory read + arithmetic. `strace` will NOT show `gettimeofday` if vDSO is active (because strace intercepts kernel crossings, and vDSO bypasses the kernel). To verify: run `strace -e trace=gettimeofday myprogram` - if it shows 0 calls, vDSO is working. |
| "strace is safe to use on production processes" | strace attaches via `ptrace` and stops the traced process on EVERY syscall (twice per syscall: at entry and exit). This creates 2 additional context switches per syscall. For I/O-intensive programs: if the application makes 100,000 syscalls/second, strace adds 200,000 context switches/second, potentially slowing the process by 10-100x. This can trigger timeouts, watchdogs, SLO violations, or cascade failures in production. SAFER ALTERNATIVES: `perf trace` (ring buffer, much lower overhead), `bpftrace` (eBPF, near-zero overhead for counting), `sysdig` (eBPF-based). If `strace` is required in production: use `-c` (count mode only, less overhead) or filter to specific syscalls with `-e trace=read,write`. |
| "All processes use the same syscall numbers" | Syscall numbers are ARCHITECTURE-SPECIFIC and can vary between 32-bit and 64-bit ABIs. On x86-64: `read=0, write=1, open=2`. On x86 (32-bit): `read=3, write=4, open=5`. On ARM64: `read=63, write=64, open=1024`. When writing seccomp filters: MUST specify the architecture and use the correct syscall numbers. The `__NR_*` constants in `unistd_64.h` are x86-64 specific. A seccomp filter written for x86-64 that uses raw numbers will fail on ARM64. This is why seccomp profiles (Docker, Kubernetes) specify the architecture list and seccomp tools abstract over architecture-specific numbers. |

---

### Failure Modes & Diagnosis

**Syscall-related debugging:**
```bash
# Symptom: "Operation not permitted" errors in application
# strace reveals which specific syscall is failing:
strace -e trace=all ./myapp 2>&1 | grep "EPERM\|EACCES\|ENOENT"
# ioctl(3, SIOCSIFFLAGS, ...) = -1 EPERM
# ^  trying to change network interface flags (needs CAP_NET_ADMIN)
# chown("/var/run/myapp.pid", 0, 0) = -1 EPERM
# ^  trying to chown a file to root (needs elevated privilege)

# Symptom: application hangs on startup
# strace with -T to show time per syscall:
strace -T -p $(pidof myapp) 2>&1 | awk '$NF > "0.100" {print}' | head -20
# ^  filter syscalls taking > 100ms

# Common findings:
# open("/etc/resolv.conf", ...) = ? (DNS lookup blocking)
# connect(3, {AF_INET, "10.0.0.1", 443}, ...) = ? (TCP connect blocking)
# read(4, ...) = ?   (waiting for socket data)

# Symptom: EMFILE (too many open files) error
# Find which process has most open files:
for pid in $(ls /proc | grep -E '^[0-9]+$'); do
    count=$(ls /proc/$pid/fd 2>/dev/null | wc -l)
    echo "$count $pid $(cat /proc/$pid/comm 2>/dev/null)"
done | sort -rn | head -10

# Find what files a specific process has open:
lsof -p 1234 | wc -l
lsof -p 1234 | grep -v "REG\|DIR" | head -20  # non-regular files (sockets etc.)

# Check file descriptor limit:
cat /proc/1234/limits | grep "open files"
# Max open files         1024         4096

# Increase limit:
ulimit -n 65536            # for current shell/children
sysctl -w fs.file-max=100000   # system-wide maximum
```

---

### Related Keywords

**Foundational:**
LNX-022 (Process management), LNX-011 (Kernel internals)

**Builds on this:**
LNX-078 (Seccomp - syscall filtering), LNX-087 (Kernel tracing), LNX-073 (eBPF)

**Related:**
LNX-083 (OOM killer), LNX-095 (CPU performance profiling)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `strace COMMAND` | Trace all syscalls of a command |
| `strace -p PID` | Attach to running process |
| `strace -c COMMAND` | Count syscall frequency |
| `strace -e trace=file` | Filter to file-related syscalls |
| `strace -T -tt` | Add timestamps and durations |
| `perf trace COMMAND` | Low-overhead syscall tracing |
| `cat /proc/PID/wchan` | Current kernel wait channel |
| `ausyscall --dump` | List all syscall names/numbers |
| `cat /proc/self/maps \| grep vdso` | View vDSO mapping |

**3 things to remember:**
1. System calls = only way for user-space to access kernel services; every I/O and process operation eventually calls a syscall
2. `strace -c` shows syscall frequency; `strace -T` shows duration; high-overhead tool - use `perf trace` in production
3. vDSO = kernel-mapped memory in every process; `gettimeofday` does NOT make a syscall (reads vDSO directly)

---

### Transferable Wisdom

The syscall interface pattern appears everywhere: Java JNI (Java Native Interface)
is the syscall equivalent for Java-to-C boundary - controlled crossing with
argument marshaling. WebAssembly WASI (WASI = WebAssembly System Interface)
is literally a redesigned syscall interface for WASM sandboxes. The Win32 API
is Windows' equivalent of libc wrapping NT native calls. gRPC is a network
"syscall interface" - a defined, versioned contract between services. The
principle: whenever you have a security or isolation boundary, you need a
controlled crossing with parameter validation. The cost of boundary crossing
(context switch, register save/restore, TLB flush) is the tax for isolation.
Engineers optimize by: batching (io_uring, Nagle algorithm), bypassing
(vDSO, DPDK, io_uring zero-copy), or reducing crossings (mmap instead of
read/write, zero-copy sendfile). `strace` literacy is a superpower for
debugging: many bugs that look like "application logic" are actually syscall
interactions (wrong errno, unexpected blocking, EMFILE from leak). The
`wchan` file in `/proc/PID/wchan` gives instant diagnosis of why a process
is sleeping in the kernel without attaching strace.

---

### The Surprising Truth

`gettimeofday()` - one of the most frequently called C functions in all of
computing - has not actually made a real system call on Linux since kernel
2.6 (2004). When glibc calls `gettimeofday()`, it reads from the vDSO -
a special shared memory region the kernel maintains - without ever entering
kernel mode. The kernel updates a shared page with the current time using
the CPU's TSC (timestamp counter). The C function does math on the shared
page. Total cost: 10-30ns. This is 10-20x faster than an actual syscall
(200-600ns including KPTI overhead). The funny consequence: `strace` CANNOT
see `gettimeofday` calls - because strace intercepts kernel crossings, and
vDSO calls don't cross the kernel boundary. Developers sometimes file "bugs"
saying "strace shows my app never calls gettimeofday but I'm calling it
in my code." The explanation - it's in the vDSO - surprises many. This
optimization is critical: a high-frequency trading system or a log
timestamping function might call `gettimeofday` millions of times per second.
At 2ns instead of 200ns: the difference is 200ms vs 2s of overhead per
second - a genuine 100x improvement for a completely transparent optimization.

---

### Mastery Checklist

- [ ] Can use `strace -c` to identify frequent syscalls and `strace -T` to find slow ones
- [ ] Can attach strace to a running process (`-p PID`) to diagnose hangs
- [ ] Understands privilege rings: why user code cannot directly access hardware
- [ ] Knows the register convention for x86-64 syscalls (rax=nr, rdi/rsi/rdx=args)
- [ ] Can use `cat /proc/PID/wchan` to quickly identify what syscall a blocked process is in

---

### Think About This

1. A microservice makes 50,000 small database calls per second. Each involves
   at minimum: `write()` to socket (send query), `read()` from socket (receive
   result). Calculate the syscall overhead: at 200ns per syscall with KPTI,
   what fraction of CPU time is just the kernel boundary crossings? How would
   you reduce this? (Consider: connection pooling, batching queries, using
   pipelining or multiplexing protocols.)

2. You're debugging a Python web application that is slow on cold start but
   fast after first request. `strace -c` shows 15,000 `stat()` calls and
   8,000 `openat()` calls during startup. Walk through: what Python is doing
   (module import path searching), which specific syscalls are involved, and
   how you'd diagnose exactly which modules are causing the most `stat()` calls.
   What optimization techniques would you apply?

3. Design a seccomp allowlist for a minimal HTTP server in C that:
   (a) listens on port 8080, (b) serves static files from /var/www/html/,
   (c) logs to /var/log/httpd/access.log. List the specific syscalls it needs
   (startup phase vs request serving phase), explain why syscalls like `fork`,
   `ptrace`, `init_module` should be denied, and write the key rules of the
   seccomp profile in pseudocode.

---

### Interview Deep-Dive

**Foundational:**
Q: What is a system call and why does Linux need this boundary between user and kernel space?
A: A system call (syscall) is a controlled request from user-space code to the Linux kernel for privileged operations. It's the fundamental security boundary in the OS. WHY NEEDED: Without this boundary: any user program could directly access all hardware (read any file, intercept network traffic, overwrite kernel memory, halt the CPU). The CPU enforces privilege rings: ring 0 (kernel, full hardware access), ring 3 (user space, restricted). Privileged CPU instructions (like directly accessing I/O ports, modifying CPU control registers) cause a fault if executed in ring 3. MECHANISM: When user code calls `write(fd, buf, count)` via libc: libc sets syscall number in `%rax` (1 = write on x86-64), arguments in `%rdi/%rsi/%rdx`, executes `SYSCALL` instruction. CPU saves user-space registers, switches to ring 0, jumps to kernel entry point. Kernel validates: is `fd` a valid open file for this process? Is `buf` a valid user-space address? Performs the write via VFS. Returns result in `%rax`. `SYSRET` instruction switches back to ring 3. COST: ~100-600ns for boundary crossing (hardware save/restore + potential TLB flush). For high-frequency operations like `gettimeofday`: the vDSO bypasses the kernel entirely by mapping kernel-maintained data into user-space. PRACTICAL: ~400 syscalls on x86-64. Every file open, network operation, process creation, and most memory management goes through syscalls. `strace` reveals these at the kernel boundary. Understanding syscalls helps debug "permission denied," hung processes, and performance bottlenecks.

**Expert:**
Q: How does strace work internally, and what are its limitations in production environments?
A: strace is built on the `ptrace` (process tracing) system call - the same mechanism used by debuggers like GDB. MECHANISM: When strace starts a process or attaches to one: (1) strace calls `ptrace(PTRACE_SYSCALL, child_pid, ...)`. (2) Child runs until the NEXT syscall entry - CPU generates a SIGTRAP before entering the syscall. (3) Child process STOPS. (4) strace reads arguments via `ptrace(PTRACE_GETREGS, ...)` - gets rax (syscall number), rdi/rsi/rdx (arguments). (5) strace calls `ptrace(PTRACE_SYSCALL, ...)` again - child now runs until syscall EXIT. (6) Child stops again. (7) strace reads return value from rax. (8) Repeat for every syscall. OVERHEAD ANALYSIS: 2 ptrace calls per application syscall = 4 kernel boundary crossings (strace call + child stop, twice). Plus process context switches between strace and child. Result: 10-100x slowdown is typical. For an I/O-intensive server making 100,000 syscalls/second: strace creates 200,000 extra context switches/second. PRODUCTION RISKS: (1) Timeout violations: a service with a 1-second timeout for database calls may fail during strace because simple calls now take 50ms. (2) Watchdog kills: Kubernetes liveness probes kill the pod, systemd restarts the service. (3) Cascade failures: slowed service causes upstream timeouts, queue backfill. PRODUCTION-SAFE ALTERNATIVES: `perf trace`: uses tracepoints (ring buffer), strace-like output but much lower overhead (2-5% vs 100x). `bpftrace`: eBPF-based, per-syscall BPF programs, near-zero overhead for counting/sampling. `sysdig`: eBPF-based, kernel event capture with filtering. WHEN STRACE IS SAFE IN PRODUCTION: (1) One-shot debugging of a single process that's already failed/slow. (2) Using `-c` count mode (less per-syscall overhead than full trace). (3) Filtering to infrequent syscalls: `strace -e trace=connect,bind`. (4) The problem is so bad that slowdown doesn't matter (app is already returning errors).
