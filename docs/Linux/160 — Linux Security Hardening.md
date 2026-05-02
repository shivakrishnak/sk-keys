---
layout: default
title: "Linux Security Hardening"
parent: "Linux"
nav_order: 160
permalink: /linux/linux-security-hardening/
number: "0160"
category: Linux
difficulty: ★★★
depends_on: Users and Groups, SSH
used_by: DevOps, Site Reliability Engineering, Cloud Security
related: SELinux / AppArmor, SSH, Users and Groups, iptables
tags:
  - linux
  - os
  - security
  - devops
  - deep-dive
---

# 160 — Linux Security Hardening

⚡ TL;DR — Linux security hardening is the practice of systematically reducing the attack surface of a Linux system by disabling unnecessary services, restricting privileges, enforcing strong authentication, and enabling security controls — turning a default "works out of the box" OS into a "deny by default" OS.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A freshly installed Ubuntu server runs dozens of services (some you didn't install), has 22 open ports, allows password-based SSH login as root, has no firewall, ships with world-readable configuration files, and has half its users with sudo access. Within hours of going live on the internet, it's being scanned; within days of a known CVE being published, automated exploitation attempts begin.

**THE BREAKING POINT:**
The default state of most Linux distributions is "convenient for developers" not "secure for production." Every unnecessary open port, every service running as root, every weak SSH password, and every misconfigured permission is an attack vector. In 2022, the average time to first login attempt on an exposed SSH port was under one minute (Pew Research / Honeypot data consistently shows this).

**THE INVENTION MOMENT:**
Security hardening isn't a single tool — it's a discipline. CIS (Center for Internet Security) publishes hardening benchmarks for every major Linux distribution. Tools like Lynis, OpenSCAP, and AWS Security Hub audit compliance against these benchmarks. The practice combines: minimal installation, principle of least privilege, strong authentication, mandatory access control, and network segmentation.

---

### 📘 Textbook Definition

**Linux security hardening** is the process of configuring a Linux system to reduce its attack surface by: (1) removing or disabling unnecessary software and services; (2) restricting privileges using the principle of least privilege; (3) enforcing strong authentication and access controls; (4) enabling kernel security features; (5) maintaining auditability and monitoring. Standards include CIS Benchmarks, STIG (Security Technical Implementation Guides from DISA), and NIST SP 800-123.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Hardening turns a default Linux install from "open by default" to "deny by default" — every unnecessary door locked, every service running with minimum rights.

**One analogy:**

> A new house has all windows unlocked, a master key under the mat, and a welcome sign at every door. Security hardening is moving in: lock every window, install deadbolts, remove the key from under the mat, replace the welcome signs with no-entry signs, and set up a camera on every entry. The house still functions — you can still get in — but only through the front door, with the right key, after showing ID.

**One insight:**
Hardening is multiplicative: no single measure is sufficient, but layers compound. SSH key auth + firewall + SELinux + no root login + audit logging means an attacker must breach every layer. Defense-in-depth means even if SSH is compromised, SELinux contains what the attacker can do.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Minimize attack surface**: every service, port, package, and account that exists is a potential vulnerability.
2. **Principle of least privilege**: processes and users should have only the minimum rights needed to function.
3. **Defense-in-depth**: assume each layer will be breached; design so no single breach causes total compromise.
4. **Auditability**: you cannot secure what you cannot observe; logging and monitoring are part of hardening, not optional extras.

**DERIVED DESIGN:**

_Authentication hardening:_

```
root login via SSH disabled → force named account + sudo
Password auth disabled → key-based auth only
MFA for privileged access
/etc/sudoers: NOPASSWD sparingly, specific commands only
```

_Network hardening:_

```
iptables/nftables default DENY → explicit ACCEPT rules only
Close all unused ports (ss -tlnp to audit)
Disable IPv6 if not used (reduces attack surface)
Fail2ban blocks brute-force attempts automatically
```

_Kernel hardening (sysctl):_

```
net.ipv4.ip_forward = 0  (unless router)
net.ipv4.conf.all.rp_filter = 1  (anti-spoofing)
kernel.randomize_va_space = 2  (ASLR enabled)
net.ipv4.tcp_syncookies = 1  (SYN flood protection)
kernel.dmesg_restrict = 1  (restrict dmesg to root)
fs.suid_dumpable = 0  (no core dumps from SUID programs)
```

_File system hardening:_

```
/tmp noexec,nosuid mount option
/home noexec,nosuid mount option
World-writable files: none (find / -perm -002)
SUID/SGID binaries: audit and remove unnecessary ones
umask 027 (default permissions: no world access)
```

**THE TRADE-OFFS:**
**Gain:** Dramatically reduced attack surface; compliance with security standards; audit trail.
**Cost:** Time investment; application breakage (services may depend on wide permissions); SELinux/AppArmor debugging complexity; ongoing maintenance as software changes.

---

### 🧪 Thought Experiment

**SETUP:**
Two identical web servers. Server A: default Ubuntu install with the web app deployed. Server B: same app, with CIS Level 2 hardening applied.

**SCENARIO: CVE published for the web framework:**

- Server A: Has multiple SSH users with password auth. Port 3306 (MySQL) open to internet (dev forgot to close it). SSHd allows root login. No firewall. App runs as root.
- Server B: SSH key auth only. Firewall allows only 80/443/22. MySQL bound to 127.0.0.1 only. No root SSH. App runs as `www-data`. SELinux enforcing. Fail2ban active.

**OUTCOME:**
An automated exploit targets the CVE. On Server A: RCE as root, game over. On Server B: RCE as `www-data` (not root), SELinux type `httpd_t` prevents reading `/etc/shadow` or writing to `/usr/bin/`. MySQL is unreachable from outside. The attacker has code execution but is confined. Time to detect: seconds (auditd logs the anomalous behavior).

**THE INSIGHT:**
Hardening doesn't prevent the CVE from being exploited. It contains the blast radius when exploitation occurs. The question isn't "can we prevent all attacks?" but "can we ensure a breach of one component doesn't mean total system compromise?"

---

### 🧠 Mental Model / Analogy

> Linux hardening is like operating a secure vault facility, not just a warehouse. A warehouse has one lock. A vault facility has: perimeter fence + card access + biometric at inner doors + motion sensors + individual safe locks + audit logs of everyone who enters. Each control is independent and layered. An attacker who climbs the fence still needs the card. An attacker with a card still needs the biometric. An attacker who bypasses all physical controls still can't open the specific safe — and every step is logged. The vault doesn't assume any single layer will hold forever; it designs for when each layer fails.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Linux hardening is turning off everything you don't need, locking down everything you do need, and setting up logging so you know when something goes wrong. Like locking your house, closing windows, and setting an alarm — vs just locking the front door.

**Level 2 — How to use it (junior developer):**
Immediate actions for any production server: disable root SSH login (`PermitRootLogin no`), disable password SSH auth (`PasswordAuthentication no`), set up a firewall (`ufw allow 22,80,443`), run `lynis audit system` to get a baseline score, review open ports with `ss -tlnp`, check listening services with `systemctl list-units --type=service --state=running`.

**Level 3 — How it works (mid-level engineer):**
CIS Benchmarks define two levels: Level 1 (minimal impact on functionality, recommended for all systems) and Level 2 (stricter, may impact some workloads). Tools: `lynis audit system` scores 0-100 and gives specific recommendations. `openscap` checks against OVAL/XCCDF policy files. `aide` (Advanced Intrusion Detection Environment) creates a hash database of system files and alerts on changes. `auditd` records security-relevant syscalls (file opens, privilege changes, network connections). Key kernel parameters in `/etc/sysctl.d/99-hardening.conf` persist across reboots. `/etc/pam.d/` controls authentication (password complexity, lockout policies). `chage -l username` shows password expiry settings.

**Level 4 — Why it was designed this way (senior/staff):**
The history of Linux hardening reflects the history of attacks. ASLR (address space layout randomisation) was added to defeat buffer overflow exploits (shellcode needed to know where to jump). Stack canaries defeated stack-smashing attacks. RELRO (Relocations Read-Only) defeated GOT (Global Offset Table) overwrite attacks. Each kernel mitigation was a direct response to a class of exploits that were actively being used. The current state (ASLR + PIE + RELRO + NX stack + seccomp + SELinux + capabilities) represents 20 years of attack-then-defend cycles. The current frontier is supply chain security (signed packages, verified boot with TPM/Secure Boot) and eBPF-based runtime security (Falco, Tetragon) that can detect malicious behavior patterns without kernel modifications.

---

### ⚙️ How It Works (Mechanism)

**SSH hardening:**

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers deploy ansibleuser
# Limit to specific users
Protocol 2
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
AllowTcpForwarding no
# Apply:
systemctl reload sshd
```

**Firewall with nftables (modern default):**

```bash
# /etc/nftables.conf
table inet filter {
  chain input {
    type filter hook input priority 0
    policy drop              # default DENY

    iif lo accept            # loopback
    ct state established,related accept   # return traffic
    tcp dport 22 accept      # SSH
    tcp dport { 80, 443 } accept  # web
    icmp type echo-request accept  # ping
    # Everything else dropped
  }
  chain forward {
    type filter hook forward priority 0
    policy drop
  }
  chain output {
    type filter hook output priority 0
    policy accept
  }
}

systemctl enable --now nftables
```

**Kernel security parameters:**

```bash
# /etc/sysctl.d/99-hardening.conf

# Network
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.disable_ipv6 = 1

# Kernel
kernel.randomize_va_space = 2   # ASLR: full randomisation
kernel.dmesg_restrict = 1       # non-root can't read dmesg
kernel.kptr_restrict = 2        # hide kernel pointers
kernel.yama.ptrace_scope = 1    # restrict ptrace
fs.suid_dumpable = 0            # no core dumps from SUID
fs.protected_hardlinks = 1
fs.protected_symlinks = 1

# Apply immediately
sysctl --system
```

**Audit logging with auditd:**

```bash
# /etc/audit/rules.d/hardening.rules
# Log all authentication failures
-w /var/log/faillog -p wa -k auth_failures
-w /var/log/lastlog -p wa -k auth_failures

# Monitor sudoers changes
-w /etc/sudoers -p wa -k sudoers_changes
-w /etc/sudoers.d/ -p wa -k sudoers_changes

# Monitor privileged command usage
-a always,exit -F arch=b64 \
  -S execve -F euid=0 -k root_commands

# Monitor /etc and /bin modifications
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /usr/bin/ -p wa -k bin_changes

# Query audit logs
ausearch -k sudoers_changes -ts recent
```

**Fail2ban for SSH brute-force protection:**

```bash
# /etc/fail2ban/jail.local
[sshd]
enabled = true
maxretry = 3
findtime = 600    # within 10 minutes
bantime = 3600    # ban for 1 hour
bantime.increment = true
bantime.multiplier = 2  # doubles on repeat offenders

systemctl enable --now fail2ban
# Check banned IPs:
fail2ban-client status sshd
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  CIS Hardening Implementation Order            │
└────────────────────────────────────────────────┘

 1. INITIAL STATE
    └── Default install: ~50 services, 20+ ports open,
        root SSH enabled, password auth, no firewall

 2. MINIMAL INSTALL
    └── Remove: telnet, rsh, xinetd, talk, rpc
        Keep: sshd, cron, rsyslog, auditd

 3. FILESYSTEM HARDENING
    └── /tmp: nosuid,noexec,nodev mount options
        Find world-writable files: fix/remove
        SUID/SGID audit: remove unnecessary ones
        Set umask 027 in /etc/profile

 4. AUTHENTICATION HARDENING
    └── Disable root SSH login
        Disable password SSH auth
        Set password complexity (PAM)
        Set account lockout (PAM pam_faillock)
        Set password expiry (chage)

 5. NETWORK HARDENING
    └── iptables/nftables: default DROP
        Open only required ports
        Fail2ban: SSH brute force protection
        sysctl: disable IP forwarding, enable syncookies

 6. KERNEL HARDENING
    └── sysctl: ASLR, dmesg_restrict, kptr_restrict
        Disable kernel modules if not needed
        Enable Secure Boot / UEFI signing

 7. MAC (SELinux/AppArmor)
    └── Enable enforcing mode
        Ensure all confined services have correct contexts

 8. MONITORING & AUDITABILITY
    └── auditd: rules for sudoers, passwd, bins
        rsyslog: centralised log shipping
        AIDE: filesystem integrity monitoring baseline

 9. ONGOING
    └── Lynis audit: score monthly
        Unattended security upgrades
        Regular review of new CVEs
```

---

### 💻 Code Example

**Example — Hardening script for a new server:**

```bash
#!/bin/bash
# Basic Linux hardening checklist runner
# Run as root. Prints PASS/FAIL for each check.

PASS="[ PASS ]"
FAIL="[ FAIL ]"

echo "=== Linux Security Hardening Audit ==="
echo ""

# 1. Root SSH login
ROOT_SSH=$(sshd -T 2>/dev/null | \
  grep "^permitrootlogin" | awk '{print $2}')
if [ "$ROOT_SSH" = "no" ]; then
  echo "$PASS Root SSH login disabled"
else
  echo "$FAIL Root SSH login allowed: $ROOT_SSH"
  echo "  Fix: PermitRootLogin no in /etc/ssh/sshd_config"
fi

# 2. Password auth
PASSWD_AUTH=$(sshd -T 2>/dev/null | \
  grep "^passwordauthentication" | awk '{print $2}')
if [ "$PASSWD_AUTH" = "no" ]; then
  echo "$PASS SSH password auth disabled"
else
  echo "$FAIL SSH password auth allowed"
  echo "  Fix: PasswordAuthentication no in sshd_config"
fi

# 3. Firewall active
if systemctl is-active --quiet nftables || \
   systemctl is-active --quiet iptables || \
   systemctl is-active --quiet ufw; then
  echo "$PASS Firewall is active"
else
  echo "$FAIL No firewall active"
fi

# 4. ASLR enabled
ASLR=$(sysctl -n kernel.randomize_va_space)
[ "$ASLR" = "2" ] && \
  echo "$PASS ASLR fully enabled (level 2)" || \
  echo "$FAIL ASLR not fully enabled: $ASLR"

# 5. dmesg restriction
DMESG=$(sysctl -n kernel.dmesg_restrict 2>/dev/null)
[ "$DMESG" = "1" ] && \
  echo "$PASS dmesg restricted to root" || \
  echo "$FAIL dmesg not restricted: $DMESG"

# 6. Core dumps disabled for SUID
SUID_DUMP=$(sysctl -n fs.suid_dumpable)
[ "$SUID_DUMP" = "0" ] && \
  echo "$PASS SUID core dumps disabled" || \
  echo "$FAIL SUID core dumps enabled: $SUID_DUMP"

# 7. auditd running
if systemctl is-active --quiet auditd; then
  echo "$PASS auditd is running"
else
  echo "$FAIL auditd is not running"
fi

# 8. fail2ban
if systemctl is-active --quiet fail2ban; then
  echo "$PASS fail2ban is running"
else
  echo "$FAIL fail2ban is not running"
fi

# 9. World-writable files
WORLD_WRITE=$(find / -xdev -type f -perm -002 \
  2>/dev/null | grep -v /proc | grep -v /sys | wc -l)
if [ "$WORLD_WRITE" = "0" ]; then
  echo "$PASS No world-writable files"
else
  echo "$FAIL $WORLD_WRITE world-writable files found"
  echo "  Audit: find / -xdev -type f -perm -002"
fi

echo ""
echo "Run 'lynis audit system' for full CIS benchmark audit"
```

---

### ⚖️ Comparison Table

| Control                      | Prevents                               | Complexity    | Impact                |
| ---------------------------- | -------------------------------------- | ------------- | --------------------- |
| SSH key auth + no root login | Password brute force, root abuse       | Low           | Low                   |
| Firewall (default deny)      | Port scanning, exposed services        | Medium        | Medium                |
| Fail2ban                     | SSH brute force                        | Low           | Very low              |
| ASLR + NX                    | Memory corruption exploits             | None (kernel) | None                  |
| SELinux/AppArmor             | Privilege escalation, lateral movement | High          | High (may break apps) |
| auditd                       | Detection (post-compromise)            | Medium        | Low                   |
| AIDE                         | File tampering detection               | Medium        | Low                   |
| Unattended upgrades          | Known CVE exploitation                 | Low           | Medium (reboots)      |

How to choose: implement from top (SSH/firewall) to bottom (AIDE); each layer adds protection but also operational complexity. Start with Level 1 CIS benchmark for baseline, move to Level 2 for high-security environments.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                  |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A firewall alone makes a system secure                      | The firewall protects network access; it does nothing about compromised application code, misconfigured services, or weak credentials                    |
| Root account should just have a strong password             | Root over SSH with password auth is vulnerable to brute force; disable root SSH and use key-based auth for named accounts                                |
| Security and convenience are mutually exclusive             | Modern key-based SSH with SSH agent is more convenient than remembering passwords; most hardening measures have minimal operational overhead once set up |
| Once hardened, always secure                                | Hardening is not a one-time task; new CVEs, new services, and configuration drift require continuous monitoring and re-assessment                        |
| disabling SELinux is acceptable to "fix" application issues | Every SELinux denial has a legitimate fix; disabling SELinux removes the entire MAC layer as a workaround                                                |

---

### 🚨 Failure Modes & Diagnosis

**Server Compromised Despite "Standard" Security Measures**

**Symptom:**
Unexpected outbound connections. High CPU. Unknown processes. `/tmp/` contains binary files.

**Root Cause:**
One or more hardening controls missing. Common vectors: weak SSH password on a service account; outdated application with known CVE; world-writable directory used for file upload that allowed code execution.

**Diagnostic Steps:**

```bash
# 1. Check running processes
ps auxf
# Look for unknown processes, especially in /tmp /var/tmp /dev/shm

# 2. Check network connections
ss -tlnp          # listening ports
ss -tnp           # active outbound connections

# 3. Check recently modified files
find / -newer /tmp/ref_timestamp -type f \
  2>/dev/null | grep -v /proc | grep -v /sys

# 4. Check audit logs
ausearch -ts today | grep -i exec

# 5. Check for cron-based persistence
for user in $(cut -d: -f1 /etc/passwd); do
  crontab -l -u $user 2>/dev/null && echo "User: $user"
done

# 6. Check login history
last | head -20
lastb | head -20   # failed logins
```

**Response:** Isolate the system (firewall it off or snapshot and terminate), conduct forensic investigation on the snapshot, rebuild from clean image with full hardening.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Users and Groups` — hardening is fundamentally about restricting who can do what; users, groups, `sudo`, and file permissions are the foundation
- `SSH` — SSH hardening is the single most impactful hardening step for internet-facing servers

**Builds On This (learn these next):**

- `SELinux / AppArmor` — MAC layer is a key component of hardening; this entry is a prerequisite
- `iptables / nftables` — deep dive into the firewall component of hardening
- `Observability & SRE` — monitoring and alerting are the detection layer of hardening

**Alternatives / Comparisons:**

- `Cloud Security Groups / IAM` — cloud providers layer additional security controls above the OS; understanding OS-level hardening enables you to understand what the cloud layer does and does not cover
- `Immutable Infrastructure` — replacing the concept of "hardening a running system" with "deploy fresh, never mutate in place"

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Systematic attack surface reduction:      │
│              │ disable unused services, restrict privs,  │
│              │ strong auth, MAC, audit logging           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Default Linux is "open for convenience"  │
│ SOLVES       │ → needs to be "deny by default" for prod  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Hardening is multiplicative — layers      │
│              │ compound; breach of one layer ≠ total     │
│              │ compromise (defense-in-depth)             │
├──────────────┼───────────────────────────────────────────┤
│ TOP 5        │ 1. SSH: key auth, no root login           │
│ CONTROLS     │ 2. Firewall: default DROP                 │
│              │ 3. Kernel: ASLR, no IP forward            │
│              │ 4. SELinux/AppArmor: enforcing            │
│              │ 5. auditd: log security events            │
├──────────────┼───────────────────────────────────────────┤
│ AUDIT TOOL   │ lynis audit system (score 0-100)          │
│              │ openscap for CIS/STIG compliance          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Lock every door, set an alarm on each,   │
│              │ and review the camera footage daily"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SELinux → auditd → AIDE → Falco           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A startup's engineering team argues that "we run everything on Kubernetes in a cloud VPC with security groups — we don't need OS-level hardening." Systematically dismantle this argument by identifying: (a) three attack vectors that bypass security groups and VPC, (b) two container escape scenarios where OS-level hardening (SELinux, kernel hardening, file system restrictions) limits blast radius, and (c) the specific CIS Benchmark controls that are relevant for Kubernetes worker nodes, explaining why each exists at the OS layer rather than the K8s layer.

**Q2.** You inherit a five-year-old production Linux server. Outline the complete hardening audit process: what tools you run, what output you collect, how you prioritise findings, which changes require a maintenance window vs can be applied live, and how you validate that hardening changes didn't break the application — citing specific commands and config file locations.
