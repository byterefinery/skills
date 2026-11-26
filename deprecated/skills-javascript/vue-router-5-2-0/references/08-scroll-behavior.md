# Scroll Behavior

## Basic scroll behavior

Configure scroll behavior on navigation via the `scrollBehavior` option:

```js
const router = createRouter({
  history: createWebHistory(),
  routes: [/* ... */],
  scrollBehavior(to, from, savedPosition) {
    // Return scroll position
    return { top: 0 }
  },
})
```

The function receives:

| Parameter | Type | Description |
|---|---|---|
| `to` | `RouteLocationNormalized` | Target route |
| `from` | `RouteLocationNormalizedLoaded` | Current route |
| `savedPosition` | `ScrollPosition \| null` | Saved position from history (back/forward), `null` otherwise |

## Scroll to top

Reset scroll on every navigation:

```js
scrollBehavior() {
  return { top: 0 }
}
```

## Restore scroll on back/forward

Preserve scroll position for history navigation:

```js
scrollBehavior(to, from, savedPosition) {
  if (savedPosition) {
    return savedPosition  // Restore saved position (back/forward)
  }
  return { top: 0 }       // Scroll to top for new navigations
}
```

## Async scroll behavior

Return a Promise for async scroll logic:

```js
scrollBehavior(to, from, savedPosition) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ top: 0 })
    }, 100)
  })
}
```

## Element-based scrolling

Scroll to a specific element using a CSS selector or DOM element:

```js
scrollBehavior(to, from, savedPosition) {
  if (to.hash) {
    return {
      el: to.hash,       // e.g., '#section-1'
      behavior: 'smooth',
    }
  }
  return { top: 0 }
}
```

### Element with offset

```js
scrollBehavior(to, from, savedPosition) {
  if (to.hash) {
    return {
      el: to.hash,
      top: 80,  // Offset from the element (e.g., for fixed header)
      behavior: 'smooth',
    }
  }
  return { top: 0 }
}
```

## Disable scrolling

Return `false` to skip scrolling entirely:

```js
scrollBehavior(to, from, savedPosition) {
  if (to.meta.disableScroll) {
    return false
  }
  return { top: 0 }
}
```

## Scroll position coordinates

Return explicit x/y coordinates:

```js
scrollBehavior(to, from, savedPosition) {
  return {
    left: 0,
    top: 0,
    behavior: 'smooth',
  }
}
```

## Per-route scroll behavior

Use meta fields to control scroll behavior per route:

```js
// Route definition
{
  path: '/long-page',
  component: LongPage,
  meta: { scrollToTop: false },
}

// Scroll behavior
scrollBehavior(to, from, savedPosition) {
  if (savedPosition) return savedPosition
  if (to.meta.scrollToTop === false) return false
  return { top: 0 }
}
```

## List items with hash

Scroll to specific list items:

```js
// Routes
{
  path: '/posts',
  component: Posts,
  children: [
    { path: ':postId', component: PostDetail },
  ],
}

// Links
<RouterLink :to="{ path: '/posts', hash: '#post-42' }">Post 42</RouterLink>

// Scroll behavior
scrollBehavior(to, from, savedPosition) {
  if (to.hash) {
    return { el: to.hash, behavior: 'smooth' }
  }
  return { top: 0 }
}
```

## How scroll saving works

Vue Router automatically saves scroll positions before navigation and restores them on back/forward. The `savedPosition` parameter contains the saved position for history traversals.

The router sets `history.scrollRestoration = 'manual'` when `scrollBehavior` is provided, taking full control of scroll management.

## Scroll behavior handler type

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
