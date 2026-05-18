---
id: DPT-028
title: Template Method
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-027
used_by: DPT-064
related: DPT-027, DPT-026, DPT-006
tags:
  - pattern
  - behavioral
  - intermediate
  - inheritance
  - framework
  - hooks
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/design-patterns/template-method/
---

⚡ TL;DR - Template Method defines the skeleton of an
algorithm in a base class and defers specific steps to
subclasses - the base class controls the algorithm
structure; subclasses provide the varying steps.

| #28 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-027 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-027, DPT-026, DPT-006 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An ETL (Extract-Transform-Load) pipeline must work for
three sources: CSV files, JSON APIs, and database tables.
All three follow the same steps: (1) connect to source,
(2) extract data, (3) validate schema, (4) transform
fields, (5) load to data warehouse, (6) disconnect.
Steps 1, 2, 4 vary by source; steps 3, 5, 6 are identical.

**WITHOUT TEMPLATE METHOD:**
Three separate ETL classes. Steps 3, 5, and 6 are copy-
pasted in all three (duplicate code, maintenance nightmare).
When the schema validation logic changes: update it in
three places. When a new "Parquet source" is added:
the developer must remember to copy steps 3, 5, and 6
exactly from an existing implementation.

**THE INVENTION MOMENT:**
Template Method: base class `DataExtractor` defines the
algorithm skeleton as a `final` method calling all 6 steps
in order. Steps 1, 2, 4 are `abstract` - subclasses
implement them. Steps 3, 5, 6 are concrete in the base
class. `CsvExtractor`, `JsonApiExtractor`, `DbExtractor`
extend `DataExtractor` and implement only the varying steps.
The invariant algorithm structure is preserved.

**EVOLUTION:**
Spring's `JdbcTemplate`, `RestTemplate`, and
`AbstractApplicationContext.refresh()` all use Template
Method. Spring's lifecycle methods (`postProcessBeforeInitialization`,
`init-method`) are template method hooks. JUnit's test
framework provides `@Before/@After` (now `@BeforeEach/@AfterEach`)
as template hooks around test methods.

---

### 📘 Textbook Definition

The **Template Method** pattern is a Behavioral design
pattern that defines the skeleton of an algorithm in
a base class, deferring some steps to subclasses.
Template Method lets subclasses redefine specific steps
of an algorithm without changing the algorithm's structure.
The base class calls abstract methods (primitive operations)
in a defined sequence; subclasses override these methods
to provide concrete behavior. The template method itself
is typically `final` to prevent subclasses from changing
the algorithm structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Template Method says "the WHAT and WHEN is fixed in the
parent; the HOW is decided by each child class."

**One analogy:**
> A recipe card (Template Method). The card says: (1)
> preheat oven, (2) prepare filling, (3) fill pastry,
> (4) bake 30 minutes, (5) let cool. Step 2 is customizable
> (apple filling vs cherry). Steps 1, 3, 4, 5 are the same.
> You provide only the filling; the recipe structure
> handles everything else.

**One insight:**
Template Method uses INHERITANCE for variation. This
creates a compile-time binding - a subclass can only
be one "variation." Strategy uses COMPOSITION for the
same purpose and is more flexible at runtime. Prefer
Strategy when runtime selection is needed; use Template
Method when the algorithm skeleton must be protected
from subclass modification.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The template method is `final` - subclasses CANNOT
   override the algorithm sequence.
2. Primitive operations are `abstract` - subclasses MUST
   provide them.
3. Hook operations have default implementations - subclasses
   MAY override them.

**DERIVED DESIGN:**
Three types of methods in the base class:
- **Template method** (`final`): the algorithm skeleton;
  calls primitive + hook operations in defined order.
- **Primitive operations** (`abstract`): MUST be overridden;
  define what varies between subclasses.
- **Hook operations** (`protected`, with default): MAY
  be overridden; optional customization points.

**INHERITANCE RULE:**
The GoF principle: "The Hollywood Principle - Don't call
us, we'll call you." Subclasses don't call base class
methods; the base class calls subclass-overridden methods.

**TRADE-OFFS:**

**Gain:** Algorithm structure is guaranteed and invariant.
Code reuse for common steps. Subclasses add customization
without understanding the full algorithm. Framework
extension pattern (users extend by subclassing).

**Cost:** Inheritance coupling - subclasses are tightly
bound to the base class. Adding a step to the algorithm
affects ALL subclasses. Cannot swap algorithms at runtime
(compile-time binding). Deep inheritance hierarchies
become unmaintainable.

---

### 🧪 Thought Experiment

**SETUP:**
A report generator for Sales, HR, and Finance departments.
All share: fetch data, format header, generate rows,
format footer, export to PDF. "Generate rows" varies
by department.

**WITHOUT TEMPLATE METHOD:**
Duplication: three report classes, each copying
`formatHeader`, `formatFooter`, `exportToPDF`.
Footer format changes: update all three classes.

**WITH TEMPLATE METHOD:**
`AbstractReport.generate()` (final): calls `fetchData()`,
`formatHeader()`, `generateRows()` (abstract), `formatFooter()`,
`exportToPDF()`. `SalesReport`, `HRReport`, `FinanceReport`
override only `generateRows()`. Footer changes: one place.

---

### 🧠 Mental Model / Analogy

> Template Method is a FRANCHISE SYSTEM. McDonald's (base
> class) defines the franchise template: location setup,
> equipment standards, ordering system, cleaning protocol.
> Each franchisee (subclass) runs their location but
> CANNOT change the core operations. They customize the
> regional menu (hook methods) but follow all other
> McDonald's templates exactly. The parent defines the
> structure; the children fill in the gaps.

- "McDonald's HQ template" = abstract base class
- "Core operations (invariant)" = concrete template method steps
- "Regional menu options" = hook/abstract methods
- "Franchisee implements regional menu" = subclass overrides

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Template Method is a recipe with "fill in the blanks."
The parent class provides the steps in order; child classes
fill in the blank steps. The parent guarantees the
sequence never changes.

**Level 2 - How to use it (junior developer):**
Create an abstract base class with a `final` method
calling the algorithm steps. Mark steps that vary as
`abstract`. Mark optional customization steps as `protected`
with a default implementation. Subclasses extend the
base and override the abstract (and optionally, hook)
methods.

**Level 3 - How it works (mid-level engineer):**
Spring's `AbstractApplicationContext.refresh()` is the
most famous Template Method in Java enterprise: it calls
`prepareRefresh()`, `obtainFreshBeanFactory()`,
`prepareBeanFactory()`, `postProcessBeanFactory()`,
`invokeBeanFactoryPostProcessors()`, `registerBeanPostProcessors()`,
`initMessageSource()`, `initApplicationEventMulticaster()`,
`onRefresh()`, `registerListeners()`, `finishBeanFactoryInitialization()`,
`finishRefresh()`. `onRefresh()` is a hook method -
subclasses (like `AnnotationConfigServletWebServerApplicationContext`)
override it to start the embedded web server. The base
class controls the startup sequence; subclasses add
their specific startup step.

**Level 4 - Why it was designed this way (senior/staff):**
Template Method is the primary pattern for framework
extension points. When a framework wants to allow users
to customize a specific step of a process without allowing
them to change the overall process:
- Mark the overall process as `final`
- Mark the customizable step as `abstract` or a hook
- Users extend the framework class and override the step
This is how JUnit 4's `TestCase` worked: `runBare()` was
the template method (setUp → test → tearDown sequence);
users overrode `setUp()`, `tearDown()`, and the test method.
This design guarantees teardown always runs even if the
test fails - the template method controls the invariant.

**Level 5 - Mastery (distinguished engineer):**
Template Method's "Hollywood Principle" is the Inversion
of Control (IoC) at the method level. In non-IoC code:
the user's code calls library code. In Template Method:
the library (base class) CALLS the user's code (overridden
methods). This IoC is what makes frameworks possible: Spring
calls YOUR `@Bean` configuration methods; JUnit calls YOUR
`@Test` methods; Spring Boot calls YOUR `CommandLineRunner.run()`.
The framework (base class / template) defines WHEN; the user
defines WHAT. Template Method IS the pattern that describes
how "framework hooks" work.

---

### ⚙️ How It Works (Mechanism)

```
Template Method Structure
┌─────────────────────────────────────────────────────────┐
│ AbstractDataExtractor                                   │
│                                                         │
│ final void extract() {       ← TEMPLATE METHOD          │
│     connect();               ← abstract: varies         │
│     List data = fetchData(); ← abstract: varies         │
│     validate(data);          ← concrete: invariant      │
│     List result = transform(data); ← abstract: varies   │
│     load(result);            ← concrete: invariant      │
│     disconnect();            ← hook: may override       │
│ }                                                       │
│                                                         │
│ abstract void connect();                                │
│ abstract List fetchData();                              │
│ abstract List transform(List data);                     │
│ void validate(List data) { /* common validation */ }    │
│ void load(List data) { /* common load to DW */ }        │
│ void disconnect() { /* default no-op or cleanup */ }    │
│                                                         │
│ CsvExtractor extends AbstractDataExtractor              │
│   void connect() { csvFile = new FileReader(...); }     │
│   List fetchData() { return csvParser.parseAll(); }     │
│   List transform(List d) { return mapCsvToSchema(d); }  │
│   // disconnect(): inherits or overrides if needed      │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CsvExtractor extractor = new CsvExtractor("data.csv");
extractor.extract():

1. connect():    CsvExtractor.connect() - opens CSV file
2. fetchData():  CsvExtractor.fetchData() - reads rows
3. validate():   AbstractDataExtractor.validate() - common
4. transform():  CsvExtractor.transform() - CSV-specific
5. load():       AbstractDataExtractor.load() - common
6. disconnect(): CsvExtractor.disconnect() - closes file
               (or AbstractDataExtractor.disconnect() if
                 not overridden)

Same call on DbExtractor:
1. connect():    DbExtractor.connect() - opens DB
  connection
2. fetchData():  DbExtractor.fetchData() - runs SQL query
3. validate():   AbstractDataExtractor.validate() - SAME
  code
4. transform():  DbExtractor.transform() - DB-specific
  mapping
5. load():       AbstractDataExtractor.load() - SAME code
6. disconnect(): DbExtractor.disconnect() - closes
  connection
```

---

### 💻 Code Example

**Example 1 - Without Template Method (code duplication):**

```java
// BAD: all three classes duplicate validate() and load()
class CsvExtractor {
    void extract() {
        FileReader csv = new FileReader("data.csv");
        List data = csv.readAll();
        validate(data);         // DUPLICATE
        List result = mapCsvFields(data);
        loadToWarehouse(result); // DUPLICATE
        csv.close();
    }
    private void validate(List d) { /* 20 lines */ }
    private void loadToWarehouse(List d) { /* 30 lines */ }
}

class JsonApiExtractor {
    void extract() {
        HttpClient http = HttpClient.create();
        List data = http.getJson(apiUrl);
        validate(data);         // SAME 20 LINES DUPLICATED
        List result = mapJsonFields(data);
        loadToWarehouse(result); // SAME 30 LINES DUPLICATED
        http.close();
    }
    // Same validate() and loadToWarehouse() copy-pasted
}
```

**Example 2 - Template Method solution:**

```java
// GOOD: algorithm skeleton in base class

abstract class DataExtractor {
    // TEMPLATE METHOD - final: sequence cannot be changed
    final void extract() {
        connect();
        List<Record> raw = fetchData();
        validate(raw);            // invariant step
        List<Record> transformed = transform(raw);
        load(transformed);        // invariant step
        disconnect();             // hook
    }

    // ABSTRACT: subclasses must implement these
    protected abstract void connect();
    protected abstract List<Record> fetchData();
    protected abstract List<Record> transform(List<Record> raw);

    // CONCRETE: invariant steps - subclasses inherit these
    private void validate(List<Record> data) {
        // schema validation, required fields, type checks
        if (data == null || data.isEmpty())
            throw new ExtractException("No data extracted");
        data.forEach(r -> schemaValidator.validate(r));
    }

    private void load(List<Record> data) {
        warehouse.bulkInsert(data);
        auditLogger.logLoad(data.size());
    }

    // HOOK: optional customization - default is no-op
    protected void disconnect() {
        // default: nothing (subclasses may override)
    }
}

// Subclass: implements ONLY what varies
class CsvDataExtractor extends DataExtractor {
    private final String filePath;
    private FileReader reader;

    CsvDataExtractor(String filePath) {
        this.filePath = filePath;
    }

    @Override
    protected void connect() {
        reader = new FileReader(filePath);
    }

    @Override
    protected List<Record> fetchData() {
        return csvParser.parse(reader);
    }

    @Override
    protected List<Record> transform(List<Record> raw) {
        return raw.stream()
            .map(this::mapCsvFieldsToSchema)
            .collect(toList());
    }

    @Override
    protected void disconnect() {
        reader.close(); // overrides hook
    }
}

// Adding a new source: ONE class, zero changes to base class
class JsonApiDataExtractor extends DataExtractor {
    private final String apiUrl;

    JsonApiDataExtractor(String apiUrl) {
        this.apiUrl = apiUrl;
    }

    @Override
    protected void connect() { /* http setup */ }

    @Override
    protected List<Record> fetchData() {
        return httpClient.getJson(apiUrl);
    }

    @Override
    protected List<Record> transform(List<Record> raw) {
        return raw.stream()
            .map(this::mapJsonToSchema)
            .collect(toList());
    }
    // disconnect(): not overridden - uses base no-op hook
}
```

**Example 3 - JUnit lifecycle as Template Method:**

```java
// RECOGNITION: JUnit @BeforeEach/@Test/@AfterEach IS Template Method

// JUnit framework (base class - conceptually):
// final void runTest() {
//   @BeforeEach methods
//   @Test method
//   @AfterEach methods  ← always run (like finally)
// }

class OrderServiceTest {
    private OrderService service;

    @BeforeEach  // hook - optional override
    void setUp() {
        service = new OrderService(mockRepo);
    }

    @Test  // primitive operation - you implement
    void placeOrder_validOrder_succeeds() {
        // ... test logic
    }

    @AfterEach  // hook - optional override
    void tearDown() {
        // cleanup if needed
    }
}
// JUnit's runner IS the template method:
// it calls setUp, then your test, then tearDown
// in a guaranteed sequence regardless of test outcome
```

**How to test/verify correctness:**
Test the template method on a concrete subclass: verify
the full sequence of steps is called in the correct order.
Test that the invariant steps are not skippable. Test
hook methods: verify the base class default behavior when
not overridden, and the subclass behavior when overridden.

---

### ⚖️ Comparison Table

| Feature | Template Method | Strategy |
|---|---|---|
| Variation mechanism | Inheritance (override) | Composition (inject) |
| Algorithm structure | Fixed (base class, final) | Each strategy is independent |
| Runtime swap | No (compile-time class) | Yes (inject different strategy) |
| Multiple behaviors per class | No | Yes (combine strategies) |
| Framework extension | Natural (extend base class) | Requires factory |
| Code reuse | High (base class methods) | Must duplicate in each strategy |

**When to prefer Template Method over Strategy:**
- Framework design where subclassers extend your base class
- Algorithm structure must be guaranteed invariant
- Many shared steps, few varying steps

**When to prefer Strategy:**
- Runtime algorithm selection needed
- Same context needs multiple algorithms simultaneously
- Avoid deep inheritance hierarchies

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Template Method is outdated (Strategy with lambdas is better) | Template Method is still the correct choice when the algorithm structure must be ENFORCED (final template method prevents any subclass from reordering steps). Strategy with lambdas cannot prevent lambda composition that breaks the required sequence |
| Hook methods are optional features | Hook methods are INTENTIONAL extension points. The base class provides a no-op default precisely because overriding is OPTIONAL. Hooks without defaults (abstract) are not hooks - they are primitive operations |
| Template Method and Factory Method are similar | Template Method is a behavioral pattern (algorithm skeleton). Factory Method is a creational pattern that creates objects. They use the same inheritance mechanism but for different purposes. They can be combined: a Template Method's step may be a Factory Method |
| Making the template method non-final is fine | A non-final template method allows subclasses to override the algorithm structure - breaking the invariant guarantee. The template method MUST be final. If a subclass needs a different structure, it should be a separate template method hierarchy |

---

### 🚨 Failure Modes & Diagnosis

**Subclass Overrides Template Method (Breaking the Invariant)**

**Symptom:**
A subclass overrides the template method itself (not a
primitive operation). The step sequence is broken: load
happens before validation, or disconnect is skipped.

**Root Cause:**
Template method not declared `final`. Subclass developer
did not realize it was a template method.

**Fix:**
Declare all template methods `final`:
```java
// BAD: template method can be overridden
abstract class DataExtractor {
    void extract() { ... } // not final!
}

// GOOD: template method is final
abstract class DataExtractor {
    final void extract() { ... } // cannot be overridden
}
```

---

**Abstract Class Grows Without Bound (Base Class Pollution)**

**Symptom:**
The base class `AbstractDataExtractor` has grown to
500 lines. It handles 12 different extraction variants.
Every new extraction type adds a new hook method to the
base class, which then needs a default implementation.
The base class is not really "abstract" anymore.

**Root Cause:**
Template Method was used where Strategy would be better.
The algorithm structure is not truly invariant - different
subclasses need different sequences.

**Fix:**
Identify the common algorithm core. Split the hierarchy
into separate Template Method families if sequences differ
significantly. Or: switch to Strategy for the varying
parts and use Template Method only for the truly invariant
skeleton.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Strategy` - DPT-027; Strategy is the composition-based
  alternative to Template Method; understanding both
  makes the inheritance vs composition trade-off clear

**Builds On This (learn these next):**
- `Factory Method` - uses the same inheritance mechanism
  as Template Method but for object creation; often
  combined with Template Method

**Alternatives / Comparisons:**
- `Strategy` - composition vs Template Method's inheritance;
  prefer Strategy for runtime flexibility

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Algorithm skeleton in base class (final);│
│              │ abstract steps filled in by subclasses   │
├──────────────┼──────────────────────────────────────────┤
│ 3 STEP TYPES │ Final template: invariant sequence       │
│              │ Abstract primitive: MUST override        │
│              │ Hook (protected): MAY override           │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ Spring AbstractApplicationContext.refresh│
│              │ JUnit @BeforeEach/@Test/@AfterEach       │
├──────────────┼──────────────────────────────────────────┤
│ MUST BE FINAL│ Template method must be final -          │
│              │ prevents subclass from breaking sequence │
├──────────────┼──────────────────────────────────────────┤
│ VS STRATEGY  │ Template Method: inheritance, compile-   │
│              │ time. Strategy: composition, runtime.    │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Visitor → Null Object → Concurrency Pats │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three types of methods: template (final - invariant),
   primitive (abstract - must override), hook (has default
   - may override). The template method MUST be final
2. Spring's `AbstractApplicationContext.refresh()` IS
   Template Method: the startup sequence is final; `onRefresh()`
   is the hook that subclasses (web application contexts)
   use to start the embedded server
3. Template Method = inheritance; Strategy = composition.
   Prefer Strategy for runtime flexibility; use Template
   Method when the sequence must be guaranteed invariant

**Interview one-liner:**
"Template Method defines an algorithm skeleton in a base
class and defers varying steps to subclasses via abstract
and hook methods. The template method must be final to
prevent subclasses from reordering steps. Spring's ApplicationContext
refresh sequence and JUnit's @BeforeEach/@Test/@AfterEach
lifecycle are canonical examples. Strategy (composition)
is preferred over Template Method (inheritance) when runtime
flexibility is needed."

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [CLASSIFY] Given an abstract base class with methods,
   correctly classify each method as: template (final),
   primitive (abstract), or hook (protected with default)
2. [EXPLAIN] Why the template method must be declared
   `final` - describe what breaks if it is not
3. [COMPARE] When given a scenario (ETL pipeline with
   shared/varying steps), decide whether Template Method
   or Strategy is the better design and justify with
   the compile-time vs runtime tradeoff
4. [IDENTIFY] Recognize Spring's `AbstractApplicationContext
   .refresh()` as Template Method - name which step
   is the hook used to start the embedded server

