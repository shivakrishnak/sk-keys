---
layout: default
title: "Page Cache"
parent: "Operating Systems"
nav_order: 109
permalink: /operating-systems/page-cache/
number: "0109"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, Paging, Page Fault, File Descriptor
used_by: Zero-Copy (sendfile), Memory-Mapped File (mmap), Async I/O
related: Buffer Cache, Dirty Page, Write-Back, fsync
tags:
  - os
  - memory
  - io
  - performance
  - deep-dive
---

# 109 — Page Cache

⚡ TL;DR — The page cache is the OS's in-memory buffer of disk data; every file read/write goes through it, making repeated reads free and writes safe to acknowledge before disk commit.

| #0109           | Category: Operating Systems                                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, Paging, Page Fault, File Descriptor        |                 |
| **Used by:**    | Zero-Copy (sendfile), Memory-Mapped File (mmap), Async I/O |                 |
| **Related:**    | Buffer Cache, Dirty Page, Write-Back, fsync                |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Every `read()` system call on a file goes directly to disk. Disks are 100,000× slower than DRAM. Any program that reads the same file twice — or two processes reading the same file — each pay full disk latency. A web server serving the same HTML file to 10,000 clients would read it from disk 10,000 times.

THE BREAKING POINT:
Even with fast SSDs (0.1ms), a server doing 100,000 reads/second of the same file would spend all its time waiting for storage. And without a write buffer, every `write()` would also block until the disk confirms the write — turning a fast database insert into a 1–10ms disk round trip for every row.

THE INVENTION MOMENT:
The page cache (merged with the buffer cache in Linux 2.4) solves both: reads fill the cache on first access, subsequent reads are served from DRAM (nanoseconds); writes go to cache immediately (acknowledged to the caller) and are flushed to disk asynchronously by kernel writeback threads.

### 📘 Textbook Definition

The **page cache** (also called the **buffer cache** in older Unix terminology) is a region of physical memory managed by the OS kernel that holds copies of disk blocks and file data. File I/O is transparently mediated through the page cache: on `read()`, the kernel checks whether the requested pages are cached; on a cache miss, it fetches the data from disk, stores it in the cache, and returns it to the caller. On `write()`, data is written into cache pages (which become "dirty") and the call returns immediately; writeback kernel threads flush dirty pages to disk asynchronously. The page cache is global to the system and shared among all processes accessing the same file — two processes reading the same file share the same physical cache pages.

### ⏱️ Understand It in 30 Seconds

**One line:**
The page cache is the kernel's transparent read/write buffer between user programs and storage — making repeated file reads free and writes non-blocking.

**One analogy:**

> The page cache is like a restaurant's kitchen prep station. Ingredients ordered from the supplier (disk) are stored on the prep counter (page cache). When a chef needs tomatoes (read), they grab from the counter — instant. If the counter is empty, someone goes to the supplier (disk I/O). Dishes prepared (writes) sit on the counter ready to serve; a back-of-house runner (writeback thread) sends leftover prep back to the warehouse later.

**One insight:**
The page cache is global — when process A reads `/etc/hosts`, the pages are cached. When process B reads the same file, it hits the same cache pages. This is why loading a library that hundreds of processes use (like libc) only causes one disk read — the shared pages live in the page cache.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. All file data access (except O_DIRECT) goes through the page cache.
2. Cache pages are 4KB (matching the hardware page size) for efficiency.
3. Dirty pages are eventually written to disk — "eventually" is controlled by dirty_expire_centisecs and dirty_writeback_centisecs.
4. The kernel can evict clean pages under memory pressure (they can be re-read from disk); dirty pages must be written before eviction.

DERIVED DESIGN:
Each page cache entry is a `struct page` indexed in a radix tree (or xarray in newer kernels) by `(inode, page_offset)`. When `read()` is called: check xarray for the page → miss → submit disk read → wait → insert page into xarray → return data. When `write()`: check xarray → insert/update page → mark dirty → return. Writeback threads (`kworker/flush-*`) periodically scan for dirty pages older than `dirty_expire_centisecs` (default 3 seconds) and submit them for disk write.

THE TRADE-OFFS:
Gain: Read latency from cache = nanoseconds vs microseconds from SSD; write latency = nanoseconds (no disk wait); same file shared in memory across all processes; reduces disk wear.
Cost: Writes are not durable until writeback completes (power loss = data loss for unfsync'd writes); page cache consumes RAM (competes with application heap); O_DIRECT bypasses cache but is complex to use correctly; `mmap` + page cache interaction has subtle consistency rules.

### 🧪 Thought Experiment

SETUP:
A Java application reads the same 1MB configuration file on every HTTP request (100 req/sec).

WITHOUT PAGE CACHE:

- Each read: 1MB from SSD @ ~0.5ms → 50ms/second on disk I/O just for config reads
- At 100 req/sec: server spends 50% of one CPU core waiting on disk for a file that never changes

WITH PAGE CACHE (default):

- First read: 1MB from SSD → loaded into 256 pages in page cache
- Requests 2–100+ per second: served from DRAM → ~250ns per page = ~64µs for 1MB
- Disk cost: amortised over all reads; effectively zero for a file that doesn't change
- Memory cost: 1MB of page cache

THE INSIGHT:
The page cache makes file reading behave like memory access for hot data. This is why Redis can boast "sub-millisecond reads" — its data is in the page cache (or its own heap), not on disk.

### 🧠 Mental Model / Analogy

> The page cache is your browser's disk cache. The first time you visit a website, the browser downloads all the assets (disk read). Next visit, it serves them from cache — instant. Your browser invalidates entries when they expire (LRU eviction). But unlike your browser cache, the OS page cache is shared: if 100 tabs need the same image (file), it's stored once.

Where this breaks down: browser cache is per-user, page cache is system-wide (cross-process). Browser cache invalidation is content-controlled (ETags), page cache coherence is maintained by the VFS layer. And the OS page cache holds dirty data that must be committed — your browser never has "dirty" entries.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you read a file, the OS keeps a copy in RAM. Next time anything reads the same file, it uses the RAM copy — much faster than going to disk again. When you write, the data goes to RAM first and gets saved to disk a moment later.

**Level 2 — How to use it (junior developer):**
The page cache is transparent — you don't explicitly manage it. `read()`/`write()` use it automatically. Use `fsync()` or `fdatasync()` when you need data guaranteed on disk before returning to caller (databases must do this after every transaction commit). `fadvise(FADV_SEQUENTIAL)` hints to the kernel to prefetch aggressively; `FADV_DONTNEED` hints to evict pages after access (useful for large streaming files to avoid polluting cache). `O_DIRECT` bypasses cache entirely — use only for databases that manage their own buffer pool.

**Level 3 — How it works (mid-level engineer):**
Page cache is indexed by `address_space` (one per inode) + offset. `read()` calls `filemap_read()` → `find_get_page()` → on miss: `page_cache_alloc()` + `readpage()` → block layer → I/O scheduler → disk. `write()` calls `generic_perform_write()` → `grab_cache_page_write_begin()` → marks page dirty with `set_page_dirty()`. Writeback: `wakeup_flusher_threads()` → `wb_writeback()` → `writepage()` → block layer. LRU eviction: `shrink_page_list()` → clean pages freed immediately, dirty pages require writeback first.

**Level 4 — Why it was designed this way (senior/staff):**
The page cache was designed around the principle that the access pattern for files looks like the access pattern for virtual memory — both are random-access over a large address space. By using a radix tree (now xarray) indexed by page offset, the kernel reused the same infrastructure for file I/O and `mmap`. The unification in Linux 2.4 that merged the buffer cache (block-level) with the page cache (file-level) eliminated double-caching: before, a file read cashed it once at the block layer and once at the file layer. After unification, one physical page serves both, reducing memory overhead. The dirty throttling system (dirty_bytes, dirty_ratio) exists to prevent write-heavy workloads from flooding the page cache with dirty pages faster than writeback can drain them, which would cause kernel OOM.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│               PAGE CACHE FLOW                          │
├────────────────────────────────────────────────────────┤
│  User:   read(fd, buf, 4096)                           │
│            │                                           │
│  VFS:    filemap_read()                                │
│            │                                           │
│            ├── page in cache? ──YES──→ copy to buf     │
│            │                          return (ns)      │
│            │                                           │
│            └── NOT in cache                            │
│                    │                                   │
│                alloc page → submit block read          │
│                    │                                   │
│            [Block layer → I/O scheduler → Disk]        │
│                    │                                   │
│                insert page into xarray                 │
│                    │                                   │
│                copy to buf → return (ms)               │
│                                                        │
│  User:   write(fd, buf, 4096)                          │
│            │                                           │
│  VFS:    generic_perform_write()                       │
│            │                                           │
│            ├── find/alloc cache page                   │
│            ├── copy from buf to page                   │
│            ├── mark page DIRTY                         │
│            └── return immediately (ns)                 │
│                    │                                   │
│            [Writeback thread — async]                  │
│                    │                                   │
│            flush dirty page → disk (ms) ← LATER       │
└────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (database write path):

```
Application: INSERT row
  → write() to WAL file
  → Page cache: WAL page marked dirty
  → write() returns immediately (ns)
  → fsync(wal_fd)
  → Kernel: flush all dirty pages for wal_fd to disk
  → Disk: confirms write (ms)
  → fsync returns
  → Application: COMMIT acknowledged

Without fsync: power failure between write() and writeback
  → data in RAM but not on disk → transaction lost
```

FAILURE PATH (write storm):

```
Large file copy: 50GB write at 10GB/s
  → Dirty pages fill RAM
  → dirty_ratio threshold hit (10% of RAM default)
  → write() BLOCKS until writeback drains dirty pages
  → Application latency spikes
  → Fix: reduce dirty_ratio, add backpressure, use O_DIRECT
```

### 💻 Code Example

Example 1 — fsync vs no-fsync (database safety):

```java
// BAD: write to DB file, no fsync — data can be lost on crash
FileOutputStream fos = new FileOutputStream("data.db");
fos.write(record);
fos.close();  // dirty pages NOT guaranteed on disk

// GOOD: fsync after critical writes
try (FileOutputStream fos = new FileOutputStream("data.db");
     FileChannel fc = fos.getChannel()) {
    ByteBuffer buf = ByteBuffer.wrap(record);
    fc.write(buf);
    fc.force(true);  // fdatasync (metadata=true for fsync)
    // Only return after disk confirms write
}
```

Example 2 — O_DIRECT bypass (database self-managed cache):

```c
// PostgreSQL, MySQL InnoDB use O_DIRECT to bypass page cache
// They manage their own buffer pool, don't want double caching
int fd = open("tablespace.db",
              O_RDWR | O_DIRECT | O_CREAT, 0600);
// WARNING: reads/writes must be aligned to 512B or 4096B
// (sector size) and buffer must be aligned in memory
void *buf;
posix_memalign(&buf, 4096, 4096);  // 4KB aligned buffer
pread(fd, buf, 4096, page_number * 4096);
```

Example 3 — fadvise for streaming (prevent cache pollution):

```c
// Processing 100GB log file: don't pollute page cache
int fd = open("large.log", O_RDONLY);
off_t offset = 0;

while ((n = read(fd, buf, 1<<20)) > 0) {
    process(buf, n);
    // Tell kernel we won't need these pages again
    posix_fadvise(fd, offset, n, POSIX_FADV_DONTNEED);
    offset += n;
}
// Result: page cache not filled with old log data
// Other programs' hot data stays cached
```

Example 4 — Inspect page cache in production:

```bash
# How much RAM is page cache?
free -h
# "buff/cache" column = page cache + kernel buffers

# More detail: available vs used cache
cat /proc/meminfo | grep -E "Cached|Dirty|Writeback|Buffers"

# Which files are in page cache? (requires pcstat or vmtouch)
vmtouch -v /etc/hosts
# [0/1] 100%  PAGE CACHE

# Force dirty pages to flush
sync

# Check writeback stats
cat /proc/vmstat | grep -E "nr_dirty|writeback"
```

### ⚖️ Comparison Table

| I/O Mode                 | Cache Used          | Durability           | Latency                         | Use For                                |
| ------------------------ | ------------------- | -------------------- | ------------------------------- | -------------------------------------- |
| Default (`read`/`write`) | Yes                 | Not until fsync      | Lowest (cache hits)             | General application I/O                |
| `O_SYNC`                 | Yes (write-through) | After each write     | Higher (disk on every write)    | Log files needing per-write durability |
| `O_DSYNC`                | Yes (data sync)     | Data, not metadata   | Slightly better than O_SYNC     | WAL files                              |
| `O_DIRECT`               | Bypassed            | App's responsibility | Varies (no OS buffering)        | Databases with own buffer pool         |
| `mmap`                   | Yes (same pages)    | Not until msync      | Lowest (page fault then cached) | Large file random access               |

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                   |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| "write() means data is on disk"                   | write() is acknowledged when data is in page cache; disk write happens asynchronously                                     |
| "O_SYNC is the same as fsync"                     | O_SYNC flushes on every write() call; fsync flushes all pending writes for an fd on demand — O_SYNC is per-write overhead |
| "close() flushes dirty pages"                     | close() does NOT fsync; dirty pages may still be in cache after close() returns                                           |
| "Page cache is wasted RAM"                        | It's the most valuable use of RAM — it makes previously-accessed files free to re-read                                    |
| "Linux uses separate buffer cache and page cache" | True before Linux 2.4; since 2.4 they are unified — one page cache for both file and block I/O                            |

### 🚨 Failure Modes & Diagnosis

**1. Write() Appears Slow — Write Storm Throttling**

Symptom: `write()` calls that normally return in microseconds suddenly take tens of milliseconds; usually during large file operations.

Root Cause: Dirty page ratio exceeded `vm.dirty_ratio` (10% of RAM default); kernel throttles writes until writeback drains.

Diagnostic:

```bash
# Watch dirty page count in real time
watch -n 0.1 "cat /proc/vmstat | grep nr_dirty"

# Monitor writeback bandwidth
iostat -x 1
# High %util + high wkB/s during slow period = writeback saturation
```

Fix: Reduce `vm.dirty_ratio` and `vm.dirty_background_ratio`; increase writeback throughput; use O_DIRECT for large writes.

Prevention: Profile dirty page growth vs writeback rate; alert when dirty pages exceed 5% of RAM.

---

**2. Data Loss After Crash (Missing fsync)**

Symptom: After power loss or OS crash, database shows inconsistent state; recently committed transactions are missing.

Root Cause: Application called `write()` and considered data committed, but `fsync()` was never called; dirty pages lost on crash.

Diagnostic:

```bash
# Check if your app calls fsync — trace syscalls
strace -e trace=fsync,fdatasync,sync_file_range -p <PID>
# Should see fsync() after every transaction commit
```

Fix: Add `fsync()`/`fdatasync()` after critical writes. Use `FileChannel.force()` in Java.

Prevention: Enforce durability in tests using crash-recovery test harnesses (e.g., fsck after simulated crash).

---

**3. Page Cache Eviction Causing Latency Spikes**

Symptom: Application is fast normally but periodically has latency spikes; `vmstat` shows high page-in activity at spike time.

Root Cause: Page cache evicted hot data under memory pressure (another process consuming RAM); re-reads from disk cause latency.

Diagnostic:

```bash
vmstat 1 | awk '{print $7, $8}'  # si/so = swap in/out
# High si = pages being read back from disk

# Pin files in page cache (prevent eviction)
vmtouch -l /path/to/critical/file  # lock in RAM
```

Fix: Increase available RAM; use `mlock()` for critical data; `MADV_WILLNEED` to hint prefetch.

Prevention: Monitor cache hit ratio; alert when page-in rate on hot paths increases.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — page cache pages are managed using the same paging infrastructure
- `Paging` — file cache uses 4KB pages; understanding page table is prerequisite
- `File Descriptor` — file I/O flows through fds → VFS → page cache

**Builds On This (learn these next):**

- `Zero-Copy (sendfile)` — sendfile transfers pages directly from page cache to socket without user-space copy
- `Memory-Mapped File (mmap)` — mmap maps page cache pages directly into process virtual address space
- `Async I/O` — async I/O still interacts with page cache; O_DIRECT bypasses it

**Alternatives / Comparisons:**

- `O_DIRECT` — bypass page cache for application-managed buffering (databases)
- `tmpfs` — file system stored entirely in RAM, backed by page cache/swap
- `Buffer pool (PostgreSQL/InnoDB)` — application-level analog of page cache for database pages

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel's transparent in-memory buffer     │
│              │ for all file and block I/O                │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Disk is 100,000× slower than RAM;         │
│ SOLVES       │ repeated reads and immediate-return writes │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Write() returns on cache write; disk      │
│              │ commit happens asynchronously via writeback│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Default for all file I/O; explicit for     │
│              │ fadvise hints, fsync durability control   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ O_DIRECT for databases managing own       │
│              │ buffer pool; O_SYNC for per-write durability│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write throughput + read latency vs        │
│              │ durability (need fsync for crash safety)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reads cached in RAM; writes buffered in  │
│              │  RAM — use fsync to force to disk"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Zero-Copy → mmap → Async I/O → fsync      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Databases like PostgreSQL use `O_DIRECT` to bypass the page cache and manage their own buffer pool. But `O_DIRECT` requires I/O buffer alignment to sector size (512B or 4096B) and writes must be multiple of sector size. What happens when PostgreSQL needs to write a partial 8KB page? Can it write less than 8KB with O_DIRECT, and if not, how does it handle the case where only part of a page changed? (Hint: look up PostgreSQL's partial page write problem and double-write buffer.)

**Q2.** The writeback system uses two thresholds: `dirty_background_ratio` (start background writeback) and `dirty_ratio` (throttle new writes). If a system has 128GB RAM, `dirty_background_ratio=5%` (6.4GB) and `dirty_ratio=10%` (12.8GB), and a database is writing transaction logs at 2GB/s while writeback can sustain 1GB/s — calculate the time until `write()` calls start blocking, the steady-state dirty page level, and whether the system can ever drain. What would you tune to fix this?
