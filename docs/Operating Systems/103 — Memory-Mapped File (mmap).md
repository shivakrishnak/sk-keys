---
layout: default
title: "Memory-Mapped File (mmap)"
parent: "Operating Systems"
nav_order: 103
permalink: /operating-systems/memory-mapped-file-mmap/
number: "0103"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, Paging, Page Fault, File Descriptor
used_by: Zero-Copy (sendfile), Page Cache, Blocking I/O
related: Page Cache, Zero-Copy (sendfile), File Descriptor
tags:
  - os
  - memory
  - internals
  - performance
  - deep-dive
---

# 103 — Memory-Mapped File (mmap)

⚡ TL;DR — `mmap` lets your process treat a file as if it's in RAM — the OS loads pages on demand and writes changes back to disk automatically.

| #0103           | Category: Operating Systems                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, Paging, Page Fault, File Descriptor |                 |
| **Used by:**    | Zero-Copy (sendfile), Page Cache, Blocking I/O      |                 |
| **Related:**    | Page Cache, Zero-Copy (sendfile), File Descriptor   |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
To process a 10 GB log file, a program must: `open()` the file, call `read(fd, buf, 4096)` in a loop, copy bytes from kernel buffer to user buffer, process, repeat 2.5 million times. Each `read()` syscall is ~200 ns overhead, totalling ~500 ms just in syscall cost. Each kernel→user copy doubles the memory traffic. To random-access byte at offset 7,342,108,432, the program must either `lseek()` + `read()` (two syscalls) or load the whole file.

THE BREAKING POINT:
Database engines, JVM class loaders, and compilers all need fast, random access to large files. The syscall-per-chunk model is too slow and too complex. Loading the whole file into a heap buffer wastes RAM for parts never accessed.

THE INVENTION MOMENT:
This is exactly why `mmap` was created — to map a file directly into the process's virtual address space, letting the OS page-fault mechanism lazily load only the needed pages, with zero explicit I/O syscalls for reads.

### 📘 Textbook Definition

**Memory-mapped file (`mmap`)** is an OS mechanism that maps a file (or anonymous region) into a process's virtual address space, backed by the file's data through the **page cache**. Reading the mapped region triggers demand-paging: the first access to a page causes a page fault, the OS reads the file page into the page cache and maps it into the process. Subsequent accesses hit either the page cache or the TLB with no syscalls. For writable maps, modified pages are marked dirty and written back to the file by the kernel (via `msync()` or writeback).

### ⏱️ Understand It in 30 Seconds

**One line:**
mmap turns a file into an array in your program's memory — read and write it like any variable.

**One analogy:**

> Traditional file I/O is like a mailbox: you make a request, wait for the postal worker to bring you one letter at a time. mmap is like having the entire filing cabinet teleported into your office — every document is right there at arm's reach. You grab exactly what you need, instantly. The office manager (OS) makes sure any changes you make are eventually filed back.

**One insight:**
The most important insight about mmap is that there is no "copy" — the file data lives in the page cache (kernel), and your virtual address is simply mapped to those same physical pages. A read() would copy kernel pages to your heap; mmap shares the physical pages directly. This is why `mmap` enables zero-copy file access.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. An mmap region is backed by physical pages in the page cache — the same pages used by `read()`.
2. File data is loaded lazily on first access via page fault — no eager loading.
3. Writable, non-private mappings share physical pages with the file; `MAP_PRIVATE` uses copy-on-write.

DERIVED DESIGN:
`mmap(NULL, size, PROT, flags, fd, offset)` creates a VMA in the process's address space linked to the file's inode. No physical pages are allocated. On first access, the page fault handler calls the VMA's `fault()` method, which calls the filesystem's `readpage()`, loading the file page into the page cache. The PTE is set to point to this page cache page. Subsequent accesses: TLB hit (if recently accessed) or PTE hit — no syscall, no copy.

THE TRADE-OFFS:
Gain: Zero-copy access to files; lazy loading (only accessed pages use RAM); sharing between processes (multiple processes can mmap the same file, sharing physical pages); pointer arithmetic instead of offset management.
Cost: Address space consumption; TLB pressure from many pages; page fault latency for cold pages; complex error handling (`SIGBUS` on I/O error instead of return value); no read-ahead control (though `madvise` helps).

### 🧪 Thought Experiment

SETUP:
A program reads 100 random records from a 1 GB database file. Each record is 1 KB, spread across different 4 KB pages.

WHAT HAPPENS WITH read():

1. 100 × `lseek()` calls = 100 syscalls (~200 ns each = 20 µs)
2. 100 × `read()` calls = 100 syscalls (~200 ns each = 20 µs)
3. Each `read()` copies 1 KB from kernel page cache to user heap = 100 copies
4. Total syscall overhead: 40 µs. Plus 100 × disk reads if not cached.

WHAT HAPPENS WITH mmap():

1. One `mmap()` call maps the entire 1 GB.
2. 100 pointer dereferences trigger 100 page faults (first access per page).
3. Each fault loads page into page cache — same underlying I/O as read().
4. No copies: user sees the page cache pages directly through virtual address.
5. Second run: all 100 pages may be warm in page cache → 100 TLB/cache hits → no I/O.

THE INSIGHT:
mmap eliminates the kernel→user copy entirely. Both `read()` and `mmap` load pages through the page cache; `mmap` just removes the extra copy step and replaces it with a virtual address mapping.

### 🧠 Mental Model / Analogy

> mmap is like mounting a filesystem inside your apartment. The entire filing cabinet (file) appears as a folder on your desk (virtual address range). Grabbing a document (reading a byte) retrieves it from the cabinet on demand — the building manager (OS) fetches it from storage (disk) if not already in the lobby (page cache). Any documents you annotate (write) are automatically filed back.

"Folder on your desk" → mapped virtual address range
"Building manager fetching document" → page fault + page cache read
"Lobby" → page cache (shared between all processes)
"Annotating a document" → writing to MAP_SHARED region
"Your own notebook copy" → MAP_PRIVATE (copy-on-write)

Where this analogy breaks down: Unlike a physical folder, multiple processes can share the same mmap'd pages in RAM — changes in one process's MAP_SHARED region are immediately visible to all others mapping the same file.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
mmap lets your program access a file's contents as if they were a normal array in memory. Instead of reading chunks with `read()`, you just use pointer arithmetic. The OS automatically handles loading data from disk when you access a part you haven't read yet.

**Level 2 — How to use it (junior developer):**
Common use cases: reading configuration files without parsing into heap (avoids allocation), sharing memory between processes (`MAP_SHARED`), loading shared libraries (`.so`/`.dll` are always mmap'd by the OS), and implementing memory-mapped databases (SQLite, LMDB, RocksDB). Avoid mmap for small files (syscall overhead of setup dominates) or when you need precise I/O error handling (mmap errors are `SIGBUS`, not return values).

**Level 3 — How it works (mid-level engineer):**
`mmap()` calls `do_mmap()` in the kernel, which creates a `vm_area_struct` (VMA) linked to the `file` struct via the VMA's `vm_ops` (operation table). The VMA's `fault` handler is set to the file system's `filemap_fault()`. On access, `filemap_fault()` calls `find_get_page()` (page cache lookup); if not present, allocates a page, calls `readpage()` to fill it from disk, and maps it. `msync(MAP_SYNC)` flushes dirty pages to disk immediately; without it, writeback is asynchronous via `pdflush`/`writeback` kernel threads. `munmap()` flushes dirty pages and removes the VMA.

**Level 4 — Why it was designed this way (senior/staff):**
The design of sharing page cache pages directly (rather than copying) was a deliberate choice to eliminate double-buffering. The tradeoff is that mmap error handling is fundamentally different from I/O errors: a `read()` that fails returns `-1`; an mmap fault that encounters a bad disk sector delivers `SIGBUS`. Production databases that mmap files must install a `SIGBUS` handler to catch and handle disk errors gracefully — a subtle source of bugs. LMDB uses mmap exclusively for reads (zero-copy, zero-allocation per read) but takes a write lock for writes. RocksDB uses mmap for SST file reads in production configurations. The JVM uses mmap for loading class files (`ClassLoader`) — a 100 MB JAR becomes a set of mmap'd pages, with classes loaded lazily on first use.

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│                mmap() INTERNAL FLOW                     │
├─────────────────────────────────────────────────────────┤
│  mmap(NULL, 4GB, PROT_READ, MAP_SHARED, fd, 0)          │
│       ↓                                                 │
│  Kernel: create VMA [0x7f000000–0x27f000000)            │
│          link VMA.vm_ops = &ext4_file_vm_ops            │
│  Returns: 0x7f000000                                    │
│       ↓                                                 │
│  User: char c = ptr[1_000_000_000]   // first access   │
│       ↓                                                 │
│  MMU: TLB miss → PTE.Present=0 → Page Fault             │
│       ↓                                                 │
│  Kernel: filemap_fault()                                │
│     1. find_get_page(inode, page_index) → not found     │
│     2. alloc page in page cache                         │
│     3. submit_bio: read page from disk                  │
│     4. wait for I/O (process blocks)                    │
│     5. install PTE: page cache page → user VA           │
│       ↓                                                 │
│  User: c = page[1_000_000_000 % 4096]  // no copy      │
└─────────────────────────────────────────────────────────┘
```

**Subsequent access to same page:** TLB hit (if warm) → direct access to page cache physical page, ~4 cycles.

**mmap vs read() comparison:**

```
read():  disk → page cache → (copy) → user heap
mmap():  disk → page cache → (mapped) → user VA  [no copy]
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[fd = open("data.bin", O_RDONLY)]
   → [ptr = mmap(NULL, size, PROT_READ, MAP_SHARED, fd, 0)]
   → [VMA created, no physical pages ← YOU ARE HERE]
   → [ptr[N]: page fault → page cache → disk if needed]
   → [PTE installed, data accessible at ptr[N]]
   → [munmap(ptr, size): PTE torn down, pages stay in cache]
```

FAILURE PATH:
[Disk I/O error during page fault] → [SIGBUS delivered to process] → [Process crashes unless SIGBUS handler installed]

WHAT CHANGES AT SCALE:
A database process mapping 1 TB of data files has 256 million PTE entries. Page table memory itself can be gigabytes. At 1000 concurrent processes all mapping the same shared files, Linux deduplicates the page cache pages — all share the same physical pages — but each process has its own PTE chain, multiplying page table overhead by 1000. Production DBs use `madvise(MADV_SEQUENTIAL)` or `MADV_RANDOM` to tune read-ahead behaviour.

### 💻 Code Example

Example 1 — Basic read-only file mapping:

```c
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

// BAD: read() requires explicit buffer management
char buf[4096];
int fd = open("data.bin", O_RDONLY);
lseek(fd, 1000000, SEEK_SET);
read(fd, buf, 4096);  // copy from page cache

// GOOD: mmap for zero-copy access
int fd = open("data.bin", O_RDONLY);
struct stat st;
fstat(fd, &st);
char *ptr = mmap(NULL, st.st_size,
    PROT_READ, MAP_SHARED, fd, 0);
// Access as array — no copy, demand paging
char c = ptr[1000000];  // page fault on first access
munmap(ptr, st.st_size);
close(fd);
```

Example 2 — Shared memory between processes:

```c
// Process A: creates shared region
int fd = shm_open("/my_shared", O_CREAT|O_RDWR, 0666);
ftruncate(fd, 4096);
int *shared = mmap(NULL, 4096,
    PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
*shared = 42;  // immediately visible to Process B

// Process B: maps same region
int fd = shm_open("/my_shared", O_RDWR, 0);
int *shared = mmap(NULL, 4096,
    PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
printf("%d\n", *shared);  // prints 42
```

Example 3 — SIGBUS handling for mmap:

```c
#include <signal.h>
#include <setjmp.h>

static sigjmp_buf sigbus_jmp;

void sigbus_handler(int sig) {
    siglongjmp(sigbus_jmp, 1);
}

// BAD: no error handling for disk errors
char c = mmap_ptr[offset];  // crashes on disk error

// GOOD: install SIGBUS handler
signal(SIGBUS, sigbus_handler);
if (sigsetjmp(sigbus_jmp, 1) != 0) {
    fprintf(stderr, "Disk I/O error at offset\n");
    // handle gracefully
} else {
    char c = mmap_ptr[offset];  // safe
}
```

### ⚖️ Comparison Table

| Approach   | Copy Overhead   | Syscalls  | Random Access      | Error Handling | Best For                  |
| ---------- | --------------- | --------- | ------------------ | -------------- | ------------------------- |
| **mmap**   | Zero            | 1 setup   | Pointer arithmetic | SIGBUS         | Large random-access files |
| read()     | Double buffered | Per-chunk | lseek+read         | Return value   | Sequential streaming      |
| sendfile   | Zero (kernel)   | 1         | No                 | Return value   | File serving over network |
| Direct I/O | Single          | Per-chunk | O_DIRECT           | Return value   | DB bypass page cache      |

How to choose: Use mmap for large files with random access patterns (databases, indexes, sparse access). Use `read()` for sequential streaming where read-ahead is important. Use `sendfile` for serving files to sockets without user-space involvement.

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────────────┐
│               mmap PAGE LIFECYCLE                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  mmap() → VMA created, no physical pages               │
│    ↓ first access                                      │
│  Page Fault → loaded into page cache (major if cold)   │
│    ↓ subsequent accesses                               │
│  TLB/cache hits → zero overhead                        │
│    ↓ if MAP_SHARED + write                            │
│  Page marked dirty → writeback thread syncs to disk    │
│    ↓ msync(MS_SYNC) called explicitly                 │
│  Dirty pages flushed to disk synchronously             │
│    ↓ munmap() or process exit                          │
│  PTE removed, dirty pages written back, VMA freed      │
│    ↓ (page cache may retain pages for other processes) │
│  Physical page released when no more references        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                             |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| "mmap loads the whole file into RAM immediately"        | mmap creates virtual mappings; physical pages are loaded on demand via page faults                                  |
| "mmap is always faster than read()"                     | For small files or sequential read-once workloads, read() with large buffers outperforms mmap due to setup overhead |
| "munmap() writes changes to disk"                       | munmap flushes dirty pages but doesn't guarantee durability; call msync(MS_SYNC) before munmap for durability       |
| "MAP_PRIVATE writes are not visible to other processes" | Correct — but the copy-on-write means your write consumes extra physical RAM for the modified pages                 |
| "File must exist on disk for mmap to work"              | MAP_ANONYMOUS mmap creates memory with no file backing — used for large heap-like allocations (e.g., by malloc)     |

### 🚨 Failure Modes & Diagnosis

**1. SIGBUS on Disk I/O Error**

Symptom: Process crashes with SIGBUS; stack trace points into mmap'd region access; disk logs show I/O error.

Root Cause: During a page fault on an mmap'd file, the underlying disk I/O failed; the kernel delivers SIGBUS instead of returning an error code.

Diagnostic:

```bash
dmesg | grep -i "I/O error\|blk_update_request"
journalctl -k | grep "ata\|scsi\|nvme" | grep -i error
```

Fix: Install a `SIGBUS` handler with `sigsetjmp`/`siglongjmp` (see code example 3). Use checksums/CRC to detect data corruption on read.

Prevention: Use RAID or replicated storage; monitor disk health with SMART; use `O_DIRECT` + `read()` for data that must have proper error handling.

---

**2. Memory Leak via Stale mmap Mappings**

Symptom: Process virtual address space grows without bound (`/proc/PID/maps` accumulates entries); OOM kill eventually.

Root Cause: `mmap()` called in a loop without corresponding `munmap()`; typically in code that remaps files on each access.

Diagnostic:

```bash
cat /proc/<PID>/maps | wc -l   # count VMAs
pmap -x <PID> | tail -5        # total mapped
# If total > 2× actual data size: leak likely
```

Fix: Ensure every `mmap()` has a matching `munmap()` in all code paths, including error paths.

Prevention: Use RAII wrappers in C++ (`std::unique_ptr` with custom deleter); audit with `valgrind --tool=massif`.

---

**3. Dirty Page Writeback Latency (msync Blocking)**

Symptom: `msync(MS_SYNC)` takes 100ms+ unexpectedly; application appears to hang during checkpoint.

Root Cause: Large number of dirty pages accumulated (MAP_SHARED + many writes); `MS_SYNC` must flush all of them synchronously to disk.

Diagnostic:

```bash
# Check dirty page count
cat /proc/meminfo | grep Dirty
# Monitor writeback
iostat -x 1 | grep -v "^$"
```

Fix:

```c
// BAD: one big msync at end
// (all dirty pages flush at once — huge latency spike)
msync(ptr, large_size, MS_SYNC);

// GOOD: periodic incremental msync
for (size_t off = 0; off < total; off += CHUNK) {
    msync(ptr + off, CHUNK, MS_ASYNC);
}
// Final sync
msync(ptr, total, MS_SYNC);
```

Prevention: Tune `vm.dirty_ratio` and `vm.dirty_background_ratio` to control when writeback threads run; call `msync(MS_ASYNC)` periodically to amortise flush cost.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — mmap is built on virtual address space management
- `Paging` — mmap pages are loaded via the standard demand-paging mechanism
- `Page Fault` — the mechanism by which mmap pages are loaded on first access

**Builds On This (learn these next):**

- `Page Cache` — mmap shares physical pages with the kernel's page cache
- `Zero-Copy (sendfile)` — similar zero-copy principle applied to file-to-socket transfers
- `File Descriptor` — mmap takes a file descriptor as input

**Alternatives / Comparisons:**

- `read() / write()` — explicit I/O with copies; simpler error handling but higher copy overhead
- `sendfile()` — zero-copy for file→socket, but no user-space access to data
- `Direct I/O (O_DIRECT)` — bypasses page cache entirely; useful for databases managing their own cache

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ File content mapped into virtual address  │
│              │ space — access as pointer, no read() calls│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ read() copies kernel→user; mmap shares    │
│ SOLVES       │ page cache pages directly (zero-copy)     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ No copy: mmap and read() use same page    │
│              │ cache pages; mmap just skips the copy     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Large files with random access; shared    │
│              │ memory IPC; database buffer pools         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small files (setup overhead dominates);   │
│              │ when I/O errors need clean return codes   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero-copy + lazy load vs SIGBUS errors    │
│              │ + address space/TLB overhead              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The file teleported into your address    │
│              │  space — grab any byte instantly"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Page Cache → Zero-Copy → sendfile         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** LMDB (Lightning Memory-Mapped Database) uses mmap for all reads, achieving near-zero per-read overhead. However, LMDB has a hard limit: the database must be smaller than available virtual address space (128 TB on 64-bit Linux). MongoDB used mmap-based storage (MMAPv1) and abandoned it for WiredTiger. What specific operational problems at scale forced MongoDB to move away from mmap storage, and which of those problems would LMDB also encounter at the same scale?

**Q2.** A microservice memory-maps a 100 GB dataset for read-only lookups. The service runs in 50 replicas, each as a separate process. How does the OS handle the physical memory usage across 50 processes all mapping the same file — and what happens to the shared page cache when one replica process is OOM-killed?
