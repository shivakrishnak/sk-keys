---
id: RCT-030
title: Prop Drilling Anti-Pattern
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-009, RCT-016, RCT-029
used_by: RCT-022, RCT-034, RCT-038, RCT-051
related: RCT-022, RCT-029, RCT-038
tags:
  - react
  - frontend
  - anti-pattern
  - state
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /react/prop-drilling-anti-pattern/
---

# RCT-030 - PROP DRILLING ANTI-PATTERN

⚡ TL;DR - Prop drilling is passing props through multiple
intermediate components that do not use them - only pass
them along to a deep descendant; it creates tight coupling,
makes refactoring painful, and is the primary motivation
for Context API, state management libraries, and component
composition patterns.

| #030 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Props, One-Way Data Binding, Lifting State Up | |
| **Used by:** | useContext Hook, useReducer Hook, State Management Decision Guide | |
| **Related:** | useContext Hook, Lifting State Up, Context API vs State Management | |

---

### 🔥 The Problem This Solves

**STATE PASSED THROUGH BYSTANDERS:**
Lifting state up solves sibling communication. But what
happens when the common ancestor is 4 levels above the
consuming component? Now every intermediate component
in between must accept and forward the props - even
though they do not use them at all.

```
App (owns user state)
  └── Layout (doesn't use user, just passes it down)
        └── MainContent (doesn't use user, just passes)
              └── Sidebar (doesn't use user, just passes)
                    └── UserAvatar (FINALLY uses user)
```

Layout, MainContent, and Sidebar are "bystanders." They
exist in the middle, forced to carry props they do not
care about. This is Prop Drilling - a symptom of the
one-way data flow model applied at scale without the
proper architectural response.

---

### 📘 Textbook Definition

**Prop Drilling** - the pattern (anti-pattern) in React
where data is passed as props through multiple component
layers, each of which passes the props to the next, until
the data reaches the component that actually needs it.
The intermediate components serve as conduits rather than
consumers. Symptoms: components with many props they do
not use, difficulty in renaming props (must update every
layer), tight coupling between unrelated components.
Solutions: Context API, state management libraries
(Redux/Zustand), component composition (children/render
props), or restructuring the component hierarchy.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// PROP DRILLING: passing user through 3 non-using layers
function App() {
  const [user] = useState({ name: 'Alice', role: 'admin' });
  return <Layout user={user} />;         // Layout doesn't use user
}
function Layout({ user }) {
  return <MainContent user={user} />;    // MainContent doesn't use user
}
function MainContent({ user }) {
  return <Sidebar user={user} />;        // Sidebar doesn't use user
}
function Sidebar({ user }) {
  return <UserAvatar user={user} />;     // UserAvatar uses it
}
function UserAvatar({ user }) {
  return <img src={user.avatar} alt={user.name} />;  // FINALLY used
}
```

Every intermediate component is coupled to the `user`
prop shape despite not using it.

---

### 🔩 First Principles Explanation

**WHY IT IS AN ANTI-PATTERN:**

```
COUPLING: Layout must know about the user prop to forward it.
  If user shape changes (user.name → user.displayName),
  you must update: App, Layout, MainContent, Sidebar,
  UserAvatar - five files for a one-field rename.

COGNITIVE OVERHEAD: Reading Layout code, you see a 'user'
  prop. Is Layout using it? You must trace down to find
  UserAvatar to understand why Layout has user at all.

TESTING: Testing Layout requires mocking user even though
  Layout does not use it.

REFACTORING: Moving UserAvatar to a different subtree
  requires finding a new common ancestor and re-threading
  the prop through a new chain.
```

**WHEN TO CALL IT DRILLING:**
There is no fixed rule. The React community generally
considers 2+ intermediate non-using layers to be "drilling."
One layer of forwarding (parent knows about child's needs)
is normal and acceptable. The question is: "Is this
component forwarding this prop purely to satisfy a
descendant's need, or does it legitimately need to know
about this data?"

**THE FOUR SOLUTIONS:**

```
1. CONTEXT API
   Move state into a context provider.
   Consumers anywhere in the tree read via useContext.
   Best: medium-frequency state changes,
         moderately large component trees.
   Cost: re-renders all consumers on every value change.

2. STATE MANAGEMENT (Redux/Zustand/Jotai)
   Store in a dedicated store outside React tree.
   Components connect/subscribe to only what they need.
   Best: large apps, complex state interactions, DevTools.
   Cost: boilerplate (Redux), learning curve.

3. COMPONENT COMPOSITION
   Restructure so the consuming component is passed as
   'children' or 'slots' - it renders "around" the
   intermediate components, bypassing them entirely.
   Best: layout/wrapper components.
   Cost: can invert the composition model awkwardly.

4. RESTRUCTURE COMPONENT HIERARCHY
   Move the consuming component closer to the state.
   Sometimes the problem is architectural, not technical.
   Best: caught early in design.
```

---

### 🧪 Thought Experiment

**THE THEME PROBLEM:**
A light/dark theme toggle is at the top of the app. The
theme value needs to reach every leaf component in the
tree (buttons, inputs, cards, text). Without Context,
this would require passing `theme` as a prop through
every single component in the app - every page, every
layout, every section.

This is why the theme is the canonical example used to
introduce Context. The theme is not owned by any specific
feature - it belongs to the app. No component in the
middle of the tree is responsible for the theme; they
only need to know their own color. Context makes the
theme globally available without any intermediate component
needing to forward it.

---

### 🧠 Mental Model / Analogy

> Prop drilling is like passing a message through a
> corporate phone tree. The CEO has a message for the
> intern. To get it there, the CEO tells it to the VP,
> who tells the Director, who tells the Manager, who
> tells the Team Lead, who tells the intern. The VP,
> Director, Manager, and Team Lead are bystanders -
> they do not need the message, they just forward it.
>
> Context is like a company-wide announcement system:
> the CEO posts the message to the announcement board.
> The intern reads it directly. No one in between needs
> to know.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
Prop drilling = passing props through components that
do not use them, only to reach a deeper component.
It creates tight coupling and makes refactoring painful.
Solutions: Context API for cross-tree sharing, state
libraries for global state.

**Level 2 (identification):**
Warning signs: a component has props in its function
signature that it never uses in its JSX or logic. Props
with the same name appearing in 3+ components in a chain.
A prop name change requires updating many files.

**Level 3 (solutions):**
Context API: create context, provide at the ancestor,
consume with `useContext` anywhere in the tree. Component
composition: restructure so that the consumer is passed
as `children` to the intermediate components (they render
it without knowing what it contains). State library:
separate state from the component tree entirely.

**Level 4 (trade-offs):**
Context creates a different coupling: all consumers are
coupled to the context shape. A context value change
re-renders all consumers simultaneously. Context is best
for truly cross-cutting concerns (theme, auth, locale).
For feature-specific state, component composition or
lifting to a narrower scope is preferable.

**Level 5 (mastery):**
The root cause of deep prop drilling is often a mismatch
between the component hierarchy and the data ownership
hierarchy. If a leaf component needs data from the root,
it suggests the leaf is doing something the root should
know about - or the root is owning data that a closer
ancestor should own. Solving prop drilling architecturally
(restructuring) is more durable than solving it
technically (adding Context). Dan Abramov described this
as: "Before you solve with Context, ask if you can solve
with composition."

---

### ⚙️ How It Works (Mechanism)

**Component composition pattern to avoid drilling:**

```jsx
// PROBLEM: passing user through Layout just for UserAvatar
// COMPOSITION SOLUTION: pass UserAvatar as children

// App provides UserAvatar as children - it has the user
function App() {
  const [user] = useState({ name: 'Alice', avatar: '...' });

  return (
    <Layout
      sidebar={<UserAvatar user={user} />}  // composed in
    >
      <MainContent />
    </Layout>
  );
}

// Layout does NOT receive user prop at all
// It just renders whatever was passed as sidebar
function Layout({ children, sidebar }) {
  return (
    <div className="layout">
      <aside>{sidebar}</aside>   {/* renders UserAvatar */}
      <main>{children}</main>
    </div>
  );
}

// UserAvatar is composed by App, which has user
// It never "drills through" Layout at all
function UserAvatar({ user }) {
  return <img src={user.avatar} alt={user.name} />;
}
```

**Context pattern:**

```jsx
// Context approach for broadly-shared state (theme, auth)
const UserContext = createContext(null);

function App() {
  const [user] = useState({ name: 'Alice' });
  return (
    <UserContext.Provider value={user}>
      <Layout />   {/* No user prop - Layout is clean */}
    </UserContext.Provider>
  );
}

function Layout() {
  return <MainContent />;  // No user prop passed
}

function UserAvatar() {
  const user = useContext(UserContext);  // reads directly
  return <img src={user.avatar} alt={user.name} />;
}
```

---

### 💻 Code Example

**BAD: Classic prop drilling:**

```jsx
// BAD: currentUser drilled through 3 non-using layers
function App() {
  const currentUser = { name: 'Alice', role: 'admin', avatar: '/alice.jpg' };
  return <Page currentUser={currentUser} />;
}
// Page doesn't use currentUser
function Page({ currentUser }) {
  return <Header currentUser={currentUser} />;
}
// Header doesn't use currentUser
function Header({ currentUser }) {
  return (
    <nav>
      <Logo />
      <UserMenu currentUser={currentUser} />
    </nav>
  );
}
// UserMenu finally uses it
function UserMenu({ currentUser }) {
  return (
    <div>
      <img src={currentUser.avatar} alt={currentUser.name} />
      <span>{currentUser.name}</span>
    </div>
  );
}
// If currentUser.name → currentUser.displayName, update 4 files
```

**GOOD: Context eliminates the drill:**

```jsx
// GOOD: create context for auth user (cross-cutting concern)
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const currentUser = { name: 'Alice', role: 'admin', avatar: '/alice.jpg' };
  return (
    <AuthContext.Provider value={currentUser}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

// App wraps everything with provider
function App() {
  return (
    <AuthProvider>
      <Page />
    </AuthProvider>
  );
}

// Page, Header: no currentUser prop needed
function Page() { return <Header />; }
function Header() {
  return <nav><Logo /><UserMenu /></nav>;
}

// UserMenu reads directly from context - no drilling
function UserMenu() {
  const currentUser = useAuth();  // direct read
  return (
    <div>
      <img src={currentUser.avatar} alt={currentUser.name} />
      <span>{currentUser.name}</span>
    </div>
  );
}
// currentUser.name → displayName: update AuthProvider + UserMenu only
```

---

### 📊 Comparison Table

| Solution | Best For | Re-render Cost | Complexity |
|---|---|---|---|
| Lift state | 1-2 level sharing, small trees | Low | Low |
| Component composition | Layout wrappers, slots | Low | Medium |
| Context API | Auth, theme, locale (app-wide, low-change) | Medium (all consumers) | Medium |
| Redux Toolkit | Large apps, complex state logic, DevTools needed | Selective (useSelector) | High |
| Zustand / Jotai | Medium apps, simpler API than Redux | Selective | Low-Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Context API completely eliminates prop drilling in all cases" | Context eliminates the forwarding problem but creates a different coupling: all consumers depend on the context shape and re-render when the context value changes. It trades prop coupling for context coupling. Not always the right solution. |
| "Passing props 2-3 levels is always prop drilling" | Passing props directly to a child that uses them is not drilling. Drilling means passing through layers that do not use the prop. Two layers of direct parent-child (each layer using the prop) is normal composition, not drilling. |
| "Redux prevents prop drilling" | Redux moves state out of the component tree entirely. Connected components read from the store directly without props. This bypasses the component tree, so it effectively eliminates drilling for global state - but it is not the right tool for component-local or feature-scoped state. |
| "Prop drilling is always a problem that must be solved" | For small component trees (3-4 levels max), prop drilling is acceptable and explicit - it is clear from the code what data flows where. Introducing Context or a library adds complexity. The trade-off depends on tree depth and how often the shape changes. |

---

### 🚨 Failure Modes & Diagnosis

**Context Over-used - Performance Regression**

**Symptom:** Typing in a form causes an unrelated sidebar
and navigation component to re-render, causing visible
lag.

**Root Cause:** The form's controlled input state was
placed in a Context value. Every consumer re-renders on
every value change. Text input fires onChange on every
keystroke - causing 30+ re-renders per second of all
context consumers.

**Fix:** Never put frequently-changing state (input values,
scroll position, mouse position) in Context. Context
is for low-frequency state changes (auth, theme, locale).
Keep input state local or use a state management library
with selective subscription (`useSelector` in Redux,
`useStore` in Zustand).

---

### 🔗 Related Keywords

**Prerequisites:**
- `Props and Component Communication` - the mechanism
  being overused in the drilling pattern
- `One-Way Data Binding` - the constraint that forces
  state ownership decisions
- `Lifting State Up` - the step that often leads to
  drilling when lifted too high

**Builds On:**
- `useContext Hook` - the primary React solution for
  avoiding drilling
- `Context API vs State Management Decision Guide` -
  when to use Context vs Redux vs Zustand
- `Redux Toolkit and Global State Architecture` - the
  full state management solution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SYMPTOM     │ Props in component signature not used     │
│             │ Same prop name in 3+ component layers     │
│             │ Renaming prop requires updating 4+ files  │
├──────────────────────────────────────────────────────────┤
│ SOLUTION 1  │ Context API: createContext + Provider +   │
│             │ useContext - best for auth/theme/locale    │
│ SOLUTION 2  │ Composition: pass consumer as children    │
│             │ or slot prop to bypass intermediate layers│
│ SOLUTION 3  │ State library: Redux/Zustand for global   │
│             │ state with selective subscription         │
│ SOLUTION 4  │ Restructure hierarchy to co-locate state  │
├──────────────────────────────────────────────────────────┤
│ AVOID       │ Context for high-frequency state changes  │
│             │ Context for feature-specific state        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Prop drilling = props passed through components that
   do not use them. Symptom: bystander components with
   irrelevant props in their signature.
2. Solutions: Context (cross-cutting concerns), component
   composition (layout wrappers), state library (global).
3. Context re-renders ALL consumers on change - never
   put fast-changing state (input values) in Context.

**Interview one-liner:**
"Prop drilling is passing props through intermediate
components that do not use them, creating tight coupling
and making refactoring painful. The primary solutions
are: Context API for cross-cutting concerns (auth, theme)
by wrapping with a Provider and reading via useContext;
component composition to pass consumers as children
bypassing intermediates; or a state library for global
state. Context trades prop coupling for context coupling
and re-renders all consumers - never put high-frequency
state (keystroke-level) in Context."

---

### 💎 Transferable Wisdom

Prop drilling is a manifestation of the "shotgun surgery"
code smell from object-oriented design: one change requires
modifying many different places. In OOP: changing a method
signature requires updating all callers. In React: renaming
a prop requires updating all the drilling intermediaries.
The cure in OOP is to encapsulate the change behind an
interface. The cure in React is to encapsulate via Context
or composition. The pattern - "one logical change should
touch minimal files" - applies universally: database schema
changes, API contract changes, config format changes.
Reducing the blast radius of changes is a core
maintainability discipline.

---

### 💡 The Surprising Truth

The React team's guidance is: "Before reaching for Context,
try to solve with component composition first." The
composition approach is often overlooked. If `<UserAvatar>`
is passed as `children` or a prop to `<Layout>`, then
Layout never needs to know about the user. The App
component, which owns user, passes `<UserAvatar user={user} />`
directly. This completely solves the drilling without
any global state or Context. Dan Abramov's 2019 tweet
explaining this (showing how many "Context needed!" cases
are actually "pass it as children" cases) became one of
the most referenced React architecture discussions. The
insight: Context solves "I need to reach across the tree."
Composition solves "I need to reach through the tree."
These are different shapes of the same problem.

---

### ✅ Mastery Checklist

1. **IDENTIFY** all drilling paths in a given component
   tree diagram and propose the correct solution for each
   based on the nature of the state (auth, local feature,
   high-frequency input).
2. **REFACTOR** a prop-drilled auth user (5 levels deep)
   using both composition and Context, and articulate why
   you would choose one over the other for this specific case.
3. **DEMONSTRATE** the performance cost of Context with
   high-frequency state by placing keystroke-level input
   state in Context and profiling with React DevTools.
4. **EXPLAIN** Dan Abramov's "solve with composition
   first" approach with a concrete before/after code
   example using the `children` prop pattern.
5. **DECIDE** for three different scenarios (auth user,
   form input value, shopping cart items) which solution
   is most appropriate and why.

---

### 🧠 Think About This Before We Continue

**Q1.** "All state that is shared across more than one
component should be in Redux." This is a rule some teams
adopt. What is the consequence of applying this rule
strictly? What kinds of state would end up in Redux that
should arguably stay local, and what does that do to
component re-render behaviour, testability, and cognitive
load?

**Q2.** Jotai and Recoil are "atomic" state management
libraries. Instead of one global store, each piece of
state is an "atom" that components subscribe to individually.
This directly addresses the Context re-render problem
(only components using that specific atom re-render).
How does the atomic model compare to the Context model
for the prop drilling problem specifically? When would
you choose one over the other?

**Q3.** React Server Components (RSC) in Next.js change
the prop drilling picture: data fetching happens on the
server in server components, and props flow downward from
there. In an RSC architecture, server components do not
re-render (they run once on the server). Does prop drilling
still matter in an RSC world? Where does it matter most?