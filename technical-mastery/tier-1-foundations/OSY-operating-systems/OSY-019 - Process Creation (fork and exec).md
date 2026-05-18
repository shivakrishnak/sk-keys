---
id: OSY-019
title: Process Creation (fork and exec)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006, OSY-057
used_by: OSY-041
related: OSY-006, OSY-057, OSY-072
tags:
  - foundational
  - fork
  - exec
  - process-creation
  - unix
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/osy/fork-exec/
---

## TL;DR

Unix process creation uses fork() to clone the calling
process (copy-on-write), then exec() to replace the
clone with a new program. The two-step model enables
powerful shell pipelines and pre-exec configuration.
Java uses ProcessBuilder which internally calls fork+exec.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-019 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | fork, exec, process creation, COW |
| **Prerequisites** | OSY-006, OSY-057 |

---

### The fork + exec Pattern

```
Why not a single "create process from file" call?
The two-step model provides power:

BETWEEN fork() and exec(), the child can:
  - Redirect stdin/stdout/stderr (for shell pipes: cmd1 | cmd2)
  - Set environment variables
  - Change working directory
  - Set resource limits (ulimit)
  - Drop privileges (setuid)
  - Close file descriptors
  All BEFORE the new program starts.

Single-step would require passing all of this as parameters.
The fork+exec model keeps the design simple and composable.
```

---

### fork() Details

```
pid_t pid = fork();
// After fork(): TWO processes running the same code
// Both processes return from fork(), but:
//   In parent: pid = child's PID (e.g., 42382)
//   In child:  pid = 0

if (pid == 0) {
    // CHILD PROCESS
    // Memory: Copy-on-Write (shares parent's pages)
    //   Physical pages shared until either writes
    //   First write: OS copies the written page
    // Open file descriptors: INHERITED (shared reference)
    // Signal handlers: INHERITED
    // Environment: INHERITED
    execlp("ls", "ls", "-la", NULL); // replace with ls
    // exec SHOULD NOT RETURN
    // if it does: exec failed
    perror("exec failed"); exit(1);
} else {
    // PARENT PROCESS
    int status;
    waitpid(pid, &status, 0); // collect exit status
    // Without waitpid: child becomes zombie
}
```

---

### Java ProcessBuilder Internals

```java
// Java ProcessBuilder -> fork + exec internally
ProcessBuilder pb = new ProcessBuilder("ls", "-la", "/tmp");
pb.directory(new File("/home/user"));
pb.environment().put("MY_VAR", "value");
pb.redirectOutput(ProcessBuilder.Redirect.PIPE);

Process process = pb.start(); // internally: fork() + exec()

// Consume stdout (MUST do this or pipe buffer fills -> deadlock)
String output = new String(process.getInputStream()
    .readAllBytes());
    
int exitCode = process.waitFor(); // internally: waitpid()

// DANGER: not reading stdout before waitFor() -> deadlock
// Process writes to pipe, pipe buffer fills (64KB typical)
// Process blocks waiting for reader
// Parent waits for process to exit
// DEADLOCK: both waiting for each other
```

---

### Textbook Definition

`fork()` creates a new process as an exact copy (clone)
of the calling process, using copy-on-write for memory
efficiency. The child gets a new PID but initially shares
the parent's memory pages. `exec()` replaces the current
process's address space with a new program loaded from
disk, preserving the PID but replacing code, data, and
stack.

---

### Understand It in 30 Seconds

fork() = photocopy the employee badge (create a clone).
exec() = paste a new photo on the badge (new program in
the clone's slot). Between copy and paste: the clone
can change their uniform (redirects, env vars, ulimits).

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "fork() is expensive because it copies all memory" | fork() uses copy-on-write: only the page table is copied, not the physical pages. Physical pages are shared until written. A fork() of a 4GB JVM takes ~1ms (page table copy) not seconds |
| "Java ProcessBuilder.start() is a single OS call" | It calls posix_spawn() or fork()+exec() depending on JVM version and platform. On Linux, fork()+exec() is typical. The JVM thread safety issue means forking a multi-threaded JVM has risks (only the calling thread is forked) |

---

### Mastery Checklist

- [ ] Knows fork() returns twice (child: 0, parent: child PID)
- [ ] Understands fork+exec two-step model and why it's powerful
- [ ] Knows ProcessBuilder internally uses fork+exec
- [ ] Can explain the deadlock risk in ProcessBuilder (unread stdout)
