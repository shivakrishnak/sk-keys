---
layout: default
title: "Inode — File System"
parent: "Operating Systems"
nav_order: 123
permalink: /operating-systems/inode-file-system/
number: "0123"
category: Operating Systems
difficulty: ★★☆
depends_on: Virtual Memory, System Call (syscall)
used_by: File Descriptor, Memory-Mapped File (mmap), Docker Layers
related: ext4, XFS, VFS, dentry, Page Cache, Hard Link
tags:
  - os
  - storage
  - linux
  - fundamentals
---

# 123 — Inode — File System

⚡ TL;DR — An inode is the metadata record for every file/directory on disk (permissions, size, block pointers) — separate from the filename; the VFS is the kernel abstraction that makes ext4, XFS, and NFS all look the same to user code.

| #0123           | Category: Operating Systems                               | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, System Call (syscall)                     |                 |
| **Used by:**    | File Descriptor, Memory-Mapped File (mmap), Docker Layers |                 |
| **Related:**    | ext4, XFS, VFS, dentry, Page Cache, Hard Link             |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Every file needs to store: who owns it, when it was modified, how large it is, and where the data blocks are physically on disk. If this metadata were stored in the directory entry (next to the filename), renaming a file would require rewriting metadata. Hard links (multiple names for the same file) would require copying metadata and keeping it in sync. Moving a file between directories on the same disk would require copying all data blocks.

THE BREAKING POINT:
The insight: separate the data blocks + metadata (inode) from the name (directory entry). The directory maps name → inode number. The inode stores everything else. Renaming = update directory entry. Hard link = add another directory entry pointing to the same inode number. Moving within a filesystem = update two directory entries, zero data movement.

THE INVENTION MOMENT:
Unix file system (1974, Dennis Ritchie). The inode structure has been fundamentally unchanged: 12 direct block pointers + indirect pointers + owner/permissions/timestamps. Modern filesystems (ext4, XFS, btrfs) extend this with extent-based allocation and checksums, but the conceptual model persists.

---

### 📘 Textbook Definition

An **inode** (index node) is a kernel data structure that stores all metadata about a file or directory: owner (UID/GID), permissions (mode), size, timestamps (atime/mtime/ctime), link count, and pointers to the data blocks on disk. Every file on a Unix filesystem has exactly one inode, identified by a unique inode number within its filesystem. The filename-to-inode mapping is stored in the **directory** (itself an inode + data blocks containing `[name, inode_number]` entries).

The **Virtual File System (VFS)** is the Linux kernel's abstraction layer between system calls (`open()`, `read()`, `stat()`) and concrete filesystem implementations (ext4, XFS, NFS, procfs). VFS defines common in-memory objects (super_block, inode, dentry, file) that all filesystem drivers populate, allowing a single `read()` syscall to work identically for local ext4 files, NFS-mounted files, and virtual `/proc` files.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Inode = file's identity card (metadata + data location); filename = label on the door; directory = door-label-to-identity-card mapping.

**One analogy:**

> A hospital patient has a medical record (inode) identified by patient ID. The hospital directory maps names ("John Smith") to patient IDs. Multiple nurses can refer to "John Smith", "Mr. Smith", or "Bed 42" — all pointing to the same medical record. Renaming the patient in one directory doesn't change the medical record. The record itself stores everything except the name.

**One insight:**
Hard links only work within a filesystem because inode numbers are only unique within one filesystem. A hard link to a file on a different disk would require copying the file, because inode numbers restart at each filesystem boundary.

---

### 🔩 First Principles Explanation

INODE ON DISK (ext4):

```c
struct ext4_inode {
    __le16  i_mode;         // File type + permissions (rwxrwxrwx)
    __le16  i_uid;          // Owner UID (low 16 bits)
    __le32  i_size_lo;      // File size (lower 32 bits)
    __le32  i_atime;        // Last access time
    __le32  i_ctime;        // Inode change time
    __le32  i_mtime;        // Data modification time
    __le32  i_dtime;        // Deletion time
    __le16  i_gid;          // Group ID (low 16 bits)
    __le16  i_links_count;  // Hard link count
    __le32  i_blocks_lo;    // Block count
    __le32  i_flags;        // Flags (e.g., extents)
    __le32  i_block[15];    // Block pointers (or extent tree root)
    // ... (128 bytes total for classic ext4)
};
```

DIRECTORY ENTRY (dentry):

```
/home/alice/notes.txt
  ↓ (directory lookup: "notes.txt")
Directory inode for /home/alice/:
  data blocks contain: [(".", 5000), ("..", 4000), ("notes.txt", 7823)]
  ↓ (inode 7823)
Inode 7823:
  permissions: 0644
  size: 4096 bytes
  mtime: 2024-01-15
  block_ptrs: [12345, 12346, 0, 0, ...]
  ↓ (data blocks 12345, 12346)
Actual file content (bytes)
```

THE TRADE-OFFS:
Gain: Rename O(1), hard links O(1), move-within-filesystem O(1).
Cost: Two lookups for any file access (directory → inode, then inode → data blocks); inode table is fixed-size at mkfs time on ext4 (running out of inodes with many small files is a real issue despite having free space).

---

### 🧪 Thought Experiment

INODE EXHAUSTION:
A log server creates thousands of 100-byte log files per second in /var/log/. The filesystem has 500GB free, but `touch newfile` returns "No space left on device". Impossible? No:

```bash
df -h /var/log      # Shows: 450GB free
df -i /var/log      # Shows: Inodes: 1048576, IUsed: 1048576, IFree: 0
```

Each file requires one inode. ext4's default inode density: 1 inode per 16KB of space. On a 16GB partition: ~1 million inodes. With millions of small files: inodes exhausted, space remains.

Fix at mkfs time:

```bash
mkfs.ext4 -T small /dev/sdb1  # Higher inode density (1 per 1KB)
```

Workaround (can't reformat): use a database or tar-ball small files into fewer large files.

THE INSIGHT:
The inode table is a fixed-size structure decided at filesystem creation. This is a design limitation of ext4. XFS uses dynamic inode allocation (no fixed inode table) — inodes are allocated on demand from data space. This is one reason XFS is preferred for workloads with millions of small files.

---

### 🧠 Mental Model / Analogy

> A library: the **card catalog** is the directory (maps title → catalog number). The **catalog number** is the inode number. The **catalog card** is the inode (author, edition, location in stacks, condition notes). The **shelved book** is the data blocks. You can have multiple catalog cards pointing to the same physical book in the stacks (hard links). The book's location can change (defragmentation) without changing any catalog cards — just update the location field on the catalog card.

> The VFS is the library's checkout system: whether the book is in the building (ext4), at a partner library (NFS), or is a virtual book that's generated on demand (procfs), the checkout process is identical to the borrower.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every file on a Unix system has a unique ID number (inode number) and a metadata record (inode) that stores the file's size, permissions, owner, and where its data is on disk. Filenames are just labels that point to these inode numbers. Deleting a file removes the label — the actual data is gone only when no labels remain and the file is not open by any program.

**Level 2 — How to use it (junior developer):**
Useful commands: `ls -i` (show inode numbers), `stat file` (show full inode metadata), `df -i` (show inode usage), `find / -inum 7823` (find all hard links to inode 7823). In Java/Python: `Files.getAttribute(path, "unix:ino")` or `os.stat().st_ino`. Understanding inodes explains: why hard links can't cross filesystems; why `mv` within a filesystem is O(1) but across filesystems requires a copy; why deleting an open file removes the directory entry but the data remains until `close()`.

**Level 3 — How it works (mid-level engineer):**
Linux VFS in-memory objects: `super_block` (mounted filesystem), `inode` (per-file metadata, backed by page cache), `dentry` (directory entry, cached in dentry cache/dcache), `file` (per-open-fd state: position, flags). Syscall `open("path")` → VFS path walk → dentry cache lookup for each component → inode reads → allocate `file` struct → return fd. The page cache caches inode data blocks: second read() of same blocks hits page cache, no disk I/O. `inode.i_mapping` (address_space struct) links inode to its page cache entries. Dirty pages are written back by `pdflush`/writeback kernel thread based on dirty_expire_centisecs (30s default).

**Level 4 — Why it was designed this way (senior/staff):**
The separation of name (dentry) and metadata (inode) is what makes POSIX rename() atomic: `rename("old", "new")` is a single syscall that atomically replaces the target dentry — either the old name or new name is visible, never a partial state. This atomicity guarantee (from the filesystem journal) is what log-structured merge trees (LevelDB, RocksDB) exploit: write to a temp file, then atomic rename to the final path. The "rename is atomic" invariant underpins safe atomic file updates across all Unix filesystems. It's why `cp foo bar` is not atomic but `mv tmp_result bar` is.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────────┐
│                  VFS LAYER ARCHITECTURE                    │
├────────────────────────────────────────────────────────────┤
│  User space:  open("/etc/passwd", O_RDONLY)                │
│                           │                               │
│  ┌────────── KERNEL VFS ──────────────────────────────┐   │
│  │                                                    │   │
│  │  1. sys_open() → do_filp_open() → path_openat()   │   │
│  │  2. Path walk: "/" → dentry_cache hit              │   │
│  │              "etc" → dentry_cache hit              │   │
│  │              "passwd" → dentry_cache miss          │   │
│  │               → ext4_lookup() → reads inode 1234  │   │
│  │               → create dentry, cache it           │   │
│  │  3. ext4_file_open() → allocate file struct        │   │
│  │  4. Return fd=3                                    │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│  read(3, buf, 1024):                                       │
│    → file->f_op->read() → page_cache_read()               │
│      page in cache? → return bytes                         │
│      page NOT in cache → ext4_readpage() → disk I/O       │
│                         → fill page cache                  │
│                         → return bytes                     │
└────────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

ATOMIC FILE UPDATE PATTERN (rename trick):

```bash
# Application: update config file atomically
# Pattern used by: Kubernetes, etcd, many databases

1. Write to temp file:
   open("/etc/app/config.tmp", O_WRONLY|O_CREAT|O_TRUNC)
   write(fd, new_config_bytes)
   fsync(fd)           # Ensure data on disk (before rename)
   close(fd)

2. Atomic rename:
   rename("/etc/app/config.tmp", "/etc/app/config")
   # Kernel: atomically replaces dentry "config" with "config.tmp"
   # Old inode's link count decrements (eventually freed if no other links)
   # New inode's link count now includes "config" entry
   # Readers see EITHER old config OR new config, never partial write

3. Result:
   Any process reading /etc/app/config sees a complete, consistent file
   No window where the file is partially written or empty
```

---

### 💻 Code Example

Example 1 — Inode info in Python:

```python
import os

stat = os.stat("/etc/passwd")
print(f"Inode number:  {stat.st_ino}")       # e.g., 1447483
print(f"Hard links:    {stat.st_nlink}")      # e.g., 1
print(f"Owner UID/GID: {stat.st_uid}/{stat.st_gid}")
print(f"Permissions:   {oct(stat.st_mode)}")  # e.g., 0o100644
print(f"Size:          {stat.st_size} bytes")
print(f"Blocks:        {stat.st_blocks}")     # 512-byte blocks allocated
print(f"mtime:         {stat.st_mtime}")      # modification time
```

Example 2 — Hard link vs symbolic link:

```python
import os

os.link("/tmp/data.csv", "/tmp/data_backup.csv")    # Hard link (same inode)
os.symlink("/tmp/data.csv", "/tmp/data_link.csv")   # Symbolic link (new inode)

s1 = os.stat("/tmp/data.csv")
s2 = os.stat("/tmp/data_backup.csv")
s3 = os.lstat("/tmp/data_link.csv")   # lstat: stat the symlink itself

print(s1.st_ino == s2.st_ino)   # True — same inode (hard link)
print(s1.st_ino == s3.st_ino)   # False — symlink is a separate inode
print(s1.st_nlink)              # 2 — both names count as links
```

Example 3 — Atomic file write (Java NIO):

```java
import java.nio.file.*;

Path target = Path.of("/etc/app/config.json");
Path temp = Path.of("/etc/app/config.tmp");

// Write to temp file
Files.writeString(temp, newConfigJson);

// Sync to disk (optional — OS may buffer)
try (FileChannel fc = FileChannel.open(temp, StandardOpenOption.WRITE)) {
    fc.force(true);  // fsync equivalent
}

// Atomic rename (same filesystem)
Files.move(temp, target,
    StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.ATOMIC_MOVE);  // throws if not atomic
// Readers see complete old OR new config; never a partial write
```

---

### ⚖️ Comparison Table

| Feature          | ext4              | XFS           | btrfs   | NFS           |
| ---------------- | ----------------- | ------------- | ------- | ------------- |
| Inode allocation | Fixed at mkfs     | Dynamic       | Dynamic | Server-side   |
| Max file size    | 16TB              | 8EB           | 16EB    | Server-side   |
| Inline data      | Yes (small files) | No            | Yes     | N/A           |
| Copy-on-Write    | No                | No            | Yes     | N/A           |
| Snapshots        | No                | Yes (limited) | Yes     | N/A           |
| Small file perf  | Good              | Medium        | Medium  | Network-bound |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                     |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| "Deleting a file frees its space immediately"    | Only when link count = 0 AND no process has the file open; `unlink()` decrements link count |
| "Renaming a file updates its mtime"              | Rename updates ctime (inode change), not mtime (data modification)                          |
| "You can run out of disk space with free inodes" | Yes — inode exhaustion is a separate limit from block exhaustion                            |
| "Hard links work across filesystems"             | No — inodes are filesystem-local; cross-filesystem links require copies (or symlinks)       |

---

### 🚨 Failure Modes & Diagnosis

**1. "No space left on device" With Free Space**

Symptom: `touch newfile` or `write()` fails with ENOSPC despite `df -h` showing free space.

Diagnosis:

```bash
df -i /var/log     # Shows IFree: 0 → inode exhaustion
find /var/log -maxdepth 1 -type d | while read d; do
    echo "$d: $(find $d | wc -l) files"
done              # Identify directory with millions of small files
```

Fix: Cannot increase inodes on ext4 without reformat. Workarounds: consolidate small files, move to XFS (dynamic inodes), or clean up accumulated small files.

---

**2. Stale File Handle (NFS)**

Symptom: NFS clients get `ESTALE` on open; files that "existed" can no longer be opened; happens after server-side operations.

Root Cause: NFS uses inode numbers as file handles. If the server remounts or reformats (new inode numbers), client's cached inode numbers become stale.

Fix: Clients must handle ESTALE by re-walking the path; NFS v4 uses persistent fileids instead of inode numbers to reduce this.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — page cache maps inode data into memory
- `System Call (syscall)` — file operations (open/read/write/stat) are all syscalls into VFS

**Builds On This (learn these next):**

- `File Descriptor` — the user-space handle that references a VFS file object
- `Memory-Mapped File (mmap)` — maps inode's page cache directly into process address space
- `Page Cache` — kernel caches inode data blocks here to avoid disk I/O

**Alternatives / Comparisons:**

- `Object Storage (S3)` — no inodes, no directories — flat namespace with key → object; no rename atomicity
- `Windows NTFS MFT` — analogous to inode table (Master File Table records)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Inode = file metadata + data ptrs        │
│              │ VFS = kernel abstraction for all FSes     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Decouple filename from file identity;    │
│ SOLVES       │ enable hard links, O(1) rename, O(1) mv  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ rename() is atomic — the foundation of   │
│              │ all safe file update patterns             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Debugging "no space" errors; implementing │
│              │ atomic config updates; understanding ln   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Avoid" = monitor inode usage, not just  │
│              │ block usage, in production systems        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Two-level indirection overhead vs        │
│              │ O(1) rename/link flexibility              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "File identity ≠ filename; inode is the  │
│              │  identity; directory is the name map"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ File Descriptor → Page Cache → mmap      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Docker images use a layered filesystem (OverlayFS on modern systems). Each layer is a set of file changes. OverlayFS merges a "lower" (read-only) directory and an "upper" (read-write) directory into a single "merged" view. When a container modifies a file that exists only in the lower layer, OverlayFS performs a **copy-up**: it copies the file from lower to upper, then the container modifies the copy. This copy-up triggers an inode allocation in the upper layer. Describe the exact performance implications of this copy-up for a Java application in a Docker container that does: (1) writes to a log file inside the container, (2) reads a large read-only configuration file, and (3) calls `stat()` on a file that exists in a lower layer but hasn't been accessed yet. Which of these triggers a copy-up and what is the overhead?

**Q2.** `fsync()` flushes a file's dirty pages from the page cache to disk. `fdatasync()` flushes only data (not metadata like timestamps). But even after `fsync()`, a `rename()` on the same directory may not be durable unless you also `fsync()` the **directory** (the inode that contains the dentry). The "write-to-temp-then-rename" atomic update pattern requires: (1) fsync the temp file, (2) fsync the parent directory (to ensure the new dentry is durable). Explain why this is necessary using a specific crash scenario, and describe how journaling filesystems (ext4 data=ordered mode) and ext4's `dirsync` mount option affect whether the directory fsync is needed.
