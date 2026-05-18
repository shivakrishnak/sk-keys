---
id: LNX-035
title: "File Links (hard links, symbolic links)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-008, LNX-010
used_by: LNX-046, LNX-061
related: LNX-046, LNX-007, LNX-008
tags: [hard-link, symbolic-link, symlink, ln, inode, filesystem, link, readlink]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/lnx/file-links/
---

## TL;DR

Linux has two link types. **Hard link**: another name for the same file
(same inode, same data). Deleting any hard link doesn't delete the file
until ALL hard links are removed. **Symbolic link (symlink)**: a pointer
to a path (like a Windows shortcut). Can cross filesystems, can point to
directories, can become dangling (pointing to nothing). Create:
`ln target newlink` (hard), `ln -s target newlink` (symlink). Identify:
`ls -la` shows symlinks with `->`. Production use: version management
(`/usr/local/java -> /usr/local/java-21.0.2`), hot-swappable configs,
current-build pointers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-035 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | hard link, symlink, symbolic link, ln, inode, filesystem links |
| **Prerequisites** | LNX-007, LNX-008, LNX-010 |

---

### The Problem This Solves

You have two applications that expect a library at different paths:
`/lib/libssl.so.1.1` and `/lib/libssl.so`. Rather than duplicating the
file (wasting space, getting out of sync), a symlink makes `/lib/libssl.so`
point to `/lib/libssl.so.1.1`. Application upgrades: atomically switch
`/opt/myapp/current` symlink from `v1.0` to `v2.0` without downtime.
Log management: standard path for logs pointing to the actual log location.

---

### Textbook Definition

**Inode**: A data structure that stores file metadata (permissions,
ownership, timestamps, pointers to data blocks). Each file has one inode,
identified by an inode number. The inode doesn't contain the filename.

**Hard link**: A directory entry that maps a filename to an inode. Multiple
directory entries (hard links) can map to the same inode. The file is
deleted when the inode's link count reaches zero.

**Symbolic link (symlink)**: A special file whose contents are a path
string. When accessed, the kernel follows the path to find the actual file.
Unlike hard links: can point to directories, can cross filesystem boundaries,
can be dangling (target doesn't exist).

---

### Understand It in 30 Seconds

```bash
# Create hard link:
ln original.txt hardlink.txt
# Both names point to the SAME file (same inode)

# Create symbolic (soft) link:
ln -s /opt/myapp-v2.1/ /opt/myapp/current
# current -> /opt/myapp-v2.1/ (pointer to path)

# Identify links:
ls -la /opt/myapp/
# drwxr-xr-x 5 myapp myapp 4096 Jan 15 14:00 myapp-v2.1/
# lrwxrwxrwx 1 myapp myapp   17 Jan 15 14:00 current -> /opt/myapp-v2.1/
# ^                                             ^        ^ target

# Check where a symlink points:
readlink /opt/myapp/current     # output: /opt/myapp-v2.1/
readlink -f /opt/myapp/current  # resolve all symlinks (canonical path)

# See inode numbers (hard links share an inode):
ls -lai file1.txt hardlink.txt
# 1234567 -rw-r--r-- 2 user user 100 file1.txt
# 1234567 -rw-r--r-- 2 user user 100 hardlink.txt
# Same inode (1234567), link count = 2

# Find all hard links to an inode:
find / -inum 1234567 2>/dev/null

# Remove a symlink:
rm /opt/myapp/current    # remove the symlink (not the target!)
unlink /opt/myapp/current  # same thing

# Atomic symlink switch (zero downtime version switch):
ln -sfn /opt/myapp-v3.0/ /opt/myapp/current
# -f = force (overwrite existing), -n = treat destination as link not dir
```

---

### First Principles

**Filesystem structure:**
```
Filesystem:
  Directory entries: [filename] -> [inode number]
  Inodes: [inode number] -> [metadata + data block pointers]
  Data blocks: [actual file content]

Hard link:
  file1.txt -> inode 1000 -> data: "Hello World"
  file2.txt -> inode 1000 -> (same data!)
  Link count: 2 (how many directory entries point to this inode)
  
  Delete file1.txt: link count -> 1. Inode still alive.
  Delete file2.txt: link count -> 0. Inode and data freed.

Symbolic link:
  myapp -> inode 2000 -> content: "/opt/myapp-v2.1/"
  The symlink is its own inode containing just a path string.
  When you access myapp/: kernel reads path string, follows it.
  Delete myapp: only removes the symlink inode. Target unchanged.
  Delete /opt/myapp-v2.1/: symlink becomes "dangling" (dead link).
```

**Why hard links can't cross filesystems:**
Inode numbers are local to a filesystem. `/dev/sda1` has its own inode
number space; `/dev/sdb1` has its own. A hard link on `/dev/sda1` to an
inode number on `/dev/sdb1` would be meaningless - the numbers are not
globally unique. Symlinks work across filesystems because they store a
PATH (text), not an inode number.

**Why hard links can't point to directories:**
(Mostly) they can't because it would create cycles in the filesystem graph,
breaking tools like find and tar that traverse directory trees. (Exception:
`.` and `..` are hard links to the current and parent directories, maintained
by the filesystem itself.)

---

### Thought Experiment

Zero-downtime version deployment using symlinks:

```bash
# Initial setup:
/opt/myapp/
    v1.0/   (old version)
    v2.0/   (new version, just deployed)
    current -> v1.0/   (symlink, what app reads config from)

# Application reads config from /opt/myapp/current/config/

# Atomic switch (one operation, no downtime window):
ln -sfn /opt/myapp/v2.0/ /opt/myapp/current
# On Linux: ln -sf creates a new symlink atomically using rename(2)
# Programs accessing /opt/myapp/current/ DURING the switch:
# - They already have an open file descriptor to v1.0 files
# - New requests get v2.0
# - There is no moment where current is undefined

# If v2.0 is broken: instant rollback
ln -sfn /opt/myapp/v1.0/ /opt/myapp/current
# One command, instant switch back
```

This is the deployment pattern used by Capistrano, Ansible, and many
CI/CD systems. The symlink switch is atomic at the kernel level.

---

### Mental Model / Analogy

```
File data:   [actual book content in a library]
Inode:       [library catalog entry: author, date, pages, shelf location]
Hard link:   [multiple catalog cards pointing to the SAME entry]
             - "War and Peace" and "Voyna i mir" both find the same book
             - Removing one card doesn't remove the book
Symlink:     [a "see also:" card that points to another card's location]
             - "Current Version" card says "look in section 2.1"
             - If section 2.1 is moved, the card is outdated (dangling)
             - But the card itself is a separate thing from what it references

Hard link properties:
  - Same book (data), same catalog entry (inode)
  - Removing one name doesn't remove the book
  - Cannot point to a different library's books (no cross-filesystem)
  
Symlink properties:
  - A separate card that REFERS to another location
  - Can be a "see also: other library" (cross-filesystem)
  - Can become outdated if the referred location moves (dangling link)
  - The card itself can have different permissions than the book
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ln -s target linkname` creates a symlink. `ls -la` shows symlinks
with `->`. `readlink target` shows where it points. Common use: version
pointers like `java -> java-21`. That's 80% of everyday use.

**Level 2:**
Hard links: `ln source dest` (no `-s`). Same inode, same data. Link count
in `ls -la` second column. `find -inum` to find all hard links. Dangling
symlinks: `find /path -type l -! -e` (links that don't resolve).
`ln -sfn` for atomic symlink update. Permissions on symlinks are always
`lrwxrwxrwx` (777) - the actual permissions are on the TARGET.

**Level 3:**
`realpath /path/to/symlink` = fully resolved path (resolves all symlinks).
`stat file` = full inode metadata including link count.
Recursive copies with symlinks: `cp -P` (preserve symlinks), `cp -L` (follow).
tar: `tar --dereference` includes symlink targets, not the symlinks themselves.
rsync: `rsync -l` (copy symlinks as symlinks), `rsync -L` (follow symlinks).

**Level 4:**
Filesystem links in containers: Docker image layers use hard links extensively
for sharing files between layers (content-addressable storage). `overlayfs`
uses hard links in upper/lower layers. Package managers use hard links to
deduplicate files across packages. `cp --link` creates hard links instead
of copies (instant "copy" with no additional space).

**Level 5:**
`/proc/self` is a symlink to `/proc/PID` of the current process.
`/dev/stdin` is a symlink to `/proc/self/fd/0`. `/etc/alternatives`
(Debian update-alternatives): a system of symlinks that manages multiple
installed versions of programs (java, python, etc.) with an admin interface.
`update-alternatives --set java /usr/lib/jvm/java-21-openjdk/bin/java`
atomically switches which java version is "default" via symlinks.

---

### Code Example

**BAD - symlink pitfalls:**
```bash
# BAD 1: creating symlink with wrong order (target and link reversed)
ln -s mylink.txt /path/to/original.txt
# Created a symlink called original.txt pointing to mylink.txt
# That's the OPPOSITE of what was intended!
# Correct: ln -s /path/to/original.txt mylink.txt
# Order: ln -s TARGET LINKNAME (like "create LINKNAME -> TARGET")

# BAD 2: rm with trailing slash on a symlink to directory
rm current/    # tries to delete the directory CONTENTS, not the symlink!
unlink current   # CORRECT way to remove a directory symlink
rm current       # also works (no trailing slash)

# BAD 3: not checking for dangling symlinks
ls /opt/myapp/config  # shows config -> /etc/myapp/config.yaml
# But /etc/myapp/config.yaml was deleted last week!
ls -la /opt/myapp/config  # shows dangling symlink (red in some terminals)
cat /opt/myapp/config  # "No such file or directory"
# Find all dangling symlinks in a directory:
find /opt/myapp -type l ! -e 2>/dev/null  # links that don't exist
```

**GOOD - deployment with symlinks:**
```bash
# Production version management:
DEPLOY_DIR="/opt/myapp"
VERSION="2.3.1"

# Deploy new version (doesn't affect current):
mkdir -p "${DEPLOY_DIR}/${VERSION}"
tar xzf "myapp-${VERSION}.tar.gz" -C "${DEPLOY_DIR}/${VERSION}"

# Verify new version before switching:
"${DEPLOY_DIR}/${VERSION}/bin/myapp" --version

# Atomic switch:
ln -sfn "${DEPLOY_DIR}/${VERSION}" "${DEPLOY_DIR}/current"
# current -> /opt/myapp/2.3.1  (atomic, zero-downtime)

# Reload application to pick up new code:
systemctl reload myapp    # if app hot-reloads
# OR:
systemctl restart myapp   # if restart needed

# Verify:
readlink -f "${DEPLOY_DIR}/current"   # should show 2.3.1 path

# Keep last 3 versions for rollback:
ls -1t "${DEPLOY_DIR}" | grep -v current | tail -n +4 | \
    xargs -I{} rm -rf "${DEPLOY_DIR}/{}"

# Instant rollback:
rollback() {
    local previous
    previous=$(ls -1t "${DEPLOY_DIR}" | grep -v current | head -2 | tail -1)
    ln -sfn "${DEPLOY_DIR}/${previous}" "${DEPLOY_DIR}/current"
    echo "Rolled back to: ${previous}"
}
```

---

### Comparison Table

| Feature | Hard Link | Symbolic Link |
|---------|-----------|---------------|
| Creates new inode | No (shares inode) | Yes (new inode with path) |
| Cross-filesystem | No | Yes |
| Point to directory | No (usually) | Yes |
| Survives target deletion | N/A (IS the target) | Becomes dangling |
| Shows original path | No (indistinguishable) | Yes (readlink) |
| Type in ls -la | `-` (same as file) | `l` (link) |
| Permissions on link | Same as inode | Always 777 (follows target) |
| Link count | Shown in inode | Symlink has its own count |
| Common use | Backup dedup, inode sharing | Version management, config |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Deleting the symlink deletes the target file" | Deleting a symlink (`rm symlink`) removes only the symlink itself - the target file is unchanged. Think: tearing up a "see also" card doesn't destroy the book it refers to. `rm -rf directory_symlink/` (with trailing slash) is dangerous - it deletes the TARGET directory contents, not the symlink. |
| "Hard links waste no space; symlinks do" | Both the symlink and hard link add minimal filesystem overhead (one directory entry). Hard links truly share data blocks with zero duplication. Symlinks have their own inode containing the path string (small - usually stored inline in the inode for short paths). For most purposes: both are effectively "free." |
| "symlink permissions are what matter" | Symlinks always show `lrwxrwxrwx` (permissions 777). This is misleading - the permissions that ACTUALLY control access are the TARGET FILE's permissions. Symlink permissions are largely ignored by Linux (except on some BSD systems). |
| "readlink gives the absolute path to the target" | `readlink` gives exactly what's stored in the symlink - which could be relative (`../configs/app.conf`) or absolute (`/etc/myapp/app.conf`). `readlink -f` or `realpath` resolves the full canonical absolute path. |
| "You can hardlink a file to another filesystem" | Hard links cannot cross filesystem boundaries because inode numbers are filesystem-local. This is why NFS hard links often don't work correctly across client/server. Use symlinks for cross-filesystem references. |

---

### Failure Modes & Diagnosis

**Dangling symlink causes mysterious "file not found":**
```bash
# Application: "FileNotFoundException: /opt/myapp/config/app.properties"
# But the file exists (you can see it in ls /opt/myapp/config/)

# Diagnosis:
ls -la /opt/myapp/config/
# Output: lrwxrwxrwx ... app.properties -> /etc/myapp/app.properties

readlink /opt/myapp/config/app.properties
# Output: /etc/myapp/app.properties

ls /etc/myapp/app.properties
# ls: cannot access '/etc/myapp/app.properties': No such file or directory
# DANGLING SYMLINK: the target was moved/deleted

# Fix:
ln -sf /new/location/app.properties /opt/myapp/config/app.properties

# Find all dangling symlinks:
find /opt/myapp -type l ! -e 2>/dev/null
```

**Circular symlinks causing infinite loop:**
```bash
# A -> B -> A (loop)
ln -s /tmp/b /tmp/a
ln -s /tmp/a /tmp/b
ls /tmp/a/file  # Too many levels of symbolic links

# Kernel limit: 40 symlink dereferences maximum
# readlink -f also fails on circular symlinks
# Fix: identify and break the loop
readlink /tmp/a    # shows b
readlink /tmp/b    # shows a (circular!)
rm /tmp/b && ln -s /actual/path /tmp/b
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-008 (Files), LNX-010 (Permissions)

**Builds on this:**
LNX-046 (Inodes, VFS Layer), LNX-061 (Shared Libraries and Dynamic Linker)

**Related:**
LNX-049 (Filesystem Types)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ln -s target linkname` | Create symlink |
| `ln source hardlink` | Create hard link |
| `ls -la` | Show symlinks with -> |
| `readlink linkname` | Show symlink target |
| `readlink -f linkname` | Canonical path (resolve all) |
| `realpath path` | Same as readlink -f |
| `stat file` | Full inode info |
| `find . -type l` | Find all symlinks |
| `find . -type l ! -e` | Find dangling symlinks |
| `ln -sfn new_target existing_link` | Atomically update symlink |
| `unlink symlink` | Remove symlink |

**3 things to remember:**
1. `ln -s TARGET LINKNAME` - order: target first, new name second
2. `rm symlink/` (trailing slash) = dangerous! Deletes directory contents. Use `unlink symlink` or `rm symlink`
3. Symlink permissions are always 777 - actual access control is on the TARGET

---

### Transferable Wisdom

Symlinks as version management is the foundation of: npm `node_modules/.bin/`
(executable symlinks to installed packages), Python `venv` (symlinks to
interpreter), Debian `update-alternatives` (symlinks to installed versions),
Kubernetes `kubectl` version managers (asdf, k3d, etc.), `/etc/alternatives`
system. The pattern: stable name -> versioned implementation. Change the
pointer, not all the consumers.

Hard links as deduplication appear in: backup tools (Time Machine on macOS,
Borg Backup), Docker image layers (content-addressable storage, hard links
between layers sharing content), npm's hoisting mechanism, container
filesystem copy-on-write (the "lower" layer shares hard links).

---

### The Surprising Truth

The `.` and `..` entries in every directory are hard links. `.` is a hard
link to the current directory's own inode. `..` is a hard link to the parent
directory's inode. This is why directories have a link count of at least 2
(the directory entry itself + the `.` inside). Each subdirectory adds 1 to
the parent's link count (via the `..` entry in the subdirectory). This is
also why you CANNOT create a hard link to a directory manually (only the
kernel can, for the `.` and `..` entries) - it would create ambiguities in
directory traversal. The `link_count` formula: `directories_with_subdirs =
link_count - 2 - (number of direct subdirectories)`. When you count a
directory's hard links with `ls -ld`: `2 + N_subdirs = link_count`. This
was the original way to count subdirectories before `ls -l` showed them.

---

### Mastery Checklist

- [ ] Can create both hard links and symbolic links
- [ ] Can identify which type of link a file is with ls -la
- [ ] Can use readlink to find where a symlink points
- [ ] Can update a symlink atomically with ln -sfn
- [ ] Can find dangling symlinks in a directory tree

---

### Think About This

1. You deploy v2.0 by atomically switching `current -> v2.0`. The
   application opens a config file at startup from `current/config/app.yaml`.
   But the application is still running with v1.0's config after the symlink
   switch. Why? What must you do to the application process to pick up the
   new config?

2. `rm -rf /opt/myapp/current/` (with trailing slash) and
   `rm /opt/myapp/current` behave very differently. Explain exactly what
   each does. How would you safely remove a symlink to a directory without
   risking deletion of the target directory's contents?

3. When you do `ls -la /etc/alternatives/java`, you might see:
   `java -> /usr/lib/jvm/java-21-openjdk-amd64/bin/java`
   And `ls -la /usr/bin/java` shows:
   `java -> /etc/alternatives/java`
   This is a CHAIN of symlinks. Explain what happens when the system
   runs `java HelloWorld` - trace all the symlink resolutions.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between a hard link and a symbolic link in Linux?
A: Hard link: another directory entry pointing to the SAME inode (same file data). Multiple names for one file. Deleting one name doesn't delete the file until all names are removed (link count reaches 0). Cannot cross filesystems, cannot point to directories. Symbolic link (symlink): a separate file whose content is a path string pointing to another file or directory. Can cross filesystems and point to directories. Can be dangling (if target is moved/deleted). Identified by `l` type in `ls -la` and `->` pointer. Practical difference: hard links are invisible once created (appear identical to regular files). Symlinks are visible (ls shows `->` target). Use hard links for: deduplication (backup systems, package managers). Use symlinks for: version management (`current -> v2.1`), configuration aliases, making one path accessible at multiple locations.

**Intermediate:**
Q: How would you implement zero-downtime application deployment using symlinks?
A: The symlink deployment pattern: (1) Deploy new version to a versioned directory: `mkdir /opt/myapp/v2.1 && tar xzf myapp-v2.1.tar.gz -C /opt/myapp/v2.1`. (2) Run pre-deployment checks on new version. (3) Atomic switch: `ln -sfn /opt/myapp/v2.1 /opt/myapp/current`. On Linux, `ln -sf` uses `rename(2)` syscall which is atomic - there's no instant where `current` is undefined. (4) Signal or restart application to pick up new code: `systemctl reload myapp` (if hot-reload supported) or `systemctl restart myapp`. (5) For rollback: `ln -sfn /opt/myapp/v2.0 /opt/myapp/current && systemctl restart myapp` (one command). Caveats: files that were already opened by the running application retain FDs pointing to the old version (files are referenced by inode, not path). New file opens after the switch resolve to the new version. Truly zero-downtime for config changes requires application support for hot-reload. This pattern is used by Capistrano, Ansible deploy, and many CI/CD tools.

**Expert:**
Q: Explain why Docker images use hard links in their content-addressable storage, and how this relates to container filesystem efficiency.
A: Docker stores image layers in `/var/lib/docker/overlay2/` (overlayfs). Each layer is a directory of files. When multiple images share the same layer (e.g., both use Ubuntu base), Docker avoids duplicating data by using hard links. Content-addressable storage: each layer is identified by a SHA256 hash of its contents. If two images reference the same layer hash, they reference the same directory. Files within that directory can be hard-linked across layer directories - same inode, zero additional storage. `docker system df` vs `df /var/lib/docker` may show apparent discrepancy because hard links count once in df but might appear multiple times in du if you count each reference. The `overlayfs` union filesystem: a container's filesystem has: "lowerdir" (read-only, image layers), "upperdir" (read-write, container's changes), "merged" (the unified view). Hard links in lowerdir are preserved in the overlay view. When you write to a file that exists in lowerdir, overlayfs performs copy-on-write: copies the file to upperdir (now owned exclusively by this container, new inode), modifies there. The lowerdir file (shared with all containers using that layer) is unchanged. This is why: `docker run ubuntu touch /etc/hosts` doesn't affect other containers running ubuntu - it triggers copy-on-write for /etc/hosts only in that container's upperdir.
