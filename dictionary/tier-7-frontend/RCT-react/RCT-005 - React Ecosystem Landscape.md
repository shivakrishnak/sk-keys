---
id: RCT-005
title: React Ecosystem Landscape
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-002, RCT-004
used_by: RCT-019, RCT-027, RCT-051, RCT-066
related: RCT-002, RCT-019, RCT-067
tags:
  - react
  - frontend
  - ecosystem
  - overview
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /react/react-ecosystem-landscape/
---

# RCT-005 - REACT ECOSYSTEM LANDSCAPE

⚡ TL;DR - React is a rendering library; everything around
it - routing, forms, data fetching, state, build tools - is
provided by ecosystem libraries; knowing the landscape prevents
reinventing solved problems.

| #005            | Category: React                                                                      | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What React Is and Is Not, The Component Mental Model                                 |                 |
| **Used by:**    | Vite and CRA, React Router, Redux Toolkit, Micro-Frontend Architecture               |                 |
| **Related:**    | What React Is and Is Not, Vite and CRA, State Management Architecture Decision Guide |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer new to React often expects it to be like Angular
or Django - a complete framework with official opinions on
routing, forms, authentication, data fetching, and testing.
They open the React docs and find... just components and hooks.

The result: they reinvent solved problems (writing their own
router), use outdated approaches (the documentation they
found was for CRA which was deprecated in 2023), or install
competing libraries that do not work well together (Redux +
React Query + Apollo all managing overlapping concerns).

**THE BREAKING POINT:**
React's "bring your own everything" philosophy is its power
and its tax. Projects with no ecosystem knowledge suffer from:

- Wrong tool for the job (Redux for data that React Query
  handles better)
- Multiple layers solving the same problem (client-side state
  - server-state cache + optimistic updates all competing)
- Build tooling chosen by accident (CRA on a new 2024 project)

**THE INVENTION MOMENT:**
This entry is the map. React is the core; the ecosystem fills
the gaps. Knowing which gap each library fills, which
libraries are canonical in 2024, and which were canonical but
are now legacy prevents the most common mistakes.

---

### 📘 Textbook Definition

The **React ecosystem** is the collection of libraries,
frameworks, and tools that complement React's rendering
library to form complete web applications. Because React
provides only component rendering and state management
primitives, every production React application depends on
ecosystem libraries for routing, form handling, data fetching,
server-side rendering, build tooling, testing, and styling.
The ecosystem is characterised by competing alternatives in
most categories, with shifting canonical choices over time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
React is the engine; the ecosystem is everything else needed
to build a car.

**One analogy:**

> React is like the engine spec for a car. Linux is like the
> kernel. Neither is usable alone. The ecosystem adds the
> transmission (routing), fuel system (data fetching), body
> panels (UI component libraries), and instrumentation
> (DevTools, testing). Knowing the ecosystem means knowing
> which parts are production-grade and which are still
> experimental.

**One insight:**
The React ecosystem moves fast. A library that was canonical
in 2020 (CRA, Enzyme, Moment.js) may be deprecated or
superseded in 2024 (Vite/Next.js, React Testing Library,
date-fns). Treating ecosystem knowledge as static is how
teams end up maintaining legacy toolchains.

---

### 🔩 First Principles Explanation

**CATEGORY MODEL - What React Does NOT Provide:**

| Category              | React Provides  | Ecosystem Fills                          |
| --------------------- | --------------- | ---------------------------------------- |
| Build tooling         | Nothing         | Vite, Next.js, Remix, CRA (deprecated)   |
| Routing               | Nothing         | React Router v6, TanStack Router         |
| Server-side rendering | Primitives only | Next.js, Remix                           |
| Data fetching         | Nothing         | React Query, SWR, Apollo, RTK Query      |
| Global state          | Context (basic) | Redux Toolkit, Zustand, Jotai, Recoil    |
| Forms                 | Nothing         | React Hook Form, Formik                  |
| Styling               | Nothing         | Tailwind, CSS Modules, Styled Components |
| Testing               | Nothing         | React Testing Library, Vitest, Jest      |
| Component libraries   | Nothing         | shadcn/ui, MUI, Chakra UI                |
| Animation             | Nothing         | Framer Motion, React Spring              |

**STABILITY TIERS:**
Not all ecosystem choices carry equal switching cost:

- **High lock-in:** Framework choice (Next.js vs Remix vs Vite)
  - expensive to change
- **Medium lock-in:** State management (Redux vs Zustand) -
  touches many files
- **Low lock-in:** Styling (CSS Modules to Tailwind) - localised
  to component files

---

### 🧪 Thought Experiment

**SETUP:**
A new engineer joins a React team and asks: "What library
should I use to load users from a REST API and display them?"

**FIVE WRONG APPROACHES:**

1. `fetch` in `useEffect` with manual loading/error state
   (reinvents React Query for no benefit)
2. Redux for server data (the wrong tool - Redux is for
   client-side global state, not server cache)
3. `axios` with a custom hook but no caching, no refetch-on-
   focus, no stale-while-revalidate
4. Apollo Client for a REST API (GraphQL-specific)
5. CRA-based template from a 2021 tutorial (deprecated)

**ONE RIGHT APPROACH:**
Use React Query (`@tanstack/react-query`) for data fetching
and caching; use `useState` or URL params for any client-side
filtering. Choose Vite or Next.js depending on whether SSR
is needed. The right tool for each category exists - the skill
is knowing the categories exist and which tools are current.

---

### 🧠 Mental Model / Analogy

> Think of the React ecosystem as a tech stack layer cake.
> React is one layer. Below it are bundlers (Vite, Webpack).
> Above it are framework layers (Next.js wraps React). Around
> it are peers (React Router, React Query, Redux Toolkit).
> Each layer has a clear responsibility. Confusion comes from
> not knowing which layer solves which problem.

```
┌────────────────────────────────────────────────┐
│      FRAMEWORK LAYER (Next.js / Remix)        │
│   SSR, file-based routing, server components  │
├────────────────────────────────────────────────┤
│           REACT CORE LAYER                    │
│   Components, hooks, state, virtual DOM       │
├───────────────────┬────────────────────────────┤
│  DATA LAYER       │  STATE LAYER              │
│  React Query/SWR  │  Redux / Zustand / Jotai  │
├───────────────────┴────────────────────────────┤
│           UI + STYLING LAYER                  │
│  MUI / shadcn/ui / Tailwind / CSS Modules     │
├────────────────────────────────────────────────┤
│        BUILD + TOOLING LAYER                  │
│      Vite / TypeScript / ESLint / Vitest      │
└────────────────────────────────────────────────┘
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
React is the LEGO bricks. The ecosystem is the instruction
booklets, glue, paint, and display stand. You need all of
them to build a real product.

**Level 2 - How to use it (junior developer):**
Start with Vite for a new SPA. Add React Router v6 for
navigation. Add React Query for data fetching. Add a component
library (MUI or shadcn/ui) for pre-built UI elements. Use
React Testing Library + Vitest for tests. This covers 80% of
use cases in 2024.

**Level 3 - How it works (mid-level engineer):**
Next.js or Remix for SSR/SSG requirements. React Query
for server state with caching, optimistic updates, and
background sync. Redux Toolkit only when you have complex
client-side state with shared reducers; Zustand for lighter
alternatives. TypeScript for all production codebases.

**Level 4 - Why it was designed this way (senior/staff):**
React's "unbundled" design was intentional - Facebook used
different data fetching and state solutions internally and
did not want to impose a specific architecture. This enabled
a rich ecosystem but also created "choice fatigue." The
trend since 2020 is toward opinionated frameworks (Next.js)
that bundle React with specific ecosystem choices, reducing
configuration overhead.

**Level 5 - Mastery (distinguished engineer):**
Ecosystem decisions are architecture decisions. The choice
between Next.js and Vite determines where rendering happens
(server vs client), which affects SEO, performance, and
infrastructure costs. The choice between React Query and
Redux for server data determines cache coherence strategy.
A principal engineer evaluates these choices against
application requirements, team expertise, and long-term
maintenance cost - not based on tutorial popularity.

---

### ⚙️ How It Works (Mechanism)

**2024 Ecosystem Snapshot - Canonical Choices:**

```
FRAMEWORK / BUNDLER
  - New SPA (no SSR):      Vite
  - SSR / SSG / RSC:       Next.js 14+ (App Router)
  - Full-stack React:      Remix
  - [DEPRECATED]:          Create React App (2023)

ROUTING
  - SPA routing:           React Router v6
  - Type-safe routing:     TanStack Router
  - File-based (bundled):  Next.js App Router

DATA FETCHING
  - REST/GraphQL cache:    TanStack Query (React Query)
  - REST simple:           SWR
  - GraphQL first:         Apollo Client
  - Redux-integrated:      RTK Query

GLOBAL STATE
  - Complex client state:  Redux Toolkit
  - Lightweight global:    Zustand
  - Atomic state:          Jotai
  - [LEGACY]:              Redux (without RTK)

FORMS
  - Performance-critical:  React Hook Form
  - Full-featured:         Formik (older, heavier)

STYLING
  - Utility CSS:           Tailwind CSS
  - CSS isolation:         CSS Modules
  - CSS-in-JS:             Styled Components
  - Component library:     shadcn/ui, MUI, Chakra UI

TESTING
  - Unit / integration:    React Testing Library + Vitest
  - E2E:                   Playwright, Cypress
  - [DEPRECATED]:          Enzyme
```

---

### 🔄 The Complete Picture - End-to-End Flow

**HOW THE LAYERS INTERACT:**

```
User visits /products?category=shoes

1. Browser -> Next.js server (or CDN edge)
2. Next.js routes request to /app/products/page.tsx
3. React Server Component runs on server:
   - Fetches initial product data directly (no client roundtrip)
   - Returns HTML + React component tree
4. Browser receives initial HTML (fast first paint)
5. React hydrates on client (attaches event handlers)
6. User changes filter -> React Query fetches updated list
7. React Query caches result (next filter change is instant)
8. React Router handles navigation to /products/42 client-side
   (no full page reload)
```

Each layer handles one concern. The overlap between React
Query server state and Redux client state is the most
common architecture confusion - they solve different problems
and should coexist, not compete.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CRA is the standard way to start a React project" | CRA was deprecated in 2023. The React team recommends Vite for SPAs or Next.js for SSR. Using CRA in a new 2024 project means inheriting an unmaintained toolchain.                         |
| "Redux is required for React state management"     | Redux solves complex client-side state sharing. Simple apps need only useState + Context. Data fetching belongs in React Query, not Redux. Many modern React apps use no Redux at all.      |
| "React Query is a replacement for Redux"           | React Query manages server state (remote data, caching, sync). Redux manages client state (UI state, local data not from servers). They serve different purposes and often coexist.         |
| "Next.js is React"                                 | Next.js is a framework that includes React. It adds routing, SSR, SSG, and server components. An application built with Next.js is a Next.js application; React is one of its dependencies. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Ecosystem Choices (Technical Debt)**

**Symptom:**
A codebase uses CRA for build tooling, Enzyme for testing,
Moment.js for dates, and Redux (non-RTK) for state. Build
times are slow, tests are fragile, and the team spends time
on boilerplate.

**Root Cause:**
Ecosystem choices were made from tutorials that were current
in 2019-2021 and never revisited. The project treats these
as permanent infrastructure.

**Diagnostic Command:**

```bash
# Check for known-deprecated dependencies
npx depcheck
cat package.json | grep -E "create-react-app|enzyme|moment"
# Audit last release date of each major dependency
# on npmjs.com or via `npm outdated`
```

**Fix:**
Migrate build tooling first (CRA to Vite - usually 1-2 days).
Replace Enzyme with React Testing Library. Replace Moment.js
with date-fns or Temporal. Migrate Redux to Redux Toolkit.
Prioritise by blast radius and team pain.

---

**Wrong Library for Wrong Problem**

**Symptom:**
Redux is used to store server-fetched data. The team manually
writes actions for loading/success/error states. Cache
invalidation is never implemented. Data is always refetched
on page load.

**Root Cause:**
Server state was treated as client state. Redux was chosen
before React Query existed (pre-2019) and the choice was
never revisited.

**Diagnostic Command:**

```bash
# Red flags in Redux store:
# - actions named *_FETCH, *_LOADING, *_ERROR
# - reducers storing isLoading, error, lastFetched
# - selectors like selectUsersLoading
# These are all server-state patterns misplaced in Redux.
```

**Fix:**
Replace server-state Redux slices with React Query. Keep
Redux only for UI state (selectedTab, modalIsOpen) or
complex client-only logic (shopping cart, undo/redo).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What React Is and Is Not` - React's deliberate scope
  boundaries that the ecosystem fills
- `The Component Mental Model` - the building block all
  ecosystem libraries extend

**Builds On This (learn these next):**

- `Vite and Create React App` - the build tooling layer
- `React Router v6 Basics` - routing in the ecosystem
- `Redux Toolkit and Global State Architecture` - state layer
- `Rendering Strategy Framework` - SSR vs CSR vs SSG decision

**Alternatives / Comparisons:**

- `Angular` - a fully opinionated framework; includes its
  own router, HTTP client, forms, and DI - no ecosystem
  choice needed but also no ecosystem flexibility
- `Vue.js` - similar "core library + optional official
  plugins" philosophy but with more official first-party
  integrations than React

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The libraries that fill React's gaps:   │
│              │ routing, data, state, build, test, UI   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ React provides only rendering; every    │
│ SOLVES       │ production app needs 5+ other concerns  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Server state (React Query) and client   │
│              │ state (Redux) are different problems     │
├──────────────┼───────────────────────────────────────────┤
│ 2024 PICKS   │ Vite/Next.js, React Router v6, React    │
│              │ Query, Redux Toolkit, React Hook Form,  │
│              │ Tailwind/CSS Modules, Vitest+RTL        │
├──────────────┼───────────────────────────────────────────┤
│ DEPRECATED   │ Create React App, Enzyme, Redux (bare)  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Using Redux for server-fetched data;    │
│              │ using CRA for new projects in 2024      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Ecosystem flexibility vs framework      │
│              │ convention (Next.js vs Vite tradeoff)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "React is the engine; the ecosystem is  │
│              │  everything else needed to ship."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Vite -> React Router -> React Query     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. React provides components and hooks only. Routing, data
   fetching, state management, build tooling, and testing
   all come from ecosystem libraries - and each category
   has a 2024 canonical choice.
2. CRA was deprecated in 2023. New projects use Vite (SPA)
   or Next.js (SSR/SSG). Using CRA in 2024 is technical debt
   from day one.
3. Server state (API data: React Query) and client state (UI
   state: Redux/Zustand) are different problems requiring
   different tools. Mixing them causes architecture confusion.

**Interview one-liner:**
"React is a rendering library - everything else in a
production application comes from ecosystem libraries. In
2024 the canonical stack is Vite or Next.js for build
tooling, React Router v6 or file-based routing for
navigation, React Query for server-state data fetching,
Redux Toolkit or Zustand for client-side global state,
React Testing Library for testing, and Tailwind or CSS
Modules for styling."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When adopting a technology ecosystem, map the full category
space of problems it does not solve before writing code.
The first month of a project is the lowest-cost time to
make the right ecosystem choices.

**Where else this pattern appears:**

- Spring ecosystem (Spring Boot, Spring Data, Spring Security)
  - same pattern: core framework with a mapped ecosystem
- Kubernetes ecosystem (Helm, Istio, Prometheus, ArgoCD) -
  each solving a gap Kubernetes deliberately left open
- Python data science (NumPy + Pandas + Matplotlib + Sklearn)
  - composable tools, each owning one category

**Industry applications:**

- Large engineering teams create "technology radar" documents
  that map the React ecosystem by stability tier: adopt,
  trial, assess, hold. This prevents individuals from
  introducing unstable or deprecated libraries.

---

### 💡 The Surprising Truth

React Query (TanStack Query) and similar server-state
libraries have made Redux redundant for one of its most
common use cases - managing loading, success, and error
states for API calls. Studies of large React codebases show
that the majority of Redux state in pre-2019 applications
was server data that React Query would now handle
automatically (with caching, background refetch, and
stale-while-revalidate behaviour included). The React team
itself now recommends React Query as the first solution for
data fetching. Redux is not deprecated - but its correct
use case (complex client-only state with shared reducers)
is far smaller than its historical usage suggests.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **MAP** Draw the ecosystem layer diagram from memory:
   framework/build, routing, data fetching, client state,
   forms, styling, testing - and name the 2024 canonical
   tool for each.
2. **AUDIT** Given a `package.json` from a 2021 project,
   identify which dependencies are deprecated or superseded
   and propose a migration priority order based on
   maintenance burden and switching cost.
3. **DECIDE** Given a new project requirement (public-facing
   e-commerce site needing SEO, internal SPA dashboard,
   real-time collaborative editor), specify which React
   ecosystem stack you would choose for each and why.
4. **EXPLAIN** Describe the difference between server state
   and client state to a React developer who has been using
   Redux for all state management, with a concrete code
   comparison.
5. **PREVENT** Write a team "ecosystem decision record" (EDR)
   for a specific library choice (e.g., choosing React Query
   over RTK Query) that documents the problem, alternatives
   considered, decision, and future migration triggers.

---

### 🧠 Think About This Before We Continue

**Q1.** The React ecosystem changes rapidly - libraries that
were recommended in the official docs 3 years ago are now
deprecated (CRA, Enzyme). How should a team manage ecosystem
evolution in a production codebase? What governance process
prevents teams from drifting to stale choices?
_Hint: Technology radar, ADR (Architecture Decision Records),
dependency review in CI._

**Q2.** React Query and Redux are often described as solving
"different problems," but they can both store the result of
an API call. When would you deliberately keep API-fetched
data in Redux rather than in React Query? What makes that
data "client state" rather than "server state"?
_Hint: Think about optimistic updates, offline-first
requirements, and complex multi-step workflows where the
server is the destination, not the source of truth._

**Q3.** Next.js now recommends React Server Components for
data fetching - fetching data directly in server components
rather than in `useEffect` or React Query. How does this
change the ecosystem layer model? Which ecosystem libraries
become less relevant in a Next.js App Router application,
and which remain essential?
_Hint: React Query's role changes when the component that
fetches data runs on the server and never hydrates._
