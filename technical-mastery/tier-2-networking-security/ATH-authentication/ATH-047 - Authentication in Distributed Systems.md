---
id: ATH-047
title: "Authentication in Distributed Systems"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-023, ATH-039, ATH-045, ATH-046
used_by: ATH-048, ATH-049, ATH-053, ATH-054
related: ATH-039, ATH-048, ATH-053
tags:
  - security
  - authentication
  - distributed-systems
  - microservices
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/authentication/authentication-in-distributed-systems/
---

⚡ **TL;DR** - In distributed systems, every service must answer
"who is this?" for each request. Propagating the user's JWT across
service calls is simple but requires every service to validate it.
Service-to-service authentication (which service is calling me?)
requires a separate identity channel: mTLS, SPIFFE/SPIRE, or
workload identity tokens. The failure mode: one service trusts a
forwarded header without verifying it cryptographically - a
compromised upstream service can impersonate any user.

---

### 📊 Entry Metadata

| #047 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-023 JWT, ATH-039 mTLS, ATH-045 Algorithm, ATH-046 Token Theft | |
| **Used by:** | ATH-048, ATH-049, ATH-053, ATH-054 | |
| **Related:** | ATH-039 mTLS, ATH-048 Service Identity, ATH-053 Auth Server Arch | |

---

### 📘 Textbook Definition

Authentication in distributed systems requires solving two
independent problems: user authentication (proving the end user's
identity to each service in a call chain) and service
authentication (proving which service is making a call). User
authentication propagation typically uses JWT forwarding (the
original user's access token is passed in the Authorization
header down the call chain, and each service validates it) or
token exchange (the service exchanges the user token for a
downstream-scoped token via OAuth 2.0 Token Exchange, RFC 8693).
Service authentication uses mTLS (certificates), SPIFFE workload
identity, or platform-issued instance tokens (AWS IAM, GCP SA).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│        Distributed Authentication Layers               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  USER IDENTITY PROPAGATION:                            │
│  Client -> Gateway: JWT (signed, RS256)                │
│  Gateway -> OrderService: forward JWT                  │
│  OrderService validates: sig, exp, aud=order-service   │
│  OrderService -> PaymentService: forward or exchange   │
│  PaymentService validates: aud=payment-service         │
│                                                        │
│  SERVICE IDENTITY (mTLS):                              │
│  OrderService -> PaymentService:                       │
│  + mTLS cert: SPIFFE URI in SAN                        │
│    spiffe://cluster.local/ns/prod/sa/order-service     │
│  PaymentService: validates cert against trusted CA     │
│  Both: user JWT + service cert = full auth context     │
│                                                        │
│  TRUST LEVELS:                                         │
│  No mTLS: PaymentService trusts any caller             │
│    who presents a valid user JWT                       │
│  With mTLS: PaymentService trusts only services        │
│    with valid cluster certificates                     │
│  With authorization: PaymentService trusts only        │
│    order-service (not all services in cluster)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - SPIFFE/SPIRE workload identity in Kubernetes**

```yaml
# SPIRE agent issues SVIDs (SPIFFE Verifiable Identity Docs)
# to pods based on Kubernetes Service Account
# Each pod gets an mTLS cert with its SPIFFE ID

# 1. Pod gets SPIFFE ID automatically from SPIRE:
#    spiffe://company.com/k8s/prod/ns/payments/sa/payment-svc

# 2. Services authenticate using SPIFFE IDs:
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-authz
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
    - from:
        - source:
            principals:
              # Only order-service can call payment-service
              - "cluster.local/ns/orders/sa/order-service"
      to:
        - operation:
            methods: ["POST"]
            paths: ["/payments"]
```

**Example - Token exchange for downstream service calls**

```java
@Service
public class TokenExchangeService {

    public String exchangeForDownstreamToken(
            String userAccessToken,
            String targetAudience) {
        // RFC 8693 Token Exchange
        // Exchange user's broad access token for a
        // narrowly-scoped token for the target service
        MultiValueMap<String, String> params =
            new LinkedMultiValueMap<>();
        params.add("grant_type",
            "urn:ietf:params:oauth:grant-type:token-exchange");
        params.add("subject_token", userAccessToken);
        params.add("subject_token_type",
            "urn:ietf:params:oauth:token-type:access_token");
        params.add("audience", targetAudience);
        params.add("scope", "payment:write"); // narrow scope

        TokenResponse response = authServer.postForToken(
            params);
        return response.getAccessToken();
        // This token: aud=targetAudience, scope=payment:write
        // Cannot be used for any other service
    }
}
```

---

*Authentication category: ATH | Entry: ATH-047 | v5.0*