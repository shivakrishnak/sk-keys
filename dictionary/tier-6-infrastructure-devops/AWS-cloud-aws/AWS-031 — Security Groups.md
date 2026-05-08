---
layout: default
title: "Security Groups"
parent: "Cloud — AWS"
nav_order: 31
permalink: /cloud-aws/security-groups/
id: AWS-031
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["VPC", "Subnets (Public / Private)"]
used_by: ["EC2", "RDS", "ELB / ALB / NLB", "EKS", "ElastiCache", "Lambda"]
related: ["VPC", "NACLs", "Subnets (Public / Private)", "Network Policy"]
tags: [aws, security-groups, firewall, networking, vpc, security, cloud]
---

# Security Groups

## ⚡ TL;DR

**Security Groups** are stateful virtual firewalls at the resource level (EC2, RDS, ALB). You define **inbound and outbound rules** using Allow only (no explicit Deny). Default: deny all inbound, allow all outbound. Best practice: reference other Security Groups (not IP CIDRs) for dynamic membership — "allow from ALB's Security Group" vs "allow from 10.0.0.0/8".

---

## 🔥 Problem This Solves

Without Security Groups: any resource in the VPC can connect to any other on any port. Security Groups provide per-resource traffic filtering — your RDS instance only accepts connections from your EC2 app tier, not from every resource in the VPC.

---

## 📘 Textbook Definition

An AWS Security Group is a stateful virtual firewall that controls inbound and outbound traffic for AWS resources (EC2 instances, ENIs, RDS, Lambda in VPC, etc.). Security Groups operate at the resource level (not subnet level), are stateful (return traffic is automatically allowed), and support only Allow rules (no explicit Deny).

---

## ⏱️ 30 Seconds

```
Security Group rules:
  Inbound:  Protocol | Port Range | Source
  Outbound: Protocol | Port Range | Destination

Stateful: if inbound TCP 443 is allowed → response traffic (outbound)
          is automatically allowed (no outbound rule needed)

Source/Destination types:
  - CIDR: 0.0.0.0/0 (anywhere), 10.0.0.0/16 (specific range)
  - Security Group ID: sg-12345 (all resources with that SG)
  - My IP: 203.0.113.1/32

Default SG behavior:
  - All inbound: DENIED (no rules = deny)
  - All outbound: ALLOWED (default outbound rule: 0.0.0.0/0)
```

---

## 🔩 First Principles

- **Stateful**: connection tracking; return packets auto-allowed; contrast with NACLs (stateless)
- **Allow-only**: you can only add Allow rules; no explicit Deny
- **Multiple SGs per resource**: up to 5 SGs per ENI; rules are combined (union of all allows)
- **SG as source/destination**: reference SG ID instead of IP; membership is dynamic
- **Changes are immediate**: no restart needed; rules apply instantly
- **SG is VPC-scoped**: can reference SGs in same VPC (or peered VPC with special config)

---

## 🧪 Thought Experiment

You have 100 EC2 app servers and add more during peak. If you use IP CIDRs in RDS security group rules: every time you add a new server, you update the SG with new IPs. Error-prone and doesn't scale. Using SG reference: "allow from sg-app-servers-sg" — whenever a new EC2 gets that SG, it's automatically allowed. Self-managing, zero maintenance.

---

## 🧠 Mental Model / Analogy

Security Group is a **club membership list**: to get in, you must be on the list (inbound rule). If you're allowed in, you can leave freely (stateful, outbound auto-allowed). The bouncer (SG) checks at the door of each resource. "Allow all members of Club EC2 (sg-ec2)" means any EC2 with that SG tag can enter, regardless of which ones or how many.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Every resource needs a Security Group. Define inbound rules for allowed traffic. Reference SG IDs instead of IPs where possible.

**Level 2 — Practitioner**: 3-tier SG pattern: ALB-SG (443 from internet) → App-SG (8080 from ALB-SG) → DB-SG (5432 from App-SG). Each SG references the tier above it. No hardcoded IPs.

**Level 3 — Advanced**: Self-referencing SG: allow all traffic within the same SG (useful for ECS/EKS pod-to-pod communication). Lambda in VPC: Lambda gets an ENI in your subnet → needs Security Group. SSM Session Manager: replaces SSH; no inbound 22 needed → stricter SG possible.

**Level 4 — Expert**: SGs with IPv6: add `::/0` rules separately (IPv4 and IPv6 rules are separate). AWS Network Firewall: SG-level filtering is stateful but layer 4 only; Network Firewall adds layer 7 inspection (domain filtering, IDS/IPS). Security Group referencing across peered VPCs is supported. VPC Endpoint policies: complement SG by restricting which S3 buckets can be accessed via endpoint.

---

## ⚙️ How It Works

### 3-Tier Security Group Design

```hcl
# 1. ALB Security Group: public-facing
resource "aws_security_group" "alb" {
  name   = "alb-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # public internet
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # redirect to 443
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. App Server Security Group: receives from ALB only
resource "aws_security_group" "app" {
  name   = "app-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # SG reference!
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Database Security Group: receives from App only
resource "aws_security_group" "db" {
  name   = "db-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432    # PostgreSQL
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]  # SG reference!
  }

  # No outbound needed for managed databases
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### EKS Security Groups

```hcl
# EKS node security group
resource "aws_security_group" "eks_nodes" {
  name   = "eks-nodes-sg"
  vpc_id = aws_vpc.main.id

  # Node-to-node communication (kubelet, pod networking)
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true   # allow from same SG (all nodes)
  }

  # API server to kubelet (for kubectl logs, exec)
  ingress {
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_control_plane.id]
  }

  # HTTPS to API server
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Principle: Lock Down Default Outbound

```hcl
# Production: restrict outbound to known destinations
resource "aws_security_group" "app_strict" {
  name   = "app-sg-strict"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow only: DNS, HTTPS (external APIs), and database
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]  # DNS
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS APIs
  }

  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.db.id]  # DB only
  }
}
```

---

## ⚖️ Comparison Table: Security Groups vs NACLs

|                     | Security Groups    | NACLs                          |
| ------------------- | ------------------ | ------------------------------ |
| **Applies to**      | Resource (ENI)     | Subnet                         |
| **Stateful**        | ✅                 | ❌ (must allow return traffic) |
| **Rules**           | Allow only         | Allow + Deny                   |
| **Evaluation**      | All rules combined | Numbered, first match wins     |
| **Default inbound** | Deny all           | Allow all (in default NACL)    |
| **Recommended for** | All resources      | Subnet-level defense-in-depth  |

---

## ⚠️ Common Misconceptions

| Misconception                          | Reality                                                           |
| -------------------------------------- | ----------------------------------------------------------------- |
| "Security Group = subnet firewall"     | Security Groups are per-resource (ENI); NACLs are per-subnet      |
| "Must add outbound rule for responses" | Stateful: responses are auto-allowed regardless of outbound rules |
| "Can only have one SG per resource"    | Up to 5 SGs per ENI; rules are additive                           |
| "SG changes require restart"           | Changes apply immediately to existing connections                 |

---

## 🔗 Related Keywords

- [NACLs](/cloud-aws/nacls/) — subnet-level stateless firewall
- [VPC](/cloud-aws/vpc/) — Security Groups are VPC-scoped
- [Subnets (Public / Private)](/cloud-aws/subnets-public-private/) — Security Groups complement subnet design
- [Network Policy](/kubernetes/network-policy/) — analogous concept in Kubernetes

---

## 📌 Quick Reference Card

```bash
# Create security group
aws ec2 create-security-group \
  --group-name my-sg \
  --description "App server SG" \
  --vpc-id vpc-12345

# Add inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp \
  --port 8080 \
  --source-group sg-alb-67890  # SG reference

# Add inbound CIDR rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Describe rules
aws ec2 describe-security-group-rules \
  --filters Name=group-id,Values=sg-12345

# Check SG attached to instance
aws ec2 describe-instances \
  --instance-ids i-12345 \
  --query 'Reservations[].Instances[].SecurityGroups'

# Find unused security groups
aws ec2 describe-network-interfaces \
  --query 'NetworkInterfaces[].Groups[].GroupId' \
  --output text | sort | uniq > used_sgs.txt
aws ec2 describe-security-groups \
  --query 'SecurityGroups[].GroupId' \
  --output text | sort | uniq > all_sgs.txt
comm -23 all_sgs.txt used_sgs.txt  # unused SGs
```

---

## 🧠 Think About This

Using **Security Group IDs as sources/destinations** (instead of IP CIDRs) is one of the most impactful AWS networking practices. When you write "allow from sg-app" you're expressing intent: "allow traffic from my application tier," which remains correct even when instances are replaced, scaled up/down, or shifted across IP addresses. IP-based rules are operationally fragile and don't express intent. The corollary: give meaningful names to Security Groups (not "launch-wizard-1"), and audit periodically for SGs with `0.0.0.0/0` inbound rules — these are almost always unnecessarily permissive and represent real security risk.
