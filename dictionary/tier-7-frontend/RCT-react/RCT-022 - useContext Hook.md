---
id: RCT-022
title: useContext Hook
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-007, RCT-010, RCT-016, RCT-020, RCT-021
used_by: RCT-024, RCT-025, RCT-031, RCT-039
related: RCT-020, RCT-031, RCT-039
tags:
  - react
  - frontend
  - hooks
  - context
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 22
permalink: /react/usecontext-hook/
---

# RCT-022 - USECONTEXT HOOK

⚡ TL;DR - `useContext` reads a context value provided
by the nearest `Context.Provider` above the component in
the tree; it solves prop drilling for infrequently-changing
shared data (theme, locale, auth user); every context
consumer re-renders when the context value changes, so
it is not suitable for high-frequency state updates.

| #022            | Category: React                                                                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Component, State, One-Way Data Binding, useState, useEffect                    |                 |
| **Used by:**    | useRef Hook, Custom Hooks, Context API vs State Decision Guide                 |                 |
| **Related:**    | useState Hook, Context API vs State Decision Guide, Prop Drilling Anti-Pattern |                 |

---

### 🔥 The Problem This Solves

**PROP DRILLING AT SCALE:**
One-way data flow (props down, callbacks up) is React's
architectural strength. But when data is needed far down
the component tree - authenticated user in a profile icon
five components deep, or current theme in every button
and card - the data must be threaded through every
intermediate component as a prop. Each intermediate
component receives the prop only to pass it further down,
with no actual use. This is prop drilling.

Context solves this: a `Provider` wraps a subtree. Any
component anywhere in that subtree can read the context
value directly with `useContext`, bypassing intermediate
components entirely.

---

### 📘 Textbook Definition

React Context is a mechanism for passing values through
the component tree without explicit prop threading.
`createContext(defaultValue)` creates a Context object.
`<Context.Provider value={...}>` makes a value available
to all descendants. `useContext(Context)` reads the
nearest Provider's value.

**Three parts:**

```jsx
// 1. Create
const ThemeContext = createContext("light"); // default if no provider

// 2. Provide
<ThemeContext.Provider value="dark">
  <App />
</ThemeContext.Provider>;

// 3. Consume
function Button() {
  const theme = useContext(ThemeContext); // 'dark'
  return <button className={`btn-${theme}`}>Click</button>;
}
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Wrap a subtree with `<MyContext.Provider value={v}>`,
read `v` anywhere in that subtree with
`useContext(MyContext)` - no prop threading needed.

**Performance caveat:**

> Every component that calls `useContext(MyContext)` re-renders
> whenever the Provider's `value` prop changes. If the value
> is an object created inline (`value={{ user, setUser }}`),
> it is a new object every render - every consumer re-renders
> every time the parent renders. Fix: wrap the value in
> `useMemo` or split into separate contexts.

---

### 🔩 First Principles Explanation

**HOW CONTEXT LOOKUP WORKS:**

```
Component tree:

App (Provider: value="dark")
  └── Header
        └── Nav
              └── UserIcon (calls useContext(ThemeContext))
                  → walks up tree
                  → finds nearest ThemeContext.Provider
                  → reads "dark"

No props on Header or Nav needed.
UserIcon reads directly from the nearest Provider ancestor.
```

**THE RE-RENDER PROBLEM:**

```jsx
// Problem: new object reference on every render
function App() {
  const [user, setUser] = useState(null);

  return (
    // Every App render creates a new { user, setUser } object
    // Every consumer of AuthContext re-renders
    <AuthContext.Provider value={{ user, setUser }}>
      <Routes />
    </AuthContext.Provider>
  );
}

// Fix: memoize the context value
function App() {
  const [user, setUser] = useState(null);
  const authValue = useMemo(() => ({ user, setUser }), [user]);
  return (
    <AuthContext.Provider value={authValue}>
      <Routes />
    </AuthContext.Provider>
  );
}
```

---

### 🧪 Thought Experiment

**AUTH CONTEXT PATTERN:**
An e-commerce site has: NavBar (shows user name), Cart
(shows user's saved items), Checkout (needs user address).
These are at completely different tree depths. The auth user
is needed in all three. Without Context: thread `user` prop
through every intermediate component. With Context: the
`AuthProvider` at the root holds user state, each component
calls `useContext(AuthContext)` and reads directly.

The trade-off: if user state changes frequently (typing in
a search box that is also in the same context), ALL
consumers re-render. So auth context (rarely changes after
login) is a good use case. A "search query" context
(changes on every keystroke) would cause performance issues.

---

### 🧠 Mental Model / Analogy

> Context is like a building's public announcement system.
> The Provider is the PA system in the lobby. Any room
> in the building (any component) can listen to the PA
> system (useContext) without running cables through every
> floor and office in between. But when the PA system
> broadcasts (context value changes), EVERY room hears it
> and might react - you cannot selectively broadcast to
> only the rooms that care.

```
Without Context:            With Context:
App (user)                  App (AuthContext.Provider)
 └── Layout (user)           └── Layout (no user prop)
      └── Header (user)           └── Header (no user prop)
           └── Avatar (user)           └── Avatar
                                          uses useContext
                                          reads user directly
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Context lets you share data with any component in a
subtree without passing it as props through every level.
Use it for data that many components need (theme, current
user, language).

**Level 2 (usage):**
Create context with `createContext`. Wrap your app (or
a subtree) in the Provider. In any child component, call
`useContext(MyContext)` to read the current value. Put
context setup in a custom hook for cleaner API.

**Level 3 (mechanism):**
When `useContext(Ctx)` is called, React walks up the Fiber
tree to find the nearest `Ctx.Provider` ancestor. It
subscribes the component to that Provider. When the
Provider's `value` prop changes (by reference, using
`Object.is`), React marks all `useContext` consumers in
the subtree as needing re-render. There is no selector
mechanism - every consumer re-renders for every value
change, even if the specific part of the value it uses
did not change.

**Level 4 (architecture):**
Context has no built-in selector/subscription mechanism.
For large contexts with frequently-changing values, this
causes unnecessary re-renders. Solutions: (1) split
context by change frequency (ThemeContext rarely changes,
NotificationContext changes often - separate providers),
(2) wrap provider value in `useMemo`, (3) use a state
management library with selectors (Zustand, Redux with
`useSelector`) for high-frequency updates.

**Level 5 (mastery):**
Context is deliberately simple. It has no batching,
no selector, no optimistic updates. It is a low-level
primitive that state management libraries build on.
Zustand, for example, uses a React Context to provide
the store reference, then uses external subscriptions
(not React Context value changes) to trigger only the
specific components that subscribe to changed slices
of state. This is why Zustand consumers do not all
re-render when one part of the store changes.

---

### ⚙️ How It Works (Mechanism)

**Pattern: context + custom hook:**

```jsx
// auth-context.jsx
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSession()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  const login = async (credentials) => {
    const user = await loginAPI(credentials);
    setUser(user);
  };

  const logout = async () => {
    await logoutAPI();
    setUser(null);
  };

  // Memoize to prevent unnecessary consumer re-renders
  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook: encapsulates context access
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

**Usage:**

```jsx
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes />
      </Router>
    </AuthProvider>
  );
}

function UserAvatar() {
  const { user } = useAuth(); // clean, no Context directly
  return user ? <img src={user.avatarUrl} /> : null;
}
```

---

### 💻 Code Example

**BAD: Inline value object causes all consumers to re-render:**

```jsx
// BAD: new object every render = all consumers re-render
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  return (
    // { theme, setTheme } is a new object on every render
    // even if theme did not change
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

**GOOD: Stable value with useMemo:**

```jsx
// GOOD: memoized value - only changes when theme changes
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  const value = useMemo(
    () => ({ theme, setTheme }),
    [theme], // setTheme is stable (from useState)
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

// OR: split read and write into separate contexts
// Readers only re-render when theme changes
// Components that only call setTheme never re-render
const ThemeValueContext = createContext("light");
const ThemeSetContext = createContext(() => {});

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");
  return (
    <ThemeValueContext.Provider value={theme}>
      <ThemeSetContext.Provider value={setTheme}>
        {children}
      </ThemeSetContext.Provider>
    </ThemeValueContext.Provider>
  );
}
```

---

### 📊 Comparison Table

| Approach               | Prop drilling                | Context                 | Redux/Zustand                 |
| ---------------------- | ---------------------------- | ----------------------- | ----------------------------- |
| Best for               | Shallow trees, few consumers | Infrequent global data  | High-frequency, complex state |
| Re-render control      | Fine-grained (props)         | All consumers on change | Selector-based                |
| Boilerplate            | Low                          | Medium                  | Medium-High                   |
| DevTools support       | Props visible                | React DevTools          | Redux DevTools                |
| Cross-component access | Explicit prop chain          | Any descendant          | Any component                 |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Context is a state management solution like Redux"                | Context is a data transport mechanism (makes data available anywhere in the tree). It is not a state management system. State still lives in useState/useReducer. Context delivers that state without prop drilling. Redux has a global store, optimised subscription model, and DevTools. |
| "useContext causes unnecessary re-renders only if I pass objects"  | ANY context value change triggers all consumers to re-render. Even passing a primitive (a number that changes from 0 to 1) re-renders every consumer. Object values that are recreated each render re-render consumers even when the data is semantically the same.                        |
| "Context.defaultValue is used when no Provider exists in the tree" | The default value is only used when a component calls `useContext` with NO Provider anywhere above it in the tree. When a Provider is present with `value={undefined}`, consumers receive `undefined`, NOT the default value.                                                              |
| "Context replaces the need for state lifting"                      | Context and lifting state up solve different problems. Lifting state solves ownership (where does the state live?). Context solves access (how does a distant component read the state?). Both are often used together.                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**All Consumers Re-render on Every Parent Render**

**Symptom:** React DevTools Profiler shows every component
calling `useContext(MyContext)` highlights on every state
change in the parent, even unrelated changes.

**Root Cause:** Provider value is a new object reference
on every parent render.

**Fix:**

1. Wrap the context value in `useMemo`
2. Split frequently-changing state into separate contexts
3. Consider a state management library with selectors

---

**`useContext` Returns null or Default Value Unexpectedly**

**Symptom:** Component receives the default value instead
of the Provider's value. Or error: cannot read property
of null.

**Root Cause:** The component is rendering outside the
Provider's subtree. Common mistake: the Provider is
placed inside a Router but the component is rendered
outside the Router.

**Fix:** Check the component tree structure. Ensure the
Provider wraps all components that need the context value.
Add an error guard in the custom hook:
`if (!ctx) throw new Error('Must be inside Provider')`.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Component` - context lives in component instances
- `One-Way Data Binding` - context is an alternative
  delivery mechanism for the same one-way flow
- `useState Hook` - context delivers state created with
  useState

**Builds On:**

- `Context API vs State Management Decision Guide` -
  when to use Context vs Redux/Zustand
- `Prop Drilling Anti-Pattern` - the problem Context solves
- `Custom Hooks` - wrap `useContext` in a custom hook
  for clean API (`useAuth`, `useTheme`)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CREATE  │ const Ctx = createContext(defaultValue)      │
│ PROVIDE │ <Ctx.Provider value={v}>{children}</...>     │
│ CONSUME │ const v = useContext(Ctx)                    │
├──────────────────────────────────────────────────────────┤
│ PATTERN │ createContext + Provider component +         │
│         │ custom hook (useAuth, useTheme)              │
├──────────────────────────────────────────────────────────┤
│ PERF    │ All consumers re-render on value change      │
│ FIX     │ useMemo on value object in Provider          │
│         │ Split by change frequency (read/write ctx)   │
├──────────────────────────────────────────────────────────┤
│ GOOD    │ Auth user, theme, locale, feature flags      │
│ FOR     │ (infrequent changes, needed by many)         │
│ BAD FOR │ Form state, search query, any fast-changing  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `createContext` + `Provider` + `useContext` forms the
   trio. Always wrap `useContext` in a custom hook for a
   cleaner API and error boundary.
2. Every `useContext` consumer re-renders when the Provider
   value changes. Stabilise object values with `useMemo`
   in the Provider to prevent unnecessary re-renders.
3. Context is for infrequent, broadly-needed data (auth
   user, theme, locale). For high-frequency or complex
   state, use a state management library with selectors.

**Interview one-liner:**
"`useContext` reads from the nearest `Context.Provider`
above in the tree - it solves prop drilling for data
needed by many components (auth user, theme, locale).
The key performance issue: every consumer re-renders
when the Provider value changes. Stabilise object values
with `useMemo`. Context is not a state management system

- it is a data transport. State still lives in useState.
  For high-frequency updates, use Zustand or Redux with
  selector-based subscriptions."

---

### 💎 Transferable Wisdom

Context implements the Service Locator pattern (or a form
of dependency injection): a consumer declares what it
needs (`useContext(AuthContext)`) and the framework
resolves the value from the nearest Provider. This pattern
appears in dependency injection frameworks (Spring
`@Autowired`, Angular providers), operating system
environment variables (any process can read `$HOME`
without being explicitly told it), and browser globals
(`window.location` is available to any script without
being passed as a parameter). The trade-off is always the
same: implicit dependency (easier access) vs explicit
dependency (harder to misuse, easier to test).

---

### 💡 The Surprising Truth

React's Context was not originally designed for performance-
sensitive shared state. The React team has explicitly said
that Context is not a performance-optimised state
management tool and that applications needing frequent
shared state updates should use an external state
management library. The React 18 documentation recommends
Context only for values that change infrequently (once
per session or once per user action) or data that does
not change at all (compile-time configuration, feature
flags). The widespread use of Context for application-wide
state that changes frequently is a misuse that causes
performance regressions.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** an `AuthProvider` with `useAuth` custom
   hook: createContext, Provider component with state,
   consumer hook that throws if used outside Provider.
2. **DIAGNOSE** why all theme-using components re-render
   when an unrelated state changes in the root component,
   and apply the `useMemo` fix.
3. **DECIDE** whether to use Context or a state management
   library for: (a) current user after login, (b) shopping
   cart state updated on every item add/remove, (c) UI
   locale for i18n.
4. **EXPLAIN** why `Context.defaultValue` is different
   from the Provider's `value` prop, and give a scenario
   where the default value is actually used.
5. **REFACTOR** a three-level prop drilling chain into
   a Context, and explain when this refactor is and
   is not worth doing.

---

### 🧠 Think About This Before We Continue

**Q1.** Context has no selector mechanism: any change to
the context value re-renders ALL consumers. Zustand solves
this with selectors: `useStore(state => state.user)` only
re-renders when `user` changes, not when other parts of
the store change. At what point in an application's
complexity does this distinction matter, and how would
you identify that Context has become a performance
bottleneck?

**Q2.** Multiple Providers of the same Context type can
be nested. A component consumes the value from the NEAREST
Provider ancestor. This enables "scoped" context: a modal
inside a form can have its own form context that overrides
the outer form context. Design a use case where nested
same-type providers make the code cleaner, and explain
the pitfalls.

**Q3.** React Server Components (RSC) in React 18/Next.js
cannot use `useContext` because they run on the server,
not in the browser. Server Components cannot have state
or use hooks. But Client Components that use context work
as before. How does this affect the standard `AuthProvider`
pattern in a Next.js App Router application, where some
components run on the server and some on the client?
