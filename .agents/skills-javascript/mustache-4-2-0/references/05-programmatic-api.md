# Programmatic API

Beyond `Mustache.render()`, the library exposes lower-level classes for advanced usage.

## Mustache.Writer

The Writer is the core rendering engine. It maintains its own template cache and handles parsing and token rendering.

### Creating a writer

```js
const writer = new Mustache.Writer();
```

Each Writer instance has its own independent cache.

### Methods

**`writer.parse(template, tags)`** — Parse a template into tokens and cache it. Returns token array.

```js
const tokens = writer.parse('{{name}} says {{message}}');
```

**`writer.render(template, view, partials, config)`** — High-level render. Parses (or uses cache), creates context, renders tokens.

```js
const html = writer.render(template, view, partials, config);
```

**`writer.renderTokens(tokens, context, partials, originalTemplate, config)`** — Low-level render from pre-parsed tokens.

```js
const tokens = writer.parse(template);
const context = new Mustache.Context(view);
const html = writer.renderTokens(tokens, context, partials, template);
```

**`writer.clearCache()`** — Clear this writer's template cache.

```js
writer.clearCache();
```

### Properties

**`writer.templateCache`** — The cache object with `set(key, value)`, `get(key)`, `clear()` methods. Set to `undefined` to disable caching.

```js
writer.templateCache = undefined;  // no caching
```

## Mustache.Context

Context wraps a view object and maintains a parent reference for variable lookup.

### Creating a context

```js
const ctx = new Mustache.Context(view);
const ctx = new Mustache.Context(view, parentContext);
```

### Methods

**`ctx.lookup(name)`** — Look up a variable by name, walking up the context chain.

```js
ctx.lookup('name');           // simple lookup
ctx.lookup('user.address.city'); // dot notation
```

Lookup rules:
- Check current view first
- If not found, walk up to parent context
- If value is a function, call it with `this` = current view
- Cache results within the context

**`ctx.push(view)`** — Create a child context with a new view, keeping this context as parent.

```js
const child = ctx.push({ name: 'child' });
child.lookup('name');        // "child" (from child view)
child.lookup('parentKey');   // resolved from parent context
```

### Internal structure

```js
ctx.view        // current view object
ctx.parent      // parent Context or undefined
ctx.cache       // lookup cache (keyed by variable name)
```

The cache includes `'.'` mapped to the current view.

## Mustache.Scanner

A simple string scanner used internally by the parser. Exposed for advanced usage.

```js
const scanner = new Mustache.Scanner(string);
```

### Methods

**`scanner.eos()`** — Returns `true` if end of string is reached.

**`scanner.scan(re)`** — Try to match `re` at current position. Returns matched string or `''`.

**`scanner.scanUntil(re)`** — Skip text until `re` matches. Returns skipped text.

### Properties

```js
scanner.string   // original string
scanner.tail     // remaining unmatched text
scanner.pos      // current position index
```

## Cache control

### Default cache

The global `Mustache` object uses a default Writer with a built-in cache. Template strings are cached by their content + delimiter pair.

### Disabling cache

```js
Mustache.templateCache = undefined;
```

All subsequent `render()` calls will re-parse the template. Useful for debugging or when templates change at runtime.

### Custom cache

```js
Mustache.templateCache = {
  _map: new Map(),
  set(key, value) { this._map.set(key, value); },
  get(key) { return this._map.get(key); },
  clear() { this._map.clear(); }
};
```

The cache object must implement `set(key, value)`, `get(key)`, and `clear()`.

### Per-writer cache

Each Writer instance manages its own cache independently:

```js
const writer1 = new Mustache.Writer();
const writer2 = new Mustache.Writer();
// writer1 and writer2 have separate caches
```

## Escape override

Override the global escape function:

```js
Mustache.escape = function (text) {
  return String(text).replace(/&/g, '&amp;');  // only escape &
};
```

Or use per-render config:

```js
Mustache.render('{{html}}', { html: '<b>x</b>' }, {}, {
  escape: (text) => text   // no escaping
});
```

The config escape function takes priority over `Mustache.escape` for that render call and does not mutate the global.
