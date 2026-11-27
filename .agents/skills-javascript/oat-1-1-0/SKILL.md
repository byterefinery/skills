---
name: oat-1-1-0
description: Oat 1.1.0 — an ultra-lightweight (~10KB CSS+JS), zero-dependency, semantic HTML/CSS/JS UI library with no framework or build step. Use when styling web apps from plain semantic HTML that is styled contextually out of the box (no class pollution). Covers buttons, forms, cards, alerts, badges, tables, modal dialogs via the native dialog element and command API, accordions via native details, switch, progress, meter, skeleton, spinner, avatar, breadcrumb, pagination, and a 12-column grid. Also the JS-powered WebComponents ot-dropdown, ot-tabs, ot-taginput, ot-upload, the ot.toast() notification API, and CSS-variable theming with automatic light-dark dark mode.
license: MIT
---

# oat 1.1.0

## Overview

Oat is an ultra-lightweight, zero-dependency semantic UI component library (~10KB CSS + JS total). No framework, build step, or dev tooling — include two small files and write semantic HTML. Elements are **styled contextually by their tag and attributes without classes** (e.g. `<button>`, `<progress>`, `<details>`, `role="alert"`), which keeps markup clean. A few dynamic components are WebComponents (`ot-*`) backed by minimal JS.

Two mental models:

1. **Semantic/CSS-only** — most components work with just `oat.min.css` (typography, button, form, card, alert, badge, table, accordion, switch, progress, meter, skeleton, spinner, avatar, breadcrumb, pagination, dialog).
2. **JS-powered** — `ot-dropdown`, `ot-tabs`, `ot-taginput`, `ot-upload`, enhanced tooltips, sidebar layout, and `ot.toast()` require `oat.min.js`.

### Quick start

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

Then write plain semantic HTML — no classes needed for base styling:

```html
<h1>Hello World</h1>
<p>This paragraph is styled automatically.</p>
<button>Click me</button>
<button data-variant="danger">Delete</button>
```

## Usage

### Installation

- **CDN** — `https://unpkg.com/@knadh/oat/oat.min.css` + `oat.min.js` (defer).
- **npm** — `npm install @knadh/oat`, then `import '@knadh/oat/oat.min.css'; import '@knadh/oat/oat.min.js';` (or import individual files from `@knadh/oat/css` and `@knadh/oat/js`).
- **Download** — fetch `oat.min.css` / `oat.min.js` and reference locally.

### Styling model

- Base semantic elements are styled with **no classes**: `h1`–`h6`, `p`, `a`, `button`, `input`, `select`, `textarea`, `table`, `blockquote`, `pre`/`code`, `progress`, `meter`, `details`/`summary`, `fieldset`.
- **`data-variant`** drives semantic color: `secondary`, `success`, `warning`, `danger`, `error` (both `danger` and `error` resolve to the danger color). Applies to `button`, `badge`, `role="alert"`, toast, etc.
- **Style modifier classes** (not semantic): `.outline`, `.ghost` (buttons), `.small`/`.large` (sizes), `.card`, `.badge`, `.table`, `.icon`, `.skeleton`, `.group`, `.button` (to make a link look like a button).
- **Layout helpers**: `.hstack`/`.vstack`, `.gap-{n}`, `.mt-{n}`/`.mb-{n}`, `.p-{n}`, `.w-100`, `.text-light`/`.text-lighter`, `.unstyled`, `.align-center`, `.justify-center`/`.justify-between`/`.justify-end`.
- **Grid**: `.container` > `.row` > `.col-{n}` (n = 1–12), with `.offset-{n}` and `.col-end`.

### Components at a glance

| Component | Markup | JS? |
|---|---|---|
| Typography | `h1`–`h6`, `p`, `a`, `code`, `blockquote`, lists | no |
| Button | `<button>`, `data-variant`, `.outline`/`.ghost`, `.small`/`.large`; group in `<menu class="buttons">` | no |
| Form | `<label data-field>` wrapping inputs; `data-hint`; `aria-invalid="true"` for errors; `.group` fieldset | no |
| Card | `<article class="card">` with `header`/`footer` | no |
| Alert | `<div role="alert" data-variant="success">` | no |
| Badge | `<span class="badge" data-variant="...">` | no |
| Table | `<table>` (styled); wrap in `class="table"` for horizontal scroll | no |
| Accordion | native `<details>`/`<summary>`; `name="x"` groups them | no |
| Switch | `<input type="checkbox" role="switch">` | no |
| Progress / Meter | native `<progress>` / `<meter>` | no |
| Skeleton | `.skeleton.line` / `.skeleton.box` with `role="status"` | no |
| Spinner | `aria-busy="true"` + `data-spinner="small|large|overlay"` | no |
| Avatar | `<figure data-variant="avatar">` with `<img>`/`<abbr>`; `role="group"` for stacks | no |
| Breadcrumb | `<nav>` + `<ol>`, `aria-current="page"` | no |
| Pagination | `<nav>` + `<menu class="buttons">` of `.button` links | no |
| Dialog | native `<dialog>` + `commandfor`/`command="show-modal"` | no |
| Dropdown / popover | `<ot-dropdown>` + native popover API (`popovertarget`) | yes |
| Tabs | `<ot-tabs>` + `role="tablist"`/`tab`/`tabpanel`; `data-anchor` for URL hash | yes |
| TagInput | `<ot-taginput value="a, b">` with child `<input>`; `.value`, `.add()`, `input` event | yes |
| Tooltip | `title` attribute (enhanced); `data-tooltip-placement`; wrap replaced elements | yes |
| Upload | `<ot-upload>` wrapping `<input type="file">`; `change` on select/drop/remove | yes |
| Toast | `ot.toast(msg, title?, {variant, placement, duration})`; `ot.toast.el(el, opts?)` | yes |
| Sidebar layout | `data-sidebar-layout` container + `data-sidebar`/`data-topnav`/`data-sidebar-toggle` | yes |

See references for full markup of every component.

### Toast API (global `ot.toast`)

```js
ot.toast("Action completed", "All good", { variant: "success" });
// options: variant ('info'|'success'|'danger'|'warning'),
//          placement ('top-right' default, 'top-left', 'top-center',
//                     'bottom-left', 'bottom-center', 'bottom-right'),
//          duration (ms, default 4000; 0 = persistent)

ot.toast.el(templateOrElement, { duration: 8000, placement: "bottom-center" }); // custom HTML (cloned)
ot.toast.clear();          // clear all
ot.toast.clear("top-right"); // clear one placement
```

For custom toast markup use `<output class="toast" data-variant="...">` with an `<h6 class="toast-title">`.

### Theming & dark mode

All colors/sizes are CSS variables (`--primary`, `--background`, `--success`, `--space-4`, `--radius-*`, `--text-*`, ...). Override them in your own CSS **loaded after** Oat's CSS to re-theme. Dark mode is automatic via `light-dark()` + `color-scheme: light dark` (follows OS). Force a theme with `document.body.style.colorScheme = 'dark' | 'light'`.

## Gotchas

- **No classes for base styling** — adding Bootstrap/Tailwind-style utility soup defeats Oat. Style by semantic tag + `data-variant`; reach for classes only for the documented modifiers.
- **`data-variant` spelling** — valid values are `secondary`, `success`, `warning`, `danger`, `error`. `error` and `danger` are aliases (both map to the danger color); don't invent others.
- **JS is optional but required for `ot-*`** — `ot-dropdown`, `ot-tabs`, `ot-taginput`, `ot-upload`, tooltips, sidebar, and `ot.toast()` do nothing without `oat.min.js`. Keep `defer` so the `ot` global exists after first render.
- **`ot` global is only the toast API** — `window.ot` exposes `ot.toast` (+`.el`, `.clear`). The other WebComponents are registered as custom elements, not on `ot`.
- **Dialogs read `returnValue`, not the button** — a `<button value="confirm">` inside `<form method="dialog">` sets `dialog.returnValue`; read it in the `close` event, not on click.
- **Toast `duration: 0` means persistent** — the default is 4000ms; pass `0` to keep a toast until `ot.toast.clear()`.
- **TagInput `.value` setter does NOT emit `input`** — set `.value = [...]` to replace silently; use `.add(value)` (or mutation via events) when you need the bubbling `input` event. Object tags dedupe by `===`.
- **Tooltips on replaced elements** — `<img>`/`<iframe>` can't take `title` meaningfully; wrap them in a parent span with the `title`.
- **Spinner is an attribute, not a tag** — `aria-busy="true"` + `data-spinner` on any element; `data-spinner="overlay"` dims + overlays the whole container.
- **Grid is 12-column** — `.col-{n}` where n is 1–12; use `.offset-{n}` to push and `.col-end` to right-align. Wrap in `.container`/`.row`.
- **Theming order matters** — your override CSS must come **after** `oat.min.css`, or the defaults win.
- **Selective builds need the base files** — if bundling only some components, always include `00-base.css`, `01-theme.css`, and `base.js` before the rest.
- **Skeleton needs `role="status"`** — `.skeleton` alone isn't enough; pair with `.line` (text) or `.box` (image).

## References

- [01-components-css](references/01-components-css.md) — markup for all semantic/CSS-only components (typography, button, form, card, alert, badge, table, accordion, switch, progress, meter, skeleton, spinner, avatar, breadcrumb, pagination, dialog)
- [02-components-js](references/02-components-js.md) — JS WebComponents & APIs (ot-dropdown, ot-tabs, ot-taginput, ot-upload, tooltip, sidebar, ot.toast)
- [03-layout-utilities](references/03-layout-utilities.md) — 12-column grid, spacing/stacking/alignment helpers, table wrapper
- [04-theming](references/04-theming.md) — CSS variables, theming, dark mode, CSS layers, selective file inclusion, community extensions
- [05-recipes](references/05-recipes.md) — composable UI patterns (split button, radio cards, form card, empty state, stats cards), related libraries
