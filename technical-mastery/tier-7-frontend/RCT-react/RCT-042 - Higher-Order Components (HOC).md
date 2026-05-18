---
id: RCT-042
title: "Higher-Order Components (HOC)"
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-005, RCT-010, RCT-021
used_by: RCT-043, RCT-044, RCT-047
related: RCT-043, RCT-044, RCT-024
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
nav_order: 42
permalink: /technical-mastery/react/higher-order-components/
---

⚡ TL;DR - A Higher-Order Component is a function that
takes a component and returns a new enhanced component;
it is a code reuse pattern for cross-cutting concerns
(auth gating, logging, data injection); HOCs were the
primary composition pattern in class components and are
largely replaced by custom hooks in functional components,
but remain relevant for component-level concerns that
hooks cannot express (wrapping component lifecycle).

| #042            | Category: React                                                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | React Components, React.memo, useEffect Hook                        |                 |
| **Used by:**    | Render Props Pattern, Compound Components, Class to Hooks Migration |                 |
| **Related:**    | Render Props Pattern, Compound Components, Custom Hooks             |                 |

---

### 🔥 The Problem This Solves

**CODE REUSE ACROSS COMPONENTS - PRE-HOOKS:**
Before hooks (React < 16.8), component logic lived in
class component lifecycle methods. Sharing that logic
between components required either: copy/paste, HOCs,
or Render Props. HOCs became the standard pattern for
"wrapping" a component with cross-cutting behaviour:

- Auth checking before rendering (redirect if not logged in)
- Error handling (wrap component to catch render errors)
- Analytics event logging on mount/unmount
- Data injection (connect() in early Redux)

In 2024, custom hooks solve most of these for functional
components. But HOCs are still the ONLY option when:

- The enhancement must be at the component (tree) level
  (you cannot use a hook to wrap another component's render)
- Working with class components
- Using third-party libraries that provide HOC APIs

---

### 📘 Textbook Definition

**Higher-Order Component (HOC)** - a function that accepts
a React component and returns a new React component:
`const EnhancedComponent = higherOrderComponent(WrappedComponent)`.
It is an application of the higher-order function pattern
from functional programming applied to React components.
HOCs are pure functions - they do not modify the input
component; they compose a new component around it.
Convention: HOC functions are named `withXxx` (e.g.,
`withAuth`, `withLogger`, `withData`).

---

### ⏱️ Understand It in 30 Seconds

```jsx
// withAuth HOC: redirects to login if not authenticated
function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const { isAuthenticated, user } = useAuth();
    if (!isAuthenticated) {
      return <Navigate to="/login" />;
    }
    // Passes all original props through + adds user
    return <WrappedComponent {...props} user={user} />;
  };
}

// Usage: enhance any component with auth check
const ProtectedDashboard = withAuth(Dashboard);
const ProtectedSettings = withAuth(Settings);

// ProtectedDashboard: redirects if not logged in,
//                     renders Dashboard if logged in
```

---

### 🔩 First Principles Explanation

**HIGHER-ORDER FUNCTIONS → HIGHER-ORDER COMPONENTS:**

```
Higher-order function (JavaScript):
  const double = (fn) => (x) => fn(x * 2);
  const addOne = (x) => x + 1;
  const doubleThenAddOne = double(addOne);  // fn → fn

Higher-order component (React):
  const withLogging = (Component) => {
    return (props) => {
      useEffect(() => {
        console.log(`${Component.displayName} mounted`);
        return () => console.log(`unmounted`);
      }, []);
      return <Component {...props} />;  // render original
    };
  };
  const LoggedButton = withLogging(Button);  // Component
    → Component
```

**Key structural property:**

```
HOC contract:
  - Input:  a React component (any - class or functional)
  - Output: a new React component
  - Rule:   MUST spread all original props through to
    wrapped component
  - Rule:   MUST forward refs if needed (using forwardRef)
  - Rule:   MUST not mutate the input component
  - Rule:   Should copy static methods
    (hoistNonReactStatics)
```

---

### 🧪 Thought Experiment

**THE WRAPPER HELL PROBLEM:**
A component needs auth, analytics, error logging, and
a loading state injected. With HOCs:

```jsx
const EnhancedPage =
    withAuth(withAnalytics(withLogger(withData(Page))));
```

This is nested HOC composition. Reading the order: `Page`
is passed to `withData` first (innermost), then `withLogger`,
then `withAnalytics`, then `withAuth` (outermost). The
execution order during render is outermost first.

This is "HOC wrapper hell" - the component tree shows
4 nested wrappers in React DevTools, debugging is harder,
and prop naming conflicts can silently override each other.

The custom hook equivalent:

```jsx
function Page() {
  const { isAuthenticated } = useAuth();
  const analytics = useAnalytics();
  const logger = useLogger();
  const data = usePageData();
  // No nesting, no prop forwarding, no wrapper hell
}
```

This is why hooks replaced HOCs for most use cases.

---

### 🧠 Mental Model / Analogy

> An HOC is like a glass case in a museum. The artefact
> (WrappedComponent) is placed inside, unchanged. The case
> adds protection and lighting (the HOC's enhancement)
> without modifying the artefact itself.
>
> Each HOC is another case - you can nest cases, but
> the artefact remains the original component deep inside.
>
> The problem: too many nested cases make it hard to see
> the actual artefact (deep nesting in React DevTools)
> and hard to reach inside (debugging).

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
A function that takes a component, returns a new one.
Used for cross-cutting concerns: auth, logging, error
handling. Named `withXxx` by convention.

**Level 2 (usage):**
Always spread `{...props}` to the wrapped component.
Display name convention: set `WrapperComponent.displayName`
for DevTools readability. Name the HOC clearly in DevTools.

**Level 3 (vs hooks):**
Custom hooks replace HOCs for LOGIC reuse (stateful logic,
effects). HOCs are still needed for COMPONENT-level
wrapping: adding lifecycle at the component boundary,
catching errors (`withErrorBoundary` pattern), or when
wrapping class components that cannot use hooks.

**Level 4 (ref forwarding):**
HOCs break ref forwarding. When a parent passes a `ref`
to `<EnhancedComponent ref={ref}>`, the ref lands on
the HOC wrapper, not the wrapped component. Fix: use
`React.forwardRef` in the HOC:

```jsx
function withAuth(WrappedComponent) {
  const AuthComponent = React.forwardRef((props, ref) => {
    // ...auth logic
    return <WrappedComponent {...props} ref={ref} />;
  });
  AuthComponent.displayName =
      `withAuth(${getDisplayName(WrappedComponent)})`;
  return AuthComponent;
}
```

**Level 5 (mastery):**
HOC composition is function composition: `compose(f, g, h)(x)`
= `f(g(h(x)))`. Libraries like Recompose (deprecated) and
Redux's original `connect()` were built on HOC composition.
Redux v7+ uses hooks (`useSelector`, `useDispatch`). The
shift reflects the broader principle: prefer flat hook
composition over nested component wrapping when both
achieve the same goal. HOCs remain the correct choice
when the library API you consume only provides an HOC
interface (react-router's `withRouter` before hooks,
MobX's `observer()`, some analytics libraries).

---

### ⚙️ How It Works (Mechanism)

**HOC with ref forwarding and displayName:**

```jsx
import React from "react";
import { hoistNonReactStatics } from "hoist-non-react-statics";

function withPermission(requiredPermission) {
  return function (WrappedComponent) {
    // forwardRef so HOC does not break ref passing
    const PermissionComponent = React.forwardRef(
      function PermissionWrapper(props, ref) {
        const { permissions } = usePermissions();

        if (!permissions.includes(requiredPermission)) {
          return <UnauthorizedMessage />;
        }

        return <WrappedComponent {...props} ref={ref} />;
      },
    );

    // Display name for React DevTools
    PermissionComponent.displayName = `withPermission(${
      WrappedComponent.displayName || WrappedComponent.name
    })`;

    // Copy static methods from WrappedComponent
    // (e.g. getInitialProps in Next.js pages)
    hoistNonReactStatics(PermissionComponent, WrappedComponent);

    return PermissionComponent;
  };
}

// Usage (curried, allows pre-configuring the permission):
const AdminOnly = withPermission("admin");
const EditPost = AdminOnly(PostEditor);
```

---

### 💻 Code Example

**BAD: HOC that mutates the wrapped component:**

```jsx
// BAD: mutates the input component (violates HOC contract)
function withLogger(WrappedComponent) {
  // Directly modifying the prototype - mutation!
  WrappedComponent.prototype.componentDidMount = function () {
    console.log("mounted");
  };
  // Returns the SAME component, not a new one
  return WrappedComponent; // mutation: breaks composability
}
// Problem: if another HOC does the same mutation, one
// will silently overwrite the other's componentDidMount
```

**GOOD: HOC that wraps without mutating:**

```jsx
// GOOD: creates a NEW component, original unchanged
function withLogger(WrappedComponent) {
  function LoggedComponent(props) {
    useEffect(() => {
      const name =
          WrappedComponent.displayName || WrappedComponent.name;
      console.log(`${name} mounted`);
      return () => console.log(`${name} unmounted`);
    }, []);

    return <WrappedComponent {...props} />;
  }

  LoggedComponent.displayName = `withLogger(${
    WrappedComponent.displayName || WrappedComponent.name
  })`;

  return LoggedComponent;
}
// Original component is UNCHANGED - composable with other HOCs
```

---

### 📊 Comparison Table

|                             | HOC                         | Custom Hook       | Render Props             |
| --------------------------- | --------------------------- | ----------------- | ------------------------ |
| Wraps component lifecycle   | Yes                         | No                | No                       |
| Can use hooks internally    | Yes (if functional wrapper) | Yes               | Yes (if functional)      |
| Visible in React DevTools   | Yes (as wrapper)            | No (logic only)   | Yes (as render function) |
| Works with class components | Yes                         | No                | Yes                      |
| Prop naming conflicts       | Possible                    | No                | No                       |
| Ref forwarding              | Requires forwardRef         | N/A               | N/A                      |
| Composition                 | Nested (wrapper hell)       | Flat (hook calls) | Nested JSX               |
| Best for                    | Component-level wrapping    | Logic reuse       | Render-time injection    |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "HOCs are deprecated and should never be used"   | HOCs are not deprecated - they remain the correct pattern for component-level wrapping (auth gating, error boundaries, class component integration). Many third-party libraries still expose HOC APIs. Custom hooks are preferred for logic reuse but cannot replace HOCs for all use cases.                                       |
| "HOCs and hooks are interchangeable"             | They solve different problems. Hooks share STATEFUL LOGIC between components - the calling component owns the state. HOCs share COMPONENT BEHAVIOUR - the HOC wrapper controls rendering (can block render, add lifecycle). Use hooks when you want the component to own the logic. Use HOCs when you want to intercept rendering. |
| "Props are automatically forwarded through HOCs" | Only if you explicitly spread `{...props}`. A HOC that does not spread props will silently swallow all props passed to the enhanced component - the wrapped component receives nothing. This is a common bug.                                                                                                                      |
| "HOCs defined inside a component are fine"       | Defining an HOC inside a component means React sees a NEW component type on every render (the HOC function recreates a new function each time). React will unmount and remount the wrapped component on every render. HOCs must always be defined at the module level.                                                             |

---

### 🚨 Failure Modes & Diagnosis

**HOC Defined Inside a Component - Full Remount on Every Render**

**Symptom:** A component wrapped by an HOC loses all
state and DOM focus on every parent render.

**Root Cause:**

```jsx
// BAD: HOC defined inside a render function
function ParentComponent() {
  // New function reference on every render!
  const WithAuth = withAuth(DashboardPage);
  // React sees a NEW component type on every render
  // Unmounts old DashboardPage, mounts new DashboardPage
  return <WithAuth />;
}
```

**Fix:** Move HOC creation to module level:

```jsx
// GOOD: HOC created once at module level
const AuthenticatedDashboard = withAuth(DashboardPage);

function ParentComponent() {
  return <AuthenticatedDashboard />;
  // Stable component type → no remount
}
```

---

**Prop Name Collision - Silent Override**

**Symptom:** A prop passed to the enhanced component is
silently overridden by the HOC with a different value.

**Root Cause:** HOC injects a prop with the same name
as a prop passed from the parent:

```jsx
// HOC injects 'data' prop:
return <WrappedComponent {...props} data={fetchedData} />;
// If parent also passes data={parentData}:
// {data: parentData, ...injectedData} → injectedData wins
// Silent override - no error, wrong value
```

**Fix:** Use specific prop names. Design HOCs to use
prefixed or namespaced props. Document injected props.

---

### 🔗 Related Keywords

**Prerequisites:**

- `React Components` - component composition fundamentals
- `React.memo` - HOC composition with memoisation
- `useEffect Hook` - HOCs often contain lifecycle effects

**Builds On:**

- `Render Props Pattern` - alternative composition pattern
  that avoids HOC nesting
- `Custom Hooks` - the modern replacement for HOC logic reuse
- `Class Components to Hooks Migration` - migrating HOC-heavy code

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION │ (Component) => EnhancedComponent           │
│ CONVENTION │ Named withXxx (withAuth, withLogger)       │
│ CONTRACT   │ Spread {...props}, never mutate input      │
├─────────────────────────────────────────────────────────┤
│ DISPLAY    │ Set .displayName for DevTools              │
│ REFS       │ Use React.forwardRef to pass refs through  │
│ STATICS    │ Use hoist-non-react-statics to copy methods│
├─────────────────────────────────────────────────────────┤
│ AVOID      │ HOC defined inside component (remount bug) │
│ REPLACE    │ Use custom hook for logic reuse instead    │
│ KEEP       │ HOC for component-level interception       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. HOC = function that takes a component, returns a new
   enhanced component. MUST spread `{...props}` through.
2. Never define an HOC inside a render function - it
   creates a new component type every render, causing
   full remounts.
3. Custom hooks replaced HOCs for logic reuse. HOCs
   remain for component-level wrapping (auth gating,
   error boundaries, third-party library integration).

**Interview one-liner:**
"A Higher-Order Component is a function that accepts a
component and returns a new enhanced component. It is
a composition pattern for cross-cutting concerns like
auth gating, analytics, and error handling. Key rules:
spread `{...props}` through to the wrapped component,
set `displayName` for DevTools, use `forwardRef` for
refs. HOCs were the primary code reuse pattern in class
components but are largely replaced by custom hooks for
logic reuse. They remain the only option for component-
level wrapping: intercepting render, adding class
component lifecycle, or integrating third-party HOC APIs."

---

### 💎 Transferable Wisdom

HOCs are React's application of the Decorator Pattern
from classical software engineering: adding behaviour to
an object without modifying the object itself. The same
principle applies across languages: Java's Spring AOP
(aspect-oriented programming) proxies add cross-cutting
behaviour (transaction management, security checks) to
methods without modifying the method body. Python
decorators wrap functions with additional behaviour.
Middleware in Express.js wraps request handlers. The
core trade-off is the same in all cases: the wrapped
subject is unmodified (good for separation of concerns)
but the composition nesting can grow (wrapper hell for
multiple cross-cutting concerns). The solution is also
consistent: flatten composition where possible (hooks,
AOP advice chains, middleware arrays).

---

### 💡 The Surprising Truth

React's most famous HOC, `connect()` from React-Redux,
was the primary way to consume the Redux store for years.
Dan Abramov (co-creator of both Redux and Redux's hooks
API) has said that if he were building Redux today, he
would not use HOCs - he would design it with hooks
(`useSelector`, `useDispatch`) from the start. The HOC
pattern was state-of-the-art in 2015-2018 and is now
considered legacy. Yet `connect()` still exists in
React-Redux v8+ (alongside hooks) for backward
compatibility. This illustrates a key reality of large
React codebases: HOCs from years ago coexist with modern
hooks code. Understanding HOCs is essential for
maintaining and migrating legacy React code, even if you
would not write a new one today.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a `withAuth(WrappedComponent)` HOC that
   reads authentication state, redirects to `/login` if
   not authenticated, and passes the user object as a
   prop to the wrapped component.
2. **DEMONSTRATE** the displayName + forwardRef pattern:
   an HOC that sets a correct display name and correctly
   forwards refs to the wrapped component. Verify both
   in React DevTools.
3. **DEMONSTRATE** the HOC-inside-component bug: show the
   remount (state reset on every parent render) and then
   fix it by moving the HOC to module level.
4. **COMPARE** an HOC-based solution vs a custom hook
   solution for the same cross-cutting concern (e.g.,
   logging component mount/unmount). Explain when each
   is appropriate.
5. **IDENTIFY** prop name collisions: create two HOCs that
   both inject a prop named `data`. Show what happens
   when both wrap the same component. Explain the fix.

---

### 🧠 Think About This Before We Continue

**Q1.** React Error Boundaries are class components that
must implement `componentDidCatch` or `getDerivedStateFromError`.
You cannot write an Error Boundary as a functional
component. But you CAN write a `withErrorBoundary(Component)`
HOC that wraps any component in an Error Boundary class.
Write the `withErrorBoundary` HOC. What parameters
should it accept? How does it differ from placing an
`<ErrorBoundary>` element directly in JSX?

**Q2.** TypeScript users often struggle with HOC types.
The wrapped component accepts props `P`. The HOC injects
additional props `InjectedProps`. The enhanced component
should accept `Omit<P, keyof InjectedProps>` (props minus
the injected ones). Write the TypeScript generic type
signature for `withAuth(WrappedComponent: React.ComponentType<P>)`.
What are the edge cases in the type system?

**Q3.** Some libraries (React-Redux, MobX React) provide
BOTH HOC and hook APIs. The HOC API came first. When a
new developer joins a codebase using the HOC API, should
they migrate to hooks? What is the risk of having both
patterns in the same codebase? How would you make the
migration decision?
