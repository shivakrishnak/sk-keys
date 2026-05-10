---
version: 2
layout: default
title: "AWS WAF"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /cloud-aws/aws-waf/
id: AWS-058
category: Cloud - AWS
difficulty: ★★★
depends_on: AWS CloudFront, AWS Shield, Security
used_by: Cloud - AWS
related: AWS Shield, AWS CloudFront, OWASP Top 10
tags:
  - aws
  - cloud
  - security
  - advanced
---

# AWS-055 - AWS WAF

⚡ **TL;DR -** AWS WAF is a web application firewall that inspects HTTP/HTTPS requests and allows, blocks, or counts them based on configurable rules - protecting against OWASP Top 10 and custom threats.

|                |                                          |
| -------------- | ---------------------------------------- |
| **Depends on** | AWS CloudFront, AWS Shield, Security     |
| **Used by**    | Cloud - AWS                              |
| **Related**    | AWS Shield, AWS CloudFront, OWASP Top 10 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your API is publicly accessible. A bot enumerates your `/login` endpoint with 10,000 credential stuffing attempts per minute. SQL injection payloads hit your `/search` parameter. A vulnerability scanner probes every URL for known CVEs. Your application servers process all of this traffic - consuming CPU, saturating the connection pool, and occasionally succeeding on a misconfigured endpoint.

**THE BREAKING POINT:** Application code cannot safely validate every HTTP request against all known attack patterns. A security team cannot manually write firewall rules fast enough to respond to emerging threats. Managed rule updates need to deploy globally in seconds, not days.

**THE INVENTION MOMENT:** AWS WAF answered: what if HTTP request inspection happened at the edge, before traffic reached your application - using managed rule sets that AWS (and third parties) update automatically as new threats emerge?

---

### 📘 Textbook Definition

**AWS WAF (Web Application Firewall)** is a managed web application firewall that monitors HTTP and HTTPS requests forwarded to Amazon CloudFront, Application Load Balancers, API Gateway, and AppSync. It uses **Web ACLs** (Access Control Lists) containing **rules** and **rule groups** to allow, block, or count requests based on conditions including IP addresses, HTTP headers, request body, URI strings, SQL injection patterns, and cross-site scripting (XSS) patterns.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A configurable HTTP inspector at the edge that blocks malicious requests before they reach your application.

**One analogy:**

> AWS WAF is like a security checkpoint at an airport. Every passenger (HTTP request) must pass through the scanner (WAF rules). Known threats are stopped at the gate (blocked). Suspicious individuals get secondary screening (counted, rate-limited). VIPs (whitelisted IPs) go through the fast lane.

**One insight:** WAF evaluates rules in priority order - the first matching rule wins. Rule priority determines whether allow rules can bypass block rules or vice versa.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. WAF inspects HTTP requests at the application layer (L7) - it understands headers, URIs, and body content.
2. Rules are evaluated in priority order; the lowest numerical priority runs first.
3. The Web ACL default action applies when no rule matches (usually `Allow`).
4. WAF is not a network firewall - it does not block by port, protocol, or IP at the network layer (that is Security Groups and NACLs).

**DERIVED DESIGN:** A Web ACL contains rules evaluated sequentially by priority. Each rule specifies a statement (what to inspect), an action (allow/block/count/challenge), and a CloudWatch metric name. Rule groups bundle multiple rules for reuse or purchase (AWS Managed, marketplace). Rate-based rules aggregate requests over a 5-minute sliding window, blocking IPs that exceed a threshold.

**THE TRADE-OFFS:**
**Gain:** OWASP Top 10 protection, bot control, rate limiting, geographic blocking, managed rules auto-updated by AWS/vendors.
**Cost:** $5/month per Web ACL + $1/month per rule + $0.60/million requests. False positives block legitimate traffic; rule tuning requires ongoing effort.

---

### 🧪 Thought Experiment

**SETUP:** Your e-commerce API has a `/checkout` endpoint. An attacker has 50,000 compromised IP addresses and runs credential stuffing at 1,000 requests/second from rotating IPs.

**WHAT HAPPENS WITHOUT WAF:** All 1,000 requests/second hit your ALB, then your application servers, then your database for credential validation. DB connection pool exhausts. Legitimate checkouts fail. The attack succeeds in finding valid credentials.

**WHAT HAPPENS WITH WAF:** Rate-based rule limits each IP to 100 requests per 5-minute window. After 100 requests, the IP is automatically blocked for the remainder of the window. CAPTCHA challenge rule on `/checkout` stops automated submissions. Bot Control managed rule identifies and blocks known bot ASNs. 99% of attack traffic is blocked at CloudFront edge - never reaching your ALB.

**THE INSIGHT:** WAF moves the security perimeter from your application code to the network edge. Attack traffic is absorbed by the AWS edge network, not your application infrastructure.

---

### 🧠 Mental Model / Analogy

> AWS WAF is like a museum entrance queue with multiple security checkpoints. Each checkpoint (rule) inspects visitors (requests) for a specific concern - ticket validity (IP allowlist), weapons (SQL injection patterns), dress code (required headers), crowd limits (rate limiting). The first checkpoint that raises a flag handles the visitor. The museum curator (you) decides the order of checkpoints and what to do with flagged visitors.

- **Checkpoints in order** = rules sorted by priority number
- **Specific concern per checkpoint** = rule statement (IP match, SQL injection, etc.)
- **What to do with flagged visitors** = rule action (block, count, challenge)
- **Museum entrance policy** = Web ACL default action
- **Pre-made security protocols** = AWS Managed Rule Groups

Where this analogy breaks down: a real checkpoint queue adds latency; WAF evaluation is done in parallel with traffic forwarding with negligible latency impact (~1ms at edge).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
WAF is a filter for your website's traffic. It reads every incoming request and blocks the ones that look malicious - like SQL injection attempts or requests from known hacker IPs - before they reach your application.

**Level 2 - How to use it (junior developer):**
Create a Web ACL in the WAF console. Add AWS Managed Rule Groups (AWSManagedRulesCommonRuleSet covers OWASP Top 10). Set rules to `Count` first to see what would be blocked without actually blocking. Review the CloudWatch metrics. Switch to `Block` once false positives are identified and excluded.

**Level 3 - How it works (mid-level engineer):**
The Web ACL is a prioritised list of rules. AWS evaluates each rule's statement against the incoming request: IP sets, geographic match, string match in header/URI/body, regex pattern match, SQL injection detection, XSS detection, size constraint, or rate-based aggregation. Rule groups can be AWS-managed, marketplace, or custom. Managed rules are updated by AWS without template changes. The `Count` action doesn't block but increments a CloudWatch metric - useful for tuning without disruption.

**Level 4 - Why it was designed this way (senior/staff):**
The separation of rule groups from Web ACLs solves the versioning and update problem in security rule management. If managed rules were embedded in the Web ACL, AWS couldn't push updates without your permission. By treating rule groups as referenced objects with vendor-managed versioning, AWS can publish new protections while you control when your Web ACL adopts them (via version pinning). The `Count`/`Block` action duality is a deliberate "shadow mode" design - it mirrors the pattern of dark launches in software, allowing operational validation before full enforcement. This is a critical safety mechanism given that a misconfigured WAF rule can block legitimate production traffic.

---

### ⚙️ How It Works (Mechanism)

1. **Web ACL** - the top-level WAF resource; associated with one or more CloudFront distributions, ALBs, API Gateways, or AppSync APIs.
2. **Rules** - individual inspection units. Each has: statement (what to inspect), action (allow/block/count/captcha/challenge), and priority (integer, lower = evaluated first).
3. **Rule groups** - reusable collections of rules. Can be AWS Managed, third-party (marketplace), or custom.
4. **AWS Managed Rules** - pre-built rule groups maintained by AWS: `AWSManagedRulesCommonRuleSet` (OWASP Top 10), `AWSManagedRulesKnownBadInputsRuleSet`, `AWSManagedRulesBotControlRuleSet`, `AWSManagedRulesSQLiRuleSet`, etc.
5. **Rate-based rules** - count requests from an IP over a 5-minute sliding window; block automatically when threshold exceeded.
6. **Bot Control** - managed rule group that identifies and handles bots using browser fingerprinting, headless detection, and known bot signatures.
7. **Fraud Control Account Takeover Prevention (ATP)** - inspects login credential submissions against a credential database and blocks known compromised pairs.
8. **Logging** - full request inspection logs to S3, CloudWatch Logs, or Kinesis Data Firehose. Includes sampled requests for inspection in the console.
9. **Scope** - `REGIONAL` (for ALB, API GW, AppSync) vs `CLOUDFRONT` (for CloudFront distributions, must be created in us-east-1).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Internet Request
     |
     v
CloudFront / ALB / API Gateway
     |
     | WAF Web ACL evaluation
     | Priority 0: IP Reputation List (Block known bad)
     | Priority 1: Rate-based rule (>1000/5min → Block)
     | Priority 2: Geo block (CN, RU → Block)
     | Priority 3: AWS Common Rule Set (SQLi, XSS)
     | Priority 4: Custom allow list (admin IPs)
     | Default: Allow               ← YOU ARE HERE
     |
     | CloudWatch metric per rule
     | Sampled request logged
     v
Application (ALB / Lambda / ECS)
```

**FAILURE PATH:**

- Managed rule creates false positive → legitimate users blocked with 403
- Web ACL not associated with resource → WAF provides no protection
- Scope mismatch → `CLOUDFRONT` Web ACL in eu-west-1 cannot be used (must be us-east-1)

**WHAT CHANGES AT SCALE:**
At high global traffic, associate WAF with CloudFront (not ALB) to enforce rules at 400+ global edge locations. WAF evaluation at CloudFront edge dramatically reduces the blast radius of attacks on origin servers. Enable Kinesis Data Firehose logging for real-time threat analytics in SIEM.

---

### 💻 Code Example

**AWS CDK - Web ACL with managed rules and rate limiting:**

```typescript
import * as wafv2 from "aws-cdk-lib/aws-wafv2";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";

// Must be in us-east-1 for CloudFront scope
const webAcl = new wafv2.CfnWebACL(this, "AppWebACL", {
  scope: "CLOUDFRONT",
  defaultAction: { allow: {} },
  visibilityConfig: {
    cloudWatchMetricsEnabled: true,
    metricName: "AppWebACL",
    sampledRequestsEnabled: true,
  },
  rules: [
    // AWS IP Reputation List (priority 0)
    {
      name: "AWSIPReputation",
      priority: 0,
      overrideAction: { none: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "AWSIPReputation",
        sampledRequestsEnabled: true,
      },
      statement: {
        managedRuleGroupStatement: {
          vendorName: "AWS",
          name: "AWSManagedRulesAmazonIpReputationList",
        },
      },
    },
    // Rate limit per IP (priority 1)
    {
      name: "RateLimitPerIP",
      priority: 1,
      action: { block: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "RateLimitPerIP",
        sampledRequestsEnabled: true,
      },
      statement: {
        rateBasedStatement: {
          limit: 1000, // per 5 min window
          aggregateKeyType: "IP",
        },
      },
    },
    // OWASP Top 10 (priority 2)
    {
      name: "AWSCommonRules",
      priority: 2,
      overrideAction: { none: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "AWSCommonRules",
        sampledRequestsEnabled: true,
      },
      statement: {
        managedRuleGroupStatement: {
          vendorName: "AWS",
          name: "AWSManagedRulesCommonRuleSet",
        },
      },
    },
  ],
});
```

**AWS CLI - associate WAF with ALB:**

```bash
# Associate Web ACL with an ALB
aws wafv2 associate-web-acl \
  --web-acl-arn \
    arn:aws:wafv2:us-east-1:123:regional/webacl/MyACL \
  --resource-arn \
    arn:aws:elasticloadbalancing:us-east-1:\
123:loadbalancer/app/my-alb/abc

# Check sampled blocked requests
aws wafv2 get-sampled-requests \
  --web-acl-arn \
    arn:aws:wafv2:us-east-1:123:regional/webacl/MyACL \
  --rule-metric-name AWSCommonRules \
  --scope REGIONAL \
  --time-window \
    StartTime=$(date -d '1 hour ago' +%s),\
EndTime=$(date +%s) \
  --max-items 100

# Get all Web ACLs
aws wafv2 list-web-acls \
  --scope REGIONAL \
  --query 'WebACLs[*].[Name,ARN]'
```

---

### ⚖️ Comparison Table

| Feature           | AWS WAF                 | AWS Shield Advanced     | Security Groups  | NACLs            |
| ----------------- | ----------------------- | ----------------------- | ---------------- | ---------------- |
| **OSI Layer**     | L7 (HTTP)               | L3/L4 + L7 (with WAF)   | L4 (TCP/UDP)     | L3/L4            |
| **Inspection**    | HTTP headers, body, URI | Traffic volume patterns | Port/protocol/IP | Port/protocol/IP |
| **Managed rules** | Yes (AWS + 3rd party)   | Via WAF integration     | No               | No               |
| **Rate limiting** | Per-IP HTTP rate        | Volumetric L3/L4        | No               | No               |
| **Geo blocking**  | Yes                     | No                      | No               | No               |
| **Bot detection** | Yes (Bot Control)       | No                      | No               | No               |
| **Cost**          | Per-rule + per-request  | $3,000/mo + 3%          | Free             | Free             |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                            |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "AWS WAF replaces AWS Shield"                     | They are complementary. Shield handles volumetric L3/L4 DDoS. WAF handles L7 application attacks (SQLi, XSS, bot traffic). Shield Advanced integrates with WAF for L7 DDoS mitigation.                                             |
| "Enabling managed rules means no false positives" | AWS Managed Rules use broad signatures to catch attacks. Legitimate traffic (certain user agents, request bodies with SQL-like content in legitimate queries) can trigger false positives. Always run rules in `Count` mode first. |
| "WAF blocks IPs permanently"                      | Rate-based rule blocks are temporary - the 5-minute sliding window. When the request rate drops below the threshold, the block expires. Use IP sets for permanent blocks.                                                          |
| "WAF on ALB is equivalent to WAF on CloudFront"   | WAF on CloudFront evaluates at the global edge (~400 PoPs). WAF on ALB evaluates in the region. Edge enforcement reduces attack traffic reaching your region; regional WAF still processes everything.                             |
| "WAF inspects the entire request body by default" | WAF inspects the first 8 KB of the request body by default. Requests with larger bodies are evaluated on the first 8 KB only; the rest is forwarded to the application.                                                            |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Managed rule false positives blocking legitimate users**
**Symptom:** After enabling `AWSManagedRulesCommonRuleSet`, some users receive HTTP 403 responses. Mobile app users are disproportionately affected.
**Root Cause:** A rule in the Common Rule Set matches a pattern in legitimate mobile app requests (e.g., a `User-Agent` matching a known scanner, or a JSON body containing text that matches a SQL injection pattern).
**Diagnostic:**

```bash
# Get sampled requests for the blocking rule
aws wafv2 get-sampled-requests \
  --web-acl-arn arn:aws:wafv2:... \
  --rule-metric-name AWSCommonRules \
  --scope REGIONAL \
  --time-window \
    StartTime=$(date -d '30 min ago' +%s),\
EndTime=$(date +%s) \
  --max-items 100 \
  --query 'SampledRequests[*].[
    Request.URI,
    Request.Headers,
    RuleWithinRuleGroup
  ]'
```

**Fix:** Override the specific triggering rule within the managed rule group to `Count` instead of inheriting the group action. Add an exclusion scope-down statement to exempt specific URI paths or IPs.
**Prevention:** Always enable managed rules in `Count` mode for 1–2 weeks in production before switching to `Block`. Monitor `BlockedRequests` metrics by rule.

**Mode 2: Rate-based rule incorrectly blocking API Gateway clients behind NAT**
**Symptom:** Corporate clients behind a shared NAT IP are blocked after the rate limit triggers. All employees share one public IP.
**Root Cause:** Rate-based rule aggregates by source IP. 200 employees behind one NAT IP generate 200× the individual rate, exceeding the threshold.
**Diagnostic:**

```bash
# Check which IPs are being rate-limited
aws cloudwatch get-metric-statistics \
  --namespace AWS/WAFV2 \
  --metric-name BlockedRequests \
  --dimensions \
    Name=WebACL,Value=MyWebACL \
    Name=Rule,Value=RateLimitPerIP \
  --period 300 \
  --statistics Sum \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

**Fix:** Add a `Forwarded-IP` header aggregation key so rate limiting is based on `X-Forwarded-For` header rather than the NAT IP. Alternatively, create an IP set allowlist for known corporate NAT IPs with a higher-priority `Allow` rule.
**Prevention:** Use header-based rate limiting (`FORWARDED_IP`) for B2B APIs. Set rate limits high enough to accommodate expected burst patterns.

**Mode 3: WAF not inspecting because Web ACL not associated**
**Symptom:** Application receives SQL injection traffic; no blocked request metrics appear in CloudWatch WAF metrics.
**Root Cause:** Web ACL created but never associated with the ALB or CloudFront distribution.
**Diagnostic:**

```bash
# Check current association for an ALB
aws wafv2 get-web-acl-for-resource \
  --resource-arn \
    arn:aws:elasticloadbalancing:...:loadbalancer/...

# List all Web ACLs and their associations
aws wafv2 list-web-acls --scope REGIONAL \
  --query 'WebACLs[*].[Name,Id]'
```

**Fix:** Associate the Web ACL with the target resource using `aws wafv2 associate-web-acl`.
**Prevention:** Include WAF association in the CloudFormation/CDK stack that creates the ALB or CloudFront distribution. Validate association with `get-web-acl-for-resource` as part of deployment smoke tests.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- AWS CloudFront - WAF for CloudFront scoped ACLs must reside in us-east-1; CloudFront architecture knowledge is required for edge WAF deployment.
- AWS Shield - Shield and WAF are complementary; Shield handles L3/L4 volumetric; WAF handles L7; Shield Advanced integrates with WAF.
- Security (OWASP Top 10) - WAF managed rules map to OWASP categories; understanding injection, XSS, and broken auth attacks makes rule selection rational.

**Builds On This (learn these next):**

- AWS Shield Advanced - pairs WAF with Shield for comprehensive L3–L7 DDoS protection; SRT uses WAF rules during active attacks.
- AWS Firewall Manager - centrally manage WAF Web ACLs and rules across multiple accounts from a single policy.
- AWS Security Hub - WAF findings and blocked request metrics feed into Security Hub for centralised security posture management.

**Alternatives / Comparisons:**

- AWS Shield Advanced - L3/L4 volumetric DDoS; complements WAF rather than replacing it.
- ModSecurity - open-source WAF engine; deployed in-application; requires self-management vs WAF's managed service model.
- CloudFlare WAF - managed WAF at CloudFlare's CDN edge; comparable managed rules; independent of AWS infrastructure.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | L7 HTTP firewall with managed rule |
|                  | groups for OWASP, bots, rate limits |
| PROBLEM IT SOLVES| SQLi, XSS, credential stuffing,   |
|                  | bot traffic, known CVE exploitation |
| KEY INSIGHT      | Rules evaluated by priority; first  |
|                  | match wins; Count mode = shadow     |
| USE WHEN         | Public-facing ALB, API GW, or      |
|                  | CloudFront requiring L7 protection  |
| AVOID WHEN       | Network-layer protection (use SGs,  |
|                  | NACLs, Shield for L3/L4)            |
| TRADE-OFF        | Managed rules may false-positive;  |
|                  | tuning cost vs attack coverage      |
| ONE-LINER        | wafv2:AssociateWebACL              |
| NEXT EXPLORE     | Shield Advanced, Firewall Manager  |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** AWS Managed Rule Groups are updated by AWS automatically when new threats emerge. This means a new rule version could introduce a false positive that blocks your production traffic without any code change on your part. What rule versioning and testing strategy balances staying current on threat coverage with protecting production stability?

2. **(System Interaction)** Your API has a `/webhook` endpoint that receives POST requests from third-party SaaS providers containing JSON payloads. The `AWSManagedRulesCommonRuleSet` is blocking some of these payloads because they contain encoded data that triggers injection detection. How do you selectively exempt webhook traffic from specific rules without removing protection for all other endpoints?

3. **(First Principles)** WAF rate-based rules use a 5-minute sliding window to count requests per IP. An attacker distributes requests across 10,000 IPs, sending 50 requests per IP per 5 minutes - below any individual rate limit. WAF rate-based rules are completely ineffective. What complementary control (AWS Bot Control, Captcha, application-level signals) addresses this specific attack pattern, and what is its fundamental mechanism?
