---
id: JPH-051
title: "@Converter and AttributeConverter"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-041
used_by: JPH-054, JPH-058
related: JPH-040, JPH-044, JPH-060
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
nav_order: 51
permalink: /jpa-hibernate/attribute-converter/
---

# JPH-051 - @Converter and AttributeConverter

⚡ **TL;DR** - `AttributeConverter<X, Y>` translates
between a Java type `X` (entity field type) and a JDBC
type `Y` (DB column type). Use when: (1) storing enums
as code strings not ordinals, (2) storing custom types
(Money, EmailAddress) as a single column, (3) encrypting
sensitive fields before persistence. Annotate with
`@Converter(autoApply=true)` to apply globally to all
fields of type `X`, or `@Convert(converter=MyConverter.class)`
on a specific field. `convertToDatabaseColumn()` runs at
flush; `convertToEntityAttribute()` runs at load.

| #051 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Entity Basics, @ManyToOne, @OneToMany, EntityManager, @Embedded/@Embeddable | |
| **Used by:** | JPA at Scale, Hibernate Internals | |
| **Related:** | Inheritance Mapping, Hibernate Validator, Hibernate 6 Migration | |

---

### 🔥 The Problem This Solves

**THE ENUM ORDINAL TRAP:**

```java
// BAD: default enum persistence
@Entity
public class Order {
    @Enumerated(EnumType.ORDINAL) // DEFAULT - dangerous
    private OrderStatus status;
}

public enum OrderStatus {
    PENDING,    // stored as 0
    PROCESSING, // stored as 1
    COMPLETED,  // stored as 2
    CANCELLED   // stored as 3
}

// In DB: status=0, 1, 2, 3
// 6 months later: requirement adds "ON_HOLD" between PENDING and PROCESSING:
// enum OrderStatus { PENDING, ON_HOLD, PROCESSING, ... }
// NOW: all existing DB rows with status=1 (PROCESSING) are misread as ON_HOLD
// DATA CORRUPTION - no migration needed to break 1M rows
```

**WITH AttributeConverter:**
```java
@Converter(autoApply = true)
public class OrderStatusConverter
    implements AttributeConverter<OrderStatus, String> {

    @Override
    public String convertToDatabaseColumn(OrderStatus s) {
        return s == null ? null : s.getCode();
    }

    @Override
    public OrderStatus convertToEntityAttribute(String code) {
        return code == null ? null :
            OrderStatus.fromCode(code);
    }
}
// DB stores: "PENDING", "PROCESSING", "COMPLETED"
// Add ON_HOLD: DB gets "ON_HOLD"; old rows unchanged
// Order-independent; insertion-safe
```

---

### 📘 Textbook Definition

**`AttributeConverter<X, Y>`** is a JPA interface that
converts between entity attribute type `X` and JDBC
column type `Y`. Registered via `@Converter` annotation.

**Two methods:**

| Method | When called | Direction |
|---|---|---|
| `convertToDatabaseColumn(X)` | At flush (INSERT/UPDATE) | Java type -> JDBC type |
| `convertToEntityAttribute(Y)` | At load (SELECT) | JDBC type -> Java type |

**`@Converter` options:**

| Attribute | Default | Behavior |
|---|---|---|
| `autoApply=true` | false | Apply to ALL entity fields of type `X` automatically |
| `autoApply=false` | - | Must explicitly annotate each field with `@Convert` |

**`@Convert` on field:**
```java
@Convert(converter = MoneyConverter.class)
private Money price;

// Or disable auto-apply for a specific field:
@Convert(disableConversion = true)
private OrderStatus overrideField;
```

---

### ⏱️ Understand It in 30 Seconds

**One line:** `AttributeConverter` is a translation layer
between a Java field type and its DB column representation,
running transparently at flush and load.

**One analogy:**
> `AttributeConverter` is like a customs translator at
> the Java-DB border. Java speaks `Money(amount=100, currency="USD")`;
> the database speaks `VARCHAR "100:USD"`. The converter
> is the customs officer that translates in both directions:
> outbound (flush): `Money` -> `"100:USD"` for DB storage.
> Inbound (load): `"100:USD"` -> `Money` object for Java.
> The entity class never knows translation is happening.

**One insight:** `AttributeConverter` is often better
than `@Embedded` for simple value types that map to ONE
column. `@Embedded` maps a value type to MULTIPLE columns.
`AttributeConverter` maps a value type to ONE column.
For `Money` stored as `DECIMAL(10,2)`: use `@Embedded`
(amount + currency as separate columns). For `Money`
stored as `"100.00 USD"` in one column: use `AttributeConverter`.

---

### 🔩 First Principles Explanation

**EXECUTION ORDER:**

```
FLUSH (INSERT/UPDATE):
  Entity.price = Money{amount=100, currency="USD"}
  -> JPA calls: converter.convertToDatabaseColumn(price)
  -> Returns: "100.00:USD"
  -> JDBC preparedStatement.setString(col, "100.00:USD")
  -> SQL: INSERT INTO products(price) VALUES('100.00:USD')

LOAD (SELECT):
  SQL: SELECT price FROM products WHERE id=1
  -> ResultSet: price = "100.00:USD"
  -> JPA calls: converter.convertToEntityAttribute("100.00:USD")
  -> Returns: Money{amount=100, currency="USD"}
  -> entity.price = Money{amount=100, currency="USD"}

JPQL/Criteria query on converted field:
  "SELECT p FROM Product p WHERE p.price = :price"
  -> price parameter: Money{amount=100, currency="USD"}
  -> JPA calls convertToDatabaseColumn on PARAMETER too
  -> Converted to "100.00:USD" before query execution
  -> WHERE price = '100.00:USD'
  NOTE: The converter is applied to parameters, not just entities.
```

---

### 🧪 Thought Experiment

**NULL HANDLING - THE SILENT FAILURE:**

```java
// Converter with missing null check:
@Override
public String convertToDatabaseColumn(OrderStatus s) {
    return s.getCode(); // NPE if s is null
}

// Entity: new Order() with no status set -> status is null
// At INSERT: converter called with null
// -> NullPointerException thrown
// -> Transaction rolls back
// -> Not obvious: error happens in converter, not in application code

// ALWAYS handle null explicitly:
@Override
public String convertToDatabaseColumn(OrderStatus s) {
    return s == null ? null : s.getCode();
}

@Override
public OrderStatus convertToEntityAttribute(String code) {
    return code == null ? null
        : OrderStatus.fromCode(code);
}

// Also: what if unknown code in DB?
// "UNKNOWN_STATUS" -> OrderStatus.fromCode fails?
// Add default/fallback:
return Arrays.stream(OrderStatus.values())
    .filter(v -> v.getCode().equals(code))
    .findFirst()
    .orElseThrow(() -> new IllegalArgumentException(
        "Unknown OrderStatus code: " + code));
```

---

### 🧠 Mental Model / Analogy

> `AttributeConverter` is the "adapter pattern" applied
> to the Java-DB interface. The JPA entity (client) uses
> a domain type (`Money`, `OrderStatus`). The database
> (service) uses a different type (`VARCHAR`, `SMALLINT`).
> The converter (adapter) makes the two types compatible
> without modifying either. This is the classic Gang of
> Four Adapter pattern applied to database serialization.
> The same design appears in: JSON serializers
> (`JsonSerializer<Money>` -> JSON), HTTP message converters
> (`HttpMessageConverter<Money>` -> HTTP body), Kafka
> serializers (`Serializer<Money>` -> bytes).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`AttributeConverter` converts a Java field type to a DB
column type automatically. The entity always uses the
rich Java type; the DB stores a simpler representation.

**Level 2 - Enum converter (junior developer):**
```java
// Convert enum to stable String code (not ordinal):
@Converter(autoApply = true)
public class OrderStatusConverter
    implements AttributeConverter<OrderStatus, String> {

    @Override
    public String convertToDatabaseColumn(OrderStatus s) {
        return s == null ? null : s.name();
        // name() = enum constant name as String
        // Stable; not ordinal-based
    }

    @Override
    public OrderStatus convertToEntityAttribute(String v) {
        return v == null ? null
            : OrderStatus.valueOf(v);
    }
}
```

**Level 3 - Custom value type converter (mid-level engineer):**
```java
// Map Money value type to DECIMAL column
@Converter
public class MoneyConverter
    implements AttributeConverter<Money, BigDecimal> {

    // Store only the amount; currency enforced by context
    @Override
    public BigDecimal convertToDatabaseColumn(Money m) {
        return m == null ? null : m.getAmount();
    }

    @Override
    public Money convertToEntityAttribute(BigDecimal v) {
        return v == null ? null : Money.of(v, "USD");
        // Currency must be known from context
    }
}
// Field usage:
@Convert(converter = MoneyConverter.class)
@Column(name = "price", precision = 10, scale = 2)
private Money price;
```

**Level 4 - Encrypted field converter (senior engineer):**
```java
@Converter
public class EncryptedStringConverter
    implements AttributeConverter<String, String> {

    private final EncryptionService enc;

    public EncryptedStringConverter(
        EncryptionService enc) {
        this.enc = enc;
    }

    @Override
    public String convertToDatabaseColumn(String plain) {
        return plain == null ? null : enc.encrypt(plain);
    }

    @Override
    public String convertToEntityAttribute(String cipher) {
        return cipher == null ? null : enc.decrypt(cipher);
    }
}

// Usage: SSN field stored encrypted in DB
@Convert(converter = EncryptedStringConverter.class)
@Column(name = "ssn", length = 256)
private String ssn;
// DB: ssn = "AES256:abc123..."
// Java: ssn = "123-45-6789"
```

Note: for `@Converter` that needs Spring beans (like
`EncryptionService`), the converter must be registered as
a Spring bean AND JPA must be configured to use the
Spring-managed converter instance. Hybrid setup required:
`@Converter(autoApply=true)` + Spring `@Bean` or
component registration in JPA configuration.

**Level 5 - Converter and Hibernate 6 (staff engineer):**
Hibernate 6 introduces `@JavaTypeRegistration` and
`@JdbcTypeRegistration` for deeper type registration.
`AttributeConverter` still works in Hibernate 6, but
Hibernate's own `BasicType` registration system is more
powerful for complex cases (custom JDBC type mappings,
e.g., PostgreSQL `jsonb`, `hstore`, `uuid`). For
`PostgreSQL jsonb`: use `@Type(JsonBinaryType.class)`
from `hibernate-types-60` (Vlad Mihalcea library) rather
than an AttributeConverter. For simple Java-to-column
conversions: `AttributeConverter` remains the cleanest JPA
standard approach.

---

### ⚙️ How It Works (Mechanism)

**QUERYING WITH CONVERTED FIELD:**

```java
// Repository method that queries a converted enum field:
@Repository
public interface OrderRepository
    extends JpaRepository<Order, Long> {

    // Spring Data translates this to:
    // WHERE status = ? (with converter applied to "PROCESSING")
    List<Order> findByStatus(OrderStatus status);

    // JPQL - converter applied to :status parameter:
    @Query("SELECT o FROM Order o WHERE o.status = :status")
    List<Order> findByStatusJpql(
        @Param("status") OrderStatus status);
}

// IMPORTANT: JPQL queries use the JAVA field name "status"
// (not the column name). JPA applies the converter to the
// parameter before generating SQL.

// CAUTION with native queries:
@Query(value = "SELECT * FROM orders WHERE status = ?1",
    nativeQuery = true)
List<Order> findByStatusNative(String statusCode);
// Native queries bypass converters!
// Must pass the CONVERTED value (e.g., "PROCESSING"),
// not the enum: findByStatusNative("PROCESSING")
// NOT: findByStatusNative(OrderStatus.PROCESSING) - won't convert
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MULTIPLE CONVERTERS ON ONE ENTITY:**

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id @GeneratedValue Long id;

    String name;

    // Encrypted PII:
    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "ssn")
    private String ssn;

    // Enum as string code:
    // Auto-applied by @Converter(autoApply=true):
    private EmploymentType employmentType;

    // Custom value type:
    @Convert(converter = MoneyConverter.class)
    @Column(name = "salary")
    private Money salary;

    // Comma-separated list -> Java List<String>:
    @Convert(converter = StringListConverter.class)
    @Column(name = "permissions")
    private List<String> permissions;
}
```

---

### 💻 Code Example

**Example 1 - StringList converter:**

```java
// Store List<String> as comma-separated VARCHAR
@Converter(autoApply = false)
public class StringListConverter
    implements AttributeConverter<List<String>, String> {

    private static final String DELIMITER = ",";

    @Override
    public String convertToDatabaseColumn(
        List<String> list) {
        if (list == null || list.isEmpty()) return null;
        return String.join(DELIMITER, list);
    }

    @Override
    public List<String> convertToEntityAttribute(
        String csv) {
        if (csv == null || csv.isBlank()) {
            return new ArrayList<>();
        }
        return Arrays.asList(csv.split(DELIMITER));
    }
}
// DB: permissions = "READ,WRITE,ADMIN"
// Java: permissions = List.of("READ","WRITE","ADMIN")
// NOTE: Cannot query individual values efficiently.
// For queryable lists: use @ElementCollection instead.
```

**Example 2 - Testing the converter in isolation:**

```java
class MoneyConverterTest {

    private final MoneyConverter converter =
        new MoneyConverter();

    @Test
    void roundTrip_convertsCorrectly() {
        Money original = Money.of(
            new BigDecimal("99.99"), "USD");
        BigDecimal column =
            converter.convertToDatabaseColumn(original);
        Money restored =
            converter.convertToEntityAttribute(column);
        assertThat(restored.getAmount())
            .isEqualByComparingTo(original.getAmount());
    }

    @Test
    void nullInput_returnsNull() {
        assertThat(converter.convertToDatabaseColumn(null))
            .isNull();
        assertThat(converter.convertToEntityAttribute(null))
            .isNull();
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Best for | Limitation |
|---|---|---|
| `@Enumerated(EnumType.STRING)` | Simple enum to String | No custom codes; enum name = DB value |
| `AttributeConverter` | Any custom type, custom enum codes, encryption | No DB-level queries on converted values (can't use LIKE, range) |
| `@Embedded` | Value type with multiple DB columns | Multiple columns; more schema space |
| `@Type` (Hibernate-specific) | PostgreSQL `jsonb`, `hstore`, array types | Hibernate-specific; not portable JPA |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "AttributeConverter works with native queries" | NO - native queries (`nativeQuery=true`) bypass JPA, including converters. For native queries, you must pass the already-converted value (e.g., the String code, not the enum). Use JPQL or Criteria API for automatic converter application. |
| "`autoApply=true` applies globally to all entities" | `autoApply=true` applies to all entity fields of the matching Java type `X` in the persistence unit. It does NOT apply to embedded objects, non-entity classes, or Spring Data projections. Always test with the actual entity, not just unit test the converter. |
| "Sorting/filtering on converted columns is always correct" | For `AttributeConverter`, the DB stores the CONVERTED value. Sorting `WHERE status > 'PROCESSING'` does string comparison, not enum ordinal comparison. If sort order matters in queries, design the converter's output to be lexicographically sortable (e.g., use status codes that sort alphabetically in the desired order) or use a different DB type. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Converter Not Applied to Native Query**

**Symptom:** `findByStatusNative(OrderStatus.PROCESSING)`
returns empty results even though rows with
`status='PROCESSING'` exist.
**Root Cause:** Native queries don't pass through JPA's
converter mechanism. The enum object is passed as-is to
the JDBC driver, which can't convert it to a String.
**Diagnosis:**
```java
// Enable SQL logging to see the actual parameter:
// Expected in SQL: WHERE status = 'PROCESSING'
// Actual: WHERE status = <enum toString representation>
// Or: BindingException: No dialect mapping for JDBC type
```
**Fix:**
```java
// Explicitly convert to string before native query:
@Query(value = "SELECT * FROM orders WHERE status = ?1",
    nativeQuery = true)
List<Order> findByStatusNative(String statusCode);

// Call with:
orderRepo.findByStatusNative(
    OrderStatus.PROCESSING.getCode());
// NOT: orderRepo.findByStatusNative(OrderStatus.PROCESSING)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-041 - @Embedded and @Embeddable]] - alternative
  for value types that map to multiple columns
- [[JPH-006 - Entity Basics]] - understanding basic entity
  field mapping before adding custom converters

**Builds On This (learn these next):**
- [[JPH-058 - Hibernate Internals]] - Hibernate's type
  system and how `AttributeConverter` fits within it

**Related:**
- [[JPH-044 - Hibernate Validator]] - bean validation
  on entity fields applies BEFORE converter conversion
- [[JPH-060 - Hibernate 6 Migration]] - Hibernate 6
  enhanced type registration; interaction with converters

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTERFACE    │ AttributeConverter<JavaType, DbType>      │
│ METHODS      │ convertToDatabaseColumn(X) -> Y  (flush) │
│              │ convertToEntityAttribute(Y) -> X  (load) │
├──────────────┼───────────────────────────────────────────┤
│ REGISTER     │ @Converter(autoApply=true) -> all X fields│
│              │ @Convert(converter=X.class) -> one field  │
├──────────────┼───────────────────────────────────────────┤
│ MUST DO      │ Handle null in both conversion methods    │
├──────────────┼───────────────────────────────────────────┤
│ NATIVE QUERY │ Converters NOT applied; pass converted    │
│ GOTCHA       │ value directly (e.g., String code)        │
├──────────────┼───────────────────────────────────────────┤
│ USE CASES    │ Enum -> String code (NOT ordinal)         │
│              │ Custom value type -> column               │
│              │ Encrypted field -> cipher text            │
│              │ List<String> -> comma-separated varchar   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "AttributeConverter<X,Y>: converts entity │
│              │ field type X to DB column type Y at       │
│              │ flush/load. Use for enums-as-codes,       │
│              │ custom types, encryption."                │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `AttributeConverter<X,Y>`: Java field type X -> DB type Y;
   implemented in 2 methods: `convertToDatabaseColumn` and
   `convertToEntityAttribute`
2. Always handle null in both methods; `autoApply=true` applies
   globally to all entity fields of type X
3. Native queries bypass converters - must pass already-converted
   value for native query parameters

**Interview one-liner:** `AttributeConverter<X,Y>` converts between
entity field type `X` and DB column type `Y` at flush/load.
Use `@Converter(autoApply=true)` for global application or
`@Convert(converter=...)` per field. Critical uses: enums stored
as String codes (not fragile ordinals), value types, encrypted fields.
Native queries bypass converters - must pass converted values directly.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The Adapter pattern
(converting between incompatible interfaces) appears at
every boundary in software: `AttributeConverter` at the
Java-DB boundary, `JsonSerializer`/`JsonDeserializer` at
the Java-JSON boundary, `HttpMessageConverter` at the
Java-HTTP boundary, Kafka's `Serializer`/`Deserializer`
at the Java-bytes boundary. The pattern is always the same:
two directions (in and out), null handling, and error
handling for unrecognized input values. Writing any
serialization adapter: (1) handle null, (2) handle invalid
input with a clear error message, (3) unit test the
round-trip (Java -> Serialized -> Java = original).

---

### 💡 The Surprising Truth

`AttributeConverter` converts query PARAMETERS too, not
just entity field values. When you write a JPQL query
`WHERE o.status = :status` and pass an `OrderStatus` enum,
JPA automatically calls `convertToDatabaseColumn(status)`
on the parameter before binding it to the PreparedStatement.
This means your converter must handle the same input types
as query parameters - which is normally fine but matters
when the converter is used in Specifications or Criteria API
queries where parameters are typed. The implication:
a converter that relies on entity-level state (e.g., reading
another field to determine how to convert a value) CANNOT
be used, because query parameter conversion has no entity
context - only the field value itself. Converters must be
pure functions of their input value.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** an `AttributeConverter` for an enum that
   stores stable String codes instead of ordinals
2. **EXPLAIN** the difference between `autoApply=true` and
   per-field `@Convert` and when to use each
3. **HANDLE** null correctly in both conversion methods
4. **EXPLAIN** why native queries bypass converters and
   how to work around this limitation
5. **TEST** the converter in isolation with a unit test
   covering round-trip conversion and null handling

---

### 🎯 Interview Deep-Dive

**Q1: Why is `@Enumerated(EnumType.ORDINAL)` dangerous
and how do you fix it using `AttributeConverter`?**
*Why they ask:* Tests practical JPA field mapping safety.
*Strong answer includes:*
- `EnumType.ORDINAL` stores 0, 1, 2... based on enum declaration order
- Adding a new enum constant in the middle shifts all subsequent ordinals
- Existing DB rows now map to the wrong enum values - DATA CORRUPTION
- Fix: use `EnumType.STRING` (stores `name()`) or custom `AttributeConverter`
  with `getCode()`/`fromCode()` for stable, business-meaningful codes
- Converter example: `OrderStatus.COMPLETED` -> `"COMP"` (never changes
  even if enum is renamed or reordered)

**Q2: Does `AttributeConverter` apply to parameters in
JPQL queries? What about native queries?**
*Why they ask:* Tests understanding of converter scope.
*Strong answer includes:*
- JPQL/JPQL-Criteria: YES - JPA calls `convertToDatabaseColumn()`
  on JPQL parameters for fields that have a converter. Transparent.
- Spring Data derived methods (`findByStatus`): YES - Spring Data
  generates JPQL; same converter application
- Native queries (`nativeQuery=true`): NO - bypasses JPA type system
  including converters. Must pass the already-converted value
  (e.g., `"COMPLETED"` string, not `OrderStatus.COMPLETED` enum)
- Practical implication: native query parameters must be typed to
  match the DB column type; create a wrapper method that does the
  conversion explicitly before calling the native query