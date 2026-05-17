---
id: RCT-012
title: ReactDOM Rendering
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-011
used_by: RCT-040, RCT-041, RCT-057
related: RCT-011, RCT-040, RCT-057
tags:
  - react
  - frontend
  - internals
  - rendering
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /react/reactdom-rendering/
---

# RCT-012 - REACTDOM RENDERING

⚡ TL;DR - ReactDOM is the bridge between React's virtual
DOM and the browser's real DOM; `createRoot().render()` is
how a React application mounts, and understanding this
bridge explains hydration, portals, and Concurrent Mode.

| #012 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Component, Virtual DOM | |
| **Used by:** | Code Splitting with React.lazy, Suspense, Hydration and Dehydration | |
| **Related:** | Virtual DOM, Code Splitting with React.lazy, Hydration and Dehydration | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
React's component model produces a description of what the
UI should look like (virtual DOM). But a description is
not a real DOM. Something must translate that description
into actual HTML elements that the browser can display.
That bridge is ReactDOM.

React itself is intentionally platform-agnostic. The same
React components can render to a browser DOM (via
`react-dom`), to native mobile views (via `react-native`),
to a string for server-side rendering (via
`react-dom/server`), to PDF (via `@react-pdf/renderer`),
or to a 3D canvas (via `react-three-fiber`). ReactDOM is
the specific renderer for the browser.

---

### 📘 Textbook Definition

**ReactDOM** is the package (`react-dom`) that provides
browser-specific DOM rendering capabilities for React.
`ReactDOM.createRoot(container)` creates a root from which
React manages a DOM container. Calling `.render(element)` on
that root mounts the React component tree and begins
lifecycle management. ReactDOM is responsible for: committing
virtual DOM changes to real DOM nodes, managing the event
delegation system, and handling browser-specific
considerations (SVG namespaces, input value management,
focus preservation). In React 18, `createRoot` replaced the
legacy `ReactDOM.render` API to enable Concurrent features.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`createRoot(document.getElementById('root')).render(<App />)`
is the entry point that connects your React component tree
to the real browser DOM.

**One analogy:**
> React is a film script. ReactDOM is the production team
> that turns the script into a real movie (DOM). The same
> script (React components) can be produced in different
> formats: cinema (browser DOM), home video (server HTML
> string), or stage play (native app). ReactDOM is the
> specific production team for cinema.

**One insight:**
The `root` element in your `index.html` (`<div id="root">`)
is the boundary between React-managed DOM and non-React
DOM. Everything inside the root is owned by React.
Everything outside it can be manipulated conventionally.
Portals (via `createPortal`) are the exception: they render
React content outside the root container while keeping it
in React's component tree.

---

### 🔩 First Principles Explanation

**REACT 18 ENTRY POINT:**

```jsx
// index.tsx (entry file for a React 18 app)
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

**WHAT EACH PART DOES:**

```
createRoot(container)
  - Tells ReactDOM "manage this DOM element"
  - Creates internal Fiber root (work unit tree root)
  - Returns a root object with .render() and .unmount()
  - Enables Concurrent features (React 18)

root.render(<App />)
  - First call: mounts the component tree
  - Subsequent calls (rare): updates the root element
  - React manages all updates via state/props from here

StrictMode
  - Development-only wrapper
  - Double-invokes render functions to detect impurity
  - Double-invokes effects to detect cleanup issues
  - No production behaviour change
```

**LEGACY API (React 17 and below):**

```jsx
// Old API - do not use for new code
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));
// Problems: does not support Concurrent features
// React 18 will work but shows deprecation warning
// Will be removed in a future React major version
```

---

### 🧪 Thought Experiment

**SETUP:**
A multi-tenant dashboard where each "widget" is an
independent React application rendered into its own
container in a legacy HTML page.

**THE CHALLENGE:**
The page is a legacy jQuery application with multiple
`<div>` containers. Each container should host an
independent React widget with its own state and lifecycle.
The widgets should not share a React root (different teams,
different deployment cycles).

**THE SOLUTION:**

```jsx
// Widget A team's code:
const rootA = createRoot(
  document.getElementById('widget-metrics')
);
rootA.render(<MetricsWidget />);

// Widget B team's code:
const rootB = createRoot(
  document.getElementById('widget-notifications')
);
rootB.render(<NotificationsWidget />);

// Two independent React roots coexist on the same page.
// Each has its own Fiber tree, event system, and context.
// widget-metrics state does not affect widget-notifications.
```

This is the "micro-frontend" pattern at its simplest: each
team owns a root and a container.

---

### 🧠 Mental Model / Analogy

> `createRoot` creates a React universe. Everything inside
> the container lives in React's world: the virtual DOM,
> event delegation, state management, Concurrent Mode. The
> container `<div>` is the event horizon - the boundary
> between React's universe and the rest of the browser.

```
HTML Page
+-------------------------------------------------+
|  <body>                                         |
|    <nav id="legacy-nav">                        |
|      <- Regular DOM, not React-managed          |
|    </nav>                                       |
|                                                 |
|    <div id="root">                              |
|      <- React's universe starts here            |
|      <- All DOM inside managed by React         |
|      <- Events bubble to React's root listener  |
|    </div>                                       |
|                                                 |
|    <div id="portal-target">                     |
|      <- Portals can render React content here   |
|      <- Still part of React's tree (events)     |
|      <- But physically outside #root            |
|    </div>                                       |
+-------------------------------------------------+
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ReactDOM is what puts your React app on the webpage.
You point it at an empty HTML element and tell it
to render your `<App>` component there. Everything else
is managed automatically.

**Level 2 - How to use it (junior developer):**
`createRoot(domElement).render(<App />)` is the whole entry
point. It goes in `index.tsx` (or `main.tsx` in Vite).
Wrap your app in `<StrictMode>` to catch common mistakes
during development.

**Level 3 - How it works (mid-level engineer):**
`createRoot` initialises a Fiber root - React's internal
data structure that tracks the component tree. `.render()`
triggers the initial reconciliation: React calls all
components, builds the full Fiber tree, and commits the
full DOM tree to the container. Subsequent updates come
from `setState` and re-render through the same Fiber tree.

**Level 4 - Why it was designed this way (senior/staff):**
React 18's `createRoot` (vs legacy `ReactDOM.render`) was
necessary to enable Concurrent Mode. The legacy `render`
API was synchronous - it blocked the main thread for the
entire initial render. `createRoot` allows React to split
work into units (Fiber tasks), schedule them, and yield
control to the browser's rendering pipeline for high-
priority user interactions.

**Level 5 - Mastery (distinguished engineer):**
ReactDOM is one of several React renderers. The React team
maintains a "React Reconciler" package that enables custom
renderer development. `react-native` is a renderer for
native mobile. `react-art` for canvas/SVG.
`react-dom/server` for server-side HTML strings.
Each renderer speaks to a different output target while
sharing the same React component model. Understanding
this explains why React Server Components can run their
render on the server (server renderer) but their client
component descendants run in the browser (client renderer):
they use different renderers for different parts of the tree.

---

### ⚙️ How It Works (Mechanism)

**React's event delegation model:**

```
React 17+: Events are delegated to the root container
  (not to document, as in React 16 and below)

User clicks a button inside #root:
  1. Click event bubbles up the DOM tree
  2. Reaches the #root container
  3. React's synthetic event handler intercepts it
  4. React dispatches to the correct component's onClick
  5. React batches any resulting state updates

Why at the root container (not document)?
  - Allows multiple React roots on one page without
    event system interference
  - Makes micro-frontend isolation possible
```

**Portals and event bubbling:**

```jsx
// Portal renders in a different DOM location
// But events still bubble through React's component tree
import { createPortal } from 'react-dom';

function Modal({ children, onClose }) {
  return createPortal(
    <div className="modal">
      <button onClick={onClose}>Close</button>
      {children}
    </div>,
    document.getElementById('modal-root') // outside #root
  );
}

// A click on the Close button:
// DOM bubble: modal-root -> body -> document
// React bubble: Modal -> its parent in REACT tree
// (not the DOM tree parent - the component tree parent)
// -> React's event system follows the component tree,
//    not the DOM tree, for portal children
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INITIAL MOUNT:**

```
index.html:
  <div id="root"></div>

main.tsx:
  const root = createRoot(document.getElementById('root'));
  root.render(<StrictMode><App /></StrictMode>);

React processes:
  1. Initialise Fiber root linked to #root DOM element
  2. Create Fiber node for StrictMode
  3. Create Fiber node for App
  4. Call App() -> get JSX -> traverse component tree
  5. Build full Fiber tree (work loop)
  6. Commit: create DOM nodes, insert into #root
  7. Run useEffect callbacks

Browser:
  Paints the initial UI
```

**SUBSEQUENT UPDATES:**

```
State change in App (or any descendant):
  1. React marks affected Fiber node as dirty
  2. Schedules work (in microtask queue)
  3. Processes dirty nodes in work loop
  4. Commits only the affected DOM mutations
  5. Runs effects
```

---

### 💻 Code Example

**Example 1 - BAD: Legacy ReactDOM.render (pre-React 18):**

```jsx
// BAD: Legacy API - no Concurrent features, deprecated
import ReactDOM from 'react-dom';

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
// This API:
// - Blocks main thread during render
// - Does not support useTransition or Suspense streaming
// - Will be removed in React 19+
// - Shows console warning in React 18+
```

**Example 2 - GOOD: React 18 createRoot:**

```jsx
// GOOD: Modern entry point for React 18
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <StrictMode>
    <App />
  </StrictMode>
);
// createRoot enables:
// - Concurrent features (useTransition, Suspense)
// - Automatic batching of all state updates
// - Interruptible rendering
```

**Example 3 - PRODUCTION: Programmatic unmount for
micro-frontend cleanup:**

```tsx
import { createRoot, Root } from 'react-dom/client';

// Registry pattern for micro-frontends
const roots = new Map<string, Root>();

export function mount(
  containerId: string,
  element: React.ReactElement
): void {
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`Container #${containerId} not found`);
  }
  const root = createRoot(container);
  root.render(element);
  roots.set(containerId, root);
}

export function unmount(containerId: string): void {
  const root = roots.get(containerId);
  if (root) {
    root.unmount(); // Runs all cleanup (useEffect cleanup)
    roots.delete(containerId);
  }
}

// Usage:
mount('widget-metrics', <MetricsWidget />);
// Later, when navigating away:
unmount('widget-metrics');
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "react-dom is the same as react" | They are separate packages. `react` provides the component model, hooks, and virtual DOM. `react-dom` is the browser-specific renderer. You import hooks from `react`, not `react-dom`. |
| "You can only have one React root per page" | Multiple independent React roots can coexist on a page. Each has its own Fiber tree and event system. This is the foundation of micro-frontend patterns with React. |
| "StrictMode affects production behaviour" | StrictMode is entirely a development-only tool. It has zero effect on production builds. It calls render functions and effects twice (discarding the first) to detect side effects. |
| "ReactDOM.render() is deprecated in React 18" | It is not removed, but it is legacy. It shows a deprecation warning and does not support Concurrent features. The recommendation is to migrate to `createRoot()` before the eventual removal. |

---

### 🚨 Failure Modes & Diagnosis

**Hydration Mismatch Errors**

**Symptom:**
Console error: "Hydration failed because the initial UI
does not match what was rendered on the server."
Parts of the UI flash or show incorrect initial state.

**Root Cause:**
The server-rendered HTML (produced by
`renderToString` or `renderToPipeableStream`) does not
match what React's client-side render produces on
`hydrateRoot`. Common causes: server/client timezone
differences, random IDs, `typeof window !== 'undefined'`
checks producing different results.

**Diagnostic Command:**
```bash
# The console error will indicate which component
# produced the mismatch and what the expected vs actual
# HTML was. In Next.js, hydration errors typically show:
# "Text content did not match. Server: '...' Client: '...'"
# Check for: Date.now(), Math.random(), window checks,
# browser-only APIs used during server render.
```

**Fix:**
Ensure server and client render identical output.
Move browser-only code to `useEffect` (runs only on client
after hydration). Use `suppressHydrationWarning` on
elements where differences are expected (e.g., timestamps).

---

**Calling createRoot on a Server**

**Symptom:**
Error: "document is not defined" during server-side
rendering or testing.

**Root Cause:**
`createRoot` requires a browser DOM. It is called in
a context where `document` is not available (Node.js,
Jest without jsdom, Deno).

**Diagnostic Command:**
```bash
# Check your test environment configuration:
# jest.config.ts -> testEnvironment: 'jsdom'
# vitest.config.ts -> environment: 'jsdom'
# Without jsdom, document is undefined in tests.
```

**Fix:**
Add jsdom as the test environment. For SSR, use
`react-dom/server` APIs (`renderToString`,
`renderToPipeableStream`) instead of `createRoot`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Component` - the tree of components that ReactDOM renders
- `Virtual DOM` - what ReactDOM commits to the real DOM

**Builds On This (learn these next):**
- `Code Splitting with React.lazy` - lazy loading components
  within the ReactDOM rendering tree
- `Suspense` - declarative loading states in the ReactDOM tree
- `Hydration and Dehydration` - the SSR-to-client handoff
  that uses `hydrateRoot` instead of `createRoot`

**Alternatives / Comparisons:**
- `react-dom/server` - server-side rendering counterpart;
  produces HTML strings or streams, not live DOM nodes
- `React Native` - alternative renderer for iOS/Android
  native widgets; same React components, different renderer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bridge between React's vDOM and the     │
│              │ browser's real DOM                      │
├──────────────┼───────────────────────────────────────────┤
│ ENTRY POINT  │ createRoot(el).render(<App />)          │
│              │ in main.tsx / index.tsx                 │
├──────────────┼───────────────────────────────────────────┤
│ STRICT MODE  │ <StrictMode> wraps App in dev;          │
│              │ zero production impact                  │
├──────────────┼───────────────────────────────────────────┤
│ EVENTS       │ Delegated to root container (React 17+) │
│              │ not to document                         │
├──────────────┼───────────────────────────────────────────┤
│ PORTALS      │ createPortal(jsx, container) renders    │
│              │ outside root but stays in React tree    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Legacy ReactDOM.render() for new code   │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Manipulating DOM inside the React root  │
│              │ without React's knowledge               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "createRoot().render() is how React     │
│              │  meets the browser DOM."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hydration -> Code Splitting -> Suspense │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `createRoot(el).render(<App />)` is the React 18
   entry point. It replaces legacy `ReactDOM.render()`.
   Without `createRoot`, Concurrent features do not work.
2. `<StrictMode>` is development-only. It double-invokes
   render functions and effects to catch impure code.
   It has zero production impact - always use it.
3. Multiple React roots can coexist on a page. Each is
   independent. This is the foundation for embedding React
   into legacy apps or building micro-frontends.

**Interview one-liner:**
"ReactDOM is the browser-specific renderer for React.
`createRoot(container).render(<App />)` is the React 18
entry point - it creates a Fiber root linked to a DOM
container, enabling Concurrent features like `useTransition`
and Suspense streaming. React 17's `ReactDOM.render()` is
legacy and does not support Concurrent Mode. I always wrap
the app in `<StrictMode>` during development for safety
without production cost."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the rendering model from the rendering target.
React's component model is renderer-agnostic. ReactDOM is
one renderer. This separation allows the same component
code to target browsers, native apps, servers, and custom
outputs. When designing systems with rendering concerns,
consider the same separation: define the "what to render"
as data, and the "how to render" as a pluggable layer.

**Where else this pattern appears:**
- Kotlin Multiplatform - business logic shared across
  Android/iOS; platform-specific UI adapters are separate
- Qt - same C++ UI logic targets Windows/Mac/Linux/embedded
- LLVM - same IR (intermediate representation) compiles to
  x86, ARM, WebAssembly via separate backends

---

### 💡 The Surprising Truth

React's event system has never used the browser's native
event bubbling at the DOM level for user events. Instead,
React attaches a single listener at the root container
(or `document` in React 16 and below) and handles all
events via synthetic event objects. This is why React can
guarantee event behavior consistency across browsers
(including old IE), why event pooling (now removed) was
possible, and why events in portals bubble through the
React component tree rather than the DOM tree. When you
call `event.stopPropagation()` in React, you stop
propagation in React's synthetic event system - but the
native DOM event has already reached the root listener;
it has not been stopped in the DOM.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe to a developer from an Angular
   background how React's `createRoot` compares to
   Angular's `bootstrapApplication` and what the conceptual
   equivalent of the root container is in each.
2. **DEBUG** Given a hydration mismatch error, identify
   the type of code (window check, Date.now(), Math.random())
   that caused it and fix it to produce identical server
   and client output.
3. **BUILD** Implement a micro-frontend mount/unmount
   registry that creates independent React roots for
   two different widgets on a legacy page and properly
   calls `root.unmount()` on navigation.
4. **EXPLAIN** Describe why React events delegate to the
   root container (not to each DOM element) and what
   the implication is for `stopPropagation()` in a portal
   versus in the main root.
5. **DECIDE** When would you use `hydrateRoot` instead of
   `createRoot`, and what breaks if you use `createRoot`
   on a server-rendered HTML page?

---

### 🧠 Think About This Before We Continue

**Q1.** React 17 changed event delegation from `document`
to the root container. Before this change, if you had two
React roots on a page (e.g., React 15 and React 17 running
side by side for a gradual migration), what problems could
arise from both attaching listeners to `document`? How
did the React 17 change specifically address this?
*Hint: Event order, stopPropagation across versions.*

**Q2.** `createRoot` returns an object with `.render()` and
`.unmount()`. If you call `.render()` multiple times on the
same root with different elements, React updates the tree
instead of creating a new one. What is the use case for
calling `.render()` multiple times on the same root, and how
does this differ from updating state inside the component?
*Hint: Theme changes at the application level, A/B test
variant switching.*

**Q3.** React's `StrictMode` double-invokes component
functions and effects. If you have a `useEffect` that
opens a WebSocket connection, StrictMode will open it
twice and close it once (running cleanup from the first
invocation). What does this reveal about the contract of
`useEffect`, and what would a correctly implemented
WebSocket effect look like under StrictMode?
*Hint: Every setup in useEffect must have a corresponding
cleanup that fully reverses the setup.*