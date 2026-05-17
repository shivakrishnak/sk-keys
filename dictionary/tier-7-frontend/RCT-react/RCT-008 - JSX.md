---
id: RCT-008
title: JSX
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: ★☆☆
depends_on: RCT-007
used_by: RCT-009, RCT-010, RCT-013, RCT-014, RCT-015, RCT-050
related: RCT-007, RCT-011, RCT-050
tags:
  - react
  - frontend
  - syntax
  - jsx
status: complete
version: 4
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /react/jsx/
---

# RCT-008 - JSX

⚡ TL;DR - JSX is JavaScript with HTML-like syntax that
compiles to `React.createElement()` calls; understanding the
compilation step prevents the class/className confusion,
explains the one-root-element rule, and demystifies XSS
protection.

| #008 | Category: React | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Component | |
| **Used by:** | Props, State, Event Handling, Conditional Rendering, List Rendering, XSS Prevention | |
| **Related:** | Component, Virtual DOM, XSS Prevention in React | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without JSX, creating a React UI element requires writing
`React.createElement()` calls directly:

```javascript
React.createElement(
  'div',
  { className: 'card' },
  React.createElement('h2', null, 'Alice'),
  React.createElement('p', null, 'alice@co.com')
)
```

For a non-trivial UI with 5 levels of nesting, this is
nearly unreadable. The structure is lost in function calls.
JSX solves the readability problem: the nested HTML structure
is immediately visible.

**THE INVENTION MOMENT:**
JSX was introduced with React in 2013 as a preprocessor
syntax. Critically, it is NOT a template language - it is
JavaScript with a syntactic transformation. Every JSX
expression is a function call at runtime. This makes it
fully composable with JavaScript: you can use variables,
expressions, and conditionals inline.

---

### 📘 Textbook Definition

**JSX** (JavaScript XML) is a syntax extension for JavaScript
that allows HTML-like markup to be written directly inside
JavaScript files. A build tool (Vite, TypeScript compiler,
Babel) compiles JSX to `React.createElement()` function calls
before execution. JSX is not valid JavaScript - it must be
compiled. It is not HTML - attribute names differ (`class`
becomes `className`, `for` becomes `htmlFor`), self-closing
tags are mandatory (`<img />`), and all expressions must be
valid JavaScript. JSX provides automatic XSS protection by
escaping all values inserted via `{}` before they reach the
DOM.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JSX is HTML-like syntax in JS files that your build tool
compiles into `React.createElement()` calls.

**One analogy:**
> JSX is like SCSS - it is not something the browser
> understands directly. It is a notation that a build tool
> (Vite, TypeScript) transforms into something the browser
> can execute. Just as SCSS compiles to CSS, JSX compiles
> to JavaScript. The human-readable form is JSX; the
> machine-executable form is `React.createElement()`.

**One insight:**
Because JSX compiles to function calls, it is JavaScript.
You can use any JavaScript expression inside `{}` in JSX:
ternary operators, `.map()`, function calls, template
literals. You cannot use statements (`if`, `for`, variable
declarations) inside JSX directly - only expressions.

---

### 🔩 First Principles Explanation

**WHAT THE COMPILER DOES:**

```jsx
// What you write:
const element = (
  <div className="card">
    <h2>{user.name}</h2>
  </div>
);

// What the compiler produces:
const element = React.createElement(
  "div",
  { className: "card" },
  React.createElement("h2", null, user.name)
);

// What React.createElement() returns (a plain object):
{
  type: "div",
  props: {
    className: "card",
    children: {
      type: "h2",
      props: { children: user.name }
    }
  }
}
```

This plain object is the "React element" - the virtual DOM
node. It is just data. React takes this data and eventually
turns it into real DOM nodes.

**THE XSS PROTECTION MECHANISM:**
Any value inserted via `{}` in JSX is automatically escaped
by `React.createElement()`. If `user.name` contains
`<script>alert(1)</script>`, React escapes it to
`&lt;script&gt;...` before inserting it into the DOM. This
makes JSX's `{value}` safe for user-provided strings by
default. The only way to bypass this is `dangerouslySetInnerHTML`.

---

### 🧪 Thought Experiment

**SETUP:**
A backend returns a user's display name from a database.
A malicious user registers with the name:
`<img src=x onerror="document.cookie='stolen=' + document.cookie">`.

**WITHOUT JSX (manual innerHTML):**

```javascript
// VULNERABLE
document.getElementById('username').innerHTML = user.name;
// Renders the <img> tag in the DOM
// onerror fires, cookies are stolen
```

**WITH JSX:**

```jsx
// SAFE - JSX escapes the value
function UserName({ name }) {
  return <span>{name}</span>;
}
// React escapes: <img...> becomes &lt;img...&gt;
// Renders as visible text, not HTML
// No script execution
```

JSX's `{}` is safe for user content by default. The
developer must explicitly opt out of safety via
`dangerouslySetInnerHTML` and must then sanitise manually.
This "safe by default, opt out consciously" pattern is
exactly the right security design.

---

### 🧠 Mental Model / Analogy

> JSX is syntactic sugar. Syntactic sugar means a notation
> that makes code easier to write and read but that compiles
> to something more verbose that the machine understands.
> `async/await` is syntactic sugar over `Promise.then()`.
> JSX is syntactic sugar over `React.createElement()`.
> The human reads the sugar; the machine executes what is
> under it.

**Where this model breaks:**
JSX looks like HTML but it is not HTML. Unlike HTML:
- You must close all tags (`<br />` not `<br>`)
- You must use `className` not `class`
- You must use `htmlFor` not `for`
- Boolean attributes: `disabled={true}` not just `disabled`
- Event handlers: `onClick={fn}` not `onclick="fn()"`
- Comments: `{/* comment */}` not `<!-- comment -->`

These differences exist because JSX compiles to JavaScript
property names (`className` is the JavaScript property of
a DOM element; `class` is the HTML attribute name).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
JSX lets you write what looks like HTML inside your
JavaScript files. It makes React components much easier to
read because the structure of the UI is visible in the code.

**Level 2 - How to use it (junior developer):**
Write HTML-like code in your component's return statement.
Use `className` instead of `class`. Put expressions in `{}`.
Every tag must be closed. A component can only return one
root element (wrap siblings in a `<>...</>` Fragment if needed).

**Level 3 - How it works (mid-level engineer):**
JSX is compiled by Vite/TypeScript to `React.createElement()`
calls. The modern JSX transform (React 17+) imports from
`react/jsx-runtime` automatically - you no longer need
`import React from 'react'` at the top of every file.
The compiled output is a tree of plain JavaScript objects
(React elements).

**Level 4 - Why it was designed this way (senior/staff):**
JSX was designed as a JavaScript transformation (not a
template engine) because it needed to be fully composable
with JavaScript logic. Template engines (Handlebars, Pug,
Mustache) have limited logic capabilities. Because JSX
compiles to function calls, it integrates seamlessly with
TypeScript for type checking of props, and with bundlers
for tree-shaking and dead code elimination.

**Level 5 - Mastery (distinguished engineer):**
The JSX transform is pluggable. You can write a custom JSX
factory function that `React.createElement()` calls map to.
This is how SolidJS, Preact, and Inferno use JSX syntax
but with different runtimes. Setting `jsxImportSource` in
`tsconfig.json` to `solid-js` makes the same JSX compile
to SolidJS reactive primitives instead of React elements.
JSX is a notation; the semantics are defined by the factory.

---

### ⚙️ How It Works (Mechanism)

**The modern JSX transform (React 17+):**

```jsx
// You write:
function App() {
  return <div>Hello</div>;
}

// Compiler produces (automatic import, no React import needed):
import { jsx as _jsx } from 'react/jsx-runtime';

function App() {
  return _jsx('div', { children: 'Hello' });
}
```

**Expression rules - what goes inside `{}`:**

```jsx
// VALID - expressions
{user.name}                // property access
{isLoading ? "..." : name} // ternary
{items.map(i => <li key={i.id}>{i.name}</li>)} // map
{count > 0 && <Badge count={count} />} // short-circuit
{formatDate(date)}         // function call
{"string literal"}         // string
{42}                       // number

// INVALID - statements cannot appear in JSX
{if (x) return y}          // ERROR: if is a statement
{for (let i=0; i<n; i++)}  // ERROR: for is a statement
{const x = 5}              // ERROR: declaration
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FROM JSX TO DOM:**

```
Your .tsx file
  |
  v
TypeScript / Vite compiler
  |
  v (JSX -> React.createElement calls)
  |
JavaScript with React.createElement
  |
  v (at runtime, React calls your component)
  |
React element tree (plain JS objects)
  |
  v (React reconciles against previous tree)
  |
DOM mutation (minimal patch)
  |
  v
Browser renders UI
```

The JSX-to-JavaScript step happens at build time, not
runtime. By the time your code runs in the browser, there
is no JSX - only JavaScript function calls.

---

### 💻 Code Example

**Example 1 - BAD: HTML attributes in JSX:**

```jsx
// BAD: Using HTML attribute names - silently broken
function Form() {
  return (
    <form>
      <label for="email">Email</label>  {/* wrong */}
      <input
        class="input-field"            {/* wrong */}
        type="email"
        id="email"
      />
    </form>
  );
}
// 'for' and 'class' are JavaScript reserved words.
// React (in dev mode) warns but still renders.
// The label association is broken (for != htmlFor).
// The CSS class is not applied ('class' is ignored).
```

**Example 2 - GOOD: Correct JSX attribute names:**

```jsx
// GOOD: JSX attribute names (JavaScript property names)
function Form() {
  return (
    <form>
      <label htmlFor="email">Email</label>
      <input
        className="input-field"
        type="email"
        id="email"
      />
    </form>
  );
}
// htmlFor creates the accessible label-input association
// className applies the CSS class
```

**Example 3 - PRODUCTION: Complex JSX with type safety:**

```tsx
interface User {
  id: string;
  name: string;
  role: 'admin' | 'user';
  isActive: boolean;
}

function UserList({ users }: { users: User[] }) {
  if (users.length === 0) {
    return <p className="empty-state">No users found.</p>;
  }

  return (
    <ul className="user-list">
      {users.map((user) => (
        <li
          key={user.id}
          className={`user-item ${
            user.isActive ? 'user-item--active' : ''
          }`}
        >
          <span>{user.name}</span>
          {user.role === 'admin' && (
            <span className="badge badge--admin">Admin</span>
          )}
        </li>
      ))}
    </ul>
  );
}
```

---

### ⚖️ Comparison Table

| Feature | JSX | HTML | Template Literals |
|---|---|---|---|
| **XSS safety** | Auto-escaped in `{}` | Manual | Manual |
| **Compiled** | Yes (to JS) | No | No |
| **Type checking** | Yes (TypeScript) | No | No |
| **Expressions** | Full JS in `{}` | None | Full JS in `${}` |
| **Conditional rendering** | `&&` / ternary | None | String concat |
| **IDE support** | Excellent | Excellent | Poor |
| **Attribute names** | `className` / `htmlFor` | `class` / `for` | N/A |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JSX is HTML" | JSX is JavaScript syntax. It compiles to function calls. Attribute names differ from HTML. Boolean attributes work differently. Comments use `{/* */}` not `<!-- -->`. |
| "JSX requires React to be imported" | With the React 17+ automatic JSX transform, `import React from 'react'` is no longer needed. The compiler inserts the import from `react/jsx-runtime` automatically. |
| "JSX is safe from XSS by default for all values" | JSX auto-escapes values in `{}`. But `dangerouslySetInnerHTML={{ __html: userInput }}` bypasses this completely. Any use of `dangerouslySetInnerHTML` requires manual sanitisation. |
| "You must return one JSX element from a component" | You must return one root node, but that can be a Fragment (`<>...</>`), which renders to no DOM element. Fragments let you return multiple siblings without a wrapper `<div>`. |

---

### 🚨 Failure Modes & Diagnosis

**Adjacent Elements Without a Root Wrapper**

**Symptom:**
Compiler error: "Adjacent JSX elements must be wrapped in an
enclosing tag."

**Root Cause:**
A component returns two sibling JSX elements without a
parent or Fragment wrapper.

```jsx
// BAD: two adjacent elements
function NavLinks() {
  return (
    <a href="/home">Home</a>
    <a href="/about">About</a>  // ERROR
  );
}
```

**Fix:**
Wrap in a Fragment to avoid adding an extra DOM node:

```jsx
// GOOD: Fragment wrapper - no extra DOM element
function NavLinks() {
  return (
    <>
      <a href="/home">Home</a>
      <a href="/about">About</a>
    </>
  );
}
```

---

**Security: XSS via `dangerouslySetInnerHTML`**

**Symptom:**
User-provided rich text is rendered without escaping, and a
malicious user can execute JavaScript.

**Root Cause:**
`dangerouslySetInnerHTML={{ __html: userInput }}` bypasses
JSX's auto-escaping.

**Fix:**
Sanitise before setting. Use DOMPurify:

```tsx
import DOMPurify from 'dompurify';

function RichContent({ html }: { html: string }) {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: DOMPurify.sanitize(html),
      }}
    />
  );
}
// DOMPurify.sanitize removes <script>, onclick="...",
// javascript: hrefs, and other attack vectors.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Component` - JSX is what components return; understanding
  components first gives context for JSX's role

**Builds On This (learn these next):**
- `Props` - JSX attribute syntax directly corresponds to
  props passed to components
- `Conditional Rendering` - how `&&` and ternary work in JSX
- `List Rendering and the key Prop` - how `.map()` is used
  in JSX for lists
- `XSS Prevention in React` - the security model built into JSX

**Alternatives / Comparisons:**
- `Hyperscript` (`h()`) - the function-based API that JSX
  compiles to; used directly in Preact and SolidJS
- `Vue templates` - declarative template syntax with
  directives (`v-if`, `v-for`); similar expressiveness but
  different compilation model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ HTML-like syntax in JS that compiles to  │
│              │ React.createElement() function calls     │
├──────────────┼───────────────────────────────────────────┤
│ KEY DIFFS    │ className (not class)                    │
│ FROM HTML    │ htmlFor (not for)                        │
│              │ self-closing: <img /> (not <img>)        │
│              │ comments: {/* */} (not <!-- -->)         │
├──────────────┼───────────────────────────────────────────┤
│ EXPRESSIONS  │ Any JS expression in {}                  │
│              │ No statements (if/for/const) in JSX     │
├──────────────┼───────────────────────────────────────────┤
│ XSS SAFETY   │ {} auto-escapes user values              │
│              │ dangerouslySetInnerHTML bypasses safety  │
├──────────────┼───────────────────────────────────────────┤
│ ONE ROOT     │ Return one root; use <> Fragment to      │
│              │ avoid extra DOM wrapper element          │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ dangerouslySetInnerHTML with unsan-      │
│              │ itised user input; 'class' not className │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Readable structure vs learning the       │
│              │ HTML-to-JSX attribute differences        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSX compiles to JS function calls;      │
│              │  {} auto-escapes for XSS safety."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Props -> Conditional Rendering -> Lists  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. JSX compiles to `React.createElement()`. The browser
   never sees JSX - only JavaScript. This means every JSX
   feature is a JavaScript feature in disguise.
2. Use `className` not `class`, `htmlFor` not `for`.
   These map to JavaScript DOM property names, not HTML
   attribute names.
3. Values in `{}` are auto-escaped. This is React's XSS
   protection. Never use `dangerouslySetInnerHTML` with
   unsanitised user input - always run through DOMPurify.

**Interview one-liner:**
"JSX is a JavaScript syntax extension that compiles to
`React.createElement()` calls at build time. It is not
HTML - attribute names like `className` and `htmlFor`
map to JavaScript property names. Values in `{}` are
automatically escaped, which prevents XSS by default.
The only unsafe pattern is `dangerouslySetInnerHTML`,
which bypasses this protection and requires explicit
sanitisation with DOMPurify."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Safe by default, opt out explicitly" is a sound security
design. JSX's auto-escaping follows this principle: user
input is safe by default, and bypassing safety requires
a conspicuous API (`dangerouslySetInnerHTML`) that signals
danger to any code reviewer. Applied elsewhere: database
queries should use parameterised queries by default (safe),
with raw SQL injection-prone paths requiring an explicit
unsafe method.

**Where else this pattern appears:**
- Python's `markupsafe.Markup` - escapes HTML strings by
  default; bypass requires explicit `Markup()` wrapper
- Go's `html/template` package - auto-escapes by context;
  `template.HTML(str)` marks a string as safe to bypass
- SQL parameterised queries - values are escaped by default;
  string interpolation is the unsafe opt-out

---

### 💡 The Surprising Truth

JSX does not require React. The JSX syntax is a general-purpose
notation that can compile to calls to any factory function.
SolidJS uses JSX to generate reactive signals and DOM
operations (no virtual DOM at all). Preact uses it to call
`h()` - a drop-in replacement for `React.createElement()`.
Million.js compiles JSX to a faster virtual DOM implementation.
The JSX transform in TypeScript (`jsxImportSource` in tsconfig)
controls which factory receives the compiled calls. When an
engineer says "I'm using JSX" they are saying nothing about
which runtime they are using.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Write the `React.createElement()` equivalent
   of a given JSX snippet with two levels of nesting, showing
   the exact function call structure.
2. **AUDIT** Given a component that renders user-provided
   content, identify every `dangerouslySetInnerHTML` usage
   and either confirm DOMPurify is applied or add it.
3. **DEBUG** Given a JSX compilation error ("Adjacent JSX
   elements"), fix it using a Fragment rather than a wrapper
   `<div>`, and explain why the Fragment is preferable.
4. **CONVERT** Take a component written with direct
   `React.createElement()` calls (legacy codebase or
   curiosity) and rewrite it as idiomatic JSX.
5. **EXTEND** Configure `jsxImportSource` in `tsconfig.json`
   to use a non-React JSX factory (e.g., Preact's `h`) and
   explain what changes in the compiled output.

---

### 🧠 Think About This Before We Continue

**Q1.** JSX auto-escapes values in `{}`. React's documentation
describes this as protection against injection attacks. But
the auto-escaping applies to strings inserted as text content,
not to attribute values like `href`. If an attacker controls
the value of `href` in `<a href={userInput}>`, could they
execute JavaScript? What attack vector does this represent,
and how should `href` values be validated?
*Hint: `javascript:alert(1)` is a valid URL.*

**Q2.** JSX uses `&&` for conditional rendering:
`{isLoading && <Spinner />}`. In JavaScript, `0 && expr`
evaluates to `0`. What happens when React renders `{0}` in
JSX? This is a known JSX gotcha. How should the conditional
be written to avoid it?
*Hint: JSX renders numbers as text. `{0}` renders "0" in
the UI.*

**Q3.** The modern JSX transform (React 17+) removed the
need to `import React from 'react'` at the top of every
file. If you are working on a large codebase that still has
these imports everywhere, is removing them a safe
refactoring? What would break if you removed them, and
how would you automate the cleanup?
*Hint: `react-codemod` has a transform for this.*