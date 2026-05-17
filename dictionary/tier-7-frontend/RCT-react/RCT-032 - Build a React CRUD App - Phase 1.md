---
id: RCT-032
title: "Build a React CRUD App - Phase 1"
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-020, RCT-021, RCT-026, RCT-027
used_by: RCT-033, RCT-048, RCT-051
related: RCT-033, RCT-026, RCT-027
tags:
  - react
  - frontend
  - project
  - crud
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /react/build-a-react-crud-app-phase-1/
---

# RCT-032 - BUILD A REACT CRUD APP - PHASE 1

⚡ TL;DR - A React CRUD app integrates all foundational
patterns in one coherent project: component hierarchy,
state management with useState, async data fetching with
useEffect, form handling, list rendering with key props,
and routing - making it the "proof of concept" exercise
that confirms whether you can apply React in a real app.

| #032 | Category: React | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | useState Hook, useEffect Hook, Form Handling, React Router v6 | |
| **Used by:** | React Quick Recall Card, Testing React with RTL, Redux Toolkit | |
| **Related:** | React Quick Recall Card, Form Handling, React Router v6 | |

---

### 🔥 The Problem This Solves

**GAP BETWEEN ISOLATED CONCEPTS AND REAL APPLICATIONS:**
Learning React hooks, forms, routing, and state management
separately is necessary but insufficient. Each concept
makes sense in isolation. The challenge is integrating
them: a state update in one component must reflect in a
list in another; a form must post to an API and update
the rendered list; navigation must carry data between
routes; loading states must prevent partial renders.

A CRUD (Create, Read, Update, Delete) app forces this
integration. It is the minimal real application: you
must fetch data, display it, add to it, edit individual
items, and delete them. Every non-trivial React application
is an extension of CRUD.

---

### 📘 Textbook Definition

**CRUD App (React)** - a React application that implements
all four data operations against a REST API: Create (POST),
Read (GET), Update (PUT/PATCH), Delete (DELETE). Phase 1
establishes: project structure, component hierarchy, data
fetching with useEffect and async/await, list rendering
with keys, basic routing between list and detail views,
create/delete operations. Phase 2 (RCT-033) adds editing,
optimistic updates, and error handling.

---

### ⏱️ Understand It in 30 Seconds

**What we are building - a task manager:**

```
Routes:
  /        → TaskList (Read + Delete)
  /new     → TaskForm (Create)
  /tasks/:id/edit → TaskEdit (Update)

State model:
  tasks: Task[]     (list of all tasks)
  loading: boolean  (fetch in progress)
  error: string     (fetch error)

API: https://jsonplaceholder.typicode.com/todos
```

Single data type (`Task`), single API resource, three
routes, three components. Everything else is integration
of concepts already covered.

---

### 🔩 First Principles Explanation

**THE ARCHITECTURE DECISION:**

```
Option A: Centralized state in parent
  App → fetches tasks, passes to TaskList
  TaskList → reads tasks from props
  TaskForm → calls onTaskAdded callback
  App updates tasks array after mutation
  + Simple flow
  - App re-renders on every change

Option B: Each component fetches its own data
  TaskList → fetches all tasks
  TaskEdit → fetches single task
  + Decoupled
  - Multiple in-flight requests, stale data
  - Harder to update list after mutation

For Phase 1: Option A (centralized state in App)
  Simpler to reason about.
  All state lives in one place.
  State management libraries (Redux, React Query)
  extend Option A with caching and optimisation.
```

**THE DATA FLOW:**

```
App (state: tasks, loading, error)
  ↓ fetch on mount (useEffect)
  ↓ tasks via props
TaskList
  ↓ task via props (one at a time, map)
TaskItem
  └── Delete button → onDelete(id) callback
      → App removes task from state array

App → navigate to /new
TaskForm (create)
  → POST to API
  → calls onTaskCreated(newTask) callback
  → App appends new task to state
```

---

### 🧪 Thought Experiment

**OPTIMISTIC VS PESSIMISTIC UI:**
The user clicks "Delete" on a task. Should you:

A) **Pessimistic:** Send DELETE request, wait for response,
   then remove from state. The item stays visible for
   200-500ms after click. Feels slow but correct.

B) **Optimistic:** Remove from state immediately, send
   DELETE in background. Item disappears instantly. If
   DELETE fails, re-add to state and show error. Feels
   fast.

Phase 1 implements pessimistic (simpler). Phase 2 (RCT-033)
implements optimistic. Understanding the trade-off requires
building both. Most production apps use optimistic for
delete/like/follow operations and pessimistic for
payment/critical mutations.

---

### 🧠 Mental Model / Analogy

> Building a CRUD app is like assembling flat-pack
> furniture. You have all the pieces (hooks, components,
> forms, routing). The instruction booklet (documentation)
> showed each piece individually. Now you must assemble
> them in the right order: foundation first (project
> setup, routing), then structure (components, state),
> then function (data fetching, mutation). Each step
> depends on the previous. The finished product is a
> working app that demonstrates you understood the
> assembly - not just the individual parts.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
A CRUD app fetches a list, shows it, provides forms to
create/edit items, and lets you delete. Each operation
maps to: GET list, POST new item, PUT/PATCH edit, DELETE
remove. Data lives in parent state and is distributed
via props.

**Level 2 (implementation):**
`useEffect` with `[]` dependency fetches the list on mount.
The fetched data is set into state with `useState`. The
list maps to `TaskItem` components with `key={task.id}`.
Create: `POST` in form submit, then `setTasks(prev => [...prev, newTask])`.
Delete: `DELETE` in handler, then `setTasks(prev => prev.filter(t => t.id !== id))`.

**Level 3 (data freshness):**
The pattern of "optimistically update state then confirm
with API" vs "wait for API then update state" creates
different UX. On network failure, optimistic updates must
be rolled back. Pessimistic updates are always consistent
with the server but feel slow. React Query and SWR
automate this trade-off with cache invalidation and
background revalidation.

**Level 4 (state management):**
As the app grows: user authentication, filtering, sorting,
pagination. The centralized `App` state becomes unwieldy.
The natural graduation is: React Query for server state
(caching, invalidation, optimistic updates), Zustand for
UI state (sidebar open, filter selection). This is how
most production React apps are structured.

**Level 5 (mastery):**
The CRUD app exposes the impedance mismatch between server
state (async, potentially stale, source of truth on server)
and client state (synchronous, immediately consistent, owned
by client). React's `useState` treats both the same.
Libraries like React Query and TanStack Query exist specifically
to model server state differently: it has `status` (loading/
error/success), `data`, `refetch`, `invalidate`, and
background refetching. Building a CRUD app manually first
makes these abstractions deeply understandable.

---

### ⚙️ How It Works (Mechanism)

**Complete Phase 1 CRUD app structure:**

```jsx
// File structure:
// src/
//   App.jsx        - routing + top-level state
//   api/tasks.js   - API functions (separation of concerns)
//   components/
//     TaskList.jsx
//     TaskItem.jsx
//     TaskForm.jsx
//     LoadingSpinner.jsx

// api/tasks.js - all API calls in one place
const BASE_URL = 'https://jsonplaceholder.typicode.com';

export async function fetchTasks() {
  const res = await fetch(`${BASE_URL}/todos?_limit=10`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createTask(data) {
  const res = await fetch(`${BASE_URL}/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function deleteTask(id) {
  const res = await fetch(`${BASE_URL}/todos/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

// App.jsx - state + routing
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { fetchTasks, createTask, deleteTask } from './api/tasks';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchTasks()
      .then(data => { if (!cancelled) setTasks(data); })
      .catch(err => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };  // cleanup
  }, []);

  const handleCreate = async (formData) => {
    const newTask = await createTask(formData);
    setTasks(prev => [newTask, ...prev]);
  };

  const handleDelete = async (id) => {
    await deleteTask(id);
    setTasks(prev => prev.filter(t => t.id !== id));
  };

  if (loading) return <p>Loading tasks...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<TaskList tasks={tasks} onDelete={handleDelete} />}
        />
        <Route
          path="/new"
          element={<TaskForm onSubmit={handleCreate} />}
        />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### 💻 Code Example

**BAD: Direct API call in component, no error handling:**

```jsx
// BAD: No separation of concerns, no error handling,
//      no loading state, no cleanup, race condition risk
function TaskList() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    // No loading state - user sees empty list
    // No error handling - silent failure
    // No cleanup - if component unmounts, setTasks
    //   still runs and causes React warning
    fetch('https://jsonplaceholder.typicode.com/todos')
      .then(res => res.json())  // doesn't check res.ok
      .then(data => setTasks(data));
  }, []);

  return (
    <ul>
      {tasks.map(task => (
        // key is on wrong element and uses index
        <li key={task.index}>{task.title}</li>
      ))}
    </ul>
  );
}
```

**GOOD: Proper structure with separation of concerns:**

```jsx
// GOOD: Separated API, loading/error state, cleanup,
//       proper keys, delete with optimistic UI

// TaskList.jsx
function TaskList({ tasks, onDelete, loading, error }) {
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (tasks.length === 0) return <p>No tasks. Create one.</p>;

  return (
    <ul>
      {tasks.map(task => (
        <TaskItem
          key={task.id}         // unique, stable key from data
          task={task}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}

// TaskItem.jsx
function TaskItem({ task, onDelete }) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <li>
      <span>{task.title}</span>
      <button onClick={handleDelete} disabled={deleting}>
        {deleting ? 'Deleting...' : 'Delete'}
      </button>
    </li>
  );
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The CRUD app teaches how React is used in production" | It teaches the patterns. Production apps almost always add React Query or SWR for server state (caching, background refetch, loading states), TypeScript, and a proper API layer. The CRUD app is the conceptual foundation, not the production template. |
| "You need Redux for a CRUD app" | For a single-resource CRUD app, `useState` in the parent component is sufficient. Redux adds value when you have complex state interactions, multiple resources, DevTools needs, or complex cache invalidation. Adding Redux to a simple CRUD app is over-engineering. |
| "useEffect with `[]` always runs once" | It runs once per mount. In React 18 strict mode (development), effects run twice intentionally (mount → unmount → mount) to detect side effect bugs. The cleanup function is essential to handle this correctly. |
| "After a successful POST, the API always returns the created item" | RESTful convention is to return the created resource. But some APIs return `201 Created` with an empty body or a different format. Always read the API docs and handle both the returned ID and the case where the ID must be read from a Location header. |

---

### 🚨 Failure Modes & Diagnosis

**Memory Leak: setState after Component Unmount**

**Symptom:** React warning: "Can't perform a React state
update on an unmounted component."

**Root Cause:** User navigates away before the `fetch`
completes. The `useEffect` callback runs, calls `setTasks`,
but the component is unmounted.

**Fix:** Use a cleanup function with a cancelled flag:
```jsx
useEffect(() => {
  let cancelled = false;
  fetchTasks().then(data => {
    if (!cancelled) setTasks(data);
  });
  return () => { cancelled = true; };
}, []);
```

---

**Race Condition: Multiple Fetches Out of Order**

**Symptom:** User changes a filter. Two fetches fire.
The first fetch (old filter) resolves AFTER the second
(new filter). The list shows stale results.

**Root Cause:** Network responses do not arrive in order.
Without cancellation, the last response to arrive wins,
regardless of when it was sent.

**Fix:** Use the same `cancelled` flag pattern, or use
`AbortController`:
```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(...)
    .catch(err => { if (err.name !== 'AbortError') setError(err.message); });
  return () => controller.abort();
}, [filter]);  // re-runs on filter change, cancels previous
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `useState Hook` - local state for tasks, loading, error
- `useEffect Hook` - data fetching on mount
- `Form Handling` - create/edit task forms
- `React Router v6` - navigation between list and form

**Builds On:**
- `React Quick Recall Card` - synthesis of all CRUD patterns
- `Testing React with RTL` - testing CRUD operations
- `Redux Toolkit` - scaling the CRUD state model to
  production with slices and RTK Query

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FETCH LIST  │ useEffect(fetchFn, []) → setItems         │
│ CREATE      │ POST → setItems(prev => [new, ...prev])   │
│ DELETE      │ DELETE id → setItems(prev => prev.filter) │
│ UPDATE      │ PUT id → setItems(prev => prev.map(       │
│             │   t => t.id===id ? updated : t))          │
├──────────────────────────────────────────────────────────┤
│ STATE SHAPE │ items: [], loading: bool, error: string   │
├──────────────────────────────────────────────────────────┤
│ PATTERNS    │ API layer (api/resource.js)               │
│             │ Cancelled flag in useEffect cleanup       │
│             │ AbortController for cancellable fetches  │
├──────────────────────────────────────────────────────────┤
│ KEYS        │ Always use stable API ID, never index     │
│ ERRORS      │ Check res.ok before res.json()           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Fetch on mount in `useEffect(fn, [])`. Always check
   `res.ok`. Set loading/error states. Use cleanup to
   prevent setState on unmounted component.
2. State updates after mutations: create → spread new
   item into array; delete → filter; update → map with
   replacement.
3. Separate API functions into an `api/` layer. Never
   inline `fetch` calls in components.

**Interview one-liner:**
"A React CRUD app uses useEffect with `[]` to fetch a
list on mount (with loading/error state and a cancelled
flag for cleanup), renders items with unique keys, posts
new items and appends to state (`[newItem, ...prev]`),
deletes by filtering state after the API call, and updates
by mapping state (replace the matching item). An API layer
(`api/tasks.js`) separates network calls from components.
React Query is the production evolution that adds caching,
background refetch, and automatic race condition handling."

---

### 💎 Transferable Wisdom

The CRUD pattern is universal. Every system that manages
data implements Create, Read, Update, Delete - from a
file system to a database to a REST API to a React state
array. The state manipulation patterns in a React CRUD
app (add item to array, filter to remove, map to update)
are functional programming operations that appear in every
language and paradigm. The React CRUD app is also a
concrete lesson in the difference between server state
(what the API knows) and client state (what React has in
memory) - a distinction that becomes the foundation for
understanding caching, optimistic updates, and data
synchronisation at scale.

---

### 💡 The Surprising Truth

The canonical React tutorial (the official docs) uses a
"tic-tac-toe" game, not a CRUD app, as the introduction.
The reason: a game has no async operations, no API calls,
no loading states - it is pure synchronous state management.
This deliberately isolates the React component model from
the async complexity of data fetching. The CRUD app adds
the async layer. This two-phase learning approach (pure
state first, then async) is pedagogically intentional.
Many React developers struggle in production because they
learned React through games and toy examples that never
had a loading state - then suddenly face API latency,
errors, and race conditions in real code.

---

### ✅ Mastery Checklist

1. **BUILD** the complete Phase 1 CRUD app from scratch:
   fetch list on mount, display with proper keys, add item
   via form, delete with confirmation, handle loading and
   error states for all operations.
2. **DEMONSTRATE** the cancelled flag pattern: trigger a
   component unmount while a fetch is in-flight and
   confirm no React warning occurs.
3. **IMPLEMENT** an API layer (`api/tasks.js`) and explain
   why separating API calls from component logic improves
   testability and maintainability.
4. **IDENTIFY** the race condition in a filter-based CRUD
   app (changing filter causes two in-flight requests)
   and implement the AbortController fix.
5. **EXPLAIN** why this Phase 1 implementation would be
   replaced by React Query in a production app, with
   specific reference to what React Query automates.

---

### 🧠 Think About This Before We Continue

**Q1.** The Phase 1 app stores tasks in `useState` in
the App component. Every time a task is added or deleted,
App re-renders and passes new props to TaskList, which
renders all TaskItem components. If the list has 500
items and you delete one, all 500 TaskItem components
re-render. How would you optimise this? What React APIs
are relevant?

**Q2.** The user adds a task, which POSTs to the API.
The API creates the task but the network times out before
the response arrives. The user clicks "Add" again. Now
two tasks are created. How do you prevent this at the
form level? Is there a server-side component to this
solution?

**Q3.** After Phase 1, the natural next step is React
Query. React Query's core value proposition is "server
state management." What does this mean concretely? What
does React Query do that `useState + useEffect + fetch`
does not, and what problems does it solve that Phase 1's
approach has?