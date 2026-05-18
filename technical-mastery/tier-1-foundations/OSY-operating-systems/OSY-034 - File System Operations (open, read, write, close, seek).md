---
id: OSY-034
title: "File System Operations (open, read, write, close, seek)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-008, OSY-014
used_by: OSY-044, OSY-052, OSY-060
related: OSY-014, OSY-044, OSY-060
tags:
  - file-system
  - syscalls
  - open
  - read
  - write
  - file-descriptors
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/osy/file-system-operations/
---

## TL;DR

File operations (open, read, write, close) are system
calls that operate on file descriptors - kernel-managed
integers representing open files. `read()`/`write()`
copy data between user buffers and the kernel page cache.
Unclosed file descriptors leak and eventually exhaust
the per-process FD limit (default 1024).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-034 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | file operations, file descriptors, open/read/write |
| **Prerequisites** | OSY-008, OSY-014 |

---

### File Descriptor Model

```
File Descriptor (FD): integer representing an open file
  Every process inherits 3 FDs at start:
    0: stdin  (read from keyboard or pipe)
    1: stdout (write to terminal or pipe)
    2: stderr (write to terminal, not buffered)
  Next FD assigned: 3, 4, 5, ... (lowest available)
  
  Process -> File Descriptor Table -> Open File Table -> Inode
  
  File Descriptor Table (per-process, in PCB):
    FD 0: ptr -> open file entry [stdin]
    FD 1: ptr -> open file entry [stdout]
    FD 2: ptr -> open file entry [stderr]
    FD 3: ptr -> open file entry [myfile.txt, offset=0]
    
  Open File Table (global in kernel):
    Entry: file position (offset), flags, inode pointer
    
  Inode Table:
    Entry: file metadata + disk block locations
    
  Key insight: two processes opening same file have
    SEPARATE file position (separate open file entries)
    BUT same inode (same metadata/disk blocks)
```

---

### Core File Syscalls

```c
// open(path, flags, mode) -> file descriptor
int fd = open("/var/log/app.log", O_RDWR | O_CREAT, 0644);
// flags:
//   O_RDONLY: read only
//   O_WRONLY: write only
//   O_RDWR:   read and write
//   O_CREAT:  create if not exists (requires mode)
//   O_TRUNC:  truncate to 0 length on open
//   O_APPEND: all writes go to end of file (atomic append)
//   O_NONBLOCK: don't block (for pipes, devices)

// read(fd, buffer, count) -> bytes_read
char buf[4096];
ssize_t bytes = read(fd, buf, sizeof(buf));
// Returns: > 0 (bytes read), 0 (EOF), -1 (error, check errno)
// read() fills buffer from kernel page cache
// If data not in page cache -> disk read first (major fault)

// write(fd, buffer, count) -> bytes_written
ssize_t written = write(fd, "hello\n", 6);
// write() copies to kernel page cache (NOT disk yet!)
// fsync(fd): force flush page cache to disk
// fdatasync(fd): flush data but not metadata (faster)

// lseek(fd, offset, whence) -> new position
lseek(fd, 0, SEEK_SET);   // go to beginning
lseek(fd, 0, SEEK_END);   // go to end of file
lseek(fd, -100, SEEK_CUR); // go back 100 bytes from current

// close(fd)
close(fd);  // MUST call this! Releases FD + flush buffers
// fclose() in C also flushes stdio buffers before close()
// Failing to close = FD leak
```

---

### Java File I/O (wrapping OS syscalls)

```java
// BAD: resource leak - close() never called on exception
public void processFile(String path) throws IOException {
    FileInputStream fis = new FileInputStream(path);
    int b;
    while ((b = fis.read()) != -1) {
        process(b);
    }
    fis.close();  // never reached if process() throws!
    // FD leak: kernel FD table entry never freed
}

// GOOD: try-with-resources (auto-calls close())
public void processFile(String path) throws IOException {
    try (FileInputStream fis = new FileInputStream(path);
         BufferedInputStream bis = new BufferedInputStream(fis)) {
        // bis wraps fis: 1 OS read per 8KB buffer (not per byte)
        // BufferedInputStream: user-space buffer -> fewer syscalls
        byte[] buf = new byte[8192];
        int bytesRead;
        while ((bytesRead = bis.read(buf)) != -1) {
            process(buf, bytesRead);
        }
    } // auto-closes: fis.close() -> close(fd) syscall
}

// GOOD: NIO for performance
public void processFileFast(String path) throws IOException {
    try (FileChannel channel = 
             FileChannel.open(Path.of(path), StandardOpenOption.READ)) {
        ByteBuffer buf = ByteBuffer.allocate(65536);  // 64KB
        while (channel.read(buf) > 0) {
            buf.flip();
            process(buf);
            buf.clear();
        }
    }
}
```

---

### I/O Data Path

```
Application write("data") -> 
  java.io.BufferedOutputStream (user-space buffer, 8KB)
  when buffer full: flush() ->
    write() syscall ->
      kernel page cache (in-memory OS buffer) ->
        (dirty page, eventually): disk write()

Application read() ->
  read() syscall ->
    page cache HIT: copy from page cache to user buf (fast)
    page cache MISS: load from disk to page cache, then copy

Key insight: Java's BufferedOutputStream/BufferedInputStream
  buffers in JVM heap (user space), PLUS kernel has its own
  page cache buffer. Two levels of buffering.

Durability:
  After write(): data in page cache ONLY (not on disk)
  After fsync(): data committed to disk
  Database transaction commit = always fsync to WAL
```

---

### File Descriptor Leak Detection

```bash
# Check FD count for a process
ls /proc/PID/fd | wc -l
# Default limit: 1024 (soft), can increase with ulimit

# List all open files
lsof -p PID | head -30
# Shows: FD number, type (REG/PIPE/sock), file name

# Check FD limit
cat /proc/PID/limits | grep "Open files"
# Soft Limit: 1024  Hard Limit: 4096

# See if near FD limit
ls /proc/PID/fd | wc -l && cat /proc/PID/limits | grep files

# If close to limit, may see:
# java.io.IOException: Too many open files
# Caused by: open() returning EMFILE (errno 24)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "write() immediately writes to disk" | write() copies data to the kernel page cache. The kernel decides when to write to disk (usually within seconds, on dirty page flush). fsync() forces an immediate disk write. This is why unclean shutdowns can corrupt databases without a write-ahead log |
| "close() without reading all data wastes the socket" | For files: correct, the FD is just freed. For TCP sockets: close() with unread data sends RST (connection reset), not FIN. Use SO_LINGER or read all data before closing |
| "FileOutputStream is safe because Java has try-with-resources" | try-with-resources prevents FD leak from exceptions in the try block, but ResourceLoader/factory patterns outside try-with-resources still leak if exception occurs before the resource enters the try block |

---

### Failure Modes

```
1. File Descriptor Leak
Symptom: "Too many open files" (java.io.IOException)
  gradual degradation over hours/days
Diagnosis: lsof -p PID | wc -l; watch for growth over time
Fix: Audit all InputStream/OutputStream usage for try-with-resources
  Bump FD limit: ulimit -n 65535 (emergency workaround)
  
2. Missing fsync -> Data Loss on Crash
Symptom: application appears to write successfully but
  data is lost after system crash or power failure
Diagnosis: test with kill -9 during write; check if data survives
Fix: call fsync(fd) or FileChannel.force(true) after critical writes
  For databases: always use WAL and sync on commit
  
3. File Position Confusion with Multiple Threads
Symptom: garbled file content when multiple threads write
Diagnosis: concurrent writes to same FileOutputStream
  without synchronization
Fix: use O_APPEND flag (atomic appends for < PIPE_BUF bytes)
  or synchronize all access to single FileChannel
  or give each thread its own FileOutputStream
```

---

### Related Keywords

**Builds on:** OSY-008 (System Call Interface), OSY-014 (File System Overview)

**Related:** OSY-044 (lsof and netstat), OSY-052 (File Descriptor Leak Anti-Pattern)

---

### Quick Reference Card

| Operation | Syscall | Java Equivalent | Notes |
|-----------|---------|----------------|-------|
| Open file | open() | new FileInputStream() | Returns FD |
| Read | read() | fis.read() | Returns bytes read; 0 = EOF |
| Write | write() | fos.write() | Copies to page cache |
| Seek | lseek() | RandomAccessFile.seek() | Move file offset |
| Sync to disk | fsync() | FileChannel.force(true) | Durability guarantee |
| Close | close() | fis.close() / try-with-resources | Free FD, flush buffers |
