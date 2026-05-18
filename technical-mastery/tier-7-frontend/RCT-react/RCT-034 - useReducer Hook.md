---
id: RCT-034
title: useReducer Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-020, RCT-021, RCT-029
used_by: RCT-036, RCT-051, RCT-052
related: RCT-020, RCT-036, RCT-051
tags:
  - react
  - frontend
  - hooks
  - state
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/react/usereducer-hook/
---

⚡ TL;DR - `useReducer` manages state with a reducer
function `(state, action) => newState`, separating "what
changed" (dispatch an action) from "how it changes"
(the reducer), making complex multi-field state transitions
predictable, testable, and explicit - it is `useState`
with a state machine model.

| #034            | Category: React                                                        | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | useState Hook, useEffect Hook, Lifting State Up                        |                 |
| **Used by:**    | useCallback Hook, Redux Toolkit Architecture, React Fiber Architecture |                 |
| **Related:**    | useState Hook, useCallback Hook, Redux Toolkit                         |                 |

---

### 🔥 The Problem This Solves

**MULTIPLE RELATED STATE VARIABLES THAT CHANGE TOGETHER:**
A complex form or state machine has 5 related state
variables. Some transitions must update multiple at once.
With `useState`:

```jsx
const [loading, setLoading] = useState(false);
const [data, setData] = useState(null);
const [error, setError] = useState(null);
const [status, setStatus] = useState("idle");

// Submit: must update loading, status, clear error
setLoading(true);
setStatus("loading");
setError(null);
// What if one of these fails? What if you forget one?
// State can be in an impossible combination:
// loading=true + status='success' (contradictory)
```

With `useReducer`, a single `dispatch({ type: 'SUBMIT' })`
atomically transitions the entire state to the correct
combination, preventing impossible intermediate states.

---

### 📘 Textbook Definition

**useReducer** - a React hook that manages state using
the reducer pattern: `(currentState, action) => newState`.
The hook returns the current state and a `dispatch`
function. Calling `dispatch(action)` queues a state update:
React calls the reducer with the current state and the
action, uses the returned value as the new state, and
re-renders the component. Like `useState` but with
explicit actions as the update mechanism.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// useState equivalent (simple):
const [count, setCount] = useState(0);
setCount(count + 1);

// useReducer equivalent:
const reducer = (state, action) => {
  switch (action.type) {
    case "INCREMENT":
      return { count: state.count + 1 };
    case "DECREMENT":
      return { count: state.count - 1 };
    case "RESET":
      return { count: 0 };
    default:
      return state;
  }
};

const [state, dispatch] = useReducer(reducer, { count: 0 });
dispatch({ type: "INCREMENT" });
dispatch({ type: "RESET" });
// state.count = 0
```

---

### 🔩 First Principles Explanation

**THE REDUCER PATTERN:**
The name "reducer" comes from functional programming:
`Array.prototype.reduce` takes an accumulator and a value,
returns a new accumulator. A state reducer takes current
state and an action, returns new state:

```
reduce([1,2,3], (acc, val) => acc + val, 0)
  → (0, 1) → 1
  → (1, 2) → 3
  → (3, 3) → 6

state reducer:
  → (idleState, { type: 'SUBMIT' }) → loadingState
  → (loadingState, { type: 'SUCCESS', data }) →
    successState
  → (loadingState, { type: 'ERROR', error }) → errorState
```

**WHY ACTIONS, NOT VALUES:**

```
useState:  dispatch the NEW value
  setUser({ ...user, name: 'Alice' })
  The WHAT (new state) is in the dispatch call

useReducer: dispatch the INTENT (action)
  dispatch({ type: 'UPDATE_NAME', payload: 'Alice' })
  The HOW (new state) is in the reducer
  The WHAT (name changed to Alice) is in the dispatch call

Benefit:
  - Logic centralised in reducer (one place)
  - Actions are loggable/debuggable (what happened, in
    order)
  - Reducer is a pure function → easily unit tested
  - Impossible states eliminated (reducer controls all
    transitions)
```

**WHEN TO USE useReducer vs useState:**

```
Use useState:
  - Single primitive value (counter, toggle, input text)
  - Independent values (no shared transition logic)

Use useReducer:
  - Multiple fields that change together
  - State machine with explicit transitions
    (idle → loading → success/error → idle)
  - Complex logic with many conditions
  - Next state depends on previous in complex ways
  - When you want actions for logging/time-travel
```

---

### 🧪 Thought Experiment

**THE IMPOSSIBLE STATE PROBLEM:**
An async operation has three flags in useState:
`loading`, `success`, `error`. There are `2^3 = 8`
possible combinations. But only 4 are valid:

- `false/false/false` (idle)
- `true/false/false` (loading)
- `false/true/false` (success)
- `false/false/true` (error)

Four combinations are logically impossible:

- `true/true/false` (loading AND success)
- `false/true/true` (success AND error)
- etc.

With three `useState` calls, code can put the component
in an impossible state if any `set*` call is missed.

With `useReducer`:

```jsx
const initialState = { status: "idle", data: null, error: null };

function reducer(state, action) {
  switch (action.type) {
    case "FETCH_START":
      return { status: "loading", data: null, error: null };
    case "FETCH_SUCCESS":
      return { status: "success", data: action.data, error: null };
    case "FETCH_ERROR":
      return { status: "error", data: null, error: action.error };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}
```

One `status` field with 4 valid values. Impossible state
is structurally prevented. The reducer is the single
point of truth for every transition.

---

### 🧠 Mental Model / Analogy

> useReducer is like a Redux store shrunk to a single
> component. The reducer is the same concept: pure function,
> (state, action) => newState, actions as intent
> declarations. `dispatch` in useReducer is the same
> concept as Redux `store.dispatch`. The difference:
> useReducer state is local to the component; Redux state
> is global and accessible from anywhere.
>
> If you outgrow useReducer (need to share state across
> many components), the migration path to Redux is almost
> mechanical: the reducer code moves unchanged, you just
> add a store and a Provider.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
useReducer is like useState but with a switch statement.
Instead of `setState(newValue)`, you `dispatch({ type:
'ACTION_NAME' })`. The reducer function determines the
new state.

**Level 2 (usage):**
`const [state, dispatch] = useReducer(reducer, initialState)`.
Reducer: `(state, action) => newState`. Actions are plain
objects with a `type` string. Payload is additional data:
`{ type: 'SET_NAME', payload: 'Alice' }`. Always return
a new object from the reducer (no mutations).

**Level 3 (patterns):**
Combine with Context: `useReducer` in a parent context
provider, pass `dispatch` via context. Children dispatch
actions without prop drilling. This is the "poor man's
Redux" pattern. Performance: `dispatch` is stable (same
function reference every render) - no `useCallback` needed.

**Level 4 (advanced):**
Lazy initialisation: third argument to `useReducer(reducer,
initialArg, init)`. `init(initialArg)` is called once to
compute initial state. Useful when initial state is
expensive to compute. Immer integration: use `produce()`
in the reducer to write "mutating" code that produces
immutable output.

**Level 5 (mastery):**
Redux Toolkit's `createSlice` generates reducers and
action creators from the same definition - it is `useReducer`
at the framework level with Immer baked in. Understanding
`useReducer` deeply means Redux Toolkit requires almost
no new concepts to learn. The underlying state update
model is identical: `(state, action) => newState`, pure
function, no side effects in the reducer.

---

### ⚙️ How It Works (Mechanism)

**Async fetch state machine with useReducer:**

```jsx
// Complete async state machine
const initialState = {
  status: "idle", // 'idle' | 'loading' | 'success' | 'error'
  data: null,
  error: null,
};

function fetchReducer(state, action) {
  switch (action.type) {
    case "FETCH_START":
      return { status: "loading", data: null, error: null };
    case "FETCH_SUCCESS":
      return { status: "success", data: action.payload, error: null };
    case "FETCH_ERROR":
      return { status: "error", data: null, error: action.payload };
    case "RESET":
      return initialState;
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function UserProfile({ userId }) {
  const [state, dispatch] = useReducer(fetchReducer, initialState);

  useEffect(() => {
    let cancelled = false;
    dispatch({ type: "FETCH_START" });

    fetchUser(userId)
      .then((user) => {
        if (!cancelled) dispatch({ type: "FETCH_SUCCESS",
            payload: user });
      })
      .catch((err) => {
        if (!cancelled) dispatch({ type: "FETCH_ERROR",
            payload: err.message });
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  if (state.status === "loading") return <Spinner />;
  if (state.status === "error") return <ErrorMessage msg={state.error} />;
  if (state.status === "idle") return null;

  // status === 'success': state.data is guaranteed non-null here
  return <Profile user={state.data} />;
}
```

---

### 💻 Code Example

**BAD: useState for multi-step state machine:**

```jsx
// BAD: 4 separate useState calls for related state
// Can produce impossible combinations
// Logic spread across 4 setX calls
function AsyncComponent() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null); // easy to forget this
    setSuccess(false); // easy to forget this
    try {
      const result = await fetchData();
      setData(result);
      setSuccess(true);
      // Forgot to setLoading(false) in the success case!
      // loading=true + success=true: impossible state
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };
  // ...
}
```

**GOOD: useReducer prevents impossible states:**

```jsx
// GOOD: useReducer as explicit state machine
// Only 4 valid status values - impossible states structurally
// prevented
// All transitions in one place

const reducer = (state, action) => {
  switch (action.type) {
    case "LOAD":
      return { status: "loading", data: null, error: null };
    case "SUCCESS":
      return { status: "success", data: action.payload, error: null };
    case "FAILURE":
      return { status: "error", data: null, error: action.payload };
    case "RETRY":
      return { status: "idle", data: null, error: null };
    default:
      return state;
  }
};

function AsyncComponent() {
  const [state, dispatch] = useReducer(reducer, {
    status: "idle",
    data: null,
    error: null,
  });

  const load = async () => {
    dispatch({ type: "LOAD" });
    try {
      const result = await fetchData();
      dispatch({ type: "SUCCESS", payload: result });
    } catch (err) {
      dispatch({ type: "FAILURE", payload: err.message });
    }
  };
  // state.status is always one of: 'idle', 'loading', 'success',
  // 'error'
  // Never both success AND loading simultaneously
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                      |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "useReducer is more powerful than useState"   | They have the same underlying power. `useReducer` can always be expressed as multiple `useState` calls, and vice versa. `useReducer` is a pattern choice (centralised logic, explicit transitions) not a capability upgrade. |
| "You should always use useReducer for forms"  | For simple 2-3 field forms, `useState` per field is clearer. `useReducer` adds value when the form has complex validation dependencies, step-based transitions, or undo/redo requirements.                                   |
| "The reducer must use a switch statement"     | The reducer is just a function: `(state, action) => state`. It can use if/else, object lookup maps, or any other approach. Switch is conventional because it mirrors the Redux community standard, but it is not required.   |
| "dispatch({ type }) is async (like setState)" | `dispatch` is synchronous in the sense that it queues the update. The state value in the current render does not change immediately after `dispatch` (just like `setState`). The new state is available in the NEXT render.  |

---

### 🚨 Failure Modes & Diagnosis

**Mutation in Reducer (Silent Bug)**

**Symptom:** State appears to update but component does
not re-render. Or state updates are inconsistent.

**Root Cause:**

```jsx
// BAD: mutating state directly in reducer
function reducer(state, action) {
  if (action.type === "ADD_ITEM") {
    state.items.push(action.item); // MUTATION
    return state; // same reference → no re-render
  }
}
```

**Fix:** Always return new objects/arrays:

```jsx
function reducer(state, action) {
  if (action.type === "ADD_ITEM") {
    return { ...state, items: [...state.items, action.item] };
  }
}
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `useState Hook` - the simpler alternative for basic state
- `useEffect Hook` - commonly used with useReducer for async
- `Lifting State Up` - context + useReducer is a common pattern

**Builds On:**

- `useCallback Hook` - `dispatch` is stable but action
  creators may need `useCallback` when passed as props
- `Redux Toolkit` - same reducer pattern with global store,
  Immer, and RTK Query

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ API         │ const [state, dispatch] = useReducer(    │
│             │   reducer, initialState)                 │
│ REDUCER     │ (state, action) => newState (pure fn)    │
│ DISPATCH    │ dispatch({ type: 'ACTION', payload: x }) │
├─────────────────────────────────────────────────────────┤
│ USE WHEN    │ Multiple related fields transition at once│
│             │ State machine (idle/loading/success/error)│
│             │ Complex transition logic in one place     │
│ USE useState│ Single/independent values, simple toggle │
├─────────────────────────────────────────────────────────┤
│ RULES       │ Reducer: pure, no side effects            │
│             │ Always return NEW object/array            │
│             │ Default: return state (not throw)         │
├─────────────────────────────────────────────────────────┤
│ dispatch IS │ Stable reference (no useCallback needed)  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `(state, action) => newState`. Pure function. No side
   effects. Always return a new object, never mutate.
2. Use when multiple state variables must transition
   together atomically (prevents impossible states).
3. `dispatch` is stable across renders - pass it to
   children without `useCallback`.

**Interview one-liner:**
"useReducer manages state with a pure reducer function
`(state, action) => newState`. `dispatch(action)` queues
a transition; React calls the reducer and re-renders.
Prefer useReducer over useState when multiple related
fields must change atomically (preventing impossible states),
when you have a state machine (idle/loading/success/error),
or when complex logic benefits from centralisation. The
reducer must be pure - no side effects. `dispatch` is a
stable reference, so it does not need useCallback when
passed as a prop."

---

### 💎 Transferable Wisdom

The reducer pattern is one of the most transferable
concepts in software engineering. It is: the accumulator
function in functional programming, the Flux/Redux
architecture for web apps, event sourcing in distributed
systems (a log of events replayed through a reducer
produces current state), database transaction logs
(a sequence of operations applied to reach current state),
and Git commits (a sequence of diffs/actions applied to
the initial state). The pattern is: immutable state,
explicit actions, pure transition function. This applies
at the component level with useReducer and at the system
level with event sourcing.

---

### 💡 The Surprising Truth

Redux was invented before React hooks existed. React's
`useReducer` hook was introduced in React 16.8 (2019)
as a first-class hook, partly inspired by the popularity
of the Redux pattern. `useReducer` is literally Redux
without the global store. The React team has acknowledged
this: the `useReducer` API (`(state, action) => state`,
`dispatch`) is almost identical to Redux's core model.
For many use cases (component-level state machines), you
never needed Redux - you just needed Redux's pattern,
which is now built into React itself. Redux Toolkit
remains relevant for global state, DevTools, and complex
cross-component state interactions, but the pattern
itself belongs to React.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a multi-step form wizard (3 steps) using
   `useReducer` where the state machine has explicit
   transitions: `(idle → step1 → step2 → step3 → submitting
→ success/error)`.
2. **REFACTOR** a component with 5 `useState` calls for
   an async operation into a single `useReducer` with a
   state machine that eliminates all impossible state
   combinations.
3. **TEST** the reducer function in isolation (without
   React) using unit tests that assert:
   `reducer(state, action)` produces the correct new state.
4. **EXPLAIN** why the reducer function must not contain
   side effects (`fetch`, `localStorage`, `console.log`),
   and where side effects should go instead.
5. **COMPARE** `useReducer` in a context provider vs Redux
   Toolkit with `createSlice`, and state when you would
   graduate from one to the other.

---

### 🧠 Think About This Before We Continue

**Q1.** `useReducer` and `useState` have the same underlying
power. Every `useReducer` can be expressed as `useState`,
and vice versa. But `useReducer` is preferred for certain
patterns. What is the deciding factor - is it purely
organisational preference (one place for logic), or is
there a correctness argument that `useReducer` provides
for state machines that `useState` cannot?

**Q2.** The reducer pattern enforces immutability. But
JavaScript objects are mutable, and React does not freeze
state objects. A developer accidentally mutates state
inside the reducer (`state.count++`). The test passes
because the test library compares by reference. The bug
is subtle in development. How do you structurally prevent
this without adopting a library like Immer? What can you
add to the reducer to detect mutations?

**Q3.** The event sourcing pattern in distributed systems
is: store a log of events, derive current state by replaying.
`useReducer`'s state is NOT event-sourced - it stores
only current state, not the history of actions. What
would you need to add to a `useReducer`-based component
to implement undo/redo? Sketch the state shape and the
reducer for a text editor with full undo history.
