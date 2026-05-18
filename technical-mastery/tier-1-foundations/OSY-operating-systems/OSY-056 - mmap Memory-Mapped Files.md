---
id: OSY-056
title: mmap Memory-Mapped Files
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-054, OSY-055
used_by: OSY-089, OSY-091
related: OSY-055, OSY-057, OSY-090
tags:
  - mmap
  - memory-mapped-files
  - zero-copy
  - page-cache
  - NIO
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/osy/mmap/
---

## TL;DR

mmap() maps a file directly into virtual address space,
giving pointer-like access to file contents without
explicit read/write syscalls. The kernel's page cache
backs the mapping. Used by databases, JVM class loading,
Java NIO MappedByteBuffer, and Redis persistence for
zero-copy, page-cache-friendly I/O.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-056 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | mmap, zero-copy, MappedByteBuffer, page cache, Redis, databases |
| **Prerequisites** | OSY-054, OSY-055 |

---

### The Problem mmap Solves

```
Traditional file I/O pipeline (two copies):
  Disk -> DMA -> Kernel page cache buffer
  Kernel page cache buffer -> CPU copy -> User space buffer
  User space buffer -> application reads data
  
  Two copies:
    Copy 1: DMA from disk to kernel page cache
    Copy 2: CPU copy from page cache to user buffer
    
  Two context switches per read/write syscall:
    user -> kernel (syscall) -> user (return)
    
mmap file I/O pipeline (zero user-space copy):
  Disk -> DMA -> Kernel page cache
  Kernel: maps page cache page into process virtual address space
  User: access the virtual address = directly reading page cache
  
  One copy (DMA only):
    Copy 1: DMA from disk to kernel page cache
    Zero copy: user accesses page cache directly via VMA
    No CPU copy from kernel to user!
    
  Reduced context switches:
    mmap() itself: one syscall (one-time setup)
    Subsequent accesses: just memory reads/writes
    Page faults handle loading (no syscall per access)
```

---

### mmap API and Patterns

```java
// Pattern 1: Read entire file without byte[]:
public class MmapReadAll {
    public static ByteBuffer readFile(Path path) throws IOException {
        try (FileChannel fc = FileChannel.open(path)) {
            // MapMode.READ_ONLY = MAP_SHARED | PROT_READ
            return fc.map(FileChannel.MapMode.READ_ONLY,
                         0, fc.size());
        }
        // MappedByteBuffer survives channel close!
        // Mapping stays until GC or explicit unmap
    }
}

// Pattern 2: Append-only log file (like WAL or commit log):
public class MmapAppendLog {
    private static final int SEGMENT_SIZE = 64 * 1024 * 1024; // 64MB
    private MappedByteBuffer current;
    private RandomAccessFile raf;
    
    public void open(String path) throws IOException {
        raf = new RandomAccessFile(path, "rw");
        raf.setLength(SEGMENT_SIZE);  // pre-allocate file size
        current = raf.getChannel().map(
            FileChannel.MapMode.READ_WRITE, 0, SEGMENT_SIZE);
    }
    
    public synchronized void append(byte[] record) {
        current.putInt(record.length);  // length prefix
        current.put(record);            // record data
        // No write() syscall! Just stores to page cache
        // OS flushes dirty pages periodically (or on msync)
    }
    
    public void sync() {
        current.force();  // msync() - flush dirty pages to file
    }
}

// Pattern 3: Shared memory between JVM processes:
public class SharedMemory {
    // Process A and B map SAME file with MAP_SHARED
    public static MappedByteBuffer openShared(
            String path, int size) throws IOException {
        try (RandomAccessFile raf = new RandomAccessFile(path, "rw")) {
            raf.setLength(size);
            return raf.getChannel().map(
                FileChannel.MapMode.READ_WRITE, 0, size);
        }
        // Process A writes to buffer -> visible in Process B's buffer
        // Because both map to the same physical page cache page!
    }
}
```

---

### Where mmap Is Used in Practice

```
Databases:
  SQLite: entire database file mmap'd for read queries
  LMDB: entire database = one mmap'd file
    (Write: update in-place in mmap, OS handles durability)
  RocksDB: SSTable files mmap'd for point lookups
  
Redis:
  AOF (Append-Only File): optionally uses mmap for appends
  RDB: mmap for saving snapshot (fork + mmap approach)
  
JVM Class Loading:
  JVM mmap()s .jar files (zip format)
  Class data accessed via page-fault-driven loading
  Warm JVM startup: page cache has jar data = fast class load
  Cold JVM startup: page faults = slower (I/O bound)
  
JVM Heap:
  -XX:+UseLargePages: mmap with MAP_HUGETLB for GC heap
  DirectByteBuffer: allocates via mmap or malloc (off-heap)
  
Apache Lucene (used by Elasticsearch):
  Index segments mmap'd (MMapDirectory)
  Read: search traverses mmap'd segment data
  OS manages LRU eviction from page cache
  Segment merge: creates new file via write(), replaces old mmap
  
Kafka:
  Log segments: sendfile() which uses page cache (similar to mmap)
  Consumer reads: page cache serves data without disk I/O
    if consumer keeps up with producer
```

---

### msync and Durability

```
Problem: mmap writes go to page cache first (not disk immediately)
  -> Process crash: data in page cache is SAFE (kernel mode)
  -> Power failure: data in page cache is LOST

msync(addr, length, flags):
  MS_SYNC:  block until dirty pages flushed to disk (fdatasync)
  MS_ASYNC: schedule flush, return immediately (no guarantee)
  
Comparison to fsync():
  fsync(fd):  flush all file data + metadata to disk
  fdatasync(fd): flush data only (not metadata like atime)
  msync(MS_SYNC): equivalent to fdatasync for mmap'd region
  
Durability pattern for databases using mmap:
  1. Write to mmap'd buffer (page cache)
  2. msync(MS_SYNC) -> wait for flush to disk
  3. Update durable on-disk state (log entry)
  This is equivalent to write-ahead logging with mmap

Java MappedByteBuffer.force():
  Equivalent to msync(MS_SYNC)
  Use before: process exit, checkpoint, or after critical writes
```

---

### Failure Modes and Diagnosis

```
1. MappedByteBuffer not released (Java <= 13)
Symptom: File cannot be deleted/renamed on Windows
  (Windows locks files with open file mappings)
  On Linux: "Device or resource busy" for file operations
Diagnosis:
  lsof | grep "DEL" (deleted but still mapped)
  Java process holds MappedByteBuffer reference
Fix:
  Java 14+: use MemorySegment.map() from Foreign Function API
  < Java 14: reflection-based unmap (Elasticsearch pattern):
    ((sun.nio.ch.DirectBuffer) buf).cleaner().clean()
  Or: close the FileChannel AND MappedByteBuffer loses backing
    (on next GC, phantom reference triggers native cleanup)

2. mmap SIGBUS - file smaller than mapping
Symptom: JVM crash: SIGBUS when accessing mapped region
Cause: File was truncated while mapped
  mmap'd region extends beyond new file end
  Access to truncated region -> SIGBUS (bus error)
Fix:
  Never truncate a file while it is mmap'd
  If file must grow/shrink: munmap, resize, remap

3. TLB pressure from many mmap regions
Symptom: Poor performance with many small mmap regions
  perf stat shows high dTLB-load-misses rate
Diagnosis:
  cat /proc/PID/maps | wc -l  (count VMAs)
  If > few hundred: consolidate mappings
Fix:
  Use larger mmap regions (one per file vs per region)
  Or: switch to huge pages for large mappings
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "mmap is always faster than read()" | mmap is faster for: large files, repeated access, random access. read() wins for: single sequential pass of large files (kernel readahead is more effective), files that fit in memory, when you need bytes in a JVM byte[] anyway (the map -> get copy is slower than read() for small files) |
| "MappedByteBuffer releases when FileChannel closes in Java" | The mapping continues to live after FileChannel.close(). The MappedByteBuffer holds a native reference that is only released when the buffer is garbage collected (or explicitly unmapped via internal Cleaner). This is a common resource leak source in Java applications |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| mmap vs read() | mmap: zero user-space copy; read(): kernel copies to user buffer |
| MAP_SHARED | Writes visible to other mappers; writes go to file |
| MAP_PRIVATE | COW; writes are private; don't go to file |
| msync(MS_SYNC) | Block until dirty pages flushed to disk |
| Java API | FileChannel.map() -> MappedByteBuffer |
| SIGBUS | Accessing mmap'd region past file end (truncated file) |
| MappedByteBuffer close | NOT released on channel.close(); released by GC or Cleaner |
