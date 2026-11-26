# Oat CSS Components

Markup reference for all semantic/CSS-only components. These work with `oat.min.css` alone (no JS).

## Table of Contents

- [Typography](#typography)
- [Button](#button)
- [Form elements](#form-elements)
- [Card](#card)
- [Alert](#alert)
- [Badge](#badge)
- [Table](#table)
- [Accordion](#accordion)
- [Switch](#switch)
- [Progress & Meter](#progress--meter)
- [Skeleton](#skeleton)
- [Spinner](#spinner)
- [Avatar](#avatar)
- [Breadcrumb](#breadcrumb)
- [Pagination](#pagination)
- [Dialog](#dialog)

---

## Typography

Base text elements are styled automatically — no classes needed: `h1`–`h6`, `p`, `a`, `strong`/`em`, `code`, `pre`/`code` blocks, `blockquote`, `hr`, `ul`/`ol`/`li`.

## Button

`<button>` is styled by default. `data-variant="secondary|danger"` for semantic variants; `.outline`/`.ghost` for visual styles; `.small`/`.large` for sizes.

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button data-variant="danger" class="outline">Danger outline</button>
<button class="ghost">Ghost</button>
<button disabled>Disabled</button>
```

Sizes and hyperlink buttons:

```html
<button class="small">Small</button>
<button class="large">Large</button>
<a href="#action" class="button">Hyperlink styled as button</a>
```

Button group — connected buttons in `<menu class="buttons">`:

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

## Form elements

Form elements are styled automatically. Wrap inputs in `<label>` (or use `<label data-field>`) for association and field layout; `data-hint` (or `<small>`) adds a hint line.

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>

  <label data-field>
    Password
    <input type="password" aria-describedby="password-hint" />
    <small id="password-hint" data-hint>This is a small hint</small>
  </label>

  <div data-field>
    <label>Select</label>
    <select>
      <option value="">Select an option</option>
      <option value="a">Option A</option>
    </select>
  </div>

  <label data-field>
    Message
    <textarea placeholder="Your message..."></textarea>
  </label>

  <!-- checkbox / radio / range / switch all work in data-field labels -->
  <label data-field>
    <input type="checkbox" role="switch" /> I agree to the terms
  </label>

  <fieldset class="hstack">
    <legend>Preference</legend>
    <label><input type="radio" name="pref">Option A</label>
    <label><input type="radio" name="pref">Option B</label>
  </fieldset>

  <button type="submit">Submit</button>
  <input type="reset" value="Reset" data-variant="secondary" />
</form>
```

Supported input types: `text`, `email`, `password`, `file`, `datetime-local`, `date`, `checkbox`, `radio`, `range`, plus `<select>`, `<textarea>`.

### Input group

`.group` on a `<fieldset>` combines inputs with buttons/labels:

```html
<fieldset class="group">
  <legend>https://</legend>
  <input type="url" placeholder="subdomain">
  <select aria-label="Select a subdomain">
    <option value="" disabled selected>Select</option>
    <option>.example.com</option>
  </select>
  <button>Go</button>
</fieldset>

<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

### Validation error

`aria-invalid="true"` on a field container reveals and styles `.error` messages:

```html
<label data-field aria-invalid="true">
  Enter secret value
  <input type="password" aria-invalid="true" aria-describedby="new-password-error" />
  <div id="new-password-error" class="error" role="status">The value is incorrect</div>
</label>
```

## Card

`class="card"` on an `<article>` (semantic container); `header`/`footer` slot in naturally:

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description goes here.</p>
  </header>
  <p>This is the card content. It can contain any HTML.</p>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

## Alert

`role="alert"` for styling; `data-variant` for `success`/`warning`/`error` (default is info):

```html
<div role="alert" data-variant="success">
  <strong>Success!</strong> Your changes have been saved.
</div>
<div role="alert" data-variant="warning">
  <strong>Warning!</strong> Please review before continuing.
</div>
<div role="alert">
  <strong>Info</strong> This is a default alert message.
</div>
<div role="alert" data-variant="error">
  <strong>Error!</strong> Something went wrong.
</div>
```

## Badge

`.badge` with `data-variant` for color variants; `.outline` is a style modifier:

```html
<span class="badge">Default</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge outline">Outline</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
```

## Table

Tables are styled by default (`<thead>`/`<tbody>`/`<tfoot>`). Wrap in `class="table"` to get a horizontal scrollbar on small screens. Badges are commonly used for status cells:

```html
<div class="table">
  <table>
    <thead>
      <tr><th>Name</th><th>Status</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>root@example.com</td>
        <td><span class="badge" data-variant="success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

## Accordion

Native `<details>`/`<summary>` — no JS required. Group items (only one open at a time, like radio) with a shared `name` attribute:

```html
<details>
  <summary>What is Oat</summary>
  <p class="p-4">Oat is a minimal, semantic-first UI component library with zero dependencies.</p>
</details>

<details name="grouped">
  <summary>Grouped item one</summary>
  <p class="p-4">Using the name attribute groups items like radio.</p>
</details>
<details name="grouped">
  <summary>Grouped item two</summary>
  <p class="p-4">Only one of the group stays open.</p>
</details>
```

## Switch

`role="switch"` on a checkbox:

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked> Confabulation
</label>
```

## Progress & Meter

Native `<progress>` and `<meter>`:

```html
<progress value="60" max="100"></progress>

<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

The browser colors `<meter>` based on `low`/`high`/`optimum`.

## Skeleton

Loading placeholders with shimmer animation. `.skeleton` + `role="status"`; `.line` for text, `.box` for images. Put skeletons inside an `<article>` for a card-style loading layout.

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

## Spinner

`aria-busy="true"` on any element shows a loading indicator. Size with `data-spinner="small|large"`; `data-spinner="overlay"` (combine with a size, e.g. `data-spinner="large overlay"`) dims the container's contents and overlays the spinner.

```html
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="large"></div>
<button aria-busy="true" data-spinner="small" disabled>Loading</button>
```

## Avatar

`<figure data-variant="avatar">` with `<img>`, `<abbr>` (text initials), or an icon. `.small`/`.large` for sizes. Groups: `role="group"` on an outer figure, with size set on the group container.

```html
<figure data-variant="avatar" class="small" aria-label="Jane Doe">
    <img src="/avatar.svg" alt="" />
</figure>

<figure data-variant="avatar" aria-label="Oat">
    <abbr title="Jane Doe">OT</abbr>
</figure>

<figure data-variant="avatar" role="group" class="small" aria-label="Team members">
    <figure data-variant="avatar" aria-label="Jane Doe"><img src="/a.svg" alt=""></figure>
    <figure data-variant="avatar" aria-label="John Smith"><img src="/b.svg" alt=""></figure>
</figure>
```

## Breadcrumb

Semantic `<nav>` with an ordered list; `aria-current="page"` marks the active item:

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack">
    <li><a href="#home" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#projects" class="unstyled">Projects</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#docs" class="unstyled" aria-current="page"><strong>Breadcrumb</strong></a></li>
  </ol>
</nav>
```

## Pagination

No special markup — reuse the button group with `.button` links and `aria-current="page"` for the active page:

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#1" class="button outline small">&larr; Previous</a></li>
    <li><a href="#1" class="button outline small">1</a></li>
    <li><a href="#3" class="button small" aria-current="page">3</a></li>
    <li><a href="#4" class="button outline small">4</a></li>
    <li><a href="#4" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

## Dialog

Zero-JS modal dialogs with the native `<dialog>` + command API. The opener uses `commandfor` + `command="show-modal"`; close buttons use `command="close"` (or `type="button"` + `commandfor`/`command`). Focus trapping, z-placement, and Escape/`closedby="any"` work out of the box.

```html
<button commandfor="demo-dialog" command="show-modal">Open dialog</button>
<dialog id="demo-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Title</h3>
      <p>This is a dialog description.</p>
    </header>
    <div>
      <p>Dialog content goes here. Click outside or press Escape to close.</p>
    </div>
    <footer>
      <button type="button" commandfor="demo-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

Forms inside dialogs work naturally. Read the result from the button's `value` via the `close` event:

```js
const dialog = document.querySelector("#demo-dialog");
dialog.addEventListener("close", () => {
  console.log(dialog.returnValue); // "confirm"
});
```
