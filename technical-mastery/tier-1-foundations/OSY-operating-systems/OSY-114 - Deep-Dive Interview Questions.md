---
id: OSY-114
title: Deep-Dive Interview Questions
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-112, OSY-113
used_by: []
related: OSY-112, OSY-115, OSY-128
tags:
  - interview
  - deep-dive
  - OS-internals
  - expert
  - production
  - questions
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 114
permalink: /technical-mastery/osy/deep-dive-interview-questions/
---

## TL;DR

Curated expert-level OS internals interview questions asked
at senior/staff engineering interviews at tech companies.
For each question: what they're really testing, strong answer
components, and common mistakes to avoid. Covers: scheduling,
memory management, concurrency, I/O, containers, and
JVM-specific OS interaction.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-114 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | interview questions, OS internals, expert, senior engineer |
| **Prerequisites** | OSY-112, OSY-113 |

---

### Category: Process and Thread Internals

```
Q: "Explain what happens when you call fork() in a
    process that has multiple threads."
    
What they're testing:
  - fork() + threads interaction (a known footgun)
  - POSIX fork() behavior in multithreaded process
  
Strong answer:
  POSIX: fork() in a multithreaded process creates a child
  with only ONE thread: the calling thread. Other threads
  are NOT cloned into the child.
  
  The problem: mutexes held by those non-copied threads
  remain locked in the child. The child cannot acquire them.
  -> Deadlock if child calls any function that uses those mutexes
  -> malloc uses an internal mutex: calling malloc after fork
     in the child can deadlock!
  
  Safe pattern: fork + exec immediately (fork is just
  to create a process; exec replaces the address space
  before doing anything else).
  
  atfork handlers: pthread_atfork() to prepare/reinitialize
  state in the child after fork.
  
Common mistakes:
  "fork copies all threads" - WRONG (POSIX, one thread only)
  Missing the mutex deadlock problem entirely

---

Q: "What is the difference between a context switch
    and a mode switch? When does each happen?"
    
What they're testing:
  - Precision on OS terminology
  - Understanding of privilege levels and when overhead occurs
  
Strong answer:
  Mode switch (privilege switch):
    User mode <-> Kernel mode transition
    Triggered by: system call, hardware interrupt, exception
    Cost: save/restore registers + CPU ring change
    ~100-300 cycles (fast)
    
  Context switch (full process/thread switch):
    Running one process -> running another process
    Triggered by: scheduler preemption, voluntary sleep/block
    Cost: save process state (registers + kernel stack pointer),
    load new process state, TLB flush (if address space change),
    pipeline stall, cache invalidation
    ~1,000-10,000 cycles (much more expensive)
    
  Key insight: every context switch involves mode switches,
  but not every mode switch causes a context switch.
  A fast syscall (getpid via VSYSCALL) may not even do
  a full mode switch.
  
Common mistakes:
  Treating them as synonyms
  Not knowing VSYSCALL optimization
```

---

### Category: Memory Management

```
Q: "A Java application uses -Xmx4g but RSS grows to 12GB.
    Explain what is happening."
    
What they're testing:
  - Understanding that JVM memory != heap
  - Knowledge of all JVM memory regions
  - Production diagnosis ability
  
Strong answer components:
  -Xmx4g only limits Java heap (GC-managed memory)
  
  Other JVM memory regions (all contribute to RSS):
    Metaspace: class metadata, JIT-compiled code
      Default: unlimited (can grow to fill memory!)
      Config: -XX:MaxMetaspaceSize=256m
      
    Thread stacks: each OS thread * -Xss (default 512KB-1MB)
      200 threads * 1MB = 200MB native memory
      
    Direct ByteBuffer / off-heap (NIO, Netty)
      -XX:MaxDirectMemorySize (default = -Xmx)
      Netty: 4GB direct buffer pool is common
      
    JIT compiled code cache: CodeCache
      Default: 256MB-512MB
      
    GC metadata: card tables, remembered sets
    
  Diagnosis:
    jcmd $PID VM.native_memory detail
    Look for large NMT sections
    
  Common culprit for 12GB RSS with 4GB heap:
    Off-heap Netty buffers OR unbounded Metaspace
    
Common mistakes:
  "Must be a memory leak in the heap" (may be native)
  Not mentioning NMT as diagnostic tool

---

Q: "Explain transparent huge pages and why disabling them
    is a common performance recommendation for databases."
    
What they're testing:
  - Production tuning knowledge
  - Trade-off understanding for different workloads
  
Strong answer:
  THP (Transparent Huge Pages):
    OS automatically uses 2MB pages instead of 4KB
    Benefit: 512x fewer TLB entries needed for same range
    -> Huge reduction in TLB miss rate for large sequential access
    
  Problem for databases:
    THP collapses pages in the background (khugepaged thread)
    During collapse: CPU must zero the page (expensive for 2MB)
    Collapse is asynchronous and unpredictable
    -> Periodic latency spikes (50-200ms) at random intervals
    
  MongoDB, Redis, Cassandra, MySQL: all recommend:
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
    
  Better alternative for Java apps with large heaps:
    Explicit huge pages (HugeTLB):
    JVM flag: -XX:+UseHugeTLBFS
    Pre-allocate huge pages: vm.nr_hugepages = N
    No background collapsing; predictable latency
    
Common mistakes:
  "Just always disable THP" without explaining why
  Not knowing the khugepaged collapse mechanism
```

---

### Category: I/O and File Systems

```
Q: "What is the difference between fsync() and fdatasync()?
    When would you use each?"
    
What they're testing:
  - Storage durability knowledge
  - Trade-off reasoning
  
Strong answer:
  fsync(fd):
    Flushes data AND metadata (file size, modification time,
    inode changes) to persistent storage
    Required by: SQLite, fsck-safe code
    
  fdatasync(fd):
    Flushes data AND only metadata required for retrieval
    (size if it changed). Not modification time, access time.
    Faster than fsync() because fewer metadata writes
    
  When to use each:
    fdatasync: append-only log files (size matters, mtime doesn't)
    fsync: critical transactions where full metadata consistency needed
    
  Both: guarantee data reaches disk, survive power failure
  Neither: faster than not syncing; always has performance cost
  
  Java: FileChannel.force(boolean metaData)
    metaData=true: fsync semantics
    metaData=false: fdatasync semantics
    
  Write-Ahead Log (WAL) pattern: uses fdatasync for speed

---

Q: "Explain what happens at the OS level when you do
    BufferedWriter.flush() in Java."
    
What they're testing:
  - Understanding of I/O buffering layers
  - System call knowledge
  
Strong answer:
  Multiple buffer layers:
    1. Java application buffer (BufferedWriter: 8KB)
    2. JVM/C library stdio buffer (usually none for Java NIO)
    3. Page cache in kernel (volatile memory)
    4. Disk device write buffer (volatile)
    5. Persistent storage (NVM/flash/HDD)
    
  BufferedWriter.flush():
    Calls write() system call with the buffered data
    Data moves: Java buffer -> page cache (kernel)
    NOT to disk! Just to kernel memory
    CPU: mode switch to kernel, copy pages, return
    
  To reach disk: need to call channel.force() or fsync()
    FileChannel.force(false): fdatasync
    FileChannel.force(true): fsync
    
  Why this matters:
    Process crash: data in page cache survives (kernel has it)
    Machine crash (kernel dies): page cache lost
    Only fsync() guarantees disk persistence
    
Common mistakes:
  "flush() writes to disk" - WRONG, just to kernel page cache
```

---

### Category: Containers and Security

```
Q: "Explain how containers achieve isolation without
    being virtual machines."
    
What they're testing:
  - Deep understanding of namespace and cgroups
  - Container security boundary knowledge
  
Strong answer:
  Isolation mechanisms (NOT virtualization):
    
    Namespaces: what a process can SEE
      pid: own PID number space (PID 1 = init inside container)
      net: own network interfaces, routing table
      mnt: own filesystem mount points
      uts: own hostname
      ipc: own shared memory, message queues
      user: own UID mapping (container root != host root)
      cgroup: own view of resource usage
      
    cgroups: what resources a process can USE
      memory: max RAM, OOM behavior
      cpu: shares, quota, period
      blkio: disk I/O rate limits
      pids: max process count
      
    Kernel sharing:
      All containers on host share the SAME kernel
      -> Kernel exploit = escapes ALL containers
      -> Container isolation < VM isolation
      -> Containers same-kernel attack surface
      
  Additional hardening:
    seccomp: restrict which syscalls container can make
    AppArmor/SELinux: mandatory access control
    Capabilities: drop capabilities container doesn't need
    
  Key implication: if you need true isolation (multi-tenant,
  untrusted code), use VMs + containers (not just containers).
  
Common mistakes:
  "Containers are isolated like VMs" - weaker isolation
  Not mentioning kernel sharing as the key vulnerability
```

---

### Category: JVM-OS Interaction

```
Q: "Why might a Java 21 application with virtual threads
    still experience OS thread blocking, and how would
    you diagnose it?"
    
What they're testing:
  - Virtual thread pinning knowledge
  - Java 21 mental model accuracy
  
Strong answer:
  Virtual thread pinning - when a virtual thread is pinned
  to its carrier OS thread and CANNOT be unmounted:
    
    1. synchronized blocks/methods:
       synchronized(lock) {
           // virtual thread: pinned to OS thread here
           Thread.sleep(1000);  // can't unmount -> OS thread blocked!
       }
       Fix: replace with ReentrantLock (unmountable)
       
    2. Native code (JNI):
       A virtual thread calling native code via JNI
       is pinned for the duration of the native call
       
  Diagnosis:
    # JVM flag to log pinning events:
    -Djdk.tracePinnedThreads=full
    
    # Thread dump will show:
    VirtualThread pinned at:
      com.example.Service.method(Service.java:42)
      - locked <0x...> (java.util.HashMap)
    
    # JFR event: jdk.VirtualThreadPinned
    jcmd $PID JFR.start filename=/tmp/vt.jfr duration=60s
    
  After diagnosis:
    Replace synchronized with ReentrantLock
    Monitor: count of VirtualThreadPinned events should drop
    
  Counter-intuitive: with virtual threads, synchronized is
  WORSE than before because it blocks the carrier OS thread,
  reducing the thread multiplexing benefit.
```

---

### Red Flags in Candidate Answers

| Topic | Red Flag | What It Signals |
|-------|---------|-----------------|
| Context switch | "Context switch = mode switch" | Incomplete OS model |
| fork() + threads | "fork copies all threads" | Hasn't read POSIX |
| JVM memory | "RSS = heap size" | No production experience |
| Containers | "Containers are as secure as VMs" | Shallow container knowledge |
| Virtual threads | "No more thread blocking with Java 21" | Missed pinning concept |
| THP | "Always disable THP" without knowing why | Cargo-cult advice |
