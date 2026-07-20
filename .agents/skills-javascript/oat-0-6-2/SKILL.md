---
name: oat-0-6-2
description: >
  Oat is an ultra-lightweight, zero-dependency, semantic HTML/CSS/JS UI component library (~8KB CSS + JS).
  Use this skill whenever the user mentions Oat UI, oat.ink, @knadh/oat, or needs a minimal semantic UI library
  for vanilla HTML projects. Covers buttons, forms, cards, dialogs, toasts, dropdowns, tabs, sidebars, grids,
  badges, alerts, avatars, tooltips, spinners, skeletons, progress bars, tables, accordions, breadcrumbs,
  pagination, switches, typography, utility classes, animations, CSS theming with auto dark mode, and
  Web Components (ot-tabs, ot-dropdown). Use when building lightweight web apps without frameworks,
  or when the user wants semantic HTML styling without class pollution.
metadata:
  tags:
    - ui
    - components
    - css
    - web-components
    - vanilla-js
---

# oat 0.6.2

## Overview

Oat is a semantic-first UI component library that styles HTML elements by default — no classes needed for basic usage. It uses CSS layers (`@layer`), CSS custom properties for theming, and `light-dark()` for automatic light/dark mode. Dynamic components are implemented as Web Components (`ot-tabs`, `ot-dropdown`) or minimal JS utilities (`ot.toast`, tooltip enhancement, sidebar toggle).

The library has zero dependencies, no build step, and no framework requirements. Include the CSS and JS files and write semantic HTML.

### Architecture

- **CSS layers**: `theme`, `base`, `components`, `animations`, `utilities` — clean cascade with no specificity wars
- **Theming**: All colors, spacing, fonts, radii, shadows defined as CSS custom properties in `:root`
- **Auto dark mode**: Uses `light-dark()` for seamless system preference detection
- **Web Components**: `ot-tabs` and `ot-dropdown` extend `OtBase` (lifecycle, event delegation, keyboard nav, event emission)
- **JS API**: `window.ot.toast()` for notifications, tooltip progressive enhancement, sidebar toggle handler

### Installation

**CDN:**

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

**npm:**

```bash
npm install @knadh/oat
```

```javascript
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Individual files available from `@knadh/oat/css` and `@knadh/oat/js`.

### Semantic Styling

Elements styled automatically without classes:

| Element | Styling |
|---|---|
| `h1`–`h6` | Responsive font sizes (clamp), font weight, margins |
| `p`, `a`, `strong`, `em`, `small`, `code`, `pre` | Typography, colors, spacing |
| `button`, `[type=submit/reset/button]`, `a.button` | Full button system with variants |
| `input`, `textarea`, `select` | Form styling with focus rings, validation states |
| `input[type=checkbox]`, `[type=radio]` | Custom checkboxes and radios |
| `input[role=switch]` | Toggle switch (checkbox + role) |
| `input[type=range]` | Styled range slider |
| `dialog` | Modal dialog with backdrop, animations |
| `details`/`summary` | Accordion with chevron |
| `table`, `thead`, `tbody`, `tfoot`, `th`, `td` | Data tables |
| `progress`, `meter` | Progress bars and gauges |
| `blockquote`, `hr`, `ul`, `ol`, `mark` | Content elements |
| `fieldset`, `legend`, `label` | Form grouping |

### JS APIs

| API | Purpose |
|---|---|
| `ot.toast(message, title?, options?)` | Show text toast notification |
| `ot.toast.el(element, options?)` | Show toast with custom HTML |
| `ot.toast.clear(placement?)` | Clear all or specific toasts |

### Web Components

| Element | Purpose |
|---|---|
| `<ot-tabs>` | Tabbed interface with keyboard nav and ARIA |
| `<ot-dropdown>` | Dropdown menus with popover API, positioning, keyboard nav |

## Usage

### Basic Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="oat.min.css">
  <script src="oat.min.js" defer></script>
</head>
<body>
  <h1>Hello World</h1>
  <p>This paragraph is styled automatically.</p>
  <button>Click me</button>
</body>
</html>
```

### Buttons

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button class="ghost">Ghost</button>
<button class="small">Small</button>
<button class="large">Large</button>
<button class="icon">🔍</button>
<a href="#" class="button">Link as button</a>
```

Button groups with `<menu class="buttons">`:

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

### Forms

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
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

  <label data-field>
    <input type="checkbox" /> I agree
  </label>

  <label data-field>
    <input type="checkbox" role="switch" /> Notifications
  </label>

  <button type="submit">Submit</button>
</form>
```

Input groups with `<fieldset class="group">`:

```html
<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

Validation errors with `aria-invalid="true"`:

```html
<label data-field aria-invalid="true">
  Email
  <input type="email" aria-invalid="true" />
  <div class="error">Please enter a valid email</div>
</label>
```

### Dialogs

Native `<dialog>` with `commandfor`/`command` attributes — zero JS:

```html
<button commandfor="my-dialog" command="show-modal">Open</button>
<dialog id="my-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Title</h3>
      <p>Description</p>
    </header>
    <div>Content here</div>
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

Handle return value:

```javascript
dialog.addEventListener('close', () => {
  console.log(dialog.returnValue); // "confirm"
});
```

### Toasts

```javascript
ot.toast('Action completed', 'Success', { variant: 'success' });
ot.toast('Error occurred', 'Oops', { variant: 'danger', placement: 'top-left' });
ot.toast('Warning message', 'Warning', { variant: 'warning', placement: 'bottom-right' });
ot.toast('Info', '', { placement: 'top-center', duration: 0 }); // persistent
ot.toast.clear(); // clear all
ot.toast.clear('top-right'); // clear specific placement
```

Custom markup toasts:

```html
<template id="my-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Saved</h6>
    <p>Document saved successfully.</p>
  </output>
</template>
```

```javascript
ot.toast.el(document.querySelector('#my-toast'), { duration: 8000 });
```

### Tabs (Web Component)

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab">Password</button>
    <button role="tab">Notifications</button>
  </div>
  <div role="tabpanel">Account content</div>
  <div role="tabpanel">Password content</div>
  <div role="tabpanel">Notification content</div>
</ot-tabs>
```

Set active tab programmatically:

```javascript
const tabs = document.querySelector('ot-tabs');
tabs.activeIndex = 2;

tabs.addEventListener('ot-tab-change', (e) => {
  console.log('Tab changed to index:', e.detail.index);
});
```

### Dropdowns (Web Component)

```html
<ot-dropdown>
  <button popovertarget="menu-id" class="outline">Options</button>
  <menu popover id="menu-id">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <hr>
    <button role="menuitem">Logout</button>
  </menu>
</ot-dropdown>
```

### Sidebar Layout

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </nav>

  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Users</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#">General</a></li>
              <li><a href="#">Security</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer><button class="outline">Logout</button></footer>
  </aside>

  <main>Main content</main>
</body>
```

### Grid

```html
<div class="container">
  <div class="row">
    <div class="col-4">One third</div>
    <div class="col-4">One third</div>
    <div class="col-4">One third</div>
  </div>
  <div class="row">
    <div class="col-6">Half</div>
    <div class="col-6">Half</div>
  </div>
</div>
```

### Theming

Override CSS variables in a stylesheet loaded after Oat's CSS:

```css
:root {
  --primary: #3b82f6;
  --primary-foreground: #fff;
  --danger: #ef4444;
  --radius-medium: 0.5rem;
}
```

Dark theme via `data-theme="dark"` on `<body>` or use the built-in `light-dark()` auto detection.

## Gotchas

- **`@layer` is required** — Oat uses CSS cascade layers. If your custom styles don't take effect, wrap them in `@layer components` or `@layer utilities`, or place your stylesheet after Oat's CSS.

- **`light-dark()` browser support** — Oat uses `light-dark()` for automatic dark mode. It is supported in Chrome 123+, Edge 123+, Safari 18+. For older browsers, use `data-theme="dark"` on `<body>` and scope dark variables under `[data-theme="dark"]`.

- **`<dialog>` needs `commandfor` polyfill for Safari** — Oat includes a polyfill for `command`/`commandfor` on buttons (not natively supported in Safari). Include `oat.min.js` for dialog open/close to work cross-browser.

- **`ot-dropdown` positions menus manually** — The dropdown calculates position relative to the trigger and applies `position: fixed`. Do not wrap it in a `transform`-ed or `overflow: hidden` container, as this breaks the positioning.

- **`ot-tabs` requires matching tab/panel counts** — The number of `[role="tab"]` elements must match the number of `[role="tabpanel"]` elements. Extra panels are ignored; fewer panels cause warnings.

- **`data-field` containers auto-style hints and errors** — Use `[data-hint]` for helper text and `.error` for validation messages. Errors auto-show when `aria-invalid="true"` is on the field container or input.

- **Toasts pause on hover** — Toast auto-dismiss timer pauses when the user hovers over the toast. Set `duration: 0` for persistent toasts.

- **Tooltip uses `title` attribute** — Oat converts `title` to `data-tooltip` for custom styling. This is progressive enhancement — native `title` works without JS. Replaced elements (`<img>`, `<iframe>`) need a wrapper with `title`.

- **Sidebar breakpoint is hardcoded at 768px** — The sidebar collapses to overlay mode below 768px. This breakpoint is hardcoded in the JS (no CSS variable). Use `data-sidebar-layout="always"` for always-collapsible behavior.

- **`<menu class="buttons">` requires `<li>` wrappers** — Button groups need `<li>` children for proper border radius handling. Direct button children won't get the joined look.

- **Grid stacks on mobile** — Below 768px, all columns span full width (4/4). Offsets are reset. Plan mobile layouts accordingly.

- **`role="switch"` on checkboxes** — Toggle switches use `role="switch"` on a checkbox. Without it, the element renders as a standard checkbox.

- **`aria-busy="true"` for spinners** — Loading spinners appear on any element with `aria-busy="true"`. Add `data-spinner="small|large|overlay"` for size and overlay mode.

- **Popover API required** — `ot-dropdown` and toast containers use the Popover API. It is supported in Chrome 114+, Firefox 125+, Safari 17.4+. For older browsers, dropdowns and toasts won't work.

- **`ot.toast.el()` clones the element** — The element passed to `ot.toast.el()` is cloned, so templates can be reused. The original element is never removed from the DOM.

- **`fieldset.group` requires direct children** — Input grouping with `fieldset.group` expects direct `<input>`, `<select>`, `<button>`, or `<legend>` children. Nested wrappers break the layout.

- **Animations respect `prefers-reduced-motion`** — All animations and transitions are disabled when the user prefers reduced motion. No extra configuration needed.

## References

- [01-css-components.md](references/01-css-components.md) — All CSS-only components: buttons, cards, alerts, badges, avatars, tables, accordions, breadcrumbs, pagination, skeleton
- [02-forms.md](references/02-forms.md) — Form elements, input groups, validation, field containers, switches, range, file, date inputs
- [03-web-components.md](references/03-web-components.md) — ot-tabs, ot-dropdown — API, events, keyboard navigation, ARIA
- [04-js-api.md](references/04-js-api.md) — ot.toast, toast.el, toast.clear, tooltip enhancement, sidebar toggle
- [05-layout.md](references/05-layout.md) — Grid system, sidebar layout, topnav, container, responsive behavior
- [06-theming.md](references/06-theming.md) — CSS variables, color tokens, spacing, fonts, radii, shadows, dark mode, custom themes
- [07-utilities.md](references/07-utilities.md) — Utility classes, flex helpers, text alignment, spacing, animations
- [08-recipes.md](references/08-recipes.md) — Composable patterns: split buttons, form cards, empty states, stats dashboards
- [09-extensions.md](references/09-extensions.md) — Community extensions: oat-chips, oat-animate, oat-table, oat-upload
