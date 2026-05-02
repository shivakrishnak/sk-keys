---
layout: default
title: "Systemd / Init System"
parent: "Linux"
nav_order: 134
permalink: /linux/systemd-init-system/
number: "0134"
category: Linux
difficulty: ★★☆
depends_on: Process Management (ps, top, kill), Linux File System Hierarchy, Shell Scripting
used_by: Linux Security Hardening, Linux Performance Tuning, Containers
related: Process Management (ps, top, kill), Cron Jobs, Signals (SIGTERM, SIGKILL, SIGHUP)
tags:
  - linux
  - os
  - intermediate
  - production
---

# 134 — Systemd / Init System

⚡ TL;DR — Systemd is Linux's PID 1 — the first process started by the kernel that manages every other service, dependency ordering, logging, and system state from boot to shutdown.

| #134            | Category: Linux                                                 | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Process Management (ps, top, kill), Linux File System Hierarchy |                 |
| **Used by:**    | Linux Security Hardening, Linux Performance Tuning, Containers  |                 |
| **Related:**    | Process Management (ps, top, kill), Cron Jobs, Signals          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before systemd, SysVinit managed Linux services with shell scripts in `/etc/init.d/`. Starting Apache required running a script that started Apache — nothing else. Dependency ordering was done manually: nginx needed the network to be up, so someone had to order the scripts correctly in `/etc/rc*.d/`. If MySQL was slow to start, the app server that depended on it would fail because there was no way to express "wait for MySQL to be ready." Services started sequentially — a 20-second boot became 2 minutes on systems with dozens of services.

**THE BREAKING POINT:**
Three specific failures drove the redesign:

1. **No parallelism:** services started one-by-one; boot times grew linearly with service count.
2. **No dependency tracking:** a service could start before its dependencies were ready.
3. **No automatic restart:** a crashed service stayed dead until an admin noticed.
4. **No unified logging:** each service wrote logs to different places with different formats.

**THE INVENTION MOMENT:**
Lennart Poettering introduced systemd in 2010 with a key insight: service management is a state machine with dependencies — a problem solved by graph theory, not shell scripts. This is exactly why systemd was created: to replace hand-written init scripts with a declarative dependency graph, parallel startup, automatic restarts, and unified logging.

---

### 📘 Textbook Definition

**Systemd** is the init system and service manager used by most modern Linux distributions (Ubuntu, Debian, RHEL, Fedora, CentOS, Arch). It runs as **PID 1** — the first userspace process started by the kernel — and manages the entire lifecycle of every service from boot to shutdown. Systemd uses **unit files** (declarative INI-format configuration files in `/etc/systemd/system/` or `/lib/systemd/system/`) to describe services, sockets, timers, mounts, and targets. It provides: parallel service startup, dependency graph resolution, automatic process restarts, socket activation, cgroups-based resource limits, and the `journald` structured logging system (queried via `journalctl`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Systemd is the manager of everything that runs on Linux — it starts services in the right order, restarts them when they crash, and keeps logs for all of them.

**One analogy:**

> Systemd is an air traffic controller for processes. When the airport (server) opens (boots), ATC doesn't just tell planes to take off randomly — it sequences them based on runway availability, weather, and priority. If a plane crashes on landing (service crash), ATC immediately arranges another departure (automatic restart). Every flight is logged centrally (journald). No flight can take off without clearance from ATC.

**One insight:**
The critical insight of systemd is **socket activation**: systemd opens the listening socket for a service before the service starts. Other services that connect to that socket can start in parallel and will queue their connections in the socket buffer. When the service is finally ready, it accepts the queued connections. This eliminates the race condition of "service X needs service Y's port to be open" — the port is always open (systemd holds it).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Exactly one process is PID 1; the kernel starts it; everything else is its descendant.
2. Units are the basic unit of configuration; targets group units into runlevels.
3. `Before=`, `After=`, `Requires=`, `Wants=` define the dependency graph.

**DERIVED DESIGN:**

```
SYSTEMD UNIT FILE STRUCTURE:
/etc/systemd/system/myapp.service

[Unit]
Description=MyApp Web Service
After=network.target postgresql.service
Wants=postgresql.service
# After: start after network and postgres are running
# Wants: try to start postgres; don't fail if it's absent

[Service]
Type=simple         # process stays in foreground
User=myapp          # run as this user
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/java -jar /opt/myapp/app.jar
ExecReload=/bin/kill -HUP $MAINPID  # config reload
Restart=on-failure  # restart if exits with non-zero
RestartSec=5        # wait 5s before restart
StandardOutput=journal  # logs go to journald
StandardError=journal

[Install]
WantedBy=multi-user.target
# Enabled for multi-user runlevel (normal operation)
```

**Dependency types:**

| Directive    | Meaning                                                 |
| ------------ | ------------------------------------------------------- |
| `Requires=`  | Hard dependency; if it fails, this unit fails           |
| `Wants=`     | Soft dependency; continues even if it fails             |
| `After=`     | Start ORDER — start this after the listed unit          |
| `Before=`    | Start ORDER — start this before the listed unit         |
| `Conflicts=` | Cannot run simultaneously                               |
| `BindsTo=`   | Like Requires, plus: if dependency stops, stop this too |

**THE TRADE-OFFS:**
**Gain:** Parallel boot, automatic restarts, structured logging, cgroup resource limits, socket activation.
**Cost:** Monolithic — systemd does logging, cron (timers), network management, device management. Some engineers view this as scope creep. Unit file syntax is learned separately from shell scripting. Debugging systemd failures requires understanding its state machine.

---

### 🧪 Thought Experiment

**SETUP:**
Three services: `database` (PostgreSQL), `cache` (Redis), and `app` (Java web app). The app needs both to be running. With SysVinit, all three start at boot.

**WHAT HAPPENS WITHOUT DEPENDENCY MANAGEMENT:**
The app starts in 2 seconds. The database takes 8 seconds to start. The app attempts to connect to the database at second 3 — connection refused. App logs "database connection failed," crashes. Database finishes starting at second 8. The app is dead. An admin notices 10 minutes later, manually starts the app.

**WHAT HAPPENS WITH SYSTEMD:**

```ini
# app.service
[Unit]
After=postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Restart=on-failure
RestartSec=10
```

Systemd reads the dependency graph. It starts all three in an ordered sequence: `postgresql` and `redis` (in parallel if no dependency between them), then `app` only after both are active. If the app crashes anyway (maybe a DB query fails), `Restart=on-failure` restarts it after 10 seconds. At next restart, the database is fully ready.

**THE INSIGHT:**
Dependency management converts operational complexity (manual service ordering) into declarative configuration. The system self-heals because the dependencies are explicit and the restart policy is automatic.

---

### 🧠 Mental Model / Analogy

> Systemd is a dependency-aware process manager. Think of it as a Makefile for your services. A Makefile has targets (like `build`), dependencies (`build` requires `compile`), and rules (how to run each step). Systemd has units (like `nginx.service`), dependencies (`After=network.target`), and exec directives (`ExecStart=/usr/sbin/nginx`). Just as `make` builds targets in the right order, systemd starts services in the right order — in parallel where possible.

- "Make target" → systemd unit (`.service`, `.timer`, `.socket`)
- "Make dependency" → `After=`, `Requires=`
- "Make recipe" → `ExecStart=`
- "Make clean" → `ExecStop=`
- "Make -j8 parallel build" → systemd parallel startup

**Where this analogy breaks down:** Make is stateless — it re-runs targets from scratch. Systemd manages ongoing state: services that are running, stopped, failed, restarting. Systemd also does far more than just starting things: resource limits, socket activation, logging, timers.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Systemd is the program that starts all other programs when your Linux computer boots up. It keeps services running and restarts them if they crash. It also collects all log messages from every service in one place.

**Level 2 — How to use it (junior developer):**
`systemctl start/stop/restart/status nginx` — manage services. `systemctl enable nginx` — start nginx at boot. `journalctl -u nginx -f` — tail nginx logs. `systemctl list-units --type=service` — see all services. Create a service: write a `.service` file to `/etc/systemd/system/`, then `systemctl daemon-reload` and `systemctl enable --now myapp`.

**Level 3 — How it works (mid-level engineer):**
Systemd resolves the dependency graph using topological sort on the unit dependency declarations. It uses D-Bus for inter-service communication and socket pairs for activation. Services are placed in cgroups at startup — ensuring resource limits (CPU, memory) are enforced and processes can be reliably tracked and killed as a unit. The journal (journald) stores logs in a binary format in `/var/log/journal/`; `journalctl` decodes and queries them. Socket activation works by systemd holding the file descriptor for a listening socket; the service is started when a connection arrives, receiving the FD via `$LISTEN_FDS`.

**Level 4 — Why it was designed this way (senior/staff):**
Systemd's most controversial design decision was to absorb components traditionally handled by separate daemons: `udev` (device management), `networkd` (network), `resolved` (DNS), `logind` (login sessions), `timesyncd` (NTP), `tmpfiles` (temp file management). The argument: these are all closely coupled to the service lifecycle; centralising them eliminates race conditions and allows uniform configuration. The counter-argument (from BSD/Unix traditionalists): violates Unix philosophy of small, independent tools. In practice, systemd has become the standard on Linux — understanding it is non-optional for any Linux engineer.

---

### ⚙️ How It Works (Mechanism)

**Boot sequence:**

```
┌──────────────────────────────────────────────────────┐
│            LINUX BOOT WITH SYSTEMD                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. BIOS/UEFI → Bootloader (GRUB)                   │
│                                                      │
│  2. Kernel loads, mounts initramfs                   │
│                                                      │
│  3. Kernel executes /sbin/init (→ systemd) as PID 1 │
│                                                      │
│  4. Systemd reads default.target                     │
│     (symlink → multi-user.target or                  │
│      graphical.target)                               │
│                                                      │
│  5. Systemd resolves dependency graph                │
│     Topological sort: start A before B if B needs A  │
│                                                      │
│  6. Parallel activation of units:                    │
│     sysinit.target → basic.target → network.target  │
│     → sockets → services                            │
│                                                      │
│  7. Services run; failures trigger restart policy    │
│                                                      │
│  8. Login prompts become available                   │
└──────────────────────────────────────────────────────┘
```

**`systemctl` cheat sheet:**

```bash
# Service control
systemctl start myapp       # start now
systemctl stop myapp        # stop now
systemctl restart myapp     # stop + start
systemctl reload myapp      # reload config (SIGHUP)
systemctl status myapp      # show status + last logs

# Persistence
systemctl enable myapp      # start at boot (creates symlink)
systemctl disable myapp     # don't start at boot
systemctl enable --now myapp  # enable + start immediately

# Inspection
systemctl list-units --type=service --state=failed
systemctl list-dependencies myapp   # show dependency tree
systemctl cat myapp                 # show unit file

# System state
systemctl daemon-reload   # reload unit files after changes
systemctl isolate multi-user.target  # switch runlevel
```

**`journalctl` cheat sheet:**

```bash
journalctl -u nginx                 # all logs for nginx
journalctl -u nginx -f              # follow (tail -f equivalent)
journalctl -u nginx --since today   # today's logs
journalctl -u nginx -n 100          # last 100 lines
journalctl -p err                   # errors only (priority)
journalctl --since "2024-01-15 08:00" --until "2024-01-15 10:00"
journalctl -b                       # this boot's logs
journalctl -b -1                    # last boot's logs
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
New service file deployed: /etc/systemd/system/myapp.service
    ↓
Admin runs: systemctl daemon-reload
    ↓
Systemd re-reads unit files, rebuilds dependency graph
    ↓
Admin runs: systemctl enable --now myapp
    ↓
Systemd creates boot symlink + starts service immediately
    ← YOU ARE HERE (systemd manages service lifecycle)
    ↓
Systemd forks, sets cgroup, sets user/group, execve myapp
    ↓
myapp starts, stdout/stderr → journald
    ↓
Service runs, journalctl captures all logs
    ↓
myapp crashes → Restart=on-failure triggers after RestartSec
    ↓
Systemd restarts up to StartLimitBurst times in StartLimitInterval
```

**FAILURE PATH:**

```
myapp crashes 5 times in 10 seconds (StartLimitBurst=5)
    ↓
Systemd enters "failed" state (no more restarts)
    ↓
Observable: systemctl status myapp → "failed"
    ↓
journalctl -u myapp → last error messages
    ↓
Admin must fix and: systemctl reset-failed myapp
                    systemctl start myapp
```

**WHAT CHANGES AT SCALE:**
In Kubernetes and container environments, systemd is replaced by the container runtime (containerd/CRI-O) for service lifecycle management. The host systemd still manages system daemons (sshd, kubelet, Docker daemon), but application services run as pods. The conceptual model is identical: desired state, dependency ordering, restart policies — just expressed in Kubernetes YAML instead of systemd unit files. Understanding systemd makes Kubernetes unit file semantics immediately familiar.

---

### 💻 Code Example

**Example 1 — Complete service unit file:**

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=MyApp REST API Service
Documentation=https://github.com/company/myapp
After=network-online.target postgresql.service
Wants=network-online.target
Requires=postgresql.service

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp

# Environment
EnvironmentFile=/etc/myapp/environment
Environment=JVM_OPTS=-Xmx2g

# Start/stop/reload
ExecStart=/usr/bin/java $JVM_OPTS -jar /opt/myapp/app.jar
ExecReload=/bin/kill -HUP $MAINPID

# Restart policy
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=120   # 2 minute window
StartLimitBurst=5           # max 5 restarts in window

# Resource limits
MemoryMax=3G
CPUQuota=200%               # max 2 CPU cores

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/myapp /var/lib/myapp

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
```

**Example 2 — Systemd timer (replaces cron):**

```ini
# /etc/systemd/system/cleanup.timer
[Unit]
Description=Daily cleanup timer

[Timer]
OnCalendar=daily         # daily at midnight
Persistent=true          # run even if missed (machine was off)
RandomizedDelaySec=300   # random delay up to 5 minutes

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/cleanup.service
[Unit]
Description=Daily cleanup job
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/opt/scripts/cleanup.sh
User=nobody
```

**Example 3 — Checking service health:**

```bash
# Full status with process details
systemctl status myapp
# Output:
# ● myapp.service - MyApp REST API Service
#    Loaded: loaded (/etc/systemd/system/myapp.service; enabled)
#    Active: active (running) since Mon 2024-01-15 09:00:00 UTC; 2h 3min ago
#   Main PID: 12345 (java)
#      Tasks: 42 (limit: 1024)
#     Memory: 1.8G
#        CPU: 1min 23.456s
#    CGroup: /system.slice/myapp.service
#            └─12345 /usr/bin/java ... -jar /opt/myapp/app.jar
# Jan 15 09:00:00 server myapp[12345]: Started on port 8080

# Check restart count
systemctl show myapp --property=NRestarts

# Watch for state changes
systemctl --watch status myapp
```

---

### ⚖️ Comparison Table

| Init System | Parallel Boot   | Dependency Graph   | Auto Restart | Logging               | Best For                  |
| ----------- | --------------- | ------------------ | ------------ | --------------------- | ------------------------- |
| **Systemd** | Yes             | Declarative        | Yes          | journald (structured) | Modern Linux distros      |
| SysVinit    | No (sequential) | Manual scripts     | No           | Syslog                | Legacy systems            |
| Upstart     | Limited         | Events-based       | Yes          | Syslog                | Older Ubuntu              |
| OpenRC      | Yes             | Dependency scripts | Limited      | Syslog                | Gentoo, Alpine            |
| Supervisor  | N/A             | None               | Yes          | Stdout files          | Single-service containers |

**How to choose:** On any modern Linux distro (Ubuntu 16+, RHEL 7+, Debian 8+), systemd is the standard. Use supervisor only inside containers that need multiple co-located processes (rare; prefer one process per container). Avoid SysVinit for new systems.

---

### ⚠️ Common Misconceptions

| Misconception                                                             | Reality                                                                                                                                                                               |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `systemctl restart` is always safe                                        | Restart kills the process; in-flight requests are dropped. For zero-downtime, use `reload` (SIGHUP) if the service supports it, or configure socket activation                        |
| Changes to unit files take effect immediately                             | Must run `systemctl daemon-reload` after any unit file change, then `systemctl restart` the affected service                                                                          |
| `After=postgresql.service` means systemd waits for PostgreSQL to be ready | `After=` only waits for the unit to enter "active" state; if the service declares `Type=simple`, it's "active" immediately after exec (not after it's actually accepting connections) |
| Systemd logs are in `/var/log/syslog`                                     | Systemd uses journald, storing binary logs in `/var/log/journal/`. Use `journalctl`, not `cat /var/log/syslog` (though many distros forward to syslog too)                            |
| `Requires=` and `After=` are the same                                     | `Requires=` is about startup dependency (must succeed); `After=` is about order only. You can have `After=` without `Requires=` (start after, but don't fail if unavailable)          |
| systemd replaces cron completely                                          | Systemd timers are more powerful than cron (logging, persistent missed jobs), but cron still works and is simpler for simple periodic tasks                                           |

---

### 🚨 Failure Modes & Diagnosis

**Service Fails to Start: Dependency Ordering Issue**

**Symptom:**
`systemctl status myapp` shows "failed"; logs say "Connection refused to database:5432" at start.

**Root Cause:**
`After=postgresql.service` is set, but PostgreSQL's `Type=notify` means it enters "active" state before it's truly ready to accept connections. Myapp starts connecting too early.

**Diagnostic Command:**

```bash
systemctl status postgresql       # is it really active?
journalctl -u myapp --since boot  # first error in logs
systemd-analyze blame             # boot time per service
```

**Fix:**

```ini
# Add readiness check with ExecStartPre:
ExecStartPre=/usr/bin/pg_isready -h localhost -t 10
# Or use: Type=notify for myapp with sd_notify readiness
```

**Prevention:**
Use `ExecStartPre` health checks for external dependencies; use `Type=notify` to signal true readiness.

---

**Service Enters Restart Loop**

**Symptom:**
`systemctl status myapp` shows "activating (start)" repeatedly; `journalctl -u myapp` shows crash-restart cycles; eventually enters "failed" after hitting StartLimitBurst.

**Root Cause:**
Application crashes at startup (e.g., missing config file, bad environment variable); systemd faithfully restarts it; application crashes again.

**Diagnostic Command:**

```bash
journalctl -u myapp -n 50        # see crash messages
systemctl show myapp -p NRestarts,ActiveState
# Reset failure counter to restart investigating:
systemctl reset-failed myapp
```

**Fix:**
Fix the underlying application crash. Add `ExecStartPre` to validate preconditions before starting.

**Prevention:**
Use `StartLimitBurst` and `StartLimitIntervalSec` to limit restart speed; add alerting on `failed` state.

---

**Stale Unit File: Service Won't Reflect Changes**

**Symptom:**
You edited `/etc/systemd/system/myapp.service` but the service still behaves as before after `systemctl restart myapp`.

**Root Cause:**
Systemd caches unit files in memory. Editing the file on disk doesn't update the cached version until `daemon-reload` is run.

**Diagnostic Command:**

```bash
systemctl cat myapp    # shows the LOADED (possibly cached) unit file
diff /etc/systemd/system/myapp.service <(systemctl cat myapp)
```

**Fix:**

```bash
systemctl daemon-reload
systemctl restart myapp
```

**Prevention:**
Always `daemon-reload` after any unit file change; add to deployment scripts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management (ps, top, kill)` — systemd manages processes; understanding processes is prerequisite
- `Linux File System Hierarchy` — unit files live at `/etc/systemd/system/`; journals at `/var/log/journal/`

**Builds On This (learn these next):**

- `Cron Jobs` — systemd timers are the modern replacement for cron
- `Linux Security Hardening` — systemd unit hardening directives (`NoNewPrivileges`, `ProtectSystem`)
- `Linux Performance Tuning` — cgroups integration for CPU/memory limits per service

**Alternatives / Comparisons:**

- `Cron Jobs` — simpler task scheduling; systemd timers are more powerful but more complex
- `Supervisor` — Python-based process manager; simpler for development, lacks systemd's feature set
- `Docker` — containers replace systemd services in modern cloud deployments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ PID 1: manages all services from boot     │
│              │ to shutdown with dependency graph          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Sequential, manual service startup        │
│ SOLVES       │ with no auto-restart or unified logging   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ After= is order-only; Requires= is        │
│              │ dependency; use both to ensure correct     │
│              │ sequencing                                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always on modern Linux; write unit files  │
│              │ for every service you deploy              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Inside containers: PID 1 should be your   │
│              │ app (via ENTRYPOINT exec form), not init  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full lifecycle management vs. complexity; │
│              │ monolithic design vs. Unix philosophy     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Systemd is a Makefile for your services: │
│              │  declare dependencies, it handles order"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cron Jobs → Linux Security Hardening →   │
│              │ Linux Performance Tuning                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice `payment-service.service` has `After=database.service Requires=database.service`. The database service is `Type=simple` — it enters "active" state as soon as the process starts (before it's actually accepting TCP connections). The payment service starts and immediately tries to connect to port 5432 — connection refused. `After=` clearly isn't sufficient. List three different ways to solve this readiness synchronisation problem in systemd, explain the trade-offs of each approach, and identify which approach PostgreSQL itself recommends.

**Q2.** You run `systemctl stop myapp`. Systemd sends `SIGTERM` to the main process (PID 12345). The application has a 30-second graceful shutdown timeout (`TimeoutStopSec=30`). At second 35, the process has not yet exited. Trace exactly what systemd does next: what signal is sent, to which processes (just the main PID or the entire cgroup?), and what happens to any child processes the service may have forked. How does this behaviour differ from a Docker container receiving `docker stop` — and what does that reveal about cgroups-based process group management?
