---
id: OSY-014
title: File System Overview
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-001, OSY-002
used_by: OSY-034, OSY-073, OSY-074, OSY-090
related: OSY-034, OSY-073, OSY-074
tags:
  - foundational
  - filesystem
  - files
  - directories
  - inodes
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/osy/file-system/
---

## TL;DR

A file system organizes data on storage as named files
and directories. The OS provides a unified API (open,
read, write, close) across all file system types. The
inode is the core data structure mapping file metadata
to data blocks on disk.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-014 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | file system, inode, VFS, directories |
| **Prerequisites** | OSY-001, OSY-002 |

---

### What a File System Provides

```
Without file system: disk is a flat array of blocks.
  "Read 512 bytes at byte offset 4,293,918,720" - raw.
  
With file system:
  open("/etc/config.yml", O_RDONLY)
  read(fd, buf, 4096)
  close(fd)
  
File system provides:
  1. Name → data mapping (path to disk blocks)
  2. Metadata storage (owner, permissions, timestamps)
  3. Directory hierarchy (tree of names)
  4. Crash recovery (journaling, COW)
  5. Access control (permission bits, ACLs)
```

---

### VFS (Virtual File System)

```
Linux VFS unifies all file system types:

Application: open("/mnt/nfs/file")  or  open("/tmp/file")
              Same API regardless of filesystem type
                          |
                VFS Layer (generic interface)
                /         \          \         \
           ext4          xfs        tmpfs      NFS client
           (disk)       (disk)      (RAM)      (network)
           
Application never knows if file is on SSD, RAM, or NFS.
VFS provides: struct file_operations with function pointers
  .read, .write, .open, .close, .mmap, .fsync, .ioctl
  Each filesystem implements these differently.
```

---

### File System Types and When to Use Each

| FS Type | Examples | Best For |
|---------|----------|---------|
| Journaling | ext4, XFS, NTFS | General purpose, crash recovery |
| Copy-on-Write | btrfs, ZFS | Snapshots, data integrity |
| In-memory | tmpfs, ramfs | Temporary files, zero I/O latency |
| Network | NFS, CIFS | Shared storage across hosts |
| Distributed | HDFS, Ceph, GlusterFS | Big data, object storage |
| Special | procfs, sysfs | Kernel/process information |

---

### /proc - The Process File System

```java
// Linux procfs: kernel info exposed as "files"
// Java can read OS information via /proc:

import java.nio.file.*;

// Current process memory info
String mem = Files.readString(
    Path.of("/proc/self/status")); // No I/O to disk!
    
// All threads of current JVM
Files.list(Path.of("/proc/self/task"))
    .forEach(t -> System.out.println(t)); // thread IDs

// JVM sees its container's cgroup limits via:
// /proc/self/cgroup    -> cgroup membership
// /sys/fs/cgroup/memory.max -> memory limit
// JVM 11+ reads these to set default heap (-Xmx)
```

---

### Textbook Definition

A file system is an OS subsystem that organizes and
manages files on storage devices. It provides naming
(paths), hierarchy (directories), metadata (permissions,
timestamps), and data integrity (journaling). The Linux
Virtual File System (VFS) layer provides a uniform API
across all file system implementations.

---

### Understand It in 30 Seconds

A file system is a library card catalog for your disk.
Files are books; directories are shelves; inodes are
catalog cards (metadata about each book). The librarian
(VFS) handles your request and finds the book regardless
of which catalog system is used.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Deleting a file frees disk space immediately" | `unlink()` removes the directory entry. Disk space is freed only when the inode's reference count drops to 0 - which requires all open file descriptors to the file to be closed. A Java program with an open FileInputStream to a "deleted" file still holds the disk space |
| "Writing to /tmp is always fast" | /tmp may be tmpfs (RAM) or a disk-backed directory depending on OS configuration. Check: `df -T /tmp`. Modern Linux often uses tmpfs for /tmp by default |

---

### Mastery Checklist

- [ ] Knows what VFS is and why it enables uniform file API
- [ ] Understands inode (metadata) vs data blocks (content)
- [ ] Knows file is freed only when all file descriptors closed
- [ ] Can use /proc filesystem to read OS and process information
