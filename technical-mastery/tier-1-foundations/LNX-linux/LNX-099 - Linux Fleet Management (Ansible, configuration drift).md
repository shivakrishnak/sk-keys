---
id: LNX-099
title: "Linux Fleet Management (Ansible, configuration drift)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-055, LNX-098
used_by: LNX-100
related: LNX-055, LNX-098, LNX-100
tags: [ansible, fleet-management, configuration-management, configuration-drift, idempotency, playbook, inventory, chef, puppet, saltstack, osquery, push-pull-model, golden-image, in-place-update, rolling-update, canary-deployment, inspec, serverspec, node-exporter, prometheus, infrastructure-as-code, immutable-infrastructure]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 99
permalink: /technical-mastery/lnx/linux-fleet-management/
---

## TL;DR

Fleet management is the discipline of keeping many Linux servers in a defined,
consistent state. The core problem: one manual change on one server creates
**configuration drift** - servers diverge from the baseline and from each
other. Solution: infrastructure-as-code tools like **Ansible** (agentless,
push-based, SSH), **Puppet/Chef** (agent-based, pull-based), or
**SaltStack** (agent or agentless). Key principle: **idempotency** - running
a configuration tool 10 times produces the same result as running it once
(no "double installation" side effects). `ansible all -m ping` to verify
connectivity; `ansible-playbook site.yml --check` for dry-run. Configuration
drift detection: `osquery` for SQL-based fleet queries
(`SELECT * FROM users WHERE uid=0`), InSpec for compliance testing.
At scale: golden images (immutable base) plus IaC for configuration = most
reliable pattern.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-099 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | fleet management, Ansible, configuration drift, idempotency, Puppet, Chef, osquery, InSpec |
| **Prerequisites** | LNX-055 (systemd services), LNX-098 (NFS) |

---

### The Problem This Solves

**Problem 1**: An organization has 50 application servers. A junior admin runs
`yum install -y openssl-legacy` on two of them to fix a bug. Six months later,
a security audit finds these two servers running a version of OpenSSL not in
the approved baseline. Three servers have a different sudoers configuration
from a forgotten temporary change. Without fleet management: audit takes 2
days, fixing takes 1 day, and drift starts accumulating again immediately.
With Ansible: `ansible-playbook security-baseline.yml` runs against all 50
servers and brings every one to the defined baseline in 20 minutes. Drift is
corrected automatically, and the corrective action is logged.

**Problem 2**: A new compliance requirement mandates that all production servers
must have SSH PasswordAuthentication disabled, specific audit rules active,
and a particular kernel parameter set. Without fleet management: SSH to each
server, make the change, document it. At 200 servers: 6+ hours of work with
high error rate. With Ansible: write the task once, test in staging, run against
all 200 production servers in parallel. Consistent, auditable, repeatable.

---

### Textbook Definition

**Configuration Management**: The discipline of maintaining a system's
configuration in a defined, known state over time. In Linux operations: ensuring
that software versions, configuration files, user accounts, services, kernel
parameters, and filesystem permissions match a defined baseline on all servers.

**Configuration Drift**: The gradual divergence of system configuration from
its defined baseline, caused by ad-hoc changes, manual interventions, failed
updates, or time.

**Idempotency**: A property of operations where running the operation multiple
times has the same effect as running it once. Essential for configuration
management: `yum install -y nginx` on a server that already has nginx
installed does nothing (idempotent). Running a shell script that always runs
`useradd` is NOT idempotent: fails with "user already exists" on the second run.

**Push vs Pull model:**
| Model | How it works | Tools |
|-------|-------------|-------|
| Push | Central system pushes config to nodes | Ansible, Salt (push mode) |
| Pull | Nodes periodically fetch config from master | Puppet, Chef, Salt (pull mode) |

---

### Understand It in 30 Seconds

```bash
# === Ansible: agentless fleet management via SSH ===

# 1. Inventory: list of servers to manage
cat /etc/ansible/hosts
# [webservers]
# web01.example.com
# web02.example.com
# web03.example.com
#
# [dbservers]
# db01.example.com
# db02.example.com
#
# [all:vars]
# ansible_user=deployer
# ansible_ssh_private_key_file=~/.ssh/deploy_key

# 2. Ad-hoc commands: immediate single-operation execution
ansible all -m ping  # test connectivity to all hosts
# web01.example.com | SUCCESS => {"ping": "pong"}
# web02.example.com | SUCCESS => {"ping": "pong"}
# ...

ansible webservers -m shell -a "systemctl status nginx"  # check nginx status
ansible all -m command -a "uname -r"  # kernel version on all hosts
ansible all -m yum -a "name=openssl state=latest"  # update openssl on all

# 3. Playbook: structured, repeatable configuration
cat nginx-setup.yml
# ---
# - name: Configure web servers
#   hosts: webservers
#   become: yes  # sudo
#   tasks:
#     - name: Install nginx
#       yum:
#         name: nginx
#         state: present  # present = install if not already installed (idempotent!)
#     
#     - name: Configure nginx
#       template:
#         src: nginx.conf.j2    # Jinja2 template
#         dest: /etc/nginx/nginx.conf
#         owner: root
#         group: root
#         mode: '0644'
#       notify: Restart nginx   # trigger handler on change
#     
#     - name: Enable nginx
#       systemd:
#         name: nginx
#         enabled: yes
#         state: started
#   
#   handlers:
#     - name: Restart nginx
#       systemd:
#         name: nginx
#         state: restarted
#       # handler only runs IF "Configure nginx" task made a change

# Run playbook:
ansible-playbook nginx-setup.yml
# PLAY [Configure web servers] *****
# TASK [Install nginx] *** ok: [web01] (no change, already installed)
# TASK [Configure nginx] *** changed: [web02] (config file updated)
# TASK [Enable nginx] *** ok: [web01] ok: [web02] (already running)
# RUNNING HANDLER [Restart nginx] *** changed: [web02] (restarted after config change)

# Dry run (check mode - no changes made):
ansible-playbook nginx-setup.yml --check

# Run against specific host or group:
ansible-playbook nginx-setup.yml --limit web01.example.com

# === Configuration drift detection ===

# Option 1: Ansible --check shows what has drifted:
ansible-playbook security-baseline.yml --check
# TASK [Disable PasswordAuthentication] changed: [db01.example.com]
# ^ db01 has drifted! This task would make a change (meaning it's not in baseline)

# Option 2: osquery - SQL queries across the fleet:
# osquery is installed as a daemon (osqueryd) on each host
# Centrally query all hosts with osctrl or Fleet Device Management

# Example osquery queries:
osqueryi "SELECT * FROM users WHERE uid=0"
# uid | gid | username | description | directory | shell
# 0   | 0   | root     | root        | /root     | /bin/bash
# 0   | 0   | attacker |             | /home/att | /bin/bash  <- ALERT!

osqueryi "SELECT name, version FROM packages WHERE name='openssl'"
# name    | version
# openssl | 1.1.1-21  <- is this the approved version?

osqueryi "SELECT value FROM system_controls WHERE name='net.ipv4.ip_forward'"
# value
# 1  <- ip_forward enabled, should be 0 for non-router!

# Option 3: InSpec compliance testing
cat check-ssh.rb
# control 'ssh-config' do
#   title 'SSH server configuration'
#   describe sshd_config do
#     its('PasswordAuthentication') { should eq 'no' }
#     its('PermitRootLogin') { should eq 'no' }
#     its('Protocol') { should eq '2' }
#   end
# end

inspec exec check-ssh.rb -t ssh://root@server
# Profile: SSH Configuration (check-ssh)
# Test Summary: 3 successful, 0 failures <- all controls pass
```

---

### First Principles

```
Why manual server management doesn't scale:

Single server (1 server): manual changes are fine
  - SSH in, make change, done
  - You remember what you changed
  - If something breaks: you know where to look

10 servers: still manageable but showing strain
  - Must SSH to each one individually
  - Easy to make mistakes on one server but not another
  - Documentation burden: must write down what you changed on each

50-100 servers: manual is broken
  - A single "emergency fix" SSH session on one server creates drift
  - Forgot which servers got which changes
  - Security audit: cannot prove servers are in compliance
  - New server provisioning: manual setup takes hours, inconsistent

1000+ servers: only automation works
  - Human cannot physically SSH to 1000 servers
  - Changes must be versioned, testable, reviewable
  - Drift detection must be automated
  - Rollback must be possible (and fast)

Infrastructure-as-Code (IaC) solution:
  Define desired state in code (playbooks, manifests, recipes)
  Code is: version-controlled (git), reviewed (pull requests),
           tested (dry-run, staging environment),
           auditable (git log shows every change)
  
  Configuration tool applies desired state to servers:
  "Make server look like this" not "run these commands"
  
  Desired state example (Ansible):
    yum: name=nginx state=present  <- "nginx should be installed"
    systemd: name=nginx state=started  <- "nginx should be running"
    
  NOT imperative: "install nginx with yum, then start it with systemctl"
  DECLARATIVE: "nginx should be in state: installed and running"
  
  Idempotency means:
  Running the same playbook again: NO changes if server already matches
  Running it after a change: ONLY the changed tasks show "changed"
  
Push model (Ansible):
  1. Admin runs: ansible-playbook site.yml
  2. Ansible SSH's to each server
  3. Uploads Python modules, runs tasks, returns results
  4. All changes happen NOW, under admin's control
  
  Advantages: simple, no agent, SSH is universal
  Disadvantages: central node must reach all servers, SSH credentials
                 must be distributed, no continuous enforcement

Pull model (Puppet/Chef):
  1. Agent runs every 30 minutes on each server
  2. Agent contacts Puppet/Chef master: "what should I look like?"
  3. Master sends catalog: desired state for THIS server
  4. Agent applies catalog, reports changes back to master
  
  Advantages: continuous enforcement, auto-correction of drift,
              scales to 10,000+ nodes, no need for central SSH access
  Disadvantages: agent must be installed and running, master is
                 critical infrastructure, more complex setup

SaltStack hybrid:
  Master/minion architecture (like Puppet)
  Minion installed on each server (like Puppet)
  BUT: can also push commands immediately (like Ansible ad-hoc)
  salt '*' cmd.run 'systemctl restart nginx'  # push to all NOW
  salt '*' state.apply  # apply desired state (pull behavior)

Drift detection approaches:
  1. Periodic re-apply (Ansible cron): 
     Run playbook every hour with --check, alert on changes
     
  2. Pull model (Puppet/Chef): built-in, agents report drift
  
  3. osquery: SQL queries on OS data (processes, packages,
     network connections, file attributes, users)
     Runs locally, reports to central dashboard
     Can detect: unexpected users (uid=0), new processes,
                 changed file hashes, new listening ports
     
  4. AIDE (file integrity): tracks file changes on disk
     Good for: detecting file changes after deployment
     Limitation: must run actively to detect (not real-time)
```

---

### Thought Experiment

Building a fleet management baseline for 200 servers:

```bash
# === Initial discovery: what is the current state? ===

# Create Ansible inventory from existing DNS/CMDB:
cat > inventory.ini << 'EOF'
[webservers]
web[01:50].example.com

[appservers]
app[01:100].example.com

[dbservers]
db[01:50].example.com

[all:vars]
ansible_user=ansible-svc
ansible_ssh_private_key_file=/home/ansible/.ssh/id_ed25519
EOF

# Discovery playbook: find current state, output to report
ansible all -m setup --tree /tmp/facts/  # gather all facts
# Creates one JSON file per host with: OS version, packages, users, ...

# Check: which servers have unexpected root SSH logins?
ansible all -m shell \
    -a "grep '^PermitRootLogin yes' /etc/ssh/sshd_config" \
    --one-line 2>/dev/null
# app03.example.com | CHANGED | PermitRootLogin yes  <- drifted!

# Check: which servers have wrong OpenSSL version?
ansible all -m shell -a "openssl version" --one-line | \
    grep -v "OpenSSL 1.1.1k"  # show servers NOT on approved version

# === Baseline playbook (security-baseline.yml) ===
cat security-baseline.yml
# ---
# - name: Security Baseline
#   hosts: all
#   become: yes
#   vars:
#     approved_openssl: "openssl-1.1.1k"
#     ntp_servers:
#       - 169.254.169.123  # AWS time sync service
#
#   tasks:
#     - name: Ensure SSH PasswordAuthentication disabled
#       lineinfile:
#         path: /etc/ssh/sshd_config
#         regexp: '^PasswordAuthentication'
#         line: 'PasswordAuthentication no'
#         state: present
#       notify: Restart sshd
#
#     - name: Ensure PermitRootLogin disabled
#       lineinfile:
#         path: /etc/ssh/sshd_config
#         regexp: '^PermitRootLogin'
#         line: 'PermitRootLogin no'
#         state: present
#       notify: Restart sshd
#
#     - name: Set kernel parameters (sysctl)
#       sysctl:
#         name: "{{ item.name }}"
#         value: "{{ item.value }}"
#         state: present
#         reload: yes
#       loop:
#         - { name: 'kernel.dmesg_restrict', value: '1' }
#         - { name: 'net.ipv4.conf.all.rp_filter', value: '1' }
#
#     - name: Install approved OpenSSL
#       yum:
#         name: "{{ approved_openssl }}"
#         state: present
#
#     - name: Configure NTP
#       template:
#         src: chrony.conf.j2
#         dest: /etc/chrony.conf
#       notify: Restart chronyd
#
#   handlers:
#     - name: Restart sshd
#       systemd: name=sshd state=restarted
#     - name: Restart chronyd
#       systemd: name=chronyd state=restarted

# === Rolling deployment: update 200 servers safely ===
# serial: deploy to N servers at a time, stop if failures exceed threshold
ansible-playbook security-baseline.yml \
    --serial 10% \           # update 10% (20 servers) at a time
    --max-fail-percentage 10  # abort if >10% of batch fails

# Canary deployment: deploy to 1 server first, test, then rest
ansible-playbook security-baseline.yml \
    --limit web01.example.com   # first: single server
# Verify manually...
ansible-playbook security-baseline.yml \
    --limit webservers  # then: all web servers

# === Continuous drift detection with osquery ===

# Install osquery on all hosts:
ansible all -m yum -a \
    "name=osquery state=present enablerepo=osquery"

# Query for unexpected SUID binaries:
osqueryi "
SELECT path, username, mode
FROM file
JOIN users ON file.uid = users.uid
WHERE mode LIKE '%s%'
  AND path NOT LIKE '/usr/bin/%'
  AND path NOT LIKE '/bin/%'
"
# Reports: /tmp/shell with SUID bit (attacker backdoor!)

# Query for unexpected listening ports:
osqueryi "
SELECT pid, port, protocol, processes.name
FROM listening_ports
JOIN processes USING (pid)
WHERE address != '127.0.0.1'
  AND port NOT IN (22, 80, 443, 3306, 5432)
"
# Reports unexpected services listening on network interfaces
```

---

### Mental Model / Analogy

```
Fleet management = franchise restaurant standards

Individual restaurant (single server): 
  Chef makes their own decisions about recipes, temperatures, portions
  Consistent within this restaurant, but unique to this kitchen
  
10 restaurants (10 servers, no fleet management):
  Each chef interprets the menu differently
  Health inspector finds different temperatures in different kitchens
  Customer gets different experience at different locations
  "Configuration drift" = chef on night shift changed the recipe
  
Franchise system (Ansible/Puppet/Chef):
  Corporate sends the standard recipe book (playbook/manifest/recipe)
  Every restaurant receives the same specifications
  Periodically: corporate sends updated standards
  Deviation from standards triggers corrective action
  
Push model (Ansible) = franchise auditor visits:
  Scheduled inspection: "Today we're visiting all 50 locations"
  Auditor arrives, checks against standards, corrects deviations
  Between visits: drift can occur (chef on night shift still changes things)
  
Pull model (Puppet) = kitchen assistant checks standards every 30 minutes:
  Every 30 minutes: consult the recipe book, correct any deviations
  Night shift chef changes recipe: 30 minutes later it's corrected
  Much faster drift correction, but requires the "assistant" (agent)
  
Idempotency = recipe book entries:
  "If oven is not at 350F, set it to 350F"
  NOT: "Turn oven dial to the right 3 times"
  Idempotent: checking when oven is already 350F does nothing
  Not idempotent: turning the dial right 3 times moves it EACH time you check
  
Drift detection (osquery) = surprise health inspection:
  SQL queries = very specific questions: "Show me EVERY kitchen with temperature != 350F"
  Answers are objective, machine-verifiable, consistent
  Traditional audit = someone remembers what they saw last time
  osquery audit = SQL database of current system state
  
Rolling update = updating franchise menu items:
  Don't change all 500 locations simultaneously
  Start with 1 location: verify customers like new dish
  Then 10 locations (canary group)
  Then all remaining locations in batches of 50
  Stop if complaints exceed threshold (--max-fail-percentage)
```

---

### Gradual Depth - Five Levels

**Level 1:**
What configuration management is and why it matters. Ansible basics: inventory,
ad-hoc commands, ping. What a playbook looks like. Idempotency concept. Push
vs pull distinction. `ansible-playbook --check` for dry-run.

**Level 2:**
Ansible roles and playbook structure. Handlers for conditional service restarts.
Jinja2 templates for configuration files. Ansible variables and group_vars.
`ansible-lint` for playbook quality. `serial` for rolling deployments. Puppet/Chef
at conceptual level. Configuration drift definition. `osquery` for basic queries.

**Level 3:**
Ansible vault for secrets (encrypted variables). Ansible tags for selective
task execution. Custom Ansible modules. InSpec/Serverspec for compliance testing.
osquery advanced queries (joining tables: file, users, processes). Pull model
detail: Puppet catalog, Chef runlist, convergence cycle. Canary deployment
pattern with Ansible. `max-fail-percentage` for safe deployments.

**Level 4:**
Ansible AWX/Tower for centralized playbook management (RBAC, job scheduling,
UI). Dynamic inventory from AWS/GCP/Azure APIs (inventory from tags, not static
files). Puppet PuppetDB for reporting and compliance dashboards. Chef InSpec
integration with CI/CD. GitOps for fleet management: git push triggers
Ansible Tower job. Infrastructure immutability: packer + ansible provisioner
for golden image building. Prometheus node_exporter + Grafana for fleet-wide
metrics.

**Level 5:**
Fleet management at cloud scale (10,000+ nodes): Ansible limitations (SSH to
10,000 hosts is slow), AWS Systems Manager (SSM) as alternative (agent-based,
no inbound SSH required). Event-driven automation: osquery events triggering
Ansible remediation automatically. Desired State Configuration (DSC) for
Windows mixed fleets. Cross-cloud fleet management with Terraform + Ansible.
Kubernetes-style reconciliation loop (controller pattern) applied to VM fleet:
operator constantly driving servers toward desired state. Policy as Code:
OPA (Open Policy Agent) + InSpec for automated compliance enforcement.

---

### Code Example

**BAD - imperative shell script for configuration management:**
```bash
#!/bin/bash
# BAD: imperative, not idempotent, hard to maintain at scale

# NOT idempotent: fails with "user already exists" on second run!
useradd -m -s /bin/bash deployer

# NOT idempotent: if file already has the line, adds it again!
echo "deployer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# NOT idempotent: downloads and installs nginx on every run
yum install -y nginx

# NOT declarative: we're describing HOW, not WHAT we want
# No dry-run, no change detection, no rollback
# If this script fails halfway: server is in unknown state
# If run on 200 servers simultaneously: 200 different outcomes
# possible based on race conditions
```

```bash
# GOOD: Ansible playbook - declarative, idempotent, safe

# site.yml - main playbook
---
- name: Web Server Configuration
  hosts: webservers
  become: yes
  vars_files:
    - group_vars/webservers.yml  # versioned variables

  tasks:
    # Idempotent: 'state: present' = ensure exists, not "create"
    # Second run: 'ok' not 'changed'
    - name: Create deployer user
      user:
        name: deployer
        shell: /bin/bash
        state: present
        # groups: wheel  # add to wheel if needed

    # Idempotent: lineinfile ensures line exists EXACTLY ONCE
    - name: Grant deployer sudo access
      lineinfile:
        path: /etc/sudoers.d/deployer
        line: "deployer ALL=(ALL) NOPASSWD:ALL"
        create: yes
        mode: '0440'
        validate: 'visudo -cf %s'  # validate syntax before writing!

    # Idempotent: 'state: present' = no-op if already installed
    - name: Install nginx
      yum:
        name: nginx
        state: present  # or 'latest' to always update

    # Template: generates config from Jinja2 template
    - name: Configure nginx
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        validate: 'nginx -t -c %s'  # validate config before applying
      notify: Reload nginx  # only restarts if THIS task changed

    # Ensure running and enabled - idempotent
    - name: Enable nginx
      systemd:
        name: nginx
        enabled: yes
        state: started

  handlers:
    # Runs ONCE at end, only if notified
    - name: Reload nginx
      systemd:
        name: nginx
        state: reloaded  # reload = graceful, not full restart

# Usage:
# Dry-run: ansible-playbook site.yml --check
# Run: ansible-playbook site.yml
# Rolling: ansible-playbook site.yml --serial 10 --max-fail-percentage 10
# Targeted: ansible-playbook site.yml --limit web01.example.com
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Ansible is all you need - Puppet/Chef are obsolete" | Ansible (push model) and Puppet/Chef (pull model) solve different problems. Ansible requires a central control node to push changes - between runs, drift can accumulate undetected for hours. Puppet and Chef agents check every 30 minutes (configurable) and automatically correct drift. For 50 servers with weekly change cadence: Ansible is simpler and sufficient. For 5000 servers with strict compliance requirements where drift must be corrected within 30 minutes automatically: Puppet or Chef's continuous enforcement is essential. At large scale: Ansible run time for 5000 servers (even in parallel) can be 30+ minutes, while pull-model agents work concurrently without central bottleneck. Many large organizations use BOTH: Puppet for continuous enforcement, Ansible for ad-hoc operations. |
| "Idempotent means the result is always the same regardless of initial state" | Idempotency means: running the operation N times has the same EFFECT as running it once. The result DOES depend on initial state, but applying the operation again doesn't CHANGE a correctly-configured system. A module that says "ensure user 'deployer' exists" is idempotent: if the user doesn't exist, it creates it; if the user already exists, it does nothing. The result is: user exists. Running it 10 times: same result (user exists). The confusion: idempotent does NOT mean "always creates the same result from scratch." It means "multiple applications are safe." Non-idempotent example: `echo "line" >> /etc/file`. First run: adds the line. Second run: adds the line AGAIN (duplicate). Use `lineinfile` (Ansible) which checks if the line exists before adding. |
| "Configuration management replaces documentation" | Configuration management describes the WHAT (desired state), not the WHY. A playbook that sets `net.ipv4.ip_forward = 0` doesn't explain: why this was set, what breaks if it's changed, when this requirement was added, which security control requires it. Documentation must still explain: architectural decisions, business requirements driving configuration choices, exceptions and their justifications, historical context. Configuration management IS living documentation for the HOW, but should always be paired with: Git commit messages explaining WHY the change was made, runbook/wiki linking to relevant security requirements, comments in playbooks for non-obvious choices. The two complement each other. |
| "Fleet management tools can push changes to all servers simultaneously" | Tools CAN push to all servers simultaneously but this is operationally dangerous and usually wrong. Ansible's default parallelism (`forks=5`) runs against 5 hosts at a time for safety. Even if you set `forks=500` (all servers simultaneously): if the change causes a service failure, ALL servers fail at the same time. Safe patterns: rolling deployments (`serial: 10%` = 10 servers at a time), canary deployments (1 server first, then groups), blue/green (build entirely new fleet, switch traffic). The correct mental model: configuration management ensures EVENTUAL consistency, not SIMULTANEOUS changes. The goal is that all servers end up in the desired state, not that they all change at exactly the same moment. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: Ansible SSH connection issues ===
ansible all -m ping
# server01 | UNREACHABLE! => {"changed": false, "msg": "Failed to connect..."}

# Debug connectivity:
ansible all -m ping -vvv  # verbose: shows SSH command being attempted
ssh ansible-svc@server01  # try manual SSH to isolate issue
# If SSH works but ansible fails: check ansible.cfg inventory, remote_user

# Check SSH key:
ansible all -m ping --private-key=~/.ssh/ansible_key -u deployer

# Timeout issues (many hosts, slow network):
ansible all -m ping --timeout 30  # increase timeout

# === Failure: Task fails on some hosts but not others ===
ansible-playbook site.yml
# TASK [Configure nginx] FAILED!: web03.example.com: ...
# ^ Only web03 failed

# Debug single host:
ansible-playbook site.yml --limit web03.example.com -vvv

# Check if template renders correctly:
ansible webservers -m template \
    -a "src=nginx.conf.j2 dest=/tmp/nginx_test.conf"

# Check nginx config syntax on web03:
ansible web03.example.com -m command \
    -a "nginx -t" --become

# === Failure: Drift detected in --check mode ===
ansible-playbook security-baseline.yml --check
# TASK [Ensure SSH PasswordAuthentication disabled] changed: [db01, db03, db07]

# Investigate why these hosts drifted:
ansible db01,db03,db07 -m shell \
    -a "grep PasswordAuthentication /etc/ssh/sshd_config"
# db01: PasswordAuthentication yes  <- manually changed!

# Find who changed it:
ansible db01 -m shell \
    -a "grep PasswordAuthentication /var/log/audit/audit.log | tail -5"

# Apply only to drifted hosts:
ansible-playbook security-baseline.yml --limit db01,db03,db07

# === Failure: osquery fleet query finds unexpected state ===
osqueryi "
SELECT h.hostname, u.username, u.uid
FROM users u
JOIN system_info h
WHERE u.uid = 0 AND u.username != 'root'
"
# hostname    | username | uid
# app07       | sysadm   | 0    <- uid=0 user that's not root! Investigate!

# Investigate app07:
ansible app07.example.com -m shell -a "getent passwd sysadm" --become
# sysadm:x:0:0::/home/sysadm:/bin/bash  <- uid=0 = root equivalent!
# This is a security incident: unauthorized root-equivalent user

# Immediate containment:
ansible app07.example.com -m user \
    -a "name=sysadm state=absent remove=yes" --become
# Remove the user (after investigation!)
```

---

### Related Keywords

**Foundational:**
LNX-055 (systemd services), LNX-098 (NFS)

**Builds on this:**
LNX-100 (hardening at scale)

**Related:**
LNX-100 (CIS Benchmarks, STIG hardening at scale)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ansible all -m ping` | Test connectivity to all hosts |
| `ansible all -m command -a "uname -r"` | Ad-hoc command on all hosts |
| `ansible-playbook site.yml --check` | Dry-run (show what would change) |
| `ansible-playbook site.yml --serial 10%` | Rolling deploy 10% at a time |
| `ansible-playbook site.yml --limit host` | Target single host |
| `osqueryi "SELECT * FROM users WHERE uid=0"` | Query root users on host |
| `inspec exec profile.rb -t ssh://root@host` | Run compliance check |
| `ansible all -m setup --tree /tmp/facts/` | Gather all host facts |

**3 things to remember:**
1. Idempotency is the core requirement: use declarative modules (`yum: state=present`, `user: state=present`) not imperative commands (`shell: yum install nginx`). Imperative shell is not idempotent and creates undefined behavior on repeated runs.
2. Push model (Ansible) requires periodic runs for drift correction. Pull model (Puppet/Chef) self-corrects every 30 minutes. Choose based on: drift correction SLA requirements and operational complexity tolerance.
3. `ansible-playbook --check` is your safety net: always dry-run before applying changes to production. Combined with `--diff` to see file content changes.

---

### Transferable Wisdom

Fleet management principles transfer directly to: Kubernetes (desired state
declarative model - `kubectl apply` drives cluster toward desired state, etcd
stores desired state, controllers reconcile actual vs desired), Terraform for
cloud infrastructure (same declarative model: define desired infrastructure,
tool calculates and applies the delta), GitOps (git repository IS the desired
state, controller continuously reconciles cluster against repository). The
idempotency requirement maps to: REST API design (PUT is idempotent, POST is
not - same body, same result), database UPSERT operations (INSERT OR UPDATE),
message queue consumers with deduplication (processing same message twice
should produce same result). Configuration drift is the infrastructure
equivalent of: code rot (codebase diverges from design over time), database
schema drift (actual schema diverges from ORM model), API version drift
(client and server diverge). The solution is the same: define desired state,
measure actual state, compute delta, apply corrections. osquery's SQL interface
to OS data is the same abstraction as: Prometheus for metrics (query system
state with PromQL), Kubernetes API (query cluster state with kubectl).

---

### The Surprising Truth

Ansible's agentless SSH approach was considered a weakness when it launched in
2012 - competitors said "you need an agent for real configuration management."
Ten years later, Ansible is the most-used configuration management tool in the
industry precisely because of its agentless design. Every Linux server has SSH.
No new software to install, no bootstrap problem, no agent to upgrade, no
agent using CPU and memory continuously. The lesson: simplicity in deployment
is a feature, not a limitation. The most sophisticated tool is not always the
right tool. Ansible succeeded by removing the barrier to entry (no agent
installation), even at the cost of continuous enforcement capabilities.

The real surprise: many large organizations that adopted Puppet and Chef in
2008-2015 have spent more time managing the Puppet/Chef infrastructure (masters,
databases, certificate authorities, module upgrades) than the servers the tools
were meant to manage. Several companies have migrated from "sophisticated"
agent-based tools back to Ansible, accepting less frequent drift correction
in exchange for massively reduced operational overhead.

---

### Mastery Checklist

- [ ] Can write an Ansible inventory file and run ad-hoc commands and playbooks
- [ ] Understands idempotency and can identify idempotent vs non-idempotent tasks
- [ ] Can implement rolling deployments with Ansible serial and max-fail-percentage
- [ ] Can write basic osquery queries to detect configuration drift
- [ ] Understands push vs pull model trade-offs for different operational requirements

---

### Think About This

1. A startup has 50 servers and uses Ansible with ad-hoc playbook runs (no
   scheduling). A larger company with 5000 servers uses Puppet with 30-minute
   agent convergence. The startup's SRE says "we have better control - we know
   exactly when changes happen." The larger company's SRE says "we have better
   compliance - drift is corrected automatically." Design an argument for each
   position. What evidence would you need to determine which approach is actually
   providing better security and stability? At what scale does the startup's
   approach break down?

2. Design an Ansible-based deployment strategy for a security patch that requires
   a service restart (nginx) for 500 servers in a production environment that
   cannot have more than 10% of its capacity offline at any time. The patch
   has failed on one server in the past (due to a config file conflict). Write
   out the key Ansible parameters you would use, the pre-checks you would run
   before the full deployment, and your rollback plan if the patch starts failing
   at scale.

3. Your company decides to move from mutable infrastructure (Ansible managing
   in-place configuration on long-lived servers) to immutable infrastructure
   (new AMI for every change, old servers terminated). What configuration
   management challenges does this solve? What new operational challenges does
   it introduce? For what types of workloads is immutable infrastructure clearly
   better? For what types of workloads does it create more problems than it solves?

---

### Interview Deep-Dive

**Foundational:**
Q: What is configuration drift, and how would you detect and correct it at scale?
A: CONFIGURATION DRIFT DEFINITION: When a server's actual configuration diverges from its intended baseline. Causes: (1) Manual emergency changes ("just SSH and fix it") that were never reverted; (2) Failed partial updates (update ran, failed halfway, server in intermediate state); (3) Different update timing (server A patched Monday, server B not yet patched Tuesday - same baseline, different state); (4) Application side effects (application modifies config files that config management also manages); (5) Human error (wrong host targeted by ad-hoc command). DETECTION METHODS: (1) Ansible --check mode: `ansible-playbook baseline.yml --check` shows every task that WOULD make a change, meaning it has drifted from desired state. Run this as a cron job and alert when changes are detected. (2) Pull-model enforcement (Puppet/Chef): agent runs every 30 minutes, compares actual vs desired state, reports differences to central dashboard. Report: "server X has drifted on 3 resources." (3) osquery: `SELECT name,version FROM packages WHERE name='openssl'` across all servers. Servers with different versions have drifted. Can query any OS data: users, processes, listening ports, file hashes, kernel parameters. (4) AIDE: file integrity monitoring reports changed files. (5) InSpec: explicit compliance tests: "PasswordAuthentication MUST be 'no'" - fails if drifted. CORRECTION: (1) For Ansible: run the full playbook (idempotent, safe). Only tasks that have drifted will show "changed". (2) For Puppet/Chef: agent automatically corrects at next convergence. (3) For specific hosts: `ansible-playbook baseline.yml --limit drifted-host1,drifted-host2`. PREVENTION: Eliminate the ability to SSH and make changes directly: require all changes through version-controlled playbooks, reviewed by peers, applied through CI/CD pipeline. "IaC only" change policy. Detect and alert on unauthorized SSH sessions that result in changes (auditd: log all root EXECVE events, correlate with non-Ansible sessions).

**Expert:**
Q: Compare push vs pull configuration management models and explain when you'd choose each in a real production environment.
A: PUSH MODEL (Ansible): Architecture: central control node SSHs to each managed host, executes tasks. Trigger: human runs `ansible-playbook`, or scheduled cron/CI job. Characteristics: (1) No agent on managed hosts (just SSH + Python); (2) Changes happen on-demand when admin triggers; (3) Drift correction: only at next playbook run; (4) At scale: sequential unless parallelized (forks setting), central SSH load; (5) Simple to set up, no central server infrastructure needed for basic use. When to choose Ansible: (a) smaller fleets (under ~500 servers), (b) low drift correction SLA (correcting within hours is fine), (c) SSH is already the universal access method, (d) team is comfortable with YAML and git, (e) ad-hoc operations are frequent (Ansible excels at one-off tasks). PULL MODEL (Puppet/Chef): Architecture: agent installed on every managed host, contacts master (or uses git repo). Trigger: agent runs on schedule (Puppet: every 30 minutes by default). Characteristics: (1) Agent always running (small CPU/memory overhead per host); (2) Drift corrected within one convergence cycle (30 minutes); (3) No inbound SSH required from central node to hosts; (4) At scale: agents work concurrently, no central SSH bottleneck; (5) More infrastructure to maintain (Puppet master + PuppetDB, or Chef server). When to choose Puppet/Chef: (a) large fleets (500+ servers), (b) strict compliance: drift must be corrected within 30 minutes automatically, (c) no-SSH environments (locked-down production, cloud ASGs where hosts come and go), (d) detailed reporting required: which resources drifted on which hosts, (e) auto-scaling environments: new instances self-configure on launch. HYBRID PATTERN (large organizations): Use Puppet for continuous enforcement (baseline always applied), use Ansible for ad-hoc operations ("restart nginx on all web servers NOW" via Ansible ad-hoc), use Ansible for initial server bootstrapping before Puppet agent is installed. Example at scale: Netflix used a hybrid approach, LinkedIn built their own (Mint). The non-negotiable: whatever tool you choose, ALL configuration changes must go through it. The moment someone "just SSHes in to make a quick fix," the tool's value is undermined and drift becomes undetectable.
