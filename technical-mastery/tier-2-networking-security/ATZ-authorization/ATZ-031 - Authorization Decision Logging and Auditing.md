---
id: ATZ-031
title: "Authorization Decision Logging and Auditing"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-026, ATZ-030
used_by: ATZ-040, ATZ-050, ATZ-054
related: ATZ-030, ATZ-054, ATZ-061
tags:
  - security
  - authorization
  - audit-logging
  - compliance
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/authorization/authorization-decision-logging-and-auditing/
---

⚡ **TL;DR** - Authorization audit logs answer: who accessed what,
when, and was it allowed or denied? These logs are required for
compliance (SOC 2, PCI DSS, HIPAA, ISO 27001) and are critical for
security incident investigation. The failure mode is incomplete
logging: only logging allows (not denies), not logging the policy
that triggered the decision, or losing logs before an incident is
investigated. Log both allowed and denied decisions, include
context (user, resource, action, policy name, timestamp, request ID),
and ship to immutable storage.

---

### 📊 Entry Metadata

| #031 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-026 PBAC, ATZ-030 Externalized Auth | |
| **Used by:** | ATZ-040, ATZ-050, ATZ-054 | |
| **Related:** | ATZ-030 Externalized Auth, ATZ-054 Observability, ATZ-061 Trust Assertion | |

---

### 📘 Textbook Definition

Authorization decision logging records every access control
evaluation: the requesting principal, the resource and action
requested, the policy or rule applied, the decision (allow/deny),
and the timestamp. These logs serve compliance requirements
(demonstrating access was controlled), security investigation
(reconstructing what happened during a breach), and operational
debugging (why was access denied?). Key requirements: structured
format (JSON, structured logging), immutability (append-only,
shipped to SIEM or object storage), completeness (log denies not
just allows), and correlation (link to request trace ID for
end-to-end investigation).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authorization Audit Log Schema                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Required fields per decision:                         │
│  {                                                     │
│    "event_type": "authorization_decision",             │
│    "timestamp": "2024-01-15T09:30:00.123Z",            │
│    "trace_id": "abc-123-def",                          │
│    "decision": "DENY",                                 │
│    "principal": {                                      │
│      "user_id": "alice@corp.com",                      │
│      "roles": ["EDITOR"],                              │
│      "ip_address": "10.0.0.45"                         │
│    },                                                  │
│    "resource": {                                       │
│      "type": "Document",                               │
│      "id": "doc-001",                                  │
│      "owner": "bob@corp.com"                           │
│    },                                                  │
│    "action": "delete",                                 │
│    "policy_applied": "ATZ-013-owner-only-delete",      │
│    "reason": "User is not owner of resource"           │
│  }                                                     │
│                                                        │
│  COMPLIANCE RETENTION:                                 │
│  PCI DSS: 1 year (3 months online + 9 months archive)  │
│  HIPAA: 6 years                                        │
│  SOC 2: available during audit period (typically 1yr)  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Structured authorization audit log**

```java
@Component
@Aspect
public class AuthorizationAuditLogger {

    private final Logger auditLog = LoggerFactory
        .getLogger("audit.authorization");

    @Around("@annotation(RequiresPermission)")
    public Object logDecision(ProceedingJoinPoint pjp,
            RequiresPermission permission)
            throws Throwable {
        String userId = SecurityContextHolder
            .getContext().getAuthentication().getName();
        String resource = extractResource(pjp);
        String action = permission.value();
        String traceId = MDC.get("traceId");
        Instant start = Instant.now();

        try {
            Object result = pjp.proceed();
            // Log allowed decision
            auditLog.info("{}", Map.of(
                "event_type", "authorization_decision",
                "timestamp", start.toString(),
                "trace_id", traceId,
                "decision", "ALLOW",
                "user_id", userId,
                "resource", resource,
                "action", action
            ));
            return result;
        } catch (AccessDeniedException e) {
            // Log denied decision - equally important!
            auditLog.warn("{}", Map.of(
                "event_type", "authorization_decision",
                "timestamp", start.toString(),
                "trace_id", traceId,
                "decision", "DENY",
                "user_id", userId,
                "resource", resource,
                "action", action,
                "reason", e.getMessage()
            ));
            throw e;
        }
    }
}
```

**Example - BAD: logging only success, not denials**

```java
// BAD: only logging successful access
@PostAuthorize("returnObject.ownerId == authentication.name")
public Document getDocument(String docId) {
    Document doc = docRepo.findById(docId).orElseThrow();
    log.info("Document {} accessed by {}", docId,
        getUsername()); // only logs successful access
    return doc;
}
// If attacker probes 1000 document IDs looking for data,
// you see nothing in logs - only successful hits

// GOOD: use audit logging aspect that captures DENY events
// Log denied access attempts - they are the most important
// signal for detecting unauthorized probing
```

---

*Authorization category: ATZ | Entry: ATZ-031 | v5.0*