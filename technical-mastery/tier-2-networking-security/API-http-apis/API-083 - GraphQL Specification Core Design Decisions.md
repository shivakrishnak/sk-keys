---
id: API-083
title: "GraphQL Specification Core Design Decisions"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★★★★★
depends_on: API-075, API-082
used_by: API-084
related: API-075, API-076, API-079, API-082, API-084
tags:
  - graphql
  - specification
  - schema
  - resolvers
  - introspection
  - federation
  - design-decisions
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/api/graphql-specification-core-design-decisions/
---

⚡ TL;DR - GraphQL's core spec decisions: schema-first
typing (SDL, strongly typed, nullable by default, use
`!` for non-null), single POST endpoint (queries,
mutations, subscriptions), execution model (each field
resolved independently by its resolver), introspection
(clients can query the schema itself at runtime - power
and a security risk for public APIs), errors (partial
success - response can have both `data` and `errors`
simultaneously), and aliases (client renames fields
in response); the most misunderstood spec decision:
GraphQL does NOT define HTTP transport - it is a query
language and execution spec, not a protocol; production
GraphQL requires conventions (persisted queries, depth
limiting, query complexity analysis) that are not in
the spec because they are security/performance additions,
not language features; Apollo Federation extends the
spec with `@key` and `@external` directives for
distributed subgraphs.

---

| #083 | Category: HTTP & APIs | Difficulty: ★★★★★ |
|:---|:---|:---|
| **Depends on:** | GraphQL vs REST vs gRPC Decision Framework, gRPC Design Rationale | |
| **Used by:** | Open Problems in API Design | |
| **Related:** | Decision Framework, API Platform, Event-Driven APIs, gRPC Rationale, Open Problems | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Facebook 2012: News Feed on mobile needs data from:
user profile, posts (with author, likes, comments,
attachments), friend suggestions, ads, trending topics.
REST: 8-12 HTTP round trips on a 200ms-latency 3G
connection = 1600-2400ms just for network. Each
round trip fetching data that may not even be displayed
(overfetching: getting 50 post fields when mobile
shows 5). Server team must build custom "summary"
endpoints for each screen. 5 screens × 5 custom
endpoints = 25 maintenance endpoints. New mobile
screen requires new backend endpoint (blocked on
backend team). GraphQL was designed to solve this
specific Facebook mobile problem.

---

### 📘 Textbook Definition

**GraphQL Specification (current: October 2021):**
Open-source specification (originally Facebook, donated
to GraphQL Foundation 2018). Defines: the query language
(what clients send), the type system (how schemas are
defined), and the execution model (how servers resolve
queries). Does NOT define: transport (not HTTP-specific),
caching strategy, authorization model, or pagination.

**Schema Definition Language (SDL):**
```graphql
type Order {
  id: ID!             # Non-null (!)
  status: OrderStatus! # Non-null enum
  totalCents: Int!
  currency: String     # Nullable (no !)
  items: [OrderItem!]! # Non-null list of non-null items
  customer: Customer   # Nullable (if not loaded)
}

enum OrderStatus {
  PLACED
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}

type Query {
  order(id: ID!): Order  # Returns nullable Order (may not exist)
  orders(
    limit: Int = 10
    cursor: String
  ): OrderConnection!
}

type Mutation {
  createOrder(input: CreateOrderInput!): OrderResult!
  cancelOrder(id: ID!): Order
}

type Subscription {
  orderStatusChanged(orderId: ID!): Order!
}
```

**Execution model:**
Each field in the schema has a resolver function.
Resolvers are called independently per field.
Query is executed depth-first: parent resolver runs
first, then child resolvers with the parent's return
value as context. This enables: DataLoader batching,
authorization per-field, lazy loading of nested data.

**Introspection:**
GraphQL servers expose a built-in `__schema` query
that returns the full type system description.
Enables: GraphQL clients (GraphiQL, Playground) to
provide autocomplete, IDEs to type-check queries.
Risk: exposes full schema to any client. For public
APIs: disable introspection in production.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GraphQL is a typed query language where clients specify
exactly what data they need; the spec defines the type
system, query language, and execution model but not the
transport.

**One analogy:**
> GraphQL schema is like a database schema for your API.
> The schema defines all possible types and relationships.
> GraphQL query is like a SQL SELECT statement: you specify
> exactly which columns you want, with what joins, with
> what filters. The server executes the query against the
> schema (resolvers = execution layer) and returns exactly
> what was requested. The key difference: SQL is a standard
> that includes transport (connection protocol, auth).
> GraphQL spec defines only the query language and execution,
> not how it is transported (which is usually HTTP POST,
> but not mandated by the spec).

---

### 🔩 First Principles Explanation

**Nullability design (SDL `!` vs nullable):**

```
SPEC DECISION: Fields are NULLABLE by default.
Non-null requires explicit `!` annotation.

WHY: GraphQL's partial success model.
If a resolver fails for a non-null field:
  - GraphQL propagates null UP the tree
  - Potentially nullifies the entire parent object
  - Returns error in the errors array

EXAMPLE:
type Order {
  id: ID!          # Non-null
  customer: Customer  # Nullable (customer might fail to load)
}

Query: { order(id: "123") { id customer { name } } }

If customer resolver throws:
  "errors": [{"message": "Failed to load customer"}]
  "data": {"order": {"id": "123", "customer": null}}

The order data is partially returned. This is GraphQL's
"partial success" model: data can be partially resolved
even when some resolvers fail.

IF customer were non-null (Customer!):
  GraphQL propagates null UP to the parent.
  data = {"order": null}
  The entire order is null because customer could not be null.
  Loss of all order data due to one resolver failure.

PRACTICAL RULE:
  Use non-null (!) for fields that:
  - Are always present when the parent exists
  - Never fail to resolve
  - Are IDs and required identifiers
  Use nullable for:
  - Relationships that may fail to load
  - Optional fields that can be absent
  - Any field that might cause partial nullification
```

**Aliases (duplicate field with different args):**

```graphql
# Without aliases: cannot fetch the same field twice
query {
  order(id: "123") { id status }
  order(id: "456") { id status }  # Error: duplicate field
}

# With aliases: rename fields in response
query {
  order1: order(id: "123") { id status }
  order2: order(id: "456") { id status }
}
# Response:
# { "order1": {"id": "123", ...}, "order2": {"id": "456", ...} }
```

---

### 🧪 Thought Experiment

**SCENARIO: Why persisted queries are not in the spec**

```
SECURITY ISSUE WITH INTROSPECTION + ARBITRARY QUERIES:

1. Introspection reveals full schema:
   query { __schema { types { name fields { name } } } }
   Returns: every type, field, enum in the schema.
   An attacker who can query your GraphQL API
   now knows your entire data model.

2. Arbitrary deep queries create DoS vectors:
   query {
     order(id: "1") {
       items { product { category { products { items {
         product { category { products { items {
           product { id }  # ...N levels deep
         }}}
       }}}}}
     }
   }
   Naive GraphQL server: executes every resolver.
   Exponential DB queries. Server OOM or timeout.

SPEC RESPONSE: GraphQL spec does NOT define:
  - Query depth limiting
  - Query complexity scoring
  - Persisted queries (pre-approved query whitelist)
  - Introspection disable

These are runtime SECURITY additions:
  Persisted queries: client sends query_id (hash of known query)
    Server executes only pre-registered queries.
    Arbitrary queries rejected.
    ArbitraryQueryError for unknown IDs.
    Eliminates arbitrary query DoS AND hides schema.
  Depth limiting: reject queries with depth > N.
  Complexity scoring: each field has a cost; reject
    if total cost > budget.
  Disable introspection in production (Apollo Server config):
    app = App(schema, introspection=False)

WHY NOT IN SPEC:
  The spec is the query language and execution model.
  Security enforcement is deployment context.
  (Same pattern: HTTP spec does not define TLS -
  that is a deployment concern)
```

---

### 🧠 Mental Model / Analogy

> GraphQL's execution model is like a tree traversal
> with lazy evaluation. The query describes a tree:
> root fields (order), with children (items, customer),
> with grandchildren (items.product, customer.address).
> Execution: root resolver runs first. Returns an Order
> object. Then all children of Order that were requested
> run in parallel (items resolver AND customer resolver).
> Then their children run in parallel. The result is
> assembled bottom-up from resolver return values.
> DataLoader intercepts "load product for item" calls
> from all OrderItem resolvers and batches them into
> one database query. Without DataLoader: one DB query
> per item (N+1 problem at the database level, not
> HTTP level). With DataLoader: the tree's leaf nodes
> share a single batch query per type per request.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
GraphQL is a way to describe exactly what data you need
from an API (like filling out a form for "I want the
order ID, the status, and the first 5 item names -
nothing else"). The API returns exactly that, not more.

**Level 2 - How to use it (junior developer):**
Define schema in SDL (`.graphql` files or schema strings).
Write resolvers for each field. Use DataLoader for any
resolver that queries a database in a loop (avoids N+1
queries). Disable introspection in production. Add
depth limiting (max 10 levels) and complexity limiting
(each field costs points; reject if total > budget).

**Level 3 - How it works (mid-level engineer):**
Execution flow: parse query → validate against schema
→ execute (resolver tree). Each resolver receives:
`(parent_value, args, context, info)`.
`parent_value`: what the parent resolver returned.
`args`: field arguments from the query.
`context`: shared per-request context (user, DB connection, DataLoaders).
`info`: metadata about the current field in the schema tree.
DataLoader: per-request batch collector. First call to
`loader.load(id)` queues it. Next tick: all queued IDs
are passed to `batch_fn(ids)` together. Returns promise
for each individual ID from the batch result.

**Level 4 - Why it was designed this way (senior/staff):**
The schema-first design was a key architectural decision.
REST: the contract is defined by URL + HTTP verb +
documentation (OpenAPI is added later). GraphQL: the
contract IS the schema (SDL). Every query is validated
against the schema before execution. Invalid fields,
wrong types, missing required arguments - all caught
at the validation stage, before any resolver runs.
This makes the schema the source of truth for the API
contract. Tools (GraphiQL, Apollo Studio, IDE plugins)
use introspection to provide real-time autocomplete and
type checking. The schema as the contract enables
Apollo Federation: each service owns a subgraph schema;
the Gateway validates distributed queries against the
composed full schema before routing.

**Level 5 - Mastery (distinguished engineer):**
GraphQL Federation architecture. Multiple services each
expose a GraphQL subgraph. Each subgraph declares which
types it owns and which it extends. A schema composition
step merges subgraphs into a unified schema (run by
the Gateway or a schema registry). Client queries the
Gateway; Gateway analyzes the query, decomposes it into
sub-queries for each relevant subgraph, executes in
parallel where possible, assembles the result. Netflix
implementation: 500+ federated schema fields contributed
by 40+ teams. Composition validation: a new subgraph
must not break the composed schema (same constraint
as Protobuf backward compatibility for REST). Apollo
Router: the Rust-based high-performance Apollo Federation
gateway that replaced the Node.js Apollo Gateway.

---

### ⚙️ How It Works (Mechanism)

**Strawberry GraphQL (Python) with DataLoader:**

```python
import strawberry
from strawberry.types import Info
from strawberry.dataloader import DataLoader
from typing import Optional
import asyncio

@strawberry.type
class Customer:
    id: strawberry.ID
    email: str
    name: str

@strawberry.type
class OrderItem:
    product_id: strawberry.ID
    quantity: int
    unit_price_cents: int

@strawberry.type
class Order:
    id: strawberry.ID
    status: str
    total_cents: int

    @strawberry.field
    async def items(self, info: Info) -> list[OrderItem]:
        """
        DataLoader: batches all item queries for orders
        in this request into one DB query.
        Without DataLoader: N queries for N orders.
        With DataLoader: 1 query for all N orders' items.
        """
        return await info.context.loaders.order_items.load(
            str(self.id)
        )

    @strawberry.field
    async def customer(
        self, info: Info
    ) -> Optional[Customer]:
        """
        Returns Optional (nullable) Customer.
        If customer resolver fails: returns None (partial success)
        without failing the entire order.
        """
        try:
            return await info.context.loaders.customers.load(
                str(self.customer_id)
            )
        except Exception:
            # Return None (nullable field) - partial success
            # GraphQL adds error to errors array automatically
            return None

@strawberry.type
class Query:
    @strawberry.field
    async def order(self, id: strawberry.ID) -> Optional[Order]:
        order = await fetch_order(str(id))
        return order  # None if not found → null in response

# DataLoader batch functions
async def batch_load_order_items(
    order_ids: list[str],
) -> list[list[OrderItem]]:
    """Batch load items for multiple orders in one query."""
    rows = await db.fetch_all(
        "SELECT * FROM order_items WHERE order_id = ANY($1)",
        order_ids
    )
    items_by_order: dict[str, list[OrderItem]] = {
        oid: [] for oid in order_ids
    }
    for row in rows:
        items_by_order[row.order_id].append(
            OrderItem(
                product_id=row.product_id,
                quantity=row.quantity,
                unit_price_cents=row.unit_price_cents,
            )
        )
    return [items_by_order[oid] for oid in order_ids]

# Context factory (per request)
def get_context():
    return {
        "loaders": type("Loaders", (), {
            "order_items": DataLoader(
                load_fn=batch_load_order_items
            ),
            "customers": DataLoader(
                load_fn=batch_load_customers
            ),
        })()
    }

schema = strawberry.Schema(query=Query)
```

**Query complexity and depth limiting:**

```python
from graphql import build_ast_schema, parse
from strawberry.extensions import (
    QueryDepthLimiter,
)

# Depth limiting (Strawberry extension)
# Rejects queries deeper than max_depth
schema = strawberry.Schema(
    query=Query,
    extensions=[
        QueryDepthLimiter(max_depth=10),
    ],
)

# Custom complexity limiting (strawberry-graphql-django):
def complexity_calculator(
    field, child_complexity: int
) -> int:
    """
    Assign cost to each field.
    Reject if total > budget.
    """
    if field.name in ("items", "orders"):
        # List fields: multiply by typical list size
        return 10 + child_complexity * 5
    return 1 + child_complexity

# Disable introspection in production
import os

schema = strawberry.Schema(
    query=Query,
    # Introspection disabled in production
    extensions=(
        [] if os.getenv("ENVIRONMENT") == "production"
        else [IntrospectionExtension()]
    ),
)
```

```mermaid
flowchart TB
    Q[Client sends GraphQL query\nPOST /graphql\n{ order id123 { id status items { productId } } }]
    P[Parse\nQuery → AST]
    V[Validate\nAgainst schema\nCheck field names, types, args]
    E[Execute\nRoot resolver: order id=123]
    R1[Resolver: order.id\nreturns string]
    R2[Resolver: order.status\nreturns string]
    R3[Resolver: order.items\nDataLoader.load order-id]
    DL[DataLoader batch\nSELECT * FROM items WHERE order_id IN ...]
    R4[Resolver: item.productId\nfor each item]
    AS[Assemble result\n{ data: { order: { id, status, items } } }]

    Q --> P --> V --> E
    E --> R1 & R2 & R3
    R3 --> DL --> R4 --> AS
    R1 & R2 --> AS
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Persisted queries (security hardening):**

```python
# Persisted queries: pre-register approved queries
# Client sends query hash, not query string
# Prevents arbitrary query attacks + reduces payload size

import hashlib
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Registry of approved queries (built at deploy time)
APPROVED_QUERIES: dict[str, str] = {
    "GetOrderById": """
        query GetOrderById($id: ID!) {
          order(id: $id) {
            id
            status
            totalCents
            items {
              productId
              quantity
            }
          }
        }
    """,
    # ... other approved queries
}

@app.post("/graphql")
async def graphql_endpoint(request: dict):
    """
    Persisted query endpoint.
    Accepts query_id (hash) + variables.
    Rejects arbitrary queries in production.
    """
    query_id = request.get("queryId")
    query = request.get("query")
    variables = request.get("variables", {})

    if query_id:
        # Look up pre-approved query
        approved_query = APPROVED_QUERIES.get(query_id)
        if not approved_query:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown query ID: {query_id}",
            )
        query = approved_query
    elif os.getenv("ENVIRONMENT") == "production":
        # In production: reject arbitrary queries
        raise HTTPException(
            status_code=400,
            detail="Arbitrary queries not allowed. Use queryId.",
        )

    result = await schema.execute_async(
        query, variable_values=variables
    )
    return {"data": result.data, "errors": result.errors}
```

---

### 💻 Code Example

**Example 1 - BAD: Non-null fields on relationships (nullification cascade)**

```graphql
# BAD: All fields non-null including relationships
type Order {
  id: ID!
  status: OrderStatus!
  customer: Customer!    # Non-null - DANGEROUS
  items: [OrderItem!]!   # Non-null list - DANGEROUS
}

# Problem: if customer resolver fails (DB down, timeout):
# GraphQL must propagate null UP to satisfy non-null.
# customer is Customer! (non-null) → can't return null.
# Propagates null to parent Order.
# Order is also Order! (non-null in query root)?
# Propagates null to root → entire query returns null.
# { data: null, errors: [{ message: "Customer load failed" }] }
# ALL order data lost because of one relationship failure.

# GOOD: Nullable relationships, non-null scalars
type Order {
  id: ID!           # Scalars that always exist: non-null
  status: OrderStatus!
  totalCents: Int!
  customer: Customer # NULLABLE - allows partial success
  items: [OrderItem!] # NULLABLE list - fails gracefully
}
# If customer fails:
# { data: { order: { id: "123", status: "PLACED",
#           customer: null } },
#   errors: [{ message: "Customer load failed",
#              path: ["order", "customer"] }] }
# Order data is preserved. Customer is null.
# Client can show order without customer details.
```

---

### ⚖️ Comparison Table

| Spec Feature | Decision | Trade-off |
|:---|:---|:---|
| **Single endpoint** | POST /graphql for all operations | Cannot use URL-based caching (CDN); must use Apollo Client normalized cache |
| **Nullable by default** | All fields nullable unless `!` | Enables partial success; requires careful non-null annotation |
| **Introspection** | Built into spec; queryable at runtime | Powerful tooling (GraphiQL); information disclosure risk in public APIs |
| **Partial success** | `data` + `errors` can coexist | Complex error handling; client must check both |
| **Transport agnostic** | Not HTTP-specific in spec | HTTP conventions (POST, caching) not standardized; use Apollo/Relay conventions |
| **Subscriptions** | In spec; implementation varies | No standard transport; usually WebSocket (not in spec) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| GraphQL responses always have HTTP 200 | In GraphQL, HTTP 200 with errors in the `errors` array is NOT the same as a client sending a malformed request (HTTP 400). GraphQL spec specifies: use 200 for any response where the GraphQL engine executed (even if resolvers returned errors). Use 400 for HTTP-level errors (malformed JSON, not a valid GraphQL request). This means monitoring based on HTTP status codes alone misses all GraphQL resolver errors. Production monitoring must check for `errors` in the response body. |
| You can use GET requests for GraphQL queries | The GraphQL spec does not mandate HTTP POST. Simple queries (no side effects) CAN use GET (with query string encoded query parameter). This enables CDN caching for GET-based queries (caching by URL). Libraries like urql support GET for queries. However: variables must be URL-encoded, limiting query complexity. Facebook's implementation uses GET for queries (enabling CDN). Mutations: always POST (idempotency concerns). This is an OPTIONAL optimization, not required by spec. |
| GraphQL schemas are self-documenting via introspection | Introspection reveals field names and types but not semantic documentation. A field named `status` returning `String` tells you nothing about what values are valid or what state transitions are allowed. Proper GraphQL schema documentation requires: (1) description strings on every type and field in SDL, (2) enum values with descriptions, (3) deprecation annotations (`@deprecated(reason: "Use newField instead")`). Introspection without descriptions is a schema skeleton, not documentation. |

---

### 🚨 Failure Modes & Diagnosis

**GraphQL resolver N+1 at database level (no DataLoader)**

**Symptom:** GraphQL endpoint is slow. DB CPU is high.
Query logs show hundreds of identical queries per request
(e.g., 50 queries: "SELECT * FROM products WHERE id=?").
Response time is 2-5 seconds for a list of 50 orders.

**Root Cause:** Order list query with items.product field.
Each OrderItem resolver calls `fetch_product(product_id)`
independently. 50 orders × 2 items each = 100 product
queries per request.

**Diagnosis:**
```python
# Enable query logging in SQLAlchemy or asyncpg
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Run the GraphQL query.
# Log output shows:
# INFO SELECT * FROM products WHERE id = 'p001'
# INFO SELECT * FROM products WHERE id = 'p002'
# ... 98 more identical queries

# Check: is DataLoader configured in context?
# If DataLoader is configured but N+1 still occurs:
# Likely cause: DataLoader not shared across resolvers
# (each resolver creates a new DataLoader instance)
```

**Fix:**
1. Create DataLoader ONCE per request in context factory.
2. Each resolver uses `info.context.loaders.products.load(id)`.
3. DataLoader batches all `.load()` calls made during the
   current execution tick into one `batch_fn([ids])` call.
4. Verify: after fix, product queries reduced to 1-2 per request.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `GraphQL vs REST vs gRPC Decision Framework` - when to use GraphQL

**Builds On This (learn these next):**
- `Open Problems in API Design` - unsolved GraphQL challenges
- `API Platform Design` - governance for GraphQL at scale

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ Nullability  │ Default: nullable. Use ! for non-null.    │
│              │ Nullable relationships = partial success  │
├──────────────┼───────────────────────────────────────────┤
│ DataLoader   │ Batch all resolver DB calls per request.  │
│              │ 1 SQL per type per request, not N.        │
├──────────────┼───────────────────────────────────────────┤
│ Introspection│ Disable in production (security risk).    │
│              │ Reveals full schema to clients.           │
├──────────────┼───────────────────────────────────────────┤
│ Persisted Q  │ Pre-register queries by hash. Reject      │
│              │ arbitrary queries in production.          │
├──────────────┼───────────────────────────────────────────┤
│ Partial succs│ data + errors coexist. Check BOTH.        │
│              │ HTTP 200 does NOT mean success in GQL.    │
├──────────────┼───────────────────────────────────────────┤
│ Complexity   │ Depth limit (max 10). Cost scoring.       │
│              │ Reject > budget. Prevents DoS.            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Schema = contract. Resolver = per field. │
│              │  DataLoader = N+1 fix. Introspect = off." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use nullable fields for relationships and non-null
   for scalars. Non-null failure cascades up the tree,
   potentially nullifying parent objects (partial success lost).
2. DataLoader is not optional - it is required for any
   list resolver that fetches related data. Without it:
   N+1 database queries per request.
3. Disable introspection in production (information
   disclosure risk). Add depth limiting and query complexity
   scoring. Use persisted queries for public APIs to prevent
   arbitrary query DoS.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Partial success is a feature, not a failure mode."
GraphQL's `data + errors` model acknowledges that real
distributed systems have partial failures. Some fields
succeed; some fail. Returning all-or-nothing (as REST
does with HTTP 200 or 500) loses the successful data
when one part fails. GraphQL's design: return everything
that succeeded, annotate what failed, let the client
decide what to show. This principle applies to:
batch API operations (return partial results + error list
instead of failing the whole batch on one error),
event processing (process what you can, dead-letter
what you cannot), database transactions (saga pattern:
compensating transactions for partial failures instead
of all-or-nothing distributed transactions). The design
trade-off: partial success requires more complex client
handling (must check both data and errors). All-or-nothing
is simpler to reason about but loses successful results
on partial failure.

**Where else this pattern applies:**
- Kafka consumer: process all messages, DLQ failed ones
  (partial success per batch)
- S3 batch delete: returns successful deletes AND failures
  in one response
- Google Cloud Pub/Sub: partial ACK (ACK successfully
  processed, NACK failed)
- HTTP 207 Multi-Status: WebDAV and some REST APIs
  return 207 with per-resource status in body

---

### 💡 The Surprising Truth

The most important design decision Facebook made when
building GraphQL was NOT the query language itself -
it was the choice to make the type system nullable by
default. This seems like a small detail but it has
profound implications for how GraphQL handles the
fundamental distributed systems problem of partial
failure. In any system that aggregates data from
multiple sources (orders + products + customers),
some sources will occasionally fail. Protobuf and
strongly-typed REST APIs assume all data is available
or the whole request fails. GraphQL assumes some data
will be unavailable and builds the type system around
returning partial data gracefully. The `!` (non-null)
annotation is an explicit commitment by the schema
author: "this field will NEVER fail to resolve." For
database scalars (an order's ID is always present if
the order exists): `ID!` is correct. For cross-service
fetches (customer data from another service): nullable
is correct. Teams that make everything non-null in
their GraphQL schemas "because it looks cleaner" will
discover this mistake the first time a downstream
service has an outage and their GraphQL API returns
`null` for the entire response instead of returning
the 90% of data that was available.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** GraphQL's nullability model: when to use `!`
   and when nullable is correct (partial success design).
2. **IMPLEMENT** DataLoader for a list resolver that
   fetches related data (e.g., product for each OrderItem).
3. **CONFIGURE** Depth limiting, complexity scoring, and
   introspection disabling for a production GraphQL API.
4. **DESIGN** A persisted queries implementation that
   rejects arbitrary queries in production.
5. **DEBUG** A GraphQL N+1 problem using query logging
   and confirm the fix with DataLoader.

---

### 🎯 Interview Deep-Dive

**Q1: What is the N+1 problem in GraphQL and how does
DataLoader solve it?**

*Why they ask:* Tests GraphQL production knowledge.

*Strong answer includes:*
- N+1 problem: GraphQL execution is per-field. A query for
  50 orders, each with items.product: the order list resolver
  returns 50 orders. For each order, the items resolver
  returns 5 items. For each item, the product resolver calls
  `fetch_product(product_id)`. 50 orders × 5 items = 250
  product fetches. Each product fetch = 1 SQL query.
  250 SQL queries per GraphQL request = N+1 (1 for orders,
  N for products). At 100 requests/sec: 25,000 product queries/sec.
- DataLoader solution: created by Facebook to solve this problem.
  Works as a per-request batching layer. All resolver calls
  to `dataloader.load(id)` within the same JavaScript/Python
  "tick" (execution cycle) are collected. After the tick:
  `batch_fn([id1, id2, ..., idN])` is called once with all IDs.
  1 SQL query: `SELECT * FROM products WHERE id IN (ids...)`.
  Results mapped back to each individual `load()` promise.
- Critical: DataLoader must be per-request (not shared across
  requests). If shared: stale data risk (data from one user's
  request cached and returned to another user's request).
  Create new DataLoader instances in the request context factory.

**Q2: How do you secure a GraphQL API for public use?**

*Why they ask:* Tests production GraphQL security knowledge.

*Strong answer includes:*
- Disable introspection: prevents schema exposure to anonymous
  clients. `strawberry.Schema(introspection=False)` or
  Apollo Server `introspection: false` in production.
  Allow introspection in dev/staging environments only.
- Query depth limiting: reject queries with depth > 10
  (default). Prevents deeply nested queries that create
  exponential resolver chains. Most legitimate queries
  are 3-5 levels deep.
- Query complexity scoring: assign a cost to each field.
  List fields (items, orders) cost more (they expand).
  Reject if total query cost > budget (e.g., 1000 points).
  Example: top-level query=1, scalar field=1, list field=10,
  nested list=10×parent_cost.
- Persisted queries: pre-register all approved queries by hash.
  Only accept query_id, not arbitrary query strings.
  In production: reject any request without a valid query_id.
  This is the strongest protection (eliminates arbitrary
  query attack surface entirely) but requires query management
  workflow (register queries during CI/CD).
- Authorization: per-field authorization using Strawberry
  permission classes or custom directives. Do not rely on
  query-level authorization alone.
- Rate limiting: by API key + query complexity score combined.
  A low-cost query can be called more frequently than
  a high-cost query.
