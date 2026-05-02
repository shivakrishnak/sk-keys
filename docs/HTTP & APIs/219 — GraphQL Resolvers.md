---
layout: default
title: "GraphQL Resolvers"
parent: "HTTP & APIs"
nav_order: 219
permalink: /http-apis/graphql-resolvers/
number: "0219"
category: HTTP & APIs
difficulty: ★★☆
depends_on: GraphQL, GraphQL Schema, Functions / Closures
used_by: GraphQL N+1 Problem, DataLoader, GraphQL Subscriptions
related: GraphQL Schema, REST Controller, Repository Pattern
tags:
  - api
  - graphql
  - resolvers
  - intermediate
---

# 219 — GraphQL Resolvers

⚡ TL;DR — A GraphQL resolver is a function that fetches the data for a single field in the schema; the GraphQL runtime calls the correct resolver for each field selected in a query and assembles the results into the response.

| #219 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | GraphQL, GraphQL Schema, Functions / Closures | |
| **Used by:** | GraphQL N+1 Problem, DataLoader, GraphQL Subscriptions | |
| **Related:** | GraphQL Schema, REST Controller, Repository Pattern | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A REST controller returns a fixed object. The endpoint defines what gets
fetched and returned — every caller gets the same shape. But in GraphQL,
different clients request different fields of the same type. If a single
controller fetched every possible field for every request, you'd be back
to REST's over-fetching problem. The engine needs a way to fetch _only
the requested fields_, each potentially from a different source.

**THE BREAKING POINT:**
A `User` type has fields: `name` (from DB), `profilePicture` (from S3),
`subscriptionStatus` (from Stripe API), and `lastLoginAt` (from Redis).
A monolithic fetch would hit all four sources for every query — even
if a query only asked for `name`. Without per-field fetch units, GraphQL
collapses back into the same problem as REST.

**THE INVENTION MOMENT:**
Resolvers solve this by decomposing data fetching to the field level.
Each field declares its own resolver — "when someone asks for User.name,
call this function." The GraphQL runtime calls _only the resolvers for
the fields the client actually requested_. A query asking for just `name`
calls only the name resolver (a property read) and skips the expensive
`subscriptionStatus` Stripe call entirely.

---

### 📘 Textbook Definition

A **resolver** in GraphQL is a function responsible for returning the data
for a specific field in the schema. Every field in a GraphQL schema has a
corresponding resolver. A resolver receives four arguments:

1. `parent` (or `root/source`) — the resolved value of the parent object
2. `args` — the arguments passed to the field in the query
3. `context` — shared request state (auth info, DB connection, DataLoader instances)
4. `info` — execution metadata (field name, return type, AST path)

If a resolver is not explicitly defined, the default resolver reads the
property with the same name from the parent object. Resolvers can return
plain values, Promises, or Observables (for subscriptions).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Each field in the schema has a resolver function — "who fetches this data" — and GraphQL calls the right ones for each query.

**One analogy:**

> Imagine a hotel concierge desk (GraphQL runtime). Guests (queries) ask for
> various services: taxi, room service, wake-up call. Each service (field)
> has a specialist (resolver): the transportation desk, room service kitchen,
> front desk. The concierge routes each request to the right specialist — only
> calling the ones the guest actually asked for. The concierge doesn't know how
> each specialist works; they just know who handles what.

**One insight:**
The resolver tree mirrors the query tree. A query nested 3 levels deep
(user → posts → comments) creates a 3-level resolver call chain where each
level's resolver receives the accumulated `parent` context from the level
above. This recursive parent-child relationship is how deeply nested queries
work — and why N+1 problems emerge naturally from list resolvers.

---

### 🔩 First Principles Explanation

**RESOLVER FUNCTION SIGNATURE:**

```
(parent, args, context, info) → value | Promise<value> | Observable<value>
```

- `parent`: resolved value of the containing type instance
- `args`: query arguments for this field `{ id: "42", limit: 10 }`
- `context`: shared across ALL resolvers in a single request — auth, DB, DataLoaders
- `info`: rarely needed — query AST, selected fields, return type

**RESOLVER CHAIN MECHANICS:**

```
Query:  { user(id: "1") { name, posts { title } } }

1. Query.user resolver called: (null, {id:"1"}, ctx, info)
   → returns: User object {id:"1", name:"Alice", ...}

2. User.name resolver called: ({id:"1",name:"Alice",...}, {}, ctx, info)
   → default resolver: returns parent.name = "Alice"

3. User.posts resolver called: ({id:"1",...}, {}, ctx, info)
   → custom resolver: returns [Post{id:"10", title:"Hello"}, Post{id:"11",...}]

4. For EACH Post in the list:
   Post.title resolver called: ({id:"10", title:"Hello",...}, {}, ctx, info)
   → default resolver: returns parent.title = "Hello"
   Post.title resolver called: ({id:"11", title:"World",...}, {}, ctx, info)
   → default resolver: returns parent.title = "World"
```

**WHY DEFAULT RESOLVER EXISTS:**
If every field needed an explicit resolver, schema wiring would be
enormous boilerplate. The default resolver eliminates ~80% of resolver
code by reading the same-named property from the parent object.

**THE TRADE-OFFS:**

- Gain: field-level fetch isolation → only fetch what's requested.
- Cost: per-field execution → N+1 query problem for lists.
- Gain: resolver tree mirrors query tree → predictable execution.
- Cost: complex resolver debugging — errors pinpoint to specific field path.

---

### 🧪 Thought Experiment

**SETUP:**
You have a query: `{ users { name, posts { title } } }`
The `users` resolver returns 50 users. The `posts` resolver fetches posts by
`userId`. The `title` resolver is the default (property read).

**RESOLVER EXECUTION COUNT:**

1. `Query.users` called once → returns 50 user objects
2. `User.name` called 50 times (default resolver, trivial)
3. `User.posts` called 50 times → `SELECT * FROM posts WHERE user_id = ?`
   → 50 separate database queries!
4. `Post.title` called N times (default resolver, trivial)
   Total DB queries: **51** (1 for users + 50 for posts)

**WITHOUT BATCHING:** 51 DB round trips.

**WITH DATALOADER:**
`User.posts` schedules a load: `dataLoader.load(userId)`.
After all 50 `User.posts` resolvers have scheduled loads in the same tick,
DataLoader batches them: `SELECT * FROM posts WHERE user_id IN (1,2,...,50)`
Total DB queries: **2** (1 for users + 1 batched for all posts).

**THE INSIGHT:**
The N+1 problem is a direct consequence of the resolver-per-field design.
DataLoader is the standard solution: collect all loads from a tick, batch,
then deliver results. Understanding resolver execution order is prerequisite
to understanding when DataLoader solves N+1 and when it doesn't.

---

### 🧠 Mental Model / Analogy

> Think of resolvers as a tree of lazy evaluators. Each node in the query
> tree corresponds to a resolver. The runtime traverses the tree top-down,
> calling each resolver with the parent's resolved value. It's like a recursive
> `map` operation over a tree structure: each node transforms its parent's output
> into the next level's input. Sibling nodes (parallel fields on the same object)
> can execute concurrently. Child nodes must wait for their parent to resolve first.

- "Root resolver" → `Query.user` — entry point, no parent
- "Object resolver" → `User.posts` — parent is the User object
- "Scalar resolver" → `User.name` — default resolver, just reads property
- "List resolver" → `User.posts` — returns an array, causing per-item child resolution

**Where this breaks down:** Execution is controlled by the GraphQL engine, not
explicitly by your code. Some engines execute sibling fields serially (not in parallel)
by default for determinism. Check your engine's concurrency guarantees,
especially for mutations where order matters.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Every field in a GraphQL query has a "handler" function (resolver) that knows
how to get that specific piece of data. GraphQL calls the right handler for
each field you request. If you don't request a field, its handler is never called.

**Level 2 — How to use it (junior developer):**
In Java (Spring for GraphQL): annotate methods with `@QueryMapping` for root
Query resolvers, `@SchemaMapping(typeName="User", field="posts")` for type
field resolvers, `@MutationMapping` for mutations. Method parameters annotated with
`@Argument` receive query arguments. Return types map to schema types — return
`Optional<T>` for nullable fields, `List<T>` for list fields.

**Level 3 — How it works (mid-level engineer):**
The runtime builds an execution plan from the query AST and schema. For each
field in the query, it finds the registered resolver. Root resolvers (Query._,
Mutation._) receive `null` as parent. Object field resolvers receive the already-
resolved parent object. The runtime handles async resolution: if a resolver returns
a `CompletableFuture`/`Promise`, it awaits resolution before passing the value
to child resolvers. Sibling fields on the same level can be resolved concurrently
(engine-dependent). The context object is injected into all resolvers — it's how
DataLoaders, auth info, and per-request DB connections are shared without
global state.

**Level 4 — Why it was designed this way (senior/staff):**
The resolver function signature `(parent, args, context, info)` is specified
in the GraphQL Reference Implementation (graphql-js). The `parent` parameter
enables type-safe chaining without global state — each resolver only knows about
its own field and its immediate parent. The `context` is a deliberate escape
hatch for per-request state (auth, DataLoaders, tracing) that would otherwise
require thread-locals or injection frameworks. The separation of `context` from
`parent` reflects a key design philosophy: resolver logic should be pure functions
over their inputs — the parent determines _what_ is being resolved, the context
provides _how_ (infra, auth). This makes resolvers unit-testable by injecting mock
contexts. The `info` field was an afterthought — it exposes the full AST path,
useful for query-level caching and field-level metrics, but accessing it couples
resolvers to execution internals.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│           RESOLVER EXECUTION ENGINE                          │
├──────────────────────────────────────────────────────────────┤
│  ParsedAST                                                   │
│    └─ Query                                                  │
│        └─ user(id:"1")   ←── Query.user resolver called     │
│            ├─ name       ←── User.name default resolver      │
│            └─ posts      ←── User.posts resolver called      │
│                ├─ title  ←── Post.title default resolver     │
│                └─ title  ─── (per post in list)             │
│                                                              │
│  Execution order:                                            │
│  1. Query.user(null, {id:"1"}, ctx, info)                   │
│     → User object  ──────────────────────┐                  │
│  2. User.name(userObj, {}, ctx, info)    │ parallel          │
│     → "Alice"                            │                  │
│  3. User.posts(userObj, {}, ctx, info)  ─┘                  │
│     → [Post, Post, Post]                                    │
│  4. Post.title(postObj, {}, ctx, info) × N  ← per post      │
│     → "Hello", "World", ...                                 │
└──────────────────────────────────────────────────────────────┘
```

**Context lifetime:**
Context is created once per request and passed to every resolver.
This is how DataLoader instances are scoped to a request — each
request gets fresh DataLoader instances (no state leak between requests).

---

### 🔄 The Complete Picture — End-to-End Flow

```
Client query → Parse+Validate → Execution starts
                                      ↓
                           Query.user resolver
                              fetch User from DB
                                      ↓ User object
                         ┌────────────┴────────────────┐
                   User.name                       User.posts
                 (default resolver)           (custom resolver)
                   return user.name          fetch posts for user
                         ↓                          ↓ [Post]
                       "Alice"               for each Post:
                                               Post.title
                                             (default resolver)
                                               return post.title
                                                     ↓ "Hello"

Assemble: {user: {name: "Alice", posts: [{title:"Hello"}]}}
Return JSON response
```

---

### 💻 Code Example

```java
// Spring for GraphQL — schema-first resolver wiring

// Schema:
// type Query { user(id: ID!): User }
// type User { id: ID!, name: String!, posts(last: Int): [Post!]! }
// type Post { id: ID!, title: String! }

@Controller
public class UserResolver {

    @Autowired private UserRepository userRepository;
    @Autowired private PostRepository postRepository;

    // Root resolver — Query.user
    // parent is implicitly null for root queries
    @QueryMapping
    public Optional<User> user(@Argument String id) {
        return userRepository.findById(id);
    }

    // Field resolver — User.posts
    // 'user' param is the resolved parent User object
    @SchemaMapping(typeName = "User", field = "posts")
    public List<Post> posts(User user,
                            @Argument Integer last) {
        int limit = (last != null) ? last : 10;
        return postRepository.findByAuthorIdOrderByCreatedAtDesc(
            user.getId(), PageRequest.of(0, limit));
    }
}

@Controller
public class PostMutationResolver {

    @Autowired private PostService postService;

    // Mutation resolver
    @MutationMapping
    public Post createPost(@Argument CreatePostInput input,
                           @ContextValue String currentUserId) {
        return postService.create(input, currentUserId);
    }
}
```

```java
// Context injection — sharing DataLoaders and auth across resolvers
// GraphQLContextContributor (Spring for GraphQL)
@Component
public class DataLoaderContextContributor
        implements GraphQlSourceBuilderCustomizer {

    @Autowired private PostDataLoader postDataLoader;

    @Override
    public void customize(GraphQlSource.SchemaResourceBuilder builder) {
        builder.configureRuntimeWiring(wiring ->
            wiring.dataLoader("postsForUser",
                DataLoaderFactory.newDataLoader(postDataLoader)));
    }
}

// DataLoader-based resolver avoids N+1
@SchemaMapping(typeName = "User", field = "posts")
public CompletableFuture<List<Post>> posts(
        User user,
        DataLoader<String, List<Post>> postsLoader) {
    // Schedules a batch load — NOT executed immediately
    // DataLoader collects all user IDs from this request tick,
    // then fires one: SELECT * FROM posts WHERE user_id IN (...)
    return postsLoader.load(user.getId());
}
```

```java
// Testing resolvers in isolation (unit test)
@Test
void user_resolver_returns_user_for_valid_id() {
    when(userRepository.findById("42"))
        .thenReturn(Optional.of(new User("42", "Alice")));

    Optional<User> result = resolver.user("42");

    assertThat(result).isPresent();
    assertThat(result.get().getName()).isEqualTo("Alice");
    // context and info parameters not needed — injected as null in test
}
```

---

### ⚖️ Comparison Table

| Concept              | GraphQL Resolver              | REST Controller   | Database Query     |
| -------------------- | ----------------------------- | ----------------- | ------------------ |
| **Granularity**      | Per field                     | Per endpoint      | Per query          |
| **Input**            | (parent, args, context, info) | HTTP request      | SQL/DSL            |
| **Called when**      | Field is in client query      | URL matches route | Explicitly invoked |
| **Return type**      | Value, Promise, Observable    | HTTP response     | ResultSet          |
| **Default behavior** | Read parent property          | None (404)        | N/A                |
| **Batching support** | DataLoader pattern            | N/A               | Set-based queries  |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                      |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| You must define a resolver for every field | Default resolver handles all scalar fields that match parent property names — only define custom resolvers when needed                       |
| Resolvers run sequentially                 | Sibling fields can run in parallel; only parent-child fields are sequential (parent must resolve first)                                      |
| The context is the HTTP request            | Context is request-scoped but you control what it contains — it should hold auth, DataLoaders, DB connections, not raw HTTP objects          |
| Mutations always run sequentially          | GraphQL spec requires root mutation fields to execute _serially_; nested mutation fields within one mutation are not guaranteed sequential   |
| Resolver errors fail the whole query       | GraphQL returns partial data + errors; a resolver throwing an exception only nulls that field (and propagates null upstream if non-nullable) |

---

### 🚨 Failure Modes & Diagnosis

**N+1 Resolver Cascade**

Symptom:
Query `{ users { posts { title } } }` causes 51 DB queries for a list of 50 users.
Dashboard load time is 3–8 seconds.

Root Cause:
`User.posts` field resolver is called once per user, each making a separate
SQL query instead of a batched IN query.

Diagnostic Command / Tool:

```
# Enable SQL query logging and count queries per GraphQL request:
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG

# In logs, count identical queries with different user_id parameters:
# SELECT * FROM posts WHERE user_id = 1
# SELECT * FROM posts WHERE user_id = 2
# ... (N queries = N+1 problem confirmed)
```

Fix:
Implement DataLoader for `User.posts` — batch all user IDs from a single
request tick into one `IN` query.

Prevention:
Every list resolver that fetches related data by parent ID must use DataLoader.
Add integration tests that assert query count per operation.

---

**Context State Leaking Between Requests**

Symptom:
User A sees User B's data in certain responses. Only reproducible under load.
Cache invalidation doesn't help.

Root Cause:
DataLoader instances created as application-scoped singletons (beans) instead
of request-scoped. DataLoader cache from request 1 leaks into request 2.

Diagnostic Command / Tool:

```java
// WRONG: DataLoader as singleton bean
@Bean
public DataLoader<String, User> userLoader() {
    return DataLoaderFactory.newDataLoader(...); // shared across requests!
}

// RIGHT: Create new DataLoader per request in context
@Bean
@RequestScope  // new instance per HTTP request
public DataLoader<String, User> userLoader() {
    return DataLoaderFactory.newDataLoader(...);
}
```

Fix:
Ensure DataLoader instances are request-scoped. In Spring for GraphQL,
register DataLoaders in `DataLoaderRegistrar` which is called per request.

Prevention:
All per-request state (DataLoaders, auth claims) must be request-scoped.
Test with concurrent requests using different users to detect cross-request leaks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `GraphQL` — must understand GraphQL fundamentals before resolver internals
- `GraphQL Schema` — resolvers implement the schema; must know schema types and fields
- `Functions / Closures` — resolvers are functions; closure over shared state is a common pattern

**Builds On This (learn these next):**

- `GraphQL N+1 Problem` — the direct performance consequence of per-field resolvers with list types
- `DataLoader` — the standard batching solution for resolver N+1 problems
- `GraphQL Subscriptions` — subscription resolvers use Observable/flux instead of Promise

**Alternatives / Comparisons:**

- `REST Controller` — monolithic approach where one method fetches everything for an endpoint
- `Repository Pattern` — resolvers typically delegate to repositories for data access

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Function that fetches data for one field  │
│              │ in the schema: (parent,args,ctx,info)→val │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Each field may come from different source │
│ SOLVES       │ (DB, cache, API) — resolvers isolate this │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Default resolver reads parent property — │
│              │ only write custom resolvers when needed   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building any GraphQL server — all fields  │
│              │ need resolvers (explicit or default)      │
├──────────────┼───────────────────────────────────────────┤
│ WATCH OUT    │ N+1 in list resolvers — use DataLoader    │
│              │ Context must be request-scoped            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Field isolation + lazy fetch vs N+1 risk  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each field's fetch function"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GraphQL N+1 Problem → DataLoader          │
│              │ → GraphQL Subscriptions                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A GraphQL resolver for `User.subscriptionStatus` calls an external Stripe
API. The query requests `{ users { name, subscriptionStatus } }` for a list of
1,000 users. Without DataLoader, this fires 1,000 Stripe API calls. With DataLoader,
you'd want to batch — but Stripe's API doesn't support bulk status fetches.
Design a caching and rate-limiting strategy for this resolver that prevents
1,000 Stripe calls while keeping subscription status reasonably fresh.

**Q2.** The `info` parameter in `(parent, args, context, info)` contains the full
query AST — you can inspect which fields were requested. Describe a case where
reading `info.getSelectionSet()` in a resolver is genuinely useful and would lead
to a measurable performance improvement. Then argue why this pattern should be used
sparingly.
