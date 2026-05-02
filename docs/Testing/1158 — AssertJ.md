---
layout: default
title: "AssertJ"
parent: "Testing"
nav_order: 1158
permalink: /testing/assertj/
number: "1158"
category: Testing
difficulty: ★★☆
depends_on: JUnit 5, Unit Test
used_by: Java Developers
related: JUnit 5, Mockito, Hamcrest, Test Readability
tags:
  - testing
  - assertj
  - java
  - assertions
---

# 1158 — AssertJ

⚡ TL;DR — AssertJ is a Java assertion library that replaces JUnit's basic `assertEquals()` with a fluent, readable API: `assertThat(result).isEqualTo(expected)` — with type-safe methods for collections, exceptions, strings, optionals, and custom assertions.

| #1158 | Category: Testing | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JUnit 5, Unit Test | |
| **Used by:** | Java Developers | |
| **Related:** | JUnit 5, Mockito, Hamcrest, Test Readability | |

### 🔥 The Problem This Solves

JUnit's basic assertions produce unhelpful failure messages:
```
AssertionError: expected:<true> but was:<false>
// Which assertion? Why was it false? What was the actual value?
```

AssertJ failure messages:
```
AssertionError: 
expected: ["Alice", "Bob"]
 but was: ["Alice", "Charlie"]
// Clear: sorted() changed Bob to Charlie
```

And JUnit's assertion order is easily confused:
```java
// JUnit: which is expected, which is actual?
assertEquals(expected, actual);  // or assertEquals(actual, expected)?
assertEquals(user.getName(), "Alice");  // WRONG ORDER! Error message backwards

// AssertJ: always clear — assertThat(ACTUAL).isEqualTo(EXPECTED)
assertThat(user.getName()).isEqualTo("Alice");
```

### 📘 Textbook Definition

**AssertJ** is a Java assertion library providing a fluent, method-chaining API for writing test assertions. Starting from `assertThat(actualValue)`, it provides type-specific assertion methods depending on the type of the actual value: string assertions (contains, startsWith, matches), collection assertions (hasSize, contains, doesNotContain), exception assertions (isInstanceOf, hasMessage), Optional assertions (isPresent, hasValue), and more. AssertJ is included by default in Spring Boot Test (`spring-boot-starter-test`).

### ⏱️ Understand It in 30 Seconds

**One line:**
AssertJ = `assertThat(x).isEqualTo(y)` and many readable, type-specific assertion methods.

**One analogy:**
> AssertJ turns test assertions from terse mathematical notation (`assertEquals(a, b)`) into English sentences (`assertThat(cart.total).isEqualTo(100.0)`). The test reads like a specification: "assert that cart total is equal to 100.0."

### 🔩 First Principles Explanation

ASSERTION CATEGORIES AND EXAMPLES:
```java
// ===== PRIMITIVE / OBJECT =====
assertThat(42).isEqualTo(42);
assertThat(user).isNotNull();
assertThat(value).isNull();
assertThat(price).isGreaterThan(0.0);
assertThat(price).isBetween(10.0, 100.0);
assertThat(status).isIn(PENDING, CONFIRMED);  // one of

// ===== STRINGS =====
assertThat("Hello World")
    .isNotEmpty()
    .startsWith("Hello")
    .endsWith("World")
    .contains("lo Wo")
    .doesNotContain("Error")
    .matches("[A-Z][a-z]+ [A-Z][a-z]+")
    .hasSize(11);

// ===== COLLECTIONS / ITERABLES =====
assertThat(list)
    .hasSize(3)
    .contains("Alice", "Bob")               // contains these (any order)
    .containsExactly("Alice", "Bob", "Charlie")  // exact order
    .containsExactlyInAnyOrder("Charlie", "Alice", "Bob")
    .doesNotContain("Dave")
    .allMatch(s -> s.length() > 2)          // all elements pass predicate
    .anyMatch(s -> s.startsWith("A"));      // at least one passes

// ===== MAPS =====
assertThat(map)
    .containsKey("name")
    .containsEntry("role", "ADMIN")
    .doesNotContainKey("password")
    .hasSize(3);

// ===== OPTIONAL =====
assertThat(Optional.of("value"))
    .isPresent()
    .hasValue("value")
    .contains("value");
assertThat(Optional.empty()).isEmpty();

// ===== EXCEPTION ASSERTIONS =====
assertThatThrownBy(() -> service.call(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessage("argument must not be null")
    .hasMessageContaining("null");

assertThatCode(() -> service.call("valid"))
    .doesNotThrowAnyException();

// ===== SOFT ASSERTIONS (collect all failures) =====
SoftAssertions soft = new SoftAssertions();
soft.assertThat(user.getName()).isEqualTo("Alice");
soft.assertThat(user.getEmail()).isEqualTo("alice@test.com");
soft.assertThat(user.isActive()).isTrue();
soft.assertAll();  // reports ALL failures, not just the first
```

EXTRACTING FROM COLLECTIONS:
```java
List<User> users = service.getAllUsers();

// Extract a field from each element, then assert on the extracted values
assertThat(users)
    .extracting("name")               // string field name (not type-safe)
    .containsExactly("Alice", "Bob");

assertThat(users)
    .extracting(User::getName)        // method reference (type-safe)
    .containsExactlyInAnyOrder("Bob", "Alice");

// Extract multiple fields as tuples
assertThat(users)
    .extracting("name", "role")
    .containsExactlyInAnyOrder(
        tuple("Alice", "ADMIN"),
        tuple("Bob", "USER")
    );
```

CUSTOM ASSERTIONS (domain-specific):
```java
// Extend AbstractAssert for your domain
public class OrderAssert extends AbstractAssert<OrderAssert, Order> {
    public OrderAssert(Order actual) { super(actual, OrderAssert.class); }
    public static OrderAssert assertThat(Order order) { return new OrderAssert(order); }
    
    public OrderAssert isConfirmed() {
        assertThat(actual.getStatus()).isEqualTo(CONFIRMED);
        return this;  // for chaining
    }
    
    public OrderAssert hasTotalOf(double amount) {
        assertThat(actual.getTotal()).isEqualByComparingTo(BigDecimal.valueOf(amount));
        return this;
    }
}

// Usage:
assertThat(order).isConfirmed().hasTotalOf(99.90);
```

### 🧠 Mental Model / Analogy

> AssertJ is a **conversation in English**: instead of `assertEquals(expected, actual)` (mathematical notation with unclear argument order), you write `assertThat(actual).isEqualTo(expected)` (a sentence: "assert that actual is equal to expected"). The test reads like a specification, not a formula.

### 📶 Gradual Depth — Four Levels

**Level 1:** Replace `assertEquals(expected, actual)` with `assertThat(actual).isEqualTo(expected)`. Use `isNotNull()`, `isTrue()`, `hasSize()`, `contains()` for richer assertions.

**Level 2:** Use `assertThatThrownBy()` for exception tests (cleaner than `assertThrows`). Use `extracting(User::getName)` to assert on fields of list elements. Use `SoftAssertions` when you want to see ALL assertion failures, not just the first.

**Level 3:** Use custom assertions for your domain objects — extend `AbstractAssert`. These become part of your domain vocabulary in tests: `assertThat(order).isConfirmed().hasTotalOf(50.0)`. Import AssertJ's static `assertThat` alongside Mockito's BDDMockito's `given()` / `then()` for a consistent BDD-style test vocabulary.

**Level 4:** AssertJ's failure messages are generated lazily using `%s` substitution — the performance cost is zero if the assertion passes. Custom assertion failure messages: `.as("user should be active after registration").isTrue()` — the description appears before the assertion failure message, providing context. The `usingComparatorForType()` method customizes how specific types are compared — e.g., compare BigDecimal by value not scale (0.50 equals 0.5), compare LocalDate with tolerance.

### 💻 Code Example

```java
// Before AssertJ (JUnit assertions):
assertEquals(3, users.size());
assertTrue(users.contains(alice));
assertNotNull(result.getId());
// Failure: "expected: <3> but was: <2>" — no context

// After AssertJ:
assertThat(users)
    .hasSize(3)
    .contains(alice)
    .doesNotContain(bannedUser);
// Failure: "expected to contain: <User[name=Alice]>
//           but could not find: <User[name=Alice]>
//           in: <[User[name=Charlie], User[name=Bob]]>"
// Much more informative!

// Exception testing — the clear way
@Test
void processOrder_nullOrder_throwsException() {
    assertThatThrownBy(() -> orderService.process(null))
        .isInstanceOf(NullPointerException.class)
        .hasMessage("order must not be null");
}

// Soft assertions — see all failures at once
@Test
void userProfile_hasAllRequiredFields() {
    UserProfile profile = service.getUserProfile(userId);
    SoftAssertions.assertSoftly(soft -> {
        soft.assertThat(profile.getName()).isNotBlank();
        soft.assertThat(profile.getEmail()).contains("@");
        soft.assertThat(profile.getJoinDate()).isBefore(LocalDate.now());
        soft.assertThat(profile.getPreferences()).isNotEmpty();
    });
    // Reports ALL failures, not just the first
}
```

### ⚖️ Comparison Table

| | JUnit Assertions | AssertJ |
|---|---|---|
| Readability | `assertEquals(a, b)` | `assertThat(a).isEqualTo(b)` |
| Failure message | "expected: X but was: Y" | Full context with values |
| Collection checks | Limited | Rich (containsExactly, extracting) |
| Exception checking | `assertThrows()` | `assertThatThrownBy()` |
| Soft assertions | `assertAll()` | `SoftAssertions` |
| Custom assertions | ✗ | `AbstractAssert` extension |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "AssertJ replaces JUnit" | AssertJ replaces JUnit's assertion methods; JUnit 5 still provides the test runner |
| "More assertion methods = more test logic" | Rich assertions still verify one thing; they just do it more expressively |
| "Soft assertions hide failures" | Soft assertions collect ALL failures before reporting — you see more failures, not fewer |

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SYNTAX       │ assertThat(actual).method(expected)      │
├──────────────┼───────────────────────────────────────────┤
│ COLLECTIONS  │ hasSize, contains, containsExactly,      │
│              │ extracting, allMatch, anyMatch            │
├──────────────┼───────────────────────────────────────────┤
│ EXCEPTIONS   │ assertThatThrownBy(() -> ...).isInstanceOf│
├──────────────┼───────────────────────────────────────────┤
│ SOFT         │ SoftAssertions: see all failures at once  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "English-readable assertions with         │
│              │  informative failure messages"            │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** AssertJ's `usingRecursiveComparison()` compares objects field-by-field without requiring `equals()` to be implemented. This is powerful for domain objects where you don't want to implement `equals()` for production code but need equality in tests. Describe: (1) when `usingRecursiveComparison()` is appropriate vs. implementing `equals()` (domain object without identity concept vs. entity with ID), (2) how `ignoringFields("id", "createdAt")` handles auto-generated fields in comparisons, (3) the performance implications for deeply nested object graphs, and (4) how `usingComparatorForType(BigDecimalComparator.class, BigDecimal.class)` customizes comparison for financial amounts.

**Q2.** Custom AssertJ assertions are reusable, domain-specific assertion methods. Describe the complete workflow for creating and using a custom `OrderAssert`: (1) when creating custom assertions is worth the investment (domain objects tested in many tests), (2) how `AbstractAssert<SELF, ACTUAL>` generics enable fluent chaining (`isConfirmed().hasTotalOf(50.0)`), (3) the `OrderAssertions.assertThat(order)` factory method pattern that shadows AssertJ's own `assertThat` — IDE import conflicts and how to resolve them, (4) whether custom assertions should live in test code or be published as a separate library for teams sharing a domain model.
