# Web Components

Oat registers two custom elements: `ot-tabs` and `ot-dropdown`. Both extend `OtBase` which provides lifecycle management, event delegation, keyboard navigation, and custom event emission.

## OtBase

Base class for all Oat Web Components. Provides:

| Method | Purpose |
|---|---|
| `connectedCallback()` | Called when element is added to DOM. Waits for DOMContentLoaded if needed. |
| `disconnectedCallback()` | Called when element is removed. Triggers `cleanup()`. |
| `init()` | Override in subclass for initialization logic. |
| `cleanup()` | Override for teardown. Called on disconnect. |
| `handleEvent(event)` | Central event handler. Calls `on{eventType}(event)`. Enables `addEventListener(this)`. |
| `keyNav(event, idx, len, prevKey, nextKey, homeEnd)` | Roving keyboard navigation. Returns next index or -1. |
| `emit(name, detail)` | Dispatch custom event (bubbles, composed, cancelable). |
| `$(selector)` | Query selector within element. |
| `$$(selector)` | Query selector all, returns array. |
| `uid()` | Generate unique ID string. |

## ot-tabs

Tabbed interface with ARIA state management and keyboard navigation.

### Structure

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Tab 1</button>
    <button role="tab">Tab 2</button>
    <button role="tab">Tab 3</button>
  </div>
  <div role="tabpanel">Panel 1 content</div>
  <div role="tabpanel">Panel 2 content</div>
  <div role="tabpanel">Panel 3 content</div>
</ot-tabs>
```

### Rules

- Exactly one direct child `<div role="tablist">`
- Tab buttons inside the tablist with `role="tab"`
- Direct child panels with `role="tabpanel"`
- Number of tabs must match number of panels
- First tab is active by default, or set `aria-selected="true"` on a tab

### API

| Property | Type | Description |
|---|---|---|
| `activeIndex` | `number` (get/set) | Current active tab index (0-based) |

### Events

| Event | Detail | Description |
|---|---|---|
| `ot-tab-change` | `{ index, tab }` | Fired when tab changes |

### Keyboard Navigation

| Key | Action |
|---|---|
| `ArrowLeft` | Move to previous tab |
| `ArrowRight` | Move to next tab (wraps) |

### Programmatic Usage

```javascript
const tabs = document.querySelector('ot-tabs');

// Get current tab
const idx = tabs.activeIndex;

// Set tab
tabs.activeIndex = 2;

// Listen for changes
tabs.addEventListener('ot-tab-change', (e) => {
  console.log('Tab:', e.detail.index, e.detail.tab);
});
```

### ARIA

Auto-generated:
- Unique IDs for each tab and panel
- `aria-controls` on tabs → panel IDs
- `aria-labelledby` on panels → tab IDs
- `aria-selected` toggled on active tab
- `tabindex` management (0 on active, -1 on others)

---

## ot-dropdown

Dropdown menus using the Popover API with auto-positioning and keyboard navigation.

### Structure

```html
<ot-dropdown>
  <button popovertarget="menu-id" class="outline">
    Options
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m6 9 6 6 6-6" />
    </svg>
  </button>
  <menu popover id="menu-id">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <button role="menuitem">Help</button>
    <hr>
    <button role="menuitem">Logout</button>
  </menu>
</ot-dropdown>
```

### Rules

- Trigger element with `[popovertarget]` pointing to menu ID
- Menu element with `[popover]` attribute and matching ID
- Menu items use `role="menuitem"`
- `<hr>` for separators

### Popover Content

Any element with `popover` works, not just `<menu>`:

```html
<ot-dropdown>
  <button popovertarget="confirm-popover" class="outline">Confirm</button>
  <article class="card" popover id="confirm-popover">
    <header>
      <h4>Are you sure?</h4>
      <p>This cannot be undone.</p>
    </header>
    <footer>
      <button class="outline small" popovertarget="confirm-popover">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm-popover">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

### Positioning

The dropdown automatically:
- Positions menu below the trigger
- Flips above if viewport overflow (bottom)
- Shifts left if viewport overflow (right)
- Repositions on scroll and resize
- Uses `position: fixed` relative to viewport

### Keyboard Navigation

| Key | Action |
|---|---|
| `ArrowUp` | Previous menu item |
| `ArrowDown` | Next menu item |
| `Home` | First menu item |
| `End` | Last menu item |

On close, focus returns to the trigger button.

### ARIA

Auto-managed:
- `aria-expanded` on trigger button (`true`/`false`)
- Focus management (first item focused on open, trigger on close)

### Cleanup

Scroll and resize listeners are removed when dropdown closes.

---

## Browser Support

- **Popover API**: Chrome 114+, Firefox 125+, Safari 17.4+
- **Custom Elements**: All modern browsers
- **`commandfor` polyfill**: Included in oat.min.js for Safari

Without Popover API support, `ot-dropdown` and toasts will not function.
