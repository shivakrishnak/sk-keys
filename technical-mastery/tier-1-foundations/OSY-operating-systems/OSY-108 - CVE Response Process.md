---
id: OSY-108
title: CVE Response Process
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-102, OSY-103, OSY-107
used_by: []
related: OSY-107, OSY-109, OSY-117
tags:
  - CVE
  - vulnerability
  - patch-management
  - incident-response
  - security
  - compliance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 108
permalink: /technical-mastery/osy/cve-response-process/
---

## TL;DR

A CVE (Common Vulnerabilities and Exposures) response process
defines how teams detect, assess, prioritize, and remediate
OS-level vulnerabilities. Key components: automated scanning
(Trivy, Grype, Qualys), CVSS severity scoring, SLA by severity,
patch application workflow, and post-patch verification.
Missing this process = persistent high-severity unpatched
vulnerabilities in production.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-108 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | CVE, CVSS, vulnerability management, patch management, Trivy |
| **Prerequisites** | OSY-102, OSY-103, OSY-107 |

---

### CVE Lifecycle

```
1. Discovery:
   Security researcher finds vulnerability
   
2. Coordination:
   Researcher reports to vendor (private disclosure)
   Vendor develops patch (embargo period: typically 90 days)
   
3. CVE ID assignment:
   MITRE assigns CVE-YYYY-NNNNN identifier
   NVD (National Vulnerability Database) publishes
   Includes: CVSS score, affected versions, CWE type
   
4. Patch release:
   Vendor releases fix
   Linux distros (Ubuntu, RHEL): backport patch to supported versions
   
5. Exploitation in the wild:
   Days-to-weeks after disclosure: exploits published
   Week 1-2: automated exploit tools appear
   Month 1+: widespread opportunistic scanning
   
6. Your team's response:
   Detection: scanning tools find CVE in your systems
   Triage: assess severity and exploitability in YOUR context
   Remediation: patch, workaround, or accept risk
   Verification: confirm patched
```

---

### CVSS Scoring

```
CVSS (Common Vulnerability Scoring System) v3.1:
  
  Severity levels:
    Critical: 9.0-10.0 (remote code execution, unauthenticated)
    High:     7.0-8.9  (privilege escalation, significant impact)
    Medium:   4.0-6.9  (requires local access or specific conditions)
    Low:      0.1-3.9  (minimal impact)
    
  CVSS Base Score components:
    Attack Vector (AV):
      Network (N): remotely exploitable -> highest severity
      Adjacent (A): same network segment
      Local (L): requires local shell
      Physical (P): physical access required
      
    Attack Complexity (AC):
      Low: reliable exploitation
      High: requires specific conditions, may not work reliably
      
    Privileges Required (PR):
      None: no authentication needed
      Low: normal user
      High: admin/root required
      
    User Interaction (UI):
      None: no victim action required
      Required: victim must click, open, etc.
      
    Scope (S):
      Unchanged: only the vulnerable component affected
      Changed: can affect other components (container escape = Changed)
      
    Confidentiality/Integrity/Availability:
      High/Low/None impact on each
      
  Example: Dirty COW CVE-2016-5195
    AV:L (Local) / AC:H (race condition) / PR:L (user) / UI:N / S:U / C:H/I:H/A:H
    CVSS 3.1 Score: 7.0 (High)
    
  Example: Log4Shell CVE-2021-44228
    AV:N / AC:L / PR:N / UI:N / S:C / C:H / I:H / A:H
    CVSS 3.1 Score: 10.0 (Critical)
```

---

### Automated Scanning Pipeline

```bash
# Container image scanning (CI/CD integration)

# Trivy: comprehensive scanner (OS + Java + npm + etc.)
# Install: https://aquasecurity.github.io/trivy

# Scan a container image:
trivy image --severity HIGH,CRITICAL nginx:latest

# Scan with exit code (fail CI if critical found):
trivy image --exit-code 1 --severity CRITICAL myapp:latest

# Scan filesystem (for VMs or build artifacts):
trivy fs --severity HIGH,CRITICAL /opt/myapp/

# Generate SARIF report (for GitHub Security tab):
trivy image --format sarif -o results.sarif myapp:latest

# Grype: alternative scanner
grype dir:. --fail-on critical

# Host scanning (running system):
# apt-based:
apt list --upgradable 2>/dev/null | grep -i security
unattended-upgrades --dry-run | grep "security"

# RHEL/CentOS:
yum check-update --security
yum update --security  # Apply security updates only

# Automatic security patching:
# Ubuntu: unattended-upgrades
apt install unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
  "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF
```

---

### SLA Framework for CVE Remediation

```
Define response SLA by severity:
  
  Critical (9.0-10.0):
    Patch within: 24-48 hours for internet-facing systems
    If patch unavailable: implement compensating control within 24h
    Escalation: immediate notification to CISO/security team
    
  High (7.0-8.9):
    Patch within: 7-14 days for internet-facing systems
    Patch within: 30 days for internal systems
    
  Medium (4.0-6.9):
    Patch within: 30-60 days
    Can batch with regular patching cycle
    
  Low (0.1-3.9):
    Patch within: next regular patch cycle (quarterly acceptable)
    
  Risk acceptance process:
    Some CVEs: not patchable immediately (no fix yet, or breaking change)
    Document: CVE ID, score, why not patched, mitigations in place
    Review: monthly for high severity; quarterly for medium
    
Patching workflow:
  1. Detect: scanning in CI/CD + periodic host scans
  2. Triage: CVSS score + exploitability in context
  3. Test in staging: apply patch; run regression tests
  4. Deploy: rolling update to production
  5. Verify: re-scan confirms CVE resolved
  6. Document: update asset inventory; record patch applied
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CVSS 10.0 means I'm immediately being attacked" | CVSS scores exploitability potential in the WORST CASE, not in YOUR context. Log4Shell (10.0): only exploitable if your application uses Log4j 2.x with user input reaching the logger. A service that doesn't use Log4j: zero impact. Context matters: assess YOUR exposure, not just the theoretical score. |
| "Patching the OS is enough" | The OS kernel is one layer. Application-layer CVEs (Log4Shell, Spring4Shell) are separate from OS CVEs. Container images contain multiple layers of software, each with potential CVEs. Scan both: OS packages AND application dependencies (Maven, npm, pip). Use tools like Trivy that check all layers. |
| "Once patched, I'm safe from that CVE" | Patching removes the specific vulnerability but doesn't address: attackers who exploited BEFORE you patched, similar vulnerabilities in the same code (variant hunting), or supply chain compromises. After patching a critical CVE: audit logs for exploitation indicators, rotate credentials that may have been exposed. |

---

### Quick Reference Card

| Severity | CVSS Range | Target Patch Time |
|----------|------------|-------------------|
| Critical | 9.0-10.0 | 24-48 hours |
| High | 7.0-8.9 | 7-14 days |
| Medium | 4.0-6.9 | 30-60 days |
| Low | 0.1-3.9 | Next patch cycle |
| Scan containers | Trivy | `trivy image --severity HIGH,CRITICAL` |
| Scan host | apt | `apt list --upgradable` |
| Auto-patch | Ubuntu | unattended-upgrades |
| Check patch applied | Trivy | Re-scan after patching |
