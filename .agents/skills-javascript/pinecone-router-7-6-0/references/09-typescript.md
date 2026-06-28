# TypeScript

## Imports

```ts
import PineconeRouter, {
  // Core types
  Handler,
  HandlerContext,
  Context,
  Route,
  RouteOptions,
  MatchResult,
  RoutesMap,
  NavigationHistory,
  Settings,
  RouteTemplate,

  // Plugin
  PineconeRouterPlugin,
} from 'pinecone-router'
```

## Handler Type

The `Handler` type is generic over input and output:

```ts
type Handler<In, Out> = (
  context: HandlerContext<In>,
  controller: AbortController
) => Out | Promise<Out>
```

- `In` — the return type of the previous handler (available as `context.data`)
- `Out` — the return type of this handler (passed to the next handler)

### Typed handler chain

```ts
type UserData = { id: string; name: string }

const fetchUser: Handler<unknown, UserData> = async (ctx, ctrl) => {
  const res = await fetch(`/api/users/${ctx.params.id}`, { signal: ctrl.signal })
  return res.json()
}

const validateUser: Handler<UserData, UserData> = (ctx) => {
  if (!ctx.data?.name) throw new Error('No name')
  return ctx.data
}

const displayUser: Handler<UserData, void> = (ctx) => {
  document.getElementById('app')!.textContent = ctx.data.name
}

// Register
PineconeRouter.add('/user/:id', {
  handlers: [fetchUser, validateUser, displayUser],
})
```

## HandlerContext

```ts
interface HandlerContext<T = unknown> extends Context {
  readonly data: T
  readonly route: Route
}
```

Extends `Context` with `data` (from previous handler) and `route` (the matched route).

## Window and Alpine Extensions

Pinecone Router extends global types:

```ts
// Window
interface Window {
  PineconeRouter: PineconeRouter
}

// Alpine.js magics
interface Magics<T> {
  $router: PineconeRouter
  $history: NavigationHistory
  $params: Context['params']
}

// Alpine global
interface Alpine {
  $router: PineconeRouter
}
```

These declarations are included in the package and available automatically when importing.

## RouteTemplate

```ts
interface RouteTemplate extends ElementWithXAttributes<HTMLTemplateElement> {
  _x_PineconeRouter_route: string
}
```

Used for type-safe access to template elements with route information.

## Plugin Type

```ts
import { type PluginCallback, type Alpine } from 'alpinejs'

const PineconeRouterPlugin: PluginCallback
```

Useful when registering the plugin explicitly:

```ts
Alpine.plugin(PineconeRouterPlugin)
```
