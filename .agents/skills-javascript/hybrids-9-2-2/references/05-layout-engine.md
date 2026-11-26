# Layout Engine

CSS layout rules directly in templates — utility-first style, focused on "invisible" CSS (display types, alignment, positioning, sizing). Visible styling belongs to reusable UI components via the template styling helpers.

## Table of Contents

- [Usage](#usage)
- [Compound selectors](#compound-selectors)
- [Media queries](#media-queries)
- [Arguments & dimensions](#arguments--dimensions)
- [CSS variables](#css-variables)
- [Rules](#rules)
- [Generic values (::)](#generic-values-)

---

## Usage

Wrap the root template in `<template layout="...">` — the `<template>` element represents the host element (and can itself be styled). Each `layout*` attribute resolves at compile time to a single unique class selector shared between all component instances; with Constructable Stylesheets support the CSS goes into one global shared stylesheet.

```js
define({
  tag: "my-element",
  render: () => html`
    <template layout="row">
      <div layout="grow"></div>
    </template>
  `,
});
```

Layout engine styles are added **before** template-helper styles (`.css`/`.style`), so both can be mixed.

**Attribute values do not support expressions** — compilation happens before the first run. Use [compound selectors](#compound-selectors) for conditional rules.

## Compound selectors

Extend `layout` with any valid CSS selector that contains no space:

```html
<div layout.selector=""></div>
```

The selector is added to the generated class selector, so rules apply only when the condition holds:

```html
<my-button
  disabled="${disabled}"
  layout="fixed top right"
  layout[disabled]="hidden"
></my-button>

<my-other-element
  class="${{ show: disabled }}"
  layout="hidden"
  layout.show="block"
></my-other-element>
```

Any selector works, including pseudo-classes:

```html
<div layout:first-child="margin:0"></div>
<div layout:last-of-type="grow"></div>
```

## Media queries

The part after `@` in `layout@...` selects the media query. Default feature is `min-width`:

| Value | Query |
|---|---|
| `portrait` | `@media (orientation: portrait)` |
| `landscape` | `@media (orientation: landscape)` |
| `hover` | `@media (hover: hover)` |
| `any-hover` | `@media (any-hover: hover)` |
| `print` | `@media print` |
| `[value]` | `@media (min-width: [value])` |

Complex conditions: `|` = AND, `:` = OR — `layout@landscape|768px:1024px` generates `@media (orientation: landscape) and (min-width: 768px), (min-width: 1024px)`.

```html
<div layout="row gap" layout@768px="column gap:2"></div>
```

## Arguments & dimensions

Attribute values are space-separated rules, applied in order; rule arguments are `:`-separated (no whitespace). Multi-argument rules allow skipping values: `layout="row::inline width::50%"`.

Dimension argument mapping, in order:

1. Predefined strings: `min` → `min-content`, `max` → `max-content`, `fit` → `fit-content`, `full` → `100%`
2. Bare numbers multiply by `8px` (`1` → `8px`, `2` → `16px`, `0.5` → `4px`)
3. Any other value is used as is

## CSS variables

A `--` prefix passes a CSS variable through untouched (dynamic runtime values, scoped subtrees):

```html
<div layout="margin:--layout-spacing"></div>
```

## Rules

### Base

| Rule | Arguments | Properties |
|---|---|---|
| `block` | `[align:value]` | `display: block; text-align: [align]` |
| `inline` | — | `display: inline`; after another display type makes it `display: [type]-inline` |
| `contents` | — | `display: contents` |
| `hidden` | — | `display: none` |

### Flexbox

| Rule | Arguments | Default | Properties |
|---|---|---|---|
| `row`, `row-reverse`, `column`, `column-reverse` | `[wrap:value]` | `nowrap` | `display: flex; flex-flow: type [wrap]` |
| `grow` | `[number:value]` | `1` | `flex-grow` |
| `shrink` | `[number:value]` | `1` | `flex-shrink` |
| `basis` | `[size:dimension]` | — | `flex-basis` |
| `gap` | `[column:dim]:[row:dim]` | `1` | `column-gap`, `row-gap` |
| `order` | `[number:value]` | `0` | `order` |

### Grid

| Rule | Arguments | Default | Properties |
|---|---|---|---|
| `grid` | `[columns]:[rows]:[autoFlow:value]:[dense]` | `1` | `display: grid`, `grid-template-columns/rows`, `grid-auto-flow` |
| `area` | `[column:value]:[row:value]` | — | `grid-column/row: span n \| value` |
| `gap` | `[column:dim]:[row:dim]` | `1` | `column-gap`, `row-gap` |
| `order` | `[number:value]` | `0` | `order` |

Grid `columns`/`rows` mapping: a bare number → `repeat([n], minmax(0, 1fr))`; otherwise dimension rules apply. Multiple tracks split with `|` (`grid:2|min|2`); complex values must not contain whitespace (`grid:repeat(2,minmax(50%,1fr))`). Examples: `grid:12` = 12 equal tracks; `grid:2:100px|max` = 2 auto columns, rows `100px max-content`.

### Alignment

| Rule | Arguments | Properties |
|---|---|---|
| `items` | `[align:value][justify:value]` | `place-items` (default `items:start`) |
| `content` | `[align:value][justify:value]` | `place-content` (default `content:start`) |
| `self` | `[align:value][justify:value]` | `place-self` (default `self:start`) |
| `center` | — | `place-items: center; place-content: center` |

### Size

| Rule | Arguments | Properties |
|---|---|---|
| `size` | `[width:dim]:[height:dim]` | `width`, `height` (or width), `box-sizing: border-box` |
| `width` | `[base:dim]:[min:dim]:[max:dim]` | `width`, `min-width`, `max-width`, `box-sizing` |
| `height` | `[base:dim]:[min:dim]:[max:dim]` | `height`, `min-height`, `max-height`, `box-sizing` |
| `ratio` | `[value]` | `aspect-ratio` |
| `overflow` | `[type:value]` or `[axis:value]:[type:value]` (default `hidden`) | `overflow`; `scroll` adds flex scroll behavior (`flex-grow: 1`, `flex-basis: 0`, `overscroll-behavior: contain`, touch scrolling) |
| `margin` | `[v1]:[v2]:[v3]:[v4]` or `[side:value]:[v:dim]` (default `1`) | `margin` shorthand / per-side |
| `padding` | `[v1]:[v2]:[v3]:[v4]` or `[side:value]:[v:dim]` (default `1`) | `padding` shorthand / per-side |

### Position

Types: `absolute`, `relative`, `fixed`, `sticky`, `static` (set `position`).

| Rule | Arguments | Default | Properties |
|---|---|---|---|
| `inset` | `[value:dim]` | `0` | `top/right/bottom/left` |
| `top` / `right` / `bottom` / `left` | `[value:dim]` | `0` | the respective offset |
| `layer` | `[index:value]` | `1` | `z-index` |

### View Transitions

| Rule | Arguments | Properties |
|---|---|---|
| `view` | `[name:value]` | `view-transition-name` |

Works with `html.transition` for named view transition elements.

## Generic values (::)

The empty rule `::` generates `[property]: var(--[...args])` — plug predefined design tokens into any CSS property:

```html
<div layout="block ::color:primary ::ui:font:body"></div>
```

Generates `display: block; color: var(--color-primary); font: var(--ui-font-body);`.
