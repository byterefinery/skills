# React Compiler

Contents

- [What it does](#what-it-does)
- [Goals and non-goals](#goals-and-non-goals)
- [How it works](#how-it-works)
- [Enabling it](#enabling-it)
- [Linting: Rules of React](#linting-rules-of-react)
- [Opting out](#opting-out)
- [Runtime](#runtime)

## What it does

React Compiler (shipped in the `react/react` monorepo under `compiler/`, stable with 19.3) is a Babel-based compiler that **automatically memoizes components and hooks** so only the minimal parts re-render when state changes, and it **validates that your code follows the Rules of React**. The net effect: fast by default, without sprinkling `memo`, `useMemo`, and `useCallback` by hand.

## Goals and non-goals

Goals (from the compiler's design docs):

- Bound the amount of re-rendering so apps are predictably fast by default.
- Keep startup time neutral — hold code-size increases and memoization overhead low.
- Keep React's declarative model; **remove** concepts (`memo`, `useMemo`, `useCallback`) rather than add new ones.
- Just work on idiomatic React; no explicit annotations for typical product code.
- Stay debuggable and understandable.

Explicit non-goals:

- Perfectly optimal re-rendering with zero recomputation (tracking overhead can exceed recomputation cost).
- Supporting code that violates React's rules.
- Supporting legacy patterns — notably **class components are not supported**.
- 100% of JavaScript — rare, unsafe, or unsoundly-modelable features (e.g., nested classes capturing mutable state, `eval`) are out.

## How it works

Two public interfaces share one core: a **Babel plugin** (transforms code) and an **ESLint plugin** (reports Rules of React violations).

The pipeline: Babel AST → **HIR** (high-level intermediate representation — a control-flow graph that preserves original high-level constructs like `??`, `for..of`, and ternaries for debuggable output) → SSA conversion → **validation** (Rules of React) → optimization (dead code elimination, constant propagation) → conservative **type inference** (identifies hooks, primitives, etc.) → **reactive scope inference** (groups values created/mutated together with the instructions that touch them) → scope construction and pruning (scopes containing hook calls are pruned; scopes that always invalidate together are merged) → **codegen** back to a Babel AST.

The Babel plugin decides per-function what to compile from plugin options plus local opt-in/opt-out directives.

## Enabling it

Install the plugin for your build:

```sh
npm install babel-plugin-react-compiler
```

Babel config:

```js
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      target: 'react-19',
    }],
  ],
};
```

Common setups:

- **Vite** — `@vitejs/plugin-react` accepts `compiler: true`.
- **Next.js** — enable via the framework's React Compiler option (experimental in 15.x).
- **Webpack/esbuild** — add the plugin to your Babel configuration.
- **Linting** — add `eslint-plugin-react-compiler` (the compiler's ESLint plugin; `eslint-plugin-react-hooks` is its predecessor) to catch rule violations without running the compiler.

The generated code imports helpers from the compiler runtime, resolved automatically by the plugin — no manual `react-compiler-runtime` wiring for typical setups.

## Linting: Rules of React

The compiler's ESLint plugin reports code that would break its optimizations — concretely, the Rules of React:

1. Don't mutate props or state during render.
2. Don't read or write props or state in a non-deterministic way during render (no `Date.now()`, `Math.random()`, changing globals).
3. Don't change hook dependencies between renders.
4. Follow the Rules of Hooks (no conditional or out-of-order hook calls).

A violation is a correctness bug in concurrent React, not just a missed optimization — fix the code rather than silencing the rule.

## Opting out

Use the `"use no memo"` directive to exclude code from compilation — at the top of a file, or inside a function to skip just that component/hook. Reach for it deliberately (e.g., a component whose render is trivially cheap, or code the compiler can't model soundly), and note the reason.

## Runtime

`react-compiler-runtime` (and the plugin's `/runtime` subpath) provides the memoization primitives the generated code uses. It is a dependency of the plugin's output; you generally don't import it directly.
