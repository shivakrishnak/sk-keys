---
id: SAP-044
title: Onion Architecture
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-063, SAP-064, SAP-065
used_by: SAP-008, SAP-018
related: SAP-063, SAP-064, SAP-007
tags:
  - architecture
  - pattern
  - advanced
  - first-principles
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /software-architecture/onion-architecture/
---

# SAP-017 - Onion Architecture

⚡ TL;DR - Onion Architecture wraps the domain in concentric layers where every layer depends only on layers closer to the centre, never on layers further out.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-063, SAP-064, SAP-065 |
| **Used by**    | SAP-008, SAP-018          |
| **Related**    | SAP-063, SAP-064, SAP-007 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A traditional layered application has the domain at the top of the call stack but at the bottom of the dependency stack - everything depends on the database schema. When the DBA decides to normalise a table, the domain objects change, the service objects change, and the controllers change. The domain - the most valuable and most stable part of the application - is the most fragile, because it sits on top of unstable infrastructure.

**THE BREAKING POINT:**
You want to introduce a new persistence mechanism for high-traffic reads. You prototype it in two days, but it takes three weeks to integrate because the domain objects contain JPA annotations that tie them to the existing persistence strategy. The domain object cannot be tested without the database.

**THE INVENTION MOMENT:**
This is exactly why Onion Architecture was created - to invert the dependency structure so that the domain is at the centre and infrastructure wraps around it, making the domain the most independent layer rather than the most dependent.

**EVOLUTION:**
Jeffrey Palermo coined Onion Architecture in 2008, building explicitly on Hexagonal Architecture (2005) and identifying that it lacked a named boundary between application services and domain logic. Palermo made the Domain Services ring explicit - a ring for domain logic spanning multiple entities - which Hexagonal Architecture had left implicit. The "Onion" metaphor emphasised the concentric, layered structure more than the hexagonal diagram. Clean Architecture (2017) later synthesized Onion, Hexagonal, and BCE (Jacobson, 1992) into a unified model. Onion Architecture remains the most influential precursor to Clean Architecture.

---

### 📘 Textbook Definition

Onion Architecture, introduced by Jeffrey Palermo in 2008, is a domain-centric architectural pattern that organises the application into concentric layers resembling an onion. The innermost layer is the Domain Model (Entities, Value Objects). Surrounding it is the Domain Services layer. Outside that is the Application Services layer. The outermost layers contain Infrastructure and UI. The fundamental rule is that inner layers define interfaces; outer layers implement them. All source code dependencies point inward, making the domain completely infrastructure-independent.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Your domain is the core of the onion; infrastructure is the outer skin you peel away.

**One analogy:**

> A real onion has its most vital layers in the core - that's what keeps the plant alive. The outer skin is disposable and interchangeable. You can replant the bulb in any soil. In Onion Architecture, the domain is the bulb: you can plug it into any infrastructure (soil) without changing it.

**One insight:**
The difference between Onion and Layered Architecture is the direction of dependencies. Layered: Presentation → Business → Database (UI knows nothing, DB knows everything). Onion: everything points inward toward the Domain. The Database adapter depends on the Domain interface, not the other way around.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The Domain Model (entities, value objects) has zero dependencies on anything outside itself.
2. Domain Services contain domain logic that doesn't naturally fit a single entity - but they still have zero infrastructure dependencies.
3. Application Services orchestrate domain objects and define what the application can do.
4. Infrastructure implements the interfaces that Application Services and Domain Services define.

**DERIVED DESIGN:**

```
┌──────────────────────────────────────────────────────┐
│              ONION ARCHITECTURE LAYERS               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌── Infrastructure / UI (outermost) ──────────┐     │
│  │  ┌── Application Services ──────────────┐   │     │
│  │  │  ┌── Domain Services ─────────────┐  │   │     │
│  │  │  │  ┌── Domain Model ──────────┐  │  │   │     │
│  │  │  │  │  Entities, Value Objects  │  │  │   │     │
│  │  │  │  └──────────────────────────┘  │  │   │     │
│  │  │  │  Business rules, Domain Events │  │   │     │
│  │  │  └────────────────────────────────┘  │   │     │
│  │  │  Use Cases, Transaction Boundaries   │   │     │
│  │  └──────────────────────────────────────┘   │     │
│  │  DB, HTTP, Email, Messaging, Tests           │     │
│  └──────────────────────────────────────────────┘     │
│                                                      │
│  All arrows: outer layer → inner layer               │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** The domain model is perfectly isolated - testable in milliseconds, deployable against any infrastructure, readable without framework knowledge.
**Cost:** More layers mean more classes, more interfaces, more mapping. The outermost ring (infrastructure) must translate between the domain's language and the infrastructure's language at every boundary. Simple operations cross more abstraction layers than necessary.

Could we have fewer layers? Yes - Hexagonal Architecture uses only two logical zones (domain + everything else). Onion Architecture's contribution is making explicit the distinction between domain rules that cross entities (Domain Services) and application-specific orchestration (Application Services).

---

### 🧪 Thought Experiment

**SETUP:**
You have a loan approval domain. Entities: `Applicant`, `LoanApplication`. Domain Service: `CreditEvaluationService`. Application Service: `LoanApplicationService`.

**WHAT HAPPENS WITHOUT ONION ARCHITECTURE:**
`LoanApplicationService` calls `JpaCreditScoreRepository.findByApplicantId()` directly. When you add a second credit bureau, you modify `LoanApplicationService`. When you add caching, you modify `LoanApplicationService`. Business logic becomes entangled with infrastructure decisions - a change to the Redis cache invalidation logic requires reading through loan approval rules.

**WHAT HAPPENS WITH ONION ARCHITECTURE:**
`LoanApplicationService` calls `CreditScoreRepository` - an interface defined in the Application Services ring. The JPA implementation in the Infrastructure ring implements it. You add a `CachingCreditScoreRepository` (Infrastructure ring) that wraps the JPA implementation - zero changes to Application Services or Domain. The domain has never heard of Redis.

**THE INSIGHT:**
Every infrastructure change is local to the outermost ring. Domain logic never changes because infrastructure changes. This isolation is only possible if the dependency direction is strictly enforced.

---

### 🧠 Mental Model / Analogy

> Think of a medieval fortress: the royal palace (Domain Model) is at the centre, completely self-sufficient. Around it, the court (Domain Services) handles affairs. Around that, the administrative offices (Application Services) manage operations. The outer walls and gates (Infrastructure) connect to the outside world. Attackers can breach the outer walls, but the palace rules are unchanged.

- "Royal palace" → Domain Model (Entities, Value Objects)
- "Court" → Domain Services (business logic spanning entities)
- "Administrative offices" → Application Services (use cases, orchestration)
- "Outer walls" → Infrastructure (JPA, HTTP, messaging)
- "Drawbridge" → Interface (port defined by inner, implemented by outer)

Where this analogy breaks down: In a real fortress, the palace can send messengers outside. In Onion Architecture, the Domain Model cannot directly call anything outside itself - it must fire events or define interfaces.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Onion Architecture organises your application in layers like an onion. The business rules are in the very centre. Code can always look inward (toward the centre) but never outward. The database and web server are the outer skin - replaceable.

**Level 2 - How to use it (junior developer):**
Your project has four main packages: `domain.model` (entities, value objects - zero imports from outside), `domain.service` (business logic methods), `application` (use cases that wire domain objects together), and `infrastructure` (Spring, JPA, REST clients). Only the infrastructure package has framework annotations. Application and Domain packages are plain Java.

**Level 3 - How it works (mid-level engineer):**
The critical mechanism is interface ownership: interfaces are defined in the inner ring, implemented in the outer ring. `Application.IOrderRepository` is defined in the application layer. `Infrastructure.JpaOrderRepository implements Application.IOrderRepository` is in the infrastructure layer. Dependency Injection in the composition root (Spring configuration class) wires the outer implementation to the inner interface, satisfying the Dependency Inversion Principle. Tests substitute InMemory implementations.

**Level 4 - Why it was designed this way (senior/staff):**
Palermo's key contribution over the simple Hexagonal approach was the explicit separation of Domain Services from Application Services. Domain Services (ring 2) encapsulate business rules that span multiple entities but don't belong to any single entity - for example, `TransferMoneyDomainService` coordinates `SourceAccount` and `TargetAccount`. Application Services (ring 3) coordinate Domain Services and define transactional boundaries. This distinction prevents the "fat application service" anti-pattern where application services accumulate business logic that belongs in the domain.

---

### ⚙️ How It Works (Mechanism)

**Layer interactions during a "Transfer Money" operation:**

1. **Infrastructure (Controller)** receives HTTP POST `/transfers`. Maps JSON body to `TransferMoneyCommand`. Calls `TransferMoneyApplicationService.execute(command)`.

2. **Application Service** opens a transaction. Calls `AccountRepository.findById(sourceId)` (interface defined here, implemented in Infrastructure). Calls `TransferMoneyDomainService.transfer(source, target, amount)`.

3. **Domain Service** applies business rule: source must have sufficient balance; target must be active. Calls `source.debit(amount)` and `target.credit(amount)`. Raises `MoneyTransferredEvent`.

4. **Domain Model** (`Account` entity) validates and applies the debit/credit. Domain events are collected in the aggregate.

5. **Application Service** calls `AccountRepository.save(source)` and `AccountRepository.save(target)`. Publishes domain events via `DomainEventPublisher` (another interface).

6. **Infrastructure** (JPA implementation) persists account changes. Event publisher sends events to Kafka.

```
┌─────────────────────────────────────────────────────────┐
│         ONION ARCHITECTURE - TRANSFER MONEY             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  HTTP Request                                           │
│      ↓                                                  │
│  [Infrastructure] HTTP Controller                       │
│      ↓ calls                                            │
│  [Application Services] TransferMoneyApplicationService │
│      ↓ calls                                            │
│  [Domain Services] TransferMoneyDomainService           │
│      ↓ calls                         ↑ interfaces       │
│  [Domain Model] Account entity       │ defined here     │
│      │ raises MoneyTransferredEvent  │                  │
│      ↓ returns                       │                  │
│  [Application Services] saves via AccountRepository ──→ │
│  [Infrastructure] JpaAccountRepository (implements)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
POST /transfers
  → HTTP Controller (Infrastructure)
  → TransferMoneyCommand (data object)
  → TransferMoneyApplicationService.execute()  ← YOU ARE HERE
  → AccountRepository.findById() [interface → JPA impl]
  → TransferMoneyDomainService.transfer()
  → Account.debit() / Account.credit()
  → AccountRepository.save() [interface → JPA impl]
  → PostgreSQL write
  → DomainEventPublisher [interface → Kafka impl]
  → HTTP 200 OK
```

**FAILURE PATH:**

```
Account.debit() throws InsufficientFundsException
  → DomainService propagates
  → ApplicationService catches → rolls back transaction
  → HTTP Controller maps to HTTP 422
```

**WHAT CHANGES AT SCALE:**
At high scale, the Application Services layer becomes the natural place to introduce CQRS - separate the write path (transactional, goes through all rings) from the read path (can short-circuit to a read-optimised repository in the infrastructure ring). The Domain Model remains unchanged.

---

### 💻 Code Example

**Example 1 - Domain Model (innermost - zero dependencies):**

```java
// DOMAIN MODEL - pure Java, no imports from outside
public class Account {
    private final AccountId id;
    private Money balance;
    private AccountStatus status;

    // Business rule lives HERE - not in services
    public void debit(Money amount) {
        if (balance.isLessThan(amount)) {
            throw new InsufficientFundsException(
                id, amount, balance
            );
        }
        balance = balance.subtract(amount);
    }

    public void credit(Money amount) {
        if (status == AccountStatus.CLOSED) {
            throw new AccountClosedException(id);
        }
        balance = balance.add(amount);
    }
}
```

**Example 2 - Application Services ring (interface ownership):**

```java
// Interface defined in Application ring
// Infrastructure must implement this
public interface AccountRepository {
    Account findById(AccountId id);
    void save(Account account);
}

// Application Service - orchestrates, doesn't contain rules
@Transactional
public class TransferMoneyApplicationService {
    private final AccountRepository accounts; // inner interface
    private final TransferMoneyDomainService transferSvc;

    public void execute(TransferMoneyCommand cmd) {
        Account source = accounts.findById(cmd.sourceId());
        Account target = accounts.findById(cmd.targetId());
        // Business rule execution delegated to domain service
        transferSvc.transfer(source, target, cmd.amount());
        accounts.save(source);
        accounts.save(target);
    }
}
```

**Example 3 - Infrastructure ring (outer, implements inner interface):**

```java
// Infrastructure - JPA implementation
// Depends on Application ring interface (inward dependency)
@Repository
public class JpaAccountRepository
        implements AccountRepository {  // inner ring interface

    @PersistenceContext
    private EntityManager em;

    @Override
    public Account findById(AccountId id) {
        AccountEntity entity = em.find(
            AccountEntity.class, id.value()
        );
        return AccountMapper.toDomain(entity);
    }

    @Override
    public void save(Account account) {
        em.merge(AccountMapper.toEntity(account));
    }
}
```

---

### ⚖️ Comparison Table

| Pattern                | Domain ring structure                | Key distinction                           | Best For                            |
| ---------------------- | ------------------------------------ | ----------------------------------------- | ----------------------------------- |
| **Onion Architecture** | Domain Model + Domain Services split | Explicit domain service ring              | DDD-heavy enterprise systems        |
| Clean Architecture     | Entities + Use Cases split           | Explicit Use Case ring, Presenter pattern | Systems with complex use-case rules |
| Hexagonal Architecture | Single domain zone                   | Driving vs driven port distinction        | Multi-delivery-mechanism systems    |
| Layered Architecture   | Domain is a single middle layer      | Horizontal layers, no inversion required  | CRUD-heavy, technical-role teams    |

**How to choose:** Use Onion Architecture when using Domain-Driven Design - the explicit Domain Services ring maps naturally to DDD's domain services concept. It's the most DDD-aligned architecture among the ring-based patterns.

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Onion and Layered Architecture are the same with different pictures | Layered allows domain to depend on DB abstractions; Onion forbids any outward dependency from the domain                               |
| Domain Services and Application Services are the same thing         | Domain Services contain business rules spanning entities; Application Services orchestrate and manage transactions                     |
| The outermost ring is least important                               | Infrastructure is the most code-dense ring; its quality determines performance and reliability                                         |
| Onion Architecture requires DDD                                     | It complements DDD naturally but can be applied without DDD concepts                                                                   |
| All validation belongs in the Domain Model                          | Presentation-layer validation (field format, required fields) belongs in the controller; business validation belongs in domain objects |

---

### 🚨 Failure Modes & Diagnosis

**Domain Service becoming Application Service (responsibility creep)**

**Symptom:** Domain Services begin managing transactions, loading multiple aggregates from repositories, and orchestrating infrastructure operations.

**Root Cause:** The boundary between Domain Services and Application Services is fuzzy - developers default to adding new logic to the "service" they already have open.

**Diagnostic Command / Tool:**

```bash
# Domain services that import repositories
grep -rn "import.*Repository\|@Transactional" \
  src/main/java/**/domain/service/
```

**Fix:** Domain Services should receive fully-loaded domain objects; they should never call repositories. Move any repository calls to Application Services.

**Prevention:** Review each Domain Service method - if it calls a repository, it's doing Application Service work.

---

**Fat Domain Model (too much in entities)**

**Symptom:** Entities import external libraries for formatting, currency conversion, or external API calls. Entity constructors require injected services.

**Root Cause:** Too much logic pushed into entities trying to keep everything in the "domain" ring, including infrastructure concerns.

**Diagnostic Command / Tool:**

```bash
# Entities with external imports
grep -rn "import" \
  src/main/java/**/domain/model/*.java \
  | grep -v "java\." | grep -v "domain\."
```

**Fix:** Entities should contain only state and the rules that apply directly to that state. Cross-entity coordination goes in Domain Services.

**Prevention:** Entities should have no constructor parameters that are service objects.

---

**Infrastructure ring as dumping ground**

**Symptom:** Infrastructure ring contains business logic spread across repository implementations, "helper" services, and mapper classes.

**Root Cause:** Developers resist adding new inner-ring classes and instead sneak logic into the infrastructure layer.

**Diagnostic Command / Tool:**

```bash
# Large non-trivial methods in infrastructure
grep -rn "if\|switch\|for\|while" \
  src/main/java/**/infrastructure/ \
  | grep -v "//\|test" \
  | wc -l
```

**Fix:** Business logic conditionals should not appear in infrastructure code. Move to appropriate inner ring layer.

**Prevention:** Infrastructure methods should contain only: data transformation, I/O calls, exception translation. No business conditions.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Concentric protection structures are a general mechanism for isolating the most stable and valuable core from volatile external dependencies. The innermost ring is the most protected because it has the fewest outward dependencies - any change in infrastructure cannot propagate inward past the port interface.

**Where else this pattern appears:**

- **OS CPU rings:** hardware enforces ring-0 (kernel) protection from ring-3 (user mode); a crash in a user-space process cannot corrupt kernel state - the architecture guarantees isolation through hardware-enforced boundaries.
- **Network security zones:** DMZ wraps the internal network which wraps the trusted core; outer zones expose services inward but the trusted core never initiates connections outward to the DMZ.
- **International law hierarchy:** UN Charter principles constrain national constitutions, which constrain national laws, which constrain regulations - inner documents cannot be overridden by outer documents; the dependency direction is inward only.

---

### 💡 The Surprising Truth

The "Onion" metaphor misleads many readers into thinking all rings should be approximately equal in size. In practice, the Domain Model ring (innermost) should be the largest - it contains all business logic. The Infrastructure ring (outermost) should be the thinnest - it is mostly wiring code. A production Onion Architecture where the outer rings contain most of the code is an architectural warning sign: business logic has leaked into infrastructure, making the innermost ring an empty shell.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-063 - Hexagonal Architecture (direct predecessor; Onion Architecture explicitly extends it with named Domain Services and Application Services rings)
- SAP-064 - Clean Architecture (synthesises Onion Architecture with Hexagonal and BCE into a unified model; understand the relationship)
- SAP-065 - Domain Model (the content of the innermost ring; understanding domain modelling fills the Onion meaningfully)

**Builds On This (learn these next):**

- SAP-008 - CQRS Pattern (commonly applied at the Application Services ring for read/write separation within the onion structure)
- SAP-018 - Event Sourcing Pattern (domain events in the Domain Model ring are the natural integration point with event sourcing strategies)

**Alternatives / Comparisons:**

- SAP-064 - Clean Architecture (synthesises Onion with explicit Use Case ring naming; more prescriptive about the application services layer)
- SAP-007 - Vertical Slice Architecture (orthogonal slicing by feature rather than by dependency ring; a different axis of organisation)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Concentric layers; domain at centre;      │
│              │ all dependencies point inward             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Domain tied to infrastructure makes       │
│ SOLVES       │ business rules fragile and untestable     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Inner rings define interfaces; outer      │
│              │ rings implement them - domain first       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DDD-heavy systems; domain model is rich   │
│              │ and must survive infrastructure changes   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; prototypes; small teams      │
│              │ without strong layer discipline           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Domain isolation vs mapping overhead      │
│              │ at every ring boundary                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Peel any layer away; the core            │
│              │  is always intact"                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Clean Architecture → DDD → CQRS          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In Onion Architecture, the Domain Services ring is supposed to contain business logic that spans multiple entities. A new requirement arrives: calculate the discounted price for a customer based on their membership tier, purchase history, and current promotional rules - each of which is a separate entity. Trace precisely which ring each piece of this calculation lives in, and what happens when promotional rules change weekly: which ring changes, and how are the other rings protected?

*Hint:* Research the rule for assigning responsibility to the Domain Services ring: logic that spans multiple aggregates but has no natural home in any single entity belongs in a Domain Service. The promotional rules are a Value Object or Entity in the Domain Model ring; the `PriceCalculationService` that combines them is a Domain Service. Research how Evans distinguishes services at each ring level (Domain Service vs Application Service vs Infrastructure Service).

**Q2.** A team implements Onion Architecture, but after six months discovers their application has 4 rings with 3 layers each, 47 interface definitions, and 47 corresponding implementations. Most of their logic is simple CRUD on 20 entities. At what point does the ring-based architecture's isolation benefit become an overhead that exceeds the cost of the occasional infrastructure coupling it prevents?

*Hint:* Research the concept of "fitness functions" and specifically the "last responsible moment" principle from Lean Software Development - the architectural pattern should be applied at the last moment before the problem it solves becomes painful, not in anticipation of pain that may never arrive. Look at how Martin Fowler's "Bliki" entry on "Is Design Dead?" addresses the cost/benefit of architecture investment in different domain complexities.

**Q3.** Two teams each implement a separate Bounded Context using Onion Architecture. Both contexts need a `Money` value object and a `CustomerId` type. Team A argues for a "shared kernel" package that both onions import as a dependency in their Domain Model ring. Team B argues each context should have its own `Money` and `CustomerId` to maintain independence. What does the Shared Kernel DDD pattern say about this, and how does importing a shared package into an inner ring affect each context's ability to evolve independently?

*Hint:* Research the "Shared Kernel" pattern from Evans' DDD - specifically the governance constraint that shared kernel code can only change by agreement of both teams, and compare with the "anti-corruption layer" alternative where each context maintains its own types and translates at the boundary. Consider: what happens when Team A needs `Money` to support cryptocurrency and Team B only uses fiat currency?
