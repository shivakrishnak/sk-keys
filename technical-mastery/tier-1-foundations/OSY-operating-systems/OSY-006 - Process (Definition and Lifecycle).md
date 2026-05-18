---
id: OSY-006
title: Process (Definition and Lifecycle)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-001
used_by: OSY-007, OSY-019, OSY-029
related: OSY-007, OSY-009, OSY-019
tags:
  - foundational
  - process
  - lifecycle
  - pcb
  - scheduling
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/osy/process/
---

## TL;DR

A process is a program in execution - an instance of
a program loaded into memory with its own address space,
file descriptors, and CPU state. It transitions through
New, Ready, Running, Blocked, and Terminated states
managed by the OS scheduler.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-006 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | process, lifecycle, PCB, scheduler |
| **Prerequisites** | OSY-001 |

---

### The Problem This Solves

A program is static: code on disk. A process is dynamic:
that code running, with a specific memory state, a
current instruction being executed, open files, and a
stack of function calls. The distinction matters because
you can run the same program 100 times simultaneously
as 100 different processes. Each has its own isolated
state. Killing one does not affect the others.

---

### Process vs Program

```
Program: /usr/bin/java (file on disk)
Process: java -jar myapp.jar (running instance, PID 42381)

Same program, multiple processes:
  PID 42381: java -jar service-A.jar  (Port 8080)
  PID 42382: java -jar service-B.jar  (Port 8081)
  
Each process has its own:
  - Virtual address space (private memory)
  - File descriptor table (open files, sockets)
  - CPU state (registers, stack pointer)
  - PID (process identifier)
  - UID/GID (security credentials)
```

---

### Process Control Block (PCB)

```
The OS tracks each process in a data structure called
the Process Control Block (PCB):

PCB fields:
  PID         - unique process identifier
  State       - New/Ready/Running/Blocked/Terminated
  PC          - program counter (next instruction address)
  CPU regs    - saved register values (on context switch)
  CPU sched   - priority, time quantum used
  Memory mgmt - page table pointer, segments
  I/O status  - open file descriptors, I/O requests
  Accounting  - CPU time used, wall clock time

On Linux: PCB = task_struct in kernel source code
  (c.  7,000 lines of fields)
  
Read it: /proc/PID/status gives user-readable PCB summary
```

---

### Process Lifecycle (State Machine)

```
         fork()            Schedule
  NEW ---------> READY -----------> RUNNING
                   ^                    |  |
        I/O done  |    I/O request      |  | exit()
        timer exp |    sleep()          |  |
                  |    wait()           v  v
               READY <--------- BLOCKED   TERMINATED
               
States:
  NEW:        Process being created (fork in progress)
  READY:      In run queue, waiting for CPU
  RUNNING:    Executing on CPU (1 per core)
  BLOCKED:    Waiting for I/O, signal, or event
  TERMINATED: Exited; PCB still exists until parent
              calls wait() to collect exit status
              (if no wait(): "zombie" process)

Linux state in /proc/PID/status:
  R = Running/Runnable
  S = Sleeping (interruptible)
  D = Disk sleep (uninterruptible - I/O wait)
  Z = Zombie (exited, parent not collected)
  T = Traced/Stopped
```

---

### Process Creation on Linux

```java
// In Java: when you start a new JVM process
ProcessBuilder pb = new ProcessBuilder("ls", "-la");
Process p = pb.start();         // fork() + exec() internally
int exit = p.waitFor();         // wait() in OS terms

// OS perspective:
// fork():    clone the parent process (COW memory copy)
//            Child PID = new number, parent PID = ppid
// exec():    replace the child's code+data with new binary
//            Stack, heap, file descriptors reset
// wait():    parent blocks until child terminates
//            Collects exit status, frees zombie PCB

// Without wait(): child becomes zombie until parent exits
// Fix: always call waitFor() or use ProcessBuilder.inheritIO()
```

---

### Textbook Definition

A process is an OS abstraction representing a running
instance of a program. The OS maintains a Process
Control Block (PCB) for each process containing its
state, CPU registers, memory map, file descriptor table,
and scheduling information. Processes transition between
states (Ready, Running, Blocked, Terminated) under OS
scheduler control.

---

### Understand It in 30 Seconds

A process is a program + its current execution state.
The OS tracks each process in a PCB. The scheduler
moves processes between Ready, Running, and Blocked
states. fork() creates a copy; exec() replaces the copy
with a new program; wait() reaps the exit status.

---

### How It Works

```
Process creation via fork():
  1. OS copies parent's PCB into new child PCB
  2. New PID assigned
  3. Memory: Copy-on-Write (physical pages shared until
     either process writes - then OS copies the page)
  4. File descriptors: shared (same reference counted
     inode entries - be careful with open files post-fork)
  5. fork() returns: 0 in child, child's PID in parent

exec() after fork():
  1. Loads new binary from disk into child's address space
  2. Resets stack, heap, data segment
  3. Preserves: PID, open file descriptors (unless O_CLOEXEC)
  4. Begins execution at new program's entry point (main)

Zombie and orphan processes:
  Zombie: child exited but parent hasn't called wait()
    Fix: parent must call waitFor() / wait()
    Danger: zombie holds PID; too many zombies = PID exhaustion
    
  Orphan: parent exited before child
    OS reparents orphan to init (PID 1 / systemd)
    init calls wait() periodically to clean up
```

---

### Complete Picture - End-to-End Flow

```
Application -> OS lifecycle for a simple web request:

1. nginx process (PID 1234): BLOCKED on accept()
2. Client connects -> socket readable -> nginx moves to READY
3. Scheduler: cpu free -> nginx moves to RUNNING
4. nginx parses request, calls fork()
5. Worker process (PID 5678): RUNNING (parent RUNNING too, briefly)
6. Worker calls read() from database (I/O) -> BLOCKED
7. Scheduler: picks another READY process to run
8. Database responds -> I/O complete -> Worker moves to READY
9. Scheduler: Worker moves to RUNNING
10. Worker writes response, calls exit()
11. Worker: TERMINATED (zombie until parent wait())
12. nginx (PID 1234): wait() collects exit status, zombie freed
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "One JVM = one process" | Correct by default, but spark.submit and similar frameworks fork JVM processes. A JVM process is just a regular Linux process with a special runtime |
| "A zombie process wastes CPU and memory" | A zombie is just a PCB entry (a few KB) with no running code. It wastes a PID slot. The danger is accumulation - PID exhaustion causes fork() failures |
| "Killing a parent kills its children" | Only if the parent has properly propagated signals. Orphaned children survive and are reparented to init. Docker ENTRYPOINT PID 1 must propagate SIGTERM to all children or they become orphans |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Zombie accumulation | `ps aux` shows many `Z` processes | Parent not calling wait() | Always call waitFor() in Java; check for missing wait() in fork() |
| PID exhaustion | `fork: retry: Resource temporarily unavailable` | Max PIDs reached (default 32768 on Linux) | Identify zombie leak; increase /proc/sys/kernel/pid_max |
| Fork bomb | System unresponsive, high process count | Unbounded process creation loop | Set process limit in /etc/security/limits.conf (nproc) |
| Security | Privileged process forks without dropping privileges | Child inherits parent's UID 0 | Call setuid() in child after fork() before exec() |

---

### Related Keywords

**Prerequisites:** OSY-001 (Why OS Exists)

**Next steps:** OSY-007 (Thread), OSY-019 (fork and exec),
OSY-033 (Memory Layout of Process)

**Advanced:** OSY-057 (Copy-on-Write Mechanism),
OSY-072 (Process Isolation), OSY-089 (Kernel Internals)

---

### Quick Reference Card

| Concept | Value |
|---------|-------|
| Process = | Program + execution state + resources |
| PCB contains | PID, state, registers, memory map, FDs |
| Process states | New, Ready, Running, Blocked, Terminated |
| fork() returns | 0 in child, child PID in parent |
| Zombie cause | Child exited, parent hasn't called wait() |
| Orphan handling | init (PID 1) adopts orphaned processes |

**3 things to remember:**
1. Process = program + state (not just code on disk)
2. fork() + exec() is the Unix process creation model
3. Always wait() for child processes or zombies accumulate

---

### Transferable Wisdom

Process lifecycle (New → Ready → Running → Blocked → 
Terminated) is the same state machine pattern as:
- HTTP request lifecycle (queued → processing → done)
- Database connection lifecycle (available → acquired → released)
- Kubernetes Pod lifecycle (Pending → Running → Succeeded)
The OS process model is the universal template for any
resource with a lifecycle.

---

### The Surprising Truth

The maximum number of processes on a default Linux system
is 32,768 (2^15), set by kernel PID_MAX. A classic
"fork bomb" - `:(){ :|:& };:` in bash - creates processes
exponentially until this limit is hit, causing a denial
of service. The fix is the `nproc` limit in
`/etc/security/limits.conf`. Correctly setting process
limits is a mandatory security hardening step for any
production Linux server, yet it is routinely omitted
from default cloud VM configurations.

---

### Mastery Checklist

- [ ] Can distinguish a process from a program (instance vs code)
- [ ] Knows all 5 process states and transitions between them
- [ ] Understands PCB and what it contains
- [ ] Can explain fork() + exec() semantics
- [ ] Knows what a zombie process is and how to prevent it

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between a program
and a process?

*Answer:* A program is a static file on disk (e.g.,
`/usr/bin/java`). A process is a running instance of
that program - it has a PID, a private virtual address
space, CPU state (registers, stack), open file descriptors,
and current execution position. You can run the same
program as multiple simultaneous processes.

---

**Q2 (Medium):** What is a zombie process and how do you
prevent it?

*Answer:* A zombie process is a process that has exited
but whose PCB (exit status) has not been collected by
its parent via `wait()`. It holds a PID slot but consumes
no CPU or significant memory. Prevention: always call
`waitFor()` on child processes in Java. If the parent
exits before collecting, init (PID 1) adopts the zombie
and calls wait(). Danger: zombie accumulation exhausts
PID space, causing fork() failures.

---

**Q3 (Hard):** When Java's ProcessBuilder.start() is
called, what OS operations happen, and what file
descriptor risks exist?

*Answer:* `start()` calls `fork()` to clone the JVM
process, then `exec()` in the child to replace it with
the target binary. Risks: (1) the child inherits all
parent file descriptors unless `O_CLOEXEC` is set -
open DB connections, log file handles, sockets all leak
to child unless explicitly closed. (2) fork() + JVM:
if the parent has multiple threads, only the calling
thread is forked; other threads are gone in the child
(fork-safety issue). Solution: use `O_CLOEXEC` on all
FDs, or use ProcessBuilder with a clean environment.
