---
layout: default
title: "ELB  ALB  NLB"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /cloud-aws/elb-alb-nlb/
id: AWS-040
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on:
  [
    "VPC",
    "Subnets (Public / Private)",
    "Security Groups",
    "Auto Scaling Groups",
  ]
used_by: ["Route 53", "EKS", "ECS / Fargate", "Auto Scaling Groups"]
related:
  [
    "Route 53",
    "Auto Scaling Groups",
    "EKS",
    "ECS / Fargate",
    "Ingress Controller",
  ]
tags: [aws, elb, alb, nlb, load-balancer, http, tcp, cloud]
---

# ELB / ALB / NLB

## ⚡ TL;DR

AWS has three load balancers: **ALB** (Application Load Balancer, Layer 7, HTTP/HTTPS, host/path routing, best for web apps), **NLB** (Network Load Balancer, Layer 4, TCP/UDP, static IPs, ultra-low latency), and legacy **CLB** (Classic, deprecated). Use ALB for HTTP microservices. Use NLB for TCP apps needing static IPs, extreme throughput, or PrivateLink. Both support multi-AZ, health checks, and auto-scaling.

---

## 🔥 Problem This Solves

Multiple EC2 instances or containers serve traffic, but users need one endpoint. Load balancers distribute requests across healthy targets, perform health checks, handle SSL termination, and route based on content (ALB) or maximize throughput (NLB).

---

## 📘 Textbook Definition

Elastic Load Balancing (ELB) automatically distributes incoming application traffic across multiple targets (EC2 instances, containers, Lambda functions, IP addresses). ALB operates at Layer 7 (HTTP/HTTPS), enabling content-based routing. NLB operates at Layer 4 (TCP/UDP/TLS), providing extreme performance and static IP addresses.

---

## ⏱️ 30 Seconds

```
ALB (Application Load Balancer) - Layer 7:
  Protocols: HTTP, HTTPS, gRPC, WebSocket
  Routing: host, path, header, query string, method, source IP
  SSL termination: yes (ACM certificates)
  Target types: instance, IP, Lambda
  Use: REST APIs, microservices, EKS Ingress

NLB (Network Load Balancer) - Layer 4:
  Protocols: TCP, UDP, TLS
  Routing: port-based only
  Static IP: yes (one per AZ, Elastic IP supported)
  Target types: instance, IP
  Use: Non-HTTP, TCP apps, static IP needed, PrivateLink

CLB (Classic) - Layer 4/7:
  Legacy. Migrate to ALB or NLB.
```

---

## 🔩 First Principles

- **Target groups**: backends registered with the LB; each has its own health check
- **Listeners**: define protocol + port on LB side; route to target groups by rules
- **Health checks**: LB periodically checks targets; unhealthy = stops sending traffic
- **Connection draining** (deregistration delay): waits for in-flight requests before removing target (default 300s)
- **Multi-AZ**: LB nodes in each AZ; cross-zone load balancing spreads traffic evenly

---

## 🧪 Thought Experiment

You have a monolith being broken into microservices. Users hit `api.example.com`. ALB: one listener on 443, path-based routing: `/users/*` → users-service target group, `/payments/*` → payments-service target group, `/` → legacy-monolith target group. Zero client-side changes. Gradual migration hidden behind the LB.

---

## 🧠 Mental Model / Analogy

ALB is a **smart hotel receptionist**: guests (requests) arrive at the front desk. The receptionist looks at the request ("You need room service (path=/food) → kitchen service; you need housekeeping (path=/clean) → housekeeping team"). NLB is a **dedicated phone exchange**: routes calls (TCP connections) fast without looking at the conversation content; optimized for throughput.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Create ALB in public subnets, target group with EC2 instances, listener on 443 with ACM certificate. Configure health check on `/health`.

**Level 2 — Practitioner**: ALB path routing for microservices. ALB weighted target groups for canary deployments (90/10 split). ALB access logs to S3. Sticky sessions for stateful apps (cookie-based). NLB for database connections needing static IPs.

**Level 3 — Advanced**: ALB as EKS Ingress (AWS Load Balancer Controller). ALB authentication: native OIDC/Cognito integration → offload authentication to LB. ALB conditions: `{field: http-header, httpHeaderConfig: {httpHeaderName: "X-API-Version", values: ["v2"]}}`. NLB PrivateLink: expose service privately to other VPCs/accounts via NLB endpoint.

**Level 4 — Expert**: ALB WAF integration: attach AWS WAF WebACL to ALB for DDoS, SQL injection, XSS protection. ALB mutual TLS (mTLS): require client certificates. ALB IP-based routing: route requests from specific client IP ranges. NLB vs ALB for gRPC: NLB for raw TCP (gRPC over TLS); ALB natively supports gRPC routing with content-based routing. ALB Capacity Units (LCU): pricing based on active connections × bandwidth × rule evaluations. Cross-zone load balancing: ALB (enabled by default, free); NLB (enabled optional, $0.01/GB cross-AZ traffic).

---

## ⚙️ How It Works

### ALB with Path-Based Routing (Terraform)

```hcl
# ALB in public subnets
resource "aws_lb" "main" {
  name               = "main-alb"
  internal           = false     # public-facing
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  security_groups    = [aws_security_group.alb.id]

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "alb-logs"
    enabled = true
  }
}

# Target Groups per microservice
resource "aws_lb_target_group" "users" {
  name        = "users-service"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"   # for ECS/EKS
  vpc_id      = aws_vpc.main.id

  health_check {
    path                = "/actuator/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 10
  }

  deregistration_delay = 30  # wait 30s for in-flight requests
}

resource "aws_lb_target_group" "payments" {
  name        = "payments-service"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id
  # ... health check config
}

# HTTPS Listener with routing rules
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  # Default action: return 404
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "application/json"
      message_body = "{\"error\":\"Not Found\"}"
      status_code  = "404"
    }
  }
}

# Path-based routing rules
resource "aws_lb_listener_rule" "users" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.users.arn
  }

  condition {
    path_pattern { values = ["/api/users/*"] }
  }
}

resource "aws_lb_listener_rule" "payments" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.payments.arn
        weight = 90    # 90% to stable
      }
      target_group {
        arn    = aws_lb_target_group.payments_v2.arn
        weight = 10    # 10% canary
      }
      stickiness {
        enabled  = true
        duration = 600  # stick user to same version for 10min
      }
    }
  }

  condition {
    path_pattern { values = ["/api/payments/*"] }
  }
}

# HTTP → HTTPS redirect
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

### NLB for Static IP + PrivateLink

```hcl
# NLB with Elastic IPs (static)
resource "aws_lb" "nlb" {
  name               = "my-nlb"
  internal           = false
  load_balancer_type = "network"

  # Static IPs per AZ
  subnet_mapping {
    subnet_id     = aws_subnet.public_a.id
    allocation_id = aws_eip.nlb_a.id  # static EIP
  }
  subnet_mapping {
    subnet_id     = aws_subnet.public_b.id
    allocation_id = aws_eip.nlb_b.id
  }
}

# NLB Listener (TCP)
resource "aws_lb_listener" "tcp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 443
  protocol          = "TLS"
  certificate_arn   = aws_acm_certificate.main.arn
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tcp.arn
  }
}
```

---

## ⚖️ Comparison Table

| Feature         | ALB            | NLB               |
| --------------- | -------------- | ----------------- |
| **Layer**       | 7 (HTTP/HTTPS) | 4 (TCP/UDP)       |
| **Routing**     | Content-based  | Port-based        |
| **Static IP**   | ❌ (DNS only)  | ✅ (EIP per AZ)   |
| **WebSocket**   | ✅             | ✅                |
| **gRPC**        | ✅             | Via TCP           |
| **SSL offload** | ✅             | ✅ TLS            |
| **Auth (OIDC)** | ✅             | ❌                |
| **WAF**         | ✅             | ❌                |
| **PrivateLink** | ❌             | ✅                |
| **Throughput**  | High           | Extreme           |
| **Use case**    | HTTP APIs      | TCP/UDP, non-HTTP |

---

## ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------------------- |
| "ALB has static IP"             | ALB DNS name resolves to dynamic IPs; use NLB or Global Accelerator for static IP         |
| "NLB does SSL termination"      | NLB supports TLS offload (not just TCP passthrough)                                       |
| "Security Groups work with NLB" | NLB with IP-based targets: Security Groups work; instance targets: SG must allow VPC CIDR |
| "CLB = ALB"                     | CLB is legacy; migrate to ALB for HTTP and NLB for TCP                                    |

---

## 🔗 Related Keywords

- [Route 53](/cloud-aws/route-53/) — DNS → ALB ALIAS records
- [Auto Scaling Groups](/cloud-aws/auto-scaling-groups/) — ALB integrates with ASG
- [EKS](/cloud-aws/eks/) — AWS Load Balancer Controller creates ALB/NLB for K8s Ingress/Service

---

## 📌 Quick Reference Card

```bash
# List load balancers
aws elbv2 describe-load-balancers

# List target groups
aws elbv2 describe-target-groups

# Check target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Deregister instance (for maintenance)
aws elbv2 deregister-targets \
  --target-group-arn arn:aws:... \
  --targets Id=i-12345

# Get ALB access logs location
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn arn:aws:... \
  --query 'Attributes[?Key==`access_logs.s3.bucket`]'

# Check ALB listener rules
aws elbv2 describe-rules \
  --listener-arn arn:aws:elasticloadbalancing:...
```

---

## 🧠 Think About This

ALB-based routing replaces an entire nginx configuration layer that many teams maintain on EC2 instances. Before AWS Load Balancer Controller for EKS became widely adopted, teams would run nginx or HAProxy on EC2 as reverse proxies, managing complex routing configs as code. ALB listener rules handle: path routing, header-based routing, weighted distribution for canary, HTTP redirect, and fixed-response — covering 80% of reverse proxy use cases without maintaining a proxy tier. The remaining 20% (complex Lua scripting, advanced header manipulation, custom auth) still needs a proxy. For EKS, AWS Load Balancer Controller provisions ALBs natively from Ingress resources — one of the cleanest integrations between Kubernetes and a cloud-native service. Use it instead of ingress-nginx unless you have specific requirements nginx handles and ALB doesn't.
