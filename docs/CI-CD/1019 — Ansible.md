---
layout: default
title: "Ansible"
parent: "CI/CD"
nav_order: 1019
permalink: /ci-cd/ansible/
number: "1019"
category: CI/CD
difficulty: ★★☆
depends_on: Infrastructure as Code, CI/CD Pipeline, SSH, Linux
used_by: Terraform, GitOps, Environment Promotion
related: Terraform, Pulumi, Chef, SaltStack, Puppet
tags:
  - cicd
  - devops
  - linux
  - intermediate
  - configuration
---

# 1019 — Ansible

⚡ TL;DR — Ansible automates configuration management and application deployment on existing servers using YAML playbooks executed over SSH, without requiring any agent installed on target machines.

| #1019 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Infrastructure as Code, CI/CD Pipeline, SSH, Linux | |
| **Used by:** | Terraform, GitOps, Environment Promotion | |
| **Related:** | Terraform, Pulumi, Chef, SaltStack, Puppet | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A DevOps engineer needs to configure 50 new web servers identically: install nginx, configure TLS, set up the application user, deploy a config file, start the service, and verify it responds. They SSH into server 1, run the steps manually, SSH into server 2, run the steps again. Two hours in, server 12 has a slightly different nginx config because they forgot one sed command. Server 31 is running nginx 1.20 because the apt package was updated mid-session. The "identical configuration" objective has drifted into 50 unique snowflake servers.

**THE BREAKING POINT:**
Manual multi-server configuration doesn't scale. Beyond 5–10 servers, humans can't maintain consistency. Shell scripts help, but they're hard to read, difficult to debug, run linearly, and don't handle partial failures gracefully. And every server needs SSH access and the script manually executed.

**THE INVENTION MOMENT:**
This is exactly why Ansible was created: describe the desired configuration for all servers in human-readable YAML, run one command, and Ansible SSH-es into every server in parallel and makes them match the description — idempotently and without installing any agent.

---

### 📘 Textbook Definition

**Ansible** (Red Hat) is an open-source, agentless configuration management and automation tool that uses SSH to execute **playbooks** (YAML-defined sequences of **tasks**) against groups of hosts defined in an **inventory**. Unlike declarative IaC tools (Terraform), Ansible is primarily **imperative** — tasks are executed in order and the operator controls the sequence. Ansible provides **modules** (Python-based, built-in operations: `apt`, `copy`, `template`, `service`, `docker_container`) that implement idempotent operations: running an `apt` task that installs nginx is safe to run multiple times — if nginx is already installed, the task reports "ok" and does nothing. Ansible is most appropriate for server configuration, software installation, and application deployment on existing infrastructure — complementing Terraform (which provisions the infrastructure itself).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write a recipe for how servers should be configured, and Ansible applies it to all of them simultaneously.

**One analogy:**
> Ansible is like a restaurant head chef who can cook the same dish in all 20 kitchen stations simultaneously. The recipe (playbook) is the source of truth. Each station follows the same steps in order. The head chef monitors all stations at once via the kitchen intercom (SSH). No station needs a special device installed — just a standard stovetop (SSH + Python).

**One insight:**
The agentless design is Ansible's defining characteristic — and its most underrated one. Tools like Puppet and Chef require a running agent daemon on every managed server. Ansible requires only SSH access and Python installed on the target (both available on every Linux server by default). This means you can use Ansible on servers the day they're provisioned, on servers you don't control (client machines), and on network devices that can't run agents.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Configuration drift is inevitable with manual processes — any automated configuration system must handle "already configured" gracefully.
2. Servers can fail mid-configuration — the system must be safe to restart from any point.
3. SSH is universal — every Linux server has it; no deployment depends on a vendor-specific agent being pre-installed.

**DERIVED DESIGN:**
Ansible's idempotency model: each module checks the current state before acting. `apt: name=nginx state=present` first checks if nginx is installed. If yes: noop, report "ok." If no: install, report "changed." This check-then-act pattern means playbooks can be run repeatedly without side effects — which is essential for CI/CD automation where the same playbook may run on servers in any state.

**Push vs Pull architecture:** Ansible uses a push model — the control node (your machine or CI runner) pushes tasks to target nodes. Puppet/Chef use a pull model — agents on target nodes periodically pull config from a central server. Push is simpler to set up (no permanent agent), but requires the control node to be able to reach targets (firewall implications). Pull is more scalable for large fleets but requires agent management.

**Roles** are Ansible's code organisation mechanism — a directory structure containing tasks, variables, handlers, templates, and files for a coherent logical grouping (a `nginx` role, a `postgresql` role). Roles are the unit of reuse in Ansible.

**THE TRADE-OFFS:**
**Gain:** Agentless; human-readable YAML; large module library (thousands of built-in modules); low barrier to entry; idempotent modules.
**Cost:** Slow for large fleets (SSH connection overhead per task). Becomes complex at scale (role dependencies, variable precedence). Not purely declarative — task order matters. No built-in state management (Ansible doesn't know "what did the last run change?" without external logging).

---

### 🧪 Thought Experiment

**SETUP:**
A team must deploy a config file update to 200 web servers during a maintenance window. The update changes a single nginx.conf parameter.

**WHAT HAPPENS WITHOUT ANSIBLE:**
Engineer writes a bash script: ssh to each server, scp the file, restart nginx. Script runs for 30 minutes. Server 73 fails its SSH connection mid-run. Script stops. The 127 remaining servers haven't received the update. Engineer must manually track which servers were updated, resume the script from server 74, and handle the failed server separately.

**WHAT HAPPENS WITH ANSIBLE:**
```yaml
- hosts: web_servers
  tasks:
    - name: Deploy nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: restart nginx
  handlers:
    - name: restart nginx
      service: name=nginx state=restarted
```
`ansible-playbook deploy.yml -i inventory/prod`
- Runs on all 200 servers in parallel (default: 5 at a time)
- Server 73 fails: Ansible records it as failed and continues
- Summary: 199 changed, 1 failed
- Re-run with `--limit server73`: only retries the failed server
- Idempotent: re-running on already-updated servers: all "ok", no nginx restart

**THE INSIGHT:**
Ansible turns a fragile sequential script into a parallel, failure-aware, idempotent automated system. The same playbook that deploys to 200 servers is the same playbook that can safely re-run to verify they're all configured correctly.

---

### 🧠 Mental Model / Analogy

> Ansible is like a standardised franchise operations manual. Each franchise location (server) follows the same manual (playbook). The head office (control node) sends the operations manager (ansible-playbook command) to each location to verify compliance and make corrections. Each task in the manual is idempotent: "ensure the lights are LED" means check first — if already LED, tick it off; if not, replace them. After a visit, every location is identical.

- "Franchise operations manual" → Ansible playbook
- "Operations manager visit" → `ansible-playbook` execution run
- "Each franchise location" → managed server (inventory host)
- "Idempotent task" → module check-then-act pattern
- "Head office" → Ansible control node (CI runner or engineer laptop)
- "Expansion: new location follows same manual" → new server added to inventory

Where this analogy breaks down: a franchise manager visits locations sequentially. Ansible runs tasks across all hosts in parallel (with configurable `forks`). The parallelism is Ansible's performance advantage over sequential shell scripts.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Ansible lets you write a list of instructions (like "install this software, put this file here, enable this service") and run them on many servers simultaneously. All servers end up identically configured, and running the same instructions again on already-configured servers changes nothing — it just confirms they're already correct.

**Level 2 — How to use it (junior developer):**
Create an inventory file listing your servers under groups. Write a playbook YAML file with `hosts:` (which group) and `tasks:` (what to do). Run with `ansible-playbook playbook.yml -i inventory.ini`. Use `ansible -m ping all` to test connectivity to all hosts. Use `--check` (dry-run mode) to preview what would change. Store sensitive values in Ansible Vault: `ansible-vault encrypt_string 'secret' --name 'db_password'`.

**Level 3 — How it works (mid-level engineer):**
Ansible compiles the playbook into a task list, then for each task: serialises the appropriate module Python code, uploads it to the target server via SSH/SFTP, executes it (Python interpreter), captures JSON output (changed/ok/failed status + message), deletes the temporary file, and moves to the next task. The entire module execution is ephemeral — no persistent process on the target. Handlers are special tasks triggered by `notify:` only when the notifying task reports "changed" — allowing nginx restart only when the config actually changed, not on every run. Variable precedence has 22 levels in Ansible — knowing the order (group_vars < host_vars < play variables < command-line -e) is essential for debugging unexpected values.

**Level 4 — Why it was designed this way (senior/staff):**
Ansible's agentless architecture was a deliberate reaction to the complexity of agent-based tools (Puppet, Chef). In 2012, provisioning a new server with Puppet meant: install Puppet agent, connect to Puppet master, wait for catalog compilation, first run sets up the server. This initial bootstrapping required the agent to be installed before any automation could run — a chicken-and-egg problem. Ansible eliminates bootstrapping entirely. The choice of YAML over a domain-specific language (Puppet DSL, Chef Ruby DSL) made Ansible accessible to operations teams without programming background. This decision also introduced YAML's limitations (no true conditionals, awkward loops) that make complex playbooks harder to maintain. The modern answer is `ansible-lint` for code quality and Molecule for role testing — bringing software engineering discipline to Ansible.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  ANSIBLE EXECUTION MODEL                    │
├─────────────────────────────────────────────┤
│                                             │
│  Control Node: ansible-playbook command     │
│                                             │
│  STEP 1: Parse inventory                    │
│  inventory.ini: [web_servers]               │
│  10.0.1.1, 10.0.1.2, ... 10.0.1.200        │
│                                             │
│  STEP 2: Connect to hosts (parallel, SSH)   │
│  fork processes: default 5 hosts at once   │
│                                             │
│  STEP 3: For each task per host:            │
│  a. Gather facts: uname, hostname, OS,      │
│     memory, disk, network interfaces       │
│  b. Serialize module Python code            │
│  c. SFTP module to /tmp/ on target          │
│  d. SSH execute: python3 /tmp/module.py     │
│  e. Capture JSON output: {                  │
│       "changed": true/false,               │
│       "msg": "...",                        │
│       "rc": 0                              │
│     }                                      │
│  f. Remove /tmp/module.py                   │
│                                             │
│  STEP 4: Handle task results                │
│  changed: update host facts                 │
│  failed: mark host as unreachable/failed   │
│  ok: continue to next task                  │
│                                             │
│  STEP 5: Play summary                       │
│  PLAY RECAP:                                │
│  server1: ok=5 changed=2 failed=0          │
│  server73: ok=2 changed=0 failed=1         │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
New server provisioned by Terraform
  → IP added to Ansible inventory
  → CI triggers Ansible playbook [← YOU ARE HERE]
     ansible-playbook server-setup.yml -i inventory/
     Task 1: install nginx (apt module)
     Task 2: deploy nginx.conf (template module)
     Task 3: ensure nginx started (service module)
     Task 4: deploy app (copy/git module)
     Task 5: run smoke test (uri module)
  → All tasks: ok or changed
  → Server is configured and verified
  → Application serving traffic
```

**FAILURE PATH:**
```
Task 4 fails: git clone times out
  → Tasks 5+ skipped for that host
  → Error displayed: "FAILED! => {msg: timeout}"
  → Other hosts continue unaffected
  → Re-run with: ansible-playbook ... --limit failed_hosts
  → Idempotent: previous tasks report "ok" (no-op)
  → Only failed task retried
```

**WHAT CHANGES AT SCALE:**
At 1000+ servers, the default SSH connection-per-task-per-host becomes a bottleneck. Solutions: increase `forks` (parallel connections), enable `pipelining` (reuse SSH connection across tasks), use `mitogen` accelerator (Ansible plugin that 10x speeds up task execution by using Python subprocess multiplexing instead of per-task SSH). AWX (open-source Ansible Tower) provides a web UI, RBAC, job scheduling, and per-run audit logs — essential for large-scale managed Ansible.

---

### 💻 Code Example

**Example 1 — Basic playbook (nginx installation):**
```yaml
# playbooks/configure_web.yml
---
- name: Configure web servers
  hosts: web_servers
  become: true     # sudo escalation
  vars:
    nginx_worker_processes: 4

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present     # idempotent: install if absent
        update_cache: true

    - name: Deploy nginx configuration
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        mode: "0644"
      notify: Restart nginx   # triggers on "changed" only

    - name: Ensure nginx is running and enabled
      service:
        name: nginx
        state: started
        enabled: true         # start on boot

  handlers:
    # Only runs if a task that notified it changed
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

**Example 2 — Inventory with groups:**
```ini
# inventory/production.ini
[web_servers]
web-01.example.com ansible_user=ubuntu
web-02.example.com ansible_user=ubuntu
web-03.example.com ansible_user=ubuntu

[db_servers]
db-01.example.com ansible_user=ubuntu

[all:vars]
ansible_ssh_private_key_file=~/.ssh/prod_key

[web_servers:vars]
nginx_workers=4
```

**Example 3 — Running Ansible in GitHub Actions CI:**
```yaml
# .github/workflows/deploy.yml
- name: Deploy with Ansible
  run: |
    # Write SSH key from GitHub Secret
    echo "${{ secrets.SSH_PRIVATE_KEY }}" > /tmp/key
    chmod 600 /tmp/key

    ansible-playbook \
      -i inventory/production.ini \
      playbooks/deploy_app.yml \
      --private-key /tmp/key \
      --extra-vars "app_version=${{ github.sha }}" \
      -v   # verbose output for CI logs
```

**Example 4 — Ansible Vault for secrets:**
```bash
# Encrypt a variable file
ansible-vault encrypt group_vars/all/secrets.yml

# Reference in playbook (Ansible decrypts at runtime)
# secrets.yml (encrypted):
# db_password: "p4ssw0rd123"
# api_key: "sk-live-abc123"

# Run playbook with vault password
ansible-playbook deploy.yml \
  --vault-password-file ~/.vault_pass.txt
# Or use ANSIBLE_VAULT_PASSWORD_FILE env var in CI
```

---

### ⚖️ Comparison Table

| Tool | Agent? | Language | State Mgmt | Paradigm | Best For |
|---|---|---|---|---|---|
| **Ansible** | No (agentless) | YAML | None | Imperative | Ad-hoc runs, app deploy, config |
| Puppet | Yes | Puppet DSL | Catalog/reports | Declarative | Large, long-lived server fleets |
| Chef | Yes | Ruby DSL | None | Declarative | Developer-centric orgs |
| SaltStack | Optional | YAML + Python | State tree | Both | Large fleets, event-driven |
| Terraform | No | HCL | State file | Declarative | Cloud provisioning |

How to choose: Use **Ansible** for configuration management on existing servers, application deployment, and ad-hoc operational tasks — especially when you can't or don't want to install agents. Use **Terraform** for provisioning new cloud infrastructure from scratch. Use **Puppet** or **Chef** for very large server fleets with complex compliance requirements that benefit from continuous drift detection via agents. In practice, many teams use Terraform + Ansible together: Terraform provisions the servers, Ansible configures them.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Ansible is declarative like Terraform | Ansible is primarily imperative — tasks run in order, and the operator is responsible for ordering. Modules implement idempotent operations, but the playbook structure is procedural, not a desired-state declaration. |
| Agentless means less secure | Agentless means Ansible uses standard SSH (port 22) — the same protocol used for manual server access. Agent-based tools like Puppet open additional ports for agent communication. "Agentless" is not inherently less secure; it's a different (and often simpler) trust model. |
| Idempotent modules mean runs are always safe | Modules are idempotent by themselves, but playbook sequencing can create non-idempotent behaviour (e.g., `shell: apt-get dist-upgrade` is not idempotent). Always prefer dedicated modules (`apt: upgrade: dist`) over `shell:/command:` for idempotency. |
| Ansible can replace Terraform | Ansible can provision cloud resources (using cloud modules), but without state management, it tracks nothing. Running a playbook that creates an EC2 instance twice creates two instances. Terraform deduplicates via state. Use Terraform for provisioning, Ansible for configuration. |

---

### 🚨 Failure Modes & Diagnosis

**1. SSH Timeout Causes Partial Playbook Run**

**Symptom:** Playbook runs against 50 servers. 12 servers fail with "SSH timeout" — those servers receive none of the configuration. Different servers were affected on different runs.

**Root Cause:** SSH connection timeout (`ansible.cfg: timeout = 10`) too conservative for slow network. Network intermittency or high load on target servers.

**Diagnostic:**
```bash
# Test SSH connectivity to affected servers
ansible web_servers -m ping -i inventory/ -v

# Check SSH timeout configuration
ansible-config dump | grep TIMEOUT

# Test with increased timeout
ansible-playbook playbook.yml \
  -i inventory/ \
  --timeout=30
```

**Fix:**
```ini
# ansible.cfg
[defaults]
timeout = 30
# Increase SSH timeout
pipelining = True
# Reduce number of SSH connections needed
forks = 10
# Increase parallelism to finish faster
```

**Prevention:** Set `timeout` appropriate for your network latency. Enable `pipelining` to reduce total SSH connections. Implement retry logic: `--retries 3` or use the `retries:` directive per task for transient failures.

---

**2. Variable Precedence Confusion Causes Wrong Config**

**Symptom:** Playbook deploys wrong nginx worker count to production servers. Engineer set `nginx_workers: 8` in the playbook, but production servers get `nginx_workers: 4`.

**Root Cause:** `group_vars/web_servers.yml` has `nginx_workers: 4`, which overrides the play-level variable due to Ansible's 22-level variable precedence (group vars override play vars at many levels).

**Diagnostic:**
```bash
# Debug variable values for a specific host
ansible web-01 -m debug \
  -a "var=nginx_workers" \
  -i inventory/

# Show all variable sources and values
ansible web-01 -m debug \
  -a "var=hostvars[inventory_hostname]" \
  -i inventory/ | grep nginx_workers

# Check which file sets the value
ansible-config dump | grep VARIABLE_PRECEDENCE
```

**Fix:** Use `-e` (extra-vars) for values that must always win — they have highest precedence:
```bash
ansible-playbook playbook.yml \
  -e "nginx_workers=8"
```

**Prevention:** Document your variable strategy. Use `defaults/main.yml` in roles for values that can be overridden. Use `vars/main.yml` for values that should not be overridden. Never rely on implicit precedence for critical values — be explicit.

---

**3. Shell/Command Module Breaks Idempotency**

**Symptom:** Every playbook run re-runs a database migration script, causing errors ("table already exists," duplicate data inserts).

**Root Cause:** Task uses `shell: python manage.py migrate` without a guard. Shell/command modules don't check-before-act — they always report "changed" and execute.

**Diagnostic:**
```bash
# Find all shell/command usage in playbooks
grep -r "shell:\|command:" playbooks/ roles/

# Run with --check to see what would "change"
ansible-playbook playbook.yml --check
```

**Fix:**
```yaml
# BAD: always runs, always reports changed
- name: Run database migration
  shell: python manage.py migrate

# GOOD: check for migration sentinel file
- name: Check if migration already ran
  stat:
    path: /app/.migration_complete
  register: migration_done

- name: Run migration (only if not done)
  shell: python manage.py migrate
  when: not migration_done.stat.exists

- name: Mark migration complete
  file:
    path: /app/.migration_complete
    state: touch
  when: not migration_done.stat.exists
```

**Prevention:** Prefer dedicated modules over `shell:/command:`. When `shell:` is unavoidable, use `creates:` or `removes:` arguments (built-in idempotency guards) or `register + when:` conditionals.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SSH` — Ansible connects to servers via SSH; understanding SSH authentication (keys, agents, bastion hosts) is required
- `Linux` — Ansible manages Linux servers; understanding file permissions, systemd, package managers is required
- `Infrastructure as Code` — Ansible is one IaC tool category; understanding the broader IaC landscape contextualises Ansible's role

**Builds On This (learn these next):**
- `Terraform` — often used together: Terraform provisions infrastructure, Ansible configures it; understanding both is the typical DevOps toolkit
- `GitOps` — Ansible playbooks in git repositories enable GitOps-style configuration management alongside application deployments

**Alternatives / Comparisons:**
- `Terraform` — declarative cloud provisioning; Ansible is complementary (configuration) not competitive (provisioning)
- `Puppet` — agent-based configuration management with continuous drift detection; more powerful for large fleets but higher operational complexity
- `Chef` — Ruby-based configuration management; developer-centric alternative with steeper learning curve
- `SaltStack` — event-driven configuration management supporting both agent and agentless modes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Agentless server configuration via YAML   │
│              │ playbooks executed over SSH               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual multi-server configuration causing │
│ SOLVES       │ inconsistency, snowflake servers, errors  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Idempotent modules: safe to re-run always.│
│              │ Avoid shell: for anything repeatable      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Configuring existing servers, app deploy, │
│              │ operational tasks on heterogeneous fleets │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Provisioning new cloud infrastructure —   │
│              │ use Terraform for resource provisioning   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity and agentless convenience vs   │
│              │ no state tracking, slower at large scale  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Head chef running the same recipe across │
│              │  200 kitchen stations simultaneously."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Ansible Roles → Molecule testing →        │
│              │ AWX/Tower → Terraform + Ansible patterns  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 1,000 servers running an Ansible-managed application. You need to apply a security patch that requires a service restart. If you restart all 1,000 services simultaneously, some are behind a load balancer and users will experience downtime. Design an Ansible strategy using `serial:`, `max_fail_percentage:`, and rolling restart patterns to apply the patch to all 1,000 servers with zero user-visible downtime — and explain what happens if a server fails mid-roll.

**Q2.** Your organisation uses Ansible for server configuration management and Terraform for cloud infrastructure provisioning. A new database server is provisioned by Terraform and must be configured by Ansible (install PostgreSQL, configure pg_hba.conf, create application database and user). How do you design the handoff between Terraform and Ansible — specifically: how does Ansible discover the new server's IP address without manual inventory updates, and how do you ensure the Ansible configuration runs exactly once on first provision but can safely re-run as a day-2 configuration audit?

