# Components

## RouterLink

Renders a navigable link. Registered globally when the router is installed — no need to import.

### Basic usage

```vue
<RouterLink to="/about">About</RouterLink>
<!-- Renders: <a href="/about" class="router-link-active">About</a> -->
```

### Props

| Prop | Type | Description |
|---|---|---|
| `to` | `string \| object` | Target route location (required) |
| `replace` | `boolean` | Use `router.replace()` instead of `router.push()` |
| `active-class` | `string` | Class when link is active (default: `router-link-active`) |
| `exact-active-class` | `string` | Class when link is exactly active (default: `router-link-exact-active`) |
| `aria-current-value` | `string` | Value of `aria-current` when exact active (default: `'page'`) |
| `custom` | `boolean` | Render slot content directly without wrapping `<a>` tag |
| `view-transition` | `boolean` | Wrap navigation in `document.startViewTransition()` |

### `to` prop formats

```vue
<!-- String path -->
<RouterLink to="/users/42">User</RouterLink>

<!-- Object with path -->
<RouterLink :to="{ path: '/users/42' }">User</RouterLink>

<!-- Named route -->
<RouterLink :to="{ name: 'user', params: { id: 42 } }">User</RouterLink>

<!-- With query -->
<RouterLink :to="{ path: '/search', query: { q: 'vue' } }">Search</RouterLink>

<!-- With hash -->
<RouterLink :to="{ path: '/guide', hash: '#api' }">API</RouterLink>
```

### Slot API (scoped slot)

Access link state for custom rendering:

```vue
<RouterLink to="/about" v-slot="{ href, route, isActive, isExactActive, navigate }">
  <button class="btn" :class="{ active: isActive }" @click="navigate">
    About
  </button>
  <span class="debug">href: {{ href }}</span>
</RouterLink>
```

### Custom mode

Use `custom` prop to render any element instead of `<a>`:

```vue
<RouterLink to="/about" custom v-slot="{ href, navigate }">
  <li @click="navigate" @mouseenter="mouseenterHandler">
    <a :href="href">About</a>
  </li>
</RouterLink>
```

With `custom`, the `<a>` tag is not rendered. You control the element and must call `navigate` on click.

### Active classes

Classes are applied automatically:

```vue
<!-- Override global defaults -->
<RouterLink to="/about" active-class="is-active" exact-active-class="is-exact">
  About
</RouterLink>
```

Set globally in router options:

```js
createRouter({
  linkActiveClass: 'active',
  linkExactActiveClass: 'exact-active',
  // ...
})
```

### View transitions

Enable CSS view transitions on navigation:

```vue
<RouterLink to="/about" view-transition>
  About
</RouterLink>
```

Requires `document.startViewTransition()` browser support.

## RouterView

Renders the component matched by the current route.

### Basic usage

```vue
<RouterView />
```

### Props

| Prop | Type | Description |
|---|---|---|
| `name` | `string` | Name of the view to render (default: `'default'`) |
| `route` | `RouteLocationNormalizedLoaded` | Override the route used for rendering |

### Named views

Render multiple components at one route:

```js
// Route definition
{
  path: '/dashboard',
  components: {
    default: DashboardMain,
    header: DashboardHeader,
    sidebar: DashboardSidebar,
  },
}
```

```vue
<!-- Template -->
<template>
  <RouterView name="header" />
  <RouterView name="sidebar" />
  <RouterView />  <!-- default -->
</template>
```

### Nested views

Multiple `<RouterView>` at different depths render parent-child route segments:

```vue
<!-- App.vue -->
<template>
  <RouterView />  <!-- Renders SettingsLayout at depth 0 -->
</template>

<!-- SettingsLayout.vue -->
<template>
  <div>
    <aside>Settings Nav</aside>
    <RouterView />  <!-- Renders child component at depth 1 -->
  </div>
</template>
```

### Slot API

Access the resolved component and route:

```vue
<RouterView v-slot="{ Component, route }">
  <component :is="Component" />
  <span>Current: {{ route.path }}</span>
</RouterView>
```

### With transitions

```vue
<template>
  <RouterView v-slot="{ Component }">
    <Transition name="fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
</template>
```

### With keep-alive

```vue
<template>
  <RouterView v-slot="{ Component }">
    <KeepAlive>
      <component :is="Component" />
    </KeepAlive>
  </RouterView>
</template>
```

## useLink composable

Programmatic access to RouterLink behavior without rendering:

```js
import { useLink } from 'vue-router'
import { ref } from 'vue'

const to = ref('/about')
const { route, href, isActive, isExactActive, navigate } = useLink({ to })

// Use in setup
function handleClick(e) {
  navigate(e)
}
```

Returns:

| Property | Type | Description |
|---|---|---|
| `route` | `ComputedRef<RouteLocationResolved>` | Resolved route location |
| `href` | `ComputedRef<string>` | Computed href string |
| `isActive` | `ComputedRef<boolean>` | True if link is active |
| `isExactActive` | `ComputedRef<boolean>` | True if link is exactly active |
| `navigate` | `(e?: MouseEvent) => Promise` | Trigger navigation (respects modifier keys) |

### Custom link component

Build a link component from `useLink`:

```js
import { defineComponent, h } from 'vue'
import { useLink } from 'vue-router'

export const MyLink = defineComponent({
  props: { to: { type: [String, Object], required: true } },
  setup(props, { slots }) {
    const { href, isActive, navigate } = useLink({ to: props.to })

    return () =>
      h('a', {
        href: href.value,
        class: { active: isActive.value },
        onClick: (e) => navigate(e),
      }, slots.default?.())
  },
})
```

## Component registration

`RouterLink` and `RouterView` are registered globally when `app.use(router)` is called. They are available in all templates without explicit import or registration.

They are also exported from the package for programmatic use:

```js
import { RouterLink, RouterView } from 'vue-router'

// Use in h() or defineComponent
components: { RouterLink, RouterView }
```
