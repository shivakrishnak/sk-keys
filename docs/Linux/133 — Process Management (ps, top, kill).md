---
layout: default
title: "Process Management (ps, top, kill)"
parent: "Linux"
nav_order: 133
permalink: /linux/process-management-ps-top-kill/
number: "0133"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy, Users and Groups, Operating System
used_by: Systemd / Init System, Shell Scripting, Observability & SRE
related: Systemd / Init System, Signals (SIGTERM, SIGKILL, SIGHUP), Zombie Processes
tags:
  - linux
  - os
  - foundational
  - production
---

# 133 — Process Management (ps, top, kill)

⚡ TL;DR — Linux process management lets you view every running program (ps, top), send signals to control them (kill), and understand the process tree — the foundation of all system administration and debugging.

| #133            | Category: Linux                                                             | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Linux File System Hierarchy, Users and Groups, Operating System             |                 |
| **Used by:**    | Systemd / Init System, Shell Scripting, Observability & SRE                 |                 |
| **Related:**    | Systemd / Init System, Signals (SIGTERM, SIGKILL, SIGHUP), Zombie Processes |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A production web server starts responding slowly. Requests time out. You suspect something is consuming all the CPU or memory. Without process visibility, you are blind — you cannot see what is running, cannot identify the culprit, cannot stop a runaway process, cannot distinguish a hung database connection from a memory leak. The only recourse would be rebooting the entire machine, taking down every service to fix one problem.

**THE BREAKING POINT:**
Without process management tools, a multi-process system is a black box. You cannot answer: "What is running right now? Who owns it? How much memory is it using? Has it been running for 3 seconds or 3 days? Is this the right binary or a rogue process?" Debugging production incidents without this information is impossible.

**THE INVENTION MOMENT:**
Unix was designed as a multi-process system from the start. The kernel tracks every running process in a process table. `ps` (process status) exposes this table to userspace. `top` gives a real-time view. `kill` (despite the name) sends signals to processes — including the graceful-shutdown signal `SIGTERM`. These tools exist because process visibility and control are the minimum viable interface to a running operating system.

---

### 📘 Textbook Definition

A **process** is a running instance of a program — an isolated execution context with its own PID (Process ID), memory space, file descriptor table, and execution state. Linux tracks all processes in the kernel's process table (`task_struct`). The `ps` command reads from `/proc/<PID>/` virtual filesystem entries to report process attributes. `top` provides a continuously-updated view of processes sorted by resource consumption. `kill` sends a **signal** — a software interrupt — to a process; despite its name, any POSIX signal can be sent (the default signal is `SIGTERM`, requesting graceful shutdown). `kill -9 PID` sends `SIGKILL`, which cannot be caught or ignored and immediately terminates the process.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ps` lists running processes; `top` shows them live; `kill` sends a signal to one of them — usually to stop it.

**One analogy:**

> Processes are like workers in a factory. `ps` is the attendance sheet — it lists every worker, their ID, what task they're doing, and how long they've been there. `top` is the factory floor manager walking around, watching who's working hardest in real time. `kill` is tapping a worker on the shoulder to give them an instruction — "please finish up and go home" (SIGTERM) or "you're fired immediately" (SIGKILL).

**One insight:**
`kill -9` (SIGKILL) is not a clean shutdown — it is an emergency circuit breaker. The process has no chance to flush buffers, close files, or release locks. Use `kill` (SIGTERM) first and give the process time to clean up. Use `kill -9` only when the process won't respond.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every process has a unique PID; every process (except PID 1) has a parent PPID.
2. Processes form a tree rooted at PID 1 (init/systemd).
3. Signals are the kernel's IPC mechanism for process control.

**DERIVED DESIGN:**

```
PROCESS TREE STRUCTURE:

PID 1 (systemd/init)
├── PID 234 (sshd)
│   └── PID 891 (sshd: alice@pts/0)
│       └── PID 892 (bash)
│           ├── PID 1023 (vim)
│           └── PID 1024 (python3 server.py)
├── PID 456 (nginx: master)
│   ├── PID 457 (nginx: worker)
│   └── PID 458 (nginx: worker)
└── PID 789 (postgres)
    ├── PID 790 (postgres: checkpointer)
    └── PID 791 (postgres: autovacuum)

Killing PID 456 with SIGTERM:
  - nginx master receives SIGTERM
  - master sends SIGQUIT to workers
  - workers finish in-flight requests
  - workers exit, then master exits

Killing PID 456 with SIGKILL:
  - nginx master instantly killed
  - workers become orphans (re-parented to PID 1)
  - in-flight requests dropped
```

**Process states:**

```
R  Running or runnable (on CPU or in run queue)
S  Sleeping (waiting for event, interruptible)
D  Uninterruptible sleep (usually waiting for I/O)
Z  Zombie (terminated but parent hasn't wait()'d)
T  Stopped (by SIGSTOP or job control)
I  Idle (kernel threads)
```

**THE TRADE-OFFS:**
`ps` is a snapshot — it reads `/proc` at a moment in time. `top` continuously updates but adds overhead. `kill -15 (SIGTERM)` is safe but requires the process to handle it. `kill -9 (SIGKILL)` is guaranteed but leaves no cleanup opportunity.

---

### 🧪 Thought Experiment

**SETUP:**
A Java application on a production server has been running for 3 days. Memory usage has climbed from 1GB to 7GB (the machine has 8GB). The garbage collector is running continuously but can't free memory (GC overhead limit exceeded). New requests are failing.

**WHAT HAPPENS WITHOUT PROCESS MANAGEMENT:**
You cannot see the problem. You cannot identify which process is consuming memory. You cannot confirm it's Java. You cannot send it a graceful shutdown signal. Your only option: reboot the server, affecting all co-hosted services.

**WHAT HAPPENS WITH PROCESS MANAGEMENT:**

```bash
# 1. Identify the culprit
top              # sorts by CPU; press 'M' for memory sort
# → java process at 87% memory, PID=12345

# 2. Get full details
ps aux | grep java
# → java 12345  ... /opt/myapp/bin/java -Xmx8g -jar app.jar

# 3. Graceful shutdown first
kill 12345       # sends SIGTERM → JVM shutdown hooks run → clean exit

# 4. If unresponsive after 30s:
kill -9 12345    # SIGKILL: no cleanup possible
```

You identified the exact process, attempted a clean shutdown, and had a fallback. Other services were unaffected.

**THE INSIGHT:**
Process management converts "something is wrong" into "process X is consuming Y resources and here is its PID" — a specific, actionable diagnosis.

---

### 🧠 Mental Model / Analogy

> The Linux process table is like an air traffic control radar screen. Every aircraft (process) has a unique transponder code (PID), a call sign (name), an altitude (memory), a speed (CPU%), and a status (running, waiting, landed). `ps` is a printed flight manifest. `top` is the live radar screen. `kill` is ATC broadcasting "Flight PID1234, please divert to runway 9" (SIGTERM) or "activating emergency stop procedure" (SIGKILL).

- "Aircraft transponder code" → PID
- "Flight origin" → PPID (parent process)
- "Fuel level" → available memory
- "Speed" → CPU usage percentage
- "ATC broadcast" → `kill` command (send signal)
- "Emergency stop" → SIGKILL (cannot be refused)

**Where this analogy breaks down:** Real aircraft can ignore ATC instructions (dangerous but possible); processes cannot ignore SIGKILL. SIGKILL is enforced by the kernel — not the process.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every program running on a Linux computer is called a "process." Linux gives each process a number (PID) so you can identify it. `ps` shows you all processes currently running. `top` shows them in real time. `kill` lets you stop a specific process by its number.

**Level 2 — How to use it (junior developer):**
`ps aux` — show all processes with CPU and memory. `top` — interactive; press `q` to quit, `k` to kill, `M` to sort by memory, `P` for CPU. `kill PID` — politely ask a process to stop. `kill -9 PID` — force-stop a process. `pkill name` — kill by name. `pgrep name` — get PIDs by name. `pidof nginx` — get PID of nginx. Always try SIGTERM (default) before SIGKILL; allow a few seconds.

**Level 3 — How it works (mid-level engineer):**
Each process is a `task_struct` in the kernel. `ps` reads `/proc/<PID>/status`, `/proc/<PID>/stat`, `/proc/<PID>/cmdline` — virtual files generated on the fly by the kernel from the task_struct. `top` uses a combination of `/proc/stat` (system-wide CPU) and per-process entries, comparing successive samples to compute utilization percentages. `kill(2)` is a system call: the kernel validates that the caller has permission (same UID, or root), then delivers the signal to the target process's signal queue. The process handles the signal at the next safe point in its execution.

**Level 4 — Why it was designed this way (senior/staff):**
The PID namespace was added in Linux 3.8 to support containers: inside a container, PID 1 can be `nginx`, isolated from the host PID namespace. This is why `ps` inside a container shows only container processes, not the full host process table. The `/proc` virtual filesystem was a revolutionary design: rather than dedicated system calls for every query, process information is exposed as a file tree — making it shell-scriptable and eliminatng the need for hundreds of new syscalls. `cgroups` extend the process management model with resource limits and accounting, giving the equivalent of "maximum CPU" and "maximum memory" per process group — the foundation of container resource management.

---

### ⚙️ How It Works (Mechanism)

**`ps` output format:**

```bash
ps aux
# USER    PID  %CPU %MEM    VSZ    RSS TTY  STAT START    TIME COMMAND
# root      1   0.0  0.1 168316  9084 ?    Ss   Jan01   0:42 /sbin/init
# www-data  457  0.1  0.5 142820 42140 ?   S    Jan01   2:15 nginx: worker

# Fields:
# PID   = Process ID
# %CPU  = CPU usage (sampled)
# %MEM  = Physical memory % (RSS/total)
# VSZ   = Virtual memory (includes mapped but unpaged)
# RSS   = Resident Set Size (actual physical RAM used)
# STAT  = Process state (R/S/D/Z/T)
# TIME  = Cumulative CPU time
```

**`top` key bindings:**

```
q      quit
k      kill (prompts for PID and signal)
r      renice (change priority)
M      sort by memory (%MEM)
P      sort by CPU (%CPU)
1      show per-CPU stats
u      filter by user
H      show threads
i      hide idle processes
```

**Signal table (most important):**

| Signal    | Number | Default Action | Can Catch? | Use Case                                  |
| --------- | ------ | -------------- | ---------- | ----------------------------------------- |
| SIGTERM   | 15     | Terminate      | Yes        | Graceful shutdown (default `kill`)        |
| SIGKILL   | 9      | Kill           | No         | Force-stop (last resort)                  |
| SIGHUP    | 1      | Terminate      | Yes        | Reload config (many daemons)              |
| SIGINT    | 2      | Terminate      | Yes        | Ctrl+C (keyboard interrupt)               |
| SIGSTOP   | 19     | Stop           | No         | Pause process (like SIGKILL: uncatchable) |
| SIGCONT   | 18     | Continue       | Yes        | Resume stopped process                    |
| SIGCHLD   | 17     | Ignore         | Yes        | Child process changed state               |
| SIGUSR1/2 | 10/12  | Terminate      | Yes        | Application-defined actions               |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Production alert: high memory usage on web server
    ↓
Engineer SSH's in
    ↓
Runs: top -b -n1 | head -20
    ↓
Identifies: java process PID=45231 at 89% memory
    ← YOU ARE HERE (process visibility)
    ↓
Runs: kill 45231   (sends SIGTERM)
    ↓
JVM receives SIGTERM, runs shutdown hooks
    ↓
JVM closes DB connections, flushes logs, exits cleanly
    ↓
systemd detects exit → restarts service (if configured)
    ↓
Alert clears after 2 minutes
```

**FAILURE PATH:**

```
JVM is stuck in GC loop, unresponsive to SIGTERM
    ↓
After 30 seconds: kill -9 45231
    ↓
Kernel force-kills JVM immediately
    ↓
DB connections left open (pool exhausted — check DB)
    ↓
Incomplete writes to log file
    ↓
Observable: DB pool exhaustion alerts; corrupt log entries
```

**WHAT CHANGES AT SCALE:**
On a Kubernetes cluster, you don't `kill` individual processes — you scale deployments, roll restarts, or evict pods. The scheduler manages process lifecycle across hundreds of nodes. `kubectl exec` provides the equivalent of SSH for process inspection. `kubectl top pods` replaces `top`. At the kernel level, the mechanisms are identical — `kill`, signals, `/proc` — but the management layer abstracts them.

---

### 💻 Code Example

**Example 1 — Common process inspection:**

```bash
# Show all processes (unix style — most useful)
ps aux

# Show process tree
ps auxf      # with ASCII tree
pstree -p    # pretty tree with PIDs

# Find a specific process
pgrep -la java          # PIDs + command lines matching "java"
ps aux | grep nginx

# Process details
cat /proc/12345/status    # kernel's process data
cat /proc/12345/cmdline   # full command line
ls -la /proc/12345/fd     # open file descriptors
```

**Example 2 — Top 10 CPU/memory consumers:**

```bash
# Top 10 by CPU
ps aux --sort=-%cpu | head -11

# Top 10 by memory (RSS)
ps aux --sort=-%mem | head -11

# Watch continuously (update every 2 seconds)
watch -n2 'ps aux --sort=-%mem | head -11'

# Single snapshot of top (non-interactive, for scripts)
top -bn1 | head -20
```

**Example 3 — Sending signals correctly:**

```bash
# STEP 1: always try graceful first
kill 12345              # SIGTERM (default signal 15)

# STEP 2: wait and check
sleep 5
if kill -0 12345 2>/dev/null; then
    # -0 = check if process exists (no signal sent)
    echo "Process still alive, using SIGKILL"
    kill -9 12345
else
    echo "Process exited cleanly"
fi

# Kill all processes matching a name
pkill -TERM java        # send SIGTERM to all "java" processes
pkill -9 zombie_app     # force-kill

# Kill a process group (all children too)
kill -- -12345          # negative PID = process group
```

**Example 4 — Process management in scripts:**

```bash
#!/bin/bash
# Start a background process and track it
./long_running_task &
TASK_PID=$!
echo "Started task: PID=$TASK_PID"

# Wait with timeout
timeout 60 bash -c "while kill -0 $TASK_PID 2>/dev/null; \
  do sleep 1; done" || {
    echo "Task timed out, killing..."
    kill -9 $TASK_PID
}
```

---

### ⚖️ Comparison Table

| Tool            | Purpose             | Real-time? | Interactive? | Best For                  |
| --------------- | ------------------- | ---------- | ------------ | ------------------------- |
| **ps**          | Process snapshot    | No         | No           | Scripts, quick checks     |
| **top**         | Resource monitor    | Yes        | Yes          | Interactive investigation |
| **htop**        | Enhanced top        | Yes        | Yes          | Rich interactive UI       |
| **pgrep/pkill** | Find/signal by name | No         | No           | Scripting, automation     |
| **kill**        | Send signal by PID  | No         | No           | Precise process control   |
| **systemctl**   | Service lifecycle   | No         | No           | Managed service control   |

**How to choose:** Use `ps aux | grep name` for quick checks in scripts. Use `top` or `htop` for interactive investigation. Use `systemctl` for managed services — it handles restarts, dependencies, and logging.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                               |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `kill -9` is always the right way to stop a process | SIGKILL leaves no cleanup chance; use SIGTERM first and allow the process to handle it gracefully                                     |
| `ps aux` shows current CPU usage                    | `%CPU` is a time-averaged sample; it can exceed 100% for multi-threaded processes (per-core usage); top's `%CPU` is also sampled      |
| Zombie processes consume resources                  | Zombie processes have exited; they consume only a slot in the process table (a few hundred bytes), not CPU or memory                  |
| `kill` always kills a process                       | `kill` sends a signal; the default signal is SIGTERM; the process can handle (or ignore) SIGTERM. Only SIGKILL guarantees termination |
| The process with the highest PID started last       | PIDs are assigned from a circular counter and wrap around; high PID doesn't mean recently started                                     |
| `kill -9` kills child processes too                 | SIGKILL only kills the targeted PID; children may become orphans (re-parented to PID 1), not killed                                   |

---

### 🚨 Failure Modes & Diagnosis

**Runaway Process Consuming All CPU**

**Symptom:**
System load average spikes; other processes become unresponsive; `top` shows one process at 99%+ CPU.

**Root Cause:**
Infinite loop, CPU-bound computation without throttling, or a thread stuck in a tight retry loop.

**Diagnostic Command:**

```bash
top -bn1 | head -20        # identify by CPU%
# Get thread-level CPU breakdown:
top -H -p <PID>             # -H shows threads
# See what it's actually doing:
strace -p <PID> -c          # system call summary
```

**Fix:**

```bash
kill <PID>                  # SIGTERM first
# Or reduce priority without killing:
renice +19 -p <PID>         # lowest priority (nice=19)
```

**Prevention:**
Set CPU limits in cgroups or systemd unit (`CPUQuota=50%`); implement timeouts in application code.

---

**Process Won't Die (Stuck in D State)**

**Symptom:**
Process is in `D` state (uninterruptible sleep); `kill -9` has no effect; process remains indefinitely.

**Root Cause:**
Process is waiting for a kernel I/O operation that cannot be interrupted — typically stuck waiting for NFS, broken disk, or kernel bug. `SIGKILL` cannot interrupt kernel-mode waits.

**Diagnostic Command:**

```bash
ps aux | grep " D "          # find D-state processes
# Find what they're waiting for:
cat /proc/<PID>/wchan        # kernel wait channel
# NFS-related:
dmesg | grep -i "nfs\|hung_task"
```

**Fix:**
Unmount the stuck NFS share; fix the underlying I/O issue. A `D`-state process cannot be killed without resolving the underlying kernel wait or rebooting.

**Prevention:**
Mount NFS with `soft,timeo=30` (timeout instead of hang indefinitely); use `intr` mount option.

---

**Zombie Process Accumulation**

**Symptom:**
`ps aux` shows many processes in `Z` (zombie) state; PID table approaching limit; `ps` reports "cannot allocate".

**Root Cause:**
Parent process is not calling `wait()` or `waitpid()` on child exit. Zombie slots accumulate until the parent dies or is fixed.

**Diagnostic Command:**

```bash
ps aux | grep " Z "          # find zombies
# Find the parent:
ps -o ppid= -p <ZOMBIE_PID>
```

**Fix:**
Send SIGCHLD to the parent: `kill -CHLD <PARENT_PID>` to trigger wait(). If parent cannot be fixed, kill the parent (zombies then re-parent to PID 1, which calls wait() and cleans them up).

**Prevention:**
In application code, always call `waitpid()` for child processes; use `SIGCHLD` handlers; or use `prctl(PR_SET_CHILD_SUBREAPER)` to intercept orphan children.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Operating System` — the kernel's process scheduler and task_struct are the foundation
- `Linux File System Hierarchy` — `/proc` virtual filesystem exposes process data as files

**Builds On This (learn these next):**

- `Systemd / Init System` — PID 1 manages the process lifecycle for all services
- `Signals (SIGTERM, SIGKILL, SIGHUP)` — the full signal model for process communication
- `Zombie Processes` — the failure mode when parents don't reap children
- `strace / ltrace` — deep-dive process inspection tools

**Alternatives / Comparisons:**

- `htop` — enhanced interactive process viewer (not built-in; install separately)
- `cgroups` — resource limits per process group (what containers use under the hood)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Tools to view and control running         │
│              │ processes on a Linux system               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without visibility into running processes, │
│ SOLVES       │ production debugging is impossible        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ kill -9 is not "kill" — it's "abort       │
│              │ immediately with no cleanup"; try         │
│              │ SIGTERM first                             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Debugging incidents, stopping services,   │
│              │ investigating resource usage              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't kill -9 managed services (use       │
│              │ systemctl stop instead)                   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ SIGTERM (safe cleanup) vs. SIGKILL        │
│              │ (guaranteed termination)                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ps tells you who's there; top tells      │
│              │  you who's misbehaving; kill tells        │
│              │  them to stop"                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Systemd / Init System → Signals →        │
│              │ Zombie Processes                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Docker container runs with a shell script as its `CMD` (not `EXEC` form). The shell forks a Java process to run the application. When Kubernetes sends `SIGTERM` to the container for graceful shutdown, which process receives it — the shell (PID 1) or the Java application? Trace the signal delivery path, explain why the Java application may not receive `SIGTERM` at all in this scenario, and describe what change to the Dockerfile fixes the problem.

**Q2.** A production server shows 300 zombie processes in `Z` state. The parent of all 300 is PID 8423, a Python web server. Memory usage is normal; the system is otherwise functional. A colleague suggests `kill -9 8423` to clean up the zombies. Predict exactly what happens to: (a) the zombie processes, (b) the in-flight HTTP requests being handled by PID 8423's threads, and (c) the listening socket on port 8080. Is this the right fix? What is the less disruptive alternative?
