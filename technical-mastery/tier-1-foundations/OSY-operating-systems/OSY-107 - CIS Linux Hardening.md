---
id: OSY-107
title: CIS Linux Hardening
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-104, OSY-105, OSY-106
used_by: []
related: OSY-106, OSY-108, OSY-117
tags:
  - CIS
  - hardening
  - security
  - Linux
  - compliance
  - auditd
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 107
permalink: /technical-mastery/osy/cis-linux-hardening/
---

## TL;DR

CIS (Center for Internet Security) Linux Benchmarks provide
prioritized, consensus-based security configurations. Level 1:
server profile (practical, minimal impact). Level 2: high
security (may impact functionality). Key controls: filesystem
hardening, service minimization, network tuning, auditd
logging, user access controls, and kernel parameters. Essential
for SOC2, PCI-DSS, and HIPAA compliance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-107 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | CIS benchmark, Linux hardening, auditd, sysctl, compliance |
| **Prerequisites** | OSY-104, OSY-105, OSY-106 |

---

### CIS Benchmark Structure

```
CIS Benchmarks: downloadable from cisecurity.org
Latest: CIS Red Hat Enterprise Linux 9 Benchmark v2.0
        CIS Ubuntu 22.04 LTS Benchmark v1.0
        
Profile levels:
  Level 1 (Server):
    - Reasonable defaults; minimal impact to functionality
    - Applicable to most production servers
    - Required for most compliance frameworks
    
  Level 2 (Server - High Security):
    - More restrictive; may break some functionality
    - For high-value targets or sensitive environments
    - Test thoroughly before applying
    
Score system:
  Scored: automated check possible; contributes to compliance %
  Not Scored: manual verification; best practice
```

---

### Key Hardening Areas

**Filesystem Hardening**

```bash
# Separate partitions for /tmp, /var, /var/log, /home
# Prevents log overflow from filling /
# Prevents /tmp exploits affecting system partition

# Mount options for /tmp:
# nodev: prevent device files
# nosuid: prevent setuid binaries
# noexec: prevent executing programs in /tmp
# /etc/fstab:
# tmpfs /tmp tmpfs nodev,nosuid,noexec,size=2G 0 0

# Check /tmp mount options:
mount | grep /tmp
# Should show: nodev,nosuid,noexec

# Disable unused filesystems:
cat >> /etc/modprobe.d/cis-hardening.conf << 'EOF'
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install udf /bin/true
EOF
```

**Kernel Parameter Hardening (sysctl)**

```bash
# /etc/sysctl.d/99-cis-hardening.conf

# Disable IP forwarding (not a router)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Enable SYN cookies (SYN flood protection)
net.ipv4.tcp_syncookies = 1

# Disable ICMP redirect acceptance
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Log suspicious packets (martians)
net.ipv4.conf.all.log_martians = 1

# Randomize virtual addresses (ASLR)
kernel.randomize_va_space = 2

# Restrict dmesg to root only
kernel.dmesg_restrict = 1

# Restrict kernel pointer exposure
kernel.kptr_restrict = 2

# Disable Ctrl+Alt+Delete (physical security)
kernel.ctrl-alt-del = 0

# Apply immediately:
sysctl --system
```

**Service Minimization**

```bash
# List all running services:
systemctl list-units --type=service --state=running

# Disable unnecessary services:
systemctl disable --now avahi-daemon  # Zero-conf DNS (not needed in servers)
systemctl disable --now cups           # Printing (servers don't print)
systemctl disable --now bluetooth      # Bluetooth (servers don't use)
systemctl disable --now nfs-server     # NFS (unless needed)

# Remove unnecessary packages:
apt purge telnet ftp rsh-client rsh-redone-client
# These use plaintext passwords - never acceptable

# Check listening ports:
ss -tlnp
# Remove services for any unexpected open port
```

**User Access and Authentication**

```bash
# /etc/login.defs (password aging):
PASS_MAX_DAYS 90
PASS_MIN_DAYS 7
PASS_WARN_AGE 14

# Lock inactive accounts:
useradd -D -f 30  # Lock after 30 days inactive

# Require strong passwords (PAM):
# /etc/pam.d/common-password:
password required pam_pwquality.so \
  retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 \
  lcredit=-1 minclass=4

# Restrict su to wheel group:
# /etc/pam.d/su:
auth required pam_wheel.so use_uid

# Check for UID 0 accounts (should be only root):
awk -F: '($3 == 0) {print}' /etc/passwd
# Expected: only "root:x:0:0:..."

# Check for empty passwords:
awk -F: '($2 == "") {print}' /etc/shadow
# Expected: no output
```

---

### auditd: The Kernel Audit Daemon

```bash
# auditd: logs kernel-level security events
# Install: apt install auditd

# Start and enable:
systemctl enable --now auditd

# Key audit rules (/etc/audit/rules.d/99-cis.rules):

# Log privilege escalation:
-w /bin/su -p x -k priv_esc
-w /usr/bin/sudo -p x -k priv_esc

# Log setuid binary execution:
-a always,exit -F arch=b64 -S execve \
  -F euid=0 -F auid>=1000 -F auid!=-1 -k root_exec

# Log passwd/shadow modification:
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/gshadow -p wa -k identity

# Log SSH config changes:
-w /etc/ssh/sshd_config -p wa -k sshd

# Log cron changes:
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron

# Log module loading (prevent unauthorized kernel modules):
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-a always,exit -F arch=b64 -S init_module -k modules

# Query audit logs:
ausearch -k priv_esc -ts recent   # Recent privilege escalations
ausearch -k identity -ts today    # Today's identity changes
aureport --login                  # Login report
```

---

### Automated CIS Compliance Checking

```bash
# OpenSCAP: automated CIS compliance checker
# Install:
apt install libopenscap8 ssg-debderived

# Run CIS Level 1 assessment:
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
  --results /tmp/cis-report.xml \
  --report /tmp/cis-report.html \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2204-ds.xml

# View report: open /tmp/cis-report.html in browser
# Shows: pass/fail per control with remediation commands

# Ansible CIS role (automated remediation):
# Galaxy: dev-sec.os-hardening
ansible-galaxy install dev-sec.os-hardening
# Apply: ansible-playbook -i hosts playbook.yml
# Role: applies most CIS controls automatically

# Lynis: security auditing tool
lynis audit system
# Generates: hardening index score; recommendations
# Not CIS-specific but covers same controls
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CIS Level 2 is always better than Level 1" | Level 2 controls can break legitimate functionality. Examples: disabling audit namespace mount, restricting ptrace (breaks Java profilers, strace), strict umask settings. For most production systems: CIS Level 1 provides excellent security. Apply Level 2 controls individually after testing. |
| "Applying CIS hardening once is sufficient" | CIS hardening drifts over time: packages update, configs are modified, new services are added. Continuous compliance: run OpenSCAP or similar weekly. Immutable infrastructure: rebuild containers/VMs from hardened base image on each deploy. |
| "Hardening only matters for internet-facing servers" | Internal servers are prime targets for lateral movement after initial compromise. Most breaches: start with one compromised host, spread internally. All servers should meet CIS Level 1 minimum, especially internal API servers and databases. |

---

### Quick Reference Card

| Control Area | Key File | Verification |
|--------------|----------|--------------|
| ASLR | `/proc/sys/kernel/randomize_va_space` | Must be 2 |
| Kernel pointers | sysctl `kptr_restrict` | Must be 2 |
| /tmp permissions | /etc/fstab | nodev,nosuid,noexec |
| Password aging | /etc/login.defs | PASS_MAX_DAYS 90 |
| Auditd | /etc/audit/rules.d/ | active + rules |
| UID 0 accounts | /etc/passwd | Only root |
| Listening services | `ss -tlnp` | Only needed ones |
| CIS auto-check | OpenSCAP | `oscap xccdf eval` |
