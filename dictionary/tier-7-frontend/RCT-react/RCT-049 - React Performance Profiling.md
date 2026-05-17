---
id: RCT-049
title: React Performance Profiling
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-035, RCT-036, RCT-037, RCT-039
used_by: RCT-060
related: RCT-035, RCT-037, RCT-060
tags:
  - react
  - frontend
  - performance
  - profiling
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /react/react-performance-profiling/
---

# RCT-049 - REACT PERFORMANCE PROFILING

⚡ TL;DR - React performance profiling uses React DevTools
Profiler to record renders and identify which components
re-render unnecessarily, how long each render takes, and
what triggered the re-render; the workflow is: profile
→ identify hot paths → apply targeted optimisations
(React.memo, useMemo, useCallback) → re-profile to confirm
improvement.

| #049            | Category: React                                                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | useMemo Hook, useCallback Hook, React.memo, React Reconciliation Algorithm |                 |
| **Used by:**    | Core Web Vitals in React Applications                                      |                 |
| **Related:**    | useMemo Hook, React.memo, Core Web Vitals                                  |                 |

---

### 🔥 The Problem This Solves

**PREMATURE OPTIMISATION WITHOUT DATA:**
The most common performance mistake in React: adding
`React.memo`, `useMemo`, and `useCallback` to every
component without measuring. This adds complexity and
can actually hurt performance (memoisation overhead for
fast operations, stale data from incorrect deps).

The second mistake: not profiling and instead optimising
based on intuition. Intuition is often wrong about where
the bottleneck is.

React DevTools Profiler makes bottlenecks visible: which
component is slow, why it re-rendered, how many times
it re-rendered per interaction. Optimise with data, not
guesses.

---

### 📘 Textbook Definition

**React Performance Profiling** - the process of measuring
a React application's rendering performance using React
DevTools Profiler (and browser DevTools Performance tab)
to identify components that render too frequently or
take too long to render. The Profiler records render
events, durations, and the interaction that triggered
each commit. Profiling identifies the 20% of components
responsible for 80% of performance problems.

---

### ⏱️ Understand It in 30 Seconds

```
React DevTools Profiler workflow:

1. Open Chrome DevTools → Profiler tab (in React DevTools)
2. Click "Start profiling"
3. Perform the slow interaction in the app
4. Click "Stop profiling"
5. Examine the flame chart:
   - Each bar = one component's render
   - Bar height/colour = render duration (yellow = slow)
   - Click a bar = see why it rendered
     ("Props changed", "State changed", "Context changed",
      "Parent rendered" - the last one is often the culprit)
6. Identify: which components render on every keystroke?
   Which renders take >16ms (drops a frame at 60fps)?
7. Apply targeted fixes:
   - Slow component: useMemo, useCallback, computation extraction
   - Unnecessary re-renders: React.memo with stable props
```

---

### 🔩 First Principles Explanation

**PROFILING METRICS:**

```
Key metrics in the Profiler:

1. Commit duration - total time React spent rendering
   this commit (paint update). >16ms = potential frame drop.
   >100ms = user notices lag.

2. Component render duration - how long one component's
   render function took. Normally <1ms. >5ms = investigate.

3. Re-render count - how many times a component rendered
   during a session. Hundreds of renders for a static
   component: something is wrong.

4. Render reason - WHY did this component render?
   "Props changed" → which prop changed? Is it a new
     object/array/function reference? (unstable reference bug)
   "State changed" → expected: state change = re-render
   "Context changed" → which context? Can context be split?
   "Parent rendered" → component has no state/props change
     but re-rendered because parent did. Fix: React.memo
   "Hooks changed" → which hook's value changed?
```

**Browser DevTools for non-React bottlenecks:**

```
React Profiler only measures React rendering.
Use Browser DevTools Performance tab for:
  - JavaScript execution time (non-React code)
  - Network waterfall (slow fetches)
  - Layout/reflow cost (too many DOM reads/writes)
  - Animation frame drops (main thread blocking)
  - Memory leaks (heap snapshots)
```

---

### 🧪 Thought Experiment

**THE LIST FILTERING INVESTIGATION:**
An autocomplete with 1000 items feels laggy on every
keystroke. The React Profiler reveals:

1. On each keystroke, the entire `<AutocompleteList>`
   re-renders (Parent rendered).
2. Every 1000 `<AutocompleteItem>` components re-render,
   each taking 0.5ms.
3. 1000 × 0.5ms = 500ms per keystroke. That is 30x beyond
   the 16ms frame budget.

Without the profiler: the developer would guess that
the input handling is slow and optimize setState.

With the profiler: the problem is clear - 1000 components
re-rendering unnecessarily. Fix: `React.memo` on
`<AutocompleteItem>` (items that did not change should
not re-render). After applying `React.memo`: only the
1-3 items that change between keystrokes re-render.
500ms → 1.5ms. Problem solved with targeted, data-driven
optimisation.

---

### 🧠 Mental Model / Analogy

> React Profiling is like a time-lapse x-ray of your
> app. Each frame of the x-ray shows which parts of
> the body (component tree) are active (rendering) and
> how hard they are working (render duration).
>
> Without the x-ray: you feel something is wrong in your
> knee, but you guess it might be the shoulder. You treat
> the shoulder and the knee still hurts.
>
> With the x-ray: you see exactly where the inflammation
> is (which components are slow). You treat the exact
> problem and verify it is resolved on the next x-ray.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (profiler basics):**
React DevTools Profiler → record → interact → stop →
read flame chart. Yellow bars are slow. Click a bar to
see why it rendered.

**Level 2 (reading render reasons):**
"Parent rendered" with no state/props change → candidate
for `React.memo`. "Props changed: function prop" →
stabilise function with `useCallback`. "Props changed:
object prop" → stabilise object with `useMemo` or extract
to outer scope.

**Level 3 (Profiler API):**
React's `<Profiler>` component can be used in code to
collect render metrics programmatically and send to an
analytics backend:

```jsx
<Profiler id="Navigation" onRender={logToMetrics}>
  <Navigation />
</Profiler>
```

Use this to monitor production performance over time.

**Level 4 (CPU profiling):**
React Profiler measures render duration but not JavaScript
execution cost within the render. Use Chrome DevTools
Performance tab → record → look for long "yellow" tasks
in the main thread. Break up long tasks with
`startTransition` (defers non-urgent updates).

**Level 5 (mastery):**
The golden workflow: (1) establish a performance budget
(e.g. all interactions under 100ms). (2) Write a
performance test using Lighthouse CI or web-vitals to
measure automatically in CI. (3) Profile locally to
find bottlenecks when metrics regress. (4) Apply
targeted fixes. (5) Re-measure to confirm improvement.
Never optimise without measurement. Never merge
performance changes without verifying the improvement
in metrics.

---

### ⚙️ How It Works (Mechanism)

**Programmatic Profiler API:**

```jsx
import { Profiler } from "react";

function onRenderCallback(
  id, // the "id" prop of the Profiler tree
  phase, // "mount" or "update"
  actualDuration, // rendering time for this update
  baseDuration, // estimated rendering without memoisation
  startTime, // when React began rendering this update
  commitTime, // when React committed this update
) {
  // Send to analytics
  if (actualDuration > 16) {
    console.warn(`Slow render: ${id} took ${actualDuration.toFixed(2)}ms`);
    analytics.trackSlowRender({
      component: id,
      duration: actualDuration,
      phase,
    });
  }
}

function App() {
  return (
    <Profiler id="Dashboard" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}
```

**Finding unnecessary re-renders with why-did-you-render:**

```jsx
// In development: install why-did-you-render
// @welldone-software/why-did-you-render
import React from "react";
if (process.env.NODE_ENV === "development") {
  const whyDidYouRender = require("@welldone-software/why-did-you-render");
  whyDidYouRender(React, {
    trackAllPureComponents: true,
  });
}

// On a component:
DataTable.whyDidYouRender = true;
// Console will log: "DataTable re-rendered. SAME PROPS."
// when a component re-renders with identical props
// (indicating React.memo would help)
```

---

### 💻 Code Example

**BAD: Premature optimisation without profiling:**

```jsx
// BAD: memoising everything without data
// These may add cost without benefit if:
// - deps change on every render (memoisation wasted)
// - computation is fast (<0.1ms, not worth the overhead)
function UserCard({ user, onEdit, onDelete }) {
  // Every value memoised - did you measure this was needed?
  const displayName = useMemo(
    () => `${user.firstName} ${user.lastName}`,
    [user.firstName, user.lastName],
  ); // String concatenation: 0.001ms, not worth useMemo

  const handleEdit = useCallback(() => onEdit(user.id), [onEdit, user.id]); // Is this component actually memoised with React.memo?
  // If not, useCallback here does nothing useful.

  const styles = useMemo(
    () => ({ color: user.active ? "green" : "gray" }),
    [user.active],
  ); // Simple ternary: 0.001ms, not worth useMemo
}
```

**GOOD: Profile first, then apply targeted fixes:**

```jsx
// GOOD: after profiling reveals DataTable re-renders
// 1000x per second, memoise the slow component
const DataTable = React.memo(function DataTable({ data, onSort }) {
  // Complex table render: takes 50ms
  return (
    <table>
      {data.map((row) => (
        <Row key={row.id} row={row} />
      ))}
    </table>
  );
});
// Parent component:
function Dashboard({ dataset }) {
  // Profiler revealed onSort is recreated each render
  // causing DataTable to not benefit from React.memo
  const handleSort = useCallback(
    (column) => sortData(dataset, column),
    [dataset], // only recreate when dataset changes
  );
  return <DataTable data={dataset} onSort={handleSort} />;
}
```

---

### 📊 Comparison Table

| Tool                                  | What it measures                                      | Best for                                                 |
| ------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| React DevTools Profiler               | Component render counts and durations, render reasons | Finding unnecessary re-renders, slow React rendering     |
| Browser DevTools Performance          | JS execution, layout, paint, network                  | Non-React bottlenecks, frame drops, main thread blocking |
| Lighthouse                            | Core Web Vitals (LCP, INP, CLS), performance score    | Page load performance, user-perceived metrics            |
| web-vitals library                    | Real-user Core Web Vitals                             | Production monitoring, RUM (Real User Monitoring)        |
| @welldone-software/why-did-you-render | Unnecessary re-renders with prop comparison           | Finding React.memo opportunities in development          |
| Bundle analyzer                       | Bundle sizes by module                                | Identifying large dependencies to code-split             |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More React.memo/useMemo/useCallback = better performance" | Memoisation has overhead: comparing deps, storing previous values. For fast computations (<1ms) or rarely-rendering components, memoisation can be slower than no optimisation. Profile first - optimise only what the profiler identifies as the bottleneck.                                                                                                 |
| "React Profiler shows real-world performance"              | The Profiler adds measurement overhead. React in development mode is also 2-3x slower than production. Profile in production build (`npm run build`) and use the Profiler API to collect metrics from real users.                                                                                                                                             |
| "A component that renders once per second is fine"         | Depends on cost. A simple component that renders 60x/second in 0.1ms each = 6ms total CPU per second (fine). A complex component that renders once per second in 200ms each = UI freezes (terrible). Frequency × cost = impact.                                                                                                                               |
| "useTransition fixes performance problems"                 | `useTransition` defers rendering so the UI stays responsive, but it does not reduce the total work. If a render takes 500ms, using `useTransition` means the UI stays responsive while that 500ms runs in the background. The work still takes 500ms. For actual speedup, reduce the render cost with memoisation, virtualisation, or computation offloading. |

---

### 🚨 Failure Modes & Diagnosis

**Component Renders on Every Keystroke Despite React.memo**

**Symptom:** Profiler shows a memoised component
("React.memo wrapped") still re-renders on every keystroke.

**Root Cause:** A prop is a new object/array/function
reference on every parent render. React.memo compares
props with shallow equality. Two objects `{x: 1}` and
`{x: 1}` are NOT equal in JavaScript (`{} !== {}`).

**Diagnosis:**

1. Profiler → click the re-rendering component → "Props changed"
2. Look for: function prop, object prop, array prop
3. The prop that changed is recreated in the parent

**Fix:**

```jsx
// If the prop is a function: useCallback in parent
const onSort = useCallback(fn, [deps]);

// If the prop is an object: useMemo in parent
const config = useMemo(() => ({ pageSize: 10 }), []);

// If the prop is an array: useMemo in parent
const filteredItems = useMemo(() => items.filter(active), [items]);
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `useMemo Hook`, `useCallback Hook`, `React.memo` - the optimisation tools
- `React Reconciliation Algorithm` - what the Profiler measures

**Builds On:**

- `Core Web Vitals in React Applications` - user-perceived
  metrics that performance optimisation improves

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WORKFLOW  │ Profile → identify → fix → re-profile        │
│ TOOLS     │ React DevTools Profiler (renders)            │
│           │ Browser Performance tab (JS/layout/network)  │
│           │ Lighthouse (Core Web Vitals)                 │
├──────────────────────────────────────────────────────────┤
│ YELLOW BAR│ Slow render (>16ms)                          │
│ PARENT RE │ "Parent rendered" → candidate for React.memo │
│ PROP FN   │ Function prop new ref → useCallback in parent│
│ PROP OBJ  │ Object prop new ref → useMemo in parent      │
├──────────────────────────────────────────────────────────┤
│ RULE      │ Never optimise without measuring first       │
│ BUDGET    │ >16ms per commit = potential frame drop      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Profile first, optimise second. The bottleneck is
   almost never where you expect. React DevTools Profiler
   shows exactly which components are slow and why.
2. "Parent rendered" as the re-render reason = candidate
   for `React.memo`. But check the props - if function/
   object props are new references each render, `memo`
   will not help without `useCallback`/`useMemo` on those props.
3. Never add `useMemo`/`useCallback` everywhere. Add
   them only where the Profiler shows a measurable benefit.
   Unnecessary memoisation adds complexity and can slow
   things down.

**Interview one-liner:**
"React performance profiling uses React DevTools Profiler
to record which components render, why they rendered
(props/state/context change, parent re-render), and how
long each render took. The workflow: profile the slow
interaction, identify yellow bars (slow renders) or
components that re-render with 'Parent rendered' as the
reason, apply targeted fixes (`React.memo`, `useCallback`,
`useMemo`), then re-profile to confirm improvement. The
rule: never optimise without measuring - memoisation
has overhead and can hurt performance when applied
without data."

---

### 💎 Transferable Wisdom

React performance profiling applies the same methodology
as performance engineering in any system: measure, find
the bottleneck (the 20% causing 80% of the problem),
fix the bottleneck, measure again. This is the Amdahl's
Law principle: the speedup from optimising one part is
limited by how much of the total time that part takes.
Optimising a component that takes 1% of render time
gives at most 1% improvement. Optimising the component
that takes 60% of render time can give up to 60%
improvement. Without measurement, you cannot apply this
principle. This methodology applies equally to database
query optimisation (EXPLAIN ANALYZE), JVM profiling
(async-profiler, JFR), and backend service profiling
(distributed tracing, flame graphs). The tools differ;
the principle is identical.

---

### 💡 The Surprising Truth

React's Profiler was added in React 16.5 (2018), over
5 years after React was released. For the first 5 years
of React, there was no built-in profiling tool -
developers used browser performance recordings and
third-party libraries. This partly explains why "add
React.memo everywhere" became common: without a profiling
tool, developers could not easily see which components
were actually slow. The addition of the Profiler
fundamentally changed the best practice: instead of
defensive memoisation (memo everywhere "just in case"),
the new recommended workflow is data-driven memoisation
(profile, then apply memo only where measurements show
a benefit). The existence of a good measurement tool
changed what "good practice" means.

---

### ✅ Mastery Checklist

1. **PROFILE** a React app with a list of 100+ items and
   a filter input. Record a profiling session while
   typing in the filter. Identify which components re-
   render on each keystroke and their render duration.
2. **APPLY** targeted optimisations based on the profiler
   output. Re-profile to confirm the improvement. Quantify
   the render time reduction.
3. **DEMONSTRATE** the "Parent rendered" cause and fix it:
   a child component re-renders only because the parent
   re-renders (child's props unchanged). Apply `React.memo`
   and verify in the profiler.
4. **FIND** an unstable function prop causing `React.memo`
   to be ineffective. Fix with `useCallback`. Verify in
   the profiler that the memoised component no longer
   re-renders when the parent state changes.
5. **USE** the Profiler API (`<Profiler onRender>`) to
   log render durations to the console during a recording.
   Identify the 3 slowest components by total time.

---

### 🧠 Think About This Before We Continue

**Q1.** The React DevTools Profiler shows a component
that renders 50ms per commit. The component renders only
3 times per second (not on every keystroke). At 150ms
total per second, is this a problem? The user reports
the interaction feels "sluggish." How do you determine
whether the 50ms render is the cause vs something else
(network latency, CSS animation, or a different component)?

**Q2.** `React.memo` uses shallow equality by default.
For a component that receives a deeply nested object
prop, shallow equality will always detect a "change"
even if the nested values are the same (because the
outer reference changed). Write a custom comparison
function for `React.memo` that does deep equality on
this specific prop. What are the performance implications
of doing a deep equality check for every render?

**Q3.** React 18's Concurrent Mode can interrupt renders
and resume them later (time-slicing). This changes what
the React DevTools Profiler reports: a render that
"actually took 50ms" might show in the profiler as two
separate segments of 25ms each with a gap in between.
How does this change how you interpret profiler data?
What new metrics are meaningful in Concurrent Mode that
were not relevant in synchronous rendering mode?
