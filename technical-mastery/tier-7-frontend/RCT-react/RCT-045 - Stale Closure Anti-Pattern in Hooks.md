---
id: RCT-045
title: Stale Closure Anti-Pattern in Hooks
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-019, RCT-021, RCT-036
used_by: RCT-046, RCT-058
related: RCT-021, RCT-035, RCT-036
tags:
  - react
  - frontend
  - bugs
  - hooks
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/react/stale-closure-anti-pattern-in-hooks/
---

⚡ TL;DR - A stale closure occurs when a hook's callback
(useEffect, useCallback, event handler) captures a state
or prop value at creation time and keeps using that old
value even after state updates; the fix is either listing
the captured variable in the dependency array or using
a `useRef` to hold a mutable reference to the latest value.

| #045            | Category: React                                           | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | useState Hook, useEffect Hook, useCallback Hook           |                 |
| **Used by:**    | useEffect Overuse Anti-Pattern, Memory Leak Anti-Patterns |                 |
| **Related:**    | useEffect Hook, useMemo Hook, useCallback Hook            |                 |

---

### 🔥 The Problem This Solves

**INVISIBLE STATE BUG - READING OLD VALUES:**
React hooks rely on JavaScript closures. Each render
creates a new closure for every function inside the
component, capturing the current values of all variables.
When a callback is NOT recreated on every render (because
it is in a `useEffect` with a dependency array, or
memoised with `useCallback`), it holds references to
the values from the render when it was created.

If state changes after that render, the callback still
holds the OLD values. This is the stale closure - the
closure is "stale" because it references data from a
past render, not the current render.

This bug is invisible in the code: the callback reads
`count` and it looks correct. But it reads the `count`
from the render when the closure was created, not the
current `count`.

---

### 📘 Textbook Definition

**Stale Closure** - a JavaScript closure that captures
variables from an outer scope, but those variables have
since been reassigned (the closure holds a reference to
the OLD value, not the current one). In React hooks, a
stale closure occurs when a callback created in a
`useEffect`, `useCallback`, or event handler captures
a `state` or `props` value at creation time, and that
callback is not recreated when the captured values change.
The callback reads outdated values from the original
render instead of the current values.

---

### ⏱️ Understand It in 30 Seconds

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // BUG: count is ALWAYS 0 here
      // This closure was created on the FIRST render
      // count=0 was captured at that time
      // count has since changed (1, 2, 3...) but
      // this closure still reads 0
      console.log("Current count:", count);
      // always: "Current count: 0"
      setCount(count + 1); // always: setCount(0 + 1) = 1
      // Counter is stuck at 1 forever
    }, 1000);
    return () => clearInterval(interval);
  }, []); // empty deps: runs once, closure captures count=0
  //         ^^^ This is the bug: missing `count` dependency

  return <p>Count: {count}</p>;
}
```

---

### 🔩 First Principles Explanation

**WHY CLOSURES CAPTURE VALUES:**

```javascript
// JavaScript closure basics:
function outer() {
  let x = 1;
  function inner() {
    console.log(x); // inner closes over x
  }
  x = 2; // reassignment
  inner(); // logs 2 (closure holds REFERENCE to x, not value)
}

// BUT in React, state values are primitives (or new references):
function Component() {
  const [count, setCount] = useState(0);
  // count is a PRIMITIVE (number)
  // When setCount(1) is called, React creates a NEW render
  // In the new render: count is 1 (new variable, new closure)
  // In the old render's closure: count is still 0 (old variable)

  const fn = useCallback(() => {
    console.log(count); // captures THIS render's count
  }, []); // recreate NEVER (empty deps)
  // When count changes from 0 to 1:
  // - fn is NOT recreated (empty deps)
  // - fn still holds the count=0 from the first render
  // fn reads 0 even when current count is 5
}
```

**The dependency array: a declaration of what the callback reads:**

```
useCallback(fn, [a, b])
Means: "fn reads a and b. Recreate fn when a or b changes."

useEffect(fn, [a, b])
Means: "fn reads a and b. Re-run fn when a or b changes."

Empty array []:
Means: "fn reads nothing. Never recreate/re-run."
If fn actually reads state, it gets stale values.

No array:
Means: "Recreate/re-run on every render."
Never stale. Potentially expensive.
```

---

### 🧪 Thought Experiment

**THE INTERVAL COUNTER EXPERIMENT:**
Set up a counter that increments every second using
`setInterval`. The naive implementation uses `count`
in the dependency array:

```jsx
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(id);
}, [count]); // re-runs when count changes
```

This works but re-creates the interval on every count
change. Every second: clear old interval, create new one.
Potentially jerky timing.

The correct approach uses the functional update form:

```jsx
useEffect(() => {
  const id = setInterval(() => {
    setCount((c) => c + 1); // functional update: no stale closure
    // c is always the CURRENT state value (React provides it)
  }, 1000);
  return () => clearInterval(id);
}, []); // runs once: interval never re-created
// Smooth, accurate, no stale closure
```

The `setCount(c => c + 1)` pattern bypasses the stale
closure: instead of capturing `count` from the closure,
you tell React "give me the current value and add 1 to
it." React provides the current value each time the
updater runs.

---

### 🧠 Mental Model / Analogy

> Every render is a snapshot photograph. A closure is
> like a person in the photograph - they remember
> everything from when the photo was taken, not what
> happened after.
>
> When you tell a person in an old photograph "what is
> the current score?", they give you the score from
> when the photo was taken. The photo is "stale" - it
> does not update as the world changes.
>
> The fix: either give the person a live phone (a ref
> that always shows the current score), or retake the
> photograph every time the score changes (add the
> score to the dependency array).

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Hooks capture values at render time. If a callback is
not recreated when state changes, it holds old values.
Fix: add the state to the dependency array.

**Level 2 (patterns):**
Four ways to avoid stale closures:

1. Add the value to the dependency array (recreate callback)
2. Use functional setState updater `setCount(c => c + 1)`
3. Use `useRef` to store a mutable reference to the latest value
4. Use `useReducer` (dispatch is stable, no stale closure risk)

**Level 3 (ESLint):**
`eslint-plugin-react-hooks` has the `exhaustive-deps`
rule. It warns when a value used inside a hook's callback
is missing from the dependency array. Running this lint
rule catches most stale closure bugs at build time. Do
NOT suppress the warning without understanding why it
fires.

**Level 4 (useRef as escape hatch):**
Sometimes adding a value to the dependency array would
cause too many re-runs. Use `useRef` to hold a "live
pointer" to the latest value without causing re-runs:

```jsx
const latestHandler = useRef(onSomeEvent);
latestHandler.current = onSomeEvent; // update on every render
useEffect(() => {
  // latestHandler.current is always the latest function
  // No stale closure, and no re-run when onSomeEvent changes
  window.addEventListener("keydown", (e) => latestHandler.current(e));
}, []); // runs once
```

This is the "event handler ref" pattern. React 18 plans
to formalise this with `useEffectEvent`.

**Level 5 (mastery):**
`useEffectEvent` (RFC in React 18+) is designed explicitly
for this case: a callback that reads reactive values but
should not be in the effect's dependency array. It wraps
the function in a ref internally and exposes a stable
reference. This is the official React solution to the
"I want to read the latest value without re-running the
effect" use case. Until it stabilises, the manual
`useRef` pattern is the correct escape hatch.

---

### ⚙️ How It Works (Mechanism)

**The useRef "latest value" pattern:**

```jsx
function SearchResults({ query, onResultSelect }) {
  const [results, setResults] = useState([]);

  // Store latest onResultSelect without adding to deps
  const onResultSelectRef = useRef(onResultSelect);
  onResultSelectRef.current = onResultSelect;
  // Updated on EVERY render - always points to latest fn

  useEffect(() => {
    const subscription = searchAPI.subscribe(query, (newResults) => {
      setResults(newResults);
    });

    // Using ref: always calls the LATEST onResultSelect
    // Even if parent re-renders with a new function reference
    const handleSelect = (item) => onResultSelectRef.current(item);
    document.addEventListener("keydown", handleSelect);

    return () => {
      subscription.unsubscribe();
      document.removeEventListener("keydown", handleSelect);
    };
  }, [query]); // only re-runs when query changes
  // onResultSelectRef is NOT in deps (it is a ref, always stable)
  // latestHandler.current holds the latest function on every render

  return (
    <ul>
      {results.map((r) => (
        <li key={r.id}>{r.name}</li>
      ))}
    </ul>
  );
}
```

---

### 💻 Code Example

**BAD: Stale state in useCallback:**

```jsx
// BAD: onSave reads stale formData
function Form() {
  const [formData, setFormData] = useState({ name: "", email: "" });

  // useCallback with empty deps: callback created once
  // captures formData={name:'', email:''} from first render
  const onSave = useCallback(() => {
    // formData is ALWAYS {name:'', email:''} here
    // User types in the form, setFormData updates state,
    // but onSave still reads the initial empty formData
    saveForm(formData); // BUG: always saves empty form
  }, []); // empty deps: never recreated

  return (
    <input
      value={formData.name}
      onChange={(e) =>
        setFormData((prev) => ({ ...prev, name: e.target.value }))
      }
    />
  );
}
```

**GOOD: Add to dependency array:**

```jsx
// GOOD: onSave is recreated when formData changes
function Form() {
  const [formData, setFormData] = useState({ name: "", email: "" });

  const onSave = useCallback(() => {
    saveForm(formData); // reads current formData
  }, [formData]); // recreated when formData changes
  // Button with React.memo receiving onSave will re-render
  // when formData changes (because onSave reference changes)
  // This is correct - the memoised button should know about
  // the new save handler

  return (
    <input
      value={formData.name}
      onChange={(e) =>
        setFormData((prev) => ({ ...prev, name: e.target.value }))
      }
    />
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "useCallback([]) means the function is always the same"             | `useCallback(() => fn, [])` means "create once, never recreate." This is only correct if the function truly reads NO reactive values. If it reads state or props (which change), the captured values become stale. The dependency array documents what the function reads, not a performance setting.                            |
| "Adding things to dependency arrays hurts performance"              | Incorrect reasoning. Dependencies tell React when to recreate/re-run the callback. Not adding a dependency that the callback reads is a BUG (stale value). The correct question is: "does this callback truly read this value?" If yes, it must be in the deps. Performance optimisation is secondary to correctness.            |
| "The ESLint rule is overly strict - I know better"                  | The `exhaustive-deps` rule exists because stale closures are non-obvious bugs that appear only in specific timing conditions. Suppressing the warning without understanding the consequence is almost always wrong. If the rule seems wrong for your case, use the `useRef` pattern or `useEffectEvent` rather than suppressing. |
| "Functional setState (setCount(c => c+1)) fixes all stale closures" | Functional setState fixes stale closures in setState calls (reading state in the updater). It does NOT fix stale closures for reading state in OTHER operations inside the callback. If the callback reads `count` for logging or an API call (not for setting state), functional setState does not help.                        |

---

### 🚨 Failure Modes & Diagnosis

**Symptom: State value is always 0 (or initial value) in an interval/timeout**

**Root Cause:** `useEffect` with empty `[]` dependencies
captures initial state value. State updates are reflected
in new renders but not in the original effect closure.

**Diagnosis:**

```jsx
useEffect(() => {
  const id = setInterval(() => {
    console.log(count); // always initial value
  }, 1000);
  return () => clearInterval(id);
}, []); // missing count dependency
```

**Fix options:**

1. Add `count` to deps (re-creates interval on each count change):
   `}, [count]);`
2. Use functional update (interval created once):
   `setCount(c => c + 1);`
3. Use `useRef`:
   ```jsx
   const countRef = useRef(count);
   countRef.current = count;
   // Use countRef.current inside interval
   ```

---

**Symptom: Event handler uses outdated state (e.g. form not submitted correctly)**

**Root Cause:** Event handler captured state at setup time,
state changed, but handler was not recreated.

**Diagnosis:** ESLint `exhaustive-deps` warning on the
`useCallback` or `useEffect`. Enable the rule.

**Fix:** Add the state to the `useCallback` deps:
`useCallback(fn, [formData])`

---

### 🔗 Related Keywords

**Prerequisites:**

- `useState Hook` - the state values that become stale
- `useEffect Hook` - the primary location for stale closures
- `useCallback Hook` - memoised callbacks with stale closure risk

**Builds On:**

- `useEffect Overuse Anti-Pattern` - related misuse patterns
- `Memory Leak Anti-Patterns in React` - related to
  subscriptions and event listeners in effects

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ THE BUG   │ Callback reads state from old render snapsho│
│ CAUSE     │ Missing dependency in useEffect/useCallback │
│ DETECT    │ ESLint exhaustive-deps rule (enable it!)    │
├─────────────────────────────────────────────────────────┤
│ FIX 1     │ Add value to dependency array               │
│ FIX 2     │ Functional setState: setCount(c => c + 1)   │
│ FIX 3     │ useRef: countRef.current = count each render│
│ FIX 4     │ useReducer: dispatch is always stable       │
├─────────────────────────────────────────────────────────┤
│ COMING    │ useEffectEvent (React experimental)         │
│           │ Official solution for reading latest values │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Every render is a snapshot. Closures capture values
   from their render's snapshot. If a hook callback is
   not recreated when state changes, it reads stale values.
2. The ESLint `exhaustive-deps` rule catches missing
   dependencies. Never suppress it without understanding
   the consequence.
3. Four fixes: add to deps, use functional setState
   `setCount(c=>c+1)`, use `useRef` for latest value,
   or restructure to use `useReducer`.

**Interview one-liner:**
"A stale closure in React hooks occurs when a callback
(in useEffect, useCallback, or event handlers) captures
a state or prop value from its render, and the callback
is not recreated when that value changes. The callback
reads outdated values from the original render. Root
cause: missing dependency in the dependency array.
Detection: enable ESLint exhaustive-deps rule. Fixes:
add to deps, use functional setState `setCount(c => c+1)`,
use `useRef` to hold the latest value, or use `useReducer`
which provides a stable dispatch function."

---

### 💎 Transferable Wisdom

Stale closures in React are a specific instance of the
general "cache invalidation" problem. The closure is a
cache of values from a point in time. When the source
values change, the cache (closure) does not automatically
update. This pattern appears everywhere: HTTP cache
headers (stale-while-revalidate), database read replicas
(reading stale data), distributed caches (cache miss vs
cache hit on updated data), event sourcing (projections
must replay events to get current state). The solution
is always the same pattern: either invalidate the cache
when the source changes (update the dependency array),
use a live reference instead of a snapshot (useRef), or
design the system so the stale value is acceptable
(idempotent operations that do not care about the exact
value).

---

### 💡 The Surprising Truth

The React documentation for years described the ESLint
`exhaustive-deps` rule as "optional" and gave examples
that arguably encouraged empty dependency arrays. In
2023, the React team updated the docs significantly and
now recommends enabling `exhaustive-deps` as a core
practice, not optional. The updated React docs explicitly
say: "If your effect uses reactive values from the
component, include them in the dependencies. Think of
the lint rule as a debugger pointing out all of the
reactive values an effect uses." This represents a
significant shift: the React team now treats the
`exhaustive-deps` rule as effectively mandatory for
correct hook usage, not just a nice-to-have.

---

### ✅ Mastery Checklist

1. **DEMONSTRATE** a stale closure bug: an interval
   counter that never gets above 1 because of empty deps.
   Explain the mechanism. Fix with functional setState.
2. **DEMONSTRATE** a stale closure in `useCallback`: a
   save handler that always saves the initial form data.
   Fix with either deps array or `useRef`.
3. **USE** the ESLint `exhaustive-deps` rule to detect
   a stale closure bug in a codebase. Show the warning
   and the fix.
4. **EXPLAIN** when `useRef` is the right fix vs adding
   to the dependency array. Give a real example where
   adding to deps is incorrect (would cause too many
   re-runs) and `useRef` is the right choice.
5. **COMPARE** `useCallback` with and without the correct
   deps in a React DevTools Profiler. Show that incorrect
   (empty) deps causes the callback to read stale values,
   while correct deps causes the callback to be recreated
   (as intended).

---

### 🧠 Think About This Before We Continue

**Q1.** A WebSocket connection is established in a
`useEffect` with an empty dependency array. The WebSocket's
`onmessage` handler needs to call `setState` with the
latest user preferences (which change frequently). How
do you ensure the `onmessage` handler always uses the
latest preferences without recreating the WebSocket
connection on every preferences change?

**Q2.** React's `useEffectEvent` (experimental) is
designed to be called inside `useEffect` but excluded
from the dependency array - it always sees the latest
values without causing re-runs. How does this differ
from just using a `useRef`? What guarantees does
`useEffectEvent` provide that the manual `useRef` pattern
does not?

**Q3.** TypeScript can help detect some stale closure
bugs at compile time. If a `useCallback` callback is
typed as `() => void` but internally reads a `count:
number` state that is declared as `const count = 0` in
a mutable-looking context, TypeScript might not flag the
stale read. What TypeScript patterns or tools can help
detect stale closure bugs at the type level, beyond what
the runtime ESLint rule catches?
