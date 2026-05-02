---
layout: default
title: "Test Reporting"
parent: "Testing"
nav_order: 1175
permalink: /testing/test-reporting/
number: "1175"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, CI-CD, JUnit 5
used_by: Developers, QA, Tech Leads, Engineering Management
related: JUnit 5, CI-CD, SonarQube Quality Gate, Observability, Test Coverage Targets
tags:
  - testing
  - reporting
  - metrics
  - ci-cd
  - allure
---

# 1175 — Test Reporting

⚡ TL;DR — Test reporting transforms raw test results (pass/fail counts) into actionable insights — failure diagnosis, trend analysis, flakiness detection, and coverage visualization — enabling teams to understand and improve their testing effectiveness.

| #1175           | Category: Testing                                                            | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, CI-CD, JUnit 5                                                    |                 |
| **Used by:**    | Developers, QA, Tech Leads, Engineering Management                           |                 |
| **Related:**    | JUnit 5, CI-CD, SonarQube Quality Gate, Observability, Test Coverage Targets |                 |

### 🔥 The Problem This Solves

"CI FAILED" — BUT WHERE?:
A 5,000-test CI run fails with "47 tests failed." The log file is 50,000 lines. Finding the actual failure requires scrolling through noise. With good test reporting: CI shows a structured failure summary — exactly which tests failed, why, and the full stack trace, with one click to the relevant test file.

FLAKINESS IS INVISIBLE WITHOUT HISTORY:
Test A fails today. Was it flaky or a real failure? Without historical test data (pass rate over last 100 runs), there's no way to know. Good test reporting tracks test history, surfaces flaky tests, and measures the impact of test health on team velocity.

### 📘 Textbook Definition

**Test reporting** is the process of collecting, formatting, and presenting test execution results in a human-readable and actionable form. Reporting occurs at multiple levels: (1) **per-run reports** — detailed results of a specific test run (JUnit XML, HTML reports, Allure Report); (2) **trend reports** — test results over time (pass rate, flakiness rate, average duration); (3) **coverage reports** — which code was exercised (JaCoCo HTML, SonarQube); (4) **CI integration** — surfacing test results directly in CI platforms (GitHub Actions test summary, Jenkins test results). Tools: JUnit XML (standard format), Allure Report (rich HTML), Surefire HTML (Maven), Gradle's built-in HTML report, Playwright's HTML report.

### ⏱️ Understand It in 30 Seconds

**One line:**
Test reports answer "what failed, why, and how often" — turning test results into engineering decisions.

**One analogy:**

> Test reporting is the **control room dashboard**: during a NASA mission, raw telemetry data from thousands of sensors is useless. The dashboard transforms it into actionable signals — green lights for OK, amber for warning, red for immediate action required. Test reports are the dashboard for your test suite's health.

### 🔩 First Principles Explanation

JUNIT XML — THE UNIVERSAL FORMAT:

```xml
<!-- JUnit XML: produced by JUnit, TestNG, pytest, Jest, etc. -->
<!-- Consumed by: Jenkins, GitHub Actions, GitLab CI, Allure, SonarQube -->
<testsuite name="OrderServiceTest" tests="15" failures="1" errors="0"
           skipped="2" time="3.456">

    <testcase name="placeOrder_success" classname="com.example.OrderServiceTest"
              time="0.123"/>

    <testcase name="placeOrder_outOfStock_throws409"
              classname="com.example.OrderServiceTest" time="0.045">
        <failure type="AssertionError">
            Expected: 409
            Actual: 500
            at com.example.OrderServiceTest.placeOrder_outOfStock_throws409(OrderServiceTest.java:87)
            Caused by: NullPointerException at OrderService.java:234
        </failure>
    </testcase>

    <testcase name="placeOrder_paymentFailed" classname="com.example.OrderServiceTest">
        <skipped message="@Disabled: payment gateway not available in CI"/>
    </testcase>

</testsuite>
```

REPORTING TOOLS:

```
1. MAVEN SUREFIRE HTML REPORT:
   Generated at: target/surefire-reports/index.html
   Shows: pass/fail per class and method, stack traces for failures
   Run: mvn test → automatic

2. ALLURE REPORT (rich, interactive):
   Integration: allure-junit5 + @Description, @Epic, @Feature, @Story annotations
   Generates: interactive HTML with:
     - Test suite tree with pass/fail/skip status
     - Trend chart (last N runs)
     - Flaky tests detection
     - Attachment support (screenshots, logs, response bodies)
     - BDD-style test descriptions

   @Test
   @Description("Order placed with valid credit card should return orderId")
   @Epic("Order Management")
   @Feature("Order Placement")
   @Story("Successful checkout")
   void placeOrder_success() { ... }

3. PLAYWRIGHT HTML REPORT:
   npx playwright show-report
   Shows: test results with screenshots, video, trace viewer per test
   Pass/fail/flaky status per test
   Perfect for E2E test failure diagnosis

4. GITHUB ACTIONS TEST SUMMARY:
   Uses JUnit XML to show test results in PR/workflow summary:
   - Total tests, passed, failed, skipped counts
   - List of failed tests with links to workflow step

   - uses: dorny/test-reporter@v1
     with:
       name: Unit Tests
       path: target/surefire-reports/*.xml
       reporter: java-junit

5. JACOCO COVERAGE REPORT:
   target/site/jacoco/index.html
   Shows: package/class/method/line coverage
   Color-coded: green (covered), yellow (partial), red (uncovered)
   Drill-down: click a class to see which lines are uncovered
```

KEY METRICS IN TEST REPORTS:

```
PASS RATE:
  Current run: passed/total
  Trend: is it improving or degrading over time?

DURATION:
  Total suite duration (is it growing? time budget breach?)
  Slowest tests (candidates for optimization or parallelization)

FAILURE ANALYSIS:
  Failure rate per test: "Test X fails 20% of runs → flaky"
  Failure correlation: tests that fail together (shared state issue)

COVERAGE TRENDS:
  Coverage this run vs. last week
  Coverage per module (is payment module dropping below 80%?)

SKIP RATE:
  @Disabled tests accumulate over time
  High skip rate = test debt (tests that should pass but are ignored)
```

FLAKINESS TRACKING:

```
To detect flaky tests, track per-test history:

For each test over last 100 runs:
  pass_rate = sum(passed) / 100

pass_rate = 1.00 (100%) → reliable
pass_rate = 0.95 (95%) → suspect flaky
pass_rate < 0.99 (< 99%) → flagged flaky → quarantine

Tools that track this automatically:
  - GitHub Actions: flaky test detection (beta)
  - BuildKite Test Analytics
  - Gradle Enterprise (Test Distribution + flakiness detection)
  - Custom: store JUnit XML results per run, query flakiness rate
```

### 🧪 Thought Experiment

THE MISSING SKIP AUDIT:

```
Project has 500 tests. CI always shows 500 run, 498 passed, 2 skipped.
"Good enough."

6 months later: 500 tests. CI shows 500 run, 480 passed, 20 skipped.
Team doesn't notice because they just look at "passed count."

The 20 skipped tests were added with @Disabled for various reasons:
  - "TODO: fix this when we upgrade to Java 17"
  - "This is flaky, disabling for now"
  - "No longer valid after API change" (i.e., the test is permanently wrong)

Test report with SKIP TREND would have shown:
  Month 1: 2 skipped
  Month 2: 5 skipped
  Month 3: 12 skipped
  Month 6: 20 skipped (alert: skip rate increasing)

Rule: @Disabled must have: (1) explanation, (2) JIRA ticket, (3) expiry (delete if not fixed within 30 days)
```

### 🧠 Mental Model / Analogy

> Test reporting is **financial reporting for test suite health**: just as quarterly financial reports show revenue trends, profit margins, and anomalies (not just "are we profitable?"), test reports show test duration trends, flakiness rates, and coverage trends — not just "did it pass?". Executives see financial trends; tech leads see test health trends. Both enable data-driven decisions.

### 📶 Gradual Depth — Four Levels

**Level 1:** CI shows pass/fail count + which tests failed. Click through to see stack trace. JUnit XML is the standard format that all CI tools understand.

**Level 2:** Allure Report: rich HTML with annotations (`@Feature`, `@Story`). Attach screenshots on failure, log HTTP request/response bodies. Trend chart shows improvement over time. Maven Surefire: `target/surefire-reports/*.xml` parsed by CI tools for PR status checks.

**Level 3:** Flakiness detection: store test run results in a database (CI artifact); query pass rate per test over 100 runs; surface tests with < 99% pass rate as flaky; quarantine with `@Tag("flaky")`. Duration trend: track suite duration over time — gradual increase indicates accumulating slow tests (candidates for optimization). Coverage trend in SonarQube: line coverage per module plotted over time — dropping coverage alerts to missing tests.

**Level 4:** Test analytics at scale: Gradle Enterprise, BuildKite Test Analytics — enterprise-grade test history, flakiness prediction, build failure attribution. Custom analytics: test results as events in a data pipeline (JUnit XML → Kafka → ClickHouse → Grafana); engineering leadership tracks test suite health as an OKR. Test efficiency metrics: "test-to-value ratio" — for each test, how often has it caught a real bug vs. how many times has it run? Low ratio on slow tests = candidates for removal. "Shift left" metrics: are failures caught in unit tests (cheap) or E2E tests (expensive)?

### 💻 Code Example

```java
// Allure Report annotations
@Test
@DisplayName("Placing an order with a valid card should create a PENDING order")
@Description("Full order placement flow: validate product availability, " +
              "charge payment, create order record")
@Epic("Commerce")
@Feature("Order Management")
@Story("Successful order placement")
@Severity(SeverityLevel.CRITICAL)
void placeOrder_validCard_returnsPendingOrder() {
    Allure.step("Given a product in stock", () -> {
        productService.setStock("PROD-001", 10);
    });

    Allure.step("When order is placed with valid payment token", () -> {
        response = orderService.placeOrder(
            new OrderRequest("PROD-001", 1, "tok_visa_valid"));
    });

    Allure.step("Then order status should be PENDING", () -> {
        assertThat(response.getStatus()).isEqualTo(OrderStatus.PENDING);
        assertThat(response.getOrderId()).isNotNull();
    });
}
```

```yaml
# GitHub Actions: test report + JUnit summary
- name: Run Tests
  run: ./mvnw test

- name: Publish Test Report
  uses: dorny/test-reporter@v1
  if: always() # Run even if tests fail
  with:
    name: Unit Tests
    path: "target/surefire-reports/*.xml"
    reporter: java-junit
    fail-on-error: true

- name: Upload Allure Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: allure-report
    path: target/allure-results/
```

```bash
# Allure CLI: generate and open report
mvn allure:report
allure open target/site/allure-maven-plugin/
```

### ⚖️ Comparison Table

| Tool                   | Type             | Rich UI         | Trend | Flakiness | Best For                     |
| ---------------------- | ---------------- | --------------- | ----- | --------- | ---------------------------- |
| JUnit XML              | Format           | No              | No    | No        | CI parsing standard          |
| Maven Surefire HTML    | Static HTML      | Basic           | No    | No        | Quick local review           |
| Allure Report          | Interactive HTML | Excellent       | Yes   | Yes       | Comprehensive test reporting |
| Playwright HTML Report | Interactive HTML | Excellent (E2E) | No    | Basic     | E2E test diagnosis           |
| Gradle Enterprise      | Cloud analytics  | Excellent       | Yes   | Yes       | Enterprise at scale          |

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                          |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| "JUnit pass/fail count is sufficient reporting" | Without failure details, duration trends, and flakiness tracking, teams can't act on test health                 |
| "Coverage report = test quality report"         | Coverage shows what was executed; test quality requires mutation testing, failure analysis, and assertion review |
| "Test reports are for QA only"                  | Test health metrics are engineering metrics — part of sprint health tracking and technical debt management       |

### 🚨 Failure Modes & Diagnosis

**1. Report Not Generated on Failure**
Cause: CI step exits early (fail-fast); report generation step never runs.
Fix: `if: always()` in GitHub Actions; `always()` in Jenkins post-build step — ensures report generation runs regardless of test outcome.

**2. Flaky Tests Invisible in Aggregate Reports**
Cause: Aggregate "98% pass rate" looks fine; individual test with 60% pass rate is hidden.
Fix: Track and report per-test pass rate (not just aggregate). Alert when any individual test falls below threshold.

**3. Historical Reports Not Retained**
Cause: CI artifacts deleted after 7 days; no trend data available.
Fix: Publish test summary to a persistent store (database, Allure server, Gradle Enterprise). Or increase artifact retention period.

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, CI-CD, JUnit 5
- **Related:** Allure Report, JUnit XML, Surefire, Playwright, Flaky Tests, SonarQube, JaCoCo, Test Coverage Targets

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Transform test results into actionable   │
│              │ insights: failures, trends, flakiness    │
├──────────────┼───────────────────────────────────────────┤
│ STANDARD     │ JUnit XML: universal format parsed by    │
│ FORMAT       │ all CI tools                             │
├──────────────┼───────────────────────────────────────────┤
│ RICH REPORT  │ Allure: interactive HTML, trend charts,  │
│              │ BDD-style descriptions, attachments      │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS       │ Generate report even if tests fail       │
│ GENERATE     │ (if: always() in CI)                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't just know if tests pass — know    │
│              │  why they fail and how often they flake" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Allure Report integrates with BDD frameworks (Cucumber, JBehave) to produce business-readable test reports. Describe: (1) how Cucumber BDD scenarios (`Given / When / Then`) are rendered in Allure as structured test steps with each step's pass/fail status, (2) how product owners and non-technical stakeholders can read Allure reports organized by `@Epic` and `@Feature` to understand what business behaviors are tested and passing, (3) the Allure Testops platform (Allure's enterprise product) — persistent test case management, linking test runs to requirements and bugs, test ownership, and historical analytics, (4) how screenshots captured by Playwright or Selenium tests are attached to Allure reports for failed tests — providing instant visual context for failure diagnosis without needing to reproduce locally, and (5) the "living documentation" value proposition — Allure reports as a continuously updated, always-accurate record of what the application does, linked to the code that verifies it.

**Q2.** Test metrics as engineering KPIs: describe a test health OKR framework for an engineering team. Include: (1) Objective: "Improve test suite reliability and speed to enable faster delivery", (2) Key Results: (a) flakiness rate < 0.5% (measured: flaky test count / total test count in last 30 days), (b) full CI pipeline duration < 15 minutes (measured: 90th percentile CI duration), (c) test coverage on new code > 80% (measured: SonarQube new code coverage), (d) zero open @Disabled tests older than 30 days, (3) how to instrument and track these KPIs: CI metrics to InfluxDB/CloudWatch, SonarQube API for coverage, custom flakiness tracking query on test history, (4) the "Test Tax" concept — every flaky test costs developer time investigating false failures; quantify the cost (N flaky tests × M false failures/week × 10 min investigation = X hours/week lost), and (5) how to prioritize test improvement work: fix flaky tests first (highest impact on developer trust), then speed (second highest impact on feedback loop), then coverage (improves over time with new code standards).
