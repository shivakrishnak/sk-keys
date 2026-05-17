---
id: RCT-002
title: What React Is and Is Not
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-001
used_by: RCT-003, RCT-004, RCT-007
related: RCT-001, RCT-003, RCT-005
tags:
  - react
  - frontend
  - foundational
  - mental-model
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /react/what-react-is-and-is-not/
---

# RCT-002 - WHAT REACT IS AND IS NOT

⚡ TL;DR - React is a JavaScript library for building UI components
- not a framework, not a language, not a solution for routing,
data fetching, or state management on its own.

| #002 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | The Frontend Complexity Problem | |
| **Used by:** | Declarative UI vs Imperative DOM, The Component Mental Model, Component | |
| **Related:** | The Frontend Complexity Problem, Declarative UI vs Imperative DOM, React Ecosystem Landscape | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
New developers arriving at their first React job often discover
they have been misled. They read "our stack is React" and assumed
they were learning one thing. They then encounter: React Router
(routing), Redux Toolkit (state), React Query (data fetching),
Axios (HTTP), Vite (build), Jest (testing), Styled Components
(styling). Seven different libraries - and that is a conservative
count. Nobody warned them.

The other extreme: engineers who know React assume it handles
what Angular handles - routing, HTTP, forms, DI, testing
utilities, all included. They build a React app and then reach
for routing and find... nothing. They reach for HTTP and find...
nothing. This leads to either analysis paralysis (which of the 23
routing libraries should I choose?) or a poorly chosen default
that causes pain later.

**THE BREAKING POINT:**
The confusion manifests in two failure modes. Beginners over-reach
- they try to use React state for things that belong in a URL, a
server, or a form library, creating unnecessary complexity.
Experienced engineers from full-framework backgrounds under-reach
- they expect React to handle concerns it deliberately delegates
to the ecosystem, then feel betrayed when it does not.

**THE INVENTION MOMENT:**
This is exactly why understanding React's precise scope matters.
React is a library for one thing: rendering UI components based
on state. Everything beyond that is a deliberate non-goal.

**EVOLUTION:**
React began in 2013 as a pure rendering library. Facebook
extracted it from their internal codebase and open-sourced it.
Over time, hooks (2019) added official state and side-effect
management to components. React 18 (2022) added concurrent
features and React Server Components. At each step, React stayed
laser-focused on the component model and explicitly left routing,
data fetching, and server communication to ecosystem libraries.
This design choice distinguishes React from Angular, which is an
opinionated full framework.

---

### 📘 Textbook Definition

React is an open-source JavaScript library developed by Meta
(formerly Facebook) for building user interfaces, specifically
the view layer of web applications. It implements a declarative,
component-based programming model in which UI is expressed as a
tree of components - functions or classes that accept data as
props and return a description of what the UI should look like.
React manages the reconciliation between that description and the
actual DOM. It is explicitly not a framework: it provides no
built-in routing, HTTP client, form management, or dependency
injection.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
React is a library for building UI components - it handles
the view layer and nothing else by default.

**One analogy:**
> React is like a LEGO brick system. It gives you the bricks
> (components) and the rules for connecting them (props, state).
> It does not give you a specific thing to build. If you want a
> car, you need to get wheels, an engine, and seats from other
> sets. React gives you the building system; the full application
> stack is your responsibility to assemble.

**One insight:**
The single most important thing to understand: React's minimal
scope is a deliberate feature, not a weakness. It gives teams the
freedom to choose best-in-class solutions for each concern.
The cost is that teams must make those choices explicitly - React
will not make them for you.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. React handles exactly one concern: rendering UI as a function
   of state and props.
2. React makes no assumptions about the rest of the application
   stack - routing, server communication, persistence, and
   styling are all outside React's responsibility.
3. React's public API is the component model: define components,
   pass props, manage state with hooks.

**DERIVED DESIGN:**
Given these invariants, React's API surface is deliberately
small. The core API is: `React.createElement` (or JSX as
syntactic sugar), `useState`, `useEffect`, `useContext`, and
`useRef`. Everything beyond the component lifecycle and state
is delegated. This keeps React's internals focused and allows
the runtime to be as small as it can be (~45KB gzipped for
React + ReactDOM, as of React 18).

**THE TRADE-OFFS:**
**Gain:** Flexibility - choose the best routing, state
management, data fetching, and testing tools for your specific
project constraints. Combine React with any backend, any styling
approach, any server architecture.
**Cost:** Decision overhead - every project requires explicit
architectural choices that Angular or Next.js would make for you.
Teams must develop framework selection expertise in addition to
React expertise.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Building a non-trivial web application requires
handling routing, state, data fetching, and styling. These
concerns are genuinely complex regardless of which library you
use.
**Accidental:** Confusion about what React handles vs what the
ecosystem handles is purely informational complexity - resolved
once by learning React's scope clearly.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams start a React project on the same day. Team A has
studied React's scope carefully. Team B has not.

**WHAT HAPPENS WITHOUT CLARITY:**
Team B begins. They wire up components. The first feature requires
navigation between pages. They look in the React docs. No routing
API. They google "React routing" and find 12 options. One hour
lost to comparison paralysis. Next feature needs to fetch data
from an API. They try `fetch` inside a component. It works, but
they notice weird behaviour on strict mode double-invocation.
They add loading states manually, then error states. Three weeks
later they have reinvented React Query badly. Every architectural
decision costs 3-5 times more time than it should.

**WHAT HAPPENS WITH CLARITY:**
Team A begins. They know React handles rendering; they will use
React Router for routing and React Query for data fetching.
They spend 20 minutes picking these tools (they researched before
starting), install them, and immediately build features. Their
mental model is clear: React = components, Router = navigation,
Query = server state. Every concern has an owner.

**THE INSIGHT:**
Understanding what a tool does NOT do is as important as
understanding what it does. A clear mental model of React's scope
boundary saves hours per feature across an entire project
lifetime.

---

### 🧠 Mental Model / Analogy

> Think of React as the engine block of a car. It does one
> thing - convert fuel (state) into motion (UI updates) - and
> it does it exceptionally well. You still need wheels, a
> steering system, brakes, a chassis, and a body. None of those
> are the engine's job. React is the engine. Your job is to
> build the car.

Mapping:
- "Engine" → React (converts state into rendered UI)
- "Steering system" → React Router (navigation)
- "Fuel delivery" → React Query / SWR (data fetching)
- "Instrument panel" → component tree (what the user sees)
- "Chassis" → Next.js or Vite (the full application framework)
- "Custom bodywork" → Styled Components / Tailwind (styling)

Where this analogy breaks down: You can swap any part of a car
independently. In a React application, some choices are less
independent - switching state management libraries mid-project
can require significant refactoring.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
React is a tool for building the visual parts of websites and
web apps - the things users see and interact with. It is
specifically the part that takes data and turns it into buttons,
forms, lists, and pages.

**Level 2 - How to use it (junior developer):**
You write React components - JavaScript functions that describe
what a piece of the UI should look like. React's job ends there.
For navigation you add React Router; for API calls you use
`fetch` or a library like React Query; for global state you pick
from Context, Redux, Zustand, or Jotai based on your needs.

**Level 3 - How it works (mid-level engineer):**
React's runtime consists of two parts: the reconciler (computes
what changed) and the renderer (applies changes to the DOM, or
to native, or to a server string). The renderer is separate,
which is why React Native can use the same reconciler with a
different renderer for iOS/Android. The reconciler is the stable,
versioned core; renderers are swap-able.

**Level 4 - Why it was designed this way (senior/staff):**
Facebook's engineering team deliberately chose the library model
over the framework model to avoid the failure mode of opinionated
frameworks that bake in architectural decisions prematurely. They
had learned from Angular 1's two-way binding that strong opinions
about data flow could block future performance improvements.
React's minimal core kept the door open for Fiber (2017),
concurrent mode (2022), and server components (2023) - none of
which would have been possible if React had owned routing and
data fetching too.

**Level 5 - Mastery (distinguished engineer):**
The library vs framework choice is a governance decision as much
as a technical one. Libraries transfer architectural
responsibility to the team. At a company with strong frontend
engineers, this enables best-in-class choices. At a company with
junior teams or high turnover, the lack of opinionation becomes
a liability - every new developer must re-learn the team's
specific architecture. This is why Next.js has grown dominant:
it provides opinions on top of React's blank slate, giving teams
a "React with framework guarantees" option. The senior engineer
chooses between raw React and Next.js based on team capability
and project longevity, not on technical merit alone.

---

### ⚙️ How It Works (Mechanism)

React's scope can be precisely defined by its package
boundaries:

```
┌────────────────────────────────────────────────────────┐
│ REACT PACKAGE SCOPE                                   │
├────────────────────────────────────────────────────────┤
│ IN:  Component model (function/class components)      │
│      Props and state                                  │
│      Virtual DOM (vDOM) reconciliation                │
│      Hooks (useState, useEffect, useContext, etc.)    │
│      Event system (synthetic events)                  │
│      Ref system                                       │
│      Context API                                      │
│      Concurrent rendering (React 18+)                 │
│      Server Components (experimental/React 18+)       │
├────────────────────────────────────────────────────────┤
│ OUT (explicitly delegated to ecosystem):              │
│      Routing                  → React Router, TanStack│
│      HTTP / data fetching     → React Query, SWR,    │
│                                  Axios, fetch         │
│      Server-side rendering    → Next.js, Remix        │
│      Build tooling            → Vite, webpack         │
│      Form validation          → React Hook Form,      │
│                                  Formik, Zod          │
│      Styling                  → CSS Modules, Tailwind,│
│                                  Styled Components    │
│      Global state management  → Redux, Zustand, Jotai │
│      Testing utilities        → React Testing Library │
│      Animations               → Framer Motion         │
└────────────────────────────────────────────────────────┘
```

The core rendering pipeline React DOES own:

1. Developer writes component as a function returning JSX.
2. React compiles JSX to `React.createElement()` calls (build
   time, via Babel or Vite).
3. At runtime, React calls the component function, producing a
   virtual DOM tree of JavaScript objects.
4. React's reconciler diffs the new tree against the previous
   one (the "commit phase").
5. React's renderer (ReactDOM for web) applies minimal real DOM
   changes.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
┌──────────────────────────────────────────────────────┐
│ Full React Application Stack                        │
├──────────────────────────────────────────────────────┤
│ Browser URL change                                  │
│        │                                            │
│        ▼                                            │
│ React Router (not React) handles route match       │
│        │                                            │
│        ▼                                            │
│ Route component renders ← REACT STARTS HERE        │
│        │                                            │
│        ▼                                            │
│ React Query (not React) fetches data               │
│        │                                            │
│        ▼                                            │
│ useState / useEffect manage local component state  │
│        │                                            │
│        ▼                                            │
│ Components re-render on state change               │
│        │                                            │
│        ▼                                            │
│ React reconciler diffs vDOM                        │
│        │                                            │
│        ▼                                            │
│ ReactDOM commits real DOM changes ← REACT ENDS     │
│        │                                            │
│        ▼                                            │
│ Styled Components / Tailwind applies styles        │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
When a team conflates React with "the whole stack," they
reinvent routing or data fetching badly inside React components,
creating unmaintainable code. Or they reach for React state to
solve URL synchronisation, producing apps where the URL and UI
desynchronise.

**WHAT CHANGES AT SCALE:**
At large scale, the ecosystem choices matter more than React's
core. A wrong state management library choice at scale is far
more painful than a wrong React API usage, because state
management touches every part of the application.

---

### ⚖️ Comparison Table

| | React | Angular | Vue | Svelte |
|---|---|---|---|---|
| Type | Library (UI only) | Full framework | Progressive framework | Compiler + library |
| Routing included | No | Yes (Angular Router) | No (Vue Router separate) | No (SvelteKit adds it) |
| State management | Hooks / external | RxJS / NgRx | Vuex / Pinia | Stores (built-in) |
| HTTP client | External (fetch, Axios) | Built-in (HttpClient) | External | External |
| Opinion level | Low | High | Medium | Medium |
| **Best For** | Teams wanting control | Enterprise with strong conventions | Balanced choice | Performance-critical |

**How to choose:** If your team needs conventions enforced and
prefers batteries-included, choose Angular (enterprise) or
Next.js (React with framework). If your team wants flexibility
to choose best-in-class for each concern, use React directly.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "React is a framework" | React is a library. It provides the component model and rendering only. The full application stack requires additional libraries for routing, data fetching, and state. |
| "React includes routing" | React has no routing built in. React Router, TanStack Router, or a meta-framework like Next.js provides routing. |
| "React and Next.js are the same thing" | Next.js is a framework built on top of React. React is the rendering layer; Next.js adds routing, SSR, file-based conventions, and build optimisations. |
| "useState is enough for all state" | React's useState manages local component state. Server state (API data), URL state, and global app state each require different solutions. |
| "Learning React means you can build a full app" | React is one piece of the stack. A production app requires additional decisions about routing, data fetching, styling, testing, and deployment. |

---

### 🚨 Failure Modes & Diagnosis

**Rebuilding Routing Inside React State**

**Symptom:**
The URL does not change when navigating between "pages." The
browser back button does not work. Bookmarking a "page" shows
the wrong content.

**Root Cause:**
Developer used `useState` to track which view to show instead of
using a routing library. Navigation state belongs in the URL,
not in React state.

**Diagnostic Signal:**
Check the browser URL bar during navigation. If it stays static
while the view changes, routing is being done wrong.

**Fix:**
Install React Router (or TanStack Router). Move navigation
decisions into `<Route>` components. Use `useNavigate` for
programmatic navigation.

**Prevention:**
Establish from day one: URL state = React Router. Server state
= React Query. Local UI state = useState.

---

**Fetching Data in useEffect From Scratch**

**Symptom:**
Components have verbose loading/error/data state management.
Race conditions appear: older requests resolve after newer ones.
Data refetches on every component mount regardless of cache.

**Root Cause:**
Developer used `useEffect` + `useState` to manage what should be
server state. This is a known anti-pattern - `useEffect` for
data fetching requires solving caching, deduplication, refetch,
and race conditions manually.

**Diagnostic Signal:**
Look for `useEffect` with `fetch` inside and manual `isLoading`
state. This pattern re-invents 20% of React Query badly.

**Fix:**
Replace with React Query (`useQuery`, `useMutation`). Let the
library handle caching, refetching, background updates, and
race condition cancellation.

**Prevention:**
Treat server state and client state as different categories.
Use specialised libraries for each.

---

**Using React Context for All Global State (Security Concern)**

**Symptom:**
Sensitive data (auth tokens, user roles) is stored in React
Context and read by many components. A devtools injection or
XSS payload can read it.

**Root Cause:**
React Context makes data accessible to any component in the
tree, including potentially injected components. Sensitive state
should not live in easily inspectable JavaScript memory.

**Diagnostic Signal:**
Open React DevTools. Can you navigate the component tree and
read the context value containing sensitive data? If yes, that
data is accessible to any JavaScript running on the page.

**Fix:**
For auth tokens, use HTTP-only cookies (inaccessible to
JavaScript). For user roles, re-validate server-side on every
request. Do not rely on client-side context as a security
boundary.

**Prevention:**
Context is not a security boundary. It is a convenience for
passing data down the tree. Never store credentials in Context.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Frontend Complexity Problem` - the problem React was
  invented to solve; context for why React's scope is what it is
- `JavaScript Functions` - React components are JavaScript
  functions; the function model is the foundation

**Builds On This (learn these next):**
- `React Ecosystem Landscape` - the full map of what React
  combines with
- `Component` - the core primitive React provides
- `JSX` - React's syntax extension for describing UI

**Alternatives / Comparisons:**
- `Angular` - full framework that includes routing, HTTP, forms,
  and DI; opinionated where React is flexible
- `Next.js` - React with framework-level opinions added;
  bridges the gap between React's flexibility and Angular's
  structure
- `Vue.js` - progressive framework; closer to React in scope
  than Angular but with a more directive-based syntax

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A JavaScript library for building UI     │
│              │ components (view layer only)              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Confusion about React's scope leads to   │
│ SOLVES       │ reinventing routing/fetching badly        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ React's minimal scope is deliberate -    │
│              │ it delegates routing, state, and fetching │
│              │ to the best library for each job          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ You need a component model with full      │
│              │ ecosystem freedom                         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Team needs full framework with all        │
│              │ decisions pre-made (use Next.js / Angular)│
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Using React state to manage what belongs  │
│              │ in the URL, server cache, or form library │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Maximum flexibility vs framework overhead │
│              │ vs architectural decision cost            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "React builds components. For everything  │
│              │  else, you pick the right tool."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Ecosystem Landscape → Component → JSX     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. React is a library, not a framework - it handles the view
   layer only. Routing, data fetching, and styling require
   separate ecosystem choices.
2. React's minimal scope is a deliberate design choice that
   enables flexibility and keeps the runtime focused on fast
   reconciliation.
3. Treat different state categories differently: URL state
   belongs in the router, server state in React Query, local UI
   state in `useState`.

**Interview one-liner:**
"React is a UI library that handles one thing: rendering
components as a function of state. Everything else - routing,
data fetching, global state, styling - is delegated to the
ecosystem. That is a deliberate design choice that gives teams
flexibility but requires explicit architectural decisions."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Single-responsibility tools compose better than opinionated
monoliths. A library that does one thing exceptionally well is
more durable than a framework that does twelve things
adequately. The cost is that composition requires more
architectural decisions upfront.

**Where else this pattern appears:**
- Unix philosophy - small tools that do one thing well,
  composed via pipes; `grep`, `sed`, `awk` are React's
  philosophical cousins
- POSIX API design - the OS kernel does process and memory
  management; file systems, network stacks, and UIs are
  separate concerns
- Microservices - each service owns one domain; the
  orchestration layer is separate

**Industry applications:**
- Startups - React's flexibility means architectural decisions
  can be deferred or changed cheaply as the product evolves
- Large enterprises - React's ecosystem means best-in-class
  tooling for data fetching (React Query), state (Redux
  Toolkit), and testing (React Testing Library) can be
  adopted independently, replaced independently

---

### 💡 The Surprising Truth

React's "library, not a framework" positioning was itself
controversial when React was released. The dominant approach at
the time was Ember and Angular 1 - batteries-included,
opinionated full frameworks. Facebook's decision to release only
the view layer was seen by many as releasing half a product.
The conventional wisdom said developers wanted everything in one
package. React's success proved the opposite: developers would
happily assemble their own stack if each component was good
enough. This "composable ecosystem" model has since become
the dominant pattern for JavaScript - Vite, Prisma, tRPC, and
Tailwind are all single-purpose tools that compose into a stack,
none of which are frameworks.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** List exactly what React handles (component
   rendering, state, effects) and exactly what requires an
   external library (routing, HTTP, forms), with one concrete
   example of each.
2. **DEBUG** Given a React app where the browser back button
   breaks, identify whether the root cause is React state being
   used for navigation vs a React Router misconfiguration.
3. **DECIDE** For a new application, choose between raw React,
   Create React App, Next.js, and Remix by articulating the
   trade-offs for a given team size, project type, and
   deployment constraint.
4. **BUILD** Set up a React project with Vite, add React Router
   for navigation, and add React Query for data fetching -
   keeping the concerns cleanly separated in the codebase.
5. **EXTEND** Explain to a team coming from Angular why React's
   "batteries not included" model is a feature rather than a
   limitation, and describe when you would still recommend
   Angular or Next.js over raw React.

---

### 🧠 Think About This Before We Continue

**Q1.** React deliberately does not include a built-in data
fetching solution. But React Query, SWR, and Apollo each make
different trade-offs in how they handle caching, invalidation,
and optimistic updates. At 100 concurrent users editing shared
data, which caching model (query-key-based invalidation vs
subscription-based vs polling) leads to the fewest UI
inconsistencies, and why?
*Hint: Think about what "stale" means differently in each model
and what server-sent updates require.*

**Q2.** A new team is starting a React project. They are debating
whether to use raw React + Vite, or Next.js. The team has 5
engineers, 2 of whom are junior. The application is a B2B SaaS
dashboard that needs auth, routing, and API data. Which choice
minimises total time to first production feature and why?
*Hint: Consider decision overhead, convention vs configuration,
and onboarding cost as measurable inputs to the estimate.*

**Q3.** Build a tiny two-page React app (without Next.js) that
navigates between a list page and a detail page. The URL must
update correctly so the back button works and the page is
bookmarkable. Then add data fetching for the detail page using
`useEffect` + `useState`. Identify the three most dangerous
failure modes in your `useEffect` data fetching implementation
and fix them.
*Hint: Look up "race condition in useEffect," "stale closure in
useEffect cleanup," and "React 18 strict mode double invocation"
before building.*