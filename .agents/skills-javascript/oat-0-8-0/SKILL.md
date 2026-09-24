---
name: oat-0-8-0
description: >
  Oat 0.8.0 — ultra-lightweight, zero-dependency semantic HTML/CSS/JS UI component library
  (~10KB minified CSS+JS, no framework, no build). Styles semantic elements contextually without
  classes — headings, buttons, forms, tables, dialog, details, progress, meter — and adds the
  WebComponents ot-dropdown, ot-tabs, ot-taginput, ot-upload plus the ot.toast() JavaScript API.
  Use when building, theming, or debugging pages with Oat; component markup, data-variant colors,
  CSS variable theming, dark mode, the 12-column grid, and sidebar layout.
license: MIT
compatibility: >
  Modern browsers — Popover API and CSS light-dark() (Chrome 114+, Firefox 125+, Safari 17+);
  HTML command/commandfor (Chrome 133+, Firefox 133+, Safari polyfilled in oat.min.js)
metadata:
  tags:
    - javascript
    - frontend
    - css
    - ui-library
    - webcomponents
---

# oat 0.8.0

## Overview

Oat is an ultra-lightweight (~10KB minified CSS+JS combined), zero-dependency UI component library. No framework, no build step — include two files and write semantic HTML; most elements are styled contextually **without classes**. Semantic tags and attributes carry the styling, which forces good markup and keeps it class-free. A few dynamic components are WebComponents with minimal JavaScript.

Three mechanisms:

- **Attributes and classes (CSS-only)** — `data-variant="secondary|success|warning|danger"` for semantic colors (`error` is an alias for `danger`); class modifiers `.outline`, `.ghost`, `.small`, `.large`, `.icon` (buttons), `.button` (links), `.badge`, `.card`, `.table`, `.skeleton`, `.group`; layout attributes `data-field`, `data-hint`, `data-sidebar*`, `data-spinner`, `data-tooltip-placement`.
- **WebComponents** — `oat.min.js` auto-registers `ot-dropdown` (popover menus with keyboard nav), `ot-tabs` (ARIA tabs with hash deep-linking), `ot-taginput` (tag input with datalist autocomplete), `ot-upload` (drag-drop file picker).
- **JS API** — `ot.toast(message, title?, options?)`, `ot.toast.el(element, options?)`, `ot.toast.clear(placement?)`.

Component inventory (full markup in the references below):

| Component | Markup pattern | JS |
|---|---|---|
| Typography | `<h1>`–`<h6>`, `<p>`, `<code>`, `<pre>`, `<blockquote>`, `<ul>`/`<ol>` | no |
| Button | `<button>` + `data-variant`, `.outline`/`.ghost`/`.small`/`.large`/`.icon`; `menu.buttons` groups | no |
| Badge | `<span class="badge" data-variant="...">` | no |
| Alert | `<div role="alert" data-variant="...">` | no |
| Accordion | `<details>` + `<summary>` (`name` groups) | no |
| Card | `<article class="card">` | no |
| Avatar | `<figure data-variant="avatar">` (groups via `role="group"`) | no |
| Breadcrumb | `<nav>` + `<ol class="unstyled hstack">` | no |
| Dialog | `<dialog>` + `commandfor`/`command` buttons | polyfill only |
| Dropdown / Popover | `<ot-dropdown>` + `popovertarget` + `<menu popover>` | yes |
| Tabs | `<ot-tabs>` + `role="tablist"`/`tab`/`tabpanel` | yes |
| Switch | `<input type="checkbox" role="switch">` | no |
| TagInput | `<ot-taginput>` + `<input>` | yes |
| Toast | `ot.toast(...)` | yes |
| Tooltip | `title` attribute (JS rewrites to `data-tooltip`) | yes |
| Upload | `<ot-upload>` + native `<input type="file">` | yes |
| Table | `<table>` + optional `.table` scroll wrapper | no |
| Pagination | `<nav>` + `<menu class="buttons">` | no |
| Form | `<label data-field>` + native inputs | no |
| Progress / Meter | `<progress>`, `<meter>` | no |
| Spinner | `aria-busy="true"` + `data-spinner` | no |
| Skeleton | `<div class="skeleton line|box" role="status">` | no |
| Grid | `.container` > `.row` > `.col-1`–`.col-12` | no |
| Sidebar layout | `data-sidebar-layout` + `<aside data-sidebar>` + `<main>` | toggle only |

## Usage

Include the two files in `<head>` (CDN):

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

Or via npm: `npm install @knadh/oat`, then `import '@knadh/oat/oat.min.css'; import '@knadh/oat/oat.min.js';` (individual component files can be imported from `@knadh/oat/css` and `@knadh/oat/js`).

Then write plain semantic HTML — no classes needed for the base look:

```html
<h1>Dashboard</h1>
<article class="card">
  <header><h3>Revenue</h3><p>vs last month</p></header>
  <progress value="72" max="100"></progress>
</article>
<button data-variant="danger" class="outline">Delete</button>
```

Theming is done by overriding CSS variables in a stylesheet loaded **after** `oat.min.css`. All colors are `light-dark()`, so dark mode follows the OS automatically; force one side with `document.body.style.colorScheme = 'dark'`. Full variable list (colors, spacing, radius, text scale, z-index), dark-mode details, and selective component bundling are in [01-usage-and-theming](references/01-usage-and-theming.md).

## Gotchas

- **Sub-v1 library** — breaking changes are likely until 1.0. Pin exact versions in CDN URLs and npm.
- **`data-variant="error"` is an alias of `danger`** — both map to `--danger`. Docs use `error` on alerts; either is valid.
- **Dialogs rely on the HTML Command API** — opening/closing goes through `commandfor` + `command="show-modal"|"close"` buttons (native in Chrome/Firefox 133+; Safari gets a click polyfill from `base.js`). Cancel buttons must be `type="button"` with `command="close"`; confirm buttons set a `value` read via `dialog.returnValue` on the `close` event. Use `closedby="any"` for outside-click dismissal (a touch shim in `base.js` prevents backdrop clicks bleeding through on touch devices).
- **Tooltips hijack `title`** — `oat.min.js` rewrites every `title` attribute to `data-tooltip` + `aria-label` (on load and via a MutationObserver). Native tooltips are gone, and Oat tooltips need the JS.
- **Replaced elements need a wrapper for tooltips** — `<img>`, `<iframe>` and friends do not get styled by `[data-tooltip]`; put the `title` on a wrapping `<span>`.
- **Selective bundling has required files** — when importing individual files from `css/`/`js/`, always include `00-base.css`, `01-theme.css`, and `base.js`, with your override CSS after Oat's files. Oat declares `@layer theme, base, components, animations, utilities`; unlayered styles (typical hand-written CSS) beat all of them, so overrides rarely need `!important`.
- **Grid collapse is a 768px media query** — the docs mention container queries, but the implementation collapses `.row` to 4 columns (full stack) below 768px. Offsets only exist up to `offset-6`.
- **Sidebar breakpoint is hardcoded in JS** — `sidebar.js` cannot read a CSS variable inside `@media`, so 768px is fixed in the handler; change it by editing the script. `data-sidebar-layout="always"` keeps the toggle active at all widths.
- **ot-tabs pairs tabs and panels by index** — `[role="tab"]` order inside the tablist must match `[role="tabpanel"]` order; a mismatched order shows wrong panels silently. `data-anchor="key"` deep-links as `#key=tab-id` (URLSearchParams in the hash), not a bare `#tab-id`. It emits an `ot-tab-change` event, and `.activeIndex` is read/write.
- **ot-taginput values are dual-natured** — the `value` attribute is a comma-separated string; the `.value` JS property is an array of strings or objects (an object's `toString()` is the display label). Setting `.value` does not emit `input`; tag add/remove does, with `detail` = the current array. Enter or comma adds a tag; Backspace on empty input removes the last one.
- **ot-upload funnels everything into one `change` event** — picker selection, drop, and removal all fire the native (bubbling) `change` on the inner `<input>`; selected files render as removable badges in `[data-files]`.
- **Toast argument order** — `ot.toast(message, title, options)`; pass `''` for `title` to reach options-only. `duration: 0` = persistent; hovering pauses the countdown.
- **`aria-busy` does not remove content** — `aria-busy="true"` shows an inline spinner next to the content; use `data-spinner="overlay"` to dim and disable a container instead.

## References

- [01-usage-and-theming](references/01-usage-and-theming.md) — installation (CDN, npm, download), full CSS variable reference, dark mode, selective bundling, CSS layers, library dev setup
- [02-basic-components](references/02-basic-components.md) — markup and examples for the CSS-only components: typography, button, badge, alert, breadcrumb, card, avatar, form elements, table, pagination
- [03-interactive-components](references/03-interactive-components.md) — markup and examples for dynamic components: accordion, dialog, dropdown/popover, tabs, switch, taginput, toast, tooltip, upload, spinner, skeleton, meter, progress
- [04-layout-grid-utilities](references/04-layout-grid-utilities.md) — 12-column grid, sidebar layout, and all utility classes
- [05-recipes-extensions](references/05-recipes-extensions.md) — composable UI recipes (split button, radio cards, form card, empty state, stats cards), community extensions, related zero-dep libraries
