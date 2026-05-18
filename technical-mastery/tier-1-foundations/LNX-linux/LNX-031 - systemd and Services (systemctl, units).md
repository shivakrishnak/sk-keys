---
id: LNX-031
title: "systemd and Services (systemctl, units)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-014, LNX-006
used_by: LNX-032, LNX-030
related: LNX-030, LNX-032, LNX-014
tags: [systemd, systemctl, service, unit, init, daemon, linux-startup, service-management]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/lnx/systemd-services/
---

## TL;DR

systemd is PID 1 on modern Linux: the first process, the parent of all
others, manages services and the boot sequence. `systemctl` is the
command to manage it. Essential commands: `systemctl start/stop/restart/status SERVICE`.
`systemctl enable SERVICE` = start automatically at boot. A "unit" is
systemd's configuration file defining a service, socket, timer, or mount.
`journalctl -u SERVICE` views service logs. On any modern Linux server,
if you need to manage a service, systemctl is the tool.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-031 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | systemd, systemctl, service, unit file, daemon, init, PID 1 |
| **Prerequisites** | LNX-014, LNX-006 |

---

### The Problem This Solves

Your application needs to: start automatically after server reboot,
restart if it crashes, log output to the system log, run as a specific
user, be manageable with standard commands. Without systemd: you'd write
init scripts, PID files, and log rotation manually. systemd provides all
of this declaratively through unit files. One `[Service]` section handles
what took hundreds of lines of shell scripts in the SysV init era.

---

### Textbook Definition

**systemd**: A system and service manager for Linux. Replaces SysV init.
PID 1 (the first process after kernel). Manages: service startup/shutdown
order, parallel boot (faster than old sequential SysV), socket activation,
cgroups (resource limits), logging (journald), mount points, timers.

**systemctl**: Command-line interface to systemd. Manages units.

**Unit**: A configuration file that defines a resource managed by systemd.
Types: `.service` (daemon), `.socket` (socket activation), `.timer`
(cron replacement), `.mount` (filesystem mount), `.target` (group of units),
`.path` (file system path watch).

**Unit file locations:**
- `/lib/systemd/system/`: package-installed units (don't modify)
- `/etc/systemd/system/`: admin/custom units (override here)
- `~/.config/systemd/user/`: per-user units

---

### Understand It in 30 Seconds

```bash
# Service management:
systemctl start nginx           # start service now
systemctl stop nginx            # stop service
systemctl restart nginx         # stop + start
systemctl reload nginx          # reload config (no restart)
systemctl status nginx          # show status + recent logs

# Boot-time management:
systemctl enable nginx          # enable: start at boot
systemctl disable nginx         # disable: don't start at boot
systemctl enable --now nginx    # enable AND start immediately

# Check status:
systemctl is-active nginx       # prints "active" or "inactive"
systemctl is-enabled nginx      # prints "enabled" or "disabled"
systemctl is-failed nginx       # prints "failed" or "active"

# List units:
systemctl list-units            # all active units
systemctl list-units --failed   # failed units
systemctl list-unit-files       # all installed unit files

# View logs for a service:
journalctl -u nginx             # all logs for nginx
journalctl -u nginx -f          # follow (like tail -f)
journalctl -u nginx --since today
journalctl -u nginx -n 50       # last 50 lines

# System state:
systemctl reboot
systemctl poweroff
systemctl suspend
```

---

### First Principles

**Why PID 1 matters:**
On Unix: PID 1 is the init process. It's the ancestor of all other
processes. If PID 1 dies, the kernel panics (system crash). PID 1 must
also "reap" zombie processes (collect exit status of orphaned children).
systemd as PID 1 means: it controls the entire process hierarchy, can
cgroup all processes, and becomes the parent of orphaned processes.

**Service state machine:**
```
                   enable
installed ---------> enabled (starts at boot)
                   disable
enabled  ----------> disabled (won't start at boot)
                   start
stopped  ----------> active (running)
                   stop
active   ----------> stopped
                   [crash or error]
active   ----------> failed
                   restart
failed   ----------> active (if restart policy set)
```

**cgroups integration:**
systemd places each service in its own cgroup hierarchy. This means:
- `systemctl stop nginx` kills ALL nginx processes (including children/workers)
- Resource limits (`MemoryLimit=`, `CPUQuota=`) apply to ALL processes in the service
- No process can escape its service's cgroup (unlike killing processes manually)

---

### Thought Experiment

Application crash scenario. Your Java app dies silently at 3am:

Without systemd:
- You might have a shell script wrapper that loops and restarts
- PID file management to detect if it's running
- Custom log management
- Manual cleanup of zombie processes
- No automatic resource limits

With systemd:
```ini
[Unit]
Description=MyApp Java Service
After=network.target postgresql.service

[Service]
Type=simple
User=myapp
ExecStart=/usr/bin/java -jar /opt/myapp/myapp.jar
Restart=always
RestartSec=10s
MemoryLimit=2G
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Result:
- Crashes at 3am: systemd detects exit within 1 second, restarts after 10s
- All output goes to journald (queryable with journalctl)
- Memory limited to 2GB (prevents OOM from killing other services)
- Starts after network and postgres are ready
- Starts automatically at boot (WantedBy=multi-user.target)

---

### Mental Model / Analogy

systemd is like a **hospital management system:**

```
Hospital (Linux system):
  Administrator (systemd) = manages all departments
  
Departments (services):
  nginx = reception desk
  postgresql = records department
  myapp = main service
  
Unit files = job descriptions:
  [Reception Desk]
  Required for: patients to enter
  Depends on: building is open (network.target)
  If reception fails: restart after 10 minutes
  Resources: max 1GB memory
  
systemctl = hospital administrator's commands:
  start/stop/restart = open/close/reopen department
  enable = "make this department part of normal operations"
  status = "what is this department doing right now?"
  
After= ordering = sequential dependency:
  "Don't open reception until building security (network) is up"
  "Don't open records until database is online"
```

---

### Gradual Depth - Five Levels

**Level 1:**
`systemctl start/stop/restart/status service`. `systemctl enable/disable service`.
`journalctl -u service -f`. That's enough to manage services on a server.

**Level 2:**
Unit file structure: [Unit] section (description, dependencies),
[Service] section (how to run), [Install] section (boot targets).
`Type=simple` (foreground), `Type=forking` (forks to background - old-style),
`Type=notify` (sends ready notification), `Type=oneshot` (runs once).
`ExecStartPre`, `ExecStartPost`, `ExecStop`, `ExecReload`.

**Level 3:**
`Restart=` options: `no`, `always`, `on-failure`, `on-abnormal`.
`RestartSec=` (wait before restart). `StartLimitInterval/StartLimitBurst`
(give up after N restarts in M seconds).
`Environment=` or `EnvironmentFile=` for environment variables.
`WorkingDirectory=` for setting CWD. `StandardOutput=journal` (logs to journald).

**Level 4:**
Resource limits: `MemoryLimit=2G`, `CPUQuota=80%`, `LimitNOFILE=65535`.
`User=` and `Group=` for privilege separation. `CapabilityBoundingSet=`
to limit Linux capabilities. `ProtectSystem=strict`, `PrivateTmp=true`
for security hardening. `WantedBy=` targets: `multi-user.target` (normal),
`graphical.target` (GUI), `network.target`, `timers.target`. `RequiredBy=`
creates hard dependency (vs `WantedBy=` = optional).

**Level 5:**
Socket activation: nginx-style pre-fork: systemd opens socket, passes to
service when first connection arrives (zero-downtime restarts possible).
`Type=notify` + `sd_notify()`: service signals when fully initialized
(vs `Type=simple` which signals "started" as soon as process launches).
For Java Spring Boot: `spring-boot-systemd` integration sends READY=1 when
application context is fully loaded. Transient units: dynamically create
units without files: `systemd-run --unit=mytask /bin/mycommand`.

---

### Code Example

**Creating a systemd service for a Java application:**
```ini
# /etc/systemd/system/myapp.service

[Unit]
Description=MyApp Java Application
Documentation=https://docs.example.com/myapp

# Start only after network and database are available:
After=network.target postgresql.service
Wants=postgresql.service

[Service]
# Run as dedicated user (not root):
User=myapp
Group=myapp

# Application startup:
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/java \
    -Xmx2g \
    -Xms512m \
    -jar /opt/myapp/myapp.jar \
    --spring.config.location=/etc/myapp/

# Restart policy:
Restart=on-failure
RestartSec=10s
# Give up after 5 restarts in 1 minute:
StartLimitInterval=1min
StartLimitBurst=5

# Logging:
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

# Resource limits:
MemoryLimit=3G
LimitNOFILE=65535

# Security:
PrivateTmp=true
ProtectSystem=full

# Environment:
Environment=SPRING_PROFILES_ACTIVE=production
EnvironmentFile=/etc/myapp/environment

[Install]
WantedBy=multi-user.target
```

```bash
# Deploy and start the service:
sudo cp myapp.service /etc/systemd/system/
sudo systemctl daemon-reload     # reload unit files (MUST after changes)
sudo systemctl enable --now myapp    # enable and start

# Verify:
sudo systemctl status myapp
sudo journalctl -u myapp -f      # follow logs

# Restart after config change:
sudo systemctl restart myapp

# View resource usage:
systemctl show myapp -p MemoryCurrent
# Or via cgroup:
cat /sys/fs/cgroup/system.slice/myapp.service/memory.current
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "systemctl restart and reload are the same" | `restart` stops the process and starts a new one (brief downtime). `reload` sends SIGHUP (or ExecReload command) to the RUNNING process, which reloads config without stopping. nginx: `systemctl reload nginx` = zero-downtime config reload. Not all services support reload. |
| "systemctl enable starts the service now" | `enable` only creates symlinks to start at NEXT BOOT. It doesn't start the service now. Use `systemctl enable --now service` to enable AND start immediately. Or: `systemctl enable service && systemctl start service`. |
| "systemctl stop kills all service processes" | Yes - and this is an improvement over SysV init. systemd uses cgroups to track ALL processes belonging to a service (including child processes the service spawns). `systemctl stop` kills them all. With `kill` on old SysV: child processes could outlive the daemon. |
| "Unit files should go in /lib/systemd/system/" | Package-installed units go there (managed by package manager). Your custom units go in `/etc/systemd/system/`. Files in `/etc/systemd/system/` take priority over `/lib/systemd/system/`. This is also how you override package units without modifying them. |
| "journalctl always shows all logs" | By default, journalctl shows logs from the current boot. Add `--boot=-1` for previous boot, `--since "2024-01-01"` for time range, `--no-pager` to disable paging. Journal may also be size-limited: `journalctl --disk-usage` shows how much space the journal uses. |

---

### Failure Modes & Diagnosis

**Service fails to start - "Unit entered failed state":**
```bash
# Quick check:
systemctl status myapp    # shows last few log lines

# Full log:
journalctl -u myapp -n 50    # last 50 log lines
journalctl -u myapp --since "5 min ago"   # recent logs

# Common causes:
# 1. Binary not found:
which /usr/bin/java    # verify path in ExecStart

# 2. Permission denied:
# Check User= in unit file
# Check file permissions: ls -la /opt/myapp/myapp.jar
# Check directory permissions

# 3. Missing EnvironmentFile:
# Verify /etc/myapp/environment exists and is readable

# 4. Port already in use:
ss -tlnp | grep 8080   # something else on the port?

# 5. Dependency not satisfied:
systemctl status postgresql   # check dependency is running
systemctl list-dependencies myapp  # show dependency tree

# Reload after fixing unit file:
sudo systemctl daemon-reload
sudo systemctl start myapp
```

**Service starts but dies repeatedly (restart loop):**
```bash
journalctl -u myapp -n 100    # look at multiple restart cycles
# Look for: the error that causes the crash

# Check start limit:
systemctl show myapp -p StartLimitInterval -p StartLimitBurst
# Default: 5 restarts in 10 seconds, then "unit enters failed state"

# Reset after hitting start limit:
systemctl reset-failed myapp
systemctl start myapp

# Temporarily increase restart delay for debugging:
# Add to [Service]: RestartSec=60s
# (gives you time to catch the issue before it restarts)
```

---

### Related Keywords

**Foundational:**
LNX-014 (Process Basics), LNX-006 (Terminal)

**Builds on this:**
LNX-032 (journalctl), LNX-030 (Cron - systemd timer alternative)

**Related:**
LNX-037 (Process Management), LNX-047 (Process Signals)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `systemctl start svc` | Start service now |
| `systemctl stop svc` | Stop service |
| `systemctl restart svc` | Stop + start |
| `systemctl reload svc` | Reload config (no restart) |
| `systemctl status svc` | Show status + recent log |
| `systemctl enable svc` | Start at boot |
| `systemctl disable svc` | Don't start at boot |
| `systemctl enable --now svc` | Enable and start now |
| `systemctl is-active svc` | Check if running |
| `systemctl list-units --failed` | Show failed services |
| `systemctl daemon-reload` | Reload unit files after change |
| `journalctl -u svc -f` | Follow service logs |

**3 things to remember:**
1. `daemon-reload` after EVERY unit file change - changes aren't applied without it
2. `enable` != start (use `enable --now` to do both)
3. `journalctl -u service -f` = the first debugging tool for any service issue

---

### Transferable Wisdom

systemd's declarative service management (`Restart=on-failure`, `After=network`,
`MemoryLimit=`) parallels: Kubernetes Deployment (replicas, restartPolicy,
resources), Docker Compose `restart: on-failure` and `depends_on`,
AWS ECS task definitions (health checks, restart policies). The pattern:
declare desired state (service should be running, memory-limited, restart on
failure), let the manager enforce it. This declarative operations model is
now universal: terraform, kubernetes, docker-compose all follow it.
systemd was one of the first implementations for OS-level service management.

---

### The Surprising Truth

systemd's creator, Lennart Poettering, introduced it in 2010 and it became
one of the most controversial pieces of software in Linux history. Traditional
Unix users objected: "systemd violates the Unix philosophy - it does too much."
systemd handles: init, logging (journald), networking (networkd), DNS (resolved),
NTP (timesyncd), hostname, locale, containers (nspawn), and more. Critics
called it "PID 1 that ate the world." Yet it was adopted by essentially
every major Linux distribution by 2015. The reason: systemd solved real
problems (parallel boot, dependency ordering, service restart, consistent
logging) that the old SysV init scripts couldn't solve without enormous
complexity. Today it's the de facto standard, even if the debate continues.
When you use Docker or Kubernetes: both use cgroups, which systemd popularized.
Even containerized systems have systemd's fingerprints everywhere.

---

### Mastery Checklist

- [ ] Can start, stop, restart, and check status of services
- [ ] Can enable and disable services for boot-time startup
- [ ] Can create a basic unit file for a custom application
- [ ] Can use journalctl to view and follow service logs
- [ ] Can diagnose a failing service using systemctl status and journalctl

---

### Think About This

1. You run `systemctl stop myapp` but `ps aux` still shows the java process
   running. Is this possible with a properly configured systemd service?
   What might explain this? How would you force-kill all processes belonging
   to the service?

2. Your application takes 45 seconds to fully initialize (database migrations
   on startup). The unit file uses `Type=simple`. Another service depends on
   yours via `After=myapp.service`. Will the dependent service wait until your
   app is fully ready? What unit type and integration would ensure correct
   ordering?

3. `systemctl reload nginx` vs `systemctl restart nginx` - when would you
   choose each in a production environment, and what risk does each carry?
   What must be true about the nginx configuration for `reload` to work
   correctly?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you make a service start automatically when a Linux server reboots?
A: Use systemctl enable: `sudo systemctl enable myapp`. This creates a symlink in the appropriate boot target directory (typically `/etc/systemd/system/multi-user.target.wants/myapp.service`). At boot, systemd processes all units in the target and starts enabled services. To both enable and start immediately: `sudo systemctl enable --now myapp`. To verify: `systemctl is-enabled myapp` (shows "enabled" or "disabled") and `systemctl status myapp`. The service will start on next reboot. Note: `enable` does NOT start the service now - it only configures it for future boots. Separately, the unit file needs `WantedBy=multi-user.target` in its `[Install]` section for the enable to create the correct symlink.

**Intermediate:**
Q: Write the key sections of a systemd unit file for a Java Spring Boot application that should restart on failure, run as a dedicated user, and limit memory to 2GB.
A:
```ini
[Unit]
Description=My Spring Boot Application
After=network.target

[Service]
User=myapp
Group=myapp
ExecStart=/usr/bin/java -Xmx1800m -jar /opt/myapp/app.jar
WorkingDirectory=/opt/myapp
Restart=on-failure
RestartSec=10s
MemoryLimit=2G
StandardOutput=journal
StandardError=journal
Environment=SPRING_PROFILES_ACTIVE=production
EnvironmentFile=/etc/myapp/app.env

[Install]
WantedBy=multi-user.target
```

Key decisions: `Restart=on-failure` (not `always`) = restart on non-zero exit, not on clean shutdown. `RestartSec=10s` = wait 10s before restart (avoids rapid-loop on broken start). `-Xmx1800m` + `MemoryLimit=2G` = JVM heap limited below the OS limit (buffer for JVM overhead). `EnvironmentFile` for secrets (not hardcoded in unit file). `User=myapp` for principle of least privilege.

**Expert:**
Q: Explain how systemd's Type=notify differs from Type=simple, and when you would use it for a Java Spring Boot service.
A: `Type=simple`: systemd considers the service "started" as soon as `ExecStart` launches (i.e., the moment the JVM process starts). If another service depends on yours (`After=myapp.service`), it starts immediately when the JVM launches - even though Spring Boot may take 30-60 seconds to load context, run migrations, and bind to a port. `Type=notify`: systemd waits for the service to send a `READY=1` notification via `sd_notify()` before considering it "started." Services depending on it genuinely wait until it's ready. For Spring Boot: the `spring-boot-systemd` library (or `spring-boot-starter-parent 2.3+` with `SystemdNotify`) integrates this. You add the library, configure `spring.lifecycle.timeout-per-shutdown-phase=25s`, and Spring Boot sends READY=1 when the application context is fully loaded and the server is accepting requests. The unit file needs: `Type=notify` and `NotifyAccess=main`. Without `Type=notify`: a dependent service (like a health check or load balancer registration) might try to connect before the application is ready, causing false startup failures or race conditions. This is the correct way to express "service A must be fully operational before service B starts."
