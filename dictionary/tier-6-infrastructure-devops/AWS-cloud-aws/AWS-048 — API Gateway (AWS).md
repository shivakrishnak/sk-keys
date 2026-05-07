---
layout: default
title: "API Gateway (AWS)"
parent: "Cloud — AWS"
nav_order: 48
permalink: /cloud-aws/api-gateway-aws/
number: "AWS-048"
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["Lambda", "IAM (Identity and Access Management)", "VPC"]
used_by: ["Lambda", "ECS / Fargate", "CloudWatch"]
related: ["Lambda", "ELB / ALB / NLB", "CloudWatch", "ECS / Fargate"]
tags: [aws, api-gateway, rest, http, websocket, serverless, cloud]
---

# API Gateway (AWS)

## ⚡ TL;DR

**API Gateway** is AWS's managed API endpoint service. Three types: **HTTP API** (simpler, cheaper, 60% less than REST), **REST API** (full features: request validation, transformation, caching, usage plans), **WebSocket API** (stateful bidirectional connections). Common use: HTTP API → Lambda for serverless REST endpoints. Handles auth (IAM, Cognito, Lambda authorizers), throttling, CORS, and CloudWatch logging.

---

## 🔥 Problem This Solves

You have Lambda functions but no HTTP endpoint. You need auth, rate limiting, CORS, request validation, and logging. Without API Gateway: build all of that yourself. API Gateway provides managed HTTP → Lambda integration with auth, throttling, and routing out of the box.

---

## 📘 Textbook Definition

Amazon API Gateway is a fully managed service that enables developers to create, publish, maintain, monitor, and secure APIs. API Gateway handles traffic management, authorization and access control, monitoring, and API version management. It acts as the "front door" for applications to access backend services.

---

## ⏱️ 30 Seconds

```
API Types:
  HTTP API:   $1.00/million requests; lower latency; JWT auth; simpler
  REST API:   $3.50/million requests; full features (caching, validation)
  WebSocket:  $1.00/million msgs + $0.25/million connection-minutes

Integration types:
  Lambda Proxy:      raw request to Lambda, Lambda formats response
  HTTP Integration:  proxy to HTTP endpoint (ECS, EC2, any URL)
  AWS Service:       integrate directly with SQS, DynamoDB, etc.
  Mock:              return static response (useful for CORS preflight)

Throttling (default):
  Account: 10,000 req/s steady, 5,000 burst
  Per route (REST): usage plans + API keys
```

---

## 🔩 First Principles

- **API Gateway is a proxy**: it receives HTTP request, forwards to integration, returns response
- **Stages**: deployments are versioned and deployed to stages (dev, staging, prod)
- **Lambda Proxy Integration**: passes full request context (headers, path, query, body) as Lambda event; Lambda must return `{statusCode, headers, body}`
- **Authorizers**: Lambda authorizer = custom auth (JWT decode, custom header); Cognito User Pool authorizer = managed OAuth2/OIDC
- **CORS**: API Gateway handles OPTIONS preflight or pass-through to Lambda
- **Caching** (REST API only): cache responses by method+path; reduce Lambda invocations

---

## 🧪 Thought Experiment

Serverless REST API: `GET /users/{id}` → Lambda reads from DynamoDB. Without API Gateway: no HTTP endpoint. With API Gateway HTTP API: route defined → Lambda integration → add JWT authorizer (Cognito or custom) → CORS enabled → CloudWatch logging enabled. Done in 20 lines of Terraform. Zero servers, scales automatically, pay per request.

---

## 🧠 Mental Model / Analogy

API Gateway is a **managed hotel concierge**: guests (HTTP clients) arrive at the front desk (API Gateway). Concierge checks if they're authorized (authorizer), directs them to the right department (routing), enforces entry limits (throttling), and logs all interactions (CloudWatch). Guests never directly access staff (Lambda/ECS) — all goes through the concierge.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Create HTTP API, add Lambda route, deploy to stage. Enable CORS. Test endpoint.

**Level 2 — Practitioner**: JWT authorizer (Cognito User Pool or custom JWT issuer). Custom domain with ACM certificate. CloudWatch access logs for debugging. Request validation (REST API): validate required parameters/body schema before hitting Lambda.

**Level 3 — Advanced**: Lambda authorizer: custom auth logic (API key in header, JWT with custom claims). AWS service integration: API Gateway → SQS (no Lambda needed for simple enqueue). Usage plans + API keys: rate limit per API consumer. Stage variables: different Lambda aliases per stage (dev/prod).

**Level 4 — Expert**: API Gateway VPC Link: expose private ECS/EC2 services via API Gateway without public endpoint (ALB in private VPC → VPC Link → API Gateway). WebSocket API: stateful connections; $connectionId for routing; Lambda handles connect/disconnect/message. REST API caching: cache by path+query; invalidate via header `Cache-Control: max-age=0`. API Gateway private APIs: accessible only within VPC via Interface Endpoint. OpenAPI/Swagger import: define API via OpenAPI spec, import to API Gateway (treats spec as source of truth).

---

## ⚙️ How It Works

### HTTP API with Lambda (Terraform)

```hcl
# HTTP API (cheaper, simpler than REST)
resource "aws_apigatewayv2_api" "main" {
  name          = "main-api"
  protocol_type = "HTTP"
  description   = "Main application API"

  # CORS configuration
  cors_configuration {
    allow_headers = ["Content-Type", "Authorization", "X-Amz-Date"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_origins = ["https://app.example.com"]
    max_age       = 300
  }
}

# JWT Authorizer (Cognito or custom JWT)
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.app.id]
    issuer   = "https://cognito-idp.us-east-1.amazonaws.com/${aws_cognito_user_pool.main.id}"
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "users" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.users.invoke_arn
  payload_format_version = "2.0"  # HTTP API format
}

# Routes
resource "aws_apigatewayv2_route" "get_user" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /users/{userId}"

  target             = "integrations/${aws_apigatewayv2_integration.users.id}"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_type = "JWT"
}

resource "aws_apigatewayv2_route" "create_user" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /users"

  target             = "integrations/${aws_apigatewayv2_integration.users.id}"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_type = "JWT"
}

# Stage + deployment
resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "prod"
  auto_deploy = true

  # Access logging
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw.arn
  }

  # Default throttling
  default_route_settings {
    throttling_burst_limit   = 500
    throttling_rate_limit    = 1000
  }
}

# Custom domain
resource "aws_apigatewayv2_domain_name" "main" {
  domain_name = "api.example.com"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.main.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

# API mapping: domain → stage
resource "aws_apigatewayv2_api_mapping" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main.id
  stage       = aws_apigatewayv2_stage.prod.id
  api_mapping_key = "v1"  # https://api.example.com/v1/users
}

# Grant API Gateway permission to invoke Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.users.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
```

### Lambda Handler (Java) for API Gateway

```java
// Lambda handler for API Gateway HTTP API v2.0 payload
public class UserHandler implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse> {

    private final UserService userService;

    @Override
    public APIGatewayV2HTTPResponse handleRequest(
            APIGatewayV2HTTPEvent event, Context context) {

        String httpMethod = event.getRequestContext().getHttp().getMethod();
        String path = event.getRawPath();

        // Extract JWT claims (already validated by API Gateway)
        Map<String, Object> claims = event.getRequestContext()
            .getAuthorizer().getJwt().getClaims();
        String userId = (String) claims.get("sub");

        try {
            return switch (httpMethod) {
                case "GET" -> handleGet(event, userId);
                case "POST" -> handlePost(event, userId);
                default -> response(405, "{\"error\":\"Method Not Allowed\"}");
            };
        } catch (NotFoundException e) {
            return response(404, "{\"error\":\"" + e.getMessage() + "\"}");
        } catch (Exception e) {
            log.error("Unhandled error", e);
            return response(500, "{\"error\":\"Internal Server Error\"}");
        }
    }

    private APIGatewayV2HTTPResponse handleGet(
            APIGatewayV2HTTPEvent event, String requestingUserId) {
        String targetUserId = event.getPathParameters().get("userId");
        User user = userService.getUser(targetUserId);
        return response(200, JsonUtils.serialize(user));
    }

    private APIGatewayV2HTTPResponse response(int statusCode, String body) {
        return APIGatewayV2HTTPResponse.builder()
            .withStatusCode(statusCode)
            .withHeaders(Map.of("Content-Type", "application/json"))
            .withBody(body)
            .build();
    }
}
```

---

## ⚖️ Comparison Table: HTTP API vs REST API

|                        | HTTP API             | REST API                     |
| ---------------------- | -------------------- | ---------------------------- |
| **Price**              | $1.00/million        | $3.50/million                |
| **Latency**            | Lower                | Higher                       |
| **Auth**               | JWT (native), Lambda | IAM, Cognito, Lambda         |
| **Request validation** | ❌                   | ✅                           |
| **Response caching**   | ❌                   | ✅                           |
| **Usage plans**        | ❌                   | ✅                           |
| **AWS integrations**   | Limited              | Full                         |
| **WebSocket**          | ❌                   | ❌ (separate)                |
| **Best for**           | Most use cases       | API monetization, enterprise |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------- |
| "REST API is better than HTTP API"      | HTTP API is newer, cheaper, and covers 90% of use cases; prefer HTTP API        |
| "API Gateway handles retries to Lambda" | API Gateway does NOT retry; if Lambda errors, 502 returned to client            |
| "API Gateway is required for Lambda"    | Lambda can be invoked via Function URL, ALB, SQS, SNS — API Gateway is optional |
| "Usage plans prevent DDoS"              | Usage plans throttle per API key; not a DDoS protection tool (use WAF + Shield) |

---

## 🔗 Related Keywords

- [Lambda](/cloud-aws/lambda/) — most common backend for API Gateway
- [ELB / ALB / NLB](/cloud-aws/elb-alb-nlb/) — alternative for container-based APIs
- [CloudWatch](/cloud-aws/cloudwatch/) — API Gateway logs and metrics

---

## 📌 Quick Reference Card

```bash
# List APIs
aws apigatewayv2 get-apis \
  --query 'Items[].{Name:Name,Id:ApiId,Protocol:ProtocolType}'

# Get API endpoint
aws apigatewayv2 get-api \
  --api-id abc123def \
  --query 'ApiEndpoint'

# Export API spec (OpenAPI)
aws apigatewayv2 export-api \
  --api-id abc123def \
  --output-type JSON \
  --specification OAS30 \
  /tmp/api-spec.json

# Get stage info
aws apigatewayv2 get-stages \
  --api-id abc123def

# View access logs (last 100 entries)
aws logs tail /aws/apigateway/main-api \
  --since 1h --format short
```

---

## 🧠 Think About This

API Gateway HTTP API vs ALB for Lambda: both can route HTTP → Lambda. Choose HTTP API when you need: JWT auth, Cognito integration, API keys/usage plans, WebSocket, or tight AWS integration. Choose ALB when: you already have an ALB (no extra cost for Lambda target), you need OIDC auth (ALB natively supports it), or you're running a mix of ECS containers and Lambda behind the same LB. The hidden cost of API Gateway is data transfer: $0.09/GB out to internet (same as EC2). For large response bodies (bulk exports, images), cache with CloudFront in front of API Gateway. For internal service-to-service calls within a VPC, skip API Gateway entirely — use VPC DNS + service discovery (ECS Service Connect, Cloud Map) instead.
