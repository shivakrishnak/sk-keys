---
id: RCT-043
title: Render Props Pattern
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-005, RCT-010, RCT-024
used_by: RCT-044, RCT-047
related: RCT-042, RCT-044, RCT-024
tags:
  - react
  - frontend
  - patterns
  - composition
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/react/render-props-pattern/
---

⚡ TL;DR - The render props pattern shares stateful logic
between components by passing a function (the "render
prop") that the sharing component calls with its state
as arguments; the consumer controls what gets rendered
with the shared logic; it solved the same problem as HOCs
without wrapper nesting, and is now largely superseded
by custom hooks for logic reuse.

| #043            | Category: React                                            | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | React Components, React.memo, Custom Hooks                 |                 |
| **Used by:**    | Compound Components Pattern, Class to Hooks Migration      |                 |
| **Related:**    | Higher-Order Components, Compound Components, Custom Hooks |                 |

---

### 🔥 The Problem This Solves

**LOGIC REUSE WITHOUT HOC WRAPPER NESTING:**
HOCs solve logic reuse but create wrapper nesting in
the component tree. Render props offered an alternative:
the logic-providing component is in the JSX tree, but
instead of wrapping the consumer, it CALLS a function
to let the consumer control the rendered output.

The pattern also solves a HOC weakness: prop collisions.
With HOCs, two HOCs injecting `data` props collide
silently. With render props, the consumer names the
arguments and there is no collision.

Key difference from HOCs: the consumer component's code
is visible at the JSX call site (no mystery about what
the wrapped component receives). This makes render props
more readable but more verbose.

---

### 📘 Textbook Definition

**Render Props Pattern** - a React composition technique
where a component exposes a prop (commonly named `render`
or `children`) whose value is a function. The component
calls this function with its internal state, allowing
the consumer to determine what UI to render using that
state. The logic component handles state management and
side effects; the consumer controls the rendered output.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// Logic component: manages mouse position state
class MouseTracker extends React.Component {
  state = { x: 0, y: 0 };

  handleMouseMove = (e) => {
    this.setState({ x: e.clientX, y: e.clientY });
  };

  render() {
    // Calls the render prop with its state
    return (
      <div onMouseMove={this.handleMouseMove}>
        {this.props.render(this.state)}
      </div>
    );
  }
}

// Consumer: decides what to render with the coordinates
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        // Full control over what to render with x and y
        <p>
          Mouse is at ({x}, {y})
        </p>
      )}
    />
  );
}

// Alternative: use children as the render prop
function App() {
  return (
    <MouseTracker>
      {({ x, y }) => (
        <p>
          Mouse: ({x}, {y})
        </p>
      )}
    </MouseTracker>
  );
}
```

---

### 🔩 First Principles Explanation

**WHY "RENDER PROP" IS A GOOD NAME:**

```
A "prop" is any value passed to a component.
A "render prop" is a prop whose VALUE is a function
that RETURNS React elements (JSX).

The pattern turns rendering into a callback:
  "I have logic. You decide what to render with it."

Three equivalent ways to implement:
  1. Named render prop:  <X render={(state) => <Y />} />
  2. Children as function: <X>{(state) => <Y />}</X>
  3. Any named prop: <X component={(state) => <Y />} />
     (react-router uses component= and element= props)

The logic-providing component (X) calls the function:
  render() {
    return this.props.render(this.state);
    // or: return this.props.children(this.state);
  }
```

**HOC vs Render Props (same problem, different approaches):**

```
HOC approach: wraps component, injects props top-down
  const EnhancedPage = withMousePosition(Page);
  // Page receives x, y as props (hidden from JSX)
  // Page cannot control HOW it receives the position

Render Props: consumer controls rendering explicitly
  <MouseTracker render={({x, y}) => <Page x={x} y={y} />}
    />
  // Page receives x, y explicitly from the caller
  // Consumer decides what to do with x and y
  // No prop name collision, no mystery injection
```

---

### 🧪 Thought Experiment

**THE FORMIK PATTERN:**
Formik (a popular React form library) historically used
render props as its primary API:

```jsx
<Formik initialValues={...} onSubmit={...}>
  {({ values, errors, handleChange, handleSubmit }) => (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        value={values.email}
        onChange={handleChange}
      />
      {errors.email && <span>{errors.email}</span>}
      <button type="submit">Submit</button>
    </form>
  )}
</Formik>
```

Formik manages form state, validation, and submission.
The consumer writes the form UI using the injected helpers.
No HOC wrapping, no prop collisions, full control over
the rendered form structure.

Formik v2 added hooks (`useFormik`, `useField`) as the
primary API - same reason custom hooks replaced render
props: the hooks version is less verbose, no JSX nesting.

---

### 🧠 Mental Model / Analogy

> Render props are like a car rental company that provides
> the engine and drivetrain (logic) but asks you to
> bring your own body design (render function). The rental
> company says: "We handle the engine, transmission, and
> all mechanical work. You tell us what the car looks like."
>
> HOC: the rental company gives you a pre-designed complete
> car (you cannot change the body). More convenient if
> you like their design. Less control.
>
> Render props: the rental company gives you the drivetrain
> and you attach whatever body you want. More control,
> more assembly required.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
A component that accepts a function as a prop and calls
it to render. Shares logic by passing state to the
function. Consumer controls the rendered output.

**Level 2 (usage):**
Use `children` as the function for cleaner syntax. Works
with class and functional components. No wrapper nesting.
No prop collisions.

**Level 3 (vs custom hooks):**
Custom hooks replaced render props for logic reuse in
functional components. `useMousePosition()` is cleaner
than `<MouseTracker render={...} />`. Render props remain
useful when: (a) the pattern needs to work with class
components, (b) the render function is used for slot/
composition patterns (not just logic injection), or (c)
the library has a render props API (react-window's
FixedSizeList uses render props for item rendering).

**Level 4 (performance concern):**
Render props can cause performance issues. The render
function is a new function instance on every parent
render. If the logic component checks for function
changes (e.g., `React.memo` on the logic component),
it will always re-render because the function prop changes.
Fix: use `useCallback` to stabilise the render function,
or lift the function outside the component.

**Level 5 (mastery):**
Render props are a special case of the "slot" pattern:
a component that delegates control over part of its
render to the caller. This generalises to compound
components (each "slot" corresponds to a named child),
headless UI components (full render control, no opinions
on markup), and the `children` pattern. Libraries like
Radix UI, react-aria, and headless-ui use this principle:
provide all the behaviour (accessibility, keyboard nav,
ARIA attributes) and let the consumer provide the markup
and styles. This is render props applied at a library scale.

---

### ⚙️ How It Works (Mechanism)

**Render prop with React.memo and useCallback:**

```jsx
// Logic component using functional style
function DataFetcher({ url, children }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(url)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setLoading(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  // Calls the children function with current state
  return children({ data, loading, error });
}

// Consumer component
function UserList() {
  // useCallback stabilises the render function reference
  const renderUsers = useCallback(({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return (
      <ul>
        {data.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    );
  }, []);

  return <DataFetcher url="/api/users">{renderUsers}</DataFetcher>;
}

// Custom hook equivalent (modern preferred approach):
function useDataFetcher(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(url)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setLoading(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { data, loading, error };
}

function UserList() {
  const { data, loading, error } = useDataFetcher("/api/users");
  // No JSX nesting, no render prop
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return (
    <ul>
      {data.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}
```

---

### 💻 Code Example

**BAD: Render prop with inline function (re-creates on every render):**

```jsx
// BAD: new function on every Parent render
// If DataFetcher uses React.memo, it re-renders anyway
// because the children prop (a function) changes reference
function Parent() {
  return (
    <DataFetcher url="/api/users">
      {(
        { data }, // new arrow fn every render
      ) => <UserTable users={data} />}
    </DataFetcher>
  );
}
```

**GOOD: Stabilise with useCallback:**

```jsx
// GOOD: stable function reference with useCallback
function Parent() {
  const renderUsers = useCallback(
    ({ data }) => <UserTable users={data} />,
    [], // stable: no deps
  );

  return <DataFetcher url="/api/users">{renderUsers}</DataFetcher>;
}
// DataFetcher wrapped in React.memo will not re-render
// when Parent re-renders (function reference is stable)
```

---

### 📊 Comparison Table

|                             | Render Props                   | HOC                                     | Custom Hook                 |
| --------------------------- | ------------------------------ | --------------------------------------- | --------------------------- |
| Visible in JSX              | Yes (function in JSX)          | No (wraps silently)                     | No (hook call in component) |
| Prop collisions             | None                           | Possible (silent)                       | None                        |
| Works with class components | Yes                            | Yes                                     | No                          |
| Nesting in DevTools         | Yes (logic component visible)  | Yes (wrapper visible)                   | No (invisible)              |
| Verbosity                   | High (function in JSX)         | Medium (wraps at module level)          | Low (hook call)             |
| Performance risk            | Function re-create each render | New component type if defined in render | Stable with no issues       |
| Co-location of logic        | In separate component          | In separate HOC function                | In separate hook            |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                            |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Render props are the same as children"           | `children` can be used as a render prop (when it is a function), but not all children usages are render props. `children` as a render prop: `{(state) => <UI />}`. `children` as content: `<p>text</p>`. They are syntactically the same prop but semantically different patterns. |
| "Render props are obsolete"                       | Render props remain the right tool for component-level slot patterns (headless UI, render-controlled libraries like react-window) and when working with class components. They are "replaced" only for logic reuse in functional components where hooks are cleaner.               |
| "Render props automatically handle performance"   | The opposite - inline render prop functions are new references on every render, causing the logic component to see changed props. Without `useCallback` or defining the render function outside the component, performance can be worse than alternatives.                         |
| "You need a prop named 'render' for render props" | The pattern works with any prop name including `children`. React Router's `<Route component={...}>` and `<Route render={...}>` are both render props. The common pattern is to use `children` as the function for cleaner JSX.                                                     |

---

### 🚨 Failure Modes & Diagnosis

**"React component suspended while rendering" with Render Props**

**Symptom:** A render prop function that returns a React.lazy
component causes the Suspense error "the component
suspended while rendering, but no fallback UI was specified."

**Root Cause:** The render prop function returns a lazy
component but there is no Suspense boundary above the
logic component.

**Fix:** Wrap the logic component (not just the lazy
component) in a Suspense boundary, or add Suspense inside
the render prop function.

---

**Render Prop Component Re-renders on Every Parent Render**

**Symptom:** A logic component using `React.memo` still
re-renders on every parent render.

**Root Cause:** The render prop function is defined inline
(new reference on every parent render), bypassing memo.

**Diagnosis:**

```jsx
// Console shows DataFetcher renders on every App render
// even though url prop has not changed
```

**Fix:** Stabilise with `useCallback`:

```jsx
const render = useCallback(({ data }) => <UI data={data} />, []);
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `React Components` - component composition fundamentals
- `Custom Hooks` - the modern alternative for logic reuse
- `React.memo` - performance interaction with render props

**Builds On:**

- `Compound Components Pattern` - extends render props
  to a full slot/composition pattern
- `Class Components to Hooks Migration` - render props in
  legacy code that needs migration
- `Higher-Order Components` - alternative composition pattern

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PATTERN  │ <X render={(state) => <UI />} />             │
│ CHILDREN │ <X>{(state) => <UI />}</X>  (cleaner)        │
│ BENEFIT  │ No prop collision, explicit, no HOC nesting  │
├─────────────────────────────────────────────────────────┤
│ PERF     │ useCallback for render fn (stabilise ref)    │
│ MODERN   │ Custom hook replaces for logic reuse         │
│ KEEP     │ Slot/headless patterns, class components     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Render prop = a component prop whose value is a
   function that returns JSX; called by the component
   with its state; consumer controls the rendered output.
2. Use `useCallback` for the render function to prevent
   unnecessary re-renders in memoised logic components.
3. Custom hooks replaced render props for logic reuse in
   functional components. Render props remain for headless/
   slot patterns and class component integration.

**Interview one-liner:**
"The render props pattern is a component composition
technique where a component accepts a function prop,
calls it with its internal state, and the consumer
decides what to render. It solves the same code reuse
problem as HOCs without wrapper nesting or prop collisions.
The pattern is now largely replaced by custom hooks for
stateful logic reuse in functional components, but
remains relevant for headless UI patterns (where a
library provides behaviour and the consumer provides
markup) and class component integration."

---

### 💎 Transferable Wisdom

Render props are React's implementation of the Strategy
Pattern from Gang of Four: the "strategy" (how to render)
is passed in as a function, not hardcoded in the component.
The logic component (context in GoF terms) delegates
the rendering decision to the render prop function
(the strategy). This pattern recurs in many forms:
callback-based APIs (Array.sort comparator, event handlers),
template method pattern (Java abstract class with
abstract methods for subclasses to implement), plugin
systems (provide a base system, consumers plug in
rendering/processing logic), and functional programming
(higher-order functions that accept and call functions).
Recognising this pattern makes library API design clearer:
when to use render props vs hooks vs configuration vs
subclassing is a recurring architectural decision.

---

### 💡 The Surprising Truth

The "children as a function" pattern predates React.
jQuery UI and other JavaScript UI libraries in the early
2010s used callback patterns for render control. The
term "render props" was popularised by Michael Jackson
(the React contributor, not the musician) in a 2017
blog post that argued "never write another HOC again."
The post became famous and drove a significant portion
of the React community toward render props over HOCs.
Two years later, hooks (React 16.8, 2019) superseded
BOTH patterns for logic reuse. Michael Jackson himself
then wrote about how hooks replaced render props. Both
patterns are now considered "solved" by hooks for new
code - but understanding the evolution is important for
working with any React codebase more than 3 years old.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a `MouseTracker` component using render
   props that shares mouse position. Show both `render`
   prop and `children` as function variants.
2. **DEMONSTRATE** the performance problem: an inline
   render prop function causing a memoised component to
   re-render. Fix with `useCallback`.
3. **CONVERT** a render props component to a custom hook.
   Show that the hook is simpler, less verbose, and
   avoids JSX nesting while achieving the same logic reuse.
4. **IDENTIFY** a use case where render props are still
   the correct choice over a custom hook (headless UI
   library pattern or class component integration).
5. **COMPARE** the DevTools tree for a component using
   HOC, render props, and custom hooks. Explain the
   difference in visibility and debuggability.

---

### 🧠 Think About This Before We Continue

**Q1.** A headless date picker library uses render props
to give full control over the calendar markup: `<DatePicker
render={({ selectedDate, onDateChange, daysInMonth }) =>
<MyCalendarUI ... />} />`. The library handles all
keyboard navigation, ARIA attributes, and date calculations.
The consumer handles all CSS and markup. How does this
differ from a custom hook `useDatePicker()` that returns
the same values? What does the render prop version enable
that a hook cannot?

**Q2.** React's `<Context.Consumer>` is a render props
API: `<ThemeContext.Consumer>{(theme) => <Button theme={theme} />}</ThemeContext.Consumer>`. The `useContext(ThemeContext)` hook
is its replacement. Given that the hooks version is
objectively simpler, why does `Context.Consumer` still
exist in React 18? Under what circumstances would you
use `Context.Consumer` today?

**Q3.** The render prop function can be conditionally
called. A logic component might decide NOT to call the
render prop in certain states. For example, if the user
lacks permission, the component renders `null` instead
of calling `render(state)`. How does this differ from
a custom hook that returns `null` data? What new
capabilities does this give the logic component that a
hook-based solution cannot provide?
