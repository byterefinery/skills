# Deep Inheritance

## Overview

handlebars-layouts supports multi-level layout inheritance chains. A layout can extend another layout, which extends another, and so on. Content modes compose across levels with deterministic ordering.

## Internal Mechanism

Two data structures drive deep inheritance:

### $$layoutStack

An array of functions. Each `{{#extend}}` pushes its body (the `content` helpers inside) onto the stack. When `{{#block}}` or `{{#content}}` runs in the layout, `applyStack` shifts functions from the stack and executes them, which queues `content` actions.

### $$layoutActions

An object mapping block names to arrays of action objects. Each action has `{ mode, fn, options }`. When `{{#block "name"}}` renders, it reduces over the actions array, applying each mode against the running value starting from the default content.

## Three-Level Chain Example

### deep-a.hbs (root layout)

```handlebars
<!doctype>
<html>
<body>
    {{#block "top"}}<p>a1</p>{{/block}}
    {{#block "middle"}}<p>a2</p>{{/block}}
    {{#block "bottom"}}<p>a3</p>{{/block}}
</body>
</html>
```

### deep-b.hbs (extends deep-a)

```handlebars
{{#extend "deep-a"}}
    {{#content "top" mode="prepend"}}<p>b1</p>{{/content}}
    {{#content "top" mode="prepend"}}<p>b1.1</p>{{/content}}
    {{#content "middle"}}<p>b2</p>{{/content}}
    {{#content "bottom" mode="append"}}
        <p>b3</p>
        {{{block "b"}}}
    {{/content}}
{{/extend}}
```

### deep-c.hbs (extends deep-b)

```handlebars
{{#extend "deep-b"}}
    {{#content "top" mode="prepend"}}<p>c1</p>{{/content}}
    {{#content "top" mode="prepend"}}<p>c1.1</p>{{/content}}
    {{#content "middle"}}<p>c2</p>{{/content}}
    {{#content "bottom" mode="append"}}
        <p>c3</p>
        {{{block "c"}}}
    {{/content}}
    {{#content "b" mode="append"}}<p>c4</p>{{/content}}
{{/extend}}
```

### page.hbs (extends deep-c)

```handlebars
{{#extend "deep-c"}}
    {{#content "top" mode="prepend"}}<p>d1</p>{{/content}}
    {{#content "top" mode="prepend"}}<p>d1.1</p>{{/content}}
    {{#content "middle"}}<p>d2</p>{{/content}}
    {{#content "bottom" mode="append"}}<p>d3</p>{{/content}}
    {{#content "b" mode="append"}}<p>d4</p>{{/content}}
    {{#content "c" mode="append"}}<p>d5</p>{{/content}}
{{/extend}}
```

### Result

```html
<!doctype>
<html>
<body>
    <p>d1.1</p>
    <p>d1</p>
    <p>c1.1</p>
    <p>c1</p>
    <p>b1.1</p>
    <p>b1</p>
    <p>a1</p>

    <p>d2</p>

    <p>a3</p>
    <p>b3</p>
    <p>c4</p>
    <p>d4</p>
    <p>c3</p>
    <p>d5</p>
    <p>d3</p>
</body>
</html>
```

### Ordering Rules

- **prepend**: deepest level first, working outward. `d1.1` (deepest) appears before `d1`, which appears before `c1.1`, etc. The base content (`a1`) is last.
- **replace**: the deepest level's replace wins. `d2` replaces `c2`, which replaced `b2`, which replaced `a2`.
- **append**: base content first, then each level in order from shallowest to deepest. `a3` (base) → `b3` → `c3` → `d3`.
- **cross-level blocks**: `{{{block "b"}}}` in deep-b is filled by `{{#content "b"}}` from deep-c and page. Actions compose via `reduce`.

## Nested Blocks Within Content

A layout level can define new blocks inside its `content` overrides, which child levels can then fill:

```handlebars
! layout-b defines block "b" inside its content for "bottom"
{{#content "bottom" mode="append"}}
    <p>b3</p>
    {{{block "b"}}}
{{/content}}

! layout-c fills block "b"
{{#content "b" mode="append"}}<p>c4</p>{{/content}}

! page fills block "b" further
{{#content "b" mode="append"}}<p>d4</p>{{/content}}
```

This pattern enables progressive layout refinement — each level adds structure that deeper levels can populate.

## applyStack Timing

`applyStack` is called before every `block` and `content` helper execution. It shifts functions from `$$layoutStack` and executes them. This means:

1. When the layout partial starts rendering, the stack contains the page's `extend` body
2. As each `block`/`content` in the layout fires, `applyStack` processes pending overrides
3. The stack is consumed — each function runs once

In deep chains, the stack accumulates functions from each level of `extend`. When the root layout renders, all levels' content overrides have been queued.

## Practical Patterns

### Admin Layout Hierarchy

```
layout.hbs          ! base: html shell, head, body, foot
admin.hbs           ! extends layout: adds sidebar, admin header
settings.hbs        ! extends admin: settings-specific nav
users.hbs           ! extends settings: user management content
```

Each level refines the layout without repeating structure.

### Theme Variants

```
layout.hbs          ! base layout
theme-dark.hbs      ! extends layout: dark theme styles, overrides
theme-light.hbs     ! extends layout: light theme styles, overrides
page.hbs            ! extends theme-dark: page content
```

Switch themes by changing which partial the page extends.
