---
id: LNX-019
title: "The sudo Command and Privilege Escalation"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-011
used_by: LNX-038, LNX-057
related: LNX-011, LNX-038, LNX-078
tags: [sudo, privilege-escalation, root, superuser, sudoers, access-control]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/lnx/sudo-command/
---

## TL;DR

`sudo` runs a command as root (or another user) without becoming
root permanently. It logs every use and requires the user to be
in the sudoers file (`/etc/sudoers`, edited with `visudo`). Prefer
`sudo specificcommand` over `sudo bash` or `sudo su`. Misconfigured
sudo is a classic Linux privilege escalation vector - production
systems should grant minimal, specific sudo permissions, not
unrestricted `ALL=(ALL) ALL`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-019 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | sudo, root, privilege escalation, sudoers, least privilege |
| **Prerequisites** | LNX-011 |

---

### The Problem This Solves

System administration requires root access for specific tasks (install
packages, manage services, modify system config). But logging in as
root for all work is dangerous: any mistake has maximum consequences;
no audit trail of who did what. sudo solves this: regular users can
run specific privileged commands, with: identity verification
(password), audit logging (who ran what, when), and fine-grained
control (alice can restart nginx but not delete files).

---

### Textbook Definition

**sudo** (superuser do) executes a command with elevated privileges
(typically as root, uid=0) based on rules defined in `/etc/sudoers`.
Key behaviors:
- Verifies user's identity (password, typically)
- Checks `/etc/sudoers` for permission to run the requested command
- Executes the command as the target user (default: root)
- Logs every sudo invocation to syslog (/var/log/auth.log)
- Caches credentials for a timeout period (default: 15 minutes)

`su` (substitute user) switches to another user's identity for the
entire shell session. `sudo` is preferred: it runs one command with
elevation, requires fewer credentials (your own password, not root's),
and creates an audit trail.

---

### Understand It in 30 Seconds

```bash
# Run one command as root:
sudo apt install nginx
sudo systemctl restart nginx
sudo cat /etc/shadow  # read root-only files

# Run a command as another user:
sudo -u postgres psql   # run psql as the postgres user

# Start a root shell (use sparingly):
sudo bash              # root shell via bash
sudo -i                # root login shell (loads root's environment)
sudo su -              # switch to root (different mechanism)

# Check what sudo you're allowed:
sudo -l                # list your sudo permissions

# Edit sudoers safely (ALWAYS use visudo, never edit directly!):
sudo visudo            # opens with syntax checking

# Add a user to the sudo group (Debian/Ubuntu way):
sudo usermod -aG sudo alice
# OR (RHEL way):
sudo usermod -aG wheel alice
```

---

### First Principles

**Why your own password, not root's:**
sudo requires YOUR password (or no password if configured that way),
not root's password. This means: root's password doesn't need to
be shared or even set. Multiple admins can have sudo access without
knowing a shared root password. If one admin leaves: remove them
from sudoers, without changing root's password.

**The sudoers file - a policy engine:**
`/etc/sudoers` defines what each user (or group) can do:
```
# Format: WHO WHERE=(AS_WHO) COMMAND
alice ALL=(ALL) ALL
# alice: can sudo from anywhere, as any user, any command

alice ALL=(ALL) /usr/bin/systemctl
# alice: can only run systemctl as root, nothing else

%admin ALL=(ALL) NOPASSWD: /sbin/reboot
# group admin: can reboot without entering password

deploy ALL=(ALL) NOPASSWD: /opt/deploy/deploy.sh
# deploy user: can ONLY run that specific script without password
```

---

### Thought Experiment

Three privilege models for a production database server:

**Model A: Everyone has root via shared password**
- All DBAs know the root password
- One DBA accidentally drops all tables as root
- Another DBA shares the password with an intern
- No audit: impossible to know who did what
- Changing the password requires telling everyone the new one

**Model B: No root access, contact IT**
- DBA needs to restart postgres: ticket submitted, 4-hour wait
- Emergency at 3am: no one available to grant access
- Operations slowed to a crawl

**Model C: Fine-grained sudo (correct)**
```
%dba ALL=(ALL) /bin/systemctl restart postgresql
%dba ALL=(ALL) /usr/bin/pg_dump
%dba ALL=(postgres) /bin/psql
```
- DBAs can restart postgres, dump databases, run psql as postgres user
- Cannot install packages, delete system files, or read /etc/shadow
- Every sudo logged: alice restarted postgresql at 03:15:32
- Easy to revoke: remove from %dba group

---

### Mental Model / Analogy

sudo is like **temporary administrator access at a company:**

```
Regular employee (alice): can access her own desk and files
Root (sysadmin): master key to the whole building

Without sudo (using su to root):
  Employee gets a master key copy permanently
  Now: anything goes wrong at the building? alice did it?
  Master key lost? Change all locks.
  
With sudo:
  alice wants to access the server room (restricted area)
  She asks security (sudo): "I need to install nginx"
  Security checks the list (/etc/sudoers):
    "alice is allowed to run /usr/bin/apt install"
  Security logs: "alice opened server room at 10:30am to run apt"
  Security gives her a KEY for exactly that door, for 15 minutes
  After 15 minutes: key expires (sudo credential cache timeout)
  
  alice cannot access the vault (sensitive data) - not in the list
  alice cannot modify the security list - not allowed
```

---

### Gradual Depth - Five Levels

**Level 1:**
`sudo command` runs as root. Needs entry in sudoers (or being in sudo/wheel group).
Logged to /var/log/auth.log. `visudo` to edit sudoers safely.
Never directly edit /etc/sudoers (no syntax checking -> lockout risk).

**Level 2:**
Sudoers directives: NOPASSWD: avoids password prompt (good for automation).
`Cmnd_Alias SERVICES = /bin/systemctl restart nginx, /bin/systemctl restart app`
then `alice ALL=(ALL) NOPASSWD: SERVICES`. /etc/sudoers.d/ directory: drop-in
files that extend the main sudoers config (package installs add files here).

**Level 3:**
sudo -e (sudoedit): safely edit files owned by root, using your own editor,
without giving sudo access to the editor itself (editors can be used for
privilege escalation). `sudo -k`: expire the credential cache immediately.
`sudo -v`: extend the credential timeout without running a command.
`sudo -s -u postgres`: run a shell as postgres user.

**Level 4:**
Privilege escalation via sudo misconfigurations - classic CTF/pentest material:
`(ALL) NOPASSWD: ALL` = effectively root. `(ALL) /usr/bin/vim`: can use
vim's `:!bash` to get a shell. `(ALL) /usr/bin/python3`: can run any code.
GTFOBins (gtfobins.github.io) catalogs: for every program, how to use
sudo permission on it to escalate to root. Security principle: only grant
sudo for specific scripts under your control, never for general-purpose tools.

**Level 5:**
Beyond sudo: PAM (Pluggable Auth Modules) controls the authentication
flow. `pam_google_authenticator.so` adds TOTP to sudo. `pam_duo.so`
adds Duo MFA. Enterprise: LDAP-integrated sudo with centralized policy.
Just-in-time access: engineers request sudo permission for a specific
time window, gets approved, automatically expires. Privileged Access
Workstations (PAW): dedicated, hardened machines for privileged operations,
with network isolation from regular machines.

---

### Code Example

**BAD - sudo security anti-patterns:**
```bash
# BAD 1: giving unrestricted sudo
# /etc/sudoers:
alice ALL=(ALL) ALL
# alice can run ANY command as root - no restriction

# BAD 2: sudo with ALL and NOPASSWD (worst possible)
alice ALL=(ALL) NOPASSWD: ALL
# alice becomes effectively root with no password required
# A compromised alice account = root compromise

# BAD 3: sudo for general-purpose tools
# /etc/sudoers:
deploy ALL=(ALL) NOPASSWD: /usr/bin/vim
# vim can open a shell: :!bash -> instant root shell
# See: gtfobins.github.io/gtfobins/vim/

# BAD 4: editing sudoers directly (bypasses syntax check)
nano /etc/sudoers    # syntax error -> lock yourself out!
# Always use:
sudo visudo          # validates syntax before saving

# BAD 5: using sudo to start a root shell for "convenience"
sudo bash            # everything you do is as root
                     # easy to accidentally break things
                     # no specific audit trail ("ran bash")
```

**GOOD - minimal, specific sudo grants:**
```bash
# GOOD 1: specific command allowance
# /etc/sudoers (use visudo!):

# Allow alice to restart specific services only:
alice ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx, \
                           /bin/systemctl restart myapp, \
                           /bin/systemctl status nginx, \
                           /bin/systemctl status myapp

# Allow deploy user to run specific deployment script:
deploy ALL=(ALL) NOPASSWD: /opt/deploy/deploy.sh

# Allow DBAs (group) to manage postgresql:
%dba ALL=(ALL) NOPASSWD: /bin/systemctl restart postgresql
%dba ALL=(postgres) /usr/bin/psql

# GOOD 2: use sudoers.d directory for organized management:
# /etc/sudoers.d/alice (chmod 440)
alice ALL=(ALL) /bin/systemctl restart nginx

# /etc/sudoers.d/deploy (chmod 440)
deploy ALL=(ALL) NOPASSWD: /opt/deploy/deploy.sh

# GOOD 3: audit sudo usage regularly
# View recent sudo commands:
sudo grep sudo /var/log/auth.log | tail -20
# Or with journalctl:
journalctl _COMM=sudo | tail -20

# GOOD 4: safely edit system files without full sudo access
sudo -e /etc/nginx/nginx.conf   # uses your editor securely
                                # creates temp file, you edit,
                                # sudo copies back (prevents
                                # editor-based privilege escalation)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`sudo bash` is the same as logging in as root" | `sudo bash` starts a root shell but your terminal history still shows you ran bash. Better audit: specific `sudo command` logs what you actually did. Both are root shells, but specific commands are preferred for traceability. |
| "sudo requires knowing root's password" | sudo requires YOUR password (or NOPASSWD). Root's password doesn't need to be known or even set. `sudo passwd -l root` locks root's password while sudo still works. |
| "The sudo group gives full root" | On Ubuntu, the `sudo` group gives `ALL=(ALL) ALL` sudo access by default (full root via password). On RHEL, the `wheel` group. These are default configs but can be changed. Always check your sudoers. |
| "sudo logs everything you do as root" | sudo logs the COMMAND INVOCATION. `sudo bash` logs that you ran bash, not the commands you ran inside. `sudo bash -c "rm -rf /etc"` logs only the command string - but what the command does is in system logs, not sudo logs. |
| "If sudo is not installed, use su" | `su` requires root's password (or target user's password). On modern systems, root's password is often unset. Without sudo and without root's password, you cannot escalate privileges (by design). |

---

### Failure Modes & Diagnosis

**"user is not in the sudoers file. This incident will be reported.":**
```bash
# Cause: user not in sudoers group or file
whoami          # check current user
groups          # check group membership (should include sudo or wheel)

# Fix on Ubuntu (as root or another sudoer):
usermod -aG sudo alice

# Fix on RHEL:
usermod -aG wheel alice

# Note: alice must log out and back in for group change to take effect
# Or: use newgrp sudo (changes group in current session)

# If NO sudoers available (locked out):
# Boot to single-user/recovery mode
# Or: use cloud provider's console to get a root shell
```

**sudo timeout and repeated password prompts:**
```bash
# Default: sudo credential cache expires after 15 minutes
# Change the timeout:
# /etc/sudoers:
Defaults        timestamp_timeout=60   # 60 minutes

# Extend current session without running a command:
sudo -v

# Invalidate cached credentials immediately:
sudo -k

# Per-user timeout:
Defaults:alice  timestamp_timeout=30
```

**Security: sudo GTFOBins escalation:**
```bash
# If you have: alice ALL=(ALL) /usr/bin/less
# You can escalate to root shell:
sudo less /etc/hosts
# Then type: !bash    (runs bash as root)
# Or: !sh

# Prevention: never grant sudo for:
# vim, nano, less, more, ed, find, awk, python, perl, ruby,
# bash, sh, tar (with --checkpoint), zip, wget, curl
# Check GTFOBins for a complete list: gtfobins.github.io

# Safe alternatives: use sudoedit for file editing
# Use specific wrapper scripts instead of general-purpose tools
```

---

### Related Keywords

**Foundational:**
LNX-011 (Users and Groups), LNX-010 (File Permissions)

**Builds on this:**
LNX-038 (User and Group Management in Depth),
LNX-057 (Security Hardening), LNX-078 (Capabilities)

**Related:**
SEC-001 (Security), IAM-001 (Identity and Access Management)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `sudo command` | Run command as root |
| `sudo -u user command` | Run as specific user |
| `sudo -l` | List your sudo permissions |
| `sudo -i` | Start a root login shell |
| `sudo -e /etc/file` | Safely edit a root-owned file |
| `sudo -k` | Invalidate credential cache |
| `sudo -v` | Refresh credential cache (no command) |
| `sudo visudo` | Safely edit /etc/sudoers |
| `usermod -aG sudo user` | Add user to sudo group (Debian) |
| `usermod -aG wheel user` | Add user to sudo group (RHEL) |
| `journalctl _COMM=sudo` | View sudo audit log |

**3 things to remember:**
1. Always use `visudo` to edit sudoers - direct editing with syntax errors = lockout
2. Grant minimum needed: specific commands only, not `ALL=(ALL) ALL`
3. Never grant sudo for general editors/interpreters (vim, python, etc.) - see GTFOBins

---

### Transferable Wisdom

The sudo model (temporary elevated permission, logged, for a specific
action) is replicated in: AWS IAM role assumption (STS AssumeRole -
temporary credentials for specific actions), Kubernetes RBAC (ClusterRole
binding - specific verbs on specific resources), database GRANT (specific
operations on specific tables), and Just-In-Time (JIT) access management
tools (Teleport, BeyondTrust). The pattern is universal: **deny by
default, explicit grant for specific actions, time-limited, audited**.

Understanding why `sudo vim` is dangerous (vim can open a shell)
teaches the broader concept of **indirect privilege escalation**: an
attacker who can run any general-purpose tool as root effectively
HAS root. This is why zero-trust security models grant permissions
on specific operations, not tools.

---

### The Surprising Truth

On Ubuntu, the default sudo configuration has a 15-minute credential
cache. This means: after you authenticate once with `sudo`, any subsequent
`sudo` command within 15 minutes runs WITHOUT re-authentication. This
is convenient but creates a window: if you run `sudo apt install something`
and then immediately execute a malicious script (which you downloaded
and ran), the script can run `sudo arbitrarycommand` without any password
prompt during that 15-minute window. This is one of the main attack
vectors for "sudo escalation" malware: make the user run sudo for
something legitimate, then immediately exploit the cached credential.
The defense: `Defaults timestamp_timeout=0` in sudoers (re-authenticate
every time) or `Defaults timestamp_type=tty` (cache per-terminal).
macOS uses the same credential caching mechanism with the same risk.

---

### Mastery Checklist

- [ ] Can add a user to sudo group and explain when it takes effect
- [ ] Can write specific sudoers entries that grant only required permissions
- [ ] Can use visudo safely and know why direct editing is dangerous
- [ ] Can audit sudo usage via auth.log or journalctl
- [ ] Can explain why granting sudo for vim/python is a security risk

---

### Think About This

1. A developer says: "I always start with `sudo -i` at the beginning
   of my work session so I don't have to type sudo repeatedly." What
   are the risks of this approach from both a security and operational
   perspective? What's a better pattern?

2. You discover this in /etc/sudoers: `%developers ALL=(ALL) NOPASSWD: ALL`.
   This was added to "make development easier." What are the immediate
   security implications? How would you remediate this without disrupting
   the development team's workflow?

3. A CTF challenge gives you sudo permission to run `/usr/bin/find`.
   How would you use find to escalate to a root shell? (Hint: find has
   an -exec flag.) What does this tell you about how you should configure
   sudo in production systems?

**TYPE G:** A 200-person engineering organization needs root access
management for 1,000 production servers. Requirements: (1) no shared
root passwords, (2) all privileged access audited, (3) access is
just-in-time (approved per session, automatically expires), (4) emergency
access possible 24/7 with appropriate approval, (5) works for both
human engineers and CI/CD automation. Design the complete privileged
access management architecture.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `sudo` and `su`?
A: `su` (substitute user) switches to another user's identity for an entire shell session. `su -` switches to root and loads root's environment. It requires KNOWING THE TARGET USER'S PASSWORD (typically root's password). `sudo` (superuser do) runs a SPECIFIC COMMAND with elevated privileges. It requires YOUR OWN PASSWORD and permission in /etc/sudoers. Key differences: (1) sudo uses your credentials + an authorization policy; su uses the target's credentials. (2) sudo logs every command; su only logs the session start. (3) sudo grants minimal scope (one command); su grants full shell as target user. (4) sudo doesn't require root's password to be set or known; su does. Modern Linux practice: sudo for privilege escalation, `su - username` only for switching to service accounts (e.g., `su - postgres` to manage the database).

**Intermediate:**
Q: How do you write a sudoers rule that allows a deploy user to run a deployment script without a password?
A: Use `sudo visudo` to edit safely. Add: `deploy ALL=(ALL) NOPASSWD: /opt/deploy/deploy.sh`. Breaking this down: `deploy` = the user (can be `%groupname` for a group). `ALL` = from any host (in a centralized sudoers, you might restrict to specific hosts). `(ALL)` = can run as any user (typically root). `NOPASSWD:` = no password required. `/opt/deploy/deploy.sh` = ONLY this specific script. Security considerations: (1) the script path must be absolute. (2) the script file should be owned by root and not world-writable (`chmod 750` or `chmod 755`, owned by root). (3) if the script accepts arguments, arguments can be restricted or not. For automation, NOPASSWD is necessary (CI/CD can't enter a password). Prefer placing this in `/etc/sudoers.d/deploy` (a drop-in file) rather than the main sudoers file for organization.

**Expert:**
Q: A security audit finds that a user has sudo permission to run /usr/bin/python3. Explain the privilege escalation risk and how to remediate.
A: The risk: python3 with sudo access allows a user to run arbitrary Python code as root. Examples: `sudo python3 -c "import os; os.system('/bin/bash')"` - instant root shell. Or: `sudo python3 exploit.py` - run any script as root. Even if restricted to specific Python scripts: `sudo python3 /opt/scripts/allowed.py`, python can be used to read/write any file, import arbitrary modules, or exec arbitrary commands. GTFOBins documents this as a common privilege escalation path. The general rule: never grant sudo permission to general-purpose interpreters (python, ruby, perl, php) or editors (vim, nano, emacs, ed) - they all provide shell access. Remediation: (1) identify what the user ACTUALLY needs python for (e.g., run a specific data migration script). (2) Create a wrapper shell script that does only that specific task. (3) Grant sudo on the wrapper script instead: `user ALL=(ALL) NOPASSWD: /opt/scripts/migrate-data.sh`. (4) Make the wrapper script root-owned, non-writable by the user (`chmod 750 /opt/scripts/migrate-data.sh; chown root:root /opt/scripts/migrate-data.sh`). (5) If the script must be customizable: use configuration files with limited scope rather than general Python execution.
