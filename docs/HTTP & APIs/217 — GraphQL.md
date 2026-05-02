---
layout: default
title: "GraphQL"
parent: "HTTP & APIs"
nav_order: 217
permalink: /http-apis/graphql/
number: "0217"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP, JSON, API Design Best Practices
used_by: GraphQL Schema, GraphQL Resolvers, GraphQL N+1 Problem
related: REST, gRPC, API Gateway, SOAP
tags:
  - api
  - graphql
  - query-language
  - intermediate
---

# 217 — GraphQL

⚡ TL;DR — GraphQL is a query language and runtime for APIs that lets clients ask for exactly the data they need, solving REST's over-fetching and under-fetching problems with a strongly typed schema as the single source of truth.

| #217 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP, JSON, API Design Best Practices | |
| **Used by:** | GraphQL Schema, GraphQL Resolvers, GraphQL N+1 Problem | |
| **Related:** | REST, gRPC, API Gateway, SOAP | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A mobile app displays a user profile: name, avatar, and their 3 most recent
posts with titles. The REST API has three endpoints: `/users/42`,
`/users/42/avatar`, `/users/42/posts`. The client makes 3 round trips.
Each response includes 40+ fields. The mobile app uses 5 of them.
This is both under-fetching (not enough in one call) and over-fetching
(too many fields per call). As the UI evolves, endpoints multiply or
diverge between mobile and web teams.

**THE BREAKING POINT:**
A product team has 6 different screens. The REST API has 30 endpoints
tailored to specific views. Every UI change requires a backend API change.
Mobile apps running v2.1 are still hitting deprecated `/v1/` endpoints.
Frontend teams are blocked waiting for backend engineers to add fields.
API versioning becomes a maintenance nightmare.

**THE INVENTION MOMENT:**
Facebook was building News Feed in 2012. Their iOS app had exactly this
problem — too many round trips, too many fields, too much coupling between
client needs and server implementation. They invented GraphQL internally,
then open-sourced it in 2015. The core insight: let the **client** declare
exactly what data it needs, and let the **server** declare what data it can
provide — bridge them with a typed schema.

---

### 📘 Textbook Definition

**GraphQL** is a query language for APIs and a server-side runtime for
executing those queries against a type system. Defined by a schema (SDL —
Schema Definition Language), GraphQL enables clients to request exactly the
fields they need from one or multiple resources in a single HTTP request.
It exposes a single endpoint (typically `POST /graphql`) and supports three
operation types: **Query** (read), **Mutation** (write/modify), and
**Subscription** (real-time event stream). The schema acts as a contract
between client and server and enables introspection, strong typing, and
automatic documentation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GraphQL lets the client write a "shopping list" of exactly what data it needs, instead of getting a fixed menu from the server.

**One analogy:**

> REST is like a restaurant with a fixed menu — you order the "user combo"
> and get name, email, phone, address, preferences, metadata, and audit logs
> whether you want them or not. GraphQL is like a custom order: "I'll have
> just the name and their last 3 posts, no metadata, and also their account
> status." One trip to the restaurant, exactly what you asked for.

**One insight:**
GraphQL shifts API negotiation power from server to client. In REST, the
server decides what a "user" object looks like. In GraphQL, each client
declares exactly what fields it needs. The server schema defines what's
_possible_; the query defines what's _wanted_. This decoupling is what
eliminates over-fetching and enables rapid UI iteration without API changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every data field has a type — the schema is the contract.
2. Clients request exactly the fields they need — nothing more, nothing less.
3. One endpoint, one request — eliminates round trip waterfall.
4. Schema is introspectable — the API documents itself.
5. Resolvers bridge schema fields to data sources.

**REST vs GraphQL Structural Comparison:**

```
REST:
  GET /users/42          → {id, name, email, phone, addr, ...40 fields}
  GET /users/42/posts    → [{id, title, body, author, tags, ...20 fields}]
  GET /posts/9/comments  → [...]
  = 3 requests, ~100 fields returned, client uses ~10

GraphQL:
  POST /graphql
  {
    user(id: "42") {
      name
      posts(last: 3) {
        title
        comments { count }
      }
    }
  }
  = 1 request, exactly 5 fields returned
```

**THE TRADE-OFFS:**

- Gain: client-driven → no over/under-fetching, fewer round trips.
- Cost: resolver complexity, N+1 query problem, more complex caching.
- Gain: schema as documentation, strong typing, introspection.
- Cost: single endpoint → HTTP caching doesn't work by URL.
- Gain: eliminates API versioning for most field additions.
- Cost: breaking changes still require deprecation strategy.

---

### 🧪 Thought Experiment

**SETUP:**
You're building a dashboard app. It shows: user name, 5 most recent orders
(just IDs and status), and the total unread notification count.

**REST APPROACH:**

```
GET /api/me               → {name, email, createdAt, ...20 fields}
GET /api/orders?limit=5   → [{id, status, items, shippingAddr, ...15 fields}]
GET /api/notifications    → [{id, text, read, createdAt}... all notifications]
// Client counts unread in JavaScript
```

3 requests, massive over-fetching, plus client-side count aggregation.

**GRAPHQL APPROACH:**

```graphql
query DashboardData {
  me {
    name
  }
  orders(last: 5) {
    id
    status
  }
  notifications(unreadOnly: true) {
    totalCount
  }
}
```

1 request, exactly 4 fields, server computes count.

**THE INSIGHT:**
GraphQL's power isn't just "fewer requests" — it's that product engineers
can build new screens without changing the backend. The schema already
exposes `orders`, `notifications`, `totalCount`. The client just writes
a new query. Zero backend changes required for UI iteration.

---

### 🧠 Mental Model / Analogy

> Think of REST as a filing cabinet with fixed drawers — each drawer (endpoint)
> gives you a fixed folder. GraphQL is a database query engine as your API —
> you write a SELECT statement (query) specifying exactly the columns you want
> from any combination of tables. The schema is the database schema. The resolver
> is the query executor. The client is the SQL developer.

- "SELECT name, email FROM users WHERE id = 42" → `user(id: "42") { name, email }`
- "JOIN posts ON user_id" → nested resolver: `user { posts { title } }`
- "Schema" → table definitions + types
- "Resolver" → the code that actually fetches the data for each field

**Where this breaks down:** SQL is optimized for set operations across a relational
store. GraphQL resolvers are per-field and can create N+1 query waterfalls unless
carefully batched with DataLoader. Unlike SQL, GraphQL doesn't have a built-in
optimizer — that's your job.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of having many different API endpoints (one for users, one for posts,
one for comments), GraphQL has ONE endpoint where you tell it exactly what data
you want, and it gives you exactly that — nothing extra.

**Level 2 — How to use it (junior developer):**
Write a query using GraphQL syntax. Queries fetch data; mutations change data;
subscriptions listen for changes. A query looks like a JSON skeleton: specify
the object, list the fields you want, nest for related data. Send it as the
body of a POST to `/graphql`. The response mirrors the query shape exactly.

**Level 3 — How it works (mid-level engineer):**
The server parses the query against the schema, validates field types and
arguments, then traverses the AST calling the resolver for each field. Resolvers
are functions: `(parent, args, context, info) → data`. Each field in the schema
has a resolver. If not explicitly defined, the default resolver reads the same-named
property from the parent object. This creates a resolver tree that mirrors the
query shape. The execution engine calls these resolvers (possibly in parallel
for sibling fields) and assembles the response. Without batching (DataLoader),
nested list resolvers create N+1 database queries.

**Level 4 — Why it was designed this way (senior/staff):**
GraphQL's design choices reflect Facebook's infrastructure realities. The
strongly typed schema enables introspection — tools like GraphiQL work because
the schema is self-describing. The single endpoint simplifies auth middleware
and avoids route proliferation. Field-level nullable types make partial responses
possible: if one resolver fails, the rest can still return, giving clients
partial data with errors. This differs from REST where a 500 kills the whole response.
The subscription type was added later and sits awkwardly on top of HTTP/WebSocket
transport, revealing that GraphQL was initially designed for request/response.
Persisted queries (store query on server, client sends ID) restore HTTP caching
and reduce bandwidth — acknowledging that the "single endpoint" approach sacrificed
caching. This shows GraphQL's design tension: optimized for developer experience at
the cost of web-native HTTP features.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│           GRAPHQL EXECUTION PIPELINE                     │
├──────────────────────────────────────────────────────────┤
│  Client sends query as POST body to /graphql             │
│                ↓                                         │
│  1. PARSE    — tokenize query string → AST               │
│  2. VALIDATE — check fields exist in schema, types valid │
│  3. EXECUTE  — traverse AST, call resolver per field     │
│                ↓            ↓                            │
│            Resolver A    Resolver B  (parallel siblings) │
│                ↓            ↓                            │
│           DB query       Cache hit                       │
│                ↓            ↓                            │
│  4. ASSEMBLE — merge results into response shape         │
│                ↓                                         │
│  Return JSON matching query structure                    │
└──────────────────────────────────────────────────────────┘

Schema:
type Query {
  user(id: ID!): User
}
type User {
  name: String!
  posts: [Post!]!
}
type Post {
  title: String!
}

Resolver tree for: user(id: "42") { name, posts { title } }
  → resolver: Query.user(id: "42")    → fetch User row
  → resolver: User.name               → return user.name
  → resolver: User.posts              → fetch posts WHERE user_id=42
  → resolver: Post.title              → return post.title (per post)
```

**N+1 Problem in Resolver Execution:**
For a list of 100 users each with posts — the default execution calls
`User.posts` resolver 100 times → 100 DB queries. Fix: DataLoader batches
all 100 `userId` lookups into one `WHERE user_id IN (...)` query.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Event                                                 │
│       ↓                                                     │
│  Client builds GraphQL query string                        │
│       ↓                                                     │
│  POST /graphql  {query: "...", variables: {...}}            │
│       ↓                                                     │
│  HTTP Middleware (auth, rate-limit headers)                 │
│       ↓                                                     │
│  GraphQL Engine: parse → validate → build execution plan   │
│       ↓                                                     │
│  Resolver execution (field by field, possibly parallel)    │
│       ↓          ↓            ↓                            │
│  DB query    Cache read   Microservice call                │
│       ↓          ↓            ↓                            │
│  Resolver results assembled into response object           │
│       ↓                                                     │
│  Return {data: {...}, errors: [...] or null}               │
│       ↓                                                     │
│  Client renders exactly the fields it requested            │
└─────────────────────────────────────────────────────────────┘
```

**What about errors?**
GraphQL always returns HTTP 200. Errors go in the `errors` array.
This surprises engineers from REST backgrounds — you must check
`response.errors`, not just the status code.

---

### 💻 Code Example

```graphql
# Schema Definition Language (SDL)
type Query {
  user(id: ID!): User
  users(limit: Int = 10): [User!]!
}

type Mutation {
  createPost(input: CreatePostInput!): Post!
  deletePost(id: ID!): Boolean!
}

type User {
  id: ID!
  name: String!
  email: String!
  posts(last: Int): [Post!]!
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
  createdAt: String!
}

input CreatePostInput {
  title: String!
  body: String!
  authorId: ID!
}
```

```graphql
# Client Query — fetch exactly what the dashboard needs
query DashboardQuery($userId: ID!) {
  user(id: $userId) {
    name
    posts(last: 5) {
      id
      title
      createdAt
    }
  }
}
```

```java
// Java resolver (Spring for GraphQL / Netflix DGS)
@QueryMapping
public User user(@Argument String id) {
    return userRepository.findById(id)
        .orElseThrow(() -> new GraphQLException("User not found: " + id));
}

@SchemaMapping(typeName = "User", field = "posts")
public List<Post> posts(User user,
                        @Argument Integer last) {
    return postRepository.findByAuthorId(
        user.getId(),
        PageRequest.of(0, last != null ? last : 10,
            Sort.by("createdAt").descending()));
}
```

```java
// GraphQL response always HTTP 200 — must check errors field
// Client-side handling:
GraphQLResponse response = httpClient.post(query);
if (response.getErrors() != null && !response.getErrors().isEmpty()) {
    // Handle partial data + errors
    log.warn("GraphQL errors: {}", response.getErrors());
}
User user = response.getData("user", User.class);
```

---

### ⚖️ Comparison Table

| Feature              | REST                     | GraphQL            | gRPC                 |
| -------------------- | ------------------------ | ------------------ | -------------------- |
| **Endpoint**         | Many (per resource)      | Single `/graphql`  | Generated per method |
| **Data shape**       | Fixed by server          | Defined by client  | Fixed (protobuf)     |
| **Over-fetching**    | Common problem           | Solved             | Not a problem        |
| **Under-fetching**   | Common (N+1 round trips) | Solved             | Not a problem        |
| **HTTP caching**     | Excellent (URL-based)    | Poor (POST body)   | N/A (HTTP/2)         |
| **Schema**           | OpenAPI (optional)       | Built-in, required | .proto (required)    |
| **Real-time**        | SSE / polling            | Subscriptions      | Server streaming     |
| **Tooling maturity** | Excellent                | Very good          | Good                 |
| **Best for**         | Simple CRUD, public APIs | Complex data, BFF  | Internal services    |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| GraphQL replaces REST                | They solve different problems; many systems use both — REST for simple endpoints, GraphQL for complex data fetching |
| GraphQL is only for Facebook-scale   | GraphQL is valuable even for small teams: self-documenting schema removes guesswork                                 |
| GraphQL always returns HTTP 200      | Yes, even on validation errors — clients must check the `errors` field not just status code                         |
| GraphQL is slower than REST          | Depends entirely on resolver implementation; can be faster (fewer round trips) or slower (N+1 problems)             |
| GraphQL means no more API versioning | Field additions are non-breaking; field removals still require deprecation; schema evolution still needs planning   |

---

### 🚨 Failure Modes & Diagnosis

**N+1 Query Explosion**

Symptom:
A query requesting 50 users with their posts fires 51 database queries
(1 for users + 50 for posts). Dashboard loads in 8 seconds.

Root Cause:
`User.posts` resolver executes once per User in the list without batching.

Diagnostic Command / Tool:

```
# Enable Spring Boot SQL logging:
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG

# Or in DataDog/Grafana: query span count per GraphQL request
# Should see n=1 for a batched query, not n=50
```

Fix:
Implement DataLoader pattern — batch all userId lookups into one
`WHERE user_id IN (...)` query. Spring for GraphQL has built-in
`@BatchMapping` annotation for this.

Prevention:
Every list resolver that fetches related data must use DataLoader/batching.
Set up query count assertions in integration tests.

---

**Deeply Nested Query — Denial of Service**

Symptom:
A malicious (or buggy) client sends:
`{ user { friends { friends { friends { friends { name } } } } } }`
causing exponential resolver calls, maxing out the database.

Root Cause:
GraphQL allows arbitrary query depth by default. No depth limit configured.

Diagnostic Command / Tool:

```
# Add query depth limit to GraphQL config:
# Spring for GraphQL / Netflix DGS:
InstrumentationMaxQueryDepth depth = 10;
# Also add query complexity limit
```

Fix:
Add `maxQueryDepth` and `maxQueryComplexity` limits in GraphQL engine config.
Use persisted queries in production to allowlist known-safe queries.

Prevention:
Always configure depth limiting and query complexity scoring in production.
Consider persisted queries for public-facing APIs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `REST` — GraphQL was designed as an alternative to REST; understanding REST's limitations motivates GraphQL's design
- `HTTP` — GraphQL runs over HTTP; must understand POST, headers, status codes
- `JSON` — GraphQL responses are JSON; query variables use JSON syntax

**Builds On This (learn these next):**

- `GraphQL Schema` — how to define the type system that powers a GraphQL API
- `GraphQL Resolvers` — the functions that actually fetch data for each field
- `GraphQL N+1 Problem` — the performance trap that hits every GraphQL beginner

**Alternatives / Comparisons:**

- `REST` — the incumbent; simpler for CRUD APIs, better HTTP caching
- `gRPC` — better for internal service-to-service communication; needs no query flexibility
- `SOAP` — legacy XML-based protocol; more rigid, enterprise-focused

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Query language + runtime for APIs:         │
│              │ client specifies exactly what data needed  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ REST over-fetching, under-fetching,       │
│ SOLVES       │ N+1 round trips, endpoint proliferation   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Single endpoint + typed schema + client-  │
│              │ driven queries = no more API versioning   │
│              │ for most changes                          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex data needs, multiple client types,│
│              │ BFF pattern, rapid UI iteration           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD API, public with HTTP caching,│
│              │ team unfamiliar with N+1 problem          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Developer flexibility vs increased        │
│              │ server complexity + N+1 risk              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask for exactly what you need"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GraphQL Schema → GraphQL Resolvers        │
│              │ → GraphQL N+1 Problem → DataLoader        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates a complex dashboard from 12 REST endpoints to GraphQL.
Initial performance is worse — P95 latency increased from 400ms to 1.2s despite
the client making only 1 request instead of 12. Walk through every layer of the
system (network, GraphQL engine, resolvers, DB) and identify all possible sources
of this regression. Which is most likely and why?

**Q2.** GraphQL's single endpoint and POST-body queries mean traditional HTTP
caching (CDN, Varnish, browser cache) doesn't work. Design a complete caching
strategy for a high-traffic GraphQL API that serves both authenticated users and
anonymous visitors, handling both query responses and field-level invalidation.
