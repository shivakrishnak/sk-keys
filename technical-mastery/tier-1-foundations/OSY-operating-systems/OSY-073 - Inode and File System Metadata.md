---
id: OSY-073
title: Inode and File System Metadata
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-013, OSY-034
used_by: OSY-074, OSY-089
related: OSY-013, OSY-074, OSY-089
tags:
  - inode
  - file-system
  - metadata
  - hard-link
  - soft-link
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/osy/inode-filesystem-metadata/
---

## TL;DR

An inode stores file metadata (permissions, timestamps,
block pointers) but NOT the filename. The directory maps
names to inode numbers. Hard links: two names for the same
inode. Soft links: name that points to another name.
`df -i` shows inode exhaustion (can cause "no space left"
even with disk space available). Each file = 1 inode;
large numbers of small files exhaust inodes first.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-073 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | inode, hard link, soft link, df -i, directory entry |
| **Prerequisites** | OSY-013, OSY-034 |

---

### Inode Structure

```
Inode (Index Node) stores:
  - File type (regular, directory, symlink, block device, etc.)
  - Permissions (rwxrwxrwx, setuid, setgid, sticky)
  - Owner (UID) and group (GID)
  - File size (in bytes)
  - Link count (number of hard links pointing to this inode)
  - Timestamps:
      atime: last ACCESS time
      mtime: last MODIFICATION time (content changed)
      ctime: last CHANGE time (inode changed: chmod, chown, etc.)
  - Block pointers: direct + indirect + double indirect blocks
    (ext4 uses extent-based allocation instead)
  
  NOT stored in inode:
    - Filename (stored in directory entry, not inode)
    - Full path (not stored anywhere explicitly)
    
Inode number:
  Unique identifier within a filesystem
  Directory entry = (filename, inode_number) pair
  Multiple filenames can map to same inode = hard links

Check inode number:
  ls -i file.txt
  stat file.txt
  # Output: inode: 1234567
  
  find / -inum 1234567  # find all hard links to this inode
```

---

### Hard Links vs Symbolic Links

```
Hard Link:
  Two (or more) directory entries pointing to the SAME inode
  
  ln original.txt hardlink.txt
  ls -i original.txt hardlink.txt
  # 1234567 original.txt
  # 1234567 hardlink.txt  <- SAME inode!
  
  Properties:
    Both names: same file (same inode = same permissions, owner, size)
    Inode link count: 2 (two directory entries)
    Delete "original.txt": inode not deleted! link count -> 1
    File data remains until link count = 0 (no more names)
    Limit: cannot cross filesystem boundaries (different inodes pools)
    Cannot hard-link directories (would create cycles in directory tree)
    
  Use case: atomic file swap
    write to new_config.txt
    ln new_config.txt config.txt  # atomic (same filesystem)
    # Or: rename (also atomic):
    mv new_config.txt config.txt  # atomic on same filesystem
    # rename() = atomic: readers see either old or new, never partial

Symbolic Link (Soft Link):
  Directory entry pointing to another PATH (string)
  
  ln -s /actual/path/file.txt link.txt
  ls -la link.txt
  # lrwxrwxrwx 1 user group 20 ... link.txt -> /actual/path/file.txt
  
  Properties:
    Has its OWN inode (stores the target path string)
    Original file deleted: symlink is "dangling" (broken)
    Can cross filesystem boundaries (just a path string)
    Can link to directories
    Kernel follows symlink transparently (resolves the path)
    Permissions: always 777 for symlink inode (target's perms apply)
    
  Use case: version management
    ln -s /opt/java-17.0.5 /opt/java-current
    # Update: ln -sfn /opt/java-21.0.1 /opt/java-current
    # Applications use /opt/java-current without knowing version
```

---

### Inode Exhaustion

```
Problem: disk has free space but no free inodes!
  
  "No space left on device" despite df showing space available
  New files cannot be created: no inodes left
  
  Check inode usage:
    df -i
    # Filesystem       Inodes  IUsed  IFree  IUse%  Mounted on
    # /dev/sda1      1310720  1310720    0   100%   /
    # <- 100% inode use = cannot create any new files!
    
    df -h   # may show 40% disk usage (plenty of space)
    
  When does this happen?
    Many small files: Maven local repo, NPM node_modules
    Log files (millions of tiny log files over time)
    Temp files not cleaned up (/tmp, /var/tmp)
    Docker image layers (many small files)
    
  Count files by directory:
    find /var -type f | wc -l         # total file count
    find /var -xdev -type f | cut -d/ -f1-3 | sort | uniq -c | sort -rn
    # Which /var subdirectories have most files?
    
  Fix:
    Delete unneeded files (log rotation, temp cleanup)
    Cannot add inodes without mkfs (reformatting)
    
  Prevention:
    Tune inode allocation at mkfs time:
      mkfs.ext4 -T large /dev/sda1   # fewer, larger files expected
      # -T small: many small files expected (more inodes)
      mkfs.ext4 -N 2000000 /dev/sda1 # explicit inode count
      
    XFS: inodes allocated dynamically (no fixed pool)
    Btrfs: inodes are dynamic (no exhaustion issue)
```

---

### /proc and /sys: Virtual File Systems

```
/proc: process and kernel information (procfs)
  Not stored on disk; kernel generates on-the-fly
  Each process: /proc/PID/ directory
    /proc/PID/cmdline    <- command line
    /proc/PID/maps       <- virtual memory map
    /proc/PID/fd/        <- open file descriptors
    /proc/PID/status     <- process status, memory
    /proc/PID/net/       <- network stats for this process
    
  System information:
    /proc/meminfo        <- memory statistics
    /proc/cpuinfo        <- CPU details
    /proc/loadavg        <- load averages
    /proc/sys/           <- sysctl parameters (writable!)
    
/sys (sysfs): kernel device and driver parameters
  Hardware topology, driver settings, cgroup controls
  /sys/block/sda/queue/scheduler  <- I/O scheduler
  /sys/devices/system/cpu/        <- CPU topology, governors
  /sys/class/net/                 <- network interface config
  
Performance benefit:
  /proc and /sys: no disk I/O; pure memory views
  cat /proc/meminfo is faster than any tool that parses files
  Used by: top, htop, ps, iostat, netstat, lsof internally
  Java: /proc/self/status (memory), /proc/self/fd/ (FD count)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Deleting a file always frees its disk space" | Deleting a file (unlink()) removes the directory entry and decrements the inode link count. Disk space is freed ONLY when link count reaches 0 AND all open file descriptors for that inode are closed. A file being written to by a running process while deleted: disk space NOT freed until the process closes the FD. This is why `lsof | grep deleted` can reveal files consuming significant disk space |
| "A symbolic link has the same permissions as its target" | A symbolic link has its own inode with permissions 0777 (lrwxrwxrwx). However, when you access data THROUGH the symlink, the target file's permissions are checked. The symlink's own permissions are rarely relevant (only for operations directly on the link itself, like `lchown`) |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Inode stores | Metadata (perms, size, timestamps, blocks); NOT filename |
| Filename stored in | Directory entry (name -> inode number mapping) |
| Hard link | Two names, one inode; file lives until all links gone |
| Soft link | Separate inode storing target path; can cross filesystems |
| Inode exhaustion | `df -i` shows 100% IUse; no new files despite free space |
| atime/mtime/ctime | access/modification/change (inode change) |
