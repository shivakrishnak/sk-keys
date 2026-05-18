---
id: NET-055
title: "TCP TIME_WAIT and Port Exhaustion"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-035
used_by: NET-047, NET-058
related: NET-035, NET-047, NET-058
tags:
  - networking
  - tcp
  - time-wait
  - port-exhaustion
  - performance
  - tuning
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/net/tcp-time-wait-and-port-exhaustion/
---

**⚡ TL;DR** - TIME_WAIT is the state a TCP connection
enters after the active closer sends the final ACK.
It stays for 2 × MSL (Maximum Segment Lifetime), typically
60-120 seconds, to handle delayed packets from the old
connection. On high-throughput services creating thousands
of short-lived connections per second, TIME_WAIT sockets
accumulate and exhaust ephemeral ports (28,231 ports
available by default on Linux). Symptoms: EADDRNOTAVAIL
errors, connection failures, high `ss` TIME-WAIT count.
Fixes: connection reuse (keep-alive, pooling), SO_REUSEADDR,
or tcp_tw_reuse kernel parameter.

| #055 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Connection Lifecycle and States (NET-035) | |
| **Used by:** | Connection Pooling (NET-047), eBPF for Networking (NET-058) | |
| **Related:** | TCP Connection Lifecycle and States, Connection Pooling, eBPF for Networking | |

---

### 🔥 The Problem This Solves

A load test at 5,000 RPS suddenly fails with "Cannot
assign requested address." `ss -s` shows 30,000+ TIME-WAIT
connections. `sysctl net.ipv4.ip_local_port_range` shows
32768-60999 (28,231 ports). 5,000 connections/second,
each in TIME_WAIT for 60 seconds = 5,000 × 60 = 300,000
needed port slots. But only 28,231 available. Port
exhaustion. The fix: stop closing connections so
frequently. That means connection pooling.

---

### 🧠 Intuition: The Time Machine Problem

```
TCP problem: delayed packets

Connection A: client port 54321 → server port 80
Connection A closed. Port 54321 returned to pool.
New connection B: client port 54321 → server port 80

What if a delayed packet from connection A arrives now?
  - Same src/dst port and IP as connection B
  - Could be misdelivered to connection B
  - Silent data corruption

Solution: TIME_WAIT
  Keep port 54321 in TIME_WAIT for 2 × MSL = 60-120s
  Any delayed packets from connection A are silently dropped
  After 2×MSL: no delayed packet from A can possibly arrive
  Port 54321 now safe to reuse

Cost: ~4KB per TIME_WAIT socket (kernel resources)
At 30,000 TIME_WAIT: ~120MB kernel memory
```

---

### ⚙️ Checking TIME_WAIT Status

```bash
# Count TIME_WAIT connections
ss -s
# Output:
# Total: 1234 (kernel 1500)
# TCP:   1100 (estab 50, closed 0, orphaned 0,
#              syn-sent 2, syn-recv 0)
#
# Transport Total     IP        IPv6
# *         1234      -         -
# RAW       0         0         0
# UDP       10        8         2
# TCP       1100      1090      10
# INET      1110      1098      12
# FRAG      0         0         0
#
# Note: "TCP: 1100" is total sockets; use ss -ant to see states

# Detailed count by state:
ss -ant | awk '{print $1}' | sort | uniq -c | sort -rn
# Output:
#   1050 TIME-WAIT
#     45 ESTAB
#      5 LISTEN

# View individual TIME_WAIT connections:
ss -ant state time-wait | head -20

# Check ephemeral port range:
sysctl net.ipv4.ip_local_port_range
# Default: 32768 60999
# Available: 60999 - 32768 = 28231 ports

# How many in use right now:
ss -ant | grep -c TIME-WAIT

# Monitor in real-time:
watch -n1 "ss -ant | awk '{print \$1}' | sort | uniq -c"
```

---

### ⚙️ Why TIME_WAIT Is on the Client Side

```
TIME_WAIT is held by the ACTIVE CLOSER (initiator of FIN).
  Client initiated close → TIME_WAIT on client
  Server initiated close → TIME_WAIT on server

In a typical web request:
  HTTP/1.0: server closes connection after response
    → TIME_WAIT accumulates on SERVER
  HTTP/1.1: client often closes connection
    → TIME_WAIT accumulates on CLIENT (or service calling upstream)
  HTTP/2: long-lived connections, few closures
    → Minimal TIME_WAIT regardless

In microservices:
  Service A calls Service B, B responds, A closes
  → TIME_WAIT accumulates on Service A
  → If A is calling at high rate: port exhaustion on A

In load balancers:
  LB → backend connections: LB is client
  → LB can exhaust ephemeral ports if not using keep-alive
```

---

### ⚙️ Wrong vs Right: Creating New Connections Per Request

```python
# BAD: creating new connection for each request
import http.client

def call_service(path):
    # New connection created and closed per call
    conn = http.client.HTTPConnection("service:8080")
    conn.request("GET", path)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()  # → enters TIME_WAIT on this host
    return data

# At 1,000 RPS: 1,000 new connections per second
# Each in TIME_WAIT for 60 seconds
# 1,000 × 60 = 60,000 simultaneous TIME_WAIT sockets
# Port range: 28,231 → port exhaustion in ~28 seconds

# GOOD: reuse HTTP connections with keep-alive
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
# Configure connection pool
adapter = HTTPAdapter(
    pool_connections=10,   # 10 host pools
    pool_maxsize=20,       # 20 connections per host
)
session.mount("http://", adapter)
session.mount("https://", adapter)

def call_service_v2(path):
    # Reuses existing TCP connection (HTTP keep-alive)
    resp = session.get(f"http://service:8080{path}")
    return resp.json()
    # Connection stays open → no TIME_WAIT on each request
    # 20 connections handle 1,000 RPS
```

---

### ⚙️ Kernel Tuning Options

```bash
# OPTION 1: tcp_tw_reuse (safest, recommended)
# Allow reuse of TIME_WAIT ports for NEW outbound connections
# Only safe for outbound (client-side) connections
sysctl -w net.ipv4.tcp_tw_reuse=1
# Permanent: echo "net.ipv4.tcp_tw_reuse=1" >> /etc/sysctl.conf

# How it works: if a TIME_WAIT port's last packet was >1s ago,
# kernel allows reuse for new connection to different destination
# TCP timestamps must be enabled (they are by default):
sysctl net.ipv4.tcp_timestamps   # should be 1

# OPTION 2: Expand ephemeral port range
sysctl -w "net.ipv4.ip_local_port_range=1024 65535"
# Gives: 65535 - 1024 = 64511 ports (vs default 28231)
# More ports = more TIME_WAIT before exhaustion
# NOT a fix - just delays the problem

# OPTION 3: Reduce TIME_WAIT timeout
sysctl -w net.ipv4.tcp_fin_timeout=30
# Reduces TIME_WAIT from 60s to 30s
# Risk: very old packets (> 30s delayed) could cause issues
# Modern networks: usually safe

# OPTION 4: SO_REUSEADDR (in application code)
# Allow binding to port in TIME_WAIT
# Standard practice for server sockets (not client)

# DO NOT USE: tcp_tw_recycle (REMOVED in Linux 4.12)
# Aggressive recycle - broke NAT environments
# Many cloud instances behind NAT → packet drops
# This option no longer exists in modern kernels

# Verify settings are applied:
sysctl net.ipv4.tcp_tw_reuse
sysctl net.ipv4.ip_local_port_range
sysctl net.ipv4.tcp_fin_timeout
```

---

### ⚙️ Diagnosing Port Exhaustion

```bash
# Symptom: EADDRNOTAVAIL errors in application logs
# "Cannot assign requested address"
# "connect: EADDRNOTAVAIL"

# Step 1: Confirm TIME_WAIT count
ss -ant | grep TIME-WAIT | wc -l
# If > 20,000: likely heading to exhaustion

# Step 2: Check port range vs TIME_WAIT count
sysctl net.ipv4.ip_local_port_range
# Available = max - min
# If TIME_WAIT count > available ports: exhausted

# Step 3: Find which destination is causing most connections
ss -ant state time-wait | \
  awk '{print $5}' | \
  sort | uniq -c | sort -rn | head -10
# Output shows: count  destination_ip:port
# Highest count = service being called too frequently

# Step 4: Check if application has connection reuse
strace -e connect -p $(pgrep -f myapp) 2>&1 | grep -c connect
# High connect() calls per second = no connection reuse

# Step 5: Verify with netstat (old systems without ss)
netstat -ant | grep TIME_WAIT | wc -l

# Step 6: Monitor during load test
watch -n1 "ss -s && sysctl net.ipv4.ip_local_port_range"
```

---

### 📐 Scale Considerations

```
TIME_WAIT math at different scales:

  100 RPS × 60s = 6,000 TIME_WAIT → 28,231 ports: fine
  500 RPS × 60s = 30,000 TIME_WAIT → exhaustion in ~56s
  5,000 RPS × 60s = 300,000 needed → impossible
  
  With tcp_tw_reuse + fin_timeout=30:
  5,000 RPS × 30s = 150,000 "needed" but reuse kicks in
  → Effective: ~64,511 ports (expanded range) + reuse
  → Sustainable

  Best solution: connection pooling
  At 5,000 RPS with 50-connection pool:
  50 long-lived connections, 0 new connections/second
  → 0 new TIME_WAIT sockets
  → Scales to any RPS (within pool capacity)

Kubernetes:
  Each pod has its own network namespace → own port range
  800 pods × 28,231 ports = fine per pod
  But: if a pod is making 1,000 outbound calls/second
  each to different endpoints → same exhaustion issue
  Fix: persistent HTTP connections via Kubernetes service mesh
  or application-level HTTP keep-alive

Cloud providers:
  AWS: NAT Gateway adds TIME_WAIT from NAT perspective
  TCP connection limit: 900K concurrent per NAT Gateway
  Private subnet to internet: use NAT, reuse connections
```

---

### 🧭 Decision Guide

```
When to investigate TIME_WAIT:
  EADDRNOTAVAIL errors under load
  "Cannot assign requested address" in logs
  ss -s shows TIME-WAIT > 20,000
  Response time degradation proportional to traffic

Fix by root cause:
  Root cause: short-lived connections to databases
  Fix: HikariCP or PgBouncer connection pooling

  Root cause: short-lived HTTP to microservices
  Fix: HTTP keep-alive, connection pool in HTTP client

  Root cause: legacy system creating new connections per request
  Fix: wrap client in singleton with connection pool

  Root cause: load test creating new connections
  Fix: configure load test tool to reuse connections
       (ab: default is new per request; -k flag for keep-alive)

Kernel tuning acceptability:
  tcp_tw_reuse=1: SAFE - enable in production for outbound-heavy
  Expanded port range: SAFE - no side effects
  tcp_fin_timeout=30: SAFE on modern networks
  tcp_tw_recycle: REMOVED - do not attempt

Quick fix during incident:
  sysctl -w net.ipv4.tcp_tw_reuse=1
  sysctl -w "net.ipv4.ip_local_port_range=1024 65535"
  sysctl -w net.ipv4.tcp_fin_timeout=30
  Then fix root cause (connection pooling) properly
```