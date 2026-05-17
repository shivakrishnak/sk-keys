---
id: RCT-036
title: useCallback Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-020, RCT-034, RCT-035, RCT-039
used_by: RCT-037, RCT-049, RCT-052
related: RCT-035, RCT-037, RCT-039
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
nav_order: 36
permalink: /react/usecallback-hook/
---

# RCT-036 - USECALLBACK HOOK

⚡ TL;DR - `useCallback(fn, [deps])` returns a memoised
function reference - the SAME function object between
renders when deps have not changed - preventing `React.memo`
children from re-rendering due to new function prop
references; without `React.memo` on the child, `useCallback`
does nothing useful.

| #036            | Category: React                                                    | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | useState Hook, useReducer Hook, useMemo Hook, React Reconciliation |                 |
| **Used by:**    | React.memo, React Performance Profiling, React Fiber Architecture  |                 |
| **Related:**    | useMemo Hook, React.memo, React Performance Profiling              |                 |

---

### 🔥 The Problem This Solves

**FUNCTION PROPS BYPASS REACT.MEMO:**
`React.memo` skips a component's re-render if its props
are shallowly equal (same references). A common pattern
is passing an `onClick` handler from parent to child:

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // This creates a NEW function on every Parent render:
  const handleClick = () => setCount((c) => c + 1);

  return <ExpensiveChild onClick={handleClick} />;
}
const ExpensiveChild = React.memo(function ({ onClick }) {
  // ...expensive render...
});
```

On every Parent render, `handleClick` is a new function
reference. `React.memo` compares old `onClick` vs new
`onClick`: `fn !== fn` (different reference). So
`ExpensiveChild` re-renders anyway, defeating `React.memo`.

`useCallback` fixes this by returning the same function
reference when deps have not changed.

---

### 📘 Textbook Definition

**useCallback** - a React hook that memoises a function
reference. `useCallback(fn, [deps])` returns `fn` on the
first render. On subsequent renders, it returns the same
`fn` if all deps are equal (shallow comparison). If any
dep changes, it returns a new `fn`. Equivalent to:
`useMemo(() => fn, [deps])` - `useCallback` is literally
`useMemo` that caches a function instead of a value.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// WITHOUT useCallback: new function every render
// → React.memo on child is bypassed
function Parent({ userId }) {
  const [count, setCount] = useState(0);

  const handleDelete = (id) => deleteUser(id);
  // handleDelete is a new function on every render
  // Even though deleteUser never changes

  return <UserRow onDelete={handleDelete} />;
}

// WITH useCallback: same function reference when deps unchanged
function Parent({ userId }) {
  const [count, setCount] = useState(0);

  const handleDelete = useCallback(
    (id) => deleteUser(id),
    [], // no deps: always same function reference
  );
  // handleDelete is the same reference on every render
  // React.memo on UserRow can now skip re-renders

  return <UserRow onDelete={handleDelete} />;
}
```

---

### 🔩 First Principles Explanation

**THE FUNCTION REFERENCE PROBLEM:**

```
JavaScript:
  const a = () => {};
  const b = () => {};
  a === b  // false (two different function objects)

  const c = a;  // c points to the SAME object as a
  a === c  // true

React render:
  Every render call creates a new function literal.
  handleClick = () => ...  // new function object each render
  React.memo compares props: prevProps.onClick !== nextProps.onClick
  → Re-renders (bypassing React.memo)

useCallback:
  First render: create function, store it
  Next render:  if no deps changed → return STORED function
  Same JavaScript object reference → React.memo comparison passes
  → Re-render skipped
```

**USECALLBACK IS USEMEMO FOR FUNCTIONS:**

```jsx
// These are equivalent:
const fn1 = useCallback((x) => doSomething(x), [dep]);
const fn2 = useMemo(() => (x) => doSomething(x), [dep]);

// useCallback is a specialised useMemo for functions
// that reads more clearly in code
```

**THE CRITICAL PREREQUISITE:**
`useCallback` is ONLY useful when:

1. The function is passed as a prop to a child wrapped
   in `React.memo`, OR
2. The function is in a `useEffect` dependency array
   (to prevent infinite loops)

Without one of these two conditions, `useCallback` adds
complexity and memory overhead with zero benefit.

---

### 🧪 Thought Experiment

**THE MISSING REACT.MEMO:**
A component has this code:

```jsx
const handleClick = useCallback(() => onClick(id), [onClick, id]);
```

A developer added `useCallback` because they read "use
`useCallback` for all handler functions." But the child
component using `handleClick` is NOT wrapped in
`React.memo`. What happens?

The child re-renders on every parent render regardless -
because all components re-render by default when the parent
re-renders, whether the props changed or not.
`useCallback` helped nothing. It just made the code more
complex and uses slightly more memory to store the memoised
function.

The correct question before adding `useCallback`: "Is
the child wrapped in `React.memo`, and is it actually
re-rendering when it should not?"

---

### 🧠 Mental Model / Analogy

> Imagine a telephone number. Every time you call someone,
> you normally give them a new business card with your
> phone number on it (a new function object). Even though
> the number is the same, they see a NEW card and update
> their contact list.
>
> `useCallback` is like having a permanent engraved name
> card that you hand to the same person repeatedly. They
> check: "Is this the same physical card I had before?"
> YES → they know nothing changed, no need to update.
>
> `React.memo` is the person doing the check. Without
> them checking (without React.memo), it does not matter
> if you hand the same card or a new one - the update
> happens regardless.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`useCallback` gives you the same function between renders
when deps have not changed. Use it to prevent unnecessary
re-renders in `React.memo` children that receive function
props.

**Level 2 (usage):**
`const fn = useCallback(() => doSomething(dep), [dep])`.
If `dep` changes, a new function is created. Otherwise,
same reference. Must have `React.memo` on the child for
any benefit.

**Level 3 (patterns):**
The `useCallback + React.memo` pattern is one of the main
performance optimisation patterns in React. But only apply
it when profiling shows unnecessary re-renders as a
bottleneck. Common stable use case: `dispatch` from
`useReducer` is already stable (no `useCallback` needed).
Event handlers wrapping `dispatch` often can be `useCallback`-
free if the child is not `React.memo`'d.

**Level 4 (useEffect deps):**
`useCallback` is also needed when a function is in a
`useEffect` dep array. Without `useCallback`, the function
is a new reference every render, and `useEffect` re-runs
on every render:

```jsx
// Without useCallback: infinite loop or unintended re-runs
const fetchData = async () => {
  /* uses userId */
};
useEffect(() => {
  fetchData();
}, [fetchData]); // fetchData new every render

// With useCallback: stable reference, effect runs only when userId changes
const fetchData = useCallback(async () => {
  /* uses userId */
}, [userId]);
useEffect(() => {
  fetchData();
}, [fetchData]);
```

**Level 5 (mastery):**
`useCallback` does not prevent the function body from
accessing stale values. If you use `useCallback(() =>
setCount(count + 1), [])`, the closure captures the
initial `count = 0`. Every invocation always increments
from 0, not from the current count. The fix: use functional
setState (`setCount(prev => prev + 1)`) inside `useCallback`
to read current state without needing it in deps. This
is the most common subtle bug with `useCallback`.

---

### ⚙️ How It Works (Mechanism)

**Complete React.memo + useCallback pattern:**

```jsx
// ProductList: renders a large list
// Passes onDelete to each row
// Without useCallback: every Parent re-render creates a new
//   onDelete function → all ProductRow children re-render

function ProductList({ products, onProductUpdate }) {
  const [filter, setFilter] = useState("all");

  // handleDelete is stable: only re-created when
  // onProductUpdate changes (should be stable from parent)
  const handleDelete = useCallback(
    (id) => {
      onProductUpdate({ type: "DELETE", id });
    },
    [onProductUpdate],
  );

  // handleToggle is stable: no deps, always the same
  const handleToggle = useCallback(
    (id) => {
      onProductUpdate({ type: "TOGGLE", id });
    },
    [onProductUpdate],
  );

  const filtered = useMemo(
    () =>
      filter === "all" ? products : products.filter((p) => p.type === filter),
    [products, filter],
  );

  return (
    <>
      <FilterBar activeFilter={filter} onFilterChange={setFilter} />
      {filtered.map((product) => (
        <ProductRow
          key={product.id}
          product={product}
          onDelete={handleDelete} // stable reference
          onToggle={handleToggle} // stable reference
        />
      ))}
    </>
  );
}

// React.memo: only re-renders when product, onDelete, or onToggle change
const ProductRow = React.memo(function ProductRow({
  product,
  onDelete,
  onToggle,
}) {
  return (
    <div>
      {product.name}
      <button onClick={() => onToggle(product.id)}>Toggle</button>
      <button onClick={() => onDelete(product.id)}>Delete</button>
    </div>
  );
});
```

---

### 💻 Code Example

**BAD: useCallback without React.memo (no benefit):**

```jsx
// BAD: useCallback with no React.memo child
// The handler is memoised but the child re-renders anyway
// because all components re-render by default

function SearchInput({ onSearch }) {
  const [query, setQuery] = useState("");

  // useCallback here adds complexity for ZERO benefit
  // SearchButton is not wrapped in React.memo
  // It will re-render on every SearchInput render regardless
  const handleSubmit = useCallback(() => {
    onSearch(query);
  }, [onSearch, query]);

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <SearchButton onClick={handleSubmit} /> {/* Not React.memo'd */}
    </div>
  );
}
```

**GOOD: useCallback paired with React.memo:**

```jsx
// GOOD: useCallback where it has measurable effect
// Profiler showed SearchButton was re-rendering on every keystroke
// SearchButton is expensive (complex ripple animation on render)

function SearchInput({ onSearch }) {
  const [query, setQuery] = useState("");

  // Stable: only re-created when onSearch changes
  const handleSubmit = useCallback(() => {
    onSearch(query);
  }, [onSearch, query]); // query must be in deps (used in closure)

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <ExpensiveSearchButton onClick={handleSubmit} />
    </div>
  );
}

// React.memo: skip re-render if onClick unchanged
const ExpensiveSearchButton = React.memo(function ({ onClick }) {
  // Heavy rendering work
  return <button onClick={onClick}>Search</button>;
});
// Now: typing in input → query changes → handleSubmit recreated
// → ExpensiveSearchButton re-renders (because onClick changed)
// For even better perf: use a ref for query and keep handleSubmit stable
```

---

### 📊 Comparison Table

|               | useCallback                            | useMemo                                                   | React.memo                       |
| ------------- | -------------------------------------- | --------------------------------------------------------- | -------------------------------- |
| Memoises      | Function reference                     | Computed value                                            | Component render                 |
| Use case      | Stable handler for React.memo children | Expensive computation, stable object                      | Skip render when props unchanged |
| Needs partner | React.memo on child                    | React.memo child (for ref stability) or expensive compute | useCallback + useMemo on parent  |
| Overhead      | Memory + deps comparison               | Memory + deps comparison                                  | Props comparison per render      |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "All event handler functions should be wrapped in useCallback" | useCallback is only beneficial when passed to a React.memo-wrapped child or used in useEffect deps. Adding it universally wastes memory and adds code complexity with no performance gain in most cases.                                                 |
| "useCallback prevents the function from being re-created"      | The function body is not literally "not created." JavaScript still evaluates the arrow function expression. useCallback stores and returns the previous instance. The new function object is created but immediately discarded if deps have not changed. |
| "useCallback with [] deps means the function never changes"    | Correct for the reference, but dangerous: the closure captures variables at the time of first render. If the function reads state or props not in deps, it reads stale values. Use functional setState or include all used values in deps.               |
| "dispatch from useReducer needs useCallback"                   | No. `dispatch` from `useReducer` is guaranteed to be stable (same reference on every render) by React. There is no need to wrap it in `useCallback`. Wrapping dispatch in useCallback is a common no-op.                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Stale Closure (deps omitted to keep callback stable):**

**Symptom:** Function handler uses a variable (e.g.,
`userId`), but after `userId` changes, the function
still uses the old value.

**Root Cause:**

```jsx
// BAD: userId in closure but not in deps
const handleFetch = useCallback(() => {
  fetchUser(userId); // captures initial userId (stale)
}, []); // [] = never update = always stale userId
```

**Fix option 1:** Add `userId` to deps (function recreates
on change, breaks React.memo):

```jsx
const handleFetch = useCallback(() => fetchUser(userId), [userId]);
```

**Fix option 2:** Use a ref to access the current value
without making it a dep:

```jsx
const userIdRef = useRef(userId);
useEffect(() => {
  userIdRef.current = userId;
}, [userId]);
const handleFetch = useCallback(() => fetchUser(userIdRef.current), []);
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `useMemo Hook` - useCallback is implemented as useMemo
- `React Reconciliation Algorithm` - why reference equality
  matters in React.memo's shallow comparison
- `useReducer Hook` - dispatch is already stable (no useCallback needed)

**Builds On:**

- `React.memo` - the consumer of stable function references
- `React Performance Profiling` - the tool to confirm
  useCallback is having the intended effect

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ API         │ const fn = useCallback(() => ..., [deps]) │
│ EQUIVALENT  │ useMemo(() => () => ..., [deps])          │
├──────────────────────────────────────────────────────────┤
│ USE WHEN    │ 1. Passing to React.memo-wrapped child    │
│             │ 2. Function is in useEffect deps array    │
│ DO NOT USE  │ When child is not React.memo-wrapped      │
│             │ When return value (not ref) matters       │
├──────────────────────────────────────────────────────────┤
│ GOTCHA      │ dispatch (useReducer) is already stable   │
│             │ Empty [] deps + stale closure = silent bug│
│             │ Use functional setState to avoid stale ref│
├──────────────────────────────────────────────────────────┤
│ PARTNER     │ Always pair with React.memo on child     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `useCallback` memoises a function REFERENCE. Only useful
   when the child is wrapped in `React.memo` or the function
   is in `useEffect` deps.
2. `dispatch` from `useReducer` is already stable. Never
   needs `useCallback`.
3. Empty `[]` deps with a closure that reads state = stale
   closure bug. Use functional setState inside callback.

**Interview one-liner:**
"useCallback memoises a function reference - returning
the same function object between renders when deps are
unchanged. It is useful only when passing handlers to
React.memo-wrapped children (to prevent bypassing the
memo) or when a function is in a useEffect dependency
array (to prevent infinite loops). Without React.memo
on the child, useCallback does nothing observable. The
most common bug: empty deps array with a stale closure
that reads state - use functional setState (`prev => prev + 1`)
inside the callback to avoid this."

---

### 💎 Transferable Wisdom

The stable function reference problem (useCallback) is
a specific instance of "identity vs value" semantics.
In many systems: HTTP caching by URL (identity) vs
response body (value); Git commit hash (identity) vs
file contents (value); React key prop (identity of list
item) vs item data (value). When equality checks use
reference identity (`===`) rather than deep value equality,
stabilising references becomes a performance concern. This
is why object identity is a design decision in many
systems: Java's `final` fields, Rust's ownership model,
Python's `id()`. React's hook system uses reference
equality throughout - understanding this explains all
three of `useMemo`, `useCallback`, and `React.memo`.

---

### 💡 The Surprising Truth

`useCallback(fn, deps)` is literally implemented in React's
source code as `useMemo(() => fn, deps)`. There is no
separate "useCallback implementation." The React team
added `useCallback` as a readable alias because
`useMemo(() => handler, deps)` is awkward to write and
read. This also means every property of `useMemo` applies
to `useCallback`: the cache can be evicted, the comparison
uses `Object.is`, it does not prevent the function from
being syntactically evaluated, and the React Compiler
can replace both automatically. They are the same hook
with a different call signature.

---

### ✅ Mastery Checklist

1. **DEMONSTRATE** the problem `useCallback` solves:
   create a `React.memo` child with a profiler, show
   it re-renders due to a new function prop, add
   `useCallback`, and confirm the re-renders stop.
2. **IDENTIFY** a case where `useCallback` is used but
   has no effect (child not wrapped in `React.memo`),
   and explain why.
3. **FIX** a stale closure bug in a `useCallback` with
   empty deps that reads a state variable - using both
   the "add to deps" approach and the "useRef to read
   current value" approach.
4. **EXPLAIN** why `dispatch` from `useReducer` never
   needs `useCallback`, and contrast this with `setState`
   from `useState`.
5. **APPLY** the `useCallback + React.memo` pattern to
   a list component with 1,000 rows where each row has
   a delete button, and measure the re-render count
   before and after.

---

### 🧠 Think About This Before We Continue

**Q1.** Consider this code:

```jsx
const handleDelete = useCallback(
  (id) => {
    setItems(items.filter((i) => i.id !== id));
  },
  [items],
);
```

`items` is in the deps array because it is used in the
closure. But `items` changes every time an item is deleted
(a new array). This means `handleDelete` is recreated
on every delete, bypassing `React.memo`. How do you fix
this without putting `items` in the deps array? (Hint:
functional setState.)

**Q2.** The React compiler promises to automatically
insert `useCallback` where needed. If it ships and works
correctly, a codebase could remove all manual `useCallback`
calls and let the compiler manage them. What are the risks
of this migration? Under what circumstances might the
compiler's analysis produce different results from
manually-written `useCallback`?

**Q3.** `useCallback` and `useMemo` both use reference
equality for dep comparison. They are designed for
optimisation. But they create implicit temporal coupling:
the component's output depends not just on current props/state
but on what was cached. This makes the component's behaviour
dependent on render history, not just current input. Is
this ever a correctness risk, and how do you test components
that use heavy memoisation correctly?
