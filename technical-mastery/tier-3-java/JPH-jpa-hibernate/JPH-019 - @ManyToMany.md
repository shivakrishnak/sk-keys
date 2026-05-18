---
id: JPH-019
title: "@ManyToMany"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-018
used_by: JPH-020, JPH-021, JPH-022, JPH-027
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
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/jpa-hibernate/manytomany/
---

⚡ **TL;DR** - `@ManyToMany` uses a join table to represent
a many-to-many relationship. Avoid pure `@ManyToMany` in
production - the moment you need an attribute on the join
table (e.g., `enrolled_at`, `role`), you must replace it
with an explicit join entity + two `@ManyToOne` associations.

| #019            | Category: JPA & Hibernate                                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, @Id, @Table/@Column, @OneToMany and @ManyToOne         |                 |
| **Used by:**    | @JoinColumn and @JoinTable, FetchType, CascadeType, N+1 Problem |                 |
| **Related:**    | @Embedded, Inheritance Mapping                                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without `@ManyToMany`, a Student-Course relationship
(many students per course, many courses per student)
requires manually managing the join table:
`INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)`.
The developer must keep the join table in sync with both
sides of the relationship. Every load of "courses for a
student" is a manual JOIN query.

**THE BREAKING POINT:**
Without ORM support for M:N, every domain that has M:N
relationships (User-Role, Product-Tag, Author-Book)
requires custom join table DAO code. The relationship
logic is scattered across service and DAO layers.

**THE INVENTION MOMENT:**
`@ManyToMany` with `@JoinTable` lets JPA manage the join
table automatically. `student.getCourses().add(course)`
manages both sides. JPA generates the INSERT/DELETE on
the join table. The developer works with object references,
not raw join table keys.

---

### 📘 Textbook Definition

**`@ManyToMany`** is a JPA annotation that maps a
many-to-many relationship between two entity types using
a join table. Each entity can be associated with multiple
instances of the other. The join table contains two FK
columns, one for each entity.

One side is the owning side (has `@JoinTable`); the other
is the inverse side (`mappedBy`). Both sides hold a
collection field. Changes to the inverse side's collection
are ignored by JPA - only the owning side's collection
changes generate insert/delete on the join table.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@ManyToMany` maps a M:N relationship via
a join table; one side owns the join table (`@JoinTable`),
the other uses `mappedBy`.

**One analogy:**

> Students and Courses: each student takes many courses,
> each course has many students. The enrollment record
> in the middle is the join table. `@ManyToMany` lets JPA
> manage the enrollment records automatically when you
> add/remove from the collection.

**One insight:** Pure `@ManyToMany` breaks the moment
you need data on the relationship itself (enrollment date,
grade, role). At that point, the join table becomes a first-class
entity and `@ManyToMany` must be replaced with an explicit
join entity + two `@ManyToOne` mappings. Design with
this upgrade path in mind from the start.

---

### 🔩 First Principles Explanation

**DATABASE SCHEMA:**

```
students:           student_courses:    courses:
id | name           student_id | course_id   id | title
1  | Alice          1          | 1           1  | Java
2  | Bob            1          | 2           2  | SQL
                    2          | 1
```

**ENTITY MAPPING:**

```java
// Owning side: Student has @JoinTable
@Entity
public class Student {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String name;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "student_courses",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();

    public void enroll(Course c) {
        courses.add(c);
        c.getStudents().add(this);  // sync inverse
    }
    public void drop(Course c) {
        courses.remove(c);
        c.getStudents().remove(this);
    }
}

// Inverse side: Course has mappedBy
@Entity
public class Course {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String title;

    @ManyToMany(mappedBy = "courses",
                fetch = FetchType.LAZY)
    private Set<Student> students = new HashSet<>();
}
```

**CORE INVARIANTS:**

1. The owning side (with `@JoinTable`) controls join table
   writes; inverse side (`mappedBy`) changes are ignored
2. Always use `Set` (not `List`) for `@ManyToMany` collections
   to avoid duplicate join table entries and Cartesian
   product issues with JOIN FETCH
3. Do NOT use `CascadeType.ALL` on `@ManyToMany` - cascading
   REMOVE across M:N can delete shared entities referenced
   by other parents
4. `@ManyToMany` collections are LAZY by default (good)
5. Never use `@ManyToMany` when the join table has extra
   columns - use an explicit join entity instead

---

### 🧪 Thought Experiment

**THE UPGRADE: join table needs an attribute**

Initial design with `@ManyToMany`:

```java
@ManyToMany
@JoinTable(name = "student_courses", ...)
private Set<Course> courses;
```

New requirement: track `enrolled_at` date and `grade` per
enrollment.

**With pure @ManyToMany:** impossible - the join table
columns `enrolled_at` and `grade` cannot be mapped to
any entity field. The join table is invisible to JPA.

**Upgraded to explicit join entity:**

```java
@Entity
public class Enrollment {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id")
    private Student student;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "course_id")
    private Course course;

    private LocalDate enrolledAt;
    private String grade;
}

// Student now has:
@OneToMany(mappedBy = "student",
           cascade = CascadeType.ALL,
           orphanRemoval = true)
private List<Enrollment> enrollments;

// Course now has:
@OneToMany(mappedBy = "course")
private List<Enrollment> enrollments;
```

**THE INSIGHT:** Design your `@ManyToMany` as an explicit
join entity from the start if there is ANY chance the
relationship will ever carry data. The refactoring from
`@ManyToMany` to explicit join entity involves a migration
of the join table and code changes in all callers.

---

### 🧠 Mental Model / Analogy

> `@ManyToMany` is like a party guest list. Each guest
> (Student) can attend many parties (Courses), and each
> party has many guests. The RSVP list (join table) links
> them. The host (owning side, Student) controls the RSVP
> list. When the host adds or removes a guest, the RSVP
> list is updated.
>
> The problem: if you need to add "RSVP'd at" timestamp
> and "dietary preference" to each RSVP, the RSVP becomes
> a proper entity (Enrollment) and the guest list becomes
> a real object in the system - not just a background table.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@ManyToMany` links two entity types where each can have
many of the other. The join table is managed automatically
by JPA.

**Level 2 - How to use it (junior developer):**
Put `@ManyToMany @JoinTable(...)` on the owning side
(the entity that "adds" members to the collection).
Put `@ManyToMany(mappedBy="courses")` on the other side.
Use `Set<Course>` (not `List`). Sync both sides.

**Level 3 - How it works (mid-level engineer):**
When `student.enroll(course)` adds to the owning side's
Set, Hibernate at flush time inserts a row in the join
table: `INSERT INTO student_courses (student_id, course_id)
VALUES (?, ?)`. When the course is removed from the set,
Hibernate deletes the join table row. The inverse side
`Course.students` is a view of the same join table from
the other direction - it is not independently managed.

**Level 4 - Why it was designed this way (senior/staff):**
`@ManyToMany` exists for the simple many-to-many case where
the join table is purely a linking table with no data.
JPA's spec designers knew that real applications often
need data on relationships (enrollment date, order
quantity, relationship type) - so the explicit join entity
pattern is the general solution. `@ManyToMany` is a
convenience shortcut for the subset of M:N cases with
no extra join data.

**Level 5 - Mastery (distinguished engineer):**
Using `@ManyToMany` in a domain model is an architectural
decision that limits future evolvability. Join tables
that start with "just two FKs" almost always gain columns
over time. By using an explicit join entity from the start,
the domain model mirrors the domain's actual semantics:
a Student-Course enrollment IS a domain concept, not just
a link. An explicit `Enrollment` entity with a proper
`@Id` and fields is more flexible, easier to query,
easier to audit, and easier to add behavior to. In DDD
terms, `@ManyToMany` hides a potential aggregate root
(the enrollment) inside a background join table.

---

### ⚙️ How It Works (Mechanism)

**SQL GENERATED FOR ENROLL:**

```sql
-- student.enroll(course):
INSERT INTO student_courses
  (student_id, course_id)
VALUES (1, 2)
```

**SQL GENERATED FOR DROP:**

```sql
-- student.drop(course):
DELETE FROM student_courses
WHERE student_id = 1 AND course_id = 2
```

**SQL GENERATED FOR LAZY LOAD:**

```sql
-- student.getCourses() first access:
SELECT c.id, c.title
FROM courses c
INNER JOIN student_courses sc ON c.id = sc.course_id
WHERE sc.student_id = 1
```

**N+1 WITH @ManyToMany:**
Loading 100 students and accessing `student.getCourses()`
on each -> 1 student query + 100 course collection queries
= 101 queries. Fix: JOIN FETCH in JPQL with DISTINCT or
`@EntityGraph`.

---

### 🔄 The Complete Picture - End-to-End Flow

**REGISTERING A STUDENT FOR COURSES:**

```java
@Transactional
public void registerCourses(Long studentId,
                            List<Long> courseIds) {
    Student student = studentRepo.findById(studentId)
        .orElseThrow();
    List<Course> courses =
        courseRepo.findAllById(courseIds);
    courses.forEach(student::enroll);
    // At commit: N INSERT INTO student_courses
}
```

**REMOVING ALL COURSES (CLEAR):**

```java
// Removes all join table rows for this student
student.getCourses().clear();
// Also sync inverse: (if needed)
student.getCourses().forEach(
    c -> c.getStudents().remove(student));
```

**FAILURE PATH:**
`cascade=ALL` on `@ManyToMany` and calling
`studentRepo.delete(student)` -> Hibernate cascades
`em.remove()` to each `Course` in `student.courses` ->
courses are DELETED from the `courses` table even though
other students are enrolled. This is the `CascadeType.ALL`
on `@ManyToMany` data loss anti-pattern.

---

### 💻 Code Example

**Example 1 - Standard @ManyToMany:**

```java
@Entity
public class User {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
}

@Entity
public class Role {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String name;

    @ManyToMany(mappedBy = "roles",
                fetch = FetchType.LAZY)
    private Set<User> users = new HashSet<>();
}
```

**Example 2 - BAD: CascadeType.ALL on @ManyToMany:**

```java
// BAD: cascade ALL on @ManyToMany
@ManyToMany(cascade = CascadeType.ALL)
@JoinTable(name = "student_courses", ...)
private Set<Course> courses;

// studentRepo.delete(student)
// -> CASCADE REMOVE: deletes all Course entities!
// -> All other students lose their courses

// GOOD: no cascade or only PERSIST/MERGE
@ManyToMany(cascade = {CascadeType.PERSIST,
                       CascadeType.MERGE})
@JoinTable(name = "student_courses", ...)
private Set<Course> courses;
// Only join table rows are managed; Course entities
// are not deleted when student is deleted
```

**Example 3 - Explicit join entity pattern (recommended for real domains):**

```java
@Entity
@Table(name = "user_roles")
public class UserRole {
    @EmbeddedId
    private UserRoleId id;

    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("userId")
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("roleId")
    private Role role;

    private LocalDateTime assignedAt;
    private String assignedBy;
}

@Embeddable
public class UserRoleId implements Serializable {
    private Long userId;
    private Long roleId;
    // equals + hashCode
}

// User now has:
@OneToMany(mappedBy = "user",
           cascade = CascadeType.ALL,
           orphanRemoval = true)
private List<UserRole> roles = new ArrayList<>();
```

---

### ⚖️ Comparison Table

| Approach             | Join table columns  | Attributes on join | Cascade safe       | Use case                        |
| -------------------- | ------------------- | ------------------ | ------------------ | ------------------------------- |
| `@ManyToMany`        | 2 FKs only          | No                 | Only PERSIST/MERGE | Simple tagging, role assignment |
| Explicit join entity | FKs + extra columns | Yes                | Full control       | When relationship has data      |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Use `CascadeType.ALL` on @ManyToMany for convenience"            | `CascadeType.ALL` includes `REMOVE`. Deleting a student cascades to remove all their Course entities - deleting courses other students are enrolled in. Never use `CascadeType.ALL` or `REMOVE` on `@ManyToMany`.                                          |
| "Changes to the @ManyToMany inverse side write to the join table" | Only the owning side (with `@JoinTable`) writes to the join table. Adding to the inverse `mappedBy` side has no effect on the database.                                                                                                                    |
| "Use List instead of Set for @ManyToMany collections"             | Using `List` for `@ManyToMany` can create duplicate join table entries and causes Hibernate to delete all join rows then re-insert them when the list changes. Always use `Set`.                                                                           |
| "Pure @ManyToMany is sufficient for most domain models"           | In most real domains, the M:N relationship eventually needs attributes (created_at, status, type). An explicit join entity is almost always the better choice. `@ManyToMany` is appropriate only for truly attribute-free relationships like product tags. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Data Loss From CascadeType.ALL**

**Symptom:** Deleting one student causes all courses
in their enrollment to be deleted from the `courses`
table. Other students' enrollments break with FK
violations or missing course data.

**Root Cause:** `@ManyToMany(cascade=CascadeType.ALL)`
cascades `em.remove()` to each entity in the collection -
including Course entities that are shared by other students.

**Diagnostic:**

```bash
spring.jpa.show-sql=true
# DELETE FROM courses WHERE id = ?
# (repeated for every course the deleted student had)
# -> Course entities being deleted (not just join rows)
```

**Fix:** Change to `cascade = {CascadeType.PERSIST, CascadeType.MERGE}`
or no cascade. Join table rows are managed implicitly;
explicit cascade of entity deletion is not appropriate
for shared M:N entities.

---

**Failure Mode 2: Duplicate Join Table Rows With List**

**Symptom:** `DataIntegrityViolationException: duplicate
entry` on the join table unique constraint, or duplicate
entries in the join table.

**Root Cause:** Using `List<Course>` instead of `Set<Course>`
for `@ManyToMany`. Adding a course twice results in two
join table INSERT attempts. Or: Hibernate's
collection dirty-checking on Lists deletes all join rows
and re-inserts them on any collection change.

**Fix:** Change `List<Course>` to `Set<Course>` for all
`@ManyToMany` collections. Implement `equals()` and
`hashCode()` on entities based on the natural key or PK.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-018 - @OneToMany and @ManyToOne]] - the building
  block that explicit join entities use
- [[JPH-020 - @JoinColumn and @JoinTable]] - customises
  the join table name and FK column names

**Builds On This (learn these next):**

- [[JPH-021 - FetchType (LAZY vs EAGER)]] - both sides
  of `@ManyToMany` should be LAZY
- [[JPH-022 - CascadeType]] - cascade rules differ for
  `@ManyToMany` vs `@OneToMany`
- [[JPH-027 - N+1 Problem (ORM Context)]] - `@ManyToMany`
  collections are a major N+1 source

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ M:N via join table; owning side has      │
│              │ @JoinTable; inverse side has mappedBy    │
├──────────────┼──────────────────────────────────────────┤
│ USE SET      │ Always Set<T>, never List<T> for M:N     │
│              │ collections                              │
├──────────────┼──────────────────────────────────────────┤
│ NEVER        │ cascade = CascadeType.ALL or REMOVE on   │
│              │ @ManyToMany -> deletes shared entities   │
├──────────────┼──────────────────────────────────────────┤
│ UPGRADE PATH │ When join table needs extra columns:     │
│              │ replace with explicit join entity +      │
│              │ two @ManyToOne mappings                  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "@ManyToMany: owning side has @JoinTable;│
│              │ use Set; never cascade=ALL/REMOVE;       │
│              │ prefer explicit join entity in production│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@ManyToMany` owning side (with `@JoinTable`) writes to
   the join table; inverse (`mappedBy`) side is ignored
2. NEVER use `CascadeType.ALL` or `REMOVE` on `@ManyToMany` -
   it deletes the shared entities, not just the join rows
3. When the join table needs any extra column, replace
   `@ManyToMany` with an explicit join entity + two
   `@ManyToOne` mappings

**Interview one-liner:** `@ManyToMany` maps M:N via a join
table; the owning side (with `@JoinTable`) writes join rows;
the inverse (`mappedBy`) side is read-only for persistence.
Use `Set` not `List`. Never cascade REMOVE across M:N
(it deletes the shared entities). When the join table needs
any attribute, upgrade to an explicit join entity with two
`@ManyToOne` associations.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any M:N relationship,
the join table is a latent entity waiting to be discovered.
The moment the join requires data (a timestamp, a status,
a quantity), the join table becomes a first-class domain
concept. Designing with explicit join entities from the
start (even if the join table starts empty) follows DDD's
"ubiquitous language" principle: if the business has a
name for the relationship (Enrollment, Assignment, Membership),
it deserves an entity class. This principle applies to:
microservice API design (many-to-many via relationship
resources), graph databases (edges carry attributes),
and event-sourced systems (join events carry metadata).

---

### 💡 The Surprising Truth

Hibernate handles `@ManyToMany` collection changes with
"delete all then re-insert" semantics for `List` collections.
When you add a single element to a `List<Course>` in a
`@ManyToMany`, Hibernate deletes ALL join table rows for
that student and re-inserts them all including the new one.
For a student enrolled in 50 courses, adding one course
generates 51 DELETE + 51 INSERT statements. Using
`Set<Course>` instead generates a single INSERT for the new
join row. This is why `Set` is mandatory for `@ManyToMany` -
not just for correctness but for performance.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **WRITE** a bidirectional `@ManyToMany` from scratch
   including correct `@JoinTable` configuration, sync
   helper methods, and `Set` collection type
2. **EXPLAIN** why `CascadeType.ALL` on `@ManyToMany` is
   dangerous and demonstrate with a delete scenario
3. **MIGRATE** a `@ManyToMany` to an explicit join entity
   when a new attribute is added to the join table
4. **DIAGNOSE** join table "delete all + re-insert" behavior
   by reading SQL logs and identifying the `List` vs `Set`
   root cause
5. **CHOOSE** between `@ManyToMany` and an explicit join
   entity for three different scenarios and justify each

---

### 🎯 Interview Deep-Dive

**Q1: What is the danger of using CascadeType.ALL on a
@ManyToMany relationship?**
_Why they ask:_ Common production bug; tests JPA cascade
depth knowledge.
_Strong answer includes:_

- `CascadeType.ALL` includes `CascadeType.REMOVE`
- Deleting the owning-side entity cascades `em.remove()`
  to all entities in the collection
- For M:N, these are SHARED entities (other parents
  reference them too)
- Result: deleting Student A deletes all Course entities
  that Student A was enrolled in, even if Students B,
  C, D are also enrolled in those courses
- Fix: use `cascade = {PERSIST, MERGE}` - join table rows
  are managed implicitly without cascade REMOVE

**Q2: Why should you use Set instead of List for @ManyToMany
collections?**
_Why they ask:_ Tests awareness of Hibernate's collection
dirty-checking behavior and the List vs Set performance trap.
_Strong answer includes:_

- Hibernate uses "delete all + re-insert" strategy for
  List changes in `@ManyToMany`
- Adding 1 item to a `List` of 100 join rows: DELETE 100,
  INSERT 101 -> 201 SQL statements
- `Set` tracks individual additions/removals:
  adding 1 item: 1 INSERT
- `Set` also prevents duplicate join table entries
  (adds to `Set` with same value are no-ops)
- Requires `equals()`/`hashCode()` on entity based on
  business key or PK

**Q3: When would you upgrade from @ManyToMany to an
explicit join entity?**
_Why they ask:_ Tests architectural thinking and JPA
design experience.
_Strong answer includes:_

- When the join table needs any additional columns
  (created_at, role, quantity, status)
- When you need to query or filter by the relationship
  itself (e.g., "enrollments in the last 30 days")
- When the relationship has its own lifecycle or audit
  requirements
- Design: explicit join entity with composite `@EmbeddedId`
  or surrogate PK + two `@ManyToOne` fields + `@OneToMany`
  on each parent
- Proactively: if the domain has a name for the relationship
  (Enrollment, Membership, Assignment), model it as an entity
