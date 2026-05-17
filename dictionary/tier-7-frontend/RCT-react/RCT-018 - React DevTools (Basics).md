---
id: RCT-018
title: React DevTools (Basics)
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007, RCT-009, RCT-010
used_by: RCT-055, RCT-060
related: RCT-007, RCT-010, RCT-055
tags:
  - react
  - frontend
  - devtools
  - debugging
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /react/react-devtools-basics/
---

# RCT-018 - REACT DEVTOOLS (BASICS)

⚡ TL;DR - React DevTools is a browser extension that adds
two panels to Chrome/Firefox DevTools: Components (inspect
the React component tree, props, state, and context) and
Profiler (record and analyse renders to diagnose performance
problems).

| #018 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Component, Props, State | |
| **Used by:** | React Performance Profiling, Core Web Vitals | |
| **Related:** | Component, State, React Performance Profiling | |

---

### 🔥 The Problem This Solves

**WITHOUT REACT DEVTOOLS:**
React components are invisible in the browser's built-in
DevTools. The DOM inspector shows raw HTML elements -
there is no way to see which React component rendered a
given element, what props it received, what its current
state is, or whether it re-rendered unnecessarily.
Debugging a React app without DevTools means adding
`console.log` statements everywhere and rerunning the
code, which is slow and cannot show the component tree
structure or live state at any moment in time.

React DevTools provides a live, interactive view of the
React component tree, letting you inspect, modify, and
understand your application's React-specific state at any
point without code changes.

---

### 📘 Textbook Definition

**React DevTools** is an official browser extension
(available for Chrome, Firefox, and Edge) that extends
the browser's developer tools with React-specific
inspection capabilities. It provides two core panels:

**Components panel:** A tree view of the React component
hierarchy. Click any component to inspect its current
props, state, context values, hooks values, and the source
file location. You can modify props and state values
directly from the panel to test how the UI responds.

**Profiler panel:** Records React renders during a
session and shows which components rendered, how long each
render took, and why each component rendered (prop change,
state change, context change, parent re-render). Used to
diagnose performance problems and unnecessary re-renders.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
React DevTools adds a "Components" view to browser DevTools
showing the live React tree with props, state, and context
values, and a "Profiler" view showing render performance.

**Installation:**
1. Chrome: install "React Developer Tools" from Chrome Web Store
2. Firefox: install from Firefox Add-ons
3. Edge: install from Microsoft Edge Add-ons
4. Open browser DevTools (F12) → look for "Components" and
   "Profiler" tabs

**Key workflows:**
- Inspect a component: click any DOM element in Elements tab
  → switch to Components tab → React DevTools shows the
  corresponding component
- Find why a component re-rendered: Profiler tab → Record
  → interact → Stop → click any highlighted component

---

### 🔩 First Principles Explanation

**WHAT DEVTOOLS EXPOSES:**

```
For each component in the tree, React DevTools shows:

PROPS     - current values of all received props
STATE     - current useState values (labelled if named)
CONTEXT   - context values this component consumes
HOOKS     - current values of all hooks in order
SOURCE    - file path and line number (dev mode only)
RENDERS   - how many times this component rendered
PROFILER  - time spent in render (from Profiler panel)
```

**HOW IT WORKS:**
React DevTools communicates with React's internal
"DevTools hook" - a debug interface that React exposes
in development mode. This hook provides the component tree,
state snapshots, and render events. It does NOT work
on minified production builds (React removes the debug
interface in production for performance and security).

---

### 🧠 Mental Model / Analogy

> React DevTools is to React components what the browser's
> DOM inspector is to HTML elements. The DOM inspector
> shows the current state of HTML elements with their
> attributes. React DevTools shows the current state of
> React components with their props and state. One level
> up in abstraction: HTML describes structure, React
> components describe the application.

```
Chrome DevTools Panels (after React DevTools installed):

  Elements     │ DOM tree (HTML, attributes, styles)
  Console      │ JavaScript logs and REPL
  Network      │ HTTP requests and responses
  Sources      │ JavaScript source files, breakpoints
  React        │  ← Components: React tree, props, state
               │  ← Profiler: render timing and causes
  Performance  │ Browser performance timeline
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
React DevTools is a browser extension that lets you see
your React component tree, inspect what props and state
each component has, and find performance problems.

**Level 2 (usage):**
Install the extension. Open browser DevTools. Use the
"Components" tab to click on components and see their
props and state. Double-click a prop/state value to
edit it live. Use the "Profiler" tab to record renders
and see which components re-rendered and why.

**Level 3 (mechanism):**
React DevTools connects to React's internal devtools
hook (`__REACT_DEVTOOLS_GLOBAL_HOOK__`). This hook is
injected by React in development mode. The hook exposes
events: component mount, update, unmount, along with
the Fiber tree (React's internal component representation).
DevTools listens to these events and builds its visual
tree. All hook data is removed in production builds
(no debug overhead in production).

**Level 4 (productivity):**
The Profiler's "Why did this component render?" feature
is the most productive debugging tool for React performance.
It labels each render with: Props changed (shows which
prop), State changed (shows which state), Context changed,
Hooks changed, or Parent re-rendered. This replaces hours
of manual debugging with a one-click diagnosis. Combined
with React.memo, useCallback, and useMemo, the Profiler
reveals exactly which memoisation is missing or ineffective.

**Level 5 (mastery):**
React DevTools exposes Fiber tree internals. Each component
in the tree corresponds to a Fiber node (React's internal
work unit in the React Fiber architecture). The DevTools
shows alternates (the "work-in-progress" Fiber during
concurrent rendering), suspended components, lazy-loaded
components, and error boundary states. Understanding
the DevTools at this level helps diagnose Concurrent Mode
issues, Suspense boundary behaviour, and hydration errors.

---

### ⚙️ How It Works (Mechanism)

**Components Panel Workflows:**

```
1. FIND COMPONENT FOR DOM ELEMENT:
   - Right-click any element in the page
   - Choose "Inspect" → Elements tab opens
   - Click the React logo icon in the toolbar
   - React DevTools jumps to that component in Components tab

2. INSPECT COMPONENT:
   - Click component name in tree
   - Right panel shows: props, state, hooks, context
   - Collapse/expand to navigate large trees
   - Search bar at top filters by component name

3. EDIT LIVE:
   - Click any prop or state value in right panel
   - Double-click to edit inline
   - Press Enter to apply - component re-renders immediately
   - Useful for testing edge cases (empty strings, null values)

4. NAVIGATE TO SOURCE:
   - Click the "<>" icon next to a component
   - Browser Sources tab opens to the component definition

5. TRIGGER RE-RENDER:
   - Right-click a component in tree
   - "Force update" - causes that component to re-render
```

**Profiler Panel Workflows:**

```
1. RECORD A SESSION:
   - Click the Record button (circle icon)
   - Interact with the app (click buttons, type, navigate)
   - Click Stop Recording

2. READ THE FLAMEGRAPH:
   - Each column = one render commit
   - Each row = component depth
   - Width = time spent in that component's render
   - Grey = did not render this commit
   - Coloured = rendered this commit
   - Darker colour = more time spent

3. "WHY DID THIS RENDER?":
   - Click any coloured cell in flamegraph
   - Right panel shows: "This component rendered because..."
   - Lists: props that changed, state that changed, context change

4. RANKED CHART:
   - Shows components sorted by render time
   - Quickly identifies the most expensive renders
```

---

### 💻 Code Example

**Setting displayName for DevTools readability:**

```jsx
// BAD: anonymous function components show as "Component"
// in DevTools - harder to navigate large trees
export default memo(function({ title }) {
  return <h1>{title}</h1>;
});

// GOOD: named components show their name in DevTools
function ArticleHeader({ title }) {
  return <h1>{title}</h1>;
}
export default memo(ArticleHeader);
// DevTools shows "Memo(ArticleHeader)" in the tree
```

**Custom hook naming for DevTools visibility:**

```jsx
// BAD: hooks show values but no label in DevTools
function useData() {
  const [data, setData] = useState(null);
  // DevTools shows: State: null (no label)
  return { data, setData };
}

// GOOD: labelled state shows in DevTools
function useUserData(userId) {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(false);
  // DevTools shows hook names and values separately
  // Makes it easier to find the right value

  // Optional: use useDebugValue for hook-level label
  // (React DevTools only shows this for custom hooks)
  return { userData, loading };
}
```

**Adding debug context with useDebugValue:**

```jsx
import { useState, useDebugValue } from 'react';

function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // useDebugValue adds a label to this hook in DevTools
  // Shows as "Online" or "Offline" next to the hook
  useDebugValue(isOnline ? 'Online' : 'Offline');

  // (event listeners omitted for brevity)
  return isOnline;
}

// In DevTools, component using this hook shows:
// useOnlineStatus: "Online"
// instead of:
// State: true
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "React DevTools shows all components, including production builds" | React DevTools requires development mode. In production builds (`npm run build`), React removes all DevTools hooks for performance and to avoid exposing component structure. DevTools shows nothing for production builds. |
| "The 'Components' tab shows the DOM structure" | The Components tab shows the React component tree, not the DOM. One React component may render multiple DOM elements. Fragments render multiple DOM nodes with no component wrapper. The component tree is an abstraction above the DOM. |
| "Editing state in DevTools persists after page refresh" | Edits in DevTools are in-memory only. Refreshing the page resets to the initial state. DevTools editing is for live inspection and testing, not for permanent changes. |
| "The Profiler panel is for measuring actual user performance" | The Profiler measures React render performance in the developer's browser during a DevTools session. It does not reflect real user performance metrics (which require RUM tools like Datadog, Sentry, or Web Vitals measurement). |

---

### 🚨 Failure Modes & Diagnosis

**"React DevTools not installed" Banner in Production**

**Symptom:** Users see a banner saying React DevTools
is not installed when visiting the app.

**Root Cause:** `process.env.NODE_ENV !== 'production'`
check missing. Development-only code running in production.

**Fix:** Ensure `npm run build` (not `npm start`) is used
for production deployment. The build process sets NODE_ENV
to "production" which removes the DevTools hint.

---

**Profiler Shows 100% Re-renders (Every Component Re-renders)**

**Symptom:** Every render commit in the Profiler shows
every component highlighted, suggesting full tree re-render.

**Root Cause 1:** Root-level state changes that cause the
top-level component to re-render, which cascades to all
children (without React.memo protection).

**Root Cause 2:** Context value changes (new object
reference on every render) that all consumers re-render
for.

**Diagnostic:** Click the top-level component in the
Profiler. "Why did this render?" shows State changed or
Context changed. Trace down to find the source.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Component` - the unit displayed in the Components tab
- `Props` and `State` - the values inspected in DevTools
- `React Development Environment Setup` - DevTools
  requires development mode

**Used With:**
- `React Performance Profiling` - advanced Profiler use
- `React.memo, useMemo, useCallback` - the tools applied
  after Profiler identifies unnecessary re-renders

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INSTALL    │ Chrome/Firefox/Edge extension store        │
│            │ Search: "React Developer Tools"            │
├──────────────────────────────────────────────────────────┤
│ COMPONENTS │ Inspect props, state, context, hooks       │
│ TAB        │ Double-click to edit values live           │
│            │ "<>" icon: jump to source file             │
├──────────────────────────────────────────────────────────┤
│ PROFILER   │ Record → interact → stop                   │
│ TAB        │ Flamegraph: width=time, colour=rendered    │
│            │ "Why did this render?": per-component      │
├──────────────────────────────────────────────────────────┤
│ DEV ONLY   │ Production builds have no DevTools support │
├──────────────────────────────────────────────────────────┤
│ TIPS       │ Name your components (not anonymous)       │
│            │ Use useDebugValue in custom hooks          │
│            │ Check Profiler BEFORE adding memoisation   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Components tab: see the React tree, inspect/edit props
   and state live, navigate to source.
2. Profiler tab: record renders, see "Why did this
   component render?" for every component.
3. Only works in development mode - production builds have
   no DevTools support.

**Interview one-liner:**
"React DevTools is a browser extension adding two panels:
Components (inspect the React tree, props, state, hooks,
context, and edit values live for testing) and Profiler
(record renders, see which components rendered and why,
diagnose unnecessary re-renders). It connects to React's
internal devtools hook available only in development mode -
production builds have no DevTools overhead or exposure."

---

### 💎 Transferable Wisdom

React DevTools follows the "make the invisible visible"
principle of good developer tooling. React's component
model is entirely invisible to standard browser DevTools.
The extension solves this by exposing the framework's
internal model. This pattern of framework-specific DevTools
appears across the ecosystem: Vue DevTools, Redux DevTools,
Angular Augury, and Apollo Client DevTools all follow
the same principle: attach to the framework's debug hook
and visualise the invisible framework state that developers
need to understand.

---

### 💡 The Surprising Truth

React DevTools' Profiler works by injecting timing code
around every component render. This instrumentation itself
has performance cost - React renders are measurably slower
with DevTools open than without. This means Profiler
results show relative render costs correctly (component A
is 3x slower than component B) but absolute timings are
inflated. Never use Profiler timings as the performance
baseline for real user performance. Use Web Vitals
measurement in production for that.

---

### ✅ Mastery Checklist

1. **FIND** any component in a running React app using
   DevTools: right-click element → Inspect → switch to
   Components tab and navigate to the component.
2. **DIAGNOSE** a prop drilling issue by using the
   Components panel to trace which ancestor owns a piece
   of state and which intermediate components pass it
   without using it.
3. **PROFILE** a specific user interaction using the
   Profiler panel, identify the top 3 most expensive
   component renders, and explain what caused each.
4. **IDENTIFY** an unnecessary re-render using "Why did
   this component render?" and apply the correct fix
   (React.memo, useCallback, or useMemo).
5. **EXPLAIN** why a component shows as "Unknown" or
   anonymous in DevTools and how to fix it with named
   function expressions or displayName.

---

### 🧠 Think About This Before We Continue

**Q1.** The Profiler shows that `ProductList` re-renders
every time any state in the parent `App` changes, even
state that is not passed to `ProductList`. What are the
three ways to prevent this, and what are the trade-offs
of each?

**Q2.** React DevTools shows the component tree in the
"development" order that React processes components.
In Concurrent Mode (React 18), React may work on multiple
trees simultaneously (the current tree and the work-in-
progress tree). How might Concurrent Mode change what
you see in the DevTools component tree, and what does
it mean when a component shows as "suspended"?

**Q3.** A team member argues: "React DevTools shows state
values, so I do not need to add logging or unit tests -
I can just inspect state visually in DevTools while
testing manually." What is wrong with this argument, and
what combination of tooling (DevTools + testing + logging)
provides the most reliable development workflow?