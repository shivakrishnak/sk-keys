---
layout: default
title: "Process"
parent: "Operating Systems"
nav_order: 91
permalink: /operating-systems/process/
number: "091"
category: Operating Systems
difficulty: ★☆☆
depends_on: Operating Systems Basics, Memory Management Models
used_by: Thread (OS), Process vs Thread, Context Switch, Virtual Memory, System Call (syscall)
tags:
  - os
  - foundational
  - process
---

# 091 — Process

`#os` `#foundational` `#process`

⚡ TL;DR — An independent, isolated execution unit: a running program with its own virtual address space, file handles, and OS-managed resources — the OS's fundamental unit of resource allocation.

| #091 | Category: Operating Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Operating Systems Basics, Memory Management Models | |
| **Used by:** | Thread (OS), Process vs Thread, Context Switch, Virtual Memory, System Call (syscall) | |

---

### 📘 Textbook Definition

A **process** is an instance of a program in execution, constituting the OS's unit of resource allocation and protection. Each process has: a unique **Process ID (PID)**, its own **virtual address space** (isolating it from all other processes), a **process control block (PCB)** maintained by the kernel containing its state, registers, memory mappings, and file descriptor table, and at least one **thread** of execution. Processes communicate via **inter-process communication (IPC)** mechanisms (pipes, sockets, shared memory, signals) rather than direct memory access. Process lifecycle states: New → Ready → Running → Waiting → Terminated.

### 🟢 Simple Definition (Easy)

A process is a running program — your browser, your database server, your Java application. Each runs in its own isolated box that the operating system manages.

### 🔵 Simple Definition (Elaborated)

When you launch a Java application, the OS creates a process: it allocates memory for the program's code, data, and stack; assigns it a PID; and sets it up to run independently of all other programs. If your process crashes, it doesn't affect other processes — each lives in its own isolated virtual address space. The OS's job is to manage many processes simultaneously, giving each the illusion of having the entire CPU and memory all to itself via time-slicing and virtual memory. Processes are heavyweight compared to threads — creating one involves many OS operations, and communicating between them requires explicit IPC mechanisms.

### 🔩 First Principles Explanation

**Why isolation matters:**

Without process isolation, any buggy program could corrupt any other program's memory. A buffer overflow in program A would overwrite program B's data. The OS enforces protection via virtual address spaces: each process sees only its own memory region, and the hardware (MMU — Memory Management Unit) enforces translation from virtual to physical addresses.

**Process Control Block (PCB) contents:**

```
PCB (stored in kernel memory):
  - PID (process ID)
  - State: Running / Ready / Blocked / Terminated
  - Program Counter (PC): address of next instruction
  - CPU Registers: saved state when process is preempted
  - Memory maps: page table base register, virtual address ranges
  - File descriptor table: open files, sockets, pipes
  - Scheduling info: priority, time slice, CPU time used
  - Accounting: owner UID, GID, resource limits (ulimit)
  - IPC info: pending signals, message queue handles
```

**Virtual address space layout (typical 64-bit Linux process):**

```
High addresses (kernel space — not accessible to user process):
0xFFFF... Kernel
──────────────────────────────────────
Low addresses (user space):
Stack (grows down) ↓         ← function call frames, local variables
...
Memory-mapped files          ← mmap(), shared libraries
...
Heap (grows up) ↑            ← malloc/new allocations
BSS segment                  ← uninitialised global/static variables
Data segment                 ← initialised global/static variables
Text segment (code)          ← read-only executable instructions
0x000000 (null)
```

**Process creation (fork-exec model on Unix):**

```
fork():  Creates a child process as a copy of parent (copy-on-write)
exec():  Replaces child's address space with a new program image
         Together: run a new program as a separate process

JVM startup: OS creates a process, JVM initialises in that process,
             then all Java threads are kernel threads within that process
```

**Process lifecycle:**

```
New      → fork() or exec() → process created
Ready    → in OS scheduler queue, waiting for CPU
Running  → currently on CPU
Waiting  → blocked on I/O, lock, sleep — not runnable
Terminated → exit() called or killed by signal
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Process Isolation:

- Multiple programs sharing one memory space: buffer overflow in any program corrupts all.
- Single-tasking (MS-DOS style): one program at a time; others freeze.
- Shared file handles: any program can corrupt another's file operations.

What breaks without it:
1. A bad HTTP request can crash not just the web server but the entire OS.
2. No way to allocate CPU time fairly among multiple applications.

WITH Processes:
→ Any process crash is isolated — OS can kill and restart just that process.
→ Multiple processes time-share the CPU, giving the illusion of parallel execution.
→ Security boundary: process A cannot read process B's secrets (passwords, session keys).

### 🧠 Mental Model / Analogy

> A process is like a contractor working in a sealed building unit. Each contractor (process) has their own workspace (virtual address space), their own set of keys to specific rooms they're allowed in (file descriptors), and their own tools (CPU registers, stack). The building manager (OS) decides when each contractor gets to work (CPU scheduling) and can evict a contractor who causes damage without affecting others. Contractors communicate through the building's intercom system (IPC: pipes, sockets) — they can't just walk into each other's units.

"Contractor" = process, "sealed unit" = virtual address space isolation, "building manager" = OS scheduler, "intercom" = IPC.

### ⚙️ How It Works (Mechanism)

**Process states and transitions:**

```
       fork()
New ──────────────► Ready ◄─────────── Interrupt (preemption)
                      │                        │
              schedule│                        │  dispach
                      ▼                        │
                   Running ────────────────────┘
                      │
               I/O or event wait
                      ▼
                   Waiting ──────┐
                      │         │
               I/O done /       │
               event occurs     │
                      └─────────┘
                      │
                   exit()
                      ▼
                  Terminated
```

**Key Linux process management commands:**

```bash
ps aux          # list all processes
ps -p <pid>     # info on specific process
kill -9 <pid>   # SIGKILL uncatchable kill
kill -15 <pid>  # SIGTERM graceful kill
/proc/<pid>/    # procfs: live process information
  /proc/<pid>/status   # process state, memory, limits
  /proc/<pid>/maps     # virtual memory layout
  /proc/<pid>/fd/      # file descriptors
  /proc/<pid>/environ  # environment variables
top / htop      # real-time process monitoring
strace -p <pid> # trace system calls
```

**Process vs JVM:**

```
OS Process
  └── JVM Process
        ├── JVM internals (class loader, GC, JIT)
        └── User code executing as Java threads
             (all sharing the same process address space)

All Java threads share heap memory — they're in the same OS process
Java isolation requires separate JVM instances (separate OS processes)
```

### 🔄 How It Connects (Mini-Map)

```
Program (idle executable on disk)
        ↓ fork() / exec()
Process ← you are here
  (running program + resources + isolation)
        ↓ lighter-weight execution unit
Thread (OS)
  (shares process memory; multiple per process)
        ↓ managed by
OS Scheduler (context switch between processes)
        ↓ communicates via
IPC: Pipes | Sockets | Shared Memory | Signals
```

### 💻 Code Example

Example 1 — Inspecting current process in Java:

```java
// Get current process info (Java 9+)
ProcessHandle self = ProcessHandle.current();
System.out.println("PID: " + self.pid());

// Process info: start time, command, user
ProcessHandle.Info info = self.info();
System.out.println("Command: " + info.command().orElse("N/A"));
System.out.println("Start Time: " + info.startInstant().orElse(null));

// List all running processes (requires OS permission)
ProcessHandle.allProcesses()
    .filter(p -> p.info().command().orElse("").contains("java"))
    .forEach(p -> System.out.println(
        "Java PID: " + p.pid()));
```

Example 2 — Spawning a child process from Java:

```java
// Start an external process (new OS process)
ProcessBuilder pb = new ProcessBuilder("ls", "-la");
pb.directory(Paths.get("/tmp").toFile());
pb.redirectErrorStream(true);

Process process = pb.start();

// Read output (runs in child process, separate address space)
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(process.getInputStream()))) {
    reader.lines().forEach(System.out::println);
}

int exitCode = process.waitFor();
System.out.println("Exit code: " + exitCode);
```

Example 3 — Checking process limits in Linux:

```bash
# Check OS resource limits for current process
ulimit -a

# Key limits that affect Java services:
# open files:    ulimit -n  (default 1024; too low for prod!)
# max user procs: ulimit -u

# Set for Java service (in systemd unit file):
# LimitNOFILE=65536
# LimitNPROC=4096

# Check a running process's limits
cat /proc/<pid>/limits
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| One program = one process | Programs can create multiple processes (Apache's pre-fork model; Nginx worker processes). Each separate `java` command is a separate OS process. |
| Processes run truly in parallel on a single CPU | On a single-core CPU, processes time-slice — they take turns. True parallelism requires multiple CPU cores (one process per core at a given moment). |
| Killing a parent process kills all children | By default on Linux, children become orphans adopted by init (PID 1) when the parent dies. SIGKILL to parent does NOT automatically kill children. |
| Processes are always slower than threads | Process creation and context switching is slower than threads, but processes provide stronger isolation. Nginx's multi-process model outperforms some multi-thread models in security and fault isolation. |
| Java threads are OS processes | Java threads are kernel threads within a single OS process. Multiple Java threads share the same JVM process address space. |

### 🔥 Pitfalls in Production

**1. File Descriptor Leak — Exhausting Process Limits**

```java
// BAD: FileInputStream not closed → file descriptor leak
FileInputStream fis = new FileInputStream("data.txt");
// exception thrown before close → fd never released
// After ~1024 fds: "too many open files"

// GOOD: Always use try-with-resources
try (FileInputStream fis = new FileInputStream("data.txt")) {
    // auto-closed
}

// Monitor: lsof -p <pid> | wc -l
// Configure: ulimit -n 65536 (raise fd limit)
```

**2. Zombie Processes — Unreaped Child Processes**

```bash
# BAD: Spawning child processes without waiting for them
Process child = Runtime.getRuntime().exec("./script.sh");
# If child exits before parent calls waitFor(),
# child enters zombie state (Z in ps output)
# Zombie holds PID allocation; too many → PID exhaustion

# GOOD: Always wait for or properly reap child processes
int exitCode = child.waitFor();
# Or use ProcessBuilder with redirects to avoid zombies
```

**3. Missing Graceful Shutdown on SIGTERM**

```java
// BAD: JVM exits abruptly on SIGTERM (Kubernetes sends SIGTERM before SIGKILL)
// All in-progress requests dropped; data may be corrupted

// GOOD: Register shutdown hook for graceful shutdown
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    log.info("Received SIGTERM, draining requests...");
    server.stop(30, TimeUnit.SECONDS);
    // Wait for in-flight requests to complete
    log.info("Graceful shutdown complete");
}));
```

### 🔗 Related Keywords

- `Thread (OS)` — a lighter-weight execution unit that runs within a process.
- `Process vs Thread` — the key distinction between isolated and shared memory models.
- `Context Switch` — the OS operation of saving one process's state and loading another's.
- `Virtual Memory` — gives each process the illusion of its own private address space.
- `System Call (syscall)` — how processes request OS services (file I/O, network, fork).
- `Inter-Process Communication (IPC)` — mechanisms for processes to share data.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Running program + isolated virtual address │
│              │ space + OS-managed resources = process.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fault isolation (crash one, not all);     │
│              │ security boundary (separate secrets);     │
│              │ different environments per component.     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Low-latency IPC needed between components │
│              │ → use threads instead (shared memory).    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Process: a program running in its own    │
│              │ sealed apartment — neighbours can't peek."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread (OS) → Context Switch → Virtual    │
│              │ Memory → System Call                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a containerised environment (Docker on Linux), each container appears to be its own isolated server, but containers on the same host actually share the OS kernel. Explain precisely which process isolation mechanisms Linux uses to achieve this container isolation (namespaces, cgroups) and identify what specifically containers do NOT isolate compared to full virtual machines — focusing on what kernel vulnerability in one container could affect others on the same host.

**Q2.** When `fork()` is called on Linux, the child process gets a copy of the parent's virtual address space, but the OS uses Copy-on-Write (CoW) rather than immediately copying all memory pages. Explain how CoW defers the actual copying until one of the processes writes to a shared page, and why a Java web server that forks child processes immediately after loading 2 GB of class data into the JVM heap might initially appear to use only marginally more memory than the original process — but eventually converges to 4 GB total usage under load.

