---
version: 2
layout: default
title: "AWS VPC Architecture Deep Dive"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 22
permalink: /cloud-aws/aws-vpc-architecture/
id: AWS-022
category: Cloud - AWS
difficulty: ★★★
depends_on: Networking, AWS, Subnets
used_by: AWS PrivateLink, Cloud - AWS
related: AWS PrivateLink, Security Groups, NAT Gateway
tags:
  - aws
  - cloud
  - networking
  - advanced
  - architecture
---

# AWS-022 - AWS VPC Architecture Deep Dive

⚡ **TL;DR -** A VPC is your private, isolated network within AWS - you control the IP ranges, subnets, routing, and network boundaries that determine what your resources can reach and who can reach them.

| | |
|---|---|
| **Depends on** | Networking, AWS, Subnets |
| **Used by** | AWS PrivateLink, Cloud - AWS |
| **Related** | AWS PrivateLink, Security Groups, NAT Gateway |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Without network isolation, every AWS resource you create is on a shared flat network reachable by default. Your production database is on the same network as your web servers and your development laptops. A compromised web server can directly connect to the production database. There is no network perimeter.

**THE BREAKING POINT:** In a shared flat network, lateral movement after an initial compromise is trivial. Modern security frameworks (CIS, NIST, PCI DSS) require network segmentation as a foundational control. A database in the same subnet as a public-facing web server fails every compliance audit.

**THE INVENTION MOMENT:** AWS VPC answered: what if every customer got a logically isolated network within AWS where they control routing, IP addressing, and internet access - exactly as they would in an on-premises data centre?

---

### 📘 Textbook Definition

**Amazon VPC (Virtual Private Cloud)** is a logically isolated virtual network within AWS that resembles a traditional data centre network. You define the **IPv4 CIDR block**, subdivide it into **subnets** across Availability Zones, control traffic routing via **route tables**, restrict traffic with **Security Groups** (stateful) and **Network ACLs** (stateless), and control internet access via **Internet Gateway** (public access) and **NAT Gateway** (outbound-only for private subnets). **VPC Flow Logs** capture all traffic metadata for auditing and troubleshooting.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Your private, programmable data centre network inside AWS - you define the address space, routing, and access rules.

**One analogy:**
> A VPC is like a private office building with a dedicated phone system, locked floors, and a security desk. The building (VPC) has its own address system (CIDR). Some floors are accessible to visitors (public subnets). Other floors require an employee escort (private subnets). The security desk (security groups) checks every visitor. The receptionist (NAT gateway) can make outbound calls from private floors without giving out their direct extension.

**One insight:** Subnet placement is the first - and most important - network security decision. A resource in a private subnet is unreachable from the internet regardless of security group settings.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A VPC is a flat Layer 3 network - every resource within it is L3-reachable from any other resource in the same VPC by default (unless Security Groups block it).
2. A subnet is a contiguous IP range within the VPC, scoped to one AZ. Subnet placement determines internet accessibility.
3. Route tables are per-subnet; they determine where packets go based on destination CIDR.
4. Security Groups are stateful firewalls on ENIs; NACLs are stateless firewalls on subnet boundaries.

**DERIVED DESIGN:** The three-tier architecture maps directly to three subnet types: public (ALB, NAT Gateway - has route to IGW), private (app servers, ECS tasks - NAT Gateway route for egress), isolated (databases - no internet route at all). Defense in depth: even if the public subnet is compromised, the isolated subnet has no route to an attacker's C2 server.

**THE TRADE-OFFS:**
**Gain:** Complete network isolation, custom IP addressing, compliance-ready segmentation, flexible peering.
**Cost:** VPC design complexity scales with architecture size; NAT Gateway costs $0.045/hr + $0.045/GB processed; VPC peering/TGW for multi-VPC adds routing complexity.

---

### 🧪 Thought Experiment

**SETUP:** You deploy a three-tier app (ALB → EC2 app servers → RDS). All three are in the same public subnet.

**WHAT HAPPENS:** A SQL injection vulnerability in the app server allows command execution. The attacker opens a reverse shell. From the EC2 instance, they connect directly to `db.internal:5432` - same subnet, no routing barrier. They dump the database. The ALB security group is irrelevant because the database is in the same flat subnet.

**WHAT HAPPENS WITH PROPER VPC DESIGN:** ALB in public subnet (CIDR: `10.0.1.0/24`). App servers in private subnet (CIDR: `10.0.2.0/24`). RDS in isolated subnet (CIDR: `10.0.3.0/24`). Security Group on RDS allows port 5432 only from the app server Security Group. Even after the app server is compromised, the attacker can reach RDS - but RDS has no internet route, so exfiltrating data requires going through the compromised app server, which is logged and alarmed.

**THE INSIGHT:** Network segmentation doesn't prevent lateral movement in the same subnet - it limits blast radius. Proper subnet design reduces the number of paths an attacker can take after initial compromise.

---

### 🧠 Mental Model / Analogy

> A VPC is like a multi-floor office building with strict access controls. The ground floor (public subnet) has a reception area anyone can enter. Upper floors (private subnets) require keycard access (security group allow rules). The basement vault (isolated subnet) requires two-person authorisation and has no external phone lines. The lobby phone (NAT Gateway) allows people in private offices to make outgoing calls without revealing their internal extension.

- **Building** = VPC (10.0.0.0/16)
- **Ground floor** = public subnet (IGW route)
- **Upper floors** = private subnets (NAT route)
- **Basement vault** = isolated subnets (no internet route)
- **Keycard** = Security Group allow rule
- **Lobby phone** = NAT Gateway
- **Floor map** = route table

Where this analogy breaks down: a real building has a single physical security model; a VPC Security Group is per-ENI (per network card), allowing different rules for different resources on the same floor (subnet).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A VPC is a private, isolated network in AWS where you put your servers and databases. You control who can talk to what - like having your own private section of the internet that only your cloud resources can use.

**Level 2 - How to use it (junior developer):**
Create a VPC with a CIDR block (e.g., `10.0.0.0/16`). Create public subnets (with an Internet Gateway route) for load balancers. Create private subnets (with a NAT Gateway route) for application servers. Create isolated subnets (no internet route) for databases. Apply Security Groups to each resource type to allow only necessary traffic.

**Level 3 - How it works (mid-level engineer):**
Route tables determine packet destination. A public subnet has a route: `0.0.0.0/0 → igw-xxx`. A private subnet has: `0.0.0.0/0 → nat-xxx`. An isolated subnet has no `0.0.0.0/0` route - any packet destined for an unknown IP is dropped. Security Groups operate at the ENI level - stateful (established connections are automatically allowed for return traffic). NACLs operate at the subnet boundary - stateless (must explicitly allow both inbound AND outbound for each traffic flow, including ephemeral port ranges).

**Level 4 - Why it was designed this way (senior/staff):**
The Security Group stateful model vs NACL stateless model reflects two different threat models at different layers. Security Groups operating at the ENI level solve the problem of resource-level microsegmentation - two EC2 instances in the same subnet can have completely different effective firewall rules. NACLs operating at the subnet boundary solve the problem of subnet-level emergency blocking - a compromised subnet can be isolated at the network level without touching individual security groups. The two-tier firewall design (SGS + NACLs) provides defense in depth: a misconfigured SG can be caught by a NACL, and vice versa. This mirrors the defense-in-depth principle in physical security - multiple independent barriers.

---

### ⚙️ How It Works (Mechanism)

1. **VPC CIDR** - the address space for the entire VPC (e.g., `10.0.0.0/16` = 65,536 addresses). Cannot be changed after creation; plan carefully.
2. **Subnets** - contiguous IP ranges within the VPC CIDR, scoped to one AZ. AWS reserves 5 IPs per subnet (first 4 + last).
3. **Internet Gateway (IGW)** - attaches to the VPC. Enables bidirectional internet connectivity for resources with public IPs in public subnets.
4. **NAT Gateway** - deployed in a public subnet. Translates outbound traffic from private subnet resources to the NAT's public IP. No inbound connections allowed (stateful NAT, not full bidirectional).
5. **Route tables** - one per subnet (or shared). Entries: `local` route (all traffic within VPC CIDR) is implicit. Additional entries route traffic to IGW, NAT, TGW, VPC endpoints, etc.
6. **Security Groups (SGs)** - stateful ENI-level firewalls. Allow rules only (no deny). Evaluated on all inbound + outbound traffic. Return traffic for established connections auto-allowed.
7. **Network ACLs (NACLs)** - stateless subnet-level firewalls. Allow and deny rules. Rules evaluated in number order (lowest first). Must explicitly allow ephemeral ports (1024–65535) for return traffic.
8. **VPC Flow Logs** - capture L3/L4 metadata (src IP, dst IP, port, protocol, bytes, action) for all ENIs in the VPC. Published to CloudWatch Logs, S3, or Kinesis Firehose.
9. **VPC Endpoints** - gateway endpoints (S3, DynamoDB) and interface endpoints (PrivateLink) for private service access.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (3-tier architecture, single AZ shown):**
```
Internet
  |
  | TCP:443 to ALB public IP
  v
Internet Gateway (igw-001)
  |
  | Route: 0.0.0.0/0 → igw-001
  v
Public Subnet 10.0.1.0/24    AZ: us-east-1a
  ALB (10.0.1.10)  ← YOU ARE HERE
  NAT GW (10.0.1.20) [for private egress]
  |
  | SG: allow :8080 from ALB SG
  v
Private Subnet 10.0.2.0/24
  ECS Task (10.0.2.50)
  [Route: 0.0.0.0/0 → nat-001]
  |
  | SG: allow :5432 from App SG
  v
Isolated Subnet 10.0.3.0/24
  RDS (10.0.3.100)
  [No 0.0.0.0/0 route - internet unreachable]
```

**FAILURE PATH:**
- Missing NAT Gateway → private subnet tasks cannot reach internet (ECR, Secrets Manager) unless VPC endpoints exist
- NACL blocking ephemeral ports → established TCP connections silently fail (SG shows allowed but NACLs drop returns)
- VPC CIDR overlap during peering → `InvalidVpcPeeringConnectionId.NotFound`

**WHAT CHANGES AT SCALE:**
Multi-VPC design: hub-spoke with Transit Gateway (TGW). Shared VPC (Resource Access Manager) for centralised networking with workload accounts as consumers. NAT Gateway per-AZ (not shared) to avoid cross-AZ data transfer charges. VPC endpoints for all AWS services used at scale.

---

### 💻 Code Example

**AWS CDK - full 3-tier VPC:**
```typescript
import * as ec2 from 'aws-cdk-lib/aws-ec2';

const vpc = new ec2.Vpc(this, 'AppVpc', {
  cidr: '10.0.0.0/16',
  maxAzs: 3,
  natGateways: 3, // one per AZ for HA
  subnetConfiguration: [
    {
      cidrMask: 24,
      name: 'Public',
      subnetType: ec2.SubnetType.PUBLIC
    },
    {
      cidrMask: 24,
      name: 'Private',
      subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS
    },
    {
      cidrMask: 28,
      name: 'Isolated',
      subnetType: ec2.SubnetType.PRIVATE_ISOLATED
    }
  ]
});

// VPC Flow Logs to CloudWatch
vpc.addFlowLog('VpcFlowLog', {
  trafficType: ec2.FlowLogTrafficType.REJECT,
  destination: ec2.FlowLogDestination.toCloudWatchLogs()
});

// Security Group for RDS - only from app SG
const appSg = new ec2.SecurityGroup(
  this, 'AppSG', { vpc }
);
const rdsSg = new ec2.SecurityGroup(
  this, 'RDSSG', { vpc, allowAllOutbound: false }
);
rdsSg.addIngressRule(
  appSg,
  ec2.Port.tcp(5432),
  'Allow PostgreSQL from app tier'
);
```

**AWS CLI - VPC diagnostic commands:**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications \
    'ResourceType=vpc,Tags=[{Key=Name,Value=AppVPC}]'

# Enable DNS resolution
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-0abc \
  --enable-dns-hostnames

# Create and attach Internet Gateway
IGW=$(aws ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW \
  --vpc-id vpc-0abc

# Add route to public route table
aws ec2 create-route \
  --route-table-id rtb-public \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW

# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-0abc \
  --traffic-type REJECT \
  --log-destination-type cloud-watch-logs \
  --log-group-name /vpc/flow-logs \
  --deliver-logs-permission-arn \
    arn:aws:iam::123:role/FlowLogRole
```

---

### ⚖️ Comparison Table

| Feature | Security Groups | Network ACLs | AWS WAF | AWS Shield |
|---|---|---|---|---|
| **OSI Layer** | L4 (TCP/UDP) | L3/L4 | L7 (HTTP) | L3/L4/L7 |
| **State** | Stateful | Stateless | Stateful | Stateful |
| **Applied to** | ENI (resource) | Subnet boundary | CloudFront/ALB | Edge/resource |
| **Default action** | Deny all | Allow all | Allow | Allow |
| **Rules** | Allow only | Allow + Deny | Allow + Block | Automatic |
| **Rule evaluation** | All rules (union) | In numeric order | Priority order | N/A |
| **Use case** | Resource-level control | Emergency subnet block | L7 application attacks | DDoS mitigation |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A resource in a private subnet is completely unreachable" | Resources in private subnets are reachable from within the VPC (other EC2 instances, Lambda in same VPC, etc.) via Security Group rules. "Private" means no direct internet route, not no internal route. |
| "Security Groups and NACLs do the same thing" | Security Groups are stateful (per-ENI, return traffic auto-allowed). NACLs are stateless (per-subnet, must explicitly allow return traffic including ephemeral ports 1024–65535). |
| "Larger VPC CIDR is always better" | VPC CIDR cannot be changed. A /16 gives 65K IPs. A /24 gives 256. But CIDR overlap with corporate on-premises ranges or peered VPCs causes routing failures. Plan CIDR ranges across the organisation before creating VPCs. |
| "Multiple Security Groups on one ENI are combined with AND logic" | Multiple Security Groups on one ENI are combined with OR logic (union). If any SG allows the traffic, it is allowed. There is no way to implement deny logic with SGs alone. |
| "NACLs provide better security than Security Groups" | NACLs are coarser (subnet-level) and stateless (error-prone). Security Groups are finer (ENI-level) and stateful (easier to configure correctly). Most security is best implemented via Security Groups; NACLs are for emergency subnet-level controls. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: NACL blocking return traffic - silent TCP failures**
**Symptom:** EC2 instance in private subnet can initiate connections but they hang after the 3-way handshake. Connections to internet endpoints fail silently.
**Root Cause:** NACL allows outbound TCP on port 443 but doesn't allow inbound ephemeral ports (1024–65535) for the return traffic. Since NACLs are stateless, return packets are dropped.
**Diagnostic:**
```bash
# Check VPC Flow Logs for REJECT actions
aws logs filter-log-events \
  --log-group-name /vpc/flow-logs \
  --filter-pattern \
    '[version, account, eni, src, dst, srcport,
      dstport, protocol, packets, bytes, start,
      end, action=REJECT, status]' \
  --query 'events[*].message' | head -20

# Check NACL rules
aws ec2 describe-network-acls \
  --filters Name=association.subnet-id,\
Values=subnet-private \
  --query \
    'NetworkAcls[*].Entries[?RuleAction==`deny`]'
```
**Fix:** Add NACL inbound rule to allow TCP ports 1024–65535 from `0.0.0.0/0` for return traffic from internet. Or remove the NACL restrictions and rely on Security Groups.
**Prevention:** Default VPC NACL allows all traffic - only add NACL rules when you have a specific deny requirement. Use Security Groups for all allow/deny logic; use NACLs only for emergency subnet-level blocks.

**Mode 2: CIDR overlap prevents VPC peering**
**Symptom:** Attempting to create VPC Peering between two VPCs fails with `InvalidVpcPeeringConnectionId` or routing works but traffic is misdirected.
**Root Cause:** Both VPCs use the same CIDR range (e.g., both use `10.0.0.0/16`). AWS cannot route between them because the destination CIDR is ambiguous.
**Diagnostic:**
```bash
# Check CIDR of all VPCs in the account
aws ec2 describe-vpcs \
  --query 'Vpcs[*].[VpcId,CidrBlock,Tags]' \
  --output table

# Check peering connection status
aws ec2 describe-vpc-peering-connections \
  --query \
    'VpcPeeringConnections[*].[
      VpcPeeringConnectionId,
      Status.Code,
      RequesterVpcInfo.CidrBlock,
      AccepterVpcInfo.CidrBlock
    ]'
```
**Fix:** Peering with overlapping CIDRs is impossible - VPCs must be recreated with non-overlapping CIDRs. Use PrivateLink or Transit Gateway (which doesn't require non-overlapping CIDRs for service access) as alternatives.
**Prevention:** Maintain a CIDR allocation registry at the organisation level. Use different /8 or /10 ranges per environment (10.0.0.0/8 = prod, 172.16.0.0/12 = dev). Use an IPAM solution (AWS VPC IPAM) for automated allocation.

**Mode 3: NAT Gateway bandwidth bottleneck**
**Symptom:** Data transfer from private subnet to S3 (or internet) is slow; high NAT Gateway data processing charges.
**Root Cause:** All egress traffic routing through a single NAT Gateway in one AZ. High-bandwidth workloads saturate NAT. Cross-AZ NAT traffic also incurs data transfer charges.
**Diagnostic:**
```bash
# Check NAT Gateway bandwidth metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/NatGateway \
  --metric-name BytesOutToDestination \
  --dimensions \
    Name=NatGatewayId,Value=nat-0abc \
  --period 300 \
  --statistics Sum \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```
**Fix:** Deploy NAT Gateways in each AZ and configure private subnets in each AZ to use their local NAT Gateway (eliminates cross-AZ traffic charges). For S3 and DynamoDB traffic, use Gateway Endpoints (free, no NAT traversal).
**Prevention:** Always create one NAT Gateway per AZ. Add S3 and DynamoDB Gateway Endpoints to all VPCs to eliminate NAT charges for those services.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Networking - understand TCP/IP, CIDR notation, subnetting, routing, and stateful vs stateless firewalls before VPC concepts make sense.
- AWS (core) - understanding AWS regions and Availability Zones is prerequisite for multi-AZ VPC subnet design.
- Subnets - CIDR subnetting math (calculating subnet ranges, available hosts, broadcast addresses) is required for VPC design.

**Builds On This (learn these next):**
- AWS PrivateLink - use interface endpoints to access AWS services and custom SaaS from private/isolated subnets without internet routes.
- AWS Transit Gateway - hub-spoke VPC connectivity model for organisations with many VPCs needing full-mesh routing.
- Security Groups - VPC is the foundation; Security Group design is the primary tool for implementing least-privilege access within the VPC.

**Alternatives / Comparisons:**
- GCP VPC - Google's equivalent; global by default (one VPC spans all regions), while AWS VPC is regional. Different subnet and routing model.
- Azure VNet - Microsoft's virtual network equivalent; similar subnet and NSG concepts with different CIDR and peering implementation.
- On-premises VLAN - traditional network segmentation; VPC mirrors this model but with software-defined networking and API-driven configuration.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Isolated AWS virtual network;      |
|                  | custom CIDR, subnets, routing, SGs  |
| PROBLEM IT SOLVES| Flat shared network, no isolation, |
|                  | no network perimeter around data    |
| KEY INSIGHT      | Subnet = first security boundary;  |
|                  | private subnet = no internet route  |
| USE WHEN         | All AWS workloads - VPC is the     |
|                  | mandatory network foundation        |
| AVOID WHEN       | Default VPC for production (design |
|                  | a custom VPC with proper segmentation)|
| TRADE-OFF        | Design complexity + NAT costs vs   |
|                  | proper isolation and compliance      |
| ONE-LINER        | ec2:CreateVpc + 3-tier subnets     |
| NEXT EXPLORE     | PrivateLink, TGW, VPC IPAM         |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** Security Groups and NACLs are both firewalls in a VPC, but their statefulness differs fundamentally. A Security Group automatically allows return traffic for established connections; a NACL does not. What does this mean for the inbound NACL rule requirements when a private subnet host initiates an HTTPS connection to the internet - and why does forgetting this cause intermittent failures rather than consistent failures?

2. **(Design Trade-off)** You need to design a VPC CIDR strategy for an organisation with 3 AWS accounts (prod, staging, dev), 3 regions (us-east-1, eu-west-1, ap-southeast-1), and a requirement to peer all environments with an on-premises network using `192.168.0.0/16`. What CIDR allocation scheme prevents overlap across all current and future VPCs, and how many /16 blocks do you need to reserve?

3. **(Scale)** A microservices architecture has 50 services in private subnets. Each service needs to call AWS APIs (Secrets Manager, S3, CloudWatch, ECR, STS). Currently all traffic routes through 3 NAT Gateways costing $4,000/month. What combination of VPC endpoints eliminates the majority of this cost, and what monitoring would you put in place to validate the reduction?
