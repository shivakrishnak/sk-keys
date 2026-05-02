---
layout: default
title: "Signals (SIGTERM, SIGKILL, SIGHUP)"
parent: "Linux"
nav_order: 161
permalink: /linux/signals/
number: "0161"
category: Linux
difficulty: ★★☆
depends_on: Process Management
used_by: Containers, Shell Scripting, DevOps
related: Process Management, Zombie Processes, Containers
tags:
  - linux
  - os
  - processes
  - devops
---

# 161 — Signals (SIGTERM, SIGKILL, SIGHUP)

⚡ TL;DR — Signals are asynchronous notifications sent to processes to request or force a state change; `SIGTERM` asks a process to terminate gracefully, `SIGKILL` forces immediate kernel-level termination (cannot be caught), and `SIGHUP` historically meant "terminal disconnect" but is now widely used to trigger configuration reload.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
How do you stop a running process? You could kill its terminal — but background processes have no terminal. You could pull power — but the process won't clean up files, close sockets, or finish writing data. You could write application-specific APIs — but then every program needs a different stop mechanism.

**THE BREAKING POINT:**
A web server is handling 1000 active connections. You need to restart it for a config change. Without signals: either kill -9 the process (drops all connections instantly, clients get TCP reset, in-flight requests fail) or find some application-specific way to trigger a restart.

**THE INVENTION MOMENT:**
Unix signals provide the standard mechanism: `SIGTERM` tells nginx "please stop." nginx catches SIGTERM, finishes current requests, then exits cleanly. This is graceful shutdown. `SIGHUP` tells nginx "please reload your config without restarting" — nginx forks new workers with new config, waits for old workers to finish their requests, then terminates the old workers. Zero-downtime reload via a signal.

---

### 📘 Textbook Definition

A **signal** is an asynchronous software interrupt delivered to a process by the kernel, another process, or the process itself. Each signal has a number and a symbolic name. Common default actions include: **Terminate** (process exits), **Core** (exits and writes core dump), **Ignore**, **Stop** (suspends execution), **Continue** (resumes). Processes can install **signal handlers** (custom functions) for most signals, overriding the default action. `SIGKILL` (9) and `SIGSTOP` (19) cannot be caught, blocked, or ignored — they are always handled by the kernel directly.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Signals are the kernel's way of poking a process: "please stop," "stop NOW," "reload your config," "you divided by zero."

**One analogy:**
> Signals are like messages slipped under a door. SIGTERM is a polite note: "Please finish up and leave." The occupant (process) can choose how to respond — finish the current task, save work, then exit. SIGKILL is a battering ram: the kernel breaks down the door and removes the occupant immediately, regardless of what they're doing. SIGHUP is a note saying "Management changed the rules — please update your procedures." The occupant (process) can choose what "updating procedures" means (often: re-read config, continue working).

**One insight:**
The difference between `SIGTERM` and `SIGKILL` is the difference between asking and forcing. Always try SIGTERM first and wait — most well-written processes will clean up. Use SIGKILL only when SIGTERM fails. A process that ignores SIGTERM (stuck in a loop, buggy handler) requires SIGKILL.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Asynchronous delivery**: a signal can arrive at any point during a process's execution — between any two instructions.
2. **Cannot be blocked**: `SIGKILL` and `SIGSTOP` are always delivered immediately by the kernel; no signal handler or `sigprocmask` can block them.
3. **Per-process delivery**: signals are sent to a specific process (by PID) or a process group; `kill -TERM 0` sends to the entire process group.
4. **Handler inheritance**: child processes inherit the parent's signal dispositions; after `exec()`, custom handlers reset to defaults but ignored signals stay ignored.

**SIGNAL TABLE (key signals):**

| Signal | Number | Default Action | Can Catch? | Common Use |
|---|---|---|---|---|
| SIGHUP | 1 | Terminate | Yes | Reload config |
| SIGINT | 2 | Terminate | Yes | Ctrl+C |
| SIGQUIT | 3 | Core dump | Yes | Ctrl+\ |
| SIGKILL | 9 | Terminate | **No** | Force kill |
| SIGUSR1 | 10 | Terminate | Yes | App-defined |
| SIGUSR2 | 12 | Terminate | Yes | App-defined |
| SIGTERM | 15 | Terminate | Yes | Graceful stop |
| SIGCHLD | 17 | Ignore | Yes | Child state change |
| SIGSTOP | 19 | Stop | **No** | Pause process |
| SIGCONT | 18 | Continue | Yes | Resume process |

**THE TRADE-OFFS:**
**SIGTERM:** Graceful shutdown — data integrity, connection draining, cleanup. Risk: process might ignore or hang.
**SIGKILL:** Guaranteed termination. Risk: data corruption, half-written files, leaked external resources (DB connections, locks).
**SIGHUP:** Elegant zero-downtime reload. Risk: process might not implement SIGHUP handler (default: terminate!).

---

### 🧪 Thought Experiment

**SETUP:**
A containerised Python Flask application receives a SIGTERM when Kubernetes decides to terminate the pod.

**SCENARIO A — No signal handler:**
```
Kubernetes sends SIGTERM
Flask has no SIGTERM handler
Default action: immediate process exit
In-flight HTTP requests: aborted mid-response
Database transactions: not committed or rolled back
Client: gets TCP RST or incomplete response
Pod status: Completed
But: clients saw errors
```

**SCENARIO B — Graceful shutdown handler:**
```python
import signal, sys, time

shutdown = False

def handle_sigterm(sig, frame):
    global shutdown
    shutdown = True  # Signal app to stop accepting new requests
    # Wait up to 30s for in-flight requests to complete
    time.sleep(0)  # yield; request handlers will check shutdown flag

signal.signal(signal.SIGTERM, handle_sigterm)
```
```
Kubernetes sends SIGTERM
Handler sets shutdown=True
In-flight requests: complete normally
New requests: rejected (503 Service Unavailable)
After 30s (or all requests done): process exits
Client: sees clean responses or polite 503, not TCP RST
```

**THE INSIGHT:**
PID 1 in a container receives all signals. A shell script as PID 1 (`CMD ["/bin/sh", "-c", "python app.py"]`) does NOT forward SIGTERM to child processes. This is why "exec form" (`CMD ["python", "app.py"]`) is critical — it makes the application PID 1 directly, so it receives SIGTERM directly.

---

### 🧠 Mental Model / Analogy

> Signals are like emergency procedures in an office building. SIGTERM is the fire warden saying "Please calmly evacuate now" — each person (process) can finish their current sentence, save their document, and walk out. SIGKILL is the fire marshal physically removing everyone from the building immediately — no time to save anything. SIGHUP is HR sending a "New HR policies effective today — please re-read the handbook" email — each department (process) handles this in their own way (most reload config). SIGCHLD is HR getting notified that an employee (child process) has changed status (exited or stopped). SIGSTOP is "everyone freeze" — no one can move until SIGCONT arrives.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Signals are notifications sent to running programs. `kill -15 PID` politely asks a program to stop. `kill -9 PID` forces it to stop immediately no matter what. Programs can listen for signals and do something specific — like saving their work before stopping, or reloading settings without restarting.

**Level 2 — How to use it (junior developer):**
`kill -SIGTERM <PID>` (same as `kill -15` or just `kill`): ask process to terminate gracefully. `kill -SIGKILL <PID>` (same as `kill -9`): force terminate. `kill -SIGHUP <PID>`: send SIGHUP (often triggers config reload). `pkill nginx`: send SIGTERM by name. `killall -SIGKILL myapp`: SIGKILL all processes named myapp. `kill -l`: list all signals. `trap 'cleanup' SIGTERM SIGINT` in shell scripts: run cleanup function on SIGTERM/Ctrl+C.

**Level 3 — How it works (mid-level engineer):**
Signal delivery: kernel marks the `pending` bitmask in the task's `task_struct`. At the next return from syscall or interrupt, the kernel checks pending signals and delivers them. If the process has a handler registered via `sigaction()`, the kernel sets up a special stack frame and redirects execution to the handler. The handler runs, then a `sigreturn` syscall returns execution to the interrupted point. For real-time signals (`SIGRTMIN`+): signals queue (can have multiple pending); standard signals don't queue (second SIGTERM before first is handled is lost). `sigprocmask` can block (defer) most signals during critical sections.

**Level 4 — Why it was designed this way (senior/staff):**
The SIGKILL-cannot-be-caught design is a fundamental Unix safety mechanism: if a process could catch and ignore SIGKILL, there would be no reliable way to terminate a misbehaving process. This is why `kill -9` is the "nuclear option" — it's guaranteed by the kernel, not dependent on process cooperation. The SIGHUP "reload" convention emerged from the fact that in old Unix systems, closing the terminal (which "hung up" the modem) sent SIGHUP to all processes in that terminal's session, telling them their terminal was gone. Daemons (which have no terminal) were written to catch SIGHUP and treat it as "reload config" rather than terminate — because receiving SIGHUP without a terminal is meaningless otherwise. This convention is now universal: nginx, PostgreSQL, HAProxy, systemd — all use SIGHUP for zero-downtime reload.

---

### ⚙️ How It Works (Mechanism)

**Sending signals:**
```bash
# By PID
kill -SIGTERM 1234    # graceful stop
kill -SIGKILL 1234    # force stop
kill -SIGHUP 1234     # reload config
kill -SIGUSR1 1234    # application-defined

# Shorthand
kill 1234             # default: SIGTERM
kill -9 1234          # SIGKILL

# By name
pkill nginx           # SIGTERM to all nginx processes
pkill -9 zombie_app   # SIGKILL to all zombie_app
killall nginx         # SIGTERM (all instances)

# To process group (negative PID)
kill -SIGTERM -1234   # send SIGTERM to process group 1234

# List all signals
kill -l
```

**Signal handlers in shell scripts:**
```bash
#!/bin/bash
# Graceful shutdown in a shell script

cleanup() {
  echo "SIGTERM received, cleaning up..."
  # Remove temp files, close connections, etc.
  rm -f /tmp/myapp.lock
  echo "Cleanup done, exiting"
  exit 0
}

# Register handler for SIGTERM and SIGINT (Ctrl+C)
trap cleanup SIGTERM SIGINT

echo "Starting (PID $$)..."
echo $$ > /tmp/myapp.pid

# Main work loop
while true; do
  do_work
  sleep 1
done
```

**Signal handlers in Python:**
```python
import signal
import sys
import time

def graceful_shutdown(signum, frame):
    """Handle SIGTERM gracefully."""
    print(f"Signal {signum} received — shutting down")
    # Set shutdown flag; main loop will finish current work
    global running
    running = False

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

# SIGHUP handler for config reload
def reload_config(signum, frame):
    """Handle SIGHUP — reload configuration."""
    print("SIGHUP received — reloading config")
    load_config()  # Re-read config file

signal.signal(signal.SIGHUP, reload_config)

running = True
while running:
    process_next_item()
    time.sleep(0.1)

print("Shutdown complete")
sys.exit(0)
```

**Checking signal handling of a process:**
```bash
# View signal disposition of a running process
cat /proc/1234/status | grep -i sig
# SigBlk: 0000000000000000  (blocked signals bitmask)
# SigIgn: 0000000000000000  (ignored signals)
# SigCgt: 0000000180000000  (caught/handled signals)

# Decode signal bitmask
python3 -c "
import signal
mask = 0x0000000180000000  # from SigCgt
for sig in signal.Signals:
    if mask & (1 << (sig.value - 1)):
        print(f'  Caught: {sig.name} ({sig.value})')
"
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Kubernetes graceful pod shutdown              │
└────────────────────────────────────────────────┘

 kubectl delete pod mypod
       │
       ▼
 Kubernetes sets pod to "Terminating"
 Removes pod from service endpoints
 (new traffic stops routing to this pod)
       │
       ▼
 After preStop hook (if defined):
 kubelet sends SIGTERM to PID 1 in each container
       │
  ┌────┴──────────────────────────────┐
  │ GOOD: app handles SIGTERM         │ BAD: sh -c entrypoint
  │ Sets shutdown flag                │ Shell doesn't forward
  │ Finishes in-flight requests       │ SIGTERM to child
  │ Closes DB connections             │ App never gets SIGTERM
  │ Exits cleanly                     │ Shell waits...
  └────┬──────────────────────────────┘     │
       │                                     ▼
       ▼                           terminationGracePeriod
 Pod terminates cleanly            (default: 30s) expires
 Exit code 0                            │
                                        ▼
                              Kubernetes sends SIGKILL
                              Force terminates container
                              Exit code 137 (128+9)
```

---

### 💻 Code Example

**Example — Implement tini-like signal forwarding for Docker:**
```dockerfile
# BAD: Shell as PID 1 doesn't forward signals
FROM ubuntu
CMD ["/bin/sh", "-c", "python app.py"]
# PID 1: /bin/sh
# PID 2: python app.py
# SIGTERM → /bin/sh → NOT forwarded to python
# docker stop timeout → SIGKILL → ungraceful

# GOOD option 1: Exec form (app is PID 1)
FROM ubuntu
CMD ["python", "app.py"]
# PID 1: python app.py
# SIGTERM → python directly → graceful shutdown

# GOOD option 2: tini as PID 1 (handles signal forwarding
# AND zombie reaping)
FROM ubuntu
RUN apt-get update && apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "app.py"]
# PID 1: tini (signal forwarder + zombie reaper)
# PID 2: python app.py
# SIGTERM → tini → python → graceful shutdown
```

---

### ⚖️ Comparison Table

| Signal | Number | Catchable | Purpose | Use When |
|---|---|---|---|---|
| SIGTERM | 15 | Yes | Request graceful stop | Always try first |
| SIGKILL | 9 | **No** | Force immediate stop | SIGTERM ignored/hung |
| SIGHUP | 1 | Yes | Reload config (by convention) | Config reload without restart |
| SIGINT | 2 | Yes | Interrupt (Ctrl+C) | Interactive terminal stop |
| SIGQUIT | 3 | Yes | Quit + core dump | Debugging (get stack trace) |
| SIGUSR1/2 | 10/12 | Yes | Application-defined | App-specific triggers |
| SIGCHLD | 17 | Yes | Child state changed | Parent waiting for children |
| SIGSTOP | 19 | **No** | Pause execution | Debugging, job control |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `kill` sends SIGKILL | `kill PID` with no signal sends SIGTERM (15); SIGKILL requires `kill -9` or `kill -SIGKILL` |
| SIGTERM always terminates the process | SIGTERM can be caught and ignored; a process with a broken SIGTERM handler will not exit |
| SIGHUP reloads config in all programs | SIGHUP only reloads config in programs that explicitly handle it; many programs have SIGHUP as default terminate |
| Shell scripts automatically handle SIGTERM | A shell script without `trap` exits on SIGTERM, but any running command (e.g., `sleep 100`) is not interrupted — the SIGTERM to the shell doesn't reach the child command |
| PID 1 in a container should be a shell script | Shell scripts as PID 1 don't forward signals to child processes; use exec form or tini |

---

### 🚨 Failure Modes & Diagnosis

**`docker stop` Takes 30 Seconds (Always Times Out)**

**Symptom:**
Every `docker stop` takes exactly 30 seconds. Container is then killed with SIGKILL. Exit code 137.

**Root Cause:**
Container's PID 1 is not receiving or handling SIGTERM. Usually: CMD uses shell form (`/bin/sh -c python app.py`), so SIGTERM goes to the shell, not the Python process. Shell exits but Python keeps running. Docker waits 30s (terminationGracePeriodSeconds) then sends SIGKILL.

**Diagnostic Commands:**
```bash
# Check PID 1 inside the container
docker exec mycontainer cat /proc/1/cmdline | tr '\0' ' '
# If it shows: /bin/sh -c python app.py
# → PROBLEM: shell is PID 1, not the app

# Check signal disposition of PID 1
docker exec mycontainer cat /proc/1/status | grep Sig

# Test SIGTERM handling
docker kill --signal=SIGTERM mycontainer
# If container keeps running for >5s: SIGTERM not handled
```

**Fix:**
Use Docker exec form: `CMD ["python", "app.py"]` or add `ENTRYPOINT ["/usr/bin/tini", "--"]`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Process Management` — signals operate on processes; understanding PIDs, parent/child relationships, and `fork()`/`exec()` is foundational

**Builds On This (learn these next):**
- `Zombie Processes` — SIGCHLD and the relationship between signal handling and zombie process creation
- `Containers` — signal handling in Docker/Kubernetes is a critical operational concern; PID 1 signal forwarding is a common source of ungraceful shutdowns

**Alternatives / Comparisons:**
- `/proc/PID/` — signals are one way to communicate with processes; `/proc` provides another (read-only) interface to process state
- `Named pipes / sockets` — application-defined IPC mechanisms for more complex communication than signals support

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Asynchronous kernel notifications to      │
│              │ processes: request or force state change  │
├──────────────┼───────────────────────────────────────────┤
│ KEY SIGNALS  │ SIGTERM (15): ask to stop — catchable     │
│              │ SIGKILL (9): force stop — uncatchable     │
│              │ SIGHUP (1): reload config — catchable     │
│              │ SIGINT (2): Ctrl+C — catchable            │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ Always try SIGTERM first; wait; then      │
│              │ SIGKILL only if SIGTERM fails             │
├──────────────┼───────────────────────────────────────────┤
│ CONTAINER    │ Use exec form CMD ["app"] so app is       │
│ RULE         │ PID 1 and receives SIGTERM directly       │
├──────────────┼───────────────────────────────────────────┤
│ SHELL TRAP   │ trap 'cleanup' SIGTERM SIGINT             │
│              │ Always add to scripts that create files   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SIGTERM: please leave; SIGKILL: you're   │
│              │ being physically removed"                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Zombie processes → tini → job control     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A multi-threaded Java application in a container receives SIGTERM from Kubernetes. The JVM registers a shutdown hook with `Runtime.getRuntime().addShutdownHook(new Thread(...))`. Trace the exact sequence of events: how does the JVM's SIGTERM handler work, which thread runs the shutdown hook, how does the JVM handle SIGTERM vs SIGKILL, and what happens if the shutdown hook itself blocks indefinitely — including Kubernetes's response after `terminationGracePeriodSeconds` expires.

**Q2.** You're writing a shell script that starts three background processes, waits for all of them, and must clean up all three when it receives SIGTERM (e.g., from `docker stop`). Write the complete script with proper trap handling, explain the race condition that occurs if SIGTERM arrives while `wait` is executing, and show how to handle it correctly — explaining why `wait $pid1 $pid2 $pid3` and `wait` (no args) behave differently in this context.
