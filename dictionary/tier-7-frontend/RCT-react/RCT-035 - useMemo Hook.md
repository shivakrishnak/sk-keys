---
id: RCT-035
title: useMemo Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-020, RCT-021, RCT-039
used_by: RCT-036, RCT-037, RCT-049
related: RCT-036, RCT-037, RCT-039
tags:
  - react
  - frontend
  - hooks
  - performance
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /react/usememo-hook/
---

# RCT-035 - USEMEMO HOOK

⚡ TL;DR - `useMemo(() => expensiveComputation(), [deps])`
caches a computed value between renders, recomputing only
when deps change - it is the performance tool for expensive
in-render calculations, and it produces a stable object
reference that prevents unnecessary `React.memo` child
re-renders; misused, it wastes memory and adds complexity
with no measurable benefit.

| #035 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | useState Hook, useEffect Hook, React Reconciliation Algorithm | |
| **Used by:** | useCallback Hook, React.memo, React Performance Profiling | |
| **Related:** | useCallback Hook, React.memo, React Reconciliation | |

---

### 🔥 The Problem This Solves

**EXPENSIVE RECALCULATION ON EVERY RENDER:**
A component renders 60 times per second during an animation.
It also has a function that sorts/filters a 10,000-item
list. Without memoisation, the sort runs on every render,
even when the list has not changed. With `useMemo`, the
sort only runs when the list data changes.

A second problem: an object or array created in render
body has a NEW reference on every render. If this object
is passed as a prop to a `React.memo` child, the child
re-renders every time the parent renders - because
`{} !== {}` (new object each time). `useMemo` returns
the SAME reference when deps have not changed.

---

### 📘 Textbook Definition

**useMemo** - a React hook that memoises the result of
a computation. The first argument is a "create" function
that performs the computation. The second argument is a
dependency array. On the first render, `useMemo` calls
the create function and caches its return value. On
subsequent renders, if no dependency has changed, `useMemo`
returns the cached value without calling the create
function. If any dependency has changed, the create
function is re-called and the new result is cached.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// WITHOUT useMemo: filter runs on every render
function ProductList({ products, category }) {
  // This runs on every re-render, even unrelated ones
  const filtered = products.filter(p => p.category === category);
  return <ul>{filtered.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}

// WITH useMemo: filter runs only when products or category changes
function ProductList({ products, category }) {
  const filtered = useMemo(
    () => products.filter(p => p.category === category),
    [products, category]  // re-run only when these change
  );
  return <ul>{filtered.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}
```

---

### 🔩 First Principles Explanation

**WHAT USEMEMO DOES NOT DO:**

```
useMemo does NOT skip the component render.
  The component's function still runs on every re-render.
  useMemo only skips the computation inside the memo call.

React.memo skips the component render if props are equal.
useMemo caches the return value of a computation.

These are complementary: useMemo for expensive in-render
computation, React.memo for expensive component render.
```

**THE REFERENCE STABILITY USE CASE:**

```jsx
// Problem: new object reference on every render
function Parent({ items }) {
  const config = { sortBy: 'name', order: 'asc' };  // new each render
  return <ExpensiveChild items={items} config={config} />;
}

// ExpensiveChild wrapped in React.memo:
const ExpensiveChild = React.memo(function ({ items, config }) {
  // ...
});
// BUT: config is always a new {} reference.
// React.memo sees config !== config (different reference)
// and re-renders ExpensiveChild on EVERY parent render.
// React.memo is completely bypassed.

// Fix: stable reference with useMemo
function Parent({ items }) {
  const config = useMemo(
    () => ({ sortBy: 'name', order: 'asc' }),
    []  // no deps: always the same object
  );
  return <ExpensiveChild items={items} config={config} />;
}
// Now config is the same reference between renders
// React.memo works correctly
```

---

### 🧪 Thought Experiment

**THE PROFILING QUESTION:**
Before adding `useMemo` to a component, ask: "Is this
actually slow?" The React component tree has hundreds of
components. Most `filter`, `map`, and `sort` operations
on arrays of under 1,000 items complete in under 1ms.
`useMemo` itself has a cost: it stores the cached value
in memory, runs a shallow comparison of all deps on every
render, and adds cognitive complexity to the code.

If the computation takes 0.1ms, and the component renders
50 times per second in a complex animation, the total
cost is 5ms per second - invisible to users. Adding
`useMemo` saves 5ms per second of computation at the
cost of: more RAM (cached value), deps comparison on every
render, and code complexity.

The rule: profile first. If React Profiler shows a
specific component taking >16ms (one frame at 60fps),
measure the computation. If the computation is the bottleneck,
add `useMemo`. Otherwise, skip it.

---

### 🧠 Mental Model / Analogy

> `useMemo` is a spreadsheet cell that says "only recalculate
> this formula if the cells it depends on have changed."
> Excel does not recompute `=VLOOKUP(A1, Table, 2, FALSE)`
> every time you scroll, resize the window, or update an
> unrelated cell. It only recalculates when the value in
> A1 or the table data changes.
>
> `useMemo` brings the same concept to React:
> "Only recompute this expensive value when these specific
> inputs change. For all other renders, use the cached
> answer."

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`useMemo` caches a computed value. The cache is invalidated
when the dependencies change. Use it when a computation
is genuinely expensive (measured, not assumed).

**Level 2 (usage):**
`const value = useMemo(() => computeValue(a, b), [a, b])`.
The create function is called when `a` or `b` changes.
The cached result is returned on all other renders. Create
function must be pure (no side effects - that is `useEffect`).

**Level 3 (patterns):**
Two use cases: (1) expensive computation (sort 100k items,
complex aggregation), (2) stable reference for `React.memo`
children. The stable reference use case is often more
impactful than the expensive computation use case.

**Level 4 (internals):**
React stores the `useMemo` cache alongside the Fiber node
for the component. On re-render, React compares each dep
in the new deps array to the stored deps using `Object.is`
(shallow comparison). If all are equal, returns cached
value. The cache holds exactly one result - if you pass
different deps sequences in alternating renders, the cache
is invalidated on every render (worse than no memoisation).

**Level 5 (mastery):**
The React Compiler (React Forget, shipping with React 19)
statically analyses components and automatically inserts
`useMemo` and `useCallback` where needed. The team's
position is that manual memoisation is a developer-experience
problem (you have to think about it) that should be solved
by the compiler. In a compiler-enabled app, manual `useMemo`
becomes redundant for most cases. The skill to retain:
understanding WHEN memoisation is needed (the conceptual
model), not the API syntax.

---

### ⚙️ How It Works (Mechanism)

**Correct and incorrect useMemo usage:**

```jsx
// CORRECT: expensive computation with meaningful deps
function AnalyticsDashboard({ transactions, dateRange }) {
  // Aggregates 50,000 transactions - genuinely expensive
  const stats = useMemo(() => {
    const filtered = transactions.filter(t =>
      t.date >= dateRange.start && t.date <= dateRange.end
    );
    return {
      total: filtered.reduce((sum, t) => sum + t.amount, 0),
      count: filtered.length,
      avg: filtered.length ? filtered.reduce((s, t) => s + t.amount, 0)
        / filtered.length : 0,
      byCategory: filtered.reduce((acc, t) => {
        acc[t.category] = (acc[t.category] || 0) + t.amount;
        return acc;
      }, {}),
    };
  }, [transactions, dateRange]);  // re-compute only when data changes

  return <StatsDisplay stats={stats} />;
}

// CORRECT: stable reference for React.memo child
function FilteredTable({ rows, onSelect }) {
  // Without useMemo, options is a new array on every render
  // → React.memo on TableHeader is bypassed
  const columns = useMemo(() => [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'status', label: 'Status' },
  ], []);  // no deps: always the same columns config

  return (
    <>
      <TableHeader columns={columns} />  {/* React.memo works */}
      {rows.map(row => <TableRow key={row.id} row={row} />)}
    </>
  );
}
```

---

### 💻 Code Example

**BAD: useMemo without profiling (premature optimisation):**

```jsx
// BAD: useMemo on trivially cheap operation
function UserCard({ user }) {
  // This computation is ~0.001ms. useMemo costs more than it saves.
  // Adds cognitive complexity for zero measurable benefit.
  const displayName = useMemo(
    () => `${user.firstName} ${user.lastName}`,
    [user.firstName, user.lastName]
  );

  // Also BAD: useMemo with object that is only used locally
  // (not passed to React.memo child) - no stable ref benefit
  const style = useMemo(
    () => ({ color: 'blue', fontSize: '16px' }),
    []
  );

  return <div style={style}>{displayName}</div>;
}

// The correct version (no useMemo needed):
function UserCard({ user }) {
  const displayName = `${user.firstName} ${user.lastName}`;
  return <div style={{ color: 'blue', fontSize: '16px' }}>{displayName}</div>;
}
```

**GOOD: useMemo where it measurably helps:**

```jsx
// GOOD: memoising an expensive sort + filter for a large dataset
// Profiler confirmed this was causing 40ms renders
function OrderHistory({ orders, filter, sortBy }) {
  const processedOrders = useMemo(() => {
    // This was measured at 35ms for 20,000 orders
    const filtered = orders.filter(o =>
      filter === 'all' || o.status === filter
    );
    return filtered.sort((a, b) =>
      sortBy === 'date' ? b.date - a.date : b.amount - a.amount
    );
  }, [orders, filter, sortBy]);

  return (
    <ul>
      {processedOrders.map(order => (
        <OrderRow key={order.id} order={order} />
      ))}
    </ul>
  );
}
```

---

### 📊 Comparison Table

| Hook/API | What it caches | Use case |
|---|---|---|
| `useMemo` | Return VALUE of a function | Expensive computed value, stable object reference |
| `useCallback` | Function REFERENCE | Stable handler for React.memo children |
| `React.memo` | Component RENDER | Skip re-render if props unchanged |
| `useRef` | Mutable value (no re-render) | DOM refs, interval IDs, non-reactive data |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "useMemo skips the component render" | useMemo only skips the computation inside it. The component's function body still runs on every render. To skip the render, use `React.memo` on the component itself. |
| "useMemo should be used for all expensive operations by default" | useMemo has a cost: memory for cached value, shallow comparison of deps on every render, code complexity. For computations under ~1ms, the overhead may exceed the savings. Profile before adding it. |
| "useMemo with empty deps `[]` is the same as computing outside the component" | `const x = useMemo(() => expensiveOp(), [])` runs once per component instance (per mount). Computing outside the component body runs once per module import. They differ for per-instance vs per-app computation. |
| "useMemo guarantees the cache is preserved" | React may evict the useMemo cache in low-memory situations (for example, when offscreen components are suspended). Never use useMemo for correctness (if the value must be computed accurately). Only use it for performance (recomputing would give the same result). |

---

### 🚨 Failure Modes & Diagnosis

**Stale Memoised Value (Missing Dependency)**

**Symptom:** The memoised value is out of date. Changing
a filter produces the wrong filtered list.

**Root Cause:** A variable used in the computation is
not in the deps array. The cache is never invalidated.

**Diagnosis:** ESLint rule `react-hooks/exhaustive-deps`
warns about this. Look for "React Hook useMemo has a
missing dependency" warnings.

**Fix:** Add all used variables to the deps array. If
this causes too-frequent recomputation, consider
restructuring to avoid reading from state/props that
change often.

---

**useMemo Object Not Stabilising React.memo**

**Symptom:** `React.memo` child re-renders on every parent
render despite `useMemo` wrapping the prop object.

**Root Cause:** The `useMemo` deps contain a value that
changes on every render (often an object or function
created in the parent's render body).

**Diagnosis:** Check deps. If a dep is itself an object
created inline in render, it has a new reference every
render, causing `useMemo` to recompute every render.

**Fix:** Trace the unstable dep. Apply `useMemo` to it
as well, or restructure the data flow.

---

### 🔗 Related Keywords

**Prerequisites:**
- `useState Hook` - state that typically drives useMemo deps
- `React Reconciliation Algorithm` - WHY reference stability
  matters for React.memo skip logic

**Builds On:**
- `useCallback Hook` - the function-reference version of useMemo
- `React.memo` - the component-level optimisation that useMemo
  enables by providing stable references
- `React Performance Profiling` - the tooling to decide if
  useMemo is needed before adding it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ API         │ const v = useMemo(() => compute(), [deps])│
│ RECOMPUTES  │ When any dep changes (Object.is comparison)│
│ CACHES      │ One result (the last computed value)      │
├──────────────────────────────────────────────────────────┤
│ USE FOR     │ 1. Expensive computation (profiler shows  │
│             │    >16ms render time from computation)    │
│             │ 2. Stable reference for React.memo child  │
├──────────────────────────────────────────────────────────┤
│ DO NOT USE  │ String concatenation, simple math         │
│             │ Trivial array/object creation             │
│             │ Without profiling first                   │
├──────────────────────────────────────────────────────────┤
│ GOTCHAS     │ Does NOT skip component render            │
│             │ Cache may be evicted (correctness risk)   │
│             │ Missing dep = stale value (silent bug)    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `useMemo` caches the return VALUE. It does not skip
   the component render (that is `React.memo`).
2. Profile FIRST. Only add `useMemo` if the computation
   is measured as expensive. It has its own overhead.
3. The stable reference use case (enabling `React.memo`
   to work) is often more important than the computation
   caching use case.

**Interview one-liner:**
"useMemo caches a computed value between renders, recomputing
only when deps change. There are two use cases: (1) expensive
computations (sort/filter on large datasets - profiled,
not assumed), and (2) creating stable object/array references
so `React.memo` children can skip re-renders. useMemo does
NOT skip the component render itself - that is `React.memo`.
It has its own overhead (memory, deps comparison) so should
only be added after profiling confirms it is needed."

---

### 💎 Transferable Wisdom

Memoisation is a universal performance pattern: cache
expensive function results keyed by inputs, return cached
result when inputs repeat. It appears in: HTTP caching
(cache responses by URL), database query result caching,
CDN edge caching (by URL), CPU branch prediction, memoize
decorators in Python/JavaScript utility libraries. The
trade-offs are always the same: memory vs computation.
Memoisation is not always a win - for inexpensive operations
or rapidly changing inputs, the overhead of cache management
exceeds the savings. "Profile before memoising" is as true
for database query caches as it is for useMemo.

---

### 💡 The Surprising Truth

The React team's internal guidance has evolved toward
"don't manually use useMemo" in React 19+, because the
React Compiler (React Forget) automatically inserts
memoisation where the compiler determines it is beneficial.
The compiler analyses the component's dependency graph
statically and adds the equivalent of `useMemo` and
`useCallback` everywhere they could help. This means in
a React 19 + Compiler app, manually written `useMemo`
calls may actually be redundant (the compiler would have
added them anyway) or even counterproductive (if they
prevent the compiler from applying its own more precise
analysis). The skill shift: understanding the WHEN and
WHY of memoisation remains essential; the HOW (the API)
becomes secondary.

---

### ✅ Mastery Checklist

1. **PROFILE** a component using React DevTools Profiler
   to identify if a computation is causing slow renders
   (>16ms), then add `useMemo` and confirm the improvement.
2. **DEMONSTRATE** the reference stability use case: a
   `React.memo` child that unnecessarily re-renders because
   a prop is a new object each render, then fix it with
   `useMemo` and confirm the child no longer re-renders.
3. **IDENTIFY** a missing dependency bug in a useMemo call
   that causes a stale computed value, using both React
   DevTools and ESLint warnings.
4. **COMPARE** the trade-offs between computing a value
   inside render (no useMemo), useMemo, and computing outside
   the component (constant). Give examples of when each is
   appropriate.
5. **EXPLAIN** why useMemo should NOT be used for
   correctness (only performance), and give a concrete
   example where relying on useMemo cache for correctness
   would fail.

---

### 🧠 Think About This Before We Continue

**Q1.** `useMemo(() => fn, [a, b])` uses `Object.is` for
dep comparison. If `a` is a large JavaScript object passed
from a parent component, and the parent re-renders but
the object's contents have not changed (but it is a new
reference), `useMemo` still recomputes. Deep equality
comparison (Lodash `isEqual`) would be more accurate but
is expensive. How do you decide between reference equality
(fast, sometimes misses) and deep equality (slow, always
correct) for useMemo deps?

**Q2.** The React Compiler (React Forget) claims to
automatically add `useMemo` where it helps. If this
compiler ships with React 19+, what does it mean for
a codebase that already has 200 manual `useMemo` calls?
Are those calls now redundant, potentially conflicting
with the compiler, or still valid?

**Q3.** A component renders 60fps during an animation.
It has `useMemo` with a large computation that depends
on `time` (which changes every frame). What happens to
the cache? How do you handle the case where the computation
depends on a rapidly changing value, making memoisation
counterproductive?