---
layout: default
title: "Template Method Pattern"
parent: "Design Patterns"
nav_order: 786
permalink: /design-patterns/template-method-pattern/
number: "786"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Inheritance, Strategy Pattern"
used_by: "Frameworks, data parsers, report generators, test base classes"
tags: #intermediate, #design-patterns, #behavioral, #oop, #inheritance, #hooks
---

# 786 — Template Method Pattern

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#inheritance` `#hooks`

⚡ TL;DR — **Template Method** defines the skeleton of an algorithm in a base class, deferring specific steps to subclasses — so the algorithm's structure is fixed but individual steps can be customized without changing the overall flow.

| #786            | Category: Design Patterns                                      | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Inheritance, Strategy Pattern     |                 |
| **Used by:**    | Frameworks, data parsers, report generators, test base classes |                 |

---

### 📘 Textbook Definition

**Template Method** (GoF, 1994): a behavioral design pattern that defines the skeleton of an algorithm in a base class, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure. Components: **Abstract class** — implements the template method (the fixed algorithm skeleton) and declares abstract (or overridable) primitive operations. **Concrete subclasses** — implement the primitive operations (the variable steps). GoF intent: "Define the skeleton of an algorithm in an operation, deferring some steps to subclasses." Java: `java.io.InputStream.read(byte[], int, int)` calls abstract `read()`. `HttpServlet.service()` calls `doGet()`, `doPost()`. JUnit's `setUp()`, `tearDown()`, `test*()`. Spring's `JdbcTemplate`, `RestTemplate`, `JpaRepository` base classes.

---

### 🟢 Simple Definition (Easy)

A job application process at any company: (1) receive application, (2) screen resume, (3) conduct interview, (4) make offer. The overall flow is fixed. But each company customizes the steps: Google's interview is different from a startup's. Template Method: abstract `HiringProcess` with the fixed steps in `hire()`. Each company subclasses `HiringProcess` and overrides `conductInterview()`. The hiring flow runs the same; the interview step varies.

---

### 🔵 Simple Definition (Elaborated)

`HttpServlet.service(request, response)` is a template method. It reads the HTTP method, then calls the appropriate hook: `doGet()`, `doPost()`, `doPut()`, `doDelete()`. Your servlet subclass overrides only the methods it needs. `service()` skeleton is fixed — request handling, error wiring, thread safety concerns already done. You just fill in the specific logic for each HTTP verb. This is Template Method: base class owns the algorithm; subclasses own specific steps.

---

### 🔩 First Principles Explanation

**Fixed skeleton + variable steps + hooks:**

```
TEMPLATE METHOD STRUCTURE:

  abstract class DataProcessor {

      // TEMPLATE METHOD: the fixed algorithm — declared final to prevent override
      final void processData(String source) {
          String rawData   = readData(source);     // step 1: abstract (must override)
          String cleaned   = validateData(rawData); // step 2: abstract
          String result    = processCore(cleaned);  // step 3: abstract
          writeOutput(result);                      // step 4: concrete (default impl)
          onComplete();                             // step 5: HOOK (optional override)
      }

      // PRIMITIVE OPERATIONS (abstract — subclasses MUST implement):
      protected abstract String readData(String source);
      protected abstract String validateData(String data);
      protected abstract String processCore(String data);

      // CONCRETE OPERATION (default implementation — subclasses MAY override):
      protected void writeOutput(String result) {
          System.out.println("Result: " + result);   // default: print to stdout
      }

      // HOOK: empty default — subclasses override if they want notification
      protected void onComplete() { }
  }

  // Subclass 1: CSV processing
  class CsvProcessor extends DataProcessor {
      @Override
      protected String readData(String filePath) {
          return Files.readString(Path.of(filePath));  // reads from file
      }

      @Override
      protected String validateData(String data) {
          if (!data.contains(",")) throw new IllegalArgumentException("Not valid CSV");
          return data.trim();
      }

      @Override
      protected String processCore(String data) {
          return Arrays.stream(data.split(","))
                       .map(String::trim)
                       .collect(Collectors.joining(" | "));
      }

      @Override
      protected void onComplete() {
          log.info("CSV processing complete");   // overrides hook
      }
  }

  // Subclass 2: JSON processing — different implementations of same steps
  class JsonProcessor extends DataProcessor {
      @Override
      protected String readData(String url) {
          return httpClient.get(url).getBody();  // reads from HTTP URL
      }

      @Override
      protected String validateData(String data) {
          objectMapper.readTree(data);  // validates JSON structure; throws on invalid
          return data;
      }

      @Override
      protected String processCore(String data) {
          JsonNode root = objectMapper.readTree(data);
          return root.get("result").asText();
      }
      // writeOutput: not overridden — uses default (print to stdout)
      // onComplete: not overridden — empty hook, no notification needed
  }

  // Client — works with the template method, not implementation details:
  DataProcessor csvProc = new CsvProcessor();
  csvProc.processData("data.csv");       // runs full algorithm; CsvProcessor fills steps

  DataProcessor jsonProc = new JsonProcessor();
  jsonProc.processData("http://api.example.com/data"); // same algorithm, different steps

HOOKS vs ABSTRACT METHODS:

  ABSTRACT METHODS:
  - Must be overridden by subclasses.
  - Steps that are logically required.
  - Compiler enforces implementation.

  HOOKS:
  - Empty or default implementation in base class.
  - Subclasses override if they need to.
  - "Opt-in" customization points.

  Example from Spring:
  class AbstractSecurityWebApplicationInitializer {
      // Hook — default implementation exists:
      protected String getContextAttribute() { return null; }
      protected void beforeSpringSecurityFilterChain(ServletContext servletContext) { }
      protected void afterSpringSecurityFilterChain(ServletContext servletContext) { }
  }

TEMPLATE METHOD vs STRATEGY:

  TEMPLATE METHOD:
  - Variation via inheritance (subclasses).
  - Algorithm skeleton in base class.
  - Varies at compile time (depends on which subclass you instantiate).
  - Harder to change at runtime (would need different instance).
  - "Don't call us, we'll call you" (Hollywood Principle).

  STRATEGY:
  - Variation via composition (delegate to strategy object).
  - Context class holds a strategy reference.
  - Can vary at runtime (swap strategy object).
  - Easier to test (inject mock strategy).
  - More flexible; preferred for modern code.

  When to use Template Method:
  ✓ Framework base classes (users extend your base class).
  ✓ Fixed algorithm with many small steps, only a few variable.
  ✓ Compile-time variation is acceptable.

  When to prefer Strategy:
  ✓ Need runtime variability.
  ✓ Need to mock/test the algorithm.
  ✓ Multiple independent dimensions of variation.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Template Method:

- Code duplication: every data processor reimplements the full pipeline (read → validate → process → write)
- Change the output step: modify every processor class

WITH Template Method:
→ Algorithm skeleton in one place. Change the output step: modify base class once. Subclasses focus only on their specific steps.

---

### 🧠 Mental Model / Analogy

> A cooking recipe format. Every recipe has the same structure: (1) gather ingredients, (2) prepare/chop, (3) cook, (4) plate and serve. The recipe BOOK defines this fixed structure. Each individual recipe (pasta, stir-fry, soup) fills in step 3 "cook" differently — boil vs wok-fry vs simmer. The recipe format is the template method; each dish is a subclass overriding the cooking step.

"Recipe format/structure" = template method (fixed skeleton in abstract class)
"Each individual recipe" = concrete subclass
"The 'cook' step" = abstract/overridable primitive operation
"Step 4 'plate'" = hook — default implementation (default plating), can be overridden
"Following the recipe format gives consistent results" = template method ensures algorithm structure is preserved

---

### ⚙️ How It Works (Mechanism)

```
TEMPLATE METHOD FLOW:

  1. Client calls templateMethod() on abstract base class
  2. Base class runs fixed steps: step1() → step2() → step3() → hook()
  3. Concrete subclass provides step1(), step2(), step3() implementations
  4. Hook: empty default in base; subclass overrides if needed
  5. Result: same algorithm flow, different step implementations
```

---

### 🔄 How It Connects (Mini-Map)

```
Fixed algorithm skeleton; variable steps via inheritance; Hollywood Principle
        │
        ▼
Template Method Pattern ◄──── (you are here)
(abstract class owns flow; subclasses override steps)
        │
        ├── Strategy: same goal (variable behavior) via composition, not inheritance
        ├── Factory Method: often uses Template Method — base factory calls abstract create()
        ├── Hook method: specialization of Template Method for optional overrides
        └── HttpServlet: classic Java Template Method in the JEE spec
```

---

### 💻 Code Example

```java
// Report generator with template method:
abstract class ReportGenerator {

    // Template method — final: algorithm structure must not change
    public final Report generateReport(ReportRequest request) {
        ReportData data     = fetchData(request);           // abstract: varies per report type
        ReportData filtered = applyFilters(data, request);  // concrete: default filter logic
        List<Section> body  = buildSections(filtered);      // abstract: layout varies
        addHeader(body, request);                           // hook: optional header
        return new Report(body, getFormat());               // abstract: format varies
    }

    protected abstract ReportData fetchData(ReportRequest request);
    protected abstract List<Section> buildSections(ReportData data);
    protected abstract ReportFormat getFormat();

    // Concrete default — subclasses override if needed:
    protected ReportData applyFilters(ReportData data, ReportRequest req) {
        return req.hasDateRange() ? data.filterByDateRange(req.getFrom(), req.getTo()) : data;
    }

    // Hook — empty default:
    protected void addHeader(List<Section> sections, ReportRequest req) { }
}

// Concrete: PDF sales report
class SalesReportPdf extends ReportGenerator {
    @Override
    protected ReportData fetchData(ReportRequest r) {
        return salesRepo.findByPeriod(r.getFrom(), r.getTo());
    }
    @Override
    protected List<Section> buildSections(ReportData data) {
        return List.of(new SummarySection(data), new ChartSection(data), new DetailTable(data));
    }
    @Override
    protected ReportFormat getFormat() { return ReportFormat.PDF; }
    @Override
    protected void addHeader(List<Section> sections, ReportRequest req) {
        sections.add(0, new LogoHeader(req.getCompany())); // override hook
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Template Method is obsolete with lambdas | Template Method with complex multi-step skeletons is still valid. However, for single-method variation, lambdas and Strategy are cleaner. Java frameworks (Spring, JUnit, Servlet API) still use Template Method extensively for framework extension points. The pattern is alive in framework design; it's most useful when you own the framework and users extend it. |
| The template method must be final        | Declaring the template method `final` is best practice (prevents subclasses from breaking the algorithm). However, Java doesn't require it. Some frameworks don't declare it `final` to allow overriding the whole flow. The `final` modifier is a design safeguard, not a pattern requirement.                                                                         |
| All steps must be abstract               | Template Method allows concrete steps (with default implementations) and hooks (empty defaults). Only the steps that MUST vary between subclasses need to be abstract. A template method might have 6 steps where 2 are abstract, 3 have defaults, and 1 is a hook. Over-abstracting forces subclasses to implement trivial steps.                                      |

---

### 🔥 Pitfalls in Production

**Subclass overriding steps in a way that breaks the parent's invariants:**

```java
// ANTI-PATTERN: subclass breaks expected algorithm behavior:
abstract class OrderProcessor {
    final void processOrder(Order order) {
        validateOrder(order);         // step 1: validate
        reserveInventory(order);      // step 2: reserve
        chargePayment(order);         // step 3: charge
        shipOrder(order);             // step 4: ship
    }
    protected abstract void validateOrder(Order order);
    protected abstract void chargePayment(Order order);
    // reserveInventory, shipOrder: concrete defaults
}

class FreeOrderProcessor extends OrderProcessor {
    @Override
    void validateOrder(Order order) {
        // ... validates
        chargePayment(order);    // ← calls chargePayment inside validateOrder!
        // Breaks algorithm: chargePayment() now runs TWICE (validate + step 3)
    }
    @Override
    void chargePayment(Order order) { /* free — no charge */ }
}

// RULE: Never call other template method steps from inside a step.
// Each primitive operation should do ONLY its own step.
// If steps need to share data, pass it via method parameters or the context object.

// FIX: use a shared context object if steps need to communicate:
abstract class OrderProcessor {
    final void processOrder(Order order) {
        OrderContext ctx = new OrderContext(order);
        validateOrder(ctx);
        reserveInventory(ctx);
        chargePayment(ctx);
        shipOrder(ctx);
    }
    protected abstract void validateOrder(OrderContext ctx);
    protected abstract void chargePayment(OrderContext ctx);
}
```

---

### 🔗 Related Keywords

- `Strategy Pattern` — same variation goal via composition (preferred for runtime flexibility)
- `Factory Method Pattern` — often implemented using Template Method: base calls abstract `create()`
- `Hook Method` — specialization: optional extension point with empty default in Template Method
- `HttpServlet` — canonical Java Template Method: `service()` calls `doGet()`, `doPost()`, etc.
- `JdbcTemplate` — Spring's Template Method for database operations (connection/cleanup fixed; SQL varies)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Base class owns the algorithm skeleton.   │
│              │ Subclasses override individual steps.     │
│              │ "Don't call us — we'll call you."         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fixed algorithm flow; multiple variants   │
│              │ differ only in specific steps; framework  │
│              │ extension via inheritance needed          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need runtime algorithm swap; deep         │
│              │ inheritance hierarchies; steps are highly │
│              │ interdependent (hard to isolate)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Recipe format: every dish follows the   │
│              │  same steps — only the 'cook' step       │
│              │  differs per dish."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → Factory Method →       │
│              │ Hook Method → HttpServlet → JdbcTemplate  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `JdbcTemplate.query(sql, rowMapper)` is a classic Template Method implementation. The fixed skeleton: get connection → prepare statement → execute → iterate ResultSet → close connection/statement. Your `RowMapper` fills in the variable step: mapping each row to a domain object. The template method handles all the connection management and resource cleanup — concerns you'd otherwise duplicate in every DAO. How does `JdbcTemplate` relate to Template Method vs. Strategy? Is the `RowMapper` a Template Method primitive operation or a Strategy?

**Q2.** GoF explicitly warns about the "Hollywood Principle" (don't call us, we'll call you) that Template Method enforces — base class calls subclass methods, not the other way around. This creates an inversion of control. However, deep Template Method hierarchies (base → abstract base → concrete) can become difficult to understand: to know what `processOrder()` does, you must trace through multiple class levels. At what depth does Template Method become an anti-pattern? What is the modern Java alternative (composition over inheritance) for the same reuse goal?
