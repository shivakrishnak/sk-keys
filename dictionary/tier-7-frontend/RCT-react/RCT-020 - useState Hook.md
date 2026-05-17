---
id: RCT-020
title: useState Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-007, RCT-010, RCT-013, RCT-016
used_by: RCT-021, RCT-026, RCT-027, RCT-034
related: RCT-010, RCT-021, RCT-034
tags:
  - react
  - frontend
  - hooks
  - state
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /react/usestate-hook/
---

# RCT-020 - USESTATE HOOK

⚡ TL;DR - `useState` is React's primitive for local
component state: it returns a current value and a setter;
calling the setter schedules a re-render with the new
value; state updates are asynchronous, batched, and the
setter is the only correct way to change state.

| #020 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Component, State, Event Handling, One-Way Data Binding | |
| **Used by:** | useEffect Hook, Controlled Components, Form Handling, useReducer | |
| **Related:** | State, useEffect Hook, useReducer Hook | |

---

### 🔥 The Problem This Solves

**CLASS COMPONENT STATE:**
Before React Hooks (pre-16.8), component state was a
class-level concept. Components had to be class components:
extend `React.Component`, use `this.state = {...}` in
constructor, read via `this.state.value`, update via
`this.setState({value: newValue})`. This meant:

- Simple stateful logic required class boilerplate
- `this` binding caused bugs in event handlers
- Logic for related state was split across lifecycle methods
- Functional components could not have state (pure
  presentation only)

`useState` solves all of this. Any function can be a
stateful component. No class, no constructor, no `this`.

---

### 📘 Textbook Definition

`useState` is a React Hook that adds local state to
a function component. It takes an initial state value
and returns a tuple: the current state value and a
setter function. Calling the setter with a new value
schedules a re-render. During the next render, React
calls the component function again; `useState` returns
the new state value. Each `useState` call is identified
by its call order within the component (the "Hooks
rules" enforce consistent call order across renders).

```
const [count, setCount] = useState(0);
         │         │              │
         │         │              └── initial value (first render only)
         │         └─────────────── setter function
         └───────────────────────── current state value
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`useState(initialValue)` returns `[currentValue, setter]`;
calling `setter(newValue)` re-renders the component with
the new value. Never mutate the value directly.

**The five rules of useState:**
1. Initial value is used ONLY on first render
2. Setter replaces state (does not merge like setState)
3. State updates are asynchronous (read new value next render)
4. State is per-component-instance (siblings have separate state)
5. Never mutate state in place (use setter always)

---

### 🔩 First Principles Explanation

**HOW REACT TRACKS STATE:**

```
Hooks are stored in a linked list per component instance.
Call order determines which state slot is which.

First render of Counter component:
  useState(0) → creates slot[0], value=0, returns [0, setter0]
  useState('') → creates slot[1], value='', returns ['', setter1]

After setCount(1):
  React schedules re-render
  Counter function runs again
  useState(0) → reads slot[0], value=1, returns [1, setter0]
  useState('') → reads slot[1], value='', returns ['', setter1]

This is why Hooks must be called in the same order every render:
  if an if/loop changes which Hook runs, the slots are misread.
```

**WHY UPDATES ARE ASYNCHRONOUS:**

```jsx
const [count, setCount] = useState(0);

const handleClick = () => {
  setCount(count + 1);  // schedules update: 0 + 1 = 1
  setCount(count + 1);  // schedules update: 0 + 1 = 1 (same!)
  // count is STILL 0 in this render's closure
  // both calls see count = 0
  // Result: count becomes 1, not 2
};

// FIX: use functional update form
const handleClickFixed = () => {
  setCount(c => c + 1);  // c is the latest value: 0 → 1
  setCount(c => c + 1);  // c is the latest value: 1 → 2
  // Result: count becomes 2
};
```

---

### 🧪 Thought Experiment

**THE STALE CLOSURE:**

```jsx
function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setSeconds(seconds + 1);  // BAD: stale closure
      // seconds is captured from the first render = 0
      // this runs every 1s but seconds is always: 0 + 1 = 1
      // counter shows 1, 1, 1, 1, ... never increases
    }, 1000);
    return () => clearInterval(id);
  }, []); // empty dependency array: runs once

  return <div>{seconds}</div>;
}

// FIX: functional update reads latest state
function TimerFixed() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setSeconds(s => s + 1);  // s is always latest value
    }, 1000);
    return () => clearInterval(id);
  }, []);

  return <div>{seconds}</div>;
}
```

This is the most common `useState` + `useEffect` bug.
The functional update form `setX(prev => prev + 1)` is
the fix for any setter called in a stale closure.

---

### 🧠 Mental Model / Analogy

> `useState` is a locker at a train station. The component
> is assigned a locker number (the hook's position in the
> call order). Each render, the component goes to its
> numbered locker, reads the current contents (state value),
> and receives a key to put new contents in (setter function).
> When the component uses the key to put new contents in
> the locker, it alerts React (schedule re-render). The
> next time the component arrives at the station (next render),
> the locker has the new contents.

```
Component function runs (render):
  useState(0) → reads locker #1, gets [value, setter]
                value = 0 (initially)

User clicks:
  setter(1) → writes 1 to locker #1
             → notifies React (re-render scheduled)

Component function runs again (re-render):
  useState(0) → reads locker #1, gets [value, setter]
                value = 1 (updated)
  Initial value (0) is ignored after first render
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`useState` gives a component memory. Without it, every
render starts fresh. With it, the component can remember
what happened before (user typed something, clicked a
button, loaded data).

**Level 2 (usage):**
`const [value, setValue] = useState(initialValue)`.
Call `setValue(newValue)` to update. Use `setValue(prev =>
newValue(prev))` (functional form) when the new value
depends on the old one. Never mutate the value directly.

**Level 3 (mechanism):**
React stores hook values in a "fibers" linked list per
component instance. Call order determines the slot.
Setter calls enqueue updates. React batches all updates
from an event handler (React 18: all updates everywhere,
including setTimeout and promises). The component re-renders
once per batch, not once per setState call.

**Level 4 (patterns):**
State shape decisions matter. For independent values, use
multiple `useState` calls (easier to read, reset
individually). For related values that change together,
use one `useState` with an object (one update always
consistent). For complex state transitions, switch to
`useReducer` (explicit action types, testable logic).
Lazy initialisation (`useState(() => expensiveComputation())`)
runs the function only on first render - use for
expensive computations.

**Level 5 (internals):**
React 18's automatic batching means `useState` setters
in async callbacks (setTimeout, Promise.then, fetch
callbacks) are now batched just like event handlers
(previously, each was its own re-render). This changes
performance characteristics for code written for React 17.
In the rare case that you need an immediate re-render
(e.g., for reading layout dimensions), `flushSync` from
`react-dom` forces synchronous rendering - but this is
a specific escape hatch, not a general pattern.

---

### ⚙️ How It Works (Mechanism)

**Primitive state patterns:**

```jsx
// Boolean
const [isOpen, setIsOpen] = useState(false);

// String
const [query, setQuery] = useState('');

// Number
const [count, setCount] = useState(0);

// Null (data not yet loaded)
const [user, setUser] = useState(null);

// Toggling boolean
const toggle = () => setIsOpen(prev => !prev);

// Incrementing
const increment = () => setCount(c => c + 1);
```

**Object state (keep fields consistent):**

```jsx
const [form, setForm] = useState({
  name: '',
  email: '',
  age: 0,
});

// Update one field: spread existing, override changed field
const handleNameChange = (e) => {
  setForm(prev => ({
    ...prev,
    name: e.target.value,
  }));
};
// NEVER: form.name = 'new name' (mutation, no re-render)
// NEVER: setForm({ name: 'new' }) (loses email, age fields)
```

**Lazy initialisation for expensive computation:**

```jsx
// WRONG: expensive function runs on EVERY render
const [state, setState] = useState(expensiveCompute());

// RIGHT: function passed (not called) - runs only once
const [state, setState] = useState(() => expensiveCompute());
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
1. Component renders for first time
2. useState(0) → creates state slot with value 0
3. Returns [0, setter]
4. Component renders <button>Count: 0</button>

5. User clicks button
6. onClick fires: setter(prev => prev + 1)
7. React enqueues update for this component's state slot
8. React batches all updates from this event
9. React schedules re-render

10. Component function runs again
11. useState(0) → reads state slot: value = 1
12. Returns [1, setter]
13. Component renders <button>Count: 1</button>
14. React reconciles: only text "0"→"1" changed
15. DOM updated: button text changes to "1"
```

---

### 💻 Code Example

**BAD: Direct mutation and state stale reads:**

```jsx
// BAD: multiple anti-patterns
function Counter() {
  const [count, setCount] = useState({ value: 0 });

  const doubleIncrement = () => {
    // BAD 1: mutation - modifies state in place
    count.value += 1;
    setCount(count);  // React may not re-render
    // (same object reference, shallow comparison may miss it)

    // BAD 2: stale read - reads count.value twice
    // but count.value may not be updated from first set
    setCount({ value: count.value + 1 });
    // Result: unpredictable, typically count goes 0 → 1
    // instead of 0 → 2
  };

  return <button onClick={doubleIncrement}>{count.value}</button>;
}
```

**GOOD: Functional updates and immutable patterns:**

```jsx
// GOOD: immutable state, functional updates
function Counter() {
  const [count, setCount] = useState(0);

  const doubleIncrement = () => {
    // Functional update: each call gets the latest value
    setCount(c => c + 1);  // 0 → 1
    setCount(c => c + 1);  // 1 → 2 (uses updated value)
    // React batches: count goes 0 → 2 in one render
  };

  return <button onClick={doubleIncrement}>{count}</button>;
}
```

**PRODUCTION: Form state management:**

```jsx
function ContactForm() {
  const [fields, setFields] = useState({
    name: '', email: '', message: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const updateField = (field) => (e) => {
    setFields(prev => ({
      ...prev,
      [field]: e.target.value,
    }));
    // Clear error when field changes
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!fields.name.trim()) newErrors.name = 'Required';
    if (!fields.email.includes('@')) {
      newErrors.email = 'Invalid email';
    }
    if (fields.message.length < 10) {
      newErrors.message = 'Too short';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    await submitContact(fields);
    setSubmitting(false);
    setSubmitted(true);
  };

  if (submitted) return <p>Thank you!</p>;

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={fields.name}
        onChange={updateField('name')}
        placeholder="Name"
      />
      {errors.name && <span>{errors.name}</span>}

      <input
        value={fields.email}
        onChange={updateField('email')}
        placeholder="Email"
      />
      {errors.email && <span>{errors.email}</span>}

      <textarea
        value={fields.message}
        onChange={updateField('message')}
        placeholder="Message"
      />
      {errors.message && <span>{errors.message}</span>}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "setState is synchronous - I can read the new value immediately after calling it" | `setState` schedules an asynchronous update. The state variable still holds the OLD value for the rest of the current render's event handler. The new value is available on the NEXT render. |
| "Calling setState multiple times causes multiple re-renders" | React batches all `setState` calls in an event handler into a single re-render. React 18 also batches calls in async callbacks (setTimeout, Promises). |
| "Object and array states update like class component setState (merging fields)" | `useState`'s setter REPLACES the entire state, it does NOT merge. If state is an object, always spread the existing fields: `setForm(prev => ({ ...prev, name: newName }))`. |
| "The initial value to useState is used on every render" | The initial value is used ONLY on the first render to populate the state slot. On subsequent renders, React reads from its internal state storage. The initial value expression is evaluated every render but the result is thrown away after the first. To avoid evaluation cost, use lazy init: `useState(() => expensiveCompute())`. |

---

### 🚨 Failure Modes & Diagnosis

**State Not Updating (Mutation Anti-Pattern)**

**Symptom:** Calling setState but the component does
not re-render. Or re-renders but shows old value.

**Root Cause:**
```jsx
// Direct mutation: React uses Object.is() to compare
// old vs new state. Same reference = no re-render.
setItems(prev => {
  prev.push(newItem);  // mutation
  return prev;         // same array reference
});
// React: prev === prev (Object.is) → no update
```

**Fix:**
```jsx
setItems(prev => [...prev, newItem]); // new array reference
```

---

**Stale Closure in Callbacks**

**Symptom:** A timer, interval, or async callback reads
stale state values.

**Root Cause:** The callback closes over a state snapshot
from when it was created. Later renders produce new
snapshots, but the callback holds the old one.

**Fix:** Use functional update form:
`setState(latest => computeNext(latest))`
This reads from React's internal latest value, not the
closure's captured value.

---

**Performance: Expensive Lazy Init Not Used**

**Symptom:** Slow initial render. `useState(expensiveCompute())`
- the function is called on every render even though
the result is only used once.

**Fix:** `useState(() => expensiveCompute())` - pass a
function (not the result) for lazy initialisation.

---

### 🔗 Related Keywords

**Prerequisites:**
- `State` - the concept; useState is the implementation
- `Component` - state is per-component-instance
- `Event Handling` - the trigger for most setState calls
- `One-Way Data Binding` - state flows down via props

**Builds On:**
- `useEffect Hook` - reads state, triggers on state changes
- `useReducer Hook` - for complex multi-action state logic
- `Controlled vs Uncontrolled Components` - useState
  is the mechanism behind controlled inputs

**Related Alternatives:**
- `useReducer` - for state with multiple transition paths
- `useContext` - sharing state across component tree
- `Zustand/Redux` - for truly global, cross-component state

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DECLARE     │ const [val, setVal] = useState(initial)  │
├──────────────────────────────────────────────────────────┤
│ SET         │ setVal(newValue)                          │
│ SET (func)  │ setVal(prev => computeFrom(prev))        │
│ USE FUNC    │ when new value depends on previous value  │
│ FORM WHEN   │ timers, batched increments, stale closure │
├──────────────────────────────────────────────────────────┤
│ LAZY INIT   │ useState(() => expensiveCompute())        │
│             │ (NOT useState(expensiveCompute()))        │
├──────────────────────────────────────────────────────────┤
│ OBJECT      │ setForm(prev => ({ ...prev, key: val })) │
│ ARRAY ADD   │ setArr(prev => [...prev, newItem])        │
│ ARRAY DEL   │ setArr(prev => prev.filter(fn))          │
├──────────────────────────────────────────────────────────┤
│ NEVER       │ state.field = value  (direct mutation)   │
│             │ setX(count + 1) twice (stale read)       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `const [val, setVal] = useState(init)`. Call `setVal`
   to update. Never mutate `val` directly.
2. When the new value depends on the previous value,
   use the functional form: `setVal(prev => prev + 1)`.
   This prevents stale closure bugs.
3. For object state, always spread: `setState(prev =>
   ({ ...prev, changedField: newValue }))`. The setter
   replaces, it does not merge like class setState.

**Interview one-liner:**
"`useState` adds local state to a function component.
It returns the current value and a setter. Calling the
setter schedules an async re-render - the state variable
still holds the old value for the rest of the current
render. Use the functional update form (`setState(prev =>
...)`) when new value depends on old value (stale closure
prevention). For object state, always spread to avoid
losing fields - the setter replaces, not merges."

---

### 💎 Transferable Wisdom

`useState`'s functional update pattern - `setState(prev =>
next(prev))` instead of `setState(current + delta)` - is
an application of the command/action pattern: express what
to do (compute new state from current), not what to set
(read current state and compute). This avoids the race
condition where multiple concurrent reads all see the same
current value. The same pattern appears in database
transactions (`UPDATE counter SET value = value + 1`
instead of `SELECT` then `UPDATE`) and concurrent systems
(compare-and-swap primitives).

---

### 💡 The Surprising Truth

React does not use `===` to compare the new state to the
old state to decide whether to re-render. It uses
`Object.is()`, which is nearly identical to `===` but has
two key differences: `Object.is(NaN, NaN)` is `true`
(unlike `NaN !== NaN`), and `Object.is(+0, -0)` is `false`
(unlike `+0 === -0`). For practical purposes, this means
calling `setState(sameValue)` with the same primitive value
does NOT trigger a re-render (React bails out). But for
objects and arrays, a new reference always triggers a
re-render even if the data inside is identical - because
`Object.is({}, {})` is `false`. This is why you should not
create new objects unnecessarily in render paths.

---

### ✅ Mastery Checklist

1. **EXPLAIN** why `setCount(count + 1); setCount(count +
   1)` in an event handler increments count by 1 not 2,
   and rewrite using the functional form to get the
   correct result.
2. **DIAGNOSE** a timer bug where a counter stops at 1
   despite an interval calling `setCount(count + 1)` every
   second - identify the stale closure and apply the fix.
3. **IMPLEMENT** lazy initialisation for a component that
   reads initial state from `localStorage`, and explain
   why `() =>` is required.
4. **UPDATE** nested object state correctly without
   mutation: given `{ user: { name: '', address: { city:
   '' } } }`, update only `city` using spread operators.
5. **EXPLAIN** the difference between React 17 and React
   18 batching behaviour, and when `flushSync` is
   appropriate.

---

### 🧠 Think About This Before We Continue

**Q1.** `useState` stores state per component instance.
A `<Counter />` component rendered twice has two separate
state slots. But what about component instances created
inside a loop: `items.map(item => <Counter key={item.id}
/>)`? Each Counter has its own state. When an item is
deleted (key removed from list), what happens to that
Counter's state? When does React create new state vs
reuse existing state for a component?

**Q2.** React 18 introduced automatic batching: all state
updates are batched, even in async callbacks. Before React
18, only event handler updates were batched. Consider
this code:
```jsx
setTimeout(() => {
  setA(1);
  setB(2);
}, 0);
```
In React 17: two re-renders. In React 18: one re-render.
What impact does this have on code that reads state
immediately after a state setter call, or code that
assumes each setState causes a visible DOM update?

**Q3.** `useState` is implemented using React Fiber's
hook linked list. The Hooks Rules (call hooks at top
level, not inside conditions or loops) exist because
of this implementation. If React used a Map (keyed by
variable name at call site) instead of a linked list
(keyed by call order), would the Hooks Rules be
necessary? What are the trade-offs of the Map approach
vs the linked list approach?