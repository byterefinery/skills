# Oat JS Components & APIs

JS-powered components and the global `ot` namespace. All require `oat.min.js`. WebComponents are registered as `ot-*` custom elements; the only thing on the global `ot` object is the toast API.

## Table of Contents

- [ot-dropdown](#ot-dropdown)
- [ot-tabs](#ot-tabs)
- [ot-taginput](#ot-taginput)
- [ot-upload](#ot-upload)
- [Tooltip](#tooltip)
- [Sidebar layout](#sidebar-layout)
- [ot.toast](#ottost)

---

## ot-dropdown

Dropdown menus and popovers using the native popover API. Wrap in `<ot-dropdown>`; the trigger uses `popovertarget="<id>"` and the menu uses `popover`. Menu items use `role="menuitem"`. Supports keyboard navigation.

```html
<ot-dropdown>
  <button popovertarget="demo-menu" class="outline">
    Options
    <!-- chevron svg -->
  </button>
  <menu popover id="demo-menu">
    <button role="menuitem" class="ghost">Profile</button>
    <button role="menuitem" class="ghost" popovertarget="demo-menu" popovertargetaction="hide">
      Click to close
    </button>
    <a href="#" role="menuitem" class="unstyled">Link</a>
    <hr>
    <button role="menuitem" data-variant="danger" class="ghost">Delete</button>
  </menu>
</ot-dropdown>
```

### Popover card

The same wrapper shows any popover element (e.g. a confirmation card):

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

## ot-tabs

Tabbed interface. Wrap tab buttons and panels in `<ot-tabs>`; use `role="tablist"`, `role="tab"`, and `role="tabpanel"`. Optionally add `data-anchor="<key>"` to `<ot-tabs>` and give each `role="tab"` an `id` to deep-link the URL hash fragment to the active tab.

```html
<ot-tabs data-anchor="tab-settings">
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab" id="password">Password</button>
    <button role="tab" id="notifications">Notifications</button>
  </div>
  <div role="tabpanel">
    <h3>Account Settings</h3>
    <p>Manage your account information here.</p>
  </div>
  <div role="tabpanel">
    <h3>Password Settings</h3>
    <p>Change your password here.</p>
  </div>
  <div role="tabpanel">
    <h3>Notification Settings</h3>
    <p>Configure your notification preferences.</p>
  </div>
</ot-tabs>
```

## ot-taginput

Type words and press Enter or comma to turn them into tags. Supports autocomplete via `<datalist>`.

```html
<ot-taginput value="apple, mango">
  <input placeholder="Add tags ..." maxlength="15" />
</ot-taginput>

<ot-taginput value="apple, mango" disabled>
  <input placeholder="Disabled taginput ..." maxlength="15" />
</ot-taginput>
```

### Autocomplete

Give the inner `<input>` a `list` attribute pointing to a `<datalist>`; populate the datalist in the input's `oninput`/`onfocus` handler. A suggestion can be a plain string or an object (attach the object via `option.data`; give objects a `toString()` for display text).

```js
function tagInputAutoComplete(el) {
  const items = ["Apple", "Apricot", new Fruit(1, "Banana")]; // mix strings + objects
  el.list.replaceChildren(
    ...items
      .filter((f) => String(f).toLowerCase().startsWith(el.value.toLowerCase()))
      .map((f) => {
        const o = new Option(f);
        o.data = f; // attach the object
        return o;
      })
  );
}
```

### Custom suggestions

To use a non-datalist control, remove the input's `list` attribute and call `.add(value)` when an item is selected.

### Programmatic read/write

Mutate the component's `value` property. A standard bubbling `input` event fires whenever a tag is added or removed.

| API | Description |
|---|---|
| `el.value` | Array of tags (strings or objects). Setting it does **not** emit `input`. |
| `el.disabled` | Boolean prop for the `disabled` attribute. |
| `el.add(value)` | Add a string or object tag. Emits `input` unless empty or a duplicate. |
| `option.data` | Optional object attached to a `<datalist>` `<option>`. |
| `input` event | Dispatched (bubbles) on add/remove; `e.detail` is the current tag array. |

```js
const el = document.getElementById("tags");
el.value = ["apple", "mango"];      // replace all (silent)
el.value = [...el.value, "kiwi"];   // append
el.value = [];                       // clear
el.add("grape");                     // emits input
console.log(el.value);
el.addEventListener("input", (e) => console.log(e.detail)); // current tag array
```

Pass a DOM element or text node to `.add()` / `.value` to render it inside the badge. Object tags are deduplicated by strict equality (`===`).

## ot-upload

Tiny click + drag/drop file uploader. Wrap a native `<input type="file">` in `<ot-upload>`. A `change` event fires on selection, drop, and removal.

```html
<ot-upload>
  <div data-field class="vstack">
    <input type="file" name="attachments" multiple hidden />
    <strong>Attachments</strong>
    <button type="button" class="ghost" aria-label="Choose files">
      <!-- upload svg -->
    </button>
    <div data-files>
      <small data-hint>Drop files here or click to choose</small>
    </div>
  </div>
</ot-upload>
```

## Tooltip

Smooth tooltips built on the standard `title` attribute, with a transition. Default placement is `top`; position with `data-tooltip-placement="top|bottom|left|right"`.

```html
<button title="Save your changes">Save</button>
<a href="#" title="View your profile">Profile</a>
<button title="Below" data-tooltip-placement="bottom">Bottom</button>
```

**Replaced elements** (`<img>`, `<iframe>`, etc.) need to be wrapped in a parent that carries the `title`:

```html
<span title="Images need a parent with title">
  <img src="/logo.svg" height="32" />
</span>
```

## Sidebar layout

Responsive admin-dashboard layout: sticky sidebar, optional topnav, collapsible sections. Put `data-sidebar-layout` on a container (typically `<body>`) with `<aside data-sidebar>` for the sidebar and `<main>` for content. The sidebar stays sticky while the main content scrolls.

- Mobile: the sidebar becomes a slide-out overlay toggled by a `[data-sidebar-toggle]` button.
- `data-sidebar-layout="always"` keeps the toggle visible and collapses the sidebar at all widths.
- `--sidebar-width` CSS variable adjusts the width globally.
- `data-topnav` on a `<nav>`/`<header>` adds a full-width sticky top bar (sidebar sits below it).
- The layout gets `data-sidebar-open` applied when the sidebar is open.

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | container (usually `<body>`) | Grid wrapper (sidebar + main) |
| `data-sidebar-layout="always"` | container | Always-collapsible sidebar |
| `data-topnav` | `<nav>`/`<header>` | Optional full-width top bar |
| `data-sidebar` | `<aside>` | Sticky sidebar |
| `data-sidebar-toggle` | `<button>` | Toggles/collapses the sidebar |

Typical structure:

```html
<body data-sidebar-layout>
  <header data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </header>
  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#home" aria-current="page">Home</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#general">General</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer><button class="outline small">Logout</button></footer>
  </aside>
  <main>Main page content.</main>
</body>
```

## ot.toast

Notification toasts with placement and stacking. Multiple toasts stack to avoid clutter; hovering expands them.

```js
ot.toast(message, title?, options?)
```

Options:

| Option | Default | Description |
|---|---|---|
| `variant` | `'info'` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | `top-left`, `top-center`, `bottom-left`, `bottom-center`, `bottom-right` |
| `duration` | `4000` | Auto-dismiss in ms; `0` = persistent |

```js
ot.toast("Action completed successfully", "All good", { variant: "success" });
ot.toast("Something went wrong", "Oops", { variant: "danger", placement: "top-left" });
ot.toast("New notification", "For your attention", { placement: "top-center" });
```

### Custom markup — `ot.toast.el(element, options?)`

Show a toast with custom HTML. The element is **cloned** before display, so templates can be reused. Build the toast as `<output class="toast" data-variant="...">` with an `<h6 class="toast-title">`.

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000 })">
  Toast with action
</button>
```

Dynamic element:

```js
const el = document.createElement("output");
el.className = "toast";
el.setAttribute("data-variant", "warning");
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content here</p>';
ot.toast.el(el);
```

### Clearing

```js
ot.toast.clear();            // clear all
ot.toast.clear("top-right"); // clear a specific placement
```
