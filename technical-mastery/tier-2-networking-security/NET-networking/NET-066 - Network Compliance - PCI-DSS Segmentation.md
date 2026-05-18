---
id: NET-066
title: "Network Compliance - PCI-DSS Segmentation"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-052
used_by: NET-067
related: NET-052, NET-062, NET-067
tags:
  - networking
  - compliance
  - pci-dss
  - segmentation
  - security
  - cardholder-data
  - audit
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/net/network-compliance-pci-dss-segmentation/
---

**⚡ TL;DR** - PCI-DSS (Payment Card Industry Data
Security Standard) requires that systems processing,
storing, or transmitting cardholder data be isolated
in a defined Cardholder Data Environment (CDE). Network
segmentation reduces PCI scope: systems outside the CDE
are not subject to PCI requirements (which are extensive).
Poor segmentation = entire network is in scope = audit
nightmare. Good segmentation: CDE is 10 servers, rest
of network is out of scope. The technical mechanism:
firewalls, VLANs, and strict ACLs at CDE boundary.

| #066 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Network Segmentation and Firewall Rules (NET-052) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | Network Segmentation and Firewall Rules, Service Mesh, Networking Deep-Dive Interview Questions | |

---

### 🔥 The Problem This Solves

Your company processes credit card payments. PCI-DSS
has 12 requirements covering 300+ controls. If your
entire network is "in scope," all 300 controls apply
to every server, workstation, and network device you
have. With proper segmentation: cardholder data is
only on 5 servers. Only those 5 servers are in scope.
5 × 300 controls vs 500 systems × 300 controls.
Audit complexity: 80-90% reduction. Developer velocity:
most of your infrastructure can be managed normally.

---

### 🧠 Intuition: Shrink the Attack Surface

```
PCI-DSS scope:
  IN SCOPE: anything that COULD affect cardholder data
    - Systems that store, process, transmit CHD
    - Systems connected to in-scope systems
    - Systems that manage in-scope systems

  OUT OF SCOPE: systems with NO path to CHD
    - Segmentation is what creates "no path"

Without segmentation (flat network):
  ALL systems are in scope
  Payment servers ↔ log servers ↔ dev machines ↔ printers
  A dev workstation can reach the payment DB?
  → In scope. Even the printer could be in scope.

With segmentation:
  [Internet]
      ↓
  [DMZ subnet]           ← Web servers, load balancers
      ↓ (port 443 only)
  [CDE subnet]           ← Payment processing servers (IN SCOPE)
      ↓ (no outbound internet)
  [CDE database subnet]  ← Cardholder data storage (IN SCOPE)
  
  [App subnet]           ← Other business apps (OUT OF SCOPE)
  [Dev subnet]           ← Developer machines (OUT OF SCOPE)
  No connection between CDE and non-CDE subnets.
  Result: CDE = 10 servers. PCI scope = those 10 servers.
```

---

### ⚙️ PCI-DSS Requirements That Network Segmentation Satisfies

```
Requirement 1: Install and maintain network security controls
  Firewall between CDE and all untrusted networks
  Firewall between CDE and all other internal networks
  Documented rules with justification for each rule
  Review firewall/router rules every 6 months

Requirement 1.3.1: Restrict inbound traffic to CDE to only
  what is necessary for the cardholder data environment.
  
  Translated: default-deny, allow only required flows

Requirement 1.3.2: Restrict outbound traffic from CDE to
  only what is necessary.
  
  Translated: CDE cannot initiate connections to internet
  or other internal zones except required destinations

Requirement 1.3.3: Prohibit direct public access between
  internet and cardholder data environment.
  
  Translated: no CDE server can have a public IP or
  direct internet route. Must go through DMZ.

Requirement 1.4: Network security controls between trusted
  and untrusted networks (wireless, public)
  
Requirement 7: Restrict access to system components and
  cardholder data by business need to know.
  Network access = firewall rules; limit to named systems

Key audit evidence:
  Network diagram showing CDE boundary
  Firewall ruleset exported and documented
  Evidence that no other path to CDE exists (penetration test)
  Change management for firewall rule additions
```

---

### ⚙️ Implementing PCI-Compliant Segmentation

```hcl
# AWS Terraform: PCI-compliant VPC segmentation

resource "aws_vpc" "pci" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "pci-vpc", PCI = "true" }
}

# DMZ: internet-facing, load balancers only
resource "aws_subnet" "dmz" {
  vpc_id            = aws_vpc.pci.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags              = { Name = "dmz", Tier = "public" }
}

# CDE: cardholder data processing (private subnet)
resource "aws_subnet" "cde" {
  vpc_id            = aws_vpc.pci.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"
  tags              = { Name = "cde", PCI = "in-scope" }
}

# CDE database: cardholder data storage
resource "aws_subnet" "cde_db" {
  vpc_id            = aws_vpc.pci.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"
  tags              = { Name = "cde-db", PCI = "in-scope" }
}

# Security group: CDE application servers
resource "aws_security_group" "cde_app" {
  name   = "cde-app-sg"
  vpc_id = aws_vpc.pci.id

  # ONLY from DMZ load balancer
  ingress {
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.dmz_lb.id]
    description     = "Payment processing from LB only"
  }

  egress {
    # Only to CDE database (NOT internet, NOT other subnets)
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.cde_db.id]
    description     = "PostgreSQL to CDE DB only"
  }
  # No other egress: CDE cannot reach internet directly
  # No egress to app subnet, dev subnet, or other networks
}

# CDE database: most restrictive
resource "aws_security_group" "cde_db" {
  name   = "cde-db-sg"
  vpc_id = aws_vpc.pci.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.cde_app.id]
    description     = "PostgreSQL from CDE app only"
  }
  # NO egress at all - database cannot initiate ANY connections
}
```

---

### ⚙️ Network Diagram Requirements for PCI Audit

```
PCI Requirement 1.2: Network diagrams must document:
  - All connections between in-scope and out-of-scope systems
  - All connections to internet and untrusted networks
  - All flows of cardholder data
  - All physical and logical network components in CDE

Diagram elements (must be current, updated within 30 days of change):
  
  ┌────────────────────────────────────────────────┐
  │  INTERNET                                      │
  └──────────────────┬─────────────────────────────┘
                     │ HTTPS:443
                     ▼
  ┌──────────────────────────────────────────────┐
  │  DMZ (10.0.1.0/24)                           │
  │  ┌────────────────┐                           │
  │  │  ALB / WAF     │ ← TLS termination here    │
  │  └────────┬───────┘                           │
  └───────────┼───────────────────────────────────┘
              │ HTTPS:8443 (only to CDE)
  ┌───────────▼───────────────────────────────────┐
  │  CDE (10.0.2.0/24)   [IN SCOPE]               │
  │  ┌────────────────┐                            │
  │  │ Payment App    │ → Tokenization             │
  │  └────────┬───────┘                            │
  └───────────┼────────────────────────────────────┘
              │ TCP:5432 (only to CDE-DB)
  ┌───────────▼────────────────────────────────────┐
  │  CDE-DB (10.0.3.0/24)  [IN SCOPE]              │
  │  ┌────────────────┐                             │
  │  │  PostgreSQL    │ ← CHD encrypted at rest     │
  │  └────────────────┘                             │
  └─────────────────────────────────────────────────┘
  
  NO connections from CDE to:
  - Other internal subnets
  - Internet (direct)
  - Corporate network
  - Dev environment

Diagram file: store in version control, date-stamped,
signed by network owner, attached to QSA audit evidence
```

---

### ⚙️ Wrong vs Right: Segmentation That Doesn't Actually Segment

```bash
# BAD: firewall allows "any" for monitoring or patching
# Security group / iptables rule for "operational convenience":
sudo iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT
# "Allows monitoring from internal subnet 10.0.0.0/8"
# Problem: 10.0.0.0/8 includes dev machines, print servers,
#          build servers, employee laptops
# ALL of these now have network path to CDE
# PCI: they are now IN SCOPE
# Audit: entire 10.0.0.0/8 becomes CDE scope

# BAD: "management" server in CDE that connects to everything
# A bastion or management server in CDE subnet with
# outbound access to all subnets
# → Bi-directional path exists between CDE and non-CDE
# → Segmentation is compromised

# GOOD: named source security groups for monitoring
# Allow monitoring ONLY from monitoring server:
resource "aws_security_group_rule" "cde_monitoring" {
  type                     = "ingress"
  from_port                = 9100  # prometheus node exporter
  to_port                  = 9100
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.monitoring.id
  security_group_id        = aws_security_group.cde_app.id
  description              = "Prometheus from monitoring server only"
}
# Monitoring server is in its own subnet, strictly controlled
# Documented in network diagram as "limited monitoring access"

# GOOD: separate patching path (AWS Systems Manager)
# Use AWS SSM (Systems Manager) for patching in CDE
# SSM uses VPC endpoints - no internet route needed
# SSM agent → VPC endpoint → SSM service
# Documents patching without opening firewall rules
```

---

### 📐 Scale Considerations

```
PCI compliance at scale:

Microservices with payment processing:
  Only the specific services that touch CHD are in scope
  Others: must NOT have a path to CHD services
  Service mesh (Istio) can enforce this via mTLS policies
  Evidence: export Istio AuthorizationPolicy as audit artifact

Kubernetes and PCI:
  Separate namespace for CDE workloads
  NetworkPolicy: default-deny, only required flows
  Node isolation: CDE pods on dedicated nodes (node selector)
  This prevents: non-PCI pod sharing node with PCI pod
    (process-level isolation issues on shared kernel)
  PCI compliance on K8s is possible but requires:
    Pod security standards (restricted)
    Runtime security (Falco or equivalent)
    Supply chain security (image scanning)

Tokenization to reduce scope:
  Accept card: at payment terminal / third-party iframe
  Receive: token (not actual PAN) in your backend
  Scope: only the tokenization gateway is in CDE
  Your backend stores tokens, not PANs = OUT OF SCOPE
  This is the most effective scope reduction strategy
  Used by: Stripe (Elements), Braintree, Square

Cloud compliance:
  AWS: PCI-DSS compliant services list (RDS, EKS, etc.)
  GCP: Assured Workloads for regulated industries
  Azure: Azure Government, compliance documentation
  Cloud provider compliance ≠ your architecture compliance
  You must still implement proper segmentation
```

---

### 🧭 Decision Guide

```
Steps to achieve PCI-compliant segmentation:

1. Map cardholder data flows
   Where does CHD enter, flow through, and leave?
   Every system on that path is CDE scope

2. Reduce scope with tokenization
   Don't accept raw PANs in your backend
   Use third-party tokenization at point of entry
   Your backend never sees the actual card number

3. Isolate remaining CDE systems
   Separate subnet, VLAN, or cloud VPC
   Firewall rules: default deny, named allowances only
   Document every allowed flow with justification

4. Validate segmentation (required by PCI)
   Penetration test: verify non-CDE cannot reach CDE
   Firewall review: every rule justified and necessary
   Network scan from outside CDE: only expected ports open

5. Ongoing evidence collection
   Log all changes to CDE network rules (change management)
   Quarterly firewall rule review (document and sign)
   Annual segmentation validation (pen test or assessment)
   Network diagrams: update within 30 days of changes

Architect's decision tree:
  "Does this system need to see raw PANs?"
  YES → it's in CDE scope, apply all PCI controls
  NO → can we use tokenization or a third-party gateway?
       YES → keep it out of scope
       NO → why does it need CHD access? (challenge the requirement)
```