# Router

A global navigation system based on a **tree-like structure of views**, each with its own routing configuration in the component definition. The router state is a stack of views connected to browser history; views on the stack keep their state, scroll positions, and last focused element. The resulting stack array contains only the current view plus any dialogs on top of it.

## Table of Contents

- [Factory](#factory)
- [View configuration](#view-configuration)
- [URL generation methods](#url-generation-methods)
- [router.navigate](#routernavigate)
- [router.resolve](#routerresolve)
- [router.active](#routeractive)
- [scrollToTop](#scrolltotop)
- [Events](#events)
- [Nested routers](#nested-routers)
- [Debug mode](#debug-mode)

---

## Factory

```js
router(views: component | component[] | () => ..., options?: object): descriptor
```

- `views` — a defined component or array of defined components (the roots). Wrap in a function to avoid uninitialized ES module issues. Navigating between roots replaces the whole stack.
- `options.url` — base URL string for views without their own `url` (default: current URL without hash). Set it for mixed URL/no-URL setups to avoid non-deterministic behavior.
- `options.params` — array of property names passed to **every** view as parameters (bypass URL generation, set by reference).
- `options.transition` — boolean; sets a `<html router-transition="">` attribute announcing transitions: `""` (first render), `forward`, `backward`, `replace`, plus `forward dialog` / `backward dialog` for dialogs. Useful for CSS `::view-transition-*` animations with the Transition API.

```js
import { define, html, router } from "hybrids";

import Home from "./views/Home.js";

define({
  tag: "my-app",
  stack: router(Home),
  render: ({ stack }) => html`
    <my-app-layout>${stack}</my-app-layout>
  `,
});
```

**Only one root router may be connected at a time** — connecting a second root router while another is in the document throws. Use nested routers for complex layouts.

The component with the router listens to `click` and `submit` events to intercept navigation. `submit` does not cross the Shadow DOM boundary — render app root templates in light DOM for form interception.

## View configuration

Views are defined components connected as a router root or via another view's `stack`. Configuration lives in the optional `[router.connect]` property:

```js
[router.connect]?: {
  stack?: component[] | () => component[];
  url?: string;
  dialog?: boolean;
  multiple?: boolean;
  replace?: boolean;
  guard?: () => boolean;
},
```

### stack

Views placed on the stack when navigating from the current view. The router uses the **lowest common ancestor** algorithm to compute the resulting history stack (e.g., navigating to the root from a deep view clears history down to the root).

### url

The router's source of state is `history.state` (view tag name + parameters), not the URL — the URL is optional and mainly used when the user enters the app with a clean history, and as output for copying. Any **writable** property can be passed when navigating, but only `url`-option parameters appear in the address bar.

Syntax: must start with `/`; path parameters via `:name` (`/users/:userId/:other`); query parameters as an explicit comma-separated list (`/users?one,two`); no `*` wildcard (use a path parameter). Matching goes from the roots, right to left through stacks; the first match wins.

### dialog

`dialog: true` displays the view on top of the full-screen views (the memory stack still contains all views). Supports backward navigation, closes on Escape, and traps keyboard focus. Dialogs cannot be entry points — the router resolves the state to the parent view. Use for prompts, alerts, and context messages.

### multiple

Views are singletons by default: navigating to an already-stacked view reuses the instance and updates its parameters. `multiple: true` allows stacking the same view repeatedly (e.g., product detail with different ids) — history entries are separate and back-navigation steps through instances.

### replace

Default in-stack navigation reuses the instance (state may persist). `replace: true` performs a full reload of the view while still replacing the history entry.

### guard

A **synchronous** function (no `host` argument — called outside the element context) invoked when navigating to the view or to children of its `stack`:

- Direct navigation: truthy → the first `stack` view is used; falsy/throw → the guarded view itself is displayed
- Navigation from the stack: failing condition redirects to the guarded view, but the intended target is stored in the history entry — use `router.guardUrl()` inside the guarded view to link to it
- Multiple guards on the path resolve from deepest up
- Guards run only during navigation, not on render/update

Typical pattern: put a `Login` view (with `guard: () => store.ready(store.get(Session))`) as the router **root** to protect the whole app — the rest of the structure stays untouched.

Async setup: the function must return synchronously, so conditionally render the app element only after the async data (session) is ready:

```js
render: ({ session }) =>
  store.ready(session) || store.error(session)
    ? html`<my-app></my-app>`
    : html`<app-loader>...</app-loader>`,
```

## URL generation methods

All return a `URL` instance or `""` (no throw) — usable as `href`/`action`. Parameters are serialized to the query string; complex object structures are not supported (pass model identifiers via the store instead).

### router.url

```js
router.url(view: component, params?: object): URL | ""
```

Target view identified by its definition reference. Unconnected view → `""` (no throw).

### router.backUrl

```js
router.backUrl(options?: { nested?: boolean; scrollToTop?: boolean }): URL | ""
```

URL to the previous view on the stack (for views reachable from multiple points or shared layouts). If the current view is the only one, the last parent in the hierarchy is used; root views return `""`. `nested: true` generates the URL from the deepest nested router instead of skipping same-main-view entries.

### router.currentUrl

```js
router.currentUrl(params?: object): URL | ""
```

URL for the **current** view without a definition reference — for reusable components or avoiding module references.

### router.guardUrl

```js
router.guardUrl(params?: object): URL | ""
```

For guarded views: dynamically the failed navigation target, or the first `stack` view by default. Use in forms: `<form action="${router.guardUrl()}">`.

## router.navigate

New in 9.2 — programmatic navigation:

```js
router.navigate(view: component, params?: object): void
```

Arguments and result are identical to a user clicking an anchor with the generated URL: the `navigate` event is dispatched on the host and the router goes forward/backward using the view structure.

- Use only when navigation cannot be expressed as an anchor or form (after timeouts, WebSocket messages, non-user-initiated async actions). For user-initiated actions, prefer `href`/`action` — they keep navigation accessible and visible to the browser.
- **Unlike the URL methods, `navigate` throws** when the root router is not connected, the view is not part of the router, or it is called while the router is dispatching the `navigate` event (e.g., inside that event listener) — this protects against infinite navigation loops.

```js
import { router, store } from "hybrids";

import Login from "./Login.js";

function signOut(host) {
  return store.set(host.session, null).then(() => {
    router.navigate(Login);
  });
}
```

## router.resolve

```js
router.resolve(event: Event, promise: Promise): Promise
```

Performs an async action during navigation; navigation happens **only if the promise resolves**. The navigation URL is taken from the event target, so the template must still generate the link via `router.url()`/`backUrl()`:

```js
function deleteUser(host, event) {
  router.resolve(event, store.set(host.user, null));
}

render: ({ user }) => html`
  <dialog>
    <a href="${router.url(Users)}" onclick="${deleteUser}">Yes</a>
    <a href="${router.backUrl()}">Cancel</a>
  </dialog>
`;
```

## router.active

```js
router.active(views: view | view[], options?: { stack?: boolean }): boolean
```

`true` when one of the views is the current view; with `stack: true` also when the current view is anywhere in their stack (parent view stays active while a child is shown). Use for nav link highlighting.

## scrollToTop

Navigation methods accept a `scrollToTop` parameter option that clears the main scroll position when navigating to a view already kept in memory. New views pushed onto the stack clear the vertical scroll automatically.

## Events

The router dispatches a `navigate` event on the host element:

```js
const app = document.getElementById("my-app");
app.addEventListener("navigate", (event) => {
  ga("send", "pageview", event.detail.url);
});
```

## Nested routers

A `router()` factory can be used **inside a view** already connected to a parent router. Unlike a view's `stack` option, the nested router renders content inside the host view as content, not as a separate view in the stack:

```js
export default define({
  tag: "my-module-view",
  tabs: router([TabOneView, TabTwoView]),
  render: ({ tabs }) => html`
    <my-tabs-group>
      <a href="${router.url(TabOneView)}">Tab One</a>
      <a href="${router.url(TabTwoView)}">Tab Two</a>
    </my-tabs-group>

    ${tabs}
  `,
});
```

## Debug mode

In debug mode the router logs navigation events and exposes the current view in DevTools via the `$$0` reference. Enable with `debug()` before any other code (see Getting Started).
