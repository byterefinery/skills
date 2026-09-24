# CSS-Only Components

These components work with zero JavaScript. They rely on semantic HTML and CSS styling.

## Accordion

Native `<details>` / `<summary>` — no JS needed.

```html
<details>
  <summary>What is Oat?</summary>
  <p class="p-4">Oat is a minimal, semantic-first UI library.</p>
</details>

<details>
  <summary>How do I use it?</summary>
  <p class="p-4">Include CSS and JS files, write semantic HTML.</p>
</details>
```

### Grouped accordions (radio behavior)

Use the `name` attribute to group — only one opens at a time:

```html
<details name="faq">
  <summary>Question 1</summary>
  <p>Answer 1</p>
</details>
<details name="faq">
  <summary>Question 2</summary>
  <p>Answer 2</p>
</details>
```

## Alert

Use `role="alert"` with optional `data-variant`:

```html
<div role="alert" data-variant="success">
  <strong>Success!</strong> Changes saved.
</div>

<div role="alert" data-variant="warning">
  <strong>Warning!</strong> Review before continuing.
</div>

<div role="alert">
  <strong>Info</strong> Default alert message.
</div>

<div role="alert" data-variant="error">
  <strong>Error!</strong> Something went wrong.
</div>
```

Variants: `success`, `warning`, `error`, `danger`.

## Avatar

Use `<figure data-variant="avatar">` with image, text initials, or icons:

```html
<figure data-variant="avatar" class="small" aria-label="Jane Doe">
  <img src="/avatar.jpg" alt="" />
</figure>

<figure data-variant="avatar" aria-label="Oat">
  <abbr title="Jane Doe">OT</abbr>
</figure>

<figure data-variant="avatar" class="large" aria-label="Jane Doe">
  <img src="/avatar.jpg" alt="" />
</figure>
```

Sizes: `.small` (2rem), default (2.5rem), `.large` (3.25rem).

### Avatar group

```html
<figure data-variant="avatar" role="group" aria-label="Team">
  <figure data-variant="avatar" aria-label="Jane"><img src="j.jpg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="John"><img src="j2.jpg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="Alex"><img src="a.jpg" alt="" /></figure>
</figure>
```

## Badge

Inline pill labels with `.badge`:

```html
<span class="badge">Default</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
<span class="badge outline">Outline</span>
```

## Breadcrumb

Semantic `<nav>` with ordered list:

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

Use `aria-current="page"` on the active item.

## Button

Styled by default. Use `data-variant` for semantic colors, classes for visual styles:

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button class="ghost">Ghost</button>
```

### Sizes

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
<button class="icon">🔍</button>
```

### Button groups

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

### Link as button

```html
<a href="#" class="button">Hyperlink styled as button</a>
```

## Card

Use `class="card"` on any container:

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description.</p>
  </header>
  <p>Card content goes here.</p>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

## Dialog

Fully semantic, zero-JS modal using `<dialog>` with `command`/`commandfor`:

```html
<button commandfor="my-dialog" command="show-modal">Open dialog</button>

<dialog id="my-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Title</h3>
      <p>Description text.</p>
    </header>
    <div>
      <p>Dialog content here.</p>
    </div>
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

### Attributes

- `commandfor="dialog-id"` — target dialog ID
- `command="show-modal"` — open as modal
- `command="close"` — close the dialog
- `closedby="any"` — allow backdrop click to close
- `form method="dialog"` — enables `returnValue`

### Handling return value

```js
dialog.addEventListener('close', (e) => {
  console.log(dialog.returnValue); // "confirm"
});
```

Or inline: `<dialog onclose="console.log(this.returnValue)">`

## Meter

Semantic `<meter>` for values within a known range:

```html
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

Colors: optimum (success/green), suboptimum (warning/orange), even-less-good (danger/red).

## Pagination

Reuses `menu.buttons`:

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#" class="button outline small">&larr; Prev</a></li>
    <li><a href="#" class="button outline small">1</a></li>
    <li><a href="#" class="button small" aria-current="page">2</a></li>
    <li><a href="#" class="button outline small">3</a></li>
    <li><a href="#" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

## Progress

Native `<progress>` element:

```html
<progress value="60" max="100"></progress>
<progress value="30" max="100"></progress>
<progress value="90" max="100"></progress>
```

## Skeleton

Loading placeholders with shimmer animation:

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

### Skeleton card

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-6);">
  <div role="status" class="skeleton box"></div>
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 60%"></div>
  </div>
</article>
```

## Spinner

Loading indicator using `aria-busy`:

```html
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="large"></div>
<button aria-busy="true" data-spinner="small" disabled>Loading</button>
```

### Overlay mode

Dims container contents and overlays spinner:

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <h3>Card Title</h3>
  <p>Content is dimmed while loading.</p>
</article>
```

## Switch

Toggle switch using checkbox with `role="switch"`:

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked> Confabulation
</label>
```

## Table

Styled automatically. Wrap in `.table` for horizontal scroll on small screens:

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>User</td>
        <td>user@example.com</td>
        <td><span class="badge" data-variant="success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

## Tooltip

Converted automatically from `title` attributes. Add `data-tooltip-placement` for positioning:

```html
<button title="Save your changes">Save</button>
<button title="Below" data-tooltip-placement="bottom">Bottom</button>
<button title="Left" data-tooltip-placement="left">Left</button>
<button title="Right" data-tooltip-placement="right">Right</button>
```

Placements: `top` (default), `bottom`, `left`, `right`.

For replaced elements (`<img>`, `<iframe>`), wrap in a parent with the `title`:

```html
<span title="Image tooltip"><img src="photo.jpg" /></span>
```
