---
id: MSV-019
title: API Composition Pattern
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-013, MSV-010, MSV-002
used_by: MSV-050
related: MSV-013, MSV-010, MSV-050, MSV-033, MSV-029
tags:
  - microservices
  - pattern
  - intermediate
  - architecture
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /microservices/api-composition-pattern/
---

# MSV-019 - API Composition Pattern

⚡ TL;DR - API Composition is the pattern of aggregating
data from multiple microservices in memory to serve a
query that spans service boundaries. It is the primary
solution to the "no JOIN across services" problem in
microservices, used in both BFF and Query Service contexts.

| #019 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Backend for Frontend (BFF), Inter-Service Communication, Microservices Architecture | |
| **Used by:** | CQRS in Microservices | |
| **Related:** | Backend for Frontend (BFF), Inter-Service Communication, CQRS in Microservices, Aggregate, Contract-First API Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Order Service and User Service are separate databases.
A query: "Get all orders with user names and addresses"
would need a JOIN in a monolith. In microservices, there
is no shared database to JOIN. Without API Composition:

Option 1: Client calls Order Service, then separately
calls User Service for each user - N+1 network calls,
O(N) latency.

Option 2: Order Service calls User Service directly -
tight coupling, Order Service now depends on User Service
API for its core function.

Option 3: Combine databases (shared DB anti-pattern) -
but now deployments are coupled and schema changes
coordinate across services.

**THE INVENTION MOMENT:**
API Composition introduces a Composer: a separate query
service or BFF that orchestrates calls to both services,
joins data in memory, and returns the composed result.
The composer owns the cross-service query logic without
coupling the source services to each other.

---

### 📘 Textbook Definition

**API Composition Pattern** is an implementation strategy
for queries that span multiple microservices by using
a Composer (a dedicated query service, BFF, or API Gateway)
that: (1) receives the query, (2) dispatches sub-queries
to the relevant microservices in parallel, (3) joins
the results in memory (in-memory JOIN), and (4) returns
the assembled response to the caller. It is the primary
alternative to shared databases for cross-service queries
in microservices architectures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API Composition replaces a database JOIN with a memory
join in a Composer service: fetch data from multiple
services in parallel, assemble in-memory, return as one.

**One analogy:**
> A research assistant preparing a report. They can't
> query a single master database. Instead: call the HR
> system for employee data, call the Finance system for
> budget data, call the Projects system for assignments,
> then assemble the report from three separate sources
> on their desk (in-memory join). The report looks like
> it came from one place, but the assistant did the
> cross-system composition.

**One insight:**
API Composition shifts JOIN cost from the database layer
(one fast DB join) to the application layer (multiple
network calls + memory merge). This trade-off is acceptable
for small-medium result sets, but at large scale (JOIN
across 10,000+ records) the N network calls become
the bottleneck. CQRS with a read-optimised view is the
alternative for high-volume cross-service queries.

---

### 🔩 First Principles Explanation

**THE COMPOSITION MECHANISM:**

```
Query: "Find all orders placed in last 7 days
        with user details"

WITHOUT API COMPOSITION (N+1 problem):
  GET /orders?since=7days -> [orderId, userId, amount]
  For each order (N orders):
    GET /users/{userId} -> {name, email, address}
  Total: 1 + N network calls
  N=100 orders: 101 network calls (slow, fragile)

WITH API COMPOSITION (parallel fan-out + in-memory join):
  Step 1: GET /orders?since=7days
           -> [{orderId:1, userId:A}, {orderId:2, userId:B}]
  Step 2: Extract unique userIds: [A, B]
  Step 3: GET /users?ids=A,B (batch call)
           -> [{id:A, name:Alice}, {id:B, name:Bob}]
  Step 4: In-memory join:
           Match orders.userId to users.id
  Result: [{orderId:1, user:Alice, amount:50},
           {orderId:2, user:Bob,   amount:75}]
  Total: 2 network calls (vs 1+N)
```

**PARALLEL COMPOSITION:**

```
Query: "Dashboard: user profile + recent orders + balance"

SEQUENTIAL (wrong):  500ms + 300ms + 200ms = 1000ms
PARALLEL (correct):  max(500ms, 300ms, 200ms) = 500ms

Java parallel composition:
  CompletableFuture<User> userFuture =
    CompletableFuture.supplyAsync(
      () -> userService.get(userId));
  CompletableFuture<List<Order>> ordersFuture =
    CompletableFuture.supplyAsync(
      () -> orderService.getRecent(userId));
  CompletableFuture<Balance> balanceFuture =
    CompletableFuture.supplyAsync(
      () -> accountService.getBalance(userId));
  CompletableFuture.allOf(
    userFuture, ordersFuture, balanceFuture).join();
  // All run in parallel, wait for last to complete
```

---

### 🧪 Thought Experiment

**COMPOSITION SCALE ANALYSIS:**

```
SCENARIO: Order history page for admin
  Shows 500 orders with user details + product details

NAIVE COMPOSITION:
  GET /orders (500 orders)
  For each order:
    GET /users/{userId}   - 500 calls
    GET /products/{id}    - 500 calls
  Total: 1001 network calls
  Latency: 500 * (20ms/call) = 10 seconds
  UNACCEPTABLE

OPTIMISED COMPOSITION (batch + cache):
  GET /orders?limit=500 -> 500 orders
  Extract unique userIds (may be <500, users repeat)
  Extract unique productIds
  GET /users?ids={200 unique ids}  - 1 call
  GET /products?ids={150 unique ids} - 1 call
  In-memory join: 500 orders + 200 users + 150 products
  Total: 3 network calls
  Latency: 3 * 20ms = 60ms
  ACCEPTABLE

KEY: Batch API support required in downstream services
  GET /users?ids=a,b,c,d (NOT GET /users/{id} repeated)
  This is a design constraint of API Composition:
  downstream services must support batch queries
```

---

### 🧠 Mental Model / Analogy

> API Composition is like a data analyst pulling from
> multiple spreadsheets. The analyst has an Excel sheet
> of sales (from CRM), employee names (from HR), and
> territories (from geographic DB). To produce the
> sales-by-rep report: VLOOKUP in memory across three
> sheets. The source systems are separate and unchanged;
> the analyst's memory (and Excel) is the join engine.
> Composer = data analyst. In-memory join = VLOOKUP.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you need data from multiple services at once, you
call them all and combine the results. Like assembling
a puzzle from multiple boxes - each box has some pieces,
you combine them to see the whole picture.

**Level 2 - How to use it (junior developer):**
Create a Composer service (or use the BFF). Call Order
Service and User Service. Use CompletableFuture.allOf
for parallel calls. Join the results using a Map keyed
by userId. Return the assembled DTO.

**Level 3 - How it works (mid-level engineer):**
The composition steps: (1) Receive composed query,
(2) Decompose into per-service sub-queries, (3) Dispatch
parallel calls (CompletableFuture or reactive), (4) Wait
for all results (allOf / Mono.zip), (5) Join in memory
(Map lookup or stream groupBy), (6) Filter, sort, page
the composed result, (7) Return. Performance constraint:
memory usage grows with result set size.

**Level 4 - Why it was designed this way (senior/staff):**
API Composition works well when: (1) result sets are
small-medium (< ~10,000 rows), (2) downstream services
support batch/bulk queries, (3) the composition is
cacheable. It breaks down when: (1) large result sets
(memory join of 1M records), (2) downstream services
don't support batch (N+1 problem), (3) high query
frequency (each request = N service calls). The correct
alternative for large-scale cross-service queries: CQRS
with a materialised view - a dedicated read store that
pre-joins data from multiple services via events.

**Level 5 - Mastery (distinguished engineer):**
At scale, API Composition faces the fan-out amplification
problem: 1 API request to the Composer = N requests
to downstream services. At 1000 req/s to the Composer
with N=5 services: 5000 req/s across downstream services.
Each service must handle the amplified load. Load testing
must simulate the amplified load, not just the Composer's
load. Mitigation: response caching in the Composer
(reduces downstream load for repeated queries), and
rate limiting on the Composer's outbound calls (backpressure
to downstream services).

---

### ⚙️ How It Works (Mechanism)

**FULL COMPOSITION EXAMPLE:**

```java
@Service
public class OrderHistoryComposer {

    @Autowired OrderServiceClient orders;
    @Autowired UserServiceClient users;
    @Autowired ProductServiceClient products;

    public OrderHistoryResponse compose(
        OrderHistoryQuery query) {

        // Step 1: Fetch base data
        List<Order> orderList =
            orders.getOrders(query);

        // Step 2: Extract unique foreign keys
        Set<String> userIds = orderList.stream()
            .map(Order::getUserId)
            .collect(Collectors.toSet());
        Set<String> productIds = orderList.stream()
            .flatMap(o -> o.getItems().stream()
                .map(Item::getProductId))
            .collect(Collectors.toSet());

        // Step 3: Batch fetch related data in parallel
        CompletableFuture<Map<String, User>> usersFuture =
            CompletableFuture.supplyAsync(
                () -> users.getBatch(userIds).stream()
                    .collect(Collectors.toMap(
                        User::getId,
                        Function.identity())));

        CompletableFuture<Map<String, Product>> prodFuture =
            CompletableFuture.supplyAsync(
                () -> products.getBatch(productIds)
                    .stream()
                    .collect(Collectors.toMap(
                        Product::getId,
                        Function.identity())));

        CompletableFuture.allOf(
            usersFuture, prodFuture).join();

        // Step 4: In-memory join
        Map<String, User> userMap = usersFuture.join();
        Map<String, Product> productMap = prodFuture.join();

        List<OrderSummary> summaries = orderList.stream()
            .map(order -> OrderSummary.builder()
                .orderId(order.getId())
                .user(userMap.get(order.getUserId()))
                .items(order.getItems().stream()
                    .map(item -> ItemDetail.of(
                        item,
                        productMap.get(
                            item.getProductId())))
                    .collect(Collectors.toList()))
                .build())
            .collect(Collectors.toList());

        return new OrderHistoryResponse(summaries);
    }
}
// Network calls: 3 (orders + batch-users + batch-products)
// vs N+1 (orders + N user calls + N product calls)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPOSER ARCHITECTURE:**

```
Client: GET /order-history?userId=U123&limit=50
  │
  ▼
Order History Composer:
  Step 1: GET order-service/orders?userId=U123&limit=50
            (50 orders, may have 30 unique users,
             40 unique products)
  Step 2: Parallel batch calls:
    GET user-service/users?ids=id1,id2...id30
    GET product-service/products?ids=p1,p2...p40
  Step 3: In-memory join
  Step 4: Return 50 composed order summaries
  │
  Total network calls: 3
  Total latency: max(order, user, product) parallel time
  Memory: 50 orders + 30 users + 40 products

VS N+1 WITHOUT COMPOSITION:
  1 + 50 + 50 = 101 network calls
  Latency: 101 * 20ms = ~2 seconds
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: N+1 problem**

```java
// BAD: N+1 - fetches user for each order individually
List<Order> orders = orderService.getOrders(userId);
List<OrderDTO> result = new ArrayList<>();
for (Order order : orders) {
    // N individual user service calls
    User user = userService.getUser(order.getUserId());
    result.add(new OrderDTO(order, user));
}
// 100 orders = 101 network calls = ~2 seconds
```

```java
// GOOD: batch fetch + in-memory join = 3 calls total
List<Order> orders = orderService.getOrders(userId);
Set<String> userIds = orders.stream()
    .map(Order::getUserId)
    .collect(Collectors.toSet());
// 1 batch call instead of N individual calls
Map<String, User> userMap = userService
    .getUsersBatch(userIds).stream()
    .collect(Collectors.toMap(User::getId, u -> u));
// In-memory join: O(N) not O(N*M)
List<OrderDTO> result = orders.stream()
    .map(o -> new OrderDTO(o, userMap.get(o.getUserId())))
    .collect(Collectors.toList());
// 100 orders = 2 network calls = ~40ms
```

---

### ⚖️ Comparison Table

| Approach | Query Type | Scale | Latency | Consistency |
|---|---|---|---|---|
| **API Composition** | Cross-service queries | Small-medium result sets | Medium (fan-out) | Eventual |
| **Shared Database** | Any SQL JOIN | Any | Low (single query) | Strong (transactions) |
| **CQRS Read Model** | Read-optimised queries | Large result sets | Low (pre-joined) | Eventual |
| **GraphQL Federation** | Flexible client queries | Any | Medium | Eventual |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| API Composition is only for BFF | Any service can be a Composer. An Order Query Service that composes orders + users + products is API Composition. The pattern applies wherever cross-service data assembly is needed. |
| In-memory join is as fast as DB join | A DB join benefits from indexes, statistics, and query planning. An in-memory join in the Composer is a full scan of the result sets. For large result sets, CQRS with a pre-built read model performs orders of magnitude better. |
| API Composition creates tight coupling | The Composer depends on the APIs of downstream services, but the downstream services are independent of each other. The coupling is Composer-to-service, not service-to-service. |

---

### 🚨 Failure Modes & Diagnosis

**Partial failure in composition**

**Symptom:**
Order history page sometimes shows orders without
user names (blank field). Rarely, orders are missing.

**Root Cause:**
User Service occasionally returns 503. The Composer
returns partial results: orders without user enrichment.
No error propagated to the client.

**Diagnostic Command:**
```bash
# Check Composer logs for partial composition warnings
kubectl logs -l app=order-composer | \
  grep -E "partial|missing|fallback"

# Prometheus: track missing enrichment rate
rate(composer_enrichment_missing_total
  {service="user"}[5m])
# If >0: User Service returning errors during composition
```

**Design Decision:**
For missing enrichment, choose: (1) fail the request
(return error), (2) return partial (orders without user),
(3) return cached user data (stale but complete). The
choice depends on whether missing user data is acceptable
for the use case.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Backend for Frontend (BFF)` - BFF is the most common
  deployment context for API Composition
- `Inter-Service Communication` - all composition
  uses inter-service HTTP/gRPC calls

**Builds On This (learn these next):**
- `CQRS in Microservices` - the alternative to API
  Composition for large-scale cross-service queries:
  materialised views pre-join data via events

**Related Patterns:**
- `Aggregate` (DDD) - the boundary at which API Composition
  stops: composing across Aggregates is fine; replacing
  Aggregate internals with composition is wrong

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ Composer fetches from N services,        │
│              │ joins in memory, returns as one         │
├──────────────┼───────────────────────────────────────────┤
│ KEY          │ Batch queries to avoid N+1               │
│ OPTIMISATION │ Parallel calls (allOf / Mono.zip)        │
├──────────────┼───────────────────────────────────────────┤
│ LIMIT        │ Works for small-medium result sets       │
│              │ Large sets: use CQRS read model instead  │
├──────────────┼───────────────────────────────────────────┤
│ AMPLIFICATION│ 1 request = N downstream calls           │
│              │ Load test downstream at N * Composer load │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "In-memory JOIN replacing cross-service   │
│              │  database join - parallel batch calls"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS in Microservices → Event Sourcing   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. API Composition = in-memory JOIN. Fetch from multiple
   services, join in a Composer, return as one response.
2. Always use batch APIs to avoid the N+1 problem.
   GET /users?ids=a,b,c is 1 call; N individual calls
   are an anti-pattern.
3. For large result sets (>~10,000 rows), API Composition
   becomes slow and memory-intensive. CQRS with a
   materialised read model is the correct alternative.

**Interview one-liner:**
"API Composition solves the 'no JOIN across services'
problem by having a Composer (BFF or Query Service) fetch
data from multiple services in parallel, join in memory,
and return the assembled result. Key patterns: batch
queries to avoid N+1, parallel calls with CompletableFuture
or Mono.zip. Limitation: memory-intensive for large result
sets - CQRS read models are the alternative."

---

### 💡 The Surprising Truth

API Composition's relationship with consistency is subtle.
A database JOIN is ACID: reads from order and user table
in the same transaction - consistent snapshot. API
Composition calls Order Service at T=0, User Service at
T=5ms. Between T=0 and T=5ms, a user can update their
address. The composed result shows the order with the
NEW address, not the address at order time. This is
inevitable eventual consistency. For most queries, this
is acceptable. For audit or compliance queries ("what
was the delivery address at time of order?"), Order
Service must store the address snapshot at order creation,
not reference the User Service. Composition cannot
replace the need to store the right data at the right time.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Given a monolith query with 3 JOINs,
   map it to an API Composition design: identify the
   Composer, the sub-queries to each service, and
   the in-memory join strategy.
2. **OPTIMISE** Convert an N+1 composition (N individual
   calls) to a 3-call batch composition with parallel
   execution.
3. **DECIDE** Given a query over 1 million orders,
   explain why API Composition is not appropriate and
   design the CQRS read model alternative.
4. **HANDLE** Design partial failure handling in a
   Composer: when User Service is unavailable, what
   should the Order History Composer return?
5. **LOAD TEST** Explain why load testing the Composer
   at 1000 req/s requires validating that each downstream
   service can handle 3000-5000 req/s.

---

### 🧠 Think About This Before We Continue

**Q1.** You need to build an order history export feature:
500,000 orders per export request, each with user and
product details. API Composition would require fetching
500,000 orders, 200,000 unique users, and 50,000 unique
products in memory (potentially gigabytes). Design an
alternative architecture that solves this at scale.

**Q2.** A Composer calls Order Service and User Service.
Order Service returns 100ms. User Service returns 800ms.
The total composition time is 800ms (parallel). The P99
SLO is 500ms. What are the options to meet the SLO without
changing the User Service implementation?

**Q3.** Two Composer services both call the User Service.
The User Service has a database. Calculate: if each
Composer handles 500 req/s with 10 unique users per
request (batch call per Composer request), and there
are 2 Composers, what is the total QPS to User Service
and its database? How does caching in the Composer
reduce this load?