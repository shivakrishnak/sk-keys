---
id: SEC-054
title: "Security Monitoring Basics (audit logs)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-003, SEC-013, SEC-016, SEC-041
used_by: SEC-079, SEC-092, SEC-100, SEC-116
related: SEC-001, SEC-003, SEC-013, SEC-041, SEC-079, SEC-100
tags:
  - security
  - security-monitoring
  - audit-logs
  - siem
  - structured-logging
  - alerting
  - owasp
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/sec/security-monitoring-basics/
---

⚡ TL;DR - Security monitoring answers "did anything bad happen?"
Log authentication events (success and failure), authorization
failures, input validation rejections, and admin actions.
Never log passwords or PII. Use structured JSON logs that
SIEM tools can parse. Alert on anomalies: failed logins,
impossible travel, unusual access patterns.

**Minimum security event logging:**
```python
import structlog

log = structlog.get_logger()

def login(user_id, success, ip_address, reason=None):
    log.info(
        "auth.login",
        user_id=user_id,
        success=success,
        ip_address=ip_address,
        reason=reason,  # "invalid_password", "account_locked", etc.
        # NEVER log: password, token, credit_card, ssn
    )
```

---

| #054 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Headers, Input Validation, Security Fundamentals, Security Code Review | |
| **Used by:** | Insufficient Logging Anti-Pattern, AWS Security Services, SIEM Architecture, Security Champions | |
| **Related:** | OWASP A09, Structured Logging, SIEM, Incident Response | |

---

### 🔥 The Problem This Solves

**WHY SECURITY MONITORING MATTERS:**

```
ATTACK WITHOUT MONITORING:

Timeline of a breach without security monitoring:
  Day 1:  Attacker tries 500 username/password combinations (brute force)
          → No alert triggered (no monitoring)
  Day 3:  Attacker tries 2,000 more combinations
          → No alert triggered
  Day 7:  Attacker finds valid credential (bob@company.com / Password1)
          → Login succeeds. No alert (successful logins not logged?).
  Day 7-60: Attacker reads 14,000 customer records via API
          → No alert (data access not monitored)
  Day 61:  Customer reports suspicious activity to support
          → Company first learns of breach
  Day 62:  Security team investigates.
          Discovers: no auth logs, no access logs, no anomaly alerts.
          "We have no idea what was taken or how long they were in."
          
          GDPR: breach must be reported within 72 hours of DISCOVERY.
          Fine: up to 4% of annual revenue.
          
          Unable to determine breach scope → assume ALL customer data affected.
          Legal obligation: notify all customers.
          Cost: class action lawsuit, regulatory fines, reputation damage.

ATTACK WITH SECURITY MONITORING:

Day 1:   Attacker tries 500 combinations in 10 minutes
          → Alert: "High rate of failed logins for user bob@company.com from 1.2.3.4"
          → Auto-response: rate limit 1.2.3.4 for 1 hour
          → Security analyst reviews: confirms brute force attempt, blocks IP range
  Day 1:  Attack stopped. Zero accounts compromised.

If monitoring fails and breach occurs:

Day 7:  Attacker logs in with valid credential from 1.2.3.4 (different IP)
Day 7:  Alert: "Login from new IP/location for bob (first time from 1.2.3.4)"
         Alert: "100 API calls to /api/customers in 2 minutes by bob@company.com"
                 (anomaly: normal usage = 5-10 calls/hour)
         → Security analyst investigates immediately
Day 7:  Incident response started same day
         GDPR: 72-hour clock starts from discovery (Day 7, not Day 61)
         Impact: only records accessed in the 30 minutes before detection
         Legal obligation: notify only affected subset of customers
```

---

### 📘 Textbook Definition

**Security Monitoring:** The continuous collection, analysis,
and alerting on security-relevant events in an application
and its infrastructure to detect attacks, unauthorized access,
and anomalous behavior.

**Key components:**

- **Audit Logs:** Records of security-relevant actions.
  Who did what, when, from where, to which resource, with what result.

- **Structured Logging:** Machine-parsable log format (JSON) that
  enables automated analysis by SIEM tools.
  vs. unstructured logging: `"User bob failed to login from 1.2.3.4"` -
  text format, hard to query and correlate.
  Structured: `{"event": "auth.login", "user": "bob", "success": false, "ip": "1.2.3.4"}`

- **SIEM (Security Information and Event Management):** Platform
  that aggregates logs from multiple sources, correlates events,
  and generates alerts based on rules and anomaly detection.
  Examples: Splunk, Elastic SIEM, AWS Security Hub, Datadog SIEM.

- **Alerting:** Real-time notification when suspicious patterns
  are detected (login failure threshold, impossible travel,
  unusual data access volume).

**OWASP A09 (2021): Security Logging and Monitoring Failures:**
One of the top 10 web application vulnerability categories.
Applications that do not log security events enable attackers
to remain undetected, making breach detection and forensics
impossible.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Security monitoring = structured audit logs + anomaly alerting.
Log security events (logins, failures, admin actions) in
machine-parsable JSON. Alert on thresholds and anomalies.
Never log secrets or PII.

**One analogy:**
> Security monitoring is like a bank's security system.
> It records every transaction (who, what, when, which account),
> has motion sensors in the vault (anomaly detection),
> and has a security guard watching monitors (SIEM alerts).
>
> Without it: "We were robbed sometime between January and June.
> No cameras. No records. We don't know what was taken."
>
> With it: "At 3:47am someone entered the vault, took items
> from safe-deposit box 347, triggered the motion sensor,
> and the guard called police at 3:48am. Security camera shows
> their face. Exactly $42,000 taken. Suspect identified."
>
> The log is the evidence. The alert is the guard calling police.
> Without the recording, you have no evidence, no timeline,
> no scope, and no defense.

---

### 🔩 First Principles Explanation

**What to log, what not to log, how to structure it:**

```
WHAT TO LOG (security-relevant events):

CATEGORY 1: Authentication events (ALL of these)
  - Successful login: user_id, ip, timestamp, method (password/oauth/api_key)
  - Failed login: user_id_attempted, ip, timestamp, reason
    (invalid_password, user_not_found, account_locked, mfa_required)
  - Logout: user_id, ip, timestamp, session_duration
  - Password reset requested: user_id, ip, timestamp
  - Password changed: user_id, ip, timestamp
  - MFA enrolled: user_id, ip, timestamp
  - Account locked/unlocked: user_id, admin_id (if admin), ip, timestamp

CATEGORY 2: Authorization failures
  - Access denied: user_id, resource_type, resource_id, action, ip, timestamp
  - Permission escalation attempt: user_id, attempted_role, ip, timestamp
  
CATEGORY 3: Input validation failures (for WAF/attack detection)
  - SQL injection attempt detected: ip, endpoint, parameter (NOT value)
  - XSS attempt: ip, endpoint
  - Request with invalid/unexpected structure: ip, endpoint
  
CATEGORY 4: Admin and sensitive operations
  - Admin login: admin_id, ip, timestamp
  - User role changed: target_user_id, old_role, new_role, admin_id, timestamp
  - User deleted/disabled: target_user_id, admin_id, timestamp
  - Configuration changed: setting_name, old_value (if safe), new_value (if safe), admin_id
  - Export of bulk data: admin_id, record_count, timestamp

CATEGORY 5: Data access anomalies
  - Bulk data access: user_id, resource_type, count, timestamp
    (alert if count > threshold for this user's normal pattern)

WHAT NEVER TO LOG:

  FORBIDDEN (compliance violations):
  - Passwords (plaintext or hashed)
  - Authentication tokens (JWT, session, API keys)
  - Credit card numbers (PCI-DSS)
  - Social security numbers
  - Bank account numbers
  - Health data (HIPAA if US, general GDPR)
  - Full PII that exceeds what's needed (full name, DOB, etc.)
  
  PRACTICAL RULE: Log the minimum PII needed to investigate.
  User ID is fine. Email may be needed (log as hash if possible).
  Name usually not needed in security logs.
  IP address: log it (for investigation) but protect it (GDPR: IP is PII).

LOG STRUCTURE (structured JSON for SIEM):

  BAD (unstructured, hard to query):
    "2024-01-15 10:23:45 ERROR: User bob failed to login"
  
  GOOD (structured JSON):
    {
      "timestamp": "2024-01-15T10:23:45.123Z",  // ISO 8601 UTC
      "level": "WARNING",
      "event": "auth.login.failure",
      "user_id": "usr_123abc",           // Internal ID, not email
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "reason": "invalid_password",
      "attempt_count": 3,               // Attempt number (for thresholds)
      "request_id": "req_456def",       // Correlate with other logs
      "service": "api-gateway",
      "environment": "production"
    }
  
  WHY STRUCTURED:
    SQL: SELECT * FROM logs WHERE event='auth.login.failure'
         AND ip_address='1.2.3.4'
         AND timestamp > NOW() - INTERVAL 1 HOUR
    
    SIEM correlation: all login failures from same IP across all services.
    Alerting: IF count(event='auth.login.failure', ip=X, window=5min) > 10 → ALERT.
    Unstructured text requires brittle regex parsing; JSON is directly queryable.
```

---

### 🧪 Thought Experiment

**SCENARIO: Designing alerting thresholds**

```
CHALLENGE: How many failed logins before alerting?

CONTEXT: Application has 10,000 active users. Average login
  failure rate: 0.5% per day = 50 failed logins per day = 2/hour.

BRUTE FORCE DETECTION - two approaches:

Approach 1: Per-account threshold
  Alert when: > 5 failed logins for a single account in 15 minutes
  
  Why 5? Legitimate users mistype passwords but rarely more than 3 times.
  Why 15 minutes? Brute force tools try 100s/sec; a 15-min window catches
  even slow/distributed attacks.
  
  Action: Lock account + alert. User receives unlock email.
  
  FALSE POSITIVES: User forgets password, tries 5 times → locked.
    Mitigation: After 3 failures, show CAPTCHA (before lockout).
    After 5 failures, lock + send unlock email (self-service unlock).
    Alert security team only after 10 failures (to filter legitimate lockouts).

Approach 2: Per-IP threshold
  Alert when: > 20 failed logins from a single IP in 15 minutes
  
  Why 20? A user trying multiple accounts: 1 failure/account = 20 accounts tried.
  This is credential stuffing (trying known password lists).
  
  Action: Rate limit IP for 1 hour. Alert security team.
  
  FALSE POSITIVES: Corporate NAT (1 IP for entire company). Mitigate with
  per-account threshold having a higher limit for known corporate IPs.

IMPOSSIBLE TRAVEL DETECTION:

  Event 1: User alice logs in from New York (IP geolocated to NY, USA)
  Event 2: 30 minutes later, User alice logs in from London (IP → UK)
  
  30 minutes NY → London is physically impossible.
  Either: (a) account compromise, OR (b) VPN usage
  
  Alert: "Impossible travel for user alice" → security review.
  Action: require MFA re-verification for the London session.
  
  Google, Microsoft, Okta all implement impossible travel detection.
  Threshold: if time_between_logins < (geographic_distance_km / 900km_per_hour):
    alert (900km/hr = roughly max commercial flight speed)

VOLUME ANOMALY DETECTION:

  User normally: 5-10 API calls per hour to /api/customers
  Anomaly: 2,000 API calls in 10 minutes to /api/customers
  
  Alert: "Unusual data access pattern for user alice"
  Possible: account compromise, insider threat, or legitimate bulk export
  Action: alert + pause the user's API quota pending review

  Threshold: 3x standard deviation above user's 30-day baseline
  (per-user baseline, not global threshold)
```

---

### 🧠 Mental Model / Analogy

> Security monitoring is a detective's evidence trail.
>
> A detective investigating a crime needs:
> 1. Timeline - when did each event happen? (timestamps)
> 2. Actors - who did each action? (user_id, ip)
> 3. Actions - what did they do? (event type)
> 4. Objects - what was affected? (resource_id, resource_type)
> 5. Outcomes - did it succeed? (success/failure, reason)
>
> Audit logs ARE the crime scene evidence.
> Without them: "something happened, we don't know what."
> With them: "at 3:47am, user 123 made 500 requests to
> /api/customers, accessed records 1-500, then stopped. IP 1.2.3.4."
>
> The detective (security analyst / SIEM) reads the logs to
> reconstruct exactly what happened, when, and what was affected.
> The detective cannot manufacture evidence after the fact.
> If the evidence wasn't recorded, the crime cannot be investigated.
>
> Alerting: the detective's automated assistant that says
> "something unusual just happened, you should look."

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Security monitoring means keeping records of important events in your application (who logged in, who failed to login, who accessed what data) and alerting when something suspicious happens (too many failed logins, access from a strange location). Like a security camera system for software. Without it: you can't tell if you've been hacked or what was stolen.

**Level 2 - How to use it (junior developer):**
Use structured logging (JSON format). Log these events: auth success, auth failure (with reason), access denied, admin actions, bulk data operations. Include in every log: timestamp (UTC ISO 8601), event name, user_id, ip_address, request_id. NEVER include: passwords, tokens, credit card numbers, social security numbers. Use `structlog` (Python) or similar structured logger. Set up CloudWatch Logs, Datadog, or ELK to collect and query logs.

**Level 3 - How it works (mid-level engineer):**
Security logs need to be separate from application logs (different storage, different access controls). Application logs may be read by developers. Security audit logs should be append-only, accessible only to security team. In AWS: CloudTrail for API calls, S3 server access logs, VPC flow logs, GuardDuty for anomaly detection. Set retention policy: security logs often required for 1-7 years (compliance). Correlation: use a request_id field in every log event across all services - allows reconstructing the full sequence of events for a single request. Alert fatigue: too many alerts → analysts ignore them. Alert on the most reliable indicators with low false-positive rate. Start with: N failed logins per account in 15 min, impossible travel, bulk data access above user's baseline.

**Level 4 - Why it was designed this way (senior/staff):**
The OWASP A09 category exists because most security tooling (WAF, rate limiting, SIEM) is only effective if you feed it the right events. An application with good security controls but no logging cannot determine: (a) if controls are working, (b) if they were bypassed, (c) what happened during a breach. Compliance requirements (PCI-DSS, GDPR, HIPAA, SOC 2) mandate specific log retention and audit trail requirements. GDPR breach notification (72 hours from discovery) is only feasible if you can quickly determine the breach scope from logs. Without logs, you must assume worst-case (all data affected) → maximum liability. Structured logs enable automated analysis; unstructured text is only useful for human eyeballing. SIEM queries against JSON are reliable; regex against text is brittle.

**Level 5 - Mastery (distinguished engineer):**
At enterprise scale: distributed tracing (Jaeger, Zipkin) becomes the security audit trail - each trace represents a user action across multiple services. Trace context propagation (W3C Trace Context standard) enables correlating security events across service boundaries. The security challenge: immutability and integrity of logs. Attackers who compromise a host often delete logs to cover tracks. Defense: write logs to a remote, write-only endpoint immediately (Kinesis Data Firehose → S3 with Object Lock, Splunk, Datadog) - the compromised host cannot retroactively delete log records that were already shipped. Log signing: each log batch is signed with a private key; tampering is detectable. WORM (Write Once Read Many) storage for audit logs. SOC 2 Type II audit: requires demonstrating that security events were logged and responded to consistently over a 6-month period - the audit trail IS the evidence.

---

### ⚙️ How It Works (Mechanism)

**Secure logging implementation:**

```
LOG PIPELINE ARCHITECTURE:

Application Code
    │ structlog / logback / log4j / winston
    ▼
Log Aggregator (local)
    │ Fluentd / Logstash / Vector / CloudWatch Agent
    ▼
Log Storage (centralized, append-only)
    │ CloudWatch Logs / Elasticsearch / Splunk / Datadog
    ▼
SIEM / Alerting Rules
    │ Real-time query on structured fields
    ▼
Alert → PagerDuty / Slack / Email → Security Analyst

```

```
Mermaid:
flowchart TD
  A[Application Code] --> B[Log Library structlog/logback]
  B --> C[Log Aggregator Fluentd/Vector]
  C --> D[Log Storage CloudWatch/Elasticsearch]
  D --> E[SIEM Alert Rules]
  E --> F[PagerDuty / Slack / Email]
  F --> G[Security Analyst]
```

```
LOG INTEGRITY (prevent tampering):

1. Ship logs immediately to remote (not buffered on host):
   On breach: attacker on host cannot delete already-shipped logs.

2. S3 Object Lock (immutable storage):
   aws s3api put-object-legal-hold \
     --bucket audit-logs \
     --key logs/2024/01/15/auth.log.gz \
     --legal-hold Status=ON
   
   Legal hold: cannot be deleted even by root.

3. Log entry integrity:
   {
     "timestamp": "...",
     "event": "auth.login.failure",
     "user_id": "usr_123",
     ...
     "entry_hash": "sha256(prev_hash + this_entry_fields)"
   }
   
   Hash chain: tampering with any entry breaks all subsequent hashes.
   (Similar to blockchain concept applied to audit logs.)

LOG SEPARATION (security vs application):

  Application logs:
    level: DEBUG / INFO / WARNING
    content: performance data, business logic
    access: developers, SREs
    retention: 30-90 days
  
  Security audit logs:
    level: always logged (not filtered by log level)
    content: auth events, access control events, admin actions
    access: security team only (RBAC)
    retention: 1-7 years (depends on compliance requirements)
    integrity: append-only, signed or hash-chained
```

---

### 💻 Code Example

**Python: structured security logging middleware:**

```python
# Security audit logging - FastAPI middleware

import structlog
import time
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structlog for JSON output
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()

# Security events to log (not just HTTP traffic, but semantic events)

def log_auth_success(user_id: str, ip: str, method: str, request_id: str):
    log.info(
        "auth.login.success",
        user_id=user_id,
        ip_address=ip,
        auth_method=method,   # "password", "oauth", "api_key"
        request_id=request_id,
        # NEVER include: password, token, hashed_password
    )

def log_auth_failure(
    user_identifier: str, ip: str, reason: str, 
    attempt_num: int, request_id: str
):
    log.warning(
        "auth.login.failure",
        user_identifier=user_identifier,  # email/username (not password!)
        ip_address=ip,
        reason=reason,     # "invalid_password", "user_not_found", "locked"
        attempt_number=attempt_num,
        request_id=request_id,
    )

def log_access_denied(
    user_id: str, resource_type: str,
    resource_id: str, action: str,
    ip: str, request_id: str
):
    log.warning(
        "authz.access_denied",
        user_id=user_id,
        resource_type=resource_type,   # "document", "account", "admin"
        resource_id=resource_id,
        action=action,                 # "read", "write", "delete"
        ip_address=ip,
        request_id=request_id,
    )

def log_admin_action(
    admin_id: str, action: str,
    target_user_id: str, details: dict,
    ip: str, request_id: str
):
    log.warning(
        "admin.action",
        admin_id=admin_id,
        action=action,             # "role_change", "user_delete", "config_change"
        target_user_id=target_user_id,
        details=details,           # role_change: {old_role, new_role}
        ip_address=ip,
        request_id=request_id,
    )

# Middleware: add request_id to all requests for correlation
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers['X-Request-Id'] = request_id
        return response

# Usage in login endpoint:
@app.post("/api/login")
async def login(credentials: LoginRequest, request: Request):
    request_id = request.state.request_id
    ip = request.client.host
    
    user = get_user_by_email(credentials.email)
    if not user:
        log_auth_failure(
            credentials.email, ip,
            "user_not_found", 1, request_id
        )
        # Generic error (don't reveal user existence)
        raise HTTPException(401, "Invalid credentials")
    
    attempt_count = get_login_attempt_count(credentials.email)
    if attempt_count >= 10:
        log_auth_failure(
            credentials.email, ip,
            "account_locked", attempt_count, request_id
        )
        raise HTTPException(423, "Account locked")
    
    if not verify_password(credentials.password, user.password_hash):
        increment_login_attempts(credentials.email)
        log_auth_failure(
            credentials.email, ip,
            "invalid_password", attempt_count + 1, request_id
        )
        raise HTTPException(401, "Invalid credentials")
    
    reset_login_attempts(credentials.email)
    token = create_session(user.id)
    log_auth_success(user.id, ip, "password", request_id)
    
    return {"token": token}
```

---

### ⚖️ Comparison Table

| Log Type | What it Captures | Who Uses It |
|:---|:---|:---|
| **Application logs** | Errors, warnings, info about app behavior | Developers, SREs |
| **Security audit logs** | Auth, authz, admin actions | Security team |
| **Access logs (HTTP)** | All requests: method, path, status, timing | SREs, security |
| **CloudTrail / API logs** | All cloud API calls (create EC2, modify IAM) | Security, compliance |
| **VPC flow logs** | Network-level: source, dest, port, accept/deny | Security, network team |
| **SIEM** | Aggregates all above, correlates, alerts | Security analysts |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Logging everything provides better security monitoring. | Logging too much creates noise that hides real signals, costs more storage, and risks logging sensitive data (passwords, tokens) by accident. The goal is to log security-relevant events with the right fields - not to log every request parameter or SQL query. Well-defined event types (auth.login.success, authz.access_denied) are more useful than "log everything." Over-logging also increases compliance risk: if you log customer emails in security logs, those logs are PII and must be handled accordingly. |
| Application error logs are sufficient for security monitoring. | Application error logs capture technical failures. Security monitoring requires semantic events: a successful login is NOT an error - but it's a critical security event. An authorization failure may not be a 500 error - it's a 403, which application error logging might ignore. Security audit logs need to capture the business-level meaning of events (user authenticated, user attempted unauthorized access) regardless of whether they produced an error. |

---

### 🚨 Failure Modes & Diagnosis

**Diagnosing logging gaps:**

```
CHECKING WHAT YOUR APPLICATION LOGS:

1. Find all authentication paths:
   - Login endpoint
   - OAuth callback
   - API key validation
   - Password reset
   - Session refresh
   
   For each: does it log success AND failure with user_id and ip?

2. Find all authorization checks:
   - Middleware/decorators (@require_permission, @login_required)
   - Manual role checks (if user.role != 'admin': return 403)
   
   For each: does access denied log user_id, resource, action?

3. Admin actions:
   grep for: admin.delete, admin.update, role, permission
   Are these logged with admin_id and affected resource?

4. Test log structure:
   Trigger a failed login.
   Check log output: is it JSON? Does it have all required fields?
   Can you query it by ip_address or user_id?

5. Check log destination:
   Are logs shipped to centralized storage immediately?
   Can a compromised host delete its own logs?
   Are security logs separate from application logs?

MISSING LOG DETECTION (audit your logs):
   After a suspicious event, can you answer:
   - WHO did it? (user_id)
   - WHAT did they do? (event type)
   - WHEN? (timestamp, UTC)
   - FROM WHERE? (ip_address)
   - TO WHAT? (resource_id, resource_type)
   - DID IT SUCCEED? (success/failure field)
   
   If any of these are unanswerable from your logs: logging gap.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - A09 Logging and Monitoring Failures
- `Security Headers` - defense in depth context
- `Input Validation` - what validation failures to log
- `Security Fundamentals` - threat model for what to monitor

**Builds on this:**
- `Insufficient Logging Anti-Pattern` - common mistakes
- `AWS Security Services` - CloudTrail, GuardDuty, Security Hub
- `SIEM Architecture Design` - enterprise monitoring at scale

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOG (always) │ Auth success/failure, access denied       │
│              │ Admin actions, bulk data access           │
├──────────────┼───────────────────────────────────────────┤
│ NEVER LOG    │ Passwords, tokens, credit cards, SSN      │
│              │ Full health data, session cookies         │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRED     │ timestamp (UTC), event, user_id           │
│ FIELDS       │ ip_address, request_id, success/failure   │
├──────────────┼───────────────────────────────────────────┤
│ FORMAT       │ Structured JSON (not free-text strings)   │
├──────────────┼───────────────────────────────────────────┤
│ ALERT ON     │ >5 failures/account/15min (brute force)   │
│              │ Impossible travel, bulk data anomaly      │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"You cannot investigate what was not recorded."
Security monitoring is fundamentally about forensic capability:
the ability to reconstruct what happened after an incident.
Every security event not logged is evidence permanently lost.
This principle is why GDPR's 72-hour breach notification rule
is so difficult without logging: you need to determine the
breach scope (which users were affected, which data accessed)
before you can notify correctly. Without logs: scope is unknown.
Without scope: you must assume worst-case.
Same principle applies to debugging in distributed systems:
if a request failed and there's no trace, the root cause is
permanently unknown. Structured logging with correlation IDs
is both a debugging practice and a security practice.
The investment is the same; the benefit is dual.
"Observability for developers" and "audit logs for security"
are the same practice with different audiences.

---

### 💡 The Surprising Truth

Equifax's 2017 breach (affecting 147 million people) was not
detected for 78 days because the monitoring system had been
broken for 19 months before the breach. A certificate in the
Equifax network security monitoring system had expired, causing
10 months of SSL traffic inspection to be completely blind.
The attackers operated undetected for 78 days because the
"monitoring" that was supposed to detect them had silently
failed. The lesson: security monitoring systems themselves
must be monitored. A monitoring system that silently fails
is worse than no monitoring system - it creates false confidence.
Implement "canary" events: synthetic security events deliberately
triggered at regular intervals to verify that logging and
alerting is working end-to-end. If the synthetic failed-login
event doesn't trigger the expected alert within 5 minutes:
alert that the monitoring system is broken. You must monitor
your monitors.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DEFINE** which events to log (authentication, authorization,
   admin) and which fields are required for each (user_id, ip, timestamp, reason).
2. **IMPLEMENT** structured JSON audit logging with
   `structlog` or `logback` with appropriate security event types.
3. **DESIGN** alerting thresholds for brute force detection
   (per-account and per-IP), impossible travel, and anomaly detection.
4. **DIAGNOSE** logging gaps by asking: can you answer WHO/WHAT/WHEN/WHERE/
   WHICH RESOURCE/SUCCESS for every security event in your app?

---

### 🎯 Interview Deep-Dive

**Q: What should a production application log for security purposes?
What should it never log?**

*Why they ask:* Tests knowledge of OWASP A09, compliance awareness,
and practical security engineering for production systems.

*Strong answer covers:*
- Log: authentication events (success and failure with reasons),
  authorization failures, admin and sensitive actions, bulk data access.
- Required fields: timestamp (UTC ISO 8601), event name, user_id,
  ip_address, request_id (for correlation), success/failure, reason.
- Never log: passwords (obviously), authentication tokens (just as
  dangerous as passwords - can be replayed), credit card numbers,
  SSNs, health data, full session cookies.
- Format: structured JSON, not free text. SIEM tools query JSON directly;
  regex on free text is brittle and slow.
- Centralized shipping: logs should be shipped to remote storage
  immediately - a compromised host should not be able to delete logs
  that were already shipped.
- Alerting: per-account login failure threshold (5 in 15 min = brute force),
  per-IP threshold (20 in 15 min = credential stuffing), impossible travel.
- OWASP A09: not logging is itself a vulnerability - enables attackers
  to operate undetected and prevents forensics after an incident.
  Equifax 2017: 78 days undetected due to broken monitoring.