---
id: LNX-014
title: "Process Basics (ps, top, htop, kill)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-037, LNX-047, LNX-060
related: LNX-037, LNX-047, LNX-082
tags: [process, ps, top, htop, kill, pid, signals, monitoring]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/lnx/process-basics/
---

## TL;DR

Every running program is a process with a numeric PID. `ps aux`
lists all processes. `top`/`htop` shows real-time CPU and memory
usage. `kill PID` sends a signal to a process (default: SIGTERM =
graceful shutdown). `kill -9 PID` sends SIGKILL (immediate forced
termination). In production: SIGTERM first, wait for graceful
shutdown, then SIGKILL if needed.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-014 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | ps, top, htop, kill, PID, process management, signals |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

When a system slows down, you need to know what's consuming CPU and
memory. When an application hangs, you need to stop it. When a
deployment fails, you need to verify the old process stopped and the
new one started. Process management commands are the fundamental tools
for understanding and controlling what's running on a Linux system.

---

### Textbook Definition

A **process** is an instance of a running program. The Linux kernel
tracks processes using a **PID** (Process ID) - a unique integer.
Every process except pid 1 (init/systemd) has a **parent process
(PPID)**.

Key attributes:
- **PID**: process ID (kernel-assigned)
- **PPID**: parent process ID
- **UID**: user running the process
- **State**: running, sleeping, zombie, stopped
- **CPU%**: processor utilization
- **MEM%**: memory utilization

Signals are software interrupts sent to processes to control them.
SIGTERM (15) = request graceful shutdown. SIGKILL (9) = force kill
(cannot be caught or ignored by the process).

---

### Understand It in 30 Seconds

```bash
# List all processes:
ps aux              # snapshot of all running processes
ps aux | grep java  # find java processes

# Real-time monitoring:
top                 # press q to quit, k to kill, shift+p for CPU sort
htop                # more user-friendly (may need: apt install htop)

# Find process by name:
pgrep nginx         # prints PID(s) of nginx processes
pgrep -l nginx      # prints PID and name

# Send signals:
kill PID            # SIGTERM (15): ask to stop gracefully
kill -15 PID        # same as kill PID
kill -9 PID         # SIGKILL: force stop immediately
killall nginx       # kill all processes named "nginx"
pkill nginx         # same as killall

# Process tree:
pstree              # show parent-child relationships
pstree -p nginx     # show nginx tree with PIDs
```

---

### First Principles

**Everything is a process:**
When you run a command, the shell creates a child process via fork().
The child calls exec() to become the new program. The shell waits
(or runs it in background with &). Every running program - nginx,
java, postgres, even ls and grep - is a process with a PID.

**Process states:**
```
R  Running or runnable (on the CPU or waiting for CPU)
S  Sleeping (interruptible) - waiting for event (I/O, signal)
D  Sleeping (uninterruptible) - waiting for I/O, cannot be killed
Z  Zombie - process finished, parent hasn't collected exit status
T  Stopped (suspended via SIGSTOP or Ctrl+Z)
```

**Signal delivery:**
The kernel delivers signals to processes. SIGTERM: delivered to
the process, which can catch it and do cleanup (close connections,
flush buffers, delete temp files). SIGKILL: kernel-delivered,
process CANNOT catch or ignore it - instant termination with no
cleanup possible. Always try SIGTERM first.

---

### Thought Experiment

Your Java application server stopped responding. Memory usage at 95%.
Users getting 503 errors. Sequence of actions:

1. `top` - identify which process is consuming the memory
2. `ps aux | grep java` - find the java process PID and how long it's been running
3. `kill 1234` - send SIGTERM to PID 1234 (request graceful shutdown)
4. Wait 30 seconds
5. `ps aux | grep java` - check if it stopped
6. If not stopped: `kill -9 1234` - force kill
7. `systemctl start myapp` - restart the service

This sequence respects the graceful shutdown window. Jumping straight
to kill -9 risks: lost transactions, corrupted state files, unclosed
connections (fill up connection pool on database).

---

### Mental Model / Analogy

Processes are like **kitchen staff** in a restaurant:

```
Each chef (process) has an ID badge (PID)
Head chef (PID 1 = systemd) manages everything else

Signals = messages to the kitchen:
  SIGTERM: "Kitchen closing - please wrap up your current dish"
    Chef finishes the current task, cleans up, goes home
    (graceful shutdown: in-flight requests complete)
    
  SIGKILL: Fire alarm + sprinklers activated
    Everyone drops everything and leaves immediately
    Current dishes are ruined, kitchen may be messy
    (force kill: in-flight requests lost)

  SIGHUP: "New menu arrived - reload your recipes"
    Chef reads new config without stopping
    (graceful config reload: nginx -s reload)
    
ps aux = the kitchen roster board (who's working, on what, since when)
top = live scoreboard of who's busiest right now
```

---

### Gradual Depth - Five Levels

**Level 1:**
ps aux shows all processes. top shows real-time stats. kill PID stops
a process. kill -9 force-stops. Use pgrep to find process by name.
Always try graceful (kill) before force (kill -9).

**Level 2:**
ps output columns: USER (who's running it), PID, %CPU, %MEM, VSZ
(virtual memory KB), RSS (resident set size - actual RAM used KB),
STAT (state), START (start time), TIME (CPU time consumed), COMMAND.
Zombie processes (Z state): use wait() to reap them. If parent
never calls wait(), zombie accumulates until parent dies.

**Level 3:**
Process priority: nice (-20 to 19, lower = higher priority). `nice -n 10 myprocess` starts with nice=10 (lower priority). `renice -n 5 -p PID` changes running process priority. For long batch jobs: `nice -n 19 backup.sh` (lowest priority, won't starve interactive users).
`ionice -c 3 -p PID` = idle I/O priority (only uses disk when nothing else needs it).

**Level 4:**
/proc filesystem: every process has /proc/PID/. `cat /proc/PID/status` = detailed status. `/proc/PID/cmdline` = full command line. `/proc/PID/fd/` = open file descriptors. `/proc/PID/maps` = memory map. `lsof -p PID` = list all open files, sockets, pipes. `strace -p PID` = trace system calls in real time (powerful but high overhead).

**Level 5:**
Process scheduling at scale: Linux CFS (Completely Fair Scheduler) gives each process vruntime. CPU cgroups: set CPU limits per container/group. Real-time processes (SCHED_FIFO, SCHED_RR) bypass CFS for latency-critical work. Production monitoring: instead of `top`, use metrics pipeline (node_exporter -> Prometheus -> Grafana) for historical data, alerting, and fleet-wide view. `top` is a point-in-time tool; production needs time-series metrics.

---

### Code Example

**BAD - process management anti-patterns:**
```bash
# BAD 1: kill -9 as first resort - skips graceful shutdown
kill -9 $(pgrep java)   # loses in-flight transactions!

# BAD 2: killall without verifying the process
killall nginx           # kills ALL processes named nginx
                        # including ones you didn't intend to stop

# BAD 3: running without checking if already running
./start-myapp.sh        # starts second instance!
                        # both try to bind port 8080 -> one fails

# BAD 4: ignoring zombie processes
# Zombie accumulation = eventually you can't fork new processes
# (PID table fills up)
```

**GOOD - correct process management:**
```bash
# GOOD 1: graceful shutdown with fallback
PID=$(pgrep -f 'java -jar myapp')
if [ -n "$PID" ]; then
    echo "Sending SIGTERM to $PID..."
    kill "$PID"
    
    # Wait up to 30 seconds for graceful shutdown:
    for i in $(seq 1 30); do
        sleep 1
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "Process stopped gracefully"
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "Timeout - sending SIGKILL..."
            kill -9 "$PID"
        fi
    done
fi

# GOOD 2: check if running before starting
if pgrep -f "myapp.jar" > /dev/null; then
    echo "Already running, skipping start"
    exit 0
fi

# GOOD 3: use systemd for proper process management
systemctl stop myapp   # sends SIGTERM, waits, then SIGKILL
systemctl start myapp
systemctl status myapp

# GOOD 4: find resource hog and investigate before killing
# CPU hog:
ps aux --sort=-%cpu | head -10

# Memory hog:
ps aux --sort=-%mem | head -10

# Identify what the process is doing before killing:
lsof -p 1234 | head -20   # what files/sockets is it using?
strace -p 1234 -c          # summarize syscalls (brief observation)
```

---

### Reading ps aux Output

```
$ ps aux | head -5
USER    PID  %CPU %MEM    VSZ   RSS TTY  STAT START  TIME COMMAND
root      1   0.0  0.1 169008 13456 ?   Ss   Jan15  0:12 /sbin/init
nginx   891   0.0  0.1  55500  5612 ?   S    Jan15  0:00 nginx: worker
alice  1234   2.5  8.3 3900000 680000 ? Sl  10:30  2:43 java -jar app.jar
root   1456   0.0  0.0  14224  1024 ?   S    10:45  0:00 [kworker/u4:1]

Column meanings:
  USER  = who runs the process
  PID   = process ID
  %CPU  = CPU usage (can exceed 100% on multi-core)
  %MEM  = percentage of physical RAM in use
  VSZ   = virtual memory size (KB) - includes unmapped memory
  RSS   = resident set size (KB) - actual RAM in use
  STAT  = process state (S=sleeping, R=running, Z=zombie, D=uninterruptible)
  START = when the process started
  TIME  = total CPU time consumed (not wall clock)
  COMMAND = the command line that started it

Notable: java -jar app.jar shows 680MB RSS (real RAM)
  If you see RSS >> available RAM: memory pressure / swapping
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "kill = kill the process immediately" | `kill PID` sends SIGTERM by default - it ASKS the process to stop. The process can ignore or delay the response. Only `kill -9` forces immediate termination. |
| "kill -9 is always safe to use immediately" | SIGKILL leaves no chance for cleanup: open database transactions may be left uncommitted, log buffers unflushed, temp files not cleaned, connections not properly closed (fills connection pool). SIGTERM first, wait, then -9. |
| "%CPU can't exceed 100%" | On a multi-core system, a single process can use 400% (4 cores fully utilized). `top` shows per-process, not system-wide. System-wide CPU% = sum of all processes / number of cores. |
| "VSZ shows actual memory usage" | VSZ (virtual size) includes memory that's mapped but not loaded, shared libraries counted multiple times, memory-mapped files. RSS (resident set size) = actual physical memory pages in use. Use RSS for memory pressure analysis, not VSZ. |
| "A zombie process is still running" | Zombie processes have FINISHED executing. The kernel keeps the entry in the process table until the parent process calls wait() to collect the exit status. Zombies consume a PID slot but no CPU or memory. |

---

### Failure Modes & Diagnosis

**Runaway process consuming 100% CPU:**
```bash
# Step 1: identify the culprit
top   # press 1 to see per-core, shift+P to sort by CPU
# OR:
ps aux --sort=-%cpu | head -5

# Step 2: identify what it's doing
PID=1234   # the PID from step 1
ls -la /proc/$PID/exe   # what binary is it?
cat /proc/$PID/cmdline | tr '\0' ' '  # full command line
strace -p $PID -e trace=all -c -f &   # sample for 10 seconds
sleep 10
kill $STRACE_PID
# shows top system calls - might identify I/O loop, infinite loop

# Step 3: for Java specifically:
kill -3 $PID   # send SIGQUIT: dumps thread stack trace to stdout/logs
               # (Java catches SIGQUIT and prints thread dump, doesn't die)

# Step 4: decide: can it recover? wait? or kill?
# graceful:
kill $PID          # SIGTERM
# Check after 30 seconds, then:
kill -9 $PID       # SIGKILL if needed
```

**Cannot kill process (D state - uninterruptible sleep):**
```bash
# D state processes are waiting for I/O from kernel
# CANNOT be killed by any signal (including -9)
# This is a kernel feature, not a bug

# Diagnosis:
ps aux | grep ' D '   # find D-state processes
ls -la /proc/$PID/fd  # what I/O is it waiting on?

# Common causes: NFS hang, storage I/O wait, driver issue
# Solution: fix the underlying I/O issue (not kill the process)
# If NFS: unmount the hung NFS mount
# If storage: check dmesg for I/O errors
```

**Security: process running as wrong user:**
```bash
# Security audit: find processes running as root that shouldn't be
ps aux | awk '$1 == "root" { print $1, $11, $12 }' | \
  grep -v -E "^\[|^root.*systemd|^root.*kernel"
# Review each one: does this need root?

# Find processes listening on ports (potential attack surface):
ss -tlnp   # TCP listening + process name
# OR:
netstat -tlnp 2>/dev/null | grep LISTEN
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-015 (Standard Streams)

**Builds on this:**
LNX-037 (Process Management - nohup, &, jobs),
LNX-047 (Process Signals), LNX-060 (Process Scheduling),
LNX-082 (System Call Interface)

**Related:**
OSY-002 (Process), OSY-025 (Process State)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ps aux` | Snapshot of all processes |
| `ps aux --sort=-%cpu` | Sort by CPU usage |
| `ps aux --sort=-%mem` | Sort by memory usage |
| `pgrep nginx` | Find PID by name |
| `pgrep -la nginx` | Find PID + full command |
| `top` | Real-time process viewer |
| `htop` | Enhanced real-time viewer |
| `kill PID` | Send SIGTERM (graceful stop) |
| `kill -9 PID` | Send SIGKILL (force stop) |
| `kill -HUP PID` | Send SIGHUP (reload config) |
| `killall name` | Kill all processes by name |
| `pkill name` | Same as killall |

**3 things to remember:**
1. `kill PID` = SIGTERM (graceful); `kill -9 PID` = SIGKILL (force) - always try graceful first
2. D-state processes (uninterruptible sleep) CANNOT be killed - fix the underlying I/O
3. RSS = actual RAM in use (VSZ is misleading for memory analysis)

---

### Transferable Wisdom

The SIGTERM/SIGKILL pattern appears everywhere: Kubernetes pod
termination (sends SIGTERM, waits terminationGracePeriodSeconds=30,
then SIGKILL), Docker stop (same pattern), systemd stop (same).
Understanding the signal model explains why graceful shutdowns
need time and why forcing them too quickly causes data loss or
connection leaks.

The **observe before act** principle (ps/top before kill) applies
to all production operations: understand the system state before
making changes. This is the foundation of the SRE approach to
incident response.

---

### The Surprising Truth

PID 1 in Linux is special: if PID 1 exits, the kernel kills all
other processes and panics. In Docker containers, your application
often runs as PID 1. This causes problems: PID 1 must handle
zombie reaping (calling wait() for orphaned processes), and many
applications don't do this. When running Java in Docker, if the
container spawns child processes (e.g., bash scripts), those
children can become zombies. Solution: use `tini` (a minimal
init process) as PID 1 in containers. Docker's `--init` flag or
`ENTRYPOINT ["/usr/bin/tini", "--"]` in Dockerfile adds tini as
PID 1, which properly reaps zombies and forwards signals.

---

### Mastery Checklist

- [ ] Can find a running process by name and by resource usage
- [ ] Can explain the difference between SIGTERM and SIGKILL and when to use each
- [ ] Can read ps aux output and identify resource-hungry processes
- [ ] Can implement a graceful shutdown sequence with timeout
- [ ] Can explain why D-state processes cannot be killed

---

### Think About This

1. You send SIGTERM to a Java application server with 100 in-flight
   HTTP requests. The application catches SIGTERM. What is the
   "correct" thing for the application to do with those 100 requests?
   Stop accepting new requests immediately? Let the 100 finish?
   What if they're taking 10 seconds each?

2. A process is in D (uninterruptible sleep) state. You run `kill -9`
   on it. What happens? What does this tell you about how kill -9 works
   at the kernel level, and what's the only way to "fix" a D-state process?

3. In a Kubernetes pod, your Java application is PID 1. When Kubernetes
   sends a graceful shutdown, it sends SIGTERM to PID 1. Your Java
   application has registered a shutdown hook that takes 60 seconds to
   complete. Kubernetes's default terminationGracePeriodSeconds is 30.
   What happens after 30 seconds?

**TYPE G:** Design a zero-downtime deployment process for a stateful
Java application (maintaining database connections, in-flight HTTP
requests, and distributed cache entries). The process involves stopping
the old version and starting the new version. What signals do you send,
in what order, with what timeouts? How do you verify the old process
cleanly stopped before starting the new one?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `kill PID` and `kill -9 PID`?
A: `kill PID` sends SIGTERM (signal 15), which asks the process to terminate gracefully. The process receives the signal and can: catch it, perform cleanup (flush buffers, close connections, complete in-flight operations), then exit. Some processes ignore SIGTERM. `kill -9 PID` sends SIGKILL (signal 9), which is handled by the KERNEL, not the process. The process cannot catch, ignore, or defer SIGKILL. The kernel immediately terminates the process, reclaims memory, closes file descriptors. No cleanup is possible. Use kill -9 only when SIGTERM doesn't work after a reasonable timeout (30-60 seconds), because forced termination can leave the system in an inconsistent state.

**Intermediate:**
Q: Your Java application has a memory leak and is consuming 8GB RAM on a 16GB server. How do you investigate and handle it?
A: (1) Confirm with `ps aux --sort=-%mem | head -5` - check RSS column. (2) Check growth rate: run `ps -o pid,rss -p $PID` every 30 seconds - if RSS grows without bound, it's a leak. (3) For Java specifically: get a heap dump without killing the process: `jmap -dump:format=b,file=/tmp/heap.dump $PID` (requires JDK tools). (4) Get thread dump: `kill -3 $PID` (SIGQUIT triggers Java thread dump to logs, doesn't kill the process). (5) Analyze with Eclipse MAT or VisualVM. (6) If memory pressure is critical: graceful restart via systemd (`systemctl restart myapp`), which sends SIGTERM and waits for graceful shutdown before starting new instance. (7) Root cause analysis before the next incident.

**Expert:**
Q: Explain the Linux process lifecycle from fork() to exit(), including zombie processes and proper cleanup.
A: (1) Parent calls fork(): kernel creates a copy of parent's address space, file descriptors, and environment. Both parent and child are now running (parent gets child PID, child gets 0). (2) Child calls exec(): replaces the process image with a new program, retaining the PID and inheriting open file descriptors. (3) Process runs until it calls exit() (or is killed). (4) At exit: kernel marks process as ZOMBIE (Z state) - process entry remains in process table but process is dead. Kernel notifies parent via SIGCHLD. (5) Parent calls wait() or waitpid(): kernel gives parent the exit status, removes zombie from process table. PID is now available for reuse. Problem scenario: parent never calls wait() - zombies accumulate. Eventually the PID table fills and no new processes can be created. Solution: parent must handle SIGCHLD and call wait(). In containers: tini as PID 1 handles this. In Java: JVM shutdown hooks. In Go: goroutines should call cmd.Wait() after cmd.Start(). Common production issue: web servers that fork child processes for request handling but don't properly reap them after they finish.
