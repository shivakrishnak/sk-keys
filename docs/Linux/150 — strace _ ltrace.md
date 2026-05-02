---
layout: default
title: "strace / ltrace"
parent: "Linux"
nav_order: 150
permalink: /linux/strace-ltrace/
number: "0150"
category: Linux
difficulty: ★★★
depends_on: Process Management, /proc File System
used_by: Observability & SRE, Linux Performance Tuning, tcpdump / Wireshark
related: lsof, /proc File System, Linux Performance Tuning
tags:
  - linux
  - os
  - debugging
  - deep-dive
---

# 150 — strace / ltrace

⚡ TL;DR — `strace` intercepts every system call a process makes and shows the arguments and return values; `ltrace` does the same for library function calls — together they are the ground-truth debuggers for "why does this binary do that?"

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A process crashes silently. No core dump. No log output. The binary is a vendor black box — no source code, no debug symbols. You know it fails, but not why. Is it a missing file? A permission error? A failing network connection? Without the ability to see what the process is actually doing at the OS level, you're guessing. You'd need to add logging to the source and recompile — but there is no source.

**THE BREAKING POINT:**
A third-party agent segfaults 30 seconds after startup on a new server configuration. The vendor's support says "works fine in our environment". No error message. No log. You cannot reproduce it in the dev environment.

**THE INVENTION MOMENT:**
`strace ./agent 2>&1 | tail` shows the last system call before the crash: `open("/etc/agent/config.conf", O_RDONLY) = -1 ENOENT`. The config file doesn't exist on the new server. The agent silently fails on missing config. Five-minute fix instead of a two-week support ticket.

---

### 📘 Textbook Definition

**strace** is a diagnostic tool that uses the `ptrace()` system call to intercept and record every system call a process makes. For each system call, it displays the call name, arguments (decoded where possible), return value, and error code. It can attach to running processes (`-p PID`) or start a new process under tracing. `strace` operates at the kernel interface level — every `read()`, `write()`, `open()`, `connect()`, `mmap()` call is visible.

**ltrace** is analogous to strace but intercepts dynamic library function calls (calls to `libc`, `libssl`, etc.) rather than system calls. It uses `LD_PRELOAD`-like mechanisms and breakpoints to intercept calls at the PLT (Procedure Linkage Table). `ltrace` shows calls like `malloc(256)`, `strcmp("expected", "actual")`, `SSL_write(...)` — calls that happen inside the process before reaching the kernel.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`strace` is a transcript of everything a process asks the kernel to do; `ltrace` transcripts what library functions it calls.

**One analogy:**

> `strace` is an interpreter sitting next to a diplomat (process) at every meeting with the government (kernel). Every request the diplomat makes — "I need access to this file", "I want to open a connection to this server", "give me more memory" — is written down verbatim, along with the government's reply. Even if the diplomat whispers, the interpreter catches it.

**One insight:**
Every observable action a process takes — reading a file, making a network connection, spawning a thread — requires a system call. `strace` captures all of them. This makes it possible to debug any binary, regardless of language, runtime, or whether source code exists.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every interaction between a process and the kernel goes through system calls.
2. `ptrace(PTRACE_SYSCALL)` causes the kernel to stop the traced process at every syscall entry and exit.
3. strace reads the process's registers to extract syscall number, arguments, and return value.
4. Tracing slows the process significantly (10-100×) — use targeted filters in production.

**DERIVED DESIGN:**
`strace` calls `ptrace(PTRACE_TRACEME)` on the target process (or `ptrace(PTRACE_ATTACH)` on a running process). The kernel suspends the traced process at each syscall boundary. strace reads the syscall number from the `orig_rax` register, looks it up in the syscall table to get argument types, reads argument values from registers (`rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9` on x86-64), and calls the appropriate decoder to format them as human-readable strings. For struct arguments (like `stat`, `sockaddr`), strace reads memory from the target process via `PTRACE_PEEKDATA`.

`ltrace` uses a different mechanism: it places software breakpoints at the PLT entries for library functions. When the process calls e.g. `malloc`, control transfers to the PLT, ltrace intercepts it, records the call, then allows the real `malloc` to execute.

**THE TRADE-OFFS:**
**Gain:** Complete visibility into process behaviour at kernel/library level with no source code needed.
**Cost:** `ptrace` causes a context switch per syscall — can slow a process by 100× for syscall-heavy code; cannot be used on processes in containers with `ptrace` disabled (Docker default); requires root or same UID (or `CAP_SYS_PTRACE`); doesn't show internal logic between syscalls.

---

### 🧪 Thought Experiment

**SETUP:**
A Java application that opens database connections is failing in a new environment. The application logs say "connection failed" but don't say why. You have no access to the database server logs.

**WITH strace:**

```bash
strace -f -e trace=network -p $(pidof java) 2>&1 \
  | grep -A2 "connect"
```

Output reveals:

```
connect(42, {sa_family=AF_INET,
  sin_port=htons(5432),
  sin_addr=inet_addr("10.0.0.1")}, 16) = -1
  ECONNREFUSED (Connection refused)
```

The application is connecting to `10.0.0.1:5432` (the database). `ECONNREFUSED` means the connection was actively refused — the database is either not listening on that port or iptables is rejecting it. The hostname resolved to `10.0.0.1` — maybe the DNS record was changed and is pointing to the wrong host.

**THE INSIGHT:**
strace showed the exact IP the JVM resolved and attempted to connect to — information that `netstat` would show for established connections but can't show for failed connection attempts. This leads directly to the root cause (DNS misconfiguration) in minutes.

---

### 🧠 Mental Model / Analogy

> `strace` is like having a phone tap on every call the process makes to the operating system. Each time the process picks up the phone (enters a syscall), you hear both sides: "I'd like to read 4096 bytes from file descriptor 3" (the process) and "Here are 4096 bytes" or "File not found" (the kernel). Between calls, you can't hear anything — strace doesn't show what the process does in user space between syscalls.

- "Phone call" → system call
- "Both sides heard" → entry and exit of syscall
- "Call log" → strace output
- "Can't hear between calls" → internal logic between syscalls is invisible

Where this analogy breaks down: you can't just "tap" a phone call passively — ptrace stops the process at each syscall boundary, causing real slowdown. In production, filtering is essential.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`strace` shows every request a program makes to the operating system — opening files, reading data, making network connections, asking for memory. It's like a detailed log of every conversation between a program and the OS, useful for understanding why a program fails even when it produces no error messages.

**Level 2 — How to use it (junior developer):**
Start a process under strace: `strace ./myapp`. Attach to running process: `strace -p 12345`. Filter to specific syscalls: `strace -e trace=file,network ./myapp` (file operations and network calls only). Follow child processes: `strace -f ./myapp`. Write output to file: `strace -o /tmp/trace.txt ./myapp`. Find what files a program opens: `strace -e openat ./myapp 2>&1 | grep ENOENT`.

**Level 3 — How it works (mid-level engineer):**
ptrace stops the process at both syscall entry (before the kernel executes the syscall) and exit (after). This allows strace to show both the arguments (entry) and return value (exit). The `-f` flag forks strace to trace each child process as it's created — essential for multi-process programs. `-y` annotates file descriptors with their paths (`/proc/PID/fd/`). `-k` prints the stack trace at each syscall. `-c` produces a summary of syscall counts and time — useful for performance analysis without reading thousands of lines.

**Level 4 — Why it was designed this way (senior/staff):**
`ptrace` was designed as a general-purpose process control interface for debuggers (gdb uses it too). strace repurposed it for observability. The limitation is fundamental: ptrace stops the process at every syscall boundary, requiring two context switches per syscall (kernel→strace, strace→process). On syscall-heavy workloads (many small `read()`/`write()` calls), this can cause 100× slowdown. This drove the development of seccomp-bpf (which filters syscalls in kernel) and eBPF-based strace equivalents (`bpftrace`, `perf trace`) that trace syscalls with a kernel-side BPF program, eliminating the context switch overhead entirely — they can trace production workloads with <1% overhead.

---

### ⚙️ How It Works (Mechanism)

**Essential strace commands:**

```bash
# Basic: trace all syscalls
strace ./program

# Trace specific program with output to file
strace -o /tmp/trace.txt ./program arg1 arg2

# Attach to running process
strace -p $(pidof nginx) -o /tmp/nginx_trace.txt

# Trace file-related syscalls only
strace -e trace=file ./program
# trace categories: file, network, ipc, memory,
#   process, signal, desc (file descriptors)

# Trace specific syscall names
strace -e openat,read,write,connect ./program

# Follow child processes (threads, forks)
strace -f ./program

# Summary of syscall counts (performance analysis)
strace -c ./program
# Output: count/time/errors per syscall

# Show timestamps (relative to start)
strace -r ./program

# Show absolute wall-clock timestamps
strace -t ./program  # seconds
strace -tt ./program # microseconds
strace -ttt ./program # epoch microseconds

# Print kernel stack at each syscall
strace -k ./program

# Decode strings (default 32 chars, increase for long paths)
strace -s 256 ./program

# Verbose: decode all struct fields
strace -v ./program
```

**Practical debugging patterns:**

```bash
# Find missing files (ENOENT errors)
strace -e openat ./program 2>&1 | grep ENOENT

# Find permission errors
strace -e openat ./program 2>&1 | grep EACCES

# Debug network connections
strace -e trace=network ./program 2>&1 \
  | grep -E 'connect|bind|listen'

# Debug DNS resolution
strace -f -e trace=network,file ./program 2>&1 \
  | grep -E 'socket|connect|open.*resolv'

# Find what config files a program reads
strace -e openat,read ./program 2>&1 \
  | grep -v -E '(ENOENT|proc|dev|lib)'

# Profile syscall frequency
strace -c -f ./program 2>&1 | sort -k4 -rn
# Shows: % time, seconds, usecs/call, calls, syscall

# Trace a specific thread
strace -p <thread-tid>
```

**ltrace examples:**

```bash
# Trace library calls
ltrace ./program

# Trace specific library function
ltrace -e malloc,free,strlen ./program

# Trace C string functions
ltrace -e 'str*' ./program

# Combined strace + ltrace equivalent
ltrace -S ./program  # also shows syscalls
```

**Reading strace output:**

```
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
│            │    │                   │                     │
│            │    └── file path       └── flags             └── fd or error
│            └── directory FD (AT_FDCWD = current dir)
└── syscall name

connect(5, {sa_family=AF_INET, sin_port=htons(5432),
  sin_addr=inet_addr("10.0.1.5")}, 16) = -1
                                         ECONNREFUSED
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  DEBUGGING: "Permission denied" — but where?  │
└────────────────────────────────────────────────┘

 strace -f -e trace=file,process -p $(pidof app)
       │
       ▼
 Syscall: execve("/usr/bin/helper", ...) = 0
       │  (app spawns a helper process)
       ▼
 Syscall: openat(AT_FDCWD,
   "/var/run/app/socket", O_RDWR) = -1
   EACCES (Permission denied)
       │
       ▼
 Root cause: /var/run/app/socket exists but
 the helper process runs as "www-data";
 socket is owned by "appuser" mode 0600
       │
       ▼
 Fix: chmod 0660 /var/run/app/socket
      chgrp www-data /var/run/app/socket

 Without strace: "permission denied" error
 buried 3 process forks deep — would have
 taken hours to trace manually
```

**FAILURE PATH:**
If `strace -p PID` returns "Operation not permitted", check if the process is in a container with `CAP_SYS_PTRACE` disabled or `seccomp` profile blocking `ptrace`. Solution: `docker run --cap-add=SYS_PTRACE` or run strace on the host with `nsenter`.

---

### 💻 Code Example

**Example 1 — Systematic debugging workflow:**

```bash
#!/bin/bash
# Structured strace debug for a failing service
SERVICE_BIN=${1:-/usr/bin/myservice}
SERVICE_ARGS=${2:-"--config /etc/myservice.conf"}

echo "=== Phase 1: File access issues ==="
strace -e openat,stat,access \
  -s 512 $SERVICE_BIN $SERVICE_ARGS 2>&1 \
  | grep -E 'ENOENT|EACCES|EPERM'

echo ""
echo "=== Phase 2: Network issues ==="
strace -e trace=network \
  -s 512 $SERVICE_BIN $SERVICE_ARGS 2>&1 \
  | grep -E 'connect|bind|ECONNREFUSED|ETIMEDOUT'

echo ""
echo "=== Phase 3: Syscall summary ==="
strace -c $SERVICE_BIN $SERVICE_ARGS 2>&1
```

**Example 2 — Performance profiling with strace:**

```bash
# Find the top 10 slowest syscalls in a program
strace -c -f ./slow_program 2>&1 | \
  grep -v "^%" | \
  sort -k2 -rn | \
  head -15

# Identify if a program is syscall-bound
# (high %time in small, fast syscalls = syscall-bound)
# vs. compute-bound (low syscall count, most time user-space)
```

**Example 3 — Trace without slowing target (using perf):**

```bash
# Modern alternative: perf trace (low overhead)
# Uses kernel-side tracepoints, not ptrace
perf trace -p $(pidof myservice) \
  --no-syscalls \
  --event 'raw_syscalls:sys_enter'

# Even lower overhead with bpftrace
bpftrace -e '
  tracepoint:syscalls:sys_enter_openat
  /pid == $1/ {
    printf("%s\n", str(args->filename));
  }
' $(pidof myservice)
```

---

### ⚖️ Comparison Table

| Tool           | What It Traces     | Overhead           | Source Needed | Root Access        |
| -------------- | ------------------ | ------------------ | ------------- | ------------------ |
| **strace**     | System calls       | High (ptrace)      | No            | Partial (same UID) |
| **ltrace**     | Library calls      | High (breakpoints) | No            | Partial            |
| **perf trace** | System calls       | Low (tracepoints)  | No            | Yes                |
| **bpftrace**   | Any kernel point   | Very low (eBPF)    | No            | Yes                |
| **gdb**        | Any instruction    | Very high          | Helps         | Partial            |
| Valgrind       | Memory ops + calls | Extreme            | Helps         | No                 |

How to choose: use `strace` for quick debugging of missing files, permissions, or network connections; avoid in production on high-syscall-rate services; use `perf trace` or `bpftrace` for production investigation; use `ltrace` for library-level debugging (linking, wrong versions).

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                    |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| strace shows the full execution of a program | strace shows kernel boundary crossings only — internal computation, function calls, and in-memory operations are invisible |
| strace is safe to use on production          | strace via ptrace can cause 10-100× slowdown; use `perf trace` or bpftrace for production — same information, <5% overhead |
| You need root to run strace                  | You can strace your own processes; root is needed to attach to other users' processes                                      |
| strace output is always complete             | Large buffers passed to syscalls are truncated to `strsize` (default 32 bytes); use `-s 512` or larger to see full strings |
| ltrace and strace are mutually exclusive     | `ltrace -S` shows both library calls and system calls simultaneously                                                       |

---

### 🚨 Failure Modes & Diagnosis

**strace Output Too Verbose to Analyse**

**Symptom:**
Running `strace -f ./myapp` produces thousands of lines per second — impossible to read or find the relevant error.

**Root Cause:**
The program is I/O-intensive (many `read()`/`write()` calls) or the `-f` flag is tracing all threads including high-frequency worker threads.

**Fix:**

```bash
# Filter to relevant syscall categories only
strace -e trace=file,network ./myapp 2>&1 \
  | grep -E 'ENOENT|EACCES|ECONNREFUSED'

# Or use summary mode first to identify
# the most frequent syscalls, then filter:
strace -c -f ./myapp 2>&1
# Then re-run with: strace -e openat,connect ./myapp

# Target a specific thread
strace -p <thread-tid>  # not the main PID

# Write to file and grep offline
strace -o /tmp/trace.txt -f ./myapp
grep ENOENT /tmp/trace.txt
```

---

**Cannot Attach to Process in Container**

**Symptom:**
`strace -p <PID>` inside a container returns "Operation not permitted".

**Root Cause:**
Container is running with the default Docker seccomp profile that blocks `ptrace`.

**Diagnostic Command:**

```bash
# Check seccomp profile
cat /proc/<PID>/status | grep Seccomp
# 2 = SECCOMP_MODE_FILTER (seccomp active)

# Check capabilities
grep CapEff /proc/$$/status
```

**Fix:**

```bash
# Option 1: Restart container with ptrace allowed
docker run --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined myimage

# Option 2: Trace from host with nsenter
nsenter -t <PID> -n -- strace -p <PID>
# (enters the container's network namespace
# while running strace from the host with full caps)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management` — understanding processes, PIDs, and the kernel-process boundary is foundational to understanding what strace traces
- `/proc File System` — strace uses `/proc/PID/fd` to resolve file descriptor paths; understanding procfs helps interpret strace output

**Builds On This (learn these next):**

- `lsof` — shows open files and sockets for processes; complementary to strace for understanding what a process has open
- `Linux Performance Tuning` — strace's `-c` flag is a performance profiling tool; identifying syscall bottlenecks informs tuning
- `Observability & SRE` — eBPF-based tools (bpftrace, perf) are the production-safe evolution of strace for observability

**Alternatives / Comparisons:**

- `perf trace` — same system call tracing with <5% overhead using kernel tracepoints
- `bpftrace` — programmable eBPF tracing; custom scripts to trace any kernel function
- `gdb` — full process debugger including user-space state; much slower but complete visibility
- `ltrace` — library call tracing, complementary to strace's system call tracing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ ptrace-based syscall interceptor — shows  │
│              │ every kernel boundary crossing a process  │
│              │ makes, with arguments and return values   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Closed-source binaries fail silently;     │
│ SOLVES       │ no source to add logging; need ground-    │
│              │ truth of what process actually does       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every process action requires a syscall;  │
│              │ strace captures them all regardless of    │
│              │ language or runtime                       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ "Why does this binary fail?" with no logs │
│              │ or source code; debugging file/network    │
│              │ permission errors                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-syscall-rate production services;    │
│              │ use perf trace or bpftrace instead        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete visibility vs high overhead;     │
│              │ any binary vs ptrace container restriction│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A phone tap on every conversation        │
│              │  between the process and the kernel"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ perf trace → bpftrace → eBPF             │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A JVM-based application (Java) has 200 threads, all writing to the same log file. `strace -c -f` on the process shows that `futex` is the top syscall by count (>90% of all syscalls) and `pwrite64` accounts for 40% of total wall time. Interpret what this syscall profile reveals about the application's architecture and write performance, and propose two specific changes (one JVM configuration change, one architectural change) that would reduce the pwrite64 time, citing the specific strace metrics you would use to validate the improvement.

**Q2.** You are writing a `bpftrace` script to replace a common `strace` use case — detecting when any process opens a file that doesn't exist (ENOENT from openat). The goal is to run this continuously in production with <1% CPU overhead. Write the bpftrace script, explain why it achieves low overhead compared to strace, and describe what additional context (beyond what strace provides) you could add to make it more useful for production incident response.
