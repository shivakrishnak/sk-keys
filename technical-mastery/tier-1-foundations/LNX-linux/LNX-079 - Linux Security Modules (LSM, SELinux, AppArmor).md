---
id: LNX-079
title: "Linux Security Modules (LSM, SELinux, AppArmor)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-078, LNX-071
used_by: LNX-080, LNX-108
related: LNX-078, LNX-080, LNX-064
tags: [lsm, selinux, apparmor, mandatory-access-control, type-enforcement, security-context, aa-status, getenforce, setenforce, ausearch, avc-denial, container-security, mac, dac]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/lnx/linux-security-modules/
---

## TL;DR

**LSM (Linux Security Modules)** is a kernel hook framework enabling
mandatory access control (MAC) alongside normal DAC (permissions). Two
dominant implementations: **SELinux** (Red Hat/RHEL: label-based MAC, every
process and file has a type label, policy defines allowed interactions -
`getenforce`, `setenforce`, `ausearch -m avc`) and **AppArmor** (Ubuntu/Debian:
path-based MAC, profiles in `/etc/apparmor.d/`, `aa-status`, `aa-logprof`).
SELinux blocks are AVC denials (check `audit.log`). AppArmor blocks appear
in `/var/log/syslog`. Docker applies its own AppArmor profile (`docker-default`)
by default. SELinux on container hosts uses `svirt_lxc_net_t` contexts.
These are COMPLEMENTARY to capabilities and seccomp - all three provide
defense in depth.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-079 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | LSM, SELinux, AppArmor, MAC, type enforcement, AVC denial, security context, container security |
| **Prerequisites** | LNX-078 (Capabilities, seccomp), LNX-071 (Namespaces) |

---

### The Problem This Solves

**Problem 1**: A web server is compromised. The attacker has code execution
as the `apache` user. On a system with only DAC (traditional permissions):
`apache` can read any file owned by `apache`, write to `/var/www/html/`,
and connect to any network destination. Attacker installs a reverse shell
by writing to `/var/www/html/shell.php` and exfiltrating data by connecting
to `attacker.com:4444`. With SELinux/AppArmor: the `apache` process runs
with a type label (`httpd_t`). Policy: httpd_t can read `httpd_config_t`
files, write `httpd_log_t` files, and make TCP connections to `http_port_t`
(ports 80, 443, 8080) only. Connecting to `attacker.com:4444` = AVC denied.
Writing to non-www directories = AVC denied. The compromise is contained.

**Problem 2**: A container runtime needs to prevent containers from
accessing host resources even when a capability or namespace bug is
exploited. LSM provides a second, independent enforcement layer. Even if
a container escapes its namespace, the SELinux context (`svirt_lxc_net_t`)
prevents it from reading host files (which have `system_u:object_r:...`
contexts outside what `svirt_lxc_net_t` can access).

---

### Textbook Definition

**Linux Security Modules (LSM)**: A kernel framework (since 2.6) that
provides hook points throughout kernel code for security modules to
intercept and control security-sensitive operations. LSM hooks are called
BEFORE the kernel performs operations: file open, socket connect, process
exec, IPC. If an LSM returns a denial: operation fails with EACCES even
if DAC (file permissions) would allow it. Multiple LSMs can stack (since
kernel 5.1): seccomp runs first, then the active LSM(s).

**DAC vs MAC:**
- DAC (Discretionary Access Control): owner decides permissions (`chmod`, `chown`). Policy is decentralized (each user controls their files)
- MAC (Mandatory Access Control): system-wide policy enforced by the kernel. Users and processes CANNOT change their own labels or bypass policy

**SELinux**: NSA-developed, merged kernel 2.6.0 (2003). RHEL/Fedora/CentOS
default. Type Enforcement (TE): every subject (process) and object (file,
socket, etc.) has a TYPE. Policy rules: `allow httpd_t httpd_config_t:file
{read open getattr}`. Multi-Level Security (MLS) optional extension.

**AppArmor**: Novell-developed, Ubuntu/Debian default. PATH-based: profiles
attached to programs by path. Profile modes: enforce (deny violations) or
complain (log violations, allow). Simpler than SELinux but less granular.

---

### Understand It in 30 Seconds

```bash
# === SELinux: check and manage ===
# Distro detection:
cat /etc/os-release | grep ID
# RHEL/CentOS/Fedora: SELinux default
# Ubuntu/Debian: AppArmor default

# === SELinux ===
# Check SELinux status:
getenforce        # Enforcing | Permissive | Disabled
sestatus          # Detailed status

# Switch to permissive mode (for debugging - logs denials, doesn't block):
setenforce 0      # Permissive (temporary, until next boot)
setenforce 1      # Enforcing

# Persistent change: /etc/selinux/config:
# SELINUX=enforcing | permissive | disabled
# (requires reboot to disable/enable)

# View SELinux context of files and processes:
ls -Z /var/www/html/
# system_u:object_r:httpd_sys_content_t:s0 index.html
# ^user    ^role     ^type              ^level

ps auxZ | grep nginx
# system_u:system_r:httpd_t:s0 nginx

# View SELinux context of current process:
id -Z
# unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023

# Fix SELinux context on a file (restore to expected default):
restorecon -v /var/www/html/myapp.conf
restorecon -Rv /var/www/html/   # recursive

# Set a context explicitly:
chcon -t httpd_sys_content_t /data/webfiles/index.html

# Check AVC denials (access vector cache = security decision cache):
ausearch -m avc | tail -20
# type=AVC msg=audit(1699888000.123:456): avc:  denied
# { read } for pid=1234 comm="nginx" path="/etc/custom.conf"
# tcontext=system_u:object_r:etc_t:s0 tclass=file

# Recommended: use audit2why for human-readable explanation:
ausearch -m avc | audit2why
# Was caused by: Missing type enforcement (TE) allow rule.
# You can use audit2allow to generate a loadable module to allow this access.

# Allow a denied operation (generate custom policy module):
ausearch -m avc | audit2allow -M mymodule
# Creates mymodule.pp and mymodule.te
semodule -i mymodule.pp   # load the policy module

# See available SELinux file contexts:
semanage fcontext -l | grep httpd
# /var/www(/.*)?   all files  system_u:object_r:httpd_sys_content_t:s0

# Add new file context mapping:
semanage fcontext -a -t httpd_sys_content_t "/data/webroot(/.*)?"
restorecon -Rv /data/webroot/

# Manage booleans (pre-defined SELinux policy switches):
getsebool -a | grep httpd     # list httpd-related booleans
setsebool httpd_can_network_connect 1  # allow httpd to make network connections
setsebool -P httpd_can_network_connect 1  # -P: persistent across reboots

# === AppArmor ===
# Check AppArmor status:
aa-status
# apparmor module is loaded.
# 14 profiles are loaded.
# 14 profiles are in enforce mode.
# 0 profiles are in complain mode.

# List profiles and their modes:
aa-status | grep -A100 "enforce mode"

# Put a profile in complain mode (log only, don't deny):
aa-complain /etc/apparmor.d/usr.sbin.nginx
# aa-complain /usr/sbin/nginx  # alternative

# Put back in enforce:
aa-enforce /etc/apparmor.d/usr.sbin.nginx

# Reload a profile after editing:
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx

# View AppArmor denials:
grep "apparmor" /var/log/syslog | grep DENIED
grep "apparmor" /var/log/kern.log | grep "DENIED"
# Example:
# kernel: audit: type=1400 audit(1699888000.123:456):
# apparmor="DENIED" operation="file_mmap" profile="docker-default"
# name="/proc/sys/kernel/shm_rmid_forced"

# Generate profile updates from logs:
aa-logprof   # interactive: reads logs, suggests profile updates

# Docker AppArmor:
docker run --security-opt apparmor=docker-default myapp  # default
docker run --security-opt apparmor=unconfined myapp      # disable for debugging
```

---

### First Principles

**SELinux decision flow:**
```
Process (Subject) tries to open a file (Object)

Step 1: DAC check (traditional Unix permissions)
  Is process UID/GID allowed? (rwx bits, ACLs)
  If NO: EACCES immediately (LSM not even consulted)
  If YES: proceed to Step 2

Step 2: SELinux check (MAC, Type Enforcement)
  Query: "Is type A allowed to perform action B on type C?"

  Subject context: system_u:system_r:httpd_t:s0
    User: system_u
    Role: system_r
    Type: httpd_t  <-- most important for TE
    Level: s0

  Object context: system_u:object_r:shadow_t:s0
    Type: shadow_t  <-- most important for TE
    (/etc/shadow is type shadow_t, root passwords!)

  Policy lookup:
    Is there an allow rule: allow httpd_t shadow_t:file {read open} ?
    NO -> AVC DENIED
    Result: EACCES (even though DAC permissions might allow it)

  If YES -> Operation proceeds

Security context format:
  user:role:type:level (MLS)
  system_u:system_r:httpd_t:s0-s0:c0.c1023

  Users: system_u (kernel/system), unconfined_u (user processes),
         root (root user), staff_u, user_u, guest_u
  Roles: system_r (system daemons), object_r (files/dirs),
         unconfined_r, sysadm_r, staff_r
  Type: the key enforcement field (httpd_t, ssh_t, kernel_t, etc.)
  Level: s0-s0:c0.c1023 (MLS level, s=sensitivity, c=category)

AVC (Access Vector Cache):
  SELinux caches recent policy decisions for performance
  Cache hit: O(1) lookup
  Cache miss: full policy evaluation (then cached)
  Cache cleared on policy change
  nr_avc_lookups, nr_avc_hits in /proc/net/selinux/avc/cache_stats
```

**AppArmor profile mechanics:**
```
Profile format:
  /usr/sbin/nginx {
    #include <abstractions/base>
    #include <abstractions/nameservice>
    
    capability net_bind_service,  # allow binding port < 1024
    capability setuid,
    capability setgid,
    
    # File access rules:
    /etc/nginx/** r,             # read config
    /var/log/nginx/*.log w,      # write logs
    /var/www/html/** r,          # read web files
    /run/nginx.pid rw,           # PID file
    
    # Deny explicitly:
    deny /etc/shadow r,          # never read passwords
    deny /proc/sys/kernel/** w,  # never modify kernel params
    
    # Network:
    network inet stream,         # IPv4 TCP
    network inet6 stream,        # IPv6 TCP
    
    # Capability-style checks:
    /proc/*/attr/current w,      # allow setting own security attr
  }

Match order:
  AppArmor checks rules in order, first match wins
  deny rules always override allow rules of same specificity

Path vs label difference (AppArmor vs SELinux):
  AppArmor: profile attached to /usr/sbin/nginx (path)
    If nginx moves to /opt/myapp/nginx: profile doesn't apply!
    File permission changes don't affect profile attachment
    
  SELinux: policy attached to type label (httpd_t)
    Label follows the file/process regardless of path
    Label is in the inode (type=httpd_sys_content_t)
    Hard to accidentally lose label coverage
    More robust but more complex to manage

Container interaction (Docker + AppArmor):
  Docker applies "docker-default" AppArmor profile to all containers
  Profile allows: basic operations, network, /proc reads
  Profile blocks: mount, ptrace, most /proc/sys writes
  
  See profile:
  cat /etc/apparmor.d/docker-default
  
  Kubernetes uses the same profile by default (on Ubuntu nodes)
  Custom profile: annotation on pod
    container.apparmor.security.beta.kubernetes.io/mycontainer: localhost/my-profile
```

---

### Thought Experiment

Real scenario: debugging a web application after SELinux denial:

```bash
# Scenario: New nginx site fails to serve files from /data/webfiles/
# Error 403 Forbidden in browser, even though file permissions are correct

# Step 1: Verify it's SELinux (not permissions):
ls -la /data/webfiles/index.html
# -rw-r--r-- 1 root root 1234 Nov  1 10:00 /data/webfiles/index.html
# ^ nginx (www-data) should be able to read this

# Check SELinux status:
getenforce    # Enforcing

# Check for AVC denial:
ausearch -m avc -ts recent | grep nginx
# avc:  denied  { read } for  pid=1234 comm="nginx" 
# name="index.html" dev="sda1" ino=456789
# scontext=system_u:system_r:httpd_t:s0
# tcontext=system_u:object_r:default_t:s0   <--- PROBLEM!
# tclass=file

# Problem identified: /data/webfiles/index.html has type "default_t"
# but httpd_t can only read "httpd_sys_content_t" (and similar)

# Step 2: Fix the context:
# Option A: Set correct context on files:
semanage fcontext -a -t httpd_sys_content_t "/data/webfiles(/.*)?"
restorecon -Rv /data/webfiles/

# Verify:
ls -Z /data/webfiles/index.html
# system_u:object_r:httpd_sys_content_t:s0 /data/webfiles/index.html

# Option B (less desirable): Enable boolean instead:
setsebool -P httpd_read_user_content 1
# Allows httpd to read user home directories etc. - too broad

# Step 3: Test:
curl -v http://localhost/
# HTTP/1.1 200 OK  <- Fixed!

# Step 4: Make permanent (semanage fcontext already done above)
# restorecon ran: context persisted in file attributes
# Files created under /data/webfiles/ will inherit httpd_sys_content_t

# Common SELinux workflow for developers:
# 1. Set permissive mode to identify ALL denials at once:
setenforce 0
# 2. Run the application, exercise all code paths
# 3. Collect all AVC denials:
ausearch -m avc | audit2allow -M myapp_policy
# 4. Review the generated policy (myapp_policy.te):
cat myapp_policy.te
# allow httpd_t httpd_sys_content_t:file { read open };
# 5. Load the policy:
semodule -i myapp_policy.pp
# 6. Return to enforcing:
setenforce 1
# 7. Test - application should work
```

---

### Mental Model / Analogy

```
DAC (traditional Unix) = building key access by ownership
  You OWN a room: you decide who can enter (chmod)
  Owner can always bypass their own locks
  Root can bypass EVERYONE's locks
  Problem: if root is compromised = all doors open

MAC (SELinux/AppArmor) = building security policy from a CENTRAL AUTHORITY
  A security policy exists OUTSIDE the control of individual users
  Even root cannot override MAC (in enforcing mode)
  Policy defines: WHAT types of processes can access WHAT types of files

SELinux = label-based MAC (like government security clearances):
  Every person (process) has a CLEARANCE LEVEL + COMPARTMENT:
    "system_u:system_r:httpd_t:s0"
    = Works for System (user), in System-Role dept, in HTTP division, clearance level 0
  
  Every document (file) has a CLASSIFICATION:
    "system_u:object_r:httpd_sys_content_t:s0"
    = Classified as HTTP-Content, clearance level 0
  
  Policy: which clearances can access which classifications?
    "httpd_t clearance CAN read httpd_sys_content_t files"
    "httpd_t clearance CANNOT read shadow_t files (passwords)"
  
  AVC denial = failed security clearance check
  audit2allow = HR process to update the policy
  
  If the HTTP division person is compromised (nginx exploit):
    Attacker has httpd_t clearance
    Cannot read password files (shadow_t): clearance denied
    Cannot make raw network connections (not in policy)
    Cannot write to system directories: not in policy
    BLAST RADIUS LIMITED to httpd_t's allowed operations

AppArmor = path-based MAC (like building access by JOB TITLE + SPECIFIC ROOMS):
  Profile attached to: /usr/sbin/nginx (this specific executable)
  Profile lists: "nginx is allowed to enter rooms: /etc/nginx/, /var/www/, /run/"
  
  Simpler: specify rooms by path, not by classification labels
  Trade-off: path-based = if the file is in the wrong place, policy misses it
             label-based = label travels with the file (more robust)
  
  aa-logprof = security admin reviewing access logs and updating door permissions

Docker default: AppArmor (Ubuntu) or SELinux (RHEL)
  Container = new employee hired through staffing agency
  Runtime applies the default profile: "temporary contractor access"
  More restricted than a regular employee (system process)
  Can do: basic file I/O, network, process management
  Cannot do: mount drives, load kernel modules, trace other processes
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept of MAC vs DAC. SELinux status: `getenforce`, permissive vs enforcing.
AppArmor status: `aa-status`. SELinux AVC denial in logs. `restorecon` to
fix file contexts. AppArmor profile enforcement vs complain mode.

**Level 2:**
SELinux context format: user:role:type:level. `ls -Z`, `ps auxZ`.
`chcon`, `semanage fcontext`, `restorecon`. SELinux booleans: `getsebool`,
`setsebool`. AppArmor profiles location: `/etc/apparmor.d/`. `aa-complain`,
`aa-enforce`, `aa-logprof`. Docker AppArmor and SELinux integration.

**Level 3:**
SELinux policy modules: `audit2allow`, `audit2why`, `semodule`. Type
transitions (process exec changes type). SELinux role transitions. Port
labeling: `semanage port -l`. SELinux file type hierarchy. AppArmor
abstractions (includes). AppArmor network rules. Kubernetes annotations
for AppArmor/SELinux profiles. SELinux `svirt_lxc_net_t` for containers.

**Level 4:**
Writing custom SELinux policies from scratch (`.te`, `.fc`, `.if` files).
SELinux MLS (Multi-Level Security): sensitivity levels, categories. SELinux
Reference Policy structure. AppArmor profile generation with `aa-genprof`.
LSM stacking (seccomp + AppArmor + SELinux ordering). Domain transitions in
SELinux (httpd_t -> cgi_script_t on exec). `dontaudit` rules (suppress noisy
denials). Performance: AVC cache behavior, policy complexity impact.

**Level 5:**
LSM hook points in kernel source: `security_inode_permission()`,
`security_socket_connect()`, etc. Writing a custom LSM (kernel module).
SELinux policy as formal logic: allow rules as directed graph of permissions.
SELinux confinement escape techniques (historical CVEs). Tomoyo (third major
LSM): learning mode, path-based with more flexibility. SMACK (Simplified
Mandatory Access Control Kernel): internet-of-things/embedded focus.
Security context propagation in distributed systems (SELinux with NFS,
iSCSI).

---

### Code Example

**BAD - disabling or bypassing MAC security:**
```bash
# BAD 1: Permanently disabling SELinux to "fix" application issues:
# /etc/selinux/config:
# SELINUX=disabled  <- NEVER do this in production
#
# This removes the entire MAC layer
# Correct approach: put in permissive mode, diagnose, fix labels/policy
# SELinux permissive mode still logs (audit.log) but doesn't block
# Gives you time to understand and fix without removing the security layer

# BAD 2: Setting AppArmor to complain on all profiles:
for profile in /etc/apparmor.d/*; do
    aa-complain "$profile"   # everything in log-only mode
done
# Now nothing is enforced: AppArmor is cosmetically active but ineffective

# BAD 3: Running containers with --security-opt apparmor=unconfined:
docker run --security-opt apparmor=unconfined myapp
# Removes AppArmor protection from container
# Only acceptable for debugging, never production

# BAD 4: Using setenforce 0 without a plan:
setenforce 0   # permissive mode: logs but doesn't block
# Commonly done as a "quick fix" when apps break
# Teams then forget to re-enable it
# Months later: SELinux is silently permissive in production
```

**GOOD - SELinux workflow:**
```bash
# GOOD: Proper SELinux workflow for a new application

# 1. Start with permissive mode to collect all denials without blocking:
setenforce 0

# 2. Run application through ALL code paths:
./run_integration_tests.sh
./exercise_all_features.sh

# 3. Collect all AVC denials:
ausearch -m avc | audit2allow -M myapp
# Creates: myapp.te (text policy) and myapp.pp (compiled policy)

# 4. REVIEW the generated policy (critical step!):
cat myapp.te
# module myapp 1.0;
# require {
#   type httpd_t;
#   type tmp_t;
# }
# allow httpd_t tmp_t:file { read write create };
# ^ Review: should httpd be writing to /tmp? Is this expected?
# If yes: load. If no: fix the application's tmp file handling.

# 5. Load the approved policy:
semodule -i myapp.pp

# 6. Return to enforcing:
setenforce 1

# 7. Test and monitor:
ausearch -m avc -ts recent   # check for any remaining denials

# GOOD: AppArmor profile generation:
# 1. Generate initial profile:
aa-genprof /usr/bin/myapp
# Opens interactive session:
# Start the application, exercise all features
# Return to aa-genprof, accept/deny/customize suggested rules
# Save profile to /etc/apparmor.d/usr.bin.myapp

# 2. Test in complain mode first:
aa-complain /usr/bin/myapp
# Run application, check: grep "apparmor" /var/log/syslog

# 3. Refine with aa-logprof:
aa-logprof   # reads logs, suggests profile additions

# 4. Switch to enforce:
aa-enforce /usr/bin/myapp

# GOOD: Custom AppArmor profile for a web service:
cat > /etc/apparmor.d/usr.sbin.mywebapp << 'PROFILE'
#include <tunables/global>
/usr/sbin/mywebapp {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/openssl>
  
  capability net_bind_service,
  capability setuid,
  capability setgid,
  
  # Application config
  /etc/mywebapp/** r,
  
  # Logs (write-only)
  /var/log/mywebapp/*.log w,
  
  # Static web files (read-only)
  /var/www/mywebapp/** r,
  
  # Upload directory (read+write+create)
  /var/lib/mywebapp/uploads/** rw,
  owner /var/lib/mywebapp/uploads/** rwkl,
  
  # PID file
  /run/mywebapp.pid rw,
  
  # SSL certificates (read-only)
  /etc/ssl/certs/** r,
  /etc/mywebapp/ssl/** r,
  
  # Deny sensitive files explicitly:
  deny /etc/shadow r,
  deny /etc/passwd w,
  deny /proc/sys/kernel/** w,
  
  # Network:
  network inet stream,
  network inet6 stream,
}
PROFILE

apparmor_parser -r /etc/apparmor.d/usr.sbin.mywebapp
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "SELinux/AppArmor can be disabled when causing problems - I'll re-enable later" | In practice, "re-enable later" becomes "never." This is one of the most common security regressions in Linux deployments. Once disabled, teams find new applications and scripts written without MAC compatibility, making re-enablement harder over time. The correct approach: put in PERMISSIVE mode temporarily, diagnose the AVC denials, fix labels or write policy modules, then return to enforcing. Permissive mode still logs all denials (which can later be bulk-analyzed) without blocking operations. A system with SELinux in permissive mode is significantly more visible (you see all violations) than a system without SELinux entirely. |
| "SELinux and AppArmor do the same thing, just differently" | SELinux and AppArmor have fundamentally different security models. AppArmor is PATH-BASED: profiles are tied to the executable path. If a file is moved, the profile doesn't follow it. If you have two copies of a binary at different paths, you need two profiles. AppArmor is easier to write policies for but less granular. SELinux is LABEL-BASED: every process and file has a security context (label) stored as an extended attribute. Labels follow files across renames and moves. Policy is based on TYPE PAIRS (source type, target type) - location-independent. SELinux is harder to configure correctly but more robust and comprehensive. Practical guidance: Ubuntu/Debian systems (AppArmor default) are easier to manage with custom profiles. RHEL/CentOS (SELinux default) has well-developed policy for standard applications but custom policy authoring requires more expertise. |
| "Docker containers on SELinux systems are fully isolated by SELinux" | Docker containers on SELinux systems do get SELinux confinement by default: all container processes run as `svirt_lxc_net_t` type. This confines them significantly. However, the protection level is only as good as the SELinux policy for `svirt_lxc_net_t`. By default: containers can access files with `container_file_t` type (Docker-managed volumes) but are blocked from host files with other types. HOWEVER: if a user mounts a host path into a container (`-v /host/path:/container/path`), the host files retain their original SELinux context (e.g., `admin_home_t`). The container (svirt_lxc_net_t) may or may not be allowed to access that type. To share files: either use `:z` or `:Z` volume flags: `docker run -v /data:/app:z myapp` - the `:z` flag relabels the host directory to `container_file_t` (shared among all containers), `:Z` relabels as private (unique container context). Forgetting `:z`/`:Z` is a very common Docker + SELinux issue. |
| "LSM is only about file access control" | LSM provides hooks for a comprehensive set of operations beyond file access: network sockets (connect, bind, listen), IPC (shared memory, semaphores, message queues), process operations (fork, exec, signal, ptrace), capabilities checks, XATTRs, and more. A complete LSM policy like SELinux's reference policy or a well-crafted AppArmor profile restricts ALL of these dimensions. For example: SELinux can prevent httpd_t from connecting to non-http ports (network policy), from creating child processes with exec (process policy), from attaching to shared memory owned by other services (IPC policy). This comprehensive coverage is what makes SELinux effective against lateral movement after a compromise: even if code execution is achieved, the policy limits almost all vectors for escalation or exfiltration. |

---

### Failure Modes & Diagnosis

**SELinux AVC denial diagnosis:**
```bash
# Complete SELinux troubleshooting workflow:

# Step 1: Confirm SELinux is causing the problem:
# Temporarily set permissive and retry:
setenforce 0
# If the problem goes away: SELinux was blocking it
# Collect denials:
ausearch -m avc -ts recent

# Step 2: Identify the denial:
ausearch -m avc | head -50
# type=AVC msg=audit(1699888000.123:456): avc:  denied
# { connectto } for pid=1234 comm="httpd"
# path="/run/some-socket.sock"
# scontext=system_u:system_r:httpd_t:s0
# tcontext=system_u:system_r:some_daemon_t:s0
# tclass=unix_stream_socket

# Fields to extract:
# action: connectto (what was denied)
# scontext type: httpd_t (who is trying)
# tcontext type: some_daemon_t (what they're accessing)
# tclass: unix_stream_socket (type of object)

# Step 3: Get human-readable explanation:
ausearch -m avc | audit2why
# Missing allow rule: allow httpd_t some_daemon_t:unix_stream_socket connectto

# Step 4: Create policy to allow it (if legitimate):
ausearch -m avc | audit2allow -M mymodule
cat mymodule.te    # review before loading
semodule -i mymodule.pp

# Step 5: Re-enable enforcing:
setenforce 1

# Common SELinux issue: web content in wrong location
# Problem: /data/webfiles/ not labeled correctly
ls -Z /data/webfiles/
# system_u:object_r:default_t:s0 index.html  <- wrong!

# Fix: apply httpd_sys_content_t label:
semanage fcontext -a -t httpd_sys_content_t "/data/webfiles(/.*)?"
restorecon -Rv /data/webfiles/

# Verify:
ls -Z /data/webfiles/
# system_u:object_r:httpd_sys_content_t:s0 index.html  <- correct

# AppArmor troubleshooting:
# Find AppArmor denials:
grep apparmor /var/log/syslog | grep DENIED | tail -20
# apparmor="DENIED" operation="open" profile="docker-default"
# name="/proc/sys/kernel/ngroups_max" ...

# Check which profiles are active:
aa-status

# Profile location for Docker:
cat /etc/apparmor.d/docker-default | head -50

# Debug: run with complain mode:
aa-complain /etc/apparmor.d/usr.sbin.myapp
# All violations logged but not blocked
# Check: grep myapp /var/log/syslog

# Add missing rules (using aa-logprof):
aa-logprof   # reads /var/log/syslog, suggests additions
```

---

### Related Keywords

**Foundational:**
LNX-078 (Capabilities and seccomp), LNX-064 (Audit subsystem)

**Builds on this:**
LNX-080 (Container internals), LNX-108 (Multi-tenant security architecture)

**Related:**
LNX-071 (Namespaces), LNX-065 (PAM and authentication)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `getenforce` | SELinux mode: Enforcing/Permissive/Disabled |
| `setenforce 0/1` | Switch to permissive/enforcing (temp) |
| `ls -Z`, `ps auxZ` | Show SELinux context (files, processes) |
| `restorecon -Rv /path` | Fix SELinux file labels |
| `ausearch -m avc` | Show SELinux AVC denials |
| `audit2why`, `audit2allow` | Explain/generate SELinux policy |
| `getsebool -a` | List SELinux policy booleans |
| `aa-status` | AppArmor loaded profiles and modes |
| `aa-complain /path/to/binary` | Set AppArmor profile to log-only |
| `aa-logprof` | Generate profile updates from logs |

**3 things to remember:**
1. SELinux = label-based MAC (context on every file/process): use `ls -Z`, `restorecon`, `ausearch -m avc` for troubleshooting
2. AppArmor = path-based MAC (profiles per executable): use `aa-status`, `aa-logprof`, check `/var/log/syslog`
3. Never permanently disable SELinux/AppArmor - use permissive/complain mode to debug, then fix and re-enforce

---

### Transferable Wisdom

MAC vs DAC design maps to: database row-level security (policy-defined
data access vs table-owner permissions), IAM attribute-based access control
(ABAC: policy rules on attributes, like SELinux type enforcement), Kubernetes
RBAC (who can do what to which resources - same allow-rule model as SELinux).
The "label everything, define what labels can interact" pattern from SELinux
appears in: AWS resource tagging for IAM policies, Kubernetes network policy
(pod selectors = label matching), service mesh authorization policies
(Istio/Linkerd allow rules between service identities). The "permissive mode
for diagnosis" pattern: deploy with permissive first, collect violations,
fix policy, then enforce. This same pattern applies to: WAF rules (detection
mode before prevention mode), network security (IDS before IPS), API gateway
rate limiting (observe before enforce). `audit2allow` generating policy from
violations mirrors: Terraform import (derive config from existing state) and
learning firewall rules from traffic patterns. Platform engineers: Pod Security
Standards (Baseline/Restricted) enforce AppArmor/SELinux requirements.
`seccompProfile: RuntimeDefault` is the minimum; Restricted profile requires
it.

---

### The Surprising Truth

SELinux was developed by the NSA (National Security Agency) and open-sourced
in 2000 - the same organization that has been at the center of major
surveillance controversies. Yet SELinux's open-source release is widely
considered one of the most positive contributions to Linux security. The
NSA developed SELinux for their own classified systems, where the threat model
assumed even privileged insiders (administrators) might be adversarial or
compromised. This extreme threat model produced a system that is genuinely
over-engineered for most use cases (hence its reputation for being hard to
configure) but provides defense in depth at a level that few other open-source
security systems match. The irony: a system built to protect against the NSA's
own adversaries is now the default security module on every RHEL/Fedora/CentOS
system, protecting millions of organizations' servers - including systems
that might be targets of the very organization that created it.
A more practical surprising truth: AppArmor, despite being simpler and easier
to configure, achieves similar practical protection for most applications.
The "SELinux is too hard, use AppArmor" divide often comes down to the
difference between protecting against an insider threat model (SELinux) vs.
protecting against external attackers who compromise a service (AppArmor).
For most production web applications: both are adequate, and the choice is
mostly about which distribution you run.

---

### Mastery Checklist

- [ ] Can check SELinux mode (`getenforce`) and interpret AVC denials (`ausearch -m avc | audit2why`)
- [ ] Can fix SELinux file labels using `semanage fcontext` + `restorecon`
- [ ] Can use AppArmor `aa-status`, `aa-complain`, `aa-logprof`, `aa-enforce`
- [ ] Understands DAC vs MAC: why MAC is needed even with correct Unix permissions
- [ ] Knows Docker's LSM behavior: AppArmor `docker-default` profile (Ubuntu), SELinux `svirt_lxc_net_t` (RHEL)

---

### Think About This

1. A company moves a critical application from a VM to Docker on Ubuntu.
   The application starts failing with "Permission denied" errors on files
   it previously accessed without issue. The file permissions are identical
   (rwxr-xr-x, owned by root). Outline your complete diagnosis: what security
   layers could be causing this (AppArmor, capabilities, SELinux, file
   permissions, seccomp), the order you'd check them, and the specific
   commands for each. The company's security team says "just disable AppArmor"
   - respond with why that's wrong and what the correct approach is.

2. SELinux policy authoring: a new microservice needs to: (a) serve HTTP on
   port 8443, (b) connect to a PostgreSQL database on port 5432, (c) write
   to `/var/lib/myservice/data/`, (d) read certificates from `/etc/pki/myservice/`.
   Describe the SELinux approach: what type labels you'd create, what
   `semanage port` commands you'd run, and what allow rules the policy
   module would need. What existing SELinux types could you leverage vs.
   what would need to be custom?

3. Compare the security guarantees of: (a) a container with `--cap-drop=ALL
   --security-opt seccomp=strict.json` but no AppArmor/SELinux, vs. (b) a
   container with default AppArmor profile but no capability dropping or
   custom seccomp. Which is more secure and why? What would you use for a
   container processing untrusted user-submitted files (assume code execution
   risk is high)?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between DAC and MAC in Linux, and why do production systems need both?
A: DAC (Discretionary Access Control) and MAC (Mandatory Access Control) are complementary security models. DAC (traditional Unix permissions): the OWNER of a resource controls access. `chmod 640 /etc/myconfig` - owner decides who reads it. Weaknesses: (1) Root bypasses all DAC. (2) A compromised process running as the file owner can modify permissions to allow wider access. (3) DAC is decentralized - each user controls their own files, no system-wide policy enforcement. MAC (SELinux/AppArmor): a central POLICY controls access, regardless of file ownership. Even root cannot override MAC policy in enforcing mode (unless root changes the policy itself). Policy is defined by the system administrator, not individual users or processes. WHY BOTH ARE NEEDED: DAC handles the normal case - file ownership and permissions are the primary access control model. MAC handles the adversarial case - when a privileged process is compromised. EXAMPLE: Apache httpd runs as user `apache`. Apache has a vulnerability. DAC: attacker has full apache user privileges - can read/write any file apache can access, connect to any network destination. With SELinux: attacker has `httpd_t` context. Policy allows httpd_t to: read httpd_sys_content_t files (web content), write httpd_log_t files (logs), connect to http_port_t sockets (ports 80/443/8080). Policy BLOCKS: connecting to arbitrary ports (data exfiltration), reading shadow_t (password files), writing to system directories. The compromise is CONTAINED within what httpd_t is allowed to do - even if the attacker gains full apache user shell. This is defense in depth: DAC is the first layer, MAC is the second.

**Expert:**
Q: You're the security architect for a Kubernetes cluster running RHEL nodes with SELinux enforcing. A new application team wants to deploy a service that needs to access raw network sockets and mount NFS volumes. How do you approach this safely with SELinux?
A: This is a multi-part problem requiring careful SELinux policy work rather than just disabling protection. STEP 1 - UNDERSTAND REQUIREMENTS PRECISELY: "Raw network sockets" could mean several things - packet capture (CAP_NET_RAW + socket AF_PACKET), raw IP sockets, or DPDK-style userspace networking. "Mount NFS volumes" in containers could mean: use Kubernetes NFS PersistentVolumes (handled by the kubelet, no container capability needed) vs. running NFS client inside the container (requires CAP_SYS_ADMIN + kernel NFSv4 client). The correct answer always begins with minimizing what's actually needed. STEP 2 - SELinux CONTEXT FOR CONTAINERS: Container processes on RHEL run as `svirt_lxc_net_t` by default. For raw sockets: SELinux policy for `svirt_lxc_net_t` may not include `rawip_socket`, `packet_socket` access. Resolution: create a custom SELinux type (e.g., `packet_capture_container_t`) with a policy that allows the needed socket types. Apply this type to the specific container pod via SELinux options in the Pod spec: `securityContext.seLinuxOptions.type: packet_capture_container_t`. STEP 3 - NFS VOLUMES: Kubernetes handles NFS mounting at the node level (kubelet mounts the volume, container sees a pre-mounted directory). This requires no container-level capabilities. The mounted files need the correct SELinux context. Use the `:z` flag equivalent in Kubernetes volume mounts (SELinux relabeling). `securityContext.seLinuxOptions` on the PVC or inline volume spec to control how labels are applied to volume contents. STEP 4 - POLICY AUTHORING WORKFLOW: (1) Deploy in a dev namespace with SELinux permissive mode. (2) Run all code paths, collect AVC denials: `ausearch -m avc | audit2allow -M myservice`. (3) Review generated policy for overly broad rules. (4) Create a named SELinux policy module. (5) Test in staging with enforcing mode + custom policy. (6) Deploy to production. The alternative - just running `--privileged` or disabling SELinux for this workload - is wrong because it removes all isolation for a service that already has elevated requirements (raw sockets = potential for network attacks if compromised).
