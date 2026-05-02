---
layout: default
title: "Zombie Processes"
parent: "Linux"
nav_order: 162
permalink: /linux/zombie-processes/
number: "0162"
category: Linux
difficulty: ★★☆
depends_on: Process Management
used_by: Shell Scripting, Containers, Java
related: Process Management, Signals, Cgroups
tags:
  - linux
  - os
  - processes
  - debugging
---

# 162 — Zombie Processes

⚡ TL;DR — A zombie process is a process that has exited but whose exit status has not yet been collected by its parent; it exists only as an entry in the process table. Accumulation indicates a parent not calling `wait()`, which in containers means PID 1 is failing its zombie-reaping responsibility.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
When a child process exits, the OS needs somewhere to store its exit status (exit code, resource usage) until the parent process retrieves it with `wait()`. If this information is simply deleted when the process exits, the parent can never know whether the child succeeded or failed, or how long it ran.

**THE BREAKING POINT:**
A parent spawns thousands of short-lived child processes (web server workers, shell command substitutions) without calling `wait()`. Each child exits, but the kernel must retain its process table entry to preserve the exit status. If the parent never calls `wait()`, these table entries accumulate. The process table has a finite size (typically PID_MAX = 32768 or 4194304). When it fills up: `fork()` fails — the system can create no new processes. System-wide outage.

**THE INVENTION MOMENT:**
The Unix design solution is simple: the kernel retains a minimal "zombie" entry (just the PID, exit status, and resource usage) after a process exits. The parent is expected to call `wait()` or `waitpid()` to collect this information (called "reaping"). Once reaped, the zombie is removed entirely. A parent that exits without reaping its children causes those children to be re-parented to PID 1 (init), which reaps them. In containers, if PID 1 doesn't reap, zombies accumulate.

---

### 📘 Textbook Definition

A **zombie process** (or "defunct process") is a process that has completed execution but still has an entry in the process table because its parent has not yet called `wait()` or `waitpid()` to read its exit status. The zombie consumes minimal resources (just a process table slot) but holds a PID. The kernel sends `SIGCHLD` to the parent when a child exits, notifying it to call `wait()`. If the parent never responds, the zombie persists until the parent exits (at which point the zombie is re-parented to PID 1 and immediately reaped).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A zombie is a process that's finished but can't fully disappear because its parent hasn't picked up its exit code yet.

**One analogy:**

> A zombie is like a checked-out hotel guest who has physically left the room but whose checkout paperwork is still on the front desk — they no longer occupy a room, but their record still exists until staff processes it. Hundreds of unprocessed checkouts (zombies) eventually fill the hotel's ledger (process table). The solution: a manager (parent process) that regularly processes checkouts, or a supervisor (PID 1 / init) that handles uncollected checkouts when the original manager leaves.

**One insight:**
Zombies are not a bug — they are a necessary and brief transitional state. One zombie for a few milliseconds is normal. Thousands of zombies that never get reaped means a broken parent process, and eventually fork() failures.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every process that exits becomes a zombie until its exit status is collected.
2. `wait()` / `waitpid()` by the parent reaps the zombie and frees the process table entry.
3. If a parent exits before reaping, orphaned children (including zombies) are adopted by PID 1.
4. PID 1 (init/systemd) reaps adopted zombies automatically.
5. In containers, PID 1 is the application — it must reap zombies or they accumulate.

**DERIVED DESIGN:**

**The life cycle of a child process:**

```
fork() → child running → child exits → SIGCHLD sent to parent
                                            │
                              parent calls wait() → zombie cleared
                              parent ignores     → zombie persists
                              parent exits       → zombie re-parented to PID 1
                                                   PID 1 reaps it
```

**Why the zombie state exists:**
The child's exit status (exit code from `exit()`, or signal number if killed) must be preserved somewhere for the parent to read. The kernel stores this in the process table entry. Once `wait()` is called, the kernel copies the status to the parent and deletes the entry. If the kernel deleted the entry on process exit, the parent could never call `wait()` to get the status — it would get ECHILD ("no child processes").

**THE TRADE-OFFS:**
Zombies are unavoidable by design. The responsibility is on the programmer to call `wait()` promptly. The trade-off is between: always calling `wait()` synchronously (simpler but blocks the parent) vs using `SIGCHLD` handler (non-blocking, complex to implement correctly). Most production code uses `waitpid(-1, WNOHANG)` in a SIGCHLD handler to reap all exited children without blocking.

---

### 🧪 Thought Experiment

**SETUP:**
A Docker container runs a shell script as PID 1. The script starts a web server and a monitoring agent as background processes.

```bash
#!/bin/bash
# entrypoint.sh (PID 1)
/app/server &
/app/monitor &
wait  # waits for both
```

**SCENARIO A — Monitoring agent crashes repeatedly:**

```
/app/monitor exits (crash)
SIGCHLD sent to PID 1 (the shell)
Shell's wait builtin reaps it (for the specific PIDs) ✓
BUT: any processes that /app/server spawned and
     that have since exited are also waiting to be
     reaped. The shell is NOT a zombie reaper for
     all orphaned processes.
```

**SCENARIO B — Using `tini` as PID 1:**

```
PID 1: tini
PID 2: /app/server (spawned by tini)
PID 3: /app/monitor (spawned by tini)

/app/server spawns worker processes (PIDs 10-100)
Workers exit → re-parented to PID 1 (tini)
tini calls waitpid(-1, WNOHANG) in a loop → reaps all
No zombie accumulation regardless of process tree structure
```

**THE INSIGHT:**
The issue is not about the direct children of the entrypoint — it's about all processes in the container's PID namespace that exit and whose parent also exits before reaping them. These orphans are re-parented to PID 1. If PID 1 is a shell script or application that doesn't call `waitpid(-1, ...)` in a loop, they become permanent zombies.

---

### 🧠 Mental Model / Analogy

> Think of process management as a hospital. When a patient (process) is discharged (exits), their room is freed immediately — but their medical record (process table entry) must be retained until the attending physician (parent process) reviews and signs off on the case (calls wait()). A zombie patient has left the building but their paperwork is still on the desk. If the attending physician also leaves without signing off, hospital administration (PID 1 / init) takes over the paperwork. If administration also never processes the paperwork, the filing system fills up and no new patients can be admitted (fork() fails).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A zombie is a process that has finished but is waiting for its parent to acknowledge that it finished. It uses almost no resources but takes up a slot in the process table. Too many zombies = no new processes can start. The fix: the parent needs to call `wait()`, or PID 1 needs to clean them up.

**Level 2 — How to use it (junior developer):**
Spot zombies: `ps aux | grep Z` (status column shows `Z`). Count them: `ps aux | awk '$8 ~ /^Z/ {count++} END {print count}'`. Find the parent: `ps -o ppid= -p <zombie_PID>` — if parent is still alive and zombies keep accumulating, the parent has a bug. In containers: add `tini` as PID 1. In Docker: `docker run --init myimage` adds tini automatically.

**Level 3 — How it works (mid-level engineer):**
When a process exits, the kernel: (1) frees all resources (memory, file descriptors, etc.); (2) retains the `task_struct` (process table entry) with the exit status; (3) sends `SIGCHLD` to the parent. The parent calls `waitpid(child_pid, &status, 0)` or `wait(&status)`. The kernel copies exit status to `status`, frees the `task_struct`, and decrements the PID counter. `WNOHANG` flag makes `waitpid` non-blocking (returns 0 if no children have exited yet). `waitpid(-1, &status, WNOHANG)` reaps any child — call in a loop until it returns -1 (no more children to reap). In C: install a `SIGCHLD` signal handler that calls `while(waitpid(-1, NULL, WNOHANG) > 0);`.

**Level 4 — Why it was designed this way (senior/staff):**
The zombie state is a direct consequence of the Unix process model's guarantee: a parent can always determine the exit status of a child it created, at any point before it calls `wait()`. This guarantee enables reliable process supervision — a supervisor (like systemd, runit, or s6) can fork a worker, do other work, then check exit status without a race condition. The alternative (kernel immediately deletes the entry) would create a window where the exit status is lost. The PID 1 adoption mechanism (`PPID → 1` when parent exits) is the system's self-healing mechanism: even if a parent is badly written, the system won't accumulate zombies forever if PID 1 is well-written. This is why systemd's zombie reaping is a core responsibility, and why `tini` (which does only two things: zombie reaping and signal forwarding) exists.

---

### ⚙️ How It Works (Mechanism)

**Detecting zombies:**

```bash
# Show all processes, look for Z in STAT column
ps aux
# USER  PID  %CPU %MEM  STAT  COMMAND
# root  1234  0.0  0.0   Z    [myapp] <defunct>

# Count zombies
ps aux | awk 'NR>1 && $8~/^Z/{count++} END{print count+0}'

# Find zombie's parent
ZOMBIE_PID=1234
PARENT_PID=$(ps -o ppid= -p $ZOMBIE_PID | tr -d ' ')
echo "Zombie $ZOMBIE_PID has parent $PARENT_PID"
ps -p $PARENT_PID -o pid,ppid,cmd
```

**Creating and reaping children in C (correct pattern):**

```c
#include <sys/wait.h>
#include <signal.h>
#include <unistd.h>

// SIGCHLD handler: reap all exited children non-blocking
void sigchld_handler(int signo) {
    int saved_errno = errno;
    pid_t pid;
    int status;
    // Loop: WNOHANG returns 0 when no more children to reap
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        // pid has exited; status contains exit code
        if (WIFEXITED(status)) {
            int code = WEXITSTATUS(status);
            // log: child pid exited with code
        } else if (WIFSIGNALED(status)) {
            int sig = WTERMSIG(status);
            // log: child pid killed by signal sig
        }
    }
    errno = saved_errno;  // preserve errno for interrupted calls
}

int main() {
    struct sigaction sa;
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sa, NULL);

    // Now fork children freely; handler will reap them
    while (1) {
        pid_t child = fork();
        if (child == 0) {
            // child work
            _exit(0);
        }
        // parent continues; SIGCHLD handler will reap child
        sleep(1);
    }
}
```

**Docker — adding tini:**

```bash
# Option 1: --init flag (uses host tini)
docker run --init myimage python app.py

# Option 2: Dockerfile with tini
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "app.py"]

# Option 3: Download tini in Dockerfile
FROM ubuntu:22.04
ARG TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/\
${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["python", "app.py"]
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Zombie accumulation in a container (BAD PATH) │
└────────────────────────────────────────────────┘

 Container PID namespace:
 PID 1: /bin/sh -c "./server"
 PID 2: ./server (main process)
 PID 3-10: ./server worker processes

 Worker (PID 7) completes a task → exits
       │
       ▼
 Kernel: frees memory, fds
         retains task_struct (zombie)
         sends SIGCHLD to PID 2 (./server)
       │
       ▼
 ./server: no SIGCHLD handler, no wait() call
           ignores SIGCHLD
 PID 7: remains zombie ← PROBLEM
       │
 Hundreds of workers exit over time
       ▼
 Process table fills: PID_MAX reached
       │
       ▼
 fork() returns -EAGAIN
 "Cannot allocate memory"
 Server can no longer spawn workers → OUTAGE

 ════════════════════════════════════════════

 GOOD PATH: tini as PID 1

 PID 1: tini (zombie reaper + signal forwarder)
 PID 2: ./server

 Worker (PID 7) exits
       │
       ▼
 kernel: zombie created, SIGCHLD to PID 2
 ./server: may or may not handle it
 PID 7's parent (PID 2) exits eventually
       │
       ▼
 PID 7 re-parented to PID 1 (tini)
       │
       ▼
 tini: waitpid(-1, WNOHANG) in event loop
       reaps PID 7 immediately
 PID 7: removed from process table ✓
```

---

### 💻 Code Example

**Example — Python subprocess with proper wait():**

```python
import subprocess
import signal
import os

# BAD: create processes without waiting
# Zombies accumulate until parent exits
def bad_pattern():
    for _ in range(10):
        proc = subprocess.Popen(["sleep", "0.1"])
        # proc never waited on → zombie until parent exits

# GOOD: always wait for subprocesses
def good_pattern():
    procs = []
    for _ in range(10):
        proc = subprocess.Popen(["sleep", "0.1"])
        procs.append(proc)

    # Reap all
    for proc in procs:
        proc.wait()
    # No zombies: all exit statuses collected

# GOOD for async: use communicate() or poll()
def async_pattern():
    proc = subprocess.Popen(
        ["long_running_task"],
        stdout=subprocess.PIPE
    )
    # do other work...
    stdout, _ = proc.communicate()  # waits + reads output
    exit_code = proc.returncode
    print(f"Exited with: {exit_code}")
    # proc reaped: no zombie

# Check for zombies in current process's children
def check_my_zombies():
    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        try:
            status_path = f'/proc/{entry}/status'
            with open(status_path) as f:
                for line in f:
                    if line.startswith('State:') and 'Z' in line:
                        ppid_path = f'/proc/{entry}/status'
                        with open(ppid_path) as f2:
                            for l in f2:
                                if l.startswith('PPid:'):
                                    ppid = l.split()[1]
                                    if ppid == str(os.getpid()):
                                        print(f"Zombie child: {entry}")
        except (IOError, OSError):
            pass
```

---

### ⚖️ Comparison Table

| State                   | Description                          | Resources Used | Fix                                  |
| ----------------------- | ------------------------------------ | -------------- | ------------------------------------ |
| **Zombie (Z)**          | Exited, waiting for parent wait()    | PID slot only  | Parent calls wait(); or parent exits |
| **Orphan**              | Parent exited; re-parented to PID 1  | Full resources | PID 1 will reap                      |
| **Sleeping (S)**        | Interruptible wait (I/O, timer)      | Full resources | Normal operation                     |
| **Uninterruptible (D)** | Waiting for I/O, cannot be signalled | Full resources | Disk/NFS hang — hard to fix          |
| **Stopped (T)**         | Paused by SIGSTOP                    | Full resources | SIGCONT to resume                    |

How to choose: zombies are harmless in small numbers; act when `ps aux | awk '$8~/Z/'` returns more than a handful; an uninterruptible (D) state process is more serious than a zombie — it means blocked I/O.

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                    |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zombie processes consume CPU and memory    | Zombies hold only a process table entry (a few hundred bytes); they use no CPU or memory (the process has fully exited)                                    |
| `kill -9` can kill a zombie                | SIGKILL cannot kill a zombie — the process is already dead; the entry persists until the parent calls wait(); killing the parent is the fix                |
| Zombies cause immediate problems           | A few zombies are harmless; problems only arise when thousands accumulate and fill the process table (PID_MAX exhaustion)                                  |
| init (PID 1) always reaps orphaned zombies | Only if PID 1 is a proper init that calls waitpid(-1, ...); if PID 1 is a custom application (common in containers), it must implement reaping or use tini |
| The shell always reaps child processes     | Interactive shells reap children; but scripts using `&` background processes may not reap them before the script exits                                     |

---

### 🚨 Failure Modes & Diagnosis

**`fork(): Cannot allocate memory` Despite Plenty of RAM**

**Symptom:**
Application fails to fork with `EAGAIN` or "Cannot allocate memory" despite free RAM. `ps aux` shows hundreds of `<defunct>` (Z) processes.

**Root Cause:**
Process table full due to zombie accumulation. PID_MAX exhausted. Usually: parent process that spawns many short-lived children without calling `wait()`.

**Diagnostic Commands:**

```bash
# Count zombies
ps aux | awk '$8~/^Z/{count++} END{print count+0}'

# Find parent of zombies
ps aux | awk '$8~/^Z/{print "Zombie:", $2, "Parent:", $3}' | head -20
# Then: ps -p <PARENT_PID> -o pid,ppid,cmd

# Check current PID count vs max
cat /proc/sys/kernel/pid_max
ls /proc | grep -E '^[0-9]+$' | wc -l

# Fix: if parent can't be fixed, kill the parent
# (zombies will be re-parented to PID 1 and reaped)
kill -SIGTERM <PARENT_PID>

# In containers: restart container (or add --init flag)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management` — zombies arise from the parent-child process relationship; understanding fork(), wait(), and PPID is foundational

**Builds On This (learn these next):**

- `Signals` — SIGCHLD is the signal that notifies parents their child has changed state; zombie reaping is done in response to SIGCHLD
- `Containers` — zombie accumulation in containers is a practical problem caused by PID 1 not being a proper init; tini/dumb-init solve this

**Alternatives / Comparisons:**

- `tini` — minimal init process (PID 1) that does signal forwarding and zombie reaping; standard solution for containers
- `dumb-init` — similar to tini; Python-based, slightly heavier
- `systemd` — full init system that handles zombie reaping as one of many responsibilities; used on host systems, not in containers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Process that exited but parent hasn't     │
│              │ called wait() — holds only a PID slot     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Thousands of zombies fill process table   │
│ CAUSES       │ → fork() fails → system-wide outage       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ kill -9 cannot kill a zombie; kill the    │
│              │ parent (which causes re-parenting to      │
│              │ PID 1 for reaping)                        │
├──────────────┼───────────────────────────────────────────┤
│ CONTAINER    │ PID 1 must reap zombies; use tini or      │
│ RULE         │ docker run --init                         │
├──────────────┼───────────────────────────────────────────┤
│ DETECT       │ ps aux | grep Z (defunct)                 │
│              │ Harmless in small numbers; act at 10+     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Checked-out guest whose paperwork is     │
│              │ still on the front desk"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ tini → init systems → process supervision │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Node.js application running as PID 1 in a container uses `child_process.spawn()` to run short-lived shell commands (e.g., health checks). Explain: (a) whether Node.js's event loop automatically reaps child processes, (b) what happens if the process exits without being awaited, (c) what `SIGCHLD` handling Node.js performs internally, and (d) whether `--init` in Docker is still necessary when using Node.js as PID 1 — with specific reference to what tini provides beyond zombie reaping.

**Q2.** Describe the complete sequence of system calls involved in creating and reaping a child process: `fork()` → child runs → child calls `exit(0)` → parent calls `waitpid()`. For each step, name the kernel data structure that is created, modified, or freed — specifically what fields of `task_struct` change at each transition, and at what point the process table entry (and PID) is fully released for reuse.
