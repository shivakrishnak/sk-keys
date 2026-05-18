---
id: NET-019
title: "Your First Network Lab - Phase 1 (Hands-On)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-012, NET-017, NET-015
used_by: NET-033, NET-075
related: NET-033, NET-017, NET-049
tags:
  - networking
  - hands-on
  - lab
  - diagnostics
  - tools
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/net/first-network-lab-phase-1/
---

**⚡ TL;DR** - A practical lab that builds real networking
intuition using only tools you already have: inspect your
own machine's network stack, capture your own DNS and HTTP
traffic, and trace packets to the internet. No special
hardware required. Builds muscle memory for the diagnostic
tools used in production.

| #019 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, DNS Overview, Network Starter Kit, Firewall Basics | |
| **Used by:** | Build a TCP Client-Server (Phase 2), Build a Secure Network Platform (Phase 3) | |
| **Related:** | Build a TCP Client-Server, Network Starter Kit, Wireshark and tcpdump | |

---

### 🔥 The Problem This Solves

Reading about networking without hands-on practice creates
fragile knowledge that fails in interviews and production.
This lab converts conceptual knowledge into tool proficiency.
Every command in this lab is a command you will run again
in production to diagnose real issues.

---

### 📘 Textbook Definition

This is a structured hands-on laboratory covering Phase 1
of the three-phase networking lab series. Phase 1 covers:
network interface inspection, IP routing inspection, DNS
resolution observation, packet capture, and firewall rule
inspection. Requires: Linux (or macOS with minor variations)
or WSL2 on Windows.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
12 hands-on exercises that build diagnostic reflexes using
your own machine - no lab environment needed.

**Lab philosophy:**
Every exercise follows: do the command → observe output →
understand what each field means → predict what would
change if X failed. Theory + observation + prediction =
intuition.

---

### 🔩 Lab Prerequisites

**Requirements:**
- Linux, macOS, or WSL2 on Windows
- `dig`, `ping`, `traceroute`, `ip`, `ss` commands
  (standard on most Linux systems)
- `tcpdump` (may require `sudo`)
- Optional: `nc` (netcat), `mtr`, `iperf3`
- Internet access for external tests

**Install on Ubuntu/Debian if missing:**
```bash
sudo apt-get update && sudo apt-get install -y \
  dnsutils \
  iputils-ping \
  traceroute \
  netcat-openbsd \
  mtr \
  tcpdump \
  iproute2 \
  iperf3
```

---

### 📶 THE LAB - 12 EXERCISES

---

#### Exercise 1: Map Your Network Interfaces

**What you'll learn:** Every interface on your machine,
its IP, MAC, and state.

```bash
# Show all interfaces with IPs
ip addr show

# Expected output (varies by system):
# 1: lo: <LOOPBACK,UP,LOWER_UP>
#   inet 127.0.0.1/8
#   inet6 ::1/128
#
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
#   link/ether aa:bb:cc:dd:ee:ff  ← your MAC address
#   inet 192.168.1.100/24         ← your private IP/subnet
#   inet6 fe80::...               ← link-local IPv6
#
# (May also show: docker0, veth*, virbr0, wlan0)
```

**Record:** Your primary IP address and subnet prefix.
Your MAC address. Any additional interfaces (Docker bridge,
VPN adapter, WiFi).

**Question:** What is the /24 broadcast address for your
IP? (Replace last octet with 255.)

---

#### Exercise 2: Inspect Your Routing Table

**What you'll learn:** How your machine decides where to
send packets.

```bash
# Show IPv4 routing table
ip route show

# Expected output:
# default via 192.168.1.1 dev eth0 proto dhcp
# 192.168.1.0/24 dev eth0 proto kernel scope link
#
# default via X.X.X.X = your default gateway (router)
# 192.168.x.0/24 = local LAN (send directly, no router)
```

**Try:**
```bash
# See which interface/gateway a specific IP uses
ip route get 8.8.8.8
# 8.8.8.8 via 192.168.1.1 dev eth0 src 192.168.1.100
#         ^^^^^^^^^^^^^^^^ → goes through default gateway

ip route get 192.168.1.50
# 192.168.1.50 dev eth0 src 192.168.1.100
# No "via" → same LAN, direct delivery
```

**Question:** What is your default gateway IP? This is
the first hop in `traceroute` to any external destination.

---

#### Exercise 3: ARP Table - Map Local MAC Addresses

**What you'll learn:** Which local hosts your machine has
communicated with recently, and their MAC addresses.

```bash
# Show ARP table (IP → MAC for local hosts)
ip neigh show

# Expected output:
# 192.168.1.1 dev eth0 lladdr 00:11:22:33:44:55 REACHABLE
# ^ gateway MAC (you need this to send any external traffic)
```

**Try:** After browsing to a website:
```bash
ip neigh show
# Do you see any new entries? Why or why not?
# (Browser → HTTPS → TCP → IP → your gateway's MAC)
```

**Insight:** You will NOT see Google's MAC address in your
ARP table. You'll only see your gateway (router). Your
gateway knows the MAC for the next hop, but you don't.
ARP is local-segment only.

---

#### Exercise 4: Full DNS Resolution Trace

**What you'll learn:** How DNS resolution works, step by step.

```bash
# Full recursive trace - see every delegation
dig +trace google.com A

# Output shows:
# . (root) → .com TLD server → google.com NS → A record
# Watch the delegation chain

# Check what your resolver is
cat /etc/resolv.conf
# nameserver 192.168.1.1  (router-based resolver)
# or
# nameserver 8.8.8.8 (Google's resolver)

# Query directly, bypassing local resolver
dig @8.8.8.8 google.com A

# Compare query times:
dig google.com A    # likely cached (fast: < 5ms)
dig google.com A    # second query (from cache)
# Look at: ;; Query time: X msec
```

**Record:** How much faster was the cached response?

---

#### Exercise 5: Observe DNS TTL Countdown

**What you'll learn:** How DNS caching works with TTL.

```bash
# Look up a domain and note the TTL
dig google.com A +noall +answer
# google.com.   299   IN  A  142.250.80.78
#               ^^^
#               TTL = 299 seconds remaining

# Wait 30 seconds and check again
sleep 30 && dig google.com A +noall +answer
# TTL should have decreased by ~30 seconds
```

**Exercise:** Find a domain with a low TTL (try `dig
cloudflare.com A` - they often use short TTLs). How fast
does the TTL count down?

**Question:** If you wanted to change a DNS record and
have the change take effect in 5 minutes, what TTL would
you set beforehand? When must you set it?

---

#### Exercise 6: TCP Connection Investigation

**What you'll learn:** What TCP connections currently
exist on your machine.

```bash
# Show all listening TCP ports
ss -lntp
# LISTEN 0  128  0.0.0.0:22    ← SSH server listening
# LISTEN 0  511  0.0.0.0:80    ← Web server (if running)

# Show all established connections
ss -tnp | grep ESTAB

# After opening a browser tab:
ss -tnp | grep ESTAB
# You'll see connections to port 443 (HTTPS)

# Show connection counts by state
ss -tn | awk '{print $1}' | sort | uniq -c | sort -rn
```

**Record:** How many established TCP connections does
your machine have? (More than you'd expect - browser
keeps connections open, SSH tunnels, etc.)

---

#### Exercise 7: Capture DNS Traffic

**What you'll learn:** What DNS queries look like on the wire.

```bash
# In terminal 1: capture DNS traffic
sudo tcpdump -i eth0 -n "port 53" -v

# In terminal 2: make DNS queries
dig new-domain-not-cached.example.com A
# (Use a domain you haven't visited recently)

# Observe in terminal 1:
# 10:23:45 IP 192.168.1.100.54321 > 8.8.8.8.53: UDP
#   A? example.com                    ← query
# 10:23:45 IP 8.8.8.8.53 > 192.168.1.100.54321: UDP
#   example.com. A 93.184.216.34     ← response
```

**Question:** What protocol does DNS use? What is the
source port of your DNS query? (It should be ephemeral.)

---

#### Exercise 8: Capture HTTP Traffic

**What you'll learn:** What HTTP requests look like, and
why HTTPS is essential.

```bash
# Capture HTTP (unencrypted) traffic
sudo tcpdump -i eth0 -A "port 80" -c 10

# Make an HTTP request to a site that still serves HTTP:
curl -v http://example.com

# With -A flag, tcpdump shows ASCII content.
# You can see the HTTP headers in plain text:
# GET / HTTP/1.1
# Host: example.com
# User-Agent: curl/...
```

**Try HTTPS:**
```bash
sudo tcpdump -i eth0 -A "port 443" -c 20 &
curl -s https://google.com > /dev/null
# HTTPS traffic shows as garbled binary - encrypted
```

**Insight:** HTTP is completely readable by anyone on
your network. HTTPS is opaque. This is exactly why
HTTPS everywhere is essential.

---

#### Exercise 9: Trace the Path to the Internet

**What you'll learn:** How packets travel from your machine
to a public server.

```bash
# Trace path to Google's DNS server
traceroute -n 8.8.8.8

# Expected:
# 1  192.168.1.1   1ms  (your gateway)
# 2  10.0.0.1      5ms  (ISP equipment)
# 3  * * *         (filtered ISP router)
# 4  ...           (backbone hops)
# N  8.8.8.8       45ms (destination)

# TCP-based traceroute (penetrates more firewalls)
traceroute -T -p 443 google.com

# Continuous trace with packet loss stats
mtr --report --report-cycles 20 8.8.8.8
```

**Record:** How many hops to `8.8.8.8`? What is the RTT
at the final hop? How many `* * *` hops (filtered)?

---

#### Exercise 10: Test Connectivity Layer by Layer

**What you'll learn:** The bottom-up diagnostic sequence.

```bash
# Target: github.com

# Layer 3: IP reachability
ping -c 5 github.com

# Layer 4: TCP port
nc -zv github.com 443
nc -zv github.com 22   # SSH port (open for git)

# Layer 7: HTTP
curl -o /dev/null -w "DNS: %{time_namelookup}s\n\
TCP: %{time_connect}s\n\
TLS: %{time_appconnect}s\n\
TTFB: %{time_starttransfer}s\n\
Total: %{time_total}s\n" \
https://github.com

# This shows timing breakdown:
# DNS lookup time
# TCP connection time (after DNS)
# TLS handshake time (after TCP)
# Time to first byte (after TLS)
# Total time
```

**Record:** How long does each phase take? What percentage
of total time is DNS? TLS? TTFB? This is your baseline
for understanding what to optimize.

---

#### Exercise 11: Inspect Firewall Rules

**What you'll learn:** What your machine is currently
allowing or blocking.

```bash
# View iptables rules
sudo iptables -L INPUT -n -v --line-numbers

# Or nftables (modern systems)
sudo nft list ruleset

# Check what's listening and what's exposed
ss -lntp
# Ports listening on 0.0.0.0 = accessible from network
# Ports listening on 127.0.0.1 = local only

# Test if your own ports are accessible from outside
# From ANOTHER machine or phone on same network:
nc -zv YOUR_IP 22
```

**Record:** What services are listening on `0.0.0.0` on
your machine? Are any of them exposed you didn't realize?

---

#### Exercise 12: MTU Discovery

**What you'll learn:** The maximum packet size on your
network path.

```bash
# Find effective MTU to a target
# Start with standard Ethernet MTU minus 28 (IP+ICMP hdr)
ping -M do -s 1472 8.8.8.8   # 1472 + 28 = 1500 bytes

# If it fails, try smaller
ping -M do -s 1400 8.8.8.8
ping -M do -s 1200 8.8.8.8

# Find exact threshold
# Binary search between working and failing sizes

# Check your interface MTU
ip link show | grep mtu
# typical: mtu 1500 (standard Ethernet)
# VPN/tunnel: might show mtu 1420 or similar
```

**Record:** What is your effective MTU to `8.8.8.8`? Is
it 1472 (standard 1500 - 28)? Less? Why might it be less?
(Hint: VPN, tunnel, or ISP PMTUD filtering)

---

### ⚙️ Lab Summary - What You've Learned

```
┌──────────────────────────────────────────────────────────┐
│  Lab 1 Competencies Acquired                             │
├────────────────┬─────────────────────────────────────────┤
│  Tool          │  Skills                                 │
├────────────────┼─────────────────────────────────────────┤
│  ip addr       │  Read interface IP, MAC, state          │
│  ip route      │  Read routing table, trace per-IP route │
│  ip neigh      │  Read ARP table, identify local hosts   │
│  dig           │  DNS lookup, TTL inspection, +trace     │
│  ss -lntp      │  List listening ports with processes    │
│  ss -tnp       │  List established connections           │
│  tcpdump       │  Capture DNS and HTTP traffic            │
│  traceroute    │  Map network path, identify hops        │
│  mtr           │  Continuous path quality measurement    │
│  nc -zv        │  Test TCP port connectivity             │
│  curl -w       │  Measure per-phase HTTP timing          │
│  ping -M do    │  Test effective MTU                     │
│  iptables -L   │  Inspect firewall rules                 │
└────────────────┴─────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You just joined a company and their web application is
reportedly slow. Using only the tools from this lab, design
a 15-minute diagnostic session:

**Suggested investigation sequence:**
1. `dig +trace app.company.com` - is DNS slow or wrong?
2. `curl -w "..." https://app.company.com` - which phase
   is slow? (DNS? TCP? TLS? TTFB?)
3. `traceroute -T -p 443 app.company.com` - routing issue?
4. `mtr app.company.com` - packet loss?
5. `ss -lntp` on the server - is app listening on right port?
6. `sudo tcpdump -i eth0 port 443 -c 50` on server -
   are requests arriving?

**THE INSIGHT:**
Each tool answers one specific question. The 15-minute
diagnostic sequence is structured to rule out layers
systematically before looking at application logs.

---

### 🧠 Mental Model / Analogy

> This lab is like learning to drive: you start by
> understanding the dashboard (ip addr, ip route), then
> the mirrors (arp, ip neigh), then basic operation
> (ping, dig, traceroute), then emergency procedures
> (tcpdump, firewall inspection). You must practice each
> until it's automatic - the diagnostics you need in a
> 3am incident must come without thinking.

---

### 🔄 The Complete Picture - End-to-End Flow

**What to do after this lab:**
- Repeat each exercise until you can run them without
  looking at notes
- Add these tools to muscle memory: `ip addr`, `ss -lntp`,
  `dig +short`, `ping -c 5`
- Set up a simple HTTP server on your machine and capture
  its traffic with tcpdump while curling it
- Phase 2 (NET-033): Build a TCP client-server program
  and capture the connection in Wireshark

---

### ⚖️ Comparison Table - Lab vs Production

| Lab Exercise | Production Usage |
|---|---|
| `ip addr show` | Verify new server's IP assignment; debug IP conflict |
| `ip route get X` | Debug unexpected routing on a host |
| `dig @8.8.8.8 domain` | Bypass broken local resolver during incident |
| `ss -lntp` | Verify service is listening after deployment |
| `tcpdump port 80` | Capture traffic during HTTP debugging |
| `traceroute -T` | Identify where packets are being dropped |
| `mtr` | Diagnose intermittent packet loss between sites |
| `nc -zv` | Health check in deployment scripts |
| `ping -M do -s` | Debug MTU issues after VPN configuration |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTERFACE    │ ip addr show                              │
├──────────────┼───────────────────────────────────────────┤
│ ROUTING      │ ip route show / ip route get X.X.X.X      │
├──────────────┼───────────────────────────────────────────┤
│ ARP          │ ip neigh show                             │
├──────────────┼───────────────────────────────────────────┤
│ DNS          │ dig @8.8.8.8 domain A +noall +answer      │
├──────────────┼───────────────────────────────────────────┤
│ TCP PORTS    │ ss -lntp (listening) / ss -tnp (active)   │
├──────────────┼───────────────────────────────────────────┤
│ CAPTURE      │ sudo tcpdump -i eth0 -n port 53 -v        │
├──────────────┼───────────────────────────────────────────┤
│ PATH         │ traceroute -T -p 443 / mtr --report       │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ curl -o /dev/null -w "%{time_*}"          │
├──────────────┼───────────────────────────────────────────┤
│ FIREWALL     │ sudo iptables -L INPUT -n -v              │
├──────────────┼───────────────────────────────────────────┤
│ MTU          │ ping -M do -s 1472 target                 │
└──────────────────────────────────────────────────────────┘
```

---

### 💡 The Surprising Truth

The most valuable networking skill is not understanding
BGP or IPv6 internals - it's the habit of running
`tcpdump` and `ss` before assuming anything. Engineers
who say "the network is broken" before checking with
tools waste hours. Engineers who capture 10 packets,
see the TCP RST, and say "the firewall is sending RST
after the SYN" fix it in 5 minutes. Wireshark was
created not because networking is complex but because
assumptions are dangerous. The tool habit is the skill.

---

### ✅ Mastery Checklist

**You've completed this lab when you can:**
1. **RUN** `ip addr`, `ip route`, `ss -lntp`, `dig +trace`
   without looking at notes and interpret the output.
2. **CAPTURE** DNS and HTTP traffic with `tcpdump` and
   read the packet headers.
3. **TRACE** a connection from your machine to a remote
   server layer by layer with timing information.
4. **IDENTIFY** which phase (DNS/TCP/TLS/TTFB) is slowest
   using `curl -w` timing data.
5. **DIAGNOSE** a simulated failure: stop a local service
   and use `ss` + `nc` to confirm it's down.

---

### 🧠 Think About This Before We Continue

**Q1.** You run `ss -lntp` and see your web server is
listening on `127.0.0.1:8080` instead of `0.0.0.0:8080`.
External clients cannot connect. What is the immediate
fix? What configuration in your server code caused this?
How would you verify the fix worked?

*Hint: Bind address `127.0.0.1` = localhost only. Change
to `0.0.0.0` = all interfaces. Verify with `ss -lntp`
and external `nc -zv` test.*

**Q2.** During the HTTP capture exercise (Exercise 8),
you notice that even for HTTPS connections to `google.com`,
tcpdump shows the destination IP (e.g., `142.250.80.78`).
You cannot see the HTTP content (it's encrypted). But can
you determine WHICH website the user is visiting from
the TLS traffic alone? (Research: TLS SNI)

*Hint: TLS Client Hello contains an SNI (Server Name
Indication) field with the hostname in cleartext, even
though the HTTP content is encrypted. This is one reason
DoH (DNS over HTTPS) and ECH (Encrypted Client Hello)
exist.*

**Q3.** [Challenge] Write a shell script that:
1. Accepts a hostname as argument
2. Runs DNS lookup and records the IP
3. Pings the IP 5 times and records avg RTT
4. Tests TCP ports 80 and 443
5. Runs a curl timing test for HTTPS
6. Outputs a summary report

This is a simplified version of what synthetic monitoring
tools do. Once written, this is a script you'll reuse
in production.