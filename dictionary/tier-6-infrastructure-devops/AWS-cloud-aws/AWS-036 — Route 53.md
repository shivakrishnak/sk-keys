---
layout: default
title: "Route 53"
parent: "Cloud — AWS"
nav_order: 36
permalink: /cloud-aws/route-53/
id: AWS-036
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["AWS Global Infrastructure", "Region / AZ / Edge Location", "VPC"]
used_by: ["ELB / ALB / NLB", "CloudFormation", "K8s Multi-Cluster"]
related: ["ELB / ALB / NLB", "CloudFront", "VPC", "K8s Multi-Cluster"]
tags: [aws, route53, dns, routing, health-checks, failover, latency, cloud]
---

# Route 53

## ⚡ TL;DR

**Route 53** is AWS's scalable, highly available DNS service. Key features beyond standard DNS: **health checks** for endpoint monitoring, **routing policies** (simple, failover, weighted, latency, geolocation, geoproximity), and **private hosted zones** for internal VPC DNS. 100% SLA. Integrates with ACM for HTTPS, ALB for traffic distribution, and CloudFront for CDN.

---

## 🔥 Problem This Solves

DNS for AWS-hosted applications needs to: resolve to load balancers (ALIAS records for apex domains), automatically fail over to healthy regions, route users to the nearest region for low latency, and support internal service discovery within VPCs. Route 53 handles all of this in one service.

---

## 📘 Textbook Definition

Amazon Route 53 is a highly available, scalable DNS web service. It performs three main functions: domain registration, DNS routing (translating names to IPs), and health checking (monitoring endpoints). Route 53 uses AWS's globally distributed anycast network for low-latency DNS resolution.

---

## ⏱️ 30 Seconds

```
Record types:
  A:       domain → IPv4
  AAAA:    domain → IPv6
  CNAME:   alias → another domain (NOT for apex/root domain)
  ALIAS:   AWS resource alias (like CNAME but works at apex; free queries)
  MX:      mail servers
  TXT:     text (SPF, DKIM, domain verification)

Routing policies:
  Simple:         one value, round-robin
  Failover:       primary/secondary with health check
  Weighted:       distribute traffic by weight (10%/90%)
  Latency:        route to lowest-latency region
  Geolocation:    route by user's country/continent
  Geoproximity:   route based on location + bias
  IP-based:       route based on client IP CIDR
```

---

## 🔩 First Principles

- **ALIAS record**: Route 53 extension; resolves to AWS resource (ALB, CloudFront, S3); free queries; works at zone apex (example.com)
- **Health checks**: poll endpoints every 10-30s; trigger routing changes on failure
- **Anycast**: Route 53 uses anycast so DNS queries route to nearest nameserver (~100 PoPs)
- **TTL**: lower TTL = faster DNS change propagation; higher TTL = less DNS query cost
- **Private hosted zones**: associate with VPCs; internal DNS for services not exposed publicly

---

## 🧪 Thought Experiment

Your app is in us-east-1 and eu-west-1. US users should hit us-east-1 (10ms), EU users should hit eu-west-1 (12ms). With latency routing policy: Route 53 measures latency from user to each region, routes each query to lowest-latency endpoint. Result: US users → us-east-1, EU users → eu-west-1, automatically, no code changes.

---

## 🧠 Mental Model / Analogy

Route 53 is like a **smart receptionist for your company's global offices**: when a caller (DNS query) comes in, the receptionist (Route 53) looks up the right office (endpoint) to forward the call. But this receptionist is smart: if the US office is sick (health check fails), calls go to the backup EU office. And they route calls to the nearest healthy office (latency routing) for fastest response.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Register domain, create hosted zone, add A/ALIAS records pointing to ALB. Use ALIAS record for apex domain (not CNAME). Enable health checks on critical endpoints.

**Level 2 — Practitioner**: Failover routing: primary (us-east-1 ALB) + secondary (eu-west-1 ALB). Health checks trigger failover. Latency routing: multiple records same name, different regions. Route 53 routes to lowest-latency region. Private hosted zone for internal services: `api.internal` → service IP.

**Level 3 — Advanced**: Active-active multi-region: latency routing with health checks. Both regions serve traffic; failed region automatically excluded. Split-horizon DNS: same domain resolves differently inside VPC (private IP) vs public internet (public IP). Route 53 Resolver: DNS resolution between VPC and on-premises via inbound/outbound endpoints.

**Level 4 — Expert**: Route 53 ARC (Application Recovery Controller): readiness checks + routing control for disaster recovery; cell-based architecture. DNSSEC: sign zone with KMS; Route 53 supports DNSSEC signing. Route 53 as a load balancer: weighted records can distribute traffic between regions for canary deployments. Route 53 Resolver DNS Firewall: block queries to malicious domains (integrated with Managed Domain Lists). Health check types: HTTP/HTTPS endpoint, TCP, calculated (aggregate child checks), CloudWatch alarm.

---

## ⚙️ How It Works

### Multi-Region Failover

```hcl
# Route 53 health check for primary region
resource "aws_route53_health_check" "primary" {
  fqdn              = "api.us-east-1.example.com"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3        # 3 consecutive failures = unhealthy
  request_interval  = 30       # check every 30s
}

# Primary record (us-east-1)
resource "aws_route53_record" "api_primary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "PRIMARY"
  }

  set_identifier  = "primary"
  health_check_id = aws_route53_health_check.primary.id

  alias {
    name                   = aws_lb.us_east_1.dns_name
    zone_id                = aws_lb.us_east_1.zone_id
    evaluate_target_health = true
  }
}

# Secondary record (eu-west-1)
resource "aws_route53_record" "api_secondary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "SECONDARY"  # used only if primary is unhealthy
  }

  set_identifier = "secondary"
  # No health check needed on secondary (it's the fallback)

  alias {
    name                   = aws_lb.eu_west_1.dns_name
    zone_id                = aws_lb.eu_west_1.zone_id
    evaluate_target_health = true
  }
}
```

### Latency-Based Routing (Active-Active)

```hcl
# Latency record for us-east-1
resource "aws_route53_record" "api_us_east" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  latency_routing_policy {
    region = "us-east-1"
  }

  set_identifier  = "us-east-1"
  health_check_id = aws_route53_health_check.us_east.id

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }
}

# Latency record for ap-southeast-1
resource "aws_route53_record" "api_ap" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  latency_routing_policy {
    region = "ap-southeast-1"
  }

  set_identifier  = "ap-southeast-1"
  health_check_id = aws_route53_health_check.ap.id

  alias {
    name                   = aws_lb.ap.dns_name
    zone_id                = aws_lb.ap.zone_id
    evaluate_target_health = true
  }
}
```

### Private Hosted Zone (Internal DNS)

```hcl
# Internal DNS zone associated with VPCs
resource "aws_route53_zone" "internal" {
  name = "internal.example.com"

  vpc {
    vpc_id = aws_vpc.main.id
  }
}

# Internal service discovery
resource "aws_route53_record" "database" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "postgres.internal.example.com"
  type    = "CNAME"
  ttl     = 60
  records = [aws_db_instance.main.address]
}

# Now app can use: jdbc:postgresql://postgres.internal.example.com:5432/mydb
# Works within VPC; not resolvable from internet
```

---

## 🔄 E2E Flow: Failover

```
Normal operation:
  User → DNS query for api.example.com
  Route 53: primary health check ✅ → return ALB-us-east-1 IP
  User connects to us-east-1 ALB

us-east-1 has outage:
  Health check: /health returns 503 (3 times in 90s)
  Route 53: marks primary record UNHEALTHY
  Route 53: switches to secondary record

New DNS query:
  Route 53: primary ❌ → return ALB-eu-west-1 IP
  User connects to eu-west-1 ALB

Recovery:
  us-east-1 /health returns 200 (3 times)
  Route 53: marks primary HEALTHY
  New DNS queries: return to primary
  (Existing connections: stay on secondary until DNS TTL expires)
```

---

## ⚖️ Comparison Table: Routing Policies

| Policy           | Use Case                         | Example                  |
| ---------------- | -------------------------------- | ------------------------ |
| **Simple**       | Single endpoint                  | dev environment          |
| **Failover**     | Active-passive DR                | primary + backup region  |
| **Weighted**     | A/B testing, canary              | 90% v1, 10% v2           |
| **Latency**      | Active-active multi-region       | route to nearest region  |
| **Geolocation**  | Content localization             | EU users → EU servers    |
| **Geoproximity** | Traffic shift by location + bias | gradual region migration |

---

## ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                      |
| ---------------------------------- | -------------------------------------------------------------------------------------------- |
| "Use CNAME for apex domain"        | CNAME at apex breaks DNS (RFC 1034); use ALIAS record                                        |
| "DNS failover is instant"          | DNS TTL determines cache time; low TTL = faster failover                                     |
| "Health checks monitor everything" | Health checks monitor endpoints; Route 53 doesn't know about your app logic                  |
| "Route 53 = global load balancer"  | Route 53 does DNS-level routing, not connection-level; use Global Accelerator for L4 routing |

---

## 🔗 Related Keywords

- [ELB / ALB / NLB](/cloud-aws/elb-alb-nlb/) — common Route 53 ALIAS target
- [AWS Global Infrastructure](/cloud-aws/aws-global-infrastructure/) — Route 53 uses Edge Locations
- [K8s Multi-Cluster](/kubernetes/k8s-multi-cluster/) — Route 53 enables multi-region K8s routing

---

## 📌 Quick Reference Card

```bash
# List hosted zones
aws route53 list-hosted-zones

# List records in hosted zone
aws route53 list-resource-record-sets \
  --hosted-zone-id Z123456789

# Create ALIAS record for ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "my-alb-123456.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true,
          "HostedZoneId": "Z35SXDOTRQ7X7K"
        }
      }
    }]
  }'

# Check health check status
aws route53 get-health-check-status \
  --health-check-id abcd1234-1234-1234-1234-abcdef123456

# Test DNS resolution
dig +short api.example.com @8.8.8.8
nslookup api.example.com
```

---

## 🧠 Think About This

Route 53 health checks have a crucial subtlety: they check from multiple AWS PoPs globally, and a record is marked unhealthy only when more than a threshold of PoPs see it as failed. This is intentional — it prevents a single regional connectivity issue from triggering a global DNS failover. However, this also means failover isn't instantaneous. For critical systems, configure: (1) low health check `request_interval` (10s vs 30s), (2) low `failure_threshold` (2 vs 3), (3) low DNS TTL (60s vs 300s). Together, this gets failover to roughly 60-90 seconds. For near-zero RTO, Route 53 ARC (Application Recovery Controller) provides actively managed routing control that can switch traffic in seconds through a dedicated API, independent of DNS propagation delays.
