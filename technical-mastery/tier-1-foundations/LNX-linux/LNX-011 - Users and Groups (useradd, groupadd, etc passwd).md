---
id: LNX-011
title: "Users and Groups (useradd, groupadd, /etc/passwd)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-010
used_by: LNX-019, LNX-038
related: LNX-010, LNX-019, LNX-038
tags: [users, groups, useradd, groupadd, /etc/passwd, /etc/shadow, identity]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/lnx/users-and-groups/
---

## TL;DR

Linux is a multi-user OS. Every process runs as a user (uid).
Every file is owned by a user and group. Users are defined in
/etc/passwd, passwords in /etc/shadow, groups in /etc/group.
`useradd` creates users, `groupadd` creates groups, `usermod`
modifies them. In production: applications should run as
dedicated service accounts (not root), with membership in
specific groups for access control.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-011 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | users, groups, useradd, /etc/passwd, /etc/shadow, service accounts |
| **Prerequisites** | LNX-010 |

---

### The Problem This Solves

Without user separation, any program can do anything to any file.
Linux's user and group model enforces isolation: a web server
running as www-data cannot read /home/alice's private files.
If the web server is compromised, the attacker has www-data
privileges - not root. This containment is fundamental to
Linux security architecture.

---

### Textbook Definition

A **user** in Linux is an identity that owns processes and files.
Represented internally as a numeric uid (user ID). Special: uid 0
= root (superuser). System users: uid 1-999 (services, daemons).
Regular users: uid 1000+ (humans).

A **group** is a collection of users that share a permission context.
Represented as a numeric gid. Every user has a primary group and
may belong to supplementary groups.

Key files:
- `/etc/passwd`: user accounts (username, uid, gid, home, shell)
- `/etc/shadow`: hashed passwords (root-readable only)
- `/etc/group`: group definitions (group name, gid, members)

---

### Understand It in 30 Seconds

```
/etc/passwd format (not actual passwords):
  username:x:uid:gid:comment:home:shell
  alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
  nginx:x:999:999:Nginx web server:/var/lib/nginx:/sbin/nologin
  
/etc/shadow format (hashed passwords, root-readable only):
  alice:$6$salt$hash...:18001:0:99999:7:::

/etc/group format:
  groupname:x:gid:member1,member2
  sudo:x:27:alice,bob
  www-data:x:33:nginx

Commands:
  useradd -m alice           # create user with home dir
  useradd -r -s /sbin/nologin nginx  # system user, no login
  groupadd developers        # create group
  usermod -aG sudo alice     # add alice to sudo group
  id alice                   # show alice's uid, gid, groups
  who                        # who is logged in now
  whoami                     # who am I (current user)
```

---

### First Principles

**Identity as numbers, not names:**
Linux kernel works with uid/gid numbers. `/etc/passwd` maps
numbers to names. This is why you can set uid=1001 without an
entry in /etc/passwd - the kernel works fine with orphaned uids.
This matters for containers: uid 1000 inside a container = uid 1000
on host (unless user namespaces are used).

**Service accounts (system users):**
Applications should NOT run as root. Create a system user:
- useradd -r (system user: uid < 1000)
- useradd -s /sbin/nologin (no login shell: cannot be SSH'd into)
- useradd -M (no home directory: no personal files needed)
This is how nginx, postgres, redis, kafka all run.

---

### Thought Experiment

You're deploying a Java application server. Three choices:

A) Run as root: full system access. One vulnerability = full system compromise.

B) Run as your personal account (alice): can access alice's personal files,
   keys, etc. One vulnerability = alice's data compromised.

C) Create a dedicated appuser account with only access to what it needs:
   home at /opt/myapp, can read /etc/myapp/config, can write /var/log/myapp.
   One vulnerability = limited blast radius.

Option C is correct. This is the security principle of least privilege
applied to process identity.

---

### Mental Model / Analogy

Users and groups are like **employee badges** in a corporation:

```
Every employee (process) has a badge (uid)
Badges grant access to certain doors (file permissions)

Special badges:
  Master key (root uid=0): opens everything
  IT staff (system users): access to server rooms
  Regular employees (uid 1000+): access to their own office
  
Group badges (like department roles):
  Engineering badge: access to dev servers
  Admin badge: access to sudo
  www-data badge: access to web content
  
When someone leaves (process exits):
  Badge is returned (uid still exists, but process gone)
  Files they created: still have their uid/gid on them
```

---

### Gradual Depth - Five Levels

**Level 1:**
root (uid=0) = superuser = can do anything. Your login account
= uid 1000+. sudo = temporarily acts as root. System services
(nginx, postgres) = system users (uid < 1000). Never run
applications as root if you can avoid it.

**Level 2:**
Create system user for app: `useradd -r -s /sbin/nologin -d /opt/myapp myappuser`.
Add to group for log access: `usermod -aG appadmin myappuser`.
Check memberships: `id myappuser`. Change file ownership: `chown myappuser:myappuser /etc/myapp/`.

**Level 3:**
Password aging and locking: `chage -E 2024-12-31 alice` (expire account).
`passwd -l alice` (lock account). /etc/shadow fields: last change,
min days, max days, warning days, inactive days, expire date.
`/etc/skel/`: template files copied to new user's home on creation.

**Level 4:**
PAM (Pluggable Authentication Modules): controls authentication,
authorization, session management. /etc/pam.d/ configs control
login behavior. LDAP/Active Directory integration: sssd daemon
maps LDAP users to local Linux identities. Sudo configuration
(/etc/sudoers): fine-grained: alice can run /bin/systemctl start
as root only. `visudo` for safe editing.

**Level 5:**
User namespaces in containers: uid 0 inside container = uid 65534
(nobody) on host. Prevents container root from being host root.
Rootless containers (Podman, rootless Docker). Enterprise identity:
LDAP, Kerberos, FreeIPA. SSO with SSSD for dynamic user creation.
Audit logging (auditd): track which uid did what, when.

---

### Code Example

**BAD - running as root:**
```dockerfile
# BAD Dockerfile - running as root
FROM ubuntu:22.04
COPY app.jar /app/
CMD ["java", "-jar", "/app/app.jar"]
# Runs as root (uid=0) - security risk!
```

**GOOD - dedicated service user:**
```dockerfile
# GOOD Dockerfile - dedicated service user
FROM ubuntu:22.04

# Create system user and group for app
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -s /sbin/nologin \
            -d /opt/myapp appuser

# Create necessary directories with correct ownership
RUN mkdir -p /opt/myapp /var/log/myapp /etc/myapp && \
    chown -R appuser:appgroup /opt/myapp /var/log/myapp && \
    chmod 750 /opt/myapp /var/log/myapp

# Copy app files with correct ownership
COPY --chown=appuser:appgroup app.jar /opt/myapp/

# Switch to app user
USER appuser

# Run with explicit user
CMD ["java", "-jar", "/opt/myapp/app.jar"]
```

```bash
# System user creation on the host
# Create dedicated user for Java application
sudo useradd \
  --system \                    # uid < 1000 (system account)
  --no-create-home \            # no /home/myapp directory
  --shell /usr/sbin/nologin \   # cannot SSH login
  --comment "MyApp Service" \
  --user-group \                # create matching group
  myapp

# Verify:
id myapp
# uid=999(myapp) gid=999(myapp) groups=999(myapp)

# Set up directories
sudo mkdir -p /opt/myapp /var/log/myapp /etc/myapp
sudo chown myapp:myapp /opt/myapp /var/log/myapp
sudo chmod 750 /opt/myapp /var/log/myapp
sudo chmod 755 /etc/myapp  # config readable by root, app

# Add to supplementary group if needed
sudo usermod -aG appadmin myapp  # for log shipping access
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "System users cannot be used for anything" | System users (uid < 1000) are just a convention. They CAN own files, run processes, and be members of groups. The only difference: most distros don't create home directories for them by default. |
| "/etc/passwd contains passwords" | The 'x' in the password field means: look in /etc/shadow. /etc/passwd is world-readable (needed for uid-to-name lookups). /etc/shadow is root-readable only and contains the actual hashed passwords. |
| "Root can bypass file permissions" | Root bypasses DAC (discretionary access control = standard file permissions). Root does NOT automatically bypass MAC (mandatory access control = SELinux, AppArmor) without specific permissions in the policy. |
| "Deleting a user removes their files" | `userdel alice` removes the entry from /etc/passwd and /etc/shadow but does NOT remove alice's files. To also remove home: `userdel -r alice`. Files elsewhere still exist with orphaned uid. |
| "Groups can own processes" | Processes have a real uid and effective uid, and a list of supplementary gids. But the "running user" is the uid, not the gid. Groups are used for file access, not for process identity per se. |

---

### Failure Modes & Diagnosis

**Service cannot access its own files after user creation:**
```bash
# Problem: created user but files still owned by root
ls -la /opt/myapp/   # -rw-r--r-- root root app.jar

# Diagnosis: check what user the service runs as
ps aux | grep myapp  # shows: root (wrong!)

# Fix 1: fix file ownership
chown -R myapp:myapp /opt/myapp/

# Fix 2: fix systemd unit to run as myapp
# /etc/systemd/system/myapp.service:
[Service]
User=myapp
Group=myapp
```

**Container processes writing files as wrong user:**
```bash
# Problem: files written inside container are owned by root on host
docker run -v /data:/data myapp
ls -la /data/  # -rw-r--r-- root root output.txt (owned by root!)

# Cause: container ran as root (uid=0) = host uid=0 = root
# Fix: use USER in Dockerfile (as shown in code example above)
# OR: use --user flag:
docker run -u 1000:1000 -v /data:/data myapp
```

**Security: uid collision in containers:**
```bash
# Risk: container uid=1000 = host uid=1000 (possibly alice)
# Container can access files owned by uid=1000 on mounted volumes

# Solution: use user namespaces (rootless containers)
# Podman uses user namespaces by default
# Docker: enable userns-remap in /etc/docker/daemon.json
# {"userns-remap": "default"}
# This maps container uid=0 to a high host uid (65536+)
```

---

### Related Keywords

**Foundational:**
LNX-010 (File Permissions), LNX-019 (sudo)

**Builds on this:**
LNX-038 (User Management in Depth), LNX-057 (Security Hardening),
LNX-078 (Linux Capabilities)

**Related:**
IAM-001 (Identity and Access Management), SEC-001 (Security)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `useradd -m alice` | Create user with home directory |
| `useradd -r -s /sbin/nologin svc` | Create system service user |
| `groupadd mygroup` | Create group |
| `usermod -aG group user` | Add user to supplementary group |
| `userdel -r alice` | Delete user and home directory |
| `id user` | Show uid, gid, groups |
| `who` | Who is logged in |
| `whoami` | Current user name |
| `passwd alice` | Change alice's password (as root) |
| `su - alice` | Switch to alice's shell |
| `groups` | Show current user's groups |

**3 things to remember:**
1. Applications should run as dedicated system users (not root)
2. /etc/passwd is public; /etc/shadow is private (hashed passwords)
3. uid 0 = root everywhere; container uid 0 = host uid 0 without user namespaces

---

### Transferable Wisdom

The **service account pattern** (each service = dedicated user) is
the same as: AWS IAM roles (each service = IAM role with specific
permissions), Kubernetes service accounts (each pod = service account),
database users (each app = db user with specific grants). The pattern
is universal: identity isolation prevents one compromise from spreading.

The **numeric uid** model (Linux works with numbers; /etc/passwd maps
names) is the same as: AWS account IDs (numbers; IAM maps roles to
names), database numeric IDs for users. Understanding the primitive
(number) vs. the representation (name) prevents confusion when they
diverge (orphaned files, user namespace remapping).

---

### The Surprising Truth

The `nobody` user (uid=65534) and `nogroup` group exist on most
Linux systems specifically as the "least privileged" identity. When
NFS mounts files from a server where the uid doesn't exist locally,
files are shown as owned by "nobody." Docker uses a similar convention:
the "nobody" user in containers has no privileges. Some security-hardened
containers run as uid=65534 specifically because it represents the maximum
possible distance from uid=0 (root) in a 16-bit uid space. Modern
systems with 32-bit uids use 65534 for the same symbolic reason.

---

### Mastery Checklist

- [ ] Can create a system service user with no login shell
- [ ] Can explain the difference between /etc/passwd and /etc/shadow
- [ ] Can add a user to a supplementary group and explain when this takes effect
- [ ] Can diagnose a "Permission denied" caused by wrong process uid
- [ ] Can set up correct ownership for a Java application's directories

---

### Think About This

1. When you add a user to a group with `usermod -aG sudo alice`, the
   change takes effect for NEW login sessions, not the current one.
   Why? What Linux mechanism determines a process's group membership,
   and when is it set?

2. Docker containers share the host kernel, and uid 1000 inside a
   container is uid 1000 on the host. If you mount a host directory
   into a container and your container runs as uid 1000 but the host
   user alice (also uid 1000) owns those files, what can the container
   do to alice's files? Why is this a security concern?

3. The `su` command switches to another user. The `sudo` command runs
   a specific command as another user. They seem similar - what makes
   sudo safer than su for system administration?

**TYPE G:** A company's security policy requires: (1) no application
runs as root, (2) every service has a dedicated service account, (3)
log files are accessible to a central log shipper but not other services,
(4) config files are readable by the app but not other apps. Design the
complete user, group, and permission scheme for a three-tier application:
nginx (web), tomcat (app server), postgresql (database).

---

### Interview Deep-Dive

**Foundational:**
Q: Why should production applications not run as root?
A: Running as root means that if the application is compromised (SQL injection, RCE vulnerability, dependency vulnerability), the attacker immediately has root access to the entire system. With root, they can: read all files (including other apps' credentials), modify system binaries, install backdoors, exfiltrate data. Running as a dedicated service user with minimal permissions contains the blast radius: the attacker can only access what that service user can access, not the entire system.

**Intermediate:**
Q: How do you create a proper service user for a Java application and ensure it can only access what it needs?
A: `useradd --system --no-create-home --shell /usr/sbin/nologin --user-group myapp`. Then set ownership: `chown -R myapp:myapp /opt/myapp /var/log/myapp`. Set permissions: `chmod 750 /opt/myapp /var/log/myapp` (app can read/write/execute, group members can read/execute, others nothing). For config: `chown root:myapp /etc/myapp/config.yaml; chmod 640 /etc/myapp/config.yaml` (root owns it to prevent tampering, app can read, others cannot). In the systemd unit: `User=myapp; Group=myapp`. Verify: `sudo -u myapp cat /etc/myapp/config.yaml` should succeed; `sudo -u myapp cat /etc/shadow` should fail.

**Expert:**
Q: Explain the relationship between Linux uids and Docker container isolation, and why running containers as root (uid=0) is a security risk even when processes are "isolated" by namespaces.
A: Docker containers share the host kernel. Namespace isolation (PID, network, mount) isolates the VIEW of resources, but not the uid space by default. If a container process runs as uid=0 (root), and it mounts a host directory, it has root access to files in that mount. If a container escape vulnerability exists (kernel bug, runc exploit like CVE-2019-5736), the escaping process has host root access. With user namespaces enabled (userns-remap), uid=0 inside the container maps to a high host uid (e.g., 65536+) that has no host privileges. The container appears to run as root internally (for compatibility), but gains no special host privileges. This is why: (1) Dockerfile USER directive should specify a non-root uid; (2) Kubernetes SecurityContext should set runAsNonRoot: true; (3) OPA/Gatekeeper policies should enforce non-root containers in production clusters.
