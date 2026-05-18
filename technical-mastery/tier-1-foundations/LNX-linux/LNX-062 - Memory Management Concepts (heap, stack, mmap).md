---
id: LNX-062
title: "Memory Management Concepts (heap, stack, mmap)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-006, LNX-061
used_by: LNX-074, LNX-083
related: LNX-074, LNX-083, LNX-072
tags: [heap, stack, mmap, virtual-memory, page-fault, malloc, brk, VMA, swap, OOM]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/lnx/memory-management-concepts/
---

## TL;DR

Linux process memory has distinct regions: **stack** (function call frames,
grows down, size-limited `ulimit -s`), **heap** (dynamic allocation via
`malloc`/`brk`/`mmap`, grows up), **mmap region** (files, anonymous memory
> 128KB, shared libraries). Virtual memory is lazy: physical pages allocated
only on first access (page fault). `cat /proc/PID/maps` shows all memory
regions. `smaps` shows RSS (resident), PSS (proportional shared). Swap:
anonymous pages evicted to disk when memory is full. OOM killer invoked
when no swap left. `vm.overcommit_memory` controls allocation vs commit.
`free -h`, `vmstat`, `pmap -x PID` for diagnosis.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-062 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | heap, stack, mmap, virtual memory, page fault, malloc, brk, VMA, swap, OOM, overcommit |
| **Prerequisites** | LNX-006 (Processes), LNX-061 (Shared Libraries) |

---

### The Problem This Solves

**Problem 1**: A Java service is killed by the OOM killer despite `free -h`
showing available memory. The JVM pre-allocates 4 GB heap (`-Xmx4g`) but
the process also has off-heap memory: direct byte buffers, code cache,
metaspace, mapped files, thread stacks. Total virtual memory commitment
far exceeds what was planned. Understanding RSS vs VSZ vs PSS explains
the actual memory usage.

**Problem 2**: A C program allocates many small objects with `malloc`. Each
allocation goes to the heap via `brk()` or `mmap()`. The heap grows but
never shrinks back to the OS even after `free()` (glibc holds freed memory
in its allocator pool). Understanding this explains why processes appear to
"leak" memory that they've actually freed - and how tools like jemalloc
help by returning memory to OS more aggressively.

---

### Textbook Definition

**Virtual address space**: Each process has its own 64-bit virtual address
space (128 TB on x86-64). Virtual addresses are mapped to physical addresses
by the MMU (Memory Management Unit) via page tables. Processes are isolated
- they can't access each other's virtual addresses.

**VMA (Virtual Memory Area)**: Contiguous range of virtual addresses with
uniform properties (permissions, type). `cat /proc/PID/maps` shows all VMAs.

**Page fault**: MMU exception when a virtual address is accessed but has no
physical page mapped yet. Kernel page fault handler: allocates a physical
page, maps it in the page table, and resumes the faulting instruction.
"Demand paging" = pages allocated only on first access (not on `malloc()`).

**Stack**: Per-thread region for function call frames (local variables,
return addresses, saved registers). Grows downward. Fixed-size (default 8 MB
per thread, see `ulimit -s`). Stack overflow = SIGSEGV.

**Heap**: The allocator's region. `brk()` syscall moves the heap "break"
pointer up to allocate more memory. `mmap(MAP_ANONYMOUS)` for large
allocations (> threshold, typically 128 KB in glibc). `malloc()`/`free()`
manage the heap; `sbrk(0)` returns the current break.

**mmap**: Map files or anonymous memory into virtual address space.
`mmap(fd, ...)` = file-backed (reads trigger page faults that read disk).
`mmap(MAP_ANONYMOUS)` = not backed by file (used for large allocations,
shared memory). All shared libraries are mapped via `mmap`.

---

### Understand It in 30 Seconds

```bash
# === View process memory layout ===
cat /proc/1234/maps
# Address range          perms offset dev inode  pathname
# 5628a9401000-5628a9402000 r--p 0 fd:01 123456 /usr/bin/myapp (text)
# 5628a9402000-5628a9403000 r-xp ... (executable code)
# 7f8b2c000000-7f8b2e000000 rw-p 0 0:0 0 [heap]
# 7fff1234f000-7fff12370000 rw-p 0 0:0 0 [stack]

# Columns: address | permissions | offset | device | inode | pathname
# r=read, w=write, x=execute, p=private(CoW), s=shared

# More detailed view:
cat /proc/1234/smaps | head -50
# Shows: Size, Rss (resident), Pss (proportional), Shared_Clean, etc.

# === Process memory stats ===
ps -o pid,vsz,rss,comm -p 1234
# VSZ: virtual size (total mapped, most not resident)
# RSS: resident set size (actually in physical RAM)
# RSS << VSZ is normal (demand paging, shared libs counted in VSZ)

# Detailed process memory usage:
pmap -x 1234
# Address    Kbytes  RSS   Dirty Mode  Mapping
# Shows each mapped region with actual RAM usage

# === System memory overview ===
free -h
#             total   used   free   shared  buff/cache  available
# Mem:          31G    8.2G   12G    345M      11G         22G
# available = free + reclaimable (buff/cache)

vmstat 1 5      # 1-second intervals, 5 samples
# Shows: swpd (swap used), free, buff, cache, si/so (swap in/out rate)

# === Swap usage ===
swapon --show      # show swap devices/files
cat /proc/swaps    # active swap areas

# Swap usage per process:
for pid in /proc/[0-9]*; do
    smaps="$pid/smaps"
    if [[ -r "$smaps" ]]; then
        swap=$(grep -i "^Swap:" "$smaps" | awk '{sum += $2} END {print sum}')
        comm=$(cat "$pid/comm" 2>/dev/null)
        if [[ "$swap" -gt 0 ]]; then
            echo "PID $(basename $pid): ${swap}KB swap - $comm"
        fi
    fi
done

# === Overcommit settings ===
sysctl vm.overcommit_memory
# 0 = heuristic (default): allow reasonable overcommit
# 1 = always allow: malloc never fails (dangerous)
# 2 = never overcommit beyond vm.overcommit_ratio% of RAM + swap

sysctl vm.overcommit_ratio    # default 50 (50% of RAM)

# === Stack size ===
ulimit -s          # current stack size limit (default: 8192 KB = 8 MB)
ulimit -s unlimited   # remove limit (for apps with deep recursion)
# Or per-process in C: setrlimit(RLIMIT_STACK, ...)
```

---

### First Principles

**Linux process virtual address space layout (x86-64):**
```
High addresses (kernel space):
  0xFFFF800000000000 - 0xFFFFFFFFFFFFFFFF

  User-kernel boundary:
  0x00007FFFFFFFFFFF  (top of user space)

  [stack]          <- grows DOWN from high address
                      each new frame moves %rsp lower
                      default limit: 8 MB (RLIMIT_STACK)
  |
  |    <-- stack growth direction
  v
  ...
  ^
  |    <-- heap growth direction (brk moves up)
  |
  [heap]           <- grows UP from data segment

  [mmap region]    <- between heap and stack
  (shared libraries, anonymous mmap, file mappings)
  Library: libc.so mapped here at random address (ASLR)
  Anonymous: large malloc(>128KB) mapped here too

  [BSS]            <- uninitialized global variables (zeroed)
  [data]           <- initialized global variables
  [text]           <- executable code (read + execute)

  Low addresses (null pointer territory):
  0x0000000000000000  <- NULL

Example /proc/PID/maps for a simple C program:
  55a2000000-55a2001000 r--p ... /usr/bin/myapp   (ELF header)
  55a2001000-55a2002000 r-xp ... /usr/bin/myapp   (code)
  55a2002000-55a2003000 r--p ... /usr/bin/myapp   (read-only data)
  55a2003000-55a2004000 r--p ... /usr/bin/myapp   (GOT, reloc RO)
  55a2004000-55a2005000 rw-p ... /usr/bin/myapp   (data)
  55a2100000-55a2200000 rw-p 0 0:0 0              [heap]
  7f8b00000000-7f8b40000000 rw-p ...              [mmap/libs]
  ...
  7ffd01234000-7ffd01255000 rw-p ...              [stack]
  7ffd01313000-7ffd01315000 r--p ... [vvar]       (kernel exported vars)
  7ffd01315000-7ffd01316000 r-xp ... [vdso]       (virtual DSO)
```

**Page fault lifecycle:**
```
Program executes: int x = *ptr;   where ptr = 0x7f8b12345000

  CPU checks TLB: no entry for 0x7f8b12345000
  CPU checks page table: no entry (page not yet allocated)
  CPU raises #PF (page fault exception, interrupt 14)

  Kernel page fault handler:
    Looks up 0x7f8b12345000 in the process's VMA list
    
    Case 1: Anonymous VMA (heap/stack/anon mmap):
      Allocate a physical page (from free list or reclaim)
      Zero it (security: never give dirty data to process)
      Map it: update page table entry
      Return from page fault: instruction re-executes, succeeds
    
    Case 2: File-backed VMA (shared lib, mmap'd file):
      Find the file's page in the page cache
      If not in cache: read from disk (disk I/O)
      Map the page into the process's page table
      Return from page fault
    
    Case 3: Address not in any VMA (NULL deref, stack overflow):
      Send SIGSEGV to the process
      Default action: terminate with core dump

Cost: first access to any page = ~100ns (in-memory page fault)
      first access to uncached file page = ~1-10ms (disk I/O)
```

---

### Thought Experiment

Diagnosing a JVM memory issue:

```bash
# Scenario: Java process with -Xmx4g is consuming 6 GB of RSS

# Step 1: See the full memory breakdown:
PID=$(pgrep -f myapp.jar | head -1)
pmap -x "$PID" | tail -5
# Shows total: 6144 MB RSS

# Step 2: Break down by region type:
cat /proc/$PID/smaps | awk '
/^[0-9a-f]/ {region=$6; next}
/^Rss:/ {rss[$6][$0] += $2; total += $2}
END {
    for (r in rss) {
        sum = 0
        for (k in rss[r]) sum += rss[r][k]
        printf "%8.1f MB  %s\n", sum/1024, r
    }
}' 2>/dev/null | sort -rn | head -20
# Example output:
# 2048.0 MB  (Java heap - Xmx4g, 2GB actually used)
# 1024.0 MB  (Code cache / JIT compiled code)
#  512.0 MB  (Thread stacks: 500 threads * 1 MB each)
#  256.0 MB  (Metaspace)
#  128.0 MB  (Direct byte buffers - NIO)
#   64.0 MB  (mapped JAR files)

# Step 3: Thread stack usage:
java_pid=$PID
num_threads=$(ls /proc/$java_pid/task | wc -l)
thread_stack_kb=$(ulimit -s)   # per-thread stack limit
echo "Threads: $num_threads, Stack per thread: ${thread_stack_kb}KB"
echo "Total thread stack: $(( num_threads * thread_stack_kb / 1024 )) MB"

# Fix: reduce thread stack size for Java:
# JVM flag: -Xss256k (reduce from default 1MB to 256KB per thread)
# For 500 threads: 500 * 256KB = 125 MB vs 500 * 1MB = 500 MB
```

---

### Mental Model / Analogy

```
Virtual memory = a very large notebook with sticky tabs

Notebook pages = virtual address pages (4KB each)
Physical RAM = the actual printed pages in the notebook
(only pages you've actually written on are printed)

Sections of the notebook:
  First few pages (text): the program's instructions (printed at load time)
  Middle pages (heap): "buy as you write" - reserved space,
    actual printing (physical allocation) only when you first write on them
  Near the back (mmap region): borrowed pages from reference books
    (shared libraries), printed on demand when you read them
  Last pages (stack): scratch paper for current work
    (function calls), reused as functions return

Page fault = a stub page:
  You flip to a page, find it's blank (no physical backing)
  A process (kernel) quickly prints the content you need:
    Anonymous: prints a blank page (zeroed memory)
    File-backed: goes and copies the content from the book shelf (disk)
  Takes ~100ns or up to 10ms depending on whether the page is on shelf

VSZ = total number of pages you've claimed in the notebook
    (most are blank stubs that haven't been printed yet)

RSS = number of pages that have actually been printed
    (actually in physical RAM right now)

Swap = moving printed pages to a storage box temporarily
    to make room for new pages
    Accessing a swapped page = finding it in the box and swapping it back

OOM killer = the librarian running out of paper:
    When ALL RAM and swap are full, new pages can't be printed
    Librarian picks the most gluttonous notebook and confiscates it (kills PID)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Stack vs heap vs mmap: what they're for. VSZ (virtual) vs RSS (resident).
`free -h` for system memory. `pmap -x PID` or `cat /proc/PID/maps` for
process memory layout. Stack overflow (SIGSEGV from recursion). OOM killer
in system logs (`dmesg | grep -i oom`).

**Level 2:**
Demand paging and page faults. `cat /proc/PID/status | grep Vm` for
VmPeak, VmRSS, VmSwap. Swap usage diagnosis. `vm.swappiness` sysctl
(0=don't swap unless forced, 60=default, 100=swap aggressively). Anonymous
vs file-backed pages. PSS (Proportional Shared Size): for shared libraries,
each process counts 1/N of shared pages (accurate total system view).

**Level 3:**
`brk()` vs `mmap()` for heap allocation (glibc uses brk for small, mmap
for > MMAP_THRESHOLD = 128KB). `malloc_info()` / `malloc_stats()` for glibc
heap analysis. Huge pages: `madvise(ptr, len, MADV_HUGEPAGE)` for THP.
`MADV_DONTNEED`: tell kernel "you can reclaim these pages". `MADV_FREE`:
lazy reclaim (pages may stick in memory if available). Memory barriers and
the `mlock()`/`mlockall()` for preventing swap of critical data.

**Level 4:**
Copy-on-Write (CoW) after `fork()`: child and parent share all pages,
marked read-only. First write by either = page fault -> copy. This is why
`fork()` is fast for server processes. Transparent Huge Pages (THP):
automatic compaction to 2 MB pages for large allocations. KSM (Kernel
Same-page Merging): finds identical pages across VMs/containers, merges
to one physical page (CoW). `vm.overcommit_memory=2` for databases (never
over-allocate; malloc fails when system can't guarantee memory).

**Level 5:**
NUMA (Non-Uniform Memory Access) and memory locality: allocating on the
wrong NUMA node adds ~40-100ns per access vs same-node. `numactl --localalloc`
for NUMA-aware allocation. `perf stat -e cache-misses,cache-references`
for cache miss analysis. Linux page reclaim: the two-list (active/inactive)
LRU algorithm. `kswapd` (background reclaim) vs direct reclaim (sync,
causes latency). Memory cgroups: per-container limits via `memory.max`
(cgroup v2). `memory.stat` for per-cgroup RSS, cache, swap breakdown.
eBPF for memory allocation tracing: `bpftrace -e 'uprobe:c:malloc { ... }'`.

---

### Code Example

**BAD - memory management mistakes:**
```c
// BAD 1: Stack overflow via deep recursion:
long factorial(long n) {
    return n == 1 ? 1 : n * factorial(n-1);  // tail call but NOT TCO
}
// factorial(1000000) = SIGSEGV: stack overflow
// Stack frame is ~16-32 bytes per call; 8MB / 16B = ~500K max depth
// Fix: iterative, or increase stack with ulimit -s / setrlimit

// BAD 2: Accessing freed memory:
char *p = malloc(100);
free(p);
printf("%s\n", p);  // use-after-free: undefined behavior (or crash)
// Detection: ASAN (AddressSanitizer): gcc -fsanitize=address
// Also: Valgrind, Electric Fence

// BAD 3: Not accounting for off-heap memory in Java:
// JVM flags: -Xmx4g  <- sets Java heap max to 4 GB
// But actual process RSS can be 6-8 GB due to:
//   Thread stacks (each thread: 512KB-1MB)
//   JIT code cache (~256MB default)
//   Metaspace (~256MB for class metadata)
//   Direct byte buffers (NIO)
//   JVM internal: GC data structures
// Fix: set MaxMetaspaceSize, ReservedCodeCacheSize, and reduce Xss:
//   -Xmx4g -XX:MaxMetaspaceSize=256m -XX:ReservedCodeCacheSize=64m -Xss256k
```

**GOOD - memory diagnosis script:**
```bash
#!/bin/bash
# mem-diag.sh: diagnose memory usage for a process

PID=${1:-$$}

echo "=== Process $PID Memory Summary ==="
cat /proc/$PID/status | grep -E "^Vm|^Threads" | sed 's/\t/ /g'

echo ""
echo "=== Top memory regions ==="
sort -k2 -rn /proc/$PID/smaps | \
    awk '/^[0-9a-f]/{addr=$1; next} /^Size/{size=$2} /^Rss/{
        if (rss>0 && size>1024) printf "%8dKB  RSS=%8dKB  %s\n", size, rss, addr
        rss=$2
    }' 2>/dev/null | sort -k3 -rn | head -10

echo ""
echo "=== System Memory ==="
free -h

echo ""
echo "=== Swap Usage ==="
swapon --show 2>/dev/null || echo "No swap configured"
total_swap=$(awk '/SwapTotal/{print $2}' /proc/meminfo)
used_swap=$(awk '/SwapFree/{print $2}' /proc/meminfo)
if [[ "$total_swap" -gt 0 ]]; then
    echo "Swap: $(( (total_swap - used_swap) / 1024 )) MB used of $(( total_swap / 1024 )) MB"
fi
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "VSZ (virtual size) is the process's actual memory usage" | VSZ includes ALL virtual address space: code (shared with other processes), heap allocated but not yet touched, memory-mapped files that may be mostly on disk, uninitialized areas. VSZ routinely exceeds physical RAM (a 4 GB Java heap with 2 GB used has VSZ > 4 GB). RSS (resident set size) is a better measure: pages actually in physical RAM. But RSS still overcounts for shared libraries. PSS (Proportional Set Size from /proc/PID/smaps) is the most accurate: shared pages divided by the number of sharers. |
| "free() returns memory to the OS immediately" | glibc's malloc holds freed memory in its own pool (allocator free list) and returns it to the OS only when large contiguous blocks accumulate. This is why `free()` doesn't always reduce RSS. For mmmap()'d allocations (>128KB): these ARE returned to OS on free(). For brk()-allocated small objects: freed but held in allocator pool indefinitely. Tools like jemalloc and tcmalloc are more aggressive about returning memory to the OS. `mallopt(M_TRIM_THRESHOLD, size)` controls when glibc trims the heap. |
| "The OOM killer kills the process using the most memory" | The OOM killer uses a score: `oom_score` (0-1000). It considers: RSS, swap usage, process age, whether it's a root process. It tries to kill the process that "frees the most memory with the least disruption." Often kills the process with high `oom_score_adj` (manually set) or large RSS. System processes, kernel threads, and processes with `oom_score_adj = -1000` are immune. Check: `cat /proc/PID/oom_score`. Protect critical processes: `echo -1000 > /proc/PID/oom_score_adj`. |
| "The stack and heap are separate physical memory regions" | Stack and heap are separate VIRTUAL memory regions, but they're backed by the SAME physical RAM pool. The kernel allocates physical pages from the same pool for both. They just have different virtual addresses and different growth behaviors. On a system with 16 GB RAM, the kernel doesn't pre-reserve 8 MB for each process's stack - the stack's virtual reservation is demand-paged, just like the heap. A stack frame's local variables only consume physical RAM when the function is called. |
| "Setting vm.swappiness=0 disables swap" | `vm.swappiness=0` means "don't swap anonymous pages unless absolutely necessary to avoid OOM" - NOT "disable swap entirely." The kernel may still swap at 0 if it needs to in extreme memory pressure. To completely disable swap use: `swapoff -a`. To prevent a specific process from being swapped: `mlockall(MCL_CURRENT | MCL_FUTURE)` (requires CAP_IPC_LOCK or RLIMIT_MEMLOCK). Database administrators often set `vm.swappiness=1` (not 0) to allow emergency swap while preventing proactive swap of database pages. |

---

### Failure Modes & Diagnosis

**OOM kill diagnosis:**
```bash
# Symptom: process dies unexpectedly, exit code 137 (128 + SIGKILL = OOM)
# or log shows "Killed" with no other info

# Step 1: confirm OOM kill:
dmesg | grep -i "oom\|killed process" | tail -20
# Output:
# Out of memory: Kill process 12345 (java) score 892 or sacrifice child
# Killed process 12345 (java) total-vm:8388608kB, anon-rss:3276800kB, ...

# Step 2: see what triggered it:
dmesg | grep -B 5 "oom"
# May show memory allocation failure that triggered OOM

# Step 3: check current memory state:
free -h    # how much RAM and swap is available
cat /proc/meminfo | grep -E "MemAvail|MemFree|SwapFree|Cached"

# Step 4: identify memory consumers:
ps aux --sort=-rss | head -10   # top RSS processes
pmap -x $(pgrep myapp) | tail -5  # detailed map

# Step 5: mitigation options:
# A) Increase RAM or swap:
dd if=/dev/zero of=/swapfile bs=1M count=4096
mkswap /swapfile
swapon /swapfile

# B) Set memory limits via cgroup (systemd):
systemctl set-property myservice.service MemoryMax=3G

# C) Tune Java heap and off-heap:
# -Xmx3g -XX:MaxMetaspaceSize=256m -XX:ReservedCodeCacheSize=64m

# D) Protect critical processes from OOM kill:
echo -1000 > /proc/$(pgrep sshd)/oom_score_adj

# E) Make batch process the preferred OOM target:
echo 500 > /proc/$(pgrep batch-job)/oom_score_adj
```

---

### Related Keywords

**Foundational:**
LNX-006 (Processes), LNX-061 (Shared Libraries)

**Builds on this:**
LNX-074 (Memory Subsystem), LNX-083 (OOM Killer)

**Related:**
LNX-072 (cgroups), LNX-075 (Transparent Huge Pages)

---

### Quick Reference Card

| Concept | Tool / Path |
|---------|------------|
| Process memory map | `cat /proc/PID/maps` |
| Process memory stats | `cat /proc/PID/status \| grep Vm` |
| Detailed memory regions | `pmap -x PID` |
| Shared memory (PSS) | `cat /proc/PID/smaps` |
| System memory overview | `free -h` |
| Swap usage | `swapon --show` |
| OOM kill history | `dmesg \| grep oom` |
| Overcommit setting | `sysctl vm.overcommit_memory` |

**3 things to remember:**
1. VSZ (virtual) >> RSS (resident) is normal - most virtual addresses are never actually touched (demand paging)
2. `free()` in C/Java doesn't immediately return memory to the OS - allocators hold freed memory in pools
3. OOM killer kills based on `oom_score`, not just highest RSS; protect critical processes with `oom_score_adj=-1000`

---

### Transferable Wisdom

Memory management concepts appear in: JVM heap and GC is a user-space
memory manager on top of Linux's mmap (JVM gets large mmap from OS, manages
objects within it). Go's garbage collector similarly manages memory within
mmap regions. Database buffer pools (PostgreSQL shared_buffers, MySQL
innodb_buffer_pool): large mmap or SysV shared memory regions managed
independently. `mlock()` is why databases often use huge pages for buffer
pools (prevents swap and improves TLB efficiency). Kubernetes Pod memory
limits map directly to cgroup v2 `memory.max` - the same mechanism as
systemd MemoryMax. Container base images: smaller images have less "pre-loaded"
memory via file-backed mmaps. The principle of "lazy allocation" (allocate
virtual space eagerly, physical pages only on first touch) appears in: JVM
heap (reserved vs committed), AWS EBS (provisioned vs used), Azure blob storage
(sparse files), sparse matrices in ML frameworks.

---

### The Surprising Truth

Linux's `overcommit_memory=0` (the default "heuristic" mode) allows programs
to allocate MORE virtual memory than physically exists. When you `malloc(8GB)`
on a system with only 4 GB RAM, it SUCCEEDS and returns a valid pointer.
No memory is allocated yet - just virtual address space is reserved. The
actual memory is allocated only when you TOUCH the pages (first write).
If you then write to all 8 GB, the kernel will start swapping and eventually
invoke the OOM killer. This "optimistic allocation" is why a process can
call `malloc()` successfully and then crash later when actually using the
memory. This is particularly surprising for Java with `-Xmx8g`: the JVM
"reserves" 8 GB virtual space immediately, but only commits physical memory
as the heap fills. `jcmd GC.heap_info` shows the distinction between
"reserved" (virtual) and "committed" (physical). The overcommit design was
chosen because it allows: fork()-based servers to spawn cheaply (CoW means
the child doesn't need to copy everything), optimistic array allocation (reserve
big, use small), and Java heap reservation to be faster. The trade-off: OOM
kills are less predictable than malloc() failure - programs can't easily
"handle" OOM, but they CAN handle `malloc()` returning NULL (in practice,
most don't check anyway).

---

### Mastery Checklist

- [ ] Understands the virtual address space layout (text, data, heap, mmap, stack)
- [ ] Understands VSZ vs RSS vs PSS and when each is meaningful
- [ ] Can diagnose OOM kills from dmesg and identify memory consumers
- [ ] Understands demand paging and why malloc doesn't immediately consume RAM
- [ ] Can use /proc/PID/maps and pmap to analyze a process's memory layout

---

### Think About This

1. A production Java service starts with `-Xmx4g` but the container has
   a 6 GB memory limit. The service is intermittently killed with exit
   code 137. List all memory consumers beyond the Java heap (-Xmx) that
   contribute to the process's total RSS. What JVM flags would you add
   to control each one?

2. A C program allocates 1 GB with `malloc(1 << 30)` and then `free()`s
   it. After the free, `free -h` shows no change in available memory.
   Explain why, and describe two different scenarios where memory WOULD
   be returned to the OS after a free() call.

3. A colleague suggests setting `vm.overcommit_memory=2` on a PostgreSQL
   server to prevent OOM kills. Explain: (a) what this setting does, (b)
   what happens when PostgreSQL tries to allocate memory that can't be
   committed, (c) why this might actually be BETTER for a database than
   the default overcommit, and (d) what to set `vm.overcommit_ratio` to
   ensure PostgreSQL can allocate its shared_buffers.

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the difference between VSZ and RSS in Linux process memory statistics.
A: VSZ (Virtual Size) and RSS (Resident Set Size) measure different things about a process's memory: VSZ: the total size of the process's VIRTUAL address space. This includes: (1) Code (text segment) - shared with other instances of the same program. (2) Heap - includes allocated but never-touched pages (demand paging: `malloc(1GB)` reserves virtual space but RSS only grows as you write to pages). (3) Memory-mapped files - entire files may be mapped but only accessed pages are in RAM. (4) Shared libraries - fully counted even though they're shared with dozens of other processes. VSZ can easily be 10x the physical RAM on a server. It's mostly meaningless for capacity planning. RSS: pages actually in PHYSICAL RAM right now. More meaningful, but still imperfect: it counts shared library pages in FULL for each process (if 50 processes share libc, each shows the full libc size in RSS). PSS (Proportional Set Size, from `/proc/PID/smaps`): the most accurate metric. For shared pages, counts 1/N of the page's size (N = number of processes sharing it). `PSS_total = unique_pages + shared_pages/N`. Used by Android for memory reporting. Practical example: a Java process with 4 GB heap (-Xmx4g) using 2 GB: VSZ might be 8 GB (4 GB heap + 2 GB for thread stacks, code, shared libs, etc.). RSS might be 3 GB (2 GB heap pages touched + shared libs + thread stacks). PSS might be 2.5 GB (subtract the shared lib portion divided among all Java processes). For capacity planning: use RSS. For system-wide accounting: sum PSS values across all processes.

**Expert:**
Q: Describe how fork() and copy-on-write affect memory usage in a multi-process server (e.g., Gunicorn or Unicorn).
A: `fork()` creates a child process that is initially a copy of the parent. Without CoW: fork would copy all 2 GB of a Rails app's memory for each worker - starting 8 workers = 16 GB RAM just for workers. With CoW: fork marks all parent pages as read-only. Both parent and child share the same physical pages. Memory usage: child starts at ~0 additional RSS. When either process WRITES to a shared page: page fault occurs, kernel copies that specific 4 KB page and gives the writer a private copy. This enables: Gunicorn/Unicorn pre-fork workers: the master loads the Rails app (2 GB), forks N workers. Each worker starts with ~0 additional RAM. Only pages modified by workers (request-specific data, GC, etc.) get copied. Typical result: 8 workers might only use an additional 200 MB total (vs 16 GB without CoW). The Ruby "copy-on-write-friendly GC" (Ruby 2.0+) tries to minimize writes to the object space, keeping more pages shared across workers. Java doesn't benefit similarly from fork (GC marks objects as "used", touching many pages and forcing CoW copies). Python uses fork for multiprocessing; torch.multiprocessing uses shared memory for tensors. Diagnosis: `cat /proc/PID/smaps | grep "Shared_Clean"` = pages still shared with parent (CoW not triggered). `Private_Dirty` = pages that have been copied after fork (CoW triggered, this process now owns them). Low `Private_Dirty` = efficient fork() CoW sharing; high = workers are diverging from parent state.
