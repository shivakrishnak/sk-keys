---
id: LNX-008
title: "Files and Directories (ls, cd, mkdir, rm, cp, mv)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006, LNX-007
used_by: LNX-009, LNX-010
related: LNX-007, LNX-009, LNX-025
tags: [files, directories, ls, cd, mkdir, rm, cp, mv, navigation]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/lnx/files-and-directories/
---

## TL;DR

Six commands handle 80% of file system navigation: `ls`
(list), `cd` (change directory), `mkdir` (create directory),
`rm` (delete), `cp` (copy), `mv` (move/rename). These are
the alphabet of Linux operation. Know their flags and you
can navigate any production server confidently.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-008 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | files, directories, ls, cd, mkdir, rm, cp, mv |
| **Prerequisites** | LNX-006, LNX-007 |

---

### The Problem This Solves

Every production task requires file navigation: checking
logs, editing configs, moving deployment artifacts, cleaning
old files. These six commands are the entry point to all
other Linux work. Getting them wrong (especially `rm -rf`)
can destroy production data. Getting them right builds
muscle memory for confident server management.

---

### Textbook Definition

**ls**: list directory contents
**cd**: change current working directory
**mkdir**: make directories
**rm**: remove files or directories
**cp**: copy files and directories
**mv**: move (or rename) files and directories

All part of GNU coreutils - the basic file utility set
available on every Linux system.

---

### Understand It in 30 Seconds

```
WHERE AM I?
  pwd                    # print working directory: /var/log/nginx

WHAT'S HERE?
  ls                     # list files
  ls -la                 # long format, show hidden files
  ls -lh                 # human-readable file sizes
  ls -lt                 # sorted by time (newest first)

NAVIGATE:
  cd /var/log            # go to /var/log
  cd ..                  # go up one level
  cd ~                   # go to home directory
  cd -                   # go to previous directory

CREATE:
  mkdir mydir            # create directory
  mkdir -p a/b/c         # create nested directories

COPY/MOVE:
  cp file.txt backup.txt           # copy file
  cp -r mydir/ backup/             # copy directory recursively
  mv file.txt /tmp/file.txt        # move file
  mv oldname.txt newname.txt       # rename file

DELETE (CAREFUL!):
  rm file.txt            # delete file (PERMANENT)
  rm -f file.txt         # delete, no error if not exists
  rm -r mydir/           # delete directory recursively
  rm -rf mydir/          # delete directory, force (DANGEROUS)
```

---

### First Principles

**Everything is a file:** In Linux, directories are files
(containing directory entries). Devices are files (/dev/sda).
Sockets are files (/var/run/docker.sock). Pipes are files (|).
All these "files" use the same read/write interface.

**Files have three timestamps:**
- atime: last access time (reading)
- mtime: last modification time (writing)
- ctime: last change time (metadata: permissions, name)

**Directories contain directory entries:**
Each directory entry maps a filename (string) to an inode
number. The inode contains metadata (permissions, size,
timestamps) and pointers to data blocks. Two filenames
can point to the same inode (hard links).

---

### Thought Experiment

You're the new hire on an SRE team. There's a production incident:
Nginx is returning 500 errors. Without knowing these commands
you cannot:
- Navigate to /var/log/nginx to check error logs
- List the log files to find the most recent one
- Check if the config directory exists and has the right files

These commands are pre-requisites for ALL other Linux work.
Think of them as the muscles that all other skills depend on.

---

### Mental Model / Analogy

Linux filesystem commands map exactly to GUI file manager
actions:
```
GUI action              Terminal equivalent
Open folder          -> cd foldername
See what's inside    -> ls
Copy file            -> cp source dest
Move file            -> mv source dest
Delete file          -> rm filename
Create folder        -> mkdir foldername
New file             -> touch filename
Search for file      -> find . -name "filename"

The terminal is the keyboard shortcut for all of these.
Faster, scriptable, available over SSH, no GUI required.
```

---

### Gradual Depth - Five Levels

**Level 1:**
Memorize: ls, cd, mkdir, rm, cp, mv. Use them until muscle memory.
Add: pwd (where am I?), touch (create empty file).

**Level 2:**
Master flags: `ls -lha` (long, hidden, human-readable), `rm -rf`
(recursive force - DANGEROUS), `cp -r` (copy directories),
`mkdir -p` (create parents). Understand . (current dir) and ..
(parent dir) and ~ (home dir).

**Level 3:**
Combine with find: `find /var/log -name "*.log" -mtime +7 -delete`
(delete logs older than 7 days). Combine with xargs: `find . -name
"*.tmp" | xargs rm`. Use ls with sort: `ls -lt` (newest first),
`ls -lS` (largest first). Understand inodes and hard links.

**Level 4:**
Performance at scale: `rm -rf` on directory with millions of files
is slow (one syscall per file). Faster: `find dir -delete` or
`rsync --delete`. Large file copies: `cp --sparse` for sparse files.
`mv` within same filesystem: instant (inode rename); across
filesystems: copies then deletes (slow for large files).

**Level 5:**
Atomic operations: `mv` (rename) is atomic on same filesystem
(one syscall). Use for atomic file replacement: write to tmp,
then mv to target. Database trick: write /tmp/new.db then
`mv /tmp/new.db /data/prod.db` atomically replaces production
file. cp is NOT atomic. Understanding when to use mv vs cp
matters for data consistency in production.

---

### Code Example

**BAD - common dangerous mistakes:**
```bash
# BAD 1: rm -rf on wrong directory (DESTROYS DATA)
cd /var
rm -rf log/    # removes all logs - oops, meant /tmp/log/

# BAD 2: cp without -r for directories
cp mydir/ backup/   # fails silently on some systems
                    # only copies directory contents on others

# BAD 3: mv overwrites without warning
mv important.conf important.conf.bak  # wait, other way around?
mv important.conf.bak important.conf  # overwrites original!
```

**GOOD - safe file operations:**
```bash
# GOOD 1: always verify location before rm
pwd               # verify: /var/log/myapp
ls                # verify: see what's there
rm myapp.log.old  # safe: specific file, not -rf /

# GOOD 2: use -r explicitly for directories
cp -r mydir/ backup_$(date +%Y%m%d)/  # date-stamped backup

# GOOD 3: use -i (interactive) for safety
rm -i important.conf            # asks: "remove important.conf?"
mv -i source.txt dest.txt       # asks if dest exists

# GOOD 4: atomic file replacement pattern
cp myapp.jar /tmp/myapp-new.jar  # copy to temp
# validate the new jar
java -jar /tmp/myapp-new.jar --version
mv /tmp/myapp-new.jar /opt/myapp/myapp.jar  # atomic replace

# GOOD 5: check before deleting large directory
du -sh /var/log/oldapp/    # how big is it? (10GB!)
ls /var/log/oldapp/ | head -5  # what's in it?
rm -rf /var/log/oldapp/    # confident deletion
```

---

### Essential ls Output Format

```
$ ls -la /etc/nginx/
total 56
drwxr-xr-x  4 root root 4096 Jan 15 10:30 .
drwxr-xr-x 98 root root 4096 Jan 15 10:30 ..
-rw-r--r--  1 root root  664 Jan 10 09:15 nginx.conf
drwxr-xr-x  2 root root 4096 Jan 10 09:15 sites-available
drwxr-xr-x  2 root root 4096 Jan 15 10:30 sites-enabled
lrwxrwxrwx  1 root root   34 Jan 15 10:30 default.conf -> /etc/nginx/sites-enabled/default
^          ^ ^    ^    ^    ^              ^
|          | |    |    |    |              filename (or -> target for symlinks)
|          | |    |    |    last modified
|          | |    |    size in bytes
|          | |    group
|          | owner
|          number of hard links
file type + permissions

File types:
  - = regular file
  d = directory
  l = symbolic link (-> shows target)
  c = character device (/dev/tty)
  b = block device (/dev/sda)
  s = socket
  p = named pipe (FIFO)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`rm -rf` can be undone" | No. rm has no trash/recycle bin in production Linux. Deleted data is gone. Use `rsync` backups or snapshots. |
| "Copying a directory with cp copies everything" | `cp dir/ dest/` fails or behaves unexpectedly. Always use `cp -r dir/ dest/` for recursive directory copy. |
| "`mv` is always instant" | mv across different filesystems requires copying then deleting. `mv /tmp/bigfile.tar /data/` may take minutes. Same filesystem: instant. |
| "ls -l sizes are file sizes" | ls -l shows apparent file size. For disk usage (accounting for block alignment and sparse files): use `du -sh file`. A 1GB sparse file shows 1GB in ls, 0 bytes in du. |
| "Spaces in filenames are unusual" | On Linux: filenames can contain any character except / and null byte. Spaces are valid. Always quote: `rm "my file.txt"` not `rm my file.txt` (deletes "my" and "file.txt"). |

---

### Failure Modes & Diagnosis

**rm -rf accident mitigation:**
```bash
# Prevention:
alias rm='rm -i'    # always ask before deleting

# For truly dangerous operations:
# 1. First, ls to confirm what you're about to delete
ls -la /path/to/delete/

# 2. Use trash-cli instead of rm (sends to trash):
# apt install trash-cli
trash-put /path/to/delete/

# Recovery (if you have snapshots or backups):
# LVM snapshot: lvconvert --merge /dev/vg/snap
# AWS EBS: restore from snapshot in console
# Filesystem with snapshots (BTRFS/ZFS): btrfs subvolume list
```

**Disk full during large file operations:**
```bash
# Check disk space before large operations:
df -h /var/log/   # how much space in /var/log?

# If disk full while copying:
# The partial file is left on disk - must clean up:
ls -la /var/log/backup/   # find partial file
rm /var/log/backup/partial-file.tar  # clean up

# Use --no-overwrite-dir with rsync to be safer:
rsync -av --no-overwrite-dir source/ dest/
```

**Security: world-writable directories:**
```bash
# Find world-writable directories (security risk):
find / -type d -perm -002 -not -path "/proc/*" 2>/dev/null
# These are directories anyone can write to
# Fix:
chmod o-w /path/to/directory  # remove world-write
```

---

### Related Keywords

**Foundational:**
LNX-007 (Filesystem Hierarchy), LNX-010 (File Permissions)

**Builds on this:**
LNX-009 (File Viewing), LNX-025 (File Search),
LNX-035 (File Links)

**Related:**
LNX-046 (Filesystem Internals - inodes), LNX-029 (Archives)

---

### Quick Reference Card

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `ls` | List files | -l (long), -a (hidden), -h (human sizes), -t (time sort) |
| `cd` | Change directory | ~ (home), - (previous), .. (parent) |
| `pwd` | Print working dir | (no flags needed) |
| `mkdir` | Create directory | -p (create parents) |
| `rm` | Delete | -r (recursive), -f (force), -i (interactive/safe) |
| `cp` | Copy | -r (recursive), -p (preserve attributes), -a (archive mode) |
| `mv` | Move/rename | -i (interactive), -n (no overwrite) |
| `touch` | Create empty file | -t (set timestamp) |
| `du` | Disk usage | -sh (summary, human-readable) |
| `df` | Disk free | -h (human-readable) |

**3 things to remember:**
1. `rm` is permanent - no trash - always confirm what you're deleting
2. Quote filenames with spaces: `rm "my file.txt"`
3. `mv` within same filesystem is instant; across filesystems copies then deletes

**Interview angle:**
"How would you atomically replace a configuration file in
production without causing any window where the file is
partially written?" -> Write to a temp file, validate it,
then `mv temp newfile` (rename is atomic on same filesystem).

---

### Transferable Wisdom

The **atomic rename** pattern (`mv` as atomic file replacement)
appears everywhere: database checkpoint files, nginx config
reload, log rotation. The invariant: the file is either the
old version or the new version; never a partial state.
This is how git stores objects atomically in .git/objects/.

The **idempotent mkdir** pattern (`mkdir -p`) appears in
infrastructure code: Ansible, Terraform, Docker. Creating a
directory that already exists should succeed silently. This
principle (idempotency) is fundamental to reliable automation.

---

### The Surprising Truth

`rm` doesn't actually delete file data - it removes the
directory entry (the filename-to-inode mapping). The kernel
only frees the data blocks when the inode's link count reaches
zero AND no process has the file open. This is why `lsof` can
show a deleted file still consuming disk space: a process still
has a file descriptor to the inode. The disk space isn't freed
until that process closes or exits. This is the cause of a
common production puzzle: `du -sh /var/log/` shows 1GB used,
but after `rm *.log`, `df -h` still shows the same disk usage.
Fix: find the process holding the deleted file open with
`lsof | grep deleted` and restart it.

---

### Mastery Checklist

- [ ] Can navigate any Linux filesystem using ls, cd, pwd
- [ ] Can explain why rm is permanent and what alternatives exist
- [ ] Can perform an atomic file replacement using mv
- [ ] Can find disk space discrepancy between du and df
- [ ] Can safely handle filenames with spaces in scripts

---

### Think About This

1. `rm -rf /` would destroy an entire Linux system. Many systems
   have safeguards (`--no-preserve-root` required). But `rm -rf /*`
   (star inside the root directory) on some older systems worked
   without the flag. What exactly happens at the kernel level
   when rm tries to delete /bin/rm while rm is still executing?

2. Docker containers have a copy-on-write filesystem. When you
   run `rm bigfile.txt` inside a container, does disk space on
   the host actually decrease? What happens at the overlay
   filesystem level?

3. `mv` is described as "instant within the same filesystem."
   What is the actual system call involved? Why is it atomic?
   What guarantees atomicity at the kernel level?

**TYPE G:** A production server is 100% full (/var/log takes 95%
of disk space). The application is failing because it can't write
logs. You need to free space immediately without losing critical
recent logs. Design a step-by-step recovery procedure using only
ls, rm, mv, cp, and du.

---

### Interview Deep-Dive

**Foundational:**
Q: What does `rm -rf /var/log/myapp/` do and what can you do if you ran it by mistake?
A: It recursively and forcefully deletes the directory /var/log/myapp/ and all contents. There is no recycle bin or undo. If you ran it by mistake: (1) stop any write activity immediately (stop the application) to prevent data being overwritten; (2) if LVM is in use: check for LVM snapshots with `lvs`; (3) if EBS/cloud storage: restore from the most recent snapshot; (4) if the files were recently deleted, some data recovery tools (extundelete for ext4) may recover inodes not yet overwritten. Prevention: use snapshots before maintenance, use `trash-put` alias instead of rm, and always `ls` before `rm -rf`.

**Intermediate:**
Q: Why might `df -h /var/log` show a filesystem at 90% capacity, but `du -sh /var/log/*` only show files totaling 10% of capacity?
A: Deleted-but-open files. A process has a file descriptor to a log file that was deleted (rm removed the directory entry), but since the process still has the file open, the kernel hasn't freed the disk blocks. The inode still points to the data blocks, and they consume disk space. `du` reports on files reachable via directory entries (the deleted file isn't there). `df` reports actual disk block usage (the blocks are still in use). Fix: find the process holding the file open with `lsof | grep deleted`, then restart that process to close the file descriptor, allowing the kernel to free the blocks.

**Expert:**
Q: Explain the atomic file replacement pattern for production config files and why cp is insufficient.
A: The pattern: (1) write the new version to a temp file in the same filesystem (e.g., `/etc/nginx/nginx.conf.tmp`), (2) validate it (`nginx -t -c /etc/nginx/nginx.conf.tmp`), (3) `mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf`. The `mv` (rename syscall) is atomic on the same filesystem: it either completes or doesn't, with no intermediate state. Any process reading the config file sees either the complete old version or the complete new version - never a partial write. `cp` is NOT atomic: it opens the destination, truncates it, then writes data. A reader during the copy sees a partially written file. This is why nginx, git, and databases all use the write-to-tmp-then-rename pattern for critical file updates. Requires: source and destination on the same filesystem (otherwise mv copies then deletes, which is not atomic).
