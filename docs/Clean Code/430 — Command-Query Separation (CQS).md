---
layout: default
title: "Command-Query Separation (CQS)"
parent: "Clean Code"
nav_order: 430
permalink: /clean-code/command-query-separation-cqs/
number: "430"
category: Clean Code
difficulty: ★★☆
depends_on: CQRS, API Design, Side Effects
used_by: CQRS, Functional Programming, Idempotency, Testing
tags: #cleancode #pattern #intermediate
---

# 430 — Command-Query Separation (CQS)

`#cleancode` `#pattern` `#intermediate`

⚡ TL;DR — Every method should either change state (command) OR return data (query) — never both at once.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #430         │ Category: Clean Code                 │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ CQRS, API Design, Side Effects                                    │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ CQRS, Functional Programming, Idempotency, Testing                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

Command-Query Separation (CQS) is a design principle by Bertrand Meyer stating that every method in a class should be either a **Command** (changes state, returns void) or a **Query** (returns data, produces no observable side effects). Mixing both makes behavior unpredictable and harder to reason about.

---

## 🟢 Simple Definition (Easy)

CQS says: **a method should either DO something or ANSWER something — never both**. If it returns a value, it shouldn't change the world. If it changes the world, it shouldn't return a value.

---

## 🔵 Simple Definition (Elaborated)

CQS makes code predictable. Queries can be called multiple times safely — they are side-effect free and idempotent. Commands always change state. When a method BOTH modifies state AND returns a value, callers cannot safely call it twice, cannot cache the result, and cannot reason about call order without understanding internals.

---

## 🔩 First Principles Explanation

**The core problem:**
`user = userRepository.findAndMarkAccessed(id)` — did it return the user? Did it increment a counter? Is it safe to call twice? The caller cannot know without reading the implementation.

**Bertrand Meyer's insight:**
> "Asking a question should not change the answer."

```
Command: void markAccessed(long id)          --> changes state, returns nothing
Query:   Optional<User> findById(long id)    --> returns data, no state change
```

---

## ❓ Why Does This Exist (Why Before What)

Without CQS, calling a "query" method has invisible side effects. Tests become order-dependent (calling a method twice changes the result). Caching is impossible (caching a "query" would block state changes). Concurrency reasoning breaks down.

---

## 🧠 Mental Model / Analogy

> Like asking a librarian for a book vs returning a book. "Where is book X?" (query — no change to library state). "Return this book" (command — changes library state). If asking "where is book X?" automatically checked it out to you, that would be surprising and dangerous.

---

## ⚙️ How It Works (Mechanism)

```
Classification:

  Query   --> returns a value, NO state change
              safe to call multiple times
              safe to cache
              safe to parallelize

  Command --> changes state (DB write, cache write, event publish)
              returns void (or throws exception)
              NOT safe to call multiple times without consequences

// VIOLATES CQS: does both
User pop() {
    User u = queue.first();
    queue.remove(u);   // side effect
    return u;          // also returns
}

// CQS-compliant split:
User peek()   { return queue.first(); }  // query - safe to repeat
void remove() { queue.removeFirst(); }   // command - explicit intent
```

---

## 🔄 How It Connects (Mini-Map)

```
[Query]  --> reads  --> [State]   (State unchanged after call)
[Command] --> writes --> [State]  (no return value; callers know it mutates)
```

---

## 💻 Code Example

```java
// VIOLATES CQS — method changes state AND returns data
class UserService {
    // Bad: increments login count AND returns the user
    User loginAndGet(String username) {
        User user = findByUsername(username);
        user.incrementLoginCount();          // side effect
        userRepository.save(user);           // side effect
        return user;                         // also returns data
    }
}

// CQS-COMPLIANT split
class UserService {
    // Command: changes state, returns nothing
    void recordLogin(String username) {
        User user = findByUsername(username)
            .orElseThrow(() -> new UserNotFoundException(username));
        user.incrementLoginCount();
        userRepository.save(user);
    }

    // Query: reads data only, no side effects — safe to call multiple times
    Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }
}

// Caller — intent is explicit
userService.recordLogin("alice");                          // command
User alice = userService.findByUsername("alice")           // query
                .orElseThrow();
```

---

## 🔁 Flow / Lifecycle

```
1. Look at each method: does it mutate state? Does it return data?
        ↓
2. If it does both --> CQS violation
        ↓
3. Split into: void command() + T query()
        ↓
4. Queries = pure reads, safe to cache, safe to repeat
   Commands = writes/events, return void
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CQS = CQRS | CQS is method-level; CQRS is an architectural pattern |
| Commands can never return anything | Commands can throw exceptions; status via exceptions is fine |
| Stack.pop() violates CQS and is wrong | It's a known pragmatic exception; document it |
| CQS is only for domain layer | Applies everywhere: services, repositories, controllers |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Incrementing Counters Inside Queries**
`findUser()` that also updates `lastAccessedAt` — now you cannot call queries freely in tests without accumulating state changes.
Fix: separate access tracking into an explicit command.

**Pitfall 2: Builder Fluent Chaining**
`builder.setName("x")` returning `this` is technically a CQS violation for chaining convenience.
This is a widely accepted pragmatic exception — document it clearly in the API.

**Pitfall 3: SELECT FOR UPDATE**
`SELECT ... FOR UPDATE` in SQL both reads and acquires a lock — a necessary CQS violation for correctness in concurrent systems.
Document the exception explicitly; keep it at the data layer, not business logic.

---

## 🔗 Related Keywords

- **CQRS (Command Query Responsibility Segregation)** — architectural extension of CQS at the system/service level
- **Idempotency** — queries must be idempotent; CQS enforces this structurally
- **Functional Programming** — pure functions are queries in CQS terms
- **Side Effects** — commands have them; queries must not
- **Event Sourcing** — pairs naturally with CQRS, which extends CQS

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Methods either change state (void) or return  │
│              │ data (no side effects) — never both           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Designing service, repository, domain methods │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Known pragmatic exceptions: pop(), iterators, │
│              │ SELECT FOR UPDATE                             │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Asking a question should not change          │
│              │  the answer"                                  │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS --> Event Sourcing --> Idempotency        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** How does CQS enable safe caching of query results?  
**Q2.** What is the difference between CQS (method level) and CQRS (architectural level)?  
**Q3.** `Iterator.next()` advances state AND returns a value — it violates CQS. Is this a design mistake or a pragmatic trade-off?

