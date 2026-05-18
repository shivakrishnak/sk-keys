---
id: RCT-031
title: Styled Components and CSS Modules
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★★☆
depends_on: RCT-005, RCT-010
used_by: RCT-033, RCT-059, RCT-069
related: RCT-059, RCT-069, RCT-050
tags:
  - react
  - frontend
  - css
  - styling
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/react/styled-components-and-css-modules/
---

⚡ TL;DR - CSS Modules scope CSS class names to a single
file via build-time transformation (`.module.css`), while
Styled Components generate unique class names at runtime
using CSS-in-JS tagged template literals; both solve
global CSS namespace collisions but with different trade-offs:
CSS Modules = zero runtime cost, Styled Components =
dynamic styles from props, larger JS bundle.

| #031            | Category: React                                                          | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | JSX, React Components                                                    |                 |
| **Used by:**    | Build a React CRUD App, Bundle Size Analysis, Design System Architecture |                 |
| **Related:**    | Bundle Size Analysis, Design System Architecture, XSS Prevention         |                 |

---

### 🔥 The Problem This Solves

**GLOBAL CSS NAMESPACE COLLISION:**
Traditional CSS applies globally. A `.button` class
defined in one file affects ALL elements with class
`button` in the entire app. Large apps with multiple
teams inevitably get:

```css
/* TeamA writes this */
.button {
  background: blue;
  padding: 8px 16px;
}

/* TeamB writes this in a different file */
.button {
  background: red;
  border-radius: 4px;
}
/* Now ALL .button elements are red with border-radius */
```

Both CSS Modules and Styled Components solve this by
scoping styles to specific components, preventing
namespace collisions without requiring complex BEM naming
conventions or style specificity wars.

---

### 📘 Textbook Definition

**CSS Modules** - a CSS file where all class names and
animation names are scoped locally by default. The build
tool (Vite, webpack) transforms `.button` in `Button.module.css`
to a unique class like `Button_button__a3b2c`. The
component imports the styles as a JS object and applies
the generated class name. The transformation is at build-
time. No runtime overhead.

**Styled Components** - a CSS-in-JS library that creates
React components with styles attached. Tagged template
literals contain CSS. At runtime, a unique class name is
generated and injected into the `<head>`. Styles can use
component props for dynamic values. Runtime overhead
but maximum flexibility.

---

### ⏱️ Understand It in 30 Seconds

**CSS Modules:**

```css
/* Button.module.css */
.button {
  background: blue;
  padding: 8px 16px;
}
.danger {
  background: red;
}
```

```jsx
import styles from "./Button.module.css";

function Button({ variant }) {
  return (
    <button
      className={`${styles.button} ${variant === "danger" ? styles.danger : ""}`}
    >
      Click me
    </button>
  );
  // Renders: class="Button_button__a3b2c Button_danger__x7y8z"
}
```

**Styled Components:**

```jsx
import styled from "styled-components";

const Button = styled.button`
  background: ${(props) => (props.danger ? "red" : "blue")};
  padding: 8px 16px;
`;

function App() {
  return <Button danger>Delete</Button>;
}
```

---

### 🔩 First Principles Explanation

**HOW CSS MODULES WORKS:**

```
Build time:
  Button.module.css:  .button { background: blue; }
  Vite/webpack transforms to:
    .Button_button__abc123 { background: blue; }

Bundle output:
  styles = { button: "Button_button__abc123" }
  <button class="Button_button__abc123">

Result: The class name is globally unique (file + name +
  hash).
  No collision with other .button classes.
  ZERO runtime overhead. Pure CSS in the browser.
```

**HOW STYLED COMPONENTS WORKS:**

```
Runtime:
  const Button = styled.button`background: blue;`
  When Button renders:
  1. Hash the template literal → class name "sc-abc123"
  2. Inject .sc-abc123 { background: blue; } into <head>
  3. Apply class to DOM element

Dynamic styles:
  styled.button`background: ${props => props.danger ?
    'red' : 'blue'};`
  When danger=true: injects .sc-abc123 { background: red; }
  When danger=false: injects .sc-abc124 { background:
    blue; }

Runtime overhead: hashing, style injection, style
  deduplication
```

---

### 🧪 Thought Experiment

**THE DESIGN SYSTEM CHOICE:**
You are building a design system for a company. The system
has 40 components (Button, Input, Card, Modal...). Each
component needs themes (light/dark), variants (primary/
secondary/danger), and size variations (sm/md/lg).

With **CSS Modules**: each component has a `.module.css`
file. Variants are separate classes. Theming uses CSS
custom properties (`var(--color-primary)`). Dynamic styles
(e.g., a progress bar width based on a percentage) require
inline styles for the dynamic part.

With **Styled Components**: variants are handled with
props in the template literal. Dynamic styles (progress
bar 73% width) are trivial: `width: ${props => props.progress}%`.
Theming uses a `ThemeProvider`. But: 40 components, each
styled - server-side rendering requires streaming styles
(extra complexity), bundle size grows.

The choice defines your architecture for years. Most
modern design systems at scale have moved to CSS custom
properties + CSS Modules or Tailwind, away from CSS-in-JS.

---

### 🧠 Mental Model / Analogy

> CSS Modules is like a postal address system with unique
> street names per neighborhood. "Main Street" in district
> A becomes "DistrictA_MainStreet_x7y8". Nobody confuses
> it with "Main Street" in district B. The rename happens
> when the city is mapped (at build time). No overhead
> during actual mail delivery (runtime).
>
> Styled Components is like a custom nameplating service.
> When you order a nameplate (render a component), the
> service creates a unique plate on the spot (generates
> class name at runtime), engraves your specific text
> (CSS based on props), and installs it (injects into
> the document head). More flexible (custom engraving),
> but every order takes time to process.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (concept):**
CSS Modules: import a `.module.css` file, use class names
as JS object properties. Build tool makes them unique.
Styled Components: write CSS inside JavaScript using
template literals. Styles are attached to components.

**Level 2 (usage):**
CSS Modules: file must end in `.module.css`. Import as
`styles`. Use as `className={styles.className}`. No extra
dependencies. Styled Components: `npm install styled-components`.
`styled.elementName` with backtick template. Props
available in the template function.

**Level 3 (SSR and performance):**
CSS Modules produce real CSS files. SSR (Next.js, Remix)
works out of the box - styles are in the CSS bundle, not
injected by JS. Styled Components require SSR setup:
`ServerStyleSheet` for Next.js pages router, or just
works in App Router. CSS-in-JS has a "FOUC" risk (flash
of unstyled content) if JS-injected styles load after
the HTML.

**Level 4 (architecture):**
Trend (2023 onwards): CSS-in-JS libraries have performance
overhead that becomes visible at scale. Vercel/Next.js
moved away from styled-components internally. Zero-runtime
CSS-in-JS alternatives (Linaria, vanilla-extract) extract
CSS at build time like CSS Modules. Tailwind CSS bypasses
the entire debate by using utility classes.

**Level 5 (mastery):**
In React 18 Server Components, CSS-in-JS libraries that
require context (styled-components, Emotion) cannot be
used in Server Components (no React context in RSC).
CSS Modules work in RSC because they produce real CSS
files. This is a hard architectural constraint that has
driven migration away from CSS-in-JS in the Next.js
ecosystem. Choosing your styling solution determines
whether your component library is compatible with RSC.

---

### ⚙️ How It Works (Mechanism)

**CSS Modules with conditional classes (clsx library):**

```jsx
// Button.module.css
// .base { ... }
// .primary { ... }
// .danger { ... }
// .sm, .md, .lg { ... }
// .disabled { ... }

import styles from "./Button.module.css";
import clsx from "clsx";

function Button({
  variant = "primary",
  size = "md",
  disabled,
  children,
  onClick,
}) {
  return (
    <button
      className={clsx(
        styles.base,
        styles[variant], // styles.primary, styles.danger
        styles[size], // styles.sm, styles.md, styles.lg
        { [styles.disabled]: disabled },
      )}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

**Styled Components with theme and variants:**

```jsx
import styled, { ThemeProvider } from "styled-components";

const theme = {
  colors: { primary: "#0070f3", danger: "#e00" },
  spacing: { sm: "4px 8px", md: "8px 16px" },
};

const Button = styled.button`
  background: ${({ variant, theme }) =>
    theme.colors[variant] || theme.colors.primary};
  padding: ${({ size,
      theme }) => theme.spacing[size] || theme.spacing.md};
  border: none;
  border-radius: 4px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
  opacity: ${({ disabled }) => (disabled ? 0.5 : 1)};
`;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Button variant="primary" size="md">
        Save
      </Button>
      <Button variant="danger" disabled>
        Delete
      </Button>
    </ThemeProvider>
  );
}
```

---

### 📊 Comparison Table

| Feature                   | CSS Modules             | Styled Components            | Tailwind CSS         |
| ------------------------- | ----------------------- | ---------------------------- | -------------------- |
| Scoping mechanism         | Build-time class rename | Runtime class generation     | Utility class naming |
| Runtime overhead          | None                    | Yes (hashing, injection)     | None                 |
| Dynamic styles from props | Inline styles needed    | Native (template fn)         | Limited              |
| SSR compatibility         | Full                    | Requires setup               | Full                 |
| RSC compatibility         | Full                    | No (needs context)           | Full                 |
| Bundle size               | Small                   | +13KB gzipped                | Varies (PurgeCSS)    |
| Co-location with JS       | Separate file           | Same file                    | Via className        |
| Theming                   | CSS custom properties   | ThemeProvider                | tailwind.config.js   |
| Best for                  | Most projects           | Component libraries (legacy) | Utility-first apps   |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                            |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CSS Modules are compiled away and have zero output"      | CSS Modules produce real CSS files in the build output. The class names are transformed (scoped), but the CSS is still in a `.css` file loaded by the browser, not injected by JavaScript.                                                         |
| "Styled Components generate new classes on every render"  | Styled Components cache generated class names. A given combination of prop values always produces the same class name (hash of template literal + interpolated values). Re-renders with the same props do not generate new styles.                 |
| "CSS Modules cannot do dynamic styles"                    | CSS Modules cannot compute styles from JavaScript values at runtime. But you can: use CSS custom properties (change a CSS variable via inline style `style={{ '--width': progress + '%' }}`), or apply different CSS module classes conditionally. |
| "styled-components v6 works with React Server Components" | As of React 18 / Next.js 13+, styled-components requires React context for theming (ThemeProvider). Server Components do not support context. Styled-components can be used only in Client Components in an RSC app.                               |

---

### 🚨 Failure Modes & Diagnosis

**Security: CSS Injection via User-Controlled Styled Components**

**Symptom:** User-supplied text is directly interpolated
into a styled-component template literal. Malicious
users inject CSS properties that affect the layout or
visibility of other elements.

**Root Cause:**

```jsx
// VULNERABLE: user input in CSS template literal
const UserCard = styled.div`
  color: ${(props) => props.userColor};
`;
// If userColor = "red; position: fixed; top: 0; width: 100vw"
// The entire component tree layout can be attacked
```

**Prevention:** Never interpolate user-supplied values
directly into styled-component CSS. Validate or sanitise
values. Use a safe set of allowed values:

```jsx
// SAFE: only allow from known-good set
const safeColor =
    ALLOWED_COLORS.includes(userColor) ? userColor : "black";
```

---

**Flash of Unstyled Content (FOUC) with CSS-in-JS**

**Symptom:** Server-rendered page briefly shows unstyled
HTML before styles appear.

**Root Cause:** CSS-in-JS styles are injected by JavaScript
after HTML is parsed. The HTML renders first without styles.

**Fix (Next.js pages router):** Use `ServerStyleSheet`:

```jsx
// _document.js
import { ServerStyleSheet } from "styled-components";
// getInitialProps collects styles during SSR
// and injects them into the <head> before HTML is sent
```

In App Router, use only CSS Modules or zero-runtime
CSS-in-JS for RSC-compatible styling.

---

### 🔗 Related Keywords

**Prerequisites:**

- `JSX and Expressions` - applying class names in JSX
- `React Components and Props` - where props flow for
  dynamic Styled Components styling

**Builds On:**

- `Bundle Size Analysis and Tree Shaking` - CSS-in-JS
  bundle overhead analysis
- `Design System Architecture with React` - choosing
  a styling approach for a component library
- `XSS Prevention in React` - CSS injection risk with
  user input in styled-components

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CSS MODULES │ import styles from './X.module.css'       │
│             │ className={styles.button}                 │
│             │ Build-time rename, zero runtime cost      │
├─────────────────────────────────────────────────────────┤
│ STYLED COMP │ const Btn = styled.button`css...`         │
│             │ Dynamic: ${props => props.x ? 'a' : 'b'} │
│             │ Runtime injection, needs RSC workaround   │
├─────────────────────────────────────────────────────────┤
│ SSR         │ CSS Modules: works OOB                    │
│             │ Styled-comp: needs ServerStyleSheet       │
│ RSC (Next13+│ CSS Modules: works in server components   │
│             │ Styled-comp: Client Components only       │
├─────────────────────────────────────────────────────────┤
│ SECURITY    │ Never interpolate user input in CSS-in-JS │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. CSS Modules: `.module.css` file, import as object,
   apply as `className={styles.name}`. Build-time scoping.
   Zero runtime cost.
2. Styled Components: `styled.button\`css\``. Dynamic
   styles via props. Runtime overhead. Cannot be used
   in React Server Components.
3. Choose CSS Modules (or Tailwind) for RSC-compatible
   apps, zero runtime overhead, and simpler mental model.

**Interview one-liner:**
"CSS Modules scope CSS at build time by transforming class
names to unique hashes; zero runtime cost, works in React
Server Components, produces real CSS files. Styled Components
generate unique class names at runtime via CSS-in-JS
tagged template literals, enabling prop-driven dynamic
styles and ThemeProvider, but add bundle size and cannot
be used in Server Components (require React context).
In 2024, most new projects prefer CSS Modules or Tailwind
over CSS-in-JS due to RSC compatibility and performance."

---

### 💎 Transferable Wisdom

The CSS scoping problem is a namespace collision problem
that appears in every large-scale system. In Java:
packages namespace classes. In Python: modules namespace
functions. In CSS: there was no built-in namespace until
CSS Modules and Shadow DOM arrived. The solutions are
always the same: prefixing (BEM: `.button--primary`),
build-time transformation (CSS Modules), or runtime
isolation (Shadow DOM, CSS-in-JS). Each trade-off is
the same: stronger isolation = more overhead or more
ceremony. The "right" choice depends on the isolation
granularity needed and the tolerable overhead.

---

### 💡 The Surprising Truth

Styled Components was one of the dominant React styling
solutions from 2016-2022. But Next.js and the React core
team's pivot to React Server Components in 2023 effectively
obsoleted CSS-in-JS libraries that use React context -
and most popular ones (styled-components, Emotion) do.
The React team's own documentation now recommends CSS
Modules as the default. This is a rare case where an
extremely popular library became architecturally
incompatible with the framework's new direction, not due
to API changes, but due to a fundamental runtime model
change. The lesson: styling architecture choices have
a 5-10 year half-life and must be evaluated against
the framework's roadmap, not just current capabilities.

---

### ✅ Mastery Checklist

1. **IMPLEMENT** a Button component with three variants
   (primary, secondary, danger) and two sizes (sm, md)
   using both CSS Modules and Styled Components - compare
   the implementation.
2. **EXPLAIN** why Styled Components cannot be used in
   React Server Components and what the recommended
   alternative is.
3. **PREVENT** a CSS injection vulnerability in a
   Styled Components codebase where user preferences
   (theme color) are applied via props.
4. **COMPARE** the bundle size impact and runtime
   performance profile of CSS Modules vs Styled Components
   in a production build using Chrome DevTools.
5. **DESIGN** a theming system using CSS custom properties
   (`var(--color-primary)`) with CSS Modules that supports
   light/dark mode switching without any CSS-in-JS.

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is building a public-facing React app
that needs optimal Core Web Vitals (especially LCP and
CLS). You have two candidates: CSS Modules (build-time
scoping) and Styled Components (runtime injection). How
do each affect LCP and CLS specifically? Is there a
measurable FCP difference between server-rendered CSS
(CSS Modules) and JavaScript-injected CSS (Styled
Components)?

**Q2.** A design system library is distributed as a
package on npm. Teams import components from it. If the
library uses CSS Modules, what is the developer experience
for teams using it? If it uses Styled Components? Which
approach produces fewer integration problems, and why?

**Q3.** Tailwind CSS takes a fundamentally different
approach: instead of scoping CSS classes per component,
it provides a fixed set of utility classes that all
components share. This seems to recreate the global
namespace problem, yet teams report no class collision
issues. Why does Tailwind avoid the collision problem
that global CSS has?
