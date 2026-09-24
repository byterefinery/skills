# JS Web Components

Dynamic components built as Custom Elements. They extend `OtBase` which provides lifecycle management, event handling, keyboard navigation helpers, and a custom event emitter.

## OtBase (internal)

Base class for all Web Components. Provides:

- `connectedCallback()` / `disconnectedCallback()` — lifecycle hooks
- `handleEvent(event)` — central event handler, calls `on{eventType}` method
- `keyNav(event, idx, len, prevKey, nextKey, homeEnd)` — roving keyboard navigation
- `emit(name, detail)` — dispatch a custom event (bubbles, composed, cancelable)
- `uid()` — generate unique ID string

## Dropdown (`<ot-dropdown>`)

Positioned dropdown menus with keyboard navigation and ARIA management.

```html
<ot-dropdown>
  <button popovertarget="menu-id" aria-haspopup="true">Options</button>
  <menu popover id="menu-id">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <hr>
    <button role="menuitem" data-variant="danger">Logout</button>
  </menu>
</ot-dropdown>
```

### Structure

- `<ot-dropdown>` — wrapper
- `[popovertarget]` — trigger button (must reference the menu's ID)
- `[popover]` — the dropdown panel (must have an `id`)
- `[role="menuitem"]` — menu items (can be `<button>`, `<a>`, etc.)
- `<hr>` — separator between groups

### Features

- Auto-positioning relative to trigger, with viewport overflow detection (flips above if needed)
- Keyboard navigation: ArrowUp/ArrowDown/Home/End
- Focus management: first item focused on open, focus returns to trigger on close
- ARIA: `aria-expanded` toggled on trigger automatically
- Scroll/resize repositioning

### Popover variant

Use any element as the popover target:

```html
<ot-dropdown>
  <button popovertarget="confirm">Confirm</button>
  <article class="card" popover id="confirm">
    <h4>Are you sure?</h4>
    <p>This action cannot be undone.</p>
    <footer>
      <button class="outline small" popovertarget="confirm">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

## Tabs (`<ot-tabs>`)

Tabbed interface with keyboard navigation and optional deep-linking.

```html
<ot-tabs data-anchor="tab">
  <div role="tablist">
    <button role="tab" id="general">General</button>
    <button role="tab" id="security">Security</button>
    <button role="tab" id="billing">Billing</button>
  </div>
  <div role="tabpanel">General settings content</div>
  <div role="tabpanel">Security settings content</div>
  <div role="tabpanel">Billing settings content</div>
</ot-tabs>
```

### Deep-linking

`data-anchor="key"` syncs the active tab's `id` into the URL hash:

```
#tab=security
```

Tabs without `id` are auto-assigned `ot-tab-{uid}`. Only tabs with explicit IDs are used in the hash.

### Properties

- `.activeIndex` — get/set the active tab index (0-based)

### Events

- `ot-tab-change` — dispatched on tab switch. `detail = { index, tab }`

```js
tabs.addEventListener('ot-tab-change', e => {
  console.log('Tab changed to index', e.detail.index);
});
```

### Keyboard navigation

ArrowLeft/ArrowRight cycles through tabs.

## TagInput (`<ot-taginput>`)

Type words and press Enter or comma to create tags. Supports autocomplete via `<datalist>`.

```html
<ot-taginput value="apple, mango">
  <input placeholder="Add tags..." maxlength="20" />
</ot-taginput>
```

### Autocomplete

```html
<ot-taginput id="tags">
  <input list="tag-list" placeholder="Type a fruit" oninput="autoComplete(this)">
  <datalist id="tag-list"></datalist>
</ot-taginput>
```

```js
function autoComplete(el) {
  const items = ['Apple', 'Banana', 'Cherry', 'Mango', 'Melon'];
  el.list.replaceChildren(...items
    .filter(f => f.toLowerCase().startsWith(el.value.toLowerCase()))
    .map(f => new Option(f)));
}
```

### Object tags

Tags can be plain strings or objects. Objects are displayed via `toString()`:

```js
class Fruit {
  constructor(id, name) { this.id = id; this.name = name; }
  toString() { return this.name; }
}

// Attach object to option
const opt = new Option('Banana');
opt.data = new Fruit(1, 'Banana');
```

### Programmatic API

```js
const el = document.getElementById('tags');

el.value = ['apple', 'mango'];     // replace all
el.value = [...el.value, 'kiwi'];  // append
el.value = [];                     // clear
console.log(el.value);             // read current tags

el.addEventListener('input', e => {
  console.log(e.detail); // current tag array
});
```

### Attributes

| Attribute | Description |
|---|---|
| `value` | Comma-separated initial tags |
| `.value` | Array of tags (strings or objects) |

### Events

| Event | Description |
|---|---|
| `input` | Dispatched on add/remove. `detail` is current tag array |

## Toast (`window.ot.toast`)

Notification toasts with placement, variants, and auto-dismiss.

### Text toasts

```js
ot.toast('Action completed', 'Success', { variant: 'success' });
ot.toast('Something failed', 'Error', { variant: 'danger', placement: 'top-left' });
ot.toast('Warning message', 'Warning', { variant: 'warning', placement: 'bottom-right' });
ot.toast('Info notification', 'Info');
```

### Options

| Option | Default | Description |
|---|---|---|
| `variant` | `'info'` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | Position on screen |
| `duration` | `4000` | Auto-dismiss ms (0 = persistent) |

### Placements

- `top-left`, `top-center`, `top-right` (default)
- `bottom-left`, `bottom-center`, `bottom-right`

### Custom markup

```js
// From a template element
ot.toast.el(document.querySelector('#my-template'), { duration: 8000 });

// From a dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content</p>';
ot.toast.el(el);
```

The element is cloned before display, so templates can be reused.

### Clearing

```js
ot.toast.clear();              // Clear all toasts
ot.toast.clear('top-right');   // Clear specific placement
```

### Behavior

- Toasts pause auto-dismiss on hover
- Containers auto-created with `popover="manual"`
- Enter/exit animations via CSS transitions
- Stacking: toasts stack vertically within each placement container

## Upload (`<ot-upload>`)

Click and drag/drop file uploader wrapping a native `<input type="file">`.

```html
<ot-upload>
  <input type="file" name="files" multiple accept="image/*" hidden />
  <button type="button">Choose files</button>
  <div data-files>
    <small data-hint>Drop files here or click to choose</small>
  </div>
</ot-upload>
```

### Structure

- `<ot-upload>` — wrapper (auto-gets `.card`, `.vstack`, `.align-center` classes)
- `<input type="file">` — native file input (must be `hidden`)
- `[data-files]` — optional area showing selected file badges
- `[data-hint]` — placeholder text shown when no files selected

### Events

- `change` — fired on picker selection, drop, and file removal. Listen on `<ot-upload>`, not the input.

### Features

- Click anywhere on the component to open file picker
- Drag and drop files onto the component
- Visual feedback with `data-drag` attribute during drag
- File badges with remove (×) button
- Respects `multiple` and `accept` attributes on the file input
