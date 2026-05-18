---
id: NET-061
title: "DDoS Attack Types and Mitigations"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-059, NET-060
used_by: NET-067
related: NET-059, NET-060, NET-064
tags:
  - networking
  - security
  - ddos
  - mitigation
  - xdp
  - anycast
  - rate-limiting
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/net/ddos-attack-types-and-mitigations/
---

**⚡ TL;DR** - DDoS attacks come in three categories:
volumetric (bandwidth exhaustion - UDP floods, amplification),
protocol (SYN floods, resource exhaustion), and application
layer (L7 - HTTP floods, API abuse). Mitigation layers:
anycast (distributes volume), XDP (kernel drop at line
rate), rate limiting (per-IP, per-subnet), CAPTCHA and
challenge pages (bot filtering), BGP blackholing (nuclear
option). The 3.8 Tbps Cloudflare DDoS (2024) was stopped
without human intervention. The key insight: you cannot
out-scale a botnet - you must detect and drop malicious
traffic close to the source, fast.

| #061 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | MTU Fragmentation and PMTUD (NET-059), Anycast Routing (NET-060) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | MTU Fragmentation and PMTUD, Anycast Routing, Cloudflare BGP Incident | |

---

### 🔥 The Problem This Solves

Your service has 10 Gbps uplink. An attacker controls
100,000 compromised devices, each sending 1 Mbps. Total:
100 Gbps attack. Your network is overwhelmed before any
application-level defense can help. You need defenses
upstream of your infrastructure, and automatic detection
that doesn't require human action on a 3 AM Saturday.

---

### 🧠 Intuition: Attack Taxonomy

```
DDoS attacks by layer:
  
  L3/L4 Volumetric (bandwidth exhaustion):
    Goal: fill your uplink with junk traffic
    Examples: UDP flood, ICMP flood, DNS amplification
    Size: can reach Tbps
    Defense: upstream scrubbing, anycast, BGP blackhole
    
  L3/L4 Protocol (resource exhaustion):
    Goal: exhaust firewall/server state tables
    Examples: SYN flood (TCP half-open state), ACK flood
    Size: lower bandwidth, but more dangerous to infrastructure
    Defense: SYN cookies, state table tuning, rate limits
    
  L7 Application (logic exhaustion):
    Goal: exhaust CPU/DB by sending expensive requests
    Examples: HTTP floods, slow reads, API scraping
    Size: lower bandwidth, harder to distinguish from real traffic
    Defense: rate limiting, CAPTCHA, behavior analysis

Attack effectiveness:
  Volumetric: easy to generate, hard to defend (bandwidth)
  Protocol: moderate difficulty, medium defense
  Application: hardest to detect, cheapest to generate
```

---

### ⚙️ Volumetric Attack Types

```bash
# UDP Flood: send max-rate UDP to random ports
# Target: every UDP packet = kernel interrupt + port lookup
# Bandwidth: attacker bandwidth × botnet size
# Defense:
sudo iptables -A INPUT -p udp \
  --dport 1:1024 -j DROP
# Or: rate limit UDP from single IP:
sudo iptables -A INPUT -p udp -m limit \
  --limit 1000/second -j ACCEPT
sudo iptables -A INPUT -p udp -j DROP

# DNS Amplification: exploit open DNS resolvers
# Attacker sends: 40-byte DNS query (spoofed src = victim IP)
# Resolver responds: 3,000-byte DNS response → to victim
# Amplification factor: 75x (3000/40)
# Defense: disable open recursion on DNS servers
# named.conf:
# allow-recursion { trusted-networks; };
# (don't allow recursion for unknown IPs)

# NTP Amplification (monlist attack):
# 90-byte query → 4,800-byte response = 53x amplification
# Fix: disable monlist (ntpdc -c monlist disabled in modern ntpd)
# Or: block NTP from internet-facing interfaces

# SSDP Amplification (UPnP):
# 30-byte request → 5,000-byte response = 166x amplification
# Fix: block UDP 1900 from internet to your servers

# Anycast defense for volumetric:
# 1 Tbps attack distributed across 300 PoPs = 3.3 Gbps each
# Each PoP has capacity >> 3.3 Gbps
# XDP drops at NIC driver level before kernel is stressed
```

---

### ⚙️ Protocol Attack: SYN Flood

```bash
# SYN flood: send millions of TCP SYN with spoofed source IPs
# Server allocates TCB (TCP control block) per SYN
# Server sends SYN-ACK to spoofed IP (no reply)
# Server waits tcp_synack_retries × timeout = ~180s
# Default listen backlog: 128-512 entries
# SYN flood exhausts backlog → legitimate SYN dropped

# Check current backlog usage:
ss -lnt | grep :80
# Or: see dropped SYNs:
netstat -s | grep "SYNs to LISTEN"

# Defense 1: SYN Cookies (Linux default when backlog full)
# Server encodes connection state in ISN (initial sequence number)
# No state stored until ACK arrives (proves real client)
sysctl net.ipv4.tcp_syncookies   # should be 1
sysctl -w net.ipv4.tcp_syncookies=1  # enable

# Defense 2: Increase backlog
sysctl -w net.ipv4.tcp_max_syn_backlog=65536
# Application listen backlog must also be increased:
# Java: ServerSocket(port, 65536)
# nginx: listen 80 backlog=65536;

# Defense 3: Reduce SYN-ACK retransmit timeout
sysctl -w net.ipv4.tcp_synack_retries=2
# Default 5 retries = ~90s per half-open connection
# 2 retries = ~15s → faster cleanup

# Defense 4: iptables rate limit SYN per source IP
sudo iptables -A INPUT -p tcp --syn -m limit \
  --limit 100/second --limit-burst 200 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
# Allows 100 SYN/second per IP, drops excess

# Defense 5: XDP SYN cookie at line rate (kernel bypass)
# Cilium and Cloudflare implement SYN cookies in XDP
# Handles millions of SYNs/second per core
```

---

### ⚙️ Application Layer (L7) DDoS

```python
# HTTP flood: legitimate HTTP requests at high rate
# Appearance: looks like real traffic
# Target: expensive endpoints (search, login, report generation)
# Defense: rate limiting + behavior analysis

# Example: FastAPI rate limiting middleware
from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
import time

app = FastAPI()
request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    window = 60  # 1-minute window
    limit = 100  # 100 requests per minute

    # Sliding window
    requests = request_counts[ip]
    requests[:] = [t for t in requests if now - t < window]

    if len(requests) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    requests.append(now)
    response = await call_next(request)
    return response

# More sophisticated: token bucket per user/API key
# See: slowapi, fastapi-limiter, nginx limit_req_zone

# Slow POST attack (Slowloris variant for requests):
# Attacker opens connection, sends headers slowly
# Server holds connection open waiting for body
# 1000 slow connections exhaust server threads
# Defense: set read/write timeouts
# nginx:
# client_body_timeout 10s;
# client_header_timeout 10s;
# keepalive_timeout 65s;
# send_timeout 10s;
```

---

### ⚙️ Wrong vs Right: Blocking by IP vs Rate Limiting by Behavior

```bash
# BAD: blocklist individual attack IPs
sudo iptables -A INPUT -s 1.2.3.4 -j DROP
sudo iptables -A INPUT -s 1.2.3.5 -j DROP
# ... 10,000 more rules

# Problems:
# 1. Botnets rotate IPs - blocking yesterday's IPs doesn't help
# 2. 10,000 iptables rules: O(n) scan per packet = performance hit
# 3. Spoofed IPs: attacker changes source every packet
# 4. Manual: can't keep up with automated attacks

# GOOD: rate limiting by source subnet (classful)
sudo iptables -A INPUT -p tcp --syn \
  -m hashlimit \
  --hashlimit-above 100/second \
  --hashlimit-burst 200 \
  --hashlimit-mode srcip \
  --hashlimit-name syn_rate \
  -j DROP
# Tracks per-source-IP rate (kernel hash table)
# Works for distributed attack: limits per botnet node
# ipset for CIDR-based blocking (more efficient than iptables list):
sudo ipset create blocked_cidrs hash:net maxelem 65536
sudo ipset add blocked_cidrs 192.168.0.0/16
sudo iptables -A INPUT -m set --match-set blocked_cidrs src -j DROP
# O(1) lookup vs O(n) iptables

# BEST: BGP blackhole routing (for volumetric at ISP level)
# Announce victim IP with community string to ISP/upstream
# ISP drops traffic BEFORE it reaches your network
# (Remotely Triggered Black Hole - RTBH)
# Trade-off: victim IP also goes down for legitimate users
# Use as last resort during severe volumetric attack
```

---

### ⚙️ Multi-Layer Defense Architecture

```
Layer 1: Anycast (distribute volume globally)
  All PoPs announce the same IP
  Attack traffic distributed across 300+ PoPs
  Each PoP sees manageable fraction of attack

Layer 2: XDP / eBPF (drop at line rate)
  Pattern matching in kernel
  Drop malicious patterns before sk_buff allocated
  Can handle 50M+ pps per core (NIC offload)

Layer 3: BGP Flowspec (upstream filtering)
  Announce "drop UDP from 1.2.3.0/24 to my IP"
  Upstream router applies filter
  Attack dropped before reaching your network

Layer 4: Rate limiting at LB/firewall level
  Per-IP, per-subnet, per-ASN rate limits
  Token bucket: allows burst, limits sustained rate
  Geographic: rate limit from suspicious regions

Layer 5: Application-level protection
  CAPTCHA / JS challenge (Cloudflare Turnstile)
  Behavioral analysis (anomaly detection)
  API rate limiting per authenticated user
  Bot detection (fingerprinting, headless browser detect)

Layer 6: Circuit breaker (protect backend)
  Even if L1-5 pass some traffic:
  Circuit breaker limits load on application
  Fail fast: return 503 rather than queue requests
```

---

### 📐 Scale Considerations

```
Attack vectors that scale:
  NTP amplification: 53x factor
    10 Gbps attack → 530 Gbps at victim
  DNS amplification: up to 100x factor
    Amplified by open resolvers worldwide
  Memcached amplification: 51,000x factor (UDP, old versions)
    150-byte request → 7.6 MB response
    Patched in modern versions; block UDP 11211

Defense scaling:
  Without anycast: single DC limited by uplink (10-100 Gbps)
  With anycast: limited by total PoP capacity (Tbps range)
  XDP: linear with core count (~14M pps/core)
  Cloudflare (2024): 100+ Tbps capacity, blocked 3.8 Tbps

Real incident timelines:
  AWS Shield: automatic mitigation < 5 seconds
  Cloudflare: autonomous mitigation < 1 second (2024)
  On-premise without scrubbing: 15-60 minutes for manual response
  Time during attack: every second = revenue loss
```

---

### 🧭 Decision Guide

```
Defense options by organization size:

Individual/small service:
  Cloudflare Free tier: basic DDoS protection
  Rate limiting in nginx/application code
  Fail2ban for connection-based attacks
  Cost: $0-20/month

Mid-size company (< 1M users):
  Cloudflare Pro/Business or AWS Shield Standard
  CDN: offloads most traffic
  nginx rate limiting + upstream proxy
  Cost: $200-5000/month

Large company (> 1M users):
  AWS Shield Advanced ($3,000/month base)
  Cloudflare Enterprise
  Custom BGP RTBH with ISPs
  Dedicated scrubbing infrastructure
  24/7 DDoS response team
  Cost: $10K+/month

Attack type response:
  Volumetric > 1 Gbps: anycast CDN required, can't handle in-house
  SYN flood: SYN cookies + iptables rate limiting
  HTTP flood: rate limiting per IP + CAPTCHA on suspicious patterns
  Amplification: contact ISP to block reflection source ports

Emergency response during attack:
  1. Enable BGP blackhole (upstream drop) → stops attack traffic
  2. Enable CDN/scrubbing service (Cloudflare, Akamai)
  3. Rate limit at edge firewall (blocks some attack IPs)
  4. Tighten application rate limiting
  5. Post-incident: identify attack patterns, update rules permanently
```