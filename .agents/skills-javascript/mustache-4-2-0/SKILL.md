---
name: mustache-4-2-0
description: Render Mustache.js 4.2.0 logic-less templates — variables, sections, inverted sections, partials, custom delimiters, higher-order sections (lambdas), pre-parsing, cache control, custom escape, CLI tool. Use for .mustache template authoring, server-side rendering, config file generation, and any text templating without logic
license: MIT
compatibility: Node.js or browser. Supports CommonJS, ESM, AMD, and global script. Zero runtime dependencies
metadata:
  tags:
    - templating
    - javascript
    - html
    - mustache
    - logic-less
---

# mustache 4.2.0

## Overview

Mustache.js is a zero-dependency implementation of the Mustache template system in JavaScript. Mustache is a *logic-less* template syntax — no if statements, else clauses, or for loops. Only tags that expand using values from a view object. Works for HTML, config files, source code — any text format.

Version 4.2.0 is the latest stable release. It supports CommonJS, ESM (`mustache.mjs`), AMD, and global browser script.

### Core API

- `Mustache.render(template, view, partials, config)` — render a template string with a view object
- `Mustache.parse(template, tags)` — pre-parse a template into tokens and cache it
- `Mustache.clearCache()` — clear the template parse cache
- `Mustache.escape(text)` — HTML-escape a string (overridable)
- `Mustache.tags` — default delimiters `['{{', '}}']` (overridable)
- `Mustache.templateCache` — get/set the caching strategy (set to `undefined` to disable)

### Template Tag Types

| Tag | Syntax | Description |
|---|---|---|
| Variable | `{{name}}` | Lookup and HTML-escape value |
| Raw variable | `{{{name}}}` or `{{&name}}` | Lookup without escaping |
| Section | `{{#name}}...{{/name}}` | Conditional or iteration block |
| Inverted section | `{{^name}}...{{/name}}` | Render when value is falsy or empty |
| Partial | `{{> partial_name}}` | Include another template |
| Comment | `{{! comment }}` | Ignored in output |
| Set delimiter | `{{=<% %>=}}` | Change tag delimiters |

### Section Behavior

- **Falsy** (`null`, `undefined`, `false`, `0`, `NaN`, `""`, `[]`) — block not rendered
- **Non-empty array** — block rendered once per item, context shifted to each item
- **Object / string / number** — block rendered once, context shifted to that value
- **Function** — higher-order section: function receives `(rawText, renderFn)` and returns output string

## Usage

### Basic rendering

```js
import Mustache from 'mustache';

const view = {
  title: 'Joe',
  calc: () => 2 + 4
};

const output = Mustache.render('{{title}} spends {{calc}}', view);
// "Joe spends 6"
```

### Variables with dot notation

```js
const view = {
  name: { first: 'Michael', last: 'Jackson' }
};

Mustache.render('{{name.first}} {{name.last}}', view);
// "Michael Jackson"
```

### Iterating arrays

```js
const view = {
  stooges: [
    { name: 'Moe' },
    { name: 'Larry' },
    { name: 'Curly' }
  ]
};

Mustache.render('{{#stooges}}<b>{{name}}</b>{{/stooges}}', view);
// "<b>Moe</b><b>Larry</b><b>Curly</b>"
```

For arrays of primitives, use `{{.}}` to reference the current item:

```js
Mustache.render('{{#items}}* {{.}}{{/items}}', { items: ['a', 'b', 'c'] });
// "* a\n* b\n* c"
```

### Inverted sections

```js
Mustache.render(
  '{{#repos}}<b>{{name}}</b>{{/repos}}{{^repos}}No repos :({{/repos}}',
  { repos: [] }
);
// "No repos :("
```

### Partials

```js
const base = '<h2>Names</h2>{{#names}}{{> user}}{{/names}}';
const user = '<strong>{{name}}</strong>';

Mustache.render(base, { names: [{ name: 'Alice' }] }, { user });
// "<h2>Names</h2><strong>Alice</strong>"
```

Partials inherit the calling context, so `{{name}}` inside the partial resolves from the parent view.

### Custom delimiters

```js
// Pass as 4th argument to render (does not mutate Mustache.tags)
const template = '<% foo %> {{foo}}';
Mustache.render(template, { foo: 'bar' }, {}, ['<%', '%>']);
// "bar {{foo}}"

// Or inline in template
const template2 = '{{ foo }}{{=<% %>=}}<% bar %><%={{ }}=%>{{ baz }}';
Mustache.render(template2, { foo: '1', bar: '2', baz: '3' });
// "123"
```

### Custom escape function

```js
// Disable escaping entirely
Mustache.escape = (text) => text;

// Or per-render via config
Mustache.render('{{html}}', { html: '<b>hi</b>' }, {}, {
  escape: (text) => text   // no escaping
});
```

### Pre-parsing and caching

```js
// Parse once, render many times
Mustache.parse(template);
const out1 = Mustache.render(template, view1);
const out2 = Mustache.render(template, view2);

// Clear cache
Mustache.clearCache();

// Disable caching entirely
Mustache.templateCache = undefined;

// Custom cache
Mustache.templateCache = {
  _map: new Map(),
  set(key, value) { this._map.set(key, value); },
  get(key) { return this._map.get(key); },
  clear() { this._map.clear(); }
};
```

### Higher-order sections (lambdas)

Section values that are functions receive the raw template text and a render function:

```js
const view = {
  name: 'Tater',
  bold: function () {
    return function (text, render) {
      return '<b>' + render(text) + '</b>';
    };
  }
};

Mustache.render('{{#bold}}Hi {{name}}.{{/bold}}', view);
// "<b>Hi Tater.</b>"
```

The function itself is called with the current context as `this`, and returns another function that receives `(text, render)`.

### Writer and Context (advanced)

```js
const writer = new Mustache.Writer();
writer.templateCache = undefined;  // no caching
const tokens = writer.parse(template, ['<%', '%>']);
const context = new Mustache.Context(view);
const html = writer.renderTokens(tokens, context, partials, template);
```

- `Mustache.Writer` — independent render engine with its own cache
- `Mustache.Context(view, parent)` — context stack for lookups
- `Mustache.Scanner(string)` — low-level string scanner

### CLI tool

```bash
# Render template with JSON view
mustache data.json template.mustache > output.html

# With partials
mustache -p partial1.mustache -p partial2.mustache data.json template.mustache

# From stdin
cat data.json | mustache - template.mustache

# JS view file (supports functions)
mustache view.js template.mustache

# Version
mustache --version
```

## Gotchas

- **`{{#section}}` with `0`, `""`, `NaN` skips the block** — these are all falsy in Mustache. To render `0`, use an inverted section or a truthy wrapper.
- **Functions in view are called differently depending on context** — as a variable (`{{fn}}`), the function is called with `this` as the view and its return value is used. As a section (`{{#fn}}`), it must return a function `(text, render) → string` (higher-order section).
- **`{{length}}` inside `{{#length}}` with a string value** — when the section value is a string like `"100 yards"`, `{{length}}` inside resolves to the string itself (not the `.length` property). This is intentional Mustache behavior.
- **Custom tags don't mutate `Mustache.tags`** — passing a 4th argument to `render()` or using `config.tags` is scoped to that call. Only direct assignment `Mustache.tags = [...]` changes the global default.
- **Custom delimiters cannot contain whitespace or `=`** — `<% %>` works, but `<% % =>` does not.
- **Partials are resolved at render time** — not compile time. This means recursive partials are possible (avoid infinite loops).
- **Partial indentation** — if a partial is the first tag on its line, its output is auto-indented to match the partial tag's indentation.
- **`{{.}}` only works inside array iteration** — references the current item when iterating arrays of primitives.
- **`Mustache.escape` handles 8 characters** — `&`, `<`, `>`, `"`, `'`, `/`, `` ` ``, `=`. Override it for non-HTML formats (JSON, XML, plain text).
- **Cache key includes tags** — templates parsed with different delimiters are cached separately. Same template string with different tags = separate cache entries.
- **CLI view files: `.js`/`.cjs` are `require()`d, everything else is JSON** — JS views support functions; JSON views do not.
- **`{{&name}}` and `{{{name}}}` are equivalent** — both render unescaped. The `&` syntax is from original Mustache; triple braces are the modern form.
- **`{{! comment }}` can span multiple lines** — everything until `}}` is stripped, including newlines.
- **Context lookup walks up the parent chain** — if a variable is not found in the current context, Mustache searches parent contexts. This is why partials inherit the calling context.
- **`Mustache.templateCache = undefined` disables caching** — useful for debugging or when templates change dynamically.
- **Numbers are rendered without escaping** — `{{count}}` with value `42` outputs `42` directly, even with HTML escaping enabled.
- **`undefined` and `null` render as empty string** — missing keys produce no output, not `"undefined"`.

## References

- [01-template-syntax](references/01-template-syntax.md) — Variables, dot notation, raw output, comments, set delimiter
- [02-sections](references/02-sections.md) — Section types, falsy values, array iteration, objects as context, higher-order sections
- [03-partials](references/03-partials.md) — Partial resolution, context inheritance, indentation, recursive partials, dynamic partials
- [04-custom-delimiters](references/04-custom-delimiters.md) — Tag customization, inline vs programmatic, cache implications
- [05-programmatic-api](references/05-programmatic-api.md) — Writer, Context, Scanner, cache control, escape override
- [06-cli](references/06-cli.md) — Command-line tool, view formats, partials, stdin, build integration
- [07-module-systems](references/07-module-systems.md) — ESM, CommonJS, AMD, global browser, Deno
- [08-security-and-escaping](references/08-security-and-escaping.md) — HTML escaping, custom escape, XSS considerations, non-HTML formats
