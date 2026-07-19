# Build-less Browser Usage

Pinia ships multiple build formats that allow usage without any build tool. This covers CDN loading, global IIFE builds, ESM browser builds, import maps, and production deployment.

## Build Files

| File | Format | Description |
|---|---|---|
| `dist/pinia.iife.js` | IIFE (global) | Dev build, exposes global `Pinia`, depends on global `Vue` |
| `dist/pinia.iife.prod.js` | IIFE (global, minified) | Production build, dev checks stripped, `nostics` excluded |
| `dist/pinia.esm-browser.js` | ESM | Dev build for browsers, imports from `vue` via import map |
| `dist/pinia.esm-browser.prod.js` | ESM (minified) | Production build, imports only from `vue` |
| `dist/pinia.js` | ESM (bundlers) | For Node/bundler usage via `package.json` exports |

## IIFE Global Build

The simplest approach — load Vue and Pinia as globals from a CDN:

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/pinia@4.0.2/dist/pinia.iife.js"></script>
```

All Pinia APIs are available on the `Pinia` global object:

```js
const { createPinia, defineStore, storeToRefs, mapStores, mapState, mapActions } = Pinia
const { createApp, ref, computed } = Vue
```

### Full example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Pinia Build-less Demo</title>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <script src="https://unpkg.com/pinia@4.0.2/dist/pinia.iife.js"></script>
</head>
<body>
  <div id="app">
    <h1>{{ store.title }}</h1>
    <p>Count: {{ store.count }} (double: {{ store.double }})</p>
    <button @click="store.increment()">Increment</button>
    <button @click="store.reset()">Reset</button>
  </div>

  <script>
    const { createApp } = Vue
    const { createPinia, defineStore } = Pinia

    const useCounter = defineStore('counter', {
      state: () => ({ count: 0, title: 'Pinia Demo' }),
      getters: {
        double: (state) => state.count * 2,
      },
      actions: {
        increment() { this.count++ },
        reset() { this.$reset() },
      },
    })

    const app = createApp({
      setup() {
        const store = useCounter()
        return { store }
      },
    })

    app.use(createPinia())
    app.mount('#app')
  </script>
</body>
</html>
```

## ESM Browser Build with Import Maps

For module-native usage without bundling, use the ESM browser build with an import map:

```html
<script type="importmap">
{
  "imports": {
    "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js",
    "pinia": "https://unpkg.com/pinia@4.0.2/dist/pinia.esm-browser.js"
  }
}
</script>

<script type="module">
  import { createApp, ref } from 'vue'
  import { createPinia, defineStore } from 'pinia'

  const useCounter = defineStore('counter', {
    state: () => ({ count: 0 }),
    actions: { increment() { this.count++ } }
  })

  createApp({
    setup() {
      const store = useCounter()
      return { store }
    },
    template: `<button @click="store.increment()">{{ store.count }}</button>`
  })
  .use(createPinia())
  .mount('#app')
</script>
```

### Browser support for import maps

- Chrome 89+, Firefox 108+, Safari 16.4+, Edge 89+
- For older browsers, use the IIFE global build

### Splitting into separate modules

For larger applications, split stores and components into separate files:

```html
<!-- index.html -->
<script type="importmap">
{
  "imports": {
    "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js",
    "pinia": "https://unpkg.com/pinia@4.0.2/dist/pinia.esm-browser.js"
  }
}
</script>

<script type="module" src="./main.js"></script>
```

```js
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounter = defineStore('counter', {
  state: () => ({ count: 0 }),
  actions: { increment() { this.count++ } }
})
```

```js
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useCounter } from './stores/counter.js'

createApp({
  setup() {
    return { counter: useCounter() }
  },
  template: `<button @click="counter.increment()">{{ counter.count }}</button>`
})
.use(createPinia())
.mount('#app')
```

## Production Deployment

For production, use the minified builds:

```html
<!-- IIFE production -->
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://unpkg.com/pinia@4.0.2/dist/pinia.iife.prod.js"></script>

<!-- ESM production -->
<script type="importmap">
{
  "imports": {
    "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js",
    "pinia": "https://unpkg.com/pinia@4.0.2/dist/pinia.esm-browser.prod.js"
  }
}
</script>
```

Production builds:
- Remove all `__DEV__`-guarded code (error checks, warnings)
- Remove `__USE_DEVTOOLS__` features (devtools plugin)
- Strip `nostics` diagnostic library entirely
- Minify output

## CDN Alternatives

| CDN | IIFE dev | IIFE prod | ESM dev |
|---|---|---|---|
| unpkg | `unpkg.com/pinia@4.0.2/dist/pinia.iife.js` | `unpkg.com/pinia@4.0.2/dist/pinia.iife.prod.js` | `unpkg.com/pinia@4.0.2/dist/pinia.esm-browser.js` |
| jsDelivr | `cdn.jsdelivr.net/npm/pinia@4.0.2/dist/pinia.iife.js` | `cdn.jsdelivr.net/npm/pinia@4.0.2/dist/pinia.iife.prod.js` | `cdn.jsdelivr.net/npm/pinia@4.0.2/dist/pinia.esm-browser.js` |

The `unpkg` and `jsdelivr` fields in `package.json` both point to `dist/pinia.iife.js`, so bare URLs like `unpkg.com/pinia@4.0.2` resolve to the IIFE build automatically.

## HTTP Server Requirement

ES modules and import maps require an HTTP server — they do not work over `file://` protocol. Use a simple static server:

```bash
# Python
python3 -m http.server 3000

# Node
npx serve .

# PHP
php -S localhost:3000
```

## Gotchas

- **IIFE depends on global `Vue`** — load Vue's global build before Pinia's IIFE build. The IIFE build reads `Vue` from `window`.
- **`@vue/devtools-api` is a peer dependency** — the IIFE build bundles `nostics` but expects `@vue/devtools-api` to be available. For build-less usage, devtools integration works when Vue Devtools extension is installed in the browser.
- **No tree-shaking with IIFE** — the global build includes all Pinia code. For smaller bundles, use the ESM build with a bundler.
- **Dev build includes diagnostics** — `pinia.iife.js` bundles `nostics` for runtime warnings. Production build `pinia.iife.prod.js` excludes it entirely.
- **`process.env` not available in browsers** — the ESM browser builds replace `process.env.NODE_ENV` at build time, so you don't need to worry about it.
