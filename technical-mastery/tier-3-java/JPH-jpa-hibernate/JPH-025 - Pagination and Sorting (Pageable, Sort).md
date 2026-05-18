---
id: JPH-025
title: "Pagination and Sorting (Pageable, Sort)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-016, JPH-023, JPH-024
used_by: JPH-027, JPH-030, JPH-043
related: JPH-036, JPH-054
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/jpa-hibernate/pagination-sorting/
---

⚡ **TL;DR** - `Pageable` (Spring Data) encapsulates page
number, page size, and sort direction; `Page<T>` wraps
results with total count metadata. Add `Pageable` to any
repository method for automatic LIMIT/OFFSET SQL. Never
use `findAll()` without pagination on production tables.

| #025            | Category: JPA & Hibernate                                         | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | JPQL, CrudRepository/JpaRepository, @Query, Derived Query Methods |                 |
| **Used by:**    | N+1 Problem, DTO Projections, Spring Data Specifications          |                 |
| **Related:**    | Criteria API, JPA at Scale                                        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without pagination, `findAll()` returns every row in the
table as a Java object in memory. A table with 10 million
rows returns 10 million entities, fills the heap, triggers
garbage collection pauses, and crashes the application.
Even a table with 100,000 rows returns more data than any
REST endpoint consumer needs.

**THE BREAKING POINT:**
A growing application's "products list" endpoint starts
at 100 records and works fine. At 50,000 records, response
time is 5 seconds. At 500,000 records, it causes
`OutOfMemoryError`. The fix (add `LIMIT/OFFSET` to the
SQL) is always needed but requires changing every query.

**THE INVENTION MOMENT:**
`Page<Product> findAll(Pageable pageable)` in Spring Data
accepts a `Pageable` parameter and automatically adds
`LIMIT` and `OFFSET` to the SQL, plus a separate
`COUNT(*)` query for total pages/items metadata. The
controller receives exactly the requested page size.
No manual SQL changes; pagination is a first-class concern.

---

### 📘 Textbook Definition

**`Pageable`** is a Spring Data interface encapsulating
three pagination parameters: page number (0-based index),
page size (items per page), and sort criteria (`Sort`).
Created via `PageRequest.of(page, size)` or
`PageRequest.of(page, size, Sort.by("fieldName").descending())`.

**`Page<T>`** is a Spring Data result type wrapping a
list of entities plus metadata: total elements count,
total pages, current page number, whether this is the
first/last page, and whether there is a next/previous page.

**`Slice<T>`** is a lighter alternative: no total count
(no `COUNT(*)` query), only `hasNext()`. Useful for
infinite scroll UIs where total pages are not needed.

**`Sort`** encapsulates sort direction and field(s).
Can be built inline: `Sort.by("price").descending().and(Sort.by("name"))`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `Pageable` = which page and how big; `Page`
= data + total count; add `Pageable` to any repository
method for automatic SQL pagination.

**One analogy:**

> `Pageable` is the chapter and page number in a book.
> `Page<T>` is that physical page with content + "page X
> of Y total pages". You request page 3 of 10; the library
> (Spring Data) fetches that exact section from the
> database (LIMIT/OFFSET), counts the total (COUNT query),
> and returns the page with navigation metadata.

**One insight:** `Page<T>` always issues 2 SQL queries:
one for the data (with LIMIT/OFFSET) and one `COUNT(*)`
for total pages. For large tables, the `COUNT(*)` can
be slow. If total count is not needed (infinite scroll,
"load more" UX), use `Slice<T>` to avoid the count query.

---

### 🔩 First Principles Explanation

**THREE RETURN TYPE OPTIONS:**

```
findAll(Pageable) -> Page<T>
  Executes: SELECT ... LIMIT ? OFFSET ?
            + SELECT COUNT(*) FROM ...
  Returns: data + total count + page metadata

findAll(Pageable) -> Slice<T>  (method signature)
  Executes: SELECT ... LIMIT ?+1  (fetches one extra)
  Returns: data + hasNext() (no COUNT query)
  Use: when total count is not needed

findAll(Sort) -> List<T>  (no pagination)
  Executes: SELECT ... ORDER BY ...
  Returns: full sorted list (no paging)
  WARNING: loads all rows!
```

**PAGE VS SLICE DECISION:**

```
"Show page 3 of 10" UI:
  -> needs total pages -> use Page<T>

"Load more / infinite scroll" UI:
  -> needs only hasNext() -> use Slice<T>
  -> saves one COUNT(*) query per request

Batch processing (iterate all records):
  -> use Slice<T> in a loop (no total needed)
  -> or use Stream<T> with proper transaction scope
```

**PAGEABLE CREATION:**

```java
// Page 0, size 20, sorted by price desc
PageRequest.of(0, 20, Sort.by("price").descending())

// Multi-field sort:
PageRequest.of(0, 20,
    Sort.by(Sort.Order.desc("price"),
            Sort.Order.asc("name")))

// Unsorted:
PageRequest.of(0, 20)
// WARNING: OFFSET without ORDER BY = non-deterministic order

// From request parameters (Spring MVC):
@GetMapping("/products")
public Page<Product> list(
    @PageableDefault(size = 20,
                     sort = "name") Pageable pageable) {
    return repo.findAll(pageable);
}
```

---

### 🧪 Thought Experiment

**DEEP PAGINATION PROBLEM:**

```sql
-- Page 1 (efficient):
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 0

-- Page 10,000 (slow):
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 199980
-- Database must scan 200,000 rows and skip 199,980
-- Execution time: O(offset) - grows linearly with page number
```

**AT PAGE 10,000 OF 200,000 ROWS:** offset=199,980 ->
database must read and discard 199,980 rows before
returning the 20 rows on page 10,000.

**THE ALTERNATIVE: keyset pagination (cursor-based):**

```sql
-- First page:
SELECT * FROM products WHERE id > 0 ORDER BY id LIMIT 20

-- Next page (use last id from previous page):
SELECT * FROM products WHERE id > 19980 ORDER BY id LIMIT 20
-- Database uses the index on id directly - O(1) navigation
-- No offset scan; always fast regardless of page number
```

**THE INSIGHT:** Spring Data's `Pageable` uses OFFSET
pagination. For deep pages (page > 1000), performance
degrades. For truly large datasets with deep pagination,
keyset/cursor-based pagination is required - not supported
natively by Spring Data `Pageable` but can be implemented
with custom `@Query` using `WHERE id > :lastId`.

---

### 🧠 Mental Model / Analogy

> Pageable is like a librarian request slip: "I want books
> in section Science, sorted by publication date, 20 at
> a time, starting from book number 40." The librarian
> (Spring Data) finds ALL books in section Science
> (conceptually), sorts them, skips 40, and brings you 20. `Page<T>` is the stack of books PLUS a note saying
> "there are 500 books in this section total."
>
> The performance problem: for the 10,000th page, the
> librarian still counts through all previous 9,999 pages
> before bringing yours (OFFSET). A bookmark (keyset
> pagination) lets the librarian go directly to the right
> position.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of loading all data at once, `Pageable` tells JPA
"give me 20 items starting at item 40". `Page<T>` returns
the 20 items plus information about the total.

**Level 2 - How to use it (junior developer):**
Add `Pageable` as a parameter to any repository method.
The method returns `Page<T>` or `Slice<T>`. Create `Pageable`
with `PageRequest.of(pageNum, pageSize)`.

**Level 3 - How it works (mid-level engineer):**
Spring Data detects `Pageable` parameter and wraps the
JPQL in a LIMIT/OFFSET clause. For `Page<T>`, an additional
`COUNT(*)` query is executed. The `Page<T>` object packages
both results with metadata (totalElements, totalPages,
isFirst, isLast, hasNext, hasPrevious).

**Level 4 - Why it was designed this way (senior/staff):**
The `Pageable` abstraction separates pagination concerns
from query concerns. A repository method `findByStatus(String, Pageable)`
expresses two orthogonal concerns: what to find (status)
and how to page it (Pageable). The `@Query` or method name
expresses the WHERE clause; `Pageable` adds LIMIT/OFFSET
and ORDER BY orthogonally. This prevents query duplication:
one method handles both paginated and non-paginated use cases.

**Level 5 - Mastery (distinguished engineer):**
Spring Data's `Pageable` generates OFFSET pagination,
which has O(offset) performance. For any production
use case with potentially millions of rows and deep page
navigation, keyset pagination is required. The pattern:
`findByIdGreaterThanOrderById(@Param("cursor") Long id, Pageable pageable)`
where `id` is the last ID from the previous page. This
always uses an index range scan instead of a full scan +
skip. Spring Data does not have built-in keyset pagination
support; it must be implemented with custom `@Query` methods
or Spring Data extensions like Blaze-Persistence or
Spring Data JDBC's keyset pagination (added in 3.1).

---

### ⚙️ How It Works (Mechanism)

**GENERATED SQL FOR Page<T>:**

```sql
-- Data query:
SELECT p.id, p.name, p.price, p.status
FROM products p
WHERE p.status = 'ACTIVE'
ORDER BY p.name ASC
LIMIT 20 OFFSET 40

-- Count query (auto-derived or custom countQuery):
SELECT COUNT(p.id) FROM products p
WHERE p.status = 'ACTIVE'
```

**GENERATED SQL FOR Slice<T>:**

```sql
-- Data query (fetches size+1 to detect hasNext):
SELECT p.id, p.name, p.price
FROM products p
WHERE p.status = 'ACTIVE'
ORDER BY p.name ASC
LIMIT 21  -- size+1 (no OFFSET for page 0)
-- Hibernate returns 20, checks if 21st exists -> hasNext
-- No COUNT query
```

---

### 🔄 The Complete Picture - End-to-End Flow

**REST CONTROLLER -> REPOSITORY -> DATABASE:**

```java
// Controller (accepts request params automatically):
@GetMapping("/products")
public ResponseEntity<Page<ProductDto>> listProducts(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(defaultValue = "name") String sort) {

    Pageable pageable = PageRequest.of(
        page, size, Sort.by(sort));
    Page<Product> productPage =
        productRepo.findByStatus("ACTIVE", pageable);

    // Convert entities to DTOs within transaction:
    Page<ProductDto> dtoPage =
        productPage.map(ProductDto::from);
    return ResponseEntity.ok(dtoPage);
}

// SQL:
// SELECT * FROM products WHERE status='ACTIVE'
//   ORDER BY name LIMIT 20 OFFSET 0
// SELECT COUNT(*) FROM products WHERE status='ACTIVE'

// JSON response:
// { "content": [...], "totalElements": 5000,
//   "totalPages": 250, "number": 0, "size": 20,
//   "first": true, "last": false }
```

---

### 💻 Code Example

**Example 1 - Standard paginated repository method:**

```java
@Repository
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // Derived: works with Pageable
    Page<Product> findByStatus(
        String status, Pageable pageable);

    // @Query: add Pageable parameter
    @Query("SELECT p FROM Product p " +
           "JOIN p.category c " +
           "WHERE c.name = :catName")
    Page<Product> findByCategory(
        @Param("catName") String catName,
        Pageable pageable);

    // Slice (no COUNT query):
    Slice<Product> findByPriceGreaterThan(
        BigDecimal price, Pageable pageable);
}
```

**Example 2 - BAD: unsorted pagination (non-deterministic):**

```java
// BAD: no sort -> non-deterministic order
// Page 1 and page 2 may have overlapping rows
// depending on query plan execution
Page<Product> findByStatus(String s,
    Pageable pageable);

// Called with: PageRequest.of(0, 20) // no sort!
// -> SELECT ... LIMIT 20 OFFSET 0 (no ORDER BY)
// -> next call: same or different rows?

// GOOD: always include sort
PageRequest.of(0, 20, Sort.by("id").ascending())
// -> ORDER BY id ASC LIMIT 20 OFFSET 0 (deterministic)
```

**Example 3 - Spring MVC with @PageableDefault:**

```java
@GetMapping("/orders")
public Page<OrderDto> getOrders(
    @PageableDefault(size = 10, sort = "createdAt",
                     direction = Sort.Direction.DESC)
    Pageable pageable,
    @RequestParam Optional<String> status) {

    return status.map(s ->
            orderRepo.findByStatus(s, pageable))
        .orElseGet(() -> orderRepo.findAll(pageable))
        .map(orderMapper::toDto);
}
// Client can override: ?page=2&size=5&sort=total,desc
```

**Example 4 - Cursor-based pagination for deep pages:**

```java
// Keyset pagination (avoids OFFSET cost):
@Query("SELECT p FROM Product p " +
       "WHERE p.id > :lastId " +
       "ORDER BY p.id ASC")
List<Product> findNextPage(
    @Param("lastId") Long lastId,
    Pageable pageable);
// Always uses index on id -> O(log n) regardless of depth
// No total count; cannot jump to arbitrary page

// Usage:
Long lastId = 0L;  // start
List<Product> page1 = repo.findNextPage(lastId,
    PageRequest.of(0, 20));
lastId = page1.get(page1.size()-1).getId();
List<Product> page2 = repo.findNextPage(lastId,
    PageRequest.of(0, 20));
```

---

### ⚖️ Comparison Table

| Return Type | Count query?    | hasNext()          | Total pages? | Use case                                                |
| ----------- | --------------- | ------------------ | ------------ | ------------------------------------------------------- |
| `Page<T>`   | Yes (2 queries) | Yes                | Yes          | Standard pagination with "X of Y pages" UI              |
| `Slice<T>`  | No (1 query)    | Yes (fetch size+1) | No           | Infinite scroll / load more                             |
| `List<T>`   | No              | No                 | No           | Fixed-size results where pagination metadata not needed |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "`Page<T>` is always the right return type for paginated queries" | `Page<T>` issues a second `COUNT(*)` query. For tables with millions of rows, this COUNT can be slow. For infinite scroll UIs that don't show total pages, `Slice<T>` is faster.                                                           |
| "Pagination without sorting is fine because ORDER BY is implicit" | Without an explicit `ORDER BY`, the database may return rows in any order (it is undefined). Consecutive paginated calls may return overlapping or missing rows. Always provide explicit sort criteria with `PageRequest`.                 |
| "`PageRequest.of(page, size)` is 1-based"                         | Spring Data `Pageable` page numbers are 0-based. Page 0 is the first page. Passing `page=1` from a 1-based frontend without adjustment returns the SECOND page.                                                                            |
| "Deep pagination (page 10,000) is equally fast as page 1"         | `OFFSET` pagination requires the database to scan and skip `page * size` rows. Page 10,000 of 20 items requires skipping 199,980 rows. This is O(offset) and becomes slow at large page numbers. Use keyset pagination for large datasets. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Non-Deterministic Pagination Results**

**Symptom:** Frontend shows duplicate products between
pages, or some products never appear. Page 1 and page 2
contain the same items.

**Root Cause:** Repository method called with `PageRequest.of(page, size)`
without a sort. The database returns rows in undefined
order without `ORDER BY`. Consecutive pages may overlap.

**Fix:** Always include sort: `PageRequest.of(page, size, Sort.by("id").ascending())`.
Use a unique column (like `id`) as a tiebreaker sort to
guarantee stable ordering.

---

**Failure Mode 2: Slow COUNT(\*) on Large Tables**

**Symptom:** Paginated API endpoint takes 3 seconds for
the first request. SQL log shows a slow `COUNT(*)` query
on a table with 50 million rows.

**Root Cause:** `Page<T>` always executes a `COUNT(*)`.
On large tables with complex WHERE clauses, this is a
full index scan.

**Fix Option 1:** Switch to `Slice<T>` if total count is
not needed (infinite scroll).

**Fix Option 2:** Provide a custom `countQuery` in `@Query`
that uses a faster path (indexed column COUNT):

```java
@Query(value = "SELECT p FROM Product p WHERE ...",
       countQuery = "SELECT COUNT(p.id) " +
                    "FROM Product p WHERE ...")
Page<Product> findPaged(Pageable pageable);
```

**Fix Option 3:** Use an approximate count strategy for
very large tables (store count in a separate counter table
updated by triggers).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-016 - CrudRepository and JpaRepository]] -
  `findAll(Pageable)` is defined on `JpaRepository`
- [[JPH-023 - @Query]] - `@Query` methods can accept
  `Pageable` parameter

**Builds On This (learn these next):**

- [[JPH-027 - N+1 Problem]] - pagination does not fix N+1;
  JOIN FETCH with pagination has ordering conflicts
- [[JPH-030 - DTO Projections]] - project to DTOs in
  paginated queries to reduce memory
- [[JPH-043 - Spring Data Specifications]] - Specifications
  can be combined with `Pageable` for dynamic filtering

**Related:**

- [[JPH-054 - JPA at Scale]] - keyset pagination and
  deep pagination strategies for large datasets

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PAGEABLE     │ PageRequest.of(page, size, Sort.by(...)) │
│              │ 0-based page numbers                     │
├──────────────┼──────────────────────────────────────────┤
│ Page<T>      │ Data + COUNT(*) query. 2 SQL queries.    │
│              │ Use for UI showing "X of Y pages"        │
├──────────────┼──────────────────────────────────────────┤
│ Slice<T>     │ Data only + hasNext(). 1 SQL query.      │
│              │ Use for infinite scroll / load more      │
├──────────────┼──────────────────────────────────────────┤
│ MANDATORY    │ Always include sort with Pageable!       │
│ SORT         │ No sort = non-deterministic page results │
├──────────────┼──────────────────────────────────────────┤
│ DEEP PAGES   │ OFFSET pagination = O(offset) cost.      │
│              │ Use keyset/cursor for page > 1000        │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Add Pageable to any repo method for LIMI│
│              │ /OFFSET SQL. Page<T>=2 queries (COUNT too│
│              │ Slice<T>=1 query. Always sort Pageable." │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `Pageable` page numbers are 0-based; always include
   an explicit Sort to prevent non-deterministic results
2. `Page<T>` issues 2 SQL queries (data + COUNT); use
   `Slice<T>` when total count is not needed
3. OFFSET pagination degrades at deep pages; use
   keyset pagination (`WHERE id > :lastId`) for
   large datasets

**Interview one-liner:** `Pageable` in Spring Data adds
LIMIT/OFFSET to any repository query. `Page<T>` returns
data + total count (2 queries); `Slice<T>` returns data +
`hasNext()` (1 query - better for infinite scroll).
Always provide a sort order with `Pageable` - without it,
pagination results are non-deterministic. OFFSET pagination
is O(offset) - for deep pages on large datasets, keyset
pagination is required.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** All list endpoints
in production must be paginated. "Load all" is a ticking
time bomb: it works at 100 records, fails at 100,000.
The pagination contract should be established at API
design time (cursor, page+size, or offset) and enforced
at the repository layer. This principle is universal:
Elasticsearch has `from`/`size` (OFFSET, same deep-page
problem), Cassandra uses cursor-based pagination natively,
Redis SCAN uses a cursor, DynamoDB pagination uses
`LastEvaluatedKey` (keyset). Every storage system has
a pagination API; always use it.

**Where else this pattern appears:**

- **REST APIs** - pagination links in response body (`next`,
  `prev`, `last` HAL links); `Content-Range` header
- **GraphQL** - cursor-based pagination via `first`/`after`
  (Relay spec) - equivalent to keyset pagination
- **Kafka consumer** - `poll()` with batch size = Pageable
  equivalent for event streams
- **Apache Spark** - partitioning large datasets for
  parallel processing = distributed pagination

---

### 💡 The Surprising Truth

Spring Data's `Page<T>.map(Function)` method (for converting
entities to DTOs) looks innocent but can cause an N+1
problem if the mapping function accesses lazy associations.
`productPage.map(ProductDto::from)` calls `ProductDto.from(product)`
for each entity, which may call `product.getCategory().getName()` -
triggering a lazy load per entity. The persistence context
is still open (called within the repository transaction),
so no `LazyInitializationException` - but N SELECT
statements for categories. Always check that `Page.map()`
conversions do not access lazy-loaded associations unless
they were loaded via JOIN FETCH in the original query.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **WRITE** a paginated endpoint with a custom `@Query`
   including `countQuery`, taking `Pageable` from request
   parameters, and mapping to DTOs
2. **CHOOSE** between `Page<T>` and `Slice<T>` for three
   different UI use cases with justification
3. **FIX** non-deterministic pagination by adding an
   explicit sort order to `PageRequest`
4. **EXPLAIN** why OFFSET pagination degrades at deep
   pages and implement a keyset pagination alternative
5. **DEBUG** slow paginated queries by identifying missing
   or inefficient `countQuery` and optimizing it

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Page<T> and Slice<T>
in Spring Data, and when would you use each?**
_Why they ask:_ Tests Spring Data depth knowledge and
performance awareness.
_Strong answer includes:_

- `Page<T>`: executes 2 SQL queries (data with LIMIT/OFFSET
  - `COUNT(*)` for total). Returns total elements, total
    pages, current page, isFirst, isLast, hasNext, hasPrevious.
    Use when UI shows "page X of Y" or total record count.
- `Slice<T>`: executes 1 SQL query (data with LIMIT+1 to
  detect next page). Returns hasNext() only. Use for
  infinite scroll / load more where total count is not
  shown.
- Performance: for tables with millions of rows, COUNT(\*)
  can be as slow as the data query. Slice<T> halves the
  database load for these cases.

**Q2: Why does pagination without a sort order produce
unreliable results?**
_Why they ask:_ Tests understanding of SQL query semantics
and determinism.
_Strong answer includes:_

- Without `ORDER BY`, the database returns rows in
  implementation-defined order (no guarantee)
- A table scan may return rows in different orders on
  consecutive calls (depending on buffer cache, parallel
  execution plan, index usage)
- Consecutive pages may have overlapping rows (page 1
  contains row X; page 2 also contains row X if the
  first-page rows have shifted in the scan order)
- Fix: always include an explicit, unique sort. For stable
  pagination: sort by a unique column (`id`) or a composite
  that is unique per row.

**Q3: What is the performance problem with deep OFFSET
pagination, and how would you solve it?**
_Why they ask:_ Tests scalability thinking; common
architectural question for senior roles.
_Strong answer includes:_

- OFFSET pagination: `SELECT ... LIMIT 20 OFFSET N` requires
  the database to scan and skip N rows
- For page 10,000 of 20 items: skip 199,980 rows -> O(N)
  cost that grows with page depth
- Keyset (cursor) pagination: `WHERE id > :lastId ORDER BY id LIMIT 20`
  -> uses index range scan -> O(log n) regardless of depth
- Trade-off: keyset cannot jump to arbitrary page; only
  next/previous navigation possible
- Spring Data does not have built-in keyset support; must
  be implemented with custom `@Query` or external libraries
  (Blaze-Persistence, Spring Data JDBC 3.1+)
