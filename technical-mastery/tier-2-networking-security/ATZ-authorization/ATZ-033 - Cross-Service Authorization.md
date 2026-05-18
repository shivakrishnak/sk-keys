---
id: ATZ-033
title: "Cross-Service Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-020, ATZ-023, ATZ-030
used_by: ATZ-040, ATZ-045, ATZ-047, ATZ-049
related: ATZ-023, ATZ-030, ATZ-045
tags:
  - security
  - authorization
  - microservices
  - service-to-service
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/authorization/cross-service-authorization/
---

⚡ **TL;DR** - When Service A calls Service B, B must decide: is this
request authorized? Two models: (1) pass the user's JWT along (user
context propagation) so B can check the user's permissions, or
(2) trust the calling service (service-to-service auth only). The
security risk of model 2: if Service A is compromised, it can call
Service B on behalf of any user without user consent. Use model 1
for user-delegated operations; use model 2 only for system-to-system
calls with no user context.

---

### 📊 Entry Metadata

| #033 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-020 API Gateway Auth, ATZ-023 Service Accounts, ATZ-030 Externalized | |
| **Used by:** | ATZ-040, ATZ-045, ATZ-047, ATZ-049 | |
| **Related:** | ATZ-023 Service Accounts, ATZ-030 Externalized, ATZ-045 Event-Driven | |

---

### 📘 Textbook Definition

Cross-service authorization is the mechanism by which a service
receiving an internal call validates whether the calling service
and/or the user on whose behalf the call is made has the required
permissions. In microservice architectures, a user request often
triggers a chain of service calls. Each downstream service must
make its own authorization decision - relying on the gateway to
have checked permissions is insufficient (horizontal movement
via compromised upstream service). Patterns include: JWT forwarding
(pass original user token through the chain), token exchange
(exchange user token for a scoped downstream token), and
service-mesh identity (mTLS proves calling service identity,
JWT proves user context).

---

### ⚙️ How It Works (Mechanism)

**Token forwarding patterns:**

```
┌────────────────────────────────────────────────────────┐
│         Cross-Service Authorization Models             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  MODEL 1: JWT forwarding (user context propagation)    │
│  User -> Gateway -> Order-Service (JWT passed) ->      │
│          Payment-Service (JWT passed)                  │
│  Each service validates: JWT sig, exp, aud, perms      │
│  Payment-Service checks: can THIS USER make payment?   │
│  Risk: long JWT chain; aud validation must be strict   │
│                                                        │
│  MODEL 2: Token exchange (OAuth 2.0 Token Exchange)    │
│  Order-Service exchanges user JWT for a payment-scoped │
│  token with limited claims (RFC 8693)                  │
│  Payment-Service trusts the exchanged token            │
│  Benefit: limits scope exposure per hop                │
│                                                        │
│  MODEL 3: Service identity + user propagation header   │
│  mTLS proves Order-Service identity                    │
│  Custom header: X-User-Id: alice (set by gateway)      │
│  Payment-Service: trusts the header ONLY if it came    │
│  from a service with a valid mTLS cert                │
│  Risk: if header can be set by external callers too    │
│                                                        │
│  ANTI-PATTERN: "the gateway checked it"                │
│  Order-Service assumes payment is authorized if        │
│  request reached it from gateway. Never do this.       │
│  Compromised Order-Service can call Payment-Service    │
│  with any user ID.                                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - JWT forwarding in Spring WebClient**

```java
@Service
public class PaymentServiceClient {

    private final WebClient webClient;

    // Forward the user's JWT to the downstream service
    public PaymentResult processPayment(
            String amount, String currency,
            String userJwt) {
        return webClient.post()
            .uri("/payments")
            // Pass original user JWT - downstream validates
            // its own permissions for this user
            .header("Authorization", "Bearer " + userJwt)
            // Also identify this service via its own client cert
            // (mTLS configured on the WebClient)
            .bodyValue(new PaymentRequest(amount, currency))
            .retrieve()
            .bodyToMono(PaymentResult.class)
            .block();
    }
}

// Payment service validates incoming JWT:
@GetMapping("/payments")
@PreAuthorize(
    "hasAuthority('SCOPE_payment:write') and "
    + "hasRole('VERIFIED_USER')")
public PaymentResult processPayment(
        @RequestBody PaymentRequest req,
        Authentication auth) {
    // JWT was validated by Spring Security
    // SCOPE_payment:write ensures only payment-scoped tokens
    // are accepted (prevents tokens for other services)
    return paymentService.process(req, auth.getName());
}
```

---

*Authorization category: ATZ | Entry: ATZ-033 | v5.0*