---
name: handlebars-4-7-9
description: Compile and render Handlebars.js 4.7.9 templates — custom helpers, partials, decorators, precompilation, AST, and runtime options. Use for .hbs/.handlebars template authoring, helper development, build-tool integration, and template debugging
license: MIT
compatibility: Node.js >=0.4.7 (compiler + runtime) or browser (ES3+). Runtime-only builds require precompiled templates
metadata:
  tags:
    - templating
    - javascript
    - html
    - handlebars
    - mustache
---

# handlebars 4.7.9

## Overview

Handlebars.js is a semantic templating language extending Mustache with helpers, block expressions, literal values, partial blocks, and decorators. Version 4.7.9 is the latest 4.x release — compiler revision 8, backward compatible with revision 7 (4.0.0–4.2.x).

Handlebars uses a two-phase model: **compile** (template string → template function) and **render** (template function + context → string). Templates can also be **precompiled** to JavaScript source for runtime-only environments.

### Core API

- `Handlebars.compile(source, options)` — compile a template string at runtime, returns a template function
- `Handlebars.precompile(source, options)` — precompile to JS source string (for build tools)
- `Handlebars.template(spec)` — wrap a precompiled spec into a callable template
- `Handlebars.registerHelper(name, fn)` / `unregisterHelper(name)` — custom helpers
- `Handlebars.registerPartial(name, template)` / `unregisterPartial(name)` — partials
- `Handlebars.registerDecorator(name, fn)` / `unregisterDecorator(name)` — decorators
- `Handlebars.create()` — isolated Handlebars instance with its own helpers/partials/decorators
- `Handlebars.parse(source, options)` — parse template into AST
- `Handlebars.SafeString(str)` — mark a string as safe (skips HTML escaping)
- `Handlebars.escapeExpression(str)` — manually escape HTML entities
- `Handlebars.VERSION` — `"4.7.9"`
- `Handlebars.noConflict()` — restore any overwritten global `Handlebars`
- `Handlebars.logger` — console logger with configurable level (`debug`, `info`, `warn`, `error`)

### Built-in Helpers

| Helper | Type | Description |
|---|---|---|
| `{{#if}}` | block | Conditional rendering. Supports `includeZero` hash arg |
| `{{#unless}}` | block | Inverted `if` — renders block when condition is falsy |
| `{{#each}}` | block | Iterate arrays, objects, and iterables. Exposes `@index`, `@key`, `@first`, `@last`, `@contextPath` |
| `{{#with}}` | block | Shift context. Renders inverse block if context is empty |
| `{{lookup obj field}}` | simple | Dynamic property access on an object |
| `{{#log}}` | block | Log to console. First arg is message(s), `level` hash arg or `@level` data controls severity |
| `{{#*inline "name"}}` | decorator | Define a partial inline from a block, scoped to current template |

### Built-in Internal Helpers (hooks)

- `helperMissing` — called when `{{foo}}` resolves to undefined. Returns `undefined` (renders as empty string). Throw if someone tries to call a missing expression as a function.
- `blockHelperMissing` — called when `{{#foo}}` has no registered helper. Implements Mustache behavior: iterates arrays via `each`, shifts context for objects, conditional for booleans.

## Usage

### Basic compile and render

```js
const Handlebars = require('handlebars');

const source = '<p>Hello, {{name}}! You have {{kids.length}} kids.</p>';
const template = Handlebars.compile(source);
const html = template({ name: 'Alice', kids: [{ name: 'Bob' }, { name: 'Carol' }] });
```

### Custom helpers

Helpers receive positional arguments plus an `options` hash as the last argument. The `options` object contains `fn` (block body), `inverse` (else block), `hash` (named args), `data` (contextual data), and `lookupProperty` (safe property lookup).

```js
Handlebars.registerHelper('upper', function(value) {
  return String(value).toUpperCase();
});

Handlebars.registerHelper('eq', function(a, b, options) {
  return a === b ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('link-to', function(label, url) {
  // Return a SafeString to skip escaping
  return new Handlebars.SafeString(`<a href="${url}">${label}</a>`);
});

// Register multiple at once:
Handlebars.registerHelper({
  upper: function(str) { return str.toUpperCase(); },
  lower: function(str) { return str.toLowerCase(); },
});
```

Template usage:

```handlebars
{{upper name}}
{{#eq status 'active'}}Active{{else}}Inactive{{/eq}}
{{link-to "Home" "/"}}
```

### Block params

Block helpers expose named variables inside the block via `options.fn(context, { blockParams: [values] })`:

```js
Handlebars.registerHelper('pair', function(obj, options) {
  let out = '';
  for (const [key, val] of Object.entries(obj)) {
    out += options.fn({ key, val }, { blockParams: [key, val] });
  }
  return out;
});
```

```handlebars
{{#pair colors as |k v|}}
  <span class="{{k}}">{{v}}</span>
{{/pair}}
```

### Partials

Register partials as compiled templates or strings (compiled lazily):

```js
Handlebars.registerPartial('card', Handlebars.compile('<div class="card">{{title}}</div>'));
Handlebars.registerPartial('card', '<div class="card">{{title}}</div>'); // string, lazy compile
```

```handlebars
{{> card title="Hello"}}
{{> (partialName)}}              ! dynamic partial
{{#> card}}<p>Custom body</p>{{/card}}  ! partial block
```

### Precompilation

```js
const precompiled = Handlebars.precompile(source);
// precompiled is a JavaScript source string
```

Or via CLI:

```bash
handlebars template.hbs -f template-compiled.js
handlebars src/templates/ -f dist/templates.js -m
```

Runtime-only usage:

```js
const Handlebars = require('handlebars.runtime');
require('./template-compiled'); // self-registers
const html = Handlebars.templates['template'](context);
```

### Isolated instances

```js
const hb = Handlebars.create();
hb.registerHelper('secret', function() { return 'classified'; });
const tpl = hb.compile('{{secret}}');
// Global Handlebars namespace is untouched
```

### Compile-time options

```js
Handlebars.compile(source, {
  strict: true,                // throw on undefined variables
  assumeExternal: true,        // skip proto-access checks (trusted data)
  compat: true,                // Mustache compat — recursive lookup (performance cost)
  noEscape: true,              // {{ }} raw; {{{ }}} escaped
  trackIds: true,              // track variable IDs for better errors
  stringParams: true,          // pass string params instead of evaluated values
  knownHelpers: { if: true, each: true },
  knownHelpersOnly: true,      // only allow listed helpers
  preventIndent: true,         // prevent auto-indent of partial output
  explicitPartialContext: true,// require explicit context in partials
  srcName: 'template.hbs',     // source name for error messages
});
```

### Runtime options

```js
template(context, {
  helpers: { custom: helperFn },       // per-call helpers
  partials: { card: cardTpl },         // per-call partials
  data: { level: 2 },                  // custom data for helpers
  allowedProtoProperties: { toString: true },
  allowedProtoMethods: { valueOf: true },
  allowProtoPropertiesByDefault: false,
  allowProtoMethodsByDefault: false,
});
```

### Whitespace control

Use `~` adjacent to `{{` or `}}` to trim surrounding whitespace (including newlines):

```handlebars
{{#each items~}}
  <li>{{this}}</li>
{{~/each}}
```

- `{{~expr}}` — trim left whitespace (including preceding newline)
- `{{expr~}}` — trim right whitespace (including trailing newline)
- `{{~expr~}}` — trim both sides
- `{{~> partial}}` — trim before partial
- `{{#block~}}...{{~/block}}` — trim inside block helpers

Standalone detection: a mustache on its own line (with only whitespace around it) automatically strips the surrounding newline.

### Data variables

Handlebars passes a `@`-prefixed data object into templates:

| Variable | Description |
|---|---|
| `@root` | Root context, accessible from any nesting depth |
| `@key` | Current key in `{{#each}}` (for objects) |
| `@index` | Current index in `{{#each}}` |
| `@first` | True if first iteration |
| `@last` | True if last iteration |
| `@contextPath` | Full path to current context |
| `@partial-block` | Content of a partial block, accessible inside the partial |

```handlebars
{{#each items}}
  <li>{{@index}}: {{this}} (root: {{@root.name}})</li>
{{/each}}
```

### Escaping

- `{{expr}}` — HTML-escaped output (default)
- `{{{expr}}}` — raw, unescaped output
- `{{&expr}}` — raw output (legacy Mustache syntax, still supported)
- With `noEscape: true`, behavior is reversed: `{{ }}` raw, `{{{ }}}` escaped

Escaped characters: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#x27;`, `` ` `` → `&#x60;`, `=` → `&#x3D;`

## Gotchas

- **`{{#if}}` treats empty arrays as falsy** — `{{#if items}}` with `[]` renders the inverse block. Use `{{#if items.length}}` to check for non-empty.
- **`{{#each}}` on empty collections renders inverse** — provide `{{else}}` to handle empty cases. Object iteration order is not guaranteed.
- **Helper wins over context function** — when a context property is a function and a helper with the same name exists, the helper always wins. In block context, a context function triggers `blockHelperMissing`, not direct invocation.
- **Proto-access protection is on by default** — `__proto__`, `constructor`, and other prototype properties are blocked. Use `assumeExternal: true` or `allowedProtoProperties`/`allowedProtoMethods` runtime options.
- **Precompiled templates must match compiler revision** — rev 8 (4.3.0+) templates require rev 8 runtime. Rev 8 runtime is backward compatible with rev 7 (4.0.0–4.2.x) templates.
- **`{{#with}}` skips empty contexts** — does not render the block if context is `null`, `undefined`, or empty. Use `{{#if}}` for truthiness checks without context shift.
- **`{{> partial}}` hash args merge into context** — `{{> card name="X"}}` makes `name` available inside the partial, overriding existing values.
- **`{{lookup}}` is the only dynamic property access** — `{{obj.[field]}}` is not valid Handlebars. Use `{{lookup obj field}}`.
- **`Handlebars.create()` includes the compiler** — for runtime-only, use `handlebars.runtime` which lacks `compile`/`precompile`.
- **`SafeString` bypasses all escaping** — never construct SafeStrings from unsanitized user input.
- **`{{#log}}` returns empty string** — side-effect helper only, never contributes output.
- **`@inline` decorator scope** — partials defined with `{{#*inline}}` are scoped to the template they're defined in, not globally registered.
- **`strict: true` throws on undefined** — without strict mode, undefined variables render as empty string.
- **`compat: true` has performance cost** — enables recursive depth lookup. Prefer explicit `@root` or `../` references.
- **`{{~ }}` is whitespace trimming, not raw output** — use `{{{ }}}` or `{{& }}` for raw output. The `~` marker only affects surrounding whitespace.
- **`{{#unless}}` is syntactic sugar for inverted `{{#if}}`** — it swaps `fn` and `inverse` internally.
- **CLI outputs CommonJS by default** — use `-a` for AMD, `-c <path>` for CommonJS with custom module path.

## References

- [01-path-expressions](references/01-path-expressions.md) — Path syntax, depth references, literals, subexpressions, data variables
- [02-helper-api](references/02-helper-api.md) — Helper signature, options object, block params, fn/inverse, hash args, iteration
- [03-partials](references/03-partials.md) — Registration, dynamic partials, partial blocks, inline decorator, indentation
- [04-precompilation](references/04-precompilation.md) — CLI usage, programmatic precompilation, build tools, runtime-only mode
- [05-security](references/05-security.md) — Proto-access control, strict mode, escapeExpression, SafeString, XSS prevention
- [06-compile-options](references/06-compile-options.md) — Full compile-time and runtime options reference
- [07-ast-and-visitor](references/07-ast-and-visitor.md) — AST node types, Visitor pattern, parse API, programmatic template transformation
- [08-typescript](references/08-typescript.md) — TypeScript type definitions, CompileOptions, RuntimeOptions, HelperOptions, AST types
