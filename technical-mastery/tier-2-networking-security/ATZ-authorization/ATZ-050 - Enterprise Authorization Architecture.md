---
id: ATZ-050
title: "Enterprise Authorization Architecture"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-030, ATZ-040, ATZ-046, ATZ-047, ATZ-048, ATZ-049
used_by: ATZ-051, ATZ-052, ATZ-053
related: ATZ-040, ATZ-049, ATZ-051
tags:
  - security
  - authorization
  - enterprise
  - architecture
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/authorization/enterprise-authorization-architecture/
---

⚡ **TL;DR** - Enterprise authorization architecture combines
multiple models and enforcement points: an identity provider
(IdP) for user authentication and JWT issuance, a central Policy
Administration Point (PAP) for policy management, a Policy
Decision Point (PDP) for evaluation, and Policy Enforcement
Points (PEPs) at API gateways and service boundaries. Large
enterprises typically use RBAC as the foundation (simple to
manage), ABAC for contextual policies (time of day, device),
and ReBAC (Zanzibar) for fine-grained resource ownership at scale.

---

### 📊 Entry Metadata

| #050 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-030 Externalized Authz, ATZ-040 Distributed Authz, ATZ-046 Perf, ATZ-047 Multi-Tenant, ATZ-048 Zero Trust, ATZ-049 Microservices | |
| **Used by:** | ATZ-051, ATZ-052, ATZ-053 | |
| **Related:** | ATZ-040 Distributed Authz, ATZ-049 Microservices, ATZ-051 Central vs Distributed | |

---

### 📘 Textbook Definition

Enterprise authorization architecture is the system design for
consistent, auditable, and scalable access control across an
entire organization's technology estate. Core components (per
XACML/NIST model): Policy Administration Point (PAP) - where
policies are authored, versioned, and stored; Policy Decision
Point (PDP) - where authorization queries are evaluated against
policies and returning allow/deny; Policy Enforcement Point
(PEP) - where the decision is enforced (API gateway, service,
database); Policy Information Point (PIP) - external attribute
sources (LDAP, HR system, device management) that PDP consults
during evaluation. Enterprise architectures additionally require
identity federation (SAML, OIDC), just-in-time access
provisioning, privileged access management (PAM), and
comprehensive audit trails for compliance (SOC2, ISO 27001).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Enterprise Authorization Architecture          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LAYER 1: Identity Foundation                          │
│  IdP (Okta, Azure AD): authentication + JWT issuance   │
│  Directory (AD/LDAP): users, groups, org structure     │
│  SCIM: automatic user provisioning from HR system      │
│                                                        │
│  LAYER 2: Policy Administration                        │
│  PAP: policy authoring tool (OPA Playground, GUI)      │
│  Policy repo: Git-versioned Rego, Cedar, or custom DSL │
│  Policy CI: opa test, validate, build bundles          │
│  Policy review: approval workflow before production    │
│                                                        │
│  LAYER 3: Policy Distribution                          │
│  Bundle server: serves versioned policy bundles        │
│  PDP fleet: OPA sidecars / central PDP cluster         │
│  PIPs: device mgmt, risk engine, HR system adapters    │
│                                                        │
│  LAYER 4: Enforcement                                  │
│  API Gateway: coarse-grained enforcement (route-level) │
│  Service PEP: fine-grained enforcement (resource-level)│
│  Database RLS: data-level enforcement                  │
│  UI: visibility (show/hide) - NOT the security layer   │
│                                                        │
│  LAYER 5: Audit and Compliance                         │
│  Decision logs: all allow/deny with full context       │
│  Shipped to SIEM (Splunk, Elastic) for compliance      │
│  Regular access reviews: quarterly entitlement review  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - XACML-style PDP integration in Java**

```java
// Policy enforcement point (PEP) calling central PDP
@Aspect
@Component
public class AuthorizationAspect {

    @Around("@annotation(requiresPermission)")
    public Object checkPermission(
            ProceedingJoinPoint pjp,
            RequiresPermission requiresPermission) throws Throwable {
        Authentication auth =
            SecurityContextHolder.getContext()
                .getAuthentication();
        String resource = requiresPermission.resource();
        String action = requiresPermission.action();

        // Build authorization request with full context
        AuthzRequest request = AuthzRequest.builder()
            .principal(auth.getName())
            .roles(getRoles(auth))
            .resource(resource)
            .action(action)
            .environment(Map.of(
                "time", LocalTime.now().toString(),
                "ip", getCurrentIp(),
                "device_managed", isDeviceManaged()))
            .build();

        AuthzDecision decision = pdp.evaluate(request);

        if (!decision.isAllow()) {
            // Audit the denial
            auditLogger.logDenial(request, decision);
            throw new AccessDeniedException(
                "Access denied: " + decision.getReason());
        }

        auditLogger.logAllow(request, decision);
        return pjp.proceed();
    }
}

// Usage: annotate service methods
@RequiresPermission(resource = "reports", action = "export")
public Report exportReport(Long reportId) {
    // Authorization check happens before method runs
    return reportService.export(reportId);
}
```

---

*Authorization category: ATZ | Entry: ATZ-050 | v5.0*