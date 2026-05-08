---
layout: default
title: "NACLs"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /cloud-aws/nacls/
id: AWS-032
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["VPC", "Subnets (Public / Private)", "Security Groups"]
used_by: ["VPC", "Subnets (Public / Private)"]
related:
  [
    "Security Groups",
    "VPC",
    "Subnets (Public / Private)",
    "Internet Gateway / NAT Gateway",
  ]
tags: [aws, nacl, network-acl, networking, firewall, stateless, vpc, cloud]
---

# NACLs

## ⚡ TL;DR

**NACLs (Network Access Control Lists)** are stateless subnet-level firewalls. Unlike Security Groups (stateful, resource-level), NACLs require explicit rules for **both** inbound AND outbound (including ephemeral return ports 1024-65535). Default NACL: allow all. Custom NACLs: deny all by default. NACLs are a secondary defense layer — most workloads rely primarily on Security Groups.

---

## 🔥 Problem This Solves

Security Groups protect individual resources but can't block traffic from one subnet to another at the network level. NACLs add subnet-to-subnet firewall rules — useful for defense-in-depth and for explicit IP-based blocking (e.g., block known malicious IPs at subnet entry before they reach any resource).

---

## 📘 Textbook Definition

A Network Access Control List (NACL) is a stateless, numbered-rule firewall associated with a subnet. Each subnet is associated with exactly one NACL. NACLs evaluate rules in order from lowest to highest rule number; the first matching rule applies. NACLs can contain both Allow and Deny rules, unlike Security Groups which only support Allow.

---

## ⏱️ 30 Seconds

```
NACL vs Security Group:
  NACL:       subnet level, stateless, allow + deny, numbered rules
  Sec Group:  resource level, stateful, allow only, all rules combined

NACL rule evaluation:
  Rule 100: Allow TCP 443 from 0.0.0.0/0  → HTTP traffic in
  Rule 200: Allow TCP 1024-65535 from 0.0.0.0/0 → ephemeral ports (responses)
  Rule *:   DENY all  (default deny, always last)

STATELESS means: if you allow inbound TCP 443,
  you MUST also allow outbound ephemeral ports (1024-65535)
  for the response packets to leave the subnet.
```

---

## 🔩 First Principles

- **Stateless**: each packet evaluated independently; no connection tracking
- **Both directions required**: allow inbound + allow outbound response ports
- **Numbered rules**: evaluated in ascending order; first match wins; \* = implicit deny
- **Subnet-level**: applies to all traffic entering/leaving the subnet (not instance-level)
- **Deny support**: NACLs can explicitly deny; useful for blocking specific IPs
- **Default NACL**: allows all inbound/outbound; associated with subnets not in a custom NACL
- **Custom NACL**: denies all by default until rules added

---

## 🧪 Thought Experiment

You want to block a specific IP (e.g., known attacker 1.2.3.4) from reaching any resource in your public subnet. Security Groups can't add Deny rules. NACL can: add Rule 90 "Deny inbound from 1.2.3.4/32" before any Allow rules — all traffic from that IP is dropped at the subnet boundary before reaching any resource.

---

## 🧠 Mental Model / Analogy

NACL is a **stateless checkpoint at the neighborhood entrance**: it checks every car entering and leaving against a numbered list of rules. First matching rule applies. Importantly: if the guard lets your car in (inbound rule), there's no automatic record of this — when your car tries to leave (response traffic), the guard checks the outbound list independently. This is why you need separate return port rules.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Default NACL allows everything (fine for start). Security Groups are your primary defense. NACLs are secondary.

**Level 2 — Practitioner**: Create custom NACLs when you need explicit Deny rules (block malicious IPs) or subnet-to-subnet traffic control. Always remember: stateless = add ephemeral port rules (1024-65535) for outbound.

**Level 3 — Advanced**: NACL + Security Group together: NACL blocks at subnet boundary (coarse), Security Group blocks at instance (fine). Use NACLs to prevent cross-subnet attacks: private-app subnet should not accept traffic from public subnet (except from ALB SG — handle this at SG level; or NACL level for subnet-wide block).

**Level 4 — Expert**: Rule numbering strategy: leave gaps (100, 200, 300) for easy insertion. Use different rule ranges for different purposes: 100-199 allow rules, 200-299 deny rules for abuse IPs (auto-populated by Lambda + GuardDuty). GuardDuty + Lambda automation: automatically add Deny rules to NACL when GuardDuty finds malicious IP. NACL rules are limited: max 20 inbound + 20 outbound rules per NACL (soft limit, can increase). For large block lists, use AWS WAF (Web Application Firewall) instead.

---

## ⚙️ How It Works

### NACL Rule Table (Public Subnet)

```
# Public subnet NACL — allows web traffic + admin SSH from specific IP

INBOUND RULES:
Rule # | Type       | Protocol | Port Range | Source          | Allow/Deny
100    | HTTPS      | TCP      | 443        | 0.0.0.0/0       | ALLOW
110    | HTTP       | TCP      | 80         | 0.0.0.0/0       | ALLOW
120    | SSH        | TCP      | 22         | 203.0.113.1/32  | ALLOW (admin IP)
130    | Custom TCP | TCP      | 1024-65535 | 0.0.0.0/0       | ALLOW (ephemeral)
*      | All traffic|          |            | 0.0.0.0/0       | DENY

OUTBOUND RULES:
Rule # | Type       | Protocol | Port Range | Destination     | Allow/Deny
100    | HTTPS      | TCP      | 443        | 0.0.0.0/0       | ALLOW
110    | HTTP       | TCP      | 80         | 0.0.0.0/0       | ALLOW
120    | Custom TCP | TCP      | 1024-65535 | 0.0.0.0/0       | ALLOW (ephemeral responses)
*      | All traffic|          |            | 0.0.0.0/0       | DENY
```

### Blocking Malicious IPs with NACL

```hcl
# Terraform: NACL with block list
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  # Block known bad actor
  ingress {
    rule_no    = 10
    action     = "deny"
    protocol   = "all"
    cidr_block = "192.0.2.0/24"  # blocked IP range
    from_port  = 0
    to_port    = 0
  }

  # Allow HTTPS
  ingress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Allow ephemeral return ports (CRITICAL for stateless)
  ingress {
    rule_no    = 900
    action     = "allow"
    protocol   = "tcp"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Implicit deny: no catch-all rule needed (AWS adds * deny)
}
```

### GuardDuty + Lambda Auto-Block

```python
# Lambda: auto-add NACL deny rule when GuardDuty finds malicious IP
import boto3

def handler(event, context):
    finding = event['detail']

    # Extract malicious IP from GuardDuty finding
    remote_ip = finding['service']['action']['networkConnectionAction']['remoteIpDetails']['ipAddressV4']

    ec2 = boto3.client('ec2')

    # Add deny rule to NACL (use rule 90 = before allow rules)
    ec2.create_network_acl_entry(
        NetworkAclId='acl-12345',
        RuleNumber=90,
        Protocol='-1',
        RuleAction='deny',
        Egress=False,
        CidrBlock=f'{remote_ip}/32'
    )

    print(f"Blocked {remote_ip} via NACL")
```

---

## ⚖️ Comparison Table

|                | NACL                             | Security Group           |
| -------------- | -------------------------------- | ------------------------ |
| **Level**      | Subnet                           | Resource (ENI)           |
| **State**      | Stateless                        | Stateful                 |
| **Rules**      | Allow + Deny                     | Allow only               |
| **Evaluation** | First matching rule (ordered)    | All rules combined       |
| **Default**    | Allow all (default NACL)         | Deny all inbound         |
| **Good for**   | IP blocking, subnet segmentation | Normal resource firewall |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                      |
| ------------------------------------------- | ---------------------------------------------------------------------------- |
| "NACL and Security Group do the same thing" | NACLs: subnet/stateless/deny; SGs: resource/stateful/allow-only              |
| "Adding inbound rule is enough"             | Stateless: must add outbound ephemeral port rule too                         |
| "NACLs replace Security Groups"             | Complementary; use both for defense-in-depth                                 |
| "Default NACL is secure"                    | Default NACL allows ALL traffic (open); rely on Security Groups for security |

---

## 🔗 Related Keywords

- [Security Groups](/cloud-aws/security-groups/) — the primary, stateful per-resource firewall
- [VPC](/cloud-aws/vpc/) — NACLs are VPC components
- [Subnets (Public / Private)](/cloud-aws/subnets-public-private/) — one NACL per subnet

---

## 📌 Quick Reference Card

```bash
# List NACLs in VPC
aws ec2 describe-network-acls \
  --filters Name=vpc-id,Values=vpc-12345

# Create NACL
aws ec2 create-network-acl --vpc-id vpc-12345

# Add deny rule (inbound)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-12345 \
  --rule-number 90 \
  --protocol -1 \
  --rule-action deny \
  --ingress \
  --cidr-block 203.0.113.0/24

# Add allow rule (inbound HTTPS)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-12345 \
  --rule-number 100 \
  --protocol tcp \
  --rule-action allow \
  --ingress \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0

# Associate NACL with subnet
aws ec2 replace-network-acl-association \
  --association-id aclassoc-12345 \
  --network-acl-id acl-67890
```

---

## 🧠 Think About This

The most common NACL debugging issue is forgetting ephemeral ports. When your application in a subnet stops responding after adding a custom NACL, the culprit is almost always missing outbound rule for ports 1024-65535. Here's the flow: client sends TCP SYN to port 443 → hits your NACL inbound rule 100 (allow 443) → passes. Server responds from port 443 → return TCP ACK comes back TO the client's ephemeral port (e.g., 54321). But wait — from the server's subnet perspective, this is OUTBOUND traffic from port 443 to destination port 54321. Your NACL outbound rules must allow TCP 1024-65535 for these responses to leave the subnet. This is the most important operational difference between NACLs (stateless) and Security Groups (stateful) — and the most common source of mysterious connectivity failures.
