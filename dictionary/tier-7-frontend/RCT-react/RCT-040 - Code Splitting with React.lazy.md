---
id: RCT-040
title: Code Splitting with React.lazy
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-028, RCT-059
used_by: RCT-041, RCT-059, RCT-060
related: RCT-028, RCT-041, RCT-059
tags:
  - react
  - frontend
  - performance
  - bundling
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /react/code-splitting-with-react-lazy/
---

# RCT-040 - CODE SPLITTING WITH REACT.LAZY

⚡ TL;DR - `React.lazy()` wraps a dynamic `import()` to
enable code splitting: the component's JavaScript is
loaded only when it is first rendered; wrap lazy components
in `<Suspense fallback={...}>` to handle the loading
state; the result is smaller initial bundle and faster
time-to-interactive by deferring non-critical code.

| #040 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Error Boundaries, Bundle Size Analysis and Tree Shaking | |
| **Used by:** | Suspense, Bundle Size Analysis and Tree Shaking, Core Web Vitals | |
| **Related:** | Error Boundaries, Suspense, Bundle Size Analysis | |

---

### 🔥 The Problem This Solves

**MONOLITHIC JAVASCRIPT BUNDLES:**
A large React single-page application ships all of its
JavaScript in one file (or a few files). Even pages the
user never visits (settings, admin panel, analytics
dashboard) are downloaded on the initial load. The result:
slow Time-to-Interactive (TTI) on low-end devices and
slow connections, even when the user just wants to see
the home page.

Code splitting divides the bundle into smaller chunks
that are loaded on demand. React.lazy + Suspense is the
built-in API for this: no separate library, direct
integration with React's rendering model, works with any
bundler that supports dynamic import (webpack, Vite,
esbuild).

---

### 📘 Textbook Definition

**`React.lazy()`** - a React API that enables code-split
lazy loading of components. Accepts a function that
returns a promise that resolves to a module with a
default export of a React component: `React.lazy(() =>
import('./MyComponent'))`. The component's JavaScript
chunk is loaded when React first attempts to render it.
While loading, React suspends the render and displays
the nearest `<Suspense fallback>`.

**Code Splitting** - the technique of dividing the
JavaScript bundle into multiple smaller files (chunks)
that are loaded dynamically. Dynamic `import()` is the
JavaScript standard mechanism; bundlers (webpack, Vite)
split the bundle at `import()` boundaries.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// BEFORE (monolithic): ALL components in one chunk
import Dashboard from './Dashboard';
import Settings from './Settings';
import AdminPanel from './AdminPanel';
// All 3 are downloaded on initial page load

// AFTER (code split): each loads independently
import { Suspense, lazy } from 'react';
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));
const AdminPanel = lazy(() => import('./AdminPanel'));

// Dashboard JS is loaded when <Dashboard /> first renders
// Settings JS is loaded when <Settings /> first renders
// AdminPanel JS is loaded only if user goes to /admin

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
}
```

---

### 🔩 First Principles Explanation

**HOW `React.lazy()` WORKS MECHANICALLY:**

```
1. React.lazy(() => import('./Component'))
   Creates a "lazy component" - a special React element type
   that wraps a promise.

2. First render attempt:
   React checks: is the promise resolved?
   - NO (first time): React THROWS the promise (Suspense mechanism)
   - Nearest Suspense boundary catches the thrown promise
   - Suspense renders its `fallback` prop
   - React sets up a listener: when promise resolves, re-render

3. Promise resolves (JS chunk loaded):
   React re-renders the Suspense boundary
   Now: React checks the promise → RESOLVED
   Renders the actual component with its props

4. Subsequent renders:
   Promise already resolved → renders immediately (no suspension)
```

**The Suspense protocol (throwing promises):**

```
This is React's internal mechanism:
  - Only React.lazy (and React.use in React 18) throw promises
  - Suspense boundaries catch thrown promises
  - Regular component errors go to Error Boundaries
  - If no Suspense boundary wraps a lazy component: React throws
    an error: "A React component suspended while rendering,
    but no fallback UI was specified."
```

---

### 🧪 Thought Experiment

**THE ADMIN PANEL CALCULATION:**
An admin panel component uses a rich text editor library
(300KB), a complex data grid (200KB), and admin-specific
charts (150KB). That is 650KB of JavaScript only admin
users ever see.

Without code splitting: all 650KB is in the main bundle.
Every user (99% non-admin) downloads 650KB on first load.

With code splitting:
```jsx
const AdminPanel = lazy(() => import('./AdminPanel'));
```
The 650KB chunk is only downloaded when a user navigates
to /admin. For the 99% of non-admin users: 650KB saved
from initial load. TTI improvement: ~2-3 seconds on
slow 3G.

Code splitting is highest-impact for routes and rarely-
visited pages - not for small components that are always
visible on initial load.

---

### 🧠 Mental Model / Analogy

> `React.lazy()` is like a restaurant that does not cook
> a dish until you order it (on-demand), rather than
> preparing all 50 dishes when the kitchen opens (upfront).
> The `<Suspense fallback>` is the "your food is being
> prepared" message shown while you wait.
>
> Without code splitting: the kitchen prepares the full
> menu every morning (all JavaScript loaded upfront),
> including dishes 99% of customers never order (admin
> dashboard, rarely-visited pages).
>
> The cost of waiting (loading the chunk) is paid only by
> users who actually need the dish - and only once (cached
> after first load).

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Large JavaScript bundles slow initial page load. Lazy
loading loads component code only when needed. React.lazy
+ Suspense is the built-in mechanism.

**Level 2 (usage):**
Use lazy loading at route boundaries first - that is the
highest impact (each route = one chunk). Wrap in Suspense
with a meaningful fallback. Add Error Boundary to handle
network failures during chunk load.

**Level 3 (chunk strategy):**
Bundlers (webpack/Vite) split at dynamic import()
boundaries. Each `lazy(() => import('./X'))` creates a
separate chunk. Multiple lazy imports from the same
chunk-worthy module can be grouped with webpack's
`webpackChunkName` comment or Vite handles it automatically
based on dependencies.

**Level 4 (preloading and prefetching):**
Code splitting defers loading until needed. But for
predictable navigation (hover over a link), you can
prefetch the chunk before the user clicks:
```jsx
// Start loading the chunk on hover (before click)
const onHover = () => import('./Settings');  // prefetch
```
Alternatively, use `<link rel="prefetch">` in HTML for
critical next-page chunks. The chunk is downloaded in
the background and cached - by the time the user clicks,
it is ready.

**Level 5 (mastery):**
React.lazy is constrained: it only accepts default exports
and only works at component level (not individual hooks
or utilities). For finer control, use dynamic import()
directly with useState for loading state. In React Server
Components (RSC), code splitting happens differently:
server components are never sent to the client (no bundle
impact), so lazy loading is only needed for client
components. In Next.js: `next/dynamic` wraps React.lazy
with SSR support and server-side rendering of the fallback.
For library code splitting (moment.js → dayjs), that
requires tree-shaking and build configuration, not
React.lazy.

---

### ⚙️ How It Works (Mechanism)

**Suspense + Error Boundary integration:**

```jsx
// PRODUCTION PATTERN: lazy + Suspense + Error Boundary
import { Suspense, lazy } from 'react';
import ErrorBoundary from './ErrorBoundary';
import PageSpinner from './PageSpinner';

const DashboardPage = lazy(() => import('./DashboardPage'));
const SettingsPage = lazy(() => import('./SettingsPage'));

// ChunkErrorBoundary: handles network failure on chunk load
// (user goes offline just as chunk starts loading)
function LazyRoute({ children }) {
  return (
    <ErrorBoundary
      fallback={<p>Failed to load page. Check connection.</p>}
    >
      <Suspense fallback={<PageSpinner />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

function App() {
  return (
    <Routes>
      <Route
        path="/dashboard"
        element={
          <LazyRoute>
            <DashboardPage />
          </LazyRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <LazyRoute>
            <SettingsPage />
          </LazyRoute>
        }
      />
    </Routes>
  );
}
```

---

### 💻 Code Example

**BAD: Named export with React.lazy (does not work):**

```jsx
// BAD: React.lazy requires DEFAULT export
// If Component is a named export, this silently fails
const Settings = lazy(() => import('./Settings'));
// ERROR: Element type is invalid - module has no default export

// The Settings.js file:
export function Settings() { return <div>Settings</div>; }
// No default export → React.lazy cannot find the component
```

**GOOD: Re-export as default if needed:**

```jsx
// Option 1: Add default export to the component file
export default function Settings() {
  return <div>Settings</div>;
}
const Settings = lazy(() => import('./Settings'));  // works

// Option 2: Wrap the named import in a re-export
const Settings = lazy(async () => {
  const module = await import('./Settings');
  return { default: module.Settings };  // adapt named → default
});
```

**Production: Retry on network failure:**

```jsx
// Retry loading the chunk on failure
function lazyWithRetry(fn, retries = 3) {
  return lazy(() => {
    const attempts = Array.from({ length: retries }, (_, i) => i);
    return attempts.reduce(
      (p) => p.catch(() => fn()),
      fn()
    );
  });
}

const Dashboard = lazyWithRetry(() => import('./Dashboard'));
// On flaky networks: automatically retries chunk load
// before showing an error to the user
```

---

### 📊 Comparison Table

| | React.lazy | next/dynamic | Manual dynamic import |
|---|---|---|---|
| SSR support | No (client-only) | Yes (SSR + CSR) | Manual setup |
| Default export required | Yes | No (named export supported) | No |
| Suspense integration | Built-in | Optional | Manual |
| Loading state | Suspense fallback | `loading` prop | useState |
| Error handling | Error Boundary | Error Boundary | try/catch |
| Preload support | Manual | `next/dynamic` preloading | Manual |
| Use case | CSR React apps | Next.js apps | Non-component JS splitting |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "React.lazy is only for large libraries" | React.lazy is most impactful for route-level splitting (whole pages). Small UI components (buttons, icons) are not worth splitting - the HTTP request overhead and waterfall effect of loading a tiny chunk can be worse than including it in the main bundle. |
| "Code splitting always improves performance" | Code splitting trades initial load time for per-route load time. If you split a component that 90% of users visit immediately, you have added a loading spinner without reducing perceived load time. The gain is when deferred code is rarely or predictably accessed. |
| "Suspense handles network errors for lazy components" | Suspense handles the loading state only. Network errors (chunk fails to load) throw an error - they must be caught by an Error Boundary. Without an Error Boundary above the Suspense, a failed chunk load crashes the UI with an unhandled error. |
| "React.lazy works the same on the server (SSR)" | React.lazy does not support server-side rendering. If a lazy component is rendered on the server, it throws. Use `next/dynamic` (Next.js) or `@loadable/component` for SSR-compatible code splitting. |

---

### 🚨 Failure Modes & Diagnosis

**Chunk Load Failure - White Screen**

**Symptom:** Navigating to a route shows a white screen
or React error overlay with "Loading chunk X failed" or
"Network request failed."

**Root Cause:** Network failure mid-navigation or chunk
file not found (e.g., new deployment with new chunk
filenames while user had old HTML).

**Fix:** Wrap lazy imports in Error Boundary:
```jsx
// Add error boundary above Suspense for every lazy route
<ErrorBoundary fallback={<p>Failed to load. Refresh page.</p>}>
  <Suspense fallback={<Spinner />}>
    <LazyComponent />
  </Suspense>
</ErrorBoundary>
```
Also consider auto-reload on stale deployment:
```jsx
// In the Error Boundary, check if it is a chunk error
// and offer "refresh" or auto-reload
if (error.name === 'ChunkLoadError') {
  window.location.reload();
}
```

---

**All Lazy Components Loading at the Same Time (Waterfall)**

**Symptom:** Navigating to a deeply nested page triggers
sequential chunk loads (spinner appears multiple times
in succession).

**Root Cause:** Parent lazy component loads → renders
child lazy component → child starts loading. Sequential
rather than parallel.

**Fix:** Group related components into one chunk (co-
locate them in the same dynamic import) or use route-level
splitting instead of component-level splitting to avoid
waterfalls.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Error Boundaries` - required to handle chunk load
  failures gracefully
- `Bundle Size Analysis and Tree Shaking` - understanding
  bundle composition to identify what to split

**Builds On:**
- `Suspense` - the React mechanism that lazy loading
  integrates with for loading state management
- `Core Web Vitals in React` - code splitting directly
  impacts LCP and TTI metrics

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BASIC USAGE │ lazy(() => import('./Component'))          │
│ REQUIREMENT │ Default export only                       │
│ LOADING     │ Wrap in <Suspense fallback={<Spinner/>}>  │
│ ERRORS      │ Wrap in <ErrorBoundary> above Suspense    │
├──────────────────────────────────────────────────────────┤
│ BEST SPLIT  │ Route-level (highest impact)              │
│ AVOID SPLIT │ Small components rendered on initial load │
├──────────────────────────────────────────────────────────┤
│ SSR         │ Does NOT work - use next/dynamic          │
│ RETRY       │ Wrap factory fn in retry logic            │
│ PRELOAD     │ import('./Component') on hover/anticipate │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `React.lazy(() => import('./X'))` defers loading X's
   JavaScript until X is first rendered. Requires a
   `<Suspense>` boundary above it.
2. Error Boundary is mandatory with lazy - network failures
   on chunk load are errors, not loading state.
3. Route-level splitting gives the highest impact. Don't
   split tiny always-visible components.

**Interview one-liner:**
"`React.lazy()` wraps a dynamic `import()` to enable code
splitting: the component's JS chunk is downloaded only
when the component first renders. Wrap in `<Suspense
fallback>` for the loading state and `<ErrorBoundary>`
for network failures. Best applied at route boundaries
where each page is a separate chunk - the initial bundle
shrinks to only the code needed for the landing page,
improving Time-to-Interactive. Does not support SSR; use
`next/dynamic` for server-side rendering."

---

### 💎 Transferable Wisdom

Code splitting is an instance of lazy initialisation:
defer expensive work until it is actually needed. This
pattern recurs in software engineering: lazy database
connections (pool allocates connection on first use),
lazy loading in ORM (Hibernate's `FetchType.LAZY`), lazy
evaluation in functional languages (Haskell's thunks),
virtual memory paging (OS loads memory pages on access).
The trade-off is always the same: better upfront resource
usage at the cost of latency on first access. The
optimisation is the same: predict which resources will be
needed and prefetch them before they are needed
(prefetching, eager loading when access is predictable).
React.lazy's prefetch pattern (`import('./X')` on hover)
is the same principle as database connection warming or
Hibernate's `JOIN FETCH` for predictable access patterns.

---

### 💡 The Surprising Truth

The JavaScript dynamic `import()` syntax (the foundation
of React.lazy) was standardised in ES2020 - relatively
recently for a language feature. Before `import()`, code
splitting required bundler-specific APIs (webpack's
`require.ensure()`, SystemJS) that were non-portable.
`React.lazy()` was introduced in React 16.6 (2018), two
years before `import()` was formally standardised -
React was betting on the proposal before it was official.
The `<Suspense>` mechanism that lazy uses (throwing
promises to signal loading state) is internal to React
and deliberately not a public API - it is possible React
will change this mechanism in a future version. React
18's `use()` hook provides a public, stable way to
consume promises inside components, and may eventually
replace the internal throwing-promise mechanism.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** route-based code splitting in a React
   Router app: each route as a lazy component, shared
   Suspense + Error Boundary wrapper. Verify in the
   Network tab that each chunk loads only when its route
   is visited.
2. **HANDLE** the named export case: a library exports
   a named component (not default). Write the wrapper
   function to adapt it for `React.lazy()`.
3. **IMPLEMENT** a prefetch on hover: a navigation link
   that starts loading the target route's chunk when the
   user hovers (before clicking). Measure the time
   difference in the Network tab.
4. **HANDLE** chunk load failure: force a network error
   (offline mode in DevTools), navigate to a lazy route,
   observe the white screen, then add Error Boundary +
   retry + reload logic.
5. **COMPARE** bundle analysis before and after code
   splitting using webpack-bundle-analyzer or Vite's
   rollup-plugin-visualizer. Quantify the initial bundle
   size reduction.

---

### 🧠 Think About This Before We Continue

**Q1.** React.lazy uses the Suspense mechanism internally
(throws a promise). In React 18, `use(promise)` is a
new hook for consuming promises directly in render. How
does `use()` differ from the internal Suspense throwing
mechanism, and what does this mean for the future of
React.lazy? Could `React.lazy` be replaced by a simpler
pattern using `use()`?

**Q2.** A large enterprise React app has 200 routes.
Each route is code-split with `React.lazy`. This means
200 separate HTTP requests for chunk files on navigation.
With HTTP/2 (multiplexed connections), is this still
a problem? What is the optimal chunk granularity - one
chunk per route, or grouped chunks by feature domain?
How would you measure the right granularity?

**Q3.** React Server Components (RSC) mean that server-
rendered components never appear in the client bundle -
zero JavaScript shipped for them. Does this make
client-side code splitting with `React.lazy` redundant
for Next.js 14+ apps using RSC? Or is there still a
use case for `React.lazy` (and `next/dynamic`) alongside
RSC?