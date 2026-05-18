---
id: RCT-037
title: React.memo
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-011, RCT-035, RCT-036, RCT-039
used_by: RCT-049, RCT-052, RCT-063
related: RCT-035, RCT-036, RCT-049
tags:
  - react
  - frontend
  - performance
  - memoisation
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/react/react-memo/
---

⚡ TL;DR - `React.memo(Component)` wraps a component and
skips its re-render if all props are shallowly equal to
the previous render - it is the component-level cache,
equivalent to `shouldComponentUpdate` for class components;
it only works correctly when props containing objects,
arrays, and functions are stabilised with `useMemo` and
`useCallback` in the parent.

| #037            | Category: React                                                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual DOM and Reconciliation, useMemo Hook, useCallback Hook, React Reconciliation Algorithm |                 |
| **Used by:**    | React Performance Profiling, React Fiber Architecture, v18 Concurrent Migration                |                 |
| **Related:**    | useMemo Hook, useCallback Hook, React Performance Profiling                                    |                 |

---

### 🔥 The Problem This Solves

**PARENT RE-RENDERS CAUSE ALL CHILDREN TO RE-RENDER:**
React's default behaviour: when a parent component's state
changes, every child component re-renders - regardless
of whether the child's props changed. For a large list
with 1,000 items, updating one counter in the parent
causes all 1,000 item components to re-render, even though
they all received the same props they had before.

For simple components this is fine - re-renders are fast.
For expensive components (complex animations, large DOM
trees, expensive computations in the render body),
unnecessary re-renders are noticeable performance issues.
`React.memo` adds a guard: "only re-render if props
changed."

---

### 📘 Textbook Definition

**React.memo** - a Higher-Order Component (HOC) that wraps
a functional component and adds prop memoisation. On
re-render, React compares each prop to its previous
value using shallow equality (`Object.is`). If all props
are equal (same primitive values or same object/function
references), React skips the component's render and
returns the previous render result. If any prop has
changed, React re-renders the component normally. The
component itself is unchanged - `React.memo` is purely
a wrapper optimisation.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// Without React.memo: re-renders whenever parent renders,
// regardless of whether its own props changed
function ExpensiveItem({ item, onDelete }) {
  // ... expensive render work
  return (
    <div>
      {item.name} <button onClick={() => onDelete(item.id)}>X</button>
    </div>
  );
}

// With React.memo: only re-renders if item or onDelete changed
const ExpensiveItem = React.memo(function ({ item, onDelete }) {
  // ... expensive render work
  return (
    <div>
      {item.name} <button onClick={() => onDelete(item.id)}>X</button>
    </div>
  );
});

// For React.memo to work, the parent must:
// - pass stable item references (useMemo or stable data)
// - pass stable onDelete function (useCallback)
```

---

### 🔩 First Principles Explanation

**HOW REACT.MEMO WORKS:**

```
Without React.memo:
  Parent re-renders
  → React calls Child() (always)
  → New JSX output
  → Reconciler diffs with previous output
  → Updates DOM if changed

With React.memo:
  Parent re-renders
  → React checks: are all props shallowly equal?
    YES: skip calling Child(), return previous JSX
    NO:  call Child(), produce new JSX, diff, update DOM

The guard is BEFORE calling the function component.
Checking props is O(n) in number of props.
```

**SHALLOW EQUALITY:**

```
Object.is(a, b):
  Primitive values: true if same value (1===1, 'a'==='a')
  Objects/arrays:   true ONLY if same reference (same
    object in memory)

React.memo uses Object.is for each prop:
  item={{ id: 1, name: 'Foo' }}  ← new object every render
    → Object.is(prev, next) = false (different reference)
    → React.memo does NOT skip render (broken)

  item={stableItemRef}  ← same reference from useMemo/store
    → Object.is(prev, next) = true
    → React.memo DOES skip render (correct)
```

**THE THREE LEVERS:**
React.memo works correctly only when all three are in place:

```
1. React.memo wraps the child component
2. Object/array props are stable references (useMemo in
  parent)
3. Function props are stable references (useCallback in
  parent)
```

Missing any one breaks the optimisation silently.

---

### 🧪 Thought Experiment

**THE 1,000-ROW PROBLEM:**
A list renders 1,000 `<ProductRow>` components. A filter
input at the top changes when the user types. Every
keystroke triggers a parent re-render. Without `React.memo`:
1,000 `ProductRow` renders per keystroke. With `React.memo`
and stable props (the product data from a stable array
reference, the `onDelete` handler from `useCallback`):
1,000 prop comparisons (fast, O(n) props) instead of
1,000 render function calls (slow, O(render complexity)).

Whether this matters depends on how expensive each
`ProductRow` render is. If each row renders in 0.01ms,
1,000 renders = 10ms - near the 16ms frame budget.
Adding `React.memo` reduces to ~0ms for unchanged rows.

---

### 🧠 Mental Model / Analogy

> `React.memo` is like a smart receptionist who checks
> a visitor's ID before letting them into the building
> (the component renders). If the ID is identical to
> the last visit (same props), the receptionist turns
> them away: "Nothing changed, no need to enter." If
> anything is different, they are allowed in to do their
> work.
>
> The receptionist uses surface-level checks (shallow
> equality) - they look at the photo (reference check)
> not verify every detail of the ID (deep equality).
> If the visitor brings a new ID card with the same
> information but a different card (new object reference
> for the same data), the receptionist will not recognise
> them as the same visitor and lets them in unnecessarily.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`React.memo(Component)` skips a component's re-render
if its props are the same as last time. Use it for
expensive components that re-render too often.

**Level 2 (usage):**
Wrap the component: `export default React.memo(MyComponent)`.
Or: `const Memoised = React.memo(function MyComponent(...) { ... })`.
For correct behaviour, parent must pass stable prop references.

**Level 3 (custom comparator):**
Second argument: `React.memo(Component, (prev, next) =>
boolean)`. Return `true` to skip render (props equal),
`false` to re-render. Custom comparator enables deep equality
or selective prop comparison. But: custom comparators
are rarely needed and add maintenance burden.

**Level 4 (class component equivalent):**
`React.memo` for function components = `PureComponent`
for class components = `shouldComponentUpdate() { return
shallowEqual(this.props, nextProps); }`. The same concept:
avoid re-rendering when props have not meaningfully changed.

**Level 5 (mastery):**
In React 18 concurrent mode, React may render components
multiple times before committing (intentional retries,
interrupted renders). `React.memo` only guards the commit
path - during concurrent render, React may still call
the component multiple times as part of its scheduler.
The profiler shows "render time" which includes concurrent
retries. Measuring the benefit of `React.memo` accurately
requires looking at committed renders in the profiler,
not total render calls.

---

### ⚙️ How It Works (Mechanism)

**Correctly applying the React.memo pattern:**

```jsx
// Parent component manages list state
function TaskManager() {
  const [tasks, setTasks] = useState(initialTasks);
  const [filter, setFilter] = useState("all");

  // Stable handler: only recreated if setTasks changes (never)
  const handleComplete = useCallback((id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: true } : t)),
    );
  }, []);

  // Stable handler: same
  const handleDelete = useCallback((id) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Filtered list: recomputed only when tasks or filter changes
  const visibleTasks = useMemo(() => {
    if (filter === "all") return tasks;
    return tasks.filter((t) =>
      filter === "active" ? !t.completed : t.completed,
    );
  }, [tasks, filter]);

  return (
    <div>
      <FilterBar filter={filter} onFilterChange={setFilter} />
      {visibleTasks.map((task) => (
        <TaskRow
          key={task.id}
          task={task}
          onComplete={handleComplete} // stable reference
          onDelete={handleDelete} // stable reference
        />
      ))}
    </div>
  );
}

// TaskRow: only re-renders when task, onComplete, or onDelete changes
// task objects from state are stable references unless that task
// changed
const TaskRow = React.memo(function TaskRow({ task, onComplete,
    onDelete }) {
  return (
    <div className={task.completed ? "done" : ""}>
      <span>{task.title}</span>
      <button onClick={() => onComplete(task.id)}>Complete</button>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  );
});
```

---

### 💻 Code Example

**BAD: React.memo with unstable props (no effect):**

```jsx
// BAD: React.memo applied but props are new on every render
function Parent({ items }) {
  return items.map((item) => (
    // New inline function on every render → not stable
    // New inline object on every render → not stable
    // React.memo on Child is COMPLETELY bypassed
    <Child
      key={item.id}
      item={item}
      config={{ sortable: true }} // new object each render
      onSelect={(id) => selectItem(id)} // new function each render
    />
  ));
}
const Child = React.memo(function ({ item, config, onSelect }) {
  // This still re-renders every time Parent renders
  // because config and onSelect are always new references
  return <div>{item.name}</div>;
});
```

**GOOD: React.memo with stable props:**

```jsx
// GOOD: stable config and handlers
const CHILD_CONFIG = { sortable: true };
// defined outside (module level)
// or useMemo inside component

function Parent({ items }) {
  const handleSelect = useCallback((id) => selectItem(id), []);

  return items.map((item) => (
    <Child
      key={item.id}
      item={item}
      config={CHILD_CONFIG} // always same reference (module const)
      onSelect={handleSelect} // stable via useCallback
    />
  ));
}
const Child = React.memo(function ({ item, config, onSelect }) {
  // Now correctly skips re-render when only other items change
  return <div>{item.name}</div>;
});
```

---

### 📊 Comparison Table

| API                     | What it guards              | Mechanism                     | React version |
| ----------------------- | --------------------------- | ----------------------------- | ------------- |
| `React.memo`            | Functional component render | Shallow prop equality check   | v16.6+        |
| `PureComponent`         | Class component render      | Shallow prop + state equality | v15.3+        |
| `shouldComponentUpdate` | Class component render      | Custom boolean logic          | v0.13+        |
| `useMemo`               | Value computation           | Shallow dep equality check    | v16.8+        |
| `useCallback`           | Function reference          | Shallow dep equality check    | v16.8+        |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "React.memo makes components significantly faster"         | For components with fast renders (<1ms), React.memo adds overhead (prop comparison cost) that may equal or exceed the saved render time. It is beneficial for expensive renders that happen unnecessarily often. Profile first.                          |
| "React.memo works correctly with inline object props"      | Inline objects (`<Memo item={{ id: 1 }} />`) create new references every render. React.memo sees a different prop reference and re-renders. For React.memo to work, object props must come from state, useMemo, or external stable sources.              |
| "React.memo is equivalent to useMemo"                      | They are different tools. React.memo is a Higher-Order Component that guards a component render. useMemo is a hook that guards a computed value inside a component. React.memo is used on the child; useMemo is used in the parent (to stabilise props). |
| "Wrapping everything in React.memo is a safe optimisation" | React.memo adds a prop comparison cost on every render. For components that almost always re-render (because their props change frequently), this is pure overhead. The optimisation should target components that re-render unnecessarily.              |

---

### 🚨 Failure Modes & Diagnosis

**Silent Bypass: New Function/Object Prop Each Render**

**Symptom:** React.memo is applied but the component still
re-renders on every parent render. Profiler shows the
component rendering at the same rate as before.

**Diagnosis:** In React DevTools Profiler: run a recording.
Click on a re-render. Check "Why did this render?" (flame
graph). It shows which specific prop changed. Common
culprit: inline functions or object literals in the parent's
JSX.

**Fix:** Add `useCallback` for function props. Add `useMemo`
or move to module-level constant for object/array props.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Virtual DOM and Reconciliation` - why React.memo saves work
  (skipping the reconciliation step entirely)
- `useMemo Hook` - provides stable value references for props
- `useCallback Hook` - provides stable function references for props

**Builds On:**

- `React Performance Profiling` - the tooling to verify
  React.memo is having the intended effect
- `React Fiber Architecture` - understanding when React
  calls the render function vs when it reuses the last result

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ API         │ const Memo = React.memo(Component)        │
│ SKIP RENDER │ When ALL props pass Object.is equality    │
│ RE-RENDER   │ When ANY prop fails Object.is equality    │
├─────────────────────────────────────────────────────────┤
│ REQUIRES    │ Stable object props → useMemo in parent   │
│             │ Stable function props → useCallback parent│
│             │ Otherwise: React.memo is bypassed silently│
├─────────────────────────────────────────────────────────┤
│ CUSTOM CMP  │ React.memo(C, (prev, next) => bool)       │
│             │ true = equal (skip render)                │
│             │ false = changed (re-render)               │
├─────────────────────────────────────────────────────────┤
│ PROFILE     │ ALWAYS profile before adding React.memo   │
│             │ Use "Why did this render?" in DevTools    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `React.memo` skips a component render if ALL props
   are shallowly equal. Objects and functions must have
   stable references (useMemo, useCallback in parent).
2. Use React DevTools "Why did this render?" to confirm
   React.memo is working and to identify the problematic prop.
3. Profile before adding. React.memo has overhead (prop
   comparison). Only useful for expensive components
   that re-render unnecessarily.

**Interview one-liner:**
"React.memo wraps a functional component and skips its
re-render when all props are shallowly equal (using
`Object.is`). It is effective for expensive components
in lists that re-render on parent state changes unrelated
to their own props. For React.memo to work correctly,
object props must be stabilised with `useMemo` and function
props with `useCallback` in the parent - otherwise new
references each render bypass the memo silently. Always
profile before applying: React.memo adds prop comparison
overhead that may exceed the savings for cheap renders."

---

### 💎 Transferable Wisdom

`React.memo` is a specific implementation of the "memoisation
at the boundary" pattern used throughout computing: cache
the output at system boundaries rather than internally.
HTTP proxy caches cache at the client-server boundary.
CDN edge caches cache at the geographic distribution
boundary. CPU instruction caches cache at the decode
boundary. In each case, the cache guards an expensive
operation (the actual work) by comparing a cheap key
(request URL, instruction address, prop reference) to
decide if the work can be skipped. The trade-off is
universal: the key comparison cost vs the work cost.
React.memo is only worthwhile when the comparison is
cheaper than the guarded render.

---

### 💡 The Surprising Truth

React's documentation explicitly warns: "Don't use memo
as a premature optimization." Yet `React.memo` is one of
the most over-applied APIs in React codebases. Many teams
wrap every component in `React.memo` "just in case." The
actual performance impact is often negative: for a component
that re-renders 3x per second with 5 props, React does
5 `Object.is` comparisons per render (15 comparisons/sec)
vs skipping the render function. If the render function
takes 0.1ms, the savings is 0.3ms/sec. The 15 comparisons
take negligible time but add code complexity, memory for
memoised results, and potential bugs when props change
in ways `Object.is` does not detect. The "default React.memo
everywhere" approach is often a net negative, not positive.

---

### ✅ Mastery Checklist

1. **PROFILE** a list component with React DevTools to
   confirm it re-renders on parent state changes unrelated
   to its props. Apply `React.memo` + `useCallback` on
   handlers. Confirm the re-renders stop.
2. **DIAGNOSE** a case where `React.memo` is applied but
   the component still re-renders, using DevTools "Why
   did this render?" to identify the unstable prop.
3. **IMPLEMENT** a custom comparison function for `React.memo`
   that does a specific deep equality check on one nested
   prop while using shallow equality for others.
4. **EXPLAIN** the difference between `React.memo` (skip
   render at component boundary), `useMemo` (skip computation
   inside render), and `useCallback` (stable function reference
   to enable React.memo).
5. **DECIDE** for three given component scenarios whether
   `React.memo` would provide measurable benefit, and
   justify with profiling criteria.

---

### 🧠 Think About This Before We Continue

**Q1.** The React Compiler (React Forget) is designed to
automatically add the equivalent of `React.memo` everywhere
it determines it would help. If this works correctly,
what happens to the manual `React.memo` + `useCallback`

- `useMemo` trio that teams currently maintain? Is there
  any scenario where manual memoisation should survive a
  React Compiler migration?

**Q2.** `React.memo` uses shallow equality for prop
comparison. A component receives a complex configuration
object: `{ theme: { colors: { primary: '#fff' } },
features: { sort: true, filter: true } }`. Shallow
equality compares the top-level reference only, not
the nested values. If the parent creates this object
with `useMemo` but it includes a date (`{ ...config,
generated: new Date() }`), the date changes every render
and invalidates the memo. How do you design the props
interface for deeply nested configurations to work
correctly with React.memo?

**Q3.** React Server Components render on the server and
are never re-rendered on the client. Does `React.memo`
apply to Server Components? What replaces the re-render
optimisation concern in an RSC architecture where the
"re-render" is a new server request?
