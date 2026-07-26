# block and content

## block

### Signature

```
{{#block "name"}}default content{{/block}}
{{{block "name"}}}
```

### Behavior

`block` defines a named insertion point in a layout. The body between `{{#block}}` and `{{/block}}` is the default content, rendered when no `content` override targets this block.

When content overrides exist, `block` applies them via `reduce` over the actions array, starting with the default content as the initial value.

### Block with Empty Default

```handlebars
{{#block "sidebar"}}{{/block}}
```

An empty block renders nothing unless a page provides content for it.

### Raw vs Escaped Output

Use triple braces for raw HTML from blocks:

```handlebars
{{{block "body"}}}   ! raw HTML
{{#block "body"}}...{{/block}}   ! standard block with default body
```

The `{{#block}}` form is the standard pattern — it provides default content inline. The `{{{block "name"}}}` form is useful in layouts where the block has no default and you want raw output.

## content

### Signature

```
{{#content "blockName"}}override{{/content}}
{{#content "blockName" mode="replace"}}override{{/content}}
{{#content "blockName" mode="append"}}append this{{/content}}
{{#content "blockName" mode="prepend"}}prepend this{{/content}}

! Getter form (subexpression, no body):
{{#if (content "blockName")}}...{{/if}}
```

### Modes

| Mode | Behavior | Result |
|---|---|---|
| `replace` (default) | Replaces default entirely | Only content body renders |
| `append` | Adds after default | `default + content` |
| `prepend` | Adds before default | `content + default` |

### Mode is Case-Insensitive

```handlebars
{{#content "body" mode="Append"}}...{{/content}}
{{#content "body" mode="APPEND"}}...{{/content}}
{{#content "body" mode="append"}}...{{/content}}
```

All three are equivalent. The mode is lowercased internally via `mode.toLowerCase()`.

### Invalid Modes Silently Ignored

```handlebars
{{#content "body" mode="foo"}}...{{/content}}
```

Unknown modes fall through to the `default` case in `applyAction`, which returns the existing value unchanged. The block keeps its default content — no error is thrown.

### Multiple Content Calls for Same Block

You can append or prepend to the same block multiple times:

```handlebars
{{#extend "layout"}}
    {{#content "head" mode="append"}}
        <link rel="stylesheet" href="a.css" />
    {{/content}}

    {{#content "head" mode="append"}}
        <link rel="stylesheet" href="b.css" />
    {{/content}}

    {{#content "head" mode="prepend"}}
        <meta charset="utf-8" />
    {{/content}}
{{/extend}}
```

Actions are applied in order they were queued. The `reduce` processes them sequentially against the default content.

### Setter Always Returns Empty String

When `content` has a body (the setter form), it queues the action and returns `''`:

```handlebars
{{#content "body"}}
    <p>This content</p>
{{/content}}
! The above renders as empty string in the template output.
! The actual content appears when the layout's {{#block "body"}} renders.
```

### Getter Form — Subexpression

When `content` is called without a body (as a subexpression), it acts as a getter:

```handlebars
{{#if (content "sidebar")}}
    <aside class="sidebar">
        {{{block "sidebar"}}}
    </aside>
{{/if}}
```

Returns `true` if any `content` helper has queued an action for that block name, `false` otherwise. This enables conditional layout structures:

```handlebars
{{!-- Layout with optional right column --}}
<div class="grid">
    <div class="col {{#if (content "right")}}2of3{{else}}full{{/if}}">
        {{{block "left"}}}
    </div>
    {{#if (content "right")}}
        <div class="col 1of3">
            {{{block "right"}}}
        </div>
    {{/if}}
</div>
```

### Content in Deep Inheritance

In multi-level inheritance chains, content from each level composes correctly:

```handlebars
! layout.hbs — base
{{#block "header"}}<h1>Default</h1>{{/block}}
{{#block "body"}}<p>Default body</p>{{/block}}

! admin.hbs — extends layout
{{#extend "layout"}}
    {{#content "header" mode="append"}}
        <span class="badge">Admin</span>
    {{/content}}
    {{#content "body"}}
        <div class="admin-panel">{{{block "admin-body"}}}</div>
    {{/content}}
{{/extend}}

! settings.hbs — extends admin
{{#extend "admin"}}
    {{#content "body"}}
        <h2>Settings</h2>
    {{/content}}
{{/extend}}
```

The `applyStack` mechanism ensures each level's overrides are applied in the correct order.

### Content with Block References

Content bodies can reference blocks defined at intermediate levels:

```handlebars
{{#extend "layout-b"}}
    {{#content "bottom" mode="append"}}
        <p>Extra content</p>
        {{{block "b"}}}   ! references a block defined in layout-b
    {{/content}}
{{/extend}}
```

This enables nested block patterns where a child layout defines a new block that grandchildren can fill.
