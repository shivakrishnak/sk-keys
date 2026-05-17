---
id: RCT-009
title: Props
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-008
used_by: RCT-010, RCT-013, RCT-014, RCT-015, RCT-016, RCT-025, RCT-029
related: RCT-016, RCT-025, RCT-029
tags:
  - react
  - frontend
  - core
  - data-flow
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /react/props/
---

# RCT-009 - PROPS

⚡ TL;DR - Props are read-only inputs that a parent passes
to a child component; they are the contract between parent
and child and the mechanism for one-way data flow - mutating
props is a common mistake that breaks the data flow model.

| #009            | Category: React                                                                                                                  | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Component, JSX                                                                                                                   |                 |
| **Used by:**    | State, Event Handling, Conditional Rendering, List Rendering, One-Way Data Binding, Controlled vs Uncontrolled, Lifting State Up |                 |
| **Related:**    | One-Way Data Binding, Controlled vs Uncontrolled, Lifting State Up                                                               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before props, making a reusable HTML element meant hard-coding
its content. A "user card" always showed the same name, the
same email, the same avatar. To show different users, you
created different HTML elements or dynamically set DOM
properties with different values - which meant the component
was not actually reusable; it was just an HTML pattern.

Props solve the reuse problem: the same `UserCard` component
can display any user because the data is passed in as
parameters, not hard-coded. This is the mechanism that makes
components genuinely reusable units.

---

### 📘 Textbook Definition

**Props** (short for "properties") are the mechanism by which
a parent React component passes data and callback functions
to a child component. Technically, `props` is a plain
JavaScript object whose properties correspond to the JSX
attributes written by the parent. Props are **read-only**:
a child component must never modify its own props. If a
child needs to signal an event to its parent, the parent
passes a callback function as a prop and the child calls it.
Props are the basis for React's unidirectional (one-way)
data flow: data flows down the tree from parent to child via
props; events flow up via callback props.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Props are the parameters of a component function - they pass
data from parent to child and are read-only.

**One analogy:**

> Props are like function arguments. You call a function with
> arguments; React renders a component with props. The
> function body does not modify its arguments; the component
> does not modify its props. When you need different output,
> you call with different arguments (or render with different
> props).

**One insight:**
Every JSX attribute you write becomes a prop. `<UserCard
name="Alice" />` passes `{ name: "Alice" }` as the props
object. The built-in HTML-like elements (`<div>`, `<input>`)
also accept props - but for those, React maps them to DOM
attributes. The same mechanism; different handling.

---

### 🔩 First Principles Explanation

**PROPS = FUNCTION PARAMETERS:**

```
Parent renders:  <UserCard name="Alice" age={30} />
                  |
React calls:     UserCard({ name: "Alice", age: 30 })
                  |
Component uses:  function UserCard(props) {
                   return <div>{props.name}</div>;
                 }
                 // OR with destructuring (preferred):
                 function UserCard({ name, age }) {
                   return <div>{name}</div>;
                 }
```

**THE IMMUTABILITY RULE:**
Props are immutable from the child's perspective. The child
receives the current snapshot of data. If the parent's data
changes, the parent re-renders and calls the child with new
props. The child never "updates" its props; it simply receives
new values on re-render.

This is enforced by convention (TypeScript's `Readonly<Props>`)
and by React's design. Violating it with `props.name = "Bob"`
does not update the parent's data - it only mutates the local
object, causing the child to show inconsistent data that
React cannot reconcile correctly.

**CALLBACK PROPS - events flow UP:**

```jsx
// Parent owns the state; passes setter as a callback prop
function Parent() {
  const [name, setName] = useState("Alice");
  return <Child name={name} onNameChange={setName} />;
}

// Child receives state as a prop AND a way to update it
function Child({ name, onNameChange }) {
  return <input value={name} onChange={(e) => onNameChange(e.target.value)} />;
}
// Data flows DOWN: name prop
// Events flow UP: onNameChange callback
```

---

### 🧪 Thought Experiment

**SETUP:**
A `PriceTag` component needs to display a price. Three pages
use it: a product page, a cart summary, and a checkout
confirmation. Each shows a different price.

**WITHOUT PROPS (hardcoded):**
Three separate PriceTag components, each with a different
price in the JSX. Formatting change (add currency symbol)
requires editing three files.

**WITH PROPS (parameterised):**

```jsx
function PriceTag({ amount, currency = "USD" }) {
  return (
    <span className="price-tag">
      {currency} {amount.toFixed(2)}
    </span>
  );
}

// Three uses, one component, one place to change:
<PriceTag amount={29.99} />            // product page
<PriceTag amount={totalAmount} />       // cart summary
<PriceTag amount={orderTotal} currency="EUR" />  // checkout
```

Adding a currency symbol to the format: one edit in
`PriceTag`, all three pages update.

---

### 🧠 Mental Model / Analogy

> Think of a component as a recipe and props as the
> ingredients. The recipe (component) defines what to do
> with ingredients. Different ingredients (props) produce
> different dishes (rendered output). You do not bake the
> ingredients into the recipe card; you pass them in
> each time you cook.

```
Recipe = UserCard function
Ingredients = { name, email, avatarUrl }
Dish = rendered UI for that user

Different ingredients:
  UserCard({ name: "Alice" }) -> Alice's card
  UserCard({ name: "Bob" })   -> Bob's card

Same recipe, different inputs, different outputs.
```

Where this breaks: props are immutable during a render.
Unlike function arguments which you could theoretically
reassign (JavaScript allows it), props should be treated
as a frozen snapshot. Reassigning them in the component
body is a code smell that confuses React's reconciliation.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Props are the way you send data to a component. When you
write `<Button color="blue" />`, the `color="blue"` is a
prop. Inside the `Button`, you can use `props.color` to
make the button blue.

**Level 2 - How to use it (junior developer):**
In JSX, attributes become props. In the component,
destructure them from the first argument: `function Button({
color, onClick, children })`. Use default values with `=`:
`function Button({ color = "blue" })`. Callback functions
are also props: `<Button onClick={handleSave} />`.

**Level 3 - How it works (mid-level engineer):**
When React renders `<UserCard name="Alice" />`, it constructs
`{ name: "Alice" }` and passes it to `UserCard()`. If the
parent re-renders with different data (`name="Bob"`), React
calls `UserCard({ name: "Bob" })` again. Props are not stored
by React between renders - they are computed fresh on each
render from the parent's current state.

**Level 4 - Why it was designed this way (senior/staff):**
Props immutability is a consequence of React's unidirectional
data flow. If children could modify their own props, data
could flow in multiple directions - the source of truth would
be ambiguous. By making props read-only, React guarantees
that the source of truth is always the parent (or the state
management layer). This is what makes React applications
debuggable: you can always trace data to its source.

**Level 5 - Mastery (distinguished engineer):**
Props create the public API of a component. In large design
systems, props are carefully versioned. A breaking change to
a prop type (renaming `color` to `variant`) requires a
migration strategy across all call sites. TypeScript
`Readonly<T>` applied to props interfaces enforces
immutability at the type level. The `children` prop deserves
special attention: it allows component composition (the slot
pattern), is typed as `React.ReactNode`, and is how React
avoids the need for named slots (a Vue/Angular concept).

---

### ⚙️ How It Works (Mechanism)

**Props spreading and TypeScript:**

```tsx
interface ButtonProps {
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  // Allow pass-through of native button attributes
  [key: string]: unknown;
}

// Spreading native button props (type-safe with Omit):
type SafeButtonProps = ButtonProps &
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, keyof ButtonProps>;

function Button({ variant = "primary", children, ...rest }: SafeButtonProps) {
  return (
    <button className={`btn btn--${variant}`} {...rest}>
      {children}
    </button>
  );
}
```

**The `children` prop:**

```jsx
// children is passed automatically when content is
// placed between the opening and closing JSX tags
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

// Usage - everything between tags becomes children:
<Card title="Profile">
  <UserAvatar url={user.avatarUrl} />
  <UserBio text={user.bio} />
</Card>;
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DATA FLOW DIAGRAM:**

```
┌────────────────────────────────────────────────────────┐
│                    App (owns state)                   │
│  state: { users: [...], selectedId: "1" }             │
│                                                       │
│  <UserList users={users}                              │
│            onSelect={setSelectedId} />                │
│       |                    ^                          │
│       | props (data down)  | callback (event up)      │
│       v                    |                          │
│  ┌─────────────────────────────────────────┐          │
│  │ UserList                                │          │
│  │  props: { users, onSelect }             │          │
│  │  maps users -> <UserItem key={u.id}     │          │
│  │                  user={u}               │          │
│  │                  onSelect={onSelect} /> │          │
│  └─────────────────────────────────────────┘          │
│       |                    ^                          │
│       | props (data down)  | callback (event up)      │
│       v                    |                          │
│  ┌─────────────────────────────────────────┐          │
│  │ UserItem                                │          │
│  │  props: { user, onSelect }              │          │
│  │  <div onClick={() => onSelect(user.id)}>│          │
│  └─────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────┘
```

Props only flow down. Events only travel up via callbacks.
The source of truth is always at the top of this diagram.

---

### 💻 Code Example

**Example 1 - BAD: Mutating props:**

```jsx
// BAD: mutating the props object
function UserCard(props) {
  // Never do this - mutates the props object
  props.name = props.name.toUpperCase(); // <- WRONG
  return <div>{props.name}</div>;
}
// Problems:
// 1. Does not update parent's state (parent still has lowercase)
// 2. Next render: parent passes lowercase again,
//    mutation is lost - inconsistent intermediate states
// 3. TypeScript will error if using Readonly<Props>
```

**Example 2 - GOOD: Deriving new values without mutation:**

```jsx
// GOOD: derive without mutation - compute, don't mutate
function UserCard({ name, isAdmin = false }) {
  const displayName = isAdmin ? `${name} (Admin)` : name;

  return <div>{displayName}</div>;
}
// Original props are untouched.
// displayName is a local computed variable.
```

**Example 3 - PRODUCTION: TypeScript props with validation:**

```tsx
interface UserCardProps {
  user: {
    id: string;
    name: string;
    email: string;
    role: "admin" | "user" | "guest";
    avatarUrl?: string;
  };
  onEdit?: (userId: string) => void;
  compact?: boolean;
}

function UserCard({ user, onEdit, compact = false }: UserCardProps) {
  return (
    <article className={`card ${compact ? "card--sm" : ""}`}>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      {user.role === "admin" && <span className="badge">Admin</span>}
      {onEdit && <button onClick={() => onEdit(user.id)}>Edit</button>}
    </article>
  );
}
```

---

### ⚖️ Comparison Table

| Concept                | Props                       | State                 | Context                    |
| ---------------------- | --------------------------- | --------------------- | -------------------------- |
| **Owner**              | Parent                      | Component itself      | Provider above in tree     |
| **Mutability**         | Read-only to child          | Read/write via setter | Read-only to consumers     |
| **Triggers re-render** | When parent re-renders      | When setter called    | When context value changes |
| **Scope**              | Single parent-to-child path | Local to component    | Any descendant             |
| **Use for**            | Passing data down           | Local changeable data | Cross-tree shared data     |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Props and state are the same thing"         | Props come from the parent and are read-only to the child. State is owned and mutated by the component itself. A prop cannot be modified by the component that receives it.                                                           |
| "I can pass any value as a prop"             | You can pass any valid JavaScript value as a prop: strings, numbers, booleans, objects, arrays, functions, React elements, even other components. Functions as props (callbacks) are the mechanism for child-to-parent communication. |
| "Updating a prop updates the parent's state" | Props are a snapshot. Modifying a prop in the child does not propagate back to the parent. To notify the parent, call a callback function that the parent passed as a prop.                                                           |
| "Default props require defaultProps"         | `defaultProps` (a React class component feature) is not needed for function components. Use JavaScript default parameter syntax: `function Btn({ color = "blue" })`.                                                                  |

---

### 🚨 Failure Modes & Diagnosis

**Stale Props in Event Handlers**

**Symptom:**
A button's `onClick` handler uses a prop value that is
one render behind. The event fires with the previous value.

**Root Cause:**
In some cases (particularly with `useCallback` or debounced
handlers), the callback closes over props from a previous
render. When the callback fires, it reads the stale closure.

**Diagnostic Command:**

```bash
# Add a console.log inside the event handler:
# console.log('prop at click time:', propValue);
# Compare with console.log in the render body.
# If render shows new value but click shows old:
# you have a stale closure over props.
```

**Fix:**
If using `useCallback`, include the prop in the dependency
array. Or avoid `useCallback` - premature memoisation of
callbacks is a common over-engineering mistake.

---

**Prop Drilling Across 5+ Levels**

**Symptom:**
A prop is passed through 5 components, most of which only
forward it to the next component. Adding a new needed piece
of data requires touching 5 component signatures.

**Root Cause:**
The component tree is not structured to match the data flow
requirements. Or the feature genuinely requires deep sharing.

**Fix:**

- If the data is needed by closely related components:
  restructure the tree (extract a compound component)
- If the data is needed by many unrelated components:
  use Context
- If the data is global app state: use Redux/Zustand

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Component` - props are how components receive external data
- `JSX` - the syntax for passing props as JSX attributes

**Builds On This (learn these next):**

- `State` - what a component owns vs what it receives via props
- `One-Way Data Binding` - the data flow model that props implement
- `Lifting State Up` - when two siblings need the same data
- `Prop Drilling Anti-Pattern` - what happens when props go too deep
- `Controlled vs Uncontrolled Components` - form inputs and props

**Alternatives / Comparisons:**

- `Context API` - a mechanism to pass values deeply without
  threading them through every intermediate component
- `Redux/Zustand` - global state accessible without props
  from anywhere in the tree

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Read-only inputs from parent to child;  │
│              │ the contract of a component's interface │
├──────────────┼───────────────────────────────────────────┤
│ SYNTAX       │ <UserCard name="Alice" age={30} />      │
│              │ function UserCard({ name, age }) {...}  │
├──────────────┼───────────────────────────────────────────┤
│ IMMUTABLE    │ Never mutate props in the child.        │
│              │ Compute derived values instead.         │
├──────────────┼───────────────────────────────────────────┤
│ EVENTS UP    │ Parent passes callback as prop.         │
│              │ Child calls it: onSave(data)            │
├──────────────┼───────────────────────────────────────────┤
│ CHILDREN     │ Content between tags = children prop   │
│              │ <Card><UserBio /></Card>                │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Mutating props; prop drilling > 3 levels│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Explicit data flow vs verbosity when    │
│              │ data is needed many levels deep         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Props are function parameters: read-   │
│              │  only, passed in, never mutated."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ State -> One-Way Binding -> Lifting Up  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Props are read-only. Never mutate `props.x = newValue`
   in the child. Compute new values from props: create a
   local variable with the derived result.
2. Callback functions passed as props are how children
   communicate upward. `onSave`, `onDelete`, `onChange` -
   these are the naming conventions for callback props.
3. The `children` prop is special: it is what you put
   between a component's opening and closing tags in JSX.
   It enables component composition (the slot pattern).

**Interview one-liner:**
"Props are the read-only inputs that a parent component
passes to a child, corresponding to the JSX attributes on
the component tag. They implement one-way data flow: data
flows down via props, events flow up via callback functions
passed as props. A child must never mutate its props; if it
needs to trigger a state change, it calls a callback the
parent provided."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Design component interfaces (props) with the same discipline
as API design. A minimal, well-typed props interface is
easier to consume, test, and evolve than a broad,
loosely-typed one. The `children` pattern (slot composition)
is almost always preferable to passing React elements as
named props (`content={<Comp />}`).

**Where else this pattern appears:**

- Function signatures in FP - pure functions receive all
  inputs as arguments; they do not reach for external state
- REST API request parameters - clients pass query params
  (read-only from the API's perspective)
- Unix program options - a program receives options as
  arguments and must not modify the caller's environment

---

### 💡 The Surprising Truth

The `children` prop is not special in React's implementation.
It is just a prop named `children`. `<Card><Spinner /></Card>`
is exactly equivalent to `<Card children={<Spinner />} />`.
React treats it the same. The JSX syntax makes the first form
natural. This means you can pass `children` explicitly as an
attribute when that is clearer, and you can type it as
`React.ReactNode` in TypeScript interfaces like any other prop.
The concept of "slots" from Angular and Vue is simply React's
`children` prop (for a default slot) and named callback/element
props (for named slots).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** Describe the flow of data from a user's
   keystroke in a child input up to a parent's state update,
   naming the two props involved (controlled value and
   onChange callback) and why both are needed.
2. **DEBUG** Given a component that shows stale prop values
   in an event handler, identify whether the issue is a stale
   closure in `useCallback` or something else, and fix it.
3. **DESIGN** Design the TypeScript interface for a
   `DataTable` component that accepts rows, columns, an
   optional `onRowClick` callback, and children for a
   toolbar slot - with correct types for each.
4. **REFACTOR** Given a component that mutates its own props
   to derive display values, rewrite it to compute those
   values locally without mutation.
5. **DECIDE** Given a prop that is passed through 4 component
   layers unused (only needed at layer 5), evaluate whether
   Context, restructuring, or prop spreading is the right
   solution for that specific case.

---

### 🧠 Think About This Before We Continue

**Q1.** React's one-way data flow means data flows down via
props and events flow up via callbacks. In Angular, two-way
binding (`[(ngModel)]`) allows a single binding to handle
both. What are the trade-offs between React's one-way model
and Angular's two-way model for a complex form with 20
fields, where every field change needs to update shared
validation state?
_Hint: Consider debugging complexity when an unexpected
value appears in a field._

**Q2.** TypeScript allows you to type props as `Readonly<T>`.
In practice, the TypeScript compiler enforces this at the
call site, but JavaScript does not enforce it at runtime.
What is the consequence of relying solely on TypeScript's
compile-time enforcement for props immutability in a
codebase that includes some JavaScript files or uses `any`?
_Hint: `Object.freeze(props)` in development mode._

**Q3.** React's `children` prop is typed as `React.ReactNode`,
which includes `null`, `undefined`, strings, numbers, JSX
elements, and arrays. This flexibility is powerful but can
cause subtle bugs: rendering `{children}` when `children`
might be a string, number, or array. When does this become
a problem, and what patterns (TypeScript discriminated unions,
React.Children API) help manage the ambiguity?
_Hint: A `Tooltip` component that expects exactly one child
to attach its ref to._
