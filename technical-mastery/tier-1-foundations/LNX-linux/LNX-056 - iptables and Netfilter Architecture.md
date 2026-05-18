---
id: LNX-056
title: "iptables and Netfilter Architecture"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-026, LNX-027
used_by: LNX-057, LNX-071, LNX-092
related: LNX-057, LNX-055, LNX-027
tags: [iptables, netfilter, firewall, NAT, conntrack, nftables, PREROUTING, POSTROUTING, iptables-save]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/lnx/iptables-netfilter-architecture/
---

## TL;DR

Netfilter is the Linux kernel's packet filtering framework. iptables is the
userspace tool to configure it. Architecture: 5 hooks in the network stack
(PREROUTING, INPUT, FORWARD, OUTPUT, POSTROUTING) -> 4 tables (filter for
allow/deny, nat for address translation, mangle for packet modification, raw
for conntrack bypass) -> chains (ordered lists of rules) -> targets
(-j ACCEPT/DROP/REJECT/MASQUERADE/SNAT/DNAT). Connection tracking (conntrack)
maintains state for `--state RELATED,ESTABLISHED`. nftables is the modern
replacement. Key commands: `iptables -L -v -n --line-numbers`, `iptables -A`,
`iptables-save`/`iptables-restore`, `conntrack -L`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-056 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | iptables, netfilter, firewall, NAT, conntrack, nftables, chains, tables, hooks |
| **Prerequisites** | LNX-026 (networking), LNX-027 (TCP/IP) |

---

### The Problem This Solves

**Problem 1**: A server hosts a public web app on port 80 but needs to
block all other inbound traffic. iptables solution: accept ESTABLISHED/
RELATED (return traffic), accept port 80, drop everything else. Stateful
because conntrack tracks TCP state - no need to explicitly allow return
traffic.

**Problem 2**: A NAT gateway allows a private subnet (192.168.1.0/24) to
access the internet through a single public IP. iptables MASQUERADE rule
in POSTROUTING chain rewrites source addresses of outbound packets to the
gateway's public IP, and conntrack automatically handles the reverse translation
for reply packets.

---

### Textbook Definition

**Netfilter**: Linux kernel framework with hooks at 5 points in the packet
path. Modules (iptables, nftables, ipset, conntrack) attach functions to
these hooks to inspect or modify packets.

**iptables**: Userspace tool for configuring Netfilter. Manages rules in
tables. Each table has chains (hook attachment points plus user-defined
chains). Each chain has rules evaluated top-to-bottom; the first matching
rule's target action is applied.

**Tables (processing order):** raw -> mangle -> nat -> filter
- **filter**: Allow, deny, reject packets (default table). Chains: INPUT, FORWARD, OUTPUT.
- **nat**: Network Address Translation. Chains: PREROUTING (DNAT), POSTROUTING (SNAT/MASQUERADE).
- **mangle**: Modify packet headers (TTL, TOS, MARK). All 5 chains.
- **raw**: Bypass conntrack (`-j NOTRACK`). Chains: PREROUTING, OUTPUT.

**Hooks (packet path through kernel):**
- `PREROUTING`: Before routing decision. DNAT here (port forwarding).
- `INPUT`: For locally-destined packets.
- `FORWARD`: For packets being routed through this host.
- `OUTPUT`: For locally-generated packets.
- `POSTROUTING`: After routing. SNAT/MASQUERADE here.

**Connection tracking (conntrack)**: Maintains a table of active connections
with state (NEW, ESTABLISHED, RELATED, INVALID). Enables stateful firewalling.
`/proc/net/nf_conntrack` lists active connections.

---

### Understand It in 30 Seconds

```bash
# === View current rules ===
iptables -L                       # filter table, all chains
iptables -L -v -n --line-numbers  # verbose, numeric (no DNS), with line#
iptables -t nat -L -v -n          # nat table
iptables -t mangle -L -v -n       # mangle table

# === Basic server firewall (whitelist approach) ===
# Allow loopback:
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections (stateful):
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow specific services:
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS

# Default deny (DROP is silent, REJECT sends TCP reset/ICMP):
iptables -P INPUT DROP
iptables -P FORWARD DROP
# OUTPUT typically stays ACCEPT unless strict control needed

# Allow ICMP (ping) with rate limit:
iptables -A INPUT -p icmp --icmp-type echo-request -m limit \
    --limit 10/second -j ACCEPT

# === NAT - outbound masquerade (internet sharing) ===
# Enable IP forwarding first:
echo 1 > /proc/sys/net/ipv4/ip_forward

# MASQUERADE: use the interface's current IP (good for dynamic IPs):
iptables -t nat -A POSTROUTING \
    -s 192.168.1.0/24 -o eth0 -j MASQUERADE

# SNAT: use a specific fixed IP (better performance than MASQUERADE):
iptables -t nat -A POSTROUTING \
    -s 192.168.1.0/24 -o eth0 -j SNAT --to-source 203.0.113.5

# === Port forwarding (DNAT) ===
# Forward external port 8080 to internal server:
iptables -t nat -A PREROUTING \
    -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.100:80

# Also need FORWARD rule if routing to another host:
iptables -A FORWARD -p tcp -d 192.168.1.100 --dport 80 \
    -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT

# === Delete rules ===
iptables -D INPUT -p tcp --dport 8080 -j ACCEPT  # by specification
iptables -D INPUT 3                               # by line number
iptables -F INPUT                                 # flush all in chain
iptables -F                                       # flush all chains (filter)
iptables -t nat -F                                # flush nat table

# === Save and restore (persistence) ===
iptables-save > /etc/iptables/rules.v4    # save
iptables-restore < /etc/iptables/rules.v4 # restore

# On Debian/Ubuntu: install iptables-persistent
# Rules loaded at boot via /etc/iptables/rules.v4

# On RHEL/CentOS: use firewalld (nftables backend) or:
service iptables save   # saves to /etc/sysconfig/iptables

# === Connection tracking ===
conntrack -L                    # list current connections
conntrack -L | wc -l            # count connections
cat /proc/net/nf_conntrack      # raw conntrack table
sysctl net.netfilter.nf_conntrack_max  # max connections (default 65536)

# Conntrack table full symptom: "nf_conntrack: table full, dropping packet"
# Fix:
sysctl -w net.netfilter.nf_conntrack_max=524288
```

---

### First Principles

**Packet flow through Netfilter hooks:**
```
Incoming packet from wire:
                |
                v
        [PREROUTING hook]
          raw:PREROUTING
          mangle:PREROUTING
          nat:PREROUTING  <- DNAT (port forwarding) happens here
                |
          Routing decision
         /              \
(for this host)        (forward to another host)
        |                         |
   [INPUT hook]           [FORWARD hook]
    mangle:INPUT           mangle:FORWARD
    filter:INPUT           filter:FORWARD
        |                         |
   Local process            [POSTROUTING hook]
        |                    mangle:POSTROUTING
        v                    nat:POSTROUTING  <- SNAT/MASQUERADE
   Local process                  |
   generates reply           Out on wire
        |
   [OUTPUT hook]
    raw:OUTPUT
    mangle:OUTPUT
    nat:OUTPUT
    filter:OUTPUT
        |
   [POSTROUTING hook]
    mangle:POSTROUTING
    nat:POSTROUTING  <- SNAT/MASQUERADE
        |
    Out on wire
```

**NAT mechanics (MASQUERADE example):**
```
Private network: 192.168.1.100 wants to reach 8.8.8.8:53

ORIGINAL PACKET:
  src: 192.168.1.100:45678 -> dst: 8.8.8.8:53

POSTROUTING MASQUERADE rule fires:
  - Rewrites src to public IP: 203.0.113.5:45678
  - conntrack entry created:
    src=192.168.1.100:45678, dst=8.8.8.8:53
    -> mapped to 203.0.113.5:45678

TRANSLATED PACKET leaves:
  src: 203.0.113.5:45678 -> dst: 8.8.8.8:53

REPLY from 8.8.8.8:53:
  src: 8.8.8.8:53 -> dst: 203.0.113.5:45678

PREROUTING conntrack lookup:
  Finds entry: 203.0.113.5:45678 = 192.168.1.100:45678
  Rewrites dst: 192.168.1.100:45678

PACKET delivered to private host:
  src: 8.8.8.8:53 -> dst: 192.168.1.100:45678
```

---

### Thought Experiment

Building a complete server firewall from scratch:

```bash
#!/bin/bash
# server-firewall.sh: complete stateful server firewall

set -e

IPT="iptables"

echo "=== Flushing existing rules ==="
$IPT -F
$IPT -X
$IPT -t nat -F
$IPT -t nat -X
$IPT -t mangle -F
$IPT -t mangle -X

echo "=== Setting default policies ==="
$IPT -P INPUT DROP
$IPT -P FORWARD DROP
$IPT -P OUTPUT ACCEPT  # allow all outbound

echo "=== Loopback (always allow) ==="
$IPT -A INPUT -i lo -j ACCEPT
$IPT -A OUTPUT -o lo -j ACCEPT

echo "=== Stateful: allow established connections ==="
$IPT -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "=== SSH (with rate limiting vs brute force) ==="
$IPT -A INPUT -p tcp --dport 22 \
    -m conntrack --ctstate NEW \
    -m limit --limit 3/minute --limit-burst 5 \
    -j ACCEPT
$IPT -A INPUT -p tcp --dport 22 \
    -m conntrack --ctstate NEW \
    -j LOG --log-prefix "SSH-RATELIMIT: " --log-level 6
$IPT -A INPUT -p tcp --dport 22 \
    -m conntrack --ctstate NEW -j DROP

echo "=== Web services ==="
$IPT -A INPUT -p tcp --dport 80 -j ACCEPT
$IPT -A INPUT -p tcp --dport 443 -j ACCEPT

echo "=== ICMP (rate-limited) ==="
$IPT -A INPUT -p icmp --icmp-type echo-request \
    -m limit --limit 10/second --limit-burst 20 -j ACCEPT

echo "=== Log and drop everything else ==="
$IPT -A INPUT -j LOG --log-prefix "INPUT-DROP: " --log-level 6
$IPT -A INPUT -j DROP

echo "=== Save rules ==="
iptables-save > /etc/iptables/rules.v4

echo "=== Verify ==="
$IPT -L -v -n --line-numbers

echo "Done: firewall configured."
```

---

### Mental Model / Analogy

```
Netfilter = a series of security checkpoints at a border crossing

5 Checkpoints (hooks):
  PREROUTING = customs on arrival (before deciding destination)
  INPUT = passport control for local travelers (to this country)
  FORWARD = transit lounge inspection (passing through to another country)
  OUTPUT = departure check (from local travelers leaving)
  POSTROUTING = last check before boarding the plane (after routing)

4 Rule Books (tables) - each checkpoint uses them in order:
  RAW rules (checked first): "Do you even need to track this traveler?"
  MANGLE rules: "Change something about this traveler's paperwork"
  NAT rules: "Change this traveler's address/identity"
  FILTER rules (last): "Allow or deny this traveler"

Stateful inspection (conntrack):
  Once a traveler enters with valid papers (NEW -> ESTABLISHED),
  they and their companions (RELATED) get a pass:
  They can come and go without checking papers again
  (ESTABLISHED,RELATED rule early in INPUT chain)

MASQUERADE = corporate front desk:
  Everyone leaving says they're from "Corp HQ" (public IP)
  Receptionist (conntrack) tracks who is really who inside
  When reply arrives addressed to "Corp HQ", receptionist
  delivers it to the right internal person

DROP vs REJECT:
  DROP = bouncer ignores you (connection times out after 30-60s)
  REJECT = bouncer says "No, go away" (immediate TCP reset/ICMP unreachable)
  Use REJECT for interactive services (better user experience)
  Use DROP for scanners/attackers (waste their time)
```

---

### Gradual Depth - Five Levels

**Level 1:**
iptables has 3 main tables (filter, nat, mangle), 3 main chains in filter
(INPUT, FORWARD, OUTPUT). `-j ACCEPT/DROP/REJECT`. Default policies. Basic
server rules: accept loopback, accept ESTABLISHED, accept specific ports,
default DROP. `iptables-save`/`restore` for persistence.

**Level 2:**
NAT with MASQUERADE and SNAT/DNAT. Port forwarding pattern (PREROUTING DNAT
+ FORWARD). Conntrack states (NEW, ESTABLISHED, RELATED, INVALID). Rate
limiting with `-m limit`. Logging with `-j LOG`. User-defined chains for
organization. `ipset` for efficient IP set matching (better than many -s
rules). nftables basics.

**Level 3:**
`-m multiport` for matching multiple ports in one rule. `-m string` for
payload matching. `-m mark` and MARK target for traffic marking (used with
tc for QoS). `--set-mark` and policy routing. `ip rule` + `ip route` tables
for mark-based routing. Connection tracking zones (for multiple NAT scenarios).
`-j REDIRECT` for transparent proxying. iptables-extensions.

**Level 4:**
Kubernetes networking: kube-proxy uses iptables (or IPVS) rules for
Service load balancing. Every Kubernetes Service generates iptables rules
in the filter and nat tables. Visualize: `iptables-save | wc -l` (can reach
10,000+ rules in large clusters). IPVS mode: replaces iptables with kernel
IP Virtual Server for better performance at scale. Docker networking: creates
DOCKER chain in filter table, DOCKER-POSTROUTING in nat. Container network
isolation via FORWARD chain rules and conntrack. nftables' advantages over
iptables: atomic rule updates, sets/maps for efficient multi-value matching.

**Level 5:**
Netfilter vs XDP: iptables/Netfilter hooks are deep in the stack (after
sk_buff allocation, after NAPI). For high-PPS filtering, this is late.
XDP (eXpress Data Path) filters BEFORE sk_buff allocation - much lower
overhead. eBPF programs can be attached to Netfilter hooks too (`nf_tables`
with eBPF). `flowtable` (nftables feature): hardware or software accelerated
fast-path for established flows - bypasses most of nftables for matching flows.
`nf_tables` architecture: same hooks but rules are bytecode evaluated by
a JIT-compiled virtual machine in the kernel. Security: Netfilter bypass
via IPv6 extension header vulnerabilities, conntrack exhaustion attacks
(SYN flood filling the conntrack table).

---

### Code Example

**BAD - common iptables mistakes:**
```bash
# BAD 1: Default ACCEPT policies with no DROP at end:
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
# No default DROP! Everything else is also ACCEPTED
# Because: default policy is ACCEPT if not changed

# GOOD: either set default policy to DROP, or add explicit DROP at end:
iptables -P INPUT DROP     # change default policy
# OR:
iptables -A INPUT -j DROP  # explicit drop at end (if policy stays ACCEPT)

# BAD 2: No ESTABLISHED rule (breaks outbound connections):
iptables -P INPUT DROP
# Can't SSH out and have reply come back!
# All established return traffic is also dropped!

# GOOD: Always add ESTABLISHED rule FIRST:
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
# Then add specific NEW connection rules below

# BAD 3: Forgetting to allow SSH before dropping INPUT:
iptables -P INPUT DROP
# Now you've locked yourself out if running on a remote server!

# GOOD: Test in order, SSH rule before default drop, and use:
# iptables-apply (auto-reverts if you lose connectivity)
iptables-apply /etc/iptables/new-rules.v4  # reverts after 30s unless confirmed

# BAD 4: DNAT without FORWARD rule:
iptables -t nat -A PREROUTING -p tcp --dport 8080 \
    -j DNAT --to-destination 192.168.1.100:80
# Port forwarding doesn't work! The FORWARD chain is DEFAULT DROP!

# GOOD: Add both NAT rule AND FORWARD rule:
iptables -t nat -A PREROUTING -p tcp --dport 8080 \
    -j DNAT --to-destination 192.168.1.100:80
iptables -A FORWARD -p tcp -d 192.168.1.100 --dport 80 \
    -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
```

**GOOD - nftables equivalent (modern Linux):**
```bash
# nftables: atomic, human-readable, single tool for all Netfilter tables

# Equivalent to the server firewall above, using nftables:
nft add table inet filter

nft add chain inet filter input \
    { type filter hook input priority 0 \; policy drop \; }

nft add rule inet filter input iif lo accept
nft add rule inet filter input ct state established,related accept
nft add rule inet filter input tcp dport 22 \
    ct state new limit rate 3/minute accept
nft add rule inet filter input tcp dport { 80, 443 } accept
nft add rule inet filter input icmp type echo-request \
    limit rate 10/second accept
nft add rule inet filter input log prefix "INPUT-DROP: " drop

# Save and restore:
nft list ruleset > /etc/nftables.conf
nft -f /etc/nftables.conf

# Show current ruleset:
nft list ruleset
```

---

### Comparison Table

| Feature | iptables | nftables |
|---------|---------|---------|
| **Rule updates** | One rule at a time (non-atomic) | Atomic batch updates |
| **Multiple tables/families** | Separate ip6tables, ebtables | Single tool, all families |
| **Sets/maps** | Requires ipset (separate) | Built-in sets and maps |
| **Performance at scale** | Slow with 1000+ rules (linear scan) | Better (JIT, sets) |
| **Kubernetes** | Default for kube-proxy | Calico, Cilium prefer nftables |
| **Learning curve** | Higher (cryptic syntax) | Moderate (cleaner syntax) |
| **Availability** | All Linux distros | Linux 3.13+, default RHEL 8+ |
| **Docker/K8s compat** | Full | Growing (some tools still iptables) |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "iptables rules are checked in table order (filter, nat, mangle)" | iptables rules within a hook are checked in TABLE priority order (raw -> mangle -> nat -> filter), but different tables attach to different hooks. The filter table's INPUT chain only applies to packets destined for the local host (after routing). The nat table's PREROUTING applies BEFORE routing. You can't put DNAT rules in the filter table - they belong in the nat table because DNAT must happen before routing (PREROUTING) to affect the routing decision. |
| "DROP in INPUT chain stops all packet processing" | DROP only applies to the packet at that chain and table. The packet is silently discarded. But RELATED traffic from conntrack uses a separate mechanism - conntrack can mark a packet as RELATED even before the filter table sees it. Also, ICMP error messages for dropped packets are NOT automatically sent (unlike REJECT). This means applications see connection timeouts (slow) instead of immediate "connection refused" errors. |
| "MASQUERADE and SNAT are equivalent" | MASQUERADE automatically reads the interface's current IP address on each packet, making it slightly slower but essential for dynamic IP addresses (DHCP, dialup, cloud with elastic IPs). SNAT uses a fixed IP specified in the rule (`--to-source X.X.X.X`) and is faster because no interface lookup is needed per packet. For production servers with static IPs, SNAT is preferred. For home routers with dynamic ISP IPs, MASQUERADE is the right choice. |
| "iptables rules persist across reboot" | iptables rules are in-memory only. Reboot = all rules gone. Persistence requires: Ubuntu/Debian: `apt install iptables-persistent` + `netfilter-persistent save`. RHEL/CentOS with iptables service: `service iptables save`. Or write rules to a file and add `iptables-restore` to a boot script. Many modern systems use firewalld (a frontend to nftables/iptables) which automatically persists rules. |
| "The FORWARD chain handles packets going to other processes on the same host" | No. FORWARD handles packets TRANSITING through the host (received on one interface, to be sent out another). Packets from the network to local processes use INPUT. Packets from local processes to the network use OUTPUT. FORWARD only applies when the host is acting as a router, container host, or VPN gateway - i.e., when IP forwarding is enabled (`net.ipv4.ip_forward=1`). This is why container hosts (Docker, Kubernetes) need FORWARD rules. |

---

### Failure Modes & Diagnosis

**Conntrack table full (packet drops under load):**
```bash
# Symptom: intermittent connection failures, kernel log shows:
# "nf_conntrack: table full, dropping packet"

dmesg | grep conntrack
# [12345.678] nf_conntrack: table full, dropping packet

# Check current count vs max:
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max

# If count approaching max - increase max:
sysctl -w net.netfilter.nf_conntrack_max=524288
# Persist: echo "net.netfilter.nf_conntrack_max=524288" >> /etc/sysctl.conf

# Also: reduce timeout for TIME_WAIT connections:
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_time_wait=30  # default 120s
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_close_wait=30

# Find what's filling the table:
conntrack -L | awk '{print $4}' | sort | uniq -c | sort -rn | head -10
# Lots of TIME_WAIT: old connections not expiring quickly enough
# Lots of SYN_SENT: possible SYN flood -> increase max or add SYN cookies

# SYN flood protection via SYN cookies (bypasses conntrack):
sysctl -w net.ipv4.tcp_syncookies=1
```

---

### Related Keywords

**Foundational:**
LNX-026 (Networking Basics), LNX-027 (TCP/IP), LNX-055 (Network Stack)

**Builds on this:**
LNX-057 (Security Hardening), LNX-071 (Namespaces), LNX-092 (Network Namespaces)

**Related:**
LNX-084 (Network Performance)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `iptables -L -v -n --line-numbers` | List rules verbose/numeric |
| `iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT` | Allow established |
| `iptables -P INPUT DROP` | Set default policy to DROP |
| `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` | Enable NAT |
| `iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-dest IP:PORT` | Port forward |
| `iptables-save > /etc/iptables/rules.v4` | Save rules |
| `conntrack -L \| wc -l` | Count tracked connections |
| `sysctl net.netfilter.nf_conntrack_max` | Max connections |

**3 things to remember:**
1. Add ESTABLISHED,RELATED rule FIRST in INPUT chain - or established return traffic is blocked
2. DNAT (port forwarding) goes in PREROUTING, SNAT/MASQUERADE in POSTROUTING - not the filter table
3. iptables rules are NOT persistent by default - save with `iptables-save` or use firewalld/nftables

---

### Transferable Wisdom

iptables concepts appear in: Docker creates rules in the DOCKER chain (in
the filter table) for container port mapping, and DOCKER-POSTROUTING (in
nat table) for container internet access. Understanding iptables is essential
for debugging Docker networking. Kubernetes kube-proxy creates thousands of
iptables rules for Service load balancing - each Service/EndpointSlice gets
a probability-based chain (`KUBE-SVC-*`). AWS Security Groups and NACLs are
cloud-abstracted versions of stateful (conntrack-like) and stateless
(iptables-like without conntrack) filtering. The concept of "hook points in
a processing pipeline" appears in web frameworks (middleware chains), API
gateways (filter chains), and service meshes (Envoy filter chains).

---

### The Surprising Truth

The `--ctstate ESTABLISHED,RELATED` match in iptables is the most important
single rule in any stateful firewall - yet it's the one most beginners forget
to add. Without it, you can outbound-connect to a server but the REPLY packets
are blocked by your INPUT DROP policy. The connection appears to hang. The
reason this rule is needed is that TCP is duplex: you initiate a connection
(OUTPUT is ACCEPT), the server's reply comes IN (via INPUT, which is DROP).
The conntrack module tracks that this INCOMING packet is the REPLY to your
OUTGOING connection (state = ESTABLISHED) and the `ESTABLISHED,RELATED` rule
permits it. The same mechanism handles FTP's data channel (RELATED to the
control channel), SIP media streams, ICMP error messages for existing
connections, etc. "Connection tracking" is the only thing that makes
`--ctstate ESTABLISHED,RELATED` work - this is why `nf_conntrack` module
must be loaded for a stateful firewall. The surprising part: conntrack
was originally considered a performance anti-pattern (table lookup per
packet, memory overhead). But the alternative - stateless firewalls that
need explicit rules for return traffic - generates O(n^2) rules that are
unmaintainable. Conntrack won, and today even high-throughput 100Gbps
firewalls use conntrack with hardware offload via flowtable.

---

### Mastery Checklist

- [ ] Understands the 5 Netfilter hooks and which table goes in which hook
- [ ] Can write a complete stateful server firewall (loopback, ESTABLISHED, service ports, default DROP)
- [ ] Can configure NAT masquerade for outbound internet sharing
- [ ] Can configure DNAT port forwarding and the required FORWARD rule
- [ ] Understands conntrack table exhaustion and how to diagnose/fix it

---

### Think About This

1. You set up a server with `iptables -P INPUT DROP` and added rules to
   allow SSH (port 22), HTTP (80), HTTPS (443), and ESTABLISHED,RELATED
   traffic. Your web application needs to make outbound API calls to
   external services. Will it work? Why or why not? If the application
   also needed to receive callbacks from the external service on port 8080,
   what additional rule(s) would you need?

2. A web server needs port forwarding: external clients connect to port 80
   on the gateway (203.0.113.1), and traffic must be forwarded to an internal
   web server at 10.0.0.5:80. The gateway has two interfaces: eth0 (external,
   203.0.113.1) and eth1 (internal). Write the complete set of iptables rules
   needed (PREROUTING DNAT, FORWARD rules, and any prerequisite settings).

3. A Kubernetes cluster has a node with 50,000+ iptables rules generated
   by kube-proxy for 2,000 Services. Performance testing shows new connections
   are slow. Why does the number of iptables rules directly impact new
   connection performance? What is the O(n) element? How would switching
   to IPVS mode solve this, and what does IPVS do differently?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain how iptables NAT (MASQUERADE) enables internet access for a private subnet.
A: MASQUERADE is Source NAT - it rewrites the source IP of outgoing packets so they appear to come from the gateway's public IP. The mechanism: (1) Enable IP forwarding: `echo 1 > /proc/sys/net/ipv4/ip_forward` (otherwise the kernel won't route between interfaces). (2) Add MASQUERADE rule: `iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE`. This says: for packets FROM the private subnet, going OUT eth0, replace the source IP with eth0's current IP. (3) Connection tracking (conntrack) is essential: when the NAT rewrite happens, conntrack records: "packet from 192.168.1.100:45678 to 8.8.8.8:53 was rewritten to 203.0.113.1:45678". (4) When the REPLY arrives (8.8.8.8:53 -> 203.0.113.1:45678): conntrack looks up the reverse mapping, rewrites the destination back to 192.168.1.100:45678, and the kernel routes it to the private host. MASQUERADE vs SNAT: MASQUERADE dynamically reads eth0's IP on every packet (for DHCP/dynamic IPs). SNAT specifies the IP explicitly (`--to-source 203.0.113.1`) and is faster for static IPs. The FORWARD chain must allow the traffic: `iptables -A FORWARD -s 192.168.1.0/24 -j ACCEPT`. Without this, the FORWARD chain's default policy (often DROP) would drop the routed packets before they reach POSTROUTING.

**Expert:**
Q: How does Docker networking use iptables, and what happens when you run `docker run -p 8080:80`?
A: Docker uses iptables extensively for container networking. Structure: (1) DOCKER chain in filter table: Docker creates a custom DOCKER chain and inserts it into FORWARD. Rules in DOCKER allow specific container-to-host and inter-container traffic. (2) DOCKER chain in nat table: For port publishing (`-p 8080:80`). Docker adds a DNAT rule in PREROUTING: any packet arriving on port 8080 is DNAT'd to the container's internal IP (e.g., 172.17.0.2) port 80. (3) DOCKER-POSTROUTING: Handles MASQUERADE for outbound container traffic (172.17.0.0/16 source -> MASQUERADE on eth0). What `docker run -p 8080:80` adds: `iptables -t nat -A DOCKER ! -i docker0 -p tcp -m tcp --dport 8080 -j DNAT --to-destination 172.17.0.2:80`. Plus: `iptables -A DOCKER -d 172.17.0.2/32 ! -i docker0 -o docker0 -p tcp -m tcp --dport 80 -j ACCEPT`. The `! -i docker0` means "not coming FROM the docker0 bridge" (to avoid double-NAT for container-to-container). Practical implications: (a) docker0 bridge interface is the default gateway for containers. (b) `iptables -F` (flush all rules) breaks Docker networking - containers lose internet access. (c) In Kubernetes, kube-proxy manages thousands of these rules for Services. (d) iptables-based k8s doesn't scale well past ~1000 services: each new connection must traverse a probabilistic chain of rules (KUBE-SVC-* -> random jump to KUBE-SEP-*). IPVS mode uses kernel's load balancer for O(1) service lookup.
