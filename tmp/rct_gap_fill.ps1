# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\rct_gap_fill.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)
$base = 'dictionary\tier-7-frontend\RCT-react'

function Write-Stub($id, $title, $diff, $tags, $slug) {
    $titleVal = if ($title -match ': ') { "`"$title`"" } else { $title }
    $tagLines = ($tags | ForEach-Object { "  - $_" }) -join "`n"
    $nav = [int]($id.Split('-')[1])
    $content = @"
---
id: $id
title: $titleVal
category: React
tier: tier-7-frontend
folder: RCT-react
difficulty: $diff
depends_on:
used_by:
related:
tags:
$tagLines
status: draft
version: 0
layout: default
parent: "React"
grand_parent: "Technical Dictionary"
nav_order: $nav
permalink: /react/$slug/
---
"@
    $fp = "$base\$id - $title.md"
    [System.IO.File]::WriteAllText($fp, $content, $enc)
    Write-Host "Created: $id"
}

$created = 0

# ── L1 Foundational (RCT-024 to RCT-045) ─────────────────────────────────────
Write-Stub "RCT-024" "JSX Syntax and Rules"                          "★☆☆" @("react","javascript","foundational")       "jsx-syntax-and-rules"
Write-Stub "RCT-025" "Functional Components"                         "★☆☆" @("react","javascript","foundational")       "functional-components"
Write-Stub "RCT-026" "Props and Prop Types"                          "★☆☆" @("react","javascript","foundational")       "props-and-prop-types"
Write-Stub "RCT-027" "State with useState Hook"                      "★☆☆" @("react","javascript","foundational")       "state-with-usestate-hook"
Write-Stub "RCT-028" "Side Effects with useEffect Hook"              "★☆☆" @("react","javascript","foundational")       "side-effects-with-useeffect-hook"
Write-Stub "RCT-029" "Event Handling in React"                       "★☆☆" @("react","javascript","foundational")       "event-handling-in-react"
Write-Stub "RCT-030" "Conditional Rendering"                         "★☆☆" @("react","javascript","foundational")       "conditional-rendering"
Write-Stub "RCT-031" "Lists and Keys"                                "★☆☆" @("react","javascript","foundational")       "lists-and-keys"
Write-Stub "RCT-032" "React DevTools"                                "★☆☆" @("react","javascript","foundational")       "react-devtools"
Write-Stub "RCT-033" "React Project Setup (Vite, CRA)"               "★☆☆" @("react","javascript","foundational")       "react-project-setup-vite-cra"
Write-Stub "RCT-034" "Component Composition"                         "★☆☆" @("react","javascript","foundational")       "component-composition"
Write-Stub "RCT-035" "Lifting State Up"                              "★☆☆" @("react","javascript","foundational")       "lifting-state-up"
Write-Stub "RCT-036" "Controlled vs Uncontrolled Components"         "★★☆" @("react","javascript","intermediate")      "controlled-vs-uncontrolled-components"
Write-Stub "RCT-037" "Forms in React"                                "★★☆" @("react","javascript","intermediate")      "forms-in-react"
Write-Stub "RCT-038" "Fragments and Portals"                         "★★☆" @("react","javascript","intermediate")      "fragments-and-portals"
Write-Stub "RCT-039" "Children Prop and Render Props"                "★★☆" @("react","javascript","intermediate")      "children-prop-and-render-props"
Write-Stub "RCT-040" "React Router (v6)"                             "★★☆" @("react","javascript","intermediate")      "react-router-v6"
Write-Stub "RCT-041" "React Context API"                             "★★☆" @("react","javascript","intermediate")      "react-context-api"
Write-Stub "RCT-042" "Custom Hooks Pattern"                          "★★☆" @("react","javascript","pattern")           "custom-hooks-pattern"
Write-Stub "RCT-043" "useRef Hook"                                   "★★☆" @("react","javascript","intermediate")      "useref-hook"
Write-Stub "RCT-044" "useMemo and useCallback"                       "★★☆" @("react","javascript","performance")       "usememo-and-usecallback"
Write-Stub "RCT-045" "Error Boundaries"                              "★★☆" @("react","javascript","intermediate")      "error-boundaries"

# ── L2 Working (RCT-046 to RCT-063) ─────────────────────────────────────────
Write-Stub "RCT-046" "React Query - TanStack Query"                  "★★☆" @("react","javascript","intermediate")      "react-query-tanstack-query"
Write-Stub "RCT-047" "Zustand State Management"                      "★★☆" @("react","javascript","intermediate")      "zustand-state-management"
Write-Stub "RCT-048" "Redux Toolkit"                                 "★★☆" @("react","javascript","intermediate")      "redux-toolkit"
Write-Stub "RCT-049" "React Hook Form"                               "★★☆" @("react","javascript","intermediate")      "react-hook-form"
Write-Stub "RCT-050" "Lazy Loading and Code Splitting"               "★★☆" @("react","javascript","performance")       "lazy-loading-and-code-splitting"
Write-Stub "RCT-051" "React.memo and PureComponent"                  "★★☆" @("react","javascript","performance")       "react-memo-and-purecomponent"
Write-Stub "RCT-052" "React Testing Library Basics"                  "★★☆" @("react","testing","intermediate")        "react-testing-library-basics"
Write-Stub "RCT-053" "Storybook for React Components"                "★★☆" @("react","testing","intermediate")        "storybook-for-react-components"
Write-Stub "RCT-054" "CSS-in-JS (Styled Components, Emotion)"        "★★☆" @("react","css","intermediate")            "css-in-js-styled-components-emotion"
Write-Stub "RCT-055" "Tailwind CSS with React"                       "★★☆" @("react","css","intermediate")            "tailwind-css-with-react"
Write-Stub "RCT-056" "Next.js Fundamentals (SSR, SSG, ISR)"          "★★☆" @("react","javascript","intermediate")      "nextjs-fundamentals-ssr-ssg-isr"
Write-Stub "RCT-057" "Next.js App Router"                            "★★☆" @("react","javascript","intermediate")      "nextjs-app-router"
Write-Stub "RCT-058" "Vite Build Configuration"                      "★★☆" @("react","build","intermediate")          "vite-build-configuration"
Write-Stub "RCT-059" "Environment Variables in React"                "★★☆" @("react","javascript","intermediate")      "environment-variables-in-react"
Write-Stub "RCT-060" "React Strict Mode"                             "★★☆" @("react","javascript","intermediate")      "react-strict-mode"
Write-Stub "RCT-061" "useReducer Hook"                               "★★☆" @("react","javascript","intermediate")      "usereducer-hook"
Write-Stub "RCT-062" "Compound Components Pattern"                   "★★★" @("react","javascript","pattern")           "compound-components-pattern"
Write-Stub "RCT-063" "Higher-Order Components (HOC)"                 "★★★" @("react","javascript","pattern")           "higher-order-components-hoc"

# ── L3 Intermediate (RCT-064 to RCT-072) ────────────────────────────────────
Write-Stub "RCT-064" "React Suspense and Concurrent Features"        "★★★" @("react","javascript","advanced")          "react-suspense-and-concurrent-features"
Write-Stub "RCT-065" "React Performance Optimization Patterns"       "★★★" @("react","javascript","performance")       "react-performance-optimization-patterns"
Write-Stub "RCT-066" "State Management Architecture Decisions"       "★★★" @("react","architecture","advanced")        "state-management-architecture-decisions"
Write-Stub "RCT-067" "React Server Components (Deep Dive)"           "★★★" @("react","javascript","advanced")          "react-server-components-deep-dive"
Write-Stub "RCT-068" "Hydration and Server-Side Rendering Internals" "★★★" @("react","javascript","advanced")          "hydration-and-server-side-rendering-internals"
Write-Stub "RCT-069" "React Testing Strategies (Unit, Integration)"  "★★★" @("react","testing","advanced")             "react-testing-strategies"
Write-Stub "RCT-070" "React with TypeScript Patterns"                "★★★" @("react","typescript","advanced")          "react-with-typescript-patterns"
Write-Stub "RCT-071" "Accessibility Testing in React (axe, jest-axe)""★★★" @("react","testing","advanced")             "accessibility-testing-in-react"
Write-Stub "RCT-072" "React Internationalization (i18n)"             "★★★" @("react","javascript","advanced")          "react-internationalization-i18n"

Write-Host "`nTotal RCT stubs created. Updating index..."

# ── Update RCT index.md ───────────────────────────────────────────────────────
$idxPath = "$base\index.md"
$idxContent = [System.IO.File]::ReadAllText($idxPath, [System.Text.Encoding]::UTF8)

# Update keyword count line
$idxContent = $idxContent.Replace(
    '**Keywords:** RCT-001–RCT-024 (24 terms)',
    '**Keywords:** RCT-001–RCT-072 (72 terms)')

# Append new rows (RCT-024 is in the index already - the last row is RCT-023)
$newRows = @"
| RCT-024 | JSX Syntax and Rules                                    | ★☆☆ |
| RCT-025 | Functional Components                                   | ★☆☆ |
| RCT-026 | Props and Prop Types                                    | ★☆☆ |
| RCT-027 | State with useState Hook                                | ★☆☆ |
| RCT-028 | Side Effects with useEffect Hook                        | ★☆☆ |
| RCT-029 | Event Handling in React                                 | ★☆☆ |
| RCT-030 | Conditional Rendering                                   | ★☆☆ |
| RCT-031 | Lists and Keys                                          | ★☆☆ |
| RCT-032 | React DevTools                                          | ★☆☆ |
| RCT-033 | React Project Setup (Vite, CRA)                         | ★☆☆ |
| RCT-034 | Component Composition                                   | ★☆☆ |
| RCT-035 | Lifting State Up                                        | ★☆☆ |
| RCT-036 | Controlled vs Uncontrolled Components                   | ★★☆ |
| RCT-037 | Forms in React                                          | ★★☆ |
| RCT-038 | Fragments and Portals                                   | ★★☆ |
| RCT-039 | Children Prop and Render Props                          | ★★☆ |
| RCT-040 | React Router (v6)                                       | ★★☆ |
| RCT-041 | React Context API                                       | ★★☆ |
| RCT-042 | Custom Hooks Pattern                                    | ★★☆ |
| RCT-043 | useRef Hook                                             | ★★☆ |
| RCT-044 | useMemo and useCallback                                 | ★★☆ |
| RCT-045 | Error Boundaries                                        | ★★☆ |
| RCT-046 | React Query - TanStack Query                            | ★★☆ |
| RCT-047 | Zustand State Management                                | ★★☆ |
| RCT-048 | Redux Toolkit                                           | ★★☆ |
| RCT-049 | React Hook Form                                         | ★★☆ |
| RCT-050 | Lazy Loading and Code Splitting                         | ★★☆ |
| RCT-051 | React.memo and PureComponent                            | ★★☆ |
| RCT-052 | React Testing Library Basics                            | ★★☆ |
| RCT-053 | Storybook for React Components                          | ★★☆ |
| RCT-054 | CSS-in-JS (Styled Components, Emotion)                  | ★★☆ |
| RCT-055 | Tailwind CSS with React                                 | ★★☆ |
| RCT-056 | Next.js Fundamentals (SSR, SSG, ISR)                    | ★★☆ |
| RCT-057 | Next.js App Router                                      | ★★☆ |
| RCT-058 | Vite Build Configuration                                | ★★☆ |
| RCT-059 | Environment Variables in React                          | ★★☆ |
| RCT-060 | React Strict Mode                                       | ★★☆ |
| RCT-061 | useReducer Hook                                         | ★★☆ |
| RCT-062 | Compound Components Pattern                             | ★★★ |
| RCT-063 | Higher-Order Components (HOC)                           | ★★★ |
| RCT-064 | React Suspense and Concurrent Features                  | ★★★ |
| RCT-065 | React Performance Optimization Patterns                 | ★★★ |
| RCT-066 | State Management Architecture Decisions                 | ★★★ |
| RCT-067 | React Server Components (Deep Dive)                     | ★★★ |
| RCT-068 | Hydration and Server-Side Rendering Internals           | ★★★ |
| RCT-069 | React Testing Strategies (Unit, Integration)            | ★★★ |
| RCT-070 | React with TypeScript Patterns                          | ★★★ |
| RCT-071 | Accessibility Testing in React (axe, jest-axe)          | ★★★ |
| RCT-072 | React Internationalization (i18n)                       | ★★★ |
"@

$idxContent = $idxContent.TrimEnd() + "`n" + $newRows.TrimStart() + "`n"
[System.IO.File]::WriteAllText($idxPath, $idxContent, $enc)
Write-Host "Updated: RCT index.md (24 -> 72 terms)"
