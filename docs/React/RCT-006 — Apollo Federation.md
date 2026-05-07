---
layout: default
title: "Apollo Federation"
parent: "React"
nav_order: 6
permalink: /react/apollo-federation/
number: "RCT-006"
category: React
difficulty: ★★★
depends_on: Apollo Client, GraphQL with React, Microservices
used_by: React, Microservices
related: Apollo Client, GraphQL Mesh, Schema Stitching
tags:
  - react
  - microservices
  - api
  - advanced
  - distributed
---

# RCT-006 — Apollo Federation

⚡ **TL;DR —** Apollo Federation composes multiple GraphQL subgraph schemas into one unified supergraph through a router, without schema stitching or a monolithic API server.

| | |
|---|---|
| **Depends on** | Apollo Client, GraphQL with React, Microservices |
| **Used by** | React, Microservices |
| **Related** | Apollo Client, GraphQL Mesh, Schema Stitching |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A single team owns the entire GraphQL schema, creating a bottleneck — every service must coordinate all schema changes centrally.

**THE BREAKING POINT:** At scale, each microservice team needs schema ownership. Schema stitching is manual, brittle, and leaks service internals into a shared layer.

**THE INVENTION MOMENT:** Apollo Federation gives each service its own subgraph. A router composes them automatically into a supergraph — teams deploy independently.

---

### 📘 Textbook Definition

Apollo Federation is a specification and toolset for distributed GraphQL architecture. Each **subgraph** owns a portion of the schema and is independently deployable. The **Apollo Router** composes subgraphs into a unified **supergraph** at runtime, resolving cross-service entity references via the `@key` directive and `__resolveReference`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Federation = compose multiple GraphQL services into one typed API automatically.

> Like a phonebook assembled from separate city directories — each city owns its pages; the combined book looks unified to readers.

**One insight:** The `@key` directive is a cross-service foreign key — it marks how one subgraph can look up an entity owned by another.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each subgraph is independently deployable
2. Entities are identified by `@key` fields that span subgraphs
3. The router owns query planning and result stitching

**DERIVED DESIGN:** `@key(fields: "id")` marks a type as an entity. Other subgraphs extend it by referencing the same key and implementing `__resolveReference`.

**THE TRADE-OFFS:**
**Gain:** Team autonomy; independent deployments; single unified client API.
**Cost:** Distributed query planning complexity; cross-service latency; router is the critical path.

---

### 🧪 Thought Experiment

**SETUP:** Users service owns `User`; Orders service owns `Order` with a `user: User` field.

**WITHOUT Federation:** Orders service must call the Users REST API and manually stitch user data, or import and coordinate schema changes across teams.

**WITH Federation:** Orders subgraph declares `extend type User @key(fields: "id")`. The router fetches `User` fields from Users subgraph automatically when a query needs them.

**THE INSIGHT:** Entities become cross-service foreign keys, resolved by the router — not by individual services.

---

### 🧠 Mental Model / Analogy

> Apollo Federation is like a database with foreign keys spanning multiple databases — the router is the query optimizer that knows where each table lives.

- Subgraph → a single autonomous database
- `@key` → the foreign key
- Router → the query planner
- `__resolveReference` → the JOIN implementation
- Supergraph SDL → the unified schema clients see

Where this analogy breaks down: there is no ACID guarantee across subgraphs — distributed consistency is the developer's responsibility.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Federation lets multiple teams own parts of a GraphQL API, combined into one endpoint for clients.

**Level 2:** Mark entity types with `@key`. Implement `__resolveReference`. Point Apollo Router at your subgraph URLs.

**Level 3:** The router builds a query plan, splitting one client query into parallel subgraph requests, then stitches results. Entity lookups use `_entities` queries on the owning subgraph.

**Level 4:** Federation solves GraphQL schema ownership at org scale — analogous to how microservices solved REST API ownership, but with typed composition guarantees enforced at build time.

---

### ⚙️ How It Works (Mechanism)

1. Each subgraph publishes its schema with `@key` annotations
2. `rover subgraph publish` pushes to the schema registry
3. Router downloads the composed supergraph SDL
4. Client query arrives → Router builds a query plan
5. Router fans out sub-requests to relevant subgraphs in parallel
6. Router stitches responses and returns unified result to client

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client → Apollo Router → query plan
  → Users subgraph  (User fields)    ← YOU ARE HERE
  → Orders subgraph (Order fields)
  ← stitch results ← return to client
```
**FAILURE PATH:** Subgraph unavailable → Router returns partial result or error based on field nullability and `@provides`.

**WHAT CHANGES AT SCALE:** Schema registry for governance; CI composition validation; Router request coalescing and caching.

---

### 💻 Code Example

```graphql
# Users subgraph
type User @key(fields: "id") {
  id: ID!
  name: String!
}

# Orders subgraph — extends the User entity
extend type User @key(fields: "id") {
  id: ID! @external
  orders: [Order!]!
}
type Order {
  id: ID!
  total: Float!
}
```

```js
// Orders subgraph resolvers
const resolvers = {
  User: {
    __resolveReference(ref) {
      // ref = { id: "42" }
      return { id: ref.id };
    },
    orders({ id }) {
      return getOrdersByUser(id);
    },
  },
};
```

---

### ⚖️ Comparison Table

| | Apollo Federation | Schema Stitching | GraphQL Mesh |
|---|---|---|---|
| Ownership model | Per-subgraph team | Centralized | Centralized |
| Type safety | Strong | Weak | Medium |
| Independent deploy | Yes | No | No |
| Cross-service joins | Via `@key` | Manual | Via transforms |
| Runtime complexity | High | Medium | High |

---

### ⚠️ Common Misconceptions

| Myth | Reality |
|---|---|
| Federation replaces microservices | It's a GraphQL layer on top of existing services |
| Subgraphs must use Apollo Server | Any Federation-spec-compliant server works |
| `@external` means no data in this service | It marks fields owned and resolved by another subgraph |
| One subgraph per team is required | Teams can share subgraphs if domain boundaries align |

---

### 🚨 Failure Modes & Diagnosis

**1. Entity resolution failure**
**Symptom:** `Cannot return null for non-nullable field User.orders`.
**Root Cause:** `__resolveReference` threw an exception or returned `null`.
**Diagnostic:** Check Router structured logs for subgraph request errors.
**Fix:** Add error handling in `__resolveReference`; return safe defaults.
**Prevention:** Contract tests on every `__resolveReference` implementation.

**2. Schema composition error**
**Symptom:** Router fails to start; supergraph SDL marked invalid.
**Root Cause:** Conflicting type definitions or missing `@key` across subgraphs.
**Fix:** Run `rover supergraph compose --config supergraph.yaml` locally to surface conflicts before deploy.

**3. N+1 entity resolution**
**Symptom:** Hundreds of `__resolveReference` calls for a list query.
**Root Cause:** Each entity in a list resolved with an individual lookup.
**Fix:** Batch `__resolveReference` using `DataLoader` per request context.

---

### 🔗 Related Keywords

**Prerequisites:** Apollo Client, GraphQL with React, Microservices
**Builds On This:** Schema registry governance, Apollo Router custom plugins
**Alternatives / Comparisons:** Schema Stitching, GraphQL Mesh, Hasura

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distributed GraphQL composition spec    │
│ PROBLEM      │ Schema ownership bottleneck at scale    │
│ KEY INSIGHT  │ @key = cross-service entity reference   │
│ USE WHEN     │ Multiple teams, microservices, GraphQL  │
│ AVOID WHEN   │ Single team or small GraphQL API        │
│ TRADE-OFF    │ Team autonomy vs. distributed overhead  │
│ ONE-LINER    │ Subgraphs + Router = unified supergraph │
│ NEXT EXPLORE │ Apollo Client, GraphQL Mesh             │
└────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** If a client query requires data from 5 subgraphs, how does the Router's query plan minimize round trips — and what topology still forces sequential subgraph requests?
2. **(Design Trade-off)** Why do some teams implementing Federation revert to schema stitching? What organizational or technical signal suggests Federation is premature for a given system?
3. **(First Principles)** The `@key` directive is a cross-service foreign key. What happens if one subgraph changes its `@key` field — and how should schema governance prevent cascading failures across dependent subgraphs?
