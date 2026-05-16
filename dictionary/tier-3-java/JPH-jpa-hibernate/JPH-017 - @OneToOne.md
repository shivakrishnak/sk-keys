---
id: JPH-017
title: "@OneToOne"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-013
used_by: JPH-018, JPH-021, JPH-022, JPH-037
related: JPH-041, JPH-040
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /jpa-hibernate/onetoone/
---

# JPH-017 - @OneToOne

⚡ **TL;DR** - `@OneToOne` maps a one-to-one relationship
between two entities. The owning side holds the foreign
key column. Always make `@OneToOne` LAZY - Hibernate loads
the related entity eagerly by default (even with
`fetch=LAZY`) unless you use bytecode enhancement or
subselect fetch.

| #017 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Id and @GeneratedValue, @Table and @Column, Entity Lifecycle | |
| **Used by:** | @OneToMany and @ManyToOne, FetchType, CascadeType, @EntityGraph | |
| **Related:** | @Embedded and @Embeddable, Inheritance Mapping | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without `@OneToOne`, a one-to-one relationship between
`User` and `UserProfile` requires manually loading the
profile by user ID: `profileRepo.findByUserId(user.getId())`.
Every time a `User` is loaded, the caller must also
remember to load the profile if needed. If the caller
forgets, they get an NPE when accessing `user.getProfile()`.
If the caller always loads it, the data is fetched even
when not needed.

**THE BREAKING POINT:**
In a complex domain model with many one-to-one relationships
(User-Address, Order-Shipment, Product-Metadata), managing
these associations manually in every service method is
tedious and error-prone. The relationship is a core part
of the domain model, not a service-layer concern.

**THE INVENTION MOMENT:**
`@OneToOne` maps the relationship directly in the entity.
`user.getProfile()` navigates the relationship naturally.
JPA manages the foreign key, cascade, and fetch strategy.
The developer declares the relationship once in the entity
and all navigation is handled transparently.

---

### 📘 Textbook Definition

**`@OneToOne`** is a JPA annotation that maps a one-to-one
relationship between two entity classes. One entity is
the "owning side" (holds the foreign key column) and the
other is the "inverse side" (uses `mappedBy`). JPA uses
the foreign key on the owning side to join the two tables.

Attributes:
- `fetch`: `EAGER` (default, bad) or `LAZY` (recommended)
- `cascade`: cascade operations from owner to related entity
- `mappedBy`: marks the inverse (non-owning) side
- `optional`: whether the related entity can be null
  (default `true`; `false` generates NOT NULL constraint)

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@OneToOne` declares that one entity instance
maps to exactly one instance of another entity via a
foreign key.

**One analogy:**
> A `User` and their `Passport` - each user has at most
> one passport and each passport belongs to one user.
> `@OneToOne` on `User.passport` tells JPA where to find
> the passport when you navigate `user.getPassport()`.

**One insight:** The "LAZY loading does not work" trap.
`@OneToOne(fetch=LAZY)` on the INVERSE side (the side with
`mappedBy`) does NOT actually fetch lazily in standard
Hibernate - Hibernate needs to know if the related entity
is null or not, and issues the query to find out. True
lazy `@OneToOne` on the inverse side requires bytecode
enhancement or placing the FK on the inverse side.

---

### 🔩 First Principles Explanation

**OWNING SIDE vs INVERSE SIDE:**

```
User table:
  id BIGINT PK
  email VARCHAR

UserProfile table:
  id BIGINT PK
  user_id BIGINT FK -> user.id  <- FK lives here
  bio VARCHAR

Owning side (has FK): UserProfile owns the relationship
Inverse side (mappedBy): User has mappedBy="user"
```

**ENTITY CODE:**

```java
// Inverse side - User does NOT have the FK column
@Entity
public class User {
    @Id @GeneratedValue
    private Long id;

    // mappedBy = field name on UserProfile that owns FK
    @OneToOne(mappedBy = "user",
              fetch = FetchType.LAZY,
              cascade = CascadeType.ALL)
    private UserProfile profile;
}

// Owning side - UserProfile HAS the FK column
@Entity
public class UserProfile {
    @Id @GeneratedValue
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id",
                nullable = false)
    private User user;

    private String bio;
}
```

**CORE INVARIANTS:**
1. The side without `mappedBy` is the owning side - it
   controls the FK column
2. The side WITH `mappedBy` is the inverse side - changes
   to this side's field are IGNORED by JPA
3. Cascade and orphanRemoval are set on the side that
   "owns" the lifecycle (usually the parent)
4. `@OneToOne(fetch=LAZY)` on the INVERSE side does NOT
   guarantee lazy loading without bytecode enhancement
5. Shared primary key strategy (`@MapsId`) avoids the
   second FK column and is more efficient

---

### 🧪 Thought Experiment

**SETUP:**
`Order` and `Shipment` with `@OneToOne(mappedBy="order")`
on `Order.shipment` (inverse side, no FK).

**WHAT HAPPENS WITH `Order order = em.find(Order.class, 1L)`:**
Even with `fetch=LAZY` on the inverse `@OneToOne`:
1. Hibernate loads the `Order` row
2. Hibernate issues a SECOND SELECT for the `Shipment`
   to check if a Shipment with `order_id=1` exists
3. If null: `order.getShipment()` returns null proxy
4. If exists: `order.getShipment()` returns loaded entity

**WHY:** Hibernate needs to know whether to return null
or a proxy object for `order.getShipment()`. It must
hit the database to find out - so the "lazy" load
still executes the query at `em.find()` time.

**THE FIX: @MapsId (shared primary key):**

```java
// Shipment uses same PK as Order (no separate FK)
@Entity
public class Shipment {
    @Id
    private Long id;  // same as order.id

    @OneToOne(fetch = FetchType.LAZY)
    @MapsId
    @JoinColumn(name = "id")
    private Order order;
}
```

With `@MapsId`, `Shipment.id == Order.id`. Hibernate can
check if `shipment = em.find(Shipment.class, order.getId())`
returns null without an extra query - it uses the PK
directly. When `@MapsId` is used, lazy `@OneToOne` truly
defers the SELECT.

---

### 🧠 Mental Model / Analogy

> Think of `@OneToOne` as two houses sharing a single gate.
> The owning side holds the key to the gate (the FK column).
> The inverse side can access the gate via `mappedBy` but
> does not hold the key. When JPA asks "who controls the
> gate?", it looks for the side WITHOUT `mappedBy`.
>
> The lazy loading problem: even with a lazy gate (LAZY fetch),
> if you are standing on the inverse side (no key), the gatekeeper
> (Hibernate) must walk to the gate to check if it is locked
> or open before handing you the result - hence the extra query.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@OneToOne` tells JPA that one entity is linked to exactly
one instance of another entity. `user.getProfile()` loads
the linked profile.

**Level 2 - How to use it (junior developer):**
Declare `@OneToOne` on one entity, `@OneToOne(mappedBy="...")` 
on the other. Set `cascade=CascadeType.ALL` if the child
should be saved/deleted with the parent.

**Level 3 - How it works (mid-level engineer):**
The owning side generates a FK column. Hibernate joins
the two tables on that FK when loading the relationship.
Without `mappedBy`, both sides would generate FK columns
(both think they own the relationship) - typically causing
extra, unused columns.

**Level 4 - Why it was designed this way (senior/staff):**
The owning/inverse side distinction comes from the JPA
spec's requirement for a single source of truth for
the relationship state. If both sides could control the FK,
a save with conflicting values on each side would be
ambiguous. The `mappedBy` annotation explicitly delegates
FK ownership to the other side.

**Level 5 - Mastery (distinguished engineer):**
`@OneToOne` is often the wrong tool. The `@Embedded`/
`@Embeddable` pattern is more efficient for value objects
(no join, no second table). True one-to-one relationships
(one entity cannot exist without the other) are best mapped
with `@MapsId` (shared primary key) - it eliminates the
extra FK column, enables true lazy loading on the inverse
side, and enforces the constraint at the database level.
`@OneToOne` without `@MapsId` on separate-PK tables should
always be questioned: is this truly a one-to-one, or should
it be an `@Embedded` value object?

---

### ⚙️ How It Works (Mechanism)

**GENERATED SQL (standard @OneToOne):**

```
user table:          user_profile table:
id | email           id | user_id | bio
1  | alice@x.com     1  | 1       | "Hi!"

JOIN: SELECT u.*, p.* FROM user u
      LEFT JOIN user_profile p ON u.id = p.user_id
      WHERE u.id = ?
```

**GENERATED SQL (@MapsId - shared PK):**

```
user table:          shipment table:
id | email           id | tracking_no
1  | alice@x.com     1  | "ABC123"

JOIN: SELECT s.* FROM shipment s WHERE s.id = ?
      (same PK as order - no FK column needed)
```

**FETCH BEHAVIOR COMPARISON:**

```
EAGER fetch (default): JOIN in initial SELECT
LAZY fetch (owning side): works correctly, no extra query
LAZY fetch (inverse side, no @MapsId):
  - extra SELECT to check if related entity exists
  - true lazy only with @MapsId or bytecode enhancement
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CREATING A USER WITH PROFILE:**

```java
User user = new User("alice@example.com");
UserProfile profile = new UserProfile();
profile.setBio("Software engineer");
profile.setUser(user);  // set owning side

// also set inverse side (for in-memory consistency):
user.setProfile(profile);

// persist: cascade ALL from User (inverse side parent)
userRepo.save(user);
// -> INSERT INTO user (email) VALUES (?)
// -> INSERT INTO user_profile (user_id, bio) VALUES (?, ?)
```

**FAILURE PATH:**
Setting only the inverse side (user.setProfile(profile))
without setting the owning side (profile.setUser(user))
results in no FK written to the database. The `user_id`
column in `user_profile` remains null. This is the most
common `@OneToOne` bug.

---

### 💻 Code Example

**Example 1 - Standard bidirectional @OneToOne:**

```java
@Entity
public class User {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String email;

    @OneToOne(mappedBy = "user",
              cascade = CascadeType.ALL,
              fetch = FetchType.LAZY,
              orphanRemoval = true)
    private UserProfile profile;

    // Helper to keep both sides in sync:
    public void setProfile(UserProfile p) {
        this.profile = p;
        if (p != null) p.setUser(this);
    }
}

@Entity
public class UserProfile {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false,
                unique = true)
    private User user;

    private String bio;
    void setUser(User u) { this.user = u; }
}
```

**Example 2 - BAD: setting only the inverse side:**

```java
// BAD: only setting non-owning side
User user = new User("alice@x.com");
user.setProfile(new UserProfile("Software engineer"));
userRepo.save(user);
// UserProfile.user_id = NULL in database!
// The FK is null because UserProfile.user was never set

// GOOD: owning side must always be set
User user = new User("alice@x.com");
UserProfile profile = new UserProfile("Software engineer");
user.setProfile(profile);  // also sets profile.user via helper
userRepo.save(user);
// UserProfile.user_id = user.id (correct)
```

**Example 3 - @MapsId for shared primary key (recommended):**

```java
@Entity
public class Order {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;

    @OneToOne(mappedBy = "order",
              cascade = CascadeType.ALL,
              fetch = FetchType.LAZY)
    private Shipment shipment;
}

@Entity
public class Shipment {
    @Id
    private Long id;  // same as Order.id (no SEQUENCE)

    @OneToOne(fetch = FetchType.LAZY)
    @MapsId
    @JoinColumn(name = "id")
    private Order order;

    private String trackingNumber;
}
// Shipment.id = Order.id; no separate FK column
// True lazy loading possible on inverse side
```

---

### ⚖️ Comparison Table

| Approach | FK columns | True lazy on inverse | Table join | When to use |
|---|---|---|---|---|
| Standard `@OneToOne` | Separate FKs | No | JOIN on FK | Related entities with independent PKs |
| `@MapsId` (shared PK) | Shared PK | Yes | JOIN on PK | Parent-child with same lifecycle |
| `@Embedded` | Same table | N/A (single row) | No join | Value objects in same table |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`@OneToOne(fetch=LAZY)` always loads lazily" | On the INVERSE side (with `mappedBy`), Hibernate issues an extra SELECT even with `LAZY` to determine null vs. proxy. True lazy on the inverse side requires `@MapsId` or bytecode enhancement. |
| "Setting the inverse side (`mappedBy`) updates the database" | JPA ignores changes made to the `mappedBy` side. Only changes to the OWNING side (the side without `mappedBy`) are reflected in the database FK column. |
| "`optional=false` is enforced at the JPA level" | `optional=false` adds a NOT NULL constraint to the generated DDL. It also hints to Hibernate to use INNER JOIN instead of LEFT JOIN when loading. It does not prevent the Java field from being set to null. |
| "`@OneToOne` is always better than a separate query" | For performance, `@Embedded` (no join) is better for value objects. A separate repository call is better when the relationship is rarely needed - avoids the join overhead even with LAZY (which fires anyway on inverse side). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: FK is NULL After Save (Owning Side Not Set)**

**Symptom:** `user_profile.user_id` is NULL after saving
a `User` with a `UserProfile`. The profile is in the
database but its `user_id` is not set.
**Root Cause:** Only the inverse side (User.profile) was
set. The owning side (UserProfile.user) was never assigned.
JPA reads the FK from the owning side; the inverse side
is ignored for persistence.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# INSERT INTO user_profile (user_id, bio) VALUES (NULL, ...)
# -> user_id=NULL confirms owning side not set
```

**Fix:** Always set the owning side. Add a helper method
on the parent entity that sets both sides atomically.
**Prevention:** Use bi-directional sync helper methods
(e.g., `user.setProfile(profile)` sets
`profile.setUser(user)` internally). Unit tests for
entity associations.

---

**Failure Mode 2: N+1 From Inverse @OneToOne With LAZY**

**Symptom:** Loading 100 `Order` entities generates 101
SELECT statements - 1 for the order list and 100 for the
Shipment per order.
**Root Cause:** `Order.shipment` is the inverse side
(`mappedBy="order"`). Even with `fetch=LAZY`, Hibernate
issues a SELECT per Order to determine null vs. proxy.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# SELECT * FROM orders WHERE ...
# SELECT * FROM shipment WHERE order_id=1
# SELECT * FROM shipment WHERE order_id=2
# ... repeated N times
```

**Fix Option 1:** Use `@MapsId` on the Shipment side
to enable true lazy loading.
**Fix Option 2:** Use `@EntityGraph` or JOIN FETCH in
the query to explicitly join shipments:

```java
@Query("SELECT o FROM Order o " +
       "LEFT JOIN FETCH o.shipment " +
       "WHERE o.status = :s")
List<Order> findByStatus(@Param("s") String s);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - entities required for the association
- [[JPH-007 - @Id and @GeneratedValue]] - PK strategy
  affects `@MapsId` design choice
- [[JPH-008 - @Table and @Column]] - `@JoinColumn` follows
  the same naming rules

**Builds On This (learn these next):**
- [[JPH-018 - @OneToMany and @ManyToOne]] - most common
  association type; same owning/inverse concepts apply
- [[JPH-021 - FetchType (LAZY vs EAGER)]] - fetch strategy
  deep dive including `@OneToOne` LAZY trap
- [[JPH-022 - CascadeType]] - cascade operations from
  parent to child through associations

**Alternatives / Comparisons:**
- [[JPH-041 - @Embedded and @Embeddable]] - often better
  than `@OneToOne` for value objects in the same table

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Maps two entities in a 1:1 relationship  │
│              │ via a FK column on the owning side       │
├──────────────┼───────────────────────────────────────────┤
│ OWNING SIDE  │ No mappedBy; has the FK column; changes  │
│              │ here are written to the database         │
├──────────────┼───────────────────────────────────────────┤
│ INVERSE SIDE │ Has mappedBy; changes here are IGNORED   │
│              │ by JPA for persistence                   │
├──────────────┼───────────────────────────────────────────┤
│ LAZY TRAP    │ LAZY on inverse side still triggers a    │
│              │ SELECT. Fix: @MapsId or bytecode enhance │
├──────────────┼───────────────────────────────────────────┤
│ BEST PATTERN │ @MapsId for shared-PK @OneToOne; enables │
│              │ true lazy and removes extra FK column    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@OneToOne maps 1:1 FK; only owning side │
│              │ (no mappedBy) writes to DB; LAZY on       │
│              │ inverse side still queries - use @MapsId" │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. The side WITHOUT `mappedBy` is the owning side - it
   holds the FK and is the only side JPA writes to the DB
2. `@OneToOne(fetch=LAZY)` on the INVERSE side does NOT
   guarantee lazy loading - use `@MapsId` for true lazy
3. Always set BOTH sides of a bidirectional association
   in Java; use helper methods to keep them in sync

**Interview one-liner:** `@OneToOne` maps a one-to-one
FK relationship. The owning side (no `mappedBy`) holds
the FK column; only it controls the database write.
The inverse side with `mappedBy` is ignored by JPA
for persistence. `LAZY` fetch on the inverse side triggers
an extra SELECT anyway (Hibernate must check null vs. proxy);
use `@MapsId` (shared primary key) for true lazy loading.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any relationship model,
one side must be designated as the canonical source of truth
for the relationship state. JPA uses `mappedBy` for this.
This pattern appears in REST APIs (the canonical URL for
a resource is the source of truth; links from other resources
are "mappedBy" the canonical URL), in event-driven systems
(the producer owns the event schema; consumers map to it),
and in distributed databases (one shard owns the record;
other shards link to it). The "owning side / inverse side"
distinction prevents split-brain consistency problems.

---

### 💡 The Surprising Truth

`@OneToOne` with `optional=true` (the default) generates
a LEFT OUTER JOIN in Hibernate 5 and earlier. With
`optional=false`, it generates an INNER JOIN. This is
a significant performance difference on large tables:
INNER JOIN is typically faster because the database can
eliminate non-matching rows earlier in the query plan.
Many developers leave `optional=true` on required relationships
because they are unaware of this; the result is a LEFT
JOIN everywhere, slightly degrading every query. Setting
`optional=false` on required `@OneToOne` associations
(those with `nullable=false` on the `@JoinColumn`) improves
query plans without any code change.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DRAW** the database schema for a bidirectional
   `@OneToOne` and identify which table has the FK column
   from the Java entity code
2. **EXPLAIN** why `@OneToOne(fetch=LAZY)` on the inverse
   side still triggers an extra SELECT and what must be
   changed to make it truly lazy
3. **FIX** a bug where `user_profile.user_id` is null
   after save by identifying the missing owning-side assignment
4. **CHOOSE** between `@OneToOne`, `@OneToOne @MapsId`,
   and `@Embedded/@Embeddable` for three specific scenarios
   and justify each choice
5. **CONFIGURE** a `@MapsId` shared-primary-key `@OneToOne`
   from scratch without referencing documentation

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between the owning side
and the inverse side in a @OneToOne relationship?**
*Why they ask:* Tests fundamental JPA association knowledge;
not knowing this leads to silent null FK bugs.
*Strong answer includes:*
- Owning side: no `mappedBy`; holds the FK column;
  JPA writes the FK value from this side's field
- Inverse side: has `mappedBy`; changes to this field
  are IGNORED by JPA for database persistence
- Example: `UserProfile.user` (owning) vs
  `User.profile` (inverse with `mappedBy="user"`)
- Consequence: must always set the owning side for the FK
  to be written; setting only the inverse side results
  in a null FK

**Q2: Why does `@OneToOne(fetch=LAZY)` on the inverse
side not actually load lazily?**
*Why they ask:* This is a well-known JPA gotcha; tests
depth of understanding beyond documentation.
*Strong answer includes:*
- Hibernate must return either null or a proxy for the
  inverse `@OneToOne` field
- To decide which, it must query the FK table to check
  if a related entity exists
- This query is issued at entity load time, defeating
  lazy loading
- Fix: `@MapsId` (shared PK) - Hibernate can check if
  the entity exists using `em.find()` with the known PK
  without an extra SELECT, enabling true proxy deferral
- Alternative: bytecode enhancement proxy generation

**Q3: When would you use @MapsId with @OneToOne instead
of a standard @OneToOne?**
*Why they ask:* Tests awareness of advanced JPA patterns
and their design rationale.
*Strong answer includes:*
- When the related entity is a "detail" that shares
  the lifecycle of the parent (same PK, created together)
- Eliminates the separate FK column (uses shared PK)
- Enables true lazy loading on the inverse side
- Enforces 1:1 at the database level via PK uniqueness
- Examples: Order-Shipment (same ID), User-UserSettings
  (created at signup, same lifecycle)
- When NOT to use: entities with independent lifecycles
  or that may be shared (use standard FK + unique constraint)