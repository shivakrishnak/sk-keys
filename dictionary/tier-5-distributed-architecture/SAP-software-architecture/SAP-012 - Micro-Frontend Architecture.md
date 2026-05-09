---
id: SAP-012
title: Micro-Frontend Architecture
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-011, SAP-051
used_by: SAP-008
related: SAP-011, SAP-039, SAP-041
tags:
  - architecture
  - frontend
  - advanced
  - pattern
  - microservices
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /software-architecture/micro-frontend-architecture/
---

# SAP-012 - Micro-Frontend Architecture

⚡ **TL;DR -** Micro-frontend architecture decomposes a web application into independently deployable UI modules, each owned and shipped by a separate team.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-011, SAP-051          |
| **Used by**    | SAP-008                   |
| **Related**    | SAP-011, SAP-039, SAP-041 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A 200-person engineering organisation has successfully decomposed its backend into 40 microservices. Each backend team deploys independently. But there is one monolithic React frontend repository with 300,000 lines of code. Every feature crosses the boundary of three teams in the same repo. A single deploy pipeline for the entire frontend creates a bottleneck: 12 teams wait on one CI gate.

**THE BREAKING POINT:** The checkout team can't ship a critical hotfix because the search team has a breaking test that doesn't pass. The frontend monolith has become the single most expensive coordination point in the organisation - cancelling all the autonomy gained by splitting the backend.

**THE INVENTION MOMENT:** By extending the microservices principle to the UI layer - "teams own a vertical slice including their frontend" - organisations gained independent deployability end-to-end. The micro-frontend idea, popularised by ThoughtWorks in 2016, completes the vertical team autonomy that microservices alone could not deliver.

**EVOLUTION:**
Early micro-frontend implementations used iframes for maximum isolation (poor UX). The next wave used single-SPA for framework-agnostic runtime orchestration (2018). Module Federation (Webpack 5, 2020) provided native runtime composition with shared library version negotiation. Today, server-side composition is re-emerging: Next.js Server Components and React Server Components offer server-rendered micro-frontends without client-side orchestration complexity, potentially resolving the bundle-size problem that client-side composition creates.

---

### 📘 Textbook Definition

**Micro-frontend architecture** is an architectural style that structures a web application as a composition of independently developed, tested, and deployed frontend modules - each owned by a single team, corresponding to a bounded business domain, and integrated at runtime in the user's browser (or at edge/server render time) by a shell application or orchestrator.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Microservices for the UI - each team owns and deploys their own piece of the page.

> A micro-frontend application is like a newspaper. Each section (Sports, Finance, Culture) is produced by an independent editorial team, printed independently, and assembled into a single product at distribution time. The reader sees one newspaper, not six.

**One insight:** The integration point moves from compile time (monorepo shared code) to runtime (browser assembling independent bundles) - which is what makes independent deployment possible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A team cannot independently deploy if its artefact is bundled with another team's artefact
2. Integration at runtime requires a defined composition model
3. Team autonomy requires owning the full vertical: API → backend → frontend
4. UX consistency requires explicit shared contracts, not implicit shared code

**DERIVED DESIGN:** Each team produces a standalone deployable frontend artefact. A shell application (the orchestrator) loads and composes these artefacts at runtime via a defined integration mechanism (Module Federation, iframes, Web Components, or `<script>` tags).

**THE TRADE-OFFS:**
**Gain:** Independent deployability; team autonomy; technology heterogeneity where justified; fault isolation.
**Cost:** Shared state management complexity; UX consistency overhead; increased initial payload risk; distributed frontend debugging is harder.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce site has three teams: Search, Product Detail, and Checkout.

**WHAT HAPPENS WITHOUT MICRO-FRONTENDS:** Search team finds a critical performance bug. Fix is written in 2 hours. But the monolith's deploy pipeline runs Search, PDP, and Checkout tests together. Checkout has a flaky test. The fix is held for three days. Revenue impact: measurable.

**WHAT HAPPENS WITH MICRO-FRONTENDS:** Search team's fix is merged and deployed to their own CDN path in 30 minutes. The shell loads the updated Search bundle on next page load. Checkout never knows a deploy happened.

**THE INSIGHT:** The organisational benefit (team autonomy) and the technical mechanism (runtime composition) are inseparable. Micro-frontends are primarily an organisational architecture with a technical implementation.

---

### 🧠 Mental Model / Analogy

> A micro-frontend application is like a web portal. The portal shell provides the frame (navigation, auth, shared chrome). Each portlet (channel widget) is an independent application that loads into a slot. Teams own their portlet lifecycle completely. The portal assembles them into a coherent page.

- **Portal shell** → micro-frontend orchestrator / app shell
- **Portlet** → micro-frontend module (owned by one team)
- **Portlet slot** → route-based or element-based mount point
- **Portal theme** → shared design system tokens
- **Portlet isolated session** → module's scoped state

Where this analogy breaks down: Classic portlets (JSR-286) were server-assembled; micro-frontends add the critical dimension of client-side runtime composition, which enables richer interaction patterns across module boundaries.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of one big website codebase, each team has their own smaller codebase for their part of the site. They publish it when it's ready, and the main page pulls all the pieces together.

**Level 2 - How to use it (junior developer):**
The most common approach: route-based splitting. The shell (`app-shell`) owns the navigation and router. When a user navigates to `/checkout`, the shell dynamically imports the Checkout micro-frontend bundle. Each team deploys a versioned JavaScript bundle to a CDN. The shell's import map (or Module Federation manifest) tells it where to find each team's latest bundle.

**Level 3 - How it works (mid-level engineer):**
Four integration strategies: (1) **Build-time integration** - npm packages; not true micro-frontends (bundled together). (2) **Server-side composition** - edge or BFF assembles HTML fragments (SSI, ESI); great for SSR. (3) **iframes** - maximum isolation, poor UX (navigation, height, shared auth). (4) **Client-side composition** - Module Federation, Single-SPA, or custom loaders; most common. Module Federation is the dominant approach: each team exposes named components via `exposes` config; the shell consumes them via `remotes`; Webpack negotiates shared library versions at runtime.

**Level 4 - Why it was designed this way (senior/staff):**
The key insight is that independence requires solving the shared dependency problem at the right layer. Build-time npm packages solve dependency management but sacrifice deployment independence. Module Federation solves both by deferring dependency resolution to runtime and providing a singleton negotiation protocol for shared libraries. The cost is that the browser now orchestrates what a bundler previously handled - introducing new failure modes (network partitioning of a module load, version negotiation failures). Mature implementations add module load monitoring, fallback bundles, and canary deployment via the import manifest. The organisational decision (Conway's Law alignment) must precede the technical decision - teams cannot be autonomous if they are not assigned full vertical ownership.

---

### ⚙️ How It Works (Mechanism)

Module Federation composition at runtime:

```
 Browser loads app-shell bundle
         │
         ▼
 Shell reads remote manifest
 (remoteEntry.js per team)
         │
         ▼
 User navigates to /checkout
         │
         ▼
 Shell dynamically imports:
 checkout-mfe/remoteEntry.js
         │
         ▼
 Webpack runtime negotiates
 shared libs (react, react-dom)
         │
         ▼
 CheckoutApp component mounts
 in shell's <div id="mfe-slot">
```

Team boundaries and ownership:

```
 ┌─────────────────────────────────────┐
 │          App Shell (Infra team)     │
 │  ┌─────────────┐ ┌───────────────┐  │
 │  │  Search MFE │ │  Product MFE  │  │
 │  │ (Team A)    │ │  (Team B)     │  │
 │  └─────────────┘ └───────────────┘  │
 │  ┌─────────────────────────────┐    │
 │  │     Checkout MFE (Team C)   │    │
 │  └─────────────────────────────┘    │
 └─────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
 Team C ships Checkout hotfix
         │
         ▼
 Checkout CI/CD pipeline runs
 (independent of other teams)
         │               ← YOU ARE HERE
         ▼
 New bundle deployed to CDN:
 checkout/remoteEntry.js v2.4.1
         │
         ▼
 Shell's module manifest updated
 (or runtime fetch on next load)
         │
         ▼
 Next user loading /checkout
 receives updated Checkout module
         │
         ▼
 Other teams unaffected, zero
 coordination required
```

**FAILURE PATH:**

- Checkout bundle fails to load (network/CDN error) → shell must show fallback, not blank page
- React version mismatch: shell uses 18.2, checkout requires 18.0 → hook call error at runtime
- Checkout module throws unhandled exception → must not crash the entire shell application

**WHAT CHANGES AT SCALE:**
At 20+ micro-frontends: performance becomes critical (import manifest preloading, edge caching of remoteEntry files). A runtime module registry (a service that maps module name to current CDN URL) enables canary deployments per module. Distributed tracing must propagate trace IDs across module boundaries for end-to-end observability.

---

### 💻 Code Example

**BAD - build-time integration via npm (not independently deployable):**

```typescript
// package.json of monolith shell
// "dependencies": {
//   "@company/checkout-ui": "2.4.1",
//   "@company/search-ui": "1.8.0"
// }
// Both teams must bump version AND
// rebuild + redeploy the shell.
// Not independently deployable.
import { CheckoutApp } from "@company/checkout-ui";
```

**GOOD - Module Federation runtime integration:**

```javascript
// webpack.config.js - App Shell
const { ModuleFederationPlugin } = require("webpack").container;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "shell",
      remotes: {
        checkout: "checkout@https://cdn.co/mfe" + "/checkout/remoteEntry.js",
        search: "search@https://cdn.co/mfe" + "/search/remoteEntry.js",
      },
      shared: {
        react: { singleton: true, requiredVersion: "^18.0" },
        "react-dom": {
          singleton: true,
          requiredVersion: "^18.0",
        },
      },
    }),
  ],
};

// webpack.config.js - Checkout MFE
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "checkout",
      filename: "remoteEntry.js",
      exposes: {
        "./CheckoutApp": "./src/CheckoutApp",
      },
      shared: {
        react: { singleton: true },
        "react-dom": { singleton: true },
      },
    }),
  ],
};

// Shell: lazy-load Checkout at runtime
const CheckoutApp = React.lazy(() => import("checkout/CheckoutApp"));
// Checkout team deploys independently.
// Shell loads latest without rebuild.
```

---

### ⚖️ Comparison Table

| Integration Type      | Deploy Independence | UX Integration | Isolation | Complexity | Best For                   |
| --------------------- | ------------------- | -------------- | --------- | ---------- | -------------------------- |
| Build-time npm        | None                | Full           | Low       | Low        | Single team monorepo       |
| Server-side (SSI/ESI) | Full                | Good           | Medium    | Medium     | SSR, SEO-critical pages    |
| iframes               | Full                | Poor           | Maximum   | Low–Medium | Third-party embeds         |
| Module Federation     | Full                | Full           | Medium    | High       | SPA with many teams        |
| Single-SPA            | Full                | Good           | Medium    | Medium     | Framework-agnostic routing |
| Web Components        | Full                | Good           | High      | Medium     | Design system isolation    |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                       |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| "Micro-frontends mean different frameworks per team" | Framework freedom is _allowed_, not required; consistency is usually preferred; heterogeneity has real costs  |
| "Module Federation = micro-frontends"                | Module Federation is one implementation mechanism; micro-frontends is the architectural pattern it implements |
| "Micro-frontends solve UX inconsistency"             | They create risk of UX inconsistency; solving it requires active design system governance                     |
| "Each page should be a micro-frontend"               | Granularity should align with team ownership boundaries, not URL structure                                    |
| "Micro-frontends are always slower"                  | With proper preloading and CDN strategy, performance can match a monolith; naive implementation is slower     |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: React version conflict causes runtime crash**

**Symptom:** `Invalid hook call` error; `react` appears twice in bundle analyser.
**Root Cause:** Two micro-frontends load separate React instances; hooks require a single React tree.
**Diagnostic:**

```bash
# Check for duplicate react in bundle
npx webpack-bundle-analyzer \
  dist/stats.json
# Look for two react nodes in tree
```

**Fix:**
BAD: Each MFE bundles its own React without `singleton: true`.
GOOD: Set `shared: { react: { singleton: true, eager: true } }` in all MFE Module Federation configs. The shell's version wins.
**Prevention:** CI step validates all MFEs use the same React major version before release.

---

**Mode 2: One failing MFE crashes the entire application**

**Symptom:** A network error loading `checkout/remoteEntry.js` throws and breaks the whole shell.
**Root Cause:** No error boundary around dynamically loaded micro-frontend.
**Diagnostic:**

```bash
# Simulate MFE load failure
curl -I https://cdn.co/mfe/checkout/\
  remoteEntry.js
# Expect 200; if 404/500, MFE is down
```

**Fix:**
BAD: `const Checkout = React.lazy(() => import('checkout/CheckoutApp'))` with no error boundary.
GOOD: Wrap each MFE mount point in an `<ErrorBoundary fallback={<CheckoutFallback />}>` with retry logic.
**Prevention:** Contract test in CI that verifies remoteEntry is reachable before promoting to production.

---

**Mode 3: Shared state cross-module coupling**

**Symptom:** Module A breaks when Module B loads because both read/write `window.store` or a shared Redux store.
**Root Cause:** Teams share mutable global state rather than communicating through events.
**Diagnostic:**

```bash
grep -r "window\.__" src/*/
grep -r "import.*from.*shell/store" src/*/
```

**Fix:**
BAD: Checkout imports auth state from `shell/store` to get `currentUser`.
GOOD: Shell passes `userId` to Checkout via a prop or URL param at mount time; Checkout fetches its own auth context.
**Prevention:** Architecture review checklist item: "Does this MFE import from another MFE's bundle?" should always be No.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Decomposing a system into independently deployable units trades internal simplicity for external coordination protocols. The value is proportional to team scale - below a critical team size, the coordination cost exceeds the autonomy benefit. This threshold pattern is universally applicable to any decomposition strategy.

**Where else this pattern appears:**

- **City planning:** autonomous districts (boroughs, arrondissements) share infrastructure protocols (roads, utilities, zoning law) but govern independently - the same pattern of autonomous units with shared integration contracts.
- **Open-source ecosystems:** npm packages are independently published modules that compose via package manager protocols - the same independent deployability model at ecosystem scale.
- **SaaS platform integration:** independent vendor products compose via webhook and API contracts in a customer's workflow - micro-frontend composition applied at the product ecosystem level.

---

### 💡 The Surprising Truth

The most expensive hidden cost of micro-frontend architecture is not the runtime composition infrastructure - it is the design system coordination tax. Each independently deployed MFE must maintain visual and behavioural consistency with every other MFE the user sees simultaneously. This requires a shared design system that all MFEs consume, which becomes the highest-coupling artefact in the entire architecture - the thing everyone depends on but no single team owns. Micro-frontends solve the deployment coupling problem while creating a design system governance problem of equal or greater complexity.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-011 - Loose Coupling of Frontend Modules (the design principle that micro-frontends implement at deployment scale)
- SAP-051 - Coupling (the fundamental concept; understanding coupling is required to evaluate micro-frontend trade-offs)

**Builds On This (learn these next):**

- SAP-039 - Modular Monolith Patterns (the simpler alternative for teams not yet needing independent deployment)
- SAP-008 - Architecture Review (the process that evaluates whether micro-frontend complexity is justified for a given team context)

**Alternatives / Comparisons:**

- Monorepo with shared libraries - managed coupling without deployment independence; lower operational overhead
- iframes - maximum isolation, worst UX integration (focus, scroll, modals are broken)
- React Server Components - server-side composition without client-side bundle splitting; a different trade-off on the same problem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────┐
│ WHAT IT IS    Independently deployable   │
│               UI modules per team        │
│ PROBLEM       Frontend monolith blocks   │
│               team autonomy at scale     │
│ KEY INSIGHT   Integration shifts from    │
│               compile-time to runtime    │
│ USE WHEN      Multiple teams, same       │
│               product, independent       │
│               deploy needed              │
│ AVOID WHEN    Single team, startup,      │
│               SEO-first static site      │
│ TRADE-OFF     Autonomy / complexity      │
│ ONE-LINER     Microservices for the UI   │
│ NEXT EXPLORE  Module Federation,         │
│               Single-SPA                 │
└──────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Type A - System Interaction)** The shell application in a micro-frontend system is itself a deployed artefact. If the shell team changes the mount contract (the props passed to each MFE at initialisation), how does that change propagate across all consumer teams - and what governance mechanism prevents it becoming a coordination bottleneck?

*Hint:* Research the concept of "contract testing" (Pact framework) as used in microservices - specifically consumer-driven contract tests, which flip the dependency direction and give each MFE team the ability to specify the contract they need from the shell, rather than the shell dictating to consumers.

2. **(Type B - Scale)** Module Federation resolves shared library versions at runtime using a negotiation protocol. At what point does the number of micro-frontends and shared libraries make this negotiation a measurable performance problem - and what architectural mitigation exists?

*Hint:* Look at the Module Federation performance benchmarks done by Zack Jackson (the feature's author) and the import maps specification - import maps were designed partly to address the version negotiation overhead problem by moving resolution to the build step, trading runtime flexibility for load-time predictability.

3. **(Type C - Design Trade-off)** A team argues for iframe-based isolation because it eliminates all shared state and CSS risks. Another team argues for Module Federation because iframes prevent seamless UX (modals, keyboard focus, shared scroll context). How would you formally evaluate this trade-off for a specific product context?

*Hint:* Research the concept of "integration surface" as used in the Thoughtworks micro-frontend article - specifically the list of UX integration requirements (cross-MFE navigation, shared authentication state, consistent error handling) and how iframe isolation breaks each one, to build a structured evaluation framework.
