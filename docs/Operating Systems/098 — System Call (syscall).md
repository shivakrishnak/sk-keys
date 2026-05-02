---
layout: default
title: "System Call (syscall)"
parent: "Operating Systems"
nav_order: 98
permalink: /operating-systems/system-call-syscall/
number: "0098"
category: Operating Systems
difficulty: ★★☆
depends_on: User Space vs Kernel Space, Process, Virtual Memory
used_by: File Descriptor, Blocking I/O, Non-Blocking I/O, Fork / Exec
related: File Descriptor, Interrupt, User Space vs Kernel Space
tags:
  - os
  - internals
  - kernel
  - performance
  - intermediate
---

# 098 — System Call (syscall)

⚡ TL;DR — A system call is the only legal gate from your application into the OS kernel — a controlled handoff that lets user code request privileged services safely.

| #0098           | Category: Operating Systems                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | User Space vs Kernel Space, Process, Virtual Memory          |                 |
| **Used by:**    | File Descriptor, Blocking I/O, Non-Blocking I/O, Fork / Exec |                 |
| **Related:**    | File Descriptor, Interrupt, User Space vs Kernel Space       |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Imagine user programs could directly call any OS function by jumping to an arbitrary memory address. A malicious program could jump to the kernel's file-write routine, pass it a path like `/etc/shadow`, and overwrite your password database. Or jump to the memory-allocation routine and grab every byte of RAM, starving other processes. Without a controlled entry point, the kernel would be an open library — no authentication, no parameter validation, no access control.

THE BREAKING POINT:
Early real-mode DOS programs called BIOS routines directly via software interrupts with no validation. Any program could call `INT 13h` (disk I/O) with any parameters, writing to any sector of the disk. This worked for single-user, single-tasking systems but became catastrophically unsafe as systems moved to multi-user, multi-process designs.

THE INVENTION MOMENT:
This is exactly why the system call was created — to provide a single, validated, permission-checked entry point that every user program must use to request kernel services.

---

### 📘 Textbook Definition

A **system call** (syscall) is a programmatic interface that allows user-space processes to request services from the operating system kernel. When a process executes a syscall instruction, the CPU switches from user mode (ring 3) to kernel mode (ring 0), the kernel validates parameters and performs the requested operation (I/O, memory allocation, process management), then returns control to user space. The syscall interface is the ABI (Application Binary Interface) between user programs and the OS kernel.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A syscall is a formal request form your program submits to the OS — the only way to ask the kernel for help.

**One analogy:**

> You're in an airport terminal (user space). The control tower (kernel) manages runways, fuel, and air traffic. You can't walk into the control tower. Instead, you use the intercom (syscall) to make a specific, numbered request: "Request gate B4 boarding." The controller validates your request, acts on it, and confirms. You never touch the controls.

**One insight:**
The syscall number is the key: your program doesn't call kernel functions by name or address — it places a number in a register (e.g., `rax=1` for `write` on Linux x86-64) and fires the `syscall` instruction. The kernel uses that number as an index into its syscall table, jumping to the right handler. This indirection means the kernel ABI can be stable even as internal kernel code changes.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. User code cannot execute privileged instructions without going through the syscall gate.
2. The kernel controls the syscall entry point — user code specifies WHICH syscall, not WHERE to jump.
3. Parameters from user space must be validated and safely copied — they cannot be trusted directly.

DERIVED DESIGN:
The CPU provides a `syscall`/`sysret` instruction pair (or `int 0x80` on older x86). When `syscall` fires, the CPU atomically loads a new instruction pointer from the MSR_LSTAR register (a fixed kernel address), switches the stack pointer to a kernel stack, and elevates privilege. The kernel's syscall dispatcher reads the syscall number from `rax`, validates it is within range, and dispatches to the handler. Handler parameters in `rdi`, `rsi`, `rdx` etc. are user-supplied addresses — the kernel calls `copy_from_user()` to safely read them, which checks that the source address is in valid user memory.

THE TRADE-OFFS:
Gain: Safe, validated, auditable interface — every kernel service request is logged, permission-checked, and bounded.
Cost: ~100–300 ns per syscall; pipeline flush; TLB effects (especially with KPTI). High-frequency code must batch syscalls.

---

### 🧪 Thought Experiment

SETUP:
A web server processes 50,000 HTTP requests per second. Each request reads a small file (~4 KB).

WHAT HAPPENS WITHOUT a controlled syscall interface:

1. The server directly calls the kernel's `inode_read()` function.
2. The OS cannot validate that the path passed is legitimate.
3. A path traversal bug (`../../etc/passwd`) reads any file on disk.
4. No resource limits can be enforced — the server reads all 50,000 files simultaneously, exhausting file handles for all other processes.

WHAT HAPPENS WITH syscall:

1. Server calls `open()` → triggers `syscall` with number 2 (openat).
2. Kernel validates: does the process have read permission? Does the file exist?
3. Kernel enforces per-process file descriptor limits (`RLIMIT_NOFILE`).
4. Returns a file descriptor (integer handle) — the server never touches raw inode data.
5. Path traversal is caught at the kernel's path resolution layer.

THE INSIGHT:
The syscall boundary is not just performance overhead — it is a mandatory security checkpoint. Every resource the application uses is granted by the kernel, not seized.

---

### 🧠 Mental Model / Analogy

> A syscall is like an ATM transaction. You (user process) want cash (kernel service). You can't walk into the bank vault (kernel memory). You use the ATM (syscall interface), which validates your PIN (permission check), reads your account (kernel data), and dispenses only what you're authorised for. Every transaction is logged.

"ATM interface" → syscall instruction + syscall number
"PIN validation" → permission/capability check in kernel handler
"Bank vault" → kernel data structures (file tables, process table)
"Account balance" → resource limits enforced by kernel
"Transaction log" → audit log (auditd, seccomp)

Where this analogy breaks down: ATM transactions are sequential; syscalls are concurrent — millions per second across all processes, handled by kernel code that must be re-entrant and lock-safe.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Whenever your program needs something from the operating system — reading a file, creating a thread, sending network data — it makes a formal "system call" request. The OS checks the request, does the work, and returns the result. Your program can't do these things directly — it must ask.

**Level 2 — How to use it (junior developer):**
You rarely call syscalls directly — you call C library functions like `read()`, `write()`, `malloc()`, `pthread_create()` that wrap them. In Java, every `FileInputStream.read()` eventually triggers a `read` syscall. You care about syscalls when profiling: `strace -p <pid>` shows every syscall your process makes, which is invaluable for debugging "why is my app slow/hanging?"

**Level 3 — How it works (mid-level engineer):**
On Linux x86-64, the syscall ABI places the syscall number in `rax`, arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`. The `syscall` instruction saves `rip` and `rflags` to kernel stack, sets CPL=0, and jumps to `entry_SYSCALL_64`. The kernel dispatcher calls `sys_call_table[rax]`. The handler validates its arguments using `copy_from_user()` / `access_ok()`, performs the operation, and returns. `sysret` restores user state. The vDSO (virtual dynamic shared object) maps frequently called, read-only syscalls (`gettimeofday`, `clock_gettime`) into user space, making them callable without a ring switch.

**Level 4 — Why it was designed this way (senior/staff):**
The stable syscall ABI is one of Linux's most consequential design choices: syscall numbers are NEVER renumbered. A binary compiled in 2002 still works on Linux 6.x because the syscall table is ABI-stable. This is why POSIX exists — to standardise the syscall interface across Unixes. The alternative (Windows approach) uses an unstable syscall table hidden behind stable Win32 DLLs, giving more kernel flexibility but requiring every program to use system DLLs. `io_uring` (Linux 5.1) is the most radical syscall evolution: it maps a shared ring buffer between user and kernel, allowing batches of I/O operations to be submitted and completed without individual syscall overhead, reducing mode switches by orders of magnitude.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│              SYSCALL FLOW (Linux x86-64)                │
├─────────────────────────────────────────────────────────┤
│  User Space                                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. App calls read(fd, buf, 4096)                 │  │
│  │ 2. libc sets rax=0, rdi=fd, rsi=buf, rdx=4096   │  │
│  │ 3. SYSCALL instruction fires ←─────────────────  │  │
│  └──────────────────────────────────────────────────┘  │
│              ↓ CPU: CPL 3→0, switch stack               │
│  Kernel Space                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 4. entry_SYSCALL_64 saves registers              │  │
│  │ 5. Dispatch: sys_call_table[0] → sys_read()      │  │
│  │ 6. Validate: access_ok(buf, 4096)                │  │
│  │ 7. VFS: file → inode → block device              │  │
│  │ 8. copy_to_user(buf, kernel_buf, bytes_read)     │  │
│  │ 9. return bytes_read in rax                      │  │
│  └──────────────────────────────────────────────────┘  │
│              ↓ SYSRET: CPL 0→3, restore registers       │
│  User Space                                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 10. libc returns n = bytes_read                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Failure path:** If step 6 fails (invalid address), `access_ok` returns false → syscall returns `-EFAULT` → libc sets `errno = EFAULT` → application receives -1.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[App: read(fd, buf, n)]
   → [libc: load syscall nr into rax]
   → [syscall instruction — YOU ARE HERE]
   → [Kernel: validate → VFS → driver → copy_to_user]
   → [sysret]
   → [App receives byte count]
```

FAILURE PATH:
[Invalid buffer address passed] → [access_ok() fails in kernel] → [returns -EFAULT] → [libc sets errno] → [app handles error]

WHAT CHANGES AT SCALE:
At 1M syscalls/sec, mode-switch cost (~200 ns each) consumes ~20% of a single CPU core. Applications like Redis use `io_uring` to batch hundreds of I/O operations per ring submission, cutting per-op syscall cost to near zero. At Google/Facebook scale, seccomp-BPF filters are applied to restrict which syscalls are allowed per service, reducing attack surface and adding ~20–50 ns overhead per syscall for filter evaluation.

---

### 💻 Code Example

Example 1 — Observing syscalls with strace:

```bash
# BAD: guessing why app is slow
./myapp  # just runs it

# GOOD: trace every syscall with timing
strace -T -p $(pgrep myapp) 2>&1 | head -50

# Output shows:
# read(5, "", 4096)  = 0 <0.000012>
# write(1, "hello\n", 6) = 6 <0.000008>
```

Example 2 — Direct syscall in C (rarely done but illustrative):

```c
#include <sys/syscall.h>
#include <unistd.h>

// BAD: using magic number directly
long ret = syscall(1, 1, "hello\n", 6);  // write

// GOOD: use the named constant
long ret = syscall(SYS_write, STDOUT_FILENO,
                   "hello\n", 6);
// Returns 6 on success, -1 on error
```

Example 3 — Reducing syscalls with io_uring (Linux 5.1+):

```c
// BAD: 1000 write() calls = 1000 syscalls
for (int i = 0; i < 1000; i++) {
    write(fd, buf[i], sizeof(buf[i]));
}

// GOOD: batch with io_uring — 1 syscall submits all
struct io_uring ring;
io_uring_queue_init(32, &ring, 0);
for (int i = 0; i < 1000; i++) {
    struct io_uring_sqe *sqe =
        io_uring_get_sqe(&ring);
    io_uring_prep_write(sqe, fd, buf[i],
                        sizeof(buf[i]), 0);
}
io_uring_submit(&ring);  // ONE syscall for 1000 writes
```

---

### ⚖️ Comparison Table

| Interface               | Latency          | Batching | Security          | Best For                        |
| ----------------------- | ---------------- | -------- | ----------------- | ------------------------------- |
| **Traditional syscall** | ~100–300 ns      | No       | Full validation   | General I/O                     |
| vDSO (read-only)        | ~5–20 ns         | No       | Kernel-mapped     | `clock_gettime`, `gettimeofday` |
| io_uring                | ~10 ns amortised | Yes      | Ring buffer       | High-frequency async I/O        |
| DPDK (kernel bypass)    | ~50 ns           | Yes      | None (user-space) | Network line-rate processing    |

How to choose: Default to standard syscalls. Adopt `io_uring` when profiling shows >500K syscalls/sec as bottleneck. Use DPDK only for dedicated network packet processing.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| "malloc() makes a syscall every time"                 | malloc() manages a heap pool; it calls `brk`/`mmap` only when pool is exhausted — typically rarely                  |
| "Syscalls are just function calls into the kernel"    | Syscalls require a CPU privilege transition (ring 3→0) — fundamentally different from a function call               |
| "The syscall number is the memory address to jump to" | Syscall number is an index into a dispatch table — the actual handler address is hidden from user space             |
| "Syscalls are always slow"                            | vDSO maps some read-only syscalls into user space — `clock_gettime` costs ~5 ns, same as a function call            |
| "strace doesn't affect performance in production"     | strace attaches ptrace which intercepts every syscall — easily 10–100× overhead, never use in production under load |

---

### 🚨 Failure Modes & Diagnosis

**1. EINTR — Syscall Interrupted by Signal**

Symptom: `read()` or `write()` returns -1 with `errno = EINTR` unexpectedly; intermittent failures in long-running operations.

Root Cause: A signal (e.g., SIGCHLD, SIGALRM) was delivered to the process while it was blocked in a syscall; the kernel returns early with EINTR rather than completing the operation.

Diagnostic:

```bash
strace -e trace=read,write -p <PID> 2>&1 | grep EINTR
```

Fix:

```c
// BAD: assume read always succeeds fully
ssize_t n = read(fd, buf, len);

// GOOD: retry on EINTR
ssize_t n;
do {
    n = read(fd, buf, len);
} while (n == -1 && errno == EINTR);
```

Prevention: Use `SA_RESTART` flag in `sigaction()` to auto-restart syscalls after signal delivery.

---

**2. EFAULT — Invalid User-Space Pointer**

Symptom: syscall returns -1, `errno = EFAULT`; often a crash in the calling code shortly after.

Root Cause: A null, freed, or otherwise invalid pointer was passed to a syscall; kernel's `access_ok()` or `copy_from_user()` rejected it.

Diagnostic:

```bash
valgrind --track-origins=yes ./myapp
# Or AddressSanitizer
gcc -fsanitize=address ./myapp.c -o myapp && ./myapp
```

Fix: Validate all pointers before syscall. Never pass stack-allocated buffers to async operations that may outlive the stack frame.

Prevention: Use `-fsanitize=address` in CI builds to catch memory errors before production.

---

**3. Seccomp Policy Violation (SIGSYS)**

Symptom: Process killed with signal 31 (SIGSYS); observed in container environments.

Root Cause: A container security profile (Docker default seccomp, or custom policy) blocks the syscall attempted by the process.

Diagnostic:

```bash
# Check syscall blocked by seccomp
dmesg | grep "audit: type=1326"
# Or with auditd
ausearch -m SECCOMP
```

Fix: Whitelist the required syscall in the container's seccomp profile or use `--security-opt seccomp=unconfined` (only in dev).

Prevention: Test applications against their production seccomp profile in staging; use `strace -c` to enumerate all syscalls the app uses.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `User Space vs Kernel Space` — syscalls are the bridge between these two zones
- `Process` — each process makes syscalls independently; kernel tracks per-process state
- `Virtual Memory` — syscall parameters are user-space virtual addresses; kernel must validate them

**Builds On This (learn these next):**

- `File Descriptor` — returned by syscalls like `open()`; the handle for all subsequent I/O syscalls
- `Blocking I/O` — the behaviour when a blocking syscall suspends the calling thread
- `io_uring` — the modern Linux interface that batches syscalls to reduce ring transitions

**Alternatives / Comparisons:**

- `vDSO` — kernel-mapped user-space page that lets some syscalls bypass ring transitions entirely
- `DPDK` — eliminates most I/O syscalls by mapping device memory directly into user space

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Controlled gate from user app into OS     │
│              │ kernel — the only legal entry point       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ User code needs privileged services but   │
│ SOLVES       │ can't run privileged instructions safely  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Syscall number = index, not address —     │
│              │ user code never knows kernel layout       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any interaction with OS resources (always)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-frequency ops: batch with io_uring   │
│              │ or use vDSO-mapped calls                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Safety + validation vs ~100–300 ns each   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The intercom between your app and the OS │
│              │  control tower"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ File Descriptor → Blocking I/O → io_uring │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Linux syscall table is ABI-stable: syscall numbers are never renumbered. Windows takes the opposite approach — hiding the syscall table behind stable Win32 DLLs. What are the precise engineering trade-offs of each approach for OS evolution, security patching, and binary compatibility?

**Q2.** `io_uring` reduces syscall overhead dramatically by using a shared ring buffer between user and kernel space. But Linus Torvalds has described `io_uring` as having "a huge attack surface." What specific security risks does the ring-buffer design introduce that traditional per-syscall validation avoids?
