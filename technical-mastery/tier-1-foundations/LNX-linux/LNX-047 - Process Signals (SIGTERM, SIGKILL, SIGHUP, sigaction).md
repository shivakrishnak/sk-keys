---
id: LNX-047
title: "Process Signals (SIGTERM, SIGKILL, SIGHUP, sigaction)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-016
used_by: LNX-031, LNX-082
related: LNX-031, LNX-082, OSY-025
tags: [signals, SIGTERM, SIGKILL, SIGHUP, kill, trap, sigaction, signal-handling, SIGINT]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/lnx/process-signals/
---

## TL;DR

Linux signals are asynchronous notifications sent to processes.
`SIGTERM` (15): graceful shutdown request - process can catch and clean up.
`SIGKILL` (9): immediate termination - CANNOT be caught, blocked, or ignored
(the kernel terminates the process directly). `SIGHUP` (1): terminal hangup -
convention for daemons to reload config. `SIGINT` (2): Ctrl+C interrupt.
`kill -SIGTERM PID` (or `kill PID`) sends graceful signal. `kill -9 PID`
or `kill -SIGKILL PID` forces termination. `trap` in bash handles signals
in scripts. `pkill nginx` sends SIGTERM by name. Always try SIGTERM first,
wait, then SIGKILL.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-047 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | signals, SIGTERM, SIGKILL, SIGHUP, kill, trap, sigaction, SIGINT |
| **Prerequisites** | LNX-015, LNX-016 |

---

### The Problem This Solves

**Problem 1**: A Java web server needs to stop gracefully - finishing
in-flight requests, flushing logs, releasing locks. `kill -9` terminates
it instantly, corrupting state. `kill -SIGTERM` gives it time to shut down
cleanly. Understanding signals lets you choose correctly.

**Problem 2**: nginx's config has changed. Restarting nginx would drop
active connections. `nginx -s reload` (which sends SIGHUP) causes nginx to
reload config without dropping existing connections.

**Problem 3**: A bash script creates temp files. If Ctrl+C is pressed,
the temp files are left behind. Using `trap` in bash handles SIGINT and
cleans up automatically.

---

### Textbook Definition

**Signal**: An asynchronous notification sent to a process by the kernel,
another process (with permission), or the process itself. Interrupts normal
execution. The process can: (1) catch the signal and run a handler function,
(2) ignore the signal (if catchable), (3) perform the default action (usually
terminate).

**Catchable signals**: Can be intercepted and handled by the process.
Examples: SIGTERM, SIGHUP, SIGINT, SIGUSR1, SIGUSR2, SIGPIPE, SIGCHLD.

**Uncatchable signals**: SIGKILL (9) and SIGSTOP (19) cannot be caught,
blocked, or ignored. The kernel enforces these directly - no process can
override them.

**Signal delivery**: Signals are delivered when the process is scheduled.
A process that's sleeping (blocked on I/O) will be woken up to handle a
signal. Signals from the same type are coalesced (you can send 100 SIGTERM
signals but the process handles it only once if it's already handling one).

---

### Understand It in 30 Seconds

```bash
# === Sending signals ===
kill PID                   # sends SIGTERM (15) - default
kill -SIGTERM PID          # same as above (explicit)
kill -15 PID               # same (numeric)
kill -SIGKILL PID          # force kill - cannot be caught
kill -9 PID                # same (numeric)
kill -SIGHUP PID           # reload signal (convention)
kill -1 PID                # same as SIGHUP

# Send to all processes matching name:
pkill nginx                # SIGTERM to all nginx processes
pkill -9 nginx             # SIGKILL to all nginx processes
pkill -SIGHUP nginx        # reload all nginx processes

# Kill by port:
fuser -k 8080/tcp          # kill process using port 8080

# === Checking what signals a process handles ===
kill -l                    # list all signals
cat /proc/PID/status | grep -E "Sig(Blk|Cgt|Ign)"
# SigBlk: blocked signals bitmap
# SigCgt: caught (handled) signals bitmap
# SigIgn: ignored signals bitmap

# Decode the hex bitmask (signal 15 = bit 15):
# SigCgt: 0000000000004a00 -> signals 11, 13, 15 are caught

# === Signal to specific process group ===
kill -SIGTERM -PID         # send to process group (negative PID)
kill -SIGTERM 0            # send to all processes in current session

# === Graceful shutdown pattern ===
kill -SIGTERM $PID         # request graceful shutdown
sleep 10                   # wait for graceful shutdown
kill -0 $PID 2>/dev/null && kill -SIGKILL $PID  # force kill if still running
# kill -0 checks if process exists without sending a signal

# === Signals from keyboard ===
# Ctrl+C = SIGINT (interrupt)
# Ctrl+Z = SIGTSTP (stop/pause)
# Ctrl+\ = SIGQUIT (quit with core dump)
```

---

### First Principles

**Signal number reference:**
```
Signal   Num  Default Action    Description
SIGHUP     1  Terminate         Terminal hangup; daemons: reload config
SIGINT     2  Terminate         Ctrl+C keyboard interrupt
SIGQUIT    3  Core dump         Ctrl+\ - quit with core dump
SIGILL     4  Core dump         Illegal instruction
SIGTRAP    5  Core dump         Debugger breakpoint
SIGABRT    6  Core dump         abort() function called
SIGFPE     8  Core dump         Arithmetic error (division by zero)
SIGKILL    9  Terminate*        UNCATCHABLE force kill
SIGSEGV   11  Core dump         Invalid memory access (segfault)
SIGPIPE   13  Terminate         Write to pipe with no reader
SIGALRM   14  Terminate         alarm() timer expired
SIGTERM   15  Terminate*        Graceful termination request
SIGCHLD   17  Ignore            Child process exited
SIGCONT   18  Continue          Resume stopped process
SIGSTOP   19  Stop*             UNCATCHABLE process pause
SIGTSTP   20  Stop              Ctrl+Z keyboard stop
SIGUSR1   10  Terminate*        User-defined signal 1
SIGUSR2   12  Terminate*        User-defined signal 2

*: default action (can be overridden except SIGKILL and SIGSTOP)

Notes on common daemons:
  nginx:  SIGHUP = reload config, SIGUSR1 = reopen log files
  sshd:   SIGHUP = reload config
  Apache: SIGUSR1 = graceful reload, SIGTERM = shutdown
  Java:   SIGUSR2 = prints thread stack (useful for deadlock diagnosis)
  MySQL:  SIGTERM = flush tables and shutdown
```

**Signal lifecycle:**
```
Process A calls: kill(PID_B, SIGTERM)
                     |
          Kernel checks permissions
          (A must own B, or be root)
                     |
          Kernel sets signal pending flag in B's task_struct
                     |
    Process B is scheduled (or woken from sleep)
                     |
          Kernel checks: is signal pending?
                     |
          Signal delivery:
            If B has registered handler -> run handler
            If B ignores signal -> no action
            If no handler -> default action (usually: terminate)
```

---

### Thought Experiment

A Docker container SIGKILL problem in production:

```bash
# Docker default stop command:
docker stop mycontainer    # sends SIGTERM, waits 10s, then SIGKILL

# If your Java app doesn't handle SIGTERM:
#   - SIGTERM arrives: default action = terminate immediately
#   - No graceful shutdown: in-flight requests dropped, DB connections killed
#   - Same effect as SIGKILL

# Fix 1: In Docker, set ENTRYPOINT to handle signals properly
# Use exec form (not shell form) so PID 1 is your app, not a shell:
# Shell form (BAD): CMD java -jar app.jar
#   -> Shell is PID 1, Java is child. Shell may not forward signals to child!
# Exec form (GOOD): CMD ["java", "-jar", "app.jar"]
#   -> Java is PID 1. Receives SIGTERM directly.

# Fix 2: Use tini as init process (handles signal forwarding):
# In Dockerfile: RUN apt-get install tini && ENTRYPOINT ["/usr/bin/tini", "--"]
# OR: docker run --init myimage

# Fix 3: Handle SIGTERM in your Java app:
# Runtime.getRuntime().addShutdownHook(new Thread(() -> {
#     server.stop(30, TimeUnit.SECONDS);  // 30s graceful shutdown
# }));

# Verify the container handles SIGTERM:
docker stop --time=30 mycontainer  # extend timeout to 30s
# Check logs: did it flush? Did requests complete?
# Check exit code: docker inspect mycontainer | grep ExitCode
# 137 = SIGKILL (container killed by timeout)
# 143 = SIGTERM (graceful exit from SIGTERM)
```

---

### Mental Model / Analogy

```
Signals are like fire alarm levels in an office:

SIGTERM = "Please evacuate in an orderly manner"
  - People save their work, close applications, walk to exits
  - Can take a few minutes
  - Orderly shutdown

SIGKILL = "FIRE! Emergency evacuation NOW!"
  - Everyone drops everything and runs
  - Work is lost, applications crash-exit
  - Cannot be argued with or delayed

SIGHUP = "Shift change: new manager, new instructions"
  - For daemons: re-read configuration, continue running
  - Workers don't leave, they just update their work instructions

SIGINT = Ctrl+C = "Stop what you're doing NOW"
  - Interactive processes stop their current task
  - Can be caught: "let me just save this file first"

SIGCHLD = "Your child process just finished"
  - Parent processes watch for this to know when to collect child status
  - Like a text message: "I'm done with what you asked me to do"

SIGUSR1/SIGUSR2 = Custom signals (convention varies per app)
  - nginx: SIGUSR1 = "please reopen your log files"
  - Java: SIGUSR2 = "print thread dump for debugging"
```

---

### Gradual Depth - Five Levels

**Level 1:**
Know: `kill PID` (SIGTERM, graceful), `kill -9 PID` (SIGKILL, force),
`pkill nginx` (by name), `Ctrl+C` = SIGINT, `Ctrl+Z` = stop. Rule: try
SIGTERM first, wait 10-30 seconds, then SIGKILL. NEVER start with kill -9
for production services.

**Level 2:**
`kill -l` (list all signals). `trap` in bash for cleanup. SIGHUP convention
for daemon reload (`systemctl reload` usually sends SIGHUP). SIGPIPE: sent
when writing to a closed pipe - default = terminate (dangerous in apps that
use pipes; handle or ignore it). `pkill -P PPID` (kill children of parent).

**Level 3:**
`sigaction(2)` syscall in C: register signal handler with SA_RESTART flag
(restart interrupted system calls), SA_SIGINFO (extended signal info),
signal masks (block signals during handler). Signal safety: only
async-signal-safe functions in signal handlers (no malloc, no printf - only
write/send/kill/etc from the POSIX async-signal-safe list). Queued signals:
real-time signals (SIGRTMIN to SIGRTMAX, 34-64) are queued (POSIX 1003.1b),
not coalesced like standard signals.

**Level 4:**
Zombie processes: when a child exits, it stays as zombie (Z state) until
parent calls `wait()`. SIGCHLD triggers parent to call `wait()`. If parent
never calls `wait()`, zombie accumulates. Orphan adoption: when parent dies
before child, PID 1 (init/systemd) adopts the child and calls `wait()`.
Signal coalescing vs POSIX real-time signals. `signalfd(2)`: receive signals
via a file descriptor (useful in event-driven programs that use epoll).
`pidfd_send_signal(2)`: signal by pidfd to avoid PID reuse races.

**Level 5:**
Linux signal implementation in task_struct: `pending` (standard) and
`signal->shared_pending` (thread group). Multithreaded signal handling:
SIGTERM to PID goes to the process (any thread can handle it). Per-thread
signals via `tgkill()`. `SA_NODEFER`: don't block the signal during handler
(allows recursive signal delivery). ptrace and signals: debuggers use SIGTRAP
to implement breakpoints. Real-time signal use in glibc's POSIX thread
cancellation (SIGRTMIN is used internally).

---

### Code Example

**BAD - signal handling mistakes in bash:**
```bash
#!/bin/bash
# BAD: script leaves temp files on interrupt:
TMPFILE=$(mktemp)
# ... write to TMPFILE ...
# User presses Ctrl+C:
# TMPFILE is left on disk!
# Process is killed but cleanup doesn't happen.
```

**GOOD - proper signal handling in bash:**
```bash
#!/bin/bash
# GOOD: use trap for cleanup on any exit
TMPFILE=$(mktemp)

# trap COMMAND SIGNAL [SIGNAL...]
trap 'rm -f "$TMPFILE"; echo "Cleaned up"; exit' \
    EXIT INT TERM HUP

# EXIT fires on any exit (clean or otherwise)
# INT = Ctrl+C
# TERM = kill PID
# HUP = terminal hangup

# Now: Ctrl+C, kill, or normal exit all clean up

do_work() {
    echo "Processing..."
    sleep 5           # simulate work
    echo "Done"
}

echo "Working with $TMPFILE"
do_work
echo "All work complete"
# EXIT trap fires here on normal exit -> cleanup

# === Graceful service stop in bash ===
#!/bin/bash
# Service loop with graceful shutdown:
RUNNING=true
trap 'echo "Shutting down..."; RUNNING=false' TERM INT

while $RUNNING; do
    # process one item
    process_item
    sleep 1
done

# After SIGTERM: exits the loop, does cleanup:
cleanup_connections
flush_buffers
echo "Graceful shutdown complete"
exit 0

# === Java SIGTERM handler ===
# Runtime.getRuntime().addShutdownHook(new Thread(() -> {
#     log.info("SIGTERM received, starting graceful shutdown");
#     server.stop(30, TimeUnit.SECONDS);
#     dbPool.close();
#     log.info("Graceful shutdown complete");
# }, "shutdown-hook"));

# === Verify signal handling before deploying ===
# Start service, check what signals it handles:
cat /proc/$(pgrep myapp)/status | grep SigCgt
# SigCgt: 0000000180014202
# Decode: which bits are set?
python3 -c "
mask = 0x0000000180014202
for i in range(1, 65):
    if mask & (1 << (i-1)):
        print(f'Signal {i} is caught')
"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`kill` always kills a process" | `kill` sends a SIGNAL to a process - by default SIGTERM. SIGTERM is a REQUEST to terminate. A process can ignore it or delay it. Only SIGKILL guarantees termination (and even then it can be delayed briefly for cleanup in kernel). `kill -0 PID` sends no signal but checks if the process exists and you have permission - useful for checking if a process is alive. |
| "`kill -9` is the safest/quickest way to stop a process" | SIGKILL is the most CERTAIN (not safest) way. "Quick" yes. "Safe" NO - it gives the process NO chance to flush buffers, close files, release locks, or complete in-flight transactions. SIGKILL can leave databases in inconsistent states, corrupt log files, leave lock files behind. SIGTERM is the correct first step for safe shutdown. Use SIGKILL only when SIGTERM fails. |
| "You can kill any process as a regular user" | You can only send signals to processes you OWN (same UID) or processes in your session. You cannot send SIGKILL to root-owned processes without root privileges. Only root (or processes with CAP_KILL capability) can signal arbitrary processes. Exception: SIGCHLD to your own children, and some signals to processes in your process group. |
| "SIGHUP closes a process because the terminal disconnected" | SIGHUP originally meant "terminal hangup" (modem dropped the line). Daemons were designed to catch it and reload configuration instead of terminating, because they have no terminal - the signal is repurposed. By convention, most Unix daemons treat SIGHUP as "reload configuration gracefully." Some (like `nohup command`) explicitly ignore SIGHUP so they survive terminal close. `systemctl reload nginx` typically sends SIGHUP. |
| "Signals are delivered immediately" | Signals are delivered the NEXT TIME the process is scheduled for execution, not instantaneously. A process doing intensive CPU work might handle the signal on the NEXT kernel preemption point. A process blocked in a sleep() syscall is woken up by the signal delivery (syscall returns EINTR). Signal delivery ordering is not guaranteed for multiple signals of different types. |

---

### Failure Modes & Diagnosis

**Process won't die after SIGTERM (or SIGKILL):**
```bash
# Symptom: kill -9 PID and process is still running after several seconds

# Case 1: Process in D state (uninterruptible sleep) - not even SIGKILL works!
ps aux | grep PID
# Shows: D (disk wait, NFS, etc.)
cat /proc/PID/wchan   # shows kernel function the process is waiting in
dmesg | tail -20      # often shows I/O errors or NFS timeouts

# D state means the process is waiting for a kernel operation (usually I/O)
# SIGKILL is queued but not delivered until the kernel operation completes
# If it's a hung NFS mount: umount -f -l /mnt/nfs_mount  (force lazy unmount)
# If it's a broken disk: the process may need hardware intervention

# Case 2: Process is a zombie (already dead, waiting for parent to reap)
ps aux | grep PID
# Shows: Z (zombie) - process is already dead
# Cannot kill a zombie - it has no code to execute
# Fix: send SIGCHLD to the parent, or kill the parent
# The zombie will be reaped by init when parent dies

# Case 3: Process is part of a process group
# kill PID killed the parent but children continue
kill -- -$(ps -o pgid= PID | tr -d ' ')
# Sends signal to the entire process group
```

---

### Related Keywords

**Foundational:**
LNX-015 (Process Management), LNX-016 (Process Monitoring)

**Builds on this:**
LNX-031 (systemd), LNX-082 (System Call Interface)

**Related:**
OSY-025 (Interrupts), LNX-016 (Process States)

---

### Quick Reference Card

| Signal | Number | Default | Catchable | Use |
|--------|--------|---------|-----------|-----|
| SIGHUP | 1 | Terminate | Yes | Reload config (daemons) |
| SIGINT | 2 | Terminate | Yes | Ctrl+C |
| SIGKILL | 9 | Terminate | NO | Force kill |
| SIGTERM | 15 | Terminate | Yes | Graceful shutdown |
| SIGUSR1 | 10 | Terminate | Yes | User-defined |
| SIGUSR2 | 12 | Terminate | Yes | User-defined |
| SIGSTOP | 19 | Stop | NO | Force pause |
| SIGTSTP | 20 | Stop | Yes | Ctrl+Z |

**3 things to remember:**
1. SIGKILL (9) and SIGSTOP (19) CANNOT be caught, blocked, or ignored
2. Always try SIGTERM first; wait 10-30s; then SIGKILL
3. Use `trap` in bash scripts for cleanup on Ctrl+C/kill/exit

---

### Transferable Wisdom

Signal handling concepts appear in: Docker stop (SIGTERM then SIGKILL after
timeout, configured with `STOPSIGNAL` in Dockerfile), Kubernetes graceful
termination (sends SIGTERM to PID 1, waits terminationGracePeriodSeconds,
then SIGKILL - default 30s), Spring Boot graceful shutdown (`server.shutdown=graceful`
in application.properties - handles SIGTERM gracefully), systemd service
stop (sends SIGTERM, waits TimeoutStopSec, then SIGKILL), AWS ECS task stop
(same pattern as Docker/Kubernetes).

The pattern: "request graceful shutdown (SIGTERM/equivalent), wait, then
force (SIGKILL/equivalent)" is universal in distributed systems - it's the
same as: Kubernetes pod deletion, EC2 instance termination, database shutdown
(`MySQL: SIGTERM` = flush + graceful). Any system managing processes needs
to implement this pattern.

---

### The Surprising Truth

When you press Ctrl+C in a terminal, the kernel sends SIGINT to the entire
foreground **process group**, not just the current process. This is why
running a shell script and pressing Ctrl+C also terminates child processes
spawned by the script - they're in the same process group. This is also
why background processes (`command &`) survive when you press Ctrl+C - they're
in a different process group. The terminal line discipline (TTY subsystem)
is responsible for converting the Ctrl+C keypress into a SIGINT signal to
the foreground process group. This is a kernel feature of the TTY layer,
completely separate from the application. Docker containers without a TTY
don't get this behavior - sending SIGINT to a Docker container requires
`docker kill --signal=SIGINT container`. This is why `docker stop` uses
SIGTERM (not SIGINT) - it doesn't rely on TTY-based signal forwarding.

---

### Mastery Checklist

- [ ] Knows SIGTERM vs SIGKILL and when to use each
- [ ] Can use kill, pkill, and verify process received signal
- [ ] Can implement signal handlers in bash scripts with trap
- [ ] Understands SIGHUP convention for daemon reload
- [ ] Knows why SIGKILL cannot stop a process in D state

---

### Think About This

1. You have a Java microservice that stores user session data in memory.
   `docker stop` (which sends SIGTERM) causes sessions to be lost because
   the JVM exits before persisting them. The JVM is PID 1 in the container.
   What is the complete solution? (Consider: Docker Dockerfile, JVM shutdown
   hooks, terminationGracePeriodSeconds in Kubernetes.)

2. A bash script runs several background jobs with `&`. You add `trap
   'kill %1 %2 %3; exit' INT TERM`. But when you send SIGTERM to the
   script, it kills the background jobs and exits, but some of the jobs
   leave partial files behind because they weren't given time to finish.
   How would you modify the trap to give background jobs 10 seconds to
   finish before killing them?

3. A long-running data processing script is consuming 100% CPU. You can't
   `kill -9` it because it holds a lock file that blocks other processes.
   But `kill -SIGTERM` seems to be ignored. Looking at `/proc/PID/status`
   you see `SigBlk: 0000000000008000` (bit 15 = SIGTERM is blocked). How
   is the process blocking SIGTERM? Is there any signal you can send that
   will terminate it? How do you handle the lock file?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between SIGTERM and SIGKILL, and when would you use each?
A: SIGTERM (signal 15) is a termination REQUEST. The process can catch it, run cleanup code (flush buffers, close connections, release locks, log "shutting down"), and then exit gracefully. It can also ignore SIGTERM entirely (though well-behaved applications don't). Use SIGTERM for: normal service shutdown, giving the application time to complete in-flight work, maintaining data integrity. SIGKILL (signal 9) is an UNCONDITIONAL termination by the kernel. It cannot be caught, blocked, or ignored. The kernel immediately terminates the process. No code runs. File buffers may not be flushed, database transactions may be incomplete, lock files may be left behind, network connections are hard-reset. Use SIGKILL only when: SIGTERM was sent and the process didn't exit within a reasonable time (10-30 seconds), the process is hung and SIGTERM is blocked, emergency situations. Standard pattern: `kill -SIGTERM $PID; sleep 30; kill -0 $PID 2>/dev/null && kill -SIGKILL $PID`. This sends SIGTERM, waits 30 seconds, checks if still alive (kill -0), and only then sends SIGKILL. Never start with SIGKILL for production services.

**Intermediate:**
Q: How does a daemon reload its configuration without dropping connections? Explain the role of SIGHUP.
A: The SIGHUP (hangup) signal was originally sent when a terminal connection dropped. Daemons (which have no terminal) redefine SIGHUP by convention to mean "reload configuration." The mechanism for nginx's graceful config reload: (1) Admin sends SIGHUP: `kill -HUP $(cat /var/run/nginx.pid)` or `nginx -s reload` or `systemctl reload nginx`. (2) nginx's signal handler is invoked. It calls `sigaction()` registered handler. (3) Master process reads and validates new configuration. If validation fails, continues with old config (no downtime). (4) Master process forks new worker processes with new configuration. (5) Master process sends SIGQUIT to old workers (graceful exit): old workers finish handling in-flight requests, accept no new connections. (6) Old workers exit when they finish. New workers handle all new connections with new config. Result: zero connection drops, zero downtime, configuration updated. This pattern: read new config, fork new workers, gracefully drain old workers, is the industry standard. Kubernetes performs rolling updates (new pods, then old pods drained) for the same reason - stateless scaling version of SIGHUP reload.

**Expert:**
Q: In a Kubernetes environment, a pod fails to shut down gracefully within terminationGracePeriodSeconds. Walk through the complete pod termination sequence and explain how you would debug and fix this.
A: Complete Kubernetes pod termination sequence: (1) Pod marked for deletion: API server sets DeletionTimestamp on pod. terminationGracePeriodSeconds countdown begins (default 30s). (2) Endpoint removal: kube-proxy updates iptables/ipvs rules to stop routing new traffic to this pod. (3) PreStop hook (if configured): container's lifecycle.preStop hook runs. Could be an HTTP call (`httpGet`) or command (`exec`). If this takes longer than terminationGracePeriodSeconds: kubelet sends SIGKILL directly. (4) SIGTERM to PID 1: kubelet sends SIGTERM to the container's PID 1 (the process with PID 1 inside the container). If using Docker exec form CMD: your app is PID 1 and receives SIGTERM directly. If using shell form CMD: shell is PID 1 and may not forward SIGTERM to child processes. (5) Wait: kubelet waits for process to exit voluntarily. (6) SIGKILL: if process hasn't exited by terminationGracePeriodSeconds: kubelet sends SIGKILL. Pod shows status 137 (128+9). Debugging: `kubectl describe pod` shows current phase and events. Check exit code: `kubectl get pod -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}'`. 137 = SIGKILL (timeout). 143 = SIGTERM (graceful). Check if PID 1 is shell: `kubectl exec pod -- cat /proc/1/cmdline | tr '\0' ' '`. Fixes: (A) Use exec form in Dockerfile CMD/ENTRYPOINT. (B) Add shutdown hook: Java's Runtime.getRuntime().addShutdownHook(). (C) Increase terminationGracePeriodSeconds: `spec.terminationGracePeriodSeconds: 120`. (D) Add preStop hook: `lifecycle: preStop: exec: command: ["/bin/sleep", "15"]` to drain connections before SIGTERM. (E) Handle SIGTERM in application code: register signal handler that completes in-flight requests, then calls System.exit(0).
