---
layout: default
title: "Users and Groups"
parent: "Linux"
nav_order: 128
permalink: /linux/users-and-groups/
number: "0128"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy, Operating System
used_by: File Permissions (chmod, chown), SSH, Linux Security Hardening, Shell
related: File Permissions (chmod, chown), SELinux / AppArmor, Environment Variables
tags:
  - linux
  - security
  - os
  - foundational
---

# 128 — Users and Groups

⚡ TL;DR — Linux users and groups are the identity system the kernel uses to decide who owns files and which processes can access which resources, stored in `/etc/passwd` and `/etc/group`.

| #128            | Category: Linux                                                | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Linux File System Hierarchy, Operating System                  |                 |
| **Used by:**    | File Permissions (chmod, chown), SSH, Linux Security Hardening |                 |
| **Related:**    | File Permissions (chmod, chown), SELinux / AppArmor            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Early batch computing systems ran one job at a time. One user. One program. No sharing. As Unix became a multi-user time-sharing system in the early 1970s, the fundamental challenge emerged: Bell Labs engineers needed their source code to be private from colleagues, yet needed shared access to common tools and libraries. Without an identity system, every process would have equal access to every file. A single buggy or malicious program could erase everything.

**THE BREAKING POINT:**
The failure mode is immediate: without identity, there is no "whose file is this?" The permission system (read/write/execute) is meaningless without identities to attach permissions to. System processes need to run with different privileges than users. The `cron` daemon should not be able to read Alice's private SSH keys. The web server process should not be able to modify system binaries.

**THE INVENTION MOMENT:**
Unix introduced numeric user IDs (UIDs) and group IDs (GIDs) as the foundation of identity. The kernel tracks them in every process. The filesystem stores them in every inode. This is exactly why users and groups exist: to give the permission system its subject — the "who" that permissions apply to.

---

### 📘 Textbook Definition

A **Linux user** is an identity represented by a numeric **User ID (UID)**. Every process runs as a UID; every file is owned by a UID. A **group** is a named collection of users, represented by a numeric **Group ID (GID)**, used to share access to files without granting access to all users. User information is stored in `/etc/passwd`; password hashes in `/etc/shadow`; group memberships in `/etc/group`. Each process has a **real UID** (who launched it), an **effective UID** (used for permission checks — may differ for SUID programs), and a list of **supplementary GIDs**. UID 0 is `root` — the superuser with unrestricted kernel access to most operations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Linux identifies every process and file by a number (UID/GID), not a name — the name in `/etc/passwd` is just a human-readable label.

**One analogy:**

> Think of UIDs like employee badge numbers. The company has thousands of people ("alice," "bob"), but the security system uses badge numbers (1001, 1002) — not names — to decide who enters which room. Groups are departments: badge holders in the "engineering" department (GID 200) can all access the engineering lab. The name on the badge is cosmetic; the number is what counts.

**One insight:**
Root's power is not "the root user" — it is **UID 0**. A process running as UID 0 has kernel-bypass privileges. You can rename the root user to anything, and UID 0 still has full power. This is why container security focuses on ensuring processes run as non-zero UIDs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every process has a UID and one or more GIDs (primary + supplementary).
2. Every file has an owner UID and a group GID.
3. The kernel uses UIDs/GIDs — not usernames — for all permission checks.

**DERIVED DESIGN:**

```
/etc/passwd FORMAT (colon-separated):
username:x:UID:GID:comment:home:shell

alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
www-data:x:33:33::/var/www:/usr/sbin/nologin
root:x:0:0:root:/root:/bin/bash

/etc/shadow FORMAT (password hashes):
alice:$6$salt$hash...:18000:0:99999:7:::

/etc/group FORMAT:
groupname:x:GID:member1,member2

developers:x:200:alice,bob
www-data:x:33:
docker:x:999:alice
```

**User categories:**

```
UID 0         → root (superuser)
UID 1–999     → system users (daemons, services)
              → no login shell (/usr/sbin/nologin)
              → e.g., www-data(33), nobody(65534)
UID 1000+     → regular (human) users
              → have home directory, login shell
```

**Process identity model:**

```
┌──────────────────────────────────────────────────────┐
│            PROCESS IDENTITY FIELDS                   │
├──────────────────────────────────────────────────────┤
│ Real UID (RUID)      │ Who launched the process      │
│ Effective UID (EUID) │ Used for permission checks    │
│ Saved UID (SUID)     │ Allows EUID to be restored    │
│ Real GID (RGID)      │ Primary group of launcher     │
│ Effective GID (EGID) │ Used for group permission     │
│ Supplementary GIDs   │ Extra group memberships       │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Lightweight identity (just two integers per file), fast checks, universal consistency.
**Cost:** Adding a user to a group takes effect only at next login (supplementary GIDs are set at login from `/etc/group`). Centralized identity requires LDAP/AD in large organisations, which adds complexity.

---

### 🧪 Thought Experiment

**SETUP:**
A deployment engineer sets up a new service. The service needs to read `/etc/myapp/db.conf` (owned by root, mode 640, group `myapp`) and write to `/var/log/myapp/` (owned by root, mode 755).

**WHAT HAPPENS WITHOUT A DEDICATED SERVICE USER:**
The service runs as root. It can read the config — fine. It can write logs — fine. But it can also modify `/etc/passwd`, read `/etc/shadow`, kill other processes, and install kernel modules. A single remote code execution vulnerability in the service = full system compromise.

**WHAT HAPPENS WITH A DEDICATED SERVICE USER:**

```bash
# Create system user "myapp" with no login shell
useradd -r -s /usr/sbin/nologin -g myapp myapp
# -r: system user (UID < 1000), -s: no interactive login

# Config: root owns it, myapp group can read it
chown root:myapp /etc/myapp/db.conf
chmod 640 /etc/myapp/db.conf

# Logs: myapp user owns the log dir
chown myapp:myapp /var/log/myapp/
chmod 750 /var/log/myapp/

# Run the service as myapp
ExecStart=/usr/bin/myapp
User=myapp
Group=myapp
```

Now a compromise of the service gets the attacker only `myapp` privileges — cannot read shadow, cannot modify system files.

**THE INSIGHT:**
The principle of least privilege is implemented through user/group design. Every service that runs as its own unprivileged user is a security boundary that limits blast radius.

---

### 🧠 Mental Model / Analogy

> Users and groups are like a company ID and department system. Your ID number (UID) is what the building access system checks — not your name. Your department membership (GID) determines which shared areas you can access. System services are like robots with contractor badges — they can access exactly the areas they need, nothing more.

- "Employee ID number" → UID
- "Contractor badge (limited access)" → system user (UID 1–999)
- "Department membership" → GID / group membership
- "Security door checks badge number" → kernel permission check using UID/GID
- "HR database" → `/etc/passwd`, `/etc/group`

**Where this analogy breaks down:** A real employee can belong to only one department at a time; a Linux user can belong to multiple supplementary groups simultaneously. Also, if you set UID=0 on any account, it becomes root regardless of the name — there's no equivalent badge-number override in a real building security system.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every person (or program) using a Linux system has a username and belongs to one or more groups. These identities decide which files they can open, change, or run. The system keeps track of all users in a list called `/etc/passwd`.

**Level 2 — How to use it (junior developer):**
Create users with `useradd`, set passwords with `passwd`, manage groups with `groupadd`/`usermod -aG group user`. Check your own identity with `id` (shows UID, GID, all groups). Add a user to a group: `usermod -aG docker alice`. The change takes effect on next login. Service users should use `useradd -r -s /usr/sbin/nologin` to prevent interactive logins.

**Level 3 — How it works (mid-level engineer):**
At login (`su`, `ssh`, `sudo`), PAM (Pluggable Authentication Modules) authenticates the user and calls `initgroups()` to build the supplementary GID list from `/etc/group`. This list is inherited by all child processes for the duration of the session. When you `sudo su alice`, you get alice's UID/GIDs — including supplementary groups set at her last login. The kernel stores real/effective/saved UIDs in the process descriptor; `setuid(0)` only works if euid=0 or ruid=0.

**Level 4 — Why it was designed this way (senior/staff):**
The separation of real/effective/saved UIDs was designed for SUID programs that need to temporarily drop and re-acquire privilege (e.g., `su`, `sudo`). The saved UID allows the process to `seteuid(ruid)` to drop privilege and `seteuid(0)` to re-acquire it. Modern security practice prefers `CAP_*` capabilities over SUID root. In containerised environments, user namespace remapping allows a container's root (UID 0) to map to an unprivileged UID on the host — critical for rootless containers.

---

### ⚙️ How It Works (Mechanism)

**User creation and storage:**

```bash
# useradd creates entries in:
# /etc/passwd  → username, UID, GID, home, shell
# /etc/shadow  → password hash
# /etc/group   → group membership

useradd -m -s /bin/bash -G docker,developers alice
# -m: create home dir
# -s: login shell
# -G: supplementary groups
```

**Reading the files:**

```
/etc/passwd:
alice:x:1001:1001:Alice:/home/alice:/bin/bash
  │   │  │    │     │        │           └── login shell
  │   │  │    │     │        └────────────── home directory
  │   │  │    │     └─────────────────────── GECOS/comment
  │   │  │    └───────────────────────────── primary GID
  │   │  └────────────────────────────────── UID
  │   └───────────────────────────────────── password (x = in shadow)
  └───────────────────────────────────────── username

/etc/shadow (root-readable only, mode 640):
alice:$6$rounds=5000$salt$hash:19500:0:99999:7:::
         │                        │
         └──── SHA-512 hash       └── days since epoch of last change
```

**Switching identities:**

```bash
su - alice          # switch to alice (full login)
sudo command        # run command as root
sudo -u bob cmd     # run as bob
runuser -u www-data -- /usr/bin/myapp  # run as www-data
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
SSH login: alice connects with key
    ↓
sshd authenticates alice
    ↓
sshd forks, calls setuid(alice_uid), setgid(alice_gid)
    ← YOU ARE HERE (identity established)
    ↓
initgroups() loads supplementary GIDs from /etc/group
    ↓
Bash shell starts with alice's UID/GIDs
    ↓
Every child process inherits alice's identity
    ↓
Kernel checks alice's UID/GIDs for every file access
```

**FAILURE PATH:**

```
alice tries: sudo systemctl restart myservice
    ↓
sudo checks /etc/sudoers — alice not listed
    ↓
sudo denies with: "alice is not in the sudoers file"
    ↓
Observable: error message; action blocked
```

**WHAT CHANGES AT SCALE:**
At scale (100s of servers, 1000s of users), local `/etc/passwd` files become unmanageable. Centralised directory services (LDAP, Active Directory, FreeIPA) provide a network-based user database. PAM's `pam_ldap` or `sssd` authenticates against the central store. NSS (Name Service Switch) resolves UIDs from LDAP instead of local files. Container platforms (Kubernetes) use service accounts — not OS users — for workload identity.

---

### 💻 Code Example

**Example 1 — Managing users and groups:**

```bash
# Create a regular user
useradd -m -s /bin/bash -c "Alice Smith" alice
passwd alice           # set password

# Create a system (service) user
useradd -r -s /usr/sbin/nologin -c "MyApp service" myapp

# Create a group
groupadd developers

# Add alice to developers group
usermod -aG developers alice

# Verify: alice's identity and groups
id alice
# → uid=1001(alice) gid=1001(alice) groups=1001(alice),200(developers),999(docker)
```

**Example 2 — Checking and switching users:**

```bash
# Current identity
id
whoami

# Switch to alice (requires alice's password)
su - alice

# Run a command as www-data
sudo -u www-data ls /var/www/html

# Check who is logged in
w
who
last alice    # login history for alice
```

**Example 3 — Service user for a deployment:**

```bash
# Create myapp service user
useradd -r -M -s /usr/sbin/nologin \
  -d /var/lib/myapp -c "MyApp daemon" myapp

# Create group and assign
groupadd -r myapp
usermod -aG myapp myapp

# Setup directories
mkdir -p /etc/myapp /var/log/myapp /var/lib/myapp
chown -R myapp:myapp /var/log/myapp /var/lib/myapp
chown root:myapp /etc/myapp
chmod 750 /var/log/myapp /var/lib/myapp
chmod 750 /etc/myapp

# systemd service unit
# [Service]
# User=myapp
# Group=myapp
```

---

### ⚖️ Comparison Table

| Identity Scope          | Mechanism         | Scale            | Best For                        |
| ----------------------- | ----------------- | ---------------- | ------------------------------- |
| **Local /etc/passwd**   | Files, immediate  | Single server    | Dev boxes, small deployments    |
| LDAP / FreeIPA          | Network directory | Enterprise       | Centralised user management     |
| Active Directory + SSSD | AD + Linux bridge | Large enterprise | Mixed Windows/Linux envs        |
| Service accounts (K8s)  | Kubernetes RBAC   | Containerised    | Microservice auth, not OS users |

**How to choose:** Use local files for single servers and containers. Use LDAP/FreeIPA for multi-server fleets where centralised user management and single sign-on matter.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                   |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Adding a user to a group takes effect immediately | The new GID is only added to the user's supplementary GID list at next login; existing sessions do not see the change     |
| The root username is special                      | UID 0 is special, not the name "root"; rename root to anything, UID 0 still has full privileges                           |
| `/etc/passwd` stores passwords                    | It stores an `x` placeholder; actual password hashes are in `/etc/shadow` (readable only by root)                         |
| Deleting a user removes all their files           | `userdel` removes the user entry; files owned by that UID remain on disk, now showing as a numeric UID                    |
| System users (UID < 1000) cannot run processes    | They absolutely can; web servers, databases, cron daemons all run as system users — they just cannot log in interactively |
| `sudo su` is the same as `su -`                   | `sudo su` keeps the current environment; `su -` starts a fresh login environment with target user's variables             |

---

### 🚨 Failure Modes & Diagnosis

**Service Fails: "No such user" After Deployment**

**Symptom:**
Service fails to start with "user myapp does not exist" in systemd journal.

**Root Cause:**
The systemd unit file specifies `User=myapp`, but the user was not created before the service was installed (e.g., package install order issue).

**Diagnostic Command:**

```bash
id myapp
# → id: 'myapp': no such user
getent passwd myapp
```

**Fix:**

```bash
useradd -r -s /usr/sbin/nologin myapp
systemctl start myapp
```

**Prevention:**
Package `postinstall` scripts should create service users before installing unit files.

---

**Group Membership Not Taking Effect**

**Symptom:**
Engineer adds user to `docker` group with `usermod -aG docker alice`. Alice runs `docker ps` — still "permission denied."

**Root Cause:**
Alice's current session has the GID list from her previous login; the new group is not present until she logs out and back in.

**Diagnostic Command:**

```bash
# Current session groups (may not include new group)
id
# Shows groups at login time

# New group IS in /etc/group
getent group docker
```

**Fix:**

```bash
# Alice must log out and back in, or:
newgrp docker    # start a new shell with docker as primary group
# OR: use 'su - alice' to simulate fresh login
```

**Prevention:**
Document this in onboarding runbooks; after adding to groups, notify user to re-login.

---

**UID Collision After System Migration**

**Symptom:**
Files from old server appear with numeric UIDs (e.g., 1001) instead of usernames on new server; permissions work unexpectedly.

**Root Cause:**
UIDs are not globally assigned; UID 1001 on the old server was "alice," but UID 1001 on the new server is "bob." Files are owned by the number, not the name.

**Diagnostic Command:**

```bash
ls -ln /home/  # numeric UIDs instead of names
find / -nouser 2>/dev/null  # files with no matching UID
```

**Fix:**

```bash
# Remap file ownership to new UIDs
find /data -user 1001 -exec chown new_alice {} \;
```

**Prevention:**
When migrating data between servers, use consistent UID assignments (e.g., via LDAP centralised identity); document UID-to-username mapping before migration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — users own files in the hierarchy
- `Operating System` — the kernel stores UID/GID in every process descriptor

**Builds On This (learn these next):**

- `File Permissions (chmod, chown)` — permissions reference users and groups by UID/GID
- `SSH` — SSH authentication establishes user identity before switching to that UID
- `Linux Security Hardening` — service users with minimal privileges is a core hardening technique

**Alternatives / Comparisons:**

- `SELinux / AppArmor` — adds mandatory access control on top of the user/group DAC model
- `Linux Capabilities` — fine-grained alternative to running services as root with SUID

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Numeric identity (UID/GID) for every      │
│              │ process and file on the system            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-user system needs to know "whose    │
│ SOLVES       │ file is this and who can touch it"        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The kernel uses UID numbers, not names;   │
│              │ UID 0 = root regardless of username       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always; also create dedicated service     │
│              │ users for every daemon/service            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never run services as root (UID 0)        │
│              │ unless absolutely required                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity vs. scale (local files vs.     │
│              │ LDAP for large fleets)                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your username is a label; your UID       │
│              │  is your identity — the kernel            │
│              │  only knows the number"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ File Permissions → SSH →                  │
│              │ Linux Security Hardening                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A container image is built with `USER 1000` in the Dockerfile. The container is deployed on Host A, where UID 1000 is "alice" — a developer with access to sensitive directories. It is also deployed on Host B, where UID 1000 is "appuser" — a restricted service account. The container mounts `/data` from the host in both cases. How do the effective permissions differ between Host A and Host B deployments, and what does this reveal about the relationship between container UIDs and host filesystem permissions?

**Q2.** A security team discovers a SUID root binary (`-rwsr-xr-x root root myapp`) that has a buffer overflow vulnerability. The binary is owned by root with SUID set. A non-privileged user (UID 5000) exploits the overflow to call `setuid(0)`. Trace what happens in the kernel's process credential fields (ruid, euid, suid) from the moment the non-root user executes the binary through the successful `setuid(0)` call, and explain why the separation of ruid/euid/suid in the kernel design makes this attack possible but also constrained.
