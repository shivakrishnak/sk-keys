---
id: OSY-023
title: Build and Inspect a Process (OS Lab Phase 1)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006, OSY-007, OSY-019, OSY-021
used_by: OSY-041
related: OSY-006, OSY-021, OSY-041
tags:
  - practice
  - lab
  - process
  - hands-on
  - phase-1
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/osy/os-lab-phase-1/
---

## TL;DR

Hands-on lab: spawn a Java process, inspect its PCB via
/proc, observe memory layout, and trace its system calls.
Completion criteria: can read a process's state, memory,
and syscalls without help.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-023 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | lab, practice, process inspection |
| **Prerequisites** | OSY-006, OSY-007, OSY-019, OSY-021 |

---

### Lab Prerequisites

```
Required tools (Linux environment):
  Java 21+ (JDK)
  ps, top, vmstat (built-in on all Linux)
  strace (sudo apt install strace / yum install strace)
  /proc filesystem (available on all Linux)
  
Optional but recommended:
  htop (better UI for top)
  lsof (file descriptor listing)
  pmap (process memory map)
```

---

### Exercise 1: Spawn and Inspect a Process

```java
// InfiniteLoop.java - simple program to inspect
public class InfiniteLoop {
    public static void main(String[] args)
            throws InterruptedException {
        System.out.println("PID: " + ProcessHandle.current().pid());
        System.out.println("Running... Ctrl+C to stop");
        while (true) {
            Thread.sleep(1000); // sleep (blocked, low CPU)
        }
    }
}
```

```bash
# Terminal 1: Run the program
java InfiniteLoop.java
# Note the PID printed

# Terminal 2: Inspect the process
PID=<from above>

# 1. Process state
ps aux | grep java
# STAT column: S = sleeping (in sleep()), R = running

# 2. Memory layout
cat /proc/$PID/status
# Look for: VmRSS (resident), VmVirt (virtual),
# Threads (thread count), State (S for sleeping)

# 3. Complete memory map
cat /proc/$PID/maps | head -30
# Shows all virtual memory regions:
# 7f8a00000000-7f8a20000000 rw-p ... heap
# 7fff12345678-7fff1234c000 rw-p ... stack
# 7f8b00000000-7f8b01000000 r-xp ... libc.so (code)

# 4. Open file descriptors
ls -la /proc/$PID/fd
# Shows: 0->stdin, 1->stdout, 2->stderr, more for JVM files

# 5. Thread listing
ls /proc/$PID/task/
# Each directory = one thread (TID)
# Count them: ls /proc/$PID/task/ | wc -l
# JVM typically has 10-20 background threads

# 6. Real-time CPU and memory
top -H -p $PID
# -H: show threads, -p: specific PID
```

---

### Exercise 2: Observe System Calls

```bash
# Trace system calls made by the InfiniteLoop program
# Must restart program with strace prefix:
strace java InfiniteLoop.java 2>&1 | head -50

# Expected to see:
# execve("/usr/bin/java", ...) = 0
# brk(NULL) = 0x...           (heap setup)
# mmap(...) = 0x...           (memory mapping)
# openat(..., "rt.jar") = 3   (JVM loading)
# nanosleep({...}, NULL) = 0  (our sleep(1000))

# Count syscalls by type:
strace -c java -version 2>&1
# Shows syscall frequency table:
# % time   seconds  usecs/call  calls  syscall
# 40.12    0.004218         42    100  mmap
# 15.23    0.001600         16    100  openat
```

---

### Exercise 3: Process Lifecycle Observation

```bash
# Terminal 1: Monitor process state changes
watch -n 0.5 'ps aux | grep InfiniteLoop'

# Terminal 2: Run and kill the process
java InfiniteLoop.java &
PID=$!
sleep 2
kill -SIGSTOP $PID  # pause (state: T = stopped)
sleep 2
kill -SIGCONT $PID  # resume (state: S = sleeping)
sleep 2
kill -SIGTERM $PID  # terminate gracefully

# Terminal 1: Watch state transitions:
# S -> T (after SIGSTOP)
# T -> S (after SIGCONT)
# S -> Z (zombie briefly after exit) -> gone (after wait)
```

---

### Exercise 4: Fork and Exec Observation

```java
// ProcessCreation.java
public class ProcessCreation {
    public static void main(String[] args) throws Exception {
        System.out.println("Parent PID: " +
            ProcessHandle.current().pid());
        
        // Fork + exec via ProcessBuilder
        ProcessBuilder pb = new ProcessBuilder(
            "ps", "aux", "--ppid",
            String.valueOf(ProcessHandle.current().pid()));
        pb.inheritIO();
        Process child = pb.start();
        
        System.out.println("Child PID: " + child.pid());
        int exit = child.waitFor();
        System.out.println("Child exit code: " + exit);
    }
}
```

```bash
java ProcessCreation.java
# Observe: parent PID, child PID (child PID = parent PID + 1 or so)
# ps output shows: child ps process with PPID = parent java

strace -f -e trace=clone,execve,wait4 java ProcessCreation.java
# -f: follow child processes
# See: clone() creating child, execve() for ps, wait4() waiting
```

---

### Completion Criteria

Mark yourself complete when you can do all of these without notes:
- [ ] Run a Java program and find its PID
- [ ] Read /proc/PID/status and interpret all key fields
- [ ] List all threads of a JVM process
- [ ] Count open file descriptors for a process
- [ ] Trace system calls with strace and identify the sleep() syscall
- [ ] Observe a process state transition (R -> S -> T -> Z)
- [ ] Use `top -H -p PID` to see JVM threads live

---

### The Surprising Truth

Every major production incident diagnosis starts with
exactly these steps: find the PID, check /proc/status
for memory and thread count, check /proc/maps for
memory layout anomalies, and run strace to see what the
process is actually doing. Senior engineers who can do
this from memory diagnose incidents in minutes. Engineers
who must look up each command diagnose them in hours.
This lab, practiced until muscle memory, is worth more
than any certification.
