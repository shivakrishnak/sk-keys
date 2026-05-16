---
id: JPH-044
title: "Hibernate Validator (Bean Validation)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-026, JPH-041
used_by: JPH-054, JPH-056
related: JPH-032, JPH-038, JPH-051
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
nav_order: 44
permalink: /jpa-hibernate/hibernate-validator/
---

# JPH-044 - Hibernate Validator (Bean Validation)

⚡ **TL;DR** - Hibernate Validator is the reference
implementation of Jakarta Bean Validation (JSR 380).
Annotate fields with `@NotNull`, `@Size`, `@Email`,
`@Min`, `@Max`, `@Pattern` etc. Spring Boot auto-validates
`@Valid`/`@Validated` on controller parameters and
`@Service` methods. JPA integration: Hibernate validates
entities before INSERT/UPDATE at the persistence layer.
Key distinction: Bean Validation happens at Java layer
(before SQL); `@Column(nullable=false)` is SQL DDL.
Both are complementary; neither replaces the other.

| #044            | Category: JPA & Hibernate                                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, @Id, @Table/@Column, EntityManager, @Transactional, @Embedded |                 |
| **Used by:**    | JPA at Scale, Spring Data JPA Architecture                             |                 |
| **Related:**    | JPA Auditing, Optimistic Locking, @Converter                           |                 |

---

### 🔥 The Problem This Solves

**VALIDATION WITHOUT BEAN VALIDATION:**

```java
@Service
public class UserService {
    public User createUser(String email, String name, int age) {
        if (email == null || !email.contains("@"))
            throw new IllegalArgumentException("Bad email");
        if (name == null || name.length() < 2 || name.length() > 100)
            throw new IllegalArgumentException("Bad name");
        if (age < 0 || age > 150)
            throw new IllegalArgumentException("Bad age");
        // Same validation duplicated in UpdateUser, ImportUser,
        // AdminCreateUser...
        return userRepo.save(new User(email, name, age));
    }
}
// Validation scattered in service methods
// Duplicated for every operation
// No structured error messages
// No automatic HTTP 400 from controller
```

**WITH BEAN VALIDATION:**

```java
@Entity
public class User {
    @NotNull @Email String email;
    @NotBlank @Size(min=2, max=100) String name;
    @Min(0) @Max(150) int age;
}

@RestController
public class UserController {
    @PostMapping("/users")
    public User create(@Valid @RequestBody UserDto dto) {
        // Auto-validation: MethodArgumentNotValidException
        // -> HTTP 400 with field errors; no manual code
    }
}
```

---

### 📘 Textbook Definition

**Hibernate Validator** is the reference implementation
of Jakarta Bean Validation (spec: `jakarta.validation`).
It validates Java beans using annotations on fields,
methods, and class level.

**Core annotations:**

- `@NotNull` - must not be null (any type)
- `@NotBlank` - must not be null or empty/whitespace (String only)
- `@NotEmpty` - must not be null or empty (String, Collection, Map, array)
- `@Size(min, max)` - size/length within range (String, Collection, array)
- `@Min(value)` / `@Max(value)` - numeric range (integer types)
- `@DecimalMin` / `@DecimalMax` - decimal range (BigDecimal, etc.)
- `@Email` - valid email format
- `@Pattern(regexp)` - matches regex
- `@Positive` / `@PositiveOrZero` - number > 0 / >= 0
- `@Negative` / `@NegativeOrZero` - number < 0 / <= 0
- `@Past` / `@PastOrPresent` / `@Future` / `@FutureOrPresent` - date/time

**Validation triggers in Spring Boot:**

1. `@Valid` / `@Validated` on controller `@RequestBody` - HTTP 400 on failure
2. `@Validated` on `@Service` class + constraints on method params - `ConstraintViolationException`
3. JPA: Hibernate validates entities before INSERT/UPDATE
   (`javax.persistence.validation.mode=auto`)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Bean Validation annotations declare constraints
on Java fields; Hibernate Validator enforces them at runtime
(at controller layer, service layer, and before SQL INSERT/UPDATE).

**One analogy:**

> Bean Validation annotations are like labels on a form's
> fields: "Email (required, valid format)", "Age (0-150)".
> The form itself can't be submitted without meeting all
> label requirements. In code, the annotations ARE the labels;
> the validator is the "submit button check" that rejects
> invalid data before it reaches the database.

**One insight:** Bean Validation works at the Java object
level - it runs before SQL. `@Column(nullable=false)` is
a SQL DDL constraint - it runs AT SQL time and produces
a `DataIntegrityViolationException` from the database.
Both layers are needed: Java-layer validation gives clear
error messages early; DB-layer constraints are the last
line of defense for direct DB access or bugs in validation
logic.

---

### 🔩 First Principles Explanation

**THREE VALIDATION TRIGGER LEVELS:**

```
Level 1: Controller (@Valid on @RequestBody)
  -> MethodArgumentNotValidException
  -> Spring handles: HTTP 400 with structured field errors
  -> Before method body executes

Level 2: Service (@Validated on class, constraints on params)
  -> ConstraintViolationException (unchecked)
  -> AOP proxy intercepts; Spring does NOT auto-map to HTTP 400
  -> Must catch and convert to HTTP 400 in @ControllerAdvice

Level 3: JPA (before INSERT/UPDATE)
  -> Hibernate calls Validator.validate(entity) before flush
  -> ConstraintViolationException wraps javax.validation violations
  -> Can catch in @Transactional method or propagates to controller
  -> JPA validation is LAST resort; prefer earlier layers
```

**CONSTRAINT HIERARCHY:**

```java
@Entity
public class Product {
    @NotNull               // Java null check (Level 1,2,3)
    @Column(nullable=false)// SQL DDL constraint (Level 3 only)
    private String name;

    // These enforce the SAME business rule at different layers:
    // @NotNull: prevents NullPointerException and HTTP 400
    // @Column(nullable=false): last defense, DB-level DDL
}
```

---

### 🧪 Thought Experiment

**VALIDATION WITHOUT @Valid ON CONTROLLER:**

```java
// BAD: missing @Valid -> no validation fires
@PostMapping("/users")
public User createUser(@RequestBody UserDto dto) {
    // dto.email = null here - no validation
    // UserService.create(dto) -> User entity saved
    // But User.email has @NotNull -> JPA validation fires
    // -> ConstraintViolationException from JPA layer
    // -> Spring: HTTP 500 (not 400!)
    // User sees "Internal Server Error" instead of 400 Bad Request

// GOOD: @Valid triggers controller-layer validation
@PostMapping("/users")
public User createUser(@Valid @RequestBody UserDto dto) {
    // If dto.email = null:
    // -> MethodArgumentNotValidException before method body
    // -> Spring: HTTP 400 with {"field": "email", "message": "must not be null"}
    // User sees clear error message
}
```

---

### 🧠 Mental Model / Analogy

> Think of validation layers as security checkpoints
> at an airport:
>
> Gate 1 (Controller + @Valid): the check-in desk checks
> your ticket (DTO/request body). Wrong format = turned
> away immediately with clear message. HTTP 400.
>
> Gate 2 (Service + @Validated): the security checkpoint
> applies business rules. Ticket valid for this zone?
> ConstraintViolationException.
>
> Gate 3 (JPA + Hibernate Validator): the gate agent does
> a final check before boarding (before SQL). Entity valid?
> If not: exception before INSERT.
>
> Gate 4 (Database NOT NULL): the airplane door - last
> physical barrier. DataIntegrityViolationException from DB.
>
> Best strategy: catch problems at Gate 1 (cheapest, clearest
> error messages). Never rely on Gate 4 as the first check.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Bean Validation annotations like `@NotNull`, `@Size`,
`@Email` declare rules on entity/DTO fields. Spring
automatically validates and returns HTTP 400 for invalid
requests. No manual null checks needed.

**Level 2 - How to enable it (junior developer):**
`spring-boot-starter-validation` adds Hibernate Validator.
Add `@Valid` to controller `@RequestBody` parameters.
Add constraint annotations to DTO and entity fields.
Use `@ExceptionHandler(MethodArgumentNotValidException.class)`
for custom error format.

**Level 3 - Service-layer validation (mid-level engineer):**
Add `@Validated` to `@Service` classes. Add constraints
to method parameters: `public void create(@Valid UserDto dto)`.
Spring AOP validates on method entry. Throws
`ConstraintViolationException`. Map to HTTP 400 in
`@ControllerAdvice`.

**Level 4 - Custom constraints (senior engineer):**
Create `@Constraint`-annotated custom annotation:

```java
@Documented
@Constraint(validatedBy = UniqueEmailValidator.class)
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueEmail {
    String message() default "Email already registered";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

`ConstraintValidator<UniqueEmail, String>` implements
`isValid()` - called by Hibernate Validator.

**Level 5 - Validation groups (staff engineer):**
Validation groups allow different constraints for different
operations: `@NotNull(groups = Create.class)` for POST,
`@Null(groups = Update.class)` for PUT. Use `@Validated(Create.class)`
in controller. Without groups, `@NotNull` on an ID field
would reject PUT requests (ID is set by server on POST
but must be provided on PUT). Groups provide operation-specific
validation sets.

---

### ⚙️ How It Works (Mechanism)

**CONTROLLER VALIDATION:**

```java
// DTO with Bean Validation constraints:
public record CreateUserRequest(
    @NotNull @Email
    String email,

    @NotBlank @Size(min = 2, max = 100)
    String name,

    @Min(0) @Max(150)
    int age,

    @NotNull @Pattern(regexp = "USER|ADMIN")
    String role
) {}

// Controller:
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse create(
            @Valid @RequestBody CreateUserRequest req) {
        // @Valid triggers MethodArgumentNotValidException
        // if any constraint fails - BEFORE method body runs
        return userService.create(req);
    }
}

// Global exception handler:
@RestControllerAdvice
public class ValidationExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, List<String>> handleValidation(
            MethodArgumentNotValidException e) {
        return e.getBindingResult().getFieldErrors()
            .stream()
            .collect(Collectors.groupingBy(
                FieldError::getField,
                Collectors.mapping(
                    FieldError::getDefaultMessage,
                    Collectors.toList())));
        // Returns: {"email": ["must be a well-formed email"],
        //           "name": ["size must be between 2 and 100"]}
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ENTITY-LEVEL VALIDATION:**

```java
@Entity
@Table(name = "users")
public class User {
    @Id @GeneratedValue
    private Long id;

    @NotNull @Email
    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @NotBlank @Size(min = 2, max = 100)
    @Column(nullable = false, length = 100)
    private String name;

    @Min(0) @Max(150)
    @Column(nullable = false)
    private int age;
}

// When repo.save(user) is called:
// 1. Hibernate calls entityManager.persist(user)
// 2. Before SQL, Hibernate validates entity (auto mode)
// 3. @NotNull, @Email, etc. checked via Hibernate Validator
// 4. Violation found -> ConstraintViolationException
//    (does NOT reach DB; no SQL issued)
// 5. No violation -> INSERT SQL issued
// 6. DB NOT NULL constraint is final backup (if somehow
//    bypassed in Java layer)
```

**CUSTOM VALIDATOR:**

```java
// Custom annotation for phone number format:
@Documented
@Constraint(validatedBy = PhoneNumberValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidPhone {
    String message() default "Invalid phone number format";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
    String countryCode() default "US";
}

public class PhoneNumberValidator
        implements ConstraintValidator<ValidPhone, String> {

    private String countryCode;

    @Override
    public void initialize(ValidPhone annotation) {
        this.countryCode = annotation.countryCode();
    }

    @Override
    public boolean isValid(String value,
            ConstraintValidatorContext context) {
        if (value == null) return true; // null handled by @NotNull
        // Real validation logic (e.g., Google libphonenumber):
        return value.matches("\\+?[0-9\\-\\s]{7,15}");
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: @NotNull on entity but missing on DTO:**

```java
// BAD: DTO has no @NotNull; entity has @NotNull
public class CreateUserRequest {
    private String email;  // no @NotNull here
    private String name;
}

@Entity
public class User {
    @NotNull private String email;  // validated at JPA layer
}

// Consequence:
// Controller: no validation -> invalid requests pass through
// JPA layer: ConstraintViolationException (too late!)
// HTTP response: 500 instead of 400
// FIX: Add @NotNull @Email to DTO as well

// GOOD: validate at DTO layer (controller input)
public class CreateUserRequest {
    @NotNull @Email private String email;
    @NotBlank @Size(min=2, max=100) private String name;
}
```

**Example 2 - Validation groups for CRUD operations:**

```java
// Groups:
public interface Create {}
public interface Update {}

public class UserDto {
    @Null(groups = Create.class)    // must be null on create
    @NotNull(groups = Update.class) // must be set on update
    private Long id;

    @NotBlank(groups = {Create.class, Update.class})
    private String email;
}

@RestController
public class UserController {
    @PostMapping
    public User create(
            @Validated(Create.class) @RequestBody UserDto dto) {
        // id must be null; email must not be blank
    }

    @PutMapping("/{id}")
    public User update(
            @Validated(Update.class) @RequestBody UserDto dto) {
        // id must be provided; email must not be blank
    }
}
```

---

### ⚖️ Comparison Table

| Layer      | Mechanism                            | When fires           | Exception                         | HTTP              |
| ---------- | ------------------------------------ | -------------------- | --------------------------------- | ----------------- |
| Controller | `@Valid` on `@RequestBody`           | Before method body   | `MethodArgumentNotValidException` | 400 (auto)        |
| Service    | `@Validated` + constraints on params | Method entry (AOP)   | `ConstraintViolationException`    | Must map manually |
| JPA        | Hibernate pre-flush validate         | Before INSERT/UPDATE | `ConstraintViolationException`    | Must map manually |
| Database   | SQL DDL NOT NULL, UNIQUE             | SQL execute          | `DataIntegrityViolationException` | Must map manually |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "@NotNull on entity is enough"                            | `@NotNull` on an entity field validates at the JPA layer (before flush). Without `@Valid` on the controller DTO, null values reach the service/entity layer first - resulting in ConstraintViolationException mapped to HTTP 500, not 400. Always validate at the earliest layer (controller DTO).  |
| "@Column(nullable=false) is the same as @NotNull"         | `@Column(nullable=false)` is SQL DDL metadata - it affects the generated CREATE TABLE statement and produces a DB-level constraint. `@NotNull` is Java-level validation that runs before SQL. They enforce the same business rule at different layers. Both are needed; neither replaces the other. |
| "Service-layer @Validated automatically returns HTTP 400" | Spring AOP throws `ConstraintViolationException` for service-layer validation failures. Spring does NOT automatically convert this to HTTP 400. You must handle it in a `@ControllerAdvice` or `@ExceptionHandler` explicitly.                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: HTTP 500 for Invalid Input**

**Symptom:** Sending null email in request body returns
HTTP 500 with `ConstraintViolationException` in logs
instead of HTTP 400.
**Root Cause:** `@Valid` missing on the `@RequestBody`
parameter in the controller method. Without it, the DTO
is not validated at the controller layer. Validation only
fires at the JPA layer (before flush), which is after
`@Transactional` is opened - the exception propagates
as a 500.
**Fix:**

```java
// BEFORE (broken):
public User create(@RequestBody UserDto dto)

// AFTER (correct):
public User create(@Valid @RequestBody UserDto dto)
```

**Verification:** Unit test with MockMvc:

```java
mockMvc.perform(post("/users")
    .content("{\"email\":null}")
    .contentType(APPLICATION_JSON))
    .andExpect(status().isBadRequest()); // 400
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-006 - @Entity]] - validation annotations on entity
  fields require understanding entities
- [[JPH-041 - @Embedded]] - `@Valid` cascades into
  embeddable objects (`@Valid` on @Embedded field)

**Builds On This (learn these next):**

- [[JPH-054 - JPA at Scale]] - validation configuration
  in large systems with multiple service layers

**Related:**

- [[JPH-032 - JPA Auditing]] - auditing and validation
  are complementary lifecycle concerns
- [[JPH-038 - Optimistic Locking]] - both are entity
  lifecycle guards; validation before save, version check at save

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE ANNOTS  │ @NotNull, @NotBlank, @Size, @Email,       │
│              │ @Min, @Max, @Pattern, @Valid (cascades)   │
├──────────────┼───────────────────────────────────────────┤
│ CONTROLLER   │ @Valid on @RequestBody -> HTTP 400 (auto) │
│ SERVICE      │ @Validated on class + @Valid on param     │
│              │ -> ConstraintViolationException           │
│ JPA          │ Auto before flush (last Java resort)      │
├──────────────┼───────────────────────────────────────────┤
│ CUSTOM       │ @Constraint(validatedBy=X.class)         │
│              │ ConstraintValidator<Ann, Type> impl       │
├──────────────┼───────────────────────────────────────────┤
│ GROUPS       │ @NotNull(groups=Create.class)             │
│              │ @Validated(Create.class) in controller    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bean Validation = Java-layer field      │
│              │ constraints; @Valid in controller = HTTP  │
│              │ 400; NOT NULL is separate SQL DDL."       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Add `@Valid` to controller `@RequestBody` parameters -
   without it, validation fires at JPA layer (too late) and
   produces HTTP 500 instead of 400
2. `@NotNull` (Java) and `@Column(nullable=false)` (SQL DDL)
   enforce the same rule at different layers - both needed
3. Service-layer `@Validated` throws `ConstraintViolationException`
   which does NOT automatically map to HTTP 400; handle in `@ControllerAdvice`

**Interview one-liner:** Hibernate Validator implements
Jakarta Bean Validation. Annotate DTO/entity fields with
`@NotNull`, `@Size`, `@Email` etc. Add `@Valid` to
controller `@RequestBody` for automatic HTTP 400 on violation.
`@Column(nullable=false)` is SQL DDL (runs at DB level);
`@NotNull` is Java validation (runs before SQL). Both layers
are needed. Custom validators implement `ConstraintValidator<Annotation, Type>`.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Validate at the entry
point (earliest possible layer). The later validation fires,
the more code has executed with invalid data, the more
exceptions are unexpected, and the harder error messages
are to surface to users. The same principle applies to:
(1) Input validation at API boundary (request DTO),
(2) Schema validation at message queue consumer boundary,
(3) Feature flag checks at service entry,
(4) Authentication/authorization at controller vs. service.
Defense in depth (multiple validation layers) is correct -
but the PRIMARY validation should always be at the outermost
boundary. Deep layers are backup, not primary enforcement.

**Where else this pattern appears:**

- **Spring @RequestParam @Valid** - path variable validation
- **Kafka consumer validation** - `@Validated` on consumer
  class validates message payloads
- **GraphQL input types** - `@NotNull`, `@Size` can be
  validated via `graphql-java` validators
- **Micronaut/Quarkus Bean Validation** - same JSR 380
  annotations, same pattern, different DI frameworks

---

### 💡 The Surprising Truth

When Hibernate Validator is on the classpath and
`spring.jpa.properties.javax.persistence.validation.mode`
is `auto` (the default), Hibernate automatically calls
`Validator.validate(entity)` before every INSERT and
UPDATE. This means entity-level `@NotNull`, `@Size`, etc.
fire BEFORE the SQL is issued. But here's the surprising
part: the validation fires AFTER `@Transactional` starts.
So if a validation exception is thrown from the JPA layer,
the transaction is rolling back - but the exception is
`ConstraintViolationException` from Hibernate Validator,
NOT from the database. This is NOT the same as SQL NOT NULL
violation. The exact exception type matters for exception
handling: `ConstraintViolationException` (javax.validation)
vs `DataIntegrityViolationException` (Spring JDBC). Know
which layer threw the exception to handle it correctly.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **ADD** `@Valid` to controller `@RequestBody` and configure
   a `@ControllerAdvice` for `MethodArgumentNotValidException`
2. **EXPLAIN** the difference between `@NotNull` (Java layer)
   and `@Column(nullable=false)` (SQL DDL)
3. **IMPLEMENT** a custom `ConstraintValidator` for a
   business-specific rule (e.g., valid phone format)
4. **USE** validation groups to have different constraints
   for Create vs Update operations
5. **DIAGNOSE** HTTP 500 instead of 400 (missing @Valid
   on @RequestBody)

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between @NotNull (Bean Validation)
and @Column(nullable=false) in JPA?**
_Why they ask:_ Very common interview question; tests depth.
_Strong answer includes:_

- `@NotNull`: Java annotation processed by Hibernate Validator;
  runs in Java before any SQL; throws `ConstraintViolationException`
  with a clear message; fires at controller (if `@Valid`),
  service (if `@Validated`), or JPA layer (pre-flush)
- `@Column(nullable=false)`: JPA annotation that affects DDL
  generation (`NOT NULL` in CREATE TABLE); enforced at DB level;
  throws `DataIntegrityViolationException` from the database
- Both are needed: Java layer gives clear user messages early;
  DB layer is last defense against bugs or direct DB access
- Neither replaces the other; they complement at different layers

**Q2: Why does a validation failure at the JPA layer return
HTTP 500 instead of HTTP 400, and how do you fix it?**
_Why they ask:_ Tests practical debugging knowledge.
_Strong answer includes:_

- `@Valid` missing on controller `@RequestBody` parameter:
  invalid DTO passes through controller without validation
- JPA layer (pre-flush) validates entity -> `ConstraintViolationException`
  thrown inside a `@Transactional` method -> Spring's default
  error handler maps unhandled exceptions to HTTP 500
- Fix: add `@Valid` on `@RequestBody` in controller - validation
  fires before method body, Spring auto-maps to HTTP 400
- Also: add `@ExceptionHandler(MethodArgumentNotValidException.class)`
  for structured error response format
