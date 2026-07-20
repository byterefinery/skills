# Recipes

Composable UI patterns using Oat components.

## Split Button

Combined primary action with dropdown for secondary actions.

```html
<ot-dropdown>
  <menu class="buttons">
    <li><button class="outline">Save</button></li>
    <li>
      <button class="outline" popovertarget="save-actions" aria-label="More save actions">
        More
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
    </li>
  </menu>
  <menu popover id="save-actions">
    <button role="menuitem">Save draft</button>
    <button role="menuitem">Save and publish</button>
    <button role="menuitem">Duplicate</button>
  </menu>
</ot-dropdown>
```

## Form Card

Grouped form fields in a card with header, fields, and actions.

```html
<article class="card">
  <header>
    <h3>Profile</h3>
    <p class="text-light">Update account information</p>
  </header>

  <div class="mt-4">
    <label data-field>
      Name
      <input type="text" value="Your name" />
    </label>

    <label data-field>
      Email
      <input type="email" value="mila@example.com" />
    </label>

    <label data-field>
      <input type="checkbox" role="switch" checked> Email notifications
    </label>
  </div>

  <footer class="hstack justify-end mt-4">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

## Empty State

Card with centered content and call-to-action.

```html
<article class="card align-center">
  <h3>Nothing here yet</h3>
  <p class="text-light">Why don't you create something?</p>
  <footer class="hstack justify-center mt-4">
    <button>New something</button>
  </footer>
</article>
```

## Stats Dashboard

Grid of metric cards with badges and progress bars.

```html
<div class="container">
  <div class="row">
    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Revenue</h4>
        <span class="badge" data-variant="success">+12%</span>
      </header>
      <h2>$42,200</h2>
      <p class="text-light">vs last month</p>
      <progress value="72" max="100"></progress>
    </article>

    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Completion</h4>
        <span class="badge" data-variant="warning">-2%</span>
      </header>
      <h2>4.6%</h2>
      <p class="text-light">checkout completion</p>
      <meter value="0.46" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
    </article>

    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Tickets</h4>
        <span class="badge">14</span>
      </header>
      <h2>14</h2>
      <p class="text-light">support queue</p>
      <progress value="35" max="100"></progress>
    </article>
  </div>
</div>
```

## Confirmation Dialog

Dialog with danger action for destructive operations.

```html
<button commandfor="delete-dialog" command="show-modal" data-variant="danger">Delete</button>
<dialog id="delete-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Delete item?</h3>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button type="button" commandfor="delete-dialog" command="close" class="outline">Cancel</button>
      <button value="delete" data-variant="danger">Delete</button>
    </footer>
  </form>
</dialog>
```

## Toast with Action

Custom toast using a template.

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000 })">
  Save and notify
</button>
```

## Loading Card

Card with spinner overlay during async operations.

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <h3>Loading...</h3>
  <p>Content is dimmed while loading.</p>
</article>
```

Toggle loading state:

```javascript
card.setAttribute('aria-busy', 'true');  // Show spinner
card.removeAttribute('aria-busy');        // Hide spinner
```

## Skeleton Loading

Placeholder shimmer before content loads.

```html
<article class="card">
  <div style="display: flex; gap: var(--space-3);">
    <div role="status" class="skeleton box"></div>
    <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
      <div role="status" class="skeleton line"></div>
      <div role="status" class="skeleton line" style="width: 60%"></div>
      <div role="status" class="skeleton line" style="width: 80%"></div>
    </div>
  </div>
</article>
```

## Notification Alert with Dismiss

Alert with a dismiss button.

```html
<div role="alert" data-variant="warning" style="position: relative;">
  <strong>Warning!</strong> Please review before continuing.
  <button class="icon" style="position: absolute; inset-block-start: 0; inset-inline-end: 0;"
          onclick="this.closest('[role=alert]').remove()" aria-label="Dismiss">✕</button>
</div>
```

## Search Bar

Input group with search icon and clear button.

```html
<fieldset class="group">
  <legend>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
    </svg>
  </legend>
  <input type="search" placeholder="Search..." />
  <button class="icon" aria-label="Clear">✕</button>
</fieldset>
```

## User Table

Table with avatars, badges, and action buttons.

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>User</th>
        <th>Role</th>
        <th>Status</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <div class="hstack">
            <figure data-variant="avatar" class="small">
              <abbr title="Alice">A</abbr>
            </figure>
            <span>Alice</span>
          </div>
        </td>
        <td>Admin</td>
        <td><span class="badge" data-variant="success">Active</span></td>
        <td>
          <ot-dropdown>
            <button popovertarget="menu-1" class="icon" aria-label="Actions">⋯</button>
            <menu popover id="menu-1">
              <button role="menuitem">Edit</button>
              <button role="menuitem">Deactivate</button>
            </menu>
          </ot-dropdown>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```
