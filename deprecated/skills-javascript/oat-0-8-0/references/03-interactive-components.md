# Oat Interactive Components Reference

Dynamic components and loading/feedback elements. WebComponents (`ot-*`) require `oat.min.js`; the rest are CSS-only.

## Contents

- [Accordion](#accordion)
- [Dialog](#dialog)
- [Dropdown and Popover](#dropdown-and-popover)
- [Tabs](#tabs)
- [Switch](#switch)
- [TagInput](#taginput)
- [Toast](#toast)
- [Tooltip](#tooltip)
- [Upload](#upload)
- [Spinner](#spinner)
- [Skeleton](#skeleton)
- [Meter](#meter)
- [Progress](#progress)

## Accordion

Collapsible sections using native `<details>` and `<summary>` elements. No JS required. The `name` attribute groups items so only one stays open at a time (radio behavior).

```html
<details>
  <summary>What is Oat</summary>
  <p class="p-4">Oat is a minimal, semantic-first UI component library with zero dependencies.</p>
</details>

<details name="grouped">
  <summary>This is grouped with the next one</summary>
  <p class="p-4">Using the name attribute groups items like radio.</p>
</details>
<details name="grouped">
  <summary>This is grouped with the previous one</summary>
  <p class="p-4">Only one of the group opens at a time.</p>
</details>
```

## Dialog

Fully semantic, zero-JavaScript dynamic dialog with `<dialog>` (the JS only polyfills `command`/`commandfor` for Safari). Use `commandfor` + `command="show-modal"` on a trigger element to open a target dialog. Focus trapping, z placement, and keyboard shortcuts work out of the box.

```html
<button commandfor="demo-dialog" command="show-modal">Open dialog</button>
<dialog id="demo-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Title</h3>
      <p>This is a dialog description.</p>
    </header>
    <div>
      <p>Dialog content goes here. You can put any HTML inside.</p>
      <p>Click outside or press Escape to close.</p>
    </div>
    <footer>
      <button type="button" commandfor="demo-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

### With form fields

Forms inside dialogs work naturally. Use `command="close"` on cancel buttons:

```html
<button commandfor="demo-dialog-form" command="show-modal">Open form dialog</button>
<dialog id="demo-dialog-form">
  <form method="dialog">
    <header><h3>Edit form</h3></header>
    <div class="vstack">
      <label>Name <input name="name" required></label>
      <label>Email <input name="email" type="email"></label>
    </div>
    <footer>
      <button type="button" commandfor="demo-dialog-form" command="close" class="outline">Cancel</button>
      <button value="save">Save</button>
    </footer>
  </form>
</dialog>
```

### Handling the return value

Listen to the native `close` event to get the button `value`:

```javascript
const dialog = document.querySelector("#demo-dialog");
dialog.addEventListener('close', (e) => {
  console.log(dialog.returnValue); // "confirm"
});
```

Or inline: `<dialog id="my-dialog" onclose="console.log(this.returnValue)">`.

## Dropdown and Popover

Wrap in `<ot-dropdown>`. Put `popovertarget` on the trigger and `popover` on the target. If the target is a dropdown `<menu>`, items use `role="menuitem"`. The component handles positioning (flips on viewport overflow), scroll/resize tracking, focus management, and roving keyboard navigation (ArrowUp/ArrowDown, Home/End).

```html
<ot-dropdown>
  <button popovertarget="demo-menu" class="outline">
    Options
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6" /></svg>
  </button>
  <menu popover id="demo-menu">
    <button role="menuitem" class="ghost">Profile</button>
    <button role="menuitem" class="ghost">Help</button>
    <a href="#" role="menuitem" class="unstyled">Link</a>
    <hr>
    <button role="menuitem" data-variant="danger" class="ghost">Delete</button>
  </menu>
</ot-dropdown>
```

### Popover

`<ot-dropdown>` can also show arbitrary popover elements (any `popover` element, e.g. a card) — use `popovertargetaction="hide"` on buttons that close it:

```html
<ot-dropdown>
  <button popovertarget="demo-confirm" class="outline">Confirm</button>
  <article class="card" popover id="demo-confirm">
    <header>
      <h4>Are you sure?</h4>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button class="outline small" popovertarget="demo-confirm">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="demo-confirm">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

## Tabs

Wrap tab buttons and panels in `<ot-tabs>`. Use `role="tablist"`, `role="tab"`, and `role="tabpanel"` (panels are direct children of `<ot-tabs>`, not of the tablist). Keyboard: ArrowLeft/ArrowRight. The component wires ARIA attributes, emits `ot-tab-change` (`{ index, tab }`), and exposes read/write `.activeIndex`.

Optionally add `data-anchor="<key>"` to `<ot-tabs>` and give each `role="tab"` an `id` to deep-link the active tab in the URL hash (`#key=tab-id`, written via `history.replaceState`, preserved across other hash params). Initial selection order: hash > `aria-selected="true"` > first tab.

```html
<ot-tabs data-anchor="tab-settings">
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab" id="password">Password</button>
    <button role="tab" id="notifications">Notifications</button>
  </div>
  <div role="tabpanel">
    <h3>Account Settings</h3>
  </div>
  <div role="tabpanel">
    <h3>Password Settings</h3>
  </div>
  <div role="tabpanel">
    <h3>Notification Settings</h3>
  </div>
</ot-tabs>
```

## Switch

Toggle switches: add `role="switch"` to a checkbox. Native HTML, no JS required.

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked disabled> Disabled on
</label>
```

## TagInput

Use `<ot-taginput>` with a single child `<input>`. Type a word and press Enter or comma to add it as a tag. Backspace on an empty input removes the last tag. Clicking a tag's `×` removes it.

```html
<ot-taginput value="apple, mango">
  <input placeholder="Add tags ..." maxlength="15" />
</ot-taginput>

<ot-taginput value="apple, mango" disabled>
  <input placeholder="Disabled taginput ..." maxlength="15" />
</ot-taginput>
```

### Autocomplete

Give the `<input>` a `list` attribute pointing at a `<datalist>`, then populate the datalist from the input's native `oninput`/`onfocus` handlers. A suggestion item can be a plain string or an object; attach the object to its `<option>` via `option.data` (selecting it creates a tag holding the object).

```html
<ot-taginput id="taginput-demo">
  <input list="fruit-list" placeholder="Type a fruit name" oninput="tagInputAutoComplete(this)" />
  <datalist id="fruit-list"></datalist>
</ot-taginput>

<script>
class Fruit {
  constructor(id, name) { this.id = id; this.name = name; }
  toString() { return this.name; }   // display text
}

function tagInputAutoComplete(el) {
  const fruits = ['Apple', 'Apricot', new Fruit(1, 'Banana'), 'Mango'];
  el.list.replaceChildren(...fruits
    .filter(f => String(f).toLowerCase().startsWith(el.value.toLowerCase()))
    .map(f => {
      const o = new Option(f);
      o.data = f;
      return o;
    }));
}
</script>
```

### Programmatic read and write

Mutate the component's `value` property (an array). A standard `input` event is dispatched (and bubbles) whenever a tag is added or removed; `e.detail` is the current tag array.

```javascript
const el = document.getElementById('tags');
el.value = ['apple', 'mango'];     // replace all
el.value = [...el.value, 'kiwi'];  // append
el.value = [];                     // clear
el.addEventListener('input', e => console.log(e.detail));
```

### Options

| Property | Description |
|---|---|
| `<input>` | Child input field where the user types |
| `value` (attr) | Comma-separated list of initial tags |
| `disabled` (attr) | Disables the control like a native input |
| `.value` (prop) | Array of tags (strings or objects); setting it does not emit `input` |
| `.disabled` (prop) | Boolean property for the `disabled` attribute |
| `option.data` | Optional object attached to a datalist `<option>` |
| `input` event | Dispatched (bubbles) on add/remove; `detail` is the current tag array |

## Toast

Show toast notifications with `ot.toast(message, title?, options?)`.

```html
<button onclick="ot.toast('Action completed successfully', 'All good', { variant: 'success' })">Success</button>
<button onclick="ot.toast('Something went wrong', 'Oops', { variant: 'danger', placement: 'top-left' })">Danger</button>
<button onclick="ot.toast('New notification', 'For your attention', { placement: 'top-center' })">Info</button>
```

### Placement

```js
ot.toast('Top left', '', { placement: 'top-left' })
ot.toast('Top center', '', { placement: 'top-center' })
ot.toast('Top right', '', { placement: 'top-right' })   // default
ot.toast('Bottom left', '', { placement: 'bottom-left' })
ot.toast('Bottom center', '', { placement: 'bottom-center' })
ot.toast('Bottom right', '', { placement: 'bottom-right' })
```

### Options

| Option | Default | Description |
|---|---|---|
| `variant` | `'info'` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | Position on screen |
| `duration` | `4000` | Auto-dismiss in ms (0 = persistent) |

Toasts stack per placement container and pause their countdown while hovered.

### Custom markup

Use `ot.toast.el(element, options?)` for custom HTML content. The element is cloned before display, so templates can be reused. Use an `<output class="toast">` root; a child with `data-close` is styled as a right-aligned dismiss button.

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>
```

```js
// From a template
ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000, placement: 'bottom-center' })

// Or a dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content here</p>';
ot.toast.el(el);
```

### Clearing toasts

```js
ot.toast.clear()              // clear all
ot.toast.clear('top-right')   // clear one placement
```

## Tooltip

Use the standard `title` attribute on any element to render a styled tooltip with a smooth transition. `oat.min.js` converts `title` → `data-tooltip` (+ `aria-label`) on load and for dynamically added elements (MutationObserver). `data-tooltip-placement="top|bottom|left|right"` positions the tooltip; default is `top`. Replaced elements (`<img>`, `<iframe>`, …) need to be wrapped in a parent that carries the `title`.

```html
<button title="Save your changes">Save</button>
<button title="Delete this item" data-variant="danger">Delete</button>
<span title="Images need a parent with title"><img src="/logo.svg" height="32" /></span>
<button title="Below" data-tooltip-placement="bottom">Bottom</button>
```

## Upload

Wrap a native `<input type="file">` in `<ot-upload>`. Clicking the component opens the picker; files can also be dropped onto it. The `change` event fires (bubbling, on the inner input) on selection, drop, and removal. Selected files render as removable badges in the optional `[data-files]` element.

```html
<ot-upload>
  <div data-field class="vstack">
    <input type="file" name="attachments" multiple hidden />
    <strong>Attachments</strong>

    <button type="button" class="ghost" aria-label="Choose files">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 16V4m0 0 4 4m-4-4-4 4" /><path d="M20 16v4H4v-4" /></svg>
    </button>

    <div data-files>
      <small data-hint>Drop files here or click to choose</small>
    </div>
  </div>
</ot-upload>
```

## Spinner

Use `aria-busy="true"` on any element to show a loading spinner. Size with `data-spinner="small|large"`; `data-spinner="overlay"` dims the container's contents and overlays the spinner centered (children get `pointer-events: none` while busy).

```html
<div class="hstack" style="gap: var(--space-8)">
  <div aria-busy="true" data-spinner="small"></div>
  <div aria-busy="true"></div>
  <div aria-busy="true" data-spinner="large"></div>
  <button aria-busy="true" data-spinner="small" disabled>Loading</button>
</div>
```

### Overlay

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <header>
    <h3>Card Title</h3>
    <p>Card description goes here.</p>
  </header>
  <p>This content is dimmed and unclickable while busy.</p>
  <footer class="hstack gap-2">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

## Skeleton

Loading placeholders with a shimmer animation. Use `.skeleton` with `role="status"` (both are required). `.line` for text rows, `.box` for square image/media placeholders.

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

### Skeleton card

Compose a card-shaped placeholder with `article` + flexbox:

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-6);">
  <div role="status" class="skeleton box"></div>
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 60%"></div>
  </div>
</article>
```

## Meter

Use `<meter>` for a value within a known range. The browser colours it based on `low`/`high`/`optimum`.

```html
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

## Progress

Use the native `<progress>` element.

```html
<progress value="60" max="100"></progress>
<progress value="30" max="100"></progress>
```
