---
id: JPH-049
title: "Hibernate Envers (Auditing and History)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-012, JPH-013, JPH-026
used_by: JPH-054, JPH-058
related: JPH-038, JPH-044, JPH-060
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /jpa-hibernate/hibernate-envers/
---

# JPH-049 - Hibernate Envers (Auditing and History)

⚡ **TL;DR** - Hibernate Envers automatically records
the full history of entity changes in audit tables
(`ENTITY_AUD` + `REVINFO`). Add `@Audited` to an entity;
Envers creates `products_aud` with all columns plus
`REV` (revision number) and `REVTYPE` (0=ADD, 1=MOD, 2=DEL).
Query history using `AuditReader`: `getRevisions()`,
`find(Product.class, id, revNumber)`. Critical limitation:
**bulk JPQL/Criteria UPDATE/DELETE bypasses Envers** - only
entity-by-entity `EntityManager.merge()`/`remove()` is
captured. Use for: financial audit trails, GDPR data
access logs, configuration history.

| #049 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Entity Basics, @ManyToOne, @OneToMany, EntityManager, JPA Lifecycle, @Transactional | |
| **Used by:** | JPA at Scale, Hibernate Internals | |
| **Related:** | Optimistic Locking, Hibernate Validator, Hibernate 6 Migration | |

---

### 🔥 The Problem This Solves

**AUDIT TRAIL WITHOUT BOILERPLATE:**
You need a "who changed what and when" history for every
Product change. Manual approach:
1. Add `createdBy`, `modifiedBy`, `createdAt`, `modifiedAt` to each entity
2. Add a `product_history` table manually
3. Write SQL/JPQL to insert into history on every change
4. Maintain this for 50 entities = 50 history tables + 100
   insert triggers + 50 history query methods

**WITH ENVERS:**
```java
@Entity
@Audited  // That's it
public class Product {
    @Id @GeneratedValue Long id;
    String name;
    BigDecimal price;
}
```
Envers automatically creates `product_aud` table and
captures every change. No manual history INSERT needed.
Query: "give me the full price history of product 42."

---

### 📘 Textbook Definition

**Hibernate Envers** is a JPA entity auditing module
that automatically records entity state changes in
revision tables. Part of Hibernate ORM (not a separate
project). Dependency: `hibernate-envers` (included in
`spring-boot-starter-data-jpa`).

**Core concepts:**

| Concept | Description |
|---|---|
| `@Audited` | Entity annotation; enables audit history capture |
| `@NotAudited` | Field annotation; excludes field from audit |
| `REVINFO` table | One row per revision (transaction); stores revision number + timestamp |
| `ENTITY_AUD` table | One row per entity state per revision; columns: all entity columns + REV + REVTYPE |
| `AuditReader` | Query API for accessing entity history |
| `REVTYPE` | 0=ADD (insert), 1=MOD (update), 2=DEL (delete) |
| Revision | A single transaction; all entities changed in one transaction share the same revision number |

**`REVINFO` table structure:**
```sql
CREATE TABLE REVINFO (
    REV        INTEGER PRIMARY KEY,  -- revision number (auto-increment)
    REVTSTMP   BIGINT                -- Unix timestamp of the revision
);
```

---

### ⏱️ Understand It in 30 Seconds

**One line:** Hibernate Envers is automatic entity
versioning - it records every change to annotated
entities in audit tables, queryable by revision number.

**One analogy:**
> Envers is like Git for your database rows. Each
> transaction is a "commit" (revision). The audit
> table (`product_aud`) stores every "version" of
> each row. `AuditReader` is `git log` + `git show` for
> your entities. "Show me product 42 as it was 3 weeks
> ago" = `find(Product.class, 42, revisionAt(3weeksAgo))`.
> Like Git, bulk operations (`git push --force`) can bypass
> history (bulk JPQL UPDATE bypasses Envers). Envers
> captures entity-by-entity operations (normal
> `save()`/`delete()`), not bulk operations.

**One insight:** Envers does not write to the audit table
directly during the flush. It collects audit data in a
listener, then writes ALL audit rows AFTER the main entity
writes WITHIN the same transaction. If the transaction
rolls back: the audit entries are also rolled back
(atomically). This is why Envers history is always
consistent with the actual entity state.

---

### 🔩 First Principles Explanation

**WHAT HAPPENS ON A PRODUCT UPDATE:**

```
@Transactional: updatePrice(42, 29.99)
  1. em.find(Product.class, 42)
     -> SELECT FROM products WHERE id=42
     -> Returns Product{id=42, price=19.99}

  2. product.setPrice(29.99)
     -> Hibernate dirty checking: price changed

  3. em.flush() (at commit)
     -> UPDATE products SET price=29.99 WHERE id=42
     -> Envers listener fires:
        INSERT INTO product_aud
          (id, price, REV, REVTYPE)
          VALUES (42, 29.99, 1001, 1)
        INSERT INTO revinfo
          (REV, REVTSTMP)
          VALUES (1001, 1712345678000)

  4. commit() -> both main table + audit table committed atomically

Resulting audit table:
  id=42, price=19.99, REV=1000, REVTYPE=0  (original ADD)
  id=42, price=29.99, REV=1001, REVTYPE=1  (MOD: price updated)
```

---

### 🧪 Thought Experiment

**BULK UPDATE BYPASS:**

```java
// This BYPASSES Envers - NO audit records created
// for price changes:
@Transactional
public void discountAllProducts(BigDecimal factor) {
    em.createQuery(
        "UPDATE Product p SET p.price = p.price * :f")
        .setParameter("f", factor)
        .executeUpdate();
    // No EnversPostUpdateEventListener fired
    // No records in product_aud for these updates
}

// For Envers to capture changes, use entity-by-entity:
@Transactional
public void discountAllProducts(BigDecimal factor) {
    List<Product> products = productRepo.findAll();
    products.forEach(p ->
        p.setPrice(p.getPrice().multiply(factor)));
    // Hibernate dirty checking -> UPDATE per entity
    // Envers listener fires per entity -> audit rows
    // CAUTION: 10,000 products = 10,000 UPDATEs + 10,000 INSERTs
    // Use for small datasets; batch for large datasets
}
```

---

### 🧠 Mental Model / Analogy

> Envers is a CDC (Change Data Capture) system implemented
> inside JPA. Traditional CDC (Debezium, AWS DMS) reads
> the database binary log AFTER the fact. Envers reads
> the Hibernate event stream DURING the transaction,
> then writes audit rows within the same transaction.
> This gives Envers a unique advantage: audit rows are
> NEVER out of sync with entity state (same transaction).
> Traditional CDC can lag (binary log delay) or miss
> changes (log format issues). Envers advantage: perfect
> consistency. Envers disadvantage: does not capture changes
> made outside Hibernate (raw SQL, other ORMs).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Envers automatically saves a history of every change
made to annotated entities. You can query "what did this
record look like on Jan 15?" or "who changed this and when?"

**Level 2 - Basic setup (junior developer):**
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.hibernate</groupId>
    <artifactId>hibernate-envers</artifactId>
</dependency>
```
```java
@Entity
@Audited
public class Product {
    @Id @GeneratedValue Long id;
    String name;
    BigDecimal price;

    @NotAudited  // Don't audit: changes too frequently
    private Instant lastViewedAt;
}
```

**Level 3 - Querying history (mid-level engineer):**
```java
@Service
@RequiredArgsConstructor
public class ProductHistoryService {

    @PersistenceContext
    private EntityManager em;

    public List<Product> getProductHistory(Long productId) {
        AuditReader ar = AuditReaderFactory.get(em);
        List<Number> revisions =
            ar.getRevisions(Product.class, productId);
        return revisions.stream()
            .map(rev -> ar.find(
                Product.class, productId, rev))
            .collect(Collectors.toList());
    }

    public Product getProductAtDate(
        Long productId, Date date) {
        AuditReader ar = AuditReaderFactory.get(em);
        return ar.find(Product.class, productId, date);
    }
}
```

**Level 4 - Custom revision entity (senior engineer):**
```java
// Add username to each revision
@Entity
@RevisionEntity(UserRevisionListener.class)
@Table(name = "REVINFO")
public class UserRevision extends DefaultRevisionEntity {
    private String username;
    // getters/setters
}

public class UserRevisionListener
    implements RevisionListener {
    @Override
    public void newRevision(Object revisionEntity) {
        UserRevision rev = (UserRevision) revisionEntity;
        String user = SecurityContextHolder.getContext()
            .getAuthentication().getName();
        rev.setUsername(user);
    }
}
// Now each revision records who made the change
```

**Level 5 - Performance and schema size (staff engineer):**
Envers doubles the write load (each INSERT/UPDATE triggers
an INSERT to the audit table). At high write volumes:
consider `@AuditOverride` to only audit specific fields
(not entire entity), or use `@NotAudited` on large blob
fields. Audit tables grow unbounded: implement a data
retention policy (e.g., archive audit rows older than
7 years, required for some compliance frameworks).
Partitioning the `_AUD` table by `REVTSTMP` date range
improves historical query performance. `@Audited(withModifiedFlag=true)`
adds a `_MOD` boolean column per field, recording WHICH
fields changed in each revision (useful for "show only
price history, not full entity history" queries).

---

### ⚙️ How It Works (Mechanism)

**ENVERS CONFIGURATION:**

```properties
# application.properties

# Store revision entity in the same schema
spring.jpa.properties.org.hibernate.envers
  .default_schema=audit_schema
# Table suffix (default: _AUD)
spring.jpa.properties.org.hibernate.envers
  .audit_table_suffix=_AUDIT
# Store deleted entity data (not just DEL marker)
spring.jpa.properties.org.hibernate.envers
  .store_data_at_delete=true
# Track which fields changed per revision:
spring.jpa.properties.org.hibernate.envers
  .global_with_modified_flag=false
```

**AUDIT TABLE DDL (auto-generated by Envers):**
```sql
-- product_aud table structure
CREATE TABLE product_aud (
    id      BIGINT  NOT NULL,
    REV     INTEGER NOT NULL,
    REVTYPE SMALLINT,         -- 0=ADD, 1=MOD, 2=DEL
    name    VARCHAR(255),
    price   DECIMAL(10,2),
    PRIMARY KEY (id, REV),
    FOREIGN KEY (REV) REFERENCES revinfo(REV)
);
```

---

### 🔄 The Complete Picture - End-to-End Flow

**QUERYING REVISION HISTORY WITH AuditQuery API:**

```java
AuditReader ar = AuditReaderFactory.get(em);

// Get all Product records modified at a specific revision:
List<Product> modifiedProducts = ar.createQuery()
    .forEntitiesModifiedAtRevision(Product.class, revNumber)
    .getResultList();

// Get all revisions for an entity with change details:
List<Object[]> history = ar.createQuery()
    .forRevisionsOfEntity(Product.class, false, true)
    .add(AuditEntity.id().eq(productId))
    .addOrder(AuditEntity.revisionNumber().asc())
    .getResultList();

for (Object[] row : history) {
    Product state     = (Product) row[0];     // entity state
    UserRevision rev  = (UserRevision) row[1]; // revision metadata
    RevisionType type = (RevisionType) row[2]; // ADD/MOD/DEL
    System.out.printf(
        "Rev %d by %s at %s: price=%.2f (%s)%n",
        rev.getId(), rev.getUsername(),
        new Date(rev.getTimestamp()),
        state.getPrice(), type);
}
```

---

### 💻 Code Example

**Example 1 - Complete audited entity with Spring Data Envers:**

```java
// Entity
@Entity
@Audited
@Table(name = "financial_transactions")
public class FinancialTransaction {
    @Id @GeneratedValue Long id;
    private BigDecimal amount;
    private String currency;
    private TransactionStatus status;

    @NotAudited  // Raw payload: large, changes too often
    @Column(columnDefinition = "TEXT")
    private String rawPayload;
}

// Spring Data Envers repository
public interface TransactionAuditRepository
    extends RevisionRepository<
        FinancialTransaction, Long, Integer> {
}

// Usage:
Revisions<Integer, FinancialTransaction> revisions =
    txAuditRepo.findRevisions(transactionId);
Page<Revision<Integer, FinancialTransaction>> page =
    txAuditRepo.findRevisions(transactionId, PageRequest.of(0, 10));
```

**Example 2 - Integration test for audit trail:**

```java
@SpringBootTest
@Transactional
class FinancialAuditTest {

    @Autowired FinancialTransactionRepository txRepo;
    @Autowired EntityManager em;

    @Test
    void statusChange_shouldBeAudited() {
        // Create
        FinancialTransaction tx = txRepo.save(
            new FinancialTransaction(new BigDecimal("100.00"),
                "USD", TransactionStatus.PENDING));
        Long id = tx.getId();
        TestTransaction.flagForCommit();
        TestTransaction.end();

        // Update
        TestTransaction.start();
        FinancialTransaction loaded = txRepo.findById(id).orElseThrow();
        loaded.setStatus(TransactionStatus.COMPLETED);
        txRepo.save(loaded);
        TestTransaction.flagForCommit();
        TestTransaction.end();

        // Verify audit
        TestTransaction.start();
        AuditReader ar = AuditReaderFactory.get(em);
        List<Number> revisions =
            ar.getRevisions(FinancialTransaction.class, id);
        assertThat(revisions).hasSize(2);

        FinancialTransaction original =
            ar.find(FinancialTransaction.class,
                id, revisions.get(0));
        assertThat(original.getStatus())
            .isEqualTo(TransactionStatus.PENDING);

        FinancialTransaction updated =
            ar.find(FinancialTransaction.class,
                id, revisions.get(1));
        assertThat(updated.getStatus())
            .isEqualTo(TransactionStatus.COMPLETED);
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Setup effort | Captures bulk ops | Who made change | DB-level capture | Best for |
|---|---|---|---|---|---|
| Hibernate Envers | Low (`@Audited`) | NO | Via custom `RevisionEntity` | No | Entity-level JPA audit |
| `@CreatedBy`/`@LastModifiedBy` | Low (`@EnableJpaAuditing`) | Partially (last modifier only) | Yes | No | Simple last-modified tracking |
| Database triggers | Medium | YES (all SQL) | DB user only | Yes | Cross-ORM, legacy systems |
| Debezium (CDC) | High | YES (all SQL) | DB user only | Yes (WAL) | Event streaming, microservices |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Envers captures all data changes including direct SQL" | Envers ONLY captures changes made through Hibernate's EntityManager/Session. Native JDBC, raw SQL, other ORMs, DB migrations (Flyway/Liquibase), stored procedures = NOT captured. For complete audit coverage: use DB triggers or CDC (Debezium) alongside Envers. |
| "Deleting an entity deletes its audit history" | NO - this is a key design feature. The `_AUD` table rows are independent of the main entity. Deleting `product` row ID=42 does NOT delete `product_aud` rows with id=42. The audit history persists permanently (until manually deleted from the audit table). The main entity table has no FK to the audit table. |
| "@NotAudited fields are blank in audit history" | When `store_data_at_delete=false` (default): @NotAudited fields are NULL in audit rows. When `store_data_at_delete=true`: the full entity state is stored at deletion time, but `@NotAudited` fields are still excluded. The audit row shows what Envers tracked, not the full entity state. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Audit Table Out of Sync with Main Table**

**Symptom:** Entity shows price=29.99 but audit history
shows the last revision had price=19.99. No revision
for the price change.
**Root Cause:** The price was changed via a bulk JPQL
UPDATE or native SQL - neither fires Envers listeners.
**Diagnosis:**
```sql
-- Check: does audit row count match expected revisions?
SELECT COUNT(*) FROM product_aud WHERE id = 42;
-- 1 row = only the initial INSERT was captured.
-- 2+ rows = changes were captured.
-- If only 1 row despite known updates: bulk update used.

-- Look for bulk update in code:
-- em.createQuery("UPDATE Product SET ...").executeUpdate()
-- jdbcTemplate.update("UPDATE products SET ...")
-- productRepo.updatePriceBulk(...) -- custom @Modifying query
```
**Fix:** Replace bulk UPDATE with entity-by-entity load +
modify + flush. For performance with large datasets: use
batch size (`hibernate.jdbc.batch_size`) and `flush()+clear()`
every N entities.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-026 - @Transactional]] - audit rows written within
  the same transaction; rollback affects both
- [[JPH-011 - Entity Lifecycle]] - Envers hooks into
  `PostInsertEvent`, `PostUpdateEvent`, `PostDeleteEvent`

**Builds On This (learn these next):**
- [[JPH-054 - JPA at Scale]] - Envers write overhead
  is significant at scale; architecture patterns to manage it
- [[JPH-058 - Hibernate Internals]] - Envers uses Hibernate
  event listeners internally

**Related:**
- [[JPH-038 - Optimistic Locking]] - `@Version` field provides
  optimistic concurrency; Envers provides history. Both are
  often used together for complete change tracking.
- [[JPH-060 - Hibernate 6 Migration]] - Envers API changes
  in Hibernate 6 + Jakarta Persistence migration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ENABLE       │ @Audited on entity class                  │
│ EXCLUDE      │ @NotAudited on field                      │
├──────────────┼───────────────────────────────────────────┤
│ TABLES       │ ENTITY_AUD: entity history                │
│              │ REVINFO: revision metadata (timestamp)    │
├──────────────┼───────────────────────────────────────────┤
│ REVTYPE      │ 0=ADD, 1=MOD, 2=DEL                       │
├──────────────┼───────────────────────────────────────────┤
│ QUERY        │ AuditReaderFactory.get(em)                │
│              │ .find(Product.class, id, revNumber)        │
│              │ .getRevisions(Product.class, id)          │
├──────────────┼───────────────────────────────────────────┤
│ CUSTOM REV   │ @RevisionEntity + @RevisionListener       │
│              │ -> add username, comment per revision     │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Bulk UPDATE/DELETE BYPASSES Envers        │
│ LIMITATION   │ Use entity-by-entity changes for audit   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Envers = automatic JPA entity history.   │
│              │ @Audited creates _AUD table. Query via    │
│              │ AuditReader. Bulk ops NOT captured."      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@Audited` creates `ENTITY_AUD` table; Envers writes
   audit row in same transaction - always consistent
2. `AuditReaderFactory.get(em)` queries history;
   `find(Product.class, id, revNumber)` returns past state
3. CRITICAL: bulk JPQL `UPDATE`/`DELETE` bypasses Envers -
   only entity-by-entity changes are captured

**Interview one-liner:** Hibernate Envers automatically
records entity state history in `_AUD` tables within
the same transaction as entity changes (always consistent).
`@Audited` enables it; `AuditReaderFactory.get(em)` queries
history. Critical limitation: bulk JPQL `UPDATE`/`DELETE`
is NOT captured - only EntityManager-level changes are.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Transactional audit
logs (Envers model) vs async audit logs (CDC/Debezium model)
represent a fundamental trade-off in audit system design.
Transactional: audit is always consistent (same commit);
overhead per write; doesn't capture out-of-ORM changes.
Async (CDC): captures ALL changes (any source); slight lag
(milliseconds to seconds); more complex infrastructure.
The right choice depends on consistency requirements:
for financial audit (must match exactly): transactional.
For operational logging (approximate is acceptable): async.
This pattern generalizes: synchronous vs asynchronous
writes = consistency vs throughput/scope trade-off.

---

### 💡 The Surprising Truth

Hibernate Envers stores the COMPLETE entity state on every
modification - not just the changed fields. If you have a
Product with 30 columns and change only `price`, the audit
row stores ALL 30 columns. This means: (1) audit tables
are often larger than the main tables in write-heavy systems
(each UPDATE creates a full row copy), and (2) querying
"what fields changed?" requires comparing two adjacent
revisions manually - unless `withModifiedFlag=true` is
set, which adds a `_MOD` boolean column per field. For
audit tables in production: partition by `REVTSTMP` to
prevent full table scans on historical queries. Consider
archiving audit rows older than your compliance retention
period (e.g., 7 years for financial records) to a cold
storage table or S3 to control main audit table size.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **ADD** `@Audited` to an entity and explain what tables
   Envers creates and what columns they contain
2. **QUERY** entity history at a specific revision and
   at a specific date using `AuditReader`
3. **CREATE** a custom `@RevisionEntity` that stores
   the username making the change
4. **EXPLAIN** why bulk JPQL UPDATE bypasses Envers and
   how to ensure audit coverage for bulk operations
5. **DESIGN** an audit retention strategy for an audit
   table that grows unbounded in a write-heavy system

---

### 🎯 Interview Deep-Dive

**Q1: You need to audit all changes to a financial
transaction entity including who made the change and
when. How would you implement this with Hibernate Envers?**
*Why they ask:* Tests practical Envers implementation.
*Strong answer includes:*
- Add `@Audited` to the entity
- Create custom `@RevisionEntity` extending `DefaultRevisionEntity`
  with `username` field
- Implement `RevisionListener` that reads username from
  `SecurityContextHolder` in `newRevision()`
- `REVINFO` table now has: `REV`, `REVTSTMP`, `USERNAME`
- Query: `AuditReader.createQuery().forRevisionsOfEntity(FinancialTransaction.class, false, true)`
  returns Object[] of [entity state, revision metadata, REVTYPE]
- Add integration test verifying status change is captured

**Q2: Why might Envers audit history be incomplete for
some entities in production?**
*Why they ask:* Tests awareness of Envers limitations.
*Strong answer includes:*
- Bulk JPQL/Criteria UPDATE/DELETE bypasses Envers listeners
- Native SQL (`em.createNativeQuery(...)`) bypasses Envers
- JDBC template queries bypass Envers
- Spring Data `@Modifying` custom JPQL queries bypass Envers
- Flyway/Liquibase schema migrations bypass Envers
- Fix: replace bulk updates with entity-by-entity for audited
  entities; or use DB triggers/CDC alongside Envers for
  complete coverage