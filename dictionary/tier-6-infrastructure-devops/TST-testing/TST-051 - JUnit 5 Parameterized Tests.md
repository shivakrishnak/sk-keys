---
version: 1
layout: default
title: "JUnit 5 Parameterized Tests"
parent: "Testing"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /testing/junit-5-parameterized-tests/
id: TST-051
category: Testing
difficulty: ★★☆
depends_on: JUnit 5, Testing, Java Language
used_by: Testing, CI-CD
related: JUnit 5, TestNG, Spock Framework
tags:
  - testing
  - java
  - intermediate
  - bestpractice
---

# TST-051 - JUnit 5 Parameterized Tests

⚡ **TL;DR -** Run one test method multiple times with different inputs using annotations, eliminating copy-paste test duplication.

| Field      | Value                            |
|------------|----------------------------------|
| Depends on | JUnit 5, Testing, Java Language  |
| Used by    | Testing, CI-CD                   |
| Related    | JUnit 5, TestNG, Spock Framework |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every input variant requires a separate `@Test` method. Testing `isPrime(1)`, `isPrime(2)`, `isPrime(17)` means three near-identical methods that differ only in data. With 20 edge cases you have 20 methods, 19 of which are copy-paste noise carrying zero extra information.

**THE BREAKING POINT:** A team adds a new numeric validator. They want to test 40 boundary combinations. They write 40 methods. The test class exceeds 600 lines. A reviewer cannot tell what is being tested vs. how, and changing the assertion pattern means editing 40 places in sync.

**THE INVENTION MOMENT:** JUnit 5 introduced `@ParameterizedTest` to separate *what* from *how*: define the assertion logic once, supply data rows via annotations. The framework iterates the method over every argument set automatically, reporting each as an individually named test run.

---

### 📘 Textbook Definition

**Parameterized tests** are test methods annotated with `@ParameterizedTest` (plus a source annotation) that JUnit 5 executes once per argument set supplied. Source annotations - `@ValueSource`, `@CsvSource`, `@MethodSource`, `@EnumSource`, `@ArgumentsSource` - identify an `ArgumentsProvider`. JUnit's `ParameterizedTestExtension` (a `TestTemplateInvocationContextProvider`) streams argument sets, converts each via `ArgumentConverter`, and registers one named invocation context per row.

---

### ⏱️ Understand It in 30 Seconds

**One line:** One test method, many data rows - JUnit loops so you don't have to.

> A factory quality-control robot runs the same inspection on every part coming down the conveyor belt, not a separate robot for each part.

**One insight:** Parameterized tests move *data* out of test code and into a declaration, making test intent readable at a glance while keeping failures individually named.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A test is a triple: *input → action → assertion*. Only the input changes across cases.
2. Structural duplication is noise; data duplication is configuration - the two deserve different treatments.
3. Each test case must produce a distinct, identifiable result in the report.

**DERIVED DESIGN:** Extract the invariant triple into one method. Supply inputs via a declarative source annotation. Let the framework generate one named execution per row, each independently pass/fail.

**THE TRADE-OFFS:**
- **Gain:** N test cases for the cost of 1 method + N data rows; failures are isolated and individually named in CI reports.
- **Cost:** Complex object graphs in `@MethodSource` factories can obscure intent; debugging a single failing row requires understanding the parameterisation machinery.

---

### 🧪 Thought Experiment

**SETUP:** You must verify that `isPrime(int n)` returns the correct result for 0, 1, 2, 3, 4, 17, and 100.

**WHAT HAPPENS WITHOUT Parameterized Tests:** You write `testZero()`, `testOne()`, `testTwo()` - seven methods, each two lines. When `isPrime` changes its contract you update seven places. When a new developer adds 5 more edge cases, the class grows by 10 more lines of structural repetition.

**WHAT HAPPENS WITH Parameterized Tests:** You write one method annotated `@ParameterizedTest @CsvSource({"0,false","1,false","2,true","3,true","4,false","17,true","100,false"})`. Seven test runs appear in the report automatically, each named with its input pair. Adding a new case costs one CSV row.

**THE INSIGHT:** The test suite scales with data, not code. The test method expresses *intent*; the source annotation expresses *coverage*.

---

### 🧠 Mental Model / Analogy

> A spreadsheet formula in cell C1 reads `=A1*B1`. You don't copy the formula 100 times - you drag it down. Each row is one parameterized invocation; the formula is your test method.

- **Cell formula** → `@ParameterizedTest` method body (the assertion logic)
- **Row data** → argument source (`@CsvSource`, `@MethodSource`, …)
- **Calculated result** → one test execution with a named result
- **Drag-down** → JUnit's `ParameterizedTestExtension` iterating the provider stream

Where this analogy breaks down: spreadsheet cells are entirely independent; parameterized test instances can share expensive setup via `@BeforeAll` class-level fixtures.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of writing the same test ten times with different numbers, you write it once and give JUnit the numbers in a list. JUnit runs it once per number and shows you which ones passed or failed.

**Level 2 - How to use it (junior developer):**
Replace `@Test` with `@ParameterizedTest`, add `@ValueSource(ints = {1, 2, 3})`, and declare the method parameter as `int value`. For multiple arguments per row, use `@CsvSource({"1,true","2,false"})` with two parameters. For complex objects, create a `static Stream<Arguments>` factory and use `@MethodSource("factoryName")`.

**Level 3 - How it works (mid-level engineer):**
JUnit 5's `ParameterizedTestExtension` implements `TestTemplateInvocationContextProvider`. It reads the resolved `@ArgumentsSource` (convenience annotations are aliases), calls `provideArguments(ExtensionContext)`, converts each `Arguments` element via registered `ArgumentConverter` instances (implicit for primitives/enums/strings, explicit via `@ConvertWith`), and creates one `TestTemplateInvocationContext` per row. The display name is built from the `name` attribute pattern using `{index}`, `{0}`, `{1}` placeholders.

**Level 4 - Why it was designed this way (senior/staff):**
`@ParameterizedTest` is implemented as syntactic sugar over `@TestTemplate`, the lower-level JUnit 5 mechanism for multi-invocation test methods. This design means third-party libraries can provide their own multi-invocation contexts (e.g., Mockito's repeated injection modes) without forking the execution engine. The `ArgumentConverter` SPI decouples data representation from type - CSV sources remain human-readable strings while strongly-typed method parameters receive domain objects - a deliberate separation of concerns that also enables `@CsvFileSource` for externally managed test data.

---

### ⚙️ How It Works (Mechanism)

```
@ParameterizedTest lifecycle:

  DISCOVERY
  ┌─────────────────────────────────┐
  │ JUnit scans @TestTemplate       │
  │ ParameterizedTestExtension      │
  │ registered as invocation        │
  │ context provider                │
  └──────────────┬──────────────────┘
                 │
  EXECUTION (per argument row)
  ┌──────────────▼──────────────────┐
  │ 1. ArgumentsProvider            │
  │    .provideArguments() called   │
  │ 2. ArgumentConverter resolves   │
  │    each element (String→type)   │
  │ 3. InvocationContext created    │
  │    with display name            │
  │ 4. Method invoked with args     │
  │ 5. Result reported as child     │
  │    of @ParameterizedTest node   │
  └─────────────────────────────────┘
```

| Annotation         | Provider class              |
|--------------------|-----------------------------|
| `@ValueSource`     | `ValueArgumentsProvider`    |
| `@CsvSource`       | `CsvArgumentsProvider`      |
| `@MethodSource`    | `MethodArgumentsProvider`   |
| `@EnumSource`      | `EnumArgumentsProvider`     |
| `@ArgumentsSource` | User-defined implementation |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
 Test Class
 ┌─────────────────────────────────────────┐
 │  @ParameterizedTest(name="n={0}→{1}")   │
 │  @CsvSource({"1,false","2,true"})       │
 │  void isPrimeTest(int n, boolean exp) { │
 │      assertEquals(exp, isPrime(n));     │ ← YOU ARE HERE
 │  }                                      │
 └───────────────┬─────────────────────────┘
                 │ JUnit discovers @TestTemplate
                 ▼
      ParameterizedTestExtension
                 │ provideArguments() → Stream
         ┌───────┴────────┐
         ▼                ▼
  [n=1, exp=false]  [n=2, exp=true]
         │                │
    test run 1       test run 2
    "n=1→false"      "n=2→true"
    PASS / FAIL      PASS / FAIL
```

**FAILURE PATH:** One row fails → that invocation is reported as `FAILED [1] n=1→false` while all others still pass or fail independently. The parent node is marked failed. CI surfaces the exact row without re-running all rows.

**WHAT CHANGES AT SCALE:** `@MethodSource` returning a `Stream` sourced from a database query lets you drive 10,000 cases without loading all into memory - JUnit consumes the stream lazily. Combine with `@Execution(CONCURRENT)` to run rows in parallel across threads.

---

### 💻 Code Example

**BAD - copy-paste test explosion:**
```java
@Test
void testPrimeOne() { assertFalse(isPrime(1)); }

@Test
void testPrimeTwo() { assertTrue(isPrime(2)); }

@Test
void testPrimeFour() { assertFalse(isPrime(4)); }
// ... 17 more near-identical methods
```

**GOOD - @CsvSource for simple cases:**
```java
@ParameterizedTest(name = "isPrime({0}) == {1}")
@CsvSource({
    "1,  false",
    "2,  true",
    "3,  true",
    "4,  false",
    "17, true",
    "100,false"
})
void isPrimeTest(int n, boolean expected) {
    assertEquals(expected, MathUtils.isPrime(n));
}
```

**GOOD - @MethodSource for complex objects:**
```java
static Stream<Arguments> invalidEmails() {
    return Stream.of(
        Arguments.of("",      "blank input"),
        Arguments.of("no-at", "missing at-sign"),
        Arguments.of("a@",    "missing domain")
    );
}

@ParameterizedTest(name = "[{index}] {1}")
@MethodSource("invalidEmails")
void rejectsInvalidEmail(String email, String desc) {
    assertThrows(
        InvalidEmailException.class,
        () -> new Email(email)
    );
}
```

---

### ⚖️ Comparison Table

| Feature              | `@CsvSource` | `@MethodSource` | `@EnumSource` | `@ValueSource` |
|----------------------|:------------:|:---------------:|:-------------:|:--------------:|
| Data location        | Inline       | Static method   | Enum class    | Inline         |
| Complex objects      | No           | Yes             | Partial       | No             |
| External data source | No           | Yes (factory)   | No            | No             |
| Null support         | `nullValues` | Yes             | No            | `@NullSource`  |
| Readability (simple) | High         | Medium          | High          | Highest        |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Parameterized tests replace unit tests" | They *are* unit tests - data-driven ones. The same assertion model applies. |
| "`@MethodSource` must be in the same class" | External class fully qualified name is supported: `"com.example.Providers#data"`. |
| "All rows must use the same types" | `@MethodSource` can supply heterogeneous `Arguments`; `@CsvSource` converts implicitly. |
| "One failing row stops the rest" | Each row is an independent invocation; one failure does not abort subsequent rows. |
| "`@EnumSource` always tests all enum values" | Use `names` + `mode = EXCLUDE` to filter specific constants from the run. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Zero tests discovered / "must not be static" error**

**Symptom:** JUnit reports 0 tests found for the parameterized method, or `@MethodSource` factory throws a `PreconditionViolationException`.
**Root Cause:** `@MethodSource` factory is not `static` (required unless `@TestInstance(PER_CLASS)` is active), or `@ParameterizedTest` annotation is absent from the method.
**Diagnostic:**
```bash
mvn test -Dtest=MyTest -Dsurefire.useFile=false \
  2>&1 | grep -E "No tests|PreconditionViolation"
```
**Fix:**
```java
// BAD - instance method without PER_CLASS lifecycle
Stream<Arguments> data() { return Stream.of(…); }

// GOOD - static factory
static Stream<Arguments> data() { return Stream.of(…); }
```
**Prevention:** Enforce `static` on factory methods via ArchUnit rule on all `@MethodSource`-annotated test classes.

---

**Mode 2 - `@CsvSource` null conversion failure**

**Symptom:** `ArgumentConversionException: Failed to convert String "null" to int` at runtime.
**Root Cause:** The literal string `"null"` in a CSV entry is four characters, not Java `null`. Primitives cannot accept null anyway.
**Diagnostic:**
```java
// Reproduce with:
@CsvSource({"null, 0"})
void test(Integer n, int expected) { … }
// Throws unless nullValues configured
```
**Fix:**
```java
// BAD
@CsvSource({"NULL, 0"})

// GOOD
@CsvSource(value = {"NULL, 0"}, nullValues = "NULL")
void test(Integer n, int expected) { … }
```
**Prevention:** Document a team-wide null-token convention (`"NULL"`) in a shared test utility constant.

---

**Mode 3 - Unreadable failure names in CI reports**

**Symptom:** CI surfaces `[1] 1, false` failures; engineers cannot identify the failing case without reading code.
**Root Cause:** Default display name template `[{index}] {arguments}` used; no `name` attribute set on `@ParameterizedTest`.
**Diagnostic:**
```bash
# Inspect Surefire report headers
grep -r "\[1\] " target/surefire-reports/ | head -20
```
**Fix:**
```java
// BAD
@ParameterizedTest
@CsvSource({"1,false"})
void test(int n, boolean e) { … }

// GOOD
@ParameterizedTest(name = "isPrime({0}) expects {1}")
@CsvSource({"1,false"})
void test(int n, boolean e) { … }
```
**Prevention:** Adopt a team-wide `name` pattern standard, enforced via a custom ArchUnit condition on all `@ParameterizedTest` usages.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** JUnit 5, Java Language, Testing

**Builds On This (learn these next):** TestNG, Spock Framework, CI-CD

**Alternatives / Comparisons:** TestNG `@DataProvider`, Spock `where:` block, JUnit 4 `@Parameterized`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    │ Data-driven test template    │
│ PROBLEM       │ Copy-paste test explosion    │
│ KEY INSIGHT   │ Separate logic from data     │
│ USE WHEN      │ Same assertion, N inputs     │
│ AVOID WHEN    │ Setup logic varies per case  │
│ TRADE-OFF     │ Concise vs. debuggability    │
│ ONE-LINER     │ @ParameterizedTest + source  │
│ NEXT EXPLORE  │ @MethodSource factories      │
└──────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** If your `@MethodSource` factory reads 50,000 rows from a database, what happens to JVM heap during test discovery - and how would lazy streaming via `Stream<Arguments>` versus eager `List<Arguments>` change the outcome?
2. **(Design Trade-off)** When would externalising test data to `@CsvFileSource` with a `.csv` file be better than inline `@CsvSource` - and what new maintenance and version-control risks does that introduce?
3. **(System Interaction)** How does `@Execution(CONCURRENT)` on a parameterized test interact with shared mutable state in a `@BeforeEach` setup method, and what test design rules prevent data races between rows?
