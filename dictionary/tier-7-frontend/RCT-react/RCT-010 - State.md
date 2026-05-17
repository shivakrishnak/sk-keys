---
id: RCT-010
title: State
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-009
used_by: RCT-020, RCT-021, RCT-025, RCT-026, RCT-029, RCT-034
related: RCT-009, RCT-020, RCT-029
tags:
  - react
  - frontend
  - core
  - state-management
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /react/state/
---

# RCT-010 - STATE

⚡ TL;DR - State is data owned by a component that changes
over time and drives re-renders; the fundamental rules -
never mutate directly, batching, one source of truth - are
what prevent the most common React bugs.

| #010 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Component, Props | |
| **Used by:** | useState Hook, useEffect Hook, Controlled vs Uncontrolled, Form Handling, Lifting State Up, useReducer Hook | |
| **Related:** | Props, useState Hook, Lifting State Up | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In vanilla JavaScript, data that changes over time is stored
in variables. But variables do not trigger UI updates. If you
do `count++` in a click handler, the counter in the DOM does
not change unless you also find the DOM element and manually
update its text. You now have two sources of truth: the JS
variable and the DOM. They can drift apart. In fact, they
always drift apart.

**THE CORE PROBLEM:**
The fundamental problem of interactive UI is: when data
changes, the screen must change to reflect it. Vanilla JS
forces the developer to manage this synchronisation manually
for every piece of data. State in React solves this: when
React state changes, React automatically re-renders the
component to reflect the new data. The synchronisation is
automatic.

**THE INVENTION MOMENT:**
React's `useState` hook (introduced in React 16.8) made
state management available in function components without
class boilerplate. It returns a value and a setter. Calling
the setter: (1) schedules a re-render, (2) guarantees the
component will re-run with the new value on the next render.
The developer never manually updates the DOM.

---

### 📘 Textbook Definition

**State** in React is a data structure owned by a specific
component that represents values that can change over time
and that, when changed, should cause the component to
re-render. State is managed via the `useState` (or
`useReducer`) hook, which returns the current value and a
setter function. Calling the setter schedules a re-render -
React will call the component function again with the new
state value. State is **local** to the component that
declares it: it is not visible to parents or siblings unless
explicitly passed down as props or shared via Context.
State updates in React are **asynchronous** (batched since
React 18) and **must not mutate the existing state value**
- a new value or reference must always be provided.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
State is data owned by a component that, when changed via
its setter, triggers a re-render to reflect the new data.

**One analogy:**
> State is like the position of a dial on a piece of
> equipment. The dial has a current position (the state
> value). You can turn it (call the setter). When you turn
> the dial, the display on the equipment updates
> automatically. You do not need to manually update the
> display - that is handled for you. React's state is the
> dial; the re-render is the automatic display update.

**One insight:**
The key constraint is: never modify state directly. `count++`
or `array.push(item)` do not trigger re-renders. You must
call the setter: `setCount(count + 1)` or `setItems([
...items, newItem])`. React needs to know that state changed
in order to schedule the re-render. Direct mutation bypasses
this notification.

---

### 🔩 First Principles Explanation

**WHAT STATE IS:**
State is the data that makes a UI interactive. When any
of the following changes, the UI must update:
- Whether a modal is open
- What text a user has typed
- The currently selected tab
- The list of loaded items
- Whether a form is submitting

Each of these is a candidate for state. The question
"what data, when it changes, should cause this UI to
update?" defines what should be state.

**WHAT STATE IS NOT:**
- Data that can be computed from other state or props
  (derived value; compute, not store)
- Data that is not used in the render output (use a ref
  or a variable outside the component)
- Data that is shared between unrelated components
  (lift it up or use Context/state management)

**THE THREE STATE RULES:**

1. **Never mutate state directly:**
   `count++` → WRONG. `setCount(count + 1)` → CORRECT.
   `items.push(x)` → WRONG. `setItems([...items, x])` → CORRECT.

2. **State updates are asynchronous:**
   After calling `setCount(5)`, the next line still reads
   the old `count`. Use the functional updater form when
   computing next state from current: `setCount(c => c + 1)`.

3. **State is a snapshot per render:**
   Each render has its own version of state. Event handlers
   created during render close over that render's state snapshot.
   Stale closure bugs happen when an event handler is created
   during render N but fires during render N+2.

---

### 🧪 Thought Experiment

**SETUP:**
A counter with two buttons: "Increment" and "Increment 3 times"
(which calls `setCount(count + 1)` three times in a row).

**WHAT HAPPENS (common misconception):**

```jsx
// BAD: triple increment in one click - does it add 3?
function Counter() {
  const [count, setCount] = useState(0);

  const incrementThree = () => {
    setCount(count + 1); // count is 0 -> schedules 1
    setCount(count + 1); // count is STILL 0 -> schedules 1
    setCount(count + 1); // count is STILL 0 -> schedules 1
  };
  // Result after click: count becomes 1, not 3.
  // All three calls read the SAME snapshot value.
}
```

**WHAT ACTUALLY FIXES IT:**

```jsx
// GOOD: functional updater - reads latest queued value
const incrementThree = () => {
  setCount(c => c + 1); // queues: prev -> prev + 1
  setCount(c => c + 1); // queues on top: prev -> prev + 1
  setCount(c => c + 1); // queues on top: prev -> prev + 1
};
// React processes the queue: 0 -> 1 -> 2 -> 3 ✓
```

The functional updater form `setCount(c => c + 1)` tells
React "compute the next value from the latest queued value"
instead of "set it to this specific snapshot value."

---

### 🧠 Mental Model / Analogy

> State is a snapshot + a queue. Each render takes a
> snapshot of state. Calling `setState` adds to a queue
> of updates. Before the next render, React processes the
> queue to compute the next snapshot. Your component never
> sees intermediate values - only the result of the full
> queue.

```
Initial: count = 0

Click "increment 3":
  Queue: [c=>c+1, c=>c+1, c=>c+1]
  
React processes queue:
  0 -> 1 -> 2 -> 3

Next render: count = 3
```

Compare to non-functional form:
```
  Queue: [1, 1, 1]    <- all based on snapshot value 0
  
React: last write wins
  count = 1
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
State is data inside a component that can change. When it
changes, React automatically updates the screen. You use
`useState` to create state, and call the returned function
to change it.

**Level 2 - How to use it (junior developer):**
`const [count, setCount] = useState(0)` gives you `count`
(current value) and `setCount` (the function that changes it
and triggers re-render). When the user clicks a button, call
`setCount(count + 1)`. React will re-render the component
with the new `count` value.

**Level 3 - How it works (mid-level engineer):**
`useState` stores its value in a "slot" in React's internal
Fiber tree node for this component instance. Each render,
React looks up the current slot value and returns it. Calling
the setter queues an update. React batches updates (since
v18, all updates are batched, including those in async
callbacks) and re-renders. The functional updater form
`setState(prev => ...)` receives the latest queued value,
not the snapshot.

**Level 4 - Why it was designed this way (senior/staff):**
State immutability (always create a new object) was chosen
because it enables React to detect changes with a simple
reference equality check (`===`). If `prevState === newState`,
no re-render is needed. If objects were mutated in place,
React would need a deep equality check (expensive) or could
miss changes (if the reference is the same). Immutability
also enables time-travel debugging (Redux DevTools) and
optimistic updates.

**Level 5 - Mastery (distinguished engineer):**
State as a snapshot means every re-render is a complete
re-execution of the component function with a new closure.
This is the fundamental model that enables Concurrent React:
if React starts rendering with state snapshot A and a higher-
priority update arrives, it can discard the in-progress
render and start fresh with state snapshot B. The component
never sees a partial state - it always sees a consistent
snapshot. This is why state updates must never mutate the
previous snapshot: the previous snapshot may still be needed
by a concurrent render attempt.

---

### ⚙️ How It Works (Mechanism)

**useState internals (simplified):**

```
React's internal Fiber node for <Counter>:
  memoizedState: [
    { queue: [], value: 0 },   // slot 0: useState(0)
    ...                        // slot 1: next hook, etc.
  ]

Component renders:
  useState(0):
    - First render: initialise slot 0 with 0
    - Subsequent: read slot 0's current value

setCount(1) called:
  - Enqueue update { action: 1 } on slot 0's queue
  - Schedule re-render

Re-render:
  - Process slot 0's queue: new value = 1
  - Call Counter() function
  - useState(0): read slot 0 -> returns [1, setter]
  - Component renders with count = 1
```

**Batching (React 18):**

```jsx
// In React 18, all of these are batched into ONE render:
function handleEvent() {
  setCount(c => c + 1);    // batched
  setName("Alice");         // batched
  setLoading(false);        // batched
  // ONE re-render with all three updates applied
}

// Even async callbacks are now batched in React 18:
setTimeout(() => {
  setCount(c => c + 1);    // batched (React 18 only)
  setName("Alice");         // batched (React 18 only)
}, 0);
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STATE UPDATE CYCLE:**

```
┌────────────────────────────────────────────────────────┐
│ User Action (click, type, submit)                     │
│   |                                                   │
│   v                                                   │
│ Event handler: setCount(c => c + 1)                  │
│   |                                                   │
│   v                                                   │
│ React: enqueue update on component's state slot      │
│   |                                                   │
│   v                                                   │
│ React: batch and schedule re-render                  │
│   |                                                   │
│   v                                                   │
│ React: call Counter() function                       │
│   |                                                   │
│   v                                                   │
│ Component: useState(0) -> reads new value from slot  │
│   returns [newCount, setter]                         │
│   |                                                   │
│   v                                                   │
│ Component: returns new JSX with newCount             │
│   |                                                   │
│   v                                                   │
│ React: diff new vDOM against old vDOM                │
│   |                                                   │
│   v                                                   │
│ React: commit DOM mutation (text node update)        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - BAD: Mutating state directly:**

```jsx
// BAD: Direct mutation - React will NOT detect the change
function TodoList() {
  const [todos, setTodos] = useState([
    { id: 1, text: "Buy milk", done: false }
  ]);

  const toggleDone = (id) => {
    // WRONG: mutating the existing array/object
    const todo = todos.find(t => t.id === id);
    todo.done = true;     // mutates existing object
    setTodos(todos);      // same reference - no re-render
  };
  // Bug: React sees prevState === newState (same ref)
  // No re-render triggered. UI doesn't update.
}
```

**Example 2 - GOOD: Immutable state update:**

```jsx
// GOOD: create new references - React detects the change
function TodoList() {
  const [todos, setTodos] = useState([
    { id: 1, text: "Buy milk", done: false }
  ]);

  const toggleDone = (id) => {
    // Create new array with new object for changed item
    setTodos(prev =>
      prev.map(todo =>
        todo.id === id
          ? { ...todo, done: !todo.done } // new object
          : todo                          // same ref OK
      )
    );
  };
  // React sees prevState !== newState (new array ref)
  // Re-render triggered. UI updates correctly.
}
```

**Example 3 - PRODUCTION: State with TypeScript and
initialization:**

```tsx
interface FilterState {
  query: string;
  category: string | null;
  sortBy: 'name' | 'date' | 'price';
  page: number;
}

const DEFAULT_FILTERS: FilterState = {
  query: '',
  category: null,
  sortBy: 'date',
  page: 1,
};

function SearchPage() {
  const [filters, setFilters] = useState<FilterState>(
    DEFAULT_FILTERS
  );

  const updateFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      // Reset page on filter changes (not on page changes)
      ...(key !== 'page' ? { page: 1 } : {}),
    }));
  };

  return (
    <div>
      <SearchInput
        value={filters.query}
        onChange={q => updateFilter('query', q)}
      />
      {/* filters.category, filters.sortBy, etc. */}
    </div>
  );
}
```

---

### ⚖️ Comparison Table

| Type | useState | useReducer | External Store (Redux/Zustand) |
|---|---|---|---|
| **Best for** | Simple, independent values | Complex interdependent state | Shared global state |
| **Updates** | Direct setter | Dispatch action | Dispatch / set |
| **Complexity** | Low | Medium | High (setup) |
| **Testability** | Easy (render + interact) | Easy (reducer is pure fn) | Medium (requires store setup) |
| **Derived state** | Compute inline | Compute in reducer | Selectors |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "setState is synchronous - I can read the new value after calling it" | State updates are asynchronous. After `setCount(5)`, reading `count` on the next line still returns the old value. The new value is available on the NEXT render. Use the functional updater if you need to base the new state on the current value. |
| "I can store anything in state - including DOM references" | DOM references belong in `useRef`, not state. `useRef` provides a mutable box without triggering re-renders. If you put a DOM ref in state, updating it causes unnecessary re-renders. |
| "Multiple setState calls cause multiple re-renders" | Since React 18, all state updates are batched - even in async callbacks. Multiple setState calls in one event handler result in ONE re-render. |
| "State is shared across component instances" | State is per-instance. Two `<Counter />` components each have their own independent count state. Rendering `<Counter />` twice gives two counters that do not share state. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Closure in Event Handlers**

**Symptom:**
An asynchronous operation (setTimeout, fetch callback)
reads a state value that is behind the current state.
The operation uses the state from when it was scheduled,
not when it completes.

**Root Cause:**
The async callback closes over a stale snapshot of state.
React creates a new snapshot on each render; closures
created during render N still reference N's values even
when render N+2 has occurred.

```jsx
// BAD: count is stale in the timer callback
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      console.log(count); // always logs initial value!
    }, 3000);
    return () => clearTimeout(timer);
  }, []); // [] means this runs once, closes over count=0
}
```

**Fix options:**
1. Use a ref to always have the latest value:
   `const countRef = useRef(count); countRef.current = count;`
2. Add `count` to the useEffect dependency array (re-registers
   the timer on each count change - may not be desired)
3. Use the functional updater form to not depend on the
   closure value: `setCount(c => c + 1)`

---

**Re-render Loop from State Update in useEffect**

**Symptom:**
The component re-renders infinitely. Browser tab becomes
unresponsive.

**Root Cause:**
A `useEffect` updates state without a dependency array
(or with incorrect dependencies), triggering a re-render,
which triggers the effect again, in an infinite loop.

```jsx
// BAD: infinite loop
useEffect(() => {
  setData(fetchedData); // triggers re-render
  // Re-render runs this effect again (no deps array)
  // -> fetches again -> sets state -> re-render -> ...
});
```

**Diagnostic Command:**
```bash
# In React DevTools Profiler, record a few seconds.
# Infinite re-renders appear as a continuous flame chart.
# The component at the top of the chart with non-zero
# self-time on every frame is the culprit.
```

**Fix:**
Add correct dependency array to `useEffect`. If the effect
should run once, use `[]`. If it depends on specific values,
list them.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Component` - state lives inside components
- `Props` - the distinction between what a component
  receives (props) and what it owns (state)

**Builds On This (learn these next):**
- `useState Hook` - the primary API for state management
- `useEffect Hook` - how side effects respond to state changes
- `Lifting State Up` - when sibling components need shared state
- `useReducer Hook` - complex state transitions

**Alternatives / Comparisons:**
- `MobX` - observable state model; mutations are tracked
  automatically (no immutability requirement); very different
  mental model from React's snapshot model
- `Signals (Preact/SolidJS)` - fine-grained reactive values;
  only the components that read a signal re-render, not the
  whole subtree

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Data owned by a component that changes  │
│              │ over time, triggering re-renders        │
├──────────────┼───────────────────────────────────────────┤
│ API          │ const [value, setValue] = useState(init)│
├──────────────┼───────────────────────────────────────────┤
│ RULE 1       │ Never mutate directly. Always provide   │
│              │ a new value/reference to the setter.    │
├──────────────┼───────────────────────────────────────────┤
│ RULE 2       │ Updates are async. Read new value in    │
│              │ next render, not on next line.          │
├──────────────┼───────────────────────────────────────────┤
│ RULE 3       │ Use functional form when deriving next  │
│              │ state from current: setState(v => v+1)  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Direct mutation; storing DOM refs in    │
│              │ state; infinite re-render loops         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Automatic UI sync vs learning immutable │
│              │ update patterns                         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "State = data that, when changed via    │
│              │  its setter, causes a re-render."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ useState Hook -> useEffect -> Lifting Up│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Never mutate state. Objects and arrays must be replaced
   with new references: `setItems([...items, newItem])` not
   `items.push(newItem); setItems(items)`.
2. State updates are asynchronous and batched. The new value
   is NOT available on the line after `setState()`. Use the
   functional updater `setState(prev => ...)` to base new
   state on current state.
3. State is per-component-instance and local. Two renders
   of `<Counter>` have completely independent states.
   State does not leak to siblings or parents.

**Interview one-liner:**
"State in React is data owned by a component that, when
changed via its setter, schedules a re-render. The three
fundamental rules: never mutate state directly (always
create new references), updates are asynchronous (read the
new value on the next render, not on the next line), and
use the functional updater form when the new state depends
on the current value. State is per-instance and local
unless explicitly shared via props or Context."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Immutability as a change detection mechanism trades memory
for simplicity. Instead of tracking which properties of an
object changed (requires deep equality), you track object
identity (reference equality). New reference = changed;
same reference = unchanged. This pattern appears in event
sourcing (immutable event log), Redux (immutable state
trees), and Kafka (immutable message log).

**Where else this pattern appears:**
- Clojure's persistent data structures - structural sharing
  creates new references efficiently when parts of a
  structure change; same pattern as React's immutable state
- Git - every commit is an immutable snapshot; "changing"
  history creates new commits, never modifies old ones
- Redux - `state = reducer(state, action)` always returns
  a new state object, enabling time-travel debugging

---

### 💡 The Surprising Truth

React's Strict Mode in development intentionally renders
components **twice** to help detect side effects in the
render path. This means `useState` initialiser functions
also run twice in development (but only the first result
is used). If you initialise state with an expensive
computation directly: `useState(expensiveComputation())`
the function runs twice in dev, once in production. This
is why the lazy initialiser form `useState(() =>
expensiveComputation())` exists - it calls the function
once, and Strict Mode's double-invocation does not run it
twice because React only calls initialisers once per
component instance.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe what "state is a snapshot" means
   to a developer who is confused about why `setCount(count
   + 1)` called three times in a row only increments by 1.
2. **DEBUG** Given a component with an infinite re-render
   loop, use React DevTools Profiler to identify the
   causative `useEffect` and add the correct dependency
   array to break the loop.
3. **DECIDE** For each of the following, choose state or ref
   or derived: (a) whether a form is dirty, (b) the previous
   render's scroll position, (c) a user's full name given
   first and last name in state.
4. **REFACTOR** Given a component that stores derived data in
   state (e.g., stores both `items` and `filteredItems`),
   remove the redundant state and compute the derived value
   during render.
5. **AUDIT** Review a codebase for direct state mutation
   patterns (object property assignment, array push/splice
   on state arrays) and fix each with an immutable update.

---

### 🧠 Think About This Before We Continue

**Q1.** React 18 batches all state updates, including those
in async callbacks (setTimeout, Promises). Before React 18,
updates in async callbacks were not batched - each caused a
separate re-render. This change could silently fix performance
issues in upgraded apps, or silently break code that relied
on intermediate renders between updates. How would you
audit a codebase for code that relies on non-batched async
state updates before upgrading to React 18?
*Hint: Look for state reads immediately after async setState
calls, or effects that depend on specific intermediate states.*

**Q2.** The React team's rule of thumb is: "if it's used
in the render output, it's state; if it's not, it's a ref
or a module variable." But there is a class of data that
is used in the render output AND is intentionally not
reactive: default values, initial configuration, static
lookup tables. Where should this data live, and what are
the performance implications of each option?
*Hint: Module-level constants vs useState vs useMemo.*

**Q3.** React's state model works well for client-owned
data (what the user has typed, which tab is selected).
But "server state" (data fetched from an API) has different
characteristics: it is stale by default, shared across
components, needs caching, and can be invalidated by
other actions. Why does storing server state in `useState`
lead to problems, and what does React Query do differently
to model server state correctly?
*Hint: Compare `useState(null)` + `useEffect` fetch vs
React Query's `useQuery`.*