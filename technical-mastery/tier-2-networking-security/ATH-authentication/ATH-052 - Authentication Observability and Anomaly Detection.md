---
id: ATH-052
title: "Authentication Observability and Anomaly Detection"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-017, ATH-044, ATH-050
used_by: ATH-051, ATH-053, ATH-056
related: ATH-050, ATH-051, ATH-053
tags:
  - security
  - authentication
  - observability
  - anomaly-detection
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/authentication/authentication-observability-and-anomaly-detection/
---

⚡ **TL;DR** - Authentication systems generate rich security
signals that most teams never analyze. Every failed login, every
new device, every impossible travel event, every successful login
after many failures is a security signal. Observability means
instrumenting these events, shipping them to a SIEM or log
aggregator, and building anomaly detection rules. Production
authentication without observability is blind: you will not know
you were breached until weeks later.

---

### 📊 Entry Metadata

| #052 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-017 Rate Limiting, ATH-044 ATO, ATH-050 Risk-Based | |
| **Used by:** | ATH-051, ATH-053, ATH-056 | |
| **Related:** | ATH-050 Risk-Based, ATH-051 Continuous Auth, ATH-053 Auth Server | |

---

### 📘 Textbook Definition

Authentication observability is the systematic collection,
aggregation, and analysis of authentication events to detect
attacks, measure health, and support incident response.
Key events to instrument: successful logins (user, IP, device,
location), failed logins (frequency, IP, user), MFA events
(success/fail/bypass), password resets, account lockouts,
session creations/terminations, OAuth token issuances, and
admin actions on authentication infrastructure. Anomaly
detection identifies patterns that deviate from a baseline:
login velocity anomalies, impossible travel (login from two
distant locations within minutes), brute force patterns,
and credential stuffing (many accounts tried from one IP).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authentication Observability Stack             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  INSTRUMENT (log these events):                        │
│  - LOGIN_SUCCESS: userId, ip, device, location, time   │
│  - LOGIN_FAILURE: ip, username (not password!), reason │
│  - MFA_SUCCESS / MFA_FAILURE: method, userId           │
│  - PASSWORD_RESET: userId, ip, method used             │
│  - ACCOUNT_LOCKED: userId, failure count, ip           │
│  - NEW_DEVICE: userId, device fingerprint              │
│  - IMPOSSIBLE_TRAVEL: userId, locations, velocity      │
│  - SESSION_CREATED / TERMINATED: userId, duration      │
│  - ADMIN_ACTION: actorId, targetId, action             │
│                                                        │
│  SHIP: structured JSON logs -> log aggregator          │
│  (Elasticsearch, Splunk, Datadog, AWS CloudWatch)      │
│                                                        │
│  DETECT (alert rules):                                 │
│  Rule: 5 LOGIN_FAILURE for same userId in 5min         │
│  Rule: LOGIN_SUCCESS after 20 failures -> ATO signal   │
│  Rule: LOGIN_SUCCESS from 2 countries in 30min         │
│  Rule: 100 LOGIN_FAILURE from single IP in 1min        │
│         (credential stuffing)                          │
│  Rule: PASSWORD_RESET + LOGIN from new device          │
│         within 10min (ATO in progress)                 │
│                                                        │
│  RESPOND: alert -> SOC / on-call -> investigate        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Structured authentication event logging**

```java
@Component
public class AuthEventLogger {

    private static final Logger log =
        LoggerFactory.getLogger(AuthEventLogger.class);

    public void loginSuccess(String userId,
                              String ip,
                              String userAgent,
                              boolean newDevice) {
        // Structured JSON log entry (not plain text)
        // NEVER log password, tokens, or secrets
        log.info("{}", Map.of(
            "event", "LOGIN_SUCCESS",
            "userId", userId,
            "ip", ip,                     // for geo/rate
            "userAgent", hashUa(userAgent), // fingerprint
            "newDevice", newDevice,
            "timestamp", Instant.now(),
            "location", geoService.getCountry(ip),
            "sessionId", MDC.get("sessionId")));
    }

    public void loginFailure(String username,
                              String ip,
                              String reason) {
        // Log username (for correlation) but NOT password
        log.warn("{}", Map.of(
            "event", "LOGIN_FAILURE",
            "username", username, // not userId - may be wrong
            "ip", ip,
            "reason", reason, // "bad_password","no_user",etc.
            "timestamp", Instant.now()));
    }

    public void impossibleTravel(String userId,
                                  String loc1,
                                  String loc2,
                                  long velocityKmH) {
        log.error("{}", Map.of(
            "event", "IMPOSSIBLE_TRAVEL",
            "userId", userId,
            "location1", loc1,
            "location2", loc2,
            "velocityKmH", velocityKmH,
            "timestamp", Instant.now()));
        // Also: trigger real-time alert to security team
        alertService.sendHighAlert(
            "Impossible travel for user " + userId);
    }
}
```

---

*Authentication category: ATH | Entry: ATH-052 | v5.0*