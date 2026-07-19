# Composition API

## `useRouter()`

Returns the router instance. Equivalent to `$router` in templates.

```js
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()

    function goHome() {
      router.push('/')
    }

    return { goHome }
  },
}
```

### Router instance methods

| Method | Description |
|---|---|
| `push(location)` | Navigate to a new route |
| `replace(location)` | Navigate without adding history entry |
| `go(delta)` | Traverse history |
| `back()` | Go back one entry |
| `forward()` | Go forward one entry |
| `resolve(location)` | Resolve location without navigating |
| `addRoute(record)` | Add a route at runtime |
| `removeRoute(name)` | Remove a route by name |
| `hasRoute(name)` | Check if named route exists |
| `getRoutes()` | Get all route records |
| `clearRoutes()` | Remove all routes |
| `beforeEach(guard)` | Add global before guard |
| `beforeResolve(guard)` | Add global beforeResolve guard |
| `afterEach(hook)` | Add global after hook |
| `onReady(callback)` | Called when initial navigation is done |
| `onError(handler)` | Global error handler |

### Accessing options

```js
const router = useRouter()
console.log(router.options.routes) // Original route definitions
```

## `useRoute()`

Returns the current route location as a reactive object. Equivalent to `$route` in templates.

```js
import { useRoute } from 'vue-router'
import { computed } from 'vue'

export default {
  setup() {
    const route = useRoute()

    const userId = computed(() => route.params.id)
    const searchQuery = computed(() => route.query.q)

    return { userId, searchQuery }
  },
}
```

### Route properties

| Property | Type | Description |
|---|---|---|
| `path` | `string` | Decoded path, always starts with `/` |
| `params` | `object` | Dynamic segment params |
| `query` | `object` | Parsed query string |
| `hash` | `string` | Hash including `#` |
| `fullPath` | `string` | Full encoded URL |
| `name` | `string \| undefined` | Matched route name |
| `matched` | `RouteRecord[]` | All matched route records |
| `meta` | `RouteMeta` | Merged meta from matched records |
| `redirectedFrom` | `RouteLocation \| undefined` | Original location before redirect |

### Reactivity

The route object is shallow reactive. Access properties directly — they auto-update on navigation:

```js
const route = useRoute()

watch(() => route.params.id, (newId, oldId) => {
  fetchUser(newId)
})
```

## `onBeforeRouteLeave()`

Register a leave guard in composition API. Automatically removed on unmount.

```js
import { onBeforeRouteLeave } from 'vue-router'
import { ref } from 'vue'

export default {
  setup() {
    const hasUnsaved = ref(false)

    onBeforeRouteLeave((to, from) => {
      if (hasUnsaved.value) {
        return confirm('Discard unsaved changes?')
      }
    })
  },
}
```

## `onBeforeRouteUpdate()`

Register an update guard in composition API. Triggers when the route changes but the component is reused.

```js
import { onBeforeRouteUpdate } from 'vue-router'
import { ref } from 'vue'

export default {
  setup() {
    const data = ref(null)

    onBeforeRouteUpdate(async (to, from) => {
      // Fetch new data for the new params
      data.value = await fetchItem(to.params.id)
    })
  },
}
```

## `loadRouteLocation()`

Preload a route's components before navigating. Useful for prefetching:

```js
import { loadRouteLocation } from 'vue-router'

const resolved = router.resolve({ name: 'heavy-page' })
await loadRouteLocation(resolved.route)
// Components are now loaded, navigation will be instant
router.push(resolved.route)
```

## Composable patterns

### Reactive route-based computed

```js
import { useRoute } from 'vue-router'
import { computed, watch } from 'vue'

export default {
  setup() {
    const route = useRoute()

    const title = computed(() => {
      return route.meta.title || 'Untitled'
    })

    watch(title, (newTitle) => {
      document.title = newTitle
    })

    return { title }
  },
}
```

### Conditional navigation on mount

```js
import { useRouter, useRoute } from 'vue-router'
import { onMounted } from 'vue'

export default {
  setup() {
    const router = useRouter()
    const route = useRoute()

    onMounted(() => {
      if (!route.query.returnUrl) {
        router.replace({ ...route, query: { ...route.query, returnUrl: '/' } })
      }
    })
  },
}
```

### Debounced search

```js
import { useRoute, useRouter } from 'vue-router'
import { watch, ref } from 'vue'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const query = ref(route.query.q || '')

    watch(query, (newQuery) => {
      router.replace({
        query: { ...route.query, q: newQuery },
      })
    })

    return { query }
  },
}
```

## Injection keys

Internal symbols used for dependency injection. Useful for testing and advanced scenarios:

```js
import {
  routerKey,
  routeLocationKey,
  matchedRouteKey,
  viewDepthKey,
  routerViewLocationKey,
} from 'vue-router'
```

Override in tests:

```js
import { routerKey, routeLocationKey } from 'vue-router'

// Provide mock router/route in test setup
app.provide(routerKey, mockRouter)
app.provide(routeLocationKey, mockRoute)
```
