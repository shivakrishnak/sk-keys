---
id: RCT-013
title: Event Handling in React
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-008, RCT-009, RCT-010
used_by: RCT-025, RCT-026, RCT-036
related: RCT-009, RCT-010, RCT-025
tags:
  - react
  - frontend
  - events
  - user-interaction
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /react/event-handling-in-react/
---

# RCT-013 - EVENT HANDLING IN REACT

⚡ TL;DR - React events are synthetic wrappers over native
DOM events, attached as camelCase JSX props; understanding
the differences from native events - no inline strings, no
parentheses, preventDefault works differently - prevents
common early mistakes.

| #013            | Category: React                                             | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Component, JSX, Props, State                                |                 |
| **Used by:**    | Controlled vs Uncontrolled, Form Handling, useCallback Hook |                 |
| **Related:**    | Props, State, Controlled vs Uncontrolled Components         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In vanilla JavaScript, attaching a click handler means
using `addEventListener` imperatively after the DOM element
exists. In React, this would require a `useRef` to access
the DOM element, a `useEffect` to attach the listener, and
another `useEffect` cleanup to remove it. This is verbose,
error-prone, and defeats the purpose of the declarative model.

React's event system solves this by making event handlers
declarative: you specify `onClick={handleClick}` in JSX,
and React manages the attachment and cleanup automatically.
When the component unmounts, React removes the handler.
When the handler changes, React updates it.

---

### 📘 Textbook Definition

React's **event handling** system uses **synthetic events**:
cross-browser wrapper objects around native DOM events that
normalise browser inconsistencies. Event handlers are
attached as JSX properties using camelCase names (`onClick`,
`onChange`, `onSubmit`) and receive a `SyntheticEvent`
object as their argument. React uses event delegation:
a single listener at the root container dispatches all
events to the correct component handler, rather than
attaching individual listeners to each DOM element.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event handlers in React are JSX props (`onClick={fn}`) that
receive a synthetic event object; the key differences from
HTML are camelCase names, function references (not strings),
and that `preventDefault()` works normally.

**One analogy:**

> React event handling is like an airline's centralised
> check-in system. All passengers (events) go through one
> central desk (root container listener). The desk looks up
> each passenger's seat (component position in tree) and
> routes them to the correct handler. Individual gates
> (DOM elements) do not have their own check-in desks.
> This is more efficient than each gate handling its own
> check-in.

**One insight:**
The most common mistakes for developers coming from HTML:
(1) writing `onclick="handleClick()"` (string, lowercase,
with parentheses) instead of `onClick={handleClick}` (prop,
camelCase, no parentheses); (2) calling `return false`
to prevent default (does not work in React - must call
`e.preventDefault()`).

---

### 🔩 First Principles Explanation

**KEY DIFFERENCES FROM HTML EVENTS:**

| HTML                              | React                       |
| --------------------------------- | --------------------------- |
| `onclick="handleClick()"`         | `onClick={handleClick}`     |
| lowercase                         | camelCase                   |
| string value                      | function reference          |
| `return false` to prevent default | `e.preventDefault()`        |
| Attaches to DOM element           | Delegated to root container |

**WHY FUNCTION REFERENCE, NOT CALL:**

```jsx
// WRONG: calls handleClick immediately during render
<button onClick={handleClick()}>Click</button>
// onClick receives the RETURN VALUE of handleClick()
// (undefined in most cases), not the function itself
// The click does nothing

// CORRECT: passes handleClick as the handler
<button onClick={handleClick}>Click</button>
// onClick receives the handleClick function
// React calls it when the button is clicked

// CORRECT: inline arrow function for arguments
<button onClick={() => handleClick(item.id)}>Delete</button>
// Creates a new function that calls handleClick with args
// Slightly less optimal (new function per render) but correct
```

**SYNTHETIC EVENTS:**
React's `SyntheticEvent` wraps the native event for
cross-browser normalisation. It has the same interface
as native events (`stopPropagation`, `preventDefault`,
`target`, `currentTarget`). The native event is accessible
via `e.nativeEvent` if needed for browser-specific APIs.

---

### 🧪 Thought Experiment

**SETUP:**
A dropdown menu that opens on click and should close
when clicking anywhere outside it.

**THE OUTSIDE-CLICK PATTERN:**

```jsx
function Dropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleOutsideClick(event) {
      // If click is outside our dropdown, close it
      if (ref.current && !ref.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    // Add to document for outside-click detection
    document.addEventListener("click", handleOutsideClick);
    return () => {
      document.removeEventListener("click", handleOutsideClick);
    };
  }, []);

  return (
    <div ref={ref}>
      <button onClick={() => setIsOpen((o) => !o)}>Menu</button>
      {isOpen && <ul>...</ul>}
    </div>
  );
}
```

This is the pattern where React's synthetic event system
and native DOM events interact. The dropdown's toggle uses
React's `onClick` (synthetic). The outside-click detection
requires a native `document` listener (because it needs
to intercept clicks on elements outside the React tree).

---

### 🧠 Mental Model / Analogy

> React event handling has two layers: the component layer
> (your `onClick` props, synthetic events) and the system
> layer (React's root listener, delegation). As a developer,
> you interact only with the component layer. The system
> layer is automatic. Understanding that the system layer
> exists explains why `stopPropagation()` in a React
> component stops propagation in the React component tree
> but the native event has already reached the root listener.

```
User clicks a button
  |
  v
Native DOM event fires on button element
  |
  v (bubbles up DOM tree)
  |
  v
Reaches React root container (#root)
  |
  v
React's single listener intercepts it
  |
  v
React maps to component tree position
  |
  v
Dispatches SyntheticEvent to onClick handler
  |
  v (your handler runs)
  |
  v (if not stopped, bubbles up React tree)
  |
  v (parent onClick handlers)
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
In React, you handle user interactions by adding event
props to JSX: `onClick`, `onChange`, `onSubmit`. These work
like HTML event attributes but use JavaScript functions
instead of strings, and camelCase instead of lowercase.

**Level 2 - How to use it (junior developer):**
Write `<button onClick={handleClick}>`. Your `handleClick`
function receives an event object as its first argument.
Call `event.preventDefault()` to stop default behaviour
(form submit page reload, link navigation). Never pass the
function with parentheses: `onClick={handleClick}` not
`onClick={handleClick()}`.

**Level 3 - How it works (mid-level engineer):**
React attaches one listener to the root container.
When a native DOM event fires, it bubbles to the root.
React looks up the component tree position of the target
and dispatches a SyntheticEvent to the correct handler.
SyntheticEvent normalises browser differences in event
properties. React batches state updates triggered by
event handlers (all updates in one render).

**Level 4 - Why it was designed this way (senior/staff):**
Event delegation (one listener at root instead of one per
element) reduces memory usage and avoids memory leaks from
forgotten `removeEventListener` calls. Synthetic events
ensure consistent behaviour across browsers. The declarative
`onClick={fn}` in JSX is superior to the imperative
`addEventListener` because it is automatically removed
when the component unmounts and automatically updated
when the function reference changes.

**Level 5 - Mastery (distinguished engineer):**
React's event system has performance implications at scale.
`onClick={() => handleClick(id)}` creates a new function
object on every render for every list item. For a 10,000-item
list, this is 10,000 new functions per render. Solutions:
`useCallback` to stabilise the reference (combined with
`React.memo` on the item component), or event delegation
at the list container level (listening on the container,
reading `event.target` to find which item was clicked -
bypassing React's event system entirely for this case).

---

### ⚙️ How It Works (Mechanism)

**Common event props:**

```
onClick         - mouse click, keyboard enter/space on interactive elements
onChange        - value change in inputs/selects (fires on every keystroke)
onSubmit        - form submission (attach to <form>, not submit button)
onFocus         - element receives focus
onBlur          - element loses focus
onKeyDown       - key pressed (check event.key)
onKeyUp         - key released
onMouseEnter    - mouse enters element (does not bubble)
onMouseLeave    - mouse leaves element (does not bubble)
onScroll        - scrollable element scrolled
onInput         - text input received (similar to onChange)
```

**Event handler patterns:**

```jsx
// Pattern 1: Named handler function
function handleSave(event) {
  event.preventDefault();
  saveData();
}
<button onClick={handleSave}>Save</button>

// Pattern 2: Inline arrow with arguments
<button onClick={() => handleDelete(item.id)}>
  Delete
</button>

// Pattern 3: Arrow function with event + arguments
<input
  onChange={event => updateField('name', event.target.value)}
/>

// Pattern 4: Prevent default (form)
<form onSubmit={event => {
  event.preventDefault();
  submitForm(data);
}}>
  ...
</form>
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FORM SUBMIT EVENT FLOW:**

```
1. User clicks submit button (or presses Enter in input)
2. Browser creates native 'submit' event on the form
3. Event bubbles up to React's root listener
4. React creates SyntheticEvent wrapping native event
5. React dispatches to form's onSubmit handler
6. Your handler: event.preventDefault() (stops page reload)
7. Your handler: calls API with form data
8. Your handler: setState to show loading state
9. React batches setState, schedules re-render
10. Re-render shows loading spinner
11. API responds, setState to success/error
12. Re-render shows result
```

---

### 💻 Code Example

**Example 1 - BAD: HTML-style event handling in React:**

```jsx
// BAD: Multiple HTML-style mistakes
function LoginForm() {
  return (
    <form>
      {/* Wrong: lowercase, string value, parentheses */}
      <button onclick="handleLogin()">Login</button>

      {/* Wrong: return false doesn't work in React */}
      <a href="/about" onclick="return false">
        About
      </a>
    </form>
  );
}
// Result:
// - onclick is ignored (not a React prop, lowercase)
// - 'handleLogin is not defined' error in the console
// - The link navigates normally (return false does nothing)
```

**Example 2 - GOOD: Correct React event handling:**

```jsx
// GOOD: React-idiomatic event handling
function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault(); // correct way to prevent default
    loginUser({ email, password });
  };

  return (
    <form onSubmit={handleSubmit}>
      {" "}
      {/* on <form> not <button> */}
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

**Example 3 - PRODUCTION: TypeScript-typed event handlers:**

```tsx
function FileUploader({
  onUpload,
  onError,
}: {
  onUpload: (file: File) => void;
  onError: (message: string) => void;
}) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      // 5MB limit
      onError("File too large. Maximum size is 5MB.");
      return;
    }
    onUpload(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault(); // prevent browser file open
    const file = event.dataTransfer.files[0];
    if (file) onUpload(file);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault(); // required for drop to fire
  };

  return (
    <div onDrop={handleDrop} onDragOver={handleDragOver}>
      <input type="file" onChange={handleChange} />
    </div>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`onClick={handleClick()}` passes the handler"                     | This CALLS `handleClick` during render and passes its return value (usually `undefined`) as the prop. Write `onClick={handleClick}` (no parentheses) to pass the function itself.                                                                               |
| "`stopPropagation` stops all event processing"                     | `stopPropagation` stops the event from bubbling further up the React component tree. The native DOM event has already reached React's root listener. It does NOT prevent the event from reaching document-level native listeners added with `addEventListener`. |
| "onChange is the same as native input's 'change' event"            | React's `onChange` fires on every keystroke (like native 'input' event). Native 'change' fires only on blur/when the value is committed. React normalised this for predictable controlled input behaviour.                                                      |
| "You need to call event.persist() to use the event asynchronously" | React removed the event pooling system in React 17. `event.persist()` is now a no-op. You can safely use event properties in async callbacks in React 17+.                                                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**Calling Handler Instead of Passing It**

**Symptom:**
Handler runs on every render, not on click. Or the button
appears to do nothing. Or there is an error about the
handler returning a value that is not a function.

**Root Cause:**
`onClick={handleClick()}` - function is called during render
(parentheses execute it).

**Diagnostic Command:**

```bash
# Put a console.log at the top of the handler function.
# If it logs on page load (not on button click),
# the function is being called during render, not on click.
# Check JSX: onClick={handler} not onClick={handler()}
```

**Fix:**
Remove the parentheses: `onClick={handleClick}`.
For passing arguments: `onClick={() => handleClick(id)}`.

---

**Security: Event Handler Injection via Props**

**Symptom:**
A component accepts an event handler via props without
validation, and the caller passes a handler that performs
dangerous operations (navigation to external URL, form
submission to wrong endpoint).

**Root Cause:**
Event handler props (`onClick`, `onSubmit`) can do anything
the caller provides. Without validation, a compromised or
malicious caller can inject unexpected behaviour.

**Prevention:**
Validate callback props in your component's TypeScript
interface. For security-sensitive actions (payments,
deletions), do not accept raw handlers as props - handle
the action internally and only call a notification callback
on completion.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Component` and `JSX` - event handlers are JSX props
- `Props` - event handlers are a specific type of prop
  (function props / callbacks)
- `State` - event handlers typically call state setters

**Builds On This (learn these next):**

- `Controlled vs Uncontrolled Components` - how `onChange`
  is used to make form inputs controlled
- `Form Handling in React` - applying event handlers to forms
- `useCallback Hook` - memoising event handlers in optimised
  component trees

**Alternatives / Comparisons:**

- `Native addEventListener` - the imperative alternative;
  required for events outside React's tree (document-level
  outside-click detection, window resize)
- `React Hook Form's register` - abstraction over individual
  onChange/onBlur handlers for form field management

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Declarative JSX event props (onClick,   │
│              │ onChange, onSubmit) wrapping native DOM  │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULES    │ camelCase props (onClick not onclick)   │
│              │ function reference (not string/call)    │
│              │ e.preventDefault() (not return false)   │
├──────────────┼───────────────────────────────────────────┤
│ ARGS         │ () => fn(id) for passing arguments      │
│              │ fn for simple handlers (no args needed) │
├──────────────┼───────────────────────────────────────────┤
│ FORM TIP     │ onSubmit on <form>, not on <button>     │
│              │ event.preventDefault() prevents reload  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ onClick={handler()} (calls on render)   │
│              │ onclick="handler()" (HTML string style) │
├──────────────┼───────────────────────────────────────────┤
│ TYPED        │ React.MouseEvent<HTMLButtonElement>     │
│              │ React.ChangeEvent<HTMLInputElement>     │
│              │ React.FormEvent<HTMLFormElement>        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "onClick={fn}, not onClick='fn()';      │
│              │  e.preventDefault(), not return false." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Controlled Components -> Form Handling  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Event props are camelCase function references:
   `onClick={handleClick}` not `onclick="handleClick()"`.
   No parentheses - parentheses call the function during
   render, not during the click.
2. `event.preventDefault()` is required to prevent default
   browser behaviour (form page reload, link navigation).
   `return false` does not work in React.
3. `onSubmit` goes on the `<form>` element, not the submit
   button. This ensures keyboard form submission (Enter key)
   also triggers your handler.

**Interview one-liner:**
"React event handlers are JSX props using camelCase names
(onClick, onChange, onSubmit). They receive synthetic event
objects that wrap native DOM events for cross-browser
consistency. Key differences from HTML: function references
not strings (no parentheses), camelCase not lowercase,
e.preventDefault() not return false. React uses event
delegation - a single listener at the root container handles
all events rather than attaching to individual DOM elements."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Event delegation (one listener at a common ancestor,
routing events by target) is more scalable than one
listener per element. This pattern appears in React's
root listener, jQuery's `.on()` method for dynamic
elements, and microservices routing (one API gateway
routes requests to services based on path).

---

### 💡 The Surprising Truth

React's `onChange` for text inputs does not match the native
DOM `change` event. The native `change` event fires when
the input loses focus after the value changed. React's
`onChange` fires on every keystroke (like the native
`input` event). React made this decision deliberately to
make controlled inputs work naturally - if `onChange` fired
only on blur, you could not update state on every keystroke,
which would break controlled input behaviour. This means
if you need the "fires only on blur" behaviour in React
(e.g., for validation that should not trigger while the
user is typing), you must use `onBlur`, not `onChange`.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** Why `onClick={handleClick()}` is a bug,
   what it does instead of what was intended, and the fix.
2. **IMPLEMENT** A keyboard shortcut handler that listens
   for Ctrl+S on the `window` object, correctly cleaning
   up the listener on unmount, and explain why this requires
   native `addEventListener` rather than React's event props.
3. **DEBUG** Given a form that reloads the page on submit,
   diagnose whether `event.preventDefault()` was missed,
   is being called too late, or the `onSubmit` is on the
   wrong element.
4. **OPTIMISE** Given a list of 500 items each with an
   onClick that passes the item's ID, explain two strategies
   to prevent creating 500 new function objects on every
   render, and when each is appropriate.
5. **TYPE** Write TypeScript-typed handlers for `onChange`
   on an input, `onSubmit` on a form, and `onDrop` on a
   drag-drop zone, naming the correct `React.*Event<*>` type
   for each.

---

### 🧠 Think About This Before We Continue

**Q1.** React's `onChange` on inputs fires on every
keystroke, making controlled inputs responsive. But for a
search input that triggers an API call, you do not want
to make an API call on every keystroke. What pattern solves
this, and does it require React's event system or native
DOM events?
_Hint: Debouncing; `setTimeout`/`clearTimeout` in the
onChange handler._

**Q2.** A component renders a button: `<button onClick={
() => someExpensiveOperation(item.id) }>`. For each of 1000
list items, this creates a new arrow function per render.
`useCallback` is often suggested as a fix. But `useCallback`
requires a dependency array. If `item.id` is in the
dependency array, does `useCallback` actually help here?
When does `useCallback` for event handlers actually provide
a performance benefit?
_Hint: useCallback helps when combined with React.memo on
the child - the child skips re-render if the callback ref
is stable._

**Q3.** React's synthetic event system normalises browser
differences. One historical normalisation was event pooling:
React reused SyntheticEvent objects by resetting them after
the handler returned (for performance). `event.persist()`
was required to retain the event in async callbacks.
React 17 removed event pooling entirely. What does this
removal tell you about React's performance philosophy:
is memory pooling worth the developer experience cost?
_Hint: Modern JS engines have efficient GC for short-lived
objects._
