---
id: OSY-113
title: Phase 4 Hands-On Lab
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-099, OSY-100, OSY-109, OSY-112
used_by: []
related: OSY-112, OSY-114, OSY-115
tags:
  - lab
  - hands-on
  - diagnosis
  - performance
  - production
  - exercise
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 113
permalink: /technical-mastery/osy/phase-4-lab/
---

## TL;DR

A series of hands-on lab exercises for OS internals at
expert level. Each scenario replicates a real production
problem: you diagnose it using OS tools, identify the
root cause, and apply the fix. Labs cover: memory leak
diagnosis, context switch storm, iowait bottleneck,
container escape detection, and JVM thread contention.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-113 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | lab exercises, hands-on, OS diagnosis, performance, production scenarios |
| **Prerequisites** | OSY-099, OSY-100, OSY-109, OSY-112 |

---

### Lab 1: Memory Growth Investigation

```
Scenario:
  A Java service has been running for 12 hours.
  RSS has grown from 800MB to 2.4GB.
  -Xmx is 1GB. No OOM error thrown. Load is constant.

Your task:
  1. Confirm whether this is JVM heap or native memory
  2. Identify the region that is growing
  3. Determine the source (which code path)

Tools to use:
  jcmd $PID GC.heap_info
  jcmd $PID VM.native_memory detail
  jstat -gc $PID 1000 60

What to look for:
  - If heap is at 1GB and not growing: heap is NOT the issue
  - If NMT Thread section is growing: unbounded thread creation
  - If NMT Class section is growing: class loader leak
  - If NMT Internal or Other is large: direct buffer leak
  
Expected finding in this scenario:
  NMT Thread (reserved=4096MB, committed=2048MB +1200MB)
  Root cause: CachedThreadPool with long-running tasks
  holding threads alive for extended periods
  
Fix:
  Replace Executors.newCachedThreadPool() with
  ThreadPoolExecutor with max=N_CPU*2, keepAlive=30s
```

---

### Lab 2: Context Switch Storm

```
Scenario:
  8-core production machine.
  Load average: 12 (high).
  CPU utilization: 35% us, 5% sy, 0% wa.
  Response time: 800ms avg (expected: 50ms).
  vmstat shows: cs = 800,000 per second.

Your task:
  1. Confirm it's context switch overhead (not CPU work)
  2. Identify which process is causing it
  3. Identify WHY (too many threads? lock contention?)
  
Tools:
  pidstat -w 1  # per-process context switches
  ps -eo pid,nlwp,comm --sort=-nlwp | head
  # nlwp = number of threads per process
  
  jcmd $PID Thread.print | grep 'State:' | sort | uniq -c
  
What to look for:
  - Which PID has highest cswch/s in pidstat?
  - How many threads does that process have? (ps nlwp)
  - What state are those threads in? (thread dump)
  
Expected finding:
  Java process: 500 threads
  Thread dump: 450 threads in WAITING state (on HikariPool)
  Root cause: Tomcat maxThreads=500; DB pool=10
  450 threads blocking on DB connection acquisition
  Voluntary context switches: 450 per DB connection release
  
Fix:
  Reduce Tomcat maxThreads to 20
  Increase DB pool to match: maximumPoolSize=20
  Result: cs drops from 800K to 15K/sec
```

---

### Lab 3: I/O Wait in Production

```
Scenario:
  Service: batch job processing 1M files per day.
  Today: job running 8 hours (expected: 2 hours).
  top shows: 35% iowait across all CPUs.
  CPU: only 15% utilization.

Your task:
  1. Identify which process is doing I/O
  2. Identify which device is the bottleneck
  3. Determine if it's reads or writes, random or sequential
  4. Propose fix

Tools:
  iotop -o -b -n 10  # which process
  iostat -xz 1 10    # which device, utilization
  iostat: check r/s vs rMB/s ratio (random vs sequential)

What to look for:
  iotop: batch-job process doing 150MB/s reads
  iostat sda: %util=98%, await=8ms, rMB/s=150
  r/s=38,000 (38K IOPS at 4KB each = 150MB/s)
  
  38K IOPS: exceeds SATA SSD max (~100K)
  But sequential: it's near device max
  
  Deeper look: what is the read pattern?
    Java application: reading 1M small files (4KB each)
    Files: scattered across filesystem
    -> Random reads (no sequential pattern)
    
Expected finding:
  38K random 4KB reads per second on SATA SSD
  Device near saturation; page cache can't help:
  files are read once and evicted (batch, no reuse)
  
Fix options:
  1. Rewrite: pack many small files into fewer large files
     (reduce IOPS from 38K to 100, sequential pattern)
  2. Store: use NVMe (700K IOPS random)
  3. Parallelize + parallelize I/O:
     Multiple readers + use NIO non-blocking
  4. Pre-warm: read all files at startup into memory map
```

---

### Lab 4: Container Escape Detection

```
Scenario:
  An alert fires: a container is attempting to read
  /etc/shadow on the host filesystem.
  
Your task:
  1. Identify which container is making the access attempt
  2. Determine if the container has host mount
  3. Check if any capabilities were granted incorrectly
  4. Write the preventive seccomp policy

Tools:
  docker ps  # identify containers
  docker inspect $CONTAINER_ID | grep -A 5 '"Binds"'
  docker inspect $CONTAINER_ID | grep -i cap
  
  # Audit log for the access attempt:
  ausearch -m SYSCALL -k sensitive-file-access

What to look for:
  Unexpected volume mounts: "/:/host" (host root mounted)
  Capabilities: CAP_SYS_ADMIN or CAP_SYS_PTRACE granted
  Audit log: openat syscall with /etc/shadow path

Correct container configuration:
  docker run \
    --security-opt no-new-privileges \
    --cap-drop ALL \
    --read-only \
    --tmpfs /tmp \
    --security-opt seccomp=/etc/docker/seccomp/strict.json \
    my-app

Minimal seccomp policy (JSON):
  {
    "defaultAction": "SCMP_ACT_ERRNO",
    "syscalls": [
      {
        "names": ["read","write","open","close","stat",
                  "fstat","lstat","poll","lseek","mmap",
                  "mprotect","munmap","brk","rt_sigaction",
                  "rt_sigprocmask","ioctl","pread64",
                  "pwrite64","readv","writev","access",
                  "pipe","select","sched_yield","mremap",
                  "msync","mincore","madvise","shmget",
                  "shmat","shmctl","dup","dup2","pause",
                  "nanosleep","getitimer","alarm","clone",
                  "fork","execve","exit","wait4","kill",
                  "uname","fcntl","flock","fsync",
                  "getcwd","chdir","rename","mkdir",
                  "rmdir","unlink","symlink","readlink",
                  "chmod","fchmod","chown","fchown",
                  "gettimeofday","getrlimit","getrusage",
                  "sysinfo","times","ptrace","getuid",
                  "syslog","getgid","setuid","setgid",
                  "geteuid","getegid","setresuid",
                  "getresuid","setresgid","getresgid",
                  "getpgrp","getpid","getppid",
                  "getgroups","setsid","socket","connect",
                  "accept","sendto","recvfrom","sendmsg",
                  "recvmsg","shutdown","bind","listen",
                  "getsockname","getpeername","socketpair",
                  "setsockopt","getsockopt","exit_group",
                  "futex","set_thread_area","get_thread_area",
                  "epoll_create","epoll_ctl","epoll_wait",
                  "set_tid_address","restart_syscall",
                  "clock_gettime","clock_getres",
                  "clock_nanosleep","tgkill","openat",
                  "getdents64","newfstatat","readlinkat",
                  "faccessat","pselect6","ppoll",
                  "unshare","splice","tee","sync_file_range",
                  "vmsplice","utimensat","epoll_pwait",
                  "signalfd","timerfd_create","eventfd",
                  "fallocate","timerfd_settime",
                  "timerfd_gettime","accept4","signalfd4",
                  "eventfd2","epoll_create1","dup3",
                  "pipe2","inotify_init1","preadv",
                  "pwritev","rt_tgsigqueueinfo",
                  "perf_event_open","recvmmsg",
                  "fanotify_init","fanotify_mark",
                  "prlimit64","name_to_handle_at",
                  "open_by_handle_at","clock_adjtime",
                  "syncfs","sendmmsg","setns","getcpu",
                  "process_vm_readv","process_vm_writev",
                  "kcmp","finit_module","sched_getattr",
                  "sched_setattr","getrandom","memfd_create",
                  "kexec_file_load","bpf","execveat",
                  "userfaultfd","membarrier","mlock2",
                  "copy_file_range","preadv2","pwritev2",
                  "io_uring_setup","io_uring_enter",
                  "io_uring_register","pidfd_send_signal",
                  "io_uring_setup"],
        "action": "SCMP_ACT_ALLOW"
      }
    ]
  }
```

---

### Lab 5: JVM Thread Contention

```
Scenario:
  Java REST service: 20K req/s
  Thread pool: 32 threads
  CPU: 8 cores at 90% utilization
  Response time: 5ms avg, 50ms p99
  
  After adding a cache (HashMap + synchronized):
  Same load: CPU 90%, but p99 = 500ms

Your task:
  1. Confirm the HashMap is the cause
  2. Show what a thread dump reveals
  3. Propose the fix

Thread dump analysis:
  Before change: threads in RUNNABLE state, short stack traces
  
  After change (what thread dump shows):
    "http-nio-8080-exec-1" #27 BLOCKED (on object monitor)
      at com.example.CacheService.get(CacheService.java:42)
      - waiting to lock <0x00000000c1b2d3e0>
         (a java.util.HashMap)
    
    "http-nio-8080-exec-2" #28 BLOCKED (on object monitor)
      at com.example.CacheService.get(CacheService.java:42)
      - waiting to lock <0x00000000c1b2d3e0>
    
    (... 30 more similar threads ...)

Fix options (best to worst):

  Option A: ConcurrentHashMap (usually best)
    private final ConcurrentHashMap<String, Object> cache =
        new ConcurrentHashMap<>();
    // No synchronized needed for get/put
    // Segment-level locking internally
    // 99% of cases: use this
    
  Option B: ReadWriteLock (if reads >> writes)
    private final ReentrantReadWriteLock rwLock =
        new ReentrantReadWriteLock();
    // read lock: many threads can hold simultaneously
    // write lock: exclusive
    
  Option C: Caffeine cache (production quality)
    Cache<String, Object> cache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(5, TimeUnit.MINUTES)
        .build();
    // High-throughput; near-zero contention under read load
    // Eviction, expiration built-in
```

---

### Lab Completion Criteria

All 5 labs completed when:

- [ ] Lab 1: Identified NMT region and root cause
- [ ] Lab 2: Found exact thread count mismatch and fix
- [ ] Lab 3: Identified random read pattern and proposed fix
- [ ] Lab 4: Wrote working seccomp profile (or conceptual equivalent)
- [ ] Lab 5: Diagnosed synchronized HashMap + applied ConcurrentHashMap
