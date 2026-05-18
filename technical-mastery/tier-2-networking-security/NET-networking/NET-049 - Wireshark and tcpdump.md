---
id: NET-049
title: "Wireshark and tcpdump"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-019, NET-033
used_by: NET-055, NET-060
related: NET-019, NET-033, NET-050
tags:
  - networking
  - wireshark
  - tcpdump
  - packet-capture
  - debugging
  - diagnosis
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/net/wireshark-and-tcpdump/
---

**⚡ TL;DR** - tcpdump captures network packets at the
kernel level; Wireshark analyzes them with protocol
dissection and filtering. Together they answer questions
that no application log can: "Is the packet actually
being sent? Is it reaching the destination? What does
the exact TCP flag sequence look like? Is TLS negotiating
correctly?" The 15 tcpdump filters in this entry cover
90% of production debugging scenarios. You don't need to
memorize Wireshark - you need to know when to reach for
it and what questions it can answer.

| #049 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Your First Network Lab (NET-019), Build a TCP Client-Server (NET-033) | |
| **Used by:** | Networking System Design Interview Patterns, Network Debugging Systematic | |
| **Related:** | Your First Network Lab, Build a TCP Client-Server, Network Performance Testing | |

---

### 🔥 The Problem This Solves

An application says "connection refused" but the service
is definitely running and `ss -lntp` shows it listening.
Application logs show a timeout, but nothing in the server
logs. A firewall is silently dropping packets - but which
one, and where? tcpdump can show you the SYN was sent and
never received a response. Wireshark can show you the
RST came from a middlebox. No application-level tool can
answer this - only packet capture can.

---

### 🧠 Intuition: Capture Anywhere in the Stack

```
tcpdump captures at:
  - Network interface (eth0, lo, wlan0)
  - Before or after iptables rules (direction matters)
  - Physical or virtual interfaces (docker0, veth*, tun0)

What you can see:
  Packets that WERE sent (client side)
  Packets that WERE received (server side)
  By comparing both: where in the path are packets lost?

What you cannot see:
  Encrypted payloads (TLS - you see record sizes, not content)
  Application logic (you see bytes, not semantics)
  UDP packet ordering (datagrams are unordered)
```

---

### ⚙️ tcpdump: Essential Filters and Commands

```bash
# CAPTURE SYNTAX:
# tcpdump [options] [filter expression]
# Filter = Berkeley Packet Filter (BPF) syntax

# 1. Basic: capture all traffic on eth0
sudo tcpdump -i eth0

# 2. Capture specific host
sudo tcpdump -i eth0 host 10.0.0.5

# 3. Capture specific port
sudo tcpdump -i eth0 port 443

# 4. Capture host AND port
sudo tcpdump -i eth0 "host 10.0.0.5 and port 8080"

# 5. Capture without hostname resolution (faster, clearer)
sudo tcpdump -i eth0 -n port 80

# 6. Capture with timestamps and verbose output
sudo tcpdump -i eth0 -n -tt -v "port 9000 and tcp"
# -tt: microsecond timestamps (Unix epoch)
# -v: verbose (show TTL, flags, window size)
# -vv: even more detail

# 7. Save to file for Wireshark analysis
sudo tcpdump -i eth0 -n -w /tmp/capture.pcap "port 443"
# Open in Wireshark later: wireshark /tmp/capture.pcap

# 8. Read from file
tcpdump -r /tmp/capture.pcap "host 10.0.0.5"

# 9. Limit capture count
sudo tcpdump -i eth0 -c 100 "port 80"
# -c 100: stop after 100 packets

# 10. Show hex dump (useful for protocol debugging)
sudo tcpdump -i eth0 -n -X "port 8080 and tcp"
# -X: hex + ASCII

# 11. All interfaces (any)
sudo tcpdump -i any -n "port 8080"
```

---

### ⚙️ TCP Flag Filters

```bash
# Capture only SYN packets (connection attempts)
sudo tcpdump -i eth0 "tcp[13] == 2"
# Byte 13 = flags byte: SYN=0x02, SYN-ACK=0x12

# Capture SYN and SYN-ACK (handshakes)
sudo tcpdump -i eth0 "tcp[13] & 0x12 != 0"

# Capture RST packets (unexpected resets)
sudo tcpdump -i eth0 "tcp[13] & 0x04 != 0"

# Capture FIN packets (graceful closes)
sudo tcpdump -i eth0 "tcp[13] & 0x01 != 0"

# More readable alternatives (requires -n):
sudo tcpdump -i eth0 -n "tcp[tcpflags] & tcp-syn != 0"
sudo tcpdump -i eth0 -n "tcp[tcpflags] & tcp-rst != 0"
sudo tcpdump -i eth0 -n "tcp[tcpflags] & tcp-fin != 0"
```

---

### ⚙️ 15 Production Debugging Scenarios

```bash
# SCENARIO 1: Is service reachable? (SYN gets response?)
sudo tcpdump -i eth0 -n "port 8080 and tcp[tcpflags] & (tcp-syn|tcp-rst) != 0"
# SYN followed by SYN-ACK = service reachable
# SYN followed by RST = service not listening (port rejected)
# SYN with no response = firewall DROP

# SCENARIO 2: What is the actual DNS response?
sudo tcpdump -i eth0 -n "udp port 53"
# Capture DNS queries and responses in plaintext

# SCENARIO 3: Is the HTTP request being sent with right headers?
sudo tcpdump -i eth0 -n -A "port 80 and tcp[20:4] == 0x47455420"
# 0x47455420 = "GET " in hex - filters for GET requests
# -A: ASCII output to see headers
# Note: only works for unencrypted HTTP

# SCENARIO 4: Capture all traffic for one pod (Kubernetes)
# Find veth interface for pod:
POD_IP=$(kubectl get pod my-pod -o jsonpath='{.status.podIP}')
sudo tcpdump -i any -n "host $POD_IP"

# SCENARIO 5: Verify TLS handshake is occurring
sudo tcpdump -i eth0 -n -v "port 443 and tcp[20] == 22"
# Byte 20 = TLS content type, 22 = Handshake
# See SNI and cipher negotiation (in verbose mode)

# SCENARIO 6: Measure retransmit frequency
sudo tcpdump -i eth0 -n "port 8080 and (tcp[tcpflags] & tcp-rst != 0)"
# Count RSTs per minute during load test

# SCENARIO 7: Diagnose high latency - is it network or app?
sudo tcpdump -i eth0 -n -tt "host 10.0.0.5 and port 8080"
# Compare timestamps: SYN → SYN-ACK gap = network latency
# Compare: request sent → response received = total latency
# Subtract: remaining = application latency

# SCENARIO 8: Capture specific connection only
sudo tcpdump -i eth0 -n \
  "src 192.168.1.10 and dst 10.0.0.5 and port 8080"

# SCENARIO 9: ICMP (ping) traffic
sudo tcpdump -i eth0 -n icmp

# SCENARIO 10: UDP traffic (DNS, game servers, video)
sudo tcpdump -i eth0 -n udp

# SCENARIO 11: ARP traffic (IP-to-MAC resolution)
sudo tcpdump -i eth0 -n arp

# SCENARIO 12: Traffic entering firewall (INPUT chain debug)
# Capture on BOTH interfaces to find where packets are dropped
sudo tcpdump -i eth0 -n -w /tmp/before_fw.pcap "port 8080" &
# Check iptables -nvL (look for packets counter increasing)

# SCENARIO 13: Capture in a Docker container
docker exec my_container tcpdump -i any -n "port 8080"
# Or: install tcpdump in container and exec

# SCENARIO 14: Capture and immediately stream to Wireshark
# (from remote server to local Wireshark via SSH)
ssh user@server "sudo tcpdump -i eth0 -n -w - 'port 8080'" \
  | wireshark -k -i -

# SCENARIO 15: Time-bounded capture (10 seconds)
sudo timeout 10 tcpdump -i eth0 -n -w /tmp/sample.pcap "port 8080"
```

---

### ⚙️ Wireshark: Key Features and Filters

```
Wireshark use cases:
  - Analyze pcap files captured by tcpdump
  - Visualize TCP stream reconstruction (Follow TCP Stream)
  - Find retransmits and out-of-order packets automatically
  - Decrypt TLS (if you have session keys)
  - Expert info: automatic anomaly detection

Wireshark display filter syntax (different from tcpdump BPF!):
  ip.addr == 10.0.0.5          ← specific IP
  tcp.port == 8080             ← specific port
  http.request.method == "GET" ← HTTP method
  tcp.flags.syn == 1           ← SYN flag set
  tcp.flags.reset == 1         ← RST flag set
  tcp.analysis.retransmission  ← retransmitted packets
  tcp.analysis.zero_window     ← zero window stalls
  tls.handshake.type == 1      ← ClientHello
  dns.qry.name contains "api"  ← DNS queries with "api"
  http.response.code == 500    ← HTTP 5xx errors
```

---

### ⚙️ TLS Session Key Decryption in Wireshark

```bash
# Decrypt TLS traffic with session keys (not private key!)
# Requires: application to log TLS session keys via SSLKEYLOGFILE

# For Chrome/Firefox:
export SSLKEYLOGFILE=/tmp/tls-keys.log
chromium --ssl-key-log-file=/tmp/tls-keys.log &

# For Python requests:
# Not natively supported, use mitmproxy or wireshark's 
# "Follow TLS Stream" after loading keylog file

# For Go or Java:
# Set environment variable before running the application
export SSLKEYLOGFILE=/tmp/keys.log

# In Wireshark:
# Edit → Preferences → Protocols → TLS
# Set "(Pre)-Master-Secret log filename" to /tmp/tls-keys.log
# Open the pcap file - TLS payloads now decrypted

# What you can see after decryption:
# HTTP/2 frames, gRPC requests, JSON payloads, headers
# This is invaluable for debugging encrypted service mesh traffic
```

---

### ⚙️ Wrong vs Right: Capturing on the Wrong Interface

```bash
# BAD: capturing on eth0 when traffic is on lo (loopback)
sudo tcpdump -i eth0 "port 9000"
# No packets shown - but service IS running on localhost
# Service communicates on 127.0.0.1 which uses lo interface

# WHY: different services use different interfaces:
#   localhost/127.0.0.1 → lo
#   LAN traffic → eth0 (or enp0s3, ens3, etc.)
#   Docker containers → docker0 + veth pairs
#   WireGuard VPN → wg0
#   All interfaces → any (but may see duplicate packets)

# GOOD: capture on correct interface or use "any"
sudo tcpdump -i lo -n "port 9000"     # loopback
sudo tcpdump -i any -n "port 9000"    # all interfaces
sudo tcpdump -i docker0 "port 9000"   # Docker bridge

# Find which interface your service uses:
ss -lntp | grep 9000
# LISTEN 0  128  0.0.0.0:9000  → all interfaces → use eth0 or any
# LISTEN 0  128  127.0.0.1:9000 → only loopback → use lo
```

---

### ⚙️ Reading tcpdump Output

```
Example output line:
21:47:52.123456 IP 10.0.0.2.54321 > 10.0.0.5.8080:
  Flags [S], seq 1234567890, win 64240,
  options [mss 1460,sackOK,TS val 100 ecr 0,nop,wscale 7],
  length 0

Breakdown:
  21:47:52.123456    timestamp (hh:mm:ss.microseconds)
  IP                 IPv4 packet
  10.0.0.2.54321    source IP and port
  10.0.0.5.8080     destination IP and port
  Flags [S]          TCP flags: S=SYN, .=ACK, P=PSH, F=FIN, R=RST
  seq 1234567890     sequence number
  win 64240          window size advertised
  mss 1460           maximum segment size option
  sackOK             selective ACK supported
  TS val/ecr         TCP timestamps option
  wscale 7           window scale factor = 2^7 = 128
  length 0           payload bytes in this packet

Common flag combinations:
  [S]    = SYN (connection request)
  [S.]   = SYN-ACK (connection accepted)
  [.]    = ACK (pure acknowledgment)
  [P.]   = PSH+ACK (data with push flag - tells receiver to deliver now)
  [F.]   = FIN+ACK (graceful close)
  [R.]   = RST+ACK (reset - unexpected)
  [R]    = RST (connection rejected or aborted)
```

---

### 📐 Scale Considerations

```
Packet capture at high traffic:
  1 Gbps interface: 83M packets/minute (1460-byte packets)
  tcpdump with filter: handles ~100K packets/second before drop
  Without filter: tcpdump drops packets ("N packets dropped")

Production capture best practices:
  1. Always use specific filters (not "capture everything")
  2. Write to file (-w), not stdout (less CPU)
  3. Set time limit (timeout 30 tcpdump ...) or packet count (-c 1000)
  4. Use brief mode until you need detail: no -v, no -A
  5. For high-speed: use AF_PACKET v3 or XDP for kernel bypass

Cloud packet capture:
  AWS: VPC Traffic Mirroring → mirror traffic to capture instance
  GCP: Packet Mirroring → similar concept
  Used for: security monitoring, debugging without agent on host

Container/Kubernetes packet capture:
  kubectl sniff: Wireshark plugin for Kubernetes pods
  ksniff: deploys tcpdump in pod, streams to local Wireshark
  Use for: debugging service mesh issues, admission webhook traffic
```

---

### 🧭 Decision Guide

```
When should I reach for tcpdump/Wireshark?
  YES when:
  - "Connection refused" but service is running
  - "Connection timeout" - is the packet even leaving?
  - TLS errors - is the handshake completing?
  - DNS issues - is the query going out? What's the response?
  - Suspected firewall dropping packets (SYN with no reply)
  - Load balancer not forwarding traffic
  - Network performance issues (latency, retransmits)
  - Intermittent failures that don't show up in app logs

  NOT needed when:
  - Application errors in logs are clear
  - Database error messages are explicit
  - HTTP 4xx/5xx with clear error body

Which tool?
  tcpdump: production servers (CLI, lightweight, scriptable)
  Wireshark: detailed analysis (GUI, protocol dissection, filtering)
  mtr: path analysis (replaces traceroute + ping combination)

Key capture patterns:
  # Quick connectivity check:
  sudo tcpdump -i any -n -c 10 "port TARGET_PORT"
  # Connection lifecycle:
  sudo tcpdump -i eth0 -n "host TARGET_IP and port TARGET_PORT"
  # Save for deep analysis:
  sudo tcpdump -i eth0 -n -w /tmp/issue.pcap "host TARGET_IP"
```