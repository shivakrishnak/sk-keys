---
layout: default
title: "Cypress (E2E Testing)"
parent: "Testing"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /testing/cypress-e2e/
id: TST-054
category: Testing
difficulty: ★★☆
depends_on: JavaScript, E2E Testing, Testing
used_by: CI-CD, Testing
related: Playwright (E2E Testing), Selenium, Testing Library
tags:
  - testing
  - javascript
  - frontend
  - intermediate
---

# TST-054 - Cypress (E2E Testing)

⚡ **TL;DR -** A JavaScript-native E2E testing framework that runs inside the browser, enabling reliable command queuing, automatic retry, and real-time network interception.

| Field      | Value                                               |
|------------|-----------------------------------------------------|
| Depends on | JavaScript, E2E Testing, Testing                    |
| Used by    | CI-CD, Testing                                      |
| Related    | Playwright (E2E Testing), Selenium, Testing Library |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Selenium tests drive a browser over WebDriver: each command crosses a network boundary (test process → WebDriver server → browser). Timing is unpredictable. Tests add `sleep(2000)` to wait for animations. Flaky failures dominate CI. Debugging requires reading logs from three processes simultaneously.

**THE BREAKING POINT:** An e-commerce checkout flow has 12 UI interactions. The Selenium test takes 45 seconds and fails 20% of the time in CI due to race conditions between the test runner and the browser. The team disables the test rather than fix it - and a regression ships.

**THE INVENTION MOMENT:** Cypress (2014, Gleb Bahmutov and team) moved the test runner *inside* the browser process. Commands run in the same JavaScript event loop as the application. There is no WebDriver boundary, no timing guesswork. The framework natively understands async DOM events, network requests, and React/Vue/Angular lifecycle hooks.

---

### 📘 Textbook Definition

**Cypress** is an end-to-end (and component) testing framework for web applications that executes test code inside a browser via a Node.js process and a proxy layer. Commands are queued as a **command chain** - each command enqueues an action that Cypress retries until a timeout or success, implementing **retry-ability** automatically. `cy.intercept()` intercepts and stubs network requests at the browser proxy level. Component Testing mode mounts individual components in isolation. Tests are written in JavaScript/TypeScript using a Mocha-like `describe/it` structure with Chai assertions.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Cypress tests run inside the browser - no WebDriver gap, no manual waits.

> Selenium is a remote-control car with a radio transmitter: commands travel through the air and arrive with unpredictable lag. Cypress is a driver *inside* the car - instant, direct, and able to read the dashboard in real time.

**One insight:** Retry-ability is the superpower. `cy.get('.btn')` automatically retries until the element exists, is visible, and is not disabled - eliminating 90% of `sleep` calls.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Test flakiness is caused by timing assumptions; removing timing assumptions eliminates flakiness.
2. The test runner and the application share the same environment - they can observe the same events.
3. Network calls are a first-class test concern, not an implementation detail to hide.

**DERIVED DESIGN:** Run the test runner inside the browser's JavaScript engine. Queue commands as a linked list of retryable actions. Intercept HTTP at the proxy level before requests leave the browser. Provide a time-travel debugger by snapshotting DOM state after every command.

**THE TRADE-OFFS:**
- **Gain:** Near-zero flakiness for UI interactions; real-time network interception; built-in time-travel debugger; automatic screenshots and video on failure.
- **Cost:** Tests run inside a single browser tab - multi-tab, multi-origin, and native mobile scenarios are not natively supported; JavaScript-only (no Java/Python); historically single-browser at a time per process (parallel requires Cypress Cloud or multiple processes).

---

### 🧪 Thought Experiment

**SETUP:** You need to test a login form that fetches user permissions from an API after successful authentication, then redirects based on role.

**WHAT HAPPENS WITHOUT Cypress:** Your Selenium test clicks login, then `Thread.sleep(3000)`, then `findElement(By.id("dashboard"))`. If the API is slow, the test times out. If the API is fast, 3 seconds are wasted. The test is both flaky and slow.

**WHAT HAPPENS WITH Cypress:**
```javascript
cy.intercept('POST', '/api/permissions').as('perms');
cy.get('#username').type('admin');
cy.get('#password').type('secret');
cy.get('#login-btn').click();
cy.wait('@perms'); // waits exactly as long as needed
cy.url().should('include', '/admin-dashboard');
```
Cypress waits precisely until the `POST /api/permissions` response is received, then asserts the URL. Zero arbitrary waits. Exact timing.

**THE INSIGHT:** By intercepting the network call and waiting on its alias, the test is self-documenting about what it depends on, and self-timing. The test communicates its protocol dependency explicitly.

---

### 🧠 Mental Model / Analogy

> Cypress is like a stage manager running a live theatre production from backstage. They can cue actors (click buttons), listen to the intercom (observe network calls), pause for a prop to arrive (wait for API), and call "cut" if anything goes wrong - all from inside the production, not from the audience.

- **Stage manager** → Cypress test runner (inside browser)
- **Actor cues** → `cy.click()`, `cy.type()`, `cy.get()` commands
- **Intercom** → `cy.intercept()` network observation
- **Prop arrival** → `cy.wait('@alias')`
- **Production log** → Cypress command log / time-travel debugger

Where this analogy breaks down: a stage manager can cross between scenes freely; Cypress cannot cross browser origins in the same test without `cy.origin()` (and even then, with constraints).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Cypress opens a browser, clicks your app's buttons, fills in forms, and checks that the right things appear on screen - automatically. It takes screenshots when something goes wrong.

**Level 2 - How to use it (junior developer):**
Install with `npm install cypress --save-dev`. Open with `npx cypress open`. Write tests in `cypress/e2e/*.cy.js`. Use `cy.visit('/login')`, `cy.get('[data-cy="email"]').type('a@b.com')`, `cy.get('button[type="submit"]').click()`, `cy.contains('Welcome')`. Run headlessly in CI with `npx cypress run`.

**Level 3 - How it works (mid-level engineer):**
Cypress runs two JavaScript runtimes: the **test runner** (Node.js, accesses the filesystem and `cy.*` APIs) and the **AUT frame** (browser, hosts the application). Commands are not executed immediately - each `cy.*` call enqueues a `Command` object into a linked list managed by `cy.queue`. The queue executes serially; each command has a default `timeout` and a `retry` strategy. The **proxy layer** (`@cypress/proxy`) intercepts browser HTTP traffic, enabling `cy.intercept()` to match, modify, and stub responses. Test results flow back to Node.js via `postMessage`.

**Level 4 - Why it was designed this way (senior/staff):**
WebDriver's synchronous remote control model serialises commands over HTTP, introducing network latency that is unpredictable in CI containers. By running the test runner inside the browser's event loop, Cypress eliminates the IPC boundary for DOM assertions entirely. The command queue model (rather than `async/await`) was a deliberate choice: asynchrony is hidden from test authors, preventing the common mistake of writing synchronous assertions against asynchronous state. The proxy architecture was necessary because browsers do not expose a native API for intercepting `fetch`/`XHR` at the network level from within a same-origin frame - the proxy is the only reliable interception point.

---

### ⚙️ How It Works (Mechanism)

```
Node.js Process (Cypress runner)
  │  serves test files + proxy
  │
  ├── @cypress/proxy (HTTP intercept layer)
  │     cy.intercept() rules → match/stub/spy
  │
  └── Browser (Chrome/Firefox/Edge)
        ├── AUT Frame (your app)
        │     React/Vue/HTML DOM
        └── Cypress Frame (test runner)
              cy.queue (Command linked list)
              │
              Command 1: cy.visit()  → execute
              Command 2: cy.get()    → retry until exists
              Command 3: cy.click()  → execute
              Command 4: cy.should() → retry until passes
              │
              postMessage → Node.js results
              │
           Screenshots / Video / JUnit XML
```

**Retry-ability matrix:**

| Command type    | Retried?  | Until condition                     |
|-----------------|:---------:|-------------------------------------|
| `cy.get()`      | Yes       | Element found + actionable          |
| `.should()`     | Yes       | Assertion passes or timeout         |
| `cy.click()`    | No        | Executes once (get() retries first) |
| `cy.intercept()`| N/A       | Registered before request fires     |
| `cy.wait()`     | No        | Waits once for alias response       |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
 cypress/e2e/login.cy.js
 ┌──────────────────────────────────────────┐
 │  cy.visit('/login')                      │
 │  cy.intercept('POST','/api/auth')        │
 │    .as('loginRequest')                   │
 │  cy.get('[data-cy=email]').type('a@b')   │
 │  cy.get('[data-cy=submit]').click()  ← YOU ARE HERE
 │  cy.wait('@loginRequest')                │
 │  cy.url().should('include','/dashboard') │
 └───────────────┬──────────────────────────┘
                 │ cy.queue executes serially
                 ▼
         proxy intercepts POST /api/auth
         ├── real network (integration mode)
         └── stubbed response (cy.intercept stub)
                 │
         browser navigates to /dashboard
                 │
         cy.url() assertion retries until passes
                 │
         PASS + screenshot + video artefacts
```

**FAILURE PATH:** An assertion times out → Cypress captures a screenshot, records the failure step in the command log, runs `afterEach`/`after` hooks, and continues to the next test. The test run does not abort unless `bail` is configured.

**WHAT CHANGES AT SCALE:** Parallel runs require either Cypress Cloud (cloud orchestration) or splitting spec files manually across CI matrix jobs (`--spec "cypress/e2e/checkout*"`). Each parallel runner is a fully independent browser process - no shared state between runners.

---

### 💻 Code Example

**BAD - arbitrary waits, no network control:**
```javascript
it('logs in', () => {
  cy.visit('/login');
  cy.get('#email').type('admin@test.com');
  cy.get('#password').type('password');
  cy.get('#submit').click();
  cy.wait(3000); // 💀 arbitrary wait
  cy.url().should('include', '/dashboard');
  // Flaky: fails if API takes > 3s,
  // wastes time if API is fast
});
```

**GOOD - network-aware, retry-driven:**
```javascript
describe('Login', () => {
  beforeEach(() => {
    cy.intercept('POST', '/api/auth').as('authCall');
  });

  it('redirects admin to dashboard on success', () => {
    cy.visit('/login');
    cy.get('[data-cy=email]').type('admin@test.com');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=submit]').click();
    cy.wait('@authCall')
      .its('response.statusCode')
      .should('eq', 200);
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, Admin').should('be.visible');
  });

  it('shows error on invalid credentials', () => {
    cy.intercept('POST', '/api/auth', {
      statusCode: 401,
      body: { error: 'Invalid credentials' }
    }).as('failedAuth');
    cy.visit('/login');
    cy.get('[data-cy=email]').type('bad@user.com');
    cy.get('[data-cy=password]').type('wrong');
    cy.get('[data-cy=submit]').click();
    cy.wait('@failedAuth');
    cy.get('[data-cy=error-msg]')
      .should('contain', 'Invalid credentials');
  });
});
```

---

### ⚖️ Comparison Table

| Feature               | Cypress        | Playwright     | Selenium       |
|-----------------------|:--------------:|:--------------:|:--------------:|
| Language              | JS/TS only     | JS/TS/Python/Java/C# | Any     |
| Multi-browser         | Chrome/FF/Edge | All major + WebKit | All       |
| Multi-tab support     | Limited        | Yes            | Yes            |
| Network intercept     | Built-in       | Built-in       | WireMock/proxy |
| Retry-ability         | Built-in       | Built-in       | Manual         |
| Component testing     | Yes            | Experimental   | No             |
| Time-travel debugger  | Yes            | Trace viewer   | No             |
| Parallel execution    | Cloud / matrix | Built-in sharding | Grid        |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Cypress eliminates all flaky tests" | It eliminates timing-induced flakiness; test logic bugs, environment instability, and data races still cause flakiness. |
| "`cy.*` commands are synchronous" | They are queued - each returns immediately, but executes asynchronously in order. Using `async/await` with `cy.*` calls breaks the queue. |
| "cy.intercept() always stubs the network" | Without a `reply` fixture, `cy.intercept()` is a spy only - the real request still fires. |
| "Cypress can test any browser" | Safari/WebKit is not natively supported; use Playwright for WebKit coverage. |
| "Component testing replaces unit testing" | Cypress component tests render in a real browser DOM - they complement, not replace, Jest/Vitest unit tests. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Detached DOM element assertion**

**Symptom:** `CypressError: cy.click() failed because the element has become detached from the DOM`.
**Root Cause:** React/Vue re-renders the component between `cy.get()` resolving and `cy.click()` executing - the reference becomes stale.
**Diagnostic:**
```javascript
// Reproduce: add a console.log to component re-render lifecycle
// Check if assertion fires during a state update
cy.get('[data-cy=btn]').then($el => {
  cy.log('Element found:', $el.length);
});
```
**Fix:**
```javascript
// BAD - element reference can go stale
const btn = cy.get('[data-cy=btn]');
cy.wait(500); // state update happens here
btn.click(); // stale reference 💀

// GOOD - re-query atomically
cy.get('[data-cy=btn]').click(); // re-queried fresh
```
**Prevention:** Never store `cy.get()` results in variables; always chain commands directly.

---

**Mode 2 - `cy.intercept()` registered after request fires**

**Symptom:** Intercept stub is defined but the real network request fires; assertions on stub state fail.
**Root Cause:** `cy.visit()` triggers the request before the `cy.intercept()` registration is processed.
**Diagnostic:**
```javascript
// Wrong order - visit fires request first:
cy.visit('/dashboard');
cy.intercept('GET', '/api/user').as('user'); // too late!
```
**Fix:**
```javascript
// BAD - intercept after visit
cy.visit('/dashboard');
cy.intercept('GET', '/api/user').as('user');

// GOOD - intercept before visit
cy.intercept('GET', '/api/user').as('user');
cy.visit('/dashboard');
cy.wait('@user');
```
**Prevention:** Always define `cy.intercept()` calls before any navigation command; use `beforeEach` for route setup.

---

**Mode 3 - Flaky tests from shared database state**

**Symptom:** Tests pass individually but fail in random order in CI; some tests find data left by previous tests.
**Root Cause:** E2E tests mutate a shared test database without cleanup; test ordering creates data dependency.
**Diagnostic:**
```bash
npx cypress run --spec "cypress/e2e/orders.cy.js" \
  --env order=random 2>&1 | grep "AssertionError"
```
**Fix:**
```javascript
// BAD - no cleanup
it('creates an order', () => {
  cy.request('POST', '/api/orders', { item: 'book' });
  // order left in DB for next test
});

// GOOD - use cy.task() for DB reset in beforeEach
beforeEach(() => {
  cy.task('db:resetOrders');
});
```
**Prevention:** Use `cy.task()` database reset hooks; adopt factory-based test data with unique identifiers per run.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** JavaScript, Testing, E2E Testing

**Builds On This (learn these next):** CI-CD, Playwright (E2E Testing), Testing Library

**Alternatives / Comparisons:** Playwright (E2E Testing), Selenium, Puppeteer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    │ In-browser JS E2E framework  │
│ PROBLEM       │ Flaky WebDriver timing tests │
│ KEY INSIGHT   │ Retry-ability removes waits  │
│ USE WHEN      │ React/Vue/Angular SPA E2E    │
│ AVOID WHEN    │ Multi-origin, Safari, mobile │
│ TRADE-OFF     │ Reliability vs. flexibility  │
│ ONE-LINER     │ cy.intercept + cy.wait alias │
│ NEXT EXPLORE  │ Playwright for cross-browser │
└──────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** Cypress runs in a single browser tab. Describe a realistic checkout flow that inherently requires two browser tabs (e.g., OAuth popup), and explain the architectural choices you would make to test it given Cypress's constraint.
2. **(Scale)** Your E2E suite has 400 specs running on a single Cypress process; CI takes 45 minutes. Compare the trade-offs of Cypress Cloud parallelisation vs. a self-managed GitHub Actions matrix strategy splitting spec files across runners.
3. **(Root Cause)** A `cy.get('[data-cy=submit]').click()` test passes locally but fails in CI with "element not visible". List the three most probable root causes and the diagnostic command you would run for each.
