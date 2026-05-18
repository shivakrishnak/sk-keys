---
id: NET-015
title: "Firewall Basics"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-010, NET-014
used_by: NET-052, NET-061, NET-066
related: NET-052, NET-061, NET-009, NET-010
tags:
  - networking
  - foundational
  - security
  - access-control
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/net/firewall-basics/
---

**⚡ TL;DR** - A firewall controls which network traffic
is allowed or denied based on rules. Stateless firewalls
filter individual packets. Stateful firewalls track
connection state. Layer 7 firewalls inspect application
content (WAF). Default-deny is the fundamental security
principle.

| #015 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, Port Number, Packet Structure | |
| **Used by:** | Network Segmentation and Firewall Rules, DDoS Attack Types, Network Compliance | |
| **Related:** | Network Segmentation and Firewall Rules, DDoS, IP Address, Port Number | |

---

### 🔥 The Problem This Solves

Without firewalls, every service on a machine is reachable
from anywhere on the network. An SSH server on port 22 that
should only be accessible by engineers would be reachable
by automated scanners worldwide. A database on port 3306
that should be internal-only would be directly exposed to
the internet. Firewalls enforce the principle of least
privilege at the network layer.

---

### 📘 Textbook Definition

A **firewall** is a network security device or software
that monitors and controls incoming and outgoing network
traffic based on configured security rules. Firewalls
can be: (1) **Packet-filtering (stateless)** - inspect
individual packets against rules (IP, port, protocol);
(2) **Stateful** - track connection state (SYN/established/
FIN), allow return traffic automatically; (3) **Application
layer (Layer 7/WAF)** - inspect HTTP content, block SQL
injection, XSS, etc. The security model is typically
**default-deny**: everything is blocked unless explicitly
allowed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A firewall is a security checkpoint: every packet checks
against a ruleset. Default-deny means "blocked unless
explicitly allowed."

**One analogy:**

> A firewall is like a building security desk:
> - Stateless: checks each person's badge color on entry
>   but doesn't remember who's in the building.
> - Stateful: knows who entered (tracks connection state),
>   so they can exit without showing ID again. Alerts if
>   someone tries to exit who never entered.
> - Layer 7 (WAF): reads the actual content of what
>   people carry - not just badge checks, but bag scans.

**One insight:**
The critical insight is **connection tracking** (stateful).
A stateless firewall must explicitly allow return traffic
(the ACK for your SYN). A stateful firewall knows a SYN
went out, so it automatically allows the SYN-ACK back in.
This is why `iptables -A INPUT -m state --state
ESTABLISHED,RELATED -j ACCEPT` is almost always in
production Linux firewall configs.

---

### 🔩 First Principles Explanation

**Three generations of firewalls:**

```
┌──────────────────────────────────────────────────────────┐
│  Firewall Types - OSI Layer Operation                    │
├──────────────┬───────────────────────────────────────────┤
│  Type        │  What It Inspects                        │
├──────────────┼───────────────────────────────────────────┤
│  Stateless   │  L3: src/dst IP                          │
│  (packet     │  L4: protocol (TCP/UDP/ICMP)             │
│  filter)     │  L4: src/dst port                        │
│              │  L3: IP flags (DF, MF)                   │
│              │  No memory between packets               │
│              │  Fast, but must allow all return traffic  │
├──────────────┼───────────────────────────────────────────┤
│  Stateful    │  All of stateless +                      │
│  (connection │  TCP state: SYN → ESTABLISHED → FIN      │
│  tracking)   │  Allows return traffic automatically      │
│              │  Drops unexpected packets (no matching    │
│              │  connection state)                        │
│              │  Standard for most enterprise firewalls   │
├──────────────┼───────────────────────────────────────────┤
│  L7 / WAF    │  All of stateful +                       │
│  (application│  HTTP URL/path inspection                 │
│  firewall)   │  HTTP header analysis                    │
│              │  SQL injection pattern detection          │
│              │  TLS termination required for inspection  │
│              │  High CPU overhead per connection         │
└──────────────┴──────────────────────────────────────────-┘
```

**Firewall rule evaluation:**

```
┌──────────────────────────────────────────────────────────┐
│  Rule Matching - FIRST MATCH WINS                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Rules evaluated top to bottom (iptables chains,         │
│  AWS security groups evaluate ALL rules, AWS wins with   │
│  allow, blocks unless no allow matches)                  │
│                                                          │
│  Typical rule order:                                     │
│  1. ALLOW established/related (stateful return traffic)  │
│  2. ALLOW loopback (127.0.0.1)                           │
│  3. ALLOW SSH from management IP range only             │
│  4. ALLOW HTTP/HTTPS from anywhere (0.0.0.0/0)          │
│  5. ALLOW specific internal service port from VPC CIDR  │
│  6. DROP everything else (default deny)                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You have a web server (port 80/443), SSH daemon (port 22),
and MySQL (port 3306). Define the minimal firewall ruleset.

**Minimal correct ruleset:**
```
INBOUND:
  ALLOW TCP:443 from 0.0.0.0/0 (HTTPS from anyone)
  ALLOW TCP:80  from 0.0.0.0/0 (HTTP from anyone)
  ALLOW TCP:22  from 10.0.0.0/8 (SSH from internal only)
  DENY  ALL     from 0.0.0.0/0 (default deny)

OUTBOUND:
  ALLOW ALL to 0.0.0.0/0 (or restrict to required targets)

For MySQL:
  MySQL should not have ANY external firewall rule.
  It should bind to 127.0.0.1 only (localhost).
  Defense in depth: even if firewall is misconfigured,
  MySQL won't accept external connections.
```

**THE INSIGHT:**
Defense in depth: the application (MySQL binding to
127.0.0.1) provides a second layer of protection in case
the firewall is misconfigured. Relying on only one layer
(firewall) for database security is a known risk - firewall
rules have accidental wildcards, are sometimes temporarily
disabled for debugging, and can be misconfigured during
cloud configuration changes.

---

### 🧠 Mental Model / Analogy

> Firewall rules are like an allow list at a nightclub door:
> - Default deny = no one gets in without being on the list
> - Stateless rule = "badge color green: enter"
> - Stateful rule = "you left an hour ago - the fact you
>   have a receipt proves you're coming back, not trying
>   to sneak in"
> - L7 rule = "checking what you're bringing IN, not just
>   who you are"
>
> The order of rules matters: if "ban everyone named Smith"
> comes AFTER "allow VIP list" and Smith is on both - who
> wins? In iptables: first match wins. In AWS security
> groups: ALLOW always wins (no deny rules in inbound SG).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A firewall blocks unwanted network connections. Like a door
with a lock: only people with the right key (matching rule)
get in.

**Level 2 - How to use it (junior developer):**
On Linux, use `iptables -L -n` or `nft list ruleset` to
see current rules. In cloud (AWS), Security Groups control
inbound/outbound per instance. In GCP, Firewall Rules are
VPC-level. Default: no inbound allowed. You must explicitly
open ports. Missing firewall rule = "connection refused".
Firewall blocking = "connection timed out" (packet dropped).

**Level 3 - How it works (mid-level engineer):**
Linux `iptables` processes packets through "chains"
(INPUT, OUTPUT, FORWARD). Each rule in the chain specifies
match criteria and action (ACCEPT, DROP, REJECT). DROP
silently discards; REJECT sends ICMP error back to sender.
The difference: DROP is harder to scan (attacker doesn't
know if host exists), REJECT is more user-friendly (tells
client quickly instead of waiting for timeout).

**Level 4 - Why it was designed this way (senior/staff):**
Stateful packet inspection was invented in 1994 because
stateless firewalls required maintaining both inbound and
outbound rules for each service. Tracking connection state
(the `conntrack` module in Linux) allows "allow established
connections" as a single rule that handles all return
traffic for all services. This dramatically simplifies
rule management and reduces misconfiguration risk.

**Level 5 - Mastery (distinguished engineer):**
Modern Linux networking uses nftables (replacing iptables)
with a unified framework for packet classification.
eBPF-based firewalls (XDP/TC hooks) bypass the kernel
networking stack entirely, processing packets at NIC
driver level for microsecond-latency filtering. Cilium
(Kubernetes CNI) uses eBPF to implement L3-L7 network
policies with near-zero overhead. Traditional iptables
requires a kernel context switch per packet; XDP processes
in NIC driver before even reaching the kernel.

---

### ⚙️ How It Works (Mechanism)

**Linux iptables (traditional approach):**

```bash
# View current rules
sudo iptables -L INPUT -n -v --line-numbers

# Default deny INPUT policy
sudo iptables -P INPUT DROP

# Allow established connections (stateful)
sudo iptables -A INPUT -m state \
  --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow SSH from specific IP range only
sudo iptables -A INPUT -p tcp --dport 22 \
  -s 10.0.0.0/8 -j ACCEPT

# Allow HTTPS from anywhere
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow HTTP (redirect to HTTPS handled by app)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Allow ICMP (ping) - do NOT block all ICMP
# (blocking ICMP type 3/4 breaks PMTUD)
sudo iptables -A INPUT -p icmp \
  --icmp-type echo-request -j ACCEPT

# DROP everything else (already handled by default policy)
# Explicit reject gives better error messages:
sudo iptables -A INPUT -j REJECT \
  --reject-with icmp-port-unreachable
```

**AWS Security Group (cloud approach):**

```bash
# Via AWS CLI - add HTTPS inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Add SSH from specific IP only
aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.5/32   # Your IP only
```

---

### 🔄 The Complete Picture - End-to-End Flow

**What "connection refused" vs "connection timeout" tells you:**

```
┌──────────────────────────────────────────────────────────┐
│  Diagnosing Firewall vs Application Issues               │
├──────────────────┬───────────────────────────────────────┤
│  Error           │  Meaning                              │
├──────────────────┼───────────────────────────────────────┤
│  Connection      │  TCP RST received. The packet         │
│  refused         │  reached the host and the OS          │
│                  │  rejected it. Causes:                 │
│                  │  - No process listening on port       │
│                  │  - iptables REJECT rule               │
│                  │  - App bound to 127.0.0.1 only        │
├──────────────────┼───────────────────────────────────────┤
│  Connection      │  No response to SYN. Packet was       │
│  timeout         │  dropped silently. Causes:            │
│                  │  - iptables DROP rule                 │
│                  │  - AWS security group blocking        │
│                  │  - Host is unreachable (offline)      │
│                  │  - Routing loop/black hole            │
└──────────────────┴───────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At 1 million connections/second, stateful firewall
connection tracking table fills up. Linux `conntrack`
default max entries: 65,536 (can be increased). When the
table is full, new connections are dropped. On cloud load
balancers, this causes intermittent connection failures
under high load. Solution: tune `nf_conntrack_max`, or
use eBPF-based firewalls (Cilium) that don't use conntrack.

---

### ⚖️ Comparison Table

| Firewall Type | OSI Layer | State | Performance | Use Case |
|---|---|---|---|---|
| Packet filter (iptables) | L3-L4 | Stateless | Very fast | Server-level rules |
| Stateful inspection | L3-L4 | Stateful | Fast | Enterprise FW |
| WAF (L7) | L7 | Stateful | Slower | Web app protection |
| AWS Security Group | L3-L4 | Stateful | Cloud-managed | EC2 instances |
| AWS NACL | L3-L4 | Stateless | Cloud-managed | Subnet-level |
| eBPF (Cilium) | L3-L7 | Stateful | Near-zero overhead | Kubernetes |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Blocking all ICMP improves security | Blocking ICMP types 3 and 4 (Destination Unreachable, Fragmentation Needed) breaks Path MTU Discovery, causing mysterious large-packet failures. Only block ICMP echo (ping) if necessary. Never block all ICMP. |
| Firewall rules protect from all attacks | Firewalls control network access but do NOT protect against application vulnerabilities (SQL injection, buffer overflow), misconfigured applications, or attacks through allowed ports (HTTP/HTTPS = always open). |
| Default-allow is "fine for dev" | Default-allow in development creates habits that leak into production. The number of data breaches from "this was a dev server but..." is substantial. Use default-deny everywhere. |

---

### 🚨 Failure Modes & Diagnosis

**Firewall Rule Blocks Legitimate Traffic**

**Symptom:** A new service deployed to production cannot
be reached from outside. The service works locally but
external clients get timeout.

**Diagnostic Command / Tool:**
```bash
# From outside: determine if DROP or REJECT
curl -v --connect-timeout 5 http://target:8080
# Timeout = DROP or host unreachable
# "Connection refused" = no rule blocking, no process

# From target machine: is the service listening?
ss -lntp | grep :8080
# If not listed: service not started or wrong port

# Is firewall blocking?
sudo iptables -L INPUT -n -v | grep 8080
# or
sudo nft list ruleset | grep 8080

# Check if packet arrives at all
sudo tcpdump -i any port 8080 -c 5
# If no packets appear: dropped before this machine
# If packets appear with no response: process issue
```

**Fix:** Add firewall rule to allow port 8080 from the
appropriate source range. Never add `0.0.0.0/0` for
internal services - use the specific source CIDR.

**Prevention:** Infrastructure-as-code (Terraform/CDK)
for security group rules. Automated testing that verifies
required ports are open (and closed ports are closed) as
part of deployment pipeline.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - source/destination IP used in firewall rules
- `Port Number` - source/destination ports for L4 rules
- `Packet Structure` - what firewalls actually inspect

**Builds On This (learn these next):**
- `Network Segmentation and Firewall Rules` - production
  design patterns for multi-tier firewall architecture
- `DDoS Attack Types and Mitigations` - how firewalls fit
  into DDoS defense (and their limits)
- `Network Compliance - PCI-DSS Segmentation` - regulatory
  requirements for firewall configuration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRINCIPLE    │ Default deny. Allow only what's needed.   │
│              │ Least privilege at the network layer.     │
├──────────────┼───────────────────────────────────────────┤
│ TYPES        │ Stateless(L4 only), Stateful(tracks TCP), │
│              │ L7/WAF (HTTP content inspection)          │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Always allow ESTABLISHED,RELATED          │
│              │ (stateful return traffic)                 │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ Timeout = DROP. Refused = REJECT/no-app. │
│              │ tcpdump to confirm packets arrive.        │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Block all ICMP (breaks PMTUD).            │
│              │ Allow 0.0.0.0/0 to internal services.    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Timeout = dropped. Refused = rejected.   │
│              │  Check tcpdump to see if packets arrive." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Network Segmentation → iptables deep dive │
│              │ → eBPF/Cilium for Kubernetes              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Default deny: block everything, then allow only needed.
   `Connection refused` = REJECT or no process. `Timeout` =
   DROP or host unreachable.
2. Allow ESTABLISHED,RELATED for stateful return traffic.
   Without this one rule, every response gets dropped.
3. NEVER block ICMP types 3 and 4. Only block echo (ping)
   if required. Blocking all ICMP breaks large-packet
   delivery (PMTUD).

**Interview one-liner:**
"A firewall controls traffic based on rules. Stateless
firewalls filter individual packets by IP/port/protocol.
Stateful firewalls track connection state (conntrack) and
allow return traffic automatically. Layer 7 WAFs inspect
HTTP content. The fundamental principle is default-deny:
allow only what is explicitly needed. In Linux, iptables/
nftables implements this. In AWS, Security Groups are
stateful, NACLs are stateless. 'Connection refused' means
REJECT or no listening process; timeout means DROP."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Default-deny with explicit allow is the safest security
posture for any access control system. The burden is on
defining what is permitted, not what is blocked. The same
principle: Unix file permissions (no access by default),
IAM policies (deny by default), OAuth scopes (no access
without explicit grant), Kubernetes RBAC (no permissions
by default).

---

### 💡 The Surprising Truth

The iptables command most engineers think is "standard"
(`iptables -A INPUT -j ACCEPT`) is actually dangerous.
The `-A` appends to the chain, which means the rule is
added AFTER the default drop policy. But if the default
policy is ACCEPT (not DROP), the rule does nothing useful.
Many tutorial firewall configurations add rules in the
wrong order or with the wrong default policy. The most
dangerous firewall configuration is one that looks correct
but has a subtle ordering error that leaves a security
gap. Always verify with `iptables -L -n --line-numbers`
after changes, and test from OUTSIDE the host.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between stateless and stateful
   firewalls and why "ESTABLISHED,RELATED" is needed.
2. **DEBUG** a "connection timed out" vs "connection refused"
   by using `tcpdump` to determine if packets arrive at the
   host.
3. **DECIDE** the correct iptables ruleset for a server
   exposing HTTPS publicly and SSH to internal-only.
4. **BUILD** the mental model of rule evaluation order and
   predict what happens when a new rule conflicts with
   an existing one.
5. **EXTEND** the firewall concept to explain AWS security
   groups (stateful, no explicit allow for return traffic
   needed) vs NACLs (stateless, need both inbound and
   outbound rules).

---

### 🧠 Think About This Before We Continue

**Q1.** A developer needs to debug a production server and
temporarily opens SSH port 22 to `0.0.0.0/0` in the security
group. They forget to close it. Two weeks later, the server
shows unusual CPU activity. What likely happened? What
automated controls could have prevented or detected this?

*Hint: SSH port 22 open to the internet is scanned within
minutes. Automated brute-force tools exist. How fast would
you notice? What monitoring would catch it?*

**Q2.** Your application receives HTTP requests that should
be proxied to a backend database. You have an L4 stateful
firewall blocking direct access to the database. An attacker
sends HTTP requests to your web server that cause it to
issue database queries the attacker controls (SQL injection).
Does the firewall stop this attack? What type of firewall
would, and how?

*Hint: The L4 firewall sees ALLOW: web server IP → DB
port 3306. The attack goes through the application, not
through the firewall. The firewall is "correct" but useless.*

**Q3.** [Hands-On] Run `sudo iptables -L INPUT -n -v` and
`sudo iptables -L OUTPUT -n -v`. Does your machine have a
default-deny policy? What rules exist? Now add a temporary
REJECT rule for ICMP echo requests:
`sudo iptables -A INPUT -p icmp --icmp-type 8 -j REJECT`.
Test with `ping -c 3 127.0.0.1`. Then remove the rule:
`sudo iptables -D INPUT -p icmp --icmp-type 8 -j REJECT`.
What was the effect? What ICMP type is echo reply (the
response to ping)?