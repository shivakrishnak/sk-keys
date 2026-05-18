---
id: RCT-024
title: Custom Hooks
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-020, RCT-021, RCT-022, RCT-023
used_by: RCT-026, RCT-027, RCT-028, RCT-039
related: RCT-021, RCT-023, RCT-039
tags:
  - react
  - frontend
  - hooks
  - composition
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/react/custom-hooks/
---

⚡ TL;DR - A custom hook is a JavaScript function named
with `use` that calls other hooks; it is React's primary
pattern for sharing stateful logic between components
without wrapper components; each call creates isolated
state (no sharing between callers).

| #024            | Category: React                                                 | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | useState Hook, useEffect Hook, useContext Hook, useRef Hook     |                 |
| **Used by:**    | Controlled Components, Form Handling, React Router, Context API |                 |
| **Related:**    | useEffect Hook, useRef Hook, Context API                        |                 |

---

### 🔥 The Problem This Solves

**THE LOGIC DUPLICATION PROBLEM:**
Before custom hooks, reusing stateful logic across
components required patterns like Higher-Order Components
(HOC) or Render Props - both involve wrapping components
inside other components, adding nesting ("wrapper hell"),
making the component tree hard to read, and creating
potential prop namespace collisions.

Custom hooks allow stateful logic to be extracted into
a plain function that can be imported and called from any
component. No wrapper components. No nesting. No prop
renaming. The same data-fetching logic, form validation
logic, or subscription logic can be called from ten
different components with five lines each.

---

### 📘 Textbook Definition

A **custom hook** is a JavaScript function whose name
starts with `use` and that calls one or more React hooks
internally. Custom hooks are not a React API - they are
a naming convention that React (and its linter rules)
recognises to identify hook-containing functions. Each
call to a custom hook creates isolated state: two
components using `useCounter()` each get their own
independent counter. Custom hooks can return anything:
a value, a tuple, an object with state and callbacks,
or nothing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Extract `useState + useEffect + logic` into a function
named `useSomething`. Import and call it from any
component that needs that logic.

**Before vs After:**

```jsx
// BEFORE: logic duplicated in each component
function ComponentA() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true);
    fetchUser(userId).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [userId]);
  // ...same 8 lines in ComponentB, ComponentC
}

// AFTER: logic extracted once, used anywhere
function useUser(userId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true);
    fetchUser(userId).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [userId]);
  return { data, loading };
}

function ComponentA() {
  const { data } = useUser(userId);
}
function ComponentB() {
  const { data } = useUser(userId);
}
// Each has its own independent state
```

---

### 🔩 First Principles Explanation

**THE `use` PREFIX CONTRACT:**

```
React rules for hooks apply to custom hooks too:
  1. Only call at top level (no loops/conditions)
  2. Only call from React functions (components or
     other custom hooks)

The `use` prefix signals to:
  - Developers: "this function uses hooks"
  - The linter: "apply react-hooks rules to this function"
  - React DevTools: "show the hook's internal state in the
    component that calls it"

Without the `use` prefix:
  - No linter protection
  - DevTools does not show internal state
  - Other developers do not know hooks are used inside
```

**ISOLATED STATE PER CALL:**

```
Two components calling the same custom hook:

ComponentA calls useCounter()
  → creates state slot A1 (count = 0) for ComponentA

ComponentB calls useCounter()
  → creates state slot B1 (count = 0) for ComponentB

ComponentA's count changes to 5:
  → ComponentA re-renders (count = 5)
  → ComponentB unaffected (still count = 0)

State is NOT shared between components by calling
the same custom hook. Each call is independent.
To share state: use context or external state manager.
```

---

### 🧪 Thought Experiment

**`useFetch` WITHOUT vs WITH CUSTOM HOOK:**
A dashboard has three widgets: user info, recent orders,
notification count. Each needs to fetch data, show loading,
handle errors, and re-fetch when their ID prop changes.

Without custom hook: each widget has 15 lines of
`useState`/`useEffect` fetch logic. Three copies of
identical logic with minor variations. Fixing a bug
(e.g., missing AbortController cleanup) requires three
separate fixes. Adding a feature (retry on error) requires
three separate additions.

With `useFetch(url)` custom hook: each widget is 2 lines.
Bug fixes apply in one place. New features (retry, caching)
added once. The three widgets are now purely presentational

- they declare what data they need, not how to fetch it.

---

### 🧠 Mental Model / Analogy

> Custom hooks are like recipes. A recipe extracts a
> cooking process (sauté onions, deglaze with wine, reduce)
> so that multiple dishes can use the same technique without
> each dish describing the technique from scratch. Each
> time you cook a dish using the recipe, you get your own
> pot with your own ingredients - the techniques are shared
> but the food is separate (isolated state per call). If
> you improve the recipe (better sauté technique), all
> dishes benefit.

```
Without custom hooks:
  ComponentA: 15 lines of fetch logic + UI
  ComponentB: 15 lines of fetch logic + UI  ← same logic
  ComponentC: 15 lines of fetch logic + UI  ← same logic

With custom hooks:
  useFetch:   15 lines of fetch logic (once)
  ComponentA: useData() + 3 lines of UI
  ComponentB: useData() + 3 lines of UI
  ComponentC: useData() + 3 lines of UI
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Custom hooks are how you reuse logic in React. Extract any
`useState + useEffect` combination that you want to use
in multiple places into a function starting with `use`.

**Level 2 (usage):**
Create a function `useXxx`. Inside, use any hooks you need.
Return whatever the calling component needs (state values,
callbacks). Each component that calls `useXxx` gets its
own independent state.

**Level 3 (mechanism):**
Custom hooks are not special to React - they are regular
functions. React treats them the same as component functions
for hook rules enforcement. The `use` prefix is a convention
that enables linter rule application. Hooks inside the custom
hook create state slots in the calling COMPONENT's Fiber
node - not in any intermediate container. The custom hook
has no state of its own.

**Level 4 (patterns):**
Good custom hooks have a single concern: `useFetch` for
data fetching, `useForm` for form management, `useDebounce`
for debounced values. They encapsulate state AND behavior
(the effect that drives the state). They expose a stable
API regardless of implementation. Testing custom hooks
directly is cleaner than testing them through components

- use the `renderHook` utility from React Testing Library.

**Level 5 (mastery):**
Custom hooks are the atomic unit of React's composability
model. Complex hooks can be built from simpler ones:
`useUserWithPermissions` = `useUser` + `usePermissions`
composed together. This is React's alternative to HOC
composition chains. At scale, a well-designed custom hook
API becomes the team's shared vocabulary: instead of each
engineer implementing auth checks, form validation, and
API calls differently, custom hooks standardise the
patterns. The hooks library becomes a force multiplier.

---

### ⚙️ How It Works (Mechanism)

**Pattern: data fetching hook:**

```jsx
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(url, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}

// Usage in any component:
function UserPage({ userId }) {
  const { data: user, loading,
      error } = useFetch(`/api/users/${userId}`);
  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <Profile user={user} />;
}
```

**Pattern: event listener hook:**

```jsx
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () =>
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return size;
}
```

**Pattern: local storage sync:**

```jsx
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item !== null ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setAndStore = (newValue) => {
    setValue(newValue);
    try {
      localStorage.setItem(key, JSON.stringify(newValue));
    } catch {
      // storage quota exceeded or private mode
    }
  };

  return [value, setAndStore];
}

// Usage:
const [theme, setTheme] = useLocalStorage("theme", "light");
```

---

### 💻 Code Example

**BAD: Logic duplicated across components:**

```jsx
// BAD: same subscription pattern in three places
function UserList() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    const unsub = db.collection("users").onSnapshot((s) => {
      setUsers(s.docs.map((d) => d.data()));
    });
    return unsub;
  }, []);
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}

function AdminList() {
  const [admins, setAdmins] = useState([]);
  useEffect(() => {
    const unsub = db.collection("admins").onSnapshot((s) => {
      setAdmins(s.docs.map((d) => d.data()));
    });
    return unsub;
  }, []);
  return (
    <ul>
      {admins.map((a) => (
        <li key={a.id}>{a.name}</li>
      ))}
    </ul>
  );
}
// Same 7-line pattern duplicated. Bugs fixed twice.
// Adding error handling: done twice.
```

**GOOD: Logic extracted into custom hook:**

```jsx
// GOOD: custom hook encapsulates the subscription
function useCollection(collectionName) {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const unsub = db.collection(collectionName).onSnapshot(
      (snapshot) => setItems(snapshot.docs.map((d) => d.data())),
      (err) => setError(err.message),
    );
    return unsub;
  }, [collectionName]);

  return { items, error };
}

function UserList() {
  const { items: users } = useCollection("users");
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}

function AdminList() {
  const { items: admins } = useCollection("admins");
  return (
    <ul>
      {admins.map((a) => (
        <li key={a.id}>{a.name}</li>
      ))}
    </ul>
  );
}
// Logic written once. Error handling written once.
// Behaviour fixed in one place.
```

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                         |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Custom hooks share state between all components that use them"        | Each call to a custom hook creates INDEPENDENT state. Calling `useCounter()` in ComponentA and ComponentB gives each its own counter. To share state, use Context or external state management inside the hook. |
| "Custom hooks are a React feature that needs special setup"            | Custom hooks are plain JavaScript functions. The `use` prefix is a naming convention. No special setup, no API import. The only requirement: call hooks inside and name the function `useSomething`.            |
| "Custom hooks can only be used in components"                          | Custom hooks can call other custom hooks. The rule is: hooks must be called from a React function component OR from another custom hook. `useX` calling `useY` is valid.                                        |
| "Custom hooks are equivalent to HOCs - same pattern, different syntax" | HOCs wrap components (adding nesting to the component tree). Custom hooks extract logic without any component wrapping. They are fundamentally different: hooks compose logic, HOCs compose components.         |

---

### 🚨 Failure Modes & Diagnosis

**Function Calls Hook but Is Not Named with `use`**

**Symptom:**
`React Hook "useState" cannot be called in a function that
is not a React function component or a custom React Hook
function.`

**Root Cause:** A utility function that uses hooks is
not named with the `use` prefix.

**Fix:** Rename the function from `getUser()` to `useUser()`.

---

**Custom Hook Used in Conditional - Rules Violation**

**Symptom:**
`React Hook "useMyHook" is called conditionally.`

**Root Cause:** Hook called inside an `if` block or
conditional expression.

**Fix:** Move the hook call to the top level of the
component. Move the condition inside the hook if needed.

---

**Shared State Expected but Not Received**

**Symptom:** Two components using the same custom hook
show different state values when one should update the other.

**Root Cause:** Custom hooks create isolated state per
call. There is no sharing between callers by default.

**Fix:** Add a Context to the custom hook: the hook wraps
the state in a Provider and consumers use `useContext`
internally. Or use an external state manager.

---

### 🔗 Related Keywords

**Prerequisites:**

- `useState Hook` - the state primitive custom hooks use
- `useEffect Hook` - the side effect primitive
- `useRef Hook` - the persistence primitive

**Builds On:**

- `Custom Hooks testing` - `renderHook` from React
  Testing Library for unit testing custom hooks in isolation
- `Context API` - extend custom hooks with context for
  shared state across components
- `Higher-Order Components (HOC)` - the older alternative
  pattern that custom hooks replaced

**Library Examples:**

- React Query's `useQuery`, SWR's `useSWR` - custom hooks
  that encapsulate the fetch-cache pattern
- React Router's `useNavigate`, `useParams` - custom hooks
  that expose router state

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PATTERN  │ function useName() { useState; useEffect;  │
│          │   return { value, handler }; }             │
├─────────────────────────────────────────────────────────┤
│ RULES    │ Name MUST start with "use"                 │
│          │ Call hooks at top level inside             │
│          │ Can call other custom hooks                │
├─────────────────────────────────────────────────────────┤
│ STATE    │ Each caller gets INDEPENDENT state         │
│          │ No sharing without Context or store        │
├─────────────────────────────────────────────────────────┤
│ TESTING  │ renderHook(() => useMyHook())              │
│          │ from @testing-library/react                │
├─────────────────────────────────────────────────────────┤
│ GOOD FOR │ Fetch logic, subscriptions, form state,   │
│          │ local storage sync, window events         │
│ NOT FOR  │ Pure utility functions (no hooks needed)   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. A custom hook is a function named `use...` that calls
   React hooks. No special API, just a naming convention.
2. Each component call to a custom hook gets INDEPENDENT
   state. To share state, add Context or a store inside.
3. Custom hooks replace the HOC/Render Props pattern for
   sharing logic. They compose better, add no component
   nesting, and are easier to test.

**Interview one-liner:**
"A custom hook is a function named `useSomething` that
calls React hooks. It extracts stateful logic for reuse
across components. Each call creates independent state

- no sharing unless you add Context or an external store.
  Custom hooks replaced Higher-Order Components as the
  primary logic-sharing pattern: same capability, no
  component wrapper nesting, easier to test with
  `renderHook`. The `use` prefix enables the React hooks
  linter to apply rules to the function."

---

### 💎 Transferable Wisdom

Custom hooks are React's implementation of the Strategy
or Facade pattern from OOP - encapsulating a behaviour
behind a clean interface, hiding the implementation
details. The same principle appears in: database access
objects (DAO) hiding SQL queries, service layers hiding
API calls, Python context managers hiding setup/teardown.
Custom hooks make the "what" (I need user data) visible
and the "how" (fetch, state, loading, error, cleanup)
invisible to the consumer. When requirements change
(switch from REST to GraphQL, add caching), only the
hook implementation changes, not the consumers.

---

### 💡 The Surprising Truth

React DevTools shows the state of custom hooks inside
the component that uses them - not in a separate hook
component. If `useUser()` internally has `useState` and
`useEffect`, those appear in the component's hooks list
in DevTools, attributed to `useUser`. This is why naming
matters: DevTools labels each hook by the custom hook
function name. An anonymous function would show up as
an unlabelled entry, making debugging harder. Named
custom hooks with clear `use` prefix names give you
the best DevTools experience.

---

### ✅ Mastery Checklist

1. **CREATE** a `useDebounce(value, delay)` custom hook
   that returns the debounced value - debouncing using
   `useEffect` + `useRef` + `useState`.
2. **CREATE** a `useLocalStorage(key, initialValue)` hook
   that syncs a state value to localStorage, with error
   handling for private browsing mode.
3. **TEST** a custom hook using `renderHook` from React
   Testing Library - test `useCounter` with initial value,
   increment, decrement, and reset actions.
4. **EXPLAIN** why `function useData()` requires the
   `use` prefix and what happens at runtime if the prefix
   is omitted (rules violation, linter error, DevTools
   display).
5. **DESIGN** a `useFetch(url, options)` hook with:
   loading state, error state, abort on unmount, abort
   and re-fetch when url changes, and a manual refetch
   trigger.

---

### 🧠 Think About This Before We Continue

**Q1.** Two components both call `useShoppingCart()`. The
hook uses `useState` internally. Each component has its
own independent state. A user adds an item in ComponentA -
ComponentB does not update. How would you modify the
`useShoppingCart` hook to share cart state between all
callers, and what are the two approaches?

**Q2.** A custom hook `usePriceFeed(symbol)` subscribes
to a real-time price WebSocket. It returns the latest
price. If three components on the same page all call
`usePriceFeed('AAPL')`, they each create their own
WebSocket subscription - three connections for the same
data. How would you design the hook to share one
WebSocket subscription across all callers subscribing
to the same symbol?

**Q3.** Custom hooks can call other custom hooks: `useAuth`
can call `useFetch` internally. At what depth does hook
composition become a performance or debuggability concern?
What tooling helps trace which custom hook is responsible
for which state change in a complex hook composition chain?
