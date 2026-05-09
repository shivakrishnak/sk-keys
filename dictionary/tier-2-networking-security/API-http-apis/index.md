---
layout: default
title: "HTTP & APIs"
parent: "Technical Dictionary"
nav_order: 6
has_children: true
permalink: /http-apis/
---

# HTTP & APIs

HTTP versions, REST, GraphQL, gRPC, WebSocket, API security, authentication, API design best practices, and creator-level protocol specification theory.

**Keywords:** API-001–API-082 (82 terms · 60 original + 22 gap-fill)**

> ⚠️ **Duplicates resolved:** `API-037` relabelled "API Key Authentication Pattern" (was duplicate of `API-001`). `API-052` / `API-053` kept as distinct entries: deep-dive vs conceptual Pagination.

| ID      | Keyword                                          | Difficulty |
|---------|--------------------------------------------------|------------|
| API-001 | API Keys                                         | ★☆☆        |
| API-002 | HTTP/1.1                                         | ★☆☆        |
| API-003 | HTTP/2                                           | ★★☆        |
| API-004 | HTTP/3                                           | ★★★        |
| API-005 | HTTP Methods                                     | ★☆☆        |
| API-006 | HTTP Status Codes                                | ★☆☆        |
| API-007 | HTTP Headers                                     | ★★☆        |
| API-008 | Keep-Alive / Connection Pooling                  | ★★☆        |
| API-009 | REST                                             | ★☆☆        |
| API-010 | RESTful Constraints                              | ★★☆        |
| API-011 | HATEOAS                                          | ★★★        |
| API-012 | Idempotency in HTTP                              | ★★☆        |
| API-013 | GraphQL                                          | ★★☆        |
| API-014 | GraphQL Schema                                   | ★★☆        |
| API-015 | GraphQL Resolvers                                | ★★☆        |
| API-016 | GraphQL N+1 Problem                              | ★★★        |
| API-017 | GraphQL Subscriptions                            | ★★★        |
| API-018 | gRPC                                             | ★★☆        |
| API-019 | Protocol Buffers                                 | ★★☆        |
| API-020 | gRPC Streaming                                   | ★★★        |
| API-021 | SOAP                                             | ★★☆        |
| API-022 | WSDL                                             | ★★☆        |
| API-023 | WebSocket                                        | ★★☆        |
| API-024 | Server-Sent Events (SSE)                         | ★★☆        |
| API-025 | Long Polling                                     | ★★☆        |
| API-026 | Apigee (API Management Platform)                 | ★★★        |
| API-027 | API Management Platform                          | ★★★        |
| API-028 | API Gateway Patterns                             | ★★★        |
| API-029 | Webhook                                          | ★★☆        |
| API-030 | API Gateway                                      | ★★☆        |
| API-031 | API Versioning                                   | ★★☆        |
| API-032 | API Rate Limiting                                | ★★☆        |
| API-033 | API Authentication                               | ★★☆        |
| API-034 | OAuth2                                           | ★★☆        |
| API-035 | JWT                                              | ★★☆        |
| API-036 | OIDC                                             | ★★★        |
| API-037 | API Key Authentication Pattern                   | ★★☆        |
| API-038 | HMAC                                             | ★★★        |
| API-039 | CORS                                             | ★★☆        |
| API-040 | XSS                                              | ★★☆        |
| API-041 | CSRF                                             | ★★☆        |
| API-042 | SQL Injection                                    | ★★☆        |
| API-043 | SSRF                                             | ★★★        |
| API-044 | Content Negotiation                              | ★★☆        |
| API-045 | OpenAPI / Swagger                                | ★★☆        |
| API-046 | API Contract Testing                             | ★★★        |
| API-047 | API Mocking                                      | ★★☆        |
| API-048 | API Backward Compatibility                       | ★★★        |
| API-049 | BFF (Backend for Frontend)                       | ★★★        |
| API-050 | API Caching                                      | ★★☆        |
| API-051 | ETag / Cache-Control                             | ★★★        |
| API-052 | Pagination (Cursor, Offset, Keyset - Deep Dive)  | ★★★        |
| API-053 | Pagination (Basics)                              | ★★☆        |
| API-054 | API Throttling                                   | ★★☆        |
| API-055 | API Documentation                                | ★☆☆        |
| API-056 | API Design Best Practices                        | ★★☆        |
| API-057 | Hypermedia / HATEOAS (Deep)                      | ★★★        |
| API-058 | API Deprecation Strategy                         | ★★★        |
| API-059 | API Observability                                | ★★★        |
| API-060 | API Security Best Practices                      | ★★★        |
| API-061 | What is an API                                   | ★☆☆        |
| API-062 | URL / URI / Endpoint                             | ★☆☆        |
| API-063 | Request / Response Model                         | ★☆☆        |
| API-064 | HTTP Protocol (Conceptual)                       | ★☆☆        |
| API-065 | JSON (API Data Format)                           | ★☆☆        |
| API-066 | Stateless Protocol (Conceptual)                  | ★☆☆        |
| API-067 | Client vs Server (API Context)                   | ★☆☆        |
| API-068 | Bearer Token (Conceptual)                        | ★☆☆        |
| API-069 | HTTP/2 Multiplexing and Server Push              | ★★★        |
| API-070 | Protobuf Encoding Internals                      | ★★★        |
| API-071 | WebSocket Protocol Internals (Framing)           | ★★★        |
| API-072 | Circuit Breaker Pattern (API Resilience)         | ★★★        |
| API-073 | API Fuzzing                                      | ★★★        |
| API-074 | Richardson Maturity Model                        | ★★★        |
| API-075 | gRPC-Web                                         | ★★★        |
| API-076 | REST Dissertation (Fielding, 2000)               | 🔬          |
| API-077 | HTTP/2 Design Rationale (RFC 7540)               | 🔬          |
| API-078 | HTTP/3 over QUIC Design Rationale (RFC 9114)     | 🔬          |
| API-079 | gRPC Protocol Specification Design               | 🔬          |
| API-080 | GraphQL Specification Design (Lee Byron)         | 🔬          |
| API-081 | OpenAPI Specification Design                     | 🔬          |
| API-082 | WebSocket Protocol RFC 6455 Design               | 🔬          |
