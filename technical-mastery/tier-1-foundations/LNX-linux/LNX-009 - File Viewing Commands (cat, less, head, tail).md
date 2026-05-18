---
id: LNX-009
title: File Viewing Commands (cat, less, head, tail)
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-008
used_by: LNX-026
related: LNX-008, LNX-026, LNX-032
tags: [cat, less, head, tail, file-viewing, logs, reading]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/lnx/file-viewing-commands/
---

## TL;DR

Four commands cover all log and file reading needs: `cat`
(dump whole file), `less` (scrollable reader), `head`
(first N lines), `tail` (last N lines, especially -f for
live logs). In incident response, `tail -f /var/log/app.log`
is the most-used command - it streams new log entries as
they appear. These four commands are your eyes into every
running system.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-009 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | cat, less, head, tail, log viewing, file reading |
| **Prerequisites** | LNX-008 |

---

### The Problem This Solves

During an incident, you need to read log files. On a production
server with no GUI and no text editor open, you need commands
to view file contents. These four commands are the workhorse
tools for reading any text file - from config files to
multi-gigabyte log files - without loading the entire file
into memory.

---

### Textbook Definition

**cat** (concatenate): outputs the entire content of one or
more files to stdout. Original use: concatenate files together.
Modern use: quick look at small files.

**less**: a "pager" - displays file content one screen at a time.
Allows scrolling up/down, searching, jumping to end. Does NOT
read entire file into memory (can handle huge files).

**head**: outputs the first N lines of a file (default: 10).

**tail**: outputs the last N lines (default: 10). With `-f`
(follow): monitors the file and outputs new lines as they appear.

---

### Understand It in 30 Seconds

```
Small file, quick look:
  cat /etc/nginx/nginx.conf      # dumps entire file

Large file, need to scroll:
  less /var/log/syslog           # opens scrollable reader
  (press q to quit, / to search, G to jump to end)

First few lines (check file header, format):
  head -20 /var/log/app.log      # first 20 lines
  head -1 /var/log/app.log       # first line only

Last few lines (check recent activity):
  tail -50 /var/log/app.log      # last 50 lines
  tail -f /var/log/app.log       # LIVE: stream new lines
  tail -F /var/log/app.log       # LIVE: follows even if rotated

For real-time monitoring during incidents:
  tail -f /var/log/app.log | grep ERROR   # only show ERROR lines live
```

---

### First Principles

**Why not always use cat?**
`cat bigfile.log` on a 10GB log file dumps everything to your
terminal at max speed. Your terminal buffer fills and scrolls.
You see only the last few thousand lines. Everything before
is gone. It also reads the entire file into terminal buffer.

**less loads lazily:**
`less bigfile.log` opens immediately (milliseconds). It reads
only what's needed for the current screen. You can navigate
through a 10GB file without loading it all. Crucial for
production debugging.

**tail -f uses inotify:**
`tail -f` doesn't poll the file every second (that would be
expensive). It uses Linux's `inotify` or `fanotify` interface:
the kernel notifies tail when the file changes. Zero CPU usage
between writes. Instant notification when new lines appear.
This is why `tail -f` is the right tool for live log monitoring.

---

### Thought Experiment

You're debugging a production Java application at 3am. The app
started throwing 500 errors 10 minutes ago. You need to see what
happened. The log file is 5GB.

Option A: `cat /var/log/myapp/app.log` -> dumps 5GB to your terminal
-> useless; you can't see anything; terminal frozen for minutes

Option B: `tail -100 /var/log/myapp/app.log` -> last 100 lines
-> shows the recent errors immediately

Option C: `tail -f /var/log/myapp/app.log | grep "ERROR\|EXCEPTION"`
-> live stream of only error lines

Option B + C = how you actually debug production issues with logs.

---

### Mental Model / Analogy

Think of a log file as a very long receipt:

```
cat = reading the entire receipt aloud from start to finish
  (useful for short receipts; torture for 10-page receipts)
  
less = flipping through the receipt page by page
  (you control the pace; can search, jump to sections)
  
head = reading only the top of the receipt
  (useful for: what store is this? what's the date/header?)
  
tail = reading only the bottom of the receipt
  (useful for: what was the last thing purchased? total?)
  
tail -f = standing at the cash register watching new items
          being rung up in real time
  (useful for: live monitoring as events happen)
```

---

### Gradual Depth - Five Levels

**Level 1:**
cat = full file. less = scrollable. head = first lines. tail = last
lines. tail -f = live streaming. That's 90% of what you need.

**Level 2:**
less navigation: j/k (line scroll), f/b (page scroll), / (search
forward), ? (search backward), n (next match), q (quit), G (end
of file), g (start of file), :n (next file if multiple).

**Level 3:**
`tail -f` vs `tail -F`: -f follows the file descriptor (breaks if
log rotated); -F follows the filename (reconnects if rotated).
Use -F in production with log rotation. Combine: `tail -f *.log`
watches multiple log files simultaneously, prefixes each line with
filename.

**Level 4:**
For very large binary files or logs with binary data, `less -S`
(no line wrapping) and `less -N` (line numbers) help. `less` can
also handle compressed files via lessopen filter: `less app.log.gz`
decompresses on-the-fly without creating a temp file. `multitail`
or `lnav` provide more advanced multi-file log viewing with
highlighting.

**Level 5:**
At production scale with distributed logs: tail -f is insufficient.
Logs are aggregated to centralized systems (ELK, Loki, Datadog).
tail -f is a local debugging tool. For distributed tracing: you
need to correlate logs by trace ID across multiple services.
`grep traceId=abc123 /var/log/service-*.log` becomes: query
your log aggregation system with trace_id filter.

---

### Code Example

**BAD - inefficient log analysis:**
```bash
# BAD: reads entire file; slow for large files
cat /var/log/app.log | grep "ERROR"

# BAD: cat + grep is redundant (useless use of cat)
cat file.txt | head -10

# BAD: watching a rotated log with -f (loses new file)
tail -f /var/log/nginx/access.log   # breaks after log rotation!
```

**GOOD - efficient log analysis:**
```bash
# GOOD: grep directly (no cat needed)
grep "ERROR" /var/log/app.log

# GOOD: head/tail directly
head -10 file.txt

# GOOD: watch rotated logs correctly
tail -F /var/log/nginx/access.log   # follows filename, not fd

# GOOD: live error monitoring during incident
tail -F /var/log/myapp/app.log | grep --line-buffered "ERROR\|FATAL\|Exception"
# --line-buffered: flushes each line immediately (important for pipe)

# GOOD: show last 100 lines AND follow new lines
tail -n 100 -F /var/log/myapp/app.log

# GOOD: monitor multiple log files simultaneously
tail -F /var/log/nginx/error.log /var/log/myapp/app.log
# Prefixes each line with filename

# GOOD: check a compressed log without extracting
less /var/log/myapp/app.log.1.gz   # if lessopen configured
# Or:
zcat /var/log/myapp/app.log.1.gz | grep "ERROR"
```

---

### less Navigation Reference

```
Navigation:
  q          quit less
  SPACE      page down
  b          page up
  j / DOWN   line down
  k / UP     line up
  g          go to beginning
  G          go to end
  
Search:
  /pattern   search forward
  ?pattern   search backward
  n          next match
  N          previous match
  
Display:
  -S         toggle line wrapping
  -N         toggle line numbers
  F          follow mode (like tail -f)
  
Files:
  :n         next file (if opened with: less *.log)
  :p         previous file
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "cat is for concatenating files" | Originally yes. But in practice 99% of cat usage is viewing single files. `cat file1 file2 > combined` is the original concatenate use. |
| "`tail -f` works after log rotation" | No! `-f` follows the file descriptor, which becomes invalid after rotation. Use `-F` to follow the filename, which reconnects to the new file after rotation. |
| "more is like less" | `more` is the older pager (scroll forward only). `less` can scroll in both directions. Use `less`. The name "less" is a Unix joke: "less is more." |
| "`head -f` follows like `tail -f`" | No. There is no `head -f`. Only tail has follow mode. |
| "You need cat to use less" | `less filename` directly. No cat needed. `cat file | less` is redundant. |

---

### Failure Modes & Diagnosis

**tail -f breaks after log rotation (most common issue):**
```bash
# Symptom: tail -f stops showing output after midnight
# (log rotation creates new file, old fd is now empty)

# Diagnosis: check if the file has been rotated
ls -la /var/log/nginx/access.log*
# access.log (new, empty)
# access.log.1 (old, full - your tail is watching this)

# Fix: use -F (capital F) instead of -f:
tail -F /var/log/nginx/access.log  # follows filename
# When rotation happens: reconnects to new access.log
```

**Large file freezes cat:**
```bash
# Symptom: cat on 5GB log file, terminal freezes for minutes
# Nothing useful in output

# Fix: use tail for recent lines, grep for specific content
tail -1000 /var/log/bigapp.log | grep "ERROR"
# Or: grep directly (reads file efficiently)
grep "ERROR" /var/log/bigapp.log | tail -50
```

**Security: log files exposing sensitive data:**
```bash
# Check if logs contain passwords or tokens:
grep -i "password\|token\|secret\|api_key" /var/log/myapp/app.log
# If found: this is a security incident
# Immediate actions:
#   1. Rotate the credentials that were logged
#   2. Fix the logging to redact sensitive fields
#   3. Consider if log file was accessed by unauthorized parties
#   4. Apply file permissions: chmod 640 /var/log/myapp/app.log
#      (owner=app, group=logs, others=no access)
```

---

### Related Keywords

**Foundational:**
LNX-008 (Files and Directories), LNX-015 (Standard Streams)

**Builds on this:**
LNX-026 (grep), LNX-027 (sed), LNX-028 (awk),
LNX-032 (journalctl and Log Management)

**Related:**
LNX-016 (Pipes and Redirection)

---

### Quick Reference Card

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `cat file` | Print entire file | -n (line numbers) |
| `less file` | Scrollable viewer | -S (no wrap), -N (line nums) |
| `head file` | First 10 lines | -n N (first N lines) |
| `tail file` | Last 10 lines | -n N (last N), -f (follow fd), -F (follow name) |
| `wc -l file` | Count lines | -c (bytes), -w (words) |
| `zcat file.gz` | View compressed | - |
| `grep "pat" file` | Search in file | -i (case-insensitive), -n (line numbers) |

**3 things to remember:**
1. `tail -F` (capital F) survives log rotation; `tail -f` does not
2. Never `cat` large files; use `less`, `tail`, or `grep`
3. `tail -f file | grep "pattern"` = live error stream during incidents

**Interview angle:**
"During a production incident, the application is throwing exceptions.
How do you monitor the logs in real time?" -> `tail -F /var/log/myapp/app.log | grep --line-buffered "ERROR\|Exception"` or better: check your centralized logging (Loki/ELK) for aggregated view.

---

### Transferable Wisdom

The `tail -f` pattern (stream new events as they occur) is the
primitive behind all real-time log aggregation. Filebeat, Logstash,
Fluentd all do the same thing: tail log files and forward new lines
to centralized storage. Understanding `tail -f` helps you understand
how these tools work at the fundamental level.

The **lazy reading** principle of `less` (load only what's needed for
the current view) is the same principle behind database cursor pagination
and virtual DOM rendering. Never load more than you need to display.

---

### The Surprising Truth

`less` can read from pipes: `grep "ERROR" /var/log/app.log | less`.
The `F` command in less (while in less) switches to follow mode -
like `tail -f`. So you can open a log with `less /var/log/app.log`,
jump to the end with `G`, then press `F` to start following new
entries live. Press Ctrl+C to return to normal navigation mode.
This makes `less` a single tool that replaces both `less` and
`tail -f` for interactive log analysis - something most Linux
engineers don't discover until years into their careers.

---

### Mastery Checklist

- [ ] Can view any file (small and large) efficiently
- [ ] Can monitor a log file in real time during an incident
- [ ] Can explain why tail -F is safer than tail -f for rotated logs
- [ ] Can navigate less efficiently (search, jump to end, quit)
- [ ] Can combine tail with grep for filtered live monitoring

---

### Think About This

1. `tail -f` uses Linux's inotify API to get kernel notifications
   when a file changes. This is zero-overhead between writes. But
   over an NFS (network filesystem) mount, inotify doesn't work -
   you have to poll. How does this affect log monitoring strategies
   for applications writing logs to NFS-mounted storage?

2. You're watching `/var/log/nginx/access.log` with `tail -F`
   during a traffic spike. The log is being written so fast that
   your terminal can't keep up. What happens? How do you filter
   to only see what you need?

3. `less` can display binary files (like a compiled Java .class
   file). What does this actually show, and why would an engineer
   ever want to `less` a binary file?

**TYPE G:** A microservices application generates 50GB of logs per
day across 200 service instances. `tail -f` on individual servers
is not a viable strategy. Design a centralized log aggregation
architecture that allows engineers to do what `tail -F | grep
"ERROR"` does locally, but across all 200 services simultaneously.
What are the trade-offs between push (Filebeat/Fluentd) and pull
(scraping) models?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `tail -f` and `tail -F` and when would you use each?
A: `-f` follows the file descriptor (the open file). When log rotation occurs, the original file is renamed (e.g., access.log.1) and a new access.log is created. The `-f` tail continues watching the old renamed file (now empty of new entries). `-F` follows the filename: it keeps retrying to open the specified filename. When the new file is created after rotation, `-F` automatically reconnects to it. In production with log rotation (logrotate): always use `-F`. The `-f` option is only correct when you know the file won't be rotated during your monitoring session.

**Intermediate:**
Q: How would you find the last 50 ERROR lines in a 10GB log file efficiently?
A: Approach: `grep "ERROR" /var/log/app.log | tail -50`. This reads the entire 10GB file but only buffers 50 lines in memory (tail keeps a sliding window). Alternative: if errors are recent, `tail -n 100000 /var/log/app.log | grep "ERROR" | tail -50` (reads only last 100K lines, which is faster for recent errors). For production at scale: query your log aggregation system (Elasticsearch, Loki) with a filter query - this doesn't require reading the raw file at all. Avoid: `tac /var/log/app.log | grep "ERROR" | head -50 | tac` - reads the entire 10GB file twice.

**Expert:**
Q: `tail -f` shows output in real time. Explain the kernel mechanism that makes this work efficiently.
A: When `tail -f` opens a file, it reads to the end and then calls `inotify_add_watch()` (on Linux) to register for `IN_MODIFY` and `IN_MOVE_SELF` events on the file. The kernel adds this fd to an inotify instance. When any process writes to the file, the kernel generates an `IN_MODIFY` event. tail's event loop (using `select()` or `epoll()`) wakes up, reads the new bytes from the current file position, and writes them to stdout. Between writes: tail is blocked in `epoll_wait()`, consuming zero CPU. This is fundamentally different from polling (reading every N milliseconds regardless of changes). The same inotify mechanism is used by Docker for build contexts, IDE file watchers, and log aggregation agents like Filebeat.
