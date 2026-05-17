---
id: RCT-021
title: useEffect Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-007, RCT-010, RCT-020
used_by: RCT-023, RCT-024, RCT-025, RCT-049
related: RCT-020, RCT-023, RCT-049
tags:
  - react
  - frontend
  - hooks
  - side-effects
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /react/useeffect-hook/
---

# RCT-021 - USEEFFECT HOOK

⚡ TL;DR - `useEffect` runs side effects (data fetching,
subscriptions, DOM setup) after the component renders;
the dependency array controls when it re-runs; the return
function is a cleanup that runs before the next effect
or on unmount; missing dependencies and missing cleanup
are the two most common bugs.

| #021 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Component, State, useState Hook | |
| **Used by:** | useContext Hook, useRef Hook, Custom Hooks, useEffect Overuse Anti-Pattern | |
| **Related:** | useState Hook, useRef Hook, useEffect Overuse Anti-Pattern | |

---

### 🔥 The Problem This Solves

**SIDE EFFECTS IN A PURE RENDER WORLD:**
React's rendering model is designed around pure functions:
given the same props and state, a component always returns
the same JSX. But real applications require impure
operations: fetching data from a server, subscribing to
a WebSocket, setting up timers, logging to analytics,
syncing state to localStorage. These are "side effects"
- operations that interact with the world outside the
function's input/output contract.

Running side effects directly in the function body is
wrong: they run on every render (including renders
triggered by unrelated state changes), cannot be cleaned
up, and cause infinite loops when they update state.

`useEffect` provides a controlled place to run side effects
after render, with explicit dependency tracking and cleanup.

---

### 📘 Textbook Definition

`useEffect(effect, deps)` schedules a side effect to run
after the component renders. The `effect` function runs
after the DOM is committed. The `deps` array controls
when it re-runs: an empty array `[]` means run once after
mount; no array means run after every render; specific
values `[a, b]` means run when `a` or `b` change. The
effect function may return a cleanup function that React
calls before running the effect again (on deps change)
and when the component unmounts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`useEffect(() => { doSideEffect(); return cleanup; },
[deps])` - runs after render, re-runs when deps change,
cleanup runs before next run or unmount.

**Three dependency array forms:**

```jsx
useEffect(() => { ... });       // runs after EVERY render
useEffect(() => { ... }, []);   // runs ONCE (on mount)
useEffect(() => { ... }, [id]); // runs when id changes
```

**The cleanup function:**

```jsx
useEffect(() => {
  const sub = subscribe(userId);     // setup
  return () => sub.unsubscribe();    // cleanup
}, [userId]);
// cleanup runs: when userId changes (before next setup)
// cleanup runs: when component unmounts
```

---

### 🔩 First Principles Explanation

**THE EFFECT LIFECYCLE:**

```
Render N (first):
  React commits DOM
  effect runs: subscribes to userId A
  cleanup scheduled

Render N+1 (userId changes to B):
  React commits DOM
  CLEANUP from previous effect runs: unsubscribes A
  NEW effect runs: subscribes to userId B
  new cleanup scheduled

Component unmounts:
  CLEANUP runs: unsubscribes B
```

**DEPENDENCY ARRAY CONTRACT:**

```
No array:
  Effect runs after every render.
  Usually wrong (infinite loops if effect sets state).
  Use case: effects that intentionally respond to all renders.

[]:
  Effect runs once after first render (mount).
  Never re-runs. Cleanup runs on unmount.
  Use case: one-time setups (analytics init, global listeners).

[dep1, dep2]:
  Effect runs when dep1 OR dep2 changes.
  React compares using Object.is().
  RULE: all values read inside the effect must be in deps.
  Linter (eslint-plugin-react-hooks) enforces this.
```

---

### 🧪 Thought Experiment

**MISSING DEPENDENCY - THE SILENT BUG:**

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId)         // reads userId
      .then(setUser);
  }, []);                     // BUG: [] means "never re-run"
  // When userId prop changes (user navigates to another
  // profile), the effect does NOT re-run.
  // Old user data shown for new userId.
  // Symptoms: stale data, no error, very hard to spot.

  return <div>{user?.name}</div>;
}

// FIX: include userId in deps
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);
// Now re-runs whenever userId changes.
```

This is the most common `useEffect` bug. The React Hooks
linter (`eslint-plugin-react-hooks`, `exhaustive-deps` rule)
detects this at development time.

---

### 🧠 Mental Model / Analogy

> `useEffect` is a thermostat for your component's side
> effects. The dependency array is the temperature reading.
> When the temperature (deps) changes, the thermostat
> triggers: first it turns off the previous heating mode
> (cleanup), then starts the new one (effect). An empty
> deps array is a thermostat that activates once when
> installed and deactivates when removed - it does not
> respond to temperature changes.

```
Render cycle:

  Component renders (virtual thermostat check)
  │
  React commits DOM changes
  │
  useEffect cleanup (from previous run):
    cancels previous subscriptions / timers
  │
  useEffect runs:
    sets up new subscriptions / timers
    captures current closure values
  │
  (waits for next render or unmount)
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`useEffect` is how you "do things outside of rendering":
load data, set up a timer, subscribe to events. It runs
after the component appears on screen.

**Level 2 (usage):**
Write `useEffect(() => { ... }, [deps])`. Put anything
that needs to happen after render inside. Return a cleanup
function if setup needs reversal. List everything the
effect reads in the deps array.

**Level 3 (mechanism):**
Effects run after the browser has painted (asynchronously).
React 18's strict mode intentionally unmounts and remounts
components in development to detect missing cleanups.
Deps comparison is `Object.is()` - objects and functions
change reference every render, so putting `{}` or `() =>`
in deps causes infinite loops.

**Level 4 (patterns):**
Separate concerns into separate effects. Combine the
fetch-set-cancel pattern for async operations. Use
`AbortController` to cancel in-flight requests on cleanup.
For derived state from props or state, use direct
computation during render (no effect needed) - effects
for derived state are almost always wrong.

**Level 5 (mastery):**
`useEffect` is not the right tool for synchronising with
external systems that need synchronous DOM access. For
that, `useLayoutEffect` runs synchronously after DOM
mutations but before paint. Using `useEffect` for
layout-dependent operations causes flicker (paint with
old layout, effect runs, layout changes, repaint).
In React 18, effects in concurrent mode may run multiple
times in development (Strict Mode double-invocation).
Production only runs effects once per mount.

---

### ⚙️ How It Works (Mechanism)

**Data fetching pattern:**

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchUser(userId)
      .then(data => {
        if (!cancelled) {  // prevent stale update
          setUser(data);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => { cancelled = true; };  // cleanup
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <Profile user={user} />;
}
```

**Subscription pattern:**

```jsx
useEffect(() => {
  const handleResize = () => {
    setWindowWidth(window.innerWidth);
  };

  window.addEventListener('resize', handleResize);

  // Cleanup: remove listener on unmount or re-run
  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []); // [] - setup once, cleanup on unmount
```

**AbortController for fetch cancellation:**

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, {
    signal: controller.signal,
  })
    .then(r => r.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err.message);
    });

  return () => controller.abort();  // cancels in-flight request
}, [userId]);
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
1. Component mounts with userId = 123
2. React commits DOM (loading skeleton shown)
3. useEffect runs: fetch /api/users/123 starts
4. Fetch completes: setUser(data), setLoading(false)
5. Re-render: user profile displayed

6. userId prop changes to 456
7. React re-renders component (still shows user 123 briefly)
8. React commits DOM
9. useEffect CLEANUP runs: cancelled = true
   (response for user 123 will be ignored if it arrives)
10. useEffect runs: fetch /api/users/456 starts
11. Fetch for user 123 arrives: cancelled = true → ignored
12. Fetch for user 456 arrives: setUser(data456)
13. Re-render: user 456 profile displayed

14. Component unmounts
15. useEffect cleanup runs: cancels any in-flight request
```

---

### 💻 Code Example

**BAD: Missing cleanup, missing deps, wrong placement:**

```jsx
// BAD: Three common mistakes in one effect
function LiveClock() {
  const [time, setTime] = useState(new Date());

  // MISTAKE 1: No dependency array - runs after every render
  // MISTAKE 2: Sets state → triggers render → runs effect
  //            → sets state → triggers render → INFINITE LOOP
  // MISTAKE 3: No cleanup - timer keeps running if unmounted
  useEffect(() => {
    setInterval(() => {
      setTime(new Date());
    }, 1000);
  });

  return <div>{time.toLocaleTimeString()}</div>;
}
```

**GOOD: Correct dependency array and cleanup:**

```jsx
// GOOD: [] for mount-once, cleanup returns clearInterval
function LiveClock() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => {
      setTime(new Date());
    }, 1000);

    // Cleanup: stop interval when component unmounts
    return () => clearInterval(id);
  }, []); // [] - set up once on mount, clean up on unmount

  return <div>{time.toLocaleTimeString()}</div>;
}
```

**PRODUCTION: Async data fetch with race condition prevention:**

```jsx
function SearchResults({ query }) {
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState('idle');

  useEffect(() => {
    if (!query) {
      setResults([]);
      setStatus('idle');
      return;  // early return, no cleanup needed
    }

    const controller = new AbortController();
    setStatus('loading');

    searchAPI(query, { signal: controller.signal })
      .then(data => {
        setResults(data);
        setStatus('success');
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setStatus('error');
        }
        // AbortError: request was cancelled, silently ignore
      });

    return () => controller.abort();
  }, [query]);

  if (status === 'loading') return <Spinner />;
  if (status === 'error') return <p>Search failed</p>;
  if (!results.length && status === 'success') {
    return <p>No results for "{query}"</p>;
  }
  return <ResultsList results={results} />;
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`useEffect` with `[]` is like `componentDidMount`" | Approximate equivalent only. In React 18 Strict Mode, `useEffect` with `[]` runs twice in development (mount, unmount, remount) to detect missing cleanups. `componentDidMount` ran once. This is intentional - if your effect breaks when run twice, it has a missing cleanup. |
| "Missing dependencies is just a linter warning, not a real bug" | Missing deps is a silent correctness bug. The component appears to work until the dependency changes - then it shows stale data indefinitely. The linter rule is enforcing correctness, not style. |
| "`useEffect` runs before the browser paints (like synchronous code)" | `useEffect` runs AFTER the browser has committed and painted the DOM. For effects that need to run before paint (to avoid visual flicker), use `useLayoutEffect`. Most effects correctly use `useEffect`. |
| "I can fix the infinite loop by removing the dependency from the array" | Removing a dependency from the array is suppressing the symptom, not fixing the bug. The correct fix is: if a function is a dep, wrap it in `useCallback`; if an object is a dep, memoize it with `useMemo` or move it outside the component. |

---

### 🚨 Failure Modes & Diagnosis

**Memory Leak: Missing Cleanup on Unmount**

**Symptom:**
```
Warning: Can't perform a React state update on an
unmounted component.
```
(This warning was removed in React 18 but the underlying
bug - updating state after unmount - still causes issues.)

**Root Cause:** Effect starts async work (fetch, timeout,
subscription). Component unmounts before work completes.
Work completes, callback calls `setState` on the now-
unmounted component. The update is discarded but React
logs the warning.

**Fix:**
```jsx
useEffect(() => {
  let mounted = true;
  fetch(url).then(d => { if (mounted) setState(d); });
  return () => { mounted = false; };
}, [url]);
```

---

**Infinite Loop**

**Symptom:** Browser tab freezes. Continuous re-renders
visible in React DevTools Profiler.

**Root Cause patterns:**
- No dependency array: effect sets state → re-render →
  effect runs again
- Object/function in deps: new reference every render →
  effect sees "change" → re-runs every render

**Fix:** Add `[]` if the effect should run once. If deps
contain objects/functions, stabilise them with
`useMemo`/`useCallback`, or move to outside the component.

---

**Race Condition: Stale Response**

**Symptom:** Fast clicks on a list show the wrong user
data - the last click wins only sometimes.

**Root Cause:** Effect triggers multiple fetch requests
in sequence. Responses arrive out of order. Last response
wins regardless of which request was latest.

**Fix:** Use `AbortController` cleanup or a cancelled flag
to discard responses from non-latest requests.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Component` - effect is tied to component lifecycle
- `State (useState)` - effect reads state, triggers re-run
  when state changes

**Builds On:**
- `Custom Hooks` - extract effects + state into reusable
  hooks (e.g., `useFetch`, `useDebounce`)
- `useRef` - ref values can be read in effects without
  being deps (stable reference)
- `useEffect Overuse Anti-Pattern` - when NOT to use
  useEffect (derived state, syncing to state)

**Alternatives:**
- `useLayoutEffect` - synchronous after DOM commit, before
  paint (for layout measurement)
- React Query / SWR - data-fetching libraries that
  handle the fetch-cache-cancel pattern automatically

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SYNTAX      │ useEffect(() => {               │
│             │   doSideEffect();                │
│             │   return () => cleanup();        │
│             │ }, [dep1, dep2]);                │
├──────────────────────────────────────────────────────────┤
│ DEPS=none   │ Runs after every render          │
│ DEPS=[]     │ Runs once on mount               │
│ DEPS=[a,b]  │ Runs when a or b changes         │
├──────────────────────────────────────────────────────────┤
│ CLEANUP     │ Returned function: cancel fetch, │
│             │ clearInterval, removeEventListener│
│             │ Runs before next effect + unmount│
├──────────────────────────────────────────────────────────┤
│ RULES       │ All values read inside = in deps │
│             │ Return cleanup if setup exists   │
│             │ Objects/functions = stable refs  │
├──────────────────────────────────────────────────────────┤
│ AVOID IN    │ Derived state, event handler sync,│
│ EFFECTS     │ state transformations on render  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Every value read inside the effect must be in the
   dependency array. Missing deps = silent stale data bug.
   The linter rule `exhaustive-deps` detects this.
2. Always return a cleanup function when the effect sets
   up subscriptions, timers, or fetch requests. No cleanup
   = memory leaks and stale callbacks.
3. For async effects, prevent stale state updates with
   `AbortController` (for fetch) or a `cancelled` flag.
   React 18 Strict Mode mounts components twice to force
   you to handle this correctly.

**Interview one-liner:**
"`useEffect` runs side effects after render. The dependency
array controls when it re-runs: `[]` = once on mount, `[dep]`
= when dep changes, no array = after every render. The
return value is a cleanup that runs before the next run
and on unmount. The two most common bugs: missing deps
(effect never re-runs for changed data) and missing
cleanup (memory leaks, stale callbacks, duplicate
subscriptions). React 18 Strict Mode double-mounts
components to expose missing cleanups."

---

### 💎 Transferable Wisdom

`useEffect` with cleanup is React's expression of RAII
(Resource Acquisition Is Initialisation) from C++:
tie resource setup (subscription, timer, connection) to
a component's lifetime. The cleanup function is the
destructor. This pattern appears in: OS file descriptors
(open/close), database connections (connect/disconnect),
Go's `defer` keyword, and Python's context managers
(`with` statement). The principle: every setup must have
a paired teardown, and the teardown must be guaranteed
to run when the scope ends.

---

### 💡 The Surprising Truth

React 18's Strict Mode intentionally mounts, unmounts,
and remounts every component in development. This causes
every `useEffect` to run twice. This is not a bug - it is
a deliberate correctness check. If your app breaks when
effects run twice (double fetches, duplicate subscriptions,
state corruption), it means you have missing cleanups.
Correct effects are idempotent: running them twice with
proper cleanup produces the same result as running them
once. The double-invocation reveals bugs that would
manifest in production during React's concurrent rendering
(where components can be interrupted and restarted).

---

### ✅ Mastery Checklist

1. **EXPLAIN** the three dependency array forms and the
   use case for each. Explain why no array causes infinite
   loops when the effect sets state.
2. **IMPLEMENT** a data fetch effect that handles: loading
   state, error state, cancellation when the component
   unmounts, and re-fetching when the `id` prop changes.
3. **DEBUG** a component showing stale data when a prop
   changes, identify the missing dependency, and apply
   the fix. Explain why adding the dep can expose new
   bugs (object reference instability).
4. **EXPLAIN** why React 18 Strict Mode runs effects twice
   and how to write effects that are safe under this
   double-invocation. Give an example of an effect that
   breaks and the fix.
5. **DISTINGUISH** between `useEffect` and `useLayoutEffect`
   - explain the paint timing difference and give a
   scenario where `useLayoutEffect` is required.

---

### 🧠 Think About This Before We Continue

**Q1.** The `exhaustive-deps` linter rule requires every
value used inside an effect to be in the dependency array.
But sometimes adding a dependency causes unwanted
re-runs (e.g., a callback function that is recreated on
every render). The temptation is to suppress the lint
rule with `// eslint-disable-next-line`. Instead of
suppressing, what are the correct tools to stabilise
a function reference so it can safely be in the deps
array?

**Q2.** `useEffect` runs asynchronously after the browser
paints. If an effect measures a DOM element's dimensions
with `getBoundingClientRect()` and updates state based
on the measurement, the user will see: (1) initial render,
(2) paint, (3) effect reads dimensions, (4) state update,
(5) re-render, (6) repaint with corrected layout. This
is visible as a flash. What hook solves this, and what
is the performance cost of using it?

**Q3.** React Query and SWR are data-fetching libraries
that abstract the `useEffect` + `useState` fetch pattern.
They handle: caching, background refetch, stale-while-
revalidate, cancellation, deduplication (two components
requesting the same URL share one fetch). At what scale
of application does the complexity of manually written
fetch effects justify adopting one of these libraries?
What do you lose by adopting them?