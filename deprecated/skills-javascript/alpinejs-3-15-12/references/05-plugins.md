# Plugins

All plugins follow the same registration pattern. CDN scripts must load BEFORE Alpine core. NPM plugins register before `Alpine.start()`.

## Installation Patterns

### CDN

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/mask@3.15.12/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.12/dist/cdn.min.js"></script>
```

### NPM

```js
import Alpine from 'alpinejs'
import mask from '@alpinejs/mask'
Alpine.plugin(mask)
Alpine.start()
```

---

## Mask (`@alpinejs/mask`)

Format text inputs as the user types (phone numbers, credit cards, dates, money).

### Static Masks

```html
<input x-mask="99/99/9999" placeholder="MM/DD/YYYY">
<input x-mask="(999) 999-9999">
```

Wildcards: `*` (any char), `a` (alpha only), `9` (numeric only).

### Dynamic Masks

```html
<input x-mask:dynamic="$input.startsWith('34') || $input.startsWith('37')
  ? '9999 999999 99999' : '9999 9999 9999 9999'">
```

`$input` contains the current raw input value. Can also reference a function:

```html
<input x-mask:dynamic="creditCardMask">
```

### Money

```html
<input x-mask:dynamic="$money($input)">
<input x-mask:dynamic="$money($input, ',')">          <!-- European: 1.000,00 -->
<input x-mask:dynamic="$money($input, '.', ' ')">    <!-- 1 000.00 -->
<input x-mask:dynamic="$money($input, '.', ',', 4)"> <!-- 4 decimal places -->
```

---

## Intersect (`@alpinejs/intersect`)

Wrapper for Intersection Observer. React when elements enter/leave the viewport.

```html
<div x-data="{ shown: false }" x-intersect="shown = true">
  <div x-show="shown" x-transition>In viewport!</div>
</div>
```

### Variants

```html
<div x-intersect:enter="shown = true">   <!-- alias for x-intersect -->
<div x-intersect:leave="shown = false">  <!-- fires when leaving viewport -->
```

### Modifiers

| Modifier | Description |
|---|---|
| `.once` | Fire only on first intersection |
| `.half` | Threshold 0.5 |
| `.full` | Threshold 0.99 |
| `.threshold.N` | Custom threshold (0-100) |
| `.margin.200px` | Root margin (CSS-like syntax) |

```html
<div x-intersect.threshold.50="shown = true">
<div x-intersect.margin.200px="loaded = true">
<div x-intersect:leave.margin.10%="-25px"="loaded = false">
```

---

## Resize (`@alpinejs/resize`)

Wrapper for Resize Observer. React when element size changes.

```html
<div x-data="{ width: 0, height: 0 }" x-resize="width = $width; height = $height">
  <p x-text="'Width: ' + width + 'px'"></p>
  <p x-text="'Height: ' + height + 'px'"></p>
</div>
```

Magic properties: `$width`, `$height`.

### Modifier

```html
<div x-resize.document="width = $width; height = $height">  <!-- observe document -->
```

---

## Persist (`@alpinejs/persist`)

Persist Alpine state across page loads via localStorage.

```html
<div x-data="{ count: $persist(0) }">
  <button @click="count++">Increment</button>
  <span x-text="count"></span>
</div>
```

Uses property name as localStorage key (prefixed with `_x_`). Works with primitives, arrays, and objects.

### Custom Key

```html
<div x-data="{ count: $persist(0).as('unique-count') }">
```

### Custom Storage

```html
<div x-data="{ count: $persist(0).using(sessionStorage) }">
<div x-data="{ count: $persist(0).using(cookieStorage) }">
```

Custom storage must expose `getItem(key)` and `setItem(key, value)`.

### With Alpine.data

Use regular function (not arrow) for `this` context:

```js
Alpine.data('component', function() {
  return { open: this.$persist(false) }
})
```

### Alpine.$persist Global

```js
Alpine.store('settings', {
  theme: Alpine.$persist('light').as('theme')
})
```

---

## Focus (`@alpinejs/focus`)

Manage focus. Previously called "Trap". Provides `x-trap` and `$focus` magic.

### x-trap

Trap focus within an element (for dialogs, modals).

```html
<div x-data="{ open: false }">
  <button @click="open = true">Open</button>
  <div x-show="open" x-trap="open">
    <input type="text">
    <button @click="open = false">Close</button>
  </div>
</div>
```

Supports nesting — focus returns to previous element when untrapped.

#### Modifiers

| Modifier | Description |
|---|---|
| `.inert` | Add `aria-hidden="true"` to non-trapped content |
| `.noscroll` | Disable page scrolling |
| `.noreturn` | Don't return focus when untrapped |
| `.noautofocus` | Don't auto-focus first element |

```html
<div x-trap.inert.noscroll="open">
```

### $focus Magic

Programmatic focus management.

| Method | Description |
|---|---|
| `$focus.focus(el)` | Focus element |
| `$focus.focusable(el)` | Check if focusable |
| `$focus.focusables()` | Get all focusable elements in scope |
| `$focus.focused()` | Currently focused element |
| `$focus.lastFocused()` | Last focused element |
| `$focus.within(el)` | Scope to element |
| `$focus.first()` | Focus first focusable |
| `$focus.last()` | Focus last focusable |
| `$focus.next()` | Focus next focusable |
| `$focus.previous()` | Focus previous focusable |
| `$focus.getFirst()` / `getLast()` / `getNext()` / `getPrevious()` | Retrieve (don't focus) |
| `$focus.wrap()` | Wrap around for next/previous |
| `$focus.noscroll()` | Prevent scroll on focus |

```html
<div @keydown.right="$focus.wrap().next()" @keydown.left="$focus.wrap().previous()">
  <button>First</button>
  <button>Second</button>
  <button>Third</button>
</div>

<button @click="$focus.within($refs.buttons).first()">Focus First</button>
```

---

## Collapse (`@alpinejs/collapse`)

Smooth height animation for showing/hiding elements. Requires `x-show`.

```html
<div x-data="{ expanded: false }">
  <button @click="expanded = !expanded">Toggle</button>
  <p x-show="expanded" x-collapse>Content...</p>
</div>
```

### Modifiers

| Modifier | Description |
|---|---|
| `.duration.1000ms` | Custom animation duration |
| `.min.50px` | Minimum collapsed height (cut-off instead of full hide) |

---

## Anchor (`@alpinejs/anchor`)

Position elements relative to other elements. Powered by Floating UI.

```html
<div x-data="{ open: false }">
  <button x-ref="button" @click="open = !open">Toggle</button>
  <div x-show="open" x-anchor="$refs.button">Dropdown</div>
</div>
```

Applies `position: absolute` with computed `top`/`left`. Auto-flips when space is insufficient.

### Positioning Modifiers

`.bottom`, `.bottom-start`, `.bottom-end`, `.top`, `.top-start`, `.top-end`, `.left`, `.left-start`, `.left-end`, `.right`, `.right-start`, `.right-end`

```html
<div x-anchor.bottom-start="$refs.button">
```

### Other Modifiers

| Modifier | Description |
|---|---|
| `.fixed` | Use `position: fixed` (escapes overflow containers) |
| `.offset.10` | Pixel offset from reference |
| `.noflip` | Prevent auto-flipping |
| `.no-style` | Don't apply styles; use `$anchor.x` / `$anchor.y` manually |

```html
<div x-anchor.no-style="$refs.button"
  x-bind:style="{ position: 'absolute', top: $anchor.y+'px', left: $anchor.x+'px' }">
```

### Anchor by ID

```html
<div x-anchor="document.getElementById('trigger')">
```

---

## Morph (`@alpinejs/morph`)

Patch DOM with new HTML while preserving Alpine state and browser state.

```js
Alpine.morph(element, newHtmlString)
Alpine.morph(element, newHtmlString, options)
Alpine.morphBetween(startMarker, endMarker, newHtml, options)
```

### Lifecycle Hooks

```js
Alpine.morph(el, newHtml, {
  updating(el, toEl, childrenOnly, skip) { },
  updated(el, toEl) { },
  removing(el, skip) { },
  removed(el) { },
  adding(el, skip) { },
  added(el) { },
  key(el) { return el.id },  // custom key attribute
  lookahead: true,
})
```

### Keys

Add `key` attributes to list items so Morph moves instead of replaces them:

```html
<ul>
  <li key="1">Mark</li>
  <li key="2">Tom</li>
</ul>
```

---

## Sort (`@alpinejs/sort`)

Drag-and-drop reordering. Powered by SortableJS.

```html
<ul x-sort>
  <li x-sort:item>foo</li>
  <li x-sort:item>bar</li>
  <li x-sort:item>baz</li>
</ul>
```

### Sort Handlers

```html
<ul x-sort="handleSort">
  <li x-sort:item="1">foo</li>
  <li x-sort:item="2">bar</li>
</ul>
```

Handler receives `item` (the key from `x-sort:item`) and `position` (new index, 0-based). Also available as magics: `$item`, `$position`.

### Sorting Groups

```html
<ul x-sort x-sort:group="todos">
<ol x-sort x-sort:group="todos">
```

Items can be dragged between lists sharing the same group name.

### Directives

| Directive | Description |
|---|---|
| `x-sort:handle` | Designate drag handle element |
| `x-sort:ignore` | Exclude element from drag initiation |
| `x-sort:config` | Override SortableJS options |

### Modifiers

`.ghost` — show ghost element at original position during drag (styled via `.sortable-ghost` class).

### CSS

Body receives `.sorting` class while dragging. Use `[body:not(.sorting)_&]:hover:border` (Tailwind) to fix Chrome/Safari hover bug during drag.
