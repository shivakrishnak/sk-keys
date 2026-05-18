---
id: OSY-080
title: POSIX Standard
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-004, OSY-034, OSY-035
used_by: []
related: OSY-004, OSY-035, OSY-131
tags:
  - POSIX
  - portability
  - IEEE-1003
  - Unix
  - standards
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/osy/posix-standard/
---

## TL;DR

POSIX (Portable Operating System Interface) is the IEEE
standard (1003.1) defining OS interfaces for Unix
compatibility. Defines: file I/O (open/read/write/close),
processes (fork/exec/wait), threads (pthreads), signals,
and more. Java's JVM abstracts POSIX, but understanding
POSIX explains Java's I/O, process, and thread models.
Linux is POSIX-compliant; Windows is not.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-080 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | POSIX, pthreads, portability, IEEE-1003, Unix |
| **Prerequisites** | OSY-004, OSY-034, OSY-035 |

---

### POSIX Overview

```
POSIX (Portable Operating System Interface):
  IEEE 1003.1: family of standards for Unix-like OS compatibility
  Goal: "write once, run anywhere" across Unix systems
  Covers: system calls, library functions, shell, utilities
  
POSIX compliance levels:
  Strictly POSIX conformant: passes all tests
  POSIX compliant: implements all required interfaces
  POSIX compatible: mostly compliant with some extensions
  
  Linux: "mostly POSIX compliant" (extensions beyond POSIX)
  macOS: certified POSIX compliant (2007)
  Windows: NOT POSIX compliant (Win32 API is different)
    Windows Subsystem for Linux (WSL): Linux POSIX environment
    Cygwin: POSIX emulation layer on Windows
    
POSIX core specifications (1003.1):
  File I/O: open(), close(), read(), write(), lseek(), fcntl()
  Processes: fork(), exec*(), wait(), getpid(), getppid()
  Signals: signal(), sigaction(), kill(), sigprocmask()
  Threads: pthread_create(), mutex, condition variables
  Memory: mmap(), mprotect(), mlock()
  Time: clock_gettime(), nanosleep()
  Networking: sockets (though originally in BSD, now POSIX)
```

---

### POSIX Threads (pthreads)

```c
// POSIX thread API (used by Java pthreads underneath):
#include <pthread.h>

// Create thread:
pthread_t tid;
pthread_create(&tid, NULL, worker_func, arg);
pthread_join(tid, NULL);  // wait for thread

// POSIX mutex:
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_lock(&mutex);
// critical section
pthread_mutex_unlock(&mutex);

// POSIX condition variable:
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
pthread_mutex_lock(&mutex);
while (!condition_met)
    pthread_cond_wait(&cond, &mutex);  // atomically release + wait
pthread_mutex_unlock(&mutex);
// Signal:
pthread_cond_signal(&cond);    // wake one
pthread_cond_broadcast(&cond); // wake all

// Read-write lock (readers can share, writers exclusive):
pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;
pthread_rwlock_rdlock(&rwlock);  // multiple readers OK simultaneously
pthread_rwlock_wrlock(&rwlock);  // exclusive write
pthread_rwlock_unlock(&rwlock);

// Java mapping:
// java.lang.Thread -> pthread_create() on Linux
// synchronized/ReentrantLock -> pthread_mutex (futex-based)
// Condition.await() -> pthread_cond_wait()
// ReadWriteLock -> pthread_rwlock
```

---

### POSIX File I/O vs Java I/O

```
POSIX file I/O -> Java abstraction mapping:
  
  open(path, flags) -> int fd
    Java: new FileInputStream(path)
    Java: FileChannel.open(path, options)
    
  read(fd, buf, count) -> bytes_read
    Java: InputStream.read(byte[])
    Java: FileChannel.read(ByteBuffer)
    
  write(fd, buf, count) -> bytes_written
    Java: OutputStream.write(byte[])
    Java: FileChannel.write(ByteBuffer)
    
  close(fd)
    Java: stream.close() or try-with-resources
    
  pread(fd, buf, count, offset) -> bytes_read (positioned read)
    Java: FileChannel.read(ByteBuffer, position)
    
  pwrite(fd, buf, count, offset) -> bytes_written
    Java: FileChannel.write(ByteBuffer, position)
    
  mmap(addr, len, prot, flags, fd, offset) -> addr
    Java: FileChannel.map() -> MappedByteBuffer
    
  fsync(fd) -> 0 on success
    Java: FileChannel.force(true)  // fsync() (metadata too)
    Java: FileChannel.force(false) // fdatasync() (data only)
    
POSIX flags for open():
  O_RDONLY, O_WRONLY, O_RDWR     read/write mode
  O_CREAT                        create if not exists
  O_EXCL                         fail if exists (atomic create)
  O_TRUNC                        truncate to zero on open
  O_APPEND                       writes always go to end (atomic)
  O_NONBLOCK                     non-blocking I/O
  O_DIRECT                       bypass page cache (database use)
  O_SYNC                         every write = fsync() (slow)
```

---

### POSIX Standards That Matter for Java Developers

```
POSIX signals: Java runtime relies on these
  SIGINT  (2):  Ctrl+C -> JVM catches, triggers shutdown hooks
  SIGTERM (15): kill PID -> JVM catches, triggers shutdown hooks
  SIGKILL (9):  cannot be caught -> immediate termination
  SIGSEGV (11): memory violation -> JVM crash dump (JVM bug)
  SIGQUIT (3):  kill -3 PID -> JVM prints thread dump to stdout
  SIGHUP  (1):  terminal closed; Java ignores by default
  SIGUSR1/SIGUSR2: user-defined; JVM may use internally
  
  Java shutdown hooks (SIGTERM handling):
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
        // Called on: System.exit(), SIGTERM, SIGINT
        // NOT called on: SIGKILL, JVM crash
    }));
    
POSIX process groups and sessions:
  Relevant for: process trees, job control
  When user runs a Java app from terminal:
    Shell creates a new process group
    Java process + any children: same process group
    Ctrl+C: sends SIGINT to the entire process group
    -> All processes in group receive SIGINT simultaneously
    
  Daemon processes:
    Detach from controlling terminal (setsid())
    Create new session: no terminal signals
    Background services start this way (systemd uses this)
    
File path and directory:
  getcwd() -> Java: System.getProperty("user.dir")
  chdir()  -> Java: no direct API (use ProcessBuilder.directory())
  POSIX defines: max filename length = 255 chars
  POSIX defines: max path length = PATH_MAX (4096 on Linux)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java is always portable so POSIX doesn't matter" | Java abstracts POSIX but the abstractions leak. File path separators differ (/ vs \), line endings differ (\n vs \r\n), signal handling differs (Windows has no SIGTERM), symbolic links behave differently. Java developers who understand POSIX write better cross-platform code and debug OS-specific issues faster |
| "POSIX threads and Java threads are the same concept" | Java threads map to POSIX threads on Linux (NPTL), but Java adds: JVM thread scheduling semantics, Java memory model (happens-before), garbage collector interaction, and Java-specific synchronization primitives (synchronized, volatile). Java threads are higher-level abstractions that happen to be implemented with pthreads |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| POSIX standard | IEEE 1003.1; portable Unix interfaces |
| Linux POSIX | Mostly compliant + Linux-specific extensions |
| Windows POSIX | Not compliant; WSL provides Linux POSIX environment |
| pthreads | POSIX thread API; Java uses it under the hood on Linux |
| SIGTERM (15) | Graceful shutdown; Java shutdown hooks fire |
| SIGKILL (9) | Cannot be caught; no Java hook; immediate kill |
| O_DIRECT | Bypass page cache; used by databases for WAL writes |
