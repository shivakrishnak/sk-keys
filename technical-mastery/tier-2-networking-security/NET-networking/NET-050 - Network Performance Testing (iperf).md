---
id: NET-050
title: "Network Performance Testing (iperf)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-043, NET-048
used_by: NET-060
related: NET-048, NET-049, NET-060
tags:
  - networking
  - iperf
  - performance-testing
  - bandwidth
  - latency
  - network-testing
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/net/network-performance-testing/
---

**⚡ TL;DR** - iperf3 measures network bandwidth, latency,
jitter, and packet loss between two hosts. It is the
standard tool for proving "the network is the bottleneck"
or clearing the network from suspicion. Used before
deploying services to validate infrastructure, and after
incidents to verify network recovery. A 10 Gbps link
passing 1 Gbps in iperf3 is the bottleneck in your
architecture. A 10 Gbps link reaching 9.8 Gbps is healthy.

| #050 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DNS Resolution Deep Dive (NET-043), Network Latency Sources (NET-048) | |
| **Used by:** | Network Debugging Systematic | |
| **Related:** | Network Latency Sources and Measurement, Wireshark and tcpdump, Network Debugging Systematic | |

---

### 🔥 The Problem This Solves

Your microservice has 500ms P99 latency between
availability zones. Is it the network or the application?
Without measurement, you guess. iperf3 test:
`iperf3 -c 10.0.0.5 -t 10 -P 10` returns 2 Gbps with
0 retransmits. The 10 Gbps link between AZs is fine.
The bottleneck is the application. This test takes
2 minutes and saves hours of application profiling on
the wrong layer.

---

### 🧠 Intuition: Dedicated Measurement vs Production Traffic

```
Production traffic: mixed requests, variable sizes,
  application overhead, connection pooling effects

iperf3: pure measurement - generates maximum possible
  throughput or stress-tests latency
  
It answers: "What is the maximum this network path can do?"
  Not: "Why is my application slow?"
  But: "Is the network constraining my application?"
```

---

### ⚙️ iperf3 Basics

```bash
# SERVER: must be running before client
iperf3 -s                      # listen on port 5201
iperf3 -s -p 9090              # custom port
iperf3 -s -D                   # daemon mode
iperf3 -s --logfile /tmp/iperf.log  # log to file

# CLIENT: basic TCP throughput test
iperf3 -c server_ip            # 10-second test to server
iperf3 -c server_ip -t 30      # 30-second test
iperf3 -c server_ip -p 9090    # custom port

# Example output (TCP):
# Connecting to host server_ip, port 5201
# [  5] local 10.0.0.1 port 54321 connected to 10.0.0.2 port 5201
# [ ID] Interval       Transfer     Bitrate         Retr
# [  5]  0.00-1.00 sec  1.10 GBytes  9.43 Gbits/sec  0
# [  5]  1.00-2.00 sec  1.10 GBytes  9.40 Gbits/sec  0
# ...
# [  5]  0.00-10.00 sec  11.0 GBytes  9.41 Gbits/sec  0  sender
# [  5]  0.00-10.00 sec  11.0 GBytes  9.41 Gbits/sec     receiver
#
# Retr = 0: no retransmits = no packet loss
# 9.41 Gbits/sec on 10G link = 94% efficiency = healthy
```

---

### ⚙️ Common Test Scenarios

**TCP throughput (simulating bulk transfer):**

```bash
# Single stream (simple baseline)
iperf3 -c server_ip -t 30

# Parallel streams (better utilization, simulates concurrent conns)
iperf3 -c server_ip -t 30 -P 8
# -P 8: 8 parallel streams (useful for links with high RTT)
# On a 100ms RTT link: single stream is limited by TCP cwnd
# 8 parallel streams = 8 independent cwnd ramp-ups
# Combined throughput: 8x higher than single stream

# Reverse mode (server sends to client - different direction)
iperf3 -c server_ip -R
# Tests asymmetric links or provider routing differences

# Bidirectional (simultaneous both directions)
iperf3 -c server_ip --bidir
```

**UDP testing (latency and packet loss):**

```bash
# UDP test: bandwidth + jitter + packet loss
iperf3 -c server_ip -u -b 1G
# -u: UDP mode
# -b 1G: target bitrate (UDP doesn't auto-throttle like TCP)

# Output:
# [ ID] Interval       Transfer     Bitrate         Jitter    Lost/Total
# [  5]  0.00-10.00 sec  1.15 GBytes   988 Mbits/sec  0.120 ms  0/838695 (0%)
#
# Jitter: variation in packet arrival time (ms)
# Lost/Total: packet loss rate
# < 1ms jitter + 0% loss = healthy for most services
# > 5ms jitter: problematic for VoIP/video

# Test packet loss at specific rates:
iperf3 -c server_ip -u -b 100M  # 100 Mbps UDP
iperf3 -c server_ip -u -b 500M  # 500 Mbps UDP
# Increase until you see packet loss - that's the saturation point
```

---

### ⚙️ Advanced Tests for Production Scenarios

```bash
# Test with realistic MTU size (match production packets)
iperf3 -c server_ip -l 1400     # 1400 byte segments (near MTU)

# Test connection setup overhead (many short connections)
iperf3 -c server_ip -n 1 -k 1000
# -n 1: send only 1 byte, then close
# -k 1000: repeat 1000 times
# Measures: connection setup overhead, TIME_WAIT accumulation

# Zero-copy mode (test kernel efficiency)
iperf3 -c server_ip --zerocopy

# JSON output for scripting/monitoring:
iperf3 -c server_ip -J | python3 -c "
import json, sys
data = json.load(sys.stdin)
mbps = data['end']['sum_received']['bits_per_second'] / 1e6
rtx = data['end']['sum_sent']['retransmits']
print(f'{mbps:.1f} Mbps, {rtx} retransmits')
"

# Set socket buffer sizes (test with explicit parameters):
iperf3 -c server_ip -w 4M
# -w 4M: 4MB TCP window/socket buffer
# Use when testing cross-region with large BDP
# BDP = 1 Gbps × 100ms RTT = 12.5 MB needed window
# Default: 212KB might be too small for high-BDP paths
```

---

### ⚙️ Wrong vs Right: Using iperf3 Without Matching Production Parameters

```bash
# BAD: test with single stream on high-latency link
iperf3 -c us-east-server -t 10
# NYC → London (75ms RTT), 1 Gbps link
# Single TCP stream throughput:
# cwnd at convergence ≈ 1MB (typical)
# Throughput = cwnd / RTT = 1MB / 0.075s = 106 Mbps
# Test reports: 100 Mbps
# You think: "the 1 Gbps link is only 10% utilized"
# Reality: single TCP stream throughput is RTT-limited
#          The link is fine - use more parallel streams

# GOOD: use parallel streams to stress the link properly
iperf3 -c us-east-server -t 30 -P 16
# 16 parallel streams each ramp independently
# Combined: approaches actual link capacity
# Each stream at ~100 Mbps × 16 = ~1.6 Gbps (close to 1G link limit)

# Also GOOD: configure TCP window to match BDP
iperf3 -c us-east-server -t 30 -w 4M
# BDP = 1 Gbps × 75ms = 9.375 MB
# 4MB window gets to ~400 Mbps per stream
# Much better than default 212KB window (100 Mbps per stream)
```

---

### ⚙️ Interpreting Results

```
Throughput interpretation:
  > 90% of link capacity: network is healthy
  60-90%: moderate overhead (CPU, protocol)
  < 60%: potential bottleneck (loss, window, CPU)

Retransmit interpretation:
  0 retransmits: no packet loss under test conditions
  > 0 at < 50% load: real packet loss problem
  Retransmits only at 90%+ load: normal congestion

Jitter interpretation (UDP):
  < 1ms: excellent (real-time apps fine)
  1-5ms: acceptable for most UDP apps
  5-50ms: problematic for VoIP, video conferencing
  > 50ms: serious jitter, investigate bufferbloat or QoS

Speed vs capacity gap analysis:
  Expected: 10 Gbps link
  Measured: 2 Gbps with 1 stream (RTT-limited)
  Measured: 9.4 Gbps with 8 streams (network limited correctly)
  → Single stream limitation: normal on high-RTT links
  → Application uses 1 stream: real bottleneck is cwnd/RTT
  → Solution: connection pooling, HTTP/2 multiplexing
```

---

### ⚙️ iperf3 Network Validation Checklist

```bash
# Pre-deployment network validation:

# Step 1: Basic connectivity
ping -c 10 target_host
# Expected: 0% loss, consistent RTT

# Step 2: Port reachability
nc -zv target_host 5201
# Expected: Connected successfully

# Step 3: TCP throughput (8 streams, 60 seconds)
iperf3 -c target_host -t 60 -P 8
# Expected: > 90% of expected link speed, Retr = 0

# Step 4: UDP jitter test (at expected service rate)
iperf3 -c target_host -u -b 100M -t 30
# Expected: < 1ms jitter, < 0.1% packet loss

# Step 5: Reverse direction (server → client)
iperf3 -c target_host -R -t 30 -P 8
# Expected: same throughput as forward direction

# Step 6: Long-running stability test
iperf3 -c target_host -t 300 -P 4
# 5-minute test to detect intermittent packet loss
# Expected: consistent throughput, zero retransmits

# FAIL criteria (investigate before deploying):
# TCP: Retr > 0 at < 80% utilization
# UDP: loss > 0.1% or jitter > 5ms
# Throughput: < 70% of expected link speed
# Asymmetry: forward vs reverse throughput > 20% difference
```

---

### ⚙️ Failure Example: Jumbo Frame Mismatch

**Symptoms:** iperf3 shows 200 Mbps on a 10 Gbps link.
Retransmits: 0. But small packets (ping) have 0ms latency.

**Root cause:**

```bash
# Hypothesis: MTU mismatch causing fragmentation/drops

# Test with specific packet sizes:
iperf3 -c target_host -l 1400    # works fine
iperf3 -c target_host -l 8000    # drops to 200 Mbps
iperf3 -c target_host -l 9000    # complete failure

# Jumbo frames configured on hosts (MTU 9000):
ip link show eth0 | grep mtu
# mtu 9000

# But switch between hosts has MTU 1500:
# Packets > 1500 bytes silently dropped by switch
# (ICMP "packet too big" might be filtered by firewall)
# TCP path MTU discovery doesn't work if ICMP blocked!

# Diagnose path MTU:
tracepath target_host   # shows MTU at each hop
# or:
ping -M do -s 8972 target_host   # DF bit set, 9000-28=8972
# "Frag needed" response shows actual MTU

# Fix: set consistent MTU across all hops
ip link set eth0 mtu 1500    # back to standard
# Or fix the switch configuration

# Another fix: disable jumbo frames on interface
# and update all application configs that assume jumbo frames
```

---

### 📐 Scale Considerations

```
Testing a 10-server cluster:
  Matrix test: all N×N pairs
  N=10 → 90 pairs (avoid all simultaneous = saturates switch)
  Run sequentially or in controlled parallel

  Script:
  SERVERS=(10.0.0.1 10.0.0.2 ... 10.0.0.10)
  for src in "${SERVERS[@]}"; do
    for dst in "${SERVERS[@]}"; do
      [[ "$src" == "$dst" ]] && continue
      ssh $src "iperf3 -c $dst -t 10 -J" | jq '.end.sum_received.bits_per_second'
    done
  done

Cloud network testing:
  AWS: Enhanced Networking (ENA) required for > 25 Gbps
  Test within AZ: typically > 25 Gbps between instances
  Test cross-AZ: typically 5-10 Gbps (more overhead)
  Test cross-region: typically 100-500 Mbps (internet path)

100 Gbps links (high-performance computing):
  iperf3 single instance: ~40-60 Gbps (CPU bound)
  Use ntttcp (Windows) or nuttcp for higher throughput
  Or: multiple iperf3 instances running in parallel
      bind to different CPU cores with taskset
```

---

### 🧭 Decision Guide

```
When to use iperf3:
  Before deploying services to new network paths
  After network changes (new switch, routing update, VPC peering)
  When application latency is unexpectedly high
  To validate SLA with cloud provider or ISP

What iperf3 cannot tell you:
  Why your application is slow (it bypasses app layer)
  Real-world latency with authentication and TLS (use curl)
  Database query performance (use EXPLAIN ANALYZE)
  Whether caching is working (use application metrics)

Network health quick test (2 minutes):
  1. ping -c 20 target     ← RTT and loss baseline
  2. iperf3 -c target -P 4 ← TCP throughput
  3. iperf3 -c target -u -b 100M -t 10  ← UDP jitter/loss

If iperf3 shows healthy network and app is still slow:
  → The bottleneck is in the application, not the network
  → Profile with: Application Performance Monitoring (APM),
    distributed tracing (Jaeger, Zipkin), or database slow query log
```