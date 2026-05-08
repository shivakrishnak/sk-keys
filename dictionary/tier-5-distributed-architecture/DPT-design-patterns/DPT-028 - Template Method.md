---
layout: default
title: "Template Method"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 28
permalink: /design-patterns/template-method/
id: DPT-028
category: Design Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming (OOP), Inheritance, Abstract Classes, Polymorphism
used_by: Framework Design, Data Processing Pipelines, Test Lifecycle, HTTP Servlets
related: Strategy, Hook Method, Factory Method, Spring AbstractController
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
---

# DPT-028 - Template Method

⚡ TL;DR - Template Method defines the skeleton of an algorithm in a base class and lets subclasses fill in specific steps without changing the algorithm's overall structure.

| #788 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Inheritance, Abstract Classes, Polymorphism | |
| **Used by:** | Framework Design, Data Processing Pipelines, Test Lifecycle, HTTP Servlets | |
| **Related:** | Strategy, Hook Method, Factory Method, Spring AbstractController | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three report generators - `SalesReportGenerator`, `InventoryReportGenerator`, and `HRReportGenerator` - all follow the same process: connect to DB, query data, format output, send email. Each class independently implements all five steps. All three have identical connect/send-email code, subtly diverging over time: one uses connection pooling, another doesn't; one formats dates differently. When the email sender changes, three classes need updating. Duplication creates three maintenance surfaces where there should be one.

**THE BREAKING POINT:**
The invariant parts (connect, send) keep diverging because they're duplicated. A security bug in the DB connection logic must be fixed in 17 different report classes. The "algorithm structure" - step 1, then 2, then 3 - is not expressed anywhere; it's only implied by reading each class individually.

**THE INVENTION MOMENT:**
This is exactly why the Template Method pattern was created. The invariant steps live in the base class. Only the variant steps are abstract - subclasses fill in the specific logic for their report type without touching the structure.

---

### 📘 Textbook Definition

The **Template Method** pattern is a behavioural design pattern that defines the skeleton of an algorithm in a base class method (the **template method**) using a series of steps. Some steps are implemented in the base class (invariant); other steps are declared `abstract` (variant) and must be overridden by subclasses. The template method is typically `final` to prevent subclasses from altering the algorithm's structure. **Hook methods** are optional steps in the base class with default (usually no-op) implementations that subclasses can optionally override.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A base class says "do A, then B, then C" - subclasses fill in what B means for them.

**One analogy:**
> A recipe template says: "prepare ingredients → cook → plate → serve." The recipe's STRUCTURE is fixed. The specific ingredients and cooking technique are filled in differently for each dish. "Prepare" for pasta means boil water; for sushi it means slice fish. The flow never changes - only the specifics do.

**One insight:**
Template Method is the Hollywood Principle: "Don't call us - we'll call you." The base class calls the subclass's methods, not the other way around. The framework/base class is in control of the flow; subclasses plug in their variation without controlling when they are called.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An algorithm has a fixed overall structure (steps A → B → C → D).
2. Some steps vary between specialisations; others are identical.
3. The structure must not be duplicated in each specialisation.

**DERIVED DESIGN:**
Given invariant 1+3: the `templateMethod()` in the base class defines the steps in sequence. Given invariant 2: invariant steps are concrete (fully implemented) in the base. Variant steps are `abstract` - subclasses MUST implement them. Optional variation points are hooks - concrete base methods subclasses CAN override.

Making `templateMethod()` final prevents subclasses from reordering steps (which would break the algorithm's structure guarantee). Abstract steps enforce that mandatory custom logic is provided. Hook methods provide extension points without making them mandatory.

**THE TRADE-OFFS:**
**Gain:** Eliminates algorithmic structure duplication; invariant code in one place; subclasses only override what they need to vary; framework controls extension points.
**Cost:** Requires inheritance - the Liskov Substitution Principle must hold for all subclasses; deep hierarchies make the flow hard to trace; Strategy offers the same extension via composition without inheritance.

---

### 🧪 Thought Experiment

**SETUP:**
A data pipeline has three stages for every data source: (1) extract, (2) transform, (3) load. The extract logic differs per source (CSV file vs REST API vs DB query). Transform and load are identical for all sources.

**WHAT HAPPENS WITHOUT TEMPLATE METHOD:**
`CsvPipeline`, `ApiPipeline`, and `DbPipeline` each implement all three steps. Transform and Load logic is copy-pasted. A bug fix in the Load step must be applied to three classes. When a fourth source is added, the developer copies the whole pipeline and often forgets to update one of the invariant steps.

**WHAT HAPPENS WITH TEMPLATE METHOD:**
`AbstractDataPipeline` contains the `run()` template method: `extract()` → `transform()` → `load()`. `transform()` and `load()` are fully implemented in the base. `extract()` is abstract. Each subclass implements only `extract()`. A bug fix in `load()` is applied once.

**THE INSIGHT:**
Template Method says: here is the algorithm's invariant skeleton - subclasses contribute only the parts that MUST vary. The invariant is de-duplicated automatically.

---

### 🧠 Mental Model / Analogy

> Template Method is like a franchise restaurant's kitchen manual. The headquarters (base class) specifies: "Step 1: take order. Step 2: prepare base. Step 3: add toppings. Step 4: cook. Step 5: serve." Steps 1, 4, and 5 are identical everywhere (franchise standard). Step 2 and 3 differ per location's menu variation. Each franchise location (subclass) fills in the specifics for their menu without changing the overall service flow.

- "Franchise kitchen manual" → base class with `templateMethod()`
- "Standard steps" → concrete methods in base class
- "Fill-in-your-toppings" → abstract methods subclasses override
- "Optional sauces on the side" → hook methods (override if needed)
- "Policy: always cook at 180°C" → `templateMethod()` is `final`

Where this analogy breaks down: real franchises can negotiate deviations from some standard steps. In code, a `final` template method has zero exceptions - no subclass can reorder steps. If full flexibility is needed, Strategy (composition) is the better choice.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Template Method is like a fill-in-the-blanks form. The form structure is fixed. Each person (subclass) fills in their specific answers. Nobody redesigns the form - they just fill in the blanks.

**Level 2 - How to use it (junior developer):**
Create an `abstract` base class. Implement the `templateMethod()` as `final` - it calls invariant methods (concrete) and variant methods (abstract) in order. Subclasses extend the base and implement only the `abstract` methods. To add optional extension points, add `protected` hook methods with empty implementations in the base.

**Level 3 - How it works (mid-level engineer):**
JUnit's test lifecycle is Template Method: `@BeforeAll`, `@BeforeEach`, test method, `@AfterEach`, `@AfterAll` define the skeleton. The test framework calls these in the correct order - your test class fills in the body. `HttpServlet.service()` is Template Method: it dispatches to `doGet()`, `doPost()`, etc. - the servlet container controls the loop; you implement the specific handler. Template Method works through the inheritance invocation mechanism: the JVM dispatches a virtual method call to the most-derived implementation, so the base class genuinely calls the subclass's code when it calls `abstract` methods.

**Level 4 - Why it was designed this way (senior/staff):**
Template Method was the dominant framework extension mechanism before dependency injection and functional programming became mainstream. Pre-Spring, J2EE developers subclassed `HttpServlet`, overrode `doGet()`/`doPost()`, and the servlet container called their code. This is pure Template Method. The pattern's fundamental weakness is the fragile base class problem: a change to the base class's template method can break all subclasses without compiler warning. Adding a new required step to the template changes the abstract interface, and every subclass must be updated. Strategy solves this via composition - the "template" is wired from the outside, and adding a new step requires only the calling code to pass an additional strategy. Modern frameworks (Spring Boot) prefer @Bean injection over Template Method subclassing for exactly this reason.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────────┐
│  TEMPLATE METHOD PATTERN                          │
│                                                   │
│  AbstractReportGenerator                          │
│  ┌─────────────────────────────────────────┐      │
│  │ final generateReport():                 │      │
│  │   1. connect()         ← concrete       │      │
│  │   2. fetchData()       ← ABSTRACT       │      │
│  │   3. formatOutput()    ← ABSTRACT       │      │
│  │   4. beforeSend()      ← hook (no-op)   │      │
│  │   5. sendEmail()       ← concrete       │      │
│  └─────────────────────────────────────────┘      │
│                                                   │
│  SalesReport         InventoryReport              │
│  ┌──────────────┐    ┌──────────────┐             │
│  │ fetchData()  │    │ fetchData()  │             │
│  │ = SELECT...  │    │ = JOIN inv...│             │
│  │ formatOutput │    │ formatOutput │             │
│  │ = CSV format │    │ = PDF format │             │
│  └──────────────┘    └──────────────┘             │
└───────────────────────────────────────────────────┘
```

**Calling flow:**
1. Client calls `salesReport.generateReport()`
2. JVM looks up `generateReport()` - found on base class (`final`)
3. Base class executes: `connect()` (concrete, base code runs)
4. Base class calls `fetchData()` - ABSTRACT, JVM dispatches to `SalesReport.fetchData()` - subclass code runs
5. Base class calls `formatOutput()` - dispatches to `SalesReport.formatOutput()`
6. Base class calls `beforeSend()` - hook, base's no-op runs (SalesReport didn't override it)
7. Base class executes `sendEmail()` - concrete, base code runs
8. Complete. The flow was entirely controlled by base class.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Caller: scheduledJob.run()
  → salesReport.generateReport()
       ← YOU ARE HERE (template method starts)
  → base: connect()
  → base calls: SalesReport.fetchData()
      → hits DB, returns rows
  → base calls: SalesReport.formatOutput()
      → returns CSV string
  → base: beforeSend() (hook - no-op here)
  → base: sendEmail(csvContent)
  → report delivered
```

**FAILURE PATH:**
```
SalesReport.fetchData() throws DataAccessException
  → bubbles through generateReport()
  → base class has no catch → propagates to caller
Fix: base class can catch in template method:
  try { fetchData(); }
  catch (Exception e) { handleFetchError(e); }
  // handleFetchError can be a hook method
```

**WHAT CHANGES AT SCALE:**
With 1,000 concurrent report generations on the same `AbstractReportGenerator` base class, the invariant `connect()` and `sendEmail()` methods must be thread-safe. If the base class uses instance fields (bad), concurrent calls corrupt state. At scale, each `generateReport()` invocation should run on a new subclass instance - never share report instances across threads.

---

### 💻 Code Example

**Example 1 - Data pipeline Template Method:**
```java
// Base class with template method
public abstract class DataPipeline {

    // TEMPLATE METHOD - final, defines the skeleton
    public final void run() {
        List<Record> raw = extract();  // abstract
        List<Record> processed = transform(raw); // concrete
        load(processed);               // concrete
        afterLoad();                   // hook
    }

    // Must be implemented by each subclass
    protected abstract List<Record> extract();

    // Invariant: same transformation for all pipelines
    protected List<Record> transform(List<Record> data) {
        return data.stream()
            .filter(r -> r.isValid())
            .collect(toList());
    }

    // Invariant: same load logic for all pipelines
    protected void load(List<Record> data) {
        dataWarehouse.bulkInsert(data);
    }

    // Hook: optional post-load action (default no-op)
    protected void afterLoad() { }
}

// Concrete subclass - only implements the variant step
public class CsvDataPipeline extends DataPipeline {
    private final String filePath;

    @Override
    protected List<Record> extract() {
        return CsvReader.read(filePath)
            .stream()
            .map(Record::fromCsvRow)
            .collect(toList());
    }
    // Uses base transform() and load() unchanged
}

public class ApiDataPipeline extends DataPipeline {
    private final String apiUrl;

    @Override
    protected List<Record> extract() {
        return httpClient.get(apiUrl)
            .body()
            .asRecords();
    }

    // Overrides the hook for API-specific post-load logic
    @Override
    protected void afterLoad() {
        httpClient.acknowledgeIngestion(apiUrl);
    }
}

// Usage
new CsvDataPipeline("/data/sales.csv").run();
new ApiDataPipeline("https://api.example.com/data").run();
```

**Example 2 - JUnit lifecycle as Template Method:**
```java
// JUnit 5 is the "framework" - Test is the "subclass"
class OrderServiceTest {

    // @BeforeEach = hook (overridable)
    @BeforeEach
    void setup() {
        // Your setup code - called by JUnit's template
        orderService = new OrderService(mockRepo);
    }

    // Test method = abstract step - filled in by you
    @Test
    void pay_transitions_to_paid_state() {
        Order order = new Order();
        orderService.pay(order);
        assertThat(order.getStatus()).isEqualTo(PAID);
    }

    @AfterEach
    void teardown() { /* cleanup */ }

    // JUnit's template: beforeAll → beforeEach →
    //   runTest → afterEach → afterAll
    // You fill in the blanks - JUnit controls the flow
}
```

---

### ⚖️ Comparison Table

| Approach | Extension Mechanism | Algorithm Control | New Variant | Best For |
|---|---|---|---|---|
| **Template Method** | Inheritance | Base class | New subclass | Algorithm with fixed structure |
| Strategy | Composition | Caller injects | New class + inject | Interchangeable algorithms |
| Hook-only Base Class | Inheritance (optional) | Base class | Override hooks | Optional extension points |
| Default Interface Methods | Interface + impl | Caller | Override method | Mixin behaviour |

How to choose: use Template Method when there is a clear invariant algorithm skeleton shared by many specialisations. Use Strategy when the whole algorithm (not just steps) needs to be swappable, or when composition is preferred over inheritance.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Template Method and Strategy are interchangeable | Template Method uses inheritance; Strategy uses composition. They can achieve similar results but through fundamentally different mechanisms |
| Making the template method `final` is optional | It should almost always be `final`. Without it, subclasses can reorder or skip steps, breaking the invariant structure the pattern provides |
| Hook methods must be used | Hooks are optional extension points. They're useful when only SOME subclasses need a specific extension point. If all subclasses must implement a step, it should be abstract |
| Template Method is only for large algorithms | It applies to any sequence of steps where some are invariant and some vary - even a 3-step process |
| Subclasses should override the template method | Subclasses override ONLY the abstract and hook steps - never the template method itself (which should be final) |

---

### 🚨 Failure Modes & Diagnosis

**1. Subclass Overrides Template Method - Breaks Invariant**

**Symptom:** Security audit logging stops working for all PDF reports. `PdfReportGenerator.generateReport()` runs without audit logs.

**Root Cause:** `PdfReportGenerator` overrides `generateReport()` (which is not `final`) with its own implementation that skips `auditLog()`.

**Diagnostic:**
```bash
# Find overrides of the template method
grep -rn "generateReport\(\)" src/ --include="*.java"
# If found in subclasses: override exists
```

**Fix:**
```java
// BAD: template method not final
public class AbstractReport {
    public void generateReport() { // not final!
        fetchData(); auditLog(); format(); send();
    }
}
// PdfReport can override and skip auditLog()

// GOOD: final prevents override
public abstract class AbstractReport {
    public final void generateReport() { // final!
        fetchData(); auditLog(); format(); send();
    }
}
```

**Prevention:** Always mark template methods `final`. Code review rule: no method named `*Template*` or acting as template method should be non-final.

---

**2. Fragile Base Class - New Step Breaks All Subclasses**

**Symptom:** Adding a mandatory validation step to the base template causes `AbstractMethodError` at runtime for a subclass that hasn't been updated.

**Root Cause:** Base class adds a new `abstract` method `validate()` to the template. One subclass in a different module wasn't recompiled after the base class change.

**Diagnostic:**
```bash
# Check for AbstractMethodError at runtime
grep "AbstractMethodError" logs/app.log
# Check which subclass is causing it
grep -A 5 "AbstractMethodError" logs/app.log
```

**Fix:**
When adding a new step that most subclasses should use but some might opt out of, use a hook (default implementation) instead of abstract:
```java
// BAD: new abstract step breaks all subclasses
protected abstract void validate(); // all must implement

// GOOD: hook with default - subclasses opt in
protected void validate() { /* safe default: no-op */ }
```

**Prevention:** Prefer hook methods over abstract methods when extending an algorithm with new steps. Reserve abstract for truly mandatory steps added at design time.

---

**3. Instance State in Base Class - Thread Safety Issue**

**Symptom:** Report content from one user appears in another user's report under concurrent load.

**Root Cause:** Base class stores intermediate results in instance fields (`protected List<Record> data`). Shared instance between threads contaminates state.

**Diagnostic:**
```bash
# Thread dump during corruption
jstack <PID> | grep -A 20 "generateReport"
# Multiple threads on same instance = evidence
```

**Fix:**
```java
// BAD: shared state in base class instance fields
public abstract class AbstractReport {
    protected List<Record> data; // shared by all calls!
    public final void generateReport() {
        data = fetchData(); // first thread sets it
        format(data); // second thread reads wrong data
    }
}

// GOOD: pass data through method parameters
public abstract class AbstractReport {
    public final void generateReport() {
        List<Record> data = fetchData(); // local variable
        String formatted = format(data); // pass through
        send(formatted);
    }
}
```

**Prevention:** Avoid instance fields in base class for intermediate pipeline data. Use method parameters or `ThreadLocal` if cross-step state is genuinely needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Abstract Classes` - Template Method is implemented using abstract base classes; understanding abstract vs concrete methods drives the pattern
- `Inheritance` - Template Method relies on inheritance for call dispatch; the base calls the subclass's implementation of abstract methods
- `Polymorphism` - the mechanism by which `abstract fetchData()` in the base class resolves to the correct subclass override at runtime

**Builds On This (learn these next):**
- `Strategy` - the composition alternative to Template Method; when inheritance becomes too rigid, Strategy provides the same variation via injected objects
- `Factory Method` - often combined with Template Method; the factory method is an abstract method in a base class, making it a specialised Template Method
- `Hook Method` - the optional extension variant of Template Method used when not all subclasses need to override a step

**Alternatives / Comparisons:**
- `Strategy` - composition instead of inheritance; more flexible but requires explicit injection; preferred in modern Java
- `Decorator` - adds behaviour around an existing algorithm; Template Method structures the algorithm from scratch in the base
- `Chain of Responsibility` - also sequences operations, but through linked handlers; Template Method sequences in a single class hierarchy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Algorithm skeleton in base class; variant │
│              │ steps as abstract methods for subclasses  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Algorithm structure duplicated across     │
│ SOLVES       │ specialisations; invariant steps diverge  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Hollywood Principle: base class calls     │
│              │ subclass, not the other way around        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many classes share an algorithm skeleton; │
│              │ only specific steps vary per subclass     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Algorithm structure itself varies; prefer │
│              │ Strategy (composition) over inheritance   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Invariant deduplication vs inheritance    │
│              │ fragility and class hierarchy depth       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't call us - we'll call you."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy → Factory Method →               │
│              │ Hook Method                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team uses Template Method for a data pipeline base class. Over two years, the base class has accumulated 14 hook methods, 6 abstract methods, and 3 concrete methods. The class has 22 subclasses. A new requirement says: "Some pipelines need step 3 before step 2 in certain conditions." Describe exactly why Template Method cannot satisfy this requirement, and explain why this signals that the team should migrate to a different pattern - including the specific migration steps.

**Q2.** Template Method and Strategy solve the same problem - varying algorithm behaviour - but one uses inheritance and the other uses composition. A team argues that Template Method is always replaceable by Strategy. Is this strictly true? Identify one scenario where Template Method's inheritance mechanism provides something Strategy cannot replicate without adding extra complexity, and one scenario where Template Method's inheritance creates a problem that Strategy's composition avoids.

