---
id: OSY-117
title: Compliance Checklist
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-107, OSY-108, OSY-116
used_by: []
related: OSY-107, OSY-118, OSY-119
tags:
  - compliance
  - checklist
  - CIS
  - hardening
  - SOC2
  - PCI-DSS
  - audit
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 117
permalink: /technical-mastery/osy/compliance-checklist/
---

## TL;DR

OS compliance checklist for common frameworks: CIS Benchmarks,
SOC 2, PCI-DSS, and HIPAA. Covers the intersection of OS
hardening (kernel parameters, file permissions, audit
logging) and compliance requirements. Not a substitute for
full audit - a starting point for Java service OS compliance.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-117 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | compliance, CIS benchmark, SOC2, PCI-DSS, OS hardening, audit |
| **Prerequisites** | OSY-107, OSY-108, OSY-116 |

---

### Compliance Framework Overview

```
CIS Benchmarks (Center for Internet Security):
  Technical prescriptive controls for specific OSes
  Level 1: basic hardening; no significant impact
  Level 2: defense-in-depth; may impact functionality
  Covers: filesystem, services, kernel parameters,
          authentication, audit logging
  Tooling: CIS-CAT scanner; OpenSCAP

SOC 2 (Service Organization Control):
  Control framework for service organizations
  Trust Service Criteria: Security, Availability, Privacy,
    Confidentiality, Processing Integrity
  OS-relevant: access controls, encryption, monitoring,
               incident response
  Not prescriptive on specific settings; auditor-interpreted

PCI-DSS (Payment Card Industry Data Security Standard):
  Requirements for handling cardholder data
  OS-relevant: v3.2.1 / v4.0 requirements:
    Req 2: vendor default passwords changed
    Req 6: secure systems and software
    Req 7: access control to system components
    Req 8: identity and authentication
    Req 10: logging and monitoring
    Req 11: security testing

HIPAA (Health Insurance Portability):
  US healthcare data protection
  Technical Safeguards: access control, audit controls,
    integrity controls, transmission security
  OS: encryption at rest, audit logging, user access control
```

---

### CIS Level 1 - Most Common Controls

```bash
# 1. Filesystem Controls

# Check world-writable directories:
find / -xdev -type d -perm -0002 2>/dev/null
# Should be empty (except /tmp, /var/tmp with sticky bit)
# Fix: chmod o-w /path/to/directory

# Verify sticky bit on /tmp:
stat /tmp | grep 'Access: ('
# Should show: (1777/drwxrwxrwt)
chmod 1777 /tmp
chmod 1777 /var/tmp

# No unowned files:
find / -xdev -nouser 2>/dev/null
find / -xdev -nogroup 2>/dev/null
# Fix: assign proper ownership or remove

# SUID/SGID files (only known binaries should have these):
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null
# Review each; remove SUID from unnecessary binaries:
chmod u-s /usr/bin/somebinary

# 2. SSH Hardening (CIS Section 5.2)

# /etc/ssh/sshd_config required settings:
grep -E '^(Protocol|PermitRootLogin|PasswordAuthentication|X11Forwarding|MaxAuthTries|IgnoreRhosts|HostbasedAuthentication|PermitEmptyPasswords|PermitUserEnvironment|LoginGraceTime|Banner)' /etc/ssh/sshd_config

# Required values:
# Protocol 2
# PermitRootLogin no
# PasswordAuthentication no (keys only)
# X11Forwarding no
# MaxAuthTries 4
# IgnoreRhosts yes
# HostbasedAuthentication no
# PermitEmptyPasswords no
# Banner /etc/issue.net (legal notice)

# 3. Password and Authentication

# /etc/login.defs:
grep PASS_MAX_DAYS /etc/login.defs  # should be <= 365
grep PASS_MIN_DAYS /etc/login.defs  # should be >= 1
grep PASS_WARN_AGE /etc/login.defs  # should be >= 7

# PAM password complexity:
grep -E 'pam_pwquality|pam_cracklib' /etc/pam.d/system-auth
# Should enforce: minlen=14, minclass=4

# 4. Kernel Parameters (CIS Section 3.x)

# IP forwarding (disable unless this is a router):
sysctl net.ipv4.ip_forward      # should be 0
sysctl net.ipv6.conf.all.forwarding  # should be 0

# ICMP redirects:
sysctl net.ipv4.conf.all.accept_redirects   # should be 0
sysctl net.ipv4.conf.all.send_redirects     # should be 0

# SYN flood protection:
sysctl net.ipv4.tcp_syncookies   # should be 1

# Source route validation (reverse path filtering):
sysctl net.ipv4.conf.all.rp_filter  # should be 1
```

---

### Audit Logging (SOC 2 + PCI-DSS Requirement 10)

```bash
# Install and configure auditd:
systemctl status auditd
systemctl enable auditd

# /etc/audit/rules.d/audit.rules
# Required by PCI-DSS Req 10.2:

# All login/logout attempts:
-w /var/log/lastlog -p wa -k logins
-w /var/run/faillock/ -p wa -k logins

# Modifications to authentication config:
-w /etc/group -p wa -k identity
-w /etc/passwd -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k identity

# All privileged command execution:
-a always,exit -F path=/usr/bin/sudo -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged

# File deletion:
-a always,exit -F arch=b64 -S unlink -S unlinkat -S rename -S renameat -F auid>=1000 -F auid!=4294967295 -k delete

# Network configuration changes:
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system-locale
-w /etc/issue -p wa -k system-locale
-w /etc/hosts -p wa -k system-locale
-w /etc/network -p wa -k system-locale

# System access controls:
-w /etc/hosts.deny -p wa -k host-access
-w /etc/hosts.allow -p wa -k host-access

# Log all root activity:
-a always,exit -F arch=b64 -F uid=0 -S execve -k root_command

# Reload audit rules:
augenrules --load
```

---

### Container Compliance Controls

```bash
# Docker/container-specific compliance:

# Ensure containers run as non-root:
docker inspect $CONTAINER | grep '"User"'
# Should show a non-root user (not "")

# No privileged containers:
docker inspect $CONTAINER | grep '"Privileged"'
# Should be false

# Read-only filesystem:
docker inspect $CONTAINER | grep '"ReadonlyRootfs"'
# Should be true (or verify app-level writable volumes only)

# No host network:
docker inspect $CONTAINER | grep '"NetworkMode"'
# Should NOT be "host"

# AppArmor profile assigned:
docker inspect $CONTAINER | grep '"AppArmorProfile"'
# Should show a profile name, not ""

# Docker daemon configuration (/etc/docker/daemon.json):
{
  "no-new-privileges": true,
  "userns-remap": "default",
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}

# Kubernetes pod security (PCI-DSS relevant):
# Use Pod Security Admission (PSA) policy:
# namespace label: pod-security.kubernetes.io/enforce=restricted
```

---

### Java-Specific Compliance Controls

```
Encryption at rest (HIPAA / PCI-DSS Req 3):
  OS-level: Linux dm-crypt / LUKS for volumes
  Java: javax.crypto for application-level encryption
  Key management: HashiCorp Vault or AWS KMS
  
  Check if disk is encrypted:
    lsblk -o NAME,TYPE,FSTYPE
    cryptsetup status /dev/mapper/cryptdisk
    
Encryption in transit (PCI-DSS Req 4):
  TLS 1.2+ for all Java service communications
  Disable TLS 1.0/1.1 in JVM:
    -Djdk.tls.disabledAlgorithms=TLSv1,TLSv1.1,RC4,DES,MD5withRSA

Log retention (SOC 2 / PCI-DSS Req 10.7):
  PCI-DSS: retain audit logs for 12 months; 3 months online
  Java app logs + OS audit logs: ship to SIEM
  logrotate configuration: keep 90 days of audit logs
  
Patching (PCI-DSS Req 6.3):
  Install security patches within 1 month
  Critical patches: within defined SLA (30 days typically)
  Automate: unattended-upgrades (Ubuntu) or yum-cron (RHEL)
  Document: CVE tracking system (Jira / ServiceNow)
  
Access control (SOC 2 CC6.1):
  Principle of least privilege for OS users
  Java service user: no login shell, no sudo, no home dir write
  useradd -r -s /sbin/nologin -M myapp
  Service files owned by root, readable by myapp user
```

---

### Compliance Gap Assessment Template

```
Framework: PCI-DSS v4.0
Scope: Java payment processing service on Linux

Requirement | Status | Finding | Remediation
---------|--------|---------|--------
2.2: Vendor defaults changed | PASS | SSH root disabled, default ports changed | None
6.3: Security patches | PARTIAL | Last patched 45 days ago | Schedule monthly patch window
7.2: Access control | PASS | Non-root user; no sudo | None
8.3: Authentication | FAIL | Password auth enabled on 2 hosts | Disable PasswordAuthentication in sshd_config
10.2: Audit logging | PASS | auditd configured per CIS | None
10.5: Log integrity | FAIL | Logs stored locally only | Ship to immutable SIEM
```

---

### Quick Reference Card

| Framework | Key OS Control | Tool to Verify |
|-----------|----------------|----------------|
| CIS Level 1 | Kernel params, SSH config, filesystem perms | CIS-CAT, OpenSCAP |
| SOC 2 | Audit logging, access control | auditd, PAM |
| PCI-DSS | Encryption, patching, log retention | SIEM, CVE tracker |
| HIPAA | Encryption at rest + transit, access logs | dm-crypt, TLS audit |
