---
id: NET-075
title: "Build a Secure Network Platform - Phase 3"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★★
depends_on: NET-071, NET-072, NET-073, NET-074
used_by: NET-083
related: NET-071, NET-072, NET-073, NET-074, NET-083
tags:
  - networking
  - platform
  - capstone
  - design
  - security
  - production
  - end-to-end
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 75
permalink: /technical-mastery/net/build-a-secure-network-platform/
---

**⚡ TL;DR** - This capstone integrates every major networking
concept into a production-grade secure network platform
design. The scenario: design the complete network layer
for a payment processing company with 50 microservices,
3 regions, PCI-DSS compliance, and a 99.99% uptime SLA.
The design covers: VPC layout, Transit Gateway, zero trust
with service mesh, DDoS protection, rate limiting,
observability, DR, and the Terraform structure to
implement it. This is the output you'd deliver at a
staff/principal level design review.

| #075 | Category: Networking | Difficulty: ★★★★★ |
|:---|:---|:---|
| **Depends on:** | Network-as-Code (NET-071), Service Mesh Adoption (NET-072), Traffic Engineering (NET-073), Decision Framework (NET-074) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | Network-as-Code, Service Mesh Adoption, Traffic Engineering, Decision Framework, Networking Career Paths | |

---

### 🔥 The Design Brief

```
Company: FinPay (fictional payments processor)
Scale: 50 microservices, 500 engineers
Regions: 3 (us-east-1, eu-west-1, ap-southeast-1)
Traffic: 10,000 TPS peak, $2M/day in transactions
Compliance: PCI-DSS level 1 (card data)
SLA: 99.99% uptime = 52 minutes downtime/year
Security requirements:
  - No direct internet access to any backend service
  - All service-to-service calls: mutual TLS
  - Card data: never leaves compliant zones
  - All network changes: auditable via code review
  
Constraints:
  - Existing monolith being migrated to microservices
  - Some services still on EC2 (not yet Kubernetes)
  - 3 teams: core payments, auth, analytics
```

---

### ⚙️ Phase 1 - VPC and Network Foundation

**Architecture diagram:**

```
+------------------------------------------------------+
|                  FINPAY NETWORK (US-EAST-1)          |
|                                                      |
|  +------------+  +------------+  +------------+     |
|  | AZ-1a      |  | AZ-1b      |  | AZ-1c      |     |
|  |            |  |            |  |            |     |
|  | [Public]   |  | [Public]   |  | [Public]   |     |
|  | ALB/WAF    |  | ALB/WAF    |  | ALB/WAF    |     |
|  | NAT GW     |  | NAT GW     |  | NAT GW     |     |
|  |            |  |            |  |            |     |
|  | [Private]  |  | [Private]  |  | [Private]  |     |
|  | App svcs   |  | App svcs   |  | App svcs   |     |
|  | K8s nodes  |  | K8s nodes  |  | K8s nodes  |     |
|  |            |  |            |  |            |     |
|  | [CDE]      |  | [CDE]      |  | [CDE]      |     |
|  | Payment    |  | Payment    |  | Payment    |     |
|  | Card svc   |  | Card svc   |  | Card svc   |     |
|  |            |  |            |  |            |     |
|  | [DB]       |  | [DB]       |  | [DB]       |     |
|  | RDS/Redis  |  | RDS/Redis  |  | RDS/Redis  |     |
|  +------------+  +------------+  +------------+     |
+------------------------------------------------------+

CDE VPC (separate - PCI-DSS isolated)
+------------------------------------------------------+
|  Card data environment: only payment + card services |
|  Separate VPC, separate security controls            |
|  TGW attachment with strict routing rules            |
+------------------------------------------------------+
```

```
flowchart TB
    Internet --> WAF
    WAF --> ALB
    ALB --> AppServers
    AppServers --> DB
    AppServers --> CDE_VPC
    CDE_VPC --> CardDB
    AppServers --> TGW
    TGW --> EU_VPC
    TGW --> AP_VPC
    style CDE_VPC fill:#f66
    style CardDB fill:#f66
```

**CIDR allocation:**

```
FinPay CIDR allocation (committed in code):

us-east-1:
  10.0.0.0/16  - main VPC (app, public, db)
  10.5.0.0/16  - CDE VPC (card data)
  
eu-west-1:
  10.1.0.0/16  - main VPC
  10.6.0.0/16  - CDE VPC
  
ap-southeast-1:
  10.2.0.0/16  - main VPC
  10.7.0.0/16  - CDE VPC
  
Staging (us-east-1 only):
  10.10.0.0/16 - staging main VPC
  
Subnet layout per VPC:
  Public:   /22 per AZ (1,022 hosts × 3 AZs)
  Private:  /21 per AZ (2,046 hosts × 3 AZs)
  CDE:      /23 per AZ (510 hosts × 3 AZs)
  DB:       /24 per AZ (254 hosts × 3 AZs)
```

---

### ⚙️ Phase 2 - Cross-Region Connectivity

```
Transit Gateway topology:
  Each region: one TGW
  Cross-region: TGW peering attachment between regions
  
  us-east-1 TGW ←→ eu-west-1 TGW (TGW peering)
  us-east-1 TGW ←→ ap-southeast-1 TGW (TGW peering)
  
VPCs attached to TGW per region:
  Main VPC
  CDE VPC
  (future: analytics VPC, dev VPC)
  
Route table design:
  CDE VPC route table:
    to 10.0.0.0/16 (main): VIA TGW (for auth services)
    to 0.0.0.0/0: BLOCKED (no internet from CDE)
  Main VPC route table:
    to 10.5.0.0/16 (CDE): VIA TGW (app → card processing)
    to 0.0.0.0/0: via NAT GW (app egress to internet)
    
Global user routing:
  Route53 latency-based routing per region
  Health checks: HTTP probe every 30 seconds
  TTL: 60 seconds (fast failover)
  Failover: if us-east-1 fails → Route53 routes to eu-west-1
```

---

### ⚙️ Phase 3 - Zero Trust Security Layer

**Service mesh (Istio) deployment:**

```
Cluster setup:
  EKS cluster per region (Kubernetes for all new services)
  Istio: installed with operator (gitops managed)
  Sidecar injection: enabled per namespace (not cluster-wide)
  
mTLS rollout plan (3-month timeline):
  Month 1: PERMISSIVE mode + full observability
  Month 2: STRICT per-namespace (non-CDE namespaces first)
  Month 3: STRICT on CDE namespace + AuthorizationPolicies
  
CDE AuthorizationPolicy (critical):
```

```yaml
# Only payment-api can call card-vault service
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: card-vault-policy
  namespace: cde
spec:
  selector:
    matchLabels:
      app: card-vault
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/payments/sa/payment-api"
      to:
        - operation:
            methods: ["POST"]
            paths: ["/tokenize", "/charge"]
  # Deny-all default: if no rule matches → 403
  # Audited: every allowed/denied access logged
```

**DDoS protection layers:**

```
Layer 1 - AWS Shield Advanced:
  Covers: all ALBs and public IPs
  Automatic: volumetric attack mitigation
  DDoS response team: 24x7 (required for PCI)
  
Layer 2 - AWS WAF on all ALBs:
  Rules:
    AWS Managed Rules: OWASP Top 10 + known bad IPs
    Rate limit per IP: 1,000 req/5min
    Block: known SQL injection patterns
    Block: requests from Tor exit nodes
    
Layer 3 - Application rate limiting:
  Redis-based per user/API key
  Limits per plan: 100/min standard, 1,000/min enterprise
  Differentiated: payment endpoints = 10/min (abuse prevention)
  
Layer 4 - Adaptive load shedding:
  At 80% CPU: shed low-priority requests (analytics)
  At 90% CPU: shed medium-priority requests
  At 95% CPU: only critical paths (payments, auth)
```

---

### ⚙️ Phase 4 - Observability

```
Network observability stack:
  Metrics: Prometheus + Thanos (long-term storage)
  Tracing: Jaeger (via Istio automatic injection)
  Logs: Elasticsearch (network flow logs, access logs)
  Dashboards: Grafana
  Alerting: PagerDuty integration via Alertmanager
  
Critical network alerts (SLA: 99.99%):
  - error_rate > 0.1% for 5 minutes → P1 alert
  - P99 latency > 2× baseline for 5 minutes → P2 alert
  - TCP retransmit rate > 1% → P2 alert
  - cert_expiry_days < 14 (any service cert) → P2 alert
  - BGP session drop (Transit Gateway) → P1 alert
  - DNS resolution failure > 0.1% → P2 alert
  
SLA calculation for 99.99% uptime:
  Error budget: 52 minutes per year
  Monthly budget: ~4.3 minutes
  Any P1 incident uses budget
  Blameless postmortem: required for any P1
  SLO burn rate alert: if burning budget too fast
```

---

### ⚙️ Phase 5 - Disaster Recovery

```
DR tier: Active-Passive (meets 99.99% SLA with < 5 min RTO)

Normal operation:
  us-east-1: primary region (100% traffic)
  eu-west-1: warm standby (scaled to 50% capacity)
  ap-southeast-1: warm standby (for Asia traffic)
  
Data replication:
  RDS: Multi-AZ within region (sync) + cross-region read replica (async)
  Redis: Elasticache Global Datastore (async replication)
  S3: cross-region replication enabled
  
Failover procedure (automated):
  Trigger: Route53 health check fails for 3 consecutive checks
  Action: Route53 changes record to eu-west-1 ALB IP
  Time: ~70 seconds (3 × 10-second check interval + DNS TTL 60s)
  Scale: Lambda triggers auto-scaling group scale-up in eu-west-1
  
RPO analysis:
  RDS async replication: ~1-60 seconds of data loss (typical)
  Accept: 60 seconds RPO for analytics tables
  Zero RPO option: synchronous cross-region (expensive, 80ms latency)
  Decision: accept 60s RPO for non-payment, 0 RPO for payment (sync)
  
Failover test (quarterly):
  1. Announce test window
  2. Route 10% traffic to eu-west-1 for 30 minutes
  3. Validate: all services work, metrics healthy
  4. Return to 100% us-east-1
  5. Runbook updated with any issues found
```

---

### ⚙️ Terraform Project Structure

```
infrastructure/
  network/
    modules/
      vpc/
        main.tf        # VPC, subnets, IGW, NAT GW
        variables.tf   # vpc_cidr, environment, region
        outputs.tf     # vpc_id, subnet_ids, nat_gw_ids
        
      security-groups/
        main.tf        # SG definitions per tier
        variables.tf
        outputs.tf
        
      transit-gateway/
        main.tf        # TGW, attachments, route tables
        variables.tf
        outputs.tf
        
      waf/
        main.tf        # WAF ACL, rules, associations
        variables.tf
        outputs.tf
        
    environments/
      production/
        us-east-1/
          main.tf      # calls modules with prod values
          variables.tf
          backend.tf   # S3 state: prod/us-east-1/network
        eu-west-1/
          main.tf
        ap-southeast-1/
          main.tf
      staging/
        us-east-1/
          main.tf
          
  service-mesh/
    istio/
      base/           # Istio CRDs, operator
      controlplane/   # IstioOperator configuration
      policies/       # AuthorizationPolicy, PeerAuthentication
        namespaces/
          payments/
          auth/
          analytics/
          cde/
          
  monitoring/
    prometheus/       # ServiceMonitor, PrometheusRule
    grafana/          # Dashboards as ConfigMaps
    alerts/           # AlertManager routes and receivers
```

---

### 📐 Trade-Off Summary

```
Every major decision and its cost:

Service mesh (Istio):
  Gain: mTLS, circuit breakers, canary, observability
  Cost: 50MB RAM per pod, 1ms latency per hop, ops complexity
  Decision: worth it for 50 services; not for 3 services

Transit Gateway:
  Gain: transitive connectivity, centralized routing
  Cost: $0.05/hour per attachment + $0.02/GB processed
  Decision: required once > 5 VPCs (VPC peering doesn't scale)

Active-Passive DR:
  Gain: 5-minute RTO, 60-second RPO
  Cost: 50% extra infrastructure running in warm standby
  Decision: required for 99.99% SLA; Active-Active unnecessary

DDoS protection (Shield Advanced):
  Gain: volumetric protection, DRT access (required for PCI)
  Cost: $3,000/month base + $30/protected resource/month
  Decision: mandatory for payment processor (compliance + brand risk)

Redis distributed rate limiting:
  Gain: fair rate limits across all instances
  Cost: ~1ms latency per rate check, Redis as dependency
  Decision: worth it at 50 services; local limiter for 1-2 services
```
permalink: /technical-mastery/net/build-a-secure-network-platform-phase-3/
---