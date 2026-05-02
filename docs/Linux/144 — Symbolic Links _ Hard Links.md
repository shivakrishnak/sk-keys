---
layout: default
title: "Symbolic Links / Hard Links"
parent: "Linux"
nav_order: 144
permalink: /linux/symbolic-links-hard-links/
number: "0144"
category: Linux
difficulty: ★★☆
depends_on: Linux File System Hierarchy, File Permissions (chmod, chown), Users and Groups
used_by: Package Managers (apt, yum, dnf), Shell Scripting, Systemd
related: Linux File System Hierarchy, File Permissions (chmod, chown), tar / gzip / zip
tags:
  - linux
  - os
  - internals
  - intermediate
---

# 144 — Symbolic Links / Hard Links

⚡ TL;DR — A hard link is another name for the same file data (same inode); a symbolic link is a pointer (redirect) to another path — each has fundamentally different semantics for deletion, cross-filesystem use, and dangling references.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A library (`libssl.so.3.0.7`) needs to be accessible at a stable name (`libssl.so.3`) so that programs compiled against the stable name work regardless of minor version updates. Without links, you must copy the library file — wasting disk space and making updates a nightmare (both copies must stay in sync). Or you must recompile all applications every time the library version number changes.

**THE BREAKING POINT:**
You upgrade `libssl` from `3.0.7` to `3.0.8`. Every application that hardcoded `/usr/lib/libssl.so.3.0.7` breaks at runtime. You must track every binary, recompile or patch them. This is unmanageable for a system with hundreds of dynamically linked binaries.

**THE INVENTION MOMENT:**
This is exactly why symbolic links were created. `/usr/lib/libssl.so.3 → libssl.so.3.0.8` acts as an indirection layer. When 3.0.9 ships, the package manager updates the symlink. Every application continues working without recompilation.

---

### 📘 Textbook Definition

In Linux, every file is stored on disk as an **inode** — a data structure containing metadata (permissions, ownership, timestamps) and pointers to data blocks. A **hard link** is a directory entry that directly maps a filename to an existing inode; multiple hard links share the same inode (same file data, same metadata). A **symbolic link** (symlink) is a special file type whose data content is a path string pointing to another file or directory; the kernel transparently follows symlinks during path resolution. Symlinks can cross filesystem boundaries and can be dangling (pointing to a non-existent target).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Hard links are two names for the same file; symlinks are shortcuts that point to another path.

**One analogy:**
> A hard link is like a person with two names on the same ID card — both names are equally valid, and the person exists as long as at least one name is in use. A symbolic link is like a forwarding address label on an empty envelope — it says "find me at this other address", but if that address no longer exists, the label leads nowhere.

**One insight:**
When you delete a file, you're not deleting the data — you're removing one directory entry. The data is freed only when the last hard link (the inode's link count) reaches zero. This is why `rm` is technically "unlink" — it just removes a directory entry.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each file has exactly one inode with a link count starting at 1.
2. Adding a hard link increments the link count; removing decrements it; data is freed when count reaches 0.
3. Symlinks are just files containing a path string; the kernel resolves them during path lookup.
4. Hard links cannot cross filesystem boundaries (inodes are filesystem-local).
5. Hard links cannot point to directories (prevents cycles in the directory tree).

**DERIVED DESIGN:**
The kernel's VFS layer resolves path components left to right. When it encounters a symlink, it reads its content and inserts that path into the resolution process. This happens transparently — applications never know a symlink was followed unless they explicitly use `lstat()` instead of `stat()`.

Hard links share metadata — there is only one inode. Changing permissions on `/data/file.txt` also changes permissions on `/backup/file.txt` if they are hard links to the same inode. This has powerful implications for backup systems (rsync `--link-dest`) where unchanged files can be hard-linked instead of copied.

**THE TRADE-OFFS:**
**Hard link gain:** Zero-cost additional reference, shared metadata, atomic reference counting.
**Hard link cost:** Same-filesystem only, no directories, no dangling state.
**Symlink gain:** Cross-filesystem, can point to directories, human-readable target, can be dangling.
**Symlink cost:** Extra kernel dereference on every path lookup, can dangle if target deleted.

---

### 🧪 Thought Experiment

**SETUP:**
You create a file `/data/report.txt` and want it accessible at `/var/www/reports/report.txt` without duplicating it.

**WHAT HAPPENS WITH a copy:**
Two copies of the file exist. They use 2× disk space. When you update `/data/report.txt`, the copy in `/var/www/reports/` is stale. You must remember to keep them in sync manually. They have independent permission sets.

**WHAT HAPPENS WITH a hard link:**
`ln /data/report.txt /var/www/reports/report.txt` — both paths point to the same inode. Zero extra disk space. Changing the content via either path changes the "same" file. Deleting one path still leaves the data accessible via the other. The file is freed only when both entries are deleted.

**WHAT HAPPENS WITH a symlink:**
`ln -s /data/report.txt /var/www/reports/report.txt` — the symlink file contains the string `/data/report.txt`. The web server follows the symlink transparently to read the content. If `/data/report.txt` is deleted, the symlink becomes dangling — the web server gets "No such file or directory" even though the symlink itself still exists.

**THE INSIGHT:**
Hard links are aliases — they are the same thing. Symlinks are references — they point to a thing. This distinction drives all their different behaviours.

---

### 🧠 Mental Model / Analogy

> Think of files as people with ID numbers (inodes). A hard link is two different entries in a phone book that list the same ID number — same person, two names. A symbolic link is a sticky note that says "for John Smith, call Jane Doe instead" — it redirects lookups. If Jane changes her phone number (path changes), the sticky note is wrong. If Jane stops existing, the note is dangling.

- "ID number" → inode number
- "Phone book entry" → directory entry (dentry)
- "Two entries, same ID" → two hard links, same inode
- "Sticky note redirect" → symlink
- "Wrong sticky note" → dangling symlink

Where this analogy breaks down: a person can be in multiple phone books (cross-filesystem hard link) — but Linux inodes are filesystem-local, so hard links can only appear in the same filesystem's "phone book".

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A hard link is another name for the same file — the data is shared, and the file only disappears when all names are removed. A symbolic link (symlink) is like a shortcut in Windows — it points to another file or folder, and if that target is deleted, the shortcut breaks.

**Level 2 — How to use it (junior developer):**
Create a hard link: `ln original.txt hardlink.txt`. Create a symlink: `ln -s /path/to/target linkname`. Identify symlinks: `ls -la` shows `link -> target`. Verify symlink target: `readlink linkname`. Hard links look identical to the original in `ls` output (same inode number visible with `ls -li`). Use `ls -li` to see inode numbers and verify hard links.

**Level 3 — How it works (mid-level engineer):**
The directory is a mapping of filename → inode number. `ln` (hard link) creates a new filename → same inode mapping and increments the inode's `i_nlink` count. `unlink` (rm) removes the mapping and decrements `i_nlink`; when it reaches 0, the kernel calls the inode's `evict_inode` to free disk blocks. A symlink is a regular file of type `S_IFLNK`; its data is the target path string. The kernel resolves symlinks in path lookups via `follow_link()`, with a loop limit (40 on Linux) to prevent infinite symlink loops.

**Level 4 — Why it was designed this way (senior/staff):**
Hard links are a direct consequence of the inode data model — inodes don't store filenames, directories do. This separation enables the reference counting model with zero overhead. The prohibition on directory hard links prevents reference cycles that would make garbage collection impossible (the Linux kernel uses a separate mechanism — `..` pointers — that creates effectively unavoidable one-direction cycles managed carefully). Symlinks were added later as a practical necessity for library versioning, `PATH` configuration, and cross-device links. The kernel loop limit (40 dereferences) was chosen to allow legitimate chains (e.g., `/usr → /usr/local/versions/2`) while preventing runaway loops.

---

### ⚙️ How It Works (Mechanism)

**Inode and link count model:**
```
┌─────────────────────────────────────────────┐
│  FILESYSTEM INODE MODEL                     │
└─────────────────────────────────────────────┘

Directory entries:        Inode table:
  /data/                  inode #42:
    file.txt ──────────▶  size: 1024 bytes
    backup.txt ────────▶  perms: 0644
                          nlink: 2          ← 2 hard links
  /backup/                owner: user:group
    file.txt ──────────▶  mtime: 2024-01-15
    (same inode #42)      data blocks: [...]

  /link/
    shortcut ──▶ [symlink]  content: "/data/file.txt"
                (own inode #99, type=symlink)
```

**Creating and inspecting links:**
```bash
# Create hard link
ln /data/file.txt /backup/file.txt

# Create symbolic link
ln -s /data/file.txt /var/www/file.txt

# Create symlink to directory
ln -s /var/lib/nginx/html /var/www/html

# Relative symlink (portable — doesn't break on path changes)
cd /var/www
ln -s ../../data/file.txt file.txt  # relative target

# Show inode numbers and link count
ls -li /data/file.txt /backup/file.txt
# Same inode number = hard links to same file

# Show symlink target
readlink /var/www/file.txt
readlink -f /var/www/file.txt  # resolve full chain

# Identify symlinks in directory
ls -la /usr/lib/ | grep '^l'    # lines starting with 'l'

# Find all dangling symlinks in a directory
find /var/www -xtype l          # -xtype l: symlink to missing target

# Find all symlinks
find /usr/lib -type l
```

**Deletion behaviour:**
```bash
# Hard links: file survives until last link is removed
ln file.txt hardlink.txt       # nlink = 2
rm file.txt                    # nlink = 1, data NOT freed
cat hardlink.txt               # still works
rm hardlink.txt                # nlink = 0, data freed

# Symlinks: symlink can survive target deletion
rm /data/file.txt              # target gone
cat /var/www/file.txt          # ERROR: No such file or directory
ls -la /var/www/               # symlink still shows (dangling)
```

**Library versioning pattern:**
```bash
# Package manager creates this structure:
ls -la /usr/lib/ | grep ssl
# libssl.so.3     -> libssl.so.3.0.8   (compatibility symlink)
# libssl.so.3.0.8                      (actual library file)
# libssl.so       -> libssl.so.3       (linker symlink)

# Applications link against libssl.so → follows chain → 3.0.8
# When 3.0.9 ships: update symlink only, no recompile needed
ln -sf libssl.so.3.0.9 libssl.so.3
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  SYMLINK RESOLUTION IN PATH LOOKUP          │
└─────────────────────────────────────────────┘

 open("/var/www/html/index.html", O_RDONLY)
       │
       ▼
 VFS resolves path component by component:
   /  → root dentry
   var → lookup "var" in root → dentry
   www → lookup "www" in var → symlink!
       │  ← YOU ARE HERE (kernel follows symlink)
       ▼
 readlink("/var/www") → "/var/lib/nginx/html"
       │  substitute, continue resolution
       ▼
   lib → lookup "lib" in var → dentry
   nginx → lookup in lib → dentry
   html → lookup in nginx → dentry
   index.html → lookup → inode #7291
       │
       ▼
 open succeeds, fd returned to process
```

**FAILURE PATH:**
Dangling symlink → `open()` returns `ENOENT` (No such file or directory) even though the symlink file itself exists → programs crash with misleading "file not found" error when the real problem is a broken symlink.

**WHAT CHANGES AT SCALE:**
NFS and distributed filesystems complicate symlinks: a symlink containing an absolute path that is valid on Server A may not resolve on Server B if mount points differ. Best practice: use relative symlinks when paths will be accessed from multiple mount points.

---

### 💻 Code Example

**Example 1 — Library versioning (package manager pattern):**
```bash
# Install a new library version
ls /usr/local/lib/
# mylib-1.0.so  mylib-1.1.so

# Create versioned symlinks
ln -sf mylib-1.1.so libmylib.so.1
ln -sf libmylib.so.1 libmylib.so

# Verify chain
readlink -f libmylib.so
# → /usr/local/lib/mylib-1.1.so
```

**Example 2 — Deployment directory switching (zero-downtime):**
```bash
# Deploy new version atomically using symlinks
# /var/www/current → /var/www/releases/v2.1

# New release ready
mkdir -p /var/www/releases/v2.2
rsync -avz build/ /var/www/releases/v2.2/

# Atomic switch: ln -snf atomically replaces symlink
ln -snf /var/www/releases/v2.2 /var/www/current

# Verify
readlink /var/www/current   # → /var/www/releases/v2.2

# Rollback
ln -snf /var/www/releases/v2.1 /var/www/current
```

**Example 3 — rsync incremental backup with hard links:**
```bash
# Space-efficient backup: unchanged files = hard links
PREV=/backup/2024-01-14
TODAY=/backup/2024-01-15

rsync -avz \
  --link-dest="$PREV" \
  /data/ "$TODAY/"

# Result:
# - Changed files: new copies in TODAY
# - Unchanged files: hard links to PREV (zero disk cost)
# - Each day's backup appears complete (browsable)
# - Disk usage = only actual changes
```

**Example 4 — Find and fix dangling symlinks:**
```bash
# Find all dangling symlinks under /var/www
find /var/www -xtype l -print

# Fix: update dangling symlink to new target
ln -sf /new/target/path /var/www/old-link

# Remove all dangling symlinks
find /var/www -xtype l -delete
```

---

### ⚖️ Comparison Table

| Feature | Hard Link | Symbolic Link |
|---|---|---|
| Cross-filesystem | No | Yes |
| Point to directory | No | Yes |
| Can be dangling | No | Yes |
| Survives target deletion | Yes (is the target) | No |
| `stat()` returns | Original file info | Symlink's own info |
| `readlink` | Fails (not a symlink) | Returns target path |
| Extra disk space | Minimal (one dentry) | ~100 bytes (path string) |
| **Best For** | Backups, reference counting | Library versions, deployment |

How to choose: use hard links for space-efficient backups and when you need the data to survive regardless of path; use symlinks for library versioning, deployment current/stable pointers, and cross-filesystem references.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Deleting a hard link deletes the file | Deleting a hard link decrements the link count; the data is freed only when ALL hard links are removed |
| symlinks and hard links waste disk space | Hard links use only ~50 bytes for a directory entry; symlinks use ~100 bytes for the path string — both are negligible |
| A symlink has the same permissions as its target | A symlink has its own permissions (lrwxrwxrwx always shows 777) but these are generally ignored — the target's permissions govern access |
| Hard links are slow because of extra lookup | Hard links are NOT slower — they ARE the same inode; following a symlink adds one extra kernel dereference, hard links add none |
| Removing the original file breaks hard links | There is no "original" with hard links — all are equal references; removal of one doesn't affect others |

---

### 🚨 Failure Modes & Diagnosis

**Dangling Symlink After Deployment**

**Symptom:**
nginx returns 404 for all requests after a deployment; `ls -la /var/www/current` shows the symlink exists but accessing it gives "No such file or directory".

**Root Cause:**
The deployment script deleted the old release directory before updating the symlink, or pointed the symlink to a path that doesn't exist yet.

**Diagnostic Command:**
```bash
# Check if symlink is dangling
readlink /var/www/current
ls -la "$(readlink /var/www/current)"

# Quick: find all dangling symlinks
find /var/www -xtype l
```

**Fix:**
```bash
# Point symlink to the correct existing path
ln -snf /var/www/releases/v2.1 /var/www/current
```

**Prevention:**
Always create and verify the new release directory BEFORE updating the symlink; use atomic `ln -snf` not two-step delete+create.

---

**Symlink Loop (Infinite Recursion)**

**Symptom:**
`ls -la /path` or any path operation hangs or returns "Too many levels of symbolic links".

**Root Cause:**
Two symlinks point to each other: `a → b` and `b → a`. The kernel detects this after 40 hops and returns `ELOOP`.

**Diagnostic Command:**
```bash
readlink -f /path/to/suspected/loop  # shows ELOOP error
namei -l /path/to/link               # traces each link step
```

**Fix:**
```bash
# Remove one of the loop members
rm /path/to/link-b
# Recreate with correct target
ln -s /correct/target /path/to/link-b
```

**Prevention:**
Use `readlink -f` to verify the final resolved path before creating symlinks in automated scripts.

---

**Hard Link Across Filesystem Boundary**

**Symptom:**
`ln /mnt/data/file.txt /home/user/file.txt` fails with "Invalid cross-device link".

**Root Cause:**
Inodes are local to a filesystem; a hard link is a second directory entry pointing to the same inode, which is impossible across different filesystem namespaces.

**Diagnostic Command:**
```bash
df /mnt/data/file.txt /home/user/  # verify they're different devices
stat /mnt/data/file.txt | grep Device
```

**Fix:**
Use a symbolic link instead: `ln -s /mnt/data/file.txt /home/user/file.txt`

**Prevention:**
Use hard links only within the same filesystem; use symlinks for cross-filesystem references.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux File System Hierarchy` — understanding the FHS directory structure is needed to understand where symlinks are used (e.g., `/usr/lib/`, `/etc/alternatives/`)
- `File Permissions (chmod, chown)` — symlinks have their own permission bits; inodes have permission bits; both matter for access control
- `Users and Groups` — ownership (UID/GID) is stored in the inode, shared by all hard links

**Builds On This (learn these next):**
- `Package Managers (apt, yum, dnf)` — package managers extensively use symlinks for library versioning and alternatives
- `Shell Scripting` — scripts create and manage symlinks for deployment, configuration, and versioning
- `Systemd` — systemd unit files use symlinks in `/etc/systemd/system/` to enable/disable services

**Alternatives / Comparisons:**
- `Bind mounts` — mounts a directory at another path; heavier than symlinks but bypass symlink resolution and work differently with containers
- `Copies` — duplicates data; uses 2× disk space; completely independent files after creation
- `tar hard links` — tar preserves hard links using link references in the archive format

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hard link: second name for same inode;    │
│              │ symlink: file whose content is a path     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Library versioning and stable names need  │
│ SOLVES       │ indirection without file duplication      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ rm = unlink: decrements link count;       │
│              │ data freed only when count reaches 0      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Symlinks: library versions, deploy        │
│              │ pointers; hard links: space-efficient     │
│              │ backups (rsync --link-dest)               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hard links across filesystems (use        │
│              │ symlinks); symlinks in NFS with abs paths │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Symlinks: flexible + can dangle vs        │
│              │ hard links: robust + same-fs only         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hard link: same person, two names;       │
│              │  symlink: forwarding address"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ inodes → VFS → bind mounts               │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A container image build copies files from a host directory where many files are hard links to each other (an rsync backup directory). Trace what happens to the hard links when Docker COPY copies them into the image layer — are they preserved as hard links or duplicated? How does this affect image layer size, and what Docker command gives you visibility into this?

**Q2.** An nginx configuration uses a symlink: `/etc/nginx/sites-enabled/myapp → /etc/nginx/sites-available/myapp`. A sysadmin runs `chown -R nginx:nginx /etc/nginx/sites-enabled/` trying to fix permissions. Trace exactly what gets chown'd (the symlink itself, the target, or both), and explain why the result may not match the sysadmin's intention. What flag should they add and what are the security implications?
