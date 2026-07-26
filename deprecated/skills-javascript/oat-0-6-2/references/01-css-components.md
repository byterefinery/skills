# CSS-Only Components

Components that require no JavaScript. Pure CSS styling of semantic HTML.

## Button

`<button>`, `[type=submit]`, `[type=reset]`, `[type=button]`, `a.button`, `::file-selector-button`

### Variants

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button data-variant="danger" class="outline">Danger Outline</button>
<button class="ghost">Ghost</button>
<button disabled>Disabled</button>
```

### Sizes

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
<button class="icon">🔍</button>
<button class="icon small">🔍</button>
<button class="icon large">🔍</button>
```

### Button Group

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

Each `<li>` must contain exactly one button or `a.button`. Borders between buttons are automatic.

---

## Card

`class="card"` on `<article>` or any container.

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Description</p>
  </header>
  <p>Card content.</p>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

---

## Alert

`role="alert"` with optional `data-variant`.

```html
<div role="alert">Default alert</div>
<div role="alert" data-variant="success">Success!</div>
<div role="alert" data-variant="warning">Warning!</div>
<div role="alert" data-variant="error">Error!</div>
<div role="alert" data-variant="danger">Danger!</div>
```

---

## Badge

`class="badge"` with optional `data-variant` and `outline`.

```html
<span class="badge">Default</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
<span class="badge outline">Outline</span>
```

---

## Avatar

`<figure data-variant="avatar">` with `<img>`, `<abbr>`, or text.

### Single

```html
<figure data-variant="avatar" aria-label="Jane Doe">
  <img src="/avatar.jpg" alt="" />
</figure>

<figure data-variant="avatar" aria-label="Jane Doe">
  <abbr title="Jane Doe">JD</abbr>
</figure>
```

### Sizes

```html
<figure data-variant="avatar" class="small">...</figure>
<figure data-variant="avatar">...</figure>
<figure data-variant="avatar" class="large">...</figure>
```

### Group

```html
<figure data-variant="avatar" role="group" aria-label="Team">
  <figure data-variant="avatar"><img src="/a.jpg" alt="" /></figure>
  <figure data-variant="avatar"><img src="/b.jpg" alt="" /></figure>
  <figure data-variant="avatar"><img src="/c.jpg" alt="" /></figure>
</figure>
```

Add `.small` or `.large` to the group for uniform sizing.

---

## Table

`<table>` styled automatically. Wrap in `class="table"` for horizontal scroll on small screens.

```html
<div class="table">
  <table>
    <thead>
      <tr><th>Name</th><th>Email</th><th>Role</th></tr>
    </thead>
    <tbody>
      <tr><td>Alice</td><td>alice@example.com</td><td>Admin</td></tr>
    </tbody>
    <tfoot>
      <tr><th>Name</th><th>Email</th><th>Role</th></tr>
    </tfoot>
  </table>
</div>
```

---

## Accordion

Native `<details>` and `<summary>`. No JS required.

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

### Grouped (only one open at a time)

```html
<details name="group">
  <summary>Option A</summary>
  <p>Content A</p>
</details>
<details name="group">
  <summary>Option B</summary>
  <p>Content B</p>
</details>
```

Adjacent `<details>` elements automatically get joined borders (no gap).

---

## Breadcrumb

Semantic `<nav>` with ordered list.

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-7)">
    <li><a href="#" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#" class="unstyled">Projects</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#" class="unstyled" aria-current="page"><strong>Current</strong></a></li>
  </ol>
</nav>
```

---

## Pagination

Reuses `<menu class="buttons">` with `.small` buttons.

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#" class="button outline small">&larr; Previous</a></li>
    <li><a href="#" class="button outline small">1</a></li>
    <li><a href="#" class="button small" aria-current="page">2</a></li>
    <li><a href="#" class="button outline small">3</a></li>
    <li><a href="#" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

---

## Progress Bar

Native `<progress>` element.

```html
<progress value="60" max="100"></progress>
<progress value="30" max="100"></progress>
```

---

## Meter

Native `<meter>` element with `low`, `high`, `optimum` attributes.

```html
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

Colors: optimum → `--success`, suboptimum → `--warning`, even-less-good → `--danger`.

---

## Spinner

`aria-busy="true"` on any element.

```html
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true" data-spinner="large"></div>
<button aria-busy="true" data-spinner="small" disabled>Loading</button>
```

### Overlay Mode

`data-spinner="overlay"` dims children and overlays spinner on top.

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <h3>Loading content...</h3>
  <p>Content is dimmed while loading.</p>
</article>
```

---

## Skeleton

`class="skeleton"` with `role="status"`.

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

### Skeleton Card

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-6);">
  <div role="status" class="skeleton box"></div>
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 60%"></div>
  </div>
</article>
```

---

## Switch

`<input type="checkbox" role="switch">`.

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked> Enabled
</label>
```

---

## Tooltip

Standard `title` attribute. JS converts to `data-tooltip` for custom styling.

```html
<button title="Save your changes">Save</button>
<button title="Delete" data-tooltip-placement="bottom">Delete</button>
<button title="Left tooltip" data-tooltip-placement="left">Left</button>
<button title="Right tooltip" data-tooltip-placement="right">Right</button>
```

Placements: `top` (default), `bottom`, `left`, `right`.

Replaced elements (`<img>`, `<iframe>`) need a wrapper:

```html
<span title="Image tooltip"><img src="photo.jpg" /></span>
```

---

## Dialog

Native `<dialog>` with `commandfor`/`command` attributes.

```html
<button commandfor="dialog-id" command="show-modal">Open</button>
<dialog id="dialog-id" closedby="any">
  <form method="dialog">
    <header><h3>Title</h3><p>Description</p></header>
    <div>Content</div>
    <footer>
      <button type="button" commandfor="dialog-id" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

### Commands

| Command | Action |
|---|---|
| `show-modal` | Opens dialog modally |
| `close` | Closes dialog |
| `toggle` (default) | Toggles open/closed |

### Dialog Structure

| Element | Styling |
|---|---|
| `dialog > header` | Flex column, padding, heading + description |
| `dialog > div/section/p` | Content area, scrollable, padding |
| `dialog > footer` | Flex row, right-aligned buttons, padding |

### Return Value

```javascript
dialog.addEventListener('close', () => {
  console.log(dialog.returnValue); // button's value attribute
});
```

---

## Typography

All styled automatically:

```html
<h1>Heading 1</h1>  <!-- clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem) -->
<h2>Heading 2</h2>  <!-- clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem) -->
<h3>Heading 3</h3>  <!-- clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem) -->
<h4>Heading 4</h4>  <!-- clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem) -->
<h5>Heading 5</h5>  <!-- 1.125rem -->
<h6>Heading 6</h6>  <!-- 0.875rem -->

<p>Paragraph with <strong>bold</strong>, <em>italic</em>, and <a href="#">links</a>.</p>
<small>Small text</small>
<code>Inline code</code>
<pre><code>Code block</code></pre>
<blockquote>Blockquote</blockquote>
<hr>
<ul><li>Unordered</li></ul>
<ol><li>Ordered</li></ol>
<mark>Highlighted</mark>
```
