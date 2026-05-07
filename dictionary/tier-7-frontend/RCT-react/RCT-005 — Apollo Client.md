---
layout: default
title: "Apollo Client"
parent: "React"
nav_order: 5
permalink: /react/apollo-client/
number: "RCT-005"
category: React
difficulty: ★★★
depends_on: GraphQL with React, React, GraphQL
used_by: Apollo Federation, React
related: Apollo Federation, React Query, SWR
tags:
  - react
  - frontend
  - api
  - advanced
---

# RCT-005 — Apollo Client

⚡ **TL;DR —** Apollo Client is a GraphQL state layer for React that normalizes fetched data into a shared cache, powering automatic UI updates.

| | |
|---|---|
| **Depends on** | GraphQL with React, React, GraphQL |
| **Used by** | Apollo Federation, React |
| **Related** | Apollo Federation, React Query, SWR |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Components fire independent REST calls, duplicating data and diverging on stale state.

**THE BREAKING POINT:** With GraphQL, the same entity appears across dozens of queries — manual caching duplicates entities and lets them drift out of sync.

**THE INVENTION MOMENT:** Apollo Client normalizes every entity by `__typename + id`, making every component that uses `User:42` share one live copy.

---

### 📘 Textbook Definition

Apollo Client is a GraphQL client library for React providing `useQuery`, `useMutation`, and `useSubscription` hooks backed by a normalized `InMemoryCache`. It acts as both a network layer and a client-side state manager for server data.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Apollo Client = GraphQL hooks + normalized cache + automatic re-renders.

> Like a smart bookshelf: every entity filed by ID; any component requesting the same item reads one shared copy.

**One insight:** When a mutation updates `User:42`, every `useQuery` referencing that user re-renders automatically — no manual invalidation needed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. GraphQL responses normalize by `__typename:id`
2. `InMemoryCache` is the single source of truth
3. UI derives reactively from cache state

**DERIVED DESIGN:** `useQuery` checks cache before network. Mutations write to cache; subscribers re-render automatically.

**THE TRADE-OFFS:**
**Gain:** Automatic cache coherence across all components.
**Cost:** Complex cache configuration; incorrect fetch policies cause stale or redundant fetches.

---

### 🧪 Thought Experiment

**SETUP:** Two components display the same `User { id name }`.

**WITHOUT Apollo Client:** Both fire separate requests; one update leaves them out of sync.

**WITH Apollo Client:** Both subscribe to `User:42` in `InMemoryCache`. One mutation updates both simultaneously.

**THE INSIGHT:** The cache is a reactive store, not a result bag.

---

### 🧠 Mental Model / Analogy

> Apollo Client is a normalized relational database in the browser — entities live in one place; queries are live views over them.

- Query response → rows upserted into cache
- `useQuery` → a live view
- `useMutation` → a write that triggers view re-renders
- Fetch policy → row freshness rules

Where this analogy breaks down: cache invalidation is explicit and manual, not transactional.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A library that fetches GraphQL data and keeps it in sync across your app.

**Level 2:** Wrap your app in `<ApolloProvider client={client}>`. Call `useQuery(GET_USER, { variables: { id } })` in any component.

**Level 3:** Responses normalize into `InMemoryCache` keyed by `__typename:id`. Writes trigger re-renders of all subscribed queries referencing modified keys.

**Level 4:** URL-based caching fails GraphQL because the same entity spans many queries. Normalization is the only correct data-layer solution at scale.

---

### ⚙️ How It Works (Mechanism)

1. `useQuery` checks `InMemoryCache` first (based on fetch policy)
2. Cache miss → request sent via `ApolloLink` chain to server
3. Response normalized: `{ 'User:42': { id, name } }`
4. All queries referencing `User:42` trigger re-render
5. `useMutation` writes optimistic value first → server response reconciles

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
useQuery → InMemoryCache
  HIT  → render data              ← YOU ARE HERE
  MISS → ApolloLink → GraphQL server
       ← response → normalize → cache → render
```
**FAILURE PATH:** Network error → `error` state returned; cache untouched; `errorPolicy` controls propagation.

**WHAT CHANGES AT SCALE:** Pagination via `fetchMore`, field-level `TypePolicies`, and cache eviction needed for large datasets.

---

### 💻 Code Example

```jsx
// BAD — manual fetch, no shared cache
useEffect(() => fetch('/graphql')
  .then(r => r.json()).then(setUser), []);

// GOOD — Apollo normalized cache
const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) { id name email }
  }
`;
function UserCard({ id }) {
  const { data, loading } = useQuery(GET_USER, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
  return loading ? <Spinner /> : <div>{data.user.name}</div>;
}
```

---

### ⚖️ Comparison Table

| | Apollo Client | React Query | SWR |
|---|---|---|---|
| Protocol | GraphQL | Any | Any |
| Cache model | Normalized | Request-key | Request-key |
| Optimistic UI | Built-in | Manual | Manual |
| Subscriptions | Built-in | No | No |
| Bundle size | ~32 KB | ~13 KB | ~4 KB |

---

### ⚠️ Common Misconceptions

| Myth | Reality |
|---|---|
| Replaces Redux | Apollo = server state; Redux = UI/app state |
| `cache-first` is always safe | Stale risk; use `cache-and-network` for live data |
| `refetchQueries` is efficient | Re-runs full queries; prefer `cache.modify` |
| Subscriptions are free | WebSockets have real server and infra cost |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale UI after mutation**
**Symptom:** Data unchanged in UI after a write operation.
**Root Cause:** Mutation does not update the cache.
**Diagnostic:** `cache.readQuery({ query: GET_USER })` in browser console.
**Fix:** Add `update(cache, { data })` callback to `useMutation`.
**Prevention:** Plan the cache update strategy alongside every mutation.

**2. Memory growth**
**Symptom:** Browser RAM climbs continuously across navigation.
**Root Cause:** Cache entries never evicted.
**Fix:** Configure `typePolicies` with merge functions; call `cache.gc()` to collect unreachable references.

**3. N+1 queries**
**Symptom:** Hundreds of identical operations logged for a list render.
**Root Cause:** Each list item triggers its own nested query.
**Fix:** Use fragments for batching; add `DataLoader` on the server.

---

### 🔗 Related Keywords

**Prerequisites:** GraphQL with React, React, GraphQL
**Builds On This:** Apollo Federation, optimistic UI patterns
**Alternatives / Comparisons:** React Query, SWR, URQL

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ GraphQL client + normalized cache  │
│ PROBLEM      │ Duplicate fetches, cache drift     │
│ KEY INSIGHT  │ Entities keyed by __typename:id    │
│ USE WHEN     │ GraphQL API with shared entities   │
│ AVOID WHEN   │ REST-only or simple fetch needs    │
│ TRADE-OFF    │ Cache power vs. config complexity  │
│ ONE-LINER    │ useQuery + InMemoryCache = state   │
│ NEXT EXPLORE │ Apollo Federation, React Query     │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** If 50 components use `useQuery` for overlapping entities, how does Apollo's normalization prevent network redundancy — and what could still cause duplicate requests despite the cache?
2. **(Design Trade-off)** When would `network-only` fetch policy be preferable to `cache-first`, and what UX cost does that introduce for the user?
3. **(First Principles)** What happens when a GraphQL type has no `id` field? How must `InMemoryCache` be configured to handle it, and what breaks if it isn't?
