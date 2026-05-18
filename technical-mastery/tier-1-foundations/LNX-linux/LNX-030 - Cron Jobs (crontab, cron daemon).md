---
id: LNX-030
title: "Cron Jobs (crontab, cron daemon)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-006, LNX-014, LNX-024
used_by: LNX-031, LNX-069
related: LNX-031, LNX-069, LNX-029
tags: [cron, crontab, cron-daemon, scheduled-tasks, automation, crond, at]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/lnx/cron-jobs/
---

## TL;DR

Cron is the Linux job scheduler. `crontab -e` edits your user's schedule.
Crontab format: `minute hour day-of-month month day-of-week command`.
`0 2 * * *` = 2:00 AM every day. `*/5 * * * *` = every 5 minutes.
`0 0 * * 0` = midnight Sunday. Cron output goes to email (usually)
unless redirected. Always use full paths in cron commands. Log at
`/var/log/cron` or `journalctl -u cron`. For modern systems:
`systemd timers` are the alternative.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-030 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | cron, crontab, crond, scheduled tasks, automation, systemd timers |
| **Prerequisites** | LNX-006, LNX-014, LNX-024 |

---

### The Problem This Solves

You need to: rotate logs every night, back up the database every hour,
send weekly reports every Sunday, clean up temp files every morning,
check service health every minute. These are tasks that must run on a
schedule without human intervention. Cron is the standard Unix answer:
define tasks once, they run automatically on your schedule indefinitely.

---

### Textbook Definition

**cron**: A time-based job scheduler daemon (`crond`) that executes
commands at specified times. Reads configuration from crontab files.

**crontab**: (1) The configuration file format specifying when to run
commands. (2) The utility (`crontab`) for editing user crontabs.

**cron locations:**
- `crontab -l` / `crontab -e`: per-user crontabs
- `/etc/crontab`: system-wide crontab (includes user field)
- `/etc/cron.d/`: directory for system crontabs
- `/etc/cron.daily/`, `/etc/cron.hourly/`, `/etc/cron.weekly/`, `/etc/cron.monthly/`: directories with scripts that run at those intervals (managed by `run-parts`)

---

### Understand It in 30 Seconds

```
CRONTAB FORMAT:
┌─────────── minute (0 - 59)
│ ┌───────── hour (0 - 23)
│ │ ┌─────── day of month (1 - 31)
│ │ │ ┌───── month (1 - 12)
│ │ │ │ ┌─── day of week (0 = Sunday, 6 = Saturday)
│ │ │ │ │
* * * * * command_to_execute

COMMON PATTERNS:
0 2 * * *      = 2:00 AM every day
0 0 * * 0      = midnight every Sunday
*/5 * * * *    = every 5 minutes
0 */4 * * *    = every 4 hours (at the hour)
30 8 * * 1-5   = 8:30 AM Monday through Friday
0 0 1 * *      = midnight on 1st of each month
@reboot        = once at system startup
@daily         = same as 0 0 * * *
@weekly        = same as 0 0 * * 0
@hourly        = same as 0 * * * *

MANAGE CRONTABS:
crontab -l     # list current crontab
crontab -e     # edit crontab in $EDITOR
crontab -r     # REMOVE (delete) crontab (careful!)
sudo crontab -l -u username    # another user's crontab
```

---

### First Principles

**Why cron output goes to email:**
cron captures stdout and stderr from jobs and mails them to the user.
On minimal servers, no mail daemon runs, so output is silently lost.
This is why many cron jobs appear to "run but do nothing" - errors are
generated but mailed to a mailbox nobody reads.

Solution: redirect output explicitly:
```bash
# Discard all output:
0 2 * * * /opt/myapp/backup.sh > /dev/null 2>&1

# Log to file:
0 2 * * * /opt/myapp/backup.sh >> /var/log/backup.log 2>&1

# Log stdout and stderr separately:
0 2 * * * /opt/myapp/backup.sh \
    >> /var/log/backup.log 2>> /var/log/backup-errors.log
```

**Cron's execution environment:**
Cron jobs run in a MINIMAL environment:
- PATH is limited (typically only `/usr/bin:/bin`)
- No terminal, no interactive session
- HOME is set to the user's home directory
- No profile or bashrc is sourced

This is why `java` may not be found in cron (it's not in the minimal PATH).
Always use FULL PATHS:
```bash
# BAD (java not in cron's PATH):
0 2 * * * java -jar /opt/myapp/app.jar

# GOOD:
0 2 * * * /usr/bin/java -jar /opt/myapp/app.jar
# Or set PATH in crontab:
PATH=/usr/local/bin:/usr/bin:/bin:/usr/java/jdk/bin
0 2 * * * java -jar /opt/myapp/app.jar
```

---

### Thought Experiment

You set up a cron job for nightly database backup at 2am. It was working
last week. Now on Monday you notice the backup didn't run over the weekend.
Debugging sequence:

```bash
# Step 1: check if cron is running
systemctl status cron    # or: crond

# Step 2: check cron logs for your job
grep "backup" /var/log/cron     # RHEL/CentOS
journalctl -u cron | grep backup  # systemd-based

# Step 3: test the command manually as the cron user
sudo -u cron_user /opt/myapp/backup.sh
# Does it fail? What's the error?

# Step 4: check if the script can find its dependencies
sudo -u cron_user bash -c "which java && java -version"
# If java not found: update script to use /usr/bin/java

# Step 5: simulate cron environment
sudo -u cron_user env -i HOME=/home/cron_user \
    PATH=/usr/local/bin:/usr/bin:/bin \
    SHELL=/bin/sh \
    /opt/myapp/backup.sh
# This reveals environment-related failures
```

---

### Mental Model / Analogy

cron is like a **kitchen timer alarm clock that repeats:**

```
You set the alarm (crontab entry):
  "Wake me at 2:00 AM every day to take the garbage out"
  = 0 2 * * * /home/user/take_out_garbage.sh

The cron daemon is the alarm clock that never stops:
  - Runs 24/7 in the background
  - Checks every minute: "does any alarm match right now?"
  - 2:00 AM Monday: YES! Run take_out_garbage.sh
  - 2:01 AM Monday: No match. Wait.
  - 2:00 AM Tuesday: YES! Run it again.
  
The minimal environment = the alarm wakes you in a dark room:
  - You're groggy, no context (minimal PATH, no shell profile)
  - You need to know EXACTLY where things are (full paths)
  - If you need context: source it explicitly in the script
  
Cron output goes to email = if the garbage is too heavy:
  - The alarm runs, but sends a note about the problem to your inbox
  - If you don't check your inbox, you never know it failed
```

---

### Gradual Depth - Five Levels

**Level 1:**
`crontab -e` to edit, `crontab -l` to list. The 5-field format plus command.
`* = every`. `/5 = every 5`. `-` = range. `,` = list. Use full paths.
Redirect output to file.

**Level 2:**
`@reboot` for startup jobs. `/etc/cron.d/` for system crontabs (format
includes username field). `/etc/cron.daily/` scripts: drop executable script
in directory, it runs daily (via `run-parts`). `MAILTO=""` in crontab
disables email. `SHELL=/bin/bash` sets the shell. Checking cron logs:
`grep CRON /var/log/syslog` or `journalctl -u cron`.

**Level 3:**
Cron job idempotency: jobs that run again if they fail halfway should be
idempotent. Lock files to prevent overlapping: `flock -n /tmp/myapp.lock
/opt/scripts/backup.sh` exits immediately if lock is held. This prevents
jobs from stacking up if one runs longer than its interval. `flock` is
the standard solution for cron job mutual exclusion.

**Level 4:**
systemd timers vs cron: `systemctl list-timers` shows all timers.
`.timer` units define schedule, `.service` units define what to run.
Advantages over cron: dependencies, proper logging (journald), resource
limits (cgroups), retry on failure, randomized delays (to spread load).
Creating a systemd timer:
```ini
# /etc/systemd/system/myapp-backup.timer
[Unit]
Description=MyApp nightly backup

[Timer]
OnCalendar=daily
Persistent=true   # run at startup if missed

[Install]
WantedBy=timers.target
```

**Level 5:**
Distributed cron: when your application runs on multiple instances, cron
on each server runs the job N times. Solutions: (1) Run cron only on one
"cron server" (single point of failure). (2) Database-backed locking
(SELECT FOR UPDATE to claim job). (3) Distributed schedulers: Quartz
(Java), Celery Beat (Python), Kubernetes CronJob (runs once per cluster).
Kubernetes CronJob is `crontab -e` for containerized workloads - same
cron syntax, but Kubernetes handles scheduling, retries, and history.

---

### Code Example

**BAD - common cron mistakes:**
```bash
# BAD 1: commands without full paths
0 2 * * * java -jar /opt/myapp/backup.jar
# java not in cron's minimal PATH -> "java: not found" (silently failed)

# BAD 2: output not captured (errors silently lost)
0 2 * * * /opt/scripts/backup.sh
# If backup fails, cron mails error to user's mailbox
# On most servers: no mail daemon -> error silently lost

# BAD 3: no lock (overlapping jobs stack up)
* * * * * /opt/scripts/slow_job.sh
# If job takes 3 minutes, you'll have 3 running at minute 3!

# BAD 4: crontab -r instead of crontab -e
crontab -r    # DELETES ALL YOUR CRON JOBS (no warning, no undo!)
# That "r" is ONE LETTER FROM -e ... always double-check
```

**GOOD - production-safe cron job:**
```bash
# 1. The crontab entry:
# Run backup at 2:30 AM daily, log output
30 2 * * * /opt/scripts/backup.sh >> /var/log/backup.log 2>&1

# 2. The backup script with proper safety:
#!/usr/bin/env bash
set -euo pipefail

# Use full paths (cron has minimal PATH)
JAVA=/usr/bin/java
DATE=$(date +%Y%m%d)
BACKUP_DIR=/opt/backups
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

# Acquire lock to prevent overlapping runs
LOCKFILE=/tmp/backup.lock
exec 200>"$LOCKFILE"
flock -n 200 || {
    echo "$LOG_PREFIX Backup already running, exiting" >&2
    exit 1
}

echo "$LOG_PREFIX Starting backup..."

# Verify dependencies
command -v "$JAVA" > /dev/null || {
    echo "$LOG_PREFIX ERROR: java not found at $JAVA" >&2
    exit 1
}

mkdir -p "$BACKUP_DIR"
"$JAVA" -jar /opt/myapp/backup.jar \
    --output-dir="$BACKUP_DIR/$DATE"

echo "$LOG_PREFIX Backup completed: $BACKUP_DIR/$DATE"

# Cleanup: remove backups older than 30 days
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true

echo "$LOG_PREFIX Cleanup complete."
```

**Crontab examples for common tasks:**
```bash
# Edit crontab:
crontab -e

# Add these entries:
# ----------------
# Backup database every hour, on the hour:
0 * * * * /opt/scripts/db_backup.sh >> /var/log/db_backup.log 2>&1

# Rotate application logs at midnight:
0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/myapp

# Weekly report: Sunday at 8 AM:
0 8 * * 0 /opt/scripts/weekly_report.sh \
    >> /var/log/weekly_report.log 2>&1

# Health check every 5 minutes:
*/5 * * * * /opt/scripts/health_check.sh >> /dev/null 2>&1

# Temp file cleanup at 3 AM every morning:
0 3 * * * find /tmp -name "myapp-*" -mtime +1 -delete 2>/dev/null

# Run on server startup:
@reboot sleep 30 && /opt/myapp/start.sh >> /var/log/startup.log 2>&1
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Cron is always reliable" | Cron has no built-in retry on failure. No alerting except email (often not configured). No dependency management. For critical jobs: use systemd timers (Persistent=true catches missed runs) or a dedicated job scheduler with monitoring. |
| "My cron job runs fine manually but not from cron" | The most common cron problem. Cause: cron's minimal PATH doesn't include your command's directory. Fix: use full paths or set PATH at top of crontab. Also check: shell differences, missing environment variables, different working directory. |
| "`crontab -r` is close to `crontab -e`" | They are! crontab -r DELETES ALL JOBS instantly with no confirmation. If you mean to edit: `crontab -e`. To be safe, always list first: `crontab -l`. |
| "Cron time is in local timezone" | Cron uses the system timezone (TZ variable or /etc/localtime). On servers in different timezones or with UTC vs local time, cron jobs may run at unexpected times. Set TZ explicitly in crontab: `TZ=America/New_York`. |
| "Cron handles missed jobs automatically" | Classic cron does NOT catch missed jobs. If the server is down at 2am, the 2am backup doesn't run. Only systemd timers with `Persistent=true` catch missed schedules. For critical jobs: use a distributed scheduler with missed-job handling. |

---

### Failure Modes & Diagnosis

**Job runs but does nothing (silent failure):**
```bash
# Check cron log:
grep CRON /var/log/syslog        # Debian/Ubuntu
grep crond /var/log/cron         # RHEL/CentOS
journalctl -u cron | tail -50    # systemd

# Simulate cron environment manually:
sudo -u your_user env -i \
    HOME=/home/your_user \
    PATH=/usr/local/bin:/usr/bin:/bin \
    SHELL=/bin/sh \
    LOGNAME=your_user \
    /path/to/your/script.sh

# If that fails: your script has environment issues
# Fix: add full paths and explicit environment setup to script
```

**Overlapping cron jobs:**
```bash
# Symptom: multiple instances of slow job running simultaneously
ps aux | grep your_script

# Fix: use flock in cron entry
*/5 * * * * flock -n /tmp/myjob.lock /opt/scripts/slow_job.sh
# -n = non-blocking: if lock held, skip this run
# Alternative: check yourself in the script (shown above)

# For Java processes: check PID file approach
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-014 (Processes), LNX-024 (Shell Scripting)

**Builds on this:**
LNX-031 (systemd - systemd timers alternative), LNX-069 (logrotate - cron-based)

**Related:**
LNX-029 (Archives - often run from cron), LNX-068 (Backup - cron-driven)

---

### Quick Reference Card

| Entry | Meaning |
|-------|---------|
| `0 2 * * *` | 2:00 AM every day |
| `0 0 * * 0` | Midnight Sunday |
| `*/5 * * * *` | Every 5 minutes |
| `0 */4 * * *` | Every 4 hours |
| `30 8 * * 1-5` | 8:30 AM weekdays |
| `0 0 1 * *` | 1st of every month |
| `@reboot` | Once at startup |
| `@daily` | Midnight every day |
| `@hourly` | Every hour |

| Command | Purpose |
|---------|---------|
| `crontab -l` | List current crontab |
| `crontab -e` | Edit crontab |
| `sudo crontab -l -u user` | List another user's crontab |

**3 things to remember:**
1. Always use FULL PATHS in cron jobs (cron has minimal PATH)
2. Redirect output: `>> /var/log/job.log 2>&1` (or errors are silently lost)
3. `crontab -r` (not `-e`) DELETES ALL cron jobs - be careful!

---

### Transferable Wisdom

The cron syntax is the universal scheduling language. Kubernetes CronJob
uses the exact same `*/5 * * * *` format. AWS EventBridge (formerly
CloudWatch Events) uses cron syntax for scheduled rules. GitLab CI
`schedule` pipelines use cron expressions. GitHub Actions `on: schedule`
uses cron. Quartz scheduler (Java) extends it to 6-7 fields. The mental
model: 5 fields define the time, `*` = any, `/N` = every N, `-` = range,
`,` = list. Learn it once, apply everywhere.

The "run as minimal user" principle in cron (dedicated service user with
no extra permissions) is the same principle as: Docker `USER` instruction
(don't run as root in containers), systemd `User=` directive, `sudo -u`
for privilege restriction. The principle: scheduled tasks should run with
exactly the permissions they need, nothing more.

---

### The Surprising Truth

The word "cron" comes from the Greek word "chronos" (time). The original
cron was written by Ken Thompson (co-creator of Unix) for Unix Version 7
in 1979. It ran as a single process that woke up once per minute, checked
all crontabs, and launched matching jobs. This is still essentially how
modern cron works - the "wake up every minute" design means cron can't
schedule jobs more frequently than once per minute. If you need sub-minute
scheduling (every 10 seconds), you need a different approach: `while sleep 10;
do command; done &` in a background process, or a dedicated job scheduler.
The 1-minute granularity was a deliberate tradeoff: one wake-up per minute
is negligible overhead; finer granularity would cost more. Today's production
systems use this limit as a feature: it enforces that "scheduled" means
"periodic, not real-time."

---

### Mastery Checklist

- [ ] Can write a crontab entry for common schedules (daily, hourly, weekly)
- [ ] Can use crontab -l and -e safely (not -r by accident)
- [ ] Can redirect cron job output to log files
- [ ] Can use full paths and set PATH in crontab for reliable execution
- [ ] Can use flock to prevent overlapping cron job runs

---

### Think About This

1. You set up `0 2 * * * /opt/scripts/backup.sh` but the backup never
   appears to run. No error messages. Describe exactly how you would
   debug this step by step, starting from checking whether crond is
   running.

2. Your backup cron job takes 90 minutes to run but is scheduled every
   hour. At some point, you'll have two backup processes running
   simultaneously, possibly corrupting the backup. What's the cleanest
   solution to ensure only one instance runs at a time, even if the
   previous run isn't done?

3. You're deploying your application on Kubernetes and need a job that
   runs every night at 2am to clean up old data. Would you use a crontab
   on the node, a Kubernetes CronJob, or something else? What advantages
   does Kubernetes CronJob have over a raw crontab in a containerized
   environment?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you schedule a script to run every day at 2 AM on Linux?
A: Edit the user's crontab: `crontab -e`. Add the entry: `0 2 * * * /full/path/to/script.sh`. Breakdown: `0` = minute 0, `2` = hour 2 (2 AM), `* * *` = any day/month/weekday. Important practices: (1) Use full path to script and any commands inside it (cron has minimal PATH). (2) Redirect output: `0 2 * * * /full/path/to/script.sh >> /var/log/myjob.log 2>&1` (otherwise errors are silently lost or mailed to a mailbox nobody reads). (3) Verify the crontab was saved: `crontab -l`. (4) Check cron is running: `systemctl status cron` (or `crond`). (5) Check logs after the first scheduled run: `grep myjob /var/log/syslog` or `journalctl -u cron`.

**Intermediate:**
Q: Explain why a script that runs fine when executed manually often fails when run by cron.
A: Three main reasons: (1) PATH difference: when you run a script in a terminal, PATH includes your shell profile's entries (often `/usr/local/bin`, Java home, etc.). Cron's PATH is minimal: typically `/usr/local/bin:/usr/bin:/bin`. Commands like `java`, `python3`, `node` may not be in cron's PATH. Fix: use full paths in the script or set PATH at the top of the crontab. (2) Missing environment variables: your terminal has variables from ~/.bash_profile, ~/.bashrc. Cron doesn't source these. If your script uses `$JAVA_HOME`, `$DB_PASSWORD`, etc., they're undefined in cron. Fix: set them in the crontab or source them in the script. (3) Working directory: in a terminal, you run from your current directory. Cron's working directory is your home directory. Relative paths break. Fix: use absolute paths or `cd /correct/dir` at the start of the script. Diagnosis: `sudo -u cronuser env -i HOME=/home/cronuser PATH=/usr/local/bin:/usr/bin:/bin SHELL=/bin/sh /path/to/script.sh` - run the script in an environment mimicking cron's.

**Expert:**
Q: What are the advantages of systemd timers over cron for scheduling recurring tasks?
A: systemd timers offer several improvements over cron: (1) Missed job handling: `Persistent=true` in a timer means if the system was down during the scheduled time, the job runs at next boot. Cron silently skips missed runs. (2) Proper logging: cron jobs' stdout/stderr goes to email (often unconfigured). systemd timers' output goes to journald: `journalctl -u myapp-backup.service` with proper timestamps and log levels. (3) Dependencies: systemd timers can specify `After=network.target` to ensure a network-dependent job runs only after networking is up. Cron has no dependency system. (4) Resource limits: timer units can use `MemoryLimit=`, `CPUQuota=`, `IOWeight=` to constrain resource usage via cgroups. (5) Retry on failure: `Restart=on-failure` and `RestartSec=30s` for automatic retry. Cron never retries. (6) Randomized delay: `RandomizedDelaySec=30min` to spread load on a fleet of servers (all servers would otherwise run at exactly the same second). (7) Status visibility: `systemctl list-timers` shows last run, next run, and time until next run for all timers. Cron has no such overview. Disadvantages of systemd timers: more verbose to set up (requires two files: .timer and .service), less familiar syntax for time specification (OnCalendar vs cron expression), not available on systems without systemd. For simple scheduled tasks on a modern Linux server: systemd timers are usually the better choice. For portable/legacy environments: cron remains the standard.
