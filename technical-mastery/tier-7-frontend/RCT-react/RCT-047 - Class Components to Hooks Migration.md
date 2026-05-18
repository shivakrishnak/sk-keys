---
id: RCT-047
title: Class Components to Hooks Migration
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-005, RCT-019, RCT-021, RCT-024, RCT-042
used_by: RCT-063
related: RCT-005, RCT-019, RCT-021, RCT-042
tags:
  - react
  - frontend
  - migration
  - hooks
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/react/class-components-to-hooks-migration/
---

⚡ TL;DR - Migrating class components to hooks converts
lifecycle methods to `useEffect`, `this.state` to
`useState`, and class-based logic sharing (HOCs, render
props) to custom hooks; two lifecycle methods have no
direct hook equivalent: `getSnapshotBeforeUpdate` and
`componentDidCatch` (Error Boundaries remain class-only);
migrate incrementally by converting one component at a
time rather than rewriting the whole app.

| #047            | Category: React                                                                        | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | React Components, useState Hook, useEffect Hook, Custom Hooks, Higher-Order Components |                 |
| **Used by:**    | React v18 Concurrent Features Migration                                                |                 |
| **Related:**    | React Components, useState, useEffect, HOCs                                            |                 |

---

### 🔥 The Problem This Solves

**LEGACY CLASS COMPONENT CODEBASES:**
Class components were React's primary API from 2013 to
2019 (React 16.8). Most React codebases older than 5
years contain class components. Class components are
not deprecated - they still work in React 18+ - but:

- They cannot use hooks (no `useState`, `useEffect` in classes)
- Their logic reuse patterns (HOCs, render props) are more
  complex and less composable than custom hooks
- Lifecycle methods (componentDidUpdate) are harder to
  reason about than dependency arrays
- New React features (Concurrent Mode, Server Components)
  are designed around hooks

Migration is a business decision: not required, but
enables better code organisation, simpler logic reuse,
and access to the full modern React ecosystem.

---

### 📘 Textbook Definition

**Class Component to Hooks Migration** - the process of
converting React class components (which use lifecycle
methods like `componentDidMount`, `componentDidUpdate`,
`componentWillUnmount`, and `this.state`) to functional
components with hooks (`useState`, `useEffect`, `useRef`,
`useContext`, and custom hooks). The key principle is
incremental, component-by-component conversion - React
class and functional components can coexist in the same
application.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// CLASS COMPONENT:
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  componentDidMount() {
    document.title = `Count: 0`;
  }
  componentDidUpdate() {
    document.title = `Count: ${this.state.count}`;
  }
  componentWillUnmount() {
    document.title = "App";
  }

  render() {
    return (
      <button onClick={() => this.setState((s) => ({ count: s.count +
          1 }))}>
        Count: {this.state.count}
      </button>
    );
  }
}

// EQUIVALENT FUNCTIONAL + HOOKS:
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `Count: ${count}`;
    return () => {
      document.title = "App";
    };
  }, [count]);

  return <button onClick={() => setCount((c) => c +
      1)}>Count: {count}</button>;
}
```

---

### 🔩 First Principles Explanation

**LIFECYCLE → HOOK MAPPING:**

```
Class Component          Hooks Equivalent
─────────────────────────────────────────────────────────
constructor(props)     → useState(initialValue)
                         (initialValue can be a function:
                           useState(() => ...)
                          for expensive initialisation)

render()               → the function body (return JSX)

componentDidMount      → useEffect(() => { ... }, [])
                         (empty deps: runs once after
                           first render)

componentDidUpdate     → useEffect(() => { ... }, [dep1,
  dep2])
                         (runs when dep1 or dep2 changes)
                         Note: useEffect ALWAYS runs after
                           first render too
                         (no equivalent to "only on
                           update, skip mount")

componentWillUnmount   → useEffect cleanup: return () => {
  ... }

this.state.x           → const [x, setX] =
  useState(initialX)

this.setState({ x })   → setX(value)
this.setState(fn)      → setX(fn)  (functional update)

this.props             → function props parameter

this.ref = createRef() → const ref = useRef(null)
this.ref.current       → ref.current

getDerivedStateFromProps → not a hook; compute during
  render:
                           const derivedValue =
                             derive(props, state)

shouldComponentUpdate  → React.memo (for the whole
  component)
                         or useMemo for specific expensive
                           values

componentDidCatch      → NO HOOK EQUIVALENT (still
  requires class)
getSnapshotBeforeUpdate→ NO HOOK EQUIVALENT (still
  requires class)
```

---

### 🧪 Thought Experiment

**THE SUBSCRIPTION COMPONENT:**
A complex class component subscribes to a data store on
mount and unsubscribes on unmount. It also updates
document.title on every render. It uses `componentDidUpdate`
to call an analytics API when the data changes.

In a class, these three concerns are spread across three
lifecycle methods. The "data store subscription" code
is split between `componentDidMount` and `componentWillUnmount`.

In hooks, each concern becomes a separate `useEffect`:

- One for document.title (tracks data dependency)
- One for store subscription (empty deps, cleanup returns unsubscribe)
- One for analytics (tracks data dependency)

The hooks version co-locates setup and teardown in the
same effect. The class version separates them across
lifecycle methods. This is the fundamental readability
win of hooks over lifecycle methods.

---

### 🧠 Mental Model / Analogy

> Class components organise code by WHEN it runs (mount,
> update, unmount - lifecycle phases). Hooks organise
> code by WHAT it does (subscribe to store, update title,
> send analytics - concerns).
>
> Class: "At mount time: subscribe to store AND set title.
> At unmount time: unsubscribe AND clear title."
> (two concerns mixed per lifecycle method)
>
> Hooks: "For the store concern: setup on mount, cleanup on unmount."
> "For the title concern: run when data changes."
> (each concern has its own setup + cleanup pair)

---

### 📶 Gradual Depth - Five Levels

**Level 1 (basic mapping):**
`this.state` → `useState`. `componentDidMount` + `componentWillUnmount`
→ `useEffect(() => { setup; return cleanup; }, [])`.
`componentDidUpdate` with condition → `useEffect(() =>
{ ... }, [dep])`. `this.props` → function arguments.

**Level 2 (multiple state variables):**
Class components have one `this.state` object with multiple
fields. Hooks: split into multiple `useState` calls or
use `useReducer` for complex state (multiple related
fields that update together). Prefer multiple `useState`
for independent fields, `useReducer` when updates are
complex or inter-dependent.

**Level 3 (logic extraction):**
After converting to hooks, extract repeated logic into
custom hooks. A class component with subscription logic
becomes a `useSubscription(store)` custom hook reusable
across components. This is the actual benefit: not just
the syntax, but the composability.

**Level 4 (no exact equivalents):**
Two class lifecycle methods have no hook equivalent:
`componentDidCatch` and `getSnapshotBeforeUpdate`. Error
Boundaries must remain class components. For `getSnapshotBeforeUpdate`
(reading DOM before it updates, e.g., preserving scroll
position): use `useLayoutEffect` with a ref to simulate
it, or keep the class component.

**Level 5 (migration strategy):**
Incremental migration strategy for large codebases:
(1) Add linting to detect class components in new files
(new code must be functional). (2) Migrate components
bottom-up (leaf components first, containers last).
(3) Extract shared HOC/render prop logic into custom
hooks as you migrate each consumer. (4) Leave Error
Boundaries as class components (no need to migrate).
(5) Use `React.memo` to replicate `shouldComponentUpdate`
at the component boundary.

---

### ⚙️ How It Works (Mechanism)

**Full class to hooks migration walkthrough:**

```jsx
// BEFORE: class component with multiple lifecycle methods
class DataTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      loading: true,
      error: null,
      sortColumn: null,
    };
    this.subscription = null;
  }

  componentDidMount() {
    this.subscription = dataStore.subscribe(this.handleUpdate);
    this.fetchData(this.props.tableId);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.tableId !== this.props.tableId) {
      this.fetchData(this.props.tableId);
    }
  }

  componentWillUnmount() {
    this.subscription?.unsubscribe();
  }

  handleUpdate = (newData) => {
    this.setState({ data: newData });
  };

  fetchData = (id) => {
    this.setState({ loading: true, error: null });
    fetch(`/api/tables/${id}`)
      .then((r) => r.json())
      .then((data) => this.setState({ data, loading: false }))
      .catch((e) => this.setState({ error: e, loading: false }));
  };

  render() {
    const { data, loading, error, sortColumn } = this.state;
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <Table data={data} sortColumn={sortColumn} />;
  }
}

// AFTER: functional component with hooks
function DataTable({ tableId }) {
  // State: each concern as separate useState
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortColumn, setSortColumn] = useState(null);

  // Effect 1: store subscription (setup + cleanup in same effect)
  useEffect(() => {
    const subscription = dataStore.subscribe((newData) => {
      setData(newData);
    });
    return () => subscription.unsubscribe();
  }, []); // subscribe once

  // Effect 2: data fetching (re-runs when tableId changes)
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetch(`/api/tables/${tableId}`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setLoading(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [tableId]);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <Table data={data} sortColumn={sortColumn} />;
}
// Optional: extract further into custom hooks:
// const { data, loading, error } = useTableData(tableId);
// const subscription = useDataStoreSubscription(handler);
```

---

### 💻 Code Example

**BAD: Partial migration that breaks the component:**

```jsx
// BAD: mixing hooks and class component incorrectly
// Hooks CANNOT be used in class components
class Counter extends React.Component {
  render() {
    const [count, setCount] = useState(0); // ERROR!
    // React Error: Invalid hook call. Hooks can only be
    // called inside of the body of a function component.
    return <button onClick={() => setCount((c) => c +
        1)}>{count}</button>;
  }
}
```

**GOOD: Incremental migration - convert one component fully:**

```jsx
// GOOD: fully converted to functional component
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount((c) => c +
      1)}>{count}</button>;
}
// The class version can be deleted entirely.
// Parent components do not need to change (same API).
```

---

### 📊 Comparison Table

| Class                      | Hooks                                      | Notes                                   |
| -------------------------- | ------------------------------------------ | --------------------------------------- |
| `this.state = { x: 0 }`    | `const [x, setX] = useState(0)`            | Multiple useState for independent state |
| `this.setState({ x: v })`  | `setX(v)`                                  |                                         |
| `this.setState(fn)`        | `setX(fn)`                                 | Functional update (same pattern)        |
| `componentDidMount`        | `useEffect(() => {}, [])`                  | Empty deps                              |
| `componentWillUnmount`     | `useEffect(() => { return () => {} }, [])` | Cleanup function                        |
| `componentDidUpdate(prev)` | `useEffect(() => {}, [dep])`               | With relevant deps                      |
| `this.props.x`             | `x` in function params                     |                                         |
| `this.ref = createRef()`   | `const ref = useRef(null)`                 |                                         |
| `shouldComponentUpdate`    | `React.memo`                               | Component-level                         |
| `componentDidCatch`        | No hook (keep class)                       | Error Boundary: class only              |

---

### ⚠️ Common Misconceptions

| Misconception                                                                                  | Reality                                                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Migrating to hooks requires rewriting the whole app"                                          | Migration is incremental. Class and functional components can coexist in the same application. Migrate leaf components first, then containers. Error Boundaries can remain class components permanently.                                                                                                                                             |
| "useEffect is exactly like componentDidMount/componentDidUpdate/componentWillUnmount combined" | Close, but not exact. `useEffect` with `[]` runs AFTER the first render (like componentDidMount). But componentDidUpdate with a condition check (`if (prev.x !== this.props.x)`) is slightly different from `useEffect([x])` which ALWAYS runs after mount AND when x changes. There is no hook-only equivalent of "skip mount, only run on update." |
| "You must use useReducer when migrating from class components"                                 | Not required. Multiple `useState` calls are the idiomatic equivalent of multiple `this.state` fields. `useReducer` is preferred when you have complex state logic (multiple related fields that update together) - which is when class components had complex setState logic too.                                                                    |
| "Class components are deprecated"                                                              | Class components are NOT deprecated. The React team has explicitly stated they will remain supported. Error Boundaries require class components to this day (2024). The recommendation is to write NEW code with hooks, but there is no urgency to migrate existing class code.                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**useEffect Runs Twice on Mount in Development (StrictMode)**

**Symptom:** After migrating, data is fetched twice on
page load in development. Subscriptions fire twice.

**Root Cause:** React 18 StrictMode intentionally mounts
effects twice (mount → unmount → mount) to detect missing
cleanup. This is development-only behaviour.

**Fix:** Ensure effects have correct cleanup functions:

```jsx
useEffect(() => {
  const sub = store.subscribe(handler);
  return () => sub.unsubscribe(); // cleanup: unsubscribe
}, []);
// In StrictMode: subscribes, unsubscribes, subscribes again
// Correct: net result is one subscription
```

If the effect has no cleanup and should not run twice,
that is a signal the effect is not correctly isolated
from external systems.

---

### 🔗 Related Keywords

**Prerequisites:**

- `React Components` - class component fundamentals
- `useState Hook`, `useEffect Hook` - the primary migration targets
- `Custom Hooks` - the destination for extracted logic
- `Higher-Order Components` - class-era pattern being replaced

**Builds On:**

- `React v18 Concurrent Features Migration` - broader React
  version migration that builds on hooks migration

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STRATEGY  │ Incremental: one component at a time        │
│ ORDER     │ Leaf components first, containers last      │
│ KEEP      │ Error Boundaries (no hook equivalent)       │
├─────────────────────────────────────────────────────────┤
│ this.state → useState (split by concern)                │
│ componentDidMount → useEffect(fn, [])                   │
│ componentWillUnmount → useEffect cleanup return         │
│ componentDidUpdate → useEffect(fn, [deps])              │
│ this.props → function parameters                        │
│ createRef → useRef(null)                                │
├─────────────────────────────────────────────────────────┤
│ NO HOOK   │ componentDidCatch, getSnapshotBeforeUpdate  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Lifecycle methods → `useEffect` with the right deps.
   Mount + unmount in the same effect (setup + cleanup
   return). Update when dep changes: `useEffect(fn, [dep])`.
2. Error Boundaries require class components. They are
   NOT deprecated. No hook equivalent exists.
3. Migration is incremental. Leaf components first.
   Class and functional coexist until all are migrated.

**Interview one-liner:**
"Migrating class components to hooks converts lifecycle
methods to `useEffect`, `this.state` to `useState`, and
logic sharing patterns (HOCs, render props) to custom
hooks. The key non-equivalences: `useEffect` always runs
on mount AND when deps change (no 'skip first render'),
and Error Boundaries have no hook equivalent (still
require class components). Migration is incremental:
class and functional components coexist. Start with leaf
components. The actual win is not just syntax - it is
the ability to extract logic into custom hooks for
composable, testable reuse."

---

### 💎 Transferable Wisdom

The class-to-hooks migration reflects a broader pattern
in software: the shift from organising code by LIFECYCLE
PHASE (when it runs) to organising by CONCERN (what
it does). This appears in many contexts: early Java
enterprise code organised by layers (DAO, Service, Controller)
vs domain-driven design organised by domain concepts
(Order, Payment, Inventory). Spring's @Configuration
classes vs XML configuration files. Kubernetes manifests
vs imperative kubectl commands. In each case, the newer
approach co-locates related code regardless of its
execution phase. This makes individual concerns easier
to understand, test, and modify in isolation. The same
refactoring principle applies: identify concerns, co-locate
related code, extract reusable logic.

---

### 💡 The Surprising Truth

React's class component API was explicitly designed to
feel familiar to developers coming from object-oriented
backgrounds. The lifecycle methods (`componentDidMount`,
etc.) map to concepts from desktop UI frameworks
(Android's `onCreate`, iOS's `viewDidLoad`). Hooks were
designed as a complete departure from this - no classes,
no lifecycle methods, no `this`. The React team expected
significant pushback from the community when hooks were
announced at React Conf 2018. Instead, the community
reaction was overwhelmingly positive, and adoption was
faster than the team expected. Within 18 months of
release, most new React code used hooks. The speed of
adoption surprised the React team itself - they expected
a much longer transition period.

---

### ✅ Mastery Checklist

1. **CONVERT** a class component with all four main
   lifecycles (constructor, componentDidMount, componentDidUpdate,
   componentWillUnmount) to a functional component with hooks.
2. **EXTRACT** the converted component's logic into a
   custom hook. Show that the component becomes simpler
   and the hook is reusable.
3. **IDENTIFY** a case where the migration is NOT
   straightforward: a class component using `getSnapshotBeforeUpdate`
   for scroll preservation. Explain the limitation and
   the workaround.
4. **VERIFY** that your migrated component behaves
   identically to the class version: same props accepted,
   same rendered output, same side effects. Write a test
   that passes for both.
5. **EXPLAIN** to a team why Error Boundaries must remain
   class components and show what a class-based Error
   Boundary looks like vs a hypothetical hook-based
   one (and why the hook version cannot be implemented).

---

### 🧠 Think About This Before We Continue

**Q1.** A class component uses `shouldComponentUpdate`
with complex logic: it re-renders only if certain nested
properties of an object prop have changed (deep equality
check). When converting to hooks, you use `React.memo`
with a custom comparison function. How does the custom
comparison function in `React.memo` differ from
`shouldComponentUpdate` semantically? (Hint: the boolean
return value means the opposite.)

**Q2.** A class component stores a timer ID in `this.timerID`
(not in state, because changing it should not trigger
a re-render). When migrating to hooks, you cannot use
a local variable (it would be recreated each render).
`useState` would cause re-renders. What is the correct
hook, and why does it solve this problem?

**Q3.** React 18 added `useId()`, `useSyncExternalStore()`,
and `useInsertionEffect()` - hooks designed for library
authors. If a large class component codebase was built
on a custom event bus for state management (a pattern
from 2016-2018), and you are migrating to hooks, which
of the React 18 hooks might be relevant for replacing
the event bus subscription pattern? How does
`useSyncExternalStore` relate to the pre-hooks subscription
pattern in class components?
