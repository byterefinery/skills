# Helper API

## Registration

```js
Handlebars.registerHelper('name', function(arg1, arg2, options) {
  // ...
});

! Register multiple at once:
Handlebars.registerHelper({
  upper: function(str) { return str.toUpperCase(); },
  lower: function(str) { return str.toLowerCase(); },
});

Handlebars.unregisterHelper('name');
```

## Helper signature

```js
function helperName(arg1, arg2, ..., options) {
  ! options.fn          — block body template function
  ! options.inverse     — else block template function
  ! options.hash        — named arguments as object
  ! options.data        — Handlebars data object (@root, @index, etc.)
  ! options.lookupProperty — safe property lookup (respects proto-access)
  ! options.name        — helper name string
  ! options.id          — helper ID string
  ! options.loc         — source location { start: { line, column }, end: { line, column } }
}
```

The `options` argument is always the last parameter. Helpers can have any number of positional arguments before it.

## Simple helpers

Return a value that gets inserted into the output:

```js
Handlebars.registerHelper('add', function(a, b) {
  return Number(a) + Number(b);
});
! Template: {{add 2 3}} → "5"
```

## Block helpers

Block helpers receive `options.fn` (the block body) and `options.inverse` (the else block). Call them with a context and optional options:

```js
Handlebars.registerHelper('eq', function(a, b, options) {
  if (a === b) {
    return options.fn(this);       ! render block body with current context
  } else {
    return options.inverse(this);  ! render else block
  }
});
```

```handlebars
{{#eq a b}}
  Equal!
{{else}}
  Not equal.
{{/eq}}
```

### `options.fn` and `options.inverse` signatures

```js
options.fn(context)                          ! render with new context
options.fn(context, { data: customData })    ! with custom data
options.fn(context, { blockParams: [a, b] }) ! with block params
```

- `options.fn(context)` — render block with given context
- `options.inverse(context)` — render else block (returns `''` if no else block)
- If no context is passed, the current context (`this`) is used

## Block params

Expose named variables inside a block:

```js
Handlebars.registerHelper('entries', function(obj, options) {
  let out = '';
  const keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    out += options.fn(obj[key], {
      blockParams: [key, obj[key]]
    });
  }
  return out;
});
```

```handlebars
{{#entries config as |key value|}}
  {{key}} = {{value}}
{{/entries}}
```

Block params are accessed positionally in the `as |...|` clause. The `@index` and `@key` data variables are also available if the helper sets them on `options.data`.

Internally, block params use the `blockParams` array. The `Handlebars.blockParams(params, ids)` utility wraps params with a `path` property:

```js
Handlebars.blockParams([value], [contextPath]);
```

## Hash arguments

Named arguments passed to helpers appear in `options.hash`:

```js
Handlebars.registerHelper('link', function(text, options) {
  const url = options.hash.href || '#';
  const target = options.hash.target || '_self';
  return new Handlebars.SafeString(
    `<a href="${url}" target="${target}">${text}</a>`
  );
});
```

```handlebars
{{link "Google" href="https://google.com" target="_blank"}}
```

## Iterating inside helpers

When a block helper needs to render multiple items, accumulate results into a string:

```js
Handlebars.registerHelper('repeat', function(n, options) {
  let out = '';
  for (let i = 0; i < n; i++) {
    out += options.fn(this, { data: Handlebars.createFrame(options.data) });
  }
  return out;
});
```

Use `Handlebars.createFrame(options.data)` to create a fresh data frame for each iteration, preserving parent data like `@root`. The frame has a `_parent` reference to the original data.

## The `lookupProperty` option

Each helper receives `options.lookupProperty` for safe property access that respects proto-access controls:

```js
Handlebars.registerHelper('get', function(obj, prop, options) {
  return options.lookupProperty(obj, prop);
});
```

This is the same lookup used internally by Handlebars and respects `allowedProtoProperties` / `allowedProtoMethods` settings.

## HelperMissing and blockHelperMissing

These are internal hooks, moved to `container.hooks` at runtime (not in `container.helpers`):

- **`helperMissing`** — called when a simple mustache `{{foo}}` resolves to undefined. Returns `undefined` (renders as empty string). Throws if someone tries to call a missing expression as a function (i.e., `{{foo bar}}` with no helper `foo`).
- **`blockHelperMissing`** — called when a block `{{#foo}}` has no registered helper. Implements Mustache-style behavior:
  - `true` → render block with current context
  - `false` / `null` / `undefined` → render inverse
  - Array → iterate via `each` (renders inverse if empty)
  - Object → shift context to that object

Override them in a `Handlebars.create()` instance for custom behavior:

```js
const hb = Handlebars.create();
hb.registerHelper('helperMissing', function() {
  return '[MISSING]';
});
```

Use `allowCallsToHelperMissing: true` runtime option to keep these in the helpers object instead of moving to hooks (backward compat with compiler rev 7).

## Decorators

Decorators modify template or helper behavior at setup time. They receive the template function and can wrap or replace it:

```js
Handlebars.registerDecorator('logRender', function(fn, props, container, context, options) {
  return function(context, options) {
    console.log('Rendering template');
    return fn(context, options);
  };
});
```

```handlebars
{{#*logRender}}
  {{name}}
{{/logRender}}
```

Decorator signature: `function(fn, props, container, depth0, data, blockParams, depths)`

- `fn` — the template function being decorated
- `props` — plain object for attaching properties to the returned function
- `container` — the template container (helpers, partials, decorators)
- `depth0` — the root context
- `data` — the data object
- `blockParams` — block params stack
- `depths` — depth contexts

The built-in `@inline` decorator captures a block as a local partial:

```js
! Internal: registerDefaultDecorators(instance)
! - @inline "partialName" — stores options.fn in props.partials[partialName]
```

## Async helpers

Handlebars 4.7.9 is fully synchronous. For async helpers, use a wrapper library like `promised-handlebars` or `@anthony-c/async-handlebars`. Native async/await is not supported.

## Utility functions

Handlebars exposes utility functions for use in helpers:

```js
Handlebars.createFrame(object)    ! shallow clone with _parent reference
Handlebars.blockParams(params, ids) ! wrap params with path metadata
Handlebars.escapeExpression(str)   ! HTML-escape a string
Handlebars.log(level, ...message)  ! log via the internal logger
```
