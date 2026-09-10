---
name: react
description: React 19 (verified against v19.3.0) for building user interfaces with components, hooks, Actions, and React Server Components. Use when writing, reviewing, or refactoring React or JSX code, RSC server components and server actions, DOM or server rendering, or configuring the React Compiler.
license: MIT
compatibility: React 19.3.0; content verified against the react/react repository at tag v19.3.0 (2026-09-09). The canonical API reference is react.dev.
metadata:
  tags:
    - frontend
    - javascript
    - react
---

# react

React is a JavaScript library for building user interfaces from components, with hooks for state and effects, Actions for forms and data mutation, and React Server Components for full-stack rendering. This skill covers React 19.3.0 as shipped in the `react/react` repository (tag v19.3.0, 2026-09-09). The canonical, always-current API reference is https://react.dev — consult it when exact signatures or props matter.

## Overview

- `react` — core package: components, hooks, Actions primitives. No DOM access.
- `react-dom` — browser renderer (`react-dom/client`) and server renderers (`react-dom/server` for SSR, `react-dom/static` for SSG).
- React Server Components (RSC) — server-only components streamed to the client over the Flight protocol; wired per bundler via `react-server-dom-{webpack,turbopack,parcel,esm}`.
- React Compiler — a Babel plugin that auto-memoizes components and hooks and validates the Rules of React; the validation rules also ship in `eslint-plugin-react-hooks`.

New across the 19.x line (19.0 → 19.3): `use()`, `useActionState`, `useOptimistic`, `useFormStatus`, `useEffectEvent`, ref-as-prop, form Actions, document metadata hoisting, `prerender`/`resume` static APIs, `<Activity>`, `<ViewTransition>`, `cacheSignal`, and the standalone-HTML `react-markup` package.

## Usage

Browser app:

```jsx
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}

createRoot(document.getElementById('root')).render(<Counter />);
```

Patterns:

- **State** — `useState` for local state, `useReducer` for complex state, `useOptimistic` to show the expected result while a slow Action completes.
- **Forms and Actions** — pass async functions to `<form action>` or `formAction`; pair with `useActionState` for pending/error state and `useFormStatus` to reflect it in nested elements.
- **Data in render** — read promises with `use(promise)`; it suspends until resolved. Also works on Context.
- **RSC** — start client-only files with the `'use client'` directive; mark exported async functions with `'use server'` to make them Server Actions callable from the client.
- **SSR/SSG** — `renderToPipeableStream`/`renderToReadableStream` for streaming SSR; `prerender` plus the `resume*` APIs for static generation with partial pre-rendering.
- **Compiler** — add `babel-plugin-react-compiler` to Babel and the `eslint-plugin-react-hooks` recommended config to ESLint, then write idiomatic code and let it optimize.

## Gotchas

- **Refs are props in 19** — pass `ref` to function components like any other prop; `forwardRef` is only needed for legacy support. Reading `element.ref` is deprecated; use `element.props.ref`.
- **`use()` is render-only** — it is the only hook-like API that may be called conditionally, but only during render. Never call it from effects or event handlers. It accepts a promise or a Context.
- **Actions reset uncontrolled forms** — when a form's Action finishes, React clears uncontrolled inputs. Preserve user input by rendering it back from state, or call `requestFormReset(form)` explicitly when you want a reset.
- **RSC directives are file-level** — `'use client'` and file-level `'use server'` must be the first statement in the file, before imports. A `'use server'` placed directly on an exported function body also works and scopes the action to that function.
- **Server Components can't use client APIs** — no state, effects, or event handlers in server components. Pass only serializable data to client components; cross the boundary via props or Server Actions.
- **`cache()` is request-scoped** — it memoizes per RSC request, not globally. Use `cacheSignal` to learn when the current `cache()` lifetime ends (e.g., to abort in-flight fetches).
- **Rules of React** — the compiler enforces them and violations silently break its optimizations: render must be pure (no side effects in `useMemo`/`useCallback`), no reading or writing `ref.current` during render, no mutating objects or arrays in render, and no unconditional `setState` in effects (update state from the event that changed it, or use `useEffectEvent`).
- **Removed in 19** — `propTypes` is silently ignored; `defaultProps` on function components, string refs, `contextTypes`/`getChildContext`, `React.createFactory`, `findDOMNode`, `ReactDOM.render`, `unmountComponentAtNode`, `react-dom/test-utils`, and UMD builds are gone. The automatic JSX transform is required.
- **`useId` output is not stable** — its format changed across versions (`:r1:` → `«r1»` → `_r1_`). Treat it as an opaque string for `id`/`aria-*` attributes only; never parse or pattern-match it.
- **`renderToString` is legacy** — it cannot suspend and blocks on slow data. Use the streaming renderers or `prerender`.
- **Dev-only APIs** — `React.act` and `captureOwnerStack` exist only in development builds; guard any usage so production code never reaches them.
- **`<Activity>` (19.2+)** — hides and restores a subtree while keeping its UI and internal state, for cheaply hidden sections. Verify exact props against the react.dev reference before shipping code that depends on them.

## References

- [01-react-core-api](references/01-react-core-api.md) — every `react` package export in 19.3.0, with notes on the new hooks
- [02-react-dom](references/02-react-dom.md) — entry points, browser and server rendering APIs, document metadata
- [03-server-components](references/03-server-components.md) — RSC architecture, directives, Server Actions, caching, prerendering, bundler adapters
- [04-react-compiler](references/04-react-compiler.md) — compiler integration and the full Rules of React list
- [05-migrating-to-19](references/05-migrating-to-19.md) — breaking changes, deprecations, and behavior changes from 18 to 19
