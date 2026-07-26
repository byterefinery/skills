# Module Systems

mustache.js 4.2.0 supports multiple module formats out of the box.

## ESM (ECMAScript Modules)

```js
import Mustache from 'mustache/mustache.mjs';
```

The `mustache.mjs` file is the ESM entry point. The `package.json` `exports` field maps:
- `import` → `./mustache.mjs`
- `require` → `./mustache.js`

## CommonJS

```js
const Mustache = require('mustache');
```

The default `main` field points to `mustache.js`, which is a UMD module that works as CommonJS.

## AMD

The UMD build detects AMD loaders (RequireJS, etc.) and registers as an anonymous module:

```js
define(['mustache'], function (Mustache) {
  // use Mustache
});
```

## Global browser script

Include via script tag — exposes global `Mustache`:

```html
<script src="mustache.js"></script>
<script>
  Mustache.render('{{name}}', { name: 'Alice' });
</script>
```

From CDN:

```html
<script src="https://unpkg.com/mustache@4.2.0"></script>
```

## Deno

```ts
import Mustache from 'https://esm.sh/mustache@4.2.0';
```

Or with a Deno-compatible import map.

## Wrapped builds

The repository includes wrapper files for legacy frameworks (jQuery, MooTools, Dojo, YUI3, qooxdoo). These are built via Rake and are not included in the npm package by default.

## Package structure

```
mustache/
├── mustache.js      # UMD build (CommonJS + AMD + global)
├── mustache.mjs     # ESM build
├── mustache.min.js  # Minified UMD
├── bin/mustache     # CLI tool
└── wrappers/        # Legacy framework wrappers
```

The `files` field in `package.json` includes `bin/`, `mustache.mjs`, `mustache.min.js`, and `wrappers/`.
