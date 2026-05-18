---
id: ATZ-020
title: "API Gateway Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-008, ATZ-016, ATZ-017
used_by: ATZ-030, ATZ-033, ATZ-049, ATZ-050
related: ATZ-017, ATZ-018, ATZ-030
tags:
  - security
  - authorization
  - api-gateway
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/authorization/api-gateway-authorization/
---

⚡ **TL;DR** - An API gateway is a single entry point for all API
traffic and a natural place to enforce authorization. Gateway-level
authorization verifies JWT signatures, validates scopes, and blocks
unauthorized requests before they reach backend services - at zero
backend cost. The limitation: gateways enforce course-grained
authorization (token valid + scope present). Fine-grained authorization
(does user X own resource Y?) must still happen in the backend service.

---

### 📊 Entry Metadata

| #020 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-008, ATZ-016, ATZ-017 | |
| **Used by:** | ATZ-030, ATZ-033, ATZ-049, ATZ-050 | |
| **Related:** | ATZ-017 OAuth Scopes, ATZ-018 JWT Claims, ATZ-030 Externalized Authorization | |

---

### 📘 Textbook Definition

API gateway authorization is the practice of enforcing
authentication and coarse-grained authorization at the API
gateway layer before requests reach backend services. The
gateway performs: JWT validation (signature, expiry, issuer,
audience), scope verification, rate limiting, and optionally
role-based route filtering. Gateway authorization reduces
the authorization burden on backend services for common checks
and provides a consistent enforcement perimeter. Backend services
are responsible for fine-grained, resource-level authorization
that requires knowledge of specific data.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The gateway checks "is this token valid and does it have
the right scope?" - the backend checks "does this user
own this specific resource?"

**Two authorization layers:**

```
┌────────────────────────────────────────────────────────┐
│         API Gateway Two-Layer Authorization            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LAYER 1: API GATEWAY (coarse-grained)                 │
│  - Is the JWT signature valid?              (reject    │
│  - Is the JWT not expired?                   if any    │
│  - Is the issuer trusted?                    fails)    │
│  - Does the audience match this API?                   │
│  - Does the token have required scope?                 │
│  - Is the calling client rate-limited?                 │
│                                                        │
│  If all pass: forward request to backend               │
│  Backend receives: verified JWT + user claims          │
│                                                        │
│  LAYER 2: BACKEND SERVICE (fine-grained)               │
│  - Does user 42 own order 9999? (IDOR check)           │
│  - Is this resource in user's tenant?                  │
│  - Does this action require elevated privilege?        │
│  - Are there row-level security constraints?           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Kong/AWS API Gateway JWT validation (config)**

```yaml
# Kong gateway: JWT plugin configuration
plugins:
  - name: jwt
    config:
      key_claim_name: kid          # key ID for JWKS lookup
      claims_to_verify:
        - exp                      # reject expired tokens
        - nbf                      # reject not-yet-valid
      # Audience restriction
      anonymous: null              # no anonymous access
      
  # Scope enforcement per route
  - name: opa                      # OPA plugin for scope checks
    config:
      opa_host: http://opa:8181
      policy_path: /v1/data/gateway/allow
      # OPA policy checks scope claims in JWT

routes:
  - name: order-api
    paths: ["/api/v1/orders"]
    plugins:
      - name: jwt
      - name: opa
        config:
          required_scope: "orders:read"
```

**Example - AWS API Gateway Lambda authorizer**

```python
# Lambda authorizer: validates JWT and extracts claims
# Returns IAM policy that allows/denies method execution
import jwt
import json

def lambda_handler(event, context):
    token = event['authorizationToken'].replace('Bearer ', '')
    method_arn = event['methodArn']

    try:
        # Validate JWT (signature + expiry + audience)
        claims = jwt.decode(
            token,
            jwks_client.get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            audience="https://api.example.com"
        )
    except jwt.ExpiredSignatureError:
        raise Exception("Unauthorized")  # 401
    except Exception:
        raise Exception("Unauthorized")

    # Build IAM policy with user context
    return {
        "principalId": claims["sub"],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": method_arn
            }]
        },
        # Pass claims to backend via context
        "context": {
            "userId": claims["sub"],
            "tenantId": claims.get("tenant_id"),
            "roles": json.dumps(claims.get("roles", []))
        }
    }
```

**Example - FAILURE: relying solely on gateway authorization**

```
Scenario:
  API gateway validates JWT and checks scope "orders:read".
  Backend service: returns the order if token is valid.
  
  Attack:
    User A (userId=42) has valid JWT with "orders:read" scope.
    User A requests: GET /api/orders/9999
    (Order 9999 belongs to User B, userId=43)
    
    Gateway: JWT valid, scope orders:read present → forward
    Backend: returns order 9999 (no user ownership check)
    
    This is IDOR - gateway cannot prevent it because the
    gateway does not know which user owns order 9999.
    
Fix:
  Backend must check: order.userId == token.sub
  The gateway layer is necessary but not sufficient.
  Fine-grained authorization is always the backend's job.
```

---

*Authorization category: ATZ | Entry: ATZ-020 | v5.0*