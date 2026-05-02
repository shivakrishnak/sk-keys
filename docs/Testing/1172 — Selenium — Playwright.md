---
layout: default
title: "Selenium / Playwright"
parent: "Testing"
nav_order: 1172
permalink: /testing/selenium-playwright/
number: "1172"
category: Testing
difficulty: ★★☆
depends_on: E2E Test, Test Environments, HTML, JavaScript
used_by: QA Engineers, Frontend Developers
related: E2E Test, Flaky Tests, Golden Path Testing, API Testing, Cypress
tags:
  - testing
  - selenium
  - playwright
  - e2e
  - browser-automation
---

# 1172 — Selenium / Playwright

⚡ TL;DR — Selenium and Playwright are browser automation frameworks for end-to-end UI testing — they control a real browser programmatically to simulate user interactions and verify application behavior from the user's perspective.

| #1172           | Category: Testing                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | E2E Test, Test Environments, HTML, JavaScript                    |                 |
| **Used by:**    | QA Engineers, Frontend Developers                                |                 |
| **Related:**    | E2E Test, Flaky Tests, Golden Path Testing, API Testing, Cypress |                 |

---

### 🔥 The Problem This Solves

"WORKS FOR ME" (IN THE BROWSER):
Unit and API tests verify logic and API behavior. But a React rendering bug, a CSS layout issue, or a JavaScript error that prevents form submission won't be caught by API tests. Browser automation tests verify the actual user experience in a real browser — clicking buttons, filling forms, navigating pages.

SELENIUM'S LEGACY PROBLEMS:
Selenium WebDriver (2004) was the industry standard for 20 years. It works but has significant pain points: verbose API, poor async support, flaky due to implicit waits, no built-in test assertions. Playwright (2020, Microsoft) addresses all of these: auto-wait (no manual waits), built-in assertions, multi-browser support, faster, and first-class TypeScript support.

---

### 📘 Textbook Definition

**Selenium WebDriver** is an open-source browser automation API that provides a programming interface to control web browsers (Chrome, Firefox, Safari, Edge). The WebDriver protocol sends commands to a browser driver (ChromeDriver, GeckoDriver) which translates them to browser-native commands. **Playwright** is a modern browser automation library by Microsoft that provides: a single API for Chromium, Firefox, and WebKit; auto-waiting (no explicit sleeps); network interception; test isolation via browser contexts; and a test runner with built-in assertions and retries. Both are used for **E2E (end-to-end) testing** — testing the full application stack through the browser UI.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Browser automation = programmatically control a browser to simulate user behavior and verify the UI.

**One analogy:**

> Selenium/Playwright is a **robot typing at a keyboard and clicking a mouse** through your application — exactly like a user would. The difference: the robot never forgets a step, runs at 3am, and reports exactly what went wrong when a step fails.

---

### 🔩 First Principles Explanation

SELENIUM WEBDRIVER ARCHITECTURE:

```
Test Code (Java/Python/JS)
    ↓  WebDriver API
  ChromeDriver (WebDriver protocol)
    ↓  DevTools Protocol / W3C WebDriver
  Chrome Browser (real)
    ↓
  Application Under Test

SELENIUM EXAMPLE (Java):
WebDriver driver = new ChromeDriver();
driver.get("https://app.example.com/login");

// Find element → type → click
driver.findElement(By.id("email")).sendKeys("user@example.com");
driver.findElement(By.id("password")).sendKeys("password123");
driver.findElement(By.cssSelector("button[type='submit']")).click();

// Wait for page load
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.urlContains("/dashboard"));

// Assert
assertThat(driver.getTitle()).contains("Dashboard");
driver.quit();
```

PLAYWRIGHT ARCHITECTURE:

```
Test Code (TypeScript/Python/Java/.NET)
    ↓  Playwright API
  Playwright Server (Node.js)
    ↓  CDP (Chrome DevTools Protocol) / Protocol
  Browser (Chromium/Firefox/WebKit)
    ↓
  Application Under Test

KEY IMPROVEMENTS OVER SELENIUM:
  1. Auto-wait: ALL actions wait for element to be actionable before proceeding
     → No explicit waits needed for most cases
     → page.click("#submit") automatically waits for button to be visible + enabled

  2. Built-in assertions with auto-retry:
     await expect(page.locator("#result")).toHaveText("Success");
     // Auto-retries until text appears (up to timeout)
     // NOT a point-in-time assertion that fails if element not yet rendered

  3. Browser contexts = isolated browsing sessions:
     const context = await browser.newContext();  // fresh cookies, storage
     const page = await context.newPage();
     // Multiple independent sessions in one browser instance

  4. Network interception:
     await page.route("**/api/products", route => {
         route.fulfill({ json: [{ id: 1, name: "Test Product" }] });
     });
     // Mock API responses without a real backend

  5. Trace viewer:
     playwright show-trace trace.zip
     // Step-by-step screenshots, network requests, console logs
     // Invaluable for debugging CI failures
```

LOCATOR STRATEGIES — BEST PRACTICES:

```
WORST (fragile):
  By.xpath("//div[@class='container']/div[2]/button[1]")
  // Breaks if any parent structure changes

BAD:
  By.cssSelector(".submit-btn")  // CSS class can change

BETTER:
  By.id("submit-order")  // IDs are stable

BEST (Playwright):
  page.getByRole("button", { name: "Submit Order" })    // ARIA role + text
  page.getByTestId("submit-order")                       // data-testid attribute
  page.getByLabel("Email address")                       // Label → input association

RATIONALE:
  data-testid="submit-order" attributes are explicitly for testing
  → Developers don't change them for styling/refactoring
  → QA team can request test IDs from developers
  → Most resilient to UI changes
```

---

### 🧪 Thought Experiment

SELENIUM vs PLAYWRIGHT FLAKINESS COMPARISON:

```
Selenium test:
  driver.findElement(By.id("result")).getText()  // → often fails: element not loaded

  "Fix": Thread.sleep(2000);  // → brittle, slow, still occasionally fails

  Better: WebDriverWait.until(textToBePresentInElement(...))  // verbose

Playwright test:
  const result = page.locator("#result");
  await expect(result).toHaveText("Order confirmed");
  // Playwright automatically polls until text appears (up to 5s default)
  // No sleep, no explicit wait, no flakiness

RESULT:
  Same test scenario.
  Selenium version: 20 lines, flaky 5% of the time, verbose.
  Playwright version: 3 lines, rock-solid, readable.

This is the core reason the industry has largely shifted to Playwright (2024).
```

---

### 🧠 Mental Model / Analogy

> Selenium is an older **command-and-response protocol**: you say "click button", the driver clicks it, you immediately check the result. If the page wasn't ready, you fail. Playwright is a **contract-based protocol**: you say "click the button and wait until something actionable happens", Playwright handles all the timing internally. You describe intent; Playwright handles the mechanics.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Playwright opens a browser, navigates to a URL, clicks elements, types text, and asserts what's visible. `page.goto()` → `page.click()` → `page.fill()` → `expect(locator).toHaveText()`. Auto-wait means no `Thread.sleep()`.

**Level 2:** Locators: prefer `getByRole`, `getByTestId`, `getByLabel` over CSS selectors (resilient to UI changes). Assertions: `expect(locator).toBeVisible()`, `.toHaveText()`, `.toHaveValue()` — all auto-retry. Test isolation: each test gets a fresh browser context (cookies/storage cleared). `playwright.config.ts` configures browsers, timeouts, base URL.

**Level 3:** Page Object Model (POM): encapsulate page interactions in a class (e.g., `LoginPage.fillCredentials()`, `LoginPage.submit()`). Test code uses the Page Object; page details are abstracted. Network interception: `page.route()` mocks API calls — tests run without backend, or test specific API response scenarios. Trace viewer: `--trace on` in CI; download and open `trace.zip` to see every step, screenshot, and network call that led to a failure.

**Level 4:** Playwright at scale: parallel test execution across browsers (`--workers=4`). Sharding (`--shard=1/4`) for CI distribution. Component testing (Playwright for components — experimental): test React/Vue components in isolation without full E2E overhead. Playwright Test's fixtures system: define `page`, `context`, `browser` fixtures with custom setup — e.g., a `authenticatedPage` fixture that logs in before each test, making test code clean. Screenshots on failure, video recording, accessibility testing with `page.accessibility.snapshot()`.

---

### 💻 Code Example

```typescript
// playwright.config.ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
  ],
});
```

```typescript
// tests/checkout.spec.ts
import { test, expect } from "@playwright/test";

// Page Object
class CheckoutPage {
  constructor(private page: Page) {}

  async addProductToCart(productName: string) {
    await this.page.getByRole("heading", { name: productName }).click();
    await this.page.getByRole("button", { name: "Add to cart" }).click();
    await expect(this.page.getByTestId("cart-count")).toHaveText("1");
  }

  async proceedToCheckout() {
    await this.page.getByRole("link", { name: "Cart" }).click();
    await this.page
      .getByRole("button", { name: "Proceed to Checkout" })
      .click();
  }
}

test("user can add product and checkout", async ({ page }) => {
  const checkout = new CheckoutPage(page);

  await page.goto("/products");
  await checkout.addProductToCart("Laptop Stand");
  await checkout.proceedToCheckout();

  await expect(page).toHaveURL(/\/checkout/);
  await expect(page.getByTestId("order-summary")).toBeVisible();
  await expect(page.getByTestId("total-price")).toHaveText(/\$\d+\.\d{2}/);
});

// Mock API for isolated UI testing
test("checkout shows error when payment fails", async ({ page }) => {
  await page.route("**/api/orders", (route) => {
    route.fulfill({ status: 402, json: { error: "Payment declined" } });
  });

  await page.goto("/checkout");
  await page.getByRole("button", { name: "Place Order" }).click();

  await expect(page.getByRole("alert")).toContainText("Payment declined");
});
```

---

### ⚖️ Comparison Table

|                   | Selenium | Playwright                         | Cypress                |
| ----------------- | -------- | ---------------------------------- | ---------------------- |
| Age               | 2004     | 2020                               | 2017                   |
| Language support  | Many     | TypeScript, JS, Python, Java, .NET | JavaScript/TypeScript  |
| Auto-wait         | Manual   | Built-in                           | Built-in               |
| Cross-browser     | Yes      | Yes (Chromium, Firefox, WebKit)    | Chromium only (mainly) |
| Network intercept | Limited  | Full                               | Full                   |
| Speed             | Slower   | Fast                               | Fast                   |
| Flakiness         | Higher   | Lower                              | Lower                  |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                     |
| ----------------------------------------- | ------------------------------------------------------------------------------------------- |
| "E2E tests should cover everything"       | E2E tests are slow and costly; use sparingly for golden paths; test logic in unit/API tests |
| "Selenium is dead"                        | Selenium is still widely used; Playwright is the modern choice for new projects             |
| "Browser automation replaces API testing" | Browser tests verify UI behavior; API tests verify service behavior — both are needed       |

---

### 🚨 Failure Modes & Diagnosis

**1. Selector Brittleness (Breaks After UI Refactor)**
Cause: Tests use CSS classes or XPath tied to implementation structure.
**Fix:** Use `data-testid` attributes; use ARIA roles (`getByRole`). Agree with dev team: test IDs are stable contracts.

**2. Flaky Tests Due to Animation/Transition**
Cause: Click fires while element is animating; click lands on wrong element or is lost.
**Fix:** Playwright handles most cases with auto-wait. For custom animations: `locator.waitFor({ state: 'stable' })` or disable animations in test config.

**3. Tests Pass Locally, Fail in CI (Headless vs. Headed)**
Cause: Headless browser has different viewport, font rendering, or missing environment variables.
**Fix:** Match CI environment locally: `playwright test --headed=false`. Use Playwright's Docker image in CI for consistency.

---

### 🔗 Related Keywords

- **Prerequisites:** E2E Test, Test Environments, HTML, JavaScript
- **Related:** Selenium WebDriver, Playwright, Cypress, Page Object Model, Test Fixtures, Flaky Tests, Golden Path Testing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Control real browsers to test UI behavior │
├──────────────┼───────────────────────────────────────────┤
│ SELENIUM     │ Mature, verbose, manual waits; wide       │
│              │ language support                         │
├──────────────┼───────────────────────────────────────────┤
│ PLAYWRIGHT   │ Modern, auto-wait, trace viewer,         │
│              │ network interception; prefer for new work │
├──────────────┼───────────────────────────────────────────┤
│ BEST         │ getByRole / getByTestId over CSS/XPath;  │
│ PRACTICE     │ Page Object Model; trace on CI failure   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Browser tests = the user's perspective; │
│              │  Playwright auto-waits make them stable" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Playwright's auto-wait mechanism is the core innovation over Selenium. Describe the internal mechanism: (1) when `page.click(locator)` is called, Playwright runs a series of "actionability checks" — element is attached to DOM, visible, stable (not animating), enabled, and not obscured — before clicking, (2) the default timeout (5 seconds) and how to configure it globally vs. per-action, (3) `expect(locator).toHaveText()` vs. `locator.textContent()` — the first auto-retries until the condition is met; the second is a point-in-time read that returns immediately (use for assertion; avoid for value extraction before it's ready), (4) `waitForSelector` vs. `locator.waitFor()` (old API vs. new locator-based API), and (5) race conditions that auto-wait DOESN'T prevent — for example, clicking a button that triggers an async operation and then immediately asserting on the result (the result might not be rendered yet); the fix: assert on a visible element that only appears when the async operation completes.

**Q2.** The Page Object Model (POM) is the standard architectural pattern for Playwright/Selenium test suites. Describe: (1) the core principle — encapsulate all page interactions in a class so test code reads like business intent, not technical implementation (`loginPage.loginAs("alice", "pass")` vs `page.fill('#email', 'alice')`), (2) the trade-off between thin Page Objects (locators only) and fat Page Objects (full workflows), and why thin is preferred (workflow logic belongs in tests, not Page Objects), (3) Page Object composition — a `CheckoutPage` that composes `CartSummary`, `ShippingForm`, `PaymentForm` sub-components, (4) the App Actions pattern (alternative to POM) — using API calls to set up state instead of UI navigation (bypass the login UI by calling the auth API directly), making tests faster and more focused, and (5) fixture-based injection in Playwright — defining `test.extend()` with a `loginPage` fixture that auto-navigates and provides the page object, keeping test setup DRY.
