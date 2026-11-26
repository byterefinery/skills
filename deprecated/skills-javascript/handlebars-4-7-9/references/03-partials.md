# Partials

## Registration

Register partials as compiled templates or raw strings:

```js
! As a compiled template (recommended):
Handlebars.registerPartial('card', Handlebars.compile('<div>{{title}}</div>'));

! As a string (compiled lazily on first use):
Handlebars.registerPartial('card', '<div>{{title}}</div>');

! Multiple at once:
Handlebars.registerPartial({
  card: '<div>{{title}}</div>',
  header: '<header>{{title}}</header>',
});

Handlebars.unregisterPartial('card');
```

## Basic usage

Invoke partials with `{{> name}}`:

```handlebars
{{> card}}
```

The partial receives the current context. Pass a different context explicitly:

```handlebars
{{> card user}}
```

## Hash arguments merge into context

Hash args on partial invocations are merged into the partial's context:

```handlebars
{{> card title="Override" size="large"}}
```

Inside `card.hbs`, both `title` and `size` are available as context properties, overriding any existing values. This is implemented via `Utils.extend({}, context, options.hash)` in `invokePartialWrapper`.

## Dynamic partials

Resolve partial names at runtime:

```handlebars
{{> (componentName)}}
{{> (lookup components name)}}
```

The expression inside parentheses must evaluate to a string (partial name) or a compiled template function. If it returns a string, Handlebars looks it up in the partials registry.

## Partial blocks

Pass a block as a fallback or wrapper for a partial:

```handlebars
{{#> card}}
  <p>Custom card body</p>
{{/card}}
```

If the partial `card` exists, the block content is available inside the partial via `@partial-block`. If the partial doesn't exist, the block renders as a fallback.

Inside the partial template:

```handlebars
<div class="card">
  {{@partial-block}}
</div>
```

The `@partial-block` data variable is set via a wrapper function that captures the current partial block from the closure. Nested partial blocks restore the outer `@partial-block` from the enclosing scope.

## Inline partials

Define partials locally using the `@inline` decorator:

```handlebars
{{#*inline "item"}}
  <li>{{this}}</li>
{{/inline}}

{{#each items}}
  {{> item}}
{{/each}}
```

Inline partials are scoped to the template they're defined in — they don't pollute the global partial registry. Internally, the `@inline` decorator stores the block function in `props.partials[name]` and wraps the template to merge those partials into the container at execution time.

## Partial indentation

Handlebars auto-indents partial output to match the indentation of the `{{> partial}}` call:

```handlebars
<ul>
{{#each items}}
    {{> item}}
{{/each}}
</ul>
```

Each line of the partial output is indented by the same whitespace preceding `{{> item}}`. The indent is extracted via regex `/([ \t]+$)/` from the preceding content line during standalone detection.

Disable with `preventIndent: true` compile option.

## Per-call partials

Pass partials at render time via runtime options:

```js
const cardTpl = Handlebars.compile('<div>{{title}}</div>');
const html = template(context, {
  partials: {
    card: cardTpl,
  },
});
```

Per-call partials are merged with globally registered partials, with per-call taking precedence. The merge uses `container.mergeIfNeeded()` to avoid redundant merges.

## Partial resolution order

1. Explicit partial (first positional arg to `{{> }}`)
2. `@partial-block` (for partial blocks without explicit partial)
3. Per-call partials (from runtime options)
4. Globally registered partials
5. Lazy compilation (if a string was registered and the compiler is available)

## Nested partials

Partials can invoke other partials. The partial registry is shared, so any registered partial is accessible from within another partial.

With `@inline`, inline partials create a new scope frame — they don't leak to sibling templates but are visible to partials invoked from within the same template.

## Runtime partial compilation

In full Handlebars (not runtime-only), partials registered as strings are compiled on first use:

```js
Handlebars.registerPartial('card', '<div>{{title}}</div>');
! Compiled lazily when first invoked
```

In runtime-only mode (`handlebars.runtime`), string partials cannot be compiled. All partials must be precompiled or passed as compiled functions.

## Standalone partials

When a partial invocation is on its own line (standalone), the surrounding newline is automatically stripped. The partial's indent is preserved for auto-indentation of its output lines.

Use `ignoreStandalone: true` compile option to disable this behavior.
