# 06 — Navigation

## navbar

Top navigation bar with start, center, and end sections.

**Class names:**
- component: `navbar`
- part: `navbar-start`, `navbar-center`, `navbar-end`

```html
<div class="navbar">
  <div class="navbar-start"><a>Logo</a></div>
  <div class="navbar-center"><a>Brand</a></div>
  <div class="navbar-end"><button class="btn">Sign In</button></div>
</div>
```

Use `base-200` for background color.

## breadcrumbs

Navigation trail showing the current page location.

**Class names:**
- component: `breadcrumbs`

```html
<div class="breadcrumbs">
  <ul>
    <li><a>Home</a></li>
    <li><a>Category</a></li>
    <li>Current Page</li>
  </ul>
</div>
```

Scrolls horizontally when items exceed container width. Can contain icons inside links.

## menu

Vertical or horizontal list of navigation links.

**Class names:**
- component: `menu`
- part: `menu-title`, `menu-dropdown`, `menu-dropdown-toggle`
- modifier: `menu-disabled`, `menu-active`, `menu-focus`, `menu-dropdown-show`
- size: `menu-xs`, `menu-sm`, `menu-md`, `menu-lg`, `menu-xl`
- direction: `menu-vertical`, `menu-horizontal`

```html
<ul class="menu">
  <li><span class="menu-title">Category</span></li>
  <li><a>Item 1</a></li>
  <li>
    <details>
      <summary>Parent</summary>
      <ul>
        <li><a>Child 1</a></li>
      </ul>
    </details>
  </li>
</ul>
```

Use `lg:menu-horizontal` for responsive layouts. Use `<details>` for collapsible submenus.

## megamenu

Large horizontal menu with popover submenus. Best for large screens.

**Class names:**
- component: `megamenu`
- part: `megamenu-active`
- modifier: `megamenu-wide`, `megamenu-full`
- direction: `megamenu-vertical`
- size: `megamenu-xs`, `megamenu-sm`, `megamenu-md`, `megamenu-lg`, `megamenu-xl`

```html
<button class="btn sm:hidden" popovertarget="my-megamenu">Menu</button>
<div class="megamenu max-sm:megamenu-vertical p-2 border border-base-300" id="my-megamenu" popover>
  <span class="megamenu-active"></span>
  <button popovertarget="item-1">Section 1</button>
  <div id="item-1" popover>{content}</div>
  <button popovertarget="item-2">Section 2</button>
  <div id="item-2" popover>{content}</div>
</div>
```

`megamenu-active` span is mandatory (indicator under active item). Each button must have a corresponding popover with matching `id`. On small screens, hide megamenu with `max-sm:megamenu-vertical` and show a toggle button.

## tab

Tabbed interface for switching content sections.

**Class names:**
- component: `tabs`
- part: `tab`, `tab-content`
- style: `tabs-box`, `tabs-border`, `tabs-lift`
- modifier: `tab-active`, `tab-disabled`
- placement: `tabs-top`, `tabs-bottom`

Using buttons:
```html
<div role="tablist" class="tabs tabs-lift">
  <button role="tab" class="tab tab-active">Tab 1</button>
  <button role="tab" class="tab">Tab 2</button>
</div>
```

Using radio inputs (for content switching):
```html
<div role="tablist" class="tabs tabs-box">
  <input type="radio" name="tabs" class="tab tab-active" aria-label="Tab 1" />
  <input type="radio" name="tabs" class="tab" aria-label="Tab 2" />
</div>
```

Radio inputs are needed for tab content to work on click.

## drawer

Grid layout with show/hide sidebar (left or right).

**Class names:**
- component: `drawer`
- part: `drawer-toggle`, `drawer-content`, `drawer-side`, `drawer-overlay`
- placement: `drawer-end`
- modifier: `drawer-open`
- variant: `is-drawer-open:`, `is-drawer-close:`

```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- All page content: navbar, main, footer -->
    <label for="my-drawer" class="btn drawer-button lg:hidden">Open</label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <li><a>Item 1</a></li>
    </ul>
  </div>
</div>
```

`id` is required for `drawer-toggle`. Use `<label for="my-drawer">` to toggle. `lg:drawer-open` keeps sidebar visible on large screens. **All page content must be inside `drawer-content`**, including navbar and footer.

## dock

Bottom navigation bar that sticks to the screen bottom.

**Class names:**
- component: `dock`
- part: `dock-label`
- modifier: `dock-active`
- size: `dock-xs`, `dock-sm`, `dock-md`, `dock-lg`, `dock-xl`

```html
<div class="dock {MODIFIER}">
  <button>
    <svg>{icon}</svg>
    <span class="dock-label">Home</span>
  </button>
  <button class="dock-active">
    <svg>{icon}</svg>
    <span class="dock-label">Search</span>
  </button>
</div>
```

Add `<meta name="viewport" content="viewport-fit=cover">` for iOS responsiveness.

## pagination

Page navigation using joined buttons.

**Class names:** Uses `join` and `join-item`.

```html
<div class="join">
  <button class="join-item btn btn-sm">«</button>
  <button class="join-item btn btn-sm">1</button>
  <button class="join-item btn btn-sm btn-disabled">2</button>
  <button class="join-item btn btn-sm">3</button>
  <button class="join-item btn btn-sm">»</button>
</div>
```
