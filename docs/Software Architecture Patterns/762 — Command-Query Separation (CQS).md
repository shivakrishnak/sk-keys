---
layout: default
title: "Command-Query Separation (CQS)"
parent: "Software Architecture Patterns"
nav_order: 762
permalink: /clean-code/command-query-separation/
number: "762"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Encapsulation, Single Responsibility Principle, Immutability
used_by: CQRS, Testing, Functional Programming, REST API Design, Debugging
tags: #architecture, #pattern, #intermediate, #testing
---

# 762 — Command-Query Separation (CQS)

`#architecture` `#pattern` `#intermediate` `#testing`

⚡ TL;DR — Every method should either change state (command) or return a value (query), but never both — making code predictable and side-effect-free to read.

| #762 | category: Software Architecture Patterns
|:---|:---|:---|
| **Depends on:** | Encapsulation, Single Responsibility Principle, Immutability | |
| **Used by:** | CQRS, Testing, Functional Programming, REST API Design, Debugging | |

---

### 📘 Textbook Definition

**Command-Query Separation (CQS)** is a design principle coined by Bertrand Meyer stating that every method in a system should be classified as either a **command** (a procedure that changes state and returns `void`) or a **query** (a function that returns a value and has no side effects). A method must never do both. CQS transforms objects into predictable, function-like interfaces: calling a query is always safe (reads don't mutate), and calling a command signals clearly that state will change. CQRS (Command-Query Responsibility Segregation) extends CQS to the architectural level, separating read and write models.

---

### 🟢 Simple Definition (Easy)

A method should either *do something* (command — no return value) or *answer something* (query — returns a value, changes nothing). Never both. Asking a question should never change the answer.

---

### 🔵 Simple Definition (Elaborated)

When a method both returns a value AND changes state, you create hidden surprises. The classic example: `stack.pop()` returns the top element AND removes it. Call it twice expecting the same result? You get different answers — and the stack changes silently. With CQS: `stack.peek()` queries (no mutation), `stack.pop()` commands (void, removes). Now reading is safe to do multiple times, and mutation is explicit. Tests become simpler: verify commands produced the right state; verify queries returned the right value — never entangle both in one call.

---

### 🔩 First Principles Explanation

**The problem — hidden side effects through reads:**

```java
// VIOLATES CQS — query that mutates
public User getNextUser() {
  User next = queue.poll(); // reads AND removes!
  return next;
}
// Calling twice:
User u1 = getNextUser(); // gets and removes Alice
User u2 = getNextUser(); // gets and removes Bob (surprise!)

// How many users are left?
// Impossible to count without CONSUMING the queue
```

**The problem cascade:**

```
┌─────────────────────────────────────────────────────┐
│  WHEN READS HAVE SIDE EFFECTS                       │
│                                                     │
│  ❌ Reading state in a loop → mutation each time    │
│  ❌ Asserting in tests → changes state under test   │
│  ❌ Debugging by inspecting → changes state!        │
│  ❌ Caching read results → stale if read mutated    │
│  ❌ Two callers read same thing → race condition    │
└─────────────────────────────────────────────────────┘
```

**CQS solution — separate the concerns:**

```java
// COMMAND: changes state, void return
void enqueue(User user) {
  queue.add(user);
}

void dequeue() {        // announces: "I change state"
  queue.poll();
}

// QUERY: reads state, no mutation
User peek() {           // announces: "safe to call freely"
  return queue.peek();
}

int size() { return queue.size(); }
boolean isEmpty() { return queue.isEmpty(); }
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT CQS:**

```
Without CQS:

  Heisenbug: reading for diagnostics changes behaviour
    System.out.println(user.getAndIncrementVisitCount());
    // Debugging added a side effect!

  Test fragility:
    assertEquals("Alice", repo.findAndMarkViewed(id).getName());
    // Test assertion marks record as viewed
    // Run test twice → different DB state

  Race condition:
    Thread A: user = session.getAndExpireToken()
    Thread B: user = session.getAndExpireToken()
    → both get a user → both expire the token
    → double processing

  Caching failure:
    Cache: result = expensiveQuery.fetch()
    // fetch() also deletes expired records
    // Caching it → expired records never deleted
```

**WITH CQS:**

```
→ Queries are safe to call freely (memoize, retry, log)
→ Commands announced clearly → side effects expected
→ Tests: commands verified by state; queries by value
→ Concurrency: queries can run in parallel safely
→ Caching: only cache pure queries
→ REST: GET methods safe, never mutate (HTTP spec)
```

---

### 🧠 Mental Model / Analogy

> CQS is the difference between **reading a book** and **tearing out pages**. A query is reading — you can read the same page 1000 times, it's always there, unchanged. A command is tearing out — you signal clearly "I'm going to change this." The violation: a library that charges you each time you read a page (reading is supposed to be free but has a hidden cost). In Meyer's terms: "Asking a question should not change the answer."

"Reading the book" = query — pure, safe, repeatable
"Tearing out pages" = command — mutation, announced
"Library charging per read" = query with side effect — CQS violation
"Meyer's principle" = asking a question should not change the answer

---

### ⚙️ How It Works (Mechanism)

**Classifying methods:**

```
COMMAND:           QUERY:
  void addItem()     Item getItem(int i)
  void save()        List<Item> getAll()
  void delete(id)    boolean isEmpty()
  void send()        int count()
  void clear()       Optional<User> findByEmail()

VIOLATION (both):
  User pop()           ← removes AND returns
  int getAndIncrement()← reads AND increments
  User findOrCreate()  ← reads OR creates
  boolean setIfAbsent()← queries AND mutates
```

**Handling the "pop" problem:**

The classic concern: "I need to both get and remove. Doesn't CQS make this impossible?"

Answer: separate the operations. The caller is responsible for orchestrating:

```java
// CQS-compliant stack:
public interface Stack<T> {
  void push(T item);        // command
  void pop();               // command — removes top
  T peek();                 // query  — reads top
  boolean isEmpty();        // query
}

// Caller orchestrates:
if (!stack.isEmpty()) {
  T item = stack.peek();   // query — safe to re-read
  stack.pop();             // explicit mutation
  process(item);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Single Responsibility Principle
(one reason to change)
        ↓
  CQS  ← you are here
  (commands change state, queries read state — never both)
        ↓
  Architectural extension:
  CQRS — separate read/write MODELS and databases
  (Axon Framework, EventSourcing patterns)
        ↓
  Enables:
  ├── Safe caching of queries
  ├── Parallel read scaling
  ├── Clear testing strategy (cmd=state, qry=value)
  └── REST HTTP semantics (GET=safe, POST=command)
```

---

### 💻 Code Example

**Example 1 — Refactoring a CQS violation:**

```java
// BAD: CQS violation — reads AND mutates
@Service
public class TokenService {
  public String getAndInvalidateToken(String userId) {
    String token = tokenStore.get(userId);
    tokenStore.remove(userId); // hidden side effect!
    return token;
  }
}
// Cache this call? → tokens never invalidated
// Call twice in error? → second call returns null silently

// GOOD: separate concerns
@Service
public class TokenService {
  // QUERY — safe to call, no mutation
  public Optional<String> getToken(String userId) {
    return Optional.ofNullable(tokenStore.get(userId));
  }

  // COMMAND — explicit mutation
  public void invalidateToken(String userId) {
    tokenStore.remove(userId);
  }
}

// Caller is explicit and safe:
Optional<String> token = tokenService.getToken(userId);
token.ifPresent(t -> {
  process(t);
  tokenService.invalidateToken(userId); // explicit
});
```

**Example 2 — REST API alignment with CQS:**

```java
// HTTP naturally enforces CQS:
// QUERY  → GET /users/{id}      (no side effects)
// COMMAND→ POST /users          (creates user, returns 201)
// COMMAND→ DELETE /users/{id}   (removes, returns 204)
// COMMAND→ PUT /users/{id}      (updates, returns 200 or 204)

// Common violations to avoid:
// BAD: GET /users/{id}/activate → mutates via a GET
// BAD: POST /users/search       → fine if truly a command
//       but semantically odd for pure reads
// GOOD: POST /users/search when query params are complex
//       is acceptable — but mark it idempotent
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQS means void commands can never return error codes | Commands can throw exceptions. They cannot return domain data. An ID of the newly created entity is a borderline case — CQRS solves this with separate events |
| CQS is the same as CQRS | CQS is a method-level principle; CQRS is an architectural pattern separating read/write models across entire system layers |
| findOrCreate() is fine — it's pragmatic | findOrCreate() violates CQS and causes race conditions under concurrency: two threads call it simultaneously, both find nothing, both create — duplicates |
| HTTP GET requests are automatically queries | GET requests are supposed to be safe (RFC 7231), but nothing in HTTP prevents mutation. CQS is a design discipline, not an HTTP constraint |

---

### 🔥 Pitfalls in Production

**1. findOrCreate — race condition and CQS violation**

```java
// BAD: violates CQS + concurrency unsafe
public User findOrCreateUser(String email) {
  User u = repo.findByEmail(email);
  if (u == null) {
    u = new User(email);
    repo.save(u);       // mutates if not found
  }
  return u;             // reads AND maybe writes
}
// Two concurrent calls → both find null → two Users created

// GOOD: command-side handles creation,
// handle uniqueness at DB level
CREATE UNIQUE INDEX idx_user_email ON users(email);
-- Concurrent inserts: one wins, one gets constraint error
-- Retry logic handles the loser → idempotent
```

**2. Lazy initialisation hiding mutation in getter**

```java
// BAD: getter with side effect — CQS violation
public List<Permission> getPermissions() {
  if (this.permissions == null) {
    this.permissions = permissionRepo.load(userId);
    // MUTATION inside a getter — invisible to caller
  }
  return this.permissions;
}
// Not thread-safe; mutates on first read; untestable cleanly

// GOOD: initialise eagerly or use explicit init command
public void loadPermissions() {        // command
  this.permissions = permissionRepo.load(userId);
}
public List<Permission> getPermissions() { // query
  return List.copyOf(permissions);     // pure read
}
```

---

### 🔗 Related Keywords

- `CQRS` — architectural extension of CQS: separate read and write models at the application layer
- `Single Responsibility Principle` — CQS is SRP applied at the method level: one job per method
- `Immutability` — queries are naturally pure when the object is immutable
- `REST API Design` — HTTP GET = query (safe), POST/PUT/DELETE = commands
- `Testing` — CQS makes test strategies clearer: test commands → assert state; test queries → assert return value
- `Functional Programming` — pure functions are the functional equivalent of CQS queries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Commands mutate (void), Queries read      │
│              │ (return value) — never both in same method│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All service methods, repositories, domain │
│              │ objects, REST endpoints — always          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — CQS is always applicable; "pop()"  │
│              │ is the concession: separate into two calls│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Asking a question should never           │
│              │  change the answer." — Bertrand Meyer     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Event Sourcing → Idempotency       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Iterator.next()` in Java is a canonical CQS violation: it both returns the next element (query) and advances the cursor (command). Yet Java chose this design deliberately and it's considered idiomatic. Explain the engineering trade-off that justified this CQS violation — specifically, what the alternative `current()` + `advance()` split would require callers to do differently — and describe the specific concurrency scenario where `Iterator.next()` being atomic (both-in-one) is actually *safer* than two separate calls.

**Q2.** In an event-sourced system, the write side (command) publishes events that the read side (query) processes to build projections. This is CQRS at the architecture level. But there is a fundamental consistency challenge: after a user submits a command, they immediately try to read the result and the projection hasn't been updated yet (eventual consistency lag). Describe the three patterns used to handle this UX problem — including their trade-offs — and explain which HTTP response code and headers are appropriate to signal this condition to API consumers.

