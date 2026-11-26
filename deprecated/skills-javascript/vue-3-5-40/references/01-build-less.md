# Build-less Vue

Using Vue without a build step — CDN, global build, ES modules, import maps.

## Table of Contents

- [Global Build](#global-build)
- [ES Module Build](#es-module-build)
- [Import Maps](#import-maps)
- [Splitting Modules](#splitting-modules)
- [Options API without Build](#options-api-without-build)
- [Production Deployment](#production-deployment)
- [Local HTTP Server](#local-http-server)

## Global Build

Load Vue from a CDN as a global script. All top-level APIs are exposed as properties on the global `Vue` object.

```html
<script src="https://unpkg.com/vue@3.5.40/dist/vue.global.js"></script>

<div id="app">{{ message }}</div>

<script>
  const { createApp, ref } = Vue

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return { message }
    }
  }).mount('#app')
</script>
```

CDN sources: unpkg, jsdelivr, cdnjs. Or download and self-host.

### Options API with Global Build

```html
<script src="https://unpkg.com/vue@3.5.40/dist/vue.global.js"></script>

<div id="app">{{ message }}</div>

<script>
  const { createApp } = Vue

  createApp({
    data() {
      return { message: 'Hello Vue!' }
    }
  }).mount('#app')
</script>
```

## ES Module Build

Use native ES modules via `<script type="module">`. This is the preferred build-less approach for modern browsers.

```html
<div id="app">{{ message }}</div>

<script type="module">
  import { createApp, ref } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return { message }
    }
  }).mount('#app')
</script>
```

## Import Maps

Teach the browser where to resolve bare specifiers like `'vue'` using [Import Maps](https://caniuse.com/import-maps).

```html
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
    }
  }
</script>

<div id="app">{{ message }}</div>

<script type="module">
  import { createApp, ref } from 'vue'

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return { message }
    }
  }).mount('#app')
</script>
```

Add additional entries for other dependencies — ensure they point to ES module builds of those libraries.

**Browser support**: Import Maps is supported in modern browsers. Safari 16.4+ required.

## Splitting Modules

Split code into separate `.js` files for manageability.

```html [index.html]
<div id="app"></div>

<script type="module">
  import { createApp } from 'vue'
  import MyComponent from './my-component.js'

  createApp(MyComponent).mount('#app')
</script>
```

```js [my-component.js]
import { ref } from 'vue'

export default {
  setup() {
    const count = ref(0)
    return { count }
  },
  template: `<div>Count: {{ count }}</div>`
}
```

The template is an inlined JavaScript string that Vue compiles at runtime. For VS Code syntax highlighting, install the `es6-string-html` extension and prefix strings with `/*html*/`.

## Options API without Build

```js
export default {
  data() {
    return { count: 0 }
  },
  methods: {
    increment() {
      this.count++
    }
  },
  mounted() {
    console.log(`Initial count: ${this.count}`)
  },
  template: `<button @click="increment">Count: {{ count }}</button>`
}
```

Or target an in-DOM template element:

```js
export default {
  data() { return { count: 0 } },
  template: '#my-template'
}
```

```html
<template id="my-template">
  <button @click="count++">Count: {{ count }}</button>
</template>
```

## Production Deployment

The examples above use development builds. For production:

- Use the production build by replacing `.global.js` with `.global.prod.js` or `.esm-browser.js` with `.esm-browser.prod.js`
- Or use URL hash: `vue.global.js` → `vue.global.prod.js`
- Production builds are smaller and strip dev-only warnings

```html
<!-- Production -->
<script src="https://unpkg.com/vue@3.5.40/dist/vue.global.prod.js"></script>
```

For ES module production:

```html
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3.5.40/dist/vue.esm-browser.prod.js"
    }
  }
</script>
```

## Local HTTP Server

ES modules require `http://` protocol — they don't work over `file://`. Serve your files with a local HTTP server:

```bash
# From the directory containing index.html
npx serve
# or
npx vite serve
# or any static file server
```

This is required whenever you use `<script type="module">` with local imports.

## Alternative: Petite Vue

For progressive enhancement of static HTML (similar to jQuery or Alpine.js use cases), consider [petite-vue](https://github.com/vuejs/petite-vue) — a 6 kB subset of Vue optimized for no-build-step scenarios. It uses `v-init` to activate and works with attribute-style bindings.
