# Getting Started

## Installation

### npm / pnpm

```bash
npm install vue-router@5.2.0
# or
pnpm add vue-router@5.2.0
```

Peer dependency: Vue 3.5.34+ or Vue 4.0.0+.

### CDN (build-less)

Development build (with warnings):

```html
<script src="https://unpkg.com/vue-router@5.2.0/dist/vue-router.global.js"></script>
```

Production build (minified):

```html
<script src="https://unpkg.com/vue-router@5.2.0/dist/vue-router.global.prod.js"></script>
```

The global build exposes `VueRouter` on the window. It depends on `Vue` being loaded first.

### ESM module (browser)

For module-native environments without a bundler:

```html
<script type="module">
  import { createRouter, createWebHistory } from 'https://unpkg.com/vue-router@5.2.0/dist/vue-router.esm-browser.js'
</script>
```

Production ESM:

```html
<script type="module">
  import { createRouter, createWebHistory } from 'https://unpkg.com/vue-router@5.2.0/dist/vue-router.esm-browser.prod.js'
</script>
```

## Available builds

| Build | File | Use case |
|---|---|---|
| ESM | `dist/vue-router.js` | Bundlers (Vite, Webpack, Rolldown) — tree-shakeable |
| ESM browser | `dist/vue-router.esm-browser.js` | Browser `<script type="module">` — dev with warnings |
| ESM browser prod | `dist/vue-router.esm-browser.prod.js` | Browser `<script type="module">` — minified |
| CJS | `dist/vue-router.cjs` | Node.js / CommonJS — dev with warnings |
| CJS prod | `dist/vue-router.prod.cjs` | Node.js / CommonJS — minified |
| IIFE global | `dist/vue-router.global.js` | `<script>` tag — dev with warnings |
| IIFE global prod | `dist/vue-router.global.prod.js` | `<script>` tag — minified |

## Project structure

Standard Vue Router setup in a Vite project:

```
src/
├── router/
│   └── index.js        # router creation + route definitions
├── views/
│   ├── Home.vue
│   ├── About.vue
│   └── User.vue
├── App.vue
└── main.js
```

**`src/router/index.js`**:

```js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/about', component: About },
  ],
})

export default router
```

**`src/main.js`**:

```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
```

**`src/App.vue`**:

```vue
<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <RouterLink to="/about">About</RouterLink>
  </nav>
  <RouterView />
</template>
```

## Build-less full example

Complete single-file app with no build step:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Vue Router Demo</title>
</head>
<body>
  <div id="app">
    <nav>
      <a href="#/">Home</a>
      <a href="#/about">About</a>
    </nav>
    <div id="view"></div>
  </div>

  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <script src="https://unpkg.com/vue-router@5.2.0/dist/vue-router.global.js"></script>
  <script>
    const { createApp, h, resolveComponent } = Vue
    const { createRouter, createWebHashHistory, RouterLink, RouterView } = VueRouter

    // Define components
    const Home = { template: '<h1>Home Page</h1><p>Welcome!</p>' }
    const About = { template: '<h1>About</h1><p>Vue Router 5.2.0</p>' }

    // Create router
    const router = createRouter({
      history: createWebHashHistory(),
      routes: [
        { path: '/', component: Home },
        { path: '/about', component: About },
      ],
    })

    // Root component using RouterLink and RouterView
    const App = {
      components: { RouterLink, RouterView },
      template: `
        <div>
          <nav>
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/about">About</RouterLink>
          </nav>
          <RouterView />
        </div>
      `,
    }

    // Mount
    const app = createApp(App)
    app.use(router)
    app.mount('#app')
  </script>
</body>
</html>
```

## Rendering with `h()` in build-less

When using the render function API without templates:

```js
const App = {
  setup() {
    return () => h('div', [
      h('nav', [
        h(VueRouter.RouterLink, { to: '/' }, () => 'Home'),
        h(VueRouter.RouterLink, { to: '/about' }, () => 'About'),
      ]),
      h(VueRouter.RouterView),
    ])
  },
}
```
