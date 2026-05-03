---
layout: default
title: "Firewall"
parent: "Networking"
nav_order: 184
permalink: /networking/firewall/
number: "0184"
category: Networking
difficulty: ★★☆
depends_on: IP Addressing, TCP, UDP, Socket, Port & Ephemeral Port
used_by: Linux, Cloud — AWS, Cloud — Azure, Kubernetes, Microservices
related: VPN, NAT, Zero Trust Networking, Network Policies, TLS/SSL
tags:
  - networking
  - firewall
  - security
  - iptables
  - nsg
  - stateful
---

# 184 — Firewall

⚡ TL;DR — A firewall is a network security control that permits or denies traffic based on rules (IP, port, protocol, state). Stateless firewalls inspect each packet independently; stateful firewalls track connection state and allow return traffic automatically — and modern next-gen firewalls (NGFWs) add Layer 7 application inspection, IDS/IPS, and TLS inspection.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Linux server with a public IP is connected to the internet. Without a firewall, every port (1-65535) is reachable by anyone. Port 3306 (MySQL), 5432 (PostgreSQL), 6379 (Redis) — all exposed to automated scanners that continuously probe for default credentials, known CVEs, and open services. The average internet-facing server receives exploit attempts within minutes of being provisioned.

**THE BREAKING POINT:**
The internet is a hostile network. Any reachable service is constantly probed. Without firewalls, every service — database, admin interfaces, internal APIs — would need to be individually hardened. A single misconfigured Redis instance exposed on port 6379 (no auth, default config) leads to data exfiltration and cryptominer installation. The attack surface is proportional to the number of reachable ports.

**THE INVENTION MOMENT:**
Firewalls emerged in the late 1980s as the "perimeter defence" model: define a trusted internal network and an untrusted external network; permit only intended traffic. Modern cloud security groups (AWS), NSGs (Azure), and Linux `iptables`/`nftables` apply the same principle: default DENY, explicit ALLOW — reducing attack surface to only what's needed.

---

### 📘 Textbook Definition

A **firewall** is a network security device (hardware or software) that monitors and controls incoming and outgoing network traffic based on predetermined security rules. Types:

1. **Packet filter (stateless):** Inspects each packet independently; rules based on src/dst IP, port, protocol. Fast, simple, no session state.
2. **Stateful inspection firewall:** Tracks TCP/UDP connection state. Automatically permits reply packets for established connections. More accurate; prevents spoofed return traffic.
3. **Application-layer (Layer 7) / NGFW:** Inspects application protocols (HTTP, DNS, TLS SNI). Can block by app type, URL, user identity — not just IP:port.
4. **Web Application Firewall (WAF):** HTTP-specific; blocks SQLi, XSS, CSRF, OWASP Top 10.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A firewall is a gatekeeper that applies ALLOW/DENY rules to network traffic — blocking everything not explicitly permitted, protecting services from unauthorised access.

**One analogy:**

> A firewall is like a nightclub bouncer with a list. Default policy: nobody gets in. The list specifies: "allow anyone wearing a suit (port 443), allow VIP members with ID (specific IPs), block everyone else." Stateful: if you went inside (established connection), the bouncer lets you come back from the bathroom (return packets) without re-checking the list. NGFW: the bouncer can also check what you're carrying inside (application payload inspection).

**One insight:**
The most important firewall rule is the **default policy**. "Default DENY" (whitelist model) means: if no rule matches, traffic is blocked. "Default ALLOW" (blacklist model) means: if no rule matches, traffic is permitted. Cloud security groups are default-deny — only explicitly whitelisted traffic reaches your instances. On-premise firewalls are often misconfigured with overly-permissive rules accumulated over years because changing rules requires a change request. Zero Trust networking extends default-deny to internal east-west traffic — not just the perimeter.

---

### 🔩 First Principles Explanation

**IPTABLES ARCHITECTURE (Linux):**

```
┌──────────────────────────────────────────────────────────┐
│  Linux iptables: Tables, Chains, Rules                   │
└──────────────────────────────────────────────────────────┘

Packet arrives → PREROUTING → FORWARD or INPUT
                              │
                        INPUT: local process
                        FORWARD: route to another interface
                        OUTPUT: locally generated packets
                              │
                           POSTROUTING → packet leaves

Tables:
  filter: main firewall (INPUT, OUTPUT, FORWARD)
  nat:    address translation (PREROUTING, POSTROUTING)
  mangle: packet modification
  raw:    pre-connection tracking

Filter chain rules: each rule = conditions + action
  Conditions: -s srcIP, -d dstIP, -p proto, --dport port, -i iface
  Actions: ACCEPT, DROP, REJECT, LOG, RETURN, JUMP to chain

Default policies:
  iptables -P INPUT DROP    ← default deny inbound
  iptables -P FORWARD DROP
  iptables -P OUTPUT ACCEPT ← allow outbound
```

**STATEFUL TRACKING:**

```
# Stateful: allow established connections back
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow incoming HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow SSH from specific IP
iptables -A INPUT -p tcp --dport 22 -s 10.0.1.5 -j ACCEPT

# Drop everything else (default policy handles this, but explicit)
iptables -A INPUT -j DROP

# Connection tracking states:
# NEW:         first packet of connection (SYN)
# ESTABLISHED: connection has been established
# RELATED:     related to existing connection (e.g., FTP data)
# INVALID:     does not match any connection
```

**CLOUD SECURITY GROUPS (AWS):**

```
Security Group: stateful firewall at instance level

Inbound rules:
  Type    Protocol  Port  Source
  HTTP    TCP       80    0.0.0.0/0  (public web)
  HTTPS   TCP       443   0.0.0.0/0  (public web)
  SSH     TCP       22    10.0.0.5/32 (bastion only)
  MySQL   TCP       3306  sg-webapp  (only from app SG)

Outbound rules:
  All traffic → 0.0.0.0/0 (allow all outbound)

Key: stateful → if inbound rule allows HTTP request, response
     automatically allowed without explicit outbound rule
```

---

### 🧪 Thought Experiment

**SETUP:**
You're designing the network security for a 3-tier web app: load balancer, app servers, database.

**FIREWALL RULE DESIGN:**

_Load Balancer (public):_

- Inbound: 80, 443 from 0.0.0.0/0 (anyone)
- Outbound: 8080 to app-server-security-group only

_App Servers (private subnet):_

- Inbound: 8080 from load-balancer-security-group only
- No direct public internet access
- Outbound: 5432 to db-security-group, 443 to internet (for API calls)

_Database (private subnet):_

- Inbound: 5432 from app-server-security-group ONLY
- No inbound from internet, no inbound from load balancer
- Outbound: None needed

**RESULT:**
Even if the load balancer is compromised, it can only reach app servers on port 8080. Even if an app server is compromised, it can only reach the database on port 5432. A direct attack from the internet to the database is impossible — the security group rule doesn't exist. This is "defence in depth" via firewall segmentation.

---

### 🧠 Mental Model / Analogy

> A stateful firewall is like a hotel doorman who maintains a guest list. The doorman's default policy: no entry unless on the list. When a guest (outgoing connection) leaves the hotel (established connection), the doorman notes their face. When they return later (return packets), the doorman recognises them and lets them back in without requiring them to be on the inbound list. A perimeter-only firewall is like only having a doorman at the hotel entrance — once someone is inside (internal network), they can move freely. Zero Trust adds doormen at every room (mutual auth for every service-to-service call).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A firewall is a security guard for network traffic. It checks every packet and decides: "You're allowed in, you're not." Rules say things like: "Let in web traffic on port 443, block everything else." This keeps hackers from connecting to your database server directly, even if they can reach your IP address.

**Level 2 — How to use it (junior developer):**
In cloud: use Security Groups (AWS) or NSGs (Azure Network Security Groups). Create inbound rules for only the ports your service needs (443 for HTTPS, 22 from your IP for SSH). Default: deny everything else. For databases (3306, 5432, 6379): NEVER allow from 0.0.0.0/0 (the internet). Allow ONLY from the security group of your app servers. Use `ufw` (Ubuntu) or `firewall-cmd` (RHEL/CentOS) for OS-level firewalls. Run `nmap` against your own IP to see what ports are reachable from outside.

**Level 3 — How it works (mid-level engineer):**
Linux firewalling: `iptables` (older, still common) or `nftables` (modern). Both hook into the kernel's netfilter framework at defined processing points (hooks: PREROUTING, INPUT, FORWARD, OUTPUT, POSTROUTING). Stateful tracking via `conntrack` module — kernel maintains a connection tracking table indexed by 4-tuple. Connection states: NEW, ESTABLISHED, RELATED, INVALID. The `-m state --state ESTABLISHED,RELATED -j ACCEPT` rule is the critical stateful rule — without it, you must explicitly allow every return packet. For complex setups: firewall zones (trusted, untrusted, DMZ), VLAN-based segmentation, network ACLs (NACLs in AWS — stateless, applied at subnet level, complements stateful security groups).

**Level 4 — Why it was designed this way (senior/staff):**
The perimeter model (firewall at the edge of the network) was designed for the 1990s threat model: trusted internal network, untrusted internet. This fails for modern cloud-native architectures where: (1) "inside the network" includes cloud providers, VPNs, contractors, lateral movement after breach; (2) services communicate over APIs across network boundaries; (3) microservices in Kubernetes pods on the same node communicate internally. The response: Zero Trust (every connection authenticated and authorised regardless of network location), Kubernetes Network Policies (pod-level firewall rules), service mesh mTLS (mutual TLS authentication at the application layer, not network layer). The evolution: packet filter → stateful → NGFW → Zero Trust — each layer adding context beyond IP:port.

---

### ⚙️ How It Works (Mechanism)

```bash
# View current iptables rules
iptables -L -v -n --line-numbers

# View with traffic counters
iptables -L INPUT -v -n | head -20

# Common iptables setup (Linux server)
# 1. Allow loopback (localhost)
iptables -A INPUT -i lo -j ACCEPT

# 2. Allow established/related connections (stateful)
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. Allow SSH from specific IP
iptables -A INPUT -p tcp --dport 22 -s 203.0.113.5 -j ACCEPT

# 4. Allow HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 5. Default deny (set policy)
iptables -P INPUT DROP

# Save rules (persist across reboot)
iptables-save > /etc/iptables/rules.v4

# Ubuntu UFW (simpler interface)
ufw default deny incoming
ufw default allow outgoing
ufw allow 443/tcp
ufw allow from 10.0.0.5 to any port 22
ufw enable
ufw status verbose

# AWS CLI: add security group rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Check what's reachable (from outside)
nmap -sV -p 1-1000 YOUR_IP
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────┐
│  3-Tier Firewall Architecture                        │
└──────────────────────────────────────────────────────┘

Internet
   │
   ▼
[WAF / NGFW]          ← Layer 7 inspection, DDoS, OWASP
   │ Allow: 80, 443
   │ Block: everything else
   ▼
[Load Balancer SG]    ← AWS Security Group (stateful)
   │ Inbound: 80, 443 from 0.0.0.0/0
   │ Outbound: 8080 to app-sg only
   ▼
[App Server SG]       ← Private subnet
   │ Inbound: 8080 from lb-sg only
   │ Outbound: 5432 to db-sg, 443 to internet
   ▼
[Database SG]         ← Isolated subnet
   │ Inbound: 5432 from app-sg ONLY
   │ No internet access whatsoever
   ▼
[Database]
```

---

### 💻 Code Example

```python
import subprocess
import json
from typing import List, Dict

def audit_security_group_rules(sg_id: str) -> List[Dict]:
    """Audit AWS Security Group for overly permissive rules.
    Returns list of risky rules (open to 0.0.0.0/0 on sensitive ports).
    """
    SENSITIVE_PORTS = {22, 3306, 5432, 6379, 27017, 9200, 2181}

    result = subprocess.run(
        ["aws", "ec2", "describe-security-groups",
         "--group-ids", sg_id, "--output", "json"],
        capture_output=True, text=True
    )
    sg_data = json.loads(result.stdout)

    risks = []
    for sg in sg_data.get("SecurityGroups", []):
        for rule in sg.get("IpPermissions", []):
            from_port = rule.get("FromPort", 0)
            to_port = rule.get("ToPort", 65535)

            for ip_range in rule.get("IpRanges", []):
                cidr = ip_range.get("CidrIp", "")
                if cidr in ("0.0.0.0/0", "::/0"):
                    for port in range(from_port, to_port + 1):
                        if port in SENSITIVE_PORTS:
                            risks.append({
                                "sg_id": sg["GroupId"],
                                "port": port,
                                "cidr": cidr,
                                "risk": "CRITICAL: sensitive port open to internet"
                            })

    return risks

# Usage
risks = audit_security_group_rules("sg-12345678")
for risk in risks:
    print(f"⚠️  {risk['sg_id']}: port {risk['port']} "
          f"open to {risk['cidr']} — {risk['risk']}")
```

---

### ⚖️ Comparison Table

| Type               | Stateless Packet Filter | Stateful Firewall | NGFW/WAF                  |
| ------------------ | ----------------------- | ----------------- | ------------------------- |
| Layer              | L3-L4                   | L3-L4 + state     | L3-L7                     |
| Tracks connections | No                      | Yes               | Yes                       |
| Performance        | Very fast               | Fast              | Slower (DPI)              |
| Return traffic     | Explicit rules needed   | Auto-allowed      | Auto-allowed              |
| App awareness      | No                      | No                | Yes                       |
| Use case           | Router ACLs, NACLs      | AWS SG, iptables  | Palo Alto, CloudFlare WAF |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                            |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A firewall means you're secure       | A firewall is one layer. If port 443 is open (it must be), all HTTP-layer attacks (SQLi, XSS, auth bypass) pass through the firewall. Need WAF, input validation, auth at the application layer    |
| AWS Security Groups are stateless    | Security Groups are STATEFUL. NACLs (Network ACLs, subnet level) are STATELESS and require explicit inbound AND outbound rules for each connection                                                 |
| Firewalls slow down all traffic      | Modern hardware firewalls and Linux `nftables` have negligible overhead for stateful inspection at speeds up to 100Gbps. Performance only degrades significantly with deep packet inspection (DPI) |
| Default-deny outbound breaks nothing | Strict outbound rules DO break things: no DNS (port 53), no NTP (port 123), no OS package updates (port 443). Design outbound rules carefully, especially in Kubernetes/containers                 |

---

### 🚨 Failure Modes & Diagnosis

**Security Group Misconfiguration: Database Exposed to Internet**

**Symptom:**
Security audit reveals `0.0.0.0/0` allowed on port 3306. Automated scanners have already attempted default MySQL credentials. Possible data exfiltration.

```bash
# Detect open sensitive ports (from outside)
nmap -sV -p 3306,5432,6379,27017 YOUR_SERVER_IP

# AWS: find all SGs with 0.0.0.0/0 on sensitive ports
aws ec2 describe-security-groups --output json | \
  jq '.SecurityGroups[] | select(.IpPermissions[].IpRanges[].CidrIp == "0.0.0.0/0") | {GroupId, GroupName}'

# Immediate fix: remove the overly permissive rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp --port 3306 --cidr 0.0.0.0/0

# Add correct rule (only from app server SG)
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp --port 3306 \
  --source-group sg-appserver-id

# Check MySQL auth logs for intrusion
grep "Access denied\|Failed\|ERROR" /var/log/mysql/error.log | tail -50
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `TCP`, `UDP`, `Socket, Port & Ephemeral Port`

**Related:** `VPN` (tunnels traffic through firewall), `NAT` (common with firewall on router), `Zero Trust Networking` (extends firewall to every connection), `Network Policies` (Kubernetes pod-level firewall), `TLS/SSL` (firewall can't inspect without TLS termination)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STATELESS    │ Per-packet rules (AWS NACL, router ACL)   │
│ STATEFUL     │ Tracks connections; auto-allows return     │
│              │ traffic (AWS Security Group, iptables)     │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Default DENY + explicit ALLOW (whitelist) │
│              │ Never open 3306/5432/6379 to 0.0.0.0/0   │
├──────────────┼───────────────────────────────────────────┤
│ LAYERS       │ AWS: NACL (subnet, stateless) +           │
│              │ Security Group (instance, stateful)       │
├──────────────┼───────────────────────────────────────────┤
│ AUDIT        │ nmap YOUR_IP; aws ec2 describe-sg; ufw status│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bouncer with a list: default deny,       │
│              │ explicit allow; stateful = knows regulars"│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a Kubernetes network security architecture for a multi-tenant SaaS application with 50 customer namespaces, each containing frontend, backend, and database pods. (a) Explain Kubernetes Network Policies: how they use pod selectors and namespace selectors to implement firewall rules at the CNI level (Calico, Cilium). (b) Write Network Policies to: allow frontend→backend on port 8080, allow backend→database on port 5432, deny all cross-namespace traffic. (c) Explain why default-deny Network Policies are critical in Kubernetes (by default, all pods in a cluster can communicate with all other pods). (d) How does eBPF-based networking (Cilium) enforce Network Policies more efficiently than traditional iptables chains? (e) How does a service mesh (Istio mTLS) complement Network Policies — what does each layer provide?

**Q2.** Analyse the security implications of deep packet inspection (DPI) firewalls for HTTPS traffic. (a) How does TLS inspection work (man-in-the-middle: enterprise CA installs root cert on all devices, firewall terminates TLS and re-encrypts). (b) What attacks does TLS inspection enable detection of vs what privacy implications it creates. (c) Why does certificate pinning (apps rejecting certificates from enterprise CAs) break TLS inspection. (d) Explain SNI-based filtering (blocking by TLS SNI hostname without full TLS termination) as a privacy-respecting alternative. (e) How does DNS-over-HTTPS (DoH) complicate traditional DNS-based firewall blocking, and how enterprises respond (force internal DNS, block known DoH servers).
