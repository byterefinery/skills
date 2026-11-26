# Path Expressions

## Simple paths

Property lookup on the current context, with depth resolution:

```handlebars
{{name}}
{{user.name}}
{{user.address.city}}
```

Handlebars resolves these by walking the context stack. If `name` is not found in the current context, it checks parent contexts (depth lookup).

## Depth references

Reference parent contexts with `..`:

```handlebars
{{../name}}        ! one level up
{{../../name}}     ! two levels up
{{../../..}}       ! three levels up, returns the context object itself
```

## Current context

Use `.` to reference the current context object explicitly:

```handlebars
{{.}}              ! entire current context (useful in #each)
{{./name}}         ! same as {{name}} but explicit
```

## Root context

`@root` always refers to the root context passed to the template, regardless of nesting:

```handlebars
{{#each items}}
  {{this}} by {{@root.author}}
{{/each}}
```

## Literal values

Handlebars supports several literal types directly in templates:

```handlebars
{{"first name"}}   ! string literal — property named "first name"
{{1}}              ! number literal
{{true}}           ! boolean literal
{{false}}          ! boolean literal
{{null}}           ! null literal
{{undefined}}      ! undefined literal
```

String literal segments for property access:

```handlebars
{{."first name"}}   ! access "first name" property on current context
{{user."first name"}}
```

## Subexpressions

Nest expressions inside other expressions using parentheses. Evaluated innermost-first:

```handlebars
{{link (upper name) "/"}}
{{#each (sort items "name")}}
  {{this}}
{{/each}}
{{> partial (compute-arg x y)}}
```

## Data variables

Access Handlebars' internal data with `@` prefix:

```handlebars
@root         ! root context
@key          ! current key (in #each over objects)
@index        ! current index (in #each)
@first        ! true if first iteration
@last         ! true if last iteration
@contextPath  ! full context path string
@level        ! log level (set via runtime options or #log)
@partial-block ! content of a partial block (accessible inside the partial)
```

## Escaping

- `{{expr}}` — HTML-escaped (default)
- `{{{expr}}}` — raw, unescaped
- `{{&expr}}` — raw (legacy Mustache syntax)
- With `noEscape: true`, behavior reverses: `{{ }}` raw, `{{{ }}}` escaped

## Whitespace control

`~` trims surrounding whitespace including newlines:

```handlebars
{{~expr}}      ! trim left
{{expr~}}      ! trim right
{{~expr~}}     ! trim both
{{~> partial}} ! trim before partial
```

This is **not** related to escaping — `~` only affects whitespace.

## Strict mode

With `strict: true`, undefined paths throw `Handlebars.Exception` with line/column info:

```js
const tpl = Handlebars.compile('{{unknown}}', { strict: true });
tpl({ name: 'Alice' }); // throws: '"unknown" not defined in ...'
```

Without strict mode, undefined paths render as empty string.

## Path classification

Handlebars classifies paths into three categories at compile time:

- **Simple** — single-part, not `this`, not `..`, no depth. Resolved directly from context.
- **Helper** — expression has params or hash, or is a known helper name. Always invokes the helper.
- **Ambiguous** — could be a helper or context property. Resolved at runtime: helper wins if registered, otherwise context lookup.

```handlebars
{{name}}           ! simple (or ambiguous if helper "name" exists)
{{helper}}         ! ambiguous
{{helper arg}}     ! helper (has params)
{{#if x}}          ! helper (known built-in)
{{this.name}}      ! simple (scoped)
{{../name}}        ! simple (depth)
```

Use `knownHelpers` and `knownHelpersOnly` to resolve ambiguity at compile time:

```js
Handlebars.compile(source, {
  knownHelpers: { myHelper: true },
  knownHelpersOnly: true,  ! throw on unknown helpers
});
```

## Lambda resolution

When a context property is a function and accessed as a simple expression (no params, no hash), Handlebars calls `container.lambda()` which invokes the function with the current context:

```js
const context = {
  greet: function() { return 'Hello, ' + this.name; },
  name: 'World'
};
```

```handlebars
{{greet}}  ! calls greet() with context, returns "Hello, World"
```

This is the Mustache-compatible behavior. If the expression has params or hash, it's treated as a helper call instead.
