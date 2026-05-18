---
id: NET-013
title: "Bandwidth vs Latency"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-001, NET-004
used_by: NET-036, NET-048, NET-056
related: NET-048, NET-036, NET-059
tags:
  - networking
  - foundational
  - performance
  - mental-model
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/net/bandwidth-vs-latency/
---

**⚡ TL;DR** - Bandwidth is how much data can move per
second (width of the pipe). Latency is how long it takes
for a single bit to travel from A to B (speed of the pipe).
They are independent - a high-bandwidth link can have high
latency, and vice versa.

| #013 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | The Networking Problem - Why Networks Exist, Packets vs Streams Mental Model | |
| **Used by:** | TCP Congestion Control, Network Latency Sources, Nagle's Algorithm | |
| **Related:** | Network Latency Sources, TCP Congestion Control, MTU Fragmentation | |

---

### 🔥 The Problem This Solves

Engineers routinely conflate bandwidth and latency, leading
to wrong optimization decisions. "We have 10Gbps connections,
our network is fast" - but if latency is 200ms, interactive
applications feel slow. "The latency is only 5ms" - but
if bandwidth is 1Mbps, video streaming is unusable. These
are different problems requiring different solutions.

---

### 📘 Textbook Definition

**Bandwidth** (or throughput): the maximum rate at which
data can be transferred over a network link, measured in
bits per second (bps, Kbps, Mbps, Gbps). Determines how
much data can move in a time window.

**Latency** (or delay): the time for a single packet to
travel from source to destination, measured in milliseconds
(ms). Round-trip time (RTT) is the time for a packet to go
and a response to return - typically what `ping` measures.
Latency has multiple components: propagation delay
(speed of light in medium), transmission delay (time to
put bits on the wire), queuing delay (waiting in router
buffers), and processing delay.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bandwidth = size of the pipe. Latency = length of the pipe.
Both matter, but for different workloads.

**One analogy:**

> A highway analogy: bandwidth is the number of lanes
> (how many cars per hour can travel). Latency is the
> distance (how long the drive takes). A 10-lane highway
> across town (high bandwidth, low latency) is different
> from a 10-lane highway across the country (high bandwidth,
> high latency). For bulk cargo shipping (file downloads),
> more lanes help. For a phone call (interactive), shorter
> distance matters more.

**One insight:**
The Bandwidth-Delay Product (BDP) = bandwidth × RTT.
This is the amount of data "in flight" on the link at any
time. A 1Gbps link with 100ms RTT has BDP = 12.5 MB. TCP
needs a receive window at least this large to fully utilize
the link. This is why high-bandwidth, high-latency links
(satellite internet) require tuned TCP window sizes to
achieve full utilization.

---

### 🔩 First Principles Explanation

**The Four Components of Latency:**

```
┌──────────────────────────────────────────────────────────┐
│  Latency = Sum of Four Delays                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. PROPAGATION DELAY                                    │
│     = distance / speed-of-signal                        │
│     Speed in fiber: ~200,000 km/s (2/3 of light speed) │
│     New York → London: ~5,600 km → ~28ms one-way        │
│     Fixed by physics. Cannot be improved.               │
│                                                          │
│  2. TRANSMISSION DELAY                                   │
│     = packet-size / bandwidth                           │
│     1000-byte packet on 1Mbps: 1000×8/1,000,000 = 8ms  │
│     1000-byte packet on 1Gbps: 1000×8/1,000,000,000    │
│       = 0.008ms (negligible at Gbps speeds)             │
│     Improved by: increasing bandwidth                   │
│                                                          │
│  3. QUEUING DELAY                                        │
│     Time waiting in router/switch buffers               │
│     Variable: 0ms (idle) to 100ms+ (congested)         │
│     Improved by: less congestion, better QoS           │
│                                                          │
│  4. PROCESSING DELAY                                     │
│     Time for router to forward a packet                 │
│     Modern hardware: < 1ms typical                      │
│     Improved by: faster hardware                        │
└──────────────────────────────────────────────────────────┘
```

**Speed-of-light limits:**
```
Fiber optic: ~200,000 km/s (0.67c)
  - Minimum RTT New York → London: ~56ms
  - Real RTT NY → London: 70-80ms (routing overhead)

Physical minimum RTT by distance:
  Same datacenter: < 0.1ms
  Cross-country (US): 40-60ms RTT
  Trans-Atlantic: 70-90ms RTT
  Trans-Pacific: 120-140ms RTT
  Geosynchronous satellite: 480-600ms RTT
  Low Earth Orbit (Starlink): 20-40ms RTT
```

---

### 🧪 Thought Experiment

**SETUP:**
Two scenarios:

**Scenario A:** Downloading a 1GB file over a 100Mbps link
with 200ms RTT (satellite).
- Time to download at full speed: 8 seconds
- But TCP slow start takes many RTTs to reach full speed
- With 200ms RTT, slow start takes 15+ seconds to ramp up
- Result: effective throughput much less than 100Mbps

**Scenario B:** Making 100 API calls over a 10Gbps link
with 5ms RTT (local datacenter).
- Bandwidth: vast (10Gbps is basically unlimited for small API payloads)
- Each API call: 5ms RTT + server processing time
- 100 sequential calls: 500ms+ minimum (100 × 5ms)
- Result: latency is the bottleneck, not bandwidth

**THE INSIGHT:**
For bulk transfers (video streaming, file downloads),
bandwidth determines performance. For interactive workloads
(API calls, key presses, voice packets), latency determines
performance. Identifying which resource is constrained
determines the optimization strategy.

---

### 🧠 Mental Model / Analogy

> **The water pipe analogy:**
> - Bandwidth = pipe diameter (how much water per second)
> - Latency = pipe length (how long for water to arrive)
>
> Filling a swimming pool: you need a wide pipe (bandwidth).
> Turning on lights via a switch: you need a short wire
> (latency). A very wide but very long pipe is great for
> bulk water delivery but awful for a light switch.
>
> **The Bandwidth-Delay Product in this analogy:**
> BDP = pipe diameter × pipe length = volume of water in
> the pipe at any time. If you close the tap, water in the
> pipe still arrives. This "in-flight" volume is BDP.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Bandwidth is how much data your connection can carry per
second (like highway lanes). Latency is how long it takes
for a signal to travel (like highway length). Fast internet
means both: many lanes AND short trips.

**Level 2 - How to use it (junior developer):**
Use `ping` to measure RTT (latency). Use `iperf3` to measure
throughput (bandwidth). A `ping` of 200ms tells you the
minimum time for any request-response cycle. If your API
calls are slow on fast hardware, check `ping` first.
200ms RTT × 100 sequential requests = 20 second minimum
total time, regardless of bandwidth.

**Level 3 - How it works (mid-level engineer):**
TCP throughput = window_size / RTT. If the TCP window is
64KB (default before window scaling) and RTT is 200ms,
maximum throughput is 64KB / 0.2s = 320 KB/s = 2.56 Mbps.
Even on a 1Gbps link with 200ms RTT, TCP achieves only
2.56 Mbps without window scaling. This is the BDP problem.

**Level 4 - Why it was designed this way (senior/staff):**
TCP's flow control was designed for low-latency LANs. The
window size was chosen to hold enough data for LAN RTTs
(< 1ms). Satellite links (200ms RTT) exposed this
limitation in the 1990s. TCP window scaling (RFC 1323)
and SACK were added to address it. Modern TCP buffer sizes
are auto-tuned by the OS to fill the BDP automatically.

**Level 5 - Mastery (distinguished engineer):**
Head-of-line (HOL) blocking is a latency amplification
pathology: in HTTP/1.1, a large response blocks subsequent
responses in the queue. HTTP/2 solves this with
multiplexing (separate streams over one TCP connection).
QUIC solves TCP-level HOL blocking by running streams
over UDP, so packet loss in one stream doesn't block others.
Understanding HOL blocking requires understanding both
bandwidth (streams compete for it) and latency (each
blocked stream adds a full RTT of delay).

---

### ⚙️ How It Works (Mechanism)

**Measuring bandwidth and latency:**

```bash
# Measure RTT (latency)
ping -c 10 google.com
# rtt min/avg/max/mdev = 5.123/5.456/6.100/0.200 ms
# mdev = jitter (variation in latency)

# Measure throughput (bandwidth)
# Requires iperf3 server at the other end
iperf3 -c target_host -t 30
# [ ID] Interval  Transfer   Bandwidth
# [ 5]  0-30 sec  3.37 GBytes  966 Mbits/sec

# Download speed test (no iperf3 server needed)
curl -o /dev/null https://speed.cloudflare.com/__down\
?bytes=100000000
# Shows transfer rate in MB/s

# Calculate Bandwidth-Delay Product
# BDP = bandwidth_Bps * RTT_seconds
# 1 Gbps = 125 MB/s
# RTT = 0.05s (50ms)
# BDP = 125MB/s * 0.05s = 6.25 MB
# TCP window must be >= 6.25 MB to fill 1Gbps at 50ms RTT

# Check TCP buffer sizes (Linux)
sysctl net.ipv4.tcp_rmem
# net.ipv4.tcp_rmem = 4096   131072   6291456
# min, default, max (bytes)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Bandwidth vs Latency decision matrix:**

```
┌──────────────────────────────────────────────────────────┐
│  Which Bottleneck - Bandwidth or Latency?                │
├──────────────────┬───────────────────────────────────────┤
│  Workload Type   │  Primary Bottleneck                   │
├──────────────────┼───────────────────────────────────────┤
│  File download   │  Bandwidth (bulk transfer)            │
│  Video streaming │  Bandwidth (sustained throughput)     │
│  API calls       │  Latency (request-response cycles)    │
│  Interactive UI  │  Latency (keypress-to-feedback)       │
│  Gaming          │  Latency + jitter (consistency)       │
│  Database queries│  Latency (query RTT matters most)     │
│  Batch ETL jobs  │  Bandwidth (moving large datasets)    │
│  Voice/video call│  Latency + jitter (not bandwidth)     │
└──────────────────┴───────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At 10,000 concurrent connections, queuing delay dominates.
Routers and switches build up buffer queues under load.
This causes bufferbloat: artificially high latency from
oversized router buffers. 200ms+ RTT that disappears when
load drops = bufferbloat. Solutions: Active Queue Management
(AQM) algorithms like CoDel, FQ-CoDel. These are now
default in modern Linux (`fq_codel` is the default qdisc
in many Linux distributions).

---

### ⚖️ Comparison Table

| Connection Type | Bandwidth | Latency | Use Case |
|---|---|---|---|
| LAN Ethernet | 1-100 Gbps | < 0.5ms | Local network |
| WiFi 6 | 9.6 Gbps | 1-10ms | Local wireless |
| Broadband cable | 100-1000 Mbps | 10-50ms | Home internet |
| 4G LTE | 10-100 Mbps | 30-70ms | Mobile |
| 5G NR | 100Mbps-1Gbps | 1-10ms | Mobile, IoT |
| Trans-Atlantic fiber | 100 Gbps+ | 70ms | Datacenter interconnect |
| Geosync satellite | 25-100 Mbps | 480-600ms | Remote areas |
| LEO satellite (Starlink) | 50-200 Mbps | 20-40ms | Remote areas |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More bandwidth always means faster applications | For latency-bound workloads (APIs, database queries), more bandwidth does nothing. 10 Gbps vs 1 Gbps makes zero difference for a 1KB API response over a 100ms link. |
| Low latency is always better | For batch jobs, latency barely matters - bandwidth and total throughput are what matter. Chasing sub-millisecond latency for a nightly data pipeline is pointless optimization. |
| `ping` measures my bandwidth | `ping` measures round-trip latency (RTT) only - not bandwidth. Use `iperf3` for bandwidth testing. |
| "Network is slow" always means congestion | Network slowness has many causes: DNS lookup delay (not bandwidth), TLS handshake RTTs (not bandwidth), queuing delay (congestion), or propagation delay (physics - unfixable). Diagnose before optimizing. |

---

### 🚨 Failure Modes & Diagnosis

**Bufferbloat - High Latency Under Load**

**Symptom:** Ping times are 5ms when idle. During a file
upload, ping times jump to 200ms+. Streaming lags when
someone else is downloading. This is bufferbloat.

**Root Cause:** Router buffers are too large. Under load,
packets queue in the buffer. New packets wait behind
buffered ones. Latency spikes dramatically. The large
buffer was intended to prevent packet loss but causes
latency instead.

**Diagnostic Command / Tool:**
```bash
# Test for bufferbloat
# Start a bulk download
curl -o /dev/null https://speed.cloudflare.com/__down\
?bytes=100000000 &

# While downloading, measure latency
ping -c 30 8.8.8.8

# Compare: ping time at rest vs under load
# If latency jumps from 10ms to 200ms: bufferbloat

# Check current qdisc (queue discipline)
tc qdisc show dev eth0
# Should show: fq_codel or cake (good)
# If showing: pfifo or bfifo → problem
```

**Fix:** Enable FQ-CoDel or CAKE on your router (if
configurable). Use ISP's QoS settings. Nothing you can
do from the application side for home router bufferbloat.
In a datacenter, configure qdisc on your network interfaces:
```bash
tc qdisc replace dev eth0 root fq_codel
```

**Prevention:** Use active queue management (AQM). Deploy
CAKE or FQ-CoDel on your network egress points.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Networking Problem - Why Networks Exist` - the context
  for why these properties matter
- `Packets vs Streams Mental Model` - how data moves

**Builds On This (learn these next):**
- `Network Latency Sources and Measurement` - deep dive into
  all latency components including CDN and caching
- `TCP Congestion Control` - how TCP responds to bandwidth
  and queuing constraints
- `Nagle's Algorithm and TCP_NODELAY` - how TCP batches
  small packets to improve bandwidth efficiency at the
  cost of latency

**Alternatives / Comparisons:**
- Throughput vs goodput: throughput includes all bytes
  (including protocol overhead). Goodput is application-
  level useful bytes only. Real performance = goodput.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BANDWIDTH    │ Data per second (pipe width)              │
│              │ Measure: iperf3 or curl download test      │
├──────────────┼───────────────────────────────────────────┤
│ LATENCY      │ Travel time (pipe length)                 │
│              │ Measure: ping RTT, traceroute              │
├──────────────┼───────────────────────────────────────────┤
│ BDP          │ Bandwidth × RTT = data in flight          │
│              │ 1Gbps × 100ms = 12.5MB TCP window needed  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Latency is physics (limited by light).    │
│              │ Bandwidth is engineering (add more fiber). │
├──────────────┼───────────────────────────────────────────┤
│ WORKLOAD FIT │ Latency-bound: APIs, interactive, voice   │
│              │ Bandwidth-bound: file xfer, video, backup  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Upgrading bandwidth to fix latency issues  │
│              │ (they are independent properties)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "10Gbps to moon still has 1.3s RTT.       │
│              │  Bandwidth ≠ speed."                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Network Latency Sources → TCP Congestion  │
│              │ Control → Bandwidth-Delay Product tuning  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Bandwidth = bits/sec (pipe width). Latency = travel time
   (pipe length). `ping` measures latency; `iperf3` measures
   bandwidth.
2. BDP = bandwidth × RTT. TCP window must be >= BDP to
   fully utilize high-BDP links.
3. Latency-bound workloads: sequential API calls, interactive
   UI, voice/video. Bandwidth-bound: file downloads, video
   streaming, backups. Diagnose which you have before fixing.

**Interview one-liner:**
"Bandwidth is the maximum data rate (pipe width). Latency
is the one-way travel time (propagation delay). They are
independent: a high-bandwidth satellite link can have 600ms
latency. The Bandwidth-Delay Product is bandwidth × RTT,
representing the data in flight. TCP must maintain a window
size >= BDP to fully saturate a high-BDP link. Latency-bound
workloads (APIs, interactive) care about RTT; bandwidth-bound
workloads (file transfer, streaming) care about throughput."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every resource has two independent performance axes:
throughput (how much per unit time) and latency (how long
for one unit). Conflating them leads to wrong optimization.
This pattern appears in: database I/O (IOPS vs latency),
CPU design (instructions per second vs single-thread
latency), message queues (messages per second vs delivery
delay), and disk storage (MB/s vs seek time).

**Industry applications:**
- **CDN design** - CDNs primarily reduce latency (by moving
  content closer to users) not bandwidth. A user downloading
  from a local PoP gets the same bandwidth as from origin
  but 10x lower latency for each DNS/TCP/TLS setup.
- **HFT (High-Frequency Trading)** - spend millions to
  reduce trans-Atlantic latency by 1ms using hollow-core
  fiber or microwave towers. Bandwidth is irrelevant for
  a 100-byte order packet.

---

### 💡 The Surprising Truth

The speed of light limits how fast the internet can ever
become. New York to London is ~5,600 km of fiber. At
200,000 km/s (fiber's signal speed), minimum one-way
propagation is 28ms. RTT is 56ms minimum. No protocol
optimization, hardware upgrade, or software improvement
can reduce trans-Atlantic RTT below ~56ms - it is a
physical constant. Companies paid millions to route
financial data through hollow-core fiber (which has
higher signal speed than conventional fiber) to shave
3-5ms off trans-Atlantic latency. This is why the
microwave relay network from Chicago to New York exists:
electromagnetic waves in air travel faster than light in
fiber, saving 5ms on commodity options trading.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the four components of latency and which are
   improvable (queuing, processing) vs which are physics
   (propagation at given distance).
2. **DEBUG** a "slow network" complaint by measuring both
   latency (ping) and bandwidth (iperf3) to identify
   the actual bottleneck.
3. **DECIDE** whether a workload is bandwidth-bound or
   latency-bound, and what optimization to apply to each.
4. **BUILD** the Bandwidth-Delay Product calculation and
   explain why high-BDP links need large TCP windows.
5. **EXTEND** this to explain why HTTP/2 multiplexing
   reduces latency (not bandwidth) and how.

---

### 🧠 Think About This Before We Continue

**Q1.** Your application makes 50 sequential API calls to
complete a page load. Average API latency: 20ms. You upgrade
from 100Mbps to 10Gbps network connection. How much does
the page load time improve? Why?

*Hint: Calculate minimum page load time for both cases.
What does each API call actually use from the network?*

**Q2.** HTTP/2 was designed to improve web performance over
HTTP/1.1. But HTTP/2 actually has WORSE performance than
HTTP/1.1 in high packet loss scenarios (> 2%). Why? What
does this tell you about the relationship between bandwidth
(packet loss recovery) and latency (HOL blocking)?

*Hint: HTTP/2 uses one TCP connection. A lost packet in
TCP blocks ALL streams until retransmitted. HTTP/1.1's
multiple connections means a lost packet only blocks one
request.*

**Q3.** [Hands-On] Use `ping` to measure RTT to: your
router (e.g., `ping 192.168.1.1`), your ISP's DNS
(`ping 8.8.8.8`), a distant server (`ping tokyo.ping.cdn77.com`
or similar). Record min/avg/max/mdev values. Which latency
component dominates at each hop? Does the mdev (jitter)
increase with distance? What does high jitter indicate?