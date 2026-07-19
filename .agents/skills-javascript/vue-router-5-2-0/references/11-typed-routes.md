# Typed Routes

## RouteMeta augmentation

Extend the `RouteMeta` interface to type custom meta fields:

```ts
// router/types.ts or typings.d.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: ('admin' | 'editor' | 'user')[]
    title?: string
    breadcrumb?: string
  }
}
```

Now meta fields are typed in guards and components:

```ts
router.beforeEach((to) => {
  // to.meta.requiresAuth is typed as boolean | undefined
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'login' }
  }
})
```

## Type-safe navigation

### Named routes with params

Define routes with explicit param types:

```ts
const routes: RouteRecordRaw[] = [
  {
    name: 'user' as const,
    path: '/users/:id',
    component: User,
  },
]
```

Navigation is type-checked:

```ts
// Correct
router.push({ name: 'user', params: { id: '42' } })

// TypeScript error: missing required param 'id'
router.push({ name: 'user' })
```

## TypesConfig augmentation

Override the global `Router` type returned by `useRouter()`:

```ts
import { router } from './router'
import type { RouteLocationNormalizedLoaded } from 'vue-router'

declare module 'vue-router' {
  interface TypesConfig {
    Router: typeof router
    $route: RouteLocationNormalizedLoaded
  }
}
```

## Route location types

| Type | Description |
|---|---|
| `RouteLocationRaw` | Input for navigation (string or object) |
| `RouteLocationNormalized` | Resolved route with decoded params |
| `RouteLocationNormalizedLoaded` | Normalized with loaded components |
| `RouteLocationResolved` | Full resolution with `href` |
| `RouteLocationAsPath` | Navigation by path |
| `RouteLocationAsRelative` | Navigation by name + params |
| `RouteLocationAsString` | Navigation by string |

## Param types

```ts
// Single param value
type RouteParamValue = string

// Raw param value (before normalization)
type RouteParamValueRaw = string | number | null | undefined

// Params object
type RouteParamsGeneric = Record<string, RouteParamValue | RouteParamValue[]>

// Raw params (for navigation input)
type RouteParamsRawGeneric = Record<string, RouteParamValueRaw | RouteParamValueRaw[]>
```

## Query types

```ts
// Normalized query (what you get from $route.query)
type LocationQuery = Record<string, LocationQueryValue | LocationQueryValue[]>

// Raw query (what you pass to router.push)
type LocationQueryRaw = Record<string | number, LocationQueryValueRaw | LocationQueryValueRaw[]>

// Individual values
type LocationQueryValue = string | null
type LocationQueryValueRaw = string | number | null | undefined
```

## Route record types

```ts
// Single component
interface RouteRecordSingleView {
  path: string
  component: RawRouteComponent
  // ...
}

// Multiple named views
interface RouteRecordMultipleViews {
  path: string
  components: Record<string, RawRouteComponent>
  // ...
}

// With children
interface RouteRecordSingleViewWithChildren {
  path: string
  component?: RawRouteComponent
  children: RouteRecordRaw[]
  // ...
}

// Redirect-only
interface RouteRecordRedirect {
  path: string
  redirect: RouteRecordRedirectOption
  // ...
}

// Union of all
type RouteRecordRaw =
  | RouteRecordSingleView
  | RouteRecordSingleViewWithChildren
  | RouteRecordMultipleViews
  | RouteRecordMultipleViewsWithChildren
  | RouteRecordRedirect
```

## Component types

```ts
// Component that can be used in routes
type RouteComponent = Component | DefineComponent

// Lazy-loaded component
type RawRouteComponent = RouteComponent | Lazy<RouteComponent>

// Lazy function
type Lazy<T> = () => Promise<T>
```

## Guard types

```ts
// Navigation guard
type NavigationGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalizedLoaded
) => NavigationGuardReturn

// Return value
type NavigationGuardReturn =
  | void
  | boolean
  | RouteLocationRaw
  | Promise<boolean | RouteLocationRaw | void>

// After hook
type NavigationHookAfter = (
  to: RouteLocationNormalizedLoaded,
  from: RouteLocationNormalizedLoaded,
  failure?: NavigationFailure
) => any
```

## Scroll behavior type

```ts
interface RouterScrollBehavior {
  (
    to: RouteLocationNormalized,
    from: RouteLocationNormalizedLoaded,
    savedPosition: ScrollPosition | null
  ): Awaitable<ScrollPosition | false | void>
}

type ScrollPosition =
  | { top?: number; left?: number; behavior?: ScrollBehavior }
  | { el: string | Element; top?: number; left?: number; behavior?: ScrollBehavior }
```

## Router options type

```ts
interface RouterOptions {
  history: RouterHistory
  routes: Readonly<RouteRecordRaw[]>
  scrollBehavior?: RouterScrollBehavior
  parseQuery?: (search: string) => LocationQuery
  stringifyQuery?: (query: LocationQueryRaw) => string
  linkActiveClass?: string
  linkExactActiveClass?: string
}
```
