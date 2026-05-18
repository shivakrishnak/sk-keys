---
id: RCT-007
title: Component
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-003, RCT-004, RCT-006
used_by: RCT-009, RCT-010, RCT-012, RCT-013, RCT-014, RCT-015
related: RCT-004, RCT-009, RCT-047
tags:
  - react
  - frontend
  - core
  - foundational
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/react/component/
---

⚡ TL;DR - A React component is a JavaScript function that
accepts props and returns JSX; every piece of UI in a React
application is a component - get the rules and conventions
right here and everything else builds on this foundation.

| #007            | Category: React                                                                           | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Declarative UI vs Imperative DOM, The Component Mental Model, React Dev Environment Setup |                 |
| **Used by:**    | Props, State, ReactDOM Rendering, Event Handling, Conditional Rendering, List Rendering   |                 |
| **Related:**    | The Component Mental Model, Props, Class Components to Hooks Migration                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before components, UI code was written as a sequence of
operations on the global HTML document. Adding the same
"user card" to three pages meant copy-pasting the HTML and
the JavaScript event wiring three times. A bug in the user
card had to be fixed in three places.

Components are the solution: write the user card once, use
it anywhere. This is the foundational building block of React.
Before writing state, hooks, routing, or anything else, a
developer must know precisely what a component is, what it
can return, and what rules govern how it behaves.

---

### 📘 Textbook Definition

A **React component** is a JavaScript function (in modern
React: always a function, not a class) whose name begins with
a capital letter, that accepts a single object argument called
`props`, and that returns either a React element (JSX), an
array of React elements, a string, a number, `null`, or a
React Portal. React calls the component function during
rendering to determine what should appear in the DOM. A
component can optionally call **hooks** to maintain state
and perform side effects. By convention, each component
encapsulates a single, well-defined responsibility.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A component is a function named with a capital letter that
returns JSX.

**One analogy:**

> A component is like a custom HTML tag that you build
> yourself. `<button>` is a browser-built-in element.
> `<UserCard>` is a component you build. Both can appear
> in JSX. Both accept attributes (props). The difference:
> you define what `<UserCard>` looks like and does.

**One insight:**
The capital letter in a component's name is not a style
convention - it is the mechanism React uses to distinguish
custom components (`<UserCard>` - call the function) from
HTML elements (`<div>` - create a DOM node). Naming a
component with a lowercase letter is a silent bug that
produces incorrect output.

---

### 🔩 First Principles Explanation

**THE THREE RULES OF COMPONENTS:**

1. **Must be a function named with a capital letter**
   - `function UserCard() {}` - valid component
   - `function userCard() {}` - valid function, not a component

2. **Must return valid React output**
   - JSX: `return <div>Hello</div>;`
   - Array: `return [<a key="1"/>, <b key="2"/>];`
   - String/Number: `return "Loading...";`
   - null: `return null;` (renders nothing)
   - Fragment: `return <> ... </>;` (no wrapper DOM node)
   - Must NOT return: objects (other than the above)

3. **Must be pure for rendering**
   - Same props + same state = same output, always
   - No side effects during render (no fetch, no setTimeout,
     no direct DOM manipulation in the function body)
   - Side effects belong in `useEffect`, not in render

**THE DERIVED RULES:**
From rule 3 (purity): React may call your component function
multiple times (Concurrent React can interrupt and re-run
renders). If your component fetches data on every render,
it will trigger infinite loops. If it modifies DOM directly,
it will corrupt React's internal state.

---

### 🧪 Thought Experiment

**SETUP:**
You need a "Save" button used on three pages of your
application. It shows "Saving..." with a spinner when an
async save is in progress.

**WITHOUT COMPONENTS:**
Copy-paste a button HTML element, CSS class, and JS event
handler three times. When the designer changes the spinner,
update three files. When a QA engineer finds a bug in the
"Saving..." logic, fix it in three places.

**WITH COMPONENTS:**

```jsx
function SaveButton({ onSave, label = "Save" }) {
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    await onSave();
    setIsSaving(false);
  };

  return (
    <button onClick={handleSave} disabled={isSaving}>
      {isSaving ? "Saving..." : label}
    </button>
  );
}
```

Now use it on all three pages:

```jsx
<SaveButton onSave={saveProfile} />
<SaveButton onSave={saveSettings} label="Save Settings" />
<SaveButton onSave={saveDraft} label="Save Draft" />
```

One implementation. One bug fix location. One design change
to make. The component is the unit of reuse.

---

### 🧠 Mental Model / Analogy

> A component is a function. When React encounters `<UserCard
name="Alice" />` in JSX, it translates that to a function
> call: `UserCard({ name: "Alice" })`. The return value is
> either a React element (which eventually becomes a DOM node)
> or more components to call recursively.

```
<App />
  -> App({ })
     -> returns <UserList users={...} />
        -> UserList({ users: [...] })
           -> returns [<UserCard key="1" name="Alice" />,
                       <UserCard key="2" name="Bob"  />]
              -> UserCard({ name: "Alice" })
                 -> returns <div>Alice</div>
```

Every JSX tag is either a lowercase DOM element
(`<div>`, `<span>`) or an uppercase component function call
(`<UserCard>`, `<Button>`). React evaluates the tree top-down
until only DOM elements remain.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A component is a reusable piece of UI. Think of it as a
custom building block: you define it once (like designing
a LEGO brick) and place it anywhere in your app.

**Level 2 - How to use it (junior developer):**
Write a function starting with a capital letter. Return JSX.
Use it in other JSX as a tag. Pass data in via props. Use
`useState` for data that changes inside the component.
That is the complete specification for 80% of component usage.

**Level 3 - How it works (mid-level engineer):**
`<UserCard name="Alice" />` compiles to
`React.createElement(UserCard, { name: "Alice" })`. React
stores this element in its virtual DOM tree. When React needs
to render, it calls `UserCard({ name: "Alice" })`, gets back
a JSX tree of DOM elements, and reconciles it against the
previous render. Hooks allow state to persist between calls.

**Level 4 - Why it was designed this way (senior/staff):**
The function component model (vs classes) was chosen because:
(1) functions are easier to understand - no `this` binding,
no inheritance hierarchies; (2) logic sharing via custom hooks
is far more composable than lifecycle methods; (3) functions
align with the algebraic effects research that underlies
React's Concurrent mode, where rendering can be interrupted
and resumed. Class components are not removed but are not
recommended for new code.

**Level 5 - Mastery (distinguished engineer):**
A component is a closure with hooks. Every call to the
component function creates a new closure scope. Hooks use
a linked list internally to associate persistent state with
each component instance. Understanding this explains why
hooks must be called in the same order (the linked list
relies on order), why closures in useEffect can be stale
(they capture the scope from a previous render), and why
React 18's Concurrent mode can pause rendering (it can
discard a partial render attempt and restart from the
last committed state).

---

### ⚙️ How It Works (Mechanism)

**JSX to JavaScript compilation:**

```jsx
// What you write (JSX):
function Welcome({ name }) {
  return <h1>Hello, {name}!</h1>;
}

// What the TypeScript/Babel compiler produces:
function Welcome({ name }) {
  return React.createElement("h1", null, "Hello, ", name, "!");
}
// React.createElement(type, props, ...children)
// -> returns a plain JS object (React element):
// { type: 'h1', props: { children: ['Hello, ', name] } }
```

**Component identity and reconciliation:**

```
First render:
  <App>
    <UserCard name="Alice" />  <- position 0
    <UserCard name="Bob" />    <- position 1

Second render (Bob removed):
  <App>
    <UserCard name="Alice" />  <- position 0 (same)
    {/* nothing at position 1 */}

React sees position 0: same type (UserCard), update props
React sees position 1: was UserCard, now empty -> UNMOUNT
```

React uses **position** in the component tree as the default
identity mechanism. Two components at different positions are
always different instances, even if same type.

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPONENT LIFECYCLE:**

```
┌────────────────────────────────────────────────────────┐
│ MOUNT (first render)                                  │
│   1. Parent renders <UserCard name="Alice" />         │
│   2. React calls UserCard({ name: "Alice" })          │
│   3. Returns JSX: <div>Alice</div>                    │
│   4. React creates real DOM node                      │
│   5. useEffect callbacks run (after DOM paint)        │
├────────────────────────────────────────────────────────┤
│ UPDATE (state or prop change)                         │
│   1. setName("Bob") triggers re-render                │
│   2. React calls UserCard({ name: "Bob" })            │
│   3. Returns new JSX: <div>Bob</div>                  │
│   4. React diffs: text changed -> update DOM node     │
│   5. useEffect cleanup + re-run (if deps changed)     │
├────────────────────────────────────────────────────────┤
│ UNMOUNT (component removed from tree)                 │
│   1. Parent no longer renders <UserCard />            │
│   2. useEffect cleanup callbacks run                  │
│   3. React removes DOM nodes                          │
│   4. State is discarded (garbage collected)           │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - BAD: Lowercase component name:**

```jsx
// BAD: lowercase name - React treats as DOM element
function userCard({ name }) {
  return <div>{name}</div>;
}

// Usage in JSX:
// <userCard name="Alice" />
// React creates: <usercard name="Alice"> in the real DOM
// userCard function is NEVER called
// No error thrown - silent incorrect behaviour
```

**Example 2 - GOOD: Correct component definition:**

```jsx
// GOOD: capital letter, clear props interface
function UserCard({ name, email, avatarUrl }) {
  return (
    <div className="user-card">
      <img src={avatarUrl} alt={`${name}'s avatar`} />
      <h2>{name}</h2>
      <p>{email}</p>
    </div>
  );
}

// Usage:
// <UserCard name="Alice" email="alice@co.com"
//           avatarUrl="/avatars/alice.jpg" />
```

**Example 3 - PRODUCTION: Component with TypeScript, defaults,
and loading state:**

```tsx
interface UserCardProps {
  name: string;
  email: string;
  avatarUrl?: string;
  isLoading?: boolean;
}

function UserCard({
  name,
  email,
  avatarUrl = "/avatars/default.jpg",
  isLoading = false,
}: UserCardProps) {
  if (isLoading) {
    return <div className="user-card user-card--skeleton" />;
  }

  return (
    <div className="user-card">
      <img src={avatarUrl} alt={`${name}'s avatar`} width={48} height={48} />
      <h2 className="user-card__name">{name}</h2>
      <p className="user-card__email">{email}</p>
    </div>
  );
}

export default UserCard;
```

**How to test / verify correctness:**

```tsx
// React Testing Library: test from user perspective
import { render, screen } from "@testing-library/react";

test("renders user name and email", () => {
  render(<UserCard name="Alice" email="alice@co.com" />);
  expect(screen.getByRole("heading")).toHaveTextContent("Alice");
  expect(screen.getByText("alice@co.com")).toBeInTheDocument();
});

test("renders skeleton when loading", () => {
  render(<UserCard name="Alice" email="" isLoading={true} />);
  expect(screen.getByTestId("skeleton")).toBeInTheDocument();
});
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Class components are deprecated"                    | Class components still work and will not be removed. The React team recommends function components for new code. Existing class components do not need to be migrated unless there is another reason to touch them. |
| "A component can only return one element"            | A component can return an array (with `key` props), a Fragment (`<>...</>`), null, a string, or a Portal. The "one element" limitation was React < 16; it no longer exists.                                         |
| "Every time state changes, the whole app re-renders" | Only the component that owns the changed state and its descendants re-render. Siblings and ancestors are unaffected unless they also consume the changed state.                                                     |
| "Component files must match component names"         | Convention strongly suggests this (one component per file, filename = component name) but React does not enforce it. A single file can export multiple components.                                                  |

---

### 🚨 Failure Modes & Diagnosis

**Component Defined Inside Another Component**

**Symptom:**
An input loses focus on every keystroke. A list resets to
its initial state on every parent render. The component tree
in React DevTools shows components unmounting and remounting
on each render.

**Root Cause:**
A component is defined inside another component's function
body. Each parent render creates a new function reference.
React sees a new component type at the same tree position
and unmounts/remounts the entire subtree.

```jsx
// BAD: InputField is a new function on every render
function Form() {
  function InputField({ value, onChange }) {
    // <- WRONG
    return <input value={value} onChange={onChange} />;
  }
  return <InputField value={name} onChange={setName} />;
}
// InputField is different every render -> unmount/remount
// -> input loses focus every time Form re-renders
```

**Fix:**
Move component definitions outside any other component:

```jsx
// GOOD: defined at module level, stable identity
function InputField({ value, onChange }) {
  return <input value={value} onChange={onChange} />;
}

function Form() {
  return <InputField value={name} onChange={setName} />;
}
```

---

**Security: XSS via `dangerouslySetInnerHTML`**

**Symptom:**
User-provided HTML is rendered directly in a component,
enabling script injection.

**Root Cause:**
`dangerouslySetInnerHTML` bypasses React's automatic HTML
escaping. Any unsanitised user content set via this API
executes as HTML, including `<script>` tags.

**Fix:**
Never pass unsanitised user input to `dangerouslySetInnerHTML`.
If rich text is required, sanitise using a dedicated library
(DOMPurify) before setting:

```jsx
import DOMPurify from "dompurify";

function RichText({ html }) {
  const clean = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
// DOMPurify removes script tags, event handlers, etc.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Declarative UI vs Imperative DOM Manipulation` - the
  programming model that makes components predictable
- `The Component Mental Model` - the conceptual framework
  before the implementation details

**Builds On This (learn these next):**

- `JSX` - the syntax for describing what a component returns
- `Props` - how data is passed into components
- `State` - how components maintain data that changes
- `Event Handling in React` - how components respond to user actions

**Alternatives / Comparisons:**

- `Class Component` - the pre-2019 alternative to function
  components; uses lifecycle methods instead of hooks; still
  valid but not recommended for new code
- `Web Component` - browser-native custom elements; no
  virtual DOM, no React; different encapsulation model

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A capital-letter JS function that        │
│              │ returns JSX (or null/string/array)      │
├──────────────┼──────────────────────────────────────────┤
│ RULES        │ 1. Capital letter name                  │
│              │ 2. Returns valid React output           │
│              │ 3. Pure during rendering                │
├──────────────┼──────────────────────────────────────────┤
│ JSX RULE     │ <UserCard /> calls UserCard function    │
│              │ <div /> creates a DOM element           │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Always - every React UI is components   │
├──────────────┼──────────────────────────────────────────┤
│ AVOID        │ Defining components inside components   │
│              │ (causes unmount/remount on every render)│
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Lowercase component names; side effects │
│              │ in the render return path               │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Encapsulation + reusability vs component│
│              │ tree depth and prop drilling            │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "A function, capital name, returns JSX; │
│              │  it must be pure during rendering."     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ JSX -> Props -> State -> Event Handling │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. A component is a function with a capital letter that
   returns JSX. React calls it; you do not call it directly.
   `<UserCard />` = `UserCard({...props})` in React's eyes.
2. Never define a component inside another component's
   function body. React sees a new type on every render,
   causing unmount/remount and losing state and focus.
3. Components must be pure during rendering: no fetch, no
   setTimeout, no DOM mutation in the function body. Side
   effects go in `useEffect`.

**Interview one-liner:**
"A React component is a capital-letter function that accepts
props and returns JSX. It must be pure during rendering: same
props and state produce the same output. Side effects are
isolated to `useEffect`. Components compose by nesting their
JSX in each other's returns, forming a tree that React
evaluates top-down to produce the DOM."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define units of reuse at the boundary of single
responsibility. If a piece of logic or UI appears in more
than one place, that is the signal to extract it into an
independent unit. The cost of extraction is the abstraction;
the benefit is a single point of change. React's component
model makes this cost explicit.

**Where else this pattern appears:**

- CSS variables / design tokens - define once, use everywhere;
  changing the token changes all usages
- Database stored procedures - encapsulate business logic;
  callers use the procedure, not raw SQL
- Python decorators - a function that wraps another function
  to add behaviour; the component = function pattern is similar

---

### 💡 The Surprising Truth

React does not differentiate between "reusable library
components" and "app-specific page components" at the
framework level. Both are functions. The commonly observed
distinction between "smart/container components" (have state,
fetch data) and "dumb/presentational components" (only props,
no state) is a team convention, not a React feature. React
has no built-in concept of "smart" or "dumb" components.
Whether you keep this separation is a design decision your
team makes, not a React rule.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** To a developer from a jQuery background: why
   a React component loses its state when the parent
   re-renders and creates a new component type at the same
   tree position - and how `key` relates to this.
2. **DEBUG** Given a form input that loses focus on every
   keystroke, diagnose whether the cause is a component
   defined inside another component or a `key` prop
   changing on every render.
3. **SECURE** Identify every use of `dangerouslySetInnerHTML`
   in a codebase, verify each has DOMPurify sanitisation,
   and add an ESLint rule to flag new usages for review.
4. **BUILD** Create a `Button` component with TypeScript props
   (`variant`, `size`, `disabled`, `onClick`, `children`),
   default values, and a React Testing Library test covering
   the disabled state.
5. **REFACTOR** Given a class component using
   `componentDidMount` and `componentDidUpdate`, rewrite
   it as a function component with equivalent `useEffect`
   behaviour and explain the semantic differences.

---

### 🧠 Think About This Before We Continue

**Q1.** React uses component position in the tree as its
default identity mechanism. The `key` prop overrides this.
A common bug: rendering a list of items without keys causes
React to reuse component instances for different items when
the list order changes. How does this manifest as a bug,
and what is the correct mental model for when to use `key`?
_Hint: An input inside a list item that retains its value
when items are reordered._

**Q2.** A component is required to be pure during rendering.
But what does "pure" really mean for a React component when
it calls `useState`? Calling `useState` with the same
argument on subsequent renders does NOT return the same
value - it returns the current state. How does this fit
the "pure function" model?
_Hint: React's definition of purity is about not having
side effects, not about referential transparency._

**Q3.** React's Strict Mode intentionally calls your component
function twice in development (but not production) to help
detect impure rendering. If your component has a
`console.log` at the top, it logs twice. What is React
testing for with the double invocation, and why would a
pure render function produce identical results both times
while an impure one would not?
_Hint: Think about a component that increments a counter
variable declared outside the component._
