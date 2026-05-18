---
id: MSV-004
title: Modular Monolith
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-001, MSV-002
used_by: MSV-005, MSV-036, MSV-085
related: MSV-001, MSV-031, MSV-037, MSV-090
tags:
  - microservices
  - architecture
  - intermediate
  - pattern
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/microservices/modular-monolith/
---

⚡ TL;DR - A Modular Monolith is a single deployable unit with
rigidly enforced internal module boundaries, giving teams code
autonomy without the operational cost of distributed services.

| #004 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Microservices Architecture | |
| **Used by:** | Service Decomposition, Strangler Fig Pattern, Monolith to Microservices Migration | |
| **Related:** | Monolith vs Microservices, Domain-Driven Design, Decomposition by Business Capability, Anti-Patterns in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team has 20 engineers on a monolith. The monolith is a
"big ball of mud" - every module imports every other module,
there are circular dependencies, and you cannot change the
Order module without accidentally breaking the User module.
The suggestion: move to microservices. The reality: you are
not ready. No platform team, no distributed tracing, no
service mesh. You build 10 microservices and end up with a
distributed big ball of mud instead.

**THE BREAKING POINT:**
You need module autonomy but cannot stomach the operational
overhead of microservices. The standard advice of "start with
a monolith, extract services later" does not tell you HOW
to make the monolith safe to work in as it grows.

**THE INVENTION MOMENT:**
This is exactly why the Modular Monolith was formalised: to
apply the strict boundaries of microservices architecture
(each module owns its data, communicates via explicit APIs,
has no internal imports from other modules) inside a single
deployment unit. Teams get autonomy through code discipline
instead of deployment isolation.

**EVOLUTION:**
The pattern predates the term. Sam Newman's "Building
Microservices" (2015) warned against premature decomposition.
Robert Martin's "Clean Architecture" (2017) described module
isolation as the first step. "Modular Monolith: A Primer" by
Kamil Grzybek (2020) provided the canonical implementation
guide that popularised the term.

---

### 📘 Textbook Definition

A **Modular Monolith** is an application deployed as a single
artifact in which the codebase is partitioned into strongly
isolated modules, each representing a distinct business
domain or bounded context. Cross-module communication occurs
only through explicitly defined public APIs (interfaces),
not direct class imports. Each module manages its own data
schema (using separate database schemas or table prefixes
within one database), and module boundaries are enforced
by automated architecture tests.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Modular Monolith is a monolith with the discipline of
microservices - strict internal boundaries, explicit APIs,
no shared internals.

**One analogy:**
> An apartment building (modular monolith) versus a set of
> detached houses (microservices). The apartments share one
> building structure (JVM, deployment), but each apartment
> has its own front door (public API), its own interior
> (private code), and the landlord enforces no drilling
> through walls (no cross-module imports). Residents
> communicate via the hallway (the module API), not by
> climbing through windows.

**One insight:**
The value of microservices is not the network boundary - it
is the enforcement of the boundary. A Modular Monolith gets
the same enforcement via automated architecture tests
(ArchUnit, jMolecules) without the network cost.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each module exposes a public facade interface and hides
   all implementation classes as package-private.
2. No module imports classes from another module's internal
   packages - only public API interfaces.
3. Each module manages its own data using separate schemas
   or table prefixes; no module queries another module's tables.

**DERIVED DESIGN:**
From invariant 1: module boundaries are enforced in Java via
package visibility (`package-private` classes only accessible
within the package). Spring components annotated `@Bean` in
a module's public configuration are the only entry points.
From invariant 2: ArchUnit tests run in CI to fail the build
if any module imports another module's internal classes.
From invariant 3: each module's JPA entities are in its own
schema. Cross-module data needs go through the module's
public read API (CQRS-style query facade).

**THE TRADE-OFFS:**

**Gain:** Team code autonomy, clean boundaries, ability to
extract services later along proven boundaries, no network
overhead, no distributed consistency challenges.

**Cost:** Still one deployment unit (slower build for the
whole monolith), still one database instance (scaled as one),
boundary discipline requires ongoing code review and automation
enforcement.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Module boundaries require design discipline at
all times - humans drift. Automated enforcement is essential.

**Accidental:** Shared schema migrations (all modules must
migrate at once) are harder in a Modular Monolith than in
separate databases. This can be solved by treating schemas
as separate per module even within one DB instance.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams work on a monolith: Team Orders and Team Users.
Currently OrderService imports UserRepository directly
(shared DB access). You want to enforce that Orders can
only interact with Users through a public API.

**WHAT HAPPENS WITHOUT MODULAR MONOLITH DISCIPLINE:**
Team Users refactors UserRepository, renaming a method.
Team Orders' build breaks. Team Orders must update their
code. This happens every sprint. Neither team can move fast
without synchronizing with the other.

**WHAT HAPPENS WITH MODULAR MONOLITH:**
Team Users owns `UserModule` with a public interface:
`UserFacade.getUser(String userId): UserDTO`. Team Orders
only calls `UserFacade`. Team Users can refactor internals
freely. ArchUnit runs in CI and fails the build immediately
if any Orders class imports from `com.example.users.internal`.
Teams are decoupled in code, still sharing a JVM.

**THE INSIGHT:**
The interface is the contract. The enforcement mechanism
(ArchUnit, build-time check) is what makes the contract
real. Without enforcement, the contract degrades over time
under deadline pressure.

---

### 🧠 Mental Model / Analogy

> A Modular Monolith is like a well-organised office building:
> each department (module) has its own floor, its own
> receptionist (public facade), and internal rooms that
> visitors cannot access. Visitors (other modules) must
> go through the receptionist. The CEO (the application)
> can walk through the whole building but the rules still
> apply to everyone else.

- "Floor" - module package namespace
- "Receptionist" - public facade / interface
- "Internal rooms" - package-private implementation classes
- "Visitor" - code from another module
- "CEO walking through" - the Spring application context
  that wires everything together

Where this analogy breaks down: unlike a physical building,
code violations are invisible without automated checking.
The receptionist analogy only holds if ArchUnit is running.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A Modular Monolith is a single application that is carefully
divided into separate sections, each section with its own
clearly marked entrance. The sections cannot reach into each
other's files directly - they must use the official entrance.

**Level 2 - How to use it (junior developer):**
When adding a feature, keep all new code inside the module
it belongs to. Never import a class from another module's
`internal` subpackage. If you need data from another module,
ask the architect which public interface method to use.
Run `./gradlew architectureTest` before every commit.

**Level 3 - How it works (mid-level engineer):**
The structure uses Java package naming to enforce boundaries.
Each module has: `api/` (public interfaces), `facade/`
(Spring beans exposed as the public entry point), `domain/`
(package-private business logic), `infra/` (package-private
DB repositories). ArchUnit tests fail the build if any class
outside `api/` or `facade/` is referenced from another module.
Spring's `@Configuration` for each module is isolated - beans
are only shared via the facade interface.

**Level 4 - Why it was designed this way (senior/staff):**
The modular monolith pattern answers: "what is the cheapest
way to have service-like autonomy before you are ready for
microservices?" The boundaries map directly to future service
extraction - if Orders and Users have clean API boundaries
in the monolith, extracting Orders as a service later means
the API contract already exists, only the transport changes
(in-process call → HTTP). The migration is mechanical, not
architectural.

**Level 5 - Mastery (distinguished engineer):**
Staff engineers know the Modular Monolith as the preferred
architecture for 20-100 engineer organisations that are not
yet at the scale where microservices operational overhead
pays off. The key decision: are your bottlenecks team
coordination (suggests microservices) or operational
simplicity (suggests modular monolith)? Most companies
with sub-50 engineers and a single product have operational
simplicity as the priority. The modular monolith is often
the correct endpoint, not just a stepping stone.

---

### ⚙️ How It Works (Mechanism)

**FOLDER STRUCTURE:**

```
src/main/java/com/example/
├── orders/                    ← Orders Module
│   ├── api/
│   │   ├── OrderFacade.java   ← PUBLIC interface
│   │   └── OrderDTO.java      ← PUBLIC data type
│   ├── facade/
│   │   └── OrderFacadeImpl.java ← package-private impl
│   ├── domain/
│   │   ├── Order.java         ← package-private entity
│   │   └── OrderService.java  ← package-private service
│   └── infra/
│       └── OrderRepository.java ← package-private repo
│
├── users/                     ← Users Module
│   ├── api/
│   │   ├── UserFacade.java    ← PUBLIC interface
│   │   └── UserDTO.java       ← PUBLIC data type
│   ├── domain/                ← ALL package-private
│   └── infra/                 ← ALL package-private
│
└── Application.java           ← Only wires modules
```

**CROSS-MODULE COMMUNICATION:**

```
OrderService needs user data:

WRONG (breaks boundary):
  OrderService → imports UserRepository directly
  "I reach into the kitchen and grab the ingredients"

CORRECT (respects boundary):
  OrderService → calls UserFacade.getUser(userId)
  "I order from the menu - I don't know how it's made"

In code:
  // In orders/domain/OrderService.java
  // Only imports from users/api/ - never users/domain/
  private final UserFacade userFacade; // injected
  UserDTO user = userFacade.getUser(order.getUserId());
```

**ARCHITECTURE TEST (ArchUnit):**

```java
@AnalyzeClasses(packages = "com.example")
public class ModuleIsolationTest {

    @ArchTest
    static final ArchRule ordersDoNotTouchUsersInternals =
        noClasses()
            .that().resideInAPackage("..orders..")
            .should().accessClassesThat()
                .resideInAPackage(
                    "..users.domain.." // internal!
                );
}
// This test FAILS the build if the boundary is violated
```

---

### 🔄 The Complete Picture - End-to-End Flow

**REQUEST FLOW (modular monolith):**

```
HTTP Request
  │
  ▼
Spring DispatcherServlet
  │
  ▼
OrderController (orders module)  ← YOU ARE HERE
  │ calls OrderFacade (public API)
  ▼
OrderFacadeImpl (orders module)
  │ calls UserFacade (users module public API)
  ▼
UserFacadeImpl (users module)
  │ queries users schema in shared DB
  ▼
returns UserDTO to OrderFacadeImpl
  │ continues processing
  ▼
OrderRepository (orders module)
  │ writes to orders schema in shared DB
  ▼
HTTP Response
```

All in-process (nanosecond between modules). One transaction
can span both modules if needed.

**FAILURE PATH:**
```
UserFacadeImpl throws UserNotFoundException
  → OrderFacadeImpl catches, wraps in OrderException
  → OrderController returns 404 to client
  No distributed failure, no network timeout
```

**WHAT CHANGES AT SCALE:**
At moderate scale (< 100k RPM), the modular monolith runs
fine on 5-10 instances. At high scale, if the User module
and Order module have different load profiles, you cannot
scale them independently - this is when extraction to
separate services becomes rational.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: module boundary violation**

```java
// BAD: OrderService reaches into Users module internals
// This is the "big ball of mud" pattern
import com.example.users.domain.UserEntity; // INTERNAL!
import com.example.users.infra.UserRepository; // INTERNAL!

@Service
public class OrderService {
    @Autowired
    private UserRepository userRepo; // violates boundary!

    public Order create(OrderRequest req) {
        UserEntity user = userRepo // direct internal access
            .findById(req.getUserId());
        // ...
    }
}
```

```java
// GOOD: OrderService uses Users module public API only
import com.example.users.api.UserFacade; // PUBLIC only
import com.example.users.api.UserDTO;    // PUBLIC only

@Service
@RequiredArgsConstructor
public class OrderService {

    private final UserFacade userFacade; // public API

    public Order create(OrderRequest req) {
        // Only knows UserDTO - not UserEntity or UserRepository
        UserDTO user = userFacade.getUser(req.getUserId());
        return new Order(user.getId(), req.getItems());
    }
}
```

**Example 2 - Module configuration isolation**

```java
// Each module has its own Spring configuration
// Only beans in @Configuration are exposed to the app context
@Configuration
public class UsersModuleConfig {

    // PUBLIC: exposed to other modules via Spring context
    @Bean
    public UserFacade userFacade(
            UserRepository repo,
            UserMapper mapper) {
        return new UserFacadeImpl(repo, mapper);
    }

    // PRIVATE: internal beans not exposed by name
    @Bean
    UserRepository userRepository(DataSource ds) {
        return new JpaUserRepository(ds);
    }
    // Note: UserRepository is package-private class
    // Other modules cannot import or autowire it
}
```

**How to test / verify correctness:**
Add ArchUnit to the build and write tests that verify no
inter-module import of internal classes. Run as part of
`./gradlew test`. Any violation fails the build immediately.

---

### ⚖️ Comparison Table

| Architecture | Team Scale | Deploy Unit | Ops Overhead | When to Choose |
|---|---|---|---|---|
| **Modular Monolith** | 10-80 devs | One jar | Low | Growing team, unclear boundaries |
| Naive Monolith | 1-10 devs | One jar | Very Low | MVP, prototype |
| Microservices | 50+ devs | Per service | High | Scale + team autonomy required |
| Micro-frontends + Microservices | 100+ devs | Per feature | Very High | Large org, independent UIs |

**How to choose:** Choose Modular Monolith over a naive monolith
when you have 2+ teams working in the same codebase. Choose
Microservices over Modular Monolith when teams need deployment
independence (cannot tolerate one team's bug blocking another
team's release).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A Modular Monolith is just a monolith with good packaging | It requires AUTOMATED enforcement (ArchUnit) and data boundary rules - packaging conventions alone degrade within months. |
| Modules must use separate databases | Modules can use separate SCHEMAS within one database. Separate databases add operational overhead that is not required for the pattern. |
| Modular Monolith is just a step toward microservices | It is a valid endpoint for many organisations. Not every company needs microservices at all. |
| Module communication must be async | In-process synchronous calls are fine and are the default - the boundary is logical, not transport-based. |

---

### 🚨 Failure Modes & Diagnosis

**Boundary erosion under deadline pressure**

**Symptom:**
Six months after adopting the Modular Monolith, the codebase
has direct cross-module imports in 40+ places. Teams no longer
feel any benefit over the old approach.

**Root Cause:**
ArchUnit tests were added but run only locally. CI pipeline
did not include architecture tests. Developers skipped the
tests or `@ArchIgnore` was used to "temporarily" bypass checks.

**Diagnostic Command:**
```bash
# Run ArchUnit tests explicitly in CI
./gradlew architectureTest --info

# Count existing violations before fixing
grep -r "import com.example.users.domain" \
  src/main/java/com/example/orders/ | wc -l

# Check for @ArchIgnore suppressions
grep -r "@ArchIgnore" src/test/java/ | wc -l
```

**Fix:**
```java
// MANDATORY: ArchUnit tests must be in the main test suite
// NOT in a separate optional module
// ADD to build.gradle:
tasks.named('test') {
    // architecture tests run with all tests
    // test failures FAIL the build
}

// REMOVE all @ArchIgnore suppressions
// Fix violations or explicitly accept via a list file
```

**Prevention:**
Make architecture tests required in CI with zero-tolerance
for new violations. Every new violation must be reviewed and
either fixed or documented with a time-bounded exception.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` - understand why boundaries
  matter before learning how to enforce them
- `Domain-Driven Design` - module boundaries should map to
  DDD Bounded Contexts

**Builds On This (learn these next):**
- `Service Decomposition` - Modular Monolith boundaries become
  service boundaries when you extract
- `Strangler Fig Pattern` - how to extract services from a
  Modular Monolith incrementally
- `Bounded Context` - the DDD concept that maps to a module

**Alternatives / Comparisons:**
- `Monolith vs Microservices` - the spectrum from one unit
  with no boundaries to many units with network boundaries
- `Microservices Architecture` - stronger enforcement via
  network boundary; higher operational cost

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single deployable jar with enforced modul│
│              │ API boundaries and separate data schemas │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Monolith coupling without the solution of│
│ SOLVES       │ microservices operational overhead       │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Boundaries are only real if automatically│
│              │ enforced - ArchUnit in CI, not convention│
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ 2-4 teams in one codebase; microservices │
│              │ operational overhead not yet justified   │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Teams need independent deployment;       │
│              │ wildly different scaling profiles        │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Modular Monolith with no automated checks│
│              │ = just a monolith with a fancy name      │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Simple operations + easy debugging vs    │
│              │ single deploy unit, shared scale profile │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Microservices discipline, monolith ops -│
│              │  enforced by tests, not by the network"  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Decomposition → Strangler Fig    │
│              │ Pattern → Bounded Context                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Boundaries are only as strong as their enforcement - without
   ArchUnit in CI, module boundaries degrade within months.
2. Modules use separate database schemas (not separate DBs)
   for data isolation without operational overhead.
3. A well-structured Modular Monolith extracts to microservices
   easily because the service contracts already exist.

**Interview one-liner:**
"A Modular Monolith applies microservices architectural
discipline - module APIs, data isolation, no internal imports -
inside a single deployable unit. Boundaries are enforced by
automated architecture tests, not network calls. The best
starting point for a growing team before microservices
operational maturity is achieved."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Architectural boundaries are only maintained when enforced
automatically. Human discipline, code reviews, and naming
conventions all degrade under deadline pressure. The only
durable boundary is one that fails the build when violated.
This applies to API contract testing, security policy
enforcement, and code quality gates.

**Where else this pattern appears:**
- Layered architecture (controller/service/repo) - same
  principle of enforced directional dependencies
- Database schema ownership - each team owns its schema,
  enforced via access control
- API versioning - mandatory backward compatibility enforced
  by contract tests in CI

**Industry applications:**
- SaaS product companies (20-80 engineers) use Modular
  Monolith to maintain developer velocity without adopting
  microservices infrastructure before they need it
- Consulting firms rebuild legacy monoliths as Modular
  Monoliths first, then incrementally extract services as
  teams and boundaries become clearer

---

### 💡 The Surprising Truth

Shopify ran its multi-billion-dollar e-commerce platform as
a Ruby on Rails monolith for over a decade. Rather than
rewriting to microservices, they built a "componentised Rails
monolith" using strict module boundaries enforced by custom
tooling - the same Modular Monolith principles, applied to
Ruby. Their engineering blog posts revealed that the
productivity gain from avoiding distributed system complexity
outweighed the scaling constraints for their specific use
case for far longer than the industry expected.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Convince a skeptical architect why a Modular
   Monolith is preferable to microservices for a 30-engineer
   team, including the specific conditions that would change
   your recommendation.
2. **DEBUG** Given a codebase where module boundary violations
   exist in 30 places, write an ArchUnit test that fails the
   build for all violations and outline the migration plan.
3. **DECIDE** An engineering team's modular monolith has two
   modules with 10x different traffic profiles. At what point
   does this become a sufficient reason to extract one module
   as a separate service?
4. **BUILD** Create a three-module Spring Boot project
   (Orders, Users, Products) with ArchUnit tests enforcing
   module boundaries and separate database schemas.
5. **EXTEND** Apply Modular Monolith principles to a frontend
   React application: define what constitutes a "module
   boundary" in frontend code and how you would enforce it.

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates from a naive monolith to a Modular
Monolith. After 3 months, a database migration for the Users
module requires changing a column type, which will lock the
users table for 2 minutes. How does this affect the Orders
module if they share one database? Compare this scenario
with separate databases per module. What is the correct
mitigation strategy in a Modular Monolith context?
*Hint: Think about zero-downtime schema migrations and how
Flyway/Liquibase migrations interact with shared DB instances.*

**Q2.** Your Modular Monolith's Orders module and Payments
module call each other in a circular dependency: Orders
calls Payments to charge, Payments calls Orders to update
status. How do you resolve this circular dependency without
making the modules stateful or introducing a message broker?
What does this reveal about the module boundary design?
*Hint: Consider whether the boundary is drawn correctly or
whether a third "Transaction" module should own this flow.*

**Q3.** Design the module structure for a learning management
system (courses, students, payments, certificates). Define
each module's public API, its data schema ownership, and
the one cross-module interaction that is hardest to model
cleanly. Write the ArchUnit test that enforces the critical
boundary.
*Hint: Identify where payment and enrollment interact and
decide which module owns the "enrollment payment" concept.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between a Modular Monolith and
a well-organised monolith with good package structure?"**

*Why they ask:* Tests whether the candidate understands
that "modular" requires enforcement, not just convention.

*Strong answer includes:*
- Good packages = naming convention, enforced by humans
- Modular Monolith = automated enforcement (ArchUnit) that
  fails the build when violated
- Data isolation: Modular Monolith requires separate schemas
  per module - not just separate packages
- Facade pattern: only public API interfaces are exposed;
  implementation classes are package-private

**Q2: "When would you choose a Modular Monolith over
microservices for a company that already has 40 engineers?"**

*Why they ask:* Tests practical architectural judgment.

*Strong answer includes:*
- 40 engineers in one product: coordination overhead is
  manageable; microservices overhead may exceed benefit
- No platform team: without dedicated DevOps/SRE, microservices
  operational burden falls on product teams
- Unclear domain boundaries: premature decomposition creates
  wrong service boundaries that are expensive to fix
- Recommend: Modular Monolith now, extract services when
  specific teams feel real deployment independence pain

**Q3: "How would you incrementally migrate a 100k-line
monolith to a Modular Monolith without a big-bang rewrite?"**

*Why they ask:* Tests knowledge of safe, incremental migration.

*Strong answer includes:*
- Phase 1: Add ArchUnit to CI, initially in report mode only
  (do not fail build yet), to understand the violation count
- Phase 2: Fix circular dependencies between two modules
  you want to isolate first (start with the smallest boundary)
- Phase 3: Extract the public API of each module; mark
  internal classes as package-private
- Phase 4: Enable ArchUnit enforcement for the two isolated
  modules; block new violations
- Phase 5: Expand module by module over 6-12 months