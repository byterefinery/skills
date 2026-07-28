---
title: Navigation
---

# Navigation

## Tabs

`<ot-tabs>` Web Component with keyboard navigation, ARIA state management, and optional deep-linking.

### Basic Tabs

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab">Password</button>
    <button role="tab">Notifications</button>
  </div>
  <div role="tabpanel">
    <h3>Account Settings</h3>
    <p>Manage your account information.</p>
  </div>
  <div role="tabpanel">
    <h3>Password Settings</h3>
    <p>Change your password.</p>
  </div>
  <div role="tabpanel">
    <h3>Notification Settings</h3>
    <p>Configure notifications.</p>
  </div>
</ot-tabs>
```

### Deep-Linking with Anchor

Add `data-anchor="key"` to `<ot-tabs>` and `id` to each `role="tab"`:

```html
<ot-tabs data-anchor="tab">
  <div role="tablist">
    <button role="tab" id="account">Account</button>
    <button role="tab" id="password">Password</button>
    <button role="tab" id="notifications">Notifications</button>
  </div>
  <div role="tabpanel"><p>Account content</p></div>
  <div role="tabpanel"><p>Password content</p></div>
  <div role="tabpanel"><p>Notification content</p></div>
</ot-tabs>
```

Activating the "Password" tab sets URL to `#tab=password`. Loading the page with that hash selects the matching tab.

### Programmatic Control

```js
const tabs = document.querySelector('ot-tabs');
console.log(tabs.activeIndex);   // Read current index
tabs.activeIndex = 2;            // Set active tab by index

tabs.addEventListener('ot-tab-change', e => {
  console.log(e.detail.index);   // New tab index
  console.log(e.detail.tab);     // Tab element
});
```

### Keyboard Navigation

- `ArrowLeft` / `ArrowRight`: Move between tabs
- Focus follows the active tab

### ARIA Attributes

Automatically managed:
- `aria-selected="true|false"` on tabs
- `tabindex="0"` on active tab, `-1` on others
- `aria-controls` on tabs → panel ids
- `aria-labelledby` on panels → tab ids

## Dropdown

`<ot-dropdown>` Web Component using the native Popover API with auto-positioning and keyboard navigation.

### Basic Dropdown

```html
<ot-dropdown>
  <button popovertarget="menu-id" class="outline">
    Options
  </button>
  <menu popover id="menu-id">
    <button role="menuitem" class="ghost">Profile</button>
    <button role="menuitem" class="ghost">Settings</button>
    <button role="menuitem" class="ghost">Help</button>
    <hr>
    <button role="menuitem" data-variant="danger" class="ghost">Logout</button>
  </menu>
</ot-dropdown>
```

### Dropdown with Links

```html
<ot-dropdown>
  <button popovertarget="link-menu" class="outline">Navigate</button>
  <menu popover id="link-menu">
    <a href="/profile" role="menuitem" class="unstyled">Profile</a>
    <a href="/settings" role="menuitem" class="unstyled">Settings</a>
    <hr>
    <a href="/logout" role="menuitem" class="unstyled">Logout</a>
  </menu>
</ot-dropdown>
```

### Popover (Non-Menu)

```html
<ot-dropdown>
  <button popovertarget="confirm-popover" class="outline">Confirm</button>
  <article class="card" popover id="confirm-popover">
    <header>
      <h4>Are you sure?</h4>
      <p>This action cannot be undone.</p>
    </header>
    <footer>
      <button class="outline small" popovertarget="confirm-popover">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm-popover">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

### Dropdown Behavior

- **Positioning**: Calculated manually (popover is fixed to viewport), flips vertically/horizontally on overflow
- **Repositioning**: On scroll and resize while open
- **Keyboard**: `ArrowUp`/`ArrowDown`/`Home`/`End` for menuitem navigation
- **Focus**: First menuitem focused on open, trigger refocused on close
- **ARIA**: `aria-expanded="true|false"` on trigger

## Sidebar

See [04-layout.md](04-layout.md) for full sidebar layout documentation.

### Quick Reference

```html
<div data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle class="outline">☰</button>
    <span>App</span>
  </nav>
  <aside data-sidebar>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Settings</a></li>
      </ul>
    </nav>
  </aside>
  <main>Content</main>
</div>
```

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | Container | Grid layout wrapper |
| `data-sidebar-layout="always"` | Container | Always-collapsible |
| `data-topnav` | `<nav>` | Full-width top nav |
| `data-sidebar` | `<aside>` | Sidebar element |
| `data-sidebar-toggle` | `<button>` | Toggle button |
| `data-sidebar-open` | Layout | Open state (auto-applied) |
