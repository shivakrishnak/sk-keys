---
version: 2
layout: default
title: "Cucumber (BDD Testing)"
parent: "Testing"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/testing/cucumber-bdd/
id: TST-059
category: Testing
difficulty: ★★★
depends_on: BDD, Testing, Java Language
used_by: CI-CD, Testing
related: Gherkin, SpecFlow, JBehave
tags:
  - testing
  - java
  - advanced
  - pattern
---

⚡ **TL;DR -** A BDD framework that binds plain-language Gherkin scenarios to executable Java step definitions, making requirements and tests the same artefact.

| Field      | Value                              |
|------------|------------------------------------|
| Depends on | BDD, Testing, Java Language        |
| Used by    | CI-CD, Testing                     |
| Related    | Gherkin, SpecFlow, JBehave         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Requirements live in Confluence; tests live in Java. The two drift apart. Engineers test what they built, not necessarily what the business specified. QA re-discovers integration gaps during UAT, weeks after implementation.

**THE BREAKING POINT:** A payment feature ships. The acceptance criteria say "a declined card shows an error message". The unit tests verify the exception is thrown. Nobody tested the UI message - because the acceptance criteria and the test suite were never linked. The bug reaches production.

**THE INVENTION MOMENT:** BDD (Behaviour-Driven Development, Dan North, 2006) proposed that requirements *be* tests. Cucumber (Aslak Hellesøy, 2008) implemented this: business-readable Gherkin sentences become executable test scenarios via annotated Java step definitions. A failing scenario is a failing requirement - there is no gap.

---

### 📘 Textbook Definition

**Cucumber** is a BDD testing framework that executes plain-text feature files written in **Gherkin** syntax. Each Gherkin step (`Given`, `When`, `Then`, `And`, `But`) is matched at runtime by a regular-expression or Cucumber Expression-annotated Java method called a **step definition**. The framework parses feature files, resolves step text to definitions, and invokes them in order. **Hooks** (`@Before`, `@After`, `@BeforeStep`) provide lifecycle callbacks. **Data Tables** and **Scenario Outlines** (`Examples:`) parameterise scenarios. The JUnit 5 or TestNG runner integrates Cucumber into standard build pipelines.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Write requirements in plain English; Cucumber runs them as tests automatically.

> Cucumber is a legal interpreter: the business writes the contract in plain language, and the interpreter translates each clause into enforceable code - if any clause fails, the contract is broken.

**One insight:** The Gherkin feature file is the single source of truth for both what the system should do and whether it currently does it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Specifications must be unambiguous enough to be mechanically verified.
2. The person who writes the requirement and the person who verifies it should read the same document.
3. Shared vocabulary (ubiquitous language) eliminates the translation gap between business and engineering.

**DERIVED DESIGN:** Define a grammar (Gherkin) that is human-readable but also machine-parseable. Map grammar sentences to code via a registry (step definitions). Run the grammar-as-tests in a standard test harness (JUnit/TestNG).

**THE TRADE-OFFS:**
- **Gain:** Living documentation that is always in sync with the test suite; non-technical stakeholders can read, write, and verify test scenarios.
- **Cost:** High upfront investment in step definition infrastructure; the "fat step definitions" anti-pattern emerges when teams push logic into glue code, defeating the collaboration intent.

---

### 🧪 Thought Experiment

**SETUP:** A product manager writes: "Given a logged-in user with insufficient balance, when they attempt a transfer, then they see 'Insufficient funds' and the balance is unchanged."

**WHAT HAPPENS WITHOUT Cucumber:** An engineer reads the spec and writes a Java test that checks an exception is thrown. The UI message and balance-unchanged assertion are omitted because they seem "obvious". Two bugs exist - silently.

**WHAT HAPPENS WITH Cucumber:** The PM's sentence *becomes* the Gherkin scenario. A step definition for `then they see 'Insufficient funds'` forces an engineer to wire up the UI assertion. `and the balance is unchanged` forces a balance re-check. The spec cannot be silently incomplete - every step without a definition causes a compilation-time `UndefinedStepException`.

**THE INSIGHT:** Cucumber enforces completeness. A step with no matching definition is a build failure, not a documentation gap.

---

### 🧠 Mental Model / Analogy

> Cucumber is a screenplay adaptation system. The Gherkin feature file is the screenplay - written by the playwright (product team) in natural language. Step definitions are the director's shot list - mapping each script line to specific camera instructions (code). The running tests are the final film.

- **Screenplay lines** → Gherkin steps (`Given`, `When`, `Then`)
- **Director's shot list** → step definition methods
- **Actors / set** → application under test
- **Screening** → Cucumber test run
- **Box office results** → pass/fail report

Where this analogy breaks down: a bad screenplay can still produce a good film through directorial creativity; in Cucumber, a poorly written feature file directly produces a poorly structured test - bad input propagates without a creative buffer.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
You write "Given I have £100, When I transfer £200, Then I see an error" in a text file. Cucumber reads it and runs real code that checks whether your app actually does that. If the app fails, Cucumber tells you which sentence failed.

**Level 2 - How to use it (junior developer):**
Create a `.feature` file in `src/test/resources`. Write `Scenario:` blocks using `Given/When/Then` steps. Create a Java `@CucumberOptions` runner class and a step definition class with `@Given("I have £{int}")` annotated methods. Run with `mvn test`. Undefined steps auto-generate stub snippets in the console.

**Level 3 - How it works (mid-level engineer):**
Cucumber's runtime parses feature files into an AST (`FeatureNode` → `ScenarioNode` → `StepNode`). Each step text is matched against registered `StepDefinition` registry entries using Cucumber Expressions or regex. Parameters are extracted and type-converted via the `TypeRegistry`. Hooks are sorted by order and executed around the scenario lifecycle. `DataTable` objects are injected into step definition parameters when a step body contains a table. PicoContainer (or Spring/Guice via plugins) manages step definition class instantiation and state sharing between steps in one scenario.

**Level 4 - Why it was designed this way (senior/staff):**
The step definition registry decouples the test language from implementation, enabling step reuse across feature files and cross-language implementations (Ruby, JavaScript, Java all run the same `.feature` files). The dependency injection plugin model was added because step definitions naturally need shared state (the `World` concept from early Cucumber-Ruby): rather than static fields, DI containers give each scenario a fresh object graph, preventing state leakage. The `@Before`/`@After` hook tag-filtering system (`@Before(value = "@payment")`) allows environment setup to be scoped precisely to feature subsets, avoiding expensive setup for irrelevant scenarios.

---

### ⚙️ How It Works (Mechanism)

```
src/test/resources/features/payment.feature
  │  Gherkin AST parsed
  ▼
CucumberRunner (JUnit5 / TestNG)
  │
  ▼
StepDefinitionRegistry
  ├── matches "Given a user with £{int} balance"
  │     → PaymentSteps.userWithBalance(int)
  ├── matches "When they transfer £{int}"
  │     → PaymentSteps.transferAmount(int)
  └── matches "Then they see {string}"
        → UISteps.assertMessage(String)

Per-Scenario lifecycle:
  @Before hooks (tagged filters)
    │
  Step 1 → Step 2 → Step 3
    │
  @After hooks
    │
  Report (HTML / JSON / JUnit XML)
```

**Hooks execution order:**

| Hook        | Scope              | Typical use                      |
|-------------|--------------------|----------------------------------|
| `@Before`   | Before scenario    | Setup test data, start browser   |
| `@After`    | After scenario     | Teardown, screenshot on failure  |
| `@BeforeStep` | Before each step | Logging, state reset             |
| `@AfterStep`  | After each step  | Capture intermediate screenshots |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
 payment.feature
 ┌──────────────────────────────────────────┐
 │  Scenario: Insufficient balance transfer │
 │    Given a user with £100 balance        │
 │    When they transfer £200       ← YOU ARE HERE
 │    Then they see 'Insufficient funds'    │
 │    And the balance remains £100          │
 └───────────────┬──────────────────────────┘
                 │ Cucumber runtime parses AST
                 ▼
       StepDefinitionRegistry
       │   match + inject args
       ▼
  @Given → setup user + balance (DB/mock)
  @When  → call transfer service
  @Then  → assert UI message
  @And   → assert balance unchanged
       │
       ▼
  Cucumber HTML Report
  scenario: PASSED / FAILED
```

**FAILURE PATH:** One step fails → Cucumber marks remaining steps as `SKIPPED`, runs `@After` hooks (enabling screenshot capture on failure), and continues with the next scenario. The report shows the exact failing step and its captured exception.

**WHAT CHANGES AT SCALE:** Use `@CucumberOptions(features = "classpath:features", tags = "@smoke")` to subset runs. Enable parallel execution via `cucumber.execution.parallel.enabled=true` in `junit-platform.properties`. Each scenario runs in isolation - no shared `World` state across threads.

---

### 💻 Code Example

**BAD - fat step definitions (anti-pattern):**
```java
@When("the user completes checkout")
public void userCompletesCheckout() {
    // 80 lines: login, add to cart, apply coupon,
    // select shipping, enter payment, submit,
    // assert confirmation page, send email...
    // ALL in one step definition method
    loginAsTestUser();
    addItemToCart("SKU-001");
    applyCoupon("SAVE10");
    selectShipping("express");
    enterCard("4111111111111111");
    clickSubmit();
    assertConfirmationPage();
    verifyEmailSent();
}
```

**GOOD - thin step definitions + domain helpers:**
```java
// Step definitions stay thin - delegate to domain helpers
@Given("a logged-in user with {int} GBP balance")
public void userWithBalance(int amount) {
    world.user = UserFixture.withBalance(amount);
    world.session = authService.login(world.user);
}

@When("they transfer {int} GBP to {string}")
public void transferAmount(int amount, String recipient) {
    world.result = transferService
        .transfer(world.session, amount, recipient);
}

@Then("they see the error {string}")
public void assertErrorMessage(String expected) {
    assertThat(world.result.errorMessage())
        .isEqualTo(expected);
}

@And("the balance remains {int} GBP")
public void assertBalance(int expected) {
    assertThat(accountService.getBalance(world.user))
        .isEqualByComparingTo(BigDecimal.valueOf(expected));
}
```

**GOOD - Scenario Outline with Examples table:**
```gherkin
Scenario Outline: Transfer validation
  Given a user with <balance> GBP balance
  When they transfer <amount> GBP to "Bob"
  Then they see the error "<error>"

  Examples:
    | balance | amount | error                |
    | 100     | 200    | Insufficient funds   |
    | 0       | 1      | Account frozen       |
    | 100     | 0      | Amount must be > 0   |
```

---

### ⚖️ Comparison Table

| Feature             | Cucumber       | Karate         | JBehave        | SpecFlow (.NET) |
|---------------------|:--------------:|:--------------:|:--------------:|:---------------:|
| Language            | Java/Ruby/JS   | Java (DSL)     | Java           | C#              |
| Glue code required  | Yes            | No             | Yes            | Yes             |
| API testing built-in| No             | Yes            | No             | No              |
| Non-engineer access | High           | High           | Medium         | High            |
| BDD philosophy      | Full           | Partial        | Full           | Full            |
| Parallel support    | Plugin/config  | Built-in       | JUnit          | SpecFlow+       |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Cucumber is just a test framework" | It is a collaboration tool first - the test framework is the mechanism, not the purpose. |
| "BAs must write feature files" | In practice, the team writes them together in "Three Amigos" sessions (dev + QA + BA). |
| "Step definitions can contain business logic" | They should contain *only* wiring calls to domain helpers. Logic in step defs is the "fat step definitions" anti-pattern. |
| "Scenario Outline replaces parameterized unit tests" | It replaces *acceptance-level* parameterized scenarios; JUnit `@ParameterizedTest` remains appropriate for unit-level data-driven tests. |
| "Tags are just for filtering" | Tags also control `@Before`/`@After` hook execution - misusing them causes expensive setup to run for unrelated scenarios. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - "Fat step definitions" anti-pattern**

**Symptom:** Step definition methods exceed 20 lines; business logic, assertions, and infrastructure code are intermixed. Reuse is impossible; test failures are undiagnosable.

**Root Cause:** Teams treat step definitions as test methods rather than thin delegation wrappers.

**Diagnostic:**
```bash
# Find step defs with high line counts
awk '/^    @(Given|When|Then|And)/{flag=1; count=0}
     flag{count++}
     /^    }$/ && flag{
       if(count>15) print FILENAME": "count" lines"; flag=0
     }' src/test/java/**/*Steps.java
```
**Fix:**
```java
// BAD - logic in step definition
@When("checkout is completed")
public void checkout() {
    driver.findElement(By.id("cart")).click();
    driver.findElement(By.id("pay")).sendKeys("4111...");
    // 30 more lines
}

// GOOD - delegate to page object / domain helper
@When("checkout is completed")
public void checkout() {
    checkoutPage.completeWithCard(TestCards.VALID);
}
```
**Prevention:** ArchUnit rule: step definition methods must not exceed 5 lines of delegation calls.

---

**Mode 2 - State leakage between scenarios**

**Symptom:** Scenarios pass in isolation but fail when run in suite order; failure is non-deterministic.

**Root Cause:** Shared mutable fields in step definition classes persist between scenarios when DI scope is misconfigured.

**Diagnostic:**
```bash
mvn test -Dcucumber.execution.order=random \
  2>&1 | grep FAILED | head -20
```
**Fix:**
```java
// BAD - static/shared field survives between scenarios
public class PaymentSteps {
    private static User user; // leaks!

// GOOD - inject World via DI (PicoContainer / Spring)
public class PaymentSteps {
    private final World world;
    public PaymentSteps(World world) {
        this.world = world; // new instance per scenario
    }
}
```
**Prevention:** Use PicoContainer or Spring DI; never use `static` fields in step definition classes.

---

**Mode 3 - Undefined steps silently skipped in CI**

**Symptom:** New Gherkin steps are added but CI reports green; the steps were never implemented.

**Root Cause:** Cucumber's default `--snippets CAMELCASE` mode generates console snippets but does not fail the build for undefined steps unless `strict` mode is enabled.

**Diagnostic:**
```bash
mvn test 2>&1 | grep -E "Undefined|Pending|snippet"
```
**Fix:**
```java
// BAD - strict not set, undefined steps pass
@CucumberOptions(features = "classpath:features")

// GOOD - fail on undefined or pending steps
@CucumberOptions(
    features = "classpath:features",
    monochrome = true,
    publish = false
)
// Add to junit-platform.properties:
// cucumber.execution.strict=true
```
**Prevention:** Add `cucumber.execution.strict=true` to `junit-platform.properties`; break CI if any scenario has `UNDEFINED` status.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** BDD, Testing, Java Language

**Builds On This (learn these next):** CI-CD, Karate Framework (API Testing), SpecFlow

**Alternatives / Comparisons:** Karate Framework (API Testing), JBehave, SpecFlow

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    │ BDD framework, Gherkin→Java  │
│ PROBLEM       │ Spec-to-test translation gap │
│ KEY INSIGHT   │ Feature file IS the spec     │
│ USE WHEN      │ Cross-functional BDD teams   │
│ AVOID WHEN    │ Solo dev, no BA involvement  │
│ TRADE-OFF     │ Collaboration vs. overhead   │
│ ONE-LINER     │ Given/When/Then → step defs  │
│ NEXT EXPLORE  │ PicoContainer DI, tags hooks │
└──────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** Karate eliminates step definitions; Cucumber requires them. Under what team composition and project type does Cucumber's higher setup cost produce a net benefit over Karate's zero-glue approach?
2. **(Root Cause)** A Cucumber suite runs green in isolation but produces intermittent failures in CI parallel mode. Walk through the three most likely root causes and how you would isolate each one.
3. **(First Principles)** The "living documentation" promise of BDD assumes feature files are kept accurate as the system evolves. What organisational or technical mechanisms would you put in place to prevent feature files from becoming stale documentation over a 2-year project?
