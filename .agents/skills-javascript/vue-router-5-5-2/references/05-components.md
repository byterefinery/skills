# RouterLink and RouterView Components

## RouterLink

Renders an `<a>` with routing behavior (no page reload, URL encoding, active classes). Use `to` instead of `href` — passing both causes double navigation.

```vue
<RouterLink to="/about">About</RouterLink>
<RouterLink :to="{ name: 'user', params: { id: 1 } }">User</RouterLink>
```

Props: `to` (required, same shape as `router.push`), `replace`, `activeClass`/`exactActiveClass` (or the `router-link-exact-active`/`router-link-active` defaults), `aria-current` (default `page`), `custom` — render any non-`<a>` element while keeping router props via the slot:

```vue
<RouterLink custom v-slot="{ isActive, href, navigate }">
  <a :href="href" @click="navigate" :class="{ active: isActive }">Link</a>
</RouterLink>
```

### useLink composable

For render functions or programmatic links, `useLink()` gives the same logic; pass the `to` location (or props) and it returns `navigate`, `href`, `route`, `isActive`, `isExactActive`:

```js
import { useLink } from 'vue-router'

const { navigate, href, route, isActive, isExactActive } = useLink(to)
```

## RouterView

Renders the component matched at the current depth. Depth auto-increments for nested `<RouterView>`s; the `name` prop selects a named view.

```vue
<RouterView v-slot="{ Component, route }">
  <transition>
    <component :is="Component" :key="route.fullPath" />
  </transition>
</RouterView>
```

Wrap `<RouterView>` inside `<transition>`/`<keep-alive>`, not the other way around. The slot also exposes the route location; the stable router additionally exposes `Component` (the resolved route component). Putting a template ref inside the slot attaches it to the route component (a ref on `<RouterView>` itself yields the RouterView instance instead).

## Displaying a different route (`route` prop)

By default `<RouterView>` displays the current route. Pass a `route` prop to display another route location instead, while the URL stays the same:

```vue
<RouterView :route="router.resolve('/users/1')" />
```

- The value must be a resolved route location, e.g. the result of `router.resolve()`.
- If the route components are lazy loaded, load them first with `loadRouteLocation()` (see 03-navigation).
- When the `route` prop is `undefined`, the view inherits the route provided by the parent view. Only a top-level `<RouterView>` falls back to the current route from the URL.

### Modals with their own URL

The most common use case: a modal that has its own URL, while the page that opened it stays visible in the background. Save the background page's location in the history state when opening the modal:

```ts
router.push({
  name: 'user',
  params: { id },
  state: { backgroundView: router.currentRoute.value.fullPath },
})
```

Then render the background page with the `route` prop, and render the modal **next to it** with a second `<RouterView>` that displays the current route. The same route component is displayed in the modal when the user opens it from a page, and as a full page when the user visits `/users/1` directly or reloads the page. If the background page uses lazy loaded components, load them before the navigation ends:

```ts
router.beforeResolve(async () => {
  const { backgroundView } = history.state ?? {}
  if (backgroundView) {
    await loadRouteLocation(router.resolve(backgroundView))
  }
})
```

Reading routes inside the view: nested `<RouterView>`s, `useRoute()`, and the active classes of `<RouterLink>` inside a `<RouterView>` with a `route` prop use that route. Some values still use the current route (the URL): `$route` (same as `useRouter().currentRoute.value`), and relative locations in `router.push()` / `<RouterLink>` (resolved against the current route, not the displayed one). If a component needs the current route, place it outside the `<RouterView>` that receives the `route` prop, or read `useRouter().currentRoute`.

> In v5.4 and earlier, `useRoute()` and nested `<RouterView>`s ignored the `route` prop and always used the current route. If a component inside the view relied on that (e.g. a modal placed inside the background page reading the modal route's params), move it next to the `<RouterView>`.

## Named views

Render several components for one route:

```js
const routes = [
  {
    path: '/dashboard',
    components: {
      default: Dashboard,      // rendered by <RouterView>
      sidebar: Sidebar,        // rendered by <RouterView name="sidebar">
      footer: Footer,
    },
  },
]
```

```vue
<RouterView name="sidebar" />
<RouterView />
```

## Passing props

Route option `props` (per view for named views):

- `props: true` — all params become props (param name must match prop name).
- `props: { static: 'value' }` — static props.
- `props: route => ({ id: route.params.id })` — function mapping params to props.

Can also be set via the `props` attribute on `<RouterView>`.

## Transitions

- Wrap `<component :is="Component" />` in `<transition>` inside the `<RouterView>` slot.
- Force a transition between reused views (param-only changes) with `:key="route.path"`.
- Per-route: store a transition name in the route's `meta` (e.g., `meta: { transition: 'slide-left' }`) and use `:name="route.meta.transition || 'fade'"`;
- Set `to.meta.transition` in `afterEach` to compute it dynamically from `to`/`from` depth.
- Initial navigation: transitions apply even without `appear`; to avoid it, await `router.isReady()` before `app.mount()`.

## Extending RouterLink

To fully customize rendering, use `custom` + `v-slot` (above) or build your own component with `useLink`. The router exposes `RouterLinkSlotScope` (and in 5.5.x the `shouldHandleLinkClick` helper is exported as `_shouldHandleLinkClick`) for advanced integration.
