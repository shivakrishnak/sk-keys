---
layout: default
title: "AWS Shield"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /cloud-aws/aws-shield/
id: AWS-016
category: Cloud - AWS
difficulty: ★★★
depends_on: DDoS Protection, AWS CloudFront, AWS WAF
used_by: Cloud - AWS
related: AWS WAF, AWS CloudFront, CloudFlare
tags:
  - aws
  - cloud
  - security
  - advanced
---

# AWS-016 - AWS Shield

⚡ **TL;DR -** AWS Shield is a managed DDoS protection service - Standard is automatic and free; Advanced adds 24/7 expert response, L7 protection, and cost shields against attack-inflated bills.

| | |
|---|---|
| **Depends on** | DDoS Protection, AWS CloudFront, AWS WAF |
| **Used by** | Cloud - AWS |
| **Related** | AWS WAF, AWS CloudFront, CloudFlare |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your application serves 10,000 legitimate users/day. An attacker launches a volumetric UDP flood generating 500 Gbps of traffic at your public IP. Your EC2 instances saturate. Auto Scaling cannot provision instances fast enough. AWS charges you for the traffic spike. Your service is down for hours.

**THE BREAKING POINT:** DDoS attacks don't just degrade service - they cause financial damage through AWS bill inflation from attack-generated bandwidth, EC2 auto-scaling, and data transfer charges. A single attack can produce a $50,000 unexpected bill.

**THE INVENTION MOMENT:** AWS built Shield to provide always-on attack detection and automatic mitigation, and to protect customers from the financial side-effect of surviving an attack.

---

### 📘 Textbook Definition

**AWS Shield** is a managed Distributed Denial of Service (DDoS) protection service that safeguards applications running on AWS. **Shield Standard** provides automatic protection against the most common network- and transport-layer attacks at no charge. **Shield Advanced** adds detection and mitigation for sophisticated application-layer (L7) attacks, access to the AWS Shield Response Team (SRT), real-time attack visibility, and financial protection against cost spikes caused by attacks.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Automatic DDoS mitigation built into AWS - Standard is free; Advanced adds human experts and bill protection.

**One analogy:**
> Shield Standard is like a building's automatic sprinkler system - it activates on its own during a fire. Shield Advanced is like having a 24/7 fire brigade on speed dial, with equipment to handle industrial fires, and insurance that covers the damage costs.

**One insight:** Shield Standard is already protecting your EC2, CloudFront, and Route 53 resources today - you don't need to enable anything. Shield Advanced is the upgrade when you need SLA-backed response and L7 protection.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. DDoS attacks operate at OSI layers L3 (Network), L4 (Transport), and L7 (Application).
2. Volumetric attacks (L3/L4) can be mitigated automatically by absorbing or redirecting traffic.
3. Application-layer attacks (L7) require request inspection - they cannot be blocked by volume alone.
4. Financial protection requires an SLA commitment from the provider to waive attack-inflated costs.

**DERIVED DESIGN:** Shield Standard operates at the network edge using AWS's global anycast scrubbing centres. Traffic is analysed inline; anomalous flows are dropped before reaching customer resources. Shield Advanced adds WAF integration, application-flow baselining, and human judgment for sophisticated attack vectors that look legitimate to automated systems.

**THE TRADE-OFFS:**
**Gain (Advanced):** 24/7 SRT access, L7 detection, cost protection, consolidated attack diagnostics, proactive engagement during major events.
**Cost (Advanced):** $3,000/month + 3% of AWS monthly bill protected. Not justifiable for small or non-critical workloads.

---

### 🧪 Thought Experiment

**SETUP:** Your e-commerce site serves 100K users during peak. You're running EC2 behind an ALB with CloudFront in front.

**WHAT HAPPENS WITHOUT Shield Advanced during an L7 attack:** An attacker sends 2 million HTTP requests/second, each requesting your most expensive database query. CloudFront forwards them. The ALB and EC2 fleet try to process them. DB connection pool exhausts. Legitimate users time out. The attack looks like legitimate traffic - no volumetric signature. Standard mitigation doesn't trigger.

**WHAT HAPPENS WITH Shield Advanced:** AWS baselining detects the request rate deviation from normal patterns. Shield Advanced automatically creates WAF rules targeting the attack pattern (user-agent, request path, source IP ranges). SRT contacts you proactively if the attack escalates. The auto-scaling costs caused by the attack are covered under the cost protection benefit.

**THE INSIGHT:** L7 DDoS attacks are indistinguishable from legitimate traffic without application context. Shield Advanced brings application-aware protection that Standard's pure network analytics cannot provide.

---

### 🧠 Mental Model / Analogy

> AWS Shield is like airport security at different levels. Standard is the automated metal detector every passenger walks through - free, always on, catches obvious threats. Advanced is the VIP security detail: a trained team that follows your high-value asset, adapts to sophisticated threats in real time, can call reinforcements, and reimburses you if something breaks through despite their protection.

- **Metal detector** = Standard automatic L3/L4 detection and mitigation
- **VIP security detail** = Shield Response Team (SRT)
- **Adapts to sophisticated threats** = application-layer WAF rule creation
- **Calls reinforcements** = proactive DDoS engagement
- **Reimburses you** = cost protection for bill spikes

Where this analogy breaks down: airport security adds latency; Shield operates inline with near-zero latency overhead because mitigation happens at the network edge before traffic reaches your resources.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Shield is AWS's protection against "flooding attacks" - when bad actors try to crash your website by sending too much fake traffic. The basic version is free and automatic; the advanced version includes a team of experts who help you fight back.

**Level 2 - How to use it (junior developer):**
Shield Standard is already active on your EC2 EIPs, CloudFront distributions, ELBs, Global Accelerator, and Route 53 hosted zones - no action required. To enable Shield Advanced, subscribe through the console, associate your protected resources, and optionally set up a WAF Web ACL. Monitor attacks in the Shield console under "Attack Diagnostics."

**Level 3 - How it works (mid-level engineer):**
Standard uses inline traffic scrubbing at AWS edge PoPs using flow-level heuristics (SYN flood detection, UDP reflection filtering, ICMP flood mitigation). Advanced adds an application layer with WAF integration - it creates automatic WAF rules when it detects L7 anomalies. Attack telemetry is collected per resource with request-level granularity. The SRT can directly modify your WAF rules with your permission during an active attack.

**Level 4 - Why it was designed this way (senior/staff):**
The two-tier model reflects a fundamental economics problem: volumetric L3/L4 mitigation can be fully automated because the signatures are deterministic (SYN without ACK, amplification ratios). L7 attacks cannot be automated completely because they require application context - the "right" WAF rule depends on your traffic patterns, not generic signatures. Charging $3K/month for Advanced is AWS saying: "we'll dedicate human expertise to your specific application profile." The cost protection clause is strategically important - it converts DDoS from a financial weapon into a pure operational nuisance for Advanced subscribers.

---

### ⚙️ How It Works (Mechanism)

**Shield Standard:**
1. **Always-on traffic monitoring** - flow-level analysis at AWS edge, all ingress traffic to AWS resources.
2. **Automatic mitigation** - SYN floods, UDP floods, reflection attacks detected and scrubbed within seconds.
3. **Zero configuration** - applies automatically to EC2 EIPs, ELB, CloudFront, Route 53, Global Accelerator.

**Shield Advanced (additional capabilities):**
4. **Resource association** - you associate specific resources (EIPs, ALBs, CloudFront, Route 53) for enhanced monitoring.
5. **Baseline traffic profiling** - Advanced learns your application's normal traffic patterns over time.
6. **L7 detection + WAF integration** - anomaly triggers automatic WAF rule creation. WAF must be associated with ALB or CloudFront.
7. **SRT engagement** - direct access to AWS DDoS experts via Support case with elevated response SLA.
8. **Global threat environment dashboard** - visibility into active DDoS campaigns affecting AWS infrastructure.
9. **Cost protection** - submit a billing credit request after an attack. AWS reviews and credits auto-scaling and data transfer costs attributable to the attack.
10. **Proactive engagement** - SRT contacts you proactively when an attack is detected on Advanced-protected resources.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Shield Advanced L7 attack response):**
```
Internet traffic
     |
     v
AWS Edge PoP (scrubbing centre)
     | [L3/L4 volumetric scrubbing - Standard]
     v
CloudFront / Global Accelerator
     | [L7 baselining - Advanced]
     v
Shield Advanced Detection Engine
     | anomaly detected        ← YOU ARE HERE
     |--- auto WAF rule ---> WAF Web ACL
     |--- SRT alert -------> Shield Response Team
     |--- dashboard event --> Security console
     v
ALB → EC2/ECS/Lambda (legitimate traffic only)
```

**FAILURE PATH:**
- Sophisticated L7 attack without WAF association → Shield Advanced detects anomaly but cannot create rules without a WAF Web ACL attached to the resource
- Standard only → L7 slowloris or HTTP flood bypasses Standard mitigation entirely
- Advanced subscription without resource association → no enhanced monitoring applies

**WHAT CHANGES AT SCALE:**
Global Accelerator + Shield Advanced provides the highest protection level: Accelerator routes traffic through AWS's anycast network, scrubbing happens closest to the attack origin. This is the recommended architecture for globally distributed applications under Advanced.

---

### 💻 Code Example

**AWS CLI - enable Shield Advanced and associate resource:**
```bash
# Subscribe to Shield Advanced (one-time, per account)
aws shield create-subscription

# Associate a CloudFront distribution
aws shield create-protection \
  --name "MyApp-CloudFront" \
  --resource-arn \
    arn:aws:cloudfront::123456789:distribution/E1ABC

# Associate an ALB
aws shield create-protection \
  --name "MyApp-ALB" \
  --resource-arn \
    arn:aws:elasticloadbalancing:us-east-1:\
123456789:loadbalancer/app/my-alb/abc123

# Associate WAF Web ACL for L7 protection
aws wafv2 associate-web-acl \
  --web-acl-arn \
    arn:aws:wafv2:us-east-1:123:regional/webacl/MyACL \
  --resource-arn \
    arn:aws:elasticloadbalancing:...:loadbalancer/...

# List active attacks
aws shield list-attacks \
  --start-time StartTime=$(date -d '24 hours ago' +%s) \
  --end-time EndTime=$(date +%s)

# Describe an attack in detail
aws shield describe-attack \
  --attack-id <attack-id>
```

**AWS CDK - Shield Advanced protection with WAF:**
```typescript
import * as shield from 'aws-cdk-lib/aws-shield';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';

// Associate a CloudFront distribution with Shield
new shield.CfnProtection(this, 'CfnDistProtection', {
  name: 'MyApp-CloudFront-Shield',
  resourceArn: distribution.distributionArn
});

// Create WAF ACL for L7 protection
const webAcl = new wafv2.CfnWebACL(
  this, 'AppWebACL', {
    scope: 'CLOUDFRONT',
    defaultAction: { allow: {} },
    visibilityConfig: {
      sampledRequestsEnabled: true,
      cloudWatchMetricsEnabled: true,
      metricName: 'AppWebACLMetric'
    },
    rules: [{
      name: 'AWSManagedRulesCommonRuleSet',
      priority: 1,
      overrideAction: { none: {} },
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: 'CommonRuleSetMetric'
      },
      statement: {
        managedRuleGroupStatement: {
          vendorName: 'AWS',
          name: 'AWSManagedRulesCommonRuleSet'
        }
      }
    }]
  }
);
```

---

### ⚖️ Comparison Table

| Feature | Shield Standard | Shield Advanced | CloudFlare DDoS | AWS WAF alone |
|---|---|---|---|---|
| **Cost** | Free | $3,000/mo + 3% | Free–$200/mo | Pay per request |
| **L3/L4 protection** | Yes (automatic) | Yes (enhanced) | Yes | No |
| **L7 protection** | No | Yes (WAF + SRT) | Yes | Yes |
| **Expert response team** | No | Yes (SRT) | Enterprise plan | No |
| **Cost protection** | No | Yes | No | No |
| **Global coverage** | AWS edge only | AWS edge + GA | Global PoPs | AWS edge |
| **Setup required** | None | Resource association | DNS delegation | Rule authoring |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Shield Standard protects against L7 attacks" | Shield Standard only handles L3/L4 (volumetric) attacks. HTTP floods, Slowloris, and layer-7 application attacks require Shield Advanced with WAF integration. |
| "Shield Advanced is enabled automatically after subscribing" | After subscribing, you must explicitly associate protected resources. Unassociated resources receive Standard protection only. |
| "Cost protection is automatic after subscribing" | You must submit a billing credit request through AWS Support after an attack. It's not automatic - AWS reviews the attack logs and grants credits manually. |
| "Shield Advanced replaces WAF" | They complement each other. Shield Advanced detects and signals attack patterns; WAF enforces the blocking rules. Advanced without WAF cannot block L7 attacks. |
| "Any IP address is protected by Standard" | Standard protects AWS-hosted resources (EC2 EIP, ELB, CloudFront, Route 53, Global Accelerator). On-premises resources or third-party IPs are not covered. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: L7 HTTP flood bypasses Standard, degrades service**
**Symptom:** Service degrades under high request rate; CloudFront returns 5xx; no Shield Standard mitigation triggered. Attack traffic looks like legitimate HTTP GET requests.
**Root Cause:** Shield Standard is L3/L4 only. HTTP-level attacks require L7 inspection.
**Diagnostic:**
```bash
# Check CloudFront access logs for request spikes
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].[Id,DomainName]'

# Check Shield attack history
aws shield list-attacks \
  --start-time StartTime=$(date -d '1 hour ago' +%s)

# Check WAF sampled requests for patterns
aws wafv2 get-sampled-requests \
  --web-acl-arn arn:aws:wafv2:... \
  --rule-metric-name CommonRuleSetMetric \
  --scope CLOUDFRONT \
  --time-window StartTime=$(date -d '1h ago'+%s),\
EndTime=$(date +%s) \
  --max-items 100
```
**Fix:** Enable Shield Advanced. Attach WAF Web ACL to CloudFront with rate-limiting rules. SRT can create application-specific rules during an active attack.
**Prevention:** Deploy WAF with rate-based rules for all public-facing CloudFront and ALB resources regardless of Shield tier.

**Mode 2: Auto-scaling spike creates massive bill during attack**
**Symptom:** DDoS attack triggers Auto Scaling; 50× normal instance count; $40,000 bill for one day.
**Root Cause:** Shield Standard has no cost protection. Attack traffic successfully triggers scaling policies.
**Diagnostic:**
```bash
# Review Auto Scaling activity during attack window
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name MyASG \
  --query \
    'Activities[?StartTime>`2024-01-01T00:00:00Z`]'
# Review Shield attack in Advanced console
aws shield describe-attack --attack-id <id>
```
**Fix:** Subscribe to Shield Advanced. Submit billing credit request through AWS Support with the attack ID.
**Prevention:** Implement max capacity limits on ASGs. Use Shield Advanced cost protection. Monitor ASG activity with CloudWatch alarms set at 3× normal capacity.

**Mode 3: SRT cannot help because WAF not associated**
**Symptom:** Shield Advanced subscribed, attack detected, SRT engaged - but SRT cannot create mitigating WAF rules. Attack continues.
**Root Cause:** No WAF Web ACL associated with the protected ALB or CloudFront distribution.
**Diagnostic:**
```bash
# Check if WAF is associated with the resource
aws wafv2 get-web-acl-for-resource \
  --resource-arn \
    arn:aws:elasticloadbalancing:...:loadbalancer/...
```
**Fix:** Create a WAF Web ACL and associate it with the protected resource. Authorize SRT with IAM role to manage WAF rules during incidents.
**Prevention:** Shield Advanced setup checklist must include WAF Web ACL association. Use the Shield Advanced protection wizard which prompts for WAF setup.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DDoS Protection - understand L3/L4/L7 attack types, volumetric vs application-layer, and amplification attacks before Shield architecture makes sense.
- AWS CloudFront - Shield Standard automatically protects CloudFront distributions; Advanced integrates with CloudFront WAF for L7 detection.
- AWS WAF - Shield Advanced's L7 protection capability works through WAF; understand WAF Web ACLs and rule groups first.

**Builds On This (learn these next):**
- AWS WAF - deploy managed rule groups and custom rate-limiting rules to complement Shield's detection with enforcement.
- AWS Global Accelerator - pair with Shield Advanced for the highest-tier DDoS protection with anycast ingress scrubbing.
- AWS CloudWatch - set alarms on Shield metrics to get proactive notification before an attack degrades service.

**Alternatives / Comparisons:**
- AWS WAF - application-layer protection only; no volumetric mitigation. Complements Shield, not a substitute.
- CloudFlare DDoS - cloud-agnostic, CDN-integrated DDoS protection with comparable Standard tier (free) and enterprise advanced offerings.
- Akamai Kona Site Defender - enterprise-grade edge DDoS + WAF, vendor-agnostic, commonly used in financial services alongside AWS.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Managed DDoS protection: Standard  |
|                  | (free/L3-L4) + Advanced (L7/SRT)   |
| PROBLEM IT SOLVES| Volumetric attacks, L7 floods,     |
|                  | attack-inflated AWS bills           |
| KEY INSIGHT      | Standard is always-on free; Adv    |
|                  | adds humans + cost protection       |
| USE WHEN         | Advanced: public-facing apps with  |
|                  | revenue or compliance requirements  |
| AVOID WHEN       | Standard is sufficient for most    |
|                  | non-critical workloads ($3K/mo)     |
| TRADE-OFF        | $3,000/mo + 3% vs unmitigated L7  |
|                  | attacks and unexpected bill spikes  |
| ONE-LINER        | shield:CreateProtection            |
| NEXT EXPLORE     | AWS WAF, Global Accelerator        |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** Shield Advanced costs $3,000/month plus 3% of the protected monthly AWS bill. A startup has a $5,000/month AWS bill but serves a healthcare platform with strict uptime requirements. What financial and risk analysis framework would you use to determine whether Shield Advanced is justified, and which resources would you associate first?

2. **(System Interaction)** Shield Advanced can automatically create WAF rules during an active L7 DDoS attack. But automated WAF rules created during high-traffic incidents could also block legitimate users with similar request patterns. What approval workflow and rule-management process reduces the risk of friendly-fire blocking?

3. **(First Principles)** Shield Standard protects against L3/L4 volumetric attacks but not L7 application attacks. The difference is that L3/L4 attacks have deterministic mathematical signatures (SYN:ACK ratio, amplification factor) while L7 attacks look like normal HTTP. Why does this distinction mean L7 protection fundamentally cannot be provided without application-specific context, and what does that imply for the architecture of any DDoS protection product?
