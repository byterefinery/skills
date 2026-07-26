# Compile Options

## Compile-time options

Passed to `Handlebars.compile(source, options)` or `Handlebars.precompile(source, options)`:

### strict

**Type:** `boolean` — **Default:** `false`

Throw `Handlebars.Exception` when a variable is not defined in context. Uses `container.strict()` which checks property existence before access. Without strict mode, undefined variables render as empty string.

```js
Handlebars.compile('{{name}}', { strict: true });
```

### assumeExternal

**Type:** `boolean` — **Default:** `false`

Skip runtime prototype-access checks. Use only when all context data is fully trusted. Eliminates proto-access overhead entirely.

```js
Handlebars.compile(source, { assumeExternal: true });
```

### compat

**Type:** `boolean` — **Default:** `false`

Enable Mustache compatibility mode — recursive depth lookup via `depthedLookup()`. Has a measurable performance cost. Sets `useDepths: true` internally. Prefer explicit `@root` or `../` references instead.

```js
Handlebars.compile(source, { compat: true });
```

### noEscape

**Type:** `boolean` — **Default:** `false`

Reverse escaping: `{{ }}` outputs raw, `{{{ }}}` escapes.

```js
Handlebars.compile(source, { noEscape: true });
```

### trackIds

**Type:** `boolean` — **Default:** `false`

Track variable IDs through compilation. Pushes ID strings alongside evaluated values onto the compile stack. Enables better error messages and debugging.

```js
Handlebars.compile(source, { trackIds: true });
```

### stringParams

**Type:** `boolean` — **Default:** `false`

Pass string representations of params to helpers instead of evaluated values. Subexpressions are still evaluated and passed in. Useful for reflection/debugging.

```js
Handlebars.compile(source, { stringParams: true });
```

### knownHelpers

**Type:** `object` — **Default:** built-in helpers only

Map of helper names that are known to exist. Resolves ambiguity at compile time — known helpers always invoke the helper, context properties are never tried. Built-in helpers (`if`, `unless`, `each`, `with`, `log`, `lookup`, `helperMissing`, `blockHelperMissing`) are always included automatically.

```js
Handlebars.compile(source, {
  knownHelpers: {
    if: true,
    each: true,
    myHelper: true,
  },
});
```

### knownHelpersOnly

**Type:** `boolean` — **Default:** `false`

Throw on unknown helpers at compile time. Must be used with `knownHelpers`.

```js
Handlebars.compile(source, {
  knownHelpers: { myHelper: true },
  knownHelpersOnly: true,
});
```

### preventIndent

**Type:** `boolean` — **Default:** `false`

Disable automatic indentation of partial output.

```js
Handlebars.compile(source, { preventIndent: true });
```

### explicitPartialContext

**Type:** `boolean` — **Default:** `false`

Require explicit context in partial invocations. Without this, `{{> partial}}` passes current context implicitly (via a synthetic `PathExpression` with depth 0 and empty parts).

```js
Handlebars.compile(source, { explicitPartialContext: true });
```

### srcName

**Type:** `string` — **Default:** `undefined`

Source file name used in error messages and stack traces. Also passed to `CodeGen` for source map generation.

```js
Handlebars.compile(source, { srcName: 'template.hbs' });
```

### ignoreStandalone

**Type:** `boolean` — **Default:** `false`

Ignore standalone detection for whitespace control. Standalone mustaches (on their own line) normally strip the surrounding newline.

```js
Handlebars.compile(source, { ignoreStandalone: true });
```

### data

**Type:** `boolean` — **Default:** `true`

Include data variables (`@root`, `@index`, etc.) in compiled templates. Enabled by default.

## Runtime options

Passed when calling a compiled template: `template(context, options)`:

### helpers

**Type:** `object` — **Default:** global helpers

Per-call helper overrides. Merged with global helpers; per-call takes precedence. Helpers are wrapped to inject `lookupProperty`.

```js
template(context, {
  helpers: {
    upper: function(str) { return str.toUpperCase(); },
  },
});
```

### partials

**Type:** `object` — **Default:** global partials

Per-call partial overrides. Merged with global partials via `container.mergeIfNeeded()`; per-call takes precedence.

```js
template(context, {
  partials: {
    card: Handlebars.compile('<div>{{title}}</div>'),
  },
});
```

### decorators

**Type:** `object` — **Default:** global decorators

Per-call decorator overrides. Merged with global decorators.

### data

**Type:** `object` — **Default:** `{ root: context }`

Custom data passed to helpers via `options.data`. Merged with Handlebars' internal data via `createFrame()`.

```js
template(context, {
  data: { level: 2, customFlag: true },
});
```

### depths

**Type:** `array` — **Default:** `[context]`

Additional depth contexts for `../` lookups. Used internally for nested template invocation.

### partial

**Type:** `boolean` — **Default:** `false`

Internal flag indicating the template is being invoked as a partial.

### allowCallsToHelperMissing

**Type:** `boolean` — **Default:** `false`

Keep `helperMissing` and `blockHelperMissing` in the helpers object instead of moving them to `container.hooks`. Used for backward compatibility with compiler rev 7 templates.

### Proto-access runtime options

```js
template(context, {
  ! Whitelist specific prototype properties
  allowedProtoProperties: {
    toString: true,
    valueOf: true,
  },

  ! Whitelist specific prototype methods
  allowedProtoMethods: {
    valueOf: true,
  },

  ! Allow all prototype properties by default (except explicit denies)
  allowProtoPropertiesByDefault: false,

  ! Allow all prototype methods by default (except explicit denies)
  allowProtoMethodsByDefault: false,
});
```

## Parser options

Passed to `Handlebars.parse(source, options)`:

### srcName

**Type:** `string`

Source name for error messages. Used by `SourceLocation` constructor.

### ignoreStandalone

**Type:** `boolean`

Skip standalone line detection during whitespace control pass.

## Internal compile options

These are set internally and not meant for direct use:

- `useDepths` — whether the template uses depth contexts
- `useBlockParams` — whether the template uses block params
- `usePartial` — whether the template invokes partials
- `useData` — whether the template uses data variables
- `useDecorators` — whether the template uses decorators

## Version compatibility

| Option | Introduced |
|---|---|
| `strict` | 1.0.0 |
| `data` | 2.0.0 |
| `compat` | 2.0.0 |
| `knownHelpers` / `knownHelpersOnly` | 3.0.0 |
| `trackIds` | 4.0.0 |
| `stringParams` | 4.0.0 |
| `assumeExternal` | 4.0.0 |
| `preventIndent` | 4.0.0 |
| `explicitPartialContext` | 4.0.0 |
| Proto-access options | 4.0.0 |
| `noEscape` | 1.0.0 |

Compiler revision 8 (4.3.0+) is backward compatible with revision 7 (4.0.0–4.2.x). Precompiled templates from rev 8 require runtime rev 8.
