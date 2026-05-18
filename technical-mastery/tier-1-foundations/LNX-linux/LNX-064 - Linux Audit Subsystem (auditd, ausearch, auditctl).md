---
id: LNX-064
title: "Linux Audit Subsystem (auditd, ausearch, auditctl)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-034, LNX-057
used_by: LNX-079, LNX-100
related: LNX-057, LNX-079, LNX-034
tags: [auditd, auditctl, ausearch, aureport, audit-rules, syscall-audit, file-watch, compliance, SELinux, PCI-DSS]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/lnx/linux-audit-subsystem/
---

## TL;DR

The Linux audit subsystem captures kernel-level security events: file
access, system calls, user logins. **auditd** daemon writes to
`/var/log/audit/audit.log`. **auditctl** manages rules at runtime.
**ausearch** queries logs by key/user/time. **aureport** generates summary
reports. Key rules: watch files (`-w /etc/passwd -p wa -k passwd-changes`),
track syscalls (`-a always,exit -F arch=b64 -S execve -k exec`). Persist
rules in `/etc/audit/rules.d/`. Essential for PCI DSS, HIPAA, SOX compliance.
`auditd` operates at the kernel level - even root can't hide from it.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-064 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | auditd, auditctl, ausearch, aureport, audit-rules, compliance, syscall audit, file-watch |
| **Prerequisites** | LNX-034 (Logs / syslog), LNX-057 (Security) |

---

### The Problem This Solves

**Problem 1**: A security incident investigation: "Who modified `/etc/sudoers`
last week?" Without audit: check `ls -la /etc/sudoers` for mtime, then...
nothing. With audit: `ausearch -k sudoers-changes --start last-week --end today`
shows exactly who (UID), when, from what process, and what change was made.
The audit log is the forensic record that makes post-incident investigation
possible.

**Problem 2**: PCI DSS compliance requires logging all access to cardholder
data systems, all sudo usage, all privileged command execution. auditd
provides the kernel-level certainty: because audit rules run in the kernel,
even root processes can't circumvent them (unlike application-level logging
which privileged code can disable or modify).

---

### Textbook Definition

**Linux Audit Subsystem**: A kernel-level event logging framework that
records security-relevant events. Distinct from syslog: audit events come
from the kernel audit framework, not from userspace processes. Key property:
kernel-level audit rules CANNOT be bypassed by userspace, even root (unless
the kernel itself is compromised or audit rules are deleted).

**auditd**: The userspace daemon that receives kernel audit messages and
writes them to `/var/log/audit/audit.log`. Survives syslog being killed.
Configurable in `/etc/audit/auditd.conf`.

**auditctl**: CLI tool to add/remove/list audit rules at runtime. Rules
are lost on reboot unless persisted.

**audit rules types:**
- **File system watch** (`-w path -p permissions -k key`): fires on file/dir access
- **System call rule** (`-a action,list -S syscall`): fires on specific syscall
- **Control rule** (`-e 0|1|2`): enable/disable, lock rules)

**ausearch/aureport**: Tools to query and summarize the audit log.

---

### Understand It in 30 Seconds

```bash
# === Check auditd status ===
systemctl status auditd
auditctl -s      # kernel audit status (enabled, pid, lost, backlog)

# === List current rules ===
auditctl -l      # list all active rules
# If no rules: auditd is running but watching nothing

# === File watch rules (most common) ===
# Watch a file for writes and attribute changes:
auditctl -w /etc/passwd -p wa -k passwd-changes
# -w = watch path
# -p wa = permissions: (w)rite, (a)ttribute change
#   permissions: r=read, w=write, x=execute, a=attribute change
# -k = key (tag for searching logs)

# Watch sensitive files:
auditctl -w /etc/shadow -p wa -k shadow-changes
auditctl -w /etc/sudoers -p wa -k sudoers-changes
auditctl -w /etc/sudoers.d/ -p wa -k sudoers-changes
auditctl -w /etc/ssh/sshd_config -p wa -k sshd-config

# Watch a directory (and everything in it):
auditctl -w /var/www/html -p wa -k webroot-changes

# === System call rules ===
# Track all program executions (exec):
auditctl -a always,exit -F arch=b64 -S execve \
    -F uid!=root -k user-exec
# -a always,exit = always audit, filter at syscall exit
# -F arch=b64 = 64-bit (also add -F arch=b32 for 32-bit)
# -S execve = the execve() syscall (program launch)
# -F uid!=root = exclude root (reduce noise; remove for full audit)
# -k user-exec = search key

# Track privileged command usage:
auditctl -a always,exit -F path=/usr/bin/sudo -F perm=x \
    -F auid>=1000 -k sudo-usage
# -F auid>=1000 = only non-system users (auid = audit UID at login)

# Track file deletion:
auditctl -a always,exit -F arch=b64 -S unlink -S unlinkat \
    -F auid>=1000 -k file-deletion

# === Search logs ===
ausearch -k passwd-changes     # by key
ausearch -k passwd-changes -i  # -i = interpret UIDs/GIDs to names
ausearch -m USER_CMD            # by message type (sudo commands)
ausearch -m EXECVE              # program executions
ausearch -ui 1000               # by user ID
ausearch -ua admin              # by username

# Time-bounded search:
ausearch -k passwd-changes \
    --start 2024-01-01 --end 2024-01-07
ausearch -k passwd-changes --start today

# Interactive / recent events:
ausearch -ts recent -k passwd-changes   # last 10 minutes

# === Summary reports ===
aureport                       # overall summary
aureport --summary             # brief summary
aureport -au                   # authentication events
aureport -x                    # executable events
aureport --failed              # failed access events
aureport -i                    # interpret IDs to names
aureport --start today --end now

# === Persist rules ===
# /etc/audit/rules.d/*.rules files are loaded at auditd startup
cat > /etc/audit/rules.d/security.rules << 'EOF'
## Lock audit rules (prevents modification without reboot):
##-e 2

## Audit file access for sensitive files:
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudo-config
-w /etc/sudoers.d/ -p wa -k sudo-config
-w /etc/ssh/sshd_config -p wa -k sshd-config

## Privileged command use:
-a always,exit -F arch=b64 -S execve -F uid=0 -k root-commands

## File deletion:
-a always,exit -F arch=b64 -S unlink -S unlinkat -F auid>=1000 -k deletion
EOF

# Load rules without reboot:
augenrules --load    # process /etc/audit/rules.d/ into /etc/audit/audit.rules
# or:
auditctl -R /etc/audit/audit.rules
```

---

### First Principles

**Audit event anatomy:**
```bash
# Raw audit log entry from /var/log/audit/audit.log:
# type=SYSCALL msg=audit(1705000000.123:4567): arch=c000003e syscall=2
# success=yes exit=3 a0=7ffe1234 a1=0 a2=0 a3=... items=1
# ppid=12345 pid=12346 auid=1000 uid=0 gid=0 euid=0 suid=0 fsuid=0
# egid=0 sgid=0 fsgid=0 tty=pts0 ses=5 comm="cat" exe="/usr/bin/cat"
# subj=system_u:system_r:kernel_t:s0 key="passwd-changes"
#
# type=PATH msg=audit(1705000000.123:4567): item=0
# name="/etc/passwd" inode=123 dev=fd:01 mode=0100644
# ouid=0 ogid=0 rdev=00:00 obj=... nametype=NORMAL cap_fp=0 cap_fi=0

# Decoded fields:
# arch=c000003e = x86-64 architecture
# syscall=2 = open() (syscall number 2 on x86-64)
# success=yes = syscall succeeded
# auid=1000 = audit UID (the UID at login, even through sudo)
# uid=0 = current effective UID (this ran as root via sudo)
# pid=12346 = process ID
# comm="cat" = command name (short, 16 chars max)
# exe="/usr/bin/cat" = full executable path
# key="passwd-changes" = the search key we set

# KEY INSIGHT: auid (audit UID) vs uid
# When you SSH as "alice" (uid=1000) then sudo to root (uid=0):
# auid = 1000 (alice - the login identity, preserved through sudo)
# uid = 0 (the current effective uid = root)
# This is HOW audit tracks who really did something even through sudo!
# auid is set at login and stays with the session.
# If uid=0 and auid=1000: root command run by user with uid 1000 (via sudo)
# If uid=0 and auid=4294967295 (0xffffffff): no-session root (e.g. cron, init)
```

**How file watches work:**
```
auditctl -w /etc/passwd -p wa -k passwd-changes
         |
         v
Kernel: register inotify-like watch on inode for /etc/passwd
Rule: on write or attribute change to this inode, generate audit record

When "vim /etc/passwd" saves the file:
  vim calls: open("/etc/passwd", O_WRONLY|O_TRUNC) -> syscall triggers audit
  Kernel audit: was this path/inode being watched with 'w' permission?
  YES -> generate SYSCALL record + PATH record -> send to auditd

auditd: receives kernel netlink message -> writes to /var/log/audit/audit.log

Fields captured:
  Who: auid (original login uid), uid (current uid), pid, comm, exe
  What: syscall, success, args
  When: timestamp
  Which file: name, inode, device

Limitation: watches are per-inode, not per-path.
  If /etc/passwd is deleted and recreated (vim does this by default!):
  The inode changes -> need to restart auditd or re-add watch.
  Some editors (vim, emacs) replace files atomically (delete + create).
  Solution: watch the directory instead: -w /etc/ -p wa (watches entire dir)
  Or use "-w /etc/passwd -p wa" but be aware of editor-based file replacement.
```

---

### Thought Experiment

Incident response investigation:

```bash
# Scenario: Alert: privilege escalation detected on prod-server-01
# SSH access log shows unusual sudo activity
# Task: determine what happened using auditd

# Step 1: When did the incident start? (from alert, ~14:00 yesterday)
ausearch --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00 \
    -m USER_AUTH,USER_CMD,EXECVE -i 2>/dev/null | head -100

# Step 2: Find all sudo commands in the window:
ausearch --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00 \
    -m USER_CMD -i 2>/dev/null
# Output shows: who ran sudo, what command, when

# Step 3: Find file modifications:
ausearch --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00 \
    -k identity,sudo-config,sshd-config -i 2>/dev/null

# Example output (interpreted with -i):
# time->Mon Jan 15 14:23:45 2024
# type=USER_CMD msg=audit(1705330425.123:9876):
# pid=23456 uid=root auid=1001 ses=12 msg='cwd="/root" cmd=6563686F20...
# The cmd is hex-encoded command:
ausearch --start 2024-01-15 14:23:45 -m USER_CMD | \
    while IFS= read -r line; do
        echo "$line" | sed 's/cmd=\([0-9a-f]*\)/echo cmd=\1 decoded=$(echo -e "\\x\1" | xxd -r -p)/e'
    done

# Better: use aureport for summary, then ausearch for details:
aureport --summary --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00

# Step 4: Find new files created:
ausearch -m CREATE --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00 -i

# Step 5: Authentication events:
aureport --auth --start 2024-01-15 14:00:00 --end 2024-01-15 15:00:00
```

---

### Mental Model / Analogy

```
Audit subsystem = security camera in a bank vault

Regular syslog = store receipt printer
  Only records what the cashier (software) chooses to print
  A malicious cashier can choose NOT to print anything
  Even root can tell the printer to stop

Audit subsystem = ceiling-mounted security camera
  Records everything at the hardware level
  The cashier can't turn it off without the security manager's override
  Even root can't delete records without being recorded doing it
  (auditctl -e 2 = locked mode: rules can't be changed without reboot)

auditctl = camera programming panel
  "Watch this door (file) for opens and closes"
  "Record any time someone runs sudo"
  "Log all network connections"

ausearch = VCR playback with fast-forward
  "Show me all activity from camera 3 (key='passwd-changes') from last Tuesday"
  "Show me all clips where person #1001 (uid=1001) was in the frame"

aureport = the security guard's summary report
  "10 failed login attempts, 3 sudo uses, 2 file modifications today"

auid = the initial badge scan at the door
  Even if someone changes clothes (sudo to root), their initial badge scan
  (auid) is recorded throughout their session.
  auid=1000 who uid=0 = "alice (badge 1000) is currently in root costume"
  
  This is the key forensic capability: tracing root actions back to the
  person who logged in, even through privilege escalation layers.
```

---

### Gradual Depth - Five Levels

**Level 1:**
auditd is running (check `systemctl status auditd`). `auditctl -l` for
current rules. `auditctl -w /etc/passwd -p wa -k key` for file watches.
`ausearch -k key` to find events. Log location: `/var/log/audit/audit.log`.
`aureport` for summary. Rules persistence in `/etc/audit/rules.d/`.

**Level 2:**
System call rules with `-a always,exit -S execve`. auid vs uid (audit trail
through sudo). `ausearch -i` for interpreted output. Rule ordering and
performance impact. `auditctl -e 2` (locked mode for compliance). Event
types: SYSCALL, PATH, EXECVE, USER_CMD, USER_AUTH. Rule matching with `-F`
filters.

**Level 3:**
Writing complex rules: multiple syscalls in one rule (`-S open -S openat`).
Performance tuning: how many rules before audit becomes a bottleneck.
`auditctl -s` to check backlog/lost events. Audit dispatcher plugins
(audisp): sending audit events to syslog, SIEM systems. `auditd.conf`:
`space_left`, `admin_space_left`, `disk_full_action` (critical: audit must
not stop on disk full for compliance). `ausyscall` for syscall name lookup.

**Level 4:**
Custom audit event types with `audit_log_user_message()` from auditd library.
Integration with SIEM (Splunk, ELK): forwarding via syslog or audisp plugin.
auditbeat (Elastic) for normalized audit forwarding. SELinux AVC denials in
the audit log: `ausearch -m AVC` for SELinux policy violations. Real-time
alerting: `auditd` with `audisp-syslog` to rsyslog, then alerting on patterns.
Per-rule performance: `-a never` rules to exclude noisy events before logging.

**Level 5:**
Audit kernel implementation: `audit_filter_syscall()`, the ring buffer, netlink
socket to userspace. Limitations: audit is not tamper-proof if root can load
kernel modules (rootkits can hook the audit functions). Defense: use IMA
(Integrity Measurement Architecture) for detecting module loads, combined with
UEFI Secure Boot. Immutable audit infrastructure: forward logs to a WORM
storage or external syslog server not accessible from the audited host. DISA
STIG and CIS benchmark audit requirements: exact rule sets for compliance.
Integrity monitoring vs access monitoring: AIDE/Tripwire for file integrity
vs auditd for access logging.

---

### Code Example

**BAD - audit configuration mistakes:**
```bash
# BAD 1: Watching /etc/passwd with read permission on high-traffic system:
auditctl -w /etc/passwd -p rwa -k identity
# -r (read) = EVERY program that reads /etc/passwd generates an event
# /etc/passwd is read by getpwnam(), ls -l, ps, many programs
# Result: thousands of audit events per second, fills disk, impacts perf

# GOOD: Watch only writes and attribute changes:
auditctl -w /etc/passwd -p wa -k identity
# Catches: modifications, but not normal reads (which are harmless)

# BAD 2: Not persisting rules:
auditctl -w /etc/shadow -p wa -k shadow
# Disappears on reboot!

# GOOD: Add to /etc/audit/rules.d/shadow.rules:
echo "-w /etc/shadow -p wa -k shadow" > \
    /etc/audit/rules.d/shadow.rules
augenrules --load   # apply without reboot

# BAD 3: Locking audit rules before verifying they work:
auditctl -e 2   # lock!
# Now rules can't be changed without reboot
# If you locked wrong rules: need reboot to fix

# GOOD: Test rules first, then lock:
# 1. Add rules and test with ausearch
# 2. Verify no performance issues (check auditctl -s for lost events)
# 3. Add -e 2 to LAST line of /etc/audit/rules.d/99-finalize.rules
# 4. Load and verify: augenrules --load
```

**GOOD - compliance rule set:**
```bash
# /etc/audit/rules.d/30-compliance.rules
# PCI DSS + general security audit rules

## Identity files:
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/security/opasswd -p wa -k identity

## Privilege escalation:
-w /etc/sudoers -p wa -k sudo-config
-w /etc/sudoers.d/ -p wa -k sudo-config
-a always,exit -F arch=b64 -F path=/usr/bin/sudo -F perm=x \
    -F auid>=1000 -k sudo-use

## SSH configuration:
-w /etc/ssh/sshd_config -p wa -k sshd-config
-w /etc/ssh/ -p wa -k sshd-dir

## All commands run by root (auid=unset means no-login session):
-a always,exit -F arch=b64 -S execve -F uid=0 -F auid!=4294967295 \
    -k root-commands
## All commands run by non-root users:
-a always,exit -F arch=b64 -S execve -F auid>=1000 \
    -k user-commands

## File deletion:
-a always,exit -F arch=b64 -S unlink -S unlinkat -S rename -S renameat \
    -F auid>=1000 -k file-delete

## Network configuration changes:
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k net-change
-w /etc/hosts -p wa -k net-config
-w /etc/network/ -p wa -k net-config
-w /etc/sysconfig/network -p wa -k net-config

## Crontab changes (common persistence mechanism):
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron
-w /etc/crontab -p wa -k cron

## Lock rules at the end (uncomment for production):
## -e 2
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "auditd is the same as syslog" | They are completely separate systems. Syslog: userspace daemon collecting messages from applications and kernel via `/dev/log`, `/dev/kmsg`, and sockets. Applications CHOOSE to log to syslog. A malicious or compromised application can simply not call `syslog()`. auditd: kernel audit framework that records events at the syscall level REGARDLESS of what the application does. The kernel enforces audit rules, not the application. Root can delete audit log files (if not protected), but the events are generated before root can intervene. |
| "Watching a file with `-p rwa` captures more security events" | Adding read (`-r`) to a file watch generates events for EVERY process that reads the file. `/etc/passwd` is read by `getpwnam()` which is called by `ls -l`, `ps`, any program doing user lookups - potentially thousands of events per second. This creates noise, fills disk, and has performance impact. For security, writes (`-w`) and attribute changes (`-a`) are what matter: reads of `/etc/passwd` are normal, modifications are suspicious. Only add read watches for highly sensitive files accessed infrequently (e.g., private keys). |
| "ausearch requires the audit log to be local" | ausearch reads `/var/log/audit/audit.log` by default. But it can read from a file: `ausearch -if /backup/audit.log.2024-01-15 -k identity`. This is important for forensics: you can analyze historical audit logs after an incident. Also: some SIEM pipelines forward audit events to Elasticsearch/Splunk via audisp plugins - in that case you'd query the SIEM directly rather than ausearch. |
| "audit -e 2 (immutable mode) makes the system completely secure" | `-e 2` prevents audit rules from being modified without a reboot. It does NOT protect the audit log file. If root does `rm /var/log/audit/audit.log` or `echo > /var/log/audit/audit.log`, the evidence is gone. Defense: (1) Send audit events to a remote syslog server via `audisp-syslog` plugin. (2) Mount `/var/log/audit/` with appropriate SELinux labels so even root can't delete via normal means. (3) Use append-only filesystem attributes: `chattr +a /var/log/audit/audit.log`. True tamper-resistance requires: remote forwarding + WORM storage. |
| "The audit log shows the exact content written to files" | auditd records WHO accessed WHAT file and WHEN, via which syscall. It does NOT record the actual content of reads or writes. For content capture you would need application-level logging, kernel `inotify` with content capture, or specialized tools like `osquery` with file integrity monitoring. Audit logs are invaluable for forensics (timeline, who, what operations) but not for content forensics. |

---

### Failure Modes & Diagnosis

**Audit backlog overflow:**
```bash
# Symptom: auditd generates "lost" events, performance degraded
auditctl -s
# enabled 1
# failure 1
# pid 12345
# rate_limit 0
# backlog_limit 8192
# lost 1523       <- audit events lost because backlog was full!
# backlog 0

# Cause: too many audit rules generating too many events
# Common culprit: -S execve on a busy system (many process launches)

# Diagnosis: measure audit event rate:
auditctl -s | grep backlog
# Check if auditd is falling behind:
ausearch -ts recent 2>/dev/null | wc -l  # events in last 10 min

# Fix 1: Increase backlog limit (kernel buffer):
auditctl -b 16384     # increase from 8192 to 16384
# Persist in /etc/audit/rules.d/10-backlog.rules:
echo "-b 16384" > /etc/audit/rules.d/10-backlog.rules

# Fix 2: Add exclusion rules to reduce noise:
# Exclude noisy processes from execve tracking:
auditctl -a never,exit -F arch=b64 -S execve \
    -F exe=/usr/bin/python3 -k exclude-python
# Or exclude by UID (system daemons):
auditctl -a always,exit -F arch=b64 -S execve \
    -F auid!=4294967295 -F uid>=1000 -k user-exec
# Only track interactive user sessions (auid set + non-system uid)

# Fix 3: Set failure action (what to do when backlog overflows):
# In /etc/audit/auditd.conf:
# failure=1 (print message, continue - default)
# failure=2 (panic: kernel panics if audit fails - for high-security systems)
```

---

### Related Keywords

**Foundational:**
LNX-034 (System Logs), LNX-057 (Linux Security)

**Builds on this:**
LNX-079 (Linux Security Modules - SELinux AVC in audit log)

**Related:**
LNX-100 (Hardening at Scale - CIS/STIG audit requirements)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `auditctl -l` | List all active audit rules |
| `auditctl -s` | Audit subsystem status |
| `auditctl -w /path -p wa -k KEY` | Watch file for writes |
| `ausearch -k KEY -i` | Search by key (interpreted) |
| `ausearch -m USER_CMD` | All sudo commands |
| `ausearch -ts today` | Events since today |
| `aureport --summary` | Summary of all events |
| `aureport --auth` | Authentication events |

**3 things to remember:**
1. `auid` = original login UID (persists through sudo); critical for "who really ran that root command"
2. `-p wa` for file watches (writes + attribute changes); avoid `-p r` on common files - extremely noisy
3. Rules are runtime-only until saved in `/etc/audit/rules.d/` and loaded with `augenrules --load`

---

### Transferable Wisdom

Audit concepts appear in: AWS CloudTrail = cloud audit subsystem (who called
which API, when, from where). GCP Cloud Audit Logs and Azure Activity Log
same concept. SIEM (Splunk, Elastic SIEM, QRadar) ingest auditd logs as
primary data source for threat detection. `auditbeat` (Elastic) = a modern
exporter that reads auditd events and ships to Elasticsearch. osquery tables
(`process_events`, `file_events`) layer on top of auditd for SQL-queryable
audit events. Kubernetes audit logging: same concept at API level (`audit.k8s.io`
policy) - which ServiceAccount called which API verb on which resource.
Database audit logs (PostgreSQL `pgaudit`, MySQL audit plugin): same pattern -
who ran what query when. The concept "kernel-level audit bypass-resistant"
appears in: eBPF security tools (Falco, Tetragon) which use eBPF programs
to capture events at the kernel level, similar to auditd but more flexible.
Compliance frameworks (PCI DSS, HIPAA, SOX) all require audit trails - auditd
is the Linux implementation of this universal requirement.

---

### The Surprising Truth

The Linux audit subsystem was originally built not for security teams but
for NSA's SELinux research project. The NSA needed a way to log all syscalls
from security-labeled processes to prove that the mandatory access controls
were working as designed. The `auid` (audit UID) field - the most powerful
forensic capability of auditd - exists because NSA required the ability to
trace every root action back to the human who logged in, even through
privilege escalation. The kernel development community was initially skeptical
("why does the NSA need this in the mainline kernel?") but the feature was
merged in 2003. Today, `auditd` is required by DISA STIGs (which originated
as DoD security requirements), PCI DSS, HIPAA, and virtually every compliance
framework. The surprising part: the most widely-used forensic tool in
enterprise Linux wasn't built for enterprise security - it was built for a
government MAC system proof-of-concept that most people will never use
(SELinux MCS/MLS). The general audit capability was essentially a
"side effect" that turned out to be far more useful than the original goal.

---

### Mastery Checklist

- [ ] Can add file watch rules and syscall audit rules with auditctl
- [ ] Can search audit logs with ausearch by key, user, and time
- [ ] Understands auid vs uid and why it matters for forensic attribution
- [ ] Can persist audit rules in /etc/audit/rules.d/ and load with augenrules
- [ ] Can diagnose audit backlog/lost events and tune the backlog limit

---

### Think About This

1. You need to prove to a PCI DSS auditor that all access to files in
   `/var/data/cardholder/` has been logged for the past 90 days, and that
   privileged users can be traced even when operating as root. Design the
   specific auditctl rules that would satisfy these requirements, and
   explain what the `auid` field in the audit log provides that `uid`
   alone cannot.

2. After adding `-a always,exit -F arch=b64 -S execve` to your audit rules
   on a busy web server, you see `lost 50000` in `auditctl -s`. The rule
   is required for compliance. Describe three approaches to reduce the
   event rate while still satisfying the "track all program executions by
   interactive users" requirement, and explain the trade-offs of each.

3. A security engineer says "we have auditd running, so we have tamper-proof
   audit logs." Describe two scenarios where a determined attacker with root
   access could still destroy or invalidate the audit evidence, and propose
   the infrastructure changes that would make the audit trail genuinely
   tamper-resistant for a compliance investigation.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `uid` and `auid` in audit logs, and why does it matter?
A: Both fields appear in audit records but represent different things: `uid` = the CURRENT effective user ID of the process at the moment the audit event was generated. If someone runs `sudo -i` and then runs commands as root, `uid=0`. It tells you what privilege level the process had right now. `auid` (audit UID) = the ORIGINAL user ID at login time, set when the user first authenticated and preserved for the entire session, even through `sudo`, `su`, or `runuser`. If "alice" (uid=1000) SSH's in, her auid=1000 is set. When she runs `sudo cat /etc/shadow`, the resulting audit record shows `uid=0` (running as root) AND `auid=1000` (alice's login identity). WITHOUT auid: the audit record for a root operation shows `uid=0` with no way to know which human ran it (all root processes look the same). WITH auid: you can trace any root operation back to the specific human user who authenticated and performed the action. The value `auid=4294967295` (0xffffffff) means "no audit login" - the process was started by a daemon, cron job, or init (no human login session). This is how you distinguish "root action by a script" vs "root action by a human via sudo." Practical forensics: `ausearch -ua alice -i` finds all audit events from Alice's sessions, including commands run as root. This is exactly what PCI DSS means by "individual user accountability" - you can attribute every root action to a human.

**Expert:**
Q: How would you set up audit rules to detect common persistence techniques used by attackers?
A: Post-exploitation persistence commonly involves: cron jobs, systemd services, SSH key addition, SUID binary creation. Here are specific audit rules for each: (1) CRON PERSISTENCE: `-w /etc/cron.d/ -p wa -k persistence-cron`, `-w /etc/cron.daily/ -p wa -k persistence-cron`, `-w /var/spool/cron/ -p wa -k persistence-cron`. (2) SYSTEMD SERVICE CREATION: `-w /etc/systemd/system/ -p wa -k persistence-systemd`, `-w /usr/lib/systemd/system/ -p wa -k persistence-systemd`. (3) SSH KEY ADDITION: `-a always,exit -F arch=b64 -S open -F dir=/home -F name=authorized_keys -F perm=wa -k persistence-ssh`. Or: `-w /root/.ssh/ -p wa -k persistence-ssh-root`. (4) SETUID BINARY CREATION: `-a always,exit -F arch=b64 -S chmod -S fchmod -S fchmodat -F auid>=1000 -k setuid-change`. Then alert when mode includes 04000 (setuid). (5) LD_PRELOAD PERSISTENCE: `-w /etc/ld.so.preload -p wa -k persistence-ldpreload`. (6) ALL EXECVE by non-root interactive users: `-a always,exit -F arch=b64 -S execve -F auid>=1000 -k user-exec`. For detection, these audit keys feed into SIEM rules: alert when `persistence-*` key fires, correlate with the user's normal activity pattern (anomaly detection). The real power: auditd captures BEFORE the attacker can cover their tracks. Even if an attacker deletes bash_history, removes log files, etc., the kernel-level audit record has already been written (and forwarded to remote syslog if configured correctly).
