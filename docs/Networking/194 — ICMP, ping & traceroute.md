---
layout: default
title: "ICMP, ping & traceroute"
parent: "Networking"
nav_order: 194
permalink: /networking/icmp-ping-traceroute/
number: "0194"
category: Networking
difficulty: ★☆☆
depends_on: IP Addressing, UDP, TCP
used_by: Networking, Linux, Observability & SRE, Cloud — AWS
related: ARP, DNS, Packet Loss Latency & Jitter, Firewall, NAT
tags:
  - networking
  - icmp
  - ping
  - traceroute
  - diagnostics
  - mtr
---

# 194 — ICMP, ping & traceroute

⚡ TL;DR — ICMP (Internet Control Message Protocol) is the internet's diagnostic protocol — used for error reporting (Destination Unreachable, Time Exceeded) and connectivity testing. `ping` uses ICMP Echo Request/Reply to measure RTT and detect loss. `traceroute` exploits TTL exhaustion to map the network path hop by hop. Both are essential first-response tools for network diagnosis.

---

### 🔥 The Problem This Solves

A service is unreachable. Is it a DNS problem? A routing problem? A firewall? A server-side crash? Network diagnostics require tools to probe connectivity layer by layer. ICMP provides the raw diagnostic capability: `ping` tests basic reachability and measures latency; `traceroute` reveals which hop in the path is failing or adding latency — reducing hours of guesswork to minutes of structured diagnosis.

---

### 📘 Textbook Definition

**ICMP (Internet Control Message Protocol):** A network-layer protocol (RFC 792) used for error messages and operational information. Not a transport protocol — carries no application data. Key ICMP types: Type 0 (Echo Reply), Type 3 (Destination Unreachable), Type 8 (Echo Request), Type 11 (Time Exceeded — TTL=0), Type 12 (Parameter Problem). ICMPv6 (RFC 4443) extends this for IPv6 and also handles neighbour discovery (NDP).

**ping:** A command that sends ICMP Echo Request packets to a destination and measures RTT. Output includes: RTT per packet, packet loss percentage, min/avg/max/mdev RTT statistics.

**traceroute/tracert:** A command that determines the route packets take by sending packets with increasing TTL values. Each router that decrements TTL to 0 sends back ICMP Time Exceeded, revealing the router's IP. Result: hop-by-hop path with latency at each hop.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ping` = "are you there? how long does it take?" (ICMP Echo). `traceroute` = "which routers are between me and you, and how long does each hop take?" (TTL manipulation).

**One analogy:**
> ICMP ping is like knocking on a door: "Anyone home?" The person inside says "Yes!" and you measure how long it took. Traceroute is like sending a letter that self-destructs at each post office (TTL exhaustion), with each post office sending you a postcard saying "your letter died here" — building a map of every postal stop between you and the destination.

---

### 🔩 First Principles Explanation

**ICMP ECHO (PING):**
```
ping google.com:
  1. DNS: resolve google.com → 142.250.x.x (if needed)
  2. Send: ICMP Echo Request
     Type: 8, Code: 0
     Identifier: 12345 (matches request/reply)
     Sequence: 1 (increments per packet)
     Data: timestamp + padding
     
  3. Receive: ICMP Echo Reply from 142.250.x.x
     Type: 0, Code: 0
     Identifier: 12345 (matched)
     Sequence: 1 (matched)
     
  4. RTT = time_received - time_sent
  5. Repeat (default: until Ctrl+C or -c N)

Output:
  64 bytes from 142.250.x.x: icmp_seq=1 ttl=116 time=14.3 ms
  64 bytes from 142.250.x.x: icmp_seq=2 ttl=116 time=13.8 ms
  --- google.com ping statistics ---
  2 packets transmitted, 2 received, 0% packet loss
  rtt min/avg/max/mdev = 13.8/14.0/14.3/0.2 ms
```

**TRACEROUTE MECHANISM (TTL TRICK):**
```
Goal: discover the path to 8.8.8.8

Step 1 (TTL=1):
  Send UDP/ICMP packet with TTL=1 to 8.8.8.8
  First router (192.168.1.1) receives it, TTL becomes 0
  Router sends back: ICMP Type 11 (Time Exceeded)
  Source: 192.168.1.1 → this reveals Hop 1!

Step 2 (TTL=2):
  Send packet with TTL=2
  First router decrements to 1, forwards
  Second router decrements to 0
  Second router sends ICMP Time Exceeded
  Source: 10.0.0.1 → this reveals Hop 2!

... repeat until ICMP Echo Reply (destination reached) or TTL=255

Output:
  traceroute to 8.8.8.8 (8.8.8.8), 30 hops max
   1  192.168.1.1 (192.168.1.1)  1.234 ms  0.987 ms  1.100 ms
   2  10.0.0.1 (10.0.0.1)       5.432 ms  5.211 ms  5.318 ms
   3  * * *                    (hop doesn't respond to ICMP)
   4  8.8.8.8 (dns.google)       14.321 ms

Three time values: traceroute sends 3 probes per TTL (for variance measurement)
* * *: hop is not responding to ICMP Time Exceeded (firewall blocks ICMP)
```

**ICMP ERROR MESSAGES:**
```
Type 3 — Destination Unreachable (sub-codes):
  Code 0: Network Unreachable (no route to network)
  Code 1: Host Unreachable (no route to host)
  Code 3: Port Unreachable (UDP: no process on that port — important!)
  Code 4: Fragmentation Needed (MTU discovery — don't fragment bit set)
  Code 13: Communication Administratively Prohibited (firewall drop)

Type 11 — Time Exceeded:
  Code 0: TTL=0 in transit (used by traceroute)
  Code 1: Fragment reassembly time exceeded

PMTUD (Path MTU Discovery):
  Sender sets DF (Don't Fragment) bit
  If MTU too large for a link → router sends ICMP Type 3 Code 4
  Sender reduces MTU for that destination
  Problem: firewalls blocking ICMP → "PMTUD black hole"
  Fix: TCP MSS clamping (adjust in SYN packet at router)
```

---

### 🧪 Thought Experiment

**DIAGNOSING A NETWORK ISSUE:**
Service at api.example.com is timing out from Tokyo, but works from London.

```bash
# Step 1: DNS (is name resolving?)
dig api.example.com @8.8.8.8
# If no response: DNS issue

# Step 2: Basic reachability (is IP reachable?)
ping api.example.com -c 10
# 100% loss: routing or firewall; High RTT: distance issue

# Step 3: Path (where is the failure?)
traceroute -n api.example.com
# Last responding hop before * * * = where routing fails

# Step 4: Better: MTR (combines ping + traceroute)
mtr --report --report-cycles 100 api.example.com
# Shows: each hop, RTT, packet loss per hop
# Hop with first significant loss = problem point

# Step 5: TCP reachability (is the port open?)
nc -zv api.example.com 443
# Connection refused: no service; Timeout: firewall blocking
curl -v https://api.example.com/health
```

---

### 🧠 Mental Model / Analogy

> Traceroute is like the postal service TTL self-destruct letter. You send a letter to Tokyo, but it has a rule: "destroy this letter after passing through N post offices, and send a postcard back to me from wherever you died." You start with "destroy after 1 office," getting a postcard from your local post office. Then "destroy after 2 offices," getting a postcard from the next town. You keep increasing until the letter finally reaches Tokyo. The postcards form a map of the route. If a post office intercepts and destroys letters silently (firewall), you see `* * *` — no postcard from that office.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `ping` checks if a machine is reachable and measures round-trip time. `traceroute` shows every router between you and the destination. `* * *` means a hop isn't responding (firewall, or doesn't send ICMP).

**Level 2:** Use `mtr` (combines ping + traceroute, continuous): `mtr --report host`. Shows packet loss per hop — if only the final destination shows loss, the network is fine (ICMP deprioritised at destination). If an intermediate hop shows loss AND all subsequent hops show loss = problem at that hop. If intermediate shows loss but destination shows fine = ICMP rate-limited at that hop (transit traffic fine, ICMP responses deprioritised).

**Level 3:** traceroute variations: Linux default uses UDP (high ports). `traceroute -I` uses ICMP. `traceroute -T -p 443` uses TCP on port 443 (bypasses firewalls that block ICMP/UDP but allow TCP 443). `hping3` for more control. `mtr --tcp` for TCP-based traceroute. Paris traceroute: maintains consistent flow hash (5-tuple) per TTL — ensures probes follow the same ECMP path, giving consistent results for load-balanced networks.

**Level 4:** ICMP rate limiting is a security feature and a diagnostic challenge. Routers legitimately rate-limit ICMP replies (e.g., only 100 ICMP Time Exceeded per second per interface) to prevent ICMP from being used for amplification attacks. This causes `* * *` in traceroute even for healthy hops. MTR with 100 probe cycles helps distinguish: consistent `* * *` = firewall block; intermittent = rate limiting. ICMP is also used in covert channels (ICMP tunneling — encapsulate TCP data in ICMP echo payloads). Firewalls should rate-limit and validate ICMP data length to prevent this.

---

### ⚙️ How It Works (Mechanism)

```bash
# Basic ping
ping -c 10 google.com
# -c N: count (N packets)
# -i 0.2: interval 0.2 seconds
# -s 1400: packet size (test MTU issues)
# -W 2: wait 2s for reply

# Flood ping (requires root, test max ICMP rate)
sudo ping -f -c 1000 192.168.1.1

# Ping with timestamp
ping -D google.com  # shows Unix timestamp per packet

# traceroute (Linux) - defaults to UDP
traceroute google.com

# ICMP traceroute (may pass more firewalls)
traceroute -I google.com

# TCP traceroute on port 443 (for firewall-heavy paths)
traceroute -T -p 443 google.com

# MTR (best combined tool)
mtr --report --report-cycles 50 google.com
# Shows: Avg, Best, Worst, StDev, Loss% per hop

# Specific: measure just packet loss to each hop
mtr --no-dns --report google.com | awk 'NR>2 {print $1, $3, $4}'
# hop_num loss% avg_rtt

# ICMP-specific: check for PMTUD issues
ping -M do -s 1472 192.168.1.1
# -M do: Don't Fragment bit
# -s 1472: 1472 + 28 (ICMP+IP header) = 1500 MTU
# If fails with larger size: MTU issue

# Windows equivalent
ping -n 10 google.com
tracert google.com
pathping google.com  # Windows MTR equivalent
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
traceroute to 8.8.8.8:

TTL=1: Probe → [Your Router] → ICMP TTL Exceeded ← Hop 1 revealed
TTL=2: Probe → [Router] → [ISP Router] → ICMP TTL Exceeded ← Hop 2
TTL=3: Probe → ... → [ISP Core] → ICMP TTL Exceeded ← Hop 3
TTL=4: Probe → ... → * * * (firewall blocks ICMP TTL Exceeded)
TTL=5: Probe → ... → [Google Edge] → ICMP TTL Exceeded ← Hop 5
TTL=6: Probe → ... → [8.8.8.8] → ICMP Echo Reply ← DESTINATION!

Result:
 1  192.168.1.1   1.2ms (home router)
 2  10.x.x.1      5.4ms (ISP router)  
 3  72.x.x.1      8.1ms (ISP core)
 4  * * *          (firewall, ICMP blocked)
 5  209.x.x.1     12.3ms (Google edge)
 6  8.8.8.8       14.1ms (destination!)
```

---

### 💻 Code Example

```python
import subprocess
import re
import statistics
from dataclasses import dataclass
from typing import Optional

@dataclass
class PingResult:
    host: str
    packets_sent: int
    packets_received: int
    loss_pct: float
    rtt_min_ms: float
    rtt_avg_ms: float
    rtt_max_ms: float
    rtt_mdev_ms: float

def ping(host: str, count: int = 10) -> PingResult:
    """Run ping and parse results."""
    result = subprocess.run(
        ["ping", "-c", str(count), host],
        capture_output=True, text=True, timeout=30
    )
    output = result.stdout + result.stderr
    
    # Parse packet stats
    stats = re.search(
        r'(\d+) packets transmitted, (\d+) received,'
        r'.*?(\d+(?:\.\d+)?)% packet loss',
        output
    )
    # Parse RTT
    rtt = re.search(
        r'rtt min/avg/max/mdev = '
        r'([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)',
        output
    )
    
    if not stats:
        raise ValueError(f"Could not parse ping output for {host}")
    
    return PingResult(
        host=host,
        packets_sent=int(stats.group(1)),
        packets_received=int(stats.group(2)),
        loss_pct=float(stats.group(3)),
        rtt_min_ms=float(rtt.group(1)) if rtt else 0,
        rtt_avg_ms=float(rtt.group(2)) if rtt else 0,
        rtt_max_ms=float(rtt.group(3)) if rtt else 0,
        rtt_mdev_ms=float(rtt.group(4)) if rtt else 0,
    )

# Connectivity health check
hosts = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
for host in hosts:
    try:
        r = ping(host, count=20)
        status = "✓" if r.loss_pct == 0 else "✗"
        print(f"{status} {host}: avg={r.rtt_avg_ms:.1f}ms "
              f"jitter={r.rtt_mdev_ms:.1f}ms loss={r.loss_pct}%")
    except Exception as e:
        print(f"✗ {host}: {e}")
```

---

### ⚖️ Comparison Table

| Tool | Protocol | Measures | Use case |
|---|---|---|---|
| ping | ICMP Echo | RTT, packet loss | Basic reachability test |
| traceroute | UDP/ICMP/TCP + TTL | Per-hop RTT, path | Path diagnosis |
| mtr | ICMP + TTL | RTT, loss per hop (continuous) | Best all-around diagnosis |
| hping3 | TCP/UDP/ICMP | Custom probes | Advanced testing, ACL testing |
| pathping (Windows) | ICMP + TTL | Per-hop statistics | Windows equivalent to MTR |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `* * *` means the hop is down | Often means the hop rate-limits ICMP or a firewall blocks ICMP Time Exceeded. If the destination is reachable, traffic is passing through `* * *` hops fine |
| No ping reply = host is down | Firewalls often block ICMP. A host may be running a web server (reachable on port 443) while blocking all ICMP. Use `curl`, `nc`, or `nmap` for application-level testing |
| traceroute shows real-time path | traceroute probes one hop at a time, sending multiple probes over seconds. The path may vary between probes (ECMP). For consistent results, use Paris traceroute |

---

### 🚨 Failure Modes & Diagnosis

**MTU Black Hole: TCP Works Slow or Fails on Large Transfers**

```bash
# Symptom: small requests work, large data transfers stall
# Cause: ICMP Type 3 Code 4 (Fragmentation Needed) blocked by firewall
# PMTUD fails → sender keeps using large packets → silently dropped

# Test: ping with DF bit and decreasing sizes
ping -M do -s 1472 target.host  # 1472 + 28 = 1500
ping -M do -s 1400 target.host  # if 1400 works, 1472 fails: MTU issue
ping -M do -s 1300 target.host  # find largest working size

# Linux: check/set interface MTU
ip link show eth0 | grep mtu
ip link set eth0 mtu 1450  # reduce if VPN/tunnel overhead

# TCP MSS clamping (fix PMTUD black holes at router level)
# iptables: clamp TCP SYN MSS to 1452 (or PMTU - 28)
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --clamp-mss-to-pmtu

# Verify ICMP is not blocked end-to-end
traceroute -I target.host  # if works better than UDP traceroute
# → ICMP being filtered for UDP but not ICMP mode
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `UDP`, `TCP`

**Related:** `ARP` (L2 resolution; needed before ICMP can be sent), `Packet Loss, Latency & Jitter` (ping measures these), `Firewall` (ICMP filtering affects diagnostic tools), `DNS` (ping resolves hostnames first)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PING         │ ICMP Echo; measures RTT & loss; -c N      │
│ TRACEROUTE   │ TTL trick; reveals per-hop path & latency │
│ MTR          │ Best combined: --report --report-cycles N │
├──────────────┼───────────────────────────────────────────┤
│ * * *        │ ICMP blocked/rate-limited at that hop;    │
│              │ traffic still flows through!              │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSE     │ 1. ping (reachable?); 2. traceroute (where│
│              │ fails?); 3. mtr (loss per hop)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ping = knock on door; traceroute = map   │
│              │ each postal stop via self-destruct letters"│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're on-call and receive an alert: "50% of users in Asia-Pacific can't reach api.example.com. European users unaffected." Walk through the complete network diagnosis: (a) use mtr from multiple APAC locations (AWS EC2 in Tokyo, Singapore) to identify the failing hop, (b) compare AS paths from APAC vs Europe to the origin (using traceroute -A or BGP looking glass), (c) if the failing hop is the CDN PoP, how do you verify CDN health (check CDN status page, test CDN bypass by hitting origin IP directly), (d) if BGP routing is the issue (APAC traffic going to wrong PoP due to a BGP route change), how do you confirm and escalate, and (e) explain the difference between ICMP being blocked at a hop (mtr shows loss at that hop but destination is reachable) vs a genuine routing failure (mtr shows loss at hop N and all subsequent hops are unreachable).
