# React Compiler in React 19.3.0

Verified from `compiler/README.md`, `compiler/docs/DESIGN_GOALS.md`, `compiler/packages/babel-plugin-react-compiler/README.md`, and `packages/eslint-plugin-react-hooks/README.md` at tag v19.3.0.

## What it does

React Compiler is a compiler that optimizes React applications so only the minimal parts of components and hooks re-render when state changes. It also validates that components and hooks follow the Rules of React. It is meant to remove the need for `React.memo()`, `useMemo()`, and `useCallback()`, not to introduce new concepts.

## Goals (from the design doc)

- Bound re-rendering so apps are predictably fast by default
- Keep startup time neutral (low code-size and memoization overhead)
- "Just work" on idiomatic React code that follows React's rules
- No explicit annotations required for typical product code

Non-goals: perfectly optimal re-rendering, code that violates React's rules, legacy features (notably class components, whose mutable state spans methods), and 100% of JavaScript (no `eval`, no tricky closure-capturing nested classes).

## Architecture in brief

Babel plugin and ESLint plugin are the two public interfaces; both use the same core. The core lowers Babel AST to HIR (a high-level control-flow graph), converts to SSA, validates the Rules of React, runs inference and reactive-scope passes, then codegens back to a Babel AST that the plugin splices in. Validation catches conditional hook calls, unconditional setState, and other rule violations.

## Enabling it

**Babel** — add `babel-plugin-react-compiler` to the Babel config (it ships in the repo under `compiler/`; published as a Babel plugin). The plugin decides which functions to compile from plugin options and local opt-in/opt-out directives in the source. Full setup instructions live at react.dev/learn/react-compiler.

**ESLint** — `eslint-plugin-react-hooks` now bundles both the core hooks rules and the compiler rules; prefer the presets over enabling rules one by one so new rules arrive automatically:

```js
// eslint.config.js
import reactHooks from 'eslint-plugin-react-hooks';
import { defineConfig } from 'eslint/config';

export default defineConfig([
  reactHooks.configs.flat.recommended, // or 'recommended-latest' for bleeding edge
]);
```

`exhaustive-deps` accepts `additionalHooks` (a regex) to validate custom hooks with dependency arguments — use it sparingly; prefer custom hooks that don't take a deps array.

## Rules of React — the rule set in this tree

Core hooks rules:

- `rules-of-hooks` — hooks only at top level, only from React (error)
- `exhaustive-deps` — dependency arrays must list every reactive value used (warn)

Compiler validation rules:

- `purity` — render and callbacks must be pure (error)
- `refs` — no reading or writing `ref.current` during render (error)
- `immutability` — no mutating objects/arrays in render (error)
- `set-state-in-render` — conditional setState in render must be guarded by a persistent variable (error)
- `set-state-in-effect` — no unconditional setState in effects (error)
- `error-boundaries` — error boundaries must handle errors they catch (error)
- `gating` — features must be gated consistently (error)
- `globals` — restrictions on global mutable state (error)
- `static-components` — components that never re-render can be treated as static (error)
- `use-memo` — memoization must be stable (error)
- `preserve-manual-memoization` — manual memoization may not break behavior (error)
- `config` — compiler configuration errors (error)
- `unsupported-syntax` — syntax the compiler cannot model (warn)
- `incompatible-library` — libraries the compiler cannot interoperate with safely (warn)

## Implications for writing code

Write idiomatic, rule-following React and let the compiler optimize: no side effects in render, `useMemo`/`useCallback` only when you actually need stable identity (they become optional), and no `ref.current` reads during render. When a rule fires, fix the code — the rule exists because violating it breaks the compiler's soundness, not just style.
