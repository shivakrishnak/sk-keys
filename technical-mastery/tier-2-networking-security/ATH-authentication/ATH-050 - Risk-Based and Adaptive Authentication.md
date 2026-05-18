---
id: ATH-050
title: "Risk-Based and Adaptive Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-012, ATH-017, ATH-044, ATH-046, ATH-052
used_by: ATH-051, ATH-053, ATH-056
related: ATH-044, ATH-051, ATH-052
tags:
  - security
  - authentication
  - risk-based
  - adaptive
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/authentication/risk-based-and-adaptive-authentication/
---

⚡ **TL;DR** - Risk-based authentication (RBA) dynamically adjusts
the authentication challenge based on the risk score of a login
attempt. Low risk (known device, usual location, normal time) =
let the user through with a password. Elevated risk (new country,
new device, unusual hour) = require MFA. High risk (credential
stuffing bot, impossible travel) = block or force re-registration.
This balances security with user experience: low-friction for normal
behavior, friction exactly when it matters.

---

### 📊 Entry Metadata

| #050 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-012 MFA, ATH-017 Rate Limiting, ATH-044 ATO, ATH-046 Token Theft, ATH-052 Observability | |
| **Used by:** | ATH-051, ATH-053, ATH-056 | |
| **Related:** | ATH-044 ATO, ATH-051 Continuous Auth, ATH-052 Anomaly Detection | |

---

### 📘 Textbook Definition

Risk-based authentication (RBA), also called adaptive
authentication, evaluates contextual risk signals at login time
to determine the required authentication strength. Risk signals
include: device fingerprint (new vs. known device), geographic
location (new country, impossible travel velocity), IP reputation
(Tor exit nodes, datacenter IPs, known bad actors), time of day
(off-hours for the user), behavioral biometrics (typing pattern,
mouse movement), and historical account behavior. The risk engine
produces a score. Below a threshold: static password suffices.
Above threshold: MFA required. High score: session blocked, CAPTCHA,
or delayed response (tarpit). True RBA also evaluates risk
continuously after login (continuous authentication).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Risk-Based Auth Decision Engine                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  At login:                                             │
│  Signals collected:                                    │
│  - Device fingerprint (browser, OS, hardware ID)       │
│  - IP address + geolocation + ISP type                 │
│  - Time of day vs user's historical login times        │
│  - Distance from last login location                   │
│  - Browser/user agent vs historical                    │
│  - Credential check vs HIBP / known-breached list      │
│                                                        │
│  Risk score produced (0-100):                          │
│  0-30:   LOW    -> password only, proceed              │
│  31-60:  MEDIUM -> require MFA (TOTP or push)          │
│  61-85:  HIGH   -> require phishing-resistant MFA      │
│                   (WebAuthn/FIDO2)                     │
│  86-100: CRITICAL -> block + notify + trigger          │
│                     account review                     │
│                                                        │
│  Post-login signals:                                   │
│  - Sudden navigation to admin pages                    │
│  - Mass export / bulk download                         │
│  - IP change mid-session                               │
│  Action: re-challenge with MFA or terminate session    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Risk engine integration in Spring Security**

```java
@Component
public class AdaptiveAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain chain) throws Exception {
        String ip = request.getRemoteAddr();
        String ua = request.getHeader("User-Agent");
        String userId = getCurrentUserId(request);

        if (userId != null) {
            RiskScore score = riskEngine.evaluate(
                RiskContext.builder()
                    .userId(userId)
                    .ipAddress(ip)
                    .userAgent(ua)
                    .sessionAge(getSessionAge(request))
                    .build());

            if (score.isHigh() && !isMfaVerified(request)) {
                // Require step-up MFA for this request
                response.sendRedirect("/mfa/challenge?return="
                    + URLEncoder.encode(
                        request.getRequestURI(), "UTF-8"));
                return;
            }

            if (score.isCritical()) {
                // Block + revoke session
                sessionService.invalidate(
                    request.getSession().getId());
                response.sendError(
                    HttpServletResponse.SC_UNAUTHORIZED,
                    "Session suspended: suspicious activity");
                securityAudit.log("SESSION_SUSPENDED",
                    userId, ip, score);
                return;
            }
        }
        chain.doFilter(request, response);
    }
}
```

---

*Authentication category: ATH | Entry: ATH-050 | v5.0*