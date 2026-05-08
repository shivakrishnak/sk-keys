---
layout: default
title: "AWS PrivateLink"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /cloud-aws/aws-privatelink/
id: AWS-015
category: Cloud - AWS
difficulty: ★★★
depends_on: AWS VPC Architecture Deep Dive, AWS, Networking
used_by: Cloud - AWS
related: AWS VPC Architecture Deep Dive, VPC Peering, Transit Gateway
tags:
  - aws
  - cloud
  - networking
  - advanced
  - security
---

# AWS-015 - AWS PrivateLink

⚡ **TL;DR -** AWS PrivateLink exposes services privately inside a VPC via Elastic Network Interfaces - traffic never traverses the public internet or requires VPC peering.

| | |
|---|---|
| **Depends on** | AWS VPC Architecture Deep Dive, AWS, Networking |
| **Used by** | Cloud - AWS |
| **Related** | AWS VPC Architecture Deep Dive, VPC Peering, Transit Gateway |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your application in a private subnet needs to call the Secrets Manager API or connect to a partner SaaS. Traffic must leave the VPC, traverse the internet, and return. This requires a NAT Gateway or internet-facing resources - adding cost, latency, attack surface, and failing strict "no internet egress" compliance requirements.

**THE BREAKING POINT:** A financial services firm deploys to a VPC with no internet gateway (air-gapped by policy). Without PrivateLink, calling AWS APIs from EC2 instances or ECS tasks is impossible. Their compliance mandate says data must never leave the AWS backbone.

**THE INVENTION MOMENT:** AWS built PrivateLink to answer: what if you could call any AWS service API or consume any SaaS offering using only private IP addresses, with traffic staying entirely on the AWS network fabric?

---

### 📘 Textbook Definition

**AWS PrivateLink** is a networking technology that enables private connectivity between VPCs and AWS services, other AWS accounts' services, or third-party SaaS services using Elastic Network Interfaces (ENIs) with private IP addresses. Traffic flows over the AWS internal network fabric - never the public internet - and requires no internet gateway, NAT device, public IP address, or VPC peering relationship.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A private tunnel from your VPC to any service endpoint - traffic stays on AWS backbone, never touching the internet.

**One analogy:**
> PrivateLink is like adding a private door between two office buildings in the same corporate campus. Employees can walk directly between buildings without going outside, going through reception, or having their movements tracked by public security cameras.

**One insight:** From the consumer VPC's perspective, the remote service looks like a local ENI with a private IP address - DNS resolves to `10.x.x.x`, not `52.x.x.x`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Traffic between consumer VPC and service never leaves the AWS network.
2. The consumer VPC and service provider VPC never need to be peered or overlapping CIDR-resolved.
3. DNS resolution for the endpoint resolves to private IPs within the consumer VPC.
4. The service provider controls which consumers can connect via endpoint service permissions.

**DERIVED DESIGN:** AWS implements PrivateLink using an internal load balancer on the provider side (NLB) and an ENI in the consumer's subnet. The consumer creates a VPC Interface Endpoint pointing at the service. AWS provisions a private IP in the consumer's subnet. All traffic flows: consumer → ENI (private IP) → AWS backbone → NLB → service. No routing rules, no IGW, no NAT.

**THE TRADE-OFFS:**
**Gain:** No internet exposure, no CIDR overlap issues (unlike VPC Peering), one-directional access, scalable to thousands of consumers from one provider.
**Cost:** $0.01/hour per AZ endpoint + $0.01/GB data processed. Endpoints in each AZ for HA.

---

### 🧪 Thought Experiment

**SETUP:** A compliance-regulated workload runs in a VPC with no internet gateway. It needs to call the AWS Secrets Manager API to retrieve database credentials.

**WHAT HAPPENS WITHOUT PrivateLink:** The call to `secretsmanager.us-east-1.amazonaws.com` has no route. It resolves to a public IP. The VPC route table has no `0.0.0.0/0` entry. The packet is dropped. The application cannot start.

**WHAT HAPPENS WITH PrivateLink:** You create a VPC Interface Endpoint for `com.amazonaws.us-east-1.secretsmanager`. AWS provisions an ENI in your private subnet with IP `10.0.1.45`. DNS in your VPC now resolves `secretsmanager.us-east-1.amazonaws.com` to `10.0.1.45`. The API call succeeds. Traffic never leaves the AWS private backbone. Compliance audit passes.

**THE INSIGHT:** PrivateLink decouples "service accessibility" from "internet connectivity." A fully private VPC can still consume the full AWS API surface.

---

### 🧠 Mental Model / Analogy

> PrivateLink is like a pneumatic tube system between office floors. You put a message (API request) in the tube at your desk (consumer VPC). It travels through the building's internal infrastructure (AWS backbone) and arrives at the target department (service). No one outside the building ever sees it. The tube opening on your floor looks like a local desk - it has your building's address, not the target department's public address.

- **Your desk** = application in the consumer VPC
- **The tube opening** = ENI in your subnet (private IP)
- **Internal infrastructure** = AWS backbone (PrivateLink fabric)
- **Target department** = the service (Secrets Manager, S3, partner SaaS)
- **No one outside sees it** = no internet traversal

Where this analogy breaks down: pneumatic tubes are point-to-point; PrivateLink uses an NLB on the provider side to fan out to multiple service instances.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
PrivateLink creates a private connection between your cloud network and a service so your traffic never goes out to the internet. The service gets a private address inside your own network.

**Level 2 - How to use it (junior developer):**
In the VPC console, create an Interface Endpoint. Select the service (e.g., `com.amazonaws.us-east-1.secretsmanager`), choose your subnets, and attach a security group. AWS creates ENIs in those subnets. Enable private DNS so the service's public hostname resolves to the private ENI IP within your VPC.

**Level 3 - How it works (mid-level engineer):**
On the provider side, the endpoint service is backed by a Network Load Balancer. AWS creates an NLB in the service's VPC and registers a PrivateLink service ARN. On the consumer side, the Interface Endpoint creates an ENI per availability zone. Route 53 private hosted zone entries are injected so `*.amazonaws.com` resolves to the ENI IPs within the VPC. Security groups on the ENI control which resources can initiate connections.

**Level 4 - Why it was designed this way (senior/staff):**
The key design tension: VPC Peering solves private connectivity between two specific VPCs but requires non-overlapping CIDRs and has a many-to-many scaling problem (N peering relationships for N consumers). PrivateLink solves both: providers expose a single service endpoint; consumers attach independently. Overlapping CIDRs don't matter because no routing relationship is established - only the ENI's private IP is relevant. This is architecturally similar to a service mesh proxy pattern at the network level.

---

### ⚙️ How It Works (Mechanism)

1. **Provider setup** - create a Network Load Balancer (NLB) fronting the service. Create an Endpoint Service from the NLB. Allowlist consumer AWS account IDs.
2. **Consumer setup** - create a VPC Interface Endpoint targeting the service name. Select subnets (one per AZ for HA). Attach a security group. Enable private DNS.
3. **ENI provisioning** - AWS creates one ENI per AZ in the selected subnets. Each ENI gets a private IP from the subnet CIDR.
4. **DNS injection** - when private DNS is enabled, Route 53 Resolver in the VPC overrides the service's public DNS record with the private ENI IPs.
5. **Traffic flow** - application resolves service hostname → private IP → traffic routes to ENI → AWS backbone → NLB → service instance.
6. **Security groups** - control inbound to the ENI (which resources in the VPC can use the endpoint). The security group acts as the perimeter on the consumer side.
7. **Gateway Endpoints** - for S3 and DynamoDB, AWS offers gateway endpoints (free, route-table-based) instead of interface endpoints. Different mechanism, same "no internet" result.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Consumer VPC (10.0.0.0/16)
  App Instance (10.0.1.10)
       |
       | DNS: secretsmanager.us-east-1.amazonaws.com
       |      resolves to 10.0.1.45 (ENI)
       |
       v
  ENI (10.0.1.45)  ← YOU ARE HERE
  [Security Group: allow 443 from 10.0.1.0/24]
       |
       | AWS Private Backbone (no internet)
       |
       v
  NLB (Provider VPC / AWS Service VPC)
       |
       v
  Service Fleet (Secrets Manager / SaaS)
```

**FAILURE PATH:**
- Security group on ENI blocks port 443 → connection timeout from app
- Private DNS disabled → hostname resolves to public IP, traffic fails in private subnet
- Consumer account not allow-listed on endpoint service → endpoint stuck in `pendingAcceptance`

**WHAT CHANGES AT SCALE:**
Deploy Interface Endpoints in every AZ where workloads run to avoid cross-AZ data transfer fees ($0.01/GB). Use AWS Config rule `vpc-endpoint-exists` to enforce endpoint presence across all regulated VPCs in the organisation.

---

### 💻 Code Example

**AWS CLI - create an Interface Endpoint for Secrets Manager:**
```bash
# Get the VPC and subnet IDs
VPC_ID=vpc-0abc1234
SUBNET_IDS="subnet-111 subnet-222 subnet-333"
SG_ID=sg-0def5678

# Create Interface Endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --vpc-endpoint-type Interface \
  --service-name \
    com.amazonaws.us-east-1.secretsmanager \
  --subnet-ids $SUBNET_IDS \
  --security-group-ids $SG_ID \
  --private-dns-enabled \
  --tag-specifications \
    'ResourceType=vpc-endpoint,Tags=[
      {Key=Name,Value=secrets-manager-endpoint}
    ]'

# Verify DNS is resolving to private IP
aws ec2 describe-vpc-endpoints \
  --filters Name=vpc-id,Values=$VPC_ID \
  --query \
    'VpcEndpoints[*].DnsEntries[*].DnsName'
```

**AWS CDK - Interface Endpoint with private DNS:**
```typescript
import * as ec2 from 'aws-cdk-lib/aws-ec2';

const vpc = new ec2.Vpc(this, 'AppVpc', {
  maxAzs: 3,
  natGateways: 0  // fully private
});

// Interface endpoint for Secrets Manager
vpc.addInterfaceEndpoint('SecretsManagerEp', {
  service: ec2.InterfaceVpcEndpointAwsService
    .SECRETS_MANAGER,
  privateDnsEnabled: true,
  subnets: {
    subnetType: ec2.SubnetType.PRIVATE_ISOLATED
  }
});

// Gateway endpoint for S3 (free)
vpc.addGatewayEndpoint('S3Ep', {
  service: ec2.GatewayVpcEndpointAwsService.S3
});
```

**Expose a custom service via PrivateLink (CDK):**
```typescript
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';

// Provider side: NLB + Endpoint Service
const nlb = new elbv2.NetworkLoadBalancer(
  this, 'ServiceNLB', {
    vpc,
    internetFacing: false
  }
);

const endpointService =
  new ec2.VpcEndpointService(this, 'EpService', {
    vpcEndpointServiceLoadBalancers: [nlb],
    acceptanceRequired: true,
    allowedPrincipals: [
      new iam.ArnPrincipal(
        'arn:aws:iam::CONSUMER_ACCT:root'
      )
    ]
  });
```

---

### ⚖️ Comparison Table

| Feature | PrivateLink (Interface EP) | VPC Peering | Transit Gateway | Gateway Endpoint |
|---|---|---|---|---|
| **Traffic path** | AWS backbone | AWS backbone | AWS backbone | AWS backbone |
| **CIDR overlap** | Not an issue | Breaks routing | Not an issue | Not an issue |
| **Direction** | One-way (consumer → service) | Bidirectional | Bidirectional | One-way |
| **Services** | Any NLB-backed service | VPC-to-VPC | Hub-spoke VPCs | S3 / DynamoDB only |
| **Cost** | $0.01/hr/AZ + data | Free (data fees apply) | $0.05/hr + data | Free |
| **Cross-account** | Yes | Yes | Yes | No |
| **DNS override** | Yes (private DNS) | Manual | Manual | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "PrivateLink requires VPC peering" | PrivateLink explicitly replaces the need for VPC peering. CIDRs can overlap and no peering relationship is needed. |
| "Gateway Endpoints and Interface Endpoints are the same" | Gateway Endpoints (S3, DynamoDB) are route-table-based and free. Interface Endpoints use ENIs, cost $0.01/hr/AZ, and support any NLB-backed service. |
| "Enabling PrivateLink means no security group is needed" | A security group must be attached to the ENI. Without explicit allow rules, traffic is blocked by default. |
| "Private DNS always works across all VPCs" | Private DNS resolution only works within the VPC where the endpoint is created, unless Route 53 Resolver rules are configured to forward queries from other VPCs. |
| "PrivateLink traffic is free" | Interface Endpoints cost $0.01/hour per AZ and $0.01/GB data processed. Only Gateway Endpoints (S3/DynamoDB) are free. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Connection timeout calling AWS API from private subnet**
**Symptom:** App in private subnet (no NAT) gets connection timeouts on AWS API calls. No error - just timeout.
**Root Cause:** No Interface Endpoint for the service. Hostname resolves to public IP. No route to internet.
**Diagnostic:**
```bash
# On the EC2 instance, check DNS resolution
nslookup secretsmanager.us-east-1.amazonaws.com
# If returning 52.x.x.x → public IP → no endpoint

# Check if endpoint exists
aws ec2 describe-vpc-endpoints \
  --filters \
    Name=vpc-id,Values=vpc-0abc \
    Name=service-name,Values=\
com.amazonaws.us-east-1.secretsmanager \
  --query 'VpcEndpoints[*].State'
```
**Fix:** Create an Interface Endpoint for the missing service in the VPC.
**Prevention:** Use an AWS Config rule or Service Control Policy to require Interface Endpoints for all regulated services before workloads deploy.

**Mode 2: Endpoint stuck in pendingAcceptance**
**Symptom:** Consumer creates endpoint targeting a custom endpoint service; state stays `pendingAcceptance` indefinitely.
**Root Cause:** Provider's endpoint service has `AcceptanceRequired=true` and no one approved the connection.
**Diagnostic:**
```bash
# Provider: list pending connections
aws ec2 describe-vpc-endpoint-connections \
  --filters \
    Name=vpc-endpoint-service-id,\
Values=vpce-svc-0abc \
  --query \
    'VpcEndpointConnections[?State==`pendingAcceptance`]'

# Accept the connection
aws ec2 accept-vpc-endpoint-connections \
  --service-id vpce-svc-0abc \
  --vpc-endpoint-ids vpce-111
```
**Fix:** Accept the connection on the provider side or set `AcceptanceRequired=false` for trusted consumers.
**Prevention:** Automate acceptance via EventBridge rule triggering a Lambda to approve known consumer account IDs.

**Mode 3: DNS resolves to public IP inside VPC**
**Symptom:** Application in VPC with an Interface Endpoint still connects via public IP; traffic leaves VPC; compliance fails.
**Root Cause:** Private DNS was not enabled on the endpoint, or `enableDnsHostnames`/`enableDnsSupport` not set on the VPC.
**Diagnostic:**
```bash
# Check VPC DNS settings
aws ec2 describe-vpc-attribute \
  --vpc-id vpc-0abc \
  --attribute enableDnsHostnames
aws ec2 describe-vpc-attribute \
  --vpc-id vpc-0abc \
  --attribute enableDnsSupport

# Check endpoint private DNS setting
aws ec2 describe-vpc-endpoints \
  --query \
    'VpcEndpoints[*].PrivateDnsEnabled'
```
**Fix:** Enable `enableDnsHostnames` and `enableDnsSupport` on the VPC. Recreate the endpoint with `--private-dns-enabled`.
**Prevention:** Enforce VPC DNS settings via CloudFormation/CDK baseline template. Include endpoint DNS verification in deployment pipeline.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- AWS VPC Architecture Deep Dive - PrivateLink operates within VPC constructs; subnets, route tables, and security groups must be understood first.
- Networking - DNS resolution, TCP/IP routing, and NAT concepts are required to diagnose PrivateLink issues.
- AWS IAM - Interface Endpoints can have endpoint policies limiting which IAM principals can use them.

**Builds On This (learn these next):**
- AWS Secrets Manager - frequently accessed via PrivateLink Interface Endpoint in regulated environments.
- AWS ECS / Fargate - Fargate tasks in private subnets require PrivateLink endpoints for ECR, Secrets Manager, and CloudWatch Logs.
- AWS VPC Architecture Deep Dive - design patterns for multi-AZ endpoint deployment and shared endpoint VPC architecture.

**Alternatives / Comparisons:**
- VPC Peering - bidirectional private connectivity between two VPCs; requires non-overlapping CIDRs; does not solve AWS service access.
- Transit Gateway - hub-and-spoke model for many VPCs; PrivateLink is more appropriate for service exposure than VPC interconnection.
- NAT Gateway - provides internet access from private subnets; PrivateLink eliminates the need for NAT for AWS service calls.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Private connectivity to services   |
|                  | via ENI; traffic stays on AWS net  |
| PROBLEM IT SOLVES| Internet exposure for AWS APIs,    |
|                  | NAT cost, compliance "no-egress"    |
| KEY INSIGHT      | Service gets a private IP in your  |
|                  | VPC; no routing/peering needed      |
| USE WHEN         | Private subnets needing AWS APIs,  |
|                  | SaaS, cross-account services        |
| AVOID WHEN       | VPC-to-VPC full routing (use TGW); |
|                  | S3/DynamoDB (use Gateway EP free)   |
| TRADE-OFF        | $0.01/hr/AZ + data vs internet     |
|                  | exposure and NAT Gateway cost       |
| ONE-LINER        | ec2:CreateVpcEndpoint (Interface)  |
| NEXT EXPLORE     | VPC Architecture, Transit Gateway  |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A shared services VPC hosts a single Interface Endpoint for Secrets Manager. Twenty spoke VPCs need to use it without deploying endpoints in each VPC. What AWS networking construct enables this, and what Route 53 configuration is required to make DNS resolution work from spoke VPCs?

2. **(Scale)** Your organisation has 150 VPCs across 3 regions. Each VPC needs Interface Endpoints for 8 AWS services across 3 AZs. At $0.01/hr/AZ/endpoint, calculate the monthly endpoint cost, and describe the architectural pattern that reduces this cost while maintaining isolation between workloads.

3. **(Design Trade-off)** PrivateLink interface endpoints and Gateway Endpoints both keep traffic on the AWS backbone. Why does AWS charge for interface endpoints but not gateway endpoints? What does this difference reveal about the underlying infrastructure cost model?
