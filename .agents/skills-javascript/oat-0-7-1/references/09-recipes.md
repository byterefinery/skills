# Recipes

Composable UI patterns built from existing Oat components.

## Split button

Combine `menu.buttons` with `<ot-dropdown>` for primary + secondary actions:

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

## Radio cards

Wrap each option in a `<label>` so the whole card is selectable:

```html
<fieldset class="w-100">
  <legend>Billing</legend>
  <p class="text-light">Select a billing cycle</p>

  <div class="row">
    <label class="col-4 card vstack">
      <span class="w-100 hstack justify-between">
        <strong>Monthly</strong>
        <input type="radio" name="billing">
      </span>
      <span class="text-light">$12 / mo</span>
    </label>

    <label class="col-4 card vstack">
      <span class="w-100 hstack justify-between">
        <strong>Yearly</strong>
        <input type="radio" name="billing">
      </span>
      <span class="text-light">$96 / yr · save 33%</span>
    </label>

    <label class="col-4 card vstack">
      <span class="w-100 hstack justify-between">
        <strong>Lifetime</strong>
        <input type="radio" name="billing" checked>
      </span>
      <span class="text-light">$299 once</span>
    </label>
  </div>
</fieldset>
```

## Form card

Group form fields inside a card with header and footer:

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

## Empty state

Card with centered text and primary action:

```html
<article class="card align-center">
  <h3>Nothing here yet</h3>
  <p class="text-light">Why don't you create something?</p>
  <footer class="hstack justify-center mt-4">
    <button>New something</button>
  </footer>
</article>
```

## Stats dashboard

Compose metrics with grid, cards, badges, and progress/meter:

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

## Confirmation dialog

Dialog with danger action:

```html
<button commandfor="confirm-delete" command="show-modal">Delete item</button>

<dialog id="confirm-delete" closedby="any">
  <form method="dialog">
    <header>
      <h3>Delete item?</h3>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button type="button" commandfor="confirm-delete" command="close" class="outline">Cancel</button>
      <button data-variant="danger" value="delete">Delete</button>
    </footer>
  </form>
</dialog>
```

## Search bar

Combined input group:

```html
<fieldset class="group">
  <input type="search" placeholder="Search..." />
  <button>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
    </svg>
  </button>
</fieldset>
```

## Notification badge

In sidebar navigation:

```html
<nav>
  <ul>
    <li><a href="#" aria-current="page">Home</a></li>
    <li>
      <a href="#">
        Messages
        <span class="badge" data-variant="danger">3</span>
      </a>
    </li>
    <li><a href="#">Settings</a></li>
  </ul>
</nav>
```
