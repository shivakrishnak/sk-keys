---
layout: default
title: "API Security Best Practices"
parent: "HTTP & APIs"
nav_order: 260
permalink: /http-apis/api-security-best-practices/
number: "0260"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP, Authentication, OWASP
used_by: REST APIs, Platform Security, API Gateways
related: JWT, OAuth2, CORS, SSRF, SQL Injection, CSRF, API Rate Limiting
tags:
  - api-security
  - owasp
  - authentication
  - authorization
  - intermediate
---

# 260 — API Security Best Practices

⚡ TL;DR — API security best practices are the set of defenses addressing the OWASP API Security Top 10: use authentication on every endpoint (JWT/OAuth2), enforce authorization at object and function level (BOLA, BFLA), validate all input, never expose sensitive data unnecessarily, rate-limit requests, avoid mass assignment, log security events, and use HTTPS everywhere — together forming a defense-in-depth strategy for production APIs.

| #260 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP, Authentication, OWASP | |
| **Used by:** | REST APIs, Platform Security, API Gateways | |
| **Related:** | JWT, OAuth2, CORS, SSRF, SQL Injection, CSRF, API Rate Limiting | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An API endpoint `GET /api/orders/{orderId}` doesn't check if the requesting user owns
the order. Any authenticated user can access any other user's orders by guessing order IDs.
This is BOLA (Broken Object Level Authorization) — the #1 OWASP API Security risk, found in
real breaches at companies like Parler (exposed all user data), Instagram (exposed user phone
numbers), Peloton (exposed all user profiles). API security failures cost millions in breach
costs and regulatory fines. Most are not novel attacks — they're predictable, well-documented
vulnerabilities that shouldn't exist in production APIs.

---

### 📘 Textbook Definition

**API Security Best Practices** are the set of controls addressing the OWASP API Security
Top 10 — a list of the most critical API security risks. Key risks and mitigations:
**API1 BOLA** (Broken Object Level Authorization): validate object ownership on every
object-level operation. **API2 Broken Authentication**: use JWT/OAuth2, enforce token
expiry, validate all claims. **API3 Broken Object Property Level Authorization**: never
return all object fields to all callers; enforce field-level visibility by role.
**API4 Unrestricted Resource Consumption**: rate limit, validate payload sizes.
**API5 BFLA** (Broken Function Level Authorization): check permissions for every function,
not just endpoint-level. **API6 Unrestricted Access to Sensitive Business Flows**: protect
scraping-prone endpoints with CAPTCHA/rate limiting. **API7 SSRF**: validate and restrict
URLs in user-supplied input. **API8 Security Misconfiguration**: harden headers (HSTS,
CSP, no server headers), disable debug, remove test endpoints. **API9 Improper Inventory
Management**: track all API versions; no shadow/undocumented endpoints. **API10 Unsafe
Consumption of APIs**: validate data from external APIs before using.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API security best practices follow OWASP's API Top 10 — the same predictable vulnerabilities
appear in breach after breach; implement the checklist and you prevent the most common attacks.

**One analogy:**
> API security is like a building's access control system.
> Every door (endpoint) needs: a key reader (authentication), 
> a check that THIS key accesses THIS room (object-level authorization), 
> size limits on what can be brought in (payload validation),
> a log of who entered (audit logging), 
> an alarm system (rate limiting blocks attackers before they succeed).
> Security theater: a guard at the front door but all windows unlocked (authentication
> at the gateway but no object-level checks in services).

---

### 🔩 First Principles Explanation

**OWASP API SECURITY TOP 10 — ACTIONABLE CHECKLIST:**

```
API1 — BOLA (Broken Object Level Authorization):
  ATTACK: GET /api/orders/ORD-001 → returns competitor's order by guessing ID
  FIX:    Always filter by authenticated user:
  ✅ SELECT * FROM orders WHERE id = ? AND user_id = ?  ← MUST verify ownership
  ✅ orderRepository.findByIdAndUserId(orderId, currentUser.getId())
  ❌ orderRepository.findById(orderId)  ← MISSING ownership check = BOLA

API2 — Broken Authentication:
  ATTACK: JWT with alg:none accepted; expired tokens accepted; weak secrets
  FIX:    Validate token on every request:
  ✅ Verify JWT signature with strong key (RS256 preferred over HS256)
  ✅ Validate exp (expiry), iss (issuer), aud (audience) claims
  ✅ Refuse alg:none, alg:none, or alg:RS256 with symmetric key
  ✅ Token rotation: short-lived access tokens (15 min) + refresh tokens

API3 — Broken Object Property Level Authorization:
  ATTACK: GET /api/users/1 returns salary field visible to all users
  FIX:    Role-based field projection:
  ✅ Public: {id, name, avatar}
  ✅ Self/Admin: {id, name, avatar, email, salary, ssn}
  ❌ Never return all fields to all callers (check WHO can see WHAT)

API4 — Unrestricted Resource Consumption (Rate Limiting):
  ATTACK: 10,000 req/sec file upload endpoint crashes server
  FIX:    ✅ Rate limit per user/IP/key
          ✅ File size limit (max-file-size: 10MB)
          ✅ Pagination enforced: max limit=100

API5 — BFLA (Broken Function Level Authorization):
  ATTACK: Regular user calls DELETE /api/admin/users/1 → succeeds
  FIX:    ✅ Role check on EVERY function, not just URL pattern:
          @PreAuthorize("hasRole('ADMIN')")  ← on each admin method
          Not just: antMatchers("/api/admin/**").hasRole("ADMIN")
          (URL matchers can be bypassed; method-level is safer)

API7 — SSRF:
  ATTACK: POST /api/webhooks {"url": "http://169.254.169.254/latest/metadata"}
  FIX:    ✅ Block private/metadata IP ranges
          ✅ Allowlist of permitted URL hostnames
          ✅ Resolve DNS before blocklist check (prevent DNS rebinding)

API8 — Security Misconfiguration:
  ✅ HTTPS everywhere (HSTS header)
  ✅ Remove debug endpoints (/actuator/env exposed in production)
  ✅ Security headers: X-Content-Type-Options, X-Frame-Options
  ✅ Remove server version header (don't advertise: Server: Apache 2.4.1)
  ✅ Disable CORS wildcard for APIs with credentials
  ✅ No default passwords/API keys in production config

MASS ASSIGNMENT (API3 related):
  ATTACK: PUT /api/users/1 Body: {"name": "Alice", "role": "ADMIN"}
  FIX:    ✅ Use DTOs (not entity directly) for request binding
          ✅ DTO only has fields consumer is allowed to set:
          record UpdateUserRequest(String name, String email) {} ← no role field
          ❌ Never bind request body directly to JPA entity
```

---

### 🧪 Thought Experiment

**SCENARIO:** BOLA vulnerability in an e-commerce API.

```
VULNERABLE CODE:
  @GetMapping("/api/orders/{orderId}")
  public OrderDto getOrder(@PathVariable Long orderId) {
      return orderRepository.findById(orderId)  ← NO ownership check
          .map(this::toDto)
          .orElseThrow(() -> new ResourceNotFoundException("Order not found"));
  }

ATTACK:
  Authenticated user1: GET /api/orders/1001 → their order
  User1 tries: GET /api/orders/1002 → ANOTHER USER'S ORDER (returned!)
  User1 writes script: for i in range(1000, 2000): GET /api/orders/{i}
  → Scrapes 1000 orders including PII, addresses, payment method hints

SECURE VERSION:
  @GetMapping("/api/orders/{orderId}")
  public OrderDto getOrder(@PathVariable Long orderId,
                           @AuthenticationPrincipal User currentUser) {
      // MUST check: does this user OWN this order?
      return orderRepository.findByIdAndUserId(orderId, currentUser.getId())
          .map(this::toDto)
          .orElseThrow(() -> new ResourceNotFoundException(
              "Order not found"));  ← same error as "not yours" (no info leakage)
  }
  
  NOTE: Return the same error for "not found" AND "not yours" — 
        attackers probing access should not know if a resource exists.
```

---

### 🧠 Mental Model / Analogy

> API security is an onion — defense in depth.
> Layer 1 (outer): API Gateway — rate limiting, DDoS protection, IP filtering
> Layer 2: Authentication — is this a valid user with a valid token?
> Layer 3: Authorization — does this user have permission for THIS operation?
> Layer 4: Object-level authorization — does this user OWN this specific resource?
> Layer 5: Input validation — is this input safe to process?
> Layer 6: Output filtering — are we not returning too much data?
> An attacker who bypasses outer layers still faces inner layers.
> Security fails when ANY layer is absent.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Check auth on every endpoint (who are you?), check ownership on every resource (is this yours?), validate all input, never expose sensitive fields, use HTTPS.

**Level 2:** Implement OWASP Top 10 checklist: BOLA (ownership check), BFLA (method-level @PreAuthorize), mass assignment prevention (DTO not entity), rate limiting, SSRF prevention, security headers.

**Level 3:** Security design principles: principle of least privilege (minimal token scopes), defense in depth (multiple layers), fail-secure (deny by default, not allow by default), no security by obscurity. Spring Security: `@PreAuthorize` for method-level authorization, JWT secret rotation, `@JsonIgnore` for sensitive fields with role-based serialization, `@Valid` + custom validators for business-rule input validation.

**Level 4:** API security is adversarial — attackers study OWASP, probe for known patterns, and automate attacks. The most impactful investments: BOLA prevention (the most common breach vector, trivially exploited), authentication token security (short-lived tokens reduce blast radius on compromise), and comprehensive audit logging (detection requires knowing what happened). Security misconfiguration (API8) is often the easiest win: removing debug endpoints, setting security headers, and disabling verbose error messages requires no complex code changes and significantly reduces attack surface. API security testing in CI: OWASP ZAP (dynamic analysis), Semgrep (static analysis for security patterns), and manual penetration testing before public API launch.

---

### ⚙️ How It Works (Mechanism)

```
SPRING SECURITY — LAYERED API SECURITY:

  Security filter chain:
  HTTP Request
       │
  [Rate Limiting Filter]          ← Layer 1: request volume
       │
  [JWT Authentication Filter]    ← Layer 2: valid token, extract user
       │
  [CORS Filter]                  ← Cross-origin policy
       │
  [Spring Security Authorization] ← Layer 3: hasRole checks (URL-level)
       │
  [Controller @PreAuthorize]     ← Layer 4: method-level authorization
       │
  [Service BOLA check]           ← Layer 5: object ownership
       │
  [Input Validation @Valid]      ← Layer 6: input safety
       │
  [Field-level output filter]    ← Layer 7: output minimization
       │
  Response

  NEVER rely on a SINGLE layer. Multiple layers = defense in depth.
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
SECURE API REQUEST FLOW:

  POST /api/v1/orders/{id}/refund
  Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...

  1. Rate limit check: consumer under limit? → proceed
  2. JWT verification: valid signature, not expired, correct issuer/audience → proceed
  3. Extract user: userId = 42, role = CUSTOMER
  4. URL-level authz: /api/v1/orders/** → requires CUSTOMER or ADMIN role → proceed
  5. Method-level: @PreAuthorize("hasAnyRole('CUSTOMER','ADMIN')") → proceed
  6. BOLA check: does order {id} belong to userId 42?
     orderRepository.findByIdAndUserId(id, 42) → found → proceed
  7. BFLA check: is CUSTOMER allowed to initiate refunds?
     @PreAuthorize("hasRole('CUSTOMER') and @orderSecurity.canRefund(#id, principal)")
     → business rule: within 30 days of delivery → proceed
  8. Input validation: @Valid refundRequest → valid → proceed
  9. Process refund
  10. Response: filter fields — CUSTOMER sees {refundId, amount, status}
               ADMIN would see {refundId, amount, status, processorId, internalNotes}

  Each layer independently enforces a specific security concern.
```

---

### 💻 Code Example

```java
// BOLA-safe order controller with defense in depth
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    @GetMapping("/{orderId}")
    @PreAuthorize("hasAnyRole('CUSTOMER', 'ADMIN')")
    public ResponseEntity<OrderDto> getOrder(
            @PathVariable Long orderId,
            @AuthenticationPrincipal UserDetails user) {

        // For ADMIN: can see any order; for CUSTOMER: only their own
        Optional<Order> order;
        if (user.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"))) {
            order = orderRepository.findById(orderId);
        } else {
            // BOLA prevention: scope query to the authenticated user
            order = orderRepository.findByIdAndUserEmail(orderId, user.getUsername());
        }

        return order
            .map(o -> ResponseEntity.ok(toDto(o, user)))  // field projection by role
            .orElse(ResponseEntity.notFound().build());   // same response: not yours = not found
    }

    private OrderDto toDto(Order order, UserDetails user) {
        OrderDto dto = new OrderDto(order.getId(), order.getStatus(), order.getTotal());
        // Only admins see internal fields
        if (user.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"))) {
            dto.setInternalNotes(order.getInternalNotes());
            dto.setProcessorTransactionId(order.getProcessorId());
        }
        return dto;
    }
}

// Mass assignment prevention: DTO not entity
record CreateOrderRequest(
    @NotNull @Positive BigDecimal amount,
    @NotBlank String productId,
    @Valid @NotNull ShippingAddress shippingAddress
    // NOTE: no 'userId', 'status', 'internalNotes' — consumer can't set these
) {}

// Security headers configuration
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    return http
        .headers(headers -> headers
            .contentTypeOptions(Customizer.withDefaults())     // X-Content-Type-Options: nosniff
            .frameOptions(FrameOptionsConfig::deny)            // X-Frame-Options: DENY
            .httpStrictTransportSecurity(hsts -> hsts          // HSTS
                .maxAgeInSeconds(31536000).includeSubDomains(true))
        )
        .csrf(AbstractHttpConfigurer::disable)  // Disabled for JWT stateless APIs
        .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .anyRequest().authenticated()
        )
        .build();
}
```

---

### ⚖️ Comparison Table

| OWASP API Risk | Attack Pattern | Primary Defense |
|---|---|---|
| **BOLA (API1)** | `GET /orders/{other_user_id}` | `findByIdAndUserId()` ownership check |
| **BFLA (API5)** | `DELETE /admin/users/1` as regular user | `@PreAuthorize` per method |
| **Mass Assignment** | `PUT /users/1 {"role":"ADMIN"}` | DTO with only writable fields |
| **SSRF (API7)** | `{"url": "http://169.254.169.254"}` | IP blocklist + allowlist |
| **Broken Auth (API2)** | `alg:none` JWT, expired token | Validate all claims + refuse weak alg |
| **Data Overexposure (API3)** | Get salary field as non-admin | Role-based field projection in DTOs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| API Gateway auth = full security | Gateways check token presence/validity. They do NOT check: does user own this order? Is user admin for this operation? Object/function level authorization must be in the service code |
| 404 for unauthorized access is wrong | Returning 404 (not 403) for resources you don't own is CORRECT — prevents resource existence enumeration. "Order doesn't exist" = same as "you don't own it" from attacker's perspective |
| Validation at the client is secure | Client-side validation is UX, not security. Server MUST independently validate all inputs. Clients can be bypassed with direct API calls (curl, Burp Suite) |

---

### 🚨 Failure Modes & Diagnosis

**BOLA in Production — Detection**

**Symptom:**
Unusual GET request patterns: one API key calling GET /orders/{id} sequentially
for thousands of consecutive IDs. Data exfiltration in progress.

Detection:
```
Anomaly detection alert:
  "API key KEY_ABC made 5,000 GET /api/orders/{id} requests in 10 minutes
   with 4,800 distinct order IDs (sequential pattern)"
  → Alert: BOLA probe detected

Indicators:
  - Sequential IDs in GET requests
  - High volume from single consumer
  - Requests for resources across multiple users (observable if logged properly)

Immediate response:
  Block API key
  Assess: which orders were accessed?
  Notify: affected users (GDPR/CCPA breach notification may be required)

Prevention:
  1. findByIdAndUserId() in all object-level queries
  2. Non-sequential IDs (UUID v4 or ULID — not guessable integers)
  3. Alert on sequential ID scanning pattern
```

---

### 🔗 Related Keywords

- `JWT` — the authentication mechanism (API2 protection)
- `OAuth2` — authorization framework for API access
- `CORS` — cross-origin resource sharing security
- `SSRF` — server-side request forgery (API7)
- `API Rate Limiting` — protection against resource consumption attacks (API4)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BOLA FIX     │ findByIdAndUserId() — ALWAYS             │
│ BFLA FIX     │ @PreAuthorize on every admin method       │
│ MASS ASSIGN  │ Use DTOs, not entities, for request body  │
│ INPUT VALID  │ @Valid + custom validators in service     │
│ OUTPUT CTRL  │ Role-based field projection in DTOs       │
│ RATE LIMIT   │ Per-user, per-IP, per-key throttling      │
│ SSRF FIX     │ IP blocklist (metadata ranges) + allowlist│
├──────────────┼───────────────────────────────────────────┤
│ OWASP TOP    │ BOLA, BrkAuth, PropLvlAuthz, ResConsump  │
│              │ BFLA, BizFlow, SSRF, Misconfig, Inventory│
│              │ Unsafe 3rd Party Consumption             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Authenticate, authorize, validate, limit"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A security audit finds that 3 of your top 5 API endpoints are vulnerable to BOLA:
the code uses `findById(id)` without checking user ownership because the original developers assumed "only authenticated users will call these endpoints." The fix requires adding `findByIdAndUserId()` to 47 repository calls across 12 services. The PM says "it's not urgent, no breach has happened yet." The security team says "this is critical." Frame the argument using the BOLA breach statistics from OWASP, estimate the blast radius if one endpoint is exploited, and make the business case for immediate remediation vs. the PM's "wait and see" stance.
