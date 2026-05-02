---
layout: default
title: "File Permissions (chmod, chown)"
parent: "Linux"
nav_order: 127
permalink: /linux/file-permissions-chmod-chown/
number: "0127"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy, Users and Groups
used_by: Shell Scripting, SSH, SELinux / AppArmor, Linux Security Hardening
related: Users and Groups, SELinux / AppArmor, Symbolic Links / Hard Links
tags:
  - linux
  - security
  - os
  - foundational
---

# 127 — File Permissions (chmod, chown)

⚡ TL;DR — Linux file permissions control who can read, write, or execute each file using a three-group model: owner, group, and everyone else — enforced by the kernel on every file access.

| #127            | Category: Linux                                              | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Linux File System Hierarchy, Users and Groups                |                 |
| **Used by:**    | Shell Scripting, SSH, SELinux / AppArmor, Security Hardening |                 |
| **Related:**    | Users and Groups, SELinux / AppArmor, Symbolic Links         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A multi-user Unix system in 1971 had a real problem: Alice's source code lived on the same disk as Bob's. Without access controls, Bob could read, modify, or delete Alice's files. The system administrator's password database was readable by every process. A buggy program could overwrite the kernel binary. Any user could fill the disk with garbage files to crash the system for everyone.

**THE BREAKING POINT:**
Early systems discovered this the hard way: a single malicious or careless user could destroy all shared data. A web server process running as a normal user should not be able to read `/etc/shadow` (the password hash file). A setuid binary run by an unprivileged user must temporarily elevate privilege — but only for exactly the operations it was designed for, not for reading arbitrary files.

**THE INVENTION MOMENT:**
Unix designers created a simple three-group, three-permission model that the kernel enforces on every file system call. This is exactly why file permissions exist: to provide mandatory, kernel-enforced access control with a model simple enough to audit at a glance.

---

### 📘 Textbook Definition

**Linux file permissions** are a discretionary access control (DAC) mechanism that assigns three types of access — **read (r)**, **write (w)**, and **execute (x)** — to three identity categories for every file and directory: the file **owner** (user), the file's **group**, and **others** (everyone else). Permissions are stored as a 12-bit field in the file's inode. The kernel checks permissions on every `open()`, `exec()`, `mkdir()`, and related system calls. The `chmod` command modifies permissions; `chown` changes owner and group. Special bits — **setuid (SUID)**, **setgid (SGID)**, and the **sticky bit** — extend the model for privilege escalation and directory sharing scenarios.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every Linux file has three permission slots — for the owner, their group, and everyone else — each allowing or denying read, write, and execute.

**One analogy:**

> A file is a safe-deposit box in a bank. The owner has a key. Members of the owner's "family group" may have a copy of the key. Everyone else can only look through the glass — or not at all, if the box is opaque. The bank teller (kernel) checks your identity before you touch the box.

**One insight:**
Permissions on a **directory** mean something different from permissions on a **file**: execute (`x`) on a directory means "you can enter this directory and access files inside it." Without execute on a parent directory, you cannot access any file beneath it — even if those files have permissive permissions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every file has exactly one owner (UID) and one group (GID).
2. The kernel checks: is caller the owner? In the group? Otherwise "other"?
3. Three bits per category: r (4), w (2), x (1). Nine bits total; three more for SUID/SGID/sticky.

**DERIVED DESIGN:**

```
PERMISSION BITS LAYOUT:

  d  rwx  rwx  rwx
  │   │    │    │
  │   │    │    └── others (everyone else)
  │   │    └─────── group
  │   └──────────── owner (user)
  └──────────────── file type: d=dir, -=file, l=link

Example: -rw-r--r-- (644)
  Owner: rw- = read + write, no execute
  Group: r-- = read only
  Others: r-- = read only

Example: drwxr-x--- (750)
  Owner: rwx = read + write + enter directory
  Group: r-x = read + enter, no write
  Others: --- = no access at all
```

**Numeric (octal) representation:**

- `r=4, w=2, x=1` — sum the digits per category.
- `chmod 755 file` → owner=7(rwx), group=5(r-x), others=5(r-x)
- `chmod 600 ~/.ssh/id_rsa` → owner=6(rw-), group=0(---), others=0(---)

**Special bits:**

- **SUID (4000):** When set on an executable, it runs as the **file owner**, not the caller. Used by `/usr/bin/passwd` (runs as root to write `/etc/shadow`).
- **SGID (2000):** On a file: runs as the file's group. On a directory: new files inherit the directory's group.
- **Sticky bit (1000):** On a directory: only the owner can delete their own files (used on `/tmp`).

**THE TRADE-OFFS:**
**Gain:** Simple model, fast kernel check, no external database needed.
**Cost:** Coarse-grained — only one owner, one group. Can't say "Alice and Bob but not Carol" without ACLs. SUID binaries are a privilege escalation risk if buggy.

---

### 🧪 Thought Experiment

**SETUP:**
A web server process runs as user `www-data`. Your application stores a private config file with a database password at `/etc/myapp/secrets.conf`.

**WHAT HAPPENS WITHOUT PERMISSIONS:**
Any process — including a PHP script handling user uploads, or a `cron` job running as `nobody` — can open and read `/etc/myapp/secrets.conf`. A malicious uploaded PHP file (`<?php readfile('/etc/myapp/secrets.conf'); ?>`) exfiltrates your database password to an attacker.

**WHAT HAPPENS WITH PERMISSIONS:**

```bash
# Set: owner=root, group=myapp, permissions 640
chown root:myapp /etc/myapp/secrets.conf
chmod 640 /etc/myapp/secrets.conf
# → -rw-r----- root myapp secrets.conf
```

Now only `root` and members of the `myapp` group can read it. The `www-data` user is not in `myapp` group. The PHP file returns "Permission denied." The attacker gets nothing.

**THE INSIGHT:**
Permissions are a first-line defence for secrets in transit on disk. The model is enforced by the kernel, not by your application code — so it works even if your app is compromised.

---

### 🧠 Mental Model / Analogy

> Think of every file as a room in an office building. The room has three types of visitor badges: **Owner badge** (full key), **Department badge** (limited access), and **Visitor badge** (lobby only). The security guard (kernel) checks your badge before you enter and refuses access if your badge doesn't match the room's policy.

- "Owner badge" → user (UID) permissions
- "Department badge" → group (GID) permissions
- "Visitor badge" → others permissions
- "Security guard checks badge" → kernel permission check on every syscall
- "Room policy posted on the door" → the 9 permission bits on the inode

**Where this analogy breaks down:** Unlike a real badge system, you cannot grant access to a specific individual who is not the owner or in the group — for that, you need POSIX ACLs (`setfacl`).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every file in Linux has a set of rules: who can read it, who can change it, and who can run it (if it's a program). There are three groups of people these rules apply to: the file's owner, people in a shared group, and everyone else.

**Level 2 — How to use it (junior developer):**
Use `ls -l` to see permissions. Use `chmod` to change them (e.g., `chmod 755 script.sh` to make it executable). Use `chown user:group file` to change ownership. Critical: SSH private keys must be `600` (owner-only read/write) or SSH will refuse to use them. Web server document roots are typically `755` so the server process can read files.

**Level 3 — How it works (mid-level engineer):**
The kernel stores permissions in the inode's `st_mode` field. On every `open()` syscall, the kernel's VFS calls `inode_permission()`, which compares the calling process's `euid`/`egid` against the inode's `uid`/`gid` and permission bits. Root (UID 0) bypasses permission checks (except execute bits on regular files). `umask` is a process-level mask that subtracts bits from default permissions at file creation time (`umask 022` → new files get `644`, new dirs get `755`).

**Level 4 — Why it was designed this way (senior/staff):**
The 9-bit model is intentionally minimal — it fits in 12 bits (9 + 3 special), checking is O(1), and it requires no external database. The trade-off is expressiveness: you can't write "Alice and Bob but not Carol" without POSIX ACLs (`getfacl`/`setfacl`). Modern Linux adds capabilities (`CAP_NET_BIND_SERVICE`, etc.) to break up root's monolithic privilege — avoiding SUID root binaries. SELinux/AppArmor add mandatory access control (MAC) on top of DAC, which cannot be overridden even by root.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│       KERNEL PERMISSION CHECK FLOW                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Process calls: open("/etc/myapp/secrets.conf","r")  │
│          ↓                                           │
│  Kernel: get inode for path                          │
│          ↓                                           │
│  Kernel: is caller euid == 0 (root)?                 │
│          YES → allow (root bypasses DAC)             │
│          NO  → continue ↓                            │
│                                                      │
│  Is caller euid == inode.uid (owner)?                │
│          YES → apply OWNER bits (rwx)                │
│          NO  → continue ↓                            │
│                                                      │
│  Is caller egid == inode.gid (group)?                │
│    OR supplementary group match?                     │
│          YES → apply GROUP bits (rwx)                │
│          NO  → apply OTHERS bits (rwx)               │
│                                                      │
│  Do the selected bits allow the requested op?        │
│          YES → return file descriptor                │
│          NO  → return EACCES (Permission denied)     │
└──────────────────────────────────────────────────────┘
```

**`chmod` modes:**

```bash
# Symbolic mode
chmod u+x file       # add execute to owner
chmod g-w file       # remove write from group
chmod o=r file       # set others to read-only
chmod a+r file       # add read for all (a = all)
chmod u=rwx,g=rx,o= file  # explicit full spec

# Octal mode (most common in scripts)
chmod 755 file       # rwxr-xr-x
chmod 644 file       # rw-r--r--
chmod 600 file       # rw------- (private key)
chmod 700 dir        # rwx------ (private dir)
chmod 1777 /tmp      # rwxrwxrwt (sticky bit)
```

**`chown` usage:**

```bash
chown alice file          # change owner to alice
chown alice:devs file     # change owner and group
chown :devs file          # change group only
chown -R alice:devs dir/  # recursive
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
User "alice" runs: cat /etc/myapp/secrets.conf
    ↓
Shell forks → execve(/bin/cat)
    ↓
cat calls: open("/etc/myapp/secrets.conf", O_RDONLY)
    ↓
Kernel VFS resolves path → fetches inode
    ↓
Kernel checks: alice's euid=1001, file uid=0(root)
    ← YOU ARE HERE (permission check)
    ↓
alice ≠ owner; is alice in group "myapp"? YES
    ↓
Apply group bits: r-- → read allowed
    ↓
Kernel returns file descriptor
    ↓
cat reads and prints file contents
```

**FAILURE PATH:**

```
alice is removed from "myapp" group
    ↓
Next login: alice's session has new group list
    ↓
cat open() → applies OTHERS bits: --- → EACCES
    ↓
Observable: "Permission denied"
```

**WHAT CHANGES AT SCALE:**
At scale, permission checks are negligible overhead (nanoseconds). The management problem scales, however: thousands of files, hundreds of users — POSIX ACLs (`setfacl`) or role-based access via groups become essential. Automated secrets management (HashiCorp Vault, AWS Secrets Manager) supplants file-based secrets entirely, eliminating the permission management problem for credentials.

---

### 💻 Code Example

**Example 1 — Reading and interpreting permissions:**

```bash
ls -la /etc/shadow
# → -rw-r----- 1 root shadow 1234 Jan 1 00:00 /etc/shadow
# Owner=root: rw- (read+write)
# Group=shadow: r-- (read only)
# Others: --- (no access)

# Numeric representation
stat -c "%a %U:%G %n" /etc/shadow
# → 640 root:shadow /etc/shadow
```

**Example 2 — Common permission patterns:**

```bash
# SSH private key: owner-only read/write (REQUIRED by ssh)
chmod 600 ~/.ssh/id_rsa

# Shell script: executable by all, writable only by owner
chmod 755 deploy.sh

# Config file: readable by all, writable only by root
chmod 644 /etc/nginx/nginx.conf

# Secret file: readable by service group only
chown root:myapp /etc/myapp/db.password
chmod 640 /etc/myapp/db.password
```

**Example 3 — SUID example (passwd binary):**

```bash
ls -la /usr/bin/passwd
# → -rwsr-xr-x 1 root root 59640 ... /usr/bin/passwd
#        ^--- s = SUID set (runs as root, not caller)

# Regular user runs passwd → process becomes effective UID 0
# → can write to /etc/shadow even though caller is uid=1001
```

**Example 4 — Finding security risks:**

```bash
# BAD: Find world-writable files (anyone can modify)
find / -perm -002 -not -path "/proc/*" 2>/dev/null

# BAD: Find SUID root binaries (potential privilege escalation)
find / -user root -perm -4000 2>/dev/null

# GOOD: Audit service config permissions
find /etc/myapp -ls 2>/dev/null
```

---

### ⚖️ Comparison Table

| Mechanism             | Granularity               | Complexity | Best For                                |
| --------------------- | ------------------------- | ---------- | --------------------------------------- |
| **DAC (chmod/chown)** | Owner, group, others      | Low        | Standard file access control            |
| POSIX ACLs (setfacl)  | Per-user, per-group       | Medium     | Fine-grained access for multiple users  |
| SELinux (labels)      | Per-process, per-resource | High       | Mandatory access control, compliance    |
| AppArmor (profiles)   | Per-program paths         | Medium     | Restricting specific application access |
| Capabilities (setcap) | Per-privilege             | Medium     | Dropping root without full privilege    |

**How to choose:** Start with DAC (chmod/chown) — it covers 95% of cases. Add POSIX ACLs when you need "Alice and Bob but not Carol." Use SELinux/AppArmor for mandatory policy enforcement that even root cannot override.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `chmod 777` is "safe for testing"            | World-writable files allow any local process to modify them; a web-server compromise can overwrite your code                          |
| Root ignores permissions                     | Root bypasses DAC, but SELinux/AppArmor MAC policies can still restrict root                                                          |
| `chown` on a symlink changes the link target | Use `-h` flag to change the symlink itself; without it, `chown` follows the symlink and changes the target                            |
| Group permissions apply if you own the file  | No — if you are the file owner, OWNER bits apply, even if you are also in the file's group                                            |
| `chmod +x` makes any file runnable           | The file must also be a valid executable or have a valid shebang line; `chmod +x` on a text file without a shebang fails at exec time |
| `umask 022` means files are created `022`    | `umask` is subtracted from defaults: default 666 for files → 666 - 022 = 644; default 777 for dirs → 777 - 022 = 755                  |

---

### 🚨 Failure Modes & Diagnosis

**SSH Refuses Private Key (Too-Open Permissions)**

**Symptom:**
`ssh` connection fails with: `WARNING: UNPROTECTED PRIVATE KEY FILE! Permissions 0644 for 'id_rsa' are too open. Bad permissions.`

**Root Cause:**
SSH enforces that private key files must not be readable by group or others (max `600`). This is a security gate: a world-readable private key could be stolen by any local user.

**Diagnostic Command:**

```bash
stat ~/.ssh/id_rsa
ls -la ~/.ssh/
```

**Fix:**

```bash
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh/
```

**Prevention:**
Always create SSH keys with `ssh-keygen` which sets correct permissions; don't copy keys manually without resetting permissions.

---

**Service Cannot Read Its Own Config**

**Symptom:**
Service fails to start; logs show "Permission denied" reading `/etc/myservice/config.yaml`.

**Root Cause:**
Config file is owned by root with mode `600`; service runs as a non-root user and is not in the file's group.

**Diagnostic Command:**

```bash
# Check what user the service runs as
ps aux | grep myservice
# Check file permissions
ls -la /etc/myservice/config.yaml
# Check if service user is in the right group
id myservice
```

**Fix:**

```bash
chown root:myservice /etc/myservice/config.yaml
chmod 640 /etc/myservice/config.yaml
```

**Prevention:**
Define service user and group at installation; set permissions in the package's `postinstall` script.

---

**Accidental SUID Binary Introduced**

**Symptom:**
Security audit flags a binary with SUID root that is not in the expected list. Could be a privilege escalation vector.

**Root Cause:**
An install script ran `chmod 4755` or copied a binary from a system where SUID was set.

**Diagnostic Command:**

```bash
find / -user root -perm -4000 -type f 2>/dev/null
# Compare against known-good baseline
```

**Fix:**

```bash
chmod u-s /path/to/unexpected/binary
```

**Prevention:**
Maintain a whitelist of expected SUID binaries; include SUID checks in CI/CD security scanning.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — permissions apply to every node in the hierarchy
- `Users and Groups` — permissions are meaningless without the identity model they reference

**Builds On This (learn these next):**

- `SELinux / AppArmor` — mandatory access control that works on top of (and can override) DAC
- `SSH` — SSH enforces strict key permissions (600) as a security requirement
- `Linux Security Hardening` — permission hardening is a core component of system security

**Alternatives / Comparisons:**

- `Kernel Capabilities` — replaces SUID root with fine-grained privilege (e.g., `CAP_NET_BIND_SERVICE`)
- `POSIX ACLs (setfacl/getfacl)` — extends the 3-group model to arbitrary user/group combinations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel-enforced read/write/execute        │
│              │ control per owner, group, others          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-user systems: stop users reading    │
│ SOLVES       │ each other's files                        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Directory execute (x) = permission to     │
│              │ enter; without it, nothing inside is      │
│              │ accessible regardless of file perms       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every file has permissions       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use 777 on files with secrets       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity (3 groups) vs. granularity     │
│              │ (need ACLs for fine-grained control)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Three groups, three permissions,         │
│              │  checked by the kernel on every access"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Users and Groups → SELinux/AppArmor →     │
│              │ Linux Security Hardening                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A containerised web application runs as UID 1000 inside the container. The container mounts `/etc/app/secrets` from the host, where the file is owned by UID 1000 on the host and has permissions `600`. On the host, UID 1000 is the user "alice." Inside the container, UID 1000 is "appuser" — a different username. Will the container process be able to read the secret? Explain what the kernel checks and why the username is irrelevant to the permission decision.

**Q2.** Your `/tmp` directory has permissions `1777` (sticky bit set). User "bob" creates a file `/tmp/shared.txt` with permissions `666`. User "alice" can read it (others permission is read). Can alice delete bob's file? Why or why not — and what specific kernel check enforces this? How does this behaviour protect a shared multi-user `/tmp` from accidental or malicious file deletion?
