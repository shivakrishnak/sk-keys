---
id: OSY-044
title: "lsof and netstat (File Descriptors and Sockets)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-034, OSY-021
used_by: OSY-079
related: OSY-034, OSY-043, OSY-079
tags:
  - lsof
  - netstat
  - ss
  - tool
  - file-descriptors
  - sockets
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/osy/lsof-netstat/
---

## TL;DR

`lsof` lists all open files (sockets, files, pipes,
devices) for a process. `ss` (or `netstat`) shows all
network connections and their states. Together they
diagnose FD leaks, connection leaks, port conflicts,
and TIME_WAIT accumulation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-044 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | lsof, netstat, ss, file descriptors, sockets |
| **Prerequisites** | OSY-034, OSY-021 |

---

### lsof Essentials

```bash
# List all open files for a Java process
lsof -p $(pgrep java)
# Column meaning:
# COMMAND  PID    USER  FD  TYPE  DEVICE  SIZE  NODE  NAME
# java    1234  nobody   4r  REG   8,1    1024    56  /app/app.jar
# java    1234  nobody  10u  IPv6   0t0    TCP  0.0.0.0:8080 (LISTEN)
# java    1234  nobody  11u  IPv6   0t0    TCP  10.0.0.1:50234->db:5432 (ESTABLISHED)

# FD column values:
# cwd: current working directory
# txt: program text (executable)
# mem: memory-mapped file
# 0u: stdin (u=read/write, r=read-only, w=write-only)
# 1w: stdout (write)
# 2w: stderr
# 3r: fd 3, open for reading
# 10u: fd 10, read/write (typical for sockets)

# TYPE values:
# REG:  regular file
# DIR:  directory
# PIPE: pipe (anonymous or named)
# IPv4: IPv4 socket
# IPv6: IPv6 socket (includes IPv4-mapped)
# unix: Unix domain socket
```

```bash
# Key diagnostic commands:

# Count total FDs (check for leaks)
lsof -p PID | wc -l
# Watch over time: growing count = FD leak

# Find what's listening on a port
lsof -i :8080
# Shows: which process owns port 8080 (PID, process name)
# Useful: "port already in use" error diagnosis

# Find all sockets of a process
lsof -p PID -i
# Shows all TCP/UDP connections

# Find files opened by a specific user
lsof -u nginx

# Find all processes with a specific file open
lsof /var/log/app.log
# Useful: "file in use" errors, log rotation issues

# Find network connections to a specific host
lsof -i @192.168.1.100
# Shows: which local processes are connected to that host
```

---

### ss / netstat Essentials

```bash
# ss is the modern replacement for netstat (faster, from iproute2)
# netstat is deprecated but still commonly found

# All TCP connections
ss -tnp
# -t: TCP, -n: numeric (no hostname lookup), -p: show process

# Output:
# Netid  State   Recv-Q Send-Q  Local Address:Port  Peer Address:Port
# tcp    ESTAB   0      0       10.0.0.1:50234      10.0.0.2:5432   users:("java",pid=1234,fd=10)
# tcp    LISTEN  0      128     0.0.0.0:8080        0.0.0.0:*       users:("java",pid=1234,fd=7)

# Connection state summary (key for diagnosis)
ss -tn | awk '{print $1}' | sort | uniq -c | sort -rn
# Or:
ss -s
# Shows count by state: TIME_WAIT, ESTABLISHED, CLOSE_WAIT, etc.

# Show only specific states
ss -tn state time-wait  # only TIME_WAIT connections
ss -tn state close-wait # only CLOSE_WAIT connections
ss -tn state established # only established

# netstat equivalents (deprecated but common in older docs):
netstat -tnp    # equivalent to ss -tnp
netstat -s      # statistics
netstat -tlnp   # listening sockets
```

---

### TCP States and What They Mean

```
TCP Connection State Diagnosis:

LISTEN: server waiting for connections (normal)
ESTABLISHED: active connection (normal)
TIME_WAIT: connection closing, waiting 2*MSL (60-120s)
  LARGE COUNT (>1000): many short-lived connections
  Fix: TCP keepalive, connection reuse, SO_REUSEADDR
CLOSE_WAIT: remote closed, local not called close()
  LARGE COUNT: socket FD leak - local code not calling close()
  Fix: audit code for unclosed sockets, use try-with-resources
SYN_SENT: outbound connection in progress
SYN_RECV: inbound connection 3-way handshake in progress
FIN_WAIT_1/2: local side initiated close
LAST_ACK: remote sent FIN, waiting for final ACK

Java common scenarios:
  Many TIME_WAIT: short-lived HTTP connections (use connection pool!)
    HttpClient connection pool or HTTP/2 (multiplexed)
  Many CLOSE_WAIT: bug in connection handling code
    -> socket.close() not called in error paths
    -> try-with-resources fixes this

# Check for CLOSE_WAIT (potential FD leak):
ss -tn state close-wait
# If many: find which process and fix socket close in code
```

---

### FD Leak Detection Pattern

```bash
# Systematic FD leak detection:

# Step 1: Get baseline FD count
lsof -p PID | wc -l

# Step 2: Wait 5 minutes under normal load
sleep 300

# Step 3: Check again
lsof -p PID | wc -l
# If growing significantly (>10% per hour): FD leak likely

# Step 4: Find what type of FDs are growing
lsof -p PID | awk '{print $5}' | sort | uniq -c | sort -rn
# REG: regular files - file descriptor leak
# IPv4/IPv6: socket leak
# PIPE: pipe leak (ProcessBuilder without proper close)

# Step 5: Find specific files growing
lsof -p PID | grep REG | awk '{print $NF}' | sort | uniq -c | sort -rn
# Shows which files have the most FDs open
# Repeated log file + large count = not closing FileInputStream

# Java leak patterns:
# FileInputStream not closed -> REG FDs grow
# HttpURLConnection not disconnected -> IPv4 FDs grow
# ResultSet/Statement/Connection not closed -> socket FDs grow
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "TIME_WAIT is a bug" | TIME_WAIT is correct TCP behavior, preventing duplicate packets from old connections being mistaken for new ones. Many TIME_WAIT connections indicate many short-lived connections. The fix is connection pooling, not suppressing TIME_WAIT |
| "lsof output shows only open files" | In Unix "everything is a file" - lsof shows regular files, but also: sockets (TCP, UDP, Unix), pipes, devices, mmap'd files, deleted files still held open. Deleted files with FDs still open still consume disk space |

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lsof -p PID` | All FDs for a process |
| `lsof -p PID \| wc -l` | Count FDs (leak detection) |
| `lsof -i :PORT` | What process owns a port |
| `ss -tnp` | All TCP connections with process info |
| `ss -s` | TCP state summary counts |
| `ss -tn state close-wait` | Find socket close() bugs |
| `ss -tn state time-wait` | Find connection pool needs |
