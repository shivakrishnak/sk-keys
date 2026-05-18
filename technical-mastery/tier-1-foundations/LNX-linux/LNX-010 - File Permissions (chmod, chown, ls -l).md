---
id: LNX-010
title: "File Permissions (chmod, chown, ls -l)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-008
used_by: LNX-011, LNX-038
related: LNX-011, LNX-019, LNX-078
tags: [permissions, chmod, chown, security, access-control, users, groups]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/lnx/file-permissions/
---

## TL;DR

Linux file permissions control who can read, write, or execute
each file. Three categories (owner, group, others) each get
three bits (read=4, write=2, execute=1). `chmod 755 file` makes
it rwxr-xr-x. `chown user:group file` changes ownership. Getting
permissions wrong causes the #1 production permission error:
"Permission denied." Understanding permissions is fundamental
to Linux security.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-010 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | permissions, chmod, chown, file security, access control |
| **Prerequisites** | LNX-008 |

---

### The Problem This Solves

Linux is a multi-user system. Without permissions, any user
could read another's files, delete system binaries, or execute
anything. Permissions are the fundamental access control mechanism.
In production: wrong permissions cause application startup failures
("cannot read config file"), security vulnerabilities (world-
readable private keys), and container security issues.

---

### Textbook Definition

Linux uses **Discretionary Access Control (DAC)**: the owner of
a file decides who can access it. Each file has:
- **Owner**: a user (uid)
- **Group**: a group (gid)
- **Permissions**: three sets of read/write/execute bits

Permissions are encoded as:
- **user (u)**: file owner
- **group (g)**: members of the file's group
- **other (o)**: everyone else

Each category has three permission bits:
- **r (read)**: 4 - read file content / list directory
- **w (write)**: 2 - modify file / create/delete files in directory
- **x (execute)**: 1 - execute file as program / enter directory

---

### Understand It in 30 Seconds

```
$ ls -la /etc/nginx/nginx.conf
-rw-r--r-- 1 root root 2048 Jan 15 10:30 nginx.conf
^          ^ ^    ^
|          | |    group
|          | owner
|          hard link count
|
Permission bits: -rw-r--r--
  -    = regular file (d=directory, l=symlink)
  rw-  = owner can: read, write (no execute)
  r--  = group can: read only
  r--  = others can: read only

chmod 644 file   ->  rw-r--r--  (common for config files)
chmod 755 file   ->  rwxr-xr-x  (common for executables/dirs)
chmod 600 file   ->  rw-------  (private: only owner can read)
chmod 777 file   ->  rwxrwxrwx  (DANGEROUS: everyone can do anything)

chown user:group file  -> change owner and group
chown alice file       -> change only owner to alice
chown :developers file -> change only group to developers
```

---

### First Principles

**The octal notation explained:**
```
Permission bits = 3 bits each for user, group, other
Read  = 4 (binary 100)
Write = 2 (binary 010)
Exec  = 1 (binary 001)

rw-  = 4+2+0 = 6
r-x  = 4+0+1 = 5
r--  = 4+0+0 = 4
rwx  = 4+2+1 = 7
---  = 0+0+0 = 0

chmod 755 = rwxr-xr-x
  7 = rwx (owner can read, write, execute)
  5 = r-x (group can read and execute, not write)
  5 = r-x (others can read and execute, not write)

chmod 644 = rw-r--r--
  6 = rw- (owner can read and write, not execute)
  4 = r-- (group can only read)
  4 = r-- (others can only read)

chmod 600 = rw-------
  6 = rw- (owner can read and write)
  0 = --- (group: no permissions)
  0 = --- (others: no permissions)
  This is the correct permission for SSH private keys.
```

**Why directories need execute bit:**
```
Execute on a directory = permission to ENTER (cd into it)
Without x on directory: cannot cd into it, cannot list contents

  drwxr-x--- = rwxr-x---
  7 = rwx: owner can list, create files, and enter
  5 = r-x: group can list contents and enter, not create files
  0 = ---: others cannot enter OR list

  A file inside: only accessible if all directories in path
  are executable by the accessing user.
  /home/alice/private/secret.txt with d---------:
    No one except alice can enter /home/alice/private/
    Even root must use special capabilities to bypass (or use sudo)
```

---

### Thought Experiment

You're setting up an application that reads a config file with
database credentials. Three permission scenarios:

**Scenario A: chmod 644 config.properties**
```
rw-r--r--: owner reads+writes, group reads, everyone reads
Problem: any user on the system can read the DB password
Security risk: HIGH - any compromised account leaks credentials
```

**Scenario B: chmod 600 config.properties + chown appuser:appuser**
```
rw-------: only appuser can read (and root)
Problem: if app runs as wrong user, it can't read its own config
Security: CORRECT for sensitive config files
```

**Scenario C: chmod 777 config.properties**
```
rwxrwxrwx: everyone can read, write, and execute
Problem: any user can modify the config file (inject malicious DB?)
Security risk: CRITICAL - never do this with config files
```

Correct answer: B. The principle of least privilege: give only
the permissions required, to only the users/processes that need them.

---

### Mental Model / Analogy

Linux permissions are like a **hotel key card system:**

```
File = hotel room
Owner = registered guest (full access: enter, modify, invite)
Group = hotel staff (limited access: enter to clean, not modify personal items)
Others = random person in lobby (no access - or maybe just peek)

rwxr-xr-x (755 for a program):
  Owner (guest): can run it, read it, modify it
  Group (staff): can run it and read it, not modify
  Others (public): can run it and read it, not modify
  This is correct for: /usr/bin/ls, system programs

rw------- (600 for SSH key):
  Owner (guest): can read/write the key
  Group (staff): cannot touch it
  Others (public): cannot touch it
  This is REQUIRED by SSH: 
    "WARNING: UNPROTECTED PRIVATE KEY FILE!" if permissions wrong
```

---

### Gradual Depth - Five Levels

**Level 1:**
chmod 644 for config files (owner reads/writes, others read).
chmod 755 for executables and directories.
chmod 600 for private files (SSH keys, sensitive configs).
Never chmod 777 - it's a security disaster.

**Level 2:**
Symbolic notation: `chmod u+x file` (add execute for user),
`chmod go-w file` (remove write for group and others),
`chmod a+r file` (add read for all). More readable than octal
for specific changes. Recursive: `chmod -R 755 directory/`.

**Level 3:**
Special permission bits: setuid (s on user bit), setgid (s on
group bit), sticky bit (t on other bit). Setuid: program runs
as owner, not caller (e.g., /usr/bin/passwd runs as root).
Sticky bit on directory: only file owner can delete their own
files (/tmp has this). `chmod 4755 program` = setuid + 755.

**Level 4:**
umask: default permissions for new files. `umask 022` = new files
get 644, directories get 755 (umask bits are REMOVED from default).
ACLs (Access Control Lists): `setfacl -m u:alice:r-- file` -
more granular than user/group/other. `getfacl file` shows ACLs.
SELinux/AppArmor labels add mandatory access control on top of DAC.

**Level 5:**
Container security: containers typically run as root inside but
should use USER directive in Dockerfile to run as non-root. In
Kubernetes: SecurityContext spec sets uid/gid for pods.
`runAsNonRoot: true` + `runAsUser: 1000` prevents root containers.
Linux capabilities replace coarse-grained root: `CAP_NET_ADMIN`
allows network config without full root. `setcap cap_net_bind_service+ep`
allows binding port <1024 without root.

---

### Code Example

**BAD - permission mistakes in production:**
```bash
# BAD 1: world-readable secrets
chmod 644 application.properties  # everyone reads DB password!
# Also bad: storing passwords in files at all

# BAD 2: world-writable directory
chmod 777 /var/log/myapp/         # anyone can tamper with logs!

# BAD 3: wrong ownership breaks app startup
# Application expects to read as appuser, but:
chown root:root /etc/myapp/config.yaml  # app runs as appuser, can't read!

# BAD 4: execute bit on data files
chmod 755 config.json   # execute bit on JSON is meaningless and misleading
```

**GOOD - correct permission management:**
```bash
# GOOD 1: sensitive config - only app user can read
chown appuser:appuser /etc/myapp/application.properties
chmod 600 /etc/myapp/application.properties  # rw-------

# GOOD 2: log directory - app writes, group reads
chown appuser:appadmin /var/log/myapp/
chmod 750 /var/log/myapp/  # app: rwx, admin group: r-x, others: ---

# GOOD 3: executable + config
chown root:appuser /opt/myapp/myapp.jar
chmod 750 /opt/myapp/myapp.jar  # root owns, appuser can execute

# GOOD 4: SSH private key MUST be 600
chmod 600 ~/.ssh/id_rsa  # SSH will refuse to use it otherwise

# GOOD 5: web content - nginx reads, developer writes
chown developer:www-data /var/www/mysite/
chmod 775 /var/www/mysite/    # developer: rwx, www-data: rwx, others: r-x
find /var/www/mysite/ -type f -exec chmod 664 {} \;  # files: rw-rw-r--

# GOOD 6: audit file permissions
find /etc/myapp/ -not -perm 600 -name "*.properties" -ls
# Lists config files with wrong permissions
```

---

### Reading Permissions in ls -la

```
$ ls -la /var/log/myapp/
total 2148
drwxr-x--- 2 appuser appadmin  4096 Jan 15 09:00 .
drwxr-xr-x 8 root    root      4096 Jan 15 09:00 ..
-rw-r----- 1 appuser appadmin  1048576 Jan 15 09:30 app.log
-rw-r----- 1 appuser appadmin   524288 Jan 14 23:59 app.log.1

For -rw-r----- (appuser, appadmin):
  - : regular file
  rw- : appuser can read and write
  r-- : appadmin group can read only (no write)
  --- : others cannot access at all

For drwxr-x---:
  d : directory
  rwx : appuser can list, create files, enter
  r-x : appadmin group can list and enter (not create)
  --- : others cannot enter or list
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "chmod 777 fixes all permission problems" | 777 is a security disaster. Use the minimal permissions needed. If your app can't read a file, fix the ownership first. |
| "Only root can change permissions" | The file's OWNER can change its own permissions (and ownership to self). Root can change anything. |
| "Root ignores permissions" | Root (uid=0) bypasses DAC (read/write/execute on any file). Root is NOT stopped by SELinux in enforcing mode. Root in containers may not be host root (depending on user namespace configuration). |
| "Execute permission on a file means it can run" | The file must also have a valid format (ELF binary or valid shebang line `#!/bin/bash`). A text file with chmod +x that doesn't start with `#!` gives "Exec format error." |
| "Read permission is enough to copy a file" | To copy a file, you need read permission on the file AND write permission on the destination directory. To delete a file, you need write permission on the directory containing it (not the file itself). |

---

### Failure Modes & Diagnosis

**"Permission denied" diagnosis flow:**
```bash
# 1. Check who the process is running as:
ps aux | grep myapp   # shows user in first column

# 2. Check the file's ownership and permissions:
ls -la /etc/myapp/config.yaml
# -rw-r----- root root  <- process runs as appuser, not root

# 3. Check the directory permissions (need execute to enter):
ls -la /etc/myapp/
# drwx------ root root   <- only root can enter this dir!

# 4. Fix: change ownership
chown appuser:appuser /etc/myapp/config.yaml
chmod 600 /etc/myapp/config.yaml

# 5. Verify process can access (test as the process user):
sudo -u appuser cat /etc/myapp/config.yaml
# Should succeed now
```

**SSH refuses private key (wrong permissions):**
```bash
# Error: "WARNING: UNPROTECTED PRIVATE KEY FILE!"
# SSH requires private key to be 600 or 700
ls -la ~/.ssh/id_rsa
# -rw-r--r-- 1 alice alice 1679 Jan 15 ...  <- too open!

# Fix:
chmod 600 ~/.ssh/id_rsa
# -rw------- 1 alice alice 1679 Jan 15 ...  <- correct

# Check entire .ssh directory:
chmod 700 ~/.ssh/          # directory: only you can enter
chmod 600 ~/.ssh/id_rsa    # private key: only you can read
chmod 644 ~/.ssh/id_rsa.pub  # public key: readable by all
chmod 644 ~/.ssh/authorized_keys  # or 600
```

**Security: world-writable files (critical vulnerability):**
```bash
# Find world-writable files (security audit):
find / -perm -002 -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null
# These files can be modified by ANY user
# Especially dangerous: scripts, config files, binaries

# Fix: remove world-write bit
chmod o-w /path/to/file

# Find setuid binaries (potential privilege escalation):
find / -perm -4000 -type f 2>/dev/null
# These run as their owner (often root) - minimize this list
```

---

### Related Keywords

**Foundational:**
LNX-008 (Files and Directories), LNX-011 (Users and Groups)

**Builds on this:**
LNX-019 (sudo), LNX-038 (User Management),
LNX-057 (Security Hardening), LNX-078 (Capabilities)

**Related:**
LNX-079 (Linux Security Modules), OSY-085 (Process Security)

---

### Quick Reference Card

| Permission | Octal | rwx format | Typical use |
|------------|-------|-----------|-------------|
| rw------- | 600 | rw------- | SSH keys, private configs |
| rw-r--r-- | 644 | rw-r--r-- | Regular files, configs |
| rwxr-xr-x | 755 | rwxr-xr-x | Executables, directories |
| rwx------ | 700 | rwx------ | Private directories |
| rw-rw-r-- | 664 | rw-rw-r-- | Group-collaborative files |
| rwxrwxr-x | 775 | rwxrwxr-x | Group-collaborative dirs |
| rwxrwxrwx | 777 | rwxrwxrwx | AVOID: security risk |

**3 things to remember:**
1. 600 for private keys and sensitive configs (owner only)
2. 755 for directories and executables (world-readable, not writable)
3. Directories need execute bit to be entered (cd) - not just read

**Interview angle:**
"Your Java application starts but immediately fails with 'Permission
denied' reading a config file. Walk me through the diagnosis." ->
Check what user the JVM runs as (ps aux), check file ownership
(ls -la /etc/myapp/), check directory permissions (can user enter
the directory?), fix with chown + chmod.

---

### Transferable Wisdom

The **principle of least privilege** from Linux permissions appears
in: AWS IAM policies (grant only required actions on required resources),
Kubernetes RBAC (role-based access control for cluster resources), Java
Security Manager (sandbox applications), and OAuth scopes (grant only
required API access). The pattern is universal: minimum access required.

The **owner/group/other** model is a simplified version of RBAC: owner
is the primary role, group is the secondary role, others is the default.
More sophisticated: ACLs (setfacl), RBAC (Kubernetes, cloud IAM), ABAC
(attribute-based). All variations of the same problem: map subjects
to permissions on resources.

---

### The Surprising Truth

On Linux, to DELETE a file, you don't need write permission on
the FILE itself - you need write permission on the DIRECTORY
containing it. This surprises many engineers. The reason: deleting
a file removes it from the directory (modifies the directory), not
from the file itself. The file data remains until the last reference
is gone. This is why a user can delete a file they cannot read or
write: they just need write access to the directory. Conversely,
read-only directories prevent deletion even if the user owns the file.
This is the mechanism behind the sticky bit on /tmp: even though
you have write access to /tmp (can create files), you cannot delete
OTHER USERS' files because the sticky bit requires you to own the file.

---

### Mastery Checklist

- [ ] Can read ls -la output and explain each permission bit
- [ ] Can calculate octal permissions from rwx notation and vice versa
- [ ] Can diagnose and fix a "Permission denied" error
- [ ] Can set correct permissions for SSH keys, web files, and app configs
- [ ] Can explain why execute permission is needed for directories

---

### Think About This

1. A file has permissions `rwxr-xr-x` and is owned by root. Your
   application runs as user `appuser`. Can appuser execute this file?
   Now change the directory containing this file to `d---------`
   (owned by root). Can appuser execute the file now? What does
   this teach you about how Linux evaluates access?

2. When a Java application writes a file using `Files.write()`, what
   permissions does the new file get? What determines this? How can
   you configure your Java application to always create files with
   specific permissions?

3. Docker containers run as root by default. When a container's root
   process writes a file to a mounted volume (on the host filesystem),
   what user and group owns that file on the host? Why does this
   cause problems for developers and how does user namespace remapping
   solve it?

**TYPE G:** Design a permission scheme for a web application with:
an nginx web server (runs as www-data), a Java application server
(runs as appuser), shared config files in /etc/myapp/, log files
in /var/log/myapp/ readable by both, and static files in /var/www/
served by nginx but deployed by appuser. What are the exact ownership
and permission settings for each directory and file type?

---

### Interview Deep-Dive

**Foundational:**
Q: What does `chmod 755 myfile` do, and when would you use it?
A: It sets permissions to rwxr-xr-x. The owner can read, write, and execute the file. Group members can read and execute (but not write). All other users can read and execute (but not write). This is appropriate for: executables in /usr/bin (any user should run them), directories (any user should enter and list them), web application directories (web server needs to read static files). Not appropriate for config files with sensitive data - use 644 or 600 instead.

**Intermediate:**
Q: Your application cannot read /etc/myapp/config.yaml. Walk through the complete diagnosis.
A: Step 1: identify the user the application process runs as: `ps aux | grep myapp`. Step 2: check the file's ownership and permissions: `ls -la /etc/myapp/config.yaml`. Step 3: check if the process user can read the file - if file is rw-r----- owned by root:root and process runs as appuser, it cannot read. Step 4: check directory execute permissions - process must be able to enter /etc/myapp/ (`ls -la /etc/ | grep myapp`). Step 5: fix - either `chown appuser:appuser /etc/myapp/config.yaml; chmod 600 /etc/myapp/config.yaml` (if app should own it) or `chown root:appgroup /etc/myapp/config.yaml; chmod 640 /etc/myapp/config.yaml; usermod -aG appgroup appuser` (group-based access). Step 6: verify: `sudo -u appuser cat /etc/myapp/config.yaml`.

**Expert:**
Q: Explain the security implications of setuid binaries and how modern systems reduce reliance on them.
A: A setuid binary executes with the file owner's privileges (typically root) regardless of who runs it. Examples: `/usr/bin/passwd` (runs as root to modify /etc/shadow, which is root-writable), `/usr/bin/sudo` (itself runs as root to apply privilege escalation). Security risks: if a setuid binary has a vulnerability, an attacker can exploit it to gain root. Historical exploits: buffer overflows in setuid binaries gave root access. Modern mitigations: (1) Linux capabilities allow specific root-like abilities without full root - `CAP_NET_BIND_SERVICE` lets a server bind port 80 without being root; (2) `setcap cap_net_bind_service+ep /usr/bin/myserver` instead of setuid root; (3) minimize setuid binaries: `find / -perm -4000 -type f` should return a short list in a hardened system; (4) use user namespaces for privilege separation; (5) SELinux/AppArmor confine setuid programs to specific allowed operations.
