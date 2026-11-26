# Getting Started

## Package managers

```bash
npm install vue-router
yarn add vue-router
pnpm add vue-router
bun add vue-router
```

New projects: `npm create vue@latest` (or yarn/pnpm/bun equivalents) scaffolds a Vite-based project with the option to include Vue Router; its example app demonstrates core features.

## Build-tool setup

```js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router) // must happen before app.mount()
app.mount('#app')
```

The plugin registers `RouterView` and `RouterLink` globally, adds `$router`/`$route`, enables `useRouter()`/`useRoute()`, and triggers resolution of the initial route.

## The App component

```vue
<template>
  <h1>Hello App!</h1>
  <p><strong>Current route path:</strong> {{ $route.fullPath }}</p>
  <nav>
    <RouterLink to="/">Go to Home</RouterLink>
    <RouterLink to="/about">Go to About</RouterLink>
  </nav>
  <main>
    <RouterView />
  </main>
</template>
```

- `RouterLink` creates links that change the URL without a page reload; it also handles URL generation and encoding.
- `RouterView` renders the route component matched by the current URL. It must exist somewhere in the tree (not necessarily in `App.vue`), or nothing renders.
- `$route` in templates is the reactive object describing the current route (`fullPath`, `path`, `params`, `query`, `hash`).

## Accessing the router and current route

| Context | Router | Current route |
|---|---|---|
| Template | `$router` | `$route` |
| Options API JS | `this.$router` | `this.$route` |
| Composition API | `useRouter()` | `useRoute()` |
| Outside components | import the exported router instance | `router.currentRoute.value` |

`RouterView` and `RouterLink` are registered globally, so no import is needed in templates; you may still import them locally. In-DOM templates require kebab-case and no self-closing tags: `<router-view></router-view>`.

## CDN / build-less usage

Global build (exposes `Vue` and `VueRouter` globals):

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/vue-router@5.5.2/dist/vue-router.global.js"></script>
```

ES module build (use import maps; recommend pinning exact versions):

```html
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js",
      "vue-router": "https://unpkg.com/vue-router@5.5.2/dist/vue-router.esm-browser.js",
      "@vue/devtools-api": "https://unpkg.com/@vue/devtools-api@8/dist/vue-devtools-api.esm-browser.js"
    }
  }
</script>
```

`@vue/devtools-api` is only needed by the development ESM build — remove it when using `vue-router.esm-browser.prod.js` or `vue-router.global.prod.js`.

## Conventions

- The guide assumes knowledge of Vue itself; route components are plain Vue components (also called _views_).
- Both Composition API (`<script setup>`) and Options API work everywhere.
- `router` refers to the object from `createRouter()`; `route` refers to the current normalized route location.
