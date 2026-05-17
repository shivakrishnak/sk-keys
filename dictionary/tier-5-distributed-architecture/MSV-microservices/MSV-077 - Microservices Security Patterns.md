---
id: MSV-077
title: Microservices Security Patterns
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-075, MSV-076, MSV-010
used_by: MSV-076
related: MSV-076, MSV-075, MSV-010, MSV-020, MSV-065, MSV-072
tags:
  - microservices
  - security
  - deep-dive
  - patterns
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 77
permalink: /microservices/microservices-security-patterns/
---

# MSV-077 - Microservices Security Patterns

⚡ TL;DR - Microservices Security Patterns: a
catalog of proven security patterns for distributed
services. Core patterns: (1) Token-based authentication
(JWT/OAuth2 propagated through service chain);
(2) API Gateway auth (centralized authentication
at the edge - services trust the gateway);
(3) mTLS workload identity (service-to-service
authentication); (4) Secrets management (Vault:
never env vars); (5) OWASP API Security Top 10
countermeasures (broken object-level auth, mass
assignment, excessive data exposure). Each pattern:
solves a specific security problem in distributed
architectures that doesn't exist in monoliths.

| #077 | Category: Microservices | Difficulty: ★★★☆ |
|:---|:---|:---|
| **Depends on:** | mTLS in Microservices, Zero Trust Security, API Gateway | |
| **Used by:** | Zero Trust Security | |
| **Related:** | Zero Trust Security, mTLS in Microservices, API Gateway, Service Mesh, OpenTelemetry in Microservices, Sidecar Pattern | |

---

### 🔥 The Problem This Solves

**SECURITY IN MICROSERVICES: UNIQUE CHALLENGES:**
Monolith: one security perimeter, one AuthN/Z
check at the entry. Microservices: 30 services,
each a potential attack surface. Authentication:
who handles it in each service? Authorization:
how does service 5 know what service 1 already
verified about the user? Secrets: how do 30
services get and rotate DB passwords without
storing them in git? API surface: 30 REST APIs
= 30x the attack surface for injection, BOLA,
mass assignment. Security patterns: proven solutions
for each of these microservices-specific problems.

---

### 📘 Textbook Definition

**Microservices Security Patterns** is the collection
of architectural patterns that address the security
challenges unique to distributed microservices
architectures. Key patterns:

**Authentication patterns:**
- **Token Relay / JWT Propagation**: user authenticates
  at API Gateway; receives JWT. JWT: propagated
  in Authorization header through the service
  call chain. Each service: validates JWT signature
  (no round-trip to auth server).
- **API Gateway Auth**: API Gateway handles all
  external authentication. Internal services:
  trust the Gateway's forwarded identity headers.
  Simpler but creates Gateway as single point of
  trust (if compromised: all internal trust fails).
- **mTLS Workload Identity**: service-to-service
  auth via SPIFFE/X.509 certs (see MSV-075).

**Authorization patterns:**
- **Claim-based authorization**: JWT contains
  claims (roles, scopes, user attributes). Services:
  authorize based on claims.
- **ABAC (Attribute-Based Access Control)**:
  authorization based on user attributes + resource
  attributes + environment. OPA policy language.
- **OAuth2 Scopes**: API-specific permission sets.
  Clients request specific scopes; services
  verify scope presence in JWT.

**Secrets management patterns:**
- **Vault Agent Sidecar**: Vault issues dynamic
  short-lived secrets, injects as files.
- **External Secrets Operator**: syncs secrets
  from Vault/AWS SSM into Kubernetes Secrets.

**Network security patterns:**
- **NetworkPolicy**: K8s L3/L4 segmentation.
- **mTLS + AuthorizationPolicy**: L4 + L7 Zero Trust.

**OWASP API Security Top 10 countermeasures:**
Broken Object Level Authorization (BOLA), Broken
Authentication, Excessive Data Exposure, Lack of
Resources + Rate Limiting, Broken Function Level
Authorization, Mass Assignment, Security Misconfiguration,
Injection, Improper Assets Management, Insufficient
Logging + Monitoring.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Microservices security: authentication (who are
you?) + authorization (what can you do?) + secrets
management (no plaintext creds) + network security
(mTLS + network policy). Each is a distinct pattern.

**One analogy:**
> Security in microservices is like security
> at an airport. Check-in (API Gateway): verifies
> identity (passport = JWT), issues boarding pass
> (authorization token). Security checkpoint (service
> AuthZ): scans boarding pass for the specific
> gate. Gate (individual service): verifies boarding
> pass for this specific flight (resource). You
> don't re-prove your passport at every gate;
> the boarding pass carries the proof. mTLS: every
> airline employee (service) also has a badge
> (workload cert). External cameras (OPA) watch
> for policy violations at all times.

**One insight:**
The most dangerous OWASP API Security vulnerability
in microservices is BOLA (Broken Object Level
Authorization) - not injection. Why: each service
exposes objects (orders, payments, customers) by
ID. Service must verify: does the REQUESTING USER
own this object? Easy to forget in a single
service; critical in 30 services. Pattern: JWT
claim contains `userId`; each service verifies
`object.userId == jwt.userId` before any operation.

---

### 🔩 First Principles Explanation

**JWT PROPAGATION PATTERN:**

```
                     JWT FLOW THROUGH SERVICE CHAIN

Browser/Client
  | POST /login {credentials}
  v
Auth Service (Keycloak/Auth0)
  Validates credentials
  Issues JWT:
    sub: user-123
    email: alice@example.com
    roles: ["customer", "premium"]
    scope: "orders:read orders:write payments:read"
    exp: now + 1h
    iss: https://auth.company.com
  Returns: {access_token: "eyJ..."}

Client -> API Gateway
  Authorization: Bearer eyJ...
  Gateway:
    Validates: JWT signature (public key from JWKS)
    Checks: exp not expired
    Checks: iss trusted
    Forwards request + JWT to order-service
    (does NOT strip the JWT)

API Gateway -> order-service
  Authorization: Bearer eyJ... (same JWT)
  Order-service:
    Validates: JWT (signature + exp)
    Extracts: sub=user-123, scope includes orders:write
    Checks: does this user own order-456?
      SELECT userId FROM orders WHERE id = 456;
      Assert: result.userId == jwt.sub (BOLA check)
    Calls: payment-service
    Forwards: same JWT in Authorization header

Order-service -> payment-service
  Authorization: Bearer eyJ... (same JWT forwarded)
  mTLS: Envoy also verifies order-service cert
  Payment-service:
    Validates: JWT (user identity)
    Validates: mTLS (workload identity)
    Checks: scope includes payments:read
    Checks: does this user own this payment?
    Processes: authorized operation

Key: JWT carries user context end-to-end
     No re-authentication at each service
     Each service: validates LOCALLY (no auth server call)
     Workload identity (mTLS): orthogonal to user identity
```

**OAUTH2 SCOPES IN MICROSERVICES:**

```
Scope design: granular, action-based
  BAD scopes: read, write, admin
    ("admin" scope = access to everything)
  
  GOOD scopes: resource:action
    orders:read, orders:write
    payments:read, payments:initiate
    customers:read, customers:update-own
    admin:users:manage  (clearly admin-only)

Scope enforcement in service:
  @PreAuthorize("hasScope('orders:write')")
  public OrderResponse createOrder(
          CreateOrderRequest req) {
      // Spring Security: checks JWT scope claim
      // If scope not present: 403 Forbidden
      // If present: proceed
  }
```

---

### 🧪 Thought Experiment

**BOLA: THE MOST COMMON MICROSERVICES AUTH BUG**

```
SCENARIO: order-service with BOLA vulnerability

GET /api/v1/orders/{orderId}

WRONG IMPLEMENTATION:
  OrderController.java:
    @GetMapping("/{orderId}")
    public Order getOrder(
            @PathVariable Long orderId,
            @AuthenticationPrincipal JwtUser user) {
        // BAD: does not check if user OWNS this order
        return orderRepository.findById(orderId)
            .orElseThrow(NotFoundException::new);
    }
  
  Attack:
    Alice (user-123): GET /api/v1/orders/999
    Order 999: belongs to Bob (user-456)
    Response: Bob's full order with
              delivery address, items, payment info
    Alice: enumerated Bob's order data
    (just try orderId = 1, 2, 3, ..., 1000)
    BOLA = Broken Object Level Authorization

CORRECT IMPLEMENTATION:
  @GetMapping("/{orderId}")
  public Order getOrder(
          @PathVariable Long orderId,
          @AuthenticationPrincipal JwtUser user) {
    Order order = orderRepository
        .findById(orderId)
        .orElseThrow(NotFoundException::new);
    
    // BOLA CHECK: user must own this resource
    if (!order.getUserId().equals(user.getSub())) {
        // Return 404 NOT FOUND (not 403):
        // don't reveal the resource exists
        throw new NotFoundException();
    }
    return order;
  }
  // Why 404 not 403?
  // 403 confirms: order exists but you can't access it
  // 404 is ambiguous: might not exist at all
  // Prevents enumeration attacks
```

---

### 🧠 Mental Model / Analogy

> Microservices security patterns are like access
> controls in a large hospital. Front door (API
> Gateway): checks ID (authentication). Role badge
> (JWT role claim): determines which floors you
> can access (course authorization). Patient room
> (individual service): checks if YOU are the
> assigned nurse for THIS patient (BOLA check).
> Medications cabinet (secrets): different key
> for each nurse, rotated daily (Vault dynamic
> secrets). CCTV (audit logs): records every
> door access. Fire doors (NetworkPolicy): limit
> spread in emergency. Staff ID scanner (mTLS):
> verifies every staff member has a valid badge.
> No single control is sufficient; together they
> achieve defense in depth.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Security patterns: proven solutions for common
security problems. In microservices: (1) prove
who you are (JWT); (2) check if you can do
this specific action (BOLA check); (3) never
put passwords in code (Vault).

**Level 2 - JWT basics (junior developer):**
JWT (JSON Web Token): signed base64 JSON. Contains
claims: sub (user ID), roles, scope, exp. Signed
with RS256 (private key by auth server; public
key shared for validation). Services: validate
JWT signature locally using public key (no network
call). Always check: signature, exp, iss.

**Level 3 - OAuth2 patterns (mid-level):**
Authorization Code Flow (for users + browsers):
user sees login page, Auth server issues auth code,
exchanged for access token + refresh token. Client
Credentials Flow (for service-to-service without
user): service authenticates with client_id +
client_secret, gets access token. Scope: defines
what the token can do. Token introspection vs
JWT: JWT = stateless validation; introspection =
centralized revocation. For short-lived tokens
(1h): JWT is fine. For immediately revocable:
use token introspection.

**Level 4 - Service mesh + OWASP (senior):**
OWASP API Security Top 10 countermeasures in
microservices: (1) BOLA: object-level ownership
check per operation; (2) Broken Authentication:
mTLS + JWT, no API keys in URLs; (3) Excessive
Data Exposure: use response DTOs (not entities
directly); never return more fields than the
client needs; (4) Rate Limiting: at API Gateway
(Istio VirtualService or Kong rate-limit plugin);
(5) Mass Assignment: use `@JsonIgnore` or explicit
`@JsonProperty` whitelist on update DTOs.

**Level 5 - Token exchange and delegation (principal):**
On-behalf-of (OBO) token exchange: when service
A calls service B on behalf of user Alice: service
A sends a token exchange request to Auth server
(OAuth2 RFC 8693), receiving a new JWT with:
- original user identity (Alice) preserved
- new audience (service B)
- additional delegation claim (delegated by service A)
Service B: sees who the user is (Alice) AND which
service delegated (service A). Full audit trail.
Useful for: financial services audit requirements
("who authorized this payment?").

---

### ⚙️ How It Works (Mechanism)

```java
// SECURITY CONFIGURATION: Spring Boot microservice
// applying multiple security patterns

@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    // 1. JWT VALIDATION FILTER
    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        return http
            .oauth2ResourceServer(oauth2 ->
                oauth2.jwt(jwt ->
                    jwt.jwkSetUri(
                        // Validate JWT against JWKS endpoint
                        // NO network call per request:
                        // JWKS cached; re-fetched every 5min
                        "https://auth.company.com"
                        + "/.well-known/jwks.json")
                ))
            // 2. ALL endpoints require authentication
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health")
                    .permitAll()  // health check: no auth
                .anyRequest().authenticated()
            )
            .sessionManagement(session ->
                // 3. STATELESS: no session cookies
                // JWT in header only
                session.sessionCreationPolicy(
                    SessionCreationPolicy.STATELESS)
            )
            .csrf(csrf ->
                // 4. CSRF disabled for REST APIs
                // (CSRF only needed for cookie-based sessions)
                csrf.disable()
            )
            .build();
    }
}

// 5. METHOD-LEVEL AUTHORIZATION + BOLA CHECK
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    
    @GetMapping("/{orderId}")
    // 6. SCOPE CHECK: requires orders:read scope
    @PreAuthorize("hasAuthority('SCOPE_orders:read')")
    public OrderResponse getOrder(
            @PathVariable Long orderId,
            // JWT-extracted user
            @AuthenticationPrincipal Jwt jwt) {
        
        Order order = orderService.findById(orderId);
        
        // 7. BOLA CHECK: user must own this order
        String userId = jwt.getSubject();
        if (!order.getUserId().equals(userId)) {
            // 404, not 403 (don't reveal existence)
            throw new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "Order not found");
        }
        
        // 8. RESPONSE DTO: never return entity
        // (prevents excessive data exposure)
        return orderMapper.toResponse(order);
        // OrderResponse: only fields client needs
        // NOT: internal tracking IDs, DB metadata,
        //      other users' data
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
SECURITY LAYERS FOR: POST /api/v1/orders (create order)

REST Client:
  Authorization: Bearer <JWT>
  mTLS cert (if machine client)

API GATEWAY (Kong/AWS API Gateway):
  [1] Rate limit: 100 req/min per user
  [2] JWT validation: signature + exp + iss
  [3] Scope check: orders:write present?
  [4] SSL termination (HTTPS -> HTTP internally)
  Passes: user identity headers to order-service

ISTIO ENVOY (order-service sidecar):
  [5] mTLS: verify gateway's workload cert
  [6] AuthorizationPolicy: is API Gateway
      allowed to call order-service? YES

ORDER-SERVICE (Spring Boot):
  [7] JWT re-validation: signature + exp
      (defense-in-depth; don't trust gateway alone)
  [8] Scope check: SCOPE_orders:write
  [9] Business validation: order data valid?
  [10] Calls payment-service (forward JWT + mTLS)

PAYMENT-SERVICE:
  [11] mTLS: verify order-service cert
  [12] JWT re-validation: user still valid?
  [13] BOLA check: this payment's userId == jwt.sub?
  [14] Scope check: payments:initiate present?
  [15] Vault: get payment gateway API key (dynamic)
  [16] Calls payment gateway with short-lived key

AUDIT LOG (all services):
  Structured log per request:
    {"userId": jwt.sub, "action": "create-order",
     "resourceId": orderId,
     "workloadId": spiffe_id,
     "result": "success", "traceId": "..."}  
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: mass assignment vulnerability**

```java
// BAD: accepts entire request as entity (mass assignment)
// Attacker: sends {"userId": "admin-999",
//                  "price": 0.01, "status": "paid"}
// Service: saves all fields including the injected ones
@PutMapping("/{orderId}")
public Order updateOrder(
        @PathVariable Long orderId,
        @RequestBody Order order,  // BAD: entity directly
        @AuthenticationPrincipal Jwt jwt) {
    order.setId(orderId);
    return orderRepository.save(order);
    // Attacker sets: order.userId = "admin-999"
    // Attacker sets: order.price = 0.01
    // Both are saved to DB - mass assignment exploit
}
```

```java
// GOOD: explicit DTO (only allowed fields)
// Attacker cannot set userId, price, or status
@Data
public class UpdateOrderRequest {
    // Only these fields can be updated by the client
    @NotBlank
    private String deliveryAddress;
    
    @NotNull
    private List<OrderItemRequest> items;
    
    // userId, price, status, createdAt:
    // NOT in DTO = cannot be mass-assigned
}

@PutMapping("/{orderId}")
public OrderResponse updateOrder(
        @PathVariable Long orderId,
        @Valid @RequestBody UpdateOrderRequest req,
        @AuthenticationPrincipal Jwt jwt) {
    
    // BOLA: does user own this order?
    Order existing = orderService.findById(orderId);
    if (!existing.getUserId().equals(jwt.getSubject())) {
        throw new ResponseStatusException(NOT_FOUND);
    }
    
    // Only update the allowed fields
    existing.setDeliveryAddress(req.getDeliveryAddress());
    existing.setItems(mapper.toItems(req.getItems()));
    // userId, price, status: server-controlled, not changed
    
    return mapper.toResponse(orderService.save(existing));
}
```

---

### ⚖️ Comparison Table

| Pattern | Problem Solved | Implementation |
|---|---|---|
| **JWT Propagation** | User identity across service chain | Authorization header forward |
| **mTLS** | Service-to-service identity | Istio auto-inject |
| **OAuth2 Scopes** | Fine-grained API permissions | JWT claim + @PreAuthorize |
| **BOLA Check** | Horizontal authorization | `object.userId == jwt.sub` |
| **Response DTO** | Excessive data exposure | Separate request/response models |
| **Vault** | Secret management | Vault Agent sidecar |
| **Rate Limiting** | Brute force, DoS | API Gateway plugin |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Authenticating at the API Gateway is sufficient; internal services don't need auth | API Gateway authentication proves: "A valid user called the API." But: what if a developer's local tool bypasses the gateway? What if there's a service mesh misconfiguration that allows direct pod-to-pod calls? Internal services MUST re-validate the JWT (signature + exp + claims) themselves. This is defense in depth: Gateway validation + service validation. The cost: two JWT signature verifications (both cached with JWK public keys, ~0.1ms each). The benefit: no assumption of gateway invulnerability. |
| HTTPS (TLS) prevents injection attacks | TLS encrypts data in transit. It does NOT validate the CONTENT of requests. SQL injection, command injection, and XPath injection: all operate at the application layer (above TLS). TLS says: this data arrived from an authenticated source without modification. Your application must still: validate and sanitize all inputs, use parameterized queries, apply output encoding. TLS is not an application security control; it is a transport security control. |
| Admin users should bypass security checks for efficiency | "Admin bypass" patterns are one of the most exploited vulnerabilities. Admin accounts: targeted by attackers precisely because they bypass controls. Every admin operation: should be logged, require re-authentication for sensitive operations (step-up auth: re-enter password for delete/bulk operations), and be subject to the same BOLA checks as regular users. The admin role: grants permissions (can access all orders); BOLA check: still verifies the operation makes sense (prevents bugs, not just attacks). |

---

### 🚨 Failure Modes & Diagnosis

**JWT not re-validated in internal service**

**Symptom:**
Expired JWT token (exp = 1 hour) is used to call
the API 2 hours later. API Gateway: cached JWT
validation result (TTL = 10 minutes). Gateway:
lets the request through (cached as valid). Order-
service: does NOT re-validate JWT (trusts gateway).
Result: expired token successfully creates orders
2 hours after expiry.

**Root Cause:**
1. API Gateway: caches JWKS validation result
   without checking `exp` per request.
2. Order-service: assumes gateway already validated
   JWT; skips re-validation.
3. Combined: expired tokens work indefinitely
   (until both the gateway cache AND service
   validation are fixed).

**Fix:**
```java
// Order-service MUST re-validate JWT
// Spring Security: does this automatically
// when using oauth2ResourceServer().jwt()
// The oauth2ResourceServer bean:
// - validates signature (from JWKS)
// - validates exp (per request, not cached)
// - validates iss (matches configured issuer)
// - rejects: invalid sig, expired, wrong issuer

// VERIFY this is configured:
@Bean
public SecurityFilterChain filterChain(
        HttpSecurity http) throws Exception {
    return http
        .oauth2ResourceServer(oauth2 ->
            oauth2.jwt(jwt ->
                // This validates exp per request:
                jwt.jwkSetUri(jwksUri)))
        // ...
        .build();
}
// NEVER: manually extract claims and skip exp check
// NEVER: trust forwarded user-id headers from gateway
//        (gateway can be bypassed)
```

---

### 🔗 Related Keywords

**Foundation of service security:**
- `mTLS in Microservices` - workload identity pattern
- `Zero Trust Security` - architectural model
  that these patterns implement

**Key security control point:**
- `API Gateway` - where external authentication
  is centralized

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| AUTH PATTERNS| JWT propagation (user identity);  |
|              | mTLS (workload identity);         |
|              | OAuth2 scopes (permissions)       |
+--------------+-----------------------------------+
| BOLA CHECK   | object.userId == jwt.sub()        |
|              | Return 404 not 403 (no disclosure)|
+--------------+-----------------------------------+
| OWASP TOP    | BOLA #1; Mass Assignment;         |
|              | Excessive Data Exposure           |
+--------------+-----------------------------------+
| ONE-LINER    | "AuthN who you are (JWT/mTLS);    |
|              |  AuthZ what you own (BOLA check)"|
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. JWT propagation: user identity travels through
   the service chain in Authorization header.
   Each service: validates independently (no
   round-trip to auth server).
2. BOLA check on EVERY resource access: `object.
   userId == jwt.sub`. The most common microservices
   auth vulnerability. Return 404, not 403.
3. Response DTOs: never return JPA entities.
   Only expose fields the client explicitly needs.
   Prevents excessive data exposure (OWASP #3).

**Interview one-liner:**
"Microservices Security Patterns: (1) JWT
propagation - user JWT forwarded through service
chain, each service validates locally; (2) mTLS -
workload identity for service-to-service; (3) OAuth2
scopes - fine-grained permissions per resource;
(4) BOLA check - `object.userId == jwt.sub()` on
every resource access (most common microservices
vuln); (5) Response DTOs - never expose JPA
entities; (6) Vault - dynamic short-lived secrets,
never env vars. Defense in depth: each layer catches
what others miss."

---

### 💡 The Surprising Truth

The most critical security pattern that teams
most often skip is BOLA (Broken Object Level
Authorization). Not injection (prevented by
parameterized queries - basic). Not mass assignment
(prevented by DTOs - easy). BOLA: requires a
check at EVERY resource access endpoint. In a
30-service system with 200 endpoints: that's 200
places to add `object.userId == jwt.sub`. Developers
forget, especially in GET endpoints ("it's just
reading data"). BOLA is the #1 vulnerability in
the OWASP API Security Top 10 for multiple years.
Why: automated scanners don't catch it (the
endpoint works, just with a different user's ID).
Only manual code review or security testing
(automated business logic testing) catches it.
Add a linting rule or architecture test: "every
@GetMapping/@PostMapping in services/* must
contain a userId ownership check."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **JWT** Decode a JWT manually (base64) and
   identify: sub, roles, scope, exp, iss. Explain
   how Spring Security validates each field.
   What happens if exp is in the past?
2. **BOLA** Review an existing microservice:
   find all endpoints that access user-owned
   resources. Identify which ones are missing
   the ownership check. Fix them.
3. **OAUTH2** Design the OAuth2 scopes for a
   payment system: order creation, payment
   initiation, customer profile read, admin
   reporting. Which scopes are user-level vs
   service-level?
4. **MASS ASSIGNMENT** Find a Spring Boot
   controller that accepts `@RequestBody Order
   order` (entity directly). Refactor to use a
   request DTO. What fields should be excluded?
5. **OWASP** For each of the OWASP API Security
   Top 10: describe the attack, show a vulnerable
   code example, and show the fix. Which ones
   are specific to microservices (vs monoliths)?

---

### 🧠 Think About This Before We Continue

**Q1.** Your order-service has 15 endpoints.
5 endpoints: have BOLA checks. 10 don't ("it's
read-only", "it's admin"). A security tester
demonstrates they can enumerate any user's order
history, delivery addresses, and payment methods
via the unprotected GET endpoints. Fix: (a) add
BOLA checks to all 10, or (b) add a shared aspect/
interceptor that enforces BOLA automatically.
Which approach? How do you implement the interceptor
approach in Spring Boot?

**Q2.** Your team wants to add a B2B API: partner
companies (not individual users) call your APIs.
Partners have their own service accounts (not
personal JWTs). Design the authentication strategy:
OAuth2 client credentials flow, scopes, BOLA
checks (partners can see all orders for their
corporate account but not other companies' orders).
How does this differ from user JWT flows?

**Q3.** You discover that 3 of your 30 services
do NOT re-validate JWTs - they trust forwarded
X-User-Id headers from the API Gateway. Design
the migration: how do you safely add JWT validation
to these 3 services without breaking existing
clients? What tests do you write to prevent
regression?