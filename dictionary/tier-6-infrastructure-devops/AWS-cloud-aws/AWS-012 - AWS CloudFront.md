---
version: 2
layout: default
title: "AWS CloudFront"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /cloud-aws/aws-cloudfront/
id: AWS-022
category: Cloud - AWS
difficulty: ★★☆
depends_on: CDN, HTTP & APIs, AWS
used_by: Lambda@Edge, Cloud - AWS
related: Lambda@Edge, AWS WAF, S3 Static Hosting
tags:
  - aws
  - cloud
  - networking
  - intermediate
  - performance
---

# AWS-038 - AWS CloudFront

⚡ **TL;DR -** AWS's global CDN that serves content from 400+ edge locations, cutting latency by caching responses close to users.

| Attribute    | Value                                   |
|--------------|-----------------------------------------|
| Depends on   | CDN, HTTP & APIs, AWS                   |
| Used by      | Lambda@Edge, Cloud - AWS                |
| Related      | Lambda@Edge, AWS WAF, S3 Static Hosting |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every user request travels to a single origin server - a data centre in `us-east-1`. A user in Tokyo waits 200 ms for a TCP handshake before a byte is sent. Static assets (images, JS bundles, HTML) hit origin on every request, burning bandwidth and CPU regardless of how many times the same file has been requested.

**THE BREAKING POINT:** You launch globally. Each region sends traffic to a single origin. A viral event fires 500k simultaneous users - your ALB melts. Browser `Cache-Control` headers help repeat visitors, but every first visit still hits origin cold. Your origin is both the source of truth and the server of every byte.

**THE INVENTION MOMENT:** What if you pre-positioned copies of your content in 400+ cities? DNS routes the user to the nearest edge node. Static content is served from RAM 10–50 ms away. Origin sees a fraction of original traffic - only cache misses.

---

### 📘 Textbook Definition

**AWS CloudFront** is a globally distributed content delivery network (CDN) that accelerates delivery of static and dynamic content by caching responses at edge locations close to end users. A CloudFront distribution maps one or more domain names to origins (S3, ALB, API Gateway, EC2, custom HTTP) and defines cache behaviours per URL path pattern, controlling TTL, cache key dimensions, allowed methods, and origin request forwarding. Security features include HTTPS enforcement, signed URLs and cookies for private content, AWS WAF integration, geo-restriction, and TLS termination at the edge.

---

### ⏱️ Understand It in 30 Seconds

**One line:** CloudFront is a cache layer placed in 400+ cities between your users and your origin.

> Think of it as a global network of vending machines stocked with your product. Instead of everyone flying to the factory, they buy from the nearest machine.

**One insight:** CloudFront does not just cache - it also terminates TLS at the edge, absorbs DDoS traffic, enforces geo-restrictions, and can run code (Lambda@Edge) before a request ever reaches your origin.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Network latency is proportional to physical distance and hop count.
2. Identical responses served repeatedly can be cached once and replayed.
3. A cache miss still requires an origin round-trip; cache design determines hit ratio.
4. Security must be enforced at the boundary closest to the user.

**DERIVED DESIGN:**

CloudFront places 400+ Points of Presence (PoPs) at internet exchange points globally. Each PoP runs a reverse-proxy cache keyed on URL plus configured headers, cookies, and query strings. The TTL chain (Min TTL → Default TTL → Max TTL) combined with `Cache-Control` headers from the origin controls how long objects live at the edge. Cache behaviours are path-pattern-matched rules that define which origin to use and how caching behaves per route.

**THE TRADE-OFFS:**

**Gain:** Latency cut from 100–300 ms to 10–50 ms for cached content. Origin offload reaches 80–95% for static assets. Global DDoS absorption and TLS termination at the edge are included at no extra latency cost.

**Cost:** Cache invalidation costs $0.005/path beyond 1 000 free paths/month. Stale content is served if TTL is too high. Dynamic content with unique query strings or auth headers defeats caching entirely. Config propagation to 400+ PoPs takes up to 15 minutes.

---

### 🧪 Thought Experiment

**SETUP:** You host a React SPA on S3 with a 500 KB `main.js` bundle. 100 000 users hit your site daily from Asia, Europe, and the Americas.

**WHAT HAPPENS WITHOUT CloudFront:** Every request hits S3 in `us-east-1`. Tokyo users incur 180 ms RTT for the TCP handshake alone. At 100k users/day S3 request costs accumulate. A traffic spike can hit S3 rate limits. Stale JS is cached in browsers but new users always hit origin cold.

**WHAT HAPPENS WITH CloudFront:** Tokyo users hit a Tokyo PoP - 4 ms RTT. `main.js` is cached at the edge for 24 hours; S3 sees one request per PoP per TTL window. On deploy, you invalidate `/index.html` (free within the first 1 000/month). `main.js` uses an immutable content-hashed filename and needs no invalidation ever.

**THE INSIGHT:** CloudFront is not a performance afterthought - it is the correct default architecture for any public-facing asset. The origin should be the source of truth, not the server of every byte.

---

### 🧠 Mental Model / Analogy

> CloudFront is a global network of post offices that stock your most popular packages. When a customer orders, the local post office checks its shelf first. Only if it does not have it does it place a special order with the central warehouse.

- **Post offices** → CloudFront edge locations (PoPs)
- **Central warehouse** → Your origin (S3 / ALB / EC2)
- **Shelf TTL** → Cache-Control / CloudFront TTL settings
- **Special order** → Cache miss → origin fetch
- **Stock clearance** → Cache invalidation

Where this analogy breaks down: unlike a post office, CloudFront can execute code on the package itself (Lambda@Edge) before handing it to the customer - inspecting, transforming, or rejecting it at the edge.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CloudFront copies your website to servers placed around the world so nearby users can load it faster.

**Level 2 - How to use it (junior developer):**
Create a distribution pointing to an S3 bucket or load balancer. Set the default cache behaviour TTL. Point your domain's CNAME to the CloudFront domain (`xyz.cloudfront.net`). Enable HTTPS with an ACM certificate. On deploy, run `aws cloudfront create-invalidation --paths "/index.html"`.

**Level 3 - How it works (mid-level engineer):**
A distribution has one or more cache behaviours matched by path pattern, evaluated top-to-bottom. `/api/*` bypasses cache; `/static/*` caches 365 days. The cache key is URL plus any configured headers/cookies/query strings - adding unnecessary dimensions destroys hit rate. Origin Shield adds an extra regional cache tier between PoPs and origin, collapsing parallel cache-miss requests for the same object (request collapsing). CloudFront uses anycast DNS - the user's resolver returns the IP of the nearest PoP.

**Level 4 - Why it was designed this way (senior/staff):**
CloudFront separates control plane (distribution config stored in AWS backend) from data plane (PoP fleet). Config propagation takes up to 15 minutes because each PoP must receive and reload config atomically. Invalidations are operationally expensive to propagate to 400+ PoPs - the preferred pattern is immutable assets with content-hashed filenames and a short-TTL `index.html`, avoiding invalidations entirely. Min/Default/Max TTL exist to honour origin `Cache-Control` headers while still enforcing operator guardrails - an operator can override a greedy `max-age=0` from a poorly configured origin.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| 1. User DNS query → anycast → nearest PoP IP  |
| 2. TLS terminated at PoP (ACM cert loaded)    |
| 3. Cache lookup on URL + cache key fields     |
|    HIT  → return cached response (4–10 ms)   |
|    MISS → forward origin request              |
| 4. Origin returns response                    |
| 5. PoP stores response per TTL                |
| 6. Response returned to viewer                |
+-----------------------------------------------+
```

**Cache Behaviours** are evaluated top-to-bottom by path pattern. Each behaviour specifies: origin, allowed HTTP methods, cache policy (TTL + cache key), origin request policy (which headers/cookies to forward to origin), and response headers policy.

**Origin Groups** support a primary plus a failover origin. If the primary returns 5xx, CloudFront automatically retries the failover origin within the same request.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User (Tokyo)
  |
  v
DNS resolver -> CloudFront anycast IP  <- YOU ARE HERE
                (Tokyo PoP)
  |
  v
TLS handshake terminated at PoP
  |
  v
Cache lookup (URL + configured cache key)
  |
  +-- HIT  --> Return cached response (~5 ms)
  |
  +-- MISS --> Forward to origin (us-east-1 ALB)
                |
                v
             Origin returns 200 OK
                |
                v
             PoP caches response per TTL
                |
                v
             Return to user (~180 ms total)
```

**FAILURE PATH:** If origin returns 5xx and an origin group failover is configured, CloudFront retries the failover origin. Without failover, CloudFront can serve stale content if `stale-if-error` is configured in the cache policy. Otherwise the 5xx propagates to the user.

**WHAT CHANGES AT SCALE:** At high QPS the PoP in-memory cache fills; objects may be evicted (LRU) before their TTL expires. Origin Shield helps - all PoPs funnel cache misses through a single regional shield cache, collapsing parallel origin requests for the same object into one.

---

### 💻 Code Example

**BAD - Single long TTL for all content, no cache strategy:**
```bash
# index.html cached 1 year -> users see stale app after deploy
# Must invalidate /* on every deploy (costs money)
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/*"
# Wildcard counts as 1 path, but triggers full edge purge
```

**GOOD - Separate cache behaviours per content type:**
```yaml
# CloudFormation snippet
CacheBehaviors:
  - PathPattern: "/static/*"
    # Content-hashed filenames: cache forever
    CachePolicyId: !Ref ImmutablePolicy    # TTL 31536000
    ViewerProtocolPolicy: redirect-to-https
  - PathPattern: "/api/*"
    # APIs must never be cached with auth headers
    CachePolicyId: !Ref NoCachePolicy      # TTL 0
    OriginRequestPolicyId: !Ref AllHeadersPolicy
    AllowedMethods:
      - GET
      - HEAD
      - OPTIONS
      - PUT
      - POST
      - PATCH
      - DELETE
DefaultCacheBehavior:
  # index.html: short TTL so new deploys are seen quickly
  CachePolicyId: !Ref ShortTTLPolicy       # TTL 60
  ViewerProtocolPolicy: redirect-to-https
```

```bash
# On deploy: only invalidate the entry point (free path)
aws s3 sync ./dist s3://my-bucket/ --delete && \
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/index.html"
```

---

### ⚖️ Comparison Table

| Feature             | CloudFront       | Cloudflare CDN   | Fastly           |
|---------------------|------------------|------------------|------------------|
| Edge locations      | 400+             | 310+             | 70+              |
| AWS-native          | Yes              | Manual           | Manual           |
| Edge compute        | Lambda@Edge      | Workers          | Compute@Edge     |
| Cache invalidation  | Paid >1k/month   | Free, instant    | Instant (API)    |
| WAF integration     | AWS WAF          | Built-in         | Signal Sciences  |
| Pricing             | Per GB transfer  | Free tier + plans| Volume-based     |
| Real-time logs      | Yes (Kinesis)    | Yes              | Yes              |
| Geo-restriction     | Built-in         | Built-in         | Via config       |

---

### 🔁 Flow / Lifecycle

**Cache Object Lifecycle:**

```
+-----------------------------------------------+
| 1. MISS   -> Object fetched from origin       |
| 2. STORE  -> Cached at PoP with TTL           |
| 3. HIT    -> Served from PoP (fast path)      |
| 4. STALE  -> TTL expired; revalidate origin   |
| 5. EVICT  -> LRU eviction before TTL expires  |
| 6. PURGE  -> Explicit invalidation API call   |
+-----------------------------------------------+
```

**Signed URL Lifecycle (private content):**

1. **Issue** - Backend generates signed URL: resource path + expiry + key-pair signature
2. **Deliver** - Signed URL returned to authenticated user (short-lived)
3. **Request** - User GETs resource via signed URL
4. **Verify** - CloudFront checks signature (trusted key group) and expiry timestamp
5. **Serve or Deny** - Valid: serve content. Expired/invalid: `403 Forbidden` at edge

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CloudFront only caches static files" | It caches any cacheable HTTP response - API responses, HTML, JSON - based on cache policy configuration. |
| "Invalidation is free" | First 1 000 paths/month are free; beyond that $0.005/path. `/*` counts as 1 path but triggers full edge purge. |
| "Higher TTL = better performance" | Higher TTL increases hit rate but risks stale content after deploys. Immutable content-hashed filenames eliminate this trade-off. |
| "CloudFront is only for speed" | It also terminates TLS, absorbs DDoS (AWS Shield Standard included), enforces geo-restrictions, integrates with WAF, and runs edge compute. |
| "Removing a distribution is instant" | Disabling propagates to 400+ PoPs and takes up to 15 min; the distribution must be disabled before it can be deleted. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Users see stale content after deploy**

**Symptom:** New JS bundle not loaded; old UI behaviour persists in some regions.
**Root Cause:** `index.html` (or JS file) cached at PoP with long TTL; no invalidation triggered on deploy.
**Diagnostic:**
```bash
curl -sI https://mysite.com/main.js \
  | grep -i 'x-cache\|age\|cache-control'
# x-cache: Hit from cloudfront
# Age: 86321   <-- cached ~24 h ago
```
**Fix:**
```bash
# BAD: deploy without invalidation
aws s3 sync ./dist s3://my-bucket/

# GOOD: sync then invalidate entry point
aws s3 sync ./dist s3://my-bucket/ && \
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/index.html"
```
**Prevention:** Use content-hashed filenames (`main.abc123.js`) for JS/CSS. Only `index.html` needs TTL 0 or post-deploy invalidation.

---

**Mode 2 - 502/504 errors from CloudFront**

**Symptom:** Users receive `502 Bad Gateway` or `504 Gateway Timeout`.
**Root Cause:** Origin unreachable or exceeding CloudFront's connect timeout (10 s) or read timeout (30 s).
**Diagnostic:**
```bash
# Download CloudFront access logs and inspect status codes
aws s3 cp s3://my-cf-logs/ ./logs/ --recursive
zcat logs/*.gz \
  | awk '{print $9}' | sort | uniq -c | sort -rn
# Field 9 = sc-status; high counts of 502/504 = origin issue
```
**Fix:** Investigate ALB target health and EC2 CPU. Increase `OriginReadTimeout` in the origin config if origin is healthy but slow. Configure an origin group with failover for HA.
**Prevention:** Health checks on ALB targets. Set appropriate origin timeouts. Configure custom error responses to serve a cached error page for 5xx with a short error TTL.

---

**Mode 3 - Cache hit rate is 0% for expected content**

**Symptom:** CloudFront CacheHitRate metric is ~0%; origin receives all traffic.
**Root Cause:** Cache key includes `Authorization` header, unique `userId` query string, or session cookie - every request generates a unique cache key.
**Diagnostic:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name CacheHitRate \
  --dimensions \
    Name=DistributionId,Value=EDFDVBD6EXAMPLE \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 --statistics Average
```
**Fix:** Audit the cache policy attached to the cache behaviour. Remove headers/cookies/query strings from the cache key that are unnecessary for cache differentiation. For authenticated endpoints, use `CachingDisabled` policy intentionally.
**Prevention:** Explicitly configure a named cache policy per behaviour. Default to `CachingDisabled` for `/api/*`. Document which dimensions belong in the cache key and why.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- CDN - the general pattern CloudFront implements
- HTTP & APIs - Cache-Control, ETag, Vary headers that CloudFront respects
- AWS - IAM, ACM, S3, ALB fundamentals needed to configure origins

**Builds On This (learn these next):**
- Lambda@Edge - run transformation code at CloudFront edge locations
- AWS WAF - attach a web application firewall to a CloudFront distribution
- S3 Static Hosting - the most common CloudFront origin for SPAs

**Alternatives / Comparisons:**
- Cloudflare CDN - feature-rich CDN with a generous free tier and instant invalidation
- Fastly - developer-focused CDN with Compute@Edge for edge logic
- Azure CDN - Microsoft's equivalent, tightly integrated with Azure services

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | AWS global CDN, 400+ PoPs        |
| PROBLEM      | High latency to single origin    |
| KEY INSIGHT  | Cache at edge; origin = truth    |
| USE WHEN     | Any public-facing static asset   |
| AVOID WHEN   | Fully personalised per-user HTML |
| TRADE-OFF    | Cache hit rate vs content freshness|
| ONE-LINER    | Cache distribution + origin group|
| NEXT EXPLORE | Lambda@Edge, AWS WAF             |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** Your cache hit rate drops from 85% to 2% after a new feature is deployed. The feature appends a `?userId=...` query string to every request. How does this destroy the cache, and what change to the cache policy restores the hit rate without breaking the feature?

2. **(Design Trade-off)** You must serve personalised HTML (different content per logged-in user) but still want CloudFront for TLS termination, WAF, and DDoS protection. What architecture lets you keep CloudFront in front without ever caching personalised responses?

3. **(System Interaction)** You deploy a new app version, invalidate `/index.html`, and verify the new version loads in your browser. Thirty minutes later, a user in a different country reports still seeing the old version. What CloudFront mechanisms could explain this, and how would you confirm which one is responsible?
