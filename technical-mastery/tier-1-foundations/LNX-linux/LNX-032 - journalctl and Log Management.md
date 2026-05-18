---
id: LNX-032
title: journalctl and Log Management
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-031, LNX-009
used_by: LNX-069
related: LNX-031, LNX-069, LNX-026
tags: [journalctl, journald, systemd-journal, log-management, logging, syslog, rsyslog]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/lnx/journalctl-log-management/
---

## TL;DR

`journalctl` is the command for reading systemd's journal (the centralized
log store on modern Linux). Essential: `journalctl -u SERVICE -f` (follow
service logs), `journalctl --since "1 hour ago"` (time filter),
`journalctl -p err..alert` (errors and above). The journal stores logs in
binary format with metadata. For persistent logs across reboots: ensure
`/var/log/journal/` exists or `Storage=persistent` in `journald.conf`.
For logs from non-systemd sources: rsyslog/syslog writes to `/var/log/`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-032 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | journalctl, journald, systemd journal, logging, syslog, log rotation |
| **Prerequisites** | LNX-031, LNX-009 |

---

### The Problem This Solves

Application crashed at 3am. You need to see what happened. Pre-systemd:
hunt through `/var/log/syslog`, `/var/log/messages`, `/var/log/myapp/*.log`
manually. With journald: `journalctl -u myapp --since "3 hours ago"`
shows exactly what that service logged, with timestamps, severity, and
context, in one unified view. journald is the centralized log system for
all systemd-managed services.

---

### Textbook Definition

**journald** (systemd-journald): A logging daemon that collects log
messages from: kernel, initrd, system services, user services, syslog.
Stores in binary format in `/var/log/journal/` (persistent) or
`/run/log/journal/` (volatile, cleared on reboot).

**journalctl**: Command to query and display journal entries. Supports
filtering by: unit, time, priority, process, user, cursor position.

**Traditional syslog**: `/var/log/syslog` (Debian) or `/var/log/messages`
(RHEL). Still written by rsyslog/syslog-ng on many systems. journald can
forward to syslog for compatibility.

---

### Understand It in 30 Seconds

```bash
# View logs for a specific service:
journalctl -u nginx          # all logs for nginx
journalctl -u nginx -f       # follow (like tail -f)
journalctl -u nginx -n 100   # last 100 lines
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx --since "2024-01-15 14:00" --until "2024-01-15 15:00"

# By priority/severity:
journalctl -p err            # error and above
journalctl -p err..alert     # range: err, crit, alert
journalctl -u nginx -p warning  # nginx warnings and above
# Priorities: 0=emerg, 1=alert, 2=crit, 3=err, 4=warning, 5=notice, 6=info, 7=debug

# Current boot vs all:
journalctl                   # current boot
journalctl -b -1             # previous boot
journalctl --list-boots      # list all recorded boots

# Kernel messages:
journalctl -k                # kernel messages only (dmesg equivalent)

# Export formats:
journalctl -u nginx -o json  # JSON output
journalctl -u nginx -o json-pretty  # pretty JSON
journalctl -u nginx --no-pager | grep ERROR  # plain text for grep

# Disk usage:
journalctl --disk-usage
journalctl --vacuum-size=500M  # reduce journal to 500MB
journalctl --vacuum-time=30d   # remove entries older than 30 days
```

---

### First Principles

**Why binary format?**
journald stores logs in binary format (structured data, not plain text).
Benefits: (1) Indexed by time, unit, priority - fast queries. (2) Metadata
preserved (PID, UID, cgroup, executable path, etc). (3) Forward secure sealing
(cryptographic chaining to detect log tampering). (4) Compression.
Drawback: not directly grep-able. Use `journalctl | grep` or `journalctl -o json`.

**Volatile vs persistent:**
Default behavior varies by distro:
- If `/var/log/journal/` exists: persistent (survives reboot)
- If only `/run/log/journal/` exists: volatile (cleared on reboot)

To enable persistence:
```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

Or in `/etc/systemd/journald.conf`:
```ini
[Journal]
Storage=persistent    # always persistent
# Storage=volatile   # always in RAM only
# Storage=auto       # persistent if directory exists (default)
```

---

### Thought Experiment

Production incident. Application serving 500 errors since 14:32.
Deploy happened at 14:31. Root cause investigation:

```bash
# Step 1: what did the service log at 14:31-14:35?
journalctl -u myapp \
    --since "2024-01-15 14:30" \
    --until "2024-01-15 14:40"

# Step 2: look at errors only
journalctl -u myapp --since "14:30" -p err

# Step 3: what did the deploy do?
journalctl --since "14:30" --until "14:35" \
    | grep -i "deploy\|restart\|start"

# Step 4: what kernel messages (OOM? network issues?)
journalctl -k --since "14:30" --until "14:40"

# Step 5: are there other services that also show errors?
journalctl -p err --since "14:30" | head -50

# Root cause found: OOM killer at 14:32 killed the database connection pool
# journalctl -k shows: "Out of memory: Kill process 12345 (postgres) score"
```

---

### Mental Model / Analogy

journald is like a **structured flight recorder (black box) for Linux:**

```
Traditional syslog = a long strip of paper tape rolling out:
  [timestamp] info message text...
  [timestamp] error message text...
  Grep is the only way to search it.
  If the paper is cut (reboot), old entries are gone.

journald = digital flight recorder:
  Every event stored with full metadata:
    - exact timestamp (microsecond)
    - service/unit name
    - priority level
    - process ID, user ID
    - cgroup path
    - hostname
    - machine ID
  Indexed for fast querying.
  Multiple query dimensions:
    "show errors from nginx during this time range"
    vs
    "grep ERROR nginx.log" (only finds the word ERROR)
    
The recording is persistent across reboots (if configured).
journalctl --list-boots shows each boot as a chapter in the record.
```

---

### Gradual Depth - Five Levels

**Level 1:**
`journalctl -u service -f` and `journalctl -u service -n 100`. These
cover 80% of day-to-day log viewing for service troubleshooting.

**Level 2:**
Time filters: `--since`, `--until`, `-b` (boot). Priority filter: `-p`.
Multiple units: `journalctl -u nginx -u myapp`. Follow a live incident:
`journalctl -f -p warning` (all warnings and above, live).
Output format: `-o short` (default), `-o json`, `-o json-pretty`, `-o cat`.
Export to text for grep: `journalctl -u service --no-pager`.

**Level 3:**
Field matching: `journalctl _SYSTEMD_UNIT=nginx.service _PRIORITY=3`
(using journal native fields). `journalctl SYSLOG_IDENTIFIER=myapp`
(match by syslog identifier). View at a specific cursor: `journalctl --cursor=...`
(useful for log shipping without duplication). Rate limiting: journald
throttles services that log too fast. Check with `journalctl --disk-usage`.

**Level 4:**
journald configuration (`/etc/systemd/journald.conf`):
`RateLimitInterval` and `RateLimitBurst` (tune to prevent log loss).
`SystemMaxUse=500M` (limit disk usage). `MaxRetentionSec=30day`.
Forwarding to syslog: `ForwardToSyslog=yes` (enable for rsyslog integration).
Remote logging: `systemd-journal-remote` or `journald-remote` to centralize
logs from multiple hosts. Forward to Elasticsearch: Filebeat with journald
input, or `journalctl -f -o json | logstash`.

**Level 5:**
Log shipping at scale: journald is a local store, not a distributed system.
Production at scale uses: Fluentd/Filebeat reads journald (via journald input
or socket), ships to Elasticsearch/Opensearch/Splunk/Loki. Kubernetes:
pods write to stdout/stderr -> container runtime collects -> fluentd/logstash
-> centralized store. The architecture: local journald is the primary short-term
store, centralized system is the queryable long-term store.

---

### Code Example

**Useful journalctl queries:**
```bash
# Service startup errors:
journalctl -u myapp --since boot -p err

# Find specific error across all services:
journalctl --since "1 hour ago" | grep "connection refused"

# JSON output for scripted analysis:
journalctl -u myapp --since "1 hour ago" -o json-pretty | \
    python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        if 'MESSAGE' in e:
            print(e['__REALTIME_TIMESTAMP'], e['MESSAGE'])
    except: pass
"

# Check if service has been restarting frequently:
journalctl -u myapp | grep "Started\|Stopped\|Failed" | wc -l

# What happened in the minute before a crash:
systemctl show myapp -p ExecMainExitTimestampMonotonic
# Get the timestamp, then:
journalctl -u myapp --until "crash_timestamp" -n 200

# Monitor all services for errors in real-time:
journalctl -f -p err -o short-iso

# Export logs to file for offline analysis:
journalctl -u myapp \
    --since "2024-01-15" \
    --until "2024-01-16" \
    --no-pager \
    -o short-iso \
    > myapp-jan15.log
```

**journald configuration:**
```ini
# /etc/systemd/journald.conf
[Journal]
Storage=persistent        # always save to disk
Compress=yes              # compress journal data
SystemMaxUse=2G           # max journal disk usage
SystemKeepFree=1G         # keep at least 1G free
MaxRetentionSec=30day     # delete entries >30 days old
RateLimitInterval=30s     # rate limit window
RateLimitBurst=10000      # max messages per window
ForwardToSyslog=yes       # also write to rsyslog
```

```bash
# Apply config changes:
sudo systemctl restart systemd-journald

# Check result:
journalctl --disk-usage
journalctl --verify    # verify journal integrity
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "journalctl shows logs from all time" | By default, journalctl shows the current boot only. Use `journalctl -b -1` for the previous boot, `journalctl -b -2` for two boots ago, or `journalctl --list-boots` to see all available boots. Persistent logs require `/var/log/journal/` to exist. |
| "journald replaces /var/log/ files" | journald captures systemd-managed service logs. Traditional log files (`/var/log/nginx/access.log`, `/var/log/myapp.log`) written by applications directly to files are NOT in journald. Both systems coexist. rsyslog can write to both journald and log files. |
| "-p err shows only ERROR level" | `-p err` shows `err` AND HIGHER SEVERITY (emerg, alert, crit, err). To see ONLY err: use `-p err..err`. Syslog priority is inverted: 0=most severe, 7=debug. So `-p err` = `-p 3` = show levels 0,1,2,3. |
| "Journal logs are always lost on reboot" | Depends on configuration. If `/var/log/journal/` exists, logs persist across reboots. If only `/run/log/journal/` exists, logs are lost on reboot. Check: `ls /var/log/journal/` - if it exists, logs are persistent. Create it to enable persistence. |
| "journalctl is too slow for production use" | journald indexes by time, unit, priority. Queries with time filters and unit filters are fast (indexed). Unfiltered full-scan queries can be slow on large journals. Use specific filters for fast queries. For 50GB+ journals: consider reducing journal size with `SystemMaxUse` or ship logs to Elasticsearch for large-scale analysis. |

---

### Failure Modes & Diagnosis

**Journal disk full:**
```bash
# Check journal size:
journalctl --disk-usage

# Vacuum (reduce journal size):
journalctl --vacuum-size=1G    # reduce to 1GB
journalctl --vacuum-time=7d    # remove entries >7 days

# Permanent limits in /etc/systemd/journald.conf:
[Journal]
SystemMaxUse=2G
MaxRetentionSec=14day
# Then:
systemctl restart systemd-journald
```

**Service logs missing (rate limited):**
```bash
# Check for rate limit messages:
journalctl -u systemd-journald | grep "messages suppressed"
# Or:
journalctl | grep "rate limit"

# Fix: increase rate limit in journald.conf
[Journal]
RateLimitInterval=30s
RateLimitBurst=50000    # increase from default 10000

# Application fix: reduce log verbosity (don't log every request)
# Or: use WARN level only in production
```

---

### Related Keywords

**Foundational:**
LNX-031 (systemd), LNX-009 (File Viewing)

**Builds on this:**
LNX-069 (Log Rotation), LNX-104 (Observability)

**Related:**
LNX-026 (grep - for text logs), LNX-032 works alongside rsyslog

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `journalctl -u svc` | All logs for service |
| `journalctl -u svc -f` | Follow service logs live |
| `journalctl -u svc -n 100` | Last 100 lines |
| `journalctl -u svc -p err` | Errors and above |
| `journalctl -u svc --since "1h ago"` | Last 1 hour |
| `journalctl -b` | Current boot logs |
| `journalctl -b -1` | Previous boot |
| `journalctl -k` | Kernel messages |
| `journalctl -f -p warning` | All warnings live |
| `journalctl --disk-usage` | Journal size |
| `journalctl --vacuum-size=1G` | Reduce journal size |

**3 things to remember:**
1. Default: current boot only - add `-b` flags or `--since` for broader time range
2. `-p err` = errors AND MORE SEVERE (0-3 in syslog priority where 0=emergency)
3. `--no-pager` needed to pipe journalctl output to grep or other commands

---

### Transferable Wisdom

journald's structured logging model (every log event has metadata: timestamp,
source, priority, process) is the foundation of modern observability.
Elasticsearch documents, Splunk events, and Datadog logs all follow the same
principle: logs as structured records, not text strings. The query model
(`journalctl -u nginx -p err --since "1 hour ago"`) is the same as
Kibana queries, Splunk SPL, Datadog log queries. Learning structured log
querying in journalctl prepares you for every enterprise logging system.

The journal cursor concept (a position in the log stream) is the same as:
Kafka consumer offsets, Elasticsearch scroll API, database cursors. The
pattern: mark your position, ship everything after it, advance the cursor.
Used in log-shipping systems (Filebeat reads journald cursor position to
ship incrementally without duplication).

---

### The Surprising Truth

journald's binary format stores each log entry with a cryptographic hash
of the previous entry (forward secure sealing). This creates a chain:
if someone modifies or deletes log entries, the chain breaks and `journalctl --verify`
detects the tampering. This makes the journal suitable as an audit trail
for compliance purposes - the same property blockchains use for immutability.
However, this only applies when using sealing (`journalctl --setup-keys` to
initialize FSS). Most production systems don't use this feature because they
ship logs to centralized systems. The feature exists, is cryptographically
sound, and is almost universally unused - a solution looking for adoption.

---

### Mastery Checklist

- [ ] Can view service logs with time and priority filters
- [ ] Can follow logs in real-time with -f
- [ ] Can check logs from previous boots
- [ ] Can manage journal disk usage with vacuum commands
- [ ] Can pipe journalctl output to grep for text analysis

---

### Think About This

1. You're investigating an incident that happened two days ago. You run
   `journalctl -u myapp --since "2 days ago"` but see no output. Your
   colleague can see the logs from their terminal. What might explain this
   difference, and how do you check?

2. A service is generating logs at 50,000 lines per second during a traffic
   spike. After the spike, you notice that some log entries are missing.
   What journald mechanism caused this, and how do you balance the need
   for complete logs against the risk of filling disk?

3. You need to ship logs from 50 servers to a centralized Elasticsearch
   cluster. What is the architecture? What component reads from journald
   on each server, what format does it use, and how does it avoid shipping
   the same log line twice after a server restart?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you view the logs for a specific service on a modern Linux system?
A: On systems with systemd (modern Linux), use `journalctl -u servicename`. Examples: `journalctl -u nginx` = all nginx logs, `journalctl -u nginx -f` = follow logs (live, like tail -f), `journalctl -u nginx -n 50` = last 50 lines, `journalctl -u nginx -p err` = errors and above only, `journalctl -u nginx --since "1 hour ago"` = last hour. For traditional file-based logs (nginx access/error logs, application logs that write directly to files): `tail -f /var/log/nginx/error.log` or `journalctl -u nginx --no-pager | grep "ERROR"`. Combined: `journalctl -u myapp --since "1 hour ago" -o short-iso | grep -i error` for post-incident analysis.

**Intermediate:**
Q: How does journald differ from traditional syslog-based logging (/var/log/syslog)?
A: Key differences: (1) Format: journald stores binary structured data (with metadata: PID, UID, cgroup, executable, etc). Syslog stores plain text. (2) Queryability: `journalctl -u nginx -p err --since yesterday` queries by multiple dimensions using indexes. grep on syslog = full text scan only. (3) Sources: journald collects from systemd services, kernel, and legacy syslog. Both can coexist. (4) Storage: journald in `/var/log/journal/` (binary, indexed). syslog in `/var/log/syslog` (text, one file per service). (5) Integration: journald is tightly integrated with systemd - service stdout/stderr automatically goes to journal. Old-style daemons wrote to syslog explicitly. (6) Persistence: journald volatile by default (lost on reboot) unless configured persistent. syslog files persist. In practice: most systems run both - journald captures service logs, rsyslog also writes to `/var/log/syslog` for compatibility. Log shippers (Filebeat) can read from both.

**Expert:**
Q: You're building a log aggregation system that reads from journald on 500 servers and ships to Elasticsearch. Describe the architecture and how you handle reliability.
A: Architecture: (1) Agent tier: Filebeat (or Fluentd with journald input plugin) runs on each server. It reads from the systemd journal using the journald native API (not text parsing). It maintains a cursor (journal position marker) in a state file so it knows where it left off. After restart: reads from last cursor, avoiding duplicate shipping. (2) Buffer tier: Filebeat ships to Elasticsearch directly or via Logstash/Kafka for buffering. Kafka is preferred for reliability: if Elasticsearch is down, logs accumulate in Kafka (bounded retention) rather than being lost. (3) Storage tier: Elasticsearch indexes logs by time. Index lifecycle management (ILM) rotates indices: hot (recent, SSD) -> warm (week-old, HDD) -> cold (month-old, cheaper storage) -> delete. (4) Reliability: at-least-once delivery using cursor state files. Idempotent indexing using document IDs derived from journal cursors (prevents exact duplicates on retry). (5) Rate limiting: journal on each server has rate limiting configured to prevent single noisy service from flooding the pipeline. Backpressure: Filebeat's queue fills, it slows reading from journal (natural backpressure). (6) Security: TLS for Filebeat-to-Logstash and Logstash-to-Elasticsearch. No sensitive data in log lines (application responsibility). Network isolation: log pipeline in management VLAN.
