# Handlers

## Basics

Handlers execute functions when a route matches. They run **before** templates render and **before** the route is added to navigation history. This allows redirecting or showing content from JS without the redirect appearing in history.

```html
<template x-route="/hello/:name" x-handler="greet"></template>
```

```js
Alpine.data('app', () => ({
  greet(context, controller) {
    document.querySelector('#app').innerHTML =
      `<h1>Hello, ${context.params.name}</h1>`
  },
}))
```

## Handler Arguments

Each handler receives two arguments:

1. **`context: HandlerContext`** — contains `path`, `params`, `route`, and `data` (from previous handler)
2. **`controller: AbortController`** — for cancellation

```js
function handler(context, controller) {
  // Access route info
  console.log(context.path)        // "/hello/john"
  console.log(context.params)      // { name: "john" }
  console.log(context.route)       // Route object
  console.log(context.data)        // Return value of previous handler

  // Check for cancellation
  if (controller.signal.aborted) return

  // Cancel subsequent handlers
  controller.abort()
}
```

## Single and Multiple Handlers

```html
<!-- Single handler (function name) -->
<template x-route="/" x-handler="home"></template>

<!-- Array of handlers -->
<template x-route="/hello/:name" x-handler="[checkName, hello]"></template>

<!-- Anonymous functions -->
<template x-route="/redirect"
  x-handler="[(ctx) => $router.navigate('/'), thisWontRun]">
</template>
```

Handlers are awaited in order. The return value of one handler is passed to the next via `context.data`.

## Data Passing Between Handlers

```html
<template x-route="/data" x-handler="[fetchData, process, display]"></template>
```

```js
Alpine.data('app', () => ({
  async fetchData(context, controller) {
    const response = await fetch('/api/data', { signal: controller.signal })
    return response.json() // passed to next handler as context.data
  },

  process(context) {
    return context.data.filter(item => item.active) // passed to next
  },

  display(context) {
    // context.data contains the filtered array from process()
    console.table(context.data)
  },
}))
```

## Cancellation Patterns

### Redirect (cancels via navigation)

```js
function checkAuth(context) {
  if (!context.params.token) {
    this.$router.navigate('/login') // cancels all queued handlers
  }
}
```

### Abort (cancels without redirecting)

```js
async function fetchData(context, controller) {
  try {
    const response = await fetch('/api/data', { signal: controller.signal })
    return response.json()
  } catch (err) {
    if (err.name !== 'AbortError') {
      // Show error without redirecting
      showError(err.message)
      controller.abort() // stops subsequent handlers and template rendering
    }
  }
}
```

### User navigates away during fetch

The router automatically aborts the controller when a new navigation starts while handlers are running. Always check `controller.signal` in async operations:

```js
async function slowFetch(context, controller) {
  const response = await fetch('/api/slow', { signal: controller.signal })
  // If user clicks another link, this fetch is cancelled
  // The AbortError is caught internally
}
```

## Global Handlers

Define handlers that run on **every** route using the `.global` modifier. They always execute before route-specific handlers.

```html
<div x-data="router" x-handler.global="[globalHandler]">
  <template x-route="/" x-handler="home"></template>
</div>
```

```js
Alpine.data('router', () => ({
  globalHandler(context) {
    console.log('Every navigation:', context.path)
    // Good for analytics, auth checks, etc.
  },
}))
```

Or set globally in settings:

```js
PineconeRouter.settings({
  globalHandlers: [
    (context) => {
      if (!isAuthenticated() && context.path !== '/login') {
        // redirect logic
      }
    },
  ],
})
```

## Handler Type Reference

```ts
export type Handler<In, Out> = (
  context: HandlerContext<In>,
  controller: AbortController
) => Out | Promise<Out>

export interface HandlerContext<T = unknown> extends Context {
  readonly data: T
  readonly route: Route
}
```

## Directive Execution Order

Directives execute in this order: `x-route` → `x-handler` → `x-template`. This ensures routes are registered, then handlers are attached, then templates are processed.
