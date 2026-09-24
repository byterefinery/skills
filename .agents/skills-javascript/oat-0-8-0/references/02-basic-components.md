# Oat Basic Components Reference

CSS-only components — no JavaScript required (they work with just `oat.min.css`).

## Contents

- [Typography](#typography)
- [Button](#button)
- [Badge](#badge)
- [Alert](#alert)
- [Breadcrumb](#breadcrumb)
- [Card](#card)
- [Avatar](#avatar)
- [Form elements](#form-elements)
- [Table](#table)
- [Pagination](#pagination)

## Typography

Base text elements are styled automatically. No classes needed.

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<p>This is a paragraph with <strong>bold</strong>, <em>italic</em>, and <a href="#">a link</a>.</p>
<p>Here's some <code>inline code</code> and a code block:</p>
<pre><code>function hello() {
  console.log('Hello, World!');
}</code></pre>
<blockquote>This is a blockquote. It's styled automatically.</blockquote>
<hr>
<ul>
  <li>Unordered list item</li>
</ul>
```

## Button

The `<button>` element is styled by default. Use `data-variant="secondary|danger"` for semantic variants and classes for visual styles.

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button data-variant="danger" class="outline">Danger</button>
<button class="ghost">Ghost</button>
<button disabled>Disabled</button>
```

### Sizes and shapes

`.small` / `.large` for sizes; `.icon` for a fixed square icon button (2.5rem, 2rem small, 3rem large). An `<a>` gets button styling with the `.button` class.

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
<a href="#button" class="button">Hyperlink</a>
```

### Button group

Wrap buttons in `<menu class="buttons">` for connected buttons. Each `<li>` is expected to contain exactly one button (or `a.button`).

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

## Badge

Use `.badge` with `data-variant` for color variants. `.outline` is a style modifier. Badges are used for inline labels/tags/pills, table status cells, and as tag elements inside `ot-taginput` and `ot-upload`.

```html
<span class="badge">Default</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge outline">Outline</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
```

## Alert

Use `role="alert"` for alert styling. Set `data-variant` for success, warning, or error (`error` and `danger` are equivalent).

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

## Breadcrumb

Use a semantic breadcrumb `<nav>` with an ordered list and `aria-current="page"` for the active item.

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-7)">
    <li><a href="#home" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#projects" class="unstyled">Projects</a></li>
    <li aria-hidden="true">/</li>
    <li aria-current="page"><a href="#oat" class="unstyled"><strong>Oat Docs</strong></a></li>
  </ol>
</nav>
```

## Card

Use `class="card"` on an `<article>` for a visual box-like card. It is the recommended wrapper for grouped content, form cards, dialogs-adjacent content, and skeleton loaders.

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

## Avatar

Use `<figure data-variant="avatar">` with an `<img>` to create an avatar. Text initials (`<abbr>`) or icons also work instead of an image.

```html
<figure data-variant="avatar" class="small" aria-label="Jane Doe">
  <img src="/avatar.svg" alt="" />
</figure>
<figure data-variant="avatar" aria-label="Oat">
  <abbr title="Jane Doe">OT</abbr>
</figure>
<figure data-variant="avatar" class="large" aria-label="Jane Doe">
  <img src="/avatar.svg" alt="" />
</figure>
```

### Avatar group

Wrap avatars in a group figure with `role="group"`. To size all avatars in the group, add `.small` or `.large` to the group container.

```html
<figure data-variant="avatar" role="group" class="small" aria-label="Team members">
  <figure data-variant="avatar" aria-label="Jane Doe">
    <img src="/avatar.svg" alt="" />
  </figure>
  <figure data-variant="avatar" aria-label="John Smith">
    <img src="/avatar.svg" alt="" />
  </figure>
</figure>
```

## Form elements

Form elements are styled automatically. Wrap inputs in `<label>` (with `data-field` for the stacked field layout) for proper association.

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>

  <label data-field>
    Password
    <input type="password" placeholder="Password" aria-describedby="password-hint" />
    <small id="password-hint" data-hint>This is a small hint</small>
  </label>

  <div data-field>
    <label>Select</label>
    <select aria-label="Select an option">
      <option value="">Select an option</option>
      <option value="a">Option A</option>
    </select>
  </div>

  <label data-field>
    Message
    <textarea placeholder="Your message..."></textarea>
  </label>

  <label data-field aria-disabled>
    Disabled
    <input type="text" placeholder="Disabled" disabled />
    <span data-hint>This is a hint</span>
  </label>

  <label data-field>
    File<br />
    <input type="file" />
  </label>

  <label data-field>
    Date
    <input type="date" />
  </label>

  <label data-field>
    <input type="checkbox" /> I agree to the terms
    <span data-hint>This is a hint</span>
  </label>

  <fieldset class="hstack">
    <legend>Preference</legend>
    <label><input type="radio" name="pref">Option A</label>
    <label><input type="radio" name="pref">Option B</label>
  </fieldset>

  <label data-field>
    Volume
    <input type="range" min="0" max="100" value="50" />
  </label>

  <label data-field>
    State
    <input type="checkbox" role="switch" />
  </label>

  <button type="submit">Submit</button>
</form>
```

Supported input types: `text`, `email`, `password`, `url`, `number`, `date`, `datetime-local`, `time`, `file`, `range`, `color`, `checkbox`, `radio`, plus `select` and `textarea`.

### Input group

Use `.group` on a `<fieldset>` to combine inputs with buttons or labels into one bordered control.

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

Use `aria-invalid="true"` on the field container (and input) to reveal and style error messages. The container is usually a `<label data-field>` or `<div data-field>`; the error element is `.error` with `role="status"`. Invalid states also style automatically via `:user-invalid` (constraint validation) and `input[aria-invalid=true]`.

```html
<fieldset class="vstack">
  <div data-field>
    <label for="email-error-input">Email</label>
    <input type="email" id="email-error-input" placeholder="Type invalid email here" autocomplete="off" />
    <div id="email-error-message" class="error" role="status">Please enter a valid email address</div>
  </div>
  <label data-field aria-invalid="true">
    Enter secret value
    <input type="password" aria-invalid="true" id="new-password" aria-describedby="new-password-error" placeholder="Enter new secret" />
    <div id="new-password-error" class="error" role="status">The value is incorrect</div>
  </label>
</fieldset>
```

## Table

Tables are styled by default. Use `<thead>` and `<tbody>` tags (and `<tfoot>` if needed). Wrap in a `div.table` container to get a horizontal scrollbar on small screens.

```html
<div class="table">
  <table>
    <thead>
      <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>Byte Bandit</td>
        <td>byte@example.com</td>
        <td>Editor</td>
        <td><span class="badge" data-variant="success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

## Pagination

Pagination has no special component — it re-uses small buttons in a `menu.buttons` group, with `aria-current="page"` marking the active page.

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#1" class="button outline small">&larr; Previous</a></li>
    <li><a href="#1" class="button outline small">1</a></li>
    <li><a href="#2" class="button outline small">2</a></li>
    <li><a href="#3" class="button small" aria-current="page">3</a></li>
    <li><a href="#4" class="button outline small">4</a></li>
    <li><a href="#5" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```
