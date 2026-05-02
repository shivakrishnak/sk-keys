---
layout: default
title: "Test Stage"
parent: "CI/CD"
nav_order: 996
permalink: /ci-cd/test-stage/
number: "0996"
category: CI/CD
difficulty: ★☆☆
depends_on: Build Stage, Automated Testing, Unit Test
used_by: Continuous Delivery, Continuous Deployment, Shift Left Testing
related: Build Stage, Shift Left Testing, Code Coverage
tags:
  - cicd
  - testing
  - devops
  - foundational
  - bestpractice
---

# 0996 — Test Stage

⚡ TL;DR — The test stage runs automated tests against the built artifact in the CI/CD pipeline, forming the safety gate that prevents broken code from advancing to deployment.

| #0996 | Category: CI/CD | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Build Stage, Automated Testing, Unit Test | |
| **Used by:** | Continuous Delivery, Continuous Deployment, Shift Left Testing | |
| **Related:** | Build Stage, Shift Left Testing, Code Coverage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Code that compiles perfectly can still be completely broken. A function that appears correct but divides by zero when the input is 0. A REST endpoint that succeeds but returns a 200 with a malformed JSON body. A database query that works for 5 records but fails for 5 million. Without a test stage, these bugs are only discovered when a human exercises the feature manually — or worse, when a customer does.

**THE BREAKING POINT:**
Manual testing doesn't scale. With 10 developers each making 3 commits per day, a QA team would need to test 30 changes daily just to keep up. Every hour of delay between commit and test result is an hour of context-switching cost when the bug is eventually found.

**THE INVENTION MOMENT:**
This is exactly why the test stage exists: encode as much human verification as possible into automated assertions that run on every single commit, providing the same confidence as manual testing at machine speed.

---

### 📘 Textbook Definition

The **test stage** is a pipeline stage that executes the project's automated test suite against the artifact produced by the build stage. It runs in an isolated environment, reports pass/fail for each test, and gates downstream stages — deployment proceeds only if all required tests pass. The test stage typically contains multiple layers: unit tests (fast, isolated), integration tests (slower, with real dependencies), and sometimes acceptance tests (full system behaviour). Code coverage reports may be generated and enforced as a minimum threshold.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The test stage proves the code does what it's supposed to do, not just that it compiles.

**One analogy:**
> The build stage proves a car starts. The test stage proves the brakes work, the steering responds, and the speedometer is accurate. A car that starts but can't stop is not road-safe — and production software that compiles but fails its core functions is not deployment-safe.

**One insight:**
The test stage is valuable only if the tests are meaningful. A test suite with 100% trivial assertions that never touch critical logic gives false confidence. The test stage is the gatekeeper, but the quality of the gate is entirely determined by the quality of the tests it runs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Tests must run against the artifact produced by the build stage — never re-build.
2. Tests must be deterministic — the same code must produce the same pass/fail result.
3. Test failure must block downstream stages and alert the committing developer.

**DERIVED DESIGN:**
The test stage is structured as a pyramid: unit tests (many, fast, isolated) run first, then integration tests (fewer, slower, with real dependencies), then E2E tests (fewest, slowest, full system). Fast tests gate slow tests — if 300 unit tests fail, there's no value in running 30 integration tests.

Parallelism: test suites can be split across parallel runners. 200 unit tests that take 4 minutes on 1 runner take 1 minute on 4 runners. The CI job aggregates results from all runners and reports the combined pass/fail.

**THE TRADE-OFFS:**
**Gain:** Automated verification of correctness with every commit. Regression protection — a passing test suite means previously working features still work.
**Cost:** Tests must be written and maintained. Flaky tests erode confidence. Slow test suites create bottlenecks. The test stage is only as good as the tests it runs.

---

### 🧪 Thought Experiment

**SETUP:**
A team ships a payment service. Every commit triggers a test stage with 150 unit tests and 20 integration tests.

**WHAT HAPPENS WITHOUT THE TEST STAGE:**
Developer adds a discount calculation feature. The code looks correct. It deploys to staging. Three days later, QA finds that a 10% discount on $100 returns $1 instead of $90 — a floating-point arithmetic precision bug. Three days of debug cycle. Fix requires re-testing the whole feature.

**WHAT HAPPENS WITH THE TEST STAGE:**
The developer commits the discount logic. The test stage runs a unit test: `assertThat(applyDiscount(100.0, 10)).isEqualTo(90.0)`. The test fails — the developer sees the precise failure within 4 minutes. The bug is fixed while the code is still fresh. It never reaches staging.

**THE INSIGHT:**
Automated tests encode the developer's intent as machine-verifiable assertions. The test stage enforces those assertions on every subsequent change — protecting against regressions and catching logical errors at their source.

---

### 🧠 Mental Model / Analogy

> The test stage is like a pre-flight checklist for a commercial aircraft. Before every flight, the same 50 checks are performed in order — engines, fuel, hydraulics, instruments. If any check fails, the plane doesn't leave the gate. The checklist catches problems even when the plane looks fine externally.

- "Pre-flight checklist items" → individual test cases
- "Check fails" → test assertion fails
- "Plane doesn't leave the gate" → pipeline blocked, no deployment
- "Performed before every flight" → test stage runs on every commit
- "Pilot who knows the plane well wrote the checklist" → developer who knows the feature writes the test

Where this analogy breaks down: a pre-flight checklist checks physical state; software tests check logical behaviour. A test can only verify what it explicitly asserts — unlike a physical inspection which catches visible anomalies beyond the checklist.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
After the code is compiled, the computer automatically runs hundreds of small checks that verify the software does what it's supposed to do. If any check fails, the code is stopped and the developer is told exactly which check failed and why.

**Level 2 — How to use it (junior developer):**
In your pipeline YAML, the test stage runs after the build stage and uses the artifact it produced. For Java: `mvn test` or `mvn verify`. For JavaScript: `npm test`. Use `if: always()` on the test result upload step to capture reports even on failure. Configure code coverage thresholds — fail the stage if coverage drops below 80%. Never skip tests with flags like `-DskipTests` in the test stage.

**Level 3 — How it works (mid-level engineer):**
Split the test stage into multiple jobs: `unit-tests` (runs immediately, no dependencies), `integration-tests` (runs after unit-tests, uses Testcontainers or a dedicated Docker Compose environment), `acceptance-tests` (runs against staging after deployment). Parallelise the unit test job across 4 runners using test splitting (JUnit's `@Tag`, pytest's `--shard`). Aggregate coverage from all runners with JaCoCo's merge step.

**Level 4 — Why it was designed this way (senior/staff):**
The test pyramid (many unit, fewer integration, fewest E2E) is an economic model, not a technical rule. Unit tests are cheap because they're fast and isolated; E2E tests are expensive because they're slow and require full stack infrastructure. The pyramid maximises coverage per dollar spent on CI infrastructure. At scale, teams invest in test impact analysis — running only the tests affected by changed code. Facebook's "test selection" system reduced test execution from hours to minutes by analysing code change impact graphs.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│             TEST STAGE EXECUTION                 │
├──────────────────────────────────────────────────┤
│  Input: artifact from build stage                │
│  (Docker image pulled from registry)             │
│         ↓                                        │
│  TIER 1: Unit Tests (fast gate)                  │
│   - No network, no DB, all mocked                │
│   - Target: < 5 minutes                          │
│   - 200+ tests → run in parallel (4 shards)      │
│         ↓ ALL PASS                               │
│  TIER 2: Integration Tests                       │
│   - Real DB (Testcontainers: PostgreSQL)         │
│   - Real cache (Redis container)                 │
│   - Tests service layer with real I/O            │
│   - Target: < 10 minutes                         │
│         ↓ ALL PASS                               │
│  Coverage check (JaCoCo)                         │
│   - Line coverage ≥ 80%                          │
│   - Branch coverage ≥ 70%                        │
│         ↓ PASS                                   │
│  Test reports uploaded to CI artifacts           │
│  → Deploy stage released                         │
└──────────────────────────────────────────────────┘
```

**Test isolation:** Each test tier runs in a fresh container. Unit tests have no network access — this enforces isolation and catches tests that accidentally depend on external services. Integration tests start required infrastructure via Testcontainers or `docker-compose` before the tests run.

**Test parallelism:** A JUnit test suite can be partitioned by test class or method count across multiple CI runners. Each runner executes its subset and uploads a results XML. The aggregation job combines all XMLs and reports the final pass/fail. A 12-minute suite becomes a 3-minute suite with 4 parallel runners.

**Coverage enforcement:** JaCoCo instruments the bytecode during test execution and reports which lines and branches were executed. A `jacoco:check` goal fails the build if the configured minimum is not met. This prevents coverage from eroding over time through uncovered new code additions.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Build stage: JAR + Docker image produced
  → Unit tests: 247 pass, 0 fail (3m 10s)
  → Integration tests: 42 pass (7m 30s) [← YOU ARE HERE]
  → Coverage: 83% lines, 76% branches → PASS
  → Test reports uploaded
  → PR: test stage ✓
  → Deploy to staging stage triggered
```

**FAILURE PATH:**
```
Unit test fails: PaymentServiceTest.discountCalculation
  → FAIL: expected 90.00 but was 1.00
  → Integration tests: NOT RUN (fast-fail)
  → Deploy stage: NOT TRIGGERED
  → PR shows ✗ — merge blocked
  → Slack: "@alice: Test failed: PaymentServiceTest#discount"
  → Developer fixes → pushes → test stage reruns
```

**WHAT CHANGES AT SCALE:**
At 500+ services with 10,000+ tests each, the "run all tests" approach breaks down. Test impact analysis (running only tests that cover changed code) becomes necessary. Teams track test flake rates as SLO metrics: a test suite with >2% flake rate is considered unhealthy and triggers an automatic quarantine. Test infrastructure cost is a real concern — parallelising 10,000 tests costs money in CI compute minutes.

---

### 💻 Code Example

**Example 1 — Parallel unit tests with GitHub Actions matrix:**
```yaml
unit-tests:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      shard: [1, 2, 3, 4]  # 4 parallel runners
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with: { java-version: '21', cache: maven }
    - name: Run unit tests (shard ${{ matrix.shard }} of 4)
      run: |
        mvn test \
          -Dsurefire.forkCount=2 \
          -Dgroups=shard${{ matrix.shard }}
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: surefire-reports-${{ matrix.shard }}
        path: target/surefire-reports/

aggregate-results:
  needs: unit-tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v4
      with: { pattern: surefire-reports-* }
    - name: Merge test results
      run: |
        # Fail if any shard uploaded failures
        find . -name "*.xml" -exec \
          grep -l 'failures="[^0]"\|errors="[^0]"' {} \;
```

**Example 2 — Coverage enforcement with JaCoCo:**
```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <executions>
    <execution>
      <id>check</id>
      <goals><goal>check</goal></goals>
      <configuration>
        <rules>
          <rule>
            <limits>
              <!-- fail if line coverage < 80% -->
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.80</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

---

### ⚖️ Comparison Table

| Test Type | Speed | Isolation | Confidence | Stage Position |
|---|---|---|---|---|
| **Unit Tests** | Seconds | Complete (all mocks) | Logic correctness | First — fast gate |
| Integration Tests | Minutes | Partial (real DB/cache) | Service behaviour | Second — after unit |
| Contract Tests | Minutes | Partial | API compatibility | Second — parallel |
| E2E / Acceptance Tests | 10–45 min | None (full stack) | User journey | Last — pre-prod |
| Performance Tests | 15–60 min | None | Load behaviour | Post-merge (non-blocking) |

How to choose: Run unit tests on every commit as the primary gate. Add integration tests for critical service boundaries. Reserve E2E tests for the final pre-production stage. Performance tests should run post-merge, not blocking every PR.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 100% test coverage means no bugs | Coverage measures which lines execute, not whether they behave correctly. A test that executes `divide(a, b)` with `b=1` achieves coverage but misses the `b=0` edge case |
| Flaky tests should be retried until they pass | Flaky tests should be investigated and fixed or quarantined. Retrying masks the underlying non-determinism and erodes confidence in the test suite |
| Slow tests should be moved to the end and kept | Slow tests should be made fast (mock expensive I/O, parallelise) or moved to a non-blocking post-merge suite. Keeping them slow creates a pipeline bottleneck |
| A test stage is only needed when the team is large | Single developers benefit equally from automated tests — it prevents regressions as the codebase grows, regardless of team size |

---

### 🚨 Failure Modes & Diagnosis

**1. Flaky Tests Undermine Pipeline Confidence**

**Symptom:** Developers re-run failed builds without reading the failure. "Just a flaky test" becomes the default assumption. Real failures are ignored.

**Root Cause:** Tests depend on timing, external network calls, or shared mutable state between test runs. Non-deterministic outcome.

**Diagnostic:**
```bash
# Run the test suite 10 times and track failures
for i in $(seq 1 10); do
  mvn test -pl :mymodule 2>&1 \
    | grep -E "Tests run:|BUILD" | tail -2
done
```

**Fix:** Quarantine the flaky test immediately with `@Disabled("Flaky: tracked as JIRA-123")`. Investigate root cause. Fix and re-enable.

**Prevention:** Track flake rate as a team metric dashboard. Zero tolerance for >1% flake rate in the blocking stage.

---

**2. Test Stage Passes but Integration Works Differently**

**Symptom:** All 300 tests pass. Code deploys to production and fails on a DB foreign key constraint that never appeared in tests.

**Root Cause:** Integration tests mock the database; the mock silently accepted an invalid foreign key that the real DB rejects.

**Diagnostic:**
```bash
# Check what percentage of tests use real vs mocked DB
grep -r "@MockBean\|@Mock" src/test/ | wc -l
grep -r "Testcontainers\|@DataJpaTest" src/test/ | wc -l
```

**Fix:** Replace mock DB with an in-process real DB (H2) or containerised real DB (Testcontainers PostgreSQL) for repository-layer tests.

**Prevention:** Reserve mocks for true unit tests. Integration tests should use real dependency containers.

---

**3. Coverage Gate Gamed With Empty Tests**

**Symptom:** Coverage reports 85%, but production bugs are common in recently written code.

**Root Cause:** Developers write tests that execute code without meaningful assertions just to meet the coverage threshold.

**Diagnostic:**
```bash
# Find tests with no assertions (JUnit)
grep -r "@Test" src/test/ | while read f; do
  file=$(echo "$f" | cut -d: -f1)
  grep -c "assert\|verify\|assertThat" "$file" \
    || echo "NO ASSERTIONS: $file"
done
```

**Fix:** Add mutation testing (PIT for Java) to the pipeline. Mutation testing verifies that tests actually detect changes in code logic — not just execute lines.

**Prevention:** Include mutation testing score alongside coverage in quality reports. Require >70% mutation score for new code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Build Stage` — the test stage receives the artifact produced by build; build must pass before tests run
- `Unit Test` — the primary test type in the fast-gate tier of the test stage
- `Automated Testing` — tests must be automated for the test stage to be useful in CI

**Builds On This (learn these next):**
- `Shift Left Testing` — the principle that test stages should move closer to the developer to catch issues earlier
- `Code Coverage` — the metric generated during the test stage to measure test thoroughness
- `Continuous Delivery` — the test stage is a prerequisite gate for CD to function safely

**Alternatives / Comparisons:**
- `Manual QA` — human testing that the test stage replaces for regression verification; still needed for exploratory testing
- `Mutation Testing` — a technique that validates the test stage's tests are actually effective

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pipeline stage that runs automated tests  │
│              │ and blocks deployment on failure          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Logical bugs that pass compilation but    │
│ SOLVES       │ break functionality in production         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The stage is only as good as the tests    │
│              │ it runs — coverage metrics can lie        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every pipeline needs a test      │
│              │ stage as its second gate after build      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — even manual-only apps benefit from  │
│              │ some automated regression tests           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Regression safety vs investment in        │
│              │ writing and maintaining tests             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A car that starts but can't stop is not  │
│              │  road-safe — the test stage checks both"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Code Coverage → Shift Left Testing        │
│              │ → Mutation Testing                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A senior engineer argues: "Our test stage passes 98% of the time — it's reliable enough. Flaky tests just indicate intermittent environmental issues, not code problems." A junior engineer argues: "A 2% flake rate means 1 in 50 pipeline runs is a false positive — that's unacceptable." Who is right, and what concrete data would you need to resolve this disagreement objectively?

**Q2.** Your test stage currently takes 28 minutes: unit tests 4 min, integration tests 12 min, acceptance tests 12 min — all sequential. The team merges 20 PRs per day. Describe the pipeline restructuring that would bring the PR-blocking feedback time under 8 minutes without removing any tests from the process. What new failure mode do you introduce with this restructuring?

