---
layout: default
title: "Approval Testing"
parent: "Testing"
nav_order: 1164
permalink: /testing/approval-testing/
number: "1164"
category: Testing
difficulty: ★★★
depends_on: Snapshot Testing, Unit Test, Test Data Management
used_by: Developers, QA
related: Snapshot Testing, Golden Path Testing, Regression Test, ApprovalTests
tags:
  - testing
  - approval-testing
  - snapshot
  - regression
---

# 1164 — Approval Testing

⚡ TL;DR — Approval testing captures the output of code (a "received" file), compares it to a previously approved "golden master", and fails if they differ — letting humans approve new outputs rather than manually writing assertions.

| #1164           | Category: Testing                                                     | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Snapshot Testing, Unit Test, Test Data Management                     |                 |
| **Used by:**    | Developers, QA                                                        |                 |
| **Related:**    | Snapshot Testing, Golden Path Testing, Regression Test, ApprovalTests |                 |

---

### 🔥 The Problem This Solves

THE ASSERTION MAINTENANCE BURDEN:
Some code produces complex output — a full HTML report, a JSON document with 50 fields, a serialized domain object with nested structures. Writing explicit `assertEquals` for every field is tedious and brittle. Any legitimate change to the output requires updating dozens of assertions. The alternative — only asserting on a few fields — gives incomplete coverage.

LEGACY SYSTEM TESTING (CHARACTERIZATION):
You inherit 10,000 lines of untested legacy code. You don't know what it's supposed to do — only what it currently does. Approval tests let you capture the current behavior as the "approved" baseline, giving you a regression safety net before refactoring.

---

### 📘 Textbook Definition

**Approval testing** (also called "golden master testing" or "characterization testing") is a testing technique where: (1) the test runs the system under test and captures its output (the "received" artifact — text, HTML, JSON, image); (2) the output is compared to a pre-approved "approved" artifact stored as a file; (3) if they match → test passes; if they differ → test fails, showing a diff; (4) a human reviews the diff and either: fixes the code (if the change is a bug) or "approves" the new output (updates the approved file, if the change is intentional). Approval tests replace manual assertion writing with a human-approval workflow for output changes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Approval testing = capture output as "golden file"; if output changes, diff is shown for human approval.

**One analogy:**

> Approval testing is like a **visual diff for documents**: a lawyer approves a contract template once. Every time the template-generating code runs, the output is shown to the lawyer as a redline (tracked changes). The lawyer approves or rejects the changes. No need to manually check every clause — just review the diff.

---

### 🔩 First Principles Explanation

APPROVAL TEST WORKFLOW:

```
FIRST RUN (no approved file exists):
  1. Test runs → generates output (received file)
  2. No approved file → test FAILS
  3. Diff tool opens: shows "received" side, "approved" side is empty
  4. Human reviews received output: "Yes, this is correct"
  5. Approve: copy received → approved file
  6. Test runs again → passes

SUBSEQUENT RUNS (approved file exists):
  If code output unchanged → received == approved → PASS

  If code output changed:
    CASE A (bug): received ≠ approved
      Test FAILS → diff shows what changed → dev fixes bug

    CASE B (intentional change): received ≠ approved
      Test FAILS → human reviews diff → approves: updates approved file
      Approved file updated → test passes

FILE STORAGE:
  approved files → committed in git alongside test code
  received files → generated at test time, ignored by .gitignore

  Git diff of approved file = intentional behavior change
  (same as snapshot testing)
```

TOOLS AND FORMATS:

```
JAVA: ApprovalTests library
  Approvals.verify(myObject);
  Approvals.verifyAsJson(myObject);
  Approvals.verifyHtml(htmlString);

  Files generated:
    src/test/java/.../MyTest.myMethod.approved.txt
    src/test/java/.../MyTest.myMethod.received.txt

JAVASCRIPT: Jest snapshots (similar concept)
  expect(output).toMatchSnapshot()

PYTHON: pytest-regtest, syrupy
  def test_output(snapshot):
      assert snapshot == generate_report()

DIFF TOOL INTEGRATION:
  ApprovalTests integrates with: DiffMerge, Beyond Compare, Araxis, IntelliJ Diff
  On CI: CI reporter shows textual diff in build output
```

---

### 🧪 Thought Experiment

CHARACTERIZATION TEST FOR LEGACY CODE:

```
Legacy method: calculateTax(invoice)
  → 500 lines, no tests, you don't fully understand it
  → You need to refactor it but can't break it

Step 1: Write approval test capturing current behavior:
  @Test void taxCalculation() {
    Invoice invoice = buildComplexTestInvoice();
    BigDecimal tax = legacyCalculator.calculateTax(invoice);
    Approvals.verify("tax=" + tax);
    // First run: FAIL, generates received file with tax=127.50
    // Approve → approved file: "tax=127.50"
  }

Step 2: Refactor legacyCalculator
  → Run test → if tax is still 127.50 → test passes → safe to continue
  → If test fails → diff shows: "tax=127.50" vs "tax=130.00" → introduced a bug

Step 3: Once refactoring is complete, write proper unit tests
  → Approval test becomes a backstop regression test
```

---

### 🧠 Mental Model / Analogy

> Approval testing is **change control for code output**: software has a "baseline" (approved file in git). Any change to the output is a "change request" (diff shown on test failure). A human authorizes (approves) or rejects the change. The baseline tracks the system's intended behavior over time, making every output change explicit and intentional.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Capture output once, compare against it forever. Humans review diffs and approve intended changes. Perfect for complex output where writing assertions is impractical.

**Level 2:** ApprovalTests library: `Approvals.verify(output)` generates `.approved.txt` and `.received.txt` files. On failure, diff tool opens automatically. Approved files are committed to git. `.gitignore` the `.received.txt` files.

**Level 3:** Best for: complex output (HTML, JSON, reports), legacy code characterization, and visual regression (screenshot approval). Workflow: write the test → first run fails → review output → approve if correct → future changes require explicit re-approval. The key discipline: never auto-approve without reviewing the diff.

**Level 4:** Approval testing at scale: combinatorial testing with approval tests. Instead of 50 individual assertions for a report generator, create one approval test with a representative complex input — the entire report becomes the assertion. Multi-approval: different approved files per operating system (date/time formatting differences), per locale. Integration: approval test results in CI show full diff in pull request — reviewer sees exactly what output changed, enabling code review of behavior changes alongside code changes.

---

### 💻 Code Example

```java
// ApprovalTests (Java) example
import org.approvaltests.Approvals;
import com.spun.util.io.FileUtils;

class InvoiceReportTest {

    @Test
    void invoiceReport_complexFormat() {
        Invoice invoice = Invoice.builder()
            .customer("Acme Corp")
            .item("Widget", 10, 9.99)
            .item("Gadget", 2, 49.99)
            .discount(0.10)
            .build();

        String report = reportGenerator.generate(invoice);

        Approvals.verify(report);
        // First run: creates InvoiceReportTest.invoiceReport_complexFormat.received.txt
        // After approval: InvoiceReportTest.invoiceReport_complexFormat.approved.txt
        // Future runs: compare received vs approved
    }

    @Test
    void invoiceReport_asJson() {
        Invoice invoice = buildTestInvoice();
        Approvals.verifyAsJson(invoice);
        // Serializes invoice to JSON, approves the full JSON structure
    }
}
```

```
// Approved file (committed in git):
// InvoiceReportTest.invoiceReport_complexFormat.approved.txt
INVOICE
Customer: Acme Corp
--------------
Widget         x10    $99.90
Gadget         x2     $99.98
--------------
Subtotal:             $199.88
Discount (10%):       -$19.99
TOTAL:                $179.89
```

---

### ⚖️ Comparison Table

|                             | Assertion-based Test | Approval Test          | Snapshot Test (Jest)   |
| --------------------------- | -------------------- | ---------------------- | ---------------------- |
| Assertion authoring         | Manual, explicit     | None (auto-capture)    | None (auto-capture)    |
| Handles complex output      | Poor (many asserts)  | Excellent              | Excellent              |
| Human review of changes     | Not inherent         | Required (by design)   | Optional               |
| Git diff on behavior change | No                   | Yes (approved file)    | Yes (snapshot file)    |
| Best for                    | Simple values        | Complex output, legacy | React component output |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                        |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| "Approval tests are the same as snapshot tests" | Conceptually similar; approval tests emphasize the human review step; snapshot tests (Jest) are more automated |
| "Auto-approving CI failures is fine"            | Auto-approving defeats the purpose — the human review of diffs IS the test value                               |
| "Approval tests replace all assertions"         | Not for simple values — they're most valuable for complex, multi-field output                                  |

---

### 🚨 Failure Modes & Diagnosis

**1. Approved Files Not Committed**
Cause: Developer forgot to commit `.approved.txt` files after first approval.
Result: CI always fails (no approved file to compare against).
Fix: Add check: if `.approved.txt` is missing, fail with clear "approve this test first" message. Lint: `git ls-files --others --exclude-standard | grep '.received.'` should be empty.

**2. Auto-Approving Without Review**
Cause: Developer runs `approvals.approve_all()` without reading the diff.
Result: Bugs captured as "approved" baseline.
Fix: Approval workflow in code review — PR reviewer sees the `.approved.txt` diff in the PR.

---

### 🔗 Related Keywords

- **Prerequisites:** Snapshot Testing, Unit Test, Test Data Management
- **Related:** Characterization Testing, Golden Master Testing, ApprovalTests, Jest Snapshots, Regression Test

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Capture output → compare to approved     │
│              │ golden file → human approves changes     │
├──────────────┼───────────────────────────────────────────┤
│ BEST FOR     │ Complex output, legacy code, reports     │
├──────────────┼───────────────────────────────────────────┤
│ LIBRARY      │ ApprovalTests (Java), Jest snapshots (JS)│
├──────────────┼───────────────────────────────────────────┤
│ WORKFLOW     │ Test fails → show diff → human approves  │
│              │ or rejects the change                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Human-approved assertions — review diffs│
│              │  rather than write dozens of assertEquals"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Characterization testing (a form of approval testing) is used to establish a regression baseline for legacy code before refactoring. Describe the full workflow: (1) selecting test inputs that exercise representative code paths (without understanding the code, use code coverage to detect untested paths), (2) the "if it runs, it's the right answer" assumption (you're testing what the code DOES, not what it SHOULD do), (3) the risk: what if the existing behavior contains bugs? (the tests will "approve" buggy behavior — document known bugs separately), and (4) how approval tests transition: initially serving as characterization tests, then replaced with intention-revealing unit tests as the legacy code is understood and refactored. What is the exit strategy for approval tests?

**Q2.** Approval testing for HTML/PDF reports creates challenges around non-deterministic content (timestamps, generated IDs, whitespace). Describe: (1) pre-processing strategies before comparison (scrub timestamps, normalize whitespace, replace UUIDs with fixed values), (2) how to compare visual output — HTML rendering differences vs. structural differences (semantic HTML comparison, ignoring whitespace-only changes), (3) the file storage strategy for approval tests — if a test generates a 2MB HTML report, storing it in git causes repository bloat; alternatives include git LFS, external artifact storage, or hash-based comparison (only store a hash of the approved output), and (4) how image approval tests work (screenshot testing tools like Percy, Chromatic for Storybook) — pixel-by-pixel vs. perceptual diff algorithms (to handle antialiasing differences between platforms).
