---
id: RCT-027
title: React Router v6 Basics
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-005, RCT-010, RCT-012
used_by: RCT-033, RCT-052, RCT-066
related: RCT-040, RCT-056, RCT-022
tags:
  - react
  - frontend
  - routing
  - spa
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/react/react-router-v6-basics/
---

⚡ TL;DR - React Router v6 maps URL paths to components
using `<Routes>` + `<Route>` declarative config, `<Link>`
for navigation, `useNavigate()` for programmatic navigation,
and `useParams()` for URL parameters - all without page
reloads, making SPAs feel like multi-page apps by
synchronising URL and rendered component.

| #027            | Category: React                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | JSX, React Components, ReactDOM Rendering         |                 |
| **Used by:**    | React CRUD App, Micro-Frontend Architecture       |                 |
| **Related:**    | Code Splitting with lazy, React Server Components |                 |

---

### 🔥 The Problem This Solves

**SPA WITH ONE URL:**
A React SPA renders everything in one HTML page. Without
a router, the URL is always `example.com/` regardless
of whether the user is viewing a dashboard, a user profile,
or a settings page. This means:

- Browser back/forward button does nothing useful
- Sharing a link always opens the home page
- Search engines cannot index individual pages
- Users cannot bookmark deep links
- Direct navigation (`example.com/settings`) returns 404

React Router maps URL path segments to React components,
solving all of these problems while keeping the SPA
architecture (no full page reloads).

---

### 📘 Textbook Definition

**React Router v6** is a client-side routing library that
synchronises the browser URL with the React component tree.
It intercepts browser navigation events, prevents default
page reloads, and renders the component tree that matches
the current URL. The v6 API uses `<BrowserRouter>` at
the root, `<Routes>` + `<Route path element>` for route
config, `<Link to>` for navigation links, `<Outlet>` for
nested routes, and hooks (`useNavigate`, `useParams`,
`useLocation`, `useSearchParams`) for programmatic routing.

---

### ⏱️ Understand It in 30 Seconds

```jsx
// 1. Wrap app with BrowserRouter (once, at root)
<BrowserRouter>
  <App />
</BrowserRouter>;

// 2. Define routes in App
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/users" element={<UserList />} />
      <Route path="/users/:id" element={<UserDetail />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

// 3. Navigate with Link
<Link to="/users">Users</Link>;

// 4. Read URL params
function UserDetail() {
  const { id } = useParams();
  return <h1>User {id}</h1>;
}
```

No page reloads. URL updates. Back/forward works.

---

### 🔩 First Principles Explanation

**HOW CLIENT-SIDE ROUTING WORKS:**

```
WITHOUT router:
  User clicks <a href="/users">
  Browser sends GET /users to server
  Server returns new HTML → full page reload

WITH React Router:
  User clicks <Link to="/users">
  React Router intercepts click event
  Calls window.history.pushState('/users', ...)
  URL changes in browser address bar (no server request)
  React Router re-renders matched <Route> components
  No network request, no page reload
```

**THE HISTORY API:**
React Router uses the browser's History API under the
hood. `pushState` adds a new entry to the browser's
history stack. Clicking the back button fires the
`popstate` event - React Router listens for this and
re-renders the matching route.

**v5 vs v6 DIFFERENCES:**

```
v5 (old):                  v6 (current):
<Switch>                   <Routes>
<Route component={X}>      <Route element={<X />}>
<Route exact path="/">     exact is default in v6
useHistory()               useNavigate()
<Redirect to="/x">         <Navigate to="/x" />
```

---

### 🧪 Thought Experiment

**THE DIRECT LINK PROBLEM:**
A user bookmarks `app.com/dashboard/reports`. They close
the browser and return later. The browser sends a GET
request to your server for `/dashboard/reports`. Your
server only serves `index.html` (the SPA shell). It
does not know about `/dashboard/reports`.

Result: 404 or the SPA loads but React Router reads the
URL and renders the Reports component. The server must
be configured to return `index.html` for all routes
(with `try_files` in nginx, or a catch-all in Express).
React Router handles the rest on the client.

This is the "SPA deployment" configuration requirement
that trips up many developers first deploying a React app.

---

### 🧠 Mental Model / Analogy

> React Router is like a hotel reception system. The hotel
> building (BrowserRouter) has many rooms. The reception
> desk (Routes) checks the guest's key (URL path) against
> the room registry (Route configs). The guest is taken
> to the right room (matched component renders). Moving
> between rooms (Link/useNavigate) does not require leaving
> the building (no page reload) - the guest just gets a
> new key (URL updates) and reception directs them to
> the correct room. If the guest tries a non-existent
> room number (unmatched path), reception takes them to
> the "room not found" area (catch-all `*` route).

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
React Router maps URLs to components without page reloads.
`<Routes>` holds `<Route>` elements. When the URL matches
a path, that route's `element` renders. `<Link>` navigates.

**Level 2 (usage):**
`path="/users/:id"` - colon prefix means URL parameter.
Read with `useParams()`. Navigate programmatically with
`useNavigate()`. Redirect: `<Navigate to="/new-path" />`.
404 catch-all: `<Route path="*" element={<NotFound />} />`.

**Level 3 (nested routes):**
Nested routes: child `<Route>` inside parent `<Route>`.
Parent component renders `<Outlet />` where the child
renders. URL `"/dashboard/settings"` renders `Dashboard`
wrapping `Settings`. Layout routes: parent with no path
that renders a shared layout (nav, sidebar) around all
child routes.

**Level 4 (loaders/actions - v6.4+):**
React Router v6.4 added `createBrowserRouter` and data
APIs: `loader` functions fetch data before the route
renders, `action` functions handle form submissions.
The component receives data via `useLoaderData()`. This
moves data fetching into the router, enabling automatic
race condition handling, pending UI via `useNavigation`,
and optimistic UI.

**Level 5 (mastery):**
React Router's `<Outlet>` enables a component composition
model identical to the "render props" pattern but URL-
driven. Each nested route segment is a named slot in the
parent. This is how `createBrowserRouter` in v6.4 enables
full-stack routing patterns where the router handles data
loading, mutations, and error boundaries - similar to
Next.js App Router but in a client-side-only setup.

---

### ⚙️ How It Works (Mechanism)

**Complete routing setup with nested routes:**

```jsx
// main.jsx - root setup
import { createBrowserRouter,
    RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />, // Always renders
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <Home /> },
      {
        path: "users",
        element: <UsersLayout />,
        children: [
          { index: true, element: <UserList /> },
          { path: ":id", element: <UserDetail /> },
        ],
      },
      { path: "settings", element: <Settings /> },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

// RootLayout - renders nav + outlet
function RootLayout() {
  return (
    <>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/users">Users</Link>
        <Link to="/settings">Settings</Link>
      </nav>
      <Outlet /> {/* child route renders here */}
    </>
  );
}

// UsersLayout - renders user section + nested outlet
function UsersLayout() {
  return (
    <div>
      <h1>Users Section</h1>
      <Outlet /> {/* UserList or UserDetail renders here */}
    </div>
  );
}
```

---

### 📊 Comparison Table

| Feature          | React Router v6                  | Next.js App Router          |
| ---------------- | -------------------------------- | --------------------------- |
| Route definition | Declarative JSX or config object | File-system based           |
| Data loading     | `loader` functions (v6.4+)       | `async` components, `fetch` |
| Server rendering | Client-side only                 | Full SSR/SSG/ISR support    |
| Nested layouts   | `<Outlet>`                       | Nested `layout.tsx` files   |
| Code splitting   | Manual with `lazy()`             | Automatic per segment       |
| Use case         | CSR React apps, Vite             | Full-stack React apps       |
| Bundle           | ~50KB                            | Included in Next.js         |

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "`<Switch>` was renamed to `<Routes>` in v6"                    | Not just a rename. `<Routes>` uses relative path matching, ranks routes by specificity (no order-dependence), and renders only the first match. `<Switch>` required `exact` and order-based first-match. v6 is a fundamentally different matching algorithm.             |
| "React Router handles 404s automatically for direct navigation" | Direct navigation (`example.com/users/5`) reaches the server, not React Router. The server must be configured to return `index.html` for all paths. React Router then handles the path. Without server config, direct navigation returns 404.                            |
| "useNavigate is just useHistory renamed"                        | `useNavigate()` returns a function. `navigate('/path')` replaces `history.push('/path')`. `navigate(-1)` replaces `history.goBack()`. Navigation state: `navigate('/path', { state: { data } })` read via `useLocation().state`. Functionally similar but different API. |
| "Nested routes require nested `<Routes>` elements"              | In v6, nested routes use `<Outlet />` in the parent component. The child routes are defined as children of the parent `<Route>` - not inside a second `<Routes>`. One `<Routes>` at the root handles the entire route tree.                                              |

---

### 🚨 Failure Modes & Diagnosis

**404 on Direct Navigation / Page Refresh**

**Symptom:** App works fine when navigating via links.
But refreshing the page or entering the URL directly
returns a 404 from the server.

**Root Cause:** The server handles the request before
React Router. The server has no HTML file at `/users/5`.
React Router only runs in the browser after `index.html`
is served.

**Fix (nginx):**

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

**Fix (Express):**

```js
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});
```

---

**Routes Not Matching Despite Correct Path**

**Symptom:** `<Route path="/users">` never renders even
when URL is `/users`. Other routes work fine.

**Root Cause:** In v6, paths are relative to the parent
route. If this `<Routes>` is inside a component already
rendered at `/dashboard`, then `path="/users"` matches
`/dashboard/users`, not `/users`. Or nested route missing
parent's `<Outlet>`.

**Fix:** Use relative paths in nested routes. Check that
the parent renders `<Outlet />`. Use React Router devtools
or add a `*` catch-all to debug which path is actually
matching.

---

### 🔗 Related Keywords

**Prerequisites:**

- `React Components` - what routes render
- `JSX and Expressions` - the `element` prop syntax
- `ReactDOM Rendering` - the browser DOM that routing operates on

**Builds On:**

- `Code Splitting with React.lazy` - lazy-load heavy route
  components to reduce initial bundle size
- `React Server Components` - Next.js App Router as a
  more advanced routing model
- `Context API` - sharing router-level state across routes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SETUP       │ <BrowserRouter> wraps root in index.jsx  │
│ ROUTES      │ <Routes><Route path element /></Routes>  │
│ LINK        │ <Link to="/path">text</Link>             │
│ ACTIVE LINK │ <NavLink> applies active class          │
├─────────────────────────────────────────────────────────┤
│ URL PARAMS  │ path="/users/:id" → useParams().id       │
│ QUERY STR   │ useSearchParams() → [params, setParams]  │
│ LOCATION    │ useLocation() → { pathname, state, ... } │
│ NAVIGATE    │ const nav = useNavigate(); nav('/path')  │
│ REDIRECT    │ <Navigate to="/x" replace />             │
├─────────────────────────────────────────────────────────┤
│ NESTED      │ Parent renders <Outlet />                │
│ INDEX ROUTE │ <Route index element={<Home />} />       │
│ 404 ROUTE   │ <Route path="*" element={<NotFound />} />│
├─────────────────────────────────────────────────────────┤
│ SERVER      │ Must return index.html for all paths     │
│             │ (nginx try_files, Express catch-all)     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `<Routes>` + `<Route path element>` defines routes.
   `<Link to>` navigates. `useParams()` reads `:param`.
2. Server must serve `index.html` for all paths or direct
   navigation returns 404.
3. Nested routes: define children inside parent `<Route>`,
   render `<Outlet />` in parent component.

**Interview one-liner:**
"React Router v6 uses `<Routes>` + `<Route path element>`
to map URLs to components, `<Link>` for navigation (no
page reload via History API pushState), `useParams` for
URL parameters, and `<Outlet>` for nested layout routes.
The server must be configured to return `index.html` for
all paths - React Router only runs client-side after the
HTML is served. v6.4 added `loader`/`action` APIs that
move data fetching into the router config, enabling
pending UI and race condition handling."

---

### 💎 Transferable Wisdom

React Router's pattern - URL as state that drives component
rendering - is "URL as the source of truth." This pattern
appears in: deep-linking in mobile apps (universal links),
server-side routing in web frameworks (Express, Django,
Rails - all map URL patterns to handlers), DNS routing
(domain → IP), API gateway routing (path → Lambda function).
The fundamental concept is: a hierarchical path string
is matched against a pattern registry, and the matching
handler is executed. React Router applies this pattern
in the browser, using component rendering as the "handler."

---

### 💡 The Surprising Truth

React Router does NOT do any network requests. It is
purely a JavaScript state machine that listens to browser
history events and re-renders components. The URL change
happens via the History API (`pushState`) which is a
browser-native mechanism to update the address bar and
history stack without any network activity. The "routing"
is entirely local. This is why React Router v6 bundle is
only ~50KB - it contains zero HTTP client code. The "network"
part of routing (fetching data for a route) is entirely
up to the developer, unless using the v6.4 data APIs.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a multi-page app with Home, Users (list),
   and UserDetail (`/users/:id`) routes using nested routes
   with a shared navigation layout.
2. **CONFIGURE** a development and production server (any
   server of your choice) to correctly handle direct
   navigation to any route without returning 404.
3. **BUILD** programmatic navigation: after form submission
   redirects to a success page, and a back button returns
   to the form.
4. **USE** `useSearchParams` to implement a URL-persisted
   search filter that survives page refresh and can be
   shared via link.
5. **EXPLAIN** the v5-to-v6 migration of `<Switch>`,
   `<Redirect>`, `useHistory`, and `exact` to their v6
   equivalents, and why the v6 route-ranking algorithm
   eliminates the need for `exact`.

---

### 🧠 Think About This Before We Continue

**Q1.** A dashboard app has protected routes. Unauthenticated
users should be redirected to `/login`. Where do you
implement this guard - in each protected component, in
the `<Route>` definition, or in a wrapper component?
What are the trade-offs of each approach?

**Q2.** React Router keeps route state in the URL. Other
application state (selected filters, pagination page,
scroll position) could also live in the URL via query
parameters. What are the advantages and disadvantages
of putting ALL application state in the URL vs in React
state? Where is the boundary?

**Q3.** React Router v6.4 `loader` functions run before
the route renders to fetch data. Next.js does something
similar with `async` server components. Both solve the
"waterfall" problem where a component mounts, then fetches
data, then renders. How does routing-level data loading
compare to React Query's approach of fetching in the
component with caching? What does each approach optimise for?
