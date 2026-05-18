---
id: CSF-055
title: Testing Paradigms for CS Concepts
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-038
used_by: TST-001, TST-010
related: TST-001, CSF-038, CSF-048
tags: [unit-testing, property-based-testing, tdd, mutation-testing, test-pyramid]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/csf/testing-paradigms-for-cs-concepts/
---

⚡ TL;DR - Three test paradigms: example-based (JUnit:
specific input/output), property-based (QuickCheck: "for
all inputs, this holds"), mutation testing (did the test
actually catch the bug?). TDD = write test first. Test
pyramid = many unit, fewer integration, minimal E2E. Pure
functions are trivially testable; side effects require mocking.

| #055 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-038 (Pure Functions) | |
| **Used by:** | TST-001 (Unit Testing), TST-010 (Property-Based Testing) | |
| **Related:** | TST-001 (Unit Testing), CSF-038 (Pure Functions), CSF-048 (Concurrency bugs) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A sorting algorithm passes all manual tests. In production,
it returns incorrect results for empty arrays, arrays with
duplicates, and arrays where all elements are equal. The
developer tested "happy path" cases only. Without a testing
paradigm, the developer has no framework for asking:
"what CLASSES of inputs might break this?" The code ships
with subtle bugs that only surface under specific conditions.

**THE BREAKING POINT:**

Example-based testing (JUnit with specific inputs) is
fundamentally incomplete. Testing `sort([3,1,2])` = `[1,2,3]`
does not test: empty array, single element, all equal, negative
numbers, overflow values, already-sorted input, reverse-sorted
input, duplicates adjacent, duplicates non-adjacent, stable
ordering. A function with 3 parameters, each with 10
possible values: 1,000 combinations. Manually testing them all
is impractical. Property-based testing and systematic
test-case generation address this.

**THE INVENTION MOMENT:**

Unit testing with example inputs (xUnit, JUnit) became
standard in the 1990s (Kent Beck's SUnit for Smalltalk, 1994).
QuickCheck (Haskell, 1999) introduced property-based testing:
instead of specifying inputs, specify PROPERTIES that must
hold for ALL inputs ("for any two lists, concatenating and
sorting should equal sorting and merging"). QuickCheck generates
random inputs and finds counterexamples. TDD (Test-Driven
Development, Kent Beck, 2002) introduced the discipline
of writing tests BEFORE code. Mutation testing (PIT for Java)
evaluates test quality by introducing deliberate bugs
(mutations) and checking if tests detect them.

---

### 📘 Textbook Definition

**Test paradigm:** A systematic approach to software testing
that defines what to test, how to specify tests, and how
to evaluate test quality.

**Example-based testing:** Specify concrete input/expected-output
pairs. JUnit `@Test`. Tests are precise but manually specified.

**Property-based testing:** Specify properties (invariants)
that must hold for all valid inputs. Framework generates
random inputs and checks properties. QuickCheck (Haskell),
jqwik (Java), Hypothesis (Python).

**Mutation testing:** Evaluate test suite quality by introducing
automated bugs (mutations: change `+` to `-`, `>` to `>=`,
return null). A strong test suite kills all mutations (detects
them). Weak tests: mutations survive (bugs would go undetected).
PIT (pitest.org) for Java.

**TDD (Test-Driven Development):** Red-Green-Refactor cycle:
(1) Write a FAILING test for the next small unit of behavior.
(2) Write MINIMAL code to make the test pass.
(3) REFACTOR while all tests remain green.

**Test pyramid:** Unit tests (fast, many) > Integration tests
(slower, fewer) > E2E tests (slowest, fewest). Invert the
pyramid: too many E2E, too few unit tests = slow, fragile CI.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Example tests check specific cases. Property tests check
invariants for all inputs. Mutation tests check if your
tests would catch real bugs. TDD makes tests a design tool,
not an afterthought.

**One analogy:**

> Example-based test: chef tastes one dish and says "this one is good."
> Property-based test: nutritionist checks EVERY dish: "every dish
> must have >0 calories and <2000mg sodium" - regardless of ingredients.
> Mutation test: secretly change the recipe; the chef must notice
> the dish is wrong (if they don't: the taste test is useless).

**One insight:**

Pure functions (same input = same output, no side effects)
are trivially testable: no mock, no setup, no teardown.
`sort([3,1,2])` is pure - test it with thousands of property-based
test cases. Impure functions (side effects: database, HTTP, file)
are hard to test: require mocking the dependencies.
The practical rule: maximize pure function surface area;
isolate impure operations at the edges. This design choice
(driven by testability) results in cleaner architecture
as a side effect.

---

### 🔩 First Principles Explanation

**TESTING THE TESTING:**

A test suite that NEVER fails (even when bugs are introduced)
is worthless. Mutation testing quantifies this:
1. PIT introduces mutations: `balance > 0` -> `balance >= 0`
2. Runs the test suite against the mutated code
3. If tests FAIL (as they should): mutation killed
4. If tests PASS (they should have failed): mutation survived

High mutation score = tests are specific enough to catch
real bugs. Low score = tests are testing the wrong things
or missing edge cases.

**THREE TEST QUALITY DIMENSIONS:**

```
┌──────────────────────────────────────────────────────┐
│ 1. COVERAGE: Does the test execute the code?         │
│    - Line coverage: 100% line coverage != 0 bugs      │
│    - Branch coverage: covers all if/else paths?       │
│    - Path coverage: covers all execution paths?       │
│    Limitation: coverage measures WHAT was executed,   │
│    not WHETHER the test would DETECT a bug.           │
│                                                      │
│ 2. ASSERTION QUALITY: Does the test assert correctly? │
│    @Test                                             │
│    void badTest() {                                  │
│        sort([3,1,2]); // no assertion! passes always │
│    }                                                 │
│    100% coverage, 0% bug detection. Mutation: survives│
│                                                      │
│ 3. INPUT DIVERSITY: Does the test cover edge cases?  │
│    Example-based: manual, limited                    │
│    Property-based: systematic, exhaustive classes    │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE "WRITTEN TEST THAT ALWAYS PASSES" TRAP:**

A developer achieves 100% line coverage with:
```java
@Test void testDeposit() {
    account.deposit(100);
    // No assertion - test always passes
}
```

The test is green. Coverage is 100%. But if `deposit()` is
changed to steal money from the account, the test still
passes. Mutation testing detects this: "we mutated `balance += amount`
to `balance -= amount` and the test still passed - the test is
asserting nothing useful."

**THE LESSON:**

Coverage is a necessary but not sufficient condition for
test quality. The minimum acceptable assertion: check the
OBSERVABLE OUTCOME of the operation (the state change or
the return value), not just that the method was called.
Property-based testing forces assertion specificity: you
must define what PROPERTY must hold, and the framework
finds counterexamples.

---

### 🎯 Mental Model / Analogy

**TDD AS DESIGN TOOL:**

TDD's real value is not "tests first" but "design driven
by usage." Writing the test first forces you to define:
- What is the API? (Method name, parameters, return type)
- How is the result verified? (What does "correct" mean?)
- What are the dependencies? (If the test needs 10 mocks, the design is wrong)

A class that is hard to test is a class with bad design:
too many responsibilities, too many dependencies, too much
global state. TDD makes design problems visible BEFORE the
code is written, when they are cheapest to fix.

**MEMORY HOOK:**

"Example-based = specific input/output. JUnit.
Property-based = for all inputs, invariant holds. jqwik/QuickCheck.
Mutation testing = inject bugs, check tests catch them. PIT.
TDD = Red-Green-Refactor. Tests as design tool.
Pure functions = easiest to test (no mocks, no setup).
Test pyramid = many unit, fewer integration, minimal E2E.
Coverage != quality. Mutation score = test quality."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Testing a calculator: example test = "press 2+3, expect 5."
Property test = "for any two positive numbers, A+B > A."
Mutation test = "secretly change + to -, see if you notice."
TDD = "write the math problem before building the calculator."

**Level 2 - Student:**
```java
// Example-based (JUnit 5):
@Test void shouldSortAscending() {
    int[] result = sort(new int[]{3, 1, 2});
    assertArrayEquals(new int[]{1, 2, 3}, result);
}

// Property-based (jqwik):
@Property void sortedArrayIsOrdered(@ForAll List<Integer> list) {
    List<Integer> sorted = sort(list);
    for (int i = 0; i < sorted.size() - 1; i++) {
        assertTrue(sorted.get(i) <= sorted.get(i+1)); // PROPERTY
    }
}
// jqwik generates 1000 random lists; if any violates the property:
// shrinks to minimal failing case
```

**Level 3 - Professional:**
Test pyramid in Spring Boot:
- Unit: `@ExtendWith(MockitoExtension.class)` + `@Mock` dependencies.
  Fast (~1ms per test). Tests business logic in isolation.
- Integration: `@SpringBootTest` + `@TestContainers` (real DB).
  Slower (~1-10s per test). Tests component wiring.
- E2E: `RestAssured` or `TestRestTemplate` against a running service.
  Slowest (~10s+). Tests happy path from client perspective.

**Level 4 - Senior Engineer:**
Mutation testing with PIT in Maven:
```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>1.15.0</version>
  <configuration>
    <mutators>ALL</mutators>
    <targetClasses>com.example.*</targetClasses>
    <targetTests>com.example.*Test</targetTests>
    <failWhenNoMutations>false</failWhenNoMutations>
  </configuration>
</plugin>
```
Run: `mvn pitest:mutationCoverage`. Report: HTML with
survived/killed mutations per class. Target: >80% mutation score.
Surviving mutations indicate missing assertions or edge cases.

**Level 5 - Expert:**
Formal verification vs testing: Property-based testing finds
bugs for random inputs. Formal verification (Isabelle, Coq,
TLA+) PROVES correctness for ALL inputs. Testing cannot prove
absence of bugs; formal verification can. For safety-critical
systems (medical devices, air traffic control, cryptographic
protocols), formal verification is used where failures are
catastrophic. For most software: property-based testing
plus high-mutation-score coverage is a practical approximation.

---

### ⚙️ How It Works (Formal Basis)

**PROPERTY-BASED TESTING WORKFLOW:**

```
┌──────────────────────────────────────────────────────┐
│ jqwik property test execution:                       │
│                                                      │
│ 1. @Property annotation: "run this 1000 times"       │
│ 2. @ForAll: generate random values per parameter     │
│    - Integers: covers positive, negative, 0, MIN/MAX │
│    - Lists: empty, single, large, with duplicates    │
│    - Strings: empty, unicode, special chars, max len │
│ 3. Execute the test body with each generated input   │
│ 4. If property FAILS:                                │
│    a. Shrink the input to minimal failing case       │
│       (binary search for smallest failing input)     │
│    b. Report: "Property failed for input: []"        │
│       (empty list if that's the minimal case)        │
│ 5. If all 1000 pass: property holds (not proven,     │
│    but high confidence)                              │
│                                                      │
│ SHRINKING: finds the SIMPLEST counterexample.        │
│ Failed on [5,3,1,2,4]? -> try [3,1,2] -> [2,1] ->   │
│ Reports the smallest failing case, not the original. │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Missing Assertion Quality**

```java
// BAD: test with no assertion (always passes, catches nothing)
@Test
void testTransferBad() {
    Account from = new Account(1000);
    Account to = new Account(0);
    from.transfer(to, 500);
    // No assertion - test passes even if transfer is broken
    // Mutation: from.balance += amount (steal) -> test STILL passes
}

// GOOD: assert observable state change
@Test
void testTransferDeductsFromSender() {
    Account from = new Account(1000);
    Account to = new Account(0);
    from.transfer(to, 500);
    assertEquals(500, from.getBalance(),
        "Sender balance should be reduced by transfer amount");
    assertEquals(500, to.getBalance(),
        "Receiver balance should be increased by transfer amount");
}
// Mutations like: balance += instead of -= -> test FAILS (caught)
// Mutations like: balance -= 0 instead of -= amount -> test FAILS

// BEST: property-based test for transfer invariants
@Property
void transferPreservesTotalMoney(
    @ForAll @IntRange(min=0, max=10000) int initialBalance,
    @ForAll @IntRange(min=0, max=10000) int amount
) {
    Assume.that(amount <= initialBalance); // guard: valid transfer
    Account from = new Account(initialBalance);
    Account to = new Account(0);
    from.transfer(to, amount);
    // PROPERTY: money is conserved (total unchanged)
    assertEquals(initialBalance, from.getBalance() + to.getBalance(),
        "Total money must be conserved across transfer");
}
```

**Example 2 - TDD Red-Green-Refactor**

```java
// TDD Cycle for implementing a simple stack:

// --- RED: write failing test first ---
@Test
void pushThenPeekReturnsPushedElement() {
    Stack<Integer> stack = new Stack<>();
    stack.push(42);
    assertEquals(42, stack.peek()); // FAILS: Stack not implemented yet
}

// --- GREEN: minimal code to pass ---
class Stack<T> {
    private T top;
    void push(T item) { this.top = item; }
    T peek() { return top; }  // Minimal: just return top field
}

// --- NEXT RED: add new behavior ---
@Test
void pushTwoElementsPeekReturnsLastPushed() {
    Stack<Integer> stack = new Stack<>();
    stack.push(1);
    stack.push(42);
    assertEquals(42, stack.peek()); // Tests LIFO behavior
}

// --- GREEN again: extend implementation ---
class Stack<T> {
    private LinkedList<T> elements = new LinkedList<>();
    void push(T item) { elements.addFirst(item); }
    T peek() { return elements.getFirst(); }
    T pop() { return elements.removeFirst(); }
}
// TDD drove the design: API is clean because we used it first
```

---

### ⚖️ Comparison Table

| Paradigm | What it tests | Strength | Weakness |
|---|---|---|---|
| Example-based (JUnit) | Specific cases | Precise, readable | Misses edge cases manually |
| Property-based (jqwik) | All inputs, invariants | Finds non-obvious edge cases | Harder to write properties |
| Mutation testing (PIT) | Test suite quality | Measures assertion quality | Slow; needs good baseline |
| TDD | Drives design | API designed for usage | Discipline overhead |
| Contract testing (Pact) | Service API contracts | Prevents integration breaks | Setup overhead |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "100% code coverage means the code is bug-free" | Code coverage measures WHAT was executed, not whether tests ASSERT correctly or cover all INPUT CLASSES. A test that executes every line but asserts nothing achieves 100% coverage with 0% bug detection. Example: `sort(list); // no assertion` = 100% coverage on sort. Mutation testing reveals this gap: mutations survive (bugs not detected). Coverage is a floor, not a ceiling. |
| "TDD slows down development" | TDD's upfront cost (writing tests first) is paid back in: (1) fewer debugging sessions (tests catch regressions immediately), (2) cleaner design (testable code is loosely coupled), (3) confidence during refactoring (green tests = safe to change), (4) documentation (tests describe the intended behavior). The net effect on experienced practitioners: similar or faster total cycle time with fewer defects. On a team new to TDD: initial slowdown, then acceleration as practice improves. |
| "Property-based testing replaces example-based testing" | They are complementary. Example-based tests: specific, readable, document expected behavior for key cases, good for regression (when a specific bug is fixed, write a specific test). Property-based tests: explore input space, find edge cases, verify invariants. Both belong in a test suite. Property tests may find a bug in `sort([-1, 0, 1])` (edge case with negative numbers); you then add a specific example test for that case as a regression test. |
| "Mocking dependencies is always the right approach for unit testing" | Mocking every dependency creates tests tightly coupled to implementation (brittle: break when implementation changes without behavioral change). The alternative: test at a slightly higher level (sociable unit tests) using real collaborators where feasible, mock only external system boundaries (database, HTTP). Mockito for external systems; real in-memory implementations for internal collaborators. The goal: tests that survive refactoring. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Intermittent Test Failures (Flaky Tests)**

**Symptom:** Tests pass most of the time but fail 1-2% of
CI runs. Different tests fail each time. No consistent pattern.

**Root Cause categories:**
1. Time-dependent tests: `assertEquals(LocalDate.now(), result.getDate())` -
   test passes at midnight if now crosses the day boundary during execution.
2. Order-dependent tests: test A modifies shared state, test B
   reads it. Tests pass when A runs first, fail when B runs first.
3. Concurrent tests: shared mutable state between parallel test threads.
4. External dependency: network call in test that sometimes times out.

**Diagnosis:** Run the failing test 100 times: `mvn test -Dtest=FlakyTest`.
Enable test order randomization: JUnit `@TestMethodOrder(Random.class)`.
Enable parallel execution; see if flakiness increases.

**Fix per category:**
1. Mock `Clock` or inject fixed time via `@MockBean`.
2. Reset shared state in `@BeforeEach`. Use `@Isolated` annotation.
3. Use `@ResourceLock` for shared resources.
4. Mock external calls in unit tests; isolate in integration tests with WireMock.

---

**Security Note:**

Testing security properties is not optional for security-sensitive
code. Property-based tests for security:
```java
@Property
void hashFunctionIsOneWay(@ForAll String input) {
    String hash = PasswordHasher.hash(input);
    assertFalse(PasswordHasher.verify(hash, "differentString"),
        "Hash of one string must not verify as another string");
}

@Property
void authorizationNeverGrantsUnprivilegedAccess(
    @ForAll Role role, @ForAll Resource resource) {
    Assume.that(role != Role.ADMIN);
    assertFalse(accessControl.isGranted(role, resource, ADMIN_OPERATION),
        "Non-admin roles must not have admin access to any resource");
}
```
Testing security invariants (authorization, authentication,
data isolation) with property-based tests catches entire
CLASSES of access control bugs, not just the specific cases
the developer thought to test.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - test isolation requires understanding
  object dependencies and mock seams
- `Pure Functions` (CSF-038) - pure functions are trivially
  testable (key design insight for testability)

**Builds On This (learn these next):**
- `Unit Testing` (TST-001) - Java-specific JUnit 5, Mockito,
  AssertJ, test organization
- `Property-Based Testing` (TST-010) - jqwik in depth,
  custom generators, shrinking strategies

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ EXAMPLE-BASED│ JUnit @Test. Specific input/output      │
│              │ Fast to write, may miss edge cases       │
├──────────────┼─────────────────────────────────────────┤
│ PROPERTY     │ jqwik @Property. "for all inputs, X"    │
│              │ Finds edge cases automatically           │
├──────────────┼─────────────────────────────────────────┤
│ MUTATION     │ PIT: inject bugs, verify tests catch them│
│              │ Mutation score = test assertion quality  │
├──────────────┼─────────────────────────────────────────┤
│ TDD          │ Red (fail) -> Green (pass) -> Refactor  │
│              │ Tests as design tool, not afterthought   │
├──────────────┼─────────────────────────────────────────┤
│ PYRAMID      │ Many unit, fewer integration, min E2E   │
│              │ Inverted pyramid = slow, fragile CI      │
├──────────────┼─────────────────────────────────────────┤
│ PURE FN TEST │ No mocks, no setup = trivially testable │
│              │ Design for testability = good design     │
├──────────────┼─────────────────────────────────────────┤
│ COVERAGE     │ Necessary but not sufficient             │
│              │ 100% coverage != 0 bugs                  │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ TST-001 (Unit Testing), TST-010 (PBT)   │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Three complementary test paradigms: example-based (JUnit:
   specific input/output), property-based (jqwik/QuickCheck:
   invariants for all inputs), mutation testing (PIT: did
   the tests actually catch bugs?). Use example tests for
   specific cases and regression; property tests for invariant
   verification and edge-case discovery; mutation testing
   to evaluate test suite quality. All three together.
2. Pure functions are trivially testable (no mocks, no setup,
   no teardown). Design code with a pure core (business logic
   as pure functions) surrounded by an impure shell (side effects
   at the edges: database, HTTP, file). This design is testable,
   correct, and maintainable. The test-driven insight: if
   testing a function requires 5 mocks, the function has
   5 reasons to fail and is doing too much.
3. Coverage is NOT a measure of test quality. A test that
   executes every line but asserts nothing achieves 100%
   coverage with zero bug detection. Add mutation testing
   (PIT) to measure ASSERTION quality: if bugs introduced
   by mutations are not caught by tests, the tests are
   not testing what they claim to test.

**Interview one-liner:**
"Three test paradigms: example-based (JUnit: specific cases),
property-based (jqwik: invariants for all inputs), mutation
testing (PIT: verifies tests catch bugs). Pure functions
are easiest to test (no mocks). TDD = Red-Green-Refactor:
tests drive design. Coverage necessary but not sufficient -
mutation score measures assertion quality."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Testability is a DESIGN PROPERTY, not a testing property.
Code that is hard to test is badly designed (too many
dependencies, shared mutable state, mixed concerns). The
discipline of writing tests first (TDD) or designing for
testability exposes design problems at the cheapest moment
to fix them: before the code is written. A class requiring
10 mocks to test has 10 coupled dependencies; the test reveals
a design violation (Single Responsibility, Dependency Inversion).
Every refactoring that improves testability also improves
design. The correlation is not accidental - they are the same
property viewed from different angles.

**Where else this pattern appears:**

- **Chaos engineering (production testing)** - Property-based
  testing at the production system level. Netflix Chaos Monkey
  injects random failures (kills random instances) and
  verifies the property: "the system remains available for
  users even when individual components fail." This is a
  property test against the production system: "for all
  random subsets of instances that can fail, the system
  should still serve requests." Chaos engineering is
  property-based testing for distributed systems.
- **Fuzzing (security testing)** - Property-based testing
  applied to security. AFL, libFuzzer, Google OSS-Fuzz
  generate random inputs to security-sensitive code (parsers,
  serializers, decoders) and check the property: "no input
  should cause a crash or undefined behavior." Fuzzing
  has found thousands of CVEs in widely used software
  (OpenSSL, libpng, ffmpeg). The property: "must not crash"
  is the most basic correctness property.
- **Contract testing in microservices** - Pact (consumer-driven
  contract testing) is an example-based test paradigm applied
  at service boundaries. Consumer defines expected API behavior
  (specific request/response examples). Provider verifies
  the contract (runs the examples against the actual implementation).
  This is distributed example-based testing: the consumer's
  test is the provider's specification. Property-based
  contract testing: define invariants on the API contract
  ("for any valid product ID, the response must include price
  and currency"), not just specific examples.

---

### 💡 The Surprising Truth

Dijkstra's famous quote: "Program testing can be used to
show the presence of bugs, but never to show their absence."
This is mathematically provable. For any non-trivial program
with infinite input space (any program that accepts strings,
integers, or unbounded input), there exist untested inputs
for which the program may have bugs. No finite test suite
can prove correctness. Yet the industry largely relies on testing
as the primary quality mechanism. This is not ignorance -
it is pragmatism: formal verification (which CAN prove
correctness) requires 10-100x the effort of testing and
is economically viable only for the most critical code
(cryptographic protocols, safety-critical systems).
The engineering compromise: property-based testing dramatically
increases confidence by testing entire equivalence classes
of inputs (not just specific examples). Mutation testing
measures how close the test suite is to "optimal" for
detecting bugs. The combination is the practical approximation
to formal verification that the industry can afford.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[WRITE]** Write a property-based test with jqwik for
   a `palindromeCheck(String)` function. Define at least
   3 properties (e.g., "a reversed palindrome is still a
   palindrome," "any string + its reverse is a palindrome").

2. **[TDD]** Implement a `FizzBuzz` function using TDD.
   Show the Red-Green-Refactor cycle for at least 5 test
   cases. Identify when you start refactoring (when the code
   becomes complex enough to justify).

3. **[MUTATION]** Given a mutation test report showing 3
   surviving mutations (e.g., `>` changed to `>=`, a returned
   value changed from -1 to 0, a conditional inverted), write
   the specific additional test cases that would kill each mutation.

4. **[DESIGN]** Take a method that is hard to test (requires
   5 mocks: database, HTTP client, cache, time service, logger)
   and refactor it into a testable design. How do you reduce
   the mock count? What design principles apply?

5. **[PYRAMID]** Design the test strategy for a Spring Boot
   payment service with: a REST controller, a payment service,
   a database repository, and an external payment gateway call.
   For each layer: unit, integration, E2E. Specify what is
   mocked at each level and why.

---

### 🧠 Think About This Before We Continue

**Q1.** A developer argues: "I don't need property-based tests
because I already have 100% code coverage and my code has
never had a bug in production." Is this a valid argument
against property-based testing?

*Hint: Several issues:
(1) "Never had a bug in production" may mean bugs weren't
    detected, not that they don't exist. Undetected bugs
    are not the same as no bugs.
(2) 100% coverage doesn't mean 100% assertion quality.
    If assertions are weak (don't check important invariants),
    bugs in those invariants will pass the coverage threshold.
(3) Property-based testing's value is finding the UNKNOWN
    edge cases. If the developer already knows what edge
    cases to test (and has example tests for them), coverage
    is high and quality is good. But the developer, by definition,
    doesn't know what they don't know. Property tests find
    the cases the developer didn't think of.
(4) The cost of property-based testing is low: write the
    property once, run 1000+ times automatically. The marginal
    cost after writing the property is near zero.
Valid counter: for extremely simple functions (trivially
correct, no edge cases), property tests add overhead with
low marginal value. For any non-trivial business logic:
property tests find bugs that example tests miss.*

**Q2.** When does TDD NOT work well? What are the conditions
where writing tests first is counterproductive?

*Hint: TDD works poorly when:
(1) Exploratory code: when the design is truly unknown
    (prototype, research, POC), writing tests first forces
    a premature design. The solution: spike first (explore
    without TDD), then delete and rewrite with TDD once
    the design is clearer.
(2) UI/visual testing: writing tests for pixel-perfect
    rendering or UI layout is difficult to specify before
    the UI exists. TDD for visual components is usually
    replaced by component tests after the visual design stabilizes.
(3) Tests require excessive setup: if each test requires
    10 pages of setup (database seeding, environment config,
    mock setup), TDD becomes painful. The correct response:
    fix the DESIGN (not the test approach). Excessive setup
    = bad design. But in legacy codebases where redesign
    is not feasible, TDD may be impractical.
(4) Tests themselves are complex: if the test is harder to
    write and verify than the production code, something is wrong.
    This is usually a sign that the contract is unclear
    (what does "correct" mean?), not that TDD is wrong.
TDD is a skill; practitioners become faster over time.
Initial slowdowns are normal; they decrease with practice.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is property-based testing and how does it differ from example-based testing?"**

*Why they ask:* Tests breadth of testing knowledge. Distinguishes
senior engineers from junior.

*Strong answer includes:*
- Example-based: specific input/output pairs. `assertEquals([1,2,3], sort([3,1,2]))`.
  Manual; the developer chooses the test cases. Limited by
  the developer's imagination for edge cases.
- Property-based: define invariants that hold for ALL valid
  inputs. "For any list, the sorted result has the same
  elements as the original in non-decreasing order."
  Framework (jqwik, QuickCheck) generates random inputs
  and checks the property. Finds edge cases the developer
  didn't think of (empty list, single element, all duplicates,
  MAX_VALUE).
- Shrinking: when a property fails, the framework shrinks
  the input to the minimal failing case. Easier to debug.
- Both are complementary: example tests for specific cases
  and regressions; property tests for invariant verification.

**Q2: "What is mutation testing and why should teams use it?"**

*Why they ask:* Tests knowledge of test quality measurement.

*Strong answer includes:*
- Mutation testing: automatically introduces bugs (mutations)
  into the production code. Runs the test suite. If tests
  FAIL: mutation is "killed" (good - tests caught the bug).
  If tests PASS: mutation "survives" (bad - tests missed the bug).
- Mutation examples: change `>` to `>=`, swap `+` to `-`,
  return `null` instead of a value, remove a conditional.
- Metric: mutation score = killed / total mutations. Target: >80%.
- Why use it: (1) Reveals tests with missing assertions
  (100% coverage, 0% mutation score). (2) Finds edge cases
  not covered by example tests. (3) Quantifies test suite
  quality objectively.
- Java tool: PIT (pitest.org). Maven plugin.
- Limitation: slow (must re-run test suite for each mutation).
  Incremental mode: only mutate changed code.

**Q3: "Describe the TDD Red-Green-Refactor cycle."**

*Why they ask:* Tests process knowledge. Common at companies
with engineering excellence culture.

*Strong answer includes:*
- Red: write a FAILING test for the next small unit of
  behavior. The test fails because the production code doesn't
  exist yet (or the feature isn't implemented). Run the test:
  see it fail (verify the failure is for the expected reason,
  not a test bug).
- Green: write the MINIMAL production code to make the test
  pass. Do not over-engineer. The goal is green, not elegant.
  A simple if-statement returning a hardcoded value is
  acceptable at this stage if it makes the test pass.
- Refactor: improve the code (remove duplication, clarify
  names, apply patterns) WITHOUT changing behavior. Run all
  tests to ensure they are still green. Refactoring is safe
  because the tests guard against behavioral change.
- Repeat: add the next test (Red) for the next behavior unit.
- Why it works: design is driven by usage (the test IS the
  first client of the code). Dependencies are designed for
  testability (hard-to-test code = bad design, caught early).
  Refactoring is safe (green tests = behavioral contract maintained).
