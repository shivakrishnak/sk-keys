---
layout: default
title: "SELinux / AppArmor"
parent: "Linux"
nav_order: 159
permalink: /linux/selinux-apparmor/
number: "0159"
category: Linux
difficulty: ★★★
depends_on: Linux Security Hardening, Users and Groups
used_by: Containers, Kubernetes, Linux Security Hardening
related: Linux Namespaces, seccomp, Capabilities
tags:
  - linux
  - os
  - security
  - deep-dive
---

# 159 — SELinux / AppArmor

⚡ TL;DR — SELinux and AppArmor are Mandatory Access Control (MAC) systems that enforce a policy layer above Unix permissions — even root cannot bypass them; they confine processes to explicitly allowed operations.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Linux security is Discretionary Access Control (DAC): the file owner decides permissions. When a process runs as root, it can do anything — read any file, open any socket, load any kernel module. A compromise of any root-running service (nginx, sshd, containerised app) means full system compromise. The attacker can pivot to any file on the system.

**THE BREAKING POINT:**
An nginx web server runs as root (or drops to www-data too late). A buffer overflow exploit compromises nginx. Now the attacker has www-data's capabilities — which, in a typical setup, means access to the entire `/var/www/`, ability to make network connections, ability to read most system config files. There's no boundary. A web server should not need to read `/etc/shadow`, connect to arbitrary ports, or write to `/usr/bin/`. But without MAC, nothing prevents it.

**THE INVENTION MOMENT:**
SELinux (developed by the NSA, merged into Linux 2.6 in 2003) and AppArmor (developed by Immunix/Novell, merged 2006) both implement MAC: every process gets a label (SELinux) or a named profile (AppArmor). Access to any resource (file, socket, capability) must be explicitly allowed in the policy. Even root cannot do what the policy doesn't permit. nginx can only access files with the `httpd_sys_content_t` label, connect to specific port types, and nothing else — even if it's compromised.

---

### 📘 Textbook Definition

**Mandatory Access Control (MAC)** is a security model where access rules are set by a system policy and cannot be overridden by individual users, even root. Linux implements MAC via the **Linux Security Modules (LSM)** framework — a set of kernel hooks that allow security modules to intercept and authorise every security-relevant operation.

**SELinux** (Security-Enhanced Linux): label-based MAC. Every process, file, socket, and device has a security context (`user:role:type:level`). Access is allowed only when policy rules explicitly permit the source type to access the target type. Default: **deny all, allow explicitly**.

**AppArmor** (Application Armor): path-based MAC. Each process is confined by a named profile that specifies which filesystem paths, capabilities, and network operations it may perform. Simpler than SELinux but less fine-grained. Default: **deny all, allow explicitly per path**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SELinux/AppArmor add a mandatory policy layer that confines every process to only the operations it needs — even root can't escape the policy.

**One analogy:**

> Normal Linux permissions are like a hotel key card system — a master key (root) opens every door. SELinux/AppArmor add a mandatory rule book in the lobby: "Security staff may only enter server rooms; cleaning staff may only enter rooms on floors 2-4; the restaurant chef may only access the kitchen." Even if someone steals the master key, they must also get past the mandatory rule book, which the master key doesn't override. The rule book is enforced by a separate authority (the kernel LSM layer) that the key cannot bypass.

**One insight:**
The power of MAC is in the default-deny model: a process is only allowed operations explicitly in its policy. In SELinux, a 0-day in nginx that gains root still can't read `/etc/shadow` because nginx's type (`httpd_t`) has no policy rule allowing access to `shadow_t` files.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Default deny**: everything not explicitly allowed is denied.
2. **Mandatory**: no process can grant itself more access than the policy allows — not even root (`uid=0`).
3. **Subject-object model**: every access is (subject → operation → object); policy defines which (type, type, operation) combinations are allowed.
4. **Orthogonal to DAC**: MAC checks happen after DAC checks; both must pass. MAC cannot make something more permissive than DAC, only more restrictive.

**SELinux DERIVED DESIGN:**
Every resource has a security context: `system_u:system_r:httpd_t:s0`. The type (`httpd_t`) is the key identifier for policy decisions. Policy rules are `allow httpd_t httpd_sys_content_t:file { read open getattr };` — nginx (type `httpd_t`) may read files with type `httpd_sys_content_t`. The `audit.log` records every deny: `avc: denied { write } for ... scontext=httpd_t tcontext=shadow_t`. Modes: **enforcing** (deny + log), **permissive** (log only, don't deny — for policy development), **disabled**.

**AppArmor DERIVED DESIGN:**
Profiles are stored in `/etc/apparmor.d/`. A profile for nginx: `profile nginx /usr/sbin/nginx { /var/www/html/** r, /var/log/nginx/** w, network tcp, ... }`. Path-based: the profile names filesystem paths. Simpler to write and audit than SELinux type enforcement rules, but a hardlink or `chroot` can bypass path-based checks — a known limitation. Modes: **enforce** (deny + log), **complain** (log only).

**THE TRADE-OFFS:**
**SELinux:** Very fine-grained, label-based (hardlinks and mounts don't bypass it), trusted by government/financial sectors. Extremely complex to configure; a misconfigured policy is very hard to debug.
**AppArmor:** Path-based, simpler profiles, easier to write and understand. Used by Ubuntu, Snap, and Docker by default. Less strict (path renames can confuse profiles).

---

### 🧪 Thought Experiment

**SETUP:**
nginx is compromised. Attacker has code execution as `www-data`. The goal is to read `/etc/shadow` (password hashes) and write a backdoor to `/usr/bin/`.

**WITHOUT SELinux/AppArmor:**

1. `cat /etc/shadow` — readable if www-data has any path to it (unlikely), but attacker can try privilege escalation first.
2. Any SUID binary or kernel exploit → root.
3. Once root: `cat /etc/shadow` works, write to `/usr/bin/` works. Full compromise.

**WITH SELinux (enforcing):**

1. nginx process label: `httpd_t`. `/etc/shadow` label: `shadow_t`.
2. Policy rule `allow httpd_t shadow_t:file read` does NOT exist.
3. `cat /etc/shadow` → SELinux denies → logged in `/var/log/audit/audit.log`.
4. Even if the attacker escalates to root within the nginx process, SELinux type enforcement remains — `uid=0` with type `httpd_t` still cannot read `shadow_t`.
5. The attacker is confined to operations that `httpd_t` is explicitly allowed. The blast radius is dramatically reduced.

**THE INSIGHT:**
SELinux defeats even root-level compromises of confined processes. This is the core value proposition: contain the blast radius of a compromise to the minimum set of operations the process legitimately needs.

---

### 🧠 Mental Model / Analogy

> SELinux/AppArmor are like the separation of duties in a bank. A bank teller (process) has a badge (type/profile). The badge determines what the teller can access — specific vaults, specific drawers, specific systems. Even the CEO (root) follows the badge system — they have a CEO badge that allows more, but the badge system still applies. No badge, or the wrong badge, and you can't access a resource regardless of your seniority. A bank robber who takes a teller hostage gets the teller's badge — but that badge only opens the teller's drawer, not the main vault.

Where this analogy breaks down: badge systems can be lost or forged; SELinux labels are attached to the process by the kernel and cannot be self-elevated without a policy rule that explicitly allows it.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SELinux and AppArmor are security systems that add rules saying "this program is only allowed to do these specific things." Even if someone breaks into the program and gets control of it, they can only do what the rules allow. It's like putting each program in its own box with a list of exactly what it's allowed to touch.

**Level 2 — How to use it (junior developer):**
Check SELinux status: `sestatus` or `getenforce`. Check AppArmor status: `aa-status`. For Docker: `docker run --security-opt label:type:container_t myimage` (SELinux) or `docker run --security-opt apparmor=myprofile myimage` (AppArmor). If a program is blocked by SELinux: check `ausearch -m AVC -ts recent` or `dmesg | grep denied`. Switch SELinux to permissive temporarily: `setenforce 0` (do NOT do this in production).

**Level 3 — How it works (mid-level engineer):**
SELinux: every file on the filesystem has an xattr `security.selinux` containing the context. `ls -Z /etc/shadow` shows `system_u:object_r:shadow_t:s0`. The kernel's SELinux module intercepts every syscall involving files, sockets, capabilities. It extracts the subject context (process) and object context (file/socket), checks the policy database (loaded into kernel at boot), and returns EACCES if no matching `allow` rule exists. Policy is compiled with `checkpolicy` and loaded with `semodule`. AppArmor: profiles are stored in binary form in `/sys/kernel/security/apparmor/profiles`. The LSM hook checks the process's profile and the operation's target path. New processes inherit the parent's profile unless the profile specifies a `px` (profile execute) transition.

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental difference between SELinux and AppArmor is label-based vs path-based access control. Path-based (AppArmor) is intuitive but has a critical flaw: a hardlink to a file creates a new path to the same inode; a process confined to not accessing `/etc/shadow` can potentially access it via a hardlink at `/tmp/backdoor`. SELinux's label is on the inode's xattr — all hardlinks to the same inode have the same label, so there's no bypass via hardlinks or bind mounts. This is why SELinux is considered more rigorous for high-security environments. AppArmor's simplicity made it the default for Ubuntu and Docker — the 80% security improvement with 20% of the complexity. The Kubernetes ecosystem uses AppArmor profiles for pods (GA in 1.30) because most teams can write AppArmor profiles without a security specialisation.

---

### ⚙️ How It Works (Mechanism)

**SELinux operations:**

```bash
# Check status
sestatus
getenforce   # Enforcing / Permissive / Disabled

# View process contexts
ps -eZ | grep nginx
# system_u:system_r:httpd_t:s0  1234 nginx: worker process

# View file contexts
ls -Z /etc/shadow /var/www/html/index.html
# system_u:object_r:shadow_t:s0 /etc/shadow
# unconfined_u:object_r:httpd_sys_content_t:s0 /var/www/html/index.html

# Find denied operations
ausearch -m AVC -ts recent
# avc: denied { read } for pid=1234 comm="nginx"
#   scontext=httpd_t tcontext=shadow_t

# Restore default file context
restorecon -v /var/www/html/index.html

# Change file context (set type)
chcon -t httpd_sys_content_t /srv/mywebsite/index.html

# Persistent: update SELinux policy for a path
semanage fcontext -a -t httpd_sys_content_t \
  "/srv/mywebsite(/.*)?"
restorecon -Rv /srv/mywebsite

# List boolean policies (runtime tunables)
getsebool -a | grep httpd
# httpd_can_network_connect --> off
# httpd_can_sendmail --> off

# Enable a boolean (allow nginx to connect to network)
setsebool -P httpd_can_network_connect on
```

**AppArmor operations:**

```bash
# Check status
aa-status

# Show profile for a process
cat /proc/$(pidof nginx)/attr/current

# List profiles
ls /etc/apparmor.d/

# Example profile structure
cat /etc/apparmor.d/usr.sbin.nginx
# /usr/sbin/nginx {
#   #include <abstractions/base>
#   #include <abstractions/nameservice>
#
#   capability net_bind_service,
#
#   /var/log/nginx/*.log  w,
#   /var/www/html/**      r,
#   /etc/nginx/**         r,
#   /run/nginx.pid        rw,
#   /dev/null             rw,
#
#   network inet tcp,
#   network inet6 tcp,
# }

# Load/reload a profile
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx

# Set profile to complain mode (log only, no deny)
aa-complain /usr/sbin/nginx

# Set profile to enforce mode
aa-enforce /usr/sbin/nginx

# Check what was denied
dmesg | grep apparmor
grep apparmor /var/log/syslog
```

**Docker / Kubernetes usage:**

```bash
# Docker with AppArmor profile
docker run --security-opt \
  apparmor=docker-nginx-profile myimage

# Docker with SELinux label
docker run --security-opt \
  label=type:container_t myimage

# Kubernetes: AppArmor profile annotation
# (pod manifest)
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/mycontainer: \
      localhost/my-nginx-profile
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  SELinux access check for nginx reading a file │
└────────────────────────────────────────────────┘

 nginx process (httpd_t) calls open("/etc/shadow")
       │
       ▼
 Kernel VFS: open syscall
       │
       ▼
 DAC check: does www-data have permission?
       │  PASS (assume world-readable for example)
       ▼
 LSM hook: selinux_inode_permission()
       │
       ▼
 Extract subject context: httpd_t
 Extract object context: shadow_t (from inode xattr)
 Operation: file:read
       │
       ▼
 SELinux policy AVC (Access Vector Cache) lookup:
 allow httpd_t shadow_t:file { read }?
       │
  ┌────┴────┐
  │  FOUND  │  NOT FOUND
  └────┬────┘       │
       │             ▼
    ALLOW       Log AVC denial:
       │        avc: denied { read }
       ▼            │
 open() returns fd  ▼
                EACCES returned
                to nginx process
                nginx logs:
                "permission denied"
```

---

### 💻 Code Example

**Example — Audit and fix SELinux denial for custom web root:**

```bash
#!/bin/bash
# Fix SELinux denial for nginx serving /srv/website

WEBROOT="/srv/website"
echo "1. Checking SELinux status..."
sestatus | head -3

echo ""
echo "2. Current file contexts in $WEBROOT..."
ls -Z "$WEBROOT"/ 2>/dev/null | head -5

echo ""
echo "3. Checking for recent AVC denials..."
ausearch -m AVC -ts recent 2>/dev/null | \
  grep -i "scontext.*httpd" | tail -5

echo ""
echo "4. Applying httpd_sys_content_t to $WEBROOT..."
# Add permanent policy for this path
semanage fcontext -a -t httpd_sys_content_t \
  "${WEBROOT}(/.*)?"

# Relabel all files under WEBROOT
restorecon -Rv "$WEBROOT"

echo ""
echo "5. Verifying new contexts..."
ls -Z "$WEBROOT/" | head -5

echo ""
echo "Done. nginx should now be able to serve $WEBROOT"
echo "If still failing: check booleans with:"
echo "  getsebool -a | grep httpd"
```

---

### ⚖️ Comparison Table

| Feature              | SELinux                      | AppArmor               | seccomp            |
| -------------------- | ---------------------------- | ---------------------- | ------------------ |
| Approach             | Label-based (inode xattr)    | Path-based             | Syscall filter     |
| Granularity          | Very fine (type enforcement) | File path + capability | Syscall-level      |
| Hardlink bypass risk | No (label on inode)          | Yes (path-based)       | N/A                |
| Complexity           | Very high                    | Moderate               | Low-moderate       |
| Default on           | RHEL, Fedora, Android        | Ubuntu, Debian, Docker | Kubernetes pods    |
| Used in containers   | Kubernetes pod security      | Docker default profile | Kubernetes seccomp |

How to choose: SELinux for RHEL-based systems or high-security requirements; AppArmor for Ubuntu-based systems and containers; seccomp for syscall filtering as a complementary layer (combine all three for defense-in-depth).

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                  |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SELinux/AppArmor are only for servers                        | Android uses SELinux for all app isolation; Ubuntu Snap uses AppArmor for confined apps                                                                  |
| Disabling SELinux is the correct fix for "permission denied" | Disabling eliminates the security layer; correct fix is to audit (`ausearch -m AVC`) and fix the policy with `semanage`/`restorecon`                     |
| Permissive mode is safe for production                       | Permissive mode logs violations but does NOT deny them; it provides no protection — only use permissive for policy debugging                             |
| SELinux contexts are just extended permissions               | They are labels used for mandatory policy enforcement — they override DAC in the deny direction; a root process with the wrong type can be denied access |
| AppArmor protects against hardlink attacks                   | AppArmor is path-based; a hardlink at a different path bypasses profile restrictions; SELinux (inode-based) does not have this issue                     |

---

### 🚨 Failure Modes & Diagnosis

**Application Fails Silently Due to SELinux Denial**

**Symptom:**
nginx returns 403 or blank page. No nginx error in access/error log. Application "works fine" when SELinux is temporarily disabled.

**Root Cause:**
nginx attempting to read files with wrong SELinux context. DAC permissions are correct (world-readable) but SELinux type enforcement denies access.

**Diagnostic Command:**

```bash
# Check if SELinux is denying
ausearch -m AVC -ts recent
# avc: denied { read } for pid=1234 comm="nginx"
#   path="/srv/website/index.html"
#   scontext=system_u:system_r:httpd_t:s0
#   tcontext=user_u:object_r:user_home_t:s0

# File has wrong type (user_home_t instead of httpd_sys_content_t)
ls -Z /srv/website/index.html

# Fix: relabel to correct type
semanage fcontext -a -t httpd_sys_content_t \
  "/srv/website(/.*)?"
restorecon -Rv /srv/website
```

**Never do this in production:**

```bash
setenforce 0   # WRONG: disables security, not a fix
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Users and Groups` — SELinux and AppArmor are an additional layer on top of DAC (Unix permissions); understanding `uid`, `gid`, and file permissions is a prerequisite
- `Linux Security Hardening` — SELinux/AppArmor are key tools in the Linux hardening toolkit; understanding the broader security posture is important context

**Builds On This (learn these next):**

- `seccomp` — syscall-level filtering; complements SELinux/AppArmor (use all three for defense-in-depth in containers)
- `Capabilities` — Linux capabilities divide root's powers; SELinux and AppArmor can restrict capability use even for privileged processes
- `Containers` — Docker default AppArmor profile; Kubernetes pod security context; seccomp profiles — all build on the concepts from this entry

**Alternatives / Comparisons:**

- `seccomp` — filters which syscalls a process can call; narrower scope than SELinux/AppArmor but simpler and useful for containers
- `gVisor` — user-space kernel for containers; provides stronger isolation by intercepting all syscalls; complement to SELinux/AppArmor

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Mandatory Access Control — a policy layer │
│              │ above Unix permissions that confines each  │
│              │ process to explicitly allowed operations   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Root compromise of any service = full     │
│ SOLVES       │ system compromise; no blast radius limit  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Even root (uid=0) cannot bypass MAC —     │
│              │ the policy is enforced at the kernel LSM  │
│              │ layer, above the process identity layer   │
├──────────────┼───────────────────────────────────────────┤
│ SELinux vs   │ SELinux: label-based, fine-grained,       │
│ AppArmor     │ RHEL/Android. AppArmor: path-based,       │
│              │ simpler, Ubuntu/Docker                    │
├──────────────┼───────────────────────────────────────────┤
│ DEBUG DENY   │ SELinux: ausearch -m AVC -ts recent       │
│              │ AppArmor: grep apparmor /var/log/syslog   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hotel with mandatory rule book — master  │
│              │ key still can't override the rules"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ seccomp → Capabilities → gVisor           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A web application is compromised through a 0-day. The attacker has code execution as `nginx` (SELinux type `httpd_t`). Describe the specific steps the attacker would need to perform to read `/etc/shadow`, write to `/usr/bin/`, and establish a reverse shell — specifically naming which SELinux policy rules or booleans would need to be in place for each action to succeed, and which default SELinux boolean settings would block them.

**Q2.** Your team is containerising a legacy Java application that reads configuration from `/etc/myapp/`, writes logs to `/var/log/myapp/`, opens a TCP socket on port 8080, and makes outbound HTTP calls. Write the complete AppArmor profile for this container, explain every permission granted, and identify the minimum set of capabilities it needs — explaining why granting `CAP_SYS_ADMIN` to solve compatibility issues would effectively defeat the purpose of the AppArmor profile.
