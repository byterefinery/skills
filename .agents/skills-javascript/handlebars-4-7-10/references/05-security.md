# Security

## HTML escaping

Handlebars automatically escapes HTML special characters in `{{ }}` expressions:

| Character | Entity |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |
| `` ` `` | `&#x60;` |
| `=` | `&#x3D;` |

The `=` character is escaped to prevent XSS via `onload` attributes in SVG/mathML.

Use `{{{ }}}` (triple stash) or `{{& }}` to output raw, unescaped content.

## SafeString

Mark a string as already safe to skip escaping:

```js
new Handlebars.SafeString('<b>bold</b>');
```

`SafeString` instances pass through `escapeExpression` unchanged via their `toHTML()` method. **Never** construct SafeStrings from unsanitized user input.

```js
! DANGEROUS — XSS vulnerability
Handlebars.registerHelper('userHtml', function(input) {
  return new Handlebars.SafeString(input);
});

! SAFE — sanitize first
const DOMPurify = require('dompurify');
Handlebars.registerHelper('safeHtml', function(input) {
  return new Handlebars.SafeString(DOMPurify.sanitize(input));
});
```

`SafeString` stores the string in a `string` property and exposes `toString()` and `toHTML()` that both return it.

## Prototype pollution protection

Handlebars blocks access to prototype properties by default. The proto-access control system has two layers, managed by `createProtoAccessControl()`:

### Property whitelist

By default, `__proto__` is blocked (set to `false` in the whitelist). Other prototype properties encountered during template rendering are also blocked unless explicitly whitelisted:

```js
const html = template(context, {
  allowedProtoProperties: {
    toString: true,
    valueOf: true,
  },
  allowProtoPropertiesByDefault: false, ! default: false
});
```

### Method whitelist

Dangerous prototype methods are blocked by default:

- `constructor`
- `__defineGetter__`
- `__defineSetter__`
- `__lookupGetter__`
- `__lookupSetter__`

```js
const html = template(context, {
  allowedProtoMethods: {
    valueOf: true,
  },
  allowProtoMethodsByDefault: false, ! default: false
});
```

### How it works

`container.lookupProperty()` checks whether a property is an own property of the parent. If not, it passes the result through `resultIsAllowed()` which checks the whitelist. If the property is not in the whitelist and `defaultValue` is false, access is denied.

A one-time warning is logged (via `logger.log('error', ...)`) for each unique denied property name. The set of logged properties can be reset via `Handlebars.resetLoggedPropertyAccesses()` (deprecated, for testing only).

### assumeExternal option

When you trust all context data (e.g., from your own server), skip proto-access checks entirely:

```js
const tpl = Handlebars.compile(source, { assumeExternal: true });
```

This removes all proto-access overhead. Only use when context data is fully trusted.

## Strict mode

Enable `strict: true` to throw on undefined variable access:

```js
const tpl = Handlebars.compile('{{unknown}}', { strict: true });
tpl({ name: 'Alice' });
! Handlebars.Exception: "unknown" not defined in [object Object] - 1:1
```

This catches typos and missing data at render time. The exception includes `lineNumber`, `column`, `endLineNumber`, and `endColumn` properties.

In strict mode, the compiled template uses `container.strict()` which throws if the property is not found on the object.

## noEscape option

Reverse the default escaping behavior:

```js
const tpl = Handlebars.compile(source, { noEscape: true });
! {{ }} → raw output
! {{{ }}} → escaped output
```

Useful when templates primarily output raw HTML and escaping is the exception.

## Context data trust levels

| Scenario | Recommended settings |
|---|---|
| Fully trusted data (internal APIs) | `assumeExternal: true` |
| Mixed trust (some user input) | Default proto-access + `strict: true` |
| Untrusted data (user templates) | Default proto-access + `strict: true` + sanitize all inputs |
| Legacy Mustache templates | `compat: true` (accept performance cost) |

## Logging security warnings

Handlebars logs to console when proto-access is denied for non-whitelisted properties. The warning is logged once per property name. Override the logger:

```js
Handlebars.logger.level = 'debug';  ! show all logs
Handlebars.logger.level = 'error';  ! only errors
Handlebars.logger.level = 3;        ! numeric: 0=debug, 1=info, 2=warn, 3=error
```

The logger uses `console.debug`, `console.info`, `console.warn`, `console.error` mapped by level. If a console method doesn't exist, it falls back to `console.log`.

## Sandboxed instances

Use `Handlebars.create()` for isolated template environments:

```js
const hb = Handlebars.create();
! No shared helpers, partials, or decorators with global Handlebars
hb.registerHelper('safe', function(val) { return String(val); });
const tpl = hb.compile('{{safe user_input}}');
```

Each instance maintains its own helper/partial/decorator registry, preventing cross-contamination.

## AST validation (4.7.10)

`Handlebars.compile()` and `Handlebars.precompile()` accept a template string **or** a pre-parsed AST. Because compilation turns an AST into JavaScript, treat it like code: only pass ASTs your application built itself. Never pass an AST that comes from untrusted input (e.g. JSON from a request body or user-writable storage) — the compiler hardens the values it writes into generated code, but that is defense in depth, not a guarantee. Store template source, not ASTs, for caching or transfer.

In 4.7.10 the AST value validation moved to the **compiler boundary** (`Compiler`), where it matters — the values are written into generated code there. Validation failures throw `Handlebars.Exception` with the message `Invalid AST: <node.type> <what-is-wrong>`:

- `PathExpression.depth` — a missing depth is treated as `0`; a present depth must be a non-negative integer
- `PathExpression.parts` — must be an array containing only strings
- `Program.blockParams` — when present, must be an array of strings
- `StringLiteral.value` — must be a string
- `NumberLiteral.value` — must be a number (need not be finite: `Infinity`/`NaN` are emitted as the read-only globals of the same name)
- `BooleanLiteral.value` — must be a boolean

Dispatch is locked down too: `Compiler#accept` and `Visitor#accept` only dispatch on the node types produced by the parser (or, for `Visitor`, types a subclass defines handlers for). Any other `type` — including ones colliding with object methods such as `accept`, `constructor`, or `__proto__` — throws `Unknown type` instead of invoking an arbitrary method.

## Precompiled output hardening (4.7.10)

- Names and strings written into generated JS use `safeJsonLiteral`, which escapes sequences that could end or change the parsing of an enclosing `<script>` element (e.g. `<!--`, `<script`) — GHSA-xw65-4hp5-5hc7.
- `//# sourceMappingURL=` URLs are sanitized: line terminators stripped, `<` percent-encoded as `%3C`.
- Lazy partial compilation accepts only string partials; function partials must return a string.
- Context data is not trusted for special properties: prototype-access control blocks `__proto__`/`constructor`-style lookups, and `isPrototypeConstructor` catches the `Function.prototype.constructor` self-back-reference that would otherwise bypass the checks.

See [04-precompilation](04-precompilation.md) for the CLI/`-m`/`-map` details.

## noConflict

Restore a previously overwritten global `Handlebars`:

```js
const hb = Handlebars.noConflict();
! Restores any saved global Handlebars reference
```

This is useful when loading Handlebars in environments where the global namespace may be shared.
