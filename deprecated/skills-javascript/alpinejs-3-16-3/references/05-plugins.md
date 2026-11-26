# Alpine.js 3.16.3 — Official Plugins

Shared install pattern for every plugin below (all ship from the same monorepo):

```html
<!-- CDN: plugin scripts before the core, both deferred -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/<name>@3.16.3/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.16.3/dist/cdn.min.js"></script>
```

```js
// Module: register between import and start
import Alpine from 'alpinejs'
import plugin from '@alpinejs/<name>'
Alpine.plugin(plugin)
Alpine.start()
```

- [anchor](#anchor)
- [collapse](#collapse)
- [csp](#csp)
- [focus](#focus)
- [history](#history)
- [intersect](#intersect)
- [mask](#mask)
- [morph](#morph)
- [navigate](#navigate)
- [persist](#persist)
- [resize](#resize)
- [sort](#sort)

## anchor

`@alpinejs/anchor` positions an element relative to another (dropdowns, popovers, tooltips), built on Floating UI.

```html
<div x-data="{ open: false }">
    <button x-ref="button" @click="open = ! open">Toggle</button>
    <div x-show="open" x-anchor="$refs.button">Dropdown content</div>
</div>
```

`x-anchor` takes any expression resolving to the reference element (usually `$refs.name`). It sets `position: absolute` with computed `top`/`left` and flips to the opposite side when there's no room.

Positioning modifiers: `.bottom .bottom-start .bottom-end .top .top-start .top-end .left .left-start .left-end .right .right-start .right-end` (default: bottom).

Other modifiers:

- `.offset.8` — pixel offset between reference and anchored element.
- `.fixed` — use `position: fixed` strategy instead of `absolute`. Use when the reference sits inside an `overflow: hidden/auto/clip` container. Caveat: any ancestor with `transform`, `filter`, `perspective`, `backdrop-filter`, `will-change`, or `contain` creates a containing block that makes `.fixed` behave like `absolute` — check for transformed ancestors when `.fixed` "does nothing".
- `.noflip` — keep the configured side even when out of room (no auto-flipping).

## collapse

`@alpinejs/collapse` animates expand/collapse of `x-show` elements (height animation, distinct from the transition system).

```html
<button @click="open = ! open">Toggle</button>
<div x-show="open" x-collapse>
    Animated content...
</div>
```

`x-collapse` must sit on an element that already has `x-show`.

Modifiers:

- `.duration.750ms` — animation duration (default 250 ms).
- `.min.100px` — collapsed state keeps a minimum height instead of `0px` + `display: none` (useful for "peek" collapse).

## csp

`@alpinejs/csp` is a drop-in **core** build (not an add-on plugin) whose evaluator does not violate `unsafe-eval` CSP. Swap the core script:

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.3/dist/cdn.min.js"></script>
```

```js
import Alpine from '@alpinejs/csp'   // instead of 'alpinejs'
Alpine.start()
```

Supports most inline expressions (literals, basic ops, assignments, method calls); rejects `new`, global references, and complex chains — extract those into methods. Full details in [01-installation](01-installation.md#csp-build-alpinejscsp) and [04-advanced](04-advanced.md#csp-build-details).

## focus

`@alpinejs/focus` manages keyboard focus, built on Tabbable.

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Dialog</button>

    <div x-show="open" x-trap="open" @keydown.escape="open = false">
        <input type="text">
        <button @click="open = false">Close</button>
    </div>
</div>
```

`x-trap` takes a reactive expression: while truthy, Tab/Shift-Tab are trapped inside the element; when it becomes false, focus returns to whatever was focused before.

- **Nesting is recursive** — a trap inside a trap works; focus restores in reverse order on untrap.
- `.noscroll` modifier: `x-trap.noscroll="open"` prevents background scrolling while trapped.
- Use for modals, dialogs, and any keyboard modal state.

## history

`@alpinejs/history` binds `x-data` properties to URL query-string parameters so deep links, back/forward, and refresh preserve state. This package is **alpha** (3.0.0-alpha.0) — in this tag the monorepo folder is a stub; development lives in the Livewire repo. Basic shape:

```html
<div x-data="{ tab: $persist('first'), items: [] }" x-history>
```

With the plugin, properties referenced by the history system sync to the query string (`?tab=first`). Treat as experimental; prefer `@alpinejs/persist` or manual `URLSearchParams` for production.

## intersect

`@alpinejs/intersect` wraps IntersectionObserver — react when elements enter/leave the viewport (lazy loading, infinite scroll, view tracking, scroll animations).

```html
<div x-data="{ shown: false }">
    <div x-intersect="shown = true" x-show="shown">I'm in the viewport!</div>
</div>
```

Forms:

- `x-intersect="expr"` — run when the element intersects (default: any pixel visible).
- `x-intersect:enter="expr"` — explicit enter alias.
- `x-intersect:leave="expr"` — run when it leaves; by default fires only when the **whole** element is out of view — add `.full` to fire when only **part** is out.

Modifiers (map to `IntersectionObserver` options):

- `.once` — fire only the first time.
- `.half` — threshold 0.5.
- `.full` — threshold 0.99.
- `.threshold.50` — custom 0–100 percentage.
- `.margin` — custom `rootMargin`, CSS-margin style: one value for all sides (`.margin.200px`), or up to four for top/right/bottom/left (`.margin.10%.25px.25.25px`). Positive expands the boundary (pre-load), negative shrinks it (`.margin.-100px` fires only 100 px past the edge).
- `.parent` — observe against the element's parent instead of the viewport.

## mask

`@alpinejs/mask` formats text input as the user types (phone, credit card, money, dates).

```html
<input x-mask="99/99/9999" placeholder="MM/DD/YYYY">
<input x-mask="(999) 999-9999" placeholder="Phone">
```

Wildcards: `9` = digit only, `a` = alpha only, `*` = any character. Non-wildcard characters (slashes, dashes, parens) are inserted automatically.

Dynamic masks with `x-mask:dynamic` — the current value is available as `$input`:

```html
<input x-mask:dynamic="
    $input.startsWith('34') || $input.startsWith('37')
        ? '9999 999999 99999'
        : '9999 9999 9999 9999'
">
```

A function reference works too: `x-mask:dynamic="creditCardMask"` with `function creditCardMask(input) {...}`.

Built-in money mask: `x-mask:dynamic="$money($input)"` — optional args `$money($input, decimalSep, thousandSep, precision)`, e.g. `$money($input, ',', '.', 4)`.

## morph

`@alpinejs/morph` patches a live DOM node toward a new HTML string **while preserving Alpine state, input values, and focus** — the Livewire/LiveView pattern.

```js
Alpine.morph(el, newHtml, options)

let el = document.querySelector('#app')
Alpine.morph(el, `
    <div>
        <input x-model="message">
        <span x-text="message"></span>
    </div>
`)
```

`options` lifecycle hooks:

| Option | Called |
|---|---|
| `updating(el, toEl, childrenOnly, skip)` | Before patching `el` against template `toEl`; `skip()` aborts this node, `childrenOnly()` patches children only |
| `updated(el, toEl)` | After patching |
| `removing(el, skip)` / `removed(el)` | Before/after removing a live node |
| `adding(el, skip)` / `added(el)` | Before/after adding a new node |
| `key(el)` | Node keying function (default: the element's `key` attribute) |
| `lookahead` | Boolean; enables lookahead so a node slated for removal can be **moved** to a later position instead of recreated |

Notes:

- Preserve inputs across morphs by giving repeated nodes stable `key` attributes (or a custom `options.key`).
- `Alpine.morphBetween(startMarker, endMarker, newHtml, options)` morphs the region between two sentinel markers (used for partial updates).
- New/changed elements are automatically initialized by Alpine after the patch.

## navigate

`@alpinejs/navigate` (3.10.2) adds SPA-like navigation — client-side page transitions with history push/replace, scroll restoration, and progress bar (nprogress). In this tag the monorepo folder is a stub; development lives in the Livewire repo. It integrates `history.pushState`/`replaceState` with full-page fetches and preserves Alpine state where possible. Use it for SPA feel on server-rendered apps; pin the npm version.

## persist

`@alpinejs/persist` stores `x-data` values in localStorage across page loads (filters, active tabs, settings).

```html
<div x-data="{ count: $persist(0) }">
    <button x-on:click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

- Works with primitives, arrays, and objects.
- Values are stored in localStorage under `_x_<propertyName>` (the `_x_` prefix is Alpine's namespace).
- **Type changes are sticky** — if the property changes type (e.g. number → object), clear localStorage or rename the key, or the next load will misparse the stored JSON.

Modifiers (method calls on the `$persist(...)` value):

- `.as('key')` — custom storage key: `$persist(0).as('other-count')`.
- `.using(sessionStorage)` — use sessionStorage instead of localStorage.
- `.using(window.cookieStorage)` — any object with `getItem`/`setItem` (custom storages, cookies, IndexedDB adapters).

In `Alpine.data` providers: `Alpine.data('form', () => ({ draft: $persist({}) }))` — persisting there keeps state across full page loads.

## resize

`@alpinejs/resize` wraps ResizeObserver.

```html
<div x-data="{ width: 0, height: 0 }"
     x-resize="width = $width; height = $height">
    Width: <span x-text="width"></span>
</div>
```

`$width` and `$height` are injected into the expression. `.document` modifier observes the whole document instead of the element.

## sort

`@alpinejs/sort` drag-to-reorder children, built on SortableJS.

```html
<ul x-sort>
    <li x-sort:item>foo</li>
    <li x-sort:item>bar</li>
</ul>
```

- `x-sort` on the container, `x-sort:item` on each draggable child.
- **Handler**: pass a callback to `x-sort` — it receives `$item` (the item's key from `x-sort:item="1"`) and `$position` (new index, 0-based), or as function args: `x-sort="(item, position) => saveOrder(item, position)"`. Use it to persist the new order server-side.
- **Groups**: `x-sort:group="todos"` on multiple containers lets items drag between them (Kanban). When moving between groups, only the destination list's handler fires.
- **Handles**: `x-sort:handle` restricts dragging to a specific child element (the rest stays clickable).
- **Ignore**: `x-sort:ignore` on interactive descendants (buttons, links) stops them from initiating drags.
