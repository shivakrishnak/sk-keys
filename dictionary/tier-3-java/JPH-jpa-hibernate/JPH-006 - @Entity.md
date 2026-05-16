---
id: JPH-006
title: "@Entity"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★☆☆
depends_on: JPH-002, JPH-004
used_by: JPH-007, JPH-008, JPH-011, JPH-013
related: JPH-008, JPH-041, JPH-040
tags:
  - java
  - database
  - jpa
  - foundational
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /jpa-hibernate/entity-annotation/
---

# JPH-006 - @Entity

⚡ **TL;DR** - `@Entity` is the JPA annotation that declares
a Java class as a persistent type mapped to a database table,
making the JPA provider responsible for its storage lifecycle.

| #006 | Category: JPA & Hibernate | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | What is ORM, Hibernate as JPA Implementation | |
| **Used by:** | @Id and @GeneratedValue, @Table and @Column, EntityManager, Entity Lifecycle | |
| **Related:** | @Table and @Column, @Embedded and @Embeddable, Inheritance Mapping Strategies | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a way to declare which Java classes represent
persistent data, the ORM provider has no signal for what
to map to the database. Every class that touches the
persistence layer would need manual registration, explicit
DDL, and hand-written mapping code. The ORM loses its core
ability to automate because it does not know where to start.

**THE BREAKING POINT:**
Before JPA standardised `@Entity` (and before Hibernate used
XML mapping files), teams maintained a separate XML descriptor
(`hibernate.cfg.xml` / `hbm.xml`) listing every persistent
class and its field mappings. Adding a new entity meant
editing XML in multiple files, redeploying the mapping
descriptor, and hoping nothing was missed. Schema and code
diverged silently.

**THE INVENTION MOMENT:**
JPA (and Hibernate before it) moved the mapping declaration
to the source file itself: annotate the class with `@Entity`
and the ORM provider scans the classpath, finds every annotated
class, builds the metadata model at startup, and manages the
mapping automatically. The class IS the mapping.

---

### 📘 Textbook Definition

**`@Entity`** is a Jakarta Persistence annotation (package
`jakarta.persistence`) that marks a Java class as a JPA
entity - a persistent type that is mapped to a relational
database table and whose lifecycle (persist, merge, remove,
refresh) is managed by the JPA `EntityManager`. An entity
class must meet four requirements: it must be annotated with
`@Entity`, have a public or protected no-argument constructor,
not be declared `final` (so Hibernate can subclass it for
proxy generation), and have a field annotated with `@Id` or
a mapped superclass that provides one.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Entity` tells JPA "this class is a row
in a database table - manage its lifecycle."

**One analogy:**
> `@Entity` is like a passport. A Java class without
> `@Entity` is a person without ID - they exist but the
> border control (the JPA provider) does not recognise them.
> `@Entity` is the registration that makes the class
> visible to the persistence system.

**One insight:** `@Entity` is not just a label - it triggers
a cascade of JPA machinery at startup. The provider scans
for every `@Entity` class, builds a metadata model, validates
or creates the schema, registers proxy factories, and sets up
dirty checking. Everything in JPA depends on this annotation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every `@Entity` class maps to exactly one primary table
   (by default, the class name; customised via `@Table`)
2. Every `@Entity` class must have an `@Id` - either on a
   field directly or inherited from a `@MappedSuperclass`
3. `@Entity` classes must not be `final` - Hibernate
   generates runtime subclass proxies for lazy loading;
   `final` prevents subclassing
4. The no-argument constructor must be accessible by the
   JPA provider (at minimum `protected`)
5. Non-persistent fields must be marked `@Transient` or
   they will be mapped automatically (field-access strategy)

**DERIVED DESIGN:**
When Hibernate scans a `@Entity` class, it:
1. Maps class name to table name (or uses `@Table(name=...)`)
2. Maps each non-`@Transient` field to a column
3. Registers a `PersisterCreator` for the entity type
4. Creates a proxy subclass via Byte Buddy for lazy loading
5. Stores a per-entity snapshot model for dirty checking

**THE TRADE-OFFS:**
**Gain:** Declarative persistence with zero XML;
the class definition is the single source of truth;
classpath scanning eliminates manual registration.
**Cost:** Entity classes must follow Hibernate's
constraints (non-final, no-arg constructor); the class
design is influenced by persistence concerns; adding
`@Entity` to an existing class may require changes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Some marker must tell the ORM which classes
to manage - that is irreducible.
**Accidental:** XML hbm mapping files were the original
approach. Annotations move the declaration to the source,
eliminating the synchronisation burden between Java files
and XML descriptors.

---

### 🧪 Thought Experiment

**SETUP:**
You have a `Product` class representing a product in an
e-commerce system. Without `@Entity`, it is just a regular
Java class.

**WHAT HAPPENS WITHOUT @Entity:**
`em.find(Product.class, 1L)` throws
`IllegalArgumentException: Unknown entity: class Product`.
`em.persist(new Product())` throws the same. The JPA provider
simply does not know this class exists as a persistent type.

**WHAT HAPPENS WITH @Entity:**

```java
@Entity
public class Product {
    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private BigDecimal price;
    // no-arg constructor required
    protected Product() {}
    public Product(String name, BigDecimal p) {
        this.name = name; this.price = p;
    }
}
```

Now `em.find(Product.class, 1L)` generates
`SELECT * FROM Product WHERE id=1`. `em.persist(product)`
generates `INSERT INTO Product (name, price) VALUES (?, ?)`.
The class is a first-class citizen of the persistence layer.

**THE INSIGHT:** `@Entity` is the single registration act
that makes a Java class visible to the entire JPA machinery.
Without it, the class is invisible to the ORM - with it, every
JPA feature (lifecycle, caching, querying, relationships) is
available to the class.

---

### 🧠 Mental Model / Analogy

> A Java class without `@Entity` is like a building that
> doesn't appear on the city planning map. Fire fighters,
> postal workers, and utility companies don't know it exists.
> `@Entity` puts the building on the map - after that, all
> city services (JPA features) can interact with it.

- "City planning map" - JPA provider's entity registry
- "Building" - Java class
- "Fire fighters, postal workers" - EntityManager operations
- "Appearing on the map" - `@Entity` annotation
- "City services" - persist, find, query, cache, audit

Where this analogy breaks down: a building always exists on
the map from the moment it is built. In JPA, a class only
appears on the "map" when annotated with `@Entity` -
it is an opt-in, not automatic.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Entity` is the annotation that tells JPA "this Java class
represents data in the database." Without it, JPA ignores
the class completely.

**Level 2 - How to use it (junior developer):**
Add `@Entity` above the class declaration. Add `@Id` to the
primary key field. Ensure the class has a no-arg constructor
(can be `protected`). The class name becomes the default table
name. Fields become columns. Use `@Table(name = "...")` and
`@Column(name = "...")` to override defaults.

**Level 3 - How it works (mid-level engineer):**
At startup, Hibernate's `EntityManagerFactory` creation
triggers a classpath scan for `@Entity` classes. For each
entity, Hibernate builds a `PersistentClass` metadata model
describing the table, columns, primary key, and relationships.
It then validates or generates the schema and creates a proxy
subclass via Byte Buddy for lazy loading support.

**Level 4 - Why it was designed this way (senior/staff):**
The `@Entity` constraint that classes must be non-final and
have a no-arg constructor is driven entirely by Hibernate's
proxy generation strategy. Lazy loading works by returning
a proxy subclass instead of the real entity; when the proxy
is first accessed, it loads from the database. `final` classes
cannot be subclassed; missing no-arg constructors prevent
the proxy from being instantiated. Hibernate 6 uses Byte Buddy
(replacing the older javassist and cglib) for more reliable
proxy generation with Java 17+ sealed classes support.

**Level 5 - Mastery (distinguished engineer):**
The non-final constraint is a persistent source of tension
with good OOP design (Effective Java: "design for inheritance
or prohibit it"). Three approaches: (1) accept the constraint
and design entity classes specifically for persistence;
(2) use `@Embeddable` value objects for immutable sub-parts;
(3) use Hibernate 6's `@Proxy(proxyClass=...)` or static
weaving (EclipseLink) to avoid runtime subclassing entirely.
An alternative is using records for projections (non-entities)
and accepting that full entities need the proxy-compatible design.

**Expert Thinking Cues:**
- Ask: "Is every field in this `@Entity` class that is not
  persisted marked `@Transient`?" - unintentionally persisted
  fields are a silent data corruption vector
- Watch: `@Entity` on an abstract class combined with
  inheritance strategies creates polymorphic loading
  behaviour that must be understood
- Know: `@MappedSuperclass` is NOT `@Entity` - it shares
  mapping data but does not create its own table or
  registration in the entity registry

---

### ⚙️ How It Works (Mechanism)

**Entity Lifecycle at Startup:**

```
┌─────────────────────────────────────────────┐
│        @ENTITY PROCESSING AT STARTUP        │
├─────────────────────────────────────────────┤
│ 1. EntityManagerFactory creation            │
│    - Classpath scanned for @Entity classes  │
│    - Each class inspected for @Id           │
│    - Column mappings extracted from fields  │
│                                             │
│ 2. Metadata Model Built                     │
│    - EntityPersister per @Entity class      │
│    - Table name, column names, types        │
│    - Relationship graph constructed         │
│                                             │
│ 3. Schema Management                        │
│    - validate: checks schema matches model  │
│    - create: drops + recreates schema       │
│    - update: adds missing columns           │
│                                             │
│ 4. Proxy Factory Created                    │
│    - Byte Buddy generates subclass proxy    │
│    - Proxy returned for lazy references     │
│    - Real class loaded on first access      │
└─────────────────────────────────────────────┘
```

**Field Access vs. Property Access:**
By default, Hibernate accesses fields directly (field access)
if `@Id` is on a field. If `@Id` is on a getter, Hibernate
uses property access (calls getters/setters). Mixing the two
in an entity hierarchy causes unpredictable mapping; keep one
access strategy per entity.

**Entity State Machine:**

```
NEW (transient)
    |
    | em.persist()
    v
MANAGED (tracked by session)
    |
    | em.detach() / session close
    v
DETACHED (copy outside session)
    |
    | em.remove()
    v
REMOVED (scheduled for DELETE)
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
A `@Entity` class instance is NOT thread-safe when managed
by a session. Two threads must never share the same entity
instance across different sessions. The `EntityManager` session
is per-thread; entity instances should not be passed between
threads while in managed state.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Application startup
    |
    v
[ @SpringBootApplication ]
    |  triggers EntityManagerFactory
    v
[ Classpath scanner ]
    |  finds @Entity classes
    v
[ Metadata builder ] <- YOU ARE HERE
    |  maps class -> table, fields -> columns
    v
[ Schema management ]
    |  validates or creates tables
    v
[ EntityManagerFactory ready ]

--- Request time ---

em.find(Product.class, 42L)
    |
    v
[ First-level cache check: miss ]
    |
    v
[ SELECT * FROM product WHERE id=42 ]
    |
    v
[ ResultSet -> Product entity ]
    |  snapshot stored
    v
[ Return managed entity ]
```

**FAILURE PATH:**
If `@Entity` is applied to a class without `@Id`, Hibernate
throws `AnnotationException: No identifier specified` at
startup, preventing the application from starting. If the class
is `final`, proxy creation fails with a `ProxyGenerationException`
at startup.

**WHAT CHANGES AT SCALE:**
With 100+ entity classes, startup time grows because each
entity requires schema validation against the database. Use
`spring.jpa.hibernate.ddl-auto=validate` in production and
`Flyway`-managed schema to keep startup fast. Avoid
`ddl-auto=update` - it scans every column of every table.

---

### 💻 Code Example

**Example 1 - BAD: @Entity class that breaks proxy generation:**

```java
// BAD: final class prevents Hibernate proxy subclass
@Entity
public final class Product {
    @Id
    private Long id;
    private String name;
    // Hibernate cannot generate lazy-load proxy
    // Throws: ProxyGenerationException at startup
}
```

**Example 2 - GOOD: minimal correct @Entity:**

```java
// GOOD: non-final, has no-arg constructor
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    // Required by JPA spec
    protected Product() {}

    // Business constructor
    public Product(String name,
                   BigDecimal price) {
        this.name = name;
        this.price = price;
    }
    // getters / setters...
}
```

**Example 3 - @Transient for non-persistent fields:**

```java
@Entity
public class Customer {

    @Id
    private Long id;
    private String firstName;
    private String lastName;

    // BAD: without @Transient, Hibernate tries
    // to map this to a "fullName" column -> fails
    // private String fullName =
    //     firstName + " " + lastName;

    // GOOD: mark computed fields @Transient
    @Transient
    private String fullName;

    // Or use a method (Hibernate ignores methods
    // that are not getters for @Column fields)
    public String getDisplayName() {
        return firstName + " " + lastName;
    }
}
```

**Example 4 - @MappedSuperclass vs @Entity:**

```java
// @MappedSuperclass: shares columns, no own table
@MappedSuperclass
public abstract class BaseEntity {

    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}

// @Entity: inherits columns, has own table
@Entity
@Table(name = "products")
public class Product extends BaseEntity {
    private String name;
    // id and createdAt columns inherited
}
```

---

### ⚖️ Comparison Table

| Annotation | Creates Table | JPA Managed | Can Query Directly | Use Case |
|---|---|---|---|---|
| `@Entity` | Yes | Yes | Yes | Persistent domain objects |
| `@MappedSuperclass` | No | Partial | No (via subclass) | Shared columns without own table |
| `@Embeddable` | No | Via owner | No | Value objects embedded in entity |
| `@Transient` | N/A | No | N/A | Fields to exclude from mapping |

**How to choose:** Use `@Entity` for any class that represents
a distinct database row with its own identity. Use
`@MappedSuperclass` for shared audit fields (createdAt,
updatedAt) inherited by multiple entities. Use `@Embeddable`
for value types (Address, Money) embedded in an entity's table.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Any Java class with @Entity will just work" | The class must be non-final, have a no-arg constructor (at minimum protected), and have an @Id field. Violating any of these causes a startup failure or broken lazy loading. |
| "@MappedSuperclass is the same as @Entity" | `@MappedSuperclass` shares column mappings but creates no table and cannot be queried directly. `@Entity` creates a table and is a first-class JPA-managed type. |
| "All fields in an @Entity class are automatically persisted" | Fields marked `@Transient` or `static` or `final` are excluded. ALL other non-transient non-static fields are mapped by default - missing `@Transient` on a computed field causes a mapping error. |
| "@Entity classes should follow standard OOP immutability rules" | JPA requires a no-arg constructor and non-final class, both of which conflict with OOP immutability guidelines. Entity classes are persistence objects, not pure domain objects. Consider separating domain objects (immutable) from entity objects (JPA-compatible). |
| "You need @Column on every field" | `@Column` is optional. Without it, Hibernate maps the field to a column with the same name. Only add `@Column` when you need to override defaults (name, nullable, length, precision). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Missing No-Arg Constructor**

**Symptom:** `org.hibernate.InstantiationException: No default
constructor for entity: Product` at application startup or
when loading an entity.
**Root Cause:** Hibernate cannot instantiate the proxy or
hydrate a fresh entity instance without a no-arg constructor.
**Diagnostic:**

```bash
grep "InstantiationException" application.log
# Shows the entity class that is missing the constructor
```

**Fix:**

```java
// BAD: only the business constructor
@Entity
public class Product {
    public Product(String name, BigDecimal p) {
        this.name = name; this.price = p;
    }
}

// GOOD: add protected no-arg constructor
@Entity
public class Product {
    protected Product() {} // JPA required
    public Product(String name, BigDecimal p) {
        this.name = name; this.price = p;
    }
}
```

**Prevention:** Add `protected [ClassName]() {}` as a comment
in your entity template: "JPA requires this."

---

**Failure Mode 2: Accidental Column Mapping**

**Symptom:** `org.hibernate.HibernateException: Could not
execute JDBC batch update` or `Unknown column 'full_name'
in 'field list'` when saving an entity.
**Root Cause:** A computed or helper field was added to the
entity without `@Transient`, causing Hibernate to try to
INSERT/UPDATE a column that does not exist.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Look for unexpected column names in INSERT/UPDATE SQL
```

**Fix:**

```java
// BAD: computed field incorrectly mapped
@Entity
public class Customer {
    private String displayName =
        "default"; // Hibernate maps this!
}

// GOOD: annotate non-persistent fields
@Entity
public class Customer {
    @Transient
    private String displayName;
}
```

**Prevention:** Review all non-annotated fields in `@Entity`
classes; every field that is NOT a database column needs
`@Transient`.

---

**Failure Mode 3: final Entity Class Breaking Lazy Loading**

**Symptom:** `@OneToMany(fetch = FetchType.LAZY)` relationship
is always eagerly loaded even when `LAZY` is configured; or
`ClassCastException` when casting the loaded entity.
**Root Cause:** `final` entity class prevents Hibernate from
generating a proxy subclass; Hibernate falls back to eager
loading or throws at proxy creation time.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# If lazy @ManyToOne always triggers a second SELECT
# immediately, the proxy is not being created
logging.level.org.hibernate.engine.internal.StatefulPersistenceContext=DEBUG
```

**Fix:** Remove `final` from the entity class declaration.
If immutability is required for domain reasons, separate the
domain object from the JPA entity.
**Prevention:** Use a code analysis rule (PMD or custom
Checkstyle rule) to flag `final` classes annotated with
`@Entity`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-002 - What is ORM (Object-Relational Mapping)]] -
  what the JPA provider does with `@Entity` classes
- [[JPH-004 - Hibernate as JPA Implementation]] - the engine
  that processes `@Entity` annotations at startup

**Builds On This (learn these next):**
- [[JPH-007 - @Id and @GeneratedValue]] - required companion
  to `@Entity` - every entity needs an identifier
- [[JPH-008 - @Table and @Column]] - customising the default
  table and column mappings established by `@Entity`
- [[JPH-011 - EntityManager]] - the API that manages the
  lifecycle of `@Entity` instances
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  the four states an `@Entity` instance can be in

**Alternatives / Comparisons:**
- [[JPH-041 - @Embedded and @Embeddable]] - for value types
  that are part of an entity but not entities themselves
- [[JPH-040 - Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS)]] -
  when one `@Entity` extends another

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Annotation declaring a Java class as a   │
│              │ JPA-managed persistent type               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Tells the JPA provider which classes to  │
│ SOLVES       │ map to tables and manage lifecycle for   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ @Entity triggers the entire JPA machinery:│
│              │ scan, proxy, schema, dirty check, cache  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ A Java class represents a row in a DB    │
│              │ table with its own identity (@Id)         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ The type is a value object without its   │
│              │ own identity -> use @Embeddable instead  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ final entity class; missing no-arg       │
│              │ constructor; missing @Transient on helpers│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Declarative persistence convenience vs.  │
│              │ class design constraints (non-final, etc) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Entity is a passport: without it, JPA  │
│              │ does not recognise the class exists"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Id -> @Table -> EntityManager -> Lifecycle│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@Entity` classes must be non-final and have a no-arg
   constructor (at minimum `protected`)
2. Every non-transient, non-static field is mapped to a
   column automatically - use `@Transient` for computed
   or helper fields
3. `@Entity` vs `@MappedSuperclass` vs `@Embeddable`:
   `@Entity` = own table + identity; `@MappedSuperclass` =
   shared columns, no table; `@Embeddable` = value type

**Interview one-liner:** `@Entity` is the JPA annotation that
registers a Java class as a persistent type mapped to a
database table. The JPA provider scans for `@Entity` classes
at startup, builds the mapping metadata, and manages their
lifecycle (persist, find, merge, remove). Requirements: the
class must be non-final (Hibernate generates proxy subclasses
for lazy loading) and have a no-arg constructor.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Annotation-driven
registration shifts the source of truth from external
descriptors (XML, configuration files) to the source code
itself. The class declares its own behaviour directly,
eliminating synchronisation lag between code and configuration.
This principle appears in every modern Java framework.

**Where else this pattern appears:**
- **Spring `@Component`/`@Service`/`@Repository`** - same
  declarative registration pattern; Spring scans for these
  annotations and registers beans, same as JPA scans for
  `@Entity`
- **JAX-RS `@Path`** - REST endpoint registration via
  annotation; no XML descriptor needed
- **JUnit 5 `@Test`** - method registration via annotation
  instead of external test suite descriptors

**Industry applications:**
- Domain-driven design at scale: entities in DDD are
  domain concepts with identity and lifecycle, which maps
  directly to `@Entity` - the annotation formalises the
  DDD entity pattern in code
- Microservices: each bounded context has its own set of
  `@Entity` classes and its own `EntityManagerFactory`,
  preventing entity coupling across service boundaries

---

### 💡 The Surprising Truth

The JPA requirement that entity classes cannot be `final`
was almost removed from the specification in JPA 2.1.
The specification committee considered requiring lazy
loading through composition (injecting a loader) rather
than proxy subclassing, which would have made `final`
classes legal. The change was rejected primarily because
it would have broken backward compatibility with the
millions of `@Entity` classes already in production
that relied on proxy behaviour. The "non-final" constraint
is therefore a legacy design decision baked in for
compatibility, not a technical necessity.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the three requirements for a valid `@Entity`
   class (non-final, no-arg constructor, `@Id` field) and
   explain WHY each requirement exists in terms of Hibernate
   internals (proxy generation, instantiation, identity)
2. **DEBUG** a startup failure where `@Entity` processing
   fails - identify whether it is a missing no-arg
   constructor, missing `@Id`, or a `final` class issue
   from the exception message
3. **DECIDE** whether a given Java class should use
   `@Entity`, `@MappedSuperclass`, or `@Embeddable` based
   on whether it has its own identity, shares columns,
   or is a value type
4. **BUILD** a minimal valid `@Entity` class from memory:
   `@Entity`, `@Table`, `@Id`, `@GeneratedValue`,
   `protected` no-arg constructor, and `@Column` where
   needed
5. **EXTEND** the `@Entity` pattern to an inheritance
   hierarchy and explain what `@Inheritance` strategy
   is needed and why `@Entity` alone is insufficient
   for polymorphic loading

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE C - Design Trade-off):** JPA requires entity
classes to be non-final to support proxy-based lazy loading.
This conflicts with Effective Java's recommendation to make
classes final unless explicitly designed for extension.
How would you reconcile these two guidelines in a real project?
What architectural pattern separates domain model design from
persistence model constraints?
*Hint: Consider the difference between domain objects (rich
behaviour, ideally immutable/final) and persistence entities
(JPA-compatible, mutable) - and how Hibernate 6's new
embeddable records partially address this.*

**Q2 (TYPE D - Root Cause Trace):** A developer adds a
`transient` Java keyword (not `@Transient` annotation) to
a field in an `@Entity` class. What happens? Trace the
difference in behaviour between `transient` (Java keyword,
Java serialisation) and `@Transient` (JPA annotation,
persistence exclusion) and explain when each is needed.
*Hint: Both exclude from their respective systems, but
`transient` affects Java serialisation and does NOT affect
JPA mapping, while `@Transient` affects JPA mapping and
does NOT affect Java serialisation.*

**Q3 (TYPE G - Hands-On):** Create an `@Entity` class that
deliberately violates each of the three requirements (final,
no no-arg constructor, no @Id), and write assertions that
confirm the correct exception type and message for each
violation. What does each exception tell you about Hibernate's
startup sequence?
*Hint: Use `@SpringBootTest` with `@TestPropertySource` to
control `ddl-auto` and observe the exact exception types
at `EntityManagerFactory` creation time.*

---

### 🎯 Interview Deep-Dive

**Q1: What are the three requirements for a valid JPA
`@Entity` class, and why does each requirement exist?**
*Why they ask:* Tests understanding of the JPA specification
constraints, which every Spring developer encounters but many
cannot explain.
*Strong answer includes:*
- Non-final: Hibernate generates proxy subclasses for lazy
  loading; `final` prevents subclassing
- No-arg constructor (at minimum `protected`): Hibernate
  must instantiate entity instances and proxy classes
  without arguments
- `@Id` field: every entity needs a persistent identity;
  `@Id` tells Hibernate which field is the primary key

**Q2: What is the difference between `@Entity`,
`@MappedSuperclass`, and `@Embeddable`?**
*Why they ask:* Tests ability to model domain hierarchies
correctly in JPA - a frequent design decision in enterprise
applications.
*Strong answer includes:*
- `@Entity`: own table, own identity (`@Id`), queryable
  directly with JPQL
- `@MappedSuperclass`: no own table, shares column mappings
  to subclass tables, not directly queryable
- `@Embeddable`: value type embedded in an entity's table,
  no identity, no direct table

**Q3: A `@Entity` class has a computed field
`fullName = firstName + " " + lastName`. After deploying
to production, you start seeing SQL errors. What happened
and how would you fix it?**
*Why they ask:* Tests practical understanding of Hibernate's
automatic field mapping - a common real-world mistake.
*Strong answer includes:*
- Hibernate automatically maps all non-transient, non-static
  fields to columns; `fullName` was mapped to a
  `full_name` column that does not exist in the database
- Fix: add `@Transient` to the field to exclude it from
  JPA mapping, or convert it to a method instead of a field