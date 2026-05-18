---
id: LNX-100
title: "Linux Hardening at Scale (CIS Benchmarks, STIG)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-057, LNX-097, LNX-099
used_by: LNX-108
related: LNX-057, LNX-097, LNX-099, LNX-108
tags: [linux-hardening, cis-benchmarks, stig, cis-cat, openscap, oscap, auditd-hardening, pam-hardening, ssh-hardening, sysctl-hardening, noexec-nosuid, aide, selinux, apparmor, ansible-lockdown, cis-ansible, dod-stig, compliance-automation, cis-level-1, cis-level-2, nist-800-53, fips-140, security-baseline, kernel-hardening, services-hardening]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 100
permalink: /technical-mastery/lnx/linux-hardening-cis-stig/
---

## TL;DR

Linux hardening transforms a default installation (optimized for ease-of-use)
into a secure configuration (optimized for attack resistance). Two major
standards: **CIS Benchmarks** (Center for Internet Security, industry standard,
two levels: L1=essential, L2=defense-in-depth) and **STIG** (Security Technical
Implementation Guide, US DoD standard). Six hardening areas: (1) **Filesystem**:
separate /tmp with `noexec,nosuid,nodev`; (2) **Services**: disable unneeded
(cups, avahi, rpcbind); (3) **SSH**: `PermitRootLogin no`, `PasswordAuthentication no`,
`MaxAuthTries 4`; (4) **PAM**: password complexity, account lockout; (5) **Audit**:
auditd rules for privilege escalation and sensitive file access; (6) **Kernel
sysctl**: `net.ipv4.conf.all.rp_filter=1`, `kernel.dmesg_restrict=1`.
Automation: **OpenSCAP** (`oscap xccdf eval`) for assessment and remediation,
**ansible-lockdown** roles for Ansible deployment.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-100 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | hardening, CIS Benchmarks, STIG, OpenSCAP, ansible-lockdown, compliance, sysctl, PAM, auditd |
| **Prerequisites** | LNX-057 (security), LNX-097 (security incidents), LNX-099 (fleet management) |

---

### The Problem This Solves

**Problem 1**: Default RHEL installation includes: rpcbind running (NFSv3
RPC service), cups running (print spooler), avahi-daemon running (mDNS
discovery), IPv6 stack active (often unused in enterprise), default sysctl
settings that don't restrict kernel info leaks. Each running service is an
attack surface: a vulnerability in cups on a server that never prints is an
avoidable risk. Hardening eliminates the attack surface by removing what isn't
needed.

**Problem 2**: An organization must pass a PCI-DSS audit or achieve FedRAMP
authorization. Auditors don't evaluate security intuitively - they check
specific technical controls from a published standard (CIS Level 2 or STIG).
Without a systematic hardening framework: the organization builds a custom
checklist, misses items, fails the audit. With CIS Benchmarks as the baseline:
the audit checklist IS the benchmark, and automated tools (OpenSCAP) verify
compliance in minutes.

---

### Textbook Definition

**CIS Benchmarks**: Configuration guides published by the Center for Internet
Security (cisecurity.org). Cover major operating systems, cloud platforms,
containers, databases. Two levels:
- Level 1: "Essential" - applicable to most environments, minimal performance impact
- Level 2: "Defense in depth" - high security environments, may impact usability

**STIG (Security Technical Implementation Guide)**: US Department of Defense
security configuration standards. Published by DISA (Defense Information
Systems Agency). Required for DoD systems, widely adopted in government and
defense contractors. Stricter than CIS Level 2 in many areas. Findings are
categorized by severity: CAT I (critical), CAT II (medium), CAT III (low).

**OpenSCAP**: Open-source implementation of the SCAP (Security Content
Automation Protocol) standard. `oscap` command-line tool for scanning and
remediating systems against CIS/STIG profiles.

---

### Understand It in 30 Seconds

```bash
# === Assessment: measure current compliance ===

# OpenSCAP (SCAP Workbench or command line):
# Install:
yum install -y openscap-scanner scap-security-guide

# Available profiles (CIS, STIG, etc.):
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml | \
    grep -A2 "Id:"
# Id: xccdf_org.ssgproject.content_profile_cis_server_l1
#   Title: CIS Red Hat Enterprise Linux 8 Benchmark for Level 1
# Id: xccdf_org.ssgproject.content_profile_stig
#   Title: DISA STIG for Red Hat Enterprise Linux 8

# Run CIS Level 1 assessment:
oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
    --results /tmp/scan-results.xml \
    --report /tmp/scan-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml

# View report: open /tmp/scan-report.html
# Summary: "Pass: 142, Fail: 38" -> shows exactly what needs fixing

# Run AND generate remediation Ansible playbook:
oscap xccdf generate fix \
    --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
    --fix-type ansible \
    /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml \
    > /tmp/rhel8-cis-remediation.yml

# Run the generated playbook:
ansible-playbook /tmp/rhel8-cis-remediation.yml --check  # dry-run first!

# === Manual: Key hardening controls ===

# 1. Filesystem: /tmp with noexec, nosuid, nodev
systemctl enable tmp.mount
grep tmp /etc/fstab
# tmpfs  /tmp  tmpfs  defaults,nodev,nosuid,noexec,size=2G  0  0
# noexec: cannot execute binaries in /tmp (stops malware in /tmp)
# nosuid: SUID bits ignored (stops SUID escalation from /tmp)
# nodev: no device files (prevents device-based attacks)

# 2. Disable unneeded services:
systemctl disable --now cups      # printing (rarely needed on servers)
systemctl disable --now avahi-daemon  # mDNS/Bonjour discovery
systemctl disable --now rpcbind   # NFS RPC mapper (if NFS not used)
systemctl disable --now bluetooth # Bluetooth (never on servers)
systemctl disable --now postfix   # mail (if not a mail server)

# 3. SSH hardening (/etc/ssh/sshd_config):
cat >> /etc/ssh/sshd_config << 'EOF'
Protocol 2
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 4
MaxSessions 10
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PrintLastLog yes
Banner /etc/issue.net
ClientAliveInterval 300
ClientAliveCountMax 0
LoginGraceTime 60
EOF
sshd -t && systemctl reload sshd  # validate before applying!

# 4. Kernel sysctl hardening (/etc/sysctl.d/99-hardening.conf):
cat > /etc/sysctl.d/99-hardening.conf << 'EOF'
# Restrict dmesg to root only
kernel.dmesg_restrict = 1
# Hide kernel pointers in /proc
kernel.kptr_restrict = 2
# Disable core dumps with SUID
fs.suid_dumpable = 0
# Enable reverse path filtering (anti-spoofing)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
# Disable IP forwarding (not a router)
net.ipv4.ip_forward = 0
# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
# Log martians (packets with impossible source addresses)
net.ipv4.conf.all.log_martians = 1
# TCP SYN flood protection
net.ipv4.tcp_syncookies = 1
# Randomize virtual memory layout (ASLR)
kernel.randomize_va_space = 2
EOF
sysctl -p /etc/sysctl.d/99-hardening.conf

# 5. PAM lockout policy (/etc/pam.d/system-auth):
# pam_faillock: lock account after N failed attempts
# Install: yum install -y pam
authconfig --enablefaillock \
    --faillockargs="deny=5 unlock_time=900" --update
# deny=5: lock after 5 failures
# unlock_time=900: unlock after 15 minutes

# 6. Auditd rules (/etc/audit/rules.d/hardening.rules):
cat > /etc/audit/rules.d/hardening.rules << 'EOF'
# Delete existing rules
-D
# Buffer size
-b 8192
# Failure mode: 1=printk, 2=panic
-f 1

# Monitor all actions by root
-a always,exit -F arch=b64 -F uid=0 \
    -S execve -k root-actions

# Monitor privilege escalation
-a always,exit -F arch=b64 -S setuid -S setgid \
    -S setreuid -S setregid -k privilege-escalation

# Monitor sensitive file access
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

# Monitor SSH authorized_keys
-w /root/.ssh -p wa -k ssh-keys
-w /home -p wa -k home-dir-changes

# Monitor cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# Immutable (audit rules cannot be changed until reboot)
-e 2
EOF
augenrules --load

# Verify:
auditctl -l | head -20
```

---

### First Principles

```
Why default OS installations are not secure:

OS vendors face opposing constraints:
  1. "Easy to use" - defaults that work for most users out-of-the-box
  2. "Secure" - defaults that minimize attack surface
  
These two goals are often in tension:
  "Easy": enable cups (printing) by default (useful for desktops)
  "Secure": disable cups (rarely needed on servers, attack surface)
  
  "Easy": sysctl defaults that don't restrict information leakage
           (dmesg is readable by all users - useful for debugging)
  "Secure": kernel.dmesg_restrict=1 (kernel info hidden from non-root)
  
  "Easy": PasswordAuthentication yes in sshd (just type your password)
  "Secure": PasswordAuthentication no (only SSH key auth, no brute force)

Result: every freshly installed Linux server has dozens of "easy"
settings that are "insecure" for a production server environment.

Hardening = systematically choosing "secure" over "easy" for servers.

CIS Benchmarks methodology:
  1. Community consensus: security experts + vendors agree on controls
  2. Rationale for every control: "why" is documented
  3. Impact documented: "this may break X, consider before applying"
  4. Two levels:
     Level 1 (essential, broadly applicable):
       - Disable bluetooth, cups, avahi on servers (never needed)
       - PasswordAuthentication no for SSH (only key-based)
       - noexec on /tmp (malware cannot execute from /tmp)
       Impact: minimal for server workloads
       
     Level 2 (high security, consider impact):
       - Disable USB storage (strict: blocks physical media)
       - Enable SELinux enforcing (strict: may break applications)
       - Disable core dumps (may impact debugging)
       Impact: may require application changes

STIG methodology:
  DoD-specific, stricter in some areas, more lenient in others
  CAT I: immediate, significant risk if not implemented
           (example: PermitRootLogin yes, no password for root)
  CAT II: medium risk (example: missing audit rules)
  CAT III: low risk (example: banner not configured)
  FIPS 140-2 mode: cryptographic algorithm restrictions
  (MD5 disabled, TLS 1.0/1.1 disabled, only FIPS-approved ciphers)

Defense in depth principle:
  No single control prevents all attacks.
  Each control raises the cost for an attacker.
  
  Example: attacker with SSH credential for non-root user wants to:
  1. Run malware: blocked by noexec on /tmp
  2. Escalate to root via kernel exploit: caught by auditd EXECVE rules
  3. Persist via cron: caught by auditd cron monitoring
  4. Exfiltrate data: AllowTcpForwarding no blocks SSH tunnels
  5. Hide via SUID binary: noexec prevents executing SUID in /tmp
  
  One control fails? Others still limit impact.

Compliance automation math:
  200 servers * 250 CIS controls = 50,000 checks
  Manual: 1 minute per check = 50,000 minutes = 833 hours = 20 weeks
  OpenSCAP: 2 minutes per server = 400 minutes = 6.7 hours for 200 servers
             (better: 1 Ansible Tower job runs all 200 in parallel = 20 min)
  
  Automation is not just convenient: it's the only way compliance is
  achievable at scale.
```

---

### Thought Experiment

CIS Level 1 hardening for a production RHEL 8 fleet using Ansible:

```bash
# === Step 1: Assessment of current state ===

# Scan a representative server:
oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
    --results /tmp/before-scan.xml \
    --report /tmp/before-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml

# Count failures:
grep 'result>fail' /tmp/before-scan.xml | wc -l
# 42 failures on fresh RHEL 8 install (expected)

# === Step 2: Apply hardening with ansible-lockdown ===
# ansible-lockdown: community Ansible roles for CIS/STIG

# Download role:
ansible-galaxy install MindPointGroup.RHEL8-CIS

# Playbook:
cat cis-hardening.yml << 'EOF'
---
- name: CIS RHEL8 Level 1 Hardening
  hosts: all
  become: yes
  vars:
    rhel8cis_level1_tasks: yes
    rhel8cis_level2_tasks: no  # Level 2 separately after testing
    
    # Override for our environment:
    rhel8cis_set_boot_pass: no  # skip GRUB password (cloud VMs)
    rhel8cis_ssh_allowusers: "deployer ansible-svc"  # only these users
    
    # NTP server:
    rhel8cis_ntp_server_name: 169.254.169.123  # AWS time sync

  roles:
    - MindPointGroup.RHEL8-CIS
EOF

# Test on one server first:
ansible-playbook cis-hardening.yml \
    --limit staging-server01.example.com \
    --check  # dry-run

# Verify staging server still works after applying:
ansible-playbook cis-hardening.yml \
    --limit staging-server01.example.com
# Run your application test suite against staging-server01!

# Scan after hardening:
oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
    --results /tmp/after-scan.xml \
    --report /tmp/after-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml

grep 'result>fail' /tmp/after-scan.xml | wc -l
# 3 failures (42 -> 3 after hardening; 3 are known exceptions)

# === Step 3: Document exceptions ===
# Document remaining failures as accepted risks or environment-specific:
# Failure: "ensure filesystem integrity is regularly checked" (AIDE)
#   -> Exception: we use AWS Inspector for file integrity (equivalent)
# Failure: "ensure GRUB bootloader password set"
#   -> Exception: cloud VMs use console access control (no physical GRUB)

# === Step 4: Rolling apply to production ===
ansible-playbook cis-hardening.yml \
    --serial 5% \                    # 5 servers at a time
    --max-fail-percentage 5          # stop if >5% fail

# === Step 5: Continuous compliance in CI/CD ===
# .gitlab-ci.yml or GitHub Actions:
# compliance-check job:
#   script:
#     - oscap xccdf eval --profile cis_l1 --results results.xml content.xml
#     - python3 check_results.py results.xml --fail-on-new  # fail if new failures
```

---

### Mental Model / Analogy

```
Hardening = building security (physical security design)

Default OS = newly built office building:
  All interior doors unlocked (services running)
  Front door opens to anyone (no authentication controls)
  No security cameras (no audit logging)
  Any employee has master key access (no privilege restriction)
  Basement unlocked (kernel info accessible to all)
  
CIS Level 1 hardening = basic building security:
  Lock unnecessary rooms (disable unused services)
  Front door requires keycard (SSH key authentication only)
  Install cameras at reception and server room (auditd basics)
  Limit who has master keys (no root login, limited sudo)
  Lock basement (kernel.dmesg_restrict, kptr_restrict)
  Emergency exits only (no X11 forwarding, no TCP forwarding)
  
CIS Level 2 hardening = bank-level security:
  All rooms require keycards (SELinux enforcing)
  No USB drives allowed (disable USB storage)
  All phone calls recorded (full syscall audit logging)
  Separate vaults (separate filesystem partitions, noexec everywhere)
  No way to disable cameras (auditd immutable rules: -e 2)
  
STIG = military base security:
  Full background check for entry (FIPS-approved crypto only)
  Two-person integrity for sensitive areas (specific access controls)
  SIGINT monitoring (comprehensive network monitoring)
  Strict uniform requirements (specific kernel parameter values)
  
Each control = closing a specific attack path:
  noexec on /tmp = "no weapons allowed past the security checkpoint"
  AllowTcpForwarding no = "no luggage smuggling through the fire exit"
  auditd = "every door opening is logged with who and when"
  MaxAuthTries 4 = "security guard stops you after 4 wrong codes"
  
Compliance framework (CIS/STIG) = building code:
  Not invented by your security team
  Developed by experts from many organizations
  Published, versioned, widely accepted by auditors
  Saves 90% of the "what should we lock?" decision-making work
  
OpenSCAP = fire inspector's checklist:
  Systematic, standardized, automated
  Produces a report: "42 items fail inspection"
  Same report format regardless of which inspector runs it
  Reproducible: run today and tomorrow, same results
```

---

### Gradual Depth - Five Levels

**Level 1:**
Why hardening matters: default installations are not production-secure. CIS
Benchmarks concept: industry standard checklist. Six key areas: filesystem,
services, SSH, PAM, auditing, kernel. Most important quick wins: disable cups/avahi,
disable PasswordAuthentication, set noexec on /tmp. OpenSCAP for assessment.

**Level 2:**
CIS Level 1 vs Level 2 differences. STIG overview and severity categories.
Sysctl parameters: rp_filter, dmesg_restrict, randomize_va_space. SSH hardening
configuration options. auditd rules: key categories (identity, privilege-escalation,
cron). PAM pam_faillock for account lockout. `oscap xccdf eval` command. AIDE
for file integrity.

**Level 3:**
ansible-lockdown roles for automated CIS/STIG application. OpenSCAP remediation
plan generation (`oscap generate fix --fix-type ansible`). FIPS 140-2 mode:
what it restricts (MD5 disabled, TLS 1.0/1.1 disabled, algorithm list). SELinux
in enforcing mode: targeted vs MLS policies, audit2allow for exceptions.
Exception management: documenting accepted risks vs compensating controls.
Compliance drift: re-running scans periodically.

**Level 4:**
Enterprise compliance automation: SCAP/OpenSCAP integrated into CI/CD pipelines,
fail build if new compliance failures introduced. Compliance as code: storing
XCCDF tailoring files in git, tracking exceptions in version control.
InSpec profiles for custom controls beyond CIS/STIG. Regulatory mapping:
CIS controls mapped to NIST 800-53, PCI-DSS, HIPAA requirements. FedRAMP
High requirements: additional controls beyond STIG. CIS-CAT Pro Assessor for
multi-host scanning with dashboard.

**Level 5:**
Defense in depth analysis: which controls address which attack techniques (MITRE
ATT&CK mapping to CIS controls). Custom STIG tailoring: XCCDF tailoring files
to create organization-specific profiles. Hardening at AMI/image level (packer
+ ansible-lockdown): baking compliance into golden image vs in-place application.
Continuous compliance monitoring: AWS Security Hub + Inspector, Azure Defender,
GCP Security Command Center - cloud-native compliance scoring. Zero-trust
implications: hardening assumes breach, focuses on limiting blast radius.
Container hardening (CIS Docker Benchmark, CIS Kubernetes Benchmark).

---

### Code Example

**BAD - ad-hoc hardening without systematic approach:**
```bash
# BAD: Hardening commands run manually without documentation or testing

# Manual, ad-hoc, not tracked in version control:
ssh server01.example.com
sudo su -
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd  # No validation! If sshd.conf is malformed: locked out!
echo "net.ipv4.ip_forward=0" >> /etc/sysctl.conf  # Note: wrong file for RHEL 8
sysctl -p

# Problems:
# 1. No validation of sshd_config before restart: risk of lockout
# 2. Changes not documented: team doesn't know what was changed
# 3. Not idempotent: run again, duplicate entries in sshd_config
# 4. Not tested: may break application functionality
# 5. Not applied to other servers: drift between servers
# 6. No audit trail: who hardened this server and when?
# 7. Wrong file: should be /etc/sysctl.d/99-*.conf not /etc/sysctl.conf

# BAD: sshd_config with conflicting/insecure settings:
PermitRootLogin yes    # Allows root login (security risk)
PasswordAuthentication yes  # Allows password brute force
X11Forwarding yes      # X11 forwarding (unnecessary for servers)
AllowTcpForwarding yes  # TCP tunneling (attacker can use for pivoting)
UseDNS yes             # DNS lookups slow down login
```

```bash
# GOOD: systematic Ansible-based hardening with validation

# roles/ssh-hardening/tasks/main.yml:
---
- name: "SSH: Set PermitRootLogin to no"
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PermitRootLogin'
    line: 'PermitRootLogin no'
    state: present
    validate: '/usr/sbin/sshd -t -f %s'  # validate before writing!
  notify: Restart sshd

- name: "SSH: Disable password authentication"
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PasswordAuthentication'
    line: 'PasswordAuthentication no'
    validate: '/usr/sbin/sshd -t -f %s'
  notify: Restart sshd

- name: "SSH: Set MaxAuthTries to 4"
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?MaxAuthTries'
    line: 'MaxAuthTries 4'
    validate: '/usr/sbin/sshd -t -f %s'
  notify: Restart sshd

- name: "SSH: Disable X11 forwarding"
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?X11Forwarding'
    line: 'X11Forwarding no'
    validate: '/usr/sbin/sshd -t -f %s'
  notify: Restart sshd

# roles/ssh-hardening/handlers/main.yml:
- name: Restart sshd
  systemd:
    name: sshd
    state: restarted
  # Handler only fires IF any task notified it
  # AND only runs ONCE even if multiple tasks notify it

# roles/sysctl-hardening/tasks/main.yml:
- name: Apply kernel hardening parameters
  sysctl:
    name: "{{ item.name }}"
    value: "{{ item.value }}"
    sysctl_file: /etc/sysctl.d/99-cis-hardening.conf
    state: present
    reload: yes
  loop:
    - { name: 'kernel.dmesg_restrict', value: '1' }
    - { name: 'kernel.kptr_restrict', value: '2' }
    - { name: 'fs.suid_dumpable', value: '0' }
    - { name: 'net.ipv4.conf.all.rp_filter', value: '1' }
    - { name: 'net.ipv4.ip_forward', value: '0' }
    - { name: 'net.ipv4.tcp_syncookies', value: '1' }
    - { name: 'kernel.randomize_va_space', value: '2' }
  # Idempotent: sysctl module only writes if value differs
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "CIS Level 2 is for military/government - regular companies should use Level 1" | CIS Benchmark levels are not about industry sector. Level 1 and Level 2 reflect trade-offs between security and operational impact. Many commercial companies in finance, healthcare, and technology run CIS Level 2 because the operational impact is acceptable (server workloads are not interactive desktops, so controls like "disable USB storage" don't affect operations). The decision should be based on: (a) What regulatory/compliance framework requires (PCI-DSS specifies minimum controls, some of which are Level 2), (b) What your threat model demands (internet-facing high-value servers warrant Level 2), (c) What operational impact you can manage (SELinux enforcing in Level 2 requires application-level exceptions). Start with Level 1, assess operational impact, then evaluate Level 2 controls individually rather than treating them as an all-or-nothing package. |
| "Hardening means enabling SELinux enforcing mode" | SELinux is ONE control in a comprehensive hardening standard, and not even a Level 1 requirement in all CIS benchmarks for all distributions. Comprehensive hardening includes: disabling unneeded services (reduces attack surface), SSH configuration hardening (prevents brute force, disables weak authentication), sysctl kernel parameters (prevents information leakage, enables anti-spoofing), auditd rules (detects and logs security events), PAM configuration (account lockout), filesystem mount options (noexec prevents malware execution). Any one of these may have more immediate security impact than SELinux depending on your threat model. Organizations that "turn on SELinux and call it hardened" while leaving PasswordAuthentication enabled and cups running have the wrong mental model. |
| "Running a CIS scan that shows 95% pass means the system is 95% secure" | CIS scan score is a compliance measure, not a security measure. Compliance != security. (1) Weight: some failing controls are trivial (banner not set) while some passing controls provide major security value. Averaging them is misleading. (2) Scope: CIS covers configuration, not vulnerabilities. A 100% CIS-compliant system with unpatched kernel vulnerabilities is not "secure." (3) Context: some CIS controls are not relevant to your environment (USB storage control on a cloud VM has no meaning). (4) Missing attacks: CIS doesn't cover application security, secrets management, network security, identity management - all critical to security. Use CIS compliance as a baseline measurement tool, not as a security guarantee. Pair with: vulnerability scanning (OpenVAS, Qualys, Tenable), threat modeling, penetration testing. |
| "Hardening can be done once and maintained" | Hardening must be continuously maintained and re-applied. Reasons it degrades over time: (1) Software updates: a package update may restore a default configuration file (e.g., /etc/sshd_config reset to default by update); (2) Application requirements: developers need a new configuration that conflicts with hardening; (3) Configuration drift (LNX-099): manual changes accumulate; (4) New CVEs require new controls not in original hardening; (5) New CIS Benchmark versions: standards evolve, v2.0 may have different controls than v1.0. Solution: periodic re-scanning (`oscap xccdf eval` as cron job, alert on new failures), Ansible playbook re-application on a schedule, integrate scanning into AMI build pipeline (new base images must pass CIS scan before approval). |

---

### Failure Modes & Diagnosis

```bash
# === Failure: SSH sshd_config syntax error causes lockout ===
# Added hardening config with a typo -> sshd fails to restart

# PREVENTION: always validate before restarting:
sshd -t  # test configuration syntax
# /etc/ssh/sshd_config line 45: Bad configuration option: AllowTCPForwarding
# ^ Typo: should be AllowTcpForwarding (case-sensitive!)

# Fix the typo:
sed -i 's/AllowTCPForwarding/AllowTcpForwarding/' /etc/ssh/sshd_config
sshd -t && systemctl reload sshd  # reload (not restart): less risky

# If already locked out (use AWS SSM Session Manager, GCP Cloud Shell,
# Azure Serial Console, or physical/KVM console to access):
# From console:
sshd -t -f /etc/ssh/sshd_config
# Fix the error, then: systemctl start sshd

# === Failure: noexec on /tmp breaks application ===
# Application fails after /tmp noexec applied

# Symptom: Java application fails to start:
# Error: cannot execute /tmp/hsperfdata_javauser/12345
# ^ JVM writes performance data files to /tmp - noexec blocks execution

# Diagnosis:
# Check what the application is doing in /tmp:
strace -p $(pgrep java) -e trace=execve 2>&1 | grep /tmp
# execve("/tmp/jna-12345/jna.so", ...) -> EACCES (noexec!)
# ^ JNA (Java Native Access) extracts native libraries to /tmp

# Fix options:
# Option A: Configure JVM to use noexec-excluded directory:
java -Djava.io.tmpdir=/var/tmp/java-noexec MyApp
# /var/tmp with noexec but on separate partition

# Option B: Separate mount for /var/tmp with exec (exception):
mount -o remount,exec /var/tmp
# In /etc/fstab: /var/tmp with exec (document the exception)

# Option C: Configure JNA to use a different directory:
java -Djna.tmpdir=/opt/app/tmp MyApp  # app-specific tmp dir

# === Failure: auditd fills disk with audit logs ===
# /var/log/audit/ grows unboundedly

# Check disk usage:
df -h /var/log/audit
# /dev/sda4  10G  9.8G  200M  98%  /var/log/audit  <- nearly full!

du -sh /var/log/audit/*
# 9.8G  audit.log  (not rotating!)

# Check auditd rotation config:
cat /etc/audit/auditd.conf | grep -E "max_log|num_logs|rotate"
# max_log_file = 8          <- max 8MB per file (too small for busy server)
# max_log_file_action = ROTATE
# num_logs = 5              <- keep only 5 rotated files

# Fix: increase log file size and count, or rotate daily:
cat >> /etc/audit/auditd.conf << 'EOF'
max_log_file = 100       # 100MB per file
num_logs = 10            # keep 10 files = 1GB total
max_log_file_action = ROTATE
space_left_action = SYSLOG  # alert when disk is low, don't stop
admin_space_left_action = SUSPEND  # suspend logging if critically low
EOF
service auditd reload

# For very high-volume audit: forward to centralized logging:
# Configure audisp-syslog plugin to send to rsyslog -> ELK/Splunk
```

---

### Related Keywords

**Foundational:**
LNX-057 (security), LNX-097 (security incidents), LNX-099 (fleet management)

**Builds on this:**
LNX-108 (multi-tenant security architecture)

**Related:**
LNX-108 (multi-tenant Linux security)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `oscap xccdf eval --profile cis_l1 ...` | Run CIS Level 1 compliance scan |
| `oscap xccdf generate fix --fix-type ansible ...` | Generate Ansible remediation |
| `sshd -t` | Validate sshd_config before restart |
| `sysctl -p /etc/sysctl.d/99-hardening.conf` | Apply sysctl hardening |
| `auditctl -l` | List active audit rules |
| `augenrules --load` | Load rules from /etc/audit/rules.d/ |
| `ansible-galaxy install MindPointGroup.RHEL8-CIS` | Get CIS Ansible role |
| `systemctl disable --now cups avahi-daemon rpcbind` | Disable unneeded services |

**3 things to remember:**
1. Always validate sshd_config with `sshd -t` BEFORE restarting sshd. A syntax error in sshd_config with a restart causes lockout. Use `systemctl reload sshd` (graceful reload) over `restart` for lower risk.
2. Six hardening areas: filesystem (noexec on /tmp), services (disable cups/avahi), SSH (no passwords, no root), PAM (lockout policy), auditd (log privilege escalation), sysctl (restrict kernel info, anti-spoofing).
3. CIS Benchmark compliance is measured by OpenSCAP (`oscap xccdf eval`). It measures CONFIGURATION compliance, not vulnerability status. Pair with vulnerability scanning for complete security picture.

---

### Transferable Wisdom

Linux hardening principles transfer directly to: container hardening
(CIS Docker/Kubernetes Benchmarks - same six areas: image contents, services,
network, credentials, runtime, audit), cloud hardening (CIS AWS/Azure/GCP
Benchmarks - IAM least privilege, S3 bucket policies, security groups instead
of sysctl, CloudTrail instead of auditd), application hardening (principle
of least privilege applies: app runs as non-root, no unnecessary file system
access, principle of minimal attack surface - disable unused endpoints,
features, dependencies). The "disable what you don't need" principle is
universal: API design (don't expose endpoints that don't exist yet),
database users (only SELECT on tables the user needs, not ALL PRIVILEGES),
Kubernetes RBAC (only verbs and resources the service account needs). The
compliance automation pattern (define desired state, measure actual state,
compute delta, remediate, re-measure) is: infrastructure IaC lifecycle,
Kubernetes reconciliation loop, GitOps workflow - the same pattern at
different abstraction levels. STIG severity categories (CAT I/II/III) map
directly to: security bug severity (Critical/High/Medium/Low in CVE CVSS
scoring), Kubernetes admission webhook violation severity (Block vs Warn).

---

### The Surprising Truth

The CIS Benchmarks document for RHEL 8 has 342 pages and covers over 250
individual controls. Yet most organizations applying "CIS Level 1" focus on
perhaps 20 of the most visible controls (SSH, noexec, sysctl parameters)
and call it "CIS compliant." An actual CIS Level 1 scan of a system with
"our standard CIS hardening applied" typically reveals 40-80 failures on
a first run.

The surprise is not that teams miss controls - it's WHY they miss them.
Many CIS controls are in areas that seem obvious in hindsight but are
invisible to the "SSH and sysctl" mental model: (1) Filesystem: separate
partitions for /var, /var/log, /var/tmp, /home with correct mount options;
(2) Time synchronization: NTP correctly configured and verified; (3)
Package management: GPG keys verified, security repositories configured;
(4) Cron access controls: who is allowed to run cron jobs; (5) Mandatory
access control: SELinux status and policy; (6) Warning banners: legal
notice before login (often required by law in some jurisdictions for
unauthorized access prosecution). The only reliable way to know your
CIS compliance level is to run an automated scan, not to manually
remember which controls you've applied.

---

### Mastery Checklist

- [ ] Can run an OpenSCAP CIS Level 1 assessment and interpret the results
- [ ] Knows the six major hardening areas and at least two controls per area
- [ ] Can write an sshd_config with key security settings and validate it before applying
- [ ] Can write basic auditd rules for privilege escalation and sensitive file monitoring
- [ ] Understands the difference between CIS Benchmarks and STIG and when each is appropriate

---

### Think About This

1. You are tasked with hardening a fleet of 500 production RHEL 8 servers that
   run Java microservices. An initial CIS Level 1 scan shows 65 failures. You
   need to reach 90% compliance within 60 days. Design your approach: how do you
   prioritize which controls to apply first (by security impact, by ease of
   remediation, or by CAT I/II/III severity)? How do you test that hardening
   doesn't break the Java applications? How do you handle the noexec/tmp issue
   if JVM uses /tmp for native libraries? What is your rollback plan?

2. Your team is evaluating: (a) CIS-based hardening applied in-place with Ansible,
   vs (b) Building a hardened golden AMI and replacing servers vs (c) Using AWS
   Inspector for continuous compliance monitoring without hardening automation.
   Evaluate each approach for: initial effort, ongoing maintenance, compliance
   auditability, risk of breaking production. Which would you recommend for a
   100-server fleet in a regulated industry (healthcare), and why?

3. A developer argues: "All this hardening slows down our deployment velocity.
   The threat model for our internal tool (only accessible within corporate
   VPN) doesn't justify CIS Level 1." Design a counter-argument OR design a
   reduced hardening baseline appropriate for internal-only tools. Which CIS
   controls are truly necessary regardless of network exposure? Which are
   optional for internal services? How do you formalize an exception process
   so that exceptions are tracked and not a slippery slope to no hardening?

---

### Interview Deep-Dive

**Foundational:**
Q: What is a CIS Benchmark, and walk me through the key areas of Linux hardening it covers.
A: CIS BENCHMARK OVERVIEW: The Center for Internet Security publishes configuration security guides for major platforms. For Linux (RHEL, Ubuntu, etc.): a detailed document with 200-350 controls organized by area, each with: description, rationale, audit procedure, remediation. Two levels: Level 1 (essential, low operational impact), Level 2 (defense-in-depth, higher impact). SIX KEY HARDENING AREAS: (1) FILESYSTEM: Separate /tmp on its own partition or tmpfs with mount options: `noexec` (cannot execute binaries from /tmp - stops malware), `nosuid` (SUID bits ignored - stops SUID escalation), `nodev` (no device files). Also: separate /var, /var/log, /home partitions to prevent log/data filling and affecting root filesystem. (2) SERVICES: Disable services not needed on servers: `cups` (print spooler), `avahi-daemon` (mDNS discovery), `rpcbind` (NFS RPC, if not using NFSv3), `bluetooth`. Fewer running services = smaller attack surface. (3) SSH: `PermitRootLogin no` (direct root login disabled, forces use of named accounts), `PasswordAuthentication no` (key-only auth, no brute force), `MaxAuthTries 4` (slow down credential stuffing), `X11Forwarding no`, `AllowTcpForwarding no`. (4) PAM (Pluggable Authentication Modules): account lockout policy (`pam_faillock: deny=5,unlock_time=900`), password complexity requirements, password history (prevent reuse). (5) AUDITING: `auditd` rules to log: who executed what (EXECVE), modifications to /etc/passwd, /etc/shadow, /etc/sudoers, /root/.ssh (identity files), cron jobs, privilege escalation (setuid/setgid syscalls). (6) KERNEL PARAMETERS (sysctl): `kernel.dmesg_restrict=1` (restrict kernel log to root), `kernel.kptr_restrict=2` (hide kernel pointers from /proc), `net.ipv4.conf.all.rp_filter=1` (anti-spoofing: reject packets with impossible source addresses), `kernel.randomize_va_space=2` (ASLR: randomize memory layout against buffer overflow exploitation), `net.ipv4.tcp_syncookies=1` (SYN flood protection). ASSESSMENT: OpenSCAP tool (`oscap xccdf eval`) automatically checks all controls and produces pass/fail report. AUTOMATION: OpenSCAP generates Ansible remediation playbook; `ansible-lockdown` roles provide maintained Ansible roles for CIS application.

**Expert:**
Q: How do you implement continuous compliance monitoring for a fleet of Linux servers, and how do you handle the tension between security requirements and application requirements?
A: CONTINUOUS COMPLIANCE ARCHITECTURE: Goal: know within 30 minutes if any server drifts from compliance baseline, and automatically remediate where possible. LAYER 1 - SCHEDULED SCANNING: `oscap xccdf eval` as Ansible playbook, run daily against all servers. Results stored in a database. Alert if new failures appear (failures that weren't present in previous scan = drift). Configuration: OpenSCAP in pull mode: each server runs its own scan and reports to central OpenSCAP server. Or: Ansible Tower scheduled job pushes OpenSCAP runs to all hosts. LAYER 2 - REAL-TIME DRIFT DETECTION: Ansible pull mode (ansible-pull via cron) or Puppet/Chef agents. Agents detect drift within one convergence cycle (30 minutes). Alert on changes to baseline configurations. LAYER 3 - FILE INTEGRITY MONITORING: AIDE or AWS Inspector (if cloud) detects file changes. Alert when /etc/ssh/sshd_config, /etc/pam.d/, /etc/sudoers change unexpectedly. HANDLING TENSION - Application Exceptions: Real scenario: Application X requires write access to /tmp for shared memory, but /tmp has noexec+nodev. WRONG approach: Remove noexec from /tmp globally (undermines security for all). RIGHT approach: (a) Investigate: does the app ACTUALLY need exec in /tmp, or does it just need write access? Many "needs /tmp exec" requirements can be satisfied by a writable directory WITHOUT exec. (b) Exception process: documented exception, approved by security team, tracked in compliance database as "accepted deviation." (c) Compensating control: if /tmp needs exec, add AppArmor/SELinux profile restricting what can run from /tmp, plus enhanced auditd monitoring. (d) Fix the application: configure JVM tmpdir to /var/tmp/java-work (which has exec but is separate from /tmp). EXCEPTION TRACKING: Compliance database: server ID, control ID, exception reason, approver, expiry date. Exceptions reviewed quarterly. New controls in CIS Benchmark version updates require re-review. ORGANIZATIONAL INTEGRATION: Compliance gates in CI/CD: new server AMIs must pass CIS Level 1 scan before approval. Change management: infrastructure changes require compliance impact assessment. Compliance dashboard: CIS score per server, trends over time, exception inventory. This creates a compliance program that is continuous, automated, and auditable - which is what PCI-DSS, HIPAA, and SOC2 Type II auditors want to see.
