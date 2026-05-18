---
id: OSY-036
title: Signals and Signal Handlers
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-006, OSY-019
used_by: OSY-035, OSY-041
related: OSY-035, OSY-041, OSY-072
tags:
  - signals
  - signal-handlers
  - unix
  - process-control
  - SIGTERM
  - SIGKILL
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/osy/signals-signal-handlers/
---

## TL;DR

Signals are async notifications sent to a process.
SIGTERM (15) = graceful stop request (catchable). SIGKILL
(9) = immediate kill (uncatchable). SIGINT (2) = Ctrl+C.
Java apps register shutdown hooks for SIGTERM. Kubernetes
sends SIGTERM before SIGKILL (graceful shutdown window).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-036 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | signals, SIGTERM, SIGKILL, signal handlers, shutdown hooks |
| **Prerequisites** | OSY-006, OSY-019 |

---

### Common Signals Reference

```
Signal    Number  Default Action  Can Catch?  Use Case
SIGHUP    1       Terminate       Yes         Terminal hangup, config reload
SIGINT    2       Terminate       Yes         Ctrl+C (keyboard interrupt)
SIGQUIT   3       Core dump       Yes         Ctrl+\ (thread dump in JVM)
SIGFPE    8       Core dump       Yes         Floating point exception
SIGKILL   9       Terminate       NO          Force kill (uncatchable!)
SIGSEGV   11      Core dump       Yes*        Segmentation fault (null ptr)
SIGPIPE   13      Terminate       Yes         Write to closed pipe
SIGTERM   15      Terminate       Yes         Graceful shutdown request
SIGUSR1   10      Terminate       Yes         User-defined signal
SIGUSR2   12      Terminate       Yes         User-defined signal
SIGCHLD   17      Ignore          Yes         Child process stopped/exited
SIGSTOP   19      Stop            NO          Pause process (uncatchable!)
SIGCONT   18      Continue        Yes         Resume paused process

* SIGSEGV can be caught but recovery is difficult
  SIGKILL and SIGSTOP are NEVER catchable by design
```

---

### Sending Signals

```bash
# Send to process by PID
kill -SIGTERM 12345    # or: kill -15 12345 or: kill 12345
kill -SIGKILL 12345    # or: kill -9 12345
kill -SIGSTOP 12345    # pause process
kill -SIGCONT 12345    # resume process

# Send to all processes named "java"
pkill -SIGTERM java    # graceful stop
pkill -9 java         # force kill

# Send SIGQUIT to JVM = trigger thread dump to stderr
kill -3 $(pgrep java)

# Broadcast to process group
kill -SIGTERM -12345   # negative PID = process group

# Docker / Kubernetes:
# docker stop container  -> sends SIGTERM, waits 10s, then SIGKILL
# kubectl delete pod     -> sends SIGTERM (terminationGracePeriodSeconds)
```

---

### Java Signal Handling

```java
// Shutdown hook: runs on SIGTERM or normal JVM exit
public class GracefulServer {
    private static volatile boolean running = true;
    private static final Server server = new Server();
    
    public static void main(String[] args) throws Exception {
        // Register shutdown hook (called on SIGTERM, SIGINT)
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("SIGTERM received, shutting down...");
            running = false;
            server.stop(5, TimeUnit.SECONDS); // graceful drain
            System.out.println("Shutdown complete");
        }));
        
        server.start();
        System.out.println("Server started. PID: " +
            ProcessHandle.current().pid());
        
        // Block main thread
        while (running) {
            Thread.sleep(1000);
        }
    }
}
// Important: shutdown hook has a time limit!
// If it doesn't complete within ~15s, JVM may be force-killed
// Keep shutdown hook fast (< 5s): stop accepting, drain, close

// SIGKILL cannot be caught - JVM is killed immediately
// Potential issues: in-progress writes not flushed,
//   database transactions not committed, open files not synced
```

---

### Signal Handling in Process Lifecycle

```
Docker/Kubernetes graceful shutdown sequence:

1. kubectl delete pod (or HPA scale-down)
2. Kubernetes sends SIGTERM to PID 1 in container
3. Application shutdown hook runs:
   - Stop accepting new requests
   - Wait for in-progress requests to complete
   - Flush buffers, close connections
4. terminationGracePeriodSeconds elapses (default 30s)
5. If still running: Kubernetes sends SIGKILL -> immediate death

Common mistake: Java app is NOT PID 1, PID 1 is bash/sh
  bash may not forward SIGTERM to child processes!
  
Solution: Use exec form in Dockerfile (not shell form):
  WRONG: CMD ["sh", "-c", "java -jar app.jar"]
  # bash is PID 1, java is PID 2; SIGTERM goes to bash only

  RIGHT: CMD ["java", "-jar", "app.jar"]
  # java IS PID 1; SIGTERM received directly
  
  Or: use tini as PID 1 (ENTRYPOINT ["/sbin/tini", "--"])
  tini forwards signals to child and reaps zombie processes
```

---

### Signal Safety (async-signal safety)

```
WARNING: Signal handlers run asynchronously, interrupting
  any point in program execution.

Functions that are ASYNC-SIGNAL-SAFE (safe in handlers):
  write(), read(), getpid(), signal(), _exit()
  
Functions that are NOT async-signal-safe:
  printf(), malloc(), free(), any C++ exception handling
  Any Java code (JVM is not signal-safe internally)
  
Java note:
  Java shutdown hooks run in a new Thread, NOT as a
  classic signal handler. They are safe to use Java APIs.
  The JVM converts SIGTERM -> Runtime.halt() path ->
  calls shutdown hooks in Java thread context.
  
  DO NOT use Runtime.getRuntime().addShutdownHook()
  for extremely time-sensitive or async-signal-safe
  requirements. Use SIGTERM -> graceful drain pattern.
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "kill -9 is the safest way to stop a process" | SIGKILL (-9) is the most dangerous stop: no cleanup, no buffer flush, no graceful shutdown. It should be a last resort. Always try SIGTERM first and give the process time to clean up |
| "JVM shutdown hooks run for SIGKILL" | Shutdown hooks run on SIGTERM and System.exit(), but NOT on SIGKILL. SIGKILL is instant - the process is terminated immediately with no cleanup code running |

---

### Quick Reference Card

| Signal | Number | Catchable | When To Use |
|--------|--------|-----------|------------|
| SIGTERM | 15 | Yes | Standard graceful stop |
| SIGKILL | 9 | NO | Force kill (last resort) |
| SIGINT | 2 | Yes | Ctrl+C interactive stop |
| SIGQUIT | 3 | Yes | Thread dump (JVM: kill -3) |
| SIGHUP | 1 | Yes | Config reload (NGINX, etc.) |
| SIGSTOP | 19 | NO | Pause (debugging) |
| SIGCONT | 18 | Yes | Resume after SIGSTOP |
