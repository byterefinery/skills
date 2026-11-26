# Router

## Table of Contents

- [Router Factory](#router-factory)
- [View Configuration](#view-configuration)
- [URL Generation](#url-generation)
- [Navigation Helpers](#navigation-helpers)
- [Active State](#active-state)
- [Dialogs](#dialogs)
- [Guards](#guards)
- [Multiple Views](#multiple-views)
- [Nested Routers](#nested-routers)
- [View Transitions](#view-transitions)
- [Debug Mode](#debug-mode)
- [URL Parameters](#url-parameters)
- [State Parameters](#state-parameters)

---

## Router Factory

The `router()` function creates a descriptor that manages view navigation:

```js
import { define, html, router } from "hybrids";

const Home = define({ tag: "view-home", render: () => html`<h1>Home</h1>` });
const Details = define({ tag: "view-details", id: "", render: ({ id }) => html`<p>Details: ${id}</p>` });

const App = define({
  tag: "app-root",
  stack: router([Home, Details]),
  render: ({ stack }) => html`
    <main>
      ${stack}
    </main>
  `,
});
```

### How It Works

- `stack` is an array of currently active view elements (reversed — top of stack first)
- Navigation pushes/pops views onto the history stack
- The router handles `popstate`, click interception, and form submission
- Views are created/destroyed as the stack changes

### Options

```js
stack: router([Home, Details], {
  url: "/app",           // base URL (default: current location without hash)
  params: ["theme"],     // global parameters shared across views
  transition: true,      // enable View Transitions API
});
```

---

## View Configuration

Configure individual views with `[router.connect]`:

```js
const Home = define({
  [router.connect]: {
    url: "/home/:categoryId",        // URL pattern with params
    stack: [Details, Settings],      // child views
    dialog: false,                   // modal overlay
    multiple: false,                 // allow duplicate entries
    replace: false,                  // replace current history entry
    guard: () => isLoggedIn(),       // access guard
  },
  tag: "view-home",
  categoryId: "",
  render: () => html`...`,
});
```

### Options

| Option | Type | Description |
|---|---|---|
| `url` | `string` | URL pattern with `:param` placeholders |
| `stack` | `Component[]` | Child views in the navigation tree |
| `dialog` | `boolean` | Render as a modal dialog overlay |
| `multiple` | `boolean` | Allow same view multiple times in stack |
| `replace` | `boolean` | Use `replaceState` instead of `pushState` |
| `guard` | `() => boolean` | Return `false` to block navigation |

---

## URL Generation

### router.url()

Generate a URL for a view:

```js
import { router } from "hybrids";

// Basic URL
const url = router.url(Details);

// With parameters
const url = router.url(Details, { id: "123" });

// With scroll behavior
const url = router.url(Details, { id: "123", scrollToTop: true });
```

Returns a `URL` object. Use in templates:

```js
html`<a href="${router.url(Details, { id: '123' })}">Details</a>`
```

Links are automatically intercepted by the router — no full page navigation.

---

## Navigation Helpers

### router.backUrl()

Get the URL for going back:

```js
const backUrl = router.backUrl();
const backUrl = router.backUrl({ nested: true });     // go to deepest nested parent
const backUrl = router.backUrl({ scrollToTop: true }); // scroll on back
```

### router.guardUrl()

Get the URL for the guarded destination (used with guards):

```js
const guardUrl = router.guardUrl();
const guardUrl = router.guardUrl({ theme: "dark" });
```

### router.currentUrl()

Get the URL of the current view:

```js
const currentUrl = router.currentUrl();
const currentUrl = router.currentUrl({ scrollToTop: true });
```

### router.resolve()

Resolve an async operation before navigation:

```js
html`
  <button onclick="${(host, event) => router.resolve(event, checkAuth())}">
    Go
  </button>
`
```

- Prevents the default navigation
- After the promise resolves, the navigation proceeds
- If a new navigation starts during the wait, the pending one is cancelled

---

## Active State

Check if a view is currently active:

```js
import { router } from "hybrids";

// Single view
const isActive = router.active(Details);

// Multiple views
const isAnyActive = router.active([Details, Settings]);

// With stack check (active or in active view's stack)
const isInStack = router.active(Details, { stack: true });
```

Use for active link styling:

```js
html`
  <a href="${router.url(Home)}" class="${router.active(Home) ? 'active' : ''}">
    Home
  </a>
`
```

---

## Dialogs

Dialog views render as modal overlays:

```js
const Dialog = define({
  [router.connect]: {
    dialog: true,
  },
  tag: "view-dialog",
  render: () => html`
    <div class="overlay">
      <div class="dialog">
        <h2>Dialog Title</h2>
        <p>Content</p>
        <button onclick="${() => history.go(-1)}">Close</button>
      </div>
    </div>
  `,
});
```

### Dialog Behavior

- Dialogs cannot have `url` or `stack` options
- Pressing `Escape` navigates back (closes the dialog)
- Focus is trapped within the dialog
- Dialogs appear on top of the current view stack
- The `router-transition` attribute includes `dialog` for CSS transitions

---

## Guards

Block navigation with a guard function:

```js
const Protected = define({
  [router.connect]: {
    guard: () => isAuthenticated(),
    stack: [SecretPage],
  },
  tag: "view-protected",
  render: () => html`<p>Protected content</p>`,
});
```

### Guard Behavior

- If `guard()` returns `false`, navigation to this view and its children is blocked
- The user is redirected to the first view in the guard's stack
- Use `router.guardUrl()` to get the redirect URL
- Guards can be async (return a Promise)

### Parent Guards

Guards cascade — if a parent view has a guard, all children inherit it:

```js
const Auth = define({
  [router.connect]: {
    guard: () => isLoggedIn(),
    stack: [Dashboard, Profile],  // both protected
  },
  tag: "view-auth",
  render: () => html`${stack}`,
});
```

---

## Multiple Views

Allow the same view to appear multiple times in the history stack:

```js
const ItemDetail = define({
  [router.connect]: {
    multiple: true,
    url: "/items/:id",
  },
  tag: "view-item-detail",
  id: "",
  render: ({ id }) => html`<p>Item: ${id}</p>`,
});
```

Without `multiple: true`, navigating to the same view replaces the existing entry.

---

## Nested Routers

A view can contain its own router for sub-navigation:

```js
const Dashboard = define({
  [router.connect]: {
    stack: [DashboardHome, DashboardSettings],
  },
  tag: "view-dashboard",

  // Nested router property
  subStack: router([DashboardHome, DashboardSettings], {
    params: ["filter"],
  }),

  filter: "",

  render: ({ subStack }) => html`
    <div>
      <h1>Dashboard</h1>
      <nav>
        <a href="${router.url(DashboardHome)}">Home</a>
        <a href="${router.url(DashboardSettings)}">Settings</a>
      </nav>
      ${subStack}
    </div>
  `,
});
```

### Rules

- A view can have at most one nested router
- Views with nested routers cannot have the `url` option
- Dialogs cannot have nested routers
- Nested routers share the parent's history state

---

## View Transitions

Enable the View Transitions API for animated navigation:

```js
stack: router([Home, Details], {
  transition: true,
});
```

### CSS

The `<html>` element gets a `router-transition` attribute:

| Value | Meaning |
|---|---|
| `forward` | New view pushed onto stack |
| `forward dialog` | Dialog opened |
| `backward` | View popped from stack |
| `backward dialog` | Dialog closed |
| `replace` | View replaced (same stack depth) |

```css
::view-transition-old(root) {
  animation: fade-out 0.3s;
}

::view-transition-new(root) {
  animation: fade-in 0.3s;
}

[router-transition="forward"] ::view-transition-old(root) {
  animation: slide-out-left 0.3s;
}
```

### Manual Transitions

Use `html.transition()` for individual template updates:

```js
html.transition(html`<div>${content}</div>`)
```

---

## Debug Mode

Enable debug logging:

```js
import { debug, router } from "hybrids";

debug();
// or
router.debug();
```

Logs navigation entries to the console with parameters. Each view is accessible via `$$1`, `$$2`, etc.

---

## URL Parameters

Define URL patterns with parameters:

```js
const Details = define({
  [router.connect]: {
    url: "/users/:userId/posts/:postId",
  },
  tag: "view-details",
  userId: "",
  postId: "",
  render: ({ userId, postId }) => html`...`,
});
```

- Parameters are extracted from the URL and set on the view
- Parameters must be writable properties on the view
- Use `router.url(Details, { userId: "1", postId: "2" })` to generate URLs

### Search Parameters

```js
const Search = define({
  [router.connect]: {
    url: "/search?:q,:page",  // ? prefix = search params
  },
  tag: "view-search",
  q: "",
  page: "1",
  render: ({ q, page }) => html`...`,
});
```

---

## State Parameters

Parameters that live in history state (not URL):

```js
stack: router([Home, Details], {
  params: ["theme", "userId"],  // shared across all views
});
```

These parameters are:

- Stored in history state, not the URL
- Shared across all views in the router
- Automatically synced when the view property changes
- Excluded from URL generation

### Scroll to Top

```js
html`<a href="${router.url(Details, { scrollToTop: true })}">Details</a>`
```

The `scrollToTop` parameter clears scroll positions when navigating.
