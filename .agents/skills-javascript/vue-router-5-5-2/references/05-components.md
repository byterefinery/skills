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

Wrap `<RouterView>` inside `<transition>`/`<keep-alive>`, not the other way around. The slot also exposes the route location; the stable router additionally exposes `Component` (the resolved route component).

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
