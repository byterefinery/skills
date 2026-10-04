# Typed Paths and Links

## Typed paths

`paths` is a proxy inferred from the route tree. Property access descends into static segments, calls bind params, and it mirrors URL anatomy — params, then a search object, then a hash string:

```tsx
paths.users(123); // ok — matchFilters flow into the callsite
paths.users(2).settings; // chainable into children
paths.users(2, { tab: "x" }, "comments"); // "/users/2?tab=x#comments"
paths.about(); // zero-arg/search calls terminate to a plain string
paths(); // "/" — the root
```

Every node coerces via `toString`, so nodes drop straight into `href`, `navigate()`, and `redirect()` without explicit termination. Accessing a segment that doesn't exist in the tree, or binding a param with the wrong type, is a compile error.

Typed paths promise *spelling, not matching* — `matchFilters` means a well-typed URL can fail to match at runtime.

## Links

There is no link component. Use `<a>`; the router intercepts same-origin clicks through delegation and manages link state through compiler-claimed anchors — correct at creation (so late mounts under `<Show>`, `<For>`, or portals are never stale) and refreshed if a dynamic `href` changes.

Behavior modifiers are attributes, so they work identically in client, server-rendered, and third-party markup:

| attribute  | description                                                                                                     |
| ---------- | --------------------------------------------------------------------------------------------------------------- |
| `replace`  | Replace the history entry instead of pushing                                                                    |
| `noscroll` | Turn off scrolling to the top after navigation                                                                  |
| `state`    | JSON string pushed onto the history stack (structured-clone serialized)                                         |
| `preload`  | Set to `"false"` to opt this link out of hover/focus preloading                                                 |
| `link`     | Marks a router link when `explicitLinks` is enabled                                                             |
| `target`   | Any value (e.g. `_self`) opts the anchor out of router handling                                                 |

```tsx
<a href={paths.login} replace>Log in</a>
<a href={paths.docs} noscroll>Docs</a>
<a href="https://example.com">External — untouched</a>
```

## Current and active state

Active and pending state is styled with CSS — one vocabulary for every kind of link:

```css
nav a[aria-current="page"] {
  font-weight: 600;
} /* exact match, query included */
nav a[data-active] {
  color: var(--accent);
} /* exact or prefix match on the path */
a[data-pending] {
  opacity: 0.6;
} /* target of in-flight navigation */
```

One rule decides both, for anchors and `useLinkState` alike:

- **current** (`aria-current="page"`) — same path and same query, ignoring parameter order and the hash. On `/?filter=active`, `<a href="/?filter=active">` is current and `<a href="/">` is not.
- **active** (`data-active`, and `data-pending` for the in-flight target) — the path only, exact or prefix, so both of those links are active there. The root path (the router's `base`, when it has one) only ever matches exactly, so `href={paths()}` doesn't light up on every page.

An `aria-current` you write yourself (`aria-current="step"` in a stepper, say) is yours: the router never overwrites or removes it, and only manages the attribute on links where it set it.

Migrating from `<A>`: `activeClass` / `inactiveClass` become CSS attribute selectors on `[data-active]` / `[aria-current="page"]`; the old `end` prop becomes styling exact matches with `[aria-current="page"]` (which also compares the query) instead of `[data-active]`.

## useLinkState

For component-library links that need reactive state beyond CSS, `useLinkState` is the programmatic counterpart of the attribute vocabulary — matched by the same rule as plain anchors:

- `current()` — same path and same query as the location, ignoring parameter order and the hash (what `aria-current="page"` reflects)
- `active()` — the location's path is the link's path or lives under it, query ignored (`data-active`); a root link (`/`, which resolves to the router's `base`) is exact-only
- `pending()` — the link's path is the target of an in-flight navigation (`data-pending`)

Pass `{ end: true }` to make `active` (and `pending`) exact-path for any link.

```tsx
import { useLinkState } from "@solidjs/router";

function TabLink(props: { href: string; children: JSX.Element }) {
  const link = useLinkState(() => props.href);
  return (
    <a href={props.href} class="tab" data-selected={link.active() || undefined}>
      {props.children}
    </a>
  );
}

const link = useLinkState(() => props.href, { end: true });
```
