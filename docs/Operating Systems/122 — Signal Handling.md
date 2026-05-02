---
layout: default
title: "Signal Handling"
parent: "Operating Systems"
nav_order: 122
permalink: /operating-systems/signal-handling/
number: "0122"
category: Operating Systems
difficulty: ★★★
depends_on: Process, System Call (syscall), Fork — Exec
used_by: Graceful Shutdown, Process Supervision, Unix Daemons
related: SIGTERM, SIGKILL, SIGINT, sigaction, kill()
tags:
  - os
  - process-management
  - linux
  - ipc
---

# 122 — Signal Handling

⚡ TL;DR — Signals are asynchronous software interrupts sent to a process; signal handlers let a process respond to termination requests, crashes, and external notifications without polling.

| #0122           | Category: Operating Systems                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Process, System Call (syscall), Fork — Exec          |                 |
| **Used by:**    | Graceful Shutdown, Process Supervision, Unix Daemons |                 |
| **Related:**    | SIGTERM, SIGKILL, SIGINT, sigaction, kill()          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You deploy a web server. The OS needs to stop it for a software update. Without signals: the OS must kill the process immediately (losing in-flight requests), or you need a polling mechanism (server constantly checks a "should I stop?" flag). Polling burns CPU and adds latency to the shutdown check. Immediate kill loses state. You need a way to say: "stop cleanly, when ready."

**THE BREAKING POINT:**
Asynchronous events — hardware faults (SIGSEGV, bus error), user interrupts (Ctrl+C → SIGINT), process management (SIGTERM, SIGKILL), and inter-process notifications — need to be delivered to a process without that process needing to poll. The process shouldn't need to know when these events might arrive. They're inherently asynchronous: a segfault happens at an instruction; Ctrl+C happens when the user presses it.

**THE INVENTION MOMENT:**
Unix V1 (1969) had signals as a simple "kill the process" mechanism. Unix V7 (1979) introduced `signal()` — allow processes to install handler functions. POSIX.1 (1988) added `sigaction()` with reliable semantics: masks, restart flags, and the siginfo_t structure. The evolution: from "kill" → "intercept and handle" → "inspect cause and recover".

---

### 📘 Textbook Definition

A **signal** is an asynchronous notification sent to a process or thread, indicating that a specific event has occurred. Signals are defined by number and name (SIGTERM=15, SIGKILL=9, SIGSEGV=11, etc.). Each signal has a **default disposition**: terminate, terminate+core, ignore, or stop/continue the process. A process may override the default disposition for most signals by installing a **signal handler** using `sigaction()`. **SIGKILL** (9) and **SIGSTOP** (19/17) cannot be caught, blocked, or ignored — they are always delivered.

Signal delivery is asynchronous: the signal is delivered to the process at the next safe kernel-to-userspace transition, not necessarily immediately. Signals can be **blocked** (deferred) using signal masks (`sigprocmask()`, `pthread_sigmask()`). A blocked signal remains **pending** until unblocked. **Real-time signals** (SIGRTMIN to SIGRTMAX) are queued (multiple identical signals are not merged); standard signals are not queued (duplicate pending signals are collapsed).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Signals = software interrupts; `SIGTERM` = "please stop"; `SIGKILL` = "stop now, no choice"; your handler = what you do when you get them.

**One analogy:**

> Signals are like a tap on the shoulder while you're working. SIGINT (Ctrl+C) is a polite "excuse me, stop." SIGTERM is a formal "please wrap up." SIGKILL is a forceful grab — you can't ignore it. Your signal handler is your trained response to each type of tap — you can decide to finish your sentence (graceful shutdown) or immediately drop everything (immediate shutdown).

**One insight:**
The reason signal handlers are hard to write correctly: they're asynchronous — they can interrupt your code at any point, even in the middle of a non-reentrant function. A signal handler must only call async-signal-safe functions (a short list). Nearly all the useful C standard library functions (malloc, printf, pthread_mutex_lock) are NOT async-signal-safe.

---

### 🔩 First Principles Explanation

SIGNAL LIFECYCLE:

1. **Generation**: Signal is sent via `kill()`, hardware exception (fault), kernel event (child exits → SIGCHLD).
2. **Pending**: Signal is recorded in the process's `pending` bitmask (task_struct.pending).
3. **Delivery**: At kernel-userspace transition (syscall return, interrupt return), kernel checks for pending unblocked signals → delivers.
4. **Disposition**: Default (terminate/core/stop/ignore) OR custom handler OR SIG_IGN.

SIGNAL MASKS:

```c
sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGTERM);
sigprocmask(SIG_BLOCK, &mask, NULL);  // Block SIGTERM
// SIGTERM is now pending (if sent) but not delivered
// Critical section here — SIGTERM won't interrupt
sigprocmask(SIG_UNBLOCK, &mask, NULL); // Deliver pending SIGTERM
```

ASYNC-SIGNAL-SAFETY:
A signal handler can interrupt ANY instruction in the program, including inside malloc (holding internal lock), inside printf (mid-format), or inside your own mutex lock. Calling these from a signal handler → deadlock or corruption.
Safe pattern: signal handler sets a `volatile sig_atomic_t flag = 1;`, main loop checks the flag.

**THE TRADE-OFFS:**
**Gain:** Asynchronous process-level notification without polling; hardware fault interception (SIGSEGV for GC, SIGBUS for mmap errors).
**Cost:** Signal handlers are extremely hard to write correctly (async-signal-safety); POSIX signal model has subtleties around fork/threads; real-time signals (queueing) add complexity.

---

### 🧪 Thought Experiment

GRACEFUL SHUTDOWN WITH SIGTERM:

```
Kubernetes (or systemctl stop): sends SIGTERM to PID 1 of container
→ Process has SIGTERM handler registered

SIGTERM handler: sets shutdown_requested = 1
Main loop checks shutdown_requested:
  - Stop accepting new connections
  - Wait for in-flight requests to complete (30s timeout)
  - Flush write-behind caches
  - Close database connections
  - Exit(0)

Kubernetes waits 30s (terminationGracePeriodSeconds)
If process hasn't exited after 30s: sends SIGKILL (cannot be caught)
Process is forcibly killed
```

If process has no SIGTERM handler: default disposition = terminate immediately → in-flight requests dropped.

If process ignores SIGTERM (SIG_IGN): Kubernetes waits full grace period, then sends SIGKILL. Processes that ignore SIGTERM cause unnecessary delay in rolling deployments.

**THE INSIGHT:**
A `SIGTERM` handler is the contract between the process and its process supervisor (systemd, Kubernetes, Docker). All production processes must handle SIGTERM gracefully. This is the #1 rule of writing containers.

---

### 🧠 Mental Model / Analogy

> A process is like a chef working in a kitchen. Signals are messages handed to them:
>
> - SIGTERM: "Chef, please finish what you're cooking and then close up."
> - SIGKILL: "FIRE — everyone out NOW" (no one can ignore this).
> - SIGINT: Ctrl+C at the terminal — "Hey, I changed my mind, can you stop?"
> - SIGCHLD: "Chef, your kitchen assistant (child process) just finished their task."
> - SIGSEGV: "Chef, you tried to grab something from an empty shelf that doesn't exist" (segfault).

> The signal handler is the chef's trained response to each message. A well-trained chef finishes plating the current dish before walking out on SIGTERM. An untrained chef drops everything mid-dish (default: terminate).

Where this breaks down: signal handlers are not like normal function calls — they interrupt the chef mid-sentence, in the middle of a word. That's why you can't "grab new ingredients" (call malloc) from inside a signal handler — the kitchen's supply chain is mid-operation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Signals are messages the OS sends to your program: "please stop", "you crashed", "your child process finished". You can write code to respond to these messages — for example, saving your data before stopping. But the OS can also force-kill your program with SIGKILL, which no code can prevent.

**Level 2 — How to use it (junior developer):**
In Java: `Runtime.getRuntime().addShutdownHook(new Thread(() -> cleanup()))` — this runs on SIGTERM/SIGINT but not SIGKILL. In Python: `signal.signal(signal.SIGTERM, handler)`. In Node.js: `process.on('SIGTERM', handler)`. For containers: always handle SIGTERM with a graceful shutdown of at most 30s (Kubernetes default terminationGracePeriodSeconds). Never register signal handlers in library code — only in application entry points.

**Level 3 — How it works (mid-level engineer):**
Signal delivery in Linux (kernel): `send_signal()` → sets bit in `pending.signal` bitmask in `task_struct` → sets `TIF_SIGPENDING` flag. At every kernel-userspace return (after syscall, after interrupt handler), the kernel calls `do_signal()` → `get_signal()` → if handler registered: sets up user-space signal frame on the process stack → jumps to handler. After handler returns: `sigreturn()` syscall restores the original execution context (saved register state). This is why a segfault in a signal handler kills the process — the stack frame is corrupted and sigreturn fails.

**Level 4 — Why it was designed this way (senior/staff):**
The "signal handler set a flag, main loop checks flag" pattern emerged because POSIX's async-signal-safety requirement (only ~50 functions are safe) severely limits what you can do directly in a handler. The alternative pattern for complex signal handling: `signalfd()` (Linux 2.6.22) — convert signal delivery to file descriptor reads. The signal is queued as a byte on an fd, readable with `read()` or `epoll`. This makes signals composable with event loops (epoll, io_uring) and eliminates async-signal-safety concerns: you read the signal in the main loop, just like any other I/O event. Golang uses this approach internally; Rust's `signal_hook` crate uses this pattern too.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              SIGNAL DELIVERY FLOW                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  kill(pid, SIGTERM)            Process (PID=100)       │
│       │                              │                 │
│       ▼                              │                 │
│  Kernel: task_struct[100]            │                 │
│    pending.signal |= SIGTERM         │                 │
│    set TIF_SIGPENDING flag           │                 │
│                                      │                 │
│  [Process running user code]         │                 │
│                                      │                 │
│  [syscall or interrupt]              │                 │
│       │                              │                 │
│       ▼                              ▼                 │
│  Kernel: do_signal()          Signal frame pushed     │
│    → TIF_SIGPENDING set?       to user stack          │
│    → Is SIGTERM blocked?       Registers saved        │
│    → No → get_signal()         PC → handler()         │
│    → handler registered?              │               │
│    → Yes → set up signal frame        ▼               │
│                               handler() runs          │
│                                       │               │
│                               sigreturn() syscall     │
│                               Registers restored      │
│                               Resume original code    │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

SPRING BOOT / JAVA APPLICATION GRACEFUL SHUTDOWN:

```
1. Kubernetes decides to roll deploy new version
2. Pod gets SIGTERM (from Kubernetes → Docker → PID 1 in container)

3. JVM signal handler (built-in):
   - Triggers JVM shutdown sequence
   - Runs all registered ShutdownHooks (in parallel)

4. Spring Boot ShutdownHook:
   - Sets application context to "closing"
   - SmartLifecycle beans: server.stop() (stops accepting connections)
   - Waits for in-flight requests (spring.lifecycle.timeout-per-shutdown-phase=30s)
   - Closes DataSource connections
   - Flushes caches
   - Destroys beans (destroy() methods)

5. JVM exits normally (exit code 0)

6. If 30s exceeded before JVM exits:
   Kubernetes sends SIGKILL → JVM terminates immediately (no hooks run)
```

Java shutdown hook setup:

```java
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    log.info("SIGTERM received, starting graceful shutdown...");
    server.stop(30_000);  // 30s for in-flight requests
    dataSource.close();
    log.info("Graceful shutdown complete.");
}, "shutdown-hook"));
```

---

### 💻 Code Example

Example 1 — sigaction (POSIX, recommended over signal()):

```c
#include <signal.h>
#include <stdio.h>
#include <stdatomic.h>

static volatile sig_atomic_t shutdown_requested = 0;

// Async-signal-safe handler: only sets flag
static void handle_sigterm(int sig) {
    (void)sig;  // unused
    shutdown_requested = 1;
}

int main() {
    struct sigaction sa = {0};
    sa.sa_handler = handle_sigterm;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;  // Restart interrupted syscalls
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);

    printf("Server running (PID %d). Send SIGTERM to stop.\n", getpid());
    while (!shutdown_requested) {
        // Main work loop
        process_next_request();
    }
    printf("Graceful shutdown initiated.\n");
    flush_and_close();
    return 0;
}
```

Example 2 — signalfd (Linux, event-loop friendly):

```c
#include <sys/signalfd.h>
#include <signal.h>

// Block SIGTERM (prevent default delivery)
sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGTERM);
sigaddset(&mask, SIGINT);
sigprocmask(SIG_BLOCK, &mask, NULL);

// Create signalfd: SIGTERM/SIGINT appear as readable events
int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);

// Add sfd to epoll alongside accept socket
epoll_ctl(epfd, EPOLL_CTL_ADD, sfd, &ev);

// In event loop:
struct signalfd_siginfo si;
if (read(sfd, &si, sizeof(si)) == sizeof(si)) {
    printf("Received signal %u\n", si.ssi_signo);
    if (si.ssi_signo == SIGTERM) start_graceful_shutdown();
}
```

Example 3 — Python signal handler (application):

```python
import signal
import sys

shutdown_requested = False

def handle_sigterm(signum, frame):
    global shutdown_requested
    print(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT,  handle_sigterm)

print(f"Server running (PID {os.getpid()})")
while not shutdown_requested:
    process_request()

# Cleanup
close_connections()
sys.exit(0)
```

---

### ⚖️ Comparison Table

| Signal        | Number | Default Action | Catchable?      | Common Use                  |
| ------------- | ------ | -------------- | --------------- | --------------------------- |
| **SIGTERM**   | 15     | Terminate      | Yes             | Graceful shutdown request   |
| **SIGKILL**   | 9      | Terminate      | **No**          | Forced kill (last resort)   |
| **SIGINT**    | 2      | Terminate      | Yes             | Ctrl+C user interrupt       |
| **SIGSEGV**   | 11     | Terminate+core | Yes (dangerous) | Segmentation fault          |
| **SIGCHLD**   | 17/20  | Ignore         | Yes             | Child process state changed |
| **SIGHUP**    | 1      | Terminate      | Yes             | Reload config (daemons)     |
| **SIGALRM**   | 14     | Terminate      | Yes             | Timer expiry                |
| **SIGUSR1/2** | 10/12  | Terminate      | Yes             | Application-defined         |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                           |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "SIGTERM always kills immediately"                  | SIGTERM is a REQUEST — the process can catch it and handle gracefully; SIGKILL is the forced kill |
| "Signal handlers can call any function"             | Only async-signal-safe functions; most useful functions (malloc, printf, locks) are NOT safe      |
| "kill -9 is always the right way to stop a process" | Only as a last resort; prevents cleanup and data loss; always try SIGTERM first                   |
| "Java shutdown hooks run on SIGKILL"                | No — JVM hooks only run on SIGTERM/SIGINT/normal exit; SIGKILL is unblockable                     |

---

### 🚨 Failure Modes & Diagnosis

**1. Graceful Shutdown Not Occurring in Container**

**Symptom:** `docker stop` waits 10s then forcefully kills; "graceful shutdown" log messages never appear; in-flight requests are dropped.

**Root Cause:** PID 1 in container is a shell script, not the application. Shell does not forward SIGTERM to the application. Application never receives SIGTERM.

**Diagnostic:**

```bash
docker exec <container> ps aux   # Is PID 1 the app or a shell?
# If PID 1 = /bin/sh -c "java -jar app.jar" → shell is PID 1
```

**Fix:**

```dockerfile
# WRONG: shell form (PID 1 = sh)
CMD java -jar app.jar

# CORRECT: exec form (PID 1 = java)
CMD ["java", "-jar", "app.jar"]

# Or use a proper init: tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["java", "-jar", "app.jar"]
```

---

**2. Signal Handler Deadlock**

**Symptom:** Process receives SIGTERM, hangs indefinitely, never exits; SIGKILL required.

**Root Cause:** Signal handler calls a non-async-signal-safe function that takes a lock; the signal interrupted the main thread while that same lock was held.

**Diagnostic:**

```bash
gdb -p <pid>
(gdb) thread apply all bt  # Check all thread stacks
# Look for: main thread in malloc/printf holding lock
#           signal handler also trying to acquire same lock
```

**Fix:** Signal handler only sets `volatile sig_atomic_t shutdown = 1;`. Main loop checks and calls cleanup functions (not the signal handler).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — signals are sent to processes; need process model
- `System Call (syscall)` — signal() and sigaction() are syscalls; signal delivery happens at syscall boundaries
- `Fork — Exec` — signals interact with fork (inherited handlers) and exec (handlers reset to default)

**Builds On This (learn these next):**

- `Unix Daemons` — use SIGHUP for config reload, SIGTERM for stop
- `Process Supervision` — supervisors (systemd, Docker) use SIGTERM+SIGKILL lifecycle
- `Graceful Shutdown Patterns` — the production application of SIGTERM handling

**Alternatives / Comparisons:**

- `signalfd()` — Linux file-descriptor-based signal delivery; composable with epoll/io_uring
- `eventfd()` — simpler fd-based notification for same-process inter-thread events

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Asynchronous software interrupts for OS  │
│              │ events and process notifications          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Notify processes of async events         │
│ SOLVES       │ (shutdown, fault, child exit) w/o polling │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ SIGTERM = request (catchable); SIGKILL=9  │
│              │ = force (uncatchable — always delivered)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Implementing graceful shutdown; writing   │
│              │ daemon reload logic; debugging hangs      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Inter-thread notifications (use         │
│              │ atomic flags or condition variables)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Asynchronous notification vs complex     │
│              │ safety constraints in handlers           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SIGTERM = please stop; SIGKILL = stop   │
│              │  now; signal handler = your response"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ signalfd → Graceful Shutdown → PID 1     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A JVM process is the target of a SIGSEGV (segmentation fault). JVM's HotSpot registers its own SIGSEGV signal handler for two legitimate purposes: (1) null pointer exception handling (NullPointerException is implemented via SIGSEGV — accessing address 0 causes segfault → JVM handler catches it → throws NPE to Java code) and (2) GC write barriers (some GC implementations use memory protection faults as notifications). Explain how JVM's SIGSEGV handler distinguishes between: a "legitimate" NPE (should be converted to Java NPE), a GC write barrier signal (should be consumed silently), and a real native crash (should generate a hs_err_pid.log and terminate). What `siginfo_t` fields does it use to make this distinction?

**Q2.** Linux's `init` (PID 1) has a special relationship with signals: SIGTERM and SIGKILL are **not** delivered to PID 1 by the kernel (to prevent accidental termination of the entire system). However, `kill -9 1` from root actually does kill PID 1 — because the kernel allows it specifically for root. In a Docker container, your application runs as PID 1. If your application code does `signal(SIGTERM, SIG_IGN)`, it will not receive SIGTERM. But unlike real PID 1, `docker stop` eventually escalates to SIGKILL. Explain the exact kernel mechanism by which PID 1 signal suppression works (`SIGNAL_UNKILLABLE` flag), why it applies to container PID 1 (the "init" of the container's PID namespace), and what `tini` (a tiny init) specifically does differently that makes it the recommended PID 1 for containers.
