---
id: RCT-023
title: useRef Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-007, RCT-010, RCT-020, RCT-021
used_by: RCT-025, RCT-043, RCT-056
related: RCT-020, RCT-021, RCT-017
tags:
  - react
  - frontend
  - hooks
  - dom
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /react/useref-hook/
---

# RCT-023 - USEREF HOOK

⚡ TL;DR - `useRef` returns a mutable `.current` container
that persists across renders without triggering re-renders;
it has two main uses: accessing DOM elements directly (for
focus, scroll, canvas, third-party libraries) and storing
mutable values that should not cause re-renders (previous
value, interval IDs, flags).

| #023 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Component, State, useState Hook, useEffect Hook | |
| **Used by:** | Custom Hooks, Stale Closure Anti-Pattern, React Fiber Architecture | |
| **Related:** | useState Hook, useEffect Hook, Direct DOM Mutation Anti-Pattern | |

---

### 🔥 The Problem This Solves

**TWO DIFFERENT PROBLEMS, ONE HOOK:**

**Problem 1 - DOM access:**
React manages the DOM. There is no variable in your
component code that holds the DOM element React rendered.
For browser API calls that need the real element (focus,
scroll, getBoundingClientRect, canvas context, video play/
pause), you need a reference to the actual DOM node.
`useRef` provides this via the `ref` JSX prop.

**Problem 2 - Mutable values without re-render:**
`useState` triggers a re-render when updated - that is its
purpose. But some values should persist across renders
without causing re-renders: the timer ID from
`setInterval` (needed for cleanup), a flag to prevent
double-submission, the previous render's value for
comparison. Storing these in `useState` would cause
unnecessary re-renders. Storing them in a plain variable
would reset on every render. `useRef` provides mutable
persistence without re-render.

---

### 📘 Textbook Definition

`useRef(initialValue)` returns a ref object `{ current: initialValue }`.
The `.current` property is mutable. The ref object persists
for the full lifetime of the component (same object across
all renders). Modifying `.current` does NOT trigger a
re-render. This distinguishes `useRef` from `useState`.

When a `ref` JSX prop is set on a DOM element, React
sets `.current` to the DOM node after mounting and clears
it to `null` on unmount.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`useRef` is a box (`{ current: value }`) that persists
across renders and can hold either a DOM element
or any mutable value, without triggering re-renders.

**Two uses:**

```jsx
// Use 1: DOM element access
const inputRef = useRef(null);
<input ref={inputRef} />
// inputRef.current → the DOM <input> element

// Use 2: Mutable value that persists (no re-render)
const timerRef = useRef(null);
timerRef.current = setInterval(fn, 1000);
// timerRef.current → timer ID, persists across renders
// changing .current does NOT cause a re-render
```

---

### 🔩 First Principles Explanation

**WHY NOT useState FOR MUTABLE VALUES:**

```
Scenario: store a timer ID so we can cancel it.

// WRONG: useState causes re-render when ID changes
const [timerId, setTimerId] = useState(null);
const startTimer = () => {
  const id = setInterval(fn, 1000);
  setTimerId(id);  // triggers re-render (unnecessary)
};

// RIGHT: useRef persists without re-render
const timerRef = useRef(null);
const startTimer = () => {
  timerRef.current = setInterval(fn, 1000);
  // no re-render, value persists
};
const stopTimer = () => {
  clearInterval(timerRef.current);
  timerRef.current = null;
};
```

**WHY NOT A PLAIN VARIABLE:**

```
// WRONG: plain variable resets on every render
function Counter() {
  let timerId = null;           // reset to null every render

  const start = () => {
    timerId = setInterval(fn, 1000);  // stored locally
  };
  const stop = () => {
    clearInterval(timerId);    // timerId is null (reset on render)
    // stop does not work
  };
}

// RIGHT: useRef persists the value between renders
function Counter() {
  const timerRef = useRef(null);  // same object every render

  const start = () => {
    timerRef.current = setInterval(fn, 1000);
  };
  const stop = () => {
    clearInterval(timerRef.current);  // correct timer ID
    timerRef.current = null;
  };
}
```

---

### 🧪 Thought Experiment

**PREVIOUS VALUE PATTERN:**
A component needs to show "changed from X to Y". It needs
to know both the current value (from useState) and the
previous render's value. `useRef` captures the previous
value without triggering extra renders:

```jsx
function PriceDisplay({ price }) {
  const prevPriceRef = useRef(price);

  useEffect(() => {
    prevPriceRef.current = price;  // store for next render
  });  // no deps: runs after every render

  const prevPrice = prevPriceRef.current;
  const changed = price !== prevPrice;

  return (
    <div>
      <span>${price}</span>
      {changed && (
        <span className="change">
          (was ${prevPrice})
        </span>
      )}
    </div>
  );
}
```

---

### 🧠 Mental Model / Analogy

> `useRef` is a sticky note on the refrigerator. The
> refrigerator (component) is replaced every time someone
> cooks (renders). But the sticky note stays on the
> refrigerator - it is not lost when the refrigerator
> is used (re-rendered). You can read and update the
> sticky note without cooking a new meal (no re-render).
> And you can attach the sticky note to a specific drawer
> (DOM element via `ref` prop) so it always refers to
> that exact drawer.

```
render 1: useRef(null) → creates { current: null }
                         (the "sticky note holder")
              ↓ ref={inputRef}
          React sets inputRef.current = <input DOM node>

render 2: same ref object returned
          inputRef.current still = <input DOM node>
          (sticky note persists on the same element)

unmount:  React sets inputRef.current = null
          (sticky note removed)
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
`useRef` stores a value that persists between renders
without causing re-renders. Also used to hold a reference
to a DOM element.

**Level 2 (usage):**
`const ref = useRef(null)`. Attach to DOM with `<el ref={ref}>`.
Access DOM as `ref.current`. For mutable storage (timer IDs,
flags), write `ref.current = value` directly.

**Level 3 (mechanism):**
React stores refs in the Fiber node alongside hook state.
Unlike state, ref updates are synchronous and do not
schedule a re-render. The ref object identity is stable
(same object every render), which makes refs safe to use
as `useEffect` dependencies (they do not trigger re-runs
from object reference changes).

**Level 4 (patterns):**
Callback refs (using a function instead of a ref object)
let you run code when the ref attaches/detaches. This is
useful for measuring elements that conditionally render.
`useImperativeHandle` combined with `forwardRef` lets
parent components call methods on child DOM elements or
custom component instances - used for design system
components that expose focus(), scrollTo(), etc.

**Level 5 (mastery):**
`useRef` is often used to break out of stale closures in
effects: instead of adding a callback to the effect's
deps (which would cause re-runs), store the latest version
in a ref and call the ref from inside the effect. This is
the "event handler in ref" pattern used in libraries like
React Hot Toast and React Beautiful DnD. It is a
performance optimisation for stable subscriptions.

---

### ⚙️ How It Works (Mechanism)

**DOM element access:**

```jsx
function TextInput() {
  const inputRef = useRef(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  const selectAll = () => {
    inputRef.current?.select();
  };

  return (
    <div>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus</button>
      <button onClick={selectAll}>Select All</button>
    </div>
  );
}
```

**Mutable instance variable (timer cleanup):**

```jsx
function AutoSave({ content, onSave }) {
  const timerRef = useRef(null);

  useEffect(() => {
    // Debounce: cancel previous timer, start new one
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      onSave(content);
    }, 1000);

    return () => clearTimeout(timerRef.current);
  }, [content, onSave]);

  return null; // this component is purely behavioural
}
```

**Previous value tracking:**

```jsx
function usePrevious(value) {
  const ref = useRef(value);
  useEffect(() => {
    ref.current = value;
  });  // runs after every render, updates after read
  return ref.current;  // returns value from PREVIOUS render
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
1. Component renders with ref={inputRef}
2. React commits DOM: sets inputRef.current = <input el>
3. User clicks "Focus" button
4. focusInput(): inputRef.current.focus()
5. Browser moves cursor to input
   (React is not involved in this DOM API call)
6. Component re-renders (from other state change)
7. inputRef.current is still the SAME <input> DOM node
   (React did not replace the input element since nothing
    in its props changed)
8. focus() call in any re-render still works correctly
```

---

### 💻 Code Example

**BAD: Trying to access ref in render (before mount):**

```jsx
// BAD: ref is null during render (not yet set by React)
function TextInput() {
  const inputRef = useRef(null);

  // WRONG: accessed during render, before React sets .current
  console.log(inputRef.current);  // null
  const length = inputRef.current?.value.length ?? 0;
  // Length is always 0/undefined during render

  return (
    <>
      <input ref={inputRef} />
      <span>Length: {length}</span>  // always 0
    </>
  );
}
```

**GOOD: Ref access in event handler or effect (after mount):**

```jsx
// GOOD: access ref in event handler or useEffect
function TextInput() {
  const inputRef = useRef(null);
  const [length, setLength] = useState(0);

  // Read from DOM in event handler (after mount, safe)
  const handleChange = () => {
    setLength(inputRef.current?.value.length ?? 0);
  };

  return (
    <>
      <input ref={inputRef} onChange={handleChange} />
      <span>Length: {length}</span>
    </>
  );
}
```

**PRODUCTION: Video player with imperative controls:**

```jsx
function VideoPlayer({ src, onEnd }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const play = () => {
    videoRef.current?.play();
    setIsPlaying(true);
  };

  const pause = () => {
    videoRef.current?.pause();
    setIsPlaying(false);
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleEnded = () => {
      setIsPlaying(false);
      onEnd?.();
    };

    video.addEventListener('ended', handleEnded);
    return () => video.removeEventListener('ended', handleEnded);
  }, [onEnd]);

  return (
    <div>
      <video ref={videoRef} src={src} />
      <button onClick={isPlaying ? pause : play}>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
    </div>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Changing `ref.current` updates the UI" | `ref.current` is mutable but NEVER triggers a re-render. If you change `ref.current` and expect the UI to update, use `useState` instead. Refs are for values that need persistence without triggering renders. |
| "ref.current is available during the first render" | For DOM refs, `.current` is `null` during the first render. React sets it after the DOM is committed. Access refs only in event handlers or `useEffect`. |
| "useRef is only for DOM elements" | `useRef` is equally valid for any mutable value that should persist across renders without causing re-renders: timer IDs, interval IDs, previous values, form submission flags, canvas contexts, WebSocket connections. |
| "`ref` on a custom component gives the component instance" | For function components, `ref` does NOT give the component instance (function components have no instance). You must use `forwardRef` to forward the ref to a specific DOM element inside the component. |

---

### 🚨 Failure Modes & Diagnosis

**ref.current is null in useEffect**

**Symptom:** `ref.current` is null inside a `useEffect`
despite being attached to a DOM element.

**Root Cause:** The DOM element is conditionally rendered
and the condition is false when the effect runs. Or the
ref is attached to a component instead of a DOM element
(without `forwardRef`).

**Diagnostic:**
```jsx
useEffect(() => {
  console.log('ref value:', ref.current);
  // If null: element is not in DOM at this time
}, []);
```

**Fix:** Ensure the element is rendered when the effect
runs. Use optional chaining: `ref.current?.focus()`.

---

**Stale Ref Pattern for Event Handlers in Effects**

**Symptom:** An event handler inside `useEffect` reads
stale state values because it is captured in a closure
from the first render.

**Fix (useRef for latest handler):**
```jsx
const handlerRef = useRef(null);
handlerRef.current = handleKeyPress; // always latest

useEffect(() => {
  const handler = (e) => handlerRef.current(e);
  window.addEventListener('keydown', handler);
  return () => window.removeEventListener('keydown', handler);
}, []); // stable effect, no re-subscribe on every render
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Component lifecycle` - refs map to DOM lifecycle
- `useState Hook` - the alternative when re-render is needed
- `useEffect Hook` - common partner for ref-based DOM ops

**Builds On:**
- `Custom Hooks` - `usePrevious`, `useDebounce`, and others
  use `useRef` internally
- `Direct DOM Mutation Anti-Pattern` - useRef is the safe
  escape hatch for legitimate DOM operations

**Related APIs:**
- `forwardRef` - pass ref through component boundaries
- `useImperativeHandle` - customise what the ref exposes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DECLARE  │ const ref = useRef(initialValue)            │
│ DOM REF  │ <input ref={ref} />                         │
│          │ ref.current = DOM element (after mount)     │
│ MUTABLE  │ ref.current = someValue  (no re-render)     │
├──────────────────────────────────────────────────────────┤
│ USE FOR  │ DOM: focus, scroll, canvas, video, measure  │
│ DOM OPS  │ Mutable: timer IDs, flags, prev values      │
├──────────────────────────────────────────────────────────┤
│ NOT FOR  │ Values that should cause re-renders         │
│          │ (use useState instead)                      │
├──────────────────────────────────────────────────────────┤
│ TIMING   │ ref.current = null during first render      │
│          │ Set by React after DOM commit               │
│          │ Read in event handlers or useEffect         │
├──────────────────────────────────────────────────────────┤
│ FORWARD  │ forwardRef + useImperativeHandle for        │
│          │ exposing ref through components             │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `useRef` returns `{ current: value }`. Mutating
   `.current` never triggers re-renders. Use it for
   DOM access (`ref={myRef}`) or mutable instance values.
2. `ref.current` is `null` during render - React sets it
   after the DOM commits. Access refs in event handlers
   or `useEffect`.
3. `useRef` vs `useState`: if changing the value should
   update the UI, use `useState`. If you just need to
   store it for later use, use `useRef`.

**Interview one-liner:**
"`useRef` returns a `{ current }` container that persists
across renders without triggering re-renders. It has two
uses: DOM element references (`ref={myRef}` on JSX, React
sets `.current` to the DOM node after mounting) and mutable
instance variables that should not cause re-renders (timer
IDs, flags, previous values). Key distinction from useState:
mutating `.current` never causes a re-render - if you need
the UI to update, use useState."

---

### 💎 Transferable Wisdom

`useRef` is React's implementation of an instance variable:
data attached to a specific object instance (component
instance) that persists for the object's lifetime and can
be mutated without reconstructing the object. This concept
appears in: OOP instance variables (`this.timerId`),
closure-captured mutable variables, C's statically-allocated
variables in functions, and Python's object attributes.
The pattern is universal: when you need "per-instance
persistent mutable state without triggering callbacks,"
you need a ref-like construct.

---

### 💡 The Surprising Truth

React DevTools cannot see `useRef` values in the same way
it sees `useState` values. If you inspect a component in
React DevTools, the hooks list shows `useRef` with its
`.current` value at the time of inspection - but unlike
`useState`, changes to `ref.current` do NOT appear as
changes in DevTools (because DevTools is notified via
React's re-render mechanism, and `useRef` mutations do not
trigger re-renders). This means `useRef` values are
effectively "invisible" to DevTools during live updates.
If you need to observe a value for debugging, temporarily
use `useState` instead, then switch back.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a component with an auto-focusing text
   input: the input focuses automatically on mount, and
   a "clear" button clears the value AND restores focus
   using a DOM ref.
2. **EXPLAIN** why `let timerId = null` declared inside
   a component function resets on every render, and why
   `useRef(null)` does not.
3. **IMPLEMENT** a `usePrevious` custom hook that returns
   the value from the previous render, using `useRef` and
   `useEffect`.
4. **DEBUG** a component where `ref.current` is always
   null inside a click handler - identify the cause
   (conditional rendering, wrong attachment) and apply
   the fix.
5. **EXPLAIN** the "stable callback ref" pattern: storing
   the latest version of an event handler in a ref so a
   `useEffect` with `[]` deps always calls the latest
   handler without re-subscribing.

---

### 🧠 Think About This Before We Continue

**Q1.** React's documentation says "ref.current acts as
a mutable instance variable for function components." But
class components have `this.x` as actual instance variables.
What happens to `useRef` values when the same component
renders twice in Strict Mode (React 18 development double-
invocation)? Do both invocations share the same ref
object, or do they get separate ones?

**Q2.** A parent component needs to call `focus()` on
an input inside a child component. The child renders
`<input ref={???} />`. The parent needs to pass a ref
in. What are the two approaches (direct `ref` prop,
`forwardRef`), when does each apply, and what happens
if you try to pass `ref` as a regular prop without
`forwardRef`?

**Q3.** `useRef` is often used for "the latest callback"
pattern to avoid stale closures in effects. Consider this
situation: a custom hook sets up a WebSocket connection
once (`useEffect` with `[]`) but the message handler
needs access to the latest state. Using `useRef` for the
handler means the WebSocket always calls the latest version.
But what are the trade-offs of this pattern vs adding the
state to the effect's deps (which causes WebSocket
reconnect on every state change)?