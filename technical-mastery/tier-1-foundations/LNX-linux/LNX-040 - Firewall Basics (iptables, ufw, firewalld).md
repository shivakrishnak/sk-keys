---
id: LNX-040
title: "Firewall Basics (iptables, ufw, firewalld)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-023, NET-001
used_by: LNX-056, LNX-057
related: LNX-056, NET-001, SEC-001
tags: [iptables, ufw, firewalld, nftables, firewall, packet-filter, INPUT, OUTPUT, FORWARD]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/lnx/firewall-basics/
---

## TL;DR

Linux firewalls filter network packets using rules. `iptables` is the
classic tool (uses Netfilter kernel framework). `ufw` (Ubuntu) and
`firewall-cmd` (RHEL/CentOS) are friendlier wrappers. Key chains:
INPUT (traffic to this host), OUTPUT (traffic from this host), FORWARD
(traffic passing through). Default policy matters: ACCEPT = allow all,
DROP = deny all. Production: `ufw allow 22/tcp` to allow SSH, `ufw enable`
to activate. `iptables -L -n -v` to inspect current rules. `nftables` is
the modern kernel replacement for iptables.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-040 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | iptables, ufw, firewalld, nftables, netfilter, chains, packet filtering |
| **Prerequisites** | LNX-023, NET-001 |

---

### The Problem This Solves

You deploy a MySQL server. Port 3306 is open and accessible to the entire
internet. An attacker finds it, brute-forces the default root password,
and owns your database. A firewall rule `iptables -A INPUT -p tcp --dport
3306 -j DROP` (or with ufw: `ufw deny 3306`) would have blocked external
access. Firewall basics are essential for any server hardening.

---

### Textbook Definition

**Netfilter**: The Linux kernel framework that hooks into the network stack
to intercept and filter packets. iptables, nftables, ufw, and firewalld all
use Netfilter as the underlying mechanism.

**iptables**: The classic command-line interface to Netfilter. Uses tables
(filter, nat, mangle, raw) and chains (sequences of rules) to process packets.

**Chain**: A list of firewall rules applied in order to matching packets.
Built-in chains: INPUT (to local process), FORWARD (through this host),
OUTPUT (from local process), PREROUTING (before routing), POSTROUTING
(after routing).

**Rule**: An individual match + action pair. Match criteria: protocol,
source/destination IP, source/destination port. Actions (targets): ACCEPT,
DROP, REJECT, LOG.

**ufw (Uncomplicated Firewall)**: Ubuntu's high-level frontend to iptables.
Simpler syntax for common firewall tasks.

**firewalld**: Red Hat's firewall daemon. Uses zones and services concept.

---

### Understand It in 30 Seconds

```bash
# === iptables (direct, all distros) ===
# List current rules (verbose, numeric - no DNS lookup):
iptables -L -n -v

# Allow SSH (port 22):
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS:
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Block a specific port:
iptables -A INPUT -p tcp --dport 3306 -j DROP

# Allow established connections (essential for return traffic!):
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Set default policy:
iptables -P INPUT DROP      # default: block all INPUT
iptables -P INPUT ACCEPT    # default: allow all INPUT

# Delete a rule:
iptables -D INPUT -p tcp --dport 3306 -j DROP  # delete by spec
iptables -D INPUT 5                              # delete rule #5

# Save rules (persist across reboots - Ubuntu/Debian):
iptables-save > /etc/iptables/rules.v4
apt install iptables-persistent   # auto-restore on boot

# === ufw (Ubuntu's friendly wrapper) ===
ufw status                     # show status and rules
ufw enable                     # activate firewall
ufw disable                    # deactivate

ufw allow 22/tcp               # allow SSH
ufw allow 80/tcp               # allow HTTP
ufw deny 3306/tcp              # deny MySQL
ufw allow from 10.0.0.0/24    # allow from specific subnet
ufw allow from 10.0.0.5 to any port 5432  # specific IP to specific port

ufw delete allow 80/tcp        # remove a rule

# === firewalld (RHEL/CentOS/Fedora) ===
systemctl status firewalld     # check if running
firewall-cmd --state           # running/not running
firewall-cmd --list-all        # show all rules

firewall-cmd --add-service=http --permanent    # allow HTTP
firewall-cmd --add-port=8080/tcp --permanent   # allow port 8080
firewall-cmd --remove-service=http --permanent # deny HTTP
firewall-cmd --reload          # apply permanent changes
```

---

### First Principles

**Packet flow through Netfilter hooks:**
```
Incoming packet:
  [NIC] -> PREROUTING -> [routing decision]
                              |
                    is it for this host?
                    /                   \
                yes                      no (forward)
                  |                        |
               INPUT                   FORWARD -> POSTROUTING -> [NIC]
                  |
         [local process]
                  |
              OUTPUT -> POSTROUTING -> [NIC] -> Outgoing packet

For a web server:
  Browser -> Internet -> NIC -> PREROUTING -> INPUT -> nginx process
  nginx -> OUTPUT -> POSTROUTING -> NIC -> Internet -> Browser

For a router:
  Source -> NIC -> PREROUTING -> FORWARD -> POSTROUTING -> NIC -> Dest

Tables (processed in order for each chain):
  raw      -> connection tracking exemption
  mangle   -> packet modification (TTL, TOS, MARK)
  nat      -> address translation (DNAT/SNAT/MASQUERADE)
  filter   -> the main firewall (ACCEPT/DROP/REJECT)
```

**Rule processing:**
```
Rules are checked TOP TO BOTTOM, first match wins:
Rule 1: -p tcp --dport 22 -j ACCEPT    <- SSH allowed
Rule 2: -p tcp --dport 80 -j ACCEPT    <- HTTP allowed
Rule 3: -j DROP                         <- everything else dropped

IMPORTANT: Order matters!
If you put DROP first: nothing gets through.
If you forget ESTABLISHED,RELATED: return packets blocked,
connections time out even when outbound is allowed.
```

---

### Thought Experiment

Starting from a "block all" policy and building up properly:

```bash
# Start fresh:
iptables -F        # flush all rules
iptables -P INPUT ACCEPT   # temporarily allow all (while we build rules)

# Rule order matters - build carefully:

# 1. Allow loopback (essential - localhost communication):
iptables -A INPUT -i lo -j ACCEPT

# 2. Allow established/related (return traffic for our connections):
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. Allow SSH (before we set default DROP - otherwise we lock ourselves out!):
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 4. Allow web traffic:
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 5. Allow ICMP ping (optional but useful for diagnosis):
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# 6. NOW set default policy to DROP:
iptables -P INPUT DROP

# Verify we're not locked out:
iptables -L -n -v    # can still run this? Good.

# Test from another terminal before saving:
ssh user@this-server "echo 'SSH still works'"

# Save:
iptables-save > /etc/iptables/rules.v4
```

---

### Mental Model / Analogy

```
Netfilter = Security checkpoint at a building
Chains = Different checkpoints (entrance, exit, lobby)
Rules = Guard's instructions (checklist in order)

INPUT chain = Entrance gate (packets trying to enter this host)
OUTPUT chain = Exit gate (packets leaving this host)
FORWARD chain = Transit area (packets passing through like a router)

Each rule:
  Match criteria = "Is this person wearing a blue badge?"
  Target (ACCEPT) = "Let them through"
  Target (DROP) = "Turn them away silently (no response)"
  Target (REJECT) = "Tell them they're not allowed (send rejection)"

First match wins = Security guard stops at first matching rule
Default policy = What happens if no rule matches (ACCEPT or DROP)

ESTABLISHED,RELATED = "If you've already been checked going out,
                       your return packet doesn't need rechecking"

ufw = simplified sign on the door:
  ufw allow 22    = "Badge number 22 is allowed"
  ufw deny 3306   = "Badge number 3306 is not allowed"
  ufw enable      = "Post the guard"
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ufw allow 22/tcp`, `ufw allow 80/tcp`, `ufw enable`, `ufw status`.
For RHEL: `firewall-cmd --add-service=ssh --permanent && firewall-cmd --reload`.
These 4-5 commands cover basic server hardening. Default behavior: everything
on most distros starts with ACCEPT (allow all) unless ufw/firewalld is active.

**Level 2:**
iptables directly: `-A` (append), `-D` (delete), `-L -n -v` (list verbose),
`-P` (default policy). Chain order: INPUT/FORWARD/OUTPUT. `--state
ESTABLISHED,RELATED` for stateful filtering. Flush with `-F`. Source/dest
filtering: `-s 10.0.0.0/24`, `-d 1.2.3.4`. Save/restore: `iptables-save`,
`iptables-restore`.

**Level 3:**
NAT table: `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` (IP
masquerading for shared internet). Port forwarding: `iptables -t nat -A
PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080` (redirect from
port 80 to 8080). Custom chains: `iptables -N MYCHAIN` for reusable rule
sets. Logging: `iptables -A INPUT -j LOG --log-prefix "BLOCKED: "`.
Connection tracking modules: `--state NEW,ESTABLISHED,RELATED,INVALID`.

**Level 4:**
iptables sets (ipset): `ipset create blacklist hash:ip; ipset add blacklist
1.2.3.4; iptables -A INPUT -m set --match-set blacklist src -j DROP`. Much
more efficient than individual IP rules for thousands of IPs. iptables-nft
vs iptables-legacy: modern systems use nft backend even when you run
iptables commands. Rate limiting: `iptables -A INPUT -p tcp --dport 22
-m limit --limit 3/min -j ACCEPT` (brute-force protection on SSH).

**Level 5:**
nftables: the modern replacement. `nft list ruleset`, `nft add rule ip
filter input tcp dport 22 accept`. nftables is more efficient (one table
scan instead of multiple), supports sets and maps natively, has better IPv4/
IPv6 unification. eBPF-based firewalling: XDP programs attached to NIC drivers
for line-rate packet filtering BEFORE the kernel network stack (used in
Cilium, Cloudflare's L3/L4 DDoS mitigation). `tc` (traffic control) with
eBPF for ingress/egress filtering. These approaches process millions of
packets per second without Netfilter overhead.

---

### Code Example

**BAD - firewall configuration mistakes:**
```bash
# BAD 1: Setting DROP policy before allowing SSH (self-lockout!)
iptables -P INPUT DROP    # ALL INPUT now dropped
iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # SSH allowed
# If there's an error in the SSH rule before it's applied:
# You've locked yourself out of the server!

# CORRECT ORDER:
# 1. Add SSH allow rule FIRST
# 2. Then set DROP policy
iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # SSH first!
iptables -P INPUT DROP                          # THEN set policy

# BAD 2: Forgetting ESTABLISHED,RELATED rule
iptables -P INPUT DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# Now: SSH connections work to login
# But after login, DNS lookups, apt updates, curl - all FAIL
# Because return packets are DROPPED (not matching any ACCEPT rule)

# FIX: Allow return traffic:
iptables -I INPUT 1 -m state --state ESTABLISHED,RELATED -j ACCEPT
# -I INPUT 1 = insert at position 1 (check BEFORE other rules)

# BAD 3: Using REJECT for security (reveals you're there)
iptables -A INPUT -p tcp --dport 3306 -j REJECT
# REJECT sends "connection refused" back to attacker
# Attacker knows port 3306 exists but is firewalled

# BETTER for security: DROP (silent drop - attacker gets no response)
iptables -A INPUT -p tcp --dport 3306 -j DROP
# Attacker sees timeout, less information about what's running
```

**GOOD - production firewall setup with ufw:**
```bash
#!/bin/bash
# server-firewall.sh: Idempotent production firewall setup

# Reset to defaults (if ufw was previously configured):
ufw --force reset

# Default policies:
ufw default deny incoming    # block all inbound by default
ufw default allow outgoing   # allow all outbound

# Always allow loopback:
ufw allow in on lo

# SSH - allow from management subnet only:
MGMT_SUBNET="10.0.1.0/24"
ufw allow from "${MGMT_SUBNET}" to any port 22 proto tcp

# Web traffic from anywhere:
ufw allow 80/tcp
ufw allow 443/tcp

# App-to-app communication (internal subnet only):
APP_SUBNET="10.0.2.0/24"
ufw allow from "${APP_SUBNET}" to any port 8080 proto tcp

# Deny database from everywhere except app subnet:
ufw allow from "${APP_SUBNET}" to any port 5432 proto tcp
# (5432 not open to 0.0.0.0 because not explicitly allowed)

# Enable:
ufw --force enable
ufw status numbered

echo "Firewall configured. Verify SSH access before closing this terminal!"
```

---

### Comparison Table

| Tool | Distro | Complexity | Backend | Persistent? |
|------|--------|-----------|---------|-------------|
| iptables | Universal | High | Netfilter | Requires iptables-persistent or scripting |
| nftables | Modern (kernel 3.13+) | High | Netfilter (next-gen) | Via nftables.service |
| ufw | Ubuntu/Debian | Low | iptables or nftables | Yes (stored in /etc/ufw/) |
| firewalld | RHEL/CentOS/Fedora | Medium | iptables or nftables | Yes (via daemon) |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "iptables rules persist after reboot" | iptables rules are in-kernel state only. On reboot, they're gone. You must save rules with `iptables-save > /etc/iptables/rules.v4` and use `iptables-persistent` or a startup script to restore. ufw and firewalld handle persistence automatically. |
| "DROP is safer than REJECT everywhere" | DROP makes sense for inbound unsolicited traffic (no information to attackers). For established connections or internal network errors, REJECT is better (tells the connecting app it's refused, preventing long connection timeouts). For SSH brute force protection: rate limiting + DROP is better. Context matters. |
| "Enabling the firewall blocks all outbound traffic" | Most firewalls default to ACCEPT for OUTPUT chain (all outbound allowed). Only INPUT is restricted by default in ufw (`ufw default deny incoming, ufw default allow outgoing`). Restricting outbound requires explicit egress rules - less common but important for defense-in-depth. |
| "ufw and iptables are separate systems" | ufw is a FRONTEND to iptables (or nftables on modern systems). When you run `ufw allow 22`, it writes iptables rules. `iptables -L -n -v` shows all rules including ufw's. They interact - manually adding iptables rules alongside ufw can cause confusion. Pick one tool per system. |
| "nftables replaces iptables - migrate now" | The kernel supports both (via netfilter). Many systems run iptables commands that are actually translated to nftables internally (iptables-nft). Full migration to native nftables syntax is recommended for new systems but not urgent for existing setups. ufw and firewalld handle the backend choice for you. |

---

### Failure Modes & Diagnosis

**Locked out of server via SSH after firewall change:**
```bash
# SSH connection hangs or refuses after iptables -P INPUT DROP

# If you have console/out-of-band access:
# Option 1: flush all rules (allow everything again):
iptables -F         # flush rules
iptables -P INPUT ACCEPT    # reset default policy

# Option 2: add just SSH rule:
iptables -I INPUT 1 -p tcp --dport 22 -j ACCEPT

# If using ufw and locked out with console access:
ufw disable         # turn off firewall entirely

# Prevention: set up an iptables "panic button" as a cron job:
# crontab -e:
# */15 * * * * /usr/bin/iptables -F && /usr/bin/iptables -P INPUT ACCEPT
# This auto-flushes firewall every 15 minutes
# Remove the cron job AFTER verifying your SSH rule works
```

**Application can't make outbound connections after INPUT rule changes:**
```bash
# curl https://api.example.com fails after adding DROP default

# Diagnosis: check ESTABLISHED,RELATED rule:
iptables -L INPUT -n -v | grep -i established

# Fix: add at the top of INPUT chain:
iptables -I INPUT 1 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Why: curl sends out (OUTPUT ACCEPT), server responds (INPUT)
# Without ESTABLISHED rule, the response packet hits INPUT and is DROPped
# curl gets no response, connection times out
```

---

### Related Keywords

**Foundational:**
LNX-023 (Networking Commands), NET-001 (Networking)

**Builds on this:**
LNX-056 (iptables and Netfilter Architecture), LNX-057 (Security Hardening)

**Related:**
SEC-001 (Security), LNX-085 (XDP), NET-001

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `iptables -L -n -v` | List all rules |
| `iptables -F` | Flush all rules |
| `iptables -P INPUT DROP` | Set default policy |
| `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` | Allow port |
| `iptables-save > /etc/iptables/rules.v4` | Save rules |
| `ufw status numbered` | Show ufw rules |
| `ufw allow 22/tcp` | Allow port (ufw) |
| `ufw enable/disable` | Enable/disable ufw |
| `firewall-cmd --list-all` | Show firewalld rules |
| `firewall-cmd --add-port=8080/tcp --permanent` | Add port (firewalld) |

**3 things to remember:**
1. Allow SSH BEFORE setting `iptables -P INPUT DROP` (or lock yourself out)
2. Always add `ESTABLISHED,RELATED -j ACCEPT` rule or return traffic gets blocked
3. iptables rules don't survive reboot - use iptables-persistent, ufw, or firewalld

---

### Transferable Wisdom

Netfilter/iptables concepts transfer directly to: AWS Security Groups (stateful
inbound/outbound rules, equivalent to iptables -m state ESTABLISHED,RELATED),
Azure NSG (same stateful model), Kubernetes NetworkPolicy (iptables rules
written by kube-proxy to restrict pod-to-pod traffic), Cilium and Calico CNI
plugins (eBPF-based packet filtering at the pod level), Docker networking
(iptables FORWARD rules control container-to-container and container-to-host
traffic). When AWS Security Groups say "allow inbound on port 443": they're
doing the same thing as `iptables -A INPUT -p tcp --dport 443 -j ACCEPT` -
same model, different interface.

The "allow outbound, statefully allow return traffic" pattern is standard
firewall design - it appears in every network security product from iptables
to Palo Alto firewalls. Understanding it at the iptables level makes AWS
Security Groups, GCP firewall rules, and enterprise firewalls instantly
understandable.

---

### The Surprising Truth

`iptables` was officially deprecated in kernel 5.x in favor of `nftables`,
but on many modern systems (including Ubuntu 22.04, Debian 11), when you
run `iptables`, you're actually running `iptables-nft` - a compatibility
layer that translates iptables commands to nftables rules. The output of
`iptables -L` looks identical, but under the hood the kernel is using nftables.
You can verify: `ls -la /usr/sbin/iptables` shows it's a symlink. The
transition is designed to be invisible. The same applies to `ip6tables`,
`ebtables`, and `arptables` - all have nftables compatibility shims. This
means on modern systems, `iptables` and `nft` rules coexist and can interact,
which can cause unexpected behavior if you use both simultaneously. The
recommendation: use nftables natively for new setups, or use ufw/firewalld
which abstract the backend choice.

---

### Mastery Checklist

- [ ] Can list current firewall rules using iptables and ufw
- [ ] Can allow and deny specific ports and protocols
- [ ] Can set up a basic allow-SSH-then-DROP-all policy without self-lockout
- [ ] Understands the INPUT/OUTPUT/FORWARD chain model
- [ ] Can make firewall rules persistent across reboots

---

### Think About This

1. You set `iptables -P INPUT DROP` and add `iptables -A INPUT -p tcp
   --dport 22 -j ACCEPT`. SSH works for login, but after logging in,
   `ping google.com` fails (connection timeout), `curl https://api.example.com`
   fails (timeout), but `curl http://localhost:8080` works. What single
   iptables rule is missing, and WHERE in the chain (position) must it
   be added?

2. You're setting up a Linux router/gateway. Client machines are on
   `10.0.1.0/24` (eth1), internet is on `eth0`. You want clients to
   share the internet connection. You've added `iptables -t nat -A
   POSTROUTING -o eth0 -j MASQUERADE`. But clients still can't reach
   the internet. What else must you configure in iptables AND in the
   kernel to make forwarding work?

3. Cloud environments (AWS, GCP) use "Security Groups" instead of
   having you configure iptables directly. When you allow port 443
   inbound in a Security Group, the VM's OS has no iptables rules for
   port 443. How does the cloud provider enforce the Security Group rule?
   At what layer of the network stack is it applied?

---

### Interview Deep-Dive

**Foundational:**
Q: What are the main iptables chains and what traffic does each handle?
A: iptables has five built-in chains in the filter table: (1) INPUT: handles packets DESTINED for the local machine (incoming traffic to services). Example: traffic to port 80 of this server hits INPUT. (2) OUTPUT: handles packets ORIGINATING from the local machine (outbound traffic). Example: when this server makes a curl request, it hits OUTPUT. (3) FORWARD: handles packets being ROUTED THROUGH this machine (this machine acts as a router). Example: if this machine is a gateway, client packets pass through FORWARD. (4) PREROUTING: packets arrive here BEFORE routing decision (in nat table). Used for DNAT (destination NAT, port forwarding). (5) POSTROUTING: packets here AFTER routing decision (in nat table). Used for SNAT/MASQUERADE (source NAT, IP masquerading). For a typical server: focus on INPUT (what can reach our services?), ensure OUTPUT has ESTABLISHED,RELATED allowed (return traffic), and ignore FORWARD unless routing. Key: ESTABLISHED,RELATED in INPUT means "if WE initiated a connection, allow the reply without explicit INPUT rule." Without it: web servers, apt updates, curl all fail because return packets get dropped.

**Intermediate:**
Q: You're setting up a new Ubuntu server and want to allow only SSH (port 22) and HTTPS (port 443) from outside, while allowing all outbound traffic. Walk me through the ufw commands, and then describe what happens to a TCP packet for MySQL port 3306 coming from the internet.
A: Using ufw: `ufw default deny incoming` (block all inbound - default), `ufw default allow outgoing` (allow all outbound - default), `ufw allow 22/tcp` (SSH), `ufw allow 443/tcp` (HTTPS), `ufw enable` (activate). Verify: `ufw status verbose`. For the MySQL packet journey: A TCP SYN packet arrives at the network interface from an external IP, destination port 3306. The kernel's Netfilter framework intercepts it at the PREROUTING hook. After routing decision: it's destined for this host, so it goes to INPUT chain. ufw has generated iptables rules. The rules are checked top to bottom. ufw's generated rules check: is it on loopback interface? No. Is it ESTABLISHED/RELATED? No (new SYN packet). Is it SSH (port 22)? No. Is it HTTPS (port 443)? No. Falls through to ufw's default policy (deny incoming = DROP). The packet is silently dropped. The client gets no response and eventually times out. If we used REJECT instead: the client gets an RST (connection refused) immediately. The difference matters: DROP hides that the port exists; REJECT tells the client it's explicitly denied.

**Expert:**
Q: In Kubernetes with kube-proxy in iptables mode, how does a Service ClusterIP work under the hood, and what are the performance implications for a large cluster?
A: Kubernetes Service with ClusterIP (say 10.96.0.1:80) routes to pods via kube-proxy-managed iptables rules. The mechanism: (1) kube-proxy watches the Kubernetes API for Service and Endpoint changes. (2) For each Service, kube-proxy creates iptables rules in the nat table. PREROUTING: packets to 10.96.0.1:80 are intercepted. `-A KUBE-SERVICES -d 10.96.0.1/32 -p tcp --dport 80 -j KUBE-SVC-XXXX`. The KUBE-SVC chain uses probabilistic DNAT to load balance: `-A KUBE-SVC-XXXX -m statistic --mode random --probability 0.33 -j KUBE-SEP-POD1`. Each KUBE-SEP chain DNATs to the actual pod IP: `-A KUBE-SEP-POD1 -j DNAT --to-destination 10.244.0.5:8080`. The kernel tracks the connection in conntrack, so return packets from 10.244.0.5:8080 are SNAT'd back to 10.96.0.1:80 for the client. Performance implications: iptables is O(n) per packet - each packet scans ALL rules linearly. With 10,000 Services and 50,000 Endpoints: each packet scans through potentially 50,000+ iptables rules. Kernel benchmark: large iptables rule sets cause 10-100ms latency for the first packet of a connection. Solutions: (1) kube-proxy IPVS mode: uses the kernel's IP Virtual Server (hash tables), O(1) lookup. Dramatically better at scale. (2) Cilium CNI: eBPF-based, replaces kube-proxy entirely, uses eBPF hash maps for O(1) Service lookup without iptables rules at all. At cluster scale (1000+ nodes, 50,000+ services): iptables mode becomes a bottleneck; IPVS or eBPF are required.
