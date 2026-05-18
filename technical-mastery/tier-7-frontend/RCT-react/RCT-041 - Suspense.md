---
id: RCT-041
title: Suspense
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-028, RCT-040, RCT-055
used_by: RCT-053, RCT-055, RCT-056, RCT-057
related: RCT-028, RCT-040, RCT-055
tags:
  - react
  - frontend
  - async
  - concurrent
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/react/suspense/
---

⚡ TL;DR - `<Suspense>` is React's boundary for
displaying a fallback UI while a child component is
"suspended" (waiting for async work to complete); today
it handles lazy component loading and data fetching in
React 18+ frameworks; it is the cornerstone of Concurrent
Mode because suspended components let React work on
other tasks while waiting.

| #041            | Category: React                                                                             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Error Boundaries, Code Splitting with React.lazy, useTransition and useDeferredValue        |                 |
| **Used by:**    | Concurrent Features, useTransition and useDeferredValue, React Server Components, Hydration |                 |
| **Related:**    | Error Boundaries, Code Splitting, useTransition                                             |                 |

---

### 🔥 The Problem This Solves

**IMPERATIVE LOADING STATE EVERYWHERE:**
Before Suspense, every async operation in a component
meant: `const [loading, setLoading] = useState(true)`.
Every component managed its own loading state. The result:

```jsx
// BEFORE: loading state scattered everywhere
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser(userId)
      .then((u) => {
        setUser(u);
        setLoading(false);
      })
      .catch((e) => {
        setError(e);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{user.name}</div>;
}
```

This loading state logic is repeated in every component
that fetches data. Nested components that each fetch data
cause "loading waterfalls" - parent loads → renders child
→ child starts loading → nested spinner shows.

Suspense moves loading state management OUT of individual
components and INTO a dedicated boundary in the component
tree, co-located with the UI layout, enabling declarative
loading states.

---

### 📘 Textbook Definition

**`<Suspense>`** - a React component that renders a
`fallback` prop while any child component is "suspended"
(throwing a promise signal indicating async work is in
progress). When all suspended children complete, Suspense
replaces the fallback with the actual content. Requires
either: (a) `React.lazy()` for code splitting, or (b) a
data-fetching library that integrates with the Suspense
protocol (React Query v5+, SWR with Suspense mode, Relay,
Next.js fetch in RSC, or React 18's `use()` hook).

---

### ⏱️ Understand It in 30 Seconds

```jsx
import { Suspense, lazy } from "react";
const SlowComponent = lazy(() => import("./SlowComponent"));

// Suspense: shows fallback while SlowComponent loads
function Page() {
  return (
    <div>
      <Header /> {/* Renders immediately */}
      <Suspense fallback={<Spinner />}>
        {/* Shows <Spinner /> while SlowComponent's JS loads */}
        {/* Shows <SlowComponent /> once loaded */}
        <SlowComponent />
      </Suspense>
      <Footer /> {/* Renders immediately */}
    </div>
  );
}

// Nested Suspense: independent loading states
function Dashboard() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      {/* Top-level skeleton while any dashboard child loads */}
      <Suspense fallback={<ChartSkeleton />}>
        <Charts /> {/* Independent: shows ChartSkeleton */}
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <DataTable /> {/* Independent: shows TableSkeleton */}
      </Suspense>
    </Suspense>
  );
}
```

---

### 🔩 First Principles Explanation

**THE SUSPENSE PROTOCOL:**

Suspense works via a "throw promise" contract:

```
1. Component during render calls a suspense-aware API
   (React.lazy, use(), or a Suspense-compatible cache)

2. If the data is not ready:
   The API throws a Promise (or an object with a
   `then` method) - this is an internal React signal,
   not a thrown error

3. React catches the thrown promise at the nearest
   Suspense boundary:
   - Renders the Suspense fallback
   - Sets up a listener: when the promise resolves,
     re-trigger the suspended subtree's render

4. Promise resolves:
   - React re-renders the subtree (from the suspended
     component)
   - Data is available (cached by the suspense-aware
     library)
   - Component renders successfully

5. If the promise REJECTS:
   - React re-throws the rejection
   - Nearest Error Boundary catches it
   - Without Error Boundary: unhandled error, React crashes
```

**Suspense vs try/catch vs useEffect:**

```
useEffect (imperative):
  - Loading state managed per component
  - Data fetching happens AFTER render (waterfall risk)
  - Easy to use, works everywhere

Suspense (declarative):
  - Loading state managed by boundary in the tree
  - Data can be initiated BEFORE render (in RSC, Relay)
  - Enables Concurrent Mode rendering of loading states
  - Requires library support (cannot use raw fetch with
    useState)
```

---

### 🧪 Thought Experiment

**THE LOADING WATERFALL PROBLEM:**
A page renders Parent → Child → Grandchild, each fetching
data:

- Parent fetches user profile (300ms)
- Child fetches user's posts (200ms) - starts AFTER Parent
- Grandchild fetches post comments (150ms) - starts AFTER Child

Total time: 650ms (sequential). This is a "request waterfall."

With Suspense + data libraries designed for it (Relay,
RSC): the server can initiate all three fetches in
parallel and stream responses. React renders each layer
as data arrives without sequential component-level fetch
waterfalls. The Promise-suspension model allows React to
know about pending work before it commits to DOM, enabling
coordinated loading states and parallel data initiation.

The waterfall problem is why Suspense at component level
(with `use()`) is not enough - you also need the data
fetching to START before component render. RSC and Relay
achieve this; typical `useEffect` fetching does not.

---

### 🧠 Mental Model / Analogy

> `<Suspense>` is like a restaurant's order ticket system.
> The kitchen (async work) is given all orders at once.
> While the food is cooking, the restaurant doesn't make
> the dining area stand still - other tables are served,
> drinks come out, other dishes are prepared.
>
> The `fallback` is the bread basket placed while you wait.
> When your main course is ready, the bread basket is
> cleared and the main course is placed.
>
> Without Suspense: every table's server stands frozen
> while waiting for that table's food, blocking everyone.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Suspense shows a fallback UI while children load. Pair
it with React.lazy for code splitting. Loading state
declared in the tree, not in each component.

**Level 2 (usage):**
Nest Suspense boundaries for independent loading areas.
Always add Error Boundary above Suspense to handle async
failures. The fallback should be a skeleton or spinner
matching the expected content size.

**Level 3 (data fetching):**
For data fetching (not just lazy loading), Suspense
requires a compatible library. React Query v5+ has
`suspense: true` option. SWR has `suspense` mode.
Raw `fetch()` + `useState` does NOT trigger Suspense.
React 18's `use(promise)` hook can read a promise in
render and integrates with Suspense natively.

**Level 4 (Concurrent Mode interaction):**
In Concurrent Mode (React 18), Suspense boundaries are
how React coordinates deferred rendering. `useTransition`
marks state updates as "transitions" - React keeps showing
the old UI while re-rendering in the background; if the
new UI suspends, the transition is held until the Suspense
resolves. This prevents the fallback from flickering
for very fast loads (under ~100ms).

**Level 5 (mastery):**
Suspense has three distinct use cases in 2024:
(1) Code splitting (React.lazy - stable since React 16.6)
(2) Client-side data fetching with `use()` (React 18, stable)
(3) Server-side streaming with RSC/SSR (Next.js App Router,
React 18 `renderToPipeableStream`)
In SSR streaming, Suspense boundaries define HTML streaming
chunks: the server sends the page shell with Suspense
fallbacks as placeholders. When each async boundary
completes, the server streams the resolved HTML and a
`<script>` tag that replaces the fallback in the browser.
This is React's progressive HTML streaming architecture.

---

### ⚙️ How It Works (Mechanism)

**SSR streaming with Suspense:**

```
Server receives GET /dashboard

React server renders the Suspense tree:
  <html>
    <body>
      <Header />  ← rendered immediately, sent
      <!--$?-->   ← Suspense placeholder (fallback sent)
      <Spinner /> ← fallback HTML sent as placeholder
      <!--/$-->
      <Footer />  ← rendered immediately, sent

Server: initiates async work for SlowData
        continues rendering other parts of the page
        streams HTML to the browser as it's ready

Browser receives: header + spinner placeholder + footer
Browser shows:    header + spinner + footer (immediately)

Server: SlowData resolves
Server: renders <SlowComponent data={data} />
Server: streams the resolved HTML chunk +
        inline <script>
          // Replace spinner placeholder with real content
          $RC("B:0", "S:0");  // React server protocol
        </script>

Browser: receives the chunk, executes the script
Browser: replaces spinner with real SlowComponent HTML
         (before any client JS runs for this component)
```

---

### 💻 Code Example

**BAD: Suspense without Error Boundary:**

```jsx
// BAD: No error boundary - any async failure crashes UI
function Page() {
  return (
    <Suspense fallback={<Spinner />}>
      <UserProfile userId={userId} />
      {/* If UserProfile's data fetch rejects: CRASH */}
      {/* React throws the error, nothing catches it */}
      {/* User sees a blank page */}
    </Suspense>
  );
}
```

**GOOD: Suspense with Error Boundary:**

```jsx
// GOOD: Error Boundary wraps Suspense
function SafeSuspense({ fallback, errorFallback, children }) {
  return (
    <ErrorBoundary fallback={errorFallback}>
      <Suspense fallback={fallback}>{children}</Suspense>
    </ErrorBoundary>
  );
}

function Page() {
  return (
    <SafeSuspense
      fallback={<ProfileSkeleton />}
      errorFallback={<p>Failed to load profile. Retry?</p>}
    >
      <UserProfile userId={userId} />
    </SafeSuspense>
  );
}
```

---

### 📊 Comparison Table

|                          | Suspense                       | useEffect + useState      | SuspenseList (experimental)   |
| ------------------------ | ------------------------------ | ------------------------- | ----------------------------- |
| Loading state location   | Tree (declarative)             | Component (imperative)    | Coordinated across boundaries |
| Waterfall prevention     | With Relay/RSC (not useEffect) | No                        | No                            |
| Error handling           | Error Boundary required        | try/catch or error state  | Error Boundary required       |
| SSR support              | Yes (React 18 streaming)       | Yes (renders during SSR)  | Experimental                  |
| Library support required | Yes (lazy or data library)     | No (works with raw fetch) | N/A                           |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Suspense works with useEffect-based data fetching"     | Suspense does NOT integrate with `useEffect` + `useState` data fetching. Only `React.lazy()`, `use()` (React 18), and libraries explicitly built for Suspense (React Query v5, SWR, Relay) trigger the Suspense protocol. `useEffect` runs after render, not during it.                                 |
| "Suspense prevents all loading spinners from appearing" | With `useTransition`, React can hold the current UI while the new tree suspends - this prevents spinner flicker for fast loads. But this requires wrapping the navigation/state update in `startTransition`. Without transitions, every navigation to a suspended route shows the fallback immediately. |
| "The fallback must be a spinner"                        | The fallback can be any React element: a skeleton screen, a low-fidelity version of the content, a blurred placeholder, or even null (to show nothing). Skeleton screens that match the shape of the content provide better perceived performance than spinners.                                        |
| "Suspense replaces Error Boundaries"                    | Suspense handles the loading state (promise pending). Error Boundaries handle the error state (promise rejected or render error). They are complementary, not interchangeable. Every Suspense boundary should have an Error Boundary ancestor.                                                          |

---

### 🚨 Failure Modes & Diagnosis

**Suspense Fallback Flickers for Fast Loads**

**Symptom:** A spinner briefly appears and disappears
on fast network connections, causing visual jank.

**Root Cause:** Suspense always shows the fallback
immediately when a child suspends. For fast loads, the
fallback appears for 50-100ms - enough to see a flash.

**Fix:** Use `useTransition` for navigations:

```jsx
const [isPending, startTransition] = useTransition();

// On navigate: wrap state update in startTransition
startTransition(() => setCurrentPage("dashboard"));
// React shows the OLD page (not the Suspense fallback)
// until DashboardPage finishes loading
// isPending is true during the transition (show a subtle indicator)
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `Error Boundaries` - required above Suspense for error handling
- `Code Splitting with React.lazy` - the primary use case for Suspense

**Builds On:**

- `useTransition and useDeferredValue` - prevent Suspense
  fallback flicker with concurrent transitions
- `React Server Components` - Suspense enables streaming SSR
  (HTML sent progressively as async data resolves)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ USAGE    │ <Suspense fallback={<Spinner/>}>children     │
│ REQUIRES │ React.lazy, use(), or Suspense-compat library│
│ ERROR    │ Always add ErrorBoundary above Suspense      │
├─────────────────────────────────────────────────────────┤
│ NEST     │ Multiple Suspense for independent boundaries │
│ SSR      │ React 18: streams HTML, replaces placeholders│
│ FLICKER  │ Prevent with useTransition for navigations   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Suspense shows `fallback` while children suspend.
   Works with `React.lazy`, `use()`, and Suspense-aware
   libraries. NOT with raw `useEffect` fetching.
2. Always pair with Error Boundary: Suspense handles
   loading, Error Boundary handles failure.
3. `useTransition` prevents fallback flicker: React holds
   old UI during transition instead of immediately showing
   the fallback.

**Interview one-liner:**
"`<Suspense>` is React's declarative loading boundary:
it shows a `fallback` while children are suspended
(waiting for async work - code loading or data fetching).
It works with `React.lazy()` for code splitting and with
Suspense-aware data libraries like React Query v5+ or
`use()`. Pair with Error Boundary for failures. In React
18, Suspense enables SSR streaming - the server sends
page shells with fallbacks and progressively replaces
them as async data resolves, improving Time to First Byte."

---

### 💎 Transferable Wisdom

Suspense is React's implementation of the "continuation"
concept from async programming theory. When a component
suspends, React captures the in-flight render (the
"continuation") and pauses it, renders other work, and
resumes the continuation when the async operation
completes. This is the same pattern as coroutines,
green threads, and cooperative multitasking. The
difference from async/await is that the suspension
boundary (Suspense) is explicit and separate from the
code that triggers it - the component that suspends
does not need to know where the fallback UI comes from.
This separation of concerns (async work from loading
UI) is a design pattern that appears in distributed
systems as well: circuit breakers show a fallback while
the downstream service is unavailable, bulk-head
patterns isolate failures to defined boundaries.

---

### 💡 The Surprising Truth

Suspense was announced at React Conf 2018 as the future
of data fetching in React. Six years later, the data
fetching vision is fully realised only in specific
frameworks (Next.js, Relay) - not in vanilla React apps
with `fetch()`. The reason: Suspense for data fetching
requires the library to start fetching BEFORE rendering,
which is architecturally incompatible with the traditional
component-mounts-then-fetches pattern. The React team
essentially announced a feature that required ecosystem
buy-in (from framework authors) to deliver its full
promise. For application developers, Suspense today (2024)
is primarily used for code splitting (React.lazy) and
via React Query/SWR/RSC rather than raw data fetching.

---

### ✅ Mastery Checklist

1. **DEMONSTRATE** nested Suspense boundaries: a dashboard
   with a charts section and a table section, each with
   an independent loading skeleton, using React Query
   with `suspense: true`.
2. **IMPLEMENT** the `useTransition` + Suspense pattern
   for route navigation: the current page stays visible
   while the next page loads, with a subtle loading
   indicator (no full-page spinner).
3. **SHOW** that raw `useEffect`+`fetch` does NOT trigger
   Suspense: a component using `useEffect` for data
   fetching inside a `<Suspense>` - the fallback never
   appears, loading is handled by the component itself.
4. **HANDLE** async errors in Suspense: force an async
   error, show that Suspense does not catch it, then
   add an Error Boundary and show the error fallback.
5. **EXPLAIN** how Next.js App Router uses Suspense for
   streaming: where are the Suspense boundaries in a
   `page.tsx` + `loading.tsx` + `error.tsx` file structure?

---

### 🧠 Think About This Before We Continue

**Q1.** The Suspense "throw promise" protocol is an
internal React mechanism (not a public API). In React 18,
the `use(promise)` hook provides a public API for reading
promises during render. How would you explain to a junior
developer why `throw promise` was chosen as the internal
mechanism rather than a dedicated lifecycle method or a
rendering flag?

**Q2.** Suspense boundaries define SSR streaming chunks.
A page with 10 independent Suspense boundaries could
stream 10 separate HTML chunks. However, each stream
boundary adds overhead (an HTTP chunk header, a script
tag). At what granularity should Suspense boundaries be
placed in an SSR app, and how would you measure the
optimal trade-off between parallelism (more Suspense
boundaries) and overhead (each boundary has cost)?

**Q3.** In a multi-tenant SaaS app, different tenants
have access to different modules. You want to dynamically
show/hide modules based on tenant configuration. Would
you use React.lazy for each module? What happens if
a tenant's configuration changes mid-session and a
previously loaded module is no longer available? How
does Suspense interact with conditional rendering
(mounting/unmounting lazy components)?
