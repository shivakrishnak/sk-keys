---
id: LNX-038
title: "User and Group Management in Depth"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-010, LNX-009
used_by: LNX-057, LNX-078
related: LNX-010, LNX-009, IAM-001
tags: [useradd, usermod, groupadd, passwd, shadow, sudoers, service-account, uid, gid]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/lnx/user-group-management/
---

## TL;DR

Linux users are defined in `/etc/passwd` (7 fields, world-readable),
passwords hashed in `/etc/shadow` (root-only). `useradd -m -s /bin/bash
-G sudo alice` creates user alice with home, bash shell, sudo access.
`usermod -aG docker bob` adds bob to docker group (without removing existing
groups - the `-a` is critical). Service accounts use `useradd -r -s
/sbin/nologin appname` (no home, no login). `id`, `groups`, and `whoami`
show current identity. Principle: run services as dedicated users, not root.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-038 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | useradd, usermod, groupadd, /etc/passwd, /etc/shadow, sudo, service account |
| **Prerequisites** | LNX-010, LNX-009 |

---

### The Problem This Solves

You deploy a Java application. If it runs as root: a vulnerability in the
app gives an attacker full root access. If it runs as a dedicated `appuser`
with minimal permissions: the attacker gets a low-privilege account with
access only to what `appuser` needs. Creating service accounts is Linux
security hygiene. Similarly: `usermod -aG docker bob` (without `-a`) would
remove bob from ALL other groups - a common mistake that breaks sudo access.

---

### Textbook Definition

**/etc/passwd**: The user account database. World-readable (no passwords here).
Format: `username:x:UID:GID:comment:home:shell` (7 colon-separated fields).
`x` in password field means: see `/etc/shadow`.

**/etc/shadow**: Hashed passwords + expiration policy. Root-readable only.
Format: `username:$algorithm$salt$hash:last_change:min:max:warn:inactive:expire`.

**/etc/group**: Group membership database. Format: `groupname:x:GID:members`.

**UID/GID ranges (typical):**
- 0 = root
- 1-999 = system/service accounts (some distros: 1-499 or 1-200)
- 1000+ = regular user accounts

**Primary group vs supplementary groups**: Each process runs with one
primary GID (from /etc/passwd) and potentially many supplementary GIDs
(from /etc/group membership). `id` shows all.

---

### Understand It in 30 Seconds

```bash
# Create a regular user:
useradd -m -s /bin/bash alice       # -m: create home, -s: shell
useradd -m -s /bin/bash -G sudo,developers alice  # add to groups

# Set password:
passwd alice          # interactive
echo "alice:secretpassword" | chpasswd  # scripted (avoid in production)

# Create a service account (no login, no home):
useradd -r -s /sbin/nologin myapp
# -r: system account (UID < 1000), -s /sbin/nologin: no shell login

# Modify existing user:
usermod -aG docker bob    # add bob to docker group (KEEP existing groups)
usermod -s /bin/zsh alice  # change shell
usermod -L alice           # lock account (disable login)
usermod -U alice           # unlock account
usermod -d /data/alice -m alice  # change home dir and move files

# Delete user:
userdel alice          # remove user (keep home directory)
userdel -r alice       # remove user AND home directory

# Groups:
groupadd developers          # create group
groupadd -g 1500 developers  # create with specific GID
groupdel developers          # delete group
gpasswd -d alice developers  # remove alice from developers

# Check current identity:
id                   # uid=1000(bob) gid=1000(bob) groups=1000(bob),27(sudo)
whoami               # bob
groups               # bob sudo docker (supplementary groups)
id alice             # check another user's identity

# View user info:
cat /etc/passwd | grep alice
# alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
getent passwd alice  # same but works with LDAP/NIS too

# View group membership:
cat /etc/group | grep alice  # might appear in multiple groups
getent group docker          # show docker group members

# Switch user:
su - alice           # switch to alice (full login, loads environment)
su alice             # switch to alice (no environment reset)
sudo -u alice command  # run single command as alice
```

---

### First Principles

**The /etc/passwd format:**
```
alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
  ^   ^ ^    ^    ^           ^           ^
  |   | |    |    |           |           Shell
  |   | |    |    |           Home directory
  |   | |    |    Comment/GECOS (full name)
  |   | |    Primary GID
  |   | UID
  |   'x' = password in /etc/shadow
  Username
```

**The /etc/shadow format:**
```
alice:$6$salt$hashedpassword...:19000:0:99999:7:::
  ^   ^                        ^     ^ ^     ^
  |   |                        |     | |     Warn days before expire
  |   |                        |     | Max days before must change
  |   |                        |     Min days between changes
  |   |                        Days since Jan 1, 1970 of last change
  |   Hashed password ($6 = SHA-512, $1 = MD5, $y = yescrypt)
  Username

'!' or '*' prefix in hash = account locked (no login possible)
'!' = locked by admin
'*' = never had password (system accounts)
```

**UID 0 is root (not the name 'root'):**
```bash
# You can have multiple UID 0 accounts (not recommended):
echo "backdoor:x:0:0::/root:/bin/bash" >> /etc/passwd
# This is a security red flag - audit for UID 0 accounts:
awk -F: '$3==0 {print $1}' /etc/passwd
# Should return ONLY "root"
```

---

### Thought Experiment

Creating a proper service account for a Java web application:

```bash
# BAD: Run as root (security nightmare)
java -jar myapp.jar   # if exploited, attacker gets root

# BETTER but incomplete: run as existing user
sudo -u nobody java -jar myapp.jar  # nobody is too restrictive

# BEST: dedicated service account
# Create service account:
useradd -r -s /sbin/nologin -d /opt/myapp -m myapp
# -r: system account (UID < 1000, won't be listed in login screens)
# -s /sbin/nologin: cannot log in via shell
# -d /opt/myapp: home directory is app directory
# -m: create the directory

# Set ownership:
chown -R myapp:myapp /opt/myapp
chmod 750 /opt/myapp

# Config files with secrets: only myapp can read
chmod 640 /opt/myapp/config/secrets.yaml
chown myapp:myapp /opt/myapp/config/secrets.yaml

# Log directory: myapp writes, others can read
mkdir /var/log/myapp
chown myapp:myapp /var/log/myapp
chmod 755 /var/log/myapp

# systemd service runs as myapp:
# [Service]
# User=myapp
# Group=myapp

# Verify:
id myapp
# uid=998(myapp) gid=998(myapp) groups=998(myapp)
# No sudo, no other groups - principle of least privilege
```

---

### Mental Model / Analogy

```
Users = employees in a company
UID = employee badge number (unique ID)
Username = name on the badge
/etc/passwd = employee directory (public, readable by all)
/etc/shadow = HR's secure vault (password hashes, access policy)

Groups = departments or teams
GID = department number
Primary group = your home department
Supplementary groups = teams you belong to (projects, committees)

'id' command = showing all your badges and department memberships

Service accounts = robots on the factory floor:
- They have badge numbers (UIDs)
- They cannot "log in" (no interactive shell)
- They have access only to the machines they operate
- Not listed in the regular employee directory

Root (UID 0) = building owner:
- Has master keys to everything
- Running applications as root = giving the entire building key 
  to untrusted contractors
```

---

### Gradual Depth - Five Levels

**Level 1:**
`useradd -m username` creates a user. `passwd username` sets password.
`id` shows who you are. `sudo -u alice command` runs as alice. That's
basic user management.

**Level 2:**
`-G group1,group2` adds to groups at creation. `usermod -aG` adds to
group without removing others (CRITICAL: the `-a` flag). `/etc/passwd`
7-field format. Service accounts: `-r -s /sbin/nologin`. `userdel -r`
deletes with home. `chpasswd` for scripted password changes.

**Level 3:**
`/etc/shadow` format and password hashing algorithms (`$6$` = SHA-512).
`getent passwd user` (works with LDAP/NIS, not just local files).
`chage` command: password expiration management (`chage -l alice`,
`chage -E 2025-12-31 alice` for account expiry). `/etc/skel`: files
copied to new home directories. `visudo` to safely edit `/etc/sudoers`.

**Level 4:**
`nsswitch.conf`: controls where user lookups go (files, ldap, sssd, etc.).
`sssd` (System Security Services Daemon): connects Linux to AD/LDAP.
`pam_limits.so`: PAM module that applies per-user resource limits from
`/etc/security/limits.conf`. `su` vs `sudo`: su authenticates as target
user; sudo authenticates as yourself and acts as target (all sudo actions
logged). Setuid executables: run as file owner regardless of who exec's them.

**Level 5:**
Linux namespaces include user namespaces (UID/GID isolation). Inside a
container user namespace: UID 0 maps to a non-root UID on the host. This
is how rootless containers (Podman, rootless Docker) work. `newuidmap`/
`newgidmap`: subUID/subGID mapping for user namespace configuration.
`/etc/subuid`, `/etc/subgid`: define the UID/GID ranges a user can use
in containers. `dbus-broker`, `systemd-homed`: modern user account
management moving beyond `/etc/passwd` toward portable home directories
and cryptographically protected user records.

---

### Code Example

**BAD - common user management mistakes:**
```bash
# BAD 1: usermod -G without -a (removes from all other groups!)
usermod -G docker bob
# This REPLACES bob's entire supplementary group list with just "docker"
# If bob was in sudo, now he can't sudo! Common disaster.

# GOOD: always use -a (append) with -G:
usermod -aG docker bob  # ADDS docker to bob's existing groups

# BAD 2: Storing password in command (visible in ps, shell history):
useradd -p "plaintextpassword" alice  # NEVER do this
# ps aux shows the command with the password!

# GOOD: use passwd interactively, or:
useradd alice
openssl passwd -6 -salt "$(openssl rand -hex 8)" "securepassword" | \
    usermod -p - alice
# Or: echo "alice:$password" | chpasswd

# BAD 3: Not using /sbin/nologin for service accounts:
useradd myapp   # defaults to /bin/bash shell
# Anyone who compromises the service can potentially
# su - myapp and get an interactive shell

# GOOD: explicit no-login shell:
useradd -r -s /sbin/nologin myapp
# If someone tries: su - myapp
# Output: "This account is currently not available."

# BAD 4: Forgetting -r for service accounts (gets UID >= 1000):
useradd -s /sbin/nologin myapp
# Gets UID 1001 (looks like a regular user)

# GOOD: use -r for system accounts (UID < 1000):
useradd -r -s /sbin/nologin myapp
# Gets UID 998 (system account range)
```

**GOOD - idempotent user management script:**
```bash
#!/bin/bash
# Idempotent: safe to run multiple times
ensure_user() {
    local username="$1"
    local groups="$2"
    
    if id "$username" &>/dev/null; then
        echo "User $username already exists"
    else
        useradd -r -s /sbin/nologin -d "/opt/${username}" -m "$username"
        echo "Created service account: $username"
    fi
    
    # Add to groups (idempotent):
    if [ -n "$groups" ]; then
        IFS=',' read -ra GROUP_LIST <<< "$groups"
        for group in "${GROUP_LIST[@]}"; do
            if ! groups "$username" | grep -q "\b${group}\b"; then
                usermod -aG "$group" "$username"
                echo "Added $username to group $group"
            fi
        done
    fi
}

ensure_user "myapp" ""
ensure_user "deploy" "docker"

# Verify:
id myapp
id deploy
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`usermod -G groupname user` adds the user to a group" | `usermod -G` REPLACES the user's entire supplementary group list. `usermod -aG groupname user` APPENDS to the existing list. Forgetting `-a` is a common mistake that silently removes the user from all other groups (including sudo). Always use `-aG`. |
| "/etc/shadow contains encrypted passwords" | `/etc/shadow` contains HASHED passwords, not encrypted ones. Encryption is reversible (you can decrypt to get the original). Hashing is one-way. SHA-512 hash (`$6$`) is used on modern systems. The hash cannot be reversed to get the password - only brute-force or dictionary attacks work. |
| "Deleting a user deletes all their files" | `userdel username` removes the user account but LEAVES the home directory intact. `userdel -r username` removes the account AND home directory. Files owned by the deleted UID on OTHER parts of the filesystem are NOT removed - they become orphaned (owned by a now-nonexistent UID). Find orphaned files: `find / -nouser 2>/dev/null`. |
| "The username 'root' is what gives superuser powers" | UID 0 grants superuser privileges, not the name "root". You could rename root to "admin" and it still has full privileges. Conversely, an account named "root" with UID 1001 has no special powers. `awk -F: '$3==0' /etc/passwd` shows all UID 0 accounts - there should be exactly one. |
| "Groups change take effect immediately" | Adding a user to a group with `usermod -aG` takes effect on the NEXT LOGIN. The currently running processes for that user still have the old group memberships. To apply without logout: `newgrp groupname` (opens a new shell with that group active) or `exec su -l $USER` (re-login in current terminal). |

---

### Failure Modes & Diagnosis

**`usermod -G docker bob` removed bob from sudo:**
```bash
# Symptom: bob can no longer use sudo after you "added" him to docker group

# Diagnosis:
id bob
# uid=1001(bob) gid=1001(bob) groups=1001(bob),999(docker)
# MISSING: 27(sudo) - was removed!

# Fix:
usermod -aG sudo bob   # add back to sudo
# Verify:
id bob
# uid=1001(bob) gid=1001(bob) groups=1001(bob),27(sudo),999(docker)

# Bob must log out and back in for groups to take effect:
# Or: sudo -i -u bob id   <- check as if freshly logged in
```

**Group change not taking effect:**
```bash
# Added user to docker group but 'docker ps' fails with permission denied
id $USER   # shows groups=1000(myuser) - no docker!

# Groups are loaded at LOGIN time
# The user needs to log out and back in
# Workaround (no logout):
newgrp docker   # open new shell with docker group active
docker ps       # now works

# Permanent fix: logout and login again
# OR: restart the user's SSH session
```

---

### Related Keywords

**Foundational:**
LNX-010 (Permissions), LNX-009 (sudo)

**Builds on this:**
LNX-057 (Security Hardening), LNX-078 (Linux Capabilities)

**Related:**
IAM-001 (Identity and Access Management)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `useradd -m -s /bin/bash user` | Create regular user with home |
| `useradd -r -s /sbin/nologin svc` | Create service account |
| `usermod -aG group user` | Add to group (keep existing) |
| `userdel -r user` | Delete user and home |
| `passwd user` | Set password |
| `id user` | Show UID, GID, groups |
| `groups user` | Show group memberships |
| `getent passwd user` | Full user info (LDAP-aware) |
| `chage -l user` | Password expiry info |
| `awk -F: '$3==0' /etc/passwd` | Find all root (UID 0) accounts |

**3 things to remember:**
1. `usermod -aG group user` (the `-a` is NOT optional - without it, you REPLACE all groups)
2. Service accounts: `useradd -r -s /sbin/nologin -d /opt/svc -m svc` (-r=system, nologin=no shell)
3. Group changes take effect at NEXT LOGIN - not immediately

---

### Transferable Wisdom

The "principle of least privilege" applied via service accounts is universal:
Docker container processes run as non-root (USER in Dockerfile), Kubernetes
pods specify `runAsUser` and `runAsNonRoot`, AWS Lambda functions run as
lambda user, systemd services specify `User=`, CI/CD pipeline agents run
as restricted service accounts. The pattern: create a dedicated account
with only necessary permissions, restrict its login shell, restrict its
home directory, add to only required groups.

The `/etc/passwd` -> `/etc/shadow` split teaches security design: put
sensitive data in separate, access-controlled storage. Only processes that
NEED the secret (login daemon, `passwd` command with setuid) can read it.
This principle appears in: AWS Secrets Manager (secrets in a separate
service), Vault (secrets separate from applications), Kubernetes Secrets
(separate API objects from regular ConfigMaps).

---

### The Surprising Truth

`/etc/passwd` is world-readable for a reason: many programs need to map
UIDs to usernames for display (`ls -la`, `ps aux`). But this means everyone
on the system can see all usernames. Originally, `/etc/passwd` DID contain
the actual password hash in field 2. It was only moved to `/etc/shadow`
in the 1980s-1990s when it was recognized that any user could run a
dictionary attack against the hashes by reading `/etc/passwd`. The
transition wasn't instant - for years many systems had `/etc/shadow`
optional or disabled. Even today, the `x` placeholder in field 2 is a
backwards-compatibility artifact from this transition. Systems using
`/etc/shadow` are called "shadow password" systems. The `john` (John the
Ripper) password cracker can crack SHA-512 hashes at millions of guesses
per second with modern GPUs - which is why modern systems add work factors
(cost parameters) with algorithms like yescrypt (`$y$`) to slow cracking.

---

### Mastery Checklist

- [ ] Can create regular and service accounts with appropriate options
- [ ] Can add a user to a group without removing existing memberships
- [ ] Can decode the /etc/passwd and /etc/shadow file formats
- [ ] Can check group memberships and understand when changes take effect
- [ ] Can create a least-privilege service account for a production application

---

### Think About This

1. You run `usermod -G docker myuser`. The user myuser cannot sudo anymore.
   What happened exactly, and how do you fix it without causing further
   damage? What is the safe command to add a user to a group?

2. A service account `appuser` has `/sbin/nologin` as its shell. An attacker
   exploits a vulnerability in the application running as `appuser`.
   Can the attacker execute arbitrary commands? Can they read files in
   `/opt/appuser/`? What does `/sbin/nologin` actually prevent?

3. You need to give the `appuser` account the ability to bind to port 443
   (normally requires root). How would you do this WITHOUT running the
   application as root and WITHOUT using setuid? (Hint: think about the
   CAP_NET_BIND_SERVICE Linux capability.)

---

### Interview Deep-Dive

**Foundational:**
Q: How do you create a service account for a Linux application that should not be able to log in interactively?
A: Use `useradd` with specific flags: `useradd -r -s /sbin/nologin -d /opt/myapp -m myapp`. Flag breakdown: `-r`: creates a system account with UID in the system range (typically < 1000 on Debian/Ubuntu). System accounts are excluded from display managers and login prompts. `-s /sbin/nologin`: the shell is set to `/sbin/nologin` (or `/usr/sbin/nologin` on some systems). If someone tries `su - myapp`, they get "This account is currently not available." The process can still be launched with this account by systemd or sudo (they bypass the shell restriction). `-d /opt/myapp`: home directory is the application directory. `-m`: creates the directory. After creation: set ownership `chown -R myapp:myapp /opt/myapp` and define in systemd: `[Service] / User=myapp / Group=myapp`. Verify with `id myapp` and `su - myapp` (should fail with appropriate message).

**Intermediate:**
Q: What is the difference between a user's primary group and supplementary groups, and what happens when usermod -G is used incorrectly?
A: Every process has one primary GID (from /etc/passwd) and potentially many supplementary GIDs (from /etc/group memberships). Files created by a user get the primary group as owner by default. Access checks consider BOTH primary and all supplementary groups. `usermod -G groupname username`: REPLACES the entire supplementary group list with just the specified group(s). If bob was in groups `sudo,developers,docker` and you run `usermod -G docker bob`, bob is now ONLY in `docker`. He lost sudo access! This is a common and dangerous mistake. `usermod -aG groupname username`: APPENDS the group to the existing list. The `-a` flag means "append." Group changes don't take effect for running processes - only on new login (new processes created after group change). Workaround: `newgrp groupname` opens a new shell with that group, or `exec su -l $USER` re-initializes the session.

**Expert:**
Q: How does Linux user namespace isolation enable rootless containers, and what are the security implications?
A: Linux user namespaces (added in kernel 3.8, enabled broadly in ~2017) allow mapping of UIDs/GIDs inside a namespace to different UIDs/GIDs outside. Key mechanism: (1) A process creates a new user namespace with `clone(CLONE_NEWUSER)` or `unshare -U`. (2) `/etc/subuid` maps ranges: `bob:100000:65536` means bob can use UIDs 100000-165535 in namespaces. (3) Inside the namespace, UID 0 (root) maps to the host user's UID. (4) `newuidmap`/`newgidmap` (setuid helpers) apply the mapping. Rootless containers (Podman): the entire container runs as the host user's UID. Inside the container, processes see themselves as root (UID 0). Outside, they're your regular user. Container filesystem is stored in `~/.local/share/containers/storage`. Each layer is owned by the real host UID. Security implications: (1) The container's "root" cannot actually access host root files (it's UID 1000 on the host). (2) Vulnerability exploitation yields access as the host user, not host root - significant reduction in blast radius. (3) Limitation: some operations require actual kernel privileges (mounting certain filesystems, using raw sockets). These are restricted even in rootless containers. (4) seccomp + no_new_privs prevents privilege escalation. `/etc/subuid` defines the privilege boundary - subUID ranges must be configured by a real admin. A rootless container can't give itself more UID mappings than its subUID allocation allows.
