---
layout: default
title: "Lambda@Edge"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /cloud-aws/lambda-edge/
id: AWS-007
category: Cloud - AWS
difficulty: ★★★
depends_on: AWS CloudFront, AWS Lambda, CDN
used_by: Cloud - AWS
related: AWS CloudFront, CloudFront Functions, Edge Computing
tags:
  - aws
  - cloud
  - networking
  - advanced
  - performance
---

# AWS-007 - Lambda@Edge

⚡ **TL;DR -** Run Node.js or Python Lambda functions at CloudFront's 400+ edge locations to transform HTTP requests and responses without a round-trip to origin.

| Attribute    | Value                                              |
|--------------|----------------------------------------------------|
| Depends on   | AWS CloudFront, AWS Lambda, CDN                    |
| Used by      | Cloud - AWS                                        |
| Related      | AWS CloudFront, CloudFront Functions, Edge Computing |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your CloudFront distribution caches and delivers content efficiently, but any request logic - JWT validation, URL rewriting, A/B testing, personalisation - must execute at your origin server. Even for a simple header injection, every request incurs a full 100–300 ms round-trip to the origin region.

**THE BREAKING POINT:** You need to: (1) validate auth tokens before serving private S3 content, (2) redirect `/old-path` to `/new-path` globally, (3) route 5% of traffic to a canary origin for feature testing. Each of these requires either a centralised server behind origin or a full extra hop through API Gateway and Lambda in `us-east-1`.

**THE INVENTION MOMENT:** What if you could run code at the edge PoP itself - before the cache is checked, before the request reaches origin? Lambda@Edge executes your function on the same CloudFront fleet that serves cached content, adding only single-digit milliseconds of execution latency without any centralised infrastructure.

---

### 📘 Textbook Definition

**Lambda@Edge** is an AWS feature that allows Lambda functions to be executed at CloudFront edge locations in response to CloudFront request/response events. Functions are triggered at one of four lifecycle points: **Viewer Request** (before cache lookup), **Origin Request** (on cache miss, before origin forward), **Origin Response** (after origin responds, before caching), and **Viewer Response** (before returning to the viewer). Functions run in the AWS region nearest to the user, enabling stateless HTTP transformation globally without centralised servers.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Lambda@Edge is Lambda that runs inside CloudFront's global network, not in a home AWS region.

> Think of it as having a smart customs agent at every international airport who can inspect, modify, stamp, or reject a parcel before it ever reaches the sorting warehouse at headquarters.

**One insight:** Lambda@Edge's power is not just latency - it is the ability to move an entire class of origin complexity (auth, routing, personalisation) to the global edge network, so your origin only receives requests that have already been validated and transformed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Network latency is proportional to physical distance - code runs fastest where the user is.
2. Stateless functions can be replicated to any location without coordination overhead.
3. The earlier in the request lifecycle you execute logic, the more expensive downstream requests you can eliminate.
4. Memory and CPU at shared PoP hardware impose strict resource limits.

**DERIVED DESIGN:**

Lambda@Edge functions are deployed to `us-east-1` (CloudFront's control-plane region) and replicated by CloudFront to all 400+ PoPs automatically. At trigger time, the nearest PoP executes the function in a Lambda execution environment co-located with the cache. The function receives a CloudFront event object, can modify it (pass-through), or return a synthetic HTTP response (short-circuit). All functions must be versioned - `$LATEST` is not supported; CloudFront replicates a specific ARN version.

**THE TRADE-OFFS:**

**Gain:** Request manipulation at <10 ms at the edge. Auth, URL rewriting, and header injection execute globally without regional infrastructure. Origin is protected from invalid or unauthenticated requests entirely.

**Cost:** Hard limits: 128 MB memory, 5 s timeout (viewer triggers), 30 s timeout (origin triggers). No VPC access - cannot directly reach RDS, ElastiCache, or internal services. Cold starts at every PoP. Logs appear in the region where the request was processed, making debugging fragmented. Deployments propagate slowly (~15 min).

---

### 🧪 Thought Experiment

**SETUP:** You have a private video-on-demand library on S3 served via CloudFront. Users must present a valid JWT cookie to access any video. Without edge compute, where does authentication happen?

**WHAT HAPPENS WITHOUT Lambda@Edge:** Every request hits the origin (API Gateway + Lambda in `us-east-1`) for authentication. Even for a 200 MB video file that CloudFront could cache, the auth check adds 150 ms and burns origin Lambda invocations. Unauthenticated users receive `401` only after a full cross-region round-trip. Origin scales to handle every global auth request.

**WHAT HAPPENS WITH Lambda@Edge:** A Viewer Request function at the nearest PoP validates the JWT using a cached public key. Invalid token → immediate `401` from the edge in <5 ms; origin never sees the request. Valid token → request proceeds to cache lookup. The origin Lambda is called only on a genuine cache miss for a valid user, collapsing auth traffic by ~99%.

**THE INSIGHT:** Lambda@Edge moves the security and routing boundary to the global edge network. The origin becomes a specialised service that only handles authorised, cache-miss traffic - not the first line of defence.

---

### 🧠 Mental Model / Analogy

> Lambda@Edge is like a network of smart border checkpoints that can inspect, modify, stamp, reroute, or reject travellers before they ever reach immigration at the destination city - and intercept their return journey too.

- **Border checkpoint** → CloudFront PoP running your Lambda function
- **Traveller** → HTTP request / response
- **Destination city** → Your origin server
- **Inspect passport** → Read/validate request headers or cookies
- **Stamp passport** → Add or modify headers before forwarding
- **Reject at border** → Return a synthetic response (short-circuit origin entirely)
- **Intercept return** → Origin/Viewer Response trigger modifying the response

Where this analogy breaks down: unlike a real border checkpoint, Lambda@Edge also intercepts the return journey (origin response, viewer response) - it can modify what the destination sends back to the traveller, not just what the traveller carries.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Lambda@Edge lets you run small programs right next to your users around the world - so you can check or change web requests before they travel far.

**Level 2 - How to use it (junior developer):**
Write a Lambda function in Node.js 18.x or Python 3.12. Deploy it to `us-east-1`. Publish a version (not `$LATEST`). In CloudFront, attach the function ARN to a cache behaviour at one of the four triggers. The function receives `event.Records[0].cf` containing `request` or `response`. Return the modified object to pass through, or return a complete response object to short-circuit.

```javascript
// Viewer Request: add security header before cache lookup
exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  request.headers['x-custom-header'] = [{
    key: 'X-Custom-Header',
    value: 'edge-injected'
  }];
  return request; // pass through
};
```

**Level 3 - How it works (mid-level engineer):**
**Viewer Request** fires on every request before the cache is consulted - use it for auth and URL normalisation, but be aware it is the most expensive trigger (runs on 100% of requests). **Origin Request** fires only on cache misses before forwarding to origin - far cheaper at scale for per-origin logic. **Origin Response** fires after origin responds and before the response is stored in cache - use it to add `Cache-Control` headers or transform origin output. **Viewer Response** fires after the cache decision and before returning to the viewer - use it for consistent response headers (HSTS, CSP) without touching origin.

**Level 4 - Why it was designed this way (senior/staff):**
The 128 MB memory limit and 5 s/30 s timeouts exist because PoP hardware is shared fleet infrastructure - unbounded memory or long-running functions would starve other distributions sharing the same PoP. No VPC access is architecturally intentional: creating ENIs at 400+ PoPs for each function would be cost-prohibitive and would couple edge compute to a specific region - defeating the latency goal. Deployment to `us-east-1` only is because CloudFront's control plane lives there; function versioning and replication are managed from a single source-of-truth region. The 4 trigger points map directly to the two cache decision boundaries and the two origin interaction boundaries, giving maximal flexibility with minimal trigger overhead.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| [1] Viewer Request  <- every request (pre-cache)|
|       | can short-circuit with response        |
|       v                                        |
| [CF]  Cache Lookup                             |
|       |                                        |
|  HIT -+-> [4] Viewer Response -> return        |
|       |                                        |
| MISS  v                                        |
| [2] Origin Request  <- cache miss only         |
|       | can rewrite URL, change origin         |
|       v                                        |
|    Your Origin                                 |
|       v                                        |
| [3] Origin Response <- modify before caching   |
|       v                                        |
|    Stored in edge cache                        |
|       v                                        |
| [4] Viewer Response <- always on return        |
|       v                                        |
|    Returned to viewer                          |
+-----------------------------------------------+
```

Trigger limits at a glance:

| Trigger           | Runs on      | Timeout | Body access |
|-------------------|--------------|---------|-------------|
| Viewer Request    | Every request| 5 s     | No          |
| Origin Request    | Cache miss   | 30 s    | No          |
| Origin Response   | Cache miss   | 30 s    | Yes         |
| Viewer Response   | Every request| 5 s     | No          |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User (Frankfurt)
  |
  v
CloudFront Frankfurt PoP        <- YOU ARE HERE
  |
  v
[1] Viewer Request Lambda fires (~2 ms)
  - Validates JWT cookie
  - Invalid? -> return 401 immediately
  - Valid? -> pass through
  |
  v
Cache lookup
  |
  +-- HIT  --> [4] Viewer Response -> user (~5 ms)
  |
  +-- MISS -->
        v
       [2] Origin Request Lambda fires
         - Injects auth header for S3 signed URL
         - Rewrites URL if needed
        v
       S3 Origin (us-east-1)
        v
       [3] Origin Response Lambda fires
         - Adds Cache-Control header if missing
        v
       Edge cache stores response
        v
       [4] Viewer Response -> user (~200 ms)
```

**FAILURE PATH:** If the Lambda function throws an unhandled exception, CloudFront returns `502`. If the function times out, CloudFront returns `504`. Lambda errors at the Viewer Request trigger prevent origin from ever being called - a crash in auth logic takes down the entire distribution path.

**WHAT CHANGES AT SCALE:** Lambda@Edge does not share the warm pool of regional Lambda. Cold starts happen at each PoP independently. High-traffic PoPs maintain warm execution environments; low-traffic PoPs cold-start frequently. For Viewer Request (runs on every request), cold starts in low-traffic PoPs can add 100–500 ms unpredictably.

---

### 💻 Code Example

**BAD - Auth check at origin (unnecessary round-trip):**
```javascript
// Origin Lambda (us-east-1) validates JWT on every request
// Even for cached assets, request must reach us-east-1
exports.handler = async (event) => {
  const token = event.headers['Authorization'];
  if (!isValidJWT(token)) {
    return { statusCode: 401, body: 'Unauthorized' };
  }
  // serve content...
};
```

**GOOD - Auth at Viewer Request edge trigger:**
```javascript
// Lambda@Edge: us-east-1 deploy, attached to Viewer Request
// Runs at nearest PoP; invalid tokens never reach origin
const jwt = require('jsonwebtoken');
const PUBLIC_KEY = process.env.JWT_PUBLIC_KEY;

exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const cookies = parseCookies(
    request.headers['cookie'] || []
  );

  try {
    jwt.verify(cookies['auth-token'], PUBLIC_KEY);
    return request; // valid: pass through to cache/origin
  } catch (e) {
    return {                    // invalid: short-circuit
      status: '401',
      statusDescription: 'Unauthorized',
      headers: {
        'content-type': [{ value: 'text/plain' }]
      },
      body: 'Unauthorized'
    };
  }
};

function parseCookies(cookieHeaders) {
  const result = {};
  cookieHeaders.forEach(({ value }) => {
    value.split(';').forEach(c => {
      const [k, v] = c.trim().split('=');
      result[k] = v;
    });
  });
  return result;
}
```

---

### ⚖️ Comparison Table

| Feature              | Lambda@Edge       | CloudFront Functions | Cloudflare Workers |
|----------------------|-------------------|---------------------|--------------------|
| Runtime              | Node.js, Python   | JS (subset)         | JS, Wasm           |
| Memory limit         | 128 MB            | 2 MB                | 128 MB             |
| Timeout              | 5 s / 30 s        | 1 ms (CPU)          | 50 ms (CPU)        |
| Trigger points       | 4 (all phases)    | 2 (viewer only)     | Every request      |
| Body access          | Origin triggers   | No                  | Yes                |
| VPC access           | No                | No                  | No                 |
| Cold starts          | Yes (per PoP)     | No (always warm)    | Very fast          |
| Price per request    | ~$0.60/million    | ~$0.10/million      | Included in plan   |
| Use case             | Complex logic     | Simple rewrites      | Full edge apps     |

---

### 🔁 Flow / Lifecycle

**Function Deployment Lifecycle:**

```
+-----------------------------------------------+
| 1. WRITE   -> Author function in us-east-1    |
| 2. PUBLISH -> Create numbered version (not    |
|               $LATEST)                        |
| 3. ATTACH  -> Link ARN to CF cache behaviour  |
| 4. DEPLOY  -> CF replicates to 400+ PoPs      |
|              (~15 min propagation)            |
| 5. EXECUTE -> PoP invokes on trigger event    |
| 6. WARM    -> Execution env reused per PoP    |
| 7. COLD    -> New PoP or idle env: cold start |
| 8. UPDATE  -> Publish new version, re-attach  |
+-----------------------------------------------+
```

**Trigger Execution Lifecycle per Request:**

1. **Receive** - PoP receives CloudFront event object
2. **Invoke** - Lambda execution environment runs handler
3. **Decide** - Return modified `request`/`response` (pass-through) OR full response (short-circuit)
4. **Continue** - CloudFront proceeds to next step (cache lookup or origin) based on return value

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Lambda@Edge runs in us-east-1" | It deploys from us-east-1 but executes at the nearest PoP to the user - potentially any of 400+ locations. |
| "It's the same as regular Lambda" | Hard limits differ: 128 MB max, no VPC, no `$LATEST`, no layers >1 MB, no `/tmp` persistence across requests. |
| "Viewer Request is cheapest" | Viewer Request runs on every single request; Origin Request runs only on cache misses. For per-origin logic, Origin Request is far cheaper. |
| "Cold starts don't matter at edge" | Each PoP has its own execution pool. Low-traffic PoPs cold-start frequently, adding 100–500 ms unpredictably for global users. |
| "CloudFront Functions is the same" | CF Functions are cheaper and always warm but have a 1 ms CPU limit, 2 MB memory, and no body access - unsuitable for crypto (JWT validation) or complex logic. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - 502 errors from Lambda exception**

**Symptom:** Users receive `502 Bad Gateway`; CloudFront logs show `LambdaExecutionError`.
**Root Cause:** Unhandled exception in Lambda@Edge function code (e.g. missing header, JSON parse error).
**Diagnostic:**
```bash
# Logs appear in the region where request was served, NOT us-east-1
# Check CloudWatch in the closest region to affected users
aws logs filter-log-events \
  --log-group-name \
    "/aws/lambda/us-east-1.my-viewer-request-fn" \
  --filter-pattern "ERROR" \
  --region eu-west-1   # region where request was processed
```
**Fix:** Add `try/catch` around all header and cookie access. Always validate that headers exist before reading `.value`. Return a safe fallback response rather than throwing.
**Prevention:** Test functions with all CloudFront event shapes (missing headers, empty cookies). Use a canary deployment - attach new version to a low-traffic cache behaviour first.

---

**Mode 2 - Function deployed but old behaviour persists**

**Symptom:** Updated function logic not executing; old behaviour observed 30 minutes after deploy.
**Root Cause:** CloudFront distribution still references the old Lambda version ARN. Redeploying the function without updating the distribution attachment has no effect.
**Diagnostic:**
```bash
# Confirm which version is attached to the distribution
aws cloudfront get-distribution-config \
  --id EDFDVBD6EXAMPLE \
  | jq '.DistributionConfig.DefaultCacheBehavior
         .LambdaFunctionAssociations'
# Check: is FunctionARN pointing to the new version?
```
**Fix:** Publish a new version, update the distribution config to reference the new ARN, deploy the distribution update, wait for propagation.
**Prevention:** Use IaC (CDK or CloudFormation) to manage the ARN reference. Never manually attach versions - automate as part of the deployment pipeline.

---

**Mode 3 - Intermittent high latency on first requests**

**Symptom:** P50 latency is fast but P99 spikes to 500 ms+ unexpectedly in low-traffic regions.
**Root Cause:** Lambda@Edge cold starts at PoPs that have had no recent traffic. The execution environment must be initialised from scratch, including loading runtime, code, and dependencies.
**Diagnostic:**
```bash
# Inspect init duration in CloudWatch logs
aws logs filter-log-events \
  --log-group-name \
    "/aws/lambda/us-east-1.my-fn" \
  --filter-pattern "REPORT Init Duration" \
  --region ap-southeast-1
# Init Duration present = cold start
```
**Fix:** Minimise the deployment package size (no heavy dependencies). Keep the handler module small. Use `process.env` caching for public keys outside the handler function body.
**Prevention:** For latency-sensitive paths, consider CloudFront Functions (always warm) for simple logic. Reserve Lambda@Edge for logic that genuinely requires its capabilities.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- AWS CloudFront - Lambda@Edge is a feature of CloudFront; understanding distributions, cache behaviours, and PoPs is required
- AWS Lambda - execution model, cold starts, handler signature, runtime limits
- CDN - the cache-hit/miss flow that determines when each trigger fires

**Builds On This (learn these next):**
- CloudFront Functions - lighter-weight alternative for simple viewer-side transformations
- Edge Computing - the broader pattern Lambda@Edge implements
- AWS WAF - complementary security layer attachable to the same CloudFront distribution

**Alternatives / Comparisons:**
- CloudFront Functions - faster, cheaper, always warm, but severely limited in capability
- Cloudflare Workers - equivalent edge compute on Cloudflare's network with broader runtime
- Fastly Compute@Edge - Wasm-based edge compute with strong isolation guarantees

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Lambda at CloudFront PoPs         |
| PROBLEM      | Origin round-trip for edge logic  |
| KEY INSIGHT  | 4 triggers = full req/resp control|
| USE WHEN     | Auth, A/B test, URL rewrite, headers|
| AVOID WHEN   | VPC resources needed; >5 s logic  |
| TRADE-OFF    | Power vs cold starts + limits     |
| ONE-LINER    | Deploy to us-east-1, attach to CF  |
| NEXT EXPLORE | CloudFront Functions, WAF          |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** You want to validate a JWT on every request. Lambda@Edge Viewer Request runs on 100% of traffic. CloudFront Functions also supports Viewer Request but has a 1 ms CPU limit. JWT verification with RS256 takes ~2 ms. Which trigger and tool do you choose, and what constraints drive that decision?

2. **(Root Cause)** A Lambda@Edge function works perfectly in testing but throws `502` errors for roughly 2% of global requests in production. The function reads `event.Records[0].cf.request.headers['accept-language'][0].value`. What is the most likely root cause, and how would you make the function resilient?

3. **(System Interaction)** You need to A/B test two origins: 90% of traffic to `origin-a.example.com`, 10% to `origin-b.example.com`. Which of the four Lambda@Edge triggers do you use, and why does using Viewer Request instead of Origin Request for this task lead to a subtle caching bug?
