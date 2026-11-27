# Plugins (Alpine.js 3.17.5)

All official plugins install the same way — CDN `<script defer>` **before** the core, or `npm install @alpinejs/<name>` + `Alpine.plugin(<name>)` before `Alpine.start()`.

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/<name>@3.x.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

```js
import Alpine from 'alpinejs'
import plugin from '@alpinejs/<name>'

Alpine.plugin(plugin)
```

## Anchor — `@alpinejs/anchor`

Anchors an element's position to another element (dropdowns, popovers, tooltips) using Floating UI.

```html
<div x-data="{ open: false }">
    <button x-ref="button" @click="open = ! open">Toggle</button>
    <div x-show="open" x-anchor="$refs.button">Dropdown content</div>
</div>
```

- Sets `position: absolute` + `top`/`left` under the hood; flips above when there's no room below.
- **Positioning** — `.bottom`, `.bottom-start`, `.bottom-end`, `.top`, `.top-start`, `.top-end`, `.left`, `.left-start`, `.left-end`, `.right`, `.right-start`, `.right-end`.
- `.offset.N` — pixel offset (e.g. `.offset.10`).
- `.fixed` — fixed positioning strategy for reference elements inside `overflow: hidden/clip/auto` containers. **Heads-up:** a `transform`, `filter`, `perspective`, `backdrop-filter`, `will-change`, or `contain` on any ancestor creates a containing block, making `.fixed` behave like `absolute` relative to it — check for transformed ancestors when `.fixed` seems to do nothing.
- `.noflip` — disable auto-flipping.
- `.no-style` + `$anchor` magic — apply styles yourself: `x-bind:style="{ position: 'absolute', top: $anchor.y+'px', left: $anchor.x+'px' }"`.

## Collapse — `@alpinejs/collapse`

Smoothly animates height when an element's `x-show` toggles. Must sit on an element that already has `x-show` (different mechanism from `x-transition`).

```html
<div x-data="{ expanded: false }">
    <button @click="expanded = ! expanded">Toggle</button>
    <p x-show="expanded" x-collapse>...</p>
</div>
```

- `.duration.Nms` — animation duration (e.g. `.duration.1000ms`).
- `.min.Npx` — collapsed state keeps a minimum height instead of `0px` + `display: none` ("cut-off" effect).

## Focus — `@alpinejs/focus`

Manages focus on the page (successor of the old "Trap" plugin; Tabbable under the hood).

**`x-trap`** — traps Tab focus while its expression is true; returns focus to its previous location on release; nesting works (each untrap restores the last active element).

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Dialog</button>
    <span x-show="open" x-trap="open">
        <input type="text" placeholder="Some input...">
        <button @click="open = false">Close</button>
    </span>
</div>
```

Modifiers:

- `.inert` — applies `aria-hidden="true"` to all other page elements while trapping (recommended for modals).
- `.noscroll` — removes the scrollbar and blocks page scrolling while trapping.
- `.noreturn` — don't return focus to its previous location on release (e.g. dropdowns opened by focusing an input).
- `.noautofocus` — don't auto-focus the first focusable element when trapping engages.

**`$focus` magic** — chained utilities for programmatic focus control:

| Method | Description |
|---|---|
| `focus(el)` | Focus an element (handles timing internally) |
| `focusable(el)` | Detect whether an element is focusable |
| `focusables()` | All focusable elements in the current scope |
| `focused()` / `lastFocused()` | Currently / last focused element |
| `within(el)` | Scope subsequent calls to an element |
| `first()` / `last()` | Focus first/last focusable |
| `next()` / `previous()` | Focus next/previous focusable |
| `getFirst()` / `getLast()` / `getNext()` / `getPrevious()` | Retrieve without focusing |
| `wrap()` | Wrap around when reaching the ends (chain before next/previous) |
| `noscroll()` | Prevent scrolling to the element about to be focused |

```html
<div @keydown.right="$focus.wrap().next()" @keydown.left="$focus.wrap().previous()">
    <button>First</button><button>Second</button><button>Third</button>
</div>
```

## Intersect — `@alpinejs/intersect`

Wrapper around IntersectionObserver — react when an element enters/leaves the viewport (lazy loading, infinite scroll, view logging).

```html
<div x-data="{ shown: false }" x-intersect="shown = true">
    <div x-show="shown" x-transition>I'm in the viewport!</div>
</div>
```

- `x-intersect` (or alias `x-intersect:enter`) — expression runs on viewport entry; `x-intersect:leave` — on exit (by default only when the *whole* element leaves; `.full` variant semantics below).
- `.once` — run only the first time.
- `.half` — threshold 0.5; `.full` — threshold 0.99.
- `.threshold.N` — 0–100 percentage (`.threshold.50` = 50%).
- `.margin.<css-margin>` — `rootMargin` control; CSS-margin style values (one to four values, px or % or bare number): `.margin.200px`, `.margin.-100px`, `.margin.10%.25px.25.25px`.
- `.dwell[.Nms]` — require N ms of continuous intersection (default 250ms) before evaluating; combinable with `.once` and thresholds.
- `.parent` — observe against the element's parent instead of the viewport (scrollable containers).

## Mask — `@alpinejs/mask`

Formats text inputs as the user types (phones, cards, money, dates).

```html
<input x-mask="99/99/9999" placeholder="MM/DD/YYYY">
```

Wildcards: `*` any character, `a` alpha only, `9` numeric only. Literal characters (like `/`) are auto-inserted.

**Dynamic masks** — `x-mask:dynamic` with the current value as `$input`:

```html
<input x-mask:dynamic="
    $input.startsWith('34') || $input.startsWith('37')
        ? '9999 999999 99999' : '9999 9999 9999 9999'
">
```

Also accepts a function reference (`x-mask:dynamic="creditCardMask"`).

**Money** — prebuilt `$money()`:

```html
<input x-mask:dynamic="$money($input)">                    <!-- 0.00 -->
<input x-mask:dynamic="$money($input, ',')">              <!-- 0,00 -->
<input x-mask:dynamic="$money($input, '.', ' ')">         <!-- 3 000.00 (thousands separator) -->
<input x-mask:dynamic="$money($input, '.', ',', 4)">      <!-- 4-digit precision -->
```

## Morph — `@alpinejs/morph`

Morphs an element into new HTML while preserving browser/Alpine state (the Livewire/LiveView pattern).

```js
Alpine.morph(el, newHtml, options)
```

- Walks both DOM trees simultaneously and patches the live tree.
- **Lifecycle hooks** (third `options` arg): `updating(el, toEl, childrenOnly, skip)`, `updated(el, toEl)`, `removing(el, skip)`, `removed(el)`, `adding(el, skip)`, `added(el)`, `key(el)`, plus `lookahead: true` (treat a to-be-removed element as a move to a later sibling).
- **Keys** — repeated nodes need a `key="..."` attribute (default key source) so Morph *moves* them instead of replacing them; customize with `key(el)` (e.g. `el.dataset.key`). Without keys, reordering lists corrupts node identity (inputs lose value/focus).

**`Alpine.morphBetween(startMarker, endMarker, newHtml, options)`** — morph the DOM range between two marker elements (typically comments) instead of a single root node.

## Persist — `@alpinejs/persist`

Persists state across page loads via localStorage.

```html
<div x-data="{ count: $persist(0) }">
    <button x-on:click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

- Stored under a namespaced key (`_x_<property>`); works with primitives, arrays, and objects.
- **Type changes** — if the property changes type (e.g. number → object), localStorage must be cleared or the key renamed, or you get corruption.
- `.as('key')` — custom storage key (`$persist(0).as('other-count')`).
- `.using(storage)` — custom store: `.using(sessionStorage)` or any object with `getItem`/`setItem` (e.g. a cookie storage).
- With `Alpine.data`, use a standard function (not arrow) so `this` binds: `Alpine.data('dropdown', function () { return { open: this.$persist(false) } })`.
- `Alpine.$persist` global — persist outside `x-data`, e.g. in stores: `Alpine.store('darkMode', { on: Alpine.$persist(true).as('darkMode_on') })`.

## Resize — `@alpinejs/resize`

Wrapper around ResizeObserver — react when an element's size changes.

```html
<div x-data="{ width: 0, height: 0 }" x-resize="width = $width; height = $height">
    <p x-text="'Width: ' + width + 'px'"></p>
</div>
```

- `.document` — observe the whole document's size.
- `.viewport` — react to visual-viewport changes (mobile browser UI / on-screen keyboard) via `window.visualViewport`; falls back to observing the document where unavailable.

## Sort — `@alpinejs/sort`

Drag-to-reorder elements (SortableJS under the hood).

```html
<ul x-sort>
    <li x-sort:item>foo</li>
    <li x-sort:item>bar</li>
</ul>
```

- **Handlers** — `x-sort="handler"` runs on every reorder; `$item` is the item's key (from `x-sort:item="key"`) and `$position` the new index (0-based). A named function receives `(item, position)`.
- **Groups** — matching `x-sort:group="name"` on multiple lists allows dragging between them; when crossing groups only the destination list's handler fires.
- **Drag handles** — `x-sort:handle` marks a sub-element as the only draggable part.
- **`x-sort:ignore`** — elements that never initiate drags (buttons/links inside items); they keep working normally.
- **`.ghost`** — show a "ghost" copy of the original while dragging instead of an empty hole; the ghost carries the `.sortable-ghost` class (or `x-sort:config="{ ghostClass: 'opacity-50' }"`).
- **`body.sorting`** — added to `<body>` while dragging; style the page conditionally with CSS (`body.sorting #warning { display: block }`).
- **CSS hover bug** — Chrome/Safari apply hover styles to the element *in the dragged element's place*; scope hover with `[body:not(.sorting)_&]:hover:border` (Tailwind arbitrary variant) or equivalent.
- **`x-sort:config="{ ... }"`** — override SortableJS options; overwriting `handle`, `group`, `filter`, `onSort`, `onStart`, or `onEnd` may break functionality.

## Undocumented in this tag's docs tree

These packages ship in the monorepo but have no pages under `packages/docs` at v3.17.5 (treat their APIs as unverified here):

- `@alpinejs/navigate` (3.10.2) — SPA-like navigation; dev harness `index2.html` uses `x-navigate:persist`.
- `@alpinejs/history` (3.0.0-alpha.0) — binds state to query-string parameters via the history API.
