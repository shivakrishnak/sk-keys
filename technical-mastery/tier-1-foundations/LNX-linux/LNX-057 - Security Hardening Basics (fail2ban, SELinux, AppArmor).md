---
id: LNX-057
title: "Security Hardening Basics (fail2ban, SELinux, AppArmor)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-056, LNX-033
used_by: LNX-079, LNX-100
related: LNX-056, LNX-078, LNX-090
tags: [fail2ban, SELinux, AppArmor, hardening, security, LSM, MAC, brute-force, ssh-hardening]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/lnx/security-hardening-basics/
---

## TL;DR

Linux security hardening has three independent layers: (1) **fail2ban**:
watches auth logs, bans IPs that brute-force SSH/services via iptables rules;
(2) **SELinux** (Red Hat): kernel-level Mandatory Access Control (MAC) with
labels - processes and files get security contexts; violations are logged
to `/var/log/audit/audit.log`; `getenforce` / `setenforce` to check/change
mode; (3) **AppArmor** (Ubuntu/Debian): MAC via path-based profiles; simpler
than SELinux; `aa-status`, `aa-enforce`, `aa-complain`. SSH hardening:
`PermitRootLogin no`, `PasswordAuthentication no`, `AllowUsers`. Defense
in depth: use all three together.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-057 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | fail2ban, SELinux, AppArmor, hardening, LSM, MAC, ssh-hardening, brute-force |
| **Prerequisites** | LNX-056 (iptables), LNX-033 (SSH basics) |

---

### The Problem This Solves

**Problem 1**: An internet-facing SSH server gets 10,000 brute-force login
attempts per day. Each attempt creates a log entry and consumes CPU.
fail2ban monitors `/var/log/auth.log`, counts failed attempts per IP, and
automatically adds iptables DROP rules after a threshold (e.g., 5 failures
in 60 seconds). The attacker's IP is banned for 10 minutes (configurable).

**Problem 2**: A compromised web application (e.g., via code injection) tries
to read `/etc/shadow` or open a reverse shell. With default Linux permissions
(DAC), if the web process can read the file, it can do so. With SELinux/
AppArmor MAC: the web process has a strict security context restricting it
to only the operations defined by its profile. Accessing `/etc/shadow` is
DENIED even if DAC would allow it.

---

### Textbook Definition

**fail2ban**: A Python daemon that monitors log files (ssh, nginx, apache,
etc.) for patterns indicating attacks (failed logins, 404 storms, etc.).
On threshold: executes an "action" (usually `iptables -I` to ban the IP)
for a configurable duration. Config: `/etc/fail2ban/jail.conf` (defaults)
and `/etc/fail2ban/jail.local` (overrides). Jails = per-service configs.

**Mandatory Access Control (MAC)**: Access control policy where the OS
ENFORCES rules that even root cannot override (vs DAC = owner sets
permissions). Subjects (processes) and objects (files, sockets) get
security labels. A policy defines what operations each label combination allows.

**SELinux (Security-Enhanced Linux)**: MAC implementation from NSA,
standard on Red Hat/Fedora/CentOS/RHEL. Uses labels (security contexts):
`user:role:type:level`. The `type` (e.g., `httpd_t`) determines what is
allowed. Policy: type enforcement (TE) rules. Modes: enforcing (deny violations),
permissive (log but allow), disabled (completely off).

**AppArmor**: MAC via application profiles (path-based). Simpler than SELinux.
Standard on Ubuntu, Debian, SUSE. Profiles in `/etc/apparmor.d/`. Modes:
enforce (block violations), complain (log but allow, for profiling).

---

### Understand It in 30 Seconds

```bash
# === fail2ban ===
apt install fail2ban            # Ubuntu/Debian
yum install fail2ban            # CentOS/RHEL

# Check status:
fail2ban-client status          # list active jails
fail2ban-client status sshd     # sshd jail: banned IPs, stats

# List currently banned IPs:
fail2ban-client status sshd | grep "Banned IP"
# or: iptables -L f2b-sshd

# Unban an IP:
fail2ban-client set sshd unbanip 203.0.113.50

# Configure (/etc/fail2ban/jail.local - overrides jail.conf):
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 3600     # 1 hour ban
findtime = 600      # within 10 minutes
maxretry = 5        # after 5 failures

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
EOF

systemctl restart fail2ban

# === SELinux (RHEL/CentOS/Fedora) ===
getenforce              # Enforcing | Permissive | Disabled
sestatus                # detailed SELinux status

# Temporarily set to permissive (survives until reboot):
setenforce 0            # permissive
setenforce 1            # enforcing

# Permanently change mode (/etc/selinux/config):
# SELINUX=enforcing     <- change to permissive or disabled (reboot required)

# Check file security context:
ls -Z /var/www/html/index.html
# -rw-r--r--. root root unconfined_u:object_r:httpd_sys_content_t:s0 index.html
#                                                 ^^^^^^^^^^^^^^^^
#                                                 This type allows httpd to read it

# Check process security context:
ps -eZ | grep httpd
# system_u:system_r:httpd_t:s0  1234  apache  httpd

# Wrong context (common problem - file won't be served):
ls -Z /srv/web/app.html
# unconfined_u:object_r:user_home_t:s0  app.html
# httpd_t can't read user_home_t -> 403 error!

# Fix: restore default context:
restorecon -v /srv/web/app.html
# Or: set context explicitly:
chcon -t httpd_sys_content_t /srv/web/app.html
# Or: add fcontext rule (persistent):
semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"
restorecon -Rv /srv/web/

# Check and fix SELinux booleans:
getsebool -a | grep httpd           # list all httpd-related booleans
setsebool -P httpd_can_network_connect on   # allow httpd to connect
# -P = persistent (survives reboot)

# Diagnose SELinux denials:
ausearch -m AVC -ts today           # today's access vector cache denials
sealert -a /var/log/audit/audit.log # human-readable with fix suggestions

# Generate custom policy from denials:
ausearch -m AVC -ts today | audit2allow -M mypolicy
semodule -i mypolicy.pp

# === AppArmor (Ubuntu/Debian) ===
aa-status                           # list all loaded profiles
# Includes: processes in enforce mode, complain mode, unconfined

# Common AppArmor commands:
aa-enforce /etc/apparmor.d/usr.sbin.nginx   # put nginx in enforce mode
aa-complain /etc/apparmor.d/usr.sbin.nginx  # switch to complain (logging)
aa-disable /etc/apparmor.d/usr.sbin.nginx   # disable profile

# Check if AppArmor is blocking something:
dmesg | grep DENIED
# or:
journalctl -t apparmor | grep DENIED

# Generate profile from scratch (complain mode -> analyze -> enforce):
aa-genprof /usr/bin/myapp           # interactive profile generator
# Run the app, then enter (S) for scan, (F) for finish

# Reload changed profile:
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx
```

---

### First Principles

**fail2ban architecture:**
```
/var/log/auth.log (log file)
         |
         | (tail -F)
         v
fail2ban-server (monitors patterns)
         |
         | pattern match: "Failed password for ... from IP"
         | count: 5 failures from same IP within 10 min
         v
fail2ban action: ban IP
         |
         | executes: iptables -I f2b-sshd 1 -s <IP> -j REJECT
         v
iptables rule: packets from attacker IP -> REJECT

         (after bantime = 1 hour)
         |
         | fail2ban removes the rule:
         | iptables -D f2b-sshd -s <IP> -j REJECT
         v
IP unbanned
```

**SELinux multi-level label anatomy:**
```
Security Context format:
  user:role:type:level

Example: system_u:system_r:httpd_t:s0

  user    = system_u (SELinux user, not Linux user)
  role    = system_r (what roles this context can transition to)
  type    = httpd_t  (the CRITICAL part: type enforcement)
  level   = s0       (sensitivity level, MLS/MCS)

Type Enforcement (TE) rules - the core policy:
  allow httpd_t httpd_sys_content_t:file { read open getattr };
  ^ Apache can read files with httpd_sys_content_t label
  
  allow httpd_t httpd_sys_rw_content_t:file { read write create };
  ^ Can also write to rw-labeled files (uploads)

  DENY (implicit, not written):
  httpd_t reading shadow_t (passwd file types) -> DENIED
  httpd_t executing bin_t (system binaries) -> DENIED
  httpd_t opening network sockets to arbitrary ports -> DENIED
  (unless httpd_can_network_connect boolean is set)

Type transition rules:
  When httpd_t executes a CGI script:
  type_transition httpd_t bin_t:process httpd_sys_script_t
  ^ The script process gets httpd_sys_script_t, not httpd_t
```

---

### Thought Experiment

Hardening an Ubuntu web server from scratch:

```bash
# Step 1: SSH hardening
vi /etc/ssh/sshd_config
# ---
PermitRootLogin no           # never allow root login
PasswordAuthentication no    # require SSH keys only
PubkeyAuthentication yes
AllowUsers deploy webmaster  # whitelist specific users
MaxAuthTries 3               # reduce to 3 attempts
LoginGraceTime 30            # 30 seconds to authenticate
ClientAliveInterval 300      # disconnect idle sessions after 5 min
ClientAliveCountMax 2
# ---
systemctl restart ssh

# Verify:
sshd -t    # test config syntax

# Step 2: fail2ban for SSH and nginx
apt install fail2ban

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 3600      # 1 hour
findtime = 600       # 10 min window
maxretry = 5

[sshd]
enabled = true
maxretry = 3         # stricter for SSH

[nginx-http-auth]
enabled = true
port    = http,https
logpath = %(nginx_error_log)s

[nginx-limit-req]
enabled = true
port    = http,https
logpath = %(nginx_error_log)s
EOF

systemctl enable --now fail2ban
fail2ban-client status    # verify active jails

# Step 3: AppArmor (Ubuntu)
aa-status                 # check current state
# nginx usually has a profile: /etc/apparmor.d/usr.sbin.nginx
# ensure it's in enforce mode:
aa-enforce /etc/apparmor.d/usr.sbin.nginx
aa-status | grep nginx    # should show enforce mode

# Check for denials after enabling enforce:
journalctl -t apparmor -f &   # watch for denials
# Trigger normal usage, watch for DENIED messages
# If needed: switch to complain, add rules, switch back to enforce

# Step 4: Verify hardening
# Run lynis (security audit tool):
apt install lynis
lynis audit system
# Shows hardening score and specific recommendations
```

---

### Mental Model / Analogy

```
Linux security = building access control layers

Layer 1: Lock on the door (SSH key auth + fail2ban)
  Only keyholders enter
  fail2ban = security guard who bans repeated door-bangers

Layer 2: ID badge scan (DAC - file permissions)
  owner, group, other permissions
  rwx on files, directories
  This is the standard Unix model

Layer 3: Department access control (MAC - SELinux/AppArmor)
  Even if you have an ID badge, the badge only grants access
  to specific rooms based on your ROLE, not just your identity
  
  SELinux: complex role-based policy
    "httpd_t process" can only access "httpd_sys_content_t files"
    Even root can't override the SELinux policy (unless changing policy)
    Like a government clearance system: needs-to-know basis
    
  AppArmor: path-based profile
    "nginx can only read /var/www/html/* and write to /var/log/nginx/*"
    Like a job description: explicitly listed tasks only

fail2ban = bouncer with a blocklist
  Watches the door (log file)
  Notes who bangs too many times (failed auth pattern)
  Adds them to the blocklist (iptables ban)
  Removes them from blocklist after their time-out expires

SELinux in permissive mode = CCTV without locked doors
  Everything is logged but not blocked
  Used to understand what a process needs before enforcing

audit2allow = reading the CCTV footage to write new access rules
  "This process tried to access these resources but was denied"
  "Generate a policy module to allow exactly those accesses"
```

---

### Gradual Depth - Five Levels

**Level 1:**
fail2ban basics: install, `fail2ban-client status sshd`, ban/unban IPs,
`jail.local` config. SSH hardening: `PermitRootLogin no`,
`PasswordAuthentication no`. SELinux: `getenforce`, `setenforce 0`
(troubleshooting trick - if issue goes away in permissive, it's SELinux).
AppArmor: `aa-status`, complain vs enforce modes.

**Level 2:**
SELinux context management: `ls -Z`, `ps -eZ`, `chcon`, `restorecon`,
`semanage fcontext`. Common SELinux booleans (`getsebool`, `setsebool -P`).
`ausearch -m AVC` for diagnosis. `audit2allow` for quick policy generation.
AppArmor profile editing, `aa-genprof` for new profiles. fail2ban custom
jails for nginx, application logs. `lynis` for automated security auditing.

**Level 3:**
SELinux policy module development: write `.te` (type enforcement) file,
compile with `checkpolicy`/`semodule_package`/`semodule`. MCS (Multi-Category
Security): same type, different categories (used by containers, VMs). SELinux
in containers: `--security-opt=no-new-privileges`, SELinux label inheritance.
AppArmor profiles for containers (Docker uses AppArmor or seccomp). CIS
Benchmarks: specific hardening settings scored and validated. SCAP/OpenSCAP
for automated compliance checking.

**Level 4:**
SELinux and systemd: services launched by systemd get the correct SELinux
context via `SELinuxContext=` in unit files. SELinux role transitions: users
transitioning from `user_u` to `sysadm_u` for admin tasks. Multi-Level
Security (MLS): sensitivity labels (s0-s15) and categories (c0-c1023),
used in government/defense. AppArmor stacking (Ubuntu 18.04+): multiple
profiles for same process. Seccomp (separate from LSM): filter system
calls per process (Docker's default seccomp profile blocks ~40 syscalls).

**Level 5:**
Linux Security Module (LSM) framework: how SELinux and AppArmor hook into
the kernel via 200+ LSM hooks. LSM stacking (Linux 4.15+): can run both
SELinux and AppArmor simultaneously (with restrictions). BPF-LSM (Linux
5.7+): write security policy as eBPF programs - more flexible than static
LSMs. Landlock (Linux 5.13+): unprivileged sandboxing, processes can restrict
their own access without root. TOMOYO (Japan): another LSM with path-based
learning mode.

---

### Code Example

**BAD - common security mistakes:**
```bash
# BAD 1: Disabling SELinux instead of fixing the context:
# Developer encounters: "403 Forbidden on my new /srv/web directory"
setenforce 0    # <- BAD: disabling security system to "fix" a problem
# Or worse:
echo "SELINUX=disabled" >> /etc/selinux/config  # permanently disabled!

# GOOD: diagnose and fix the context:
ausearch -m AVC -ts recent   # find the denial
# Found: httpd_t reading user_home_t denied
ls -Z /srv/web/
# Wrong type: user_home_t
semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"
restorecon -Rv /srv/web/
# Re-test: web server now works with SELinux enforcing

# BAD 2: fail2ban with wrong log path:
# /etc/fail2ban/jail.local:
# [sshd]
# logpath = /var/log/syslog   <- WRONG for Debian/systemd
# On systemd systems, there's no /var/log/auth.log by default!

# GOOD: use the journald backend:
# [sshd]
# enabled = true
# backend = systemd   <- reads from journald, not file

# BAD 3: AppArmor in complain mode in production:
aa-complain /etc/apparmor.d/usr.sbin.nginx
# Complain = logs violations but doesn't block them
# Security profile provides zero protection in complain mode!

# GOOD: develop in complain, test thoroughly, then enforce:
aa-enforce /etc/apparmor.d/usr.sbin.nginx   # MUST be enforcing in production
aa-status | grep -A2 "processes in enforce"  # verify
```

**GOOD - automated hardening check:**
```bash
#!/bin/bash
# security-check.sh: quick hardening verification

PASS=0; FAIL=0
check() {
    if eval "$2" > /dev/null 2>&1; then
        echo "[PASS] $1"
        ((PASS++))
    else
        echo "[FAIL] $1"
        ((FAIL++))
    fi
}

check "SSH: PermitRootLogin disabled" \
    "sshd -T | grep -q 'permitrootlogin no'"
check "SSH: PasswordAuth disabled" \
    "sshd -T | grep -q 'passwordauthentication no'"
check "fail2ban running" \
    "systemctl is-active fail2ban"
check "SELinux/AppArmor active" \
    "getenforce 2>/dev/null | grep -q Enforcing || aa-status 2>/dev/null | grep -q 'enforce mode'"
check "Unattended upgrades enabled" \
    "dpkg -l unattended-upgrades 2>/dev/null | grep -q '^ii'"

echo ""
echo "Results: $PASS passed, $FAIL failed"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "SELinux in permissive mode is still protecting the system" | Permissive mode LOGS violations but does NOT block anything. It provides zero security protection. Its purpose is troubleshooting and policy development: run in permissive, check what would be denied, write policy to allow or fix it, switch to enforcing. Production systems must run in enforcing mode. `setenforce 0` is a troubleshooting step, not a permanent fix. |
| "fail2ban prevents brute-force attacks" | fail2ban DETECTS and BANS IPs that are actively brute-forcing. It doesn't PREVENT attempts - it limits the rate of attempts by banning persistent attackers. An attacker with thousands of different IP addresses can still attempt many logins before any single IP gets banned. The best protection against brute-force is disabling password auth entirely (`PasswordAuthentication no`) - then brute-force is meaningless because only SSH keys work. fail2ban is a defense-in-depth measure, not the primary defense. |
| "Disabling SELinux temporarily to test is always safe" | `setenforce 0` (permissive mode) is not permanent - it resets on reboot. But on a running production system, switching to permissive mode removes MAC protection for ALL running processes immediately. An attacker who has exploited a service can now access anything that DAC permits. The correct approach: fix the specific SELinux denial (use `ausearch` + `audit2allow` + test) in a test environment, then apply to production. Never run production in permissive mode. |
| "AppArmor is weaker than SELinux" | They have different threat models and are not directly comparable in terms of "strength." SELinux is more granular (type-based, all system objects labeled) but more complex. AppArmor is path-based (simpler profiles, easier to write) but can miss some attack vectors that SELinux would catch (e.g., hard links, bind mounts can bypass path checks). For web servers: a correctly written AppArmor profile is just as effective as SELinux for confining nginx. SELinux is stronger for multi-tenant isolation and government/defense scenarios. AppArmor is easier to maintain correctly. A poorly written SELinux policy is not better than a correct AppArmor profile. |
| "SSH key auth makes fail2ban unnecessary" | With `PasswordAuthentication no`, brute-force against passwords is impossible. But fail2ban still provides value: (1) blocking scanners and script-kiddies that spam connection attempts (consuming CPU/resources even if they fail), (2) protecting other services on the same host (nginx, ftp, mail), (3) blocking port-scanning from the same IPs, (4) clean logs (less noise). It's defense in depth. But the PRIMARY protection against SSH brute force is `PasswordAuthentication no`. |

---

### Failure Modes & Diagnosis

**SELinux blocking a newly deployed application:**
```bash
# Symptom: nginx returns 403 or application logs "permission denied"
# after moving files to new location

# Step 1: Check if SELinux is the cause:
getenforce          # is it Enforcing?
setenforce 0        # temporarily permissive
# Test application: if it works now, SELinux is the cause
setenforce 1        # re-enable enforcing ASAP

# Step 2: Find the denial:
ausearch -m AVC -ts recent
# Output:
# type=AVC msg=audit(...): avc: denied { read } for pid=1234
#  comm="nginx" name="app.php" dev="sda1" ino=123456
#  scontext=system_u:system_r:httpd_t:s0
#  tcontext=unconfined_u:object_r:user_home_t:s0
#  tclass=file permissive=0

# Type transition: httpd_t trying to read user_home_t
# httpd needs httpd_sys_content_t, not user_home_t

# Step 3: Human-readable with fix suggestions (if setroubleshoot installed):
sealert -a /var/log/audit/audit.log | tail -100
# Output includes: "run the following command..."

# Step 4: Fix the file context:
ls -Z /var/www/newapp/           # confirm wrong type
semanage fcontext -a -t httpd_sys_content_t "/var/www/newapp(/.*)?"
restorecon -Rv /var/www/newapp/
ls -Z /var/www/newapp/           # verify correct type now
# Test application - should work

# Quick check all apache/httpd booleans:
getsebool -a | grep httpd
# httpd_can_network_connect --> off  <- if app needs to call external APIs:
setsebool -P httpd_can_network_connect on
```

---

### Related Keywords

**Foundational:**
LNX-056 (iptables), LNX-033 (SSH)

**Builds on this:**
LNX-079 (Linux Security Modules), LNX-100 (Hardening at Scale)

**Related:**
LNX-078 (seccomp and Capabilities)

---

### Quick Reference Card

| Tool | Key Command |
|------|-------------|
| fail2ban status | `fail2ban-client status sshd` |
| fail2ban unban | `fail2ban-client set sshd unbanip IP` |
| SELinux mode | `getenforce` / `setenforce 0\|1` |
| SELinux file context | `ls -Z FILE` / `restorecon -v FILE` |
| SELinux denials | `ausearch -m AVC -ts recent` |
| SELinux fix context | `semanage fcontext -a -t TYPE PATH; restorecon -Rv PATH` |
| AppArmor status | `aa-status` |
| AppArmor enforce | `aa-enforce /etc/apparmor.d/PROFILE` |

**3 things to remember:**
1. SELinux permissive = logs only, NO protection; always use enforcing in production
2. `setenforce 0` is a troubleshooting step - if issue disappears, use `ausearch -m AVC` to find and fix the actual SELinux policy issue
3. fail2ban bans IPs after X failures, but `PasswordAuthentication no` is the real SSH brute-force protection

---

### Transferable Wisdom

MAC concepts appear in: Kubernetes Pod Security Standards (restrict, baseline,
privileged) are essentially AppArmor/SELinux policies applied to pods.
Container runtimes (Docker, containerd) apply AppArmor or SELinux profiles to
containers by default. AWS IAM policies are MAC for cloud resources: IAM
defines what each role can access, regardless of whether the application code
would "want" to access something broader. The principle of least privilege
in security architecture IS MAC - the concept that each component should have
exactly the access it needs, no more. Zero-trust architecture extends this
to network access. fail2ban's pattern: "monitor -> detect anomaly -> auto-
respond by changing firewall rules" is the same pattern used by AWS GuardDuty
+ WAF automated blocking, Cloudflare's bot management, and SIEM-based
automated response.

---

### The Surprising Truth

SELinux was developed by the NSA and contributed to the Linux kernel in 2003.
The NSA's motivation was to enforce the "type enforcement" security model
that had been used in military/government systems. The Linux community's
initial reaction was extremely hostile: many developers believed the NSA
was inserting backdoors. The code was extensively reviewed and found to
be legitimate. It was merged into the kernel. Today, it runs on billions
of Android devices (Android uses SELinux for app sandboxing since Android 4.3)
and every RHEL/CentOS server that hasn't had it disabled. The irony: a system
developed by an intelligence agency to RESTRICT access is now the foundation
of Android's security model that protects users' private data FROM intelligence
agencies (and other attackers). The more surprising fact: the single biggest
security improvement a sysadmin can make takes literally 10 seconds:
`sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && systemctl reload ssh`. The most common Linux server compromise vector is weak or reused SSH passwords. All of SELinux, AppArmor, and fail2ban combined provide less protection than simply disabling password-based authentication.

---

### Mastery Checklist

- [ ] Can configure fail2ban jails and diagnose why fail2ban isn't banning
- [ ] Can check SELinux status and determine if it's causing application issues
- [ ] Can find and fix SELinux file context errors (ausearch, chcon, semanage, restorecon)
- [ ] Can use AppArmor to check, enforce, and develop profiles
- [ ] Can harden SSH configuration (PermitRootLogin, PasswordAuthentication, AllowUsers)

---

### Think About This

1. You deploy a new Java web application to `/opt/myapp/` on a CentOS
   server with SELinux enforcing. The application is managed by a systemd
   service unit (`myapp.service`) running as the `myapp` user. The
   application cannot read its own configuration files and cannot connect
   to MySQL on localhost. Describe the complete diagnosis and remediation
   steps using SELinux tools. What is the likely SELinux type needed for
   the application directory, and what boolean might be needed for MySQL
   connectivity?

2. fail2ban is configured but an attacker is still successfully brute-
   forcing SSH passwords with 1,000 different IP addresses (one attempt
   per IP, cycling through a botnet). fail2ban bans each IP after 5
   attempts, but since each IP only makes 1 attempt, nothing gets banned.
   What configuration changes and what additional controls would you
   implement to stop this attack?

3. An application developer complains that AppArmor is blocking their
   app from creating files in `/tmp/myapp-work/`. The current profile
   has `deny /tmp/** rw`. They want you to simply disable AppArmor for
   their app. Instead, describe how you would (a) investigate the exact
   denials, (b) write a minimal profile change that allows exactly what
   the app needs without over-permitting, and (c) test the change without
   disrupting production.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between DAC and MAC in Linux security?
A: DAC (Discretionary Access Control) is the traditional Unix permission model: the OWNER of a resource decides who can access it via `chmod`/`chown`. The resource owner has discretion to grant or revoke access. DAC is enforced by the kernel's file permission checks (rwx bits, ACLs). LIMITATION: root can override all DAC. A compromised root (or setuid binary) can access any file. MAC (Mandatory Access Control) is enforced by the OS itself, INDEPENDENT of ownership. Even root cannot override MAC policy (without changing the policy itself). In Linux, MAC is implemented via the Linux Security Module (LSM) framework. SELinux and AppArmor are MAC implementations. SELinux adds a LABEL (security context) to every process and file. A kernel-enforced policy defines what operations label combinations are allowed. When a process (with label `httpd_t`) tries to read a file (with label `shadow_t`), SELinux checks the policy - if no `allow httpd_t shadow_t:file read` rule exists, the read is DENIED, even if the file is world-readable (DAC permits it). AppArmor uses PATH-BASED profiles instead of labels: a process running as `nginx` can only access files whose paths match the profile's rules. MAC is particularly valuable for confining network-facing services (web servers, databases) because even if they are compromised via code injection, their access is limited to what the MAC policy allows. This is "defense in depth" - multiple independent security layers.

**Expert:**
Q: Walk through diagnosing and fixing an SELinux policy problem that blocks a newly deployed application.
A: Systematic approach: STEP 1 - Confirm SELinux is the issue: `getenforce` (must be Enforcing). Set `setenforce 0` temporarily. Test application. If it works now: SELinux is the cause. Immediately `setenforce 1` - permissive provides zero protection. STEP 2 - Find the denial: `ausearch -m AVC -ts recent` (AVCs = Access Vector Cache denials). Look for lines with `avc: denied`. Key fields: `scontext` (what process/label was denied), `tcontext` (what resource/label), `tclass` (type: file, tcp_socket, etc.), `{ }` (operation: read, write, connect). Example output: `denied { read } for comm="java" scontext=system_u:system_r:java_t:s0 tcontext=system_u:object_r:var_t:s0`. STEP 3 - Determine the fix (in priority order): (a) Wrong file context: the file exists in the right location but has wrong SELinux type. Fix: `semanage fcontext -a -t CORRECT_TYPE "PATH(/.*)?"` then `restorecon -Rv PATH`. Most common cause. (b) Missing boolean: a pre-defined toggle for common patterns. Check: `getsebool -a | grep <service>`. Fix: `setsebool -P <boolean> on`. (c) Missing policy rule: the policy doesn't account for your setup. Fix: `ausearch -m AVC -ts recent | audit2allow -M mypol && semodule -i mypol.pp`. This generates and installs a custom policy module. STEP 4 - For `sealert` (if setroubleshoot-server is installed): `sealert -a /var/log/audit/audit.log` provides human-readable explanations with specific commands to fix each denial. STEP 5 - Verify: with SELinux enforcing, test the application again. The denial should be gone. Document the fix and add it to the deployment procedure.
