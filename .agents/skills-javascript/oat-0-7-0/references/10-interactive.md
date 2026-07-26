---
title: Interactive Components
---

# Interactive Components

## Dialog

Native `<dialog>` element, zero JavaScript needed. Uses `commandfor` and `command` attributes.

### Basic Dialog

```html
<button commandfor="my-dialog" command="show-modal">Open Dialog</button>

<dialog id="my-dialog">
  <form method="dialog">
    <header>
      <h3>Dialog Title</h3>
      <p>Description text.</p>
    </header>
    <div>
      <p>Dialog content goes here.</p>
      <p>Click outside or press Escape to close.</p>
    </div>
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

### Dialog with Form Fields

```html
<button commandfor="form-dialog" command="show-modal">Edit</button>

<dialog id="form-dialog">
  <form method="dialog">
    <header>
      <h3>Edit User</h3>
    </header>
    <div class="vstack">
      <label>Name <input name="name" required></label>
      <label>Email <input name="email" type="email"></label>
    </div>
    <footer>
      <button type="button" commandfor="form-dialog" command="close" class="outline">Cancel</button>
      <button value="save">Save</button>
    </footer>
  </form>
</dialog>
```

### Handling Return Value

```js
const dialog = document.getElementById('my-dialog');
dialog.addEventListener('close', () => {
  console.log(dialog.returnValue); // "confirm" or "save"
});
```

Or inline:

```html
<dialog id="my-dialog" onclose="console.log(this.returnValue)">
```

### Dialog Commands

| Command | Purpose |
|---|---|
| `command="show-modal"` | Open dialog as modal (with backdrop) |
| `command="close"` | Close the dialog |
| `command="toggle"` | Toggle open/closed (default) |
| `commandfor="id"` | Target the element with this id |

### Dialog Features

- Focus trapping (native browser behavior)
- Escape key closes dialog
- Click outside backdrop closes dialog
- Animated open/close with scale + fade
- Backdrop fade animation
- `z-index: var(--z-modal)` (200)

### Safari Polyfill

Oat bundles a `commandfor` polyfill for Safari. The polyfill handles:
- `commandfor` + `command="show-modal"` → `dialog.showModal()`
- `commandfor` + `command="close"` → `dialog.close()`
- `commandfor` + `command="toggle"` → toggle based on `dialog.open`

### Dialog Touch Shim

A touch event handler prevents dialog backdrop clicks from bleeding through on touch devices.

## Accordion

Native `<details>`/`<summary>` — no JavaScript needed.

### Basic Accordion

```html
<details>
  <summary>Section 1</summary>
  <p>Content for section 1.</p>
</details>

<details>
  <summary>Section 2</summary>
  <p>Content for section 2.</p>
</details>
```

Adjacent `<details>` elements stack with shared borders (no gap between them).

### Accordion in Sidebar

```html
<details open>
  <summary>Settings</summary>
  <ul>
    <li><a href="#">General</a></li>
    <li><a href="#">Security</a></li>
  </ul>
</details>
```

Inside sidebar nav, accordions have no border and the summary has left-aligned chevron.

### Accordion Styling

- Bordered container with `border-radius: var(--radius-medium)`
- Chevron arrow (SVG mask) that rotates 180° when open
- Hover background on summary
- Content padding: `var(--space-4)`
- Adjacent details: shared borders (no radius on touching corners)

## TagInput

`<ot-taginput>` Web Component for managing a list of tags.

### Basic TagInput

```html
<ot-taginput value="apple, mango">
  <input placeholder="Add tags..." maxlength="20" />
</ot-taginput>
```

- Type a word, press `Enter` or `,` to add as a tag
- Press `Backspace` on empty input to remove the last tag
- Click `×` on a tag to remove it
- Initial tags from `value` attribute (comma-separated)

### With Autocomplete

```html
<ot-taginput id="taginput-demo">
  <input list="fruit-list" placeholder="Type a fruit" oninput="tagAutoComplete(this)">
  <datalist id="fruit-list"></datalist>
</ot-taginput>

<script>
function tagAutoComplete(el) {
  const items = ['Apple', 'Banana', 'Cherry', 'Mango', 'Melon'];
  el.list.replaceChildren(...items
    .filter(f => f.toLowerCase().startsWith(el.value.toLowerCase()))
    .map(f => new Option(f, f)));
}
</script>
```

### Programmatic API

```js
const el = document.getElementById('tags');

// Read
console.log(el.value);  // ['apple', 'mango']

// Set (replace all)
el.value = ['apple', 'mango'];

// Append
el.value = [...el.value, 'kiwi'];

// Clear
el.value = [];

// With objects (toString() for display)
class Fruit {
  constructor(id, name) { this.id = id; this.name = name; }
  toString() { return this.name; }
}
el.value = [new Fruit(1, 'Apple'), new Fruit(2, 'Banana')];

// Listen for changes
el.addEventListener('input', e => {
  console.log(e.detail); // Current tag array
});
```

### TagInput Properties

| Property | Description |
|---|---|
| `value` attribute | Comma-separated initial tags |
| `.value` property | Array of tags (strings or objects) |
| `input` event | Dispatched on add/remove, `detail` = current tags |
| `.input` property | The child `<input>` element |

### Object Tags

Tags can be objects with `toString()` — the display shows the string, but `.value` retains the full object:

```js
const opt = new Option('Apple');
opt.data = { id: 1, name: 'Apple' };
// Tag shows "Apple" but .value returns { id: 1, name: 'Apple' }
```

## Upload

`<ot-upload>` Web Component for drag-and-drop file uploads.

### Basic Upload

```html
<ot-upload>
  <input type="file" name="files" multiple accept="image/*" hidden />
  <button type="button">Choose files</button>
  <div data-files>
    <small data-hint>Drop files here or click to choose</small>
  </div>
</ot-upload>
```

### With Styled Upload Area

```html
<ot-upload>
  <div data-field class="vstack">
    <input type="file" name="attachments" multiple hidden />
    <strong>Attachments</strong>
    <button type="button" class="ghost" aria-label="Choose files">
      <!-- Upload icon SVG -->
    </button>
    <div data-files>
      <small data-hint>Drop files here or click to choose</small>
    </div>
  </div>
</ot-upload>
```

### Events

```js
const upload = document.querySelector('ot-upload');
const input = upload.querySelector('input[type="file"]');

input.addEventListener('change', () => {
  console.log(input.files); // FileList
});
```

The native `change` event fires on picker selection, drop, and file removal.

### Upload Behavior

- **Click**: Opens file picker
- **Drag over**: Highlights with `data-drag` attribute
- **Drop**: Adds dropped files
- **Badge ×**: Removes the file from the selection
- **Multiple**: Respects `multiple` attribute on input; single file if absent
- **Accept**: Respects `accept` attribute on input

### Upload Structure

| Element | Purpose |
|---|---|
| `<input type="file">` | Native file input (can be hidden) |
| `<button>` | Click target to open picker |
| `[data-files]` | Container for file name badges |
| `[data-hint]` | Placeholder text shown when no files selected |
