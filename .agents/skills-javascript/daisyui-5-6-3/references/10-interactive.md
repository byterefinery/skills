# 10 — Interactive

## button

Action trigger. Works on `<button>`, `<a>`, `<input>`.

**Class names:**
- component: `btn`
- color: `btn-primary`, `btn-secondary`, `btn-accent`, `btn-neutral`, `btn-info`, `btn-success`, `btn-warning`, `btn-error`
- style: `btn-outline`, `btn-dash`, `btn-soft`, `btn-ghost`, `btn-link`
- behavior: `btn-active`, `btn-disabled`
- size: `btn-xs`, `btn-sm`, `btn-md`, `btn-lg`, `btn-xl`
- modifier: `btn-wide`, `btn-block`, `btn-square`, `btn-circle`

```html
<button class="btn {MODIFIER}">Label</button>
```

Can have an icon before or after text. To disable with a class, use `tabindex="-1" role="button" aria-disabled="true"` instead of the `disabled` attribute.

## dropdown

Opens a menu or element on click/hover/focus.

**Class names:**
- component: `dropdown`
- part: `dropdown-content`
- placement: `dropdown-start`, `dropdown-center`, `dropdown-end`, `dropdown-top`, `dropdown-bottom`, `dropdown-left`, `dropdown-right`
- modifier: `dropdown-hover`, `dropdown-open`, `dropdown-close`

Using details/summary:
```html
<details class="dropdown">
  <summary>Button</summary>
  <ul class="dropdown-content">{items}</ul>
</details>
```

Using popover API:
```html
<button popovertarget="{id}" style="anchor-name:--{anchor}">Button</button>
<ul class="dropdown-content" popover id="{id}" style="position-anchor:--{anchor}">{items}</ul>
```

Using CSS focus:
```html
<div class="dropdown">
  <div tabindex="0" role="button">Button</div>
  <ul tabindex="-1" class="dropdown-content">{items}</ul>
</div>
```

Content can be any HTML element, not just `<ul>`.

## fab

Floating Action Button in the screen corner with speed dial.

**Class names:**
- component: `fab`
- part: `fab-close`, `fab-main-action`
- modifier: `fab-flower`

Single FAB:
```html
<div class="fab">
  <button class="btn btn-lg btn-circle">{icon}</button>
</div>
```

With speed dial:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{icon}</div>
  <button class="btn btn-lg btn-circle">{icon}</button>
  <button class="btn btn-lg btn-circle">{icon}</button>
</div>
```

Use `fab-flower` for quarter-circle arrangement. Use `fab-close` or `fab-main-action` to replace the original button when open.

## collapse

Shows/hides content independently (not grouped).

**Class names:**
- component: `collapse`
- part: `collapse-title`, `collapse-content`
- modifier: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

```html
<div tabindex="0" class="collapse {MODIFIER}">
  <div class="collapse-title">{title}</div>
  <div class="collapse-content">{content}</div>
</div>
```

Use `tabindex="0"` or `<input type="checkbox">` as first child. Also works with `<details>/<summary>`.

## accordion

Shows/hides content — only one item open at a time. Uses radio inputs.

**Class names:** Same as collapse (`collapse`, `collapse-title`, `collapse-content`, `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`).

```html
<div class="collapse">
  <input type="radio" name="accordion" checked="checked" />
  <div class="collapse-title">Item 1</div>
  <div class="collapse-content">Content 1</div>
</div>
<div class="collapse">
  <input type="radio" name="accordion" />
  <div class="collapse-title">Item 2</div>
  <div class="collapse-content">Content 2</div>
</div>
```

All radios sharing a `name` form one group (only one open). Use different names for separate accordion groups.

## filter

Radio button group that hides unselected options and shows a reset button.

**Class names:**
- component: `filter`
- part: `filter-reset`

Using form:
```html
<form class="filter">
  <input class="btn btn-square" type="reset" value="×"/>
  <input class="btn" type="radio" name="filter-group" aria-label="All"/>
  <input class="btn" type="radio" name="filter-group" aria-label="Active"/>
</form>
```

Without form:
```html
<div class="filter">
  <input class="btn filter-reset" type="radio" name="filter-group" aria-label="×"/>
  <input class="btn" type="radio" name="filter-group" aria-label="All"/>
</div>
```

Do not check any radio by default. Each group must have unique `name`.

## card

Groups and displays content with optional image, title, body, and actions.

**Class names:**
- component: `card`
- part: `card-title`, `card-body`, `card-actions`
- style: `card-border`, `card-dash`
- modifier: `card-side`, `image-full`
- size: `card-xs`, `card-sm`, `card-md`, `card-lg`, `card-xl`

```html
<div class="card {MODIFIER}">
  <figure><img src="{url}" alt="{alt}" /></figure>
  <div class="card-body">
    <h2 class="card-title">Title</h2>
    <p>Description</p>
    <div class="card-actions">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

`<figure>` and `<div class="card-body">` are optional. Use `sm:card-horizontal` for responsive layouts. If image is placed after `card-body`, it appears at the bottom.
