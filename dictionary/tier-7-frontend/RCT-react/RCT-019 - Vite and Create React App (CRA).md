---
id: RCT-019
title: Vite and Create React App (CRA)
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-005, RCT-006
used_by: RCT-058, RCT-065
related: RCT-006, RCT-058, RCT-065
tags:
  - react
  - frontend
  - tooling
  - build-tools
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /react/vite-and-create-react-app/
---

# RCT-019 - VITE AND CREATE REACT APP (CRA)

⚡ TL;DR - Create React App (CRA) was the official React
scaffolding tool for 2016-2023 but is now deprecated and
unmaintained; Vite has replaced it as the standard - it
uses native ES modules for near-instant dev server starts
and is 10-100x faster for large projects.

| #019            | Category: React                                               | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | React Ecosystem Landscape, React Dev Environment Setup        |                 |
| **Used by:**    | Bundle Size Analysis, CRA Deprecation Entry                   |                 |
| **Related:**    | React Dev Environment Setup, Bundle Analysis, CRA Deprecation |                 |

---

### 🔥 The Problem This Solves

**THE ZERO-CONFIG PROBLEM:**
Setting up a modern React application from scratch requires
configuring: a transpiler (Babel or SWC to convert JSX
and modern JavaScript to browser-compatible code), a bundler
(Webpack or Rollup to bundle modules), a dev server (with
hot reload), a test runner, and environment variable
handling. This is non-trivial configuration that beginners
should not have to do and even experienced developers should
not have to repeat.

CRA and Vite both solve this by providing a scaffolded,
pre-configured project that is ready to develop in one
command. The difference is the technology inside the
scaffolding and how it affects developer experience at scale.

---

### 📘 Textbook Definition

**Create React App (CRA)** was the official React project
scaffolding tool maintained by Facebook/Meta from 2016 to 2023. It created a zero-configuration Webpack + Babel
setup. CRA is now deprecated (last meaningful release was
React Scripts 5 in 2022; the repository is effectively
unmaintained as of 2023).

**Vite** (created by Evan You, Vue.js creator) is the
current standard for React scaffolding. Vite uses a two-
phase architecture: during development, it serves files
as native ES Modules directly (no bundling required,
using browser-native `import`); for production builds,
it uses Rollup to create optimised bundles. This results
in dev server cold start in milliseconds (no bundle step)
and near-instant Hot Module Replacement (HMR) for any
file change.

---

### ⏱️ Understand It in 30 Seconds

**Create a React project today:**

```bash
# Vite (recommended):
npm create vite@latest my-app -- --template react
cd my-app
npm install
npm run dev

# TypeScript React with Vite:
npm create vite@latest my-app -- --template react-ts
```

**Why not CRA:**
`npx create-react-app` still works but creates a project
using deprecated, unmaintained packages. The dev server
is slow for any non-trivial project. CRA cannot be easily
ejected and customised. The React team's own docs now
recommend Vite or a full-stack framework (Next.js, Remix).

---

### 🔩 First Principles Explanation

**CRA'S WEBPACK-BASED ARCHITECTURE:**

```
Dev server start:
  1. Webpack reads all files in the project
  2. Builds a complete dependency graph
  3. Bundles ALL files into a single bundle
  4. Serves the bundle to the browser

This means: 500 files → 500 files bundled before first
render. As project grows, cold start time grows.
A large React SPA with 2000+ modules can take 30-60
seconds to start in CRA.
```

**VITE'S NATIVE ESM ARCHITECTURE:**

```
Dev server start:
  1. Pre-bundle only node_modules (CommonJS → ESM)
     (uses esbuild, written in Go - 10-100x faster than
     Webpack's JavaScript-based transform)
  2. Start HTTP server immediately

Browser requests:
  1. Browser loads index.html
  2. index.html has <script type="module" src="./main.jsx">
  3. Browser requests main.jsx from dev server
  4. Vite transforms ONLY main.jsx on demand (JSX → JS)
  5. Browser executes, encounters imports
  6. Browser requests each imported file
  7. Vite transforms each on demand

Result: only files actually used are transformed.
500 file project: only the ~10 files currently in view
are transformed. Cold start: milliseconds not seconds.
```

---

### 🧪 Thought Experiment

**DEV SERVER SPEED AT SCALE:**
A CRA project starts fresh every morning. At 50 components:
5-second start. At 200 components: 20-second start. At
1000 components (common in enterprise): 45+ seconds.
After each HMR file save: 3-5 seconds for full re-bundle.

The same project in Vite: dev server start in ~300ms
regardless of project size (only dependencies are
pre-bundled). After each HMR file save: 50-200ms (only
the changed file is transformed). The productivity
difference compounds over a full workday.

---

### 🧠 Mental Model / Analogy

> CRA is like a restaurant that pre-cooks every item on
> the menu before opening. Every dish is ready instantly
> once a customer arrives, but the restaurant cannot open
> until every item has been cooked (even the ones no
> customer will order today). Vite is like a restaurant
> that prepares only what is ordered. The kitchen starts
> in seconds. Each dish takes a moment to prepare when
> ordered, but only the ordered dishes are prepared.
> For a 500-item menu, the on-demand approach is
> dramatically faster to open.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
CRA and Vite are tools that create a ready-to-use React
project for you with all the configuration done. Vite is
the modern replacement for CRA, which is no longer
maintained.

**Level 2 (usage):**
Use `npm create vite@latest` to start new React projects.
If maintaining an existing CRA project, consider migrating
to Vite. The migration process involves replacing react-
scripts with Vite config files, which typically takes 1-4
hours for a medium project.

**Level 3 (mechanism):**
CRA uses Webpack (JavaScript bundler) and Babel
(JavaScript/JSX transpiler) under the hood. Vite uses
esbuild (Go-based) for development transforms and Rollup
for production builds. Vite's dev server leverages native
ES Module imports in modern browsers - no bundling step
during development. Only production builds are bundled.

**Level 4 (architecture):**
Vite's architecture separates dev and prod toolchains
intentionally. esbuild is 10-100x faster than Webpack for
transforms but lacks Webpack's ecosystem of plugins.
Rollup produces smaller, more optimised bundles than
Webpack for libraries. This two-tool approach gets the
best of both: fast dev (esbuild) and optimised prod
(Rollup). The tradeoff: dev and prod environments are
slightly different (potential for bugs that appear only
in production bundles, not dev server).

**Level 5 (mastery):**
For production applications, neither CRA nor bare Vite
is the ideal choice. React's own documentation recommends
full-stack frameworks: Next.js (file-system routing, SSR,
RSC), Remix (progressive enhancement, nested routing,
error boundaries by default), or Expo (React Native).
Pure SPAs (Vite + React Router) lack server-side rendering,
which hurts Core Web Vitals (especially LCP) for content-
heavy pages. Vite is the correct choice for tools/dashboards/
admin panels (where SEO and LCP are less critical) or
as the development environment inside a framework like
Remix or Astro.

---

### ⚙️ How It Works (Mechanism)

**Vite project structure:**

```
my-app/
  node_modules/
  public/               # static assets (not processed)
    vite.svg
  src/
    assets/             # processed assets (imported in JS)
      react.svg
    App.css
    App.jsx             # root component
    main.jsx            # entry point
  index.html            # HTML template (in root, not public!)
  package.json
  vite.config.js        # Vite configuration
```

**vite.config.js (standard React setup):**

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Optional: path aliases
  resolve: {
    alias: { "@": "/src" },
  },
});
```

**package.json scripts:**

```json
{
  "scripts": {
    "dev": "vite", // start dev server
    "build": "vite build", // production build → dist/
    "preview": "vite preview", // preview prod build locally
    "test": "vitest" // Vitest test runner (Vite-native)
  }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**VITE DEVELOPMENT FLOW:**

```
1. Developer: npm run dev
2. Vite pre-bundles node_modules with esbuild
3. Dev server starts on localhost:5173
4. Browser requests http://localhost:5173
5. Vite serves index.html
6. Browser parses <script type="module" src="/src/main.jsx">
7. Browser requests /src/main.jsx
8. Vite transforms main.jsx (JSX → JS) on demand
9. Browser imports App.jsx (encounters import)
10. Vite transforms App.jsx on demand
11. App renders in browser

On file save:
12. Vite invalidates ONLY the changed module
13. Browser receives HMR update for that module
14. Only the changed component re-renders
15. Total time: ~50-200ms (vs CRA's 3-5s full rebundle)
```

---

### 💻 Code Example

**BAD: Starting a new project with deprecated CRA:**

```bash
# BAD: CRA is deprecated (do not use for new projects)
npx create-react-app my-app
# Problems:
# - Installs react-scripts 5.x (last release: Dec 2022)
# - Node 22+ requires --openssl-legacy-provider workaround
# - Slow dev server for any project > 50 components
# - Cannot upgrade React to latest easily
# - Many known security vulnerabilities in dependencies
# - The React team themselves no longer recommend CRA
```

**GOOD: Vite for new React projects:**

```bash
# GOOD: Vite with React template
npm create vite@latest my-app -- --template react
cd my-app
npm install
npm run dev
# Dev server starts in ~300ms
# HMR updates in ~50ms

# Or with TypeScript (recommended for new projects)
npm create vite@latest my-app -- --template react-ts
```

**PRODUCTION: CRA to Vite migration steps:**

```bash
# 1. Install Vite dependencies
npm install --save-dev vite @vitejs/plugin-react

# 2. Remove CRA dependencies
npm uninstall react-scripts

# 3. Update package.json scripts
# From: "start": "react-scripts start", "build": "react-scripts build"
# To:   "dev": "vite",                  "build": "vite build"

# 4. Create vite.config.js
# (see configuration above)

# 5. Move index.html from public/ to root
# Remove %PUBLIC_URL% references (Vite does not use it)
# Add <script type="module" src="/src/main.jsx"></script>

# 6. Fix env variables
# CRA: process.env.REACT_APP_API_URL
# Vite: import.meta.env.VITE_API_URL
# Rename all .env variables from REACT_APP_ to VITE_
```

---

### 📊 Comparison Table

| Feature                    | Create React App        | Vite                    | Next.js                   |
| -------------------------- | ----------------------- | ----------------------- | ------------------------- |
| Status                     | Deprecated              | Active (recommended)    | Active                    |
| Dev server                 | Webpack (slow at scale) | Native ESM (fast)       | Turbopack (fast)          |
| Cold start (large project) | 30-60s                  | ~300ms                  | ~500ms                    |
| HMR                        | 2-5s                    | 50-200ms                | 50-200ms                  |
| SSR support                | No (SPA only)           | No (SPA only)           | Yes (built-in)            |
| File-system routing        | No                      | No                      | Yes                       |
| Bundle for prod            | Webpack                 | Rollup                  | Webpack/Turbopack         |
| TypeScript                 | Supported               | Supported               | Supported                 |
| Best for                   | Legacy projects         | SPAs, tools, dashboards | Content sites, full-stack |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CRA is still supported because it is the official React tool" | CRA is officially deprecated. The React docs removed CRA from the Getting Started guide in 2023. The `create-react-app` GitHub repository has had no meaningful releases since December 2022.                                                                                       |
| "Vite is only for Vue projects (created by the Vue author)"    | Vite is framework-agnostic. Official templates exist for React, Vue, Svelte, Solid, Preact, and Vanilla JavaScript. The React template (`@vitejs/plugin-react`) is the most widely used.                                                                                            |
| "Vite dev and prod build differences cause bugs"               | This is a real concern (dev = native ESM; prod = Rollup bundle). Mitigate by always testing the production build (`npm run preview`) before deployment, and configure Vite to use consistent module resolution in both modes.                                                       |
| "Ejecting from CRA gives you full control"                     | CRA's `eject` command removes the abstraction and exposes raw Webpack/Babel config, but the exposed config is the old CRA config from React Scripts. The result is a complex, hard-to-maintain Webpack setup based on outdated patterns. Migrating to Vite is better than ejecting. |

---

### 🚨 Failure Modes & Diagnosis

**CRA: "Digital Envelope Routines" Error on Node 18+**

**Symptom:**

```
error:0308010C:digital envelope routines::unsupported
```

**Root Cause:** Node 18+ uses OpenSSL 3 which deprecated
MD4 hash algorithm that CRA's Webpack config uses.

**Fix (temporary):**

```bash
set NODE_OPTIONS=--openssl-legacy-provider
npm start
```

**Fix (permanent):** Migrate to Vite.

---

**Vite: `import.meta.env` Variables Undefined in Production**

**Symptom:** Environment variables work in dev but are
`undefined` in production.

**Root Cause:** Variable names must be prefixed with
`VITE_` to be exposed. `REACT_APP_` prefixes from CRA
migration are not picked up by Vite.

**Fix:** Rename all env variables to `VITE_` prefix and
update references from `process.env.REACT_APP_*` to
`import.meta.env.VITE_*`.

---

### 🔗 Related Keywords

**Prerequisites:**

- `React Ecosystem Landscape` - the broader context of
  React tooling
- `React Development Environment Setup` - getting
  started with the development environment

**Builds On:**

- `Bundle Size Analysis and Tree Shaking` - optimising
  the Vite/Rollup production bundle
- `Create React App Deprecation (2023)` - deeper analysis
  of the CRA → Vite migration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NEW PROJECT │ npm create vite@latest app -- --template  │
│             │ react  (or react-ts for TypeScript)       │
├──────────────────────────────────────────────────────────┤
│ DEV SERVER  │ npm run dev  → localhost:5173             │
│ PROD BUILD  │ npm run build → dist/ folder             │
│ PREVIEW     │ npm run preview → test prod build locally │
├──────────────────────────────────────────────────────────┤
│ ENV VARS    │ VITE_API_URL=... in .env file             │
│             │ import.meta.env.VITE_API_URL in code      │
├──────────────────────────────────────────────────────────┤
│ CRA STATUS  │ Deprecated (last release: Dec 2022)       │
│             │ DO NOT use for new projects               │
├──────────────────────────────────────────────────────────┤
│ WHEN VITE   │ SPAs, admin dashboards, tools             │
│ WHEN NEXT   │ Content sites, marketing, e-commerce      │
│ WHEN REMIX  │ Full-stack, forms-heavy, progressive      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. CRA is deprecated. Use Vite for new React projects:
   `npm create vite@latest app -- --template react-ts`
2. Vite is fast because it does not bundle files in dev
   mode - it serves files as native ES Modules directly.
3. For production applications, consider Next.js or Remix
   over bare Vite + React - they add SSR, routing, and
   data loading that Vite lacks.

**Interview one-liner:**
"Create React App is deprecated as of 2023. Vite is the
recommended replacement. Vite's dev server is 10-100x
faster than CRA's Webpack because it skips bundling during
development - it serves native ES Modules directly and
transforms files on demand using esbuild (Go-based,
very fast). For new projects, use Vite for SPAs or a
full-stack framework (Next.js, Remix) for content sites."

---

### 💎 Transferable Wisdom

CRA's deprecation illustrates a recurring pattern in
software tooling: the "official blessed path" optimised
for onboarding eventually becomes the bottleneck for
professional use. CRA solved the zero-config problem
perfectly for beginners but could not evolve fast enough
to keep pace with Vite's architectural innovation. The
lesson: evaluate tools not just on "does it work now"
but on "is it architecturally positioned to improve?"
Vite's native ESM approach has room to grow; Webpack's
"bundle everything first" approach has a fundamental
scaling limit.

---

### 💡 The Surprising Truth

Vite was not created for React. Evan You created Vite
as the development server for Vue 3. The React ecosystem
adopted it because the native ESM approach and esbuild
performance were dramatically superior to CRA's Webpack
setup, regardless of framework. The `@vitejs/plugin-react`
was a community/official addition later. This is why Vite
is "framework-agnostic" - it was not designed around any
specific framework's needs. React's own tooling team
effectively outsourced the development tooling problem
to a community project from the Vue ecosystem, and
endorsed it in the official docs.

---

### ✅ Mastery Checklist

1. **CREATE** a new React + TypeScript project with Vite
   and explain what each generated file does (index.html,
   vite.config.ts, main.tsx, App.tsx).
2. **EXPLAIN** why Vite's dev server starts faster than
   CRA's Webpack dev server, using the terms "native ES
   Modules" and "on-demand transformation."
3. **MIGRATE** a CRA project to Vite: update package.json
   scripts, create vite.config.js, move index.html,
   and rename environment variables.
4. **DECIDE** when to use Vite (bare SPA) vs Next.js
   (SSR, file routing) vs Remix (full-stack) for three
   specific project types.
5. **DEBUG** the Node 18+ OpenSSL error in a legacy CRA
   project and explain whether the temporary fix or
   full migration is appropriate.

---

### 🧠 Think About This Before We Continue

**Q1.** Vite uses native ES Modules in development and
Rollup for production bundles. This means the code your
browser executes in development is fundamentally different
from the code in the production bundle (unmoduleised vs
bundled). What class of bugs can appear in production
but not development, and how does `npm run preview`
help catch them?

**Q2.** React's official docs suggest full-stack frameworks
(Next.js, Remix) for new projects rather than bare Vite.
The primary reason is SSR for better LCP (Largest
Contentful Paint). But not every React app needs SSR.
What types of React applications genuinely benefit from
client-side-only rendering (bare Vite), and what is
the cost of using SSR for those applications?

**Q3.** Vite's Hot Module Replacement (HMR) works by
updating only the changed module without a full page
refresh. For a module with side effects (a module that
sets up global state, attaches event listeners, or
starts a WebSocket connection on import), HMR may not
correctly undo the side effects before applying the
update. How does Vite handle modules with side effects
during HMR, and how does the React HMR plugin (Fast
Refresh) address this for React components?
