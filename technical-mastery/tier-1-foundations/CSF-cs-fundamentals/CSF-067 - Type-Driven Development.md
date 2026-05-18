---
id: CSF-067
title: Type-Driven Development
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-066, CSF-060
used_by:
related: CSF-066, CSF-060, CSF-034, CSF-065
tags: [type-driven-development, make-illegal-states-unrepresentable, domain-modeling, phantom-types, smart-constructors]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/csf/type-driven-development/
---

⚡ TL;DR - Type-Driven Development (TDD-types): use types
to ELIMINATE illegal states rather than detect them at runtime.
"Make illegal states unrepresentable" (Yaron Minsky). If the
type only allows valid values to be constructed, runtime checks
become unnecessary. Smart constructors: private constructor,
factory method with validation returns Success or Failure.
Parse, don't validate. Phantom types: carry constraints at
the type level with zero runtime cost.

| #067 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-066 (Type System Design for Large Codebases), CSF-060 (Curry-Howard Correspondence) | |
| **Used by:** | (builds into domain modeling and architecture patterns) | |
| **Related:** | CSF-066 (Type System Design), CSF-060 (Curry-Howard), CSF-034 (OOP), CSF-065 (Formal Semantics) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

```java
// A user object in a typical Java codebase:
class User {
    String email;
    String name;
    String phoneNumber;  // may be null if not provided
    boolean isEmailVerified;
    Date createdAt;
    Date lastLoginAt;    // null if never logged in
    String role;         // "ADMIN", "USER", "MODERATOR"
    // ...
}
```

Every field is "any valid String." `email` could be `""`, `"not-an-email"`,
or `null`. `role` could be `"SUPERADMIN"` (typo for non-existent role).
`lastLoginAt` could be before `createdAt` (impossible state). `isEmailVerified`
could be `true` but `email` is null (inconsistent state). The only defense:
runtime validation scattered across service methods, validators, and interceptors.
When validation is missed: bugs in production. When validation is duplicated:
maintenance cost.

**THE BREAKING POINT:**

In a large codebase, the same validation logic appears in 15 places:
the REST controller, the service layer, the repository layer,
the Kafka consumer, the scheduled job, the admin API...
Each implementation has slightly different rules. An inconsistency
causes a bug. A new validation rule requires 15 changes. Without
type-driven development, DEFENSIVE PROGRAMMING IS THE ONLY STRATEGY.
Every function defensively validates its inputs because it cannot
trust callers.

**THE INVENTION MOMENT:**

Yaron Minsky (Jane Street Capital, 2010): "Make Illegal States
Unrepresentable" in a blog post about OCaml. The insight: instead
of writing code to detect invalid states at runtime, change the
TYPES so invalid states CANNOT BE CONSTRUCTED. A type that can
only hold valid email addresses (validated at construction) means
every function that accepts `Email` (not `String`) automatically
works with a valid email. No defensive validation needed. The
type IS the invariant. This shifted the question from "how do I
validate inputs?" to "how do I design types that only allow valid values?"

---

### 📘 Textbook Definition

**Type-Driven Development:** A design methodology where the
TYPE SYSTEM is used as the primary tool for expressing and
enforcing domain invariants. Types are designed to EXCLUDE
invalid states, not just document valid ones. The compiler
becomes the primary validator.

**Make illegal states unrepresentable:** A design principle:
if a combination of values is invalid (e.g., an email address
that is both "verified" and null), that combination should
not be CONSTRUCTIBLE at the type level.

**Smart constructor:** A factory method (or companion object factory)
that validates input and returns a typed value only if valid.
The constructor is PRIVATE (cannot bypass validation).

**Parse, don't validate:** Rather than validating that an input
is valid and then using the raw string later, PARSE the input
into a rich type (Email, UserId, etc.) at the boundary. Functions
in the domain receive the rich type, not the raw string.

**Phantom types:** Type parameters that are present at compile
time but erased at runtime. Used to carry state or permission
information in the type without runtime overhead.

**Refined types:** Types with value-level constraints expressed
in the type (e.g., `PositiveInt`, `NonEmptyString`). Checked
at construction time only.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Type-Driven Development: design types so that valid code
COMPILES and invalid code DOES NOT. Move validation from
runtime (if statements, exceptions) to compile time (type errors).
If the type can only hold valid values, the type IS the validation.

**One analogy:**

> Validation approach: a customs officer who checks EVERY
> person who crosses the border (runtime validation). Slow,
> error-prone if the officer is tired (defensive checks everywhere).
>
> Type-Driven approach: a door that PHYSICALLY ONLY FITS valid
> keycards (type safety). Invalid keycards cannot even be
> tried. No officer needed. The door itself enforces the rule.
>
> Parse, don't validate: at the border, transform the passport
> into a "Border-Cleared Person" object. Inside the country,
> everyone is a Border-Cleared Person. No rechecking needed.

**One insight:**

"Parse, don't validate" (Alexis King, 2019) is the key insight.
Validation says: "I checked that this string is a valid email."
But you still have a String. Anyone can pass any String.
Parsing says: "I transformed this String into an Email object."
Now you have an Email. You cannot accidentally use a non-Email
String where an Email is expected. The transformation is the
proof that the validation succeeded. This is Curry-Howard
(CSF-060) in practice: the Email object is the PROOF that
the string is a valid email.

---

### 🔩 First Principles Explanation

**THE TWO APPROACHES COMPARED:**

```
┌──────────────────────────────────────────────────────┐
│ VALIDATE APPROACH:                                   │
│                                                      │
│ void sendEmail(String email, String body) {          │
│   if (!isValidEmail(email)) throw ...;               │
│   // email is still String after validation.         │
│   // Next function also needs to validate.           │
│   emailSender.send(email, body);  // trusts String   │
│ }                                                    │
│ void EmailSender.send(String to, String body) {      │
│   if (!isValidEmail(to)) throw ...; // again!        │
│   // Defensive checks everywhere.                    │
│ }                                                    │
│                                                      │
│ PARSE APPROACH:                                      │
│                                                      │
│ // Parse at boundary:                                │
│ Email email = Email.parse(rawInput)  // throws if bad│
│               .orElseThrow(...);                     │
│                                                      │
│ void sendEmail(Email email, EmailBody body) {        │
│   // email is Email. Known valid by construction.   │
│   // No validation needed. Cannot be invalid.       │
│   emailSender.send(email, body);                     │
│ }                                                    │
│ void EmailSender.send(Email to, EmailBody body) {    │
│   // to is Email. No defensive check needed.        │
│   // The type IS the proof.                          │
│ }                                                    │
└──────────────────────────────────────────────────────┘
```

**PHANTOM TYPES FOR STATE MACHINES:**

```
┌──────────────────────────────────────────────────────┐
│ Phantom type: type parameter present at compile,     │
│ erased at runtime. Carries STATE info in the type.  │
│                                                      │
│ // Phantom states (empty marker types):             │
│ sealed interface Unverified {}                       │
│ sealed interface Verified {}                         │
│                                                      │
│ // Request parameterized by state:                  │
│ @JvmInline value class Request<S>(val value: String)│
│                                                      │
│ // Verify: takes Unverified, returns Verified:       │
│ fun verify(r: Request<Unverified>): Request<Verified>│
│   = if (isValid(r.value)) Request(r.value)           │
│     else throw ValidationException()                 │
│                                                      │
│ // Process: requires Verified request:              │
│ fun process(r: Request<Verified>) { ... }            │
│                                                      │
│ // Cannot call process on unverified:               │
│ val raw = Request<Unverified>("user-input")          │
│ process(raw) // COMPILE ERROR: type mismatch        │
│ val verified = verify(raw)  // verify first         │
│ process(verified) // OK: verified request           │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE USER REGISTRATION FLOW:**

Consider: a user registers. The flow:
1. User submits email + password (raw strings)
2. Validate email format
3. Hash password
4. Send verification email
5. User clicks link -> email verified
6. User can now log in

With raw strings: every step needs to check "is this email valid?",
"has this email been verified?", "is this the hashed password or raw password?"
These are runtime checks because String can represent ANY state.

With type-driven design:
```kotlin
// Distinct types for each state:
@JvmInline value class RawEmail(val value: String)
@JvmInline value class ValidEmail(val value: String)  // valid format
@JvmInline value class VerifiedEmail(val value: String) // user clicked link

@JvmInline value class RawPassword(val value: String)
@JvmInline value class HashedPassword(val value: String)

// Constructor functions enforce transitions:
fun parseEmail(raw: RawEmail): ValidEmail  // or throws
fun hashPassword(raw: RawPassword): HashedPassword
fun sendVerification(email: ValidEmail): Unit
fun verifyEmail(valid: ValidEmail, token: String): VerifiedEmail // or throws

// Login: requires VerifiedEmail - unverified users cannot log in:
fun login(email: VerifiedEmail, password: HashedPassword): Session

// Register:
fun register(raw: RawEmail, rawPw: RawPassword) {
    val valid = parseEmail(raw)  // validates format
    val hashed = hashPassword(rawPw)  // hashes, forgets raw
    sendVerification(valid)
    // Store (valid, hashed) - NOT (raw, raw)
    // cannot call login here: only VerifiedEmail allowed
}
```
The flow is ENCODED IN TYPES. It is impossible to call `login`
with an unverified email: the type system prevents it.
No runtime check for "is this email verified?" in the login function.
The type already proves it.

---

### 🎯 Mental Model / Analogy

**ILLEGAL STATES IN DOMAIN MODELING:**

```
┌──────────────────────────────────────────────────────┐
│ SCENARIO: User profile with optional phone number    │
│                                                      │
│ BAD (Boolean + field, 4 states, 1 illegal):          │
│ class Profile {                                      │
│   String phone;         // may be null               │
│   boolean hasPhone;     // indicates if phone exists │
│   // Illegal state: hasPhone=true, phone=null        │
│   // Illegal state: hasPhone=false, phone="555-1234" │
│ }                                                    │
│ (2^1 * 2 string states = 4 combinations, 2 illegal) │
│                                                      │
│ BETTER (Option/nullable field, 2 states, both valid):│
│ class Profile {                                      │
│   String? phone;  // null = no phone, non-null = has │
│   // All combinations are valid:                    │
│   // null = no phone (consistent)                   │
│   // "555-1234" = has phone (consistent)            │
│ }                                                    │
│                                                      │
│ BEST (sealed class, states explicit):               │
│ sealed class PhoneStatus {                          │
│   object None : PhoneStatus()                       │
│   data class Present(val number: PhoneNumber)       │
│     : PhoneStatus()                                 │
│   // PhoneNumber is validated at construction.      │
│   // "555-INVALID" cannot be PhoneNumber.          │
│ }                                                    │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"Type-Driven Development: make illegal states unrepresentable.
Parse, don't validate: parse at boundary, work with rich types inside.
Smart constructor: private ctor, public factory that validates.
Factory returns Either/Option/Result, not throws (or throws at boundary only).
Phantom types: empty marker types as type parameters. State in the type.
Sealed classes for domain states: ordered (PENDING < PAID < SHIPPED).
Always think: 'what invalid state can this type hold?' If any: refactor.
Curry-Howard: Email object = proof that string is valid email."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Making a "safe" box: instead of a generic box that holds anything,
make a "valid email box" that only accepts email-shaped strings.
Once in the box: it's an email. No need to check again.
Type-Driven Development: design boxes that only hold valid things.

**Level 2 - Student:**
Smart constructor in Java:
```java
// Smart constructor: Email can only be created with valid value
public final class Email {
    private final String value; // private: cannot create Email directly
    private Email(String value) { this.value = value; }

    // Factory: validates, returns Optional or throws
    public static Optional<Email> of(String raw) {
        if (raw != null && raw.matches("^[^@]+@[^@]+\\.[^@]+$")) {
            return Optional.of(new Email(raw));
        }
        return Optional.empty();
    }
    public String getValue() { return value; }
}
// Usage:
Email email = Email.of(rawInput).orElseThrow(() ->
    new ValidationException("Invalid email: " + rawInput));
// After this point: email is guaranteed valid. No re-validation needed.
```

**Level 3 - Professional:**
Non-empty collection type:
```kotlin
// NonEmptyList: a list that is NEVER empty by construction
data class NonEmptyList<A>(val head: A, val tail: List<A>) {
    val all: List<A> get() = listOf(head) + tail
    val size: Int get() = 1 + tail.size

    companion object {
        fun <A> of(first: A, vararg rest: A): NonEmptyList<A> =
            NonEmptyList(first, rest.toList())
        // Cannot create empty NonEmptyList: must provide head
    }
}
// Function requiring at least one item:
fun sendToAll(recipients: NonEmptyList<Email>): Unit {
    // No need to check recipients.isEmpty() - impossible by type.
    // head is always available. No NPE risk.
}
```

**Level 4 - Senior Engineer:**
Phantom types for SQL query safety:
```kotlin
// Prevent raw SQL injection at the type level:
sealed interface Trusted
sealed interface Untrusted

@JvmInline value class SqlParam<S>(val value: String)

// Only trusted params can be used in queries:
fun buildQuery(
    table: SqlParam<Trusted>,
    condition: SqlParam<Trusted>
): String = "SELECT * FROM ${table.value} WHERE ${condition.value}"

// Mark user input as Untrusted:
fun fromUserInput(raw: String): SqlParam<Untrusted> = SqlParam(raw)

// Sanitize: validate and promote to Trusted:
fun sanitize(param: SqlParam<Untrusted>): SqlParam<Trusted> {
    if (!param.value.matches(Regex("[a-zA-Z_][a-zA-Z0-9_]*")))
        throw SecurityException("Invalid identifier: ${param.value}")
    return SqlParam(param.value)
}

// Cannot pass Untrusted to buildQuery:
val userTable = fromUserInput(request.getParam("table"))
buildQuery(userTable, ...) // COMPILE ERROR: Untrusted != Trusted
val safeTable = sanitize(userTable)
buildQuery(safeTable, ...) // OK: now Trusted
```

**Level 5 - Expert:**
Refinement types with Vavr (Java) or Arrow (Kotlin):
```kotlin
// Arrow 1.x: Either for type-safe error handling
import arrow.core.*

@JvmInline value class PositiveInt private constructor(val value: Int) {
    companion object {
        fun of(v: Int): Either<String, PositiveInt> =
            if (v > 0) Either.Right(PositiveInt(v))
            else Either.Left("Not positive: $v")
    }
}

@JvmInline value class Email private constructor(val value: String) {
    companion object {
        fun of(v: String): Either<String, Email> =
            if (v.contains("@")) Either.Right(Email(v))
            else Either.Left("Not an email: $v")
    }
}

// Compose validations with Either:
data class UserForm(val email: String, val age: Int)
data class ValidUser(val email: Email, val age: PositiveInt)

fun validate(form: UserForm): Either<String, ValidUser> =
    Email.of(form.email).flatMap { email ->
        PositiveInt.of(form.age).map { age ->
            ValidUser(email, age)
        }
    }
// Both validations run. Errors short-circuit.
// On success: ValidUser with typed email and age.
// On failure: Left with description of what failed.
```

---

### ⚙️ How It Works

**SMART CONSTRUCTOR PATTERN MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ Pattern:                                             │
│ 1. Type has PRIVATE constructor.                     │
│    No external code can create without validation.   │
│                                                      │
│ 2. PUBLIC factory method validates + wraps:          │
│    Returns: Either<Error, T> | T? | T (throws)       │
│    Choice depends on: expected frequency of invalid  │
│    input. User input: Either. Internal: throw.       │
│                                                      │
│ 3. Domain logic uses the TYPE, not the raw string.   │
│    Functions taking Email never receive raw string.  │
│                                                      │
│ 4. At SERVICE BOUNDARIES: parse.                     │
│    At REST controllers, Kafka consumers, file parsers│
│    -> PARSE to rich type immediately.               │
│    All internal code: work with rich types only.    │
│                                                      │
│ RESULT:                                              │
│ - Validation logic: ONE PLACE (the factory).        │
│ - All downstream: no validation needed.             │
│ - Compiler prevents bypassing validation.           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Ad-Hoc vs Smart Constructor**

```java
// BAD: Ad-hoc validation scattered everywhere
class OrderService {
    Order createOrder(String customerId, String productId,
                      int quantity) {
        // Defensive: validate here too
        if (customerId == null || customerId.isEmpty())
            throw new IllegalArgumentException("Invalid customerId");
        if (productId == null || productId.isEmpty())
            throw new IllegalArgumentException("Invalid productId");
        if (quantity <= 0)
            throw new IllegalArgumentException("Quantity must be > 0");
        // Same validation appears in CartService, CheckoutService, etc.
        return new Order(customerId, productId, quantity);
    }
}

// GOOD: Validate once, work with types everywhere (Kotlin)
@JvmInline value class CustomerId private constructor(val id: String) {
    companion object {
        fun of(raw: String): CustomerId {
            require(raw.isNotBlank()) { "CustomerId cannot be blank" }
            require(raw.matches(Regex("[a-zA-Z0-9-]{8,36}"))) {
                "Invalid CustomerId format: $raw"
            }
            return CustomerId(raw)
        }
    }
}
@JvmInline value class ProductId private constructor(val id: String) {
    companion object {
        fun of(raw: String) = ProductId(
            raw.also { require(it.isNotBlank()) { "Invalid ProductId" } }
        )
    }
}
data class PositiveQuantity private constructor(val value: Int) {
    companion object {
        fun of(v: Int) = PositiveQuantity(
            v.also { require(it > 0) { "Quantity must be positive" } }
        )
    }
}

// Service: no validation needed, types guarantee validity
class OrderService {
    fun createOrder(
        customerId: CustomerId,
        productId: ProductId,
        quantity: PositiveQuantity
    ): Order = Order(customerId, productId, quantity)
    // CustomerId, ProductId, PositiveQuantity: all valid by construction.
}
```

**Example 2 - Parse, Don't Validate (REST Controller)**

```kotlin
// BAD: validate in service (string passed around)
@RestController
class OrderController(val orderService: OrderService) {
    @PostMapping("/orders")
    fun createOrder(@RequestBody req: CreateOrderRequest): Order {
        // String IDs passed to service
        return orderService.create(req.customerId, req.productId, req.qty)
        // Service must validate too (defensive)
    }
}

// GOOD: Parse at the boundary (controller)
@RestController
class OrderController(val orderService: OrderService) {
    @PostMapping("/orders")
    fun createOrder(@RequestBody @Valid req: CreateOrderRequest): Order {
        // Parse strings to rich types at the HTTP boundary:
        val customerId = CustomerId.of(req.customerId) // throws 400 if bad
        val productId = ProductId.of(req.productId)
        val quantity = PositiveQuantity.of(req.qty)
        // All domain types from here on. No re-validation in service.
        return orderService.create(customerId, productId, quantity)
    }
}
// Register exception handler: ConstraintViolationException or
// IllegalArgumentException (from require) -> 400 Bad Request.
```

---

### ⚖️ Comparison Table

| Approach | Validation location | Defensive checks | Refactoring safety |
|---|---|---|---|
| Raw strings everywhere | Every function | Required everywhere | Poor (any string accepted) |
| Smart constructors | Factory only | Not needed after parse | Good (type system enforces) |
| Phantom types | Transition functions | Not needed after marking | Excellent (states in types) |
| Sealed class ADTs | Pattern match exhaustive | Not needed | Excellent (compiler enforces) |
| Runtime annotations (@Valid) | AOP/framework layer | Reduced (framework checks) | Moderate (annotation-based) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Smart constructors make the codebase more verbose - not worth it" | The verbosity of defining value types is a ONE-TIME cost. The benefit is the elimination of REPEATED validation logic across the entire codebase. If your codebase has 20 places that check "is this a valid customer ID?", that's 20 opportunities for inconsistency and maintenance burden. One smart constructor eliminates all 20 defensive checks. The verbosity equation tips positive at 2-3 call sites for a validation rule. Beyond that: net reduction in code (one validation vs 20 defensive checks). Modern Kotlin value classes have near-zero overhead in both code and runtime performance. |
| "You still need runtime validation for user input - types don't help at boundaries" | Types DO help at boundaries, but the PARSING happens at the boundary. "Parse, don't validate": convert user input to rich types AS EARLY AS POSSIBLE (at the REST controller, Kafka consumer, etc.). After the boundary, ALL code works with rich types. The boundary validation IS the smart constructor. You still write validation logic once (in the constructor). What you eliminate: the same validation logic repeated deep inside the domain logic. The boundary is narrowed to one place. Validation remains; defensive re-validation is eliminated. |
| "This is only useful in Haskell or Scala, not in Java" | Type-Driven Development works in Java (with more ceremony): final classes with private constructors and static factory methods, Optional for nullable smart constructors, sealed interfaces/classes (Java 17+), and record types (Java 14+). Java's lack of value types (before Project Valhalla) means smart constructors create object allocations. For high-performance hot paths: benchmark before applying. For most domain logic: the correctness benefit far outweighs the minor allocation cost. Kotlin's value classes are zero-overhead. Spring applications with Java can apply the parse-at-boundary pattern using @RequestBody with bean validation + custom converter classes. |
| "Phantom types are esoteric - not useful in production" | Phantom types appear in production at Google, Jane Street, and other large engineering orgs. Common production uses: (1) Builder patterns that enforce required steps in order: `Builder<Missing, Missing>` -> after setName: `Builder<Name, Missing>` -> after setAge: `Builder<Name, Age>` -> only buildable when both fields set. (2) Security: `Sanitized<String>` vs `Unsanitized<String>` - SQL parameters, HTML output. (3) Transaction contexts: `WithinTransaction<T>` ensures certain operations only run inside DB transactions. (4) Kotlin coroutines: `Deferred<T>` is a phantom-type-like concept (async result type). They are not esoteric; they are underused because most engineers haven't been taught the pattern. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Smart Constructor Throws in Unexpected Places**

**Symptom:** `IllegalArgumentException` deep inside a service
layer from a smart constructor that "should never be called
with invalid data." The stack trace shows the exception
comes from `Email.of(String)` inside a scheduled job that
reads from a database.

**Root Cause:** Data was stored in the database as a raw String
before the smart constructor was introduced. Now that the
constructor validates, PREVIOUSLY STORED invalid data causes
failures when read from DB.

**Diagnosis:**
```sql
-- Find invalid emails in the database:
SELECT id, email FROM users WHERE email NOT REGEXP '^[^@]+@[^@]+\.[^@]+$';
-- How many? Decide: fix data, or provide lenient parsing for legacy data.
```

**Fix:** Two-phase migration:
1. Add `Email.ofLegacy(String)`: lenient factory for reading from DB
   (accepts any non-null string for backward compatibility)
2. `Email.of(String)`: strict factory for user input
3. Gradually migrate legacy emails to valid format (batch job)
4. Once all emails valid: remove `ofLegacy`, use `of` everywhere

---

**Security Note:**

Parse, don't validate is a SECURITY PATTERN. The classic
security vulnerability: validate a string, then use the
STRING (not the validated result). Between validation and use,
the string can be modified (TOCTOU: Time-of-Check Time-of-Use).

With smart constructors: validation and creation are ATOMIC.
The `Email` object is the proof that the string was valid
at the moment of creation. You work with the `Email` object
afterward, not the raw string. The TOCTOU window is eliminated.

For SQL injection prevention via phantom types:
```kotlin
// Type-safe parameterized query (phantom type pattern):
val rawInput: SqlParam<Untrusted> = fromUserInput(req.param("id"))
// Cannot use rawInput in query directly: type error.
val safeId: SqlParam<Trusted> = sanitize(rawInput) // validates + promotes
val result = db.query("SELECT * FROM users WHERE id = ?", safeId.value)
// safeId.value: sanitized, safe to use in query.
// Raw input: cannot be accidentally passed to query.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Type System Design for Large Codebases` (CSF-066) - the
  type system features (sealed classes, value types, structural
  typing) that enable type-driven design
- `Curry-Howard Correspondence` (CSF-060) - the deep reason
  why "type = proof": a rich type IS a proof of validity

**Builds On This (learn these next):**
- Domain Modeling with ADTs (see DPT and SAP categories for
  patterns like Repository, Value Object, Aggregate)
- Arrow/Vavr for functional error handling in typed domain models

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ PRINCIPLE    │ Make illegal states unrepresentable    │
│              │ Types express invariants, not just data│
├──────────────┼─────────────────────────────────────────┤
│ PARSE NOT    │ Validate once at boundary               │
│ VALIDATE     │ Return rich type (Email, not String)   │
├──────────────┼─────────────────────────────────────────┤
│ SMART CTOR   │ Private constructor + public factory   │
│              │ Factory returns Either/Option/T (throws)│
├──────────────┼─────────────────────────────────────────┤
│ PHANTOM TYPE │ Empty marker interface as type param   │
│              │ State carried in type, zero runtime cost│
├──────────────┼─────────────────────────────────────────┤
│ SEALED CLASS │ Fixed variants + exhaustive matching   │
│              │ Impossible to add state without handling│
├──────────────┼─────────────────────────────────────────┤
│ REFINED TYPE │ Value constraint in type               │
│              │ PositiveInt, NonEmptyString, etc.       │
├──────────────┼─────────────────────────────────────────┤
│ JAVA TOOLS   │ Private ctor + static factory + record │
│              │ Sealed classes (Java 17+)               │
├──────────────┼─────────────────────────────────────────┤
│ KOTLIN TOOLS │ @JvmInline value class (zero cost)      │
│              │ Sealed class + when (exhaustive)        │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-066 (Type System Design)            │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. "Make illegal states unrepresentable": design types so that
   invalid combinations CANNOT BE CONSTRUCTED. Replace `String email`
   + `boolean isVerified` (4 states, 2 illegal) with `Optional<VerifiedEmail>`
   (2 states, both valid). The type system enforces invariants;
   no runtime checks needed after construction. This scales: each
   smart constructor is one place where validation lives.
2. Parse, don't validate: at system boundaries (HTTP controllers,
   message consumers, file parsers), PARSE raw input into rich domain
   types (Email, UserId, PositiveInt). Domain logic receives rich
   types only. No re-validation needed inside domain logic. The rich
   type IS the proof that parsing (validation) succeeded. This eliminates
   defensive validation scattered throughout the codebase.
3. Phantom types: add type parameters that carry STATE or PERMISSION
   information at the type level with ZERO runtime cost (erased at compile/JVM).
   `SqlParam<Untrusted>` and `SqlParam<Trusted>` have identical runtime
   representations but distinct compile-time types. `sanitize(Untrusted) -> Trusted`
   is the validated upgrade path. Functions that accept `Trusted` cannot
   accidentally receive `Untrusted` input. Used for: SQL injection prevention,
   security boundaries (sanitized/unsanitized), workflow state (verified/unverified),
   and builder patterns (required fields).

**Interview one-liner:**
"Type-Driven Development: make illegal states unrepresentable. Parse don't validate:
parse at boundaries, work with rich types inside (Email, UserId, not String/Long).
Smart constructors: private ctor + public factory that validates, returns Either/Option.
Phantom types: empty marker type params carry state at compile time, erased at runtime.
Sealed classes: exhaustive pattern matching eliminates forgotten cases. Curry-Howard:
the rich type IS the proof the value is valid."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
MOVE VALIDATION INWARD, MOVE PARSING OUTWARD. Validation
should happen at the SYSTEM BOUNDARY (inward: not deep inside
domain logic). Parsing (conversion to rich types) should happen
AS EARLY AS POSSIBLE (outward: at the boundary, before domain logic).
These are the same principle stated from two directions. The result:
domain logic works only with valid, rich types. The boundary
is the only place where "what if this is invalid?" must be answered.
This is the SINGLE RESPONSIBILITY PRINCIPLE applied to validation:
one place (the smart constructor) is responsible for ensuring validity.
All other places RELY on the type guarantee.

**Where else this pattern appears:**

- **Protocol Buffer / Avro schema with code generation** - Protobuf
  and Avro schemas are TYPE-DRIVEN DEVELOPMENT for serialization.
  The schema (fields with types, required/optional) defines the
  valid message structure. Code generation produces typed classes
  (e.g., `UserProto` in Java with `getUserId(): String`). Parsing
  a protobuf binary: either succeeds and produces a typed `UserProto`,
  or fails with a parse error. You never work with raw bytes after
  parsing. The generated class IS the proof that the bytes were valid
  protobuf. Contrast with JSON + POJO: Jackson can silently produce
  a `User` with null fields if JSON is missing required fields (without
  strict null checking). Protobuf's generated code: required fields
  have default values (proto2: missing required = parse failure;
  proto3: all optional, fields have default zero values).
  Schema evolution rules (backward/forward compatibility) are
  type-driven constraints on what schema changes are valid.
- **React PropTypes and TypeScript in React** - React's PropTypes
  (runtime) is validate-at-runtime. TypeScript interface for props
  is type-driven (compile-time). The progression: (1) No types:
  any prop can be any value. (2) PropTypes: runtime check, warning
  in dev. (3) TypeScript interface: compile error if wrong prop type.
  (4) Discriminated union for component state: sealed class equivalent.
  `type ButtonState = { kind: "loading" } | { kind: "error"; msg: string } | { kind: "ready" }`.
  Components that pattern-match on ButtonState with exhaustive checks:
  adding a new state variant fails compilation until all components handle it.
  This is type-driven UI development: the compiler enforces that all
  components handle all states. No missing case causes a blank screen silently.
- **Database schema as type system** - A well-designed database schema
  IS type-driven design for persistence. NOT NULL constraints: eliminate
  invalid null states (the nullable column = `Option<T>`). FOREIGN KEY
  constraints: referential integrity (you cannot have an order for a
  non-existent customer = the type system enforces the relationship).
  CHECK constraints: refined types (`quantity > 0`, `price >= 0`).
  UNIQUE constraints: prevent duplicate values (unique email = Email type
  with uniqueness enforced). The schema is the type system for data at rest.
  Jooq (type-safe SQL Java library) bridges: schema = types in Java code,
  enforced at compile time. A column rename in the DB regenerates Jooq types,
  and ALL queries that use the old name fail to compile. This is parse-at-
  compile-time for database access: schema changes are caught before deployment.

---

### 💡 The Surprising Truth

Jane Street Capital, the algorithmic trading firm, handles
billions of dollars in trades daily using OCaml - a language
famous for its strong type system and value of type-driven
development. Yaron Minsky's "Make Illegal States Unrepresentable"
blog post came from his experience at Jane Street: in financial
software, an illegal state (a negative position, a mismatched
trade, a wrong instrument type) does not just cause a bug report.
It causes financial loss. The cost of a type error in production
is measured in millions of dollars per second. Type-driven
development at Jane Street is not a stylistic choice - it is
a FINANCIAL RISK MANAGEMENT tool. Types are the cheapest,
fastest, and most reliable form of verification. The OCaml
type checker runs in milliseconds and catches errors that would
cost millions to detect in production. Every value class,
every smart constructor, every phantom type is a financial hedge.
This explains why trading firms and aerospace software (both
with catastrophic failure costs) invest heavily in type theory
and formal methods: the upfront cost of types is trivial
compared to the downside of type errors in production.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY-ILLEGAL-STATES]** Given the following class, identify
   ALL illegal states: `class DeliveryAddress { String street; String city;
   String country; boolean isValidated; String validatedBy; }`.
   Redesign it using sealed classes and value types to eliminate them.

2. **[SMART-CONSTRUCTOR]** Implement a smart constructor for a
   `CreditCardNumber` in Kotlin using `@JvmInline value class`.
   Include Luhn algorithm validation. Return `Either<ValidationError, CreditCardNumber>`.
   Show how the controller uses it (parse at boundary pattern).

3. **[PHANTOM-TYPES]** Implement a phantom type pattern for HTML
   template rendering: distinguish `RawHtml<Untrusted>` (user input)
   from `SafeHtml<Sanitized>` (after HTML escaping). Implement `escape()`
   as the promotion function. Ensure rendering functions only accept `Sanitized`.

4. **[SEALED-STATE-MACHINE]** Design a Kotlin sealed class hierarchy
   for a subscription: `Trial(daysLeft: Int)`, `Active(renewsAt: LocalDate)`,
   `PastDue(overdueDays: Int)`, `Cancelled(reason: String)`. Write
   `canAccessFeature(s: SubscriptionState): Boolean` exhaustively.

5. **[ANALYZE]** A codebase has `UserService.findById(String id)` returning
   `User?`. User has `val email: String?` and `val isEmailVerified: Boolean`.
   List all illegal states this design allows. Provide a redesigned API
   using type-driven development principles.

---

### 🧠 Think About This Before We Continue

**Q1.** "Parse, don't validate" says to transform input into
a rich type at the boundary. But what about OPTIONAL fields?
If `phoneNumber` might not be present, what do we parse it into?

*Hint: Optional fields are modeled as `Optional<PhoneNumber>` (Java),
`PhoneNumber?` (Kotlin), or `Option<PhoneNumber>` (Haskell/Arrow).
Parse at the boundary:
  val phone = rawPhone?.let { PhoneNumber.of(it) }
  // rawPhone is String? (from request, may be null or absent)
  // PhoneNumber.of() validates format
  // result: PhoneNumber? (null if not provided, validated if provided)
The key: you don't parse null into a PhoneNumber.
You parse null into "no phone number" (the None/null case of Optional<PhoneNumber>).
You parse a non-null String into either PhoneNumber (valid) or throw (invalid format).
The TYPE SYSTEM then enforces:
- Functions that REQUIRE a phone: take PhoneNumber (non-optional).
- Functions that HANDLE optional phone: take PhoneNumber? (nullable in Kotlin).
- Functions that don't care: take User (which contains PhoneNumber?).
ILLEGAL STATE from the previous section example: `hasPhone=true AND phone=null`.
With `PhoneNumber?`: this state is IMPOSSIBLE. Either it's `null` (no phone) or
it's a `PhoneNumber` (valid phone). The boolean `hasPhone` is ELIMINATED.
The type is the flag. Presence of `PhoneNumber` = has phone. Absence = doesn't.
Extension: `sealed class PhoneStatus { object None; data class Verified(val n: PhoneNumber) }`
This distinguishes "no phone" from "phone provided but unverified" from
"phone verified" - three states, all valid, no illegal combinations.*

**Q2.** At what granularity should you apply smart constructors?
Should every field of a domain object be its own type?
What's the trade-off?

*Hint: There's a spectrum from "too little" to "too much":
TOO LITTLE: Every field is String/Long/Int. The compiler provides no domain safety.
Primitive obsession. Transfer(long, long, long) - any argument order compiles.
TOO MUCH: Every possible constraint is a separate type.
Email, ValidEmail, VerifiedEmail, VerifiedWorkEmail, VerifiedPersonalEmail...
The type hierarchy becomes its own complexity. Cognitive overhead increases.
The question is: WHICH DISTINCTIONS MATTER FOR YOUR DOMAIN?
Guidelines:
1. ID-type fields ALWAYS deserve their own type (UserId, OrderId).
   Mixing IDs is the most common and most costly primitive obsession bug.
2. Status/state fields: sealed class (not String or enum string).
   OrderStatus.Pending vs "PENDING" string.
3. Validated strings that appear at APIs: Email, PhoneNumber, URL.
   These have format rules and appear in many function signatures.
4. Units that could be confused: Money(cents: Long, currency: Currency)
   not just Long. Price vs Quantity vs Amount.
5. Domain invariants that appear in multiple places:
   PositiveInt (for quantities), NonEmptyString (for required text).
DON'T wrap:
1. Purely internal temporaries (loop counters, index variables).
2. Simple flags where Boolean is unambiguous.
3. Derived values that are immediately used and discarded.
The RULE OF THUMB: if a value crosses an API boundary (function parameter,
return type, storage), ask "could the wrong type be passed here?"
If yes: strong type. If no: primitive is fine.
The cost of wrapping is syntax verbosity (wrapping/unwrapping) + minor allocation
(Java without Valhalla; Kotlin @JvmInline is zero-cost).
The benefit: every crossing of a type boundary is a compile-time safety check.*

---

### 🎯 Interview Deep-Dive

**Q1: "What does 'make illegal states unrepresentable' mean? Give an example."**

*Why they ask:* Tests domain modeling depth and functional programming influences.

*Strong answer includes:*
- Concept: design types so that invalid combinations of values CANNOT BE CONSTRUCTED.
  Not "validate at runtime" but "prevent invalid types from existing."
- Classic example: `class User { String email; boolean isVerified; }`.
  Illegal state: `email = null` AND `isVerified = true`. Better: `Optional<VerifiedEmail>`.
  If present: email exists and is verified. If absent: no verified email.
  Now: email-null-but-verified state is IMPOSSIBLE (null Optional != verified state).
- Sealed class example: Order status as String (can be "SHIPPED", "shiped", null)
  vs sealed class (only defined variants, no invalid strings, no null).
- Java implementation: private constructor + static factory, sealed interface.
- Kotlin implementation: @JvmInline value class, sealed class, data class with validation in init.
- Trade-off: more upfront type design, less runtime checking. Shifts bugs from runtime to compile time.

**Q2: "What is the difference between 'parse, don't validate' and traditional input validation?"**

*Why they ask:* Tests understanding of functional approach to data validation.

*Strong answer includes:*
- Traditional validation: check if input is valid, then use the RAW INPUT. The validation
  result (true/false) is separate from the data. You still have a String. Defensive
  re-validation is needed at every function that uses the String.
- Parse, don't validate: convert input to a RICH TYPE. The transformation is the validation.
  If it succeeds: you have an `Email`, not a `String`. Every function that accepts `Email`
  is guaranteed a valid email - by the type system, not by convention.
- Why it's better:
  1. ONE validation point (the smart constructor). Not scattered.
  2. TYPE SYSTEM enforces it. Cannot bypass.
  3. TOCTOU prevention: you work with the parsed object, not the raw string.
     No window between validation and use.
- Java example: `Email.of(rawString)` -> Optional<Email> or throws.
  Controller: parses to Email. Service: receives Email. Never String.
- Connection to Curry-Howard: the Email object is the PROOF that the string was valid.
  Types as propositions: `Email` = the proposition "this is a valid email."
  Having an Email object = having a proof of that proposition.
