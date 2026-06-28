# Installation & Setup

## CDN

Include the script tag in `<head>` **before Alpine.js**:

```html
<script src="https://cdn.jsdelivr.net/npm/pinecone-router@7.6.0/dist/router.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js"></script>
```

The CDN build exposes `PineconeRouter` globally as an IIFE module. Alpine.js auto-detects it when loaded after.

## NPM

```bash
npm install pinecone-router
```

```js
import Alpine from 'alpinejs'
import PineconeRouter from 'pinecone-router'

Alpine.plugin(PineconeRouter)
Alpine.start()
```

## Browser ESM

```js
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/module.esm.js'
import PineconeRouter from 'https://cdn.jsdelivr.net/npm/pinecone-router@7.6.0/dist/router.esm.js'

Alpine.plugin(PineconeRouter)
Alpine.start()
```

## Alpine.js Plugin Registration

Pinecone Router registers as an Alpine.js plugin. On registration it:

1. Creates the `PineconeRouter` reactive object and assigns it to `window.PineconeRouter` and `Alpine.$router`
2. Registers three magic helpers: `$router`, `$history`, `$params`
3. Sets up `popstate` listener for browser back/forward navigation
4. Installs click interception on `document.body`
5. Registers the `x-route`, `x-handler`, and `x-template` directives (in that order)
6. On `alpine:initialized`, performs initial navigation to the current URL path

### With Alpine Plugins

```js
import Alpine from 'alpinejs'
import Persist from '@alpinejs/persist'
import PineconeRouter from 'pinecone-router'

// Register plugins before starting
Alpine.plugin(Persist)
Alpine.plugin(PineconeRouter)

Alpine.start()
```

### With event listeners

```js
document.addEventListener('alpine:init', () => {
  // Configure settings before Alpine starts
  PineconeRouter.settings({
    targetID: 'app',
    basePath: '/app',
  })

  // Register global data components
  Alpine.data('router', () => ({
    globalHandler(context) {
      console.log('Navigated to', context.path)
    },
  }))
})
```

## Compatibility

| Pinecone Router | Alpine.js |
|-----------------|-----------|
| ^7.x            | v3        |
| ^2.x            | v3        |
| v1.x            | v2        |

## Bundle Size

The minified+gzipped bundle is approximately 5KB. The library has zero runtime dependencies beyond Alpine.js.
