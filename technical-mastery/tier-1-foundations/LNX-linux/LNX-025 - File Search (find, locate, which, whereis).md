---
id: LNX-025
title: "File Search (find, locate, which, whereis)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-008
used_by: LNX-026, LNX-024
related: LNX-026, LNX-008, LNX-007
tags: [find, locate, which, whereis, file-search, filesystem, glob, exec]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/lnx/file-search/
---

## TL;DR

Four tools for finding files: `find` (search by name/size/date/type,
real-time, most powerful), `locate` (index-based, fast but stale),
`which` (find a command's executable path in PATH), `whereis` (find
binary, source, and man page for a command). `find` is the one you'll
use most: `find /path -name "*.log" -mtime +30 -delete` (find and
delete logs older than 30 days). Master `find -exec` and `-name`/`-type`
for real system administration.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-025 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | find, locate, which, whereis, file search, exec, mtime, prune |
| **Prerequisites** | LNX-007, LNX-008 |

---

### The Problem This Solves

Where is the Java configuration file that was modified today? Which
version of java is actually running? The application server is out of
disk space but where are the large files? Some log file is eating
all the space but which one? File search is the bread-and-butter of
system administration: finding things you don't remember the location
of, cleaning up old files, and verifying what's installed.

---

### Textbook Definition

**find**: Searches the filesystem hierarchy starting from a specified
directory. Evaluates boolean expressions against each file: name, type,
size, modification time, permissions, owner, etc. Can execute commands
on matched files (`-exec`). Always current (no cache).

**locate**: Uses a pre-built database (updated by `updatedb`) to quickly
find filenames matching a pattern. Very fast but the database may be
hours or days old. Not suitable when you need to find recently created files.

**which**: Searches directories in `$PATH` and returns the first
occurrence of the specified command name. Shows you exactly which binary
will run when you type a command.

**whereis**: Finds the binary, source files, and man page sections
for a command. More comprehensive than `which`.

---

### Understand It in 30 Seconds

```bash
# find - most powerful, most used:
find /var/log -name "*.log"             # by name
find /tmp -type f -mtime +7 -delete     # delete files >7 days old
find / -name "application.properties"  # find config file (root search)
find /opt -name "*.jar" -size +100M     # large jar files
find . -type f -newer reference.file   # files newer than reference
find /var/log -name "*.log" -exec wc -l {} \;  # count lines in each log
find . -name "*.java" | xargs grep "TODO"       # search content

# locate - fast, uses index:
locate nginx.conf           # find nginx config (from index)
updatedb                    # update the locate database (as root)
locate -i "*.XML"           # case-insensitive search

# which - find command in PATH:
which java                  # where is the java binary?
which -a java               # all java binaries in PATH
which python3               # which python3 is used?

# whereis - more detail:
whereis java                # binary + man page location
whereis -b nginx            # binary only
```

---

### First Principles

**find vs locate: pull vs push:**
`find` traverses the filesystem RIGHT NOW - every search is current but
costs I/O. `locate` reads a pre-built index (typically `/var/lib/mlocate/mlocate.db`)
- fast but stale. updatedb runs via cron (typically daily). If a file was
created after the last updatedb run, `locate` won't find it.

**why `which` only shows one path:**
`which` searches `$PATH` directories in order and returns the FIRST match.
If you have two versions of java (/usr/bin/java and /usr/local/java/bin/java),
`which java` shows whichever PATH entry comes first. This is exactly why
understanding PATH order matters (LNX-012). `which -a java` shows all.

**find's expression model:**
`find` uses a boolean expression model:
```
find /path [options] [expression]

-name "*.log"   matches files whose name ends in .log
-type f         matches regular files
-size +100M     matches files larger than 100MB
-mtime +30      matches files modified more than 30 days ago
-and            logical AND (default between expressions)
-or             logical OR
-not            logical NOT
-exec cmd {} \; executes cmd for each match ({} = file, \; = end of cmd)
-exec cmd {} +  executes cmd once with all matches as arguments (faster)
```

---

### Thought Experiment

Disk is 95% full. You have 5 minutes before the application crashes.
How do you find and fix the problem?

```bash
# Step 1: where is the space used?
df -h /               # see overall usage by filesystem

# Step 2: narrow down to largest directories
du -sh /* 2>/dev/null | sort -rh | head -20
# Then:
du -sh /var/* 2>/dev/null | sort -rh | head -10
du -sh /var/log/* 2>/dev/null | sort -rh | head -10

# Step 3: find the actual large files
find /var/log -type f -size +500M -ls

# Step 4: find recently grown files
find /var/log -type f -newer /var/log/syslog -ls

# Step 5: fix it
# Option A: truncate without downtime (don't delete open files!)
> /var/log/myapp/debug.log   # empties file without removing it
# Option B: delete old rotated logs
find /var/log/myapp -name "*.log.*" -mtime +7 -delete

# Step 6: prevent recurrence
# (configure log rotation - LNX-069)
```

---

### Mental Model / Analogy

`find` is like a **smart search engine for your filesystem:**

```
find /var/log           = "search in this directory"
-name "*.log"           = "that match this pattern"
-type f                 = "and are regular files (not directories)"
-mtime +30              = "and haven't been modified in 30+ days"
-size +100M             = "and are larger than 100MB"
-exec gzip {} \;        = "and compress each one"

Each filter NARROWS the results.
All filters combined with AND by default.
```

vs locate = phone book lookup (fast, but printed last night)
vs which = "which janitor's closet is first in my path?"

---

### Gradual Depth - Five Levels

**Level 1:**
`find /path -name "filename"` and `which command`. Find config files
by name. Know which binary runs. That's 80% of everyday use.

**Level 2:**
`-type f` (file), `-type d` (directory), `-type l` (symlink). `-mtime`
(days), `-mmin` (minutes). `-size +N M/G/k`. `-exec cmd {} \;` vs
`-exec cmd {} +`. `-delete` shorthand for `-exec rm {} +`.
`find . -name "*.tmp" -delete` = one-liner cleanup.

**Level 3:**
`-maxdepth N` to limit depth. `-prune` to skip directories:
`find / -path /proc -prune -o -name "*.conf" -print` (skip /proc for speed).
`-newer file` (newer than reference). `-user username` and `-group groupname`.
`-perm /4000` for setuid files (security auditing).
`find / -perm /4000 -ls 2>/dev/null` = find all SUID binaries.

**Level 4:**
`-printf` format strings for custom output. `-print0` + `xargs -0` for
filenames with spaces. `find` as input to complex pipelines:
`find . -name "*.java" -print0 | xargs -0 grep -l "TODO"` (files with TODO).
Multiple `-exec`: `find . -type f -exec ls -lh {} \; -exec md5sum {} \;`.
Performance: `find /` is I/O intensive; localize searches. Use `-maxdepth`
aggressively.

**Level 5:**
Security auditing with find: `find / -perm -4000 -type f` (SUID),
`find / -perm -2000 -type f` (SGID), `find / -nouser -o -nogroup` (orphan files),
`find / -writable -type d 2>/dev/null` (world-writable dirs). Container image
analysis: `find / -newer /reference_timestamp` to see what changed.
Forensics: `find / -atime -1 -type f 2>/dev/null` (accessed in last 24h).

---

### Code Example

**BAD - common find mistakes:**
```bash
# BAD 1: searching entire / filesystem when you know the location
find / -name "application.properties"
# Scans everything including /proc, /sys, /dev (takes forever + errors)

# BETTER:
find /opt /etc /home -name "application.properties" 2>/dev/null

# BAD 2: using -exec without {} +:
find /tmp -name "*.tmp" -exec rm {} \;
# Calls rm once per file (slow for thousands of files)

# BETTER: -exec with {} + (calls rm once with all files)
find /tmp -name "*.tmp" -exec rm {} +
# Or even: -delete (most efficient)
find /tmp -name "*.tmp" -delete

# BAD 3: piping find to rm (breaks on spaces in filenames)
find /logs -name "*.log" | xargs rm
# Breaks if filename contains spaces!

# GOOD: use -print0 and xargs -0
find /logs -name "*.log" -print0 | xargs -0 rm
# Or just: find /logs -name "*.log" -delete

# BAD 4: deleting open files (breaks running applications)
find /var/log/myapp -name "*.log" -delete
# App may still have the file open - deletes directory entry but
# disk space isn't freed until app closes the file!

# GOOD: truncate instead of delete for open log files
find /var/log/myapp -name "*.log" -exec truncate -s 0 {} \;
# Or use logrotate with copytruncate option for live logs
```

**GOOD - real-world find examples:**
```bash
# Find all Java heap dumps (large hprof files) and list by size:
find /opt /tmp /var -name "*.hprof" -ls 2>/dev/null | sort -k 7 -rn

# Find config files modified in the last 10 minutes (post-deploy check):
find /etc/myapp /opt/myapp -name "*.properties" -mmin -10 -ls

# Find and compress logs older than 30 days (preserving newer ones):
find /var/log/myapp -name "*.log" -mtime +30 \
    -exec gzip {} \;

# Find files not owned by expected user (security check):
find /opt/myapp -not -user myapp -ls 2>/dev/null

# Find SUID binaries (security audit):
find / -perm /4000 -type f -ls 2>/dev/null

# Find duplicate jars (by name pattern):
find /opt -name "*.jar" -printf "%f\n" | sort | uniq -d

# List all Java versions installed:
find / -name "java" -type f 2>/dev/null \
    -exec file {} \; | grep -i "executable"
which -a java    # simpler: find java in PATH
```

---

### find Expression Reference

```
TYPE TESTS:
  -type f    regular file
  -type d    directory
  -type l    symbolic link
  -type p    named pipe
  -type s    socket
  -type b    block device

TIME TESTS:
  -mtime N   modified exactly N days ago
  -mtime +N  modified more than N days ago (older)
  -mtime -N  modified less than N days ago (newer)
  -mmin N    same, but in minutes
  -newer file  modified more recently than file

SIZE TESTS:
  -size N[ckMG]  exactly N units
  -size +NM      more than N megabytes
  -size -NM      less than N megabytes

PERMISSION TESTS:
  -perm 644     exactly these permissions
  -perm -644    at least these permissions (all bits set)
  -perm /4000   any of these bits set (SUID = 4000)

ACTIONS:
  -print   print filename (default action)
  -print0  print + null separator (xargs -0 compatible)
  -delete  delete matched files
  -ls      detailed listing (like ls -l)
  -exec cmd {} \;   run cmd once per file
  -exec cmd {} +    run cmd once with all files

OPERATORS:
  [expr1] [expr2]    implicit AND
  [expr1] -and [expr2]
  [expr1] -or [expr2]
  -not [expr]        or: ! [expr]
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "locate is always fine for finding files" | locate reads a database that is updated periodically (typically once a day). Files created after the last `updatedb` run will NOT be found. For recently created files, always use `find`. |
| "which finds all versions of a command" | `which` returns only the FIRST match in PATH. Use `which -a` to see all. Also: `type -a java` in bash shows functions and aliases too. |
| "find -name is case-sensitive" | Yes, `-name` is case-sensitive. For case-insensitive: use `-iname`. This catches files named README.md that you search for as readme.md. |
| "`find . -name` searches from root" | No - `find .` searches from the CURRENT directory. `find /` searches from root. Forgetting the path is a common mistake: `find -name "*.conf"` without a path may behave unexpectedly. |
| "find is too slow for everyday use" | find on a local filesystem is fast for targeted searches. It's slow when searching very large trees (like `/`) or slow network filesystems. Use `-maxdepth`, specify the nearest known parent directory, and use `-prune` to skip /proc, /sys, /dev. |

---

### Failure Modes & Diagnosis

**"find: '/proc/...': Permission denied" floods:**
```bash
# Problem: find / generates massive stderr output
find / -name "*.conf"   # Permission denied for /proc, /sys, etc.

# GOOD: redirect stderr to /dev/null
find / -name "*.conf" 2>/dev/null

# BEST: exclude noisy filesystems explicitly
find / -path /proc -prune \
       -o -path /sys -prune \
       -o -path /dev -prune \
       -o -name "*.conf" -print 2>/dev/null
```

**Disk space not freed after deleting large files:**
```bash
# Problem: deleted a large log file but disk is still full
df -h /    # still 95% full

# Diagnosis: the file is still open by a process
lsof | grep deleted    # find processes with deleted open files

# The fix options:
# 1. Restart the process (it will close the file handle)
#    systemctl restart myapp
# 2. Truncate rather than delete:
#    > /var/log/myapp/app.log    (empties file, keeps it open OK)
# 3. Find the FD and truncate via /proc:
lsof | grep deleted | grep myapp.log
# Shows: java  1234  ... /var/log/myapp/app.log (deleted)
# PID=1234, FD=12
truncate -s 0 /proc/1234/fd/12   # truncate the open file descriptor
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-008 (Files and Directories)

**Builds on this:**
LNX-026 (grep - search within files), LNX-024 (Shell Scripting)

**Related:**
LNX-010 (Permissions), LNX-014 (Process Basics)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `find /path -name "*.log"` | Find by name pattern |
| `find . -type f -mtime +30` | Files older than 30 days |
| `find . -size +100M` | Files larger than 100MB |
| `find . -name "*.tmp" -delete` | Find and delete |
| `find . -exec ls -la {} \;` | Execute per file |
| `find . -exec ls -la {} +` | Execute once, all files |
| `find . -print0 \| xargs -0` | Handle spaces in names |
| `which command` | Where is a command binary |
| `which -a command` | All occurrences in PATH |
| `locate filename` | Fast index-based search |
| `updatedb` | Refresh locate database |
| `whereis command` | Binary + man page location |

**3 things to remember:**
1. `find /path` not `find /` - narrow the search to avoid /proc, /sys overhead
2. `find -exec cmd {} +` (not `\;`) for performance - one command call, all files
3. `locate` is stale - for recently changed files, always use `find`

---

### Transferable Wisdom

`find -exec` is the prototypical "find matching things and do work on them"
pattern. This concept appears everywhere: Ansible when-filter, Kubernetes
label selectors, SQL WHERE clauses, stream filtering in Java Streams
(`stream.filter(...).forEach(...)`). The pattern: declare what you're looking
for, declare what to do with matches. find was doing this in 1971.

The `-prune` pattern (exclude directories from traversal) parallels
`.gitignore` (exclude paths from git), `dockerignore` (exclude from
build context), `findbugs` ignore paths, and search tool exclusions.
Understanding how to tell a recursive tool "skip this subtree" is a
universally applicable skill.

---

### The Surprising Truth

`find` was included in UNIX Version 1 (1971). It's older than C (the
language was formalized in 1972). The `-exec` syntax (with `{}` and
`\;`) has been exactly the same for over 50 years. The reason `\;` is
needed (rather than just `;`) is that `;` has special meaning to the
SHELL (end of command) and must be escaped from shell interpretation
so find receives it as-is. Similarly, `{}` needs quoting in some shells.
These 50-year-old syntactic quirks are still the most common source of
find-exec confusion today. Alternative: `find . -name "*.log" | xargs cmd`
avoids `\;` entirely, but breaks on filenames with spaces (use `-print0`
and `xargs -0` to handle this properly).

---

### Mastery Checklist

- [ ] Can find files by name, type, size, and modification time
- [ ] Can execute commands on found files with -exec
- [ ] Can use which to identify which binary will run for a command
- [ ] Can use locate for fast searches and understand its staleness
- [ ] Can use find to identify disk space hogs on a full filesystem

---

### Think About This

1. You run `find /opt/app -name "*.jar" -delete` on a production server
   but the application is still running and has some of these JARs in
   its classpath (loaded at startup). Does deleting them crash the running
   application? Why or why not? What happens when the application is
   restarted?

2. `find / -perm /4000 -type f 2>/dev/null` finds all SUID binaries on
   the system. Why are SUID binaries a security concern? Which SUID
   binaries are legitimate (expected on a standard system)? How would
   you use this command as part of a security audit?

3. You need to find all `.java` files in a large project that contain
   the string "TODO" using both `find -exec grep` and `find | xargs grep`.
   What are the performance and correctness differences between these
   approaches? How does `-print0` and `xargs -0` solve the filename
   space problem, and when does it matter?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you find all files larger than 1GB on a Linux filesystem?
A: `find / -type f -size +1G -ls 2>/dev/null`. Breakdown: `/` = start from root, `-type f` = regular files only (not directories or symlinks), `-size +1G` = larger than 1 gigabyte (`+` means "more than", `G` = gigabytes), `-ls` = show detailed listing with size in KB (more useful than just filename), `2>/dev/null` = suppress "Permission denied" errors. For practical disk space investigation, pair with `du`: first use `du -sh /* 2>/dev/null | sort -rh | head -20` to find which directories are largest, then use `find` to find the specific files. Limiting the path (`find /var` instead of `find /`) significantly speeds up the search.

**Intermediate:**
Q: What is the difference between `find -exec rm {} \;` and `find -exec rm {} +` and when would you use each?
A: Both execute `rm` on matched files, but: `-exec rm {} \;` calls `rm` once per file (N find matches = N `rm` invocations). `-exec rm {} +` collects all matched files and calls `rm` once with all of them as arguments (one `rm` invocation with multiple arguments). Performance: for 10,000 files, `\;` spawns 10,000 rm processes. `{}+` spawns one (or a few if the argument list exceeds ARG_MAX). For most use cases: `{}+` is vastly faster and preferred. Use `\;` only when you need to run a different command for each file (where order or file-by-file behavior matters), or when the command can only accept one argument at a time. For file operations (rm, gzip, chmod): always use `{}+` or `-delete`. Also: `find . -name "*.tmp" -delete` is even simpler than `-exec rm {} +` for deletion.

**Expert:**
Q: A production server disk is full but you can't find large files with find. The application is running but logs show no writes. What else could be causing the disk to appear full?
A: Several possibilities: (1) Deleted files still open: a process deleted a large log file but still has it open. The filesystem entry is removed but the inode and data blocks are held until the file descriptor is closed. `lsof | grep deleted` shows these. Fix: restart the process or truncate via `/proc/PID/fd/N`. (2) Filesystem reserved blocks: ext4 reserves 5% of blocks for root by default. `df -h` shows full but root can still write. Check with `tune2fs -l /dev/sda1 | grep "Reserved block"`. Adjust with `tune2fs -m 1 /dev/sda1` (1% reserved). (3) Many small files filling inode table: inode table is a fixed size. `df -i /` shows inode usage. A directory with millions of tiny temp files (like PHP sessions, mail queue) can exhaust inodes while disk usage appears low. Fix: `find /tmp -type f -mtime +1 -delete`. (4) Filesystem corruption: partially allocated blocks from incomplete writes. Run `fsck` (unmounted). (5) Docker or container storage: containers may use a loop device mounted separately. `df -h` might not show the container storage pool. Check with `docker system df`.
