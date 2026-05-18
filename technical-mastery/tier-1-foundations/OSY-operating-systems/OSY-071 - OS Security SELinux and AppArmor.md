---
id: OSY-071
title: OS Security SELinux and AppArmor
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-030, OSY-045
used_by: OSY-107, OSY-118
related: OSY-072, OSY-107, OSY-118
tags:
  - SELinux
  - AppArmor
  - MAC
  - mandatory-access-control
  - LSM
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/osy/selinux-apparmor/
---

## TL;DR

SELinux (Security-Enhanced Linux) and AppArmor are
Linux Security Module (LSM) implementations of Mandatory
Access Control (MAC). Unlike file permissions (DAC),
MAC enforces policy even on root. SELinux: label-based,
very granular (used by RHEL/CentOS). AppArmor: path-based,
simpler (used by Ubuntu/Debian). Containers: both are
used by Docker/Kubernetes for process isolation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-071 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | SELinux, AppArmor, MAC, LSM, container security, seccomp |
| **Prerequisites** | OSY-030, OSY-045 |

---

### DAC vs MAC

```
DAC (Discretionary Access Control) - traditional Unix:
  Object owner CONTROLS access (can grant/revoke)
  File owner: chmod, chown
  Root bypasses all DAC checks (UID 0 = all access)
  
  Limitation: compromised root = total system compromise
  Limitation: user can share their data with anyone
  
MAC (Mandatory Access Control) - SELinux/AppArmor:
  SYSTEM POLICY controls access (owner cannot override)
  Even root is subject to MAC policy
  Process labeled with domain; file labeled with type
  Access: domain must have permission to act on type
  
  Benefit: compromised root in restricted domain:
    Cannot read /etc/shadow if domain policy says NO
    Cannot write to /var/log/ if not allowed
    Cannot fork a new process if domain policy says NO
    
  Defense-in-depth: reduces blast radius of exploits

Linux Security Module (LSM):
  Kernel framework for security modules
  Hooks into every security-sensitive operation
  Multiple LSMs can be active (seccomp, yama, apparmor, selinux)
  But: SELinux and AppArmor are mutually exclusive as main MAC
```

---

### SELinux Labels and Policy

```
Every object (file, process, socket) has a SELinux context:
  user:role:type:level
  
  File: system_u:object_r:httpd_exec_t:s0
    type = httpd_exec_t (type that httpd expects to exec)
    
  Process: system_u:system_r:httpd_t:s0-s0:c0.c1023
    domain = httpd_t (domain where httpd runs)
    
  Context = LABEL (what this object is, not who owns it)

Policy rule example:
  allow httpd_t httpd_config_t:file read;
  # httpd (domain: httpd_t) can READ files of type httpd_config_t
  
  deny:
  # httpd cannot write /etc/passwd (type: passwd_file_t)
  # -> Not in allow rules -> denied (default deny)

SELinux modes:
  Enforcing:  policy enforced; violations blocked + logged
  Permissive: policy not enforced; violations ONLY logged
    (use for troubleshooting: what WOULD be blocked?)
  Disabled:   SELinux completely off (requires reboot to re-enable)
  
  getenforce  # show current mode
  setenforce 0  # switch to permissive (runtime, no reboot)
  setenforce 1  # switch to enforcing

View process context:
  ps auxZ | grep httpd
  # httpd: system_u:system_r:httpd_t:s0

View file context:
  ls -Z /etc/httpd/conf/httpd.conf
  # system_u:object_r:httpd_config_t:s0 httpd.conf
```

---

### AppArmor Profiles

```
AppArmor: profile-per-binary, path-based rules
  Simpler than SELinux; easier to write profiles
  
Profile for a web server:
  /etc/apparmor.d/usr.sbin.nginx:
  
  #include <tunables/global>
  
  /usr/sbin/nginx {
    #include <abstractions/base>
    
    # Capabilities:
    capability net_bind_service,  # bind to port 80/443
    capability setuid,            # drop privileges
    
    # File access:
    /etc/nginx/** r,              # config files: read
    /var/www/html/** r,           # web root: read only
    /var/log/nginx/** w,          # logs: write
    /run/nginx.pid rw,            # PID file
    /tmp/ rw,
    
    # Deny (implicit):
    # Cannot access /etc/shadow
    # Cannot access /home/*
    # Cannot execute arbitrary binaries
  }

AppArmor modes per profile:
  enforce: policy applied, violations blocked+logged
  complain: violations logged but not blocked (like permissive)
  
  aa-status         # show all profiles and modes
  aa-complain /etc/apparmor.d/profile  # set profile to complain
  aa-enforce  /etc/apparmor.d/profile  # set profile to enforce
  
  Logs (AppArmor violations):
    /var/log/syslog | grep apparmor
    /var/log/kern.log | grep audit
```

---

### Docker and Kubernetes Security

```
Docker security layers (all active by default):
  1. seccomp: limits which syscalls the container can make
     Default profile: ~300 allowed syscalls (blocks ~50 dangerous ones)
     Blocked: reboot(), mount(), swapon(), kexec_load(), etc.
     
  2. AppArmor: Docker's default profile (docker-default)
     Restricts: mounts, /proc writes, file caps
     
  3. Linux capabilities: drop all but needed caps
     Default: NOT root in container; limited caps
     --privileged: bypasses ALL security (don't use!)
     
  4. Namespaces: isolation (see OSY-072)
  5. cgroups: resource limits

Kubernetes Pod security:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    readOnlyRootFilesystem: true  # prevents writes to container root
    allowPrivilegeEscalation: false
    seccompProfile:
      type: RuntimeDefault    # use containerd's default seccomp
    appArmorProfile:
      type: RuntimeDefault    # use runtime's AppArmor profile
      
  Pod Security Admission (PSA, replaces PSP):
    restricted: most secure (all of the above required)
    baseline:   prevents known privilege escalations
    privileged: no restrictions

seccomp profile (example - custom):
  {
    "defaultAction": "SCMP_ACT_ERRNO",
    "syscalls": [
      { "names": ["read", "write", "open", "close"],
        "action": "SCMP_ACT_ALLOW" }
    ]
  }
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Setting SELinux to permissive is fine for production to avoid false positives" | Permissive mode disables all MAC enforcement - it's equivalent to SELinux disabled from a security perspective. If your application violates policy in permissive mode, an attacker can exploit the same access paths. Use permissive only for troubleshooting, then re-enable enforcing and fix the denials |
| "Docker containers are secure by default because they are isolated" | Docker namespace isolation provides process isolation but NOT MAC policy. Without AppArmor/SELinux profiles and seccomp filters, a container breakout vulnerability gives an attacker access to the host at the container's capability level. The default AppArmor and seccomp profiles provide a good baseline but custom applications often need custom profiles |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| DAC | File owner controls access; root bypasses all |
| MAC | System policy controls access; even root restricted |
| SELinux | Label-based; type enforcement; RHEL/CentOS default |
| AppArmor | Path-based profiles; simpler; Ubuntu/Debian default |
| Permissive mode | Logs violations but doesn't block (troubleshooting only) |
| Container security | seccomp + AppArmor + capabilities = Docker default layers |
