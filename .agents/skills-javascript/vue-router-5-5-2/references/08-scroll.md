# Scroll Behavior and Scroll Restoration

## `scrollBehavior` option (stable, deprecated by the plugin)

Only works when the browser supports `history.pushState`.

```js
const router = createRouter({
  history: createWebHashHistory(),
  routes: [...],
  scrollBehavior(to, from, savedPosition) {
    // return a position, a Promise of a position, or falsy to skip
  },
})
```

`savedPosition` is only set on `popstate` navigations (back/forward buttons).

Common returns:

- `{ top: 0 }` — always scroll to top.
- `savedPosition` — native-like back/forward restore.
- `{ el: '#main', top: 10 }` — element + relative offset (also accepts a DOM element).
- `{ el: to.hash }` — scroll-to-anchor behavior.
- `behavior: 'smooth'` for smooth scrolling.
- `false`/`undefined`/`{}` — no scrolling.

Delaying: return a Promise (e.g., resolve after a transition finishes). Adding `scrollBehavior` sets `history.scrollRestoration` to `manual`; set it to `auto` (and/or omit `scrollBehavior`) to let the browser handle restoration natively.

```js
scrollBehavior(to, from, savedPosition) {
  if (savedPosition) return savedPosition
  if (to.hash) return { el: to.hash, behavior: 'smooth' }
  return { top: 0 }
}
```

## Scroll Restoration plugin (experimental, replaces `scrollBehavior`)

`ScrollRestoration` + `useScrollRestoration()` from `vue-router/experimental` — save/restore positions in **sessionStorage** (persist across reloads in the same tab).

Install the plugin **before the router**; `router`, `capture`, and `restore` are required:

```ts
import {
  ScrollRestoration,
  SCROLL_RESTORATION_CAPTURE_DEFAULT,
  SCROLL_RESTORATION_RESTORE_DEFAULT,
} from 'vue-router/experimental'

app.use(ScrollRestoration, {
  router,
  capture: SCROLL_RESTORATION_CAPTURE_DEFAULT,
  restore: SCROLL_RESTORATION_RESTORE_DEFAULT,
  // optional: key (default to => to.path + to.hash), storageKeyPrefix ('vue:scroll:')
})
app.use(router)
```

Then call `useScrollRestoration()` in **a component inside a `<RouterView>`** (layout or page). Do not call it in the root `App.vue` or other components outside `<RouterView>` — there the restore would run in `afterEach` before the new route renders, and it is not called for the initial navigation when the app mounts after `router.isReady()` (5.5.x breaking change).

Default behavior: capture on page leave and on tab hide; restore after the page renders (after mount/update, after `<Suspense>` resolves, after out-in `<Transition>`). Per-page custom keys: `useScrollRestoration({ key: to => to.path + to.hash })`. A page call with the same key replaces the layout call.

Custom capture/restore for other scroll containers, with manual initial restore:

```js
const { scroll } = useScrollRestoration({
  key: 'sidebar',
  capture: () => ({ sidebar: { top: sidebar.value?.scrollTop } }),
  restore: entry => sidebar.value?.scrollTo({ top: entry?.sidebar?.top ?? 0 }),
})
onMounted(scroll) // initial navigation finished before this component existed
```

Capture triggers are configurable via `setupListeners(capture, signal)` — keep defaults with `SCROLL_RESTORATION_SETUP_LISTENERS_DEFAULT`, or disable all automatic capture with `setupListeners: () => {}`.
