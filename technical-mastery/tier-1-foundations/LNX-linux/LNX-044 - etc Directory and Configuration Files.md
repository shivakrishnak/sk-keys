---
id: LNX-044
title: "/etc Directory and Configuration Files"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-010
used_by: LNX-031, LNX-038
related: LNX-007, LNX-031, LNX-038
tags: [/etc, configuration, sshd_config, sudoers, fstab, hosts, nsswitch, resolv.conf]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/lnx/etc-directory/
---

## TL;DR

`/etc` contains system-wide configuration files (text files, root-editable).
Essential files: `/etc/passwd` and `/etc/shadow` (users), `/etc/group`
(groups), `/etc/hosts` (hostname-to-IP mapping), `/etc/resolv.conf` (DNS),
`/etc/fstab` (filesystems), `/etc/ssh/sshd_config` (SSH daemon), `/etc/sudoers`
(sudo rules - edit ONLY with `visudo`). Config files are plain text - use
`diff`, `git`, or configuration management (Ansible, Puppet) to track
changes. Changes usually require service restart to take effect.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-044 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | /etc, configuration files, sshd_config, sudoers, resolv.conf, hosts, nsswitch.conf |
| **Prerequisites** | LNX-007, LNX-010 |

---

### The Problem This Solves

You need to: allow a new user to use sudo (edit `/etc/sudoers` via `visudo`),
add a local hostname resolution (edit `/etc/hosts`), configure the SSH
daemon to disable root login (edit `/etc/ssh/sshd_config`, restart sshd).
Without knowing which config file controls which behavior, you'd search
for documentation every time. `/etc` is THE configuration hub for Linux
system administration.

---

### Textbook Definition

**/etc** (Etcetera, historically): The directory for host-specific system
configuration. Contains: text-based configuration files, application
configuration files (often in subdirectories), and system databases.
Files are read by daemons, system tools, and login processes.

**System daemon configuration pattern**: Daemon reads config at startup.
Config change -> restart daemon -> config applied. Some daemons support
reload (SIGHUP) to re-read without full restart.

**Drop-in directory pattern**: Modern services often support `/etc/service.d/*.conf`
(or similar) - a directory of override files. Override files are merged
with the main config. Allows packages to add config without editing the
main file (and avoiding conflicts on upgrades).

---

### Understand It in 30 Seconds

```bash
# === Key /etc files to know ===

# User and auth:
/etc/passwd          # user accounts (7 fields, world-readable)
/etc/shadow          # hashed passwords (root only)
/etc/group           # group definitions
/etc/sudoers         # sudo rules (ALWAYS edit with: visudo)
/etc/pam.d/          # PAM authentication configuration
/etc/security/limits.conf  # per-user resource limits

# Network:
/etc/hosts           # static hostname-to-IP mappings
/etc/resolv.conf     # DNS server configuration
/etc/nsswitch.conf   # name service switch (order of lookups)
/etc/hostname        # this machine's hostname
/etc/network/interfaces  # network config (Debian/Ubuntu older)
/etc/netplan/        # network config (Ubuntu 18+)
/etc/NetworkManager/ # NetworkManager config (desktop/RHEL)

# SSH:
/etc/ssh/sshd_config  # SSH daemon configuration
/etc/ssh/ssh_config   # SSH client defaults (all users)

# System services:
/etc/fstab           # filesystem mount table
/etc/crontab         # system-wide cron jobs
/etc/cron.d/         # per-package cron files
/etc/rc.local        # legacy startup script (may not exist)
/etc/systemd/        # systemd configuration and service overrides

# Package management:
/etc/apt/            # APT sources and config (Debian/Ubuntu)
/etc/yum.repos.d/    # YUM/DNF repos (RHEL/CentOS)

# Application examples:
/etc/nginx/          # nginx configuration
/etc/apache2/        # Apache configuration
/etc/mysql/          # MySQL configuration
/etc/java-*-openjdk/ # Java configuration

# View any config:
cat /etc/ssh/sshd_config
grep -v "^#" /etc/ssh/sshd_config | grep -v "^$"  # non-comment lines only

# Show differences from default (using dpkg on Debian):
dpkg --verify | grep -v "^$"    # shows modified package files

# Safely edit sudoers (NEVER use regular editor!):
visudo                          # validates before saving
visudo -f /etc/sudoers.d/myapp  # edit a sudoers drop-in

# Apply sshd changes:
sshd -t                         # test config syntax before restarting
systemctl reload sshd           # or: restart sshd
```

---

### First Principles

**Why /etc is text files:**
Text files are human-readable, versionable with git, auditable with diff,
transferable across machines (copy or automation). The Unix philosophy:
"configure via text, not binary." Every config change in `/etc` is a
text edit that can be reviewed and reverted.

**Key config file patterns:**
```
1. Key=Value (INI-like):
   # /etc/ssh/sshd_config
   Port 22
   PermitRootLogin no
   PasswordAuthentication no
   MaxAuthTries 3

2. Colon-delimited records:
   # /etc/passwd
   username:x:uid:gid:comment:home:shell

3. Tab/space delimited:
   # /etc/hosts
   127.0.0.1   localhost
   10.0.0.5    app-server app-server.example.com

4. Directive-based (nginx, Apache):
   # /etc/nginx/nginx.conf
   server {
       listen 80;
       server_name example.com;
   }

5. Drop-in directories (config.d/ pattern):
   /etc/sudoers.d/   <- each file adds sudo rules
   /etc/apt/sources.list.d/  <- each file adds APT sources
   /etc/cron.d/      <- each file adds cron jobs
   /etc/profile.d/   <- each script runs at login
```

---

### Thought Experiment

Systematically securing a newly provisioned server by editing /etc:

```bash
# /etc/ssh/sshd_config changes:
# 1. Disable root login:
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
# 2. Disable password auth (after adding your key!):
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' \
    /etc/ssh/sshd_config
# 3. Limit users who can SSH:
echo "AllowUsers deploy ubuntu" >> /etc/ssh/sshd_config
# 4. Validate and restart:
sshd -t && systemctl reload sshd

# /etc/hosts: add hostname resolution for private services
cat >> /etc/hosts << 'EOF'
10.0.0.10  database database.internal
10.0.0.11  cache cache.internal
10.0.0.12  logging logging.internal
EOF

# /etc/resolv.conf: configure DNS with fallback
cat > /etc/resolv.conf << 'EOF'
nameserver 10.0.0.2
nameserver 8.8.8.8
search internal.example.com example.com
options timeout:2 attempts:3
EOF

# /etc/security/limits.conf: raise file descriptor limits for app
cat >> /etc/security/limits.conf << 'EOF'
appuser soft nofile 65536
appuser hard nofile 65536
EOF

# /etc/sudoers.d/deploy (via visudo -f):
# deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart myapp
```

---

### Mental Model / Analogy

```
/etc = the company's policy binder
       (all the rules and settings for how everything works)

Each file = a specific policy document:
  /etc/passwd = employee roster
  /etc/shadow = HR's secure vault (credentials)
  /etc/sudoers = authorization list (who can do what)
  /etc/hosts = internal phone directory (names -> IPs)
  /etc/resolv.conf = "which directory service to call for lookups"
  /etc/fstab = storage allocation plan (which disk goes where)
  /etc/ssh/sshd_config = door policy (who can enter, how)

Editing rules:
  - Most files: any text editor works
  - sudoers: MUST use visudo (validates before saving)
    (like requiring HR approval for policy changes)
  - Most changes: restart the service after editing
    (like re-briefing security after updating the policy)

Drop-in directories (/etc/nginx/conf.d/, /etc/sudoers.d/):
  = annexes to the main policy document
    (departments can add their own rules without rewriting the whole thing)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Know: `/etc/hosts` (add hostname), `/etc/sudoers` (use `visudo`!),
`/etc/ssh/sshd_config` (configure SSH), `/etc/resolv.conf` (DNS).
These are the most commonly edited files in day-to-day admin. Editing
rule: always backup before editing (`cp file file.bak`).

**Level 2:**
`/etc/nsswitch.conf`: controls lookup order (hosts: files dns = check
/etc/hosts THEN DNS). `/etc/pam.d/`: PAM modules for authentication.
`/etc/profile` and `/etc/profile.d/`: system-wide environment variables
(for login shells). `/etc/environment`: environment for all processes
(non-shell). Drop-in pattern: `/etc/sudoers.d/`, `/etc/cron.d/`.

**Level 3:**
`/etc/sysctl.conf` and `sysctl.d/`: kernel parameter tuning (applied at
boot with `sysctl -p`). `/etc/systemd/system/`: systemd unit override
files. `systemctl edit servicename` creates overrides in
`/etc/systemd/system/servicename.d/override.conf`. `/etc/logrotate.conf`
and `/etc/logrotate.d/`: log rotation configuration. `/etc/default/`:
Debian's default values for init scripts.

**Level 4:**
`/etc/ld.so.conf` and `/etc/ld.so.conf.d/`: shared library search paths
(run `ldconfig` after changes). `/etc/hosts.deny` and `/etc/hosts.allow`:
TCP wrappers (legacy, many services still check these). `/etc/iptables/rules.v4`:
saved iptables rules (applied by iptables-persistent). `/etc/audit/auditd.conf`:
Linux audit daemon config.

**Level 5:**
Configuration drift: `/etc` files diverging from desired state across
servers. Solution: configuration management (Ansible, Puppet, Chef) tracks
desired state and enforces it. Immutable infrastructure: don't edit `/etc`
directly in production - use image builds (Packer), version control config,
apply with automation. Cloud-init: `/etc/cloud/` stores cloud-init config
that runs at first boot to configure the system from metadata. HashiCorp
Consul-Template: writes to files in `/etc/` based on service discovery
data, enabling dynamic configuration.

---

### Code Example

**BAD - /etc editing mistakes:**
```bash
# BAD 1: Editing sudoers with a regular editor:
nano /etc/sudoers    # NEVER do this
vim /etc/sudoers     # ALSO NEVER do this
# If you make a syntax error: sudo BREAKS for everyone!
# You might lock yourself out of sudo entirely.

# GOOD: ALWAYS use visudo:
visudo               # validates before saving, prevents lockout

# BAD 2: Editing resolv.conf directly on systemd systems:
echo "nameserver 8.8.8.8" > /etc/resolv.conf
# NetworkManager and systemd-resolved may overwrite this on network restart!

# Check if it's managed:
ls -la /etc/resolv.conf   # might be a symlink
# Debian/Ubuntu with systemd-resolved:
# /etc/resolv.conf -> ../run/systemd/resolve/stub-resolv.conf

# GOOD: configure the actual manager:
# For systemd-resolved:
cat > /etc/systemd/resolved.conf << 'EOF'
[Resolve]
DNS=8.8.8.8 8.8.4.4
FallbackDNS=1.1.1.1
Domains=~.
EOF
systemctl restart systemd-resolved

# BAD 3: Editing sshd_config without testing:
vim /etc/ssh/sshd_config
systemctl restart sshd    # if config has syntax error: sshd won't start
                          # and you might be locked out!

# GOOD: test config before restarting:
sshd -t                   # test configuration syntax
# If output is blank: config is valid
# If error: fix before restarting
systemctl restart sshd    # restart only if -t passed
```

**GOOD - auditing and managing /etc changes:**
```bash
# Track /etc changes with git (useful for audit trail):
cd /etc
git init
git add -A
git commit -m "Initial /etc state - $(hostname)"

# Now every change is tracked:
vim /etc/ssh/sshd_config
git diff /etc/ssh/sshd_config  # see what changed
git add /etc/ssh/sshd_config
git commit -m "sshd_config: disable root login and password auth"

# View change history:
git log --oneline /etc/ssh/sshd_config

# Compare current state to a previous known-good state:
git diff HEAD~5 /etc/

# Find files modified recently (possible unauthorized changes):
find /etc -newer /etc/passwd -type f | head -20
# Shows files newer than /etc/passwd (proxy for "recently modified")

# Or: find files modified in last 24 hours:
find /etc -mtime -1 -type f 2>/dev/null

# Validate key config files:
sshd -t                      # sshd_config syntax
nginx -t                     # nginx config syntax
apache2ctl configtest        # apache syntax
visudo -c                    # sudoers syntax check
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`/etc/resolv.conf` always controls DNS" | On modern systems, `/etc/resolv.conf` may be a symlink managed by `systemd-resolved` or `NetworkManager`. Editing it directly may be overwritten at next network event. Check `ls -la /etc/resolv.conf` - if it's a symlink, configure the owning service instead. |
| "Any editor can edit any file in /etc" | Most files: yes. But `/etc/sudoers` MUST be edited with `visudo` because it validates syntax before saving. A syntax error in sudoers breaks `sudo` for everyone. `visudo` prevents saving an invalid file, protecting you from lockout. |
| "/etc/hosts takes precedence over DNS" | Depends on `/etc/nsswitch.conf`. Typical value: `hosts: files dns`. This means check `/etc/hosts` FIRST, then DNS. But this is configurable - it could be `hosts: dns files` (DNS first) or other combinations. `/etc/hosts` is NOT always first. |
| "Editing /etc immediately applies changes" | Most services READ their config at startup and don't re-read unless signaled or restarted. Editing `/etc/nginx/nginx.conf` has NO effect until `systemctl reload nginx` or `nginx -s reload`. The exception: some files are read on each access (`/etc/hosts`, `/etc/resolv.conf` - checked by the resolver library on each DNS lookup). |
| "/etc is the only place to configure services" | Applications also use: `~/.config/` (user-specific), `/usr/share/` (defaults), `/var/lib/` (runtime state), environment variables, command-line arguments, and cloud metadata. `/etc` is the SYSTEM-WIDE config for multi-user settings. User-specific settings go in home directories. |

---

### Failure Modes & Diagnosis

**sudo broken after bad sudoers edit:**
```bash
# Symptom: sudo gives ">>> /etc/sudoers: syntax error near line N <<<"
# And: "sudo: no valid sudoers sources found, quitting"

# You cannot use sudo to fix it (sudo is broken)!

# Option 1: switch to root via su (if root password is known):
su -          # enter root password
visudo        # fix the syntax error

# Option 2: boot into recovery/single-user mode:
# At GRUB: select "Advanced options" -> "recovery mode"
# Choose "root" in recovery menu
# mount -o remount,rw /    # make root writable
# visudo -f /etc/sudoers   # fix sudoers

# Option 3: if using pkexec (PolicyKit) as alternative:
pkexec visudo   # uses PolicyKit instead of sudo

# Prevention: NEVER edit sudoers with anything other than visudo
# Prevention: add a drop-in file in /etc/sudoers.d/ rather than editing
# the main sudoers (less risk - you can delete the drop-in if broken)
```

**sshd won't start after config change:**
```bash
# Symptom: systemctl restart sshd fails, locked out of SSH

# FIRST: don't close your current SSH session!
# If you still have an active session, use it to fix the issue

# Check syntax:
sshd -t 2>&1
# Shows the syntax error and line number

# Check journal for error details:
journalctl -xe -u sshd | tail -20

# Fix the config:
vim /etc/ssh/sshd_config   # fix the error on the reported line
sshd -t                     # verify fix
systemctl start sshd        # start again

# Prevention: ALWAYS run 'sshd -t' before restarting sshd
# Prevention: Keep your current session open while testing
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-010 (Permissions)

**Builds on this:**
LNX-031 (systemd), LNX-038 (User Management)

**Related:**
LNX-041 (SSH Keys), LNX-039 (Mounting Filesystems)

---

### Quick Reference Card

| File | Purpose |
|------|---------|
| `/etc/passwd` | User account database |
| `/etc/shadow` | Password hashes (root only) |
| `/etc/group` | Group definitions |
| `/etc/sudoers` | sudo rules (edit with visudo!) |
| `/etc/hosts` | Static name-to-IP mappings |
| `/etc/resolv.conf` | DNS server configuration |
| `/etc/nsswitch.conf` | Name service lookup order |
| `/etc/ssh/sshd_config` | SSH daemon settings |
| `/etc/fstab` | Filesystem mount table |
| `/etc/hostname` | System hostname |

**3 things to remember:**
1. ALWAYS use `visudo` to edit `/etc/sudoers` (never vim/nano directly)
2. Config changes need service restart to take effect: `sshd -t && systemctl reload sshd`
3. `/etc/resolv.conf` may be managed by systemd-resolved - check if it's a symlink first

---

### Transferable Wisdom

The `/etc` pattern appears in: Docker containers (`/etc` in container image),
Kubernetes ConfigMaps (mounted into `/etc/` inside pods as config files),
Ansible (tasks that template files into `/etc/`), Terraform (cloud-init
templates write to `/etc/`), Packer (base image builds configure `/etc/`).
Configuration management at scale = managing what goes in `/etc/` across
hundreds of servers. Ansible's `template` module writes Jinja2-rendered
templates to `/etc/` files on remote hosts.

The "edit config, restart service" pattern appears as: `kubectl apply -f`
for Kubernetes resources (apply = restart/reconcile), Helm chart values
(templates rendered to config files), Terraform resource changes (update
= restart managed service), Spring Boot application.properties (read at
startup, require restart to change).

---

### The Surprising Truth

`/etc` doesn't stand for "etcetera" in the original Unix meaning - it was
intended as the directory for things that "don't belong elsewhere." The
"et cetera" meaning came later as folk etymology. In early Unix systems,
`/etc` contained miscellaneous host-specific data (configuration AND
administrative programs). The FHS eventually formalized it as "host-specific
system configuration" only (programs moved to `/usr/sbin` and `/sbin`).
The practice of git-tracking `/etc` has a long history: "etckeeper" is a
package specifically for this purpose - it automatically commits changes
to `/etc` (including package installs that modify configs), integrates
with apt/yum hooks, and supports multiple VCS backends. Security teams
use etckeeper (or AIDE, Tripwire) to detect unauthorized changes to
`/etc` - a common indicator of compromise.

---

### Mastery Checklist

- [ ] Knows the purpose of 10 key files in /etc
- [ ] Can edit sudoers safely with visudo
- [ ] Can add a static hostname in /etc/hosts
- [ ] Can configure SSH daemon settings and test before restarting
- [ ] Understands the drop-in directory pattern for config overrides

---

### Think About This

1. You add `10.0.0.5 database.internal` to `/etc/hosts`. But your
   application still resolves `database.internal` via DNS (getting the
   old IP). You confirm with `cat /etc/hosts` that the entry is there.
   What does `/etc/nsswitch.conf` have to do with this, and how would
   you verify the lookup order being used?

2. You make changes to `/etc/sysctl.conf` to tune kernel parameters.
   After saving, you run `sysctl -p` - the changes appear applied.
   After a reboot, they're gone. Why? What is the correct path to
   place sysctl configuration files that will persist? (Hint: there's
   a drop-in directory convention.)

3. Why does `/etc/sudoers` require `visudo` while `/etc/ssh/sshd_config`
   can be edited with any editor? What protection does `visudo` provide
   that can't be reproduced by "be careful when editing"? What happens
   if your text editor crashes mid-save on a sudoers file?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the role of /etc/nsswitch.conf and how does it affect hostname resolution?
A: `/etc/nsswitch.conf` (Name Service Switch) configures the ORDER and SOURCES for various system lookups - not just hostnames, but also user lookups, group lookups, shadow passwords, etc. The `hosts:` line controls hostname resolution order. Typical value: `hosts: files dns`. This means: (1) Check `/etc/hosts` first (files). If found, use that IP. (2) If not in /etc/hosts, query DNS servers in `/etc/resolv.conf`. Alternative: `hosts: dns files` (DNS first, then /etc/hosts - less common). Or: `hosts: files mdns4_minimal [NOTFOUND=return] dns` (Ubuntu with mDNS). Impact on your question: if your `/etc/hosts` has `10.0.0.5 database.internal` but `/etc/nsswitch.conf` has `hosts: dns files`, DNS is checked FIRST. If DNS returns a different IP for `database.internal`, the /etc/hosts entry is never consulted. Diagnosis: `getent hosts database.internal` shows what the system resolves it to (uses nsswitch, not just /etc/hosts). `host database.internal` queries DNS directly (bypasses /etc/hosts). The difference shows you which lookup source is being used.

**Intermediate:**
Q: You need to give a CI/CD system user the ability to restart a specific systemd service using sudo, without a password, on 20 servers. How do you implement this securely?
A: Use the `/etc/sudoers.d/` drop-in directory for least-privilege sudo access: (1) Create `/etc/sudoers.d/cicd-deploy` with `visudo -f /etc/sudoers.d/cicd-deploy`. Content: `deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart myapp, /usr/bin/systemctl start myapp, /usr/bin/systemctl stop myapp`. This grants the `deploy` user ONLY the ability to restart/start/stop the specific `myapp` service. Why drop-in file? Safer: a syntax error only breaks this file (the main sudoers still works). Can be deleted if wrong. Packaged with your config management. Idempotent with Ansible. (2) Deploy with Ansible to all 20 servers: `ansible-playbook -i inventory deploy_sudoers.yml`. Task: `template: src=cicd-deploy.j2 dest=/etc/sudoers.d/cicd-deploy mode=0440 validate='visudo -cf %s'`. The `validate` parameter ensures Ansible runs `visudo -c` on the file before deploying it - won't deploy invalid sudoers. (3) Permissions: sudoers drop-ins must be `0440` (root:root, no write by group/others). Ansible sets this. (4) Verify: `ssh deploy@server "sudo /usr/bin/systemctl restart myapp"`. (5) Audit: review `/var/log/auth.log` for `sudo` entries to confirm only expected commands are run.

**Expert:**
Q: How do modern configuration management systems like Ansible differ from directly editing /etc, and what are the implications for infrastructure security?
A: Direct /etc editing has three problems: (1) No audit trail: who changed what and when? (2) Configuration drift: one server's /etc diverges from others over time. (3) No version control: can't revert to previous state. Ansible (and Puppet, Chef, etc.) solve these: (1) Declarative state: you define WHAT the config should be, not HOW to change it. Ansible's `template` module renders a Jinja2 template and writes it to `/etc/nginx/nginx.conf`, ensuring it ALWAYS matches the template. Re-running the playbook is idempotent - no change if already correct. (2) Version control: playbooks and templates are in git. Every config change is a git commit. (3) Audit: Ansible logs every change (Ansible Tower/AWX provides UI). (4) Scale: apply the same config to 100 servers simultaneously. Security implications: (1) Separation of duties: developers don't need SSH access to edit configs - they submit pull requests to the config repo. (2) Policy as code: security requirements encoded in Ansible roles (e.g., always set `PasswordAuthentication no`). (3) Drift detection: Ansible in check mode (`--check`) reports if any server has drifted from desired state. (4) Secret management: Ansible Vault encrypts secrets in the repository. HashiCorp Vault integration: secrets injected at deploy time, never stored in /etc as plaintext. (5) Change control: all /etc changes go through git PR review, CI testing, and controlled deployment - same process as application code. The gold standard: immutable infrastructure where /etc is never edited after boot (all config via cloud-init or user data), with complete image rebuilds for changes.
