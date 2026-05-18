---
id: LNX-069
title: "Log Rotation and Management (logrotate)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-034, LNX-009
used_by: LNX-099
related: LNX-034, LNX-035, LNX-009
tags: [logrotate, log-management, journald, log-rotation, postrotate, copytruncate, compression, log-retention]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 69
permalink: /technical-mastery/lnx/log-rotation-management/
---

## TL;DR

**logrotate** manages log file rotation: compresses, renames, and deletes
old logs on schedule. Config: `/etc/logrotate.conf` + `/etc/logrotate.d/`.
Key directives: `daily`/`weekly`/`monthly` (frequency), `rotate 7` (keep
N copies), `compress`/`delaycompress`, `missingok`, `notifempty`,
`postrotate` (reload service after rotate), `create 644 root root`
(new file permissions), `copytruncate` (for apps that can't reopen logs).
Debug: `logrotate -d` (dry run). Force: `logrotate -f`. systemd journal
rotation: `journalctl --vacuum-size=1G` or `--vacuum-time=7d`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-069 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | logrotate, log management, journald, rotation, postrotate, copytruncate, compression |
| **Prerequisites** | LNX-034 (System logs/syslog), LNX-009 (Disk management) |

---

### The Problem This Solves

**Problem 1**: A production server's disk fills up at 3am because Nginx
access logs grew to 50 GB over the past week. Without logrotate: the
application starts failing when disk is full. With logrotate: daily rotation
compresses and keeps only 7 days of logs, capping total log disk usage at
a predictable size.

**Problem 2**: After logrotate renames `nginx/access.log` to
`nginx/access.log.1`, Nginx keeps writing to the OLD file (now called
`.log.1`) because it has an open file descriptor. New requests aren't
logged. Fix: `postrotate` script sends `nginx -s reopen` or
`systemctl reload nginx`, causing Nginx to reopen its log files.

---

### Textbook Definition

**logrotate**: A daemon/utility that automates log file management.
Runs via cron (daily, typically `cron.daily`) or systemd timer. For each
configured log: renames the current log (adds number suffix or date),
optionally compresses old logs, deletes logs older than the retention count.

**Key mechanisms:**
- **Rotation**: current `app.log` -> `app.log.1`, old `.log.1` -> `.log.2`, etc.
- **Compression**: `app.log.1` -> `app.log.1.gz` (saves 70-90% disk space)
- **Create**: after rotation, create a new empty `app.log` with configured permissions
- **postrotate**: run a command after rotation (typically SIGHUP or reload to the logging application, so it reopens its log file)
- **copytruncate**: copy log to backup, then truncate original to zero bytes. For apps that can't reopen their log file.

**journald vacuum**: systemd journal does not use logrotate. Uses `journalctl
--vacuum-size=N` or `--vacuum-time=Nd` to cap journal size or age.

---

### Understand It in 30 Seconds

```bash
# === Check logrotate status ===
# Run logrotate in debug mode (dry run - shows what WOULD happen):
logrotate -d /etc/logrotate.conf 2>&1 | head -50

# List configs:
ls /etc/logrotate.d/

# Check logrotate status file (what was rotated and when):
cat /var/lib/logrotate/logrotate.status
# logrotate state -- version 2
# "/var/log/nginx/access.log" 2024-1-15-0:0:0
# "/var/log/syslog" 2024-1-15-0:0:0

# Force immediate rotation (useful after config changes):
logrotate -f /etc/logrotate.conf
# or for a specific config:
logrotate -f /etc/logrotate.d/nginx

# === Basic logrotate config example ===
cat /etc/logrotate.d/myapp
# Config for an application that logs to /var/log/myapp/app.log:
# 
# /var/log/myapp/*.log {
#     daily              <- rotate every day
#     rotate 14          <- keep 14 rotated files (2 weeks)
#     compress           <- compress rotated files (gzip)
#     delaycompress      <- don't compress the most recent rotated file
#     missingok          <- don't error if log file missing
#     notifempty         <- skip rotation if log file is empty
#     create 640 appuser appgroup  <- create new log with these permissions
#     sharedscripts      <- run postrotate ONCE for all matched logs
#     postrotate
#         systemctl reload myapp || true
#     endscript
# }

# === Why delaycompress? ===
# Without: app.log -> app.log.1.gz (compressed immediately)
# Problem: if app is still writing to the rotated file (before reload),
#          you can't easily read it for debugging (it's compressed)
# With delaycompress: app.log -> app.log.1 (uncompressed today)
#                              -> app.log.1.gz (compressed NEXT rotation)
# So: you always have the most recent rotated log readable

# === size-based rotation (vs time-based) ===
# /var/log/myapp/*.log {
#     size 100M    <- rotate when file exceeds 100 MB
#     rotate 5     <- keep 5 copies
#     compress
#     missingok
#     postrotate
#         kill -USR1 $(cat /var/run/myapp.pid) 2>/dev/null || true
#     endscript
# }

# === copytruncate: for apps that can't reopen logs ===
# Normal rotation:
#   1. Rename app.log to app.log.1
#   2. Create new app.log
#   3. Signal app to reopen (app closes fd to old app.log, opens new)
# Problem: some apps (old Java apps, some legacy systems) hold log file open
#          and CAN'T be told to reopen without restart
# Solution: copytruncate:
#   1. COPY app.log to app.log.1
#   2. TRUNCATE original app.log to zero bytes
#   App's open fd now points to the (now empty) original file
#   App continues writing to empty app.log (no reopen needed)
# Downside: small window where log entries can be lost (between copy and truncate)

# /var/log/legacy/*.log {
#     daily
#     rotate 7
#     compress
#     copytruncate   <- for apps that can't be reloaded
# }

# === dateext: use date in filename instead of number ===
# /var/log/myapp/*.log {
#     daily
#     rotate 30
#     dateext        <- app.log.2024-01-15 instead of app.log.1
#     dateformat -%Y-%m-%d
#     compress
#     missingok
# }

# === systemd journal rotation ===
journalctl --disk-usage   # show current journal size

# Vacuum by size (keep max 1 GB of journal):
journalctl --vacuum-size=1G

# Vacuum by time (delete entries older than 7 days):
journalctl --vacuum-time=7d

# Persistent journal config in /etc/systemd/journald.conf:
# SystemMaxUse=1G        <- max disk space for journal
# MaxRetentionSec=7d     <- max age of entries
# Compress=yes           <- compress journal entries

# Apply: systemctl restart systemd-journald

# Show journal size breakdown:
journalctl --disk-usage
# Archived and active journals take up 420.0M in the file system.
```

---

### First Principles

**How logrotate rotation works (rename model):**
```
State before rotation:
  app.log          <- current, application writing here (fd open)
  app.log.1.gz     <- yesterday's rotated, compressed
  app.log.2.gz     <- 2 days ago
  app.log.3.gz     <- 3 days ago (rotate 3 config)

logrotate runs (rename model):
  1. Rename app.log.2.gz -> app.log.3.gz
  2. Rename app.log.1.gz -> app.log.2.gz  
  3. Rename app.log.1   -> app.log.1.gz  (compress if delaycompress)
  4. Rename app.log     -> app.log.1      (CRITICAL MOMENT)
  
  Problem after step 4:
    Application still has FILE DESCRIPTOR to what is NOW app.log.1
    Application writes -> goes to app.log.1
    New file doesn't exist yet!

  5. Create new app.log with "create 640 appuser appgroup"
  
  Application is STILL writing to app.log.1, not the new app.log
  
  6. Run postrotate script:
     systemctl reload nginx
     # nginx closes old fd (to app.log.1), opens new app.log
  
State after rotation:
  app.log          <- new empty file, application now writing here
  app.log.1        <- yesterday (still uncompressed due to delaycompress)
  app.log.2.gz     <- compressed
  app.log.3.gz     <- compressed, will be deleted next rotation
```

**Why postrotate is critical:**
```
Without postrotate (after logrotate renames app.log to app.log.1):
  Process table:
    nginx, PID 1234, fd[5] -> /var/log/nginx/access.log.1
  
  New request arrives -> nginx logs to fd[5]
  -> data goes to access.log.1 (the rotated file, not the new access.log!)
  
  New access.log file: empty (no one writing to it)
  access.log.1: keeps growing (nginx is writing to it)
  Rotation "worked" but did nothing useful

With postrotate:
  systemctl reload nginx
  -> nginx receives SIGHUP
  -> nginx closes all log fds
  -> nginx reopens /var/log/nginx/access.log (the NEW empty file)
  -> nginx fd[5] now -> /var/log/nginx/access.log (new file)
  
  New requests: correctly logged to new access.log
  access.log.1: contains yesterday's logs, ready for compression next cycle
  
Signal alternatives:
  - SIGHUP: most apps reopen logs (nginx, apache, syslog)
  - SIGUSR1: nginx specifically reopen logs without full reload
  - systemctl reload service: graceful reload
  - kill -HUP $(pidof nginx): send signal directly
```

---

### Thought Experiment

Diagnosing a disk full due to log management failure:

```bash
# Alarm: disk at 100% at 3am, application starting to fail

# Step 1: Find the culprit:
du -sh /var/log/* | sort -rh | head -10
# /var/log/myapp    45G
# /var/log/nginx     3G

# Step 2: See what's in the large directory:
ls -lh /var/log/myapp/
# app.log     44G  <- one file, 44 GB! Logrotate not running!
# app.log.1.gz  1.2G
# app.log.2.gz  890M

# Step 3: Why is logrotate not working?
# Check logrotate status:
cat /var/lib/logrotate/logrotate.status | grep myapp
# No entry! Logrotate has never run for myapp

# Check config:
cat /etc/logrotate.d/myapp   # does it exist?
logrotate -d /etc/logrotate.d/myapp 2>&1
# Shows: what would happen if run now

# Step 4: Emergency - truncate the huge log (preserving some):
# Copy last 10000 lines to temp, then truncate:
tail -n 10000 /var/log/myapp/app.log > /tmp/app.log.recent
truncate -s 0 /var/log/myapp/app.log
# DO NOT: rm /var/log/myapp/app.log (leaves the app writing to deleted file!)
# truncate -s 0 = zero-size the file in place (fd still valid)

# Step 5: Fix logrotate config and test:
cat > /etc/logrotate.d/myapp << 'EOF'
/var/log/myapp/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 640 appuser appgroup
    sharedscripts
    postrotate
        systemctl reload myapp 2>/dev/null || true
    endscript
}
EOF

logrotate -d /etc/logrotate.d/myapp 2>&1   # dry run
logrotate -f /etc/logrotate.d/myapp         # force rotate now
```

---

### Mental Model / Analogy

```
logrotate = a filing system for a busy office

File cabinet (log directory):
  Today's papers (app.log) = active, being written to constantly
  Yesterday's folder (app.log.1) = still readable, not compressed
  Older folders (app.log.2.gz to app.log.14.gz) = compressed, archived
  
  Without a filing system: papers pile up until they fill the office (disk full)

Rotation schedule (daily/weekly) = when to start a new folder:
  Daily: each morning, start a new "Today" folder
  Previous "Today" becomes "Yesterday" (numbered backup)

retain N = how long to keep old folders:
  rotate 14 = keep 2 weeks of history
  Folder 15 gets thrown in the shredder

compress = put old folders in zip bags:
  Logs compress 70-95% (repetitive text = excellent compression ratio)
  200 MB daily log = 10-20 MB compressed
  14 days * 20 MB = 280 MB total (vs 14 * 200 MB = 2.8 GB uncompressed)

postrotate = telling the secretary to use the new folder:
  After creating a new "Today" folder, inform the writer (the app)
  to START WRITING IN THE NEW FOLDER
  Without this: writer keeps writing in "Yesterday" (the rotated file)
  
  systemctl reload nginx = "hey Nginx, switch to the new folder"

copytruncate = photocopying instead of moving:
  For writers who REFUSE to change folders (can't be reloaded)
  Copy the full "Today" folder to "Yesterday"
  Then erase "Today" (empty it), leave it in the same place
  Writer continues filling "Today" (same location, now empty)
  Downside: very brief window between copy and erase = some papers may be lost
```

---

### Gradual Depth - Five Levels

**Level 1:**
logrotate config structure. Key directives: daily/weekly, rotate N, compress,
missingok, notifempty, postrotate. Location: `/etc/logrotate.conf` and
`/etc/logrotate.d/`. Run: cron.daily. Debug: `logrotate -d`. Force: `logrotate -f`.

**Level 2:**
delaycompress (why: debug recent logs without decompressing). copytruncate
(when apps can't reopen logs). create directive (set permissions on new log).
dateext (date-based naming). size vs periodic rotation. `sharedscripts`
(one postrotate for all matching files). `logrotate.status` for tracking.

**Level 3:**
`firstaction`/`lastaction` (run before/after all files in config block).
`olddir` (move rotated files to a different directory). `extension` and
`compressext` for custom compression. `su root root` (change user before
rotating). Custom compressors (`compresscmd gzip; compressoptions -9`).
systemd journal configuration (`journald.conf`: SystemMaxUse, MaxRetentionSec).

**Level 4:**
logrotate with multiple patterns and different schedules: dev logs (daily,
short retention) vs access logs (daily, long retention) vs audit logs
(monthly, very long retention). Integration with external log shipping:
rotating BEFORE fluentd/Filebeat reads (file position tracking). `logrotate`
race conditions: postrotate timing, `prerotate` for flush before rotate.
Application log framework configuration: Java `log4j2.xml` rolling appender
vs OS-level logrotate.

**Level 5:**
Centralized log management at scale: local logrotate becomes less relevant
when logs ship to Elasticsearch/Splunk in real time. Log shipper (Filebeat,
fluentd) reads files and tracks position - logrotate rotation doesn't lose
data if the shipper tracks by inode. `copytruncate` vs rename + reopen:
the window for data loss in copytruncate. Immutable log archives: write
logs to WORM storage (S3 with Object Lock) for compliance. Log retention
policies by regulation: PCI DSS (1 year), HIPAA (6 years), GDPR (3 months
for access logs).

---

### Code Example

**BAD - logrotate configuration mistakes:**
```bash
# BAD 1: No postrotate for a service that can't reopen logs:
/var/log/nginx/*.log {
    daily
    rotate 7
    compress
    # NO postrotate!
    # After rotation: nginx writes to renamed file (access.log.1)
    # New access.log grows SLOWER than expected
    # Eventually discover: hours of logs in the rotated file
}

# GOOD: Always add postrotate for active services:
/var/log/nginx/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        /usr/bin/systemctl reload nginx 2>/dev/null || true
        # "|| true" prevents logrotate from failing if nginx is down
    endscript
}

# BAD 2: Rotating audit logs too aggressively:
/var/log/audit/audit.log {
    daily
    rotate 7    # only 7 days - violates PCI DSS (1 year requirement)
    compress
}

# GOOD: Compliance-appropriate retention:
/var/log/audit/audit.log {
    weekly
    rotate 52   # 52 weeks = 1 year
    compress
    missingok
    notifempty
    postrotate
        /sbin/service auditd restart 2>/dev/null || true
    endscript
}

# BAD 3: Missing missingok (cron job fails if log doesn't exist yet):
/var/log/newapp/*.log {
    daily
    rotate 7
    # No missingok: if log file doesn't exist, logrotate ERRORS
    # New application that hasn't written any logs yet:
    # error: stat of /var/log/newapp/*.log failed: No such file or directory
}

# GOOD:
/var/log/newapp/*.log {
    daily
    rotate 7
    missingok    # don't error if file doesn't exist
    notifempty   # don't rotate if file is empty
}
```

**GOOD - comprehensive app log config:**
```bash
# /etc/logrotate.d/myapp: Production-grade logrotate config

/var/log/myapp/app.log {
    daily
    rotate 30              # 30 days of daily logs
    compress
    delaycompress          # most recent rotated: uncompressed for quick access
    missingok
    notifempty
    create 640 myapp myapp   # new log with app user:group and group-readable
    dateext                  # app.log.2024-01-15 (readable names)
    dateformat -%Y-%m-%d
    sharedscripts
    prerotate
        # Optional: flush application buffers before rotation
        # (if app supports SIGUSR2 for buffer flush)
        kill -USR2 $(pidof myapp) 2>/dev/null || true
        sleep 1
    endscript
    postrotate
        systemctl reload myapp 2>/dev/null || true
    endscript
}

/var/log/myapp/error.log {
    weekly                   # error log: weekly (usually smaller)
    rotate 52                # 1 year of weekly error logs
    compress
    missingok
    notifempty
    create 640 myapp myapp
    sharedscripts
    postrotate
        systemctl reload myapp 2>/dev/null || true
    endscript
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "logrotate automatically handles all logs in /var/log" | logrotate only rotates logs that are explicitly configured in `/etc/logrotate.conf` or `/etc/logrotate.d/`. Package installations add their config to `/etc/logrotate.d/` for their own logs. For custom application logs (e.g., `/var/log/myapp/`), you must add a configuration file manually. The system doesn't auto-discover log files. If a log isn't configured, it grows forever until disk fills. After creating a new logrotate config: run `logrotate -d /etc/logrotate.d/myapp` (dry run) to verify it works before waiting for the daily cron job. |
| "compress means logs are compressed immediately" | Without `delaycompress`: yes, the rotated log is immediately compressed. With `delaycompress` (recommended): the MOST RECENTLY rotated log (`.log.1`) is left uncompressed. It gets compressed on the NEXT rotation (when it becomes `.log.2`). This is intentional: if a problem occurs, you want the most recent logs readable without decompressing. Many distributions and default configs use `delaycompress` for this reason. The trade-off: slightly more disk usage for the one most-recent rotated log. |
| "logrotate runs in real-time, monitoring file sizes" | logrotate is NOT a daemon. It runs as a one-shot program, typically via `/etc/cron.daily/logrotate` (once per day). It reads each config, checks conditions (size, date), and rotates if needed. The `size` directive triggers rotation when the LOG EXCEEDS the size at the TIME logrotate runs - not instantly when the log hits the limit. If a log grows from 50 MB to 200 MB between two daily logrotate runs, the size directive doesn't kick in until the next cron run. For truly size-triggered rotation in near-real-time: some applications have built-in rolling (Java's RollingFileAppender), or use the `size` directive with hourly logrotate (create a cron in cron.hourly or a systemd timer). |
| "copytruncate is always safe as a drop-in replacement for postrotate" | copytruncate has a race condition: it (1) copies the log file to a backup, then (2) truncates the original. In the window between copy completion and truncation, new log entries written by the application appear in NEITHER the copy (already done) NOR the archive (not yet truncated). These entries are lost. For low-volume logs: this window is tiny and acceptable. For high-volume logs: can lose significant entries. Use copytruncate ONLY for applications that genuinely can't be reloaded/signaled. For applications that can be reloaded: always use the rename + postrotate + reopen approach (zero data loss). |
| "systemd journal logs use logrotate" | systemd's `journald` manages its own journal files in `/run/log/journal/` (volatile) and `/var/log/journal/` (persistent). It has its own size/retention management via `journald.conf` (`SystemMaxUse`, `MaxRetentionSec`). logrotate does NOT manage journal files. Use `journalctl --vacuum-size=1G` to manually vacuum, or configure `SystemMaxUse=1G` in `/etc/systemd/journald.conf`. Services that write to journal AND to a file (via `StandardOutput=file:/var/log/myapp.log` in systemd unit) need BOTH logrotate (for the file) AND journald config (for the journal copy). |

---

### Failure Modes & Diagnosis

**logrotate not working diagnosis:**
```bash
# Symptom: logs growing, disk filling up, logrotate config exists

# Step 1: Test the config (dry run):
logrotate -d /etc/logrotate.d/myapp 2>&1
# Look for: "error:" messages, "not modifying" (conditions not met)

# Common errors:
# "stat of /var/log/myapp/*.log failed: No such file or directory"
# Fix: add missingok directive

# "log does not need rotating (log is empty)"
# Expected with notifempty directive - log file is 0 bytes

# "log needs rotating" - but it wasn't rotated:
# May be due to: wrong user permissions, syntax error

# Step 2: Check permissions:
ls -la /var/log/myapp/
# logrotate runs as root by default
# But "create 640 appuser appgroup" requires root to change ownership
# Check: is the "su" directive needed? (if config file itself is restricted)

# Step 3: Check logrotate status:
cat /var/lib/logrotate/logrotate.status | grep myapp
# If not listed: logrotate has never run for this config
# If date is old: logrotate ran but not recently

# Step 4: Force run and observe:
logrotate -f -v /etc/logrotate.d/myapp 2>&1
# -f = force (ignore "already rotated today")
# -v = verbose (show what's being done)

# Step 5: Check if cron is running logrotate:
ls -la /etc/cron.daily/logrotate
systemctl status cron    # or crond, depending on distro
grep logrotate /var/log/cron* /var/log/syslog 2>/dev/null | tail -5
```

---

### Related Keywords

**Foundational:**
LNX-034 (System Logs), LNX-009 (Disk management)

**Builds on this:**
LNX-099 (Fleet management)

**Related:**
LNX-035 (journald/systemd logs), LNX-048 (Cron scheduling)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `logrotate -d /etc/logrotate.d/myapp` | Dry run (debug) |
| `logrotate -f /etc/logrotate.d/myapp` | Force rotation now |
| `logrotate -v /etc/logrotate.conf` | Verbose (show all actions) |
| `cat /var/lib/logrotate/logrotate.status` | Last rotation dates |
| `journalctl --disk-usage` | Journal disk usage |
| `journalctl --vacuum-size=1G` | Trim journal to 1 GB |
| `journalctl --vacuum-time=7d` | Delete entries older than 7 days |

**3 things to remember:**
1. `postrotate` to reload the application after rotation - without it, the app keeps writing to the rotated file
2. `delaycompress` = leave most recent rotated log uncompressed (readable for quick debugging)
3. `logrotate -d` for dry run debugging - runs before actual cron job to verify config works

---

### Transferable Wisdom

Log rotation concepts appear in: Java Log4j2 RollingFileAppender:
same concepts (max size, max count, compression) but implemented within the
JVM - no OS-level logrotate needed. Python's `logging.handlers.RotatingFileHandler`
and `TimedRotatingFileHandler`: same rolling behavior in application code.
AWS CloudWatch Logs retention policies: same concept (delete logs older than
N days) but managed by the cloud service. ELK/Splunk index lifecycle management:
equivalent of `rotate N` + `compress` but at petabyte scale with tiered storage.
The postrotate/signal pattern (SIGHUP to reopen files) is the standard Unix
daemon pattern for log file reopening - any well-behaved daemon supports it.
The trade-off between application-level rolling vs OS-level logrotate: application-
level gives you more control (can write to new file atomically), OS-level
is simpler to configure and works for any application regardless of language.

---

### The Surprising Truth

logrotate's default behavior when a log file is deleted externally (rm -f
log.txt while the app is running) is instructive: the application keeps
writing to an INODE that has no directory entry anymore. The data is
consumed but invisible. This is why `truncate -s 0 log.txt` is safer than
`rm log.txt` for emergency log space reclamation: truncate zeros the file
in place (same inode, same fd), while rm removes the directory entry (the
writing process's fd remains valid but points to an orphaned inode - data
still grows but `df` shows the disk space released only after the process
CLOSES its fd or is killed). In disk-full emergencies: `truncate -s 0` is
your friend. The deeper insight: this fd-keeps-inode-alive behavior is also
how logrotate's RENAME model works correctly - the application's fd remains
valid pointing to the now-renamed file, giving you a window to send the
reload signal before the data flows into the new file.

---

### Mastery Checklist

- [ ] Can write a logrotate config with daily rotation, compression, and postrotate
- [ ] Understands the difference between postrotate (reopen) vs copytruncate
- [ ] Can debug logrotate issues with -d (dry run) and -v (verbose)
- [ ] Knows how to manage systemd journal size separately from logrotate
- [ ] Can diagnose "writing to old file" issue (missing postrotate)

---

### Think About This

1. A Java application writes logs to `/var/log/javaapp/app.log` using a
   FileAppender (not a RollingAppender). The application does NOT support
   hot log file reopening - it would require a full restart to open a new
   log file, causing downtime. You need daily log rotation without any
   downtime. Which logrotate directive handles this, what is its trade-off
   (potential data loss window), and under what conditions is that trade-off
   acceptable?

2. After deploying logrotate for an Nginx server that handles 50,000
   requests/minute, the NOC team reports that every day at midnight,
   there's a 30-second gap in the access logs. Explain why this happens
   with the standard rotate + postrotate approach, and whether `copytruncate`
   or `prerotate` might be better solutions. Identify any potential pitfalls.

3. Your company's compliance team requires that application logs be retained
   for 1 year, with the ability to query any log entry from the past year
   within 15 minutes. Design a logrotate configuration for a high-volume
   application (1 GB/day) that satisfies this requirement. Calculate the
   approximate total storage needed and explain the rotation strategy.

---

### Interview Deep-Dive

**Foundational:**
Q: What does the logrotate `postrotate` directive do, and why is it necessary?
A: `postrotate` runs a shell command after logrotate renames (rotates) a log file. It's necessary because of how Unix file descriptors work: when a process opens a file, it gets a file descriptor (fd) pointing to the INODE, not the path. When logrotate renames `app.log` to `app.log.1`, the file system path changes but all open file descriptors to the old inode remain valid. The application is now unknowingly writing to `app.log.1` (the renamed file), not to the new empty `app.log`. WITHOUT postrotate: new log entries go to the rotated file (app.log.1), the new app.log stays empty, rotation effectively didn't help - the growing file is just renamed. WITH postrotate: after renaming, logrotate runs the postrotate command (typically `systemctl reload nginx` or `kill -USR1 $(pidof nginx)`). The application receives the signal, closes and reopens its log files by path - now it opens the new empty `app.log`. From this point: new entries go to the correct file. Practical commands for common services: Nginx: `nginx -s reopen` or `systemctl reload nginx`. Apache: `apachectl graceful`. Syslog: `systemctl reload rsyslog`. Custom apps: `kill -HUP $(cat /var/run/myapp.pid)`. The "graceful reload" (SIGHUP) is the Unix standard mechanism for "reopen your files without restarting."

**Expert:**
Q: How would you configure log rotation for a compliance-critical environment where logs must not be lost or tampered with?
A: Compliance-critical log management requires several layers beyond basic logrotate: (1) IMMEDIATE SHIPPING TO IMMUTABLE STORAGE: configure log shippers (Filebeat, fluentd) to forward log entries to a WORM (Write Once Read Many) destination in real time: S3 with Object Lock, Splunk, or a dedicated SIEM. This way, even if the server is compromised or logs deleted, the centralized store has an authoritative copy. logrotate becomes secondary - its job is only local disk management. (2) LOGROTATE AS SECONDARY: configure logrotate for disk management (prevent disk fill) while the centralized store is the authoritative retention system. Local: `rotate 7` (1 week). Central: 1 year (PCI DSS requirement). (3) LOG INTEGRITY: Append-only filesystem: `chattr +a /var/log/audit/audit.log` prevents deletion. SELinux labels on log directories restrict write access. `auditd` itself should log access to log directories. (4) CHECKSUMS: compute SHA256 of each rotated log file and store in a separate location: `sha256sum app.log.1 >> /var/log/checksums.txt`. Compliance auditors can verify logs weren't modified. (5) TESTED RETENTION VERIFICATION: automated test that: queries the SIEM for a 90-day-old log entry and confirms it exists + is retrievable. Documents restore time. (6) CHAIN OF CUSTODY: logrotate config should include: dateext (date-stamped filenames for clear audit trail), numeric-owner (preserve correct ownership in archives), and avoid copytruncate (use rename + reopen to prevent the data loss window). The key architectural principle: local logrotate protects disk space; the centralized immutable store protects compliance.
