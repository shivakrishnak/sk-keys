---
id: RCT-014
title: Conditional Rendering
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-008, RCT-009, RCT-010
used_by: RCT-025, RCT-026, RCT-027
related: RCT-015, RCT-010, RCT-008
tags:
  - react
  - frontend
  - rendering
  - jsx
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /react/conditional-rendering/
---

# RCT-014 - CONDITIONAL RENDERING

⚡ TL;DR - React renders UI conditionally using plain
JavaScript expressions inside JSX: the `&&` operator for
simple show/hide, ternary for if/else, and early returns
from the component function for entire block exclusion.

| #014            | Category: React                                    | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Component, JSX, Props, State                       |                 |
| **Used by:**    | Controlled Components, Form Handling, React Router |                 |
| **Related:**    | List Rendering, State, JSX                         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
HTML is static: you cannot express "show this element only
if the user is logged in" declaratively. Vanilla JavaScript
solves this imperatively: find the element, toggle a class,
or insert/remove it with `innerHTML`. This creates hidden
state scattered across DOM manipulation code. If multiple
conditions interact (user logged in AND has premium plan AND
is on the correct page), the imperative code becomes a
nest of if/else branches with no clear relationship to
the UI structure.

React's declarative conditional rendering keeps the
condition co-located with the UI element in JSX. The
component's return value describes what the UI looks like
for every possible state combination. The "how to show/hide"
is gone - replaced with "what the UI is when condition
is true or false."

---

### 📘 Textbook Definition

**Conditional rendering** in React is the practice of
returning different JSX from a component (or including
different elements within JSX) based on the values of
props or state. Because JSX is a JavaScript expression,
standard JavaScript conditionals - `if`, ternary (`? :`),
and logical AND (`&&`) - can be used to choose what to
render. React renders `null`, `undefined`, and `false`
as nothing (no DOM output), which enables the common
pattern of `{condition && <Component />}`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use `{condition && <El />}` for simple show/hide, ternary
`{condition ? <A /> : <B />}` for if/else, and `if`/`return`
before the JSX for complex logic.

**One insight:**

> `{0 && <Component />}` renders `0` on the screen.
> This is the most common conditional rendering bug.
> `&&` short-circuits to the falsy value if the condition
> is falsy. `0` is falsy but is a valid React child (renders
> as `"0"`). Always use booleans: `{items.length > 0 &&
<List />}` or `{!!items.length && <List />}`.

---

### 🔩 First Principles Explanation

**THE THREE PATTERNS:**

```
1. SIMPLE SHOW/HIDE: use && operator
2. IF/ELSE (two options): use ternary
3. COMPLEX MULTI-BRANCH: use if/early return in function
```

**HOW JSX HANDLES FALSY VALUES:**
React renders: strings, numbers (including 0!), JSX elements.
React renders nothing for: `null`, `undefined`, `false`.

```
null       → nothing rendered (no DOM node)
undefined  → nothing rendered
false      → nothing rendered
0          → renders "0" string in DOM  ← TRAP!
""         → renders empty string (no visible effect,
             but a text node exists)
```

**THE && TRAP IN DETAIL:**

```jsx
// TRAP: 0 renders as "0" on screen
const count = 0;
{
  count && <List />;
} // renders "0", not nothing!

// SAFE: comparison produces boolean, not number
{
  count > 0 && <List />;
} // renders nothing
{
  !!count && <List />;
} // renders nothing
{
  Boolean(count) && <List />;
} // renders nothing
```

---

### 🧪 Thought Experiment

**THE LOADING/ERROR/DATA PATTERN:**
Most UI components have three states: loading data, errored,
or data available. This is the canonical conditional
rendering multi-branch problem.

**Solution: extract to helper before JSX:**

```jsx
function UserProfile({ userId }) {
  const { data, loading, error } = useUser(userId);

  // Extract complex logic BEFORE JSX return
  function renderContent() {
    if (loading) return <Spinner />;
    if (error) return <Error message={error.message} />;
    if (!data) return <EmptyState />;
    return <Profile user={data} />;
  }

  return (
    <div className="profile-container">
      <h1>User Profile</h1>
      {renderContent()}
    </div>
  );
}
```

This is more readable than nesting ternaries:
`{loading ? <Spinner /> : error ? <Error /> : !data ? ...}`.

---

### 🧠 Mental Model / Analogy

> React component output is like a digital menu board at a
> cafe. The board shows different items depending on the
> time of day (breakfast menu in the morning, lunch menu
> later). The board does not hide/show physical panels -
> it re-renders its entire content for each time slot.
> Conditional rendering is the logic that determines which
> "menu" to include in the output at any given time.

```
Component function runs (on every render):

  ┌─────────────────────────────────────┐
  │  if loading → return loading state  │
  │  if error   → return error state    │
  │  return     → return data state     │
  └─────────────────────────────────────┘
        │
        ▼ JSX description of UI
        │
        ▼ React reconciles with previous output
        │
        ▼ DOM updated (only the changed parts)
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
You can show or hide parts of your UI by putting conditions
in JSX. If a condition is false, React shows nothing for
that part.

**Level 2 (usage):**
Three patterns: `&&` for simple show/hide,
`condition ? <A /> : <B />` for two alternatives, and
`if` statements before the return for complex branching.
Never use `if` directly inside JSX (JSX only supports
expressions, not statements).

**Level 3 (mechanism):**
JSX compiles to `React.createElement` calls. Only
expressions are valid inside `{}` in JSX - `if`/`for` are
statements, not expressions. `&&` and ternary are
expressions, so they work. `null`/`false`/`undefined` are
valid React children that render as empty content.
React's reconciler sees them as "render nothing here."

**Level 4 (architecture):**
For complex state machines (loading/error/idle/success),
consider extracting rendering logic to a separate function
or component. Rendering a component as `null` (early return)
is different from not mounting it - a component that
returns `null` is still mounted and keeps its state.
Use `{condition && <Component />}` to unmount and remount
(state is lost). This distinction matters for forms, timers,
and subscriptions.

**Level 5 (mastery):**
Conditional rendering interacts with React's reconciliation.
`{isLoggedIn ? <UserMenu /> : <LoginButton />}` places two
different element types at the same tree position - React
unmounts one and mounts the other. But `{isLoggedIn &&
<UserMenu />}{!isLoggedIn && <LoginButton />}` places
elements at different positions - React may keep both
mounted with one hidden. The first approach is usually
correct (clean unmount/mount). Stable keys across branches
can force identity preservation even across conditional
switches in specific use cases.

---

### ⚙️ How It Works (Mechanism)

**Pattern 1 - Logical AND (show/hide):**

```jsx
// Show a badge only when there are notifications
{
  notifications.length > 0 && (
    <span className="badge">{notifications.length}</span>
  );
}
```

**Pattern 2 - Ternary (if/else):**

```jsx
// Show either the authenticated or unauthenticated menu
{
  isLoggedIn ? <UserMenu username={user.name} /> : <LoginButton />;
}
```

**Pattern 3 - Early return (complex logic):**

```jsx
function Dashboard({ user, permissions }) {
  if (!user) {
    return <LoadingScreen />;
  }
  if (!permissions.canViewDashboard) {
    return <AccessDenied />;
  }
  // Main render - all preconditions satisfied
  return (
    <div>
      <AdminPanel />
      <DataTable />
    </div>
  );
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STATE CHANGE TRIGGERS CONDITIONAL RE-RENDER:**

```
1. User clicks "Load Data" button
2. onClick handler: setLoading(true)
3. React re-renders: loading=true
4. JSX: {loading && <Spinner />} → Spinner mounts
5. API fetch completes: setLoading(false), setData(result)
6. React re-renders: loading=false, data=result
7. JSX: {loading && <Spinner />} → false, Spinner unmounts
8. JSX: {data && <DataTable rows={data} />} → DataTable mounts
9. DOM updates: Spinner removed, DataTable added
```

---

### 💻 Code Example

**BAD: Nested ternaries and the 0-bug:**

```jsx
// BAD: hard to read nested ternaries
function ProductStatus({ product }) {
  return (
    <div>
      {product.stock ? (
        product.stock > 10 ? (
          <span>In Stock</span>
        ) : (
          <span>Low Stock</span>
        )
      ) : (
        <span>Out of Stock</span>
      )}
      {/* BAD: renders "0" when count is 0 */}
      {product.reviewCount && <span>{product.reviewCount} reviews</span>}
    </div>
  );
}
```

**GOOD: clear patterns with no 0-bug:**

```jsx
// GOOD: readable pattern selection
function ProductStatus({ product }) {
  function getStockStatus() {
    if (!product.stock) return <span>Out of Stock</span>;
    if (product.stock > 10) return <span>In Stock</span>;
    return <span>Low Stock: {product.stock} left</span>;
  }

  return (
    <div>
      {getStockStatus()}
      {/* GOOD: boolean comparison avoids 0-renders-as-0 */}
      {product.reviewCount > 0 && <span>{product.reviewCount} reviews</span>}
    </div>
  );
}
```

**PRODUCTION: Loading/error/data pattern:**

```jsx
function OrderHistory({ customerId }) {
  const [state, setState] = useState({
    status: "idle", // idle | loading | error | success
    orders: [],
    error: null,
  });

  useEffect(() => {
    setState((s) => ({ ...s, status: "loading" }));
    fetchOrders(customerId)
      .then((orders) =>
        setState({
          status: "success",
          orders,
          error: null,
        }),
      )
      .catch((err) =>
        setState({
          status: "error",
          orders: [],
          error: err.message,
        }),
      );
  }, [customerId]);

  if (state.status === "idle") return null;
  if (state.status === "loading") {
    return <LoadingSpinner label="Loading orders..." />;
  }
  if (state.status === "error") {
    return <ErrorMessage title="Could not load orders" detail={state.error} />;
  }
  if (state.orders.length === 0) {
    return <EmptyState message="No orders found." />;
  }
  return <OrderList orders={state.orders} />;
}
```

---

### 📊 Comparison Table

| Pattern            | Syntax                   | Best For                  | Readability at Scale    |
| ------------------ | ------------------------ | ------------------------- | ----------------------- |
| `&&` operator      | `{cond && <A />}`        | Simple show/hide          | Good for 1 condition    |
| Ternary            | `{c ? <A /> : <B />}`    | Two clear alternatives    | Degrades with nesting   |
| Early return       | `if...return` before JSX | Multiple branches, guards | Best for 3+ branches    |
| Helper function    | `{renderContent()}`      | Complex multi-state       | Best for state machines |
| Separate component | `<ConditionalComp />`    | Reused conditional logic  | Best for complex trees  |

---

### ⚠️ Common Misconceptions

| Misconception                                                        | Reality                                                                                                                                                                                                                       |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`{false}` renders the text 'false'"                                 | `false`, `null`, and `undefined` render as empty (no DOM node). Only `0` is a falsy value that does render visibly as the character `"0"`.                                                                                    |
| "You cannot use if/else inside JSX"                                  | You cannot use `if` STATEMENTS as JSX expressions (inside `{}`). You CAN use an `if` block in the function body before the `return`, or call a function inside `{}` that contains `if`/`else`.                                |
| "Conditional rendering with `&&` is equivalent to ternary with null" | `{cond && <A />}` and `{cond ? <A /> : null}` are functionally identical for boolean `cond`. The `&&` version is shorter. The difference only matters when `cond` is a non-boolean falsy value (0, empty string).             |
| "A component that returns null is unmounted"                         | A component that `return null` is still mounted in React's component tree - it just renders nothing to the DOM. State and effects are preserved. Only removing the component from JSX (via conditional) actually unmounts it. |

---

### 🚨 Failure Modes & Diagnosis

**The `0` Renders on Screen Bug**

**Symptom:** A `0` appears in the UI unexpectedly.

**Root Cause:**

```jsx
{
  items.length && <List />;
}
// When items.length is 0: renders "0" as text
```

**Fix:**

```jsx
{
  items.length > 0 && <List />;
}
```

---

**Unexpected Component Remount**

**Symptom:** Form fields reset, animations restart, or
subscriptions re-initialise when a sibling condition changes.

**Root Cause:**
Two conditionally rendered elements at the same tree
position swap types, causing React to unmount one and
mount the other. React keyed state to tree position, not
component identity.

**Fix:**
Use a `key` prop to stabilise identity, or restructure so
elements at the same position are always the same type.

---

**Complex Nesting Hides Logic**

**Symptom:** Code reviews flag nested ternaries as unreadable.
New developers cannot follow the rendering conditions.

**Fix:**
Extract conditional logic to a helper function or render
method before the JSX return. Use a switch-like pattern
with if/return chains for state machines.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Component` - the function that contains conditional logic
- `JSX` - the syntax where conditionals are expressed
- `State` and `Props` - the data conditions are based on

**Builds On:**

- `List Rendering` - pairs with conditional rendering for
  "show list only if items exist" patterns
- `Error Boundaries` - handles rendering errors, a
  higher-level form of conditional rendering
- `Suspense` - declarative conditional rendering for
  async loading states

**Tooling:**

- `React DevTools` - inspect what a component rendered;
  confirm conditional branches are working as expected

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ &&      │ {cond && <A />}      │ show/hide           │
│ ternary │ {c ? <A /> : <B />}  │ two alternatives    │
│ if/ret  │ if (x) return <A />  │ multiple branches   │
├──────────────────────────────────────────────────────────┤
│ null/false/undefined → renders nothing (no DOM node)    │
│ 0 → renders "0" on screen ← COMMON TRAP                 │
├──────────────────────────────────────────────────────────┤
│ FIX: {count > 0 && <List />} not {count && <List />}    │
├──────────────────────────────────────────────────────────┤
│ return null = mounted, no output (state preserved)       │
│ {cond && <Comp />} = unmount when false (state lost)    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Use `&&` for simple show/hide, ternary for two options,
   `if`/early return for 3+ branches.
2. `{0 && <Component />}` renders `"0"` - always use a
   boolean comparison: `{count > 0 && <Component />}`.
3. A component that `return null` is still mounted; only
   `{condition && <Component />}` actually unmounts it.

**Interview one-liner:**
"Conditional rendering in React uses JavaScript expressions
in JSX: `&&` for show/hide, ternary for if/else, and
if-statements before the return for complex branching.
The key trap is `{0 && <El />}` which renders '0' because
0 is falsy but not null/false/undefined - use boolean
comparisons. A component returning null is still mounted;
the `&&` pattern actually unmounts the component."

---

### 💎 Transferable Wisdom

The conditional rendering patterns here (guard clauses,
early return, helper function for state machines) apply
beyond React. In any code that has "render/build/generate
something differently based on state", prefer flat
if-chains with early returns over nested ternaries. This
is called "fail fast" or "guard clause" pattern. It keeps
the happy path at the bottom of the function, visually
unindented, and each failure condition handled explicitly
at the top.

---

### 💡 The Surprising Truth

React's decision to make `false` render nothing but `0`
render as text was not arbitrary - it was a consequence
of JavaScript's type system. React must render numbers
because `{42}` is a legitimate inline value in JSX.
Making `0` invisible would break valid use cases like
`{score}` when score is 0. Making all falsy values invisible
(including `0` and `""`) would be more consistent, but
would hide real data. The actual design contract is:
React renders "valid displayable values" (strings, numbers,
JSX elements), and treats "empty/absent" signals (null,
undefined, false) as "render nothing." `0` is a valid
displayable number, not an empty signal - hence the
counterintuitive behaviour.

---

### ✅ Mastery Checklist

1. **EXPLAIN** the difference between `{count && <List />}`
   and `{count > 0 && <List />}`, and when the first
   version produces a visible bug.
2. **IMPLEMENT** a component that displays one of four
   states (loading, error, empty, data) using early returns,
   and explain why this is preferable to nested ternaries.
3. **IDENTIFY** a scenario where using `&&` conditional
   rendering unexpectedly causes a child component to lose
   its state (form data, scroll position, focus).
4. **DISTINGUISH** between a component returning `null` and
   a component being conditionally excluded with `&&` -
   explain the React lifecycle difference.
5. **REFACTOR** a component with three nested ternaries
   into a helper function with early returns, improving
   readability without changing behaviour.

---

### 🧠 Think About This Before We Continue

**Q1.** When React encounters `{condition && <Component />}`
and the condition becomes true, React mounts the component
(runs constructor/initialisation effects). When it becomes
false, React unmounts it (runs cleanup effects, state is
lost). What happens to a text input that was partially
filled out if the form section containing it is hidden
with `&&` and then shown again?

**Q2.** A team member suggests using CSS `display: none`
to "conditionally hide" components instead of conditional
rendering, arguing that mounting/unmounting has performance
cost. When is this argument valid, and when does it
backfire? Consider animations, screen readers, form state,
and expensive fetch effects.

**Q3.** React's `Suspense` component is described as
"declarative conditional rendering for async states":
`<Suspense fallback={<Spinner />}><AsyncComponent /></Suspense>`
shows the fallback while the component is loading. How does
this differ from manually writing `{loading ? <Spinner /> :
<AsyncComponent />}` in terms of what triggers the
conditional, and what this implies about where async
loading state lives?
