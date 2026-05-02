---
layout: default
title: "API Deprecation Strategy"
parent: "HTTP & APIs"
nav_order: 258
permalink: /http-apis/api-deprecation-strategy/
number: "0258"
category: HTTP & APIs
difficulty: ★★☆
depends_on: API Versioning, API Backward Compatibility, HTTP
used_by: Public APIs, Platform Teams, Microservices
related: API Versioning, API Backward Compatibility, HTTP Headers
tags:
  - api-deprecation
  - sunset
  - versioning
  - breaking-changes
  - intermediate
---

# 258 — API Deprecation Strategy

⚡ TL;DR — API deprecation strategy is the process and policies for safely retiring old API versions or endpoints: announce deprecation early (via `Deprecation` + `Sunset` headers, changelog, email), provide a migration path, enforce a sunset date after which the endpoint is removed, and monitor which consumers are still calling deprecated endpoints to target migration outreach.

┌──────────────────────────────────────────────────────────────────────────┐
│ #258 │ Category: HTTP & APIs │ Difficulty: ★★☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ API Versioning, API Backward │ │
│ │ Compatibility, HTTP │ │
│ Used by: │ Public APIs, Platform Teams, │ │
│ │ Microservices │ │
│ Related: │ API Versioning, API Backward Compat│ │
│ │ HTTP Headers │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company maintains 6 API versions simultaneously because they never deprecated old ones.
Engineering supports v1 through v6 of the user service. v1 uses a broken auth model,
v2-v4 have security vulnerabilities, v5 has performance issues. 20% of API traffic still
hits v1 (legacy integration nobody knows about). Nobody knows which companies still use v1.
Removing v1 risks breaking an unknown customer. The team can never safely remove anything.
Technical debt accumulates: 6 versions × N endpoints = 6N code paths to maintain.

---

### 📘 Textbook Definition

**API Deprecation** is the formal process of marking an API version, endpoint, parameter,
or response field as "to be removed in a future release," giving consumers time to migrate.
A complete deprecation strategy includes: (1) **Announcement**: deprecation notice via
response headers (`Deprecation`, `Sunset`, `Link` pointing to successor), changelog,
developer portal notification, email to API consumers. (2) **Migration path**: documentation
of what replaces the deprecated item + migration guide. (3) **Sunset enforcement**: after the
announced sunset date, the endpoint returns `410 Gone` (permanent removal) rather than
`404 Not Found` (never existed). (4) **Consumer tracking**: log which API keys/consumers
still call deprecated endpoints; targeted outreach before removal. RFC 8594 standardizes
the `Sunset` HTTP header for machine-readable sunset date communication.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API deprecation strategy is the plan for retiring old API versions gracefully — announce,
provide migration path, set a date, then remove — without surprising consumers.

**One analogy:**

> API deprecation is like a building demolition notice.
> You don't demolish a building while people are still inside.
> You post notices 6 months in advance: "This building closes October 31."
> You direct occupants to the new building (migration path).
> You track who hasn't moved yet (usage monitoring).
> On the date: building closes, occupants who ignored warnings deal with the consequences.
> The sequence: announce → guide → monitor → enforce.

---

### 🔩 First Principles Explanation

**DEPRECATION HEADERS (RFC 8594 + RFC 9110):**

```
Response headers for deprecated endpoints:

  Deprecation: @1704067200           ← Unix timestamp when deprecation was announced
               (or "true" for generic)
  Sunset: Thu, 31 Dec 2026 23:59:59 GMT  ← When endpoint will be removed (RFC 8594)
  Link: </api/v2/users>; rel="successor-version"  ← Where to migrate to
  Link: <https://docs.example.com/migration/v1-to-v2>; rel="deprecation"  ← Migration guide

  These headers serve:
  1. Human developers: see headers in dev tools, understand timeline
  2. SDK clients: parse Deprecation/Sunset → log warnings automatically
  3. Monitoring tools: track which endpoints have upcoming sunsets
  4. API consumers: build alerts for approaching sunset dates
```

**DEPRECATION PHASES:**

```
PHASE 1 — ANNOUNCE (Day 0):
  ✅ New version (v2) released and stable
  ✅ Migration guide published
  ✅ Developer portal: deprecation notice visible
  ✅ Email to all API consumers with affected endpoints
  ✅ Add Deprecation + Sunset headers to all v1 responses
  ✅ Set sunset date: minimum 6 months public, 3 months internal

PHASE 2 — MONITOR (~ongoing):
  ✅ Dashboard: v1 API call volume over time
  ✅ Per-API-key breakdown: which consumers still calling v1?
  ✅ Threshold alerts: "Consumer X makes 5000 v1 calls/day — outreach needed"
  ✅ Reminder communications at 90-day, 30-day, 7-day, 1-day before sunset

PHASE 3 — ENFORCE (Sunset Date):
  ✅ v1 endpoints return 410 Gone (not 404)
  ✅ Response body: {"code": "API_DEPRECATED",
                     "message": "This API version was sunset on 2026-12-31.
                                 Please migrate to /api/v2/users.
                                 Migration guide: https://docs.example.com/migration"}
  ✅ Monitoring: spike in 410s expects; escalation path for missed migrations

PHASE 4 — REMOVE (post-sunset grace period):
  After confirming zero traffic to deprecated endpoints:
  Remove code, remove route, update documentation
  Final notification: "v1 completely removed"
```

---

### 🧪 Thought Experiment

**SCENARIO:** Stripe versioning policy (real-world reference).

```
STRIPE'S APPROACH (extreme backward compatibility):
  Each Stripe account is "pinned" to the API version at their first integration date.
  Stripe maintains EVERY version ever released (back to 2011).
  Breaking changes create a new version (YYYY-MM-DD format: "2024-04-10").
  Consumers can upgrade their version on their dashboard.
  Pro: zero forced migrations, extreme backward compatibility
  Con: Stripe maintains hundreds of active API versions simultaneously;
       immense engineering overhead

ALTERNATIVE: GITHUB's APPROACH (simpler):
  Uses API-Version header: "X-GitHub-Api-Version: 2022-11-28"
  Breaking changes create a new version date
  Old versions deprecated with sunset notice
  Forced migration after sunset
  Pro: consumers must migrate, but code stays clean
  Con: breaking changes more impactful

STANDARD PUBLIC API PRACTICE:
  /api/v1/ → /api/v2/ path versioning
  v1 deprecated upon v2 stable release
  Minimum 12-month sunset window for public APIs
  v1 → 410 Gone after sunset date
  Sunset window reduced to 3-6 months for internal APIs
```

---

### 🧠 Mental Model / Analogy

> API deprecation strategy is like a subscription service cancellation flow.
> A gym that wants to close one location:
>
> 1. Announces closure date 6 months ahead (deprecation notice)
> 2. Notifies all members, shows nearest alternative gym (migration path)
> 3. Sends reminders at 30-day, 7-day, 1-day before closure
> 4. On closure day: location physically closes (410 Gone)
> 5. Members who ignored all notices: now go to alternative location
>    The gym doesn't "surprise close" — that would be catastrophic for member trust.
>    Same for API consumers: trust is built by predictable, well-communicated deprecation.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Deprecation means "we're removing this — here's when and what to use instead." Always give a date, always provide the replacement, always monitor who still uses the old version.

**Level 2:** Add `Deprecation` and `Sunset` HTTP response headers (RFC 8594) to deprecated endpoints. Track deprecated endpoint usage per API key in your observability platform. Run consumer outreach 30 days before the sunset date.

**Level 3:** Design the full deprecation lifecycle: announce → monitor usage dashboard → targeted outreach to lagging consumers → enforced sunset (410 Gone). SDK clients should parse the `Deprecation` header and log a warning automatically. CI checks: use `oasdiff` or `Spectral` to detect when a field removal is introduced without a matching sunset date.

**Level 4:** The hard problem in API deprecation is the "long tail of forgotten integrations" — API keys that are technically active but belong to automations or companies that will never check their email. These are discovered only on the day of sunset when they break. The mitigation: granular usage monitoring at the consumer level (not just total volume), combined with proactive "we see you're still calling deprecated endpoint X — here's how to migrate." The organizational challenge: deprecations are often politically difficult. Teams that "own" consumers (internal or external) resist migration because it takes effort. A clear, enforced sunset policy with executive backing removes the ambiguity and creates a forcing function for migrations.

---

### ⚙️ How It Works (Mechanism)

```
DEPRECATION MONITORING IN PRACTICE:

  Metrics:
  - Counter: deprecated_api_calls_total{endpoint="/api/v1/users", api_key="key_abc"}
  - Dashboard: daily calls per endpoint + per consumer
  - Alert: when consumer volume > threshold N days before sunset

  Weekly email to lagging consumers (automated):
  "Your API key KEY_ABC made 10,432 calls to deprecated /api/v1/users last week.
   This endpoint sunsets on 2026-12-31 (92 days remaining).
   Migration guide: https://docs.example.com/migration/v1-to-v2
   Questions? Contact api-support@example.com"

  FILTER: only send if consumer has > X calls/day to deprecated endpoint
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
FULL DEPRECATION LIFECYCLE:

  T+0  (Day of v2 launch):
  - v1 gets Deprecation + Sunset headers
  - Migration guide published
  - Email to all v1 consumers

  T+3mo: v1 call volume: 60% migrated (down from 100%)
  - Targeted emails to remaining 40% consumers
  - Dashboard: per-consumer v1 call volume

  T+5mo: v1 call volume: 15% remaining
  - Reminder: "30 days to sunset"
  - Direct outreach to top 10 consumers by volume

  T+6mo (Sunset Date):
  - v1 returns 410 Gone
  - Expect support tickets from stragglers
  - Incident response: help remaining consumers migrate quickly

  T+7mo:
  - v1 call volume: ~1% (forgotten integrations)
  - Decision: remove v1 code (after confirming negligible traffic)
```

---

### 💻 Code Example

```java
// Spring Boot: global deprecation response header filter
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class DeprecationFilter extends OncePerRequestFilter {

    private static final Map<String, SunsetInfo> DEPRECATED_PATHS = Map.of(
        "/api/v1/", new SunsetInfo(
            Instant.parse("2026-12-31T23:59:59Z"),
            "/api/v2/",
            "https://docs.example.com/migration/v1-to-v2"
        )
    );

    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String path = request.getRequestURI();
        DEPRECATED_PATHS.entrySet().stream()
            .filter(e -> path.startsWith(e.getKey()))
            .findFirst()
            .ifPresent(entry -> {
                SunsetInfo info = entry.getValue();
                response.setHeader("Deprecation", "@" + info.announcedAt().getEpochSecond());
                response.setHeader("Sunset",
                    DateTimeFormatter.RFC_1123_DATE_TIME.format(
                        info.sunsetAt().atZone(ZoneOffset.UTC)));
                response.setHeader("Link",
                    "<" + info.successorPath() + ">; rel=\"successor-version\", " +
                    "<" + info.migrationGuide() + ">; rel=\"deprecation\"");

                // Track deprecated call
                meterRegistry.counter("api.deprecated.calls",
                    "endpoint", entry.getKey(),
                    "api_key", extractApiKey(request)).increment();
            });

        filterChain.doFilter(request, response);
    }
}

// 410 Gone controller for fully removed endpoints
@Controller
public class SunsetController {

    @RequestMapping("/api/v1/**")
    public ResponseEntity<ProblemDetail> v1Gone() {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.GONE);
        detail.setTitle("API Version Removed");
        detail.setDetail("API v1 was sunset on 2026-12-31. Migrate to /api/v2/. " +
                        "Guide: https://docs.example.com/migration/v1-to-v2");
        detail.setType(URI.create("https://api.example.com/errors/api-deprecated"));
        return ResponseEntity.status(HttpStatus.GONE).body(detail);
    }
}
```

---

### ⚖️ Comparison Table

| Strategy                         | Consumer Impact              | Maintenance Cost                            | Adoption                    |
| -------------------------------- | ---------------------------- | ------------------------------------------- | --------------------------- |
| **Versioned with sunset**        | Forced migration on deadline | Low (old code removed)                      | Most platform APIs          |
| **Stripe-style version pinning** | Never forced                 | Very high (all versions maintained forever) | Extreme scale only          |
| **Immediate removal**            | High (breaking)              | None                                        | Never (for production APIs) |
| **Perpetual deprecated**         | None                         | High (unmaintained code)                    | Antipattern                 |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                    |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 404 is the right response for removed endpoints | 404 means "never existed." 410 Gone is correct for removed endpoints: it's permanent and tells clients to remove bookmarks/references      |
| Deprecation is only needed for public APIs      | Internal APIs also need formal deprecation. Internal consumers also need migration time and tracking                                       |
| Email announcements are sufficient              | Email goes unread. HTTP headers (`Deprecation`, `Sunset`) are visible to developers actively working with the API and to automated tooling |

---

### 🚨 Failure Modes & Diagnosis

**Silent Consumer After Sunset**

Symptom:
Day after sunset: enterprise customer reports their integration broke. They never
received the deprecation notice. Support crisis; executive escalation.

Root Cause:
API key belongs to an integration built 3 years ago; the developer who built it left
the company; emails went to their old inbox; no developer actively monitored the API.

Prevention:

```
1. HTTP Deprecation/Sunset headers: visible in every response, not dependent on email
2. Monitoring: track deprecated API usage PER consumer; call volume chart
3. In-product notification: developer portal banner for API keys with deprecated calls
4. "Contact us" link in the 410 Gone response body + phone number for enterprise support
5. Emergency extension policy: for large enterprise customers: extend sunset 30 days
   with explicit written acknowledgment + migration commitment
```

---

### 🔗 Related Keywords

- `API Versioning` — the strategy that creates versions that will eventually need deprecation
- `API Backward Compatibility` — the expand-contract pattern reduces need for forced deprecations
- `RFC 8594` — the HTTP Sunset header specification
- `410 Gone` — correct HTTP status for permanently removed resources

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HEADERS      │ Deprecation: @{unix_timestamp}            │
│              │ Sunset: {RFC1123 date}                    │
│              │ Link: <new>; rel="successor-version"      │
├──────────────┼───────────────────────────────────────────┤
│ PHASES       │ Announce → Monitor → Outreach → Enforce   │
├──────────────┼───────────────────────────────────────────┤
│ REMOVAL CODE │ 410 Gone (not 404) after sunset           │
├──────────────┼───────────────────────────────────────────┤
│ WINDOWS      │ Public: 12 months minimum                 │
│              │ Internal: 3-6 months                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Announce → guide → monitor → enforce"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You manage a public API used by 2,000 external subscribers. Your API v1 has a security
vulnerability that requires a breaking fix. You estimate 60% of consumers will migrate in
3 months, 90% in 6 months, but some enterprise consumers say they need 18 months to migrate.
You cannot leave the security vulnerability active for 18 months. Design an emergency
deprecation strategy that addresses the security timeline (3-month hard deadline) while
minimizing consumer impact, and propose what you offer to enterprise consumers who genuinely
cannot migrate in 3 months (hint: consider security fix backport, v1-with-fix, or expedited
migration support).
