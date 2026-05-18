---
id: RCT-033
title: React Quick Recall Card
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-001, RCT-020, RCT-021, RCT-022, RCT-023, RCT-024, RCT-026, RCT-027, RCT-032
used_by: RCT-048, RCT-065, RCT-070
related: RCT-065, RCT-070, RCT-048
tags:
  - react
  - frontend
  - reference
  - cheatsheet
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/react/react-quick-recall-card/
---

⚡ TL;DR - A dense cross-referencing map of React's
core concepts, hooks, patterns, and gotchas in one place

- for review before interviews, refreshing memory after
  a framework break, or quickly locating which concept
  to study when debugging a specific class of React problem.

| #033            | Category: React                                            | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | All foundational React entries (RCT-001 through RCT-032)   |                 |
| **Used by:**    | Testing React, React Deep-Dive Interview Questions         |                 |
| **Related:**    | React Deep-Dive Interview Questions, Staff-Level Scenarios |                 |

---

### 🔥 The Problem This Solves

**KNOWLEDGE FRAGMENTATION:**
After studying 30+ React concepts, the knowledge is
distributed across many mental boxes. Before an interview
or starting a complex feature, you need a quick high-
density recall of "what is the right thing to use here?"
This card synthesises the complete L1-L3 React picture
into a single reference with cross-links to the deep
entries.

---

### 📘 Textbook Definition

**Quick Recall Card** - a synthesis entry that provides
dense cross-referenced coverage of a topic's core patterns,
hooks, anti-patterns, and decision rules. Unlike individual
topic entries, it is designed for scanning and review,
not deep learning. Use it to: find the right API for
a problem, check decision criteria, recall the correct
pattern before writing code, or locate gaps in knowledge
for further study.

---

### ⏱️ Understand It in 30 Seconds

This is the one card to review the night before a React
interview or before starting a new React project. It maps
every concept to its "when to use" decision criterion and
the most common mistake to avoid.

---

### 🔩 First Principles Explanation

**REACT MENTAL MAP - THE FULL PICTURE:**

```
RENDERING:
  JSX → React.createElement → VDOM → DOM reconciliation
  Reconciler: finds minimal DOM changes (diffing)
  Fiber: unit of work, enables time-slicing in React 18
  Re-render trigger: setState, new props, parent re-render

COMPONENT TYPES:
  Function component: (props) => JSX  [standard]
  Class component: extends React.Component [legacy, needed
    for Error Boundaries]

DATA FLOW:
  Parent → Child: props (one-way)
  Child → Parent: callback props (lifting state up)
  Sibling → Sibling: via common parent (lifted state)
  Tree-wide: Context API (auth, theme, locale)
  Global/complex: Redux/Zustand

STATE HOOKS:
  useState      - local sync state
  useReducer    - local complex state (state machine)
  useContext    - read from context (avoids prop drilling)
  External store: useSyncExternalStore (Redux internals)

SIDE EFFECT HOOKS:
  useEffect     - after render, async work, subscriptions
  useLayoutEffect - after render, before paint, DOM measure

REF HOOKS:
  useRef        - DOM element access, mutable value (no
    re-render)

PERFORMANCE HOOKS:
  useMemo       - memoize expensive computed value
  useCallback   - memoize function reference (for
    React.memo children)
  React.memo    - skip re-render if props unchanged

CUSTOM HOOKS:
  Extract shared stateful logic → use* naming convention
  Rules of Hooks: top-level only, React functions only

FORMS:
  Controlled: value={state} + onChange={setter}
  Uncontrolled: ref={inputRef}, read on submit
  Libraries: React Hook Form (uncontrolled, fast), Formik
    (controlled)

ROUTING:
  React Router v6: <Routes> + <Route path element>
  Params: useParams(), Query: useSearchParams()
  Navigate: useNavigate(), Redirect: <Navigate to>
  Nested: <Outlet> in parent, child Route in Route

ERROR HANDLING:
  Error Boundaries: class component,
    getDerivedStateFromError
  Catches: render-phase errors
  Misses: event handlers (try/catch), async, own errors
  Library: react-error-boundary (functional wrapper)

LIFECYCLE:
  Mount: function runs + useEffect([]) fires
  Update: function re-runs + useEffect([dep]) if dep
    changed
  Unmount: useEffect cleanup function runs

CODE SPLITTING:
  React.lazy + <Suspense fallback>
  Must wrap lazy in ErrorBoundary (chunk load can fail)
  Split at route level first

CONCURRENT (React 18):
  createRoot replaces ReactDOM.render
  useTransition: mark state update as non-urgent
  useDeferredValue: defer a value, show stale during
    transition
  Suspense: boundaries now suspend during data fetching too
```

---

### 🧪 Thought Experiment

**THE DEBUGGING DECISION TREE:**

```
PROBLEM: Component not re-rendering when expected
  → Is state being mutated directly? (Should use setState)
  → Is the state update setting the same reference?
    (Object/array mutation doesn't trigger re-render)
  → Are you in a stale closure?
    (useEffect reading old value - check dependencies)
  → Is React.memo blocking it?
    (Parent re-renders but child doesn't because
      React.memo)

PROBLEM: Component re-rendering too often
  → Is state too high up? (Lifting too far causes all
    children to re-render)
  → Missing React.memo on expensive child?
  → Context value recreated on every render?
    (Move value creation into useMemo or useState)
  → Event handler recreated on every render?
    (Wrap in useCallback if passed to React.memo child)

PROBLEM: useEffect running infinitely
  → Object/array/function in dependencies array
    (New reference every render = new dep = infinite loop)
  → Fix: useMemo for objects/arrays, useCallback for
    functions

PROBLEM: Stale value in useEffect
  → Reading a variable not in deps array
  → Fix: add to deps array or use functional setState
```

---

### 🧠 Mental Model / Analogy

> React is a UI state machine. State is the input;
> JSX is the output. Every render is a pure function:
> `(state, props) → JSX`. Hooks are the inputs
> you declare at component level. Effects are the
> side-channels to the outside world (DOM, API, timer).
> The reconciler is the diff engine that converts
> two JSX outputs into minimal DOM operations.
> Context is the ambient broadcast channel. Router
> is the URL-to-JSX mapping. Error Boundaries are
> the try/catch for the render phase.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (core loop):**
State changes → component re-renders → new JSX → React
updates the DOM. That is the entire React model.

**Level 2 (hooks):**
useState for values. useEffect for side effects. useRef
for mutable non-state values. useMemo/useCallback for
performance. useContext for cross-tree state.

**Level 3 (patterns):**
Lifting state up for sibling communication. Context for
deep tree sharing. Controlled inputs for forms. Error
Boundaries for render failures. React.memo for re-render
prevention.

**Level 4 (advanced):**
useReducer for state machines. Custom hooks for shared
logic. Code splitting with lazy/Suspense. Concurrent
features (useTransition) for non-blocking UI updates.

**Level 5 (architecture):**
Server Components for zero-bundle server-rendered components.
Streaming SSR. React Fiber internals. Lane priorities.
Algebraic effects research influence on hook design.

---

### ⚙️ How It Works (Mechanism)

**HOOKS DECISION TABLE:**

```
WHAT I NEED                        HOOK / PATTERN
──────────────────────────────────────────────────
Store a value, trigger re-render   useState
Complex state with actions          useReducer
Read context value                  useContext
DOM element reference               useRef
Mutable value (no re-render)        useRef
Run after render (API, timer)       useEffect
Run after render, before paint      useLayoutEffect
Expensive computed value            useMemo
Stable function reference           useCallback
Skip child re-render                React.memo
Catch render errors                 Error Boundary (class)
Cross-tree state                    createContext +
  Provider
Shared stateful logic               Custom hook (use*)
Async state updates (non-urgent)    useTransition
Defer a value while loading         useDeferredValue
Read async resource during render   use() (React 19)
```

---

### 💻 Code Example

**The "complete component" - reference implementation:**

```jsx
// A component that uses most core patterns correctly
import { useState, useEffect, useCallback, useRef } from "react";

function ProductSearch({ onSelect }) {
  // State
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("idle");

  // Ref for focus management (DOM access)
  const inputRef = useRef(null);

  // Stable callback for child (useCallback for React.memo child)
  const handleSelect = useCallback(
    (product) => {
      onSelect(product);
      setQuery("");
      setResults([]);
    },
    [onSelect],
  );

  // Side effect: fetch on query change
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    setStatus("loading");
    fetch(`/api/products?q=${encodeURIComponent(query)}`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.status);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) {
          setResults(data);
          setStatus("idle");
        }
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          if (!cancelled) setStatus("error");
        }
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [query]);

  // Focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div>
      <input
        ref={inputRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search products..."
      />
      {status === "loading" && <span>Searching...</span>}
      {status === "error" && <span>Search failed</span>}
      <ul>
        {results.map((p) => (
          <ProductItem key={p.id} product={p} onSelect={handleSelect} />
        ))}
      </ul>
    </div>
  );
}

// React.memo prevents re-render when ProductSearch state changes
// but this product's props haven't changed
const ProductItem = React.memo(function ProductItem({ product,
    onSelect }) {
  return (
    <li>
      {product.name}
      <button onClick={() => onSelect(product)}>Select</button>
    </li>
  );
});
```

---

### 📊 Comparison Table

| Concept        | When to use                         | Common mistake                       | Entry   |
| -------------- | ----------------------------------- | ------------------------------------ | ------- |
| useState       | Local synchronous state             | Mutating state directly              | RCT-020 |
| useEffect      | Side effects after render           | Missing/wrong deps                   | RCT-021 |
| useContext     | Cross-tree shared state             | High-freq state in context           | RCT-022 |
| useRef         | DOM access, mutable non-state       | Using for state (causes bugs)        | RCT-023 |
| useMemo        | Expensive computed values           | Premature optimisation               | RCT-035 |
| useCallback    | Stable fn ref for React.memo        | Without React.memo on child          | RCT-036 |
| React.memo     | Skip expensive child re-renders     | Without useCallback on handlers      | RCT-037 |
| useReducer     | State machines, complex transitions | Using where useState is enough       | RCT-034 |
| Error Boundary | Render-phase error containment      | Expecting it to catch async errors   | RCT-028 |
| Lifting state  | Sibling communication               | Lifting too high (causes prop drill) | RCT-029 |
| Context        | Cross-cutting concerns              | High-frequency values (perf issue)   | RCT-022 |

---

### ⚠️ Common Misconceptions

| Misconception                                                                  | Reality                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "React re-renders are expensive and must be minimised with useMemo everywhere" | Re-renders are cheap in React for most components. The bottleneck is usually the DOM update, not the JavaScript re-render. Profile before optimising. Premature useMemo adds cost (the memoization itself) and complexity without benefit.       |
| "useEffect runs after every render by default"                                 | useEffect with `[]` runs once (mount). With `[deps]`, it runs when deps change. With no argument, it runs after every render - which is rarely what you want and usually a bug waiting to happen.                                                |
| "Context causes the entire app to re-render"                                   | Only components that call `useContext(SomeContext)` re-render when that context's value changes. Components that do not consume the context are unaffected. The risk is if many components consume the same context with a high-frequency value. |
| "React.memo makes components never re-render"                                  | React.memo skips re-render if props are shallowly equal (same references). Passing a new object/array/function literal as a prop every render defeats React.memo because `{} !== {}` (new reference each render).                                |

---

### 🚨 Failure Modes & Diagnosis

**Infinite useEffect Loop**

**Pattern that causes it:**

```jsx
// This loops forever:
const [data, setData] = useState({});
useEffect(() => {
  setData({ processed: true });
}, [data]);
// data changes → effect runs → setData → data changes → ...
```

**Diagnosis:** React DevTools shows rapid re-renders.

**Fix:** Review the dependency array. Remove the circular
dep or use a ref to break the cycle.

---

**Stale Closure in useEffect**

**Pattern that causes it:**

```jsx
const [count, setCount] = useState(0);
useEffect(() => {
  const id = setInterval(() => {
    console.log(count); // always logs 0 (stale closure!)
  }, 1000);
  return () => clearInterval(id);
}, []); // count not in deps - closure captures initial value
```

**Fix:** Add `count` to deps (re-creates interval on change).
Or use functional setState: `setCount(prev => prev + 1)`.

---

### 🔗 Related Keywords

**This card synthesises:**

- Core: RCT-001 through RCT-010 (fundamentals)
- Hooks: RCT-020 through RCT-024
- Patterns: RCT-025 through RCT-032
- Performance: RCT-035, RCT-036, RCT-037, RCT-039

**Leads to:**

- `React Deep-Dive Interview Questions` (RCT-065)
- `Staff-Level React Architecture Interview Scenarios` (RCT-070)
- `Testing React with RTL` (RCT-048)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RE-RENDER   │ setState, new props, parent re-render     │
│ SKIP RENDER │ React.memo + stable props references      │
├─────────────────────────────────────────────────────────┤
│ SIDE EFFECTS│ useEffect - after render                  │
│ DEPS ARRAY  │ [] once, [x] on x change, none = always  │
│ CLEANUP     │ return fn in useEffect (unmount)          │
├─────────────────────────────────────────────────────────┤
│ DATA FLOW   │ Down: props | Up: callbacks | Wide: Contex│
├─────────────────────────────────────────────────────────┤
│ FORMS       │ Controlled: value+onChange (real-time)    │
│             │ Uncontrolled: ref (submit-only)           │
├─────────────────────────────────────────────────────────┤
│ ERRORS      │ Error Boundary: render errors only        │
│             │ try/catch: event handlers + async         │
├─────────────────────────────────────────────────────────┤
│ GOTCHAS     │ Stale closure, object in deps, direct     │
│             │ mutation, setInterval in useEffect        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Every re-render is a function call. Hooks call order
   must be stable. Deps array controls when effects run.
2. Data flows down (props), up (callbacks), wide (Context).
   Lift state to the LOWEST common ancestor.
3. useMemo/useCallback/React.memo are performance
   optimisations - profile before using them.

**Interview one-liner:**
"React re-renders a component when state or props change,
producing new JSX that the reconciler uses to update the
DOM minimally. Hooks declare dependencies: useState for
state, useEffect for side effects (run after render,
cleanup on unmount), useRef for mutable values/DOM access,
useMemo/useCallback for performance. Data flows down via
props, up via callbacks, and across via Context. Lift
state to the lowest common ancestor; use Context for
cross-cutting concerns; React.memo to skip re-renders
when props are unchanged."

---

### 💎 Transferable Wisdom

React's design principles generalise to architecture at
large: (1) Unidirectional data flow prevents debugging
nightmares caused by two-way binding. (2) Immutability
(setState creates new values, not mutations) makes change
detection trivial and enables time-travel debugging.
(3) Separation of state from rendering enables optimisation,
testing, and server rendering. (4) Composition over
inheritance allows flexible reuse without rigid class
hierarchies. These are not React-specific - they are
software engineering principles that React enforces at
the UI framework level.

---

### 💡 The Surprising Truth

The React codebase has two entirely separate reconcilers:
`react-dom` for browsers and `react-native` for native
apps. The same component code (JSX, hooks, state) runs
on both. This is only possible because React's model is
completely decoupled from the output medium. JSX produces
a description of what to render (React elements), not
actual DOM nodes. The reconciler chooses what to create
from that description. This "description, not implementation"
principle enables React Native, React VR, React Test
Renderer, and hypothetically any future rendering target.
The virtual DOM is not a performance trick - it is the
abstraction layer that enables React's platform agnosticism.

---

### ✅ Mastery Checklist

1. **DESCRIBE** without notes the complete React rendering
   cycle: from `setState` call to DOM update, naming every
   step (scheduler, reconciler, Fiber, diffing, commit).
2. **REPRODUCE** from memory the correct patterns for:
   one-time fetch, filtered fetch with cancel, controlled
   form with validation, debounced input, list with stable
   keys.
3. **DIAGNOSE** from symptoms: infinite loop, stale closure,
   missing dependency warning, performance regression from
   context.
4. **DECIDE** for any given state management scenario:
   useState vs useReducer vs Context vs Zustand vs Redux.
5. **EXPLAIN** the distinction between server state and
   client state and why React Query exists to manage the
   former separately from the latter.

---

### 🧠 Think About This Before We Continue

**Q1.** You are doing a React code review. You see a
component that has 8 `useState` calls, 3 `useEffect` calls,
and 2 `useMemo` calls. At what point is this a signal
that refactoring is needed? What are the specific triggers
(not just "too many") that indicate the component should
be split or the state model changed?

**Q2.** React's rules of hooks ("only call hooks at the
top level," "only call hooks from React functions") seem
like arbitrary constraints. What is the architectural
reason for each rule? What specifically breaks if you
call a hook conditionally?

**Q3.** The React team has talked about a "React compiler"
(React Forget) that automatically adds `useMemo` and
`useCallback` everywhere they are needed, removing the
need for developers to manually write them. If this shipped
to production, which of the patterns in this entry would
become obsolete, and which would remain?
