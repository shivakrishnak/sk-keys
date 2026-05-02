---
layout: default
title: "Cron Jobs"
parent: "Linux"
nav_order: 135
permalink: /linux/cron-jobs/
number: "0135"
category: Linux
difficulty: ★☆☆
depends_on: Shell Scripting, Process Management (ps, top, kill), Linux File System Hierarchy
used_by: Systemd / Init System, CI/CD, Shell Scripting
related: Systemd / Init System, Shell Scripting, Environment Variables (Linux)
tags:
  - linux
  - os
  - foundational
  - production
---

# 135 — Cron Jobs

⚡ TL;DR — Cron is Linux's built-in task scheduler: it runs commands at specified times or intervals, expressed in a five-field schedule syntax, making any command automatable and recurring.

| #135            | Category: Linux                                                       | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Shell Scripting, Process Management (ps, top, kill)                   |                 |
| **Used by:**    | Systemd / Init System, CI/CD, Shell Scripting                         |                 |
| **Related:**    | Systemd / Init System, Shell Scripting, Environment Variables (Linux) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A DBA needs to run a database backup at 2am every morning. Without automation, this requires: waking up at 2am every morning, logging in, running the backup command, waiting for it to complete, logging out, and going back to sleep. For seven days a week, 365 days a year. The team also needs to rotate log files weekly, clean up temp files daily, send a usage report every Monday, and refresh a cache every 5 minutes. Without scheduling, these tasks require permanent human vigilance.

**THE BREAKING POINT:**
Manual scheduled tasks fail in three predictable ways: they are missed (human error, illness, vacation), they are inconsistent (different operators follow slightly different procedures), and they don't scale (you cannot have a human run a task every 5 minutes). For operational automation to work, the computer must be able to run tasks without human involvement.

**THE INVENTION MOMENT:**
`cron` (from the Greek "Chronos" — time) was written for Unix in the 1970s. The key idea: a daemon that reads a table of "run this command at this time" entries and executes them automatically. This is exactly why cron was created: to remove the human from repetitive scheduled operations and make time-based automation reliable.

---

### 📘 Textbook Definition

**Cron** is a time-based job scheduling daemon that executes commands at specified intervals. It runs as a persistent background process (the `cron` or `crond` daemon) that wakes up every minute, reads crontab files, and executes any jobs whose schedule matches the current time. Each entry in a **crontab** file specifies five time fields (minute, hour, day-of-month, month, day-of-week) followed by the command to run. User crontabs are managed with `crontab -e`; system crontabs live in `/etc/cron.d/`, `/etc/cron.daily/`, `/etc/cron.weekly/`, etc. By default, cron sends job output to the user's email; redirecting to a log file is standard practice.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cron runs any command automatically at a time you specify — once a minute, once a day, or on a complex schedule like "every 15 minutes on weekdays."

**One analogy:**

> Cron is like a wall calendar with alarms. You write on each day: "At 2:00 AM: run backup." Every morning at 2 AM, the alarm goes off and the action happens automatically, whether you're asleep, on holiday, or sick. The calendar keeps running the schedule indefinitely until you change it.

**One insight:**
Cron runs with a minimal environment — `PATH=/usr/bin:/bin`, no `.bashrc` or `.bash_profile` sourced, no interactive terminal. This is why scripts that work manually often fail in cron: they rely on environment variables or PATH entries that exist in your interactive session but not in cron's bare environment. Always use absolute paths in cron commands.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Cron checks the schedule every minute; minimum granularity is 1 minute.
2. Cron runs with a minimal environment — not your login shell's environment.
3. Each user has their own crontab; root's crontab can run anything.

**DERIVED DESIGN:**

```
CRONTAB SYNTAX:
┌─────────── minute (0-59)
│ ┌───────── hour (0-23)
│ │ ┌─────── day-of-month (1-31)
│ │ │ ┌───── month (1-12 or JAN-DEC)
│ │ │ │ ┌─── day-of-week (0-7, 0 and 7=Sunday, or SUN-SAT)
│ │ │ │ │
│ │ │ │ │
* * * * *  command_to_run

EXAMPLES:
0 2 * * *     /opt/scripts/backup.sh       # 2:00 AM daily
*/15 * * * *  /opt/scripts/health_check.sh # every 15 min
0 9 * * 1     /opt/scripts/weekly_report.sh # Mon 9:00 AM
0 0 1 * *     /opt/scripts/monthly_clean.sh # 1st of month
30 3 * * 0    /opt/scripts/full_backup.sh   # Sunday 3:30 AM
0 */6 * * *   /opt/scripts/refresh_cache.sh # every 6 hours

SPECIAL STRINGS (shorthand):
@reboot    # run once at startup
@hourly    # 0 * * * *
@daily     # 0 0 * * *
@weekly    # 0 0 * * 0
@monthly   # 0 0 1 * *
@yearly    # 0 0 1 1 *
```

**THE TRADE-OFFS:**
**Gain:** Universal, zero dependencies, simple syntax, supported everywhere.
**Cost:** Minimum 1-minute granularity; no dependency tracking (if job A must run before job B, you must manage that manually); no built-in retry on failure; no locking (two cron instances of the same job can run in parallel); minimal environment causes the most common cron failures.

---

### 🧪 Thought Experiment

**SETUP:**
Your team runs a database cleanup script every night at 3 AM. The script deletes records older than 90 days. Without cron, an on-call engineer runs it manually.

**WHAT HAPPENS WITHOUT CRON:**
The engineer forgets on Monday (long day). Tuesday: database table has 91 days of data. Records are queried but not found — the app assumes records were deleted but returns empty results. Another engineer notices Wednesday, runs a catch-up cleanup. The manual process adds human-error variability to a task that should be mechanical.

**WHAT HAPPENS WITH CRON:**

```bash
# Edit crontab: crontab -e
0 3 * * * /opt/scripts/db_cleanup.sh >> /var/log/db_cleanup.log 2>&1
```

Every morning at 3:00 AM, the script runs automatically. Output is logged. If the script fails (non-zero exit), the failure is recorded in the log. Alerts can be set up to check the log. The human is removed from the critical path.

**THE INSIGHT:**
Cron's value is not cleverness — it's reliability. A task that runs consistently at the scheduled time, logs its output, and doesn't require human intervention is more valuable than a sophisticated tool that an engineer needs to remember to run.

---

### 🧠 Mental Model / Analogy

> Cron is a security guard who checks a clipboard every minute. The clipboard lists: "At 9 PM: lock the back door. At 2 AM: run the backup generator test. Every 15 minutes: check the lobby cameras." Every minute, the guard looks at the clipboard and asks: "Is it time to do any of these?" If yes, the guard does it. The guard never forgets, never takes a day off, and never misses the time.

- "Security guard" → crond daemon
- "Checking the clipboard every minute" → cron wakes up every minute
- "The clipboard entries" → crontab lines
- "Doing the task" → fork + exec the command
- "Adding a new task to the clipboard" → `crontab -e`

**Where this analogy breaks down:** The security guard does tasks sequentially; cron can run multiple jobs simultaneously (if multiple jobs are scheduled for the same minute, they all run in parallel). The guard can notice if a task takes too long; cron cannot — a job that takes longer than its interval will run concurrently with the next instance.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Cron is the alarm clock for your computer. You tell it "run this program at 2 AM every day," and it does — automatically, forever, without you needing to be there.

**Level 2 — How to use it (junior developer):**
`crontab -e` — edit your cron schedule. `crontab -l` — list current schedule. `crontab -r` — remove all cron jobs (dangerous! be careful). Always redirect output: `cmd >> /var/log/job.log 2>&1` otherwise output goes to the user's email (or is silently discarded if no mail server). Use `MAILTO=""` to suppress emails. Test your script manually first — cron's minimal PATH means scripts that work interactively often fail.

**Level 3 — How it works (mid-level engineer):**
The `crond` daemon (or `cron` on some systems) runs continuously, sleeping for the number of seconds until the next minute boundary, then waking up. For each user with a crontab, it forks a shell, sets up the environment (minimal: `HOME`, `USER`, `LOGNAME`, `PATH=/usr/bin:/bin`, `SHELL=/bin/sh`), and runs the command. System crontabs (`/etc/cron.d/`) additionally specify a username field. The `/etc/cron.daily/`, `/etc/cron.weekly/`, `/etc/cron.monthly/` directories are handled by `run-parts` — a script that runs all executable files in a directory. `anacron` fills the gap for systems that aren't always on: it tracks last-run time and runs missed jobs at next opportunity.

**Level 4 — Why it was designed this way (senior/staff):**
Cron's minimal environment is intentional: it prevents "works on my machine" bugs by forcing administrators to be explicit about every dependency. The 1-minute granularity was a practical decision in the 1970s (1-minute resolution was appropriate for all use cases then). Sub-minute scheduling requires external tools or programming. Systemd timers address cron's main weaknesses: structured logging (journald), dependency ordering, persistent missed jobs, and better random offset support. In cloud/container environments, cron is increasingly replaced by Kubernetes CronJobs, AWS EventBridge Scheduler, or managed cron services — eliminating the need to manage the scheduler daemon itself.

---

### ⚙️ How It Works (Mechanism)

**Environment comparison:**

```bash
# INTERACTIVE shell environment (what you see in terminal)
echo $PATH
# → /usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:...
# → includes ~/bin, virtualenv paths, custom tools, etc.

# CRON environment (minimal)
# Only: HOME, LOGNAME, USER, SHELL=/bin/sh, PATH=/usr/bin:/bin
# → your custom PATH additions are NOT present
# → no .bashrc or .bash_profile sourced

# To see what cron sees, run this cron job:
* * * * * env > /tmp/cron_env.txt 2>&1
```

**System crontab locations:**

```
/etc/crontab          ← system crontab (has user field)
/etc/cron.d/          ← drop-in system cron files
/etc/cron.daily/      ← scripts run once daily
/etc/cron.weekly/     ← scripts run once weekly
/etc/cron.monthly/    ← scripts run once monthly
/var/spool/cron/      ← per-user crontabs (managed by crontab cmd)
```

**`/etc/cron.d/` format (with user field):**

```
# /etc/cron.d/myapp-maintenance
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=ops@company.com

# MIN HR  DOM MON DOW  USER    COMMAND
0   2  *  *   *   myapp  /opt/myapp/scripts/nightly_cleanup.sh
*/5 *  *  *   *   myapp  /opt/myapp/scripts/health_check.sh
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Clock reaches 02:00:00
    ↓
crond wakes up, reads all crontab files
    ↓
Finds: "0 2 * * * /opt/scripts/backup.sh"
    ↓
Current time matches (minute=0, hour=2): trigger!
    ← YOU ARE HERE (cron triggers job)
    ↓
crond forks, sets minimal environment
    ↓
Exec: /bin/sh -c "/opt/scripts/backup.sh"
    ↓
Script runs, stdout/stderr captured
    ↓
If MAILTO is set: mail output to user
If redirected to log: append to log file
    ↓
crond records completion, sleeps until next minute
```

**FAILURE PATH:**

```
backup.sh fails (non-zero exit code)
    ↓
stdout/stderr output generated (error messages)
    ↓
Without redirection: sent to user's email (often dropped)
Without email setup: silently lost
    ↓
Observable: database has no new backup file
→ Failure is invisible without log monitoring
Prevention: always >> log 2>&1 AND monitor the log
```

**WHAT CHANGES AT SCALE:**
At scale, cron jobs on a single server become bottlenecks: one server runs all scheduled tasks; it becomes a single point of failure; long-running jobs block if the server is overloaded. Solutions: distribute jobs across multiple servers using distributed locks (Redis SETNX), use a dedicated job scheduler (Kubernetes CronJob, AWS Batch, Celery Beat), or use systemd timers with `RandomizedDelaySec` to spread load. Monitoring cron job completion becomes essential: dead man's switch services (Healthchecks.io, Cronitor) detect when a cron job fails to check in.

---

### 💻 Code Example

**Example 1 — Basic crontab setup:**

```bash
# Edit user crontab
crontab -e

# Content to add:
# Run backup at 2 AM every day
0 2 * * * /home/alice/scripts/backup.sh >> /home/alice/logs/backup.log 2>&1

# Clean temp files every 6 hours
0 */6 * * * find /tmp -name "*.tmp" -mtime +1 -delete >> /tmp/cleanup.log 2>&1

# Health check every 5 minutes
*/5 * * * * /home/alice/scripts/health_check.sh >> /var/log/health.log 2>&1

# View the crontab
crontab -l
```

**Example 2 — System crontab with best practices:**

```bash
# /etc/cron.d/myapp
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
MAILTO=""     # suppress email; we log to files

# Nightly backup (2:30 AM to avoid peak)
30 2 * * * myapp /opt/myapp/scripts/backup.sh \
  >> /var/log/myapp/backup.log 2>&1

# Database cleanup (3:00 AM)
0 3 * * * myapp /opt/myapp/scripts/db_cleanup.sh \
  >> /var/log/myapp/cleanup.log 2>&1
```

**Example 3 — Preventing concurrent runs (lock file):**

```bash
#!/bin/bash
# Prevent multiple instances of this cron job running
LOCKFILE="/var/run/myapp_cron.lock"
MAXAGE=3600  # lock older than 1 hour = stale

# Check for stale lock
if [[ -f "$LOCKFILE" ]]; then
    LOCK_AGE=$(( $(date +%s) - $(stat -c %Y "$LOCKFILE") ))
    if (( LOCK_AGE > MAXAGE )); then
        echo "WARNING: Removing stale lock (age: ${LOCK_AGE}s)"
        rm -f "$LOCKFILE"
    else
        echo "Another instance is running (lock age: ${LOCK_AGE}s)"
        exit 0
    fi
fi

# Create lock
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT  # remove lock on exit

# ... do work ...
echo "Job completed successfully"
```

**Example 4 — Monitoring cron job health:**

```bash
#!/bin/bash
# Add at end of cron script to ping a monitoring service
# (e.g., healthchecks.io, Cronitor, Dead Man's Snitch)

run_job() {
    /opt/myapp/scripts/nightly_process.sh
}

START=$(date +%s)
if run_job; then
    DURATION=$(( $(date +%s) - START ))
    echo "SUCCESS: completed in ${DURATION}s"
    # Ping success endpoint
    curl -fsS "https://hc-ping.com/YOUR-UUID" > /dev/null 2>&1
else
    echo "FAILURE: job exited with code $?"
    # Ping failure endpoint
    curl -fsS "https://hc-ping.com/YOUR-UUID/fail" > /dev/null 2>&1
fi
```

---

### ⚖️ Comparison Table

| Scheduler          | Min Interval | Missed Job                     | Locking                | Logging           | Best For                        |
| ------------------ | ------------ | ------------------------------ | ---------------------- | ----------------- | ------------------------------- |
| **cron**           | 1 minute     | Skipped                        | Manual                 | Manual (redirect) | Simple, universal scheduling    |
| systemd timer      | 1 second     | Persistent (`Persistent=true`) | Via cgroups            | journald          | Modern Linux, complex schedules |
| Kubernetes CronJob | 1 minute     | Configurable                   | Via concurrencyPolicy  | Pod logs          | Container workloads             |
| AWS EventBridge    | 1 minute     | No                             | Via Lambda idempotency | CloudWatch        | Serverless / AWS ecosystem      |
| Celery Beat        | Sub-second   | No                             | Via task locking       | Celery logs       | Python apps, task queues        |

**How to choose:** Use cron for simple single-server scheduled tasks. Use systemd timers when you need better logging, persistent missed jobs, or sub-minute precision. Use Kubernetes CronJobs for containerised workloads. Use managed services (AWS EventBridge) to eliminate scheduling infrastructure entirely.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                           |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Cron runs with your normal shell environment         | Cron runs with a minimal environment (PATH=/usr/bin:/bin, no .bashrc); scripts must use absolute paths or set PATH explicitly     |
| `*/5` means "5 times per hour"                       | `*/5` means "every 5 units" — `*/5` in the minute field means every 5th minute (0, 5, 10, ... 55) = 12 times per hour             |
| Cron jobs output errors visibly                      | Without output redirection, cron mails output to the user; if no mail agent is configured, output is silently lost                |
| `crontab -r` removes one job                         | `crontab -r` removes ALL cron jobs for the user; use `crontab -e` to edit and remove individual lines                             |
| Cron retries failed jobs                             | Cron runs each job once per scheduled trigger; if it fails, cron does not retry — the next run is at the next scheduled time      |
| `0 2 * * *` runs at 2:00 AM in the server's timezone | It runs at 2:00 AM in the local timezone of the server; if the server is UTC and you want 2:00 AM local time, convert accordingly |

---

### 🚨 Failure Modes & Diagnosis

**Cron Job Never Runs**

**Symptom:**
You added a cron job but it never executes; the log file is never created.

**Root Cause:**
Common causes: cron daemon not running; wrong syntax in crontab; script not executable; `MAILTO` set but no mail agent; typo in schedule.

**Diagnostic Command:**

```bash
# Is cron running?
systemctl status cron       # or: service cron status

# Check cron logs
grep CRON /var/log/syslog   # Debian/Ubuntu
grep cron /var/log/cron     # RHEL/CentOS

# Verify crontab syntax
crontab -l     # list current jobs

# Test: does this run?
* * * * * echo "cron works" >> /tmp/cron_test.log 2>&1
# Wait 1 minute and check: cat /tmp/cron_test.log
```

**Fix:**
Ensure cron is running; verify syntax; ensure script is executable (`chmod +x`); check the cron log for error messages.

**Prevention:**
After adding a cron job, immediately verify with a frequent test entry (`* * * * *`); use `crontab -l` to confirm the entry was saved.

---

**Script Works Manually, Fails in Cron**

**Symptom:**
`/opt/scripts/deploy.sh` works when run manually as the cron user; fails silently when run by cron.

**Root Cause:**
Script uses commands not in cron's PATH (e.g., `/usr/local/bin/docker`, `~/bin/myapp`); or uses environment variables set in `.bashrc` but not in cron's environment.

**Diagnostic Command:**

```bash
# Add this temporary job to see cron's environment:
* * * * * env >> /tmp/cron_env.txt 2>&1

# Run the script with cron-like environment:
env -i HOME=/root LOGNAME=root USER=root \
  PATH=/usr/bin:/bin /bin/sh /opt/scripts/deploy.sh
```

**Fix:**

```bash
# At top of cron script:
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin
source /etc/profile 2>/dev/null || true
# Use absolute paths for all commands
/usr/local/bin/docker build ...
```

**Prevention:**
Always use absolute paths in cron scripts; test with `env -i` simulation before scheduling.

---

**Overlapping Cron Runs**

**Symptom:**
A cron job that normally takes 3 minutes is scheduled every 2 minutes; multiple instances run simultaneously; they corrupt shared data or exhaust database connections.

**Root Cause:**
Cron does not prevent concurrent execution. If a job takes longer than its interval, the next scheduled run starts a new instance regardless.

**Diagnostic Command:**

```bash
# Count running instances of the script
pgrep -c -f "my_script.sh"

# Check cron log for overlapping starts
grep my_script /var/log/syslog | tail -20
```

**Fix:**
Use `flock` (Linux) to prevent concurrent execution:

```bash
# In crontab:
*/2 * * * * flock -n /var/run/my_script.lock /opt/scripts/my_script.sh
# -n: non-blocking; skip if lock is held (another instance running)
```

**Prevention:**
For jobs that may overlap their schedule, always use `flock` or a custom lock file mechanism.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Shell Scripting` — cron executes shell scripts; all scripting best practices apply
- `Process Management (ps, top, kill)` — cron jobs are processes; managing them uses the same tools

**Builds On This (learn these next):**

- `Systemd / Init System` — systemd timers are the modern alternative to cron
- `Shell Scripting` — advanced cron usage requires robust scripts with proper error handling
- `Linux Security Hardening` — cron jobs running as root are a security concern; run as least-privilege user

**Alternatives / Comparisons:**

- `Systemd Timers` — more powerful: structured logging, persistent missed jobs, dependency awareness
- `Kubernetes CronJob` — cloud-native scheduling for containerised workloads
- `Celery Beat` — application-level task scheduling for Python applications

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Time-based job scheduler: runs commands   │
│              │ at specified intervals automatically      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Repetitive scheduled tasks require        │
│ SOLVES       │ human availability and memory             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cron's minimal PATH is the #1 reason      │
│              │ cron scripts fail; always use absolute    │
│              │ paths or set PATH explicitly              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Regular maintenance, backups, reports,    │
│              │ any task that repeats on a schedule       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sub-minute intervals (use systemd timer   │
│              │ or application-level scheduler instead)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple + universal vs. no retry, no       │
│              │ locking, no dependency management        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cron never forgets; it just doesn't      │
│              │  know your PATH"                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Systemd / Init System → Shell Scripting   │
│              │ → Linux Security Hardening                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a cron job scheduled at `*/5 * * * *` (every 5 minutes). The job queries a database, processes results, and writes to a file — it normally takes 90 seconds. Due to a database slow query, one instance takes 8 minutes. Describe what happens: how many instances are running at the 5-minute, 10-minute, and 15-minute marks? What is the state of the shared output file? How would `flock -n` vs `flock -w 0` behave differently, and which is appropriate for this use case?

**Q2.** A cron job is scheduled `0 2 * * *` (2 AM daily). The server is in UTC, but your business operates in US Eastern time (UTC-5 in winter, UTC-4 in summer). To run "at 2 AM Eastern," what crontab entry would you use in winter vs. summer? Now consider: the server clock is wrong by 13 minutes. At what real-world time does the job actually run? What systemic change would eliminate timezone and clock accuracy issues from cron scheduling entirely?
