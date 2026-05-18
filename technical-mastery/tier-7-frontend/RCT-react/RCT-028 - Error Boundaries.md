---
id: RCT-028
title: Error Boundaries
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-006, RCT-010, RCT-047
used_by: RCT-040, RCT-052, RCT-063
related: RCT-041, RCT-047, RCT-048
tags:
  - react
  - frontend
  - error-handling
  - resilience
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/react/error-boundaries/
---

⚡ TL;DR - Error Boundaries are class components with
`static getDerivedStateFromError()` and `componentDidCatch()`
that catch render-phase JavaScript errors in their subtree
and display a fallback UI instead of crashing the whole
app - they are the React equivalent of a try/catch for
the component tree, but hooks cannot replace them (class
components only, as of React 18).

| #028            | Category: React                                                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Class vs Functional Components, React Components, Class Components to Hooks Migration |                 |
| **Used by:**    | Code Splitting with lazy/Suspense, Concurrent Features, v18 Migration                 |                 |
| **Related:**    | Suspense, Class Components, Testing React                                             |                 |

---

### 🔥 The Problem This Solves

**ENTIRE APP CRASHES ON ANY RENDER ERROR:**
Before React 16, an unhandled JavaScript error during
rendering corrupted React's internal state and produced
cryptic errors. React continued trying to render the
broken tree, often displaying garbage UI or a blank screen.

From React 16 onwards, unhandled render errors unmount
the entire component tree - the whole app disappears and
shows nothing. This is "fail fast" behaviour that prevents
corrupted UI from being shown to users. But it means one
component's rendering bug takes down the entire app.

Error Boundaries let you contain the damage: only the
subtree inside the Error Boundary unmounts on error. The
rest of the app continues working. You display a fallback
UI (error message, retry button) instead of a blank screen.

---

### 📘 Textbook Definition

**Error Boundary** - a React class component that implements
`static getDerivedStateFromError(error)` and/or
`componentDidCatch(error, info)` lifecycle methods. When
a JavaScript error is thrown during rendering, in lifecycle
methods, or in constructors of any component in the
subtree below the boundary, React invokes these methods
instead of propagating the error upward. The boundary
renders a fallback UI instead of the crashed subtree.
Error Boundaries do NOT catch: errors in event handlers,
async code (setTimeout, Promise), server-side rendering
errors, or errors thrown in the Error Boundary itself.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// Only class components can be Error Boundaries
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  // Update state when error occurs in child tree
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  // Log the error (side effects go here)
  componentDidCatch(error, errorInfo) {
    logErrorToService(error, errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return <h2>Something went wrong. Please refresh.</h2>;
    }
    return this.props.children; // render children normally
  }
}

// Wrap any subtree to isolate it
<ErrorBoundary>
  <UserProfile userId={id} />
</ErrorBoundary>;
```

---

### 🔩 First Principles Explanation

**THE ERROR PROPAGATION MODEL:**

```
WITHOUT Error Boundary:
  ChildComponent throws during render
  → React propagates error up component tree
  → Reaches root, no handler found
  → Entire app unmounts (blank screen in production)
  → In development: React DevTools error overlay

WITH Error Boundary:
  ChildComponent throws during render
  → React propagates error up component tree
  → Reaches ErrorBoundary (has getDerivedStateFromError)
  → getDerivedStateFromError: returns new state
  → Boundary re-renders with hasError=true
  → Renders fallback UI instead of crashed subtree
  → Rest of app continues working normally
```

**TWO LIFECYCLE METHODS:**

```
getDerivedStateFromError(error):
  - Static method (no access to this)
  - Purpose: update state to trigger fallback render
  - Called during "render phase" - must be pure
  - Return: state update object or null
  - No side effects here (logging, etc.)

componentDidCatch(error, errorInfo):
  - Instance method (access to this)
  - Purpose: log the error (side effects allowed)
  - Called during "commit phase"
  - errorInfo.componentStack: the React component stack
  - Use to send to error monitoring (Sentry, Datadog)
```

**STRATEGIC PLACEMENT:**
Place Error Boundaries at multiple levels for granular
containment:

```
<App>
  <ErrorBoundary fallback={<PageError />}>  ← page-level
    <Sidebar />
    <ErrorBoundary fallback={<WidgetError />}> ←
      widget-level
      <RecentOrders />  ← if this crashes...
    </ErrorBoundary>               ← ...only widget shows
      fallback
    <AccountBalance />  ← this continues working
  </ErrorBoundary>
</App>
```

---

### 🧪 Thought Experiment

**THE FINANCIAL DASHBOARD:**
An investment dashboard has six widgets: portfolio value,
recent transactions, market news, watchlist, P&L chart,
account info. The market news widget fetches from a
third-party API and occasionally crashes.

Without Error Boundaries: the entire dashboard disappears.
A user cannot check their portfolio value because the
news widget crashed.

With an Error Boundary around each widget: the news widget
shows "News unavailable" while the other five widgets
continue working perfectly. Users can still monitor their
portfolio. The boundary converted a catastrophic crash
into a contained degradation.

This is the key architectural insight: Error Boundaries
implement partial availability - "degrade gracefully,
not completely."

---

### 🧠 Mental Model / Analogy

> An Error Boundary is like a circuit breaker in
> electrical engineering. When a circuit carries too
> much current (a component throws), the circuit breaker
> trips (getDerivedStateFromError updates state) and
> isolates that circuit (renders fallback instead of
> crashed subtree). The rest of the building's electrical
> system (other components) continues working normally.
> Without circuit breakers, one faulty appliance could
> short the entire building's power.
>
> You do not put one circuit breaker for the whole building.
> You put them per room, per appliance. Strategic placement
> determines how much gets isolated when one circuit trips.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Error Boundaries catch errors in their child component
tree and show a fallback UI instead of crashing the whole
app. They are class components with special lifecycle
methods.

**Level 2 (usage):**
Create a class component. Add `static getDerivedStateFromError`
to set `hasError: true`. Add `componentDidCatch` to log.
In `render`, return `this.props.children` normally or
a fallback if `hasError`. Wrap any risky subtree in it.

**Level 3 (architecture):**
Place boundaries at multiple levels: top-level (prevent
full blank screen), page-level (per route), section-level
(per widget/panel), component-level (experimental or
unstable components). Balance granularity vs fallback
quality - a per-component boundary has less context to
display a meaningful error message.

**Level 4 (production):**
In `componentDidCatch`, send to an error monitoring service
(Sentry: `Sentry.captureException(error, { extra:
errorInfo })`). Include `componentStack` for debugging.
Add a reset mechanism (`key` prop change to remount):
change the boundary's `key` prop to reset its error state
and retry rendering.

**Level 5 (mastery):**
Error Boundaries only exist as class components because
the lifecycle methods (`getDerivedStateFromError`,
`componentDidCatch`) have no equivalent hook. The React
team has explored adding an `useErrorBoundary` hook but
as of React 18, it remains a class-only feature. Libraries
like `react-error-boundary` provide a pre-built functional
API that wraps a class boundary internally, with a `FallbackComponent`
prop and a `resetKeys` prop for automatic reset. Concurrent
mode adds complexity: React may retry a failed render (it
can re-invoke the render function multiple times in
concurrent mode), so only commit the error to the boundary
after the commit phase (this is why logging is in
`componentDidCatch`, not `getDerivedStateFromError`).

---

### ⚙️ How It Works (Mechanism)

**Production-ready Error Boundary:**

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Called during render phase - return state update only
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Called after commit - safe for side effects
    // errorInfo.componentStack = React component trace
    console.error("Error Boundary caught:", error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback;
      if (FallbackComponent) {
        return (
          <FallbackComponent
            error={this.state.error}
            resetError={this.handleReset}
          />
        );
      }
      return (
        <div role="alert">
          <p>Something went wrong.</p>
          <button onClick={this.handleReset}>Try again</button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Usage
function WidgetErrorFallback({ error, resetError }) {
  return (
    <div className="widget-error">
      <p>Failed to load widget.</p>
      <button onClick={resetError}>Retry</button>
    </div>
  );
}

<ErrorBoundary
  fallback={WidgetErrorFallback}
  onError={(err, info) => sentry.captureException(err, info)}
>
  <RecentOrdersWidget />
</ErrorBoundary>;
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Error Boundaries catch all errors in their children"       | They catch errors during: rendering, lifecycle methods, constructors. They do NOT catch: errors in event handlers (`onClick`, etc.), async code (`setTimeout`, `Promise`, `async/await`), server-side rendering errors, or errors thrown in the Error Boundary's own render. Event handler errors need regular `try/catch`. |
| "Functional components can be Error Boundaries using hooks" | As of React 18, only class components can be Error Boundaries. No hook equivalent exists. Libraries like `react-error-boundary` provide a hooks-friendly API but wrap a class component internally.                                                                                                                         |
| "An Error Boundary at the root is sufficient"               | A root-level boundary prevents a blank screen, but everything inside it is still a single unit of failure. Strategic per-section boundaries limit damage and allow partial functionality when one area fails.                                                                                                               |
| "Error Boundaries automatically reset when props change"    | They do not reset automatically. Once `hasError` is true, it stays true until the component unmounts, `setState({ hasError: false })` is called explicitly, or the boundary is remounted (by changing its `key` prop).                                                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**Event Handler Error Not Caught**

**Symptom:** An error thrown inside an `onClick` handler
crashes the app (or silently fails), but the Error Boundary
fallback does not show.

**Root Cause:** Error Boundaries only intercept errors
during the React render phase. Event handler errors occur
outside the render phase.

**Fix:**

```jsx
// Wrap event handler errors manually
const handleClick = () => {
  try {
    riskyOperation();
  } catch (error) {
    setError(error.message); // display via state
  }
};
```

---

**Error Boundary Not Resetting on Route Change**

**Symptom:** User navigates to a page that throws. Error
boundary shows fallback. User navigates away and back.
Error boundary still shows fallback (stale error state).

**Root Cause:** The Error Boundary component did not
unmount and remount between navigations - its error state
persists.

**Fix:** Tie the Error Boundary's `key` to the route
location. When key changes, React unmounts and remounts
the boundary, clearing error state:

```jsx
const location = useLocation();
<ErrorBoundary key={location.pathname}>
  <RouteContent />
</ErrorBoundary>;
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `Class vs Functional Components` - Error Boundaries
  require class component syntax
- `React Components and Props` - the component model
  that boundaries operate on

**Builds On:**

- `Suspense` - works alongside Error Boundaries; both
  intercept the render phase for different purposes
  (loading vs error)
- `Code Splitting with React.lazy` - lazy imports must
  always be wrapped in both `<Suspense>` and `<ErrorBoundary>`
- `Testing React with RTL` - testing boundary behavior
  under simulated errors

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CLASS ONLY  │ Class components only (no hook equivalent)│
│ CATCHES     │ Render, lifecycle, constructor errors     │
│ MISSES      │ Event handlers, async, SSR, own errors    │
├─────────────────────────────────────────────────────────┤
│ LIFECYCLE 1 │ getDerivedStateFromError(error)           │
│             │ → pure, return state update, render phase │
│ LIFECYCLE 2 │ componentDidCatch(error, info)            │
│             │ → commit phase, log/monitor here          │
├─────────────────────────────────────────────────────────┤
│ RESET       │ setState({hasError: false}) or key change │
│ PLACEMENT   │ Granular: per-section/per-widget          │
├─────────────────────────────────────────────────────────┤
│ LIBRARY     │ react-error-boundary (functional API)     │
│             │ Sentry: captureException in componentDidCa│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Class component with `getDerivedStateFromError`
   (update state to show fallback) and `componentDidCatch`
   (log the error - side effects here).
2. Only catches render-phase errors. Event handler errors
   need `try/catch`.
3. Reset by calling `setState({hasError:false})` or by
   changing the boundary's `key` prop.

**Interview one-liner:**
"Error Boundaries are class components that implement
`getDerivedStateFromError` (to set error state during
render phase) and `componentDidCatch` (to log errors
in commit phase). They catch render-phase errors in their
child tree and display a fallback UI. They do NOT catch
event handler errors, async code, or their own render
errors. No hook equivalent exists as of React 18. Strategic
placement at multiple levels (page, section, widget)
enables partial availability - one crashed widget does
not take down the whole dashboard."

---

### 💎 Transferable Wisdom

Error Boundaries implement the "bulkhead" pattern from
distributed systems: isolate failures to prevent
cascading. A bulkhead in a ship divides the hull into
compartments so a breach in one compartment does not sink
the whole ship. In microservices: circuit breakers and
bulkheads prevent one slow downstream service from
exhausting the thread pool of the entire system (Resilience4j,
Hystrix). In React: Error Boundaries prevent one bad
component from unmounting the entire app. The placement
question - "how granular should the isolation be?" - is
identical in both domains. Finer granularity = better
partial availability but more operational overhead.

---

### 💡 The Surprising Truth

React's decision to not catch event handler errors in
Error Boundaries is intentional, not an oversight. React's
team reasoned: event handlers don't happen during rendering.
An event handler error does not corrupt React's internal
state. Therefore, throwing from an event handler is no
different from throwing from any JavaScript callback -
it should be caught with a standard try/catch, just like
in vanilla JS. Only errors that corrupt React's internal
render state (thrown during the render phase) need the
Error Boundary mechanism. This boundary between "React-
managed" and "user-space JavaScript" is a key architectural
line that React deliberately enforces.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a multi-section dashboard where each
   section (user profile, recent orders, recommendations)
   has its own Error Boundary with a custom fallback UI
   and a retry button.
2. **DEMONSTRATE** the difference in behavior between
   an error thrown in a render function vs in an event
   handler, and explain why the boundary catches one
   but not the other.
3. **INTEGRATE** with an error monitoring service
   (Sentry or a mock) using `componentDidCatch`, including
   the component stack trace.
4. **IMPLEMENT** a reset mechanism using the `key` prop
   on a route-level Error Boundary that resets on navigation.
5. **EXPLAIN** why Error Boundaries cannot be functional
   components, and what the `react-error-boundary` library
   provides as a convenience API.

---

### 🧠 Think About This Before We Continue

**Q1.** An Error Boundary wraps a lazy-loaded component
(`React.lazy`). The lazy import fails (network error,
chunk 404). Does the Error Boundary catch this? Suspense
is also involved. What is the interaction between Suspense
(which handles the loading state) and Error Boundary
(which handles the error state) for a `React.lazy` import?

**Q2.** You need to show a "retry" button in the Error
Boundary fallback that reloads the failed data. The
Error Boundary is a class component, but the data fetching
hook is in the (now-crashed) child functional component.
How do you implement a retry that re-fetches data and
re-renders the component tree from scratch, without full
page reload?

**Q3.** React's concurrent mode may "retry" renders -
calling the render function multiple times before committing.
If a component intermittently throws (it throws 50% of
the time based on some condition), what does an Error
Boundary show? How does concurrent mode's retry interact
with Error Boundary behavior, and what does this mean
for production error monitoring (you could see many
"error" events that React internally retried and succeeded)?
