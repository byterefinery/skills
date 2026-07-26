# Browser Usage

## UMD Distribution

The `dist/handlebars-layouts.js` file is a Browserify-bundled UMD module. It works in three environments:

### CommonJS (Node.js, Browserify, Webpack)

```js
const layouts = require('handlebars-layouts');
const Handlebars = require('handlebars');
layouts.register(Handlebars);
```

### AMD (RequireJS)

```js
define(['handlebars', 'handlebars-layouts'], function(Handlebars, layouts) {
  layouts.register(Handlebars);
});
```

### Global Variable

```html
<script src="handlebars.min.js"></script>
<script src="dist/handlebars-layouts.js"></script>
<script>
  handlebarsLayouts.register(Handlebars);
</script>
```

The global variable is `handlebarsLayouts` (camelCase).

## Bower Installation

```bash
bower install shannonmoeller/handlebars-layouts
```

This installs the package into `bower_components/handlebars-layouts/` with the dist file available at `bower_components/handlebars-layouts/dist/handlebars-layouts.js`.

## Precompiled Templates

For browser environments, precompile templates on the server and include the compiled JS:

```js
! Build step (Node.js)
const Handlebars = require('handlebars');
const fs = require('fs');

const source = fs.readFileSync('page.hbs', 'utf8');
const compiled = Handlebars.precompile(source);
fs.writeFileSync('dist/page-compiled.js', compiled);
```

```html
! Browser
<script src="handlebars.runtime.min.js"></script>
<script src="dist/handlebars-layouts.js"></script>
<script src="dist/layout-compiled.js"></script>
<script src="dist/page-compiled.js"></script>
<script>
  handlebarsLayouts.register(Handlebars);

  ! Register compiled layout as partial
  Handlebars.registerPartial('layout', Handlebars.templates['layout']);

  ! Render page
  var html = Handlebars.templates['page']({ title: 'Hello' });
  document.getElementById('app').innerHTML = html;
</script>
```

## Inline Script Registration

For simple single-page setups:

```html
<!doctype html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.7.8/handlebars.min.js"></script>
  <script src="handlebars-layouts.js"></script>
</head>
<body>
  ! Layout partial (registered inline)
  <script id="layout" type="text/x-handlebars-template">
    <!doctype html>
    <html>
    <head><title>{{title}}</title></head>
    <body>
      {{#block "body"}}<p>Default</p>{{/block}}
    </body>
    </html>
  </script>

  ! Page template
  <script id="page" type="text/x-handlebars-template">
    {{#extend "layout"}}
      {{#content "body"}}
        <h1>Hello World</h1>
      {{/content}}
    {{/extend}}
  </script>

  <script>
    Handlebars.registerHelper(handlebarsLayouts.register(Handlebars));

    Handlebars.registerPartial('layout',
      document.getElementById('layout').textContent.trim()
    );

    var template = Handlebars.compile(
      document.getElementById('page').textContent.trim()
    );

    document.open();
    document.write(template({ title: 'My Page' }));
    document.close();
  </script>
</body>
</html>
```

## Module Bundlers

### Webpack

handlebars-layouts works with Webpack out of the box as a CommonJS module:

```js
! webpack.config.js
module.exports = {
  entry: './src/app.js',
  output: { filename: 'bundle.js' },
};
```

```js
! src/app.js
import Handlebars from 'handlebars';
import layouts from 'handlebars-layouts';

layouts.register(Handlebars);
```

### Browserify

```bash
browserify src/app.js -o dist/bundle.js
```

The UMD wrapper in `dist/handlebars-layouts.js` already handles Browserify.

## Standalone Handlebars

When using `handlebars.runtime` (runtime-only build without compiler), all templates must be precompiled. The layout helpers still work, but partials must be precompiled and registered:

```js
const Handlebars = require('handlebars.runtime');
const layouts = require('handlebars-layouts');

layouts.register(Handlebars);

! Precompiled partials self-register
require('./partials/layout-compiled');
Handlebars.registerPartial('layout', Handlebars.templates['layout']);

! Precompiled page
require('./pages/home-compiled');
const html = Handlebars.templates['home'](context);
```

## CSP Considerations

If using Content Security Policy with `unsafe-inline` disallowed, precompile all templates and avoid inline `<script>` templates. Use external `.hbs` files compiled at build time.
