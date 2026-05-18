---
id: NET-048
title: "Network Latency Sources and Measurement"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-020, NET-030, NET-038, NET-041
used_by: NET-050, NET-055
related: NET-030, NET-047, NET-050
tags:
  - networking
  - latency
  - performance
  - measurement
  - curl
  - p99
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/net/network-latency-sources/
---

**⚡ TL;DR** - Network latency has 5 distinct sources:
propagation (speed of light, irreducible), transmission
(packet size / bandwidth), processing (router and server
CPU), queuing (buffer when congested), and protocol
overhead (handshakes, serialization). Understanding which
source dominates explains why optimizations work or fail.
`curl -w` breaks down latency by phase. A 200ms response
where DNS takes 150ms is a DNS problem, not an application
problem - without measurement, you'd guess wrong.

| #048 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TCP (NET-020), HTTP and HTTPS Basics (NET-030), HTTP/2 Multiplexing (NET-038), gRPC (NET-041) | |
| **Used by:** | Network Performance Testing, Networking System Design Interview Patterns | |
| **Related:** | HTTP and HTTPS Basics, Connection Pooling, Network Performance Testing | |

---

### 🔥 The Problem This Solves

Your API endpoint responds in 300ms. The SLA is 200ms.
Where is the 100ms going? Without measurement, you
guess at the database. After adding `curl -w` timing
output, you discover: DNS lookup takes 120ms (stale TTL,
resolver is far away). Fix: pin DNS to local resolver,
lower TTL. Response time: 30ms. The measurement made a
5-minute fix obvious that would otherwise be a week of
optimization in the wrong layer.

---

### 🧠 The 5 Sources of Latency

```
1. PROPAGATION DELAY (irreducible)
   = distance / (speed of light × 2/3)
   Speed of light in fiber: ~200,000 km/s
   
   NYC → London (5,500 km): 5,500 / 200,000 = 27.5ms one-way
   RTT: ~55ms  (matches observed ~70ms with routing overhead)
   
   You CANNOT beat the speed of light.
   CDNs win by reducing distance (edge nodes near users).

2. TRANSMISSION DELAY (payload-size dependent)
   = packet_size / bandwidth
   1 MB / 1 Gbps = 8,000,000 bits / 1,000,000,000 bits/s = 8ms
   
   Negligible on high-speed links for small packets.
   Dominates for large payloads on slow links.

3. PROCESSING DELAY (CPU, NIC, kernel)
   = time to process packet in router/host
   Typical: 0.1-1ms per hop
   
   Sources: NIC interrupt, kernel networking stack, 
            socket buffer copies, TLS encryption

4. QUEUING DELAY (congestion, buffer bloat)
   = time waiting in router/NIC queue
   Can spike from 0ms to 100ms+ under load
   Highly variable - dominates tail latency
   
   Bufferbloat: oversized buffers that add latency
   (100ms delay at a slow link with a large buffer)

5. PROTOCOL OVERHEAD (handshakes, serialization)
   TCP SYN: 1 RTT
   TLS 1.3: +1 RTT
   HTTP/2 SETTINGS: negligible (encrypted in TLS)
   gRPC protobuf encode/decode: < 1ms for typical payload
   
   JSON parse 1MB: ~10ms on server CPU
   Protobuf decode 1MB: ~1ms on server CPU
```

---

### ⚙️ Measuring HTTP Latency with curl

```bash
# The definitive latency breakdown tool:
curl -o /dev/null -s -w "
namelookup:   %{time_namelookup}s
connect:      %{time_connect}s
appconnect:   %{time_appconnect}s
pretransfer:  %{time_pretransfer}s
redirect:     %{time_redirect}s
starttransfer:%{time_starttransfer}s
total:        %{time_total}s
size:         %{size_download} bytes
speed:        %{speed_download} bytes/s
\n" https://api.example.com/health

# namelookup:    DNS resolution time
# connect:       TCP connection (after DNS)
# appconnect:    TLS handshake (after TCP)
# pretransfer:   Protocol setup after TLS
# starttransfer: TTFB - time to first byte of response
# total:         End-to-end including response body download

# Interpretation:
# namelookup high (>50ms): DNS problem (fix resolver, lower TTL)
# connect - namelookup high: network latency (check routing)
# appconnect - connect high: TLS problem (OCSP, large certs)
# starttransfer - appconnect high: application slow

# Repeat 10 times for percentile data:
for i in $(seq 1 10); do
    curl -o /dev/null -s -w "%{time_total}\n" \
        https://api.example.com/health
done | sort -n
# Last value = P100, second-to-last ≈ P99
```

---

### ⚙️ Latency Budget: How to Allocate 200ms

```
User expects < 200ms response time for an API call.
Budget each phase:

Phase                 │  Budget  │  Typical
──────────────────────┼──────────┼──────────
DNS resolution        │   10ms   │  1-100ms (cached=1ms, miss=100ms)
TCP connect           │   20ms   │  2-200ms (local=2ms, cross-region=200ms)
TLS handshake         │   30ms   │  10-100ms (TLS 1.3=1RTT)
HTTP request/headers  │    5ms   │  1-10ms
Server processing     │  100ms   │  50-500ms (your code!)
Response body         │   20ms   │  1-100ms (depends on size)
Last-mile delivery    │   15ms   │  5-50ms
──────────────────────┼──────────┼──────────
Total budget          │  200ms   │

At 200ms budget: server processing gets only 100ms.
If DNS isn't cached: entire budget consumed before server runs.
```

---

### ⚙️ Propagation Latency Table

```
Route                         One-way RTT
─────────────────────────────────────────
Same data center (1 Gbps)     0.05-0.5ms
Same city (metropolitan)      1-2ms
US East - US West             30-40ms
US East - London              75-85ms
US East - Frankfurt           90-100ms
US East - Tokyo               150-180ms
US East - Sydney              180-200ms
US East - Bangalore           195-220ms
LEO Satellite (Starlink)      20-40ms
GEO Satellite                 600-700ms

Speed of light in fiber: 200,000 km/s
NYC to London: 5,500 km / 200,000 = 27.5ms one-way
Observed: ~80ms RTT (accounts for routing detours, processing)
Overhead factor: ~1.4-2.0x over theoretical minimum
```

---

### ⚙️ Tail Latency: Why P99 > P50 × 2 Is a Red Flag

```
P50 = median: 50% of requests faster than this
P95 = 95th percentile: 95% of requests faster than this
P99 = 99th percentile: 99% of requests faster than this
P999 = 99.9th percentile: 1 in 1000 requests

Healthy distribution:
  P50=10ms, P95=25ms, P99=50ms, P999=100ms
  P99/P50 = 5 (acceptable)

Problematic distribution:
  P50=10ms, P95=100ms, P99=500ms, P999=5000ms
  P99/P50 = 50 (pathological - long tail)

Causes of long tail:
  - Garbage collection pauses (Java, Go GC stop-the-world)
  - Lock contention (shared mutable state)
  - Disk I/O (spinning disks with elevator algorithm)
  - Head-of-line blocking (one slow request blocks others)
  - Connection pool exhaustion (wait for available connection)
  - DNS negative caching (cold miss on first lookup)

Measurement matters:
  Average (mean) latency is misleading:
    10 requests at 10ms + 1 request at 1,000ms
    Mean = 100ms  ← looks bad
    P99 = 1,000ms ← this is the actual problem
  
  Always measure P99 and P999 for SLA compliance
```

---

### ⚙️ Network Measurement Tools

```bash
# 1. Round-trip time baseline
ping -c 100 target.host
# Look at: min/avg/max/stddev
# stddev high = variable latency (queuing or wireless)

# 2. Path trace with latency per hop
traceroute -n target.host     # Linux
tracert -d target.host        # Windows
mtr -n target.host            # modern: combines ping + traceroute

# mtr output (best tool for path analysis):
#                        My traceroute
# HOST           Loss%  Snt  Last  Avg  Best  Wrst  StDev
# 192.168.1.1    0.0%   100   0.3   0.3   0.2   1.2   0.1
# ...
# 104.26.10.76   0.0%   100  12.4  12.5  12.1  14.2   0.3
#   ← StDev > 2ms on a hop = that hop has queuing or issues

# 3. TCP connection time (bypasses DNS)
time nc -zv TARGET_IP PORT
# or
curl --connect-timeout 5 --max-time 10 \
  -o /dev/null -w "TCP: %{time_connect}s\n" \
  https://TARGET_IP:443

# 4. Bandwidth measurement between two hosts (iperf3)
# Server:
iperf3 -s

# Client:
iperf3 -c server_ip -t 10 -P 4  # 10s test, 4 parallel streams
# Look for: Sender bitrate (throughput to server)
#           Retransmits (packet loss under load)

# 5. HTTP latency histogram (wrk load tester)
wrk -t4 -c100 -d30s --latency https://api.example.com/health
# Output:
#   Latency    Avg   Stdev   Max   +/-Stdev
#     12.50ms  3.44ms  45.20ms  89.38%
#   Latency Distribution
#      50%    11.00ms
#      75%    13.00ms
#      90%    16.00ms
#      99%    36.00ms  ← this is what users at 99th percentile see
```

---

### ⚙️ Failure Example: Sudden P99 Spike in Production

**Symptoms:** P99 latency spikes from 50ms to 2,000ms
every 4 minutes. P50 is unchanged at 15ms. No errors.

**Diagnosis:**

```bash
# Pattern: spike every 4 minutes exactly = scheduled process
# Check what runs every 4 minutes:
crontab -l
# */4 * * * * /opt/app/scripts/backup.sh

# Is it generating network traffic?
sudo tcpdump -i eth0 -n -q 2>&1 | head -20 &
# While spike occurs, look for traffic bursts

# Is it generating disk I/O that affects the process?
iostat -x 1 5
# Look for: busy_time spike every 4 minutes

# Root cause: backup script runs every 4 minutes
# Saturates network interface for 10-15 seconds
# During saturation: queuing delay explodes
# API requests queue behind backup traffic

# Fix: tc qdisc (traffic control) - limit backup bandwidth
sudo tc qdisc add dev eth0 root handle 1: htb default 10
sudo tc class add dev eth0 parent 1: classid 1:10 \
  htb rate 100mbit burst 10mbit
sudo tc class add dev eth0 parent 1: classid 1:20 \
  htb rate 10mbit burst 1mbit  ← backup limited to 10 Mbps
# Mark backup traffic with class 1:20 (via iptables MARK)
```

---

### 📐 Scale and Latency Relationships

```
Latency budget at scale:
  1 microservice call: 10ms
  10 sequential calls: 100ms
  Fan-out 10 parallel: 10ms (but adds tail latency)

Little's Law: L = λ × W
  L = avg concurrent requests in system
  λ = throughput (req/s)
  W = avg latency (seconds)
  
  1,000 RPS × 0.1s latency = 100 concurrent requests
  If max connections = 50: queuing starts at 500 RPS
  Queue adds latency: W increases → L increases → more queue

At 10,000 RPS:
  Without connection pooling: 10,000 new TCP/TLS per second
  → TLS handshake CPU becomes bottleneck
  With pooling: 0 new handshakes, amortized cost ≈ 0

Geographic latency strategy:
  Region-local data (read replicas): 2-5ms instead of 100ms
  CDN for static: 5-20ms instead of 100-200ms
  Edge computing: move logic near user → sub-10ms
```

---

### 🧭 Decision Guide

```
What phase is the bottleneck? Use this flowchart:
  1. Measure with curl -w (DNS, connect, TLS, TTFB, total)
  2. namelookup > 50ms? → DNS optimization (caching, resolver)
  3. connect > 100ms? → Network routing issue (traceroute)
  4. appconnect - connect > 50ms? → TLS issue (OCSP, cert size)
  5. starttransfer - appconnect > 200ms? → Server application slow
  6. total - starttransfer > 100ms? → Large response body

Performance rules of thumb:
  Same region: < 5ms   (don't tolerate > 20ms)
  Cross-region: 50-200ms (irreducible)
  DNS cached: < 1ms    (not cached: 50-100ms)
  TLS 1.3: ~10ms       (OCSP uncached: +100ms)

Interview answer for "why is my API slow":
  "First: measure what's slow. curl -w breaks latency into
  DNS, TCP, TLS, application. Most 'slow API' problems are
  either DNS cache miss, TLS OCSP validation, or N+1 database
  queries. Without measuring, you optimize the wrong layer.
  For high-traffic systems: monitor P99, not average - the
  tail latency is what users and SLAs care about."
```