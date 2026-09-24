# Oat Recipes and Extensions Reference

## Contents

- [Recipes](#recipes)
  - [Split button](#split-button)
  - [Radio cards](#radio-cards)
  - [Form card](#form-card)
  - [Empty state](#empty-state)
  - [Stats cards](#stats-cards)
- [Community extensions](#community-extensions)
- [Related zero-dependency libraries](#related-zero-dependency-libraries)

## Recipes

Composable UI patterns built from stock Oat components — useful when a widget is not a built-in component.

### Split button

`menu.buttons` for the joined controls plus `ot-dropdown` for the secondary action menu.

```html
<ot-dropdown>
  <menu class="buttons">
    <li><button class="outline">Save</button></li>
    <li>
      <button class="outline" popovertarget="save-actions" aria-label="More save actions">
        More
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6" /></svg>
      </button>
    </li>
  </menu>
  <menu popover id="save-actions">
    <button role="menuitem" class="ghost">Save draft</button>
    <button role="menuitem" class="ghost">Save and publish</button>
    <button role="menuitem" class="ghost">Duplicate</button>
  </menu>
</ot-dropdown>
```

### Radio cards

Wrap each option in a `<label>` so the whole card is selectable, and group them in a `<fieldset>` with a `<legend>`.

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

### Form card

Group related form fields inside a card with standard field containers and footer actions.

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

### Empty state

A card with a message and a primary action for list/result empty states.

```html
<article class="card align-center">
  <h3>Nothing here yet</h3>
  <p class="text-light">Why don't you create something?</p>
  <footer class="hstack justify-center mt-4">
    <button>New something</button>
  </footer>
</article>
```

### Stats cards

Compose dashboard metrics with the grid, cards, badges, and `progress`/`meter`.

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

## Community extensions

Third-party extensions that work with Oat (see the repo's Extensions page for demos):

- **oat-chips** ([github.com/someshkar/oat-chips](https://github.com/someshkar/oat-chips)) — chip/tag component with dismissible filters, colors, and toggle selection. ~1KB gzipped.
- **oat-animate** ([github.com/dharmeshgurnani/oat-animate](https://github.com/dharmeshgurnani/oat-animate)) — declarative `ot-animate` triggers (`on-load`, `hover`, `in-view`) with reduced-motion support. ~1KB gzipped.
- **oat-table** ([github.com/MADEVAL/Oat-Table](https://github.com/MADEVAL/Oat-Table)) — semantic table enhancement: sort, filter, and select rows without turning tables into framework widgets.
- **oat-upload** ([github.com/MADEVAL/Oat-Upload](https://github.com/MADEVAL/Oat-Upload)) — dropzone, file previews, validation, removal, and progress for native `<input type="file">`.

## Related zero-dependency libraries

Useful tiny zero-dependency JS libraries that pair well with Oat (same author):

- **tinyrouter.js** — frontend routing and navigation on top of `window.history`. ~950 bytes.
- **highlighted-input.js** — highlights keywords/tags inside an `<input>`. ~450 bytes.
- **floatype.js** — floating autocomplete/autosuggestion for textareas. ~1.2KB.
- **dragmove.js** — make DOM elements draggable/movable. ~500 bytes.
- **indexed-cache.js** — cache static assets in IndexedDB for offline/long-term use. ~2.1KB.
