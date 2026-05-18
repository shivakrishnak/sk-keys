---
id: NET-018
title: "Top 10 Networking Interview Questions (Basics)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-007, NET-009, NET-012, NET-010
used_by: NET-053, NET-054, NET-067, NET-076
related: NET-053, NET-054, NET-067
tags:
  - networking
  - interview
  - foundational
  - reference
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/net/networking-interview-questions-basics/
---

**⚡ TL;DR** - The 10 most common networking questions in
software engineering interviews at the L1 (entry/junior)
level: OSI model, DNS, TCP vs UDP, what happens when you
type a URL, IP addressing, subnets, firewalls, ports, and
latency vs bandwidth.

| #018 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | OSI Model, IP Address, DNS Overview, Port Number | |
| **Used by:** | Networking System Design Interview Patterns, Explain Networking at Every Level, Networking Deep-Dive Interview Questions | |
| **Related:** | Networking System Design Interview Patterns, Networking Deep-Dive Interview Qs | |

---

### 🔥 The Problem This Solves

Networking questions appear in almost every technical
interview, from junior developer to senior architect.
Without a structured set of answers, engineers either
ramble or give shallow responses. This entry provides
calibrated answers - enough depth to satisfy senior
interviewers without getting lost in unnecessary detail.

---

### 📘 Textbook Definition

This entry provides canonical, interview-ready answers to
the 10 most frequent basic networking questions. Each answer
follows the pattern: definition → mechanism → real-world
relevance → common follow-up. Calibrated for a 2-3 minute
verbal answer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Know these 10 answers cold - they appear in some form in
virtually every technical interview.

**Interview meta-principle:**
When answering networking questions, always:
1. Define the concept
2. Explain the mechanism (HOW it works)
3. Give a concrete example
4. Mention a failure mode or trade-off
5. Stop - don't over-explain

---

### 🔩 THE TEN QUESTIONS

---

### Q1: Explain the OSI Model. How many layers? Name them.

**Calibrated Answer (2-3 minutes):**

The OSI model has 7 layers that each handle one concern
in network communication. Bottom to top: Physical (bits on
wire), Data Link (local frame delivery by MAC address),
Network (global routing by IP address), Transport (port-to-
port delivery, TCP/UDP), Session (connection state, TLS
sessions), Presentation (encryption, compression via TLS),
Application (HTTP, DNS, SMTP).

In practice, TCP/IP collapses these into 4 layers: Link,
Internet, Transport, Application. The industry uses OSI
layer numbers for precision: "layer 3 problem" means IP
routing, "layer 7" means the application protocol.

The diagnostic utility is the real value: test bottom-up.
Confirm layer 3 with `ping`. Confirm layer 4 with
`nc -zv host port`. Confirm layer 7 with `curl`.

**Mnemonic:** "Please Do Not Throw Sausage Pizza Away"
(Physical, Data Link, Network, Transport, Session,
Presentation, Application).

**Common follow-up:** "What layer does a firewall operate
at?" - L4 (stateful packet inspection on ports/IPs) or
L7 (WAF on HTTP content).

---

### Q2: What happens when you type google.com in a browser?

**Calibrated Answer (2-3 minutes):**

This is a full-stack question. The steps:

1. DNS: Browser checks cache → OS cache → DNS resolver.
   DNS resolver walks the hierarchy (root → .com TLD →
   Google's NS) to resolve `google.com` to an IP like
   `142.250.80.78`.

2. TCP connection: Browser initiates 3-way handshake
   (SYN → SYN-ACK → ACK) to port 443 on the resolved IP.
   This takes one RTT.

3. TLS handshake: Client and server negotiate cipher suite,
   exchange certificates, derive session keys. TLS 1.3 takes
   one RTT (TLS 1.2: two RTTs).

4. HTTP request: Browser sends `GET / HTTP/2`. Server
   responds with HTML. HTTP/2 allows multiple streams over
   one TCP connection (multiplexing), sending CSS/JS in
   parallel.

5. Browser rendering: Parses HTML, builds DOM, loads
   sub-resources (images, JS, CSS), executes JS.

**Key insight for interviews:** The minimum time is 3 RTTs
(DNS + TCP + TLS 1.3 + HTTP). For a user 100ms away, that's
300ms before the first byte arrives. This is why CDNs,
DNS prefetching, TCP connection reuse, and TLS session
resumption all exist - to eliminate these RTTs.

---

### Q3: What is the difference between TCP and UDP?

**Calibrated Answer (2-3 minutes):**

TCP (Transmission Control Protocol) is connection-oriented
and provides: reliable delivery (retransmit lost packets),
ordered delivery (seq/ack numbers), flow control (receive
window), and congestion control. Cost: connection overhead,
head-of-line blocking, 20+ bytes of header per segment.

UDP (User Datagram Protocol) is connectionless: send and
forget. No reliability, no ordering, no congestion control.
Just 8 bytes of header. Faster for single-packet queries,
supports multicast, avoids HOL blocking.

**When to use each:**
- TCP: HTTP, HTTPS, gRPC, databases, SSH, email - any
  protocol requiring reliable ordered delivery.
- UDP: DNS queries (fast, single packet), video streaming
  (tolerate loss, not delay), VoIP, gaming, QUIC protocol
  (which implements reliability in user space over UDP).

**Key interview insight:** QUIC (HTTP/3) runs over UDP to
avoid TCP head-of-line blocking. It implements reliability,
ordering, and congestion control in user space, gaining
flexibility. A packet loss in one QUIC stream doesn't block
other streams the way it would in TCP.

---

### Q4: What is DNS and how does it work?

**Calibrated Answer (2-3 minutes):**

DNS (Domain Name System) translates domain names to IP
addresses. It's a globally distributed hierarchical
database organized as: Root servers → TLD servers (.com,
.org) → Authoritative servers (per domain) → Resolver
cache.

When a client needs to resolve `api.example.com`:
1. Check local cache and `/etc/hosts`
2. Ask configured resolver (e.g., `8.8.8.8`)
3. Resolver asks root: "who handles .com?" 
4. Root delegates to `.com` TLD servers
5. `.com` TLD delegates to `example.com`'s nameservers
6. Authoritative server returns the A record with TTL

Key record types: A (IPv4), AAAA (IPv6), CNAME (alias),
MX (email), TXT (SPF/DKIM/verification), NS (nameservers).

**Production relevance:** TTL controls cache lifetime.
Always lower TTL to 300s before changing DNS records,
wait 24h for old TTL to expire, then make the change.
Lowering TTL AFTER a change doesn't help.

**Common follow-up:** "What's the difference between a
CNAME and an A record?" - A record maps to IP. CNAME maps
to another name (alias). CNAME cannot be used at the zone
apex (`example.com` itself). Use ALIAS/ANAME or A record
with the CDN's IP instead.

---

### Q5: What is a subnet and CIDR notation?

**Calibrated Answer (2-3 minutes):**

A subnet divides a larger IP network into smaller segments.
CIDR (Classless Inter-Domain Routing) notation expresses
this as `IP/prefix_length`: `10.0.1.0/24` means the first
24 bits are the network prefix, the last 8 bits are for
hosts. A /24 gives 256 addresses (2^8), with 254 usable
(network address `.0` and broadcast `.255` are reserved).

Common subnets in practice:
- `/32`: Single host (used in security groups, routes)
- `/24`: 254 hosts (common for small networks/subnets)
- `/16`: 65,534 hosts (AWS VPCs often use /16)
- `/8`: 16M+ hosts (10.0.0.0/8 = all RFC 1918 10.x space)

**In cloud (AWS VPC):** A VPC has a CIDR block (e.g.,
`10.0.0.0/16`). Subnets within the VPC carve out smaller
ranges (e.g., `10.0.1.0/24` public, `10.0.2.0/24` private).
Routing tables control whether subnets are public (via
Internet Gateway) or private (via NAT Gateway).

**Common follow-up:** "How many usable hosts in a /25?"
A /25 has 2^(32-25) = 128 addresses, 126 usable.

---

### Q6: What is NAT and why is it used?

**Calibrated Answer (~2 minutes):**

NAT (Network Address Translation) allows multiple devices
on a private network (RFC 1918 addresses: 10/8, 172.16/12,
192.168/16) to share a single public IP address when
accessing the internet.

How it works: When a private host (`192.168.1.100`) sends
a packet to the internet, the NAT device (router) replaces
the source IP with its public IP and records the mapping
in a translation table: `(192.168.1.100:50234, 8.8.8.8:53)`
→ `(203.0.113.1:55000, 8.8.8.8:53)`. When the response
arrives, the router reverses the mapping and delivers it
to the right host.

**Why used:** IPv4 address exhaustion. 4.3B addresses
aren't enough for all devices. NAT allows millions of
devices per public IP.

**Cloud relevance:** AWS instances in private subnets use
a NAT Gateway to access the internet (send traffic out
without being directly reachable from outside). AWS charges
per hour + per GB for NAT Gateway.

---

### Q7: What is the difference between a load balancer
and a reverse proxy?

**Calibrated Answer (~2 minutes):**

A **reverse proxy** sits in front of servers and forwards
client requests to backend servers. Single entry point,
hides backend topology, can provide SSL termination,
caching, compression. Examples: Nginx, HAProxy.

A **load balancer** distributes requests across multiple
backend instances to prevent overload. Can be L4 (TCP-
level, routes by IP/port) or L7 (HTTP-level, routes by
URL path, headers). Examples: AWS ALB (L7), NLB (L4),
HAProxy.

**Overlap:** All load balancers are reverse proxies, but
not all reverse proxies are load balancers. A single-backend
Nginx is a reverse proxy but not a load balancer. An ALB
routing to 10 EC2 instances is both.

**When to use L4 vs L7:**
- L4: high throughput, low latency, non-HTTP protocols
  (database connections, generic TCP)
- L7: HTTP routing, path-based routing, A/B testing,
  auth, SSL termination

---

### Q8: What is a firewall? Stateless vs stateful?

**Calibrated Answer (~2 minutes):**

A firewall controls network access by allowing or denying
traffic based on rules. Principle: default-deny (block
everything, allow only what's needed).

**Stateless firewall:** Evaluates each packet independently
against rules (src IP, dst IP, src port, dst port, protocol).
Must explicitly allow return traffic. Fast, simple, but
requires more rules.

**Stateful firewall:** Tracks TCP connection state (SYN
seen = new connection, ACK = established, FIN = closing).
Automatically allows return traffic for established
connections. One rule ("allow ESTABLISHED,RELATED") handles
all return traffic for all services.

**Production:** AWS Security Groups are stateful (return
traffic is automatic). AWS NACLs are stateless (need both
inbound and outbound rules). Linux iptables is stateful
with `conntrack` module.

**Diagnostic tip:** "Connection refused" = firewall REJECT
or no process on port. "Connection timeout" = firewall
DROP or host unreachable.

---

### Q9: What is the difference between latency and
bandwidth?

**Calibrated Answer (~2 minutes):**

**Bandwidth**: how much data can move per second (width
of the pipe). Measured in Mbps/Gbps.

**Latency**: how long for a bit to travel from A to B
(length of the pipe). Measured in milliseconds.

They are independent: a satellite link can have 100Mbps
bandwidth and 600ms latency. A LAN can have 100Gbps
bandwidth and 0.1ms latency.

**Bandwidth-Delay Product (BDP):** bandwidth × RTT = data
in flight. A 1Gbps link with 100ms RTT has BDP = 12.5MB.
TCP window must be >= BDP to fully saturate the link.

**Which matters for what:**
- Bandwidth-bound: file downloads, video streaming, backups
- Latency-bound: API calls (each call needs an RTT),
  interactive UIs, voice/video calls, gaming

**Real-world trap:** Upgrading from 100Mbps to 10Gbps
does NOT speed up 100 sequential API calls. Each call
requires an RTT. The bottleneck is latency.

---

### Q10: What is the purpose of a port number? What
are well-known ports?

**Calibrated Answer (~2 minutes):**

Port numbers (0-65535, 16-bit integers) in TCP/UDP headers
identify the application on a host. IP addresses route
packets to the right machine; port numbers route them to
the right process. A TCP connection is uniquely identified
by the 4-tuple: (src_IP, src_port, dst_IP, dst_port).

Port ranges:
- 0-1023: Well-known ports (require root/admin to bind)
- 1024-49151: Registered ports (applications)
- 49152-65535: Ephemeral ports (client source ports, OS-assigned)

**Must-know well-known ports:**
22=SSH, 25=SMTP, 53=DNS, 80=HTTP, 443=HTTPS, 3306=MySQL,
5432=PostgreSQL, 6379=Redis, 27017=MongoDB

**Connection scaling insight:** A single server can handle
millions of connections on port 443. The 4-tuple uniqueness
allows one port to serve many simultaneous clients (each
client has a different source IP:port). Port exhaustion
(running out of ephemeral ports for outbound connections)
is a real production problem for high-throughput clients.

---

### 🧪 Thought Experiment

**SETUP:**
An interviewer says "Just tell me what you know about
networking." How do you structure a 3-minute response?

**Structure:**
1. "I'll organize by the layers of the network stack..."
2. OSI 7 layers in 30 seconds (top-down or bottom-up)
3. "The practical tools I use daily are..." (dig/ping/nc/curl)
4. "The most common issues I've debugged are..." (DNS,
   firewall, latency)
5. "The key design principle is..." (default-deny, least
   privilege, defense in depth)

**THE INSIGHT:**
Structured answers demonstrate senior-level thinking.
Jumping to "uh, TCP and UDP" without structure shows
junior-level pattern matching.

---

### 🧠 Mental Model / Analogy

> Interview networking questions are like a medical exam:
> they test whether you can apply fundamentals to diagnose
> problems. The examiner doesn't want you to recite
> textbook definitions - they want to know you can use
> the knowledge. Always tie concepts back to:
> - What problem does this solve?
> - When does it fail?
> - How would you diagnose a failure?

---

### 📶 Gradual Depth - Depth Calibration

**Depth calibration by seniority:**

```
┌──────────────────────────────────────────────────────────┐
│  Expected Answer Depth by Level                          │
├────────────────┬─────────────────────────────────────────┤
│  Level         │  Expected for Q1 (OSI)                  │
├────────────────┼─────────────────────────────────────────┤
│  Junior        │  7 layers, names, brief description     │
│                │  1 minute max                           │
├────────────────┼─────────────────────────────────────────┤
│  Mid-level     │  7 layers + PDU names + protocols      │
│                │  Diagnostic use. 2 minutes.             │
├────────────────┼─────────────────────────────────────────┤
│  Senior        │  7 layers + where TCP/IP model differs │
│                │  + real protocol examples + failure     │
│                │  modes. 3 minutes.                      │
├────────────────┼─────────────────────────────────────────┤
│  Staff/Prin.   │  All above + OSI vs TCP/IP politics,   │
│                │  QUIC breaking layer boundaries, eBPF  │
│                │  at L2, DPDK at L1. 3 min max +         │
│                │  invite follow-up questions.            │
└────────────────┴─────────────────────────────────────────┘
```

---

### ⚙️ How It Works (Mechanism)

**Interview answer construction template:**

```
For each networking question, use this structure:

1. DEFINITION (1 sentence): "X is Y that does Z"

2. MECHANISM (2-3 sentences): "How it works: ..."
   Include a concrete example with real numbers

3. WHEN IT FAILS (1 sentence): "Common failure: ..."

4. REAL-WORLD RELEVANCE (1 sentence):
   "In production, this matters because..."

5. STOP. Invite follow-up: "Happy to go deeper on any
   specific aspect."

Total: 1.5 - 3 minutes per answer
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Full diagnostic walk for interview question Q2:**

The interviewer who asks "what happens when you type a URL"
wants to see systems thinking. The best answers cover all
6 phases (DNS, TCP, TLS, HTTP, server, response) with
performance implications. The worst answers stop at "the
browser gets the webpage." Add one failure mode to each
step to demonstrate production experience:

- DNS: What if DNS fails? (Name resolution error, connection
  starts with DNS cache miss adding 300ms)
- TCP: What if TCP fails? (SYN flood attack, connection
  timeout from firewall, connection refused from no process)
- TLS: What if TLS fails? (Expired certificate, self-signed,
  wrong hostname in SAN)
- HTTP: What if HTTP fails? (404 = wrong path, 502 = backend
  down, 504 = backend timeout)

---

### ⚖️ Comparison Table

| Question | Key Concept to Demonstrate | Failure Mode to Mention |
|---|---|---|
| OSI model | Diagnostic layering | Each layer has distinct failure signatures |
| URL in browser | Full-stack flow | DNS failure causes all subsequent steps to fail |
| TCP vs UDP | Trade-off reasoning | HOL blocking in TCP, QUIC over UDP |
| DNS | Caching and TTL | High TTL delays propagation of changes |
| Subnet/CIDR | IP address math | VPC CIDR overlap breaks peering |
| NAT | Address scarcity | Port exhaustion for outbound connections |
| LB vs proxy | Architecture choice | Layer 7 LB adds latency vs Layer 4 |
| Firewall | Default-deny | ICMP blocking breaks PMTUD |
| Latency vs BW | Workload profiling | Upgrading BW doesn't fix latency-bound workloads |
| Port numbers | 4-tuple uniqueness | Ephemeral port exhaustion |

---

### ⚠️ Common Interview Mistakes

| Mistake | Better Approach |
|---|---|
| Reciting the OSI mnemonic without explanation | Give the mnemonic AND explain what each layer does and what fails at that layer |
| "TCP is reliable, UDP is fast" without elaboration | Explain WHY TCP is reliable (retransmit, seq/ack), WHY reliability adds latency (RTTs for retransmit), and WHEN to choose each |
| Not knowing a specific port number | "I know the ranges: well-known below 1024, ephemeral 49152+. The specific port I'd check is `getent services http` or `/etc/services` in practice." Showing process > memorization |
| Answering "what is DNS" with only forward lookups | Mention PTR records (reverse), CNAME aliases, TTL management, and that DNS is the first step of every network connection |

---

### 🚨 Failure Modes & Diagnosis

**Common Interview Failure - Over-explaining**

**Symptom:** Asked "what is DNS?" - answers for 10 minutes
covering DNSSEC, DNS over HTTPS, split-horizon DNS,
anycast routing, EDNS0, and TTL caching strategies.
Interviewer is confused and disengaged.

**Root Cause:** No calibration to the expected depth for
the question's context and the interviewer's level.

**Fix:**
```
CALIBRATED ANSWER STRUCTURE:
1. Answer the question directly (1 sentence)
2. Explain mechanism (2-3 sentences)
3. Give concrete example
4. Mention ONE important failure mode
5. STOP. Say "happy to go deeper" and watch for cues.

If interviewer asks "what else?" → go deeper
If interviewer moves on → you nailed the depth
```

**Prevention:** Practice with a timer. Each answer should
take 1.5-3 minutes maximum. Anything longer is over-
explaining.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OSI Model (Seven Layers)` - Q1 topic in depth
- `IP Address` - Q5 and Q6 topic
- `DNS Overview` - Q4 topic
- `Port Number` - Q10 topic

**Builds On This (learn these next):**
- `Networking System Design Interview Patterns` - how
  these basics appear in system design interview scenarios
- `Explain Networking at Every Level` - how to adjust
  explanation depth for different audiences
- `Networking Deep-Dive Interview Questions` - the L4
  hard questions that follow these basics

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THE TEN      │ OSI, URL journey, TCP/UDP, DNS, Subnet,   │
│ QUESTIONS    │ NAT, LB vs proxy, Firewall, BW/Latency,  │
│              │ Port numbers                              │
├──────────────┼───────────────────────────────────────────┤
│ ANSWER RULE  │ Definition → Mechanism → Example →        │
│              │ Failure → STOP. 1.5-3 min max.            │
├──────────────┼───────────────────────────────────────────┤
│ DEPTH SIGNAL │ Junior: define. Mid: mechanism + example. │
│              │ Senior: mechanism + failure + trade-off.  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Always tie to: "in production this means" │
│              │ Shows operational experience.             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every networking question is really      │
│              │  asking: do you diagnose or guess?"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ System Design Patterns → Deep-Dive Qs    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. OSI diagnostic sequence: bottom-up. ping(L3) → nc(L4)
   → curl(L7). Each answers one layer.
2. URL journey = DNS + TCP + TLS + HTTP. Minimum 3 RTTs.
   This is why CDNs, connection reuse, TLS session
   resumption exist.
3. TCP = reliable+ordered+slow. UDP = unreliable+fast.
   QUIC = reliability over UDP (best of both in user space).

---

### 💎 Transferable Wisdom

**The Meta-Principle for Technical Interviews:**
Technical questions test your reasoning process, not your
memorization. For any networking question:
1. Define the concept
2. Explain the mechanism (how it works internally)
3. Name a failure mode (shows operational experience)
4. State a trade-off (shows engineering maturity)
5. Connect to a real system you've worked with

This pattern works for every domain (databases, OS,
distributed systems), not just networking.

---

### 💡 The Surprising Truth

The interviewer asking "what happens when you type a URL"
almost certainly cannot fully answer it themselves without
gaps. The question has been asked millions of times, with
comprehensive written answers online, precisely because
it has no fixed endpoint - you can always go deeper. The
test is not "can you recite all steps" but "where do you
stop and how coherent is your mental model of the layers
you do cover?" Stopping at DNS + TCP + HTTP with good
explanations beats mentioning 30 topics shallowly.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** all 10 questions clearly in 2-3 minutes
   each without notes, with real examples.
2. **CALIBRATE** depth to the audience - shorter for
   a junior HR screen, deeper for a senior staff interview.
3. **DEMONSTRATE** operational knowledge by adding a
   failure mode or production experience to each answer.
4. **BRIDGE** from basics to system design: "and this
   is why we use a CDN" or "this is why we have connection
   pooling."
5. **INVITE** depth when you know it: "I can go deeper on
   TCP congestion control if that's relevant."

---

### 🧠 Think About This Before We Continue

**Q1.** You're interviewing a candidate for a senior
backend engineer role. They answer "TCP vs UDP" as:
"TCP is reliable, UDP is fast. We use TCP for HTTP and
UDP for video." Rate this answer on a scale of 1-5 for
a senior role. What's missing? What would a 5/5 answer
include?

*Hint: Missing: HOL blocking, QUIC/HTTP3, specific failure
modes of TCP retransmit vs UDP loss behavior, congestion
control algorithms, why UDP for DNS (single RTT). A 5/5
mentions QUIC and includes a real-world trade-off decision.*

**Q2.** An interviewer asks "What is NAT?" and you
answer with the full technical explanation (address
table, PAT, SNAT vs DNAT, carrier-grade NAT, NAT64).
The interviewer says "great, now tell me about subnets."
What signal does this give you about the interview, and
how should you calibrate your next answer?

*Hint: The interviewer may be screening breadth rather
than depth. Moving to the next topic signals "good enough,
don't over-explain." Adjust depth accordingly.*

**Q3.** [Practice] Set a timer for 2 minutes and answer
Q2 (URL in browser) out loud without notes. Record
yourself. Review: Did you cover DNS, TCP, TLS, and HTTP?
Did you mention RTTs and why performance optimization
exists? Did you stop within 2 minutes? Where did you
ramble vs where were you precise?