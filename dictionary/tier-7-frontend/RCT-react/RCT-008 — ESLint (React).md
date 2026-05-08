---
layout: default
title: "ESLint (React)"
parent: "React"
nav_order: 8
permalink: /react/eslint-react/
id: RCT-008
category: React
difficulty: ★★☆
depends_on: JavaScript, React, TypeScript
used_by: CI-CD, Code Quality
related: Prettier, SonarQube Quality Gate, TypeScript
tags:
  - react
  - javascript
  - cicd
  - bestpractice
  - intermediate
---

# RCT-008 — ESLint (React)

⚡ **TL;DR —** ESLint with React plugins catches Rules of Hooks violations, prop errors, and accessibility bugs statically — before they reach the browser or CI.

| Relationship | Keywords |
|---|---|
| **Depends on** | JavaScript, React, TypeScript |
| **Used by** | CI-CD, Code Quality |
| **Related** | Prettier, SonarQube Quality Gate, TypeScript |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You ship a React component that conditionally calls a hook inside an `if` statement. It works in development but throws an unhandled error in production under a specific user interaction. You spend four hours bisecting the bug. Another developer passes a stale function reference to a `useEffect` dependency array, creating an infinite render loop only reproducible under load. These bugs share one characteristic: a static analyser would have caught them in under one second.

**THE BREAKING POINT:**
React's hook system has hard invariants: hooks must be called in the same order on every render. `useEffect` must declare all values it reads in its dependency array. These rules cannot be enforced by TypeScript's type system alone. Without a dedicated linter, they are enforced only at runtime — by crashes and subtle behavioural bugs in production.

**THE INVENTION MOMENT:**
The React team published the **Rules of Hooks** as part of the React Hooks RFC. They immediately shipped `eslint-plugin-react-hooks` to enforce those rules statically. The community added `eslint-plugin-react` for JSX and component best practices, and `eslint-plugin-jsx-a11y` for accessibility. ESLint v9 introduced flat config, replacing cascading `.eslintrc` files with a single `eslint.config.js`. Together these plugins form a safety net that catches entire classes of React bugs before the developer even saves the file.

---

### 📘 Textbook Definition

**ESLint (React)** is the configuration of ESLint with React-specific plugins — `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-jsx-a11y`, and `@typescript-eslint` — to perform static analysis on React component code. It parses JSX and TypeScript syntax, enforces the Rules of Hooks, validates prop types and accessible naming, and runs in editors, pre-commit hooks, and CI pipelines to block invalid code before it executes.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A static spell-checker for React rules that finds hook violations, stale closures, and a11y errors at save time.

> ESLint for React is like a building code inspector who checks your blueprints before construction begins — not after the wall has already collapsed.

**One insight:** The Rules of Hooks cannot be verified by TypeScript. Only a dedicated AST-level linter can track call order across conditional branches — which is exactly why `eslint-plugin-react-hooks` exists as a non-optional tool.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Hooks must be called in the same order on every render — no hooks inside `if`, loops, or nested functions.
2. Every `useEffect` (and `useCallback`, `useMemo`) must declare every reactive value it reads in its dependency array.
3. React components must return renderable output and follow component naming conventions.
4. JSX that renders interactive elements must include accessible names and correct ARIA roles.
5. Lint rules must run in CI; editor-only linting is insufficient for team enforcement.

**DERIVED DESIGN:**
ESLint parses source code into an Abstract Syntax Tree (AST). Plugins register AST visitor functions that fire on specific node types (e.g., `CallExpression` where callee starts with `use`). Rules inspect AST nodes, check invariants, and emit errors or warnings. The `exhaustive-deps` rule performs data-flow analysis across the AST to track which outer-scope values are referenced inside effect callbacks.

**THE TRADE-OFFS:**

**Gain:** Entire classes of runtime bugs caught statically. Hook invariant violations, stale closures, missing prop keys, and a11y errors become compile-time failures, not production incidents.

**Cost:** Initial config takes time (especially flat config migration in ESLint v9). `exhaustive-deps` produces false positives for intentionally stable references, requiring per-line suppression comments that add noise. TypeScript + ESLint parsing requires `@typescript-eslint/parser` and careful coordination to avoid duplicate type checking.

---

### 🧪 Thought Experiment

**SETUP:** A developer writes a `UserCard` component that conditionally calls `useUser` inside an `if (isAdmin)` check. The component works for admin users — the only users in the dev environment.

**WHAT HAPPENS WITHOUT ESLint:**
The code is reviewed visually. No reviewer notices the conditional hook. The component ships to production. Regular users who are not admins trigger the component. React's hook index desynchronizes between renders. The component throws a runtime error for 85% of users. The on-call engineer debugs for six hours. The fix is a three-line change.

**WHAT HAPPENS WITH ESLint:**
The developer saves the file. The editor shows a red underline: `react-hooks/rules-of-hooks: React Hook "useUser" cannot be called inside a condition.` The developer sees the error before switching tabs. Fix time: 10 seconds.

**THE INSIGHT:** Static analysis does not make you a better developer — it eliminates the need to be perfect. It converts runtime surprises into edit-time corrections.

---

### 🧠 Mental Model / Analogy

> Think of ESLint as a compiler for React conventions. A TypeScript compiler checks types. ESLint checks architectural invariants — hook call order, effect dependencies, accessible names. These are things that TypeScript's type system has no model for, so they need their own analysis pass.

- **TypeScript compiler** → checks types and interfaces
- **ESLint + react-hooks plugin** → checks hook call order and dependency arrays
- **ESLint + jsx-a11y plugin** → checks accessibility contracts
- **ESLint + react plugin** → checks JSX conventions and component structure
- **CI gate** → enforces all of the above for every commit

Where this analogy breaks down: A compiler rejects invalid programs at build time; ESLint warnings can be suppressed with comments, which a compiler cannot. Discipline is still required.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ESLint is a code checker that reads your JavaScript or TypeScript files and warns you about mistakes before you run the code. For React, it knows the specific rules React requires — like where you can and cannot put hooks — and tells you when you break them.

**Level 2 — How to use it (junior developer):**
Install `eslint`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, and `eslint-plugin-jsx-a11y`. Install the ESLint VS Code extension. Create an `eslint.config.js` file. The editor will show red and yellow underlines on violations. Run `npx eslint src/` to see all errors. Add `eslint --max-warnings 0` to your CI pipeline.

**Level 3 — How it works (mid-level engineer):**
ESLint uses a parser (`@typescript-eslint/parser` for TypeScript) to convert source code into an AST. Each plugin registers visitor functions against AST node types. `rules-of-hooks` tracks call sites of functions starting with `use` and verifies they never appear inside conditional branches or loops by walking the AST control flow graph. `exhaustive-deps` performs data-flow analysis to build the set of reactive values referenced inside an effect callback and compares it against the declared `deps` array.

**Level 4 — Why it was designed this way (senior/staff):**
The `exhaustive-deps` rule is one of the most sophisticated static analyses in the JavaScript ecosystem. It must resolve: which identifiers are reactive (come from state/props/context), which are stable (refs, `setState`), and which are truly external constants. It uses ESLint's scope analysis to track variable declarations and assignments across closures. This is why `exhaustive-deps` cannot simply be disabled — it enforces a correctness invariant that the React runtime depends on. Teams that disable it consistently ship stale-closure bugs. The correct approach is to fix the component's data flow so the rule is naturally satisfied.

---

### ⚙️ How It Works (Mechanism)

```
Source file (.tsx)
       ↓
ESLint Parser (@typescript-eslint/parser)
       ↓
    AST (Abstract Syntax Tree)
       ↓
+----------------------------------+
| Plugin Visitors                  |
|  react-hooks/rules-of-hooks      |
|    → checks hook call sites      |
|  react-hooks/exhaustive-deps     |
|    → checks dependency arrays    |
|  jsx-a11y/alt-text               |
|    → checks img alt attributes   |
|  react/jsx-key                   |
|    → checks list key props       |
+----------------------------------+
       ↓
  Diagnostics (errors / warnings)
       ↓
  Editor underlines  /  CLI output
  Pre-commit hook    /  CI failure
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes JSX + hooks
  → ESLint VS Code extension analyses on save
    → Red underline: rules-of-hooks violation
      → Developer fixes before context-switching
        → git commit                ← YOU ARE HERE
          → lint-staged runs eslint --fix
            → Husky blocks commit if errors remain
              → CI runs eslint --max-warnings 0
                → PR blocked until lint passes
```

**FAILURE PATH:**
```
eslint-plugin-react-hooks not installed
  → No static analysis of hook call order
    → Conditional hook ships to production
      → Runtime error for % of users
        → Six-hour on-call incident
          → Three-line fix in the morning
```

**WHAT CHANGES AT SCALE:**
At 50+ developers, ad-hoc lint configs diverge. Teams standardise on a shared config package (`@company/eslint-config-react`) published to the internal registry. Flat config makes this simpler: `eslint.config.js` imports the shared config and merges per-project overrides. CI enforces `--max-warnings 0` with zero tolerance. New rules are introduced via a migration PR that auto-fixes existing violations with `eslint --fix`.

---

### 🔁 Flow / Lifecycle

**ESLint in the Development Pipeline:**

```
1. INSTALL
   npm install -D eslint
     eslint-plugin-react
     eslint-plugin-react-hooks
     eslint-plugin-jsx-a11y
     @typescript-eslint/eslint-plugin
     @typescript-eslint/parser

2. DEVELOP
   VS Code ESLint extension shows violations inline.
   Errors appear as red underlines at save time.
   Quick Fix: eslint --fix for auto-fixable rules.

3. COMMIT (lint-staged + Husky)
   lint-staged runs: eslint --fix on staged .tsx files.
   Husky pre-commit hook: fails on remaining errors.
   Prevents any lint violation from entering history.

4. CI (required check)
   eslint --max-warnings 0 fails on any warning.
   PR cannot merge until lint passes.
   Violations are visible in PR diff annotations.

5. EVOLVE
   Add new rule → run eslint --fix across codebase.
   Update shared config package → bump version.
   Review disable comments quarterly; remove if stale.
```

---

### 💻 Code Example

**BAD — common violations caught by ESLint:**
```tsx
// ❌ rules-of-hooks: hook inside condition
function UserCard({ isAdmin }: { isAdmin: boolean }) {
  if (isAdmin) {
    const user = useAdminUser(); // VIOLATION
  }
  return <div />;
}

// ❌ exhaustive-deps: stale closure — userId not in deps
function Profile({ userId }: { userId: string }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchUser(userId).then(setData);
  }, []); // VIOLATION — userId missing from deps
  return <div>{data?.name}</div>;
}

// ❌ jsx-a11y/alt-text: img with no alt
function Avatar({ src }: { src: string }) {
  return <img src={src} />; // VIOLATION
}
```

**GOOD — all violations resolved:**
```tsx
// ✅ Hook always called, role checked inside
function UserCard({ isAdmin }: { isAdmin: boolean }) {
  const user = useUser(); // called unconditionally
  if (!isAdmin) return null;
  return <div>{user.name}</div>;
}

// ✅ userId in deps — re-fetches when userId changes
function Profile({ userId }: { userId: string }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchUser(userId).then(setData);
  }, [userId]); // correct deps
  return <div>{data?.name}</div>;
}

// ✅ Descriptive alt for meaningful images
function Avatar({ src, name }: { src: string; name: string }) {
  return <img src={src} alt={`${name}'s avatar`} />;
}
```

**ESLint Flat Config (`eslint.config.js`):**
```js
// eslint.config.js (ESLint v9 flat config)
import js from '@eslint/js';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import reactPlugin from 'eslint-plugin-react';
import hooksPlugin from 'eslint-plugin-react-hooks';
import a11yPlugin from 'eslint-plugin-jsx-a11y';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { project: './tsconfig.json' },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      'react': reactPlugin,
      'react-hooks': hooksPlugin,
      'jsx-a11y': a11yPlugin,
    },
    rules: {
      // Hooks invariants — never disable these
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      // JSX best practices
      'react/jsx-key': 'error',
      'react/no-array-index-key': 'warn',
      // Accessibility
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/aria-props': 'error',
      'jsx-a11y/interactive-supports-focus': 'error',
    },
    settings: {
      react: { version: 'detect' },
    },
  },
];
```

---

### ⚖️ Comparison Table

| Plugin | What It Catches | Severity | Can Auto-Fix |
|---|---|---|---|
| `react-hooks/rules-of-hooks` | Hook in condition / loop | Error | No |
| `react-hooks/exhaustive-deps` | Missing effect deps | Warn | Partial |
| `jsx-a11y/alt-text` | Missing img alt | Error | No |
| `jsx-a11y/aria-props` | Invalid ARIA attrs | Error | No |
| `react/jsx-key` | Missing list keys | Error | No |
| `@typescript-eslint/no-explicit-any` | `any` usage | Warn | No |
| `react/display-name` | Anonymous components | Warn | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "TypeScript already checks everything ESLint does" | TypeScript checks types and interfaces. It has no model for hook call order, effect dependency arrays, or ARIA correctness. These require AST-level analysis that only ESLint plugins provide. |
| "I can disable `exhaustive-deps` — it gives false positives" | It gives correct results that indicate a data-flow problem. When it fires, the fix is almost always restructuring the effect, not suppressing the rule. Disabling it consistently leads to stale-closure bugs in production. |
| "ESLint and Prettier can run together as separate tools" | They conflict on formatting rules. The correct setup: `eslint-config-prettier` disables ESLint's formatting rules, and Prettier handles formatting independently. Never run both on formatting. |
| "Editor ESLint is enough; I don't need CI enforcement" | Developers can toggle the extension, disable rules per-line, or use other editors. CI enforcement with `--max-warnings 0` is the only reliable gate. |
| "All ESLint errors auto-fix with `--fix`" | Only a subset of rules are auto-fixable (spacing, import order, some JSX). `rules-of-hooks` violations require manual refactoring because the fix changes component logic. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1 — Stale closure from missing `useEffect` dep**

**Symptom:** An effect reads a prop or state value but the effect only runs once. After the value changes, the effect operates on the old (stale) value. Bug is intermittent and hard to reproduce in development.

**Root Cause:** `exhaustive-deps` warning was suppressed or ignored. The prop is not in the dependency array.

**Diagnostic:**
```bash
# Run ESLint and look for exhaustive-deps warnings:
npx eslint src/ --rule '{"react-hooks/exhaustive-deps":"error"}'

# Typical output:
# src/Profile.tsx:8:5
# React Hook useEffect contains a call to 'fetchUser'.
# Without a list of dependencies, every render could
# return a new value. Add 'userId' to the dep array.
```

**Fix:**
```tsx
// BAD: stale userId after prop change
useEffect(() => {
  fetchUser(userId).then(setData);
}, []); // eslint-disable-line ← BAD suppression

// GOOD: effect re-runs when userId changes
useEffect(() => {
  fetchUser(userId).then(setData);
}, [userId]);
```

**Prevention:** Set `react-hooks/exhaustive-deps` to `"error"` (not `"warn"`) in CI. Warn in editor, error in pipeline. Never allow `eslint-disable` comments for this rule in PRs.

---

**Failure Mode 2 — ESLint and Prettier in conflict**

**Symptom:** Running `eslint --fix` reformats code one way; running `prettier --write` reformats it the opposite way. Every save triggers infinite reformatting. Engineers disable one or both tools in frustration.

**Root Cause:** ESLint has formatting rules enabled (e.g., `indent`, `quotes`, `semi`) that conflict with Prettier's output.

**Diagnostic:**
```bash
# Check for conflicting rules:
npx eslint-config-prettier src/App.tsx
# Output lists which ESLint rules conflict with Prettier.
# Example: "indent" rule conflicts — disable it in ESLint.
```

**Fix:**
```js
// eslint.config.js — add prettier config last
// It disables all ESLint formatting rules
import prettierConfig from 'eslint-config-prettier';

export default [
  // ...other configs...
  prettierConfig, // must be LAST — overrides formatting rules
];
```

**Prevention:** Always add `eslint-config-prettier` when both tools are used. Never enable ESLint formatting rules in projects that use Prettier. Let Prettier own all formatting decisions.

---

**Failure Mode 3 — ESLint passes locally, fails in CI**

**Symptom:** Developer's local run shows zero errors. CI pipeline shows 15 errors. PR is blocked. Developer is confused and frustrated.

**Root Cause:** Local `.eslintrc.js` and CI config differ — often because the local file has a `root: true` override, uses an older plugin version, or a `NODE_ENV`-conditional config.

**Diagnostic:**
```bash
# Compare configs: run ESLint with debug output
npx eslint --debug src/App.tsx 2>&1 | grep "Config"
# Shows which config files are loaded in which order.

# In CI, print the resolved config for a file:
npx eslint --print-config src/App.tsx
# Compare this output between local and CI.
```

**Fix:**
```bash
# Ensure CI uses the same Node and plugin versions:
# package.json — pin ESLint plugin versions exactly
{
  "devDependencies": {
    "eslint": "9.14.0",
    "eslint-plugin-react-hooks": "5.0.0"
  }
}
# Run npm ci (not npm install) in CI for reproducible deps
```

**Prevention:** Use a flat `eslint.config.js` at the project root (no cascading). Commit `package-lock.json` and use `npm ci` in CI. Add an ESLint version check to the CI setup step.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- JavaScript — AST structure, scope, closures, and module system
- React — hooks model, Rules of Hooks, effect cleanup lifecycle
- TypeScript — type annotations and `tsconfig.json` parser options

**Builds On This (learn these next):**
- Prettier — opinionated formatter that resolves the formatting concerns ESLint should not own
- CI-CD — integrating `eslint --max-warnings 0` as a required pipeline gate
- Code Quality — SonarQube and broader quality metrics that complement ESLint

**Alternatives / Comparisons:**
- Biome — all-in-one linter + formatter (Rust-based, faster, fewer plugins)
- TSLint — deprecated TypeScript linter replaced by `@typescript-eslint`
- oxlint — experimental Rust-based ESLint-compatible linter (fast, limited rules)

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS   | Static analysis for React/TS source    |
| PROBLEM      | Hook violations only caught at runtime  |
| KEY INSIGHT  | rules-of-hooks needs AST, not types    |
| USE WHEN     | Every React project — non-negotiable    |
| AVOID WHEN   | Never disable rules-of-hooks or a11y   |
| TRADE-OFF    | Config overhead; exhaustive-deps noise  |
| ONE-LINER    | Catch bugs at save, not in production  |
| NEXT EXPLORE | Prettier, CI-CD, @typescript-eslint    |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction — Type A)** `eslint-plugin-react-hooks/exhaustive-deps` fires on a `useEffect` where you intentionally want the effect to run only once, but the callback reads a prop that changes. What are the three different solutions to satisfy the linter correctly, and what are the trade-offs of each?

2. **(Scale — Type B)** Your monorepo has 12 React apps and 3 shared component packages. Each app currently has its own `.eslintrc.js` with slight variations. ESLint v9 flat config has been released. Design a strategy for consolidating these configs into a single shared package while allowing per-app overrides and avoiding a big-bang migration.

3. **(Design Trade-off — Type C)** `eslint-plugin-jsx-a11y` catches roughly 30–40% of WCAG violations. A colleague argues it gives a false sense of security and should not be run if the team cannot also do manual AT testing. How do you respond, and how would you position automated lint rules within a broader accessibility testing strategy?
