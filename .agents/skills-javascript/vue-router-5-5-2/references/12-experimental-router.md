# Experimental Router (`vue-router/experimental`)

The experimental router previews the next major version. It is **not production-ready** — use it for testing and feedback. It introduces a resolver-based matching layer powering stronger typing, file-based routing integration, and custom param parsers.

## Setup

Import the factory from `vue-router/experimental` plus a resolver:

```ts
import { createWebHistory } from 'vue-router'
import { experimental_createRouter as createRouter } from 'vue-router/experimental'
import { resolver, handleHotUpdate } from 'vue-router/auto-resolver'

export const router = createRouter({
  history: createWebHistory(),
  resolver,
})

if (import.meta.hot) handleHotUpdate(router)
```

For static route arrays, use `createFixedResolver` (also exported from `vue-router/experimental`). Register `RouterLink`/`RouterView` globally yourself — the experimental router does not.

Opt in to a strictly-typed `useRouter()`/`useRoute()` by registering the router:

```ts
declare module 'vue-router' {
  export interface TypesConfig {
    Router: typeof router
  }
}
```

## Query values are arrays

Every `route.query` value is an array: a valueless key gives `[null]`, a missing key is `undefined`.

```ts
// /search?q=vue&tag=a&tag=b&debug
route.query.q     // ['vue']
route.query.tag   // ['a', 'b']
route.query.debug // [null]
route.query.page  // undefined
```

Pass arrays when navigating — a non-array still works but logs a deprecation warning. An empty array equals a missing key.

## Navigation semantics

- Relative locations (strings not starting with `/`, or objects without `name`/absolute `path`) resolve against the **current route**: `router.push('add')` from `/users/posva` → `/users/add`.
- An object without `name`/`path` keeps current params/query/hash unless overridden; `query` is **merged** with the current query, not replaced. Use a named location to replace the whole query.
- `router.resolve(location, baseRoute?)` accepts a second base argument.
- **Encoding**: string locations are normalized like `new URL()` — no manual encoding (`router.push('/café?q=a b')` works). Object locations are not normalized: `path` must already be encoded, while `query` values and `params` stay decoded (the router encodes them).
- **Guard redirects** resolve relative locations against the target route (`to`), including during back/forward. **Route-record `redirect`** must return a named location or an absolute path; copy `to.query`/`to.hash` to preserve them.

## 5.5.x breaking changes

- **`new NavigationResult(to)` removed** (5.5.2) — use `reroute(to)` inside data loaders instead.
- **Matchers return `null` on a miss** (5.5.1) — `MatcherPattern.match()` (path/query/hash) returns `TParams | null`; `MatchMiss` no longer extends `Error` (check `instanceof MatchMiss`, not `instanceof Error`). A named `resolve()` that doesn't match throws `MatchMiss`.
- **Scroll hooks moved inside `<RouterView>`** (5.5.2) — `onRouteRendered()`/`useScrollRestoration()` are not called for the initial navigation when the component is outside a `<RouterView>` and the app mounts after `router.isReady()`.

## Custom param parsers

Transform raw URL strings into rich JS values (and back) for path, query, and hash params, end-to-end typed. Enable the Vite plugin option to scan a directory and register parsers at runtime and in generated types:

```ts
// vite.config.ts
plugins: [
  VueRouter({ experimental: { paramParsers: { dir: 'src/params' } } }),
  Vue(),
]
```

Built-in parsers: `int` (number), `bool` (boolean), `string` (default, no-op) — all usable in path, query, and hash.

Define a parser as a module exporting `parser` (file name = parser name):

```ts
// src/params/number.ts
import { defineParamParser, miss } from 'vue-router/experimental'

export const parser = defineParamParser<number>({
  get: value => {
    const n = Number(value)
    if (Number.isNaN(n)) miss('"value" is not a number')
    return n
  },
  set: value => String(value),
})
```

- `defineParamParser<T>` — single-value transform; the router wraps it for optional/repeatable usage and handles null/arrays. Write validation in `get`; a validation error skips the route (another route, e.g., a catch-all, can match).
- `defineParamParserRaw<T>` — full control over all shapes (null/undefined/single/array); collapse everything into one output type (e.g., `Set<string>`). Returning an array from `set` is the safest serialization; `[]` ≡ omitted param.
- `defineHashParamParser<T>` — hash params only; `get` receives the hash without `#`. No array/nullish wrapping.
- `miss(reason?)` — mark a value as not matching in `get`.
- **Standard Schema** (Zod, Valibot) objects work directly as parsers, but are one-way: the router stringifies with `String(value)` when navigating, so only use when `String(parsed) === original`.

Use parsers in routes: rename the file segment `[id=int]`, or via `definePage()`:

```ts
definePage({
  params: {
    path: { id: 'number', org: { re: /@\w+/ } },   // regex restriction (non-capturing, no anchors, no empty match)
    query: { page: { parser: 'int', format: 'value', default: 1 } },
    hash: { page: { parser: 'int', default: 1 } },
  },
})
```

Query field options: `parser`, `format` (`'value'` takes the last value; `'array'`), `default` (value or factory, used when missing or parsing fails), `required` (reject match when absent). Remove an optional query param by setting it to `undefined` when navigating.

## Vapor mode (Vue 3.6+)

Vapor apps need Vapor versions of the components:

```ts
import { createVaporApp } from 'vue'
import { RouterLink, RouterView } from 'vue-router/experimental/vapor'

const app = createVaporApp(App)
app.use(router)
app.component('RouterLink', RouterLink)
app.component('RouterView', RouterView)
app.mount('#app')
```

Differences from the VDOM components: no Options API (no `$route` in templates, no `beforeRouteEnter`/`Update`/`Leave` options — use composables); in the `<RouterView>` slot, `Component` is the route component **instance** — render `<component :is="Component" />` (props/slots passed to `<component>` are ignored; use route props or `<RouterView>` attributes). VDOM route components work through `vaporInteropPlugin`. SSR hydration not supported yet.
