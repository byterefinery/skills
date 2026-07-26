---
name: handlebars-layouts-3-1-4
description: Handlebars helpers implementing layout blocks (extend, embed, block, content) similar to Jade, Jinja, Nunjucks, Swig, and Twig. Use when building Handlebars templates with layout inheritance, content slots, multi-page template hierarchies, or nested component layouts.
license: MIT
compatibility: Node.js >= 0.10 and Handlebars 3.x+. No runtime dependencies beyond Handlebars itself
metadata:
  tags:
    - templating
    - handlebars
    - layouts
    - inheritance
---

# handlebars-layouts 3.1.4

## Overview

Four Handlebars helpers — `extend`, `embed`, `block`, `content` — that implement template layout inheritance. A layout partial defines named blocks with default content. Page templates extend the layout and override blocks via `content` helpers, supporting `replace` (default), `append`, and `prepend` modes.

The mental model is class inheritance: `extend` is `extends`, `embed` is `new`, `block` defines a method with a default body, `content` overrides it.

The library uses two internal context properties — `$$layoutStack` (queued override functions from `extend` bodies) and `$$layoutActions` (named content actions with mode) — to resolve block content at render time. `embed` resets both, creating an isolated scope.

Installation: `npm install handlebars-layouts` (zero dependencies beyond Handlebars).

## Usage

### Registration

Two equivalent approaches:

```js
const handlebars = require('handlebars');
const layouts = require('handlebars-layouts');

// Option A: generate helpers object, register manually
handlebars.registerHelper(layouts(handlebars));

// Option B: one-call registration (recommended)
layouts.register(handlebars);
```

For isolated Handlebars instances (e.g., per-tenant templates):

```js
const hb = handlebars.create();
layouts.register(hb);
```

### Registering Layout Partials

Layouts must be registered as partials before page templates are compiled:

```js
const fs = require('fs');

// Single partial
handlebars.registerPartial('layout', fs.readFileSync('views/layout.hbs', 'utf8'));

// Batch registration
handlebars.registerPartial({
  layout: fs.readFileSync('views/layout.hbs', 'utf8'),
  admin: fs.readFileSync('views/admin.hbs', 'utf8'),
  modal: fs.readFileSync('views/modal.hbs', 'utf8'),
});
```

String partials are compiled lazily on first use via `handlebars.compile()`.

### The Four Helpers

**`{{#block "name"}}...{{/block}}`** — Define a named slot in a layout. The body is default content, rendered when no `content` override targets it.

**`{{#extend "layout"}}...{{/extend}}`** — Load a layout partial and define `content` overrides inside. Hash attributes (`key=value`) are merged into the template context.

**`{{#embed "partial"}}...{{/embed}}`** — Like `extend` but resets internal state, creating an isolated scope. Use for components that define their own blocks (modals, cards, media objects).

**`{{#content "name" mode="replace"}}...{{/content}}`** — Override a block. Modes: `replace` (default, full override), `append` (add after default), `prepend` (add before default). Also usable as subexpression `(content "name")` for conditional checks.

### Typical Layout + Page

Layout (`layout.hbs`):

```handlebars
<!doctype html>
<html>
<head>
    {{#block "head"}}<title>{{title}}</title>{{/block}}
</head>
<body>
    {{#block "body"}}<h2>Default content</h2>{{/block}}
    {{#block "foot"}}{{/block}}
</body>
</html>
```

Page (`page.hbs`):

```handlebars
{{#extend "layout"}}
    {{#content "head" mode="append"}}
        <link rel="stylesheet" href="page.css" />
    {{/content}}

    {{#content "body"}}
        <h2>Welcome</h2>
    {{/content}}

    {{#content "foot" mode="prepend"}}
        <script src="analytics.js"></script>
    {{/content}}
{{/extend}}
```

### Conditional Blocks

Use the subexpression form `(content "name")` to check whether content was provided:

```handlebars
{{#if (content "sidebar")}}
    <aside>{{{block "sidebar"}}}</aside>
{{/if}}
```

Returns boolean — true if any `content` helper targeted that block name.

### Nested Embeds

For partials that define their own blocks, `embed` isolates the scope:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#embed "modal" title="Settings"}}
            {{#content "body"}}
                <p>Modal content</p>
            {{/content}}
        {{/embed}}
    {{/content}}
{{/extend}}
```

### Express Integration

```js
const express = require('express');
const consolidate = require('consolidate');
const handlebars = require('handlebars');
const layouts = require('handlebars-layouts');

layouts.register(handlebars);
handlebars.registerPartial('layout', fs.readFileSync('views/layout.hbs', 'utf8'));

const app = express();
app.set('views', './views');
app.set('view engine', 'html');
app.engine('html', consolidate.handlebars);

app.get('/', (req, res) => res.render('index', { title: 'Home' }));
```

## Gotchas

- **Partials must be registered before compilation** — `{{#extend "layout"}}` looks up `handlebars.partials[name]`. Missing partials throw `Missing partial: 'layout'`. Register all layout partials before compiling page templates.
- **`content` as setter always returns empty string** — the setter form queues an action and returns `''`. Only the getter form `(content "name")` returns a boolean.
- **`mode` is case-insensitive, invalid modes silently ignored** — `mode="Append"`, `mode="APPEND"` work. Unknown modes like `mode="foo"` keep the block's default content (no error).
- **`embed` resets `$$layoutStack` and `$$layoutActions`** — block actions inside an `embed` are scoped to that partial. Block names inside `embed` do not conflict with the parent page's layout.
- **`extend` merges context from three sources** — current context (`this`), optional custom context object, and hash attributes. Later sources override earlier ones: `hash` > `customContext` > `this`.
- **`applyStack` runs before every `block` and `content`** — the internal stack of override functions is consumed eagerly. In deep inheritance chains, each level's content overrides apply in order.
- **No `$$` prefix in template variables** — `$$layoutStack` and `$$layoutActions` are internal. Naming template data with `$$` risks collisions.
- **Deep inheritance chains are supported** — layouts can extend other layouts (e.g., `deep-c` extends `deep-b` extends `deep-a`). Content modes compose across levels with correct ordering.
- **`{{{block "name"}}}` vs `{{#block "name"}}`** — use triple-brace `{{{block "name"}}}` for raw HTML output from blocks. The block helper `{{#block}}` is the standard form with body as default.
- **String partials are compiled on first use** — if a registered partial is a string, it is compiled via `handlebars.compile()` automatically. In production, pre-compile partials to avoid repeated compilation.
- **`embed` accepts custom context and hash like `extend`** — `{{#embed "user" name showBanner=true}}` merges `name` and `showBanner` into the embedded partial's context.

## References

- [01-extend-and-embed](references/01-extend-and-embed.md) — extend/embed signatures, context merging, custom context objects, hash attributes, partial resolution
- [02-block-and-content](references/02-block-and-content.md) — block definitions, content modes (replace/append/prepend), conditional blocks, subexpression getter, multiple content calls
- [03-deep-inheritance](references/03-deep-inheritance.md) — multi-level layout chains, stack and action ordering, nested blocks within content, cross-level block references
- [04-embed-isolation](references/04-embed-isolation.md) — context reset mechanics, nested embeds, block scoping, embed inside loops, hash context in embeds
- [05-express-integration](references/05-express-integration.md) — Express setup with consolidate, partial registration patterns, per-route layouts, error handling
- [06-browser-usage](references/06-browser-usage.md) — UMD dist bundle, AMD modules, global variable, Bower installation, precompiled template workflows
- [07-common-patterns](references/07-common-patterns.md) — grid layouts, media objects, component partials, admin layouts, conditional sections, multi-column patterns
